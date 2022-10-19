#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-04-14 21:00:04
@LastEditors: yanyongyu
@LastEditTime: 2020-04-14 21:34:58
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from datetime import datetime, timedelta
from random import choice

# from aiocqhttp import Event as CQEvent
# from nonebot import get_bot, scheduler
# from nonebot import on_command, CommandSession
# from nonebot.helpers import render_expression

from EAbotoy import jconfig, Text, Action, WeChatMsg
from EAbotoy.schedule import scheduler

assert scheduler, "Apscheduler not installed! Try using `pip install nonebot[scheduler]` to install it."

action = Action()

on_planed = {}


def remind(target: str, toUser: str, userNickName: str, userId: str):
    """
    Send shake and remind notification to user
    """

    on_planed[userId] = on_planed.get(userId, 1) - 1

    # 发送提醒
    action.sendWxText(toUserName=toUser,
                      content=choice(EXPR_REMIND).replace("{action}", target) + f' @{userNickName}',
                      atUser=userId)
    # 发送提醒


def alarm(time: datetime, target: str, ctx: WeChatMsg):
    # 过滤时间
    now = datetime.now()
    # 过去的时间

    if time <= now:
        Text(choice(EXPR_COULD_NOT))
        return
    # 超过30天的时间
    elif time - now > timedelta(days=5):
        Text(choice(EXPR_TOO_LONG))
        return

    if on_planed.get(ctx.ActionUserName, 0) > 0:
        if ctx.master != ctx.FromUserName:
            Text("哎哟，我的记性还不太好，一个人只能记住一次提醒，等之后再来吧")
            return
    on_planed[ctx.ActionUserName] = on_planed.get(ctx.ActionUserName, 0) + 1
    # 添加job
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    scheduler.add_job(  # type: ignore
        remind,
        "date",
        run_date=time,
        args=[target, ctx.FromUserName, ctx.ActionNickName or "你", ctx.ActionUserName])
    action.sendWxText(ctx.FromUserName,
                      f"提醒创建成功：\n"
                      f"> 提醒时间：{time_str}\n"
                      f"> 内容：{target}")


nickname = getattr(jconfig, "NICKNAME", "我")
nickname = nickname if nickname is not None else "我"

EXPR_COULD_NOT = (f"哎鸭，{nickname}没有时光机，这个时间没办法提醒你。",
                  f"你这是要穿越吗？这个时间{nickname}没办法提醒你。")

EXPR_TOO_LONG = ("很抱歉，现在暂时不能设置超过5天的提醒呢。",
                 f"……时间这么久的话，{nickname}可能也记不住。还是换个时间吧。")

EXPR_OK = ("遵命！我会在{time}叫你{action}！\n", "好！我会在{time}提醒你{action}！\n",
           "没问题！我一定会在{time}通知你{action}。\n", "好鸭~ 我会准时在{time}提醒你{action}。\n",
           "嗯嗯！我会在{time}准时叫你{action}哒\n", "好哦！我会在{time}准时叫你{action}~\n")

EXPR_REMIND = ("提醒通知：\n提醒时间到啦！该{action}了！", "提醒通知：\n你设置的提醒时间已经到了~ 赶快{action}！",
               "提醒通知：\n你应该没有忘记{action}吧？", "提醒通知：\n你定下的提醒时间已经到啦！快{action}吧！")
