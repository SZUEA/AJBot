import os

from botoy import Botoy, jconfig, GroupMsg, Action
from botoy.schedule import scheduler

qq = jconfig.qq
os.environ["BOTQQ"] = str(qq)
bot = Botoy(qq=qq, use_plugins=True)


@bot.group_context_use
def group_mid(ctx):
    ctx.master = jconfig.master
    return ctx


action = Action(qq, host=jconfig.host, port=jconfig.port)


def zhibo():
    action.sendGroupText(
        903278109,
        content="@all\n好哥哥们，看直播啦啦啦，如果没直播的话当我没说。"
    )


def jinyan(switch):
    action.shutAllUp(
        903278109,
        switch=switch
    )
    if switch == 1:
        action.sendGroupText(
            903278109,
            content="半夜一点啦，早睡早起哦。"
        )
    else:
        action.sendGroupText(
            903278109,
            content="起床了，记得干事情哦。"
        )


scheduler.add_job(zhibo, "cron", hour=19, minute=55)
scheduler.add_job(jinyan, "cron", hour=0, minute=59, args=(1,))
scheduler.add_job(jinyan, "cron", hour=6, minute=30, args=(0,))

if __name__ == "__main__":
    bot.run()
