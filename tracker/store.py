# -*- coding: utf-8 -*-
"""既読管理・minorキュー・ソース死活記録。ファイルに触る層。

判定は「seen.json に無いもの＝新着」なので、cron が遅延・スキップしても
次に走ったときに必ず拾う。取りこぼしは発生せず、遅れるだけ。
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import Update

RETENTION_DAYS = 90
FAILURE_THRESHOLD = 3


def empty_state() -> dict:
    return {"uids": {}, "pending_minor": [], "failures": {}}


def load_state(path: Path) -> dict:
    if not Path(path).exists():
        return empty_state()
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    for key, default in empty_state().items():
        state.setdefault(key, default)
    return state


def save_state(path: Path, state: dict) -> None:
    """一時ファイルに書いてから置換する。

    直接 "w" で開くと書き込み前にファイルが0バイトに切り詰められ、途中で
    落ちると壊れた seen.json が残る。そうなると以降の実行が毎回落ちる。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)


def select_unseen(state: dict, updates: list[Update]) -> list[Update]:
    return [u for u in updates if u.uid not in state["uids"]]


def mark_seen(state: dict, updates: list[Update], now: datetime) -> None:
    for update in updates:
        state["uids"].setdefault(update.uid, now.isoformat())


def queue_minor(state: dict, updates: list[Update]) -> None:
    """翌朝のダイジェストに載せるため minor を溜める。"""
    state["pending_minor"].extend(u.to_dict() for u in updates)


def take_pending_minor(state: dict) -> list[Update]:
    """溜まった minor を取り出してキューを空にする。"""
    items = [Update.from_dict(d) for d in state["pending_minor"]]
    state["pending_minor"] = []
    return items


def record_result(state: dict, source_id: str, error: str | None, count: int) -> None:
    """取得結果を記録する。成功かつ1件以上なら失敗カウントをリセットする。

    ⚠️ count には「そのポーリングで取得できた生の件数」を渡すこと。
    select_unseen 後の「新着件数」を渡してはいけない。更新の少ないソースは
    新着0が普通なので、それを渡すと健全なソースが3時間で死亡扱いになる。
    生の件数なら、更新が止まっているフィードでも過去記事が返るので0にならない。
    """
    if error is None and count > 0:
        state["failures"].pop(source_id, None)
        return
    entry = state["failures"].get(source_id, {"count": 0, "last_error": ""})
    entry["count"] += 1
    entry["last_error"] = error or "0件"
    state["failures"][source_id] = entry


def dead_sources(state: dict) -> list[tuple[str, int, str]]:
    """FAILURE_THRESHOLD 回以上連続で失敗しているソースを返す。

    フィードURLは予告なく変わる。これが無いと「静かに情報が来なくなって
    いたことに数ヶ月気づかない」という最悪の壊れ方をする。
    """
    return [
        (source_id, entry["count"], entry["last_error"])
        for source_id, entry in sorted(state["failures"].items())
        if entry["count"] >= FAILURE_THRESHOLD
    ]


def forget_removed_sources(state: dict, active_source_ids: set[str]) -> int:
    """sources.yml から消えたソースの失敗記録を捨て、捨てた件数を返す。

    これが無いと、設定から外したソースが永久にダイジェストの死活警告に
    出続け、警告欄そのものが読まれなくなる。
    """
    stale = [sid for sid in state["failures"] if sid not in active_source_ids]
    for source_id in stale:
        del state["failures"][source_id]
    return len(stale)


def prune(state: dict, now: datetime) -> int:
    """RETENTION_DAYS を超えた uid を削除し、削除件数を返す。"""
    cutoff = now - timedelta(days=RETENTION_DAYS)
    stale = []
    for uid, seen_at in state["uids"].items():
        try:
            seen_dt = datetime.fromisoformat(seen_at)
        except (TypeError, ValueError):
            stale.append(uid)
            continue
        if seen_dt.tzinfo is None:
            seen_dt = seen_dt.replace(tzinfo=timezone.utc)
        if seen_dt < cutoff:
            stale.append(uid)
    for uid in stale:
        del state["uids"][uid]
    return len(stale)
