# pylint: disable=too-many-instance-attributes
import warnings
from re import Match, findall
from typing import Optional, List
from xml.dom.minidom import Element, parseString

from EAbotoy import collection
from EAbotoy.collection import MsgTypes


class WeChatMsg:
    MsgId: int
    FromUserName: str
    ToUserName: str
    MsgType: int

    Content: str

    Status: int

    ImgStatus: int
    ImgBuf: str  # 图片小图 模糊图片 base64
    imgCDNContent: str

    emojiMd5: str

    CreateTime: int
    MsgSource: str

    PushContent: str
    NewMsgId: int
    ActionUserName: str
    ActionNickName: str

    IsGroup: bool = False
    GroupId: str = ""
    MessageSenderId: str
    master: str

    isAtMsg: bool = False
    atUserIds: List[str] = None
    atUserNames: List[str] = None

    message: dict  # raw message
    CurrentWxid: str
    data: dict

    # 动态添加
    _host: str
    _port: int
    _match: Match
    _findall: list

    def __init__(self, message: dict):
        data = message["CurrentPacket"]["Data"]

        # basic
        for name, value in dict(
                message=message,
                CurrentWxid=message["CurrentWxid"],
                data=data,
        ).items():
            self.__dict__[name] = value

        # set Data items
        for name in [
            "MsgId",
            "FromUserName",
            "ToUserName",
            "MsgType",
            "Content",
            "Status",
            "ImgStatus",
            "ImgBuf",
            "CreateTime",
            "MsgSource",
            "PushContent",
            "NewMsgId",
            "ActionUserName",
            "ActionNickName",
        ]:
            self.__dict__[name] = data.get(name)

        if "@chatroom" in self.FromUserName:
            self.IsGroup = True
            self.GroupId = self.FromUserName
        else:
            self.__dict__['ActionUserName'] = self.FromUserName

        if self.MsgType == MsgTypes.ImgMsg:
            self.imgCDNContent = self.Content

        if self.MsgType == MsgTypes.EmojiMsg:
            self.emojiMd5 = parseString(self.Content).getElementsByTagName('emoji')[0].getAttribute("md5")

        if self.MsgType == MsgTypes.TextMsg and "<atuserlist>" in self.MsgSource:
            self.isAtMsg = True
            self.atUserIds = parseString(self.MsgSource).getElementsByTagName("atuserlist")[0].childNodes[0].data.split(
                ",")
            self.atUserIds = [user for user in self.atUserIds if user != ""]
            self.atUserNames = [i + ' ' for i in findall(r"(@.*?)\u2005", self.Content)]

        self.MessageSenderId = self.ActionUserName

    def __setattr__(self, name, value):
        if name in (
                "MsgId",
                "FromUserName",
                "ToUserName",
                "MsgType",
                "Content",
                "Status",
                "ImgStatus",
                "ImgBuf",
                "CreateTime",
                "MsgSource",
                "PushContent",
                "NewMsgId",
                "ActionUserName",
                "ActionNickName",
        ):
            warnings.warn(f"{name} 为保留属性，不建议修改", SyntaxWarning, 2)

        self.__dict__[name] = value

    def __getattr__(self, name):
        return super().__getattribute__(name)

    def __repr__(self):
        return f"WeChatMsg => {self.data}"


class EventMsg:
    message: dict  # raw message
    CurrentWxid: int  # bot qq
    data: dict  # Data
    # EventMsg items
    EventName: str

    # DATA items
    ChatUserName: str
    FromUserName: str
    PattedUserName: str

    # 拍一拍
    Template: dict

    # 邀请进群
    InviteNickName: str
    InviteUserName: str
    InvitedNickName: str
    InvitedUserName: str

    _host: str
    _port: int

    def __init__(self, message: dict):
        data = message["CurrentPacket"]["Data"]

        # basic
        for name, value in dict(
                message=message,
                CurrentWxid=message["CurrentWxid"],
                data=data,
        ).items():
            self.__dict__[name] = value

        # set Data items
        for name in ["EventName", "Template", "ChatUserName", "FromUserName", "PattedUserName"]:
            self.__dict__[name] = data.get(name)

    def __setattr__(self, name, value):
        if name in (
                "EventName", "Template", "ChatUserName", "FromUserName", "PattedUserName"
        ):
            warnings.warn(f"{name} 为保留属性，不建议修改", SyntaxWarning, 2)
        self.__dict__[name] = value

    def __getattr__(self, name):
        return super().__getattribute__(name)

    def __repr__(self):
        return f"EventMsg => {self.data}"
