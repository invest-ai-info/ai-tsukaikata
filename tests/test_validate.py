# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path

import pytest

from src.content import Article, render_markdown
from src.validate import validate


# 既定を pages にしてある。レシピには密度の下限（指示文6個・図・本文1800字）が
# かかるので、それ以外の検査（機密・リンク・マーカー等）のテストで毎回
# 分厚い本文を用意する必要が出てしまう。密度は下の専用テストで見る。
def _article(body="ふつうの本文です。", slug="sample", category="pages", title="題名", **kwargs):
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


# 検査用のダミー。接頭辞と本体を分けて組み立てる。
# 完全な形で書くと、偽物でもGitHubのシークレット検出に引っかかって
# push が丸ごと拒否される（実際に拒否された）。
FAKE_TOKENS = [
    "ghp_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "github_" + "pat_11ABCDEFG0abcdefghijklmnopqrstuvwxyz012345",
    "sk-" + "ant-api03-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789",
    "AKIA" + "IOSFODNN7EXAMPLE",
    "xoxb-" + "1234567890-abcdefghijklmnop",
]


@pytest.mark.parametrize("secret", FAKE_TOKENS)
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
    errors = validate([_article(title=f"{FAKE_TOKENS[0]} の使い方")])
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
    source = _article(slug="source", body="[あれ](/target/)を見てください。")
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


FIGURE = (
    '<figure class="figure">\n'
    '<img src="/static/images/sample.svg" alt="図の説明">\n'
    "<figcaption>キャプション</figcaption>\n"
    "</figure>"
)

STATIC_PATHS = {"/static/style.css", "/static/images/sample.svg"}


def test_figure_with_existing_image_passes():
    assert validate([_article(body=FIGURE)], static_paths=STATIC_PATHS) == []


def test_missing_image_file_is_detected():
    body = FIGURE.replace("sample.svg", "nothing-here.svg")
    errors = validate([_article(body=body)], static_paths=STATIC_PATHS)
    assert any("画像" in error and "存在しません" in error for error in errors)


def test_image_without_alt_is_detected():
    body = FIGURE.replace(' alt="図の説明"', "")
    errors = validate([_article(body=body)], static_paths=STATIC_PATHS)
    assert any("alt" in error for error in errors)


def test_image_with_empty_alt_is_detected():
    body = FIGURE.replace('alt="図の説明"', 'alt=""')
    errors = validate([_article(body=body)], static_paths=STATIC_PATHS)
    assert any("alt" in error for error in errors)


def test_broken_static_link_is_detected():
    errors = validate(
        [_article(body="[CSS](/static/nope.css)")], static_paths=STATIC_PATHS
    )
    assert any("nope.css" in error for error in errors)


def test_static_paths_unknown_means_no_check():
    """static_paths を渡さないときは静的ファイルの実在を検査しない（純粋なままにするため）。"""
    body = FIGURE.replace("sample.svg", "nothing-here.svg")
    assert validate([_article(body=body)]) == []


def test_external_image_is_not_checked():
    body = '<img src="https://example.com/a.png" alt="外部の画像">'
    assert validate([_article(body=body)], static_paths=STATIC_PATHS) == []


PROMPT = '<div class="prompt">AIにこう頼んでください。\n2行目です。</div>'


def test_plain_prompt_passes():
    assert validate([_article(body=PROMPT)]) == []


def test_html_tag_inside_prompt_is_detected():
    """指示文はそのままコピーされるので、中にタグが混ざるとタグごと貼られる。"""
    body = '<div class="prompt">これは<mark>重要</mark>です。</div>'
    errors = validate([_article(body=body)])
    assert any("指示文" in error for error in errors)


def test_markdown_emphasis_inside_prompt_is_detected():
    """生HTMLの中では ** が展開されないので、画面にそのまま出てしまう。"""
    body = '<div class="prompt">**実際に開いて確認してから**リストにしてください。</div>'
    errors = validate([_article(body=body)])
    assert any("指示文" in error for error in errors)


# --- 記事の作法（これまで目視で確認していたもの） -------------------------
#
# マーカーの数え上げと「h2の数とclass付きの数の突き合わせ」は、引き継ぎメモに
# 手作業として書かれていた。実際に2026-08-02、マーカー14個の記事を手で数えて
# 気づいた。人の注意力に頼る限り、いつか通り抜ける。


def _marks(count, warn=0):
    plain = "".join(f"<mark>目印{i}</mark>" for i in range(count - warn))
    warns = "".join(f'<mark class="warn">警告{i}</mark>' for i in range(warn))
    return plain + warns


def test_marker_count_at_the_limit_passes():
    assert validate([_article(body=_marks(13, warn=5))]) == []


def test_too_many_markers_is_detected():
    errors = validate([_article(body=_marks(14, warn=5))])
    assert any("マーカー" in error and "14" in error for error in errors)


def test_too_many_warning_markers_is_detected():
    # 赤は「やると事故る」だけに使う。増やすと効かなくなる。
    errors = validate([_article(body=_marks(13, warn=6))])
    assert any("警告" in error and "6" in error for error in errors)


