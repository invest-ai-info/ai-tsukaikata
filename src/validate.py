# -*- coding: utf-8 -*-
"""公開前チェック。何も書かず、エラー文字列のリストを返すだけ。

最初のエラーで止めず全部集める。1個直して再実行、の往復を避けるため。

広告表記のチェックは景表法のステマ規制対応で、法的に必須の項目。
人間の記憶ではなくここで強制する。（本ファイルは法的助言ではない）
"""
from __future__ import annotations

import html
import re
from datetime import date

from . import config
from .content import Article

TOKEN_PATTERNS = (
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHubのトークン"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHubのトークン"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"), "AnthropicのAPIキー"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAIのAPIキー"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWSのアクセスキー"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"), "Slackのトークン"),
)

CREDENTIAL_RE = re.compile(
    r"(?i)(password|passwd|api[_\- ]?key|secret[_\- ]?key|access[_\- ]?token)"
    r"\s*[=:]\s*[\"']?([A-Za-z0-9/+_\-]{8,})"
)

# ダミー値まで落とすと記事が書けなくなるので、明らかな穴埋め語は通す
PLACEHOLDER_HINTS = (
    "your", "xxx", "dummy", "example", "sample", "here",
    "changeme", "placeholder", "secrets.", "env.",
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-\[\]]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
SAFE_EMAIL_DOMAINS = (
    "example.com", "example.org", "example.net", "users.noreply.github.com",
)

# C:\Users\<ユーザー名> のような穴埋めは通し、実在しそうな名前だけ落とす
LOCAL_PATH_RE = re.compile(r"C:\\Users\\(?![<%{＜])")

AFFILIATE_PATTERNS = (
    re.compile(r"a8\.net"),
    re.compile(r"moshimo\.com"),
    re.compile(r"valuecommerce\."),
    re.compile(r"accesstrade\."),
    re.compile(r"amzn\.to"),
    re.compile(r"hb\.afl\.rakuten"),
    re.compile(r"amazon\.co\.jp/[^\s\"')]*[?&]tag="),
)
DISCLOSURE_WORDS = ("広告", "PR", "アフィリエイト", "プロモーション")

# マーカーは「読み飛ばす人がそこだけ拾えば筋が通る」ための目印なので、
# 増やすと目印でなくなる。上限だけを課し、下限は課さない（短い記事で
# 永久に消えない偽陽性になり、検査全体の信用を落とすため）。
MARK_MAX = 13
MARK_WARN_MAX = 5
MARK_RE = re.compile(r"<mark\b")
MARK_WARN_RE = re.compile(r'<mark class="warn"')

# 見出しのclassは付け忘れても既定アイコンが出るだけで、見た目が崩れない。
# つまり目視では気づけない。誤字も同じ。
SECTION_CLASSES = frozenset({"what", "need", "ask", "fix", "next"})
TROUBLE_CLASSES = frozenset({"trouble"})
HEADING_RE = re.compile(r"<(h2|h3)\b([^>]*)>")
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')

INTERNAL_LINK_RE = re.compile(r'href="(/[^"]*)"')
PROMPT_RE = re.compile(r'<div class="prompt">(.*?)</div>', re.DOTALL)
IMG_TAG_RE = re.compile(r"<img\b[^>]*>")
IMG_SRC_RE = re.compile(r'\bsrc="([^"]*)"')
IMG_ALT_RE = re.compile(r'\balt="([^"]*)"')
ALWAYS_VALID_PATHS = ("/", "/feed.xml", "/sitemap.xml", "/robots.txt")

