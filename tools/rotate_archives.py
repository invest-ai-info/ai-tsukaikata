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
QUEUE_DONE = "## 処理済み"

# 🚨 待ち行列の中の「散文」も回転の対象にする（2026-09-22 追加）。
#
# 実測: `_recipe_queue.md` の待ち行列 2,009行のうち **920行が散文**（項目でも索引でもない）で、
# 中身は `_earn_research.md`・`_writer_log.md`・`_hypothesis_queue.md` と重複していた。
# 毎晩3〜4担当がこれを読み直していた＝トークン食の設計が狙った「死んだテキスト」そのもの。
#
# ⚠️ **許可リスト方式**＝下の見出しだけを対象にする。場面の節（副業・詐欺を防ぐ等）の決まりや、
#    新しい種類の見出しを巻き込まないため。
# ⚠️ **未処理（`- [ ]`）が1件でも残る節の散文は動かさない**＝並び順の指示など、まだ効く指示が
#    混ざる（実測: 「下の4件はこの順に書くこと」）。
PROSE_HEADINGS = ("補充", "研究パック")  # 日付つきの補充・研究パック＝その日の経緯
LOG_HEADINGS = (  # 担当の日誌。項目が無ければ節ごと移す（中身は各担当の作業ログと重複）
    "詰まったところ", "仮説キューの在庫補充", "源ごとの結果", "バックログの整理", "見送ったもの",
)
_HEAD_RE = re.compile(r"^(#{3,6}) *(.*)$")


def _head_kind(heading: str) -> str | None:
    """見出しの種類。'prose'＝経緯だけ移す / 'log'＝節ごと移す / None＝触らない。"""
    m = _HEAD_RE.match(heading)
    if not m:
        return None
    title = m.group(2).lstrip("🚨✅🛑📚🔑⚠️ ").strip()
    if title.startswith(LOG_HEADINGS):
        return "log"
    if title.startswith(PROSE_HEADINGS):
        return "prose"
    if _DATE_HEAD_RE.match(title):  # `### 2026-09-22 15:30 稼ぎ方研究担当` のような日誌
        return "log"
    if heading.startswith("#####"):  # 節の中の出来事の報告（🛑 書けなかった・✅ 解決した）
        return "log"
    return None


def _item_note(detail_lines: list[str]) -> str:
    """索引1行。slug があれば slug、無ければ詳細の1行目を切り出す（要約しない）。

    担当が自分で `→保管:` から書き始めていた行は、その接頭辞を剥がしてから切り出す
    （剥がさないと `→保管: →保管: …` になる）。
    """
    joined = "\n".join(detail_lines)
    m = _SLUG_RE.search(joined)
    if m:
        return f"  - {NOTE_PREFIX}: 公開: `{m.group(1)}`"
    first = detail_lines[0].strip().lstrip("- ").strip()
    if first.startswith(NOTE_PREFIX):
        first = first[len(NOTE_PREFIX):].lstrip(":： ").strip()
    return f"  - {NOTE_PREFIX}: {first[:60]}"


def rotate_queue(
    text: str, markers: tuple[str, ...], prose: bool = False
) -> tuple[str, list[str]]:
    """`## 待ち行列` 以降の済んだ項目の詳細を archive へ。マーカー行は残す。

    prose=True なら、済んだ節の散文（補充の経緯・担当の日誌）と `## 処理済み` の
    古い日報も移す（PROSE_HEADINGS のコメント参照）。既定は False ＝従来どおり。
    """
    if prose:
        text, prose_chunks = _rotate_prose(text)
    else:
        prose_chunks = []
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(QUEUE_START))
    except StopIteration:
        return text, prose_chunks

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
            body = [l for l in details if l.strip()]
            # 「回転済み」＝索引行1本だけ。担当が自分で `→保管:` を書き、その下に長い報告を
            # 続けた項目は回転済みではない（2026-09-22 実測: `_recipe_queue.md` の済んだ項目
            # 158件中66件・約2,300行がこの形ですり抜け、予算2500行に対して4594行になっていた）
            already = len(body) == 1 and body[0].strip().startswith(f"- {NOTE_PREFIX}")
            if body and not already:
                chunks.append("\n".join([line, *details]) + "\n")
                out.append(line)
                out.append(_item_note(body))
                i = j
                continue
        out.append(line)
        i += 1
    new = "\n".join(out) + ("\n" if text.endswith("\n") else "")
    return new, prose_chunks + chunks


def _rotate_prose(text: str) -> tuple[str, list[str]]:
    """待ち行列の散文と、`## 処理済み` の古い日報を archive へ。項目には触らない。"""
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(QUEUE_START))
    except StopIteration:
        return text, []
    done_at = next(
        (i for i, l in enumerate(lines) if l.startswith(QUEUE_DONE)), len(lines)
    )

    heads = [i for i in range(start, done_at) if _HEAD_RE.match(lines[i])]
    drop: set[int] = set()
    notes: dict[int, str] = {}  # 節ごと移したときに跡地へ置く索引行
    chunks: list[str] = []
    for k, i in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else done_at
        kind = _head_kind(lines[i])
        if kind is None:
            continue
        body = range(i + 1, end)
        items = [x for x in body if lines[x].startswith("- [")]
        if kind == "log" and not items:
            if any(lines[x].strip() for x in body):
                chunks.append("\n".join(lines[i:end]).rstrip("\n") + "\n")
                drop.update(body)
                drop.add(i)
                notes[i] = f"- {NOTE_PREFIX}: {_HEAD_RE.match(lines[i]).group(2)}"
            continue
        if any(lines[x].startswith("- [ ] ") for x in body):
            continue  # まだ効く指示が混ざる
        # ⚠️ 索引行（`- →保管: …`）は散文ではない。担当が自分で残したものもあるので、
        #    ここで拾うと2回目の回転で跡形ごと吸い込まれる（＝回転が非冪等になる）。
        prose = [
            x for x in body
            if lines[x].strip()
            and not lines[x].startswith((" ", "\t", "- [", f"- {NOTE_PREFIX}"))
        ]
        if not prose:
            continue
        chunks.append(lines[i] + "\n\n" + "\n".join(lines[x] for x in prose) + "\n")
        drop.update(prose)

    # `## 処理済み` の日報は直近 KEEP_DAYS 日ぶんを残す（他のログと同じ決まり）
    done_heads = [i for i in range(done_at, len(lines)) if lines[i].startswith("### ")]
    dated = [(i, _section_date(lines[i][4:])) for i in done_heads]
    keep = sorted({d for _, d in dated if d}, reverse=True)[:KEEP_DAYS]
    for k, (i, d) in enumerate(dated):
        if d is None or d in keep:
            continue
        end = done_heads[k + 1] if k + 1 < len(done_heads) else len(lines)
        chunks.append("\n".join(lines[i:end]).rstrip("\n") + "\n")
        drop.update(range(i, end))
        notes[i] = f"- {NOTE_PREFIX}: {lines[i][4:]}"

    if not chunks:
        return text, []
    out = []
    for i, line in enumerate(lines):
        if i in notes:
            out.append(notes[i])
            continue
        if i in drop:
            continue
        if line == "" and out and out[-1] == "":
            continue  # 抜いた跡の空行が重ならないように
        out.append(line)
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
    ("content/_recipe_queue.md", "queue",
     {"markers": ("- [x] ", "- [!] "), "prose": True}),
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
