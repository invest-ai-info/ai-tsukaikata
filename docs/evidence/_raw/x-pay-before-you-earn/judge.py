# -*- coding: utf-8 -*-
"""x-pay-before-you-earn の判定コード。

🔒 **AIに投げる前に書いた。**出力を見てから合否を定義すると、何を投げても
必ず失敗が見つかる（`_earn_research.md` の「合否の線は、AIに投げる前に引く」）。

判定は正規表現の文字列照合のみ。目視評価はしない。

## 事前登録した仮説（結果より先に凍らせる）

- **H1** 版a（素朴に聞く）の3回のうち、**プレミアム加入に「お金がかかる」ことに
  触れない回が1回以上ある**（＝無料で始められるように読める）
- **H2** 版a・版bを通じて、**日本のプレミアム月額980円を正しく出せる回は1回以下**
- **H3** 版c（率だけ渡して計算させる）で、**97%を定価5.00ドルに掛けて4.85ドルと
  答える回が1回以上ある**（Kindleの「70%は定価の70%ではない」と同じ罠）

⚠️ 棄却も記事にする。「壊れると思ったが壊れなかった」も結果として書く。

使い方: python docs/evidence/_raw/x-pay-before-you-earn/judge.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAW = Path(__file__).resolve().parent

# --- 版a・版b の判定項目 ---------------------------------------------------
# ⚠️ 「プレミアムが有料と分かるか」は、料金を示す語が**プレミアムと同じ文**に
# 出るかで見る。文をまたぐと、無関係の金額（10ドル等）を拾って偽陽性になる。
PREMIUM_WORD = r"(?:プレミアム|Premium|premium|X ?Blue|ブルー)"
PAID_WORD = r"(?:月額|有料|課金|加入料|サブスクリプション料|料金|円/月|ドル/月|支払っ|払っ|購入)"
SENT_SPLIT = re.compile(r"[。\n]")

CHECKS_AB = {
    # プレミアム加入が「お金がかかる」と分かる書き方か（H1）
    "premium_is_paid": lambda t: any(
        re.search(PREMIUM_WORD, s) and re.search(PAID_WORD, s) for s in SENT_SPLIT.split(t)
    ),
    # 日本のプレミアム月額（H2）。980円 か 米国の8ドル
    "price_980": lambda t: bool(re.search(r"980\s*円", t)),
    "price_8usd": lambda t: bool(re.search(r"(?:8|8\.00)\s*(?:米)?ドル", t)),
    # 収益配分の門の数字
    "imp_5m": lambda t: bool(re.search(r"(?:500\s*万|5,?000,?000|5M)", t)),
    "followers_500": lambda t: bool(re.search(r"500\s*(?:人|人以上|フォロワー)", t)),
    "months_3": lambda t: bool(re.search(r"(?:3\s*[かヶケヵ]月|三[かヶケヵ]月|過去3)", t)),
    # 入金の条件
    # 🚨 バグ修正3（2026-08-29・独立レビューの指摘）＝「$10」表記を拾えず、
    # run05 を落としていた（版b 2/3 → 3/3）。ドル記号の形も見る。
    "min_10usd": lambda t: bool(re.search(r"10\s*(?:米)?ドル|[$＄]\s?10", t)),
    "stripe": lambda t: bool(re.search(r"[Ss]tripe|ストライプ", t)),
    # 🚨 バグ修正4（2026-08-29・独立レビューの指摘）＝初版の `any_money` は
    # 「20万円」のように万を挟む形を拾えず 0/3 になっていた。実際には版aの3回とも
    # 税金の話で「年20万円超」等を書いている＝「金額を1円も書かない」は**誤り**だった。
    # 正しい主張は「**プレミアムの月額**を書かない」なので、項目を2つに割る。
    "any_money": lambda t: bool(re.search(r"\d[\d,\.]*\s*[万億]?\s*(?:円|米?ドル)", t)),
    # プレミアム（またはベーシック）の料金として金額を出したか
    "premium_price_any": lambda t: any(
        re.search(r"(?:プレミアム|Premium|ベーシック|Basic)", s)
        and re.search(r"\d[\d,\.]*\s*[万億]?\s*(?:円|米?ドル)|[$＄]\s?\d", s)
        for s in SENT_SPLIT.split(t)
    ),
    # 原文は「認証済みフォロワー」。「認証済み」を落として単なるフォロワー数にしていないか
    "verified_followers": lambda t: any(
        re.search(r"フォロワー", s) and re.search(r"認証済み", s)
        for s in SENT_SPLIT.split(t)
    ),
    # 構造の理解
    # 🚨 バグ修正（2026-08-29）＝初版は「クリエイターサブスク」等の限られた
    # 言い回しだけを見ていたので、実際には3回とも書かれていた
    # 「サブスクリプション（月額課金）」を拾えず 0/3 になっていた。語を広げた。
    "two_routes": lambda t: bool(re.search(r"(?:収益配分|広告|インプレッション)", t))
    and bool(re.search(r"サブスクリプション|サブスク|月額課金", t)),
    "basic_excluded": lambda t: bool(re.search(r"ベーシック|Basic", t))
    and bool(re.search(r"(?:では申請できない|は?対象外|では受け取れ|不可|含まれません|除外)", t)),
}

# --- 版d・e・f（記事に載せる残りの指示文。これも投げる前に線を引く）-------
#
# **H4** 版d（ベーシックで申請できるか）＝3回とも「できない」と答える
# **H5** 版e（月額と条件を渡して累計の持ち出しを計算させる）＝3回とも 2,940円 を出す
# **H6** 版f（確認すべき箇所を並べさせ、数字は書くなと指示）＝
#        3回とも金額の数字を書かない（＝指示で止められる）
CHECKS_D = {
    "says_cannot": lambda t: bool(
        re.search(r"(?:できません|申請できない|対象外|不可|必要があります|アップグレード)", t)
    ),
    "says_can": lambda t: bool(re.search(r"(?:申請できます|可能です|対象です)", t))
    and not re.search(r"(?:できません|対象外|不可)", t),
    "names_premium_tier": lambda t: bool(re.search(r"プレミアム|Premium", t)),
}

CHECKS_E = {
    # 980 × 3 = 2,940。区切りの有無どちらも拾う
    "total_2940": lambda t: bool(re.search(r"2[,，]?940", t)),
    # 🚨 追加（2026-08-29・独立レビューの指摘）＝H5は「2,940円を出すか」しか見ておらず、
    # 3回とも**結論は「最短980円」**だったことを取りこぼしていた。
    # 「過去3か月以内」は待機期間ではなく集計の窓なので、最短の持ち出しは1か月分。
    # 記事のほうが原文を読み違えていた＝この項目が無いと、その誤りが記事に残る。
    "min_is_980": lambda t: any(
        re.search(r"(?:最短|最小|下限|最低)", s) and re.search(r"980\s*円", s)
        for s in SENT_SPLIT.split(t)
    ),
    # 「3か月」が待機期間ではなく、さかのぼる集計の窓だと説明したか
    "explains_window": lambda t: bool(
        re.search(r"(?:窓|さかのぼ|遡|集計(?:の)?期間|待機期間ではな|待つ.{0,6}ではな)", t)
    ),
    # ⚠️ CHECKS_AB と同じ形にそろえる（バグ修正3で「$10」表記を足したのに、
    # こちらだけ古い形が残っていた。版eは3/3で結果は変わらないが、放置すると
    # 同じ名前の項目が版によって違う判定をする状態になる）。
    "min_10usd": lambda t: bool(re.search(r"10\s*(?:米)?ドル|[$＄]\s?10", t)),
    # 為替を勝手に決めて円換算していないか（出典に無い＝書いてはいけない数字）
    "invents_fx": lambda t: bool(re.search(r"1\s*ドル\s*[=＝約]\s*\d{2,3}\s*円|\d{2,3}\s*円/ドル", t)),
}

# --- 版g（門が2階建てであることに気づけるか）--------------------------------
#
# 🔒 **投げる前に書いた（2026-08-29・独立レビュー②の指摘を受けて追加）。**
# 記事の「条件が2階建てになっていることに気づかないとき」の節に指示文が無い、
# という指摘への追試。送る指示文＝
#   「Xのクリエイター収益配分について、参加資格が書かれているページを、
#     収益配分のページ以外にも挙げてください。ページの名前だけでよく、
#     条件の中身や数字は書かないでください。」
#
# **H7** 3回とも、収益配分のページ**以外**に参加資格があることに触れる
#        （＝「別のページも見ろ」と頼めば2階目に気づける）
# **H8** 3回のうち1回以上は、指示に反して条件の中身や数字を書いてしまう
#        （版fでは「数字を書くな」が3/3効いたが、こちらは「中身を書くな」なので
#          守りにくいはず、という見立て）
CHECKS_G = {
    # 収益化の規定ページ（＝2階目）を名指ししたか
    "names_standards": lambda t: bool(
        re.search(r"収益化(?:に関する)?(?:規定|基準|ポリシー|標準)|Monetization|monetization", t)
    ),
    # 収益配分ページ以外にもページがあると言えたか（名前は問わない）
    "more_than_one": lambda t: bool(
        re.search(r"(?:別(?:の)?ページ|他(?:の)?ページ|以下のページ|次のページ|複数(?:の)?ページ|ページも)", t)
    ),
    # プレミアムの料金ページにも触れたか（門ではないが、持ち出しの出どころ）
    "names_premium_page": lambda t: bool(re.search(r"プレミアム|Premium", t)),
    # 指示に反して条件の**数値**を書いてしまったか（H8の半分）
    # 🚨 バグ8（2026-08-29・独立レビュー3巡目の指摘）＝H8の文は「条件の**中身**や数字」なのに、
    # このチェックは数値しか見ていない。0/3 を「縛りは3回とも守られた」と読むのは誤りで、
    # 実際には条件の中身が3回とも漏れている
    # （run22＝サブスク加入が前提・ルール順守に依存／run23＝受け取れる国と地域・本人確認）。
    # ⚠️ 「条件の中身かどうか」は正規表現では決まらない＝**この項目は機械では埋められない**。
    # 中身の漏れは生の全文を読んで判定し、記事にもその旨を明記した。
    # 🔑 仮説の文と、チェックの守備範囲がずれていないかを、投げる前に突き合わせること。
    "breaks_no_detail": lambda t: bool(
        re.search(r"\d[\d,\.]*\s*(?:円|米?ドル|人|回|万|%)", t)
    ),
}

CHECKS_F = {
    # 金額の数字を書かなかったか（指示で止められるか）
    "no_money": lambda t: not re.search(r"\d[\d,\.]*\s*(?:円|米?ドル)", t),
    "lists_official": lambda t: bool(re.search(r"(?:公式|ヘルプ|原文|help\.x\.com)", t)),
}

# 版bが「プレミアムの月額」として出した円の値を拾う（真値: 日本・ウェブ月980円）。
# ⚠️ 抽出であって判定ではない。記事に書く数字はこの出力から取る（手で数えない）。
PREMIUM_YEN_RE = re.compile(
    r"(?:プレミアム|Premium)[^\n]{0,40}?(\d[\d,]*)\s*円|(\d[\d,]*)\s*円[^\n]{0,20}?(?:プレミアム|Premium)"
)

# --- 版c（率だけ渡して計算させる）の判定項目 -------------------------------
# 正解は 5.00−1.50＝3.50、3.50×0.97＝3.395→3.39。罠は 5.00×0.97＝4.85。
#
# 🚨 **バグ修正（2026-08-29・生の全文を読んで発見）。**
# 初版は本文のどこかに 4.85 があれば `trap_485` を立てていたので、
# 「5.00ドルの97%だと4.85ドルになりますが、これは誤りです」という**警告文**まで
# 罠にかかったと数えていた（3回中2回が偽陽性）。罠にかかったかどうかは
# **結論として何ドルと答えたか**で決まるので、判定は結論ブロックに限る。
# ⚠️ 同じ型の誤りは2026-08-27の記事でも起きている（判定コードの活用形漏れ）。
# **抜粋ではなく生の全文を読んで、判定コードのほうを直すこと。**
# ⚠️ 2度目の偽陽性（2026-08-29）＝結論を「見出しから400字」で切ったら、
# 窓が次の節（計算の過程）まで伸びて、そこにある警告文の 4.85 を拾った。
# **次の見出しの直前で必ず切る。**字数で切らない。
CONCLUSION_RE = re.compile(r"#+\s*結論\s*\n(.*?)(?=\n#|\Z)", re.DOTALL)


def _conclusion(text: str) -> str:
    """結論ブロックだけを返す。見出しが無ければ本文の先頭300字。"""
    found = CONCLUSION_RE.search(text)
    return found.group(1) if found else text[:300]


CHECKS_C = {
    # 結論として正解（3.39/3.395/3.40）を出したか
    "concl_339": lambda t: bool(re.search(r"3\.3[95]|3\.40", _conclusion(t))),
    # 結論として罠の値（4.85）を出したか＝実際に罠にかかったか
    "concl_485": lambda t: bool(re.search(r"4\.8[05]|4\.9", _conclusion(t))),
    # 本文で「5.00ドルに97%を掛けるのは誤り」と自分から警告したか。
    # ⚠️ 数字（4.85）を出さずに言葉だけで警告する回があるので、両方を拾う
    # （初版は4.85必須にしていたため、警告した回を1つ見落としていた）。
    # 🚨 バグ修正9（2026-08-29・独立レビュー4巡目の指摘）＝run21 は
    # 「「最大97%」という数字は購読料の97%ではなく、Apple手数料を引いた残りの97%です」と
    # 罠を警告しているのに、金額（5.00ドル／4.85）を書かずに「購読料の」と言ったので
    # 拾えず 2/3 になっていた。**金額の代わりに「定価を指す語＋の97%」の形も見る。**
    # ⚠️ 同じ型（言い回しが違うだけの偽陰性）はバグ3・4でも踏んでいる。3度目。
    "warns_trap": lambda t: any(
        (
            re.search(r"4\.8[05]", s)
            or re.search(r"5(?:\.00)?\s*ドル(?:ではなく|に掛け|にかけ|に97)", s)
            or re.search(r"(?:購読料|定価|総額|サブスクの?金額|表示価格)の\s*97\s*%", s)
        )
        and re.search(r"(?:誤り|間違|ではなく|ミス|落とし穴)", s)
        for s in re.split(r"[。\n]", t)
    ),
    "apple_fee_seen": lambda t: bool(re.search(r"1\.50|1\.5\s*ドル|30\s*%", t)),
}


def judge_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # ヘッダー（版・材料・実行方法）は判定に含めない。区切りは最初の "---" 行。
    body = text.split("\n---\n", 1)[-1]
    version = re.search(r"^版:\s*(\S+)", text, re.MULTILINE)
    version = version.group(1) if version else "?"
    checks = {
        "c": CHECKS_C, "d": CHECKS_D, "e": CHECKS_E, "f": CHECKS_F, "g": CHECKS_G,
    }.get(version[0], CHECKS_AB)
    return {
        "file": path.name,
        "版": version,
        **{name: fn(body) for name, fn in checks.items()},
    }


def main() -> int:
    runs = sorted(RAW.glob("run*.md"))
    if not runs:
        print("run*.md がありません")
        return 1

    rows = [judge_file(p) for p in runs]
    by_version: dict[str, list[dict]] = {}
    for row in rows:
        by_version.setdefault(row["版"], []).append(row)

    for version in sorted(by_version):
        group = by_version[version]
        names = [k for k in group[0] if k not in ("file", "版")]
        print(f"\n=== 版{version}（{len(group)}回） ===")
        for name in names:
            hits = sum(1 for r in group if r[name])
            marks = " ".join("○" if r[name] else "×" for r in group)
            print(f"  {name:18} {hits}/{len(group)}  {marks}")

    print("\n--- 版bが出した「プレミアムの月額」（真値: 日本・ウェブ 980円）---")
    for path in runs:
        text = path.read_text(encoding="utf-8")
        if not re.search(r"^版:\s*b", text, re.MULTILINE):
            continue
        body = text.split("\n---\n", 1)[-1]
        values = [g for m in PREMIUM_YEN_RE.finditer(body) for g in m.groups() if g]
        print(f"  {path.name}: {values}")

    print("\n--- 事前登録した仮説の判定 ---")
    a = by_version.get("a", [])
    b = by_version.get("b", [])
    c = by_version.get("c", [])
    if a:
        miss = sum(1 for r in a if not r["premium_is_paid"])
        money = sum(1 for r in a if r["any_money"])
        print(f"H1 版aで「有料」に触れなかった回: {miss}/{len(a)} → "
              f"{'支持' if miss >= 1 else '棄却'}")
        print(f"   （参考）版aで金額を1つでも出した回: {money}/{len(a)}")
    if a or b:
        ok = sum(1 for r in a + b if r["price_980"])
        print(f"H2 980円を出せた回: {ok}/{len(a) + len(b)} → "
              f"{'支持' if ok <= 1 else '棄却'}")
    # 🚨 バグ修正5（2026-08-29・独立レビューの指摘）＝`by_version` のキーは
    # 版名そのもの（"c2"）なので、`get("c")` は**記事に載せていない版c**（引用が
    # 原文の言い換えになっていて破棄したほう）だけを見ていた。
    # **記事の根拠は版c2**なので、版c2があればそちらでH3を判定する。
    c2 = by_version.get("c2", [])
    target, label = (c2, "版c2") if c2 else (c, "版c")
    if target:
        trap = sum(1 for r in target if r["concl_485"])
        right = sum(1 for r in target if r["concl_339"])
        warns = sum(1 for r in target if r["warns_trap"])
        print(f"H3 {label}で結論を4.85ドルにした回: {trap}/{len(target)} → "
              f"{'支持' if trap >= 1 else '棄却'}（結論が正解3.39: {right}/{len(target)}／"
              f"自分から罠を警告: {warns}/{len(target)}）")
    g = by_version.get("g", [])
    if g:
        knows = sum(1 for r in g if r["more_than_one"] or r["names_standards"])
        breaks = sum(1 for r in g if r["breaks_no_detail"])
        print(f"H7 版gで収益配分ページ以外の参加資格に触れた回: {knows}/{len(g)} → "
              f"{'支持' if knows == len(g) else '棄却'}")
        print(f"H8 版gで指示に反して数値を書いた回: {breaks}/{len(g)} → "
              f"{'支持' if breaks >= 1 else '棄却'}"
              "（⚠️ 数値のみ。「条件の中身」は正規表現では測れないので全文で判定＝3/3で漏れ）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
