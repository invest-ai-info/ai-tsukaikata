# -*- coding: utf-8 -*-
"""AI動画まとめの1回分＝集める → 要約する → 片づける → 保存する。

使い方: python -m videos.run [--max-summaries N] [--no-summarize]

- GEMINI_API_KEY が無ければ要約だけ飛ばす（集めた動画は pending で貯まる）。exit 0
- 枠切れ（429）が出たら、その回の要約はそこで止める（動画の失敗回数に数えない）
- 要約に失敗した動画は MAX_ATTEMPTS 回まで次の回に持ち越す
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import feed, gemini, store

ROOT = Path(__file__).resolve().parent.parent
CHANNELS_PATH = Path(__file__).resolve().parent / "channels.yml"
DATA_PATH = ROOT / "data" / "videos" / "videos.json"
MAX_SUMMARIES = 4   # 1回あたり。6時間おき×4本×最初の30分＝無料枠（1日8時間）の内側


def load_channels(path: Path = CHANNELS_PATH) -> list[dict]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    channels = data.get("channels") or []
    for channel in channels:
        for key in ("key", "name", "channel_id", "category"):
            if not channel.get(key):
                raise ValueError(f"channels.yml: {channel} に {key} がありません")
        if channel["category"] not in gemini.CATEGORIES:
            raise ValueError(f"channels.yml: {channel['key']} の category が想定外です")
    keys = [c["key"] for c in channels]
    if len(keys) != len(set(keys)):
        raise ValueError("channels.yml: key が重複しています")
    return channels


def collect(data: dict, channels: list[dict], now: datetime,
            fetch=None, log=print) -> int:
    """全チャンネルの RSS を見て、新しい動画を足す。足した本数を返す。"""
    fetch = fetch or feed.fetch_feed
    added = 0
    for channel in channels:
        try:
            entries = feed.parse_feed(fetch(channel["channel_id"]))
        except feed.FeedError as error:
            store.record_channel(data, channel["key"], ok=False, now=now)
            log(f"  ✗ {channel['name']}: {error}")
            continue
        store.record_channel(data, channel["key"], ok=True, now=now)
        count = store.merge(data, channel, entries, now)
        added += count
        log(f"  ✓ {channel['name']}: {len(entries)}本を確認・新しく{count}本")
    return added


def summarize(data: dict, call, now: datetime, limit: int = MAX_SUMMARIES,
              log=print) -> int:
    """要約待ちを新しい順に limit 本まで要約する。要約できた本数を返す。"""
    done = 0
    for video in store.pending(data)[:limit]:
        try:
            text, model = call(video)
            result = gemini.parse_reply(text)
        except gemini.QuotaError as error:
            log(f"  ⏸ 枠切れのため、この回の要約を止めます（{error}）")
            break
        except Exception as error:  # noqa: BLE001 - 次の回にもう一度試す
            store.mark_failed(video, f"{type(error).__name__}: {error}")
            log(f"  ✗ {video['title'][:40]}: {type(error).__name__}"
                f"（{video['attempts']}回目）")
            continue
        store.mark_done(video, result, model, now)
        state = "AIと関係なし" if video["status"] == "skipped" else video["category"]
        log(f"  ✓ {video['title'][:40]}: {state}（{model}）")
        done += 1
    return done


def main(argv=None, now: datetime | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI動画まとめを更新する")
    parser.add_argument("--max-summaries", type=int, default=MAX_SUMMARIES)
    parser.add_argument("--no-summarize", action="store_true")
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    args = parser.parse_args(argv)
    now = now or datetime.now(timezone.utc)

    channels = load_channels()
    data = store.load(args.data)

    print(f"チャンネル {len(channels)}本を確認します")
    added = collect(data, channels, now)

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    summarized = 0
    if args.no_summarize:
        print("要約は飛ばします（--no-summarize）")
    elif not api_key:
        print("GEMINI_API_KEY が無いので要約は飛ばします（集めた動画は次の回に要約します）")
    else:
        print(f"要約します（最大{args.max_summaries}本）")
        summarized = summarize(data, gemini.client(api_key), now, args.max_summaries)

    removed = store.prune(data, now, {c["key"] for c in channels})
    store.save(args.data, data)

    counts = {}
    for video in data["videos"]:
        counts[video["status"]] = counts.get(video["status"], 0) + 1
    print(f"新しく{added}本・要約{summarized}本・片づけ{removed}本 ／ 現在 {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
