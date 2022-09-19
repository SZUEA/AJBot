import os
import random
import re
import time

from EAbotoy import Action, GroupMsg, jconfig
from EAbotoy.decorators import from_botself, in_content

_KEYWORD = "revoke"

# 包含指定关键字时撤回，假设关键字为 revoke
# revoke 随机0-90s撤回
# revoke[10] 10s后撤回


def receive_group_msg(ctx: GroupMsg):
    if 'revoke' not in ctx.Content:
        return
    delay = re.findall(_KEYWORD + r"\[(\d+)\]", ctx.Content)
    if delay:
        delay = min(int(delay[0]), 90)
    else:
        random.seed(os.urandom(30))
        delay = random.randint(30, 80)
    time.sleep(delay)
    Action(ctx.CurrentQQ).revokeGroupMsg(
        group=ctx.FromGroupId,
        msgSeq=ctx.MsgSeq,
        msgRandom=ctx.MsgRandom,
    )
