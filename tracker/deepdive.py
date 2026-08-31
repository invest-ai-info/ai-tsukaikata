# -*- coding: utf-8 -*-
"""major のお知らせを深掘り待ち行列（content/_deepdive_queue.md）へ自動追記する。

キューは人間もスマホから編集する生きたファイルなので、ここでは「行を足す」
以上のことをしない。出典が読めないときに書かずに止まる判断はルーティン側の
仕事で、ここでは選別と追記だけを行う。

歯止めが本体：1日 DAILY_LIMIT 件まで・同じ uid / URL は二度追記しない。
追記しすぎるとキューが読まれなくなり、仕組みごと死ぬため。
"""
from __future__ import annotations

import urllib.parse
from datetime import datetime

from .models import Update
from .summarize import ANNOUNCEMENT_TYPES

DAILY_LIMIT = 3
DONE_HEADING = "## 処理済み"
_MARKERS = ("- [ ] ", "- [x] ", "- [!] ")

# 先方の bot 判定で出典ページが読めないホスト＝深掘りの枠を取らせない（2026-08-31）。
#
# 🚨 これは「読まない」ための一覧ではなく、**読める会社へ枠を回す**ための一覧。
# 枠は1日3件しかないのに、直近5件の自動追記（8/10・8/18・8/21・8/25・8/26）が
# **全部 openai.com** だった＝発表語「Introducing …」にいちばんよく当たるため。
# openai.com の記事ページは cf-mitigated: challenge の403で、2026-08-20 に入れた
# 再試行は設計どおり対象外（何度やっても同じなので、その判断のほうは正しい）。
# 結果、枠を取った時点で捨て札になり、tools/ の自動公開は 2026-08-21 で止まっていた。
#
# ⚠️ 載せてよいのは「**先方の bot 判定**で読めない」と実測して記録に残っているものだけ。
#    経路遮断（CONNECT tunnel failed / EGRESS_BLOCKED）は**載せない**——許可リストに
#    足せば直るので、直った日に自動で復活してほしいから。種類を混ぜると、直ったことに
#    気づけなくなる（CLAUDE.md「遮断には2種類ある」）。
# ⚠️ 推測で足さない。「最近読めない気がする」では足さない。
# ⚠️ サブドメインは含めない。`developers.openai.com` と `platform.openai.com` は200を
#    実測済みで、まとめて締め出すと読める出典まで捨てる。
# 📌 外すとき＝先方の判定が変わって実際に読めた日に、手で消す。自動では戻さない。
UNREADABLE_HOSTS = ("openai.com",)


def is_unreadable(url: str, hosts: tuple[str, ...] = UNREADABLE_HOSTS) -> bool:
    """出典ページが読めないと分かっているホストのURLか（`www.` だけ同じものとして扱う）。"""
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host in hosts


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
    skipped: list[Update] | None = None,
) -> list[Update]:
    """自動追記してよい major のお知らせを選ぶ。

    モデル系は選ばない——「出たこと」自体はニュース欄で足りていて、
    深掘りは発表文がある告知にだけ意味があるため。

    出典が読めないホスト（UNREADABLE_HOSTS）も選ばない。⚠️ **黙って捨てない**＝
    `skipped` を渡すと飛ばしたぶんがそこに入るので、呼び出し側が件数を必ず出すこと。
    枠を静かに削るのが、この仕組みで一番まずい壊れ方（No silent caps）。
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
        if is_unreadable(update.url):
            if skipped is not None:
                skipped.append(update)
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
