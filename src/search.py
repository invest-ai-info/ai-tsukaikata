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

from . import config
from .content import Article

HEADING_RE = re.compile(r"<h[23]\b[^>]*>(.*?)</h[23]>", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

# 索引の大きさの予算（バイト）。実測 248KB（2026-09-20・187本）に5割の余裕。
# 超えたら tests/test_search.py が落ちる＝黙って重くならないための歯止め。
# 記事が増えて超えたら、値を上げる前に「見出しが冗長になっていないか」を見る
INDEX_BUDGET_BYTES = 400 * 1024


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


def search_json(articles: list[Article]) -> str:
    """search.json の本文。日本語をそのまま書き、区切りは詰める（gzip 後は差が無いが生の大きさが読みやすい）。"""
    return json.dumps(build_index(articles), ensure_ascii=False, separators=(",", ":")) + "\n"
