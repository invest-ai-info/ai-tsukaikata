# -*- coding: utf-8 -*-
"""外部を参照している記事が腐っていないかを、週次で見る。

⚠️ ビルドには組み込まない。ネットワークに出るのでビルドが不安定になるし、
「古い」は時間が経てば勝手に起きる。ビルドで止めると、毎晩21:00の
レシピ担当が push した記事が、指南書の日付を理由に公開されなくなる
（build.py は「全部通る or 何も出さない」）。止めるのではなく知らせる。

見るのは3つ:
  1. 外部リンクが開けるか
  2. 確認日（checked）が古くなっていないか
  3. 外部リンクを持つのに checked が無い記事はどれか（付け忘れの網）

使い方: python tools/check_freshness.py
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.content import load_articles  # noqa: E402

USER_AGENT = "ai-tsukaikata-checker/1.0"
TIMEOUT = 30
MAX_AGE_DAYS = 90

EXTERNAL_LINK_RE = re.compile(r'href="(https?://[^"]+)"')

# 自分のサイトと自分のリポジトリへのリンクは「腐る外部情報」ではない。
# checked: は「他人が公開した事実を、この日に確かめた」という意味なので、
# 自分で管理しているものに日付を付けても意味がない。
# ⚠️ 死活の検査からは外さない。自分のリポジトリへのリンクでも、切れていれば直す。
OWN_LINK_PREFIXES = (
    "https://ai-tsukaikata.com",
    "https://github.com/invest-ai-info/",
)


def external_links(body_html: str) -> list[str]:
    """本文の外部リンクを、出てきた順で重複なく返す。"""
    found: list[str] = []
    for url in EXTERNAL_LINK_RE.findall(body_html):
        if url not in found:
            found.append(url)
    return found


def head(url: str) -> int | None:
    """状態コードを返す。届かなければ None。

    HEAD を拒む相手がいるので、拒まれたら GET で開き直す。
    """
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            url, method=method, headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status
        except urllib.error.HTTPError as error:
            if method == "HEAD" and error.code in (403, 405):
                continue
            return error.code
        except Exception:  # noqa: BLE001 - 1件の失敗で全体を止めない
            if method == "HEAD":
                continue
            return None
    return None


def check_articles(articles, today: date, head=head, max_age_days=MAX_AGE_DAYS) -> list[str]:
    """問題を文字列のリストで返す。空なら健康。"""
    problems: list[str] = []
    for article in articles:
        where = str(article.source_path)
        links = external_links(article.body_html)
        # checked: を求めるのは他人の情報だけ。自分のリンクは死活検査の対象には残す。
        others = [url for url in links if not url.startswith(OWN_LINK_PREFIXES)]

        if others and article.checked is None:
            problems.append(
                f"{where}: 外部リンクが{len(others)}本あるのに checked: がありません"
                f"（腐っても誰も気づけません）"
            )
        elif article.checked is not None:
            age = (today - article.checked).days
            if age > max_age_days:
                problems.append(
                    f"{where}: 確認日が{age}日前です"
                    f"（{max_age_days}日を超えました。checked: {article.checked}）"
                )

        for url in links:
            status = head(url)
            if status is None:
                problems.append(f"{where}: リンクが開けません（接続できず）: {url}")
            elif status >= 400:
                problems.append(f"{where}: リンクが開けません（{status}）: {url}")
    return problems


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    articles, errors = load_articles(root / "content")
    for error in errors:
        print(f"記事が読めません: {error}")

    problems = check_articles(articles, date.today())
    for problem in problems:
        print(problem)

    if errors or problems:
        print(f"\n{len(errors) + len(problems)}件の問題があります")
        return 1
    print(f"{len(articles)}本を見て、問題はありませんでした")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
