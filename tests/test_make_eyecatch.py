# -*- coding: utf-8 -*-
"""アイキャッチ自動生成のテスト。

作った理由＝記事を足すたびに絵を描く手数をゼロにするため（自動公開の
深掘り記事にも絵を付ける）。同じslugなら必ず同じ絵になること（決定的）と、
「CSSクラスを<style>に定義し忘れるとSVGが黒塗りになる」事故（2026-08-05に
実害）を機械で封じることを確かめる。
"""
import re

import pytest

from tools.make_eyecatch import build_svg, main


def test_same_slug_gives_same_svg():
    assert build_svg("sample-slug", "recipes") == build_svg("sample-slug", "recipes")


def test_different_slugs_give_different_svgs():
    assert build_svg("slug-a", "recipes") != build_svg("slug-b", "recipes")


def test_categories_differ():
    assert build_svg("same-slug", "recipes") != build_svg("same-slug", "tools")


def test_svg_has_size_attributes():
    svg = build_svg("sample-slug", "recipes")
    assert 'viewBox="0 0 720 180"' in svg
    assert 'width="720"' in svg
    assert 'height="180"' in svg


def test_svg_has_dark_mode():
    assert "prefers-color-scheme: dark" in build_svg("sample-slug", "tools")


def test_all_used_classes_are_defined_in_style():
    """使っている class が <style> に無いと黒塗りになる（実害あり）。"""
    for category in ("recipes", "tools"):
        svg = build_svg("class-check", category)
        style = re.search(r"<style>(.*?)</style>", svg, re.DOTALL).group(1)
        defined = set(re.findall(r"\.([a-z-]+)\s*\{", style))
        used = set()
        for value in re.findall(r'class="([^"]+)"', svg):
            used.update(value.split())
        assert used <= defined, f"未定義のclass: {used - defined}（{category}）"


def test_main_writes_one_svg_per_listed_article(tmp_path):
    content = tmp_path / "content" / "recipes"
    content.mkdir(parents=True)
    (content / "one.md").write_text("x", encoding="utf-8")
    (content / "_draft.md").write_text("x", encoding="utf-8")
    pages = tmp_path / "content" / "pages"
    pages.mkdir()
    (pages / "about.md").write_text("x", encoding="utf-8")
    out = tmp_path / "out"

    written = main(content_dir=tmp_path / "content", output_dir=out)

    assert written == 1
    assert (out / "one.svg").exists()
    assert not (out / "_draft.svg").exists()
    assert not (out / "about.svg").exists()


# --- 場面ごとに絵柄が変わる（2026-08-08 追加） ---

def test_scenes_give_different_pictures():
    """全部が同じ絵になっていた不具合の再発防止。どの場面も別の絵になる。

    ⚠️ 場面の数はここに書かない（足すたびに腐る）。SCENE_BUILDERS から数える。
    """
    from tools.make_eyecatch import SCENE_BUILDERS
    svgs = {s: build_svg("same-slug", "recipes", s) for s in SCENE_BUILDERS}
    assert len(set(svgs.values())) == len(SCENE_BUILDERS)


def test_every_scene_in_config_has_a_picture():
    """config.SCENES に足した場面が、絵柄の無いまま公開されないこと。

    🚨 SCENE_BUILDERS に無い場面は、build_svg の受け皿で**黙って「仕事」の絵**に
    なる。エラーは出ず、テストも通り、記事も普通に公開される——実際
    earn（副業）/ safety（詐欺を防ぐ）/ security の3つが 2026-08-13 の新設から
    そのまま公開されていて、**オーナーが画面を見て気づくまで誰も分からなかった**。
    このサイトが一番警戒している「静かな欠落」そのものなので、機械で照合する。
    """
    from src.config import SCENES
    from tools.make_eyecatch import SCENE_BUILDERS
    missing = [s for s in SCENES if s not in SCENE_BUILDERS]
    assert not missing, (
        f"絵柄の無い場面: {missing}。tools/make_eyecatch.py に "
        f"_scene_<名前> を足して SCENE_BUILDERS に登録すること"
    )


def test_main_reads_scene_from_frontmatter(tmp_path):
    content = tmp_path / "content" / "recipes"
    content.mkdir(parents=True)
    (content / "a.md").write_text(
        "---\ntitle: T\ncategory: recipes\nscene: life\n---\n本文", encoding="utf-8"
    )
    (content / "b.md").write_text(
        "---\ntitle: T\ncategory: recipes\nscene: automate\n---\n本文", encoding="utf-8"
    )
    out = tmp_path / "out"
    main(content_dir=tmp_path / "content", output_dir=out)
    # 場面が違えば中身も違う（同じテンプレの使い回しになっていない）
    assert (out / "a.svg").read_text(encoding="utf-8") != (out / "b.svg").read_text(encoding="utf-8")


def test_scene_of_reads_and_missing_is_none():
    from tools.make_eyecatch import scene_of
    assert scene_of("---\ncategory: recipes\nscene: work\n---\n") == "work"
    assert scene_of("---\ncategory: recipes\n---\n") is None


def test_main_without_scene_still_writes(tmp_path):
    """scene 無しでも絵は出す（絵が無い記事を作らない）。"""
    content = tmp_path / "content" / "recipes"
    content.mkdir(parents=True)
    (content / "a.md").write_text("---\ntitle: T\ncategory: recipes\n---\n本文", encoding="utf-8")
    out = tmp_path / "out"
    assert main(content_dir=tmp_path / "content", output_dir=out) == 1
    assert (out / "a.svg").exists()


def test_main_variants_differ_within_same_scene():
    """同じ場面でも slug で揺れる（全部同じ絵にならない）。"""
    same = {build_svg(f"slug-{i}", "recipes", "work") for i in range(6)}
    assert len(same) > 1


def test_focus_region_holds_the_main_motif():
    """カードのサムネは中央180pxだけを映すので、主役はそこに要る。

    ⚠️ 端に置くとカードで見えない（実際にノートだけが並んで見えた原因）。
    """
    import re
    from tools.make_eyecatch import FOCUS_LEFT, FOCUS_RIGHT, SCENE_BUILDERS
    for scene in SCENE_BUILDERS:
        svg = build_svg("focus-check", "recipes", scene)
        xs = [float(m) for m in re.findall(r"translate\((-?[\d.]+),", svg)]
        assert any(FOCUS_LEFT <= x <= FOCUS_RIGHT for x in xs), f"{scene}: 主役が中央に無い"
