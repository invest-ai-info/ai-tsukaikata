"""待ち行列を30日・90日ぶんまで伸ばして生成する。仕込みを検算する。

前作（fresh-easy-row-throws-off-the-stuck-count）が実測したのは10日まで。
その記事自身が「資料が永久に届かない行が、1か月・3か月でどこまで積み上がるかは
測っていません」と明記している。この生成は、前作で10日間・0%の行方不明／印の
破損が実証された「毎日1件ずつ処理し、処理できない行は資料なしのまま残る」という
前提を、同じ到着パターン（3日に1回・資料なし）でそのまま30日・90日へ機械的に
延長したもの。連鎖実行（claude CLIを1日ずつ繋ぐ）を90回繰り返すのは、本調査の主題
（週次カウントの精度が規模とともにどうなるか）には必須ではないため行っていない。
行う実際のclaude CLI呼び出しは、この生成済みの状態に対する「週次カウント」の
質問そのものに対して行う（run.pyで新規セッション×複数回）。
"""

BASELINE_DONE = [
    ("山田", "見積書を送付した", "見積書 No.1203 送付済み"),
    ("高橋", "資料を転送した", "カタログPDF 転送済み"),
    ("伊藤", "日程を確認して返信した", "来週水曜14時で確定"),
    ("渡辺", "請求書の宛名を直して送った", "宛名を「株式会社渡辺商会」に修正して送付済み"),
]
BASELINE_HELD = [
    ("中村", "見積りの再提示を待っている（前回から保留）", "先方の予算確認待ち（返信待ち）"),
    ("田中", "担当者が不在のため保留（前回から保留）", "担当者は来週月曜に戻る予定（返信待ち）"),
]
# 元は未処理だったが、base期間内に処理済みになった想定の3行
BASELINE_RESOLVED = [
    ("加藤", "見積りの有効期限を教えてほしいとの問い合わせ", "有効期限は2026年11月30日"),
    ("吉田", "契約書の第3条について確認したいとの問い合わせ", "第3条「損害賠償は上限100万円」"),
    ("松本", "返品の手続き方法を教えてほしいとの問い合わせ", "返品は到着後7日以内・着払い"),
]
# 元から資料が無く、以後も永久に処理不能
BASELINE_STUCK = ("山本", "注文番号A-204の納期を教えてほしいとの問い合わせ")

NO_MATERIAL = "（取得できませんでした）"

# 到着内容のローテーション用テンプレート（名前は到着順に自動生成）
TOPICS = [
    "注文番号の在庫状況を教えてほしいとの問い合わせ",
    "配送予定日を教えてほしいとの問い合わせ",
    "請求書の宛名を直してほしいとの依頼",
    "支払い方法を教えてほしいとの問い合わせ",
    "見積りの有効期限を教えてほしいとの問い合わせ",
    "契約条項について確認したいとの問い合わせ",
    "返品の手続き方法を教えてほしいとの問い合わせ",
    "次回発注の割引有無を教えてほしいとの問い合わせ",
    "担当者の名前を教えてほしいとの問い合わせ",
    "消費税の扱いを教えてほしいとの問い合わせ",
]
ANSWERS = [
    "在庫は3点・次回入荷は来月上旬",
    "通常3〜5営業日",
    "正しい宛名は「株式会社フジタ商事」",
    "銀行振込・クレジットカードに対応",
    "有効期限は申し込みから60日間",
    "第4条「解約は30日前通知」",
    "返品は到着後7日以内・着払い",
    "次回発注5%割引キャンペーン中",
    "担当は営業3課 鈴木",
    "消費税別表記・税率10%",
]
# 姓の使い回しを避けるための50音プール（苗字が重複しても実害はないが読みやすさのため）
SURNAMES = [
    "佐藤", "鈴木", "高木", "小林", "斎藤", "清水", "森田", "橋本", "石井", "前田",
    "藤田", "岡田", "長谷川", "村上", "井上", "木村", "林", "山口", "池田", "橋口",
    "松田", "大野", "福田", "原田", "武田", "青木", "西村", "坂本", "遠藤", "近藤",
    "中島", "増田", "小川", "宮本", "三浦", "平野", "今井", "久保", "横山", "菅原",
    "酒井", "工藤", "太田", "岩崎", "北村", "荒木", "安藤", "望月", "新井", "柴田",
    "野田", "岸本", "加納", "上田", "八木", "川口", "中川", "金子", "服部", "本田",
    "須藤", "稲葉", "水野", "高野", "吉川", "大塚", "東", "西岡", "南", "北川",
    "内田", "外山", "宇野", "深田", "浅野", "柏木", "黒田", "白石", "赤松", "緑川",
    "飯田", "米田", "麦田", "豆田", "塩田", "砂田", "石田", "岩田", "山田二", "川田",
]


