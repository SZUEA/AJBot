import mimetypes
import time
import traceback
import uuid
from typing import List, Optional, Union

import httpx

from EAbotoy.parser import event as eventParser

from . import macro, utils
from .config import jconfig
from .log import logger
from .model import EventMsg, WeChatMsg


class AsyncAction:
    def __init__(
            self,
            wxid: Optional[str] = None,
            port: Optional[int] = None,
            host: Optional[str] = None,
            timeout: int = 20,
    ):
        self.host = utils.check_schema(host or jconfig.host)
        self.port = port or jconfig.port
        self.address = utils.to_address(self.host, self.port)

        self._wxid = wxid or jconfig.wxid or ""

        self.c = httpx.AsyncClient(
            headers={"Content-Type": "application/json"},
            timeout=timeout + 5,
            base_url=self.address,
            params={"timeout": timeout},
        )

    @property
    def wxid(self) -> int:
        if self._wxid == 0:
            self._wxid = self.getAllBots()[0]
        return self._wxid

    @classmethod
    def from_ctx(
            cls, ctx: Union[EventMsg, WeChatMsg], timeout: int = 20
    ) -> "AsyncAction":
        return cls(
            ctx.CurrentWxid,
            host=getattr(ctx, "_host", None),
            port=getattr(ctx, "_port", None),
            timeout=timeout,
        )

    async def close(self):
        return await self.c.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return await self.c.__aexit__(*args)

    ############发送相关############

    async def sendWxText(
            self, toUserName: str, content: str, atUser: Union[str, List[str]] = "", atAll: bool = False
    ) -> dict:
        """发送群组文本消息"""
        if atAll:
            content = "@所有人 " + content
            atUser = "notify@all"

        return await self.post(
            "SendMsg",
            {
                "ToUserName": toUserName,
                "MsgType": 1,
                "Content": content,
                "AtUsers": atUser
            },
        )

    # 发送图片
    async def sendImg(
            self,

            toUserName: str,
            imageUrl: str = "",
            imageBase64: str = "",
            imagePath: str = "",
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

        return await self.post(
            "SendImage",
            arg,
        )

    async def sendCdnImg(
            self,

            toUserName: str,
            xml: str,
    ):
        """发送图片消息"""

        arg = {
            "ToUserName": toUserName,
            "XmlStr": xml,
        }

        return await self.post(
            "SendCdnImage",
            arg,
        )

    async def sendEmoji(
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

        return await self.post(
            "SendEmoji",
            arg,
        )

    ############################################################################
    async def revokeMsg(
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

        return await self.post(
            "MagicCgi",
            arg,
        )

    ############################################################################
    async def baseRequest(
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
        if not params.get("qq"):
            params["qq"] = await self.qq

        # 发送请求
        try:
            resp = await self.c.request(
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

    async def post(
            self,
            funcname: str,
            payload: dict,
            params: Optional[dict] = None,
            path: str = "/v1/LuaApiCaller",
    ) -> dict:
        """封装常用的post操作"""
        return await self.baseRequest(
            "POST", funcname=funcname, path=path, payload=payload, params=params
        )

    async def get(
            self,
            funcname: str,
            params: Optional[dict] = None,
            path: str = "/v1/LuaApiCaller",
    ) -> dict:
        """封装get操作"""
        return await self.baseRequest(
            "GET", funcname=funcname, path=path, params=params
        )
