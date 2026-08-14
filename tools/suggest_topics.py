# -*- coding: utf-8 -*-
"""題材の候補を、勘ではなく「実際に打たれている言い回し」から集める。

2026-08-10 から手で4回やってきた手順を、道具にした。手でやっていた頃の記録は
`docs/superpowers/notes/2026-08-10-demand-research.md`（判断の理由もそこにある）。

🚨 **この道具は「候補を集める」ところで止まる。どれをキューに入れるかは決めない。**
2026-08-14 の実測で、実質語数の**上位3つが1件も採用にならなかった**
（note 186＝収益化でお金直球／コンサル 133＝業界と就職の話で読者像違い／
kindle 108＝出版でグレー）。**採否の理由は語数からは出てこない。**
機械が順位を付けてそのままキューへ入れる形にすると、この判断が丸ごと消える。

⚠️ **生の語数を信じないこと。**ノイズが2種あって、引かないと順位が入れ替わる:

  ① 種の `ai` が Google 側で**カタカナ「アイ」に転記**される
     （「アイ カツ カード メルカリ 相場」「アイ ラッシュ サロン 集客」）
  ② **AIツール自身の話**が混ざる（「chatgpt 請求書 ダウンロード」＝自分の課金明細、
     `ai note taker`＝英語の note で議事録アプリ・ノート端末）

実測: メルカリは128語のうち34語が①、請求書は57語のうち40語が②、
note は282語のうち92語が②だった。

使い方:
    python -m tools.suggest_topics automate      # 種の束を指定して1回
    python -m tools.suggest_topics --list        # 束の一覧
出力: docs/topic-candidates/<日付>-<束>.md
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = ROOT / "content" / "recipes"
QUEUE_PATH = ROOT / "content" / "_recipe_queue.md"
OUTPUT_DIR = ROOT / "docs" / "topic-candidates"

# ツール名。5つ固定（8/10 以来ずらしていない＝過去の回と語数を比べられるように）
TOOLS = ("chatgpt", "claude", "gemini", "生成ai", "ai")

# ⚠️ 意図語（「自動」「プロンプト」等）は入れない。採取を偏らせると、
# 「自動化の需要がある」が自分の種のせいなのか分からなくなる。
SUFFIXES = ("", "方法", "コツ", "例", "やり方",
            "あ", "い", "う", "か", "き", "こ", "さ", "し", "た", "な", "は")

# 種の束。⚠️ **一度使った束は、次は種を入れ替えること**（同じ種は同じ語しか返さない）。
# 使った日を書き足していく＝次に回す人が重複を避けられる。
SEED_BANKS: dict[str, tuple[str, ...]] = {
    # 2026-08-14 初回
    "automate": (
        "自動化", "定期実行", "自動返信", "通知", "リマインド",
        "集計", "転記", "仕分け", "バックアップ", "定型文",
        "ワークフロー", "連携", "効率化", "ルーティン", "一括",
    ),
    # 2026-08-13 実施済み（記録は notes の「2026-08-13 追加実行」節）
    "earn": (
        "副業", "稼ぐ", "収益化", "在宅ワーク", "ブログ", "アフィリエイト",
        "ライティング", "動画編集", "せどり", "ハンドメイド", "スキル販売",
        "クラウドソーシング", "インスタ運用", "ポートフォリオ", "確定申告",
    ),
    # 2026-08-13 実施済み（追加実行②）
    "safety": (
        "詐欺", "詐欺メール", "詐欺電話", "フィッシング", "偽サイト", "偽広告",
        "なりすまし", "ディープフェイク", "フェイク動画", "投資詐欺", "副業詐欺",
        "サポート詐欺", "乗っ取り", "見分け方", "個人情報",
    ),
    # 2026-08-13 実施済み（床割れの回復）
    "work": (
        "文字起こし", "アンケート", "マニュアル", "提案書", "データ入力",
        "グラフ", "スピーチ", "挨拶文", "クレーム対応", "面接",
        "自己PR", "手紙", "チラシ", "図解", "タスク管理",
    ),
}

# 情報収集・商用・無関係。8/10 の定型に、このサイトが書かない領域を足したもの。
DROP_WORDS = (
    "とは", "料金", "無料", "値段", "口コミ", "評判", "求人", "転職", "資格", "検定",
    "株", "投資", "fx", "仮想通貨", "ビットコイン", "トレード", "競馬", "パチンコ",
    "危険", "違法", "訴訟", "逮捕", "なんj", "2ch", "5ch", "知恵袋",
    "ログイン", "ダウンロード", "解約", "退会", "アンインストール",
)

# ノイズ①: 種の ai がカタカナ「アイ」に転記された誤ヒット
KATAKANA_AI_RE = re.compile(r"アイ ")

# ノイズ②: AIツール自身の話（副業や仕事の作業ではない）
SELF_TALK_RE = re.compile(
    r"(chatgpt|claude|gemini|openai)[^ ]* ?(請求書|課金|サブスク|支払|解約|領収|料金|プラン)"
    r"|請求書 ?(どこ|ダウンロード|確認|解約後|の住所|インボイス|発行|払い)"
    r"|note ?(taker|taking|air|app|amazon|apple|companion|converter|copilot|icon|ii|"
    r"in |ios|ipad|iphone|kickstarter|samsung|wearable|website|windows|native)"
    r"|notebooklm|notetaker|notion"
)


def suggest(query: str, timeout: int = 15) -> list[str]:
    """Google サジェストを1回叩く。⚠️ 件数は返ってこない（言い回しの種類だけ）。"""
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&hl=ja&"
           + urllib.parse.urlencode({"q": query}))
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))[1]


def is_noise(word: str) -> bool:
    """採取した語が、数えるに値しないか。⚠️ 落とした語は必ず表に出すこと。"""
    return bool(KATAKANA_AI_RE.search(word) or SELF_TALK_RE.search(word))


def is_off_topic(word: str) -> bool:
    return any(drop in word for drop in DROP_WORDS)


def sweep(seeds, tools=TOOLS, suffixes=SUFFIXES, fetch=suggest, pause: float = 0.1):
    """種×ツール×語尾を全部投げて、種ごとに語を集める。

    fetch を差し替えられるのはテストのため（本物の Google を叩かずに検査する）。
    ⚠️ 1回失敗したら1度だけ待って再試行し、それでも駄目なら数えて先へ進む。
    途中で止めると、どこまで採れたのか分からない中途半端な表ができる。
    """
    collected: dict[str, set[str]] = defaultdict(set)
    failures = 0
    for seed in seeds:
        for tool in tools:
            for suffix in suffixes:
                query = f"{tool} {seed} {suffix}".strip()
                for attempt in (1, 2):
                    try:
                        collected[seed].update(fetch(query))
                        break
                    except Exception:
                        if attempt == 2:
                            failures += 1
                        else:
                            time.sleep(1.0)
                if pause:
                    time.sleep(pause)
    return dict(collected), failures


def classify(collected: dict[str, set[str]]) -> list[dict]:
    """種ごとに 生 / ノイズ / 対象外 / 実質 に割る。全件どれかに入る（台帳5番）。"""
    rows = []
    for seed, words in collected.items():
        noise = sorted(w for w in words if is_noise(w))
        off = sorted(w for w in words if not is_noise(w) and is_off_topic(w))
        real = sorted(w for w in words if not is_noise(w) and not is_off_topic(w))
        rows.append({"seed": seed, "raw": len(words), "noise": noise,
                     "off_topic": off, "real": real})
    rows.sort(key=lambda r: -len(r["real"]))
    return rows


def existing_coverage(rows, recipes_dir=RECIPES_DIR, queue_path=QUEUE_PATH):
    """種の語が、既存記事とキューに出てくるかを見る。

    ⚠️ **語面の一致しか見ていない。**8/11 に実際に外している＝「プレゼン」は
    「ゼロ」と出たがスライドと同じ需要、「整理」は「あり」に見えたが該当記事は無かった。
    **束ねと最終判断は人がやること。**ここは目安。
    """
    articles = "\n".join(p.read_text(encoding="utf-8") for p in sorted(recipes_dir.glob("*.md")))
    queue = queue_path.read_text(encoding="utf-8") if queue_path.exists() else ""
    for row in rows:
        row["in_articles"] = row["seed"] in articles
        row["in_queue"] = row["seed"] in queue
    return rows


def report(bank: str, rows, failures: int, queries: int, today: date) -> str:
    raw = sum(r["raw"] for r in rows)
    real = sum(len(r["real"]) for r in rows)
    lines = [
        f"# 題材の候補 — {bank}（{today.isoformat()}）",
        "",
        f"`python -m tools.suggest_topics {bank}` の出力。",
        f"クエリ **{queries}**／失敗 {failures}／生 **{raw}**／実質 **{real}**"
        f"（ノイズと対象外を引いた残り）。",
        "",
        "🚨 **これは候補であって決定ではない。**採否の理由は語数からは出てこない",
        "（2026-08-14 は実質語数の上位3つが1件も採用にならなかった）。",
        "**入れるときは、キューの各節の縛りと既存記事との切り分けを必ず書くこと。**",
        "",
        "| 種 | 生 | ノイズ | 対象外 | **実質** | 既存記事 | キュー |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['seed']} | {r['raw']} | {len(r['noise'])} | {len(r['off_topic'])} | "
            f"**{len(r['real'])}** | {'あり' if r['in_articles'] else 'ゼロ'} | "
            f"{'あり' if r['in_queue'] else 'ゼロ'} |"
        )
    lines += ["", "⚠️ 「既存記事」「キュー」は**語面の一致だけ**を見た目安。",
              "束ねと最終判断は人がやること（8/11 に実際に外している）。", ""]

    for r in rows:
        if len(r["real"]) < 10:
            continue
        lines += [f"## {r['seed']}（実質 {len(r['real'])}語）", ""]
        lines += [f"- {w}" for w in r["real"][:60]]
        if len(r["real"]) > 60:
            lines.append(f"- …ほか {len(r['real']) - 60} 語")
        if r["noise"]:
            lines += ["", f"<details><summary>落としたノイズ {len(r['noise'])}語</summary>", ""]
            lines += [f"- {w}" for w in r["noise"][:20]]
            lines += ["", "</details>"]
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("--list", "-l"):
        print("種の束:")
        for name, seeds in SEED_BANKS.items():
            print(f"  {name:<10} {len(seeds)}語  {'・'.join(seeds[:5])}…")
        return 0
    bank = argv[0]
    if bank not in SEED_BANKS:
        print(f"知らない束: {bank}（--list で一覧）")
        return 1

    seeds = SEED_BANKS[bank]
    queries = len(seeds) * len(TOOLS) * len(SUFFIXES)
    print(f"{bank}: 種{len(seeds)} × ツール{len(TOOLS)} × 語尾{len(SUFFIXES)} = {queries} クエリ")

    collected, failures = sweep(seeds)
    rows = existing_coverage(classify(collected))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"{date.today().isoformat()}-{bank}.md"
    out.write_text(report(bank, rows, failures, queries, date.today()), encoding="utf-8")
    print(f"\n書き出し: {out}")
    for r in rows[:8]:
        print(f"  {r['seed']:<10} 生{r['raw']:>4}  実質{len(r['real']):>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
