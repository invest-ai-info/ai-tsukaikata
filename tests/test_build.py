# -*- coding: utf-8 -*-
from pathlib import Path

from src import build

RECIPE = """---
title: テスト記事
description: これはテストです。
category: recipes
published: 2026-08-01
time_required: 30分
cost: 無料
---

本文です。
"""


def _content_dir(tmp_path: Path, text: str = RECIPE) -> Path:
    content = tmp_path / "content" / "recipes"
    content.mkdir(parents=True)
    (content / "sample.md").write_text(text, encoding="utf-8")
    return tmp_path / "content"


def test_collect_returns_all_expected_files(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path))
    assert errors == []
    assert set(files) >= {
        "index.html",
        "recipes/index.html",
        "recipes/sample/index.html",
        "feed.xml",
        "sitemap.xml",
        "robots.txt",
        "CNAME",
    }


def test_collect_writes_cname_for_custom_domain(tmp_path):
    files, _ = build.collect(_content_dir(tmp_path))
    assert files["CNAME"].strip() == "ai-tsukaikata.com"


def test_collect_returns_errors_and_no_files_when_invalid(tmp_path):
    broken = RECIPE.replace("本文です。", r"作業場所は C:\Users\taro です。")
    files, errors = build.collect(_content_dir(tmp_path, broken))
    assert files == {}
    assert len(errors) == 1


def test_collect_reports_unreadable_article(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path, "frontmatterがない"))
    assert files == {}
    assert any("frontmatter" in error for error in errors)


def test_write_creates_directory_structure(tmp_path):
    build_dir = tmp_path / "build"
    build.write({"recipes/sample/index.html": "<p>x</p>"}, build_dir, tmp_path / "missing-static")
    assert (build_dir / "recipes" / "sample" / "index.html").read_text(encoding="utf-8") == "<p>x</p>"


def test_write_copies_static_directory(tmp_path):
    static = tmp_path / "static"
    static.mkdir()
    (static / "style.css").write_text("body{}", encoding="utf-8")
    build_dir = tmp_path / "build"
    build.write({"index.html": "<p>x</p>"}, build_dir, static)
    assert (build_dir / "static" / "style.css").read_text(encoding="utf-8") == "body{}"


def test_write_clears_previous_output(tmp_path):
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "stale.html").write_text("古い", encoding="utf-8")
    build.write({"index.html": "<p>x</p>"}, build_dir, tmp_path / "missing-static")
    assert not (build_dir / "stale.html").exists()


def test_main_writes_nothing_when_validation_fails(tmp_path, monkeypatch, capsys):
    broken = RECIPE.replace("本文です。", r"作業場所は C:\Users\taro です。")
    build_dir = tmp_path / "build"
    monkeypatch.setattr(build, "CONTENT_DIR", _content_dir(tmp_path, broken))
    monkeypatch.setattr(build, "BUILD_DIR", build_dir)

    assert build.main() == 1
    assert not build_dir.exists()
    assert "ビルド中止" in capsys.readouterr().err


def test_main_builds_successfully(tmp_path, monkeypatch):
    build_dir = tmp_path / "build"
    monkeypatch.setattr(build, "CONTENT_DIR", _content_dir(tmp_path))
    monkeypatch.setattr(build, "BUILD_DIR", build_dir)

    assert build.main() == 0
    assert (build_dir / "index.html").exists()
    assert (build_dir / "static" / "style.css").exists()
