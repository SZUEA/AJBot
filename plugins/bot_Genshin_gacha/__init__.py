from EAbotoy import decorators as deco, WeChatMsg
from EAbotoy.sugar import Text

from .genshin import GenshenGacha

__doc__ = """原神抽卡"""
digitalConversionDict = {
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}

poolConversion = {
    '常驻': 'ordinary',
    '普通': 'ordinary',
    '普': 'ordinary',
    '角色': 'roleUp',
    '人物': 'roleUp',
    '武器': 'armUp',
}


@deco.on_regexp(r"原神(.*?)池(.*)连")
def main(ctx:WeChatMsg):
    if ctx.FromUserName == '24773935278@chatroom':
        return
    info = getattr(ctx, "_match")
    if cardPool := poolConversion.get(info[1]):
        if info[2] in digitalConversionDict.keys():
            cardCount = int(digitalConversionDict[info[2]])
        else:
            if info[2].isdigit():
                cardCount = int(info[2])
            else:
                Text('能不能用阿拉伯数字?')
                return None
        if cardCount > 10:
            Text('不能大于10哦')
            return
        elif cardCount <= 0:
            Text('?')
            return
        GenshenGacha(ctx, cardPool, cardCount).main()


def receive_wx_msg(ctx):
    main(ctx)
