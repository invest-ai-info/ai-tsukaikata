# AI更新情報トラッカー Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 主要AIベンダーの新機能・新モデルを毎時自動で捕捉し、重要なものは即時メール・それ以外は毎朝のダイジェストで運営者に届ける。

**Architecture:** `tracker/` パッケージ。外界（ネットワーク・ファイル・SMTP）に触るのは `fetch.py` / `store.py` / `notify.py` の3つだけで、`models.py` と `classify.py` は純粋。テストは全てインメモリで、ネットワークに一切出ない。GitHub Actions の cron 2本（毎時チェック / 毎朝ダイジェスト）から `run.py` を叩く。

**Tech Stack:** Python 3.12 / feedparser（導入済み） / PyYAML / pytest / GitHub Actions / Gmail SMTP

**設計書:** [2026-08-01-ai-update-tracker-design.md](../specs/2026-08-01-ai-update-tracker-design.md)

**設計書からの差分（意図的）:**
1. `Update` 型を `fetch.py` ではなく **`models.py`** に置く。`classify.py` が `fetch.py` を import するとネットワーク依存が純粋モジュールに漏れるため。
2. 設計書に明記していなかった **`pending_minor` キュー** を `seen.json` に追加する。毎時チェックが minor を既読にしてしまうと、翌朝のダイジェストに載せるものが消えるため。

---

## File Structure

| ファイル | 責務 | 外界に触るか |
|---|---|---|
| `tracker/models.py` | `Update` 型。要約200文字上限と出典URL必須をコンストラクタで強制 | しない |
| `tracker/classify.py` | 重要度判定（major / minor） | しない |
| `tracker/fetch.py` | `sources.yml` 読み込みと3種別の取得・正規化 | ネットワーク |
| `tracker/store.py` | 既読管理・minorキュー・ソース死活・古いID掃除 | ファイル |
| `tracker/notify.py` | メール本文の組み立てと送信 | SMTP |
| `tracker/run.py` | 上記を繋ぐエントリポイント（`--mode check/digest/bootstrap`） | — |
| `tracker/sources.yml` | 追跡対象の定義（コード変更なしで増やせる） | — |
| `.github/workflows/tracker.yml` | 毎時チェック | — |
| `.github/workflows/tracker-digest.yml` | 毎朝ダイジェスト | — |

---

### Task 1: プロジェクトの土台

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `tracker/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: 依存とpytest設定を作る**

`requirements.txt`:
```
feedparser>=6.0.11
PyYAML>=6.0.1
pytest>=8.0.0
```

`pyproject.toml`:
```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

`.gitignore`:
```
__pycache__/
*.pyc
.pytest_cache/
build/
.venv/
```

`tracker/__init__.py`: 空ファイル
`tests/__init__.py`: 空ファイル

- [ ] **Step 2: 依存をインストールする**

Run: `pip install -r requirements.txt`
Expected: feedparser は導入済みのためスキップ、PyYAML と pytest が新規インストールされる

- [ ] **Step 3: pytestが動くことを確認する**

Run: `python -m pytest -q`
Expected: `no tests ran` （エラーではなくテスト0件で終了すればOK）

- [ ] **Step 4: Commit**

```bash
git add requirements.txt pyproject.toml .gitignore tracker/__init__.py tests/__init__.py
git commit -m "chore: トラッカーの土台（依存・pytest設定・パッケージ）を追加"
```

---

### Task 2: `models.py` — Update型と著作権ガード

要約の200文字上限と出典URL必須を、コンストラクタで機械的に強制する。ここを型で守ることで、以降のどのモジュールからも規則を破れなくなる。

**Files:**
- Create: `tracker/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_models.py`:
```python
# -*- coding: utf-8 -*-
from datetime import datetime, timezone

import pytest

from tracker.models import SUMMARY_MAX_CHARS, Update, clip_summary, make_uid

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _update(**kwargs):
    base = dict(
        uid="abc123",
        source_id="openai-news",
        vendor="OpenAI",
        label="OpenAI News",
        title="Introducing something",
        url="https://example.com/a",
        published=NOW,
        summary="短い要約",
    )
    base.update(kwargs)
    return Update(**base)


def test_make_uid_is_stable_and_source_scoped():
    assert make_uid("s1", "e1") == make_uid("s1", "e1")
    assert make_uid("s1", "e1") != make_uid("s2", "e1")


def test_clip_summary_strips_html_and_collapses_whitespace():
    assert clip_summary("<p>hello   <b>world</b></p>") == "hello world"


def test_clip_summary_unescapes_entities():
    assert clip_summary("A &amp; B") == "A & B"


def test_summary_is_clipped_to_limit():
    long_text = "あ" * 500
    u = _update(summary=long_text)
    assert len(u.summary) == SUMMARY_MAX_CHARS
    assert u.summary.endswith("…")


def test_short_summary_is_untouched():
    u = _update(summary="短い要約")
    assert u.summary == "短い要約"


def test_url_is_required():
    with pytest.raises(ValueError):
        _update(url="")


def test_importance_defaults_to_minor():
    assert _update().importance == "minor"


def test_with_importance_returns_new_object():
    u = _update()
    major = u.with_importance("major")
    assert major.importance == "major"
    assert u.importance == "minor"


def test_roundtrip_dict():
    u = _update()
    assert Update.from_dict(u.to_dict()) == u
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_models.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tracker.models'`

- [ ] **Step 3: 実装する**

`tracker/models.py`:
```python
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
    vendor: str
    label: str
    title: str
    url: str
    published: datetime  # tz-aware UTC
    summary: str
    importance: str = "minor"  # "major" | "minor"

    def __post_init__(self) -> None:
        if not self.url:
            raise ValueError("Update.url は必須（出典を必ず示すため）")
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
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_models.py -q`
Expected: PASS（9 passed）

- [ ] **Step 5: Commit**

