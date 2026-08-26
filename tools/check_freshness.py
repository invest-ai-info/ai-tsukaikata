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
        python tools/check_freshness.py --writer  # レシピ担当の心拍だけ（日次）

⚠️ `--writer` は 2026-08-26 に足した。担当の停止（★91）は**週次では最大6日遅れる**ので、
「気づいたのは4日後」が直らない。毎日回すための口。

🚨 **わざと「担当の心拍だけ」に絞ってある。**ここに他の検査を相乗りさせないこと——
足した日に実測したら、週次の検査は**その時点で既に5件赤かった**（需要語の裏取り4件・
台帳の行数1件）。それを日次に載せると**初日から毎日赤い番人**になり、鳴っても読まれなくなる。
**日次の番人は「鳴ったら本当に異常」を保つ**（下限を課さないのと同じ判断）。
"""
from __future__ import annotations

import html
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


# --- 証拠の機械照合（進化ループ v1.5・2026-08-14）---
#
# 記事に載せた指示文が、証拠ファイル（docs/evidence/<slug>.md）に
# そのままの文字列で入っているかを突き合わせる。
#
# ✅ **2026-08-14 に `src/validate.py` へ昇格した（ビルドで強制）。**
# 経緯: 較正の実測が 94/129（8/12=54%・8/13=96%）だったので、まずここに置いて
# 週次で可視化した。畳んで記録されていた33件を同日中に追試して 129/129（100%）に
# したうえで昇格した。⚠️ 100%でないうちにビルドで止めると、毎晩の記事公開が
# 巻き込まれる（`/start/` の鮮度で学んだ罠＝止めてよいのは本人がその場で直せるものだけ）。
#
# ⚠️ **ここの検査は消さない。**ビルドは「これから作る記事」を止めるが、
# こちらは**証拠ファイルだけを後から書き換えた場合**にも週次で気づける
# （ビルドは記事に変更が無ければ走らないことがある）。二重にしておく。
PROMPT_RE = re.compile(r'<div class="prompt">(.*?)</div>', re.S)
EVIDENCE_ERA = date(2026, 8, 12)  # 進化ループ v1 の証拠様式が入った日
EVIDENCE_DIR = "docs/evidence"


def evidence_gaps(articles, evidence: dict[str, str],
                  era: date = EVIDENCE_ERA) -> list[str]:
    """記事の指示文と証拠ファイルの食い違いを、問題の文字列にして返す。

    照合は**完全一致**にする。空白を無視した緩い一致だと、記事で膨らませた
    指示文（証拠より長い版）を見逃す——実測ではそれが本命の食い違いだった。

    ⚠️ 対象は era 以降のレシピだけ。**slug 名指しの除外は作らない**
    （`FIGURE_EXEMPT_SLUGS` の教訓＝名指しの穴は「そこに足せばいい」と学習される）。
    """
    problems: list[str] = []
    for article in sorted(articles, key=lambda a: a.slug):
        if getattr(article, "category", None) != "recipes":
            continue
        if article.published < era:
            continue
        text = evidence.get(article.slug)
        if text is None:
            problems.append(
                f"{EVIDENCE_DIR}/{article.slug}.md: 証拠ファイルがありません"
                f"（{article.published} 公開のレシピ。キュー10条）"
            )
            continue
        prompts = [html.unescape(p).strip() for p in PROMPT_RE.findall(article.body_html)]
        missing = [p for p in prompts if p not in text]
        if missing:
            sample = missing[0].splitlines()[0][:40]
            problems.append(
                f"{EVIDENCE_DIR}/{article.slug}.md: 記事の指示文"
                f"{len(missing)}/{len(prompts)}件が証拠に同じ文字列で見つかりません"
                f"（例: 「{sample}…」）"
            )
    return problems


def load_evidence(root: Path) -> dict[str, str]:
    """docs/evidence/<slug>.md を {slug: 本文} で読む。TEMPLATE は除く。"""
    directory = Path(root) / EVIDENCE_DIR
    if not directory.exists():
        return {}
    return {
        path.stem: path.read_text(encoding="utf-8")
        for path in directory.glob("*.md")
        if path.stem != "TEMPLATE"
    }


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


# --- 需要語の裏取り（2026-08-25 オーナー判断）---
#
# 🚨 2026-08-25 の診断＝scene:earn は28本まで増えたのに表示17回・クリック0だった。
# 技術側は正常（robots オープン・sitemap 118本・canonical 有・noindex 無し）。
# 原因は補充の記録に自分で書いてあった——8/15「6件は1件をのぞいて需要語から来ていない」・
# 8/16「4件とも需要語から来ていない」。源③（既存記事の隣）と源①（自分の台帳）だけで
# 題材が回り、**サイトが自分自身を掘る閉じた輪**になっていた。それが素通りしていた。
# 🔑 詰まりは供給の速さではなく、需要と繋がっていない題材が通ることのほう。
#
# ⚠️ 語数の下限は課さない。課すのは「調べた形跡があるか」だけ。
# 「調べたが薄かった」と書いてあれば通る＝薄い題材を禁じるのではなく、
# **調べずに採ることを禁じる**。下限を課すと永久に消えない偽陽性になり、
# 検査全体の信用が落ちる（`validate.py` で下限を課さなかったのと同じ判断）。
DEMAND_WORD = "需要"


def _detail_lines(lines: list[str], start: int) -> list[str]:
    """マーカー行に続く字下げ行（間の空行は、次に字下げ行が来るなら中身）。"""
    detail = []
    j = start + 1
    while j < len(lines):
        if lines[j].startswith((" ", "\t")):
            detail.append(lines[j])
        elif lines[j] == "" and j + 1 < len(lines) and lines[j + 1].startswith((" ", "\t")):
            pass
        else:
            break
        j += 1
    return detail


def earn_demand_gaps(queue_text: str) -> list[str]:
    """「副業」の節の未処理で、需要語の裏取りが書かれていないものを挙げる。"""
    m = EARN_HEADING_RE.search(queue_text)
    if m is None:
        return []  # 節の欠落は earn_queue_shortage が鳴らす。二重に鳴らさない
    rest = queue_text[m.end():]
    nxt = re.search(r"^### ", rest, re.M)
    lines = (rest[: nxt.start()] if nxt else rest).splitlines()

    problems = []
    for i, line in enumerate(lines):
        if not line.startswith("- [ ] "):
            continue
        if any(DEMAND_WORD in d for d in _detail_lines(lines, i)):
            continue
        problems.append(
            f"{QUEUE_PATH}: 「副業」の未処理に需要語の裏取りがありません＝"
            f"{line[6:][:40]}"
            f"（研究パックの様式9番。調べて薄かったならそう書けば通る＝語数の下限は無い）"
        )
    return problems


# --- 仮説キューの事前登録（2026-08-25 オーナー判断「我々で研究してアイデアを出す」）---
#
# 機械は投資側の巨匠仮説キューから借りた。あちらが「順張り生存ゼロ」という結論を
# 出せたのは、棄却を正直に積んだから。借りたいのはその規律のほう。
#
# 🔑 関門に置くのは「反証条件」と「試行回数」＝**結果を見てから決めると
# 何とでも言える欄**。先に凍らせておかないと、何を投げても必ず失敗が見つかる
# （投資側で1本失った同語反復の罠のAI版）。
#
# ⚠️ 統計の道具は持ち込まない。標本が数十回の手作業なので有意差の話にすると嘘になる。
HYPOTHESIS_PATH = "content/_hypothesis_queue.md"
HYPOTHESIS_HEAD_RE = re.compile(r"^### (H[0-9]+) (.+)$", re.M)
HYPOTHESIS_STATE_RE = re.compile(r"^- 状態: *(.+)$", re.M)
HYPOTHESIS_REQUIRED = ("仮説", "材料", "測り方", "試行回数", "反証条件", "需要")
HYPOTHESIS_UNCHECKED = "未調査"
HYPOTHESIS_NOT_STARTED = "⏳"


def hypothesis_registration_gaps(text: str | None) -> list[str]:
    """仮説ブロックの必須欄の欠けを挙げる。書式見本（```の中）は H<番号> なので当たらない。"""
    if not text:
        return []
    heads = list(HYPOTHESIS_HEAD_RE.finditer(text))
    problems = []
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        block = text[head.end():end]
        number, name = head.group(1), head.group(2)

        # ⚠️ 欄だけ置いて中身が空、を見逃さない（行末までを取って strip で判定する。
        # 文字クラスで書くと改行に当たって空欄が通る＝テストが捕まえた）
        missing = []
        for field in HYPOTHESIS_REQUIRED:
            found = re.search(rf"^- {field}: *(.*)$", block, re.M)
            if found is None or not found.group(1).strip():
                missing.append(field)
        if missing:
            problems.append(
f"{HYPOTHESIS_PATH}: {number} の必須欄が空です＝{'・'.join(missing)}"
f"（{name}）。設計が固まっていないなら「## バックログ」へ移してH番号を発行しない"
            )

        # 需要の「未調査」は、着手前(⏳)のあいだだけ許す。動かし始めたら埋まっていること
        state = HYPOTHESIS_STATE_RE.search(block)
        started = state is not None and HYPOTHESIS_NOT_STARTED not in state.group(1)
        demand = re.search(r"^- 需要: *(.+)$", block, re.M)
        if started and demand is not None and HYPOTHESIS_UNCHECKED in demand.group(1):
            problems.append(
f"{HYPOTHESIS_PATH}: {number} が着手済みなのに需要が未調査のままです（{name}）。"
f"0語でも採ってよいが、調べた記録は残すこと（様式9番と同じ扱い）"
            )
    return problems

# --- 稼ぎ方研究担当の heartbeat（2026-08-14 稼ぎ方研究の設計）---
#
# 担当は0件の日も1行書く（沈黙禁止）。だから「ログが止まった＝担当が止まった」。
# ⚠️ ATには automation-health 相当のページがまだ無いので、当面はここが
# 稼働登録を兼ねる（相当物ができたらそちらにも登録する）。
#
# 🚨 2026-08-17 に担当自身が設計の穴を見つけた（修正済み）。
# 初版は**ファイルの最終コミット時刻**を見ていたが、それだと
# **無関係なコミットがこのファイルに触れるだけで心拍が正常に戻る**。
# 実際 8/16 は `44091fd`（タイトルの型をオーナー指示で直した回）がこの
# ファイルに触れたので、**担当が1日沈黙したのに素通りした**。
# 🔑 沈黙禁止は「ファイルが触られたか」ではなく「**その日の行があるか**」で測る。
EARN_RESEARCH_PATH = "content/_earn_research.md"
EARN_RESEARCH_MAX_DAYS = 2  # 1日休んでも鳴らない。2日ぶん空いたら鳴る
# 作業ログの日付見出し＝「### 2026-08-17 — …」
EARN_RESEARCH_DATE_RE = re.compile(r"^### (\d{4})-(\d{2})-(\d{2})", re.M)


def earn_research_heartbeat(log_text, today: date,
                            max_days: int = EARN_RESEARCH_MAX_DAYS) -> str | None:
    """稼ぎ方研究担当の作業ログが止まっていたら、知らせる文字列を返す。

    log_text は作業ログの中身。ファイルが無ければ None を渡す。
    ⚠️ コミット時刻ではなく**ログに書かれた日付**を見る（上のコメント参照）。
    """
    tail = f"（沈黙禁止＝0件の日も1行書く設計。担当は毎日15:30 JSTの"            f"クラウドルーティン。動いたか確認すること）"
    if log_text is None:
        return f"{EARN_RESEARCH_PATH} が見つかりません。稼ぎ方研究担当の作業ログです{tail}"

    dates = [date(int(y), int(m), int(d))
             for y, m, d in EARN_RESEARCH_DATE_RE.findall(log_text)]
    if not dates:
        return (
            f"{EARN_RESEARCH_PATH}: 作業ログに日付の節（### YYYY-MM-DD）が1つもありません"
            f"（見出しの形を変えたなら EARN_RESEARCH_DATE_RE も直すこと）"
        )

    latest = max(dates)
    gap = (today - latest).days
    if gap > max_days:
        return (
            f"{EARN_RESEARCH_PATH}: 最後の追記が{latest}で、{gap}日ぶん空いています"
            f"（上限{max_days}日）。稼ぎ方研究担当が止まっている可能性があります{tail}"
        )
    return None


# --- レシピ担当の日次ログ（★91の環境停止を捕まえる・2026-08-26 オーナー指示）---
#
# 🚨 守りたい失敗＝**実測の相手を立てられず、静かに0本に戻る夜**。
# 2026-08-22 と 08-24 に実際に起きた（★91）。`create_session` が
# `the parent session's permission mode is not yet available` で4回とも失敗し、
# Agentツールもその晩は使えなかった。担当は0番のとおり正しく止まったが、
# **オーナーが気づいたのは4日後**だった。ここはその遅れを潰すための番人。
#
# 🔑 **既存の成果物だけを見る番人では捕まらない**（2026-08-26 に実測して確かめた）:
#   ・停止記録 `docs/evidence/_*-not-published.md` は4件中3件が健全な題材停止＝偽陽性75%
#   ・08-24 の環境停止は**証拠ファイルを1つも残していない**（材料を作る前に止めたため）
#   ・公開本数でも鳴らない（08-22=1本・08-24=3本。別の回が成功するので0日にならない）
# → だから稼ぎ方研究担当と同じ**沈黙禁止の日次ログ**を置き、そこを見る。
#   ⚠️ コミット時刻ではなく**ログに書かれた日付**で測る（8/16 の素通りと同じ罠）。
#
# ⚠️ 環境停止と題材停止を必ず分ける。題材なら題材を替えれば直るので鳴らす必要がない。
# 混ぜると4件中3件が偽陽性になり、検査全体の信用が落ちる（下限を課さないのと同じ判断）。
WRITER_LOG_PATH = "content/_writer_log.md"
WRITER_LOG_MAX_DAYS = 2      # 1晩休んでも鳴らない（0番による正常な停止があるため）
WRITER_BLOCKED_DAYS = 7      # 直った後も鳴り続けさせない
WRITER_LOG_DATE_RE = re.compile(r"^### (\d{4})-(\d{2})-(\d{2})", re.M)
WRITER_MEASURE_RE = re.compile(r"^- 実測: *(.+)$", re.M)
WRITER_BLOCKED_MARK = "❌環境"

