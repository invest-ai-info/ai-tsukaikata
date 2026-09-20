#!/usr/bin/env python3
"""
instagram-two-gates-500-and-10000 の判定コード。文字列照合のみ。目視評価はしない。

真値（2026-09-16 に help.instagram.com を実ブラウザで本文まで確認・出典カード12枚目）:
- サブスク＝「Instagramのプロアカウントを保有し、フォロワーが10,000人以上いること。」「18歳以上であること。」対象国に日本
- ギフト＝「フォロワーが500人以上いること。」「ファンから受け取ったスター1個につき$0.01 (米ドル)をクリエイターに提供します。」
  「このアプリ内購入の手数料はモバイルプラットフォームにより定められており、通常は30%です。」対象国に日本
- 支払い（米国以外）＝「電信送金: 残高が$100以上になると、月1回」「他のすべての支払い方法: 残高が$25以上になると、月1回」
  「毎月21日ごろ」「支払いアカウントがなくても、収益化ツールあたり最大$500」「6か月以内に支払いアカウントの追加を完了しなかった場合、
  収益を受け取るすべての権利を喪失・放棄」
- コンテンツ収益化ポリシーの禁止フォーマット＝「動きの乏しい動画」「静止画像を使ったアンケート」「画像のスライドショー」「ループ動画」
  「主にテキストを組み合わせたコンテンツ」「埋め込み広告」。禁止カテゴリに「オリジナルでないコンテンツ」
- ボーナスは原文未取得（記事に書かない）
"""
import os
import re
import glob

RAW_DIR = "docs/evidence/_raw/instagram-two-gates-500-and-10000"


def load(pattern):
    paths = sorted(glob.glob(f"{RAW_DIR}/{pattern}"))
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        body = text.split("## 返ってきたもの", 1)[1]
        body = body.split(chr(10), 1)[1]  # 見出し行（tokens・秒の数字）は判定対象から外す
        out.append((os.path.basename(p), body))
    return out


def has(pattern, text):
    # 見出しと本文が改行で分かれる書き方が多いので、常に改行をまたいで照合する
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


GIFT_500 = r"ギフト.{0,120}500\s*人|500\s*人.{0,60}ギフト"
# 同じ行（表なら同じ行）の中だけで見る＝改行の先の別の話題を拾わない
GIFT_VAGUE = r"ギフト[^\n]{0,200}(下限(が|は)?(公表されていない|なし|ない)|数百人|数千人|明記されていない|明確な(下限|フォロワー数)|条件が設定されている時期)"
SUB_10000 = r"(10,000|1万|10000)\s*人"

