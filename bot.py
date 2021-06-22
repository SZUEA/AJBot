import os

from botoy import Botoy, jconfig, GroupMsg, Action, sugar
from botoy.schedule import scheduler

from plugins.bot_reply import is_bot_master

qq = jconfig.qq
os.environ["BOTQQ"] = str(qq)
bot = Botoy(qq=qq, use_plugins=True)


@bot.group_context_use
def group_mid(ctx):
    ctx.master = jconfig.master
    return ctx


@bot.on_group_msg
def on_group_msg(ctx: GroupMsg):
    if ctx.FromUserId != jconfig.master:
        return
    if ctx.Content == '刷新插件':
        bot.plugMgr.refresh_plugins()

        # 语法糖
        sugar.Text("~~所有插件刷新完毕")
    if 'add admin' in ctx.Content and ctx.MsgType == 'AtMsg':
        res = '下列用户添加为admin:\n'
        user_ls = set(eval(ctx.Content).get('UserID', None))
        if user_ls is None or len(user_ls) == 0:
            return
        for _qq in user_ls:
            res += f'[GETUSERNICK({_qq})] √\n'
            if is_bot_master(ctx.CurrentQQ, _qq):
                continue
            from plugins.bot_reply import DB
            sql = DB()
            sql.add_bot_admin(_qq, ctx.CurrentQQ)
        sugar.Text(res)


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
