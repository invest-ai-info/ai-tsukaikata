# -*- coding: utf-8 -*-
"""「AIの使い方」のデザイン部品を Claude Design 用バンドルに固める。

各プレビューは自己完結（style.css と SVG をインライン）。先頭行の
<!-- @dsCard group="…" --> がカード索引になる（MarketWatch連携と同じ型）。
出力: このスクリプトと同じ場所の ds_bundle/
"""
import base64
from pathlib import Path

REPO = Path(r"C:\Users\info0\ai-tsukaikata")
OUT = Path(__file__).resolve().parent / "ds_bundle"

CSS = (REPO / "static" / "style.css").read_text(encoding="utf-8")
HERO_SVG = (REPO / "static" / "images" / "hero.svg").read_text(encoding="utf-8")

# Design側は外部ファイルを持てないので、写真はdata URIで焼き込む
_hero_jpg = (REPO / "static" / "images" / "hero-photo.jpg").read_bytes()
HERO_PHOTO_DATA_URI = "data:image/jpeg;base64," + base64.b64encode(_hero_jpg).decode()
FIGURE_SVG = (REPO / "static" / "images" / "feels-off-map.svg").read_text(encoding="utf-8")

def eyecatch(slug: str) -> str:
    return (REPO / "static" / "images" / "eyecatch" / f"{slug}.svg").read_text(encoding="utf-8")

def page(group: str, title: str, body: str, max_width: str = "46rem") -> str:
    return f"""<!-- @dsCard group="{group}" -->
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{CSS}
.ds-stage {{ max-width: {max_width}; margin: 0 auto; padding: 1.5rem 1.1rem; }}
.ds-note {{ color: var(--muted); font-size: 0.8rem; margin: 0 0 1rem; }}
</style>
</head>
<body>
<div class="ds-stage">
<p class="ds-note">{title} — ai-tsukaikata.com「あたたかい紙」デザイン</p>
{body}
</div>
</body>
</html>
"""

FILES: dict[str, str] = {}

# --- foundations ---

_swatches_light = [
    ("--bg", "#faf5ec", "紙"), ("--fg", "#3d3428", "文字"), ("--muted", "#7a6b57", "弱い文字"),
    ("--line", "#e8dcc8", "罫線"), ("--accent", "#a8481d", "リンク"), ("--accent-deco", "#d85a30", "飾り"),
    ("--card-bg", "#fffdf8", "カード"), ("--prompt-bg", "#fbf0dc", "指示文"),
]
_swatches_dark = [
    ("--bg", "#1c1712", "紙"), ("--fg", "#efe7da", "文字"), ("--muted", "#a99b87", "弱い文字"),
    ("--line", "#3a3226", "罫線"), ("--accent", "#f0997b", "リンク"), ("--accent-deco", "#f0997b", "飾り"),
    ("--card-bg", "#241d15", "カード"), ("--prompt-bg", "#2c2317", "指示文"),
]
_h2_colors = [
    ("🎯 これで何ができるか", "#f9e7dc", "#d85a30"), ("📋 前提", "#f8edd6", "#ba7517"),
    ("💬 AIへの頼み方", "#eff3df", "#639922"), ("🛠️ 言い直し方", "#fcebeb", "#a32d2d"),
    ("🚀 応用・次の一手", "#fbeaf0", "#d4537e"),
]

def _swatch_row(items, bg, fg):
    cells = "".join(
        f'<div style="flex:1;min-width:110px;"><div style="height:56px;border-radius:8px;'
        f'background:{hex_};border:1px solid rgba(128,116,96,.35);"></div>'
        f'<p style="margin:.35rem 0 0;font-size:.78rem;color:{fg};">{label}<br>'
        f'<code style="font-size:.72rem;">{var} {hex_}</code></p></div>'
        for var, hex_, label in items
    )
    return (f'<div style="background:{bg};padding:1rem;border-radius:10px;'
            f'display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1rem;">{cells}</div>')

