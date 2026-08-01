# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from src.content import Article, render_markdown
from src.feeds import build_robots, build_rss, build_sitemap

SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def _article(slug="sample", category="recipes", title="題名", published=date(2026, 8, 1), **kwargs):
    defaults = dict(
        slug=slug,
        title=title,
        description="説明文です。",
        category=category,
        published=published,
        updated=None,
        tags=(),
        time_required="30分" if category == "recipes" else None,
        cost="無料" if category == "recipes" else None,
        body_html=render_markdown("本文です。"),
        source_path=Path(f"content/{category}/{slug}.md"),
    )
    defaults.update(kwargs)
    return Article(**defaults)


def test_rss_parses_as_xml():
    root = ET.fromstring(build_rss([_article()]))
    assert root.tag == "rss"
    assert root.find("channel/title").text == "AIの使い方"


def test_rss_uses_absolute_urls():
    root = ET.fromstring(build_rss([_article()]))
    assert root.find("channel/item/link").text == "https://ai-tsukaikata.com/recipes/sample/"


def test_rss_excludes_pages():
    xml = build_rss([_article(slug="about", category="pages", title="このサイトについて")])
    assert ET.fromstring(xml).find("channel/item") is None


def test_rss_limits_item_count():
    articles = [_article(slug=f"a{i}", published=date(2026, 7, 1)) for i in range(30)]
    root = ET.fromstring(build_rss(articles))
    assert len(root.findall("channel/item")) == 20


def test_rss_pubdate_is_rfc822():
    root = ET.fromstring(build_rss([_article()]))
    assert root.find("channel/item/pubDate").text.startswith("Sat, 01 Aug 2026")


def test_rss_escapes_special_characters():
    xml = build_rss([_article(title="A & B <C>")])
    assert ET.fromstring(xml).find("channel/item/title").text == "A & B <C>"


def test_sitemap_contains_article_and_section_urls():
    xml = build_sitemap([_article()], ("/", "/recipes/"))
    locs = [e.text for e in ET.fromstring(xml).iter(f"{SITEMAP_NS}loc")]
    assert "https://ai-tsukaikata.com/" in locs
    assert "https://ai-tsukaikata.com/recipes/" in locs
    assert "https://ai-tsukaikata.com/recipes/sample/" in locs


def test_sitemap_includes_pages():
    xml = build_sitemap([_article(slug="about", category="pages")], ("/",))
    locs = [e.text for e in ET.fromstring(xml).iter(f"{SITEMAP_NS}loc")]
    assert "https://ai-tsukaikata.com/about/" in locs


def test_sitemap_lastmod_prefers_updated():
    article = _article(published=date(2026, 8, 1), updated=date(2026, 8, 20))
    xml = build_sitemap([article], ("/",))
    lastmods = [e.text for e in ET.fromstring(xml).iter(f"{SITEMAP_NS}lastmod")]
    assert "2026-08-20" in lastmods


def test_robots_allows_all_and_points_to_sitemap():
    text = build_robots()
    assert "User-agent: *" in text
    assert "Disallow:" not in text
    assert "Sitemap: https://ai-tsukaikata.com/sitemap.xml" in text
