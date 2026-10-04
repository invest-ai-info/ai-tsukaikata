# -*- coding: utf-8 -*-
"""サイト内検索の索引。記事から search.json の中身を作る。ファイルは書かない。

探すのはブラウザ側（static/js/search.js）。ここが決めるのは「何を探せる文字に
するか」だけ＝タイトル・説明文・タグ・見出し（h2/h3）。本文は入れない
（索引が10倍になる。実測 2026-09-20: 見出しまで 248KB / 本文全部 2.7MB）。
正規化（全角→半角・小文字）は JS 側で行うので、ここは生の文字だけを入れる
（正規化済みの文字を並べて持つと索引が2倍になる）。
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta

from . import config
from .content import Article

HEADING_RE = re.compile(r"<h[23]\b[^>]*>(.*?)</h[23]>", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

# ニュースは毎日たまるので、索引に入れるのは直近この日数だけ（2026-10-04 オーナー判断＝1か月）。
# 古いものは /news/・/ainews/ の一覧でたどれる。全部入れると索引が上限を超え、重くなり続ける
NEWS_DAYS = 30

# 索引の大きさの予算（バイト・**gzip で圧縮した後の大きさ**）。
# 超えたら tests/test_search.py が落ちる＝黙って重くならないための歯止め。
# 記事が増えて超えたら、値を上げる前に「見出しが冗長になっていないか」を見る。
#
# 📌 2026-10-04 に「圧縮前 400KB」から「圧縮後 200KB」へ変えた。ニュース（直近1か月）を足すと
# 圧縮前は約480KBになるが、本番（GitHub Pages）は gzip で送っていて、読者が実際に受け取るのは
# 約125KB（記事だけの時点で圧縮前 約340KB → 届くのは約100KB を実測）。重さを決めるのは後者。
# 記事は1日数本ずつ増える（1本あたり圧縮後 約0.4KB）ので、200KB なら数か月は持つ
INDEX_BUDGET_GZIP_BYTES = 200 * 1024


def plain_text(fragment: str) -> str:
    """HTML の断片から文字だけを取り出す。タグを剥がし、実体参照を戻し、空白を1つに畳む。"""
    return SPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", fragment))).strip()


def headings(body_html: str) -> list[str]:
    """本文の h2/h3 の文字。`{: .what}` は Markdown 変換で class になっているので残らない。"""
    texts = (plain_text(inner) for inner in HEADING_RE.findall(body_html))
    return [text for text in texts if text]


def build_index(articles: list[Article]) -> list[dict]:
    """記事1本を索引1件にする。表示用の札（category_label / scene_label）も config から入れる＝
    JS 側に日本語の対応表を持たせない。"""
    return [
        {
            "url": a.url,
            "title": a.title,
            "description": a.description,
            "tags": list(a.tags),
            "headings": headings(a.body_html),
            "category": a.category,
            "category_label": config.CATEGORIES[a.category]["label"],
            "scene": a.scene,
            "scene_label": config.SCENES[a.scene]["label"] if a.scene else None,
            "published": a.published.isoformat(),
        }
        for a in articles
    ]


def video_index(videos: dict | None) -> list[dict]:
    """AI動画まとめ（src/videos.py の load_videos の結果）の動画を索引にする（2026-10-02）。

    行き先は YouTube ではなく /videos/ の該当カード（#v-<動画ID>）＝要約と注意書きを先に見せる。
    載せるのは /videos/ に実際に並んでいる動画だけ（ページに無い動画へ飛ばさない）。
    探せる文字＝題（タイトル枠）・要約（説明文枠）・チャンネル名と分類（タグ枠）。
    """
    if not videos:
        return []
    return [
        {
            "url": f"/videos/#v-{video['video_id']}",
            "title": video["title"],
            "description": " ".join(video["summary"]),
            "tags": [video["channel_name"], section["label"], "動画", "YouTube"],
            "headings": [],
            "category": "videos",
            "category_label": "AI動画",
            "scene": None,
            "scene_label": None,
            "published": video["published"].date().isoformat(),
        }
        for section in videos["sections"]
        for video in section["entries"]
    ]


def news_index(items, category: str, label: str, now: datetime,
               days: int = NEWS_DAYS, with_summary: bool = True) -> list[dict]:
    """ニュース（src/news.py の NewsItem）を索引にする（2026-10-04）。直近 days 日だけ。

    行き先は発表元・メディアの記事そのもの（検索結果に要約が出るので中身は先に分かる）。
    with_summary=False（メディアの見出し）は説明文を空にする＝/ainews/ と同じく本文の抜粋を載せない。
    ⚠️ http(s) 以外の URL は入れない（JS がそのまま href にするため。javascript: を通さない）。
    """
    since = now - timedelta(days=days)
    return [
        {
            "url": item.url,
            "title": item.title,
            "description": (item.summary_ja or "").replace("\n", " ") if with_summary else "",
            "tags": [item.vendor],
            "headings": [],
            "category": category,
            "category_label": label,
            "scene": None,
            "scene_label": None,
            "published": item.published.date().isoformat(),
        }
        for item in items or []
        if item.published >= since and item.url.startswith(("https://", "http://"))
    ]


def search_json(articles: list[Article], videos: dict | None = None,
                news=None, media_news=None, now: datetime | None = None) -> str:
    """search.json の本文。日本語をそのまま書き、区切りは詰める（gzip 後は差が無いが生の大きさが読みやすい）。

    news / media_news は src/news.py の NewsItem のリスト（AIアップデート / AIニュース）。
    now はニュースの「直近1か月」を数える基準（テストから固定できるように引数にしてある）。
    """
    index = build_index(articles) + video_index(videos)
    if news or media_news:
        if now is None:
            raise ValueError("ニュースを索引に入れるときは now が要ります")
        index += news_index(news, "updates", "AIアップデート", now)
        index += news_index(media_news, "ainews", "AIニュース", now, with_summary=False)
    return json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n"
