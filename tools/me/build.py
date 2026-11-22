"""물질과 에너지 커리큘럼 재구성(해원고 부교재 기준) 빌드.
  python3 tools/me/build.py --stats   # 개수만
  python3 tools/me/build.py           # bank/ 쓰기
"""
import sys, os, json, re, hashlib, collections, importlib
sys.path.insert(0, os.path.dirname(__file__))
import mk, core
from orig_common import ORIG, TYPES, SUBNAME, SET_OF
for mname in ['orig31', 'orig32', 'orig33', 'orig41', 'orig42', 'orig43']:
    importlib.import_module(mname)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BANK = os.path.join(ROOT, 'bank')
GENS = ['g3a', 'g3b', 'g3c', 'g4a', 'g4b', 'g4c']
CAP = 520
PTS = {'하': 2, '중': 3, '상': 3, '최': 4}
RV = {'A1': 1, 'A2': 2, 'A3': 3, 'A4': 3, 'A5': 4, 'B1': 1, 'B2': 2, 'B3': 2, 'B4': 2, 'B5': 5, 'B6': 4, 'C1': 2, 'C2': 4, 'C3': 5, 'C4': 6,
      'D1': 1, 'D2': 2, 'D3': 3, 'D4': 4, 'D5': 4, 'E1': 1, 'E2': 2, 'E3': 2, 'F1': 1, 'F2': 2, 'F3': 3, 'F4': 1, 'F5': 4}
CONCEPT_TITLES = {}   # concept.py가 채운다(섹션 제목)

def tag_of(typ): return 'hw' + typ[0].lower() + typ[1]

def rv_of(typ):
    if not CONCEPT_TITLES:
        import concept
        for x in concept.SECS: CONCEPT_TITLES[(x['sub'], int(x['no']))] = x['title']
    sub = TYPES[typ][0]; no = RV[typ]
    t = CONCEPT_TITLES.get((sub, no), TYPES[typ][1])
    return [(t, f'{sub} {no}')]

def norm_text(h): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)).strip()

def make_q(code, no, item, pts):
    qid = 'bk' + re.sub(r'[^a-z0-9]', '', code.lower())
    body = ''.join(item['body'])
    if item.get('ch'):
        body += mk.choices(item['ch'], item.get('chl'))
    return qid, mk.qhtml(qid, no, pts, body)

def src_text(item):
    if item['hw'] == 'o': return f'해원고 부교재 {SET_OF[TYPES[item["typ"]][0]]} 수준별 평가 {item["ono"]}번 (원본)'
    if item['hw'] == 'v': return f'해원고 부교재 {item["ono"]}번 변형'
    return f'해원고 부교재 {item["ono"]}번 동유형 유사 문항'

def collect():
    out = []
    for o in ORIG:
        it = dict(typ=o['typ'], lv=o['lv'], ono=o['no'], hw='o', body=o['body'], ch=o['ch'], ans=o['ans'], sol=o['sol'], key=o['key'],
                  chl=o['chl'], kind=o['kind'], pts=o['pts'], ansText=o['ansText'], figs=o['figs'])
        out.append(it)
    core.ITEMS.clear()
    for g in GENS:
        try:
            mod = importlib.import_module(g)
        except ModuleNotFoundError:
            continue
        mod.run()
    seen = set(); dup = 0; kept = []
    for it in core.ITEMS:
        h = hashlib.md5((norm_text(''.join(it['body'])) + '|' + '|'.join(it['ch'] or [])).encode()).hexdigest()
        if h in seen: dup += 1; continue
        seen.add(h); it['kind'] = 'mc'; kept.append(it)
    # 유형별 상한: (난이도, 원본 번호) 묶음을 돌아가며 고르게 담는다
    by = collections.defaultdict(list)
    for it in kept: by[it['typ']].append(it)
    for typ, L in by.items():
        g = collections.defaultdict(list)
        for it in L: g[(it['lv'], it['ono'], it['hw'])].append(it)
        qs = list(g.values()); take = []; j = 0
        while len(take) < CAP and any(qs):
            for q in qs:
                if j < len(q) and len(take) < CAP: take.append(q[j])
            j += 1
            if all(j >= len(q) for q in qs): break
        out.extend(take)
    return out, dup

def build(write=True):
    items, dup = collect()
    by_tag = collections.defaultdict(list)
    for it in items:
        tag = tag_of(it['typ']) if it['kind'] == 'mc' else 'hwe' + it['typ'][0].lower() + it['typ'][1]
        by_tag[tag].append(it)
    files = {}; index = {}
    for tag, L in by_tag.items():
        L.sort(key=lambda x: (x['hw'] != 'o', x['ono'] or 0, '하중상최'.index(x['lv'])))
        qs = []
        gen = 1000
        for k, it in enumerate(L, 1):
            if it['hw'] == 'o': no = it['ono']
            else: gen += 1; no = gen
            code = f'G-{tag}-{no:04d}'
            sub = TYPES[it['typ']][0]
            pts = it.get('pts') or PTS[it['lv']]
            qid, qh = make_q(code, k, it, pts)
            ans = it['ans']
            ansText = it.get('ansText')
            if it['kind'] == 'short':
                ansText = mk.fmt(str(ans)); ans_field = str(ans)
            else:
                ans_field = str(ans)
            exp = mk.solhtml(qid, k, code, ans_field if it['kind'] == 'mc' else '', src_text(it), it['sol'], it.get('key', ''), '', rv_of(it['typ']), ansText=ansText)
            q = dict(code=code, no=k, set='bank' if it['kind'] == 'mc' else 'essay', sub=sub, subname=SUBNAME[sub], type=TYPES[it['typ']][1],
                     ans=ans_field if it['kind'] == 'mc' else mk.fmt(str(ans)), lv=it['lv'], fam=f'hw{it["ono"]}', q=qh, exp=exp, hw=it['hw'], ono=it['ono'])
            qs.append(q)
        files[tag] = qs
        lvc = collections.Counter(q['lv'] for q in qs)
        t0 = L[0]['typ']
        index[tag] = dict(lv=dict(lvc), label=TYPES[t0][1], sub=TYPES[t0][0], subname=SUBNAME[TYPES[t0][0]], n=len(qs), hw=1, hwn=sum(1 for q in qs if q['hw'] in ('o', 'v', 's')))
        if tag.startswith('hwe'): index[tag]['set'] = 'essay'
    return files, index, dup, items

if __name__ == '__main__':
    files, index, dup, items = build()
    tot = sum(len(v) for v in files.values())
    c = collections.Counter((i['hw']) for i in items)
    print('총', tot, '문항 (중복 제거', dup, ')', dict(c))
    lvc = collections.Counter(i['lv'] for i in items); print('난이도', dict(lvc))
    for t in sorted(index): print(t, index[t]['label'], index[t]['n'], index[t]['lv'])
    if '--stats' in sys.argv: sys.exit()
    import apply
    apply.write(files, index)
