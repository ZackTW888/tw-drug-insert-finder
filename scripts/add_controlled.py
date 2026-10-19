"""把 data/controlled.json 的管制藥品分級併入 drugs.json（每筆第 16 欄：1–4 級，0 = 非管制或已取消管制）。"""
import json, os
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
src = os.path.join(root, "drugs.json")
ctl = json.load(open(os.path.join(root, "data", "controlled.json"), encoding="utf-8"))
NUM = {"第一級管制藥品": 1, "第二級管制藥品": 2, "第三級管制藥品": 3, "第四級管制藥品": 4}
d = json.load(open(src, encoding="utf-8"))
n = 0
for r in d["rows"]:
    lv = NUM.get(ctl["levels"].get(r[0].replace(" ", ""), ""), 0)
    r[15:] = [lv]; n += bool(lv)
d["meta"]["controlledAt"] = ctl["generatedAt"]; d["meta"]["controlled"] = n
json.dump(d, open(src, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("controlled licenses tagged:", n)
