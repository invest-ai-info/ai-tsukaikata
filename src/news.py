# -*- coding: utf-8 -*-
"""data/tracker/news.json を読んで、トップの「AIアップデート」欄と
/news/ アーカイブに渡す形へ整える。

トラッカーの内部は知らない。知っているのは news.json の項目形式と
「お知らせは読む・モデルは見る」の粒度ルールだけ。読めないときは
NewsError を投げてビルドを止める（半端な欄を公開しないため）。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

JST = timezone(timedelta(hours=9))

# 要約の対象と同じ線引き（tracker/summarize.py の ANNOUNCEMENT_TYPES と同値）。
# お知らせ＝1件ずつ読む。モデル＝出たことが分かればよいので畳む。
ANNOUNCEMENT_TYPES = frozenset({"rss", "anthropic_news"})

TOP_ANNOUNCEMENTS = 10
MODEL_WINDOW_FALLBACK = timedelta(days=14)

REQUIRED_KEYS = ("uid", "source_id", "title", "url", "importance", "published")

# ベンダー識別アイコン（頭文字＋連想色の独自マーク）。
# ⚠️ 公式ロゴの模倣はしない——商標の誤認を招くため。色と文字だけで見分ける。
VENDOR_ICONS = {
    "OpenAI": ("O", "#10A37F"),
    "Anthropic": ("A", "#C15F3C"),
    "Google": ("G", "#4285F4"),
    "Google DeepMind": ("DM", "#185ABC"),
    "DeepSeek": ("DS", "#4D6BFE"),
    "Sakana AI": ("S", "#E8442E"),
    "Preferred Networks": ("PF", "#0E7C7B"),
    "ELYZA": ("E", "#2B6CB0"),
    "Alibaba Qwen": ("Q", "#6E44C4"),
    "Zhipu AI": ("Z", "#3859C4"),
    "Moonshot AI": ("M", "#5B5B6E"),
    "xAI": ("X", "#6B7280"),
}
DEFAULT_ICON_COLOR = "#8A7A64"


def vendor_icon(vendor: str) -> tuple[str, str]:
    """(表示文字, 色)。知らないベンダーは頭文字＋土色で出す（隠さない）。"""
    if vendor in VENDOR_ICONS:
        return VENDOR_ICONS[vendor]
    initial = vendor[:1].upper() if vendor else "?"
    return (initial, DEFAULT_ICON_COLOR)


class NewsError(Exception):
    """news.json / sources.yml を読めない・形が違うときに投げる。"""


@dataclass(frozen=True)
class NewsItem:
    uid: str
    source_id: str
    title: str
    url: str
    vendor: str
    label: str
    importance: str
    published: datetime  # JST
    summary_ja: str | None
    icon_code: str = "?"
    icon_color: str = DEFAULT_ICON_COLOR


def load_source_types(path: Path) -> dict[str, str]:
    """sources.yml から {id: type} を作る。お知らせ/モデルの振り分けに使う。"""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return {s["id"]: s["type"] for s in data["sources"]}
    except (OSError, yaml.YAMLError, KeyError, TypeError) as error:
        raise NewsError(f"{path}: 読めませんでした: {error}") from error


def load_news(path: Path) -> list[NewsItem]:
    """news.json を読み、新しい順の NewsItem にする。published は JST。"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        raw_items = data["items"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise NewsError(f"{path}: 読めませんでした: {error}") from error

    items: list[NewsItem] = []
    for raw in raw_items:
        missing = [key for key in REQUIRED_KEYS if not raw.get(key)]
        if missing:
            raise NewsError(
                f"{path}: 項目に必須キーがありません: {', '.join(missing)}"
                f"（uid: {raw.get('uid', '?')}）"
            )
        published = datetime.fromisoformat(raw["published"]).astimezone(JST)
        vendor = raw.get("vendor") or raw.get("label") or raw["source_id"]
        icon_code, icon_color = vendor_icon(vendor)
        items.append(NewsItem(
            uid=raw["uid"],
            source_id=raw["source_id"],
            title=raw["title"],
            url=raw["url"],
            vendor=vendor,
            label=raw.get("label") or raw.get("vendor") or raw["source_id"],
            importance=raw["importance"],
            published=published,
            summary_ja=raw.get("summary_ja") or None,
            icon_code=icon_code,
            icon_color=icon_color,
        ))
    items.sort(key=lambda item: (item.published, item.uid), reverse=True)
    return items


def is_announcement(item: NewsItem, source_types: dict[str, str]) -> bool:
    """お知らせ系なら True。型表に無い source_id は隠さない側（お知らせ）に倒す。"""
    return source_types.get(item.source_id, "rss") in ANNOUNCEMENT_TYPES


def split_recent(
    items: list[NewsItem],
    source_types: dict[str, str],
    limit: int = TOP_ANNOUNCEMENTS,
) -> dict:
    """トップ用。お知らせ最新 limit 件と、同期間のモデルのラベル畳み。"""
    announcements = [i for i in items if is_announcement(i, source_types)][:limit]
    models = [i for i in items if not is_announcement(i, source_types)]

    if announcements:
        window_start = announcements[-1].published
    elif items:
        window_start = items[0].published - MODEL_WINDOW_FALLBACK
    else:
        return {"announcements": [], "model_groups": []}

    groups: dict[str, dict] = {}
    for item in models:
        if item.published < window_start:
            continue
        group = groups.setdefault(item.label, {
            "label": item.label,
            "vendor": item.vendor,
            "count": 0,
            "latest_title": item.title,       # items は新しい順なので最初が最新
            "latest_published": item.published,
        })
        group["count"] += 1

    model_groups = sorted(
        groups.values(), key=lambda g: g["latest_published"], reverse=True
    )
    return {"announcements": announcements, "model_groups": model_groups}


def group_by_month(items: list[NewsItem]) -> list[tuple[str, list[NewsItem]]]:
    """/news/ 用。新しい月から順に（「2026年8月」, 項目リスト）を返す。"""
    months: dict[str, list[NewsItem]] = {}
    for item in items:
        label = f"{item.published.year}年{item.published.month}月"
        months.setdefault(label, []).append(item)
    return list(months.items())
