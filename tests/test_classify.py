# -*- coding: utf-8 -*-
from datetime import datetime, timezone

import pytest

from tracker.classify import classify, is_variant_model
from tracker.models import Update

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _update(title):
    return Update(
        uid="u", source_id="s", vendor="V", label="L",
        title=title, url="https://example.com/x", published=NOW, summary="",
    )


@pytest.mark.parametrize("title", [
    "Introducing Claude Code 3",
    "We are launching a new model",
    "Announcing our latest research",
    "GPT-6 is now available",
    "Unveiling the next generation",
])
def test_english_announcement_is_major(title):
    assert classify(_update(title), "rss").importance == "major"


@pytest.mark.parametrize("title", [
    "新モデルを発表しました",
    "Gemini の提供開始について",
    "最新版をリリースしました",
    "研究成果を公開しました",
    "新モデルの概要",
])
def test_japanese_announcement_is_major(title):
    assert classify(_update(title), "rss").importance == "major"


def test_case_is_ignored_for_english():
    assert classify(_update("INTRODUCING A NEW TOOL"), "rss").importance == "major"


@pytest.mark.parametrize("title", [
    "Weekly engineering notes",
    "今週の技術ブログ",
    "Fixing a typo in the docs",
])
def test_ordinary_post_is_minor(title):
    assert classify(_update(title), "rss").importance == "minor"


def test_github_minor_version_bump_is_major():
    assert classify(_update("v1.2.0"), "github_releases").importance == "major"


def test_github_major_version_bump_is_major():
    assert classify(_update("v2.0.0"), "github_releases").importance == "major"


def test_github_patch_release_is_minor():
    assert classify(_update("v1.2.3"), "github_releases").importance == "minor"


def test_version_number_alone_is_minor_for_plain_rss():
    # バージョン番号ルールは github_releases のみに効かせる
    assert classify(_update("v1.2.0"), "rss").importance == "minor"


def test_huggingface_new_base_model_is_major():
    u = _update("deepseek-ai/DeepSeek-V4-Flash-0731")
    assert classify(u, "huggingface").importance == "major"


@pytest.mark.parametrize("model_id", [
    "Qwen/Qwen3-ForcedAligner-0.6B-hf",
    "Qwen/Qwen3-8B-GGUF",
    "org/model-AWQ",
    "org/model-GPTQ",
    "org/model-int4",
    "org/model-int8",
    "org/model-FP8",
    "org/model-bnb",
])
def test_huggingface_variant_is_minor(model_id):
    assert classify(_update(model_id), "huggingface").importance == "minor"


def test_is_variant_model_is_case_insensitive():
    assert is_variant_model("org/model-gguf")
    assert is_variant_model("org/model-GGUF")
    assert not is_variant_model("org/model-v2")


def test_classify_does_not_mutate_input():
    u = _update("Introducing X")
    classify(u, "rss")
    assert u.importance == "minor"


@pytest.mark.parametrize("title", [
    "GPT-5.6: Frontier intelligence that scales with your ambition",
    "Gemini 3.5: frontier intelligence with action",
    "Gemma 4: Byte for byte, the most capable open models",
])
def test_colon_tagline_launch_is_major(title):
    assert classify(_update(title), "rss").importance == "major"


def test_release_word_alone_does_not_make_it_major():
    # MAJOR_EN から "release" を意図的に外している。GitHubのリリース見出しは
    # 常にこの語を含みうるため、入れると全patchが major になって埋もれる。
    u = _update("Release notes for v1.2.3")
    assert classify(u, "github_releases").importance == "minor"


def test_huggingface_base_checkpoint_is_minor():
    # 同日に出る X-Base / X-Instruct で2通になるのを防ぐ。
    assert classify(_update("moonshotai/Kimi-K2-Base"), "huggingface").importance == "minor"
    assert classify(_update("moonshotai/Kimi-K2-Instruct"), "huggingface").importance == "major"


@pytest.mark.parametrize("title", [
    "v1.2.3: Fix memory leak in worker pool",
    "v0.9.7: patch release",
])
def test_colon_patch_release_stays_minor(title):
    # コロン規則が _is_feature_release を上書きしてはいけない。
    assert classify(_update(title), "github_releases").importance == "minor"


def test_colon_feature_release_still_major():
    assert classify(_update("v1.2.0: new provider support"), "github_releases").importance == "major"


def test_openrouter_new_model_is_major():
    assert classify(_update("x-ai/grok-4.5"), "openrouter").importance == "major"


@pytest.mark.parametrize("model_id", [
    "x-ai/grok-4.5:free",
    "x-ai/grok-4.5:thinking",
    "anthropic/claude-opus-5:beta",
])
def test_openrouter_tagged_variant_is_minor(model_id):
    # OpenRouter は ":free" などのタグでベースモデルの派生を表す。
    assert classify(_update(model_id), "openrouter").importance == "minor"
