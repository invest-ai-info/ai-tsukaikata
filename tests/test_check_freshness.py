# -*- coding: utf-8 -*-
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from check_freshness import (  # noqa: E402
    Reached,
    check_articles,
    external_links,
    earn_queue_shortage,
    evidence_gaps,
    lawyer_deadline_gate,
    lesson_promotions,
    queue_shortage,
)

from src.content import Article, render_markdown  # noqa: E402

TODAY = date(2026, 8, 9)


def _article(body, checked=None, slug="start"):
    return Article(
        slug=slug, title="題", description="説明", category="pages",
        published=date(2026, 8, 1), updated=None, tags=(),
        time_required=None, cost=None,
        body_html=render_markdown(body),
        source_path=Path(f"content/pages/{slug}.md"),
        checked=checked,
    )


def _ok(url):
    return Reached(200, url)


def test_external_links_are_found_once_each():
    body = "[A](https://example.com/a) [again](https://example.com/a) [B](https://example.com/b)"
    links = external_links(render_markdown(body))
    assert links == ["https://example.com/a", "https://example.com/b"]


def test_internal_links_are_not_external():
    assert external_links(render_markdown("[中](/recipes/x/)")) == []


def test_article_with_external_links_but_no_checked_is_reported():
    """付け忘れの網。ビルドでは止めないので、ここで拾わないと静かに漏れる。"""
    article = _article("[公式](https://example.com/a)", checked=None)
    problems = check_articles([article], TODAY, head=_ok).problems
    assert any("checked" in p for p in problems)


def test_link_to_our_own_repo_does_not_require_checked():
    """自分のリポジトリへのリンクは、日付を付けても意味がない。
    永久に消えない警告は、一覧そのものを読まれなくする。"""
    article = _article("[このサイトの中身](https://github.com/invest-ai-info/ai-tsukaikata)")
    assert check_articles([article], TODAY, head=_ok).problems == []


def test_our_own_broken_link_is_still_reported():
    """checked を求めないだけで、死活の検査からは外さない。"""
    article = _article("[このサイトの中身](https://github.com/invest-ai-info/ai-tsukaikata)")
    problems = check_articles([article], TODAY, head=lambda url: Reached(404, url)).problems
    assert any("404" in p for p in problems)


def test_fresh_checked_date_is_quiet():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    assert check_articles([article], TODAY, head=_ok).problems == []


def test_old_checked_date_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 1, 1))
    problems = check_articles([article], TODAY, head=_ok).problems
    assert any("確認日" in p for p in problems)


def test_dead_link_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles([article], TODAY, head=lambda url: Reached(404, url)).problems
    assert any("404" in p for p in problems)


def test_unreachable_link_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles([article], TODAY, head=lambda url: Reached(None, url)).problems
    assert any("開けません" in p for p in problems)


def test_article_without_external_links_and_without_checked_is_quiet():
    """既存記事の大半がこれ。ここで鳴ると一覧が読まれなくなる。"""
    assert check_articles([_article("ふつうの本文")], TODAY, head=_ok).problems == []


def test_link_moved_to_another_host_is_reported():
    """200が返ることと、そのURLが正式であることは別。

    リダイレクトが効いているうちは死活の検査では鳴らないので、
    たどり着いた先を突き合わせないと永久に気づけない。
    実測した本物の引っ越し: docs.claude.com→code.claude.com、
    deepmind.google→blog.google。
    """
    article = _article("[公式](https://old.example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles(
        [article], TODAY, head=lambda url: Reached(200, "https://new.example.org/a")
    ).problems
    assert any("引っ越して" in p for p in problems)
    assert any("https://new.example.org/a" in p for p in problems)


def test_same_host_redirect_is_not_a_move():
    """未ログインで /login へ飛ばされるのは引っ越しではない。

    実測: https://claude.ai/ は https://claude.ai/login へ飛ぶ。
    直しようがない警告を毎週出すと、一覧そのものが読まれなくなる。
    """
    article = _article("[公式](https://example.com/)", checked=date(2026, 8, 1))
    problems = check_articles(
        [article], TODAY, head=lambda url: Reached(200, "https://example.com/login")
    ).problems
    assert problems == []


