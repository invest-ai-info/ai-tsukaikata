# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path

from src.content import Article, render_markdown
from src.render import render_site


def _article(slug="sample", category="recipes", title="題名", body="本文です。", **kwargs):
    defaults = dict(
        slug=slug,
        title=title,
        description="説明文です。",
        category=category,
        published=date(2026, 8, 1),
        updated=None,
        tags=("自動化",),
        time_required="30分" if category == "recipes" else None,
        cost="無料" if category == "recipes" else None,
        body_html=render_markdown(body),
        source_path=Path(f"content/{category}/{slug}.md"),
    )
    defaults.update(kwargs)
    return Article(**defaults)


def test_index_contains_site_name_and_article_titles():
    pages = render_site([_article(title="レシピ1")])
    assert "AIの使い方" in pages["index.html"]
    assert "レシピ1" in pages["index.html"]


def test_article_page_contains_title_and_body():
    pages = render_site([_article(title="固有の題名", body="固有の本文")])
    html = pages["recipes/sample/index.html"]
    assert "固有の題名" in html
    assert "固有の本文" in html


def test_article_page_has_canonical_and_ogp():
    pages = render_site([_article()])
    html = pages["recipes/sample/index.html"]
    assert '<link rel="canonical" href="https://ai-tsukaikata.com/recipes/sample/">' in html
    assert 'property="og:url" content="https://ai-tsukaikata.com/recipes/sample/"' in html
    assert 'property="og:type" content="article"' in html


def test_title_is_escaped():
    pages = render_site([_article(title="A <script>alert(1)</script> B")])
    html = pages["recipes/sample/index.html"]
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_body_html_is_not_escaped():
    pages = render_site([_article(body="**強調**")])
    assert "<strong>強調</strong>" in pages["recipes/sample/index.html"]


def test_recipe_meta_is_shown():
    pages = render_site([_article()])
    html = pages["recipes/sample/index.html"]
    assert "かかる時間" in html
    assert "30分" in html


def test_page_has_no_recipe_meta():
    pages = render_site([_article(slug="about", category="pages")])
    html = pages["about/index.html"]
    assert "かかる時間" not in html


def test_list_page_is_generated_for_non_empty_category():
    pages = render_site([_article()])
    assert "recipes/index.html" in pages


def test_list_page_is_not_generated_for_empty_category():
    pages = render_site([_article()])
    assert "tools/index.html" not in pages


def test_nav_omits_empty_category():
    pages = render_site([_article()])
    assert 'href="/recipes/"' in pages["index.html"]
    assert 'href="/tools/"' not in pages["index.html"]


def test_pages_are_not_listed_on_index():
    pages = render_site([_article(slug="about", category="pages", title="固定ページの題名")])
    assert "固定ページの題名" not in pages["index.html"]
    assert 'href="/about/"' in pages["index.html"]  # フッタのリンクとしては出る


def test_output_paths_use_trailing_slash_structure():
    pages = render_site([_article(), _article(slug="about", category="pages")])
    assert set(pages) == {
        "index.html",
        "recipes/index.html",
        "recipes/sample/index.html",
        "about/index.html",
    }


def test_japanese_date_format():
    pages = render_site([_article(published=date(2026, 8, 1))])
    assert "2026年8月1日" in pages["recipes/sample/index.html"]
