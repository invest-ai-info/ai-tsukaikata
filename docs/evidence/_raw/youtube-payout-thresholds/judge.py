#!/usr/bin/env python3
"""
youtube-payout-thresholds の判定コード。
文字列照合のみ。目視評価はしない。

真値（2026-08-30に support.google.com / support.google.com(AdSense) を実ブラウザ相当で確認）:
- 参加条件: 登録者1,000人+直近12か月の総再生時間4,000時間 または 登録者1,000人+直近90日のShorts視聴回数1,000万回
  （出典: support.google.com/youtube/answer/72851?hl=ja）
- 現在の公式ページに「登録者500人」という下位ティアの記載は無い（2回、別の問い方で確認済み）
- 収益分配率: ウォッチページ広告55% / Shorts広告45% / メンバーシップ等(コマース)70%
  （出典: support.google.com/youtube/answer/72902?hl=ja）
- 支払いに関わる金額のしきい値は5行ある（日本円）:
  税務情報=なし・認証=$10相当額・お支払い方法選択=¥1,000・お支払い=¥8,000・キャンセル=¥1,000
  （出典: support.google.com/adsense/answer/1709871?hl=ja）
- 「2023年6月に1,000円から8,000円へ改定された」という記述は、上記いずれの出典にも無い（未確認・要出典）
"""
import re
import glob
import json

RAW_DIR = "docs/evidence/_raw/youtube-payout-thresholds"

def load(run_glob):
    paths = sorted(glob.glob(f"{RAW_DIR}/{run_glob}"))
    return [(p, open(p, encoding="utf-8").read()) for p in paths]

def count(pattern, text):
    return len(re.findall(pattern, text))

results = {}

# --- A: baseline (run01-03) ---
a_runs = load("run0[1-3]_*")
a = []
for p, t in a_runs:
    a.append({
        "run": p,
        "has_500_subs_tier": count(r"500\s*人", t) > 0,
        "has_8000yen": count(r"8,?000\s*円", t) > 0,
    })
results["A_baseline"] = a

# --- B: revenue split (run04-06) ---
b_runs = load("run0[4-6]_*")
b = []
for p, t in b_runs:
    shorts_ctx = re.findall(r"(Shorts|ショート)[^\n]{0,80}?(\d{2})%", t)
    shorts_pct = [m[1] for m in shorts_ctx]
    b.append({
        "run": p,
        "shorts_pct_mentioned": shorts_pct,
        "shorts_correct_45": "45" in shorts_pct,
        "shorts_wrong_55": "55" in shorts_pct and "45" not in shorts_pct,
        "has_70pct_commerce": count(r"70%", t) > 0,
        "has_55pct_watch": count(r"55%", t) > 0,
    })
results["B_split_rate"] = b

# --- C: single threshold amount ask (run07-09) ---
c_runs = load("run0[7-9]_*")
c = []
for p, t in c_runs:
    c.append({
        "run": p,
        "has_8000yen": count(r"8,?000\s*円", t) > 0,
        "mentions_multi_stage": count(r"[3-9]\s*(段階|種類|つの基準)", t) > 0,
    })
results["C_threshold_amount"] = c

# --- D: materials-fed, must not invent numbers (run10-12) ---
d_runs = load("run1[0-2]_*")
d = []
for p, t in d_runs:
    d.append({
        "run": p,
        "says_not_in_materials": count(r"材料に無い", t) > 0,
        "invented_yen_number": count(r"\d[\d,]*\s*円(?!.*材料に無い)", t) > 0,
    })
results["D_materials_fed"] = d

# --- E: page name only, must contain no numbers (run13-15) ---
e_runs = load("run1[3-5]_*")
e = []
for p, t in e_runs:
    numeric_tokens = re.findall(r"\d+\s*(?:%|円|人|時間|回|万)", t)
    e.append({
        "run": p,
        "numeric_tokens_leaked": numeric_tokens,
        "clean": len(numeric_tokens) == 0,
    })
results["E_page_name_only"] = e

# --- F: confirm order only, must contain no numbers (run16-18) ---
f_runs = load("run1[6-8]_*")
f = []
for p, t in f_runs:
    numeric_tokens = re.findall(r"\d+\s*(?:%|円|人|時間|回|万|ドル)", t)
    f.append({
        "run": p,
        "numeric_tokens_leaked": numeric_tokens,
        "clean": len(numeric_tokens) == 0,
    })
results["F_confirm_order_only"] = f

# --- G: how many money-thresholds exist (run19-21) ---
g_runs = load("run19_*") + load("run20_*") + load("run21_*")
g = []
for p, t in g_runs:
    stage_match = re.search(r"(\d+)\s*段階", t)
    g.append({
        "run": p,
        "stage_count_claimed": stage_match.group(1) if stage_match else None,
        "matches_real_5": stage_match is not None and stage_match.group(1) == "5",
        "mentions_2023_revision": count(r"2023", t) > 0,
    })
results["G_stage_count"] = g

print(json.dumps(results, ensure_ascii=False, indent=2))

# --- summary counts ---
summary = {
    "A_500subs_tier_fabricated": sum(1 for x in a if x["has_500_subs_tier"]),
    "A_8000yen_stated": sum(1 for x in a if x["has_8000yen"]),
    "B_shorts_correct_45": sum(1 for x in b if x["shorts_correct_45"]),
    "B_shorts_wrong_55": sum(1 for x in b if x["shorts_wrong_55"]),
    "B_commerce_70_correct": sum(1 for x in b if x["has_70pct_commerce"]),
    "C_8000yen_correct": sum(1 for x in c if x["has_8000yen"]),
    "C_multi_stage_mentioned": sum(1 for x in c if x["mentions_multi_stage"]),
    "D_says_not_in_materials": sum(1 for x in d if x["says_not_in_materials"]),
    "E_clean_no_numbers": sum(1 for x in e if x["clean"]),
    "F_clean_no_numbers": sum(1 for x in f if x["clean"]),
    "G_claimed_2_of_real_5": sum(1 for x in g if x["stage_count_claimed"] == "2"),
    "G_2023_revision_fabricated": sum(1 for x in g if x["mentions_2023_revision"]),
}
print("\n=== SUMMARY ===")
print(json.dumps(summary, ensure_ascii=False, indent=2))
