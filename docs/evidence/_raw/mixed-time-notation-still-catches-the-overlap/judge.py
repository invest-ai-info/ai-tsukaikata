# -*- coding: utf-8 -*-
"""機械判定スクリプト（文字列照合のみ。正規表現の\\wはUnicode対応で日本語にもマッチして
誤判定を起こすため、ここでは使わず str.find によるスライス抽出だけで判定する）。
docs/evidence/TEMPLATE.md の「判定は機械でやる」「その計測コード自体を1回読み直す」に従う。
"""
import re
from pathlib import Path

HERE = Path(__file__).parent


def read(name: str) -> str:
    text = (HERE / name).read_text(encoding="utf-8")
    # 表形式で「候補」の語を省いて数字だけで行が始まる場合、候補Nを補う
    # (例: "| 1 (11:30-12:00) | 重複なし | ..." -> "|候補1 (11:30-12:00) | ...")
    return re.sub(r"(?m)^\|\s*(\d)(?!\d)", lambda m: f"|候補{m.group(1)}", text)


FREE_WORDS = (
    "重複なし", "重複しない", "重複しません", "重なりません", "重ならない",
    "接するだけ", "接しているだけ", "重複にはなりません", "重複になりません",
    "重複とは扱っていません", "重複と扱っていません", "重複とはみなしません", "重複とみなさない",
)
OVERLAP_WORDS = ("重複", "重なり", "重なって", "重なる", "重なった", "含まれる")


def verdict(slice_text: str) -> str:
    """スライス内で最初に出てくる空き語・重複語のうち、先に出たほうを採用する。"""
    free_pos = min((slice_text.find(w) for w in FREE_WORDS if w in slice_text), default=-1)
    overlap_candidates = [slice_text.find(w) for w in OVERLAP_WORDS if w in slice_text]
    overlap_pos = min(overlap_candidates) if overlap_candidates else -1
    if free_pos == -1 and overlap_pos == -1:
        return "unknown"
    if free_pos == -1:
        return "overlap"
    if overlap_pos == -1:
        return "free"
    return "free" if free_pos <= overlap_pos else "overlap"


def last_decisive(text: str, marker: str):
    """markerの全出現箇所(同じ行の範囲だけ)を順に見て、判定語を含む(unknownでない)
    直近の行と判定を返す。自己訂正があれば、後に出てくる判定で上書きされる。
    表形式は1行=1候補、箇条書きも1行(1ブロック)=1候補なので、行単位で十分。
    """
    best_slice, best_verdict = "", "unknown"
    start = 0
    while True:
        idx = text.find(marker, start)
        if idx == -1:
            break
        line_start = text.rfind("\n", 0, idx) + 1
        line_end = text.find("\n", idx)
        if line_end == -1:
            line_end = len(text)
        s = text[line_start:line_end]
        v = verdict(s)
        if v != "unknown":
            best_slice, best_verdict = s, v
        start = idx + 1
    return best_slice, best_verdict


def check_material(name: str, free_ids, overlap_pairs, client_names) -> dict:
    """overlap_pairs: {候補番号: (必須で現れるべきクライアント名のタプル)}"""
    text = read(name)
    result = {"file": name}
    ok = True
    for n in free_ids:
        _, v = last_decisive(text, f"候補{n}")
        result[f"候補{n}"] = v
        ok = ok and v == "free"
    for n, clients in overlap_pairs.items():
        s, v = last_decisive(text, f"候補{n}")
        has_all_clients = all(c in s for c in clients)
        result[f"候補{n}"] = (v, "clients_ok" if has_all_clients else f"missing one of {clients}")
        ok = ok and v == "overlap" and has_all_clients
    result["has_correction"] = "訂正" in text
    result["ok"] = ok
    return result


