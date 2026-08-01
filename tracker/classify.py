# -*- coding: utf-8 -*-
"""更新の重要度を判定する。ネットワークもファイルも触らない純粋関数。

判定に迷う場合は minor に倒す。minor もダイジェストには必ず載るため
情報は失われず、最大24時間遅れるだけ。逆に major に倒すと通知が溢れて
全部読まなくなり、そちらのほうが実害が大きい。
"""
from __future__ import annotations

import re

from .models import Update

# 英語の発表語。"release" は入れない（GitHubのリリースは常にこの語を含むため）
MAJOR_EN = (
    "introducing",
    "launch",
    "announcing",
    "now available",
    "unveil",
)

MAJOR_JA = ("発表", "提供開始", "リリース", "公開しました", "新モデル")

# HuggingFace の派生モデル（量子化版・形式違い）の接尾辞
VARIANT_SUFFIXES = (
    "-gguf", "-awq", "-gptq", "-int4", "-int8", "-fp8", "-hf", "-bnb",
)

_VERSION_RE = re.compile(r"v?(\d+)\.(\d+)\.(\d+)")


def is_variant_model(model_id: str) -> bool:
    """HuggingFace の派生モデルか（量子化版など）。"""
    return model_id.lower().endswith(VARIANT_SUFFIXES)


def _has_announcement_word(title: str) -> bool:
    lowered = title.lower()
    if any(word in lowered for word in MAJOR_EN):
        return True
    return any(word in title for word in MAJOR_JA)


def _is_feature_release(title: str) -> bool:
    """バージョン番号を含み、patch が 0（＝機能リリース）なら True。"""
    match = _VERSION_RE.search(title)
    if not match:
        return False
    return int(match.group(3)) == 0


def classify(update: Update, source_type: str) -> Update:
    """importance を付けた新しい Update を返す。入力は変更しない。"""
    if source_type == "huggingface":
        importance = "minor" if is_variant_model(update.title) else "major"
        return update.with_importance(importance)

    if _has_announcement_word(update.title):
        return update.with_importance("major")

    if source_type == "github_releases" and _is_feature_release(update.title):
        return update.with_importance("major")

    return update.with_importance("minor")
