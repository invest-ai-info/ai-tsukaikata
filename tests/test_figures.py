# -*- coding: utf-8 -*-
"""図の検査。座標を手で書くので、目視では見落とす崩れをここで止める。"""
import pathlib

import pytest

from src.figures import check_svg, text_width

IMAGES = pathlib.Path(__file__).resolve().parent.parent / "static" / "images"

STYLE = """<style>
  .box { fill: #fff; stroke: #d5dae0; stroke-width: 1.5; }
  .plate { fill: #f2f4f6; }
  .t { fill: #1f2328; font-size: 13px; }
  .mono { font-size: 12px; font-family: Consolas, monospace; }
</style>"""


def svg(body, w=400, h=200):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">{STYLE}{body}</svg>'
    )


def test_clean_figure_passes():
    body = '<rect class="box" x="10" y="10" width="380" height="60"/><text class="t" x="20" y="45">短い</text>'
    assert check_svg("a.svg", svg(body)) == []


def test_text_overflowing_its_box_is_detected():
    body = (
        '<rect class="box" x="10" y="10" width="80" height="40"/>'
        '<text class="t" x="20" y="35">この文字は枠より明らかに長いので溢れます</text>'
    )
    errors = check_svg("a.svg", svg(body))
    assert any("右にはみ出し" in e for e in errors)


def test_line_crossing_text_is_detected():
    """枠線が文字を貫くやつ。実際に公開直前まで見逃していた崩れ方。"""
    body = (
        '<rect class="box" x="10" y="30" width="380" height="40"/>'
        '<text class="t" x="20" y="34">線の上に乗っている</text>'
    )
    errors = check_svg("a.svg", svg(body))
    assert any("横線が貫い" in e for e in errors)


def test_fill_only_plate_is_not_treated_as_a_box():
    """塗りだけの当て板は境界が描かれないので、囲いとみなさない。"""
    body = (
        '<rect class="plate" x="10" y="30" width="380" height="10"/>'
        '<text class="t" x="20" y="34">当て板の上の文字</text>'
    )
    assert check_svg("a.svg", svg(body)) == []


def test_text_outside_the_canvas_is_detected():
    body = '<text class="t" x="330" y="40">画面からはみ出す長さの文字列です</text>'
    errors = check_svg("a.svg", svg(body))
    assert any("図の右にはみ出し" in e for e in errors)


def test_broken_xml_is_reported():
    assert any("読めません" in e for e in check_svg("a.svg", "<svg><text>"))


@pytest.mark.parametrize("text,size,family,bold,low,high", [
    ("あいうえお", 13, "sans", False, 60, 75),          # 全角5文字 ≒ 65px
    ("health-check", 13, "sans", True, 70, 95),
    ("2026-08-02", 12, "mono", False, 65, 78),
])
def test_width_estimate_is_in_the_measured_range(text, size, family, bold, low, high):
    """ブラウザ実測（315要素）から較正した値。ずれたら気づけるように範囲で押さえる。"""
    assert low <= text_width(text, size, family, bold) <= high


def test_all_real_figures_are_clean():
    """本番に置いてある図が全部きれいなこと。ここが赤くなったら公開しない。"""
    errors = []
    for path in sorted(IMAGES.glob("*.svg")):
        errors += check_svg(path.name, path.read_text(encoding="utf-8"))
    assert errors == [], "\n".join(errors)
