# -*- coding: utf-8 -*-
"""終わった在庫を archive ファイルへ逐語で移す機械回転（LLM不要）。

設計 = docs/superpowers/specs/2026-08-20-token-diet-design.md
動機 = キューの78%が済んだ項目で、毎晩3〜4担当がそれを読み直していた。

原則:
  - 生きているファイルのパスは変えない（クラウド側プロンプトの修正が不要）
  - 逐語で移す。要約・言い換えはしない（機械にできるのはそれだけ。数値を扱わない）
  - マーカー行（`- [x] 題` / `- [x] URL`）は残す＝重複防止が読むのはこの行
    （tracker.deepdive.queued_urls / ネタ探しの題での突き合わせ）
  - _deepdive_queue の `- [!]` は移さない＝経路遮断の再試行対象（CLAUDE.md の設計）
  - _earn_research は直近3日を残す＝heartbeat（48時間）が最新日付を読める
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

NOTE_PREFIX = "→保管"
_SLUG_RE = re.compile(r"公開: `([^`]+)`")
_DATE_HEAD_RE = re.compile(r"^(?:[#\s]*)(?:🚨\s*)?(\d{4})-(\d{2})-(\d{2})")
KEEP_DAYS = 3
EXEMPT_WORD = "申し送り"
QUEUE_START = "## 待ち行列"


def _item_note(detail_lines: list[str]) -> str:
    """索引1行。slug があれば slug、無ければ詳細の1行目を切り出す（要約しない）。"""
    joined = "\n".join(detail_lines)
    m = _SLUG_RE.search(joined)
    if m:
        return f"  - {NOTE_PREFIX}: 公開: `{m.group(1)}`"
    first = detail_lines[0].strip().lstrip("- ").strip()
    return f"  - {NOTE_PREFIX}: {first[:60]}"


def rotate_queue(text: str, markers: tuple[str, ...]) -> tuple[str, list[str]]:
    """`## 待ち行列` 以降の済んだ項目の詳細を archive へ。マーカー行は残す。"""
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(QUEUE_START))
    except StopIteration:
        return text, []

    out = lines[: start + 1]
    chunks: list[str] = []
    i = start + 1
    while i < len(lines):
        line = lines[i]
        if any(line.startswith(m) for m in markers):
            # 詳細ブロック＝続く字下げ行（間の空行は、次に字下げ行が来るなら中身）
            j = i + 1
            while j < len(lines):
                if lines[j].startswith((" ", "\t")):
                    j += 1
                elif lines[j] == "" and j + 1 < len(lines) and lines[j + 1].startswith((" ", "\t")):
                    j += 1
                else:
                    break
            details = lines[i + 1 : j]
            has_body = any(l.strip() for l in details)
            already = details and details[0].strip().startswith(f"- {NOTE_PREFIX}")
            if has_body and not already:
                chunks.append("\n".join([line, *details]) + "\n")
                out.append(line)
                out.append(_item_note([l for l in details if l.strip()]))
                i = j
                continue
        out.append(line)
        i += 1
    new = "\n".join(out) + ("\n" if text.endswith("\n") else "")
    return new, chunks


def _section_date(heading: str) -> date | None:
    m = _DATE_HEAD_RE.match(heading)
    if not m:
        return None
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def rotate_daily_log(
    text: str,
    heading_prefix: str,
    keep: int = KEEP_DAYS,
    exempt_word: str = EXEMPT_WORD,
) -> tuple[str, list[str]]:
    """日付で始まる節のうち、新しい `keep` 日ぶんを残して archive へ。

    - 日付で始まらない見出し（指示節）は触らない
    - 見出しに exempt_word を含む節（申し送り）は年齢に関わらず残す＝閉じるのは人
    - 同じ日付の節（「（夜）」等）は同じ日として一緒に残り、一緒に動く
    """
    lines = text.splitlines()
    # 節の切れ目＝同格以上の見出し。h3 の節は h2 でも切れる
    def is_boundary(l: str) -> bool:
        if l.startswith(heading_prefix):
            return True
        return heading_prefix == "### " and l.startswith("## ")

    sections: list[tuple[int, int, date | None, bool]] = []  # start, end, date, exempt
    starts = [i for i, l in enumerate(lines) if l.startswith(heading_prefix)]
    for s in starts:
        head = lines[s][len(heading_prefix):]
        d = _section_date(head)
        if d is None:
            continue
        e = s + 1
        while e < len(lines) and not is_boundary(lines[e]):
            e += 1
        sections.append((s, e, d, exempt_word in head))

    dated = sorted({d for _, _, d, ex in sections if not ex}, reverse=True)
    keep_dates = set(dated[:keep])
    victims = [(s, e) for s, e, d, ex in sections if not ex and d not in keep_dates]
    if not victims:
        return text, []

    chunks = []
    out = []
    skip_until = -1
    victim_map = dict(victims)
    for i, line in enumerate(lines):
        if i < skip_until:
            continue
        if i in victim_map:
            e = victim_map[i]
            chunks.append("\n".join(lines[i:e]).rstrip("\n") + "\n")
            head = lines[i][len(heading_prefix):]
            out.append(f"- {NOTE_PREFIX}: {head}")
            out.append("")
            skip_until = e
            continue
        out.append(line)
    new = "\n".join(out) + ("\n" if text.endswith("\n") else "")
    return new, chunks


ARCHIVE_HEADER = (
    "# {name} の保管庫\n"
    "\n"
    "`tools/rotate_archives.py` が済んだ在庫を逐語で移す先（追記専用・担当は読まない）。\n"
    "真の保管庫は git 履歴。設計＝docs/superpowers/specs/2026-08-20-token-diet-design.md\n"
)


def append_archive(existing: str | None, chunks: list[str], today: date, name: str) -> str:
    base = existing if existing is not None else ARCHIVE_HEADER.format(name=name)
    body = "\n".join(c.rstrip("\n") for c in chunks)
    return f"{base.rstrip()}\n\n## {today.isoformat()} 回転\n\n{body}\n"


# (live ファイル, 回転の種類, 引数)
TARGETS = [
    ("content/_recipe_queue.md", "queue", {"markers": ("- [x] ", "- [!] ")}),
    ("content/_deepdive_queue.md", "queue", {"markers": ("- [x] ",)}),
    ("content/_topic_ideas.md", "log", {"heading_prefix": "## "}),
    ("content/_review_log.md", "log", {"heading_prefix": "## "}),
    ("content/_earn_research.md", "log", {"heading_prefix": "### "}),
]


def rotate_all(root: Path, today: date) -> dict[str, int]:
    """対象5ファイルを回転し、{live相対パス: 移した塊の数} を返す（0件は載せない）。"""
    summary: dict[str, int] = {}
    for rel, kind, kwargs in TARGETS:
        live = root / rel
        if not live.exists():
            continue
        text = live.read_text(encoding="utf-8")
        if kind == "queue":
            new, chunks = rotate_queue(text, **kwargs)
        else:
            new, chunks = rotate_daily_log(text, **kwargs)
        if not chunks:
            continue
        archive = live.with_name(live.stem + "_archive.md")
        old = archive.read_text(encoding="utf-8") if archive.exists() else None
        archive.write_text(
            append_archive(old, chunks, today, live.stem.lstrip("_")),
            encoding="utf-8", newline="\n",
        )
        live.write_text(new, encoding="utf-8", newline="\n")
        summary[rel] = len(chunks)
    return summary


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    today = datetime.now(timezone(timedelta(hours=9))).date()  # JST
    summary = rotate_all(root, today)
    if not summary:
        print("回転するものはありませんでした")
        return 0
    for rel, n in summary.items():
        print(f"{rel}: {n}塊を保管庫へ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
