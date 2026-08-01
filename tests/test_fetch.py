# -*- coding: utf-8 -*-
from datetime import timezone
from pathlib import Path

from tracker.fetch import load_sources, parse_feed, parse_huggingface

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
