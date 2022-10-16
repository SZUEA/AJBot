"""以.或。开头
~~~~~~~~~~~~~~
.mine 查看我的关键字
.dele 等删除 匹配关键字
设置格式： .eq 【关键字】 【回复词】
回复词可以用 | 分割多条回复，会随机发送一个
~~~~~~~~~~~~~~
.eq .set 等添加 全等匹配
.con 等添加 包含匹配
.re 等添加 正则匹配
.pre 等添加 前缀匹配
"""
import re
import time
from random import randrange, choice
from typing import Union, List
from xml.dom.minidom import parseString

from EAbotoy import Action, sugar, jconfig
from EAbotoy.contrib import plugin_receiver
from EAbotoy.model import WeChatMsg
from EAbotoy.collection import MsgTypes

from EAbotoy.session import SessionHandler, session
from EAbotoy.session import ctx

from .db import DB, is_bot_master, count_owner_reply


# 下面三个函数名不能改，否则不会调用
# 但是都是可选项，建议把不需要用到的函数删除，节约资源


class Reply(object):
    def __init__(self, _id, rule_list, reply_list, match_group, response_type='text', pic_url=''):
        self.id: int = _id
        self.rule_list: [str] = rule_list
        self.reply_list: [str] = reply_list
        self.response_type = response_type
        self.pic_url = pic_url
        self.match_group = match_group

    def match(self, message, FromUserName):
        for rule in self.rule_list:
            if FromUserName == self.match_group and self.check(rule, message):
                return True
        return False

    def check(self, rule: str, message: str):
        raise NotImplementedError

    def reply(self, ctx: WeChatMsg):
        if self.response_type == 'text':
            Action(ctx.CurrentWxid).sendWxText(ctx.FromUserName,
                                               content=choice(self.reply_list).replace("\\n", "\n"))
        elif self.response_type == 'pic':
            Action(ctx.CurrentWxid).sendCdnImg(ctx.FromUserName, xml=self.pic_url)
        else:
            Action(ctx.CurrentWxid).sendEmoji(ctx.FromUserName, EmojiMd5=self.pic_url)

    def remove(self):
        op = DB()
        op.delete_reply_message(self.id)


class RegReply(Reply):
    """
    正则回复
    """

    def check(self, rule: str, message: str):
        try:
            return re.search(rule, message) is not None
        except Exception as e:
            return False


class PreReply(Reply):
    """
    前缀回复
    """

    def check(self, rule: str, message: str):
        return message.startswith(rule)


class ContainReply(Reply):
    """
    包含回复
    """

    def check(self, rule: str, message: str):
        return rule in message


class EqualReply(Reply):
    """
    全等回复
    """

    def check(self, rule: str, message: str):
        return rule == message


response_list: [Reply] = []
mapping_dict = {
    'PreReply': PreReply,
    'RegReply': RegReply,
    'ContainReply': ContainReply,
    'EqualReply': EqualReply
}

type_map = {
    'EqualReply': 1,
    'PreReply': 2,
    'ContainReply': 3,
    'RegReply': 4,
}


def init_response():
    response_list.clear()
    start_time = time.perf_counter()
    op = DB()
    res = op.get_qq_bot_reply()
    for reply in res:
        add_response(reply['id'], reply['rules'],
                     reply['response'], reply['rule_type'], reply['from_wxid'],
                     reply['response_type'], reply['pic_url'])
    end_time = time.perf_counter()

    # def k(obj: Reply):
    #     return type_map[obj.__class__.__name__]
    #
    # response_list.sort(key=k)
    return end_time - start_time


def add_response(_id, rules, response, rule_type, FromUserName, response_type, pic_url=''):
    response_list.append(mapping_dict[rule_type](_id, rules.split('|'),
                                                 response.split('|'), FromUserName,
                                                 response_type, pic_url))


init_response()
MAX = 5

honey = SessionHandler().receive_wx_msg()


def wait_get(name, st):
    arg = session.want(name, timeout=3)
    if arg is None:
        arg = session.want(name, st, timeout=30)
    return arg

