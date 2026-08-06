# -*- coding: utf-8 -*-
"""major のお知らせを深掘り待ち行列（content/_deepdive_queue.md）へ自動追記する。

キューは人間もスマホから編集する生きたファイルなので、ここでは「行を足す」
以上のことをしない。出典が読めないときに書かずに止まる判断はルーティン側の
仕事で、ここでは選別と追記だけを行う。

歯止めが本体：1日 DAILY_LIMIT 件まで・同じ uid / URL は二度追記しない。
追記しすぎるとキューが読まれなくなり、仕組みごと死ぬため。
"""
from __future__ import annotations

from datetime import datetime

from .models import Update
from .summarize import ANNOUNCEMENT_TYPES

DAILY_LIMIT = 3
DONE_HEADING = "## 処理済み"
_MARKERS = ("- [ ] ", "- [x] ", "- [!] ")


def queued_urls(text: str) -> set[str]:
    """キュー本文に既に並んでいるURL。手動追記との重複を防ぐために見る。"""
    urls = set()
    for line in text.splitlines():
        stripped = line.strip()
        for marker in _MARKERS:
            if stripped.startswith(marker):
                urls.add(stripped[len(marker):].strip())
    return urls


def select_candidates(
    updates: list[Update],
    source_types: dict[str, str],
    *,
    queued_uids: set[str],
    queued_urls_: set[str],
    today_count: int,
    limit: int = DAILY_LIMIT,
) -> list[Update]:
    """自動追記してよい major のお知らせを選ぶ。

    モデル系は選ばない——「出たこと」自体はニュース欄で足りていて、
    深掘りは発表文がある告知にだけ意味があるため。
    """
    picked: list[Update] = []
    for update in updates:
        if today_count + len(picked) >= limit:
            break
        if update.importance != "major":
            continue
        if source_types.get(update.source_id) not in ANNOUNCEMENT_TYPES:
            continue
        if update.uid in queued_uids or update.url in queued_urls_:
            continue
        picked.append(update)
    return picked


def append_lines(text: str, updates: list[Update], now: datetime) -> str:
    """「## 処理済み」の手前（無ければ末尾）に追記した本文を返す。"""
    date = now.date().isoformat()
    block = "".join(
        f"- [ ] {update.url}\n"
        f"  - {date} 自動追記（major・{update.vendor}「{update.title}」）\n"
        for update in updates
    )
    marker = f"\n{DONE_HEADING}"
    if marker in text:
        return text.replace(marker, "\n" + block + marker, 1)
    if not text.endswith("\n"):
        text = text + "\n"
    return text + block
