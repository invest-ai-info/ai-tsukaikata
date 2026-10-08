import json

def dump_store():
    d = json.load(open("store_sheet.json", encoding="utf-8"))
    sheet = d["sheet"]
    lines = ["行,A(地域ブロック),B(エリア),C(店舗),D(区分),E(日付),F(金額)"]
    lines.append("1,地域ブロック,エリア,店舗,区分,日付,金額")
    for r in sheet:
        f = "" if r["F"] is None else r["F"]
        lines.append(f'{r["row"]},{r["A"]},{r["B"]},{r["C"]},{r["D"]},{r["E"]},{f}')
    open("store_table.txt", "w", encoding="utf-8").write("\n".join(lines))
    print("store table lines:", len(lines))

def dump_dept():
    d = json.load(open("dept_sheet.json", encoding="utf-8"))
    sheet = d["sheet"]
    lines = ["行,A(事業部),B(部署),C(担当者),D(区分),E(費目),F(金額)"]
    lines.append("1,事業部,部署,担当者,区分,費目,金額")
    for r in sheet:
        f = "" if r["F"] is None else r["F"]
        lines.append(f'{r["row"]},{r["A"]},{r["B"]},{r["C"]},{r["D"]},{r["E"]},{f}')
    open("dept_table.txt", "w", encoding="utf-8").write("\n".join(lines))
    print("dept table lines:", len(lines))

dump_store()
dump_dept()