@honey.handle
def add_reply():
    if ctx.MsgType != MsgTypes.TextMsg and "@chatroom" not in ctx.FromUserName:
        honey.finish()
    content = ctx.Content
    if content == "" or content is None:
        honey.finish()

    if content[0] not in ".。?？":
        honey.finish()

    isAdmin = is_bot_master(ctx.CurrentWxid, ctx.ActionUserName) or ctx.ActionUserName == ctx.master

    content = content[1:]
    if content == 'reload' and isAdmin:
        cost = init_response()
        honey.finish(f"关键词回复重载完毕，用时{str(cost)[:5]} s")

    message_type = ''
    arg = content.split(' ')[0]
    if arg in ['pre', '前缀']:
        message_type = 'PreReply'
    elif arg in ['eq', '全等', '等于', 'set', 'reply']:
        message_type = 'EqualReply'
    elif arg in ['re', '正则']:
        message_type = 'RegReply'
    elif arg in ['con', '包含', 'contain', 'cont']:
        message_type = 'ContainReply'
    else:
        honey.finish()

    if isAdmin:
        pass
    elif count_owner_reply(ctx.ActionUserName, ctx.FromUserName) >= MAX:
        honey.finish(f"你能添加的关键词数已经达到上限 '{MAX}', 请删除多余关键字，输入.mine查看自己的关键字")

    args = content.split(' ')
    if len(args) < 2:
        if message_type != 'EqualReply':
            honey.finish("参数不足")

        arg = wait_get("arg", "请发送匹配词")
        if arg is None:
            honey.finish("已超时，请从头开始")
        elif arg.startswith("<msg><emoji fromusername"):
            arg = parseString(arg).getElementsByTagName('emoji')[0].getAttribute("md5")
        elif '<?xml version="1.0"?>' in arg:
            arg = parseString(arg).getElementsByTagName('img')[0].getAttribute("md5")
        elif '<' in arg:
            honey.finish("捣乱是吧，抓出去砍了")
        rule = arg
    else:
        rule = args[1]

    isImg = 'text'
    if len(args) < 3:
        response = wait_get("response", "请发送你想要的回复词，可以是图片")
        if response is None:
            honey.finish("已超时，请从头开始")
        elif response.startswith("<msg><emoji fromusername"):
            isImg = 'emoji'
            response = parseString(response).getElementsByTagName('emoji')[0].getAttribute("md5")
        elif '<?xml version="1.0"?>' in response:
            isImg = 'pic'
        elif '<' in response:
            honey.finish("捣乱是吧，抓出去砍了")
    else:
        response = ' '.join(args[2:])
        if '<' in response:
            honey.finish("捣乱是吧，抓出去砍了")

    if rule == '' or response == '':
        honey.finish("捣乱是吧，抓出去砍了")

    op = DB()
    if isImg == 'text':
        _id = op.insert_reply_message(rule, response, message_type,
                                      'text', ctx.FromUserName, ctx.ActionUserName)
        add_response(_id, rule, response, message_type, ctx.FromUserName, 'text')
    elif isImg == 'pic':
        _id = op.insert_reply_message(rule, "", message_type,
                                      'pic', ctx.FromUserName, ctx.ActionUserName, response)
        add_response(_id, rule, "", message_type, ctx.FromUserName, 'pic', response)
    elif isImg == 'emoji':
        _id = op.insert_reply_message(rule, "", message_type,
                                      'emoji', ctx.FromUserName, ctx.ActionUserName, response)
        add_response(_id, rule, "", message_type, ctx.FromUserName, 'emoji', response)
    honey.finish(f"""回复添加成功~""")


@plugin_receiver.wx
def go_reply(ctx: WeChatMsg):
    if ctx.Content[0] in ".。?？":
        return

    if ctx.MsgType == MsgTypes.TextMsg:
        content = ctx.Content
    elif ctx.MsgType == MsgTypes.EmojiMsg:
        content = ctx.emojiMd5
    elif ctx.MsgType == MsgTypes.ImgMsg:
        content = ctx.imgMd5
    else:
        return

    res_list: List[Reply] = []
    for reply in response_list:
        if reply.match(content, ctx.FromUserName):
            res_list.append(reply)

    if len(res_list) == 0:
        return
    choice(res_list).reply(ctx)
    return


@plugin_receiver.wx
def delete_reply(ctx: WeChatMsg):
    if ctx.MsgType != MsgTypes.TextMsg:
        return

    if ctx.Content[0] not in ".。?？":
        return

    content = ctx.Content[1:]
    if content.startswith("del") or content.startswith('删除'):
        args = content.split(' ')
        if len(args) < 2:
            sugar.Text(f"参数不足")
            return

        remove = False
        for reply in response_list:
            if reply.match(args[1], ctx.FromUserName):
                reply.remove()
                remove = True
        if remove:
            init_response()
            sugar.Text(f"对关键词\"{args[1]}\"的回复已删除")
        else:
            sugar.Text(f"没找到对应的关键字")
        return

    if not (ctx.Content == ".mine" or ctx.Content == "。mine"):
        return
    res = DB().get_my_keywords(ctx.ActionUserName, ctx.FromUserName)
    if len(res) == 0:
        sugar.Text(f"""暂无关键字""")
    else:
        end = '\n'
        sugar.Text(f"""你的关键字:\n----------\n{end.join([i['rules'] for i in res])}""")