```bash
git add tracker/models.py tests/test_models.py
git commit -m "feat: Update型を追加。要約200文字上限と出典URL必須を型で強制"
```

---

### Task 3: `classify.py` — 重要度判定

このプロジェクトで最もテストを厚くする箇所。誤判定は minor に倒す（ダイジェストには必ず載るので情報は失われず、最大24時間遅れるだけ）。

**Files:**
- Create: `tracker/classify.py`
- Test: `tests/test_classify.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_classify.py`:
```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_classify.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tracker.classify'`

- [ ] **Step 3: 実装する**

`tracker/classify.py`:
```python
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
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_classify.py -q`
Expected: PASS（29 passed）

- [ ] **Step 5: Commit**

```bash
git add tracker/classify.py tests/test_classify.py
git commit -m "feat: 重要度判定を追加。迷ったらminorに倒す方針をテストで固定"
```

---

### Task 4: `fetch.py` — 3種別の取得と正規化

テストはネットワークに出ない。固定のサンプルを `tests/fixtures/` に置いてパース関数だけを検証する。

**Files:**
- Create: `tracker/fetch.py`
- Create: `tests/fixtures/sample_rss.xml`
- Create: `tests/fixtures/sample_releases.atom`
- Create: `tests/fixtures/sample_hf_models.json`
- Test: `tests/test_fetch.py`

- [ ] **Step 1: フィクスチャを作る**

`tests/fixtures/sample_rss.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sample News</title>
    <item>
      <title>Introducing a new model</title>
      <link>https://example.com/news/1</link>
      <pubDate>Fri, 01 Aug 2026 09:00:00 GMT</pubDate>
      <description>&lt;p&gt;We are &lt;b&gt;excited&lt;/b&gt; to share this.&lt;/p&gt;</description>
    </item>
    <item>
      <title>Weekly notes</title>
      <link>https://example.com/news/2</link>
      <pubDate>Thu, 31 Jul 2026 09:00:00 GMT</pubDate>
      <description>Ordinary post.</description>
    </item>
    <item>
      <title>Broken entry without link</title>
      <pubDate>Wed, 30 Jul 2026 09:00:00 GMT</pubDate>
      <description>No link here.</description>
    </item>
  </channel>
</rss>
```

`tests/fixtures/sample_releases.atom`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Releases</title>
  <entry>
    <id>tag:github.com,2008:Repository/1/v1.2.0</id>
    <title>v1.2.0</title>
    <updated>2026-08-01T10:00:00Z</updated>
    <link rel="alternate" type="text/html" href="https://github.com/o/r/releases/tag/v1.2.0"/>
    <content type="html">Added a feature.</content>
  </entry>
  <entry>
    <id>tag:github.com,2008:Repository/1/v1.1.3</id>
    <title>v1.1.3</title>
    <updated>2026-07-28T10:00:00Z</updated>
    <link rel="alternate" type="text/html" href="https://github.com/o/r/releases/tag/v1.1.3"/>
    <content type="html">Fixed a bug.</content>
  </entry>
</feed>
```

`tests/fixtures/sample_hf_models.json`:
```json
[
  {"modelId": "deepseek-ai/DeepSeek-V4-Flash-0731", "createdAt": "2026-07-31T04:05:06.000Z"},
  {"modelId": "deepseek-ai/DeepSeek-V4-Flash-0731-GGUF", "createdAt": "2026-07-31T05:00:00.000Z"},
  {"modelId": "", "createdAt": "2026-07-30T00:00:00.000Z"}
]
```

- [ ] **Step 2: 失敗するテストを書く**

`tests/test_fetch.py`:
```python
# -*- coding: utf-8 -*-
from datetime import timezone
from pathlib import Path

from tracker.fetch import load_sources, parse_feed, parse_huggingface

FIXTURES = Path(__file__).parent / "fixtures"

RSS_SOURCE = {"id": "sample", "vendor": "Sample", "label": "Sample News", "type": "rss"}
GH_SOURCE = {"id": "gh", "vendor": "GitHub", "label": "Repo", "type": "github_releases"}
HF_SOURCE = {"id": "hf", "vendor": "DeepSeek", "label": "DeepSeek", "type": "huggingface"}


def _read(name):
    return (FIXTURES / name).read_bytes()


def test_parse_feed_reads_entries():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert [u.title for u in updates] == ["Introducing a new model", "Weekly notes"]


def test_parse_feed_skips_entry_without_link():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert all(u.url for u in updates)
    assert len(updates) == 2


def test_parse_feed_normalizes_to_utc():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert updates[0].published.tzinfo is not None
    assert updates[0].published.utcoffset() == timezone.utc.utcoffset(None)


def test_parse_feed_strips_html_from_summary():
    updates = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    assert updates[0].summary == "We are excited to share this."


def test_parse_feed_uids_are_source_scoped():
    a = parse_feed(RSS_SOURCE, _read("sample_rss.xml"))
    other = dict(RSS_SOURCE, id="different")
    b = parse_feed(other, _read("sample_rss.xml"))
    assert a[0].uid != b[0].uid


def test_parse_atom_releases():
    updates = parse_feed(GH_SOURCE, _read("sample_releases.atom"))
    assert [u.title for u in updates] == ["v1.2.0", "v1.1.3"]
    assert updates[0].url == "https://github.com/o/r/releases/tag/v1.2.0"


def test_parse_huggingface_builds_model_url():
    updates = parse_huggingface(HF_SOURCE, _read("sample_hf_models.json"))
    assert updates[0].title == "deepseek-ai/DeepSeek-V4-Flash-0731"
    assert updates[0].url == "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731"


def test_parse_huggingface_skips_entry_without_model_id():
    updates = parse_huggingface(HF_SOURCE, _read("sample_hf_models.json"))
    assert len(updates) == 2


def test_parse_feed_on_garbage_returns_empty_without_raising():
    assert parse_feed(RSS_SOURCE, b"not a feed at all") == []


