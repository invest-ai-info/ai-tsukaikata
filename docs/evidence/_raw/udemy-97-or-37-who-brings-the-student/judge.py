#!/usr/bin/env python3
"""
udemy-97-or-37-who-brings-the-student の判定コード。文字列照合のみ。目視評価はしない。

真値（2026-09-18 に support.udemy.com を本文まで確認・出典カード23枚目）:
- 「instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.」
- 「instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.」
- 「revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google」
- Udemy Business＝「Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed」
- Starter Plan（広告）＝「25% of the amount attributable to eligible ad surfaces」
- ⚠️ 原文に載っているのは現在の率だけ。過去の率（50%・25%・17.5%・20% など）や変更時期は原文に無い＝検証できない
真値の計算＝3,000円×100本＝300,000円 → 紹介リンク経由 ×97%＝291,000円／検索経由 ×37%＝111,000円（差 180,000円）
"""
import os
import re
import glob

RAW_DIR = "docs/evidence/_raw/udemy-97-or-37-who-brings-the-student"
ENUM_RE = re.compile(r"^[\s#*]*\d+[.．、)]\s", re.M)


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


def pct(n):
    # 「5%」が「15%」に当たらないように数字の前を見る
    return r"(?<![\d.])" + n + r"\s*[%％]"


def digits_excluding_enum(text):
    return len(re.findall(r"\d", ENUM_RE.sub("", text)))


def money_or_rate_numbers(text):
    # 「率や金額の数字」＝%・円・ドル・$ が付いた数字だけを数える（W-8BEN や「項目2」は数えない）
    return len(re.findall(r"(?<![\d.])\d+(?:[.,]\d+)*\s*(?:[%％]|円|ドル|万円)|[$＄]\s*\d", text))


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


HISTORY = r"(以前|かつて|過去|20[12]\d\s*年)[^\n]{0,60}(50|25|20|17\.5)\s*[%％]|(50|25|20|17\.5)\s*[%％][^\n]{0,60}(以前|かつて|過去|20[12]\d\s*年)"

print("## 指示文A（取り分を素朴に聞く・run01〜03）")
cols = ["97%（紹介リンク・クーポン経由）", "37%（Udemy経由）", "Net Amount／アプリ手数料30%に触れた", "Udemy Business プールに触れた", "UB＝15%と述べた", "UB＝17.5%と述べた（原文に無い）", "過去の率や変更時期を述べた（原文に無い）"]
rows = []
for name, body in load("run0[1-3]_*"):
    rows.append((name, {
        cols[0]: has(pct("97"), body),
        cols[1]: has(pct("37"), body),
        cols[2]: has(r"Net Amount|純額|アプリ[^\n]{0,30}30\s*[%％]|Apple|Google", body),
        cols[3]: has(r"Udemy Business|Business", body),
        cols[4]: has(r"(Business|法人|プール)[^\n]{0,80}" + pct("15") + "|" + pct("15") + r"[^\n]{0,60}(Business|法人|プール)", body),
        cols[5]: has(pct("17[.]5"), body),
        cols[6]: has(HISTORY, body),
    }))
table(rows, cols)

print("## 指示文B（Udemy Business の支払われ方・run04〜06）")
cols = ["「プール（配分枠）」の仕組みを説明した", "「視聴された分数（minutes）の割合」で分けると述べた", "プール率＝15%と述べた", "17.5%を述べた（原文に無い）", "過去の率や変更時期を述べた（原文に無い）", "「確認を／変わりうる」と断った"]
rows = []
for name, body in load("run0[4-6]_*"):
    rows.append((name, {
        cols[0]: has(r"プール|配分|按分", body),
        cols[1]: has(r"分数|視聴時間|視聴された時間|消費された|minutes|再生時間", body),
        cols[2]: has(pct("15"), body),
        cols[3]: has(pct("17[.]5"), body),
        cols[4]: has(HISTORY, body),
        cols[5]: has(r"確認(して|を|した)|変わ(る|り得る|りうる)|変更(される|になる)(こと|可能性)", body),
    }))
table(rows, cols)

print("## 指示文C（原文を貼って計算・run07〜09）")
cols = ["紹介リンク経由 291,000円", "検索経由 111,000円", "差 180,000円", "「材料に無い」を使った", "材料に無い率（%）を足した個数"]
ALLOWED = {"97", "37", "30", "15", "25", "100", "3"}
rows = []
for name, body in load("run0[7-9]_*"):
    pcts = re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)\s*[%％]", body)
    rows.append((name, {
        cols[0]: "291,000" in body,
        cols[1]: "111,000" in body,
        cols[2]: "180,000" in body,
        cols[3]: "材料に無い" in body,
        cols[4]: len([p for p in pcts if p not in ALLOWED]),
    }))
table(rows, cols)

print("## 指示文D（ページ名だけ・数字は書かずに・run10〜12）")
cols = ["数字ゼロ（番号を除く）", "本文中の数字の個数", "「Instructor Revenue Share」を挙げた", "Udemy Business の配分ページに触れた"]
rows = []
for name, body in load("run1[0-2]_*"):
    n = digits_excluding_enum(body)
    rows.append((name, {cols[0]: n == 0, cols[1]: n, cols[2]: has(r"Instructor Revenue Share|Revenue Share", body), cols[3]: has(r"Udemy Business|Business", body)}))
table(rows, cols)

print("## 指示文E（過去に変更されたか・run13〜15）")
cols = ["現在＝97%／37%と述べた", "UB現在＝15%と述べた", "UB現在＝17.5%と述べた（原文と食い違う）", "50%（過去の率）を挙げた", "変更時期を年で書いた", "「原文で確認を」と断った"]
rows = []
for name, body in load("run1[3-5]_*"):
    rows.append((name, {
        cols[0]: has(pct("97"), body) and has(pct("37"), body),
        cols[1]: has(r"(2026\s*年[^\n]{0,8}|現在[^\n]{0,30})" + pct("15"), body),
        cols[2]: has(r"(2026\s*年[^\n]{0,8}|現在[^\n]{0,30})" + pct("17[.]5"), body),
        cols[3]: has(pct("50"), body),
        cols[4]: has(r"20[12]\d\s*年", body),
        cols[5]: has(r"確認(して|を|した)|公式|ヘルプ", body),
    }))
table(rows, cols)

print("## 指示文F（確認する順番・数字は書かずに・run16〜18）")
cols = ["率・金額の数字ゼロ", "率・金額の数字の個数", "「誰が客を連れてきたか（紹介リンク／クーポン）」を確認項目に入れた", "Udemy Business の配分を確認項目に入れた", "支払い（PayPal／Payoneer・時期）を確認項目に入れた"]
rows = []
for name, body in load("run1[6-8]_*"):
    n = money_or_rate_numbers(body)
    rows.append((name, {
        cols[0]: n == 0, cols[1]: n,
        cols[2]: has(r"紹介|クーポン|リファラル|referral", body),
        cols[3]: has(r"Udemy Business|Business", body),
        cols[4]: has(r"PayPal|Payoneer|支払(い|われ)|振込|入金", body),
    }))
table(rows, cols)
