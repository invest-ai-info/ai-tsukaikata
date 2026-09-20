#!/usr/bin/env python3
"""
gpts-retirement-check-the-source の判定コード。文字列照合のみ。目視評価はしない。

真値（2026-09-16 に help.openai.com を実ブラウザで開いて本文まで確認・出典カード9枚目）:
- 「New GPT creation and publishing are not available on personal ChatGPT accounts,
   including Free, Go, Plus, and Pro.」＝個人プラン（Plus を含む）では新規作成・公開が不可
- 「Sep 25, 2026 (planned): Creation of new custom GPTs ends.」
- 「Dec 11, 2026: Scheduled retirement. Custom GPTs stop running.」
- 「Note that the dates are subject to change.」
- 収益化FAQ（記事 9119255）は削除され、8798878 へリダイレクト（本文に revenue/monetiz/earn/payout 0件）
- 後継＝「plugins」。収益化は外部チェックアウト推奨、承認は物理的な商品のみ（2026-09-18・出典カード26枚目）
"""
import os
import re
import glob

RAW_DIR = "docs/evidence/_raw/gpts-retirement-check-the-source"


def load(pattern):
    paths = sorted(glob.glob(f"{RAW_DIR}/{pattern}"))
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        # 「返ってきたもの」以降だけを判定対象にする（送った指示文の中の語を拾わないため）
        body = text.split("## 返ってきたもの", 1)[1]
        body = body.split(chr(10), 1)[1]  # 見出し行（tokens・秒の数字）は判定対象から外す
        out.append((os.path.basename(p), body))
    return out


def has(pattern, text):
    return re.search(pattern, text) is not None


def table(rows, cols):
    head = "| run | " + " | ".join(cols) + " |"
    print(head)
    print("|" + "---|" * (len(cols) + 1))
    for name, flags in rows:
        print("| " + name + " | " + " | ".join("○" if flags[c] else "—" for c in cols) + " |")
    totals = {c: sum(1 for _, f in rows if f[c]) for c in cols}
    print("| **計** | " + " | ".join(f"**{totals[c]}/{len(rows)}**" for c in cols) + " |")
    print()
    return totals


print("## 指示文A・B・C（素朴／収益化プログラム／廃止予定・run01〜09）")
cols = ["個人プラン(Plus)で作れないと述べた", "廃止の日付(9/25・12/11)を挙げた", "廃止・終了の予定は出ていないと述べた",
        "Plus等の有料プランなら作れると述べた", "収益化プログラムを米国限定・招待制の試験と述べた", "Apps SDK／ChatGPT内アプリに触れた"]
rows = []
for name, body in load("run0[1-9]_*"):
    flags = {
        cols[0]: has(r"(個人|personal).{0,60}(作成|作れ|作る|公開).{0,30}(でき(ない|ません)|不可|利用できない)", body),
        cols[1]: has(r"(9\s*月\s*25\s*日|12\s*月\s*11\s*日|Sep(tember)?\.? 25|Dec(ember)?\.? 11)", body),
        cols[2]: has(r"(廃止|終了|退役).{0,80}(出ていません|ありません|把握していません|確認できません|知りません|提示できません|ありませんでした)", body),
        cols[3]: has(r"(Plus|有料プラン).{0,80}(作成でき|作れ|作るには|作ることもでき|作るには有料|で作成)", body) and not has(r"Plus.{0,40}(作れない|作成でき(ない|ません))", body),
        cols[4]: has(r"(米国|アメリカ).{0,40}(限定|招待|試験|パイロット|一部)", body),
        cols[5]: has(r"(Apps SDK|Apps in ChatGPT|ChatGPT内アプリ|ChatGPTの中のアプリ|ChatGPTアプリ|「アプリ」)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文D（材料を渡す・run10〜12）")
cols = ["材料の範囲で「できない」と答えた", "「材料に無い」の受け皿を使った", "材料に無い金額(円・ドル・%)を出した", "今日の日付(9月18日)を自分で持ち込んだ", "「日付は変更されうる」に触れた"]
rows = []
for name, body in load("run1[0-2]_*"):
    flags = {
        cols[0]: has(r"(できません|できない|閉じて|成り立ちません|実質できません)", body),
        cols[1]: has(r"材料に無い", body),
        cols[2]: has(r"(\d\s*円|\$\s*\d|\d\s*ドル|\d\s*%)", body),
        cols[3]: has(r"9\s*月\s*18\s*日", body),
        cols[4]: has(r"(変更され|変わる可能性|確定ではな|subject to change)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文E（ページ名だけ・run13〜15）")
cols = ["年月日を書いた", "金額を書いた", "「ヘルプセンター」を挙げた", "廃止・移行FAQ(retirement/migration)の名を挙げた", "自分の記憶に限界があると断った"]
rows = []
for name, body in load("run1[3-5]_*"):
    flags = {
        cols[0]: has(r"(20\d\d\s*年|\d+\s*月\s*\d+\s*日)", body),
        cols[1]: has(r"(\d\s*円|\$\s*\d|\d\s*ドル)", body),
        cols[2]: has(r"(ヘルプセンター|help\.openai\.com|Help Center)", body),
        cols[3]: has(r"(retirement|Retirement|migration|Migration|廃止.{0,6}FAQ|移行.{0,6}FAQ)", body),
        cols[4]: has(r"(記憶にもとづく|私の知識の範囲|改題|統合されている可能性|記憶になく)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文F（後継で個人が受け取る仕組み・run16〜18）")
cols = ["「分からない」と書いた", "誰でも使える仕組みは無い(確認できない)と述べた", "物販(物理的な商品)向けの決済に触れた", "決済はChatGPTの外(自分のサイト)と述べた", "「プラグイン」を前身(2023年)と扱った"]
rows = []
for name, body in load("run1[6-8]_*"):
    flags = {
        cols[0]: has(r"(分からない|分かりません)", body),
        cols[1]: has(r"(提供されていません|整っておらず|確認できていません|一般提供されていません|用意されていません|確認できる情報はありません|把握していません)", body),
        cols[2]: has(r"(物販|物品|商品を|物を売る|物理)", body),
        cols[3]: has(r"(自分のサイト|自社サービス|自分のサービス|ChatGPTの外|自分の決済)", body),
        cols[4]: has(r"プラグイン.{0,80}(前身|終了|置き換|別の機能)", body),
    }
    rows.append((name, flags))
table(rows, cols)
