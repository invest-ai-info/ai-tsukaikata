import re, pathlib

HERE = pathlib.Path(__file__).parent

# target account/label per material, and the correct count (0)
TARGET = {
    "matA": "pottery_studio_tsuchi",
    "matB": "LINE公式アカウント",
}

CONDS = ["A_bullet_noprio", "B_bullet_prio", "C_charlimit_noprio", "D_charlimit_prio"]
MATS = ["matA", "matB"]
REPS = [1, 2]

DIGIT_KEN_RE = re.compile(r"(\d+)件")

# 🚨 台帳12番の再発その2＝最後の『N件』を取る版も誤爆した。
# 「以下のどちらの前提で集計すればよいかお知らせいただけますか」のような
# 確認・質問だけで終わる回は、本文の中に選択肢の説明として「0件」という
# 文字列が出てくるため、最後のN件を機械的に拾うと「0件で正解」に見えてしまう。
# 実際は数字を1つも確定して出していない＝不正解でも正解でもない「確認」。
# これを拾うため、質問・確認のサインを先に見る。
STALL_SIGNS = (
    "教えていただけますか", "お知らせいただけますか", "確認させてください",
    "どちらで処理すればよいか", "どちらの前提で", "いずれで処理",
)


def classify(text: str, target: str) -> str:
    """『正解』『不正解』『確認（未回答）』の3値を返す。

    ⚠️ 対象名の直後をそのまま探すと誤爆する。実測で発覚＝
    「記録が1件も存在しないため0件です」のような否定文では、本当の答え
    （0件）の手前に、否定の対象として「1件」という数字が先に出てくる。
    対象名の直後にある最初の『N件』を取ると、この「1件」を拾ってしまう
    （台帳12番＝計測スクリプトのほうを先に疑う、の実例）。
    この記事の指示文はどの版も「新しく追加した対象を必ず最後に報告する」
    構造なので、本文全体で最後に出てくる『N件』が新規対象の答えになるが、
    確認・質問で終わる回はその『最後のN件』が選択肢の説明の中の数字でしかない。
    """
    if any(sign in text for sign in STALL_SIGNS):
        return "確認"
    if target not in text:
        return "不正解"
    matches = DIGIT_KEN_RE.findall(text)
    if not matches:
        return "不正解"
    return "正解" if matches[-1] == "0" else "不正解"


for cond in CONDS:
    tally = {"正解": 0, "不正解": 0, "確認": 0}
    rows = []
    for mat in MATS:
        for rep in REPS:
            name = f"{cond}-{mat}-{rep}"
            text = (HERE / f"{name}.out.txt").read_text(encoding="utf-8")
            target = TARGET[mat]
            verdict = classify(text, target)
            tally[verdict] += 1
            chars = len(text)
            has_bullet = bool(re.search(r"^[-・]", text, re.M))
            rows.append(f"  {name}: 判定={verdict}  文字数={chars}  先頭が-/・={has_bullet}")
    print(f"{cond}: 正解{tally['正解']}/4  確認{tally['確認']}/4  不正解{tally['不正解']}/4")
    for r in rows:
        print(r)
    print()

print("--- 言い直し後（日付の念押しあり・材料Aのみ各4回） ---")
for cond in ["E_bullet_prio_datefix", "F_charlimit_prio_datefix"]:
    tally = {"正解": 0, "不正解": 0, "確認": 0}
    rows = []
    for rep in [1, 2, 3, 4]:
        name = f"{cond}-matA-{rep}"
        text = (HERE / f"{name}.out.txt").read_text(encoding="utf-8")
        verdict = classify(text, "pottery_studio_tsuchi")
        tally[verdict] += 1
        rows.append(f"  {name}: 判定={verdict}  文字数={len(text)}")
    print(f"{cond}: 正解{tally['正解']}/4  確認{tally['確認']}/4  不正解{tally['不正解']}/4")
    for r in rows:
        print(r)
    print()
