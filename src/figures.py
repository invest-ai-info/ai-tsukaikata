# -*- coding: utf-8 -*-
"""図（SVG）の文字が枠からはみ出していないか・線に重なっていないかを検査する。

図は手で座標を書くので、文字が枠を超えても線を跨いでも、
ファイルを読んだだけでは分からない。目視でも見落とす（実際に
「見出しが枠線を跨ぐ」「ラベルが枠からはみ出る」を公開直前まで見逃した）。

ブラウザの実測値と突き合わせて係数を決めてあるが、フォントは環境で
変わるので、多少の余裕（TOLERANCE）を見て「明らかにおかしいもの」を
落とす。細かい1〜2pxのズレは追わない。
"""
from __future__ import annotations

import re
import unicodedata
from xml.etree import ElementTree as ET

SVG_NS = "{http://www.w3.org/2000/svg}"

# 実測（2026-08-02・315要素）から最小二乗で求めた値を、安全側に丸めたもの。
# 半角は文字種でかなり違う（i と W で3倍）ので、ひとまとめにすると
# 英字の長い行で3割以上ずれて誤検知になる。
WIDE_RATIO = 1.02      # 全角・絵文字
MONO_RATIO = 0.58      # 等幅（実測 0.543〜0.572）

_THIN = set(" .,:;'`!|iljI()[]{}/\\-")
_NARROW = set("ftrs")
_WIDE_LATIN = set("mwMW")

NARROW_RATIO = {
    False: {"thin": 0.30, "narrow": 0.36, "digit": 0.58, "upper": 0.65, "wide": 0.84, "other": 0.60},
    True: {"thin": 0.40, "narrow": 0.44, "digit": 0.61, "upper": 0.67, "wide": 1.00, "other": 0.62},
}

ASCENT_RATIO = 1.11   # ベースラインより上（実測の最大値）
DESCENT_RATIO = 0.25

# 推定幅は実測の 1.00〜1.15 倍に収まることを315要素で確認済み。
# 横方向は「推定 ÷ この値」＝ありうる最小の幅で判定する。こうすると
# 見逃しは増えるが、誤検知は原理的に起きない。止まったら本当にはみ出している。
WIDTH_SAFETY = 1.15

TOLERANCE = 2.0        # これ以下のはみ出しは見ない
LINE_MARGIN = 1.5      # 線と文字がこれ以上重なったら跨いでいるとみなす


def _is_wide(ch: str) -> bool:
    """日本語フォントで全角幅になる文字か。

    Ambiguous（…→⚠× など）も日本語環境では全角で出るので全角に数える。
    """
    return unicodedata.east_asian_width(ch) in ("W", "F", "A")


def _narrow_class(ch: str) -> str:
    if ch in _THIN:
        return "thin"
    if ch in _NARROW:
        return "narrow"
    if ch.isdigit():
        return "digit"
    if ch in _WIDE_LATIN:
        return "wide"
    if ch.isupper():
        return "upper"
    return "other"


def text_width(text: str, size: float, family: str, bold: bool) -> float:
    ratios = NARROW_RATIO[bold]
    total = 0.0
    for ch in text:
        if ch == "\n":
            continue
        if _is_wide(ch):
            total += WIDE_RATIO
        elif family == "mono":
            total += MONO_RATIO
        else:
            total += ratios[_narrow_class(ch)]
    return total * size


def parse_styles(svg_text: str) -> dict[str, dict]:
    """<style> の中のクラス定義から font-size / weight / family を拾う。"""
    styles: dict[str, dict] = {}
    for block in re.findall(r"<style>(.*?)</style>", svg_text, re.DOTALL):
        # ダークモードの上書きは色だけなので見ない
        block = re.sub(r"@media[^{]*\{.*?\}\s*\}", "", block, flags=re.DOTALL)
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", block):
            size = re.search(r"font-size:\s*([\d.]+)px", body)
            weight = re.search(r"font-weight:\s*(\d+)", body)
            family = "mono" if "monospace" in body or "Consolas" in body else None
            for name in selector.split(","):
                name = name.strip()
                if not name.startswith("."):
                    continue
                entry = styles.setdefault(name[1:], {})
                if size:
                    entry["size"] = float(size.group(1))
                if weight:
                    entry["bold"] = int(weight.group(1)) >= 600
                if family:
                    entry["family"] = family
    return styles


def _tag(element) -> str:
    return element.tag.replace(SVG_NS, "")


class _Text:
    def __init__(self, element, styles):
        cls = element.get("class", "")
        style = {}
        for name in cls.split():
            style.update(styles.get(name, {}))
        self.content = "".join(element.itertext())
        self.size = style.get("size", 13.0)
        self.bold = style.get("bold", False)
        self.family = style.get("family", "sans")
        self.x = float(element.get("x", 0))
        self.baseline = float(element.get("y", 0))
        self.width = text_width(self.content, self.size, self.family, self.bold)

    @property
    def top(self) -> float:
        return self.baseline - self.size * ASCENT_RATIO

    @property
    def bottom(self) -> float:
        return self.baseline + self.size * DESCENT_RATIO

    @property
    def right_min(self) -> float:
        """ありうる最小の右端。ここを超えていれば確実にはみ出している。"""
        return self.x + self.width / WIDTH_SAFETY

    @property
    def right_max(self) -> float:
        return self.x + self.width

    @property
    def label(self):
        text = " ".join(self.content.split())
        return text[:26] + ("…" if len(text) > 26 else "")


