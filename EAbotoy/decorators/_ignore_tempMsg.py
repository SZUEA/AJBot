from ..model import WeChatMsg


def ignore_FriendMsg(func=None):
    """忽略私聊信息 FriendMsg"""
    if func is None:
        return ignore_FriendMsg

    def inner(ctx: WeChatMsg):
        if "@chatroom" in ctx.FromUserName:
            return func(ctx)
        return None

    return inner
