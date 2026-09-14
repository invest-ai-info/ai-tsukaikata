# -*- coding: utf-8 -*-
"""major のお知らせを深掘りキューへ自動追記する仕組みのテスト。

歯止め（1日3件・二度追記しない・手動追記と衝突しない）が主題。
追記そのものより「追記しすぎない」ほうが事故になるため。
"""
from datetime import datetime, timezone

from tracker.deepdive import (
    DAILY_LIMIT, append_lines, is_unreadable, queued_urls, select_candidates,
)
from tracker.models import Update
from tracker.run import run_check
from tracker.store import load_state

NOW = datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc)

SOURCE_TYPES = {"ann": "rss", "mod": "huggingface"}


def _update(uid, source_id="ann", importance="major", url=None):
    return Update(
        uid=uid, source_id=source_id, vendor="V", label="L",
        title=f"題{uid}", url=url or f"https://example.com/{uid}",
        published=NOW, summary="",
    ).with_importance(importance)


def test_select_picks_major_announcements_only():
    updates = [
        _update("a"),
        _update("b", importance="minor"),
        _update("c", source_id="mod"),
    ]
    picked = select_candidates(
        updates, SOURCE_TYPES, queued_uids=set(), queued_urls_=set(), today_count=0
    )
    assert [u.uid for u in picked] == ["a"]


def test_select_skips_already_queued_uid_and_url():
    updates = [_update("a"), _update("b", url="https://example.com/manual")]
    picked = select_candidates(
        updates, SOURCE_TYPES,
        queued_uids={"a"}, queued_urls_={"https://example.com/manual"}, today_count=0,
    )
    assert picked == []


def test_select_respects_daily_limit():
    updates = [_update(f"u{i}") for i in range(5)]
    picked = select_candidates(
        updates, SOURCE_TYPES, queued_uids=set(), queued_urls_=set(), today_count=1
    )
    assert len(picked) == DAILY_LIMIT - 1


def test_queued_urls_reads_all_markers():
    text = (
        "- [ ] https://a\n"
        "- [x] https://b\n"
        "- [!] https://c\n"
        "  - メモ行は拾わない https://d\n"
    )
    assert queued_urls(text) == {"https://a", "https://b", "https://c"}


def test_append_lines_inserts_before_done_section():
    text = "# 頭\n\n## 待ち行列\n\n- [ ] https://old\n\n## 処理済み\n\n- 済み\n"
    result = append_lines(text, [_update("a")], NOW)
    assert "- [ ] https://example.com/a" in result
    assert result.index("https://old") < result.index("https://example.com/a")
    assert result.index("https://example.com/a") < result.index("## 処理済み")
    assert "2026-08-06 自動追記（major・V「題a」）" in result


def test_append_lines_without_done_section_appends_at_end():
    result = append_lines("## 待ち行列\n", [_update("a")], NOW)
    assert result.endswith("  - 2026-08-06 自動追記（major・V「題a」）\n")



# --- 読めないホストに枠を取らせない（2026-08-31）---
#
# 直近5件の自動追記が全部 openai.com で、そのどれも先方の bot 判定で読めず、
# tools/ の自動公開が2026-08-21で止まっていた。枠は1日3件しかないので、
# 「読めないと分かっているものが枠を取る」ことそのものが事故になる。


def test_is_unreadable_matches_the_host_and_www():
    assert is_unreadable("https://openai.com/index/a")
    assert is_unreadable("https://www.openai.com/index/a")


def test_is_unreadable_does_not_match_subdomains():
    """⚠️ developers/platform は200を実測済み。まとめて締め出すと読める出典まで捨てる。"""
    assert not is_unreadable("https://developers.openai.com/api/docs/pricing")
    assert not is_unreadable("https://platform.openai.com/docs/models")
    assert not is_unreadable("https://notopenai.com/index/a")


