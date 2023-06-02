"""链接OPENAI_API使用GPT
"""

import os,openai
from EAbotoy import Action, logger, Text
from EAbotoy.contrib import get_cache_dir, plugin_receiver
# from EAbotoy.decorators import from_these_groups
from EAbotoy.model import WeChatMsg
from EAbotoy.schedule import scheduler
from plugins.bot_dev.bot_api import is_api_master

def get_message_from_openai(message):
    os.environ["http_proxy"] = "http://localhost:7890"
    os.environ["https_proxy"] = "http://localhost:7890"
    openai.api_key = ""
    openai.api_base = "https://api.openai.com/v1/chat"
    prompt = "我希望你充当 IT 专家。我会向您提供有关我的技术问题所需的所有信息，而您的职责是解决我的问题。你应该使用你的计算机科学、网络基础设施和 IT 安全知识来解决我的问题。在您的回答中使用适合所有级别的人的智能、简单和易于理解的语言将很有帮助。用要点逐步解释您的解决方案很有帮助。尽量避免过多的技术细节，但在必要时使用它们。我希望您回复解决方案，而不是写任何解释。我的第一个问题如下，"
    completion = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt + message}],
    )
    response = completion.choices[0].message.content
    return response
@plugin_receiver.wx
def receive_wx_msg(ctx: WeChatMsg):
    isAdmin = is_api_master(ctx.CurrentWxid, ctx.ActionUserName) or ctx.ActionUserName == ctx.master
    if not isAdmin:
        return
    if ctx.Content.startswith("GPT "):
        args = ctx.Content[4:]
        message = get_message_from_openai(args)
        Text(message)
