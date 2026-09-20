#!/usr/bin/env python3
"""
note-membership-monthly-formula の判定コード。文字列照合のみ。目視評価はしない。

真値（2026-09-18 に help-note.com を実ブラウザで本文まで確認・出典カード24枚目＋7枚目）:
- 「定期購読マガジンのプラットフォーム利用料は20%、メンバーシップは10%です。」
- 「※１ 売上から事務手数料を引いたうちのプラットフォーム利用料」
- 事務手数料（7枚目）＝クレジットカード決済 5%・携帯キャリア決済 15%・PayPay 7%・Amazon Pay 7%・noteポイント 10%・PayPal 6.5%
- 振込手数料 270円/回（振込申請は売上 1,000円以上）
- 「メンバーシップは開設・運用費用が無料です。」
真値の計算＝月額1,000円×300人＝300,000円 → 全員クレカ: −15,000 → ×0.9＝256,500 → −270＝256,230円
             全員キャリア: −45,000 → ×0.9＝229,500 → −270＝229,230円（差 27,000円）
"""
import os
import re
import glob

RAW_DIR = "docs/evidence/_raw/note-membership-monthly-formula"
ENUM_RE = re.compile(r"^[\s#*]*\d+[.．、)]\s", re.M)  # 「1. 」「### 2.」など箇条書きの番号


def load(pattern):
    out = []
    for p in sorted(glob.glob(f"{RAW_DIR}/{pattern}")):
        text = open(p, encoding="utf-8").read()
        body = text.split("## 返ってきたもの", 1)[1]
        body = body.split(chr(10), 1)[1]  # 見出し行（tokens・秒の数字）は判定対象から外す
        out.append((os.path.basename(p), body))
    return out


def has(pattern, text):
    return re.search(pattern, text, re.S) is not None


def pos(pattern, text):
    m = re.search(pattern, text, re.S)
    return m.start() if m else None


HEAD_RE = re.compile(r"^\s*(#+|[①②③④⑤]|\d+[.．、)]|\||\*\*(?!結論))")


def in_order(text, *patterns):
    # 見出し・箇条書きの頭・表の行だけで前後を見る（前置きの一文に出る語で順番が壊れないように）
    heads = chr(10).join(line for line in text.splitlines() if HEAD_RE.match(line))
    ps = [pos(p, heads) for p in patterns]
    return all(p is not None for p in ps) and ps == sorted(ps)


def digits_excluding_enum(text):
    return len(re.findall(r"\d", ENUM_RE.sub("", text)))


def money_or_rate_numbers(text):
    # 「金額や率の数字」＝%・円・ドル が付いた数字だけを数える
    return len(re.findall(r"(?<![\d.])\d+(?:[.,]\d+)*\s*(?:[%％]|円|ドル|万円)", text))


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


CARD5 = r"クレジットカード[^\n]{0,40}(?<![\d.])5\s*%|(?<![\d.])5\s*%[^\n]{0,30}クレジットカード"
CARD10 = r"クレジットカード[^\n]{0,40}(?<![\d.])10\s*%|(?<![\d.])10\s*%[^\n]{0,30}クレジットカード"
CARRIER15 = r"キャリア[^\n]{0,40}(?<![\d.])15\s*%|(?<![\d.])15\s*%[^\n]{0,30}キャリア"
FEE_WORD = r"事務手数料|決済手数料"
ORDER = (FEE_WORD, r"プラットフォーム利用料|利用料", r"振込手数料|振込")

print("## 指示文A（300人・素朴に聞く・run01〜03）")
cols = ["最終額 256,230円（真値）", "242,730円（クレカ10%で計算した誤答）", "クレカ＝5%と述べた", "クレカ＝10%と述べた（誤り）", "利用料10%を「事務手数料を引いた後」に掛けた", "振込270円を引いた", "順番＝事務手数料→利用料→振込"]
rows = []
for name, body in load("run0[1-3]_*"):
    rows.append((name, {
        cols[0]: "256,230" in body,
        cols[1]: "242,730" in body,
        cols[2]: has(CARD5, body),
        cols[3]: has(CARD10, body),
        cols[4]: has(r"(引いた|差し引いた|控除した)[^\n]{0,6}(後|残|あと)[^\n]{0,30}(?<![\d.])10\s*%|(?<![\d.])10\s*%[^\n]{0,40}(引いた|差し引いた)[^\n]{0,6}(後|残)", body),
        cols[5]: "270円" in body,
        cols[6]: in_order(body, *ORDER),
    }))
