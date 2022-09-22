"""以复读开头bot会复读你说的话
"""
import os
from queue import deque  # type:ignore

from EAbotoy import Action, MsgTypes
from EAbotoy import decorators as deco

# 自动消息加一功能, 支持文字消息和图片消息
from EAbotoy.decorators import these_msgtypes
from EAbotoy.model import WeChatMsg

action = Action(os.environ["wxid"], is_use_queue=True)


@deco.ignore_botself
@these_msgtypes(MsgTypes.TextMsg)
@deco.in_content("复读")
def receive_wx_msg(ctx: WeChatMsg):
    if ctx.Content.startswith("复读"):
        content = ctx.Content.replace("复读", "")
    else:
        content = ctx.Content
    action.sendWxText(toUserName=ctx.FromUserName, content=content)
