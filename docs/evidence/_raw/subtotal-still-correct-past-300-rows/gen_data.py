import csv, random, json

random.seed(2026)

def make_store_table():
    # 東日本: 関東のみ(10店) / 西日本: 関西・中部・九州(各10店)
    blocks = {
        "東日本": ["関東"],
        "西日本": ["関西", "中部", "九州"],
    }
    rows = []  # each: dict(type, block, area, store, date, amount)
    for block, areas in blocks.items():
        for area in areas:
            for s in range(1, 11):
                store = f"{area}{s:02d}店"
                for d in range(1, 8):
                    amt = random.randint(30, 95) * 1000
                    rows.append(dict(kind="detail", block=block, area=area, store=store,
                                      date=f"10/{d:02d}", amount=amt))
                rows.append(dict(kind="store_sub", block=block, area=area, store=store,
                                  date="", amount=None))
            rows.append(dict(kind="area_sub", block=block, area=area, store="", date="", amount=None))
        rows.append(dict(kind="block_sub", block=block, area="", store="", date="", amount=None))
    rows.append(dict(kind="grand", block="", area="", store="", date="", amount=None))
    return rows

def make_dept_table():
    units = {
        "フロント事業部": ["営業部"],
        "バックオフィス事業部": ["総務部", "人事部", "経理部"],
    }
    cats = ["消耗品費", "交通費", "会議費", "通信費", "研修費"]
    rows = []
    for unit, depts in units.items():
        for dept in depts:
            for s in range(1, 16):
                staff = f"{dept}担当{s:02d}"
                for cat in cats:
                    amt = random.randint(3, 40) * 1000
                    rows.append(dict(kind="detail", unit=unit, dept=dept, staff=staff,
                                      cat=cat, amount=amt))
                rows.append(dict(kind="staff_sub", unit=unit, dept=dept, staff=staff, cat="", amount=None))
            rows.append(dict(kind="dept_sub", unit=unit, dept=dept, staff="", cat="", amount=None))
        rows.append(dict(kind="unit_sub", unit=unit, dept="", staff="", cat="", amount=None))
    rows.append(dict(kind="grand", unit="", dept="", staff="", cat="", amount=None))
    return rows

store_rows = make_store_table()
dept_rows = make_dept_table()
print("store rows:", len(store_rows), "dept rows:", len(dept_rows))

with open("store_rows.json", "w", encoding="utf-8") as f:
    json.dump(store_rows, f, ensure_ascii=False, indent=1)
with open("dept_rows.json", "w", encoding="utf-8") as f:
    json.dump(dept_rows, f, ensure_ascii=False, indent=1)
