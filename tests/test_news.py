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


SOURCE_TYPES = {"openai-news": "rss", "claude-code": "github_releases"}


def _loaded(tmp_path, items):
    news_path, _ = _write(tmp_path, items)
    return news.load_news(news_path)


def test_split_recent_separates_announcements_and_models(tmp_path):
    items = _loaded(tmp_path, [
        _item(uid="a", source_id="openai-news", published="2026-08-04T19:00:00+00:00",
              summary_ja="1行目\n2行目\n3行目"),
        _item(uid="m1", source_id="claude-code", title="v2.1.222",
              vendor="Anthropic", label="Claude Code",
              published="2026-08-04T22:00:00+00:00"),
        _item(uid="m2", source_id="claude-code", title="v2.1.223",
              vendor="Anthropic", label="Claude Code",
              published="2026-08-06T00:00:00+00:00"),
    ])
    top = news.split_recent(items, SOURCE_TYPES)
    assert [i.uid for i in top["announcements"]] == ["a"]
    assert len(top["model_groups"]) == 1
    group = top["model_groups"][0]
    assert group["label"] == "Claude Code"
    assert group["count"] == 2
    assert group["latest_title"] == "v2.1.223"


def test_split_recent_limits_announcements(tmp_path):
    items = _loaded(tmp_path, [
        _item(uid=f"a{i}", published=f"2026-08-{i:02d}T00:00:00+00:00")
        for i in range(1, 14)
    ])
    top = news.split_recent(items, SOURCE_TYPES, limit=10)
    assert len(top["announcements"]) == 10
    assert top["announcements"][0].uid == "a13"


def test_split_recent_model_window_follows_shown_announcements(tmp_path):
    # 表示中お知らせの最古（8/2）より前のモデル（8/1）は畳みに入らない
    items = _loaded(tmp_path, [
        _item(uid="a1", published="2026-08-02T00:00:00+00:00"),
        _item(uid="a2", published="2026-08-05T00:00:00+00:00"),
        _item(uid="m-in", source_id="claude-code", label="Claude Code",
              published="2026-08-03T00:00:00+00:00"),
        _item(uid="m-out", source_id="claude-code", label="Claude Code",
              published="2026-08-01T00:00:00+00:00"),
    ])
    top = news.split_recent(items, SOURCE_TYPES)
    assert top["model_groups"][0]["count"] == 1


def test_split_recent_unknown_source_counts_as_announcement(tmp_path):
    items = _loaded(tmp_path, [_item(uid="x", source_id="retired-source")])
    top = news.split_recent(items, SOURCE_TYPES)
    assert [i.uid for i in top["announcements"]] == ["x"]


def test_split_recent_empty_is_harmless(tmp_path):
    top = news.split_recent([], SOURCE_TYPES)
    assert top == {"announcements": [], "model_groups": []}


def test_group_by_month_labels_in_japanese(tmp_path):
    items = _loaded(tmp_path, [
        _item(uid="jul", published="2026-07-10T00:00:00+00:00"),
        _item(uid="aug", published="2026-08-04T19:00:00+00:00"),
    ])
    months = news.group_by_month(items)
    assert [label for label, _ in months] == ["2026年8月", "2026年7月"]
    assert [i.uid for i in months[0][1]] == ["aug"]
