# -*- coding:utf-8 -*-
import base64
import os
from enum import Enum

from botoy import Action, GroupMsg
from botoy.collection import MsgTypes
from botoy.decorators import ignore_botself, these_msgtypes
from PIL import Image, ImageDraw, ImageFont

try:
    import ujson as json
except ImportError:
    import json


# ==========================================

RESOURCES_BASE_PATH = "./resources/image-custom"

# ==========================================

# 屏蔽群 例：[12345678, 87654321]
blockGroupNumber = []
# 是否自动制作表情列表二维码 默认是
# 表情太多时二维码可能装不下扫不出来，请自行制作或者删去 resources/list.jpg 即关闭查询表情列表图（qrListOpen 也要关闭）
qrListOpen = True
# 表情包字体
fontPath = f"{RESOURCES_BASE_PATH}/font/simhei.ttf"
# 最小字体限制
fontMin = 15

if qrListOpen:
    import qrcode
# ==========================================


bot = Action(int(os.getenv("BOTQQ")))


@ignore_botself
def receive_group_msg(ctx: GroupMsg):

    if Tools.commandMatch(ctx.FromGroupId, blockGroupNumber):
        return

    if not Tools.textOnly(ctx.MsgType):
        return

    mainEntrance(ctx.Content, ctx.FromUserId, ctx.FromGroupId, bot)


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
    def sendPictures(cls, userGroup, picPath, bot):
        bot.sendGroupPic(userGroup, picBase64Buf=cls.base64conversion(picPath))

    @staticmethod
    def sendText(userGroup, msg, bot, model=Model.SEND_DEFAULT, atQQ=""):
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


def mainEntrance(msg, userQQ, userGroup, bot):
    pictureListCommand = ["img list"]
    primaryMatchingSuffix = [".jpg", ".JPG"]
    switchEmojiCommandPrefix = ["img "]
    # Emoticon list function
    if Tools.commandMatch(msg, pictureListCommand, Model.ALL):
        makeQrCode()
        listFilePath = f"{RESOURCES_BASE_PATH}/list.jpg"
        if os.path.exists(listFilePath):
            Tools.sendPictures(userGroup=userGroup, picPath=listFilePath, bot=bot)
            return
    # Render emoji function
    if Tools.commandMatch(msg, primaryMatchingSuffix, Model.BLURRY):
        text = msg[: msg.rfind(".")]
        emoticonId = getEmojiId(userQQ)
        result = drawing(emoticonId, text, userQQ)
        if result == Status.SUCCESS:
            resultPath = f"{RESOURCES_BASE_PATH}/cache/{userQQ}.jpg"
            Tools.sendPictures(userGroup=userGroup, picPath=resultPath, bot=bot)
            return
    # Change emoji function
    if Tools.commandMatch(msg, switchEmojiCommandPrefix, Model.BLURRY):
        emoticonAlias = msg[msg.find(" ") + 1 :]
        result = changeEmoji(userQQ, emoticonAlias)
        if result == Status.SUCCESS:
            sendMsg = f"表情已更换为 [{emoticonAlias}] 喵~"
            Tools.sendText(
                userGroup=userGroup,
                msg=sendMsg,
                bot=bot,
                model=Model.SEND_AT,
                atQQ=userQQ,
            )
            return


def changeEmoji(userQQ, emoticonAlias):
    emojiConfiguration = f"{RESOURCES_BASE_PATH}/image_data/bieming/name.ini"
    if not os.path.exists(emojiConfiguration):
        raise Exception(f"表情配置 {emojiConfiguration} 不存在！")
    emoticonId = queryEmoticonId(emoticonAlias)
    currentEmoji = getEmojiId(userQQ)
    if emoticonId != Status.FAILURE and emoticonId != currentEmoji:
        p = f"{RESOURCES_BASE_PATH}/image_data/qqdata/{userQQ}.ini"
        Tools.writeFile(p, emoticonId)
        return Status.SUCCESS
    return Status.FAILURE


def queryEmoticonId(emoticonAlias):
    emojiConfiguration = f"{RESOURCES_BASE_PATH}/image_data/bieming/name.ini"
    if not os.path.exists(emojiConfiguration):
        raise Exception(f"表情配置 {emojiConfiguration} 不存在！")
    for line in Tools.readFileByLine(emojiConfiguration):
        line = line.strip()
        alias = line.split(" ")[0]
        codename = line.split(" ")[1]
        if alias == emoticonAlias:
            return codename
    return Status.FAILURE


def getEmojiId(userQQ):
    p = f"{RESOURCES_BASE_PATH}/image_data/qqdata/{userQQ}.ini"
    c = Tools.readFileContent(p)
    return "initial" if c == Status.FAILURE else c


def drawing(emoticonId, text, userQQ):
    picPathJPG = f"{RESOURCES_BASE_PATH}/image_data/{emoticonId}/{emoticonId}.jpg"
    picPathPNG = f"{RESOURCES_BASE_PATH}/image_data/{emoticonId}/{emoticonId}.png"
    picPath = ""
    # Check that the file exists
    if os.path.exists(picPathJPG):
        picPath = picPathJPG
    elif os.path.exists(picPathPNG):
        picPath = picPathPNG
    else:
        return Status.FAILURE
    configPath = f"{RESOURCES_BASE_PATH}/image_data/{emoticonId}/config.ini"
    if not os.path.exists(configPath):
        return Status.FAILURE

    # Drawing
    config = Tools.readJsonFile(configPath)
    img = Image.open(picPath)
    draw = ImageDraw.Draw(img)
    color = config["color"]
    fontSize = config["font_size"]
    fontMax = config["font_max"]
    imageFontCenter = (config["font_center_x"], config["font_center_y"])
    imageFontSub = config["font_sub"]
    # 设置字体暨字号
    ttfront = ImageFont.truetype(fontPath, fontSize)
    fontLength = ttfront.getsize(text)
    while fontLength[0] > fontMax:
        fontSize -= imageFontSub
        ttfront = ImageFont.truetype(fontPath, fontSize)
        fontLength = ttfront.getsize(text)
    if fontSize <= fontMin:
        return Status.FAILURE
    # 自定义打印的文字和文字的位置
    if fontLength[0] > 5:
        draw.text(
            (
                imageFontCenter[0] - fontLength[0] / 2,
                imageFontCenter[1] - fontLength[1] / 2,
            ),
            text,
            fill=color,
            font=ttfront,
        )

    dirPath = f"{RESOURCES_BASE_PATH}/cache"
    Tools.checkFolder(dirPath)
    img.save(f"{dirPath}/{userQQ}.jpg")
    return Status.SUCCESS


def makeQrCode():
    if qrListOpen:
        p = f"{RESOURCES_BASE_PATH}/image_data/bieming/name.ini"
        lines = Tools.readFileByLine(p)
        if lines == Status.FAILURE:
            raise Exception(f"{p} 表情包配置不存在！")
        out = ""
        for line in lines:
            name = line.strip().split()[0]
            out += name + "\n"
        out = out.strip()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=5,
            border=4,
        )
        qr.add_data(out)
        img = qr.make_image(fill_color="green", back_color="white")
        img.save(f"{RESOURCES_BASE_PATH}/list.jpg")
