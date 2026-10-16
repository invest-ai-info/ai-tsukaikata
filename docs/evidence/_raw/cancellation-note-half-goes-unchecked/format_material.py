# -*- coding: utf-8 -*-
from gen import MATERIAL_A, MATERIAL_B


def render(material):
    lines = []
    lines.append(f"【{material['name']}：請求一覧】")
    lines.append("社名 / 基本月額 / 備考 / 今月の入金額")
    for name, base, memo, confirmed, paid in material["clients"]:
        memo_disp = memo if memo else "（なし）"
        lines.append(f"{name} / {base:,}円 / {memo_disp} / {paid:,}円")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "A"
    mat = MATERIAL_A if which == "A" else MATERIAL_B
    print(render(mat))