def test_trailing_slash_is_not_a_move():
    """末尾スラッシュだけの差で鳴ると、毎週ほぼ全部のリンクが並ぶ。"""
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles([article], TODAY, head=lambda url: Reached(200, url + "/")).problems
    assert problems == []


def test_bot_blocked_link_is_a_note_not_a_problem():
    """先方の bot 判定で弾かれただけ。人がブラウザで開けば見える。

    実測: https://claude.ai/ は cf-mitigated: challenge 付きの403を返す。
    UA偽装で迂回しない方針なので、こちらからは確かめられない。
    ⚠️ これで週次を失敗させると、直しようがない警告が毎週出る。
    """
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    report = check_articles(
        [article], TODAY, head=lambda url: Reached(403, url, bot_blocked=True)
    )
    assert report.problems == []
    assert any("確かめられませんでした" in n for n in report.notes)


def test_plain_403_without_bot_marker_is_still_a_problem():
    """目印の無い403は、本当に見られなくなった可能性がある。握り潰さない。"""
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    report = check_articles([article], TODAY, head=lambda url: Reached(403, url))
    assert any("403" in p for p in report.problems)


def test_move_is_quiet_when_the_article_already_links_the_destination():
    """転送先を記事が既に貼っているなら、書き手は引っ越しを把握している。

    実測（gemini-3-6-flash）＝出典1番に移転先 blog.google を貼ったうえで、
    旧 deepmind.google を「開くとここへ転送されます」と注記していた。
    ここで鳴らすと、正しく書いてある記事を毎週叩くことになる。
    """
    body = (
        "[新](https://new.example.org/a) "
        "[旧](https://old.example.com/a)"
    )
    article = _article(body, checked=date(2026, 8, 1))
    moved = {"https://old.example.com/a": "https://new.example.org/a?utm_source=old"}
    report = check_articles(
        [article], TODAY,
        head=lambda url: Reached(200, moved.get(url, url)),
    )
    assert report.problems == []


def test_move_is_reported_when_the_destination_is_nowhere_in_the_article():
    """把握していない引っ越しは、これまでどおり鳴らす。"""
    article = _article("[旧](https://old.example.com/a)", checked=date(2026, 8, 1))
    report = check_articles(
        [article], TODAY, head=lambda url: Reached(200, "https://new.example.org/a")
    )
    assert any("引っ越して" in p for p in report.problems)


def test_queue_shortage_fires_below_the_floor():
    """待ち行列が枯れかけていたら知らせる。

    静かに枯れると、毎晩の担当が「題材が無い」で止まり始めてから気づくことになる。
    """
    queue = "\n".join(["- [ ] 題材A", "- [x] 済み", "- [!] 止めた", "- [ ] 題材B"])
    problem = queue_shortage(queue, floor=6)
    assert problem is not None
    assert "2件" in problem


def test_queue_shortage_counts_only_unprocessed():
    """`- [x]`（済み）も `- [!]`（止めた）も未処理ではない。"""
    queue = "\n".join(["- [x] 済み"] * 10 + ["- [!] 止めた"] * 10)
    problem = queue_shortage(queue, floor=6)
    assert problem is not None
    assert "0件" in problem


def test_queue_shortage_is_quiet_at_or_above_the_floor():
    queue = "\n".join(f"- [ ] 題材{i}" for i in range(6))
    assert queue_shortage(queue, floor=6) is None


def test_earn_queue_shortage_fires_below_the_floor():
    """「副業」の節の残量は全体とは別に見張る（毎晩3本の方針を支える床）。"""
    queue = "\n".join(
        ["- [ ] 全体側の題材"] * 10
        + ["### 副業（テスト）", "- [ ] 副業の題材A", "- [!] 保留", "### 次の節", "- [ ] 別の節の題材"]
    )
    problem = earn_queue_shortage(queue, floor=3)
    assert problem is not None
    assert "1件" in problem


def test_earn_queue_shortage_is_quiet_at_the_floor():
    queue = "\n".join(
        ["### 副業（テスト）"] + [f"- [ ] 副業の題材{i}" for i in range(3)] + ["### 次の節"]
    )
    assert earn_queue_shortage(queue, floor=3) is None


