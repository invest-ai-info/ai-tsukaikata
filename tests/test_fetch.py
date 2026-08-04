# -*- coding: utf-8 -*-
import re
from datetime import timedelta, timezone
from pathlib import Path

import pytest

from tracker.fetch import (
    _to_utc,
    fetch_source,
    load_sources,
    parse_anthropic_news,
    parse_feed,
    parse_huggingface,
    parse_openrouter,
)

FIXTURES = Path(__file__).parent / "fixtures"

RSS_SOURCE = {"id": "sample", "vendor": "Sample", "label": "Sample News", "type": "rss"}
GH_SOURCE = {"id": "gh", "vendor": "GitHub", "label": "Repo", "type": "github_releases"}
HF_SOURCE = {"id": "hf", "vendor": "DeepSeek", "label": "DeepSeek", "type": "huggingface"}


def _read(name):
    return (FIXTURES / name).read_bytes()


def test_parse_feed_reads_entries():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert [u.title for u in updates] == ["Introducing a new model", "Weekly notes"]


def test_parse_feed_skips_entry_without_link():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert all(u.url for u in updates)
    assert len(updates) == 2


def test_parse_feed_normalizes_to_utc():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert updates[0].published.tzinfo is not None
    assert updates[0].published.utcoffset() == timezone.utc.utcoffset(None)


def test_parse_feed_strips_html_from_summary():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert updates[0].summary == "We are excited to share this."


def test_parse_feed_uids_are_source_scoped():
    a = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    other = dict(RSS_SOURCE, id="different")
    b = parse_feed(other, _read("sample_rss.xml"))
    assert a[0].uid != b[0].uid


def test_parse_atom_releases():
    updates = parse_feed(GH_SOURCE, _read("sample_releases.atom"))
    assert [u.title for u in updates] == ["v1.2.0", "v1.1.3"]
    assert updates[0].url == "https://github.com/o/r/releases/tag/v1.2.0"


def test_parse_huggingface_builds_model_url():
    updates = parse_huggingface(HF_SOURCE, _read("sample_hf_models.json"))
    assert updates[0].title == "deepseek-ai/DeepSeek-V4-Flash-0731"
    assert updates[0].url == "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731"


def test_parse_huggingface_skips_entry_without_model_id():
    updates = parse_huggingface(HF_SOURCE, _read("sample_hf_models.json"))
    assert len(updates) == 2


def test_parse_huggingface_skips_entry_without_created_at():
    updates = parse_huggingface(HF_SOURCE, _read("sample_hf_models.json"))
    assert "deepseek-ai/NoDateModel" not in [u.title for u in updates]


def test_parse_feed_on_garbage_returns_empty_without_raising():
    assert parse_feed(RSS_SOURCE, b"not a feed at all") == []


def test_load_sources(tmp_path):
    path = tmp_path / "sources.yml"
    path.write_text(
        "sources:\n"
        "  - id: a\n"
        "    vendor: V\n"
        "    label: L\n"
        "    type: rss\n"
        "    url: https://example.com/feed\n",
        encoding="utf-8",
    )
    sources = load_sources(path)
    assert sources[0]["id"] == "a"


def test_fetch_source_parses_rss_and_reports_no_error(monkeypatch):
    captured = {}

    def fake_get(url):
        captured["url"] = url
        return _read("sample_rss.xml")

    monkeypatch.setattr("tracker.fetch._http_get", fake_get)
    updates, error = fetch_source(dict(RSS_SOURCE, url="https://example.com/feed"))
    assert error is None
    assert captured["url"] == "https://example.com/feed"
    assert len(updates) == 2


def test_fetch_source_builds_huggingface_api_url(monkeypatch):
    captured = {}

    def fake_get(url):
        captured["url"] = url
        return _read("sample_hf_models.json")

    monkeypatch.setattr("tracker.fetch._http_get", fake_get)
    updates, error = fetch_source(dict(HF_SOURCE, org="deepseek-ai"))
    assert error is None
    assert "author=deepseek-ai" in captured["url"]
    assert "sort=createdAt" in captured["url"]
    assert "direction=-1" in captured["url"]
    assert len(updates) == 2


def test_fetch_source_returns_error_string_instead_of_raising(monkeypatch):
    def boom(url):
        raise OSError("connection reset by peer")

    monkeypatch.setattr("tracker.fetch._http_get", boom)
    updates, error = fetch_source(dict(RSS_SOURCE, url="https://example.com/feed"))
    assert updates == []
    assert error.startswith("OSError: ")
    assert "connection reset by peer" in error


def test_fetch_source_missing_org_degrades_to_recorded_error(monkeypatch):
    # sources.yml の書き間違いでクラッシュせず、死活記録に落ちることを保証する。
    monkeypatch.setattr("tracker.fetch._http_get", lambda url: b"[]")
    updates, error = fetch_source(HF_SOURCE)
    assert updates == []
    assert "KeyError" in error


def test_fetch_source_truncates_long_error_messages(monkeypatch):
    def boom(url):
        raise OSError("x" * 500)

    monkeypatch.setattr("tracker.fetch._http_get", boom)
    _, error = fetch_source(dict(RSS_SOURCE, url="https://example.com/feed"))
    assert error.startswith("OSError: ")
    assert len(error) < 100


