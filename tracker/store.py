# -*- coding: utf-8 -*-
"""既読管理・minorキュー・ソース死活記録。ファイルに触る層。

判定は「seen.json に無いもの＝新着」なので、cron が遅延・スキップしても
次に走ったときに必ず拾う。取りこぼしは発生せず、遅れるだけ。
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import Update

RETENTION_DAYS = 90
FAILURE_THRESHOLD = 3

# 何日あたらしい記事が出ていなければ「止まっている」とみなすか。
# 実測（2026-08-02）でベンダーの静かな期間は最長でも2週間程度だったのに対し、
# 実質停止していた Moonshot / Zhipu / Qwen は5〜7週。14日にすると通常の
# 静かな期間まで拾って警告欄が読まれなくなるので、30日で切る。
STALE_DAYS = 30

# 保存直後の読み込みが常駐ソフトのスキャンとぶつかることがある（Windows）。
# 数十ミリ秒で解けるので、少しだけ待って読み直す。
LOCK_RETRY_DELAYS = (0.05, 0.1, 0.2)


def empty_state() -> dict:
    return {"uids": {}, "pending_minor": [], "failures": {}, "latest": {}}


def load_state(path: Path) -> dict:
    if not Path(path).exists():
        return empty_state()

    # PermissionError だけ待って読み直す。壊れたJSONは即座に落とす
    # （リトライしても直らないし、握り潰すと全uidが新着に戻って
    #   過去の major まで再送される）。
    for delay in LOCK_RETRY_DELAYS:
        try:
            with open(path, encoding="utf-8") as f:
                state = json.load(f)
            break
        except PermissionError:
            time.sleep(delay)
    else:
        # 最後の1回。ここでも駄目なら本物の権限問題なので落として気づかせる
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

    # 置換も常駐ソフトのスキャンとぶつかる（Windows の WinError 32）。
    # 実測ではここが本命で、load_state 側より高い頻度で当たる。
    for delay in LOCK_RETRY_DELAYS:
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(delay)
    os.replace(tmp, path)  # 最後の1回。駄目なら落として気づかせる


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


def record_latest(state: dict, source_id: str, updates: list[Update]) -> None:
    """そのソースで観測した最新の公開日を記録する。

    record_result が見るのは取得の成否と件数だけなので、更新が止まった
    フィードは古い記事を返し続けて永久に健康に見える。中身が動いているかは
    公開日で見るしかない。

    ⚠️ 日付を巻き戻さないこと。フィードが一時的に古い記事だけ返した回に
    上書きすると、止まっていないソースが突然「停止」に見える。
    """
    if not updates:
        return
    newest = max(update.published for update in updates)
    current = state["latest"].get(source_id)
    if current:
        try:
            if datetime.fromisoformat(current) >= newest:
                return
        except (TypeError, ValueError):
            pass  # 壊れた記録は上書きして直す
    state["latest"][source_id] = newest.isoformat()


def stale_sources(state: dict, now: datetime) -> list[tuple[str, int]]:
    """STALE_DAYS 以上あたらしい記事の出ていないソースを、古い順に返す。

    記録の無いソースは出さない。「止まっている」ではなく「まだ分からない」で、
    この機能より前に書かれた seen.json には latest が無いため。
    """
    result: list[tuple[str, int]] = []
    for source_id, seen_at in state["latest"].items():
        try:
            latest = datetime.fromisoformat(seen_at)
        except (TypeError, ValueError):
            continue  # ここで落とすとダイジェスト送信ごと止まる
        if latest.tzinfo is None:
            latest = latest.replace(tzinfo=timezone.utc)
        days = (now - latest).days
        if days >= STALE_DAYS:
            result.append((source_id, days))
    result.sort(key=lambda item: (-item[1], item[0]))
    return result


def forget_removed_sources(state: dict, active_source_ids: set[str]) -> int:
    """sources.yml から消えたソースの記録を捨て、捨てたソース数を返す。

    これが無いと、設定から外したソースが永久にダイジェストの死活警告に
    出続け、警告欄そのものが読まれなくなる。
    """
    dropped = set()
    for key in ("failures", "latest"):
        stale = [sid for sid in state[key] if sid not in active_source_ids]
        for source_id in stale:
            del state[key][source_id]
            dropped.add(source_id)
    return len(dropped)


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
