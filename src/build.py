# -*- coding: utf-8 -*-
"""全体をつなぐ。ファイルを書くのはこのモジュールだけ。

検証エラーが1件でもあれば build/ に一切触らず exit 1 する。
「壊れた記事が1本あるせいで、直った記事だけ古いまま公開され続ける」
という中途半端な状態を作らないため。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from . import config, feeds, news, render
from .content import load_articles
from .figures import check_svg
from .validate import validate

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"
BUILD_DIR = ROOT / "build"


def static_paths(static_dir: Path) -> set[str]:
    """static/ にあるファイルを公開URLの形（/static/...）で列挙する。

    ディスクを見るのはここだけ。validate.py はこの集合と照合するだけにして
    純粋なまま保つ。
    """
    static_dir = Path(static_dir)
    if not static_dir.exists():
        return set()
    return {
        "/static/" + path.relative_to(static_dir).as_posix()
        for path in static_dir.rglob("*")
        if path.is_file()
    }


def figure_errors(static_dir: Path) -> list[str]:
    """図（SVG）の文字が枠からはみ出していないか・線に重なっていないか。"""
    images = Path(static_dir) / "images"
    if not images.exists():
        return []
    errors: list[str] = []
    for path in sorted(images.glob("*.svg")):
        errors += check_svg(path.name, path.read_text(encoding="utf-8"))
    return errors


NEWS_PATH = ROOT / "data" / "tracker" / "news.json"
SOURCES_PATH = ROOT / "tracker" / "sources.yml"


def collect(
    content_dir: Path,
    static_dir: Path = STATIC_DIR,
    news_path: Path = NEWS_PATH,
    sources_path: Path = SOURCES_PATH,
) -> tuple[dict[str, str], list[str]]:
    """書き出す内容を全部メモリ上で作る。(files, errors) を返す。"""
    articles, errors = load_articles(content_dir)
    available = static_paths(static_dir)
    errors = errors + validate(articles, available)
    errors = errors + figure_errors(static_dir)

    news_data = None
    try:
        source_types = news.load_source_types(sources_path)
        items = news.load_news(news_path)
        news_data = {
            "top": news.split_recent(items, source_types),
            "archive": {"months": news.group_by_month(items)},
        }
    except news.NewsError as error:
        errors = errors + [str(error)]

    if errors:
        return {}, errors

    # アイキャッチが実在する記事だけ画像付きで組む（tools/make_eyecatch.py が生成）
    eyecatches = {
        path.rsplit("/", 1)[-1][:-4]
        for path in available
        if path.startswith("/static/images/eyecatch/") and path.endswith(".svg")
    }
    files = render.render_site(articles, news=news_data, eyecatches=eyecatches)

    section_paths = ("/", "/news/") + tuple(
        f"/{name}/" for name in config.LISTED_CATEGORIES
        if any(a.category == name for a in articles)
    ) + tuple(
        f"/scenes/{name}/" for name in config.SCENES
        if any(a.scene == name for a in articles)
    )
    files["feed.xml"] = feeds.build_rss(articles)
    files["sitemap.xml"] = feeds.build_sitemap(articles, section_paths)
    files["robots.txt"] = feeds.build_robots()

    # 生成HTMLをコミットしない方式では、CNAME を artifact に含めないと
    # デプロイのたびに独自ドメインの設定が外れる
    files["CNAME"] = config.CUSTOM_DOMAIN + "\n"

    return files, []


def write(files: dict[str, str], build_dir: Path, static_dir: Path) -> None:
    """build/ を作り直して書き出す。消えた記事の残骸を残さないため毎回消す。"""
    build_dir = Path(build_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    for relative, text in files.items():
        path = build_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    if Path(static_dir).exists():
        shutil.copytree(static_dir, build_dir / "static")


def main(argv=None) -> int:
    files, errors = collect(CONTENT_DIR, STATIC_DIR)
    if errors:
        print(f"ビルド中止: {len(errors)}件の問題があります", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    write(files, BUILD_DIR, STATIC_DIR)
    print(f"ビルド完了: {len(files)}ファイルを {BUILD_DIR} に出力しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
