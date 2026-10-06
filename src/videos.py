# -*- coding: utf-8 -*-
"""data/videos/videos.json を読んで、/videos/（AI動画まとめ）に渡す形へ整える。

ページは3段（2026-10-06・オーナー判断「長くて見づらい・過去の動画も見たい」）:
  /videos/                 入口。分類ごとに最新 TOP_PER_SECTION 本（題とサムネだけ）
  /videos/<分類>/           分類のページ。最新 PER_SECTION 本（要約つき）＋過去の月への入口
  /videos/<分類>/<年-月>/   月のページ。その月の動画を全部（要約つき）
入口・検索の行き先は分類のページ（入口の6本も検索に入る動画も、必ずそこに並んでいる）。

載せるのは要約が済んだ動画（status=done）だけ。ファイルが無い・載せる動画が
0本＝ページごと出さない（/ainews/ と同じ）。ファイルが壊れている・形が違う＝
VideoError でビルドを止める（半端なページを公開しない）。
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

JST = timezone(timedelta(hours=9))
PER_SECTION = 20        # 分類のページに並べる本数（＝サイト内検索に入る本数）
TOP_PER_SECTION = 6     # 入口に並べる本数

SECTIONS = (
    ("tech", "AI技術", "AIの仕組みや、ツールの使い方・設定・自動化の手順を解説している動画。"),
    ("earn", "AIで稼ぐ", "AIを使った副業・仕事の受注・販売などを扱う動画。"),
    ("news", "AI最新情報", "新しいモデルや新機能、各社の発表を扱う動画。"),
)

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
REQUIRED = ("video_id", "title", "url", "published", "channel_key",
            "channel_name", "category", "summary")


class VideoError(Exception):
    """videos.json / channels.yml を読めない・形が違う。"""


def load_notes(channels_path: Path) -> dict[str, str]:
    """チャンネル単位の注意書き {key: note}。ファイルが無ければ空。"""
    if not Path(channels_path).exists():
        return {}
    try:
        data = yaml.safe_load(Path(channels_path).read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        raise VideoError(f"{channels_path} が読めません（{error}）") from error
    return {c["key"]: c["note"] for c in data.get("channels") or [] if c.get("note")}


def _entry(video: dict, notes: dict[str, str]) -> dict:
    missing = [key for key in REQUIRED if not video.get(key)]
    if missing:
        raise VideoError(f"videos.json: {video.get('video_id')} に {missing} がありません")
    if not VIDEO_ID_RE.match(video["video_id"]):
        raise VideoError(f"videos.json: video_id の形が違います（{video['video_id']!r}）")
    # リンク先は YouTube の視聴ページに固定する（データにどんな URL が入っても使わない）
    video_id = video["video_id"]
    try:
        published = datetime.fromisoformat(video["published"]).astimezone(JST)
    except (TypeError, ValueError) as error:
        raise VideoError(f"videos.json: {video_id} の published が読めません") from error
    if not isinstance(video["summary"], list):
        raise VideoError(f"videos.json: {video_id} の summary が一覧ではありません")
    return {
        "video_id": video_id,
        "title": video["title"],
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg",
        "channel_name": video["channel_name"],
        "published": published,
        "date_label": f"{published.year}年{published.month}月{published.day}日",
        "summary": [str(line) for line in video["summary"]],
        "for_whom": video.get("for_whom") or "",
        "caution": video.get("caution") or "",
        "note": notes.get(video["channel_key"], ""),
        "category": video["category"],
    }


def _months(key: str, items: list[dict]) -> list[dict]:
    """新しい順に並んだ動画を、日本時間の月ごとに分ける（新しい月から）。"""
    months: list[dict] = []
    for entry in items:
        published = entry["published"]
        month_key = f"{published.year:04d}-{published.month:02d}"
        if not months or months[-1]["key"] != month_key:
            months.append({
                "key": month_key,
                "label": f"{published.year}年{published.month}月",
                "url": f"/videos/{key}/{month_key}/",
                "entries": [],
            })
        months[-1]["entries"].append(entry)
    for month in months:
        month["count"] = len(month["entries"])
    return months


def page_paths(videos: dict | None) -> tuple[str, ...]:
    """/videos/ 以下のページの URL（sitemap 用）。動画が0本の分類のページは作らない。"""
    if not videos:
        return ()
    paths = ["/videos/"]
    for section in videos["sections"]:
        if section["count"]:
            paths.append(section["url"])
            paths.extend(month["url"] for month in section["months"])
    return tuple(paths)


def load_videos(path: Path, channels_path: Path, per_section: int = PER_SECTION,
                top: int = TOP_PER_SECTION) -> dict | None:
    """/videos/ 用のデータ。載せる動画が無ければ None。

    分類ごとに top（入口）・latest（分類のページ）・months（月のページ）・count を持つ。
    """
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VideoError(f"{path} が壊れています（{error}）") from error
    if not isinstance(data, dict) or not isinstance(data.get("videos"), list):
        raise VideoError(f"{path} の形が違います（videos の一覧がありません）")

    notes = load_notes(channels_path)
    entries = [_entry(v, notes) for v in data["videos"] if v.get("status") == "done"]
    if not entries:
        return None
    entries.sort(key=lambda e: e["published"], reverse=True)

    sections = []
    for key, label, lead in SECTIONS:
        items = [e for e in entries if e["category"] == key]
        sections.append({"key": key, "label": label, "lead": lead,
                         "url": f"/videos/{key}/",
                         "top": items[:top], "latest": items[:per_section],
                         "months": _months(key, items), "count": len(items)})
    return {"sections": sections, "total": len(entries)}
