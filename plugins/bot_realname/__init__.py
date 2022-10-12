"""实名插件
"""
import os
from EAbotoy import Action, MsgTypes, sugar
from EAbotoy.contrib import plugin_receiver
from EAbotoy.decorators import ignore_botself
from EAbotoy.model import WeChatMsg
from .db import DB
from plugins.bot_reply import is_bot_master

action = Action()


@plugin_receiver.wx
@ignore_botself
def query_real_name(ctx: WeChatMsg):
    if ctx.MsgType != MsgTypes.TextMsg:
        return

    if not ctx.isAtMsg:
        return

    if "是谁" in ctx.Content:
        real_name = DB().get_real_name(ctx.atUserIds[0])
        if len(real_name) == 0:
            action.sendWxText(toUserName=ctx.FromUserName,
                              content=f'''{ctx.atUserNames[0]}未实名''',
                              atUser=ctx.atUserIds[0])
        else:
            action.sendWxText(toUserName=ctx.FromUserName,
                              content=f'''{ctx.atUserNames[0]}是{real_name[0]['name']}''',
                              atUser=ctx.atUserIds[0])


@plugin_receiver.wx
@ignore_botself
def add_real_name(ctx: WeChatMsg):
    if not ctx.isAtMsg:
        return

    if ctx.Content[0] not in ".。?？":
        return

    isAdmin = is_bot_master(ctx.CurrentWxid, ctx.ActionUserName) or ctx.ActionUserName == ctx.master

    if not isAdmin:
        return

    content = ctx.Content[1:]
    if content.startswith("reg") or content.startswith('实名'):
        args = content.split(' ')
        if len(args) < 3:
            sugar.Text(f"参数不足")
            return

        else:
            DB().add_real_name(ctx.atUserIds[0], args[1])
            action.sendWxText(toUserName=ctx.FromUserName,
                              content=f'''{ctx.atUserNames[0]}实名“{args[1]}”成功''',
                              atUser=ctx.atUserIds[0])
        return