# 打つ手をメッセージに畳んで持たせる。★91を読み直さないと動けない番人にしない。
WRITER_BLOCKED_REMEDIES = (
    "①`claude --safe-mode --tools \"\" -p \"<指示文>\"`（実績あり。"
    "`--bare` は認証が通らない）／②Agentツール `general-purpose`／"
    "③`create_session`"
)


def _writer_entries(text: str) -> list[tuple[date, str]]:
    """日付節ごとに (日付, その節の本文) を返す。次の日付節の手前までが1節。"""
    heads = list(WRITER_LOG_DATE_RE.finditer(text))
    entries = []
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        entries.append((
            date(int(head.group(1)), int(head.group(2)), int(head.group(3))),
            text[head.end():end],
        ))
    return entries


def writer_log_heartbeat(log_text, today: date,
                         max_days: int = WRITER_LOG_MAX_DAYS) -> str | None:
    """レシピ担当の日次ログが止まっていたら、知らせる文字列を返す。

    log_text はログの中身。ファイルが無ければ None を渡す。
    """
    tail = ("（沈黙禁止＝0本の夜も1行書く設計。担当は毎晩21:00 JSTの"
            "クラウドルーティン。動いたか確認すること）")
    if log_text is None:
        return f"{WRITER_LOG_PATH} が見つかりません。レシピ担当の日次ログです{tail}"

    entries = _writer_entries(log_text)
    if not entries:
        return (
            f"{WRITER_LOG_PATH}: 日付の節（### YYYY-MM-DD）が1つもありません"
            f"（見出しの形を変えたなら WRITER_LOG_DATE_RE も直すこと）"
        )

    latest = max(day for day, _ in entries)
    gap = (today - latest).days
    if gap > max_days:
        return (
            f"{WRITER_LOG_PATH}: 最後の記録が{latest}で、{gap}日ぶん空いています"
            f"（上限{max_days}日）。レシピ担当が止まっている可能性があります{tail}"
        )
    return None


