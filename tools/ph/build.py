# -*- coding: utf-8 -*-
"""문제 은행 빌더.   python3 tools/ph/build.py [--tags ph001,ph002] [--n 90] [--out ph] [--check-only]
types_*.py 에 등록된 생성기를 돌려 ph/phNNN.json 과 ph/index.json 을 만든다."""
import sys, os, json, glob, random, importlib, re, argparse, collections, hashlib
import xml.dom.minidom as minidom
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phlib
from phlib import REGISTRY, render, pts_for, sig, plain
from outline import TYPES, TYPES_ORD, SHIP_TYPES, BYTAG, SUBS

LVI = {'하': 0, '중': 1, '상': 2, '최': 3}

def load_types():
    for f in sorted(glob.glob(os.path.join(HERE, 'types_*.py'))):
        importlib.import_module(os.path.basename(f)[:-3])

def validate(tag, it):
    """Item 이 규칙을 지키는지 검사. 문제 목록을 돌려준다."""
    bad = []
    if len(it.opts) != 5: bad.append('선택지 5개 아님')
    if len({re.sub(r'\s+', '', plain(o)) for o in it.opts}) != 5: bad.append('선택지 중복')
    if not (1 <= it.ans <= 5): bad.append('정답 번호')
    txt = it.body + ''.join(it.opts) + ''.join(it.steps)
    for w in ('None', 'nan', 'inf', '{', '}', '%s', '%d', 'Traceback', '[object', 'undefined'):
        if w in txt: bad.append('이상한 문자열 ' + w)
    for o in it.opts:
        po = plain(o)
        if re.search(r'\d\.\d{4,}', po): bad.append('선택지 소수점 너무 김')
        if re.search(r'(?<![\d.])0\.0\d{3,}', po): bad.append('선택지 너무 작은 값')
    if it.lv not in LVI: bad.append('난이도')
    if not it.steps: bad.append('풀이 없음')
    if len(plain(it.body)) < 12: bad.append('본문 너무 짧음')
    for m in re.finditer(r'<svg.*?</svg>', it.body, flags=re.S):
        try: minidom.parseString(m.group(0))
        except Exception as e: bad.append('SVG 오류 ' + str(e)[:40])
    return bad

def gen_tag(tag, n, maxtry_mult=40, seed_extra='', exclude=None):
    f = REGISTRY.get(tag)
    if f is None: return None, ['생성기 없음']
    seed = int(hashlib.md5((tag + seed_extra).encode()).hexdigest()[:8], 16)
    r = random.Random(seed)
    items, seen, errs = [], set(exclude or ()), collections.Counter()
    k = 0
    while len(items) < n and k < n * maxtry_mult:
        rr = random.Random(r.getrandbits(48))
        k += 1
        try:
            it = f(rr, k)
        except AssertionError as e:
            errs['assert ' + str(e)[:50]] += 1; continue
        if it is None: continue
        bad = validate(tag, it)
        if bad:
            for b in bad: errs[b] += 1
            continue
        s = sig(it)
        if s in seen: errs['중복'] += 1; continue
        seen.add(s); it._r = rr
        items.append(it)
    return items, errs

def to_entries(tag, items):
    ty = BYTAG[tag]
    items = sorted(enumerate(items), key=lambda z: (LVI[z[1].lv], z[0]))
    out = []
    for no, (_, it) in enumerate(items, 1):
        code = 'G-%s-%04d' % (tag, no)
        q, e = render(it, tag, no, code, ty['sub'], pts_for(it.lv, it._r))
        out.append({'code': code, 'no': no, 'set': 'bank', 'sub': ty['sub'], 'subname': ty['subname'], 'type': ty['label'],
                    'ans': str(it.ans), 'lv': it.lv, 'fam': tag + it.fam, 'q': q, 'exp': e})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tags', default='')
    ap.add_argument('--n', type=int, default=90)
    ap.add_argument('--out', default=os.path.join(HERE, '..', '..', 'ph'))
    ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    load_types()
    tags = [t for t in a.tags.split(',') if t] or [t['tag'] for t in TYPES if t['tag'] in REGISTRY]
    os.makedirs(a.out, exist_ok=True)
    idxf = os.path.join(a.out, 'index.json')
    index = {}
    if os.path.exists(idxf) and a.tags:
        index = json.load(open(idxf, encoding='utf-8'))
    tot = 0
    for tag in tags:
        items, errs = gen_tag(tag, a.n)
        if items is None:
            print(tag, 'SKIP', errs); continue
        ent = to_entries(tag, items)
        lv = collections.Counter(e['lv'] for e in ent)
        print('%s %-32s %3d/%d  하%d 중%d 상%d  %s' % (tag, BYTAG[tag]['label'][:30], len(ent), a.n, lv['하'], lv['중'], lv['상'], dict(errs.most_common(3)) if errs else ''))
        tot += len(ent)
        if a.check_only: continue
        json.dump(ent, open(os.path.join(a.out, tag + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        ty = BYTAG[tag]
        index[tag] = {'lv': {k: v for k, v in lv.items()}, 'label': ty['label'], 'sub': ty['sub'], 'subname': ty['subname'], 'n': len(ent)}
    if not a.check_only:
        order = [t['tag'] for t in SHIP_TYPES]
        index = {k: index[k] for k in order if k in index}
        json.dump(index, open(idxf, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('total', tot)

if __name__ == '__main__':
    main()