# --- レシピの密度の下限（2026-08-08 追加） ---
# 毎晩レシピを自動生成する担当を置いたので、薄い記事が積み上がるのを機械で止める。
# 閾値は既存20本の実測（指示文 最小8/中央12、内部リンク 最小1、本文 最小2,343字）
# より下に取ってある＝手で書いた良い記事は必ず通り、明らかに薄いものだけ落ちる。
# ⚠️ 上限（マーカー）と違って下限なので、誤検知が出ると全部無視されるようになる。
# 数字を上げたくなったら、先に既存記事を測り直すこと。
RECIPE_MIN_PROMPTS = 6
RECIPE_MIN_INTERNAL_LINKS = 1
RECIPE_MIN_BODY_CHARS = 1800
RECIPE_MIN_FIGURES = 1

# 図の下限には例外を置かない。2026-08-08 まで、図を必須にする前に書かれた集約型3本
# （verify-before-report / who-does-what / limit-what-ai-touches）を名指しで外していたが、
# 3本とも図を足したので一覧ごと消した。
# ⚠️ 例外を作らないこと。1件でも名指しで外すと、次に書く人が「そこに足せばいい」と学ぶ。

# --- 金額目安ブロック（2026-08-14 稼ぎ方研究の設計）---
#
# 金額は「出典つき単価 × 明示した前提」でしか出さない、という型を機械で守る。
# ⚠️ ここで見るのはブロックの中身の3点だけ。ブロックの外に書かれた金額は
# 見ない（価格と収入を機械で区別できないため。誤検知は検査全体の信用を殺す）。
MONEY_NOTE_RE = re.compile(r'<div class="money-note">(.*?)</div>', re.DOTALL)
# 🚨 字下げると Markdown がコードブロックにして、divが `&lt;div …&gt;` に化ける。
# そのとき読者には生HTMLが見え、しかも上の正規表現に当たらないので
# **検査が素通りする**＝金額の主張が出典・免責の強制を丸ごと迂回する。
# 2026-08-15 に実測で見つけた。化けた形を見つけたら、それ自体を止める。
# ⚠️ 金額ブロックの書き方そのものを記事で説明したくなったら、この検査に当たる。
# そのときは class 名を変えた例を載せること（検査を緩めない）。
MONEY_NOTE_ESCAPED = '&lt;div class="money-note"&gt;'
MONEY_DISCLAIMER = "収益を保証するものではありません"
MONEY_SOURCE_RE = re.compile(r'href="https?://')
MONEY_CHECKED_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# 収益を保証する断定。earn の黒レーン（2026-08-13）をコードにしたもの。
# ⚠️ 完全一致の少数だけにする。日本語の断定を正規表現で広く追うと誤検知が出て、
# validate 全体の信用が落ちる（このサイトの判断済みの型）。
BANNED_INCOME_PHRASES = (
    "必ず稼げ",
    "確実に稼げ",
    "絶対に稼げ",
    "誰でも稼げ",
    "円保証",
    "収入保証",
)
# 🚨 詐欺を防ぐ場面は、詐欺の勧誘文句を引用するのが仕事なので除外する。
# ⚠️ いまある safety 記事（too-good-offer-checklist）が引用しているのは
# 「AIで稼げる」で、これは上の6語のどれにも当たらない＝**今日この除外が
# 効いている記事は無い**。将来 safety 記事が「必ず稼げます」のように
# 勧誘文句をそのまま引くときのための備え。番人が本来の仕事を邪魔しないように。
INCOME_PHRASE_EXEMPT_SCENES = frozenset({"safety"})

# --- タイトルの型（2026-08-15 オーナー指示）---
#
# オーナー指示＝「方法よりも**何ができるか**のほうが分かりやすい」。
# 「〜すると、〜になる」は手法＋発見の形で、できることが読み取れない。
#
# ⚠️ **字数では検査しない。**46本を実測したら、30字超15本のうち10本は
# 「散らかったフォルダは、AIに『移動先だけ』出させて自分で動かす」のように
# 長いが分かりやすい題だった（誤検知が3分の2）。型だけを見る。
# 実測では、この型に当たったのは46本中5本で、**どれも指摘どおりの形**だった。
#
# 📌 既存記事の題は変えない（指示は「次から」）ので、証拠の様式と同じく日付で線を引く。
TITLE_ERA = date(2026, 8, 16)
TITLE_METHOD_FINDING_RE = re.compile(r"(?:する|させる|せる|なる)と、")