def test_article_without_markers_passes():
    # 下限は課さない。短い記事で永久に消えない偽陽性になるため。
    assert validate([_article(body="マーカーのない記事です。")]) == []


SECTIONS = (
    "## これで何ができるか {: .what }\n\n本文。\n\n"
    "## 前提 {: .need }\n\n本文。\n\n"
    "## AIへの頼み方 {: .ask }\n\n本文。\n\n"
    "## うまくいかないときの言い直し方 {: .fix }\n\n本文。\n\n"
    "## 応用・次の一手 {: .next }\n\n本文。\n"
)


def test_known_section_classes_pass():
    assert validate([_article(body=SECTIONS)]) == []


def test_unknown_heading_class_is_detected():
    # 誤字は既定アイコンが出るだけで、静かに間違ったまま公開される。
    body = SECTIONS.replace("{: .what }", "{: .waht }")
    errors = validate([_article(body=body)])
    assert any("waht" in error for error in errors)


def test_h2_missing_its_class_is_detected():
    # 引き継ぎメモが「ブラウザでh2の数とclass付きの数を突き合わせる」と
    # 書いていた手作業がこれ。1つ付け忘れても見た目は崩れない。
    body = SECTIONS.replace("## 前提 {: .need }", "## 前提")
    errors = validate([_article(body=body)])
    assert any("class" in error for error in errors)


def test_headings_entirely_without_class_pass():
    # 固定ページ（about / privacy）は既定アイコンで運用している。
    body = "## 見出しA\n\n本文。\n\n## 見出しB\n\n本文。\n"
    assert validate([_article(body=body, category="pages", slug="about")]) == []


def test_h3_without_class_is_allowed():
    # h3 に class を付けるのは「言い直し方」の節だけ。混在が正常。
    body = SECTIONS + "\n### 手順のひとつ\n\n本文。\n\n### 詰まったとき {: .trouble }\n\n本文。\n"
    assert validate([_article(body=body)]) == []


def test_unknown_h3_class_is_detected():
    body = SECTIONS + "\n### 詰まったとき {: .trubble }\n\n本文。\n"
    errors = validate([_article(body=body)])
    assert any("trubble" in error for error in errors)


def test_all_errors_are_collected_not_just_the_first():
    body = (
        "連絡は taro.yamada@gmail.com へ。\n\n"
        r"作業場所は C:\Users\taro です。" + "\n\n"
        "[これ](/recipes/nothing-here/)も見てください。\n"
    )
    errors = validate([_article(body=body)])
    assert len(errors) == 3


# --- レシピの密度の下限（自動生成の歯止め） ---

def _recipe(body_html, slug="sample"):
    from datetime import date
    from pathlib import Path
    from src.content import Article
    return Article(
        slug=slug, title="題", description="説明", category="recipes",
        published=date(2026, 8, 8), updated=None, tags=(),
        time_required="5分", cost="無料", body_html=body_html,
        source_path=Path(f"content/recipes/{slug}.md"), scene="work",
    )


def _thick_body(prompts=8, figure=True, link=True, chars=2200, link_to="/recipes/sample/"):
    parts = ['<div class="prompt">指示文です</div>'] * prompts
    if figure:
        parts.append('<figure class="figure"><img src="/static/images/x.svg" alt="説明"></figure>')
    if link:
        parts.append(f'<a href="{link_to}">他の記事</a>')
    parts.append("<p>" + "あ" * chars + "</p>")
    return "".join(parts)


def test_thick_recipe_passes():
    assert validate([_recipe(_thick_body())]) == []


def test_recipe_with_too_few_prompts_is_rejected():
    errors = validate([_recipe(_thick_body(prompts=5))])
    assert any("指示文が5個" in e for e in errors)


def test_recipe_without_figure_is_rejected():
    errors = validate([_recipe(_thick_body(figure=False))])
    assert any("図が1枚もありません" in e for e in errors)


def test_recipe_without_internal_link_is_rejected():
    errors = validate([_recipe(_thick_body(link=False))])
    assert any("他の記事へのリンク" in e for e in errors)


def test_thin_recipe_is_rejected():
    errors = validate([_recipe(_thick_body(chars=500))])
    assert any("本文が" in e for e in errors)


def test_no_recipe_slug_is_exempt_from_the_figure_rule():
    """図の下限に名指しの例外を作らない。

    2026-08-08 まで、図を必須にする前に書かれた集約型3本を名指しで外していた。
    3本とも図を足したので例外ごと消した。名指しの穴が1つでも残ると、
    次に書く人が「そこに足せばいい」と学んでしまう。
    """
    for slug in ("verify-before-report", "who-does-what", "limit-what-ai-touches"):
        body = _thick_body(figure=False, link_to=f"/recipes/{slug}/")
        errors = validate([_recipe(body, slug=slug)])
        assert any("図が1枚もありません" in e for e in errors), slug


def test_tools_article_is_not_measured_by_recipe_density():
    """ツール記事は指示文が少なくても成り立つ形なので、同じ物差しを当てない。"""
    from datetime import date
    from pathlib import Path
    from src.content import Article
    article = Article(
        slug="model-x", title="題", description="説明", category="tools",
        published=date(2026, 8, 8), updated=None, tags=(),
        time_required=None, cost=None,
        body_html="<p>" + "あ" * 500 + "</p>",
        source_path=Path("content/tools/model-x.md"), scene="choose",
    )
    assert validate([article]) == []


