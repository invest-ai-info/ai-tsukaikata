# -*- coding: utf-8 -*-
"""記事に書いた数字が、出典ページに実在するかを照合する。

作った理由（2026-08-04）＝出典URLは正しいのに、**そのページにその数字が無い**
記事が出た。`gpt-5.5-pro` に「長い入力」の行が無いのに、他モデルの倍率
（×2 / ×1.5）を当てはめて $60/$270 と書いていた。出典が付いていると人は
確認しないので、一番見つかりにくい壊れ方になる。

⚠️ ビルドには組み込まない。ネットワークに出るのでビルドが不安定になるし、
記事が計算した値（「1.67倍」など）は出典に無くて当然なので、止めるのではなく
報告して人が判断する形にする。

使い方:
    python tools/check_numbers.py content/tools/gemini-3-6-flash.md
"""
from __future__ import annotations

import re
import sys
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path

USER_AGENT = "ai-tsukaikata-checker/1.0"
TIMEOUT = 30

# 出典の書き方は2つ。<https://...> と [文字](https://...)。
_ANGLE_URL_RE = re.compile(r"<(https?://[^>\s]+)>")
_MD_URL_RE = re.compile(r"\]\((https?://[^)\s]+)\)")

# 照合できるのは「表記がそのまま出典に出る」数字だけ。
# ドル額とパーセントに絞る。日本語に直した単位（20万トークン / 2025年7月 /
# 1.67倍）は出典側の表記と一致しないので、拾うと誤検知だらけになる。
_DOLLAR_RE = re.compile(r"\$\s?(\d+(?:,\d{3})*(?:\.\d+)?)")
# 先読みの除外に「,」を入れないと "1,349%" を "349%" と読む。
_PERCENT_RE = re.compile(r"(?<![\d.,])(\d+(?:,\d{3})*(?:\.\d+)?)\s?%")

_TAG_RE = re.compile(r"<[^>]+>")

# ⚠️ 型（ドル額／パーセント）を落として「ページのどこかに出る数字」と照合すると
# 検出力がゼロになる。実測（2026-08-05）＝出典10ページぶんの数字を1つのプールに
# まとめたら、捏造された $60 と $270 が「どこかに 60 と 270 がある」で通ってしまった。
# ページ側も同じ型で拾って突き合わせる。
_KINDS = {"$": _DOLLAR_RE, "%": _PERCENT_RE}


def cited_urls(text: str) -> list[str]:
    """記事が挙げている外部URLを、出てきた順に重複なく返す。"""
    found = _ANGLE_URL_RE.findall(text) + _MD_URL_RE.findall(text)
    seen: dict[str, None] = {}
    for url in found:
        seen.setdefault(url.rstrip(").,、。"), None)
    return list(seen)


def _to_decimal(raw: str) -> Decimal | None:
    try:
        return Decimal(raw.replace(",", ""))
    except InvalidOperation:
        return None


def checkable_numbers(text: str) -> dict[tuple[str, Decimal], list[str]]:
    """照合できる数字を {(型, 値): [書かれ方]} で返す。

    型は "$"（ドル額）か "%"（パーセント）。URLの中の数字は拾わない
    （`gemini-3-6-flash` のような slug が混ざるため）。
    """
    without_urls = _ANGLE_URL_RE.sub(" ", text)
    without_urls = _MD_URL_RE.sub(" ", without_urls)

    result: dict[tuple[str, Decimal], list[str]] = {}
    for kind, pattern in _KINDS.items():
        fmt = "${}" if kind == "$" else "{}%"
        for raw in pattern.findall(without_urls):
            value = _to_decimal(raw)
            if value is None:
                continue
            result.setdefault((kind, value), []).append(fmt.format(raw))
    return result


def numbers_in_page(page_text: str) -> set[tuple[str, Decimal]]:
    """ページに出てくる数字を {(型, 値)} で返す。

    Decimal は値で等しさを見るので、$1.50 と $1.5 が同じものとして当たる。
    """
    numbers: set[tuple[str, Decimal]] = set()
    for kind, pattern in _KINDS.items():
        for raw in pattern.findall(page_text):
            value = _to_decimal(raw)
            if value is not None:
                numbers.add((kind, value))
    return numbers


def unverified(
    article: str, pages: dict[str, str | None]
) -> list[tuple[tuple[str, Decimal], list[str]]]:
    """どの出典ページにも見つからなかった数字を返す。

    取得できなかったページ（値が None）は判定に使わない。取得失敗を
    「書かれていない」と扱うと、全部が未確認として並んでしまう。
    """
    available = [text for text in pages.values() if text]
    if not available:
        return []

    known: set[tuple[str, Decimal]] = set()
    for text in available:
        known |= numbers_in_page(text)

    missing = [
        (key, forms)
        for key, forms in checkable_numbers(article).items()
        if key not in known
    ]
    missing.sort(key=lambda item: (item[0][0], item[0][1]))
    return missing


def fetch(url: str) -> str | None:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            raw = response.read()
    except Exception as error:  # noqa: BLE001 - 1件の失敗で全体を止めない
        print(f"  取得できず: {url}  ({type(error).__name__})")
        return None
    return _TAG_RE.sub(" ", raw.decode("utf-8", "replace"))


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("使い方: python tools/check_numbers.py <記事のパス> [...]")
        return 2

    worst = 0
    for path in argv:
        article = Path(path).read_text(encoding="utf-8")
        urls = cited_urls(article)
        print(f"\n=== {path} ===")
        print(f"出典 {len(urls)}件を取得します")
        pages = {url: fetch(url) for url in urls}
        got = sum(1 for text in pages.values() if text)
        checkable = checkable_numbers(article)
        missing = unverified(article, pages)

        print(f"取得できた出典 {got}/{len(urls)}件 ／ 照合できる数字 {len(checkable)}個")
        if not got:
            print("  ⚠️ 1件も取得できなかったので判定していません")
            continue
        if not missing:
            print("  ✅ すべての数字が、いずれかの出典ページに存在しました")
            continue
        worst = 1
        print(f"  ⚠️ 出典に見つからない数字 {len(missing)}個:")
        for _key, forms in missing:
            print(f"     {' / '.join(sorted(set(forms)))}")
        print("  ※ 記事が計算した値（倍率・差分）は出典に無くて当然です。人が判断してください。")
    return worst


if __name__ == "__main__":
    sys.exit(main())