TAG_RE = re.compile(r"<[^>]+>")


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in PLACEHOLDER_HINTS)


def _secret_errors(where: str, text: str) -> list[str]:
    """機密らしきものを探す。トークンの中身はエラー文に出さない。"""
    errors: list[str] = []

    for pattern, label in TOKEN_PATTERNS:
        if pattern.search(text):
            errors.append(f"{where}: {label}らしき文字列が含まれています")

    for match in CREDENTIAL_RE.finditer(text):
        if _looks_like_placeholder(match.group(2)):
            continue
        errors.append(f"{where}: 認証情報らしき代入があります（{match.group(1)}=…）")

    for match in EMAIL_RE.finditer(text):
        address = match.group(0)
        if address.lower().endswith(SAFE_EMAIL_DOMAINS):
            continue
        errors.append(f"{where}: メールアドレス {address} が本文に含まれています")

    if LOCAL_PATH_RE.search(text):
        errors.append(f"{where}: ローカルの絶対パス（C:\\Users\\…）が含まれています")

    return errors


def _prompt_errors(where: str, body_html: str) -> list[str]:
    """AIへの指示文が「そのままコピーできる素のテキスト」かを見る。

    指示文は生HTMLで書くので、中に書いたものは一切変換されない。
    - タグを入れるとコピーしたときにタグごと貼られる
    - Markdownの ** は展開されず、画面に ** がそのまま出る
    どちらも書いた本人には気づきにくいので、ここで止める。
    """
    errors = []
    for index, body in enumerate(PROMPT_RE.findall(body_html), start=1):
        if "<" in body:
            errors.append(f"{where}: {index}個目の指示文にHTMLタグが入っています（コピーすると混ざります）")
        if "**" in body:
            errors.append(f"{where}: {index}個目の指示文に ** が入っています（画面にそのまま出ます）")
    return errors


def _has_affiliate_link(text: str) -> bool:
    return any(pattern.search(text) for pattern in AFFILIATE_PATTERNS)


def _link_errors(
    where: str,
    body_html: str,
    valid_paths: set[str],
    static_paths: set[str] | None,
) -> list[str]:
    errors = []
    for raw in INTERNAL_LINK_RE.findall(body_html):
        path = raw.split("#")[0].split("?")[0]
        if not path:
            continue
        if path.startswith("/static/"):
            # 静的ファイルの一覧を渡されたときだけ実在を見る
            if static_paths is not None and path not in static_paths:
                errors.append(f"{where}: リンク先 {raw} が存在しません")
            continue
        if path in valid_paths:
            continue
        errors.append(f"{where}: リンク先 {raw} が存在しません")
    return errors


def _image_errors(where: str, body_html: str, static_paths: set[str] | None) -> list[str]:
    """画像の参照先と alt を検査する。

    alt を必須にするのは、読み上げ環境で図の意味が消えるのを防ぐため。
    図が説明の中心になる記事ほど、alt が無いと本文が成立しなくなる。
    """
    errors = []
    for tag in IMG_TAG_RE.findall(body_html):
        src_match = IMG_SRC_RE.search(tag)
        src = src_match.group(1) if src_match else ""
        alt_match = IMG_ALT_RE.search(tag)

        if not src:
            errors.append(f"{where}: src の無い画像があります")
        elif src.startswith("/static/") and static_paths is not None:
            if src not in static_paths:
                errors.append(f"{where}: 画像 {src} が存在しません")

        if alt_match is None or not alt_match.group(1).strip():
            errors.append(f"{where}: 画像 {src or '(src不明)'} に alt がありません")
    return errors


