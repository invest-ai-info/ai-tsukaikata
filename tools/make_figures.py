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



def estimate_range_naive_vs_log_chart() -> None:
    """「聞いただけ」と「自分の記録を貼った」で、返ってきた見積もりの幅を並べる。

    実測（2026-08-15・架空の案件1件と架空の作業記録3本）。
    帯は返りに書いてあった合計をそのまま分に直したもの。
    縦の点線は、記録に実際に残っている2本の合計（675分・725分）。
    """
    lo_axis, hi_axis = 540, 1020  # 9時間〜17時間
    plot_x, plot_w = 190, 500
    scale = plot_w / (hi_axis - lo_axis)

    def px(minutes: float) -> float:
        return plot_x + (minutes - lo_axis) * scale

    groups = [
        ("記録を渡さずに聞いた（3回）", "bar-old", [
            ("1回目　10〜16時間", 600, 960),
            ("2回目　12〜16時間", 720, 960),
            ("3回目　10〜13時間", 600, 780),
        ]),
        ("自分の作業記録を貼った（3回）", "bar-new", [
            ("1回目　670〜765分", 670, 765),
            ("2回目　660〜770分", 660, 770),
            ("3回目　665〜755分", 665, 755),
        ]),
    ]
    actual = [675, 725]

    top = 118
    pitch, bar_h = 26, 18
    rows = sum(1 + len(items) for _, _, items in groups)
    plot_bottom = top + rows * pitch
    axis_y = plot_bottom + 8
    height = axis_y + 24 + 24 + 22 + 22 + 16

    assert px(hi_axis) + 18 <= WIDTH, px(hi_axis)

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ仕事の見積もり。聞いただけだと 10〜16時間、記録を貼ると 11.0〜12.8時間</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の案件1件（5,000字・未経験の分野）に、同じ指示文を3回ずつ通した実測。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "帯は、返ってきた合計そのまま。縦の点線は、記録に実際に残っている2本の合計。</text>\n",
        f'<text class="t-xs" x="{px(actual[1]) + 10:.1f}" y="{top - 8}">'
        "← 実際にかかった2本（675分・725分）</text>\n",
    ]

    for minutes in actual:
        x = px(minutes)
        parts.append(
            f'<path class="line" d="M{x:.1f} {top - 2} L{x:.1f} {plot_bottom - 4}" '
            f'stroke-dasharray="4 3"/>\n'
        )

    y = top
    for title, klass, items in groups:
        parts.append(f'<text class="t-accent" x="18" y="{y + 14}">{_esc(title)}</text>\n')
        y += pitch
        for label, lo, hi in items:
            left, right = px(lo), px(hi)
            parts.append(
                f'<text class="t-sm" x="18" y="{y + 14}">{_esc(label)}</text>\n'
            )
            parts.append(
                f'<rect class="{klass}" x="{left:.1f}" y="{y + 1}" '
                f'width="{right - left:.1f}" height="{bar_h}" rx="3"/>\n'
            )
            y += pitch

    parts.append(
        f'<path class="line" d="M{plot_x} {axis_y} L{px(hi_axis):.1f} {axis_y}"/>\n'
    )
    for hours in (10, 12, 14, 16):
        x = px(hours * 60)
        parts.append(
            f'<path class="line" d="M{x:.1f} {axis_y} L{x:.1f} {axis_y + 5}"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{x - 16:.1f}" y="{axis_y + 20}">{hours}時間</text>\n'
        )

    parts.append(
        f'<text class="t-xs" x="18" y="{height - 60}">'
        "※ 3回を合わせた開きは 6.00時間 と 1.83時間。記録を貼ると 3.27倍せまくなった。</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="18" y="{height - 38}">'
        "※ 上の3回は、何をもとにした数字かが1行も書かれていない。聞き直すと3回とも「推測です」と返る。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。</text>\n"
    )

    alt = (
        "同じ案件の見積もりを、記録を渡さずに聞いた3回と、自分の作業記録を貼って聞いた3回で"
        "比べた図。渡さない3回は10〜16時間・12〜16時間・10〜13時間とばらつき、"
        "記録を貼った3回は670〜765分・660〜770分・665〜755分にそろった。"
        "記録に実際に残っている2本の合計675分と725分は、貼った3回の帯の内側にある。"
    )
    (OUT / "estimate-range-naive-vs-log.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def list_work_not_delivery_chart() -> None:
    """集めた25件が「納品できる7件」と「自分が確かめる11件」に割れる図。

    実測（2026-08-15・架空の候補25行）。真値は材料から計算した。
    同じ指示文を3回通して、3回とも同じ割れ方になった。
    """
    segments = [
        ("確かめられた", 7, "bar-new", "3条件とも○。このまま出せる"),
        ("自分で確かめる", 11, "bar-in", "従業員数が空欄。○とも×とも言えない"),
        ("重複の疑い", 1, "bar-old", "同じ社名の表記ゆれ"),
        ("条件から外れる", 6, "bar-old", "100人超3件・別業種2件・関東外1件"),
    ]
    total = sum(n for _, n, _, _ in segments)
    plot_x, plot_w = 18, 684
    unit = plot_w / total
    bar_y, bar_h = 122, 40

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「20件そろえて」と言われた仕事。条件を○にできたのは 7件だった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の候補25行を渡して、同じ指示文を3回。3回とも同じ7件・11件・6件・重複1件に割れた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "3回とも「20件は作れません」と断り、数をそろえるために条件外を混ぜた回は0回。</text>\n",
    ]

    # 20件目の位置（ここに線を引くと、条件から外れる側に入る）
    x20 = plot_x + 20 * unit
    parts.append(
        f'<text class="t-bad" x="{x20 - 150:.1f}" y="{bar_y - 34}">'
        "発注が求めた20件目 → ここ</text>\n"
    )
    parts.append(
        f'<path class="line" d="M{x20:.1f} {bar_y - 28} L{x20:.1f} {bar_y + bar_h + 8}" '
        f'stroke-dasharray="4 3"/>\n'
    )

    x = plot_x
    label_rows = []
    for name, count, klass, note in segments:
        w = count * unit
        parts.append(
            f'<rect class="{klass}" x="{x:.1f}" y="{bar_y}" '
            f'width="{w:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{x + w / 2 - 12:.1f}" y="{bar_y + 25}">{count}件</text>\n'
        )
        label_rows.append((name, count, note))
        x += w

    y = bar_y + bar_h + 40
    for name, count, note in label_rows:
        parts.append(
            f'<text class="t-accent" x="18" y="{y}">{_esc(name)}　{count}件</text>\n'
        )
        parts.append(f'<text class="t-sm" x="200" y="{y}">{_esc(note)}</text>\n')
        y += 24

    height = y + 12 + 22 + 22 + 16
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 60}">'
        "※ 7件＋11件＝18件。全部が100人以下だったとしても、20件には届かない。</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="18" y="{height - 38}">'
        "※ 値打ちは「20件が7件に減ったこと」ではない。11件が自分の作業として残ったこと。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。</text>\n"
    )

    alt = (
        "自分で集めた候補25件を条件で仕分けた図。3条件とも○にできたのが7件、"
        "従業員数が空欄で自分が確かめることになるのが11件、重複の疑いが1件、"
        "条件から外れるのが6件。発注が求めた20件目の位置は、"
        "条件から外れる6件の中に入ってしまう。"
    )
    (OUT / "list-work-not-delivery.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def reply_undecided_marks_chart() -> None:
    """答えられない6通が、工程ごとに「送れる文」になっていくところ。

    実測（2026-08-15・架空の条件表8行と架空の問い合わせ12通）。
    青＝本文の中に「私が決める」印が残っている（そのままでは送れない＝正しい）。
    赤＝印が無く、1つの文面に決まっている（決めていないのに決まった）。
    """
    rows = [
        ("「下書きを作って」1回目", [1, 1, 0, 0, 1, 0]),
        ("「下書きを作って」2回目", [0, 1, 0, 1, 0, 0]),
        ("「そのまま送れる形に」2回とも", [0, 0, 0, 0, 0, 0]),
        ("〔私が決める〕を本文に残して", [1, 1, 1, 1, 1, 1]),
    ]
    cols = ["B1", "B2", "B3", "B4", "B5", "B6"]
    label_w = 208
    cell_w, cell_h, gap = 48, 30, 8
    top = 122
    pitch = cell_h + gap
    grid_x = label_w
    right_x = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_x + 130 <= WIDTH - 18, right_x

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "条件表に答えの無い6通が、頼み方ひとつで「そのまま送れる文」になる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の条件表8行と架空の問い合わせ12通。6通は条件表のどこにも答えが書いていない。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "青＝本文の中に「私が決める」印が残っている ／ 赤＝印が無く、1つの文面に決まっている。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "数えたのは、相手に貼る本文だけ。文面の外に付いた注記は数えていない。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x + cell_w / 2 - 9:.1f}" y="{top - 10}">{name}</text>\n'
        )

    for row_index, (name, marks) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(f'<text class="t-sm" x="18" y="{y + 20}">{_esc(name)}</text>\n')
        for col_index, kept in enumerate(marks):
            x = grid_x + col_index * (cell_w + gap)
            klass = "box-accent" if kept else "box-bad"
            parts.append(
                f'<rect class="{klass}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            mark = "印" if kept else "送"
            tone = "t-accent" if kept else "t-bad"
            parts.append(
                f'<text class="{tone}" x="{x + cell_w / 2 - 7:.1f}" y="{y + 20}">{mark}</text>\n'
            )
        kept_n = sum(marks)
        parts.append(
            f'<text class="t-sm" x="{right_x + 14}" y="{y + 20}">印 {kept_n}／6</text>\n'
        )

    height = top + len(rows) * pitch + 12 + 22 + 22 + 16
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 60}">'
        "※ 「そのまま送れる形に」の2回では、条件表に無い決めごとが本文に6件ずつ入った。</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="18" y="{height - 38}">'
        "※ うち1回は「記事料金の3割」という数字を、もう1回は「他のお取引先とのお約束」という事実を作った。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。</text>\n"
    )

    alt = (
        "条件表に答えの無い6通について、頼み方ごとに「私が決める」印が本文に残った数を並べた図。"
        "下書きを作ってと頼んだ1回目は6通中3通、2回目は6通中2通にしか印が残らなかった。"
        "そのまま送れる形にしてと頼むと2回とも0通になり、"
        "〔私が決める〕を本文に残してと頼むと6通すべてに印が残った。"
    )
    (OUT / "reply-undecided-marks.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def material_checks_matrix_chart() -> None:
    """材料に仕込んだ4つの異常が、頼み方3通りで返りに出たかどうか。

    実測（2026-08-16・架空の日次の記録2本＝表形式と走り書き）。
    真値は材料を作ったコードの assert で確かめてある。
    セルの分母＝その頼み方を走らせた回数。
    """
    rows = [
        ("中身が完全に同じ行（3組）", "4/4", "good", "2/4", "warn", "4/4", "good"),
        ("途中で切れている行（1行）", "4/4", "good", "2/4", "warn", "4/4", "good"),
        ("日付が1日古い（昨日ぶんではない）", "0/4", "bad", "0/4", "bad", "3/3", "good"),
        ("毎日ある種類が、今日は0件", "0/4", "bad", "0/4", "bad", "2/2", "good"),
    ]
    cols = [
        ("① そのまま頼む", "毎朝の集計を頼むだけ"),
        ("② 自動実行の形に短く", "「この2つ以外は書かない」"),
        ("③ 点検の欄を作る", "数と日付を先に書かせる"),
    ]
    klass = {"good": "box-good", "warn": "box-accent", "bad": "box-bad"}
    text_klass = {"good": "t-good", "warn": "t-accent", "bad": "t-bad"}

    label_x, label_w = 18, 276
    col_w, col_gap = 132, 6
    col_x = [label_x + label_w + col_gap + i * (col_w + col_gap) for i in range(3)]
    head_y, head_h = 92, 46
    row_h, row_gap = 48, 6
    row_y = [head_y + head_h + row_gap + i * (row_h + row_gap) for i in range(4)]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "材料が壊れた日に、返りがそれを言ってくるか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の日次の記録2本（表形式・走り書き）に、同じ4つの異常を仕込んで走らせた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "分母は走らせた回数。③は、その項目を点検の欄に入れた回だけを数えている。</text>\n",
    ]

    for i, (head, sub) in enumerate(cols):
        parts.append(
            f'<rect class="box-quiet" x="{col_x[i]}" y="{head_y}" '
            f'width="{col_w}" height="{head_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-strong" x="{col_x[i] + 8}" y="{head_y + 20}" '
            f'style="font-size:12px">{_esc(head)}</text>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + 8}" y="{head_y + 36}">{_esc(sub)}</text>\n'
        )

    for r, (label, *cells) in enumerate(rows):
        y = row_y[r]
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + row_h / 2 + 5:.0f}">{_esc(label)}</text>\n'
        )
        for c in range(3):
            value, kind = cells[c * 2], cells[c * 2 + 1]
            parts.append(
                f'<rect class="{klass[kind]}" x="{col_x[c]}" y="{y}" '
                f'width="{col_w}" height="{row_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="{text_klass[kind]}" x="{col_x[c] + col_w / 2 - 16:.0f}" '
                f'y="{y + row_h / 2 + 5:.0f}">{value}</text>\n'
            )

    bottom = row_y[-1] + row_h
    notes = [
        ("t-bad", "※ 下の2行は、材料の中を読んでも決まらない。今日が何日か・普段は何件かを"
                  "AIは持っていない。"),
        ("t-xs", "※ ②で 2/4 になったのは、表形式の材料2回で警告が丸ごと消えたため"
                 "（走り書きの材料2回では残った）。"),
        ("t-xs", "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。"),
    ]
    y = bottom + 26
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "材料が壊れた日に、返りが異常を指摘したかどうかを4つの異常と3つの頼み方で並べた表。"
        "中身が完全に同じ行が3組ある件は、そのまま頼んだ4回で4回、"
        "自動実行の形に短くした4回で2回、点検の欄を作った4回で4回。"
        "途中で切れている行も同じく4回・2回・4回。"
        "日付が1日古いことは、そのまま頼んだ4回で0回、短くした4回でも0回、"
        "今日の日付をこちらから渡した3回では3回とも指摘した。"
        "毎日ある種類が今日は0件だったことは、そのまま頼んだ4回で0回、"
        "短くした4回でも0回、毎日ある種類の名前をこちらから渡した2回では2回とも指摘した。"
        "下の2つは材料の中を読んでも決まらないもので、"
        "今日が何日か、普段は何件かという情報をAIは持っていない。"
    )
    (OUT / "material-checks-matrix.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def material_check_split_chart() -> None:
    """点検の欄と一覧はそろったのに、その下の集計だけが2回で割れた回。

    実測（2026-08-16・同じ指示文を2回）。真値は材料から計算した。
    """
    blocks = [
        ("毎日ある種類の 0件 の警告",
         "請求 0件 / 納期 0件", "請求 0件 / 納期 0件", True, "2回とも同じ"),
        ("種類ごとの件数",
         "仕様2・返品2・その他2", "仕様3・返品3・その他3", False, "真値は 3・3・3"),
        ("まだ対応が終わっていない一覧",
         "3行（文字列まで一致）", "3行（文字列まで一致）", True, "2回とも同じ"),
    ]
    label_x, label_w = 18, 218
    col_w, col_gap = 218, 8
    col_x = [label_x + label_w + col_gap, label_x + label_w + col_gap * 2 + col_w]
    head_y = 96
    blk_h, blk_gap = 58, 8
    blk_y = [head_y + 24 + i * (blk_h + blk_gap) for i in range(3)]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "点検の欄はそろった。その下の集計だけが、2回で割れた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ指示文を2回。どちらの回も「中身が完全に同じ行は、1件として数えてください」入り。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "0件の警告も、未対応の一覧も、2回とも1文字も違わない。違ったのは件数だけ。</text>\n",
        f'<text class="t-xs" x="{col_x[0]}" y="{head_y + 10}">1回目</text>\n',
        f'<text class="t-xs" x="{col_x[1]}" y="{head_y + 10}">2回目</text>\n',
    ]

    for i, (label, a, b, same, note) in enumerate(blocks):
        y = blk_y[i]
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + 24}">{_esc(label)}</text>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{label_x}" y="{y + 44}">{_esc(note)}</text>\n'
        )
        for j, value in enumerate((a, b)):
            css = "box-good" if same else "box-bad"
            tcss = "t-good" if same else "t-bad"
            if not same and j == 1:
                css, tcss = "box-good", "t-good"
            parts.append(
                f'<rect class="{css}" x="{col_x[j]}" y="{y}" '
                f'width="{col_w}" height="{blk_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="{tcss}" x="{col_x[j] + 12}" y="{y + blk_h / 2 + 5:.0f}" '
                f'style="font-size:12px">{_esc(value)}</text>\n'
            )

    bottom = blk_y[-1] + blk_h
    notes = [
        ("t-bad", "※ 1回目の件数は、材料から計算した真値と合っていない。"
                  "一覧が合っているので、表だけでは気づけない。"),
        ("t-xs", "※ 点検の欄（行数・最新の日付・重複の組数・崩れた行）は、"
                 "10回とも真値と一致した。"),
        ("t-xs", "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。"),
    ]
    y = bottom + 26
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "同じ指示文を2回走らせて、返りの3つの部分を並べた図。"
        "毎日ある種類が0件だという警告は、1回目も2回目も請求0件・納期0件で同じ。"
        "まだ対応が終わっていない一覧も、1回目も2回目も3行で文字列まで一致。"
        "ところが種類ごとの件数だけが、1回目は仕様2・返品2・その他2、"
        "2回目は仕様3・返品3・その他3に割れた。材料から計算した真値は3・3・3なので、"
        "1回目のほうが間違っている。警告も一覧も合っているため、"
        "件数が間違っていることに画面からは気づけない。"
    )
    (OUT / "material-check-split.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def scope_lines_ai_drew_chart() -> None:
    """頼み方ごとに、返ってきた表の3つの数を並べる（回ごとの値をそのまま出す）。

    実測（2026-08-17・材料2本×各2回＝4回。指示文5と6は各1回で計2回）。
    値は check2.py の出力そのまま。畳まずに回ごとに並べる（台帳★42）。
    """
    rows = [
        ("そのまま「表を作って」", ["7", "7", "7", "0"], ["10", "3", "1", "1"], ["0", "0", "0", "0"]),
        ("＋「含まれないものも」", ["7", "7", "7", "7"], ["4", "1", "1", "0"], ["0", "0", "0", "0"]),
        ("＋「同じ数だけ・1行に1つ」", ["7", "7", "7", "7"], ["5", "1", "0", "0"], ["0", "0", "0", "0"]),
        ("＋〔私が決める〕を表の中に", ["0", "0", "0", "0"], ["0", "1", "0", "0"], ["19", "27", "26", "18"]),
        ("対照＝「書いてないことは書くな」", ["0", "0", "—", "—"], ["0", "0", "—", "—"], ["0", "0", "—", "—"]),
    ]
    label_x, label_w = 18, 208
    col_w, col_gap = 152, 10
    col_x = [label_x + label_w + col_gap + i * (col_w + col_gap) for i in range(3)]
    heads = [
        ("含まれないこと", "並んだ項目の数"),
        ("AIが引いた上限", "「3枚まで」等の数"),
        ("〔私が決める〕", "表の中に残った印"),
    ]
    head_y = 92
    row_h, row_gap = 40, 7
    row_y = [head_y + 44 + i * (row_h + row_gap) for i in range(len(rows))]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "頼み方を変えると、表の中で決まっているものが入れ替わる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の「できること7件・もう決めたこと3件」を材料2本ぶん作り、各2回ずつ通した（計4回）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "セルの4つの数は、左から 材料A1回目・A2回目・B1回目・B2回目。畳まずに並べてある。</text>\n",
    ]
    for i, (title, sub) in enumerate(heads):
        parts.append(
            f'<rect class="box-quiet" x="{col_x[i]}" y="{head_y}" '
            f'width="{col_w}" height="38" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-strong" x="{col_x[i] + 8}" y="{head_y + 17}" '
            f'style="font-size:12px">{_esc(title)}</text>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + 8}" y="{head_y + 32}">{_esc(sub)}</text>\n'
        )

    for r, (label, excl, caps, marks) in enumerate(rows):
        y = row_y[r]
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + row_h / 2 + 5:.0f}" '
            f'style="font-size:12px">{_esc(label)}</text>\n'
        )
        for c, values in enumerate((excl, caps, marks)):
            nums = [v for v in values if v != "—"]
            if c == 0:
                good = all(v == "7" for v in nums)
                bad = any(v == "0" for v in nums)
            elif c == 1:
                good = all(v == "0" for v in nums)
                bad = any(int(v) >= 3 for v in nums)
            else:
                good = all(v != "0" for v in nums)
                bad = False
            klass = "box-good" if good else ("box-bad" if bad else "box")
            tone = "t-good" if good else ("t-bad" if bad else "t")
            parts.append(
                f'<rect class="{klass}" x="{col_x[c]}" y="{y}" '
                f'width="{col_w}" height="{row_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="{tone}" x="{col_x[c] + 12}" y="{y + row_h / 2 + 5:.0f}" '
                f'style="font-size:12.5px">{_esc(" ・ ".join(values))}</text>\n'
            )

    y = row_y[-1] + row_h + 26
    notes = [
        ("t-bad", "※ そのまま頼んだ4回のうち1回は、含まれないことが1項目も並ばなかった。"
                  "残る3回は形が毎回違う（別表・列・見出し）。"),
        ("t-bad", "※ 上限の中身も回ごとに違う。材料Aの2回で両方に出たのは「3枚」「14日」だけで、"
                  "3,000字・5件・2枚・5ページは片方にしか出ない。"),
        ("t-xs", "架空データでの実測。回ごとの生の返りは docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "引き受ける範囲の表を、頼み方を5通りに変えて作らせ、3つの数を回ごとに並べた図。"
        "材料は架空の「できること7件・もう決めたこと3件」を2本用意し、各2回ずつ通した。"
        "数は左から材料Aの1回目、Aの2回目、Bの1回目、Bの2回目。"
        "そのまま「表を作って」と頼むと、含まれないことの項目は7・7・7・0で、"
        "4回のうち1回は1項目も並ばなかった。"
        "そのときAIが自分で引いた上限、たとえば写真3枚までや公開後14日以内といった数は"
        "10・3・1・1で、材料に書いていない数字が線として表に入っている。"
        "〔私が決める〕の印は4回とも0件。"
        "「含まれないものも書いてください」を足すと、含まれないことは4回とも7件になり、"
        "上限は4・1・1・0に減る。"
        "「含まれるものと同じ数だけ、1行に1つ」まで足すと、含まれないことは4回とも7件、"
        "上限は5・1・0・0。"
        "〔私が決める：何を決めればよいか〕を表の中に残させると、"
        "上限は0・1・0・0まで落ち、かわりに印が19・27・26・18件残る。"
        "ただしこの版では含まれないことの項目は4回とも0件になる。"
        "対照として「私が上に書いていないことは一切書かないでください」だけを渡すと、"
        "2回とも含まれないことも上限も印も全部0件で、表は材料の写しになった。"
    )
    (OUT / "scope-lines-ai-drew.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def scope_saved_form_flips_chart() -> None:
    """保存版（出す形を固定）を2回転させたら、判定列が丸ごと逆になった回。"""
    cols = [("材料A 1回目", ["未定"] * 7), ("材料A 2回目", ["含む"] * 7),
            ("材料B 1回目", ["含む"] * 7), ("材料B 2回目", ["未定"] * 7)]
    items = ["作業1", "作業2", "作業3", "作業4", "作業5", "作業6", "作業7"]

    label_x, label_w = 18, 92
    col_w, col_gap = 138, 10
    col_x = [label_x + label_w + col_gap + i * (col_w + col_gap) for i in range(4)]
    head_y = 96
    cell_h, cell_gap = 30, 5
    row_y = [head_y + 26 + i * (cell_h + cell_gap) for i in range(len(items))]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "出す形を固定しても、判定そのものが2回で入れ替わった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "1行目の見出し・列の名前・列の数まで指定した保存版を、同じ材料で2回ずつ走らせた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "列の名前も行の形も4回とも同じ。違うのは「含む/含まない」の欄の値だけ。</text>\n",
    ]
    for i, (name, _) in enumerate(cols):
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + 8}" y="{head_y + 12}">{_esc(name)}</text>\n'
        )
    for r, item in enumerate(items):
        y = row_y[r]
        parts.append(
            f'<text class="t-sm" x="{label_x}" y="{y + cell_h / 2 + 4:.0f}">{_esc(item)}</text>\n'
        )
        for c, (_, values) in enumerate(cols):
            value = values[r]
            klass = "box-bad" if value == "未定" else "box-accent"
            tone = "t-bad" if value == "未定" else "t-accent"
            parts.append(
                f'<rect class="{klass}" x="{col_x[c]}" y="{y}" '
                f'width="{col_w}" height="{cell_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="{tone}" x="{col_x[c] + col_w / 2 - 16:.0f}" '
                f'y="{y + cell_h / 2 + 5:.0f}" style="font-size:12px">{_esc(value)}</text>\n'
            )

    y = row_y[-1] + cell_h + 26
    notes = [
        ("t-bad", "※ 2回目には、材料Aで3行（納期・修正・支払い）、材料Bでも3行が新しく生えた。"
                  "行数が7行と10行で違う。"),
        ("t-xs", "※ 「私が決める」欄の中身は4回とも埋まっており、空欄になった回は無い。"
                 "割れたのは判定の欄だけ。"),
        ("t-xs", "架空データでの実測。4回ぶんの生の返りは docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "毎回同じ形で出すための保存版の指示文を、同じ材料で2回ずつ走らせた結果を並べた図。"
        "1行目の見出し、列の名前、列の数まで指定してある。"
        "材料Aの1回目は、作業1から作業7まで7項目すべてが「未定」だった。"
        "同じ指示文の2回目は、7項目すべてが「含む」になった。"
        "材料Bでは逆で、1回目が7項目すべて「含む」、2回目が7項目すべて「未定」だった。"
        "列の名前も行の形も4回とも同じなので、表を見ているかぎり割れていることが分からない。"
        "さらに2回目には、材料Aでも材料Bでも納期・修正・支払いの3行が新しく生え、"
        "行数が7行と10行で違っている。"
        "「私が決める」の欄はどの回も埋まっていて、割れたのは判定の欄だけだった。"
    )
    (OUT / "scope-saved-form-flips.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def records_length_vs_result_chart() -> None:
    """架空の応募記録12件を、提案文の字数の多い順に並べた図。

    真値は gen.py が材料そのものから数えたもの（手で書いていない）。
    上位3件がそのまま採用の3件になる仕込み。
    """
    rows = [
        (1, 311, True), (2, 284, True), (3, 271, True), (7, 258, False),
        (5, 236, False), (12, 224, False), (10, 160, False), (9, 151, False),
        (11, 126, False), (6, 119, False), (4, 108, False), (8, 85, False),
    ]
    label_x = 18
    plot_x = 118
    plot_w = 430
    top = 118
    bar_h, bar_gap = 21, 6
    hi = 330

    def px(n: float) -> float:
        return plot_x + plot_w * n / hi

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "字数の多い順に並べると、上位3件がそのまま採用の3件だった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の応募記録12件（採用3・不採用9）。字数は材料そのものから数えた真値で、"
        "手で書いていない。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "この並びは、記録の中で数えれば誰でも確かめられる。推測は要らない。</text>\n",
        '<text class="t-xs" x="18" y="94">案件の番号</text>\n',
        f'<text class="t-xs" x="{plot_x}" y="94">提案文の字数</text>\n',
    ]
    for i, (no, n, adopted) in enumerate(rows):
        y = top + i * (bar_h + bar_gap)
        parts.append(
            f'<text class="t-sm" x="{label_x}" y="{y + bar_h - 6}">{no}番</text>\n'
        )
        klass = "bar-new" if adopted else "bar-old"
        parts.append(
            f'<rect class="{klass}" x="{plot_x}" y="{y}" '
            f'width="{px(n) - plot_x:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        css = "t-accent" if adopted else "t-sm"
        parts.append(
            f'<text class="{css}" x="{px(n) + 8:.1f}" y="{y + bar_h - 6}">'
            f'{n}字{"　採用" if adopted else ""}</text>\n'
        )

    line_y = top + 3 * (bar_h + bar_gap) - bar_gap / 2
    parts.append(
        f'<path class="line" d="M{label_x} {line_y:.1f} L{plot_x + plot_w} {line_y:.1f}" '
        f'stroke-dasharray="4 3"/>\n'
    )
    parts.append(
        f'<text class="t-bad" x="{plot_x + 300}" y="{line_y - 8:.0f}">'
        "ここより上が採用3件</text>\n"
    )

    y = top + len(rows) * (bar_h + bar_gap) + 24
    notes = [
        ("t-bad", "※ 「通った提案と通らなかった提案の差を出して」と頼んだ4回は、"
                  "4回とも「長さの差ではありません」と書いた。"),
        ("t-bad", "※ その4回とも、案件ごとの字数は1件も数えていない。数えずに否定している。"),
        ("t-xs", "架空データでの実測。4回ぶんの生の返りは docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "架空の応募記録12件を、提案文の字数の多い順に並べた横棒グラフ。"
        "字数は材料そのものから数えた真値で、手で書いたものではない。"
        "1番が311字で採用、2番が284字で採用、3番が271字で採用。"
        "ここまでが上位3件で、そのまま採用の3件と一致する。"
        "以下は不採用で、7番258字、5番236字、12番224字、10番160字、9番151字、"
        "11番126字、6番119字、4番108字、8番85字と続く。"
        "つまり字数で並べるだけで採用と不採用が完全に分かれており、"
        "これは記録の中で数えれば誰でも確かめられる事実である。"
        "ところが「通った提案と通らなかった提案の差を出してください」と頼んだ4回は、"
        "4回とも「長さの差ではありません」と書いた。"
        "しかもその4回とも、案件ごとの字数を1件も数えていない。数えずに否定している。"
    )
    (OUT / "records-length-vs-result.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def records_counted_or_not_chart() -> None:
    """頼み方ごとに、字数を何件数えたか・真値と何件一致したかを並べる。"""
    rows = [
        ("そのまま「差を出して」", ["0/12", "0/12", "0/12", "0/12"], "×"),
        ("「言えること／言えないこと」に分ける", ["3/12", "0/12", "5/12", "0/12"], "△"),
        ("「記録にあることだけ表に」（各1回）", ["12/12", "12/12", "—", "—"], "○"),
        ("保存版（形を固定）", ["12/12", "0/12", "12/12", "6/12"], "△"),
    ]
    label_x, label_w = 18, 244
    col_w, col_gap = 96, 8
    col_x = [label_x + label_w + col_gap + i * (col_w + col_gap) for i in range(4)]
    head_y = 96
    row_h, row_gap = 42, 8
    row_y = [head_y + 28 + i * (row_h + row_gap) for i in range(len(rows))]
    heads = ["A 1回目", "A 2回目", "B 1回目", "B 2回目"]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "案件ごとの字数を、何件ぶん数えて書いたか（真値と一致した数）</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "分母は12件。真値は材料そのものから数えたもの。1件でもずれたら不一致として数えた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「記録にあることだけ表に」は材料2本を各1回なので、右2列は空欄。</text>\n",
    ]
    for i, name in enumerate(heads):
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + 10}" y="{head_y + 14}">{_esc(name)}</text>\n'
        )
    for r, (label, values, _mark) in enumerate(rows):
        y = row_y[r]
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + row_h / 2 + 5:.0f}" '
            f'style="font-size:12px">{_esc(label)}</text>\n'
        )
        for c, value in enumerate(values):
            if value == "—":
                klass, tone = "box-quiet", "t-sm"
            elif value.startswith("12/"):
                klass, tone = "box-good", "t-good"
            elif value.startswith("0/"):
                klass, tone = "box-bad", "t-bad"
            else:
                klass, tone = "box", "t"
            parts.append(
                f'<rect class="{klass}" x="{col_x[c]}" y="{y}" '
                f'width="{col_w}" height="{row_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="{tone}" x="{col_x[c] + 20}" y="{y + row_h / 2 + 5:.0f}" '
                f'style="font-size:12.5px">{_esc(value)}</text>\n'
            )

    y = row_y[-1] + row_h + 26
    notes = [
        ("t-good", "※ 「差や理由は書かないでください。記録に書いてあることだけを表にしてください」"
                   "＝24マス全部が真値と一致した。"),
        ("t-bad", "※ 保存版は形が4回ともそろっているのに、2回目だけ字数が消えて"
                  "「長短だけでは分かれていない」という言葉に変わった。"),
        ("t-xs", "架空データでの実測。回ごとの生の返りは docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "頼み方を4通りに変えて、案件ごとの提案文の字数を何件ぶん書いたかを並べた図。"
        "分母は12件で、真値は材料そのものから数えたもの。"
        "そのまま「差を出して」と頼んだ4回は、材料Aの1回目も2回目も、材料Bの1回目も2回目も、"
        "すべて0件で、字数を1件も書いていない。"
        "「言えること／言えないことに分けてください」と頼むと、材料Aの1回目が3件、"
        "2回目が0件、材料Bの1回目が5件、2回目が0件で、書いた回と書かない回に割れた。"
        "しかも材料Aの1回目に書いた3件は、3件とも真値とずれていた。"
        "「差や理由は書かないでください。記録に書いてあることだけを表にしてください」と頼むと、"
        "材料Aも材料Bも12件すべてを書き、24マス全部が真値と一致した。"
        "出す形を固定した保存版では、材料Aの1回目が12件、2回目が0件、"
        "材料Bの1回目が12件、2回目が6件で割れた。"
        "形は4回ともそろっているのに、2回目だけ字数が消えて"
        "「長短だけでは分かれていない」という言葉に置き換わっている。"
    )
    (OUT / "records-counted-or-not.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def job_capacity_subtraction_chart() -> None:
    """使える時間から既存案件を引いた残りに、幅つきの見積もりを重ねた図。

    値は gen.py が材料から計算した真値（手で書いていない）。
    """
    avail, held, left, lo, hi = 2160, 1140, 1020, 800, 1120
    plot_x, plot_w = 152, 500
    hi_axis = 2200

    def px(m: float) -> float:
        return plot_x + plot_w * m / hi_axis

    bar_h = 30
    y1, y2, y3 = 116, 166, 216

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "合計は足りている。上限で見ると100分足りない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の2週間ぶんの予定表・抱えている案件3件・新しい依頼1件。"
        "数字はすべて材料から計算した真値。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "見積もりは幅で出ている（800分〜1,120分）。どちらを使うかで答えが逆になる。</text>\n",
        f'<text class="t-sm" x="18" y="{y1 + 20}">使える時間</text>\n',
        f'<rect class="bar-old" x="{plot_x}" y="{y1}" '
        f'width="{px(avail) - plot_x:.1f}" height="{bar_h}" rx="2"/>\n',
        f'<text class="t" x="{px(avail) + 8:.1f}" y="{y1 + 20}">2,160分</text>\n',
        f'<text class="t-sm" x="18" y="{y2 + 20}">抱えている案件</text>\n',
        f'<rect class="bar-in" x="{plot_x}" y="{y2}" '
        f'width="{px(held) - plot_x:.1f}" height="{bar_h}" rx="2"/>\n',
        f'<text class="t" x="{px(held) + 8:.1f}" y="{y2 + 20}">1,140分</text>\n',
        f'<text class="t-sm" x="18" y="{y3 + 20}">新しい依頼</text>\n',
    ]
    # 残り 1,020分の枠（既存の右端から）
    left_x = px(held)
    parts.append(
        f'<rect class="box-quiet" x="{left_x:.1f}" y="{y3}" '
        f'width="{px(held + left) - left_x:.1f}" height="{bar_h}" rx="2"/>\n'
    )
    parts.append(
        f'<rect class="bar-new" x="{left_x:.1f}" y="{y3 + 5}" '
        f'width="{px(held + lo) - left_x:.1f}" height="{bar_h - 10}" rx="2"/>\n'
    )
    parts.append(
        f'<rect class="box-bad" x="{px(held + lo):.1f}" y="{y3 + 5}" '
        f'width="{px(held + hi) - px(held + lo):.1f}" height="{bar_h - 10}" rx="2"/>\n'
    )
    parts.append(
        f'<text class="t-good" x="{plot_x + 14}" y="{y3 + 20}">下限 800分</text>\n'
    )
    parts.append(
        f'<text class="t-bad" x="{px(held + hi) - 78:.1f}" y="{y3 + bar_h + 14}">'
        "上限 1,120分</text>\n"
    )
    # 使える時間の右端の縦線
    edge = px(avail)
    parts.append(
        f'<path class="line" d="M{edge:.1f} {y1 - 6} L{edge:.1f} {y3 + bar_h + 14}" '
        f'stroke-dasharray="4 3"/>\n'
    )
    parts.append(
        f'<text class="t-bad" x="{edge - 236:.0f}" y="{y3 + bar_h + 28}">'
        "この線を100分はみ出す＝上限で見ると入らない</text>\n"
    )

    y = y3 + bar_h + 54
    rows = [
        ("使える時間の合計", "2,160分"),
        ("抱えている案件の残り", "1,140分"),
        ("差し引き（新しい依頼に回せる時間）", "1,020分"),
        ("下限（800分）で見た場合", "220分あまる"),
        ("上限（1,120分）で見た場合", "100分たりない"),
    ]
    for i, (name, value) in enumerate(rows):
        css = "t-bad" if "たりない" in value else "t"
        parts.append(f'<text class="t-sm" x="18" y="{y}">{_esc(name)}</text>\n')
        parts.append(f'<text class="{css}" x="{plot_x + 100}" y="{y}">{_esc(value)}</text>\n')
        y += 22

    y += 6
    notes = [
        ("t-bad", "※ 「この依頼、受けられますか」と聞いた4回は、4回ともこの数字を正しく出したうえで、"),
        ("t-bad", "　 受ける／断るの言い切りを 2語・3語・1語・3語 書いた。決めるのは自分のはず。"),
        ("t-xs", "架空データでの実測。回ごとの生の返りは docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "架空の2週間ぶんの予定表から、新しい依頼が入るかどうかを引き算で出した図。"
        "使える時間の合計は2,160分。いま抱えている案件3件の残りが1,140分。"
        "差し引き1,020分が、新しい依頼に回せる時間になる。"
        "新しい依頼の見積もりは幅で出ていて、下限が800分、上限が1,120分。"
        "下限の800分なら1,020分の枠に収まり、220分あまる。"
        "上限の1,120分だと枠を100分はみ出して、たりない。"
        "つまり見積もりの下限と上限のどちらを使うかで、入るか入らないかの答えが逆になる。"
        "「この依頼、受けられますか」と聞いた4回は、4回ともこの数字を正しく計算したうえで、"
        "受ける、または断るという言い切りを、それぞれ2語・3語・1語・3語書いた。"
    )
    (OUT / "job-capacity-subtraction.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def job_ask_shape_vs_verdict_chart() -> None:
    """頼み方ごとに、返りの長さと「受ける/断る」の言い切りの数を並べる。"""
    rows = [
        ("そのまま「受けられますか」", ["2,520字 / 2語", "3,241字 / 3語",
                                   "2,308字 / 1語", "1,974字 / 3語"], False),
        ("「計算だけしてください」", ["612字 / 0語", "521字 / 0語",
                               "338字 / 0語", "349字 / 0語"], True),
        ("保存版（6行に固定）", ["103字 / 0語", "103字 / 0語",
                            "259字 / 0語", "276字 / 0語"], True),
    ]
    label_x, label_w = 18, 200
    col_w, col_gap = 112, 8
    col_x = [label_x + label_w + col_gap + i * (col_w + col_gap) for i in range(4)]
    head_y = 96
    row_h, row_gap = 44, 9
    row_y = [head_y + 26 + i * (row_h + row_gap) for i in range(len(rows))]
    heads = ["A 1回目", "A 2回目", "B 1回目", "B 2回目"]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "判断をやめさせると、言い切りも長さも同時に落ちた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "材料2本（A＝きつい側／B＝余裕がある側）を各2回。"
        "数字は「返りの字数 / 受ける・断るの言い切りの語数」。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "引き算の4つの数は、どの頼み方でも真値どおりだった。変わったのは判断と長さだけ。</text>\n",
    ]
    for i, name in enumerate(heads):
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + 12}" y="{head_y + 12}">{_esc(name)}</text>\n'
        )
    for r, (label, values, good) in enumerate(rows):
        y = row_y[r]
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + row_h / 2 + 5:.0f}" '
            f'style="font-size:12px">{_esc(label)}</text>\n'
        )
        for c, value in enumerate(values):
            klass = "box-good" if good else "box-bad"
            tone = "t-good" if good else "t-bad"
            parts.append(
                f'<rect class="{klass}" x="{col_x[c]}" y="{y}" '
                f'width="{col_w}" height="{row_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="{tone}" x="{col_x[c] + 8}" y="{y + row_h / 2 + 5:.0f}" '
                f'style="font-size:11.5px">{_esc(value)}</text>\n'
            )

    y = row_y[-1] + row_h + 26
    notes = [
        ("t-bad", "※ 保存版の材料Bでは、こちらが決めた最後の行の様式（「上限なら◯分足りない」）が"),
        ("t-bad", "　 事実と合わず、2回とも様式のほうを変えて注記が付いた。"),
        ("t-xs", "架空データでの実測。回ごとの生の返りは docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "頼み方を3通りに変えて、返りの長さと、受ける・断るの言い切りの語数を並べた図。"
        "材料は2本、それぞれ2回ずつ通した。"
        "そのまま「この依頼、受けられますか」と聞くと、"
        "材料Aの1回目が2,520字で言い切り2語、2回目が3,241字で3語、"
        "材料Bの1回目が2,308字で1語、2回目が1,974字で3語だった。"
        "「受けるかどうかは私が決めます。計算だけしてください」にすると、"
        "612字・521字・338字・349字となり、言い切りは4回とも0語になった。"
        "出す形を6行に固定した保存版では、103字・103字・259字・276字で、"
        "言い切りはやはり4回とも0語。材料Aの2回は1文字も違わなかった。"
        "引き算の4つの数は、どの頼み方でも材料から計算した真値どおりだった。"
        "変わったのは判断が付くかどうかと、返りの長さだけである。"
        "ただし保存版の材料Bでは、こちらが決めた最後の行の様式が事実と合わず、"
        "2回とも様式のほうを変えて注記が付いた。"
    )
    (OUT / "job-ask-shape-vs-verdict.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


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


def ask_invented_settings_chart() -> None:
    """21字の依頼に対し、AIが勝手に決めた設定の数（2026-08-12 実測）。"""
    rows = [
        ("そのまま書かせる", 4, "box-accent", "t-accent",
         "原因・部署・氏名・再発防止策"),
        ("「この頼み方を良くして」", 7, "box-bad", "t-bad",
         "＋日数・取引の長さ・初回か・文体・字数"),
        ("「足りない情報を挙げて」", 0, "box-good", "t-good",
         "決めずに、7件を質問で返す"),
    ]
    # 注記は棒の右ではなく行の下に敷く（右に置くと 21字ぶんで枠を越える）
    label_x, label_w = 18, 214
    unit = 34
    bar_x = label_x + label_w + 14
    row_h, gap_y = 34, 30  # gap_y に注記1行ぶんを含める
    top = 100
    height = top + len(rows) * (row_h + gap_y) - gap_y + 46
    assert bar_x + 7 * unit + 60 <= WIDTH - 18, bar_x + 7 * unit + 60

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「良くして」と頼むと、AIが決めた設定はむしろ増える</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "21字の依頼「取引先に謝るメールを書いて。納期が遅れた。」に対して。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "AIが勝手に決めた設定の数</text>\n",
    ]
    for index, (name, value, cls, tcls, note) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        mid = y + row_h / 2 + 5
        parts.append(f'<text class="t-sm" x="{label_x}" y="{mid:.0f}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{bar_x}" y="{y}" '
            f'width="{7 * unit}" height="{row_h}" rx="6"/>\n'
        )
        if value:
            parts.append(
                f'<rect class="{cls}" x="{bar_x}" y="{y}" '
                f'width="{value * unit}" height="{row_h}" rx="6"/>\n'
            )
        parts.append(
            f'<text class="{tcls}" x="{bar_x + 7 * unit + 12}" '
            f'y="{mid:.0f}">{value}件</text>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{bar_x}" y="{y + row_h + 18}">{_esc(note)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 2行目の改良版プロンプトは立派に見えるので、そのまま使いやすい。"
        "「5年以上の取引」「初めての遅延」は、こちらが一度も言っていない。</text>\n"
    )
    alt = (
        "21字の曖昧な依頼に対して、AIが勝手に決めた設定の数を比べた図。"
        "依頼は「取引先に謝るメールを書いて。納期が遅れた。」で、書いてある事実は3件だけ。"
        "そのまま書かせると、原因・部署・氏名・再発防止策の4件をAIが決めた。"
        "「この頼み方を良くして」と頼むと、さらに遅延日数・取引の長さ・初回かどうか・"
        "文体・文字数が加わって7件に増えた。「足りない情報を挙げて」と頼むと"
        "決めた設定は0件で、代わりに7件を質問として返してきた。"
        "改良版プロンプトは立派に見えるのでそのまま使いやすいが、"
        "5年以上の取引や初めての遅延は、こちらが一度も言っていない。"
    )
    (OUT / "ask-invented-settings.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def ask_missing_info_chart() -> None:
    """「足りない情報」として返ってきた7件と、その並び順の意味。"""
    items = [
        ("1", "何がどれだけ遅れたのか", "謝罪の重さが変わる"),
        ("2", "遅れた原因", "書かないと「隠している」と読まれる"),
        ("3", "新しい納期が決まっているか", "無いと相手が動けない"),
        ("4", "相手が受ける影響", "補償に触れるかが決まる"),
        ("5", "自分の立場と相手の役職", "文面の重さが変わる"),
        ("6", "これが初めてか", "再発防止策の要否"),
        ("7", "補償や値引きに触れるか", "社内未決を書くと後で困る"),
    ]
    num_x, name_x, why_x = 22, 56, 330
    row_h, gap = 34, 8
    top = 100
    height = top + len(items) * (row_h + gap) - gap + 62
    assert why_x + 26 * 13 <= WIDTH - 18, why_x + 26 * 13

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "答えが変わる度合いの大きい順に、質問が返ってくる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "上の3つが埋まれば下書きは作れる。4〜7は「不明」のまま触れない形にできる。</text>\n",
        f'<text class="t-xs" x="{name_x}" y="{top - 12}">足りない情報</text>\n',
        f'<text class="t-xs" x="{why_x}" y="{top - 12}">埋まらないと何が起きるか</text>\n',
    ]
    for index, (num, name, why) in enumerate(items):
        y = top + index * (row_h + gap)
        mid = y + row_h / 2 + 5
        top3 = index < 3
        parts.append(
            f'<rect class="{"box-accent" if top3 else "box-quiet"}" x="{num_x - 4}" '
            f'y="{y}" width="{WIDTH - 40}" height="{row_h}" rx="5"/>\n'
        )
        parts.append(
            f'<text class="{"t-accent" if top3 else "t-sm"}" x="{num_x + 6}" '
            f'y="{mid:.0f}">{num}</text>\n'
        )
        parts.append(f'<text class="t-sm" x="{name_x}" y="{mid:.0f}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t-xs" x="{why_x}" y="{mid:.0f}">{_esc(why)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 32}">'
        "※ 色の付いた1〜3が「これが無いと仮の内容になる」もの。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 質問が7件返るということは、そのまま書かせていたら"
        "7件をAIが決めていたということ。</text>\n"
    )
    alt = (
        "「足りない情報を挙げて」と頼んだときに返ってきた7件を、"
        "答えが変わる度合いの大きい順に並べた図。1番は何がどれだけ遅れたのかで"
        "謝罪の重さが変わる。2番は遅れた原因で、書かないと隠していると読まれる。"
        "3番は新しい納期が決まっているかで、無いと相手が動けない。"
        "4番は相手が受ける影響で補償に触れるかが決まる。5番は自分の立場と相手の役職で"
        "文面の重さが変わる。6番はこれが初めてかで再発防止策の要否。"
        "7番は補償や値引きに触れるかで、社内で決まっていないことを書くと後で困る。"
        "上の3つが埋まれば下書きは作れ、4から7は不明のまま触れない形にできる。"
        "質問が7件返るということは、そのまま書かせていたら7件をAIが決めていたということ。"
    )
    (OUT / "ask-missing-info.svg").write_text(
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



def critique_written_vs_missing_chart() -> None:
    """批評のさせ方8通りで、仕込んだ欠陥10件のうち何件が指摘されたか。

    実測（2026-08-12・架空の社内メールの下書き283字）。
    仕込みは「文の中にある欠陥」5件と「一度も書かれていない欠陥」5件。
    判定は Python の文字列照合（`docs/evidence/critique-not-rewrite.md`）。
    """
    rows = [
        ("①「批評してください」", 4, 1),
        ("②「添削してください」", 1, 0),
        ("③ 直さずに批評", 5, 2),
        ("④ 書かれていないことを", 1, 3),
        ("⑤ ③＋一文を引用", 5, 3),
        ("⑥ 読み手を名指し", 0, 5),
        ("⑦ 最初に聞かれる質問", 0, 4),
        ("⑧ 段落ごとに割り当て", 5, 4),
    ]
    left, right = 190, 566
    span = right - left
    scale = span / 5.0
    top, bar_h, bar_gap, group_gap = 96, 14, 4, 18
    group_h = bar_h * 2 + bar_gap + group_gap
    height = top + len(rows) * group_h + 46
    assert right + 44 <= WIDTH - 18, right

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ下書きを8通りに批評させて、仕込んだ欠陥10件のうち何件が指摘されたか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の社内メール283字。文の中にある欠陥5件（濃い色）と、"
        "一度も書かれていない欠陥5件（薄い色）を先に仕込んだ。</text>\n",
        f'<text class="t-xs" x="{left}" y="{top - 30}">'
        "濃い色＝文の中にある欠陥（指させる文がある） ／ "
        "薄い色＝書かれていない欠陥（指させる文が無い）</text>\n",
    ]
    for index, (name, in_text, missing) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls) in enumerate(((in_text, "bar-out"), (missing, "bar-in"))):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            label_class = "t-bad" if value <= 1 else "t-sm"
            parts.append(
                f'<text class="{label_class}" x="{left + bw + 8:.1f}" y="{by + bar_h - 2}">'
                f"{value}/5</text>\n"
            )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        "※ ①は指摘を6件も出すので十分な批評に見えるが、"
        "書かれていない欠陥は5件中1件しか出ない。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ ⑥は書かれていない欠陥を全部拾う代わりに、文の中の欠陥が0件になる。"
        "片方だけでは足りないので2回に分けて聞く。</text>\n"
    )
    alt = (
        "同じ下書きを8通りのやり方で批評させ、仕込んだ欠陥10件のうち何件が"
        "指摘されたかを比べた横棒グラフ。欠陥は、文の中にある欠陥5件と、"
        "下書きに一度も書かれていない欠陥5件に分けてある。"
        "「批評してください」だけだと、文の中にある欠陥は5件中4件拾うのに、"
        "書かれていない欠陥は5件中1件しか出ない。"
        "「添削してください」は指摘としては5件中1件と0件しか出ない。"
        "「直さずに批評してください」で文の中の欠陥が5件中5件、"
        "書かれていない欠陥は5件中2件。"
        "「書かれていないことを挙げて」で書かれていない欠陥が5件中3件。"
        "一文を引用させると5件中5件と5件中3件。"
        "読み手を名指しして何が分からないまま残るかを聞くと、"
        "書かれていない欠陥が5件中5件になる代わりに、文の中の欠陥は5件中0件になる。"
        "返信で最初に聞かれる質問を出させると5件中0件と5件中4件。"
        "段落ごとに割り当てさせると5件中5件と5件中4件で、"
        "1つの指示文としては最も広く拾った。"
        "読み手を名指しする聞き方は、書かれていない欠陥を全部拾う代わりに"
        "文の中の欠陥が見えなくなるので、2回に分けて聞く必要がある。"
    )
    (OUT / "critique-written-vs-missing.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def critique_rewrite_loses_chart() -> None:
    """「添削してください」と頼んだとき、下書きに何が起きたか。

    実測（2026-08-12・同じ下書き）。原文10行のうち何行がそのまま残ったかを
    Python の文字列一致で数え、AIの申告件数と突き合わせた。
    """
    kept = 2
    total = 10
    cell_x, cell_gap = 18, 6
    cell_w = (666 - cell_gap * (total - 1)) / total
    cell_y, cell_h = 96, 34
    top = 176
    row_h, gap_y = 30, 10
    facts = [
        ("AIが申告した変更点", "3件", "box-quiet", "t-sm"),
        ("指摘として挙がった欠陥（仕込み10件のうち）", "1件", "box-bad", "t-bad"),
        ("原文に根拠のない記述が、書き直し本文に足された", "5件", "box-bad", "t-bad"),
        ("書かれていない欠陥（期限・連絡先・主管・工数）が埋まった", "0件", "box-bad", "t-bad"),
    ]
    height = top + len(facts) * (row_h + gap_y) - gap_y + 46

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「この下書きを添削してください」と頼んだとき、下書きに起きたこと</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の社内メール（本文10行）。返ってきた書き直し本文に"
        "原文の行がそのまま残っているかを機械で数えた。</text>\n",
        f'<text class="t-xs" x="18" y="{cell_y - 12}">'
        "原文10行のうち、そのまま残った行（濃い枠）と、消えた行（赤い枠）</text>\n",
    ]
    for i in range(total):
        x = cell_x + i * (cell_w + cell_gap)
        klass = "box-good" if i < kept else "box-bad"
        parts.append(
            f'<rect class="{klass}" x="{x:.1f}" y="{cell_y}" '
            f'width="{cell_w:.1f}" height="{cell_h}" rx="4"/>\n'
        )
    parts.append(
        f'<text class="t-good" x="{cell_x}" y="{cell_y + cell_h + 18}">'
        "残った2行＝宛名と名乗り</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="{cell_x + 200}" y="{cell_y + cell_h + 18}">'
        "消えた8行。うち「大幅にコストが下がります」は指摘されずに削除された</text>\n"
    )
    for index, (label, value, box, text_class) in enumerate(facts):
        y = top + index * (row_h + gap_y)
        parts.append(
            f'<rect class="{box}" x="18" y="{y}" width="666" height="{row_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t" x="30" y="{y + 20}">{_esc(label)}</text>\n')
        parts.append(
            f'<text class="{text_class}" x="600" y="{y + 20}">{_esc(value)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        "※ いちばん重いのは3行目。書き直し本文には、下書きの持ち主が決めていない"
        "内容が5件入っていた。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 根拠のない断定は「指摘」ではなく「削除」で処理されるので、"
        "書いた本人は自分の断定に根拠が無かったことを知らないまま終わる。</text>\n"
    )
    alt = (
        "「この下書きを添削してください」と頼んだときに下書きに起きたことを示した図。"
        "本文10行のうち、そのまま残ったのは宛名と名乗りの2行だけで、残り8行は消えた。"
        "消えた8行には「大幅にコストが下がります」という根拠のない断定が含まれるが、"
        "これは指摘されずに削除された。"
        "AIが申告した変更点は3件。仕込んだ欠陥10件のうち指摘として挙がったのは1件。"
        "原文に根拠のない記述が書き直し本文に5件足された。"
        "期限・連絡先・主管・工数といった、下書きに書かれていない欠陥が埋まったものは0件。"
        "書き直し本文には、下書きの持ち主が決めていない内容が5件入っていた。"
        "根拠のない断定は指摘ではなく削除で処理されるので、"
        "書いた本人は自分の断定に根拠が無かったことを知らないまま終わる。"
    )
    (OUT / "critique-rewrite-loses.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def runbook_find_holes_chart() -> None:
    """手順書に仕込んだ穴8件を、頼み方4通りで何件見つけられたか。

    実測（2026-08-12・架空の社内手順書8手順）。4通りとも会話の1手目として
    独立に実行した。判定は Python の正規表現照合
    （`docs/evidence/try-the-runbook.md`）。
    """
    rows = [
        ("①「レビューしてください」", 5, "bar-old", "読んで批評させた"),
        ("②「そのとおりにやってみて」", 0, "box-bad", "止まらずに8手順とも完了した"),
        ("③ ②＋「できない所で止まって」", 8, "bar-new", "8手順すべてで止まった"),
        ("④ 手順ごとに要る物を先に出させる", 7, "bar-in", "成果物の連鎖が切れた2か所を名指し"),
    ]
    left, right = 258, 470
    scale = (right - left) / 8.0
    top, bar_h, gap = 96, 24, 30
    row_h = bar_h + gap
    height = top + len(rows) * row_h + 46
    assert right + 40 <= WIDTH - 18, right

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ手順書に仕込んだ穴8件を、頼み方4通りで何件見つけられたか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の社内手順書（8手順）。前の手順の成果物が無い・場所が決まらないなどの穴を、"
        "先に8件仕込んだ。</text>\n",
        f'<text class="t-xs" x="{left}" y="{top - 12}">0件</text>\n',
        f'<text class="t-xs" x="{right - 22}" y="{top - 12}">8件</text>\n',
    ]
    for index, (name, found, klass, note) in enumerate(rows):
        y = top + index * row_h
        parts.append(f'<text class="t" x="18" y="{y + 17}">{_esc(name)}</text>\n')
        bw = max(3.0, found * scale)
        parts.append(
            f'<rect class="{klass}" x="{left}" y="{y}" '
            f'width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        value_class = "t-bad" if found <= 2 else "t-strong"
        parts.append(
            f'<text class="{value_class}" x="{left + bw + 10:.1f}" y="{y + 17}">'
            f"{found}/8</text>\n"
        )
        parts.append(
            f'<text class="t-xs" x="{left}" y="{y + bar_h + 15}">{_esc(note)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        "※ ②は穴を1件も報告しなかった。書かれていないことを自分で決めて、"
        "8手順とも「完了」で終えたため。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 差は「実行させたかどうか」ではなく、"
        "「できないときに止まってよい、と伝えたかどうか」で出ている。</text>\n"
    )
    alt = (
        "同じ手順書に仕込んだ穴8件を、頼み方4通りで何件見つけられたかを比べた横棒グラフ。"
        "架空の社内手順書8手順に、前の手順の成果物が無い、保存場所が決まらないなどの穴を"
        "先に8件仕込んである。"
        "「この手順書をレビューしてください」と読ませて批評させると8件中5件。"
        "「そのとおりにやってみてください」と実行させただけだと8件中0件で、"
        "止まらずに8手順とも完了した。"
        "同じ実行の指示に「できないところがあったらそこで止まって理由を書いてください」を"
        "足すと8件中8件で、8手順すべてで止まった。"
        "各手順の開始時点で手元に必要なものを先に出させると8件中7件で、"
        "前の手順の成果物として存在しないものを2か所名指しした。"
        "実行させただけの回が穴を1件も報告しなかったのは、書かれていないことを"
        "自分で決めて、8手順とも完了で終えたため。"
        "差は実行させたかどうかではなく、できないときに止まってよいと"
        "伝えたかどうかで出ている。"
    )
    (OUT / "runbook-find-holes.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def runbook_silent_completion_chart() -> None:
    """「そのとおりにやってみて」だけで頼んだとき、各手順で何件を自分で決めたか。

    実測（2026-08-12・同じ手順書）。返ってきた実行記録から、手順書に
    書かれていない決定を人が数え、あとから申告させた件数と突き合わせた。
    """
    steps = [
        ("1 メールから集める", 3),
        ("2 共有フォルダに保存", 1),
        ("3 ファイル名を変更", 2),
        ("4 金額を確認・差し戻す", 3),
        ("5 明細表を添付して連絡", 3),
        ("6 経理から承認", 0),
        ("7 上長に提出", 1),
        ("8 記録を残す", 1),
    ]
    total = sum(n for _, n in steps)
    left = 232
    unit = 26
    top, row_h = 96, 28
    bottom = top + len(steps) * row_h + 16
    facts = [
        ("この実行で「止まった」と報告された手順", "0 / 8", "box-bad", "t-bad"),
        ("「完了しました」で終わった手順", "8 / 8", "box-bad", "t-bad"),
        ("あとから「自分で決めたこと」を挙げさせたときの申告", "12 件", "box-quiet", "t-sm"),
        ("決めるその場で「仮置き」と印を付けさせた場合", "12 / 12 一致", "box-good", "t-good"),
    ]
    height = bottom + len(facts) * (26 + 8) + 46
    assert left + 8 * unit + 60 <= WIDTH - 18

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「この手順書のとおりにやってみてください」だけで頼んだとき、"
        "各手順で自分で決めた数</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "手順書に書かれていないのに値を決めた箇所を、返ってきた実行記録から数えた。"
        f"全8手順で計{total}件。</text>\n",
    ]
    for index, (name, count) in enumerate(steps):
        y = top + index * row_h
        parts.append(f'<text class="t" x="18" y="{y + 15}">{_esc(name)}</text>\n')
        for i in range(count):
            parts.append(
                f'<rect class="box-bad" x="{left + i * unit}" y="{y}" '
                f'width="{unit - 6}" height="18" rx="3"/>\n'
            )
        label = f"{count}件を自分で決めた" if count else "決めた値なし"
        cls = "t-bad" if count else "t-sm"
        parts.append(
            f'<text class="{cls}" x="{left + 8 * unit}" y="{y + 14}">{_esc(label)}</text>\n'
        )
    for index, (label, value, box, text_class) in enumerate(facts):
        y = bottom + index * (26 + 8)
        parts.append(
            f'<rect class="{box}" x="18" y="{y}" width="666" height="26" rx="6"/>\n'
        )
        parts.append(f'<text class="t" x="30" y="{y + 18}">{_esc(label)}</text>\n')
        parts.append(
            f'<text class="{text_class}" x="560" y="{y + 18}">{_esc(value)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        f"※ 実際に決めていたのは{total}件だが、あとから挙げさせた申告は12件。"
        "漏れた2件は、値を書かずに黙って進んだ判断だった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 決めた値を、決めるその場で「仮置き」と印を付けさせると、"
        "本文の印と最後の一覧が12件で一致した。</text>\n"
    )
    alt = (
        "「この手順書のとおりにやってみてください」とだけ頼んだときに、"
        "各手順でいくつの値を自分で決めたかを示した図。"
        "手順1のメールから集めるで3件、手順2の共有フォルダに保存で1件、"
        "手順3のファイル名を変更で2件、手順4の金額を確認し差し戻すで3件、"
        "手順5の明細表を添付して連絡で3件、手順6の経理から承認で0件、"
        "手順7の上長に提出で1件、手順8の記録を残すで1件。合計14件。"
        "この実行で止まったと報告された手順は8つのうち0。"
        "完了しましたで終わった手順は8つのうち8。"
        "あとから自分で決めたことを挙げさせたときの申告は12件で、"
        "実際に決めていた14件より2件少ない。"
        "漏れた2件は、値を書かずに黙って進んだ判断だった。"
        "決めた値を、決めるその場で仮置きと印を付けさせた場合は、"
        "本文の印と最後の一覧が12件で一致した。"
    )
    (OUT / "runbook-silent-completion.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def listing_facts_vs_flourish_chart() -> None:
    """フリマの商品説明文。盛り語が減ると、メモの事実がいくつ残るか。

    実測（2026-08-14・架空の出品メモ19行から23項目を機械で照合）。
    盛り語は先に決めた49語のうち、説明文の本文に出たものだけを数えた
    （〔私が確かめること〕欄の「書いていません」という説明は数えない）。
    """
    rows = [
        ("そのまま頼む", 14, 14, False),
        ("＋「書いていないことは書くな」", 17, 0, False),
        ("＋〔私が確かめること〕を作らせる", 21, 1, False),
        ("＋不明も本文に書かせる", 23, 0, True),
    ]
    total = 23
    label_x = 18
    bar_x, bar_max = 250, 300
    row_h, gap_y = 30, 20
    top = 104
    height = top + len(rows) * (row_h + gap_y) - gap_y + 70
    assert bar_x + bar_max + 150 <= WIDTH - 18, bar_x + bar_max + 150

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "盛りが入ったぶんだけ、メモの事実が落ちている</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ架空の出品メモ（19行）。頼み方だけを変えて、返ってきた説明文を機械で照合した。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">メモの23項目のうち、説明文に残った数</text>\n',
        f'<text class="t-xs" x="{bar_x + bar_max + 62}" y="{top - 12}">本文の盛り語</text>\n',
    ]
    for index, (name, kept, flourish, best) in enumerate(rows):
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
        flourish_class = "t-bad" if flourish >= 10 else "t-sm"
        parts.append(
            f'<text class="{flourish_class}" x="{bar_x + bar_max + 62}" y="{y + 20}">'
            f"{flourish}件</text>\n"
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 50}">'
        "※ そのまま頼んだ回で落ちた9項目は、なめし方が不明・金具の材質が不明・"
        "水濡れは試していない・金具の耐久は試していない・追跡なし、など。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 32}">'
        "※ 禁止だけを足すと盛り語は0件になるが、"
        "落ちた6項目のうち5項目が「不明」「試していない」「追跡なし」だった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 3行目に残った盛り語1件は「それ以外に目立った傷や汚れはありません」。"
        "確かめていない箇所まで含めて言い切っている。</text>\n"
    )
    alt = (
        "架空の出品メモ19行から作った商品説明文を、頼み方を4通りに変えて機械で照合した図。"
        "メモから取り出した23項目のうち説明文に残った数と、"
        "先に決めた49語の盛り語のうち本文に出た数を並べている。"
        "そのまま頼むと、残った事実は23項目中14項目で、盛り語は14件だった。"
        "落ちた9項目は、制作時間、なめし方と産地が不明、金具の材質が不明、"
        "色ムラが1ミリであること、水濡れは試していない、金具の耐久は試していない、"
        "価格、普通郵便で追跡なし、同じ型を3個作った、である。"
        "メモに書いていないことは書かないでくださいと足すと、盛り語は0件になるが、"
        "残った事実は17項目にとどまった。"
        "落ちた6項目のうち5項目は、なめし方が不明、金具の材質が不明、水濡れは試していない、"
        "金具の耐久は試していない、追跡なし、で、いずれも買う人に不利な情報である。"
        "良し悪しの言葉は引用できるときだけ使い、書けないものは私が確かめることとして"
        "箇条書きにしてくださいと足すと、事実は21項目まで戻り、本文に残った盛り語は1件になった。"
        "その1件はそれ以外に目立った傷や汚れはありませんという一文で、"
        "確かめていない箇所まで含めて言い切っている。"
        "さらに不明と試していない項目と追跡の有無を本文の中に書いてくださいと足すと、"
        "盛り語0件のまま23項目すべてが残った。"
        "つまり盛りが入った量だけ事実が落ちており、禁止だけを渡すと不利な情報まで一緒に消える。"
    )
    (OUT / "listing-facts-vs-flourish.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def reply_terms_survive_chart() -> None:
    """取引先への返事。丁寧さを強めるほど、こちらが決めた条件が文面から消える。

    実測（2026-08-14・先に決めた条件8件を11の文字列に分解して照合）。
    ぼかし語15語は先に決め、材料（条件＋相手のメール）に1件も無いことを確かめてある。
    """
    rows = [
        ("そのまま「角が立たないように」", 4, 8, False),
        ("「できるだけ丁寧に」を足す", 0, 9, False),
        ("「数字と期日は一字一句そのまま」", 11, 0, True),
    ]
    total = 11
    label_x = 18
    bar_x, bar_max = 258, 290
    row_h, gap_y = 32, 24
    top = 106
    height = top + len(rows) * (row_h + gap_y) - gap_y + 88
    assert bar_x + bar_max + 148 <= WIDTH - 18, bar_x + bar_max + 148

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "丁寧にするほど、自分が決めた条件が文面から消える</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ材料（先に決めた条件8件＋相手のメール）。頼み方だけを変えた。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">条件の11の文字列のうち、文面に残った数</text>\n',
        f'<text class="t-xs" x="{bar_x + bar_max + 60}" y="{top - 12}">ぼかし語</text>\n',
    ]
    for index, (name, kept, hedge, best) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        width = round(bar_max * kept / total)
        parts.append(
            f'<text class="t-sm" x="{label_x}" y="{y + 21}">{_esc(name)}</text>\n'
        )
        parts.append(
            f'<rect class="bar-old" x="{bar_x}" y="{y + 5}" '
            f'width="{bar_max}" height="{row_h - 10}" rx="3" opacity="0.35"/>\n'
        )
        if width:
            klass = "bar-new" if best else "bar-in"
            parts.append(
                f'<rect class="{klass}" x="{bar_x}" y="{y + 5}" '
                f'width="{width}" height="{row_h - 10}" rx="3"/>\n'
            )
        value_class = "t-accent" if best else ("t-bad" if kept == 0 else "t-sm")
        parts.append(
            f'<text class="{value_class}" x="{bar_x + width + 10}" y="{y + 21}">'
            f"{kept}件</text>\n"
        )
        hedge_class = "t-bad" if hedge >= 8 else "t-sm"
        parts.append(
            f'<text class="{hedge_class}" x="{bar_x + bar_max + 60}" y="{y + 21}">'
            f"{hedge}件</text>\n"
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 68}">'
        "※ 消えたのは 15,000円・7日以内・銀行振込・8月29日・著作権の譲渡・30分まで、など。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 50}">'
        "※ 消えるだけでなく反転する。「これより早くはできない」が"
        "「早められるよう進めてまいります」になった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 32}">'
        "※ ぼかし語15語は先に決めたもの。条件にも相手のメールにも1件も無い"
        "（書く工程で入っている）。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ どの返事も、読むかぎり礼儀正しい。条件と並べるまで、緩んだことに気づけない。</text>\n"
    )
    alt = (
        "取引先への返事の文面を、頼み方を3通りに変えて機械で照合した図。"
        "先に自分で決めた条件8件を11の文字列に分解し、文面にそのまま残った数を数えた。"
        "あわせて、条件を緩めるぼかし語15語が何件出たかも数えている。"
        "角が立たないように書いてくださいと頼むと、残った条件は11のうち4件で、ぼかし語は8件だった。"
        "できるだけ丁寧に、相手の気分を害さないようにと足すと、残った条件は0件になり、"
        "ぼかし語は9件に増えた。48,000円も9月12日も修正2回も、文面から丸ごと消えている。"
        "私が決めた条件の数字と期日は一字一句そのまま文面に書いてください、"
        "言い換えやぼかしをしないでください、と足すと、11件すべてが残り、ぼかし語は0件になった。"
        "消えたのは、ページ追加1ページ15,000円、支払いは納品後7日以内、銀行振込、"
        "素材は8月29日まで、著作権の譲渡、打ち合わせは1回30分まで、などである。"
        "消えるだけでなく反転もしており、これより早くはできないという条件が、"
        "早められるよう進めてまいりますという文になった。"
        "ぼかし語15語は先に決めたもので、条件にも相手のメールにも1件も出てこない。"
        "つまり書く工程で入っている。どの返事も読むかぎり礼儀正しく、"
        "条件と並べるまで緩んだことに気づけない。"
    )
    (OUT / "reply-terms-survive.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def hourly_rate_boundary_chart() -> None:
    """同じ作業記録から出る時給が、線引きだけでどれだけ動くか。

    実測（2026-08-14・架空の作業記録26行・報酬5件）。
    真値は記録から計算した（手で書いていない）。
    """
    rows = [
        ("制作だけ", 5091, "A社 5,143 / C社 4,932"),
        ("制作＋修正", 3490, "A社 3,972 / C社 2,748"),
        ("制作＋修正＋打ち合わせ", 3231, "A社 3,600 / C社 2,517"),
        ("全部（提案・事務も）", 2827, "A社 3,600 / C社 2,517"),
    ]
    biggest = max(v for _, v, _ in rows)
    label_x = 18
    bar_x, bar_max = 210, 210
    row_h, gap_y = 30, 22
    top = 106
    height = top + len(rows) * (row_h + gap_y) - gap_y + 88
    assert bar_x + bar_max + 250 <= WIDTH - 18, bar_x + bar_max + 250

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ記録・同じ報酬。時給は「線引き」だけで1.8倍動く</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の作業記録26行（報酬98,000円）。何を案件の作業時間に含めるかを変えただけ。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">全体の時給</text>\n',
        f'<text class="t-xs" x="{bar_x + bar_max + 96}" y="{top - 12}">案件ごとの時給（一部）</text>\n',
    ]
    for index, (name, value, detail) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        width = round(bar_max * value / biggest)
        parts.append(
            f'<text class="t-sm" x="{label_x}" y="{y + 20}">{_esc(name)}</text>\n'
        )
        parts.append(
            f'<rect class="bar-old" x="{bar_x}" y="{y + 4}" '
            f'width="{bar_max}" height="{row_h - 8}" rx="3" opacity="0.35"/>\n'
        )
        klass = "bar-new" if index == 0 else "bar-in"
        parts.append(
            f'<rect class="{klass}" x="{bar_x}" y="{y + 4}" '
            f'width="{width}" height="{row_h - 8}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-accent" x="{bar_x + width + 10}" y="{y + 20}">'
            f"{value:,}円</text>\n"
        )
        parts.append(
            f'<text class="t-sm" x="{bar_x + bar_max + 96}" y="{y + 20}">{_esc(detail)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 68}">'
        "※ 案件ごとの計算そのものは、5件とも真値と完全に一致した。"
        "間違うのは計算ではない。</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="18" y="{height - 46}">'
        "※ そのまま頼むと、どの線引きを使ったかは書かれない。読む側は1つの答えだと思う。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 24}">'
        "※ 順位も入れ替わる。全部入れるとE社が最下位（2,341円）、"
        "制作＋修正だけだとC社が最下位（2,748円）。</text>\n"
    )
    alt = (
        "同じ架空の作業記録26行と報酬98,000円から出した全体の時給を、"
        "作業時間の線引きを4通りに変えて比べた図。"
        "制作だけを案件の作業時間に含めると、全体の時給は5,091円になる。"
        "制作と修正を含めると3,490円、制作と修正と打ち合わせを含めると3,231円、"
        "提案や事務まで全部含めると2,827円になる。同じ記録から出る数字が1.8倍動いている。"
        "案件ごとに見ると、A社サイトは5,143円から3,600円へ、"
        "C社ロゴは4,932円から2,517円へ動く。"
        "案件ごとの計算そのものは、5件とも記録から計算した真値と完全に一致していた。"
        "つまり間違うのは計算ではない。"
        "そのまま頼むと、どの線引きを使ったかは返りのどこにも書かれず、"
        "読む側は1つの答えだと思って受け取ることになる。"
        "順位も入れ替わり、全部入れるとE社記事が最下位で2,341円、"
        "制作と修正だけだとC社ロゴが最下位で2,748円になる。"
        "いちばん割に合わない案件が、線引きによって変わる。"
    )
    (OUT / "hourly-rate-boundary.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def transcript_keep_vs_rewrite_chart() -> None:
    """「整えてください」と「種類を並べて渡す」で、文字起こしに何が起きたか。

    実測（2026-08-13・架空の電話打ち合わせの文字起こし28行）。
    仕込み＝誤変換5件・食い違い2組・言い切りの度合い4件。
    判定は Python の行差分（`docs/evidence/tidy-transcript-without-rewriting.md`）。
    """
    rows = [
        ("誤変換5件（人事移動・決済など）", ["5/5 直った"], True, ["5/5 直った"], True),
        ("40台/50台・加藤/佐藤の食い違い", ["自発的に指摘した"], True,
         ["〔要確認〕を付けて両方残した"], True),
        ("発言の言い回し（28行）", ["12行が別の語に置き換わった", "（うちの→弊社・たぶん→おそらく）"],
         False, ["置き換え 0行"], True),
        ("「たぶん」「はず」など確度4件", ["4件とも書き換わった", "「遅れたはず」→「遅れました」"],
         False, ["4件とも原文のまま"], True),
        ("直した箇所の申告", ["誤変換5件だけ", "（実際に変わったのは25行）"], False,
         ["直した種類を自分から明記"], True),
    ]
    label_x, naive_x, rule_x = 18, 268, 496
    line_h, row_pad = 16, 14
    top = 96
    ys = []
    y = top
    for _, nl, _, rl, _ in rows:
        ys.append(y)
        y += max(len(nl), len(rl)) * line_h + row_pad
    height = y + 44
    assert rule_x + 210 <= WIDTH, rule_x

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ文字起こし28行を、2通りの頼み方で整えさせた結果</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の電話打ち合わせ。誤変換5件・食い違い2組・言い切りの度合い4件を先に仕込んだ。</text>\n",
        f'<text class="t-bad" x="{naive_x}" y="{top - 22}">「読みやすく整えて」</text>\n',
        f'<text class="t-accent" x="{rule_x}" y="{top - 22}">種類を並べて渡す</text>\n',
    ]
    for (label, naive_lines, naive_ok, rule_lines, rule_ok), y0 in zip(rows, ys):
        parts.append(f'<text class="t" x="{label_x}" y="{y0 + 12}">{_esc(label)}</text>\n')
        for col_x, lines, ok in ((naive_x, naive_lines, naive_ok), (rule_x, rule_lines, rule_ok)):
            cls = "t-good" if ok else "t-bad"
            for i, line in enumerate(lines):
                use = cls if i == 0 else "t-xs"
                parts.append(
                    f'<text class="{use}" x="{col_x}" y="{y0 + 12 + i * line_h}">'
                    f"{_esc(line)}</text>\n"
                )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 26}">'
        "※ どちらの頼み方でも修正と発見は同じだけ働く。違いは「発言がその人の言葉のまま残るか」。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ 判定はすべて行差分の機械照合。真値が音源にしか無い「4日」は、どちらの頼み方でも見つからない。</text>\n"
    )
    alt = (
        "同じ文字起こし28行を2通りの頼み方で整えさせて、仕込んだ誤りがどうなったかを"
        "並べた比較表。仕込みは、文脈から確定できる誤変換5件、文脈から確定できない"
        "食い違い2組（40台と50台、加藤と佐藤）、変えてはいけない言い切りの度合い4件。"
        "「読みやすく整えてください」と頼むと、誤変換は5件とも直り、食い違いも自発的に"
        "指摘されたが、発言の言い回しは28行中12行が元の発言に無い語へ置き換わり"
        "（うちの、が弊社に、たぶん、がおそらくに）、言い切りの度合いは4件とも書き換わって、"
        "遅れたはずです、が、遅れました、という断定に変わった。直した箇所の申告は"
        "誤変換5件だけで、実際に変わった25行に対して大きく足りない。"
        "一方、取り除いてよい種類と変えてはいけない種類を並べて渡すと、"
        "誤変換の修正5件と食い違いの発見は同じまま、言い回しの置き換えは0行になり、"
        "言い切りの度合い4件は原文のまま残り、食い違いには要確認の印が付いて両方残った。"
        "どちらの頼み方でも、真値が音源にしか無い、4日、の聞き間違いは見つからない。"
    )
    (OUT / "transcript-keep-vs-rewrite.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def blog_research_coverage_chart() -> None:
    """貼った見出し32件のうち、返ってきた一覧に何件残ったか。

    実測（2026-08-13・架空の上位6本の見出し39件＝重複を除くと32件）。
    判定は文字列照合（論点欄か引用欄に、原文どおりの見出しが出た数）。
    証拠＝`docs/evidence/blog-research-from-headings.md`。
    """
    rows = [
        ("表の形で、落とさない2行つき", 32, "26行", True),
        ("毎朝の形に短くした（1回目）", 22, "22行", False),
        ("毎朝の形に短くした（2回目）", 19, "16行", False),
        ("短く＋落とさせない一文（1回目）", 29, "27行", True),
        ("短く＋落とさせない一文（2回目）", 32, "26行", True),
    ]
    total = 32
    label_x = 18
    bar_x, bar_max = 272, 296
    row_h, gap_y = 28, 18
    top = 104
    height = top + len(rows) * (row_h + gap_y) - gap_y + 70
    assert bar_x + bar_max + 108 <= WIDTH - 18, bar_x + bar_max + 108

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "自動実行の形に短くすると、貼った見出しが静かに消える</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の上位6本の見出し32件（重複を除く）を貼って、論点の一覧を出させた。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "一覧に出た見出し（32件中）</text>\n",
        f'<text class="t-xs" x="{bar_x + bar_max + 16}" y="{top - 12}">返りの行数</text>\n',
    ]
    for index, (name, kept, lines, good) in enumerate(rows):
        y = top + index * (row_h + gap_y)
        width = round(bar_max * kept / total)
        parts.append(f'<text class="t-sm" x="{label_x}" y="{y + 19}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="bar-old" x="{bar_x}" y="{y + 4}" '
            f'width="{bar_max}" height="{row_h - 8}" rx="3" opacity="0.35"/>\n'
        )
        parts.append(
            f'<rect class="{"bar-new" if good else "bar-in"}" x="{bar_x}" y="{y + 4}" '
            f'width="{width}" height="{row_h - 8}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="{"t-accent" if good else "t-bad"}" '
            f'x="{bar_x + width + 10}" y="{y + 19}">{kept}件</text>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{bar_x + bar_max + 16}" y="{y + 19}">{lines}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 50}">'
        "※ 短くしたときに落としたのは「まとめた言い方に置き換えないで」"
        "「1本だけの論点も省かずに」の2行だけ。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 32}">'
        "※ 同じ指示文を2回走らせて論点名が完全一致した数＝"
        "短くしただけ 4件 ／ 落とさせない一文つき 21件。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 引用の捏造は5回とも0件、記事番号と引用の食い違いも0件。"
        "消えるほうだけが起きている。</text>\n"
    )
    alt = (
        "架空の上位6本の記事の見出し32件を貼って論点の一覧を出させ、"
        "貼った見出しのうち何件が一覧に残ったかを頼み方ごとに並べた横棒グラフ。"
        "表の形で、まとめた言い方に置き換えないでください、"
        "1本にしか出てこない論点も省かずに全部載せてください、の2行を付けて頼むと、"
        "32件中32件が一覧に出た。返りは26行。"
        "毎朝の自動実行に載せるために前置きを禁じて行の形だけを決め、"
        "その2行を落とすと、1回目は32件中22件で22行、"
        "同じ指示文の2回目は32件中19件で16行しか出ず、10件以上が消えた。"
        "落とさせない一文を足し直すと、1回目は32件中29件で27行、"
        "2回目は32件中32件で26行まで戻った。"
        "短くしたときに落としたのは、まとめた言い方に置き換えないで、と、"
        "1本だけの論点も省かずに、の2行だけである。"
        "同じ指示文を2回走らせて論点名が完全に一致した数は、"
        "短くしただけの場合が4件、落とさせない一文を付けた場合が21件だった。"
        "なお引用の捏造は5回の実測すべてで0件、記事番号と引用の食い違いも0件で、"
        "起きているのは作り話ではなく静かな欠落のほうだけだった。"
    )
    (OUT / "blog-research-coverage.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def blog_research_volume_drift_chart() -> None:
    """同じ指示文で検索回数を2回聞いた結果の食い違い。

    実測（2026-08-13）。別々の新しいセッションに、1文字も同じ指示文を渡した。
    証拠＝`docs/evidence/blog-research-from-headings.md`。
    """
    rows = [
        ("食洗機 工事不要", "1位・約12,000", "1位・8,000〜12,000", False),
        ("タンク式食洗機", "2位・約9,900", "4位・4,000〜7,000", True),
        ("食洗機 賃貸", "3位・約8,100", "8位・2,000〜3,500", True),
        ("卓上食洗機", "4位・約8,100", "2位・6,000〜10,000", True),
        ("食洗機 一人暮らし", "5位・約5,400", "3位・5,000〜8,000", True),
        ("食洗機 分岐水栓", "6位・約4,400", "6位・3,000〜5,000", False),
        ("食洗機 置き場所", "8位・約2,900", "9位・1,500〜3,000", False),
        ("食洗機 設置", "10位・約2,400", "10位・1,500〜3,000", False),
    ]
    label_x, first_x, second_x = 18, 250, 470
    row_h = 24
    top = 100
    height = top + len(rows) * row_h + 74
    assert second_x + 200 <= WIDTH - 18, second_x + 200

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ指示文で「月間の検索回数」を2回聞いた結果</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "別々の新しいセッションに、1文字も同じ指示文を渡した。"
        "20個のうち両方に出たのは11個。</text>\n",
        f'<text class="t-xs" x="{label_x}" y="{top - 14}">キーワード</text>\n',
        f'<text class="t-xs" x="{first_x}" y="{top - 14}">1回目</text>\n',
        f'<text class="t-xs" x="{second_x}" y="{top - 14}">2回目（同じ指示文）</text>\n',
    ]
    for index, (kw, first, second, moved) in enumerate(rows):
        y = top + index * row_h + 16
        cls = "t-bad" if moved else "t-sm"
        parts.append(f'<text class="t" x="{label_x}" y="{y}">{_esc(kw)}</text>\n')
        parts.append(f'<text class="{cls}" x="{first_x}" y="{y}">{_esc(first)}</text>\n')
        parts.append(f'<text class="{cls}" x="{second_x}" y="{y}">{_esc(second)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 52}">'
        "※ 赤い行＝順位か桁が動いたもの。"
        "「食洗機 賃貸」は記事の主題そのもので、3位→8位・数字で2.3〜4倍ちがう。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 34}">'
        "※ どちらの回も「ツールに接続できないので推定です」と自分から断っている。"
        "断ったうえで順位が並ぶ。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "※ 20個のうち9個は入れ替わった（1回目だけに出た語・2回目だけに出た語が9個ずつ）。</text>\n"
    )
    alt = (
        "同じ指示文で月間の検索回数を2回聞いた結果を並べた表。"
        "別々の新しいセッションに、1文字も同じ指示文を渡している。"
        "挙がった20個のキーワードのうち、両方の回に出たのは11個だけで、"
        "9個は入れ替わった。両方に出た語も数字が食い違う。"
        "食洗機 工事不要は1回目が1位で約12,000、2回目も1位で8,000から12,000。"
        "タンク式食洗機は2位で約9,900だったものが4位で4,000から7,000。"
        "食洗機 賃貸は3位で約8,100だったものが8位で2,000から3,500へ動いた。"
        "これは記事の主題そのもののキーワードで、順位で5つ、数字で2.3倍から4倍ちがう。"
        "卓上食洗機は4位で約8,100が2位で6,000から10,000へ、"
        "食洗機 一人暮らしは5位で約5,400が3位で5,000から8,000へ動いた。"
        "食洗機 分岐水栓、食洗機 置き場所、食洗機 設置は順位がほぼ動いていない。"
        "どちらの回も、検索ボリュームのツールに接続できないので推定ですと自分から断ったうえで、"
        "具体的な順位と数字を並べている。"
    )
    (OUT / "blog-research-volume-drift.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def writing_check_three_asks_chart() -> None:
    """発注書14項目と原稿を突き合わせる、3通りの頼み方の比較。

    実測（2026-08-13・架空の発注書14項目と、違反8件を仕込んだ架空の原稿）。
    判定はすべて Python の文字列照合。
    証拠＝`docs/evidence/writing-check-against-spec.md`。
    """
    rows = [
        ("違反8件のうち見つけた数", "8/8", True, "8/8", True, "8/8", True),
        ("誤って違反にした数", "0件", True, "0件", True, "0件", True),
        ("14項目に判定が付いたか", "表で14項目", True, "14/14", True, "14/14", True),
        ("本人が言った件数", "「7つ」", False, "「8項目」", True, "—", None),
        ("文字数の申告（実測823字）", "約814字", False, "823字", True, "823字", True),
        ("最長の文（実測46字）", "47字", False, "46字", True, "46字", True),
        ("原稿の一文を引用したか", "指摘ごとに引用", True, "根拠として引用", True, "12/14に引用", True),
        ("引用が原稿に実在したか", "—", None, "—", None, "12/12", True),
    ]
    label_x, cols = 18, (240, 380, 520)
    row_h = 26
    top = 108
    height = top + len(rows) * row_h + 82
    assert cols[2] + 140 <= WIDTH - 18, cols[2] + 140

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "発注書14項目との突き合わせ — 頼み方を3通り試した</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の発注書14項目と、違反を8件仕込んだ架空の原稿。判定はすべて文字列照合。</text>\n",
        f'<text class="t-bad" x="{cols[0]}" y="{top - 30}">「確認して」</text>\n',
        f'<text class="t-accent" x="{cols[1]}" y="{top - 30}">1項目ずつ</text>\n',
        f'<text class="t-accent" x="{cols[2]}" y="{top - 30}">＋根拠を引用</text>\n',
        f'<text class="t-xs" x="{cols[0]}" y="{top - 14}">（素朴）</text>\n',
        f'<text class="t-xs" x="{cols[1]}" y="{top - 14}">（飛ばさないで）</text>\n',
        f'<text class="t-xs" x="{cols[2]}" y="{top - 14}">（原稿の一文）</text>\n',
    ]
    for index, (label, a, aok, b, bok, c, cok) in enumerate(rows):
        y = top + index * row_h + 16
        parts.append(f'<text class="t" x="{label_x}" y="{y}">{_esc(label)}</text>\n')
        for x, val, ok in ((cols[0], a, aok), (cols[1], b, bok), (cols[2], c, cok)):
            cls = "t-sm" if ok is None else ("t-good" if ok else "t-bad")
            parts.append(f'<text class="{cls}" x="{x}" y="{y}">{_esc(val)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 64}">'
        "※ どの頼み方でも、違反そのものは8件とも見つかっている。"
        "違いは「数字と件数が合うか」だけ。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 44}">'
        "※ 素朴版は、自分が作った表に8件のNGを並べておいて、"
        "冒頭の要約では「7つ」と書いた（読むのは要約のほう）。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 24}">'
        "※ 曖昧な項目（価格に触れたか）は、頼み方によって"
        "「判断できない」と「違反の可能性が高い」に割れた。</text>\n"
    )
    alt = (
        "架空の発注書14項目と、違反を8件仕込んだ架空の原稿を突き合わせさせて、"
        "3通りの頼み方を比べた表。素朴に確認してと頼んだ場合、1項目ずつ飛ばさずに"
        "判定を付けさせた場合、さらに根拠として原稿の一文を引用させた場合の3つ。"
        "仕込んだ違反8件は、3通りとも8件すべて見つかり、誤って違反にしたものは"
        "どれも0件だった。違いは数字のほうに出た。素朴に頼んだ場合、"
        "自分が作った判定表にはNGが8件並んでいるのに、冒頭の要約では"
        "修正が必要な項目が7つと書いた。文字数の申告は約814字で、実測の823字と合わない。"
        "最長の文も47字と申告したが実測は46字だった。"
        "1項目ずつ順番に、項目を飛ばさないでくださいと頼むと、14項目すべてに判定が付き、"
        "件数の申告も8項目で正しく、文字数823字も最長の文46字も実測と一致した。"
        "さらに根拠として原稿の一文をそのまま引用させると、14項目のうち12項目に引用が付き、"
        "その12件はすべて原稿に実在した。残る2項目は引用できる箇所がないと明記された。"
        "なお、価格に触れたかどうかという曖昧な項目は、頼み方によって"
        "原稿からは判断できないと、違反の可能性が高いに割れた。"
    )
    (OUT / "writing-check-three-asks.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def writing_fix_loses_your_text_chart() -> None:
    """「発注書に合うように直して」と頼んだときに、原稿がどうなるか。

    実測（2026-08-13・同じ架空の原稿28文）。判定は文字列照合。
    証拠＝`docs/evidence/writing-check-against-spec.md`。
    """
    bars = [
        ("自分が書いた文が、そのまま残った数", 1, 28, "28文中 1文"),
        ("発注書の違反が直った数", 8, 8, "8件中 8件"),
    ]
    label_x = 18
    bar_x, bar_max = 300, 268
    row_h, gap_y = 30, 22
    top = 100
    height = top + len(bars) * (row_h + gap_y) - gap_y + 116
    assert bar_x + bar_max + 116 <= WIDTH - 18, bar_x + bar_max + 116

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「発注書に合うように直してください」と頼んだ結果</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ架空の原稿（28文）。違反はきれいに直る。残らないのは、自分の文のほう。</text>\n",
    ]
    for index, (name, value, total, note) in enumerate(bars):
        y = top + index * (row_h + gap_y)
        width = round(bar_max * value / total)
        good = value == total
        parts.append(f'<text class="t-sm" x="{label_x}" y="{y + 20}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="bar-old" x="{bar_x}" y="{y + 4}" '
            f'width="{bar_max}" height="{row_h - 8}" rx="3" opacity="0.35"/>\n'
        )
        parts.append(
            f'<rect class="{"bar-new" if good else "bar-in"}" x="{bar_x}" y="{y + 4}" '
            f'width="{max(width, 3)}" height="{row_h - 8}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="{"t-good" if good else "t-bad"}" '
            f'x="{bar_x + max(width, 3) + 10}" y="{y + 20}">{_esc(note)}</text>\n'
        )
    base = top + len(bars) * (row_h + gap_y) + 16
    parts.append(
        f'<text class="t-bad" x="18" y="{base}">'
        "そして、原稿に無かった「参考にしたページ」が4件立った</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="18" y="{base + 20}">'
        "元の原稿のURL 0件 → 直した版 4件（厚生労働省・業界団体・規格のPDFなど）。</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="18" y="{base + 38}">'
        "自分は1つも開いていない。そのまま出せば「参考にした」と申告したことになる。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 24}">'
        "※ 同じ原稿を「確認して」と頼んだときは、"
        "URLは補われず「ご自身で列挙してください」と返ってきた。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 6}">'
        "※ 直した版には申し送りが付いていた。"
        "付いていても、貼って出すのは自分なので、読まなければ同じこと。</text>\n"
    )
    alt = (
        "同じ架空の原稿28文に、発注書に合うように直してくださいと頼んだ結果を並べた図。"
        "発注書の違反8件は8件とも直った。一方、自分が書いた28の文のうち、"
        "直した版にそのまま残ったのは1文だけだった。"
        "つまり納品物のほとんどが、自分の書いた文ではなくなる。"
        "さらに、元の原稿にはURLが1件も無かったのに、直した版には"
        "参考にしたページとして4件のURLが立った。"
        "厚生労働省のガイドラインや業界団体の資料、規格のページなどで、"
        "自分は1つも開いていない。そのまま出せば、参考にしたと申告したことになる。"
        "同じ原稿を、直さずに確認してくださいと頼んだときは、URLは補われず、"
        "実際に参照したページをご自身で列挙してくださいと返ってきた。"
        "直した版には申し送りが付いていたが、付いていても、"
        "貼って出すのは自分なので、読まなければ同じことである。"
    )
    (OUT / "writing-fix-loses-your-text.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def offer_verdict_vs_claims_chart() -> None:
    """同じ中身の勧誘文2種に「これは詐欺?」と聞いた結果の比較。

    実測（2026-08-13・架空のAI副業講座の勧誘文）。検証できない主張5件は両方に共通で、
    文面の丁寧さだけが違う。判定の語は動いたが、確かめられないものは1件も減っていない。
    証拠＝`docs/evidence/too-good-offer-checklist.md`（実測環境の注記もそちら）。
    """
    left_x, right_x = 18, 372
    box_w = 330
    top = 64
    box_h = 118
    claims = [
        "受講生の92%が初収益（出所は「当社調べ」だけ）",
        "メディア掲載実績（媒体の名前が無い）",
        "返金保証（条件が書かれていない）",
        "通常価格298,000円→98,000円（根拠が無い）",
        "運営会社・所在地・特商法表記が無い",
    ]
    cl_top = top + box_h + 44
    cl_h = len(claims) * 19 + 34
    height = cl_top + cl_h + 46

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ中身の勧誘文2種に「これは詐欺?」と聞いた結果（実測の一例）</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空のAI副業講座。検証できない主張5件は両方に共通で、文面の丁寧さだけが違う。</text>\n",
        f'<rect class="box-bad" x="{left_x}" y="{top}" width="{box_w}" height="{box_h}" rx="8"/>\n',
        f'<rect class="box-quiet" x="{right_x}" y="{top}" width="{box_w}" height="{box_h}" rx="8"/>\n',
        f'<text class="t-strong" x="{left_x + 16}" y="{top + 26}">粗い版（SNSのDM風）</text>\n',
        f'<text class="t-sm" x="{left_x + 16}" y="{top + 46}">「残り3名」「本日23:59まで」</text>\n',
        f'<text class="t-sm" x="{left_x + 16}" y="{top + 62}">「迷っている時間はありません」</text>\n',
        f'<text class="t-bad" x="{left_x + 16}" y="{top + 92}">判定＝「黒に極めて近い」</text>\n',
        f'<text class="t-strong" x="{right_x + 16}" y="{top + 26}">整えた版（案内ページ風）</text>\n',
        f'<text class="t-sm" x="{right_x + 16}" y="{top + 46}">丁寧な敬語。急がせる言葉は</text>\n',
        f'<text class="t-sm" x="{right_x + 16}" y="{top + 62}">「お早めにご検討ください」だけ</text>\n',
        f'<text class="t-bad" x="{right_x + 16}" y="{top + 92}">判定＝「グレー（要警戒）」</text>\n',
        f'<text class="t-accent" x="18" y="{cl_top - 12}">'
        "↓ どちらの版にも、そのまま残っている「確かめられないもの」5件</text>\n",
        f'<rect class="box" x="18" y="{cl_top}" width="{684}" height="{cl_h}" rx="8"/>\n',
    ]
    for i, c in enumerate(claims):
        parts.append(
            f'<text class="t" x="34" y="{cl_top + 24 + i * 19}">・{_esc(c)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 26}">'
        "※ 文面を整えただけで判定は一段やわらいだ。判定が見ているのは中身ではなく文面。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ どちらの判定も「92%が本当か」は確かめていない（AIには確かめられない）。"
        "返りは環境によって変わる。</text>\n"
    )
    alt = (
        "同じ中身の架空の勧誘文2種にAIで、これは詐欺かと聞いた結果を並べた図。"
        "検証できない主張5件、受講生の92%が初収益で出所は当社調べだけ、"
        "メディア掲載実績で媒体の名前が無い、返金保証で条件が書かれていない、"
        "通常価格298,000円から98,000円への割引で根拠が無い、"
        "運営会社と所在地と特定商取引法に基づく表記が無い、は両方の版に共通している。"
        "残り3名や本日23時59分までのような急がせる言葉が並ぶ粗い版への判定は"
        "黒に極めて近い、だったのに対し、同じ中身を丁寧な敬語に整えた版への判定は"
        "グレー、要警戒、へ一段やわらいだ。つまり判定が見ているのは中身ではなく文面で、"
        "どちらの判定も92%が本当かどうかは確かめていない。"
        "確かめられないもの5件は文面を整えても1件も減らない。"
    )
    (OUT / "offer-verdict-vs-claims.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def proposal_sentence_check_chart() -> None:
    """素朴に書かせた提案文25文を、3つに割り当てさせた結果。

    実測（2026-08-13・架空の募集要項と、事実だけを並べた架空の素材15行）。
    判定はすべて Python の文字列照合。
    証拠＝`docs/evidence/proposal-without-inflating.md`。
    """
    segs = [
        ("A", 12, "box-good", "（A）素材の行から導ける　12文"),
        ("B", 4, "box-bad", "（B）素材より強い　4文"),
        ("C", 9, "box-quiet", "（C）素材に無い　9文"),
    ]
    strong = [
        ("デスクは自分で買い替えたことがあり、昇降デスクを1年使っている",
         "デスクまわりは自分で試行錯誤してきました"),
        ("画像の差し替えはやったことがない",
         "初回のみ手順をご共有いただけますと確実です"),
        ("SEOの勉強はしたことがない",
         "SEOを体系的に学んだ経験はありません"),
        ("キーワードを指定されればそれに沿って書ける",
         "キーワードや構成をご指定いただければ"),
    ]
    left, right = 18, WIDTH - 18
    span = right - left
    total = sum(n for _, n, _, _ in segs)
    bar_y, bar_h = 70, 26
    list_top = 152
    row_h = 46
    height = list_top + len(strong) * row_h + 62

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "素朴に書かせた提案文25文を、1文ずつ3つに割り当てさせた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の募集要項と、事実だけを並べた架空の素材15行。25文が25項目で返り、引用25件は全部下書きに実在した。</text>\n",
    ]
    x = left
    label_ys = []
    for _, count, cls, label in segs:
        w = round(span * count / total)
        parts.append(
            f'<rect class="{cls}" x="{x}" y="{bar_y}" width="{w}" height="{bar_h}" rx="3"/>\n'
        )
        label_ys.append((x, label))
        x += w
    for index, (x0, label) in enumerate(label_ys):
        cls = ("t-good", "t-bad", "t-sm")[index]
        parts.append(
            f'<text class="{cls}" x="{x0 + 4}" y="{bar_y + bar_h + 20}">{_esc(label)}</text>\n'
        )
    parts.append(
        f'<text class="t-strong" x="18" y="{list_top - 8}">'
        "（B）＝素材にある事実を、素材より強く書いた4文</text>\n"
    )
    for index, (src, drafted) in enumerate(strong):
        y = list_top + index * row_h + 14
        parts.append(
            f'<text class="t-sm" x="18" y="{y}">{_esc("素材：" + src)}</text>\n'
        )
        parts.append(
            f'<text class="t-bad" x="18" y="{y + 19}">{_esc("下書き：" + drafted)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 40}">'
        "※ 事実の捏造は0件だった。素材の数字（7本・4本・3本・8時間）は"
        "1つも書き換わっていない。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 20}">'
        "※ （C）9文のうち4文は挨拶と結び。中身のある（C）は5文で、"
        "いずれも素材の外にある申し出と見込みだった。</text>\n"
    )
    alt = (
        "架空の募集要項と、事実だけを並べた架空の素材15行を渡して素朴に書かせた"
        "提案文25文を、1文ずつ3つに割り当てさせた結果の図。"
        "素材の行から導ける文が12文、素材にある事実だが素材より強く書いてある文が4文、"
        "素材のどの行からも導けない文が9文だった。25文が25項目として返り、"
        "引用25件はすべて下書きに実在した。素材より強く書いてある4文は次のとおり。"
        "素材にはデスクは自分で買い替えたことがあり昇降デスクを1年使っているとあるのに、"
        "下書きはデスクまわりは自分で試行錯誤してきましたと書いた。"
        "素材には画像の差し替えはやったことがないとあるのに、"
        "下書きは初回のみ手順をご共有いただけますと確実ですと書いた。"
        "素材にはSEOの勉強はしたことがないとあるのに、"
        "下書きはSEOを体系的に学んだ経験はありませんと書いた。"
        "素材にはキーワードを指定されればそれに沿って書けるとあるのに、"
        "下書きはキーワードや構成をご指定いただければと書いた。"
        "なお事実の捏造は0件で、素材の数字である7本、4本、3本、8時間は1つも書き換わっていない。"
        "素材のどの行からも導けない9文のうち4文は挨拶と結びで、"
        "中身のある文は5文、いずれも素材の外にある申し出と見込みだった。"
    )
    (OUT / "proposal-sentence-check.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def proposal_who_decides_chart() -> None:
    """素材に書いていない決め事を、頼み方4通りで誰が決めたか。

    実測（2026-08-13）。証拠＝`docs/evidence/proposal-without-inflating.md`。
    """
    rows = [
        ("1週間に対応できる本数", "「週1本」", False, "「週1本」", False,
         "空欄", None, "私が決める欄", True),
        ("単価8,000円を受けるか", "出てこない", None, "出てこない", None,
         "空欄", None, "私が決める欄", True),
        ("サンプルを出すか", "無償で書くと申し出", False, "出てこない", None,
         "相談と書いた", None, "私が決める欄", True),
        ("画像差し替えの2回目以降", "「自分で進めます」", False, "出てこない", None,
         "出てこない", None, "出てこない", None),
        ("週2本への増加", "相談を約束", False, "相談を約束", False,
         "出てこない", None, "出てこない", None),
    ]
    label_x, cols = 18, (216, 356, 476, 596)
    row_h = 30
    top = 112
    height = top + len(rows) * row_h + 66
    assert cols[3] + 84 <= WIDTH - 18, cols[3] + 84

    heads = (
        (cols[0], "t-bad", "素朴に頼む", "（そのまま）"),
        (cols[1], "t-bad", "「書くな」だけ", "（禁止のみ）"),
        (cols[2], "t-sm", "〔素材に無い〕", "（空けさせる）"),
        (cols[3], "t-accent", "〔私が決める〕", "（印を残す）"),
    )
    parts = [
        '<text class="t-strong" x="18" y="26">'
        "素材に書いていない決め事を、誰が決めたか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ募集要項・同じ素材で、頼み方だけを4通りに変えた。"
        "素材にはこの5件がどれも書かれていない。</text>\n",
    ]
    for x, cls, head, sub in heads:
        parts.append(f'<text class="{cls}" x="{x}" y="{top - 32}">{_esc(head)}</text>\n')
        parts.append(f'<text class="t-xs" x="{x}" y="{top - 15}">{_esc(sub)}</text>\n')
    for index, row in enumerate(rows):
        y = top + index * row_h + 16
        parts.append(f'<text class="t" x="{label_x}" y="{y}">{_esc(row[0])}</text>\n')
        for pos, (x, _, _, _) in enumerate(heads):
            val, ok = row[1 + pos * 2], row[2 + pos * 2]
            cls = "t-sm" if ok is None else ("t-good" if ok else "t-bad")
            parts.append(f'<text class="{cls}" x="{x}" y="{y}">{_esc(val)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 44}">'
        "※ 募集要項は「1週間に対応できる本数」を書くよう求めている。"
        "禁止だけを渡すと、この必須の欄が空欄になった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 24}">'
        "※ どの頼み方でも、素材にある事実（7本・記名なし・SEO未学習）は"
        "書き換わっていない。動くのは決め事のほうだけ。</text>\n"
    )
    alt = (
        "同じ架空の募集要項と素材で頼み方だけを4通りに変えて、"
        "素材に書いていない決め事5件を誰が決めたかを比べた表。"
        "1つ目は素朴に頼む、2つ目は素材に書いていないことは書かないでくださいという禁止だけ、"
        "3つ目は書けない箇所を素材に無いと書いて空けさせる、"
        "4つ目は私が決めると印を残させる、の4通り。"
        "1週間に対応できる本数は、素朴に頼むとAIが週1本と決め、禁止だけでも週1本と決めた。"
        "空けさせると空欄になり、私が決めると印を残させたときだけ私が決める欄として残った。"
        "単価8,000円を受けるかは、素朴でも禁止だけでも出てこず、"
        "空けさせると空欄、印を残させたときだけ私が決める欄になった。"
        "サンプルを出すかは、素朴に頼むと無償で書くと申し出て、禁止だけでは出てこず、"
        "空けさせると相談と書き、印を残させたときは私が決める欄になった。"
        "画像差し替えの2回目以降は、素朴に頼んだときだけ自分で進めますと約束し、"
        "ほかの3通りでは出てこなかった。"
        "週2本への増加は、素朴でも禁止だけでも相談を約束し、ほかの2通りでは出てこなかった。"
        "募集要項は1週間に対応できる本数を書くよう求めているので、"
        "禁止だけを渡すとこの必須の欄が空欄になる。"
        "どの頼み方でも、素材にある事実である7本、記名なし、SEO未学習は書き換わっていない。"
        "動くのは決め事のほうだけである。"
    )
    (OUT / "proposal-who-decides.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def sell_price_not_asked_chart() -> None:
    """棚卸しを頼んだときに、聞いていない金額が付いてくるか。

    実測（2026-08-13・架空の会社員の箇条書き21行）。
    金額の検出は Python の正規表現（数字＋円／万円／万）。
    証拠＝`docs/evidence/sell-what-you-already-do.md`。
    """
    rows = [
        ("「私は何で稼げますか。一言で」", "言っていない", False, "3件", False),
        ("「売れそうなものを挙げて」", "言っていない", False, "4件", False),
        ("「募集されている仕事の名前に」", "言った", True, "0件", True),
        ("「相場を自分で確かめる手順を」", "言った", True, "0件", True),
    ]
    appeared = [
        "単価が時間2,000〜3,000円のあたりから始まるとして、最初の数ヶ月は月2〜5万円",
        "雛形づくりが1件1〜3万円、リストの整理が1,000件で1〜3万円あたりから",
        "引き継ぎ書の代行は（中略）1本5〜15万円くらいのレンジ",
    ]
    label_x, cols = 18, (330, 500)
    row_h = 28
    top = 104
    list_top = top + len(rows) * row_h + 40
    height = list_top + len(appeared) * 20 + 52
    assert cols[1] + 60 <= WIDTH - 18, cols[1] + 60

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "棚卸しを頼むと、聞いていない金額が付いてくる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の会社員の箇条書き21行。同じ材料で、頼み方だけを変えた。"
        "金額の数え上げは正規表現（数字＋円／万円）。</text>\n",
        f'<text class="t-sm" x="{cols[0]}" y="{top - 18}">金額を書くなと言ったか</text>\n',
        f'<text class="t-sm" x="{cols[1]}" y="{top - 18}">返りに出た金額</text>\n',
    ]
    for index, (label, said, said_ok, count, count_ok) in enumerate(rows):
        y = top + index * row_h + 16
        parts.append(f'<text class="t" x="{label_x}" y="{y}">{_esc(label)}</text>\n')
        for x, val, ok in ((cols[0], said, said_ok), (cols[1], count, count_ok)):
            cls = "t-good" if ok else "t-bad"
            parts.append(f'<text class="{cls}" x="{x}" y="{y}">{_esc(val)}</text>\n')
    parts.append(
        f'<text class="t-strong" x="18" y="{list_top - 10}">'
        "頼んでいないのに出てきた金額（そのまま引用）</text>\n"
    )
    for index, line in enumerate(appeared):
        parts.append(
            f'<text class="t-sm" x="18" y="{list_top + index * 20 + 8}">{_esc("・" + line)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ 金額を禁じた側は、断ったうえで理由まで書いた"
        "＝「推測の数字は、当てにできる数字と見た目が同じ」。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ どの数字にも出どころが書かれていない。募集ページを開いて確かめた数字ではない。</text>\n"
    )
    alt = (
        "架空の会社員の箇条書き21行を渡して、頼み方だけを変えたときに、"
        "返りに金額がいくつ出るかを比べた表。"
        "私は何で稼げますかと一言で聞いた場合、金額を書くなとは言っておらず、返りに金額が3件出た。"
        "売れそうなものを挙げてと頼んだ場合も、言っておらず、金額が4件出た。"
        "募集されている仕事の名前に対応づけてくださいと頼み、"
        "実際に募集ページを見て確かめた数字でない限り金額を書かないでくださいと足した場合は、0件だった。"
        "相場を自分で確かめる手順を書いてくださいと頼み、同じ禁止を足した場合も0件だった。"
        "頼んでいないのに出てきた金額は次のとおり。"
        "単価が時間2,000から3,000円のあたりから始まるとして、最初の数ヶ月は月2から5万円。"
        "雛形づくりが1件1から3万円、リストの整理が1,000件で1から3万円あたりから。"
        "引き継ぎ書の代行は1本5から15万円くらいのレンジ。"
        "金額を禁じた側は、断ったうえで理由まで書いた。"
        "推測の数字は、当てにできる数字と見た目が同じだから混ぜないのが安全だ、という理由である。"
        "どの数字にも出どころが書かれておらず、募集ページを開いて確かめた数字ではない。"
    )
    (OUT / "sell-price-not-asked.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def sell_what_carries_over_chart() -> None:
    """会社の中で積んだ経験のうち、社外に持ち出せるものはどれだけか。

    実測（2026-08-13）。証拠＝`docs/evidence/sell-what-you-already-do.md`。
    """
    rows = [
        ("○ 作り直せる", 4, "box-good", "t-good", "会社のものを使わずに、自分で作れる"),
        ("△ 一部だけ", 6, "box-quiet", "t-sm", "やり方は再現できるが、現物は会社のもの"),
        ("× 作り直せない", 3, "box-bad", "t-bad", "中身が会社そのもの。手元では再現できない"),
        ("判定以前", 1, "box-quiet", "t-sm", "資格の領域（確定申告の相談）"),
    ]
    label_x = 18
    bar_x, bar_unit = 150, 26
    desc_x = 340
    row_h = 34
    top = 104
    height = top + len(rows) * row_h + 76
    assert desc_x + 22 * 11.5 <= WIDTH - 18

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "12年ぶんの経験のうち、社外に持ち出せるのはどれか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "「勤務先のデータ・書式・システムを一切使わずに作り直せるか」で、"
        "候補14件を判定させた結果。</text>\n",
        f'<text class="t-sm" x="{bar_x}" y="{top - 16}">件数</text>\n',
        f'<text class="t-sm" x="{desc_x}" y="{top - 16}">判定の意味</text>\n',
    ]
    for index, (label, count, box_cls, text_cls, desc) in enumerate(rows):
        y = top + index * row_h
        parts.append(f'<text class="{text_cls}" x="{label_x}" y="{y + 17}">{_esc(label)}</text>\n')
        parts.append(
            f'<rect class="{box_cls}" x="{bar_x}" y="{y + 4}" '
            f'width="{count * bar_unit}" height="18" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{bar_x + count * bar_unit + 8}" y="{y + 17}">{count}件</text>\n'
        )
        parts.append(f'<text class="t-sm" x="{desc_x}" y="{y + 17}">{_esc(desc)}</text>\n')
    parts.append(
        f'<text class="t-bad" x="18" y="{height - 56}">'
        "そのまま売れるものは0件。△は、作り直すと実績のほうが消える。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 36}">'
        "※ 持ち出しの問題がない候補は1つだけだった＝会社の外で7年続けた、"
        "無償のチーム会計（本人が一番あっさり書いた行）。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "※ 冒頭でAI自身が書いた数は「○が5つ」。本文を数えると4件だった"
        "（判定は合っていて、まとめの数だけが合わない）。</text>\n"
    )
    alt = (
        "架空の会社員の箇条書き21行から作った売り物の候補14件を、"
        "勤務先のデータ・書式・システムを一切使わずに自分でゼロから作り直せるか、"
        "という基準で判定させた結果の図。"
        "作り直せるものが4件で、会社のものを使わずに自分で作れるという意味。"
        "一部だけ作り直せるものが6件で、やり方は再現できるが現物は会社のものだという意味。"
        "作り直せないものが3件で、中身が会社そのものなので手元では再現できないという意味。"
        "判定以前のものが1件で、資格の領域である確定申告の相談だった。"
        "そのまま売れるものは0件で、一部だけ作り直せるものは、"
        "作り直すと実績のほうが消えるという構造になっている。"
        "持ち出しの問題がない候補は1つだけで、"
        "会社の外で7年続けた無償のチーム会計だった。本人が一番あっさり書いた行である。"
        "なお冒頭でAI自身が書いた数は作り直せるものが5つだったが、"
        "本文を数えると4件だった。判定そのものは合っていて、まとめの数だけが合わない。"
    )
    (OUT / "sell-what-carries-over.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def video_length_drift_chart() -> None:
    """動画の台本の尺が、頼み方でどれだけ動くか。

    実測（2026-08-13・架空の走り書き14行、5分の動画）。
    台詞の字数は Python で数えた（抜き出し規則は証拠ファイルに書いてある）。
    証拠＝`docs/evidence/video-script-by-the-clock.md`。
    """
    rows = [
        ("「5分くらいの台本を書いて」", 2320, "7分44秒", "＋2分44秒", False),
        ("「1分300字・5分なので1,500字」", 1449, "4分50秒", "−10秒", True),
        ("同じ指示文をもう1回", 1489, "4分58秒", "−2秒", True),
        ("＋1文40字・書き言葉禁止・足さない", 969, "3分14秒", "−1分46秒", False),
    ]
    label_x = 18
    bar_x, bar_w = 300, 230
    biggest = max(n for _, n, _, _, _ in rows)
    row_h = 34
    top = 100
    height = top + len(rows) * row_h + 76
    time_x = bar_x + bar_w + 14
    diff_x = time_x + 74
    assert diff_x + 78 <= WIDTH - 18, diff_x

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「5分の動画」と言っても、5分にはならない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の走り書き14行から、5分の動画の台本を作らせた。"
        "棒は台詞の字数（Pythonで実測）。</text>\n",
        f'<text class="t-sm" x="{bar_x}" y="{top - 16}">台詞の字数</text>\n',
        f'<text class="t-sm" x="{time_x}" y="{top - 16}">1分300字なら</text>\n',
        f'<text class="t-sm" x="{diff_x}" y="{top - 16}">5分との差</text>\n',
    ]
    for index, (label, count, mmss, diff, ok) in enumerate(rows):
        y = top + index * row_h
        parts.append(f'<text class="t" x="{label_x}" y="{y + 17}">{_esc(label)}</text>\n')
        w = round(bar_w * count / biggest)
        cls = "box-good" if ok else "box-bad"
        parts.append(
            f'<rect class="{cls}" x="{bar_x}" y="{y + 4}" width="{w}" height="18" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{bar_x + 6}" y="{y + 17}">{count:,}字</text>\n'
        )
        vcls = "t-good" if ok else "t-bad"
        parts.append(f'<text class="{vcls}" x="{time_x}" y="{y + 17}">{_esc(mmss)}</text>\n')
        parts.append(f'<text class="{vcls}" x="{diff_x}" y="{y + 17}">{_esc(diff)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 52}">'
        "※ 素朴に頼んだ版は、自分が何字書いたかを最後まで書かなかった。"
        "画面上は「5分の台本」として渡される。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 32}">'
        "※ 時間ではなく字数で渡した2回は、どちらも申告した字数が実測と一致した"
        "（1,449字と1,489字）。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 縛り（1文40字・書き言葉の禁止・足さない）を重ねると、"
        "今度は尺が足りなくなる。足すのは自分の仕事になる。</text>\n"
    )
    alt = (
        "架空の走り書き14行から5分の動画の台本を作らせて、"
        "頼み方ごとに台詞の字数を実測した図。"
        "5分くらいの台本を書いてと頼んだ場合、台詞は2,320字で、"
        "1分300字で計算すると7分44秒、5分より2分44秒長い。"
        "1分300字で計算して5分なので1,500字を目安にと頼むと1,449字で4分50秒、5分より10秒短いだけ。"
        "同じ指示文をもう1回走らせると1,489字で4分58秒、5分より2秒短いだけだった。"
        "さらに1文40字以内、書き言葉の禁止、走り書きにないことを足さない、"
        "という3つの縛りを足すと969字で3分14秒になり、今度は1分46秒足りなくなった。"
        "素朴に頼んだ版は、自分が何字書いたかを最後まで書かなかったので、"
        "画面上は5分の台本として渡される。"
        "時間ではなく字数で渡した2回は、どちらも申告した字数が実測と一致した。"
        "縛りを重ねると尺が足りなくなり、足すのは自分の仕事になる。"
    )
    (OUT / "video-length-drift.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def video_numbers_you_will_say_chart() -> None:
    """台本に入った、走り書きに無い数字。

    実測（2026-08-13）。証拠＝`docs/evidence/video-script-by-the-clock.md`。
    """
    rows = [
        ("117,600円", "定期は月9,800円だった", "9,800 × 12か月"),
        ("36,000円", "月3,000円の駐輪場を借りた", "3,000 × 12か月"),
        ("54,400円", "点検とタイヤ交換で18,400円", "18,400 ＋ 36,000"),
        ("6万円ちょっと", "（上の2つの差）", "117,600 − 54,400"),
        ("2,800kmちょっと", "片道7.2km／198日", "7.2 × 2 × 198"),
        ("46分", "信号込みで23分", "23 × 2"),
    ]
    label_x, cols = 18, (150, 400)
    row_h = 27
    top = 112
    height = top + len(rows) * row_h + 74
    assert cols[1] + 16 * 11.5 <= WIDTH - 18

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "台本に入っていた、走り書きに無い数字</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "素朴に頼んだ台本の台詞から、走り書きに出てこない数字を全部拾った（6件）。"
        "計算は6件とも合っていた。</text>\n",
        f'<text class="t-bad" x="{label_x}" y="{top - 16}">台本で言うことになる数字</text>\n',
        f'<text class="t-sm" x="{cols[0]}" y="{top - 16}">走り書きにある行</text>\n',
        f'<text class="t-sm" x="{cols[1]}" y="{top - 16}">どう作られたか</text>\n',
    ]
    for index, (num, src, how) in enumerate(rows):
        y = top + index * row_h + 16
        parts.append(f'<text class="t-bad" x="{label_x}" y="{y}">{_esc(num)}</text>\n')
        parts.append(f'<text class="t-sm" x="{cols[0]}" y="{y}">{_esc(src)}</text>\n')
        parts.append(f'<text class="mono" x="{cols[1]}" y="{y}">{_esc(how)}</text>\n')
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 50}">'
        "※ 計算はどれも合っている。問題は、これをカメラの前で言うのが自分だということ。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ 素朴な台本には「雨の日の電車代が入っていません」という断りが自分から書かれていた"
        "＝抜けを隠してはいない。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ 別の頼み方では「定期の1年ぶんは9,800円×12か月で計算しました」と、"
        "使った前提を書き添えて返った。</text>\n"
    )
    alt = (
        "素朴に頼んだ動画台本の台詞から、走り書きに出てこない数字を全部拾った表。6件あった。"
        "117,600円は、走り書きの定期は月9,800円だったという行から、9,800かける12か月で作られた。"
        "36,000円は、月3,000円の駐輪場を借りたという行から、3,000かける12か月で作られた。"
        "54,400円は、点検とタイヤ交換で18,400円という行から、18,400たす36,000で作られた。"
        "6万円ちょっとは、上の2つの差で、117,600ひく54,400である。"
        "2,800kmちょっとは、片道7.2kmと198日から、7.2かける2かける198で作られた。"
        "46分は、信号込みで23分という行から、23かける2で作られた。"
        "計算はどれも合っている。問題は、これをカメラの前で言うのが自分だということ。"
        "素朴な台本には、雨の日の電車代が入っていませんという断りが自分から書かれていて、"
        "抜けを隠してはいなかった。"
        "別の頼み方では、定期の1年ぶんは9,800円かける12か月で計算しましたと、"
        "使った前提を書き添えて返った。"
    )
    (OUT / "video-numbers-you-will-say.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def _usd(value: float) -> str:
    """$0.375 のような3桁の端数も、$1.50 のような2桁も、そのまま書ける形にする。"""
    text = f"{value:.3f}".rstrip("0")
    if len(text.split(".")[1]) < 2:
        text = f"{value:.2f}"
    return f"${text}"


def gemini37_price_window() -> None:
    """導入価格（2026年12月31日まで）と、2027年1月1日からの価格。"""
    rows = [
        ("入力（Standard）", 0.75, 1.50),
        ("出力（Standard）", 3.75, 7.50),
        ("入力（Batch）", 0.375, 0.75),
        ("出力（Batch）", 1.875, 3.75),
    ]
    left, right = 250, 620
    span = right - left
    top, bar_h, bar_gap, group_gap = 82, 14, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    biggest = max(max(a, b) for _, a, b in rows)
    scale = span / biggest

    parts = [
        '<text class="t-strong" x="18" y="26">Gemini 3.7 Flash の単価は、2027年1月1日に2倍になります</text>\n',
        '<text class="t-sm" x="18" y="45">青＝2026年12月31日までの導入価格、灰色＝2027年1月1日からの価格。</text>\n',
        '<text class="t-sm" x="18" y="64">100万トークンあたりのドル。Batch＝急がない仕事をまとめて流す使い方。</text>\n',
    ]
    for index, (name, intro, later) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((intro, "bar-new", "年内"), (later, "bar-old", "以降"))
        ):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(f'<text class="t-xs" x="204" y="{by + bar_h - 3}">{tag}</text>\n')
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"{_usd(value)}</text>\n"
            )

    height = top + len(rows) * group_h + 50
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ 前の世代の Gemini 3.6 Flash も、いまは同じ $0.75 ／ $3.75 です。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 半額なのは 3.7 だからではなく、いまが導入期間だからです。</text>\n"
    )
    alt = (
        "Gemini 3.7 Flash の単価が期間で変わることを示した横棒グラフ。"
        "100万トークンあたりのドル。Standard の入力は2026年12月31日まで0.75ドル、"
        "2027年1月1日から1.50ドル。Standard の出力は3.75ドルから7.50ドル。"
        "まとめ処理（Batch）の入力は0.375ドルから0.75ドル、出力は1.875ドルから3.75ドル。"
        "いずれも2027年1月1日に2倍になる。"
        "前の世代の Gemini 3.6 Flash も、いまは同じ0.75ドルと3.75ドルで、"
        "半額なのは3.7だからではなく導入期間だから。"
    )
    (OUT / "gemini37-price-window.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini37_vs_36_chart() -> None:
    """3.6 Flash と 3.7 Flash の点数（％で出ているものだけ）。"""
    rows = [
        ("FrontierCode 1.1", 34.4, 43.6),
        ("DeepSWE v1.1", 48.6, 65.3),
        ("Terminal-bench 2.1", 78.0, 85.8),
        ("AutomationBench", 17.0, 30.4),
        ("GDP.pdf", 22.0, 34.0),
        ("CharXiv（道具なし）", 85.2, 84.5),
    ]
    left, right = 250, 620
    span = right - left
    top, bar_h, bar_gap, group_gap = 82, 14, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    scale = span / 100.0

    parts = [
        '<text class="t-strong" x="18" y="26">モデルカードの点数（3.6 Flash → 3.7 Flash）</text>\n',
        '<text class="t-sm" x="18" y="45">灰色＝3.6 Flash、青＝3.7 Flash。目盛りは0〜100％で揃えてあります。</text>\n',
        '<text class="t-sm" x="18" y="64">一番下だけ下がっています。上がった項目だけを見ないでください。</text>\n',
    ]
    for index, (name, old, new) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((old, "bar-old", "3.6"), (new, "bar-new", "3.7"))
        ):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(f'<text class="t-xs" x="216" y="{by + bar_h - 3}">{tag}</text>\n')
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
        "※ テストの中身も測り方も、この6つで別々です。並べても平均は取れません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 何回試した値なのかは、モデルカードにも発表ページにも書かれていません。</text>\n"
    )
    alt = (
        "Gemini 3.6 Flash と 3.7 Flash の点数を比べた横棒グラフ。"
        "FrontierCode 1.1 は34.4％から43.6％、DeepSWE v1.1 は48.6％から65.3％、"
        "Terminal-bench 2.1 は78.0％から85.8％、AutomationBench は17.0％から30.4％、"
        "GDP.pdf は22.0％から34.0％へ上がった。"
        "いっぽう CharXiv（道具なし）だけは85.2％から84.5％へ下がっている。"
        "いずれも Google のモデルカードに載っている値で、テストの中身も測り方も別々のため平均は取れない。"
    )
    (OUT / "gemini37-vs-36.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini37_four_prices_chart() -> None:
    """Google が比較相手に選んだ4モデルの単価。"""
    rows = [
        ("Gemini 3.7 Flash", 0.75, 3.75),
        ("Claude Sonnet 5", 2.00, 10.00),
        ("GPT-5.6 Terra", 2.00, 12.00),
        ("Muse Spark 1.2", 1.25, 4.25),
    ]
    left, right = 210, 620
    span = right - left
    top, bar_h, bar_gap, group_gap = 66, 15, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    biggest = max(max(a, b) for _, a, b in rows)
    scale = span / biggest

    parts = [
        '<text class="t-strong" x="18" y="26">Google が比較相手に選んだ4モデルの単価</text>\n',
        '<text class="t-sm" x="18" y="45">入力＝薄い色 ／ 出力＝濃い色。100万トークンあたりのドル。</text>\n',
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
                f"{_usd(value)}</text>\n"
            )

    height = top + len(rows) * group_h + 68
    notes = [
        "※ Gemini の $0.75 ／ $3.75 は導入価格です。2027年1月1日から $1.50 ／ $7.50 になります。",
        "※ GPT-5.6 Terra は「短い入力」のときの値段です。境目のトークン数は公表されていません。",
        "※ Muse Spark 1.2 だけ、提供元の公式ページをこの記事では確認できていません。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 48 + note_index * 18}">{_esc(note)}</text>\n'
        )
    alt = (
        "Google が自社のモデルカードで比較相手に選んだ4モデルの単価を比べた横棒グラフ。"
        "100万トークンあたりのドル。Gemini 3.7 Flash は入力0.75ドル・出力3.75ドル、"
        "Claude Sonnet 5 は入力2.00ドル・出力10.00ドル、"
        "GPT-5.6 Terra は入力2.00ドル・出力12.00ドル、"
        "Muse Spark 1.2 は入力1.25ドル・出力4.25ドル。"
        "ただし Gemini の値は2026年12月31日までの導入価格で、2027年1月1日から1.50ドルと7.50ドルになる。"
        "GPT-5.6 Terra は短い入力のときの値段。"
        "Muse Spark 1.2 だけ提供元の公式ページを確認できていない。"
    )
    (OUT / "gemini37-four-prices.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini37_not_first_chart() -> None:
    """Google 自身の比較表の中で、3.7 Flash が一番ではなかった項目。"""
    total, won = 20, 9
    losses = [
        ("DeepSWE v1.1", "65.3%", "GPT-5.6 Terra 69.6%"),
        ("Terminal-bench 3.0", "14.9%", "GPT-5.6 Terra 20.8%"),
        ("GDPVal-AA v2（Elo）", "1525", "Muse Spark 1.2 1628"),
        ("Agent's Last Exam", "26.3%", "Claude Sonnet 5 33.3%"),
        ("CharXiv（道具あり）", "88.7%", "Gemini 3.6 Flash 89.4%"),
    ]
    bar_left, bar_right, bar_y, bar_h = 18, 702, 86, 26
    cell_gap = 3
    cell_w = (bar_right - bar_left + cell_gap) / total - cell_gap

    parts = [
        '<text class="t-strong" x="18" y="26">同じ表の中で、3.7 Flash が一番だったのは20項目中9項目</text>\n',
        '<text class="t-sm" x="18" y="45">Google のモデルカードに載っている比較表を、この記事で数えたものです。</text>\n',
        '<text class="t-sm" x="18" y="64">青＝3.7 Flash が最高値だった項目、灰色＝他社か前の世代のほうが上だった項目。</text>\n',
    ]
    for index in range(total):
        x = bar_left + index * (cell_w + cell_gap)
        cls = "bar-new" if index < won else "bar-old"
        parts.append(
            f'<rect class="{cls}" x="{x:.1f}" y="{bar_y}" '
            f'width="{cell_w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
    parts.append(f'<text class="t-accent" x="18" y="{bar_y + bar_h + 20}">9項目で最高</text>\n')
    parts.append(
        f'<text class="t-sm" x="150" y="{bar_y + bar_h + 20}">'
        "11項目は、他社か前の世代のほうが上でした</text>\n"
    )

    head_y = bar_y + bar_h + 58
    col1, col2, col3 = 18, 296, 424
    parts.append(f'<text class="t-xs" x="{col1}" y="{head_y}">項目</text>\n')
    parts.append(f'<text class="t-xs" x="{col2}" y="{head_y}">3.7 Flash</text>\n')
    parts.append(f'<text class="t-xs" x="{col3}" y="{head_y}">それより上だったモデル</text>\n')
    for row_index, (name, mine, better) in enumerate(losses):
        y = head_y + 24 + row_index * 22
        parts.append(f'<text class="t" x="{col1}" y="{y}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t" x="{col2}" y="{y}">{_esc(mine)}</text>\n')
        parts.append(f'<text class="t-bad" x="{col3}" y="{y}">{_esc(better)}</text>\n')

    height = head_y + 24 + len(losses) * 22 + 48
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ Muse Spark 1.2 は測っていない項目が多く、空欄は勝ち負けの数に入れていません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 表を作ったのは Google です。相手の会社が同じ条件で測った値ではありません。</text>\n"
    )
    alt = (
        "Google のモデルカードの比較表で、Gemini 3.7 Flash が最高値だった項目の数を示した図。"
        "20項目のうち9項目で最高、残り11項目は他社か前の世代のほうが上だった。"
        "上だった例として、DeepSWE v1.1 は3.7 Flash の65.3％に対し GPT-5.6 Terra が69.6％、"
        "Terminal-bench 3.0 は14.9％に対し GPT-5.6 Terra が20.8％、"
        "GDPVal-AA v2 は Elo 1525 に対し Muse Spark 1.2 が1628、"
        "Agent's Last Exam は26.3％に対し Claude Sonnet 5 が33.3％、"
        "CharXiv（道具あり）は88.7％に対し前の世代の Gemini 3.6 Flash が89.4％。"
        "表を作ったのは Google であり、相手の会社が同じ条件で測った値ではない。"
    )
    (OUT / "gemini37-not-first.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def transcript_auto_shape_vs_content_chart() -> None:
    """置くだけの形に固定した指示文を、2本×2回＝4回走らせて何が揃ったか。

    実測（2026-08-14・架空の文字起こし2本、29行と31行）。
    判定はすべて Python の文字列照合。証拠＝
    `docs/evidence/transcript-auto-same-every-time.md`。
    """
    cols = ("出す形\n（見出し・列）", "時刻タグが\n残った行", "語尾が\n原文のまま", "本文の誤変換を\n直したか")
    rows = (
        (
            "① 素朴に短くしただけ",
            ("4回とも違う", False),
            ("0・0・31・31", False),
            ("2/7・4/7\n7/7・7/7", False),
            ("4回とも直した", False),
        ),
        (
            "② 欄と順番を決めた",
            ("4回とも同じ", True),
            ("4回とも全行", True),
            ("6/7・7/7\n7/7・7/7", True),
            ("直した1回\n直さない3回", False),
        ),
        (
            "③ ②＋直さないと\n　 どこへ入れるか",
            ("4回とも同じ", True),
            ("4回とも全行", True),
            ("4回とも 7/7", True),
            ("4回とも直さない", True),
        ),
    )
    label_w = 158
    left = 18 + label_w
    col_w = (WIDTH - 36 - label_w) // len(cols)
    pad = 10
    top = 108
    row_h, row_gap = 62, 10
    height = top + len(rows) * (row_h + row_gap) - row_gap + 68
    assert left + col_w * len(cols) <= WIDTH - 18, left + col_w * len(cols)

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ指示文を4回走らせて、毎回そろったものと、そろわなかったもの</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の文字起こし2本（29行・31行）に、同じ指示文をそれぞれ2回ずつ通した"
        "＝1つの頼み方につき4回。</text>\n",
    ]
    # ⚠️ text-anchor="middle" は使わない。src/figures.py の検査は x を左端として
    # 見るので、中央寄せにすると必ず「はみ出し」と判定される。左寄せに揃える。
    for index, title in enumerate(cols):
        cx = left + index * col_w + pad
        for line_no, line in enumerate(title.split("\n")):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 30 + line_no * 14}">'
                f"{_esc(line)}</text>\n"
            )
    for r_index, row in enumerate(rows):
        y = top + r_index * (row_h + row_gap)
        name, cells = row[0], row[1:]
        for line_no, line in enumerate(name.split("\n")):
            parts.append(
                f'<text class="t-sm" x="18" y="{y + 26 + line_no * 16}">{_esc(line)}</text>\n'
            )
        for c_index, (text, good) in enumerate(cells):
            x = left + c_index * col_w
            box = "box-good" if good else "box-bad"
            parts.append(
                f'<rect class="{box}" x="{x + 3}" y="{y}" '
                f'width="{col_w - 6}" height="{row_h}" rx="4"/>\n'
            )
            lines = text.split("\n")
            start = y + row_h // 2 - (len(lines) - 1) * 8 + 5
            for line_no, line in enumerate(lines):
                cls = "t-good" if good else "t-bad"
                parts.append(
                    f'<text class="{cls}" x="{x + pad}" '
                    f'y="{start + line_no * 16}">{_esc(line)}</text>\n'
                )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 46}">'
        "※ ①は1本目だけ「[時刻] 話者:」の形が消え、29行から時刻が全部無くなった。"
        "2本目は31行とも残った。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        "※ ②は見出しも表の列も4回とも一致する。それでも本文を直すかどうかが割れる"
        "＝表からは分からない。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ ③＝「誤変換に見えるものも1文字も直さない。直したい箇所は要確認に入れる」"
        "を足した版。禁止だけでなく、行き先まで書いてある。</text>\n"
    )
    alt = (
        "架空の文字起こし2本に同じ指示文をそれぞれ2回ずつ通し、"
        "1つの頼み方につき4回の結果がそろったかどうかを4つの観点で並べた表。"
        "観点は、出す形（見出しと表の列）、時刻タグが残った行、"
        "語尾が原文のまま残った数、本文の誤変換を直したかどうか。"
        "①手でうまくいった指示文を素朴に短くしただけの版では、"
        "出す形が4回とも違い、時刻タグは1本目の2回が29行中0行、"
        "2本目の2回が31行中31行、語尾は7件中2件、4件、7件、7件、"
        "本文の誤変換は4回とも直された。"
        "②出す欄と順番を指示文の中に決めた版では、出す形が4回とも同じになり、"
        "時刻タグは4回とも全行残り、語尾は7件中6件、7件、7件、7件になったが、"
        "本文の誤変換を直した回が1回、直さなかった回が3回に割れた。"
        "③②に加えて、誤変換に見えるものも1文字も直さず、"
        "直したい箇所は要確認の表に入れる、と方針まで書いた版では、"
        "出す形も時刻タグも語尾も4回ともそろい、"
        "本文の誤変換は4回とも直されずに原文のまま残った。"
        "①では1本目の文字起こしだけ時刻と話者の行の形が丸ごと消えたが、"
        "2本目では残っており、同じ指示文でも入力によって形が変わる。"
        "②は見出しも表の列も4回とも一致するので、"
        "表だけを見ていると中身の方針が割れていることに気づけない。"
    )
    (OUT / "transcript-auto-shape-vs-content.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def transcript_auto_what_drifts_chart() -> None:
    """形も方針も固定したあとに、まだ残っていたブレ。

    実測（2026-08-14）。同じ指示文の2回転を機械で突き合わせた結果。
    証拠＝`docs/evidence/transcript-auto-same-every-time.md`。
    """
    groups = (
        (
            "整えたテキスト（本文）",
            (
                ("1本目・29行のうち違った行", 1, 29),
                ("2本目・31行のうち違った行", 0, 31),
            ),
        ),
        (
            "要確認の表",
            (
                ("1本目・片方にしか無かった行", 1, 9),
                ("2本目・種類の欄が食い違った行", 1, 7),
            ),
        ),
    )
    left, right = 296, 592
    span = right - left
    top = 112
    bar_h, bar_gap = 20, 16
    head_gap = 30
    height = top + sum(head_gap + len(r) * (bar_h + bar_gap) for _, r in groups) + 60
    assert right + 96 <= WIDTH - 18, right

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "形も方針も固定したあとに、それでも残ったブレ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ指示文を2回ずつ通して、1回目と2回目を機械で突き合わせた"
        "（灰色＝全体、色つき＝違った数）。</text>\n",
        f'<text class="t-xs" x="{left}" y="{top - 34}">'
        "見出しの名前・並び順・表の列は、どちらの本でも2回とも完全に一致した。</text>\n",
    ]
    y = top
    for title, rows in groups:
        parts.append(f'<text class="t-accent" x="18" y="{y + 12}">{_esc(title)}</text>\n')
        y += head_gap
        for name, diff, total in rows:
            width = max(3.0, span * diff / total)
            parts.append(f'<text class="t-sm" x="18" y="{y + bar_h - 5}">{_esc(name)}</text>\n')
            parts.append(
                f'<rect class="bar-old" x="{left}" y="{y}" '
                f'width="{span}" height="{bar_h}" rx="3" opacity="0.35"/>\n'
            )
            if diff:
                parts.append(
                    f'<rect class="bar-out" x="{left}" y="{y}" '
                    f'width="{width:.1f}" height="{bar_h}" rx="3"/>\n'
                )
            cls = "t-good" if diff == 0 else "t-bad"
            parts.append(
                f'<text class="{cls}" x="{right + 12}" y="{y + bar_h - 5}">'
                f"{diff} / {total}</text>\n"
            )
            y += bar_h + bar_gap
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 46}">'
        "※ 1本目で消えた1行＝「稼働から6か月と書いてあったはずです／音源で確かめる」。"
        "残り8行は2回とも同じだった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        "※ 2本目は行数も中身も一致したが、担当者名の行だけ種類が"
        "「音源で確かめる」と「話の中の食い違い」に割れた。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ 本文で違った1行は、つなぎ語の「あー、」が片方に残っただけ。"
        "発言そのものの書き換えは、2本とも0行。</text>\n"
    )
    alt = (
        "出す形と、直すか直さないかの方針まで指示文に書いたうえで、"
        "同じ指示文を2回ずつ通し、1回目と2回目の違いを機械で突き合わせた横棒グラフ。"
        "見出しの名前と並び順、表の列は、どちらの文字起こしでも2回とも完全に一致した。"
        "整えたテキストの本文では、1本目は29行のうち違ったのが1行、"
        "2本目は31行のうち違った行が0行だった。"
        "違った1行は、つなぎ語のあー、が片方の回にだけ残ったもので、"
        "発言そのものの書き換えは2本とも0行だった。"
        "一方、要確認の表にはブレが残り、"
        "1本目は9行のうち1行が片方の回にしか出ず、"
        "消えたのは、稼働から6か月と書いてあったはずです、を音源で確かめる、という行だった。"
        "2本目は7行で行数も中身も一致したが、担当者名の行だけ、"
        "種類の欄が音源で確かめると話の中の食い違いに割れた。"
        "そろうのは本文のほうが先で、最後まで残るのは要確認の表のブレである。"
    )
    (OUT / "transcript-auto-what-drifts.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def weekly_loop_swelling_chart() -> None:
    """毎週の週報を自動で回したとき、報告書の項目数がどう動いたか。

    実測（2026-08-14・架空の走り書きメモ3週ぶんを連鎖させ、各週2回ずつ）。
    判定は Python（見出しごとの箇条書きの数え上げ）。証拠＝
    `docs/evidence/weekly-report-loop-without-drift.md`。
    """
    rows = (
        ("第2週（メモ9行）", "前回の週報を型に", 16, 16, False),
        ("", "空の見出しだけ", 9, 10, True),
        ("第3週（メモ8行）", "前回の週報を型に", 18, 19, False),
        ("", "空の見出しだけ", 7, 8, True),
        ("第4週（メモ8行）", "前回の週報を型に", 23, 21, False),
        ("", "空の見出しだけ", 12, 11, True),
    )
    biggest = 23
    label_x, sub_x = 18, 150
    left, right = 292, 604
    span = right - left
    top = 104
    bar_h, bar_gap, group_gap = 13, 4, 14
    group_h = bar_h * 2 + bar_gap + group_gap
    height = top + len(rows) * group_h + 62
    assert right + 60 <= WIDTH - 18, right

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "前回の出来上がりを次回に渡すと、報告書だけが毎週太る</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の走り書きメモ3週ぶんを連鎖させ、各週2回ずつ走らせた。"
        "数えたのは見出し1〜4の箇条書きの数。</text>\n",
        f'<text class="t-xs" x="{left}" y="{top - 26}">'
        "上＝1回目 ／ 下＝2回目（同じ指示文をもう一度走らせたもの）</text>\n",
    ]
    for index, (week, how, first, second, good) in enumerate(rows):
        y = top + index * group_h
        if week:
            parts.append(f'<text class="t" x="{label_x}" y="{y + 12}">{_esc(week)}</text>\n')
        cls = "t-good" if good else "t-bad"
        parts.append(f'<text class="{cls}" x="{sub_x}" y="{y + 12}">{_esc(how)}</text>\n')
        for offset, value in enumerate((first, second)):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, span * value / biggest)
            parts.append(
                f'<rect class="{"bar-new" if good else "bar-in"}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{left + bw + 8:.1f}" y="{by + bar_h - 2}">'
                f"{value}件</text>\n"
            )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 44}">'
        "※ メモの行数は9→8→8と減っている。太っているのは報告書だけ。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 26}">'
        "※「4. 相談したいこと」だけを数えると、前回を型にした側は"
        "1件（人が書いた第1週）→3→3→5件。空の見出しの側は2→1→0件。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 8}">'
        "※ メモの事実そのものは、どちらの側も落ちていない"
        "（語で照合して9/9・8/8・8/8。落ちたのは1回だけ1語）。</text>\n"
    )
    alt = (
        "架空の走り書きメモ3週ぶんを連鎖させ、各週2回ずつ週報を作らせて、"
        "見出し1から4の箇条書きの数を比べた横棒グラフ。"
        "前回の出来上がりを今週の型として渡した側は、"
        "第2週がメモ9行に対し16件と16件、"
        "第3週がメモ8行に対し18件と19件、"
        "第4週がメモ8行に対し23件と21件で、毎週増えていく。"
        "前回の出来上がりを渡さず、空の見出しだけを渡した側は、"
        "第2週が9件と10件、第3週が7件と8件、第4週が12件と11件で、"
        "メモの行数とほぼ同じところに留まる。"
        "メモの行数は9行、8行、8行と減っているので、"
        "太っているのは報告書のほうだけである。"
        "相談したいことの欄だけを数えると、前回を型にした側は"
        "人が書いた第1週の1件から3件、3件、5件と増え、"
        "空の見出しの側は2件、1件、0件と増えない。"
        "メモに書かれた事実そのものは、どちらの側も落ちていない。"
    )
    (OUT / "weekly-loop-swelling.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def weekly_loop_invented_carry_chart() -> None:
    """メモにも第1週の週報にも無い語が、世代を越えて残ったか。

    実測（2026-08-14）。4語とも、材料側に1度も出てこないことを
    先に機械で確かめてある（`check.py` の assert）。証拠＝
    `docs/evidence/weekly-report-loop-without-drift.md`。
    """
    cols = ("第2週\n1回目", "第2週\n2回目", "第3週\n1回目", "第3週\n2回目",
            "第4週\n1回目", "第4週\n2回目")
    rows = (
        ("窓口", (True, False, True, True, True, False)),
        ("働きかけ", (True, False, True, True, False, False)),
        ("業務量の配分", (False, False, False, False, True, True)),
        ("未回答", (False, False, False, False, True, False)),
    )
    label_w = 130
    left = 18 + label_w
    col_w = (WIDTH - 36 - label_w) // len(cols)
    top = 116
    row_h, row_gap = 30, 8
    height = top + len(rows) * (row_h + row_gap) + 84
    assert left + col_w * len(cols) <= WIDTH - 18, left + col_w * len(cols)

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "メモにも第1週の週報にも無い言葉が、世代を越えて残る</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "前回の出来上がりを今週の型として渡した側。"
        "下の4語は、3週ぶんのメモにも第1週の週報にも1度も出てこない。</text>\n",
        f'<text class="t-xs" x="18" y="{top - 40}">'
        "■＝その回の週報に出た ／ 空白＝出なかった</text>\n",
    ]
    for index, title in enumerate(cols):
        cx = left + index * col_w + 8
        for line_no, line in enumerate(title.split("\n")):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 22 + line_no * 13}">'
                f"{_esc(line)}</text>\n"
            )
    for r_index, (word, marks) in enumerate(rows):
        y = top + r_index * (row_h + row_gap)
        parts.append(f'<text class="t" x="18" y="{y + 20}">{_esc(word)}</text>\n')
        for c_index, on in enumerate(marks):
            x = left + c_index * col_w
            box = "box-bad" if on else "box-quiet"
            parts.append(
                f'<rect class="{box}" x="{x + 3}" y="{y}" '
                f'width="{col_w - 10}" height="{row_h}" rx="3"/>\n'
            )
            if on:
                parts.append(
                    f'<text class="t-bad" x="{x + 11}" y="{y + 20}">出た</text>\n'
                )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 62}">'
        "※「窓口」「働きかけ」は第2週の1回目に生まれた。"
        "その回の週報を第3週に渡したので、第3週は2回とも出ている。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 44}">'
        "※ 第2週の2回目は0件だった＝生まれるかどうかは回による。"
        "生まれた回を次に渡すかどうかは、こちらが決めている。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 26}">'
        "※ 前回の出来上がりを渡さず空の見出しだけにした側は、"
        "12回すべてで4語とも0件だった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 8}">'
        "※「窓口が定まっていません」はメモに無い。"
        "元のメモは「情シスの担当が誰か確定してない」だけである。</text>\n"
    )
    alt = (
        "前回の出来上がりを今週の型として渡す形で週報を3週ぶん連鎖させ、"
        "メモにも第1週の週報にも1度も出てこない4つの言葉が、"
        "どの回の週報に出たかを並べた表。"
        "窓口という語は、第2週の1回目、第3週の1回目と2回目、第4週の1回目に出た。"
        "働きかけという語は、第2週の1回目、第3週の1回目と2回目に出た。"
        "業務量の配分という語は第4週の1回目と2回目、未回答という語は第4週の1回目に出た。"
        "窓口と働きかけは第2週の1回目に生まれ、その回の週報を第3週に渡したため、"
        "第3週は2回とも出ている。第2週の2回目は4語とも0件だったので、"
        "生まれるかどうかは回によるが、生まれた回を次の週に渡すかどうかは書き手が決めている。"
        "前回の出来上がりを渡さず空の見出しだけを渡した側は、12回すべてで4語とも0件だった。"
        "窓口が定まっていません、という文はメモに無く、"
        "元のメモは情シスの担当が誰か確定してない、だけである。"
    )
    (OUT / "weekly-loop-invented-carry.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def inbox_loop_carryover_share_chart() -> None:
    """毎朝の一覧のうち、昨日も同じ欄に出ていたものが何件か。

    実測（2026-08-15・架空の受信箱3日ぶん・居座り5通は3日とも同じ文字列）。
    判定は Python（件名の文字列の完全一致）。証拠＝
    `docs/evidence/inbox-loop-new-since-yesterday.md`。
    """
    # (日と欄, 昨日も同じ欄にいた数, 今日はじめて入った数)
    rows = (
        ("2日目 A欄（返信が要る）", 3, 1),
        ("2日目 B欄（自分の作業）", 2, 3),
        ("3日目 A欄（返信が要る）", 3, 2),
        ("3日目 B欄（自分の作業）", 2, 3),
    )
    biggest = max(a + b for _, a, b in rows)
    label_x, left = 18, 216
    span = 232
    top, bar_h, gap = 96, 22, 20
    height = top + len(rows) * (bar_h + gap) + 74
    # 棒のうしろに「同じ◯件／新しい◯件」（10字・12.5px）が入る幅を確保する。
    assert left + span + 10 + 10 * 13 <= WIDTH - 18, left + span

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "毎朝の一覧の半分以上は、昨日も同じ欄にいたもの</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の受信箱3日ぶん。未処理のまま残った5通は、3日とも1文字も同じ文字列で入れてある。</text>\n",
        '<text class="t-sm" x="18" y="63">'
        "同じ指示文を各日2回ずつ走らせた。下の数字は2回とも同じだった。</text>\n",
        f'<text class="t-xs" x="{left}" y="{top - 14}">'
        "薄い色＝昨日も同じ欄にいた ／ 濃い色＝今日はじめて入った</text>\n",
    ]
    for index, (label, stayed, fresh) in enumerate(rows):
        y = top + index * (bar_h + gap)
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + bar_h - 6}">{_esc(label)}</text>\n'
        )
        wide_stay = span * stayed / biggest
        wide_fresh = span * fresh / biggest
        parts.append(
            f'<rect class="bar-old" x="{left}" y="{y}" '
            f'width="{wide_stay:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<rect class="bar-new" x="{left + wide_stay:.1f}" y="{y}" '
            f'width="{wide_fresh:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<text class="t-bad" x="{left + wide_stay + wide_fresh + 10:.1f}" '
            f'y="{y + bar_h - 6}">同じ{stayed}件／新しい{fresh}件</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 52}">'
        "※ 仕分けそのものは崩れていない。居座り5通は3日×2回＝6回とも同じ欄に入り、"
        "件名も6回とも一字一句そのままだった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 34}">'
        "※ 問題は精度ではなく、返ってきた一覧のどこにも"
        "「これは昨日もあった」と書かれていないこと。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "※ 1日目は比べる相手が無いので数えていない。</text>\n"
    )
    alt = (
        "架空の受信箱3日ぶんを毎朝仕分けさせて、"
        "返ってきた一覧のうち昨日も同じ欄にいた件数と、"
        "今日はじめて入った件数を並べた積み上げ横棒グラフ。"
        "2日目のA欄は4件のうち3件が昨日と同じで、新しいのは1件。"
        "2日目のB欄は5件のうち2件が昨日と同じで、新しいのは3件。"
        "3日目のA欄は5件のうち3件が昨日と同じで、新しいのは2件。"
        "3日目のB欄は5件のうち2件が昨日と同じで、新しいのは3件。"
        "同じ指示文を各日2回ずつ走らせたが、この数字は2回とも同じだった。"
        "仕分けそのものは崩れておらず、未処理のまま残した5通は"
        "3日かける2回の6回とも同じ欄に入り、件名も6回とも一字一句そのままだった。"
        "問題は仕分けの精度ではなく、返ってきた一覧のどこにも"
        "これは昨日もあったと書かれていないことである。"
    )
    (OUT / "inbox-loop-carryover-share.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def inbox_loop_ai_guesses_chart() -> None:
    """「前から残っているもの」をAIに振り分けさせたときの当たり外れ。

    実測（2026-08-15・2日目と3日目を各2回）。真値は受信箱の作り方から出した。
    判定は Python。証拠＝`docs/evidence/inbox-loop-new-since-yesterday.md`。
    """
    # (回, 当たり, はずれ, 「分からない」に置いた数)
    rows = (
        ("2日目 1回目", 3, 1, 5),
        ("2日目 2回目", 3, 1, 5),
        ("3日目 1回目", 6, 4, 0),
        ("3日目 2回目", 4, 2, 4),
    )
    biggest = max(a + b + c for _, a, b, c in rows)
    label_x, left = 18, 150
    span = 330
    top, bar_h, gap = 96, 22, 20
    height = top + len(rows) * (bar_h + gap) + 92
    # 棒のうしろに「当たり◯／はずれ◯／分からない◯」（15字・12.5px）が入る幅を確保する。
    assert left + span + 10 + 15 * 13 <= WIDTH - 18, left + span

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「前から残っているもの」をAIに聞くと、3件に1件は逆になる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "AIが見ているのは今日の受信箱だけなので、昨日あったかどうかは原理的に分からない。</text>\n",
        '<text class="t-sm" x="18" y="63">'
        "「推測で振り分けないでください」と書いたうえで、2日目と3日目を各2回。</text>\n",
        f'<text class="t-xs" x="{left}" y="{top - 14}">'
        "濃い色＝当たり ／ 赤＝はずれ ／ 薄い色＝「どちらか分からない」に置いた</text>\n",
    ]
    for index, (label, hit, miss, unknown) in enumerate(rows):
        y = top + index * (bar_h + gap)
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + bar_h - 6}">{_esc(label)}</text>\n'
        )
        x = float(left)
        for value, cls in ((hit, "bar-new"), (miss, "box-bad"), (unknown, "bar-old")):
            wide = span * value / biggest
            if wide > 0:
                parts.append(
                    f'<rect class="{cls}" x="{x:.1f}" y="{y}" '
                    f'width="{wide:.1f}" height="{bar_h}" rx="2"/>\n'
                )
            x += wide
        cls = "t-bad" if miss else "t-good"
        parts.append(
            f'<text class="{cls}" x="{x + 10:.1f}" y="{y + bar_h - 6}">'
            f"当たり{hit}／はずれ{miss}／分からない{unknown}</text>\n"
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 70}">'
        "※ 4回で振り分けた24件のうち、はずれは8件。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 52}">'
        "※ 3日目は1回目が10件すべてを振り分け、2回目は4件を「分からない」に置いた。同じ指示文で。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 34}">'
        "※ はずれ方に癖がある＝件名に「Re:」が付いているもの、"
        "差出人が前日にも出ていたものを「前から残っている」に入れる。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "※ 真値は受信箱の作り方から出した（3日とも同じ文字列で入れた5通＝前から残っているもの）。</text>\n"
    )
    alt = (
        "毎朝の仕分けのあとに、今日はじめて来たものと前から残っているものへ"
        "AIに振り分けさせた結果の積み上げ横棒グラフ。"
        "2日目は1回目も2回目も、当たり3件、はずれ1件、"
        "どちらか分からないに置いたものが5件。"
        "3日目の1回目は10件すべてを振り分けて当たり6件、はずれ4件、分からない0件。"
        "3日目の2回目は当たり4件、はずれ2件、分からない4件で、"
        "同じ指示文なのに1回目とまったく違う。"
        "4回で振り分けた24件のうち、はずれは8件だった。"
        "AIが見ているのは今日の受信箱だけなので、"
        "昨日あったかどうかは原理的に分からない。"
        "はずれ方には癖があり、件名にRe:が付いているものや、"
        "差出人が前日にも出ていたものを前から残っているに入れる。"
    )
    (OUT / "inbox-loop-ai-guesses.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def constraints_hold_totals_drift_chart() -> None:
    """5往復たっても縛りは守られ、頼んでいない合計だけが外れたところ。

    実測（2026-08-16・材料2本×2回＋対照2本＝6本の会話・5往復）。
    機械で照合したのは1往復目と5往復目の返り（6本×2＝12回）。
    数字は「その回で縛りが守られていた会話の数／6」。
    """
    rules = [
        ("① 全部の行を1行ずつ", 6, 6),
        ("② 数字はメモのまま", 6, 5),
        ("③ メモに無い品質を書かない", 6, 6),
        ("④ 言い回しを整えない", 6, 6),
        ("⑤ 〔要確認〕を残す", 6, 6),
    ]
    left = 18
    label_w = 230
    cell_w, cell_h, gap = 84, 30, 12
    grid_x = left + label_w
    note_x = grid_x + 2 * (cell_w + gap)
    note_w = 250
    assert note_x + note_w <= WIDTH - left, note_x
    top = 128
    pitch = cell_h + gap

    parts = [
        f'<text class="t-strong" x="{left}" y="26">'
        "5往復たっても縛りは戻らない。狂ったのは、頼んでいない合計のほう</text>\n",
        f'<text class="t-sm" x="{left}" y="45">'
        "架空の副業の材料2本×各2回＋毎回縛りを貼り直した対照2本＝6本の会話。</text>\n",
        f'<text class="t-sm" x="{left}" y="64">'
        "2往復目からは、縛りに一切触れない普通の追加依頼だけを送っている。</text>\n",
        f'<text class="t-sm" x="{left}" y="83">'
        "数字は「その回で縛りが守られていた会話の数／6」。</text>\n",
        f'<text class="t-xs" x="{grid_x + 22}" y="{top - 10}">1往復目</text>\n',
        f'<text class="t-xs" x="{grid_x + cell_w + gap + 22}" y="{top - 10}">5往復目</text>\n',
    ]

    for row_index, (name, first, last) in enumerate(rules):
        y = top + row_index * pitch
        parts.append(f'<text class="t-sm" x="{left}" y="{y + 20}">{_esc(name)}</text>\n')
        for col_index, value in enumerate((first, last)):
            x = grid_x + col_index * (cell_w + gap)
            full = value == 6
            parts.append(
                f'<rect class="{"box-good" if full else "box-bad"}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{"t-good" if full else "t-bad"}" '
                f'x="{x + cell_w / 2 - 20:.1f}" y="{y + 20}">{value}／6</text>\n'
            )

    # 右側＝頼んでいない合計
    box_y = top
    box_h = 2 * pitch - gap
    parts.append(
        f'<rect class="box-bad" x="{note_x}" y="{box_y}" width="{note_w}" height="{box_h}" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t-bad" x="{note_x + 14}" y="{box_y + 22}">'
        "頼んでいない在庫の合計</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="{note_x + 14}" y="{box_y + 44}">'
        "記録した4回とも54点（真値56点）</text>\n"
    )
    box2_y = top + 2 * pitch
    parts.append(
        f'<rect class="box-good" x="{note_x}" y="{box2_y}" width="{note_w}" height="{box_h}" rx="6"/>\n'
    )
    parts.append(
        f'<text class="t-good" x="{note_x + 14}" y="{box2_y + 22}">'
        "もう1本の材料の報酬の合計</text>\n"
    )
    parts.append(
        f'<text class="t-good" x="{note_x + 14}" y="{box2_y + 44}">'
        "104,000円＝真値と一致（小計6件も）</text>\n"
    )

    height = top + len(rules) * pitch + 10 + 22 + 22 + 16
    parts.append(
        f'<text class="t-bad" x="{left}" y="{height - 60}">'
        "※ ②の1件は、在庫1が3に変わったもの。返り自身が気づいたが、"
        "「直前の一覧で誤っていた」という申告のほうが事実と違った。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="{left}" y="{height - 38}">'
        "※ 合計の誤りは1往復目から出ていて、5往復ずっと直らない。"
        "毎回縛りを貼り直した対照でも同じ54点だった。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="{left}" y="{height - 16}">'
        "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。</text>\n"
    )

    alt = (
        "最初に渡した5つの縛りが、5往復のやりとりのあとも守られていたかを並べた図。"
        "6本の会話のうち何本で守られていたかを、1往復目と5往復目で比べている。"
        "全部の行を1行ずつ書く、メモに無い品質を書かない、言い回しを整えない、"
        "〔要確認〕を残す、の4つは1往復目も5往復目も6本すべてで守られた。"
        "数字をメモのまま写す縛りだけが5往復目に6本中5本になり、1件だけ在庫の数が変わった。"
        "一方で、頼んでいない在庫の合計は記録した4回とも54点で、"
        "メモの行を足した真値56点と合っていない。"
        "もう1本の材料では、報酬の合計104,000円も発注元ごとの小計6件も真値と一致した。"
    )
    (OUT / "constraints-hold-totals-drift.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def missing_material_noticed_chart() -> None:
    """貼り忘れた材料の種類ごとに、気づかれたかどうか。

    実測（2026-08-16・保存版の指示文6本・全32回）。
    青の帯＝「貼られていないもの」を名前で挙げた回の割合。
    右の赤い数字＝そのまま相手に貼れる文面が返った回数
    （行頭の「件名：」があって、材料から埋める穴が0個の回）。
    """
    rows = [
        ("材料をひとつも貼らない", 12, 12, 0),
        ("事実の中身を1つ貼り忘れ", 4, 4, 0),
        ("「いつもの様式」を貼り忘れ", 0, 2, 2),
        ("受け皿を足して、様式を貼り忘れ", 2, 2, 0),
    ]
    left = 18
    label_w = 244
    bar_x = left + label_w
    bar_max = 268
    right_x = bar_x + bar_max + 16
    right_w = 96
    # 見出し「そのまま貼れる文面」は9字。t-xs（10.5px）なので、ありうる最大でも 9×12 = 108px
    assert right_x + max(right_w, 108) <= WIDTH - left, right_x
    top = 122
    row_h = 30
    gap = 22
    pitch = row_h + gap

    parts = [
        f'<text class="t-strong" x="{left}" y="26">'
        "貼り忘れに気づくかどうかは、貼り忘れたものの種類で割れる</text>\n",
        f'<text class="t-sm" x="{left}" y="45">'
        "架空の副業ライターの、保存して使い回している指示文6本。全32回の実測。</text>\n",
        f'<text class="t-sm" x="{left}" y="64">'
        "青＝「貼られていないもの」を名前で挙げた回。灰＝一言も触れなかった回。</text>\n",
        f'<text class="t-sm" x="{left}" y="83">'
        "右は、そのまま相手に貼れる文面が返った回数（埋める穴が1つも無いもの）。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "貼られていないものを名指しした回</text>\n",
        f'<text class="t-xs" x="{right_x}" y="{top - 12}">'
        "そのまま貼れる文面</text>\n",
    ]

    for index, (name, named, total, sendable) in enumerate(rows):
        y = top + index * pitch
        parts.append(
            f'<text class="t-sm" x="{left}" y="{y + 20}">{_esc(name)}</text>\n'
        )
        parts.append(
            f'<rect class="box-quiet" x="{bar_x}" y="{y}" '
            f'width="{bar_max}" height="{row_h}" rx="4"/>\n'
        )
        filled = bar_max * named / total
        if named:
            parts.append(
                f'<rect class="bar-new" x="{bar_x}" y="{y}" '
                f'width="{filled:.1f}" height="{row_h}" rx="4"/>\n'
            )
        # 数字は帯の中に置くと短い帯からはみ出すので、常に帯の右端の外に置く
        parts.append(
            f'<text class="t-strong" x="{bar_x + bar_max - 62}" y="{y + 20}">'
            f"{named}／{total}回</text>\n"
        )
        tone = "t-bad" if sendable else "t-good"
        mark = f"{sendable}回" if sendable else "0回"
        parts.append(
            f'<rect class="{"box-bad" if sendable else "box-good"}" '
            f'x="{right_x}" y="{y}" width="{right_w}" height="{row_h}" rx="4"/>\n'
        )
        parts.append(
            f'<text class="{tone}" x="{right_x + 34}" y="{y + 20}">{mark}</text>\n'
        )

    height = top + len(rows) * pitch + 8 + 22 + 22 + 16
    parts.append(
        f'<text class="t-bad" x="{left}" y="{height - 60}">'
        "※ 素通りした2回は、原稿を1文字も見ていないのに"
        "「範囲内に収めております」と4件ずつ書いていた。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="{left}" y="{height - 38}">'
        "※ 「受け皿」＝保存版の上に貼る前置き。参照している材料が実際に貼られているかを、先に確かめさせる。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="{left}" y="{height - 16}">'
        "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。</text>\n"
    )

    alt = (
        "貼り忘れた材料の種類ごとに、AIがその不足に気づいたかどうかを並べた図。"
        "材料をひとつも貼らなかった12回は、12回とも貼られていないものを名前で挙げ、"
        "そのまま貼れる文面が返った回は0回だった。"
        "実績メモや原稿のような事実の中身を1つだけ貼り忘れた4回も、4回とも名指しした。"
        "ところが「いつもの様式」を貼り忘れた2回は、2回とも様式に一言も触れず、"
        "2回ともそのまま相手に貼れる納品連絡メールが返った。"
        "保存版の上に受け皿の前置きを足すと、同じ様式の貼り忘れを2回とも名指しして止まり、"
        "そのまま貼れる文面は0回になった。"
    )
    (OUT / "missing-material-noticed.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def two_runs_read_volume_chart() -> None:
    """2回ぶんを見比べさせたとき、何件が返り、そのうち仕込みが何件かを頼み方ごとに並べる。

    実測（2026-08-17・材料2本×各2回＝4回ずつ）。仕込んだ「形の崩れ」は材料ごとに5件。
    棒の長さ＝1行1件で挙がった項目の総数。濃い部分が仕込みの5件。
    """
    rows = [
        ("そのまま「違うところを教えて」", [8, 8, 9, 10], [5, 5, 5, 5]),
        ("「違うところだけ・1行1件で」", [17, 18, 14, 14], [5, 5, 5, 5]),
        ("＋毎回変わってよい3つを先に宣言", [5, 6, 7, 5], [5, 5, 5, 5]),
        ("＋置いてよい/直す/判断できない", [11, 7, 9, 8], [5, 5, 5, 5]),
        ("宣言を残したまま短くした版", [5, 5, 6, 7], [5, 5, 5, 5]),
    ]
    label_x, label_w = 18, 246
    bar_x = label_x + label_w + 10
    bar_max_w = 330
    unit = bar_max_w / 18          # 最大値18件を基準に1件あたりの幅を出す
    bar_h, bar_gap = 10, 4
    row_gap = 16
    top = 104

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "返ってくる件数は頼み方で3倍変わる。仕込んだ5件は、どの頼み方でも全部出た</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の自動処理の出力を2組（表形式・箇条書き）用意し、"
        "毎回そろっていないと困る違いを5件ずつ仕込んだ。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "1つの頼み方につき、材料2本 × 各2回 = 4回。棒1本が1回ぶん。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "濃い部分＝仕込んだ5件　薄い部分＝毎回変わって当然の差</text>\n",
    ]

    y = top
    row_tops = []
    for label, totals, reds in rows:
        row_tops.append(y)
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + 22}">{_esc(label)}</text>\n'
        )
        for i, (total, red) in enumerate(zip(totals, reds)):
            by = y + i * (bar_h + bar_gap)
            parts.append(
                f'<rect class="bar-old" x="{bar_x}" y="{by}" '
                f'width="{total * unit:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<rect class="bar-new" x="{bar_x}" y="{by}" '
                f'width="{red * unit:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-xs" x="{bar_x + total * unit + 8:.1f}" '
                f'y="{by + bar_h - 1}">{total}件</text>\n'
            )
        y += 4 * (bar_h + bar_gap) + row_gap

    notes = [
        ("t-bad", "※「違うところだけ」と頼んだ4回は 14〜18件。"
                  "そのうち13〜9件は、日付や件数など毎回変わって当然の差だった。"),
        ("t-good", "※「毎回変わってよいのは日付・件数・中身の3つだけ」を先に書いた4回は"
                   " 5〜7件。仕込みの5件は4回とも全部残った。"),
        ("t-xs", "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 8
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y
    alt = (
        "自動処理の出力2回ぶんを見比べさせたとき、返ってきた項目の件数を"
        "頼み方5通りで並べた横棒グラフ。1つの頼み方につき4回ぶんの棒がある。"
        "そのまま違うところを教えてと頼んだ4回は8件・8件・9件・10件。"
        "違うところだけ1行1件でと頼んだ4回は17件・18件・14件・14件。"
        "毎回変わってよい3つを先に宣言した4回は5件・6件・7件・5件。"
        "置いてよい・直す・判断できないの3択を付けさせた4回は11件・7件・9件・8件。"
        "宣言を残したまま短くした版は5件・5件・6件・7件。"
        "どの頼み方でも、仕込んだ5件は4回とも全部挙がっている。"
        "違うのは、そこに混ざってくる「毎回変わって当然の差」の量で、"
        "いちばん多い回で13件、宣言をした回は0件から2件だった。"
    )
    (OUT / "two-runs-read-volume.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def two_runs_narrowing_chart() -> None:
    """見る場所を絞ると、絞った外がAIの気まぐれに乗るところ。

    実測（2026-08-17）。仕込み5件のうち、見分けられる値が返りに出た数を
    「こちらが指定した欄の中」と「AIが自分から付けた補足だけ」に分けて数えた。
    """
    rows = [
        ("見出しの名前と順番だけ", "表形式の材料", 1, 2, 1),
        ("見出しの名前と順番だけ", "表形式の材料", 2, 2, 3),
        ("見出しの名前と順番だけ", "箇条書きの材料", 1, 2, 0),
        ("見出しの名前と順番だけ", "箇条書きの材料", 2, 2, 0),
        ("4つの欄を数えて並べさせる", "表形式の材料", 1, 4, 0),
        ("4つの欄を数えて並べさせる", "表形式の材料", 2, 4, 0),
        ("4つの欄を数えて並べさせる", "箇条書きの材料", 1, 2, 1),
        ("4つの欄を数えて並べさせる", "箇条書きの材料", 2, 1, 3),
    ]
    label_x, label_w = 18, 216
    mat_x = label_x + label_w
    bar_x = mat_x + 118
    cell = 46                       # 仕込み1件ぶんの幅
    bar_h, gap = 22, 7
    top = 100

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "見る場所を絞ると、絞った外は「その回に補足が付いたかどうか」で決まる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "仕込みは材料ごとに5件。棒は、見分けられる値が返りに出た数。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "濃い部分＝こちらが指定した欄の中に出た　薄い部分＝AIが自分から付けた補足にだけ出た</text>\n",
    ]
    for i in range(6):
        parts.append(
            f'<text class="t-xs" x="{bar_x + i * cell - 3}" y="{top - 8}">{i}</text>\n'
        )

    y = top
    prev_label = None
    for label, mat, run, field, note in rows:
        if label != prev_label:
            parts.append(
                f'<text class="t" x="{label_x}" y="{y + 15}">{_esc(label)}</text>\n'
            )
            prev_label = label
        parts.append(
            f'<text class="t-xs" x="{mat_x}" y="{y + 15}">{_esc(mat)}・{run}回目</text>\n'
        )
        parts.append(
            f'<rect class="box-quiet" x="{bar_x}" y="{y}" '
            f'width="{5 * cell}" height="{bar_h}" rx="2"/>\n'
        )
        if field:
            parts.append(
                f'<rect class="bar-new" x="{bar_x}" y="{y}" '
                f'width="{field * cell}" height="{bar_h}" rx="2"/>\n'
            )
        if note:
            parts.append(
                f'<rect class="bar-in" x="{bar_x + field * cell}" y="{y}" '
                f'width="{note * cell}" height="{bar_h}" rx="2"/>\n'
            )
        css = "t-bad" if field + note < 4 else "t-good"
        parts.append(
            f'<text class="{css}" x="{bar_x + 5 * cell + 10}" y="{y + bar_h - 6}">'
            f'{field + note}/5</text>\n'
        )
        y += bar_h + gap

    notes = [
        ("t-bad", "※ 同じ指示文の2回で 3/5 と 5/5 に割れた。"
                  "増えた2件は、AIが自分から付けた補足に出たもの。"),
        ("t-bad", "※ 4つの欄を数えさせた形では、欄に無い違い"
                  "（点検の項目が1つ消えた・行の書き方が変わった）は写らない。"),
        ("t-xs", "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 18
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y
    alt = (
        "見る場所を絞った2つの頼み方について、仕込んだ5件のうち何件を見分けられたかを"
        "8回ぶん並べた横棒グラフ。見出しの名前と順番だけを並べさせた形では、"
        "表形式の材料の1回目が5件中3件（指定した欄に2件、AIが自分から付けた補足に1件）、"
        "2回目が5件中5件（欄に2件、補足に3件）と割れた。"
        "同じ形を箇条書きの材料に当てると、2回とも5件中2件で、"
        "行の書き方・末尾の注記・合計行の3つは出てこない。"
        "4つの欄を数えて並べさせた形では、表形式の材料は2回とも5件中4件で"
        "全部が指定した欄の中に出たが、点検の項目が1つ消えたことは2回とも写らなかった。"
        "箇条書きの材料では5件中3件と4件に割れ、"
        "そのうち1件と3件はAIが自分から付けた補足にだけ出ている。"
    )
    (OUT / "two-runs-narrowing.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def month_boundary_where_rows_land_chart() -> None:
    """境界の行が、7月の実行と8月の実行のどちらに入ったかを材料別に並べる。

    実測（2026-08-18・指示文1「◯月ぶんの合計を出してください」を材料2本×各月2回＝8回）。
    印の位置は返りの合計から機械で決めた（合計が一意に線引きを決めるよう値を選んである）。
    """
    rows_a = [
        ("前月からまたいできた退勤（7/1 05:30）", 2),
        ("翌月へまたいでいく出勤（7/31 21:00）", 2),
        ("その勤務の続き（8/1 05:30）", 2),
        ("7/29 の残業を足す訂正（8/4 記録）", 2),
        ("7/30 の打刻を消す訂正（8/7 記録）", 2),
    ]
    rows_b = [
        ("締め日当日の納品（7/31・84,000円）", 0),
        ("2回に分けた納品の1回目（7/19）", 0),
        ("その2回目（8/3・48,000円）", 1),
        ("7/17 ぶんの請求漏れ（8/4・+38,000円）", 1),
        ("7/19 ぶんの返品（8/6・−63,000円）", 1),
    ]
    label_x, label_w = 18, 268
    col_x = [label_x + label_w + 30, label_x + label_w + 148, label_x + label_w + 288]
    col_names = [["7月の実行"], ["8月の実行"], ["どちらにも", "入らなかった"]]
    row_h = 26

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ頼み方でも、境界の行の行き先は材料でまるごと変わった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "毎月ぶんのログを別々に渡し、「◯月ぶんの合計を出してください」とだけ頼んだ"
        "（材料2本 × 各月2回 = 8回）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "行き先は、返ってきた合計から機械で判定した。同じ材料の2回は、どちらも同じ行き先だった。"
        "</text>\n",
    ]

    head_y = 92
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{head_y + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = 128
    for title, rows in (("材料A ＝ 勤怠の打刻ログ", rows_a),
                        ("材料B ＝ 売上の記録", rows_b)):
        parts.append(f'<text class="t-accent" x="{label_x}" y="{y}">{_esc(title)}</text>\n')
        y += 8
        for label, col in rows:
            ty = y + 18
            parts.append(
                f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n'
            )
            for i, cx in enumerate(col_x):
                if i == col:
                    cls = "box-bad" if col == 2 else "box-good"
                    mark = "×" if col == 2 else "○"
                    mcls = "t-bad" if col == 2 else "t-good"
                    parts.append(
                        f'<rect class="{cls}" x="{cx - 27}" y="{ty - 14}" '
                        f'width="54" height="19" rx="4"/>\n'
                    )
                    parts.append(
                        f'<text class="{mcls}" x="{cx}" y="{ty}" '
                        f'text-anchor="middle">{mark}</text>\n'
                    )
                else:
                    parts.append(
                        f'<line class="line" x1="{cx - 6}" y1="{ty - 5}" '
                        f'x2="{cx + 6}" y2="{ty - 5}"/>\n'
                    )
            y += row_h
        y += 14

    notes = [
        ("t-bad", "※ 勤怠では、境界の5件すべてが7月にも8月にも入らなかった。"
                  "それでも合計はどちらの月も1分もずれていない。"),
        ("t-good", "※ 売上では、境界の5件すべてがどちらかの月にちょうど1回入った。"
                   "二重計上も欠落も起きていない。"),
        ("t-xs", "架空データでの実測。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 4
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y
    alt = (
        "境界の行が7月の実行と8月の実行のどちらに入ったかを、材料2本ぶん並べた表。"
        "材料Aの勤怠の打刻ログでは、前月からまたいできた退勤・翌月へまたいでいく出勤・"
        "その勤務の続き・7月29日の残業を足す訂正・7月30日の打刻を消す訂正の5件すべてが、"
        "7月の実行にも8月の実行にも入らず、どちらにも入らなかったの列に印が付いている。"
        "材料Bの売上の記録では、締め日当日の納品と2回に分けた納品の1回目が7月の実行に、"
        "その2回目と請求漏れの追加請求と返品が8月の実行に入っていて、"
        "5件とも、どちらにも入らなかったの列は空である。"
        "同じ頼み方・同じ回数でも、材料が変われば境界の行の行き先がまるごと変わった。"
    )
    (OUT / "month-boundary-where-rows-land.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def month_boundary_two_runs_chart() -> None:
    """出す形を固定して2回ずつ走らせたときの、またぎ欄の件数と合計。

    実測（2026-08-18・指示文4を材料2本×各月2回＝8回）。
    棒の長さ＝またぎ欄に挙がった行数。右の数字＝その回が出した合計。
    """
    rows = [
        ("材料A ・ 7月ぶん", [(4, "10,890分"), (4, "10,890分")], True),
        ("材料A ・ 8月ぶん", [(5, "10,800分"), (5, "10,800分")], True),
        ("材料B ・ 7月ぶん", [(5, "922,000円"), (5, "922,000円")], True),
        ("材料B ・ 8月ぶん", [(4, "852,000円"), (8, "594,000円")], False),
    ]
    label_x, label_w = 18, 130
    bar_x = label_x + label_w + 10
    bar_max_w = 300
    unit = bar_max_w / 8          # 最大値8件を基準に1件あたりの幅を出す
    bar_h, bar_gap = 14, 6
    row_gap = 18
    top = 106

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "出す形が1文字も動かなくても、拾う行数のほうが割れる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "【期間】【またぎ】【合計】の3つを見出しごと決めて、同じ指示文を2回ずつ走らせた"
        "（材料2本 × 各月2回 = 8回）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "棒の長さ＝またぎ欄に挙がった行数。右の数字＝その回が出した合計。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "上の棒が1回目、下の棒が2回目</text>\n",
    ]

    y = top
    for label, runs, agreed in rows:
        parts.append(f'<text class="t" x="{label_x}" y="{y + 20}">{_esc(label)}</text>\n')
        for i, (n, total) in enumerate(runs):
            by = y + i * (bar_h + bar_gap)
            cls = "bar-old" if agreed else "bar-new"
            parts.append(
                f'<rect class="{cls}" x="{bar_x}" y="{by}" '
                f'width="{n * unit:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            tcls = "t-xs" if agreed else "t-bad"
            parts.append(
                f'<text class="{tcls}" x="{bar_x + n * unit + 8:.1f}" '
                f'y="{by + bar_h - 2}">{n}件 / {_esc(total)}</text>\n'
            )
        y += 2 * (bar_h + bar_gap) + row_gap

    notes = [
        ("t-good", "※ 8回のうち6回は、返ってきた文が2回とも1文字も違わなかった。"),
        ("t-bad", "※ 割れたのは材料B・8月ぶんの2回だけ。またぎが4件と8件で、"
                  "合計の差は258,000円。形の崩れは1か所も無い。"),
        ("t-xs", "架空データでの実測。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y
    alt = (
        "出す形を固定した指示文を2回ずつ走らせたときの、またぎ欄に挙がった行数を並べた横棒グラフ。"
        "材料Aの7月ぶんは1回目も2回目も4件で、合計はどちらも10,890分。"
        "材料Aの8月ぶんは1回目も2回目も5件で、合計はどちらも10,800分。"
        "材料Bの7月ぶんは1回目も2回目も5件で、合計はどちらも922,000円。"
        "材料Bの8月ぶんだけが割れて、1回目は4件で合計852,000円、2回目は8件で合計594,000円。"
        "その差は258,000円である。8回のうち6回は返ってきた文が2回とも1文字も違わず、"
        "割れた回にも見出しの崩れや欄の欠落は1か所も無い。"
    )
    (OUT / "month-boundary-two-runs.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
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
    gemini37_price_window()
    gemini37_vs_36_chart()
    gemini37_four_prices_chart()
    gemini37_not_first_chart()
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
    ask_invented_settings_chart()
    ask_missing_info_chart()
    summary_what_drops_chart()
    summary_length_vs_keep_chart()
    files_naive_outcome_chart()
    files_decidable_chart()
    critique_written_vs_missing_chart()
    critique_rewrite_loses_chart()
    runbook_find_holes_chart()
    runbook_silent_completion_chart()
    transcript_keep_vs_rewrite_chart()
    offer_verdict_vs_claims_chart()
    blog_research_coverage_chart()
    blog_research_volume_drift_chart()
    writing_check_three_asks_chart()
    writing_fix_loses_your_text_chart()
    proposal_sentence_check_chart()
    proposal_who_decides_chart()
    sell_price_not_asked_chart()
    sell_what_carries_over_chart()
    video_length_drift_chart()
    video_numbers_you_will_say_chart()
    transcript_auto_shape_vs_content_chart()
    transcript_auto_what_drifts_chart()
    weekly_loop_swelling_chart()
    weekly_loop_invented_carry_chart()
    listing_facts_vs_flourish_chart()
    reply_terms_survive_chart()
    hourly_rate_boundary_chart()
    inbox_loop_carryover_share_chart()
    inbox_loop_ai_guesses_chart()
    estimate_range_naive_vs_log_chart()
    list_work_not_delivery_chart()
    reply_undecided_marks_chart()
    material_checks_matrix_chart()
    material_check_split_chart()
    missing_material_noticed_chart()
    constraints_hold_totals_drift_chart()
    two_runs_read_volume_chart()
    two_runs_narrowing_chart()
    scope_lines_ai_drew_chart()
    scope_saved_form_flips_chart()
    records_length_vs_result_chart()
    records_counted_or_not_chart()
    job_capacity_subtraction_chart()
    job_ask_shape_vs_verdict_chart()
    month_boundary_where_rows_land_chart()
    month_boundary_two_runs_chart()
    print(f"{len(list(OUT.glob('*.svg')))}枚を {OUT} に出力しました")