def _stroked(element, styles) -> bool:
    """枠線が描かれる要素か（塗りだけの帯は線を引かないので対象外）。"""
    for name in element.get("class", "").split():
        if "stroke" in styles.get(name, {}).get("raw", ""):
            return True
    return False


def _class_has_stroke(svg_text: str) -> set[str]:
    """stroke を持つクラス名の集合。"""
    names = set()
    for block in re.findall(r"<style>(.*?)</style>", svg_text, re.DOTALL):
        block = re.sub(r"@media[^{]*\{.*?\}\s*\}", "", block, flags=re.DOTALL)
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", block):
            if re.search(r"\bstroke:\s*(?!none)", body):
                for name in selector.split(","):
                    name = name.strip()
                    if name.startswith("."):
                        names.add(name[1:])
    return names


def check_svg(name: str, svg_text: str) -> list[str]:
    """1枚を検査してエラー文字列のリストを返す。"""
    errors: list[str] = []
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as error:
        return [f"{name}: XMLとして読めません: {error}"]

    view = root.get("viewBox", "").split()
    if len(view) != 4:
        return [f"{name}: viewBox がありません"]
    vw, vh = float(view[2]), float(view[3])

    styles = parse_styles(svg_text)
    stroked = _class_has_stroke(svg_text)

    texts = [_Text(e, styles) for e in root.iter() if _tag(e) == "text"]

    rects = []
    for e in root.iter():
        if _tag(e) != "rect":
            continue
        try:
            x, y = float(e.get("x", 0)), float(e.get("y", 0))
            w, h = float(e.get("width", 0)), float(e.get("height", 0))
        except ValueError:
            continue
        has_stroke = bool(set(e.get("class", "").split()) & stroked)
        rects.append({"box": (x, y, x + w, y + h), "area": w * h, "stroke": has_stroke})

    # 水平な線（stroke を持つ rect の上下辺と <line>）
    h_lines = []
    for r in rects:
        if r["stroke"]:
            x0, y0, x1, y1 = r["box"]
            h_lines.append((x0, x1, y0))
            h_lines.append((x0, x1, y1))
    for e in root.iter():
        if _tag(e) != "line":
            continue
        y1, y2 = float(e.get("y1", 0)), float(e.get("y2", 0))
        if abs(y1 - y2) < 0.5:
            h_lines.append((float(e.get("x1", 0)), float(e.get("x2", 0)), y1))

    for t in texts:
        ty0, ty1 = t.top, t.bottom

        # ① 図の外へのはみ出し（縦は厳密、横は最小幅で判定）
        if t.right_min > vw - TOLERANCE:
            errors.append(
                f"{name}: 「{t.label}」が図の右にはみ出しています"
                f"（右端 {t.right_min:.0f}〜{t.right_max:.0f} / 図の幅 {vw:.0f}）"
            )
        if ty1 > vh - TOLERANCE or ty0 < -TOLERANCE:
            errors.append(
                f"{name}: 「{t.label}」が図の上下にはみ出しています"
                f"（文字 {ty0:.0f}〜{ty1:.0f} / 図の高さ {vh:.0f}）"
            )

        # ② 文字を囲んでいる一番小さい枠からのはみ出し。
        #    枠とみなすのは線のある矩形だけ。塗りだけの矩形は角を四角く
        #    見せるための当て板などで、境界が描かれないため囲いではない。
        containing = [
            r for r in rects
            if r["stroke"]
            and r["box"][0] <= t.x + 1 <= r["box"][2]
            and r["box"][1] <= t.baseline <= r["box"][3]
            and r["area"] < vw * vh * 0.95
        ]
        if containing:
            inner = min(containing, key=lambda r: r["area"])
            bx0, by0, bx1, by1 = inner["box"]
            if t.right_min > bx1 + TOLERANCE:
                errors.append(
                    f"{name}: 「{t.label}」が枠から右にはみ出しています"
                    f"（文字の右端 {t.right_min:.0f}〜{t.right_max:.0f} / 枠 {bx1:.0f}）"
                )
            if ty0 < by0 - TOLERANCE or ty1 > by1 + TOLERANCE:
                errors.append(
                    f"{name}: 「{t.label}」が枠から上下にはみ出しています"
                    f"（文字 {ty0:.0f}〜{ty1:.0f} / 枠 {by0:.0f}〜{by1:.0f}）"
                )

        # ③ 線が文字を貫いていないか（縦位置だけで判定できるので厳密）
        for lx0, lx1, ly in h_lines:
            if min(lx0, lx1) - 1 <= t.right_min and max(lx0, lx1) + 1 >= t.x:
                if ty0 + LINE_MARGIN < ly < ty1 - LINE_MARGIN:
                    errors.append(
                        f"{name}: 「{t.label}」を横線が貫いています"
                        f"（文字 {ty0:.0f}〜{ty1:.0f} / 線 y={ly:.0f}）"
                    )
                    break

    return errors
