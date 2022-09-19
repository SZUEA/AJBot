"""汉字转拼音：拼音{汉字}"""
import httpx
import requests
from EAbotoy import GroupMsg
from EAbotoy.collection import MsgTypes
from EAbotoy.decorators import ignore_botself, startswith, these_msgtypes
from EAbotoy.sugar import Text


@ignore_botself
@these_msgtypes(MsgTypes.TextMsg)
@startswith("拼音")
def receive_group_msg(ctx: GroupMsg):
    word = ctx.Content[2:]
    if word:
        resp = requests.get(
            "https://v2.alapi.cn/api/pinyin",
            params={"word": word, 'token': '3jqctpm9i4IwXwJp'},
        )
        res = resp.json()
        word = res["data"]["word"]
        pinyin = res["data"]["pinyin"]
        Text(f"{word}\n{pinyin}")
