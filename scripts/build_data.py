"""把上游 drugs_data.json 精簡成網頁用的 drugs.json：用法：python scripts/build_data.py <上游 drugs_data.json> <輸出 drugs.json>"""
import json, sys, re, collections, html, os
sys.path.insert(0, sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(__file__))); import freq
src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding='utf-8'))
P = "https://mcp.fda.gov.tw/insert/"
BOILER = re.compile(r'^(請?(詳見|詳如|詳閱|如|內容詳見)(仿單|說明書)(後使用)?。?|製劑原料。?|)$')
def route(name):
    n = name.upper()
    if re.search(r'透析|DIALY|HEMOFILT|血液過濾', n): return 'dia'
    if re.search(r'注射|輸注|INJ|INFUSION|VIAL', n): return 'inj'
    if re.search(r'眼|耳|鼻|EYE|OPHTH|NASAL|OTIC', n): return 'eent'
    if re.search(r'栓|陰道|SUPP|VAGINAL', n): return 'pr'
    if re.search(r'軟膏|乳膏|凝膠|外用|貼|洗劑|乳液|噴霧|CREAM|OINT|GEL|LOTION|PATCH|SPRAY|TOPICAL', n): return 'top'
    return 'oral'
def release(name):
    return 'er' if re.search(r'持續|緩釋|長效|控釋|延長|延釋|\b(XR|SR|ER|CR|XL|LA|OROS|RETARD|MR|PR)\b', name.upper()) else 'ir'
def ingkey(ing):
    core = re.sub(r'\([^)]*\)', ' ', (ing or '').upper())
    parts = sorted({p.strip() for p in re.split(r';;|;|,', core) if p.strip()})
    return '|'.join(parts)
items = []
U = lambda v: html.unescape(html.unescape(v or '')).strip()
for r in d['data']:
    for k in ('chName','enName','ingredients','indication','usage'): r[k] = U(r.get(k))
    for k in ('chName','enName'):
        if not re.search(r'[0-9A-Za-z\u4e00-\u9fff]', r[k]): r[k] = ''  # 官方登載為「*」等佔位符
    name = r['chName'] + ' ' + r['enName']
    u = r['usage']
    f, multi = freq.extract2(u)
    r['_multi'] = multi
    key = (ingkey(r['ingredients']), route(name), release(name))
    items.append((r, u, f, key))
groups = collections.defaultdict(collections.Counter)
for r, u, f, key in items:
    if f and not r['_multi'] and key[0] and not r['isRawMaterial']: groups[key][f] += 1
rows = []; stat = collections.Counter(); codes = set()
for r, u, f, key in items:
    ins = lab = ""; ex = 0
    for x in [x for y in r['packageLinks'] for x in y.split(';')]:
        if '/exportpdf/' in x: ex = 1; continue
        if not x.startswith(P): continue
        t = x[len(P):]
        if t.startswith('pdfcasefile/') and not ins: ins = t
        elif t.startswith('lablefiles/') and not lab: lab = t
    nhi = []
    for m in r['nhiMatches']:
        c = (m.get('code') or '').strip().upper()
        if c: codes.add(c); nhi.append([c, m.get('price') or '', 1 if m.get('confidence') == 'verified' else 0])
    fsrc = 0; fn = 0
    if f: fsrc = 1
    elif not r['isRawMaterial'] and key[0] and key[1] != 'dia':
        g = groups.get(key)
        if g:
            top, n = g.most_common(1)[0]; tot = sum(g.values())
            if n >= 2 and n / tot >= 0.6: f, fsrc, fn = top, 2, n
    stat[fsrc] += 1
    usage = '' if BOILER.match(u.replace(' ', '')) else u
    rows.append([r['licenseNumber'], r['chName'], r['enName'], '; '.join(dict.fromkeys(p.strip() for p in re.split(r';;|;', r['ingredients'] or '') if p.strip())),
                 ins, lab, nhi, 1 if r['isRawMaterial'] else 0, ex,
                 r['indication'], f, fsrc, fn, usage, 1 if (fsrc == 1 and r['_multi']) else 0])
ver = json.load(open(os.path.join(os.path.dirname(src), 'data_version.json')))
meta = {"generatedAt": ver.get('generatedAt', ''), "licenses": len(rows), "nhiCodes": len(codes)}
json.dump({"meta": meta, "rows": rows}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(meta, 'multi', sum(1 for x in rows if x[14]), 'freq from label', stat[1], 'peer', stat[2], 'none', stat[0])
nh = [x for x in rows if x[6]]; print('NHI drugs with freq', sum(1 for x in nh if x[10]), 'of', len(nh))
