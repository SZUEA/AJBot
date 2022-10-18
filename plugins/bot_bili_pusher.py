"""我是模板
"""
import asyncio
import base64
import os
import traceback
from io import BytesIO
from queue import deque  # type:ignore
from threading import Thread

import requests
from grpc import StatusCode
from grpc.aio import AioRpcError

from EAbotoy import logger, WeChatMsg, Text, Action
from EAbotoy.async_decorators import on_command
from EAbotoy.schedule import scheduler
from utils.browser import get_dynamic_screenshot, get_browser, init_browser
from .bot_bili_dynamic.database import DB as db
from .bot_bili_dynamic.database import dynamic_offset as offset
from bilireq.grpc.dynamic import grpc_get_user_dynamics
from bilireq.grpc.protos.bilibili.app.dynamic.v2.dynamic_pb2 import DynamicType
from .bot_bili_dynamic.sub_db import DB as sub_DB
from .bot_bili_dynamic.api import API
from .bot_reply import is_bot_master

action = Action(os.environ["wxid"])


@on_command("查动态")
async def receive_wx_msg(ctx: WeChatMsg, arg, command):
    isAdmin = ctx.ActionUserName == ctx.master or is_bot_master(ctx.CurrentWxid, ctx.ActionUserName)
    if isAdmin:
        await dy_sched()
    else:
        Text("非admin不能查询")


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
        logger.info(f"初始化{name}的最新动态")
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
            if dynamic.card_type == DynamicType.av:
                continue
            isSend = True
            logger.info(f"检测到新动态（{dynamic_id}）：{name}（{uid}）")

            try:
                text = "\n".join([" ".join([j.text for j in i]) for i in
                                  [module.module_desc.desc for module in dynamic.modules] if len(i) != 0])
            except Exception as e:
                logger.warning(traceback.format_exc())
                text = f"{name} 的新动态"

            try:
                image = await get_dynamic_screenshot(dynamic_id)
            except Exception as e:
                logger.warning(traceback.format_exc())
                image = None

            push_list = await db.get_push_list(uid, "dynamic")
            for sets in push_list:
                action.sendApp(sets.type_id,
                               '<appmsg appid="wxcb8d4298c6a09bcb" sdkver="0">\n\t\t'
                               f'<title>{text}</title>\n\t\t'
                               f'<des>UP主：{name}</des>'
                               '<username />\n\t\t<action>view</action>\n\t\t<type>5</type>\n\t\t'
                               '<showtype>0</showtype>\n\t\t'
                               f'<content />\n\t\t<url>https://t.bilibili.com/{dynamic_id}</url>\n\t\t'
                               '<appattach>\n\t\t\t<attachid />\n\t\t\t'
                               '<cdnthumburl>3057020100044b3049020100020421423bf002032f80290204e6'
                               '833cb70204634e9da7042435623233323837362d663830352d346233352d626438'
                               '612d643661343239343363666433020401290a020201000405004c53d900</cdnthumburl>\n\t\t\t'
                               '<cdnthumbmd5>5d538bd737e8e6c09323c560b386360c</cdnthumbmd5>\n\t\t\t'
                               '<cdnthumblength>5492</cdnthumblength>\n\t\t\t'
                               '<cdnthumbheight>117</cdnthumbheight>\n\t\t\t<cdnthumbwidth>120</cdnthumbwidth>\n\t\t\t'
                               '<cdnthumbaeskey>9093651ad791aabe0c1852a3678a2e3e</cdnthumbaeskey>\n\t\t\t'
                               '<aeskey>9093651ad791aabe0c1852a3678a2e3e</aeskey>\n\t\t\t<encryver>1</encryver>'
                               '\n\t\t\t<fileext />\n\t\t\t<islargefilemsg>0</islargefilemsg>\n\t\t</appattach>\n\t\t'
                               '</appmsg>'
                               )

                if image is not None:
                    base = str(base64.b64encode(image), encoding="utf-8")
                    action.sendImg(sets.type_id, imageBase64=base)

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
        for group in sub_db.get_gids_by_up_mid(uid):
            action.sendApp(group,
                           '<appmsg appid="wxcb8d4298c6a09bcb" sdkver="0">\n\t\t'
                           f'<title>{video.title}</title>\n\t\t'
                           f'<des>UP主：{video.author}\n{video.description}</des>'
                           '<username />\n\t\t<action>view</action>\n\t\t<type>4</type>\n\t\t<showtype>0</showtype>\n\t\t'
                           '<content />\n\t\t<url>https://m.bilibili.com/video/{video.bvid}</url>\n\t\t'
                           '<appattach>\n\t\t\t<attachid />\n\t\t\t'
                           '<cdnthumburl>3057020100044b3049020100020421423bf002032f80290204e6'
                           '833cb70204634e9da7042435623233323837362d663830352d346233352d626438'
                           '612d643661343239343363666433020401290a020201000405004c53d900</cdnthumburl>\n\t\t\t'
                           '<cdnthumbmd5>5d538bd737e8e6c09323c560b386360c</cdnthumbmd5>\n\t\t\t'
                           '<cdnthumblength>5492</cdnthumblength>\n\t\t\t'
                           '<cdnthumbheight>117</cdnthumbheight>\n\t\t\t<cdnthumbwidth>120</cdnthumbwidth>\n\t\t\t'
                           '<cdnthumbaeskey>9093651ad791aabe0c1852a3678a2e3e</cdnthumbaeskey>\n\t\t\t'
                           '<aeskey>9093651ad791aabe0c1852a3678a2e3e</aeskey>\n\t\t\t<encryver>1</encryver>'
                           '\n\t\t\t<fileext />\n\t\t\t<islargefilemsg>0</islargefilemsg>\n\t\t</appattach>\n\t\t'
                           '</appmsg>'
                           )
            send_img(
                group,
                imageUrl=video.pic,
            )


async def video_sched():
    """动态推送"""
    uids = await db.get_uid_list("dynamic")
    if not uids:
        return
    for uid in uids:
        await check_up_video(uid)


def run_scheduler():
    logger.info("执行定时任务")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(dy_sched())
    loop.run_until_complete(video_sched())
    loop.close()
    logger.info("执行定时任务完毕")


scheduler.add_job(run_scheduler, "interval", minutes=0, seconds=5)
asyncio.run(init_browser())
run_scheduler()