def _marker_errors(where: str, body_html: str) -> list[str]:
    """マーカーの数を数える。2026-08-02 まで人間が手で数えていた工程。"""
    errors = []
    total = len(MARK_RE.findall(body_html))
    warns = len(MARK_WARN_RE.findall(body_html))
    if total > MARK_MAX:
        errors.append(
            f"{where}: マーカーが{total}個あります"
            f"（上限{MARK_MAX}個。増やすと目印として働きません）"
        )
    if warns > MARK_WARN_MAX:
        errors.append(
            f"{where}: 警告マーカー（赤）が{warns}個あります"
            f"（上限{MARK_WARN_MAX}個。「やると事故る」だけに使わないと効かなくなります）"
        )
    return errors


def _density_errors(where: str, article: Article) -> list[str]:
    """レシピが薄すぎないかを見る。自動生成を積み上げるための歯止め。

    レシピだけを対象にする。ツール記事（数字の比較）と固定ページは、
    指示文が少なくても成り立つ形なので同じ物差しを当てない。
    """
    if article.category != "recipes":
        return []

    body = article.body_html
    errors = []

    prompts = len(PROMPT_RE.findall(body))
    if prompts < RECIPE_MIN_PROMPTS:
        errors.append(
            f"{where}: 指示文が{prompts}個しかありません"
            f"（レシピは{RECIPE_MIN_PROMPTS}個以上。指示文がこのサイトの本体です）"
        )

    links = [p for p in INTERNAL_LINK_RE.findall(body) if p.startswith(("/recipes/", "/tools/"))]
    if len(links) < RECIPE_MIN_INTERNAL_LINKS:
        errors.append(
            f"{where}: 他の記事へのリンクがありません"
            f"（{RECIPE_MIN_INTERNAL_LINKS}本以上。読者の次の一手を用意してください）"
        )

    figures = len(IMG_TAG_RE.findall(body))
    if figures < RECIPE_MIN_FIGURES:
        errors.append(
            f"{where}: 図が1枚もありません"
            f"（文字だけだと読まれません。tools/make_figures.py で作ってください）"
        )

    chars = len(TAG_RE.sub("", body).strip())
    if chars < RECIPE_MIN_BODY_CHARS:
        errors.append(
            f"{where}: 本文が{chars}字しかありません"
            f"（レシピは{RECIPE_MIN_BODY_CHARS}字以上。薄い記事は審査にも読者にも効きません）"
        )

    return errors


def _checked_errors(where: str, article: Article, today: date) -> list[str]:
    """確認日の形だけを見る。

    ⚠️ 「古い」ではビルドを止めない。古さは時間が経てば勝手に起きるので、
    止めると毎晩21:00のレシピ担当が push した記事が、指南書の日付を理由に
    公開されなくなる（build.py は「全部通る or 何も出さない」）。
    古さと外部リンク切れは tools/check_freshness.py が週次で見る。

    ここで止めるのは、書いた本人がその場で直せる「未来の日付」だけ。
    """
    if article.checked is None:
        return []
    if article.checked > today:
        return [
            f"{where}: 確認日が未来の日付です"
            f"（checked: {article.checked} / 今日: {today}）"
        ]
    return []


def _title_errors(where: str, article: Article) -> list[str]:
    """タイトルが「手法＋発見」の形になっていないかを見る。

    見るのは形だけで、分かりやすさそのものは機械には分からない
    （そこは確認担当の観点7が持つ）。ここで止めるのは、
    オーナーが名指しした「〜すると、〜になる」という1つの型だけ。
    """
    if article.published < TITLE_ERA:
        return []
    if not TITLE_METHOD_FINDING_RE.search(article.title):
        return []
    return [
        f"{where}: タイトルが「〜すると、〜になる」の形です"
        f"（手法＋発見）。**何ができるか**に書き直してください"
        f"（例: 「時給をAIに出させると線引きが書かれない」→「副業の本当の時給を出す」。"
        f"手法と発見は説明文へ。content/_recipe_queue.md の「タイトルの付け方」）"
    ]


