# -*- coding: utf-8 -*-
"""YouTube チャンネルの RSS を取って、動画の一覧にする。

鍵は要らない（`/feeds/videos.xml?channel_id=`）。ネットワークに触るのは fetch_feed だけ。

🚨 2026-10-02 の調査で、**正しい channel_id でも 404 や 500 を何回も続けて返す**ことが分かった
（最大30回）。だから再試行する。1回の 404 で「ID違い」「チャンネル停止」と決めない。
"""
from __future__ import annotations

import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
USER_AGENT = "ai-tsukaikata-videos/1.0 (+https://ai-tsukaikata.com)"
TIMEOUT = 20
# 待ち時間（秒）。合計で約1分。全部失敗したらその回は飛ばす（次の回でまた試す）
RETRY_WAITS = (3, 5, 8, 12, 15, 20)

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


class FeedError(Exception):
    """再試行しても取れなかった・中身が RSS ではない。"""


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def fetch_feed(channel_id: str, get=_get, sleep=time.sleep,
               waits: tuple[int, ...] = RETRY_WAITS) -> bytes:
    """RSS の生データを返す。404/500 は一時的な失敗として待って取り直す。"""
    url = FEED_URL.format(channel_id=channel_id)
    errors: list[str] = []
    for attempt in range(len(waits) + 1):
        try:
            return get(url)
        except urllib.error.HTTPError as error:
            errors.append(f"HTTP {error.code}")
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            errors.append(type(error).__name__)
        if attempt < len(waits):
            sleep(waits[attempt])
    raise FeedError(f"{len(errors)}回とも取れませんでした（{', '.join(errors[-3:])}）")


def _text(element, path: str) -> str:
    found = element.find(path, NS)
    return (found.text or "").strip() if found is not None and found.text else ""


def parse_feed(raw: bytes) -> list[dict]:
    """動画の一覧を返す。ショート（リンクが /shorts/）は除く。

    返す形＝{"video_id", "title", "url", "published"（ISO 8601）, "description"}。
    """
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        raise FeedError(f"RSS として読めません（{error}）") from error
    if root.tag != f"{{{NS['atom']}}}feed":
        raise FeedError("RSS として読めません（feed 要素がありません）")

    videos = []
    for entry in root.findall("atom:entry", NS):
        video_id = _text(entry, "yt:videoId")
        link = entry.find("atom:link[@rel='alternate']", NS)
        url = link.get("href", "") if link is not None else ""
        if not video_id or "/shorts/" in url:
            continue
        published = _text(entry, "atom:published")
        try:
            datetime.fromisoformat(published)
        except ValueError:
            continue   # 日付の無い項目は並べられないので飛ばす
        videos.append({
            "video_id": video_id,
            "title": _text(entry, "atom:title"),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "published": published,
            "description": _text(entry, "media:group/media:description"),
        })
    return videos
