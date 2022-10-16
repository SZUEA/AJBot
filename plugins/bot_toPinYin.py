"""汉字转拼音：拼音{汉字}"""
import requests

from EAbotoy.async_decorators import on_command
from EAbotoy.collection import MsgTypes
from EAbotoy.decorators import startswith, these_msgtypes
from EAbotoy.model import WeChatMsg
from EAbotoy.sugar import Text


@on_command("拼音")
def receive_wx_msg(ctx: WeChatMsg, arg, command):
    word = arg
    if word:
        resp = requests.get(
            "https://v2.alapi.cn/api/pinyin",
            params={"word": word, 'token': '3jqctpm9i4IwXwJp'}
        )
        res = resp.json()
        word = res["data"]["word"]
        pinyin = res["data"]["pinyin"]
        Text(f"{word}\n{pinyin}")