def writer_measurement_gaps(log_text, today: date,
                            within_days: int = WRITER_BLOCKED_DAYS) -> list[str]:
    """実測の欄の欠けと、直近の環境停止（★91）を挙げる。

    ⚠️ 題材が理由の停止は健全なので挙げない。ファイルの不在は heartbeat の担当。
    """
    if not log_text:
        return []

    problems = []
    for day, block in _writer_entries(log_text):
        # ⚠️ 1日に複数の回がある（実測: 14:15の回=CLI・21:00の回=Agent）。
        # 先頭1行だけ見ると、2回目が塞がった夜を丸ごと見落とす（テストが捕まえた）
        measured = [m.group(1).strip() for m in WRITER_MEASURE_RE.finditer(block)
                    if m.group(1).strip()]
        if not measured:
            problems.append(
                f"{WRITER_LOG_PATH}: {day} の記録に「- 実測:」の欄がありません。"
                f"何で実測したか（または止めた理由）を必ず書くこと"
                f"——欄が消えると、この番人は空回りする"
            )
            continue
        if (today - day).days > within_days:
            continue
        for line in measured:
            if WRITER_BLOCKED_MARK in line:
                problems.append(
                    f"🚨 {WRITER_LOG_PATH}: {day} に実測の相手を立てられませんでした"
                    f"（★91の再発）＝{line}。"
                    f"**直るまで実測を伴うレシピは1本も書けません。**試す順＝"
                    f"{WRITER_BLOCKED_REMEDIES}"
                )
    return problems


