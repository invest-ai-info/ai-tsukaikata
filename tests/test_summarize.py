# -*- coding: utf-8 -*-
import json

import pytest

from tracker import summarize as summarize_module
from tracker.summarize import (
    apply_summaries,
    build_prompt,
    needs_summary,
    parse_response,
)

TYPES = {
    "anthropic-news": "anthropic_news",
    "openai-news": "rss",
    "hf-deepseek": "huggingface",
    "claude-code": "github_releases",
    "openrouter-qwen": "openrouter",
}


def _item(uid="a", source_id="anthropic-news", **kw):
    item = {
        "uid": uid,
        "source_id": source_id,
        "vendor": "Anthropic",
        "title": "Introducing Thing",
        "url": "https://example.com/x",
        "published": "2026-08-01T15:00:00+00:00",
        "summary": "A short summary of the thing.",
    }
    item.update(kw)
    return item


# --- どれを要約するか ---


def test_announcement_sources_need_a_summary():
    assert needs_summary(_item(source_id="anthropic-news"), TYPES)
    assert needs_summary(_item(source_id="openai-news"), TYPES)


@pytest.mark.parametrize("source_id", ["hf-deepseek", "claude-code", "openrouter-qwen"])
def test_model_releases_do_not_need_a_summary(source_id):
    # モデルが出たことは「見る」もので「読む」ものではない。名前と件数で足りる。
    # ここを要約に回すと、37件の日に費用も待ち時間も跳ね上がる。
    assert not needs_summary(_item(source_id=source_id), TYPES)


def test_already_summarized_item_is_skipped():
    assert not needs_summary(_item(summary_ja="もう入っている"), TYPES)


def test_unknown_source_is_skipped():
    # sources.yml から消えたソースの記事。型が分からないものは触らない。
    assert not needs_summary(_item(source_id="removed-source"), TYPES)


# --- プロンプト ---


def test_prompt_contains_every_uid_and_title():
    prompt = build_prompt([_item("a", title="One"), _item("b", title="Two")])
    assert "a" in prompt and "b" in prompt
    assert "One" in prompt and "Two" in prompt


def test_prompt_forbids_inventing_facts():
    # 題名と200字の説明しか渡せない。足りないぶんを埋めさせない指示は必須。
    prompt = build_prompt([_item()])
    assert "推測" in prompt


# --- 応答の解釈 ---


def test_parse_response_maps_summaries_by_uid():
    body = json.dumps([{"uid": "a", "summary_ja": "1行目\n2行目\n3行目"}])
    assert parse_response(body, {"a"}) == {"a": "1行目\n2行目\n3行目"}


def test_parse_response_accepts_fenced_json():
    body = "```json\n" + json.dumps([{"uid": "a", "summary_ja": "本文"}]) + "\n```"
    assert parse_response(body, {"a"}) == {"a": "本文"}


def test_parse_response_drops_uid_we_did_not_ask_for():
    # 頼んでいないuidを受け入れると、別の記事に他人の要約が付く。
    body = json.dumps([
        {"uid": "a", "summary_ja": "正しい"},
        {"uid": "でっちあげ", "summary_ja": "誤り"},
    ])
    assert parse_response(body, {"a"}) == {"a": "正しい"}


def test_parse_response_drops_empty_summary():
    body = json.dumps([{"uid": "a", "summary_ja": "   "}])
    assert parse_response(body, {"a"}) == {}


def test_parse_response_clips_overlong_summary():
    body = json.dumps([{"uid": "a", "summary_ja": "あ" * 500}])
    result = parse_response(body, {"a"})
    assert len(result["a"]) <= summarize_module.MAX_SUMMARY_CHARS


def test_parse_response_returns_empty_on_garbage():
    # 落とさない。要約はあれば嬉しいだけの派生データで、無くても記事は残る。
    assert parse_response("not json at all", {"a"}) == {}


# --- 反映 ---


def _client(mapping):
    def call(prompt):
        asked = [u for u in mapping if u in prompt]
        return json.dumps([{"uid": u, "summary_ja": mapping[u]} for u in asked])
    return call


def test_apply_summaries_writes_into_the_items():
    items = [_item("a"), _item("b")]
    added = apply_summaries(items, _client({"a": "Aの要約", "b": "Bの要約"}))
    assert added == 2
    assert items[0]["summary_ja"] == "Aの要約"


def test_apply_summaries_records_which_model_wrote_it():
    # 機械生成である旨を残す。about.md の「体験と調べたことを混ぜない」ため。
    items = [_item("a")]
    apply_summaries(items, _client({"a": "要約"}))
    assert items[0]["summary_source"] == "gemini"


def test_apply_summaries_survives_a_failing_batch(monkeypatch):
    monkeypatch.setattr(summarize_module, "BATCH_SIZE", 1)
    items = [_item("a"), _item("b")]

    def flaky(prompt):
        if "a" in prompt and "b" not in prompt:
            raise RuntimeError("api down")
        return json.dumps([{"uid": "b", "summary_ja": "Bだけ成功"}])

    added = apply_summaries(items, flaky)
    assert added == 1
    assert "summary_ja" not in items[0]
    assert items[1]["summary_ja"] == "Bだけ成功"


def test_apply_summaries_respects_the_per_run_cap(monkeypatch):
    # 暴走で課金を焼かないための歯止め。残りは次の実行で拾う。
    monkeypatch.setattr(summarize_module, "MAX_ITEMS_PER_RUN", 2)
    items = [_item(u) for u in ("a", "b", "c", "d")]
    added = apply_summaries(items, _client({u: "要約" for u in "abcd"}))
    assert added == 2


def test_apply_summaries_does_nothing_without_items():
    assert apply_summaries([], _client({})) == 0
