#!/usr/bin/env python3
"""
ai-stock-images-adobe-vs-pixta の判定コード。文字列照合のみ。目視評価はしない。

真値（2026-09-16 に実ブラウザで本文まで確認・出典カード10・11枚目）:
- Adobe Stock: 写真・ベクター・イラスト 33%／公式例 1枚 US$0.99／最低残高 $25／初回販売から45日／
  日本はプレミアム PayPal。禁止プロンプト5項目＝「アーティスト、実在の人物、架空のキャラクターの名前」
  「著作権で保護されているクリエイティブ作品への言及」「政府機関名」「サードパーティの知的財産への言及」
  「コンテンツが実際のニュース価値のある出来事を描写していることを示唆する説明」。
  やってはいけないこと＝「同じプロンプトまたは類似したプロンプトの繰り返しから複数のバージョンを提出すること。」
- PIXTA: 「AI生成コンテンツの新規審査申請受入終了： 2026年4月20日（月）」
  「販売中のAI生成コンテンツの販売停止： 2026年5月22日（金）」（告知 2026-04-14）
"""
import os
import re
import glob

RAW_DIR = "docs/evidence/_raw/ai-stock-images-adobe-vs-pixta"

# Adobe の禁止5項目に当たる語（英語プロンプトの中で拾う）。固有名詞は代表例の列挙＝「無い」の証明ではなく
# 「よくある固有名詞は入っていない」の確認。
ARTIST_STYLE = r"(in the style of|style of [A-Z]|by [A-Z][a-z]+ [A-Z][a-z]+|Van Gogh|Monet|Picasso|Banksy|Hokusai|Warhol|Rembrandt|Klimt|Mucha|Artgerm|Rutkowski|Ansel Adams|Leibovitz|Hopper|Dal[ií]|Ghibli|Miyazaki|Wes Anderson|Kinkade|Rockwell|Vermeer|Basquiat|Kusama)"
PERSON_CHAR = r"(Mickey|Batman|Superman|Pikachu|Pok[eé]mon|Spider-?Man|Harry Potter|Star Wars|Marvel|Disney|Pixar|Mario|Elsa|Hello Kitty|Doraemon|Totoro|Barbie|Elon|Musk|Trump|Biden|Taylor Swift|Beyonc|Messi|Ronaldo|Einstein|Marilyn|Monroe|Obama)"
GOVERNMENT = r"\b(NASA|FBI|CIA|NHS|IRS|Pentagon|White House|United Nations|\bUN\b|European Union|Parliament|Congress|Ministry|government agency)\b"
THIRD_PARTY_IP = r"\b(Apple|iPhone|iPad|MacBook|Nike|Adidas|Coca-?Cola|Starbucks|Tesla|Google|Microsoft|Amazon|Netflix|Lego|Nintendo|Sony|Samsung|McDonald|IKEA|Photoshop|Instagram|Facebook|Twitter|YouTube|TikTok|Zoom|Slack|Rolex|Gucci|Louis Vuitton|Chanel|Ferrari|Porsche|BMW|Toyota|Uber|Airbnb|Spotify|Adobe|Canva|Midjourney|DALL)\b"
NEWS_EVENT = r"\b(Olympics?|World Cup|election|COVID|pandemic|earthquake|hurricane|wildfire|tsunami|protest|breaking news|war in|invasion|Super Bowl|Coronation|inauguration)\b"


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


def code_blocks(text):
    return re.findall(r"```[^\n]*\n(.*?)```", text, re.S)


def table(rows, cols, count=False):
    head = "| run | " + " | ".join(cols) + " |"
    print(head)
    print("|" + "---|" * (len(cols) + 1))
    for name, flags in rows:
        cells = []
        for c in cols:
            v = flags[c]
            if isinstance(v, bool):
                cells.append("○" if v else "—")
            else:
                cells.append(str(v))
        print("| " + name + " | " + " | ".join(cells) + " |")
    totals = {}
    for c in cols:
        vals = [f[c] for _, f in rows]
        if all(isinstance(v, bool) for v in vals):
            totals[c] = f"**{sum(vals)}/{len(rows)}**"
        else:
            totals[c] = f"**{sum(vals)}**"
    print("| **計** | " + " | ".join(totals[c] for c in cols) + " |")
    print()


