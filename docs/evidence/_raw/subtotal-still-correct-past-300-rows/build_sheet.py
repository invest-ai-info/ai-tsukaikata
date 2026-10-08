import json

def load(name):
    with open(name, encoding="utf-8") as f:
        return json.load(f)

def build_store_sheet(rows):
    # columns: A 地域ブロック, B エリア, C 店舗, D 区分, E 日付, F 金額
    sheet = []  # list of dict(row=int, A,B,C,D,E,F, formula_target=None/'store'/'area'/'block'/'grand')
    r = 2
    for row in rows:
        if row["kind"] == "detail":
            sheet.append(dict(row=r, A=row["block"], B=row["area"], C=row["store"],
                               D="売上", E=row["date"], F=row["amount"], target=None,
                               store=row["store"], area=row["area"], block=row["block"]))
        elif row["kind"] == "store_sub":
            sheet.append(dict(row=r, A=row["block"], B=row["area"], C=row["store"],
                               D=f'{row["store"]}小計', E="", F=None, target="store",
                               store=row["store"], area=row["area"], block=row["block"]))
        elif row["kind"] == "area_sub":
            sheet.append(dict(row=r, A=row["block"], B=row["area"], C="",
                               D=f'{row["area"]}中計', E="", F=None, target="area",
                               store=None, area=row["area"], block=row["block"]))
        elif row["kind"] == "block_sub":
            sheet.append(dict(row=r, A=row["block"], B="", C="",
                               D=f'{row["block"]}大計', E="", F=None, target="block",
                               store=None, area=None, block=row["block"]))
        elif row["kind"] == "grand":
            sheet.append(dict(row=r, A="", B="", C="", D="総合計", E="", F=None, target="grand",
                               store=None, area=None, block=None))
        r += 1
    return sheet

def build_dept_sheet(rows):
    # columns: A 事業部, B 部署, C 担当者, D 区分, E 費目, F 金額
    sheet = []
    r = 2
    for row in rows:
        if row["kind"] == "detail":
            sheet.append(dict(row=r, A=row["unit"], B=row["dept"], C=row["staff"],
                               D="経費", E=row["cat"], F=row["amount"], target=None,
                               staff=row["staff"], dept=row["dept"], unit=row["unit"]))
        elif row["kind"] == "staff_sub":
            sheet.append(dict(row=r, A=row["unit"], B=row["dept"], C=row["staff"],
                               D=f'{row["staff"]}小計', E="", F=None, target="staff",
                               staff=row["staff"], dept=row["dept"], unit=row["unit"]))
        elif row["kind"] == "dept_sub":
            sheet.append(dict(row=r, A=row["unit"], B=row["dept"], C="",
                               D=f'{row["dept"]}中計', E="", F=None, target="dept",
                               staff=None, dept=row["dept"], unit=row["unit"]))
        elif row["kind"] == "unit_sub":
            sheet.append(dict(row=r, A=row["unit"], B="", C="",
                               D=f'{row["unit"]}大計', E="", F=None, target="unit",
                               staff=None, dept=None, unit=row["unit"]))
        elif row["kind"] == "grand":
            sheet.append(dict(row=r, A="", B="", C="", D="総合計", E="", F=None, target="grand",
                               staff=None, dept=None, unit=None))
        r += 1
    return sheet

def ground_truth_store(sheet):
    gt = {}
    cur_store_sum = 0
    cur_area_sum = 0
    cur_block_sum = 0
    for rec in sheet:
        if rec["target"] is None:
            cur_store_sum += rec["F"]
        elif rec["target"] == "store":
            gt[rec["row"]] = cur_store_sum
            cur_area_sum += cur_store_sum
            cur_store_sum = 0
        elif rec["target"] == "area":
            gt[rec["row"]] = cur_area_sum
            cur_block_sum += cur_area_sum
            cur_area_sum = 0
        elif rec["target"] == "block":
            gt[rec["row"]] = cur_block_sum
            # accumulate into grand
        elif rec["target"] == "grand":
            gt[rec["row"]] = sum(v for k, v in gt.items() if any(
                s["row"] == k and s["target"] == "block" for s in sheet))
    return gt

def ground_truth_dept(sheet):
    gt = {}
    cur_staff_sum = 0
    cur_dept_sum = 0
    cur_unit_sum = 0
    for rec in sheet:
        if rec["target"] is None:
            cur_staff_sum += rec["F"]
        elif rec["target"] == "staff":
            gt[rec["row"]] = cur_staff_sum
            cur_dept_sum += cur_staff_sum
            cur_staff_sum = 0
        elif rec["target"] == "dept":
            gt[rec["row"]] = cur_dept_sum
            cur_unit_sum += cur_dept_sum
            cur_dept_sum = 0
        elif rec["target"] == "unit":
            gt[rec["row"]] = cur_unit_sum
        elif rec["target"] == "grand":
            gt[rec["row"]] = sum(v for k, v in gt.items() if any(
                s["row"] == k and s["target"] == "unit" for s in sheet))
    return gt

store_rows = load("store_rows.json")
dept_rows = load("dept_rows.json")
store_sheet = build_store_sheet(store_rows)
dept_sheet = build_dept_sheet(dept_rows)
store_gt = ground_truth_store(store_sheet)
dept_gt = ground_truth_dept(dept_sheet)

with open("store_sheet.json", "w", encoding="utf-8") as f:
    json.dump(dict(sheet=store_sheet, gt=store_gt), f, ensure_ascii=False, indent=1)
with open("dept_sheet.json", "w", encoding="utf-8") as f:
    json.dump(dict(sheet=dept_sheet, gt=dept_gt), f, ensure_ascii=False, indent=1)

print("store last row", store_sheet[-1]["row"], "grand=", store_gt[store_sheet[-1]["row"]])
print("dept last row", dept_sheet[-1]["row"], "grand=", dept_gt[dept_sheet[-1]["row"]])
print("store targets count:", sum(1 for r in store_sheet if r["target"]))
print("dept targets count:", sum(1 for r in dept_sheet if r["target"]))
