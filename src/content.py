# -*- coding: utf-8 -*-
"""content/ の Markdown を読んで Article にする。

テンプレートもHTMLの組み立ても知らない。ここが知っているのは
「frontmatter付きMarkdownという入力形式」だけ。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml

from .config import CATEGORIES, SCENES

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

REQUIRED_FIELDS = ("title", "description", "category", "published")
RECIPE_REQUIRED_FIELDS = ("time_required", "cost")
MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "sane_lists", "attr_list"]


class ArticleError(Exception):
    """記事1本を Article にできないときに投げる。"""


@dataclass(frozen=True)
class Article:
    slug: str
    title: str
    description: str
    category: str
    published: date
    updated: date | None
    tags: tuple[str, ...]
    time_required: str | None
    cost: str | None
    body_html: str
    source_path: Path
    scene: str | None = None
    # 外部の公式ページを見て書いた記事が「いつ時点の話か」。
    # ⚠️ 古いことでビルドは止めない（週次の check_freshness.py が見る）。
    checked: date | None = None
    # 連載（2026-08-25 デザイン承認・提案A）。series が同じ記事は series_no で
    # つながり、カードに札・記事に連載帯と前後ナビが付く
    series: str | None = None
    series_no: int | None = None
    series_total: int | None = None

    @property
    def url(self) -> str:
        """公開URL。末尾スラッシュ形式に統一する。"""
        if self.category == "pages":
            return f"/{self.slug}/"
        return f"/{self.category}/{self.slug}/"

    @property
    def output_path(self) -> str:
        return self.url.strip("/") + "/index.html"


def split_frontmatter(text: str) -> tuple[dict, str]:
    """先頭の --- で囲まれたYAMLと本文に分ける。"""
    match = FRONTMATTER_RE.match(text.lstrip("﻿"))
    if not match:
        raise ArticleError("先頭に --- で囲まれた frontmatter がありません")
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise ArticleError(f"frontmatter のYAMLが壊れています: {error}") from error
    if not isinstance(meta, dict):
        raise ArticleError("frontmatter が「項目: 値」の形になっていません")
    return meta, match.group(2)


def render_markdown(body: str) -> str:
    return markdown.markdown(body, extensions=MARKDOWN_EXTENSIONS, output_format="html")


def _to_date(value, field: str) -> date:
    """PyYAML が日付として解釈した値だけを受け付ける。

    クォートで囲むと文字列になり、ここで落ちる。日付形式の揺れを
    frontmatter の時点で1つに固定するため。
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise ArticleError(f"{field} は YYYY-MM-DD 形式で書いてください（今の値: {value!r}）")


def parse_article(source_path: Path, text: str) -> Article:
    """Markdown 1本を Article にする。ディスクには触らない。"""
    source_path = Path(source_path)
    slug = source_path.stem
    if not SLUG_RE.match(slug):
        raise ArticleError(
            f"ファイル名は半角小文字・数字・ハイフンだけにしてください（URLになります）: {slug}"
        )

    meta, body = split_frontmatter(text)

    missing = [field for field in REQUIRED_FIELDS if not meta.get(field)]
    if missing:
        raise ArticleError("必須項目がありません: " + ", ".join(missing))

    category = str(meta["category"])
    if category not in CATEGORIES:
        raise ArticleError(
            f"知らないカテゴリです: {category}（{' / '.join(CATEGORIES)} のいずれか）"
        )

    if category == "recipes":
        missing = [field for field in RECIPE_REQUIRED_FIELDS if not meta.get(field)]
        if missing:
            raise ArticleError("レシピの必須項目がありません: " + ", ".join(missing))

    tags = meta.get("tags") or []
    if not isinstance(tags, list):
        raise ArticleError("tags は [A, B] のリスト形式で書いてください")

    # 場面は付け忘れても落とさない（固定ページには要らない）。ただし知らない値は
    # 落とす——誤字を許すと、その記事だけどの場面にも出ない静かな欠落になる
    scene = meta.get("scene")
    if scene is not None:
        scene = str(scene)
        if scene not in SCENES:
            raise ArticleError(
                f"知らない場面です: {scene}（{' / '.join(SCENES)} のいずれか）"
            )

    # 連載。series を書いたら series_no（1始まりの整数）も必須——番号の無い
    # 連載札は表示が壊れるので、片方だけの状態をここで止める
    series = str(meta["series"]) if meta.get("series") else None
    series_no = meta.get("series_no")
    series_total = meta.get("series_total")
    if series is not None:
        if not isinstance(series_no, int) or isinstance(series_no, bool) or series_no < 1:
            raise ArticleError(
                f"series を書いたら series_no（1以上の整数）も必須です（今の値: {series_no!r}）"
            )
    elif series_no is not None:
        raise ArticleError("series_no だけがあります。連載なら series（連載名）も書いてください")
    if series_total is not None and (
        not isinstance(series_total, int) or isinstance(series_total, bool) or series_total < 1
    ):
        raise ArticleError(f"series_total は1以上の整数で書いてください（今の値: {series_total!r}）")

    return Article(
        slug=slug,
        title=str(meta["title"]),
        description=str(meta["description"]),
        category=category,
        published=_to_date(meta["published"], "published"),
        updated=_to_date(meta["updated"], "updated") if meta.get("updated") else None,
        tags=tuple(str(tag) for tag in tags),
        time_required=str(meta["time_required"]) if meta.get("time_required") else None,
        cost=str(meta["cost"]) if meta.get("cost") else None,
        body_html=render_markdown(body),
        source_path=source_path,
        scene=scene,
        checked=_to_date(meta["checked"], "checked") if meta.get("checked") else None,
        series=series,
        series_no=series_no if series else None,
        series_total=series_total if series else None,
    )


def load_articles(content_dir: Path) -> tuple[list[Article], list[str]]:
    """content/ 以下を全部読む。

    1本壊れていても止めずに最後まで読み、エラーを集めて返す。
    直して再実行、を1往復で済ませるため。
    """
    articles: list[Article] = []
    errors: list[str] = []
    for path in sorted(Path(content_dir).rglob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            articles.append(parse_article(path, path.read_text(encoding="utf-8")))
        except ArticleError as error:
            errors.append(f"{path}: {error}")
    articles.sort(key=lambda article: (article.published, article.slug), reverse=True)
    return articles, errors
