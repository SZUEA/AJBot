"""博客订阅
博客订阅+FEED_URL
"""
import base64, requests, re, sqlite3, traceback, feedparser, os, time, asyncio
import socket
from io import BytesIO
from typing import List, Optional
from pydantic import BaseModel
from EAbotoy import Action, logger
from EAbotoy.contrib import get_cache_dir, plugin_receiver
# from EAbotoy.decorators import from_these_groups
from EAbotoy.model import WeChatMsg
from EAbotoy.schedule import scheduler
from plugins.bot_reply import is_bot_master

action = Action(os.environ["wxid"])
socket.setdefaulttimeout(60)
# white_groups = ['18803656716@chatroom']
DB_PATH = get_cache_dir("blog_feed_subscriber") / "db.sqlite3"


class DB:
    def __init__(self):
        self.con = sqlite3.connect(DB_PATH)
        self.cur = self.con.cursor()
        # blog_data: url, date
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS blog_feed_data(url varchar(40) primary key, created integer);"
        )
        # blog_subscribed: name, gid, url
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS blog_subscribed(name varchar(40),gid varchar(40),url string,primary key(gid,url));"
        )
        self.con.commit()

    def subscribe_blog(self, name: str, gid: str, url: str) -> bool:
        """返回False表示已经订阅过了"""
        self.cur.execute(f"SELECT * FROM blog_subscribed WHERE gid='{gid}' AND url='{url}'")
        if self.cur.fetchall():
            return False
        self.cur.execute(f"INSERT INTO blog_subscribed (name,gid,url) VALUES ('{name}', '{gid}','{url}')")
        self.con.commit()
        return True

    def unsubscribe_blog(self, gid: str, name: str) -> bool:
        """返回False表示未订阅"""
        self.cur.execute(f"SELECT * FROM blog_subscribed WHERE gid='{gid}' AND name='{name}'")
        if not self.cur.fetchall():
            return False
        self.cur.execute(f"DELETE FROM blog_subscribed WHERE gid='{gid}' AND name='{name}'")
        self.con.commit()
        return True

    def get_subscribed_blogs_by_gid(self, gid: str) -> List[str]:
        self.cur.execute(f"SELECT * FROM blog_subscribed WHERE gid='{gid}'")
        return [ret[0] + ':' + ret[2] for ret in self.cur.fetchall()]

    def get_subscribed_blogs_url(self) -> List[str]:
        self.cur.execute("SELECT * FROM blog_subscribed")
        return [ret[2] for ret in self.cur.fetchall()]

    def get_gids_by_url(self, url: str) -> List[str]:
        self.cur.execute(f"SELECT * FROM blog_subscribed WHERE url='{url}'")
        return [ret[1] for ret in self.cur.fetchall()]

    def get_name_by_url_url_gid(self, url: str, gid: str) -> str:
        self.cur.execute(f"SELECT name FROM blog_subscribed WHERE url='{url}' and gid='{gid}'")
        return self.cur.fetchall()[0][0]

    def judge_blog_updated(self, url: str, created: int) -> bool:
        """如果更新了则返回True，并更新数据"""
        self.cur.execute(f"SELECT * FROM blog_feed_data WHERE url='{url}'")
        found = self.cur.fetchone()
        if found:
            if created > found[1]:
                self.cur.execute(
                    f"UPDATE blog_feed_data SET created='{created}' WHERE url='{url}'"
                )
                self.con.commit()
                return True
        else:
            # 没找到说明首次更新，就不提示了
            self.cur.execute(
                f"INSERT INTO blog_feed_data (url, created) VALUES ('{url}', '{created}')"
            )
            self.con.commit()
            return False
        return False


# 博客
class Blog(BaseModel):
    author: str
    title: str
    description: str
    url: str
    created: int


##kv = {'user-agent': 'Mozilla/5.0'}


class API:
    @classmethod
    def get_latest_blog_by_url(cls, url: str) -> Optional[Blog]:
        try:
            feed = feedparser.parse(url)
            if feed['bozo'] == False and len(feed['entries']) > 1:
                feed = feed.entries[0]
                try:
                    blog_author = feed.author
                except Exception:
                    blog_author = 'None'

                return Blog(title=feed.title, author=blog_author, url=feed.link, description=clean_html(feed.summary),
                            created=time.mktime(feed.updated_parsed))
        except Exception:
            logger.warning(traceback.format_exc())
        return None


# @from_these_groups(*white_groups)
@plugin_receiver.wx
def receive_wx_msg(ctx: WeChatMsg):
    if not ctx.IsGroup:
        return
    # from_group = ctx.FromUserName
    # if from_group not in white_groups:
    #    return
    isAdmin = is_bot_master(ctx.CurrentWxid, ctx.ActionUserName) or ctx.ActionUserName == ctx.master
    if not isAdmin:
        return
    # 订阅博客
    if ctx.Content.startswith("博客订阅"):
        args = ctx.Content.split(' ')
        if len(args) == 3:
            db = DB()
            if db.subscribe_blog(args[1], ctx.GroupId, args[2]):
                msg = f"成功订阅博客：{args[1]}\n订阅地址：{args[2]}"
            else:
                msg = "本群已订阅该博客"
            action.sendWxText(ctx.GroupId, msg)
        elif len(args) == 1:
            db = DB()
            tmp = "\n".join(db.get_subscribed_blogs_by_gid(ctx.GroupId));
            msg = "本群已订阅博客\n------------\n" + tmp;
            action.sendWxText(ctx.GroupId, msg)
    # 退订博客
    elif ctx.Content.startswith("博客退订"):
        args = ctx.Content.split(' ')
        if len(args) == 2:
            db = DB()
            if db.unsubscribe_blog(ctx.GroupId, args[1]):
                msg = "成功退订博客：{}".format(args[1])
            else:
                msg = "本群未订阅该博客"
        action.sendWxText(ctx.GroupId, msg)


def send_img(group, imageUrl):
    res = requests.get(imageUrl)
    base = str(base64.b64encode(BytesIO(res.content).read()), encoding="utf-8")
    action.sendImg(group, imageBase64=base)


# schedule task
async def check_blog():
    db = DB()
    for url in db.get_subscribed_blogs_url():
        blog = API.get_latest_blog_by_url(url)
        if blog is not None:
            if db.judge_blog_updated(url, blog.created):
                if action is not None:
                    for group in db.get_gids_by_url(url):
                        # action.send_img(
                        #    group,
                        #    imageUrl=video.pic,
                        # )
                        if blog.author == 'None':
                            author = db.get_name_by_url_url_gid(url, group)
                        else:
                            author = blog.author
                        action.sendApp(group,
                                       '<appmsg appid="" sdkver="0">\n\t\t'
                                       f'<title>{blog.title}</title>\n\t\t'
                                       f'<des>{author}：{blog.description + "...更多内容请移步订阅源"}</des>\n\t\t'
                                       '<username />\n\t\t<action>view</action>\n\t\t'
                                       '<type>5</type>\n\t\t'
                                       '<showtype>0</showtype>\n\t\t'
                                       f'<url>{blog.url}</url>\n\t\t'
                                       '</appmsg>')


def clean_html(string):
    return re.sub(r"</?.+?/?>", "", string)


def run_scheduler():
    logger.info("FEED订阅抓取")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(check_blog())
    loop.close()
    logger.info("FEED订阅抓取完毕")
scheduler.add_job(run_scheduler, "interval", minutes=10)
run_scheduler()
