# -*- coding: utf-8 -*-
"""書いた記事が読めるかを数える。書いた直後に自分で回す道具。

    python tools/check_readability.py content/recipes/foo.md   # 書いた記事を見る
    python tools/check_readability.py --recent 14              # 直近14日の記事
    python tools/check_readability.py --all                    # 全部（順位つき）

**なぜ要るか**＝2026-09-22 にオーナーから「タイトルも文章も分かりづらい」。
測ったら、1文の平均が 28.3字（8月上旬の20本）から **44.7字**（9月下旬の20本）へ、
60字以上の文が 2% → **21%** に伸びていた。🔑 **原因は「誠実さ」のほう**で、
試行回数と条件を省かずに書いた結果、実測の条件が1文に流れ込んでいる。

🚨 **直し方は「分ける」より「箇条書きにする」ことが多い。**
文化審議会建議「公用文作成の考え方」Ⅲ-3 ウ＝「三つ以上の情報を並べるときには、
箇条書を利用する」。オーナーの「リスト・表・図を多く」とも同じ方向。

⚠️ **ビルドとは別物。**ビルド（`src/validate.py`）が止めるのは
「追えない1文」（120字以上）だけ。この道具は**記事全体の読みにくさ**を見る。
ここで赤くてもサイトは出る。出るからこそ、書いた本人が見る。
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import readability as R  # noqa: E402
from src.content import parse_article  # noqa: E402

CONTENT = ROOT / "content"
# 1件ずつ直せるように、長い順に出す上限。全部要るときは --all で数字を見る
SHOW = 8


def _articles(paths):
    for path in paths:
        text = path.read_text(encoding="utf-8")
        yield parse_article(path, text)


def _collect(argv) -> list[Path]:
    if "--all" in argv:
        return sorted(p for p in CONTENT.rglob("*.md") if not p.name.startswith("_"))
    if "--recent" in argv:
        days = int(argv[argv.index("--recent") + 1])
        limit = date.today() - timedelta(days=days)
        out = []
        for path in CONTENT.rglob("*.md"):
            if path.name.startswith("_"):
                continue
            if parse_article(path, path.read_text(encoding="utf-8")).published >= limit:
                out.append(path)
        return sorted(out)
    return [Path(a) for a in argv if not a.startswith("-")]


def report(article) -> tuple[list[str], bool]:
    """1本ぶんの行と、直すべきものがあったか。"""
    s = R.stats(article.body_html)
    if not s["count"]:
        return [f"{article.source_path}: 地の文がありません（図と表だけ？）"], False

    over = R.long_sentences(article.body_html, R.SENTENCE_MAX)
    warn = R.long_sentences(article.body_html, R.SENTENCE_WARN)
    bad = bool(over) or s["long_ratio"] > R.LONG_RATIO_MAX

    mark = "🚩" if bad else "✅"
    lines = [
        f"{mark} {article.source_path}",
        f"   文{s['count']}  平均{s['mean']:.0f}字  "
        f"{R.SENTENCE_WARN}字以上 {s['long_ratio'] * 100:.0f}%"
        f"（目安 {R.LONG_RATIO_MAX * 100:.0f}%以下）  最長{s['max']}字",
    ]
    if over:
        lines.append(f"   🚨 {R.SENTENCE_MAX}字以上（ビルドが止まります）: {len(over)}文")
    for sentence in warn[:SHOW]:
        lines.append(f"   [{len(sentence):>3}字] {sentence[:70]}…")
    if len(warn) > SHOW:
        lines.append(f"   （ほか {len(warn) - SHOW}文）")
    return lines, bad


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    paths = _collect(argv)
    if not paths:
        print(__doc__)
        return 0

    articles = sorted(_articles(paths), key=lambda a: -R.stats(a.body_html)["long_ratio"])
    bad_count = 0
    for article in articles:
        lines, bad = report(article)
        bad_count += bad
        print("\n".join(lines))

    print(f"\n{len(articles)}本を見て、直すとよいものが {bad_count}本ありました。")
    if bad_count:
        print("🔑 長い文は、分けるより**箇条書きにする**と直ることが多い"
              "（三つ以上を並べている文がたいていの犯人）。")
    return 1 if bad_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
