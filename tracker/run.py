# -*- coding: utf-8 -*-
"""トラッカーのエントリポイント。

fetcher と mailer は引数で差し替えられるようにしてある。テストが
ネットワークにも SMTP にも出ないようにするため。

「送信してから保存する」順序は意図的。保存を先にすると、送信に失敗したときに
「既読にしたのに届いていない更新」が生まれて永久に失われる。逆順なら最悪でも
重複送信で済み、情報は落ちない。
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import deepdive
from . import fetch as fetch_module
from . import notify, store, summarize
from .classify import classify

DEFAULT_SOURCES = Path(__file__).parent / "sources.yml"
DEFAULT_STATE = Path("data/tracker/seen.json")
DEFAULT_QUEUE = Path("content/_deepdive_queue.md")


def _default_mailer(subject: str, plain: str, html_body: str) -> None:
    notify.send_mail(subject, plain, html_body)


REQUIRED_KEYS = ("id", "vendor", "label", "type")


def _source_label(source: dict, index: int) -> str:
    """ソースを識別するラベル。id があればそれを、無ければ位置から作る。

    _valid_sources と forget_removed_sources 用の active_source_ids の
    両方でこの同じラベルを使うこと。片方だけ生の source["id"] を使うと、
    id の無い壊れた定義でまた KeyError になるか、記録した直後の死活記録を
    forget_removed_sources が同じ run 内で消してしまう。
    """
    return source.get("id") or f"sources[{index}]"


def _valid_sources(sources: list[dict], state: dict) -> list[dict]:
    """必須キーの揃ったソースだけを返し、壊れた定義は死活記録に落とす。

    sources.yml は手書きなので誤字が入る。1件の誤字で全ソースの取得が
    止まらないよう、壊れた定義だけを外して残りは通常どおり処理する。
    外した定義はダイジェストの死活警告に出るので放置されない。
    """
    valid = []
    for index, source in enumerate(sources):
        missing = [key for key in REQUIRED_KEYS if not source.get(key)]
        if missing:
            label = _source_label(source, index)
            reason = f"定義エラー: {'/'.join(missing)} が無い"
            store.record_result(state, label, reason, 0)
            # 絵文字は使わない。cp932 コンソール（PYTHONUTF8 未設定の Windows）では
            # "⚠️" の実行時 print が UnicodeEncodeError で落ちる。既存の他の
            # print はどれも絵文字を含まないのと合わせる。
            print(f"[警告] {label}: {reason}")
            continue
        valid.append(source)
    return valid


def _collect(sources: list[dict], state: dict, fetcher) -> list:
    """全ソースを取得し、重要度を付けた Update のリストを返す。

    record_result には select_unseen 前の生の件数を渡す。新着件数を渡すと、
    更新の少ないソースが数時間で死亡扱いになる。
    """
    collected = []
    for source in _valid_sources(sources, state):
        updates, error = fetcher(source)
        store.record_result(state, source["id"], error, len(updates))
        store.record_latest(state, source["id"], updates)
        collected.extend(classify(u, source["type"]) for u in updates)
    return collected


def _enqueue_deepdive(major, sources, state, now, queue_path) -> None:
    """major のお知らせを深掘りキューへ自動追記する。

    キューは派生データなので、ここの失敗でメール送信や既読の保存を
    巻き込まない（要約と同じ扱い）。失敗はログに出して次へ進む。
    """
    queue_path = Path(queue_path)
    if not queue_path.exists():
        print(f"[警告] 深掘りキューが見つからないため自動追記しません: {queue_path}")
        return
    try:
        source_types = {
            s["id"]: s["type"] for s in sources if s.get("id") and s.get("type")
        }
        text = queue_path.read_text(encoding="utf-8")
        picked = deepdive.select_candidates(
            major,
            source_types,
            queued_uids=store.deepdive_queued_uids(state),
            queued_urls_=deepdive.queued_urls(text),
            today_count=store.deepdive_queued_today(state, now),
        )
        if not picked:
            return
        queue_path.write_text(
            deepdive.append_lines(text, picked, now), encoding="utf-8", newline="\n"
        )
        store.record_deepdive_queued(state, picked, now)
        print(f"深掘りキューへ {len(picked)}件を自動追記")
    except OSError as error:
        print(f"[警告] 深掘りキューへの追記に失敗: {error}")


def run_check(*, sources, state_path, fetcher, mailer, now, news_path=None,
              queue_path=None) -> int:
    """毎時チェック。major は即送信、minor はダイジェスト用に溜める。"""
    state = store.load_state(state_path)
    collected = _collect(sources, state, fetcher)
    fresh = store.select_unseen(state, collected)

    # アーカイブは送信より先に書く。送信に失敗した回の記事が抜けると、
    # あとから埋められない穴になるため。uid で重複を弾くので、送信に失敗して
    # 次の回で再送されても二重にはならない。
    archive_path = news_path or store.news_path_for(state_path)
    archive = store.load_news(archive_path)
    store.append_news(archive, fresh, now)
    store.prune_news(archive, now)
    store.save_news(archive_path, archive)

    major = [u for u in fresh if u.importance == "major"]
    minor = [u for u in fresh if u.importance == "minor"]

    if major:
        plain, html_body = notify.build_body(major, [])
        mailer(notify.build_subject("major", len(major)), plain, html_body)
        # build_body が1通に載せきれなかった分は捨てずにダイジェストへ回す。
        # 捨てると「情報は失われず最大24時間遅れるだけ」の原則が壊れる。
        newest_first = sorted(major, key=lambda u: u.published, reverse=True)
        minor = minor + newest_first[notify.MAX_ITEMS:]
        if queue_path is not None:
            _enqueue_deepdive(major, sources, state, now, queue_path)

    store.mark_seen(state, fresh, now)
    store.queue_minor(state, minor)
    active_ids = {_source_label(s, i) for i, s in enumerate(sources)}
    store.forget_removed_sources(state, active_ids)
    store.prune(state, now)
    store.save_state(state_path, state)

    print(f"新着 {len(fresh)}件（major {len(major)} / minor {len(minor)}）")
    return len(fresh)


def run_digest(*, state_path, mailer, now) -> int:
    """毎朝のダイジェスト。溜まった minor と異常なソースを1通にまとめる。

    異常は2種類ある。取得できていない(dead)ものと、取得はできるが中身が
    止まっている(stale)もの。後者は失敗カウントが0のままなので、公開日を
    見ないと永久に気づけない。
    """
    state = store.load_state(state_path)
    pending = store.take_pending_minor(state)
    dead = store.dead_sources(state)
    stale = store.stale_sources(state, now)

    if not pending and not dead and not stale:
        print("ダイジェスト対象なし。送信しません")
        return 0

    plain, html_body = notify.build_body(pending, dead, stale)
    mailer(
        notify.build_subject(
            "digest", len(pending), dead_count=len(dead), stale_count=len(stale)
        ),
        plain,
        html_body,
    )
    store.save_state(state_path, state)

    print(
        f"ダイジェスト送信 {len(pending)}件"
        f"（取得失敗 {len(dead)}件 / 更新停止 {len(stale)}件）"
    )
    return len(pending)


def run_summarize(*, news_path, source_types, client) -> int:
    """アーカイブのうち、まだ要約の無いお知らせに日本語の要約を付ける。

    メール送信とは別の実行にしてある。要約は派生データなので、Geminiが
    落ちている日にメールまで止まるのは筋が悪い。
    """
    news = store.load_news(news_path)
    targets = [i for i in news["items"] if summarize.needs_summary(i, source_types)]
    if not targets:
        print("要約が必要な記事はありません")
        return 0

    added = summarize.apply_summaries(targets, client)
    if added:
        store.save_news(news_path, news)
    print(f"要約 {added}件（対象 {len(targets)}件・残りは次の実行で）")
    return added


def run_bootstrap(*, sources, state_path, fetcher, mailer, now) -> int:
    """初回セットアップ。全件を既読にするだけで、1通も送らない。

    これをせずに run_check を初回実行すると、OpenAI news だけで1105件の
    通知が飛ぶ。
    """
    state = store.load_state(state_path)
    collected = _collect(sources, state, fetcher)
    store.mark_seen(state, collected, now)
    state["pending_minor"] = []
    store.save_state(state_path, state)
    print(f"初期化しました。{len(collected)}件を既読として記録（通知なし）")
    return len(collected)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AI更新情報トラッカー")
    parser.add_argument(
        "--mode",
        choices=["check", "digest", "bootstrap", "summarize"],
        required=True,
    )
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    args = parser.parse_args(argv)

    if args.mode == "check" and not args.state.exists():
        print(
            f"状態ファイルがありません: {args.state}\n"
            "先に --mode bootstrap を実行してください。これをせずに check を走らせると、"
            "全ソースの過去記事が新着扱いになり1000通以上のメールが飛びます。"
        )
        return 1

    now = datetime.now(timezone.utc)

    if args.mode == "digest":
        run_digest(state_path=args.state, mailer=_default_mailer, now=now)
        return 0

    if args.mode == "summarize":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # ここで exit 1 にしない。この後に控える既読状態のコミットが
            # 止まると、送信済みの記事が未読に戻って再送される。
            print("GEMINI_API_KEY が未設定のため要約しません（記事の収集には影響しません）")
            return 0
        sources = fetch_module.load_sources(args.sources)
        run_summarize(
            news_path=store.news_path_for(args.state),
            source_types={s["id"]: s["type"] for s in sources
                          if s.get("id") and s.get("type")},
            client=summarize.gemini_client(api_key),
        )
        return 0

    sources = fetch_module.load_sources(args.sources)
    if args.mode == "check":
        run_check(
            sources=sources,
            state_path=args.state,
            fetcher=fetch_module.fetch_source,
            mailer=_default_mailer,
            now=now,
            queue_path=DEFAULT_QUEUE,
        )
    else:
        run_bootstrap(
            sources=sources,
            state_path=args.state,
            fetcher=fetch_module.fetch_source,
            mailer=_default_mailer,
            now=now,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
