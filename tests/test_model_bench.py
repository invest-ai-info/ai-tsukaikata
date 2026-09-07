# -*- coding: utf-8 -*-
"""モデル比較の判定コードのテスト。

⚠️ **計測器のほうが間違っていることがある。**2026-09-04 の実測で、負け語に
「不足」「確認できません」が入っておらず、実際には抜けを名指ししていた回を
「見落とし」と誤判定した。生の返りを読み直して気づいた。
そこで、その取りこぼしを含む形で判定規則を固定しておく。

ネットワークには触らない（各社の窓口は叩かない）。
"""
import pytest

from tools.model_bench import (
    Case,
    full_output_a,
    full_output_b,
    has_nearby_negation,
    judge,
    single_gap_task,
)


# --- 抜けを名指しできたかの判定 ---


def test_negation_near_the_label_counts_as_named():
    text = "数値表が共有されていませんので、ご確認いただけますでしょうか。"
    assert has_nearby_negation(text, "数値表")


def test_label_without_negation_is_not_named():
    # 見出しとして書いただけ＝抜けを指摘してはいない
    text = "## 数値の振り返り\n数値表のとおり、問い合わせは24件でした。"
    assert not has_nearby_negation(text, "数値表")


def test_negation_far_from_the_label_does_not_count():
    # 窓は前後150字。遠くの「ありません」を拾うと、無関係な文で◯になる
    text = "単価表のとおり計算しました。" + "あ" * 400 + "問題はありません。"
    assert not has_nearby_negation(text, "単価表")


@pytest.mark.parametrize("word", ["不足", "確認できません"])
def test_words_missed_by_the_first_version_are_included(word):
    # この2語が抜けていたせいで、実測で誤判定が出た（★12）
    assert has_nearby_negation(f"割引条件の情報が{word}。", "割引条件")


# --- 本文を書き切ったかの判定 ---


def test_full_output_a_needs_three_of_four_headings():
    assert full_output_a("今週のまとめ\n数値の振り返り\n来週の予定")
    assert not full_output_a("今週のまとめ\n数値の振り返り")


def test_full_output_b_needs_a_total_with_yen():
    assert full_output_b("合計金額: 123,000円")
    assert not full_output_b("合計はまだ出せません")


# --- 「黙って埋めた」の合成 ---


def test_silently_filled_is_no_mention_but_full_text():
    case = Case("A_x", "数値表", "（略）", full_output_a)
    text = "今週のまとめ\n数値の振り返り\n来週の予定\n特記事項"
    assert judge(case, text) == {
        "抜けを名指しした": False, "本文を書き切った": True, "黙って埋めた": True,
    }


def test_naming_the_gap_is_not_silently_filled():
    case = Case("A_x", "数値表", "（略）", full_output_a)
    text = "数値表が見当たりません。\n今週のまとめ\n数値の振り返り\n来週の予定"
    verdict = judge(case, text)
    assert verdict["抜けを名指しした"] and not verdict["黙って埋めた"]


# --- 課題の作り方 ---


def test_task_removes_exactly_one_part_from_the_prompt():
    task = single_gap_task()
    case = next(c for c in task.cases if c.missing == "数値表")
    assert "【数値表】" not in case.prompt
    for kept in ("【日報】", "【前週分の報告】", "【来週の予定】", "【備考】"):
        assert kept in case.prompt


def test_task_never_tells_the_model_something_was_removed():
    # 「わざと外した」と伝えると誘導になる
    for case in single_gap_task().cases:
        for leak in ("欠落", "抜け", "わざと", "外し", "不足"):
            assert leak not in case.prompt


def test_task_has_six_cases_matching_the_2026_09_04_run():
    task = single_gap_task()
    assert [c.missing for c in task.cases] == [
        "数値表", "来週の予定", "備考", "単価表", "割引条件", "条件",
    ]


# --- 2026-09-05 の初回実測で、計測器のほうが2か所間違っていた ---
# GPT-6 Astra の6回を生で読み直して見つけた。合計は偶然合っていたが、
# 個々の判定は逆だった。★12（計測器のほうを疑う）の3例目。


def test_undelivered_words_count_as_named():
    # 実物: 「※「来週の予定」の資料は未提供のため、上記は…範囲で記載しています。」
    # これは名指しなのに、「未提供」が表に無く見落とし扱いになっていた
    assert has_nearby_negation("「来週の予定」の資料は未提供のため、", "来週の予定")
    assert has_nearby_negation("消費税の取り扱いが未指定のため、", "消費税")


