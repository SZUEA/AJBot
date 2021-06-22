import sqlite3
from typing import List

from botoy.contrib import get_cache_dir

DB_PATH = get_cache_dir("reply") / "myDB.sqlite3"


class DB:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.cursor = self.db.cursor()
        self.create()

    def create(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `bot_config` (
              `current_qq` bigint(20) NOT NULL,
              `master_qq` bigint(20) NOT NULL
            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS `reply_message` (
                `id` bigint(20) primary key ,
              `rules` text,
              `response` text,
              `rule_type` varchar(40)  NOT NULL,
              `response_type` varchar(40)  NOT NULL,
              `pic_url` text,
              `from_group` bigint(20) NOT NULL
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

    def insert_reply_message(self, rules, response, rule_type, response_type, from_group, pic_url=''):
        return self.insert('reply_message', dict(
            rules=rules,
            response=response,
            rule_type=rule_type,
            response_type=response_type,
            pic_url=pic_url,
            from_group=from_group,
        ))

    def get_qq_bot_reply(self):
        return self.query('''SELECT * FROM reply_message WHERE 1=1''')

    def add_bot_admin(self, admin_qq, bot_qq):
        self.insert('bot_config', dict(
            current_qq=bot_qq,
            master_qq=admin_qq,
        ))

    def find_qq_bot_master(self, current_qq, master_qq):
        return self.query(f'''SELECT * FROM bot_config WHERE current_qq={current_qq} 
                            AND master_qq={master_qq}''')


def is_bot_master(bot_qq, user):
    db = DB()
    try:
        r = db.find_qq_bot_master(bot_qq, user)
        if len(r) == 0:
            return False
        else:
            return True
    except Exception as e:
        print('is_bot_master')
        print(e)
        return False
