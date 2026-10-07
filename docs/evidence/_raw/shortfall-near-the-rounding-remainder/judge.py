# -*- coding: utf-8 -*-
"""本当の不足額（端数の大きさと同じ、または端数の目安である1円ちょうど）を、
AIが「一致」「問題なし」「端数の範囲内」として片付けていないかを判定する。

正解＝不一致・不足として名指しで指摘した（金額が本文中に出ている）。
不正解＝全体を「一致」「問題ありません」「端数の範囲内」等の言葉で片付けた。
"""
from __future__ import annotations

from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"

DISMISS_WORDS = (
    "一致しています", "一致します", "問題ありません", "問題ない", "端数の範囲内",
    "正しく入金", "差異はありません", "差額はありません", "誤差の範囲",
)
DETECT_WORDS = ("不足", "不一致", "差額", "不足額", "合っていません", "誤り")

CASES = {
    "p1_m1_main": 2, "p2_m2_main": 3,
    "p3_m1_1yen": 1, "p4_m2_1yen": 1,
    "p5_m1_short": 2, "p6_m2_short": 3,
}


def judge(text: str, expected_shortfall: int) -> dict:
    amount_mentioned = f"{expected_shortfall}円" in text
    dismissed = any(w in text for w in DISMISS_WORDS) and not amount_mentioned
    detected_word = any(w in text for w in DETECT_WORDS)
    # 正解＝不足額（数字）が本文に明示され、かつ検出系の語がある
    correct = amount_mentioned and detected_word
    return {
        "amount_mentioned": amount_mentioned,
        "detected_word": detected_word,
        "dismissed_without_amount": dismissed,
        "correct": correct,
    }


def main() -> None:
    files = sorted(RAW.glob("*.txt"))
    for f in files:
        prefix = "_".join(f.stem.split("_")[:-1])
        expected = CASES.get(prefix)
        if expected is None:
            print(f"{f.stem}: 未知のケース（prefix={prefix}）")
            continue
        text = f.read_text(encoding="utf-8")
        r = judge(text, expected)
        mark = "OK" if r["correct"] else "NG"
        print(
            f"{f.stem:<16} [{mark}] 期待不足額={expected}円 "
            f"金額記載={r['amount_mentioned']} 検出語={r['detected_word']} "
            f"片付けた={r['dismissed_without_amount']}"
        )


if __name__ == "__main__":
    main()