print("## 指示文A（素朴に聞く・run01〜03）")
cols = ["ギフト＝500人と述べた", "ギフトの人数をぼかした（数百人・数千人・下限なし等）", "サブスク＝10,000人と述べた", "スター1個＝$0.01 と述べた", "最低支払額 $25 を挙げた", "「1フォロワー1〜3円」等の相場を出した", "「ダッシュボード／ヘルプで確認」と断った"]
rows = []
for name, body in load("run0[1-3]_*"):
    flags = {
        cols[0]: has(GIFT_500, body),
        cols[1]: has(GIFT_VAGUE, body),
        cols[2]: has(SUB_10000, body),
        cols[3]: has(r"(0\.01\s*(米)?ドル|\$0\.01|1セント)", body),
        cols[4]: has(r"25\s*(米)?ドル|\$25", body),
        cols[5]: has(r"1\s*〜\s*3\s*円", body),
        cols[6]: has(r"(ダッシュボード|ヘルプ).{0,40}(確認|正とする)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文B（門の種類と人数・run04〜06）")
cols = ["ギフト＝500人と述べた", "ギフトの人数をぼかした", "サブスク＝10,000人と述べた", "「バッジ」を挙げた", "ストア手数料（30%等）に触れた", "「ボーナスは日本で使えない／招待制」と述べた", "「ダッシュボードで確認」と断った"]
rows = []
for name, body in load("run0[4-6]_*"):
    flags = {
        cols[0]: has(GIFT_500, body),
        cols[1]: has(GIFT_VAGUE, body),
        cols[2]: has(SUB_10000, body),
        cols[3]: has(r"バッジ", body),
        cols[4]: has(r"(ストア|App Store|Google Play|アプリ内課金).{0,40}手数料", body),
        cols[5]: has(r"ボーナス.{0,80}(招待制|未提供|対象外|提供されていません)", body),
        cols[6]: has(r"ダッシュボード.{0,60}(確認|表示され|決まります)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文C（スター単価と振込・run07〜09）")
cols = ["スター1個＝$0.01", "最低支払額 $25", "電信送金は $100 と述べた", "「毎月21日ごろ」", "「以前は100ドルから引き下げ」等の出典に無い経緯を書いた", "円換算の目安を出した", "「ヘルプで最新を確認」と断った"]
rows = []
for name, body in load("run0[7-9]_*"):
    flags = {
        cols[0]: has(r"(0\.01\s*(米)?ドル|\$0\.01|1セント)", body),
        cols[1]: has(r"25\s*(米)?ドル|\$25", body),
        cols[2]: has(r"(電信送金|銀行送金|ワイヤー).{0,40}100", body),
        cols[3]: has(r"21\s*日", body),
        cols[4]: has(r"(以前は|かつては).{0,20}100", body),
        cols[5]: has(r"約?\s*\d[\d.,]*\s*円|1\.5\s*円|1円強", body),
        cols[6]: has(r"(ヘルプ|ダッシュボード).{0,60}(確認)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文D（材料を渡す・フォロワー600人・run10〜12）")
cols = ["①ギフトだけ該当と答えた", "②2,500個と答えた", "③6か月の期限を挙げた", "支払いアカウントの追加を挙げた", "「材料に無い」の受け皿を使った", "材料に無い円・％の数字を出した個数", "「21日ごろ」の適用範囲を留保した"]
rows = []
for name, body in load("run1[0-2]_*"):
    yen = re.findall(r"\d[\d,.]*\s*円", body)
    pct = re.findall(r"\d[\d.]*\s*[%％]", body)
    flags = {
        cols[0]: has(r"ギフト.{0,40}(満たす|条件を満たしています|だけ|1つ)", body) and has(r"サブスクリプション.{0,60}(満たさない|満たしていません|届きません|不足)", body),
        cols[1]: has(r"2,?500\s*個", body),
        cols[2]: has(r"6\s*か月", body),
        cols[3]: has(r"支払いアカウント.{0,20}(追加|作|用意)", body),
        cols[4]: has(r"材料に(無い|ない|書かれていない|ありません)", body),
        cols[5]: len(yen) + len(pct),
        cols[6]: has(r"「他の」|他の.{0,20}ツール.{0,60}(材料に無い|判断できません|含まれるか)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文E（禁止フォーマット・run13〜15）")
cols = ["スライドショーを対象外と述べた", "ループ動画を対象外と述べた", "文字主体（テキストモンタージュ等）を対象外と述べた", "「オリジナルでないコンテンツ」に触れた", "アカウント単位の資格停止に触れた", "「Metaが2025年に発表」等の出典に無い経緯を書いた", "「ポリシーの最新版を確認」と断った"]
rows = []
for name, body in load("run1[3-5]_*"):
    flags = {
        cols[0]: has(r"スライドショー", body),
        cols[1]: has(r"ループ動画", body),
        cols[2]: has(r"(テキストモンタージュ|文字だけ|文字の表示が主体|文字を出すだけ|画面のほとんどが文字)", body),
        cols[3]: has(r"(オリジナルでない|非オリジナル|オリジナリティ)", body),
        cols[4]: has(r"アカウント.{0,20}(停止|剥奪|制限|失う|失っ|対象外)", body),
        cols[5]: has(r"2025\s*年", body),
        cols[6]: has(r"(最新|現行).{0,80}(確認)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文F（ページ名だけ・run16〜18）")
cols = ["数字を書いた", "「パートナー収益化ポリシー」を挙げた", "「コンテンツ収益化ポリシー」を挙げた", "支払い（支払いアカウント等）のページを挙げた", "ギフトのページを挙げた", "「ページ名は変わりうる」と断った"]
rows = []
for name, body in load("run1[6-8]_*"):
    flags = {
        cols[0]: has(r"\d", body),
        cols[1]: has(r"パートナー収益化ポリシー", body),
        cols[2]: has(r"コンテンツ収益化ポリシー", body),
        cols[3]: has(r"支払い(アカウント|口座|のしくみ|について|の最低額|のスケジュール|を受け取る)", body),
        cols[4]: has(r"ギフト", body),
        cols[5]: has(r"(改称|改題|変わる|変更|表記ゆれ|揺れ)", body),
    }
    rows.append((name, flags))
table(rows, cols)