@pytest.mark.parametrize("value,expected_hour", [
    ("Fri, 01 Aug 2026 09:00:00 GMT", 9),
    ("Fri, 01 Aug 2026 09:00:00 +0900", 0),
    ("Fri, 01 Aug 2026 09:00:00 +0800", 1),
    ("2026-08-01T10:00:00Z", 10),
    ("2026-07-31T04:05:06.000Z", 4),
])
def test_to_utc_handles_real_world_formats(value, expected_hour):
    result = _to_utc(value)
    assert result is not None
    assert result.utcoffset() == timedelta(0)
    assert result.hour == expected_hour


@pytest.mark.parametrize("value", ["", "not a date", "2026-13-45T99:99:99Z"])
def test_to_utc_returns_none_for_unparseable(value):
    assert _to_utc(value) is None


OR_SOURCE = {"id": "or", "vendor": "xAI", "label": "Grok 新モデル",
             "type": "openrouter", "org": "x-ai"}


def test_parse_openrouter_filters_by_org_prefix():
    updates = parse_openrouter(OR_SOURCE, _read("sample_openrouter.json"))
    assert all(u.title.startswith("x-ai/") for u in updates)
    assert "anthropic/claude-opus-5" not in [u.title for u in updates]


def test_parse_openrouter_converts_unix_timestamp():
    updates = parse_openrouter(OR_SOURCE, _read("sample_openrouter.json"))
    published = {u.title: u.published for u in updates}
    assert published["x-ai/grok-4.5"].year == 2026
    assert published["x-ai/grok-4.5"].tzinfo is not None
    assert published["x-ai/grok-4.5"].utcoffset() == timedelta(0)


def test_parse_openrouter_sorts_newest_first():
    updates = parse_openrouter(OR_SOURCE, _read("sample_openrouter.json"))
    assert updates[0].title == "x-ai/grok-4.5:free"


def test_parse_openrouter_skips_entry_without_created():
    updates = parse_openrouter(OR_SOURCE, _read("sample_openrouter.json"))
    assert "x-ai/no-timestamp" not in [u.title for u in updates]


NEWS_SOURCE = {"id": "anthropic-news", "vendor": "Anthropic",
               "label": "Anthropic 公式ニュース", "type": "anthropic_news"}


def _news():
    return parse_anthropic_news(NEWS_SOURCE, _read("sample_anthropic_news.html"))


def test_parse_anthropic_news_reads_items_newest_first():
    assert [u.title for u in _news()] == [
        "Introducing Thing",
        "Investigating three real-world incidents",
        "We’re inviting hard questions",
        'The "best" model yet',
    ]


def test_parse_anthropic_news_builds_article_urls():
    assert _news()[0].url == "https://www.anthropic.com/news/introducing-thing"


def test_parse_anthropic_news_dedupes_by_slug():
    # 同じ記事が「注目」と一覧の両方に埋め込まれるため、実物でも重複する。
    assert len([u for u in _news() if u.url.endswith("/introducing-thing")]) == 1


def test_parse_anthropic_news_keeps_non_ascii_intact():
    # unicode_escape で復号すると "We’re" が "Weâ€™re" に化ける。json で復号すること。
    titles = [u.title for u in _news()]
    assert "We’re inviting hard questions" in titles
    assert not any("â" in t for t in titles)


def test_parse_anthropic_news_unescapes_quotes_in_title_and_summary():
    item = next(u for u in _news() if u.url.endswith("/quoted-title-post"))
    assert item.title == 'The "best" model yet'
    assert item.summary == 'He said "hello" loudly.'


def test_parse_anthropic_news_null_summary_becomes_empty():
    item = next(u for u in _news() if u.url.endswith("/no-summary-post"))
    assert item.summary == ""


def test_parse_anthropic_news_published_is_utc_aware():
    published = _news()[0].published
    assert published.tzinfo is not None
    assert published.utcoffset() == timedelta(0)
    assert (published.year, published.month, published.day) == (2026, 8, 1)


def test_parse_anthropic_news_raises_when_payload_is_gone():
    # 見た目のマークアップは残したまま、埋め込みデータだけ消えた状態。
    # CSSクラス名を頼りに拾っていたら、ここで「1件取れた」ことになってしまう。
    # ハッシュ付きクラス名はビルドごとに変わるので、拾ってはいけない。
    html = _read("sample_anthropic_news.html")
    broken = re.sub(rb"<script>self\.__next_f.*?</script>", b"", html, flags=re.S)
    assert b"PublicationList-module" in broken  # 見た目側は残っている
    with pytest.raises(ValueError):
        parse_anthropic_news(NEWS_SOURCE, broken)


def test_fetch_source_records_structure_change_as_error(monkeypatch):
    # 静かに0件を返さず、死活記録に落ちること。3回続けばダイジェストに出る。
    monkeypatch.setattr("tracker.fetch._http_get", lambda url: b"<html></html>")
    updates, error = fetch_source(dict(NEWS_SOURCE, url="https://example.com/news"))
    assert updates == []
    assert "ValueError" in error


def test_parse_openrouter_builds_model_url():
    updates = parse_openrouter(OR_SOURCE, _read("sample_openrouter.json"))
    by_title = {u.title: u.url for u in updates}
    assert by_title["x-ai/grok-4.5"] == "https://openrouter.ai/x-ai/grok-4.5"


def test_fetch_source_uses_openrouter_api(monkeypatch):
    captured = {}

    def fake_get(url):
        captured["url"] = url
        return _read("sample_openrouter.json")

    monkeypatch.setattr("tracker.fetch._http_get", fake_get)
    updates, error = fetch_source(OR_SOURCE)
    assert error is None
    assert captured["url"] == "https://openrouter.ai/api/v1/models"
    assert all(u.title.startswith("x-ai/") for u in updates)
