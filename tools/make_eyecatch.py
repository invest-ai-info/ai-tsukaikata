# -*- coding: utf-8 -*-
"""記事のアイキャッチSVGを自動生成する。

手描きしない理由＝記事を足すたびに絵を描く手数を残すと、自動公開の
レシピや深掘り記事に絵が付かず、サイトの見た目が二層に割れるため。

⚠️ **絵柄は「場面（scene）」で選ぶ。**カテゴリだけで選んでいた版は、
レシピ21本が全部ノート＋鉛筆になって「記事と関係ない絵」になった
（2026-08-08 オーナー指摘）。scene ごとに主役の道具を変える。

⚠️ **主役は中央 x=270〜450 に置く。**カードのサムネis 84px角で、
`object-fit: cover` が横長バナー(720x180)の中央180px幅だけを切り出す
（計算で確認済み）。端に置いた小物はカードでは見えない。

slug をシードに配置と小物を揺らすので、同じ場面でも1枚ずつ違う絵になる。
同じ slug なら必ず同じ絵（決定的）。

⚠️ SVG内で使う class は必ず下の STYLE に定義すること。定義漏れは黒塗りに
なる（2026-08-05 実害）。tests/test_make_eyecatch.py が機械で照合している。

使い方: python -m tools.make_eyecatch
出力: static/images/eyecatch/<slug>.svg（毎回すべて作り直す・冪等）
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
OUTPUT_DIR = ROOT / "static" / "images" / "eyecatch"

CATEGORIES = ("recipes", "tools")

WIDTH, HEIGHT = 720, 180
# カードのサムネに映る範囲。主役はこの中に収める
FOCUS_LEFT, FOCUS_RIGHT = 270, 450
FOCUS_CENTER = (FOCUS_LEFT + FOCUS_RIGHT) // 2

# scene が無い記事の受け皿（固定ページには付けない）
CATEGORY_FALLBACK_SCENE = {"recipes": "work", "tools": "choose"}

SCENE_RE = re.compile(r"^scene:\s*(\w+)\s*$", re.MULTILINE)

CORAL = "#D85A30"
AMBER = "#FAC775"
AMBER_DEEP = "#EF9F27"
GREEN = "#97C459"
GREEN_DEEP = "#639922"
PINK = "#ED93B1"
PINK_PALE = "#F5C4B3"
BLUE = "#85B7EB"
PURPLE = "#AFA9EC"

STYLE = """<style>
.ec-bg{fill:#F5E6D3}
.ec-paper{fill:#FFFDF8}
.ec-ln{stroke:#4A3F35}
.ec-rule{stroke:#D9CBB8}
.ec-ink{fill:#4A3F35}
@media (prefers-color-scheme: dark){
.ec-bg{fill:#33251B}
.ec-paper{fill:#241D15}
.ec-ln{stroke:#EFE7DA}
.ec-rule{stroke:#5C5044}
.ec-ink{fill:#EFE7DA}
}
</style>"""


def seed_from(slug: str) -> int:
    """slug から決定的なシードを作る。ビルド環境が変わっても揺れない。"""
    return int(hashlib.sha1(slug.encode("utf-8")).hexdigest(), 16)


def pick(seed: int, salt: int, options: int) -> int:
    return (seed >> (salt * 5)) % options


# --- 部品。(x, y) は左上または中心 ---

def notebook(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect width="104" height="74" rx="8" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<line x1="14" y1="22" x2="88" y2="22" class="ec-rule" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="14" y1="38" x2="78" y2="38" class="ec-rule" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="14" y1="54" x2="86" y2="54" stroke="{CORAL}" stroke-width="3" stroke-linecap="round"/>'
        f"</g>"
    )


def clipboard(x: int, y: int) -> str:
    """仕事＝チェックの付いた書類。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect width="96" height="112" rx="8" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<rect x="32" y="-9" width="32" height="16" rx="5" fill="{AMBER}" class="ec-ln" stroke-width="3"/>'
        f'<path d="M18 34 l8 8 14 -16" fill="none" stroke="{GREEN_DEEP}" stroke-width="4" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<line x1="50" y1="36" x2="80" y2="36" class="ec-rule" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M18 62 l8 8 14 -16" fill="none" stroke="{GREEN_DEEP}" stroke-width="4" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<line x1="50" y1="64" x2="76" y2="64" class="ec-rule" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="18" y1="92" x2="60" y2="92" class="ec-rule" stroke-width="3" stroke-linecap="round"/>'
        f"</g>"
    )


def magnifier(x: int, y: int, angle: int = 0) -> str:
    """情報収集＝探す。"""
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<circle cx="0" cy="0" r="34" class="ec-paper ec-ln" stroke-width="4"/>'
        f'<circle cx="0" cy="0" r="24" fill="none" stroke="{BLUE}" stroke-width="2.5"/>'
        f'<line x1="25" y1="25" x2="50" y2="50" class="ec-ln" stroke-width="8" stroke-linecap="round"/>'
        f"</g>"
    )


def antenna(x: int, y: int) -> str:
    """情報収集＝向こうから届く。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<line x1="0" y1="0" x2="0" y2="-34" class="ec-ln" stroke-width="3.5" stroke-linecap="round"/>'
        f'<circle cx="0" cy="-38" r="5" fill="{CORAL}"/>'
        f'<path d="M-14 -46 q14 -12 28 0" fill="none" stroke="{CORAL}" stroke-width="2.5" '
        f'stroke-linecap="round" opacity="0.8"/>'
        f'<path d="M-22 -56 q22 -18 44 0" fill="none" stroke="{CORAL}" stroke-width="2.5" '
        f'stroke-linecap="round" opacity="0.5"/>'
        f"</g>"
    )


def gear(x: int, y: int, r: int = 26) -> str:
    """自動化＝仕掛け。"""
    teeth = "".join(
        f'<rect x="-4" y="{-r - 9}" width="8" height="12" rx="2" fill="{AMBER_DEEP}" '
        f'transform="rotate({a})"/>'
        for a in range(0, 360, 45)
    )
    return (
        f'<g transform="translate({x},{y})">{teeth}'
        f'<circle cx="0" cy="0" r="{r}" fill="{AMBER}" class="ec-ln" stroke-width="3"/>'
        f'<circle cx="0" cy="0" r="{r // 2 - 2}" class="ec-bg ec-ln" stroke-width="3"/>'
        f"</g>"
    )


def clock(x: int, y: int) -> str:
    """自動化＝決まった時刻。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<circle cx="0" cy="0" r="24" class="ec-paper ec-ln" stroke-width="3.5"/>'
        f'<line x1="0" y1="0" x2="0" y2="-14" class="ec-ln" stroke-width="3.5" stroke-linecap="round"/>'
        f'<line x1="0" y1="0" x2="11" y2="5" stroke="{CORAL}" stroke-width="3.5" stroke-linecap="round"/>'
        f"</g>"
    )


def loop_arrows(x: int, y: int) -> str:
    """自動化＝繰り返し。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M-24 6 a24 24 0 1 1 42 14" fill="none" stroke="{GREEN_DEEP}" '
        f'stroke-width="3.5" stroke-linecap="round"/>'
        f'<path d="M12 16 l7 6 -1 -10 Z" fill="{GREEN_DEEP}"/>'
        f"</g>"
    )


def house(x: int, y: int) -> str:
    """暮らし＝家。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M-46 0 L0 -38 L46 0 Z" fill="{PINK_PALE}" class="ec-ln" '
        f'stroke-width="3.5" stroke-linejoin="round"/>'
        f'<rect x="-36" y="0" width="72" height="52" class="ec-paper ec-ln" stroke-width="3.5"/>'
        f'<rect x="-12" y="18" width="24" height="34" rx="3" fill="{AMBER}" class="ec-ln" stroke-width="3"/>'
        f"</g>"
    )


def receipt(x: int, y: int, angle: int = 0) -> str:
    """暮らし＝紙もの。"""
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<path d="M0 0 h40 v58 l-8 -5 -8 5 -8 -5 -8 5 -8 -5 V0 Z" '
        f'class="ec-paper ec-ln" stroke-width="2.5" stroke-linejoin="round"/>'
        f'<line x1="8" y1="14" x2="32" y2="14" class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f'<line x1="8" y1="26" x2="26" y2="26" class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f"</g>"
    )


def palette(x: int, y: int) -> str:
    """遊び・創作＝絵の具。"""
    dots = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="6" fill="{c}"/>'
        for cx, cy, c in ((-16, -10, CORAL), (2, -16, AMBER), (18, -4, GREEN), (8, 12, PINK))
    )
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M-38 6 a38 32 0 1 1 60 22 a10 9 0 0 0 -12 12 a38 32 0 0 1 -48 -34 Z" '
        f'class="ec-paper ec-ln" stroke-width="3.5"/>{dots}'
        f"</g>"
    )


def brush(x: int, y: int, angle: int = 0) -> str:
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<rect width="12" height="52" rx="3" fill="{AMBER}" class="ec-ln" stroke-width="2.5"/>'
        f'<path d="M0 52 h12 l-2 16 h-8 Z" fill="{PURPLE}" class="ec-ln" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
        f"</g>"
    )


def balance(x: int, y: int) -> str:
    """AIを選ぶ＝比べる。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<line x1="0" y1="0" x2="0" y2="46" class="ec-ln" stroke-width="4" stroke-linecap="round"/>'
        f'<line x1="-42" y1="0" x2="42" y2="0" class="ec-ln" stroke-width="4" stroke-linecap="round"/>'
        f'<path d="M-56 18 h28 l-14 -18 Z" fill="{AMBER}" class="ec-ln" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
        f'<path d="M28 24 h28 l-14 -24 Z" fill="{BLUE}" class="ec-ln" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
        f'<circle cx="0" cy="-4" r="5" fill="{CORAL}"/>'
        f'<path d="M-20 46 h40" class="ec-ln" stroke-width="4" stroke-linecap="round"/>'
        f"</g>"
    )


def price_tag(x: int, y: int, angle: int = 0) -> str:
    """副業＝自分の仕事に値を付ける。

    ⚠️ **札束・硬貨の山・右肩上がりのグラフは描かない。**この場面の記事は
    「必ず稼げる」「月◯万」を書かない約束なので、絵でも稼ぎを匂わせない
    （キューの「副業」節の冒頭の縛り）。値札は「自分で決める」ほうの絵。
    """
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<path d="M0 40 L34 4 H92 V76 H34 Z" class="ec-paper ec-ln" '
        f'stroke-width="3" stroke-linejoin="round"/>'
        f'<line x1="34" y1="6" x2="34" y2="74" stroke="{AMBER_DEEP}" '
        f'stroke-width="3" opacity="0.55"/>'
        f'<circle cx="24" cy="40" r="7" class="ec-bg ec-ln" stroke-width="3"/>'
        f'<line x1="48" y1="30" x2="80" y2="30" stroke="{CORAL}" '
        f'stroke-width="3.5" stroke-linecap="round"/>'
        f'<line x1="48" y1="52" x2="72" y2="52" class="ec-rule" '
        f'stroke-width="3" stroke-linecap="round"/>'
        f"</g>"
    )


def coin(x: int, y: int) -> str:
    """副業の小物。⚠️ 通貨記号は入れない（金額の約束に読ませない）。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<circle r="17" fill="{AMBER}" class="ec-ln" stroke-width="3"/>'
        f'<circle r="9" fill="none" class="ec-ln" stroke-width="2.5" opacity="0.7"/>'
        f"</g>"
    )


def shield(x: int, y: int) -> str:
    """詐欺を防ぐ＝確かめてから進む。

    ⚠️ **怖がらせる絵にしない**（ドクロ・警告の三角・赤い×・鎖）。この場面の型は
    「詐欺かどうかをAIに判定させる」ではなく「**確認の手順に変える**」なので、
    盾の中は「確かめた印」のチェックにする。
    """
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M0 0 L40 14 V50 C40 74 22 90 0 98 C-22 90 -40 74 -40 50 V14 Z" '
        f'class="ec-paper ec-ln" stroke-width="3.5" stroke-linejoin="round"/>'
        f'<path d="M-16 48 l12 13 22 -28" fill="none" stroke="{GREEN_DEEP}" '
        f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        f"</g>"
    )


