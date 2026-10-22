# -*- coding: utf-8 -*-
MATERIALS = {
    "M1_deshou": {
        "label": "新しいendings「〜でしょう」×4（新人研修の挨拶）",
        "text": (
            "来週から新しい部署に配属されることになりました。初めての業務にはきっと戸惑うことも多いでしょう。"
            "周りの先輩方も最初は同じように苦労されたでしょう。わからないことがあれば、遠慮なく質問するのがよいでしょう。"
            "少しずつ慣れていけば、仕事の流れも見えてくるでしょう。"
        ),
        "ending": "でしょう",
        "run": 4,
    },
    "M2_to_omoimasu": {
        "label": "新しいendings「〜と思います」×4（出張報告の所感）",
        "text": (
            "今回の出張では、新しい取引先との関係を築けたと思います。先方の要望を直接伺えたのは有意義だったと思います。"
            "今後の提案に活かせる情報も得られたと思います。次回はもう少し準備期間を長く取るべきだと思います。"
        ),
        "ending": "と思います",
        "run": 4,
    },
    "M3_nodesu5": {
        "label": "既出「〜のです」×5（清掃当番の引き継ぎメモ）",
        "text": (
            "今月から清掃当番のやり方を少し変更するのです。まず入口付近から掃き始めるのです。"
            "次に机の上を乾いた布で拭くのです。ゴミ袋は毎回新しいものに交換するのです。"
            "最後に換気のため窓を少し開けておくのです。"
        ),
        "ending": "のです",
        "run": 5,
    },
    "M4_kudasai6": {
        "label": "既出「〜ください」×6（忘年会の案内）",
        "text": (
            "忘年会の出欠は今週中に回答してください。会場の変更があれば必ず確認してください。"
            "アレルギーがある方は事前に伝えてください。遅刻する場合は幹事に連絡してください。"
            "会費は当日受付で渡してください。写真撮影が苦手な方は一声かけてください。"
        ),
        "ending": "ください",
        "run": 6,
    },
}

if __name__ == "__main__":
    import re
    for key, m in MATERIALS.items():
        sentences = [s for s in re.split(r"(?<=[。])", m["text"]) if s.strip()]
        print(key, "文数:", len(sentences))
        run = 0
        maxrun = 0
        for s in sentences:
            if s.rstrip("。").endswith(m["ending"]):
                run += 1
                maxrun = max(maxrun, run)
            else:
                run = 0
        print("  最長連続:", maxrun, "（仕込み目標:", m["run"], "）")
        assert maxrun == m["run"], (key, maxrun, m["run"])
    print("検算OK")
