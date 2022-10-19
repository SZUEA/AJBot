#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-04-14 21:30:20
@LastEditors    : yanyongyu
@LastEditTime   : 2020-04-14 21:30:20
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"
__doc__ = '自然语言通知'

import re
import json
from datetime import datetime, timedelta

from EAbotoy import MsgTypes, WeChatMsg, logger, Text
from EAbotoy.decorators import these_msgtypes, re_findall
from .commands import alarm

from .nlp_time.TimeNormalizer import TimeNormalizer

tn = TimeNormalizer()


@re_findall(r"(?:提醒我)|(?:通知我)|(?:叫我)")
@these_msgtypes(MsgTypes.TextMsg)
def receive_wx_msg(ctx: WeChatMsg):
    stripped_arg = ctx.Content.strip()

    # 将消息分为两部分（时间|事件）
    time, target = re.split(r"(?:提醒)|(?:通知)|(?:叫)", stripped_arg, maxsplit=1)

    # 解析时间
    try:
        time_json = json.loads(tn.parse(target=time))
    except Exception:
        # Text("哎哟，没看懂，说点人话吧")
        return
    target = target.lstrip("我") or "干事情"
    if "error" in time_json.keys() or not target:
        # Text("哎哟，没看懂，说点人话吧")
        return
    # 时间差转换为时间点
    elif time_json['type'] == "timedelta":
        time_diff = time_json['timedelta']
        time_diff = timedelta(days=time_diff['day'],
                              hours=time_diff['hour'],
                              minutes=time_diff['minute'],
                              seconds=time_diff['second'])
        time_target = datetime.now() + time_diff
    elif time_json['type'] == "timestamp":
        time_target = datetime.strptime(time_json['timestamp'],
                                        "%Y-%m-%d %H:%M:%S")
        # 默认时间点为中午12点
        if not re.search(r"[\d+一二两三四五六七八九十]+点", time) \
                and time_target.hour == 0 and time_target.minute == 0 and time_target.second == 0:
            time_target += timedelta(hours=12)
    else:
        raise

    logger.info(f"获取到时间{time_target}, 将会定时进行通知")
    alarm(time_target, target, ctx)
