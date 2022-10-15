from ..model import WeChatMsg


def from_these_groups(*groups):
    """只接受这些群组的消息 GroupMsg"""

    def deco(func):
        async def inner(ctx: WeChatMsg):
            nonlocal groups
            if not ctx.IsGroup:
                return None
            from_group = ctx.FromUserName
            if from_group in groups:
                return await func(ctx)
            return None

        return inner

    return deco
