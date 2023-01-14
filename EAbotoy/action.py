# pylint: disable=R0904
import functools
import mimetypes
import queue
import random
import threading
import time
import traceback
import uuid
from io import BytesIO
from typing import List, Optional, Union, Callable

import httpx
import requests
from PIL import Image

from EAbotoy import macro
from EAbotoy.config import jconfig
from EAbotoy.log import logger
from EAbotoy.model import EventMsg, WeChatMsg

from . import utils
from .contrib import get_cache_dir


class _Task:
    def __init__(self, target: Callable, args: tuple = None, callback: Callable = None):
        args = args or tuple()
        self.target = functools.partial(target, *args)
        functools.update_wrapper(self.target, target)
        self.callback = callback


class _SendThread(threading.Thread):
    def __init__(self, delay=1.1):
        super().__init__()
        self.tasks = queue.Queue(maxsize=-1)
        self.running = False
        self.delay = delay
        self.last_send_time = time.time()

    def run(self):
        self.running = True
        while True:
            try:
                # 因为重载(importlib.relaod)之后，线程仍会在后台运行
                # 暂时使用超时跳出线程
                # 线程停了之后，被重载后，是不是会被gc??? 0.o
                task: _Task = self.tasks.get(timeout=30 * 60)  # 30min
            except queue.Empty:
                self.running = False
                break
            else:
                should_wait = (self.delay + self.delay * random.random() * 0.2) - (time.time() - self.last_send_time)
                if should_wait > 0:
                    time.sleep(should_wait)
                try:
                    ret = task.target()
                    if task.callback is not None:
                        task.callback(ret)
                except Exception:
                    logger.exception('Action发送线程出错')
                finally:
                    self.last_send_time = time.time()

    def start(self):
        # 强改内部方法以允许重复执行start方法, 暂时不知道这样做有什么后果
        if not self.running:
            self._started.is_set = lambda: False
        else:
            self._started.is_set = lambda: True
        super().start()

    def put_task(self, task: _Task):
        assert isinstance(task, _Task)
        self.tasks.put(task)
        if not self.running:
            self.start()


queue_delay = 1.1
_send_thread = _SendThread(queue_delay)
_send_thread.setDaemon(True)


