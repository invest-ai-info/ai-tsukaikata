# -*- coding: utf-8 -*-
"""H22実測: 集計欄が2段(小計+総合計)になっても名指しの一文が両方に効くかの
プロンプトを機械生成する。座標(行番号)・真値も同時に確定して真値ファイルに残す。
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
PROMPT_DIR = OUT / "prompts"
PROMPT_DIR.mkdir(exist_ok=True)

# --- 材料A: 学習塾の月謝管理表 ---
MATERIAL_A = {
    "id": "A",
    "name": "学習塾の月謝管理表",
    "group_col": "教室",
    "item_col": "生徒名",
    "value_col": "月謝(円)",
    "groups": [
        ("渋谷教室", [("田中", 24000), ("佐藤", 28000), ("鈴木", 18000), ("高橋", 32000)]),
        ("新宿教室", [("伊藤", 20000), ("渡辺", 26000), ("山本", 24000), ("中村", 30000)]),
        ("池袋教室", [("小林", 22000), ("加藤", 28000), ("吉田", 34000)]),
    ],
    "preamble": "次の表は、架空の学習塾の月謝管理表です。",
    "grand_label": "全教室",
}

# --- 材料B: カフェの仕入れ管理表 ---
MATERIAL_B = {
    "id": "B",
    "name": "カフェの仕入れ管理表",
    "group_col": "カテゴリ",
    "item_col": "品目",
    "value_col": "仕入れ額(円)",
    "groups": [
        ("豆・茶葉", [("エチオピア豆", 45000), ("コロンビア豆", 38000), ("紅茶葉", 52000), ("ほうじ茶葉", 21000)]),
        ("乳製品", [("牛乳", 18000), ("生クリーム", 24000), ("バター", 15000)]),
        ("食材(パン・スイーツ用)", [("小麦粉", 12000), ("砂糖", 9000), ("卵", 16000), ("チョコレート", 11000)]),
    ],
    "preamble": "次の表は、架空のカフェの仕入れ管理表です。",
    "grand_label": "全体",
}

BASE_INSTRUCTION = (
    "この表には、{group_col}ごとの合計欄がデータのすぐ下（{sub_start}〜{sub_end}行目）に"
    "含まれています。集計欄自身を範囲に含めない形で、行が増えても直さなくていい"
    "数式にしてください。"
)
TWO_DAN_ADDITION = "総合計欄も{total_row}行目にあります。"


def build_table(material: dict, two_dan: bool) -> tuple[str, dict]:
    """タブ区切りの表テキストと、真値・行番号のメタ情報を返す。"""
    header = [material["group_col"], material["item_col"], material["value_col"]]
    lines = ["\t".join(header)]
    row = 2
    data_rows = []
    for group_name, items in material["groups"]:
        for item_name, value in items:
            lines.append(f"{group_name}\t{item_name}\t{value}")
            data_rows.append(row)
            row += 1
    sub_start = row
    subtotal_rows = {}
    subtotal_values = {}
    for group_name, items in material["groups"]:
        lines.append(f"{group_name}\t合計\t")
        subtotal_rows[group_name] = row
        subtotal_values[group_name] = sum(v for _, v in items)
        row += 1
    sub_end = row - 1

    total_row = None
    grand_total = sum(subtotal_values.values())
    if two_dan:
        lines.append(f"{material['grand_label']}\t合計\t")
        total_row = row
        row += 1

    meta = {
        "data_rows": (data_rows[0], data_rows[-1]),
        "sub_start": sub_start,
        "sub_end": sub_end,
        "subtotal_rows": subtotal_rows,
        "subtotal_values": subtotal_values,
        "total_row": total_row,
        "grand_total": grand_total,
        "value_col_letter": "C",
        "group_col_letter": "A",
    }
    return "\n".join(lines), meta


def build_prompt(material: dict, two_dan: bool) -> tuple[str, dict]:
    table_text, meta = build_table(material, two_dan)
    data_start, data_end = meta["data_rows"]
    legend = (
        f"{material['preamble']} 列は A {material['group_col']} / "
        f"B {material['item_col']} / C {material['value_col']} です。"
        f"{data_start}〜{data_end}行目がデータ、{meta['sub_start']}〜{meta['sub_end']}行目が"
        f"{material['group_col']}ごとの合計欄です（同じ列・データの直後）。"
    )
    instruction = BASE_INSTRUCTION.format(
        group_col=material["group_col"],
        sub_start=meta["sub_start"],
        sub_end=meta["sub_end"],
    )
    if two_dan:
        instruction += TWO_DAN_ADDITION.format(total_row=meta["total_row"])

    prompt = f"{legend}\n\n{table_text}\n\n{instruction}"
    return prompt, meta


def main():
    manifest = []
    for material in (MATERIAL_A, MATERIAL_B):
        for two_dan in (False, True):
            cond = "2dan" if two_dan else "1dan"
            prompt, meta = build_prompt(material, two_dan)
            for rep in range(1, 6):
                trial_id = f"{material['id']}_{cond}_{rep}"
                path = PROMPT_DIR / f"{trial_id}.txt"
                path.write_text(prompt, encoding="utf-8")
                manifest.append({
                    "trial_id": trial_id,
                    "material": material["id"],
                    "condition": cond,
                    "rep": rep,
                    "prompt_path": str(path),
                    "meta": meta,
                })
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{len(manifest)}件のプロンプトを生成しました")


if __name__ == "__main__":
    main()
