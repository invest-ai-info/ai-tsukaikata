# -*- coding: utf-8 -*-
"""アイキャッチ自動生成のテスト。

作った理由＝記事を足すたびに絵を描く手数をゼロにするため（自動公開の
深掘り記事にも絵を付ける）。同じslugなら必ず同じ絵になること（決定的）と、
「CSSクラスを<style>に定義し忘れるとSVGが黒塗りになる」事故（2026-08-05に
実害）を機械で封じることを確かめる。
"""
import re

import pytest

from tools.make_eyecatch import build_svg, main


def test_same_slug_gives_same_svg():
    assert build_svg("sample-slug", "recipes") == build_svg("sample-slug", "recipes")


def test_different_slugs_give_different_svgs():
    assert build_svg("slug-a", "recipes") != build_svg("slug-b", "recipes")


def test_categories_differ():
    assert build_svg("same-slug", "recipes") != build_svg("same-slug", "tools")


def test_svg_has_size_attributes():
    svg = build_svg("sample-slug", "recipes")
    assert 'viewBox="0 0 720 180"' in svg
    assert 'width="720"' in svg
    assert 'height="180"' in svg


def test_svg_has_dark_mode():
    assert "prefers-color-scheme: dark" in build_svg("sample-slug", "tools")


def test_all_used_classes_are_defined_in_style():
    """使っている class が <style> に無いと黒塗りになる（実害あり）。"""
    for category in ("recipes", "tools"):
        svg = build_svg("class-check", category)
        style = re.search(r"<style>(.*?)</style>", svg, re.DOTALL).group(1)
        defined = set(re.findall(r"\.([a-z-]+)\s*\{", style))
        used = set()
        for value in re.findall(r'class="([^"]+)"', svg):
            used.update(value.split())
        assert used <= defined, f"未定義のclass: {used - defined}（{category}）"


def test_main_writes_one_svg_per_listed_article(tmp_path):
    content = tmp_path / "content" / "recipes"
    content.mkdir(parents=True)
    (content / "one.md").write_text("x", encoding="utf-8")
    (content / "_draft.md").write_text("x", encoding="utf-8")
    pages = tmp_path / "content" / "pages"
    pages.mkdir()
    (pages / "about.md").write_text("x", encoding="utf-8")
    out = tmp_path / "out"

    written = main(content_dir=tmp_path / "content", output_dir=out)

    assert written == 1
    assert (out / "one.svg").exists()
    assert not (out / "_draft.svg").exists()
    assert not (out / "about.svg").exists()
