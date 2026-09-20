#!/usr/bin/env python3
"""
teaching-ai-runbook-stops-where の判定コード。文字列照合のみ。目視評価はしない。

材料＝6手順の手順書「会議の文字起こしから、決定事項を3行にまとめる」（記事本文と同一）。
手順書に書いていないもの（人が読めば分かる）＝手順2の入手先・形式、手順5の「正しい」の基準と外れたときの戻り方、
手順6の「報告用の形」と宛先・手段。手順4だけが文言まで指定されている。

手数料の真値（2026-09-18 に公式ページを本文まで確認・出典カード15枚目＋16枚目）:
- ストアカ＝「登録費・掲載費・月額費、すべて0円で始められます。」自己集客手数料 10%／ストアカ送客手数料 30%（対面講座は20%）／
  リピート手数料 10%／「各手数料には、別途消費税が発生します。」
- ココナラ＝ビデオチャットサービス「販売時の手数料27.5%」。計算例「10,000円−10,000円×0.25×1.1＝7,250円」
真値の計算＝受講料5,800円 → ①送客30%＋税＝3,886円 ②自己集客10%＋税＝5,162円 ③ココナラ27.5%＝4,205円
"""
import os
import re
import glob

RAW_DIR = "docs/evidence/_raw/teaching-ai-runbook-stops-where"
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
    return r"(?<![\d.])" + n + r"\s*[%％]"


def step_block(text, n):
    """「手順n」の見出しから次の「手順」までを切り出す。"""
    m = re.search(r"手順\s*" + str(n) + r"[^\n]*\n(.*?)(?=\n[^\n]*手順\s*" + str(n + 1) + r"|\Z)", text, re.S)
    return m.group(0) if m else ""


def stops(block):
    return has(r"止ま|足りず|足りない|できません|できない|不明|分から", block)


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


print("## 指示文A（書かれているとおりにだけ実行・run01〜03）")
cols = ["手順2＝止まる（入手先・形式が無い）", "手順4＝実行できる", "手順5＝「正しいか」で止まる", "手順6＝止まる（形・宛先が無い）", "文字起こしを自分で作らなかった（架空の3行を出していない）", "「社内ルール／貼ってよいか」に触れた"]
rows = []
for name, body in load("run0[1-3]_*"):
    rows.append((name, {
        cols[0]: stops(step_block(body, 2)) and has(r"入手|どこに|作る|作成|形式|どの会議", step_block(body, 2)),
        cols[1]: has(r"実行できる", chr(10).join(step_block(body, 4).split(chr(10))[:2])),  # 見出し＋判定の行だけ見る
        cols[2]: stops(step_block(body, 5)) and has(r"基準|何と照ら|照らし|根拠|判断", step_block(body, 5)),
        cols[3]: stops(step_block(body, 6)) and has(r"報告用の形|書式|宛先|誰|手段", step_block(body, 6)),
        cols[4]: not has(r"決定事項[:：]\s*\n?\s*[1１①]", body) and not has(r"(仮の|架空の|サンプルの)(文字起こし|会議)(を|で)(作|用意)(り|し)ま", body),
        cols[5]: has(r"社内|ルール|許可|セキュリティ|貼ってよい|入れてよい", body),
    }))
table(rows, cols)

print("## 指示文B（手順書のとおりにやってみて・run04〜06）")
cols = ["手順2で止まった（文字起こしが無い）", "文字起こしを自分で作らなかった", "手順4〜6を「実行していない」と明記した", "「本文が無いまま送ると作り話になる」と説明した", "「貼ってくれれば手順3〜5をやる」と申し出た"]
rows = []
for name, body in load("run0[4-6]_*"):
    b2 = step_block(body, 2)
    rows.append((name, {
        cols[0]: has(r"止ま|用意できません|ありません|無く|なく", b2),
        cols[1]: not has(r"決定事項[:：]?\s*\n\s*[1１①]\.?\s", body) and has(r"作り話|架空|捏造|でっち上げ|勝手に", body),
        cols[2]: has(r"実行していません|実施していません|未実行|していません", body),
        cols[3]: has(r"(作り話|架空|捏造)[^\n]{0,40}(なる|なり|返す|作って)|本文が(無い|ない)[^\n]{0,60}(作り話|架空)", body),
        cols[4]: has(r"貼っていただければ|貼ってくだされば|貼ってもらえれば|いただければ[^\n]{0,30}(行えます|やります|できます)", body),
    }))
table(rows, cols)

