# -*- coding: utf-8 -*-
"""문제 은행 빌더.   python3 tools/hl/build.py [--tags hl001,hl002] [--n 90] [--check-only]
types_*.py 에 등록된 생성기를 돌려 검증하고 요약을 출력한다(실제 파일 쓰기는 make_hl.py)."""
import sys, os, json, glob, random, importlib, re, argparse, collections, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hllib
from hllib import REGISTRY, render, pts_for, sig, plain
from outline import TYPES, BYTAG, SUBS

LVI = {'하': 0, '중': 1, '상': 2, '최': 3}


def load_types():
    for f in sorted(glob.glob(os.path.join(HERE, 'types_*.py'))):
        importlib.import_module(os.path.basename(f)[:-3])


def validate(tag, it):
    bad = []
    if len(it.opts) != 5: bad.append('선택지 5개 아님')
    if len({re.sub(r'\s+', '', plain(o)) for o in it.opts}) != 5: bad.append('선택지 중복')
    if not (1 <= it.ans <= 5): bad.append('정답 번호')
    txt = it.body + ''.join(it.opts) + ''.join(it.steps)
    for w in ('None', 'nan', '{', '}', '%s', '%d', 'Traceback', '[object', 'undefined', '??'):
        if w in txt: bad.append('이상한 문자열 ' + w)
    if it.lv not in LVI: bad.append('난이도')
    if not it.steps: bad.append('풀이 없음')
    if len(plain(it.body)) < 8: bad.append('본문 너무 짧음')
    if it.body.count('<u>') != it.body.count('</u>'): bad.append('u 태그')
    return bad


def gen_tag(tag, n, maxtry_mult=60, seed_extra='', exclude=None):
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
        q, e = render(it, tag, no, code, pts_for(it.lv, it._r))
        out.append({'code': code, 'no': no, 'set': 'bank', 'sub': ty['sub'], 'subname': ty['subname'], 'type': ty['label'],
                    'ans': str(it.ans), 'lv': it.lv, 'fam': tag + it.fam, 'q': q, 'exp': e})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tags', default='')
    ap.add_argument('--n', type=int, default=0)
    a = ap.parse_args()
    load_types()
    tags = [t for t in a.tags.split(',') if t] or [t['tag'] for t in TYPES if t['tag'] in REGISTRY]
    tot = 0
    ans = collections.Counter(); lvs = collections.Counter()
    for tag in tags:
        n = a.n or BYTAG[tag]['n']
        items, errs = gen_tag(tag, n)
        if items is None:
            print(tag, 'SKIP', errs); continue
        lv = collections.Counter(i.lv for i in items)
        ans.update(i.ans for i in items); lvs.update(lv)
        flag = '' if len(items) >= n else '  <<< 부족'
        print('%s %-34s %3d/%d  하%d 중%d 상%d 최%d  %s%s' % (tag, BYTAG[tag]['base'][:32], len(items), n, lv['하'], lv['중'], lv['상'], lv['최'], dict(errs.most_common(3)) if errs else '', flag))
        tot += len(items)
    print('total', tot, dict(lvs), 'ans', sorted(ans.items()))

if __name__ == '__main__':
    main()
