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


# 場面アイコン（2026-08-25 デザイン承認・提案A）。16pxグリッドの線画SVGの中身だけを持つ。
# 描画は templates/_macros.html の scene_icon マクロ（stroke=currentColor＝場面の文字色を継承）。
# ⚠️ SCENES に場面を足したら、ここにも必ず足すこと。漏れは tests/test_render.py の
# test_every_scene_has_an_icon が機械で検出する（アイキャッチのclass照合と同じ思想）。
SCENE_ICONS = {
    "start": (  # 芽
        '<path d="M8 13.5 V7"></path>'
        '<path d="M8 9 C6 9 4.5 7.5 4 5.5 C6 5.5 7.5 6.5 8 8.5"></path>'
        '<path d="M8 7 C8 5 9.5 3.5 11.5 3 C11.5 5 10 6.8 8 7"></path>'
    ),
    "work": (  # 鉛筆
        '<path d="M11 3 L13 5 L6 12 L3.5 12.5 L4 10 Z"></path>'
    ),
    "research": (  # 虫めがね
        '<circle cx="6.5" cy="6.5" r="4"></circle>'
        '<path d="M9.5 9.5 L13.5 13.5"></path>'
    ),
    "automate": (  # 歯車
        '<circle cx="8" cy="8" r="3"></circle>'
        '<path d="M8 2.5 V4.5 M8 11.5 V13.5 M2.5 8 H4.5 M11.5 8 H13.5"></path>'
        '<path d="M4.1 4.1 L5.5 5.5 M10.5 10.5 L11.9 11.9 M11.9 4.1 L10.5 5.5 M5.5 10.5 L4.1 11.9"></path>'
    ),
    "life": (  # 家
        '<path d="M3 8.5 L8 4 L13 8.5"></path>'
        '<path d="M4.5 7.5 V13 H11.5 V7.5"></path>'
    ),
    "earn": (  # ¥硬貨
        '<circle cx="8" cy="8" r="5.5"></circle>'
        '<path d="M5.8 5 L8 8 M10.2 5 L8 8 M8 8 V11.2 M6.2 8.8 H9.8 M6.2 10.4 H9.8"></path>'
    ),
    "safety": (  # 盾
        '<path d="M8 2.5 L13 4.5 V8 C13 11.5 10.8 13.2 8 14 C5.2 13.2 3 11.5 3 8 V4.5 Z"></path>'
        '<path d="M5.8 8 L7.4 9.6 L10.4 6.6"></path>'
    ),
    "security": (  # 南京錠
        '<rect x="4.5" y="7" width="7" height="6" rx="1"></rect>'
        '<path d="M5.8 7 V5 C5.8 3.6 6.8 2.6 8 2.6 C9.2 2.6 10.2 3.6 10.2 5 V7"></path>'
    ),
    "fun": (  # パレット
        '<path d="M8 2.8 C4.2 2.8 2.2 5.6 2.6 8.4 C3 11.4 5.6 13.2 8.2 13.2 '
        'C9.4 13.2 9.8 12.4 9.4 11.6 C9 10.8 9.4 10 10.4 10 H12 C13 10 13.6 9 13.4 7.6 '
        'C13 4.6 11 2.8 8 2.8 Z"></path>'
        '<circle cx="5.4" cy="6" r="0.9" fill="currentColor" stroke="none"></circle>'
        '<circle cx="8" cy="4.9" r="0.9" fill="currentColor" stroke="none"></circle>'
        '<circle cx="10.6" cy="6.4" r="0.9" fill="currentColor" stroke="none"></circle>'
    ),
    "choose": (  # 分岐
        '<path d="M8 13.5 V8 M8 8 L4.2 4.8 M8 8 L11.8 4.8"></path>'
        '<path d="M4.2 7 V4.8 H6.4 M11.8 7 V4.8 H9.6"></path>'
    ),
}
