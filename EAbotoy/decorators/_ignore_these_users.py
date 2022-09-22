from ..model import WeChatMsg


def ignore_these_users(*users):
    """忽略这些人的消息 GroupMsg, FriendMsg"""

    def deco(func):
        def inner(ctx: WeChatMsg):
            nonlocal users

            if ctx.ActionUserName not in users:
                return func(ctx)
            return None

        return inner

    return deco
