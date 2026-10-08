import json

def recompute_store():
    d = json.load(open("store_sheet.json", encoding="utf-8"))
    sheet = d["sheet"]
    details = [r for r in sheet if r["target"] is None]
    gt = {}
    for r in sheet:
        if r["target"] == "store":
            gt[r["row"]] = sum(x["F"] for x in details if x["store"] == r["store"])
        elif r["target"] == "area":
            gt[r["row"]] = sum(x["F"] for x in details if x["area"] == r["area"])
        elif r["target"] == "block":
            gt[r["row"]] = sum(x["F"] for x in details if x["block"] == r["block"])
        elif r["target"] == "grand":
            gt[r["row"]] = sum(x["F"] for x in details)
    d["gt"] = gt
    json.dump(d, open("store_sheet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("store grand truth:", gt[sheet[-1]["row"]])

def recompute_dept():
    d = json.load(open("dept_sheet.json", encoding="utf-8"))
    sheet = d["sheet"]
    details = [r for r in sheet if r["target"] is None]
    gt = {}
    for r in sheet:
        if r["target"] == "staff":
            gt[r["row"]] = sum(x["F"] for x in details if x["staff"] == r["staff"])
        elif r["target"] == "dept":
            gt[r["row"]] = sum(x["F"] for x in details if x["dept"] == r["dept"])
        elif r["target"] == "unit":
            gt[r["row"]] = sum(x["F"] for x in details if x["unit"] == r["unit"])
        elif r["target"] == "grand":
            gt[r["row"]] = sum(x["F"] for x in details)
    d["gt"] = gt
    json.dump(d, open("dept_sheet.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("dept grand truth:", gt[sheet[-1]["row"]])

recompute_store()
recompute_dept()
