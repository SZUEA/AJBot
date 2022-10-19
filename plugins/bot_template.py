"""我是模板
"""
import os
from queue import deque  # type:ignore

from EAbotoy import Action, MsgTypes, EventNames, Text
from EAbotoy import decorators as deco

# 自动消息加一功能, 支持文字消息和图片消息
from EAbotoy.decorators import these_msgtypes
from EAbotoy.model import WeChatMsg, EventMsg

action = Action(os.environ["wxid"], is_use_queue=True)


@these_msgtypes(MsgTypes.TextMsg)  # 指定消息类型
@deco.in_content("我是模板")  # 一些装饰器
def receive_wx_msg(ctx: WeChatMsg):  # 函数名字只能是这个才能触发
    pass


