from ..model import WeChatMsg
from ..parser import friend as fp
from ..parser import group as gp


def startswith(string: str):
    """Content以指定前缀开头  GroupMsg, FriendMsg
    :param string: 前缀字符串, 会解析图片消息的Content
    """

    def deco(func):
        def inner(ctx: WeChatMsg):
            assert isinstance(ctx, WeChatMsg)
            content = ctx.Content

            if content.startswith(string):
                return func(ctx)
            return None

        return inner

    return deco