table(rows, cols)

print("## 指示文B（手数料の種類・率・順番・run04〜06）")
cols = ["事務手数料（決済手段別）を挙げた", "クレカ＝5%", "キャリア＝15%", "利用料＝10%", "定期購読20%との違いに触れた", "振込270円", "順番＝事務手数料→利用料→振込"]
rows = []
for name, body in load("run0[4-6]_*"):
    rows.append((name, {
        cols[0]: has(FEE_WORD, body),
        cols[1]: has(CARD5, body),
        cols[2]: has(CARRIER15, body),
        cols[3]: has(r"利用料[^\n]{0,40}(?<![\d.])10\s*%|(?<![\d.])10\s*%[^\n]{0,30}利用料", body),
        cols[4]: has(r"定期購読[^\n]{0,60}(?<![\d.])20\s*%|(?<![\d.])20\s*%[^\n]{0,40}定期購読", body),
        cols[5]: "270円" in body,
        cols[6]: in_order(body, *ORDER),
    }))
table(rows, cols)

print("## 指示文C（材料を貼って計算・run07〜09）")
cols = ["クレカ 256,230円", "キャリア 229,230円", "差 27,000円", "「材料に無い」を使った", "材料に無い率（%）を足した個数"]
ALLOWED_PCT = {"5", "15", "10", "20", "7", "6.5", "90", "85", "95", "100"}
rows = []
for name, body in load("run0[7-9]_*"):
    pcts = re.findall(r"(\d+(?:\.\d+)?)\s*%", body)
    rows.append((name, {
        cols[0]: "256,230" in body,
        cols[1]: "229,230" in body,
        cols[2]: "27,000" in body,
        cols[3]: "材料に無い" in body,
        cols[4]: len([p for p in pcts if p not in ALLOWED_PCT]),
    }))
table(rows, cols)

print("## 指示文D（ページ名だけ・数字は書かずに・run10〜12）")
cols = ["数字ゼロ（番号を除く）", "本文中の数字の個数", "「メンバーシップとは」系のページ名", "「手数料」系のページ名", "「振込」系のページ名"]
rows = []
for name, body in load("run1[0-2]_*"):
    n = digits_excluding_enum(body)
    rows.append((name, {cols[0]: n == 0, cols[1]: n, cols[2]: "メンバーシップ" in body, cols[3]: "手数料" in body, cols[4]: "振込" in body}))
table(rows, cols)

print("## 指示文E（振込手数料・run13〜15）")
cols = ["270円", "売上1,000円以上", "負担＝クリエイター（売上から差し引き）", "検証できない過去・期限を述べた（260円・失効・以前は）", "「変わることがある／確認を」と断った"]
rows = []
for name, body in load("run1[3-5]_*"):
    rows.append((name, {
        cols[0]: "270円" in body,
        cols[1]: has(r"1,000\s*円\s*(以上|から|を超え)", body),
        cols[2]: has(r"差し引|クリエイター(側|が|の)負担|自己負担|クリエイターが払", body),
        cols[3]: has(r"260円|失効|180日|以前は|かつては", body),
        cols[4]: has(r"(変わる|変更(される|になる)|改定)(こと|可能性|場合)|確認(して|を)", body),
    }))
table(rows, cols)

print("## 指示文F（確認する順番・数字は書かずに・run16〜18）")
cols = ["率・金額の数字ゼロ", "率・金額の数字の個数", "順番＝手数料→振込の順に並べた", "「最終更新日／いつの情報か」を確認項目に入れた"]
rows = []
for name, body in load("run1[6-8]_*"):
    n = money_or_rate_numbers(body)
    rows.append((name, {
        cols[0]: n == 0, cols[1]: n,
        cols[2]: in_order(body, r"手数料", r"振込"),
        cols[3]: has(r"最終更新|更新日|いつの情報|お知らせ", body),
    }))
table(rows, cols)
