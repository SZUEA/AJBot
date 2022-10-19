"""短网址0e7.cn
"""

import requests
from EAbotoy import Action, sugar
from EAbotoy.contrib import plugin_receiver
from EAbotoy.model import WeChatMsg
from plugins.bot_reply import is_bot_master

action = Action()

@plugin_receiver.wx
def check_join_code(ctx: WeChatMsg):
    if ctx.Content[0] not in ".。?？":
        return

    content = ctx.Content[1:]
    if content.startswith("short"):

        isAdmin = is_bot_master(ctx.CurrentWxid, ctx.ActionUserName) or ctx.ActionUserName == ctx.master

        if not isAdmin:
            return

        if content.startswith("shorts"):
            args = content.split(' ')
            if len(args) < 3:
                sugar.Text(f"参数不足")
                return
            resp = requests.get(
                "https://0e7.cn",
                params={"s": args[1], "c": args[2], 'token': '9p4THrA975JVPjyAcjLp8tDDFhPzXFm7'}
            )
        elif content.startswith("shortn"):
            args = content.split(' ')
            if len(args) < 3:
                sugar.Text(f"参数不足")
                return
            resp = requests.get(
                "https://0e7.cn",
                params={"n": args[1], "c": args[2], 'token': '9p4THrA975JVPjyAcjLp8tDDFhPzXFm7'}
            )
        elif content.startswith("shortd"):
            url = content[7:]

            resp = requests.get(
                "https://0e7.cn",
                params={"d": url, 'token': '9p4THrA975JVPjyAcjLp8tDDFhPzXFm7'}
            )
        else:
            url = content[6:]
            resp = requests.get(
                "https://0e7.cn",
                params={"c": url, 'token': '9p4THrA975JVPjyAcjLp8tDDFhPzXFm7'}
            )
        res = resp.json()
        sugar.Text(res["result"])
    return
