from typing import List, Optional

import requests
from pydantic import BaseModel  # pylint: disable=E0611


# 番剧
class EP(BaseModel):
    id: int
    cover: str
    long_title: str
    url: str


class Bangumi(BaseModel):
    media_id: int
    title: str
    cover: str
    styles: str
    desc: str
    eps: List[EP]


# 视频
class Video(BaseModel):
    author: str
    title: str
    description: str
    aid: int
    bvid: str
    pic: str
    created: int


# 用户
class UPInfo(BaseModel):
    mid: str
    name: str
    face: str
    sign: str


kv = {'user-agent': 'Mozilla/5.0',
      'cookie': """_uuid=41D2210A7-3333-123A-BDC6-4382C3C4510AB87492infoc; buvid3=B4E544FE-C064-C9DF-57B0-2953F25C955F89020infoc; b_nut=1659966789; buvid4=926C5EA5-DC80-B1F1-42AC-98A00325899D89020-022080821-cHGytz2Yu5E95vzk3YB7UA==; i-wanna-go-back=-1; fingerprint=74596e6f3589a7693e0d49093a010a95; buvid_fp_plain=undefined; DedeUserID=10302374; DedeUserID__ckMd5=e573f8ad8199b334; buvid_fp=74596e6f3589a7693e0d49093a010a95; b_ut=5; CURRENT_BLACKGAP=0; LIVE_BUVID=AUTO4516600502797196; rpdid=|(kRJkY~)~J0J'uYYRlR|mm|; SESSDATA=5ad164ce,1680172183,6f013*a1; bili_jct=064f76e196370f776c66596947704453; bp_video_offset_10302374=712027435226366200; bp_t_offset_10302374=712027435226366148; CURRENT_FNVAL=4048; sid=ppshjk0q; b_lsid=514105296_183B2E514EE; bsource=search_google""",
      }


class API:
    @classmethod
    def get_latest_video_by_mid(cls, mid: int) -> Optional[Video]:
        try:
            resp = requests.get(
                f"https://api.bilibili.com/x/space/arc/search?mid={mid}&ps=1",
                headers=kv,
                timeout=20,
            )
            resp.raise_for_status()
            result = resp.json()
            if result["code"] == 0:
                vlist = result["data"]["list"]["vlist"]
                return Video(**vlist[0])
        except Exception as e:
            print(e)
        return None

    @classmethod
    def get_up_info_by_mid(cls, mid: int) -> Optional[UPInfo]:
        try:
            resp = requests.get(
                f"https://api.bilibili.com/x/web-interface/card?mid={mid}",
                headers=kv,
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()
            if result["code"] == 0:
                return UPInfo(**result["data"]["card"])
        except Exception as e:
            print(e)
        return None

    @classmethod
    def search_up_by_keyword(cls, keyword: str) -> Optional[List[UPInfo]]:
        try:
            resp = requests.get(
                "https://api.bilibili.com/x/web-interface/search/type",
                headers=kv,
                params={"search_type": "bili_user", "keyword": keyword},
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            if result["code"] == 0:
                return [
                    UPInfo(
                        mid=up["mid"],
                        name=up["uname"],
                        face=up["upic"],
                        sign=up["usign"],
                    )
                    for up in result["data"]["result"]
                ]
        except Exception as e:
            print(e)
        return None

    @classmethod
    def search_bangumi_by_keyword(cls, keyword: str) -> Optional[List[Bangumi]]:
        try:
            resp = requests.get(
                "https://api.bilibili.com/x/web-interface/search/type",
                headers=kv,
                params={"search_type": "media_bangumi", "keyword": keyword},
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            if result["code"] == 0:
                return [Bangumi(**media) for media in result["data"]["result"]]
        except Exception as e:
            print(e)
        return None

    @classmethod
    def get_latest_ep_by_media_id(cls, media_id: int) -> Optional[EP]:
        try:
            resp = requests.get(
                f"https://api.bilibili.com/pgc/review/user?media_id={media_id}",
                headers=kv,
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            if result["code"] == 0:
                media = result["result"]["media"]
                return EP(
                    id=media["new_ep"]["id"],
                    cover=media["cover"],
                    long_title=media["title"],
                    url=media["share_url"],
                )
        except Exception as e:
            print(e)
        return None


if __name__ == "__main__":
    print(
        API.get_latest_ep_by_media_id(
            API.search_bangumi_by_keyword("辉夜大小姐")[0].media_id
        )
    )
