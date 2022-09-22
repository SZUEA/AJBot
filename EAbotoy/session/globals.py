from contextvars import ContextVar
from typing import Union

from ..model import WeChatMsg
from ..utils import bind_contextvar
from .base import Session

_ctx: ContextVar[Union[WeChatMsg]] = ContextVar("ctx")
_session: ContextVar[Session] = ContextVar("session")

ctx: Union[WeChatMsg] = bind_contextvar(_ctx)  # type:ignore
session: Session = bind_contextvar(_session)  # type:ignore