def check_generative(name: str) -> dict:
    """番号付き太字の提案(1. **HH:MM-HH:MM**)だけを提案スロットとして抽出し、
    G/H/I(12-13,15-16,17-18)と重ならないかをPythonの時刻計算で確認する。
    """
    import re

    text = read(name)
    busy = [(720, 780), (900, 960), (1020, 1080)]
    pat = re.compile(r"^\s*\d+\.\s+\*\*(\d{1,2})[:：](\d{2})[–\-〜](\d{1,2})[:：](\d{2})\*\*", re.MULTILINE)
    slots = []
    for h1, m1, h2, m2 in pat.findall(text):
        slots.append((int(h1) * 60 + int(m1), int(h2) * 60 + int(m2)))
    bad = [(s, e) for s, e in slots for bs, be in busy if s < be and e > bs]
    return {"file": name, "slots": slots, "bad": bad, "ok": len(slots) >= 3 and not bad}


def main():
    print("## material1（日常的な表記ゆれ＋境界またぎ） D9:00-9:30/E11:00-12:00/F12:00-13:00")
    print("   正解: 空き={1,2,5} / 重複={3:Eのみ, 4:E・F両方}")
    hits = 0
    for i in range(1, 6):
        r = check_material(f"m1_trial{i}.txt", {1, 2, 5}, {3: ("E",), 4: ("E", "F")}, ["D", "E", "F"])
        print(r)
        hits += r["ok"]
    print(f"=> {hits}/5 正解\n")

    print("## material2（文脈依存のあいまいな裸の時刻） G12:00-13:00/H15:00-16:00/I17:00-18:00")
    print("   正解: 空き={1,2,4} / 重複={3:Hのみ, 5:Iのみ}")
    hits, corrections = 0, 0
    for i in range(1, 6):
        r = check_material(f"m2_trial{i}.txt", {1, 2, 4}, {3: ("H",), 5: ("I",)}, ["G", "H", "I"])
        print(r)
        hits += r["ok"]
        corrections += r["has_correction"]
    print(f"=> {hits}/5 正解、途中で「訂正」した回={corrections}/5\n")

    print("## material2_fix（先に24時間表記へ変換させる指示を追加） 同じ正解")
    hits, corrections = 0, 0
    for i in range(1, 6):
        r = check_material(f"m2fix_trial{i}.txt", {1, 2, 4}, {3: ("H",), 5: ("I",)}, ["G", "H", "I"])
        print(r)
        hits += r["ok"]
        corrections += r["has_correction"]
    print(f"=> {hits}/5 正解、途中で「訂正」した回={corrections}/5\n")

    print("## material1_addendum（表記の違う新クライアントを追記） D/E/F + 追記G13:00-13:20")
    print("   正解: 空き={1,2} / 重複={3:Eのみ, 4:E・F両方, 5:Gのみ(Fとは重複しない)}")
    hits = 0
    for i in range(1, 4):
        r = check_material(
            f"m1add_trial{i}.txt", {1, 2}, {3: ("E",), 4: ("E", "F"), 5: ("G",)}, ["D", "E", "F", "G"]
        )
        # 候補5がFとも重複と書いていないか(Fの直後30文字に空き語があるかを確認)
        text = read(f"m1add_trial{i}.txt")
        s5, _ = last_decisive(text, "候補5")
        f_idx = s5.rfind("F")
        f_context = s5[f_idx:] if f_idx != -1 else ""
        f_says_no_overlap = (f_idx == -1) or any(w in f_context for w in FREE_WORDS)
        r["候補5のF近傍"] = f_context
        print(r)
        hits += r["ok"] and f_says_no_overlap
    print(f"=> {hits}/3 正解\n")

    print("## material2_generative（候補を渡さず提案させる） G/H/Iと重ならない1時間提案3件")
    hits = 0
    for i in range(1, 4):
        r = check_generative(f"m2gen_trial{i}.txt")
        print(r)
        hits += r["ok"]
    print(f"=> {hits}/3 正解")


if __name__ == "__main__":
    main()
