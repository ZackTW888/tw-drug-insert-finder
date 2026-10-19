import re
CN = {'一':1,'二':2,'兩':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'十二':12}
def num(s):
    s = s.strip().replace('１','1').replace('２','2').replace('３','3').replace('４','4').replace('６','6').replace('８','8')
    if s.isdigit(): return int(s)
    return CN.get(s)
N = r'(\d{1,2}|[一二兩三四五六七八九]|十二?|[１２３４６８])'
RNG = N + r'\s*(?:[-~～至到或]|\s*~\s*)\s*' + N
def fmt(a, b=None, unit='次', per='每日'):
    if b and b != a: return f'{per} {a}–{b} {unit}'
    return f'{per} {a} {unit}'
PATS = [
    (re.compile(r'(?:每日|一日|每天|一天|1日|１日)[^\d。；;，,、量mg]{0,5}?' + N + r'\s*次\s*(?:或|至|到|~|～|-)\s*' + N + r'\s*次'), lambda m: fmt(num(m.group(1)), num(m.group(2)))),
    (re.compile(r'(?:每|一)(?:日|天)\s*(?:早晚|早、晚)'), lambda m: '每日 2 次'),
    (re.compile(r'(?:每日|一日|每天|一天|1日|１日|日服)\s*[^\d。；;，,、量mg]{0,5}?' + RNG + r'\s*次'), lambda m: fmt(num(m.group(1)), num(m.group(2)))),
    (re.compile(r'(?:每日|一日|每天|一天|1日|１日|日服)\s*[^\d。；;，,、量mg]{0,5}?' + N + r'\s*次'), lambda m: fmt(num(m.group(1)))),
    (re.compile(r'(?:每週|一週|每星期)\s*' + N + r'\s*次'), lambda m: fmt(num(m.group(1)), per='每週')),
    (re.compile(r'每\s*' + RNG + r'\s*(?:個)?小時'), lambda m: f'每 {num(m.group(1))}–{num(m.group(2))} 小時'),
    (re.compile(r'每\s*' + N + r'\s*(?:個)?小時'), lambda m: f'每 {num(m.group(1))} 小時'),
    (re.compile(r'\b(?:q\.?d|once\s+(?:a\s+)?daily|once\s+a\s+day)\b', re.I), lambda m: '每日 1 次'),
    (re.compile(r'\b(?:b\.?i\.?d|twice\s+(?:a\s+)?daily|twice\s+a\s+day)\b', re.I), lambda m: '每日 2 次'),
    (re.compile(r'\b(?:t\.?i\.?d|three\s+times\s+(?:a\s+)?daily|three\s+times\s+a\s+day)\b', re.I), lambda m: '每日 3 次'),
    (re.compile(r'\bq\.?i\.?d\b', re.I), lambda m: '每日 4 次'),
    (re.compile(r'(?:每日|一日|每天|一天)\s*(?:早上|早晨|睡前)?\s*(?:服用|使用)?\s*一次'), lambda m: '每日 1 次'),
]
LIMIT_PRE = re.compile(r'(最多|不可超過|不得超過|不宜超過|勿超過|不超過|最高|上限)\s*$')
LIMIT_POST = re.compile(r'^\s*(內|以內|之內)?\s*[，,]?\s*(不可|不得|不宜|勿|最多|不超過|總量|限)')
def extract_all(text):
    if not text: return []
    t = text.replace('\n', ' ').replace('\r', ' ')
    hits = []
    for pat, f in PATS:
        for m in pat.finditer(t):
            try: v = f(m)
            except Exception: continue
            if not v or 'None' in v: continue
            g = m.group(0)
            if re.search(r'最多|不超過|不可超過|最高|上限', g): continue
            if re.search(r'早晚|早、晚', g) and v.startswith('每日'): v = '每日 2 次'
            if LIMIT_PRE.search(t[max(0, m.start()-8):m.start()]) or LIMIT_POST.search(t[m.end():m.end()+8]): continue
            hits.append((m.start(), -(m.end()-m.start()), v))
    hits.sort()
    out, seen_pos = [], []
    for st, ln, v in hits:
        if any(abs(st - p) < 4 for p in seen_pos): continue  # overlapping alternative of same phrase
        seen_pos.append(st); out.append(v)
    return out
def extract(text):
    vals = extract_all(text)
    if vals: return vals[0]
    if re.search(r'需要時|必要時|疼痛時|不適時|症狀發生時', text or ''): return '需要時使用'
    return ''
def extract2(text):
    """(主要頻次, 是否另有不同頻次)"""
    vals = extract_all(text)
    if vals:
        return vals[0], len(set(vals)) > 1
    return extract(text), False
if __name__ == '__main__':
    for s in ['每次一錠，每日服用3 次，於用餐時','一天3至4次，或需要時服用','每日使用本品2-4次塗敷','每8小時一次','每 4-6 小時服用','每週一次','1 tablet bid','需要時服用','每日早晚各一次','請詳見仿單']:
        print(s,'→',extract(s))
