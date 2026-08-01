# -*- coding: utf-8 -*-
"""トラッカー全体で共有するデータ型。ネットワークもファイルも触らない。

要約の文字数上限と出典URL必須は著作権対策であり、ここで機械的に強制する。
"""
from __future__ import annotations

import hashlib
import html
import re
from dataclasses import asdict, dataclass, replace
from datetime import datetime

SUMMARY_MAX_CHARS = 200

_TAG_RE = re.compile(r"<[^>]+>")


def make_uid(source_id: str, entry_id: str) -> str:
    """ソースIDとエントリIDから安定した重複判定キーを作る。"""
    raw = f"{source_id}::{entry_id}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def clip_summary(text: str) -> str:
    """HTMLを落とし、空白を潰し、SUMMARY_MAX_CHARS で切る。"""
    cleaned = _TAG_RE.sub(" ", text or "")
    cleaned = html.unescape(cleaned)
    cleaned = " ".join(cleaned.split())
    if len(cleaned) <= SUMMARY_MAX_CHARS:
        return cleaned
    return cleaned[: SUMMARY_MAX_CHARS - 1] + "…"


@dataclass(frozen=True)
class Update:
    uid: str
    source_id: str
    vendor: str  # 会社名（グルーピングとメール件名の接頭辞に使う）
    label: str  # フィード個別の人間向け表示名
    title: str
    url: str
    published: datetime  # tz-aware UTC
    summary: str
    importance: str = "minor"  # "major" | "minor"

    def __post_init__(self) -> None:
        if not self.url:
            raise ValueError("Update.url は必須（出典を必ず示すため）")
        if self.published.tzinfo is None:
            raise ValueError("Update.published は tz-aware である必要があります")
        object.__setattr__(self, "summary", clip_summary(self.summary))

    def with_importance(self, importance: str) -> "Update":
        return replace(self, importance=importance)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["published"] = self.published.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Update":
        d = dict(d)
        d["published"] = datetime.fromisoformat(d["published"])
        return cls(**d)