def test_earn_queue_shortage_counts_only_inside_the_section():
    """節の外の未処理をいくら積んでも、副業の床は埋まらない。"""
    queue = "\n".join(
        ["- [ ] 外の題材"] * 20 + ["### 副業（テスト）", "### 次の節"] + ["- [ ] 外の題材"] * 20
    )
    problem = earn_queue_shortage(queue, floor=3)
    assert problem is not None
    assert "0件" in problem


def test_earn_queue_shortage_warns_when_the_section_is_missing():
    """見出しの改名で番人が黙って死なないこと（静かな欠落の防止）。"""
    queue = "\n".join(f"- [ ] 題材{i}" for i in range(10))
    problem = earn_queue_shortage(queue, floor=3)
    assert problem is not None
    assert "見つかりません" in problem


# --- 弁護士相談の期日ゲート（2026-08-14・収入エンジン設計 D-4）---


def test_lawyer_gate_is_a_note_while_the_deadline_is_far():
    """遠いうちは表示のみ。直せない警告を毎週メールすると一覧が読まれなくなる。"""
    problems, notes = lawyer_deadline_gate(
        date(2026, 8, 15), deadline=date(2026, 10, 31), done=False)
    assert problems == []
    assert len(notes) == 1
    assert "残り77日" in notes[0]


def test_lawyer_gate_escalates_in_the_final_month():
    problems, notes = lawyer_deadline_gate(
        date(2026, 10, 10), deadline=date(2026, 10, 31), done=False)
    assert notes == []
    assert len(problems) == 1
    assert "残り21日" in problems[0]


def test_lawyer_gate_declares_the_downgrade_after_the_deadline():
    """期日超過＝グレー全域の格下げ宣言。どちらに転んでも浮遊状態が消える。"""
    problems, _ = lawyer_deadline_gate(
        date(2026, 11, 1), deadline=date(2026, 10, 31), done=False)
    assert len(problems) == 1
    assert "白のみで設計" in problems[0]


def test_lawyer_gate_boundary_day_is_still_the_ramp_not_the_downgrade():
    """期日当日はまだ格下げではない（過ぎたら、が仕様）。"""
    problems, _ = lawyer_deadline_gate(
        date(2026, 10, 31), deadline=date(2026, 10, 31), done=False)
    assert "残り0日" in problems[0]
    assert "格下げされます" in problems[0]
    assert "格下げです" not in problems[0]  # 宣言文（超過後）とは別の文


def test_lawyer_gate_goes_silent_once_the_consultation_is_done():
    """済んだら黙る。済んだ後も鳴り続ける検査は読まれなくなる。"""
    assert lawyer_deadline_gate(date(2026, 11, 1), done=True) == ([], [])


# --- 台帳の昇格判定（2026-08-14）---


def _ledger(*sections):
    return "## 生きている教訓\n\n" + "\n\n".join(sections)


def test_lesson_promotions_counts_articles_named_in_the_section():
    ledger = _ledger(
        "### ★1. 禁止は受け皿と対で\n\n`alpha` と `beta` で出た。",
        "### 2. 別の教訓\n\n`alpha` だけ。",
    )
    problems, notes = lesson_promotions(ledger, {"alpha", "beta"}, cap=15)
    assert problems == []
    assert any("★1." in n and "記事2本" in n for n in notes)


def test_lesson_promotions_counts_references_from_other_sections():
    """あとから「N番が再発」と書かれたものも1回に数える。

    再発は、その節ではなく**別の節**に書かれる（夜の担当は追記のみなので、
    既存の節を書き換えられない）。片方だけ数えると昇格候補が沈む。
    """
    ledger = _ledger(
        "### 4. 自己申告は当てにならない\n\n`alpha` で出た。",
        "### ★17. 添削は削除で処理する\n\n📌 **4番が再発した**。",
        "### ★18. 既定は決めて進む\n\n📌 **4番が再発（3本目）**。",
    )
    _, notes = lesson_promotions(ledger, {"alpha"}, cap=15)
    assert any("4." in n and "被参照2件" in n for n in notes)


