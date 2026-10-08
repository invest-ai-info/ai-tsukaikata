import re
import json
from judge import build_and_check, shift_formula

store_d = json.load(open("store_sheet.json", encoding="utf-8"))
dept_d = json.load(open("dept_sheet.json", encoding="utf-8"))

def true_rows(d, target):
    return [r["row"] for r in d["sheet"] if r["target"] == target]

store_true = {t: true_rows(store_d, t) for t in ["store","area","block","grand"]}
dept_true  = {t: true_rows(dept_d, t) for t in ["staff","dept","unit","grand"]}

store_trials = {
  "T1_aa10f19b": {"store": (9,'=SUMIFS($F:$F,$C:$C,C9,$D:$D,"売上")'),"area":(82,'=SUMIFS($F:$F,$B:$B,B82,$D:$D,"*小計")'),"block":(83,'=SUMIFS($F:$F,$A:$A,A83,$D:$D,"*中計")'),"grand":(328,'=SUMIF($D:$D,"*大計",$F:$F)')},
  "T2_a090633b": {"store": (9,'=SUMIFS(F$2:INDEX(F:F,ROW()-1), C$2:INDEX(C:C,ROW()-1), C9, D$2:INDEX(D:D,ROW()-1), "売上")'),"area":(82,'=SUMIFS(F$2:INDEX(F:F,ROW()-1), B$2:INDEX(B:B,ROW()-1), B82, D$2:INDEX(D:D,ROW()-1), "*小計")'),"block":(83,'=SUMIFS(F$2:INDEX(F:F,ROW()-1), A$2:INDEX(A:A,ROW()-1), A83, D$2:INDEX(D:D,ROW()-1), "*中計")'),"grand":(328,'=SUMIFS(F$2:INDEX(F:F,ROW()-1), D$2:INDEX(D:D,ROW()-1), "*大計")')},
  "T3_a0bb29be": {"store": (9,'=SUMIFS($F:$F,$C:$C,C9,$D:$D,"売上")'),"area":(82,'=SUMIFS($F:$F,$B:$B,B82,$D:$D,"*小計")'),"block":(83,'=SUMIFS($F:$F,$A:$A,A83,$D:$D,"*中計")'),"grand":(328,'=SUMIF($D:$D,"*大計",$F:$F)')},
  "T4_a14d080f": {"store": (9,'=SUMIFS($F:$F,$C:$C,C9,$D:$D,"売上")'),"area":(82,'=SUMIFS($F:$F,$B:$B,B82,$D:$D,"*店小計")'),"block":(83,'=SUMIFS($F:$F,$A:$A,A83,$D:$D,"*中計")'),"grand":(328,'=SUMIFS($F:$F,$D:$D,"*大計")')},
  "T5_a787a341_SUBTOTAL": {"store": (9,'=SUBTOTAL(9,F2:F8)'),"area":(82,'=SUBTOTAL(9,F2:F81)'),"block":(83,'=SUBTOTAL(9,F2:F82)'),"grand":(328,'=SUBTOTAL(9,F2:F327)')},
}
dept_trials = {
  "D1_adfedb62": {"staff": (10,'=SUMIFS($F:$F, $C:$C, C10, $D:$D, "経費")'),"dept":(95,'=SUMIFS($F:$F, $B:$B, B95, $D:$D, "経費")'),"unit":(96,'=SUMIFS($F:$F, $A:$A, A96, $D:$D, "経費")'),"grand":(368,'=SUMIF($D:$D, "経費", $F:$F)')},
  "D2_ae33f8f6": {"staff": (10,'=SUMIFS($F:$F,$C:$C,$C10,$D:$D,"経費")'),"dept":(92,'=SUMIFS($F:$F,$A:$A,$A92,$B:$B,$B92,$D:$D,"*小計")'),"unit":(93,'=SUMIFS($F:$F,$A:$A,$A93,$D:$D,"*中計")'),"grand":(368,'=SUMIFS($F:$F,$D:$D,"*大計")')},
  "D3_a11527fd_SUBTOTAL": {"staff": (7,'=SUBTOTAL(9,F2:F6)'),"dept":(92,'=SUBTOTAL(9,F2:F91)'),"unit":(93,'=SUBTOTAL(9,F2:F92)'),"grand":(368,'=SUBTOTAL(9,F2:F367)')},
  "D4_aba54131_SUBTOTAL": {"staff": (7,'=SUBTOTAL(9,F2:F6)'),"dept":(92,'=SUBTOTAL(9,F2:F91)'),"unit":(93,'=SUBTOTAL(9,F2:F92)'),"grand":(368,'=SUBTOTAL(9,F2:F367)')},
  "D5_ad16b5aa": {"staff": (10,'=SUMIFS($F:$F,$A:$A,A10,$B:$B,B10,$C:$C,C10,$D:$D,"経費")'),"dept":(95,'=SUMIFS($F:$F,$A:$A,A95,$B:$B,B95,$D:$D,"*小計")'),"unit":(96,'=SUMIFS($F:$F,$A:$A,A96,$D:$D,"*中計")'),"grand":(368,'=SUMIFS($F:$F,$D:$D,"*大計")')},
}

def formula_logic_check_fixed(sheet_json, trials, truths, prefix):
    print(f"\n=== 修正版：数式ロジック判定（誤記は正しい行へ平行移動してから検証） [{prefix}] ===")
    out = {}
    for name, tiers in trials.items():
        fixed = {}
        for tier, (stated_row, f) in tiers.items():
            true_row0 = truths[tier][0]
            if stated_row in truths[tier]:
                anchor, f2 = stated_row, f
            else:
                delta = true_row0 - stated_row
                f2 = shift_formula(f, delta)
                anchor = true_row0
            fixed[tier] = (anchor, f2)
        res = build_and_check(sheet_json, fixed, f"{prefix}_{name}_fix.xlsx")
        bad = {r: v for r, v in res["results"].items() if v[0] is not True}
        out[name] = (len(res["results"]), len(bad), bad)
        print(f"{name:25s} total={len(res['results']):3d}  bad={len(bad):3d}  bad_rows={list(bad.keys())[:10]}")
    return out

if __name__ == "__main__":
    formula_logic_check_fixed("store_sheet.json", store_trials, store_true, "storefix")
    formula_logic_check_fixed("dept_sheet.json", dept_trials, dept_true, "deptfix")
