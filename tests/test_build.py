# -*- coding: utf-8 -*-
from pathlib import Path

from src import build

# レシピには密度の下限（指示文6個・図1枚・内部リンク1本・本文1800字）が
# かかるので、擬似記事もそれを満たす形にしてある。ここを薄くすると
# ビルドが正しく止まり、他の検査のテストが道連れになる。
_PROMPTS = '<div class="prompt">指示文です</div>\n' * 6
_FIGURE = (
    '<figure class="figure">'
    '<img src="/static/images/hero.svg" alt="読み上げでも意味が通る説明">'
    "</figure>"
)

RECIPE = f"""---
title: テスト記事
description: これはテストです。
category: recipes
published: 2026-08-01
time_required: 30分
cost: 無料
---

{_PROMPTS}
{_FIGURE}

[別の記事](/recipes/sample/)も見てください。

{"本文です。" * 400}
"""


def _content_dir(tmp_path: Path, text: str = RECIPE) -> Path:
    content = tmp_path / "content" / "recipes"
    content.mkdir(parents=True)
    (content / "sample.md").write_text(text, encoding="utf-8")
    return tmp_path / "content"


def test_collect_returns_all_expected_files(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path))
    assert errors == []
    assert set(files) >= {
        "index.html",
        "recipes/index.html",
        "recipes/sample/index.html",
        "feed.xml",
        "sitemap.xml",
        "robots.txt",
        "CNAME",
    }


def test_collect_writes_cname_for_custom_domain(tmp_path):
    files, _ = build.collect(_content_dir(tmp_path))
    assert files["CNAME"].strip() == "ai-tsukaikata.com"


def test_collect_returns_errors_and_no_files_when_invalid(tmp_path):
    broken = RECIPE.replace("本文です。", r"作業場所は C:\Users\taro です。")
    files, errors = build.collect(_content_dir(tmp_path, broken))
    assert files == {}
    assert len(errors) == 1


def test_collect_reports_unreadable_article(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path, "frontmatterがない"))
    assert files == {}
    assert any("frontmatter" in error for error in errors)


def test_static_paths_lists_files_as_urls(tmp_path):
    static = tmp_path / "static"
    (static / "images").mkdir(parents=True)
    (static / "style.css").write_text("body{}", encoding="utf-8")
    (static / "images" / "a.svg").write_text("<svg/>", encoding="utf-8")
    assert build.static_paths(static) == {"/static/style.css", "/static/images/a.svg"}


def test_static_paths_on_missing_directory_is_empty(tmp_path):
    assert build.static_paths(tmp_path / "nope") == set()


def test_collect_rejects_article_pointing_at_missing_image(tmp_path):
    body = '<img src="/static/images/nothing.svg" alt="無い画像">'
    files, errors = build.collect(_content_dir(tmp_path, RECIPE + body + "\n"))
    assert files == {}
    assert any("画像" in error for error in errors)


def test_write_creates_directory_structure(tmp_path):
    build_dir = tmp_path / "build"
    build.write({"recipes/sample/index.html": "<p>x</p>"}, build_dir, tmp_path / "missing-static")
    assert (build_dir / "recipes" / "sample" / "index.html").read_text(encoding="utf-8") == "<p>x</p>"


def test_write_copies_static_directory(tmp_path):
    static = tmp_path / "static"
    static.mkdir()
    (static / "style.css").write_text("body{}", encoding="utf-8")
    build_dir = tmp_path / "build"
    build.write({"index.html": "<p>x</p>"}, build_dir, static)
    assert (build_dir / "static" / "style.css").read_text(encoding="utf-8") == "body{}"


def test_write_clears_previous_output(tmp_path):
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "stale.html").write_text("古い", encoding="utf-8")
    build.write({"index.html": "<p>x</p>"}, build_dir, tmp_path / "missing-static")
    assert not (build_dir / "stale.html").exists()


def test_main_writes_nothing_when_validation_fails(tmp_path, monkeypatch, capsys):
    broken = RECIPE.replace("本文です。", r"作業場所は C:\Users\taro です。")
    build_dir = tmp_path / "build"
    monkeypatch.setattr(build, "CONTENT_DIR", _content_dir(tmp_path, broken))
    monkeypatch.setattr(build, "BUILD_DIR", build_dir)

    assert build.main() == 1
    assert not build_dir.exists()
    assert "ビルド中止" in capsys.readouterr().err


def test_main_builds_successfully(tmp_path, monkeypatch):
    build_dir = tmp_path / "build"
    monkeypatch.setattr(build, "CONTENT_DIR", _content_dir(tmp_path))
    monkeypatch.setattr(build, "BUILD_DIR", build_dir)

    assert build.main() == 0
    assert (build_dir / "index.html").exists()
    assert (build_dir / "static" / "style.css").exists()


import json

NEWS_ITEM = {
    "uid": "n1", "source_id": "openai-news",
    "title": "ニューステスト", "url": "https://example.com/post",
    "vendor": "OpenAI", "label": "OpenAI News", "importance": "minor",
    "published": "2026-08-04T19:00:00+00:00", "summary_ja": "要約です",
}

SOURCES_YML = """\
sources:
  - id: openai-news
    vendor: OpenAI
    label: OpenAI News
    type: rss
    url: https://example.com/rss
"""


def _news_files(tmp_path: Path, items=None) -> tuple[Path, Path]:
    news_path = tmp_path / "news.json"
    news_path.write_text(
        json.dumps({"items": items if items is not None else [NEWS_ITEM]}, ensure_ascii=False),
        encoding="utf-8",
    )
    sources_path = tmp_path / "sources.yml"
    sources_path.write_text(SOURCES_YML, encoding="utf-8")
    return news_path, sources_path


def test_collect_with_news_renders_top_and_archive(tmp_path):
    news_path, sources_path = _news_files(tmp_path)
    files, errors = build.collect(
        _content_dir(tmp_path), news_path=news_path, sources_path=sources_path
    )
    assert errors == []
    assert "ニューステスト" in files["index.html"]
    assert "news/index.html" in files
    assert "https://ai-tsukaikata.com/news/</loc>" in files["sitemap.xml"]


def test_collect_with_broken_news_stops_build(tmp_path):
    news_path, sources_path = _news_files(tmp_path)
    news_path.write_text("{壊れている", encoding="utf-8")
    files, errors = build.collect(
        _content_dir(tmp_path), news_path=news_path, sources_path=sources_path
    )
    assert files == {}
    assert any("news.json" in error or "読めません" in error for error in errors)


def test_collect_without_news_paths_keeps_old_behavior(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path))
    assert errors == []
    assert "news/index.html" in files  # 既定は本物の data/tracker/news.json を読む
