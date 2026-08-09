# -*- coding: utf-8 -*-
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from check_freshness import check_articles, external_links  # noqa: E402

from src.content import Article, render_markdown  # noqa: E402

TODAY = date(2026, 8, 9)


def _article(body, checked=None, slug="start"):
    return Article(
        slug=slug, title="題", description="説明", category="pages",
        published=date(2026, 8, 1), updated=None, tags=(),
        time_required=None, cost=None,
        body_html=render_markdown(body),
        source_path=Path(f"content/pages/{slug}.md"),
        checked=checked,
    )


def _ok(url):
    return 200


def test_external_links_are_found_once_each():
    body = "[A](https://example.com/a) [again](https://example.com/a) [B](https://example.com/b)"
    links = external_links(render_markdown(body))
    assert links == ["https://example.com/a", "https://example.com/b"]


def test_internal_links_are_not_external():
    assert external_links(render_markdown("[中](/recipes/x/)")) == []


def test_article_with_external_links_but_no_checked_is_reported():
    """付け忘れの網。ビルドでは止めないので、ここで拾わないと静かに漏れる。"""
    article = _article("[公式](https://example.com/a)", checked=None)
    problems = check_articles([article], TODAY, head=_ok)
    assert any("checked" in p for p in problems)


def test_link_to_our_own_repo_does_not_require_checked():
    """自分のリポジトリへのリンクは、日付を付けても意味がない。
    永久に消えない警告は、一覧そのものを読まれなくする。"""
    article = _article("[このサイトの中身](https://github.com/invest-ai-info/ai-tsukaikata)")
    assert check_articles([article], TODAY, head=_ok) == []


def test_our_own_broken_link_is_still_reported():
    """checked を求めないだけで、死活の検査からは外さない。"""
    article = _article("[このサイトの中身](https://github.com/invest-ai-info/ai-tsukaikata)")
    problems = check_articles([article], TODAY, head=lambda url: 404)
    assert any("404" in p for p in problems)


def test_fresh_checked_date_is_quiet():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    assert check_articles([article], TODAY, head=_ok) == []


def test_old_checked_date_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 1, 1))
    problems = check_articles([article], TODAY, head=_ok)
    assert any("確認日" in p for p in problems)


def test_dead_link_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles([article], TODAY, head=lambda url: 404)
    assert any("404" in p for p in problems)


def test_unreachable_link_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles([article], TODAY, head=lambda url: None)
    assert any("開けません" in p for p in problems)


def test_article_without_external_links_and_without_checked_is_quiet():
    """既存記事の大半がこれ。ここで鳴ると一覧が読まれなくなる。"""
    assert check_articles([_article("ふつうの本文")], TODAY, head=_ok) == []
