# -*- coding: utf-8 -*-
"""記事の数字が、出典ページに実在するかを照合する検査のテスト。

作った理由＝出典URLが正しくても、その数字がそのページに在るとは限らないため。
人が毎回突き合わせないと通ってしまうので、機械に渡す。

⚠️ この検査は「どの出典ページにも無い数字」を報告するだけで、
「別の行に在る数字を、違う行のものとして書いた」は捕まえられない。
料金表1枚に80種類の金額があることも珍しくないので、そこは人が生の行を見る。
"""
from decimal import Decimal

import pytest

from tools.check_numbers import (
    checkable_numbers,
    cited_urls,
    numbers_in_page,
    unverified,
)


# --- 記事から出典URLを拾う ---


def test_cited_urls_picks_up_angle_bracket_form():
    text = "料金は $5 です（出典: <https://example.com/pricing>）。"
    assert cited_urls(text) == ["https://example.com/pricing"]


def test_cited_urls_picks_up_markdown_link_form():
    text = "1. 料金ページ: [公式](https://example.com/a)"
    assert cited_urls(text) == ["https://example.com/a"]


def test_cited_urls_dedupes_but_keeps_order():
    text = "<https://b.example> と <https://a.example> と <https://b.example>"
    assert cited_urls(text) == ["https://b.example", "https://a.example"]


def test_cited_urls_ignores_internal_links():
    # サイト内リンクは出典ではない。叩きに行かない。
    text = "詳しくは [別の記事](/recipes/foo/) に書きました。<https://example.com/x>"
    assert cited_urls(text) == ["https://example.com/x"]


# --- 記事から「照合できる数字」を拾う ---


def test_checkable_numbers_takes_dollar_amounts():
    assert checkable_numbers("入力 $1.50、出力 $7.50 です。") == {
        ("$", Decimal("1.50")): ["$1.50"],
        ("$", Decimal("7.50")): ["$7.50"],
    }


def test_checkable_numbers_takes_percentages():
    assert set(checkable_numbers("DeepSWE は 37% から 49% へ。")) == {
        ("%", Decimal("37")), ("%", Decimal("49")),
    }


def test_checkable_numbers_skips_japanese_converted_units():
    # 「20万トークン」は出典では "200k tokens"。桁も表記も違うので機械照合できない。
    # 拾うと誤検知だらけになるので、最初から対象外にする。
    assert checkable_numbers("一度に読める量は 20万トークン です。") == {}


def test_checkable_numbers_skips_derived_multipliers():
    # 「1.67倍」は記事が計算した値で、出典には書かれていない。
    assert checkable_numbers("出力は 1.67倍 になります。") == {}


def test_checkable_numbers_skips_dates():
    assert checkable_numbers("2026年7月21日に発表されました。") == {}


def test_checkable_numbers_ignores_numbers_inside_urls():
    text = "（出典: <https://example.com/gemini-3-6-flash/>）で $2.00"
    assert set(checkable_numbers(text)) == {("$", Decimal("2.00"))}


# --- ページ側の数字 ---


def test_numbers_in_page_normalizes_thousands_separator():
    assert ("%", Decimal("1349")) in numbers_in_page("score of 1,349%")


def test_numbers_in_page_treats_trailing_zero_as_equal():
    # 記事が $1.50、ページが $1.5 でも同じ数。文字列比較だと落ちる。
    assert ("$", Decimal("1.50")) in numbers_in_page("costs $1.5 per unit")


# --- 突き合わせ ---


def test_unverified_returns_nothing_when_every_number_is_on_a_page():
    article = "入力 $1.50 / 出力 $7.50（出典: <https://a.example>）"
    pages = {"https://a.example": "input $1.50 output $7.50"}
    assert unverified(article, pages) == []


def test_unverified_flags_a_number_that_is_on_no_page():
    # 出典は正しいのに、その数字がページに無い場合。
    article = "入力 $30 / 出力 $180（長い入力は $60 / $270）（出典: <https://a.example>）"
    pages = {"https://a.example": "gpt-5.5-pro $30 input $180 output"}
    found = {key for key, _ in unverified(article, pages)}
    assert found == {("$", Decimal("60")), ("$", Decimal("270"))}


def test_unverified_accepts_a_number_found_on_any_cited_page():
    article = "$1.50 と $9.99（出典: <https://a.example> と <https://b.example>）"
    pages = {"https://a.example": "$1.50", "https://b.example": "$9.99"}
    assert unverified(article, pages) == []


def test_unverified_skips_pages_that_could_not_be_fetched():
    # 取得できなかったページを「数字が無い」と扱うと、全部が未確認になる。
    article = "$1.50（出典: <https://a.example>）"
    assert unverified(article, {"https://a.example": None}) == []


def test_unverified_reports_how_the_number_was_written():
    article = "出力は $270 です（出典: <https://a.example>）"
    pages = {"https://a.example": "nothing here"}
    assert unverified(article, pages) == [(("$", Decimal("270")), ["$270"])]


def test_unverified_does_not_accept_a_bare_number_of_a_different_kind():
    # 型を落として照合すると検出力が落ちる。実測（2026-08-05）＝出典10ページの数字を
    # 型なしで1つのプールにまとめたら、ドル額が「どこかに同じ数がある」だけで通った。
    article = "長い入力は $60 です（出典: <https://a.example>）"
    pages = {"https://a.example": "context window 60k tokens, 60 languages, 60% faster"}
    assert unverified(article, pages) == [(("$", Decimal("60")), ["$60"])]
