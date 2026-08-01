# -*- coding: utf-8 -*-
"""RSS / sitemap.xml / robots.txt を文字列で作る。標準ライブラリだけ。

文字列連結ではなく ElementTree で組む。記事タイトルに & や < が入ったとき、
手組みだと壊れたXMLを配信してしまうため。
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from email.utils import format_datetime
from xml.etree import ElementTree as ET

from . import config
from .content import Article

JST = timezone(timedelta(hours=9))
RSS_MAX_ITEMS = 20
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def _published_at(article: Article) -> datetime:
    """日付しか持たない記事に、RSS用の時刻（JST 9:00）を与える。"""
    return datetime.combine(article.published, time(9, 0), tzinfo=JST)


def build_rss(articles: list[Article]) -> str:
    items = [a for a in articles if a.category in config.LISTED_CATEGORIES][:RSS_MAX_ITEMS]

    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:atom": "http://www.w3.org/2005/Atom",
    })
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = config.SITE_NAME
    ET.SubElement(channel, "link").text = f"{config.SITE_URL}/"
    ET.SubElement(channel, "description").text = config.SITE_DESCRIPTION
    ET.SubElement(channel, "language").text = config.SITE_LANG
    ET.SubElement(channel, "atom:link", {
        "href": f"{config.SITE_URL}/feed.xml",
        "rel": "self",
        "type": "application/rss+xml",
    })

    for article in items:
        url = config.SITE_URL + article.url
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article.title
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = url
        ET.SubElement(item, "description").text = article.description
        ET.SubElement(item, "pubDate").text = format_datetime(_published_at(article))

    return XML_HEADER + ET.tostring(rss, encoding="unicode")


def build_sitemap(articles: list[Article], section_paths: tuple[str, ...] = ("/",)) -> str:
    urlset = ET.Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    latest = max((a.updated or a.published for a in articles), default=None)

    for path in section_paths:
        node = ET.SubElement(urlset, "url")
        ET.SubElement(node, "loc").text = config.SITE_URL + path
        if latest is not None:
            ET.SubElement(node, "lastmod").text = latest.isoformat()

    for article in articles:
        node = ET.SubElement(urlset, "url")
        ET.SubElement(node, "loc").text = config.SITE_URL + article.url
        ET.SubElement(node, "lastmod").text = (article.updated or article.published).isoformat()

    return XML_HEADER + ET.tostring(urlset, encoding="unicode")


def build_robots() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {config.SITE_URL}/sitemap.xml\n"
    )
