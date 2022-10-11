import sqlite3
from typing import List

from EAbotoy.contrib import get_cache_dir

DB_PATH = get_cache_dir("realname") / "myDB.sqlite3"


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
            CREATE TABLE IF NOT EXISTS `realname` (
              `wxid` varchar(40) PRIMARY KEY NOT NULL,
              `name` varchar(40) NOT NULL
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

    def replace(self, tb, dt):
        ls = [(k, dt[k]) for k in dt if dt[k] is not None]
        sql = 'replace into %s (' % tb + ','.join(i[0] for i in ls) + \
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

    def get_real_name(self, from_wxid):
        return self.query(f'''SELECT * FROM realname WHERE wxid="{from_wxid}"''')

    def add_real_name(self, wxid, name):
        self.replace('realname', dict(
            wxid=wxid,
            name=name,
        ))


def join_real_name(wxid, name):
    db = DB()
    try:
        return db.replace('realname', dict(wxid=wxid, name=name))
    except Exception as e:
        print('add_real_name_error')
        print(e)
        return False
