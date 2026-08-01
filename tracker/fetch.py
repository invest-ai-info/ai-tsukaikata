# -*- coding: utf-8 -*-
"""sources.yml を読み、各ソースから Update を取得する。ネットワークに触る唯一の層。

bot ブロックを迂回するための User-Agent 偽装はしない。403 を返すソースは
別ルートを使うか追わない。
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import yaml

from .models import Update, make_uid

USER_AGENT = "ai-tsukaikata-tracker/1.0"
TIMEOUT = 20
MAX_ENTRIES = 30
HF_API = "https://huggingface.co/api/models"


def load_sources(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("sources", [])


def _http_get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def _to_utc(value: str) -> datetime | None:
    """RFC822 と ISO8601 の両方を受け付けて UTC に正規化する。"""
    if not value:
        return None
    parsed = None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_feed(source: dict, raw: bytes) -> list[Update]:
    """RSS / Atom のバイト列を Update のリストにする。"""
    feed = feedparser.parse(raw)
    updates = []
    for entry in feed.entries[:MAX_ENTRIES]:
        published = _to_utc(entry.get("published") or entry.get("updated") or "")
        link = entry.get("link", "")
        if published is None or not link:
            continue
        updates.append(Update(
            uid=make_uid(source["id"], entry.get("id") or link),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=(entry.get("title") or "").strip(),
            url=link,
            published=published,
            summary=entry.get("summary", "") or entry.get("description", ""),
        ))
    return updates


def parse_huggingface(source: dict, raw: bytes) -> list[Update]:
    """HuggingFace models API の JSON を Update のリストにする。"""
    models = json.loads(raw)
    updates = []
    for model in models[:MAX_ENTRIES]:
        model_id = model.get("modelId") or model.get("id") or ""
        created = _to_utc(model.get("createdAt", ""))
        if not model_id or created is None:
            continue
        updates.append(Update(
            uid=make_uid(source["id"], model_id),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=model_id,
            url=f"https://huggingface.co/{model_id}",
            published=created,
            summary=f"HuggingFace に新しいモデル {model_id} が公開されました。",
        ))
    return updates


def fetch_source(source: dict) -> tuple[list[Update], str | None]:
    """1ソースを取得する。(updates, error) を返し、例外は投げない。

    1ソースの失敗で全体を止めないため。失敗は呼び出し側が記録する。
    """
    try:
        if source["type"] == "huggingface":
            url = (
                f"{HF_API}?author={source['org']}"
                f"&sort=createdAt&direction=-1&limit={MAX_ENTRIES}"
            )
            return parse_huggingface(source, _http_get(url)), None
        return parse_feed(source, _http_get(source["url"])), None
    except Exception as error:  # noqa: BLE001 - 全ソースを止めないため握る
        return [], f"{type(error).__name__}: {str(error)[:80]}"