def test_load_sources(tmp_path):
    path = tmp_path / "sources.yml"
    path.write_text(
        "sources:\n"
        "  - id: a\n"
        "    vendor: V\n"
        "    label: L\n"
        "    type: rss\n"
        "    url: https://example.com/feed\n",
        encoding="utf-8",
    )
    sources = load_sources(path)
    assert sources[0]["id"] == "a"
```

- [ ] **Step 3: テストが失敗することを確認する**

Run: `python -m pytest tests/test_fetch.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tracker.fetch'`

- [ ] **Step 4: 実装する**

`tracker/fetch.py`:
```python
# -*- coding: utf-8 -*-
"""sources.yml を読み、各ソースから Update を取得する。ネットワークに触る唯一の層。

bot ブロックを迂回するための User-Agent 偽装はしない。403 を返すソースは
別ルートを使うか追わない。
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import yaml

from .models import Update, make_uid

USER_AGENT = "ai-tsukaikata-tracker/1.0"
TIMEOUT = 20
MAX_ENTRIES = 30
HF_API = "https://huggingface.co/api/models"


def load_sources(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("sources", [])


def _http_get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def _to_utc(value: str) -> datetime | None:
    """RFC822 と ISO8601 の両方を受け付けて UTC に正規化する。"""
    if not value:
        return None
    parsed = None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_feed(source: dict, raw: bytes) -> list[Update]:
    """RSS / Atom のバイト列を Update のリストにする。"""
    feed = feedparser.parse(raw)
    updates = []
    for entry in feed.entries[:MAX_ENTRIES]:
        published = _to_utc(entry.get("published") or entry.get("updated") or "")
        link = entry.get("link", "")
        if published is None or not link:
            continue
        updates.append(Update(
            uid=make_uid(source["id"], entry.get("id") or link),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=(entry.get("title") or "").strip(),
            url=link,
            published=published,
            summary=entry.get("summary", "") or entry.get("description", ""),
        ))
    return updates


def parse_huggingface(source: dict, raw: bytes) -> list[Update]:
    """HuggingFace models API の JSON を Update のリストにする。"""
    models = json.loads(raw)
    updates = []
    for model in models[:MAX_ENTRIES]:
        model_id = model.get("modelId") or model.get("id") or ""
        created = _to_utc(model.get("createdAt", ""))
        if not model_id or created is None:
            continue
        updates.append(Update(
            uid=make_uid(source["id"], model_id),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=model_id,
            url=f"https://huggingface.co/{model_id}",
            published=created,
            summary=f"HuggingFace に新しいモデル {model_id} が公開されました。",
        ))
    return updates


def fetch_source(source: dict) -> tuple[list[Update], str | None]:
    """1ソースを取得する。(updates, error) を返し、例外は投げない。

    1ソースの失敗で全体を止めないため。失敗は呼び出し側が記録する。
    """
    try:
        if source["type"] == "huggingface":
            url = (
                f"{HF_API}?author={source['org']}"
                f"&sort=createdAt&direction=-1&limit={MAX_ENTRIES}"
            )
            return parse_huggingface(source, _http_get(url)), None
        return parse_feed(source, _http_get(source["url"])), None
    except Exception as error:  # noqa: BLE001 - 全ソースを止めないため握る
        return [], f"{type(error).__name__}: {str(error)[:80]}"
```

- [ ] **Step 5: テストが通ることを確認する**

Run: `python -m pytest tests/test_fetch.py -q`
Expected: PASS（10 passed）

- [ ] **Step 6: Commit**

```bash
git add tracker/fetch.py tests/test_fetch.py tests/fixtures/
git commit -m "feat: RSS/Atom/HuggingFace の取得と正規化を追加"
```

---

### Task 5: `store.py` — 既読管理・minorキュー・死活記録

**Files:**
- Create: `tracker/store.py`
- Test: `tests/test_store.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_store.py`:
```python
# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta, timezone

from tracker.models import Update
from tracker.store import (
    dead_sources,
    empty_state,
    load_state,
    mark_seen,
    prune,
    queue_minor,
    record_result,
    save_state,
    select_unseen,
    take_pending_minor,
)

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _update(uid, title="t"):
    return Update(
        uid=uid, source_id="s", vendor="V", label="L",
        title=title, url="https://example.com/x", published=NOW, summary="",
    )


def test_load_state_returns_empty_when_file_missing(tmp_path):
    state = load_state(tmp_path / "nope.json")
    assert state == empty_state()


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "sub" / "seen.json"
    state = empty_state()
    state["uids"]["abc"] = NOW.isoformat()
    save_state(path, state)
    assert load_state(path) == state


def test_save_state_creates_parent_directory(tmp_path):
    path = tmp_path / "deep" / "nested" / "seen.json"
    save_state(path, empty_state())
    assert path.exists()


def test_select_unseen_filters_known_uids():
    state = empty_state()
    state["uids"]["known"] = NOW.isoformat()
    result = select_unseen(state, [_update("known"), _update("fresh")])
    assert [u.uid for u in result] == ["fresh"]


def test_mark_seen_records_uids():
    state = empty_state()
    mark_seen(state, [_update("a"), _update("b")], NOW)
    assert set(state["uids"]) == {"a", "b"}


def test_mark_seen_does_not_overwrite_existing_timestamp():
    state = empty_state()
    earlier = (NOW - timedelta(days=5)).isoformat()
    state["uids"]["a"] = earlier
    mark_seen(state, [_update("a")], NOW)
    assert state["uids"]["a"] == earlier


def test_queue_minor_then_take_returns_and_clears():
    state = empty_state()
    queue_minor(state, [_update("a"), _update("b")])
    taken = take_pending_minor(state)
    assert [u.uid for u in taken] == ["a", "b"]
    assert state["pending_minor"] == []


def test_take_pending_minor_on_empty_returns_empty():
    assert take_pending_minor(empty_state()) == []


def test_record_result_success_clears_failures():
    state = empty_state()
    record_result(state, "s1", "Timeout", 0)
    record_result(state, "s1", None, 3)
    assert "s1" not in state["failures"]


def test_record_result_counts_zero_result_as_failure():
    state = empty_state()
    record_result(state, "s1", None, 0)
    assert state["failures"]["s1"]["count"] == 1
    assert state["failures"]["s1"]["last_error"] == "0件"


def test_dead_sources_requires_three_consecutive_failures():
    state = empty_state()
    for _ in range(2):
        record_result(state, "s1", "Timeout", 0)
    assert dead_sources(state) == []
    record_result(state, "s1", "Timeout", 0)
    assert dead_sources(state) == [("s1", 3, "Timeout")]


def test_prune_removes_entries_older_than_retention():
    state = empty_state()
    state["uids"]["old"] = (NOW - timedelta(days=91)).isoformat()
    state["uids"]["fresh"] = (NOW - timedelta(days=1)).isoformat()
    removed = prune(state, NOW)
    assert removed == 1
    assert set(state["uids"]) == {"fresh"}


def test_prune_removes_unparseable_timestamps():
    state = empty_state()
    state["uids"]["broken"] = "not-a-date"
    assert prune(state, NOW) == 1
    assert state["uids"] == {}


def test_state_file_is_human_readable_json(tmp_path):
    path = tmp_path / "seen.json"
    state = empty_state()
    state["uids"]["a"] = NOW.isoformat()
    save_state(path, state)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["uids"]["a"] == NOW.isoformat()
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_store.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tracker.store'`

