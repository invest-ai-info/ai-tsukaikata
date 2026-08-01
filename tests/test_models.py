# -*- coding: utf-8 -*-
import dataclasses
import json
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


def test_roundtrip_through_json():
    u = _update()
    restored = Update.from_dict(json.loads(json.dumps(u.to_dict())))
    assert restored == u
    assert restored.published.tzinfo is not None


def test_published_must_be_timezone_aware():
    with pytest.raises(ValueError):
        _update(published=datetime(2026, 8, 1, 12, 0))


def test_update_is_immutable():
    u = _update()
    with pytest.raises(dataclasses.FrozenInstanceError):
        u.title = "changed"


def test_summary_at_exact_limit_is_untouched():
    text = "あ" * SUMMARY_MAX_CHARS
    assert _update(summary=text).summary == text


def test_summary_one_over_limit_is_clipped_to_limit():
    u = _update(summary="あ" * (SUMMARY_MAX_CHARS + 1))
    assert len(u.summary) == SUMMARY_MAX_CHARS
    assert u.summary.endswith("…")


def test_clip_summary_handles_none():
    assert clip_summary(None) == ""


def test_make_uid_returns_16_lowercase_hex_chars():
    uid = make_uid("s1", "e1")
    assert len(uid) == 16
    assert all(c in "0123456789abcdef" for c in uid)
