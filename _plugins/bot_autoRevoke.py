import os
import random
import re
import time

from EAbotoy import Action, MsgTypes
from EAbotoy.model import WeChatMsg


# 包含指定关键字时撤回，假设关键字为 revoke
# revoke 随机0-90s撤回
# revoke[10] 10s后撤回


def receive_wx_msg(ctx: WeChatMsg):
    if ctx.MsgType != MsgTypes.TextMsg:
        return
    if not ctx.Content.startswith('!') and not ctx.Content.startswith("！"):
        return
    delay = re.findall(r"^[!！][\[【（({]?(\d+)[]】）)}]?", ctx.Content)

    if delay:
        delay = min(int(delay[0]), 60)
    else:
        random.seed(os.urandom(30))
        delay = random.randint(5, 15)
    time.sleep(delay)
    Action(ctx.CurrentWxid).revokeMsg(ctx)