FILES["foundations/colors.html"] = page("Foundations", "配色（ライト/ダーク）",
    '<h2 class="section-title">ライト</h2>' + _swatch_row(_swatches_light, "#faf5ec", "#3d3428")
    + '<h2 class="section-title">ダーク（暖かい闇）</h2>' + _swatch_row(_swatches_dark, "#1c1712", "#efe7da")
    + '<h2 class="section-title">見出し帯の5色</h2>'
    + "".join(
        f'<div style="display:flex;align-items:center;gap:.65rem;background:{bg};'
        f'border-left:5px solid {bar};padding:.6rem 1rem;border-radius:8px;margin:.4rem 0;">'
        f'<span style="font-size:.95rem;color:#3d3428;">{label}</span>'
        f'<code style="margin-left:auto;font-size:.72rem;color:#7a6b57;">{bar}</code></div>'
        for label, bg, bar in _h2_colors
    ))

FILES["foundations/typography.html"] = page("Foundations", "文字組", """
<h1 style="font-size:1.6rem;margin:0 0 .5rem;">サイト名の見出し 1.6rem/700</h1>
<p style="font-size:1.05rem;margin:0 0 1.5rem;">リード文 1.05rem。本文はゆったり、行間 1.9〜2.5。</p>
<p>本文 17px。システムフォント（Segoe UI / Hiragino / Noto Sans JP）。<a href="#">リンクは深いレンガ色</a>で、
<mark>重要な一文には黄色いマーカー</mark>を引く。<mark class="warn">やると事故ることは赤</mark>。</p>
<p><code>コードは等幅・淡い紙色の座布団</code>つき。</p>
""")

# --- components ---

FILES["components/header.html"] = page("Components", "ヘッダ", """
<header class="site-header" style="max-width:none;">
  <a class="site-name" href="#">AIの使い方</a>
  <nav class="site-nav">
    <a href="#">レシピ</a><a href="#">ツール</a><a href="#">AIアップデート</a>
  </nav>
</header>
""", max_width="52rem")

FILES["components/hero.html"] = page("Components", "ヒーロー", f"""
<section class="hero">
  <img class="hero-photo" src="{HERO_PHOTO_DATA_URI}" alt="">
  <div class="hero-text">
    <p class="hero-eyebrow">プログラミングなしで、AIに頼む</p>
    <h1>AIの使い方</h1>
    <p class="hero-lead">プログラミングなしで、AIに頼んで自動化を作る方法。使った指示文をそのまま載せ、なぜその言い方が効くのかまで書いています。</p>
    <p class="hero-links">
      <a class="hero-link is-primary" href="#">レシピを読む</a>
      <a class="hero-link" href="#">AIアップデート</a>
    </p>
  </div>
</section>
""", max_width="52rem")

FILES["components/article-card.html"] = page("Components", "記事カード", f"""
<article class="card">
  <span class="card-thumb">{eyecatch("something-feels-off")}</span>
  <div class="card-body">
    <h2 class="card-title"><a href="#">AIと作業していて「なんか違う」と思ったときの対処</a></h2>
    <p class="card-description">違和感を言葉にできないまま作業が進んでしまう、を止める方法。</p>
    <p class="card-meta"><time>2026年8月6日</time><span class="card-badge">5分</span><span class="card-badge">無料</span></p>
  </div>
</article>
<article class="card">
  <span class="card-thumb">{eyecatch("catch-broken-figures")}</span>
  <div class="card-body">
    <h2 class="card-title"><a href="#">AIに図を作らせると崩れる、を検査で止める</a></h2>
    <p class="card-description">目視では見落とす図の崩れを、公開前に機械で検査させる頼み方。</p>
    <p class="card-meta"><time>2026年8月6日</time><span class="card-badge">30分</span><span class="card-badge">無料</span></p>
  </div>
</article>
<style>.card-thumb svg{{width:100%;height:100%;object-fit:cover;}}
.card-thumb{{display:block;flex:none;width:84px;height:84px;border-radius:8px;overflow:hidden;border:1px solid var(--line);}}</style>
""")

