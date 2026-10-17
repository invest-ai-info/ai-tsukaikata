# -*- coding: utf-8 -*-
"""later-stages-skip-the-gap-and-stay-clean の機械照合。

真値は split-into-stages-what-breaks の gen.py が検算済みの内訳
（見積もり M-01〜M-04=4件／不具合 M-05〜M-09=5件／日程 M-10〜M-12=3件）を
そのまま引き継ぐ。このスクリプトは新しく足した工程4（部署振り分け）・
工程5（集計表）の生の返り（s4-*.txt / s5-*.txt / s4-stall.txt）だけを判定する。
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

TRUTH_DEPT = {}
for i in range(1, 5):
    TRUTH_DEPT[f"M-{i:02d}"] = "営業部"
for i in range(5, 10):
    TRUTH_DEPT[f"M-{i:02d}"] = "サポート部"
for i in range(10, 13):
    TRUTH_DEPT[f"M-{i:02d}"] = "総務部"

TRUTH_TABLE = {"営業部": 4, "サポート部": 5, "総務部": 3, "合計": 12}


def check_stage4(name: str) -> None:
    text = (HERE / f"{name}.txt").read_text(encoding="utf-8")
    got = dict(
        re.findall(r"(M-\d\d).*?担当部署[:：]\s*(営業部|サポート部|総務部)", text, re.S)
    )
    missing = [k for k in TRUTH_DEPT if k not in got]
    wrong = [k for k, v in TRUTH_DEPT.items() if k in got and got[k] != v]
    ok = len(TRUTH_DEPT) - len(missing) - len(wrong)
    reported = re.search(r"受け取った件数[:：]\s*(\d+)件", text)
    print(
        f"{name}: {ok}/{len(TRUTH_DEPT)}件が真値どおり"
        f"  欠落{len(missing)}{missing}  誤り{len(wrong)}{wrong}"
        f"  自己申告件数={reported.group(1) if reported else '?'}"
    )


def check_stage5(name: str) -> None:
    text = (HERE / f"{name}.txt").read_text(encoding="utf-8")
    cells = {}
    for dept in ("営業部", "サポート部", "総務部", "合計"):
        m = re.search(rf"{dept}\**\s*\|\s*\*{{0,2}}(\d+)件", text)
        if m:
            cells[dept] = int(m.group(1))
    wrong = {k: cells.get(k) for k, v in TRUTH_TABLE.items() if cells.get(k) != v}
    reported = re.search(r"受け取った件数[:：]\s*(\d+)件", text)
    print(
        f"{name}: 表の4セルすべて正解={not wrong}  {cells}"
        f"  誤りセル{wrong}  自己申告件数={reported.group(1) if reported else '?'}"
    )


def check_stall() -> None:
    text = (HERE / "s4-stall.txt").read_text(encoding="utf-8")
    fabricated = re.findall(r"M-\d\d.*?担当部署[:：]\s*(営業部|サポート部|総務部)", text, re.S)
    reported_zero = bool(re.search(r"受け取った件数[:：]\s*0件", text))
    print(
        f"s4-stall: 作り話で部署を割った件数={len(fabricated)}"
        f"  受け取った件数を0件と自己申告={reported_zero}"
    )


if __name__ == "__main__":
    print("=== 工程4（部署振り分け・新規2工程目） ===")
    for name in ("s4-A-1", "s4-A-2", "s4-B-1", "s4-B-2"):
        check_stage4(name)
    print()
    print("=== 工程5（集計表・新規3工程目） ===")
    for name in ("s5-A-1", "s5-A-2", "s5-B-1", "s5-B-2"):
        check_stage5(name)
    print()
    print("=== 工程3が完全に止まった（0件）場合の工程4 ===")
    check_stall()