def _money_note_errors(where: str, body_html: str) -> list[str]:
    """金額目安ブロックの中身を検査する。

    ブロックが無ければ何も言わない（金額を書かない記事のほうが多い）。
    あるなら、出典・確認日・免責の3点が揃っていること。
    """
    errors = []
    blocks = list(MONEY_NOTE_RE.finditer(body_html))

    if MONEY_NOTE_ESCAPED in body_html and not blocks:
        errors.append(
            f"{where}: 金額ブロックが**ブロックになっていません**"
            f"（4スペース以上の字下げがあると、Markdownがコードとして出します）。"
            f"行頭から書いてください"
        )

    for index, match in enumerate(blocks, start=1):
        block = match.group(1)
        where_block = f"{where}: 金額ブロック{index}"
        if MONEY_DISCLAIMER not in block:
            errors.append(
                f"{where_block}に「{MONEY_DISCLAIMER}」の一文がありません"
            )
        if not MONEY_SOURCE_RE.search(block):
            errors.append(f"{where_block}に出典のリンクがありません")
        if not MONEY_CHECKED_RE.search(block):
            errors.append(
                f"{where_block}に確認日（YYYY-MM-DD）がありません"
            )
    return errors


def _income_phrase_errors(where: str, article: Article) -> list[str]:
    """収益を保証する断定を見つける。

    ⚠️ 誤検知してはいけないものが2つある:
    ①免責文（「収益を保証するものではありません」）＝語を選んで避けてある
     （「円保証」「収入保証」は免責文と一致しない）
    ②詐欺を防ぐ場面の引用＝場面ごと除外する
    """
    if article.scene in INCOME_PHRASE_EXEMPT_SCENES:
        return []
    return [
        f"{where}: 収益を保証する書き方があります（「{phrase}」）"
        for phrase in BANNED_INCOME_PHRASES
        if phrase in article.body_html
    ]


def _heading_errors(where: str, body_html: str) -> list[str]:
    """見出しのclassを検査する。

    誤字も付け忘れも、既定アイコンが出るだけで見た目は崩れない。
    ブラウザで数を突き合わせる手作業をここに置き換える。
    """
    errors = []
    h2_classes: list[str] = []

    for match in HEADING_RE.finditer(body_html):
        level, attrs = match.group(1), match.group(2)
        found = CLASS_ATTR_RE.search(attrs)
        css_class = found.group(1).strip() if found else ""
        allowed = SECTION_CLASSES if level == "h2" else TROUBLE_CLASSES
        if css_class and css_class not in allowed:
            errors.append(
                f"{where}: {level} に知らない class が付いています: {css_class}"
                f"（{' / '.join(sorted(allowed))} のいずれか）"
            )
        if level == "h2":
            h2_classes.append(css_class)

    # 全部付いていないのは固定ページの正常な形。混ざっているのが付け忘れ。
    if any(h2_classes) and not all(h2_classes):
        missing = sum(1 for css_class in h2_classes if not css_class)
        errors.append(
            f"{where}: h2 が{len(h2_classes)}個あるうち{missing}個に class がありません"
            "（付け忘れても見た目は崩れないので、ここで止めます）"
        )
    return errors


# --- 証拠の機械照合（進化ループ v1.5・2026-08-14 に昇格）---
#
# 記事に載せた指示文は、証拠ファイルに**同じ文字列で**入っていなければならない。
# キュー10条（記事と同一文字列で全文を残す）をコードで強制する。
#
# 📌 昇格の経緯: 8/14 朝の較正では一致率 94/129（73%）だったので、まず
# `tools/check_freshness.py` に置いて週次で可視化した。畳んで記録されていた
# 33件を同日中に追試して **129/129（100%）** にしたので、ここへ移した。
# ⚠️ ビルドで止めてよいのは「本人がその場で直せるもの」だけ。この検査は
# 書いた本人が証拠を書き足せば直るので、その条件を満たす。
EVIDENCE_ERA = date(2026, 8, 12)  # 進化ループ v1 の証拠様式が入った日


