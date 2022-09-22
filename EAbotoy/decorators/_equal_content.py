from ..collection import MsgTypes
from ..model import WeChatMsg
from ..parser import friend as fp
from ..parser import group as gp


def equal_content(string: str):
    """发送的内容与指定字符串相等时 GroupMsg, FriendMsg"""

    def deco(func):
        def inner(ctx: WeChatMsg):

            if ctx.MsgType != MsgTypes.TextMsg:
                return
            if ctx.Content == string:
                return func(ctx)

            return None
        return inner
    return deco
