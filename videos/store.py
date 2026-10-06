# -*- coding: utf-8 -*-
"""data/videos/videos.json の読み書きと、動画の出入り。

形＝{"videos": [動画, ...], "channels": {key: {"last_ok", "fail_streak"}}}。
動画の status:
  pending  … 要約待ち
  done     … 要約済み（サイトに載る）
  skipped  … AIと関係ないと Gemini が判断した（載せない）
  failed   … 要約に MAX_ATTEMPTS 回失敗した（載せない）

⚠️ 壊れたファイルは握り潰さない（空にして続けると、要約済みが全部消えて
作り直しになり、Gemini の枠を無駄に食う）。落として人に気づかせる。
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

# 載らない動画（skipped/failed）を公開から何日まで残すか。残すのは「もう見た」の記録＝
# 同じ動画を要約待ちに戻さないため（merge が足すのは PENDING_DAYS 以内なので、それより長ければ足りる）。
# ⚠️ 要約済み（done）は期限なしで残す＝過去の月のページ（/videos/<分類>/<年-月>/）に載せ続ける
# （2026-10-06 オーナー判断「過去の動画も見れるようにしたい」）。1本 約1.3KB・1日7本ほどで、1年 約3MB
KEEP_DAYS = 45
PENDING_DAYS = 14       # 要約待ちのまま何日たったら諦めるか（溜まりすぎ防止）
MAX_ATTEMPTS = 3
DESCRIPTION_MAX = 1500  # 要約に渡す概要欄（要約が済んだら捨てる）


class StoreError(Exception):
    """videos.json が壊れている。"""


def empty() -> dict:
    return {"videos": [], "channels": {}}


def load(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        return empty()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise StoreError(f"{path} が壊れています（{error}）") from error
    if not isinstance(data, dict) or not isinstance(data.get("videos"), list):
        raise StoreError(f"{path} の形が違います（videos の一覧がありません）")
    data.setdefault("channels", {})
    return data


def save(path: Path, data: dict) -> None:
    """一時ファイルに書いてから置き換える（途中で落ちても壊れたファイルを残さない）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8", newline="\n")
    for _ in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:   # 常駐ソフトが掴んでいることがある（tracker/store.py と同じ）
            time.sleep(0.2)
    os.replace(tmp, path)


def merge(data: dict, channel: dict, entries: list[dict], now: datetime) -> int:
    """新しく見つけた動画を pending で足す。足した本数を返す。

    古すぎる動画（PENDING_DAYS より前の公開）は足さない＝チャンネルを
    追加した日に過去の動画が一気に要約待ちに入らないようにする。
    """
    known = {video["video_id"] for video in data["videos"]}
    oldest = now - timedelta(days=PENDING_DAYS)
    added = 0
    for entry in entries:
        if entry["video_id"] in known:
            continue
        if datetime.fromisoformat(entry["published"]) < oldest:
            continue
        data["videos"].append({
            "video_id": entry["video_id"],
            "title": entry["title"],
            "url": entry["url"],
            "published": entry["published"],
            "channel_key": channel["key"],
            "channel_name": channel["name"],
            "default_category": channel["category"],
            "description": entry.get("description", "")[:DESCRIPTION_MAX],
            "first_seen": now.isoformat(),
            "status": "pending",
            "attempts": 0,
        })
        known.add(entry["video_id"])
        added += 1
    return added


def record_channel(data: dict, key: str, ok: bool, now: datetime) -> None:
    status = data["channels"].setdefault(key, {"last_ok": None, "fail_streak": 0})
    if ok:
        status["last_ok"] = now.isoformat()
        status["fail_streak"] = 0
    else:
        status["fail_streak"] = status.get("fail_streak", 0) + 1


def pending(data: dict) -> list[dict]:
    """要約待ちを新しい順に。"""
    waiting = [v for v in data["videos"] if v["status"] == "pending"]
    return sorted(waiting, key=lambda v: v["published"], reverse=True)


def mark_done(video: dict, result: dict, model: str, now: datetime) -> None:
    if not result["is_ai"]:
        video["status"] = "skipped"
    else:
        video["status"] = "done"
        video["category"] = result["category"]
        video["summary"] = result["summary"]
        video["for_whom"] = result["for_whom"]
        video["caution"] = result["caution"]
        video["summary_source"] = "gemini"   # 機械生成である旨の明示
        video["model"] = model
        video["summarized_at"] = now.isoformat()
    video.pop("description", None)


def mark_failed(video: dict, reason: str) -> None:
    video["attempts"] = video.get("attempts", 0) + 1
    video["last_error"] = reason[:200]
    if video["attempts"] >= MAX_ATTEMPTS:
        video["status"] = "failed"
        video.pop("description", None)


def prune(data: dict, now: datetime, channel_keys: set[str] | None = None) -> int:
    """古い動画・諦めた要約待ち・外したチャンネルの動画を消す。消した本数を返す。

    要約済み（done）は古くても消さない（過去の月のページに載せ続ける）。
    チャンネルを channels.yml から外したときだけ、そのチャンネルの要約済みも消える。
    """
    keep_after = now - timedelta(days=KEEP_DAYS)
    pending_after = now - timedelta(days=PENDING_DAYS)
    before = len(data["videos"])

    def keep(video: dict) -> bool:
        published = datetime.fromisoformat(video["published"])
        if video["status"] != "done" and published < keep_after:
            return False
        if video["status"] == "pending" and published < pending_after:
            return False
        if channel_keys is not None and video["channel_key"] not in channel_keys:
            return False
        return True

    data["videos"] = [v for v in data["videos"] if keep(v)]
    if channel_keys is not None:
        data["channels"] = {k: v for k, v in data["channels"].items() if k in channel_keys}
    return before - len(data["videos"])
