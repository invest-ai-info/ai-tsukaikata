# -*- coding: utf-8 -*-
"""材料A・Bに、3パターン(a/b/c)の指示文を各3回ずつ送って生の返りを保存する。

実行: python3 run_tests.py
各回を独立した `claude --print --safe-mode --tools ""` プロセスとして呼ぶ
（このリポジトリ・この会話の文脈を一切引き継がない。人格は --append-system-prompt で固定）。
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from material import MATERIAL_A, MATERIAL_B

PERSONA = (
    "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。"
    "ユーザーの依頼に文章だけで答えてください。"
)

PROMPT_A = "次の文章を、AIが書いたような文章ではなく人間らしい文章に書き直してください。"

BANNED_LIST_TEXT = (
    "と言えるでしょう／いかがでしたか／要するに／つまり／することができます／"
    "かもしれません／ぜひ／と言っても過言ではありません／さまざまな／"
    "について解説します／となっています／このように／していきましょう"
)

PROMPT_B = (
    "次の文章を、AIが書いたような文章ではなく人間らしい文章に書き直してください。"
    f"次の語句は使わないでください：{BANNED_LIST_TEXT}"
)

PROMPT_C = (
    "次の文章を、AIが書いたような文章ではなく人間らしい文章に書き直してください。"
    f"次の語句は使わないでください：{BANNED_LIST_TEXT}"
    "さらに、同じ文末表現（「〜でしょう」「〜ます」など）を3回以上連続で使わないでください。"
)

PATTERNS = {"a": PROMPT_A, "b": PROMPT_B, "c": PROMPT_C}
MATERIALS = {"A": MATERIAL_A, "B": MATERIAL_B}
ROUNDS = 3

OUT = Path(__file__).resolve().parent / "raw"


def call_claude(prompt: str, material: str) -> str:
    full = f"{prompt}\n\n{material}"
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
    for pat_key, prompt in PATTERNS.items():
        for mat_key, material in MATERIALS.items():
            for round_no in range(1, ROUNDS + 1):
                fname = OUT / f"{pat_key}_{mat_key}_{round_no}.txt"
                if fname.exists():
                    print(f"skip {fname.name} (exists)")
                    continue
                print(f"running {fname.name} ...", file=sys.stderr)
                t0 = time.time()
                try:
                    out = call_claude(prompt, material)
                except Exception as exc:  # noqa: BLE001
                    print(f"  FAILED: {exc}", file=sys.stderr)
                    continue
                fname.write_text(out, encoding="utf-8")
                print(f"  done in {time.time()-t0:.1f}s ({len(out)}字)", file=sys.stderr)


if __name__ == "__main__":
    main()
