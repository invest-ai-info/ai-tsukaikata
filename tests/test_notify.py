# -*- coding: utf-8 -*-
from datetime import datetime, timezone

import pytest

from tracker.models import Update
from tracker.notify import build_body, build_subject, send_mail

NOW = datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc)


def _update(title="Introducing X", vendor="OpenAI", url="https://example.com/a",
            summary="ある要約"):
    return Update(
        uid="u", source_id="s", vendor=vendor, label="L",
        title=title, url=url, published=NOW, summary=summary,
    )


def test_body_contains_vendor_title_url_and_summary():
    plain, html_body = build_body([_update()], [])
    for text in (plain, html_body):
        assert "OpenAI" in text
        assert "Introducing X" in text
        assert "https://example.com/a" in text
        assert "ある要約" in text


def test_body_escapes_html_in_title():
    plain, html_body = build_body([_update(title="A <script>x</script> B")], [])
    assert "<script>" not in html_body
    assert "&lt;script&gt;" in html_body


def test_body_sorts_newest_first():
    older = Update(
        uid="a", source_id="s", vendor="V", label="L", title="Older",
        url="https://example.com/1",
        published=datetime(2026, 7, 1, tzinfo=timezone.utc), summary="",
    )
    newer = Update(
        uid="b", source_id="s", vendor="V", label="L", title="Newer",
        url="https://example.com/2",
        published=datetime(2026, 7, 20, tzinfo=timezone.utc), summary="",
    )
    plain, _ = build_body([older, newer], [])
    assert plain.index("Newer") < plain.index("Older")


def test_body_includes_summary_line_when_present():
    plain, _ = build_body([_update(summary="ある要約")], [])
    indented = [line for line in plain.splitlines() if line.startswith("  ")]
    assert len(indented) == 3
    assert "  ある要約" in indented


def test_body_omits_summary_line_when_empty():
    # DeepMind は実データで約4割が要約カラ。空行を出さない。
    plain, _ = build_body([_update(summary="")], [])
    indented = [line for line in plain.splitlines() if line.startswith("  ")]
    assert len(indented) == 2


def test_html_has_no_dangling_break_when_summary_empty():
    _, html_body = build_body([_update(summary="")], [])
    assert "</small></li>" in html_body


def test_body_reports_dead_sources():
    plain, html_body = build_body([], [("openai-news", 3, "HTTPError: 404")])
    assert "openai-news" in plain
    assert "openai-news" in html_body
    assert "404" in plain


def test_subject_for_major_mentions_count():
    assert "2" in build_subject("major", 2)


def test_subject_differs_between_modes():
    assert build_subject("major", 1) != build_subject("digest", 1)


def test_send_mail_requires_credentials(monkeypatch):
    monkeypatch.delenv("GMAIL_USER", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    with pytest.raises(RuntimeError):
        send_mail("subject", "plain", "<p>html</p>")


def test_send_mail_uses_smtp_ssl(monkeypatch):
    sent = {}

    class FakeServer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def login(self, user, pw):
            sent["login"] = (user, pw)

        def sendmail(self, sender, to, message):
            sent["sendmail"] = (sender, to, message)

    monkeypatch.setenv("GMAIL_USER", "me@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "secret")
    monkeypatch.setenv("ALERT_RECIPIENT", "to@example.com")
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *a, **k: FakeServer())

    send_mail("件名", "本文", "<p>本文</p>")

    assert sent["login"] == ("me@example.com", "secret")
    assert sent["sendmail"][0] == "me@example.com"
    assert sent["sendmail"][1] == ["to@example.com"]


def test_send_mail_falls_back_to_sender_when_recipient_unset(monkeypatch):
    sent = {}

    class FakeServer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def login(self, *args):
            pass

        def sendmail(self, sender, to, message):
            sent["to"] = to

    monkeypatch.setenv("GMAIL_USER", "me@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "secret")
    monkeypatch.delenv("ALERT_RECIPIENT", raising=False)
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *a, **k: FakeServer())

    send_mail("件名", "本文", "<p>本文</p>")

    assert sent["to"] == ["me@example.com"]
