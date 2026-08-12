# -*- coding: utf-8 -*-
"""外部を参照している記事が腐っていないかを、週次で見る。

⚠️ ビルドには組み込まない。ネットワークに出るのでビルドが不安定になるし、
「古い」は時間が経てば勝手に起きる。ビルドで止めると、毎晩21:00の
レシピ担当が push した記事が、指南書の日付を理由に公開されなくなる
（build.py は「全部通る or 何も出さない」）。止めるのではなく知らせる。

見るのは4つ:
  1. 外部リンクが開けるか
  2. 外部リンクが引っ越していないか
  3. 確認日（checked）が古くなっていないか
  4. 外部リンクを持つのに checked が無い記事はどれか（付け忘れの網）

⚠️ 2番は 2026-08-09 に足した。記事に貼った docs.claude.com のURLが、すでに
code.claude.com へのリダイレクトになっていた。**リダイレクトが効いている限り
200が返るので、死活の検査だけでは永久に気づけない。**200が返ることと、
そのURLが正式であることは別。

使い方: python tools/check_freshness.py
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import NamedTuple

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


class Reached(NamedTuple):
    """リンクを1本叩いた結果。

    status が None なら届かなかった。url は「実際にたどり着いた先」で、
    リダイレクトされていれば移転先が入る。⚠️ 状態コードだけ返していると、
    引っ越し済みのURLが永久に緑のままになる（それで実際に1本見逃した）。

    bot_blocked ＝ 先方の bot 判定で弾かれた。人がブラウザで開けば見えるので
    「リンク切れ」ではない。⚠️ UA偽装で迂回しない方針なので、確かめられない。
    """

    status: int | None
    url: str
    bot_blocked: bool = False


class Report(NamedTuple):
    """problems ＝直すべきもの（週次ワークフローを失敗させる）。

    notes ＝直しようがないが、黙って消すと「確かめた」と誤解されるもの。
    ⚠️ notes で失敗させないこと。直せない警告を毎週出すと一覧が読まれなくなる。
    """

    problems: list[str]
    notes: list[str]


# Cloudflare が bot 判定で返す 403 の目印。実測（2026-08-09・claude.ai）で
# `cf-mitigated: challenge` が付いていた。これがあれば「壊れている」ではなく
# 「こちらからは確かめられない」。
BOT_BLOCK_HEADER = "cf-mitigated"


def _moved_away(asked: str, reached: str) -> bool:
    """引っ越したとみなすのは「別のホストへ飛ばされたとき」だけ。

    ⚠️ パスの違いで鳴らしてはいけない。2026-08-09 に実測したところ、
    `https://claude.ai/` は未ログインだと `https://claude.ai/login` へ飛ぶ。
    これは引っ越しではなく、こちらがログインしていないだけで、直しようがない。
    **直せない警告を毎週出すと、一覧そのものが読まれなくなる。**
    末尾スラッシュやロケール付与も同じ理由でパスの差に入る。

    逆にホストが変わったときは、まず本物の引っ越し（実測: docs.claude.com →
    code.claude.com、deepmind.google → blog.google）。ここだけ鳴らす。
    """
    return urllib.parse.urlsplit(asked).netloc != urllib.parse.urlsplit(reached).netloc


def _canonical(url: str) -> str:
    """突き合わせ用に、クエリ・断片・末尾スラッシュを落とす。

    転送先には `?utm_source=...` が付くことがあり、そのままだと
    記事が貼っているURLと文字列比較で一致しない。
    """
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}{parts.path.rstrip('/')}"


def head(url: str) -> Reached:
    """状態コードと、実際にたどり着いたURLを返す。

    HEAD を拒む相手がいるので、拒まれたら GET で開き直す。
    """
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            url, method=method, headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return Reached(response.status, response.url)
        except urllib.error.HTTPError as error:
            blocked = error.headers.get(BOT_BLOCK_HEADER) is not None
            if method == "HEAD" and error.code in (403, 405) and not blocked:
                continue
            return Reached(error.code, getattr(error, "url", None) or url, blocked)
        except Exception:  # noqa: BLE001 - 1件の失敗で全体を止めない
            if method == "HEAD":
                continue
            return Reached(None, url)
    return Reached(None, url)


def check_articles(articles, today: date, head=head, max_age_days=MAX_AGE_DAYS) -> Report:
    """直すべきもの（problems）と、確かめられなかったもの（notes）を返す。"""
    problems: list[str] = []
    notes: list[str] = []
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

        # 転送先を記事が既に貼っているなら、書き手は引っ越しを把握している。
        # 実測（gemini-3-6-flash）＝出典1番に移転先 blog.google を貼ったうえで、
        # 旧 deepmind.google を「開くとここへ転送されます」と注記していた。
        # ⚠️ ここで鳴らすと、正しく書いてある記事を毎週叩くことになる。
        known = {_canonical(url) for url in links}

        for url in links:
            reached = head(url)
            if reached.bot_blocked:
                notes.append(
                    f"{where}: 確かめられませんでした（先方のbot判定・{reached.status}）: {url}"
                )
            elif reached.status is None:
                problems.append(f"{where}: リンクが開けません（接続できず）: {url}")
            elif reached.status >= 400:
                problems.append(f"{where}: リンクが開けません（{reached.status}）: {url}")
            elif _moved_away(url, reached.url) and _canonical(reached.url) not in known:
                problems.append(
                    f"{where}: リンクが引っ越しています（貼り替えてください）\n"
                    f"    いま貼っている先: {url}\n"
                    f"    実際に着いた先:   {reached.url}"
                )
    return Report(problems, notes)


QUEUE_PATH = "content/_recipe_queue.md"
QUEUE_FLOOR = 6  # 2晩ぶん。ここを切ったら補充が最優先
UNPROCESSED_RE = re.compile(r"^- \[ \]", re.M)


def queue_shortage(queue_text: str, floor: int = QUEUE_FLOOR) -> str | None:
    """レシピの待ち行列が枯れかけていたら、知らせる文字列を返す。

    ⚠️ 静かに枯れると、毎晩の担当が「題材が無い」で止まり始めてから気づくことになる。
    サイトが止まるわけではないので、ビルドでは止めずに週次で知らせる。

    未処理は `- [ ]` だけ。`- [x]`（公開済み）も `- [!]`（書かずに止めた）も数えない。
    """
    count = len(UNPROCESSED_RE.findall(queue_text))
    if count < floor:
        return (
            f"{QUEUE_PATH}: 待ち行列の未処理が{count}件です"
            f"（床は{floor}件＝2晩ぶん。補充が最優先です。"
            f"再実行の手順は docs/superpowers/notes/2026-08-10-demand-research.md）"
        )
    return None


EARN_HEADING_RE = re.compile(r"^### 副業.*$", re.M)
EARN_FLOOR = 3  # 1晩ぶん。「副業も毎晩3本」（2026-08-13 オーナー指示）を支える床


def earn_queue_shortage(queue_text: str, floor: int = EARN_FLOOR) -> str | None:
    """「副業」の節の未処理が1晩ぶんを切ったら、知らせる文字列を返す。

    毎晩3本の方針は、節の残量が尽きると黙って守れなくなる（担当は正しく
    「残りが無い」と報告するが、週次まで誰も補充しない）ので、床を別に持つ。

    ⚠️ 節の見出しが見つからない場合も知らせる。見出しの改名で番人が
    黙って死ぬのが、このサイトが一番警戒している「静かな欠落」だから。
    """
    m = EARN_HEADING_RE.search(queue_text)
    if m is None:
        return (
            f"{QUEUE_PATH}: 「### 副業」の節が見つかりません。"
            f"見出しを変えたなら tools/check_freshness.py の EARN_HEADING_RE も直すこと"
        )
    rest = queue_text[m.end():]
    nxt = re.search(r"^### ", rest, re.M)
    section = rest[: nxt.start()] if nxt else rest
    count = len(UNPROCESSED_RE.findall(section))
    if count < floor:
        return (
            f"{QUEUE_PATH}: 「副業」の節の未処理が{count}件です"
            f"（床は{floor}件＝1晩ぶん。毎晩3本の方針が守れなくなります。"
            f"補充の手順は docs/superpowers/notes/2026-08-10-demand-research.md の"
            f"「2026-08-13 追加実行」節）"
        )
    return None


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    articles, errors = load_articles(root / "content")
    for error in errors:
        print(f"記事が読めません: {error}")

    report = check_articles(articles, date.today())

    # 待ち行列の残量は記事の腐りとは別件だが、見る頻度（週次）が同じなので相乗りさせる。
    queue_file = root / "content" / "_recipe_queue.md"
    if queue_file.exists():
        queue_text = queue_file.read_text(encoding="utf-8")
        for check in (queue_shortage, earn_queue_shortage):
            shortage = check(queue_text)
            if shortage:
                report.problems.append(shortage)

    for problem in report.problems:
        print(problem)

    # ⚠️ notes では失敗させない。直せない警告を毎週出すと一覧が読まれなくなる。
    # ただし黙って消すと「確かめた」と誤解されるので、必ず表示はする。
    if report.notes:
        print("\n--- 参考（こちらからは確かめられないもの・直す必要はありません） ---")
        for note in report.notes:
            print(note)

    if errors or report.problems:
        print(f"\n{len(errors) + len(report.problems)}件の問題があります")
        return 1
    print(f"\n{len(articles)}本を見て、直すべきものはありませんでした")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