def _evidence_errors(article: Article, evidence: dict[str, str] | None) -> list[str]:
    """指示文が証拠に見つからなければエラー。era より前の記事は対象外。

    ⚠️ 対象を slug 名指しで外さない（`FIGURE_EXEMPT_SLUGS` の教訓＝
    名指しの穴は「そこに足せばいい」と学習される）。線は日付で引く。
    """
    if evidence is None or article.category != "recipes":
        return []
    if article.published < EVIDENCE_ERA:
        return []
    where = str(article.source_path)
    text = evidence.get(article.slug)
    if text is None:
        return [
            f"{where}: 証拠ファイル docs/evidence/{article.slug}.md がありません"
            f"（キュー10条。試した記録が無い記事は公開しません）"
        ]
    prompts = [
        html.unescape(body).strip()
        for body in PROMPT_RE.findall(article.body_html)
    ]
    missing = [p for p in prompts if p not in text]
    if not missing:
        return []
    sample = missing[0].splitlines()[0][:40]
    return [
        f"{where}: 指示文{len(missing)}/{len(prompts)}件が"
        f"docs/evidence/{article.slug}.md に同じ文字列で見つかりません"
        f"（例: 「{sample}…」）。記事と証拠は同一文字列にしてください"
    ]


def validate(
    articles: list[Article],
    static_paths: set[str] | None = None,
    today: date | None = None,
    evidence: dict[str, str] | None = None,
) -> list[str]:
    """全記事を検査してエラー文字列のリストを返す。空なら公開してよい。

    static_paths には `/static/...` 形式の実在する静的ファイルの一覧を渡す。
    ディスクを見に行くのは build.py の仕事なので、ここは渡された集合と
    照合するだけにしてある。渡されなければ静的ファイルの実在は検査しない。
    evidence も同じ流儀＝{slug: 証拠の本文}。渡されなければ検査しない。
    """
    today = today or date.today()
    errors: list[str] = []

    reserved = {"/"} | {f"/{name}/" for name in config.LISTED_CATEGORIES}
    valid_paths = set(ALWAYS_VALID_PATHS) | reserved | {a.url for a in articles}
    taken: dict[str, str] = {}

    for article in articles:
        where = str(article.source_path)
        text = html.unescape(article.body_html)

        errors += _secret_errors(where, text)
        errors += _secret_errors(where, f"{article.title} {article.description}")

        if article.source_path.parent.name != article.category:
            errors.append(
                f"{where}: 置き場所とカテゴリが食い違っています"
                f"（category: {article.category} / フォルダ: {article.source_path.parent.name}/）"
            )

        if article.url in reserved:
            errors.append(f"{where}: {article.url} はサイトが使う予約済みURLです")
        elif article.url in taken:
            errors.append(f"{where}: URL {article.url} が {taken[article.url]} と重複しています")
        else:
            taken[article.url] = where

        errors += _link_errors(where, article.body_html, valid_paths, static_paths)
        errors += _evidence_errors(article, evidence)
        errors += _image_errors(where, article.body_html, static_paths)
        errors += _prompt_errors(where, article.body_html)
        errors += _marker_errors(where, article.body_html)
        errors += _heading_errors(where, article.body_html)
        errors += _density_errors(where, article)
        errors += _checked_errors(where, article, today)
        errors += _title_errors(where, article)
        errors += _money_note_errors(where, article.body_html)
        errors += _income_phrase_errors(where, article)

        if _has_affiliate_link(text) and not any(word in text for word in DISCLOSURE_WORDS):
            errors.append(
                f"{where}: アフィリエイトリンクがあるのに「広告」「PR」の表記がありません"
            )

    return errors
