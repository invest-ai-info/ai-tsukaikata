"""ココナラ「AI業務効率化・自動化」1ページ目（60件）を、出品タイトルの語だけで機械的に分ける。

分け方は上から順に当てる（先に当たった区分で決まる）。人の裁量を入れないため。
"""
import re, statistics, pathlib, collections

HERE = pathlib.Path(__file__).parent
RULES = [
    ("D 教える・相談",       r"教えます|相談|入門|レッスン"),
    ("F 指示書・プロンプト", r"指示書|プロンプト"),
    ("E 代行・伴走・成果物", r"代行|伴走|投稿を[^ ]*作ります|リストを作成|テスト対策を作成"),
    ("B 既製ツールを渡す",   r"ツールを提供|ツール提供|販売します|売ります"),
    ("A 注文で作る",         r"開発|構築|制作|作ります|アプリ化|実装|仕組みを導入|環境設定|導入支援|システム"),
]
TOOLS = ["n8n", "GAS", "Claude", "MCP", "NotebookLM", "WordPress", "MF/freee", "Zapier", "Make", "Dify", "GPT"]


def classify(title):
    for name, pat in RULES:
        if re.search(pat, title):
            return name
    return "C 自動化します（形はタイトルに無い）"


def main():
    rows = [l.rstrip("\n").split("\t") for l in (HERE / "page1_2026-09-18.tsv").open(encoding="utf-8")][1:]
    counts = collections.Counter()
    prices_by = collections.defaultdict(list)
    quote = collections.Counter()
    tool_hits = collections.Counter()
    out = []
    for no, title, price, q, rev, href in rows:
        c = classify(title)
        counts[c] += 1
        prices_by[c].append(int(price))
        if q == "1":
            quote[c] += 1
        for t in TOOLS:
            if t.lower() in title.lower():
                tool_hits[t] += 1
        out.append((int(no), c, int(price), q, title))
    prices = [int(r[2]) for r in rows]
    print(f"件数 {len(rows)} / 見積り必須 {sum(1 for r in rows if r[3]=='1')}")
    print(f"価格 最小 {min(prices):,} / 中央値 {statistics.median(prices):,.0f} / 平均 {statistics.mean(prices):,.0f} / 上位四分位 {statistics.quantiles(prices, n=4)[2]:,.0f} / 最大 {max(prices):,}")
    print("価格帯:", {k: sum(1 for p in prices if lo <= p < hi) for k, (lo, hi) in {"〜9,999": (0, 10000), "10,000〜49,999": (10000, 50000), "50,000〜99,999": (50000, 100000), "100,000〜": (100000, 10**9)}.items()})
    print()
    print("| 区分 | 件数 | 見積り必須 | 価格の中央値 | 最小〜最大 |")
    print("|---|---|---|---|---|")
    for name, _ in RULES + [("C 自動化します（形はタイトルに無い）", "")]:
        ps = prices_by[name]
        if ps:
            print(f"| {name} | {counts[name]} | {quote[name]} | {statistics.median(ps):,.0f}円 | {min(ps):,}〜{max(ps):,}円 |")
    print()
    print("道具名がタイトルにある件数:", dict(tool_hits))
    print()
    for no, c, price, q, title in out:
        print(f"{no:2d}\t{c}\t{price:,}\t{'見積り必須' if q=='1' else ''}\t{title}")


if __name__ == "__main__":
    main()
