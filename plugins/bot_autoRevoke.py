import os
import random
import re
import time

from EAbotoy import Action, jconfig
from EAbotoy.decorators import from_botself, in_content
from EAbotoy.model import WeChatMsg


# 包含指定关键字时撤回，假设关键字为 revoke
# revoke 随机0-90s撤回
# revoke[10] 10s后撤回


def receive_group_msg(ctx: WeChatMsg):
    if 'revoke' not in ctx.Content:
        return
    delay = re.findall(r"^![\[【（({]?(\d+)[]】）)}]?", ctx.Content)


    if delay:
        delay = min(int(delay[0]), 60)
    else:
        random.seed(os.urandom(30))
        delay = random.randint(5, 15)
    time.sleep(delay)
    Action(ctx.CurrentWxid).revokeMsg(ctx)
