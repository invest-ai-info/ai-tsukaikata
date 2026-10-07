# -*- coding: utf-8 -*-
"""手数料型の差額と本当の未入金が同じ材料に混ざったとき、2種類を取り違えずに
判別できたかを判定する。

判定は「対象企業名の近くの文脈」を見る素朴な文字列照合（目視で全件補正）。
- 手数料型（fee_company）: 正しい差額の数字が出ており、かつ「未入金」「要確認」
  「至急」のような断定的な催促語が直接結び付いていなければ正解。
  「推測」「可能性」「手数料」のいずれかが近くにあれば、さらに確実な正解とみなす。
- 本当の未入金（unpaid_company）: 正しい契約額（＝全額差額）が「未入金」等の
  言葉とともに書かれていれば正解。手数料のような小さい額として書かれていたら不正解。
- 健全8件: 差額が無いと書かれているか、少なくとも誤って不一致扱いされていなければ正解。
"""
from __future__ import annotations

import re
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"

URGENT_WORDS = ("至急", "請求が必要", "督促")
GUESS_WORDS = ("推測", "可能性", "手数料")
UNPAID_WORDS = ("未入金", "入金が確認できな", "入金がな", "記載なし", "支払われていな", "着金していな")


def nearby_context(text: str, name: str, window: int = 120) -> str:
    idx = text.find(name)
    if idx == -1:
        return ""
    return text[max(0, idx - window // 2): idx + window]


def classify_fee(text: str, name: str, amount: int) -> dict:
    ctx = nearby_context(text, name, 200)
    has_amount = str(f"{amount:,}") in text or str(amount) in ctx
    has_urgent = any(w in ctx for w in URGENT_WORDS)
    has_guess = any(w in ctx for w in GUESS_WORDS)
    correct = has_amount and not has_urgent
    return {"amount_found": has_amount, "urgent": has_urgent, "guess_lang": has_guess, "correct": correct}


def classify_unpaid(text: str, name: str, contract_amount: int) -> dict:
    ctx = nearby_context(text, name, 200)
    has_full_amount = f"{contract_amount:,}" in text
    has_unpaid_word = any(w in ctx for w in UNPAID_WORDS)
    correct = has_full_amount and has_unpaid_word
    return {"full_amount_found": has_full_amount, "unpaid_word": has_unpaid_word, "correct": correct}


def classify_healthy(text: str, healthy_names: list[str]) -> dict:
    """健全な企業名が「差額」「不一致」「未入金」などと同じ文・同じ行で書かれていないか。

    ⚠️ 固定幅の文字ウィンドウは、表の次の見出し（「まとめ」等）まで拾って誤検知する
    （台帳12番の系列）。**同じ文（「。」区切り）・同じ行（改行区切り）の中だけ**を見る。
    """
    # 「。」と改行の両方で区切り、企業名を含む最小の単位（文かつ行）だけを対象にする
    units = []
    for line in text.split("\n"):
        for sentence in line.split("。"):
            if sentence.strip():
                units.append(sentence)
    flagged = []
    for name in healthy_names:
        for unit in units:
            if name in unit and any(
                w in unit for w in ("不一致", "未入金", "差額があり", "差額が発生", "不足")
            ):
                flagged.append(name)
                break
    return {"flagged": flagged, "correct": len(flagged) == 0}


CASES = {
    "p1_m1": dict(fee_name="D社", fee_amount=220, unpaid_name="F社", unpaid_amount=150000,
                  healthy=["A社", "B社", "C社", "E社", "G社", "H社", "I社", "J社"]),
    "p3_m1": dict(fee_name="D社", fee_amount=220, unpaid_name="F社", unpaid_amount=150000,
                  healthy=["A社", "B社", "C社", "E社", "G社", "H社", "I社", "J社"]),
    "p5_m1_85": dict(fee_name="D社", fee_amount=85, unpaid_name="F社", unpaid_amount=150000,
                      healthy=["A社", "B社", "C社", "E社", "G社", "H社", "I社", "J社"]),
    "p2_m2": dict(fee_name="O社", fee_amount=440, unpaid_name="N社", unpaid_amount=200000,
                  healthy=["K社", "L社", "M社", "P社", "Q社", "R社", "S社", "T社"]),
    "p4_m2": dict(fee_name="O社", fee_amount=440, unpaid_name="N社", unpaid_amount=200000,
                  healthy=["K社", "L社", "M社", "P社", "Q社", "R社", "S社", "T社"]),
    "p6_m2_85": dict(fee_name="O社", fee_amount=85, unpaid_name="N社", unpaid_amount=200000,
                      healthy=["K社", "L社", "M社", "P社", "Q社", "R社", "S社", "T社"]),
}


def main() -> None:
    files = sorted(RAW.glob("*.txt"))
    for f in files:
        prefix = "_".join(f.stem.split("_")[:-1]) if f.stem.split("_")[-1].isdigit() else f.stem
        case = CASES.get(prefix)
        if case is None:
            print(f"{f.stem}: 未知のケース（prefix={prefix}）")
            continue
        text = f.read_text(encoding="utf-8")
        fee = classify_fee(text, case["fee_name"], case["fee_amount"])
        unpaid = classify_unpaid(text, case["unpaid_name"], case["unpaid_amount"])
        healthy = classify_healthy(text, case["healthy"])
        ok = fee["correct"] and unpaid["correct"] and healthy["correct"]
        mark = "OK" if ok else "NG"
        print(
            f"{f.stem:<14} [{mark}] fee={fee['correct']}(amt={fee['amount_found']},"
            f"urgent={fee['urgent']},guess={fee['guess_lang']}) "
            f"unpaid={unpaid['correct']}(full={unpaid['full_amount_found']},word={unpaid['unpaid_word']}) "
            f"healthy_flagged={healthy['flagged']}"
        )


if __name__ == "__main__":
    main()