def test_future_checked_date_is_rejected():
    """未来の確認日は書き間違い。書いた本人がその場で直せるので止める。"""
    errors = validate([_article(checked=date(2099, 1, 1))], today=date(2026, 8, 9))
    assert any("未来の日付" in error for error in errors)


def test_past_checked_date_is_fine():
    assert validate([_article(checked=date(2020, 1, 1))], today=date(2026, 8, 9)) == []


def test_missing_checked_is_not_an_error():
    """checked が無いだけでは止めない。全記事に必須にすると既存記事が全部落ちる。"""
    assert validate([_article()], today=date(2026, 8, 9)) == []


# --- 証拠の機械照合（v1.5・2026-08-14 に validate へ昇格）---
#
# キュー10条（記事に載せる指示文は、証拠に同一文字列で全文を残す）の強制。
# 較正では 94/129（73%）だったので週次で可視化 → 33件を追試して 129/129 に
# してから、ここへ移した。⚠️ 100%でないうちにビルドで止めると、毎晩の
# 記事公開が巻き込まれる（`/start/` の鮮度で学んだ罠）。

def _recipe_with_prompts(*prompts, published=date(2026, 8, 13), slug="r"):
    body = "\n\n".join(f'<div class="prompt">{p}</div>' for p in prompts)
    return _article(body=body, slug=slug, category="recipes", published=published)


def _evidence_errors(errors):
    """⚠️ 「指示文」で絞ると密度下限のエラー（指示文6個以上）まで拾う。
    証拠照合のエラーは必ず docs/evidence を指すので、そこで絞る。"""
    return [e for e in errors if "docs/evidence" in e]


def test_recipe_without_evidence_file_is_rejected():
    article = _recipe_with_prompts("これを試す")
    errors = validate([article], evidence={})
    assert any("証拠ファイル" in e for e in errors)


def test_recipe_with_a_prompt_missing_from_evidence_is_rejected():
    article = _recipe_with_prompts("試した文", "記事にしか無い文")
    errors = validate([article], evidence={"r": "…試した文…"})
    assert any("1/2件" in e for e in errors)


def test_recipe_with_all_prompts_in_evidence_passes():
    article = _recipe_with_prompts("試した文", "もう一つ")
    errors = validate([article], evidence={"r": "試した文 と もう一つ"})
    assert _evidence_errors(errors) == []


def test_evidence_check_is_skipped_when_not_provided():
    """evidence を渡さない呼び出し（部分ビルド・既存テスト）では検査しない。"""
    article = _recipe_with_prompts("どこにも無い文")
    assert _evidence_errors(validate([article])) == []


def test_articles_before_the_era_are_exempt_by_date_not_by_name():
    """⚠️ slug 名指しの除外を作らない（FIGURE_EXEMPT_SLUGS の教訓）。"""
    old = _recipe_with_prompts("記録の無い文", published=date(2026, 8, 11))
    assert _evidence_errors(validate([old], evidence={})) == []


def test_non_recipe_pages_do_not_need_evidence():
    page = _article(body='<div class="prompt">x</div>', category="pages",
                    published=date(2026, 8, 13))
    assert _evidence_errors(validate([page], evidence={})) == []


# --- 金額目安ブロック（2026-08-14 稼ぎ方研究の設計）---
#
# 金額は money-note ブロックの中だけに書く。ブロックの外に書かれた収入金額は
# 機械では見ない（「月3,000円のツール」＝価格 と「月3万円稼げる」＝収入 を
# 確実に区別できず、誤検知は検査全体の信用を殺す）。人が見る＝確認担当の観点5。

MONEY_OK = (
    '<div class="money-note">\n'
    "金額の目安: 月1〜6万円（副業帯）\n"
    '根拠: 文字単価0.5〜3円（出典: <a href="https://example.com/price">○○公表価格</a>・'
    "2026-08-15確認）× 月2万字の場合\n"
    "この金額は目安であり、収益を保証するものではありません。\n"
    "</div>"
)


def test_money_note_with_all_three_passes():
    assert validate([_article(body=MONEY_OK)]) == []


def test_money_note_without_disclaimer_is_detected():
    body = MONEY_OK.replace("この金額は目安であり、収益を保証するものではありません。\n", "")
    errors = validate([_article(body=body)])
    assert any("収益を保証するものではありません" in e for e in errors)


def test_money_note_without_source_link_is_detected():
    body = MONEY_OK.replace(
        '<a href="https://example.com/price">○○公表価格</a>', "○○公表価格"
    )
    errors = validate([_article(body=body)])
    assert any("出典" in e for e in errors)


def test_money_note_without_checked_date_is_detected():
    body = MONEY_OK.replace("・2026-08-15確認", "")
    errors = validate([_article(body=body)])
    assert any("確認日" in e for e in errors)


def test_article_without_money_note_passes():
    assert validate([_article(body="金額の話をしない記事です。")]) == []
