"""事件处理
"""
import os
from queue import deque  # type:ignore

from EAbotoy import Action, MsgTypes, EventNames, Text

from EAbotoy.model import WeChatMsg, EventMsg


def receive_events(ctx: EventMsg):  # 函数名字只能是这个才能触发
    pass
    if ctx.EventName == EventNames.ON_EVENT_PAT_MSG and ctx.PattedUserName == ctx.CurrentWxid:
        Text("再拍我就拍死你[发怒]")
    elif ctx.EventName == EventNames.ON_EVENT_CHATROOM_INVITE_OTHER:
        Text(f"欢迎{ctx.data['InvitedNickName']} 加入，(^з^)")