def row_text(name: str, topic: str, material: str, mark: str) -> str:
    return f"- {mark} {name}様：{topic}\n  資料: {material}"


def build_state(n_days: int) -> tuple[str, dict]:
    """n_days日分の到着を混ぜた最終状態を作る。

    ルール:
      - 3日に1回（day % 3 == 0）＝資料なし＝永久に処理不能（スタック行）
      - 残りの到着（資料あり）のうち、4件に1件は「まだ未着手」のまま
        積み残る（到着が処理より速い、よくある現実の想定）。残りは処理済み。
      - 未着手判定は資料ありの到着を古い順に数えて index % 4 == 0 (1始まり) で決める。
    """
    lines = []
    for name, topic, material in BASELINE_DONE:
        lines.append(row_text(name, topic, material, "[x]"))
    for name, topic, material in BASELINE_HELD:
        lines.append(row_text(name, topic, material, "[!]"))
    for name, topic, material in BASELINE_RESOLVED:
        lines.append(row_text(name, topic, material, "[x]"))
    lines.append(row_text(BASELINE_STUCK[0], BASELINE_STUCK[1], NO_MATERIAL, "[!]"))

    stuck_count = 1
    pending_count = 0
    done_count = len(BASELINE_DONE) + len(BASELINE_RESOLVED)
    held_count = len(BASELINE_HELD)

    resolvable_seen = 0
    for day in range(1, n_days + 1):
        name = SURNAMES[(day - 1) % len(SURNAMES)]
        topic = TOPICS[(day - 1) % len(TOPICS)]
        if day % 3 == 0:
            lines.append(row_text(name, topic, NO_MATERIAL, "[!]"))
            stuck_count += 1
        else:
            resolvable_seen += 1
            answer = ANSWERS[(day - 1) % len(ANSWERS)]
            if resolvable_seen % 4 == 0:
                lines.append(row_text(name, topic, answer, "[ ]"))
                pending_count += 1
            else:
                lines.append(row_text(name, topic, answer, "[x]"))
                done_count += 1

    text = "\n".join(lines)
    # 機械で真値を数え直す（★24＝走らせる前に仕込みをコードで確認する）
    counted_stuck = text.count(NO_MATERIAL)
    assert counted_stuck == stuck_count, f"stuck mismatch: {counted_stuck} != {stuck_count}"

    info = {
        "n_days": n_days,
        "stuck": stuck_count,
        "pending_resolvable": pending_count,
        "done": done_count,
        "held": held_count,
        "total_rows": text.count("\n- ["),
    }
    return text, info


def adjacency_report(text: str) -> dict:
    """スタック行（資料なし）の直前・直後が「未着手だが資料あり」の行である
    組数を数える（前作で起きた巻き込みと同じ隣接条件）。"""
    # 資料行を使って判定する（行の次の行が「  資料: ...」）
    full_lines = text.splitlines()
    pairs = []
    for i, l in enumerate(full_lines):
        if l.startswith("- ["):
            mat_line = full_lines[i + 1] if i + 1 < len(full_lines) else ""
            is_stuck = NO_MATERIAL in mat_line
            pairs.append((l, is_stuck))
    adjacent_traps = 0
    trap_rows = []
    for i, (l, is_stuck) in enumerate(pairs):
        if not is_stuck and l.startswith("- [ ]"):
            prev_stuck = i > 0 and pairs[i - 1][1]
            next_stuck = i < len(pairs) - 1 and pairs[i + 1][1]
            if prev_stuck or next_stuck:
                adjacent_traps += 1
                trap_rows.append(l.strip())
    return {"adjacent_traps": adjacent_traps, "trap_rows": trap_rows}


def main() -> None:
    for n in (30, 90):
        text, info = build_state(n)
        adj = adjacency_report(text)
        print(f"--- {n}日 ---")
        print(info)
        print(f"隣接トラップ（資料あり未着手行がスタック行の隣）: {adj['adjacent_traps']}件")
        for r in adj["trap_rows"]:
            print("   ", r)
        with open(f"out/state_day{n:02d}.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print()


if __name__ == "__main__":
    main()
