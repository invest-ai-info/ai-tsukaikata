# -*- coding: utf-8 -*-
"""記事の図を、座標を計算して生成する。

目分量で SVG を書くと必ず破綻する（文字を線が貫く・枠からはみ出す）ので、
位置は全部ここで計算する。出力は `python -m src.build` の figures 検査を通る。

使い方: python tools/make_figures.py
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "images"
WIDTH = 720

STYLE = """  .bg { fill: #fbfcfd; }
  .box { fill: #ffffff; stroke: #d5dae0; stroke-width: 1.5; }
  .box-accent { fill: #eaf1fc; stroke: #1a56b8; stroke-width: 1.5; }
  .box-quiet { fill: #f2f4f6; stroke: #d5dae0; stroke-width: 1.5; }
  .box-bad { fill: #fdf0ef; stroke: #d92b2b; stroke-width: 1.5; }
  .box-good { fill: #eef7f0; stroke: #1a7f37; stroke-width: 1.5; }
  .line { stroke: #8b949e; stroke-width: 1.6; fill: none; }
  .t-bad { fill: #b02020; font-size: 12.5px; font-weight: 700; }
  .t-good { fill: #16682e; font-size: 12.5px; }
  .mono { fill: #1f2328; font-size: 12.5px; font-family: Consolas, "SFMono-Regular", Menlo, monospace; }
  .t { fill: #1f2328; font-size: 13px; }
  .t-sm { fill: #616b76; font-size: 11.5px; }
  .t-xs { fill: #8b949e; font-size: 10.5px; }
  .t-strong { fill: #1f2328; font-size: 13.5px; font-weight: 700; }
  .t-accent { fill: #1a56b8; font-size: 13px; font-weight: 700; }
  .bar-in { fill: #7aa7e0; }
  .bar-out { fill: #1a56b8; }
  .bar-old { fill: #c8d1da; }
  .bar-new { fill: #1a56b8; }
  @media (prefers-color-scheme: dark) {
    .bg { fill: #191d21; }
    .box { fill: #14171a; stroke: #363c43; }
    .box-accent { fill: #1b2735; stroke: #7ab0ff; }
    .box-quiet { fill: #1c2126; stroke: #363c43; }
    .box-bad { fill: #2a1a1a; stroke: #f07a7a; }
    .box-good { fill: #16261b; stroke: #57ab68; }
    .line { stroke: #6e7781; }
    .t-bad { fill: #f07a7a; }
    .t-good { fill: #57ab68; }
    .mono { fill: #e6e9ec; }
    .t { fill: #e6e9ec; }
    .t-sm { fill: #9aa4ae; }
    .t-xs { fill: #6e7781; }
    .t-strong { fill: #e6e9ec; }
    .t-accent { fill: #7ab0ff; }
    .bar-in { fill: #4a72a8; }
    .bar-out { fill: #7ab0ff; }
    .bar-old { fill: #3a4149; }
    .bar-new { fill: #7ab0ff; }
  }"""


def _svg(height: int, alt: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{alt}">\n'
        f"<style>\n{STYLE}\n</style>\n"
        f'<rect class="bg" x="0" y="0" width="{WIDTH}" height="{height}"/>\n'
        f"{body}</svg>\n"
    )


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def price_chart() -> None:
    """単価の横棒グラフ。入力と出力を2本並べる。"""
    rows = [
        ("Claude Opus 5", 5, 25, True),
        ("Claude Fable 5", 10, 50, True),
        ("GPT-5.6-sol", 5, 30, False),
        ("GPT-5.6-terra", 2, 12, False),
        ("Gemini 3.1 Pro", 2, 12, False),
    ]
    label_w, left, right = 150, 168, 636
    span = right - left
    top, bar_h, bar_gap, group_gap = 62, 15, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    biggest = max(max(a, b) for _, a, b, _ in rows)
    scale = span / biggest

    parts = [
        f'<text class="t-strong" x="18" y="26">1トークンあたりの単価（100万トークンあたり・ドル）</text>\n',
        f'<text class="t-sm" x="18" y="45">入力＝薄い色 ／ 出力＝濃い色。GPTとGeminiは短い入力のときの値段。</text>\n',
    ]
    for index, (name, price_in, price_out, _highlight) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls) in enumerate(((price_in, "bar-in"), (price_out, "bar-out"))):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"${value}</text>\n"
            )
        parts.append(f'<text class="t-xs" x="{label_w - 40}" y="{y + 12}">入力</text>\n')
        parts.append(
            f'<text class="t-xs" x="{label_w - 40}" y="{y + bar_h + bar_gap + 12}">出力</text>\n'
        )

    height = top + len(rows) * group_h + 34
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 単価が安い＝支払いが安い、ではありません。会社ごとにトークンの数え方が違います。</text>\n"
    )
    alt = (
        "5つのモデルの単価を比べた横棒グラフ。100万トークンあたりのドル。"
        "Claude Opus 5 は入力5ドル・出力25ドル、Claude Fable 5 は入力10ドル・出力50ドル、"
        "GPT-5.6-sol は入力5ドル・出力30ドル、GPT-5.6-terra は入力2ドル・出力12ドル、"
        "Gemini 3.1 Pro は入力2ドル・出力12ドル。"
        "ただし会社ごとにトークンの数え方が違うため、単価の安さは支払額の安さを意味しません。"
    )
    (OUT / "opus5-price-comparison.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def changed_chart() -> None:
    """Opus 4.8 から Opus 5 で、変わらなかったもの／変わったもの。"""
    same = ["入力 $5 → $5", "出力 $25 → $25", "読める量 100万トークン", "書ける量 12.8万トークン"]
    diff = ["学習データ 2026年1月 → 5月", "既定で「考えてから答える」", "返事が4.8より長くなる"]

    col_w, gap, pad = 330, 24, 18
    left_x, right_x = pad, pad + col_w + gap
    # head_y は「枠の上辺（head_y - 22）が副題の文字（〜y=48）を貫かない」ように取る。
    # 62 にしていたら上辺 y=40 が副題を横切ってビルドが止まった。
    head_y, first_y, row_h = 84, 114, 34
    rows = max(len(same), len(diff))
    box_h = 30 + rows * row_h
    height = first_y + rows * row_h + 40

    parts = [
        '<text class="t-strong" x="18" y="26">Opus 4.8 から Opus 5 で何が変わったか</text>\n',
        '<text class="t-sm" x="18" y="45">値段と容量は据え置き。変わったのは知識の新しさと、既定の動き方。</text>\n',
        f'<rect class="box-quiet" x="{left_x}" y="{head_y - 22}" '
        f'width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<rect class="box-accent" x="{right_x}" y="{head_y - 22}" '
        f'width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-strong" x="{left_x + 14}" y="{head_y - 2}">変わらないもの</text>\n',
        f'<text class="t-accent" x="{right_x + 14}" y="{head_y - 2}">変わったもの</text>\n',
    ]
    for index, text in enumerate(same):
        parts.append(
            f'<text class="t" x="{left_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    for index, text in enumerate(diff):
        parts.append(
            f'<text class="t" x="{right_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※「考えてから答える」ぶんも出力として数えられます。上限を低いままにすると途中で切れます。</text>\n"
    )
    alt = (
        "Opus 4.8 から Opus 5 への変化を2列で比べた図。"
        "変わらないもの＝入力5ドル、出力25ドル、読める量100万トークン、書ける量12.8万トークン。"
        "変わったもの＝学習データの締め切りが2026年1月から5月へ、既定で考えてから答えるようになった、"
        "返事が4.8より長くなる。"
    )
    (OUT / "opus5-what-changed.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def tokenizer_chart() -> None:
    """同じ文章でもトークン数が違う、を見せる。"""
    left, right = 210, 640
    span = right - left
    scale = span / 130.0
    top, bar_h, gap = 74, 30, 26

    parts = [
        '<text class="t-strong" x="18" y="26">同じ文章でも、数えたトークンの量が違います</text>\n',
        '<text class="t-sm" x="18" y="45">公式は、Claude 4.7 以降は新しい数え方で約30%多くなると説明しています。</text>\n',
    ]
    for index, (label, value, cls) in enumerate(
        (("Sonnet 4.6 まで", 100, "bar-old"), ("Opus 5（4.7以降）", 130, "bar-new"))
    ):
        y = top + index * (bar_h + gap)
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 9}">{_esc(label)}</text>\n')
        bw = value * scale
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{y + bar_h - 9}">'
            f"{value}（相対）</text>\n"
        )

    height = top + 2 * (bar_h + gap) + 46
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 26}">'
        "※ 同じ原稿でも、請求されるトークン数が約1.3倍になります。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ だから単価表を横に並べても、どちらが安いかは決められません。</text>\n"
    )
    alt = (
        "トークンの数え方の違いを示した横棒グラフ。Sonnet 4.6 までの数え方を100とすると、"
        "Claude 4.7 以降の新しい数え方では同じ文章が約130になる。"
        "つまり同じ原稿でも請求されるトークン数が約1.3倍になるため、"
        "単価表を並べただけでは安さを比較できない。"
    )
    (OUT / "opus5-tokenizer.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def filler_before_after() -> None:
    """埋め草が入った要約の割合。指示を直す前と後。"""
    left, right = 250, 600
    span = right - left
    top, bar_h, gap = 82, 34, 34
    rows = [
        ("行数を固定していたとき", 59, 59, "bar-old"),
        ("固定をやめたあと", 0, 120, "bar-new"),
    ]

    parts = [
        '<text class="t-strong" x="18" y="26">「当たり障りのない一文」が入っていた要約の割合</text>\n',
        '<text class="t-sm" x="18" y="45">「〜に影響します」「注目されています」のような、誰にでも当てはまる行のこと。</text>\n',
        '<text class="t-sm" x="18" y="64">同じ相手・同じ材料で、指示文だけを変えて数えました。</text>\n',
    ]
    for index, (label, hit, total, cls) in enumerate(rows):
        y = top + index * (bar_h + gap)
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 11}">{_esc(label)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{left}" y="{y}" '
            f'width="{span}" height="{bar_h}" rx="3"/>\n'
        )
        ratio = hit / total
        if hit:
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{y}" '
                f'width="{span * ratio:.1f}" height="{bar_h}" rx="3"/>\n'
            )
        parts.append(
            f'<text class="t-strong" x="{right + 12}" y="{y + bar_h - 11}">'
            f"{hit} / {total}件</text>\n"
        )

    height = top + 2 * (bar_h + gap) + 22
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 直したのはAIではなく、こちらの指示文です。行数の指定をやめただけで消えました。</text>\n"
    )
    alt = (
        "指示文を直す前と後で、当たり障りのない一文が入っていた要約の割合を比べた図。"
        "行数を3行に固定していたときは59件中59件すべてに入っていたが、"
        "行数の固定をやめたあとは120件中0件になった。"
    )
    (OUT / "filler-before-after.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def line_count_chart() -> None:
    """行数の分布。固定をやめると、書ける量に応じて短くなる。"""
    left, right = 210, 600
    span = right - left
    top, bar_h, gap = 78, 30, 22
    rows = [("1行で済んだ", 10), ("2行", 43), ("3行", 67)]
    biggest = max(v for _, v in rows)

    parts = [
        '<text class="t-strong" x="18" y="26">固定をやめたあとの、要約の行数（120件）</text>\n',
        '<text class="t-sm" x="18" y="45">書くことが少ない記事は、短く終わるようになりました。</text>\n',
        '<text class="t-sm" x="18" y="64">前は全件が3行でした。足りない行は埋め草で埋まっていました。</text>\n',
    ]
    for index, (label, value) in enumerate(rows):
        y = top + index * (bar_h + gap)
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 9}">{_esc(label)}</text>\n')
        bw = span * value / biggest
        parts.append(
            f'<rect class="bar-new" x="{left}" y="{y}" '
            f'width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + bw + 10:.1f}" y="{y + bar_h - 9}">{value}件</text>\n'
        )

    height = top + 3 * (bar_h + gap) + 18
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ 短いほうが手抜きとは限りません。元の記事に書いてあることが少ないだけです。</text>\n"
    )
    alt = (
        "行数の固定をやめたあとの要約120件の行数分布を示した横棒グラフ。"
        "1行で済んだものが10件、2行が43件、3行が67件。"
        "以前は全件が3行で、足りない行は当たり障りのない文で埋まっていた。"
    )
    (OUT / "summary-line-counts.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def summary_vs_raw_chart() -> None:
    """要約された確認結果と、生ページの実物を並べる。"""
    top = 96
    row = "gpt-5.5-pro   $30.00   -   -   $180.00   $60.00   -   -   $270.00"
    parts = [
        '<text class="t-strong" x="18" y="26">「確認しました」の中身が、作られていることがあります</text>\n',
        '<text class="t-sm" x="18" y="45">料金表の1行を確かめようとして、AIに要約させた結果と、生ページの実物です。</text>\n',
        '<text class="t-sm" x="18" y="64">要約のほうを信じて、正しく書かれていた数字を消してしまいました。</text>\n',
        f'<rect class="box-good" x="22" y="{top}" width="676" height="86" rx="6"/>\n',
        f'<text class="t-good" x="38" y="{top + 26}">生ページに実際にあった行</text>\n',
        f'<text class="mono" x="38" y="{top + 52}">{_esc(row)}</text>\n',
        f'<text class="t-xs" x="38" y="{top + 74}">'
        "見出しは「Short context（短い入力）／ Long context（長い入力）」の8列。長い入力の行は在る。</text>\n",
        f'<rect class="box-bad" x="22" y="{top + 104}" width="676" height="86" rx="6"/>\n',
        f'<text class="t-bad" x="38" y="{top + 130}">AIが返してきた「確認結果」</text>\n',
        f'<text class="t" x="38" y="{top + 156}">'
        "「長い入力の行はありません。272Kトークン未満という但し書きだけです」</text>\n",
        f'<text class="t-xs" x="38" y="{top + 178}">'
        "→ 行は在る。そして 272K という文字列は、このページに1度も出てこない。</text>\n",
    ]
    height = top + 190 + 40
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 確認をAIに要約させると、確認そのものが作り話になります。生の行を見てください。</text>\n"
    )
    alt = (
        "要約された確認結果と生ページを比べた図。"
        "生ページには gpt-5.5-pro の行が実際にあり、短い入力が30ドルと180ドル、"
        "長い入力が60ドルと270ドルと書かれていた。見出しは Short context と Long context の8列。"
        "ところがAIが返してきた確認結果は「長い入力の行はありません。272Kトークン未満という"
        "但し書きだけです」というもので、行は実在し、272Kという文字列はページに1度も出てこない。"
        "確認をAIに要約させると、確認そのものが作り話になる。"
    )
    (OUT / "summary-vs-raw.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def citation_chain_chart() -> None:
    """出典が付いていると、最後の確認が飛ばされる。"""
    box_w, box_h, gap = 200, 92, 34
    top = 92
    steps = [
        ("出典URLが付いている", "見ればすぐ分かる", True),
        ("そのページが開ける", "押せば分かる", True),
        ("その数字がページに\n書いてある", "ここだけ誰も見ない", False),
    ]
    parts = [
        '<text class="t-strong" x="18" y="26">出典が付いているほど、確認されなくなります</text>\n',
        '<text class="t-sm" x="18" y="45">3つ目だけ、ページを開いて文字を探さないと確かめられません。</text>\n',
        '<text class="t-sm" x="18" y="64">手間がかかるので飛ばされます。そこが抜け道になります。</text>\n',
    ]
    for index, (title, note, ok) in enumerate(steps):
        x = 22 + index * (box_w + gap)
        cls = "box" if ok else "box-bad"
        parts.append(
            f'<rect class="{cls}" x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        for line_index, line in enumerate(title.split("\n")):
            parts.append(
                f'<text class="t-strong" x="{x + 14}" y="{top + 30 + line_index * 20}">'
                f"{_esc(line)}</text>\n"
            )
        parts.append(
            f'<text class="{"t-good" if ok else "t-bad"}" x="{x + 14}" y="{top + box_h - 16}">'
            f"{_esc(note)}</text>\n"
        )
        if index < len(steps) - 1:
            ax = x + box_w + 8
            parts.append(
                f'<path class="line" d="M{ax} {top + box_h / 2} '
                f'L{ax + gap - 16} {top + box_h / 2}"/>\n'
            )

    height = top + box_h + 46
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ だから「その数字が書いてある部分を、周りの文ごと引用して」と頼みます。</text>\n"
    )
    alt = (
        "出典の確認が3段階あることを示した図。"
        "1つ目は出典URLが付いているか（見ればすぐ分かる）、"
        "2つ目はそのページが開けるか（押せば分かる）、"
        "3つ目はその数字がページに書いてあるか。"
        "3つ目だけはページを開いて文字を探す必要があるため飛ばされやすく、そこが抜け道になる。"
    )
    (OUT / "citation-chain.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def queue_flow_chart() -> None:
    """1行足す → 定時に起動 → 出典を読む → 下書き → 人が読む → 公開。"""
    steps = [
        ("スマホで1行", "URLを足すだけ", "you"),
        ("定時に起動", "毎朝きまった時刻", "ai"),
        ("出典を読む", "本文を実際に開く", "ai"),
        ("下書きを置く", "公開されない場所へ", "ai"),
        ("人が読む", "ここだけ人間", "you"),
    ]
    box_w, box_h, gap = 124, 96, 20
    top, left = 92, 22
    parts = [
        '<text class="t-strong" x="18" y="26">気になったURLを1行足すと、翌朝には下書きができています</text>\n',
        '<text class="t-sm" x="18" y="45">青がAIの担当。人がやるのは最初の1行と、最後に読むところだけ。</text>\n',
        '<text class="t-sm" x="18" y="64">途中で公開されることはありません。置き場所を分けてあります。</text>\n',
    ]
    for index, (title, note, who) in enumerate(steps):
        x = left + index * (box_w + gap)
        cls = "box-accent" if who == "ai" else "box"
        parts.append(
            f'<rect class="{cls}" x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{"t-accent" if who == "ai" else "t-strong"}" '
            f'x="{x + 12}" y="{top + 32}">{_esc(title)}</text>\n'
        )
        parts.append(f'<text class="t-xs" x="{x + 12}" y="{top + 58}">{_esc(note)}</text>\n')
        parts.append(
            f'<text class="t-xs" x="{x + 12}" y="{top + box_h - 14}">'
            f'{"AI" if who == "ai" else "あなた"}</text>\n'
        )
        if index < len(steps) - 1:
            ax = x + box_w + 4
            parts.append(
                f'<path class="line" d="M{ax} {top + box_h / 2} L{ax + gap - 8} {top + box_h / 2}"/>\n'
            )

    height = top + box_h + 44
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 待ち行列はただのテキストファイルです。専用の管理画面は作りません。</text>\n"
    )
    alt = (
        "待ち行列の流れを示した図。あなたがスマホでURLを1行足す、"
        "AIが毎朝きまった時刻に起動する、AIが出典の本文を実際に開いて読む、"
        "AIが公開されない場所に下書きを置く、最後にあなたが読む、の5段階。"
        "AIが担当するのは真ん中の3つで、人がやるのは最初の1行と最後に読むところだけ。"
        "途中で公開されることはない。"
    )
    (OUT / "queue-flow.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def write_or_stop_chart() -> None:
    """一次情報に届いたかで、書く／書かないを分ける。"""
    top, box_w, box_h = 96, 300, 130
    left_x, right_x = 22, 380
    parts = [
        '<text class="t-strong" x="18" y="26">届かなかったときに、書かずに止まれるかどうか</text>\n',
        '<text class="t-sm" x="18" y="45">今日じっさいに動かした2件は、片方が公開・片方が見送りでした。</text>\n',
        '<text class="t-sm" x="18" y="64">見送れたことのほうが大事です。埋めて書かれるより安全なので。</text>\n',
        f'<rect class="box-good" x="{left_x}" y="{top}" width="{box_w}" height="{box_h}" rx="6"/>\n',
        f'<rect class="box-bad" x="{right_x}" y="{top}" width="{box_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-good" x="{left_x + 16}" y="{top + 30}">一次情報に届いた</text>\n',
        f'<text class="t-bad" x="{right_x + 16}" y="{top + 30}">届かなかった</text>\n',
        f'<text class="t" x="{left_x + 16}" y="{top + 60}">出典を読んで下書きを書く</text>\n',
        f'<text class="t" x="{right_x + 16}" y="{top + 60}">下書きを作らない</text>\n',
        f'<text class="t-sm" x="{left_x + 16}" y="{top + 86}">人が読んでから公開</text>\n',
        f'<text class="t-sm" x="{right_x + 16}" y="{top + 86}">止まった理由を書いて残す</text>\n',
        f'<text class="t-xs" x="{left_x + 16}" y="{top + 112}">例: Claude Opus 5 の比較記事</text>\n',
        f'<text class="t-xs" x="{right_x + 16}" y="{top + 112}">例: Qwen3.8（公式情報が未公開）</text>\n',
    ]
    height = top + box_h + 42
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 二次情報で埋めれば表は完成します。完成した表のほうが危ないので、そうさせません。</text>\n"
    )
    alt = (
        "一次情報に届いたかどうかで動きを分ける図。"
        "届いた場合は出典を読んで下書きを書き、人が読んでから公開する（例：Claude Opus 5 の比較記事）。"
        "届かなかった場合は下書きを作らず、止まった理由を書いて残す（例：Qwen3.8、公式情報が未公開）。"
        "二次情報で埋めれば表は完成するが、完成した表のほうが危ないため、そうさせない。"
    )
    (OUT / "write-or-stop.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini36_lineup() -> None:
    """同時に出た3つのモデルの、用途の違い。値段を並べる前にこれを見せる。"""
    cards = [
        (
            "Gemini 3.6 Flash",
            "主力（ふだん使い）",
            ["コーディングと知識作業", "エージェントの土台", "3.5 Flash の置き換え"],
            "入力 $1.50 ／ 出力 $7.50",
            "一般提供中",
        ),
        (
            "Gemini 3.5 Flash-Lite",
            "速さと量",
            ["低遅延・大量処理向け", "検索や書類の処理", "3.1 Flash-Lite の後継"],
            "入力 $0.30 ／ 出力 $2.50",
            "一般提供中",
        ),
        (
            "Gemini 3.5 Flash Cyber",
            "安全の点検",
            ["脆弱性の検出と修正", "CodeMender と組で提供", "政府と一部の相手のみ"],
            "料金の記載なし",
            "限定パイロット（近日）",
        ),
    ]
    box_w, gap, left, top, box_h = 216, 18, 18, 88, 200

    parts = [
        '<text class="t-strong" x="18" y="26">同じ日に出た3つは、用途が別々です</text>\n',
        '<text class="t-sm" x="18" y="45">値段を並べる前に、まず何のためのモデルかを分けます。</text>\n',
        '<text class="t-sm" x="18" y="64">単価は100万トークンあたりのドル（Standard・有料層）。</text>\n',
    ]
    for index, (name, role, lines, price, status) in enumerate(cards):
        x = left + index * (box_w + gap)
        cls = "box-quiet" if index == 2 else "box-accent"
        parts.append(
            f'<rect class="{cls}" x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t-strong" x="{x + 12}" y="{top + 28}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t-accent" x="{x + 12}" y="{top + 52}">{_esc(role)}</text>\n')
        for line_index, line in enumerate(lines):
            parts.append(
                f'<text class="t-sm" x="{x + 12}" y="{top + 78 + line_index * 18}">'
                f"{_esc(line)}</text>\n"
            )
        parts.append(f'<text class="t-strong" x="{x + 12}" y="{top + 146}">{_esc(price)}</text>\n')
        parts.append(f'<text class="t-xs" x="{x + 12}" y="{top + 172}">{_esc(status)}</text>\n')

    height = top + box_h + 42
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ Cyber だけ料金ページに行がありません。使える相手も限られています。</text>\n"
    )
    alt = (
        "2026年7月21日に同時発表された3つのモデルの用途を並べた図。"
        "Gemini 3.6 Flash は主力で、コーディングと知識作業、エージェントの土台、"
        "3.5 Flash の置き換え。入力100万トークンあたり1.50ドル、出力7.50ドル。一般提供中。"
        "Gemini 3.5 Flash-Lite は速さと量が持ち味で、低遅延・大量処理向け、検索や書類の処理、"
        "3.1 Flash-Lite の後継。入力0.30ドル、出力2.50ドル。一般提供中。"
        "Gemini 3.5 Flash Cyber は安全の点検用で、脆弱性の検出と修正、CodeMender と組で提供、"
        "政府と一部の相手のみ。料金の記載はなく、限定パイロットで近日提供。"
    )
    (OUT / "gemini36-lineup.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini36_cheap_price_chart() -> None:
    """安いモデル4つの単価。入力と出力を2本並べる。"""
    rows = [
        ("Gemini 3.6 Flash", 1.50, 7.50),
        ("Gemini 3.5 Flash-Lite", 0.30, 2.50),
        ("Claude Haiku 4.5", 1.00, 5.00),
        ("GPT-5.6 Luna", 0.20, 1.20),
    ]
    left, right = 210, 630
    span = right - left
    top, bar_h, bar_gap, group_gap = 66, 15, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    biggest = max(max(a, b) for _, a, b in rows)
    scale = span / biggest

    parts = [
        '<text class="t-strong" x="18" y="26">安いモデル4つの単価（100万トークンあたり・ドル）</text>\n',
        '<text class="t-sm" x="18" y="45">入力＝薄い色 ／ 出力＝濃い色。GPT-5.6 Luna は短い入力のときの値段。</text>\n',
    ]
    for index, (name, price_in, price_out) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((price_in, "bar-in", "入力"), (price_out, "bar-out", "出力"))
        ):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(f'<text class="t-xs" x="178" y="{by + bar_h - 4}">{tag}</text>\n')
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"${value:.2f}</text>\n"
            )

    height = top + len(rows) * group_h + 50
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ 単価が安い＝支払いが安い、ではありません。会社ごとにトークンの数え方が違います。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 読める量も違います（Haiku 4.5 は20万トークン、他の3つは100万トークン超）。</text>\n"
    )
    alt = (
        "安いモデル4つの単価を比べた横棒グラフ。100万トークンあたりのドル。"
        "Gemini 3.6 Flash は入力1.50ドル・出力7.50ドル、"
        "Gemini 3.5 Flash-Lite は入力0.30ドル・出力2.50ドル、"
        "Claude Haiku 4.5 は入力1.00ドル・出力5.00ドル、"
        "GPT-5.6 Luna は短い入力のとき入力0.20ドル・出力1.20ドル。"
        "ただし会社ごとにトークンの数え方も読める量も違うため、単価の安さは支払額の安さを意味しません。"
    )
    (OUT / "gemini36-cheap-price.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini36_generation_chart() -> None:
    """世代が上がって、単価が下がったもの／上がったもの。"""
    rows = [
        ("Flash の入力", 1.50, 1.50),
        ("Flash の出力", 9.00, 7.50),
        ("Flash-Lite の入力", 0.25, 0.30),
        ("Flash-Lite の出力", 1.50, 2.50),
    ]
    left, right = 210, 600
    span = right - left
    top, bar_h, bar_gap, group_gap = 82, 14, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    biggest = max(max(a, b) for _, a, b in rows)
    scale = span / biggest

    parts = [
        '<text class="t-strong" x="18" y="26">世代が上がって、下がった単価と上がった単価</text>\n',
        '<text class="t-sm" x="18" y="45">灰色＝前の世代（3.5 Flash / 3.1 Flash-Lite）、青＝新しい世代。</text>\n',
        '<text class="t-sm" x="18" y="64">100万トークンあたりのドル。Flash-Lite の入力はテキストの値。</text>\n',
    ]
    for index, (name, old, new) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((old, "bar-old", "前"), (new, "bar-new", "新"))
        ):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(f'<text class="t-xs" x="180" y="{by + bar_h - 3}">{tag}</text>\n')
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"${value:.2f}</text>\n"
            )

    height = top + len(rows) * group_h + 50
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ Flash は出力が安くなりました。Flash-Lite は入力も出力も高くなっています。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 世代が新しいほど安い、とは限りません。乗り換える前に自分の使い方で計算してください。</text>\n"
    )
    alt = (
        "世代交代で単価がどう動いたかを比べた横棒グラフ。100万トークンあたりのドル。"
        "Flash の入力は 3.5 Flash の1.50ドルから 3.6 Flash も1.50ドルで据え置き。"
        "Flash の出力は9.00ドルから7.50ドルへ下がった。"
        "Flash-Lite の入力（テキスト）は 3.1 Flash-Lite の0.25ドルから 3.5 Flash-Lite の0.30ドルへ上がり、"
        "出力は1.50ドルから2.50ドルへ上がった。"
        "世代が新しいほど安いとは限らない。"
    )
    (OUT / "gemini36-generation.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini36_bench_chart() -> None:
    """3.5 Flash と 3.6 Flash の、公式が挙げた点数（％のものだけ）。"""
    rows = [
        ("DeepSWE", 37.0, 49.0),
        ("MLE Bench", 49.7, 63.9),
        ("OSWorld-Verified", 78.4, 83.0),
    ]
    left, right = 230, 620
    span = right - left
    top, bar_h, bar_gap, group_gap = 82, 14, 5, 22
    group_h = bar_h * 2 + bar_gap + group_gap
    scale = span / 100.0

    parts = [
        '<text class="t-strong" x="18" y="26">公式が挙げた点数（3.5 Flash → 3.6 Flash）</text>\n',
        '<text class="t-sm" x="18" y="45">灰色＝3.5 Flash、青＝3.6 Flash。目盛りは0〜100％で揃えてあります。</text>\n',
        '<text class="t-sm" x="18" y="64">どれも Google が自社で測った値です。他社が同じ条件で測った値ではありません。</text>\n',
    ]
    for index, (name, old, new) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((old, "bar-old", "3.5"), (new, "bar-new", "3.6"))
        ):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(f'<text class="t-xs" x="196" y="{by + bar_h - 3}">{tag}</text>\n')
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"{value:g}%</text>\n"
            )

    height = top + len(rows) * group_h + 50
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ テストの中身も測り方も、この3つで別々です。並べても平均は取れません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 点数が何回試した値なのかは、発表ページに書かれていません。</text>\n"
    )
    alt = (
        "Gemini 3.5 Flash と 3.6 Flash の点数を比べた横棒グラフ。"
        "DeepSWE は37％から49％、MLE Bench は49.7％から63.9％、"
        "OSWorld-Verified は78.4％から83.0％。いずれも Google が自社で測った値で、"
        "テストの中身も測り方も3つで別々のため平均は取れない。"
        "何回試した値なのかは発表ページに書かれていない。"
    )
    (OUT / "gemini36-bench.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def class_scrape_chart() -> None:
    """クラス名で拾う／埋め込みデータで拾う、の対比。"""
    left_rows = [
        ("scss-module__KxYrHG__date", "mono"),
        ("デザイン変更のたびに名前が変わる", "t"),
        ("ある日、静かに0件になる", "t"),
    ]
    right_rows = [
        ('"publishedOn": "2026-08-04"', "mono"),
        ("記事そのもののデータを読む", "t"),
        ("デザインが変わっても残る", "t"),
    ]
    col_w, gap, pad = 330, 24, 18
    left_x, right_x = pad, pad + col_w + gap
    head_y, first_y, row_h = 84, 114, 34
    rows = max(len(left_rows), len(right_rows))
    box_h = 30 + rows * row_h
    height = first_y + rows * row_h + 40

    parts = [
        '<text class="t-strong" x="18" y="26">同じページを追う、2つの拾い方</text>\n',
        '<text class="t-sm" x="18" y="45">見た目の目印（クラス名）は借り物。記事のデータは本体。</text>\n',
        f'<rect class="box-bad" x="{left_x}" y="{head_y - 22}" width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<rect class="box-good" x="{right_x}" y="{head_y - 22}" width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-bad" x="{left_x + 14}" y="{head_y - 2}">クラス名で拾う</text>\n',
        f'<text class="t-good" x="{right_x + 14}" y="{head_y - 2}">埋め込みデータで拾う</text>\n',
    ]
    for index, (text, cls) in enumerate(left_rows):
        parts.append(
            f'<text class="{cls}" x="{left_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    for index, (text, cls) in enumerate(right_rows):
        parts.append(
            f'<text class="{cls}" x="{right_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ クラス名の例は実際のサイトで観測したもの。ハッシュ部分がビルドのたびに変わります。</text>\n"
    )
    alt = (
        "RSSが無いサイトの2つの拾い方を比べた図。"
        "左（クラス名で拾う）は、scss-module__KxYrHG__date のようなハッシュ付きクラス名を目印にするため、"
        "デザイン変更のたびに名前が変わり、ある日静かに0件になる。"
        "右（埋め込みデータで拾う）は、publishedOn: 2026-08-04 のような記事そのもののデータを読むため、"
        "デザインが変わっても残る。"
    )
    (OUT / "rss-class-vs-data.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def silent_zero_chart() -> None:
    """0件のとき空リストで済ませる設計と、例外で止める設計の対比。"""
    lanes = [
        ("bad", "空のまま成功扱いにする設計", "t-bad",
         ["クラス名が変わる", "取得 0件・エラー無し", "翌週も 0件", "数週間 気づけない"]),
        ("good", "1件も無ければ止める設計", "t-good",
         ["クラス名が変わる", "その場でエラーになる", "3回続くと警告扱い", "翌朝のメールで気づく"]),
    ]
    box_w, box_h, gap_x = 152, 46, 22
    left = 18
    height = 292

    parts = [
        '<text class="t-strong" x="18" y="26">「0件」をどう扱うかで、壊れたことに気づけるかが決まる</text>\n',
        '<text class="t-sm" x="18" y="45">どちらもクラス名の変更で取れなくなった、同じ事故から始まります。</text>\n',
    ]
    for lane_index, (kind, label, label_cls, steps) in enumerate(lanes):
        label_y = 84 + lane_index * 104
        box_y = label_y + 12
        parts.append(f'<text class="{label_cls}" x="18" y="{label_y}">{_esc(label)}</text>\n')
        for step_index, text in enumerate(steps):
            x = left + step_index * (box_w + gap_x)
            box_cls = "box-quiet" if step_index == 0 else f"box-{kind}"
            parts.append(
                f'<rect class="{box_cls}" x="{x}" y="{box_y}" '
                f'width="{box_w}" height="{box_h}" rx="6"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{x + 10}" y="{box_y + 28}">{_esc(text)}</text>\n'
            )
            if step_index < len(steps) - 1:
                ax = x + box_w
                ay = box_y + box_h / 2
                parts.append(
                    f'<line class="line" x1="{ax + 3}" y1="{ay}" x2="{ax + gap_x - 8}" y2="{ay}"/>\n'
                )
                parts.append(
                    f'<path d="M{ax + gap_x - 8} {ay - 4} L{ax + gap_x - 1} {ay} '
                    f'L{ax + gap_x - 8} {ay + 4} Z" fill="#8b949e"/>\n'
                )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※「取得できたが0件」と「取得の仕組みが壊れた」は、外から見ると同じ0件です。</text>\n"
    )
    alt = (
        "取得0件の扱い方2通りを時系列で比べた図。どちらもクラス名の変更から始まる。"
        "上（空のまま成功扱いにする設計）＝取得0件でもエラーが出ず、翌週も0件のまま、数週間気づけない。"
        "下（1件も無ければ止める設計）＝その場でエラーになり、3回続くと警告扱いになって、翌朝のメールで気づく。"
    )
    (OUT / "silent-zero.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def figure_checks_chart() -> None:
    """図の崩れを止める2段構えの検査と、それぞれが捕まえた実例。"""
    stages = [
        ("box-quiet", "図を生成する", "座標は目分量ではなく計算で出す", ""),
        ("box-accent", "① 座標の検査（公開のたび・自動）", "文字を線が貫く／枠や画面からはみ出す、を機械で見る",
         "実例: 副題を枠の上辺が貫いた → 公開前に停止"),
        ("box-accent", "② ブラウザで実寸を計測（図を触った日に1回）", "①が見逃す数ピクセルのはみ出しまで拾う",
         "実例: 3px と 22px のはみ出しを検出"),
        ("box-good", "公開", "", ""),
    ]
    box_x, box_w, box_h, gap_y = 18, 430, 52, 26
    top = 66
    height = top + len(stages) * (box_h + gap_y) - gap_y + 40

    parts = [
        '<text class="t-strong" x="18" y="26">図の崩れは2段構えで止める</text>\n',
        '<text class="t-sm" x="18" y="45">目視は最後の手段。先に機械に見せます。</text>\n',
    ]
    for index, (cls, title, sub, example) in enumerate(stages):
        y = top + index * (box_h + gap_y)
        parts.append(
            f'<rect class="{cls}" x="{box_x}" y="{y}" width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        title_y = y + (32 if sub else 32)
        parts.append(f'<text class="t" x="{box_x + 14}" y="{y + 21}">{_esc(title)}</text>\n')
        if sub:
            parts.append(f'<text class="t-sm" x="{box_x + 14}" y="{y + 40}">{_esc(sub)}</text>\n')
        if example:
            parts.append(
                f'<text class="t-sm" x="{box_x + box_w + 16}" y="{y + 31}">{_esc(example)}</text>\n'
            )
        if index < len(stages) - 1:
            ax = box_x + 60
            ay = y + box_h
            parts.append(
                f'<line class="line" x1="{ax}" y1="{ay + 3}" x2="{ax}" y2="{ay + gap_y - 8}"/>\n'
            )
            parts.append(
                f'<path d="M{ax - 4} {ay + gap_y - 8} L{ax} {ay + gap_y - 1} '
                f'L{ax + 4} {ay + gap_y - 8} Z" fill="#8b949e"/>\n'
            )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 崩れていたら公開そのものが止まります。「直った記事だけ古いまま公開」を作らないため。</text>\n"
    )
    alt = (
        "図の崩れを止める流れ。図を生成したら、①公開のたびに自動で座標を検査"
        "（文字を線が貫く・枠や画面からのはみ出し。実例として副題を枠の上辺が貫いたのを公開前に停止）、"
        "②図を触った日にはブラウザで実寸を計測（実例として3pxと22pxのはみ出しを検出）、"
        "その両方を通ってから公開する。"
    )
    (OUT / "figure-checks.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def check_blindspot_chart() -> None:
    """座標の検査が見ていないもの（色）と、その塞ぎ方。"""
    left_rows = ["文字と線の位置", "枠からのはみ出し", "画面からのはみ出し"]
    right_rows = ["色は見ていない", "定義漏れのclassは真っ黒になる", "真っ黒でも位置は正しい → 通る"]
    col_w, gap, pad = 330, 24, 18
    left_x, right_x = pad, pad + col_w + gap
    head_y, first_y, row_h = 84, 114, 34
    rows = max(len(left_rows), len(right_rows))
    box_h = 30 + rows * row_h
    bar_y = first_y + rows * row_h + 18
    height = bar_y + 64 + 36

    parts = [
        '<text class="t-strong" x="18" y="26">検査には死角がある。何を見ていないかを知っておく</text>\n',
        '<text class="t-sm" x="18" y="45">座標の検査は位置しか見ません。色の事故は素通りします。</text>\n',
        f'<rect class="box-good" x="{left_x}" y="{head_y - 22}" width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<rect class="box-bad" x="{right_x}" y="{head_y - 22}" width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-good" x="{left_x + 14}" y="{head_y - 2}">座標の検査が見ているもの</text>\n',
        f'<text class="t-bad" x="{right_x + 14}" y="{head_y - 2}">見ていないもの</text>\n',
    ]
    for index, text in enumerate(left_rows):
        parts.append(
            f'<text class="t" x="{left_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    for index, text in enumerate(right_rows):
        parts.append(
            f'<text class="t" x="{right_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    parts.append(
        f'<rect class="box-accent" x="{pad}" y="{bar_y}" width="{col_w * 2 + gap}" height="64" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t-accent" x="{pad + 14}" y="{bar_y + 25}">死角は、別の小さな検査で塞ぐ</text>\n'
    )
    parts.append(
        f'<text class="t" x="{pad + 14}" y="{bar_y + 48}">'
        f'{_esc("使っているclassが<style>に定義されているか、公開のたびに機械で照合する")}</text>\n'
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 実際にこの死角で、真っ黒に塗り潰された図が検査を通り抜けました。</text>\n"
    )
    alt = (
        "座標の検査の死角を説明する図。見ているもの＝文字と線の位置、枠からのはみ出し、画面からのはみ出し。"
        "見ていないもの＝色。定義漏れのclassは真っ黒になるが、位置は正しいので検査を通る。"
        "塞ぎ方＝使っているclassがstyleに定義されているかを、公開のたびに機械で照合する。"
    )
    (OUT / "check-blindspot.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def feels_off_chart() -> None:
    """「なんか違う」の3つの正体と、それぞれにかける一言。"""
    rows = [
        ("結果が違う", "期待していたのは◯◯、出てきたのは△△"),
        ("進め方が違う", "いったん止めて、途中で1回見せて"),
        ("目的からズレた", "最初の依頼を引用して。対応してる？"),
    ]
    label_w, box_h, gap_y = 236, 56, 24
    left_x = 18
    right_x = left_x + label_w + 66
    right_w = WIDTH - right_x - 18
    top = 84
    height = top + len(rows) * (box_h + gap_y) - gap_y + 40

    parts = [
        '<text class="t-strong" x="18" y="26">「なんか違う」には正体が3つある</text>\n',
        '<text class="t-sm" x="18" y="45">どれかが分かれば、かける一言が決まる。分からなければ、それをAIに聞く。</text>\n',
    ]
    for index, (label, phrase) in enumerate(rows):
        y = top + index * (box_h + gap_y)
        mid = y + box_h / 2
        parts.append(
            f'<rect class="box-quiet" x="{left_x}" y="{y}" width="{label_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-strong" x="{left_x + 14}" y="{mid + 5:.0f}">{_esc(label)}</text>\n'
        )
        ax = left_x + label_w
        parts.append(
            f'<line class="line" x1="{ax + 6}" y1="{mid:.0f}" x2="{right_x - 14}" y2="{mid:.0f}"/>\n'
        )
        parts.append(
            f'<path d="M{right_x - 14} {mid - 4:.0f} L{right_x - 7} {mid:.0f} '
            f'L{right_x - 14} {mid + 4:.0f} Z" fill="#8b949e"/>\n'
        )
        parts.append(
            f'<rect class="box-accent" x="{right_x}" y="{y}" width="{right_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t" x="{right_x + 14}" y="{mid + 5:.0f}">{_esc(phrase)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 違和感は誤報ではなく、いちばん早い警報。言葉になる前に止まってよい。</text>\n"
    )
    alt = (
        "「なんか違う」の3つの正体と、それぞれにかける一言を並べた図。"
        "結果が違う→「期待していたのは◯◯、出てきたのは△△」。"
        "進め方が違う→「いったん止めて、途中で1回見せて」。"
        "目的からズレた→「最初の依頼を引用して。対応してる？」。"
        "どれか分からなければ、それ自体をAIに聞く。"
    )
    (OUT / "feels-off-map.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def delegate_types_chart() -> None:
    """AIに渡せる作業の4つの型と、見分けるための問い。"""
    rows = [
        ("繰り返し", "毎週おなじ手順でやっている", "曜日や締切で思い出す作業はここ"),
        ("転記", "AからBへ写している", "コピペが5回以上出てきたらここ"),
        ("下書き", "ゼロから書き始めている", "白紙を埋める時間が長いならここ"),
        ("チェック", "抜けや誤りを目で探している", "見落としが怖い作業はここ"),
    ]
    box_x, box_w, box_h, gap_y = 18, 200, 62, 18
    mid_x = box_x + box_w + 22
    mid_w = 236
    right_x = mid_x + mid_w + 22
    right_w = WIDTH - right_x - 18
    top = 84
    height = top + len(rows) * (box_h + gap_y) - gap_y + 40

    parts = [
        '<text class="t-strong" x="18" y="26">AIに渡せる作業は、だいたい4つの型に入る</text>\n',
        '<text class="t-sm" x="18" y="45">自分の1週間を思い出して、当てはまるものを探すのが速い。</text>\n',
    ]
    for index, (name, question, hint) in enumerate(rows):
        y = top + index * (box_h + gap_y)
        mid = y + box_h / 2
        parts.append(
            f'<rect class="box-accent" x="{box_x}" y="{y}" width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-accent" x="{box_x + 16}" y="{mid + 5:.0f}">{_esc(name)}</text>\n'
        )
        parts.append(
            f'<rect class="box-quiet" x="{mid_x}" y="{y}" width="{mid_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t" x="{mid_x + 14}" y="{mid + 5:.0f}">{_esc(question)}</text>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{right_x}" y="{mid + 5:.0f}">{_esc(hint)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ どれにも入らない作業は、たいてい判断が主役です。そこは人が持ったままでかまいません。</text>\n"
    )
    alt = (
        "AIに渡せる作業の4つの型を並べた図。"
        "繰り返し＝毎週おなじ手順でやっている（曜日や締切で思い出す作業）。"
        "転記＝AからBへ写している（コピペが5回以上）。"
        "下書き＝ゼロから書き始めている（白紙を埋める時間が長い）。"
        "チェック＝抜けや誤りを目で探している（見落としが怖い作業）。"
        "どれにも入らない作業は判断が主役なので、人が持ったままでよい。"
    )
    (OUT / "delegate-types.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def life_paperwork_chart() -> None:
    """紙・書類まわりで、AIに渡せるところと自分で持つところ。"""
    steps = [
        ("box-good", "写真を撮る", "レシートも通知も\nスマホで1枚"),
        ("box-good", "読み取らせる", "文字にして\n表にまとめさせる"),
        ("box-good", "下書きさせる", "申請文・問い合わせ文\nを型どおりに"),
        ("box-bad", "出す判断は自分", "金額と宛先だけ\n目で確かめる"),
    ]
    box_w, box_h, gap_x = 156, 78, 18
    left, top = 18, 80
    height = top + box_h + 60

    parts = [
        '<text class="t-strong" x="18" y="26">暮らしの書類は「読み取り」と「下書き」まで渡せる</text>\n',
        '<text class="t-sm" x="18" y="45">最後の確認だけ自分に残す。ここを渡すと事故になります。</text>\n',
    ]
    for index, (cls, title, sub) in enumerate(steps):
        x = left + index * (box_w + gap_x)
        parts.append(
            f'<rect class="{cls}" x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        label_cls = "t-good" if cls == "box-good" else "t-bad"
        parts.append(
            f'<text class="{label_cls}" x="{x + 12}" y="{top + 24}">{_esc(title)}</text>\n'
        )
        for line_index, line in enumerate(sub.split("\n")):
            parts.append(
                f'<text class="t-sm" x="{x + 12}" y="{top + 46 + line_index * 17}">'
                f"{_esc(line)}</text>\n"
            )
        if index < len(steps) - 1:
            ax = x + box_w
            ay = top + box_h / 2
            parts.append(
                f'<line class="line" x1="{ax + 3}" y1="{ay}" x2="{ax + gap_x - 8}" y2="{ay}"/>\n'
            )
            parts.append(
                f'<path d="M{ax + gap_x - 8} {ay - 4} L{ax + gap_x - 1} {ay} '
                f'L{ax + gap_x - 8} {ay + 4} Z" fill="#8b949e"/>\n'
            )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 金額・宛先・期限は、AIの読み取り結果をそのまま信じないでください。原本と1回だけ見比べます。</text>\n"
    )
    alt = (
        "暮らしの書類でAIに渡せる工程の図。写真を撮る（レシートも通知もスマホで1枚）、"
        "読み取らせる（文字にして表にまとめさせる）、下書きさせる（申請文や問い合わせ文を型どおりに）"
        "までは渡せる。最後の「出す判断」は自分が持ち、金額と宛先だけ目で確かめる。"
        "金額・宛先・期限はAIの読み取りをそのまま信じず、原本と1回見比べる。"
    )
    (OUT / "life-paperwork.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def fun_iteration_chart() -> None:
    """創作では、1回で完成させず「案を並べさせて選ぶ」を回す。"""
    lanes = [
        ("bad", "1回で完成させようとする", "t-bad",
         ["長い注文を書く", "1案だけ返ってくる", "違う→また長い注文", "だんだん惜しくなる"]),
        ("good", "案を並べさせて選ぶ", "t-good",
         ["短い注文を書く", "5案まとめて返る", "良い所を指して選ぶ", "選んだ案を伸ばす"]),
    ]
    box_w, box_h, gap_x = 152, 46, 22
    left = 18
    height = 292

    parts = [
        '<text class="t-strong" x="18" y="26">創作は「1回で完成」より「並べて選ぶ」が速い</text>\n',
        '<text class="t-sm" x="18" y="45">好みは言葉にしにくいので、見てから選ぶほうが早く着きます。</text>\n',
    ]
    for lane_index, (kind, label, label_cls, steps) in enumerate(lanes):
        label_y = 84 + lane_index * 104
        box_y = label_y + 12
        parts.append(f'<text class="{label_cls}" x="18" y="{label_y}">{_esc(label)}</text>\n')
        for step_index, text in enumerate(steps):
            x = left + step_index * (box_w + gap_x)
            box_cls = "box-quiet" if step_index == 0 else f"box-{kind}"
            parts.append(
                f'<rect class="{box_cls}" x="{x}" y="{box_y}" '
                f'width="{box_w}" height="{box_h}" rx="6"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{x + 10}" y="{box_y + 28}">{_esc(text)}</text>\n'
            )
            if step_index < len(steps) - 1:
                ax = x + box_w
                ay = box_y + box_h / 2
                parts.append(
                    f'<line class="line" x1="{ax + 3}" y1="{ay}" x2="{ax + gap_x - 8}" y2="{ay}"/>\n'
                )
                parts.append(
                    f'<path d="M{ax + gap_x - 8} {ay - 4} L{ax + gap_x - 1} {ay} '
                    f'L{ax + gap_x - 8} {ay + 4} Z" fill="#8b949e"/>\n'
                )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 5案は多すぎず少なすぎない数です。3案だと似たものが並び、10案だと選ぶのが仕事になります。</text>\n"
    )
    alt = (
        "創作でのAIの使い方2通りを比べた図。"
        "上（1回で完成させようとする）＝長い注文を書く、1案だけ返ってくる、違うのでまた長い注文、"
        "だんだん惜しくなる。"
        "下（案を並べさせて選ぶ）＝短い注文を書く、5案まとめて返る、良い所を指して選ぶ、選んだ案を伸ばす。"
    )
    (OUT / "fun-iteration.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def batch_vs_one_chart() -> None:
    """1件ずつ10回 vs 10件まとめて1回。毎回かかる説明の手間を可視化する。"""
    left, right = 150, 660
    span = right - left
    top, bar_h, gap = 78, 34, 30

    # 1回あたり: 説明1.0 + 待ち0.6。10回ぶんと、まとめて1回ぶん
    rows = [
        ("1件ずつ10回", 10.0, 6.0, "bar-old"),
        ("10件まとめて1回", 1.0, 2.0, "bar-new"),
    ]
    biggest = max(a + b for _, a, b, _ in rows)
    scale = span / biggest

    parts = [
        '<text class="t-strong" x="18" y="26">同じ説明を毎回書き直しているぶんが、まるごと消える</text>\n',
        '<text class="t-sm" x="18" y="45">濃い色＝説明を書く時間 ／ 薄い色＝待ち時間。長さは考え方を示す目安です。</text>\n',
    ]
    for index, (label, explain, wait, cls) in enumerate(rows):
        y = top + index * (bar_h + gap)
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 11}">{_esc(label)}</text>\n')
        ew = explain * scale
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" width="{ew:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        ww = wait * scale
        parts.append(
            f'<rect class="bar-in" x="{left + ew:.1f}" y="{y}" '
            f'width="{ww:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + 10}" y="{y + bar_h - 11}">説明</text>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + ew + 10:.1f}" y="{y + bar_h - 11}">待ち</text>\n'
        )

    height = top + len(rows) * (bar_h + gap) + 34
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 待ち時間は減りません。減るのは「毎回おなじ前置きを書き直す」ぶんです。</text>\n"
    )
    alt = (
        "1件ずつ10回頼む場合と、10件まとめて1回頼む場合を比べた横棒グラフ。"
        "1件ずつ10回は、説明を書く時間が10回ぶん積み上がり、待ち時間も10回ぶんかかる。"
        "10件まとめて1回は、説明が1回ぶんで済み、待ち時間も1回にまとまる。"
        "待ち時間そのものは減らず、減るのは毎回同じ前置きを書き直すぶん。"
    )
    (OUT / "batch-vs-one.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def meeting_outputs_chart() -> None:
    """1本の録音から、用途の違う3つの成果物を出させる。"""
    src_x, src_y, src_w, src_h = 18, 96, 168, 62
    out_x = 300
    out_w = WIDTH - out_x - 18
    out_h = 52
    out_gap = 16
    outs = [
        ("決まったこと", "そのまま共有できる形で"),
        ("宿題（誰が・いつまで）", "担当と期限が空欄なら空欄と書かせる"),
        ("持ち帰りの論点", "決まらなかったことを消させない"),
    ]
    top = 84
    height = top + len(outs) * (out_h + out_gap) - out_gap + 46

    parts = [
        '<text class="t-strong" x="18" y="26">録音1本から、用途の違う3つを別々に出させる</text>\n',
        '<text class="t-sm" x="18" y="45">まとめて「議事録にして」と頼むと、宿題が本文に埋もれます。</text>\n',
        f'<rect class="box-quiet" x="{src_x}" y="{src_y}" width="{src_w}" height="{src_h}" rx="6"/>\n',
        f'<text class="t" x="{src_x + 16}" y="{src_y + 26}">会議の録音</text>\n',
        f'<text class="t-sm" x="{src_x + 16}" y="{src_y + 46}">文字起こしでも可</text>\n',
    ]
    for index, (title, note) in enumerate(outs):
        y = top + index * (out_h + out_gap)
        parts.append(
            f'<rect class="box-accent" x="{out_x}" y="{y}" width="{out_w}" height="{out_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-accent" x="{out_x + 14}" y="{y + 22}">{_esc(title)}</text>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{out_x + 14}" y="{y + 40}">{_esc(note)}</text>\n'
        )
        ay = y + out_h / 2
        parts.append(
            f'<line class="line" x1="{src_x + src_w + 8}" y1="{src_y + src_h / 2}" '
            f'x2="{out_x - 14}" y2="{ay}"/>\n'
        )
        parts.append(
            f'<path d="M{out_x - 14} {ay - 4} L{out_x - 7} {ay} '
            f'L{out_x - 14} {ay + 4} Z" fill="#8b949e"/>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 音声を渡す前に、社外秘や個人名が含まれていないかを確認してください。</text>\n"
    )
    alt = (
        "会議の録音1本から3つの成果物を別々に出させる図。"
        "決まったこと（そのまま共有できる形で）、宿題（誰が・いつまで。担当と期限が空欄なら空欄と書かせる）、"
        "持ち帰りの論点（決まらなかったことを消させない）。"
        "まとめて議事録にしてと頼むと宿題が本文に埋もれる。"
    )
    (OUT / "meeting-outputs.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def sourced_research_chart() -> None:
    """出典なしの答えと、出典つきの答えの違い。"""
    left_rows = ["答えだけ返ってくる", "合っていそうに見える", "確かめる方法が無い", "間違いに気づけない"]
    right_rows = ["答えとURLが並ぶ", "URLを開けば確かめられる", "無い情報は「無い」と分かる", "自分の責任で使える"]
    col_w, gap, pad = 330, 24, 18
    left_x, right_x = pad, pad + col_w + gap
    head_y, first_y, row_h = 84, 114, 34
    rows = max(len(left_rows), len(right_rows))
    box_h = 30 + rows * row_h
    height = first_y + rows * row_h + 40

    parts = [
        '<text class="t-strong" x="18" y="26">調べものは「答え」ではなく「答えと出典」で受け取る</text>\n',
        '<text class="t-sm" x="18" y="45">正しさを見抜く力より、確かめられる形で受け取る習慣のほうが効きます。</text>\n',
        f'<rect class="box-bad" x="{left_x}" y="{head_y - 22}" width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<rect class="box-good" x="{right_x}" y="{head_y - 22}" width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-bad" x="{left_x + 14}" y="{head_y - 2}">出典を求めないとき</text>\n',
        f'<text class="t-good" x="{right_x + 14}" y="{head_y - 2}">出典を求めたとき</text>\n',
    ]
    for index, text in enumerate(left_rows):
        parts.append(
            f'<text class="t" x="{left_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    for index, text in enumerate(right_rows):
        parts.append(
            f'<text class="t" x="{right_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 出典が付いていても、URLが実在するとは限りません。1つは実際に開いて確かめてください。</text>\n"
    )
    alt = (
        "調べものを出典つきで受け取る効果を比べた図。"
        "出典を求めないとき＝答えだけ返り、合っていそうに見えるが、確かめる方法が無く、間違いに気づけない。"
        "出典を求めたとき＝答えとURLが並び、URLを開けば確かめられ、無い情報は無いと分かり、自分の責任で使える。"
        "ただし出典が付いていてもURLが実在するとは限らないので、1つは実際に開いて確かめる。"
    )
    (OUT / "sourced-research.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def mail_triage_chart() -> None:
    """受信箱を3つに仕分ける図。2分類だと真ん中が落ちることを見せる。"""
    rows = [
        (
            "box-accent",
            "t-accent",
            "A 返信しないと相手が止まる",
            "可否の回答待ち・実装が止まっている問い合わせ",
        ),
        (
            "box-bad",
            "t-bad",
            "B 返信は要らないが、自分の作業がある",
            "経費精算・回答期限つきの社内アンケート ← 2分類だとここが落ちる",
        ),
        (
            "box-quiet",
            "t",
            "C 読むだけでよい",
            "「返信は不要です」と本文に書いてある周知・メールマガジン",
        ),
    ]
    src_x, src_w, src_h = 18, 168, 70
    out_x = 300
    out_w = WIDTH - out_x - 18
    out_h, out_gap = 64, 18
    top = 90
    span = len(rows) * (out_h + out_gap) - out_gap
    src_y = top + (span - src_h) / 2
    height = top + span + 46

    parts = [
        '<text class="t-strong" x="18" y="26">受信箱は「返信が要る／要らない」の2つでは仕分けられない</text>\n',
        '<text class="t-sm" x="18" y="45">'
        "返信は不要でも締切のある作業は残ります。3つに分けると、そこが消えません。</text>\n",
        f'<rect class="box-quiet" x="{src_x}" y="{src_y:.0f}" '
        f'width="{src_w}" height="{src_h}" rx="6"/>\n',
        f'<text class="t" x="{src_x + 16}" y="{src_y + 28:.0f}">受信箱の未読</text>\n',
        f'<text class="t-sm" x="{src_x + 16}" y="{src_y + 50:.0f}">まとめて貼って渡す</text>\n',
    ]
    for index, (box_cls, text_cls, title, note) in enumerate(rows):
        y = top + index * (out_h + out_gap)
        parts.append(
            f'<rect class="{box_cls}" x="{out_x}" y="{y}" '
            f'width="{out_w}" height="{out_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{text_cls}" x="{out_x + 14}" y="{y + 26}">{_esc(title)}</text>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{out_x + 14}" y="{y + 47}">{_esc(note)}</text>\n'
        )
        ay = y + out_h / 2
        parts.append(
            f'<line class="line" x1="{src_x + src_w + 8}" y1="{src_y + src_h / 2:.0f}" '
            f'x2="{out_x - 14}" y2="{ay:.0f}"/>\n'
        )
        parts.append(
            f'<path d="M{out_x - 14} {ay - 4:.0f} L{out_x - 7} {ay:.0f} '
            f'L{out_x - 14} {ay + 4:.0f} Z" fill="#8b949e"/>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ どちらにも当てはまる1通があります（返信もするし、社内の登録変更も要る）。"
        "急ぐほうに入れて、もう片方を同じ行に書かせます。</text>\n"
    )
    alt = (
        "受信箱の未読をAIに渡して3つに仕分ける図。"
        "A＝返信しないと相手が止まるもの（可否の回答待ち、実装が止まっている問い合わせ）。"
        "B＝返信は要らないが自分の作業があるもの（経費精算、回答期限つきの社内アンケート）。"
        "「返信が要るものだけ」と頼むとBが落ちる。"
        "C＝読むだけでよいもの（返信は不要ですと本文に書いてある周知、メールマガジン）。"
        "AとBの両方に当てはまる1通は、急ぐほうに入れてもう片方を同じ行に書かせる。"
    )
    (OUT / "mail-triage.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gpt56_family_chart() -> None:
    """GPT-5.6 の3モデル。値段は25倍差だが、器の仕様は全部同じ。"""
    rows = [
        ("GPT-5.6 Sol", 5.0, 30.0, "いちばん賢い"),
        ("GPT-5.6 Terra", 2.0, 12.0, "中間"),
        ("GPT-5.6 Luna", 0.20, 1.20, "いちばん安い"),
    ]
    left, right = 168, 600
    span = right - left
    top, bar_h, bar_gap, group_gap = 76, 15, 5, 26
    group_h = bar_h * 2 + bar_gap + group_gap
    scale = span / max(b for _, _, b, _ in rows)

    parts = [
        '<text class="t-strong" x="18" y="26">GPT-5.6 の3モデル（100万トークンあたり・ドル）</text>\n',
        '<text class="t-sm" x="18" y="45">薄い色＝入力 ／ 濃い色＝出力。短い入力のときの値段です。</text>\n',
    ]
    for index, (name, price_in, price_out, note) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t-xs" x="18" y="{y + 30}">{_esc(note)}</text>\n')
        for offset, (value, cls) in enumerate(((price_in, "bar-in"), (price_out, "bar-out"))):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"${value:g}</text>\n"
            )

    box_y = top + len(rows) * group_h - group_gap + 16
    box_h = 74
    parts.append(
        f'<rect class="box-accent" x="18" y="{box_y}" width="{WIDTH - 36}" height="{box_h}" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{box_y + 24}">3つとも同じもの</text>\n'
    )
    parts.append(
        f'<text class="t" x="34" y="{box_y + 46}">'
        "読める量 1.05M ／ 書ける量 12.8万 ／ 知識は2026年2月16日まで</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="34" y="{box_y + 64}">'
        "使える道具（関数・ウェブ検索・ファイル検索・パソコン操作）も同じ</text>\n"
    )

    height = box_y + box_h + 34
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 違うのは値段と賢さだけ。器の大きさは同じなので、安いほうを試して足りれば安いままで済みます。</text>\n"
    )
    alt = (
        "GPT-5.6 の3モデルの値段を比べた横棒グラフ。100万トークンあたりのドル。"
        "GPT-5.6 Sol（いちばん賢い）は入力5ドル・出力30ドル、"
        "GPT-5.6 Terra（中間）は入力2ドル・出力12ドル、"
        "GPT-5.6 Luna（いちばん安い）は入力0.2ドル・出力1.2ドル。"
        "3つとも読める量1.05M、書ける量12.8万、知識は2026年2月16日まで、"
        "使える道具（関数・ウェブ検索・ファイル検索・パソコン操作）も同じ。"
        "違うのは値段と賢さだけ。"
    )
    (OUT / "gpt56-family.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def report_split_chart() -> None:
    """報告の一文を「確認済み／未確認」に分けさせると、穴がその場で見える。"""
    # 左の3つは記事の冒頭で挙げている、実際に返ってくる言い回しそのまま。
    # 右は「分けさせたときに出てくる形」で、測った数字を勝手に足さない。
    rows = [
        (
            "実装しました",
            "box-good", "t-good", "確認済み",
            "実行したコマンドと出力を添える",
        ),
        (
            "おそらく正常に動作します",
            "box-quiet", "t-sm", "未確認",
            "まだ一度も動かしていない",
        ),
        (
            "こちらのURLから取得できます",
            "box-bad", "t-bad", "開けなかった",
            "実際に開くと404だった",
        ),
    ]
    left_x, left_w = 18, 282
    right_x = 340
    right_w = WIDTH - 18 - right_x
    top, row_h, gap = 96, 68, 16
    height = top + len(rows) * row_h + (len(rows) - 1) * gap + 46

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「できました」を、確かめたかどうかで分けさせる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ1回の報告を3つに分けたものです。分けるまで、どれが未確認かは出てきません。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "URL・ファイル名・設定項目・オプション名は、とくに作られやすい4つです。</text>\n",
        f'<text class="t-xs" x="{left_x}" y="{top - 12}">AIの報告（そのまま）</text>\n',
        f'<text class="t-xs" x="{right_x}" y="{top - 12}">分けさせると、その場で見えるもの</text>\n',
    ]
    for index, (claim, box_cls, label_cls, label, detail) in enumerate(rows):
        y = top + index * (row_h + gap)
        parts.append(
            f'<rect class="box-quiet" x="{left_x}" y="{y}" '
            f'width="{left_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t" x="{left_x + 14}" y="{y + 40}">{_esc(claim)}</text>\n')
        parts.append(
            f'<rect class="{box_cls}" x="{right_x}" y="{y}" '
            f'width="{right_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{label_cls}" x="{right_x + 14}" y="{y + 26}">{_esc(label)}</text>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{right_x + 14}" y="{y + 50}">{_esc(detail)}</text>\n'
        )
        ay = y + row_h / 2
        parts.append(
            f'<line class="line" x1="{left_x + left_w + 8}" y1="{ay:.0f}" '
            f'x2="{right_x - 14}" y2="{ay:.0f}"/>\n'
        )
        parts.append(
            f'<path d="M{right_x - 14} {ay - 4:.0f} L{right_x - 7} {ay:.0f} '
            f'L{right_x - 14} {ay + 4:.0f} Z" fill="#8b949e"/>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 3行ともそのまま読めば「できました」に見えます。だから分けさせます。</text>\n"
    )
    alt = (
        "AIの報告を、確かめたかどうかで3つに分けた対応表。"
        "「実装しました」は確認済みで、実行したコマンドと出力を添えさせる。"
        "「おそらく正常に動作します」は未確認で、まだ一度も動かしていない。"
        "「こちらのURLから取得できます」は開けなかったもので、実際に開くと404だった。"
        "3行ともそのまま読めば「できました」に見えるため、分けさせるまでどれが未確認かは出てこない。"
    )
    (OUT / "report-split.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_timing_chart() -> None:
    """人にしかできない作業が、いつ見えるか。作業は同じで、変わるのは時刻だけ。"""
    bar_w, human_w, bar_h = 470, 206, 34
    left = 18
    lane_a_y, lane_b_y = 106, 212
    band_y, band_h = 286, 62
    height = band_y + band_h + 34

    parts = [
        '<text class="t-strong" x="18" y="26">人にしかできない作業を、いつ知るか</text>\n',
        '<text class="t-sm" x="18" y="45">'
        "作業そのものは変わりません。変わるのは、それが見える時刻だけです。</text>\n",
        '<text class="t-sm" x="18" y="64">このサイトを公開したときに実際に起きたことです。</text>\n',
        f'<text class="t-bad" x="18" y="{lane_a_y - 8}">分担表を出させないとき</text>\n',
        f'<rect class="bar-old" x="{left}" y="{lane_a_y}" '
        f'width="{bar_w}" height="{bar_h}" rx="3"/>\n',
        f'<text class="t" x="{left + 14}" y="{lane_a_y + 22}">AIが作る</text>\n',
        f'<rect class="box-bad" x="{left + bar_w + 8}" y="{lane_a_y}" '
        f'width="{human_w}" height="{bar_h}" rx="6"/>\n',
        f'<text class="t-bad" x="{left + bar_w + 22}" y="{lane_a_y + 22}">人の作業が3つ</text>\n',
        f'<text class="t-sm" x="18" y="{lane_a_y + 50}">'
        "公開の直前にまとめて出てくる。別の日に持ち越しになった</text>\n",
        f'<text class="t-good" x="18" y="{lane_b_y - 8}">先に分担表を出させたとき</text>\n',
        f'<rect class="box-good" x="{left}" y="{lane_b_y}" '
        f'width="{human_w}" height="{bar_h}" rx="6"/>\n',
        f'<text class="t-good" x="{left + 14}" y="{lane_b_y + 22}">人の作業が3つ</text>\n',
        f'<rect class="bar-old" x="{left + human_w + 8}" y="{lane_b_y}" '
        f'width="{bar_w}" height="{bar_h}" rx="3"/>\n',
        f'<text class="t" x="{left + human_w + 22}" y="{lane_b_y + 22}">AIが作る</text>\n',
        f'<text class="t-sm" x="18" y="{lane_b_y + 50}">'
        "頼んだ日に一覧で見えている。順番を入れ替えるだけで済む</text>\n",
        f'<rect class="box-accent" x="18" y="{band_y}" '
        f'width="{WIDTH - 36}" height="{band_h}" rx="6"/>\n',
        f'<text class="t-accent" x="32" y="{band_y + 30}">'
        "3つとも、ログインして画面を操作する作業</text>\n",
        f'<text class="t-sm" x="32" y="{band_y + 52}">'
        "ドメインのDNS設定 ／ HTTPSの有効化 ／ 検索エンジンへの登録。AIは代われない</text>\n",
    ]
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ どれも難しい作業ではありません。最後にまとめて出てくることだけが問題です。</text>\n"
    )
    alt = (
        "人にしかできない作業をいつ知るかを2本のレーンで比べた図。"
        "分担表を出させないときは、AIが作る工程が長く続いたあと、公開の直前に人の作業が3つまとめて出てきて、"
        "別の日に持ち越しになった。"
        "先に分担表を出させたときは、人の作業3つが頼んだ日に一覧で見えているので、順番を入れ替えるだけで済む。"
        "3つとはドメインのDNS設定、HTTPSの有効化、検索エンジンへの登録で、"
        "どれもログインして画面を操作する作業のためAIは代われない。"
        "作業そのものは変わらず、変わるのはそれが見える時刻だけ。"
    )
    (OUT / "handoff-timing.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def scope_weight_chart() -> None:
    """頼んだ範囲と、返ってきた案の重さ。範囲を区切っても案は消えない。"""
    left_x, left_w = 18, 310
    right_x = 352
    right_w = WIDTH - 18 - right_x
    top, box_h = 96, 170
    band_y, band_h = 290, 62
    height = band_y + band_h + 34
    proposal = [
        "記事ごとに3段階のラベルを付ける仕組み",
        "記事の設定に項目を足す",
        "テンプレートを直す",
        "検査も足す",
    ]

    parts = [
        '<text class="t-strong" x="18" y="26">頼んだのは、文章を1つ消すことだけでした</text>\n',
        '<text class="t-sm" x="18" y="45">'
        "範囲を言わずに頼むと、返ってくる案は「良くする」方向へ膨らみます。</text>\n",
        '<text class="t-sm" x="18" y="64">悪意ではありません。丁寧にやろうとした結果です。</text>\n',
        f'<rect class="box-good" x="{left_x}" y="{top}" '
        f'width="{left_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-good" x="{left_x + 14}" y="{top + 28}">頼んだこと</text>\n',
        f'<text class="t" x="{left_x + 14}" y="{top + 56}">トップページの文章を1つ消す</text>\n',
        f'<text class="t-sm" x="{left_x + 14}" y="{top + 84}">実際に済んだ形:</text>\n',
        f'<text class="t-sm" x="{left_x + 14}" y="{top + 106}">テキスト4か所の書き換え</text>\n',
        f'<text class="t-strong" x="{left_x + 14}" y="{top + 140}">かかった時間 5分</text>\n',
        f'<rect class="box-bad" x="{right_x}" y="{top}" '
        f'width="{right_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-bad" x="{right_x + 14}" y="{top + 28}">返ってきた案</text>\n',
    ]
    for index, line in enumerate(proposal):
        parts.append(
            f'<text class="t-sm" x="{right_x + 14}" y="{top + 56 + index * 22}">'
            f"{_esc(line)}</text>\n"
        )
    parts.append(
        f'<text class="t-strong" x="{right_x + 14}" y="{top + 152}">放っておけば 半日</text>\n'
    )
    parts.append(
        f'<rect class="box-accent" x="18" y="{band_y}" '
        f'width="{WIDTH - 36}" height="{band_h}" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t-accent" x="32" y="{band_y + 30}">'
        "範囲を区切っても、案が消えるわけではありません</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="32" y="{band_y + 52}">'
        "「範囲外は直さずに指摘だけ」と足すと、同じ案が提案として出てきます</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 案の良し悪しと、いまそれをやるべきかどうかは別の話です。</text>\n"
    )
    alt = (
        "頼んだ範囲と返ってきた案の重さを比べた図。"
        "頼んだことはトップページの文章を1つ消すことだけで、"
        "実際にはテキスト4か所の書き換えで済み、かかった時間は5分。"
        "ところが返ってきた案は、記事ごとに3段階のラベルを付ける仕組み、記事の設定に項目を足す、"
        "テンプレートを直す、検査も足す、というもので、放っておけば半日かかる。"
        "ただし範囲を区切っても案が消えるわけではなく、"
        "「範囲外は直さずに指摘だけ」と足せば同じ案が提案として出てくる。"
    )
    (OUT / "scope-weight.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def start_requirements_chart() -> None:
    """4つのツールの最低要件。公式に書いていない欄は推測で埋めない。

    値は docs/superpowers/notes/2026-08-09-start-facts.md（公式ページの生テキストから
    収集）そのまま。⚠️ 埋まっていない欄を推測で埋めないこと。書いていないこと自体が
    「普通のPCなら通る」という答えになっている。
    """
    rows = [
        ("ChatGPT", "ブラウザ", "記載なし", ["記載なし"], "無料で開始"),
        ("Claude", "ブラウザ", "記載なし", ["記載なし"], "無料で開始"),
        ("Gemini", "ブラウザ", "記載なし",
         ["Chrome / Safari / Firefox /", "Opera / Edgium"], "無料で開始"),
        ("Claude Code", "アプリ", "4GB以上",
         ["Windows 10 1809+", "macOS 13.0+"], "有料プラン"),
    ]
    name_x, mem_x, os_x, price_x = 32, 206, 296, 596
    top, row_h, box_h = 104, 56, 48
    band_y, band_h = 344, 54
    height = band_y + band_h + 34

    parts = [
        '<text class="t-strong" x="18" y="26">公式が出している「最低これだけ要る」</text>\n',
        '<text class="t-sm" x="18" y="45">'
        "2026年8月9日に各社の公式ページで確認したものだけを並べています。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「記載なし」は、公式が書いていないという意味です。こちらの推測では埋めていません。</text>\n",
        f'<text class="t-xs" x="{name_x}" y="{top - 12}">ツール</text>\n',
        f'<text class="t-xs" x="{mem_x}" y="{top - 12}">メモリ</text>\n',
        f'<text class="t-xs" x="{os_x}" y="{top - 12}">対応OS・ブラウザ</text>\n',
        f'<text class="t-xs" x="{price_x}" y="{top - 12}">料金</text>\n',
    ]
    for index, (name, kind, memory, os_lines, price) in enumerate(rows):
        y = top + index * row_h
        cls = "box-accent" if name == "Claude Code" else "box-quiet"
        parts.append(
            f'<rect class="{cls}" x="18" y="{y}" '
            f'width="{WIDTH - 36}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t-strong" x="{name_x}" y="{y + 20}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t-xs" x="{name_x}" y="{y + 38}">{_esc(kind)}</text>\n')
        mem_cls = "t-strong" if memory != "記載なし" else "t-xs"
        parts.append(f'<text class="{mem_cls}" x="{mem_x}" y="{y + 20}">{_esc(memory)}</text>\n')
        for line_index, line in enumerate(os_lines):
            line_cls = "t-xs" if line == "記載なし" else "t-sm"
            parts.append(
                f'<text class="{line_cls}" x="{os_x}" y="{y + 20 + line_index * 18}">'
                f"{_esc(line)}</text>\n"
            )
        parts.append(f'<text class="t-sm" x="{price_x}" y="{y + 20}">{_esc(price)}</text>\n')

    parts.append(
        f'<rect class="box-good" x="18" y="{band_y}" '
        f'width="{WIDTH - 36}" height="{band_h}" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t-good" x="32" y="{band_y + 24}">'
        "4GB あれば、この4つのうち一番重いものが動きます</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="32" y="{band_y + 44}">'
        "ブラウザで使う3つは、必要なメモリを公表していません。それだけ軽いということです。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ Claude Code だけ、公式が 4GB以上・x64かARM64 と明記しています。</text>\n"
    )
    alt = (
        "4つのAIツールの最低要件を並べた表。2026年8月9日に各社の公式ページで確認したもの。"
        "ChatGPT・Claude のブラウザ版は、対応OSもメモリも公式の記載なしで、無料で開始できる。"
        "Gemini のブラウザ版は対応ブラウザが Chrome、Safari、Firefox、Opera、Edgium と"
        "公表されているが、メモリの記載はなく、無料で開始できる。"
        "Claude Code はメモリ4GB以上、Windows 10 1809以降または macOS 13.0以降で、有料プラン。"
        "つまり4GBあれば、この4つのうち一番重いものが動く。"
        "ブラウザで使う3つは必要なメモリを公表しておらず、それだけ軽いということ。"
    )
    (OUT / "start-requirements.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def start_boundary_chart() -> None:
    """ブラウザだけで足りること と、Claude Code が要ること の境界。

    ⚠️ 初稿は「Claude Code＝ターミナルが要る」で描いていたが、公式に
    「The Desktop app lets you use Claude Code without the terminal」とあり、
    さらにネイティブ導入は Node.js を要求しない（npm版だけが Node.js 22+）。
    初心者の障壁として一番大きい2つが、実は必須ではない。
    """
    left_rows = [
        "文章を書かせる・直させる",
        "資料を読ませて要約させる",
        "調べものに付き合わせる",
        "写真を見せて相談する",
    ]
    right_rows = [
        "パソコンのファイルを直接触る",
        "決まった時刻に自動で動かす",
        "このサイトのレシピを実行する",
        "作ったものを動かして確かめる",
    ]
    col_w, gap, pad = 330, 24, 18
    left_x, right_x = pad, pad + col_w + gap
    head_y, first_y, row_h = 84, 114, 34
    rows = max(len(left_rows), len(right_rows))
    box_h = 30 + rows * row_h
    band_y, band_h = first_y + rows * row_h + 18, 76
    height = band_y + band_h + 36

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "ブラウザだけで足りるか、Claude Code が要るか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "左だけでも、AIの頼み方はひととおり身につきます。</text>\n",
        f'<rect class="box-good" x="{left_x}" y="{head_y - 22}" '
        f'width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<rect class="box-accent" x="{right_x}" y="{head_y - 22}" '
        f'width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-good" x="{left_x + 14}" y="{head_y - 2}">ブラウザだけでできる</text>\n',
        f'<text class="t-accent" x="{right_x + 14}" y="{head_y - 2}">Claude Code が要る</text>\n',
    ]
    for index, text in enumerate(left_rows):
        parts.append(
            f'<text class="t" x="{left_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    for index, text in enumerate(right_rows):
        parts.append(
            f'<text class="t" x="{right_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    parts.append(
        f'<rect class="box-quiet" x="{pad}" y="{band_y}" '
        f'width="{col_w * 2 + gap}" height="{band_h}" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t-accent" x="{pad + 14}" y="{band_y + 26}">'
        "Claude Code の入り口は2つある</text>\n"
    )
    parts.append(
        f'<text class="t" x="{pad + 14}" y="{band_y + 50}">'
        "デスクトップ版＝ターミナルを使わない ／ コマンド版＝1行貼るだけ</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="{pad + 14}" y="{band_y + 68}">'
        "どちらも Node.js は要りません（2026年8月9日に公式で確認）</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 右が要らないなら、Claude Code は入れなくて構いません。左だけで十分に役に立ちます。</text>\n"
    )
    alt = (
        "ブラウザ版だけでできることと、Claude Code が必要になることを2列で比べた図。"
        "ブラウザだけでできる＝文章を書かせる・直させる、資料を読ませて要約させる、"
        "調べものに付き合わせる、写真を見せて相談する。"
        "Claude Code が要る＝パソコンのファイルを直接触る、決まった時刻に自動で動かす、"
        "このサイトのレシピを実行する、作ったものを動かして確かめる。"
        "Claude Code の入り口は2つあり、デスクトップ版はターミナルを使わず、"
        "コマンド版は1行貼るだけ。どちらも Node.js は要らない（2026年8月9日に公式で確認）。"
        "右が要らないなら Claude Code は入れなくてよい。"
    )
    (OUT / "start-boundary.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def table_anomaly_types_chart() -> None:
    """表に混ざる異常の6種類と、目で見つかるかどうか。"""
    rows = [
        ("桁のミス", "他の月の10倍の数字が1つだけ入っている", "目で見つかる", False),
        ("単位の混ざり", "1つの行だけ円、他の行は千円で入っている", "目で見つかる", False),
        ("符号", "売上の列にマイナスの数字が混ざっている", "目で見つかる", False),
        ("空欄", "1か月だけ何も入っていない", "目で見つかる", False),
        ("合計欄のズレ", "合計欄と12か月の和が3,000だけ違う", "足し直すまで見えない", True),
        ("行の重複", "同じ数字の行が別の名前で2つある", "足し直すまで見えない", True),
    ]
    box_x, box_w, box_h, gap_y = 18, 140, 52, 14
    mid_x = box_x + box_w + 20
    mid_w = 318
    right_x = mid_x + mid_w + 20
    top = 84
    height = top + len(rows) * (box_h + gap_y) - gap_y + 44
    assert right_x + 180 <= WIDTH - 18, right_x

    parts = [
        '<text class="t-strong" x="18" y="26">表に混ざる異常は6種類。後ろの2つは見た目が普通</text>\n',
        '<text class="t-sm" x="18" y="45">'
        "上の4つは数字そのものが目立つ。下の2つは1つ1つの数字が正常に見える。</text>\n",
    ]
    for index, (name, example, how, hidden) in enumerate(rows):
        y = top + index * (box_h + gap_y)
        mid = y + box_h / 2
        name_cls = "box-bad" if hidden else "box-accent"
        text_cls = "t-bad" if hidden else "t-accent"
        parts.append(
            f'<rect class="{name_cls}" x="{box_x}" y="{y}" width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{text_cls}" x="{box_x + 14}" y="{mid + 5:.0f}">{_esc(name)}</text>\n'
        )
        parts.append(
            f'<rect class="box-quiet" x="{mid_x}" y="{y}" width="{mid_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t" x="{mid_x + 14}" y="{mid + 5:.0f}">{_esc(example)}</text>\n'
        )
        parts.append(
            f'<text class="{"t-bad" if hidden else "t-sm"}" x="{right_x}" y="{mid + 5:.0f}">'
            f"{_esc(how)}</text>\n"
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 下の2つは、セル1つだけを見ても異常に見えません。探す種類として名指しするまで出てきません。</text>\n"
    )
    alt = (
        "表に混ざる異常を6種類に分けた図。桁のミス（他の月の10倍の数字が1つ）、"
        "単位の混ざり（1つの行だけ円で他は千円）、符号（売上の列にマイナス）、"
        "空欄（1か月だけ何も入っていない）の4つは、数字そのものが目立つので目で見つかる。"
        "合計欄のズレ（合計欄と12か月の和が3,000違う）と行の重複（同じ数字の行が別の名前で2つある）の"
        "2つは、1つ1つの数字が正常に見えるため、足し直すまで見えない。"
        "この2つは探す種類として名指しするまで指摘に出てこない。"
    )
    (OUT / "table-anomaly-types.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def report_facts_lost_chart() -> None:
    """今週のメモにあった事実のうち、週報に残った数（2026-08-12 実測）。"""
    lost = ["返事がまだ来ていない", "止まっている理由（担当が出張）",
            "△△工業は今週動きなし", "研修が延期になった",
            "延期は先方都合", "事務作業で2日つぶれた",
            "値引きの可否を相談したい"]
    left, unit = 214, 42
    bar_h, gap_y = 46, 20
    top = 96
    list_top = top + 2 * (bar_h + gap_y) + 22
    height = list_top + len(lost) * 25 + 44
    assert left + 9 * unit <= WIDTH - 18, left + 9 * unit

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "先週の形に合わせると、今週の事実が消える</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "走り書きのメモにあった「報告すべき事実」9件が、週報にいくつ残ったか。</text>\n",
    ]
    for index, (name, value, cls, tcls) in enumerate(
        (("「先週のこの形式で」", 2, "box-bad", "t-bad"),
         ("型だけ使わせ、対応表を出させる", 9, "box-good", "t-good"))
    ):
        y = top + index * (bar_h + gap_y)
        mid = y + bar_h / 2 + 5
        parts.append(f'<text class="t-sm" x="18" y="{mid:.0f}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{left}" y="{y}" '
            f'width="{9 * unit}" height="{bar_h}" rx="6"/>\n'
        )
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" '
            f'width="{value * unit}" height="{bar_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{tcls}" x="{left + 9 * unit + 10}" '
            f'y="{mid:.0f}">{value}／9</text>\n'
        )
    parts.append(
        f'<text class="t-bad" x="18" y="{list_top - 8}">'
        "消えた7件（上ほど困るもの）</text>\n"
    )
    for index, name in enumerate(lost):
        parts.append(
            f'<text class="t-sm" x="34" y="{list_top + index * 25 + 12}">'
            f"・{_esc(name)}</text>\n"
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 消えた7件は、どれも「進んでいない」ことを伝える情報。"
        "報告書としては、いちばん伝えなければいけないところ。</text>\n"
    )
    alt = (
        "週報を作らせたときに、今週のメモにあった事実がいくつ残ったかを比べた図。"
        "走り書きのメモにあった報告すべき事実9件のうち、「先週のこの形式で書いて」と"
        "頼んだ場合は2件しか残らなかった。型だけ使わせてメモとの対応表を出させると"
        "9件すべてが残った。消えた7件は、返事がまだ来ていない、止まっている理由が"
        "担当の出張であること、△△工業は今週動きなし、研修が延期になった、"
        "延期は先方都合、事務作業で2日つぶれた、値引きの可否を相談したい、の7つ。"
        "どれも進んでいないことを伝える情報で、報告書としてはいちばん伝えなければ"
        "いけないところ。"
    )
    (OUT / "report-facts-lost.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def report_template_overwrite_chart() -> None:
    """先週の型の言葉が、今週の事実を上書きした対応（実測）。"""
    pairs = [
        ("返事なし・担当が出張", "検討が進んでいます"),
        ("今週は動きなし", "順調に進行中"),
        ("研修が延期・日程未定", "日程を調整中"),
        ("値引きの可否を相談したい", "特になし"),
        ("（メモに進捗の数字なし）", "進捗85%"),
    ]
    left_x, right_x = 18, 392
    box_w = 300
    item_h, gap = 44, 12
    top = 106
    height = top + len(pairs) * (item_h + gap) - gap + 48
    assert right_x + box_w <= WIDTH - 18, right_x + box_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "型の言葉が、今週の事実を上書きする</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "左が今週のメモに書いてあったこと。右が返ってきた週報の文。</text>\n",
        f'<text class="t-xs" x="{left_x + 8}" y="{top - 14}">メモ（本当のこと）</text>\n',
        f'<text class="t-xs" x="{right_x + 8}" y="{top - 14}">週報に出てきた文</text>\n',
    ]
    for index, (fact, written) in enumerate(pairs):
        y = top + index * (item_h + gap)
        mid = y + item_h / 2 + 5
        parts.append(
            f'<rect class="box-quiet" x="{left_x}" y="{y}" '
            f'width="{box_w}" height="{item_h}" rx="5"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left_x + 12}" y="{mid:.0f}">{_esc(fact)}</text>\n'
        )
        parts.append(
            f'<rect class="box-bad" x="{right_x}" y="{y}" '
            f'width="{box_w}" height="{item_h}" rx="5"/>\n'
        )
        parts.append(
            f'<text class="t-bad" x="{right_x + 12}" y="{mid:.0f}">{_esc(written)}</text>\n'
        )
        arrow_y = y + item_h / 2
        parts.append(
            f'<line class="link" x1="{left_x + box_w + 8}" y1="{arrow_y}" '
            f'x2="{right_x - 8}" y2="{arrow_y}"/>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 右の文はどれも週報として自然に読める。"
        "メモと並べるまで、書き換わっていることが分からない。</text>\n"
    )
    alt = (
        "週報で、型の言葉が今週の事実を上書きした対応を並べた図。"
        "メモに「返事なし・担当が出張」とあったものが週報では「検討が進んでいます」に、"
        "「今週は動きなし」が「順調に進行中」に、「研修が延期・日程未定」が「日程を調整中」に、"
        "「値引きの可否を相談したい」が「特になし」になった。"
        "さらにメモに進捗の数字が無いのに「進捗85%」と書かれた。"
        "右の文はどれも週報として自然に読めるので、メモと並べるまで"
        "書き換わっていることが分からない。"
    )
    (OUT / "report-template-overwrite.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def menu_constraints_chart() -> None:
    """渡した条件が、献立にいくつ反映されたかの実測（2026-08-12）。

    架空の冷蔵庫（15品）と5つの条件（えびアレルギー・予算3,000円・
    平日20分・期限順・7日分）を渡して測った。判定は Python。
    """
    rows = [
        ("えびアレルギーを守った", False, True),
        ("買い足しに金額がある", False, True),
        ("予算3,000円に触れている", False, True),
        ("各日の調理時間がある", False, True),
        ("使わなかったものが分かる", False, True),
        ("在庫の残量が分かる", False, True),
    ]
    label_x, label_w = 18, 268
    mark_w = 150
    a_x = label_x + label_w + 18
    b_x = a_x + mark_w + 26
    row_h, gap_y = 38, 11
    top = 104
    height = top + len(rows) * (row_h + gap_y) - gap_y + 46
    assert b_x + mark_w <= WIDTH - 18, b_x + mark_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "条件は、書いて渡しただけでは守られない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の冷蔵庫15品と条件5つを渡して測った。判定はすべて機械。</text>\n",
        f'<text class="t-xs" x="{a_x}" y="{top - 12}">'
        "「あるもので献立を作って」</text>\n",
        f'<text class="t-xs" x="{b_x}" y="{top - 12}">'
        "条件を先に書き出させる</text>\n",
    ]
    for index, (name, before, after) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        mid = y + row_h / 2 + 5
        parts.append(f'<text class="t-sm" x="{label_x}" y="{mid:.0f}">{_esc(name)}</text>\n')
        for start, ok in ((a_x, before), (b_x, after)):
            parts.append(
                f'<rect class="{"box-good" if ok else "box-quiet"}" x="{start}" y="{y}" '
                f'width="{mark_w}" height="{row_h}" rx="6"/>\n'
            )
            parts.append(
                f'<text class="{"t-good" if ok else "t-bad"}" x="{start + 14}" '
                f'y="{mid:.0f}">{"守られた" if ok else "守られない"}</text>\n'
            )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 左の献立は読んでもおかしくない。えびが入っていることは、"
        "自分で条件と照らし合わせるまで気づけない。</text>\n"
    )
    alt = (
        "献立作りで、渡した条件がどれだけ守られたかを比べた実測の図。"
        "架空の冷蔵庫15品と条件5つを渡して機械で判定した。"
        "「あるもので献立を作って」とだけ頼むと、えびアレルギーを守る、"
        "買い足しに金額がある、予算3,000円に触れている、各日の調理時間がある、"
        "使わなかったものが分かる、在庫の残量が分かる、の6項目すべてが守られなかった。"
        "守る条件を先に書き出させると6項目すべてが守られた。"
        "素朴に頼んだ献立は読んでもおかしくないので、えびが入っていることは"
        "自分で条件と照らし合わせるまで気づけない。"
    )
    (OUT / "menu-constraints.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def menu_stock_usage_chart() -> None:
    """冷蔵庫にある15品のうち、献立に登場したものの数。"""
    left, unit = 172, 30
    bar_h, gap_y = 46, 20
    top = 96
    leftover = ["にんじん", "玉ねぎ", "ピーマン", "牛乳", "ミックスベジタブル", "食パン"]
    list_top = top + 2 * (bar_h + gap_y) + 14
    height = list_top + 30 + 44
    assert left + 15 * unit <= WIDTH - 18, left + 15 * unit

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「あるもので」と頼んでも、6品は使われずに残る</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "冷蔵庫と食品棚にあった15品のうち、献立に出てきた数。</text>\n",
    ]
    for index, (name, value, cls, tcls) in enumerate(
        (("「あるもので作って」", 9, "box-accent", "t-accent"),
         ("使い切る量まで書かせる", 15, "box-good", "t-good"))
    ):
        y = top + index * (bar_h + gap_y)
        mid = y + bar_h / 2 + 5
        parts.append(f'<text class="t-sm" x="18" y="{mid:.0f}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{left}" y="{y}" '
            f'width="{15 * unit}" height="{bar_h}" rx="6"/>\n'
        )
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" '
            f'width="{value * unit}" height="{bar_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{tcls}" x="{left + 15 * unit + 10}" '
            f'y="{mid:.0f}">{value}／15品</text>\n'
        )
    parts.append(
        f'<text class="t-bad" x="18" y="{list_top}">'
        f"残ったもの: {_esc('・'.join(leftover))}</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 残った6品は、次の週まで持たないものが混ざる。"
        "「使わなかったものを挙げて」と頼むまで、残ったこと自体が見えない。</text>\n"
    )
    alt = (
        "冷蔵庫にあった15品のうち、献立に登場した品数を比べた図。"
        "「あるもので作って」と頼んだときは15品中9品しか使われず、"
        "にんじん、玉ねぎ、ピーマン、牛乳、ミックスベジタブル、食パンの6品が残った。"
        "使い切る量まで書かせると15品すべてが使われた。"
        "残った6品には次の週まで持たないものが混ざるが、"
        "使わなかったものを挙げてと頼むまで、残ったこと自体が見えない。"
    )
    (OUT / "menu-stock-usage.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def slides_screen_vs_spoken_chart() -> None:
    """同じ素材で、頼み方だけを変えて測った4項目。

    実測（2026-08-11・15分の社内提案・素材は箇条書き14件）。
    判定は Python（枚数・画面に出る文字数・口頭の分離・未確認情報の位置）。
    """
    rows = [
        ("枚数（15分）", "18枚", "9枚", True),
        ("画面に出る字（平均）", "63字", "17字", True),
        ("40字を超えた枚", "18枚中15枚", "9枚中0枚", True),
        ("口で言うこと", "分かれていない", "画面の3.9倍", True),
        ("裏を取れていない話", "画面に載る", "画面から外す", True),
    ]
    label_x, label_w = 18, 168
    col_w = 168
    a_x = label_x + label_w + 16
    b_x = a_x + col_w + 22
    row_h, gap_y = 40, 12
    top = 100
    height = top + len(rows) * (row_h + gap_y) - gap_y + 46
    assert b_x + col_w <= WIDTH - 18, b_x + col_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ素材・同じ15分。頼み方だけを変えて測った</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "素材は箇条書き14件の発表メモ。判定はすべて機械（文字数と枚数を数えた）。</text>\n",
        f'<text class="t-xs" x="{a_x + 8}" y="{top - 12}">'
        "「15分の発表用に構成を作って」</text>\n",
        f'<text class="t-xs" x="{b_x + 8}" y="{top - 12}">'
        "枚数・字数・口頭を指定</text>\n",
    ]
    for index, (name, before, after, better) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        mid = y + row_h / 2 + 5
        parts.append(f'<text class="t-sm" x="{label_x}" y="{mid:.0f}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{a_x}" y="{y}" '
            f'width="{col_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-bad" x="{a_x + 12}" y="{mid:.0f}">{_esc(before)}</text>\n'
        )
        parts.append(
            f'<rect class="box-good" x="{b_x}" y="{y}" '
            f'width="{col_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-good" x="{b_x + 12}" y="{mid:.0f}">{_esc(after)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 口で言うことが画面の3.9倍。発表は「書いてあることを読む」ものではないので、"
        "この差が出るのが正しい。</text>\n"
    )
    alt = (
        "スライドの骨子を作らせた実測の比較図。素材は箇条書き14件の発表メモで、"
        "持ち時間は15分。「15分の発表用に構成を作って」とだけ頼むと、枚数は18枚、"
        "画面に出る文字は平均63字、40字を超えた枚が18枚中15枚、口で言うことは"
        "画面と分かれておらず、裏を取れていない他社の話も画面に載った。"
        "枚数と画面の字数と口頭の分離を指定すると、枚数は9枚、画面の文字は平均17字、"
        "40字超は9枚中0枚、口で言うことは画面の3.9倍になり、裏を取れていない話は"
        "画面から外れた。発表は書いてあることを読むものではないので、"
        "口で言うことのほうが多くなるのが正しい。"
    )
    (OUT / "slides-screen-vs-spoken.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def slides_transcription_chart() -> None:
    """素朴に頼むと、メモの箇条書きが1行1枚に転記されるだけになる図。"""
    left_x, right_x = 18, 384
    box_w = 318
    item_h, gap = 30, 8
    top = 112
    memo_items = ["電話とFAXで確認", "1件12分・1日20件", "二重販売が3件",
                  "謝罪訪問に部長同行", "倉庫も電話60本", "…（全14件）"]
    slide_items = ["1. はじめに", "2. 現状の課題", "3. 業務量の実態",
                   "4. 二重販売の発生", "5. 二重販売の影響", "…（全18枚）"]
    height = top + len(memo_items) * (item_h + gap) - gap + 76
    assert right_x + box_w <= WIDTH - 18, right_x + box_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "構成を考えたのではなく、箇条書きを1行1枚に置き換えただけ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "素材14件に対して18枚。表紙・まとめ・ご清聴の3枚を足すと数が合ってしまう。</text>\n",
        f'<text class="t-xs" x="{left_x + 8}" y="{top - 14}">素材のメモ（箇条書き）</text>\n',
        f'<text class="t-xs" x="{right_x + 8}" y="{top - 14}">返ってきたスライド</text>\n',
    ]
    for index in range(len(memo_items)):
        y = top + index * (item_h + gap)
        mid = y + item_h / 2 + 5
        parts.append(
            f'<rect class="box-quiet" x="{left_x}" y="{y}" '
            f'width="{box_w}" height="{item_h}" rx="5"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left_x + 12}" y="{mid:.0f}">'
            f"{_esc(memo_items[index])}</text>\n"
        )
        parts.append(
            f'<rect class="box-accent" x="{right_x}" y="{y}" '
            f'width="{box_w}" height="{item_h}" rx="5"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{right_x + 12}" y="{mid:.0f}">'
            f"{_esc(slide_items[index])}</text>\n"
        )
        arrow_y = y + item_h / 2
        parts.append(
            f'<line class="link" x1="{left_x + box_w + 8}" y1="{arrow_y}" '
            f'x2="{right_x - 8}" y2="{arrow_y}"/>\n'
        )
    parts.append(
        f'<text class="t-bad" x="18" y="{height - 38}">'
        "1〜7枚目が全部「課題」。聞く側は、何が問題なのかを7回に分けて聞かされる</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 材料を渡した順に並べ替えているだけなので、"
        "「何を承認してほしいのか」が最後まで出てこない。</text>\n"
    )
    alt = (
        "素朴に頼んだときのスライド構成を、素材のメモと並べた図。左が素材の箇条書きで、"
        "電話とFAXで確認、1件12分・1日20件、二重販売が3件、謝罪訪問に部長同行、"
        "倉庫も電話60本と続き全14件。右が返ってきたスライドで、はじめに、現状の課題、"
        "業務量の実態、二重販売の発生、二重販売の影響と続き全18枚。"
        "箇条書きがほぼ1行1枚に置き換えられており、表紙とまとめとご清聴の3枚を足すと"
        "数が合う。1枚目から7枚目までが全部課題の説明で、聞く側は何が問題なのかを"
        "7回に分けて聞かされることになり、何を承認してほしいのかが最後まで出てこない。"
    )
    (OUT / "slides-transcription.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def proofread_scope_chart() -> None:
    """頼み方3種で「直った欠陥」と「守れた語」がどう動くかの実測。

    架空の社内お知らせに、直してほしい欠陥6件（誤字3・冗長3）と、
    触ってほしくない語4件（本件・別紙・稟議・体言止め）を仕込んで測った。
    """
    rows = [
        ("「校正して」", 6, 0, "社内用語が全部消えた"),
        ("「誤字だけ。他は変えるな」", 3, 4, "冗長さが3件とも残った"),
        ("直す種類を列挙＋守る語を宣言", 6, 4, "両方そろった"),
    ]
    label_x, label_w = 18, 206
    unit = 20
    fixed_x = label_x + label_w + 14
    kept_x = fixed_x + 6 * unit + 30
    note_x = kept_x + 4 * unit + 26
    row_h, gap_y = 46, 16
    top = 96
    height = top + len(rows) * (row_h + gap_y) - gap_y + 46
    # 注記のいちばん長い行「冗長さが3件とも残った」11字ぶんの幅を見込む
    assert note_x + 11 * 16 <= WIDTH - 18, note_x + 11 * 16

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "広すぎても狭すぎても駄目。直す種類を名指しするとそろう</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ下書きに、直したい欠陥6件と触ってほしくない語4件を仕込んで測った。</text>\n",
        f'<text class="t-xs" x="{fixed_x}" y="{top - 12}">直った欠陥（6件中）</text>\n',
        f'<text class="t-xs" x="{kept_x}" y="{top - 12}">守れた語（4件中）</text>\n',
    ]
    for index, (name, fixed, kept, note) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        mid = y + row_h / 2 + 5
        good = fixed == 6 and kept == 4
        parts.append(f'<text class="t-sm" x="{label_x}" y="{mid:.0f}">{_esc(name)}</text>\n')
        for start, value, total in ((fixed_x, fixed, 6), (kept_x, kept, 4)):
            parts.append(
                f'<rect class="box-quiet" x="{start}" y="{y}" '
                f'width="{total * unit}" height="{row_h}" rx="6"/>\n'
            )
            if value:
                cls = "box-good" if good else "box-accent"
                parts.append(
                    f'<rect class="{cls}" x="{start}" y="{y}" '
                    f'width="{value * unit}" height="{row_h}" rx="6"/>\n'
                )
            text_cls = "t-good" if good else ("t-bad" if value < total else "t-accent")
            parts.append(
                f'<text class="{text_cls}" x="{start + total * unit + 8}" '
                f'y="{mid:.0f}">{value}</text>\n'
            )
        parts.append(
            f'<text class="{"t-good" if good else "t-bad"}" x="{note_x}" '
            f'y="{mid:.0f}">{_esc(note)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 1行目は誤字が全部直っているので、読むと良くなったように見える。"
        "書き換えは差分を取るまで見えない。</text>\n"
    )
    alt = (
        "校正の頼み方3種を比べた実測の図。下書きに直したい欠陥6件と触ってほしくない語4件を"
        "仕込んで測った。「校正して」とだけ頼むと欠陥は6件すべて直るが、守りたい語は"
        "4件中0件しか残らず、社内用語が全部書き換わった。「誤字だけ。他は変えるな」と頼むと"
        "守りたい語は4件すべて残るが、直った欠陥は6件中3件で冗長さが3件とも残った。"
        "直す種類を列挙して守る語を宣言すると、欠陥6件すべてが直り、守りたい語も4件すべて残った。"
        "1行目は誤字が全部直っているため、読むと良くなったように見え、書き換えは差分を取るまで見えない。"
    )
    (OUT / "proofread-scope.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def proofread_unreported_chart() -> None:
    """「直した箇所の一覧」に載らなかった変更を、実際の差分と突き合わせた図。"""
    reported = 7
    actual = 13
    silent = ["行って下さい", "本件", "別紙", "稟議", "期限厳守。", "お問い合わせいただけますよう"]
    left, unit = 150, 34
    bar_h, gap_y = 44, 18
    top = 92
    list_top = top + 2 * (bar_h + gap_y) + 16
    height = list_top + len(silent) * 26 + 44
    assert left + actual * unit <= WIDTH - 18, left + actual * unit

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「直した箇所」の申告は7件。実際に変わっていたのは13件</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ1回の校正について、申告した一覧と、原文との差分を突き合わせた。</text>\n",
    ]
    for index, (name, value, cls, tcls) in enumerate(
        (("AIの申告", reported, "box-accent", "t-accent"),
         ("実際の差分", actual, "box-bad", "t-bad"))
    ):
        y = top + index * (bar_h + gap_y)
        mid = y + bar_h / 2 + 5
        parts.append(f'<text class="t-sm" x="18" y="{mid:.0f}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" '
            f'width="{value * unit}" height="{bar_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{tcls}" x="{left + value * unit + 10}" '
            f'y="{mid:.0f}">{value}件</text>\n'
        )
    parts.append(
        f'<text class="t-bad" x="18" y="{list_top - 14}">'
        f"申告に載らなかった{len(silent)}件（守りたかった語がここに入っていた）</text>\n"
    )
    for index, word in enumerate(silent):
        parts.append(
            f'<text class="t-sm" x="34" y="{list_top + index * 26 + 12}">'
            f"・{_esc(word)}</text>\n"
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 一覧に出るのは「直した」と自覚したものだけ。"
        "良くしたつもりの書き換えは、本人の申告に出てこない。</text>\n"
    )
    alt = (
        "校正で申告された変更件数と、実際の差分を比べた図。AIが「直した箇所」として"
        "申告したのは7件だったが、原文と突き合わせると実際には13件が変わっていた。"
        "申告に載らなかった6件は、行って下さい、本件、別紙、稟議、期限厳守。、"
        "お問い合わせいただけますよう、で、守りたかった社内用語と体言止めがすべてここに入っていた。"
        "一覧に出るのは直したと自覚したものだけで、良くしたつもりの書き換えは申告に出てこない。"
    )
    (OUT / "proofread-unreported.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def quiz_coverage_chart() -> None:
    """「10問作って」と「条ごとに1問」で、どの条から出題されたかの実測。

    数字は架空の規程7条に対する実測（2026-08-11）。左＝10問まとめて頼んだとき、
    右＝条ごとに最低1問と指定したとき。左は後半2条がゼロになる。
    """
    rows = [
        ("第1条 申請期限", 2, 1),
        ("第2条 領収書", 3, 1),
        ("第3条 会議費", 2, 1),
        ("第4条 出張日当", 2, 1),
        ("第5条 前払金", 1, 1),
        ("第6条 差戻し", 0, 1),
        ("第7条 私的利用", 0, 1),
    ]
    label_x, label_w = 18, 150
    unit = 34  # 1問あたりの幅
    left_x = label_x + label_w + 16
    left_w = 3 * unit  # 最大3問
    right_x = left_x + left_w + 96
    row_h, gap_y = 40, 10
    top = 92
    height = top + len(rows) * (row_h + gap_y) - gap_y + 46
    # 右の帯の右端が画面からはみ出さないこと（幅は推定ではなく計算で出す）
    assert right_x + unit + 120 <= WIDTH - 18, right_x + unit + 120

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「10問作って」だと、後ろの2条から1問も出なかった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の規程7条に対する実測。同じ教材・同じ相手で、頼み方だけを変えた。</text>\n",
        f'<text class="t-xs" x="{left_x}" y="{top - 12}">「10問作って」</text>\n',
        f'<text class="t-xs" x="{right_x}" y="{top - 12}">「条ごとに最低1問ずつ」</text>\n',
    ]
    for index, (name, before, after) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        mid = y + row_h / 2 + 5
        parts.append(f'<text class="t-sm" x="{label_x}" y="{mid:.0f}">{_esc(name)}</text>\n')
        if before:
            parts.append(
                f'<rect class="box-quiet" x="{left_x}" y="{y}" '
                f'width="{before * unit}" height="{row_h}" rx="6"/>\n'
            )
            parts.append(
                f'<text class="t" x="{left_x + before * unit / 2 - 8:.0f}" '
                f'y="{mid:.0f}">{before}</text>\n'
            )
        else:
            parts.append(
                f'<rect class="box-bad" x="{left_x}" y="{y}" '
                f'width="{unit * 3}" height="{row_h}" rx="6"/>\n'
            )
            parts.append(
                f'<text class="t-bad" x="{left_x + 14}" y="{mid:.0f}">0問（出題なし）</text>\n'
            )
        parts.append(
            f'<rect class="box-good" x="{right_x}" y="{y}" '
            f'width="{after * unit}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-good" x="{right_x + after * unit / 2 - 8:.0f}" '
            f'y="{mid:.0f}">{after}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 落ちた2条は、差し戻し後の再申請期限と、私的利用が混ざったときの扱い。"
        "実務で一番困る側から落ちている。</text>\n"
    )
    alt = (
        "出題された条を、頼み方2種類で比べた図。「10問作って」と頼むと、"
        "第1条2問・第2条3問・第3条2問・第4条2問・第5条1問と前半に集まり、"
        "第6条（差戻し）と第7条（私的利用）は0問で出題されなかった。"
        "「条ごとに最低1問ずつ」と指定すると、第1条から第7条まですべて1問ずつ出題された。"
        "落ちた2条は差し戻し後の再申請期限と私的利用が混ざったときの扱いで、"
        "実務で一番困る側から落ちている。"
    )
    (OUT / "quiz-coverage.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def quiz_three_leaks_chart() -> None:
    """出題させたときに起きる3つの漏れと、それぞれを止める一言。"""
    rows = [
        ("出ない", "後ろの条から1問も出ない", "条ごとに最低1問ずつ出して"),
        ("無い話", "教材に無い言葉で出題する", "書いてあることだけから出して"),
        ("理由違い", "正解だが根拠が別の条", "根拠の一文をそのまま引用して"),
    ]
    tag_x, tag_w = 18, 108
    mid_x = tag_x + tag_w + 18
    mid_w = 252
    fix_x = mid_x + mid_w + 18
    fix_w = WIDTH - 18 - fix_x
    row_h, gap_y = 62, 16
    top = 88
    height = top + len(rows) * (row_h + gap_y) - gap_y + 46
    assert fix_w >= 260, fix_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "出題させると漏れは3種類。どれも一言で止まる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の規程で実際に出題させて出たもの。3つとも原文と突き合わせて確かめた。</text>\n",
        f'<text class="t-xs" x="{mid_x}" y="{top - 10}">何が起きるか</text>\n',
        f'<text class="t-xs" x="{fix_x}" y="{top - 10}">足す一言</text>\n',
    ]
    for index, (tag, what, fix) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        mid = y + row_h / 2 + 5
        parts.append(
            f'<rect class="box-bad" x="{tag_x}" y="{y}" '
            f'width="{tag_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t-bad" x="{tag_x + 14}" y="{mid:.0f}">{_esc(tag)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{mid_x}" y="{y}" '
            f'width="{mid_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t" x="{mid_x + 14}" y="{mid:.0f}">{_esc(what)}</text>\n')
        parts.append(
            f'<rect class="box-good" x="{fix_x}" y="{y}" '
            f'width="{fix_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t-good" x="{fix_x + 14}" y="{mid:.0f}">{_esc(fix)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 3つ目がいちばん見つけにくい。答えが合っているので、読んでも気づけない。</text>\n"
    )
    alt = (
        "出題させたときに起きる3つの漏れと、それぞれを止める一言をまとめた図。"
        "1つ目は「出ない」＝後ろの条から1問も出ないので、「条ごとに最低1問ずつ出して」と足す。"
        "2つ目は「無い話」＝教材に無い言葉で出題するので、「書いてあることだけから出して」と足す。"
        "3つ目は「理由違い」＝正解だが根拠が別の条なので、「根拠の一文をそのまま引用して」と足す。"
        "3つ目は答えが合っているため、読んでも気づけない。"
    )
    (OUT / "quiz-three-leaks.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def table_average_pulled_chart() -> None:
    """誤入力が1つ混ざると平均がどこまで動くかを、数直線で見せる。"""
    normal = [44800, 45300, 46300, 46800, 47100, 49200, 50100, 51400, 55600, 58900, 61200]
    median = 49650
    mean_with = 86558
    mean_without = 50609
    axis_max = 100000
    left, right = 118, 628
    span = right - left
    axis_y = 152
    height = 258

    def x_of(value: int) -> float:
        return left + span * value / axis_max

    parts = [
        '<text class="t-strong" x="18" y="26">誤入力が1つ入ると、平均はここまで動く</text>\n',
        '<text class="t-sm" x="18" y="45">'
        "東京の12か月。9月だけ 482,000（この目盛りの外）が入っている。</text>\n",
    ]
    # 平均・中央値の目印（縦線なので文字を貫かない）
    parts.append(
        f'<line class="line" x1="{x_of(median):.1f}" y1="112" '
        f'x2="{x_of(median):.1f}" y2="{axis_y + 12}"/>\n'
    )
    parts.append(
        f'<line class="line" x1="{x_of(mean_with):.1f}" y1="112" '
        f'x2="{x_of(mean_with):.1f}" y2="{axis_y + 12}"/>\n'
    )
    parts.append(
        f'<text class="t-accent" x="{x_of(median) - 62:.1f}" y="102">中央値 49,650</text>\n'
    )
    parts.append(
        f'<text class="t-bad" x="{x_of(mean_with) - 56:.1f}" y="102">平均 86,558</text>\n'
    )
    # 数直線
    parts.append(
        f'<line class="line" x1="{left}" y1="{axis_y}" x2="{right}" y2="{axis_y}"/>\n'
    )
    for value in normal:
        parts.append(
            f'<circle cx="{x_of(value):.1f}" cy="{axis_y}" r="5" class="bar-out"/>\n'
        )
    for tick in (0, 50000, 100000):
        tx = x_of(tick)
        parts.append(
            f'<line class="line" x1="{tx:.1f}" y1="{axis_y}" x2="{tx:.1f}" y2="{axis_y + 7}"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{tx - 18:.1f}" y="{axis_y + 22}">{tick:,}</text>\n'
        )
    parts.append(f'<text class="t-sm" x="18" y="{axis_y - 14}">9月以外の11か月</text>\n')
    parts.append(
        f'<text class="t" x="18" y="{height - 32}">'
        f"9月を除いた平均は {mean_without:,}。9月を入れると {mean_with:,} まで動く。</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="18" y="{height - 12}">'
        "この結果、12か月のうち11か月が「平均より下」になる。</text>\n"
    )
    alt = (
        "東京支店の月次売上12か月を数直線に並べた図。9月を除く11か月は44,800から61,200の間に"
        "かたまっていて、中央値は49,650。9月だけ482,000という誤入力が入っており、"
        "目盛りの外にあるため図には点として出ていない。"
        "その1つのせいで平均は50,609から86,558まで右へ動き、"
        "12か月のうち11か月が平均より下という状態になる。"
        "平均を基準に異常を探すと、この動いた平均が基準になってしまう。"
    )
    (OUT / "table-average-pulled.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def tool_only_here_chart() -> None:
    """4社の公式ページで、1社しか書いていなかったもの。

    ⚠️ 「他社にできない」ではなく「調べた範囲で1社しか書いていない」。
    他社が黙っているだけかもしれないし、来月には並ぶ。日付が本体。
    出典＝x.ai/grok・claude.com/product/claude-code・gemini.google/overview/・
    help.openai.com（2026-08-10 に各社の公式ページで確認）。
    """
    rows = [
        ("ChatGPT", "会議やメモを録音して、そのまま要約させる",
         "公式ヘルプに「ChatGPT Record」の項目がある"),
        ("Claude", "手元のパソコンのファイルを直接書き換えさせる",
         "ターミナル・VS Code・Slack から動く（Claude Code）"),
        ("Gemini", "音楽をつくる／Gmail やドライブの中身を読ませる",
         "公式の「できること」に音楽生成と Workspace 連携が並ぶ"),
        ("Grok", "X（旧Twitter）で、いま起きていることを読ませる",
         "同じ会社が X を持っている"),
    ]
    top, row_h, box_h = 96, 76, 64
    height = top + len(rows) * row_h + 44

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "4社のうち、1社しか書いていなかったこと</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "2026年8月10日に、各社の公式ページで確認できた範囲です。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「他社にはできない」ではありません。書いていないだけかもしれず、来月には並びます。</text>\n",
    ]
    for index, (name, what, why) in enumerate(rows):
        y = top + index * row_h
        parts.append(
            f'<rect class="box-accent" x="18" y="{y}" '
            f'width="{WIDTH - 36}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t-strong" x="32" y="{y + 26}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t" x="190" y="{y + 26}">{_esc(what)}</text>\n')
        parts.append(f'<text class="t-sm" x="190" y="{y + 48}">{_esc(why)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 4社とも、文章・画像・ウェブ検索・音声はどれもできます。違いはその外側に出ます。</text>\n"
    )
    alt = (
        "4つのAIツールについて、2026年8月10日に各社の公式ページで確認した範囲で、"
        "1社しか書いていなかった機能を並べた図。"
        "ChatGPT は会議やメモを録音してそのまま要約させること（公式ヘルプに ChatGPT Record の項目がある）。"
        "Claude は手元のパソコンのファイルを直接書き換えさせること"
        "（ターミナル・VS Code・Slack から動く Claude Code）。"
        "Gemini は音楽をつくることと、Gmail やドライブの中身を読ませること"
        "（公式のできること一覧に音楽生成と Workspace 連携が並ぶ）。"
        "Grok は X（旧Twitter）でいま起きていることを読ませること（同じ会社が X を持っている）。"
        "これは他社にできないという意味ではなく、書いていないだけかもしれず、来月には並ぶ。"
        "4社とも文章・画像・ウェブ検索・音声はどれもできる。"
    )
    (OUT / "tool-only-here.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def translate_hidden_issues_chart() -> None:
    """訳文だけを見ても気づけない返りを5種類に分けて並べる。

    右列は「原文と突き合わせないと見えないか」。5つのうち4つが見えない側に入る
    ＝訳文の日本語を読む検査では素通りする、というのがこの図の主張。
    """
    rows = [
        ("用語の揺れ", "workspace と work area が別の日本語になる", True),
        ("足された助言", "原文に無い「おすすめします」が1文増える", True),
        ("日付の断定", "3/4/2026 を確認せずに1つの日付に決める", True),
        ("時差の換算", "9:00 AM PT の換算が1時間ずれる", True),
        ("文体の混在", "です・ます体と体言止めが混ざる", False),
    ]
    pad = 18
    name_w, mid_w, gap = 132, 330, 16
    box_h, gap_y = 46, 12
    name_x = pad
    mid_x = name_x + name_w + gap
    right_x = mid_x + mid_w + gap
    top = 84
    height = top + len(rows) * (box_h + gap_y) - gap_y + 42
    assert right_x + 150 <= WIDTH - pad, right_x

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "訳したあとに残るものは、5つのうち4つが訳文からは見えない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "日本語として読みやすいかを確かめても素通りします。原文と並べないと出てきません。</text>\n",
    ]
    for index, (name, example, hidden) in enumerate(rows):
        y = top + index * (box_h + gap_y)
        mid = y + box_h / 2 + 5
        parts.append(
            f'<rect class="{"box-bad" if hidden else "box-accent"}" x="{name_x}" y="{y}" '
            f'width="{name_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{"t-bad" if hidden else "t-accent"}" x="{name_x + 14}" '
            f'y="{mid:.0f}">{_esc(name)}</text>\n'
        )
        parts.append(
            f'<rect class="box-quiet" x="{mid_x}" y="{y}" '
            f'width="{mid_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t" x="{mid_x + 14}" y="{mid:.0f}">{_esc(example)}</text>\n'
        )
        parts.append(
            f'<text class="{"t-bad" if hidden else "t-sm"}" x="{right_x}" y="{mid:.0f}">'
            f'{"訳文からは見えない" if hidden else "読めば気づく"}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 上の4つは、訳文だけが手元にある人には見つけられません。原文を持っている人が確かめる作業です。</text>\n"
    )
    alt = (
        "訳したあとに残る問題を5種類に分けた図。"
        "用語の揺れ（workspace と work area が別の日本語になる）、"
        "足された助言（原文に無い「おすすめします」が1文増える）、"
        "日付の断定（3/4/2026 を確認せずに1つの日付に決める）、"
        "時差の換算（9:00 AM PT の換算が1時間ずれる）の4つは、"
        "訳文だけを読んでも見えない。"
        "文体の混在（です・ます体と体言止めが混ざる）だけは読めば気づく。"
        "上の4つは訳文だけが手元にある人には見つけられず、原文を持っている人が確かめる作業になる。"
    )
    (OUT / "translate-hidden-issues.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def translate_three_steps_chart() -> None:
    """訳す前・訳すとき・訳したあとで、それぞれ何を指定するか。"""
    columns = [
        ("訳す前に決める", ["揺れる言葉を表にする", "訳さない語を決める", "文体を1つに決める"], "box-accent", "t-accent"),
        ("訳すときに縛る", ["原文に無いことを足さない", "迷ったら訳さず報告する", "段落に番号を振る"], "box", "t-strong"),
        ("訳したあとに測る", ["数字を並べて突き合わせる", "用語表どおりか確かめる", "原文に無い文を探させる"], "box-good", "t-good"),
    ]
    pad, gap = 18, 16
    col_w = (WIDTH - pad * 2 - gap * (len(columns) - 1)) // len(columns)
    head_y, first_y, row_h = 88, 122, 30
    rows = max(len(items) for _, items, _, _ in columns)
    box_h = 34 + rows * row_h
    band_y, band_h = head_y - 22 + box_h + 20, 54
    height = band_y + band_h + 34
    assert pad + len(columns) * col_w + (len(columns) - 1) * gap <= WIDTH - pad

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "指定する場所は3つに分かれる。前の1つを飛ばすと、直しが全文に及ぶ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "用語と文体は、訳し終わってから直すと全部の段落を触ることになります。</text>\n",
    ]
    for index, (title, items, box_cls, text_cls) in enumerate(columns):
        x = pad + index * (col_w + gap)
        parts.append(
            f'<rect class="{box_cls}" x="{x}" y="{head_y - 22}" '
            f'width="{col_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{text_cls}" x="{x + 14}" y="{head_y}">{_esc(title)}</text>\n'
        )
        for row, item in enumerate(items):
            parts.append(
                f'<text class="t" x="{x + 14}" y="{first_y + row * row_h}">{_esc(item)}</text>\n'
            )
    parts.append(
        f'<rect class="box-quiet" x="{pad}" y="{band_y}" '
        f'width="{WIDTH - pad * 2}" height="{band_h}" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t" x="{pad + 14}" y="{band_y + 22}">'
        "左の3つは、訳す前なら1回書けば全文に効きます。</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="{pad + 14}" y="{band_y + 42}">'
        "右の3つは、原文と訳文の両方を渡さないとできません。訳文だけを渡しても答えは返りません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 真ん中の「段落に番号を振る」は、右の突き合わせを機械的にするための下ごしらえです。</text>\n"
    )
    alt = (
        "翻訳をAIに頼むときの指定を、3つの場所に分けた図。"
        "訳す前に決めるのは、揺れる言葉を表にする・訳さない語を決める・文体を1つに決める、の3つ。"
        "訳すときに縛るのは、原文に無いことを足さない・迷ったら訳さず報告する・段落に番号を振る、の3つ。"
        "訳したあとに測るのは、数字を並べて突き合わせる・用語表どおりか確かめる・原文に無い文を探させる、の3つ。"
        "左の3つは訳す前なら1回書けば全文に効く。"
        "右の3つは原文と訳文の両方を渡さないとできず、訳文だけを渡しても答えは返らない。"
        "真ん中の段落に番号を振る指定は、右の突き合わせを機械的にするための下ごしらえ。"
    )
    (OUT / "translate-three-steps.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def summary_what_drops_chart() -> None:
    """素朴に「要約して」と頼んだとき、何が残って何が落ちたか。

    実測（2026-08-11・架空の社内通知2,192字・落としてはいけない情報14件を先に決めた）。
    判定は Python の文字列照合。要約Aは458字で 4/14 が残った。
    """
    kept = [
        "9月1日に新システム稼働",
        "8月28日18:00が締切",
        "45時間超は事前申請",
        "交通費の上限35,000円",
    ]
    lost = [
        ("ただし書き", "残業申請は9月4日まで"),
        ("ただし書き", "管理職1名なら承認1名"),
        ("ただし書き", "新幹線通勤は据え置き"),
        ("条件", "スマホ打刻は社内Wi-Fiのみ"),
        ("禁止", "移行3日間は打刻しない"),
        ("対象外", "警備担当の契約社員12名"),
        ("作業", "3日以内にパスワード変更"),
        ("結果", "未変更は9月8日に停止"),
        ("期限", "旧データは2027年3月に削除"),
        ("窓口", "電話では受け付けない"),
    ]
    left_x, right_x, col_w = 18, 372, 330
    row_h, gap_y = 30, 8
    top = 96
    height = top + len(lost) * (row_h + gap_y) - gap_y + 44
    assert right_x + col_w <= WIDTH - 18, right_x + col_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「次の文書を要約してください」だけで頼んだとき、何が残ったか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "落としてはいけない情報14件を先に決めてから要約させ、機械で1件ずつ照合した。</text>\n",
        f'<text class="t-good" x="{left_x}" y="{top - 14}">残った　4件</text>\n',
        f'<text class="t-bad" x="{right_x}" y="{top - 14}">落ちた　10件</text>\n',
    ]
    for index, label in enumerate(kept):
        y = top + index * (row_h + gap_y)
        parts.append(
            f'<rect class="box-good" x="{left_x}" y="{y}" '
            f'width="{col_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-good" x="{left_x + 12}" y="{y + 20}">{_esc(label)}</text>\n'
        )
    note_y = top + len(kept) * (row_h + gap_y) + 12
    parts.append(
        f'<text class="t-xs" x="{left_x}" y="{note_y}">'
        "残ったのは、文書の主語が大きい話ばかり。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="{left_x}" y="{note_y + 18}">'
        "「誰に効くか」「いつまでか」は右へ移った。</text>\n"
    )
    for index, (kind, label) in enumerate(lost):
        y = top + index * (row_h + gap_y)
        parts.append(
            f'<rect class="box-bad" x="{right_x}" y="{y}" '
            f'width="{col_w}" height="{row_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{right_x + 12}" y="{y + 20}">{_esc(kind)}</text>\n'
        )
        parts.append(
            f'<text class="t-bad" x="{right_x + 78}" y="{y + 20}">{_esc(label)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 原文54文のうち、ただし書き・禁止・対象外を含む文は10文。"
        "そのうち要約に残ったのは0文だった。</text>\n"
    )
    alt = (
        "素朴に「要約してください」と頼んだときに、何が残って何が落ちたかを並べた図。"
        "教材は架空の社内通知で、落としてはいけない情報を14件、先に決めてある。"
        "残ったのは4件で、9月1日に新システム稼働、8月28日18時が締切、"
        "45時間超は事前申請、交通費の上限35,000円。"
        "落ちたのは10件で、ただし書きが3件（残業申請は9月4日まで、"
        "管理職1名なら承認1名、新幹線通勤は据え置き）、"
        "条件が1件（スマホ打刻は社内Wi-Fiのみ）、禁止が1件（移行3日間は打刻しない）、"
        "対象外が1件（警備担当の契約社員12名）、自分の作業が1件（3日以内にパスワード変更）、"
        "結果が1件（未変更は9月8日に停止）、期限が1件（旧データは2027年3月に削除）、"
        "窓口が1件（電話では受け付けない）。"
        "残ったのは主語が大きい話ばかりで、誰に効くか・いつまでかは落ちている。"
        "原文54文のうち、ただし書き・禁止・対象外を含む文は10文あったが、"
        "そのうち要約に残ったものは0文だった。"
    )
    (OUT / "summary-what-drops.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def summary_length_vs_keep_chart() -> None:
    """要約の長さと、残った件数の関係。長さのせいではないことを見せる。

    実測（2026-08-11・同じ原文2,192字・落としてはいけない情報14件）。
    字数は空白を除いて数えた。
    """
    rows = [
        ("「要約してください」", 458, 4, False),
        ("「大事なところを落とさずに」", 511, 5, False),
        ("「200字以内で要約して」", 196, 5, False),
        ("6種類を名指し＋400字以内", 417, 14, True),
    ]
    total = 14
    label_x, label_w = 18, 210
    bar_x, bar_max = 236, 340
    row_h, gap_y = 30, 20
    top = 104
    height = top + len(rows) * (row_h + gap_y) - gap_y + 52
    assert bar_x + bar_max + 126 <= WIDTH - 18, bar_x + bar_max + 126

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "落ちるのは、長さが足りないからではない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ原文（2,192字）。落としてはいけない情報14件のうち、いくつ残ったか。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">残った件数（14件中）</text>\n',
        f'<text class="t-xs" x="{bar_x + bar_max + 16}" y="{top - 12}">要約の長さ</text>\n',
    ]
    for index, (name, chars, kept, best) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        width = round(bar_max * kept / total)
        parts.append(
            f'<text class="t-sm" x="{label_x}" y="{y + 20}">{_esc(name)}</text>\n'
        )
        parts.append(
            f'<rect class="bar-old" x="{bar_x}" y="{y + 4}" '
            f'width="{bar_max}" height="{row_h - 8}" rx="3" opacity="0.35"/>\n'
        )
        klass = "bar-new" if best else "bar-in"
        parts.append(
            f'<rect class="{klass}" x="{bar_x}" y="{y + 4}" '
            f'width="{width}" height="{row_h - 8}" rx="3"/>\n'
        )
        value_class = "t-accent" if best else "t-sm"
        parts.append(
            f'<text class="{value_class}" x="{bar_x + width + 10}" y="{y + 20}">'
            f"{kept}件</text>\n"
        )
        parts.append(
            f'<text class="t-sm" x="{bar_x + bar_max + 16}" y="{y + 20}">{chars}字</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 32}">'
        "※ いちばん下は、いちばん上より41字短い。それでも14件すべて残っている。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※「400字以内」は守られず417字だった（4%超過）。字数は目安として効くが、"
        "上限としては当てにできない。</text>\n"
    )
    alt = (
        "要約の長さと、落としてはいけない情報が残った件数を並べた図。"
        "同じ原文2,192字を、落としてはいけない情報14件を先に決めたうえで要約させた。"
        "「要約してください」とだけ頼むと458字で4件しか残らない。"
        "「大事なところを落とさずに」と足すと511字になるが、残ったのは5件で1件しか増えない。"
        "「200字以内で要約して」は196字で5件。"
        "落とさない6種類を名指ししたうえで400字以内と指定すると、417字で14件すべて残った。"
        "いちばん下は、いちばん上より41字短いのに全部残っている。"
        "つまり落ちる原因は長さではなく、何を残すかを決めていないこと。"
        "なお400字以内という指定は守られず417字で、4%超過していた。"
        "字数は目安として効くが、上限としては当てにできない。"
    )
    (OUT / "summary-length-vs-keep.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def files_naive_outcome_chart() -> None:
    """「このファイル一覧を整理して」だけで頼んだとき、45件がどこへ行ったか。

    実測（2026-08-11・架空の散らかったフォルダ45件）。
    出力に名前がそのまま出たかを Python で照合した（長い名前から先に消して誤ヒットを防いだ）。
    """
    segments = [
        ("移動先が示された", 22, "bar-in"),
        ("削除を提案された", 14, "bar-old"),
        ("名前が一度も出てこない", 9, "box-bad"),
    ]
    total = sum(count for _, count, _ in segments)
    bar_x, bar_w, bar_y, bar_h = 18, 666, 84, 34
    top = 152
    row_h, gap_y = 30, 10
    height = top + len(segments) * (row_h + gap_y) - gap_y + 62
    assert bar_x + bar_w <= WIDTH - 18, bar_x + bar_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「このファイル一覧を整理してください」だけで頼んだとき、45件はどこへ行ったか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の散らかったフォルダ45件。返ってきた提案に名前がそのまま出たかを機械で数えた。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{bar_y - 10}">45件の内訳</text>\n',
    ]
    x = bar_x
    for label, count, klass in segments:
        width = round(bar_w * count / total)
        parts.append(
            f'<rect class="{klass}" x="{x}" y="{bar_y}" '
            f'width="{width}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{x + 10}" y="{bar_y + 22}">{count}件</text>\n'
        )
        x += width
    for index, (label, count, klass) in enumerate(segments):
        y = top + index * (row_h + gap_y)
        box = {"bar-in": "box-accent", "bar-old": "box-quiet", "box-bad": "box-bad"}[klass]
        text_class = {"bar-in": "t", "bar-old": "t-sm", "box-bad": "t-bad"}[klass]
        parts.append(
            f'<rect class="{box}" x="18" y="{y}" width="666" height="{row_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="{text_class}" x="30" y="{y + 20}">{_esc(label)}　{count}件</text>\n'
        )
        note = {
            22: "この22件だけを見ていると、全部さばけたように読める",
            14: "うち名前だけで確実に判定できるのは3件。残り11件は名前からの推測",
            9: "「スクリーンショット5点」「など」に丸められて、一覧から消えた",
        }[count]
        parts.append(f'<text class="t-xs" x="286" y="{y + 20}">{_esc(note)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 32}">'
        "※ いちばん下の9件が問題。提案の中に「5点」と書いてあるので、"
        "読んでも抜けたことに気づけない。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 削除を提案された14件には、更新日時では最も新しいファイルが含まれていた"
        "（名前の「最終_確定」を信じたため）。</text>\n"
    )
    alt = (
        "「このファイル一覧を整理してください」とだけ頼んだときに、"
        "45件のファイルがどこへ行ったかを示した図。"
        "移動先が示されたものが22件、削除を提案されたものが14件、"
        "名前が一度も出てこなかったものが9件。"
        "移動先が示された22件だけを見ていると、全部さばけたように読める。"
        "削除を提案された14件のうち、名前だけで確実に判定できるのは3件で、"
        "残り11件は名前からの推測にすぎない。"
        "名前が出てこなかった9件は、スクリーンショット5点、などという書き方に丸められて"
        "一覧から消えた。提案の中に5点と書いてあるので、読んでも抜けたことに気づけない。"
        "また削除を提案された14件には、更新日時では最も新しいファイルが含まれていた。"
        "名前についている最終_確定という語を信じたため。"
    )
    (OUT / "files-naive-outcome.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def files_decidable_chart() -> None:
    """名前だけで決まるものと、決まらないもの。決まらないものは「何を見れば決まるか」で割る。

    実測（2026-08-11・同じ45件）。全件を1行ずつ出させ、判断できないものは
    「判断できない」に入れるよう指定した結果。45行が45行のまま返った。
    """
    first = ("名前だけで移動先が決まった", 26)
    reasons = [
        ("開いて中身を見れば決まる", 15, "スクショ5・写真2・領収書2・無題3・メモ3"),
        ("プロパティの発行元を見れば決まる", 2, "setup.exe と setup (1).exe"),
        ("社内規程を見れば決まる", 1, "社員名簿（個人情報を含む）"),
        ("Excelを閉じれば決まる", 1, "~$ で始まる一時ファイル"),
    ]
    total = 45
    label_x = 18
    bar_x, bar_max = 230, 150
    count_x = bar_x + bar_max + 14
    note_x = count_x + 46
    row_h = 28
    assert note_x + 240 <= WIDTH - 18, note_x

    top = 96
    header2_y = top + row_h + 34
    rows_top = header2_y + 14
    gap_y = 12
    height = rows_top + len(reasons) * (row_h + gap_y) - gap_y + 46

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「全部の行を出して。決まらないものは判断できないに入れて」と頼んだ結果</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ45件。45行が45行のまま返り、勝手に消えたファイルも作られたファイルも無かった。</text>\n",
        f'<text class="t-good" x="{label_x}" y="{top - 12}">自分が開かなくてよいもの</text>\n',
    ]
    width = round(bar_max * first[1] / total)
    parts.append(
        f'<text class="t-sm" x="{label_x}" y="{top + 19}">{_esc(first[0])}</text>\n'
    )
    parts.append(
        f'<rect class="bar-new" x="{bar_x}" y="{top + 3}" '
        f'width="{width}" height="{row_h - 6}" rx="3"/>\n'
    )
    parts.append(
        f'<text class="t-accent" x="{count_x}" y="{top + 19}">{first[1]}件</text>\n'
    )
    parts.append(
        f'<text class="t-bad" x="{label_x}" y="{header2_y}">'
        "名前だけでは決まらない　19件　←　ここだけ自分で見る</text>\n"
    )
    for index, (label, count, note) in enumerate(reasons):
        y = rows_top + index * (row_h + gap_y)
        width = round(bar_max * count / total)
        parts.append(
            f'<text class="t-sm" x="{label_x}" y="{y + 19}">{_esc(label)}</text>\n'
        )
        parts.append(
            f'<rect class="bar-in" x="{bar_x}" y="{y + 3}" '
            f'width="{max(width, 3)}" height="{row_h - 6}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{count_x}" y="{y + 19}">{count}件</text>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{note_x}" y="{y + 19}">{_esc(note)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 45件を全部開く代わりに、19件だけ開けばよくなる。"
        "「判断できない」を用意しないと、この19件は推測で振り分けられる。</text>\n"
    )
    alt = (
        "全部の行を出させ、決まらないものは判断できないに入れるよう頼んだ結果の図。"
        "同じ45件のファイル一覧を使い、45行が45行のまま返り、"
        "勝手に消えたファイルも作られたファイルも無かった。"
        "名前だけで移動先が決まったものが26件。"
        "名前だけでは決まらないものが19件で、この19件だけを自分で見ればよい。"
        "その内訳は、開いて中身を見れば決まるものが15件"
        "（スクリーンショット5点、写真2点、領収書2点、無題のファイル3点、メモ3点）、"
        "プロパティの発行元を見れば決まるものが2件（setup.exe と setup (1).exe）、"
        "社内規程を見れば決まるものが1件（個人情報を含む社員名簿）、"
        "Excelを閉じれば決まるものが1件（チルダとドル記号で始まる一時ファイル）。"
        "45件を全部開く代わりに19件だけ開けばよくなる。"
        "判断できないという行き先を用意しないと、この19件は推測で振り分けられる。"
    )
    (OUT / "files-decidable.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    price_chart()
    changed_chart()
    tokenizer_chart()
    filler_before_after()
    line_count_chart()
    summary_vs_raw_chart()
    citation_chain_chart()
    queue_flow_chart()
    write_or_stop_chart()
    gemini36_lineup()
    gemini36_cheap_price_chart()
    gemini36_generation_chart()
    gemini36_bench_chart()
    class_scrape_chart()
    silent_zero_chart()
    figure_checks_chart()
    check_blindspot_chart()
    feels_off_chart()
    delegate_types_chart()
    life_paperwork_chart()
    fun_iteration_chart()
    batch_vs_one_chart()
    meeting_outputs_chart()
    sourced_research_chart()
    gpt56_family_chart()
    mail_triage_chart()
    report_split_chart()
    handoff_timing_chart()
    scope_weight_chart()
    start_requirements_chart()
    start_boundary_chart()
    table_anomaly_types_chart()
    table_average_pulled_chart()
    tool_only_here_chart()
    translate_hidden_issues_chart()
    translate_three_steps_chart()
    quiz_coverage_chart()
    quiz_three_leaks_chart()
    proofread_scope_chart()
    proofread_unreported_chart()
    slides_screen_vs_spoken_chart()
    slides_transcription_chart()
    menu_constraints_chart()
    menu_stock_usage_chart()
    report_facts_lost_chart()
    report_template_overwrite_chart()
    summary_what_drops_chart()
    summary_length_vs_keep_chart()
    files_naive_outcome_chart()
    files_decidable_chart()
    print(f"50枚を {OUT} に出力しました")
