from ..model import WeChatMsg


def from_botself(func=None):
    """只处理机器人自身的消息 GroupMsg, FriendMsg"""
    if func is None:
        return from_botself

    def inner(ctx: WeChatMsg):
        if ctx.ActionUserName == ctx.CurrentWxid:
            return func(ctx)
        return None

    return inner
