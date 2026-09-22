# -*- coding: utf-8 -*-
"""tools/rotate_archives.py — 終わった在庫を archive へ逐語で移す機械回転。

設計 = docs/superpowers/specs/2026-08-20-token-diet-design.md
守るべき既存の依存（ここのテストが回帰の壁になる）:
  - tracker.deepdive.queued_urls はマーカー行の残りをURLとして読む
    → 回転後もマーカー行は残す（消すと同じURLが再追記される）
  - check_freshness.earn_research_heartbeat は `^### YYYY-MM-DD` の最大値を見る
    → 直近3日ぶんの節を残せば48h検知は無傷
"""
import sys
from datetime import date
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from rotate_archives import (  # noqa: E402
    append_archive,
    rotate_all,
    rotate_hypotheses,
    rotate_daily_log,
    rotate_queue,
)
from check_freshness import (  # noqa: E402
    earn_research_heartbeat,
    file_budgets,
    hypothesis_registration_gaps,
    hypothesis_stock_empty,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker.deepdive import queued_urls  # noqa: E402


QUEUE = dedent("""\
    # キュー

    ## 書き方

    - 済んだら `- [x]` に変える。

    ## 待ち行列

    - [x] 長いメールの山から抜く
      - 公開: `mail-needs-reply`（2026-08-08）／題を変えた。
        実際に架空の受信箱14通で試した。
    - [ ] まだやっていない題材
      - 切り口: これは残る
    - [!] 取材の質問づくり
      - 症状が起きなかったので記事にしていない（全24回）。
    """)


class TestRotateQueue:
    def test_done_item_details_move_to_archive(self):
        new, chunks = rotate_queue(QUEUE, markers=("- [x] ", "- [!] "))
        assert "架空の受信箱14通" not in new
        assert any("架空の受信箱14通" in c for c in chunks)

    def test_marker_line_survives(self):
        # 行ごと消すと deepdive の URL 重複防止が壊れる。題での重複確認も同じ
        new, _ = rotate_queue(QUEUE, markers=("- [x] ", "- [!] "))
        assert "- [x] 長いメールの山から抜く" in new
        assert "- [!] 取材の質問づくり" in new

    def test_undone_item_is_untouched(self):
        new, _ = rotate_queue(QUEUE, markers=("- [x] ", "- [!] "))
        assert "- [ ] まだやっていない題材\n  - 切り口: これは残る" in new

    def test_slug_is_kept_in_the_index_line(self):
        # ネタ探しの重複確認は索引行で足りるように slug を残す
        new, _ = rotate_queue(QUEUE, markers=("- [x] ", "- [!] "))
        assert "mail-needs-reply" in new

    def test_reason_first_line_is_kept_for_rejected(self):
        new, _ = rotate_queue(QUEUE, markers=("- [x] ", "- [!] "))
        idx = new.index("- [!] 取材の質問づくり")
        note = new[idx:].splitlines()[1]
        assert "症状が起きなかった" in note

    def test_markers_param_limits_targets(self):
        # deepdive は [x] だけ（[!] は経路遮断の再試行対象なので触らない）
        new, _ = rotate_queue(QUEUE, markers=("- [x] ",))
        assert "症状が起きなかったので記事にしていない（全24回）。" in new

    def test_idempotent(self):
        once, chunks = rotate_queue(QUEUE, markers=("- [x] ", "- [!] "))
        twice, chunks2 = rotate_queue(once, markers=("- [x] ", "- [!] "))
        assert twice == once
        assert chunks2 == []

    def test_bare_marker_line_without_details_is_untouched(self):
        text = "## 待ち行列\n\n- [x] 詳細なしの行\n"
        new, chunks = rotate_queue(text, markers=("- [x] ",))
        assert new == text
        assert chunks == []

    def test_instructions_before_queue_heading_are_untouched(self):
        # 冒頭の指示節にある `- [x]` の例文を巻き込まない
        new, _ = rotate_queue(QUEUE, markers=("- [x] ", "- [!] "))
        assert "- 済んだら `- [x]` に変える。" in new

    def test_deepdive_url_dedup_still_works_after_rotation(self):
        text = dedent("""\
            ## 待ち行列

            - [x] https://example.com/announce
              - **2026-08-05: 下書きを作成**（長い詳細）。
            """)
        new, _ = rotate_queue(text, markers=("- [x] ",))
        assert "https://example.com/announce" in queued_urls(new)

NOTED = dedent("""\
    ## 待ち行列

    - [x] 案件のAI利用ルールを確かめる
      - →保管: 公開: `job-ai-policy-check`（2026-08-27。実測は全39回
        ＋追加検証7回。証拠は `docs/evidence/job-ai-policy-check.md`）
        🔑 企画仕様から意図的に外した2点、理由つき
      - 2026-08-20 自動追記（major）
    - [x] 回転済みの行
      - →保管: 公開: `already-rotated`
    - [!] 数字が1つ埋まっているだけで
      - →保管: **重複のため保留（2026-09-19・レシピ担当）**。上の項目と同じ
        根拠・実測の芯がほぼ一字一句同じ
    """)


class TestRotateQueueWhenTheNoteWasWrittenByHand:
    """担当が自分で `→保管:` を書き、その下に長い報告を続ける形。

    2026-09-22 実測: `_recipe_queue.md` で済んだ項目158件のうち66件がこの形で、
    約2,300行が「回転済み」とみなされて回転をすり抜けていた（予算2500行に対して4594行）。
    索引行1本だけ残して、残りは逐語で保管庫へ。
    """

    def test_long_body_under_a_hand_written_note_is_moved(self):
        new, chunks = rotate_queue(NOTED, markers=("- [x] ", "- [!] "))
        assert "追加検証7回" not in new
        assert "企画仕様から意図的に外した" not in new
        assert "2026-08-20 自動追記" not in new
        assert any("追加検証7回" in c and "2026-08-20 自動追記" in c for c in chunks)

    def test_index_line_is_rebuilt_from_the_slug_without_doubling_the_prefix(self):
        new, _ = rotate_queue(NOTED, markers=("- [x] ", "- [!] "))
        idx = new.index("- [x] 案件のAI利用ルールを確かめる")
        note = new[idx:].splitlines()[1]
        assert note == "  - →保管: 公開: `job-ai-policy-check`"

    def test_note_without_slug_keeps_its_first_line_once(self):
        new, _ = rotate_queue(NOTED, markers=("- [x] ", "- [!] "))
        idx = new.index("- [!] 数字が1つ埋まっているだけで")
        note = new[idx:].splitlines()[1]
        assert note.startswith("  - →保管: **重複のため保留")
        assert note.count("→保管") == 1
        assert "根拠・実測の芯" not in new

    def test_single_line_note_is_left_alone(self):
        new, chunks = rotate_queue(NOTED, markers=("- [x] ", "- [!] "))
        assert "- [x] 回転済みの行\n  - →保管: 公開: `already-rotated`\n" in new
        assert not any("already-rotated" in c for c in chunks)

    def test_idempotent(self):
        once, _ = rotate_queue(NOTED, markers=("- [x] ", "- [!] "))
        twice, chunks = rotate_queue(once, markers=("- [x] ", "- [!] "))
        assert twice == once
        assert chunks == []

    def test_deepdive_style_note_survives_as_one_index_line(self):
        text = dedent("""\
            ## 待ち行列

            - [x] https://deepmind.google/blog/introducing-agentic-video-in-gemini/
              - →保管: ✅ **2026-09-03: 公開した** → `content/tools/gemini-agentic-video.md`
                （`deepmind.google` → `blog.google` へ302転送・到達できた。図3枚）
              - 2026-09-01 自動追記（major・Google DeepMind）
            """)
        new, chunks = rotate_queue(text, markers=("- [x] ",))
        assert "https://deepmind.google/blog/introducing-agentic-video-in-gemini/" in queued_urls(new)
        note = new.splitlines()[3]
        assert note.startswith("  - →保管: ✅ **2026-09-03: 公開した**")
        assert note.count("→保管") == 1
        assert "302転送" not in new
        assert any("302転送" in c for c in chunks)

PROSE = dedent("""\
    # キュー

    ## 待ち行列

    ### 副業（2026-08-13・オーナー指示で新設。場面 `earn`）

    🎯 この節の目的（オーナー指示）＝決まりなので、いつまでも残す。

    - [x] 済んだ副業の題材
      - →保管: 公開: `done-earn`

    #### 補充（2026-08-19・ネタ探し担当。源①から4件）

    🚨 **足した理由＝この節が今夜で実弾ゼロになるから。**
    残量の説明がさらに数行続く。

    - [x] 足した題材A
      - →保管: 公開: `added-a`
    - [!] 足した題材B
      - →保管: 重複のため保留

    #### 補充（2026-09-14・ネタ探し担当。床割れ対応）

    🚨 足した理由。下の2件は**この順に**書くこと。

    - [ ] まだ書いていない題材
      - 切り口: これは残る
    - [x] もう書いた題材
      - →保管: 公開: `added-c`

    #### 詰まったところ（2026-09-14）

    促進項目3件は今日も一次情報に届かなかった。
    明日の担当は環境の許可リストを確認すること。

    ## 処理済み

    ### 2026-09-14 21:00 レシピ担当

    いちばん古い日報。

    ### 2026-09-16 21:00 レシピ担当

    2番目に古い日報。

    ### 2026-09-17 21:00 レシピ担当

    3番目の日報。

    ### 2026-09-18 21:00 レシピ担当

    最新の日報＝今夜の担当が「どこから着手するか」を読む。
    """)


class TestRotateQueueProse:
    """待ち行列の散文（補充の経緯・担当の日誌）も回転の対象にする。

    2026-09-22 実測: `_recipe_queue.md` の待ち行列 2,009行のうち **920行が散文**で、
    項目でも索引でもないのに毎晩3〜4担当が読み直していた（中身は `_earn_research.md`・
    `_writer_log.md`・`_hypothesis_queue.md` と重複）。
    ⚠️ **未処理が残っている節の散文は動かさない**（並び順の指示など、まだ効く指示が混ざる）。
    ⚠️ **場面の節（副業・詐欺を防ぐ等）の決まりは動かさない**（日付の付いた補充・研究パック・
    担当の日誌だけを対象にする＝許可リスト方式。新しい種類の見出しを巻き込まない）。
    """

    def test_prose_of_a_finished_restock_moves(self):
        new, chunks = rotate_queue(PROSE, markers=("- [x] ", "- [!] "), prose=True)
        assert "足した理由＝この節が今夜で実弾ゼロになるから" not in new
        assert any("足した理由＝この節が今夜で実弾ゼロになるから" in c for c in chunks)
        assert "#### 補充（2026-08-19・ネタ探し担当。源①から4件）" in new

    def test_items_and_marker_lines_are_never_touched(self):
        new, _ = rotate_queue(PROSE, markers=("- [x] ", "- [!] "), prose=True)
        for line in ("- [x] 足した題材A", "- [!] 足した題材B", "- [x] もう書いた題材",
                     "- [ ] まだ書いていない題材", "  - 切り口: これは残る"):
            assert line in new

    def test_prose_stays_while_an_open_item_remains(self):
        """並び順の指示など、まだ効く指示が混ざっているため。"""
        new, _ = rotate_queue(PROSE, markers=("- [x] ", "- [!] "), prose=True)
        assert "下の2件は**この順に**書くこと" in new

    def test_section_rules_stay(self):
        """場面の節の決まりは、済んだ項目しか無くても残す。"""
        new, _ = rotate_queue(PROSE, markers=("- [x] ", "- [!] "), prose=True)
        assert "この節の目的（オーナー指示）＝決まりなので、いつまでも残す" in new

    def test_log_block_moves_whole_with_an_index_line(self):
        new, chunks = rotate_queue(PROSE, markers=("- [x] ", "- [!] "), prose=True)
        assert "促進項目3件は今日も一次情報に届かなかった" not in new
        assert "#### 詰まったところ（2026-09-14）" not in new
        assert "- →保管: 詰まったところ（2026-09-14）" in new
        assert any("促進項目3件" in c for c in chunks)

    def test_processed_section_keeps_the_newest_three_days(self):
        new, chunks = rotate_queue(PROSE, markers=("- [x] ", "- [!] "), prose=True)
        assert "最新の日報＝今夜の担当が" in new
        assert "3番目の日報。" in new
        assert "2番目に古い日報。" in new
        assert "いちばん古い日報。" not in new
        assert "- →保管: 2026-09-14 21:00 レシピ担当" in new
        assert any("いちばん古い日報。" in c for c in chunks)

    def test_idempotent(self):
        once, _ = rotate_queue(PROSE, markers=("- [x] ", "- [!] "), prose=True)
        twice, chunks = rotate_queue(once, markers=("- [x] ", "- [!] "), prose=True)
        assert twice == once
        assert chunks == []


    def test_existing_index_lines_are_not_swallowed(self):
        """担当が残した `- →保管:` の索引行は、済んだ節でも消さない。

        2026-09-22 実測: 索引行は `- [` で始まらないので「散文」と判定され、
        2回目の回転で保管庫へ吸い込まれていた（跡形が消える＝回転が非冪等になる）。
        """
        text = dedent("""\
            ## 待ち行列

            #### 補充（2026-08-19・ネタ探し担当）

            🚨 足した理由の説明。

            - →保管: 2026-09-20 研究パック1件（担当が自分で残した索引行）

            - [x] 足した題材
              - →保管: 公開: `added`
            """)
        once, chunks = rotate_queue(text, markers=("- [x] ",), prose=True)
        assert "- →保管: 2026-09-20 研究パック1件（担当が自分で残した索引行）" in once
        assert "🚨 足した理由の説明。" not in once
        twice, chunks2 = rotate_queue(once, markers=("- [x] ",), prose=True)
        assert twice == once
        assert chunks2 == []

    def test_prose_is_untouched_without_the_flag(self):
        """深掘りキューなど、他のファイルの挙動は変えない。"""
        new, _ = rotate_queue(PROSE, markers=("- [x] ", "- [!] "))
        assert "足した理由＝この節が今夜で実弾ゼロになるから" in new
        assert "いちばん古い日報。" in new

HYPO = dedent("""\
    # 🔬 仮説キュー

    ## 書式（1仮説1ブロック）

    ```
    ### H<番号> <名前>
    - 状態: ⏳未着手 / 📤変換済み / ✅生存 / ❌棄却
    - 仮説: <1文>
    ```

    ---

    ## 優先キュー

    ### H1 個数指定は、使える案の個数と相関しない
    - 状態: 📤変換済み
    - 登録日: 2026-08-25
    - 仮説: ◯案出しての◯を増やしても、採用線を通る案は増えない。
    - 反証条件: 30案の通過数が5案の2倍以上なら棄却。

    ### H2 欠落は「1つだけ無い」ほうが検出されない
    - 状態: ❌棄却（2026-09-08・`long-report` で公開。反証条件を満たさず）
    - 登録日: 2026-08-25
    - 仮説: 1つだけ欠けた材料は見落とされる。

    ### H3 まだ渡していない仮説
    - 状態: ⏳未着手
    - 登録日: 2026-09-22
    - 仮説: これはこれから測る。

    ### H4 いま測っている最中の仮説
    - 状態: 🔬検証中
    - 登録日: 2026-09-21
    - 仮説: 測っている途中なので残す。

    ## バックログ（H番号は発行しない）

    - ~~済んだ候補~~ → H1で登録済み
    """)


class TestRotateHypotheses:
    """済んだ仮説（📤変換済み・✅生存・❌棄却・🚫検定不能）を保管庫へ。

    2026-09-22 実測: `_hypothesis_queue.md` は1,074行（予算900）で、毎日1件（約50行）
    増えるのに減る仕組みが無かった（ファイル自身に「✅／❌は手で移す」と書いてあった）。
    ⚠️ **⏳未着手と🔬検証中は動かさない**＝源0の在庫そのもの（`hypothesis_stock_empty()`
    が数える）。⚠️ **書式見本とバックログは触らない**（見本の `### H<番号>` を拾うと壊れる）。
    """

    def test_finished_blocks_move_with_an_index_line(self):
        new, chunks = rotate_hypotheses(HYPO)
        assert "- 反証条件: 30案の通過数が5案の2倍以上なら棄却。" not in new
        assert "- →保管: H1 個数指定は、使える案の個数と相関しない — 📤変換済み" in new
        assert any("反証条件: 30案の通過数" in c for c in chunks)

    def test_the_verdict_stays_readable_on_the_index_line(self):
        new, _ = rotate_hypotheses(HYPO)
        line = next(l for l in new.splitlines() if l.startswith("- →保管: H2"))
        assert "❌棄却" in line and "long-report" in line

    def test_unstarted_and_running_blocks_stay_whole(self):
        new, _ = rotate_hypotheses(HYPO)
        assert "### H3 まだ渡していない仮説\n- 状態: ⏳未着手" in new
        assert "- 仮説: これはこれから測る。" in new
        assert "### H4 いま測っている最中の仮説" in new
        assert "- 仮説: 測っている途中なので残す。" in new

    def test_format_sample_and_backlog_are_untouched(self):
        new, _ = rotate_hypotheses(HYPO)
        assert "### H<番号> <名前>" in new
        assert "- ~~済んだ候補~~ → H1で登録済み" in new

    def test_idempotent(self):
        once, _ = rotate_hypotheses(HYPO)
        twice, chunks = rotate_hypotheses(once)
        assert twice == once
        assert chunks == []

    def test_guards_still_read_the_rotated_file(self):
        """番人が壊れないこと＝在庫（⏳）は数えられ、必須欄の欠けは鳴らない。"""
        new, _ = rotate_hypotheses(HYPO)
        assert hypothesis_stock_empty(new) is None  # H3 が ⏳ で残っている
        assert [p for p in hypothesis_registration_gaps(new) if "H1" in p or "H2" in p] == []

    def test_numbers_stay_visible_for_the_next_registration(self):
        """次のH番号は索引行から分かること（担当が H1〜H4 を見て H5 を発行できる）。"""
        new, _ = rotate_hypotheses(HYPO)
        for n in ("H1", "H2", "H3", "H4"):
            assert n in new

BLOCKED = dedent("""\
    ## 待ち行列

    - [!] https://openai.com/index/one
      - 2026-08-26 自動追記（major・OpenAI）
      - 🛑 再試行対象外（先方のbot判定）
      - **2026-08-27 1回目: 記事を書かずに停止した。**長い調査の記録がここに続く。
        表も含めて数十行ある。
      - 2026-09-01 2回目: 変わらず。

    - [!] https://sakana.ai/frontier-intelligence-group/
      - 2026-09-18 自動追記（major・Sakana AI）
      - **2026-09-18 1回目: 停止した。**経路遮断でもbot判定でもない＝記事の型に合わない。
        オーナー確認待ち。

    - [ ] https://example.com/next
      - まだ処理していない
    """)


class TestRotateBlockedRows:
    """`- [!]`（保留）のうち、**印の付いた行だけ**を回転する。

    2026-09-22 オーナー判断「A」＝bot判定の行は再試行しないので、長い調査記録を
    live に置いておく意味が無い（実測: 深掘りキュー784行のうち約390行がこれ）。
    🚨 **語句で自動判定しない。**実測した7件はどれも本文に「bot判定」と「許可リスト」の
    両方が出てくるうえ、Sakana FIG の行は**読めたが記事の型に合わない**（＝bot判定ではない）。
    判定は担当が行に書いた印（`🛑 再試行対象外`）だけを見る。
    """

    def test_tagged_row_keeps_its_marker_and_the_reason(self):
        new, chunks = rotate_queue(BLOCKED, markers=("- [x] ",), blocked_tag="🛑 再試行対象外")
        assert "- [!] https://openai.com/index/one" in new
        assert "  - →保管: 🛑 再試行対象外（先方のbot判定）" in new
        assert "長い調査の記録がここに続く" not in new
        assert any("長い調査の記録がここに続く" in c for c in chunks)

    def test_untagged_row_is_untouched(self):
        new, _ = rotate_queue(BLOCKED, markers=("- [x] ",), blocked_tag="🛑 再試行対象外")
        assert "経路遮断でもbot判定でもない＝記事の型に合わない" in new
        assert "オーナー確認待ち" in new

    def test_open_item_is_untouched(self):
        new, _ = rotate_queue(BLOCKED, markers=("- [x] ",), blocked_tag="🛑 再試行対象外")
        assert "- [ ] https://example.com/next\n  - まだ処理していない" in new

    def test_url_dedup_still_sees_every_row(self):
        new, _ = rotate_queue(BLOCKED, markers=("- [x] ",), blocked_tag="🛑 再試行対象外")
        urls = queued_urls(new)
        assert "https://openai.com/index/one" in urls
        assert "https://sakana.ai/frontier-intelligence-group/" in urls

    def test_idempotent(self):
        once, _ = rotate_queue(BLOCKED, markers=("- [x] ",), blocked_tag="🛑 再試行対象外")
        twice, chunks = rotate_queue(once, markers=("- [x] ",), blocked_tag="🛑 再試行対象外")
        assert twice == once
        assert chunks == []

    def test_without_the_tag_option_nothing_moves(self):
        new, chunks = rotate_queue(BLOCKED, markers=("- [x] ",))
        assert "長い調査の記録がここに続く" in new
        assert chunks == []


DAILY = dedent("""\
    # ネタ帳

    ## 4つの源（毎回すべて見る）

    源の説明は日付があっても指示節なので残る（2026-08-14 オーナー指示）。

    ## 2026-08-15 — 担当の初回

    採用の詳細A。

    ### 内側の小見出し

    小見出しの中身も節の一部。

    ## 🚨 2026-08-15 — 担当からオーナーへの申し送り（2件）

    申し送りの中身は閉じるまで残す。

    ## 2026-08-16 — 5件採用

    採用の詳細B。

    ## 2026-08-17 — 4件採用

    採用の詳細C。

    ## 2026-08-18 — 2件採用

    採用の詳細D。
    """)


class TestRotateDailyLog:
    def test_keeps_newest_three_dates(self):
        new, chunks = rotate_daily_log(DAILY, heading_prefix="## ")
        assert "採用の詳細B" in new and "採用の詳細C" in new and "採用の詳細D" in new
        assert "採用の詳細A" not in new
        assert any("採用の詳細A" in c for c in chunks)

    def test_section_body_includes_inner_subheadings(self):
        _, chunks = rotate_daily_log(DAILY, heading_prefix="## ")
        assert any("小見出しの中身も節の一部" in c for c in chunks)

    def test_moushiokuri_is_exempt(self):
        new, _ = rotate_daily_log(DAILY, heading_prefix="## ")
        assert "申し送りの中身は閉じるまで残す" in new

    def test_instruction_headings_are_untouched(self):
        new, _ = rotate_daily_log(DAILY, heading_prefix="## ")
        assert "源の説明は日付があっても指示節なので残る" in new

    def test_index_line_replaces_archived_section(self):
        new, _ = rotate_daily_log(DAILY, heading_prefix="## ")
        assert "保管" in new and "2026-08-15 — 担当の初回" in new

    def test_three_or_fewer_dates_is_a_noop(self):
        text = "## 2026-08-16 — a\n\nA\n\n## 2026-08-17 — b\n\nB\n"
        new, chunks = rotate_daily_log(text, heading_prefix="## ")
        assert new == text
        assert chunks == []

    def test_same_date_twice_counts_as_one_day(self):
        # 「2026-08-15」と「2026-08-15（夜）」は同じ日＝一緒に残り、一緒に動く
        text = dedent("""\
            ## 2026-08-14 — a

            A

            ## 2026-08-15 — b

            B

            ## 2026-08-15（夜） — c

            C

            ## 2026-08-16 — d

            D

            ## 2026-08-17 — e

            E
            """)
        new, _ = rotate_daily_log(text, heading_prefix="## ")
        assert "B" in new and "C" in new
        assert "\nA\n" not in new

    def test_idempotent(self):
        once, _ = rotate_daily_log(DAILY, heading_prefix="## ")
        twice, chunks = rotate_daily_log(once, heading_prefix="## ")
        assert twice == once
        assert chunks == []

    def test_h3_config_for_earn_log_keeps_heartbeat_alive(self):
        text = dedent("""\
            ## 作業ログ

            ### 2026-08-14 — 初回

            古い日。

            ### 2026-08-15 — 2日目

            B

            ### 2026-08-16 — 3日目

            C

            ### 2026-08-17 — 4日目

            D
            """)
        new, _ = rotate_daily_log(text, heading_prefix="### ")
        assert "古い日" not in new
        # 回転後も heartbeat は最新の日付を読める（回帰の壁）
        assert earn_research_heartbeat(new, date(2026, 8, 18)) is None


class TestAppendArchive:
    def test_creates_file_with_header_and_appends(self):
        first = append_archive(None, ["- [x] a\n  - 詳細\n"], date(2026, 8, 21), "キュー")
        assert "2026-08-21" in first and "- [x] a" in first
        second = append_archive(first, ["- [x] b\n  - 詳細2\n"], date(2026, 8, 22), "キュー")
        assert first.rstrip("\n") in second and "- [x] b" in second


class TestFileBudgets:
    def test_over_budget_is_reported(self):
        problems = file_budgets({"content/_recipe_queue.md": "x\n" * 2501})
        assert len(problems) == 1
        assert "content/_recipe_queue.md" in problems[0]
        assert "回転" in problems[0]

    def test_under_budget_is_silent(self):
        assert file_budgets({"content/_recipe_queue.md": "x\n" * 100}) == []

    def test_unknown_file_is_ignored(self):
        assert file_budgets({"content/_unknown.md": "x\n" * 99999}) == []


class TestRotateAll:
    def test_end_to_end_on_a_tmp_tree(self, tmp_path):
        content = tmp_path / "content"
        content.mkdir()
        (content / "_recipe_queue.md").write_text(QUEUE, encoding="utf-8")
        (content / "_topic_ideas.md").write_text(DAILY, encoding="utf-8")
        summary = rotate_all(tmp_path, today=date(2026, 8, 21))
        live = (content / "_recipe_queue.md").read_text(encoding="utf-8")
        archive = (content / "_recipe_queue_archive.md").read_text(encoding="utf-8")
        assert "架空の受信箱14通" not in live
        assert "架空の受信箱14通" in archive
        ideas_archive = (content / "_topic_ideas_archive.md").read_text(encoding="utf-8")
        assert "採用の詳細A" in ideas_archive
        assert summary["content/_recipe_queue.md"] >= 1

    def test_missing_files_are_skipped(self, tmp_path):
        (tmp_path / "content").mkdir()
        summary = rotate_all(tmp_path, today=date(2026, 8, 21))
        assert summary == {}

    def test_nothing_to_do_writes_nothing(self, tmp_path):
        content = tmp_path / "content"
        content.mkdir()
        (content / "_recipe_queue.md").write_text(
            "## 待ち行列\n\n- [ ] 未処理だけ\n  - 詳細\n", encoding="utf-8"
        )
        before = (content / "_recipe_queue.md").stat().st_mtime_ns
        summary = rotate_all(tmp_path, today=date(2026, 8, 21))
        assert summary == {}
        assert not (content / "_recipe_queue_archive.md").exists()
        assert (content / "_recipe_queue.md").stat().st_mtime_ns == before
