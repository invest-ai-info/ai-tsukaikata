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
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import fetch as fetch_module
from . import notify, store
from .classify import classify

DEFAULT_SOURCES = Path(__file__).parent / "sources.yml"
DEFAULT_STATE = Path("data/tracker/seen.json")


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
        collected.extend(classify(u, source["type"]) for u in updates)
    return collected


def run_check(*, sources, state_path, fetcher, mailer, now) -> int:
    """毎時チェック。major は即送信、minor はダイジェスト用に溜める。"""
    state = store.load_state(state_path)
    collected = _collect(sources, state, fetcher)
    fresh = store.select_unseen(state, collected)

    major = [u for u in fresh if u.importance == "major"]
    minor = [u for u in fresh if u.importance == "minor"]

    if major:
        plain, html_body = notify.build_body(major, [])
        mailer(notify.build_subject("major", len(major)), plain, html_body)
        # build_body が1通に載せきれなかった分は捨てずにダイジェストへ回す。
        # 捨てると「情報は失われず最大24時間遅れるだけ」の原則が壊れる。
        newest_first = sorted(major, key=lambda u: u.published, reverse=True)
        minor = minor + newest_first[notify.MAX_ITEMS:]

    store.mark_seen(state, fresh, now)
    store.queue_minor(state, minor)
    active_ids = {_source_label(s, i) for i, s in enumerate(sources)}
    store.forget_removed_sources(state, active_ids)
    store.prune(state, now)
    store.save_state(state_path, state)

    print(f"新着 {len(fresh)}件（major {len(major)} / minor {len(minor)}）")
    return len(fresh)


def run_digest(*, state_path, mailer) -> int:
    """毎朝のダイジェスト。溜まった minor と死んだソースを1通にまとめる。"""
    state = store.load_state(state_path)
    pending = store.take_pending_minor(state)
    dead = store.dead_sources(state)

    if not pending and not dead:
        print("ダイジェスト対象なし。送信しません")
        return 0

    plain, html_body = notify.build_body(pending, dead)
    mailer(
        notify.build_subject("digest", len(pending), dead_count=len(dead)),
        plain,
        html_body,
    )
    store.save_state(state_path, state)

    print(f"ダイジェスト送信 {len(pending)}件（死活警告 {len(dead)}件）")
    return len(pending)


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
    parser.add_argument("--mode", choices=["check", "digest", "bootstrap"], required=True)
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
        run_digest(state_path=args.state, mailer=_default_mailer)
        return 0

    sources = fetch_module.load_sources(args.sources)
    runner = run_check if args.mode == "check" else run_bootstrap
    runner(
        sources=sources,
        state_path=args.state,
        fetcher=fetch_module.fetch_source,
        mailer=_default_mailer,
        now=now,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
