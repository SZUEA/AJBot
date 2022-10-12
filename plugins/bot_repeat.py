"""自动+1 插件
连续重复3句话会自动复读
"""
from collections import defaultdict
from queue import deque  # type:ignore
from threading import Lock

from EAbotoy import decorators as deco
from EAbotoy.collection import MsgTypes
from EAbotoy.model import WeChatMsg
from EAbotoy.sugar import Picture, Text, Emoji


# 自动消息加一功能, 支持文字消息和图片消息

# 文本消息存文本，图片消息存MD5
class RepeatDeque(deque):
    def __init__(self, *args, **kwargs):
        super().__init__(maxlen=3, *args, **kwargs)
        self.lock = Lock()
        with self.lock:
            self.refresh()

    def refresh(self):
        for i in range(self.maxlen):
            self.append(i)

    def should_repeat(self, item):
        with self.lock:
            self.append(item)
            if len(set(self)) == 1:
                self.refresh()
                return True
        return False


text_deque_dict = defaultdict(RepeatDeque)
pic_deque_dict = defaultdict(RepeatDeque)


@deco.ignore_botself
def receive_wx_msg(ctx: WeChatMsg):
    if ctx.MsgType == MsgTypes.TextMsg:
        text = ctx.Content
        if text_deque_dict[ctx.FromUserName].should_repeat(text):
            Text(text)
    elif ctx.MsgType == MsgTypes.EmojiMsg:
        emojiMd5 = ctx.emojiMd5
        if pic_deque_dict[ctx.GroupId].should_repeat(emojiMd5):
            Emoji(emojiMd5)