- [ ] **Step 3: 実装する**

`tracker/store.py`:
```python
# -*- coding: utf-8 -*-
"""既読管理・minorキュー・ソース死活記録。ファイルに触る層。

判定は「seen.json に無いもの＝新着」なので、cron が遅延・スキップしても
次に走ったときに必ず拾う。取りこぼしは発生せず、遅れるだけ。
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import Update

RETENTION_DAYS = 90
FAILURE_THRESHOLD = 3


def empty_state() -> dict:
    return {"uids": {}, "pending_minor": [], "failures": {}}


def load_state(path: Path) -> dict:
    if not Path(path).exists():
        return empty_state()
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    for key, default in empty_state().items():
        state.setdefault(key, default)
    return state


def save_state(path: Path, state: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)


def select_unseen(state: dict, updates: list[Update]) -> list[Update]:
    return [u for u in updates if u.uid not in state["uids"]]


def mark_seen(state: dict, updates: list[Update], now: datetime) -> None:
    for update in updates:
        state["uids"].setdefault(update.uid, now.isoformat())


def queue_minor(state: dict, updates: list[Update]) -> None:
    """翌朝のダイジェストに載せるため minor を溜める。"""
    state["pending_minor"].extend(u.to_dict() for u in updates)


def take_pending_minor(state: dict) -> list[Update]:
    """溜まった minor を取り出してキューを空にする。"""
    items = [Update.from_dict(d) for d in state["pending_minor"]]
    state["pending_minor"] = []
    return items


def record_result(state: dict, source_id: str, error: str | None, count: int) -> None:
    """取得結果を記録する。成功かつ1件以上なら失敗カウントをリセットする。"""
    if error is None and count > 0:
        state["failures"].pop(source_id, None)
        return
    entry = state["failures"].get(source_id, {"count": 0, "last_error": ""})
    entry["count"] += 1
    entry["last_error"] = error or "0件"
    state["failures"][source_id] = entry


def dead_sources(state: dict) -> list[tuple[str, int, str]]:
    """FAILURE_THRESHOLD 回以上連続で失敗しているソースを返す。

    フィードURLは予告なく変わる。これが無いと「静かに情報が来なくなって
    いたことに数ヶ月気づかない」という最悪の壊れ方をする。
    """
    return [
        (source_id, entry["count"], entry["last_error"])
        for source_id, entry in sorted(state["failures"].items())
        if entry["count"] >= FAILURE_THRESHOLD
    ]


def prune(state: dict, now: datetime) -> int:
    """RETENTION_DAYS を超えた uid を削除し、削除件数を返す。"""
    cutoff = now - timedelta(days=RETENTION_DAYS)
    stale = []
    for uid, seen_at in state["uids"].items():
        try:
            seen_dt = datetime.fromisoformat(seen_at)
        except (TypeError, ValueError):
            stale.append(uid)
            continue
        if seen_dt.tzinfo is None:
            seen_dt = seen_dt.replace(tzinfo=timezone.utc)
        if seen_dt < cutoff:
            stale.append(uid)
    for uid in stale:
        del state["uids"][uid]
    return len(stale)
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_store.py -q`
Expected: PASS（14 passed）

- [ ] **Step 5: Commit**

```bash
git add tracker/store.py tests/test_store.py
git commit -m "feat: 既読管理・minorキュー・ソース死活記録を追加"
```

---

### Task 6: `notify.py` — メール本文と送信

