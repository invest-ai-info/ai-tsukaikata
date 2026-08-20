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
    rotate_daily_log,
    rotate_queue,
)
from check_freshness import earn_research_heartbeat, file_budgets  # noqa: E402

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