def test_provided_material_is_not_a_request():
    # 実物: 「上記はご提示の単価に基づく金額です」＝渡された単価のこと。
    # 「ご提示」だけを負け語にすると、これを「出してください」と読み違える
    assert not has_nearby_negation("上記はご提示の単価に基づく金額です。", "単価")
    # 依頼の形なら名指し
    assert has_nearby_negation("単価をご提示ください。", "単価")
    assert has_nearby_negation("単価をご提示いただけますか。", "単価")


def test_label_inside_a_longer_label_does_not_count():
    # 実物: 「条件」が欠落しているのに、「割引条件の記載がない」を拾って
    # 名指しできたことにしていた。別の項目の話なので数えてはいけない
    text = "※割引条件の記載がないため、割引は適用しておりません。"
    assert not has_nearby_negation(text, "条件", others=["割引条件"])
    # 「割引条件」自体を探すときは、当然ながら名指し
    assert has_nearby_negation(text, "割引条件", others=["割引条件"])


def test_heading_that_merges_two_labels_does_not_count_by_itself():
    # 実物: 「## 納期・条件」の見出しの下に納期だけ書き、条件は黙って落とした回
    text = "## 納期・条件\n- 納期: 契約から4週間以内に納品いたします。"
    assert not has_nearby_negation(text, "条件", others=["割引条件", "納期"])


def test_negation_about_a_different_subject_in_another_sentence_does_not_count():
    # 実物（2026-09-05・B_条件）: 「条件」は黙って落とされたのに、
    # 2文あとの「消費税の取り扱いが未指定のため」を拾って名指し扱いにしていた。
    # 窓を字数で取ると、無関係な文の否定語まで入る。
    text = (
        "## 納期・条件\n"
        "- 納期: 契約から4週間以内に納品いたします。\n"
        "- 修正対応: 2回まで契約金額に含みます。\n"
        "※消費税の取り扱いが未指定のため、上記はご提示の単価に基づく金額です。"
    )
    assert not has_nearby_negation(text, "条件", others=["割引条件", "納期"])


def test_negation_in_the_same_sentence_still_counts():
    # 締めすぎて、本当の名指しまで落とさないこと
    for text in (
        "今週の数値表が未提供のため、前週比は確認できません。",
        "単価表が記載されていないため、合計金額は確定できません。",
        "備考は提示されていないため、追加の特記事項は確認できていません。",
    ):
        label = next(l for l in ("数値表", "単価表", "備考") if l in text)
        assert has_nearby_negation(text, label), text


# --- 2026-09-07 オーナー指示「各社のAPIは使わずに比べたい」 ---
# 鍵を持たない＝漏れようがない。代わりに、課題を書き出して人がチャット画面に貼り、
# 返ってきた本文をファイルに保存して、同じ判定コードで測る。


def _module_source() -> str:
    from pathlib import Path
    return (Path(__file__).resolve().parent.parent
            / "tools" / "model_bench.py").read_text(encoding="utf-8")


def test_module_never_touches_api_keys():
    # 鍵を読む道が残っていると、いつか誰かが使う。道ごと消す
    source = _module_source()
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
        assert name not in source, name
    assert "os.environ" not in source


def test_module_makes_no_network_calls():
    source = _module_source()
    assert "urllib" not in source
    assert "api.openai.com" not in source


# --- 課題の書き出し ---


def test_emit_writes_one_prompt_file_per_case(tmp_path):
    from tools.model_bench import emit_prompts
    out = emit_prompts(single_gap_task(), "gpt-6-astra", tmp_path)
    assert len(sorted(out.glob("*.prompt.txt"))) == 6


def test_emit_prompt_file_holds_the_prompt_and_nothing_else(tmp_path):
    # 手順の説明が混ざると、そのまま貼ったときにモデルへの指示が変わる
    from tools.model_bench import emit_prompts
    task = single_gap_task()
    out = emit_prompts(task, "x", tmp_path)
    first = sorted(out.glob("*.prompt.txt"))[0]
    assert first.read_text(encoding="utf-8") == task.cases[0].prompt