# --- 金額目安ブロックの鮮度（2026-08-14 稼ぎ方研究の設計）---
#
# 相場・プラットフォームの規約は変わるので、古い金額の目安は再確認へ出す。
#
# ⚠️ MONEY_NOTE_RE は src/validate.py にも同じものがある。これは意図的な重複。
# tools/ と src/ は別レイヤーで、週次のこちらがビルド強制側（validate.py）を
# import することはしない（ここが止まってもビルドは止めたくないので、
# 依存を持たせない）。「重複を消そう」と import へまとめないこと。
#
# ⚠️ ここは古さでビルドを止めない。_checked_errors と同じ理由＝古さは時間が
# 経てば勝手に起きるので、止めると毎晩の担当が push した記事が公開できなくなる。
MONEY_NOTE_RE = re.compile(r'<div class="money-note">(.*?)</div>', re.S)
MONEY_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
MONEY_MAX_AGE_DAYS = 180


def money_note_staleness(articles, today: date, max_age_days=MONEY_MAX_AGE_DAYS) -> list[str]:
    """金額目安ブロックの確認日が古い記事を、問題の文字列にして返す。

    日付が見つからないブロックは黙ってスキップする（無いこと自体は
    ビルド時の src/validate.py が既に強制している。ここで重複して言わない）。
    """
    problems: list[str] = []
    for article in articles:
        for block in MONEY_NOTE_RE.findall(article.body_html):
            m = MONEY_DATE_RE.search(block)
            if m is None:
                continue
            checked = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            age = (today - checked).days
            if age > max_age_days:
                problems.append(
                    f"{article.slug}: 金額目安ブロックの確認日が{age}日前です"
                    f"（checked: {checked} / 上限{max_age_days}日。"
                    f"単価と規約を確認し直してください）"
                )
    return problems


