import os

from botoy import Botoy, jconfig, GroupMsg
from botoy.decorators import equal_content, ignore_botself
from botoy.sugar import Text

qq = jconfig.qq
os.environ["BOTQQ"] = str(qq)
bot = Botoy(qq=qq, use_plugins=True)


@bot.group_context_use
def group_mid(ctx):
    ctx.master = jconfig.master
    return ctx


# @bot.on_group_msg
# @ignore_botself
# @equal_content("帮助")
# def bot_help(_):
#     Text("123123")


if __name__ == "__main__":
    bot.run()
