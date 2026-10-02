# -*- coding: utf-8 -*-
"""AI動画まとめ（/videos/・2026-10-02）。

守っている約束:
①ショートは載せない ②404 は再試行してから諦める（正しいIDでも404が続くため）
③要約が済んだ動画だけ載せる ④枠切れ（429）は動画の失敗に数えない
⑤壊れたデータはビルドを止める ⑥リンク先は YouTube の視聴ページに固定
"""
import json
import re
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src import build, videos as site_videos
from videos import feed, gemini, run, store

NOW = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)

FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"
      xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
 <title>Test channel</title>
 <entry>
  <yt:videoId>AAAAAAAAAAA</yt:videoId>
  <title>Claude Opus 5.5 explained</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=AAAAAAAAAAA"/>
  <published>2026-10-01T09:00:00+00:00</published>
  <media:group><media:description>LINE登録で特典</media:description></media:group>
 </entry>
 <entry>
  <yt:videoId>BBBBBBBBBBB</yt:videoId>
  <title>short clip</title>
  <link rel="alternate" href="https://www.youtube.com/shorts/BBBBBBBBBBB"/>
  <published>2026-10-01T10:00:00+00:00</published>
 </entry>
</feed>
""".encode("utf-8")

CHANNEL = {"key": "test", "name": "テストch", "channel_id": "UC" + "x" * 22,
           "category": "tech"}


def _entry(video_id="AAAAAAAAAAA", published="2026-10-01T09:00:00+00:00"):
    return {"video_id": video_id, "title": "題", "published": published,
            "url": f"https://www.youtube.com/watch?v={video_id}", "description": "説明"}


def _reply(**overrides):
    data = {"is_ai": True, "category": "tech",
            "summary": ["一つ目と説明している", "二つ目", "三つ目"],
            "for_whom": "自動化したい会社員", "caution": ""}
    data.update(overrides)
    return json.dumps(data, ensure_ascii=False)


# --- 配信（RSS） ---

def test_parse_feed_skips_shorts_and_keeps_fields():
    entries = feed.parse_feed(FEED)
    assert [e["video_id"] for e in entries] == ["AAAAAAAAAAA"]
    assert entries[0]["title"] == "Claude Opus 5.5 explained"
    assert entries[0]["url"] == "https://www.youtube.com/watch?v=AAAAAAAAAAA"
    assert entries[0]["description"] == "LINE登録で特典"


def test_parse_feed_rejects_non_feed():
    with pytest.raises(feed.FeedError):
        feed.parse_feed(b"<html>not a feed</html>")


def test_fetch_feed_retries_404_then_succeeds():
    calls, waits = [], []

    def get(url):
        calls.append(url)
        if len(calls) < 3:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        return FEED

    assert feed.fetch_feed("UCabc", get=get, sleep=waits.append) == FEED
    assert len(calls) == 3 and waits == list(feed.RETRY_WAITS[:2])


def test_fetch_feed_gives_up_after_all_retries():
    def get(url):
        raise urllib.error.HTTPError(url, 500, "err", {}, None)

    with pytest.raises(feed.FeedError, match="HTTP 500"):
        feed.fetch_feed("UCabc", get=get, sleep=lambda s: None, waits=(1, 1))


# --- 保存 ---

def test_merge_adds_pending_once_and_skips_old():
    data = store.empty()
    old = (NOW - timedelta(days=store.PENDING_DAYS + 1)).isoformat()
    entries = [_entry(), _entry("CCCCCCCCCCC", old)]
    assert store.merge(data, CHANNEL, entries, NOW) == 1
    assert store.merge(data, CHANNEL, entries, NOW) == 0
    video = data["videos"][0]
    assert video["status"] == "pending" and video["channel_key"] == "test"


def test_mark_failed_gives_up_after_max_attempts():
    data = store.empty()
    store.merge(data, CHANNEL, [_entry()], NOW)
    video = data["videos"][0]
    for _ in range(store.MAX_ATTEMPTS - 1):
        store.mark_failed(video, "err")
    assert video["status"] == "pending"
    store.mark_failed(video, "err")
    assert video["status"] == "failed" and "description" not in video


def test_prune_removes_old_stale_and_dropped_channels():
    data = store.empty()
    store.merge(data, CHANNEL, [_entry()], NOW)
    store.merge(data, {**CHANNEL, "key": "gone"}, [_entry("DDDDDDDDDDD")], NOW)
    later = NOW + timedelta(days=store.PENDING_DAYS + 1)
    assert store.prune(data, NOW, {"test"}) == 1          # 外したチャンネル
    assert store.prune(data, later, {"test"}) == 1        # 要約待ちのまま古くなった
    assert data["videos"] == []


def test_load_missing_is_empty_and_broken_raises(tmp_path):
    assert store.load(tmp_path / "none.json") == store.empty()
    broken = tmp_path / "videos.json"
    broken.write_text("{", encoding="utf-8")
    with pytest.raises(store.StoreError):
        store.load(broken)


def test_save_then_load_roundtrip(tmp_path):
    data = store.empty()
    store.merge(data, CHANNEL, [_entry()], NOW)
    path = tmp_path / "data" / "videos.json"
    store.save(path, data)
    assert store.load(path) == data


# --- Gemini の返事 ---

def test_parse_reply_accepts_fenced_json_and_truncates():
    long_line = "あ" * (gemini.SUMMARY_MAX + 20)
    text = "```json\n" + _reply(summary=[long_line, "二", "三", "四"]) + "\n```"
    result = gemini.parse_reply(text)
    assert result["category"] == "tech"
    assert len(result["summary"]) == 3
    assert len(result["summary"][0]) == gemini.SUMMARY_MAX


def test_parse_reply_not_ai():
    assert gemini.parse_reply('{"is_ai": false}') == {"is_ai": False}


@pytest.mark.parametrize("text", [
    "要約できません",
    _reply(category="other"),
    _reply(summary=[]),
    _reply(summary="文字列"),
    '{"is_ai": "yes"}',
])
def test_parse_reply_rejects_bad_shapes(text):
    with pytest.raises(gemini.ReplyError):
        gemini.parse_reply(text)


def test_response_text_extractors():
    interactions = {"steps": [{"type": "model_output",
                               "content": [{"type": "text", "text": "本文"}]}]}
    assert gemini.interactions_text(interactions) == "本文"
    generate = {"candidates": [{"content": {"parts": [{"text": "本文"}]}}]}
    assert gemini.generate_text(generate) == "本文"


def test_prompt_includes_description_and_caution_rules():
    prompt = gemini.build_prompt({"title": "題", "channel_name": "ch",
                                  "default_category": "earn", "description": "LINE登録"},
                                 today="2026-10-02")
    assert "LINE登録" in prompt and "出演者の主張" in prompt
    # 知らないモデル名を「架空」と書かせない（初回実行で実際に起きた）
    assert "今日は 2026-10-02" in prompt and "実在するもの" in prompt


def test_client_falls_back_and_keeps_key_out_of_url():
    seen = []

    def post(url, api_key, payload):
        seen.append(url)
        assert "key" not in url and api_key == "secret"
        if "interactions" in url:
            raise urllib.error.HTTPError(url, 400, "bad", {}, None)
        return {"candidates": [{"content": {"parts": [{"text": _reply()}]}}]}

    text, model = gemini.client("secret", post=post)({"url": "https://youtu.be/x",
                                                      "title": "t"})
    assert json.loads(text)["category"] == "tech"
    assert model == gemini.MODELS[0] and len(seen) == 2


def test_client_raises_quota_error_on_429():
    def post(url, api_key, payload):
        raise urllib.error.HTTPError(url, 429, "quota", {}, None)

    with pytest.raises(gemini.QuotaError):
        gemini.client("k", post=post)({"url": "u", "title": "t"})


# --- 1回分の流れ ---

def _pending_data(count=3):
    data = store.empty()
    entries = [_entry(f"{chr(65 + i)}" * 11, f"2026-10-0{i + 1}T00:00:00+00:00")
               for i in range(count)]
    store.merge(data, CHANNEL, entries, NOW)
    return data


def test_summarize_marks_done_newest_first_and_respects_limit():
    data = _pending_data(3)
    asked = []

    def call(video):
        asked.append(video["video_id"])
        return _reply(category="news"), "gemini-test"

    assert run.summarize(data, call, NOW, limit=2, log=lambda m: None) == 2
    assert asked == ["CCCCCCCCCCC", "BBBBBBBBBBB"]
    done = [v for v in data["videos"] if v["status"] == "done"]
    assert {v["category"] for v in done} == {"news"}
    assert all(v["summary_source"] == "gemini" for v in done)


def test_summarize_stops_on_quota_without_counting_failure():
    data = _pending_data(2)

    def call(video):
        raise gemini.QuotaError("429")

    assert run.summarize(data, call, NOW, log=lambda m: None) == 0
    assert all(v["status"] == "pending" and v["attempts"] == 0 for v in data["videos"])


def test_summarize_counts_bad_reply_as_attempt():
    data = _pending_data(1)
    run.summarize(data, lambda v: ("要約できません", "m"), NOW, log=lambda m: None)
    assert data["videos"][0]["attempts"] == 1


def test_collect_skips_failed_channel_and_records_it():
    data = store.empty()

    def fetch(channel_id):
        if channel_id == "UCbad":
            raise feed.FeedError("404")
        return FEED

    channels = [CHANNEL, {**CHANNEL, "key": "bad", "channel_id": "UCbad"}]
    assert run.collect(data, channels, NOW, fetch=fetch, log=lambda m: None) == 1
    assert data["channels"]["bad"]["fail_streak"] == 1
    assert data["channels"]["test"]["fail_streak"] == 0


def test_main_without_key_collects_but_does_not_summarize(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(run, "load_channels", lambda: [CHANNEL])
    monkeypatch.setattr(feed, "fetch_feed", lambda channel_id: FEED)
    path = tmp_path / "videos.json"
    assert run.main(["--data", str(path)], now=NOW) == 0
    saved = store.load(path)
    assert [v["status"] for v in saved["videos"]] == ["pending"]


def test_real_channels_file_is_valid():
    channels = run.load_channels()
    assert len(channels) >= 3
    assert {c["category"] for c in channels} == set(gemini.CATEGORIES)
    for channel in channels:
        assert re.fullmatch(r"UC[A-Za-z0-9_-]{22}", channel["channel_id"]), channel["key"]


# --- サイト側 ---

def _done_data(**video_overrides):
    video = {
        "video_id": "AAAAAAAAAAA", "title": "題<b>", "url": "javascript:alert(1)",
        "published": "2026-10-01T09:00:00+00:00", "channel_key": "muttyo",
        "channel_name": "ch", "status": "done", "category": "earn",
        "summary": ["一", "二"], "for_whom": "会社員", "caution": "金額は出演者の主張",
    }
    video.update(video_overrides)
    return {"videos": [video], "channels": {}}


def _write(tmp_path, data):
    path = tmp_path / "videos.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_videos_missing_or_no_done_is_none(tmp_path):
    assert site_videos.load_videos(tmp_path / "none.json", run.CHANNELS_PATH) is None
    path = _write(tmp_path, _done_data(status="pending"))
    assert site_videos.load_videos(path, run.CHANNELS_PATH) is None


def test_load_videos_groups_and_forces_youtube_link(tmp_path):
    result = site_videos.load_videos(_write(tmp_path, _done_data()), run.CHANNELS_PATH)
    sections = {s["key"]: s for s in result["sections"]}
    assert list(sections) == ["tech", "earn", "news"]
    entry = sections["earn"]["entries"][0]
    assert entry["url"] == "https://www.youtube.com/watch?v=AAAAAAAAAAA"
    assert entry["thumbnail"].startswith("https://i.ytimg.com/vi/AAAAAAAAAAA/")
    assert "LINE" in entry["note"]          # channels.yml の注意書きが付く
    assert sections["tech"]["entries"] == []


@pytest.mark.parametrize("overrides", [{"video_id": "bad id"}, {"summary": "文字列"},
                                       {"title": ""}, {"published": "昨日"}])
def test_load_videos_rejects_bad_rows(tmp_path, overrides):
    with pytest.raises(site_videos.VideoError):
        site_videos.load_videos(_write(tmp_path, _done_data(**overrides)), run.CHANNELS_PATH)


def test_load_videos_broken_json_raises(tmp_path):
    path = tmp_path / "videos.json"
    path.write_text("{", encoding="utf-8")
    with pytest.raises(site_videos.VideoError):
        site_videos.load_videos(path, run.CHANNELS_PATH)


def _tmp_build(tmp_path, videos_data):
    from tests.test_build import _content_dir
    content = _content_dir(tmp_path)
    news_dir = tmp_path / "data" / "tracker"
    news_dir.mkdir(parents=True)
    news_path = news_dir / "news.json"
    news_path.write_text(Path(build.NEWS_PATH).read_text(encoding="utf-8"), encoding="utf-8")
    if videos_data is not None:
        (tmp_path / "data" / "videos").mkdir(parents=True)
        _write(tmp_path / "data" / "videos", videos_data)
    return build.collect(content, news_path=news_path)


def test_build_renders_videos_page_and_button(tmp_path):
    files, errors = _tmp_build(tmp_path, _done_data())
    assert errors == []
    page = files["videos/index.html"]
    assert "https://www.youtube.com/watch?v=AAAAAAAAAAA" in page
    assert "javascript:" not in page
    assert "題&lt;b&gt;" in page                      # 題はエスケープされる
    assert "出演者の主張" in page
    assert 'href="/videos/"' in files["index.html"]
    assert "/videos/" in files["sitemap.xml"]
    assert 'id="v-AAAAAAAAAAA"' in page                 # 検索結果の飛び先


def test_build_puts_videos_in_search_index(tmp_path):
    files, errors = _tmp_build(tmp_path, _done_data())
    assert errors == []
    index = json.loads(files["search.json"])
    hits = [e for e in index if e["category"] == "videos"]
    assert len(hits) == 1
    hit = hits[0]
    assert hit["url"] == "/videos/#v-AAAAAAAAAAA"        # YouTube ではなく要約のあるカードへ
    assert hit["title"] == "題<b>"                        # JS 側が textContent で出す
    assert "一" in hit["description"] and "二" in hit["description"]
    assert "ch" in hit["tags"] and "AIで稼ぐ" in hit["tags"]
    assert hit["published"] == "2026-10-01"
    # 記事の索引と同じ形（JS が同じ描き方で出せる）
    article = next(e for e in index if e["category"] != "videos")
    assert set(hit) == set(article)


def test_search_index_has_no_videos_without_data(tmp_path):
    files, _ = _tmp_build(tmp_path, None)
    assert all(e["category"] != "videos" for e in json.loads(files["search.json"]))


def test_build_without_videos_has_no_page_or_button(tmp_path):
    files, errors = _tmp_build(tmp_path, None)
    assert errors == []
    assert "videos/index.html" not in files
    assert 'href="/videos/"' not in files["index.html"]


def test_build_stops_on_broken_videos(tmp_path):
    files, errors = _tmp_build(tmp_path, _done_data(video_id="bad"))
    assert files == {} and any("video_id" in e for e in errors)
