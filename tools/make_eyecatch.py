# -*- coding: utf-8 -*-
"""記事のアイキャッチSVGを自動生成する。

手描きしない理由＝記事を足すたびに絵を描く手数を残すと、自動公開の
深掘り記事に絵が付かず、サイトの見た目が二層に割れるため。slug をシードに
配置を揺らすので、同じカテゴリでも1枚ずつ違う絵になる。同じ slug なら
必ず同じ絵（決定的）。

部品は「机の上の道具」の世界観（設計書②）。レシピ＝ノート・鉛筆系、
ツール＝歯車・ルーペ・小ロボット。植物と太陽は余白の飾り。

⚠️ SVG内で使う class は必ず下の STYLE に定義すること。定義漏れは黒塗りに
なる（2026-08-05 実害）。tests/test_make_eyecatch.py が機械で照合している。

使い方: python -m tools.make_eyecatch
出力: static/images/eyecatch/<slug>.svg（毎回すべて作り直す・冪等）
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
OUTPUT_DIR = ROOT / "static" / "images" / "eyecatch"

# アイキャッチを付けるカテゴリ（pages は固定ページなので付けない）
CATEGORIES = ("recipes", "tools")

WIDTH, HEIGHT = 720, 180

# 「あたたかい紙」パレット（static/style.css と同じ世界観）
CORAL = "#D85A30"
AMBER = "#FAC775"
AMBER_DEEP = "#EF9F27"
GREEN = "#97C459"
GREEN_DEEP = "#639922"
PINK = "#ED93B1"
PINK_PALE = "#F5C4B3"

STYLE = """<style>
.ec-bg{fill:#F5E6D3}
.ec-paper{fill:#FFFDF8}
.ec-ln{stroke:#4A3F35}
.ec-rule{stroke:#D9CBB8}
@media (prefers-color-scheme: dark){
.ec-bg{fill:#33251B}
.ec-paper{fill:#241D15}
.ec-ln{stroke:#EFE7DA}
.ec-rule{stroke:#5C5044}
}
</style>"""


def seed_from(slug: str) -> int:
    """slug から決定的なシードを作る。ビルド環境が変わっても揺れない。"""
    return int(hashlib.sha1(slug.encode("utf-8")).hexdigest(), 16)


def pick(seed: int, salt: int, options: int) -> int:
    return (seed >> (salt * 5)) % options


# --- 部品。すべて (x, y) を左上または中心にした断片を返す ---

def notebook(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect width="120" height="85" rx="8" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<line x1="16" y1="24" x2="102" y2="24" class="ec-rule" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="16" y1="42" x2="92" y2="42" class="ec-rule" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="16" y1="60" x2="100" y2="60" stroke="{CORAL}" stroke-width="3" stroke-linecap="round"/>'
        f"</g>"
    )


def pencil(x: int, y: int, angle: int) -> str:
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<rect width="18" height="72" rx="3" fill="{AMBER}" class="ec-ln" stroke-width="3"/>'
        f'<path d="M2 74 L9 92 L16 74 Z" fill="{CORAL}" class="ec-ln" stroke-width="2.5" stroke-linejoin="round"/>'
        f"</g>"
    )


def sticky(x: int, y: int, angle: int) -> str:
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<rect width="46" height="46" rx="4" fill="{PINK_PALE}" class="ec-ln" stroke-width="2.5"/>'
        f'<line x1="10" y1="20" x2="36" y2="20" class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f'<line x1="10" y1="32" x2="30" y2="32" class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f"</g>"
    )


def coffee(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<circle cx="0" cy="0" r="17" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<path d="M-7 -3 Q0 -10 7 -3" fill="none" stroke="{GREEN_DEEP}" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M-4 -26 Q-1 -32 4 -30 M2 -22 Q5 -28 10 -26" fill="none" class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f"</g>"
    )


def gear(x: int, y: int) -> str:
    teeth = "".join(
        f'<rect x="-4" y="-34" width="8" height="12" rx="2" fill="{AMBER_DEEP}" transform="rotate({a})"/>'
        for a in range(0, 360, 60)
    )
    return (
        f'<g transform="translate({x},{y})">{teeth}'
        f'<circle cx="0" cy="0" r="24" fill="{AMBER}" class="ec-ln" stroke-width="3"/>'
        f'<circle cx="0" cy="0" r="9" class="ec-bg ec-ln" stroke-width="3"/>'
        f"</g>"
    )


def magnifier(x: int, y: int, angle: int) -> str:
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<circle cx="0" cy="0" r="22" class="ec-paper ec-ln" stroke-width="3.5"/>'
        f'<line x1="16" y1="16" x2="34" y2="34" class="ec-ln" stroke-width="6" stroke-linecap="round"/>'
        f"</g>"
    )


def robot(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<line x1="42" y1="0" x2="42" y2="-12" class="ec-ln" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="42" cy="-16" r="5" fill="{CORAL}"/>'
        f'<rect width="84" height="60" rx="15" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<circle cx="28" cy="28" r="5" fill="#4A3F35" class="ec-ln" stroke-width="1"/>'
        f'<circle cx="56" cy="28" r="5" fill="#4A3F35" class="ec-ln" stroke-width="1"/>'
        f'<path d="M30 42 Q42 50 54 42" fill="none" stroke="{CORAL}" stroke-width="3" stroke-linecap="round"/>'
        f'<rect x="16" y="62" width="52" height="20" rx="8" fill="{PINK_PALE}" class="ec-ln" stroke-width="3"/>'
        f"</g>"
    )


def sprout(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M0 0 Q2 -18 12 -24" fill="none" stroke="{GREEN_DEEP}" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M12 -24 Q4 -28 3 -38 Q14 -36 15 -26 Z" fill="{GREEN}" stroke="{GREEN_DEEP}" stroke-width="2"/>'
        f'<path d="M12 -24 Q20 -30 30 -28 Q24 -18 14 -21 Z" fill="{GREEN}" stroke="{GREEN_DEEP}" stroke-width="2"/>'
        f"</g>"
    )


def sun(x: int, y: int) -> str:
    rays = "".join(
        f'<line x1="0" y1="-24" x2="0" y2="-30" stroke="{AMBER_DEEP}" stroke-width="3" '
        f'stroke-linecap="round" transform="rotate({a})"/>'
        for a in range(0, 360, 45)
    )
    return (
        f'<g transform="translate({x},{y})">'
        f'<circle cx="0" cy="0" r="17" fill="{AMBER}"/>{rays}'
        f"</g>"
    )


def ground(seed: int) -> str:
    lift = pick(seed, 7, 3) * 4
    return (
        f'<path d="M40 {150 - lift} Q200 {128 - lift} 380 {142 - lift} T690 {134 - lift}" '
        f'fill="none" stroke="{CORAL}" stroke-width="3.5" stroke-linecap="round" opacity="0.85"/>'
    )


# --- 構図。カテゴリごとに数パターン、seed で選ぶ ---

def _recipes_cluster(seed: int) -> str:
    variant = pick(seed, 1, 3)
    if variant == 0:
        return notebook(300, 42) + pencil(444, 48, 18) + sticky(236, 36, -8)
    if variant == 1:
        return notebook(316, 52) + coffee(262, 108) + pencil(452, 60, -14)
    return notebook(284, 40) + sticky(424, 46, 10) + coffee(486, 104)


def _tools_cluster(seed: int) -> str:
    variant = pick(seed, 1, 3)
    if variant == 0:
        return robot(318, 48) + gear(254, 74)
    if variant == 1:
        return gear(330, 78) + magnifier(424, 70, -12) + sticky(240, 40, -8)
    return robot(300, 46) + magnifier(232, 80, 12) + sticky(430, 42, 8)


def build_svg(slug: str, category: str) -> str:
    """アイキャッチ1枚ぶんのSVG文字列。同じ入力なら必ず同じ出力。"""
    seed = seed_from(slug + "/" + category)
    cluster = _recipes_cluster(seed) if category == "recipes" else _tools_cluster(seed)
    sun_x = 84 if pick(seed, 3, 2) == 0 else 636
    sprout_x = 120 + pick(seed, 5, 5) * 110
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-hidden="true">'
        f"{STYLE}"
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" class="ec-bg"/>'
        f"{sun(sun_x, 44)}{ground(seed)}{cluster}{sprout(sprout_x, 148)}"
        f"</svg>"
    )


def main(content_dir: Path = CONTENT_DIR, output_dir: Path = OUTPUT_DIR) -> int:
    """content/ の記事ぶんを output_dir に書き出す。書いた枚数を返す。

    `_` 始まり（下書き・キュー）は記事ではないので飛ばす。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for category in CATEGORIES:
        directory = Path(content_dir) / category
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name.startswith("_"):
                continue
            slug = path.stem
            svg = build_svg(slug, category)
            (output_dir / f"{slug}.svg").write_text(svg, encoding="utf-8", newline="\n")
            written += 1
    return written


if __name__ == "__main__":
    count = main()
    print(f"アイキャッチ {count} 枚を {OUTPUT_DIR} に生成しました")
    sys.exit(0)
