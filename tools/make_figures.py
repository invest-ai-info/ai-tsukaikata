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




def brief_asked_side_only_chart() -> None:
    """発注書に仕込んだ「両立しない6組」と「書かれていない6件」を、頼み方ごとに何件挙げたか。

    実測（2026-08-18・架空の発注書2本 × 頼み方7通り＝22回）。
    棒1本が1回ぶん。左の帯＝両立しない6組のうち挙がった数、右の帯＝書かれていない6件のうち挙がった数。
    """
    rows = [
        ("そのまま「発注書どおりに書いて」", [6, 6, 6, 6], [0, 0, 0, 0]),
        ("「足りない情報を挙げて。まだ書かないで」", [6, 6, 6, 6], [4, 6, 4, 3]),
        ("「同時には守れない組を対にして挙げて」", [6, 6, 6, 6], [0, 0, 0, 0]),
        ("組ごとに〔私が決める〕を残させる", [6, 6], [1, 0]),
        ("保存版＝組と、書かれていないことの2つ", [6, 6, 6, 6], [6, 6, 6, 6]),
    ]
    label_x, label_w = 18, 252
    gap = 14
    unit = 26.0                     # 1件あたりの幅
    left_x = label_x + label_w + gap
    left_w = 6 * unit
    right_x = left_x + left_w + 76
    right_w = 6 * unit
    bar_h, bar_gap = 10, 4
    row_gap = 18
    top = 126

    assert right_x + right_w + 40 <= WIDTH, right_x + right_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "仕込んだ矛盾は、どの頼み方でも全部出た。出ないのは「聞かなかったほう」だけ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の副業の発注書を2本作り、同時には守れない条件を6組と、単に書かれていない項目を"
        "6件ずつ仕込んだ。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "棒1本が1回ぶん（材料2本 × 各2回、または各1回）。目盛りは0件から6件。</text>\n",
        f'<text class="t-accent" x="{left_x}" y="{top - 30}">両立しない6組</text>\n',
        f'<text class="t-accent" x="{right_x}" y="{top - 30}">書かれていない6件</text>\n',
    ]
    # 目盛り（0と6のところに薄い縦線）
    total_h = sum(len(a) * (bar_h + bar_gap) + row_gap for _, a, _ in rows)
    for x0, w0 in ((left_x, left_w), (right_x, right_w)):
        for k in (0, 6):
            parts.append(
                f'<line class="line" x1="{x0 + k * unit:.1f}" y1="{top - 14}" '
                f'x2="{x0 + k * unit:.1f}" y2="{top + total_h - row_gap + 2}" '
                f'stroke-dasharray="2 3"/>\n'
            )
        parts.append(
            f'<text class="t-xs" x="{x0 + w0 - 8:.1f}" y="{top - 16}">6件</text>\n'
        )

    y = top
    for label, left_vals, right_vals in rows:
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + 20}">{_esc(label)}</text>\n'
        )
        for i, (lv, rv) in enumerate(zip(left_vals, right_vals)):
            by = y + i * (bar_h + bar_gap)
            parts.append(
                f'<rect class="bar-new" x="{left_x}" y="{by}" '
                f'width="{lv * unit:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-xs" x="{left_x + lv * unit + 8:.1f}" '
                f'y="{by + bar_h - 1}">{lv}</text>\n'
            )
            cls = "bar-old" if rv <= 1 else "bar-in"
            parts.append(
                f'<rect class="{cls}" x="{right_x}" y="{by}" '
                f'width="{max(rv * unit, 2.0):.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-xs" x="{right_x + rv * unit + 8:.1f}" '
                f'y="{by + bar_h - 1}">{rv}</text>\n'
            )
        y += len(left_vals) * (bar_h + bar_gap) + row_gap

    notes = [
        ("t-good", "※ 仕込んだ6組は22回とも6組ぜんぶ挙がった。黙って片方を捨てた回は0回。"),
        ("t-bad", "※「同時には守れない組を挙げて」と聞いた4回は、書かれていない項目を1件も挙げない。"),
        ("t-xs", "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y
    alt = (
        "架空の副業の発注書2本に、同時には守れない条件を6組と、単に書かれていない項目を6件ずつ"
        "仕込んで、頼み方を5通りで比べた横棒グラフ。棒1本が1回ぶんで、左が両立しない6組のうち"
        "挙がった数、右が書かれていない6件のうち挙がった数。"
        "そのまま発注書どおりに書いてと頼んだ4回は、6組が4回とも6件、書かれていない項目は"
        "4回とも0件。"
        "足りない情報を挙げてまだ書かないでと頼んだ4回は、6組が4回とも6件、"
        "書かれていない項目が4件・6件・4件・3件。"
        "同時には守れない組を対にして挙げてと頼んだ4回は、6組が4回とも6件、"
        "書かれていない項目は4回とも0件。"
        "組ごとに私が決める欄を残させた2回は、6組が2回とも6件、書かれていない項目が1件と0件。"
        "組と書かれていないことの2つを名指しした保存版の4回は、"
        "6組も書かれていない項目も4回とも6件でそろった。"
        "つまり仕込んだ矛盾はどの頼み方でも全部挙がり、"
        "挙がらないのは聞かなかったほうの項目だけだった。"
    )
    (OUT / "brief-asked-side-only.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def first_client_where_minutes_come_from_chart() -> None:
    """初めての発注元の見積もりで、合計の何分が記録から出ていて、何分がそうでないか。

    実測（2026-08-18・材料A＝初めての発注元。頼み方6通り）。
    棒の長さ＝返りが「合計」として提示した分数。幅で答えた回は上限を採った。
    """
    rows = [
        ("そのまま「何時間かかりますか」1回目", 360, 240, "500〜600分（うち推測 140〜240分）"),
        ("そのまま「何時間かかりますか」2回目", 430, 170, "500〜600分（うち推測 100〜170分）"),
        ("＋「記録なしと書いて」1回目", 405, 0, "405分"),
        ("＋「記録なしと書いて」2回目", 408, 0, "408分"),
        ("保存版（3つの欄に分ける）", 430, 0, "430分"),
        ("初回4件の分を、私が決めて渡す", 405, 165, "570分（うち私が決めた 165分）"),
    ]
    label_x, label_w = 18, 236
    bar_x = label_x + label_w + 12
    unit = 0.40                      # 1分あたりの幅
    bar_h, gap = 18, 12
    top = 116

    assert bar_x + 600 * unit + 190 <= WIDTH, bar_x + 600 * unit

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "合計は1.4倍に伸びる。伸びたぶんは、記録ではなく推測から来ている</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の作業記録3本（すべて4件目・5件目・3件目＝続けている発注元の仕事）に、"
        "「この発注元は初めてです」の1行だけを足した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "棒の長さ＝返りが合計として書いた分数。幅で答えた回は上限を採った。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "濃い部分＝作業記録から計算した分　薄い部分＝記録に無い分</text>\n",
    ]

    # 記録から出る目安（3,000字あたり 398〜430分）の帯
    y_end = top + len(rows) * (bar_h + gap)
    parts.append(
        f'<line class="line" x1="{bar_x + 415 * unit:.1f}" y1="{top - 6}" '
        f'x2="{bar_x + 415 * unit:.1f}" y2="{y_end - 4}" stroke-dasharray="3 3"/>\n'
    )
    parts.append(
        f'<text class="t-xs" x="{bar_x + 415 * unit + 6:.1f}" y="{top - 14}">'
        "↑ 記録3本から出る目安 415分</text>\n"
    )

    y = top
    for label, rec, extra, note in rows:
        parts.append(f'<text class="t" x="{label_x}" y="{y + 13}">{_esc(label)}</text>\n')
        parts.append(
            f'<rect class="bar-old" x="{bar_x}" y="{y}" '
            f'width="{rec * unit:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        if extra:
            parts.append(
                f'<rect class="bar-new" x="{bar_x + rec * unit:.1f}" y="{y}" '
                f'width="{extra * unit:.1f}" height="{bar_h}" rx="2"/>\n'
            )
        css = "t-bad" if extra else "t-good"
        parts.append(
            f'<text class="{css}" x="{bar_x + (rec + extra) * unit + 8:.1f}" '
            f'y="{y + 13}">{_esc(note)}</text>\n'
        )
        y += bar_h + gap

    notes = [
        ("t-bad", "※ そのまま聞いた2回は、初回だけの工程を自分から挙げたうえで、"),
        ("t-bad", "　 その分数を推測で作り、合計に混ぜた（返り自身が「当て推量です」と書いている）。"),
        ("t-good", "※「記録に対応する行が無い工程は、数字を出さずに記録なしと書いて」を足した2回は、"),
        ("t-good", "　 合計が記録どおりの405分・408分にとどまった。"),
        ("t-xs", "架空データでの実測。指示文ごとの生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 14
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 20

    height = y
    alt = (
        "初めての発注元の見積もりで、返りが合計として書いた分数を頼み方6通りで並べた横棒グラフ。"
        "濃い部分が作業記録から計算した分、薄い部分が記録に無い分。"
        "作業記録3本から出る目安は3,000字あたり415分で、そこに点線を引いてある。"
        "そのまま何時間かかりますかと聞いた1回目は、記録から360分、推測で140分から240分を足して"
        "合計500分から600分。2回目は記録から430分、推測で100分から170分を足して"
        "やはり合計500分から600分。"
        "記録に対応する行が無い工程は数字を出さずに記録なしと書いてくださいを足した2回は、"
        "合計405分と408分で、記録から出る目安のままだった。"
        "3つの欄に分ける保存版も430分で、記録に無い工程には時間を書いていない。"
        "初回だけ発生する4件の時間を利用者が自分で決めて渡した回は、"
        "記録から405分と、決めた165分を別の行にしたまま足して570分になった。"
        "つまり合計が1.4倍に伸びるかどうかは、記録ではなく、"
        "記録に無い分を誰がどう埋めるかで決まっている。"
    )
    (OUT / "first-client-where-minutes-come-from.svg").write_text(
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



def receipt_category_drift_by_ask_chart() -> None:
    """4つの頼み方で、3か月とも同じ費目に入らなかった定点の数を並べる。

    実測（2026-08-19）。定点＝「店名＋メモ」が3か月とも1文字も同じ行で、材料ごとに5件。
    1つの頼み方につき、材料2本 × 各2回 ＝ 4系列。棒1本が1系列ぶん（最大5件）。
    値はすべて check.py／summary.py が出したもの。
    """
    rows = [
        ("そのまま「費目ごとに分けて」", [3, 3, 3, 2], 11),
        ("＋費目の一覧9つを固定・受け皿つき", [3, 1, 1, 0], 5),
        ("＋「毎月かならず同じ費目に」", [0, 1, 0, 2], 3),
        ("＋こちらが持つ店名／メモ／費目の対応表", [0, 0, 0, 0], 0),
    ]
    label_x, label_w = 18, 268
    bar_x = label_x + label_w + 12
    unit = 56.0                    # 1件あたりの幅（最大5件＝280px）
    bar_h, bar_gap = 11, 4
    row_gap = 20
    top = 112

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ店・同じ用途の行が、月をまたいで違う費目に入った数</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の領収書メモを3か月ぶん・材料2本（表形式と走り書き）作り、"
        "3か月とも1文字も同じで出る行を5件ずつ仕込んだ。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "1つの頼み方につき、材料2本 × 各2回 = 4系列。棒1本が1系列ぶんで、"
        "長いほど月ごとにばらけている。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "棒の長さ＝5件の定点のうち、3か月そろわなかった件数（短いほうがよい）</text>\n",
    ]

    y = top
    for label, series, total in rows:
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + 24}">{_esc(label)}</text>\n'
        )
        for i, v in enumerate(series):
            by = y + i * (bar_h + bar_gap)
            parts.append(
                f'<rect class="bar-old" x="{bar_x}" y="{by}" '
                f'width="{5 * unit:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            if v:
                parts.append(
                    f'<rect class="bar-new" x="{bar_x}" y="{by}" '
                    f'width="{v * unit:.1f}" height="{bar_h}" rx="2"/>\n'
                )
            parts.append(
                f'<text class="t-xs" x="{bar_x + 5 * unit + 8:.1f}" '
                f'y="{by + bar_h - 1}">{v}/5</text>\n'
            )
        parts.append(
            f'<text class="t-accent" x="{bar_x + 5 * unit + 40}" '
            f'y="{y + 2 * (bar_h + bar_gap) + 4}">のべ {total}/20</text>\n'
        )
        y += 4 * (bar_h + bar_gap) + row_gap

    notes = [
        ("t-bad", "※ そのまま頼んだ12回では、費目の名前そのものが毎月作り直された"
                  "（3か月ぶんでのべ18〜20種、3か月とも出たのは2〜4種）。"),
        ("t-good", "※ 対応表を渡して「あなたが選び直さないでください」と書いた12回だけが、"
                   "4系列とも 0/5 だった。"),
        ("t-xs", "架空データでの実測（全56回）。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y
    alt = (
        "4通りの頼み方で、同じ店・同じ用途の行が月をまたいで違う費目に入った数を並べた"
        "横棒グラフ。1つの頼み方につき4系列ぶんの棒があり、棒1本の最大は5件。"
        "そのまま費目ごとに分けてと頼んだ4系列は3件・3件・3件・2件で、のべ20件中11件。"
        "費目の一覧9つを固定して受け皿を付けた4系列は3件・1件・1件・0件で、のべ5件。"
        "そこに毎月かならず同じ費目にという一文を足した4系列は0件・1件・0件・2件で、のべ3件。"
        "こちらが持つ店名とメモと費目の対応表を渡した4系列は4系列とも0件で、のべ0件。"
        "頼み方を変えるほど揺れは減るが、0になったのは対応表を渡した回だけだった。"
    )
    (OUT / "receipt-category-drift-by-ask.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def receipt_inside_or_outside_material_chart() -> None:
    """費目が材料の中で決まる行と、決まらない行を、定点10件ぶん並べる。

    実測（2026-08-19）。○の数＝2試行のうち、3か月とも同じ費目に入った試行の数。
    値は check.py が出したもの（材料2本 × 定点5件 ＝ 10行 × 頼み方4通り）。
    """
    rows_a = [
        ("東京電力エナジーパートナー／電気料金", True, [2, 2, 2, 2]),
        ("東京メトロ 新宿駅／ICカードチャージ", True, [2, 1, 1, 2]),
        ("セブン-イレブン 北口店／コピー代 20枚", False, [0, 1, 2, 2]),
        ("丸善ジュンク堂書店／文庫本2冊", False, [0, 2, 2, 2]),
        ("マツモトキヨシ 中央店／のど飴とマスク", False, [0, 0, 2, 2]),
    ]
    rows_b = [
        ("ガス／都市ガス 引き落とし", True, [2, 2, 2, 2]),
        ("スイカ／チャージ", True, [2, 2, 2, 2]),
        ("ダイソー／収納ケースとペン", False, [0, 2, 2, 2]),
        ("イオン／子どもの上履き", False, [1, 2, 1, 2]),
        ("スタバ／ノートPC広げて作業", False, [0, 1, 1, 2]),
    ]
    label_x, label_w = 18, 288
    col_x = [label_x + label_w + 42 + i * 84 for i in range(4)]
    col_names = [["そのまま"], ["一覧を", "固定"], ["＋毎月", "同じに"], ["＋対応表"]]
    row_h = 26

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "そろうかどうかは、費目が「メモの中で決まるか」で分かれた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "3か月とも1文字も同じ文字列で出てくる行を、材料2本に5件ずつ仕込んだ。"
        "◆の数＝2回のうち、3か月とも同じ費目に入った回の数。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "青い見出しの2行は、メモを読めば費目が決まる行。黒い3行は、"
        "決めるのが自分しかいない行。</text>\n",
    ]

    head_y = 96
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{head_y + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = 132
    for title, rows in (("材料A ＝ 家計簿アプリの書き出し（表形式）", rows_a),
                        ("材料B ＝ 手帳の走り書き", rows_b)):
        parts.append(f'<text class="t-accent" x="{label_x}" y="{y}">{_esc(title)}</text>\n')
        y += 8
        for label, obvious, vals in rows:
            ty = y + 18
            cls = "t-accent" if obvious else "t"
            parts.append(
                f'<text class="{cls}" x="{label_x}" y="{ty}">{_esc(label)}</text>\n'
            )
            for cx, v in zip(col_x, vals):
                box = "box-good" if v == 2 else "box-bad"
                mark = {2: "◆◆", 1: "◆－", 0: "－－"}[v]
                mcls = "t-good" if v == 2 else "t-bad"
                parts.append(
                    f'<rect class="{box}" x="{cx - 26}" y="{ty - 14}" '
                    f'width="52" height="19" rx="4"/>\n'
                )
                parts.append(
                    f'<text class="{mcls}" x="{cx}" y="{ty}" '
                    f'text-anchor="middle">{mark}</text>\n'
                )
            y += row_h
        y += 14

    notes = [
        ("t-good", "※ 青い4行（電気・ガス・交通系IC）は、そのまま頼んだだけで"
                   "のべ8回とも3か月そろった。答えがメモの中にあるため。"),
        ("t-bad", "※ 黒い6行は、そのまま頼むと のべ12回中11回がずれた。コピー代を雑費に"),
        ("t-bad", "　 入れるか事務用品に入れるかは、メモのどこにも書いていない。"),
        ("t-xs", "架空データでの実測（全56回）。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 4
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y
    alt = (
        "3か月とも同じ文字列で出てくる10件の行が、4通りの頼み方でどれだけ"
        "月をまたいで同じ費目に入ったかを並べた表。ひとつの枠の◆の数が、"
        "2回のうち3か月ともそろった回の数を表す。"
        "電気料金・ガス・交通系ICのチャージという、メモを読めば費目が決まる4行は、"
        "そのまま頼んだ回でも8回中8回そろった。"
        "コピー代・文庫本・のど飴とマスク・収納ケース・子どもの上履き・"
        "カフェでの作業という6行は、そのまま頼むと12回中11回がずれた。"
        "費目の一覧を固定すると多くがそろいはじめ、"
        "こちらが対応表を渡した列では10行すべてが2回とも3か月そろっている。"
        "そろうかどうかを分けたのは、費目がメモの中で決まるか、"
        "決めるのが自分しかいないかだった。"
    )
    (OUT / "receipt-inside-or-outside-material.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def breaking_checks_what_rings_chart() -> None:
    """AIに壊れ例を作らせたとき、実際に点検が鳴った例と鳴らなかった例を頼み方ごとに並べる。

    実測（2026-08-19・材料2本×各2回＝4回ずつ）。5条は Python で実装し、
    AIが返した「壊した記録の全文」に当てて数えた。値は check.py の出力。
    """
    rows = [
        ("そのまま「わざと壊して確かめて」", 21, 6),
        ("＋「6件作って、どの条か書いて」", 22, 2),
        ("＋「すり抜ける例も3件」", 19, 12),
        ("「条ごとに1件ずつ」に変える", 20, 0),
    ]
    label_x, label_w = 18, 252
    bar_x = label_x + label_w + 12
    unit = 340.0 / 31                # いちばん多い31例を基準に1例あたりの幅を出す
    bar_h = 16
    row_gap = 30
    top = 112

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "AIが作った壊れ例のうち、点検が実際に鳴ったのはどれだけか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の「毎朝の点検・5条」を文章で渡し、わざと壊した記録の全文を書かせた"
        "（材料2本 × 各2回 = 4回ずつ）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "5条は Python で実装してあり、返ってきた記録に当てて数えている。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 12}">'
        "濃い部分＝実際に鳴った例　薄い部分＝1条も鳴らなかった例</text>\n",
    ]

    y = top
    for label, rang, silent in rows:
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + bar_h - 3}">{_esc(label)}</text>\n'
        )
        total = rang + silent
        parts.append(
            f'<rect class="bar-old" x="{bar_x}" y="{y}" '
            f'width="{total * unit:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<rect class="bar-new" x="{bar_x}" y="{y}" '
            f'width="{rang * unit:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{bar_x + total * unit + 8:.1f}" '
            f'y="{y + bar_h - 4}">{rang} / {total}例</text>\n'
        )
        y += bar_h + row_gap

    notes = [
        ("t-bad", "※「すり抜ける例も3件」と頼んだ4回だけ、鳴らない例が12件出た。"),
        ("t-bad", "　 頼んだのは 4回 × 3件 ＝ ちょうど12件。作れないのではなく、頼まないと作らない。"),
        ("t-good", "※「条ごとに1件ずつ」に変えた4回は、20例すべてが鳴り、"),
        ("t-good", "　 AIの申告（どの条に当たるか）も 10件中10件が実際と一致した。"),
        ("t-xs", "架空データでの実測（全24回）。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "AIが作った壊れ例のうち、点検の5条が実際に鳴った例の数を頼み方4通りで並べた横棒グラフ。"
        "棒全体が作られた例の数、濃い部分が実際に鳴った例の数。"
        "そのままわざと壊して確かめてと頼んだ4回は27例中21例が鳴った。"
        "6件作ってどの条か書いてと足した4回は24例中22例。"
        "すり抜ける例も3件と足した4回は31例中19例で、鳴らない例が12件出ている。"
        "条ごとに1件ずつに変えた4回は20例すべてが鳴り、鳴らない例は0件だった。"
        "鳴らない例が大きく出たのは、すり抜ける例を明示的に頼んだ回だけで、"
        "その数は頼んだ数とちょうど同じ12件である。"
    )
    (OUT / "breaking-checks-what-rings.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def breaking_checks_who_finds_holes_chart() -> None:
    """こちらが仕込んだ2つの抜け道を、どの頼み方が指したかを並べる。

    実測（2026-08-19）。穴A＝条2は最新の日付しか見ない。穴B＝条5は1件あれば通る。
    ○の数＝材料2本×各2回＝4回のうち、その穴を指した回の数。値は hole.py と q5check.py。
    """
    rows = [
        ("壊れ例を作らせる（すり抜ける例も頼む）", 3, 4, "0〜4文"),
        ("記録は壊させず、手順書のほうを読ませる", 4, 3, "4〜11文"),
        ("こちらが作った記録を、5条で判定させる", 4, 4, "参考欄に"),
    ]
    label_x, label_w = 18, 300
    col_x = [label_x + label_w + 60, label_x + label_w + 190]
    row_h = 34
    top = 128

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "点検の抜け道は、壊させるより「読ませた」ほうが出てきた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "5条のうち2条に、こちらが抜け道を残しておいた。"
        "抜けられることは走らせる前にコードで確かめてある。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "穴A＝条2は「いちばん新しい日付」しか見ないので、古い行が積み上がっても鳴らない。"
        "</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "穴B＝条5は「1件以上あるか」しか見ないので、毎日10件ある種類が今日1件でも鳴らない。"
        "</text>\n",
    ]
    for cx, name in zip(col_x, ("穴Aを指した回", "穴Bを指した回")):
        parts.append(
            f'<text class="t-xs" x="{cx}" y="{top - 14}" '
            f'text-anchor="middle">{_esc(name)}</text>\n'
        )

    y = top
    for label, a, b, note in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for cx, v in zip(col_x, (a, b)):
            box = "box-good" if v == 4 else "box-bad"
            mcls = "t-good" if v == 4 else "t-bad"
            parts.append(
                f'<rect class="{box}" x="{cx - 30}" y="{ty - 14}" '
                f'width="60" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{mcls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{v} / 4</text>\n'
            )
        parts.append(
            f'<text class="t-xs" x="{col_x[1] + 42}" y="{ty}">{_esc(note)}</text>\n'
        )
        y += row_h

    notes = [
        ("t-good", "※ 判定をやらせた4回は、5条 × 記録3本 = 15マスが4回とも全部真値と一致した（60/60）。"),
        ("t-good", "　 そのうえで4回とも「判定には使っていない事実」という欄を自分から作り、"),
        ("t-good", "　 そこに、こちらが仕込んだ抜け道そのものを書いた。"),
        ("t-xs", "架空データでの実測（全24回）。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "点検の5条に残した2つの抜け道を、3通りの頼み方がそれぞれ何回指したかを並べた表。"
        "1つの頼み方につき材料2本かける各2回で4回ある。"
        "壊れ例を作らせた回は、穴Aを4回中3回、穴Bを4回中4回指したが、"
        "該当する文は1回あたり0文から4文だった。"
        "記録を壊させず手順書のほうを読ませた回は、穴Aを4回中4回、穴Bを4回中3回指し、"
        "該当する文は1回あたり4文から11文と多い。"
        "こちらが作った記録を5条で判定させた回は、穴Aも穴Bも4回中4回で、"
        "判定表とは別の参考欄に書かれていた。"
        "その判定表そのものは、5条かける記録3本の15マスが4回とも全部真値と一致している。"
    )
    (OUT / "breaking-checks-who-finds-holes.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def wrong_client_two_failures_chart() -> None:
    """案件を取り違えて貼ったときの事故と、止めさせたときの誤停止を、頼み方ごとに並べる。

    実測（2026-08-19・架空の案件2組×各2回＝1つの頼み方につき4回、全40回）。
    値は check.py の出力。左は「別案件を貼ったのに成果物を作った回数」、
    右は「正しい材料なのに止まった回数」。どちらも 0 でないと使えない。
    """
    rows = [
        ("そのまま「納品の連絡メールを作って」", 4, None),
        ("そのまま「検品の一覧を作って」", 4, None),
        ("＋先頭に受け皿の1行", 0, 0),
        ("＋かぶせる1枚（発注元と案件名を照合）", 0, 3),
        ("＋かぶせる1枚（発注元だけを照合）", 0, 0),
    ]
    label_x, label_w = 18, 300
    col_x = [label_x + label_w + 82, label_x + label_w + 268]
    col_names = [
        ["別案件を貼ったのに", "成果物を作った"],
        ["正しい材料なのに", "止まった"],
    ]
    row_h = 34
    top = 122

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "止めさせるまでは作ってしまう。止めさせすぎると、正しい材料でも止まる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の副業案件を2組（記事執筆・商品ページ制作）作り、"
        "保存した指示文に「別の案件の発注書」を貼って通した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "1つの頼み方につき、材料2組 × 各2回 ＝ 4回。数字はどちらも「事故が起きた回数」で、"
        "0 でないと使えない。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "※ 食い違いそのものは、そのまま頼んだ8回とも指摘された。作ってしまうかどうかは別。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 26 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, made, false_stop in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for cx, v in zip(col_x, (made, false_stop)):
            if v is None:
                parts.append(
                    f'<line class="line" x1="{cx - 8}" y1="{ty - 5}" '
                    f'x2="{cx + 8}" y2="{ty - 5}"/>\n'
                )
                continue
            box = "box-good" if v == 0 else "box-bad"
            mcls = "t-good" if v == 0 else "t-bad"
            parts.append(
                f'<rect class="{box}" x="{cx - 26}" y="{ty - 14}" '
                f'width="52" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{mcls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{v} / 4</text>\n'
            )
        y += row_h

    notes = [
        ("t-bad", "※ 上の2行＝作られたメールには、別案件の6項目（発注元・担当者・納期・分量・"),
        ("t-bad", "　 修正回数・納品形式）が4回とも6項目そのまま入っていた。正しい案件の値は社名だけ。"),
        ("t-bad", "※ 4行目＝止める基準に「案件名」を入れた版は、正しい発注書でも4回中3回止まった。"),
        ("t-bad", "　 保存側の案件名は「商品ページ制作」、発注書の案件名は「秋の保存容器」だったため。"),
        ("t-good", "※ 止める基準を「発注元の会社名だけ」にすると、別案件で4/4止まり、誤停止は0/4。"),
        ("t-xs", "架空データでの実測（全40回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "保存した指示文に別の案件の発注書を貼ったときに何が起きるかを、頼み方5通りで並べた表。"
        "架空の副業案件を2組つくり、1つの頼み方につき材料2組かける各2回で4回ずつ通した。"
        "左の列は、別案件を貼ったのに成果物を作ってしまった回数。"
        "右の列は、正しい材料を貼ったのに誤って止まった回数。どちらも0でないと使えない。"
        "そのまま納品の連絡メールを作ってと頼んだ4回は、4回とも作ってしまった。"
        "そのまま検品の一覧を作ってと頼んだ4回も、4回とも作ってしまった。"
        "指示文の先頭に受け皿を1行足した版は、作ってしまったのが0回で、誤って止まったのも0回。"
        "かぶせる1枚で発注元と案件名の両方を照合させた版は、作ってしまったのは0回だが、"
        "正しい材料なのに4回中3回も止まった。"
        "かぶせる1枚で発注元だけを照合させた版は、作ってしまったのが0回で、誤って止まったのも0回。"
        "なお、食い違いそのものは、そのまま頼んだ8回とも指摘されている。"
        "指摘するかどうかと、作ってしまうかどうかは別の話だった。"
    )
    (OUT / "wrong-client-two-failures.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def work_grew_what_comes_with_it_chart() -> None:
    """往復メールから「増えた作業」を拾わせたとき、何が崩れて何が付いてくるかを頼み方6通りで並べる。

    実測（2026-08-19・架空の往復メール12通を2本、1つの頼み方につき材料2本×各2回＝4回、全24回）。
    値は check.py の出力。左は事故の件数（真値0）、中と右は「頼んでいないものが付いた回数」。
    """
    rows = [
        ("そのまま「やることを全部挙げて」", 0, 4, 4),
        ("＋「相手の希望だけのものは入れないで」", 0, 3, 4),
        ("＋「私が決めます。金額の話は書かないで」", 0, 0, 0),
        ("4つに分けさせる（判断はしないで）", 0, 0, 0),
        ("4つに分ける＋上の禁止も足す", 0, 0, 0),
        ("保存版（4見出し以外は書かない・引用つき）", 0, 0, 0),
    ]
    label_x, label_w = 18, 268
    col_x = [label_x + label_w + 74, label_x + label_w + 208, label_x + label_w + 336]
    col_names = [
        ["相手の希望が", "やること欄に入った"],
        ["金額の語が", "出た回"],
        ["交渉・おすすめが", "出た回"],
    ]
    row_h = 34
    top = 126

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "拾い分けは崩れない。崩れないかわりに、頼んでいない交渉の話が付いてくる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の副業案件の往復メール12通を2本作り、"
        "自分が承諾した4件・相手の希望だけの3件・断った2件・発注書のぶん3件を仕込んだ。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "1つの頼み方につき、材料2本 × 各2回 ＝ 4回。左の列は事故の件数で、真値は0。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "※ 材料の中に、金額・報酬・単価の記載は1文字も無い。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 26 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, wrong, money, advice in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for cx, v in zip(col_x, (wrong, money, advice)):
            box = "box-good" if v == 0 else "box-bad"
            mcls = "t-good" if v == 0 else "t-bad"
            parts.append(
                f'<rect class="{box}" x="{cx - 26}" y="{ty - 14}" '
                f'width="52" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{mcls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{v} / 4</text>\n'
            )
        y += row_h

    notes = [
        ("t-good", "※ 左の列は24回とも0。相手が希望を書いただけのものが「やること」に入った回は0回だった。"),
        ("t-bad", "※ 上の2行では「報酬を確認したほうがよい」「再交渉を」が付く。材料に金額は1文字も無い。"),
        ("t-bad", "　 1回は「作業が5点増えている」と書いて、その直後に4点しか並べていなかった。"),
        ("t-good", "※ 4つに分ける形にすると、禁止を書かなくても金額も交渉も0回になった。"),
        ("t-xs", "架空データでの実測（全24回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "副業の往復メール12通から、自分がやることになっている作業を拾わせたときの結果を、"
        "頼み方6通りで並べた表。架空の案件2本を作り、1つの頼み方につき材料2本かける各2回で4回ずつ通した。"
        "左の列は、相手が希望を書いただけの作業が「やること」の欄に入ってしまった件数で、真値は0。"
        "中の列は、金額や報酬の語が出た回数。右の列は、交渉やおすすめが出た回数。"
        "そのままやることを全部挙げてと頼んだ4回は、左が0回、金額が4回、交渉が4回。"
        "相手の希望だけのものは入れないでと足した4回は、左が0回、金額が3回、交渉が4回。"
        "私が決めます、金額の話は書かないでと足した4回は、3つとも0回。"
        "4つに分けさせた4回も、3つとも0回。4つに分けて禁止も足した4回も、3つとも0回。"
        "保存版の4回も、3つとも0回。"
        "つまり拾い分けそのものは24回とも崩れず、崩れるかわりに、"
        "材料に1文字も書かれていない金額や交渉の話が、そのまま頼んだときだけ付いてきた。"
    )
    (OUT / "work-grew-what-comes-with-it.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def copy_ideas_that_pass_chart() -> None:
    """「30案出して」で返る30案のうち、発注書の条件を通るのが何案かを頼み方6通りで並べる。

    実測（2026-08-19・架空の商品2件×各2回＝1つの頼み方につき4回、全24回）。
    条件は4つとも機械で○×が決まる（字数・必須語・禁止語・英数字）。
    値は check.py の出力。棒は4回ぶんの最小〜最大。
    """
    rows = [
        ("条件を渡さず「30案出して」", 0, 4),
        ("条件を渡して「30案出して」", 30, 30),
        ("＋「条件を満たさない案は出さないで」", 30, 30),
        ("＋〔条件外〕の欄を作って落とさせる", 19, 22),
        ("＋「私が確かめること」も添えさせる", 20, 22),
        ("保存版（2見出しだけ・外れた条件の番号つき）", 19, 24),
    ]
    label_x, label_w = 18, 292
    plot_x = label_x + label_w + 10
    plot_w = 300
    hi = 30
    row_h = 34
    top = 120
    bar_h = 20

    def px(n: float) -> float:
        return plot_x + plot_w * n / hi

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「三十案出して」の三十は、使える案の数ではない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の商品2件（勤怠管理アプリ・温泉旅館）と、"
        "○×が機械で決まる4条件だけを並べた架空の発注書で実測。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "条件＝字数の上限／必ず入れる語／禁止語3語／英数字を使わない。"
        "どの頼み方でも、返ってきた案は24回とも30案ちょうど。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "棒は、その30案のうち4条件をすべて通った数（4回ぶんの最小〜最大）。</text>\n",
        f'<text class="t-xs" x="{px(0):.0f}" y="{top - 12}" text-anchor="middle">0</text>\n',
        f'<text class="t-xs" x="{px(15):.0f}" y="{top - 12}" text-anchor="middle">15</text>\n',
        f'<text class="t-xs" x="{px(30):.0f}" y="{top - 12}" text-anchor="middle">30案</text>\n',
    ]

    y = top
    for label, lo, up in rows:
        ty = y + 15
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{px(0):.1f}" y="{y}" '
            f'width="{plot_w}" height="{bar_h}" rx="2"/>\n'
        )
        css = "bar-out" if lo >= 19 else "bar-in"
        w = max(px(up) - px(0), 2.0)
        parts.append(
            f'<rect class="{css}" x="{px(0):.1f}" y="{y}" '
            f'width="{w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        if lo != up:
            parts.append(
                f'<rect class="bar-old" x="{px(lo):.1f}" y="{y}" '
                f'width="{px(up) - px(lo):.1f}" height="{bar_h}" rx="2"/>\n'
            )
        text = f"{lo}案" if lo == up else f"{lo}〜{up}案"
        tc = "t-bad" if up < 19 else "t"
        parts.append(
            f'<text class="{tc}" x="{px(up) + 8:.1f}" y="{ty}">{_esc(text)}</text>\n'
        )
        y += row_h

    notes = [
        ("t-bad", "※ 条件を渡さないと、温泉旅館の材料では2回とも0案。30案あって1案も使えない。"),
        ("t-good", "※ 条件を渡せば、24回のうち条件つきの20回はすべて機械判定と一致した。"),
        ("t-good", "　 〔条件外〕に落とした案が実は条件を満たしていた回は0件、逆の誤りも0件。"),
        ("t-bad", "※ ただし〔条件外〕の欄を作ると、使える案は30案から19〜24案に減る。"),
        ("t-bad", "　 減った8〜11案は、その欄を埋めるために作られた案だった。"),
        ("t-xs", "架空データでの実測（全24回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 14
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "キャッチコピーを30案出させたとき、発注書の条件を通ったのが何案かを、"
        "頼み方6通りで並べた横棒グラフ。架空の商品2件について各2回、1つの頼み方につき4回ずつ通した。"
        "条件は、字数の上限、必ず入れる語、禁止語3語、英数字を使わないの4つで、すべて機械で○×が決まる。"
        "返ってきた案は24回とも30案ちょうどだった。"
        "条件を渡さずに30案出してと頼んだ4回は、条件を通ったのが0案から4案。"
        "温泉旅館の材料では2回とも0案で、30案あって1案も使えない。"
        "条件を渡して30案出してと頼んだ4回は、4回とも30案すべてが条件を通った。"
        "条件を満たさない案は出さないでと足した4回も、4回とも30案すべて通った。"
        "条件外の欄を作って落とさせた4回は、使える案が19案から22案に減った。"
        "私が確かめることも添えさせた4回は20案から22案。"
        "保存版は19案から24案。"
        "つまり条件を渡すかどうかで0案から30案まで変わり、"
        "条件外の欄を作ると、その欄を埋めるための案が8案から11案ぶん作られて、使える案はそのぶん減る。"
    )
    (OUT / "copy-ideas-that-pass.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )



def monthly_check_carryover_chart() -> None:
    """毎月の点検で、前月の指摘を渡す／返す形を決める、が検出に効くかを頼み方6通りで並べる。

    実測（2026-08-19・架空の月次表を2か月ぶん×2本、1つの頼み方につき4回、全24回）。
    8月に指摘すべきは6件（7月から残った2件＋7月の指摘に出てこない種類の新種4件）。
    値は check.py の出力（当て方2通りの和集合）。座標は計算で出す。
    """
    rows = [
        ("前月の指摘を渡さない（6種類の指示文だけ）", 6, None, False),
        ("＋前月の指摘5件をそのまま貼る", 6, 5, False),
        ("＋「前回の指摘は答えではありません」", 6, 5, False),
        ("＋「毎月この形で返して」と返す形まで決める", 5, 5, True),
        ("＋「足し直した値と表の値を並べて」", 6, None, False),
        ("＋「来月そのまま貼れる形に短く」", 6, None, False),
    ]
    label_x, label_w = 18, 300
    col_x = [label_x + label_w + 92, label_x + label_w + 268]
    col_names = [
        ["8月の6件のうち", "指摘した数（4回とも）"],
        ["7月の5件の仕分け", "が真値と一致"],
    ]
    row_h = 38
    top = 130

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "落ちたのは「前月の指摘を渡したから」ではなく「返す形を短く決めたから」</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の月次表を2か月ぶん・2本作った。7月に異常5件（桁2・空欄2・符号1）。"
        "8月は3件が直り、2件が残り、</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "7月の指摘に出てこない種類の異常を4件（単位の混ざり・行の重複・小計の不一致・総計の不一致）足した。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "→ 8月に指摘すべきは6件。セルの位置まで真値が決まる。1つの頼み方につき4回、全24回。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 26 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, found, sort_ok, bad in rows:
        ty = y + 18
        parts.append(
            f'<text class="{"t-bad" if bad else "t"}" x="{label_x}" y="{ty}">'
            f"{_esc(label)}</text>\n"
        )
        parts.append(
            f'<rect class="{"box-bad" if bad else "box-good"}" x="{col_x[0] - 74}" '
            f'y="{ty - 14}" width="148" height="19" rx="4"/>\n'
        )
        parts.append(
            f'<text class="{"t-bad" if bad else "t-good"}" x="{col_x[0]}" y="{ty}" '
            f'text-anchor="middle">4回とも {found}/6</text>\n'
        )
        if sort_ok is None:
            parts.append(
                f'<line class="line" x1="{col_x[1] - 8}" y1="{ty - 5}" '
                f'x2="{col_x[1] + 8}" y2="{ty - 5}"/>\n'
            )
            parts.append(
                f'<text class="t-xs" x="{col_x[1]}" y="{ty + 13}" '
                f'text-anchor="middle">（渡していないので判定なし）</text>\n'
            )
        else:
            parts.append(
                f'<rect class="box-good" x="{col_x[1] - 62}" y="{ty - 14}" '
                f'width="124" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="t-good" x="{col_x[1]}" y="{ty}" '
                f'text-anchor="middle">4回とも {sort_ok}/5</text>\n'
            )
        y += row_h

    notes = [
        ("t-good", "※ 前月の指摘を貼っても貼らなくても 6/6。新しい種類の異常は見えなくならなかった。"),
        ("t-good", "※ 直った3件を「まだあります」と書いた回は、24回とも0件。"),
        ("t-good", "※ 渡して増えるのは検出ではなく「直った3件／残った2件」の仕分け。12回とも 5/5。"),
        ("t-bad", "※ 返す形まで短く決めた4回だけ 5/6。落ちたのは4回とも同じ種類＝ほかの異常と"),
        ("t-bad", "　 結び付かない、足し算だけの小計のズレ（総務部 +5,000／新宿店 +7,000）。"),
        ("t-bad", "　 代わりに、見つけた異常から派生した小計を挙げていた＝周りしか足し直していない。"),
        ("t-good", "※ 「足し直した値と表の値を並べて」を足すと、その1件も4回とも戻った。"),
        ("t-xs", "架空データでの実測（全24回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 14
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎月の表の点検で、前月の指摘を一緒に渡すことと、返す形を決めることが、"
        "新しい異常の検出に効くかを頼み方6通りで並べた表。"
        "架空の月次表を2か月ぶん、2本作った。"
        "7月版に異常を5件仕込み、8月版では3件が直り2件が残り、"
        "7月の指摘に出てこない種類の異常を4件足した。"
        "8月に指摘すべきは6件で、セルの位置まで真値が決まる。"
        "1つの頼み方につき材料2本かける各2回で4回ずつ、全部で24回通した。"
        "前月の指摘を渡さず6種類の指示文だけで頼んだ4回は、4回とも6件中6件を指摘した。"
        "前月の指摘5件をそのまま貼った4回も4回とも6件中6件。"
        "前回の指摘は答えではありませんと足した4回も4回とも6件中6件だった。"
        "つまり前月の指摘を渡しても新しい種類の異常は見えなくならなかった。"
        "ところが、前月の指摘を渡したうえで毎月この形で返してくださいと返す形まで決めた4回だけは、"
        "4回とも6件中5件にとどまった。"
        "落ちたのは4回とも同じ種類で、ほかの異常と結び付かない足し算だけの小計のズレである。"
        "材料Aでは総務部の小計が5000円多い件、材料Bでは新宿店の小計が7000円多い件だった。"
        "この4回は代わりに、見つけた異常から派生した小計のほうを挙げていた。"
        "つまり気づいた異常の周りしか足し直していない。"
        "足し直した値と表の値を並べて書いてくださいと足した4回は、"
        "その1件も含めて4回とも6件中6件に戻った。"
        "来月そのまま貼れる形に短くしてくださいと足した4回も4回とも6件中6件だった。"
        "また、直った3件をまだありますと誤って書いた回は24回とも0件。"
        "前月の指摘を渡した12回は、7月の5件が直ったか残ったかの仕分けも12回とも5件中5件が真値と一致した。"
    )
    (OUT / "monthly-check-carryover.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def tilt_leaks_to_unwritten_judgment_chart() -> None:
    """倒す方向を書いた判定と、書いていない判定で、返りがどう変わるかを4通りで並べる。

    実測（2026-08-19・架空の30行を2本、1つの頼み方につき4回、全16回）。
    値は check.py の出力。座標は計算で出す。
    """
    rows = [
        ("倒す方向を言わない（土台だけ）", "8・7・7・7", "1・1・11・10", 2, False),
        ("＋「迷ったら重要ではない側に倒して」", "5・5・5・6", "11・6・12・12", 2, False),
        ("＋倒す理由を2文", "5・5・6・4", "12・11・12・12", 2, False),
        ("＋ ! の判定にも倒す方向を書く", "5・5・3・3", "11・11・12・12", 4, True),
    ]
    label_x, label_w = 18, 250
    col_x = [label_x + label_w + 112, label_x + label_w + 312]
    col_names = [
        ["書いていない判定", "! の件数（4回ぶん）"],
        ["書いた判定", "境界12件のうち低へ（4回ぶん）"],
    ]
    row_h = 56
    top = 132

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "倒す方向は、書いていない判定にも漏れる。ただし漏れ方は回ごとに違う</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の30行を2本（問い合わせメールの件名／ニュースの見出し）。"
        "明らかに重要8件・明らかに重要でない10件・</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "どちらとも取れる境界12件。同じ回の中に、倒す方向を一度も書いていない"
        "第2の判定（! を付ける）を混ぜてある。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "1つの頼み方につき4回（材料2本 × 各2回）、全16回。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 28 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, bang, mid, agree, good in rows:
        ty = y + 18
        parts.append(
            f'<text class="{"t-good" if good else "t"}" x="{label_x}" y="{ty}">'
            f"{_esc(label)}</text>\n"
        )
        parts.append(
            f'<rect class="{"box-good" if good else "box-bad"}" x="{col_x[0] - 66}" '
            f'y="{ty - 14}" width="132" height="19" rx="4"/>\n'
        )
        parts.append(
            f'<text class="{"t-good" if good else "t-bad"}" x="{col_x[0]}" y="{ty}" '
            f'text-anchor="middle">{_esc(bang)}</text>\n'
        )
        parts.append(
            f'<rect class="box-quiet" x="{col_x[1] - 108}" y="{ty - 14}" '
            f'width="216" height="19" rx="4"/>\n'
        )
        parts.append(
            f'<text class="t" x="{col_x[1]}" y="{ty}" '
            f'text-anchor="middle">{_esc(mid)}</text>\n'
        )
        parts.append(
            f'<text class="{"t-good" if agree == 4 else "t-bad"}" x="{label_x + 14}" '
            f'y="{ty + 17}">2回転でそろった組: {agree}／4組</text>\n'
        )
        y += row_h

    notes = [
        ("t-bad", "※ 1行目→2行目＝! の指示は1文字も変えていないのに、! が 29件から21件に減った。"),
        ("t-bad", "　 倒す方向は、書いた判定の外へ漏れる。"),
        ("t-bad", "※ ただし漏れ方は安定しない。理由まで書いた3行目は、同じ材料の2回転で 6件と4件"),
        ("t-bad", "　 （中身も2件ちがう）。漏れることを当てにはできない。"),
        ("t-good", "※ ! の判定にも倒す方向を書いた4行目だけ、境界の割り当ても ! も、"),
        ("t-good", "　 2回転で4組とも完全に一致した。"),
        ("t-good", "※ 理由の2文が効いたのは「漏れ」ではなく「書いた判定の安定」のほう"),
        ("t-good", "　 （2行目は 11・6・12・12 とばらつき、3行目は 12・11・12・12）。"),
        ("t-xs", "架空データでの実測（全16回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 14
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "迷ったときに倒す方向を指示すると、指示していない別の判定まで影響を受けるかを、"
        "頼み方4通りで並べた表。"
        "架空の30行を2本（問い合わせメールの件名とニュースの見出し）作り、"
        "明らかに重要8件、明らかに重要でない10件、どちらとも取れる境界12件を仕込んだ。"
        "同じ回の中に、倒す方向を一度も書いていない第2の判定として、"
        "いますぐ知らせたいものに感嘆符を付けるという指示を混ぜてある。"
        "1つの頼み方につき材料2本かける各2回で4回ずつ、全部で16回。"
        "倒す方向を言わない土台だけの4回は、感嘆符が8件7件7件7件で合計29件。"
        "迷ったら重要ではない側に倒してくださいの1文を足した4回は、"
        "感嘆符の指示を1文字も変えていないのに5件5件5件6件の合計21件まで減った。"
        "つまり倒す方向は、書いた判定の外へ漏れる。"
        "さらに倒す理由を2文足した4回も5件5件6件4件で合計20件と、数はほとんど変わらなかった。"
        "しかも同じ材料の2回転で6件と4件になり、中身も2件ちがった。漏れ方は安定しない。"
        "感嘆符の判定にも、その判定のための倒す方向を書いた4回だけが、"
        "感嘆符5件5件3件3件で、境界12件の割り当ても感嘆符の集合も、"
        "2回転で4組とも完全に一致した。"
        "他の3通りは4組中2組しか一致していない。"
        "また、境界12件のうち重要ではない側に入った件数は、"
        "倒す方向を言わないと1件1件11件10件と材料によって正反対になり、"
        "倒す方向を書くと11件6件12件12件、理由まで書くと12件11件12件12件になった。"
        "理由の2文が効いたのは、書いていない判定への漏れではなく、書いた判定の安定のほうである。"
    )
    (OUT / "tilt-leaks-to-unwritten-judgment.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def runbook_gaps_surface_chart() -> None:
    """家族なりすましの備えの手順書を、まっさらな読み手に場面つきで通し、
    穴（書かれていないこと）が何件出たかを頼み方4通りで並べる。

    実測（2026-08-19・手順書を8本作り、それぞれ別セッションに通した＝作る8本＋通す8本）。
    値は check.py の出力。座標は計算で出す。
    """
    rows = [
        ("「備えの手順書を作って」だけ", "5・4", True),
        ("＋声で見分ける方法は書かない", "5・3", True),
        ("＋1手順1動作・判断に任せる言葉を禁止", "6・10", True),
        ("＋新しい連絡先を伝えられた場合を必ず入れる", "2・5", True),
    ]
    label_x, label_w = 18, 322
    col_x = label_x + label_w + 96
    row_h = 40
    top = 150

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "できた手順書を「初めて読む人」に通すと、書き手が気づかなかった穴が出る</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "家族を装う電話への備えの手順書を、4通りの頼み方で作らせた（各2回・全8本）。"
        "その8本を、それぞれ</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "別のまっさらなセッションに渡し、実際の場面（新しい番号を伝えてくる、"
        "ビデオ通話で顔が映る）で何をするか書かせた。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "読み手には「書いていないことを自分の知識で補わず、そこで止まって『書かれていない』と書く」"
        "と指示した。</text>\n",
        '<text class="t-good" x="18" y="112">'
        "🚨 わなの番号にかけ直す・送金する・口座番号を伝える —— 8本すべてで 0 件。"
        "どの頼み方でも、読み手は引っかからなかった。</text>\n",
        '<text class="t-xs" x="{}" y="{}" text-anchor="middle">'.format(col_x, top - 22)
        + "読み手が挙げた</text>\n",
        '<text class="t-xs" x="{}" y="{}" text-anchor="middle">'.format(col_x, top - 9)
        + "「書かれていない」穴（2回ぶん）</text>\n",
    ]

    y = top
    for label, gaps, _ in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{col_x - 60}" y="{ty - 14}" '
            f'width="120" height="19" rx="4"/>\n'
        )
        parts.append(
            f'<text class="t" x="{col_x}" y="{ty}" '
            f'text-anchor="middle">{_esc(gaps)} 件</text>\n'
        )
        y += row_h

    notes = [
        ("t", "※ どれだけ丁寧に頼んでも、穴は0にならなかった。穴の中身がそのまま直す先になる。"),
        ("t", "※ 場面には、どの手順書にも書きにくい罠を入れた＝相手が新しい電話番号を伝えてくる。"),
        ("t-good", "※ その罠への対応を『必ず入れて』と頼んだ最後の版は、その穴が消えた（場面Aで2件）。"),
        ("t-bad", "※ 代わりに別の穴が残った＝どの版でも、ビデオ通話（顔が映る）は手順書に無いと指摘された。"),
        ("t-bad", "　 読み手は『声で判断しない』を顔にも当てはめたが、それは手順書の指示ではなく読み手の補い。"),
        ("t-xs", "架空データでの実測（作る8本・通す8本）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 14
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "家族を装う電話への備えの手順書を、まっさらな読み手に場面つきで通したとき、"
        "書かれていない穴が何件出たかを頼み方4通りで並べた表。"
        "手順書を4通りの頼み方で各2回、全8本作らせ、その8本をそれぞれ別のセッションに渡して、"
        "新しい電話番号を伝えてくる、ビデオ通話で顔が映るという場面で何をするか書かせた。"
        "読み手には、書いていないことを自分の知識で補わず、そこで止まって書かれていないと書くよう指示した。"
        "まず安全の結果として、わなの番号にかけ直す、送金する、口座番号を伝えるという禁止動作は、"
        "8本すべてで0件だった。どの頼み方でも読み手は引っかからなかった。"
        "読み手が挙げた書かれていない穴の件数は、"
        "備えの手順書を作ってとだけ頼んだ版が5件と4件、"
        "声で見分ける方法は書かないでと足した版が5件と3件、"
        "1手順1動作にして判断に任せる言葉を禁止した版が6件と10件、"
        "新しい連絡先を伝えられた場合を必ず入れてと足した版が2件と5件だった。"
        "どれだけ丁寧に頼んでも穴は0にならず、穴の中身がそのまま直す先になる。"
        "場面には、どの手順書にも書きにくい罠として、相手が新しい電話番号を伝えてくる状況を入れた。"
        "その罠への対応を必ず入れてと頼んだ最後の版では、その穴が消えて場面Aで2件になった。"
        "代わりに別の穴が残り、どの版でもビデオ通話で顔が映る場合が手順書に無いと指摘された。"
        "読み手は声で判断しないという原則を顔にも当てはめたが、"
        "それは手順書に書かれた指示ではなく読み手が補った部分である。"
    )
    (OUT / "runbook-gaps-surface.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def queue_blocked_row_where_it_goes_chart() -> None:
    """毎日1件ずつ回す待ち行列で、「処理できない行」がどこへ行ったかを頼み方4通りで並べる。

    実測（2026-08-19・材料2本×各2回＝4系列ずつ、各系列を2回転）。
    並びは、2回転目に必ず「処理できない行」が未処理の先頭に来るよう固定してある。
    値は split.py と pos.py の出力。
    """
    rows = [
        ("そのまま「済の印を付けて」", 4, 0, 0),
        ("＋印を固定・ほかの行は1文字も変えない", 1, 3, 0),
        ("＋「できない行は - [!] にして理由を書く」", 4, 0, 0),
        ("＋「できない行はいちばん下に移す」", 1, 0, 4),
    ]
    label_x, label_w = 18, 292
    col_x = [label_x + label_w + 52, label_x + label_w + 168, label_x + label_w + 288]
    col_names = [["できない印が", "付いた"], ["行き先が無い", "（そのまま）"], ["いちばん下へ", "移った"]]
    row_h = 34
    top = 118

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "縛りを足したほうで、「処理できない行」の行き先が消えた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の待ち行列12行（済4・前回できなかった2・未処理6）を作り、"
        "1回転目の返りをそのまま2回転目に渡した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "未処理の2番目は、資料が取れていなくてどうしても処理できない行にしてある。"
        "1つの頼み方につき4系列。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 26 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, ok_mark, none, moved in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for cx, v, good in zip(col_x, (ok_mark, none, moved), (True, False, True)):
            if v == 0:
                parts.append(
                    f'<line class="line" x1="{cx - 8}" y1="{ty - 5}" '
                    f'x2="{cx + 8}" y2="{ty - 5}"/>\n'
                )
                continue
            box = "box-good" if good else "box-bad"
            mcls = "t-good" if good else "t-bad"
            parts.append(
                f'<rect class="{box}" x="{cx - 26}" y="{ty - 14}" '
                f'width="52" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{mcls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{v} / 4</text>\n'
            )
        y += row_h

    notes = [
        ("t-bad", "※ 2行目だけが事故。印を固定して「ほかの行は1文字も変えないで」と縛ると、"),
        ("t-bad", "　 できない行は - [ ] のまま同じ位置に残り、明日もまた先頭で引っかかる。"),
        ("t-good", "※ 1行目は、指示文で - [!] と言っていないのに4系列とも付けた。"),
        ("t-good", "　 待ち行列にもとから - [!] の行が2件あり、それに倣っている。"),
        ("t-xs", "架空データでの実測（全32回）。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎日1件ずつ処理する待ち行列で、どうしても処理できない行が2回転目にどうなったかを"
        "頼み方4通りで並べた表。1つの頼み方につき4系列ある。"
        "そのまま済の印を付けてと頼んだ4系列は、4系列ともできない印が付いた。"
        "印を固定してほかの行は1文字も変えないでと縛った4系列は、"
        "できない印が付いたのは1系列だけで、残る3系列は行き先が無くそのまま残った。"
        "できない行はハイフン角かっこびっくりにして理由を書くと足した4系列は、4系列とも印が付いた。"
        "できない行はいちばん下に移すと足した4系列は、4系列とも待ち行列のいちばん下へ移った。"
        "縛りを足したほうだけで、できない行の行き先が消えている。"
    )
    (OUT / "queue-blocked-row-where-it-goes.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def queue_what_never_broke_chart() -> None:
    """心配していた事故が、32回とも起きなかったことを並べる。

    実測（2026-08-19）。真値はすべて0または1で、check.py が突き合わせた。
    """
    rows = [
        ("処理できない行に「済」が付いた", "0 / 32回", True),
        ("済にした行が、次の回でまた未処理に戻った", "0 / 32回", True),
        ("もとから済・できなかった印だった6行が変わった", "0 / 32回", True),
        ("待ち行列の行が消えた（12行が保たれなかった）", "0 / 32回", True),
        ("1回で処理された件数が1件でなかった", "0 / 16系列", True),
        ("できない行の行き先が無くなった", "3 / 16系列", False),
    ]
    label_x, label_w = 18, 392
    val_x = label_x + label_w + 76
    row_h = 30
    top = 108

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "心配していた事故は起きなかった。起きたのは1つだけ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "「済の印を付けさせると、失敗した行にも済が付いて永久に飛ばされる」"
        "という見立てで測りはじめた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "真値はすべて機械が出している（済4行・できなかった2行・未処理6行の12行を、"
        "1行ずつ突き合わせた）。</text>\n",
        f'<text class="t-xs" x="{val_x}" y="{top - 12}" text-anchor="middle">'
        "実測</text>\n",
    ]

    y = top
    for label, val, good in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        box = "box-good" if good else "box-bad"
        mcls = "t-good" if good else "t-bad"
        parts.append(
            f'<rect class="{box}" x="{val_x - 58}" y="{ty - 14}" '
            f'width="116" height="19" rx="4"/>\n'
        )
        parts.append(
            f'<text class="{mcls}" x="{val_x}" y="{ty}" '
            f'text-anchor="middle">{_esc(val)}</text>\n'
        )
        y += row_h

    notes = [
        ("t-good", "※ 上の5つは、4通りの頼み方すべてで0だった。"
                   "済の印そのものは、素朴に頼んでも壊れない。"),
        ("t-bad", "※ 最後の1つだけが事故で、しかも起きたのは"
                  "「印を固定して1文字も変えるな」と縛った回だけ。"),
        ("t-xs", "架空データでの実測（全32回）。生の返りは docs/evidence/ に置いてある。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "待ち行列を毎日1件ずつ処理させる形で、起こりうる事故を6つ数えた表。"
        "処理できない行に済が付いたのは32回中0回。"
        "済にした行が次の回でまた未処理に戻ったのも0回。"
        "もとから済またはできなかった印だった6行が変わったのも0回。"
        "待ち行列の行が消えたのも0回。"
        "1回で処理された件数が1件でなかったのは16系列中0系列。"
        "唯一起きたのは、できない行の行き先が無くなったことで、16系列中3系列。"
        "その3系列はすべて、印を固定してほかの行は1文字も変えないでと縛った頼み方だった。"
    )
    (OUT / "queue-what-never-broke.svg").write_text(
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



def broken_morning_who_decides_chart() -> None:
    """記録が途切れている朝（今朝の行が無い）に、頼み方4通りが何と答えたかを並べる。

    実測（2026-08-20・架空の実行の記録3本、1つの頼み方につき材料3本×各2回＝6回、全24回）。
    ここに出すのは材料A（今朝の行が無い＝記録だけでは決まらない朝）の2回ぶん。
    値は check.py の出力。座標は計算で出す。
    """
    rows = [
        ("そのまま「なぜ動かなかったのか教えて」",
         "「実行そのものが記録に無い」", "2回", False),
        ("＋3択だけ渡す（実行されていない／遅れた／取得0件）",
         "4回とも「1. 実行されていない」", "4回", False),
        ("＋「どれにも当たらないならそう書いて」",
         "4回とも「どれにも当たらない」", "4回", True),
        ("＋「根拠になった行をそのままコピーして」",
         "2回とも「どれにも当たらない」", "2回", True),
        ("保存版＝3行に固定（区分／根拠／記録に無いこと）",
         "2回とも「この記録では決まらない」", "2回", True),
    ]
    label_x = 18
    count_x = 640
    ans_x = 38
    row_h = 54
    top = 138

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "記録が途切れている朝。候補を3つだけ渡すと、決まらないのに1つ選ぶ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の「毎朝の実行の記録」14日ぶん。今朝（8/19）の行だけが無い。"
        "行が無い状態は「実行されていない」とも</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「まだ書かれていない（遅れて走っている途中）」とも両立するので、"
        "この記録だけでは3択のどれとも決まらない。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "1つの頼み方につき2回。下の行の指示文は、上の行に足し重ねてある。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "※ 記録には「通信」「権限」「制限」「仕様変更」など24語の原因語が1語も出てこない"
        "（走らせる前に検算）。</text>\n",
    ]
    parts.append(
        f'<text class="t-xs" x="{label_x}" y="{top - 12}">'
        "頼み方（下の行は、上の行に足し重ねてある）／その下は、今朝について返りが書いたこと</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="{count_x}" y="{top - 12}">通した回数</text>\n'
    )

    y = top
    for label, answer, count, good in rows:
        ty = y + 16
        parts.append(
            f'<text class="{"t-good" if good else "t"}" x="{label_x}" y="{ty}">'
            f"{_esc(label)}</text>\n"
        )
        parts.append(
            f'<text class="t" x="{count_x}" y="{ty}">{_esc(count)}</text>\n'
        )
        box_w = len(answer) * 13.6 + 18
        parts.append(
            f'<rect class="{"box-good" if good else "box-bad"}" x="{ans_x}" '
            f'y="{ty + 6}" width="{box_w:.0f}" height="21" rx="4"/>\n'
        )
        parts.append(
            f'<text class="{"t-good" if good else "t-bad"}" x="{ans_x + 9}" y="{ty + 21}">'
            f"{_esc(answer)}</text>\n"
        )
        y += row_h

    notes = [
        ("t-bad", "※ 2行目が核。候補を3つ渡すと、記録がその3つを見分けられない朝でも、4回とも1つ選んだ。"),
        ("t-good", "※ 「どれにも当たらないならそう書いて」を1行足すと、4回とも選ばずに理由を書いた。"),
        ("t-good", "　 返り自身が「行が無いことは、実行されなかった証拠にも、まだ記録されていない証拠にもなります」。"),
        ("t-good", "※ 記録の中で答えが決まる朝（遅れた／取得0件）は、4通りとも16回すべて当てた。ここは崩れない。"),
        ("t-xs", "この表は「記録が途切れている朝」の14通ぶん。全体では9個の頼み方で56通。生の返りは docs/evidence/ に全文。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "自動実行が動かなかった朝に、実行の記録を貼って原因を聞いたときの返りを、"
        "頼み方4通りで並べた表。"
        "材料は架空の毎朝の実行の記録14日ぶんで、今朝の行だけが無い。"
        "行が無い状態は、実行されていないとも、遅れてまだ書かれていないとも両立するので、"
        "この記録だけでは3択のどれとも決まらない。1つの頼み方につき2回ずつ通した。"
        "そのままなぜ動かなかったのか教えてと頼んだ2回は、実行そのものが記録に無いと書いた。"
        "3択だけを渡した4回は、4回とも1の実行されていないを選んだ。"
        "どれにも当たらないならそう書いてくださいという1行を足した4回は、"
        "4回ともどれにも当たらないと答えた。"
        "さらに根拠になった行をそのままコピーしてくださいを足した2回も、"
        "2回ともどれにも当たらないと答えた。"
        "保存版として区分と根拠と記録に無いことの3行に固定した2回も、"
        "2回とも区分の欄にこの記録では決まらないと書いた。"
        "核は2行目で、候補を3つ渡すと、記録がその3つを見分けられない朝でも1つ選ぶ。"
        "受け皿の1行を足した4回は、選ばずに理由を書いた。"
        "なお、記録の中で答えが決まる朝、つまり遅れた朝と取得0件の朝は、"
        "4通りの頼み方すべてで16回とも当たっており、そこは崩れていない。"
    )
    (OUT / "broken-morning-who-decides.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def broken_morning_causes_not_in_log_chart() -> None:
    """記録に1語も出てこない原因語を、原因として何件挙げたかを頼み方4通りで並べた棒グラフ。

    実測（2026-08-20・全24回）。当て方を2通り変えても並びが同じかを見る（台帳★51）。
    棒の長さは件数から計算する。
    """
    rows = [
        ("そのまま「なぜ動かなかったのか教えて」", 26, 16),
        ("＋3択だけ渡す", 10, 6),
        ("＋「どれにも当たらないならそう書いて」", 5, 3),
        ("＋「根拠になった行をそのままコピーして」", 0, 0),
    ]
    label_x, label_w = 18, 268
    plot_x = label_x + label_w
    plot_w = 330
    top = 128
    row_h = 58
    unit = plot_w / 28.0
    bar_h = 15

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "記録に1語も無い原因を、いくつ挙げたか（6回ぶんの合計・当て方2通り）</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の実行の記録3本（今朝の行が無い／2時間遅れた／取得0件）に、"
        "1つの頼み方につき材料3本 × 各2回 ＝ 6回。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "記録には「通信」「権限」「制限」「仕様変更」など24語が1語も出てこない"
        "（走らせる前に検算した）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "濃い棒＝24語で数えた件数。薄い棒＝「記録の外にしか根拠が無い」8語だけに絞って数えた件数。</text>\n",
    ]
    for v in (0, 10, 20):
        gx = plot_x + v * unit
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + row_h * len(rows) - 26}" stroke-dasharray="3 4"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{gx:.1f}" y="{top - 12}" '
            f'text-anchor="middle">{v}件</text>\n'
        )

    y = top
    for label, wide, narrow in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty + 9}">{_esc(label)}</text>\n')
        for i, (val, klass) in enumerate(((wide, "bar-new"), (narrow, "bar-old"))):
            by = ty + i * (bar_h + 4)
            w = max(val * unit, 2.0)
            parts.append(
                f'<rect class="{klass}" x="{plot_x:.1f}" y="{by - 11}" '
                f'width="{w:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            cls = "t-good" if val == 0 else "t"
            parts.append(
                f'<text class="{cls}" x="{plot_x + w + 8:.1f}" y="{by + 1}">'
                f"{val}件</text>\n"
            )
        y += row_h

    notes = [
        ("t-bad", "※ そのまま聞いた6回は、記録に根拠が1行も無い原因を26件並べた。うち1回は5つを「可能性の高い順」で。"),
        ("t-bad", "　 順位の根拠も記録には無い。読む側からは、記録から決まったことと見分けがつかない。"),
        ("t-good", "※ いちばん下の6回は0件。返り自身が「なぜ取得が0件になったのかは、この記録には書かれて"),
        ("t-good", "　 いないので判断できません」と書いて止まった。"),
        ("t-xs", "当て方を2通りに変えても並びは同じ（26>10>5>0 と 16>6>3>0）。生の返りは docs/evidence/ に全文。"),
    ]
    y += 2
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "自動実行が動かなかった朝に原因を聞いたとき、"
        "実行の記録に1語も出てこない原因語をいくつ挙げたかを、頼み方4通りで並べた横棒グラフ。"
        "架空の実行の記録3本、つまり今朝の行が無いもの、2時間遅れたもの、取得0件のものに、"
        "1つの頼み方につき材料3本かける各2回で6回ずつ、全部で24回通した。"
        "記録には通信、権限、制限、仕様変更など24語の原因語が1語も出てこないことを、"
        "走らせる前に検算してある。"
        "濃い棒は24語で数えた件数、薄い棒は記録の外にしか根拠が無い8語だけに絞って数えた件数。"
        "そのままなぜ動かなかったのか教えてと頼んだ6回は26件と16件。"
        "3択だけを渡した6回は10件と6件。"
        "どれにも当たらないならそう書いてくださいを足した6回は5件と3件。"
        "根拠になった行をそのままコピーしてくださいまで足した6回は、0件と0件だった。"
        "当て方を2通りに変えても並びは同じで、26が10、5、0と減り、16が6、3、0と減る。"
        "そのまま聞いた回では、記録に根拠が1行も無い原因が可能性の高い順として並ぶことがあり、"
        "その順位の根拠も記録には書かれていない。"
        "いちばん下の頼み方では、返り自身がなぜ取得が0件になったのかはこの記録には書かれていないので"
        "判断できませんと書いて止まった。"
    )
    (OUT / "broken-morning-causes-not-in-log.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def unread_mark_where_it_lands_chart() -> None:
    """本文が取れなかった項目の要約に「読んでいない」という断りが付くか、
    付くとしたら何行目に入るかを、頼み方5通りで並べる。

    実測（2026-08-20・架空の一覧20件を4本、全24回）。値は check2.py の出力。
    """
    rows = [
        ("そのまま「1件ずつ3行で要約して」", "80/80", "0/80", "0/80", 8, False),
        ("＋「本文を読んでいない前提で書いて」", "40/40", "0/40", "10/40", 4, False),
        ("＋「1行目の先頭に〔本文未読〕と付けて」", "40/40", "40/40", "40/40", 4, True),
        ("＋「断定しない書き方にして」", "40/40", "40/40", "40/40", 4, True),
        ("本文の行が無い一覧＋〔本文未読〕の印", "40/40", "40/40", "40/40", 4, True),
    ]
    label_x = 18
    col_x = [372, 470, 576]
    col_names = [
        ["読んでいないという", "断りが付いた"],
        ["〔本文未読〕", "の印が付いた"],
        ["断りが", "1行目に入った"],
    ]
    row_h = 44
    top = 146

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "断りは付く。ただし、こちらが場所を決めるまで1行目には来ない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の一覧20件を4本。うち10件は本文あり（平均233字）、10件は本文が取れていない。"
        "薄い10件の説明文には、</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "あとで数えられる数字をちょうど1個だけ置いた。分母は「薄い10件 × 回数」。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "上4行は「本文: 取得できませんでした」と書いてある一覧。"
        "いちばん下は、本文の行そのものが無い一覧。</text>\n",
        '<text class="t-bad" x="18" y="105">'
        "※ 心配していた事故は起きなかった＝24回・240件のうち、"
        "材料に無い数字が要約に出た件数は0件。</text>\n",
        '<text class="t-bad" x="18" y="124">'
        "　 本文の行が無い一覧でも、頼まないうちから40件とも自分で断った。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 26 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, got, mark, first, n, good in rows:
        ty = y + 18
        parts.append(
            f'<text class="{"t-good" if good else "t"}" x="{label_x}" y="{ty}">'
            f"{_esc(label)}</text>\n"
        )
        parts.append(
            f'<text class="t-xs" x="{label_x + 8}" y="{ty + 16}">'
            f"（同じ指示文を{n}回）</text>\n"
        )
        for cx, val, ok in ((col_x[0], got, True),
                            (col_x[1], mark, mark != "0/80" and mark != "0/40"),
                            (col_x[2], first, good)):
            box = "box-good" if ok else "box-bad"
            cls = "t-good" if ok else "t-bad"
            parts.append(
                f'<rect class="{box}" x="{cx - 40}" y="{ty - 14}" '
                f'width="80" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{_esc(val)}</text>\n'
            )
        y += row_h

    notes = [
        ("t-bad", "※ 1行目が核。そのまま頼んだ8回では、断りは80件とも付いたのに、80件とも1行目ではなかった。"),
        ("t-bad", "　 一覧ページで1行目しか見せない形にすると、断りは読者に届かない。"),
        ("t-bad", "※ 「本文を読んでいない前提で書いて」だけだと、置き場所が4回で3通りに割れた"),
        ("t-bad", "　 （1行目10件・途中の行10件・最終行20件）。付くことは決まっても、場所は決まらない。"),
        ("t-good", "※ 置き場所を指定した16回は、160件とも1行目。本文がある10件に誤って印が付いた件数は0件。"),
        ("t-xs", "架空データでの実測（全24回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 14
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "本文が取れなかった項目の要約に、読んでいないという断りが付くか、"
        "付くとしたら何行目に入るかを、頼み方5通りで並べた表。"
        "架空の一覧20件を4本作り、うち10件は本文あり、10件は本文が取れていない状態にした。"
        "分母は薄い10件かける回数。"
        "そのまま1件ずつ3行で要約してと頼んだ8回では、断りは80件中80件に付いたが、"
        "印は0件で、1行目に入ったのは0件だった。80件とも最終行である。"
        "本文を読んでいない前提で書いてを足した4回では、断りは40件中40件に付き、"
        "印は0件、1行目に入ったのは10件だった。残りは途中の行が10件、最終行が20件で、"
        "4回で3通りに割れている。"
        "1行目の先頭に本文未読と付けてを足した4回では、断り40件、印40件、1行目40件。"
        "断定しない書き方にしてを足した4回も同じく40件、40件、40件。"
        "本文の行そのものが無い一覧に印を頼んだ4回も、40件、40件、40件だった。"
        "心配していた事故は起きておらず、24回240件のうち、"
        "材料に無い数字が要約に出た件数は0件である。"
        "本文の行が無い一覧でも、頼まないうちから40件とも自分から断りを書いた。"
        "本文がある10件に誤って印が付いた件数も0件だった。"
    )
    (OUT / "unread-mark-where-it-lands.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def unread_mark_line_position_chart() -> None:
    """断りが「何行目」に入ったかの内訳を、頼み方ごとに横棒で並べる。

    実測（2026-08-20・全24回）。棒の長さは件数の割合から計算する。
    """
    rows = [
        ("そのまま「3行で要約して」（8回・80件）", 0, 0, 80, 80),
        ("＋「読んでいない前提で書いて」（4回・40件）", 10, 10, 20, 40),
        ("＋「1行目の先頭に〔本文未読〕」（4回・40件）", 40, 0, 0, 40),
        ("＋「断定しない書き方に」（4回・40件）", 40, 0, 0, 40),
        ("本文の行が無い一覧＋印（4回・40件）", 40, 0, 0, 40),
    ]
    label_x = 18
    plot_x = 330
    plot_w = 300
    top = 128
    row_h = 52
    bar_h = 22

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「本文を読んでいない」という断りは、何行目に入ったか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "3行の要約のうち、断りがどの行に入ったかを数えた。読者が一覧で見るのは1行目だけ、"
        "という前提で読む。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "分母は「本文が取れていない10件 × 回数」。棒の中の数字は件数。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "濃い＝1行目　／　中間＝途中の行　／　薄い＝最終行</text>\n",
    ]

    y = top
    for label, first, mid, last, total in rows:
        ty = y + 16
        parts.append(f'<text class="t" x="{label_x}" y="{ty + 6}">{_esc(label)}</text>\n')
        x = plot_x
        for val, klass in ((first, "bar-new"), (mid, "bar-in"), (last, "bar-old")):
            if val == 0:
                continue
            w = plot_w * val / total
            parts.append(
                f'<rect class="{klass}" x="{x:.1f}" y="{ty - 8}" '
                f'width="{w:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-xs" x="{x + w / 2:.1f}" y="{ty + 7}" '
                f'text-anchor="middle">{val}件</text>\n'
            )
            x += w
        y += row_h

    notes = [
        ("t-bad", "※ そのまま頼むと、80件が80件とも最終行だった。1行目に入った回は1件も無い。"),
        ("t-bad", "※ 前提だけを伝えた4回は、1行目・途中・最終行の3通りに割れた。同じ指示文で割れている。"),
        ("t-good", "※ 「1行目の先頭に」まで指定した12回は、120件とも1行目。割れは無くなった。"),
        ("t-xs", "架空データでの実測（全24回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "本文を読んでいないという断りが、3行の要約のうち何行目に入ったかを、"
        "頼み方5通りで並べた横棒グラフ。"
        "分母は本文が取れていない10件かける回数で、濃い部分が1行目、"
        "中間の色が途中の行、薄い部分が最終行である。"
        "そのまま3行で要約してと頼んだ8回・80件は、1行目が0件、途中が0件、最終行が80件。"
        "読んでいない前提で書いてを足した4回・40件は、1行目が10件、途中の行が10件、最終行が20件で、"
        "同じ指示文なのに3通りに割れた。"
        "1行目の先頭に本文未読と付けてを足した4回・40件は、40件とも1行目。"
        "断定しない書き方にを足した4回・40件も40件とも1行目。"
        "本文の行そのものが無い一覧に印を頼んだ4回・40件も40件とも1行目だった。"
        "つまり断りが付くかどうかは崩れておらず、崩れるのは置き場所のほうである。"
        "一覧ページで1行目しか見せない形にすると、そのまま頼んだ場合の断りは読者に届かない。"
    )
    (OUT / "unread-mark-line-position.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def false_alarm_today_vs_tomorrow_chart() -> None:
    """誤報を1件止めたあと、今日の記録と翌日の記録で結果がどう違うかを並べる。

    実測（2026-08-20・架空の点検5条と記録30行を2組、3通りの直し方 × 各2回 × 2組 ＝ 全12回）。
    値は check.py / check2.py の出力。座標は計算で出す。
    """
    rows = [
        ("そのまま「この誤検知が出ないように直して」", "10/10", "0件", "7/12", 4),
        ("＋「検査は消さないで。この1件だけを除く条件を」", "10/10", "0件", "8/12", 4),
        ("＋「直す前に鳴っていた行が全部まだ鳴るか確かめて」", "10/10", "0件", "9/12", 4),
    ]
    label_x = 18
    col_x = [340, 436, 560]
    col_names = [
        ["今日の記録", "本物10件の検出"],
        ["今日の記録", "巻き添え"],
        ["翌日の記録", "桁落ち3件の検出"],
    ]
    row_h = 50
    top = 150

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "誤報を1件止めても、今日は何も減らない。減るのは翌日から</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の「毎朝の点検・5条」と記録30行を2組。各条に本物の異常を2件ずつ＝10件と、"
        "第3条に当たってしまう</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "無害な行を1件（誤報の種）仕込んだ。①5条を当てる →"
        "②誤報の1行だけ見せて直させる → ③同じ記録に当て直す</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "→ ④翌日の記録（別の20行）に当てる。1つの直し方につき、記録2組 × 各2回 ＝ 4回。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "翌日の記録には、元の第3条なら拾えるはずの桁落ちを3件だけ入れてある"
        "（ほかの条の違反は0件）。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 28 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, keep, lost, tomorrow, n in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        parts.append(
            f'<text class="t-xs" x="{label_x + 8}" y="{ty + 16}">（{n}回）</text>\n'
        )
        for cx, val, good, w in ((col_x[0], keep, True, 60),
                                 (col_x[1], lost, True, 50),
                                 (col_x[2], tomorrow, False, 60)):
            box = "box-good" if good else "box-bad"
            cls = "t-good" if good else "t-bad"
            parts.append(
                f'<rect class="{box}" x="{cx - w // 2}" y="{ty - 14}" '
                f'width="{w}" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{_esc(val)}</text>\n'
            )
        y += row_h

    notes = [
        ("t-good", "※ 心配していた事故は今日の記録には出なかった＝12回とも、直す前に鳴っていた本物10件は全部まだ鳴る。"),
        ("t-good", "　 誤報の1行は12回とも止まり、条文が丸ごと消えた回も0回（12回とも5条そろっている）。"),
        ("t-bad", "※ 翌日の記録では、12回で合わせて12件を見落とした（3件 × 12回 ＝ 36件のうち24件しか拾えない）。"),
        ("t-bad", "　 12回のうち11回が、同じ1件を落とした＝「誤報の種と同じ品目」の桁落ち。除外がその品目ごと効くため。"),
        ("t-good", "※ 7/12回は、頼んでいないのに「その行は除外に当たるので挙がっていません」と自分から書いた。"),
        ("t-xs", "架空データでの実測（全12回・各4段）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の点検の誤報を1件だけ止めさせたあと、今日の記録と翌日の記録で結果がどう変わるかを、"
        "直し方3通りで並べた表。"
        "架空の点検5条と記録30行を2組作り、各条に本物の異常を2件ずつ合計10件と、"
        "第3条に当たってしまう無害な行を1件仕込んだ。"
        "手順は4段で、5条を当てる、誤報の1行だけ見せて直させる、同じ記録に当て直す、"
        "翌日の別の記録に当てる。1つの直し方につき記録2組かける各2回で4回ずつ、全12回。"
        "今日の記録では、3通りとも本物10件を10件とも検出し、巻き添えは0件だった。"
        "誤報の1行は12回とも止まり、条文が丸ごと消えた回も0回である。"
        "ところが翌日の記録では、そのまま直させた4回が桁落ち3件のうち7件しか拾えず、"
        "検査は消さないでこの1件だけを除く条件をと足した4回が8件、"
        "直す前に鳴っていた行が全部まだ鳴るか確かめてと足した4回が9件だった。"
        "合わせて36件のうち24件しか拾えず、12件を見落としている。"
        "しかも12回のうち11回が同じ1件を落としていて、それは誤報の種と同じ品目の桁落ちだった。"
        "除外がその品目ごと効くためである。"
        "なお7回は、頼んでいないのに、その行は除外に当たるので挙がっていませんと自分から書いた。"
    )
    (OUT / "false-alarm-today-vs-tomorrow.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def false_alarm_what_goes_blind_chart() -> None:
    """翌日の記録で、桁落ち3件のうち何件を拾えたかを横棒で並べる。

    実測（2026-08-20・全12回）。棒の長さは件数から計算する。
    """
    rows = [
        ("そのまま「この誤検知が出ないように直して」", 7, 12),
        ("＋「検査は消さないで。1件だけを除く条件を」", 8, 12),
        ("＋「直す前に鳴っていた行がまだ鳴るか確かめて」", 9, 12),
    ]
    label_x = 18
    plot_x = 322
    plot_w = 300
    top = 132
    row_h = 54
    bar_h = 24

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "翌日の記録で、元の条文なら拾えたはずの桁落ちを何件拾えたか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "翌日の記録（20行）には、元の第3条が拾うはずの桁落ちを3件だけ入れてある。"
        "1つの直し方につき4回なので、</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "3件 × 4回 ＝ 12件が満点。ほかの4条に当たる違反は1件も入れていない。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "濃い＝拾えた件数　／　薄い＝見落とした件数</text>\n",
    ]
    for v in (0, 4, 8, 12):
        gx = plot_x + plot_w * v / 12
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + row_h * len(rows) - 22}" stroke-dasharray="3 4"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{gx:.1f}" y="{top - 12}" '
            f'text-anchor="middle">{v}件</text>\n'
        )

    y = top
    for label, got, total in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty + 4}">{_esc(label)}</text>\n')
        w1 = plot_w * got / total
        parts.append(
            f'<rect class="bar-new" x="{plot_x:.1f}" y="{ty - 10}" '
            f'width="{w1:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{plot_x + w1 / 2:.1f}" y="{ty + 6}" '
            f'text-anchor="middle">{got}件</text>\n'
        )
        w2 = plot_w - w1
        if w2 > 1:
            parts.append(
                f'<rect class="bar-old" x="{plot_x + w1:.1f}" y="{ty - 10}" '
                f'width="{w2:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-xs" x="{plot_x + w1 + w2 / 2:.1f}" y="{ty + 6}" '
                f'text-anchor="middle">{total - got}</text>\n'
            )
        y += row_h

    notes = [
        ("t-bad", "※ どの直し方でも満点にならない。12回で合わせて12件の見落とし。"),
        ("t-bad", "※ 落ちたのはほぼ同じ1件＝12回中11回が「誤報の種と同じ品目」の桁落ちだった。"),
        ("t-bad", "　 品目名で除外すると、その品目の今後の異常が丸ごと見えなくなる。"),
        ("t-good", "※ 満点だったのは1回だけ。第3条を除外で直さず、"),
        ("t-good", "　 「同じ品目の多数派と違う金額の行を挙げる」に書き換えた回。"),
        ("t-xs", "架空データでの実測（全12回）。誤報が翌日に戻った回は12回とも0回だった。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "誤報を1件止めるよう直させた点検の条文を、翌日の記録に当てたときに、"
        "元の条文なら拾えたはずの桁落ちを何件拾えたかを、直し方3通りで並べた横棒グラフ。"
        "翌日の記録20行には、元の第3条が拾うはずの桁落ちを3件だけ入れてあり、"
        "1つの直し方につき4回なので3件かける4回で12件が満点である。"
        "ほかの4条に当たる違反は1件も入れていない。"
        "そのままこの誤検知が出ないように直してと頼んだ4回は12件中7件で、5件の見落とし。"
        "検査は消さないで1件だけを除く条件をと足した4回は8件で、4件の見落とし。"
        "直す前に鳴っていた行がまだ鳴るか確かめてと足した4回は9件で、3件の見落としだった。"
        "どの直し方でも満点にならず、12回で合わせて12件を見落としている。"
        "落ちたのはほぼ同じ1件で、12回中11回が誤報の種と同じ品目の桁落ちだった。"
        "品目名で除外すると、その品目の今後の異常が丸ごと見えなくなるためである。"
        "満点だったのは1回だけで、第3条を除外で直さず、"
        "同じ品目の多数派と違う金額の行を挙げる、という条文に書き換えた回だった。"
        "なお、誤報そのものが翌日に戻った回は12回とも0回である。"
    )
    (OUT / "false-alarm-what-goes-blind.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8"
    )


def qwen38_two_weights_chart() -> None:
    """公開された2つの重みは、名前が似ているだけで別物だという図。

    出典＝HuggingFace のモデルカード（Qwen 自身が書いたもの）と、
    同リポジトリが公開しているファイル一覧。ファイル合計はこの記事で足した値。
    """
    left_rows = [
        ("ファイルの合計", "約4.9TB（4,892GB）"),
        ("パラメータ数", "2.4T（うち95Bが動く）"),
        ("ライセンス", "Qwen3.8-Max License"),
        ("画像・動画", "読めない（文章だけ）"),
        ("思考モード", "常にオン。切れない"),
        ("一度に読める量", "262,144（最大101万）"),
    ]
    right_rows = [
        ("ファイルの合計", "約55.6GB"),
        ("パラメータ数", "27B"),
        ("ライセンス", "Apache-2.0"),
        ("画像・動画", "読める"),
        ("思考モード", "切り替えられる"),
        ("一度に読める量", "262,144（最大100万）"),
    ]
    box_x = (18, 366)
    box_w = 336
    box_top = 84
    head_h = 30
    row_top = box_top + head_h + 22
    pitch = 38
    box_h = head_h + 22 + len(left_rows) * pitch + 4
    height = box_top + box_h + 62

    assert box_x[1] + box_w + 18 <= WIDTH, box_x[1] + box_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ日に公開された2つは、名前が似ているだけで別物です</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "左＝最上位クラスの重み。右＝手元に置ける大きさの重み。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "どちらも Qwen 自身がモデルカードに書いている値です。</text>\n",
    ]
    for index, (rows, cls, name) in enumerate(
        ((left_rows, "box-quiet", "Qwen3.8-2.4T-A95B"), (right_rows, "box-accent", "Qwen3.8-27B"))
    ):
        bx = box_x[index]
        parts.append(
            f'<rect class="{cls}" x="{bx}" y="{box_top}" '
            f'width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-strong" x="{bx + 16}" y="{box_top + 24}">{_esc(name)}</text>\n'
        )
        for row_index, (label, value) in enumerate(rows):
            y = row_top + row_index * pitch
            parts.append(f'<text class="t-xs" x="{bx + 16}" y="{y}">{_esc(label)}</text>\n')
            parts.append(f'<text class="t" x="{bx + 16}" y="{y + 18}">{_esc(value)}</text>\n')

    notes = [
        "※ ファイルの合計は、HuggingFace が出しているファイル一覧をこの記事で足した値です。",
        "※ APIで使える Qwen3.8-Max は、左の重みをもとにした別仕様です（画像も読めます）。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 42 + note_index * 18}">{_esc(note)}</text>\n'
        )

    alt = (
        "同じ日に公開された Qwen3.8 の2つの重みを比べた図。"
        "左の Qwen3.8-2.4T-A95B はファイル合計が約4.9テラバイト（4,892ギガバイト）、"
        "パラメータ数は2.4兆でうち950億が動き、ライセンスは Qwen3.8-Max License、"
        "画像や動画は読めず文章だけ、思考モードは常にオンで切れない、"
        "一度に読める量は262,144トークンで最大101万トークン。"
        "右の Qwen3.8-27B はファイル合計が約55.6ギガバイト、パラメータ数は270億、"
        "ライセンスは Apache-2.0、画像や動画を読める、思考モードは切り替えられる、"
        "一度に読める量は262,144トークンで最大100万トークン。"
        "ファイルの合計はファイル一覧を記事側で足した値。"
    )
    (OUT / "qwen38-two-weights.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def qwen38_vs_37_chart() -> None:
    """前の世代 Qwen3.7-Max と Qwen3.8-Max の点数（0〜100で出ているものだけ）。"""
    rows = [
        ("DeepSWE 1.1", 21.6, 56.6),
        ("PaperBench", 64.8, 93.0),
        ("Terminal Bench 2.1", 74.5, 86.6),
        ("JobBench", 31.3, 53.4),
        ("SWE-bench Pro", 60.6, 67.7),
        ("IFBench", 79.1, 82.8),
        ("HLE", 41.4, 43.6),
    ]
    left, right = 250, 610
    span = right - left
    top, bar_h, bar_gap, group_gap = 82, 14, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    scale = span / 100.0

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "前の世代との比較。数字が出ている30項目すべてで上がっています</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "灰色＝Qwen3.7-Max、青＝Qwen3.8-Max。目盛りは0〜100で揃えてあります。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "上がり幅の大きい順に7項目を抜き出しました。下がった項目は1つもありません。</text>\n",
    ]
    for index, (name, old, new) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((old, "bar-old", "3.7"), (new, "bar-new", "3.8"))
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
                f"{value:g}</text>\n"
            )

    height = top + len(rows) * group_h + 50
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ モデルカードには単位の記載がありません。数字はそのまま写しています。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ テストの中身も測り方も別々です。並べても平均は取れません。</text>\n"
    )
    alt = (
        "前の世代 Qwen3.7-Max と Qwen3.8-Max の点数を比べた横棒グラフ。"
        "DeepSWE 1.1 は21.6から56.6、PaperBench は64.8から93.0、"
        "Terminal Bench 2.1 は74.5から86.6、JobBench は31.3から53.4、"
        "SWE-bench Pro は60.6から67.7、IFBench は79.1から82.8、"
        "HLE は41.4から43.6へ上がった。"
        "モデルカードで数字が出ている30項目すべてで上がっており、下がった項目は1つもない。"
        "モデルカードには単位の記載がなく、テストの中身も測り方も別々のため平均は取れない。"
    )
    (OUT / "qwen38-vs-37.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def qwen38_not_first_chart() -> None:
    """Qwen 自身の比較表の中で、Qwen3.8-Max が一番ではなかった項目。"""
    total, won = 30, 7
    losses = [
        ("SWE-bench Pro", "67.7", "Claude Fable 5　80.0"),
        ("DeepSWE 1.1", "56.6", "GPT-5.6 Sol　73.0"),
        ("FrontierSWE", "73.5", "Claude Fable 5　88.8"),
        ("HLE", "43.6", "Claude Fable 5　53.3"),
        ("GPQA Diamond", "92.6", "GPT-5.6 Sol　94.1"),
    ]
    bar_left, bar_right, bar_y, bar_h = 18, 702, 86, 26
    cell_gap = 3
    cell_w = (bar_right - bar_left + cell_gap) / total - cell_gap

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "Qwen 自身の表で、Qwen3.8-Max が一番だったのは30項目中7項目</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "Qwen がモデルカードに載せた比較表を、この記事で1行ずつ数えたものです。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "青＝最高値だった項目、灰色＝他社のほうが上だった項目。</text>\n",
    ]
    for index in range(total):
        x = bar_left + index * (cell_w + cell_gap)
        cls = "bar-new" if index < won else "bar-old"
        parts.append(
            f'<rect class="{cls}" x="{x:.1f}" y="{bar_y}" '
            f'width="{cell_w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
    parts.append(f'<text class="t-accent" x="18" y="{bar_y + bar_h + 20}">7項目で最高</text>\n')
    parts.append(
        f'<text class="t-sm" x="150" y="{bar_y + bar_h + 20}">'
        "23項目は、他社のほうが上でした</text>\n"
    )

    head_y = bar_y + bar_h + 58
    col1, col2, col3 = 18, 270, 396
    parts.append(f'<text class="t-xs" x="{col1}" y="{head_y}">項目</text>\n')
    parts.append(f'<text class="t-xs" x="{col2}" y="{head_y}">Qwen3.8-Max</text>\n')
    parts.append(f'<text class="t-xs" x="{col3}" y="{head_y}">それより上だったモデル</text>\n')
    for row_index, (name, mine, better) in enumerate(losses):
        y = head_y + 24 + row_index * 22
        parts.append(f'<text class="t" x="{col1}" y="{y}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t" x="{col2}" y="{y}">{_esc(mine)}</text>\n')
        parts.append(f'<text class="t-bad" x="{col3}" y="{y}">{_esc(better)}</text>\n')

    height = head_y + 24 + len(losses) * 22 + 48
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 30}">'
        "※ 数字が5モデルぶん揃っていない項目は、勝ち負けの数に入れていません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 表を作ったのは Qwen です。相手の会社が同じ条件で測った値ではありません。</text>\n"
    )
    alt = (
        "Qwen がモデルカードに載せた比較表で、Qwen3.8-Max が最高値だった項目の数を示した図。"
        "30項目のうち7項目で最高、残り23項目は他社のほうが上だった。"
        "上だった例として、SWE-bench Pro は Qwen3.8-Max の67.7に対し Claude Fable 5 が80.0、"
        "DeepSWE 1.1 は56.6に対し GPT-5.6 Sol が73.0、"
        "FrontierSWE は73.5に対し Claude Fable 5 が88.8、"
        "HLE は43.6に対し Claude Fable 5 が53.3、"
        "GPQA Diamond は92.6に対し GPT-5.6 Sol が94.1。"
        "表を作ったのは Qwen であり、相手の会社が同じ条件で測った値ではない。"
    )
    (OUT / "qwen38-not-first.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def qwen38_price_region_chart() -> None:
    """Qwen3.8-Max の単価は地域で違う（元建て・100万トークンあたり）。"""
    rows = [
        ("北京", 12.0, 36.0),
        ("東京", 12.0, 36.0),
        ("フランクフルト", 12.0, 36.0),
        ("バージニア", 12.0, 36.0),
        ("シンガポール", 14.988, 44.965),
    ]
    left, right = 210, 600
    span = right - left
    top, bar_h, bar_gap, group_gap = 66, 15, 5, 20
    group_h = bar_h * 2 + bar_gap + group_gap
    biggest = max(max(a, b) for _, a, b in rows)
    scale = span / biggest

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "Qwen3.8-Max の単価は、置いてある場所で違います</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "入力＝薄い色 ／ 出力＝濃い色。100万トークンあたりの元（ドルではありません）。</text>\n",
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
                f"{value:g}元</text>\n"
            )

    height = top + len(rows) * group_h + 68
    notes = [
        "※ シンガポールだけ表の「服务部署范围」が国际で、ほかの4か所は全球と書かれています。",
        "※ 前の世代 qwen3.7-max は、同じ表で原価12元に「限时5折」が付いています。",
        "※ 元とドルは、出典のどこにも換算レートが書かれていないので換算していません。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 48 + note_index * 18}">{_esc(note)}</text>\n'
        )
    alt = (
        "Qwen3.8-Max の単価を置いてある場所ごとに比べた横棒グラフ。"
        "100万トークンあたりの元。北京・東京・フランクフルト・バージニアはいずれも"
        "入力12元・出力36元、シンガポールだけ入力14.988元・出力44.965元。"
        "シンガポールの行だけ服务部署范围が国际で、ほかの4か所は全球と書かれている。"
        "前の世代の qwen3.7-max は同じ表で原価12元に限时5折が付いている。"
        "元とドルの換算レートは出典に書かれていないため換算していない。"
    )
    (OUT / "qwen38-price-region.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def delivery_note_claim_vs_flag_chart() -> None:
    """納品の連絡文で、検品の結果と、送る文面に入った断定が食い違うことを頼み方6通りで並べる。

    実測（2026-08-20・架空の発注書8条件と、5条件しか満たしていない架空の原稿を2組。
    1つの頼み方につき材料2本×各2回＝4回、全28回）。値は check.py の出力。
    左＝送る文面の中に入った「事実と違う充足の断定」の件数（真値は0でないと使えない）。
    右＝返りのどこかで「満たしていない」と名指しした件数（多いほうがよい）。
    分母はどちらも「満たしていない3条件 × 4回 ＝ 12」。
    """
    rows = [
        ("そのまま「納品の連絡メールを書いて」", 8, 9),
        ("同じ指示文を、もう4回", 7, 10),
        ("同じ指示文で、原稿だけ貼らない", 4, 0),
        ("＋「条件ごとの一覧を添えて」", 2, 12),
        ("＋確かめた項目だけ書く（受け皿つき）", 0, 11),
        ("保存版＝【本文】と【確認欄】を分ける", 0, 7),
    ]
    label_x, label_w = 18, 322
    col_x = [label_x + label_w + 78, label_x + label_w + 258]
    col_names = [
        ["送る文面に入った", "事実と違う断定"],
        ["返りのどこかで", "違反を名指し"],
    ]
    row_h = 34
    top = 128

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "検品は効く。それでも、送る文面のほうには「満たしています」と書かれる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の発注書8条件と、そのうち5条件しか満たしていない架空の原稿を2組"
        "（記事執筆・商品ページ）作って通した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "満たしていない3条件は、どちらの材料でも字数の下限割れ・禁止語1回・"
        "指定キーワードの回数不足。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "1つの頼み方につき、材料2本 × 各2回 ＝ 4回。分母はどちらも 3条件 × 4回 ＝ 12。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "※ 3行目は対照＝原稿を貼らない回。見ていないので名指しは0件だが、断定のほうは入る。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 26 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, claimed, flagged in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        # 左＝事故。0 なら緑、1件でもあれば赤
        box = "box-good" if claimed == 0 else "box-bad"
        mcls = "t-good" if claimed == 0 else "t-bad"
        parts.append(
            f'<rect class="{box}" x="{col_x[0] - 37}" y="{ty - 14}" '
            f'width="74" height="19" rx="4"/>\n'
        )
        parts.append(
            f'<text class="{mcls}" x="{col_x[0]}" y="{ty}" '
            f'text-anchor="middle">{claimed} / 12</text>\n'
        )
        # 右＝見つけた数。事故ではないので色を付けない
        parts.append(
            f'<rect class="box-quiet" x="{col_x[1] - 37}" y="{ty - 14}" '
            f'width="74" height="19" rx="4"/>\n'
        )
        parts.append(
            f'<text class="t" x="{col_x[1]}" y="{ty}" '
            f'text-anchor="middle">{flagged} / 12</text>\n'
        )
        y += row_h

    notes = [
        ("t-bad", "※ 同じ返りの中で起きる。上の1行目と2行目は同じ指示文で、合わせて8回。"),
        ("t-bad", "　 自分で「満たしていません」と書いた条件を、文面では「満たしています」と書いた件数が11件。"),
        ("t-bad", "※ 字数について「満たした」と書いた4件は、4件とも数字が空欄のままだった。"),
        ("t-bad", "　 「〇〇〇〇字（1,900〜2,200字の範囲内）」＝穴が空くのは数字だけで、判定のほうは埋まっている。"),
        ("t-good", "※ 下の2行は、指摘を減らさずに断定だけを0にした。受け皿と、様式で分けた版。"),
        ("t-xs", "架空データでの実測（全28回）。生の返りと判定コードは docs/evidence/ に全文置いてある。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "納品の連絡メールをAIに作らせたときの結果を、頼み方6通りで並べた表。"
        "架空の発注書8条件と、そのうち5条件しか満たしていない架空の原稿を2組作り、"
        "1つの頼み方につき材料2本かける各2回で4回ずつ通した。"
        "満たしていない3条件は、どちらの材料でも字数の下限割れ、禁止語が1回出る、"
        "指定キーワードの回数不足の3つ。"
        "左の列は、相手に送る文面の中に入ってしまった事実と違う充足の断定の件数で、"
        "分母は3条件かける4回の12。右の列は、返りのどこかで違反を名指しした件数で、同じく分母は12。"
        "そのまま納品の連絡メールを書いてと頼んだ4回は、断定が12件中8件、名指しが12件中9件。"
        "同じ指示文をもう4回通した結果は、断定が7件、名指しが10件。"
        "同じ指示文で原稿だけ貼らなかった対照の4回は、断定が4件、名指しは0件。"
        "条件ごとの一覧を添えてと足した4回は、断定が2件、名指しは12件すべて。"
        "確かめた項目だけ書き、残りを受け皿に残させた4回は、断定が0件、名指しが11件。"
        "本文と確認欄を分ける保存版の4回は、断定が0件、名指しが7件。"
        "つまり検品そのものは効いていて、崩れるのは送る文面のほうだけだった。"
        "字数について満たしたと書いた4件は、4件とも数字が空欄のままで、"
        "そのうしろの範囲内という判定だけが埋まっていた。"
    )
    (OUT / "delivery-note-claim-vs-flag.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def conditions_changed_what_survives_chart() -> None:
    """途中で条件を取り消して差し替えたあと、何が残り、何が増えるかを版4通りで並べる。

    実測（2026-08-20・架空の発注書8条件を2本。1往復目に作業計画→2往復目に3件を差し替え→
    条件に触れない依頼を3往復→もう一度作らせる。4版×材料2本×各2回＝16会話・76ターン）。
    左＝取り消した3件が「いま使う値」として残った項目数（真値0）。分母は3項目×4回＝12。
    中＝新しい値が入った項目数。右＝材料に1文字も無い金額の話が、依頼つきで出た行数（4回合計）。
    """
    rows = [
        ("変更をそのまま伝えて作り直させる", 0, 12, 9),
        ("＋「古い条件は使わないでください」", 0, 12, 5),
        ("＋作り直す前に、いまの条件を書き出させる", 0, 12, 0),
        ("新しい会話に、書き換えた条件表を貼り直す", 0, 12, 0),
    ]
    label_x, label_w = 18, 330
    col_x = [label_x + label_w + 58, label_x + label_w + 180, label_x + label_w + 302]
    col_names = [
        ["取り消した値が", "残った"],
        ["新しい値が", "入った"],
        ["頼んでいない", "金額の話"],
    ]
    row_h = 36
    top = 128

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "取り消した数字は残らない。残るのは「変更があった」という出来事のほう</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の発注書8条件を2本作り、作業計画を出させたあと、"
        "2往復目で3件（分量・納期・修正回数）を取り消して差し替えた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "そのあと条件に一切触れない依頼を3往復はさんでから、もう一度おなじ作業計画を作らせている。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "1つの版につき、材料2本 × 各2回 ＝ 4会話。左と中の分母は 3項目 × 4回 ＝ 12。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "※ 材料には金額・単価・報酬の記載が1文字もない（走らせる前にコードで確認）。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 26 + i * 13}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, old, new, money in rows:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        cells = [
            ("box-good" if old == 0 else "box-bad",
             "t-good" if old == 0 else "t-bad", f"{old} / 12"),
            ("box-good", "t-good", f"{new} / 12"),
            ("box-good" if money == 0 else "box-bad",
             "t-good" if money == 0 else "t-bad", f"{money} 行"),
        ]
        for cx, (box, mcls, text) in zip(col_x, cells):
            parts.append(
                f'<rect class="{box}" x="{cx - 37}" y="{ty - 14}" '
                f'width="74" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{mcls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{_esc(text)}</text>\n'
            )
        y += row_h

    notes = [
        ("t-good", "※ 左は16会話・48項目とも0。変更の直後でも0/36。触っていない5条件も79/80そのまま残った。"),
        ("t-bad", "※ 右は「金額の語」と「決めてください・ご提示ください」が同じ行にある数。材料に金額は無い。"),
        ("t-bad", "　 1行目には「条件変更を受け入れた直後は、交渉がいちばん通りやすいタイミングです」まで入る。"),
        ("t-good", "※ 会話を新しくすると0行。値のためではなく、変更というできごとを持ち越さないために効く。"),
        ("t-xs", "架空データでの実測（16会話・のべ76ターン）。生の返りと判定コードは docs/evidence/ に全文置いてある。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "副業案件の条件を会話の途中で取り消して差し替えたあと、何が残り何が増えるかを、"
        "頼み方4通りで並べた表。架空の発注書8条件を2本作り、まず作業計画を出させ、"
        "2往復目で分量・納期・修正回数の3件を取り消して新しい値に差し替え、"
        "そのあと条件に一切触れない依頼を3往復はさんでから、もう一度おなじ作業計画を作らせた。"
        "1つの版につき材料2本かける各2回で4会話ずつ。"
        "左の列は、取り消した3件が今使う値として成果物に残った項目数で、分母は3項目かける4回の12。"
        "中の列は、新しい値が入った項目数。右の列は、材料に1文字も書かれていない金額の話が、"
        "決めてくださいという依頼つきで出た行の数で、4会話の合計。"
        "変更をそのまま伝えて作り直させた版は、取り消した値が0、新しい値が12、金額の話が9行。"
        "古い条件は使わないでくださいと足した版は、0と12と5行。"
        "作り直す前に今の条件を書き出させた版は、0と12と0行。"
        "新しい会話に書き換えた条件表を貼り直した版は、0と12と0行。"
        "つまり、取り消した数字が残る事故は4版とも一度も起きず、"
        "版によって変わったのは、頼んでいない金額の話が付くかどうかだけだった。"
    )
    (OUT / "conditions-changed-what-survives.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def pfp9_arena_rank_chart() -> None:
    """MLIP Arena の総合ランキング（合計点は小さいほど上位）。

    出典＝Preferred Networks の技術ブログ「PFP v9のご紹介」の表1。
    PFP v9 以外の値は 2026-03-01 時点の公開リーダーボードに基づく、と同ページに明記。
    """
    rows = [
        ("PFP v9", 12, True),
        ("MACE-MPA", 12, True),
        ("MatterSim", 19, False),
        ("MACE-MP(M)", 24, False),
        ("CHGNet", 29, False),
        ("ORB v2", 33, False),
        ("SevenNet", 35, False),
        ("M3GNet", 36, False),
    ]
    left, right = 210, 620
    span = right - left
    top, bar_h, pitch = 100, 20, 30
    worst = max(value for _, value, _ in rows)
    scale = span / worst

    assert right + 60 <= WIDTH, right

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "MLIP Arena の総合ランキング。PFP v9 は MACE-MPA と同率1位です</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "棒は5種目の順位を足した合計点。短いほど上位です（1位＝12点）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "PFP v9 以外の値は、2026年3月1日時点の公開リーダーボードにもとづくと"
        "発表ページに書かれています。</text>\n",
    ]
    for index, (name, value, top_two) in enumerate(rows):
        y = top + index * pitch
        cls = "t-strong" if top_two else "t"
        parts.append(f'<text class="{cls}" x="18" y="{y + bar_h - 4}">{_esc(name)}</text>\n')
        bar_w = max(2.0, value * scale)
        parts.append(
            f'<rect class="{"bar-new" if top_two else "bar-old"}" x="{left}" y="{y}" '
            f'width="{bar_w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + bar_w + 8:.1f}" y="{y + bar_h - 4}">'
            f"{value}点</text>\n"
        )

    height = top + len(rows) * pitch + 62
    notes = [
        "※ 5種目＝二原子分子・状態方程式・エネルギーと体積・安定性・燃焼。",
        "※ 同じ表に「wbm_ev の1位は eSEN」という注記が付いています。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 42 + note_index * 19}">{_esc(note)}</text>\n'
        )

    alt = (
        "MLIP Arena の総合ランキングを示した横棒グラフ。"
        "棒は5種目の順位を足した合計点で、短いほど上位。"
        "PFP v9 が12点、MACE-MPA も12点で同率1位。"
        "以下 MatterSim が19点、MACE-MP(M) が24点、CHGNet が29点、ORB v2 が33点、"
        "SevenNet が35点、M3GNet が36点。"
        "PFP v9 以外の値は2026年3月1日時点の公開リーダーボードにもとづくと発表ページに書かれている。"
        "5種目は二原子分子・状態方程式・エネルギーと体積・安定性・燃焼で、"
        "同じ表にはエネルギーと体積の1位は eSEN という注記が付いている。"
    )
    (OUT / "pfp9-arena-rank.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def pfp9_five_tasks_chart() -> None:
    """5種目それぞれの順位。PFP v9 と MACE-MPA を並べる。

    出典＝Preferred Networks の技術ブログ「PFP v9のご紹介」の表1。
    """
    tasks = [
        ("二原子分子のなめらかさ", "diatomics", 1, 2),
        ("状態方程式", "eos_bulk", 1, 2),
        ("エネルギーと体積", "wbm_ev", 5, 2),
        ("高温・圧縮での安定性", "stability", 1, 4),
        ("水素の燃焼", "combustion", 4, 2),
    ]
    label_x = 18
    col_x = [400, 560]
    col_w = 130
    head_y = 96
    top = 126
    pitch = 44
    cell_h = 32

    assert col_x[1] + col_w + 18 <= WIDTH, col_x[1] + col_w

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同率1位でも、種目ごとに見ると3種目が1位・2種目は4位と5位です</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "数字は種目ごとの順位。緑＝その種目で1位、灰色＝2位以下。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "合計点はどちらも12点で並びますが、点の取り方はまったく違います。</text>\n",
    ]
    for index, name in enumerate(("PFP v9", "MACE-MPA")):
        parts.append(
            f'<text class="t-accent" x="{col_x[index] + 10}" y="{head_y}">{_esc(name)}</text>\n'
        )

    for row_index, (label, code, mine, theirs) in enumerate(tasks):
        y = top + row_index * pitch
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + 14}">{_esc(label)}</text>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{label_x}" y="{y + 30}">{_esc(code)}</text>\n'
        )
        for col_index, rank in enumerate((mine, theirs)):
            cls = "box-good" if rank == 1 else "box-quiet"
            text_cls = "t-good" if rank == 1 else "t-sm"
            parts.append(
                f'<rect class="{cls}" x="{col_x[col_index]}" y="{y - 4}" '
                f'width="{col_w}" height="{cell_h}" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{text_cls}" x="{col_x[col_index] + 52}" y="{y + 17}">'
                f"{rank}位</text>\n"
            )

    height = top + len(tasks) * pitch + 60
    notes = [
        "※ 燃焼の値は、5回走らせた平均だと発表ページに書かれています。",
        "※ 5種目の中身も測り方も別々です。順位を足した合計点に、精度の意味はありません。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 42 + note_index * 19}">{_esc(note)}</text>\n'
        )

    alt = (
        "MLIP Arena の5種目それぞれの順位を、PFP v9 と MACE-MPA で並べた表。"
        "二原子分子のなめらかさ（diatomics）は PFP v9 が1位、MACE-MPA が2位。"
        "状態方程式（eos_bulk）も PFP v9 が1位、MACE-MPA が2位。"
        "エネルギーと体積（wbm_ev）は PFP v9 が5位、MACE-MPA が2位。"
        "高温・圧縮での安定性（stability）は PFP v9 が1位、MACE-MPA が4位。"
        "水素の燃焼（combustion）は PFP v9 が4位、MACE-MPA が2位。"
        "合計点はどちらも12点で同率1位だが、点の取り方はまったく違う。"
        "燃焼の値は5回走らせた平均だと発表ページに書かれている。"
        "5種目は中身も測り方も別々なので、順位を足した合計点に精度の意味はない。"
    )
    (OUT / "pfp9-five-tasks.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def pfp9_h2_rmse_chart() -> None:
    """水素燃焼19素反応の反応熱の誤差（RMSE・kcal/mol・小さいほど正確）。

    出典＝Preferred Networks の技術ブログ「PFP v9のMLIP Arenaベンチマーク評価(詳細版)」。
    """
    rows = [
        ("PFP v9（r2SCAN モード）", 3.10, "bar-new"),
        ("PFP v9（PBE モード）", 7.88, "bar-in"),
        ("MACE-MPA-0", 11.15, "bar-old"),
    ]
    left, right = 260, 600
    span = right - left
    top, bar_h, pitch = 108, 26, 46
    worst = max(value for _, value, _ in rows)
    scale = span / worst

    assert right + 90 <= WIDTH, right

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "水素が燃える19本の反応。予測した熱と実験値のずれ（小さいほど正確）</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "単位は kcal/mol。この数え方は、走らせるたびに結果が変わらないと"
        "発表ページが説明しています。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "実験値は、比較相手 MACE-MPA の論文の図から読み取ったものだと"
        "同じページに書かれています。</text>\n",
    ]
    for index, (name, value, cls) in enumerate(rows):
        y = top + index * pitch
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 7}">{_esc(name)}</text>\n')
        bar_w = max(2.0, value * scale)
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" '
            f'width="{bar_w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + bar_w + 10:.1f}" y="{y + bar_h - 7}">'
            f"{value:.2f}</text>\n"
        )

    height = top + len(rows) * pitch + 62
    notes = [
        "※ MLIP Arena の順位づけには、この数え方は入っていません。別に足した確認です。",
        "※ 発表ページは「r2SCAN は PBE に対して誤差を56%低減」と書いています。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 42 + note_index * 19}">{_esc(note)}</text>\n'
        )

    alt = (
        "水素が燃える19本の素反応について、予測した反応熱と実験値のずれを比べた横棒グラフ。"
        "単位は kcal/mol で、短いほど正確。"
        "PFP v9 の r2SCAN モードが3.10、PFP v9 の PBE モードが7.88、MACE-MPA-0 が11.15。"
        "この数え方は走らせるたびに結果が変わらないと発表ページが説明しており、"
        "実験値は比較相手 MACE-MPA の論文の図から読み取ったものだと同じページに書かれている。"
        "MLIP Arena の順位づけには、この数え方は入っていない。"
        "発表ページは r2SCAN は PBE に対して誤差を56パーセント低減と書いている。"
    )
    (OUT / "pfp9-h2-rmse.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def pfp9_elements_chart() -> None:
    """r2SCAN モードで扱える元素の数が 70 から 96 へ増えた、という図。

    出典＝Preferred Networks の技術ブログ「PFP v9のご紹介」。
    """
    bars = [("PFP v8", 70, "bar-old"), ("PFP v9", 96, "bar-new")]
    left, right = 190, 600
    span = right - left
    top, bar_h, pitch = 96, 30, 48
    scale = span / 96.0

    box_top = top + len(bars) * pitch + 14
    box_h = 96
    height = box_top + box_h + 54

    assert right + 70 <= WIDTH, right

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "実験値に近づける計算モードで扱える元素が、70種類から96種類になりました</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "水素（H）からキュリウム（Cm）まで。増えたのはランタノイドとアクチノイドの系列です。</text>\n",
    ]
    for index, (name, value, cls) in enumerate(bars):
        y = top + index * pitch
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 9}">{_esc(name)}</text>\n')
        bar_w = value * scale
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" '
            f'width="{bar_w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + bar_w + 10:.1f}" y="{y + bar_h - 9}">'
            f"{value}種類</text>\n"
        )

    parts.append(
        f'<rect class="box-accent" x="18" y="{box_top}" '
        f'width="{WIDTH - 36}" height="{box_h}" rx="6"/>\n'
    )
    box_lines = [
        ("t-strong", "学習データに新しく入ったもの"),
        ("t", "表面構造・吸着構造・クラスター・金属錯体"),
        ("t-sm", "触媒・電池材料・合金・多孔性材料で頻繁に出てくる形だと発表ページは説明しています。"),
    ]
    for line_index, (css, text) in enumerate(box_lines):
        parts.append(
            f'<text class="{css}" x="36" y="{box_top + 28 + line_index * 24}">{_esc(text)}</text>\n'
        )

    parts.append(
        f'<text class="t-xs" x="18" y="{height - 24}">'
        "※ もう一方の計算モード（PBE）で扱える元素の数は、この発表ページには書かれていません。</text>\n"
    )

    alt = (
        "実験値に近づける r2SCAN 計算モードで扱える元素の数を比べた横棒グラフ。"
        "PFP v8 が70種類、PFP v9 が96種類で、水素（H）からキュリウム（Cm）まで。"
        "増えたのはランタノイドとアクチノイドの系列。"
        "また学習データには表面構造・吸着構造・クラスター・金属錯体が新しく入っており、"
        "触媒・電池材料・合金・多孔性材料で頻繁に出てくる形だと発表ページは説明している。"
        "もう一方の計算モードである PBE で扱える元素の数は、この発表ページには書かれていない。"
    )
    (OUT / "pfp9-elements.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def daybreak_bedrock_vs_direct_chart() -> None:
    """同じモデルの単価を、OpenAI と直接／AWS 経由（Amazon Bedrock）で並べる。

    出典＝OpenAI の料金ページ（Cyber models の表）と、
    Amazon Bedrock のモデルカード2枚（In-Region・Standard・100万トークンあたり）。
    倍率はこの記事が割り算した値。
    """
    rows = [
        ("Daybreak Red の入力", 12.50, 13.75),
        ("Daybreak Red の出力", 75.00, 82.50),
        ("Daybreak Blue の入力", 4.00, 5.50),
        ("Daybreak Blue の出力", 20.00, 33.00),
    ]
    left, right = 262, 606
    span = right - left
    top, bar_h, bar_gap, group_gap = 96, 15, 5, 22
    group_h = bar_h * 2 + bar_gap + group_gap
    scale = span / max(max(a, b) for _, a, b in rows)

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じモデルでも、AWS 経由のほうが高くなっています</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "灰色＝OpenAI と直接契約したとき ／ 青＝Amazon Bedrock 経由のとき。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "100万トークンあたりのドル。どちらも標準（Standard）の値です。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "Red は短い入力だけ、Blue も短い入力（27.2万トークンまで）の行で揃えています。</text>\n",
    ]
    for index, (name, direct, aws) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((direct, "bar-old", "直接"), (aws, "bar-new", "AWS"))
        ):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(f'<text class="t-xs" x="228" y="{by + bar_h - 4}">{tag}</text>\n')
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"${value:.2f}</text>\n"
            )

    height = top + len(rows) * group_h + 66
    notes = [
        "※ Red は 1.1倍。Blue は入力が 1.375倍・出力が 1.65倍。倍率はこの記事の割り算です。",
        "※ OpenAI の料金ページには「Sol の割引価格は少なくとも2026年11月21日まで」とあります。",
        "※ 上げ幅がなぜ揃っていないのかは、どちらのページにも書かれていません。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 54 + note_index * 18}">{_esc(note)}</text>\n'
        )
    alt = (
        "OpenAI と直接契約したときと Amazon Bedrock 経由のときで、"
        "同じモデルの単価を比べた横棒グラフ。100万トークンあたりのドル。"
        "Daybreak Red の入力は直接12.50ドルに対し AWS 経由が13.75ドル、"
        "出力は直接75.00ドルに対し AWS 経由が82.50ドル。"
        "Daybreak Blue の入力は直接4.00ドルに対し AWS 経由が5.50ドル、"
        "出力は直接20.00ドルに対し AWS 経由が33.00ドル。"
        "Red は 1.1倍だが、Blue は入力が 1.375倍・出力が 1.65倍で、上げ幅が揃っていない。"
        "倍率は記事側の割り算で、上げ幅が揃わない理由はどちらのページにも書かれていない。"
    )
    (OUT / "daybreak-bedrock-vs-direct.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def daybreak_blue_same_price_chart() -> None:
    """Bedrock 上で、安全装置つきの Blue と汎用の Sol が同額であることを示す。

    出典＝Amazon Bedrock のモデルカード2枚。
    In-Region・Standard・短い文脈（27.2万トークン）・100万トークンあたりのドル。
    """
    rows = [
        ("汎用の Sol（Global 経路）", 5.00, 30.00),
        ("汎用の Sol（同一リージョン）", 5.50, 33.00),
        ("Daybreak Blue（同一のみ）", 5.50, 33.00),
    ]
    left, right = 262, 600
    span = right - left
    top, bar_h, bar_gap, group_gap = 96, 15, 5, 22
    group_h = bar_h * 2 + bar_gap + group_gap
    scale = span / max(max(a, b) for _, a, b in rows)

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "安全装置がついても、値段は汎用モデルと同じです</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "薄い青＝入力 ／ 濃い青＝出力。100万トークンあたりのドル。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "どれも Amazon Bedrock のモデルカードに載っている標準（Standard）の値です。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "ただし Daybreak Blue は、一番安い Global 経路を選べません。</text>\n",
    ]
    for index, (name, price_in, price_out) in enumerate(rows):
        y = top + index * group_h
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(name)}</text>\n')
        for offset, (value, cls, tag) in enumerate(
            ((price_in, "bar-in", "入力"), (price_out, "bar-out", "出力"))
        ):
            by = y + offset * (bar_h + bar_gap)
            bw = max(2.0, value * scale)
            parts.append(f'<text class="t-xs" x="228" y="{by + bar_h - 4}">{tag}</text>\n')
            parts.append(
                f'<rect class="{cls}" x="{left}" y="{by}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="2"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{by + bar_h - 3}">'
                f"${value:.2f}</text>\n"
            )

    height = top + len(rows) * group_h + 66
    notes = [
        "※ 汎用の Sol は Global 経路なら $5.00 / $30.00。Daybreak は「Not supported」です。",
        "※ つまり同じ中身でも、Daybreak 側は一番安い選び方が最初から消えています。",
        "※ 長い文脈（100万トークン）の行は Blue にだけあり、$11.00 / $49.50 です。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 54 + note_index * 18}">{_esc(note)}</text>\n'
        )
    alt = (
        "Amazon Bedrock 上での単価を比べた横棒グラフ。100万トークンあたりのドル。"
        "汎用の GPT-5.6 Sol は Global 経路なら入力5.00ドル・出力30.00ドル、"
        "同じリージョン内で処理する経路なら入力5.50ドル・出力33.00ドル。"
        "安全装置つきの Daybreak Blue も入力5.50ドル・出力33.00ドルで、汎用と同額。"
        "ただし Daybreak Blue は Geo 経路も Global 経路も Not supported と書かれており、"
        "一番安い Global 経路を選べない。"
        "長い文脈（100万トークン）の行は Blue にだけあり、入力11.00ドル・出力49.50ドル。"
    )
    (OUT / "daybreak-blue-same-price.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def daybreak_what_is_closed_chart() -> None:
    """審査・リージョン・層・微調整で、選べる幅がどれだけ狭いかを並べる。

    出典＝Amazon Bedrock のモデルカード3枚（汎用 Sol・Daybreak Blue・Daybreak Red）。
    """
    positive = {"要らない", "表にある", "使える", "米欧亜に多数"}
    negative = {"要る", "表にない", "使えない", "できない", "オハイオだけ"}
    rows = [
        ("事前の審査", "要らない", "要る", "要る"),
        ("使えるリージョン", "米欧亜に多数", "オハイオだけ", "オハイオだけ"),
        ("東京リージョン", "表にある", "表にない", "表にない"),
        ("Geo・Global 経路", "使える", "使えない", "使えない"),
        ("速い層・安い層", "使えない", "使えない", "使えない"),
        ("微調整（Fine-tuning）", "記載なし", "できない", "できない"),
        ("一度に読める量", "100万", "100万", "27.2万"),
    ]
    col_label, col_a, col_b, col_c = 18, 292, 428, 566
    head_y = 106
    row_top = head_y + 28
    pitch = 26

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "値段より先に、選べる幅のほうが狭くなっています</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "Amazon Bedrock のモデルカード3枚に書かれていることを並べたものです。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "汎用＝GPT-5.6 Sol、Blue＝Daybreak Blue、Red＝Daybreak Red。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "「使えない」は、モデルカードに Not supported と書かれているという意味です。</text>\n",
        f'<text class="t-xs" x="{col_label}" y="{head_y}">見るところ</text>\n',
        f'<text class="t-xs" x="{col_a}" y="{head_y}">汎用の Sol</text>\n',
        f'<text class="t-xs" x="{col_b}" y="{head_y}">Blue</text>\n',
        f'<text class="t-xs" x="{col_c}" y="{head_y}">Red</text>\n',
    ]
    for index, (name, plain, blue, red) in enumerate(rows):
        y = row_top + index * pitch
        parts.append(f'<text class="t" x="{col_label}" y="{y}">{_esc(name)}</text>\n')
        for x, value in ((col_a, plain), (col_b, blue), (col_c, red)):
            cls = "t-bad" if value in negative else "t-good" if value in positive else "t"
            parts.append(f'<text class="{cls}" x="{x}" y="{y}">{_esc(value)}</text>\n')

    height = row_top + len(rows) * pitch + 60
    notes = [
        "※ 審査＝OpenAI の Trusted Access for Cyber への登録。承認後に AWS 側で申請します。",
        "※ 速い層（Priority）と安い層（Flex）は、汎用の Sol でも使えないと書かれています。",
    ]
    for note_index, note in enumerate(notes):
        parts.append(
            f'<text class="t-xs" x="18" y="{height - 40 + note_index * 18}">{_esc(note)}</text>\n'
        )
    alt = (
        "Amazon Bedrock のモデルカード3枚に書かれている条件を並べた表。"
        "汎用の GPT-5.6 Sol は事前の審査が要らず、米国・欧州・アジアの多数のリージョンの表があり、"
        "東京もその表にあり、Geo 経路と Global 経路が使えて、一度に100万トークン読める。"
        "Daybreak Blue と Daybreak Red はどちらも事前の審査が要り、"
        "リージョンの表は米国東部オハイオの1行だけで東京は無く、"
        "Geo 経路も Global 経路も使えず、微調整もできない。"
        "一度に読める量は Blue が100万トークン、Red は27.2万トークン。"
        "速い層（Priority）と安い層（Flex）は、汎用の Sol を含む3つとも使えないと書かれている。"
        "審査は OpenAI の Trusted Access for Cyber への登録で、"
        "承認後に AWS 側で申請する必要がある。"
    )
    (OUT / "daybreak-what-is-closed.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def daybreak_vendor_shapes_chart() -> None:
    """同じ「防御側にAIを渡す」話を、3社がどういう形で出しているか。

    出典＝AWS の発表ブログ、Anthropic の発表ページ、Google のモデル一覧。
    """
    cards = [
        (
            "box-accent",
            "OpenAI（AWS 経由）",
            "審査を通った相手だけに、専用のモデルを別料金で開く",
            "Daybreak Red は $13.75 / $82.50、Blue は $5.50 / $33.00",
            "2026年8月11日発表・オハイオのみ・Trusted Access for Cyber が必要",
        ),
        (
            "box-quiet",
            "Anthropic",
            "専用モデルではなく、Claude Code に組み込んだ機能として出す",
            "Claude Code Security。限定リサーチプレビュー",
            "2026年2月20日発表・Enterprise と Team 向け・別料金の記載なし",
        ),
        (
            "box-quiet",
            "Google",
            "Gemini API のモデル一覧に、専用モデルの掲載はありません",
            "同じ形の発表は、この記事を書いた時点では見つかっていません",
            "確認したのは ai.google.dev のモデル一覧ページだけです",
        ),
    ]
    box_x, box_w = 18, 684
    box_top = 86
    box_h = 96
    box_gap = 12

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ「防御側にAIを渡す」話でも、出し方が3社で違います</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "各社の公式ページに書かれていることだけを並べています。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "値段は100万トークンあたりのドル（Amazon Bedrock・同一リージョン・標準）。</text>\n",
    ]
    for index, (cls, name, line1, line2, line3) in enumerate(cards):
        by = box_top + index * (box_h + box_gap)
        parts.append(
            f'<rect class="{cls}" x="{box_x}" y="{by}" '
            f'width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(f'<text class="t-strong" x="{box_x + 16}" y="{by + 26}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t" x="{box_x + 16}" y="{by + 48}">{_esc(line1)}</text>\n')
        parts.append(f'<text class="t-sm" x="{box_x + 16}" y="{by + 68}">{_esc(line2)}</text>\n')
        parts.append(f'<text class="t-xs" x="{box_x + 16}" y="{by + 87}">{_esc(line3)}</text>\n')

    height = box_top + len(cards) * (box_h + box_gap) + 44
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 26}">'
        "※ 「見つかっていません」は、確かめたページに載っていなかったという意味です。</text>\n"
    )
    alt = (
        "同じサイバー防御向けの取り組みを、3社がどういう形で出しているかを並べた図。"
        "OpenAI は AWS 経由で、審査を通った相手だけに専用モデルを別料金で開いており、"
        "Amazon Bedrock の同一リージョンでの標準価格は100万トークンあたり"
        "Daybreak Red が入力13.75ドル・出力82.50ドル、"
        "Daybreak Blue が入力5.50ドル・出力33.00ドル。"
        "2026年8月11日発表で、米国東部オハイオのみ、Trusted Access for Cyber への登録が必要。"
        "Anthropic は専用モデルではなく Claude Code に組み込んだ機能 Claude Code Security として出しており、"
        "2026年2月20日発表の限定リサーチプレビューで、Enterprise と Team 向け、別料金の記載はない。"
        "Google は Gemini API のモデル一覧に専用モデルを載せておらず、"
        "同じ形の発表はこの記事を書いた時点では見つかっていない。"
    )
    (OUT / "daybreak-vendor-shapes.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_memo_length_vs_values_chart() -> None:
    """引き継ぎメモの字数と、メモに残った「翌日が要る値」の数を版ごとに並べる。

    実測（2026-08-21・架空の待ち行列10行を2本、4通りの頼み方 × 各2回 × 2本 ＝ 全16回）。
    値は check.py の B節・C節の出力。棒の長さは値から計算する。
    """
    rows = [
        ("そのまま「その旨を書いて」", 1004, 20),
        ("＋「何が起きたか・何を試したか・次に何を」", 1254, 21),
        ("＋「会話ではなくファイルにだけ書いて」", 1721, 21),
        ("＋「行・ファイル名・出た文言をそのままコピー」", 2316, 24),
    ]
    label_x = 18
    len_x = 330
    len_w = 150
    val_x = 512
    val_w = 150
    top = 148
    row_h = 56
    bar_h = 22
    max_len = 2400
    max_val = 24

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "メモは2.3倍に伸びた。翌日が要る値の数は、ほとんど動かない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の待ち行列10行を2本（調べもの／請求書の突き合わせ）。上から3行を毎朝処理させ、"
        "そのうち</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "2行が別々の理由で止まるように仕込んだ（資料が404／中身が別案件のもの）。"
        "止まった2行について</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "「行の名前・資料のファイル名・出た文言」の3つ＝計6個が、"
        "メモに一字一句そのまま残ったかを数えた。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "1つの頼み方につき、材料2本 × 各2回 ＝ 4回。全16回。</text>\n",
        f'<text class="t-xs" x="{len_x + len_w // 2}" y="{top - 36}" '
        f'text-anchor="middle">メモの字数</text>\n',
        f'<text class="t-xs" x="{len_x + len_w // 2}" y="{top - 22}" '
        f'text-anchor="middle">（4回の平均）</text>\n',
        f'<text class="t-xs" x="{val_x + val_w // 2}" y="{top - 36}" '
        f'text-anchor="middle">翌日が要る6個の値</text>\n',
        f'<text class="t-xs" x="{val_x + val_w // 2}" y="{top - 22}" '
        f'text-anchor="middle">（4回で24個中）</text>\n',
    ]

    y = top
    for label, n_len, n_val in rows:
        ty = y + 16
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w1 = round(len_w * n_len / max_len)
        parts.append(
            f'<rect class="bar-old" x="{len_x}" y="{ty - 15}" '
            f'width="{w1}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{len_x + w1 + 6}" y="{ty}">{n_len}字</text>\n'
        )
        w2 = round(val_w * n_val / max_val)
        cls = "bar-new" if n_val == max_val else "bar-in"
        parts.append(
            f'<rect class="{cls}" x="{val_x}" y="{ty - 15}" '
            f'width="{w2}" height="{bar_h}" rx="3"/>\n'
        )
        txt_cls = "t-good" if n_val == max_val else "t-sm"
        parts.append(
            f'<text class="{txt_cls}" x="{val_x + w2 + 6}" y="{ty}">{n_val}/24</text>\n'
        )
        y += row_h

    notes = [
        ("t-bad", "※ 上の3つは 20・21・21 でほとんど同じ。メモが1.7倍になっても、残る値は1個しか増えない。"),
        ("t-bad", "　 落ちるものは決まっている＝調べものでは品目コード KX-2200 が6回とも、"),
        ("t-bad", "　 請求書ではファイル名 seikyu-shinonome-06.txt が6回中4回。どちらも会社名や品名に言い換えられていた。"),
        ("t-good", "※ 4つ目（そのままコピーさせる）だけが 24/24。落ちた値は0個だった。"),
        ("t-xs", "架空データでの実測（全16回）。当て方を2通り（完全一致／ゆるい正規表現）試したが、"
                 "16回とも同じ数だった。"),
        ("t-xs", "生の返り16通は docs/evidence/memo-that-names-the-next-row.md に全文置いてある。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の自動処理が止まった日に書かせた引き継ぎメモについて、"
        "メモの字数と、翌日が必要とする値がメモに残った数を、頼み方4通りで並べた横棒グラフ。"
        "架空の待ち行列10行を2本作り、上から3行を処理させ、そのうち2行が別々の理由で止まるように仕込んだ。"
        "理由は、資料が404で取得できないことと、資料の中身が別案件のものだったこと。"
        "止まった2行について、行の名前、資料のファイル名、画面に出た文言の3つ、"
        "合わせて6個の文字列がメモに一字一句そのまま残ったかを数えた。"
        "1つの頼み方につき材料2本かける各2回で4回ずつ、全16回である。"
        "そのまま、その旨を書いてと頼んだ4回は、メモの平均が1004字で、値は24個中20個残った。"
        "何が起きたか、何を試したか、次に何をすれば直るかの3つを入れてと足した4回は、"
        "1254字で21個。"
        "さらに、次に読む人は会話を見られないので会話ではなくファイルにだけ書いてと足した4回は、"
        "1721字で21個。"
        "行の文字列とファイル名と出た文言をそのままコピーしてと足した4回は、2316字で24個全部が残った。"
        "つまりメモは2.3倍に伸びたのに、残る値は上の3つではほとんど動かない。"
        "落ちるものは決まっていて、調べものの材料では品目コード KX-2200 が6回とも落ち、"
        "請求書の材料ではファイル名 seikyu-shinonome-06.txt が6回中4回落ちた。"
        "どちらもメモの中では会社名や品名に言い換えられていた。"
        "4つ目のそのままコピーさせる頼み方だけが24個中24個で、落ちた値は0個だった。"
    )
    (OUT / "handoff-memo-length-vs-values.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_memo_next_row_chart() -> None:
    """メモだけを渡した翌日の会話が、次に手を付ける行を名指しできたかを版ごとに並べる。

    実測（2026-08-21・16通のメモをそれぞれ別のまっさらな会話に渡した）。
    値は check.py の E節・F節の出力。位置は計算で出す。
    """
    rows = [
        ("そのまま「その旨を書いて」", "2/4", "4/4"),
        ("＋「何が起きたか・何を試したか・次に何を」", "1/4", "4/4"),
        ("＋「会話ではなくファイルにだけ書いて」", "2/4", "4/4"),
        ("＋「次はこの行から: 」を1行書かせる", "3/4", "4/4"),
    ]
    label_x = 18
    col_x = [452, 606]
    col_names = [
        ["答えの書き出しで", "行を名指しした"],
        ["答えのどこかに", "行の番号は出ている"],
    ]
    top = 168
    row_h = 52

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "行の番号は16回とも書いてある。それでも半分は「決まらない」と答える</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "前の図と同じ16回で作らせたメモを、1通ずつ別のまっさらな会話に渡した"
        "（待ち行列も資料も渡していない）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "聞いたのは3つ。①止まっている行はどれか ②それぞれ次に何をすればよいか"
        "③まだ一度も手を付けて</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "いない行のうち、いちばん上はどれか。③は「メモから決まらないときは"
        "そう書いて」と添えてある。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "①の答えは16回とも正解だった（止まった2行を2行とも名指し）。"
        "下は③の結果。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 30 + i * 14}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, named, anywhere in rows:
        ty = y + 17
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        good = named == "3/4"
        for cx, val, box, cls, w in (
            (col_x[0], named, "box-good" if good else "box-bad",
             "t-good" if good else "t-bad", 52),
            (col_x[1], anywhere, "box-quiet", "t-sm", 52),
        ):
            parts.append(
                f'<rect class="{box}" x="{cx - w // 2}" y="{ty - 14}" '
                f'width="{w}" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{_esc(val)}</text>\n'
            )
        y += row_h

    notes = [
        ("t-bad", "※ 上の3つを合わせると 5/12。残る7回は「このメモからは決まらない」と答えた。"),
        ("t-bad", "　 ところが右の列のとおり、16回とも答えの中には行の番号が出てくる。"),
        ("t-bad", "　 断った理由は返り自身が書いている——「その行が本当に未着手かはメモに書かれていない」。"),
        ("t-good", "※ 「次はこの行から: 」を1行書かせた4回は、4回ともその1行を根拠に答えた。"),
        ("t-bad", "※ ただし4回のうち1回は、AIがその1行に止まっている行を書いた。翌日は正しく「決まらない」と答えた。"),
        ("t-xs", "架空データでの実測（メモ16通・各1回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "止まった日の引き継ぎメモだけを、1通ずつ別のまっさらな会話に渡して、"
        "次に手を付ける行を答えられるかを頼み方4通りで並べた表。"
        "待ち行列そのものも資料も渡していない。"
        "聞いたのは3つで、止まっている行はどれか、それぞれ次に何をすればよいか、"
        "まだ一度も手を付けていない行のうちいちばん上はどれか、である。"
        "3つ目には、メモから決まらないときはそう書いてくださいと添えてある。"
        "1つ目の質問は16回とも正解で、止まった2行を2行とも名指しした。"
        "3つ目の結果は、そのまま、その旨を書いてと頼んだメモが4回中2回、"
        "何が起きたか、何を試したか、次に何をすれば直るかを入れさせたメモが4回中1回、"
        "会話ではなくファイルにだけ書いてと足したメモが4回中2回で、合わせて12回中5回だった。"
        "残る7回はこのメモからは決まらないと答えている。"
        "ところが、答えのどこかに行の番号が出てくるかで数えると16回とも16回である。"
        "断った理由は返り自身が書いていて、その行が本当に未着手かはメモに書かれていない、というものだった。"
        "次はこの行からという1行を書かせた4回は、4回ともその1行を根拠に答えている。"
        "ただしその4回のうち1回は、AIがその1行に止まっている行のほうを書いてしまい、"
        "翌日は正しく決まらないと答えた。"
    )
    (OUT / "handoff-memo-next-row.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def pass_criteria_detection_chart() -> None:
    """合格の条件を渡すかどうかで、不良40件の検出と誤検出がどう動くかを並べる。

    実測（2026-08-21・架空の毎朝の出来上がり20日ぶんを2本、3通りの頼み方 × 各2回 × 2本
    ＝ 全12回・のべ240判定）。値は check.py の B節・C節の出力。棒の長さは件数から計算する。
    """
    rows = [
        ("条件を渡さず「うまくいっていますか」", 36, 6, None),
        ("先にAIに書かせた5条件を渡して判定させる", 24, 0, None),
        ("5条件＋〔条件の外で気になったこと〕の欄", 18, 0, 40),
    ]
    label_x = 18
    plot_x = 336
    plot_w = 250
    top = 150
    row_h = 62
    bar_h = 20
    max_n = 40

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "条件を渡すと誤検出は消える。かわりに、条件の外の不良も消える</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の「毎朝の出来上がり」20日ぶんを2本（経費申請の仕分け／サイトのリンク切れ点検）。"
        "どちらも</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "10日は本物の成功、10日は成功に見える失敗にした（内訳が合わない／前日と1文字も同じ／"
        "日付だけ</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "今日で中身は3日前／欄はそろっているが全部0／並び順だけ変えて中身は前日と同じ、を各2日）。"
        "</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "1つの頼み方につき材料2本 × 各2回 ＝ 4回、20日ぶんずつ判定させた。全12回・のべ240判定。"
        "</text>\n",
        f'<text class="t-xs" x="{plot_x}" y="{top - 22}">'
        "不良40件のうち、判定の欄で「うまくいっていない」と答えた数</text>\n",
    ]

    y = top
    for label, found, fp, boxed in rows:
        ty = y + 16
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w = round(plot_w * found / max_n)
        parts.append(
            f'<rect class="bar-out" x="{plot_x}" y="{ty - 14}" '
            f'width="{w}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-accent" x="{plot_x + w + 6}" y="{ty}">{found}/40</text>\n'
        )
        note = f"誤検出 {fp}/40" if fp else "誤検出 0/40"
        cls = "t-bad" if fp else "t-good"
        parts.append(f'<text class="{cls}" x="{plot_x}" y="{ty + 20}">{_esc(note)}</text>\n')
        if boxed is not None:
            wb = round(plot_w * boxed / max_n)
            parts.append(
                f'<rect class="box-good" x="{plot_x}" y="{ty + 26}" '
                f'width="{wb}" height="{bar_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="t-good" x="{plot_x + 8}" y="{ty + 40}">'
                "欄の中身まで数えると 40/40</text>\n"
            )
        y += row_h + (24 if boxed is not None else 0)

    notes = [
        ("t-bad", "※ 条件を渡さない版の誤検出6件は、4回とも同じ3日＝「差し戻し0件だが受け取りは25件」の平常な朝。"),
        ("t-bad", "　 件数が多い日に不備0件なのはおかしい、という筋の通った理由が付いていた。それでも正常な日である。"),
        ("t-bad", "※ 条件を渡した版で落ちるのは、条件に書かれていない型だけ。条件に書いてある型（内訳が合わない）は"),
        ("t-bad", "　 3版とも 8/8 で崩れない。落ちたのは前日との重複と、全部0の朝。"),
        ("t-good", "※ 〔条件の外で気になったこと〕の欄を1つ足すと、4回とも欄の中に落ちたぶんが全部出てきた（10/10 × 4回）。"),
        ("t-bad", "🚨 ただし判定の欄は 24/40 → 18/40 にさらに減った。欄を読まない人には、いちばん悪い版に見える。"),
        ("t-xs", "架空データでの実測（全12回・のべ240判定）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の自動処理の出来上がりを判定させたとき、合格の条件を渡すかどうかで"
        "不良の検出と誤検出がどう変わるかを並べた横棒グラフ。"
        "架空の出来上がり20日ぶんを2本作り、どちらも10日を本物の成功、10日を成功に見える失敗にした。"
        "失敗の型は5つで、内訳が合わない、前日と1文字も同じ、日付だけ今日で中身は3日前、"
        "欄はそろっているが全部0、並び順だけ変えて中身は前日と同じ、を各2日ずつである。"
        "1つの頼み方につき材料2本かける各2回で4回、20日ぶんずつ判定させ、全12回のべ240判定を取った。"
        "条件を渡さずうまくいっていますかと聞いた4回は、不良40件のうち36件を検出し、誤検出が6件あった。"
        "先にAIに書かせた5つの条件を渡して判定させた4回は、検出24件で誤検出は0件。"
        "5条件に加えて条件の外で気になったことという欄を足した4回は、判定の欄では18件しか検出しなかったが、"
        "その欄の中身まで数えると40件すべてを拾っていた。誤検出は0件である。"
        "条件を渡さない版の誤検出6件は、4回とも同じ3日で、差し戻しが0件だが受け取りは25件という平常な朝だった。"
        "件数が多い日に不備が0件なのはおかしいという筋の通った理由が付いていたが、実際には正常な日である。"
        "条件を渡した版で落ちるのは条件に書かれていない型だけで、"
        "条件に書いてある内訳が合わない型は3つの版とも8件中8件で崩れていない。"
        "落ちたのは前日との重複と、全部0の朝だった。"
        "条件の外で気になったことの欄を足すと、4回とも欄の中に落ちたぶんが全部出てきている。"
        "ただし判定の欄は24件から18件へさらに減っており、欄を読まない人にはいちばん悪い版に見える。"
    )
    (OUT / "pass-criteria-detection.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def pass_criteria_by_fault_type_chart() -> None:
    """不良の型ごとに、3つの版が何件拾えたかを並べる。

    実測（2026-08-21）。型ごとに 2日 × 材料2本 × 各2回 ＝ 8件。値は check.py の F節。
    """
    rows = [
        ("内訳が合わない（合計が閉じない）", 8, 8, 8),
        ("欄はそろっているが全部0", 8, 4, 4),
        ("日付だけ今日で、中身は3日前", 8, 4, 2),
        ("前日と1文字も同じ", 6, 4, 2),
        ("並び順だけ変えて、中身は前日と同じ", 6, 4, 2),
    ]
    label_x = 18
    col_x = [420, 510, 610]
    col_names = [["条件を", "渡さない"], ["5条件を", "渡す"], ["5条件＋", "欄"]]
    top = 158
    row_h = 46

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "崩れない型が1つだけある。条件に書いてある型がそれ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "前の図と同じ12回を、仕込んだ不良の型ごとに数え直した。"
        "1つの型につき 2日 × 材料2本 × 各2回 ＝ 8件。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "AIが先に書いた5条件には、材料2本 × 2回の計20条のうち"
        "「前日と同じ中身か」を見る条が1つも無かった。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "「全部0」を失敗と書いたのは、リンク点検の側の2回だけ"
        "（経費の側は「0件の朝も行が出ていれば合格」と書いた）。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "下の数は、いずれも判定の欄だけを数えたもの。"
        "〔条件の外〕の欄は含めていない。</text>\n",
    ]
    for cx, lines in zip(col_x, col_names):
        for i, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 30 + i * 14}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, na, nb, nd in rows:
        ty = y + 17
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for cx, n in zip(col_x, (na, nb, nd)):
            if n == 8:
                box, cls = "box-good", "t-good"
            elif n <= 2:
                box, cls = "box-bad", "t-bad"
            else:
                box, cls = "box-quiet", "t-sm"
            parts.append(
                f'<rect class="{box}" x="{cx - 24}" y="{ty - 14}" '
                f'width="48" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{cx}" y="{ty}" '
                f'text-anchor="middle">{n}/8</text>\n'
            )
        y += row_h

    notes = [
        ("t-good", "※ いちばん上の「内訳が合わない」だけが、3つの版とも 8/8。条件を書かせた4回とも、この型を見る条がある。"),
        ("t-bad", "※ 下の3つは、条件を渡すほど下がる。条件に無い型は、判定の欄では話題にならない。"),
        ("t-bad", "※ 「全部0」は、条件に書いた側（リンク点検）では 4/4 で拾い、書かなかった側（経費）では 0/4 だった。"),
        ("t-bad", "　 同じ型でも、条件に書いたかどうかで結果が割れる。AIの賢さではなく、条文の側で決まっている。"),
        ("t-xs", "架空データでの実測（全12回）。型ごとの件数は判定の一覧から数え直したもので、手で数えていない。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の出来上がりに仕込んだ5種類の不良について、"
        "合格の条件を渡すかどうかで何件拾えたかを並べた表。"
        "1つの型につき2日かける材料2本かける各2回で8件ある。"
        "内訳が合わない型は、条件を渡さない版が8件中8件、5条件を渡した版が8件、"
        "5条件と条件の外の欄を足した版も8件で、3つとも崩れていない。"
        "欄はそろっているが全部0の型は、条件を渡さない版が8件、5条件を渡した版が4件、欄を足した版が4件。"
        "日付だけ今日で中身は3日前の型は、8件、4件、2件。"
        "前日と1文字も同じ型は、6件、4件、2件。"
        "並び順だけ変えて中身は前日と同じ型は、6件、4件、2件である。"
        "AIが先に書いた5条件には、材料2本かける2回の合わせて20条のうち、"
        "前日と同じ中身かどうかを見る条が1つも無かった。"
        "全部0を失敗と書いたのはリンク点検の側の2回だけで、"
        "経費の側は0件の朝も行が出ていれば合格と書いている。"
        "その結果、全部0の型は条件に書いた側では4件中4件を拾い、書かなかった側では4件中0件だった。"
        "同じ型でも、条件に書いたかどうかで結果が割れている。"
        "なおこの数はいずれも判定の欄だけを数えたもので、条件の外の欄は含めていない。"
    )
    (OUT / "pass-criteria-by-fault-type.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def formula_range_by_version_chart() -> None:
    """頼み方4通りごとに、最後に勧められた数式の参照範囲の形を並べる。

    実測（2026-08-21・架空の売上表2本 × 4版 × 各2回 ＝ 全16回）。
    値は check.py の C節（16回それぞれから「最後に勧められた数式」を1本ずつ拾い、
    実際に SUMIF を計算して31行目を足した表の真値と突き合わせたもの）。
    """
    rows = [
        ("そのまま「担当ごとの合計を出す数式を」", 4, 0, 0, 4),
        ("＋「この表は毎月行が増えます」", 2, 2, 0, 2),
        ("＋「行が増えても直さなくていい形に」", 0, 3, 1, 0),
        ("＋㋐㋑㋒に分けて書かせる（受け皿つき）", 0, 4, 0, 0),
    ]
    label_x = 18
    plot_x = 330
    cell_w = 56
    top = 156
    row_h = 54

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "そのまま頼むと、4回とも範囲が「渡した表の最終行」で止まる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の売上表を2本（きれいな30行／列の形を変えて空欄と表記ゆれを混ぜた30行）。"
        "1つの頼み方に</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "つき材料2本 × 各2回 ＝ 4回。全16回。"
        "1行足したあとの正しい答えは、走らせる前に Python で確定させた。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "下の数は、16回それぞれから「最後にこれを使ってと勧められた数式」を"
        "1本ずつ拾って分類したもの。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "いちばん右は、その数式を実際に計算して、31行目を1行足した表の真値と"
        "合わなくなった回の数。</text>\n",
    ]
    heads = [
        ["最終行で", "固定"],
        ["列ぜんぶ", "$B:$B"],
        ["テーブル", "参照"],
        ["1行足すと", "合わない"],
    ]
    for i, lines in enumerate(heads):
        cx = plot_x + i * (cell_w + 22) + cell_w // 2
        for j, ln in enumerate(lines):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 32 + j * 14}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, fixed, whole, table, broken in rows:
        ty = y + 17
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for i, n in enumerate((fixed, whole, table, broken)):
            cx = plot_x + i * (cell_w + 22)
            if i == 3:
                box = "box-bad" if n else "box-good"
                cls = "t-bad" if n else "t-good"
            elif i == 0:
                box = "box-bad" if n else "box-quiet"
                cls = "t-bad" if n else "t-sm"
            else:
                box = "box-good" if n else "box-quiet"
                cls = "t-good" if n else "t-sm"
            parts.append(
                f'<rect class="{box}" x="{cx}" y="{ty - 14}" '
                f'width="{cell_w}" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{cx + cell_w // 2}" y="{ty}" '
                f'text-anchor="middle">{n}/4</text>\n'
            )
        y += row_h

    notes = [
        ("t-bad", "※ そのまま頼んだ4回は、返した SUMIF 12本が12本とも $B$2:$B$31 の形だった。渡した30行では真値と一致する。"),
        ("t-sm", "※ 「毎月行が増えます」と前提だけ伝えると、4回中2回しか直らない。残る2回は固定のまま、"),
        ("t-sm", "　 「行を足したら『31』を最終行の番号に書き換えてください」と自分から書き添えてくる。"),
        ("t-good", "※ 「行が増えても直さなくていい形にしてください」まで書くと、4回とも固定が消えた（列ぜんぶ／テーブル参照）。"),
        ("t-good", "※ ㋒「その範囲は行を足したときにどうなるか」の欄を作ると、㋑に固定を書いた2回が、直後の㋒で自分で打ち消した。"),
        ("t-xs", "架空データでの実測（全16回）。生の返りと照合コードは docs/evidence/ に全文置いてある。"),
    ]
    y += 8
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "架空の売上表2本に担当ごとの売上合計を出す数式を書かせた全16回について、"
        "頼み方4通りごとに、最後に勧められた数式の参照範囲の形を数えた表。"
        "1つの頼み方につき材料2本かける各2回で4回ある。"
        "そのまま担当ごとの合計を出す数式をと頼んだ4回は、4回とも最終行で固定の形で、"
        "列ぜんぶもテーブル参照も0回、31行目を1行足すと真値と合わなくなった回が4回。"
        "この表は毎月行が増えますと前提を足した4回は、最終行で固定が2回、列ぜんぶが2回、"
        "合わなくなった回が2回。"
        "行が増えても直さなくていい形にしてくださいまで書いた4回は、固定が0回、"
        "列ぜんぶが3回、テーブル参照が1回で、合わなくなった回は0回。"
        "入れるセルと参照する範囲と行を足したときにどうなるかを分けて書かせ、"
        "範囲が決められないものを別の欄に残させた4回も、固定が0回、列ぜんぶが4回、"
        "合わなくなった回は0回だった。"
        "そのまま頼んだ4回が返した SUMIF は12本あり、12本とも最終行で固定の形である。"
        "渡した30行の範囲では、いずれも真値と一致していた。"
        "毎月行が増えますと前提だけ伝えた版で固定のままだった2回は、"
        "行を足したら31を最終行の番号に書き換えてくださいと自分から書き添えている。"
        "範囲の説明を分けて書かせた版では、参照する範囲の欄に固定の形を書いた2回が、"
        "直後の行を足したときどうなるかの欄で自分でそれを打ち消し、列ぜんぶに直した。"
    )
    (OUT / "formula-range-by-version.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def formula_added_row_invisible_chart() -> None:
    """1行足したときに、参照範囲の形で答えがどう動くかを並べる。

    実測（2026-08-21・材料A）。値は check.py の C節と truth.json。
    検算の合計も同じ範囲で書かれているので、内訳と合計が一致したままになる。
    """
    cols = [("足す前（30行）", 320), ("1行足したあと", 452), ("その表の真値", 584)]
    rows = [
        ("範囲を最終行で固定", "=SUMIF($B$2:$B$31, H3, $F$2:$F$31)", "269,500", "269,500", "305,500", True),
        ("列ぜんぶを見る", "=SUMIF($B:$B, H3, $F:$F)", "269,500", "305,500", "305,500", False),
    ]
    top = 168
    row_h = 64

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "足した1行は、エラーも警告も出さずにどこにも入らない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の売上表（30行）に、佐藤さんの 36,000 円の行を1行足した。"
        "担当ごとの合計がどう動くかを、</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "参照範囲の形ごとに並べたもの。数字は SUMIF を実際に計算して出した"
        "（表計算ソフトで目視していない）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "1行足したあとの佐藤さんの正しい合計は 305,500 円。"
        "足す前は 269,500 円で、差は 36,000 円ちょうど。</text>\n",
    ]
    for name, cx in cols:
        parts.append(
            f'<text class="t-xs" x="{cx}" y="{top - 26}" '
            f'text-anchor="middle">{_esc(name)}</text>\n'
        )

    y = top
    for label, formula, before, after, truth, bad in rows:
        ty = y + 17
        parts.append(f'<text class="t-strong" x="18" y="{ty}">{_esc(label)}</text>\n')
        parts.append(f'<text class="mono" x="18" y="{ty + 21}">{_esc(formula)}</text>\n')
        for i, (value, (_, cx)) in enumerate(zip((before, after, truth), cols)):
            if i == 1:
                box = "box-bad" if bad else "box-good"
                cls = "t-bad" if bad else "t-good"
            else:
                box, cls = "box-quiet", "t-sm"
            parts.append(
                f'<rect class="{box}" x="{cx - 58}" y="{ty - 15}" '
                f'width="116" height="24" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{cx}" y="{ty + 2}" '
                f'text-anchor="middle">{_esc(value)} 円</text>\n'
            )
        if bad:
            parts.append(
                f'<text class="t-bad" x="18" y="{ty + 42}">'
                "🚨 足した 36,000 円がどこにも入らない（範囲が31行目で切れているため）</text>\n"
            )
        y += row_h + (10 if bad else 0)

    y += 8
    parts.append(f'<rect class="box-bad" x="18" y="{y}" width="666" height="80" rx="6"/>\n')
    parts.append(
        f'<text class="t-bad" x="34" y="{y + 25}">'
        "検算も同じ範囲で書かれている</text>\n"
    )
    parts.append(
        f'<text class="t" x="34" y="{y + 48}">'
        "返りが添えてくる =SUM($F$2:$F$31) も31行目までなので、合計は 837,500 のまま。"
        "</text>\n"
    )
    parts.append(
        f'<text class="t" x="34" y="{y + 69}">'
        "内訳の3人ぶんを足しても 837,500。一致するので、36,000 円足りないことが画面から分からない。"
        "</text>\n"
    )
    y += 80

    notes = [
        ("t-good", "※ 「さきほどの数式は直さないでください」＋「数字が変わらない担当がいたら、その理由も書いてください」"),
        ("t-good", "　 と頼んだ4回は、4回とも「変わりません」と答え、4回とも理由に範囲を挙げ、4回とも正しい合計を書いた。"),
        ("t-sm", "※ 「この数式で大丈夫ですか」ではなく、変わらなかったこと自体を説明させると、範囲の話が出てくる。"),
        ("t-xs", "架空データでの実測（検算の頼み方は材料2本 × 各2回 ＝ 4回）。生の返りは docs/evidence/ にある。"),
    ]
    y += 22
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "架空の売上表30行に佐藤さんの36,000円の行を1行足したとき、"
        "数式の参照範囲の形で答えがどう動くかを並べた図。"
        "範囲を最終行で固定した数式、つまりSUMIFのB2からB31とF2からF31を参照する形では、"
        "佐藤さんの合計が足す前も足したあとも269,500円のまま変わらない。"
        "その表の真値は305,500円なので、36,000円ぶん足りない。"
        "列ぜんぶを見る数式、つまりSUMIFのB列全体とF列全体を参照する形では、"
        "足す前が269,500円、足したあとが305,500円になり、真値と一致する。"
        "さらに、返りが添えてくる検算の数式も同じ範囲で書かれている。"
        "SUMのF2からF31は31行目までしか見ないので、合計は837,500円のまま変わらず、"
        "内訳の3人ぶんを足しても837,500円になる。"
        "合計と内訳が一致してしまうため、36,000円足りないことが画面からは分からない。"
        "なお、さきほどの数式は直さないでくださいと断ったうえで、"
        "数字が変わらない担当がいたらその理由も書いてくださいと頼んだ4回は、"
        "4回とも変わりませんと答え、4回とも理由に参照範囲を挙げ、"
        "4回ともその表の正しい合計を書いた。"
    )
    (OUT / "formula-added-row-invisible.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def take_home_two_readings_chart() -> None:
    """契約12万円で、段の基準を税込・税抜どちらで分けるかで手取りが割れることを並べる。

    実測（2026-08-21・架空の契約2種 × 5版 × 各2回 ＝ 20回）。
    値は check.py の B節。金額は公表されている料率と公式の計算例から計算した。
    """
    steps = [
        (
            "段の基準を「税込 132,000円」で分ける",
            ["10万円まで  100,000 × 20% = 20,000", "残り         32,000 × 10% =  3,200"],
            "利用料 23,200 ＋ 消費税 2,320 ＝ 25,520",
            "106,480 円",
        ),
        (
            "段の基準を「税抜 120,000円」で分ける",
            ["10万円まで  100,000 × 20% = 20,000", "残り         20,000 × 10% =  2,000"],
            "利用料 22,000 ＋ 消費税 2,200 ＝ 24,200",
            "107,800 円",
        ),
    ]
    top = 138
    box_h = 118
    gap = 18
    box_w = 330

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ契約額から、手取りが2通り出る</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の契約金額 120,000円（税抜）。公表されている料率（10万円以下の部分 20%／"
        "10万円超20万円</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "以下の部分 10%）と、公式の計算例の順（税込にしてから率を掛ける）を、"
        "そのまま当てはめた。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "分かれ目は1点だけ——段を分ける「10万円」を、税込の額で見るか税抜の額で見るか。"
        "</text>\n",
        '<text class="t-bad" x="18" y="107">'
        "🚨 どちらが正しいかは、料率のページに書かれていない（2026-08-21 に開いて確認）。</text>\n",
    ]

    for i, (label, lines, sub, total) in enumerate(steps):
        x = 18 + i * (box_w + gap)
        cls = "box-quiet"
        parts.append(
            f'<rect class="{cls}" x="{x}" y="{top}" '
            f'width="{box_w}" height="{box_h}" rx="6"/>\n'
        )
        parts.append(
            f'<text class="t-strong" x="{x + 14}" y="{top + 26}">{_esc(label)}</text>\n'
        )
        for j, ln in enumerate(lines):
            parts.append(
                f'<text class="mono" x="{x + 14}" y="{top + 50 + j * 19}">{_esc(ln)}</text>\n'
            )
        parts.append(
            f'<text class="t-sm" x="{x + 14}" y="{top + 92}">{_esc(sub)}</text>\n'
        )
        parts.append(
            f'<text class="t-accent" x="{x + 14}" y="{top + 111}">'
            f"手取り {_esc(total)}</text>\n"
        )

    y = top + box_h + 20
    parts.append(f'<rect class="box-bad" x="18" y="{y}" width="678" height="46" rx="6"/>\n')
    parts.append(
        f'<text class="t-bad" x="34" y="{y + 29}">'
        "差 1,320 円。契約額の 1.1% にあたる。どちらで計算したかを書かないと、"
        "受け取ってから気づく。</text>\n"
    )
    y += 46

    notes = [
        ("t-sm", "※ 表の見出しは「報酬額」とだけあり、税込か税抜かを示す行が無い。"),
        ("t-sm", "※ 公式の計算例は契約 10,000円（税抜）の1通りだけ。この額は10万円を超えないので、段を分ける場面が出てこない。"),
        ("t-good", "※ 「書かれていますか。書かれていれば行を写して、なければ『書かれていません』とだけ」と聞いた3回は、3回とも正解した。"),
        ("t-xs", "架空データでの実測（全26回）。生の返りと照合コードは docs/evidence/ に全文置いてある。料率は変わるので、使う前に開いて確かめること。"),
    ]
    y += 26
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "架空の契約金額12万円（税抜）について、手数料の段を分ける基準を"
        "税込の132,000円で見るか税抜の120,000円で見るかで、手取りが2通りに分かれることを示した図。"
        "税込の132,000円で分けると、10万円までの100,000円に20パーセントで20,000円、"
        "残りの32,000円に10パーセントで3,200円、システム利用料は23,200円に消費税2,320円を足して25,520円となり、"
        "手取りは106,480円になる。"
        "税抜の120,000円で分けると、10万円までの100,000円に20パーセントで20,000円、"
        "残りの20,000円に10パーセントで2,000円、利用料は22,000円に消費税2,200円を足して24,200円となり、"
        "手取りは107,800円になる。差は1,320円で、契約額の1.1パーセントにあたる。"
        "どちらが正しいかは料率のページに書かれていない。"
        "2026年8月21日に開いて確認したところ、表の見出しは報酬額とだけあり、"
        "税込か税抜かを示す行が無かった。"
        "公式の計算例は契約10,000円（税抜）の1通りだけで、この額は10万円を超えないため、"
        "段を分ける場面が例には出てこない。"
        "なお、書かれていますか、書かれていれば行を写して、なければ書かれていませんとだけ、"
        "と聞いた3回は3回とも正解した。"
    )
    (OUT / "take-home-two-readings.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def take_home_by_version_chart() -> None:
    """頼み方ごとに、「2通りの手取りがある」と分かる形で返ってきた回を数える。

    実測（2026-08-21）。値は check.py の C節（契約12万円ぶんの2回ずつ）。
    """
    rows = [
        ("① 率を貼らずに「手取りはいくらですか」", 0, 2, None),
        ("② 料率の表と公式の計算例を貼る", 1, 2, None),
        ("③ ②＋〔ページに書かれていないので決められないこと〕", 2, 2, None),
        ("④ ③＋計算はさせず、率と根拠の行だけ写させる", None, 2, "金額を1つも出さない（指示どおり）"),
        ("⑤ 先に公式の計算例を再現させてから本番", 1, 2, None),
    ]
    label_x = 18
    plot_x = 420
    plot_w = 160
    top = 148
    row_h = 50

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "ページを貼るだけでは閉じない。閉じたのは、置き場所を作ったとき</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の契約金額 120,000円（税抜）を、5通りの頼み方で各2回。"
        "下の数は、税込で段を分けた額</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "（106,480円）と税抜で段を分けた額（107,800円）の"
        "両方が返りに出てきた回の数。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "片方だけの回は、読む人にとっては「答えは1つ」に見える。</text>\n",
        f'<text class="t-xs" x="{plot_x}" y="{top - 22}">'
        "2通りの額を並べた回</text>\n",
    ]

    y = top
    for label, n, total, note in rows:
        ty = y + 17
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        if n is None:
            parts.append(
                f'<rect class="box-quiet" x="{plot_x}" y="{ty - 14}" '
                f'width="{plot_w + 100}" height="19" rx="4"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{plot_x + 10}" y="{ty}">{_esc(note)}</text>\n'
            )
        else:
            w = max(4, round(plot_w * n / total))
            cls = "bar-out" if n == total else ("bar-in" if n else "bar-old")
            parts.append(
                f'<rect class="{cls}" x="{plot_x}" y="{ty - 14}" '
                f'width="{w}" height="19" rx="3"/>\n'
            )
            tcls = "t-good" if n == total else ("t-sm" if n else "t-bad")
            parts.append(
                f'<text class="{tcls}" x="{plot_x + w + 8}" y="{ty}">{n}/{total}回</text>\n'
            )
        y += row_h

    notes = [
        ("t-bad", "※ ①は2回とも1つの額しか出さない。しかも率のURLは4回とも書かず、12万円で聞いた2回はページ名も付かない。"),
        ("t-bad", "※ ②で料率の表と公式の計算例を全文貼っても、2回のうち1回は 107,800円 だけを出して終わった。"),
        ("t-good", "※ ③の欄には2回とも3件ずつ落ち、両方とも先頭2件が同じ（段の基準が税込か税抜か／固定報酬制の集計単位）。"),
        ("t-good", "　 4回ぶん12件をページの本文と1件ずつ突き合わせたところ、実は書いてあったものは0件だった。"),
        ("t-sm", "※ ⑤は4回とも計算例（10,000円→8,580円）を再現できた。それでも本番が例の外に出ると、再現は保証にならない。"),
        ("t-xs", "架空データでの実測（契約12万円ぶん10回。全体は26回）。生の返りは docs/evidence/ にある。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "架空の契約金額12万円の手取りを5通りの頼み方で各2回計算させたとき、"
        "税込で段を分けた106,480円と税抜で段を分けた107,800円の両方が返りに出てきた回の数を並べた図。"
        "率を貼らずに手取りはいくらですかと聞いた版は2回中0回。"
        "料率の表と公式の計算例を貼った版は2回中1回。"
        "それに、ページに書かれていないので決められないことという欄を足した版は2回中2回。"
        "計算をさせず率と根拠の行だけ写させた版は、金額を1つも出さないので対象外である。"
        "先に公式の計算例を再現させてから本番を計算させた版は2回中1回だった。"
        "率を貼らない版は2回とも1つの額しか出さず、率のURLは4回とも書かれず、"
        "12万円で聞いた2回はページ名も付かなかった。"
        "料率の表と公式の計算例を全文貼っても、2回のうち1回は107,800円だけを出して終わっている。"
        "決められないことの欄を作った版では、2回とも3件ずつ落ち、"
        "両方とも先頭2件が同じで、段の基準が税込か税抜かと、固定報酬制の集計単位だった。"
        "4回ぶん12件をページの本文と1件ずつ突き合わせたところ、実は書いてあったものは0件である。"
        "計算例を再現させた版は4回とも10,000円から8,580円を再現できたが、"
        "本番の額が例の外に出ると再現は保証にならない。"
    )
    (OUT / "take-home-by-version.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def proposal_what_repeats_chart() -> None:
    """同じ募集文・同じ頼み方の4本すべてに現れた文の数を、当て方2通りで並べる。

    実測（2026-08-21・架空の募集文2本 × 3版 × 各4本 ＝ 24本）。値は check.py の B節。
    """
    rows = [
        ("(a) 募集文だけ／記事執筆", 2, 1),
        ("(a) 募集文だけ／手順書の清書", 3, 2),
        ("(b) ＋素材メモ／記事執筆", 2, 2),
        ("(b) ＋素材メモ／手順書の清書", 2, 2),
        ("(c) ＋なぜこの案件か1行／記事執筆", 5, 2),
        ("(c) ＋なぜこの案件か1行／手順書の清書", 4, 2),
    ]
    label_x = 18
    col1, col2 = 400, 520
    top = 156
    row_h = 40
    max_n = 5
    bar_w = 90

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "4本すべてに共通した文は、挨拶と見出しだけだった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の募集文2本（記事執筆／手順書の清書）を一字一句そのまま固定し、"
        "渡すものだけを3通りに</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "振って、それぞれ4本ずつ ＝ 全24本。突き合わせは Python の文字列照合だけ"
        "（AIには判定させていない）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "全角半角と空白をそろえ、句点で文に分けてから、4本すべてに現れた文を数えた。"
        "</text>\n",
        f'<text class="t-xs" x="{col1 + bar_w // 2}" y="{top - 30}" text-anchor="middle">'
        "そのまま</text>\n",
        f'<text class="t-xs" x="{col1 + bar_w // 2}" y="{top - 16}" text-anchor="middle">'
        "比べる</text>\n",
        f'<text class="t-xs" x="{col2 + bar_w // 2}" y="{top - 30}" text-anchor="middle">'
        "項目名と番号を</text>\n",
        f'<text class="t-xs" x="{col2 + bar_w // 2}" y="{top - 16}" text-anchor="middle">'
        "落として比べる</text>\n",
    ]

    y = top
    for label, n1, n2 in rows:
        ty = y + 16
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for cx, n in ((col1, n1), (col2, n2)):
            w = max(4, round(bar_w * n / max_n))
            cls = "bar-in" if cx == col1 else "bar-out"
            parts.append(
                f'<rect class="{cls}" x="{cx}" y="{ty - 13}" '
                f'width="{w}" height="18" rx="3"/>\n'
            )
            parts.append(
                f'<text class="t-sm" x="{cx + w + 7}" y="{ty}">{n}件</text>\n'
            )
        y += row_h

    y += 10
    parts.append(f'<rect class="box-quiet" x="18" y="{y}" width="678" height="72" rx="6"/>\n')
    parts.append(
        f'<text class="t-strong" x="34" y="{y + 24}">'
        "残った文の中身</text>\n"
    )
    parts.append(
        f'<text class="mono" x="34" y="{y + 46}">'
        "「はじめまして」／「■ ご指定の5点」／「3. これまでに書いた記事の有無：あります」</text>\n"
    )
    parts.append(
        f'<text class="t-sm" x="34" y="{y + 65}">'
        "3つ目は、素材メモを渡していない版にだけ出てくる（渡した版では中身つきの文になる）。</text>\n"
    )
    y += 72

    notes = [
        ("t-bad", "※ 「はじめまして」は 24/24本、「よろしくお願いいたします」も 24/24本。冒頭の1文は、どの4本組でも4本とも同じ。"),
        ("t-sm", "※ (c) だけ「そのまま比べる」が 4〜5件に増える。素材を渡したぶん単価・時間・日数の行がまるごと一致するため。"),
        ("t-sm", "　 項目名と番号を落とすと (b) と同じ2件に戻る。増えたのは中身が被ったからではない。"),
        ("t-xs", "架空データでの実測（全24本）。生の返りと照合コードは docs/evidence/ に全文置いてある。"),
    ]
    y += 26
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "架空の募集文2本から作った提案文24本について、"
        "同じ募集文・同じ頼み方の4本すべてに現れた文の数を、当て方2通りで並べた横棒グラフ。"
        "募集文だけを渡した版は、そのまま比べると記事執筆で2件、手順書の清書で3件。"
        "項目名と行頭の番号を落として比べると、それぞれ1件と2件に減る。"
        "素材メモを足した版は、そのまま比べても落として比べても、どちらの募集文でも2件。"
        "なぜこの案件かを1行書かせた版は、そのまま比べると記事執筆で5件、手順書の清書で4件だが、"
        "項目名と番号を落とすと どちらも2件に戻る。"
        "残った文の中身は、はじめまして、ご指定の5点という見出し、"
        "そして、これまでに書いた記事の有無はありますという行の3つだけだった。"
        "3つ目は素材メモを渡していない版にだけ出てくる。"
        "なお、はじめましては24本すべて、よろしくお願いいたしますも24本すべてに出ており、"
        "冒頭の1文はどの4本組でも4本とも同じである。"
        "なぜこの案件かを1行書かせた版でそのまま比べた数だけが増えるのは、"
        "素材を渡したぶん単価・時間・日数の行がまるごと一致するためで、"
        "中身が被ったからではない。"
    )
    (OUT / "proposal-what-repeats.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def proposal_answers_drift_chart() -> None:
    """募集文が必須と指定した5項目の答えが、4本で何種類に分かれたかを並べる。

    実測（2026-08-21）。値は check.py の D節2。種類が1なら4本とも同じ値。
    """
    rows = [
        ("希望単価", 3, 4, 1, 1),
        ("1週間に使える時間", 3, 3, 1, 1),
        ("初稿までの日数", 2, 2, 1, 1),
    ]
    label_x = 18
    cols = [(300, "素材なし\n記事執筆"), (400, "素材なし\n清書"),
            (520, "素材あり\n記事執筆"), (620, "素材あり\n清書")]
    top = 172
    row_h = 52

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "他人と被る前に、自分の4本の中で割れていた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "募集文が「必ず書いてください」と指定した5項目のうち、"
        "数字で比べられる3項目を数えたもの。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "同じ募集文から作った4本の答えが、何種類に分かれたか。"
        "1 なら4本とも同じ値、4 なら全部ばらばら。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "5項目に答えたかどうかで見れば、24本すべてが 5/5 で満点である。"
        "割れているのは中身のほう。</text>\n",
    ]
    for cx, name in cols:
        for i, ln in enumerate(name.split("\n")):
            parts.append(
                f'<text class="t-xs" x="{cx}" y="{top - 34 + i * 14}" '
                f'text-anchor="middle">{_esc(ln)}</text>\n'
            )

    y = top
    for label, *vals in rows:
        ty = y + 17
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for (cx, _), n in zip(cols, vals):
            if n == 1:
                box, cls = "box-good", "t-good"
            elif n >= 4:
                box, cls = "box-bad", "t-bad"
            else:
                box, cls = "box-bad", "t-bad"
            parts.append(
                f'<rect class="{box}" x="{cx - 30}" y="{ty - 15}" '
                f'width="60" height="23" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{cls}" x="{cx}" y="{ty + 2}" '
                f'text-anchor="middle">{n}種類</text>\n'
            )
        y += row_h

    y += 8
    parts.append(f'<rect class="box-bad" x="18" y="{y}" width="678" height="72" rx="6"/>\n')
    parts.append(
        f'<text class="t-bad" x="34" y="{y + 24}">'
        "素材メモを渡さない8本に出た、実際の値</text>\n"
    )
    parts.append(
        f'<text class="mono" x="34" y="{y + 46}">'
        "単価: 1文字1.2円 / 1.0円 / 1文字1.5円 / 1本4,000円 / 1本4,500円 / 1本5,000円</text>\n"
    )
    parts.append(
        f'<text class="mono" x="34" y="{y + 65}">'
        "時間: 8 / 10 / 12 時間　　日数: 3 / 4 日</text>\n"
    )
    y += 72

    notes = [
        ("t-bad", "※ 手順書の清書では、1本あたりの金額と1文字あたりの金額が混ざった。数え方そのものが4本で違う。"),
        ("t-bad", "※ 「これまでに書いた記事の有無」は、素材を渡さない8本とも「あります」だけ。中身は 8本とも0件だった。"),
        ("t-good", "※ 素材メモを渡した16本では、その「あります」だけの本は0本。5項目の答えも4本とも同じ値になる。"),
        ("t-good", "※ 素材をまだ渡していないときは、〔私が決める：〕で空欄のまま残させると、4回とも5項目すべてが空欄で残った。"),
        ("t-xs", "架空データでの実測（素材なし8本・素材あり16本・空欄版4回）。生の返りは docs/evidence/ にある。"),
    ]
    y += 26
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "架空の募集文が必ず書いてくださいと指定した5項目のうち、"
        "数字で比べられる3項目について、同じ募集文から作った4本の答えが何種類に分かれたかを並べた表。"
        "素材メモを渡さない場合、希望単価は記事執筆で3種類、手順書の清書で4種類。"
        "1週間に使える時間はどちらも3種類。初稿までの日数はどちらも2種類だった。"
        "素材メモを渡した場合は、単価も時間も日数も、どちらの募集文でも1種類、"
        "つまり4本とも同じ値である。"
        "5項目に答えたかどうかで見れば24本すべてが5項目中5項目で満点なので、"
        "割れているのは答えの中身のほうだけである。"
        "素材メモを渡さない8本に実際に出た値は、単価が1文字1.2円、1.0円、1文字1.5円、"
        "1本4,000円、1本4,500円、1本5,000円。時間が8時間、10時間、12時間。日数が3日と4日だった。"
        "手順書の清書では1本あたりの金額と1文字あたりの金額が混ざり、数え方そのものが4本で違っている。"
        "これまでに書いた記事の有無は、素材を渡さない8本とも、あります、だけで中身は0件だった。"
        "素材メモを渡した16本では、あります、だけの本は0本になる。"
        "素材をまだ渡していないときに、私が決めるという形で空欄のまま残させると、"
        "4回とも5項目すべてが空欄で残った。"
    )
    (OUT / "proposal-answers-drift.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def append_shape_by_version_chart() -> None:
    """書式をどこで伝えるかを6通りに振って、追記行が規定形になった数を並べる。

    実測（2026-08-22・架空の記録2本を各3日ぶん、6版 × 材料2本 × 各2回 × 3回転 ＝ 全72回）。
    値は check.py の B節。棒の長さは 12 を分母にした割合から計算する。
    """
    rows = [
        ("(a) ファイルは見出しだけ・指示文に書式を書かない", 0, "0/12"),
        ("(b) ファイルは見出しだけ・指示文で書式を説明", 12, "12/12"),
        ("(c) お手本を1行だけファイルに置く・指示文には書かない", 12, "12/12"),
        ("(d) お手本1行＋指示文でも説明", 12, "12/12"),
        ("(e) お手本はスラッシュ、指示文の説明はカンマ", 0, "0/12"),
        ("(f) お手本1行＋「ファイルにある行と同じ形に」", 12, "12/12"),
    ]
    label_x = 18
    plot_x = 402
    plot_w = 200
    top = 132
    row_h = 34
    bar_h = 19
    max_n = 12

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "お手本1行だけでも、指示文だけでも同じ。崩れたのは両方書いて食い違わせた版だけ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の記録を2本（副業の作業記録／家計の買い物メモ）。毎日ひとつの走り書きを渡して、"
        "1行だけ</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "追記させる。前の日の返りをそのまま次の日の入力にして3日ぶん回した。"
        "日々の依頼文は6版とも</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "一字一句同じで、振ったのは「書式をどこで伝えるか」だけ。"
        "6版 × 材料2本 × 各2回 × 3回転 ＝ 全72回。</text>\n",
        f'<text class="t-xs" x="{plot_x}" y="{top - 14}">'
        "追記された行が規定の形だった回（のべ12回転ぶん）</text>\n",
    ]

    y = top
    for label, hit, text in rows:
        ty = y + 15
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w = round(plot_w * hit / max_n)
        if w:
            parts.append(
                f'<rect class="bar-out" x="{plot_x}" y="{ty - 14}" '
                f'width="{w}" height="{bar_h}" rx="3"/>\n'
            )
        cls = "t-accent" if hit else "t-bad"
        parts.append(
            f'<text class="{cls}" x="{plot_x + w + 6}" y="{ty}">{_esc(text)}</text>\n'
        )
        y += row_h

    notes = [
        ("t-bad", "※ (a) の0件は「ばらけた」ではない。3日とも同じ形にはそろっている。"),
        ("t-bad", "   ただしその形を決めたのは、初日の走り書きの見た目のほうだった。"),
        ("t-bad", "🚨 (e) は12回とも指示文の側（カンマ）に従い、ファイルのお手本（スラッシュ）に従った回は0。"),
        ("t-good", "※ (b)(c)(d)(f) は、日付の書き方も区切り記号も末尾の単位も、12回とも規定どおり。"),
        ("t-good", "※ 追記が1行でなかった回は72回中0回。すでにある行が1文字でも変わった回も0回。"),
        ("t-xs", "架空データでの実測（全72回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "テキストファイルに毎日1行ずつAIに追記させるとき、書式をどこで伝えるかを6通りに振って、"
        "追記された行が規定の形になった回数を並べた横棒グラフ。"
        "架空の記録を2本、副業の作業記録と家計の買い物メモで用意し、"
        "前の日の返りをそのまま次の日の入力にして3日ぶん回した。"
        "日々の依頼文は6版とも一字一句同じで、振ったのは書式をどこで伝えるかだけである。"
        "6版かける材料2本かける各2回かける3回転で全72回。"
        "ファイルは見出しだけで指示文にも書式を書かない版は12回中0回。"
        "ファイルは見出しだけで指示文で書式を説明した版は12回中12回。"
        "お手本を1行だけファイルに置いて指示文には書かない版も12回中12回。"
        "お手本1行と指示文の説明の両方を置いた版も12回中12回。"
        "お手本はスラッシュ区切りなのに指示文の説明をカンマ区切りにした版は12回中0回で、"
        "12回とも指示文の側に従い、ファイルのお手本に従った回は0回だった。"
        "お手本1行にファイルにある行と同じ形にという一文を添えた版は12回中12回。"
        "追記が1行でなかった回は72回中0回、すでにある行が1文字でも変わった回も0回である。"
    )
    (OUT / "append-shape-by-version.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def append_shape_mixed_file_chart() -> None:
    """(e) の3日ぶんを縦に並べて、1行目のお手本だけが取り残される様子を見せる。

    実測（2026-08-22）。行の文字列は state.json の材料A・系列 e-A-1 のもの。
    """
    left_x = 18
    col_w = 330
    right_x = left_x + col_w + 24
    top = 124
    line_h = 26

    left_lines = [
        ("mono", "# 副業の作業記録（1日1行）"),
        ("mono", "2026-07-31 / C社 / 記事の下書き / 90分"),
        ("mono", "2026-08-01,C社,記事の下書き,90分"),
        ("mono", "2026-08-02,D社,打ち合わせメモ起こし,45分"),
        ("mono", "2026-08-03,C社,修正対応,60分"),
    ]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "食い違わせると、置いたお手本の行だけが取り残される。3日たっても直らない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "ファイルの1行目にはスラッシュ区切りのお手本を置き、指示文ではカンマ区切りだと説明した版"
        "（(e)）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "毎日の依頼文は3日とも一字一句同じ。下は3日目のファイル（材料A・1系列ぶんの実物）。"
        "</text>\n",
        f'<text class="t-xs" x="{left_x}" y="{top - 12}">3日たったファイル</text>\n',
        f'<text class="t-xs" x="{right_x}" y="{top - 12}">その行の区切り</text>\n',
    ]

    box_h = line_h * len(left_lines) + 16
    parts.append(
        f'<rect class="box" x="{left_x - 8}" y="{top - 4}" '
        f'width="{col_w}" height="{box_h}" rx="4"/>\n'
    )

    y = top + 18
    marks = [None, "bad", "quiet", "quiet", "quiet"]
    for (css, text), mark in zip(left_lines, marks):
        parts.append(f'<text class="{css}" x="{left_x}" y="{y}">{_esc(text)}</text>\n')
        if mark == "bad":
            parts.append(
                f'<text class="t-bad" x="{right_x}" y="{y}">スラッシュ（お手本のまま・1行だけ）</text>\n'
            )
        elif mark == "quiet":
            parts.append(
                f'<text class="t-sm" x="{right_x}" y="{y}">カンマ（指示文どおり）</text>\n'
            )
        y += line_h

    y = top + box_h + 28
    notes = [
        ("t-bad", "🚨 4系列とも同じことが起きた。ファイルの中に2通りの形が混ざったまま残ったのは 4/4。"),
        ("t-bad", "   食い違いを直したのは0回。AIは毎日きちんと指示文どおりに書いており、間違えていない。"),
        ("t-bad", "   直らないのは、こちらが「すでにある行は1文字も変えないでください」と書いているため。"),
        ("t-good", "※ 見つけるほうは効く。3日目のファイルを別の新しい会話に渡して形のそろわない行を聞くと、"),
        ("t-good", "   混ざったファイル4回とも、この1行を一字一句そのままコピーして返した。"),
        ("t-good", "   そろっているファイル4回では、4回とも「ありません」＝誤検出0件。"),
        ("t-xs", "架空データでの実測（追記72回＋点検8回＝全80回）。生の返りは docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "ファイルの1行目にスラッシュ区切りのお手本を置き、指示文ではカンマ区切りだと説明した版で、"
        "3日たったあとのファイルの実物を並べた図。"
        "1行目の見出しの下に、2026-07-31のお手本の行だけがスラッシュ区切りで残り、"
        "8月1日、8月2日、8月3日に追記された3行はすべてカンマ区切りになっている。"
        "同じことが4系列とも起き、ファイルの中に2通りの形が混ざったまま残ったのは4系列中4系列で、"
        "食い違いを直した回は0回だった。"
        "AIは毎日きちんと指示文どおりに書いており、間違えてはいない。"
        "直らないのは、こちら側が、すでにある行は1文字も変えないでください、と書いているためである。"
        "見つけるほうは効いた。3日目のファイルを別の新しい会話に渡して形のそろわない行を聞くと、"
        "混ざったファイル4回とも、この1行を一字一句そのままコピーして返した。"
        "そろっているファイル4回では4回ともありませんと答え、誤検出は0件だった。"
    )
    (OUT / "append-shape-mixed-file.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def reply_chase_count_by_version_chart() -> None:
    """催促の一覧に挙がった件数を、6版 × 各4回で並べる。真値は6件。

    実測（2026-08-23・架空の送信済み30行と受信25行を2本、6版 × 材料2本 × 各2回 ＝ 全24回）。
    値は check.py の「催促の一覧に挙がった送信」。帯は4回の最小から最大まで。
    """
    rows = [
        ("① そのまま頼む", [6, 6, 6, 6]),
        ("② ＋出す形を決める", [11, 5, 9, 7]),
        ("③ ＋「2回送ったら1行に」", [8, 11, 9, 9]),
        ("④ ＋「件名で決めないで」", [8, 12, 14, 9]),
        ("⑤ ＋〔決められない〕の欄", [6, 13, 6, 9]),
        ("⑥ 保存版（短く畳む）", [7, 8, 8, 6]),
    ]
    label_x = 18
    plot_x = 286
    plot_w = 280
    axis_max = 15
    scale = plot_w / axis_max
    top = 128
    row_h = 34
    bar_h = 16
    truth = 6

    def px(n: float) -> float:
        return plot_x + n * scale

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "そのまま頼んだ4回は4回とも6件ちょうど。出す形を決めてから、件数が回ごとに割れた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の「送信済み30行」と「受信25行」を2本（会社の総務課／お祭りの事務局）。"
        "催促すべきは</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "6件（本当に未返信の5件＋同じ用件を2回送った1組）で、走らせる前にコードで確かめてある。"
        "</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "6版 × 材料2本 × 各2回 ＝ 全24回。帯は4回の最小から最大まで、縦棒はその4回の値。</text>\n",
        f'<text class="t-xs" x="{px(truth) - 46:.1f}" y="{top - 10}">催促すべきは6件 →</text>\n',
    ]

    plot_bottom = top + len(rows) * row_h - 8
    tx = px(truth)
    parts.append(
        f'<path class="line" d="M{tx:.1f} {top - 4} L{tx:.1f} {plot_bottom}" '
        f'stroke-dasharray="4 3"/>\n'
    )

    y = top
    for label, values in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        lo, hi = min(values), max(values)
        left, right = px(lo), px(hi)
        parts.append(
            f'<rect class="bar-old" x="{left:.1f}" y="{ty - 12}" '
            f'width="{max(right - left, 2):.1f}" height="{bar_h}" rx="3"/>\n'
        )
        for v in sorted(set(values)):
            vx = px(v)
            parts.append(
                f'<path class="line" d="M{vx:.1f} {ty - 13} L{vx:.1f} {ty + 5}" '
                f'stroke-width="2.4"/>\n'
            )
        text = "・".join(str(v) for v in values) + "件"
        cls = "t-accent" if lo == hi == truth else "t-bad"
        parts.append(
            f'<text class="{cls}" x="{px(axis_max) + 8:.1f}" y="{ty}">{_esc(text)}</text>\n'
        )
        y += row_h

    notes = [
        ("t-good", "※ 本当に未返信の5件は、24回のうち23回で5件とも挙がった。落ちたのは②の1回だけ。"),
        ("t-bad", "🚨 ①以外で増えたぶんは、返事の要らない送信（お礼・周知）と、返事が来ている相手。"),
        ("t-bad", "   ②④⑤では、同じ指示文の2回が 11件と5件・8件と12件・6件と13件に割れた。"),
        ("t-xs", "架空データでの実測（全24回）。生の返り24通は docs/evidence/ に全文置いてある。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "送信済み一覧と受信一覧から「返事が来ていないもの」を挙げさせたとき、"
        "催促の一覧に挙がった件数を6通りの頼み方で並べた図。"
        "架空の送信済み30行と受信25行を2本、会社の総務課とお祭りの事務局で用意した。"
        "催促すべきは6件で、本当に未返信の5件と、同じ用件を2回送った1組である。"
        "6版かける材料2本かける各2回で全24回。"
        "そのまま頼んだ版は4回とも6件ちょうど。"
        "出す形を決めた版は11件、5件、9件、7件。"
        "同じ用件を2回送ったら1行にまとめてを足した版は8件、11件、9件、9件。"
        "件名の一致で決めないでを足した版は8件、12件、14件、9件。"
        "決められないの欄を足した版は6件、13件、6件、9件。"
        "毎朝そのまま貼る保存版は7件、8件、8件、6件。"
        "本当に未返信の5件は24回のうち23回で5件とも挙がり、落ちたのは出す形を決めた版の1回だけである。"
        "増えたぶんは、返事の要らない送信と、返事が来ている相手だった。"
    )
    (OUT / "reply-chase-count-by-version.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def reply_changed_subject_chased_chart() -> None:
    """件名を変えて戻ってきた返事を、催促の一覧に入れた件数を版ごとに並べる。

    実測（2026-08-23）。分母は 3件 × 4回 ＝ 12。真値は0件。
    値は check.py の X_chase。当て方2通り（件名／宛先）で同じ数だった。
    """
    rows = [
        ("① そのまま頼む", 0, "0/12"),
        ("② ＋出す形を決める", 0, "0/12"),
        ("③ ＋「2回送ったら1行に」", 6, "6/12"),
        ("④ ＋「件名で決めないで」", 1, "1/12"),
        ("⑤ ＋〔決められない〕の欄", 2, "2/12"),
        ("⑥ 保存版（短く畳む）", 2, "2/12"),
    ]
    label_x = 18
    plot_x = 300
    plot_w = 240
    max_n = 12
    top = 132
    row_h = 34
    bar_h = 19

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "件名を変えて戻ってきた返事は、散文で返る回には1件も混ざらない。混ざるのは形を決めてから"
        "</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "材料には、こちらの問い合わせに答えているのに件名が別物になっている返信を、"
        "1本につき3件</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "仕込んである（「Re:」が付かず、こちらの件名を1文字も含まない）。"
        "この3件は返事が来ているので、</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "催促してはいけない。分母は 3件 × 4回 ＝ 12。真値は0件。</text>\n",
        f'<text class="t-xs" x="{plot_x}" y="{top - 14}">'
        "催促の一覧に入れてしまった件数（少ないほどよい）</text>\n",
    ]

    y = top
    for label, hit, text in rows:
        ty = y + 15
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w = round(plot_w * hit / max_n)
        if w:
            parts.append(
                f'<rect class="box-bad" x="{plot_x}" y="{ty - 14}" '
                f'width="{w}" height="{bar_h}" rx="3"/>\n'
            )
        cls = "t-good" if hit == 0 else "t-bad"
        parts.append(
            f'<text class="{cls}" x="{plot_x + w + 6}" y="{ty}">{_esc(text)}</text>\n'
        )
        y += row_h

    notes = [
        ("t-bad", "🚨 ③がいちばん悪い。「同じ用件は1行にまとめて」を足しただけで、4回とも混ざった。"),
        ("t-bad", "   ④で「件名の一致で決めないで」と書いても、0件にはならなかった（1/12）。"),
        ("t-good", "※ 同じ相手から来た別件のメール3件を「返事」と取り違えた回は、24回で0件だった。"),
        ("t-xs", "当て方は2通り（件名で数える／宛先で数える）とも同じ数。架空データでの実測（全24回）。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "こちらの問い合わせに答えているのに件名が別物になって戻ってきた返信を、"
        "催促の一覧に入れてしまった件数を6通りの頼み方で並べた横棒グラフ。"
        "その返信は1本の材料につき3件仕込んであり、Reが付かず、こちらの件名を1文字も含まない。"
        "返事は来ているので催促してはいけない。分母は3件かける4回で12、真値は0件である。"
        "そのまま頼んだ版は12回中0件。出す形を決めた版も12回中0件。"
        "同じ用件を2回送ったら1行にまとめてを足した版は12回中6件で、4回とも混ざった。"
        "件名の一致で決めないでを足した版は12回中1件。"
        "決められないの欄を足した版は12回中2件。毎朝そのまま貼る保存版は12回中2件。"
        "同じ相手から来た別件のメール3件を返事と取り違えた回は、24回で0件だった。"
        "当て方は件名で数える方法と宛先で数える方法の2通りとも同じ数だった。"
    )
    (OUT / "reply-changed-subject-chased.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def chain_final_count_by_version_chart() -> None:
    """工程の切り方を4通りに振って、最終に出た件数を並べる。真値は12件。

    実測（2026-08-23・架空の問い合わせ24件を2本、4版 × 材料2本 × 各2回 ＝ 16通し・全40回）。
    値は check.py の「最終件数」。帯は4回の最小から最大まで。
    """
    rows = [
        ("(a) 1回で全部やらせる", [12, 12, 12, 12], "4回とも真値どおり"),
        ("(b) 3回に分ける", [12, 12, 0, 1], "材料Bの2回は止まった"),
        ("(c) 分ける＋毎回もとの24件も", [24, 12, 24, 24], "4回中3回で24件全部"),
        ("(d) 分ける＋件数を書かせる", [12, 12, 12, 12], "4回とも真値どおり"),
    ]
    label_x = 18
    plot_x = 232
    plot_w = 240
    axis_max = 26
    scale = plot_w / axis_max
    top = 136
    row_h = 40
    bar_h = 16
    truth = 12

    def px(n: float) -> float:
        return plot_x + n * scale

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "工程に分けても精度は上がらなかった。1回で全部やらせた4回が、4回とも真値どおり</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の問い合わせ24件を2本（A＝事務機器メーカーの窓口・丁寧な長文／"
        "B＝公共施設の窓口・短い口語）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "やらせる中身は4版とも同じ＝①期限が書いてあるものだけ抜く ②3つに分ける "
        "③1件3行にまとめる。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "振ったのは工程の切り方だけ。抜くべきは12件で、走らせる前にコードで確かめてある。"
        "</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "4版 × 材料2本 × 各2回 ＝ 16通し・のべ40回。帯は4回の最小から最大まで。</text>\n",
        f'<text class="t-xs" x="{px(truth) - 42:.1f}" y="{top - 10}">抜くべきは12件 →</text>\n',
    ]

    plot_bottom = top + len(rows) * row_h - 14
    tx = px(truth)
    parts.append(
        f'<path class="line" d="M{tx:.1f} {top - 4} L{tx:.1f} {plot_bottom}" '
        f'stroke-dasharray="4 3"/>\n'
    )

    y = top
    for label, values, note in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        lo, hi = min(values), max(values)
        parts.append(
            f'<rect class="bar-old" x="{px(lo):.1f}" y="{ty - 12}" '
            f'width="{max(px(hi) - px(lo), 2):.1f}" height="{bar_h}" rx="3"/>\n'
        )
        for v in sorted(set(values)):
            vx = px(v)
            parts.append(
                f'<path class="line" d="M{vx:.1f} {ty - 13} L{vx:.1f} {ty + 5}" '
                f'stroke-width="2.4"/>\n'
            )
        text = "・".join(str(v) for v in values) + "件"
        cls = "t-accent" if lo == hi == truth else "t-bad"
        parts.append(
            f'<text class="{cls}" x="{px(axis_max) + 8:.1f}" y="{ty}">{_esc(text)}</text>\n'
        )
        parts.append(f'<text class="t-sm" x="{label_x + 12}" y="{ty + 17}">{_esc(note)}</text>\n')
        y += row_h

    notes = [
        ("t-bad", "🚨 (b) の0件と1件は「間違えた」ではない。下流が「中身が渡っていません」と断って"),
        ("t-bad", "   一覧を作らなかった回。毎朝ひとりでに走らせていれば、その朝は何も出ない。"),
        ("t-bad", "🚨 (c) の24件は、下流が上流の絞り込みを捨てて、もとの24件を全部やり直したもの。"),
        ("t-good", "※ 材料に無い型番が出た回は、40回で0件。作り話は1件も混ざらなかった。"),
        ("t-xs", "架空データでの実測（16通し・のべ40回）。40通の生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の処理を工程に分けて回したとき、最終に出た件数を4通りの切り方で並べた図。"
        "架空の問い合わせ24件を2本、事務機器メーカーの窓口の丁寧な長文と、"
        "公共施設の窓口の短い口語で用意した。"
        "やらせる中身は4版とも同じで、期限が書いてあるものだけ抜き、3つに分け、1件3行にまとめる。"
        "抜くべきは12件である。4版かける材料2本かける各2回で16通し、のべ40回。"
        "1回で全部やらせた版は4回とも12件で真値どおり。"
        "3回に分けた版は12件、12件、0件、1件で、短い口語の材料の2回は下流が中身が渡っていないと断って"
        "一覧を作らなかった。"
        "分けたうえで毎回もとの24件も渡した版は24件、12件、24件、24件で、4回中3回は下流が"
        "上流の絞り込みを捨てて24件全部をやり直している。"
        "分けたうえで各工程に受け取った件数を書かせた版は4回とも12件で真値どおり。"
        "材料に無い型番が出た回は40回で0件だった。"
    )
    (OUT / "chain-final-count-by-version.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def chain_what_stage_one_passed_chart() -> None:
    """工程1が下流へ「用件」を渡したかと、その先で何が起きたかを並べる。

    実測（2026-08-23）。手がかりは、各件の本文からその1件にしか出てこない4文字以上の
    文字列を機械で取り出したもの（手で語を選んでいない）。値は carry.py と check.py。
    """
    rows = [
        ("(b) 材料A・1回目", 12, "→ 最終12件（真値どおり）", "good"),
        ("(b) 材料A・2回目", 12, "→ 最終12件（真値どおり）", "good"),
        ("(b) 材料B・1回目", 0, "→ 止まった（一覧を作らず断った）", "bad"),
        ("(b) 材料B・2回目", 0, "→ 止まった（一覧を作らず断った）", "bad"),
        ("(c) 材料A・1回目", 12, "→ 最終24件（絞り込みが消えた）", "bad"),
        ("(c) 材料A・2回目", 8, "→ 最終12件（真値どおり）", "good"),
        ("(c) 材料B・1回目", 1, "→ 最終24件（絞り込みが消えた）", "bad"),
        ("(c) 材料B・2回目", 0, "→ 最終24件（絞り込みが消えた）", "bad"),
        ("(d) 材料A・1回目", 8, "→ 最終12件（真値どおり）", "good"),
        ("(d) 材料A・2回目", 12, "→ 最終12件（真値どおり）", "good"),
        ("(d) 材料B・1回目", 12, "→ 最終12件（真値どおり）", "good"),
        ("(d) 材料B・2回目", 8, "→ 最終12件（真値どおり）", "good"),
    ]
    label_x = 18
    plot_x = 152
    plot_w = 150
    max_n = 12
    top = 128
    row_h = 30
    bar_h = 17
    text_x = plot_x + plot_w + 42

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "止まった2回は、どちらも工程1が「何についての問い合わせか」を1件も渡していない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "工程1に頼んだのは「期限が書いてあるものだけ抜き出して」だけで、"
        "何を添えるかは書いていない。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "棒は、工程1の出力に「その1件にしか出てこない文字列」が残っていた件数"
        "（12件が満点）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "手がかりの文字列は各件の本文から機械で取り出したもので、手で語を選んでいない。</text>\n",
        f'<text class="t-xs" x="{plot_x}" y="{top - 10}">工程1が渡した用件の手がかり</text>\n',
        f'<text class="t-xs" x="{text_x}" y="{top - 10}">その先で起きたこと</text>\n',
    ]

    y = top
    for label, hit, outcome, kind in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w = round(plot_w * hit / max_n)
        if w:
            parts.append(
                f'<rect class="bar-out" x="{plot_x}" y="{ty - 13}" '
                f'width="{w}" height="{bar_h}" rx="3"/>\n'
            )
        parts.append(
            f'<text class="t-sm" x="{plot_x + w + 6}" y="{ty}">{_esc(f"{hit}/12")}</text>\n'
        )
        parts.append(
            f'<text class="{"t-good" if kind == "good" else "t-bad"}" '
            f'x="{text_x}" y="{ty}">{_esc(outcome)}</text>\n'
        )
        y += row_h

    notes = [
        ("t-bad", "🚨 同じ指示文なのに、工程1が渡した量は 220字から875字まで開いた。"),
        ("t-bad", "   材料が短い口語だと、工程1は「番号と期限だけ」に畳んで渡すことがある。"),
        ("t-good", "※ 用件が8件ぶんしか渡らなかった回でも、最終は12件そろっている（要旨は残っていた）。"),
        ("t-xs", "架空データでの実測。工程に分けた12通しぶん（(a) は1回で終わるのでこの表には無い）。"),
    ]
    y += 10
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の処理を3つの工程に分けて回したとき、工程1が下流へ「何についての問い合わせか」を"
        "どれだけ渡したかと、その先で起きたことを並べた横棒グラフ。"
        "工程1に頼んだのは期限が書いてあるものだけ抜き出してということだけで、"
        "何を添えるかは書いていない。"
        "棒は、工程1の出力にその1件にしか出てこない文字列が残っていた件数で、12件が満点である。"
        "分けただけの版は、丁寧な長文の材料で2回とも12件を渡して最終12件になったが、"
        "短い口語の材料では2回とも0件しか渡さず、2回とも下流が一覧を作らずに断った。"
        "毎回もとの24件も渡した版は12件、8件、1件、0件を渡し、最終はそれぞれ24件、12件、24件、24件で、"
        "3回は絞り込みが消えた。"
        "各工程に受け取った件数を書かせた版は8件、12件、12件、8件を渡し、4回とも最終12件で真値どおりだった。"
        "同じ指示文なのに、工程1が渡した量は220字から875字まで開いている。"
        "用件が8件ぶんしか渡らなかった回でも最終は12件そろっており、要旨のほうは残っていた。"
    )
    (OUT / "chain-what-stage-one-passed.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def three_samples_what_gets_shown_chart() -> None:
    """「3件見せて」の見せ方を6通りに振って、その3件に不良が何件入ったかを並べる。

    実測（2026-08-23・架空の毎朝の出来ばえ30日ぶんを2本、6版 × 材料2本 × 各2回 ＝ 全24回）。
    値は check.py。真値＝30件中7件が不良（うち5件は誰が見ても不良、2件は線引きが割れる）。
    """
    # 🚩2026-08-24確認レビュー（🚩2）で修正：⑥（保存版）は「3件見せて、うち何件が不良か」の
    # 形ではなく、不良の件数と識別子だけを返す版（この実測では毎回5件）。この表の物差し
    # （3件のうち何件が不良か）に乗らないので、⑤（全件判定）と同じく表から外す。
    rows = [
        ("① そのまま「3件見せて」", [2, 2, 2, 2]),
        ("② 1件目・15件目・30件目", [1, 1, 1, 1]),
        ("③ 出来のよくないほうから3件", [3, 3, 3, 3]),
        ("④ 先に件数を数えてから3件", [3, 3, 3, 3]),
    ]
    label_x = 18
    plot_x = 268
    cell = 46
    top = 132
    row_h = 34
    bar_h = 18

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「見せてくる3件に、失敗した回は入らない」は外れた。16回とも入っている</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の「毎朝ひとりでにAIが作った要約」を30日ぶん、2本（ニュース要約／問い合わせ日報）用意し、"
        "</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "不良を7件仕込んだ（数字が1つも無い埋め草3件／「本文は読んでいません」2件／材料0行の空要約2件）。"
        "</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "振ったのは「どう見せさせるか」の1つだけ。6版 × 材料2本 × 各2回 ＝ 全24回。</text>\n",
        f'<text class="t-xs" x="{plot_x}" y="{top - 12}">'
        "見せてきた3件のうち、仕込んだ不良だった数（材料2本×各2回の4回ぶん）</text>\n",
    ]

    y = top
    for label, values in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for k, v in enumerate(values):
            x = plot_x + k * cell
            w = round(cell * 0.72 * v / 3)
            if w:
                parts.append(
                    f'<rect class="bar-out" x="{x}" y="{ty - 13}" '
                    f'width="{w}" height="{bar_h}" rx="3"/>\n'
                )
            parts.append(
                f'<text class="t-xs" x="{x + w + 4}" y="{ty}">{v}</text>\n'
            )
        y += row_h

    notes = [
        ("t-good", "※ どの版でも、見せてきた3件に不良が1件も入らなかった回は 16回中0回。"),
        ("t-good", "   当て方2通り（識別子で数える／不良の本文がそのまま引用されたか）でも同じ。"),
        ("t-bad", "🚨 ②が毎回1件なのは、こちらが指定した15件目がたまたま不良だったから。"),
        ("t-bad", "   位置を決めると、結果はその位置に何があるかで決まる。指示文の手柄ではない。"),
        ("t-xs", "⑤（全件判定）と⑥（保存版・件数と識別子だけ）は、3件を選ばせていないので、この表には無い。"),
        ("t-xs", "架空データでの実測（全24回）。24通の生の返りは docs/evidence/ に全文置いてある。"),
    ]
    y += 8
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の出来ばえをAIに3件見せさせたとき、その3件に仕込んだ不良が何件入ったかを"
        "見せ方6通りで並べた図。"
        "架空の毎朝の要約を30日ぶん、ニュース要約と問い合わせ日報の2本用意し、不良を7件仕込んだ。"
        "内訳は数字が1つも無い埋め草3件、本文は読んでいませんという断り付き2件、材料0行の空要約2件である。"
        "6版かける材料2本かける各2回で全24回。"
        "そのまま3件見せてと頼んだ版は4回とも3件のうち2件が不良。"
        "1件目15件目30件目と位置を指定した版は4回とも1件。"
        "出来のよくないほうから3件と頼んだ版は4回とも3件。"
        "先に件数を数えてから3件と頼んだ版も4回とも3件。"
        "見せてきた3件に不良が1件も入らなかった回は16回中0回で、"
        "当て方を識別子で数える方法と不良の本文がそのまま引用されたかで数える方法の2通りに変えても同じだった。"
        "位置を指定した版が毎回1件なのは、指定した15件目がたまたま不良だったためである。"
        "保存版（不良の識別子だけを返す版）は3件を選ばせる形ではなく、この実測では毎回5件を返したので、この表には無い。"
    )
    (OUT / "three-samples-what-gets-shown.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def three_samples_line_flips_chart() -> None:
    """全件判定させたとき、どのグループを「よくない」に入れたかを材料ごとに並べる。

    実測（2026-08-23）。⑤＝30件すべてを1行ずつ判定させた版、⑥＝保存版。
    値は check.py の flagged。
    """
    rows = [
        ("⑤ 全件判定・ニュース要約 1回目", 5, 2, 0),
        ("⑤ 全件判定・ニュース要約 2回目", 5, 2, 0),
        ("⑤ 全件判定・問い合わせ日報 1回目", 5, 0, 3),
        ("⑤ 全件判定・問い合わせ日報 2回目", 5, 0, 3),
        ("⑥ 保存版・ニュース要約 1回目", 5, 0, 0),
        ("⑥ 保存版・ニュース要約 2回目", 5, 0, 0),
        ("⑥ 保存版・問い合わせ日報 1回目", 5, 0, 0),
        ("⑥ 保存版・問い合わせ日報 2回目", 5, 0, 0),
    ]
    cols = [
        ("埋め草＋読んでいません", 5, "不良で正しい"),
        ("材料0行の空要約", 2, "線引きが割れる"),
        ("1文だけだが数字あり", 3, "呼んだら誤り"),
    ]
    label_x = 18
    col_x = [300, 452, 588]
    col_w = 132
    top = 152
    row_h = 30

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "拾い漏れは起きない。割れるのは、どこから先を「よくない」と呼ぶかの線</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "30件すべてを1行ずつ判定させた版（⑤）と、毎朝そのまま貼る保存版（⑥）の、"
        "合わせて8回ぶん。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "仕込みは3つに分かれる＝誰が見ても不良の5件／材料0行の日の空要約2件／"
        "1文だけだが数字は入って</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "いる3件。数字は「よくない」と呼ばれた件数で、いちばん左の列だけが真値どおりの5件になる。</text>\n",
    ]

    for x, (name, denom, note) in zip(col_x, cols):
        parts.append(f'<text class="t-xs" x="{x}" y="{top - 26}">{_esc(name)}</text>\n')
        parts.append(f'<text class="t-xs" x="{x}" y="{top - 10}">（{denom}件・{_esc(note)}）</text>\n')

    y = top
    for label, a, b, c in rows:
        ty = y + 15
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for x, (val, denom, good_is_full) in zip(
            col_x, ((a, 5, True), (b, 2, None), (c, 3, False))
        ):
            if good_is_full is True:
                cls = "box-good" if val == denom else "box-bad"
            elif good_is_full is False:
                cls = "box-good" if val == 0 else "box-bad"
            else:
                cls = "box-quiet"
            parts.append(
                f'<rect class="{cls}" x="{x - 4}" y="{ty - 15}" '
                f'width="{col_w - 8}" height="21" rx="3"/>\n'
            )
            parts.append(f'<text class="t" x="{x + 6}" y="{ty}">{val} / {denom}</text>\n')
        y += row_h

    notes = [
        ("t-bad", "🚨 真ん中と右が、材料をまたぐと逆に動く。ニュース要約では空要約を「よくない」に入れて"),
        ("t-bad", "   薄い3件を通し、問い合わせ日報では空要約を通して薄い3件を「よくない」に入れた。"),
        ("t-good", "※ 左の列（誰が見ても不良の5件）は、8回とも 5/5。拾い漏れは1件も無い。"),
        ("t-good", "※ ふつうの良品20件を「よくない」と呼んだ回は、8回で0件。"),
        ("t-xs", "灰色は真値を決めていない列（材料0行の日に空の要約を出すことを不良と呼ぶかは、決める人の側の話）。"),
    ]
    y += 12
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 21

    height = y
    alt = (
        "毎朝の出来ばえを30件すべて判定させたときと、保存版で判定させたときに、"
        "どのグループを「よくない」と呼んだかを材料ごとに並べた表。"
        "仕込みは3つに分かれ、誰が見ても不良の5件、材料0行の日の空要約2件、"
        "1文だけだが数字は入っている3件である。"
        "誰が見ても不良の5件は、8回とも5件すべてがよくないと呼ばれた。"
        "材料0行の空要約は、ニュース要約の材料では2回とも2件ともよくないに入り、"
        "問い合わせ日報の材料では2回とも0件、保存版では4回とも0件だった。"
        "1文だけだが数字のある3件は、ニュース要約では2回とも0件、"
        "問い合わせ日報では2回とも3件ともよくないに入り、保存版では4回とも0件だった。"
        "つまり2つの列が材料をまたぐと逆に動いている。"
        "ふつうの良品20件をよくないと呼んだ回は8回で0件だった。"
    )
    (OUT / "three-samples-line-flips.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def reply_template_line_by_version_chart() -> None:
    """『ほぼ同じ』の結びの一文を、誤って固定した回数（6回中）。版ごと。

    実測（2026-08-24・架空の返信12通を2本、3版 × 材料2本 × 各3回 ＝ 全18回、
    独立した新規セッションに指示文を送って機械照合）。
    その種類の4通中3通にしか出ない一文（言い回しが1通だけ違う）を、
    「4通全部で一字一句一致」の条件を付けずに固定してしまった回数。
    """
    rows = [
        ("版a　そのまま", 5, True),
        ("版b　＋「4通全部で一致」", 0, False),
        ("版c　＋通数を申告させる", 0, False),
    ]
    label_w = 210
    left = 18 + label_w
    right = WIDTH - 90
    span = right - left
    axis_max = 6
    scale = span / axis_max
    top = 96
    row_h = 40
    bar_h = 20

    def px(n: float) -> float:
        return left + n * scale

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「4通全部で一致」を付けるだけで、誤固定は6回中5回→0回になった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の返信12通を2本。同じ種類の4通のうち3通にしか出ない結びの一文（1通だけ言い回しが違う）を、</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「毎回同じ文」として固定してしまった回数。3版 × 材料2本 × 各3回＝全18回、独立した新規セッションで実施。</text>\n",
    ]
    for i in range(axis_max + 1):
        gx = px(i)
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + len(rows) * row_h - 10}" stroke-width="1" opacity="0.35"/>\n'
        )
        parts.append(f'<text class="t-xs" x="{gx - 3:.1f}" y="{top - 12}">{i}</text>\n')

    y = top
    for label, value, bad in rows:
        by = y + (row_h - bar_h) / 2
        parts.append(f'<text class="t" x="18" y="{y + row_h / 2 + 5:.0f}">{_esc(label)}</text>\n')
        cls = "box-bad" if bad else "box-good"
        bw = max(2.0, value * scale)
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{by:.1f}" '
            f'width="{bw:.1f}" height="{bar_h}" rx="4"/>\n'
        )
        tone = "t-bad" if bad else "t-good"
        parts.append(
            f'<text class="{tone}" x="{left + bw + 8:.1f}" y="{by + bar_h - 5:.1f}">'
            f"{value}／6件</text>\n"
        )
        y += row_h

    height = y + 16 + 21 * 3 + 12
    notes = [
        ("t-sm", "※ 版a（記事 mail-needs-reply.md の一文そのまま）だけが「毎回同じ文は固定して」としか言っていない。"),
        ("t-good", "※ 版b・cは18回中12回とも0件。他の客の固有名詞が固定部に残った回数は、3版とも18回中0回。"),
        ("t-xs", "架空データでの実測。生の返り18通は docs/evidence/ に全文置いてある。"),
    ]
    ny = y + 20
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "『ほぼ同じ』の結びの一文を誤って固定した回数を、3つの版で比べた横棒グラフ。"
        "版a（そのまま）は6回中5回、版b（＋『4通全部で一致』の条件）は6回中0回、"
        "版c（＋通数を申告させる）は6回中0回。"
        "他の客の固有名詞が固定部に残った回数は、3版とも18回中0回だった。"
    )
    (OUT / "reply-template-line-by-version.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def reply_template_grid_chart() -> None:
    """18回すべての結果を、版×回で並べたマス目。

    実測（2026-08-24・全18回。青＝誤って固定しなかった／赤＝1通しか無い言い回しを固定した）。
    """
    rows = [
        ("版a　そのまま", [True, False, False, False, False, False]),
        ("版b　＋「4通全部で一致」", [True, True, True, True, True, True]),
        ("版c　＋通数を申告させる", [True, True, True, True, True, True]),
    ]
    cols = ["A-1", "A-2", "A-3", "B-1", "B-2", "B-3"]
    label_w = 200
    cell_w, cell_h, gap = 60, 30, 8
    top = 118
    pitch = cell_h + gap
    grid_x = label_w
    right_x = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_x + 60 <= WIDTH - 18, right_x

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "18回すべての結果。青＝正しく空欄にした／赤＝誤って固定した</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "A＝副業ライターの返信12通、B＝ハンドメイド作家の返信12通。それぞれ独立した新規セッションに送った。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "誤って固定した＝その種類の4通中3通にしか出ない結びの一文を「毎回同じ文」として型に残した。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "各セルは1回ぶんの返り。同じ版でも6回すべてを別々に数えている（まとめていない）。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x + cell_w / 2 - 12:.1f}" y="{top - 10}">{name}</text>\n'
        )

    for row_index, (name, oks) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(f'<text class="t-sm" x="18" y="{y + 20}">{_esc(name)}</text>\n')
        for col_index, ok in enumerate(oks):
            x = grid_x + col_index * (cell_w + gap)
            klass = "box-accent" if ok else "box-bad"
            parts.append(
                f'<rect class="{klass}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            mark = "空欄" if ok else "固定"
            tone = "t-accent" if ok else "t-bad"
            parts.append(
                f'<text class="{tone}" x="{x + cell_w / 2 - 13:.1f}" y="{y + 20}">{mark}</text>\n'
            )
        ok_n = sum(oks)
        parts.append(
            f'<text class="t-sm" x="{right_x + 14}" y="{y + 20}">{ok_n}／6</text>\n'
        )

    height = top + len(rows) * pitch + 12 + 21 * 2 + 16
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 34}">'
        "※ 版aの1回目だけ、固定せずに両方の言い回しを併記していた（正しい側に数えた）。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 13}">'
        "架空データでの実測。生の返り18通は docs/evidence/ に全文置いてある。</text>\n"
    )

    alt = (
        "18回すべての結果を並べたマス目。A列3回・B列3回を版a・版b・版cで比べている。"
        "版aはA-1だけ正しく空欄にし、A-2・A-3・B-1・B-2・B-3の5回は誤って固定した。"
        "版bと版cはA-1からB-3まで6回とも正しく空欄にした。"
    )
    (OUT / "reply-template-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def date_decides_detect_and_decide_chart() -> None:
    """4組の矛盾を、版ごとに「確定できたか（回数／6）」で並べたマス目。

    実測（2026-08-24・架空のメモ12枚、3版 × 各6回 ＝ 全18回。独立した claude -p
    サブプロセスに送って機械照合）。検出そのものはほぼ全回で4組とも出た
    （18回中17回。詳しくは記事本文）。ここに出すのは「要確認と書かずに
    片方を『いま使う内容』として確定できたか」の回数。
    """
    rows = [
        ("経費精算の承認ライン（日付あり）", [0, 6, 6]),
        ("見積書を送る順番（日付あり）", [0, 6, 6]),
        ("資料へのグラフ（日付なし）", [0, 0, 0]),
        ("問い合わせ返信の宛先（日付なし）", [0, 0, 0]),
    ]
    cols = ["版a：そのまま", "版b：＋日付ルール", "版c：＋下流課題"]
    label_w = 228
    cell_w, cell_h, gap = 132, 34, 10
    top = 132
    pitch = cell_h + gap
    grid_x = 18 + label_w
    right_edge = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_edge <= WIDTH - 18, right_edge

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "確定できるのは日付がある組だけ。日付が無い組は、どの版でも確定しない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空のメモ12枚に矛盾4組（うち2組は各メモに絶対日付あり）を仕込み、"
        "指示文を3版・各6回＝全18回、独立したサブプロセスに送った。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "セルの数＝「要確認」と書かずに片方を『いま使う内容』として確定できた回数（6回中）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "版b＝「日付が新しいほうを採る。日付が無い組は決めない」を追加。"
        "版c＝版bのあと同じ会話で、決めた内容を実際の経費一覧に使わせた。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x + cell_w / 2 - 34:.1f}" y="{top - 12}">{_esc(name)}</text>\n'
        )

    for row_index, (label, values) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(
            f'<text class="t-sm" x="18" y="{y + cell_h / 2 + 5:.0f}">{_esc(label)}</text>\n'
        )
        for col_index, v in enumerate(values):
            x = grid_x + col_index * (cell_w + gap)
            resolved = v > 0
            box = "box-accent" if resolved else "box-quiet"
            tone = "t-accent" if resolved else "t-sm"
            parts.append(
                f'<rect class="{box}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            mark = f"確定 {v}／6" if resolved else "要確認のまま"
            parts.append(
                f'<text class="{tone}" x="{x + cell_w / 2 - 30:.1f}" '
                f'y="{y + cell_h / 2 + 5:.0f}">{mark}</text>\n'
            )

    height = top + len(rows) * pitch + 8 + 21 * 3 + 16
    notes = [
        ("t-sm", "※ 版bの1回だけ、問い合わせ返信の宛先という組自体に触れなかった（18回中1回）。"),
        ("t-good", "※ 日付がある2組を古い方の値で確定した回は、版b・cとも12回中0回。"),
        ("t-xs", "架空データでの実測。生の返り18通は docs/evidence/ に全文置いてある。"),
    ]
    ny = height - 21 * 3 + 5
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "4組の矛盾を版ごとに確定できた回数で並べたマス目。行は経費精算の承認ライン（日付あり）・"
        "見積書を送る順番（日付あり）・資料へのグラフ（日付なし）・問い合わせ返信の宛先（日付なし）。"
        "列は版a（そのまま）・版b（日付ルールを追加）・版c（同じ会話で下流課題）。"
        "日付がある2組は版aで6回中0回しか確定せず要確認のままだったが、版bと版cでは6回とも確定した。"
        "日付が無い2組は3版とも6回中0回で、確定せず要確認のままだった。"
        "日付がある2組を古い方の値で確定した回は版b・cとも12回中0回だった。"
    )
    (OUT / "date-decides-detect-and-decide.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def date_decides_downstream_chart() -> None:
    """版cの2ターン目＝決めたルールを実際の経費一覧に使わせた6回の結果。

    実測（2026-08-24・全6回。棒の長さ＝「要確認」に挙げた件数）。
    古い基準（1万円）のままなら6件、更新後の基準（3万円）なら2件になるように
    経費一覧（8件）を作ってある。
    """
    rows = [f"c-{i}回目" for i in range(1, 7)]
    values = [2, 2, 2, 2, 2, 2]
    label_w = 70
    left = 18 + label_w
    right = WIDTH - 190
    span = right - left
    axis_max = 8
    scale = span / axis_max
    top = 118
    row_h = 30
    bar_h = 16

    def px(n: float) -> float:
        return left + n * scale

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "決まったルールは、同じ会話の次の作業でも6回とも正しく使われた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "版bのやり取りに続けて、同じ会話で「このルールを使って、次の経費一覧から"
        "要確認を挙げて」と頼んだ（全6回）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "経費一覧は8件。古い基準（1万円）のままなら6件、更新後の基準（3万円）なら2件が挙がる作り。</text>\n",
    ]
    for i in range(axis_max + 1):
        gx = px(i)
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + len(rows) * row_h - 6}" stroke-width="1" opacity="0.3"/>\n'
        )
        parts.append(f'<text class="t-xs" x="{gx - 3:.1f}" y="{top - 12}">{i}</text>\n')

    old_x, new_x = px(6), px(2)
    parts.append(
        f'<path class="line" d="M{old_x:.1f} {top - 20} L{old_x:.1f} '
        f'{top + len(rows) * row_h - 6}" stroke-width="1.6" stroke-dasharray="4 3"/>\n'
    )
    parts.append(
        f'<text class="t-xs" x="{old_x - 66:.1f}" y="{top - 24}">古い基準なら6件（0回）</text>\n'
    )
    parts.append(
        f'<path class="line" d="M{new_x:.1f} {top - 36} L{new_x:.1f} '
        f'{top + len(rows) * row_h - 6}" stroke-width="1.6"/>\n'
    )
    parts.append(
        f'<text class="t-accent" x="{new_x - 40:.1f}" y="{top - 40}">新しい基準なら2件（6回とも）</text>\n'
    )

    y = top
    for label, value in zip(rows, values):
        by = y + (row_h - bar_h) / 2
        parts.append(
            f'<text class="t-xs" x="18" y="{y + row_h / 2 + 4:.0f}">{_esc(label)}</text>\n'
        )
        bw = max(2.0, value * scale)
        parts.append(
            f'<rect class="bar-in" x="{left}" y="{by:.1f}" '
            f'width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{left + bw + 8:.1f}" y="{by + bar_h - 3:.1f}">{value}件</text>\n'
        )
        y += row_h

    height = y + 16 + 21 * 2 + 12
    notes = [
        ("t-good", "※ 6回とも、要確認に挙げた金額は35,000円と40,000円の2件でそろった。"),
        ("t-xs", "架空データでの実測。生の返り6通は docs/evidence/ に全文置いてある。"),
    ]
    ny = y + 20
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "決まったルールを同じ会話の次の作業に使わせた6回の結果を並べた横棒グラフ。"
        "経費一覧8件のうち、古い基準（1万円以上）のままなら6件、"
        "更新後の基準（3万円以上）なら2件が要確認に挙がる作りにしてある。"
        "c-1回目からc-6回目まで、6回ともきっちり2件が挙がり、"
        "古い基準の6件になった回は1回も無かった。"
        "挙げた金額も6回とも35,000円と40,000円の2件でそろっていた。"
    )
    (OUT / "date-decides-downstream.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def deadline_holiday_grid_chart() -> None:
    """4件の受注日で「中5営業日」を逆算させた結果を、版ごとに並べたマス目。

    実測（2026-08-24・4件×3版＝12回。独立した新規エージェントに送った）。
    版aは休みの情報を渡していないので、真値そのものが版ごとに違う
    （版aは週末のみを除いた場合の値、版b・cは架空の祝日表ありの値と比べる）。
    ここで比べるのは「その版の中で、4件が同じ数え方に揃ったか」。
    """
    cols = ["9/4(金)", "9/7(月)", "9/18(金)", "9/28(月)"]
    # 🚩2026-08-24確認レビュー（🚩1）で修正：9/4と9/7はどちらも「翌営業日」規則と矛盾しない結果で、
    # この2件だけでは区別できない（同じ規則の可能性が高い）。異なるラベルを付けない。
    row_a = ["翌営業日", "翌営業日", "非営業日", "答えと矛盾"]
    row_a_ok = [True, True, False, False]
    row_b = ["一致", "一致", "一致", "一致"]
    row_c = ["一致", "一致", "一致", "一致"]

    label_w = 210
    cell_w, cell_h, gap = 96, 32, 10
    top = 130
    pitch = cell_h + gap
    grid_x = label_w
    right_x = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_x + 40 <= WIDTH - 18, right_x

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "休みを言わない版は、起算日の決め方が3通りに割れた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "受注日4件（金曜／祝日前日の月曜／連休直前の金曜／月をまたぐ月曜）に「中5営業日で」とだけ頼んだ（版a）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "同じ4件に、架空の祝日表を渡した版（版b）と、数え方の定義文まで足した版（版c）も試した。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "版b・版cは、返ってきた着手日・納品日が4件とも真値と一致し、内容も完全に同じだった。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x + cell_w / 2 - 22:.1f}" y="{top - 12}">{name}</text>\n'
        )

    rows = [
        ("版a　休みを言わない", row_a, [("box-accent" if ok else "box-bad") for ok in row_a_ok],
         ["t-accent" if ok else "t-bad" for ok in row_a_ok]),
        ("版b　＋架空の祝日表", row_b, ["box-good"] * 4, ["t-good"] * 4),
        ("版c　＋数え方の定義文", row_c, ["box-good"] * 4, ["t-good"] * 4),
    ]
    for row_index, (label, cells, boxes, tones) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(f'<text class="t-sm" x="18" y="{y + 20}">{_esc(label)}</text>\n')
        for col_index, text in enumerate(cells):
            x = grid_x + col_index * (cell_w + gap)
            parts.append(
                f'<rect class="{boxes[col_index]}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            tx = x + cell_w / 2 - len(text) * 5.6
            parts.append(
                f'<text class="{tones[col_index]}" x="{tx:.1f}" y="{y + 20}">{text}</text>\n'
            )

    height = top + len(rows) * pitch + 12 + 21 * 3 + 16
    notes = [
        ("t-xs", "※ 9/4と9/7は、どちらも「翌営業日」の規則で説明でき、この2件だけでは区別できない。"),
        ("t-xs", "※ 版aの真値は「週末のみ除いた場合」。版b・cの真値は架空の祝日表ありの場合で、両者は別の値になる。"),
        ("t-xs", "架空データでの実測。生の返り12回は docs/evidence/ に全文置いてある。"),
    ]
    ny = height - 21 * len(notes) + 5
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "受注日4件（9/4金・9/7月・9/18金・9/28月）に「中5営業日で」と逆算させた結果を、"
        "版ごとに並べたマス目。休みを言わない版aは、起算日の決め方が3通りに割れた——"
        "9/4と9/7は翌営業日にずらす規則で説明でき区別できない、9/18は非営業日を着手日にする、"
        "9/28は答えた着手日と計算が矛盾する。"
        "架空の祝日表を渡した版bと、さらに数え方の定義文を足した版cは、"
        "どちらも4件とも真値と一致し、結果の内容も完全に同じだった。"
    )
    (OUT / "deadline-holiday-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def material_match_vs_facts_chart() -> None:
    """「言い換えて」の強さを3段階にしたとき、資料との20字以上一致と、
    社名・地名・数字などの事実の残り方が、それぞれどう動いたかを並べたマス目。

    実測（2026-08-25）。架空の紹介資料3本（各1社ぶん）に、同じ依頼文を
    版a（そのまま）／版b（＋自分の言葉で書き直して）／版c（＋20字以上つながらないように、
    ただし固有名詞と数字はそのまま）の3版で送った。資料3本×3版×2試行＝18回。
    20字以上の一致は Python の difflib で機械判定。事実は社名・地名・創業年・人数・
    数量・締め日など資料ごと6項目（計36項目）を正規表現で照合した。
    """
    cols = ["20字以上の一致（6回合計）", "事実の保持（36項目中）", "慣用句の一致（30個中）"]
    rows = [
        ("版a　そのまま頼む", ["19件", "36/36", "7/30"], ["box-bad", "box-good", "box-quiet"], ["t-bad", "t-good", "t-sm"]),
        ("版b　＋自分の言葉で", ["6件", "36/36", "0/30"], ["box-accent", "box-good", "box-quiet"], ["t-accent", "t-good", "t-sm"]),
        ("版c　＋20字以上つなげない", ["0件", "34/36", "0/30"], ["box-good", "box-accent", "box-quiet"], ["t-good", "t-accent", "t-sm"]),
    ]

    label_w = 190
    cell_w, cell_h, gap = 150, 34, 10
    top = 138
    pitch = cell_h + gap
    grid_x = label_w
    right_x = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_x + 18 <= WIDTH, right_x

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "言い換えを強めるほど一致は消えたが、事実はほとんど残った</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の紹介資料3本に「この資料をもとに紹介文を書いて」と頼み、言い換えの指示を3段階で足した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "版cで欠けた2件は、いずれも同じ資料の「横浜市」から「市」が落ちた回だった（本文参照）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "慣用句（決まり文句5個）は、言い換えを頼んだ版b・cでは1件も残らなかった。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x:.1f}" y="{top - 12}">{_esc(name)}</text>\n'
        )

    for row_index, (label, cells, boxes, tones) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(f'<text class="t-sm" x="18" y="{y + 22}">{_esc(label)}</text>\n')
        for col_index, text in enumerate(cells):
            x = grid_x + col_index * (cell_w + gap)
            parts.append(
                f'<rect class="{boxes[col_index]}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            tx = x + cell_w / 2 - len(text) * 5.6
            parts.append(
                f'<text class="{tones[col_index]}" x="{tx:.1f}" y="{y + 22}">{text}</text>\n'
            )

    height = top + len(rows) * pitch + 12 + 21 * 2 + 16
    notes = [
        ("t-xs", "※ 事実の項目＝社名・所在地・創業年・人数・数量・締め日など資料1本につき6項目。正規表現で照合。"),
        ("t-xs", "架空データでの実測。生の返り18回は docs/evidence/ に全文置いてある。"),
    ]
    ny = height - 21 * 2 + 5
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "架空の紹介資料3本をもとに紹介文を書かせ、言い換えの指示を3段階にしたときの、"
        "20字以上の一致件数と、事実の保持数を並べたマス目。"
        "版a（そのまま頼む）は6回合計で19件の一致があり、事実は36項目中36件が残った。"
        "版b（自分の言葉で書き直して、を足す）は一致が6件に減り、事実は36件のまま残った。"
        "版c（20字以上つながらないように、ただし固有名詞と数字はそのまま、を足す）は一致が0件になったが、"
        "事実は36項目中34件に減った。慣用句5個の一致は、版b・cではいずれも0件だった。"
    )
    (OUT / "material-match-vs-facts.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def filler_source_detection_chart() -> None:
    """保存指示文に仕込んだ「下限を強制する指定」8個を、3つの頼み方で18回試して
    いくつ見つかったかを、指定の種類ごとに並べた横棒グラフ。

    実測（2026-08-25）。保存指示文3本（受信箱の仕分け／表の点検／記録の要約）に、
    同じ8個の指定を1個ずつ仕込み、3つの頼み方（そのまま聞く／下限だけ挙げて／
    ＋書くことが無い日に何が出るか）× 材料3本 × 各2回 ＝ 18回を通した。
    仕込みには「最大3行」「該当が無い種類はその旨」など安全な8個も混ぜてある
    （下の②の分母）。値は grade.py の集計＋手作業での読み合わせ。
    """
    rows = [
        ("「必ず3つ挙げて」型", 18),
        ("「候補から必ず1つ選んで」型", 16),
        ("「良い点と悪い点を同数で」型", 12),
        ("「原因を3つ書いて」型", 12),
        ("「表の全欄を埋めて」型", 10),
        ("「◯行でまとめて」型", 3),
        ("「5段階で点数を」型", 2),
        ("「各項目に一言添えて」型", 2),
    ]
    label_x, label_w = 18, 232
    plot_x = label_x + label_w
    plot_w = 300
    top = 150
    row_h = 34
    unit = plot_w / 18.0
    bar_h = 16

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "8種類の埋め草のもと、18回でいくつ見つかったか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "保存指示文3本（受信箱の仕分け／表の点検／記録の要約）に、"
        "同じ8個の危険な指定と、8個の安全な指定を1個ずつ仕込んだ。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "3つの頼み方 × 材料3本 × 各2回 ＝ 18回。棒は「見つかった回数」。</text>\n",
        '<text class="t-bad" x="18" y="86">'
        "※ 安全な8個（上限のみの指定）を「危険」と間違えて挙げた回は、"
        "18回×8個＝144件中0件だった。</text>\n",
        '<text class="t-bad" x="18" y="105">'
        "　 見つけた項目の直し方は、すべて「下限を外す・逃げ道を足す」方向。"
        "「言葉を強める」提案は1件も無かった。</text>\n",
    ]
    for v in (0, 6, 12, 18):
        gx = plot_x + v * unit
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + row_h * len(rows) - 18}" stroke-dasharray="3 4"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{gx:.1f}" y="{top - 12}" '
            f'text-anchor="middle">{v}回</text>\n'
        )

    y = top
    for label, val in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty + 5}">{_esc(label)}</text>\n')
        w = max(val * unit, 2.0)
        klass = "bar-new" if val >= 10 else ("bar-old" if val >= 5 else "box-bad")
        parts.append(
            f'<rect class="{klass}" x="{plot_x:.1f}" y="{ty - 11}" '
            f'width="{w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        cls = "t-bad" if val < 5 else "t"
        parts.append(
            f'<text class="{cls}" x="{plot_x + w + 8:.1f}" y="{ty + 2}">{val}/18</text>\n'
        )
        y += row_h

    notes = [
        ("t-xs", "赤い3本（◯行でまとめて／5段階で点数を／各項目に一言添えて）が、見えにくい埋め草のもと。"),
        ("t-xs", "生の返り18回ぶんは docs/evidence/ に全文置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y
    alt = (
        "保存指示文3本に仕込んだ8種類の「下限を強制する指定」を、"
        "3つの頼み方×材料3本×各2回＝18回でいくつ見つけたかを、横棒グラフで並べた図。"
        "「必ず3つ挙げて」型は18回中18回、「候補から必ず1つ選んで」型は16回、"
        "「良い点と悪い点を同数で」型は12回、「原因を3つ書いて」型は12回、"
        "「表の全欄を埋めて」型は10回見つかった。"
        "一方「◯行でまとめて」型は3回、「5段階で点数を」型は2回、"
        "「各項目に一言添えて」型は2回しか見つからず、赤で示している。"
        "安全な8個の指定（上限のみ）を危険と間違えて挙げた回は、18回×8個=144件中0件だった。"
        "見つけた項目の直し方は、すべて「下限を外す・逃げ道を足す」方向で、"
        "「言葉を強める」という提案は1件も無かった。"
    )
    (OUT / "filler-source-detection.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def filler_source_five_scale_chart() -> None:
    """見つけにくかった代表例「5段階で点数をつけてください」を、
    頼み方5通りでいくつ見つけたかを並べた横棒グラフ。

    実測（2026-08-25）。開いて聞く／下限だけ挙げて／＋書くことが無い日に何が出るか
    は各6回（材料3本×2回）。一括で「全部見直して」まで含めて一度に頼むのは
    材料3本×1回＝3回（新規エージェント）。もう一度全部見直してと重ねて聞くのは、
    最初に開いて聞いた3つの会話に、材料ごと1回だけ追加で聞いた。
    """
    rows = [
        ("そのまま開いて聞く", 0, 6),
        ("「下限だけ挙げて」と絞る", 1, 6),
        ("＋書くことが無い日に何が出るか", 1, 6),
        ("一度に「全部見直して」まで頼む", 0, 3),
        ("あとから「もう一度全部見直して」", 3, 3),
    ]
    label_x, label_w = 18, 250
    plot_x = label_x + label_w
    plot_w = 280
    top = 130
    row_h = 40
    unit = plot_w / 6.0
    bar_h = 17

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「5段階で点数をつけてください」は、聞き方でこれだけ変わる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "見つけにくかった8個中の1つを取り出した図。上4つは新規の会話、"
        "いちばん下だけは同じ会話への重ね聞き。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "近くにある「無ければ空欄でよい」という逃げ道は、実は隣の指定にかかっていて、"
        "この指定自身には届いていなかった。</text>\n",
    ]
    for v in (0, 3, 6):
        gx = plot_x + v * unit
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + row_h * len(rows) - 22}" stroke-dasharray="3 4"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{gx:.1f}" y="{top - 12}" '
            f'text-anchor="middle">{v}回</text>\n'
        )

    y = top
    for label, val, denom in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty + 5}">{_esc(label)}</text>\n')
        w = max(val * unit, 2.0)
        klass = "box-good" if val == denom else ("bar-old" if val else "box-bad")
        parts.append(
            f'<rect class="{klass}" x="{plot_x:.1f}" y="{ty - 11}" '
            f'width="{w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        cls = "t-good" if val == denom else ("t" if val else "t-bad")
        parts.append(
            f'<text class="{cls}" x="{plot_x + w + 8:.1f}" y="{ty + 3}">{val}/{denom}</text>\n'
        )
        y += row_h

    notes = [
        ("t-good", "※ 一番下だけ緑＝あとから同じ会話に重ねて聞くと、3つの会話とも見つけた。"),
        ("t-xs", "生の返り（5通り・21回ぶん）は docs/evidence/ に全文置いてある。"),
    ]
    y += 4
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y
    alt = (
        "見つけにくかった埋め草のもとの代表例「5段階で点数をつけてください」を、"
        "頼み方5通りでいくつ見つけたかを並べた横棒グラフ。"
        "そのまま開いて聞くと6回中0回、「下限だけ挙げて」と絞ると6回中1回、"
        "＋書くことが無い日に何が出るかを足しても6回中1回しか見つからなかった。"
        "一度に「全部見直して」まで含めて新規の会話で頼んでも3回中0回。"
        "ところが、最初に開いて聞いた同じ会話に、あとから"
        "「もう一度全部見直して」と重ねて聞くと、3回中3回とも見つけた。"
        "近くにあった「無ければ空欄でよい」という逃げ道は、"
        "実は隣の指定にかかっていて、この指定自身には届いていなかったことが分かった。"
    )
    (OUT / "filler-source-five-scale.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_relative_terms_grid_chart() -> None:
    """絶対日付に直す4版で、触ってはいけない4項目が何回誤変換されたかのマス目。

    実測（2026-08-26・引き継ぎメモ20行・4版×各2回＝8回。独立した
    `claude --safe-mode` サブプロセスに送って機械照合）。変換すべき12件は
    8回とも全問正解（96/96）だったので、ここに出すのは触ってはいけない
    8件のうち、実際に誤変換が出た4件だけ。
    """
    rows = [
        ("「先週号」（固有名詞）", [2, 2, 1, 1]),
        ("「先月比」（比較の言葉）", [2, 2, 2, 0]),
        ("「前年同月比」（同上）", [1, 1, 0, 0]),
        ("「翌月初」（規則）", [0, 1, 0, 0]),
    ]
    cols = ["版a", "版b", "版c", "版d"]
    label_w = 176
    cell_w, cell_h, gap = 118, 34, 10
    top = 157
    pitch = cell_h + gap
    grid_x = 18 + label_w
    right_edge = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_edge <= WIDTH - 18, right_edge

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「先月比」だけは、版を変えても誤変換が消えなかった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "引き継ぎメモ20行（変換すべき日付12件＋触ってはいけない語8件）に、"
        "指示文を4版・各2回＝8回、独立したプロセスに送った。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "版a＝そのまま。版b＝＋「先週/来月まで/最近を禁止」（記事の推奨そのまま）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "版c＝＋基準日と〔基準日不明〕の逃げ道。版d＝＋「○○比は残せ」を明記。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "セルの数＝誤って絶対日付に書き換えた回数（2回中）。0が誤変換なし。</text>\n",
        '<text class="t-sm" x="18" y="121">'
        "※ 変換すべき12件は4版とも8回中8回、96／96件が正解だった（別枠）。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x + cell_w / 2 - 8:.1f}" y="{top - 12}">{name}</text>\n'
        )

    for row_index, (label, values) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(
            f'<text class="t-sm" x="18" y="{y + cell_h / 2 + 5:.0f}">{_esc(label)}</text>\n'
        )
        for col_index, v in enumerate(values):
            x = grid_x + col_index * (cell_w + gap)
            bad = v > 0
            box = "box-bad" if bad else "box-good"
            tone = "t-bad" if bad else "t-good"
            parts.append(
                f'<rect class="{box}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            text = f"{v}／2"
            tx = x + cell_w / 2 - len(text) * 5.4
            parts.append(
                f'<text class="{tone}" x="{tx:.1f}" y="{y + cell_h / 2 + 5:.0f}">{text}</text>\n'
            )

    height = top + len(rows) * pitch + 8 + 21 * 3 + 16
    notes = [
        ("t-xs", "※「先週号」は版c・dで各2回中1回、誤変換せず〔基準日不明〕の逃げ道が働いた（もう1回は誤変換）。"),
        ("t-bad", "※「先月比」は版cまで2回とも誤変換。版dで初めて2回とも0件になった。"),
        ("t-xs", "架空データでの実測。生の返り8通は docs/evidence/ に全文置いてある。"),
    ]
    ny = height - 21 * len(notes) + 5
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "絶対日付に直す指示文4版で、触ってはいけない4項目が2回中何回誤変換されたかのマス目。"
        "先週号は版a・bで2回とも誤変換、版c・dでは2回中1回（もう1回は基準日不明の逃げ道）。"
        "先月比は版a・b・cで2回とも誤変換されたが、比較語を残す指示を足した版dでは2回とも0件。"
        "前年同月比は版a・bで2回中1回、版c・dでは0回。翌月初は版bで2回中1回のみ、他は0回。"
        "変換すべき12件は4版とも8回中8回、96件中96件が正解だった。"
    )
    (OUT / "handoff-relative-terms-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_wrong_touch_total_chart() -> None:
    """触ってはいけない8件（×2回＝16件）のうち、版ごとに誤変換した合計件数。

    実測（2026-08-26）。記事の推奨（先週/来月まで/最近を禁止＝版b）は
    版aより件数が減らず、むしろ1件増えた。減ったのは基準日と逃げ道を
    足した版c、0件近くまで落ちたのは誤変換の対象そのもの
    （比較の言葉）を名指しした版dだけだった。
    """
    rows = [
        "版a：そのまま",
        "版b：＋「先週/来月まで/最近」を禁止",
        "版c：＋基準日と〔基準日不明〕",
        "版d：＋「○○比は残せ」を明記",
    ]
    values = [5, 6, 3, 1]
    label_w = 190
    left = 18 + label_w
    right = WIDTH - 60
    span = right - left
    axis_max = 8
    scale = span / axis_max
    top = 128
    row_h = 34
    bar_h = 18

    def px(n: float) -> float:
        return left + n * scale

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "記事の推奨（版b）は減らなかった。減らしたのは基準日と、名指しの一文</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "触ってはいけない8件×2回＝16件のうち、絶対日付へ誤って書き換えた件数の合計。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "版b＝このサイトの別記事が勧める「先週/来月まで/最近を禁止」をそのまま追加した版。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "版d＝誤変換の対象そのもの（「○○比」のような比較の言葉）を名指しして残すよう頼んだ版。</text>\n",
    ]
    for i in range(0, axis_max + 1, 2):
        gx = px(i)
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + len(rows) * row_h - 10}" stroke-width="1" opacity="0.3"/>\n'
        )
        parts.append(f'<text class="t-xs" x="{gx - 3:.1f}" y="{top - 12}">{i}</text>\n')

    y = top
    for label, value in zip(rows, values):
        by = y + (row_h - bar_h) / 2
        parts.append(
            f'<text class="t-xs" x="18" y="{y + row_h / 2 + 4:.0f}">{_esc(label)}</text>\n'
        )
        bar_cls = "bar-out" if value >= 5 else ("bar-in" if value >= 2 else "bar-new")
        bw = max(2.0, value * scale)
        parts.append(
            f'<rect class="{bar_cls}" x="{left}" y="{by:.1f}" '
            f'width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{left + bw + 8:.1f}" y="{by + bar_h - 4:.1f}">{value}／16件</text>\n'
        )
        y += row_h

    height = y + 16 + 21 * 2 + 12
    notes = [
        ("t-xs", "※ 変換すべき12件×2回＝24件はどの版も24／24で正解（この図には含めない）。"),
        ("t-xs", "架空データでの実測。生の返り8通は docs/evidence/ に全文置いてある。"),
    ]
    ny = y + 20
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "触ってはいけない8件×2回＝16件のうち、版ごとに絶対日付へ誤って書き換えた件数の合計を示す横棒グラフ。"
        "版a（そのまま）は5件、版b（先週/来月まで/最近を禁止を追加）は6件でむしろ増え、"
        "版c（基準日と基準日不明の逃げ道を追加）は3件に減り、"
        "版d（比較の言葉は残せと名指しした）は1件まで下がった。"
        "変換すべき12件×2回＝24件は、どの版も24件中24件が正解だった。"
    )
    (OUT / "handoff-wrong-touch-total.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def note_fee_payout_waterfall_chart() -> None:
    """1,000円の記事がクレカ決済で1件売れたとき、振込までに3回引かれる様子を階段状に見せる。

    実測ではなく原文の式の転記（2026-08-25確認）。事務手数料5%→プラットフォーム利用料10%
    （残額に掛ける）→振込手数料270円/回、の順。
    """
    stages = [
        ("売上", 1000, ""),
        ("事務手数料 5%（クレカ決済）を引く", 950, "－50円"),
        ("プラットフォーム利用料 10% を引く", 855, "－95円"),
        ("振込手数料 270円/回 を引く", 585, "－270円"),
    ]
    label_x = 18
    bar_x = 280
    max_bar_w = 300
    top = 108
    row_h = 46

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "1,000円の売上から、振込までに3回引かれる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "クレジットカード決済で1,000円の記事が1件売れた場合。原文の公式例の順に、"
        "事務手数料→プラットフォーム利用料→振込手数料の順で当てはめた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "プラットフォーム利用料は「売上そのもの」ではなく「事務手数料を引いた残り」に掛かる。"
        "</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 20}">残額（円）</text>\n',
    ]

    y = top
    for label, amount, delta in stages:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w = max(4, round(max_bar_w * amount / 1000))
        cls = "bar-out" if amount in (1000, 585) else "bar-in"
        parts.append(
            f'<rect class="{cls}" x="{bar_x}" y="{ty - 15}" width="{w}" height="20" rx="3"/>\n'
        )
        amount_label = f"{amount:,}円" + (f"（{delta}）" if delta else "")
        parts.append(
            f'<text class="t-strong" x="{bar_x + w + 8}" y="{ty}">{_esc(amount_label)}</text>\n'
        )
        y += row_h

    y += 8
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="678" height="40" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 25}">'
        "振込額 585円（1,000円の58.5%）。振込手数料270円は1回あたりなので、まとめて申請するほど比率が下がる。</text>\n"
    )
    y += 40

    notes = [
        ("t-sm", "※ 事務手数料の料率は決済手段で変わる（クレカ以外は次の図）。この図はクレカ決済の場合。"),
        ("t-xs", "原文の公式例（2026-08-25確認）から計算。料率は変わるため、使う前に開いて確かめること。"),
    ]
    y += 24
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y + 10
    alt = (
        "noteで1,000円の記事がクレジットカード決済で1件売れたときの振込額の内訳を示す図。"
        "売上1,000円から事務手数料5%の50円が引かれて950円になり、"
        "そこからプラットフォーム利用料10%の95円が引かれて855円になり、"
        "さらに振込手数料270円が1回ぶん引かれて、最終的な振込額は585円になる。"
        "1,000円に対して58.5パーセントが手元に残る計算。"
        "事務手数料の料率は決済手段によって変わり、クレジットカード5パーセント・携帯キャリア15パーセント・"
        "PayPay 7パーセント・Amazon Pay 7パーセント・noteポイント10パーセント・PayPal 6.5パーセントで、"
        "この図はクレジットカード決済の場合を示している。"
    )
    (OUT / "note-fee-payout-waterfall.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def note_fee_rate_match_chart() -> None:
    """noteの決済手段別の事務手数料6種類のうち、AIの回答が正しく言えた個数を6回ぶん並べる。

    実測（2026-08-26・「noteで有料記事を売ると手数料はいくら引かれますか」を版2通り×各3回）。
    真値の6種類＝クレカ5%・キャリア15%・PayPay 7%・Amazon Pay 7%・noteポイント10%・PayPal 6.5%。
    値は check.py の A/B節。
    """
    rows = [
        ("① 率を貼らずに聞く・1回目", 1),
        ("① 率を貼らずに聞く・2回目", 2),
        ("① 率を貼らずに聞く・3回目", 2),
        ("② 出典URLも書いてと足す・1回目", 2),
        ("② 出典URLも書いてと足す・2回目", 2),
        ("② 出典URLも書いてと足す・3回目", 2),
    ]
    label_x = 18
    plot_x = 380
    plot_w = 200
    total = 6
    top = 150
    row_h = 34

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "6種類ある決済手段のうち、6回とも2つ止まり</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "「noteで有料記事を売ると手数料はいくら引かれますか」を、率を貼らずに3回・"
        "出典URLも足して3回、計6回聞いた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "下の数は、6種類の事務手数料（クレカ5%・キャリア15%・PayPay 7%・Amazon Pay 7%・"
        "noteポイント10%・PayPal 6.5%）のうち、</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "正しく出てきた個数。</text>\n",
        f'<text class="t-xs" x="{plot_x}" y="{top - 22}">6種類のうち一致した数</text>\n',
    ]

    y = top
    for label, n in rows:
        ty = y + 15
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w = max(4, round(plot_w * n / total))
        cls = "bar-in"
        parts.append(
            f'<rect class="{cls}" x="{plot_x}" y="{ty - 13}" width="{w}" height="18" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{plot_x + w + 8}" y="{ty}">{n}/{total}種</text>\n'
        )
        y += row_h

    y += 10
    parts.append(f'<rect class="box-bad" x="18" y="{y}" width="678" height="44" rx="6"/>\n')
    parts.append(
        f'<text class="t-bad" x="34" y="{y + 18}">'
        "🚨 6回を通じて出たのは、クレジットカードと携帯キャリアの2つだけ。</text>\n"
    )
    parts.append(
        f'<text class="t-bad" x="34" y="{y + 36}">'
        "PayPay・Amazon Pay・noteポイント・PayPalは、6回とも1回も出なかった。</text>\n"
    )
    y += 44

    notes = [
        ("t-sm", "※ 「購読者の決済手段によります（クリエイターは選べない）」の一言は、率を貼らずに聞いた3回では一度も出なかった。"),
        ("t-xs", "架空の実測ではなくAIの知識そのものを聞いた6回。送った指示文と返りは docs/evidence/ に置いてある。"),
    ]
    y += 24
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y + 10
    alt = (
        "noteの決済手段別の事務手数料6種類（クレジットカード5パーセント・携帯キャリア15パーセント・"
        "PayPay 7パーセント・Amazon Pay 7パーセント・noteポイント10パーセント・PayPal 6.5パーセント）のうち、"
        "AIの回答に正しく出てきた個数を6回ぶん並べた棒グラフ。"
        "率を貼らずに聞いた3回はそれぞれ1個・2個・2個、出典URLを求めた3回はいずれも2個で、"
        "6回ともクレジットカードと携帯キャリアの2つ止まりだった。"
        "PayPay・Amazon Pay・noteポイント・PayPalは6回とも0回だった。"
        "「決済手段は購読者が選ぶ」という原文の一言は、率を貼らずに聞いた3回では一度も出なかった。"
    )
    (OUT / "note-fee-rate-match.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def kindle_disclosure_scenario_grid_chart() -> None:
    """4つの作業パターンについて、AIの判定が原文の線と一致したかを格子で見せる。

    実測（2026-08-26・4シナリオを聞く2版×各2回＝16判定）。値は check.py。
    真値: ①要申告 ②不要 ③不要 ④要申告（原文＝KDPコンテンツガイドライン、2026-08-25確認）。
    """
    scenarios = [
        "① AIに本文を書かせ、自分で大幅に編集",
        "② 自分で本文を書き、AIは校正だけ",
        "③ AIでアイデア出し、文章は自分で執筆",
        "④ 表紙の画像をAIで生成",
    ]
    truth = ["要申告", "不要", "不要", "要申告"]
    runs = ["①そのまま聞く・1回目", "①そのまま聞く・2回目", "②原文を貼る・1回目", "②原文を貼る・2回目"]
    # 全16判定が真値と一致（実測結果）
    grid = [[True] * 4 for _ in runs]

    label_w = 190
    col_w = 118
    top = 132
    row_h = 26

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "4つの場面×4通りの聞き方＝16判定。全16判定が原文の線と一致</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "真値（KDPコンテンツガイドライン・2026-08-25確認）＝①要申告 ②不要 ③不要 ④要申告。"
        "</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「大幅に編集した」①も、4回とも正しく「要申告」側に判定した。</text>\n",
    ]

    for i, s in enumerate(scenarios):
        x = 18 + label_w + i * col_w
        parts.append(
            f'<text class="t-xs" x="{x + col_w // 2}" y="{top - 34}" text-anchor="middle">{_esc(s[:2])}</text>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{x + col_w // 2}" y="{top - 18}" text-anchor="middle">（真値{_esc(truth[i])}）</text>\n'
        )

    y = top
    for r, run in enumerate(runs):
        ty = y + 17
        parts.append(f'<text class="t" x="18" y="{ty}">{_esc(run)}</text>\n')
        for i in range(4):
            x = 18 + label_w + i * col_w
            ok = grid[r][i]
            cls = "box-good" if ok else "box-bad"
            tcls = "t-good" if ok else "t-bad"
            parts.append(
                f'<rect class="{cls}" x="{x + 14}" y="{ty - 15}" width="{col_w - 28}" height="20" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{tcls}" x="{x + col_w // 2}" y="{ty}" text-anchor="middle">一致</text>\n'
            )
        y += row_h + 6

    y += 10
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="678" height="40" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 25}">'
        "16/16判定が一致。ただし根拠の一字一句の引用は2回とも「引用できません」（次の図）。</text>\n"
    )
    y += 40 + 18

    height = y + 8
    alt = (
        "Kindleダイレクトパブリッシングで、4つの作業パターンについて申告が必要か不要かを"
        "AIに4通りの聞き方（率を貼らずに聞く2回・原文を貼って聞く2回）で聞いた結果の格子図。"
        "AIに本文を書かせて自分で大幅に編集した場合は申告が必要、"
        "自分で本文を書きAIには校正だけしてもらった場合は申告不要、"
        "AIにアイデア出しを手伝ってもらい最終的な文章はすべて自分で書いた場合は申告不要、"
        "表紙の画像をAIで生成した場合は申告が必要というのが原文の線であり、"
        "4通りの聞き方すべてで、4つの場面すべての判定が原文の線と一致した。合計16判定中16判定が一致。"
    )
    (OUT / "kindle-disclosure-scenario-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def kindle_disclosure_no_citation_chart() -> None:
    """判定は当たっても、根拠の一字一句の引用と出典URLは出てこないことを示す。

    実測（2026-08-26）。値は check.py。
    """
    rows = [
        ("4シナリオを聞いた4回で、出典URLを書いた回", 0, 4),
        ("根拠の一字一句の引用を求めた2回で、引用できた回", 0, 2),
        ("根拠の一字一句の引用を求めた2回で、正直に「引用できません」と答えた回", 2, 2),
    ]
    label_x = 18
    plot_x = 460
    plot_w = 130
    top = 110
    row_h = 48

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "判定は当たっても、原文の言葉そのものは持っていない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "16判定は原文と一致したが、それとは別に「根拠を一字一句引用して」と求めると別の顔を見せる。"
        "</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "同じ連載のnoteの回では、出典URLを求めると実在しないURLが3回とも返った"
        "（前の回を参照）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "こちらは、無いものは「無い」と答えた。</text>\n",
    ]

    y = top
    for label, n, total in rows:
        ty = y + 15
        # ラベルは折り返さず、複数行に分けて置く
        words = label
        parts.append(f'<text class="t-sm" x="{label_x}" y="{ty}">{_esc(words)}</text>\n')
        w = max(4, round(plot_w * n / total)) if total else 4
        cls = "bar-old" if n == 0 else "bar-out"
        parts.append(
            f'<rect class="{cls}" x="{plot_x}" y="{ty + 6}" width="{w}" height="18" rx="3"/>\n'
        )
        tcls = "t-bad" if n == 0 else "t-good"
        parts.append(
            f'<text class="{tcls}" x="{plot_x + w + 8}" y="{ty + 20}">{n}/{total}回</text>\n'
        )
        y += row_h

    notes = [
        ("t-xs", "架空の実測ではなくAIの知識そのものを聞いた回。生の返りと照合コードは docs/evidence/ に全文置いてある。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y + 10
    alt = (
        "Kindleダイレクトパブリッシングの申告について、AIの判定は原文と一致したが、"
        "根拠の一字一句の引用や出典URLは出てこないことを示す図。"
        "4シナリオを聞いた4回のうち出典URLを書いた回は0回。"
        "根拠の一字一句の引用を求めた2回のうち、引用できた回は0回で、"
        "正直に「引用できません」と答えた回が2回。"
        "同じ連載のnoteの回では出典URLを求めると実在しないURLが3回とも返ったのに対し、"
        "こちらは無いものは無いと答えた。"
    )
    (OUT / "kindle-disclosure-no-citation.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def note_payout_version_comparison_chart() -> None:
    """1,000円の記事が3件売れたときの手取りを、3通りの聞き方で比較する。

    実測（2026-08-26・各3回）。真の幅は決済手段6種類での計算結果
    （携帯キャリア2,025円〜クレジットカード2,295円）。値は check.py。
    """
    axis_lo, axis_hi = 1900, 2650
    axis_x, axis_w = 160, 380

    def sx(v: int) -> int:
        return axis_x + round(axis_w * (v - axis_lo) / (axis_hi - axis_lo))

    rows = [
        ("① 率を貼らずに聞く（3回とも別々の値）", [(2400, 2600), (2300, 2550), (2300, 2600)], False),
        ("② 料率表を貼るだけ", [(2025, 2295)] * 3, True),
        ("③ ②＋「決まらない変数があれば挙げて」", [(2025, 2295)] * 3, True),
    ]

    top = 130
    group_h = 74

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "率を貼らない3回は、真の幅からズレる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "「noteで1,000円の有料記事が3件売れました。手取りはいくらになりますか」を3通りの聞き方で、"
        "各3回。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "真の幅（決済手段6種類での計算・携帯キャリア決済〜クレジットカード決済）は"
        "2,025円〜2,295円。</text>\n",
    ]

    # 真値の帯を全体の背景に薄く描く
    true_x0, true_x1 = sx(2025), sx(2295)
    parts.append(
        f'<rect class="box-good" x="{true_x0}" y="{top - 14}" width="{true_x1 - true_x0}" '
        f'height="{len(rows) * group_h + 6}" rx="4" opacity="0.35"/>\n'
    )
    parts.append(
        f'<text class="t-xs" x="{(true_x0 + true_x1) // 2}" y="{top - 20}" text-anchor="middle">'
        "真の幅</text>\n"
    )

    y = top
    for label, ranges, matched in rows:
        parts.append(f'<text class="t" x="18" y="{y + 12}">{_esc(label)}</text>\n')
        for i, (lo, hi) in enumerate(ranges):
            ry = y + 24 + i * 16
            x0, x1 = sx(lo), sx(hi)
            parts.append(
                f'<line class="line" x1="{x0}" y1="{ry}" x2="{x1}" y2="{ry}" '
                f'stroke="{"#1a7f37" if matched else "#b02020"}" stroke-width="5" '
                f'stroke-linecap="round"/>\n'
            )
            tcls = "t-good" if matched else "t-bad"
            parts.append(
                f'<text class="{tcls}" x="{x1 + 8}" y="{ry + 4}">{lo:,}〜{hi:,}円</text>\n'
            )
        y += group_h

    y += 6
    parts.append(f'<rect class="box-bad" x="18" y="{y}" width="678" height="40" rx="6"/>\n')
    parts.append(
        f'<text class="t-bad" x="34" y="{y + 25}">'
        "🚨 ①の3本は、真の幅（緑の帯）と1本も重ならない。独自に発明した料率で計算しているため。</text>\n"
    )
    y += 40

    notes = [
        ("t-sm", "※ ②③は3回とも、真値と1円単位で一致（クレジットカード2,295円〜携帯キャリア2,025円）。"),
        ("t-xs", "架空の実測ではなくAIの知識そのものを聞いた回。生の返りと照合コードは docs/evidence/ に全文置いてある。"),
    ]
    y += 24
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y + 8
    alt = (
        "noteで1,000円の記事が3件売れたときの手取りを、率を貼らずに聞いた3回・"
        "料率表を貼って聞いた3回・料率表に加えて決まらない変数を挙げてと頼んだ3回で比較した図。"
        "真の幅は2,025円から2,295円で、決済手段6種類（クレジットカード・携帯キャリア・PayPay・"
        "Amazon Pay・noteポイント・PayPal）での計算結果の範囲を示す。"
        "率を貼らない3回は2,300円台から2,600円台の、真の幅と重ならないズレた独自の範囲を返した。"
        "料率表を貼った6回（版2・版3）は3回ずつとも真の幅と1円単位で一致した。"
    )
    (OUT / "note-payout-version-comparison.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def kindle_royalty_invented_band_chart() -> None:
    """70%を選べる価格帯の上限を、AIが3回とも同じ方向に間違えることを示す。

    実測（2026-08-26・各3回）。値は docs/evidence/kindle-royalty-formula.md の判定コード。
    真値＝kdp.amazon.co.jp「日本のマーケットプレイス向けの価格設定」(G201849770)
    ＝70%は250円〜1,650円（税込）・35%は99円〜20,000円（税込）。
    """
    lo_axis, hi_axis = 0, 1800
    plot_x, plot_w = 200, 420
    scale = plot_w / (hi_axis - lo_axis)

    def px(yen: float) -> float:
        return plot_x + (yen - lo_axis) * scale

    rows = [
        ("原文（KDPヘルプ）", 250, 1650, "250円〜1,650円", "bar-out", "t-good"),
        ("そのまま聞いた1回目", 250, 1250, "250円〜1250円", "bar-old", "t-bad"),
        ("そのまま聞いた2回目", 250, 1250, "250円〜1250円", "bar-old", "t-bad"),
        ("そのまま聞いた3回目", 99, 1250, "99円〜1,250円", "bar-old", "t-bad"),
    ]

    top = 116
    pitch, bar_h = 30, 17
    axis_y = top + len(rows) * pitch + 6

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "上限を3回とも同じ方向に間違える。しかも下限は1回だけずれる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "500円のKindle本の印税を、原文を貼らずに聞いた3回。"
        "3回とも「70%を選べる価格帯」を数字で言い切った。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "上限は3回とも1,250円。原文は1,650円で、400円ぶん低く見積もっている。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "3回目の下限99円は、35%オプションの下限（99円）。"
        "隣の行の数字が混ざったように見える。</text>\n",
    ]

    y = top
    for label, lo, hi, note, bar_cls, txt_cls in rows:
        ty = y + 13
        parts.append(f'<text class="t-sm" x="18" y="{ty + 12}">{_esc(label)}</text>\n')
        x0, x1 = px(lo), px(hi)
        parts.append(
            f'<rect class="{bar_cls}" x="{x0:.1f}" y="{ty}" '
            f'width="{x1 - x0:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="{txt_cls}" x="{x1 + 8:.1f}" y="{ty + 13}">{_esc(note)}</text>\n'
        )
        y += pitch

    parts.append(
        f'<path class="line" d="M{plot_x} {axis_y} L{px(hi_axis):.1f} {axis_y}"/>\n'
    )
    for tick in (0, 500, 1000, 1500, 1800):
        tx = px(tick)
        parts.append(f'<path class="line" d="M{tx:.1f} {axis_y} L{tx:.1f} {axis_y + 5}"/>\n')
        parts.append(f'<text class="t-xs" x="{tx - 14:.1f}" y="{axis_y + 18}">{tick}円</text>\n')

    y = axis_y + 40
    for text in (
        "500円（今回聞いた価格）は、原文の範囲にも3回の答えにも入る。"
        "つまり500円で試すかぎり、この間違いは表に出ない。",
        "原文の確認日 2026-08-26。価格帯は税込。"
        "生の返りと判定コードは docs/evidence/ に全文置いてある。",
    ):
        parts.append(f'<text class="t-xs" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 18

    height = y + 6
    alt = (
        "500円のKindle本の印税を聞いた実測で、70%を選べる価格帯の上限をAIが3回とも"
        "間違えたことを示す図。原文では250円から1,650円（税込）だが、"
        "そのまま聞いた3回は250円から1250円、250円から1250円、99円から1250円と答えた。"
        "上限は3回とも1,250円で、原文より400円低い。"
        "3回目の下限99円は35%オプションの下限と一致する。"
        "500円はどの範囲にも入るので、500円で試すかぎりこの間違いは表に出ない。"
    )
    (OUT / "kindle-royalty-invented-band.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def kindle_royalty_version_grid_chart() -> None:
    """原文を貼るかどうかで、何が変わって何が変わらないかを判定ごとに並べる。

    実測（2026-08-26・版A=そのまま聞く3回／版B=原文を貼って聞く3回）。
    値は docs/evidence/kindle-royalty-formula.md の判定コード（正規表現照合）。
    """
    rows = [
        ("35%と70%の選択制に触れた", 3, 3),
        ("配信コストに触れた", 3, 3),
        ("10MBルールに触れた", 1, 3),
        ("10MBルールを原文どおり（引かれない）", 0, 3),
        ("日本の70%条件＝KDPセレクトと正しく結んだ", 0, 3),
        ("70%の価格帯を数字で言い切らなかった（言い切った3回は上限が誤り）", 0, 3),
        ("渡していないことを、資料に無いと断った", 0, 3),
    ]
    label_x = 18
    col_a, col_b = 470, 590
    bar_w = 84
    top = 128
    row_h = 40

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "原文を貼ると直るもの、貼らなくても出るもの</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ質問を、そのまま聞いた3回（版A）と、KDPの原文を貼って聞いた3回（版B）。"
        "各項目は3回中の該当回数。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "配信コストは貼らなくても出る。落ちるのは、その配信コストが"
        "日本では10MB以上だと引かれないという例外のほう。</text>\n",
        f'<text class="t-sm" x="{col_a}" y="{top - 14}">版A そのまま</text>\n',
        f'<text class="t-accent" x="{col_b}" y="{top - 14}">版B 原文あり</text>\n',
    ]

    y = top
    for label, a, b in rows:
        ty = y + 14
        parts.append(f'<text class="t-sm" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        for col, n, cls in ((col_a, a, "bar-old"), (col_b, b, "bar-out")):
            w = max(4, round(bar_w * n / 3))
            parts.append(
                f'<rect class="{cls}" x="{col}" y="{ty + 6}" width="{w}" height="15" rx="3"/>\n'
            )
            # ⚠️ 3回そろって初めて緑。1/3 を緑にすると、10MBに1回だけ触れて
            #    向きを間違えた回が合格に見える（独立レビューで発覚）。
            tcls = "t-good" if n == 3 else "t-bad"
            parts.append(
                f'<text class="{tcls}" x="{col + w + 6}" y="{ty + 18}">{n}/3</text>\n'
            )
        y += row_h

    y += 4
    for text in (
        "⚠️ 「触れた」は、その語が返りに出たかどうかだけを機械照合したもの。"
        "正しく使えたかは別の行で数えている。",
        "実測 2026-08-26・全6回。生の返りと判定コードは docs/evidence/ に全文置いてある。",
    ):
        parts.append(f'<text class="t-xs" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 18

    height = y + 6
    alt = (
        "KDPの印税をAIに計算させた実測で、原文を貼ると直る項目と、貼らなくても出る項目を並べた図。"
        "3回中の該当回数で、版Aはそのまま聞いた3回、版Bは原文を貼って聞いた3回。"
        "35%と70%の選択制に触れたのは版A3回・版B3回。配信コストに触れたのは両方とも3回。"
        "10MBルールに触れたのは版A1回・版B3回で、原文どおり引かれないと述べたのは版A0回・版B3回。"
        "日本の70%条件をKDPセレクトと正しく結んだのは版A0回・版B3回。"
        "70%の価格帯を数字で言い切らなかったのは版A0回・版B3回で、"
        "言い切った3回とも上限が原文と違っていた。"
        "渡していないことを書かれていないと断ったのは版A0回・版B3回。"
    )
    (OUT / "kindle-royalty-version-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_summary_format_drift_grid_chart() -> None:
    """8ルールのうち、版によって崩れたのは形式の3つだけ（ルール⑧は崩れず）。

    実測（2026-08-27・毎朝の日報作成に8ルールを渡し、材料2本×2回＝
    のべ4試行。版a=会話を続ける／版b=要約して新しい会話に貼る／
    版c=対照版・ルール原文を貼りなおす）。1回も出番の無かったルール⑧
    （情報不足・矛盾の行を保留にする）は24／24件で崩れなかった一方、
    形式まわりの3項目は版bに集中して崩れた。
    """
    rows = [
        ("見出しが12字を超えた", [0, 2, 0]),
        ("IDの通し番号を落とした", [0, 1, 0]),
        ("合計の後に新しい話題を足した", [1, 3, 0]),
    ]
    cols = ["版a 続ける", "版b 要約して貼る", "版c 貼りなおす"]
    label_w = 220
    cell_w, cell_h, gap = 140, 34, 8
    top = 150
    pitch = cell_h + gap
    grid_x = 18 + label_w
    right_edge = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_edge <= WIDTH - 18, right_edge

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "崩れたのはルールではなく、形式だった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "毎朝の日報作成に8ルールを渡し、材料2本×2回＝4試行を独立したプロセスに送った。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "版a＝会話を切らずに続ける。版b＝「引き継ぎメモを作って」に応じた返りだけを新しい会話に貼る。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "版c＝対照版。8ルールの原文をそのまま新しい会話に貼りなおす。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "セルの数＝4試行中に崩れた回数。0が崩れなし。</text>\n",
        '<text class="t-sm" x="18" y="121">'
        "※ ①②④⑤⑥⑦・とくに1回も出番の無かった⑧（保留処理）は、どの版も4試行24／24件で崩れなかった（別枠）。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x + cell_w / 2 - len(name) * 3.2:.1f}" y="{top - 12}">{_esc(name)}</text>\n'
        )

    for row_index, (label, values) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(
            f'<text class="t-sm" x="18" y="{y + cell_h / 2 + 5:.0f}">{_esc(label)}</text>\n'
        )
        for col_index, v in enumerate(values):
            x = grid_x + col_index * (cell_w + gap)
            bad = v > 0
            box = "box-bad" if bad else "box-good"
            tone = "t-bad" if bad else "t-good"
            parts.append(
                f'<rect class="{box}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            text = f"{v}／4"
            tx = x + cell_w / 2 - len(text) * 5.4
            parts.append(
                f'<text class="{tone}" x="{tx:.1f}" y="{y + cell_h / 2 + 5:.0f}">{text}</text>\n'
            )

    height = top + len(rows) * pitch + 8 + 21 * 2 + 16
    notes = [
        ("t-bad", "※「見出しが12字を超えた」の2回は39字・21字——上限の2〜3倍だった。"),
        ("t-xs", "架空データでの実測。生の返り16通は docs/evidence/ に全文置いてある。"),
    ]
    ny = height - 21 * len(notes) + 5
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "毎朝の日報作成に8ルールを渡した実測で、版ごとに何回崩れたかを示すマス目。"
        "見出しが12字を超えたのは版aで0/4・版bで2/4・版cで0/4。"
        "IDの通し番号を落としたのは版aで0/4・版bで1/4・版cで0/4。"
        "合計の後に新しい話題を足したのは版aで1/4・版bで3/4・版cで0/4。"
        "1回も出番の無かったルール⑧（保留処理）は、どの版も4試行24/24件で崩れなかった。"
    )
    (OUT / "handoff-summary-format-drift-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_summary_heading_length_chart() -> None:
    """見出しの字数を試行ごとに並べる。上限12字を超えたのは版bだけ。

    実測（2026-08-27）。①見出しは全角12字以内、という同じルールを
    渡しても、版bだけが39字・21字という、本文の説明文のような
    見出しを2回返した。
    """
    trials = ["材料1・1回目", "材料1・2回目", "材料2・1回目", "材料2・2回目"]
    data = {
        "版a 続ける": [11, 7, 5, 7],
        "版b 要約して貼る": [39, 5, 7, 21],
        "版c 貼りなおす": [7, 5, 2, 7],
    }
    label_w = 108
    left = 18 + label_w
    right = WIDTH - 60
    span = right - left
    axis_max = 40
    scale = span / axis_max
    top = 150
    group_h = 96
    bar_h = 16
    bar_gap = 6

    def px(n: float) -> float:
        return left + n * scale

    limit_x = px(12)

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "見出しが12字を超えたのは、版bの2回だけ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ「見出しは全角12字以内」というルールを渡した、材料2本×2回＝4試行の見出しの字数。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "版b（要約して新しい会話に貼る）だけが、本文の説明文のような見出しを返す回があった。</text>\n",
    ]

    y = top
    for trial, label in zip(trials, [None] * 4):
        parts.append(f'<text class="t-strong" x="18" y="{y - 8}">{_esc(trial)}</text>\n')
        row_y = y
        for name, values in data.items():
            v = values[trials.index(trial)]
            over = v > 12
            cls = "bar-out" if not over else "bar-old"
            parts.append(
                f'<text class="t-xs" x="18" y="{row_y + bar_h - 4}">{_esc(name)}</text>\n'
            )
            bw = max(2.0, v * scale)
            box = "box-bad" if over else "box-good"
            parts.append(
                f'<rect class="{box}" x="{left}" y="{row_y}" '
                f'width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
            )
            tone = "t-bad" if over else "t-good"
            parts.append(
                f'<text class="{tone}" x="{left + bw + 8:.1f}" y="{row_y + bar_h - 3:.1f}">{v}字</text>\n'
            )
            row_y += bar_h + bar_gap
        y += group_h

    total_height = top + 4 * group_h
    parts.append(
        f'<path class="line" d="M{limit_x:.1f} {top - 20} L{limit_x:.1f} {total_height - 20}" '
        f'stroke-width="1.4" stroke-dasharray="4 3"/>\n'
    )
    parts.append(f'<text class="t-xs" x="{limit_x - 10:.1f}" y="{top - 26}">上限12字</text>\n')

    height = total_height + 8 + 21 * 2
    notes = [
        ("t-bad", "※ 版bの2回（39字・21字）は、上限の2〜3倍——見出しではなく説明文になっていた。"),
        ("t-xs", "架空データでの実測。生の返り12通は docs/evidence/ に全文置いてある。"),
    ]
    ny = height - 21 * len(notes) + 5
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "毎朝の日報作成で見出しの字数を試行ごとに並べた横棒グラフ。上限12字に破線を引いてある。"
        "材料1・1回目は版a11字・版b39字・版c7字。材料1・2回目は版a7字・版b5字・版c5字。"
        "材料2・1回目は版a5字・版b7字・版c2字。材料2・2回目は版a7字・版b21字・版c7字。"
        "版bだけ、39字と21字という上限の2〜3倍の見出しを2回返した。他はすべて12字以内だった。"
    )
    (OUT / "handoff-summary-heading-length.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def job_ai_policy_verdict_chart() -> None:
    """AI利用が一言も書かれていない募集文で、頼み方ごとに可否を断定した回数を示す。

    実測（2026-08-27・各2回）。値は docs/evidence/job-ai-policy-check.md の判定コード。
    「断定」＝可否のどちらかを判断語で答えたこと（真値＝募集文には何も書かれていない）。
    """
    rows = [
        ("そのまま聞く", 2, "留保つき許容/自作グレー判定", "bar-old", "t-bad"),
        ("抜き出すだけを頼む", 0, "「書かれていない」", "bar-out", "t-good"),
        ("＋確認文の下書き", 0, "「書かれていない」", "bar-out", "t-good"),
        ("＋規約を別枠で挙げる", 0, "「書かれていない」", "bar-out", "t-good"),
    ]

    plot_x, plot_w = 230, 380
    scale = plot_w / 2  # 0〜2回

    def px(n: float) -> float:
        return plot_x + n * scale

    top = 108
    pitch, bar_h = 34, 18
    axis_y = top + len(rows) * pitch + 6

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "AI利用が一言も書かれていない募集文でも、そのまま聞くと判断が生まれる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "同じ募集文（AI利用について何も書いていない）に、頼み方だけを変えて2回ずつ実測。"
        "縦軸＝可否を断定した回数。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "真値＝募集文には何も書かれていない。正しい答えは「書かれていない」で、"
        "可否のどちらにも決めないこと。</text>\n",
    ]

    y = top
    for label, n, note, bar_cls, txt_cls in rows:
        ty = y + 13
        parts.append(f'<text class="t-sm" x="18" y="{ty + 12}">{_esc(label)}</text>\n')
        x0, x1 = px(0), px(n)
        w = max(4, x1 - x0)
        parts.append(
            f'<rect class="{bar_cls}" x="{x0:.1f}" y="{ty}" '
            f'width="{w:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="{txt_cls}" x="{x0 + w + 8:.1f}" y="{ty + 13}">{n}/2</text>\n'
        )
        y += pitch

    parts.append(
        f'<path class="line" d="M{plot_x} {axis_y} L{px(2):.1f} {axis_y}"/>\n'
    )
    for tick in (0, 1, 2):
        tx = px(tick)
        parts.append(f'<path class="line" d="M{tx:.1f} {axis_y} L{tx:.1f} {axis_y + 5}"/>\n')
        parts.append(f'<text class="t-xs" x="{tx - 6:.1f}" y="{axis_y + 18}">{tick}回</text>\n')

    y = axis_y + 40
    for text in (
        "そのまま聞いた2回＝1回は留保つき許容、1回は自作のグレー判定。",
        "抜き出すだけの3版は、いずれも2回とも「書かれていない」。",
        "実測 2026-08-27・全32回（募集文4パターン×頼み方4通り×2回）。"
        "生の返りと判定コードは docs/evidence/ に全文置いてある。",
    ):
        parts.append(f'<text class="t-xs" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 18

    height = y + 6
    alt = (
        "AI利用について何も書かれていない募集文に4通りの頼み方をした実測で、"
        "可否を断定した回数を版ごとに示す図。そのまま聞いた版は2回中2回で可否を断定した"
        "（1回は留保つきの許容、1回は自作のグレー判定）。抜き出すだけを頼んだ版・"
        "確認文の下書きを頼んだ版・規約を別枠で挙げさせた版は、いずれも2回中0回で、"
        "2回とも「書かれていない」と正しく答えた。"
    )
    (OUT / "job-ai-policy-verdict-vs-version.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def job_ai_policy_v4_citation_chart() -> None:
    """規約を別枠で挙げさせた頼み方（版④）で、出典を辞退した回数と作り話した回数を示す。

    実測（2026-08-27・全8回＝4群×各2回）。値は docs/evidence/job-ai-policy-check.md の集計⑤。
    架空の募集文にはプラットフォーム名を書いていないため、真値＝出典は挙げられないはず。
    """
    rows = [
        ("実在しない規約を作り話した", 0, "bar-old", "t-good"),
        ("「特定できない」と正直に辞退した", 8, "bar-out", "t-good"),
    ]

    plot_x, plot_w = 260, 350
    scale = plot_w / 8  # 0〜8回

    def px(n: float) -> float:
        return plot_x + n * scale

    top = 112
    pitch, bar_h = 34, 18
    axis_y = top + len(rows) * pitch + 6

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "版④（規約を別枠で挙げさせる）＝出典を辞退した回数と作り話した回数</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の募集文にはプラットフォーム名を書いていない。真値＝規約の出典は挙げられないはず。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "8回＝4群（禁止・要申告・可・一言も書かれていない）×各2回。</text>\n",
    ]

    y = top
    for label, n, bar_cls, txt_cls in rows:
        ty = y + 13
        parts.append(f'<text class="t-sm" x="18" y="{ty + 12}">{_esc(label)}</text>\n')
        x0, x1 = px(0), px(n)
        w = max(4, x1 - x0)
        parts.append(
            f'<rect class="{bar_cls}" x="{x0:.1f}" y="{ty}" '
            f'width="{w:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="{txt_cls}" x="{x0 + w + 8:.1f}" y="{ty + 13}">{n}/8</text>\n'
        )
        y += pitch

    parts.append(
        f'<path class="line" d="M{plot_x} {axis_y} L{px(8):.1f} {axis_y}"/>\n'
    )
    for tick in (0, 2, 4, 6, 8):
        tx = px(tick)
        parts.append(f'<path class="line" d="M{tx:.1f} {axis_y} L{tx:.1f} {axis_y + 5}"/>\n')
        parts.append(f'<text class="t-xs" x="{tx - 6:.1f}" y="{axis_y + 18}">{tick}回</text>\n')

    y = axis_y + 40
    for text in (
        "8回とも、募集文からはどのプラットフォームか特定できないため規約は挙げられない、",
        "という趣旨で正直に答えた。実在しない規約を作り話した回は0回。",
        "⚠️ これは「プラットフォーム名を書かなかった場合」の実測。実在の名前があった場合は試していない。",
    ):
        parts.append(f'<text class="t-xs" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 18

    height = y + 6
    alt = (
        "AI利用について書かれた文に加えてプラットフォームの規約も別枠で挙げるよう頼んだ実測で、"
        "出典を辞退した回数と作り話した回数を示す図。8回中8回が、募集文からはどのプラットフォームか"
        "特定できないため規約は挙げられない、という趣旨で正直に答え、実在しない規約を作り話した回は0回だった。"
    )
    (OUT / "job-ai-policy-v4-citation.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def weekly_rate_boundary_crossed_chart() -> None:
    """「何週連続で下がっているか」の答えが、線引きの違う週をまたいだか。

    実測（2026-08-27・3版×各3回＝9回）。P社サイト（第3・6週が欠測で、
    第4週の前後に線引きの変わり目が来る案件）の「連続」判定を、正規表現で
    機械判定した（第3週以下と第5週以上の週番号が同じ1文に同時に出るか）。
    値は docs/evidence/weekly-rate-crosses-the-line.md の判定コード。
    """
    rows = [
        ("そのまま頼む", "版a", [True, True, True]),
        ("＋「線引きが違う週は比べない」", "版b", [False, False, False]),
        ("＋「比べた週と線引きを書く」", "版c", [False, False, False]),
    ]
    label_x, sub_x = 18, 208
    box_x0, box_gap, box_w = 300, 46, 34
    top = 118
    row_h = 46
    height = top + len(rows) * row_h + 92

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「何週連続で下がっているか」は、P社サイトで境界をまたいだか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "P社サイトは第3週と第6週が欠測で、線引きが変わる第4週の前後をまたぎやすい案件。"
        "3版×各3回＝9回。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "×＝「制作と修正のみ」の週（第1〜3週）と「全部含める」の週（第5〜8週）を"
        "同じ「連続」に数えた（赤）。○＝またいでいない（緑）。</text>\n",
    ]

    y = top
    for label, sub, verdicts in rows:
        cy = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{cy + 4}">{_esc(label)}</text>\n')
        parts.append(f'<text class="t-xs" x="{sub_x}" y="{cy + 4}">{_esc(sub)}</text>\n')
        crossed = sum(1 for v in verdicts if v)
        for i, v in enumerate(verdicts):
            cx = box_x0 + i * box_gap
            cls = "box-bad" if v else "box-good"
            tcls = "t-bad" if v else "t-good"
            parts.append(
                f'<rect class="{cls}" x="{cx}" y="{y}" width="{box_w}" height="28" rx="4"/>\n'
            )
            mark = "×" if v else "○"
            parts.append(
                f'<text class="{tcls}" x="{cx + box_w / 2:.1f}" y="{y + 20}" '
                f'text-anchor="middle" style="font-size:15px;font-weight:700">{mark}</text>\n'
            )
        count_cls = "t-bad" if crossed else "t-good"
        parts.append(
            f'<text class="{count_cls}" x="{box_x0 + 3 * box_gap + 14}" y="{y + 18}">'
            f"{crossed}/3</text>\n"
        )
        y += row_h

    notes_y = y + 20
    for text in (
        "※ 版aは3回とも、それとは別に「線引きが変わった」こと自体は文中で自分から書いていた。"
        "気づいてはいたが、答えの数字には反映されなかった。",
        "※ 表に行が無い週（第3・4・6週）を0円として扱った回は、9回を通じて0回だった。",
        "※ 版aの答えの1つを、別の独立した回答に「境界をまたいだ案件がないか点検して」と貼ったところ、"
        "またいだ3案件を1回で正しく指摘できた。",
    ):
        parts.append(f'<text class="t-xs" x="18" y="{notes_y}">{_esc(text)}</text>\n')
        notes_y += 20

    height = notes_y + 6
    alt = (
        "週次の時給レポート8週分を見せて「何週連続で下がっているか」を尋ねた実測で、"
        "第3・6週が欠測でもっとも数えにくいP社サイトについて、答えが「制作と修正のみ」の週と"
        "「全部含める」の週をまたいだかどうかを示す図。"
        "そのまま頼んだ版aは3回中3回ともまたいでいた。"
        "「線引きが違う週は比べないでください」を足した版bは3回中0回、"
        "「比べた週と線引きを書いてください」を足した版cも3回中0回で、またがなかった。"
        "版aは3回とも、線引きが変わったこと自体は文中で言及していたが、答えの数字には反映されていなかった。"
        "表に行が無い週を0円として扱った回は9回を通じて0回だった。"
        "版aの答えの1つを、別の独立した回答に「境界をまたいだ案件がないか点検して」と貼ったところ、"
        "またいだ3案件を1回で正しく指摘できた。"
    )
    (OUT / "weekly-rate-boundary-crossed.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_todo_version_hits_chart() -> None:
    """架空スレッド2本×2回＝16機会のうち、版ごとに宿題を何件拾えたか。

    実測（2026-08-28）。宿題は1材料あたり4件（未解決）。
    版c（この記事の元になった記事「最後の1往復だけ見て」の指示文そのまま）が
    いちばん低く、版b（「まず経緯を要約してから」）が16/16で最も高かった。
    """
    max_val = 16
    bar_x, bar_w = 210, 380
    scale = bar_w / max_val
    rows = [
        ("版a　そのまま聞く", "bar-in", 8),
        ("版b　まず経緯を要約してから", "bar-out", 16),
        ("版c　最後の1往復だけ見て（元の記事の指示文）", "bar-old", 6),
        ("版d　c＋保険の一文", "bar-in", 11),
    ]
    top = 108
    pitch, bar_h = 34, 20
    height = top + len(rows) * pitch + 78

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "宿題4件×教材2本×2回＝16機会のうち、版ごとに何件拾えたか</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の案件スレッド2本（各14通・宿題9件のうち未解決4件）に、読み方だけを変えて通した実測。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「漏れ」は、すでに終わった仕事を宿題として書いてしまった件数（下の注に別枠で書く）。</text>\n",
    ]

    y = top
    for label, klass, value in rows:
        cy = y + bar_h / 2 + 4
        parts.append(f'<text class="t" x="18" y="{cy:.1f}">{_esc(label)}</text>\n')
        w = value * scale
        parts.append(
            f'<rect class="{klass}" x="{bar_x}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-accent" x="{bar_x + w + 8:.1f}" y="{cy:.1f}">{value}/16</text>\n'
        )
        y += pitch

    notes_y = y + 24
    for text in (
        "※ 版cは元の記事「長いスレッドで、いま何を求められているのか分からない」の指示文そのもの。",
        "※ 終わった仕事を宿題として書いてしまった「漏れ」は、版a〜dのどれも0件だった。",
    ):
        parts.append(f'<text class="t-xs" x="18" y="{notes_y}">{_esc(text)}</text>\n')
        notes_y += 20

    height = notes_y + 6
    alt = (
        "架空の案件スレッド2本（宿題9件のうち未解決4件）に、読み方だけを変えた4つの版を"
        "各2回・のべ16機会通した実測で、版ごとに拾えた宿題の件数を横棒グラフで示す図。"
        "版a（そのまま聞く）は8/16、版b（まず経緯を要約してから）は16/16で漏れ0件、"
        "版c（最後の1往復だけ見て。元の記事の指示文そのまま）は6/16でもっとも低く、"
        "版d（版cに保険の一文を足したもの）は11/16で漏れ0件だった。"
        "版bで、すでに終わった仕事を宿題として書いてしまった回は8機会を通じて0回だった。"
    )
    (OUT / "handoff-todo-version-hits.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def handoff_todo_position_hits_chart() -> None:
    """宿題が生まれた順番（スレッドの中の古さ）ごとに、拾われた回数。

    実測（2026-08-28）。4版×教材2本×2回＝16機会を、宿題の生まれた順番でまとめ直した。
    """
    max_val = 16
    bar_x, bar_w = 260, 370
    scale = bar_w / max_val
    rows = [
        ("① いちばん古い宿題", "bar-old", 5),
        ("② 2番目に古い宿題", "bar-out", 15),
        ("③ 3番目に古い宿題", "bar-in", 6),
        ("④ 直前のやり取りの宿題", "bar-out", 15),
    ]
    top = 108
    pitch, bar_h = 34, 20
    height = top + len(rows) * pitch + 60

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "宿題は、生まれた順番が古いほど拾われにくい（直前の宿題は別）</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "版a〜dの16機会を、スレッドの中で宿題が出てきた順番（1〜4番目）でまとめ直した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "④は「最後の1往復」に入るので、版cでもほぼ拾われている。①はそこに入らない。</text>\n",
    ]

    y = top
    for label, klass, value in rows:
        cy = y + bar_h / 2 + 4
        parts.append(f'<text class="t" x="18" y="{cy:.1f}">{_esc(label)}</text>\n')
        w = value * scale
        parts.append(
            f'<rect class="{klass}" x="{bar_x}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-accent" x="{bar_x + w + 8:.1f}" y="{cy:.1f}">{value}/16</text>\n'
        )
        y += pitch

    notes_y = y + 20
    parts.append(
        f'<text class="t-xs" x="18" y="{notes_y}">'
        "※ ②が15/16と高いのは、この教材で②の宿題が「検討中です」という言い切りの一文を"
        "持っていたため（他の宿題より目立ちやすかった可能性がある）。</text>\n"
    )
    height = notes_y + 26
    alt = (
        "架空スレッド2本に読み方を変えた4版を各2回通した16機会を、宿題がスレッドの中で"
        "生まれた順番（1〜4番目）でまとめ直した横棒グラフ。"
        "いちばん古い宿題は16機会中5回、2番目に古い宿題は16回中15回、"
        "3番目に古い宿題は16回中6回、直前のやり取りの宿題は16回中15回拾われた。"
        "直前の宿題は「最後の1往復だけ見て」という絞り込みの版でもほぼ拾われるが、"
        "いちばん古い宿題はどの版でも拾われにくい。"
    )
    (OUT / "handoff-todo-position-hits.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def role_prompt_grid_chart() -> None:
    """役割を付ける・付けないの6版で、正答・検出・「条文名の書き添え」がどう動いたか。

    実測（2026-08-28・6版×各2回＝12回・計72問）。値は
    docs/evidence/role-prompt-same-answer.md の判定コード。
    正答（問1〜3の条文番号の一致）と検出（問4〜6の「記載なし」表明）は
    12回すべてで満点（各6/6）。聞いていない「条文名の書き添え」だけが版によって揺れた。
    """
    rows = [
        ("a. 役割なし", "6/6", "6/6", 0),
        ("b. 「あなたは担当者です」", "6/6", "6/6", 0),
        ("c. 「20年の専門家です」", "6/6", "6/6", 2),
        ("d. 念押しの一文を外す", "6/6", "6/6", 0),
        ("e. 逐語引用を求める", "6/6", "6/6", 1),
        ("f. c＋逐語引用を求める", "6/6", "6/6", 0),
    ]
    label_w = 210
    col_w = 150
    col_x = [18 + label_w, 18 + label_w + col_w, 18 + label_w + col_w * 2]
    top = 130
    row_h = 30

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "正答と検出はどの版も満点。動いたのは「条文名の書き添え」だけ</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "6版×各2回＝12回・計72問。正答＝問1〜3で条文番号が正しい。検出＝問4〜6で"
        "「規程に記載がない」と明言。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "条文名の書き添え＝聞いていないのに「第2条（出張旅費）」のように名前を添えた回数（／2回）。"
        "</text>\n",
    ]

    headers = ["正答（問1〜3）", "検出（問4〜6）", "条文名の書き添え"]
    for i, h in enumerate(headers):
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + col_w / 2:.1f}" y="{top - 14}" '
            f'text-anchor="middle">{_esc(h)}</text>\n'
        )

    y = top
    for label, correct, detect, name_hits in rows:
        ty = y + 19
        parts.append(f'<text class="t" x="18" y="{ty}">{_esc(label)}</text>\n')
        for i, val in enumerate((correct, detect)):
            x = col_x[i]
            parts.append(
                f'<rect class="box-good" x="{x + 20}" y="{y}" width="{col_w - 40}" height="26" rx="4"/>\n'
            )
            parts.append(
                f'<text class="t-good" x="{x + col_w / 2:.1f}" y="{ty}" '
                f'text-anchor="middle" style="font-weight:700">{_esc(val)}</text>\n'
            )
        x = col_x[2]
        klass = "box-accent" if name_hits else "box-quiet"
        tcls = "t-accent" if name_hits else "t-sm"
        parts.append(
            f'<rect class="{klass}" x="{x + 20}" y="{y}" width="{col_w - 40}" height="26" rx="4"/>\n'
        )
        parts.append(
            f'<text class="{tcls}" x="{x + col_w / 2:.1f}" y="{ty}" '
            f'text-anchor="middle" style="font-weight:700">{name_hits}／2</text>\n'
        )
        y += row_h + 6

    y += 8
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="678" height="46" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 19}">'
        "72問中72問が正答・検出とも満点。捏造引用（未記載の問に実在条文を当てた数）も0件。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 37}">'
        "条文名の書き添えは「20年の専門家」で2／2回。ただし同じ役割＋逐語引用（f）では0／2回で、一貫しない。</text>\n"
    )
    y += 46 + 16

    height = y + 8
    alt = (
        "役割を付ける・付けないの6版（役割なし、あなたは担当者です、20年の専門家です、"
        "念押しの一文を外す、逐語引用を求める、専門家＋逐語引用）について、各2回・"
        "計12回72問を実測した結果の表。正答（問1〜3の条文番号一致）と検出（問4〜6の"
        "「記載がない」明言）はどの版も6／6で満点、12回全体では72問中72問が正答・検出とも"
        "満点だった。捏造引用（記載のない問に実在の条文番号を当てた数）も0件。"
        "聞いていないのに条文名を書き添えた回数だけが版によって違い、"
        "役割なし・担当者・念押しなし・専門家＋逐語引用の4版は2回とも0回、"
        "逐語引用を求めた版は2回中1回、20年の専門家を付けた版だけ2回とも書き添えた。"
        "ただし同じ役割に逐語引用を重ねた版では0回に戻っており、一貫した効果とは言えない。"
    )
    (OUT / "role-prompt-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def resume_list_correctness_chart() -> None:
    """3つの続け方（続きを書いて／＋IDは書かないで／件目で指定）で、

    欠落・重複・紛らわしい組の取りこぼしがどれだけ起きたかを並べる。
    実測（2026-08-29・架空の名簿2本×各2回＝12回、続きの25件ぶん）。
    値は docs/evidence/resume-a-cut-off-list.md の判定コード。
    """
    rows = [
        ("a. 続きを書いて", "0／100", "0／100", "0／12"),
        ("b. ＋すでに出したIDは書かない", "0／100", "0／100", "0／12"),
        ("c. 「16件目から40件目まで」", "0／100", "0／100", "0／12"),
    ]
    label_w = 210
    col_w = 150
    col_x = [18 + label_w, 18 + label_w + col_w, 18 + label_w + col_w * 2]
    top = 118
    row_h = 30

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "続け方を3通り変えても、欠落・重複は1件も起きなかった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の名簿2本（領収書40件・問い合わせ40件）×各2回＝12回。"
        "15件目で切れた続きの25件ぶんを判定。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "紛らわしい組＝同じ金額・区分（部署・件名）が同じで、"
        "日付とIDだけ違う行を3組仕込み、取りこぼしも数えた。</text>\n",
    ]

    headers = ["欠落（件）", "重複（件）", "紛らわしい組の取りこぼし"]
    for i, h in enumerate(headers):
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + col_w / 2:.1f}" y="{top - 14}" '
            f'text-anchor="middle">{_esc(h)}</text>\n'
        )

    y = top
    for label, missing, dup, pair in rows:
        ty = y + 19
        parts.append(f'<text class="t" x="18" y="{ty}">{_esc(label)}</text>\n')
        for i, val in enumerate((missing, dup, pair)):
            x = col_x[i]
            parts.append(
                f'<rect class="box-good" x="{x + 15}" y="{y}" width="{col_w - 30}" height="26" rx="4"/>\n'
            )
            parts.append(
                f'<text class="t-good" x="{x + col_w / 2:.1f}" y="{ty}" '
                f'text-anchor="middle" style="font-weight:700">{_esc(val)}</text>\n'
            )
        y += row_h + 6

    y += 8
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="678" height="82" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 19}">'
        "3通りとも、続きの25件は欠落・重複なし。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 37}">'
        "紛らわしい組の取りこぼしも0件だった。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 55}">'
        "最初から2分割した下限も欠落・重複0件。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 73}">'
        "崩れたのは中身ではなく書式のほう（次の図）。</text>\n"
    )
    y += 82 + 16

    height = y + 8
    alt = (
        "続きを書いて・すでに出したIDは書かないで・16件目から40件目までの3通りの頼み方について、"
        "架空の名簿2本（領収書40件・問い合わせ40件）を各2回、計12回試した結果の表。"
        "続きの25件ぶんで判定した欠落は3通りとも0／100件、重複も0／100件。"
        "同じ金額・区分や部署・件名で日付とIDだけ違う紛らわしい組を3組ずつ仕込み、"
        "後ろ側が誤って省かれないかを機会数12で見たが、取りこぼしは0／12件だった。"
        "最初から2回に分けて頼んだ健全性の下限（40件）でも欠落・重複は0件。"
        "3通りとも中身は崩れず、崩れたのは書式のほうだった。"
    )
    (OUT / "resume-list-correctness.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def resume_list_header_drift_chart() -> None:
    """見出し行を繰り返すかどうかが、頼み方と回によってどう割れたかを見せる。

    実測（2026-08-29）。a・bは4回とも見出しなしで一貫。cだけ、素材と回によって
    見出しの有無が割れた（材料Aは2回とも有、材料Bは1回だけ有）。
    """
    rows = [
        ("a. 続きを書いて", ["無", "無", "無", "無"]),
        ("b. ＋すでに出したIDは書かない", ["無", "無", "無", "無"]),
        ("c. 「16件目から40件目まで」", ["有", "有", "無", "有"]),
    ]
    col_labels = ["材料A 1回目", "材料A 2回目", "材料B 1回目", "材料B 2回目"]
    label_w = 210
    col_w = 118
    col_x = [18 + label_w + col_w * i for i in range(4)]
    top = 127
    row_h = 34

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "見出し行を繰り返すかどうかは、「◯件目から」だけが回によって割れた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "実測2026-08-29。a・bは4回とも見出し行を</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "繰り返さず一貫。cは材料Aで2回とも見出し付き、</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "材料Bは1回目が無し・2回目が有りと回によって割れた。</text>\n",
    ]

    for i, h in enumerate(col_labels):
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + col_w / 2:.1f}" y="{top - 12}" '
            f'text-anchor="middle">{_esc(h)}</text>\n'
        )

    y = top
    for label, cells in rows:
        ty = y + 22
        parts.append(f'<text class="t" x="18" y="{ty}">{_esc(label)}</text>\n')
        has_split = len(set(cells)) > 1
        for i, val in enumerate(cells):
            x = col_x[i]
            is_present = val == "有"
            klass = "box-accent" if (has_split and is_present) else ("box-quiet" if not is_present else "box")
            tcls = "t-accent" if (has_split and is_present) else "t-sm"
            parts.append(
                f'<rect class="{klass}" x="{x + 12}" y="{y}" width="{col_w - 24}" height="28" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{tcls}" x="{x + col_w / 2:.1f}" y="{ty}" '
                f'text-anchor="middle" style="font-weight:700">見出し{val}</text>\n'
            )
        y += row_h + 8

    y += 6
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="678" height="82" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 19}">'
        "「続きを書いて」系は8回とも見出しなしで安定。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 37}">'
        "「◯件目から」は4回中3回が見出し付き、</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 55}">'
        "材料Bの1回目だけ見出しなしで割れた。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 73}">'
        "件数と内容は割れた回でも正しく、崩れたのは書式だけ。</text>\n"
    )
    y += 82 + 16

    height = y + 8
    alt = (
        "見出し行を繰り返すかどうかを、頼み方a・b・cごとに材料A・材料Bの各2回、"
        "計4回ずつ並べた表。「続きを書いて」と「すでに出したIDは書かないで」は、"
        "どちらも材料A・材料Bの2回ずつ計4回とも見出しなしで一貫していた。"
        "「16件目から40件目までを出してください」だけは、材料Aで2回とも見出しあり、"
        "材料Bでは1回目が見出しなし・2回目が見出しありと割れた。強調した枠は、"
        "同じ頼み方の中で割れた回に見出しが付いたケース。件数と内容はどの回でも"
        "正しく、崩れたのは見出しの有無という書式だけだった。"
    )
    (OUT / "resume-list-header-drift.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def money_map_three_routes_chart() -> None:
    """副業のお金が届く3つの流れ（誰が払い、どこを経由して、自分に届くか）。

    実測ではなく各公式ページの記述の整理（2026-08-29確認）。
    ①運営から配られる（X・YouTube）②買い手から直接（note・Kindle）
    ③発注者から（クラウドワークス等）。
    """
    rows = [
        (
            "①運営から配られる（X・YouTube）",
            "広告主など",
            "運営が集めて、門を通った人に配る",
            "門＝X: Premium加入＋過去3か月に500万回以上のオーガニック インプレッション"
            "＋認証済みフォロワー500人／YouTube: 登録者1,000人ほか",
        ),
        (
            "②買い手から直接（note・Kindle）",
            "買い手（読者）",
            "売り場が手数料を引いて渡す",
            "門＝実績の数字ではなく事務手続き（note: 振込申請は売上1,000円から／Kindle: 出版前に税の手続き）",
        ),
        (
            "③発注者から（クラウドワークスなど）",
            "発注者",
            "仲介の場が手数料を引く（5〜20%）",
            "門＝応募して選ばれる（受注）。金額は受注時の契約で決まる",
        ),
    ]
    a_x, a_w = 18, 150
    b_x, b_w = 190, 300
    c_x, c_w = 512, 190
    box_h = 40
    assert c_x + c_w == WIDTH - 18

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "副業のお金は、3つの流れのどれかで届く</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "違いは「誰の財布から出るか」。出どころが違えば、門（受け取る条件）の場所も違う。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "各公式ページの記述の整理（2026-08-29確認）。条件は変わるため、始める前に原文を開くこと。</text>\n",
    ]

    y = 92
    for title, src, via, gate in rows:
        parts.append(f'<text class="t-accent" x="18" y="{y + 14}">{_esc(title)}</text>\n')
        by = y + 24
        mid = by + box_h / 2 + 4
        parts.append(f'<rect class="box" x="{a_x}" y="{by}" width="{a_w}" height="{box_h}" rx="6"/>\n')
        parts.append(f'<text class="t" x="{a_x + 12}" y="{mid}">{_esc(src)}</text>\n')
        parts.append(f'<path class="line" d="M{a_x + a_w + 4} {by + box_h / 2} L{b_x - 4} {by + box_h / 2}"/>\n')
        parts.append(f'<rect class="box-accent" x="{b_x}" y="{by}" width="{b_w}" height="{box_h}" rx="6"/>\n')
        parts.append(f'<text class="t" x="{b_x + 12}" y="{mid}">{_esc(via)}</text>\n')
        parts.append(f'<path class="line" d="M{b_x + b_w + 4} {by + box_h / 2} L{c_x - 4} {by + box_h / 2}"/>\n')
        parts.append(f'<rect class="box-good" x="{c_x}" y="{by}" width="{c_w}" height="{box_h}" rx="6"/>\n')
        parts.append(f'<text class="t" x="{c_x + 12}" y="{mid}">自分の口座</text>\n')
        parts.append(f'<text class="t-xs" x="{a_x}" y="{by + box_h + 18}">{_esc(gate)}</text>\n')
        y = by + box_h + 34

    y += 4
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="684" height="46" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 20}">'
        "①は先に条件、②は先に商品、③は先に受注。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 38}">'
        "「AIで稼ぐ」と一言で言っても、始め方はこの3つで別物になる。</text>\n"
    )
    y += 46 + 14

    height = y + 8
    alt = (
        "副業のお金が自分の口座に届くまでの3つの流れを並べた図。"
        "1つ目は運営から配られる型で、XやYouTubeが当てはまる。広告主などのお金を"
        "運営が集めて、門を通った人に配る。門はXならPremium加入と過去3か月に500万回以上の"
        "オーガニック インプレッションと認証済みフォロワー500人、YouTubeなら登録者1,000人などが"
        "公式ページに書いてある。"
        "2つ目は買い手から直接の型で、noteやKindleが当てはまる。買い手が払ったお金から"
        "売り場が手数料を引いて渡す。門は実績の数字ではなく事務手続きで、"
        "noteは振込申請が売上1,000円から、Kindleは出版の前に税に関するインタビューの完了が必要。"
        "3つ目は発注者からの型で、クラウドワークスなどが当てはまる。発注者が払ったお金から"
        "仲介の場が5から20パーセントの手数料を引く。門は応募して選ばれること、"
        "つまり受注で、金額は受注時の契約で決まる。"
        "まとめると、1つ目は先に条件、2つ目は先に商品、3つ目は先に受注が要る。"
    )
    (OUT / "money-map-three-routes.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def money_map_gates_timing_chart() -> None:
    """4つのサービスの「門」と「受け取り」を、公式ページの記述だけでカードに並べる。

    実測ではなく原文の転記（2026-08-29確認）。noteの数字だけは
    2026-08-25確認の既存記事（note-fee-before-you-sell）と同じ出典。
    """
    cards = [
        (
            "X（クリエイター収益配分）",
            [
                ("t", "門: Premium加入＋認証済みフォロワー500人"),
                ("t", "　　＋過去3か月に500万回以上の"),
                ("t", "　　　オーガニック インプレッション"),
                ("t-sm", "受け取り: Stripe経由・2週間ごと・最低10ドル・本人確認"),
            ],
        ),
        (
            "YouTube（パートナープログラム）",
            [
                ("t", "門: 登録者1,000人＋12か月で4,000時間"),
                ("t", "　　（またはショート90日で1,000万回）"),
                ("t-sm", "受け取り: YouTube向けAdSense経由"),
                ("t-sm", "原資は「広告掲載から得られる収益」の分配"),
            ],
        ),
        (
            "Kindle（KDP）",
            [
                ("t", "門: 銀行情報＋税に関するインタビュー"),
                ("t", "　　（出版の前に完了する）"),
                ("t-sm", "受け取り: 売上月の末日から約60日後"),
                ("t-sm", "最低売上金額を満たした月が対象"),
            ],
        ),
        (
            "クラウドワークス（受託）",
            [
                ("t", "門: 応募して受注する"),
                ("t", "　　（金額は契約で決まる）"),
                ("t-sm", "手数料: 10万円以下の部分が20%（段階制）"),
                ("t-sm", "振込手数料: 楽天100円・他行500円"),
            ],
        ),
    ]
    card_w, card_h = 333, 130
    xs = [18, 369]
    top = 92

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「門」の中身と受け取りの形は、公式ページで確かめられる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "門は①型（X・YouTube）＝実績の数字、②型（Kindle）＝事務手続きと振込条件、"
        "③型（受託）＝受注。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "2026-08-29に各公式ページで確認した記述の整理（noteは2026-08-25確認の既存記事と同じ出典）。</text>\n",
    ]

    for index, (name, lines) in enumerate(cards):
        x = xs[index % 2]
        y = top + (index // 2) * (card_h + 14)
        parts.append(f'<rect class="box" x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="6"/>\n')
        parts.append(f'<text class="t-strong" x="{x + 14}" y="{y + 24}">{_esc(name)}</text>\n')
        ly = y + 48
        for css, text in lines:
            parts.append(f'<text class="{css}" x="{x + 14}" y="{ly}">{_esc(text)}</text>\n')
            ly += 20
    y = top + 2 * card_h + 14

    y += 14
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="684" height="28" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 19}">'
        "条件と料率は変わる（国・規約遵守などの前提条件も別にある）。始める前に必ず原文を開くこと。</text>\n"
    )
    y += 28 + 12

    height = y + 8
    alt = (
        "4つのサービスの門と受け取りの形を、公式ページの記述だけでカードに並べた図。"
        "Xのクリエイター収益配分は、門がPremium加入と認証済みフォロワー500人と"
        "過去3か月に500万回以上のオーガニック インプレッションで、"
        "受け取りはStripe経由で2週間ごと、最低10ドル、"
        "本人確認の完了が必要。YouTubeパートナープログラムは、門が登録者1,000人と"
        "12か月で4,000時間、またはショート動画90日で1,000万回で、受け取りはYouTube向け"
        "AdSense経由、原資は広告掲載から得られる収益の分配と書いてある。"
        "KindleのKDPは、門が銀行情報と税に関するインタビューで出版の前に完了し、"
        "受け取りは売上月の末日から約60日後、最低売上金額を満たした月が対象。"
        "クラウドワークスの受託は、門が応募して受注することで金額は契約で決まり、"
        "手数料は10万円以下の部分が20パーセントの段階制、振込手数料は楽天銀行100円・"
        "他行500円。いずれも2026年8月29日に各公式ページで確認した記述の整理で、"
        "国・規約遵守などの前提条件は別にあり、条件と料率は変わるため"
        "始める前に原文を開いて確かめること。"
    )
    (OUT / "money-map-gates-timing.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def estimate_basis_count_chart() -> None:
    """申告した件数が、自分で列挙した日付の数・真値と一致したかを版ごとに並べる。

    実測（20回・材料2本×5版×各2回）。○＝件数・日付とも真値と一致。
    ×＝申告した件数が、自分が列挙した日付の数とも真値とも食い違った
    （2回とも「下調べ」を4件のところ5件と申告）。
    △＝いったん数え間違えたが、同じ回答の中で自分から数え直して訂正した
    （「修正」を6件→7件に、応答の中で訂正）。
    """
    rows = [
        ("a 素朴に「件数と日付を」", ["○", "×", "○", "○"]),
        ("b 先に「最大値だけ基準に」", ["○", "○", "○", "○"]),
        ("c 先に「2工程だけに絞って」", ["○", "×", "○", "○"]),
        ("d 先に無関係な雑談を挟む", ["○", "○", "△", "○"]),
        ("e ＋「何件から選んだか」念押し", ["○", "○", "○", "○"]),
    ]
    label_x, label_w = 18, 250
    col_w, col_gap = 96, 10
    col_x = [label_x + label_w + col_gap + i * (col_w + col_gap) for i in range(4)]
    head_y = 96
    row_h, row_gap = 40, 10
    row_y = [head_y + 28 + i * (row_h + row_gap) for i in range(len(rows))]
    heads = ["材料A 1回目", "材料A 2回目", "材料B 1回目", "材料B 2回目"]

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「件数が少ない順に、件数と日付も」と頼んだ20回の一致・不一致</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "○＝申告した件数・列挙した日付・真値がすべて一致。"
        "×＝申告した件数が日付の数とも真値とも食い違った。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "△＝いったん数え間違えたが、同じ回答の中で自分から数え直して訂正した。</text>\n",
    ]
    for i, name in enumerate(heads):
        parts.append(
            f'<text class="t-xs" x="{col_x[i] + col_w / 2:.0f}" y="{head_y + 14}" '
            f'text-anchor="middle">{_esc(name)}</text>\n'
        )
    for r, (label, values) in enumerate(rows):
        y = row_y[r]
        parts.append(
            f'<text class="t" x="{label_x}" y="{y + row_h / 2 + 5:.0f}" '
            f'style="font-size:12px">{_esc(label)}</text>\n'
        )
        for c, value in enumerate(values):
            if value == "○":
                klass, tone = "box-good", "t-good"
            elif value == "×":
                klass, tone = "box-bad", "t-bad"
            else:
                klass, tone = "box-accent", "t-accent"
            parts.append(
                f'<rect class="{klass}" x="{col_x[c]}" y="{y}" '
                f'width="{col_w}" height="{row_h}" rx="3"/>\n'
            )
            parts.append(
                f'<text class="{tone}" x="{col_x[c] + col_w / 2:.0f}" '
                f'y="{y + row_h / 2 + 6:.0f}" text-anchor="middle" '
                f'style="font-size:15px;font-weight:700">{_esc(value)}</text>\n'
            )

    y = row_y[-1] + row_h + 26
    notes = [
        ("t-bad", "※ ×の2回はどちらも「下調べ」を4件のところ5件と申告し、"
                  "自分で挙げた日付は4つしか書けていなかった。"),
        ("t-accent", "※ △は「修正」をいったん6件と書いたあと、"
                     "同じ回答の中で「数え直すと7件でした」と自分で訂正した回。"),
        ("t-xs", "架空データでの実測。20回とも、会話の文脈を引き継がない独立した回答。"
                 "生の回答は docs/evidence/ に全文置いてある。"),
    ]
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 22

    height = y + 2
    alt = (
        "「この見積もりで、いちばん外れやすい工程はどれですか。根拠にした記録の件数が"
        "少ない順に並べてください。件数と、根拠にした記録の日付も書いてください」と、"
        "5通りの前置き（素朴に聞く・先に最大値だけを基準にする質問を挟む・"
        "先に2工程だけに絞る質問を挟む・先に無関係な雑談を挟む・"
        "「何件から選んだかを書いてください」を念押しで足す）×材料2本×各2回＝20回試した結果の表。"
        "素朴に聞いた回は、材料Aの1回目は件数・日付とも真値と一致したが、"
        "2回目は「下調べ」を4件のところ5件と申告し、自分で挙げた日付は4つしか書けていなかった。"
        "材料Bは1回目・2回目とも一致。"
        "先に最大値だけを基準にする質問を挟んだ回は、材料A・材料Bとも1回目・2回目とも一致。"
        "先に2工程だけに絞る質問を挟んだ回は、材料Aの2回目でまた"
        "「下調べ」を5件と申告する同じ誤りが起きたが、他の3回は一致。"
        "先に無関係な雑談を挟んだ回は、材料Bの1回目で「修正」をいったん6件と申告したあと、"
        "同じ回答の中で「数え直すと7件でした」と自分で訂正した。他の3回は一致。"
        "「何件から選んだかを書いてください」を念押しで足した回は、材料A・材料Bとも"
        "1回目・2回目とも一致し、この4回だけは食い違いが1件も起きなかった。"
    )
    (OUT / "estimate-basis-count-check.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def cron_delay_distribution_chart() -> None:
    """このサイト自身のトラッカーの実行間隔を、git履歴から実測して並べる。

    実測（2026-08-30・`data/tracker/seen.json` の全コミット276件・間隔275個。
    外向き通信ゼロ、手元のgit履歴だけで測れる）。設計は「毎時」だが、
    実際の間隔は70分以内が半分にとどかず、6時間を超える回も7%ある。
    """
    buckets = [
        ("70分以内(ほぼ定刻)", 135),
        ("70分〜3時間", 87),
        ("3〜6時間", 33),
        ("6時間超", 20),
    ]
    total = 275
    label_x, label_w = 18, 150
    plot_x = label_x + label_w + 14
    plot_w = 400
    axis_max = 135
    scale = plot_w / axis_max
    top = 132
    row_h = 34
    bar_h = 18

    def px(n: float) -> float:
        return plot_x + n * scale

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "毎時の設計に対し、実際の間隔は「70分以内」が半分にとどかない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "このサイト自身のニューストラッカー（毎時実行の設計）が状態ファイルを"
        "書き戻したコミット276件、間隔275個を実測。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "外向き通信は使わず、手元のgit履歴の日時だけで数えられる。"
        "中央値は76分・最長は25.0時間（8/9 07:49→8/10 08:49）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "GitHub Actionsのスケジュール実行は「その時刻ちょうどに動く」ことを保証しない"
        "（GitHub公式の注記どおり）。</text>\n",
    ]

    y = top
    for label, count in buckets:
        ty = y + row_h / 2 + 5
        parts.append(f'<text class="t" x="{label_x}" y="{ty:.0f}">{_esc(label)}</text>\n')
        w = max(px(count) - plot_x, 2)
        klass = "bar-new" if "70分以内" in label else "bar-old"
        parts.append(
            f'<rect class="{klass}" x="{plot_x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        pct = round(count / total * 100)
        parts.append(
            f'<text class="t-accent" x="{plot_x + w + 8:.1f}" y="{ty:.0f}">'
            f"{count}件（{pct}%）</text>\n"
        )
        y += row_h + 10

    notes = [
        ("t-xs", "縦軸4区分・横軸は件数（全275間隔中）。"),
        ("t-xs", "設計は「毎時」なので本来は275回とも70分以内のはずの値。"),
    ]
    y += 6
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 20

    height = y + 4
    alt = (
        "GitHub Actionsで毎時実行の設計になっているこのサイト自身のニューストラッカーの、"
        "実際の実行間隔を測った棒グラフ。状態ファイルへのコミット276件・間隔275個が対象。"
        "70分以内（ほぼ定刻）が135件で49%、70分から3時間が87件で32%、"
        "3時間から6時間が33件で12%、6時間超が20件で7%。"
        "中央値は76分、最長は25.0時間（8月9日07:49から8月10日08:49）。"
        "設計どおりなら275回とも70分以内のはずが、半分にとどかない。"
    )
    (OUT / "cron-delay-distribution.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def cutoff_vs_resume_duplicate_chart() -> None:
    """「時刻を基準」と「前回の続きから」を4版×各3回で試し、重複件数を並べる。

    実測（2026-08-30）。架空の申込みログ24件（前回処理済み14件・新着10件）を
    1本用意し、同じログのまま指示文だけ変えて、新規の会話3回ずつ試した。
    重複＝すでに処理済みの14件のうち何件を再び対象に含めたか（真値0）。
    """
    rows = [
        ("(a) 時刻基準のみ", [14, 14, 0], "3回とも数字が割れた"),
        ("(b) 前回位置のみ", [0, 0, 0], "3回とも重複0"),
        ("(c) 時刻基準+遅れを伝える", [14, 14, 14], "3回一致・でも直らない"),
        ("(d) 前回位置+遅れを伝える", [0, 0, 0], "3回とも重複0"),
    ]
    label_x = 18
    plot_x = 260
    plot_w = 220
    axis_max = 14
    scale = plot_w / axis_max
    top = 150
    row_h = 42
    bar_h = 16
    truth = 0

    def px(n: float) -> float:
        return plot_x + n * scale

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「前回の続きから」は3回とも重複0。「時刻基準」は同じ指示文でも数字が割れた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空のセミナー申込みログ24件（前回処理済みR-001〜014・新着R-015〜024）を"
        "1本のログのまま渡した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "振ったのは指示文だけ＝(a)(c)は「本日7時までに届いた分」、"
        "(b)(d)は「前回処理済みの最後のID」を基準にした。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "(c)(d)は「本来7時の予定が実際は10時12分に実行された」という遅延も伝えている。"
        "4版×各3回＝12回、新規の会話ごと。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "重複＝前回すでに処理済みの14件のうち、今回また対象に含めてしまった件数（真値0）。"
        "帯は3回の最小から最大まで。</text>\n",
        f'<text class="t-xs" x="{px(truth) + 6:.1f}" y="{top - 12}">← 真値は0件</text>\n',
    ]

    plot_bottom = top + len(rows) * row_h - 18
    tx = px(truth)
    parts.append(
        f'<path class="line" d="M{tx:.1f} {top - 4} L{tx:.1f} {plot_bottom}" '
        f'stroke-dasharray="4 3"/>\n'
    )

    y = top
    for label, values, note in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        lo, hi = min(values), max(values)
        parts.append(
            f'<rect class="bar-old" x="{px(lo):.1f}" y="{ty - 12}" '
            f'width="{max(px(hi) - px(lo), 2):.1f}" height="{bar_h}" rx="3"/>\n'
        )
        for v in sorted(set(values)):
            vx = px(v)
            parts.append(
                f'<path class="line" d="M{vx:.1f} {ty - 13} L{vx:.1f} {ty + 5}" '
                f'stroke-width="2.4"/>\n'
            )
        text = "・".join(str(v) for v in values) + "件"
        cls = "t-accent" if lo == hi == truth else "t-bad"
        parts.append(
            f'<text class="{cls}" x="{px(axis_max) + 10:.1f}" y="{ty}">{_esc(text)}</text>\n'
        )
        parts.append(f'<text class="t-sm" x="{label_x + 12}" y="{ty + 17}">{_esc(note)}</text>\n')
        y += row_h

    notes = [
        ("t-bad", "🚨 (a)は3回目だけ0件になった。ただし取りこぼしは逆に増えている"
                  "（本文の表を参照）。0件は正解だからではない。"),
        ("t-sm", "※ (c)は遅れを伝えても対象範囲は変わらなかった。ただし3回とも同じ答えになり、"
                 "(a)より安定はした。"),
        ("t-xs", "架空データでの実測（12回・新規の会話ごと）。生の回答は docs/evidence/ に全文置いてある。"),
    ]
    y += 4
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 20

    height = y + 4
    alt = (
        "自動処理の対象範囲を「時刻を基準」にするか「前回処理した続きから」にするかを、"
        "4通りの指示文で3回ずつ試した図。架空のセミナー申込みログ24件を使い、"
        "前回処理済みの14件と新着の10件を仕込んだ。"
        "時刻基準のみの版は重複件数が14件・14件・0件と3回とも割れた。"
        "前回位置のみの版は3回とも重複0件。"
        "時刻基準に実行が3時間遅れた事実を伝えた版は3回とも重複14件で、"
        "遅れを伝えても対象範囲は変わらなかったが3回とも同じ答えで安定した。"
        "前回位置に遅延の事実を伝えた版も3回とも重複0件。"
        "重複の真値は0件である。"
    )
    (OUT / "cutoff-vs-resume-duplicate.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def x_cash_flow_timeline_chart() -> None:
    """Xの収益配分で、お金が出ていく順と入ってくる順を並べる。

    実測ではなく原文の転記（2026-08-29確認）。①先に払う→②門→③入金。
    2,940円＝980円×3か月（この記事の掛け算。原文には無い）。
    """
    rows = [
        (
            "① 先に払う（自分の持ち出し）",
            "Xプレミアム 月980円（日本・ウェブ）",
            "申請にはプレミアム以上が必要。持ち出し＝980円 × 加入した月数",
            "box-bad",
        ),
        (
            "② 門を通る（2階建て）",
            "収益配分ページの参加資格5項目 ＋ 別ページの収益化の参加資格9項目",
            "プレミアム以上／過去3か月以内に500万回以上のオーガニック インプレッション／認証済みフォロワー500人以上",
            "box-quiet",
        ),
        (
            "③ 入金される",
            "最小入金額10ドル・2週間ごとに処理",
            "Stripeの入金アカウント接続と本人確認の完了が要る",
            "box-good",
        ),
    ]
    box_x, box_w = 18, 684
    parts = [
        '<text class="t-strong" x="18" y="26">'
        "Xの収益配分は、入ってくる前に出ていく</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "各公式ページの記述の整理（2026-08-29確認）。金額は日本・ウェブサイトからの購入の場合。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "「過去3か月以内」は、待つ期間ではなく、さかのぼって数える集計の窓。</text>\n",
    ]

    y = 92
    for title, headline, detail, klass in rows:
        parts.append(f'<rect class="{klass}" x="{box_x}" y="{y}" width="{box_w}" height="74" rx="6"/>\n')
        parts.append(f'<text class="t-strong" x="{box_x + 16}" y="{y + 24}">{_esc(title)}</text>\n')
        parts.append(f'<text class="t" x="{box_x + 16}" y="{y + 46}">{_esc(headline)}</text>\n')
        parts.append(f'<text class="t-sm" x="{box_x + 16}" y="{y + 65}">{_esc(detail)}</text>\n')
        if title.startswith("③"):
            break
        arrow_y = y + 74
        parts.append(f'<path class="line" d="M{box_x + 40} {arrow_y + 3} L{box_x + 40} {arrow_y + 17}"/>\n')
        y = arrow_y + 20

    y += 74 + 14
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="684" height="46" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 20}">'
        "①と③のあいだ、収益がゼロでも月980円は出ていく（持ち出し＝980円×加入月数）。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 38}">'
        "窓いっぱいの3か月かけたなら2,940円（この掛け算は記事のもの。原文の数字ではない）。</text>\n"
    )
    y += 46 + 12

    height = y + 8
    alt = (
        "Xの収益配分でお金が動く順を、上から3段に並べた図。"
        "1段目「先に払う」＝Xプレミアム月980円（日本・ウェブ）。持ち出しは980円×加入した月数。"
        "2段目「門を通る」＝収益配分ページの参加資格5項目と、別ページの収益化の参加資格9項目の"
        "2階建て。図に書き出してある3つは、プレミアム以上、過去3か月以内に500万回以上のオーガニック インプレッション、"
        "認証済みフォロワー500人以上。"
        "3段目「入金される」＝最小入金額10ドル・2週間ごとに処理・Stripeの接続と本人確認が必要。"
        "最下段の注記は、1段目と3段目のあいだは収益がゼロでも月980円が出ていくこと、"
        "窓いっぱいの3か月なら2,940円だがこの掛け算は記事のものであること。"
    )
    (OUT / "x-cash-flow-timeline.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def x_ai_hit_and_miss_chart() -> None:
    """AIに聞いた6回（版a・版b 各3回）で、当たった項目と外れた項目を並べる。

    実測（2026-08-29・Agentツール general-purpose・独立実行）。
    判定は docs/evidence/_raw/x-pay-before-you-earn/judge.py の出力から。
    """
    rows = [
        ("過去3か月・500万回・フォロワー500人", 3, 3, False),
        ("Stripe経由で受け取ること", 3, 3, False),
        ("プレミアム加入にお金がかかること", 3, 3, False),
        ("最小入金額の金額（10ドル）", 0, 3, False),
        ("ベーシックでは申請できないこと", 0, 3, False),
        ("フォロワーの「認証済み」という限定", 0, 0, True),
        ("プレミアムの料金を金額で書いた", 0, 3, False),
        ("その金額が合っていた（月980円）", 0, 0, True),
    ]
    label_w = 268
    col_w = 200
    col_x = [18 + label_w, 18 + label_w + col_w + 16]
    top = 130
    row_h = 34

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "条件と経路は6回とも当たった。外したのは料金と、条件の限定語</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "実測2026-08-29。ウェブ検索を切ったAIに、文脈を引き継がせず独立に実行。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "①＝「Xで収益化して稼ぐには何が必要ですか」／"
        "②＝「Xのクリエイター収益配分で収益を受け取り始めるまでに…」を各3回。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "数字は3回のうち何回その内容が出たか。真値は公式ページ"
        "（日本・ウェブ購入で月980円・認証済みフォロワー500人以上）。</text>\n",
    ]
    for index, head in enumerate(["① 素朴に聞く", "② 金額を直接聞く"]):
        parts.append(
            f'<text class="t-xs" x="{col_x[index] + col_w / 2:.1f}" y="{top - 12}" '
            f'text-anchor="middle">{_esc(head)}</text>\n'
        )

    y = top
    for label, a_hits, b_hits, is_key in rows:
        ty = y + 21
        css = "t-strong" if is_key else "t"
        parts.append(f'<text class="{css}" x="18" y="{ty}">{_esc(label)}</text>\n')
        for index, hits in enumerate((a_hits, b_hits)):
            x = col_x[index]
            if hits == 3:
                klass, tcls = "box-good", "t-good"
            elif hits == 0:
                klass, tcls = "box-bad", "t-bad"
            else:
                klass, tcls = "box", "t-sm"
            parts.append(
                f'<rect class="{klass}" x="{x}" y="{y}" width="{col_w}" height="28" rx="4"/>\n'
            )
            parts.append(
                f'<text class="{tcls}" x="{x + col_w / 2:.1f}" y="{ty}" '
                f'text-anchor="middle" style="font-weight:700">{hits}/3</text>\n'
            )
        y += row_h

    y += 6
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="684" height="64" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 20}">'
        "②「金額を直接聞く」が出した月額は 1,380円・1,380円・1,000円前後。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 38}">'
        "真値980円と一致した回は6回中0回（①は料金を金額で書かないので、外す以前に出ない）。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 56}">'
        "＝枠組みは聞いてよい。料金と、条件の限定語は原文を見る。</text>\n"
    )
    y += 64 + 12

    height = y + 8
    alt = (
        "AIに聞いた6回の結果を、項目ごとに「① 素朴に聞く」「② 金額を直接聞く」の"
        "2列で並べた表。各欄は3回中の回数。"
        "過去3か月・500万回・フォロワー500人が3/3と3/3、"
        "Stripe経由で受け取ることが3/3と3/3、"
        "プレミアム加入にお金がかかることが3/3と3/3、"
        "最小入金額の金額（10ドル）が0/3と3/3、"
        "ベーシックでは申請できないことが0/3と3/3、"
        "フォロワーの「認証済み」という限定が0/3と0/3、"
        "プレミアムの料金を金額で書いたが0/3と3/3、"
        "その金額が合っていた（月980円）が0/3と0/3。"
        "副題に、真値は公式ページの値（日本・ウェブ購入で月980円・"
        "認証済みフォロワー500人以上）だと書かれている。"
        "最下段の注記は3行で、②が出した値が1,380円・1,380円・1,000円前後であること、"
        "真値980円と一致した回は6回中0回であること（①は料金を金額で書かないので、外す以前に出ない）、"
        "枠組みは聞いてよいが料金と条件の限定語は原文を見る、という結論。"
    )
    (OUT / "x-ai-hit-and-miss.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def x_subscription_97_chart() -> None:
    """サブスクの「最大97%」が定価の97%ではないことを、原文の内訳例で見せる。

    原文の転記（2026-08-29確認）。5.00ドル→Apple 1.50→3.50→97%→3.39。
    67.8% はこの記事の割り算。
    """
    stages = [
        ("サブスクの金額（iOSアプリ経由）", 5.00, ""),
        ("Appleのアプリ内購入手数料 30% を引く", 3.50, "－1.50ドル"),
        ("残った額の最大97%がクリエイターへ", 3.39, ""),
    ]
    label_x = 18
    bar_x = 330
    max_bar_w = 250
    top = 116
    row_h = 46

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "「最大97%」は、5.00ドルの97%ではない</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "Xのサブスクリプション（フォロワーが払う側の道）。"
        "原文の内訳例4行に、差引後の額を補って並べた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "97%が掛かるのは「アプリ内購入手数料を差し引いた後」の3.50ドル。定価には掛からない。</text>\n",
        f'<text class="t-xs" x="{bar_x}" y="{top - 20}">残額（ドル）</text>\n',
    ]

    y = top
    for label, amount, delta in stages:
        ty = y + 18
        parts.append(f'<text class="t" x="{label_x}" y="{ty}">{_esc(label)}</text>\n')
        w = max(4, round(max_bar_w * amount / 5.00))
        cls = "bar-out" if amount in (5.00, 3.39) else "bar-in"
        parts.append(
            f'<rect class="{cls}" x="{bar_x}" y="{ty - 15}" width="{w}" height="20" rx="3"/>\n'
        )
        text = f"{amount:.2f}ドル" + (f"（{delta}）" if delta else "")
        parts.append(
            f'<text class="t-strong" x="{bar_x + w + 8}" y="{ty}">{_esc(text)}</text>\n'
        )
        y += row_h

    y += 8
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="684" height="46" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 20}">'
        "手元に残る3.39ドルは、定価5.00ドルの67.8%（この割合はこの記事の割り算）。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 38}">'
        "引かれた合計1.61ドル（5.00−3.39。この引き算も記事のもの）のうち1.50ドルはApple。</text>\n"
    )
    y += 46

    notes = [
        ("t-sm", "※ この内訳例はiOSアプリで購入された場合のみ。ウェブ経由は含まれないと原文が明記している。"),
        ("t-xs", "※ 原文には「0.10ドル - 収益からXが得る最低金額」の行も併記されている。"),
        ("t-xs", "※ サブスクの最低支払額は50ドル。収益配分（10ドル）とは別の数字なので混ぜない。"),
    ]
    y += 24
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y + 10
    alt = (
        "Xのサブスクリプションが1件売れたときの残額を、横棒3本で上から並べた図。"
        "1本目はサブスクの金額5.00ドル（iOSアプリ経由）。"
        "2本目はAppleのアプリ内購入手数料30%を引いた3.50ドル（−1.50ドル）。"
        "3本目は残った額の最大97%がクリエイターへ渡った3.39ドル。"
        "つまり最大97%は定価5.00ドルではなく、手数料を引いた後の額に掛かる。"
        "下の枠には、手元に残る3.39ドルは定価の67.8%（この割合は記事の割り算）、"
        "引かれた合計1.61ドル（5.00−3.39。この引き算も記事のもの）のうち1.50ドルはApple、と書かれている。"
        "さらに3つの注記——この内訳例はiOSアプリで購入された場合のみでウェブ経由は含まれないこと、"
        "原文には「0.10ドル - 収益からXが得る最低金額」の行も併記されていること、"
        "サブスクの最低支払額50ドルは収益配分の10ドルとは別の数字であること。"
    )
    (OUT / "x-subscription-97.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def youtube_payout_ladder_chart() -> None:
    """YouTubeの振込までにある、金額の関所（しきい値）を5段で並べる。

    原文の転記（2026-08-30確認・support.google.com/adsense/answer/1709871）。
    5行あるうち「お支払い」だけが実際の振込ライン。
    """
    rows = [
        ("① 税務情報", "なし", "box-quiet", "t"),
        ("② 認証（本人確認PIN）", "$10 相当額", "box-quiet", "t"),
        ("③ お支払い方法選択", "¥1,000", "box-quiet", "t"),
        ("④ お支払い（実際の振込）", "¥8,000", "box-good", "t-good"),
        ("⑤ キャンセル", "¥1,000", "box-quiet", "t"),
    ]
    box_x, box_w = 18, 684
    row_h = 44
    top = 96
    amount_x = box_x + box_w - 150  # 左端から固定距離。最長の amount 文字列でも右にはみ出さない幅を確保

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "振込までの「金額の関所」は、5段ある</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "AdSense「お支払い基準額」ページの日本円の表を、そのまま5行として並べた（2026-08-30確認）。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "実際に銀行口座へ振り込まれるラインは④だけ。①〜③・⑤は別の目的の基準額。</text>\n",
    ]

    y = top
    for label, amount, klass, tcls in rows:
        parts.append(f'<rect class="{klass}" x="{box_x}" y="{y}" width="{box_w}" height="{row_h - 8}" rx="6"/>\n')
        parts.append(f'<text class="t-strong" x="{box_x + 16}" y="{y + 24}">{_esc(label)}</text>\n')
        parts.append(
            f'<text class="{tcls}" x="{amount_x}" y="{y + 24}" style="font-weight:700">{_esc(amount)}</text>\n'
        )
        y += row_h

    y += 10
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="684" height="64" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 20}">'
        "AIに「金額の基準は何段階ありますか」と3回聞くと、3回とも「2段階」と答えた。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 38}">'
        "挙げたのは②（PIN確認）と④（お支払い）だけ。③と⑤には3回とも触れなかった。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 56}">'
        "米ドル口座の④は$100。①〜③・⑤は米ドルでも別の額（原文の別表）。</text>\n"
    )
    y += 64 + 12

    height = y + 8
    alt = (
        "YouTubeの収益が銀行口座に届くまでにある、金額の関所を5段で上から並べた図。"
        "①税務情報＝なし、②認証（本人確認PIN）＝10ドル相当額、③お支払い方法選択＝1,000円、"
        "④お支払い（実際の振込）＝8,000円、⑤キャンセル＝1,000円。④だけが緑で強調され、"
        "実際に銀行口座へ振り込まれるラインだと注記されている。"
        "下の枠には、AIに「金額の基準は何段階ありますか」と3回聞くと3回とも「2段階」と答えたこと、"
        "挙げたのは②と④だけで③と⑤には3回とも触れなかったこと、"
        "米ドル口座の④は100ドルで①〜③・⑤は米ドルでも別の額であることが書かれている。"
    )
    (OUT / "youtube-payout-ladder.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def youtube_ai_hit_and_miss_chart() -> None:
    """YouTubeの各質問で、AIの答えが真値と何回一致したかを並べる。

    実測（2026-08-30・claude -p を空ディレクトリで独立実行・各3回）。
    判定は docs/evidence/_raw/youtube-payout-thresholds/judge.py の出力から。
    """
    # (label, 3回中の回数, "good"=多いほど良い / "bad"=多いほど問題)
    rows = [
        ("ウォッチページ広告＝55%が正解", 3, "good"),
        ("Shorts広告＝45%が正解", 2, "good"),
        ("メンバーシップ等＝70%が正解", 3, "good"),
        ("振込の最低額＝8,000円が正解", 3, "good"),
        ("しきい値は5段階（真値）と答えた", 0, "good"),
        ("Shorts＝55%と誤答（長尺と混同）", 1, "bad"),
        ("現行に無い「登録者500人」条件", 1, "bad"),
    ]
    label_w = 330
    col_w = 200
    col_x = 18 + label_w
    top = 122
    row_h = 32

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "枠組みと料率は当たる。「何段階あるか」は外れる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "実測2026-08-30。ウェブ検索を切ったAI（claude -p・独立プロセス）に、各質問を3回ずつ。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "上5行＝真値と一致した回数（多いほど良い）。下2行＝誤り・作り話をした回数（少ないほど良い）。</text>\n",
    ]
    parts.append(
        f'<text class="t-xs" x="{col_x + col_w / 2:.1f}" y="{top - 14}" '
        f'text-anchor="middle">3回中</text>\n'
    )

    y = top
    for label, hits, kind in rows:
        ty = y + 21
        parts.append(f'<text class="t" x="18" y="{ty}">{_esc(label)}</text>\n')
        if kind == "good":
            klass, tcls = ("box-good", "t-good") if hits == 3 else (
                ("box-bad", "t-bad") if hits == 0 else ("box", "t-sm")
            )
        else:
            klass, tcls = ("box-good", "t-good") if hits == 0 else ("box-bad", "t-bad")
        parts.append(f'<rect class="{klass}" x="{col_x}" y="{y}" width="{col_w}" height="26" rx="4"/>\n')
        parts.append(
            f'<text class="{tcls}" x="{col_x + col_w / 2:.1f}" y="{ty}" '
            f'text-anchor="middle" style="font-weight:700">{hits}/3</text>\n'
        )
        y += row_h

    y += 6
    parts.append(f'<rect class="box-accent" x="18" y="{y}" width="684" height="64" rx="6"/>\n')
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 20}">'
        "料率と最低額は3回中2〜3回、正確に当たった（Shortsの45%だけ1回が長尺と同じ55%に化けた）。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 38}">'
        "「段階数」を聞くと3回とも2段階どまりで、公式の表にある5行には届かなかった。</text>\n"
    )
    parts.append(
        f'<text class="t-accent" x="34" y="{y + 56}">'
        "＝率と最低額は聞いてよい。「これで全部か」は原文の表を自分で見る。</text>\n"
    )
    y += 64 + 12

    height = y + 8
    alt = (
        "YouTubeについてAIに聞いた各質問の結果を並べた表。上5行は真値と一致した回数（3回中）で、"
        "ウォッチページ広告＝55%が3/3、Shorts広告＝45%が2/3、メンバーシップ等＝70%が3/3、"
        "振込の最低額＝8,000円が3/3、しきい値は5段階（真値）と答えた回数は0/3で赤。"
        "下2行は誤り・作り話をした回数（少ないほど良い）で、"
        "Shorts＝55%と長尺の55%を混同して誤答した回数が1/3、"
        "現行の公式ページに無い「登録者500人」条件を書いた回数が1/3、いずれも赤。"
        "下の枠には、料率と最低額は3回中2〜3回正確に当たったこと、"
        "段階数を聞くと3回とも2段階どまりで公式の表の5行には届かなかったこと、"
        "率と最低額は聞いてよいが「これで全部か」は原文の表を自分で見る、という結論が書かれている。"
    )
    (OUT / "youtube-ai-hit-and-miss.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def mixed_folder_count_vs_leak_chart() -> None:
    """無関係な資料を増やしても、答えに紛れ込んだ受付番号は0のままだったことを示す横棒グラフ。

    実測（2026-08-31）。当日の受付ログ・連絡メモ・判定基準の3点に、
    無関係な資料（献立表・先月ログ・別部署メモ・旧判定基準）を0〜4本足した
    5つの版を、各2回・計10回試した。棒は「混ぜた無関係資料の本数」、
    右のラベルが「答えに紛れ込んだ件数（分母は試行回数）」。
    """
    rows = [
        ("(a) 関係する3本だけ", 0, "0/2"),
        ("(b) ＋献立表を1本", 1, "0/2"),
        ("(c) ＋無関係4本を混ぜる", 4, "0/2"),
        ("(d) (c)＋「使わないで」を明記", 4, "0/2"),
        ("(e) (c)＋「使った資料を書いて」", 4, "0/2"),
    ]
    label_x, label_w = 18, 250
    plot_x = label_x + label_w
    plot_w = 260
    top = 130
    row_h = 40
    unit = plot_w / 4.0
    bar_h = 16

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "無関係な資料を4本まで増やしても、混入は0のままだった</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "当日の受付ログ・連絡メモ・判定基準の3点に、無関係な資料を0〜4本混ぜた5つの版を、"
        "各2回・計10回試した。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "棒＝混ぜた無関係資料の本数。右の分数＝答えに紛れ込んだ件数／試行回数。</text>\n",
        '<text class="t-bad" x="18" y="86">'
        "※ 先月ログには、今日の基準に当てはめると該当しそうに見える5件を仕込んだが、"
        "10回とも1件も出てこなかった。</text>\n",
    ]
    for v in (0, 1, 2, 3, 4):
        gx = plot_x + v * unit
        parts.append(
            f'<path class="line" d="M{gx:.1f} {top - 6} L{gx:.1f} '
            f'{top + row_h * len(rows) - 22}" stroke-dasharray="3 4"/>\n'
        )
        parts.append(
            f'<text class="t-xs" x="{gx:.1f}" y="{top - 12}" '
            f'text-anchor="middle">{v}本</text>\n'
        )

    y = top
    for label, val, frac in rows:
        ty = y + 14
        parts.append(f'<text class="t" x="{label_x}" y="{ty + 5}">{_esc(label)}</text>\n')
        w = max(val * unit, 2.0)
        parts.append(
            f'<rect class="bar-old" x="{plot_x:.1f}" y="{ty - 11}" '
            f'width="{w:.1f}" height="{bar_h}" rx="2"/>\n'
        )
        parts.append(
            f'<text class="t-good" x="{plot_x + plot_w + 14:.1f}" y="{ty + 2}">'
            f"混入 {frac}</text>\n"
        )
        y += row_h

    y += 4
    notes = [
        "5版とも、該当5件（S-2601・S-2606・S-2607・S-2609・S-2611）は10回とも一致した。",
        "旧い判定基準（2か所だけ新基準と違う）を使ってしまった回も、10回中0回だった。",
    ]
    for text in notes:
        parts.append(f'<text class="t-xs" x="18" y="{y}">{_esc(text)}</text>\n')
        y += 19

    height = y + 6
    alt = (
        "無関係な資料を混ぜた本数（0〜4本）を横棒で示し、その右に答えに紛れ込んだ件数を"
        "試行回数分の分数で示した図。関係する3本だけの版・献立表を1本足した版・"
        "無関係4本を混ぜた版・使わないでと明記した版・使った資料を書かせた版の5つとも、"
        "混入は0/2で、10回通しても0/10だった。先月ログには今日の基準に当てはめると"
        "該当しそうに見える5件をわざと仕込んだが、10回とも1件も答えに出てこなかった。"
        "5版とも該当5件は10回とも一致し、旧い判定基準を使ってしまった回も0回だった。"
    )
    (OUT / "mixed-folder-count-vs-leak.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def mixed_folder_old_vs_new_criteria_chart() -> None:
    """当日の12件を、新基準・旧基準それぞれで該当/非該当に分けた内訳グリッド。

    実測（2026-08-31）。旧い判定基準は新しい基準と2か所だけ違う
    （人数の閾値と、キャンセル待ちの例外救済の有無）。その差から、
    新旧で判定が割れる行が3件生まれるように材料を作った。
    """
    cols = [
        ("S-2601", "○", "○", ""),
        ("S-2602", "×", "○", "旧のみ"),
        ("S-2603", "×", "×", ""),
        ("S-2604", "×", "×", ""),
        ("S-2605", "×", "×", ""),
        ("S-2606", "○", "×", "新のみ"),
        ("S-2607", "○", "○", ""),
        ("S-2608", "×", "×", ""),
        ("S-2609", "○", "○", ""),
        ("S-2610", "×", "○", "旧のみ"),
        ("S-2611", "○", "○", ""),
        ("S-2612", "×", "×", ""),
    ]
    top = 156
    col_w = 54
    left = 18
    row_h = 26

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "12件のうち3件は、新旧どちらの基準を使うかで結果が変わる</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "旧い判定基準は新しい基準と2か所だけ違う（人数の閾値3名→4名／</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "キャンセル待ちの例外救済の有無）。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "その2か所から、新旧で判定が割れる行が3件生まれる。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "10回の実測は、すべて新基準の列どおりだった。</text>\n",
        '<text class="t-bad" x="18" y="124">'
        "赤＝新旧で判定が割れた行（S-2602・S-2606・S-2610）。</text>\n",
        '<text class="t-bad" x="18" y="143">'
        "この3件のうち1件でも旧基準側に寄れば「混入」と分かる仕込み。</text>\n",
    ]

    headers = ["受付番号", "新基準", "旧基準", ""]
    hx = left
    for h in headers:
        w = col_w * 2 if h == "受付番号" else col_w
        parts.append(f'<text class="t-sm" x="{hx + 4}" y="{top - 8}">{_esc(h)}</text>\n')
        hx += w

    y = top
    for rid, new_v, old_v, diff in cols:
        row_bg = "box-bad" if diff else "box"
        parts.append(
            f'<rect class="{row_bg}" x="{left}" y="{y}" width="{col_w * 5}" '
            f'height="{row_h - 4}" rx="3"/>\n'
        )
        parts.append(f'<text class="mono" x="{left + 8}" y="{y + 15}">{rid}</text>\n')
        for i, val in enumerate((new_v, old_v)):
            cls = "t-good" if val == "○" else "t-xs"
            parts.append(
                f'<text class="{cls}" x="{left + col_w * 2 + col_w * i + 20:.1f}" '
                f'y="{y + 15}" text-anchor="middle">{val}</text>\n'
            )
        if diff:
            parts.append(
                f'<text class="t-bad" x="{left + col_w * 4 + 8:.1f}" y="{y + 15}">'
                f"{_esc(diff)}</text>\n"
            )
        y += row_h

    y += 10
    parts.append(
        f'<text class="t-strong" x="18" y="{y}">'
        "実測10回とも、答えは新基準の列（5件）と一致した</text>\n"
    )
    y += 22

    height = y + 8
    alt = (
        "本日ログ12件を、新基準・旧基準それぞれで該当（○）か非該当（×）かに分けた表。"
        "S-2601・S-2607・S-2609・S-2611は新旧とも○。S-2603・S-2604・S-2605・S-2608・"
        "S-2612は新旧とも×。S-2602とS-2610は旧基準だけ○（人数の閾値が3名のため）、"
        "S-2606は新基準だけ○（キャンセル待ちの例外救済があるため）。"
        "この3件が赤で示され、実測10回はすべて新基準の列（5件）と一致したと書かれている。"
    )
    (OUT / "mixed-folder-old-vs-new-criteria.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini35cu_timeline_chart() -> None:
    """画面操作が3.5 Flashに載ってから、推奨モデルの座を3.7 Flashに渡すまでの日数。

    出典＝Google の発表ページ（画面操作の標準搭載・2026-06-24）、
    Gemini 3.5 Flash モデルカード（発表日 2026-05-19）、
    Gemini 3.7 Flash 発表（2026-08-13）、
    ai.google.dev の Computer use ドキュメント（最終更新 2026-08-26）。
    日数はいずれも暦日の単純な引き算（この記事で計算）。
    """
    rows = [
        ("2026年5月19日", "Gemini 3.5 Flash を発表", "この時点では、画面操作（Computer Use）は搭載されていない"),
        ("2026年6月24日（36日後）", "画面操作を標準搭載", "Gemini API・Gemini Enterprise Agent Platform ですぐ使える"),
        ("2026年8月13日（+50日）", "Gemini 3.7 Flash を発表", "ドキュメントの「推奨モデル」が3.7 Flashに交代"),
        ("2026年8月26日（この記事の確認時点）", "ドキュメント最終更新", "3.5 Flashは「Previous stable model」と説明されている"),
    ]
    dot_x = 26
    text_x = 50
    top = 96
    row_h = 60

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "画面操作が標準搭載されてから、推奨モデルが交代するまで50日</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "Gemini 3.5 Flash に画面操作が載ったのは発表の36日後。そこから50日で、"
        "公式ドキュメントの推奨モデルは次の世代に移りました。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "日数はいずれも暦日の引き算です（この記事で計算）。</text>\n",
    ]

    last_y = top + (len(rows) - 1) * row_h
    parts.append(
        f'<line class="line" x1="{dot_x}" y1="{top}" x2="{dot_x}" y2="{last_y}"/>\n'
    )
    for index, (date_label, title, desc) in enumerate(rows):
        cy = top + index * row_h
        cls = "box-accent" if index in (1, 2) else "box-quiet"
        parts.append(f'<circle class="{cls}" cx="{dot_x}" cy="{cy}" r="7"/>\n')
        parts.append(
            f'<text class="t-xs" x="{text_x}" y="{cy - 8}">{_esc(date_label)}</text>\n'
        )
        parts.append(
            f'<text class="t-strong" x="{text_x}" y="{cy + 10}">{_esc(title)}</text>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{text_x}" y="{cy + 27}">{_esc(desc)}</text>\n'
        )

    height = last_y + 56
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 34}">'
        "※ 「推奨モデル」はドキュメントの Model versions 節の記載です。"
        "3.5 Flash 自体が使えなくなったわけではありません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 16}">'
        "※ 3.6 Flash・3.5 Flash-Lite も画面操作に対応していますが、"
        "この図では日付が確認できた3点だけを示しています。</text>\n"
    )

    alt = (
        "Gemini の画面操作機能の年表。2026年5月19日にGemini 3.5 Flashを発表"
        "（この時点では画面操作は搭載されていない）。その36日後の6月24日、"
        "画面操作をGemini API・Gemini Enterprise Agent Platform経由で標準搭載。"
        "さらに50日後の8月13日にGemini 3.7 Flashを発表し、公式ドキュメントの"
        "推奨モデルが3.7 Flashに交代した。8月26日（この記事の確認時点）でも"
        "ドキュメントは3.5 Flashを「Previous stable model」と説明している。"
        "日数はいずれも暦日の単純な引き算。"
    )
    (OUT / "gemini35cu-timeline.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini35cu_osworld_chart() -> None:
    """OSWorld-Verified（画面操作の実力を測るベンチマーク）の6モデル比較。

    出典＝Gemini 3.5 Flash モデルカード（deepmind.google/models/model-cards/gemini-3-5-flash）。
    「Results as of May, 2026」の表から、UI Control / OSWorld-Verified の行をそのまま写した。
    """
    rows = [
        ("GPT-5.5", 78.7, "bar-old"),
        ("Gemini 3.5 Flash", 78.4, "bar-new"),
        ("Claude Opus 4.7", 78.0, "bar-old"),
        ("Gemini 3.1 Pro", 76.2, "bar-old"),
        ("Claude Sonnet 4.6", 72.5, "bar-old"),
        ("Gemini 3 Flash", 65.1, "bar-old"),
    ]
    left, right = 232, 650
    span = right - left
    scale = span / 100.0
    top, bar_h, row_gap = 88, 22, 14
    pitch = bar_h + row_gap

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "画面操作の実力テストで、3.5 Flashは自社の旧世代より他社に近い</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "OSWorld-Verified（パソコンを実際に操作させて採点するテスト）の点数。"
        "Googleのモデルカードに載っている6モデルです。</text>\n",
    ]
    for index, (name, value, cls) in enumerate(rows):
        y = top + index * pitch
        bw = value * scale
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 6}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" '
            f'width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{y + bar_h - 6}">'
            f"{value:g}%</text>\n"
        )

    height = top + len(rows) * pitch + 62
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 46}">'
        "※ 表を作ったのはGoogleです。他社が同じ条件で測った値ではありません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        "※ 比較に使われた他社モデルは2026年5月時点の世代です"
        "（Claude Sonnet 4.6・Opus 4.7、GPT-5.5）。今の最新世代ではありません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ このテストの名前はOSWorld-Verified。別記事のOSWorld-2.0とは版が違うため、"
        "そちらの数字とは並べていません。</text>\n"
    )
    alt = (
        "OSWorld-Verified（画面操作の実力を測るベンチマーク）の点数を6モデルで比べた横棒グラフ。"
        "GPT-5.5が78.7%、Gemini 3.5 Flashが78.4%、Claude Opus 4.7が78.0%、"
        "Gemini 3.1 Proが76.2%、Claude Sonnet 4.6が72.5%、Gemini 3 Flashが65.1%。"
        "Gemini 3.5 Flashは自社の旧世代（Gemini 3 Flash・3.1 Pro）より高く、"
        "他社の当時の最上位（GPT-5.5・Claude Opus 4.7）とほぼ並ぶ。"
        "表を作ったのはGoogleであり、他社が同じ条件で測った値ではない。"
        "比較に使われた他社モデルは2026年5月時点の世代。"
    )
    (OUT / "gemini35cu-osworld.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def gemini35cu_actions_chart() -> None:
    """3社の「画面操作」ツールで、1回に呼べる操作の種類がいくつあるか。

    出典＝Gemini: ai.google.dev/gemini-api/docs/computer-use の環境別の表を数えた。
    Anthropic: platform.claude.com の computer use tool ページ「17 member tools」。
    OpenAI: developers.openai.com の computer use ガイド「Possible Computer use actions」の列挙。
    """
    rows = [
        ("Gemini（ブラウザ環境）", 20, "bar-new"),
        ("Gemini（デスクトップ環境）", 17, "bar-new"),
        ("Anthropic（デスクトップのみ）", 17, "bar-in"),
        ("Gemini（モバイル環境）", 10, "bar-new"),
        ("OpenAI（gpt-5.6のcomputerツール）", 9, "bar-old"),
    ]
    left, right = 288, 650
    span = right - left
    biggest = max(v for _, v, _ in rows)
    scale = span / biggest
    top, bar_h, row_gap = 88, 22, 14
    pitch = bar_h + row_gap

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "同じ「画面操作」でも、1回に呼べる操作の数は会社ごとに違う</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "各社のドキュメントに列挙されている操作（クリック・型・スクロール等）の総数です。</text>\n",
    ]
    for index, (name, value, cls) in enumerate(rows):
        y = top + index * pitch
        bw = value * scale
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 6}">{_esc(name)}</text>\n')
        parts.append(
            f'<rect class="{cls}" x="{left}" y="{y}" '
            f'width="{bw:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-sm" x="{left + bw + 8:.1f}" y="{y + bar_h - 6}">'
            f"{value}個</text>\n"
        )

    height = top + len(rows) * pitch + 62
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 46}">'
        "※ OpenAIのclickは1つの操作にボタン（左/右/中央）を渡す形なので、"
        "右クリックや中央クリックのぶんは別の操作として数えていません。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 28}">'
        "※ Anthropicは画面操作（デスクトップ）とは別に、ブラウザ専用の"
        "「browser use tool」を別立てで用意しています（この図には含めていません）。</text>\n"
    )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 10}">'
        "※ 操作の粒度が違うので、数が多いほど高性能というわけではありません。</text>\n"
    )
    alt = (
        "3社の画面操作ツールで、1回に呼べる操作の種類の数を比べた横棒グラフ。"
        "Geminiのブラウザ環境が20個、Geminiのデスクトップ環境が17個、"
        "Anthropicのデスクトップ専用ツールが17個、Geminiのモバイル環境が10個、"
        "OpenAIのgpt-5.6のcomputerツールが9個。"
        "OpenAIのclickはボタン（左・右・中央）を引数で渡す形なので、"
        "右クリックや中央クリックは別の操作として数えていない。"
        "Anthropicは画面操作とは別にブラウザ専用のbrowser use toolを持つが、"
        "この図には含めていない。"
    )
    (OUT / "gemini35cu-actions.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def expense_rule_category_agreement_chart() -> None:
    """経費規程の判定を3回とって見比べた結果。カテゴリ別・食い違いゼロ。

    実測（2026-09-01・架空の経費規程7条×申請一覧2本、各24件）。同じ指示文を
    新規のサブエージェントで材料ごとに3回ずつ＝6回、のべ144件の判定を送った。
    3回の答えが割れた項目・真値と食い違った項目とも0件だった。
    """
    rows = [
        ("素直に1条へ当たる申請（20件）", 20, 20),
        ("隣接条・除外条項と紛らわしい申請（12件）", 12, 12),
        ("規程のどこにも無い申請（16件）", 16, 16),
    ]
    left, right = 300, 620
    span = right - left
    top, bar_h, gap = 108, 32, 30

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "3回そろって正解した件数（材料A・Bあわせて48件）</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "架空の経費規程7条に照らして、申請一覧24件×2本を、新規の会話で3回ずつ判定させた。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "3回の答えが割れた項目、真値と食い違った項目は、どちらも0件だった。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "「紛らわしい」12件には、除外条項に当たる5件・上限超過でも条文自体は該当する1件を含む。</text>\n",
    ]
    for index, (label, hit, total) in enumerate(rows):
        y = top + index * (bar_h + gap)
        parts.append(f'<text class="t" x="18" y="{y + bar_h - 10}">{_esc(label)}</text>\n')
        parts.append(
            f'<rect class="box-quiet" x="{left}" y="{y}" '
            f'width="{span}" height="{bar_h}" rx="3"/>\n'
        )
        ratio = hit / total
        parts.append(
            f'<rect class="box-good" x="{left}" y="{y}" '
            f'width="{span * ratio:.1f}" height="{bar_h}" rx="3"/>\n'
        )
        parts.append(
            f'<text class="t-good" x="{right + 12}" y="{y + bar_h - 10}">'
            f"{hit} / {total}件</text>\n"
        )

    height = top + len(rows) * (bar_h + gap) + 26
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 14}">'
        "※ 判定はのべ144件（24件×2材料×3回）。生の回答は docs/evidence/ に全文置いてある。</text>\n"
    )
    alt = (
        "経費規程の該当条文を3回ずつ判定させた結果を、カテゴリ別に示した横棒グラフ。"
        "素直に1条へ当たる申請20件は20件とも3回そろって正解、"
        "隣接条・除外条項と紛らわしい申請12件も12件とも正解、"
        "規程のどこにも無い申請16件も16件とも正解で、3種類とも100%だった。"
        "判定はのべ144件で、3回の答えが割れた項目・真値と食い違った項目はどちらも0件。"
    )
    (OUT / "expense-rule-category-agreement.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


def expense_rule_trap_grid_chart() -> None:
    """わざと誤読しやすくした申請8件が、3回とも正しく判定できたかのマス目。

    実測（2026-09-01）。OR条件の見落とし・姻族の一親等・キーワードに
    引っ張られる誤読など、あらかじめ狙いを決めた「罠」を8件仕込んだが、
    3回×8件＝24回の判定は24回とも真値と一致した。
    """
    rows = [
        ("深夜だが電車もあった(1条)", [1, 1, 1]),
        ("配偶者の父(義父)の死亡(5条)", [1, 1, 1]),
        ("社内送別会+取引先1名(3条)", [1, 1, 1]),
        ("21:55・他に手段なし(1条)", [1, 1, 1]),
        ("私物WiFiルーター代(6条)", [1, 1, 1]),
        ("貸与端末の私用分請求(該当なし)", [1, 1, 1]),
        ("宿泊キャンセル料(該当なし)", [1, 1, 1]),
        ("資格の再受験料(7条)", [1, 1, 1]),
    ]
    cols = ["1回目", "2回目", "3回目"]
    label_w = 262
    cell_w, cell_h, gap = 110, 30, 8
    top = 145
    pitch = cell_h + gap
    grid_x = 18 + label_w
    right_edge = grid_x + len(cols) * (cell_w + gap) - gap
    assert right_edge <= WIDTH - 18, right_edge

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "わざと仕込んだ「罠」8件も、3回とも正しく読めた</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "OR条件の見落とし・姻族の一親等・キーワードに引っ張られる誤読を、狙って仕込んだ8件。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "例：「22時以降なら電車が使えてもタクシー代は対象」というOR条件の読み違いを狙った1件目。</text>\n",
        '<text class="t-sm" x="18" y="83">'
        "新規の会話で3回判定させ、セルの◯＝その回で真値と一致（×は不一致・今回は0件）。</text>\n",
        '<text class="t-sm" x="18" y="102">'
        "※ 判定コードが正しいかどうかは別に確かめてある（★24＝計測器も先に疑う）。</text>\n",
    ]
    for index, name in enumerate(cols):
        x = grid_x + index * (cell_w + gap)
        parts.append(
            f'<text class="t-xs" x="{x + cell_w / 2 - 10:.1f}" y="{top - 12}">{name}</text>\n'
        )

    for row_index, (label, values) in enumerate(rows):
        y = top + row_index * pitch
        parts.append(
            f'<text class="t-sm" x="18" y="{y + cell_h / 2 + 5:.0f}">{_esc(label)}</text>\n'
        )
        for col_index, v in enumerate(values):
            x = grid_x + col_index * (cell_w + gap)
            ok = v == 1
            box = "box-good" if ok else "box-bad"
            tone = "t-good" if ok else "t-bad"
            parts.append(
                f'<rect class="{box}" x="{x}" y="{y}" '
                f'width="{cell_w}" height="{cell_h}" rx="4"/>\n'
            )
            text = "○ 一致" if ok else "× 不一致"
            tx = x + cell_w / 2 - len(text) * 5.2
            parts.append(
                f'<text class="{tone}" x="{tx:.1f}" y="{y + cell_h / 2 + 5:.0f}">{text}</text>\n'
            )

    height = top + len(rows) * pitch + 8 + 21 * 2 + 12
    notes = [
        ("t-xs", "架空の経費規程での実測。生の回答24件ぶんは docs/evidence/ に全文置いてある。"),
        ("t-xs", "この材料・この件数での結果であり、「AIは規程の罠を読み違えない」と一般化はしない。"),
    ]
    ny = height - 21 * len(notes) + 5
    for css, text in notes:
        parts.append(f'<text class="{css}" x="18" y="{ny}">{_esc(text)}</text>\n')
        ny += 21

    alt = (
        "OR条件の見落とし・姻族の一親等・キーワードに引っ張られる誤読を狙って仕込んだ申請8件を、"
        "3回ずつ判定させた結果のマス目。8件×3回＝24セルすべてが「○ 一致」（真値と一致）で、"
        "「× 不一致」は1件も無かった。"
    )
    (OUT / "expense-rule-trap-grid.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    mixed_folder_count_vs_leak_chart()
    mixed_folder_old_vs_new_criteria_chart()
    youtube_payout_ladder_chart()
    youtube_ai_hit_and_miss_chart()
    x_cash_flow_timeline_chart()
    x_ai_hit_and_miss_chart()
    x_subscription_97_chart()
    money_map_three_routes_chart()
    money_map_gates_timing_chart()
    resume_list_correctness_chart()
    resume_list_header_drift_chart()
    estimate_basis_count_chart()
    cron_delay_distribution_chart()
    cutoff_vs_resume_duplicate_chart()
    handoff_todo_version_hits_chart()
    handoff_todo_position_hits_chart()
    weekly_rate_boundary_crossed_chart()
    kindle_royalty_invented_band_chart()
    kindle_royalty_version_grid_chart()
    job_ai_policy_verdict_chart()
    job_ai_policy_v4_citation_chart()
    filler_source_detection_chart()
    filler_source_five_scale_chart()
    proposal_what_repeats_chart()
    proposal_answers_drift_chart()
    take_home_two_readings_chart()
    take_home_by_version_chart()
    formula_range_by_version_chart()
    formula_added_row_invisible_chart()
    pass_criteria_detection_chart()
    pass_criteria_by_fault_type_chart()
    handoff_memo_length_vs_values_chart()
    handoff_memo_next_row_chart()
    pfp9_arena_rank_chart()
    pfp9_five_tasks_chart()
    pfp9_h2_rmse_chart()
    pfp9_elements_chart()
    daybreak_bedrock_vs_direct_chart()
    daybreak_blue_same_price_chart()
    daybreak_what_is_closed_chart()
    daybreak_vendor_shapes_chart()
    conditions_changed_what_survives_chart()
    delivery_note_claim_vs_flag_chart()
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
    brief_asked_side_only_chart()
    first_client_where_minutes_come_from_chart()
    receipt_category_drift_by_ask_chart()
    receipt_inside_or_outside_material_chart()
    breaking_checks_what_rings_chart()
    breaking_checks_who_finds_holes_chart()
    tilt_leaks_to_unwritten_judgment_chart()
    runbook_gaps_surface_chart()
    queue_blocked_row_where_it_goes_chart()
    queue_what_never_broke_chart()
    wrong_client_two_failures_chart()
    work_grew_what_comes_with_it_chart()
    copy_ideas_that_pass_chart()
    monthly_check_carryover_chart()
    broken_morning_who_decides_chart()
    broken_morning_causes_not_in_log_chart()
    unread_mark_where_it_lands_chart()
    unread_mark_line_position_chart()
    false_alarm_today_vs_tomorrow_chart()
    false_alarm_what_goes_blind_chart()
    qwen38_two_weights_chart()
    qwen38_vs_37_chart()
    qwen38_not_first_chart()
    qwen38_price_region_chart()
    append_shape_by_version_chart()
    append_shape_mixed_file_chart()
    reply_chase_count_by_version_chart()
    reply_changed_subject_chased_chart()
    chain_final_count_by_version_chart()
    chain_what_stage_one_passed_chart()
    three_samples_what_gets_shown_chart()
    three_samples_line_flips_chart()
    reply_template_line_by_version_chart()
    reply_template_grid_chart()
    date_decides_detect_and_decide_chart()
    date_decides_downstream_chart()
    deadline_holiday_grid_chart()
    material_match_vs_facts_chart()
    handoff_relative_terms_grid_chart()
    handoff_wrong_touch_total_chart()
    note_fee_payout_waterfall_chart()
    note_fee_rate_match_chart()
    kindle_disclosure_scenario_grid_chart()
    kindle_disclosure_no_citation_chart()
    note_payout_version_comparison_chart()
    handoff_summary_format_drift_grid_chart()
    handoff_summary_heading_length_chart()
    role_prompt_grid_chart()
    estimate_basis_count_chart()
    gemini35cu_timeline_chart()
    gemini35cu_osworld_chart()
    gemini35cu_actions_chart()
    expense_rule_category_agreement_chart()
    expense_rule_trap_grid_chart()
    print(f"{len(list(OUT.glob('*.svg')))}枚を {OUT} に出力しました")
