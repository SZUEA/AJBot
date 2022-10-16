"""一些用于接收函数的装饰器"""
from ._equal_content import equal_content
from ._from_phone import from_phone
from ._from_these_groups import from_these_groups
from ._from_these_users import from_these_users
from ._ignore_admin import ignore_admin
from ._ignore_these_groups import ignore_these_groups
from ._ignore_these_users import ignore_these_users
from ._in_content import in_content
from ._need_action import need_action
from ._on_regexp import on_regexp
from ._queued_up import queued_up
from ._re_findall import re_findall
from ._re_match import re_match
from ._startswith import startswith
from ._these_msgtypes import these_msgtypes
from ._on_command import on_command

__all__ = [
    "equal_content",
    "on_command",
    "from_these_groups",
    "from_these_users",
    "ignore_these_users",
    "ignore_these_groups",
    "in_content",
    "on_regexp",
    "queued_up",
    "startswith",
    "these_msgtypes",
    "need_action",
    "re_findall",
    "re_match",
]
