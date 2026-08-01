# -*- coding: utf-8 -*-
"""Article のリストを {出力パス: HTML} にする。ファイルは書かない。

autoescape を有効にしてあるので、記事タイトルにHTMLが混ざっても
そのままタグとして解釈されることはない。本文だけは Markdown 変換済みの
信頼できるHTMLなので | safe を通す。
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import config
from .content import Article

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def jp_date(value: date) -> str:
    """2026年8月1日 の形にする。strftime の %-m は Windows で使えないため自前で組む。"""
    return f"{value.year}年{value.month}月{value.day}日"


def build_env(templates_dir: Path = TEMPLATES_DIR) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir), encoding="utf-8"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["jp_date"] = jp_date
    env.globals["site"] = {
        "name": config.SITE_NAME,
        "url": config.SITE_URL,
        "description": config.SITE_DESCRIPTION,
        "lang": config.SITE_LANG,
    }
    return env


def render_site(articles: list[Article], env: Environment | None = None) -> dict[str, str]:
    """全ページを組み立てる。キーは build/ からの相対パス。"""
    env = env or build_env()

    listed = [a for a in articles if a.category in config.LISTED_CATEGORIES]
    active = [
        name for name in config.LISTED_CATEGORIES
        if any(a.category == name for a in listed)
    ]
    # 記事が1本もないカテゴリはナビにも一覧にも出さない（空ページを作らない）
    env.globals["nav"] = [
        {"url": f"/{name}/", "label": config.CATEGORIES[name]["label"]} for name in active
    ]

    pages: dict[str, str] = {}

    pages["index.html"] = env.get_template("index.html").render(
        page_title=None,
        description=config.SITE_DESCRIPTION,
        canonical=f"{config.SITE_URL}/",
        og_type="website",
        articles=listed[: config.INDEX_MAX_ARTICLES],
    )

    for name in active:
        meta = config.CATEGORIES[name]
        pages[f"{name}/index.html"] = env.get_template("list.html").render(
            page_title=meta["label"],
            description=meta["description"],
            canonical=f"{config.SITE_URL}/{name}/",
            og_type="website",
            category_label=meta["label"],
            articles=[a for a in listed if a.category == name],
        )

    article_template = env.get_template("article.html")
    for article in articles:
        meta = config.CATEGORIES[article.category]
        pages[article.output_path] = article_template.render(
            page_title=article.title,
            description=article.description,
            canonical=config.SITE_URL + article.url,
            og_type="article",
            article=article,
            category_label=meta["label"] or None,
            category_url=f"/{article.category}/",
        )

    return pages