# --- 台帳の昇格判定（2026-08-14）---
#
# 進化ループ輪2（週次）の「昇格判定」は、これまで人が台帳を読んで数えていた。
# 実際にそれで数が腐った＝★1の節は自分を「4本で出た（最多）」と書き、
# 引き継ぎは「5本」「6本」と書いていて、機械で数えると7だった。
# 🔑 **数を文章で持つと必ず古くなる**（キューの本数が2か所にあって腐ったのと同じ型）。
# ここでは数を持たず、毎回台帳から数え直す。
LEDGER_PATH = "content/_lessons.md"
LEDGER_CAP = 15  # 設計値。「長い台帳は読まれなくなって死ぬ」
LESSON_RE = re.compile(r"^### (★?\d+[a-z]?)\. (.+)$", re.M)
# 「4番が再発」「1番の系列」「12番の親戚」「2番の実例が増えた」
LESSON_REF_RE = re.compile(r"(\d+[a-z]?)\s*番(?:が)?(?:再発|の系列|の親戚|の実例)")


# --- 生きているファイルの行数予算（2026-08-20 トークン食の設計）---
#
# 毎晩3〜4担当が読むファイルは、tools/rotate_archives.py が済んだ在庫を
# 保管庫へ移して小さく保つ。予算超過＝「回転が止まった」のシグナル
# （heartbeat と同じ思想＝ビルドは止めず、週次で人に知らせるだけ）。
# 予算＝初回回転直後の実測（2026-08-20: 1649/352/997/506/762行）に
# 5割前後の余裕を載せた値。実測より小さい予算は初日から偽陽性になる。
FILE_BUDGETS = {
    "content/_recipe_queue.md": 2500,
    "content/_deepdive_queue.md": 600,
    "content/_topic_ideas.md": 1500,
    "content/_review_log.md": 800,
    "content/_earn_research.md": 1200,
    "content/_hypothesis_queue.md": 900,
}


