import random
from pathlib import Path

import ujson as json
from EAbotoy import WeChatMsg
from EAbotoy import decorators as deco
from EAbotoy.session import SessionHandler, ctx

curFileDir = Path(__file__).parent  # 当前文件路径

with open(curFileDir / "onset.json", "r", encoding="utf-8") as f:
    data: list = json.load(f)["data"]

handler = SessionHandler(
    deco.startswith("发病")
).receive_wx_msg()
white_groups = ['18728854191@chatroom', '18803656716@chatroom']


@handler.handle
def main():
    from_group = ctx.FromUserName
    if from_group not in white_groups:
        handler.finish()

    name = ctx.Content[2:].strip()
    if name.isspace() or len(name) == 0:
        handler.finish("要对谁发病捏?")
    content: str = random.choice(data)["content"]
    handler.finish(content.replace("{{user.name}}", name))