print("## 指示文A・B（10本のプロンプト・run01〜06）")
cols = ["プロンプトの本数", "①アーティスト名・実在の人物・キャラクター名", "②著作物への言及", "③政府機関名", "④第三者の知的財産（ブランド名等）", "⑤ニュース性のある出来事", "「1プロンプト1枚だけ出す」に触れた", "「no text / no logo」を自分で足した"]
rows = []
for name, body in load("run0[1-6]_*"):
    blocks = code_blocks(body)
    prompts = [b for b in blocks if len(b) > 80 and not b.strip().startswith("text,")]
    joined = "\n".join(prompts)
    flags = {
        cols[0]: len(prompts),
        cols[1]: sum(1 for p in prompts if has(ARTIST_STYLE, p) or has(PERSON_CHAR, p)),
        cols[2]: sum(1 for p in prompts if has(r"(movie|film|novel|anime|manga|game) (called|titled|named)|from the (movie|film|game|series)", p)),
        cols[3]: sum(1 for p in prompts if has(GOVERNMENT, p)),
        cols[4]: sum(1 for p in prompts if has(THIRD_PARTY_IP, p)),
        cols[5]: sum(1 for p in prompts if has(NEWS_EVENT, p)),
        cols[6]: has(r"(1枚|1本|ベストカット|最良|最も出来|最もよい).{0,40}(だけ|のみ)|色違い.{0,40}(並べて|出品しない|出さない)", body),
        cols[7]: has(r"(no text|no logo|no watermark)", joined),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文C（サイトごとの可否と取り分・run07〜09）")
cols = ["Adobe 33% と述べた", "PIXTA は不可と述べた", "PIXTA の理由を「2023年」と述べた", "PIXTA の正しい日付(2026年4月20日/5月22日)を挙げた", "本文に出てくる％表記の種類数（Adobe の33%・35%を含む）", "「最新のガイドラインを確認」と断った"]
rows = []
for name, body in load("run0[7-9]_*"):
    percents = set(re.findall(r"\d+(?:〜\d+)?%", body))
    flags = {
        cols[0]: has(r"Adobe Stock.{0,200}33%", body) or has(r"33%.{0,40}(動画|ビデオ)", body),
        cols[1]: has(r"PIXTA.{0,120}(不可|禁止|受け付けて(い|お)らず|受け付けない|認めて(い|お)らず|認めていな|登録禁止|×)", body),
        cols[2]: has(r"PIXTA.{0,200}2023\s*年", body),
        cols[3]: has(r"2026\s*年\s*(4|5)\s*月", body),
        cols[4]: len(percents),
        cols[5]: has(r"(最新|現行).{0,30}(確認|確かめ)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文D（材料を渡す・run10〜12）")
cols = ["26枚と答えた", "プレミアム PayPal を挙げた", "45日を挙げた", "「材料に無い」の受け皿を使った", "材料に無いドル額・％を出した個数", "「両方を満たした時点」と整理した"]
ALLOWED = {"33", "10", "29.99", "0.99", "25", "45", "26", "24.75", "25.74", "25.25"}
rows = []
for name, body in load("run1[0-2]_*"):
    dollars = re.findall(r"(?:US)?\$\s?(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*ドル", body)
    vals = {a or b for a, b in dollars}
    pct = set(re.findall(r"(\d+(?:\.\d+)?)\s*[%％]", body))
    extra = {v for v in vals | pct if v.rstrip("0").rstrip(".") not in {x.rstrip("0").rstrip(".") for x in ALLOWED} and v not in ALLOWED}
    flags = {
        cols[0]: has(r"26\s*枚", body),
        cols[1]: has(r"プレミアム\s*PayPal", body),
        cols[2]: has(r"45\s*日", body),
        cols[3]: has(r"材料に(無い|ない|書かれていない|ありません)", body),
        cols[4]: len(extra),
        cols[5]: has(r"(両方|遅いほう|どちらが後)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文E（派生を何十枚も・run13〜15）")
cols = ["類似・重複として不採用になると述べた", "「最良の数枚だけ」を勧めた", "アカウント停止に触れた", "PIXTA は不可と述べた", "「規約を確認」と断った"]
rows = []
for name, body in load("run1[3-5]_*"):
    flags = {
        cols[0]: has(r"(類似|重複|Similar|similar|duplicate)", body),
        cols[1]: has(r"(最良|最も出来のよい|ベスト|本当に違いのある|1〜3枚|2〜5枚|3〜5枚)", body),
        cols[2]: has(r"アカウント(の)?(停止|閉鎖|制限)", body),
        cols[3]: has(r"PIXTA.{0,80}(認めて|受け付け|禁止|不可)", body),
        cols[4]: has(r"(最新|現行).{0,30}(確認|読み直)", body),
    }
    rows.append((name, flags))
table(rows, cols)

print("## 指示文F（ページ名だけ・run16〜18）")
cols = ["数字を書いた（サイト名 123RF は除く）", "Adobe の生成AIガイドラインの名を挙げた", "Adobe のロイヤリティのページ名を挙げた", "PIXTA のページ名を挙げた", "「改題・改定がある」と断った"]
rows = []
for name, body in load("run1[6-8]_*"):
    flags = {
        cols[0]: has(r"\d", body.replace("123RF", "")),  # サイト名 123RF の数字は除く
        cols[1]: has(r"Adobe.{0,200}(生成AI|Generative AI)", body),
        cols[2]: has(r"(ロイヤリティ|Royalt)", body),
        cols[3]: has(r"PIXTA", body),
        cols[4]: has(r"(改題|改定|改称|改定|変わ|変更)", body),
    }
    rows.append((name, flags))
table(rows, cols)