class Action:
    def __init__(
            self,
            wxid: Optional[str] = None,
            port: Optional[int] = None,
            host: Optional[str] = None,
            timeout: int = 20,
            is_use_queue: bool = True,

    ):
        self.host = utils.check_schema(host or jconfig.host)
        self.port = port or jconfig.port
        self.address = utils.to_address(self.host, self.port)

        self._wxid = wxid or jconfig.wxid or ""

        self.c = httpx.Client(
            headers={"Content-Type": "application/json"},
            timeout=timeout + 5,
            base_url=self.address,
            params={"timeout": timeout},
        )
        self.lock = threading.Lock()

        self._use_queue = is_use_queue
        # self._send_thread = _SendThread(queue_delay)
        # self._send_thread.setDaemon(True)

    @property
    def wxid(self) -> str:
        return self._wxid

    @classmethod
    def from_ctx(
            cls, ctx: Union[EventMsg, WeChatMsg], timeout: int = 20
    ) -> "Action":
        return cls(
            ctx.CurrentWxid,
            host=getattr(ctx, "_host", None),
            port=getattr(ctx, "_port", None),
            timeout=timeout,
        )

    # 改造完成
    # ###########发送相关############
    def sendWxText(
            self, toUserName: str, content: str, atUser: Union[str, List[str]] = "", atAll: bool = False
    ) -> dict:
        """发送群组文本消息"""
        if atAll:
            content = "@所有人 " + content
            atUser = "notify@all"

        arg = {
            "ToUserName": toUserName,
            "MsgType": 1,
            "Content": content,
            "AtUsers": atUser if isinstance(atUser, str) else ','.join(atUser)
        }

        if atUser != "" and len(atUser) != 0:
            arg['AtUsers'] = atUser if isinstance(atUser, str) else ','.join(atUser)
            content = arg['Content']
            atUserCount = 1 if isinstance(atUser, str) else len(atUser)
            if '@' not in content:
                content += "\n" + ("@" * (atUserCount - content.count('@')))
            arg['Content'] = content

        return self._post(
            "SendMsg",
            arg,
        )

    # 发送图片
    def sendImg(
            self,

            toUserName: str,
            imageUrl: str = "",
            imageBase64: str = "",
            imagePath: str = "",
            text: str = ""
    ):
        """发送图片消息"""
        assert any([imageUrl, imageBase64, imagePath]), "缺少参数"

        arg = {
            "ToUserName": toUserName,
        }
        if imagePath != "":
            arg['ImageUrl'] = imageUrl
        elif imageBase64 != "":
            arg['ImageBase64'] = imageBase64
        elif imagePath != "":
            arg['ImagePath'] = imagePath
        if text != '':
            return self._post(
                "SendImage",
                arg,
            )
        self._post(
            "SendImage",
            arg,
        )
        return self.sendWxText(toUserName, text)

    def sendCdnImg(
            self,

            toUserName: str,
            xml: str,
    ):
        """发送图片消息"""

        arg = {
            "ToUserName": toUserName,
            "XmlStr": xml,
        }

        return self._post(
            "SendCdnImage",
            arg,
        )

    def sendEmoji(
            self,

            toUserName: str,
            EmojiMd5: str,
            EmojiLen: int = 0,
    ):
        """发送好友图片消息"""

        arg = {
            "ToUserName": toUserName,
            "EmojiMd5": EmojiMd5,
            "EmojiLen": EmojiLen
        }

        return self._post(
            "SendEmoji",
            arg,
        )

    def sendApp(
            self,
            toUserName: str,
            content: str,
    ):
        """发送好友图片消息"""

        arg = {
            "ToUserName": toUserName,
            "Content": content,
            "MsgType": 49
        }

        return self._post(
            "SendAppMsg",
            arg,
        )

    def uploadIMGByCDN(
            self,

            toUserName: str,
            path: str = "",
            imageUrl: str = "",
            type: str = 'jpg'
    ):
        """发送图片消息"""
        assert any([imageUrl, path]), "缺少参数"
        arg = {
            "ToUserName": toUserName,
            "MediaType": "2"
        }

        if path != '':
            arg["FilePath"] = path
            return self._post(
                "UploadIMGByCDN",
                arg,
                use_queue=False
            )
        try:
            res = requests.get(imageUrl)
            image = Image.open(BytesIO(res.content))
            if image.mode == "P":
                image = image.convert('RGB')

            _path = get_cache_dir("cache_img") / f"{toUserName}-{random.randint(1, 10000)}.{type}"
            image.save(_path)
        except Exception as e:
            print(e)
            return None
        arg['FilePath'] = str(_path)
        return self._post(
            "UploadIMGByCDN",
            arg,
            use_queue=False
        )

    ############################################################################
    def revokeMsg(
            self,
            ctx: WeChatMsg
    ):
        """撤回"""

        arg = {
            "CgiCmd": 594,
            "CgiRequest": {
                "OpCode": 0,
                "MsgId": ctx.MsgId,
                "NewMsgId": ctx.NewMsgId,
                "ToUserName": ctx.FromUserName
            }
        }

        return self._post(
            "MagicCgi",
            arg,
        )

    ############################################################################
    def _baseRequest(
            self,
            method: str,
            funcname: str,
            path: str,
            payload: Optional[dict] = None,
            params: Optional[dict] = None,
    ) -> dict:
        """基础请求方法, 提供部分提示信息，出错返回空字典，其他返回服务端响应结果"""
        params = params or {}
        params["funcname"] = funcname
        if not params.get("wxid"):
            params["wxid"] = self.wxid

        # 发送请求
        try:
            self.lock.acquire()
            threading.Timer(5, self.release_lock).start()
            resp = self.c.request(
                method, httpx.URL(url=path, params=params), json=payload
            )
            resp.raise_for_status()
        except httpx.TimeoutException:
            logger.warning(f"响应超时，但不代表处理未成功, 结果未知!")
            return {}
        except httpx.HTTPStatusError:
            logger.error(
                f"响应码出错 => {resp.status_code}，大概率是因为账号已离线或者qq号错误",  # type:ignore
            )
            return {}
        except Exception:
            logger.error(f"请求出错: {traceback.format_exc()}")
            return {}
        finally:
            threading.Timer(1, self.release_lock).start()

        # 处理数据
        try:
            data = resp.json()
        except Exception:
            logger.error("API响应结果非json格式")
            return {}

        if data is None:
            logger.error("返回为null, 该类情况多数是因为响应超时或者该API不存在，或服务端操作超时(此时不代表未成功)")
            return {}

        # 返回码提示
        if "Ret" in data:
            ret = data.get("Ret")
            if ret == 0:
                pass
            elif ret == 34:
                logger.error(f"未知错误，跟消息长度似乎无关，可以尝试分段重新发送 => {data}")
            elif ret == 110:
                logger.error(f"发送失败，你已被移出该群，请重新加群 => {data}")
            elif ret == 120:
                logger.error(f"机器人被禁言 => {data}")
            elif ret == 241:
                logger.error(f"消息发送频率过高，对同一个群或好友，建议发消息的最小间隔控制在1100ms以上 => {data}")
            elif ret == 299:
                logger.error(f"超过群发言频率限制 => {data}")
            else:
                logger.error(f"请求发送成功, 但处理失败 => {data}")

        return data

    def _post(
            self,
            funcname: str,
            payload: dict,
            params: Optional[dict] = None,
            path: str = "/v1/LuaApiCaller",
            use_queue: bool = True,
    ) -> Union[dict, None]:
        """封装常用的post操作"""
        job = functools.partial(
            self._baseRequest,
            "POST", funcname=funcname, path=path, payload=payload, params=params
        )
        functools.update_wrapper(job, self._baseRequest)
        if self._use_queue and use_queue:
            _send_thread.put_task(
                _Task(target=job))
            return None
        return job()

    def _get(
            self,
            funcname: str,
            params: Optional[dict] = None,
            path: str = "/v1/LuaApiCaller",
    ) -> Union[dict, None]:
        """封装get操作"""

        job = functools.partial(
            self._baseRequest,
            "GET", funcname=funcname, path=path, params=params
        )
        functools.update_wrapper(job, self._baseRequest)
        if self._use_queue:
            _send_thread.put_task(
                _Task(target=job))
            return None
        return job()

    def release_lock(self):
        try:
            self.lock.release()
        except Exception:
            pass