FILES["components/news-item.html"] = page("Components", "AIアップデート欄", """
<section class="news-section">
  <h2 class="section-title">AIアップデート</h2>
  <p class="section-lead">各社の発表を自動で集めています。1日数回、自動更新。要約は自動生成です。</p>
  <ul class="news-list">
    <li class="news-item">
      <p class="news-head"><time>2026年8月3日</time>
        <span class="news-vendor"><span class="vdot" style="background:#E8442E;">S</span>Sakana AI</span>
        <span class="news-major">重要</span></p>
      <p class="news-title"><a href="#">Sakana AI、日本語特化のLLM API「Sakana Namazu」を提供開始</a></p>
      <p class="news-summary">Sakana AIが日本語特化のAIモデルを提供開始。
「Sakana Namazu」という名前の
外部サービス連携の仕組みです。</p>
    </li>
    <li class="news-item">
      <p class="news-head"><time>2026年8月4日</time>
        <span class="news-vendor"><span class="vdot" style="background:#10A37F;">O</span>OpenAI</span></p>
      <p class="news-title"><a href="#">New ways to learn and teach with ChatGPT Work and Codex</a></p>
      <p class="news-summary">ChatGPT WorkとCodexに教育用プラグインが登場。
小中高や大学の教師、学生の学習・教育・研究を支援。</p>
    </li>
  </ul>
  <p class="news-models-head">新モデル・新バージョン</p>
  <ul class="news-models"><li>Claude Code: 3件（最新: v2.1.223）</li><li>Qwen 新モデル: 1件（最新: qwen/qwen3.8-max）</li></ul>
  <p class="news-more"><a href="#">すべて見る →</a></p>
</section>
""")

FILES["components/h2-bands.html"] = page("Components", "見出し帯（5ブロック）", """
<div class="article-body">
<h2 class="what">これで何ができるか</h2>
<h2 class="need">前提</h2>
<h2 class="ask">AIへの頼み方</h2>
<h2 class="fix">うまくいかないときの言い直し方</h2>
<h2 class="next">応用・次の一手</h2>
<h3>h3 は章の中の手順</h3>
<h3 class="trouble">困りごとの見出しは赤い縦線</h3>
</div>
""")

FILES["components/prompt-box.html"] = page("Components", "指示文ボックス", """
<div class="article-body">
<div class="prompt-box">
  <div class="prompt-head"><span class="prompt-label">AIへの指示文</span>
  <button class="prompt-copy" type="button">コピーする</button></div>
  <div class="prompt">いったん手を止めてください。

いま何をどこまで作ったか、3行で教えてください。続きを進めるかは、それを読んでから判断します。</div>
</div>
<p>このサイトで一番コピーされる部品。JSが無い環境では枠とヘッダなしの素の指示文が出る。</p>
</div>
""")

FILES["components/markers.html"] = page("Components", "マーカー", """
<div class="article-body">
<p>読み飛ばす人が<mark>マーカー部分だけ拾えば筋が通る</mark>ように引く。1記事13個まで。</p>
<p><mark class="warn">やると事故ることだけ赤</mark>。上限5個。多用すると効かなくなる。</p>
</div>
""")

FILES["components/figure.html"] = page("Components", "図の枠", f"""
<div class="article-body">
<figure class="figure"><span style="display:block;min-width:600px;">{FIGURE_SVG}</span>
<figcaption>図はSVGで、座標は計算で出す。ライト/ダーク両対応を図の中に内蔵。</figcaption></figure>
</div>
""", max_width="52rem")

# --- brand ---

FILES["brand/hero-illustration.html"] = page("Brand", "ヒーローイラスト", f"""
<div style="max-width:420px;margin:0 auto;">{HERO_SVG}</div>
<p style="text-align:center;color:var(--muted);font-size:.85rem;">机の道具＋小ロボットの相棒。手描き風・太い輪郭線。</p>
""", max_width="52rem")

FILES["brand/eyecatch-set.html"] = page("Brand", "アイキャッチ（自動生成）", f"""
<div style="display:grid;gap:12px;">
  <div>{eyecatch("follow-site-without-rss")}</div>
  <div>{eyecatch("claude-opus-5")}</div>
  <div>{eyecatch("stop-filler-sentences")}</div>
</div>
<p style="color:var(--muted);font-size:.85rem;">記事slugをシードに部品ライブラリから決定的に生成。レシピ=ノート系、ツール=歯車・ロボット系。</p>
<style>svg{{width:100%;height:auto;}}</style>
""", max_width="52rem")

if __name__ == "__main__":
    for path, text in FILES.items():
        target = OUT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(FILES)} files -> {OUT}")
