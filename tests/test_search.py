# -*- coding: utf-8 -*-
import json
from datetime import date
from pathlib import Path

from src.content import Article, load_articles, render_markdown
from src.render import render_site
from src.search import INDEX_BUDGET_BYTES, build_index, headings, plain_text, search_json

ROOT = Path(__file__).resolve().parent.parent


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


def test_plain_text_strips_tags_unescapes_and_collapses_spaces():
    assert plain_text("A &amp; B\n  <em>C</em>") == "A & B C"


def test_headings_take_h2_and_h3_text_only():
    body = (
        "## これで何ができるか {: .what }\n\n"
        "### 小見出し `code`\n\n"
        "#### h4 は入れない\n\n"
        "本文\n"
    )
    assert headings(render_markdown(body)) == ["これで何ができるか", "小見出し code"]


def test_build_index_has_one_entry_per_article_with_expected_fields():
    index = build_index([_article(slug="a"), _article(slug="b", category="tools")])
    assert [e["url"] for e in index] == ["/recipes/a/", "/tools/b/"]
    entry = index[0]
    assert set(entry) == {
        "url", "title", "description", "tags", "headings",
        "category", "category_label", "scene", "scene_label", "published",
    }
    assert entry["tags"] == ["自動化"]
    assert entry["headings"] == []
    assert entry["published"] == "2026-08-01"
    assert entry["scene"] is None and entry["scene_label"] is None


def test_index_labels_come_from_config():
    entry = build_index([_article(category="tools", scene="earn")])[0]
    assert entry["category_label"] == "ツール"
    assert entry["scene"] == "earn"
    assert entry["scene_label"] == "副業"


def test_search_json_keeps_japanese_readable_and_round_trips():
    articles = [_article(title="題名テスト")]
    text = search_json(articles)
    assert "題名テスト" in text          # \uXXXX に逃がさない
    assert text.endswith("\n")
    assert json.loads(text) == build_index(articles)


def test_real_content_index_is_within_budget_and_clean():
    """実データの歯止め。索引が黙って重くなったり、見出しにタグが混ざったりしたら落ちる。"""
    articles, errors = load_articles(ROOT / "content")
    assert errors == []
    index = build_index(articles)
    assert {e["url"] for e in index} == {a.url for a in articles}
    for entry in index:
        for heading in entry["headings"]:
            assert "<" not in heading, (entry["url"], heading)
    size = len(search_json(articles).encode("utf-8"))
    assert size <= INDEX_BUDGET_BYTES, f"search.json が {size} バイト（予算 {INDEX_BUDGET_BYTES}）"


def test_search_page_is_rendered_with_noindex_and_script():
    pages = render_site([_article()])
    html = pages["search/index.html"]
    assert '<meta name="robots" content="noindex">' in html
    assert '<script src="/static/js/search.js" defer></script>' in html
    assert 'id="search-input"' in html and 'id="search-results"' in html
    assert "<noscript>" in html and 'href="/recipes/"' in html
    assert '<link rel="canonical" href="https://ai-tsukaikata.com/search/">' in html


def test_header_search_form_is_on_every_page_except_search():
    pages = render_site([_article()])
    for path in ("index.html", "recipes/index.html", "recipes/sample/index.html"):
        header = pages[path].split("</header>")[0]
        assert 'action="/search/"' in header, path
        assert 'name="q"' in header, path
    header = pages["search/index.html"].split("</header>")[0]
    assert "site-search" not in header      # 同じ窓が2つ並ばない


def test_other_pages_do_not_load_search_js():
    pages = render_site([_article()])
    assert "search.js" not in pages["recipes/sample/index.html"]
    assert "search.js" not in pages["index.html"]
