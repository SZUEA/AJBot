import sqlite3
from typing import List

from EAbotoy import jconfig, MsgTypes, WeChatMsg, decorators, sugar
from EAbotoy.contrib import get_cache_dir, plugin_receiver

DB_PATH = get_cache_dir("api") / "myDB.sqlite3"


class DB:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.cursor = self.db.cursor()
        self.create()

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.cursor.row_factory = dict_factory

    def create(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `bot_config` (
              `current_wxid` varchar(40) NOT NULL,
              `master_wxid` varchar(40) NOT NULL
            );
            """
        )
        self.db.commit()
    def insert(self, tb, dt):
        ls = [(k, dt[k]) for k in dt if dt[k] is not None]
        sql = 'insert into %s (' % tb + ','.join(i[0] for i in ls) + \
              ') values (' + ','.join('%r' % i[1] for i in ls) + ');'
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(sql)
            print(e)
        res = self.cursor.lastrowid
        self.db.commit()
        return res

    def commit(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as error:
            print('\033[031m', error, '\033[0m', sep='')
    def query(self, sql):
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res
    def add_bot_apiadmin(self, admin_wxid, bot_wxid):
        self.insert('bot_config', dict(
            current_wxid=bot_wxid,
            master_wxid=admin_wxid,
        ))
    def find_qq_bot_master(self, current_wxid, master_wxid):
        return self.query(f'''SELECT COUNT(1) FROM bot_config WHERE 
        current_wxid="{current_wxid}" AND master_wxid="{master_wxid}"''')

def is_api_master(bot_wxid, user):
    db = DB()
    try:
        r = db.find_qq_bot_master(bot_wxid, user)
        if r[0]['COUNT(1)'] == 0:
            return False
        else:
            return True
    except Exception as e:
        print('is_bot_apimaster')
        print(e)
        return False

@plugin_receiver.wx
@decorators.these_msgtypes(MsgTypes.TextMsg)
def admin_manage(ctx: WeChatMsg):
    if ctx.ActionUserName != jconfig.master:
        return
    if 'add apiadmin' in ctx.Content and ctx.isAtMsg:
        res = '上面用户成功添加为api_admin'
        user_ls = ctx.atUserIds
        if user_ls is None or len(user_ls) == 0:
            return
        for _qq in user_ls:
            if is_api_master(ctx.CurrentWxid, _qq):
                continue
            sql = DB()
            sql.add_bot_apiadmin(_qq, ctx.CurrentWxid)
        sugar.Text(res)


