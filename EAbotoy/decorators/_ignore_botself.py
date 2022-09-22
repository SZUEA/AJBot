from ..model import WeChatMsg


def ignore_botself(func=None):
    """忽略机器人自身的消息 GroupMsg, FriendMsg"""
    if func is None:
        return ignore_botself

    def inner(ctx: WeChatMsg):
        if ctx.ActionUserName != ctx.CurrentWxid:
            return func(ctx)
        return None
    return inner
