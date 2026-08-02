# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone

import pytest

from tracker.models import Update
from tracker.notify import MAX_ITEMS
from tracker.run import run_bootstrap, run_check, run_digest
from tracker.store import empty_state, load_state, save_state

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

SOURCES = [
    {"id": "s1", "vendor": "V", "label": "L", "type": "rss", "url": "https://x/f"},
]


def _update(uid, title):
    return Update(
        uid=uid, source_id="s1", vendor="V", label="L",
        title=title, url=f"https://example.com/{uid}", published=NOW, summary="",
    )


def _fetcher(updates, error=None):
    def fetch(source):
        return list(updates), error
    return fetch


class Mailer:
    def __init__(self):
        self.sent = []

    def __call__(self, subject, plain, html_body):
        self.sent.append(subject)


def _boom(subject, plain, html_body):
    raise RuntimeError("smtp down")


def test_check_sends_major_immediately(tmp_path):
    mailer = Mailer()
    run_check(
        sources=SOURCES,
        state_path=tmp_path / "seen.json",
        fetcher=_fetcher([_update("a", "Introducing X")]),
        mailer=mailer,
        now=NOW,
    )
    assert len(mailer.sent) == 1
    assert "重要" in mailer.sent[0]


def test_check_queues_minor_without_sending(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Weekly notes")]),
        mailer=mailer, now=NOW,
    )
    assert mailer.sent == []
    assert len(load_state(path)["pending_minor"]) == 1


def test_check_does_not_notify_twice(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    fetcher = _fetcher([_update("a", "Introducing X")])
    run_check(sources=SOURCES, state_path=path, fetcher=fetcher, mailer=mailer, now=NOW)
    run_check(sources=SOURCES, state_path=path, fetcher=fetcher, mailer=mailer, now=NOW)
    assert len(mailer.sent) == 1


def test_check_sends_nothing_when_no_updates(tmp_path):
    mailer = Mailer()
    run_check(
        sources=SOURCES, state_path=tmp_path / "seen.json",
        fetcher=_fetcher([]), mailer=mailer, now=NOW,
    )
    assert mailer.sent == []


def test_check_records_fetch_failure(tmp_path):
    path = tmp_path / "seen.json"
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([], error="HTTPError: 404"),
        mailer=Mailer(), now=NOW,
    )
    assert load_state(path)["failures"]["s1"]["count"] == 1


def test_check_passes_raw_fetch_count_not_new_count(tmp_path):
    # 更新の止まったフィードでも過去記事が返るので生の件数は0にならない。
    # 新着件数を渡すと、健全なソースが3回で死亡扱いになる。
    path = tmp_path / "seen.json"
    fetcher = _fetcher([_update("a", "Weekly notes")])
    for _ in range(3):
        run_check(sources=SOURCES, state_path=path, fetcher=fetcher,
                  mailer=Mailer(), now=NOW)
    assert load_state(path)["failures"] == {}


def test_check_forgets_failures_of_removed_sources(tmp_path):
    path = tmp_path / "seen.json"
    state = empty_state()
    state["failures"]["gone"] = {"count": 5, "last_error": "Timeout"}
    save_state(path, state)

    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Weekly notes")]),
        mailer=Mailer(), now=NOW,
    )
    assert "gone" not in load_state(path)["failures"]


def test_check_does_not_mark_seen_when_send_fails(tmp_path):
    # 送信に失敗したら既読にしない。次回に再送されることが保証される。
    path = tmp_path / "seen.json"
    with pytest.raises(RuntimeError):
        run_check(
            sources=SOURCES, state_path=path,
            fetcher=_fetcher([_update("a", "Introducing X")]),
            mailer=_boom, now=NOW,
        )
    assert not path.exists()


