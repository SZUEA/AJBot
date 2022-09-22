import sqlite3
from typing import List

from EAbotoy.contrib import get_cache_dir

DB_PATH = get_cache_dir("reply") / "myDB.sqlite3"


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

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `reply_message` (
              `id` integer PRIMARY KEY autoincrement ,
              `rules` text,
              `response` text,
              `rule_type` varchar(40)  NOT NULL,
              `response_type` varchar(40)  NOT NULL,
              `pic_url` text,
              `from_wxid` varchar(40) NOT NULL,
              `owner` varchar(40) NOT NULL
            );
            """
        )

        self.db.commit()

    def commit(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as error:
            print('\033[031m', error, '\033[0m', sep='')

    def update(self, table, dt_update, dt_condition):
        sql = 'UPDATE %s SET ' % table + ','.join('%s=%r' % (k, dt_update[k]) for k in dt_update) \
              + ' WHERE ' + ' AND '.join('%s=%r' % (k, dt_condition[k]) for k in dt_condition) + ';'
        try:
            self.commit(sql)
        except Exception as e:
            print(sql)
            print(e)

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

    def query(self, sql):
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def delete_reply_message(self, message_id):
        self.commit(f'DELETE FROM reply_message WHERE id={message_id}')

    def insert_reply_message(self, rules, response, rule_type, response_type, from_wxid, owner, pic_url=''):
        return self.insert('reply_message', dict(
            rules=rules,
            response=response,
            rule_type=rule_type,
            response_type=response_type,
            pic_url=pic_url,
            from_wxid=from_wxid,
            owner=owner,
        ))

    def get_qq_bot_reply(self):
        return self.query('''SELECT * FROM reply_message WHERE 1=1''')

    def add_bot_admin(self, admin_wxid, bot_wxid):
        self.insert('bot_config', dict(
            current_wxid=bot_wxid,
            master_wxid=admin_wxid,
        ))

    def my_count_owner_reply(self, owner, from_wxid):
        return self.query(f'''SELECT COUNT(1) FROM reply_message
        WHERE owner = '{owner}' and from_wxid='{from_wxid}'
        ''')

    def get_my_keywords(self, owner, from_wxid):
        return self.query(f'''SELECT rules, owner, from_wxid FROM reply_message
        WHERE owner = '{owner}' and from_wxid='{from_wxid}'
        ''')

    def find_qq_bot_master(self, current_wxid, master_wxid):
        return self.query(f'''SELECT COUNT(1) FROM bot_config WHERE 
        current_wxid="{current_wxid}" AND master_wxid="{master_wxid}"''')


def is_bot_master(bot_wxid, user):
    db = DB()
    try:
        r = db.find_qq_bot_master(bot_wxid, user)
        if r[0]['COUNT(1)'] == 0:
            return False
        else:
            return True
    except Exception as e:
        print('is_bot_master')
        print(e)
        return False


def count_owner_reply(owner, from_wxid):
    db = DB()
    try:
        return db.my_count_owner_reply(owner, from_wxid)[0]['COUNT(1)']
    except Exception as e:
        print('count_owner_reply')
        print(e)
        return False
