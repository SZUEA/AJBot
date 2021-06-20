# -*- coding:utf-8 -*-

import base64
import os
import random
from enum import Enum
from io import BytesIO

import httpx
from botoy import Action, GroupMsg
from botoy.collection import MsgTypes
from botoy.decorators import ignore_botself, these_msgtypes
from PIL import Image, ImageDraw

try:
    import ujson as json
except Exception:
    import json

# ==========================================
RESOURCES_BASE_PATH = "./resources/throw-creep"

# ==========================================

# 屏蔽群 例：[12345678, 87654321]
blockGroupNumber = []
# 触发命令列表
creepCommandList = ["爬", "爪巴", "给爷爬", "爬啊", "快爬"]
throwCommandList = ["丢", "我丢"]
# 爬的概率 越大越容易爬 取值区间 [0, 100]
creep_limit = 80

# ==========================================


@ignore_botself
def receive_group_msg(ctx: GroupMsg):
    userGroup = ctx.FromGroupId

    if Tools.commandMatch(userGroup, blockGroupNumber):
        return

    if not Tools.atOnly(ctx.MsgType):
        return

    msg = ctx.Content

    bot = Action(ctx.CurrentQQ)

    match(msg, bot, userGroup)


class Model(Enum):

    ALL = "_all"

    BLURRY = "_blurry"

    SEND_AT = "_send_at"

    SEND_DEFAULT = "_send_default"


class Status(Enum):

    SUCCESS = "_success"

    FAILURE = "_failure"