def test_bootstrap_records_without_sending(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_bootstrap(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Introducing X"), _update("b", "Weekly")]),
        mailer=mailer, now=NOW,
    )
    assert mailer.sent == []
    state = load_state(path)
    assert set(state["uids"]) == {"a", "b"}
    assert state["pending_minor"] == []


def test_digest_sends_queued_minor_and_clears(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Weekly notes")]),
        mailer=Mailer(), now=NOW,
    )
    run_digest(state_path=path, mailer=mailer, now=NOW)
    assert len(mailer.sent) == 1
    assert load_state(path)["pending_minor"] == []


def test_digest_sends_nothing_when_queue_empty(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_digest(state_path=path, mailer=mailer, now=NOW)
    assert mailer.sent == []


def test_digest_sends_when_only_dead_sources_exist(tmp_path):
    path = tmp_path / "seen.json"
    state = empty_state()
    state["failures"]["s1"] = {"count": 3, "last_error": "HTTPError: 404"}
    save_state(path, state)

    mailer = Mailer()
    run_digest(state_path=path, mailer=mailer, now=NOW)
    assert len(mailer.sent) == 1
    assert "0件" not in mailer.sent[0]


def test_digest_keeps_queue_when_send_fails(tmp_path):
    # 送信に失敗したらキューを消さない。消すと minor が永久に失われる。
    path = tmp_path / "seen.json"
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Weekly notes")]),
        mailer=Mailer(), now=NOW,
    )
    with pytest.raises(RuntimeError):
        run_digest(state_path=path, mailer=_boom, now=NOW)
    assert len(load_state(path)["pending_minor"]) == 1


# --- 更新が止まったソースの警告 -------------------------------------------


def _update_at(uid, published):
    return Update(
        uid=uid, source_id="s1", vendor="V", label="L",
        title="Weekly notes", url=f"https://example.com/{uid}",
        published=published, summary="",
    )


def test_check_records_the_newest_published_date_per_source(tmp_path):
    path = tmp_path / "seen.json"
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([
            _update_at("a", NOW - timedelta(days=3)),
            _update_at("b", NOW),
        ]),
        mailer=Mailer(), now=NOW,
    )
    assert load_state(path)["latest"]["s1"] == NOW.isoformat()


def test_digest_warns_when_a_source_stopped_publishing(tmp_path):
    # 取得は成功し続けるので failures は空。それでも気づけること。
    path = tmp_path / "seen.json"
    state = empty_state()
    state["latest"]["s1"] = (NOW - timedelta(days=45)).isoformat()
    save_state(path, state)

    mailer = Mailer()
    run_digest(state_path=path, mailer=mailer, now=NOW)
    assert len(mailer.sent) == 1
    assert "0件" not in mailer.sent[0]


def test_digest_stays_silent_when_a_source_is_merely_quiet(tmp_path):
    # 20日の沈黙は通常の範囲。ここで鳴らすと警告欄が読まれなくなる。
    path = tmp_path / "seen.json"
    state = empty_state()
    state["latest"]["s1"] = (NOW - timedelta(days=20)).isoformat()
    save_state(path, state)

    mailer = Mailer()
    run_digest(state_path=path, mailer=mailer, now=NOW)
    assert mailer.sent == []


def test_check_skips_malformed_source_and_keeps_the_rest(tmp_path):
    # sources.yml は手書きなので誤字が入る。1件の誤字で全体が止まってはいけない。
    path = tmp_path / "seen.json"
    broken = {"vendor": "V", "label": "L", "type": "rss"}  # id が無い
    mailer = Mailer()
    run_check(
        sources=SOURCES + [broken], state_path=path,
        fetcher=_fetcher([_update("a", "Introducing X")]),
        mailer=mailer, now=NOW,
    )
    assert len(mailer.sent) == 1
    assert "a" in load_state(path)["uids"]


def test_check_records_malformed_source_as_a_failure(tmp_path):
    path = tmp_path / "seen.json"
    broken = {"vendor": "V", "label": "L", "type": "rss"}
    run_check(
        sources=SOURCES + [broken], state_path=path,
        fetcher=_fetcher([]), mailer=Mailer(), now=NOW,
    )
    failures = load_state(path)["failures"]
    assert any("定義エラー" in entry["last_error"] for entry in failures.values())


def test_check_queues_overflow_majors_for_the_digest(tmp_path):
    # 1通に載りきらない major を捨てると情報が永久に失われる。
    path = tmp_path / "seen.json"
    many = [_update(str(i), f"Introducing model {i}") for i in range(MAX_ITEMS + 5)]
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher(many), mailer=Mailer(), now=NOW,
    )
    assert len(load_state(path)["pending_minor"]) == 5


def test_main_refuses_check_without_state_file(tmp_path, capsys):
    # bootstrap 前に check が走ると、全ソースの過去記事が新着扱いになり
    # 1000通以上のメールが飛ぶ。cron が先に発火する事故を防ぐ。
    from tracker.run import main

    code = main([
        "--mode", "check",
        "--sources", str(tmp_path / "sources.yml"),
        "--state", str(tmp_path / "seen.json"),
    ])
    assert code == 1
    assert "bootstrap" in capsys.readouterr().out


def test_main_allows_bootstrap_without_state_file(tmp_path, monkeypatch):
    from tracker import run as run_module

    sources = tmp_path / "sources.yml"
    sources.write_text(
        "sources:\n"
        "  - id: a\n"
        "    vendor: V\n"
        "    label: L\n"
        "    type: rss\n"
        "    url: https://example.com/feed\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(run_module.fetch_module, "fetch_source", lambda s: ([], None))
    code = run_module.main([
        "--mode", "bootstrap",
        "--sources", str(sources),
        "--state", str(tmp_path / "seen.json"),
    ])
    assert code == 0