def test_select_skips_unreadable_and_gives_the_slot_to_a_readable_one():
    updates = [
        _update("blocked", url="https://openai.com/index/blocked"),
        _update("ok", url="https://deepmind.google/blog/ok"),
    ]
    picked = select_candidates(
        updates, SOURCE_TYPES, queued_uids=set(), queued_urls_=set(), today_count=2,
    )
    # today_count=2 ＝残り枠は1つ。読めないほうが取ってしまわないこと
    assert [u.uid for u in picked] == ["ok"]


def test_select_reports_what_it_skipped():
    """黙って捨てない。呼び出し側が件数を出せるように受け皿へ入る。"""
    skipped = []
    picked = select_candidates(
        [_update("blocked", url="https://openai.com/index/blocked")],
        SOURCE_TYPES, queued_uids=set(), queued_urls_=set(), today_count=0,
        skipped=skipped,
    )
    assert picked == []
    assert [u.uid for u in skipped] == ["blocked"]


def test_select_without_skipped_list_still_works():
    """受け皿を渡さない呼び出し（既存の使い方）が壊れないこと。"""
    picked = select_candidates(
        [_update("blocked", url="https://openai.com/index/blocked")],
        SOURCE_TYPES, queued_uids=set(), queued_urls_=set(), today_count=0,
    )
    assert picked == []


# --- run_check への配線 ---

SOURCES = [
    {"id": "ann", "vendor": "V", "label": "L", "type": "rss", "url": "https://x/f"},
]


def _fetcher(updates):
    def fetch(source):
        return list(updates), None
    return fetch


class Mailer:
    def __init__(self):
        self.sent = []

    def __call__(self, subject, plain, html_body):
        self.sent.append(subject)


def _major(uid):
    return Update(
        uid=uid, source_id="ann", vendor="V", label="L",
        title=f"Introducing {uid}", url=f"https://example.com/{uid}",
        published=NOW, summary="",
    )


def _queue_file(tmp_path):
    path = tmp_path / "_deepdive_queue.md"
    path.write_text("## 待ち行列\n\n## 処理済み\n", encoding="utf-8")
    return path


def test_run_check_appends_major_to_queue(tmp_path):
    queue = _queue_file(tmp_path)
    state_path = tmp_path / "seen.json"
    run_check(
        sources=SOURCES, state_path=state_path,
        fetcher=_fetcher([_major("a")]), mailer=Mailer(), now=NOW,
        queue_path=queue,
    )
    text = queue.read_text(encoding="utf-8")
    assert "- [ ] https://example.com/a" in text
    assert "a" in load_state(state_path).get("deepdive_queued", {})


def test_run_check_does_not_append_twice(tmp_path):
    queue = _queue_file(tmp_path)
    state_path = tmp_path / "seen.json"
    for _ in range(2):
        run_check(
            sources=SOURCES, state_path=state_path,
            fetcher=_fetcher([_major("a")]), mailer=Mailer(), now=NOW,
            queue_path=queue,
        )
    assert queue.read_text(encoding="utf-8").count("https://example.com/a") == 1


def test_run_check_caps_daily_appends(tmp_path):
    queue = _queue_file(tmp_path)
    run_check(
        sources=SOURCES, state_path=tmp_path / "seen.json",
        fetcher=_fetcher([_major(f"u{i}") for i in range(5)]),
        mailer=Mailer(), now=NOW, queue_path=queue,
    )
    assert queue.read_text(encoding="utf-8").count("- [ ] ") == DAILY_LIMIT


def test_run_check_without_queue_path_still_works(tmp_path):
    mailer = Mailer()
    run_check(
        sources=SOURCES, state_path=tmp_path / "seen.json",
        fetcher=_fetcher([_major("a")]), mailer=mailer, now=NOW,
    )
    assert len(mailer.sent) == 1


def test_run_check_does_not_queue_unreadable_sources(tmp_path):
    """読めないホストのお知らせは、キューにもstateにも入らない。"""
    queue = _queue_file(tmp_path)
    state_path = tmp_path / "seen.json"
    blocked = Update(
        uid="b", source_id="ann", vendor="V", label="L",
        title="Introducing b", url="https://openai.com/index/b",
        published=NOW, summary="",
    )
    run_check(
        sources=SOURCES, state_path=state_path,
        fetcher=_fetcher([blocked]), mailer=Mailer(), now=NOW,
        queue_path=queue,
    )
    text = queue.read_text(encoding="utf-8")
    assert "openai.com" not in text
    assert load_state(state_path).get("deepdive_queued", {}) == {}


