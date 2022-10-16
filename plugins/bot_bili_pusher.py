"""我是模板
"""
import base64
import os
from io import BytesIO
from queue import deque  # type:ignore

import requests
from grpc import StatusCode
from grpc.aio import AioRpcError

from EAbotoy import logger, WeChatMsg, AsyncAction, Text
from EAbotoy.async_decorators import on_command
from EAbotoy.schedule import async_scheduler
from utils.browser import get_dynamic_screenshot
from .bot_bili_dynamic.database import DB as db
from .bot_bili_dynamic.database import dynamic_offset as offset
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType
from .bot_bili_dynamic.sub_db import DB as sub_DB
from .bot_bili_dynamic.api import API
from .bot_reply import is_bot_master

action = AsyncAction(os.environ["wxid"])


@on_command("查动态")
async def receive_wx_msg(ctx: WeChatMsg, arg, command):
    isAdmin = ctx.ActionUserName == ctx.master or is_bot_master(ctx.CurrentWxid, ctx.ActionUserName)
    if isAdmin:
        await dy_sched()


def send_img(group, imageUrl):
    res = requests.get(imageUrl)
    base = str(base64.b64encode(BytesIO(res.content).read()), encoding="utf-8")
    action.sendImg(group, imageBase64=base)


async def dy_sched_up(uid: int):
    user = await db.get_user(uid=uid)
    assert user is not None
    name = user.name

    logger.debug(f"爬取动态 {name}（{uid}）")
    try:
        # 获取 UP 最新动态列表
        dynamics = (
            await grpc_get_user_dynamics(uid, timeout=10)
        ).list
    except AioRpcError as e:
        if e.code() == StatusCode.DEADLINE_EXCEEDED:
            logger.error(f"爬取动态超时，将在下个轮询中重试")
            return
        raise

    if not dynamics:  # 没发过动态
        if uid in offset and offset[uid] == -1:  # 不记录会导致第一次发动态不推送
            offset[uid] = 0
        return
    # 更新昵称
    name = dynamics[0].modules[0].module_author.author.name

    if uid not in offset:  # 已删除
        return
    elif offset[uid] == -1:  # 第一次爬取
        logger.info(f"初始化{uid}的offset了")
        if len(dynamics) == 1:  # 只有一条动态
            offset[uid] = int(dynamics[0].extend.dyn_id_str)
        else:  # 第一个可能是置顶动态，但置顶也可能是最新一条，所以取前两条的最大值
            offset[uid] = max(
                int(dynamics[0].extend.dyn_id_str), int(dynamics[1].extend.dyn_id_str)
            )
        return

    dynamic = None
    isSend = False
    for dynamic in dynamics[::-1]:  # 动态从旧到新排列
        dynamic_id = int(dynamic.extend.dyn_id_str)
        if dynamic_id > offset[uid]:
            isSend = True
            logger.info(f"检测到新动态（{dynamic_id}）：{name}（{uid}）")
            url = f"https://t.bilibili.com/{dynamic_id}"
            image = await get_dynamic_screenshot(dynamic_id)
            if image is None:
                logger.debug(f"动态不存在，已跳过：{url}")
                return

            type_msg = {
                0: "发布了新动态",
                DynamicType.forward: "转发了一条动态",
                DynamicType.word: "发布了新文字动态",
                DynamicType.draw: "发布了新图文动态",
                DynamicType.av: "发布了新投稿",
                DynamicType.article: "发布了新专栏",
                DynamicType.music: "发布了新音频",
            }
            message = (
                    f"{name} {type_msg.get(dynamic.card_type, type_msg[0])}：\n"
                    + f"\n{url}"
            )

            push_list = await db.get_push_list(uid, "dynamic")
            for sets in push_list:
                await action.sendWxText(sets.type_id, message)
                base = str(base64.b64encode(image), encoding="utf-8")
                await action.sendImg(sets.type_id, imageBase64=base)

            offset[uid] = dynamic_id
    if dynamic:
        await db.update_user(uid, name)
    return isSend


async def dy_sched():
    """动态推送"""
    uids = await db.get_uid_list("dynamic")
    if not uids:
        return
    for uid in uids:
        await dy_sched_up(uid)


async def check_up_video(uid):
    video = API.get_latest_video_by_mid(uid)
    if video is None:
        return
    sub_db = sub_DB()
    if sub_db.judge_up_updated(uid, video.created):
        if action is not None:
            for group in sub_db.get_gids_by_up_mid(uid):
                send_img(
                    group,
                    imageUrl=video.pic,
                )
                await action.sendApp(group,
                                     '<appmsg appid="wxcb8d4298c6a09bcb" sdkver="0">\n\t\t'
                                     f'<title>{video.title}</title>\n\t\t'
                                     f'<des>UP主：{video.author}\n{video.description}</des>'
                                     '\n\t\t<username />\n\t\t'
                                     '<action>view</action>\n\t\t'
                                     '<type>4</type>\n\t\t'
                                     '<showtype>0</showtype>\n\t\t'
                                     f'<content />\n\t\t<url>https://m.bilibili.com/video/{video.bvid}</url>\n\t\t'
                                     '</appmsg>')


async def video_sched():
    """动态推送"""
    uids = await db.get_uid_list("dynamic")
    if not uids:
        return
    for uid in uids:
        await check_up_video(uid)


async_scheduler.add_job(video_sched, "interval", minutes=10)
async_scheduler.add_job(dy_sched, "interval", minutes=5)
