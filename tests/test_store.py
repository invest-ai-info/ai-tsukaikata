# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from tracker import store as store_module
from tracker.models import Update
from tracker.store import (
    append_news,
    dead_sources,
    empty_news,
    empty_state,
    forget_removed_sources,
    load_news,
    load_state,
    mark_seen,
    news_path_for,
    prune,
    prune_news,
    queue_minor,
    record_result,
    save_news,
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


def test_save_state_leaves_no_temp_file_behind(tmp_path):
    path = tmp_path / "seen.json"
    save_state(path, empty_state())
    assert [p.name for p in tmp_path.iterdir()] == ["seen.json"]


def test_save_state_preserves_existing_file_when_serialisation_fails(tmp_path):
    path = tmp_path / "seen.json"
    good = empty_state()
    good["uids"]["a"] = NOW.isoformat()
    save_state(path, good)

    broken = empty_state()
    broken["uids"]["b"] = object()  # JSON にできない値
    with pytest.raises(TypeError):
        save_state(path, broken)

    assert load_state(path) == good


def test_minor_queue_survives_a_real_disk_roundtrip(tmp_path):
    # 毎時チェックで溜めた minor が、翌朝の別プロセスのダイジェストまで生き残ること。
    path = tmp_path / "seen.json"
    state = empty_state()
    queue_minor(state, [_update("a"), _update("b")])
    save_state(path, state)

    taken = take_pending_minor(load_state(path))
    assert [u.uid for u in taken] == ["a", "b"]
    assert all(u.published.tzinfo is not None for u in taken)


def test_load_state_raises_on_corrupt_file_rather_than_resetting(tmp_path):
    # 壊れたファイルを空状態に握り潰してはいけない。全uidが新着に戻り、
    # 過去の major まで再送してメールが溢れる。落ちて人間に気づかせるのが正しい。
    path = tmp_path / "seen.json"
    path.write_text('{"uids": {"a": "2026', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_state(path)


def test_forget_removed_sources_drops_orphaned_failures():
    state = empty_state()
    record_result(state, "alive", "Timeout", 0)
    record_result(state, "removed", "Timeout", 0)
    assert forget_removed_sources(state, {"alive"}) == 1
    assert set(state["failures"]) == {"alive"}


def test_load_state_retries_when_the_file_is_briefly_locked(tmp_path, monkeypatch):
    """常駐ソフトが os.replace 直後のファイルを掴む競合から復帰できること。

    Windows + リアルタイムスキャンの環境で、保存直後の読み込みが
    PermissionError になることがある。数十ミリ秒で解けるので待って読み直す。
    """
    path = tmp_path / "seen.json"
    save_state(path, empty_state())

    real_open = open
    calls = {"n": 0}

    def flaky_open(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise PermissionError(13, "Permission denied")
        return real_open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", flaky_open)
    assert load_state(path) == empty_state()
    assert calls["n"] == 2


def test_load_state_gives_up_when_the_lock_never_clears(tmp_path, monkeypatch):
    """本物の権限問題は握り潰さず、落ちて人間に気づかせる。"""
    path = tmp_path / "seen.json"
    save_state(path, empty_state())

    def always_denied(*args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr("builtins.open", always_denied)
    with pytest.raises(PermissionError):
        load_state(path)


def test_load_state_does_not_retry_on_broken_json(tmp_path, monkeypatch):
    """壊れたファイルは即座に落とす。リトライしても直らないし、
    握り潰すと全uidが新着に戻って過去のmajorまで再送される。"""
    path = tmp_path / "seen.json"
    path.write_text("{壊れている", encoding="utf-8")

    calls = {"n": 0}
    real_open = open

    def counting_open(*args, **kwargs):
        calls["n"] += 1
        return real_open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", counting_open)
    with pytest.raises(json.JSONDecodeError):
        load_state(path)
    assert calls["n"] == 1


def test_save_state_retries_when_replace_is_briefly_blocked(tmp_path, monkeypatch):
    """os.replace が常駐ソフトのスキャンとぶつかる競合から復帰できること。

    実測ではこちらが本命で、Windows で WinError 32 として出る。
    """
    path = tmp_path / "seen.json"
    real_replace = os.replace
    calls = {"n": 0}

    def flaky_replace(src, dst):
        calls["n"] += 1
        if calls["n"] == 1:
            raise PermissionError(32, "別のプロセスが使用中です")
        return real_replace(src, dst)

    monkeypatch.setattr("os.replace", flaky_replace)
    save_state(path, empty_state())

    assert calls["n"] == 2
    assert load_state(path) == empty_state()


def test_save_state_gives_up_when_replace_never_succeeds(tmp_path, monkeypatch):
    """本物の権限問題は握り潰さず落とす。"""
    path = tmp_path / "seen.json"

    def always_blocked(src, dst):
        raise PermissionError(32, "別のプロセスが使用中です")

    monkeypatch.setattr("os.replace", always_blocked)
    with pytest.raises(PermissionError):
        save_state(path, empty_state())


# --- 更新が止まったソースの検出 -------------------------------------------
#
# record_result は「取得できたか」しか見ない。凍ったフィードは古い記事を
# 返し続けるので、失敗カウントは永久に0のまま健康に見える。実測で Moonshot /
# Zhipu / Qwen が5〜7週止まっていたのに dead_sources は0件だった。
# ここでは「中身が更新されているか」を公開日から見る。


def _update_at(uid, published, source_id="s"):
    return Update(
        uid=uid, source_id=source_id, vendor="V", label="L",
        title="t", url="https://example.com/x", published=published, summary="",
    )


def test_record_latest_stores_the_newest_published_date():
    state = empty_state()
    store_module.record_latest(state, "s1", [
        _update_at("a", NOW - timedelta(days=5)),
        _update_at("b", NOW - timedelta(days=1)),
    ])
    assert state["latest"]["s1"] == (NOW - timedelta(days=1)).isoformat()


def test_record_latest_never_moves_the_date_backwards():
    # フィードが古い記事だけ返した回に上書きすると日付が巻き戻り、
    # 止まっていないソースが突然「停止」に見える。
    state = empty_state()
    state["latest"]["s1"] = NOW.isoformat()
    store_module.record_latest(state, "s1", [_update_at("a", NOW - timedelta(days=10))])
    assert state["latest"]["s1"] == NOW.isoformat()


def test_record_latest_ignores_an_empty_fetch():
    state = empty_state()
    store_module.record_latest(state, "s1", [])
    assert "s1" not in state["latest"]


def test_stale_sources_flags_a_source_that_stopped_publishing():
    state = empty_state()
    state["latest"]["frozen"] = (NOW - timedelta(days=31)).isoformat()
    assert store_module.stale_sources(state, NOW) == [("frozen", 31)]


def test_stale_sources_ignores_a_source_that_published_recently():
    state = empty_state()
    state["latest"]["alive"] = (NOW - timedelta(days=29)).isoformat()
    assert store_module.stale_sources(state, NOW) == []


def test_stale_sources_treats_thirty_days_as_stale():
    state = empty_state()
    state["latest"]["edge"] = (NOW - timedelta(days=store_module.STALE_DAYS)).isoformat()
    assert [sid for sid, _ in store_module.stale_sources(state, NOW)] == ["edge"]


def test_stale_sources_ignores_sources_with_no_record():
    # 記録が無いのは「止まっている」ではなく「まだ分からない」。
    # 稼働中の seen.json には latest が無いので、初回実行で誤警告してはいけない。
    assert store_module.stale_sources(empty_state(), NOW) == []


def test_stale_sources_ignores_unparseable_dates():
    # ここで落ちるとダイジェスト送信ごと止まる。警告を1件諦めるほうが軽い。
    state = empty_state()
    state["latest"]["broken"] = "not-a-date"
    assert store_module.stale_sources(state, NOW) == []


def test_stale_sources_lists_the_most_stale_first():
    state = empty_state()
    state["latest"]["a"] = (NOW - timedelta(days=35)).isoformat()
    state["latest"]["b"] = (NOW - timedelta(days=60)).isoformat()
    assert [sid for sid, _ in store_module.stale_sources(state, NOW)] == ["b", "a"]


def test_forget_removed_sources_also_drops_latest_records():
    # これが無いと、外したソースが永久に停止警告に出続けて警告欄が読まれなくなる。
    state = empty_state()
    state["latest"] = {"alive": NOW.isoformat(), "removed": NOW.isoformat()}
    forget_removed_sources(state, {"alive"})
    assert set(state["latest"]) == {"alive"}


def test_load_state_adds_latest_to_a_file_written_before_the_feature(tmp_path):
    # 稼働中の seen.json には latest が無い。落ちずに空で補われること。
    path = tmp_path / "seen.json"
    path.write_text(
        json.dumps({"uids": {}, "pending_minor": [], "failures": {}}),
        encoding="utf-8",
    )
    assert load_state(path)["latest"] == {}


# --- ニュースのアーカイブ（サイト掲載の材料） ---
#
# seen.json は「いつ見たか」しか持たない＝記事の中身はどこにも残っていなかった。
# 掲載するにはここに貯める。状態（seen.json）とは別ファイルにする。用途も寿命も
# 違うし、サイト側が状態ファイルの形に依存しないほうがよいため。


def _dated(uid, published, title="t"):
    return Update(
        uid=uid, source_id="s", vendor="V", label="L",
        title=title, url="https://example.com/x", published=published, summary="",
    )


def test_news_path_sits_next_to_the_state_file(tmp_path):
    assert news_path_for(tmp_path / "seen.json") == tmp_path / "news.json"


def test_load_news_returns_empty_when_file_missing(tmp_path):
    assert load_news(tmp_path / "nope.json") == empty_news()


def test_save_and_load_news_roundtrip(tmp_path):
    path = tmp_path / "sub" / "news.json"
    news = empty_news()
    append_news(news, [_update("a", title="タイトル")], NOW)
    save_news(path, news)
    assert load_news(path)["items"][0]["title"] == "タイトル"


def test_append_news_records_when_it_was_first_seen(tmp_path):
    news = empty_news()
    append_news(news, [_update("a")], NOW)
    assert news["items"][0]["first_seen"] == NOW.isoformat()


def test_append_news_returns_number_added():
    news = empty_news()
    assert append_news(news, [_update("a"), _update("b")], NOW) == 2


def test_append_news_ignores_uid_already_archived():
    news = empty_news()
    append_news(news, [_update("a")], NOW)
    added = append_news(news, [_update("a")], NOW + timedelta(days=1))
    assert added == 0
    assert len(news["items"]) == 1


def test_append_news_keeps_the_original_first_seen():
    # 2回目に見たときの時刻で上書きすると「いつ届いたか」が狂う。
    news = empty_news()
    append_news(news, [_update("a")], NOW)
    append_news(news, [_update("a")], NOW + timedelta(days=1))
    assert news["items"][0]["first_seen"] == NOW.isoformat()


def test_append_news_sorts_newest_first():
    news = empty_news()
    old = _dated("old", NOW - timedelta(days=2), title="古い")
    new = _dated("new", NOW, title="新しい")
    append_news(news, [old, new], NOW)
    assert [i["title"] for i in news["items"]] == ["新しい", "古い"]


def test_prune_news_drops_items_older_than_retention():
    news = empty_news()
    stale = _dated("stale", NOW - timedelta(days=store_module.NEWS_RETENTION_DAYS + 1))
    fresh = _dated("fresh", NOW)
    append_news(news, [stale, fresh], NOW)
    assert prune_news(news, NOW) == 1
    assert [i["uid"] for i in news["items"]] == ["fresh"]


def test_prune_news_caps_the_item_count(monkeypatch):
    monkeypatch.setattr(store_module, "NEWS_MAX_ITEMS", 3)
    news = empty_news()
    items = [_dated(f"u{n}", NOW - timedelta(hours=n)) for n in range(6)]
    append_news(news, items, NOW)
    prune_news(news, NOW)
    # 新しい順に残る
    assert [i["uid"] for i in news["items"]] == ["u0", "u1", "u2"]


def test_load_news_raises_on_corrupt_file_rather_than_resetting(tmp_path):
    # 握り潰すと集めた履歴が黙って消える。seen.json と同じく落として気づかせる。
    path = tmp_path / "news.json"
    path.write_text("{壊れている", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_news(path)