def envelope(x: int, y: int, angle: int = 0) -> str:
    """身に覚えのない知らせ。⚠️ 「!」や「×」の印は付けない（煽らない）。"""
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<rect width="60" height="42" rx="5" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<path d="M0 5 L30 27 L60 5" fill="none" class="ec-ln" stroke-width="3" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f"</g>"
    )


def padlock(x: int, y: int) -> str:
    """セキュリティ対策＝鍵をかける・渡さない。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M-17 0 V-13 a17 17 0 0 1 34 0 V0" fill="none" class="ec-ln" '
        f'stroke-width="6" stroke-linecap="round"/>'
        f'<rect x="-29" y="0" width="58" height="46" rx="8" fill="{AMBER}" '
        f'class="ec-ln" stroke-width="3"/>'
        f'<circle cy="19" r="6" class="ec-ink"/>'
        f'<path d="M0 23 v11" fill="none" class="ec-ln" stroke-width="4" stroke-linecap="round"/>'
        f"</g>"
    )


def signpost(x: int, y: int) -> str:
    """はじめて＝どっちへ行くか。"""
    return (
        f'<g transform="translate({x},{y})">'
        f'<line x1="0" y1="0" x2="0" y2="72" class="ec-ln" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M-2 6 h44 l12 12 -12 12 h-44 Z" fill="{AMBER}" class="ec-ln" '
        f'stroke-width="3" stroke-linejoin="round"/>'
        f'<path d="M2 38 h-40 l-12 11 12 11 h40 Z" fill="{PINK_PALE}" class="ec-ln" '
        f'stroke-width="3" stroke-linejoin="round"/>'
        f"</g>"
    )


def pencil(x: int, y: int, angle: int) -> str:
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<rect width="16" height="62" rx="3" fill="{AMBER}" class="ec-ln" stroke-width="3"/>'
        f'<path d="M2 64 L8 80 L14 64 Z" fill="{CORAL}" class="ec-ln" '
        f'stroke-width="2.5" stroke-linejoin="round"/>'
        f"</g>"
    )


def sticky(x: int, y: int, angle: int) -> str:
    return (
        f'<g transform="translate({x},{y}) rotate({angle})">'
        f'<rect width="42" height="42" rx="4" fill="{PINK_PALE}" class="ec-ln" stroke-width="2.5"/>'
        f'<line x1="9" y1="18" x2="33" y2="18" class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f'<line x1="9" y1="29" x2="27" y2="29" class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f"</g>"
    )


def coffee(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<circle cx="0" cy="0" r="17" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<path d="M-7 -3 Q0 -10 7 -3" fill="none" stroke="{GREEN_DEEP}" '
        f'stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M-4 -26 Q-1 -32 4 -30 M2 -22 Q5 -28 10 -26" fill="none" '
        f'class="ec-rule" stroke-width="2.5" stroke-linecap="round"/>'
        f"</g>"
    )


def robot(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<line x1="42" y1="0" x2="42" y2="-12" class="ec-ln" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="42" cy="-16" r="5" fill="{CORAL}"/>'
        f'<rect width="84" height="60" rx="15" class="ec-paper ec-ln" stroke-width="3"/>'
        f'<circle cx="28" cy="28" r="5" class="ec-ink"/>'
        f'<circle cx="56" cy="28" r="5" class="ec-ink"/>'
        f'<path d="M30 42 Q42 50 54 42" fill="none" stroke="{CORAL}" '
        f'stroke-width="3" stroke-linecap="round"/>'
        f'<rect x="16" y="62" width="52" height="20" rx="8" fill="{PINK_PALE}" '
        f'class="ec-ln" stroke-width="3"/>'
        f"</g>"
    )


def sprout(x: int, y: int) -> str:
    return (
        f'<g transform="translate({x},{y})">'
        f'<path d="M0 0 Q2 -18 12 -24" fill="none" stroke="{GREEN_DEEP}" '
        f'stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M12 -24 Q4 -28 3 -38 Q14 -36 15 -26 Z" fill="{GREEN}" '
        f'stroke="{GREEN_DEEP}" stroke-width="2"/>'
        f'<path d="M12 -24 Q20 -30 30 -28 Q24 -18 14 -21 Z" fill="{GREEN}" '
        f'stroke="{GREEN_DEEP}" stroke-width="2"/>'
        f"</g>"
    )


def sun(x: int, y: int) -> str:
    rays = "".join(
        f'<line x1="0" y1="-24" x2="0" y2="-30" stroke="{AMBER_DEEP}" stroke-width="3" '
        f'stroke-linecap="round" transform="rotate({a})"/>'
        for a in range(0, 360, 45)
    )
    return f'<g transform="translate({x},{y})"><circle cx="0" cy="0" r="17" fill="{AMBER}"/>{rays}</g>'


def star(x: int, y: int, r: int = 12) -> str:
    points = []
    for i in range(10):
        radius = r if i % 2 == 0 else r * 0.45
        angle = -90 + i * 36
        points.append(f"{radius * _cos(angle):.1f},{radius * _sin(angle):.1f}")
    return (
        f'<polygon points="{" ".join(points)}" fill="{AMBER}" stroke="{AMBER_DEEP}" '
        f'stroke-width="2" transform="translate({x},{y})"/>'
    )


def _cos(deg: float) -> float:
    import math

    return math.cos(math.radians(deg))


def _sin(deg: float) -> float:
    import math

    return math.sin(math.radians(deg))


def ground(seed: int) -> str:
    lift = pick(seed, 7, 3) * 4
    return (
        f'<path d="M40 {150 - lift} Q200 {128 - lift} 380 {142 - lift} T690 {134 - lift}" '
        f'fill="none" stroke="{CORAL}" stroke-width="3.5" stroke-linecap="round" opacity="0.85"/>'
    )


# --- 場面ごとの構図。主役は必ず中央 270〜450 に置く ---

def _scene_start(seed: int) -> str:
    """はじめて＝道しるべと芽。"""
    return signpost(FOCUS_CENTER - 4, 44) + sprout(238, 150) + coffee(496, 116)


def _scene_work(seed: int) -> str:
    """仕事＝チェック付きの書類。"""
    variant = pick(seed, 1, 2)
    main = clipboard(FOCUS_CENTER - 48, 40)
    if variant == 0:
        return main + pencil(456, 54, 16) + coffee(236, 120)
    return main + sticky(452, 46, 9) + pencil(226, 58, -14)


def _scene_research(seed: int) -> str:
    """情報収集＝探す・届く。"""
    variant = pick(seed, 1, 2)
    main = magnifier(FOCUS_CENTER, 86, -14)
    if variant == 0:
        return main + antenna(246, 128) + notebook(452, 66)
    return main + notebook(206, 62) + antenna(492, 132)


def _scene_automate(seed: int) -> str:
    """自動化＝歯車と時刻。"""
    variant = pick(seed, 1, 2)
    main = gear(FOCUS_CENTER, 88, 30)
    if variant == 0:
        return main + clock(244, 92) + loop_arrows(468, 84)
    return main + loop_arrows(240, 84) + clock(470, 92)


def _scene_life(seed: int) -> str:
    """暮らし＝家と紙もの。"""
    variant = pick(seed, 1, 2)
    main = house(FOCUS_CENTER, 62)
    if variant == 0:
        return main + receipt(228, 58, -7) + sprout(492, 148)
    return main + sprout(232, 148) + receipt(470, 56, 8)


def _scene_fun(seed: int) -> str:
    """遊び・創作＝絵の具と星。"""
    variant = pick(seed, 1, 2)
    main = palette(FOCUS_CENTER, 88)
    if variant == 0:
        return main + brush(452, 58, 14) + star(244, 70, 13)
    return main + star(474, 64, 13) + brush(232, 60, -12)


def _scene_choose(seed: int) -> str:
    """AIを選ぶ＝天秤。"""
    variant = pick(seed, 1, 2)
    main = balance(FOCUS_CENTER, 62)
    if variant == 0:
        return main + robot(200, 56) + sticky(494, 62, 8)
    return main + sticky(214, 60, -8) + robot(474, 56)


def _scene_earn(seed: int) -> str:
    """副業＝自分の仕事に値を付けて納める。"""
    variant = pick(seed, 1, 2)
    main = price_tag(FOCUS_CENTER - 46, 50, -6)
    if variant == 0:
        return main + coin(238, 112) + notebook(452, 58)
    return main + notebook(202, 56) + coin(490, 108)


def _scene_safety(seed: int) -> str:
    """詐欺を防ぐ＝確かめてから進む。"""
    variant = pick(seed, 1, 2)
    main = shield(FOCUS_CENTER, 40)
    if variant == 0:
        return main + envelope(202, 96, -7) + sticky(478, 56, 8)
    return main + sticky(214, 54, -8) + envelope(450, 98, 6)


def _scene_security(seed: int) -> str:
    """セキュリティ対策＝鍵をかける・渡さない。"""
    variant = pick(seed, 1, 2)
    main = padlock(FOCUS_CENTER, 66)
    if variant == 0:
        return main + envelope(206, 94, 6) + robot(474, 54)
    return main + robot(196, 54) + envelope(454, 92, -6)


# ⚠️ ここに無い場面は黙って「仕事」の絵になる（build_svg の受け皿）。
# 実際 earn / safety / security の3つが、絵柄の無いまま公開されていた
# （2026-08-14 にオーナーが画面で気づいた）。config.SCENES と突き合わせる
# テスト（test_every_scene_in_config_has_a_picture）で再発を止めている。
SCENE_BUILDERS = {
    "start": _scene_start,
    "work": _scene_work,
    "research": _scene_research,
    "automate": _scene_automate,
    "life": _scene_life,
    "earn": _scene_earn,
    "safety": _scene_safety,
    "security": _scene_security,
    "fun": _scene_fun,
    "choose": _scene_choose,
}


def build_svg(slug: str, category: str, scene: str | None = None) -> str:
    """アイキャッチ1枚ぶんのSVG。同じ入力なら必ず同じ出力。

    scene が無ければカテゴリから受け皿の場面を決める（絵が無い記事を作らない）。
    """
    scene = scene or CATEGORY_FALLBACK_SCENE.get(category, "work")
    builder = SCENE_BUILDERS.get(scene, _scene_work)
    seed = seed_from(f"{slug}/{scene}")
    sun_x = 84 if pick(seed, 3, 2) == 0 else 636
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-hidden="true">'
        f"{STYLE}"
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" class="ec-bg"/>'
        f"{sun(sun_x, 44)}{ground(seed)}{builder(seed)}"
        f"</svg>"
    )


def scene_of(text: str) -> str | None:
    """frontmatter の scene を読む。無ければ None。"""
    found = SCENE_RE.search(text)
    return found.group(1) if found else None


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
            text = path.read_text(encoding="utf-8")
            svg = build_svg(path.stem, category, scene_of(text))
            (output_dir / f"{path.stem}.svg").write_text(svg, encoding="utf-8", newline="\n")
            written += 1
    return written


if __name__ == "__main__":
    count = main()
    print(f"アイキャッチ {count} 枚を {OUTPUT_DIR} に生成しました")
    sys.exit(0)