**Files:**
- Create: `tracker/notify.py`
- Test: `tests/test_notify.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_notify.py`:
```python
# -*- coding: utf-8 -*-
from datetime import datetime, timezone

import pytest

from tracker.models import Update
from tracker.notify import build_body, build_subject, send_mail

NOW = datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc)


def _update(title="Introducing X", vendor="OpenAI", url="https://example.com/a"):
    return Update(
        uid="u", source_id="s", vendor=vendor, label="L",
        title=title, url=url, published=NOW, summary="ある要約",
    )


def test_body_contains_vendor_title_url_and_summary():
    plain, html_body = build_body([_update()], [])
    for text in (plain, html_body):
        assert "OpenAI" in text
        assert "Introducing X" in text
        assert "https://example.com/a" in text
        assert "ある要約" in text


def test_body_escapes_html_in_title():
    plain, html_body = build_body([_update(title="A <script>x</script> B")], [])
    assert "<script>" not in html_body
    assert "&lt;script&gt;" in html_body


def test_body_sorts_newest_first():
    older = Update(
        uid="a", source_id="s", vendor="V", label="L", title="Older",
        url="https://example.com/1",
        published=datetime(2026, 7, 1, tzinfo=timezone.utc), summary="",
    )
    newer = Update(
        uid="b", source_id="s", vendor="V", label="L", title="Newer",
        url="https://example.com/2",
        published=datetime(2026, 7, 20, tzinfo=timezone.utc), summary="",
    )
    plain, _ = build_body([older, newer], [])
    assert plain.index("Newer") < plain.index("Older")


def test_body_reports_dead_sources():
    plain, html_body = build_body([], [("openai-news", 3, "HTTPError: 404")])
    assert "openai-news" in plain
    assert "openai-news" in html_body
    assert "404" in plain


def test_subject_for_major_mentions_count():
    assert "2" in build_subject("major", 2)


def test_subject_differs_between_modes():
    assert build_subject("major", 1) != build_subject("digest", 1)


def test_send_mail_requires_credentials(monkeypatch):
    monkeypatch.delenv("GMAIL_USER", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)
    with pytest.raises(RuntimeError):
        send_mail("subject", "plain", "<p>html</p>")


def test_send_mail_uses_smtp_ssl(monkeypatch):
    sent = {}

    class FakeServer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def login(self, user, pw):
            sent["login"] = (user, pw)

        def sendmail(self, sender, to, message):
            sent["sendmail"] = (sender, to, message)

    monkeypatch.setenv("GMAIL_USER", "me@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "secret")
    monkeypatch.setenv("ALERT_RECIPIENT", "to@example.com")
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *a, **k: FakeServer())

    send_mail("件名", "本文", "<p>本文</p>")

    assert sent["login"] == ("me@example.com", "secret")
    assert sent["sendmail"][0] == "me@example.com"
    assert sent["sendmail"][1] == ["to@example.com"]


def test_send_mail_falls_back_to_sender_when_recipient_unset(monkeypatch):
    sent = {}

    class FakeServer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def login(self, *args):
            pass

        def sendmail(self, sender, to, message):
            sent["to"] = to

    monkeypatch.setenv("GMAIL_USER", "me@example.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "secret")
    monkeypatch.delenv("ALERT_RECIPIENT", raising=False)
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *a, **k: FakeServer())

    send_mail("件名", "本文", "<p>本文</p>")

    assert sent["to"] == ["me@example.com"]
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_notify.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tracker.notify'`

- [ ] **Step 3: 実装する**

`tracker/notify.py`:
```python
# -*- coding: utf-8 -*-
"""メール本文の組み立てと送信。SMTP に触る層。

送信方式は marketwatch-ai の email_weekly_zone.py と同じ Gmail SMTP。
"""
from __future__ import annotations

import html as html_mod
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from .models import Update

FOOTER = "※個人用の情報収集メモです。詳細は必ず出典元をご確認ください。"


def build_subject(mode: str, count: int) -> str:
    if mode == "major":
        return f"🚨 AI重要アップデート {count}件"
    return f"📮 AI更新ダイジェスト {count}件"


def build_body(
    updates: list[Update],
    dead: list[tuple[str, int, str]],
) -> tuple[str, str]:
    """(plain, html) を返す。新しい順に並べる。"""
    ordered = sorted(updates, key=lambda u: u.published, reverse=True)

    plain_lines = []
    html_items = []
    for update in ordered:
        stamp = update.published.strftime("%Y-%m-%d %H:%M UTC")
        plain_lines.append(
            f"[{update.vendor}] {update.title}\n"
            f"  {stamp}\n"
            f"  {update.url}\n"
            f"  {update.summary}\n"
        )
        html_items.append(
            "<li style='margin-bottom:14px'>"
            f"<b>[{html_mod.escape(update.vendor)}]</b> "
            f"<a href=\"{html_mod.escape(update.url, quote=True)}\">"
            f"{html_mod.escape(update.title)}</a>"
            f"<br><small style='color:#6e7781'>{stamp}</small>"
            f"<br>{html_mod.escape(update.summary)}"
            "</li>"
        )

    plain = "\n".join(plain_lines) if plain_lines else "（新着なし）\n"
    body_html = (
        f"<ul style='padding-left:18px'>{''.join(html_items)}</ul>"
        if html_items else "<p>（新着なし）</p>"
    )

    if dead:
        plain += "\n--- 取得できていないソース ---\n"
        dead_items = []
        for source_id, count, error in dead:
            plain += f"⚠️ {source_id}: {count}回連続で失敗 ({error})\n"
            dead_items.append(
                f"<li>⚠️ {html_mod.escape(source_id)}: {count}回連続で失敗 "
                f"({html_mod.escape(error)})</li>"
            )
        body_html += (
            "<h3 style='font-size:14px'>取得できていないソース</h3>"
            f"<ul style='padding-left:18px'>{''.join(dead_items)}</ul>"
        )

    plain += f"\n{FOOTER}\n"
    html_body = (
        "<html><body style=\"font-family:-apple-system,Segoe UI,sans-serif;"
        "font-size:14px;line-height:1.6;color:#1f2328;max-width:760px;"
        "margin:0 auto;padding:8px\">"
        f"{body_html}"
        f"<hr><p style=\"font-size:12px;color:#6e7781\">{FOOTER}</p>"
        "</body></html>"
    )
    return plain, html_body


def send_mail(subject: str, plain: str, html_body: str) -> None:
    user = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("ALERT_RECIPIENT") or user
    if not (user and password):
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD が未設定")

    message = MIMEMultipart("alternative")
    message["From"] = user
    message["To"] = recipient
    message["Subject"] = subject
    message["Date"] = formatdate(localtime=True)
    message.attach(MIMEText(plain, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(user, password)
        server.sendmail(user, [recipient], message.as_string())
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_notify.py -q`
Expected: PASS（9 passed）