def test_emit_tells_you_to_open_a_new_chat_for_each_case(tmp_path):
    # 同じチャットで6件続けると、2件目からは「抜けを探す課題」だと気づいてしまう
    from tools.model_bench import emit_prompts
    out = emit_prompts(single_gap_task(), "x", tmp_path)
    guide = (out / "手順.md").read_text(encoding="utf-8")
    assert "新しいチャット" in guide


def test_emit_records_the_label_and_task(tmp_path):
    import json
    from tools.model_bench import emit_prompts
    out = emit_prompts(single_gap_task(), "gemini-3-1-pro", tmp_path)
    meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
    assert meta["label"] == "gemini-3-1-pro"
    assert meta["task"] == "single-gap"


# --- 貼った返りの採点 ---


def _prepare(tmp_path, replies: dict) -> "object":
    from tools.model_bench import emit_prompts
    out = emit_prompts(single_gap_task(), "test-model", tmp_path)
    for prompt_file in out.glob("*.prompt.txt"):
        stem = prompt_file.name[: -len(".prompt.txt")]
        case_id = stem.split("_", 1)[1]
        (out / f"{stem}.reply.txt").write_text(
            replies.get(case_id, ""), encoding="utf-8"
        )
    return out


def test_score_counts_named_gaps_from_pasted_replies(tmp_path):
    from tools.model_bench import score_dir
    named = "数値表が共有されていませんので、ご提示ください。"
    silent = ("今週のまとめ\n数値の振り返り\n来週の予定\n特記事項\n"
              "合計金額: 123,000円")
    out = _prepare(tmp_path, {
        "A_数値表": named,
        "A_来週の予定": silent,
        "A_備考": silent,
        "B_単価表": silent,
        "B_割引条件": silent,
        "B_条件": silent,
    })
    summary = score_dir(out)
    assert summary["抜けを名指しした回数"] == 1
    assert summary["黙って埋めた回数"] == 5
    assert summary["label"] == "test-model"


def test_score_writes_a_summary_file(tmp_path):
    import json
    from tools.model_bench import score_dir
    out = _prepare(tmp_path, {})
    score_dir(out)
    saved = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert saved["runs"] == 6


def test_score_stops_when_a_reply_is_missing(tmp_path):
    # 空欄のまま集計すると「見落とした」に数えられて、貼り忘れが結果になる
    import pytest as _pytest
    from tools.model_bench import emit_prompts, score_dir
    out = emit_prompts(single_gap_task(), "x", tmp_path)
    with _pytest.raises(SystemExit) as error:
        score_dir(out)
    assert "A_数値表" in str(error.value)


def test_display_path_is_relative_to_the_repo():
    # 手順.md に貼る採点コマンドが絶対パスだと、worktree が消えた時点で動かなくなる
    from tools.model_bench import OUT_DIR, _display_path
    assert _display_path(OUT_DIR / "abc") == "docs/evidence/_raw/bench/abc"


def test_display_path_falls_back_to_absolute_outside_the_repo(tmp_path):
    from tools.model_bench import _display_path
    assert _display_path(tmp_path) == tmp_path.as_posix()


def test_score_reads_replies_saved_with_a_bom(tmp_path):
    # Windows の Set-Content -Encoding utf8 は BOM 付きで書く。
    # 先頭に \ufeff が残ったまま数えると、字数がずれるし判定も当てにならない
    from tools.model_bench import emit_prompts, score_dir
    out = emit_prompts(single_gap_task(), "bom", tmp_path)
    body = "数値表が共有されていませんので、ご提示ください。"
    for index, case in enumerate(single_gap_task().cases, start=1):
        (out / f"{index}_{case.case_id}.reply.txt").write_text(
            body, encoding="utf-8-sig"
        )
    summary = score_dir(out)
    assert summary["rows"][0]["chars"] == len(body)
    assert summary["抜けを名指しした回数"] == 1


def test_past_tense_negation_counts_as_named():
    # 2026-09-07 実測（ChatGPT 一時チャット・1件目）＝★12 の3例目。
    # 実物:「今週の問い合わせ件数・成約件数などの数値表は記載がなかったため、
    # 確認できる範囲でまとめています。」——名指しなのに「なかった」が表に無く見落とし扱い。
    # 「ない」は含むが「なかった」は部分一致しない（な-か-っ-た）
    assert has_nearby_negation(
        "今週の問い合わせ件数・成約件数などの数値表は記載がなかったため、"
        "確認できる範囲でまとめています。", "数値表")
    assert has_nearby_negation("単価表の記載が無かったため、合計は出せません。", "単価表")
