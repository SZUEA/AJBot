from ..model import WeChatMsg


def from_these_users(*users):
    """仅接受来自这些用户的消息 GroupMsg, FriendMsg"""

    def deco(func):
        def inner(ctx: WeChatMsg):
            nonlocal users

            if ctx.ActionUserName in users:
                return func(ctx)
            return None

        return inner

    return deco