- [ ] **Step 5: Commit**

```bash
git add tracker/notify.py tests/test_notify.py
git commit -m "feat: メール本文の組み立てと Gmail SMTP 送信を追加"
```

---

### Task 7: `run.py` — 配線

3つのモードを持つ。`bootstrap` は初回に大量メールが飛ぶ事故（OpenAI news だけで1105件）を防ぐために必須。

**Files:**
- Create: `tracker/run.py`
- Test: `tests/test_run.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_run.py`:
```python
# -*- coding: utf-8 -*-
from datetime import datetime, timezone

from tracker.models import Update
from tracker.run import run_bootstrap, run_check, run_digest
from tracker.store import empty_state, load_state

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

SOURCES = [
    {"id": "s1", "vendor": "V", "label": "L", "type": "rss", "url": "https://x/f"},
]


def _update(uid, title):
    return Update(
        uid=uid, source_id="s1", vendor="V", label="L",
        title=title, url=f"https://example.com/{uid}", published=NOW, summary="",
    )


def _fetcher(updates, error=None):
    def fetch(source):
        return list(updates), error
    return fetch


class Mailer:
    def __init__(self):
        self.sent = []

    def __call__(self, subject, plain, html_body):
        self.sent.append(subject)


def test_check_sends_major_immediately(tmp_path):
    mailer = Mailer()
    run_check(
        sources=SOURCES,
        state_path=tmp_path / "seen.json",
        fetcher=_fetcher([_update("a", "Introducing X")]),
        mailer=mailer,
        now=NOW,
    )
    assert len(mailer.sent) == 1
    assert "重要" in mailer.sent[0]


def test_check_queues_minor_without_sending(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Weekly notes")]),
        mailer=mailer, now=NOW,
    )
    assert mailer.sent == []
    assert len(load_state(path)["pending_minor"]) == 1


def test_check_does_not_notify_twice(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    fetcher = _fetcher([_update("a", "Introducing X")])
    run_check(sources=SOURCES, state_path=path, fetcher=fetcher, mailer=mailer, now=NOW)
    run_check(sources=SOURCES, state_path=path, fetcher=fetcher, mailer=mailer, now=NOW)
    assert len(mailer.sent) == 1


def test_check_sends_nothing_when_no_updates(tmp_path):
    mailer = Mailer()
    run_check(
        sources=SOURCES, state_path=tmp_path / "seen.json",
        fetcher=_fetcher([]), mailer=mailer, now=NOW,
    )
    assert mailer.sent == []


def test_bootstrap_records_without_sending(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_bootstrap(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Introducing X"), _update("b", "Weekly")]),
        mailer=mailer, now=NOW,
    )
    assert mailer.sent == []
    state = load_state(path)
    assert set(state["uids"]) == {"a", "b"}
    assert state["pending_minor"] == []


def test_digest_sends_queued_minor_and_clears(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([_update("a", "Weekly notes")]),
        mailer=Mailer(), now=NOW,
    )
    run_digest(state_path=path, mailer=mailer)
    assert len(mailer.sent) == 1
    assert load_state(path)["pending_minor"] == []


def test_digest_sends_nothing_when_queue_empty(tmp_path):
    path = tmp_path / "seen.json"
    mailer = Mailer()
    run_digest(state_path=path, mailer=mailer)
    assert mailer.sent == []


def test_digest_sends_when_only_dead_sources_exist(tmp_path):
    path = tmp_path / "seen.json"
    state = empty_state()
    state["failures"]["s1"] = {"count": 3, "last_error": "HTTPError: 404"}
    from tracker.store import save_state
    save_state(path, state)

    mailer = Mailer()
    run_digest(state_path=path, mailer=mailer)
    assert len(mailer.sent) == 1


def test_check_records_fetch_failure(tmp_path):
    path = tmp_path / "seen.json"
    run_check(
        sources=SOURCES, state_path=path,
        fetcher=_fetcher([], error="HTTPError: 404"),
        mailer=Mailer(), now=NOW,
    )
    assert load_state(path)["failures"]["s1"]["count"] == 1
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_run.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tracker.run'`

- [ ] **Step 3: 実装する**

