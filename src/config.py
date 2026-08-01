# -*- coding: utf-8 -*-
"""サイト全体の定数。サイト名やURLを変えるときはここだけを触る。

render.py と feeds.py の両方が同じ値を必要とするため、両方に書かず
ここに集約する。
"""
from __future__ import annotations

SITE_NAME = "AIの使い方"
SITE_URL = "https://ai-tsukaikata.com"
CUSTOM_DOMAIN = "ai-tsukaikata.com"
SITE_DESCRIPTION = "プログラマーでなくても動かせる、実際に運用している自動化の手順書。"
SITE_LANG = "ja"

# 一覧ページを持つカテゴリ。pages（about等）は一覧に出さない
LISTED_CATEGORIES = ("recipes", "tools")

CATEGORIES = {
    "recipes": {
        "label": "レシピ",
        "description": "実際に動かしている自動化を、コピペできる手順にしたものです。",
    },
    "tools": {
        "label": "ツール",
        "description": "自分で使っているAIツールの使い方と、向き不向き。",
    },
    "pages": {"label": "", "description": ""},
}

INDEX_MAX_ARTICLES = 12
