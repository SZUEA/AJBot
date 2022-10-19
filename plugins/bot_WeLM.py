import os
import json
import requests
from queue import deque  # type:ignore

from EAbotoy import Action, MsgTypes
from EAbotoy import decorators as deco

# 自动消息加一功能, 支持文字消息和图片消息
from EAbotoy.decorators import these_msgtypes, startswith, on_command
from EAbotoy.model import WeChatMsg

action = Action(os.environ["wxid"], is_use_queue=True)


def get_answer(input):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer cchi48mv9mc753cgthvg',
    }

    json_data = {
        'prompt': input + '\n回答：',
        'model': 'xl',
        'max_tokens': 64,
        'temperature': 0.8,
        'top_p': 0.95,
        'top_k': 50,
        'n': 1,
        'echo': False,
        'stop': '。.'
    }

    response = requests.post('https://welm.weixin.qq.com/v1/completions', headers=headers, json=json_data)
    answer = '接口超限，请明天再试'
    if response.content:
        text = json.loads(response.content)["choices"][0]['text']
        if not text:
            answer = 'EAbot遗憾地告诉你：生成错误！！以下为可能的错误原因：\n1、输入的文字过长\n2、输入或者输出违反相关法律法规不予显示\n3、奇奇怪怪的bug'
        else:
            answer = text.replace('\n', '')\
                .replace('@', '').replace('\r', '').replace('>', '').replace('匿名用户','').replace('[图片]', '')
    return answer


@on_command([".cc", '。cc'])
def receive_wx_msg(ctx: WeChatMsg, arg, command):  # 函数名字只能是这个才能触发
    answer = get_answer(arg)
    action.sendWxText(toUserName=ctx.FromUserName,
                      content=answer, )