`tracker/run.py`:
```python
# -*- coding: utf-8 -*-
"""トラッカーのエントリポイント。

fetcher と mailer は引数で差し替えられるようにしてある。テストが
ネットワークにも SMTP にも出ないようにするため。
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import fetch as fetch_module
from . import notify, store
from .classify import classify

DEFAULT_SOURCES = Path(__file__).parent / "sources.yml"
DEFAULT_STATE = Path("data/tracker/seen.json")


def _default_mailer(subject: str, plain: str, html_body: str) -> None:
    notify.send_mail(subject, plain, html_body)


def _collect(sources, state, fetcher):
    """全ソースを取得し、重要度を付けた Update のリストを返す。"""
    collected = []
    for source in sources:
        updates, error = fetcher(source)
        store.record_result(state, source["id"], error, len(updates))
        collected.extend(classify(u, source["type"]) for u in updates)
    return collected


def run_check(*, sources, state_path, fetcher, mailer, now) -> int:
    """毎時チェック。major は即送信、minor はダイジェスト用に溜める。"""
    state = store.load_state(state_path)
    collected = _collect(sources, state, fetcher)
    fresh = store.select_unseen(state, collected)

    major = [u for u in fresh if u.importance == "major"]
    minor = [u for u in fresh if u.importance == "minor"]

    store.mark_seen(state, fresh, now)
    store.queue_minor(state, minor)
    store.prune(state, now)
    store.save_state(state_path, state)

    if major:
        plain, html_body = notify.build_body(major, [])
        mailer(notify.build_subject("major", len(major)), plain, html_body)

    print(f"新着 {len(fresh)}件（major {len(major)} / minor {len(minor)}）")
    return len(fresh)


def run_digest(*, state_path, mailer) -> int:
    """毎朝のダイジェスト。溜まった minor と死んだソースを1通にまとめる。"""
    state = store.load_state(state_path)
    pending = store.take_pending_minor(state)
    dead = store.dead_sources(state)
    store.save_state(state_path, state)

    if not pending and not dead:
        print("ダイジェスト対象なし。送信しません")
        return 0

    plain, html_body = notify.build_body(pending, dead)
    mailer(notify.build_subject("digest", len(pending)), plain, html_body)
    print(f"ダイジェスト送信 {len(pending)}件（死活警告 {len(dead)}件）")
    return len(pending)


def run_bootstrap(*, sources, state_path, fetcher, mailer, now) -> int:
    """初回セットアップ。全件を既読にするだけで、1通も送らない。

    これをせずに run_check を初回実行すると、OpenAI news だけで1105件の
    通知が飛ぶ。
    """
    state = store.load_state(state_path)
    collected = _collect(sources, state, fetcher)
    store.mark_seen(state, collected, now)
    state["pending_minor"] = []
    store.save_state(state_path, state)
    print(f"初期化しました。{len(collected)}件を既読として記録（通知なし）")
    return len(collected)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI更新情報トラッカー")
    parser.add_argument("--mode", choices=["check", "digest", "bootstrap"], required=True)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)

    if args.mode == "digest":
        run_digest(state_path=args.state, mailer=_default_mailer)
        return 0

    sources = fetch_module.load_sources(args.sources)
    runner = run_check if args.mode == "check" else run_bootstrap
    runner(
        sources=sources,
        state_path=args.state,
        fetcher=fetch_module.fetch_source,
        mailer=_default_mailer,
        now=now,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_run.py -q`
Expected: PASS（9 passed）

- [ ] **Step 5: 全テストを通す**

Run: `python -m pytest -q`
Expected: PASS（合計 80 passed）

- [ ] **Step 6: Commit**

```bash
git add tracker/run.py tests/test_run.py
git commit -m "feat: check/digest/bootstrap の3モードを配線"
```

---

### Task 8: `sources.yml` — 実測済みソースの投入とスモークテスト

設計書 §3 の実測結果（2026-08-01）に基づく。**到達性を確認できたものだけを入れる。**

**Files:**
- Create: `tracker/sources.yml`

- [ ] **Step 1: ソース定義を書く**

`tracker/sources.yml`:
```yaml
# 追跡対象。到達性を実測で確認したものだけを入れる（設計書 §3 参照）。
# 追加はこのファイルに数行足すだけでよく、コードの変更は不要。
sources:
  # --- Anthropic ---
  # 公式news はRSS未提供（/news/rss.xml・/rss.xml・/engineering/rss.xml すべて404）。
  # releases 2本で実質的にカバーする。
  - id: claude-code
    vendor: Anthropic
    label: Claude Code
    type: github_releases
    url: https://github.com/anthropics/claude-code/releases.atom

  - id: anthropic-sdk
    vendor: Anthropic
    label: Anthropic SDK (Python)
    type: github_releases
    url: https://github.com/anthropics/anthropic-sdk-python/releases.atom

  # --- OpenAI ---
  - id: openai-news
    vendor: OpenAI
    label: OpenAI News
    type: rss
    url: https://openai.com/news/rss.xml

  # --- Google ---
  - id: google-ai-blog
    vendor: Google
    label: Google AI Blog
    type: rss
    url: https://blog.google/technology/ai/rss/

  - id: deepmind-blog
    vendor: Google DeepMind
    label: DeepMind Blog
    type: rss
    url: https://deepmind.google/blog/rss.xml

  # --- xAI ---
  # x.ai/news は403でbotブロック。迂回はせずHuggingFace経由で追う。
  - id: hf-xai
    vendor: xAI
    label: xAI 新モデル
    type: huggingface
    org: xai-org

  # --- 中国系 ---
  - id: qwen-blog
    vendor: Alibaba Qwen
    label: Qwen Blog
    type: rss
    url: https://qwenlm.github.io/blog/index.xml

  - id: hf-qwen
    vendor: Alibaba Qwen
    label: Qwen 新モデル
    type: huggingface
    org: Qwen

  - id: hf-deepseek
    vendor: DeepSeek
    label: DeepSeek 新モデル
    type: huggingface
    org: deepseek-ai

  - id: hf-moonshot
    vendor: Moonshot AI
    label: Kimi 新モデル
    type: huggingface
    org: moonshotai

  - id: hf-zhipu
    vendor: Zhipu AI
    label: GLM 新モデル
    type: huggingface
    org: zai-org

  # --- 日本系 ---
  - id: sakana-blog
    vendor: Sakana AI
    label: Sakana AI Blog
    type: rss
    url: https://sakana.ai/feed.xml

  - id: pfn-blog
    vendor: Preferred Networks
    label: PFN 技術ブログ
    type: rss
    url: https://tech.preferred.jp/ja/blog/feed/

  - id: elyza-note
    vendor: ELYZA
    label: ELYZA note
    type: rss
    url: https://note.com/elyza/rss
```

- [ ] **Step 2: 全ソースの到達性を実測する**

このスクリプトを一時ファイル `smoke.py` として作り、実行する。

```python
# -*- coding: utf-8 -*-
"""sources.yml の全ソースを1回だけ叩いて到達性を確認する（使い捨て）。"""
from pathlib import Path

from tracker.fetch import fetch_source, load_sources

for source in load_sources(Path("tracker/sources.yml")):
    updates, error = fetch_source(source)
    status = "OK  " if error is None and updates else "FAIL"
    detail = error or f"{len(updates)}件"
    print(f"{status} {source['id']:<18} {detail}")
    if updates:
        print(f"      最新: {updates[0].title[:60]}")
```

