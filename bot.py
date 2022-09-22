import json
import os

from EAbotoy import Botoy, jconfig, Action, sugar, MsgTypes
from EAbotoy.model import WeChatMsg, EventMsg
from EAbotoy import decorators
from EAbotoy.schedule import scheduler
from plugins.bot_reply import is_bot_master

wxid = jconfig.wxid
os.environ["wxid"] = str(wxid)
bot = Botoy(wxid=wxid, use_plugins=True)

action = Action(wxid, host=jconfig.host, port=jconfig.port, is_use_queue=True)


@bot.wx_context_use
def wx_mid_add_master(ctx):
    ctx.master = jconfig.master
    return ctx


@bot.on_wx_msg
@decorators.these_msgtypes(MsgTypes.TextMsg)
def admin_manage(ctx: WeChatMsg):
    if ctx.ActionUserName != jconfig.master:
        return
    if 'add admin' in ctx.Content and ctx.isAtMsg:
        res = '上面用户成功添加为admin'
        user_ls = ctx.atUserIds
        if user_ls is None or len(user_ls) == 0:
            return
        for _qq in user_ls:
            if is_bot_master(ctx.CurrentWxid, _qq):
                continue
            from plugins.bot_reply import DB
            sql = DB()
            sql.add_bot_admin(_qq, ctx.CurrentWxid)
        sugar.Text(res)


@bot.on_wx_msg
@decorators.these_msgtypes(MsgTypes.TextMsg)
def plugin_manage(ctx: WeChatMsg):
    if ctx.ActionUserName != jconfig.master:
        return
    if ctx.Content == '刷新插件':
        bot.plugMgr.reload_plugins()

        sugar.Text("~~所有插件刷新完毕")



@bot.on_wx_msg
@decorators.these_msgtypes(MsgTypes.TextMsg)
@decorators.on_regexp(r'^[.。]')
def help(ctx: WeChatMsg):
    args = ctx.Content.split(" ")
    if args[0].lower() in ['.h', '.help', '。h', '。help']:
        plugins = bot.plugMgr.enabled_plugins
        end = '\n'
        if len(args) == 1:
            sugar.Text(f"输入.help 【插件名】 来查看具体插件说明\n"
                       f"~~~~~~~~~~~~~~\n"
                       f"{end.join([i[1] for i in plugins])}")
        else:
            for plugin in plugins:
                if args[1] == plugin[1]:
                    sugar.Text(f"{plugin[1]}的说明:\n"
                               f"~~~~~~~~~~~~~~\n"
                               f"{plugin[2]}")
                    return
            sugar.Text(f"没找到这种插件")


@bot.on_event
def event_log(ctx: EventMsg):
    pass


def notice(switch):
    if switch == 1:
        action.sendWxText(
            toUserName="25373433877@chatroom",
            content="半夜一点啦，早睡早起哦。"
        )
    else:
        action.sendWxText(
            toUserName="25373433877@chatroom",
            content="起床了，记得好好学习。"
        )


scheduler.add_job(notice, "cron", hour=0, minute=59, args=(1,))
scheduler.add_job(notice, "cron", hour=7, minute=20, args=(0,))

if __name__ == "__main__":
    bot.run()
