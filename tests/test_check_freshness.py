# -*- coding: utf-8 -*-
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from check_freshness import (  # noqa: E402
    Reached,
    check_articles,
    external_links,
    earn_demand_gaps,
    hypothesis_registration_gaps,
    hypothesis_stock_empty,
    deepdive_queue_shortage,
    earn_queue_shortage,
    earn_research_heartbeat,
    evidence_gaps,
    writer_log_heartbeat,
    writer_measurement_gaps,
    lawyer_deadline_gate,
    lesson_promotions,
    money_note_staleness,
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


# --- 需要語の裏取り（2026-08-25 オーナー判断）---


def _queue(*lines: str) -> str:
    """待ち行列の断片を組み立てる（テスト用）。"""
    return chr(10).join(lines)


def test_earn_demand_gaps_fires_when_the_backing_is_missing():
    """需要を調べずに採った題材は、静かに通さない（閉じた輪の再発防止）。"""
    queue = _queue(
        "### 副業（テスト）",
        "- [ ] 裏取りのある題材",
        "  - 需要: 実質186語（生282から英語のnote 92を引いた）",
        "- [ ] 裏取りの無い題材",
        "  - 源③＝既存記事が書き残した問いから",
        "### 次の節",
    )
    problems = earn_demand_gaps(queue)
    assert len(problems) == 1
    assert "裏取りの無い題材" in problems[0]


def test_earn_demand_gaps_has_no_word_count_floor():
    """薄いと分かった題材は通す。禁じるのは調べないことで、薄いことではない。"""
    queue = _queue(
        "### 副業（テスト）",
        "- [ ] 薄いと分かっている題材",
        "  - 需要: 3語しかない。それでも既存に乗らない核があるので採る",
        "### 次の節",
    )
    assert earn_demand_gaps(queue) == []


def test_earn_demand_gaps_ignores_held_and_done_items():
    """`- [!]`（保留）と `- [x]`（済み）は対象外＝書く順番が来ていない/終わっている。"""
    queue = _queue(
        "### 副業（テスト）",
        "- [!] 保留の題材",
        "  - 理由: 弁護士相談待ち",
        "- [x] 済んだ題材",
        "  - →保管: 公開: `some-slug`",
        "### 次の節",
    )
    assert earn_demand_gaps(queue) == []


def test_earn_demand_gaps_counts_only_inside_the_section():
    """節の外の未処理は対象外（副業の節だけの縛り）。"""
    queue = _queue(
        "- [ ] 外の題材",
        "### 副業（テスト）",
        "### 次の節",
        "- [ ] 外の題材",
    )
    assert earn_demand_gaps(queue) == []


def test_earn_demand_gaps_is_quiet_when_the_section_is_missing():
    """節の欠落は earn_queue_shortage が鳴らす。同じことで二重に鳴らさない。"""
    assert earn_demand_gaps("- [ ] 題材") == []


# --- 仮説キューの事前登録（2026-08-25）---


def test_hypothesis_registration_is_quiet_when_every_field_is_filled():
    assert hypothesis_registration_gaps(_queue(
        "### H1 個数指定は使える案の数と相関しない",
        "- 状態: ⏳未着手",
        "- 仮説: ◯案出しての◯を増やしても通る案は増えない",
        "- 材料: ①架空のコピー ②架空の機能名",
        "- 測り方: 採用線を先に固定して通過数を数える",
        "- 試行回数: 18回",
        "- 反証条件: 30案の通過が5案の2倍以上なら棄却",
        "- 需要: 12語",
    )) == []


def test_hypothesis_registration_fires_on_the_frozen_fields():
    """反証条件と試行回数は、結果を見てから決めると何とでも言える欄。"""
    queue = _queue(
        "### H2 欠落は1つだけのとき素通りする",
        "- 状態: ⏳未着手",
        "- 仮説: 欠落が1つのときだけ素通りする",
        "- 材料: ①週次報告 ②見積もり",
        "- 測り方: 止まったか進んだかの2値",
        "- 需要: 0語。それでも既存に乗らない核があるので採る",
    )
    problems = hypothesis_registration_gaps(queue)
    assert len(problems) == 1
    assert "試行回数" in problems[0]
    assert "反証条件" in problems[0]


def test_hypothesis_registration_treats_an_empty_field_as_missing():
    """欄だけ置いて中身を書かない、を通さない。"""
    queue = _queue(
        "### H3 誇張は約束欄に出る",
        "- 状態: ⏳未着手",
        "- 仮説: 検証できない欄だけが足される",
        "- 材料: ①応募文 ②謝罪文",
        "- 測り方: 欄ごとに元原稿に無い記述を数える",
        "- 試行回数: 10回",
        "- 反証条件: ",
        "- 需要: 8語",
    )
    problems = hypothesis_registration_gaps(queue)
    assert len(problems) == 1
    assert "反証条件" in problems[0]


def test_hypothesis_registration_ignores_the_format_sample():
    """書式見本は `### H<番号>` なので当たらない（番人が見本で鳴らない）。"""
    queue = _queue(
        "### H<番号> <名前>",
        "- 状態: ⏳未着手 / 🔬検証中 / ✅生存 / ❌棄却",
    )
    assert hypothesis_registration_gaps(queue) == []


def test_hypothesis_demand_may_be_unchecked_before_starting():
    """着手前(⏳)は「未調査」を許す。調べるのは動かし始める前でよい。"""
    assert hypothesis_registration_gaps(_queue(
        "### H1 個数指定は使える案の数と相関しない",
        "- 状態: ⏳未着手",
        "- 仮説: ◯案出しての◯を増やしても通る案は増えない",
        "- 材料: ①架空のコピー ②架空の機能名",
        "- 測り方: 採用線を先に固定して通過数を数える",
        "- 試行回数: 18回",
        "- 反証条件: 30案の通過が5案の2倍以上なら棄却",
        "- 需要: 未調査。登録前に調べること",
    )) == []


def test_hypothesis_demand_must_be_filled_once_started():
    """着手したのに未調査のままなら鳴らす＝調べずに走り出すことを禁じる。"""
    queue = _queue(
        "### H1 個数指定は使える案の数と相関しない",
        "- 状態: 🔬検証中",
        "- 仮説: ◯案出しての◯を増やしても通る案は増えない",
        "- 材料: ①架空のコピー ②架空の機能名",
        "- 測り方: 採用線を先に固定して通過数を数える",
        "- 試行回数: 18回",
        "- 反証条件: 30案の通過が5案の2倍以上なら棄却",
        "- 需要: 未調査。登録前に調べること",
    )
    problems = hypothesis_registration_gaps(queue)
    assert len(problems) == 1
    assert "着手済みなのに需要が未調査" in problems[0]

def test_hypothesis_registration_is_quiet_without_a_file():
    assert hypothesis_registration_gaps(None) == []
    assert hypothesis_registration_gaps("") == []


# --- 弁護士相談の期日ゲート（2026-08-14・収入エンジン設計 D-4）---


def test_lawyer_gate_is_a_note_while_the_deadline_is_far():
    """遠いうちは表示のみ。直せない警告を毎週メールすると一覧が読まれなくなる。"""
    problems, notes = lawyer_deadline_gate(
        date(2026, 8, 15), deadline=date(2026, 10, 31), done=False, declined=None)
    assert problems == []
    assert len(notes) == 1
    assert "残り77日" in notes[0]


def test_lawyer_gate_escalates_in_the_final_month():
    problems, notes = lawyer_deadline_gate(
        date(2026, 10, 10), deadline=date(2026, 10, 31), done=False, declined=None)
    assert notes == []
    assert len(problems) == 1
    assert "残り21日" in problems[0]


def test_lawyer_gate_declares_the_downgrade_after_the_deadline():
    """期日超過＝グレー全域の格下げ宣言。どちらに転んでも浮遊状態が消える。"""
    problems, _ = lawyer_deadline_gate(
        date(2026, 11, 1), deadline=date(2026, 10, 31), done=False, declined=None)
    assert len(problems) == 1
    assert "白のみで設計" in problems[0]


def test_lawyer_gate_boundary_day_is_still_the_ramp_not_the_downgrade():
    """期日当日はまだ格下げではない（過ぎたら、が仕様）。"""
    problems, _ = lawyer_deadline_gate(
        date(2026, 10, 31), deadline=date(2026, 10, 31), done=False, declined=None)
    assert "残り0日" in problems[0]
    assert "格下げされます" in problems[0]
    assert "格下げです" not in problems[0]  # 宣言文（超過後）とは別の文


def test_lawyer_gate_goes_silent_once_the_consultation_is_done():
    """済んだら黙る。済んだ後も鳴り続ける検査は読まれなくなる。"""
    assert lawyer_deadline_gate(date(2026, 11, 1), done=True, declined=None) == ([], [])


def test_lawyer_gate_stops_nagging_when_the_consultation_is_declined():
    """見送り（2026-08-29 オーナー判断）＝催促は止める。直せない催促は読まれなくなる。"""
    problems, notes = lawyer_deadline_gate(
        date(2026, 10, 10), deadline=date(2026, 10, 31), done=False,
        declined=date(2026, 8, 29))
    assert problems == []          # 最終月でも problems にしない＝週次メールで急かさない
    assert len(notes) == 1
    assert "見送り" in notes[0]


def test_lawyer_gate_keeps_the_white_only_restriction_after_declining():
    """見送りでも制限は消えない。『相談しない』は設計の2分岐の片方＝白のみ設計の確定。"""
    _, notes = lawyer_deadline_gate(
        date(2026, 11, 30), deadline=date(2026, 10, 31), done=False,
        declined=date(2026, 8, 29))
    assert "白のみで設計" in notes[0]


def test_lawyer_gate_declined_does_not_claim_the_consultation_happened():
    """見送りは『実施済み』ではない＝DONE を True にして事実を偽らない。"""
    from tools.check_freshness import LAWYER_CONSULT_DONE
    assert LAWYER_CONSULT_DONE is False


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


# --- 稼ぎ方研究担当の heartbeat ---
#
# 🚨 2026-08-17 に担当自身が見つけた設計の穴の回帰テスト。
# 初版はファイルの最終コミット時刻を見ていたので、**無関係なコミットが
# このファイルに触れるだけで心拍が正常に戻った**（8/16 に実際に素通りした）。
# いまは「ログにその日の行があるか」で測る。

def _log(*days):
    head = "# 稼ぎ方研究の作業ログ\n\n## 作業ログ\n\n"
    return head + "".join(
        f"### 2026-08-{d} — その日の記録\n本文\n\n" for d in days
    )


def test_earn_research_today_is_silent():
    assert earn_research_heartbeat(_log("17"), date(2026, 8, 17)) is None


def test_earn_research_is_quiet_at_exactly_the_boundary():
    # 上限は2日。ちょうど2日ぶん空いた日はまだ鳴らない
    assert earn_research_heartbeat(_log("15"), date(2026, 8, 17)) is None


def test_earn_research_silent_too_long_is_detected():
    message = earn_research_heartbeat(_log("14"), date(2026, 8, 17))
    assert message is not None
    assert "2026-08-14" in message and "3日" in message


def test_earn_research_uses_the_newest_dated_entry():
    # 日付節が複数あるときは、いちばん新しいものを見る
    assert earn_research_heartbeat(_log("10", "17", "12"), date(2026, 8, 17)) is None


def test_earn_research_ignores_unrelated_edits():
    # 🚨 これが本体。ファイルに新しい文字が増えていても、
    # **その日の日付節が無ければ鳴る**（8/16 の素通りの再発防止）
    stale = _log("14") + "\n無関係な編集がここに入っても、日付節ではない。\n"
    assert earn_research_heartbeat(stale, date(2026, 8, 17)) is not None


def test_earn_research_without_dated_section_is_detected():
    message = earn_research_heartbeat("日付の節が無い本文", date(2026, 8, 17))
    assert message is not None and "日付の節" in message


def test_earn_research_missing_file_is_detected():
    message = earn_research_heartbeat(None, date(2026, 8, 17))
    assert message is not None
    assert "見つかりません" in message


def _money_body(checked):
    return (
        '<div class="money-note">金額の目安: 月1〜6万円\n'
        f'根拠: 出典 <a href="https://example.com">価格表</a>・{checked}確認\n'
        "この金額は目安であり、収益を保証するものではありません。</div>"
    )


def test_fresh_money_note_is_silent():
    articles = [SimpleNamespace(slug="a", body_html=_money_body("2026-08-01"))]
    assert money_note_staleness(articles, date(2026, 9, 1)) == []


def test_stale_money_note_is_listed():
    articles = [SimpleNamespace(slug="a", body_html=_money_body("2026-01-01"))]
    problems = money_note_staleness(articles, date(2026, 9, 1))
    assert len(problems) == 1
    assert "a" in problems[0]


def test_article_without_money_note_is_silent():
    articles = [SimpleNamespace(slug="a", body_html="<p>金額を書かない記事</p>")]
    assert money_note_staleness(articles, date(2026, 9, 1)) == []


def test_money_note_without_a_date_is_silently_skipped():
    """日付が無いブロックはビルド時の検査が既に強制する。ここで重複して鳴らさない。"""
    articles = [SimpleNamespace(
        slug="a",
        body_html='<div class="money-note">出典はあるが日付が無い</div>',
    )]
    assert money_note_staleness(articles, date(2026, 9, 1)) == []


# --- レシピ担当の日次ログ（★91の環境停止を捕まえる番人・2026-08-26）---
#
# 🚨 較正の結果、**既存の成果物だけを見る番人では捕まらない**ことが分かっている。
# ・停止記録 `_*-not-published.md` は4件中3件が健全な題材停止（偽陽性75%）
# ・8/24 の環境停止は**証拠ファイルを1つも残していない**（材料を作る前に止めたため）
# ・公開本数でも鳴らない（8/22=1本・8/24=3本＝別の回が成功しているので0にならない）
# → 稼ぎ方研究担当と同じ「沈黙禁止の日次ログ」を置き、そこを見るしかない。

def _wlog(*entries):
    """(日, 実測欄) の並びから担当ログを組む。実測欄が None なら欄ごと落とす。"""
    head = "# レシピ担当の日次ログ\n\n## 記録\n\n"
    out = []
    for day, measured in entries:
        block = f"### 2026-08-{day}\n- 公開: 1本\n"
        if measured is not None:
            block += f"- 実測: {measured}\n"
        out.append(block + "\n")
    return head + "".join(out)


_OK = "Agentツール（general-purpose）"


def test_writer_log_today_is_silent():
    assert writer_log_heartbeat(_wlog(("26", _OK)), date(2026, 8, 26)) is None


def test_writer_log_is_quiet_at_exactly_the_boundary():
    # 上限は2日。1晩休んでも鳴らない（0番による正常な停止があるため）
    assert writer_log_heartbeat(_wlog(("24", _OK)), date(2026, 8, 26)) is None


def test_writer_log_silent_too_long_is_detected():
    message = writer_log_heartbeat(_wlog(("23", _OK)), date(2026, 8, 26))
    assert message is not None
    assert "2026-08-23" in message and "3日" in message


def test_writer_log_uses_the_newest_dated_entry():
    assert writer_log_heartbeat(
        _wlog(("20", _OK), ("26", _OK), ("22", _OK)), date(2026, 8, 26)) is None


def test_writer_log_ignores_unrelated_edits():
    # ★91の系列＝ファイルが触られただけで心拍が戻ってはいけない（8/16の素通りと同型）
    stale = _wlog(("23", _OK)) + "\n無関係な追記。日付節ではない。\n"
    assert writer_log_heartbeat(stale, date(2026, 8, 26)) is not None


def test_writer_log_missing_file_is_detected():
    message = writer_log_heartbeat(None, date(2026, 8, 26))
    assert message is not None and "見つかりません" in message


def test_writer_log_without_dated_section_is_detected():
    message = writer_log_heartbeat("日付の節が無い本文", date(2026, 8, 26))
    assert message is not None and "日付の節" in message


def test_environment_blockage_is_detected():
    """🚨 これが本体。★91（実測の相手を立てられない）を、その日のうちに鳴らす。"""
    problems = writer_measurement_gaps(
        _wlog(("26", "❌環境 — create_session が4回とも permission_mode エラー")),
        date(2026, 8, 26),
    )
    assert len(problems) == 1
    assert "★91" in problems[0] and "2026-08-26" in problems[0]
    # 打つ手を必ず添える（記録だけ残して次の担当が探し直すのを防ぐ）
    assert "--safe-mode" in problems[0]


def test_topic_stop_is_not_an_alarm():
    """⚠️ 偽陽性の本体。題材が理由の停止は健全なので鳴らさない（4件中3件がこれ）。"""
    problems = writer_measurement_gaps(
        _wlog(("26", "❌題材 — 見立てた症状が再現しなかった")), date(2026, 8, 26))
    assert problems == []


def test_successful_measurement_is_silent():
    assert writer_measurement_gaps(_wlog(("26", _OK)), date(2026, 8, 26)) == []


def test_old_environment_blockage_is_not_repeated_forever():
    # 直った後も鳴り続けると一覧が読まれなくなる（下限を課さないのと同じ判断）
    problems = writer_measurement_gaps(
        _wlog(("18", "❌環境 — 別セッションを立てられなかった")), date(2026, 8, 26))
    assert problems == []


def test_missing_measurement_field_is_detected():
    """欄ごと消えたら鳴る。消えたまま素通りすると番人が空回りする。"""
    problems = writer_measurement_gaps(_wlog(("26", None)), date(2026, 8, 26))
    assert len(problems) == 1 and "実測" in problems[0]


def test_every_run_of_the_day_is_checked_not_just_the_first():
    """🚨 1日に複数回ある（実測 14:15の回=CLI・21:00の回=Agent が実在）。
    先頭の1行だけ見ると、2回目が塞がった夜を丸ごと見落とす。"""
    log = ("# レシピ担当の日次ログ\n\n## 記録\n\n"
           "### 2026-08-26\n- 公開: 1本\n"
           f"- 実測: {_OK}\n"
           "- 実測: ❌環境 — 2回目の担当は立てられなかった\n\n")
    problems = writer_measurement_gaps(log, date(2026, 8, 26))
    assert len(problems) == 1 and "★91" in problems[0]


def test_writer_measurement_gaps_without_a_file_is_silent():
    """ファイルの不在は heartbeat 側の担当。ここで二重に鳴らさない。"""
    assert writer_measurement_gaps(None, date(2026, 8, 26)) == []


# --- 枯渇を鳴らす番人（2026-08-31 追加）---
#
# 3系統とも「空なのに緑」だった。数え方を直すだけでは足りず、
# 「空である」ことをファイルが言い表せるかどうかが本体だった。


def test_earn_queue_shortage_does_not_count_paused_items():
    """⏸（いま着手できない）は在庫に数えない。床を支えるのは書けるものだけ。"""
    queue = _queue(
        "### 副業（テスト）",
        "- [ ] 書ける題材A",
        "- [ ] 届かない出典の題材",
        "  - ⏸ いま着手できない＝出典に到達できない",
        "- [ ] 前提待ちの題材 ⏸ いま着手できない＝確認待ち",
        "### 次の節",
    )
    problem = earn_queue_shortage(queue, floor=3)
    assert problem is not None
    assert "1件" in problem
    assert "⏸付きが2件" in problem


def test_earn_queue_shortage_still_quiet_when_enough_are_workable():
    queue = _queue(
        "### 副業（テスト）",
        "- [ ] A", "- [ ] B", "- [ ] C",
        "- [ ] 届かない題材",
        "  - ⏸ いま着手できない",
        "### 次の節",
    )
    assert earn_queue_shortage(queue, floor=3) is None


def test_deepdive_queue_shortage_fires_when_empty():
    """毎朝38秒で帰る状態には、これまで番人がいなかった。"""
    problem = deepdive_queue_shortage(_queue("## 待ち行列", "", "- [x] 済み"))
    assert problem is not None
    assert "0件" in problem


def test_deepdive_queue_shortage_does_not_count_blocked_items():
    """⚠️ `- [!]` は再試行の対象外が混ざる。あることが在庫の証明にならない。"""
    problem = deepdive_queue_shortage(_queue("- [!] https://a", "- [!] https://b"))
    assert problem is not None
    assert "保留" in problem and "2件" in problem


def test_deepdive_queue_shortage_is_quiet_with_one_unprocessed():
    assert deepdive_queue_shortage(_queue("- [ ] https://a", "- [!] https://b")) is None
    assert deepdive_queue_shortage(None) is None


def _hypothesis(state: str, backlog: int = 0) -> str:
    lines = [
        "## 優先キュー",
        "### H1 なにか",
        f"- 状態: {state}",
        "- 登録日: 2026-08-25",
        "- 仮説: あ", "- 材料: い", "- 測り方: う",
        "- 試行回数: 10回", "- 反証条件: え", "- 需要: 実質9語",
        "",
        "## バックログ",
    ] + [f"- 案{i}" for i in range(backlog)]
    return _queue(*lines)


def test_hypothesis_stock_empty_fires_when_everything_was_handed_over():
    """📤変換済みだけになったら鳴る＝源0が空。これが今まで無音だった。"""
    problem = hypothesis_stock_empty(_hypothesis("📤変換済み", backlog=7))
    assert problem is not None
    assert "0件" in problem
    assert "バックログに7件" in problem


def test_hypothesis_stock_empty_is_quiet_while_one_is_unstarted():
    assert hypothesis_stock_empty(_hypothesis("⏳未着手", backlog=7)) is None


def test_hypothesis_stock_empty_is_quiet_without_a_file():
    assert hypothesis_stock_empty(None) is None
    assert hypothesis_stock_empty("") is None


def test_hypothesis_stock_empty_does_not_break_the_registration_guard():
    """状態語彙を増やしても、必須欄の判定は変わらない。"""
    assert hypothesis_registration_gaps(_hypothesis("📤変換済み")) == []
