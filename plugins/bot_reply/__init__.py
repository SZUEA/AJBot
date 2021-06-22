import re
import time
from random import randrange

from botoy import Action, GroupMsg, sugar
from botoy.refine import refine_pic_group_msg

from botoy.decorators import ignore_botself
from .db import DB, is_bot_master


# 下面三个函数名不能改，否则不会调用
# 但是都是可选项，建议把不需要用到的函数删除，节约资源


class Reply(object):
    def __init__(self, _id, rule_list, reply_list, match_group, response_type='text', pic_url=''):
        self.id: int = _id
        self.rule_list: [str] = rule_list
        self.reply_list: [str] = reply_list
        self.response_type = response_type
        self.pic_url = pic_url
        self.match_group = match_group

    def match(self, message, FromGroupId):
        for rule in self.rule_list:
            if str(FromGroupId) == str(self.match_group) and self.check(rule, message):
                return True
        return False

    def check(self, rule: str, message: str):
        raise NotImplementedError

    def reply(self, ctx: GroupMsg):
        if self.response_type == 'text':
            Action(ctx.CurrentQQ).sendGroupText(ctx.FromGroupId,
                                                content=self.reply_list[randrange(0, len(self.reply_list))])
        else:
            Action(ctx.CurrentQQ).sendGroupPic(ctx.FromGroupId, picUrl=self.pic_url,
                                               content=self.reply_list[randrange(0, len(self.reply_list))])

    def remove(self):
        op = DB()
        op.delete_reply_message(self.id)


class RegReply(Reply):
    """
    正则回复
    """

    def check(self, rule: str, message: str):
        try:
            return re.search(rule, message) is not None
        except Exception as e:
            return False


class PreReply(Reply):
    """
    前缀回复
    """

    def check(self, rule: str, message: str):
        return message.startswith(rule)


class ContainReply(Reply):
    """
    包含回复
    """

    def check(self, rule: str, message: str):
        return rule in message


class EqualReply(Reply):
    """
    全等回复
    """

    def check(self, rule: str, message: str):
        return rule == message


response_list: [Reply] = []
mapping_dict = {
    'PreReply': PreReply,
    'RegReply': RegReply,
    'ContainReply': ContainReply,
    'EqualReply': EqualReply
}


def init_response():
    start_time = time.perf_counter()
    op = DB()
    res = op.get_qq_bot_reply()
    for reply in res:
        add_response(reply['id'], reply['rules'],
                     reply['response'], reply['rule_type'], reply['from_group'],
                     reply['response_type'], reply['pic_url'])
    end_time = time.perf_counter()
    return end_time - start_time


def add_response(_id, rules, response, rule_type, FromGroupId, response_type, pic_url=''):
    response_list.append(mapping_dict[rule_type](_id, rules.split('|'),
                                                 response.split('|'), FromGroupId,
                                                 response_type, pic_url))


init_response()


@ignore_botself
def receive_group_msg(ctx: GroupMsg):
    pic_ctx = refine_pic_group_msg(ctx)
    if pic_ctx is not None:
        content = "" if pic_ctx.Content is None else pic_ctx.Content.replace('\r', '')
    else:
        content = ctx.Content
    if content == "" or content is None:
        return

    if content.startswith('.') or content.startswith('。'):
        if not is_bot_master(ctx.CurrentQQ, ctx.FromUserId):
            return
        content = content[1:]
        if content == 'reload':
            cost = init_response()
            sugar.Text(f"关键词回复重载完毕，用时{str(cost)[:5]} s")
            return
        elif content.startswith('pre') or content.startswith('前缀'):
            message_type = 'PreReply'
        elif content.startswith('re') or content.startswith('正则'):
            message_type = 'RegReply'
        elif content.startswith('con') or content.startswith('包含'):
            message_type = 'ContainReply'
        elif content.startswith('eq') or content.startswith('全等') or content.startswith('等于') \
                or content.startswith('reply'):
            message_type = 'EqualReply'
        elif content.startswith('dele') or content.startswith('删除'):
            args = content.split(' ')
            if len(args) < 2:
                return
            for reply in response_list:
                if reply.match(args[1], ctx.FromGroupId):
                    reply.remove()
                    response_list.remove(reply)
            sugar.Text(f"对关键词{args[1]}的回复已删除")
            return
        else:
            return
        args = content.split(' ')
        if len(args) < 2:
            sugar.Text("参数不足")
            return
        op = DB()
        if pic_ctx is None:
            if len(args) < 3:
                sugar.Text("参数不足")
                return
            response = ' '.join(args[2:])
            _id = op.insert_reply_message(args[1], response, message_type,
                                          'text', ctx.FromGroupId)
            add_response(_id, args[1], response, message_type, ctx.FromGroupId, 'text')
        else:
            response = ' '.join(args[2:]) if len(args) >= 3 else ''
            _id = op.insert_reply_message(args[1], response, message_type,
                                          'pic', ctx.FromGroupId, pic_ctx.GroupPic[0].Url)
            add_response(_id, args[1], response, message_type, ctx.FromGroupId, 'pic', pic_ctx.GroupPic[0].Url)
        sugar.Text(f"""对关键词"{args[1]}"的回复添加成功""")
        return

    if ctx.MsgType != 'TextMsg':
        return
    for reply in response_list:
        if reply.match(content, ctx.FromGroupId):
            reply.reply(ctx)
            return