def file_budgets(texts: dict[str, str], budgets: dict[str, int] = FILE_BUDGETS):
    """{相対パス: 中身} を受け取り、予算超過を問題の文字列にして返す。"""
    problems = []
    for rel, text in texts.items():
        budget = budgets.get(rel)
        if budget is None:
            continue
        n = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        if n > budget:
            problems.append(
                f"{rel}: {n}行あります（予算{budget}行）。tools/rotate_archives.py の"
                f"回転が止まっている可能性があります（毎日04:43 JST の rotate.yml。"
                f"手で1回 `python tools/rotate_archives.py` を実行して減るか確かめること）"
            )
    return problems


def lesson_promotions(ledger_text: str, slugs, cap: int = LEDGER_CAP):
    """台帳の「何本で出たか」を数えて、(problems, notes) を返す。

    昇格の条件は「2回出た教訓／全題材に効く教訓」（進化ループ設計）。
    数え方は2つあって、どちらも1回に数える:

      A. その節が本文で名指ししている記事slug（＝実際に出た記事）
      B. 他の節から「N番が再発」と参照された回数（＝あとから再発したもの）

    ⚠️ **Aは取りこぼす。**節が記事を「同じ実測」とだけ書いてslugを書かない場合、
    0本と数える（実際 ★17・★24 などがそう）。**過小に出るほうへ倒してある**＝
    昇格候補を多めに挙げて人が落とすほうが、見逃すより安全だから。
    ⚠️ この検査は問題ではなく参考。**昇格させるかどうかは人が決める**
    （設計で「昇格は人間セッションのみ」と決めてある）。
    """
    lessons = LESSON_RE.findall(ledger_text)
    if not lessons:
        return ([f"{LEDGER_PATH}: 教訓の節が1件も読めません"
                 f"（見出しの形を変えたなら LESSON_RE も直すこと）"], [])

    bodies = re.split(LESSON_RE, ledger_text)[3::3]
    refs: dict[str, set[str]] = {}
    for (num, _), body in zip(lessons, bodies):
        for key in LESSON_REF_RE.findall(body):
            if key != num.lstrip("★"):
                refs.setdefault(key, set()).add(num)

    scored = []
    for (num, title), body in zip(lessons, bodies):
        cited = sum(1 for s in slugs if s in body)
        referred = len(refs.get(num.lstrip("★"), ()))
        scored.append((cited + referred, cited, referred, num, title))
    scored.sort(reverse=True)

    problems = []
    if len(lessons) > cap:
        problems.append(
            f"{LEDGER_PATH}: 生きている教訓が{len(lessons)}件です"
            f"（上限{cap}件。昇格させて「昇格済み」へ移すか、束ねて整理してください。"
            f"長い台帳は読まれなくなって死にます）"
        )

    ready = [s for s in scored if s[0] >= 2]
    notes = [
        f"{LEDGER_PATH}: 昇格の条件（2回以上）を満たす教訓が{len(ready)}件あります"
        f"（昇格させるかは人が決める）"
    ]
    notes += [
        f"    {num}. {title[:38]}（記事{cited}本＋被参照{referred}件＝{total}）"
        for total, cited, referred, num, title in ready
    ]
    return (problems, notes)


