# -*- coding: utf-8 -*-
"""サイト全体の定数。サイト名やURLを変えるときはここだけを触る。

render.py と feeds.py の両方が同じ値を必要とするため、両方に書かず
ここに集約する。
"""
from __future__ import annotations

SITE_NAME = "AIの使い方"
SITE_URL = "https://ai-tsukaikata.com"
CUSTOM_DOMAIN = "ai-tsukaikata.com"

# トップページのカテゴリーボタン（2026-08-13 オーナー指示・設計書 §1）。
# 後から増やすときはここに1行足すだけ。並び順のまま表示される。
# ⚠️ /scenes/<name>/ を指すボタンは、その場面に記事が入るまで自動で隠れる
# （render.py が絞る）。0本の場面へのリンクは404になるため。
TOP_NAV = [
    {"label": "初めての方", "url": "/start/"},
    {"label": "AI副業", "url": "/scenes/earn/"},
    {"label": "AI詐欺を防ぐ", "url": "/scenes/safety/"},
    {"label": "セキュリティ対策", "url": "/scenes/security/"},
    {"label": "最新アップデート情報", "url": "/news/"},
    {"label": "AIレシピ", "url": "/recipes/"},
    {"label": "深掘り記事", "url": "/tools/"},
]

# AdSense のサイト運営者ID（2026-08-13 オーナーが審査コードを提供）。
# 審査タグは templates/base.html、ads.txt は src/build.py がこのIDから作る。
ADSENSE_PUBLISHER_ID = "pub-2552122294306014"
SITE_DESCRIPTION = (
    "プログラミングなしで、AIに頼んで自動化を作る方法。"
    "使った指示文をそのまま載せ、なぜその言い方が効くのかまで書いています。"
)
SITE_LANG = "ja"

# 一覧ページを持つカテゴリ。pages（about等）は一覧に出さない
LISTED_CATEGORIES = ("recipes", "tools")

CATEGORIES = {
    "recipes": {
        "label": "レシピ",
        "description": "AIに頼んで自動化を作る手順と、そのとき使った指示文。コピーしてそのまま使えます。",
    },
    "tools": {
        "label": "ツール",
        "description": "自分で使っているAIツールの使い方と、向き不向き。",
    },
    "pages": {"label": "", "description": ""},
}

INDEX_MAX_ARTICLES = 12

# 場面（scene）＝「どんなときに読むか」の軸。カテゴリ（記事の種類）とは別で、
# 1記事に1つだけ付ける。記事が0本の場面はナビにも一覧にも出さないので、
# 中身が無いうちから並べておいてよい（入った時点で出てくる）。
SCENES = {
    "start": {
        "label": "はじめて",
        "lead": "AIに何を頼めるのかが、まだ見えていない段階の人へ。",
    },
    "work": {
        "label": "仕事",
        "lead": "書く・まとめる・確かめる。仕事の頼み方をそのまま載せています。",
    },
    "research": {
        "label": "情報収集",
        "lead": "追いかける・調べる・要約させる。見に行かなくても届く形にします。",
    },
    "automate": {
        "label": "自動化",
        "lead": "決まった時刻に動かす、静かに壊れたのを見張らせる。",
    },
    "life": {
        "label": "暮らし",
        "lead": "家計・手続き・買いもの。仕事以外の面倒をAIに渡します。",
    },
    "earn": {
        "label": "副業",
        "lead": "副業の作業と段取りをAIに手伝わせます。「必ず稼げる」は書きません。",
    },
    "safety": {
        "label": "詐欺を防ぐ",
        "lead": "AIで作られた・AIを名乗る詐欺から身を守ります。断定より、確かめる手順を。",
    },
    "security": {
        "label": "セキュリティ対策",
        "lead": "個人情報・アカウント・履歴。AIを使う前後の守りを固めます。",
    },
    "fun": {
        "label": "遊び・創作",
        "lead": "写真・文章・趣味。役に立つかは置いておいて、まず面白い使い方。",
    },
    "choose": {
        "label": "AIを選ぶ",
        "lead": "どのAIを使うか。公式発表の数字だけで比べています。",
    },
}
