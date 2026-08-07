# -*- coding: utf-8 -*-
"""ブランド画像（ヒーロー写真・ファビコン）を1枚の原画から作る。

原画＝`static/images/og-card.png`（オーナーが生成したイラスト）。
ここから切り出しと縮小だけで作るので、絵柄は必ず全部そろう。手で
書き出したPNGを何枚も置くと、差し替えたとき片方だけ古くなる。

⚠️ 原画を差し替えたら、このスクリプトを再実行すること。
座標は原画 1659x948 を前提にしている（サイズが変わったら FACE_BOX を測り直す）。

使い方: python -m tools.make_brand_images
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "static" / "images"
SOURCE = IMAGES / "og-card.png"

# ロボットの顔の位置（原画 1659x948 での実測）。ファビコンの元になる
FACE_BOX = (1340, 345, 1592, 597)

HERO_WIDTH = 1200
JPEG_QUALITY = 82  # 実測: 1200px幅で約128KB。88にすると164KBで、見た目の差は出ない
FAVICON_SIZES = (16, 32, 48)
APPLE_TOUCH = 180


def build(source: Path = SOURCE, out: Path = IMAGES) -> list[str]:
    """作ったファイル名を返す。"""
    if not source.exists():
        raise SystemExit(f"原画がありません: {source}")
    image = Image.open(source).convert("RGB")
    made: list[str] = []

    # ヒーローとOGPは同じ絵。PNGのままだと1.3MBで表示が遅いのでJPEGにする
    ratio = HERO_WIDTH / image.width
    hero = image.resize((HERO_WIDTH, round(image.height * ratio)), Image.LANCZOS)
    for name in ("hero-photo.jpg", "og-image.jpg"):
        hero.save(
            out / name, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True
        )
        made.append(name)

    face = image.crop(FACE_BOX)

    # apple-touch は背景の透過を許さないので、そのままの正方形で出す
    face.resize((APPLE_TOUCH, APPLE_TOUCH), Image.LANCZOS).save(
        out / "apple-touch-icon.png", optimize=True
    )
    made.append("apple-touch-icon.png")

    face.resize((512, 512), Image.LANCZOS).save(out / "icon-512.png", optimize=True)
    made.append("icon-512.png")

    # .ico は複数サイズを1ファイルに入れられる。Safari と古いブラウザ向け
    face.resize((256, 256), Image.LANCZOS).save(
        out / "favicon.ico", sizes=[(s, s) for s in FAVICON_SIZES]
    )
    made.append("favicon.ico")

    return made


if __name__ == "__main__":
    names = build()
    print("作成: " + " / ".join(names))
    sys.exit(0)
