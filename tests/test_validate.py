# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path

import pytest

from src.content import Article, render_markdown
from src.validate import validate


def _article(body="ふつうの本文です。", slug="sample", category="recipes", title="題名", **kwargs):
    defaults = dict(
        slug=slug,
        title=title,
        description="説明文です。",
        category=category,
        published=date(2026, 8, 1),
        updated=None,
        tags=(),
        time_required="30分" if category == "recipes" else None,
        cost="無料" if category == "recipes" else None,
        body_html=render_markdown(body),
        source_path=Path(f"content/{category}/{slug}.md"),
    )
    defaults.update(kwargs)
    return Article(**defaults)


def test_clean_article_has_no_errors():
    assert validate([_article()]) == []


@pytest.mark.parametrize("secret", [
    "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "github_pat_11ABCDEFG0abcdefghijklmnopqrstuvwxyz012345",
    "sk-ant-api03-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789",
    "AKIAIOSFODNN7EXAMPLE",
    "xoxb-1234567890-abcdefghijklmnop",
])
def test_token_shaped_string_is_detected(secret):
    errors = validate([_article(body=f"設定値は {secret} です。")])
    assert len(errors) == 1


def test_credential_assignment_is_detected():
    errors = validate([_article(body="api_key=8Kd93jfMs02nfLq1")])
    assert any("認証情報" in error for error in errors)


def test_placeholder_credential_is_allowed():
    assert validate([_article(body="api_key=your-api-key-here")]) == []


def test_github_actions_secrets_reference_is_allowed():
    body = "```yaml\nenv:\n  GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}\n```"
    assert validate([_article(body=body)]) == []


def test_raw_email_is_detected():
    errors = validate([_article(body="連絡先は taro.yamada@gmail.com です。")])
    assert any("メールアドレス" in error for error in errors)


@pytest.mark.parametrize("address", [
    "you@example.com",
    "41898282+github-actions[bot]@users.noreply.github.com",
])
def test_safe_email_domain_is_allowed(address):
    assert validate([_article(body=f"宛先には {address} を使います。")]) == []


def test_local_windows_path_is_detected():
    errors = validate([_article(body=r"作業場所は C:\Users\taro\project です。")])
    assert any("絶対パス" in error for error in errors)


def test_placeholder_windows_path_is_allowed():
    assert validate([_article(body=r"作業場所は C:\Users\<ユーザー名>\project です。")]) == []


def test_secret_in_title_is_detected():
    errors = validate([_article(title="ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 の使い方")])
    assert len(errors) == 1


def test_duplicate_url_is_detected():
    errors = validate([_article(slug="same"), _article(slug="same")])
    assert any("重複" in error for error in errors)


def test_page_slug_colliding_with_category_is_detected():
    page = _article(slug="recipes", category="pages")
    errors = validate([page])
    assert any("予約" in error for error in errors)


def test_category_not_matching_directory_is_detected():
    article = _article(category="recipes", source_path=Path("content/tools/sample.md"))
    errors = validate([article])
    assert any("置き場所" in error for error in errors)


def test_broken_internal_link_is_detected():
    errors = validate([_article(body="[これ](/recipes/nothing-here/)を見てください。")])
    assert any("リンク先" in error for error in errors)


def test_valid_internal_link_passes():
    target = _article(slug="target")
    source = _article(slug="source", body="[あれ](/recipes/target/)を見てください。")
    assert validate([target, source]) == []


def test_link_to_category_list_passes():
    assert validate([_article(body="[一覧](/recipes/)を見てください。")]) == []


def test_link_to_static_file_passes():
    assert validate([_article(body="[CSS](/static/style.css)")]) == []


def test_external_link_is_not_checked():
    assert validate([_article(body="[GitHub](https://github.com/nothing/here)")]) == []


def test_affiliate_link_without_disclosure_is_detected():
    errors = validate([_article(body="[商品](https://px.a8.net/svt/ejp?a8mat=abc)")])
    assert any("広告" in error for error in errors)


def test_affiliate_link_with_disclosure_passes():
    body = "この記事には広告が含まれます。\n\n[商品](https://px.a8.net/svt/ejp?a8mat=abc)"
    assert validate([_article(body=body)]) == []


def test_all_errors_are_collected_not_just_the_first():
    body = (
        "連絡は taro.yamada@gmail.com へ。\n\n"
        r"作業場所は C:\Users\taro です。" + "\n\n"
        "[これ](/recipes/nothing-here/)も見てください。\n"
    )
    errors = validate([_article(body=body)])
    assert len(errors) == 3
