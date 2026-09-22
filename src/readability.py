# -*- coding: utf-8 -*-
"""本文の読みやすさを数える。判定はせず、数えた結果だけを返す。

**なぜ要るか**＝2026-09-22 にオーナーから「タイトルも文章も分かりづらい」と
指摘された。測ってみたら、感覚ではなく数字に出ていた:

| | 古い20本（8/01〜8/12） | 直近20本（9/15〜9/22） |
|---|---|---|
| 1文の平均 | 28.3字 | **44.7字** |
| 60字以上の文 | 2% | **21%** |

🔑 **犯人は「不誠実」ではなく「誠実」のほう。**「試行回数を本文に書く」
「条件を省かない」を守った結果、実測の条件が1文に流れ込んで伸びている。
実際いちばん長い文（249字）は、`📌 この記事の実測は、①…②…③…④…の4段階で、
材料6本・のべ38回試しました。`という**列挙を1文に詰めたもの**だった。

**基準の出どころ**＝文化審議会建議「公用文作成の考え方」（令和4年1月7日）Ⅲ-3「文の書き方」。
<https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/pdf/93651301_01.pdf>

- ア 一文を短くする＝「適当な長さは一概に決められないが、**50〜60字ほどに
  なってきたら読みにくくなっていないか意識するとよい**」→ `SENTENCE_WARN`
- ウ **三つ以上の情報を並べるときには、箇条書を利用する** → 長い文の直し方は
  たいていこれ（分割ではなくリスト化）
- イ 一文の論点は、一つにする／カ 接続助詞や中止法を多用しない

⚠️ **数えないもの**（直せないか、直すべきでないもの）:

- **指示文**（`<div class="prompt">`）＝コピーされる原文。読みやすさのために書き換えない
- **図**（`<figure>`）＝`alt` は「読み上げでも意味が通る説明」が要件で、長いのが正しい
- **表・コードブロック・見出し**（⚠️ 文中の `コード` は文の一部なので数える）
- **英語の原文引用**＝出典の文をそのまま写すのが仕事（`_is_english`）
"""
from __future__ import annotations

import html
import re
from datetime import date

# 📌 既存記事は直さない（2026-09-22 オーナー判断）＝日付で線を引く。
# 🚨 **番人もこの線から見る。**線を引かずに直近2週間を見たら46本が鳴り、
# 週次が「打つ手のない赤」で埋まった（2026-09-14 の死活警告と同じ壊れ方）。
# ここから先に書かれた記事だけを見るので、番人は0件から始まる
ERA = date(2026, 9, 23)

# 建議 Ⅲ-3 ア の「50〜60字ほどになってきたら意識するとよい」。
# ⚠️ これは**目安**であって、ここを超えたら即エラーではない（`tools/check_readability.py`
# が割合で見る）。実測: 全記事16,644文の中央値32字・90%が65字以内
SENTENCE_WARN = 60

# ここを超えたら、読みやすさ以前に文の構造が追えない。ビルドで止める線。
# 実測で決めた＝120字以上は全体の0.6%（106文）。⚠️ 直し方は「分ける」よりも
# たいてい「箇条書きにする」（建議 Ⅲ-3 ウ）
SENTENCE_MAX = 120

# 60字以上の文がこの割合を超えたら、記事全体として読みにくい。
# 実測＝古い20本は2%、直近20本は21%。0.15 は「直近の水準より少し良い」線
LONG_RATIO_MAX = 0.15

_DROP_BLOCKS = (
    re.compile(r"<div class=\"prompt\">.*?</div>", re.S),   # 指示文
    re.compile(r"<figure.*?</figure>", re.S),               # 図（alt は長いのが正しい）
    re.compile(r"<table.*?</table>", re.S),
    re.compile(r"<pre.*?</pre>", re.S),                     # コードブロック
    re.compile(r"<h[1-6][^>]*>.*?</h[1-6]>", re.S),
)
# ⚠️ 文中の `コード` は文の一部なので**中身は残す**（消すと文が読めなくなり、
# 長さも実際より短く出る）。消すのはブロックのほうだけ
_URL_RE = re.compile(r"https?://[^\s<>）)」』、。]+")
_TAG_RE = re.compile(r"<[^>]+>")
_JA_RE = re.compile(r"[ぁ-んァ-ヶ一-龥]")
# 箇条書きの項目と段落は、それぞれ別の文のかたまりとして扱う
_BLOCK_END_RE = re.compile(r"</(?:p|li|dd|dt|blockquote)>")


def _is_english(sentence: str) -> bool:
    """出典の原文をそのまま写した文か。⚠️ 写すのが仕事なので数えない。"""
    return sum(1 for c in sentence if ord(c) < 128) / max(len(sentence), 1) > 0.6


def prose_sentences(body_html: str) -> list[str]:
    """本文の地の文を、文（。で区切る）の一覧にする。"""
    text = body_html
    for pattern in _DROP_BLOCKS:
        text = pattern.sub(" ", text)
    text = _BLOCK_END_RE.sub("\n", text)
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    text = _URL_RE.sub("", text)

    sentences = []
    for line in text.split("\n"):
        line = line.strip().lstrip("-・*")
        for sentence in re.split(r"(?<=。)", line):
            sentence = sentence.strip()
            # ⚠️ 短い文を捨てると平均が実際より悪く出る。落とすのは
            # 記号・番号の切れ端（日本語の字を1つも含まないもの）だけにする。
            # 英語の原文引用は数えない
            if (
                len(sentence) >= 3
                and _JA_RE.search(sentence)
                and not _is_english(sentence)
            ):
                sentences.append(sentence)
    return sentences


def long_sentences(body_html: str, limit: int = SENTENCE_MAX) -> list[str]:
    """`limit` 字以上の文だけを、長い順に返す。"""
    return sorted(
        (s for s in prose_sentences(body_html) if len(s) >= limit),
        key=len,
        reverse=True,
    )


def stats(body_html: str) -> dict:
    """文の数・平均・60字以上の割合・最長。文が無ければ 0 を返す（落とさない）。"""
    sentences = prose_sentences(body_html)
    if not sentences:
        return {"count": 0, "mean": 0.0, "long_ratio": 0.0, "max": 0}
    lengths = [len(s) for s in sentences]
    long_count = sum(1 for n in lengths if n >= SENTENCE_WARN)
    return {
        "count": len(lengths),
        "mean": sum(lengths) / len(lengths),
        "long_ratio": long_count / len(lengths),
        "max": max(lengths),
    }
