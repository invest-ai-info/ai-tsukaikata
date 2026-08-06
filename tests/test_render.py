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


def test_copy_script_is_loaded_with_defer():
    """指示文のコピーボタンは JS で足す。defer にして描画を止めない。"""
    pages = render_site([_article()])
    html = pages["recipes/sample/index.html"]
    assert '<script src="/static/js/copy.js" defer></script>' in html


def test_japanese_date_format():
    pages = render_site([_article(published=date(2026, 8, 1))])
    assert "2026年8月1日" in pages["recipes/sample/index.html"]


def _news_top():
    from datetime import datetime
    from src.news import JST, NewsItem
    item = NewsItem(
        uid="n1", source_id="openai-news",
        title="New ways to learn", url="https://example.com/post",
        vendor="OpenAI", label="OpenAI News", importance="major",
        published=datetime(2026, 8, 4, 9, 0, tzinfo=JST),
        summary_ja="1行目\n2行目\n3行目",
        icon_code="O", icon_color="#10A37F",
    )
    return {
        "top": {
            "announcements": [item],
            "model_groups": [{
                "label": "Claude Code", "vendor": "Anthropic", "count": 2,
                "latest_title": "v2.1.223",
                "latest_published": item.published,
            }],
        },
        "archive": {"months": [("2026年8月", [item])]},
    }


def test_index_shows_news_section():
    pages = render_site([_article()], news=_news_top())
    html = pages["index.html"]
    assert "AIアップデート" in html
    assert "New ways to learn" in html
    assert "1行目" in html
    assert "重要" in html
    assert "Claude Code: 2件（最新: v2.1.223）" in html
    assert "要約は自動生成" in html
    assert 'href="/news/"' in html


def test_news_page_is_rendered_with_months():
    pages = render_site([_article()], news=_news_top())
    html = pages["news/index.html"]
    assert "2026年8月" in html
    assert "New ways to learn" in html
    assert '<link rel="canonical" href="https://ai-tsukaikata.com/news/">' in html


def test_without_news_index_has_no_news_section():
    pages = render_site([_article()])
    assert "AIアップデート" not in pages["index.html"]
    assert "news/index.html" not in pages


def test_news_nav_link_present_only_with_news():
    with_news = render_site([_article()], news=_news_top())
    without = render_site([_article()])
    assert '<a href="/news/">AIアップデート</a>' in with_news["index.html"]
    assert '<a href="/news/">AIアップデート</a>' not in without["index.html"]


def test_card_shows_eyecatch_only_when_available():
    with_img = render_site([_article(slug="sample")], eyecatches={"sample"})
    without = render_site([_article(slug="sample")])
    assert "/static/images/eyecatch/sample.svg" in with_img["index.html"]
    assert "/static/images/eyecatch/sample.svg" not in without["index.html"]


def test_article_page_shows_eyecatch_banner():
    pages = render_site([_article(slug="sample")], eyecatches={"sample"})
    html = pages["recipes/sample/index.html"]
    assert 'class="eyecatch"' in html
    assert "/static/images/eyecatch/sample.svg" in html


def test_index_hero_has_illustration():
    pages = render_site([_article()])
    assert "/static/images/hero.svg" in pages["index.html"]


def test_news_vendor_icon_is_rendered():
    pages = render_site([_article()], news=_news_top())
    html = pages["index.html"]
    assert 'class="vdot"' in html
    assert "#10A37F" in html


def test_every_page_has_og_image():
    pages = render_site([_article()])
    for name in ("index.html", "recipes/sample/index.html"):
        html = pages[name]
        assert 'property="og:image" content="https://ai-tsukaikata.com/static/images/og-card.png"' in html
        assert 'name="twitter:card" content="summary_large_image"' in html
