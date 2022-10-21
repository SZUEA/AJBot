"""我是模板
"""
import os
import re
from queue import deque  # type:ignore

from EAbotoy import Action, MsgTypes, EventNames, Text
from EAbotoy import decorators as deco

# 自动消息加一功能, 支持文字消息和图片消息
from EAbotoy.decorators import these_msgtypes
from EAbotoy.model import WeChatMsg, EventMsg
from plugins.bot_reply import is_bot_master

action = Action(os.environ["wxid"], is_use_queue=True)


@these_msgtypes(MsgTypes.TextMsg)  # 指定消息类型
@deco.startswith("轰炸")  # 一些装饰器
def receive_wx_msg(ctx: WeChatMsg):  # 函数名字只能是这个才能触发
    isAdmin = is_bot_master(ctx.CurrentWxid, ctx.ActionUserName) or ctx.ActionUserName == ctx.master
    if not isAdmin:
        return

    arg = re.findall(r"^轰炸(.+?)\s*(\d*)$", ctx.Content)[0]
    time = int(arg[1] or 3)
    if time > 10:
        time = 3
    for i in range(time):
        Text(arg[0])
