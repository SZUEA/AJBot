""" B站视频或番剧订阅

视频订阅+{UID:123}
视频订阅+{UP名字}
视频退订+{UID}
视频列表

番剧订阅+{番剧名}
番剧退订+{番剧id}
番剧列表
"""
import base64
# pylint: disable=R0915
import re
from io import BytesIO

import requests

from EAbotoy import Action, jconfig, Text, Picture
from EAbotoy.model import WeChatMsg
from EAbotoy.schedule import scheduler
from EAbotoy.session import Prompt, SessionHandler, ctx, session
from EAbotoy.decorators import from_these_groups

from .api import API
from .db import DB
from .utils import clean_html

# 订阅逻辑
bilibili_handler = SessionHandler()

white_groups = ['18728854191@chatroom', '18803656716@chatroom']


@bilibili_handler.handle
def _():
    if not ctx.IsGroup:
        bilibili_handler.finish()
    from_group = ctx.FromUserName
    if from_group not in white_groups:
        bilibili_handler.finish()

    if ctx.Content.startswith("视频订阅"):
        # 确定订阅UP的mid, 如果无法确定则随时退出
        # 通过格式1 -> UID:数字
        try:
            mid = re.findall(r"UID:(\d+)", ctx.Content)[0]
        except Exception:
            mid = None

        # 格式1不行，通过格式2，关键词搜索
        if mid is None:
            keyword = ctx.Content[4:]
            ups = API.search_up_by_keyword(keyword)
            if not ups:
                bilibili_handler.finish("未找到相关UP，请重试或修改指令内容")
            if len(ups) == 1:
                mid = ups[0].mid
            else:
                choose_msgs = []
                for idx, up in enumerate(ups[:10]):
                    choose_msgs.append(f"{idx} 【{up.name}】")
                choose = session.want(
                    "choose", "发送对应序号选择UP主:\n" + "\n".join(choose_msgs), timeout=60
                )
                if isinstance(choose, str) and choose.isdigit():
                    try:
                        mid = ups[int(choose)].mid
                    except IndexError:
                        bilibili_handler.finish("序号错误，已退出当前会话!")
                else:
                    bilibili_handler.finish("序号错误，已退出当前会话!")

        db = DB()

        if db.subscribe_up(ctx.GroupId, mid):
            upinfo = API.get_up_info_by_mid(mid)
            if upinfo is None:
                bilibili_handler.finish(f"成功订阅UP主：{mid}")
            else:
                send_img(ctx.GroupId, upinfo.face)
                bilibili_handler.finish(f"成功订阅UP主：{upinfo.name}")
        else:
            bilibili_handler.finish("本群已订阅该UP主")

    elif ctx.Content.startswith("番剧订阅"):
        keyword = ctx.Content[4:]
        bangumis = API.search_bangumi_by_keyword(keyword)
        if not bangumis:
            bilibili_handler.finish("未找到相关番剧，请重试或修改指令内容")
        if len(bangumis) == 1:
            choose_bangumi = bangumis[0]
        else:
            choose_msgs = []
            for idx, bangumi in enumerate(bangumis[:10]):
                choose_msgs.append(
                    f"{idx} 【{clean_html(bangumi.title)}】\n{bangumi.styles}\n{bangumi.desc}"
                )
            choose = session.want(
                "choose", "发送对应序号选择番剧:\n" + "\n".join(choose_msgs), timeout=60
            )
            if isinstance(choose, str) and choose.isdigit():
                try:
                    choose_bangumi = bangumis[int(choose)]
                except IndexError:
                    bilibili_handler.finish("序号错误，已退出当前会话!")
            else:
                bilibili_handler.finish("序号错误，已退出当前会话!")

        db = DB()

        if db.subscribe_bangumi(ctx.GroupId, choose_bangumi.media_id):
            send_img(ctx.GroupId, choose_bangumi.cover)
            bilibili_handler.finish(f"成功订阅番剧: {clean_html(choose_bangumi.title)}")
        else:
            bilibili_handler.finish("本群已订阅过该番剧")

    # -----------------------
    bilibili_handler.finish()


def send_img(group, imageUrl):
    res = requests.get(imageUrl)
    base = str(base64.b64encode(BytesIO(res.content).read()), encoding="utf-8")
    action.sendImg(group, imageBase64=base)


# ==============
# 用于定时任务
action: Action = None


# ==============