class Tools:
    @staticmethod
    def textOnly(msgType):
        return msgType == MsgTypes.TextMsg

    @staticmethod
    def atOnly(msgType):
        return msgType == MsgTypes.AtMsg

    @staticmethod
    def writeFile(p, content):
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def readFileByLine(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return f.readlines()

    @staticmethod
    def readJsonFile(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return json.loads(f.read())

    @staticmethod
    def writeJsonFile(p, content):
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(content))
        return Status.SUCCESS

    @staticmethod
    def readFileContent(p):
        if not os.path.exists(p):
            return Status.FAILURE
        with open(p, "r", encoding="utf-8") as f:
            return f.read().strip()

    @staticmethod
    def readPictureFile(picPath):
        if not os.path.exists(picPath):
            return Status.FAILURE
        with open(picPath, "rb") as f:
            return f.read()

    @classmethod
    def base64conversion(cls, picPath):
        picByte = cls.readPictureFile(picPath)
        if picByte == Status.FAILURE:
            raise Exception("图片文件不存在！")
        return str(base64.b64encode(picByte), encoding="utf-8")

    @classmethod
    def sendPictures(cls, userGroup, picPath, bot: Action, content="", atUser=0):
        bot.sendGroupPic(
            userGroup,
            picBase64Buf=cls.base64conversion(picPath),
            atUser=atUser,
            content=str(content),
        )

    @staticmethod
    def sendText(userGroup, msg, bot, model=Model.SEND_DEFAULT, atQQ=""):
        if msg not in ("", Status.FAILURE):
            if model == Model.SEND_DEFAULT:
                bot.sendGroupText(userGroup, content=str(msg))
            if model == Model.SEND_AT:
                if atQQ == "":
                    raise Exception("没有指定 at 的人！")
                at = f"[ATUSER({atQQ})]\n"
                bot.sendGroupText(userGroup, content=at + str(msg))

    @staticmethod
    def commandMatch(msg, commandList, model=Model.ALL):
        if model == Model.ALL:
            for c in commandList:
                if c == msg:
                    return True
        if model == Model.BLURRY:
            for c in commandList:
                if msg.find(c) != -1:
                    return True
        return False

    @staticmethod
    def checkFolder(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    @staticmethod
    def atQQ(userQQ):
        return f"[ATUSER({userQQ})]\n"

    @staticmethod
    def identifyAt(content):
        try:
            result = json.loads(content)
            return [result["Content"], result["UserID"]]
        except Exception:
            return Status.FAILURE


class Network:
    @staticmethod
    def getBytes(url, headers="", timeout=10):
        if headers == "":
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
            }
        try:
            return httpx.get(url=url, headers=headers, timeout=timeout).read()
        except:
            return Status.FAILURE


def match(plainText, bot, userGroup):
    # creep features
    result = Tools.commandMatch(plainText, creepCommandList, model=Model.BLURRY)
    if result:
        # Parsing parameters
        params = Tools.identifyAt(plainText)
        if params != Status.FAILURE:
            qq = int(params[1][0])
            outPath = ThrowAndCreep.creep(qq)
            Tools.sendPictures(userGroup, outPath, bot)
            return
    # throe features
    result = Tools.commandMatch(plainText, throwCommandList, model=Model.BLURRY)
    if result:
        # Parsing parameters
        params = Tools.identifyAt(plainText)
        if params != Status.FAILURE:
            qq = int(params[1][0])
            outPath = ThrowAndCreep.throw(qq)
            Tools.sendPictures(userGroup, outPath, bot)
            return


class ThrowAndCreep:

    _avatar_size = 139

    _center_pos = (17, 180)

    @staticmethod
    def getAvatar(url):
        img = Network.getBytes(url)
        return img

    @staticmethod
    def randomClimb():
        randomNumber = random.randint(1, 100)
        if randomNumber < creep_limit:
            return True
        return False

    @staticmethod
    def get_circle_avatar(avatar, size):
        avatar.thumbnail((size, size))

        scale = 5
        mask = Image.new("L", (size * scale, size * scale), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size * scale, size * scale), fill=255)
        mask = mask.resize((size, size), Image.ANTIALIAS)

        ret_img = avatar.copy()
        ret_img.putalpha(mask)

        return ret_img

    @classmethod
    def creep(cls, qq):
        creeped_who = qq
        id = random.randint(0, 53)

        whetherToClimb = cls.randomClimb()

        if not whetherToClimb:
            return f"{RESOURCES_BASE_PATH}/不爬.jpg"

        avatar_img_url = "http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640".format(
            QQ=creeped_who
        )
        res = cls.getAvatar(avatar_img_url)
        avatar = Image.open(BytesIO(res)).convert("RGBA")
        avatar = cls.get_circle_avatar(avatar, 100)

        creep_img = Image.open(f"{RESOURCES_BASE_PATH}/pa/爬{id}.jpg").convert("RGBA")
        creep_img = creep_img.resize((500, 500), Image.ANTIALIAS)
        creep_img.paste(avatar, (0, 400, 100, 500), avatar)
        dirPath = f"{RESOURCES_BASE_PATH}/avatar"
        Tools.checkFolder(dirPath)
        creep_img.save(f"{RESOURCES_BASE_PATH}/avatar/{creeped_who}_creeped.png")

        return f"{RESOURCES_BASE_PATH}/avatar/{creeped_who}_creeped.png"

    @classmethod
    def throw(cls, qq):
        throwed_who = qq

        avatar_img_url = "http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640".format(
            QQ=throwed_who
        )

        res = cls.getAvatar(avatar_img_url)
        avatar = Image.open(BytesIO(res)).convert("RGBA")
        avatar = cls.get_circle_avatar(avatar, cls._avatar_size)

        rotate_angel = random.randrange(0, 360)

        throw_img = Image.open(f"{RESOURCES_BASE_PATH}/throw.jpg").convert("RGBA")
        throw_img.paste(
            avatar.rotate(rotate_angel), cls._center_pos, avatar.rotate(rotate_angel)
        )
        dirPath = f"{RESOURCES_BASE_PATH}/avatar"
        Tools.checkFolder(dirPath)
        throw_img.save(f"{RESOURCES_BASE_PATH}/avatar/{throwed_who}.png")

        return f"{RESOURCES_BASE_PATH}/avatar/{throwed_who}.png"
