# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta, timezone

from tracker.models import Update
from tracker.store import (
    dead_sources,
    empty_state,
    load_state,
    mark_seen,
    prune,
    queue_minor,
    record_result,
    save_state,
    select_unseen,
    take_pending_minor,
)

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _update(uid, title="t"):
    return Update(
        uid=uid, source_id="s", vendor="V", label="L",
        title=title, url="https://example.com/x", published=NOW, summary="",
    )


def test_load_state_returns_empty_when_file_missing(tmp_path):
    state = load_state(tmp_path / "nope.json")
    assert state == empty_state()


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "sub" / "seen.json"
    state = empty_state()
    state["uids"]["abc"] = NOW.isoformat()
    save_state(path, state)
    assert load_state(path) == state


def test_save_state_creates_parent_directory(tmp_path):
    path = tmp_path / "deep" / "nested" / "seen.json"
    save_state(path, empty_state())
    assert path.exists()


def test_select_unseen_filters_known_uids():
    state = empty_state()
    state["uids"]["known"] = NOW.isoformat()
    result = select_unseen(state, [_update("known"), _update("fresh")])
    assert [u.uid for u in result] == ["fresh"]


def test_mark_seen_records_uids():
    state = empty_state()
    mark_seen(state, [_update("a"), _update("b")], NOW)
    assert set(state["uids"]) == {"a", "b"}


def test_mark_seen_does_not_overwrite_existing_timestamp():
    state = empty_state()
    earlier = (NOW - timedelta(days=5)).isoformat()
    state["uids"]["a"] = earlier
    mark_seen(state, [_update("a")], NOW)
    assert state["uids"]["a"] == earlier


def test_queue_minor_then_take_returns_and_clears():
    state = empty_state()
    queue_minor(state, [_update("a"), _update("b")])
    taken = take_pending_minor(state)
    assert [u.uid for u in taken] == ["a", "b"]
    assert state["pending_minor"] == []


def test_take_pending_minor_on_empty_returns_empty():
    assert take_pending_minor(empty_state()) == []


def test_record_result_success_clears_failures():
    state = empty_state()
    record_result(state, "s1", "Timeout", 0)
    record_result(state, "s1", None, 3)
    assert "s1" not in state["failures"]


def test_record_result_counts_zero_result_as_failure():
    state = empty_state()
    record_result(state, "s1", None, 0)
    assert state["failures"]["s1"]["count"] == 1
    assert state["failures"]["s1"]["last_error"] == "0件"


def test_dead_sources_requires_three_consecutive_failures():
    state = empty_state()
    for _ in range(2):
        record_result(state, "s1", "Timeout", 0)
    assert dead_sources(state) == []
    record_result(state, "s1", "Timeout", 0)
    assert dead_sources(state) == [("s1", 3, "Timeout")]


def test_prune_removes_entries_older_than_retention():
    state = empty_state()
    state["uids"]["old"] = (NOW - timedelta(days=91)).isoformat()
    state["uids"]["fresh"] = (NOW - timedelta(days=1)).isoformat()
    removed = prune(state, NOW)
    assert removed == 1
    assert set(state["uids"]) == {"fresh"}


def test_prune_removes_unparseable_timestamps():
    state = empty_state()
    state["uids"]["broken"] = "not-a-date"
    assert prune(state, NOW) == 1
    assert state["uids"] == {}


def test_state_file_is_human_readable_json(tmp_path):
    path = tmp_path / "seen.json"
    state = empty_state()
    state["uids"]["a"] = NOW.isoformat()
    save_state(path, state)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["uids"]["a"] == NOW.isoformat()