# 订阅使用session， 其他操作使用普通指令
@from_these_groups(*white_groups)
def receive_wx_msg(ctx: WeChatMsg):
    global action  # pylint: disable=W0603
    if action is None:
        # pylint: disable=W0212
        action = Action(ctx.CurrentWxid, host=ctx._host, port=ctx._port)

    if ctx.ActionUserName == ctx.CurrentWxid or ctx.ActionUserName != jconfig.master:
        return

    # 退订UP
    if ctx.Content.startswith("视频退订"):
        try:
            mid = re.findall(r"(\d+)", ctx.Content)[0]
        except Exception:
            msg = "UID应为数字"
        else:
            db = DB()
            if db.unsubscribe_up(ctx.GroupId, mid):
                upinfo = API.get_up_info_by_mid(mid)
                if upinfo is not None:
                    msg = "成功退订UP主：{}".format(upinfo.name)
                else:
                    msg = "成功退订UP主：{}".format(mid)
            else:
                msg = "本群未订阅该UP主"
        action.sendWxText(ctx.GroupId, msg)
    # 查看订阅UP列表
    elif ctx.Content == "视频列表":
        db = DB()
        mids = db.get_ups_by_gid(ctx.GroupId)
        if mids:
            ups = []
            for mid in mids:
                upinfo = API.get_up_info_by_mid(mid)
                if upinfo is not None:
                    ups.append("{}({})".format(upinfo.mid, upinfo.name))
                else:
                    ups.append(str(mid))
            msg = "本群已订阅UP主：\n" + "\n".join(ups)
        else:
            msg = "本群还没有订阅过一个UP主"
        action.sendWxText(ctx.GroupId, msg)

    # 退订番剧
    elif ctx.Content.startswith("番剧退订"):
        try:
            mid = re.findall(r"(\d+)", ctx.Content)[0]
        except Exception:
            msg = "番剧ID应为数字"
        else:
            db = DB()
            if db.unsubscribe_bangumi(ctx.GroupId, mid):
                # 通过最新集数中的api获取番剧基本信息勉勉强强满足需求
                bangumi = API.get_latest_ep_by_media_id(mid)
                if bangumi is not None:
                    msg = "成功退订番剧：{}".format(bangumi.long_title)
                else:
                    msg = "成功退订番剧：{}".format(mid)
            else:
                msg = "本群未订阅该UP主"
        action.sendWxText(ctx.GroupId, msg)
    # 查看订阅番剧列表
    elif ctx.Content == "番剧列表":
        db = DB()
        mids = db.get_bangumi_by_gid(ctx.GroupId)
        if mids:
            msgs = []
            for mid in mids:
                bangumi = API.get_latest_ep_by_media_id(mid)
                if bangumi is not None:
                    msgs.append("{}({})".format(mid, bangumi.long_title))
                else:
                    msgs.append(str(mid))
            msg = "本群已订阅番剧：\n" + "\n".join(msgs)
        else:
            msg = "本群还没有订阅过一部番剧"
        action.sendWxText(ctx.GroupId, msg)

    # 其他操作逻辑转到session操作
    else:
        bilibili_handler.message_receiver(ctx)


# schedule task


def check_up_video():
    db = DB()
    for mid in db.get_subscribed_ups():
        video = API.get_latest_video_by_mid(mid)
        if video is not None:
            if db.judge_up_updated(mid, video.created):
                info = "UP主<{}>发布了新视频!\n{}\n{}\n{}".format(
                    video.author,
                    video.title,
                    video.description,
                    video.bvid,
                )
                if action is not None:
                    for group in db.get_gids_by_up_mid(mid):
                        send_img(
                            group,
                            imageUrl=video.pic,
                        )
                        Text(info, ctx=ctx)


def check_bangumi():
    db = DB()
    for mid in db.get_subscribed_bangumis():
        ep = API.get_latest_ep_by_media_id(mid)
        if ep is not None:
            if db.judge_bangumi_updated(mid, ep.id):
                info = "番剧《{}》更新了！\n{}".format(
                    ep.long_title,
                    ep.url,
                )
                if action is not None:
                    for group in db.get_gids_by_bangumi_mid(mid):
                        send_img(
                            group,
                            imageUrl=ep.cover,
                        )
                        Text(info, ctx=ctx)


scheduler.add_job(check_up_video, "interval", minutes=5)
scheduler.add_job(check_bangumi, "interval", minutes=10)