# --- 弁護士相談の期日ゲート（2026-08-14・収入エンジン設計 D-4）---
#
# 「決めない状態」を機械が禁止する。相談が期日までに実施されなければ、
# グレー全域（保留中の題材・公開範囲の拡張）は「今四半期は白のみで設計」へ
# 格下げされる——どちらに転んでも浮遊状態が消える。
# 設計書＝docs/superpowers/specs/2026-08-14-income-engine-design.md
#
# ⚠️ 期日と状態はここが唯一の置き場（2か所に書くと片方が腐る）。
# 相談が済んだら LAWYER_CONSULT_DONE を True にする（1行のコミットで解除）。
# 📌 早期トリガー「メアド100件到達」は自動では読めないので、達したら
# 人が期日を手前に詰める（この定数を書き換える）。
LAWYER_GATE_DEADLINE = date(2026, 10, 31)
LAWYER_CONSULT_DONE = False
LAWYER_GATE_RAMP_DAYS = 28  # 期日の4週前から週次メールに昇格する


def lawyer_deadline_gate(today: date,
                         deadline: date = LAWYER_GATE_DEADLINE,
                         done: bool = LAWYER_CONSULT_DONE):
    """(problems, notes) を返す。

    鳴り方は3段階。⚠️ 遠いうちから problems で鳴らさない——直せない警告を
    毎週メールすると一覧が読まれなくなる（/start/ の鮮度検査で学んだ型）。

      期日まで4週超 : notes（表示のみ・失敗させない）
      期日まで4週以内: problems（毎週メール＝最後の1か月だけ急かす）
      期日超過      : problems（格下げの宣言。以後は毎週これが出る）
    """
    if done:
        return ([], [])
    days_left = (deadline - today).days
    if days_left < 0:
        return ([
            f"弁護士相談の期日ゲート: 期日（{deadline}）を過ぎました。"
            f"設計どおり、グレー全域は「今四半期は白のみで設計」へ格下げです。"
            f"解除は相談実施後に LAWYER_CONSULT_DONE を True にする"
        ], [])
    if days_left <= LAWYER_GATE_RAMP_DAYS:
        return ([
            f"弁護士相談の期日ゲート: 期日（{deadline}）まで残り{days_left}日。"
            f"未実施のまま期日を過ぎると、グレー全域が白のみ設計へ自動格下げされます"
        ], [])
    return ([], [
        f"弁護士相談の期日ゲート: 期日 {deadline}（残り{days_left}日）。"
        f"メアド100件に達したら期日を手前に詰める（tools/check_freshness.py）"
    ])


