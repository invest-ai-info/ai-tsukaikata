# -*- coding: utf-8 -*-
"""材料1・2（不足2円/3円版・1円版）に、明示的/短い指示文を送って生の返りを保存する。

実行: python3 run_tests.py
各回を独立した `claude --print --safe-mode --tools ""` プロセスとして呼ぶ。
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from material import (
    CONTRACT1, CONTRACT2,
    DEPOSITS1_MAIN, DEPOSITS2_MAIN,
    DEPOSITS1_1YEN, DEPOSITS2_1YEN,
    render,
)

PERSONA = (
    "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。"
    "ユーザーの依頼に文章だけで答えてください。"
)

PROMPT_MAIN = "契約書どおりに入金されているか確認してください。"
PROMPT_SHORT = "この入金、何かおかしいところはありますか。"

JOBS = [
    # (key, prompt, contract, deposits, label, rounds)
    ("p1_m1_main", PROMPT_MAIN, CONTRACT1, DEPOSITS1_MAIN, "材料1（端数は最終回）", 5),
    ("p2_m2_main", PROMPT_MAIN, CONTRACT2, DEPOSITS2_MAIN, "材料2（端数は初回）", 5),
    ("p3_m1_1yen", PROMPT_MAIN, CONTRACT1, DEPOSITS1_1YEN, "材料1（端数は最終回）", 3),
    ("p4_m2_1yen", PROMPT_MAIN, CONTRACT2, DEPOSITS2_1YEN, "材料2（端数は初回）", 3),
    ("p5_m1_short", PROMPT_SHORT, CONTRACT1, DEPOSITS1_MAIN, "材料1（端数は最終回）", 3),
    ("p6_m2_short", PROMPT_SHORT, CONTRACT2, DEPOSITS2_MAIN, "材料2（端数は初回）", 3),
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
    for key, prompt, contract, deposits, label, rounds in JOBS:
        material_text = render(contract, deposits, label)
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
