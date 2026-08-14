# -*- coding: utf-8 -*-
"""題材の候補あつめのテスト。

⚠️ **本物の Google は叩かない。**fetch を差し替えて検査する。
外を叩くテストは、ネットの調子で赤くなって「テストが赤いのは普通」を教えてしまう。
"""
from datetime import date

from tools.suggest_topics import (
    SEED_BANKS,
    TOOLS,
    SUFFIXES,
    classify,
    existing_coverage,
    is_noise,
    is_off_topic,
    report,
    sweep,
)


def test_sweep_asks_every_combination():
    asked = []

    def fake(query):
        asked.append(query)
        return [f"{query} の候補"]

    collected, failures = sweep(("種A", "種B"), tools=("chatgpt",),
                               suffixes=("", "コツ"), fetch=fake, pause=0)
    assert failures == 0
    assert asked == ["chatgpt 種A", "chatgpt 種A コツ", "chatgpt 種B", "chatgpt 種B コツ"]
    assert set(collected) == {"種A", "種B"}


def test_sweep_counts_failures_and_keeps_going():
    """1つ失敗しても止まらない。途中で止めるとどこまで採れたか分からなくなる。"""
    def fake(query):
        if "種B" in query:
            raise RuntimeError("落ちた")
        return ["語"]

    collected, failures = sweep(("種A", "種B"), tools=("ai",), suffixes=("",),
                                fetch=fake, pause=0)
    assert failures == 1
    assert collected["種A"] == {"語"}


def test_katakana_ai_misfire_is_noise():
    """種の ai が「アイ」に転記された誤ヒット（メルカリ128語のうち34語がこれだった）。"""
    assert is_noise("アイ カツ カード メルカリ 相場")
    assert is_noise("アイ ラッシュ サロン 集客 方法")
    assert not is_noise("chatgpt メルカリ 出品 自動化")


def test_tool_self_talk_is_noise():
    """AIツール自身の課金や、英語の note（議事録アプリ）は作業の需要ではない。"""
    assert is_noise("chatgpt 請求書 ダウンロード")
    assert is_noise("ai note taker for teams")
    assert is_noise("gemini notebooklm")
    assert not is_noise("ai note 収益化")  # これは本物の note.com


def test_off_topic_is_separate_from_noise():
    """「対象外」と「ノイズ」を混ぜない。投資は領域外、ノイズは誤ヒット。"""
    assert is_off_topic("ai 投資 実績")
    assert not is_noise("ai 投資 実績")


def test_classify_puts_every_word_somewhere():
    """全件どれかに入る（台帳5番＝単一条件で抜くと隣接が静かに落ちる）。"""
    rows = classify({"種": {"アイ カツ メルカリ", "ai 副業 料金", "chatgpt 種 やり方"}})
    row = rows[0]
    assert row["raw"] == 3
    assert len(row["noise"]) + len(row["off_topic"]) + len(row["real"]) == row["raw"]


def test_classify_sorts_by_real_not_raw():
    """順位は生ではなく実質で付ける。生で並べると note が1位になってしまう。"""
    rows = classify({
        "ノイズだらけ": {f"アイ {i} 語" for i in range(10)} | {"chatgpt ノイズだらけ"},
        "本物": {f"chatgpt 本物 {i}" for i in range(5)},
    })
    assert [r["seed"] for r in rows] == ["本物", "ノイズだらけ"]


def test_existing_coverage_marks_articles_and_queue(tmp_path):
    recipes = tmp_path / "recipes"
    recipes.mkdir()
    (recipes / "a.md").write_text("見積もりの話", encoding="utf-8")
    queue = tmp_path / "_recipe_queue.md"
    queue.write_text("- [ ] 通知の題材", encoding="utf-8")

    rows = existing_coverage(
        classify({"見積もり": {"x"}, "通知": {"y"}, "未出": {"z"}}),
        recipes_dir=recipes, queue_path=queue,
    )
    by_seed = {r["seed"]: r for r in rows}
    assert by_seed["見積もり"]["in_articles"] and not by_seed["見積もり"]["in_queue"]
    assert by_seed["通知"]["in_queue"] and not by_seed["通知"]["in_articles"]
    assert not by_seed["未出"]["in_articles"] and not by_seed["未出"]["in_queue"]


def test_report_says_it_is_not_a_decision():
    """候補を決定として読ませない。語数の上位が採用とは限らない（8/14 の実測）。"""
    rows = existing_coverage(classify({"通知": {"chatgpt 通知 やり方"}}),
                             recipes_dir=RECIPES_FIXTURE, queue_path=QUEUE_FIXTURE)
    text = report("automate", rows, 0, 1200, date(2026, 8, 14))
    assert "候補であって決定ではない" in text
    assert "2026-08-14" in text


def test_report_shows_dropped_counts():
    """落とした数を表に出す。黙って消すと「確かめた」と誤解される。"""
    rows = existing_coverage(
        classify({"種": {"アイ カツ 語", "ai 種 料金", "chatgpt 種 やり方"}}),
        recipes_dir=RECIPES_FIXTURE, queue_path=QUEUE_FIXTURE,
    )
    text = report("automate", rows, 0, 80, date(2026, 8, 14))
    assert "| 種 | 3 | 1 | 1 | **1** |" in text


def test_suffixes_carry_no_intent_words():
    """語尾に「自動」「プロンプト」を入れない。採取を偏らせると需要が自作自演になる。"""
    for bad in ("自動", "プロンプト", "自動化", "ループ"):
        assert bad not in SUFFIXES


def test_seed_banks_do_not_overlap():
    """束どうしで種が重なっていないこと（同じ種は同じ語しか返さない）。"""
    seen: dict[str, str] = {}
    for bank, seeds in SEED_BANKS.items():
        for seed in seeds:
            assert seed not in seen, f"{seed} が {seen.get(seed)} と {bank} で重複"
            seen[seed] = bank


def test_tools_are_the_same_five_as_the_earlier_runs():
    """ツールを増減すると過去の回と語数が比べられなくなる（8/10 以来固定）。"""
    assert TOOLS == ("chatgpt", "claude", "gemini", "生成ai", "ai")


# report() は実ファイルを触らないので、既存の実物を使う（存在確認も兼ねる）
from tools.suggest_topics import QUEUE_PATH as QUEUE_FIXTURE  # noqa: E402
from tools.suggest_topics import RECIPES_DIR as RECIPES_FIXTURE  # noqa: E402
