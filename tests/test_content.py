# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path

import pytest

from src.content import (
    Article,
    ArticleError,
    load_articles,
    parse_article,
    render_markdown,
    split_frontmatter,
)

RECIPE = """---
title: テスト記事
description: これはテストです。
category: recipes
published: 2026-08-01
tags: [GitHub Actions, 自動化]
time_required: 30分
cost: 無料
---

本文です。
"""

PAGE = """---
title: このサイトについて
description: 運営者と方針。
category: pages
published: 2026-08-01
---

固定ページの本文。
"""


def _write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_split_frontmatter_returns_meta_and_body():
    meta, body = split_frontmatter(RECIPE)
    assert meta["title"] == "テスト記事"
    assert body.strip() == "本文です。"


def test_split_frontmatter_without_frontmatter_raises():
    with pytest.raises(ArticleError):
        split_frontmatter("いきなり本文が始まる記事")


def test_split_frontmatter_with_broken_yaml_raises():
    with pytest.raises(ArticleError):
        split_frontmatter("---\ntitle: [壊れた\n---\n本文\n")


def test_parse_article_reads_all_fields():
    article = parse_article(Path("content/recipes/sample.md"), RECIPE)
    assert article.title == "テスト記事"
    assert article.description == "これはテストです。"
    assert article.category == "recipes"
    assert article.published == date(2026, 8, 1)
    assert article.updated is None
    assert article.tags == ("GitHub Actions", "自動化")
    assert article.time_required == "30分"
    assert article.cost == "無料"
    assert "本文です。" in article.body_html


def test_parse_article_slug_comes_from_filename():
    article = parse_article(Path("content/recipes/my-slug.md"), RECIPE)
    assert article.slug == "my-slug"


def test_recipe_url_and_output_path():
    article = parse_article(Path("content/recipes/my-slug.md"), RECIPE)
    assert article.url == "/recipes/my-slug/"
    assert article.output_path == "recipes/my-slug/index.html"


def test_page_url_is_top_level():
    article = parse_article(Path("content/pages/about.md"), PAGE)
    assert article.url == "/about/"
    assert article.output_path == "about/index.html"


def test_missing_required_field_raises():
    text = RECIPE.replace("description: これはテストです。\n", "")
    with pytest.raises(ArticleError, match="description"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_recipe_without_time_required_raises():
    text = RECIPE.replace("time_required: 30分\n", "")
    with pytest.raises(ArticleError, match="time_required"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_page_does_not_require_time_required():
    article = parse_article(Path("content/pages/about.md"), PAGE)
    assert article.time_required is None


def test_unknown_category_raises():
    text = RECIPE.replace("category: recipes", "category: blog")
    with pytest.raises(ArticleError, match="カテゴリ"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_non_url_safe_slug_raises():
    with pytest.raises(ArticleError, match="ファイル名"):
        parse_article(Path("content/recipes/日本語.md"), RECIPE)


def test_quoted_date_raises():
    text = RECIPE.replace("published: 2026-08-01", 'published: "2026年8月1日"')
    with pytest.raises(ArticleError, match="published"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_updated_is_parsed_when_present():
    text = RECIPE.replace("published: 2026-08-01", "published: 2026-08-01\nupdated: 2026-08-10")
    article = parse_article(Path("content/recipes/sample.md"), text)
    assert article.updated == date(2026, 8, 10)


def test_render_markdown_makes_fenced_code_block():
    html = render_markdown("```bash\npip install foo\n```")
    assert "<pre>" in html
    assert 'class="language-bash"' in html
    assert "pip install foo" in html


def test_render_markdown_makes_table():
    html = render_markdown("| a | b |\n|---|---|\n| 1 | 2 |")
    assert "<table>" in html


def test_render_markdown_escapes_raw_html_characters_in_code():
    html = render_markdown("```\n<script>alert(1)</script>\n```")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_load_articles_collects_errors_without_raising(tmp_path):
    _write(tmp_path / "recipes", "good.md", RECIPE)
    _write(tmp_path / "recipes", "bad.md", "frontmatterがない")
    articles, errors = load_articles(tmp_path)
    assert [a.slug for a in articles] == ["good"]
    assert len(errors) == 1
    assert "bad.md" in errors[0]


def test_load_articles_sorts_newest_first(tmp_path):
    _write(tmp_path / "recipes", "old.md", RECIPE.replace("2026-08-01", "2026-07-01"))
    _write(tmp_path / "recipes", "new.md", RECIPE)
    articles, errors = load_articles(tmp_path)
    assert errors == []
    assert [a.slug for a in articles] == ["new", "old"]


def test_load_articles_skips_underscore_files(tmp_path):
    _write(tmp_path, "_ideas.md", "記事ネタのメモ")
    articles, errors = load_articles(tmp_path)
    assert articles == []
    assert errors == []


def test_scene_is_parsed():
    from src.content import parse_article
    text = RECIPE.replace("category: recipes", "category: recipes\nscene: work")
    assert parse_article(Path("content/recipes/x.md"), text).scene == "work"


def test_unknown_scene_is_rejected():
    from src.content import ArticleError, parse_article
    text = RECIPE.replace("category: recipes", "category: recipes\nscene: しごと")
    with pytest.raises(ArticleError):
        parse_article(Path("content/recipes/x.md"), text)


def test_scene_is_optional():
    from src.content import parse_article
    assert parse_article(Path("content/recipes/x.md"), RECIPE).scene is None


def test_checked_is_parsed_as_a_date():
    text = (
        "---\n"
        "title: 題\n"
        "description: 説明\n"
        "category: pages\n"
        "published: 2026-08-09\n"
        "checked: 2026-08-09\n"
        "---\n"
        "本文\n"
    )
    article = parse_article(Path("content/pages/start.md"), text)
    assert article.checked == date(2026, 8, 9)


def test_checked_is_optional():
    text = (
        "---\n"
        "title: 題\n"
        "description: 説明\n"
        "category: pages\n"
        "published: 2026-08-09\n"
        "---\n"
        "本文\n"
    )
    assert parse_article(Path("content/pages/x.md"), text).checked is None


def test_quoted_checked_is_rejected():
    """クォートで囲むと文字列になる。日付形式の揺れを frontmatter で止める。"""
    text = (
        "---\n"
        "title: 題\n"
        "description: 説明\n"
        "category: pages\n"
        "published: 2026-08-09\n"
        'checked: "2026-08-09"\n'
        "---\n"
        "本文\n"
    )
    with pytest.raises(ArticleError):
        parse_article(Path("content/pages/x.md"), text)
