# -*- coding: utf-8 -*-
"""読みやすさの物差しそのものを試す。

🔑 **計測器のほうが壊れる**（CLAUDE.md の性能比較の節の教訓）。実際、最初に
手で書いた測り方は `https?://\\S+` が `>）。` まで食べてしまい、**2つの文が
1つにつながって「395字の文」**に見えていた。測り方を先に試しておかないと、
その数字がそのまま「結果」になる。
"""
from src.readability import (
    LONG_RATIO_MAX,
    SENTENCE_MAX,
    SENTENCE_WARN,
    long_sentences,
    prose_sentences,
    stats,
)


def test_splits_plain_paragraphs_into_sentences():
    html = "<p>短い文です。もう一つの文です。</p>"
    assert prose_sentences(html) == ["短い文です。", "もう一つの文です。"]


def test_paragraphs_do_not_run_together():
    """段落や箇条書きをまたいで文がつながらないこと（つながると長さが嘘になる）。"""
    html = "<p>前の段落です</p><p>次の段落です</p><ul><li>箇条書きの項目です</li></ul>"
    assert prose_sentences(html) == ["前の段落です", "次の段落です", "箇条書きの項目です"]


def test_url_does_not_swallow_the_sentence_end():
    """🚨 最初の測り方が踏んだ穴。URLの後ろの `）。` まで消すと文が連結する。"""
    html = (
        '<p>発表しました（出典: <a href="https://example.com/a/b">'
        "https://example.com/a/b</a>）。公式ページだけを並べます。</p>"
    )
    got = prose_sentences(html)
    assert len(got) == 2, got
    assert got[0].startswith("発表しました")
    assert got[1] == "公式ページだけを並べます。"


def test_prompts_and_figures_are_not_counted():
    """指示文と図は、読みやすさのために書き換えるものではないので数えない。"""
    html = (
        '<div class="prompt">' + "あ" * 200 + "</div>"
        '<figure class="figure"><img alt="' + "い" * 200 + '"></figure>'
        "<p>地の文です。</p>"
    )
    assert prose_sentences(html) == ["地の文です。"]


def test_tables_code_and_headings_are_not_counted():
    html = (
        "<h2>" + "見" * 100 + "</h2>"
        "<table><tr><td>" + "表" * 100 + "</td></tr></table>"
        "<pre><code>" + "code " * 40 + "</code></pre>"
        "<p>地の文です。</p>"
    )
    assert prose_sentences(html) == ["地の文です。"]


def test_english_quotes_are_not_counted():
    """出典の原文はそのまま写すのが仕事。長くても直せない。"""
    html = (
        "<p>根拠: 「instructors receive 97% of the revenue when the student "
        "purchases their content using an instructor's coupon or referral link」</p>"
        "<p>日本語の地の文です。</p>"
    )
    assert prose_sentences(html) == ["日本語の地の文です。"]


def test_entities_are_decoded_before_counting():
    """&amp; のまま数えると1文字が5文字になる。"""
    assert prose_sentences("<p>A&amp;B です。</p>") == ["A&B です。"]


def test_long_sentences_are_returned_longest_first():
    html = f"<p>{'あ' * 130}。</p><p>{'い' * 200}。</p><p>短い。</p>"
    got = long_sentences(html)
    assert [len(s) for s in got] == [201, 131]


def test_long_sentences_respects_the_limit():
    html = f"<p>{'あ' * 70}。</p>"
    assert long_sentences(html, limit=SENTENCE_MAX) == []
    assert len(long_sentences(html, limit=SENTENCE_WARN)) == 1


def test_stats_counts_the_ratio_of_long_sentences():
    html = f"<p>短い文です。</p><p>{'あ' * 80}。</p>"
    got = stats(html)
    assert got["count"] == 2
    assert got["long_ratio"] == 0.5
    assert got["max"] == 81


def test_symbol_only_fragments_are_dropped_but_short_sentences_are_kept():
    """⚠️ 短い文まで捨てると、平均が実際より悪い方へ寄る。"""
    got = prose_sentences("<p>①</p><p>・</p><p>速い。</p>")
    assert got == ["速い。"]


def test_stats_does_not_crash_on_an_empty_body():
    assert stats("<figure><img alt='図だけ'></figure>")["count"] == 0


def test_thresholds_come_from_the_guideline():
    """建議は「50〜60字ほどで意識するとよい」。ここを勝手に緩めない。"""
    assert SENTENCE_WARN == 60
    assert SENTENCE_MAX > SENTENCE_WARN
    assert 0 < LONG_RATIO_MAX < 1
