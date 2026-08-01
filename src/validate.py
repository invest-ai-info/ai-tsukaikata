# -*- coding: utf-8 -*-
"""公開前チェック。何も書かず、エラー文字列のリストを返すだけ。

最初のエラーで止めず全部集める。1個直して再実行、の往復を避けるため。

広告表記のチェックは景表法のステマ規制対応で、法的に必須の項目。
人間の記憶ではなくここで強制する。（本ファイルは法的助言ではない）
"""
from __future__ import annotations

import html
import re

from . import config
from .content import Article

TOKEN_PATTERNS = (
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHubのトークン"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHubのトークン"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"), "AnthropicのAPIキー"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAIのAPIキー"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWSのアクセスキー"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"), "Slackのトークン"),
)

CREDENTIAL_RE = re.compile(
    r"(?i)(password|passwd|api[_\- ]?key|secret[_\- ]?key|access[_\- ]?token)"
    r"\s*[=:]\s*[\"']?([A-Za-z0-9/+_\-]{8,})"
)

# ダミー値まで落とすと記事が書けなくなるので、明らかな穴埋め語は通す
PLACEHOLDER_HINTS = (
    "your", "xxx", "dummy", "example", "sample", "here",
    "changeme", "placeholder", "secrets.", "env.",
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-\[\]]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
SAFE_EMAIL_DOMAINS = (
    "example.com", "example.org", "example.net", "users.noreply.github.com",
)

# C:\Users\<ユーザー名> のような穴埋めは通し、実在しそうな名前だけ落とす
LOCAL_PATH_RE = re.compile(r"C:\\Users\\(?![<%{＜])")

AFFILIATE_PATTERNS = (
    re.compile(r"a8\.net"),
    re.compile(r"moshimo\.com"),
    re.compile(r"valuecommerce\."),
    re.compile(r"accesstrade\."),
    re.compile(r"amzn\.to"),
    re.compile(r"hb\.afl\.rakuten"),
    re.compile(r"amazon\.co\.jp/[^\s\"')]*[?&]tag="),
)
DISCLOSURE_WORDS = ("広告", "PR", "アフィリエイト", "プロモーション")

INTERNAL_LINK_RE = re.compile(r'href="(/[^"]*)"')
ALWAYS_VALID_PATHS = ("/", "/feed.xml", "/sitemap.xml", "/robots.txt")


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in PLACEHOLDER_HINTS)


def _secret_errors(where: str, text: str) -> list[str]:
    """機密らしきものを探す。トークンの中身はエラー文に出さない。"""
    errors: list[str] = []

    for pattern, label in TOKEN_PATTERNS:
        if pattern.search(text):
            errors.append(f"{where}: {label}らしき文字列が含まれています")

    for match in CREDENTIAL_RE.finditer(text):
        if _looks_like_placeholder(match.group(2)):
            continue
        errors.append(f"{where}: 認証情報らしき代入があります（{match.group(1)}=…）")

    for match in EMAIL_RE.finditer(text):
        address = match.group(0)
        if address.lower().endswith(SAFE_EMAIL_DOMAINS):
            continue
        errors.append(f"{where}: メールアドレス {address} が本文に含まれています")

    if LOCAL_PATH_RE.search(text):
        errors.append(f"{where}: ローカルの絶対パス（C:\\Users\\…）が含まれています")

    return errors


def _has_affiliate_link(text: str) -> bool:
    return any(pattern.search(text) for pattern in AFFILIATE_PATTERNS)


def _link_errors(where: str, body_html: str, valid_paths: set[str]) -> list[str]:
    errors = []
    for raw in INTERNAL_LINK_RE.findall(body_html):
        path = raw.split("#")[0].split("?")[0]
        if not path or path.startswith("/static/"):
            continue
        if path in valid_paths:
            continue
        errors.append(f"{where}: リンク先 {raw} が存在しません")
    return errors


def validate(articles: list[Article]) -> list[str]:
    """全記事を検査してエラー文字列のリストを返す。空なら公開してよい。"""
    errors: list[str] = []

    reserved = {"/"} | {f"/{name}/" for name in config.LISTED_CATEGORIES}
    valid_paths = set(ALWAYS_VALID_PATHS) | reserved | {a.url for a in articles}
    taken: dict[str, str] = {}

    for article in articles:
        where = str(article.source_path)
        text = html.unescape(article.body_html)

        errors += _secret_errors(where, text)
        errors += _secret_errors(where, f"{article.title} {article.description}")

        if article.source_path.parent.name != article.category:
            errors.append(
                f"{where}: 置き場所とカテゴリが食い違っています"
                f"（category: {article.category} / フォルダ: {article.source_path.parent.name}/）"
            )

        if article.url in reserved:
            errors.append(f"{where}: {article.url} はサイトが使う予約済みURLです")
        elif article.url in taken:
            errors.append(f"{where}: URL {article.url} が {taken[article.url]} と重複しています")
        else:
            taken[article.url] = where

        errors += _link_errors(where, article.body_html, valid_paths)

        if _has_affiliate_link(text) and not any(word in text for word in DISCLOSURE_WORDS):
            errors.append(
                f"{where}: アフィリエイトリンクがあるのに「広告」「PR」の表記がありません"
            )

    return errors
