# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

from src import news

SOURCES_YML = """\
sources:
  - id: openai-news
    vendor: OpenAI
    label: OpenAI News
    type: rss
    url: https://example.com/rss
  - id: claude-code
    vendor: Anthropic
    label: Claude Code
    type: github_releases
    url: https://example.com/releases.atom
"""


def _item(uid="a1", source_id="openai-news", title="題", published="2026-08-04T19:00:00+00:00", **kwargs):
    base = {
        "uid": uid,
        "source_id": source_id,
        "title": title,
        "url": "https://example.com/post",
        "vendor": "OpenAI",
        "label": "OpenAI News",
        "importance": "minor",
        "published": published,
        "summary_ja": None,
    }
    base.update(kwargs)
    return base


def _write(tmp_path: Path, items) -> tuple[Path, Path]:
    news_path = tmp_path / "news.json"
    news_path.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")
    sources_path = tmp_path / "sources.yml"
    sources_path.write_text(SOURCES_YML, encoding="utf-8")
    return news_path, sources_path


def test_load_source_types_maps_id_to_type(tmp_path):
    _, sources_path = _write(tmp_path, [])
    assert news.load_source_types(sources_path) == {
        "openai-news": "rss",
        "claude-code": "github_releases",
    }


def test_load_news_returns_items_new_to_old_in_jst(tmp_path):
    news_path, _ = _write(tmp_path, [
        _item(uid="old", published="2026-08-03T15:00:00+00:00"),
        _item(uid="new", published="2026-08-04T19:00:00+00:00"),
    ])
    items = news.load_news(news_path)
    assert [i.uid for i in items] == ["new", "old"]
    # 2026-08-04T19:00Z は JST では 8月5日 4:00
    assert items[0].published.date().isoformat() == "2026-08-05"


def test_load_news_missing_file_raises(tmp_path):
    with pytest.raises(news.NewsError):
        news.load_news(tmp_path / "nothing.json")


def test_load_news_broken_json_raises(tmp_path):
    path = tmp_path / "news.json"
    path.write_text("{壊れている", encoding="utf-8")
    with pytest.raises(news.NewsError):
        news.load_news(path)


def test_load_news_item_without_required_key_raises(tmp_path):
    item = _item()
    del item["published"]
    news_path, _ = _write(tmp_path, [item])
    with pytest.raises(news.NewsError):
        news.load_news(news_path)


def test_load_source_types_broken_yaml_raises(tmp_path):
    path = tmp_path / "sources.yml"
    path.write_text("sources: [壊れ", encoding="utf-8")
    with pytest.raises(news.NewsError):
        news.load_source_types(path)
