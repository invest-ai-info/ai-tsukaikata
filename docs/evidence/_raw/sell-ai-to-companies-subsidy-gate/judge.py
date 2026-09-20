#!/usr/bin/env python3
"""
sell-ai-to-companies-subsidy-gate の判定コード。文字列照合のみ。目視評価はしない。

真値（2026-09-18 に it-shien.smrj.go.jp を本文まで確認・出典カード22枚目）:
- 「IT導入支援事業者の登録形態は「法人（単独）」「コンソーシアム」の2つの登録方法があり」
- 「単独でIT導入支援事業者としての要件を満たすことができない法人および個人事業主等は、構成員の要件を満たしていれば構成員として参画できます。」
⚠️ gBizID・SECURITY ACTION・決算書などの細目は、この記事の出典ページでは確認していない＝「原文に無い」として数える（誤りとは言わない）
"""
import os
import re
import glob

RAW_DIR = "docs/evidence/_raw/sell-ai-to-companies-subsidy-gate"


def load(pattern):
    out = []
    for p in sorted(glob.glob(f"{RAW_DIR}/{pattern}")):
        text = open(p, encoding="utf-8").read()
        body = text.split("## 返ってきたもの", 1)[1]
        body = body.split(chr(10), 1)[1]
        out.append((os.path.basename(p), body))
    return out


def has(pattern, text):
    return re.search(pattern, text, re.S) is not None


def table(rows, cols):
    print("| run | " + " | ".join(cols) + " |")
    print("|" + "---|" * (len(cols) + 1))
    for name, flags in rows:
        cells = []
        for c in cols:
            v = flags[c]
            cells.append(("○" if v else "—") if isinstance(v, bool) else str(v))
        print("| " + name + " | " + " | ".join(cells) + " |")
    totals = []
    for c in cols:
        vals = [f[c] for _, f in rows]
        totals.append(f"**{sum(vals)}/{len(rows)}**" if all(isinstance(v, bool) for v in vals) else f"**{sum(vals)}**")
    print("| **計** | " + " | ".join(totals) + " |")
    print()


print("## 指示文I1（個人事業主が単独で支援事業者に登録できるか・run01〜03）")
cols = ["単独登録＝できない（法人のみ）", "コンソーシアムの構成員なら関われる", "「申請代行は不正扱い」に触れた", "補助を受ける側（申請者）にはなれると述べた", "「登録要領で確認を」と断った", "出典ページで確認していない細目（gBizID・SECURITY ACTION・決算書）を挙げた"]
rows = []
for name, body in load("run0[1-3]_*"):
    rows.append((name, {
        cols[0]: has(r"単独[^\n]{0,40}(できません|できない|不可)", body) and has(r"法人", body),
        cols[1]: has(r"構成員", body) and has(r"コンソーシアム", body),
        cols[2]: has(r"申請代行|代行", body) and has(r"不正", body),
        cols[3]: has(r"(補助事業者|申請者|使う側|受ける側)[^\n]{0,40}(なれ|できます|可能)", body),
        cols[4]: has(r"登録要領|最新|確認(して|を|した)", body),
        cols[5]: has(r"gBizID|SECURITY ACTION|決算", body),
    }))
table(rows, cols)