Run: `python smoke.py`
Expected: 全ソースが `OK` で1件以上を返す。`FAIL` があればそのソースのURLを設計書 §3 の実測結果と照合し、修正するか `sources.yml` から外す。

> **HuggingFace の org 名は検証済み（2026-08-01）:** `xai-org` / `moonshotai` / `zai-org` / `Qwen` / `deepseek-ai` の5つはいずれも実際にモデルを返すことを確認した。大文字の `MoonshotAI` と `THUDM` は0件を返すので使わないこと。

- [ ] **Step 3: スモークスクリプトを消す**

Run: `rm smoke.py`
Expected: 一時ファイルが消える（リポジトリに残さない）

- [ ] **Step 4: Commit**

```bash
git add tracker/sources.yml
git commit -m "feat: 実測で到達性を確認した14ソースを追加"
```

---

### Task 9: GitHub Actions ワークフロー

**Files:**
- Create: `.github/workflows/tracker.yml`
- Create: `.github/workflows/tracker-digest.yml`

- [ ] **Step 1: 毎時チェックのワークフローを作る**

`.github/workflows/tracker.yml`:
```yaml
name: AI Update Tracker

on:
  # 毎時17分。毎時0分は負荷が集中して遅延・スキップが起きやすいため避ける
  schedule:
    - cron: "17 * * * *"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: tracker
  cancel-in-progress: false

jobs:
  check:
    runs-on: ubuntu-latest
    env:
      GMAIL_USER: ${{ secrets.GMAIL_USER }}
      GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
      ALERT_RECIPIENT: ${{ secrets.ALERT_RECIPIENT }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: 依存をインストール
        run: pip install -r requirements.txt

      - name: 新着をチェック
        run: python -m tracker.run --mode check

      - name: 既読状態をコミット
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/tracker/seen.json
          git diff --staged --quiet || git commit -m "chore: トラッカーの既読状態を更新"
          git push
```

- [ ] **Step 2: ダイジェストのワークフローを作る**

`.github/workflows/tracker-digest.yml`:
```yaml
name: AI Update Digest

on:
  # JST 7:22（UTC 22:22）。毎時0分を避ける
  schedule:
    - cron: "22 22 * * *"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: tracker
  cancel-in-progress: false

jobs:
  digest:
    runs-on: ubuntu-latest
    env:
      GMAIL_USER: ${{ secrets.GMAIL_USER }}
      GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
      ALERT_RECIPIENT: ${{ secrets.ALERT_RECIPIENT }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: 依存をインストール
        run: pip install -r requirements.txt

      - name: ダイジェストを送信
        run: python -m tracker.run --mode digest

      - name: 既読状態をコミット
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/tracker/seen.json
          git diff --staged --quiet || git commit -m "chore: ダイジェスト送信後の状態を更新"
          git push
```

- [ ] **Step 3: YAMLが妥当か確認する**

Run: `python -c "import yaml,pathlib; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in pathlib.Path('.github/workflows').glob('*.yml')]; print('YAML OK')"`
Expected: `YAML OK`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/tracker.yml .github/workflows/tracker-digest.yml
git commit -m "ci: 毎時チェックと毎朝ダイジェストのワークフローを追加"
```

---

### Task 10: 初期化と稼働開始

ここは人間の作業が混ざる。**Secrets の登録は運営者が行う**（Claude はトークンや認証情報を入力しない）。

**Files:**
- Create: `data/tracker/seen.json`（`--mode bootstrap` が生成する）

- [ ] **Step 1: GitHubに公開リポジトリを作り、pushする**

リポジトリ名: `ai-tsukaikata`（public）

```bash
git remote add origin https://github.com/invest-ai-info/ai-tsukaikata.git
git push -u origin main
```

- [ ] **Step 2: Secrets を3件登録する（運営者の作業）**

`Settings → Secrets and variables → Actions` で以下を登録する。値は marketwatch-ai と同じものを使う。

| 名前 | 内容 |
|---|---|
| `GMAIL_USER` | 送信元のGmailアドレス |
| `GMAIL_APP_PASSWORD` | Gmailのアプリパスワード |
| `ALERT_RECIPIENT` | 受信先アドレス |

- [ ] **Step 3: ローカルで初期化する（通知は飛ばない）**

まずローカルの環境変数に何も設定しない状態で実行する。bootstrap はメールを送らないため認証情報は不要。

Run: `python -m tracker.run --mode bootstrap`
Expected: `初期化しました。NNN件を既読として記録（通知なし）` と表示され、`data/tracker/seen.json` が生成される。**メールは1通も飛ばない。**

- [ ] **Step 4: seen.json をコミットしてpushする**

```bash
git add data/tracker/seen.json
git commit -m "chore: トラッカーの初期状態を記録（bootstrap）"
git push
```

- [ ] **Step 5: 手動実行で動作を確認する**

GitHub の Actions タブから `AI Update Tracker` を `Run workflow` で手動実行する。

Expected: ジョブが成功する。bootstrap 直後なので新着は0〜数件。major があればメールが届く。

- [ ] **Step 6: ダイジェストも手動実行で確認する**

`AI Update Digest` を `Run workflow` で手動実行する。

Expected: ジョブが成功する。キューが空なら `ダイジェスト対象なし。送信しません` と表示され、メールは飛ばない。

- [ ] **Step 7: 1週間運用してノイズを見る**

以下を確認し、必要なら `sources.yml` と `classify.py` の判定語を調整する。

- major の頻度が1日あたり数件を大きく超えていないか
- 逆に見たかった発表が minor に落ちていないか
- ダイジェストの末尾に死活警告が出ているソースはないか

---

## 完了条件

- [ ] `python -m pytest -q` が全て通る
- [ ] `python -m tracker.run --mode bootstrap` でメールを1通も送らずに `seen.json` が作られる
- [ ] GitHub Actions の両ワークフローが手動実行で成功する
- [ ] `sources.yml` の全ソースがスモークテストで1件以上を返す
