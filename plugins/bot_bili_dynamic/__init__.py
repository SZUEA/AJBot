"""动态订阅啊啊啊
"""
import asyncio
import os
import re
from queue import deque  # type:ignore

from bilireq.exceptions import ResponseCodeError

from EAbotoy import Text
from EAbotoy.session import ctx, Prompt, SessionHandler, session
from .database import DB as db
from bilireq.user import get_user_info

from .api import API
from ..bot_bili_pusher import dy_sched_up

bilibili_handler = SessionHandler().receive_wx_msg()

white_groups = ['18728854191@chatroom', '18803656716@chatroom']


@bilibili_handler.handle
def _():
    if not ctx.IsGroup:
        bilibili_handler.finish()
    from_group = ctx.FromUserName
    if from_group not in white_groups:
        bilibili_handler.finish()

    if ctx.Content.startswith("订阅up") or ctx.Content.startswith("b站订阅"):
        asyncio.run(add_sub())
    elif ctx.Content.startswith("取关up"):
        asyncio.run(del_sub())
    elif ctx.Content == "关注列表":
        asyncio.run(sub_list())
    bilibili_handler.finish()


def get_UID(keyword_len: int):
    try:
        uid = re.findall(r"UID:(\d+)", ctx.Content)[0]
    except Exception:
        uid = None

    if uid is not None:
        return uid
    keyword = ctx.Content[keyword_len:]
    ups = API.search_up_by_keyword(keyword)
    if not ups:
        bilibili_handler.finish("未找到相关UP，请重试或修改指令内容")
    if len(ups) == 1:
        uid = ups[0].mid
    else:
        choose_msgs = []
        for idx, up in enumerate(ups[:10]):
            choose_msgs.append(f"{idx} 【{up.name}】")
        choose = session.want(
            "choose", "发送对应序号选择UP主:\n" + "\n".join(choose_msgs), timeout=60
        )
        if isinstance(choose, str) and choose.isdigit():
            try:
                uid = ups[int(choose)].mid
            except IndexError:
                bilibili_handler.finish("序号错误，已退出当前会话!")
        else:
            bilibili_handler.finish("序号错误，已退出当前会话!")
    return uid


async def add_sub():
    uid = get_UID(keyword_len=4)
    if uid is None:
        bilibili_handler.finish()
    user = await db.get_user(uid=uid)
    name = user and user.name
    if not name:
        try:
            name = (await get_user_info(uid, reqtype="web"))["name"]
        except ResponseCodeError as e:
            if e.code == -400 or e.code == -404:
                bilibili_handler.finish("UID不存在，注意UID不是房间号")
            elif e.code == -412:
                bilibili_handler.finish("操作过于频繁IP暂时被风控，请半小时后再尝试")
            else:
                bilibili_handler.finish(f"未知错误，请联系开发者反馈")
    result = await db.add_sub(
        uid=uid,
        type='group',
        type_id=ctx.GroupId,
        bot_id=ctx.CurrentWxid,
        name=name,
        live=True,
        dynamic=True,
        at=False,
    )
    if result:
        bilibili_handler.finish(f"已关注 {name}（{uid}）")
        await dy_sched_up(int(uid))
    bilibili_handler.finish(f"{name}（{uid}）已经关注过了")


async def del_sub():
    """根据 UID 删除 UP 主订阅"""
    uid = get_UID(keyword_len=4)
    if uid is None:
        bilibili_handler.finish()

    name = getattr(await db.get_user(uid=uid), "name", None)
    if name:
        result = await db.delete_sub(
            uid=uid, type='group', type_id=ctx.GroupId
        )
    else:
        result = False

    if result:
        bilibili_handler.finish(f"已取关 {name}（{uid}）")
    bilibili_handler.finish(f"UID（{uid}）未关注")


async def sub_list():
    """发送当前位置的订阅列表"""
    message = "关注列表（所有群/好友都是分开的）\n" \
              "~~~~~~~~~~~~~~~~~~~~~\n"
    subs = await db.get_sub_list('group', ctx.GroupId)
    for sub in subs:
        user = await db.get_user(uid=sub.uid)
        assert user is not None
        message += (
            f"{user.name}（{user.uid}\n"
            # f"直播：{'开' if sub.live else '关'}，"
            # f"动态：{'开' if sub.dynamic else '关'}，"
            # f"全体：{'开' if sub.at else '关'}\n"
        )
    bilibili_handler.finish(message.strip())
