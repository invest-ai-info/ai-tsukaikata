# -*- coding: utf-8 -*-
"""材料A/B × パターンa/b/c × 3回ぶんの生の返りを機械判定する。

- 残存した禁止語の件数（13語のうち何件が本文に残っているか）
- 文末の重複（「。」区切りの各文の末尾表現を分類し、最頻の表現が何回連続・何回出たか）
"""
from __future__ import annotations

import re
from pathlib import Path

from material import BANNED, MATERIAL_A, MATERIAL_B

RAW = Path(__file__).resolve().parent / "raw"

ENDING_PATTERNS = [
    "でしょう", "ません", "ください", "きます", "ります", "います",
    "ます", "です", "した", "ある", "いる",
]


def classify_ending(sentence: str) -> str:
    s = sentence.strip()
    for pat in ENDING_PATTERNS:
        if s.endswith(pat):
            return pat
    return s[-2:] if len(s) >= 2 else s


def sentence_ending_stats(text: str) -> dict:
    sentences = [s for s in re.split(r"[。\n]", text) if s.strip()]
    if not sentences:
        return {"n": 0, "max_run": 0, "max_count": 0, "top_ending": None}
    endings = [classify_ending(s) for s in sentences]
    # 最長の連続反復（同じ語尾が連続して何回続くか）
    max_run, run = 1, 1
    for i in range(1, len(endings)):
        if endings[i] == endings[i - 1]:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1
    from collections import Counter
    counts = Counter(endings)
    top_ending, top_count = counts.most_common(1)[0]
    return {
        "n": len(sentences),
        "max_run": max_run,
        "top_ending": top_ending,
        "top_count": top_count,
    }


def banned_count(text: str) -> dict:
    hits = {w: text.count(w) for w in BANNED if text.count(w) > 0}
    return {"total": sum(hits.values()), "distinct": len(hits), "hits": hits}


def strip_meta_commentary(text: str) -> str:
    """一部の回（パターンaの3回）は、書き直した本文の後ろに
    「直したポイント」という自己解説を `---` 区切りで付け足す。
    解説の中で禁止語そのものを引用するため、本文だけを見て判定する。
    """
    return text.split("\n---\n")[0]


def main() -> None:
    files = sorted(RAW.glob("*.txt"))
    print(f"{'file':<12} {'残存禁止語(件/種)':<16} {'文数':<5} {'最長連続語尾':<10} {'最頻語尾(回数)'}")
    for f in files:
        raw_text = f.read_text(encoding="utf-8")
        text = strip_meta_commentary(raw_text)
        had_meta = text != raw_text
        bc = banned_count(text)
        es = sentence_ending_stats(text)
        meta = "（自己解説あり・本文から除外）" if had_meta else ""
        print(
            f"{f.stem:<12} {bc['total']}件/{bc['distinct']}種{'':<6} "
            f"{es['n']:<5} {es['max_run']:<10} "
            f"{es['top_ending']}×{es['top_count']}{meta}"
        )
        if bc["hits"]:
            print(f"    残存語（本文のみ）: {bc['hits']}")


if __name__ == "__main__":
    main()
