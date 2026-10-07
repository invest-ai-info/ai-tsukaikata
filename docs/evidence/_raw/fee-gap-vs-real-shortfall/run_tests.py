# -*- coding: utf-8 -*-
"""材料1・2（通常版・85円版）に、推測指示あり/なしの指示文を送って生の返りを保存する。

実行: python3 run_tests.py
各回を独立した `claude --print --safe-mode --tools ""` プロセスとして呼ぶ。
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from material import (
    MATERIAL1, MATERIAL2, MATERIAL1_85, MATERIAL2_85, render,
)

PERSONA = (
    "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。"
    "ユーザーの依頼に文章だけで答えてください。"
)

PROMPT_WITH_GUESS = (
    "入金明細と契約一覧を突き合わせて、差額がある契約を挙げてください。"
    "差額が振込手数料の可能性がある場合はその旨を推測として書いてください。"
)
PROMPT_NO_GUESS = (
    "入金明細と契約一覧を突き合わせて、差額がある契約を挙げてください。"
)

JOBS = [
    # (key, prompt, rows, label_contract, label_deposit, rounds)
    ("p1_m1", PROMPT_WITH_GUESS, MATERIAL1, "契約一覧（デザイン制作・月額）", "入金明細（当月）", 5),
    ("p2_m2", PROMPT_WITH_GUESS, MATERIAL2, "契約一覧（翻訳・月額）", "入金明細（当月）", 5),
    ("p3_m1", PROMPT_NO_GUESS, MATERIAL1, "契約一覧（デザイン制作・月額）", "入金明細（当月）", 3),
    ("p4_m2", PROMPT_NO_GUESS, MATERIAL2, "契約一覧（翻訳・月額）", "入金明細（当月）", 3),
    ("p5_m1_85", PROMPT_WITH_GUESS, MATERIAL1_85, "契約一覧（デザイン制作・月額）", "入金明細（当月）", 3),
    ("p6_m2_85", PROMPT_WITH_GUESS, MATERIAL2_85, "契約一覧（翻訳・月額）", "入金明細（当月）", 3),
]

OUT = Path(__file__).resolve().parent / "raw"


def call_claude(prompt: str, material_text: str) -> str:
    full = f"{prompt}\n\n{material_text}"
    result = subprocess.run(
        [
            "claude", "--print", "--safe-mode", "--tools", "",
            "--append-system-prompt", PERSONA,
            full,
        ],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude failed: {result.returncode}\n{result.stderr}")
    return result.stdout.strip()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for key, prompt, rows, lc, ld, rounds in JOBS:
        material_text = render(rows, lc, ld)
        for round_no in range(1, rounds + 1):
            fname = OUT / f"{key}_{round_no}.txt"
            if fname.exists():
                print(f"skip {fname.name} (exists)")
                continue
            print(f"running {fname.name} ...", file=sys.stderr)
            t0 = time.time()
            try:
                out = call_claude(prompt, material_text)
            except Exception as exc:  # noqa: BLE001
                print(f"  FAILED: {exc}", file=sys.stderr)
                continue
            fname.write_text(out, encoding="utf-8")
            print(f"  done in {time.time()-t0:.1f}s ({len(out)}字)", file=sys.stderr)


if __name__ == "__main__":
    main()
