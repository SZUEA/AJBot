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
dev = ''
RESOURCES_BASE_PATH = "./resources/welcome"


@these_msgtypes(MsgTypes.TextMsg)
@deco.in_content(r".join ea")
def receive_wx_msg(ctx: WeChatMsg):
    if ctx.Content.startswith(".join ea"):
        pass
