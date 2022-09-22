from typing import Any, Callable, Optional, Union

from .model import EventMsg, WeChatMsg


"""wx消息接收函数"""
T_WxMsgReceiver = Callable[[WeChatMsg], Any]


"""事件接收函数"""
T_EventReceiver = Callable[[EventMsg], Any]

"""通用接收函数"""
T_GeneralReceiver = Union[T_EventReceiver, T_WxMsgReceiver]


"""wx消息接收函数"""
T_WxMsgMiddleware = Callable[[WeChatMsg], Optional[WeChatMsg]]

"""事件中间件"""
T_EventMiddleware = Callable[[EventMsg], Optional[EventMsg]]

