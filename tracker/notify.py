# -*- coding: utf-8 -*-
"""メール本文の組み立てと送信。SMTP に触る層。

送信方式は marketwatch-ai の email_weekly_zone.py と同じ Gmail SMTP。
"""
from __future__ import annotations

import html as html_mod
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from .models import Update

FOOTER = "※個人用の情報収集メモです。詳細は必ず出典元をご確認ください。"

# 1通に載せる最大件数。Gmail は約102KBでメールを途中打ち切りする（実測で
# 1件あたり約1KB）。打ち切られると末尾が読めなくなるので、こちらで先に切る。
MAX_ITEMS = 50


def _one_line(text: str) -> str:
    """改行やタブを潰して1行にする。

    壊れたフィードのタイトルに改行が入ると、プレーンテキスト本文で
    別エントリの見出しのように見えてしまう。
    """
    return " ".join((text or "").split())


def build_subject(mode: str, count: int, dead_count: int = 0) -> str:
    if mode == "major":
        return f"🚨 AI重要アップデート {count}件"
    if count == 0 and dead_count:
        return f"⚠️ AIトラッカー: {dead_count}件のソースが取得できていません"
    return f"📮 AI更新ダイジェスト {count}件"


def build_body(
    updates: list[Update],
    dead: list[tuple[str, int, str]],
) -> tuple[str, str]:
    """(plain, html) を返す。新しい順に並べる。"""
    ordered = sorted(updates, key=lambda u: u.published, reverse=True)
    shown = ordered[:MAX_ITEMS]
    omitted = len(ordered) - len(shown)

    plain_lines = []
    html_items = []
    for update in shown:
        title = _one_line(update.title)
        stamp = update.published.strftime("%Y-%m-%d %H:%M UTC")
        rows = [
            f"[{update.vendor}] {title}",
            f"  {stamp}",
            f"  {update.url}",
        ]
        # 要約が空のソースは実在する（DeepMind は実測で約4割）。空行を出さない。
        if update.summary:
            rows.append(f"  {update.summary}")
        plain_lines.append("\n".join(rows) + "\n")

        summary_html = (
            f"<br>{html_mod.escape(update.summary)}" if update.summary else ""
        )
        html_items.append(
            "<li style='margin-bottom:14px'>"
            f"<b>[{html_mod.escape(update.vendor)}]</b> "
            f"<a href=\"{html_mod.escape(update.url, quote=True)}\">"
            f"{html_mod.escape(title)}</a>"
            f"<br><small style='color:#6e7781'>{stamp}</small>"
            f"{summary_html}"
            "</li>"
        )

    plain = "\n".join(plain_lines) if plain_lines else "（新着なし）\n"
    body_html = (
        f"<ul style='padding-left:18px'>{''.join(html_items)}</ul>"
        if html_items else "<p>（新着なし）</p>"
    )

    if omitted:
        plain += f"\n（他 {omitted} 件は省略しました）\n"
        body_html += f"<p>（他 {omitted} 件は省略しました）</p>"

    if dead:
        plain += "\n--- 取得できていないソース ---\n"
        dead_items = []
        for source_id, count, error in dead:
            plain += f"⚠️ {source_id}: {count}回連続で失敗 ({error})\n"
            dead_items.append(
                f"<li>⚠️ {html_mod.escape(source_id)}: {count}回連続で失敗 "
                f"({html_mod.escape(error)})</li>"
            )
        body_html += (
            "<h3 style='font-size:14px'>取得できていないソース</h3>"
            f"<ul style='padding-left:18px'>{''.join(dead_items)}</ul>"
        )

    plain += f"\n{FOOTER}\n"
    html_body = (
        "<html><body>"
        "<div style=\"font-family:-apple-system,Segoe UI,sans-serif;"
        "font-size:14px;line-height:1.6;color:#1f2328;max-width:760px;"
        "margin:0 auto;padding:8px\">"
        f"{body_html}"
        f"<hr><p style=\"font-size:12px;color:#6e7781\">{FOOTER}</p>"
        "</div></body></html>"
    )
    return plain, html_body


def send_mail(subject: str, plain: str, html_body: str) -> None:
    user = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("ALERT_RECIPIENT") or user
    if not (user and password):
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD が未設定")

    message = MIMEMultipart("alternative")
    message["From"] = user
    message["To"] = recipient
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message.attach(MIMEText(plain, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(user, password)
        server.sendmail(user, [recipient], message.as_string())