# --- 読める会社の minor も候補にする（2026-09-14）---
#
# 自動追記が major だけだったため、8/25〜9/14 の3週間で読める会社の候補は5件しか無く、
# tools/ の自動公開は 9/7 で止まった。手で入れた minor 2件（Gemini Omni 1.1・
# 3.5 Transcribe）は記事になっている＝minor を切ることが供給を止めていた。
# ⚠️ opt-in はソース単位（sources.yml の deepdive_minor）。雑記の多いフィードまで
# 広げると、1日3件の枠と担当の朝を雑記が取る。


def test_select_takes_minor_from_sources_that_opted_in():
    picked = select_candidates(
        [_update("m", importance="minor")], SOURCE_TYPES,
        queued_uids=set(), queued_urls_=set(), today_count=0,
        minor_sources={"ann"},
    )
    assert [u.uid for u in picked] == ["m"]


def test_select_still_ignores_minor_from_sources_that_did_not_opt_in():
    types = dict(SOURCE_TYPES, other="rss")
    picked = select_candidates(
        [_update("m", importance="minor"),
         _update("o", source_id="other", importance="minor")],
        types, queued_uids=set(), queued_urls_=set(), today_count=0,
        minor_sources={"ann"},
    )
    assert [u.uid for u in picked] == ["m"]


def test_select_gives_majors_the_slots_before_minors():
    """枠が足りない日は major が先。並び順（minor が先に来ていても）に依存しない。"""
    updates = [
        _update("m1", importance="minor"),
        _update("M"),
        _update("m2", importance="minor"),
    ]
    picked = select_candidates(
        updates, SOURCE_TYPES, queued_uids=set(), queued_urls_=set(),
        today_count=DAILY_LIMIT - 2, minor_sources={"ann"},
    )
    assert [u.uid for u in picked] == ["M", "m1"]


def test_select_never_takes_minor_from_model_sources_even_if_opted_in():
    """モデル系は minor でも major でも選ばない（出たこと自体はニュース欄で足りる）。"""
    picked = select_candidates(
        [_update("x", source_id="mod", importance="minor")], SOURCE_TYPES,
        queued_uids=set(), queued_urls_=set(), today_count=0,
        minor_sources={"mod"},
    )
    assert picked == []


def test_append_lines_records_the_importance_of_each_item():
    result = append_lines("## 待ち行列\n", [_update("a", importance="minor")], NOW)
    assert "2026-08-06 自動追記（minor・V「題a」）" in result


def _minor(uid):
    """発表語を含まない題＝classify で minor になる。"""
    return Update(
        uid=uid, source_id="ann", vendor="V", label="L",
        title=f"Weekly notes {uid}", url=f"https://example.com/{uid}",
        published=NOW, summary="",
    )


def test_run_check_appends_minor_when_the_source_opted_in(tmp_path):
    queue = _queue_file(tmp_path)
    mailer = Mailer()
    run_check(
        sources=[dict(SOURCES[0], deepdive_minor=True)],
        state_path=tmp_path / "seen.json",
        fetcher=_fetcher([_minor("a")]), mailer=mailer, now=NOW, queue_path=queue,
    )
    assert "- [ ] https://example.com/a" in queue.read_text(encoding="utf-8")
    assert mailer.sent == []  # minor は従来どおり即時メールにしない


def test_run_check_keeps_minor_out_of_the_queue_without_opt_in(tmp_path):
    queue = _queue_file(tmp_path)
    run_check(
        sources=SOURCES, state_path=tmp_path / "seen.json",
        fetcher=_fetcher([_minor("a")]), mailer=Mailer(), now=NOW, queue_path=queue,
    )
    assert "https://example.com/a" not in queue.read_text(encoding="utf-8")
