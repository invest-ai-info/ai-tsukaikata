# -*- coding: utf-8 -*-
from datetime import datetime, timezone

import pytest

from tracker.models import SUMMARY_MAX_CHARS, Update, clip_summary, make_uid

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _update(**kwargs):
    base = dict(
        uid="abc123",
        source_id="openai-news",
        vendor="OpenAI",
        label="OpenAI News",
        title="Introducing something",
        url="https://example.com/a",
        published=NOW,
        summary="短い要約",
    )
    base.update(kwargs)
    return Update(**base)


def test_make_uid_is_stable_and_source_scoped():
    assert make_uid("s1", "e1") == make_uid("s1", "e1")
    assert make_uid("s1", "e1") != make_uid("s2", "e1")


def test_clip_summary_strips_html_and_collapses_whitespace():
    assert clip_summary("<p>hello   <b>world</b></p>") == "hello world"


def test_clip_summary_unescapes_entities():
    assert clip_summary("A &amp; B") == "A & B"


def test_summary_is_clipped_to_limit():
    long_text = "あ" * 500
    u = _update(summary=long_text)
    assert len(u.summary) == SUMMARY_MAX_CHARS
    assert u.summary.endswith("…")


def test_short_summary_is_untouched():
    u = _update(summary="短い要約")
    assert u.summary == "短い要約"


def test_url_is_required():
    with pytest.raises(ValueError):
        _update(url="")


def test_importance_defaults_to_minor():
    assert _update().importance == "minor"


def test_with_importance_returns_new_object():
    u = _update()
    major = u.with_importance("major")
    assert major.importance == "major"
    assert u.importance == "minor"


def test_roundtrip_dict():
    u = _update()
    assert Update.from_dict(u.to_dict()) == u