def test_lesson_promotions_does_not_count_a_section_referring_to_itself():
    """自分の節で「12番の系列」と書いても、それは再発ではない。

    記事2本で一覧には出る。そこで被参照が0件のままであることを見る。
    """
    ledger = _ledger(
        "### 12. 計測スクリプトを疑う\n\n12番の系列。`alpha` と `beta` で出た。"
    )
    _, notes = lesson_promotions(ledger, {"alpha", "beta"}, cap=15)
    assert any("記事2本＋被参照0件" in n for n in notes)


def test_lesson_promotions_is_quiet_about_lessons_seen_once():
    ledger = _ledger("### 9. 一度きりの教訓\n\n`alpha` で出た。")
    _, notes = lesson_promotions(ledger, {"alpha"}, cap=15)
    assert any("0件あります" in n for n in notes)


def test_lesson_promotions_fires_when_the_ledger_is_over_the_cap():
    """上限を超えたら知らせる。長い台帳は読まれなくなって死ぬ。"""
    ledger = _ledger(*(f"### {i}. 教訓{i}\n\n本文。" for i in range(1, 21)))
    problems, _ = lesson_promotions(ledger, set(), cap=15)
    assert len(problems) == 1
    assert "20件" in problems[0]


def test_lesson_promotions_is_quiet_at_the_cap():
    ledger = _ledger(*(f"### {i}. 教訓{i}\n\n本文。" for i in range(1, 16)))
    problems, _ = lesson_promotions(ledger, set(), cap=15)
    assert problems == []


def test_lesson_promotions_warns_when_no_section_can_be_read():
    """見出しの形を変えて番人が黙って死なないこと（静かな欠落の防止）。"""
    problems, notes = lesson_promotions("## 生きている教訓\n\n* 1. 形が違う\n", set())
    assert len(problems) == 1
    assert "1件も読めません" in problems[0]
    assert notes == []


# --- 証拠の機械照合（v1.5・2026-08-14）---

def _recipe(slug="r", published=date(2026, 8, 13), prompts=("これを試す",)):
    body = "".join(f'<div class="prompt">{p}</div>' for p in prompts)
    return SimpleNamespace(slug=slug, category="recipes", published=published,
                           body_html=body, source_path=Path(f"content/recipes/{slug}.md"))


def test_evidence_gap_when_the_file_is_missing():
    problems = evidence_gaps([_recipe()], evidence={})
    assert problems and "証拠ファイルがありません" in problems[0]


def test_evidence_gap_when_a_prompt_is_not_in_the_evidence():
    article = _recipe(prompts=("試した文", "記事だけの文"))
    problems = evidence_gaps([article], evidence={"r": "…試した文…"})
    assert problems and "1/2件" in problems[0]


def test_evidence_is_quiet_when_all_prompts_match():
    article = _recipe(prompts=("試した文", "もう一つ"))
    assert evidence_gaps([article], evidence={"r": "試した文 と もう一つ"}) == []


def test_evidence_matching_is_exact_not_whitespace_insensitive():
    """空白を無視すると「記事で膨らませた指示文」を見逃す（実測で本命だった型）。"""
    article = _recipe(prompts=("一行目\n二行目",))
    assert evidence_gaps([article], evidence={"r": "一行目二行目"}) != []


def test_evidence_unescapes_html_entities():
    """本文はHTML化されているので、実体参照を戻してから突き合わせる。"""
    article = _recipe(prompts=("「A」&amp;「B」",))
    assert evidence_gaps([article], evidence={"r": "「A」&「B」"}) == []


def test_articles_before_the_era_are_exempt_by_date_not_by_name():
    """⚠️ slug 名指しの除外は作らない（FIGURE_EXEMPT_SLUGS の教訓）。"""
    old = _recipe(slug="old", published=date(2026, 8, 11))
    assert evidence_gaps([old], evidence={}) == []


def test_non_recipes_are_not_checked():
    page = SimpleNamespace(slug="about", category="pages", published=date(2026, 8, 13),
                           body_html='<div class="prompt">x</div>',
                           source_path=Path("content/pages/about.md"))
    assert evidence_gaps([page], evidence={}) == []
