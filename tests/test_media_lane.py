# -*- coding: utf-8 -*-
"""メディアのAIニュース（lane: media・2026-08-13 設計書 §2）のレーン分離。

守っている約束: ①メディア記事はメールに入らない ②別ファイルに貯まる
③総合メディア（filter: ai）はAI関連語のタイトルだけ拾う ④サイト側は
ファイルが無ければ欄ごと出さない。
"""
from datetime import datetime, timezone
from pathlib import Path

from tracker.models import Update
from tracker.run import _media_keep, run_check
from tracker.store import load_news

NOW = datetime(2026, 8, 13, 12, 0, tzinfo=timezone.utc)

MEDIA_SOURCE = {
    "id": "media-x", "vendor": "架空メディア", "label": "架空メディア",
    "type": "rss", "lane": "media", "filter": "ai", "url": "https://x/m",
}


def _item(uid, title):
    return Update(
        uid=uid, source_id="media-x", vendor="架空メディア", label="架空メディア",
        title=title, url=f"https://example.com/{uid}", published=NOW, summary="",
    )


class Mailer:
    def __init__(self):
        self.sent = []

    def __call__(self, subject, plain, html_body):
        self.sent.append(subject)


def _fetcher(updates):
    def fetch(source):
        return list(updates), None
    return fetch


def test_media_filter_keeps_only_ai_titles():
    assert _media_keep(_item("a", "ChatGPTの新機能が公開"), MEDIA_SOURCE)
    assert _media_keep(_item("b", "生成AIの業務利用が拡大"), MEDIA_SOURCE)
    assert not _media_keep(_item("c", "新型スマホ発表"), MEDIA_SOURCE)


def test_media_filter_passes_everything_without_flag():
    source = dict(MEDIA_SOURCE)
    del source["filter"]
    assert _media_keep(_item("c", "新型スマホ発表"), source)


def test_run_check_puts_media_in_separate_archive_and_never_mails(tmp_path):
    mailer = Mailer()
    state_path = tmp_path / "seen.json"
    run_check(
        sources=[MEDIA_SOURCE], state_path=state_path,
        fetcher=_fetcher([_item("a", "ChatGPT関連の記事"), _item("b", "無関係の記事")]),
        mailer=mailer, now=NOW,
    )
    archive = load_news(tmp_path / "media_news.json")
    uids = [item["uid"] for item in archive["items"]]
    assert uids == ["a"]                       # フィルタ通過分だけ貯まる
    assert mailer.sent == []                   # メディアはメールに入らない
    assert not (tmp_path / "news.json").exists() or \
        load_news(tmp_path / "news.json")["items"] == []


def test_run_check_does_not_rejudge_filtered_media(tmp_path):
    """フィルタ落ちも既読になる＝次の回で再判定しない。"""
    state_path = tmp_path / "seen.json"
    fetch = _fetcher([_item("b", "無関係の記事")])
    run_check(sources=[MEDIA_SOURCE], state_path=state_path,
              fetcher=fetch, mailer=Mailer(), now=NOW)
    run_check(sources=[MEDIA_SOURCE], state_path=state_path,
              fetcher=fetch, mailer=Mailer(), now=NOW)
    archive = load_news(tmp_path / "media_news.json")
    assert archive["items"] == []


def test_load_media_news_returns_empty_when_missing(tmp_path):
    from src.news import load_media_news
    assert load_media_news(tmp_path / "media_news.json") == []
