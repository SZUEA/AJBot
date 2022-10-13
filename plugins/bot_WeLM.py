import os
import json
import requests
from queue import deque  # type:ignore

from EAbotoy import Action, MsgTypes
from EAbotoy import decorators as deco

# 自动消息加一功能, 支持文字消息和图片消息
from EAbotoy.decorators import these_msgtypes, startwith
from EAbotoy.model import WeChatMsg

action = Action(os.environ["wxid"], is_use_queue=True)

def get_answer(input):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer cchi48mv9mc753cgthvg',
    }

    json_data = {
        'prompt': input,
        'model': 'xl',
        'max_tokens': 128,
        'temperature': 0.95,
        'top_p': 0.95,
        'top_k': 50,
        'n': 1,
        'echo': False
    }

    response = requests.post('https://welm.weixin.qq.com/v1/completions', headers=headers, json=json_data)
    text = json.loads(response.content)["choices"][0]['text']
    answer = 'EAbot遗憾地告诉你：生成错误！！以下为可能的错误原因：\n1、输入的文字过长\n2、输入或者输出违反相关法律法规不予显示\n3、奇奇怪怪的bug'
    if text:
        answer = text.replace('\n', '').replace('@', '').replace('\r', '').replace('>', '').replace('匿名用户', '').replace('[图片]', '')
    return answer

@these_msgtypes(MsgTypes.TextMsg)  # 指定消息类型
@startswith(".convo")
def receive_wx_msg(ctx: WeChatMsg):  # 函数名字只能是这个才能触发
    text = ctx.Content.split(' ')[-1].lower()
    answer = get_answer(text)
    action.sendWxText(toUserName=ctx.FromUserName,
                      content=answer,
                      atUser=ctx.atUserIds[0])