def writer_problems(root: Path, today: date) -> list[str]:
    """レシピ担当の心拍と実測の詰まりだけを挙げる（日次の番人が呼ぶ）。"""
    writer_file = root / "content" / "_writer_log.md"
    text = writer_file.read_text(encoding="utf-8") if writer_file.exists() else None
    problems = []
    beat = writer_log_heartbeat(text, today)
    if beat:
        problems.append(beat)
    problems.extend(writer_measurement_gaps(text, today))
    return problems


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent

    # --writer ＝担当の心拍だけ。日次で回す口（冒頭のコメント参照）。
    # ⚠️ ここに他の検査を足さないこと。毎日赤い番人は読まれなくなる
    if "--writer" in (sys.argv[1:] if argv is None else argv):
        problems = writer_problems(root, date.today())
        for problem in problems:
            print(problem)
        if problems:
            print(f"\n{len(problems)}件の問題があります")
            return 1
        print("レシピ担当は動いています（実測の詰まりもありません）")
        return 0

    articles, errors = load_articles(root / "content")
    for error in errors:
        print(f"記事が読めません: {error}")

    report = check_articles(articles, date.today())

    # 待ち行列の残量は記事の腐りとは別件だが、見る頻度（週次）が同じなので相乗りさせる。
    # 証拠の機械照合（v1.5）。ビルドは止めず、週次で知らせるだけ
    report.problems.extend(evidence_gaps(articles, load_evidence(root)))

    queue_file = root / "content" / "_recipe_queue.md"
    if queue_file.exists():
        queue_text = queue_file.read_text(encoding="utf-8")
        for check in (queue_shortage, earn_queue_shortage):
            shortage = check(queue_text)
            if shortage:
                report.problems.append(shortage)
        # 需要語の裏取り（2026-08-25 オーナー判断）。閉じた輪の再発を止める
        report.problems.extend(earn_demand_gaps(queue_text))

    # 弁護士相談の期日ゲート（収入エンジン設計 D-4）
    gate_problems, gate_notes = lawyer_deadline_gate(date.today())
    report.problems.extend(gate_problems)
    report.notes.extend(gate_notes)

    # 稼ぎ方研究担当の heartbeat と金額の鮮度（2026-08-14 稼ぎ方研究の設計）
    research_file = root / "content" / "_earn_research.md"
    heartbeat = earn_research_heartbeat(
        research_file.read_text(encoding="utf-8") if research_file.exists() else None,
        date.today(),
    )
    if heartbeat:
        report.problems.append(heartbeat)
    report.problems.extend(money_note_staleness(articles, date.today()))

    # レシピ担当の日次ログ（2026-08-26）。日次の `--writer` と同じものを週次でも見る
    # （日次のワークフローが止まっていても、週次で必ず拾えるように二重にしておく）
    report.problems.extend(writer_problems(root, date.today()))

    # 仮説キューの事前登録（2026-08-25）。反証条件と試行回数を結果より先に凍らせる
    hypothesis_file = root / "content" / "_hypothesis_queue.md"
    report.problems.extend(hypothesis_registration_gaps(
        hypothesis_file.read_text(encoding="utf-8") if hypothesis_file.exists() else None
    ))

    # 台帳の昇格判定。輪2（月曜）が数え直さずに済むように、数はここで出す。
    ledger_file = root / "content" / "_lessons.md"
    if ledger_file.exists():
        ledger_problems, ledger_notes = lesson_promotions(
            ledger_file.read_text(encoding="utf-8"),
            {p.stem for p in (root / "content" / "recipes").glob("*.md")},
        )
        report.problems.extend(ledger_problems)
        report.notes.extend(ledger_notes)

    # 生きているファイルの行数予算（回転が止まったことの検知）
    report.problems.extend(file_budgets({
        rel: (root / rel).read_text(encoding="utf-8")
        for rel in FILE_BUDGETS if (root / rel).exists()
    }))

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
