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
            # 2026-08-13 の再構成後、トップが使うのはこちら（最新発表日の全件）
            "updates_day": {"label": "8月4日", "entries": [item]},
        },
        "archive": {"months": [("2026年8月", [item])]},
    }


def test_index_shows_news_section():
    """トップのアップデート欄は「最新の発表日の全件」（2026-08-13 再構成）。"""
    pages = render_site([_article()], news=_news_top())
    html = pages["index.html"]
    assert "AIアップデート — 8月4日の発表" in html
    assert "New ways to learn" in html
    assert "1行目" in html
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


def test_header_has_no_nav_links():
    """ヘッダーのナビは 2026-08-13 に廃止（カテゴリーボタンと重複するため）。
    ヘッダーに残るのはサイト名のリンクだけ。"""
    pages = render_site([_article()], news=_news_top())
    html = pages["recipes/sample/index.html"]
    header = html.split("</header>")[0]
    assert 'class="site-name"' in header
    assert "site-nav" not in header


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
    assert "/static/images/hero-photo.jpg" in pages["index.html"]


def test_every_page_has_favicon():
    pages = render_site([_article()])
    for name in ("index.html", "recipes/sample/index.html"):
        assert '<link rel="icon" href="/static/images/favicon.ico"' in pages[name]
        assert 'rel="apple-touch-icon"' in pages[name]


def test_news_vendor_icon_is_rendered():
    pages = render_site([_article()], news=_news_top())
    html = pages["index.html"]
    assert 'class="vdot"' in html
    assert "#10A37F" in html


def test_every_page_has_og_image():
    pages = render_site([_article()])
    for name in ("index.html", "recipes/sample/index.html"):
        html = pages[name]
        assert 'property="og:image" content="https://ai-tsukaikata.com/static/images/og-image.jpg"' in html
        assert 'name="twitter:card" content="summary_large_image"' in html


def test_scene_pages_are_generated_for_used_scenes():
    pages = render_site([_article(slug="a", scene="work"), _article(slug="b", scene="life")])
    assert "scenes/work/index.html" in pages
    assert "scenes/life/index.html" in pages
    assert "scenes/fun/index.html" not in pages


def test_scene_page_lists_only_its_own_articles():
    pages = render_site([
        _article(slug="a", title="仕事の記事", scene="work"),
        _article(slug="b", title="暮らしの記事", scene="life"),
    ])
    html = pages["scenes/work/index.html"]
    assert "仕事の記事" in html
    assert "暮らしの記事" not in html


def test_index_top_nav_hides_empty_scene_buttons():
    """カテゴリーボタン（2026-08-13）。記事の無い場面のボタンは出さない＝
    0本の場面ページは作られず404になるため。記事が入れば自動で現れる。"""
    pages = render_site([_article(slug="a", scene="earn")])
    html = pages["index.html"]
    assert 'class="top-nav-pill" href="/scenes/earn/"' in html
    assert ">AI副業</a>" in html
    assert 'href="/scenes/safety/"' not in html   # 記事0本 → ボタンごと隠す
    assert 'href="/recipes/"' in html             # 記事のあるカテゴリは出る
    assert ">深掘り記事</a>" not in html           # tools が0本ならボタンごと隠す
    # 旧デザインの場面カード節はもう無い
    assert "場面から探す" not in html


def test_index_top_nav_shows_tools_button_when_tools_exist():
    pages = render_site([_article(slug="a", scene="work"),
                         _article(slug="t", category="tools")])
    html = pages["index.html"]
    assert 'class="top-nav-pill" href="/tools/"' in html
    assert ">深掘り記事</a>" in html


def test_article_without_scene_still_renders():
    pages = render_site([_article(slug="a", scene=None)])
    assert "scenes/" not in "".join(k for k in pages)
    assert 'class="card-scene"' not in pages["index.html"]


def test_article_page_breadcrumb_has_scene():
    pages = render_site([_article(slug="a", scene="work")])
    assert 'href="/scenes/work/"' in pages["recipes/a/index.html"]


def test_checked_date_is_shown_on_the_page():
    article = _article(slug="start", category="pages", checked=date(2026, 8, 9))
    html = render_site([article])["start/index.html"]
    assert "2026年8月9日" in html
    assert "確認" in html


def test_no_checked_note_when_the_date_is_missing():
    html = render_site([_article(slug="start", category="pages")])["start/index.html"]
    assert "checked-note" not in html


def test_start_guide_appears_on_the_top_page_when_it_exists():
    html = render_site([_article(slug="start", category="pages")])["index.html"]
    assert 'href="/start/"' in html


def test_no_start_link_when_the_guide_is_missing():
    """記事が無いのにリンクを出すとリンク切れになる（既存の nav と同じ考え方）。"""
    html = render_site([_article(slug="about", category="pages")])["index.html"]
    assert 'href="/start/"' not in html

def _media():
    from datetime import datetime
    from src.news import JST, NewsItem
    item = NewsItem(
        uid="m1", source_id="media-x", title="生成AIの業務利用が拡大",
        url="https://example.com/media/1", vendor="架空メディア", label="架空メディア",
        importance="minor", published=datetime(2026, 8, 13, 8, 0, tzinfo=JST),
        summary_ja=None,
    )
    return {
        "top": {"label": "8月13日", "entries": [item]},
        "days": [("2026年8月13日", [item])],
    }


def test_index_shows_media_news_and_ainews_page():
    """メディアのAIニュース欄（2026-08-13）。見出し＋出典のみ・/ainews/ が生える。"""
    pages = render_site([_article()], media=_media())
    html = pages["index.html"]
    assert "8月13日のAIニュース" in html
    assert "生成AIの業務利用が拡大" in html
    assert "架空メディア" in html
    assert 'href="/ainews/"' in html
    archive = pages["ainews/index.html"]
    assert "2026年8月13日" in archive
    assert "https://example.com/media/1" in archive


def test_without_media_index_hides_the_section_and_page():
    """media_news.json が無い（トラッカー初回前）＝欄ごと出さない・/ainews/ も作らない。"""
    pages = render_site([_article()])
    assert "のAIニュース" not in pages["index.html"]
    assert "ainews/index.html" not in pages


def test_index_caps_articles_at_six():
    articles = [_article(slug=f"a{i}") for i in range(8)]
    pages = render_site(articles)
    html = pages["index.html"]
    assert 'href="/recipes/a5/"' in html
    assert 'href="/recipes/a6/"' not in html
    assert "すべてのレシピ" in html
