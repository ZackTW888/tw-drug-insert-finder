"""從食藥署開放資料下載「未註銷藥品許可證資料集」(InfoId 37)，擷取管制藥品分類級別。
輸出 data/controlled.json：{ "generatedAt": ..., "source": ..., "levels": { 許可證字號: "第四級管制藥品", ... }, "summary": {...} }
"""
import io, json, zipfile, datetime, collections, sys, time, urllib.request

URLS = [
    "https://data.fda.gov.tw/data/opendata/export/37/json",
    "https://data.fda.gov.tw/opendata/exportDataList.do?method=ExportData&InfoId=37&logType=3",
]

def fetch(url):
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (tw-drug-insert-finder)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:
            last = e; print(f"retry {i+1}: {e}", file=sys.stderr); time.sleep(20 * (i + 1))
    raise last

def load(raw):
    if raw[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(raw))
        name = next(n for n in z.namelist() if n.lower().endswith(".json"))
        raw = z.read(name)
    return json.loads(raw.decode("utf-8-sig"))

data, used = None, None
for u in URLS:
    try:
        data = load(fetch(u)); used = u; break
    except Exception as e:
        print(f"failed {u}: {e}", file=sys.stderr)
if not data:
    sys.exit("無法下載許可證資料集")
rows = data if isinstance(data, list) else next(v for v in data.values() if isinstance(v, list))
keys = list(rows[0].keys())
print("fields:", keys)
kl = next(k for k in keys if "許可證字號" in k)
kc = next(k for k in keys if "管制藥品" in k)
levels, summary = {}, collections.Counter()
for r in rows:
    v = (r.get(kc) or "").strip()
    if v:
        levels[(r.get(kl) or "").replace(" ", "")] = v
        summary[v] += 1
out = {"generatedAt": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z", "source": used,
       "totalLicenses": len(rows), "summary": dict(summary), "levels": levels}
json.dump(out, open("data/controlled.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(rows), "licenses;", dict(summary))