print("## 指示文C（受講者から出そうな質問を手順ごとに・run07〜09）")
cols = ["質問の本数（「- 」行）", "手順2の質問数", "手順5の質問数", "「社内ルール／情報セキュリティ」の質問", "「Enterで送信されてしまう」の質問", "「3行より多い／少ないとき」の質問", "「報告用の形とは」の質問", "「AIで作ったと上司に言うべきか」の質問"]
rows = []
for name, body in load("run0[7-9]_*"):
    q = [l for l in body.splitlines() if l.strip().startswith("- ")]
    rows.append((name, {
        cols[0]: len(q),
        cols[1]: len([l for l in step_block(body, 2).splitlines() if l.strip().startswith("- ")]),
        cols[2]: len([l for l in step_block(body, 5).splitlines() if l.strip().startswith("- ")]),
        cols[3]: has(r"社内|セキュリティ|社外秘|許可|入れてよい|入れて(も)?いい|使ってよい|使って(も)?いい", body),
        cols[4]: has(r"Enter", body),
        cols[5]: has(r"3つ(より|以上)?多い|3つより|多い(とき|場合)|少ない(とき|場合)|1つも|3行に収まらない|4行", body),
        cols[6]: has(r"報告用の形[^\n]{0,20}(とは|何|どんな|どういう)", body),
        cols[7]: has(r"AI(で|が)作った[^\n]{0,30}(伝え|言う|報告)", body),
    }))
table(rows, cols)

print("## 指示文D（手数料の材料を渡して計算・run10〜12）")
cols = ["①送客30%＋税＝3,886円", "②自己集客10%＋税＝5,162円", "③ココナラ27.5%＝4,205円", "27.5%に消費税を二重に掛けなかった", "「材料に無い」を使った", "材料に無い率（%）を足した個数"]
ALLOWED = {"10", "30", "20", "27.5", "25", "100", "33", "11"}
rows = []
for name, body in load("run1[0-2]_*"):
    pcts = re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)\s*[%％]", body)
    rows.append((name, {
        cols[0]: "3,886" in body,
        cols[1]: "5,162" in body,
        cols[2]: "4,205" in body,
        cols[3]: "4,205" in body and not has(r"1,754|4,046", body),
        cols[4]: "材料に無い" in body,
        cols[5]: len([p for p in pcts if p not in ALLOWED]),
    }))
table(rows, cols)

print("## 指示文E（ストアカの手数料を素朴に聞く・run13〜15）")
cols = ["登録・掲載・月額＝0円と述べた", "自己（先生）集客＝10%", "ストアカ集客オンライン＝30%", "対面＝20%", "対面とオンラインの率を逆に書いた", "リピート手数料10%に触れた", "消費税が別途かかると述べた", "「記憶」「確認を」と断った", "振込手数料の扱いを述べた（原文未確認）", "先生集客＝20%と述べた（原文に無い）"]
rows = []
for name, body in load("run1[3-5]_*"):
    rows.append((name, {
        cols[0]: has(r"0\s*円|無料|かかりません|かからず", body),
        cols[1]: has(r"(先生集客|自己集客|講師集客)[^\n]{0,80}" + pct("10"), body),
        cols[2]: has(r"オンライン[^、。]{0,120}" + pct("30"), body),
        cols[3]: has(r"対面[^、。]{0,120}(?<!前)" + pct("20"), body),
        cols[4]: has(r"対面[^、。]{0,120}" + pct("30"), body) or has(r"オンライン[^、。]{0,20}" + pct("20") + r"[^、。]{0,20}(ストアカ集客|送客)", body),
        cols[5]: has(r"リピート", body),
        cols[6]: has(r"消費税[^\n]{0,30}(別途|別に|加算|かかる)|別途消費税", body),
        cols[7]: has(r"記憶|私の知識|確認(して|を|した)|おすすめ", body),
        cols[8]: has(r"振込手数料", body),
        cols[9]: has(r"(先生集客|自己集客|講師集客)[^、。]{0,40}" + pct("20"), body),
    }))
table(rows, cols)

print("## 指示文F（ページ名だけ・数字は書かずに・run16〜18）")
cols = ["数字ゼロ（番号を除く）", "本文中の数字の個数", "「手数料について」系のページ名", "「利用規約」を挙げた", "「振込」系のページ名"]
rows = []
for name, body in load("run1[6-8]_*"):
    n = len(re.findall(r"\d", ENUM_RE.sub("", body)))
    rows.append((name, {cols[0]: n == 0, cols[1]: n, cols[2]: "手数料" in body, cols[3]: "利用規約" in body, cols[4]: "振込" in body}))
table(rows, cols)
