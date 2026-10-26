# -*- coding: utf-8 -*-
"""전 과목 문항 자동 검수.   python3 tools/audit_all.py [--all]
 대상: bank/(물질과 에너지: data.js + 유형 은행) · cm/ · ph/ · hl/ 의 모든 문항 JSON
 검사
  1. 코드 중복(과목 안), 빈 문항
  2. 5지선다: 선택지 개수 · 중복 선택지 · 정답 번호 범위
  3. 해설 머리의 '정답 ○'와 ans 일치
  4. 태그 짝(<u> <b> <sup> <sub> <table> <div>) · 이상한 문자열(None, NaN, undefined, %s …)
  5. 그림 파일(src="…")이 실제로 있는지
"""
import os, re, json, glob, sys, html as H, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
CIR = '①②③④⑤⑥⑦⑧⑨⑩'
SUBJ = {'me': 'bank', 'cm': 'cm', 'ph': 'ph', 'hl': 'hl'}


def plain(h):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[a-zA-Z/!][^>]*>', ' ', h or ''))).strip()


def load(subj):
    d = SUBJ[subj]
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, d, '*.json'))):
        b = os.path.basename(f)
        if b in ('index.json', 'concept.json'):
            continue
        j = json.load(open(f, encoding='utf-8'))
        if isinstance(j, dict):
            j = j.get('items') or []
        for x in j:
            if isinstance(x, dict) and 'code' in x:
                out.append((b, x))
    js = os.path.join(ROOT, d, 'data.js')
    if os.path.exists(js):
        t = open(js, encoding='utf-8').read()
        m = re.search(r'const DATA\s*=\s*(\[.*\])\s*;?', t, re.S)
        if m:
            for x in json.loads(m.group(1)):
                out.append(('data.js', x))
    return out


def chs(q):
    if 'class="chs' not in q:
        return None
    part = q.split('class="chs', 1)[1]
    return [plain(o) for o in re.findall(r'<span>(.*?)</span></div>', part, re.S)]


def tag_bal(h, t):
    return len(re.findall(r'<%s[\s>]' % t, h)) == h.count('</%s>' % t)


def check(subj, src, x):
    e = []
    q, exp = x.get('q') or '', x.get('exp') or ''
    if not plain(q):
        return ['빈 문항']
    st = x.get('set')
    if st in ('mc', 'top', 'bank') or (st not in ('ox', 'blank', 'essay', 'sa') and 'class="chs' in q):
        o = chs(q)
        if o is not None:
            if len(o) != 5: e.append('선택지 %d개' % len(o))
            if len({re.sub(r'\s+', '', t) for t in o}) != len(o): e.append('선택지 중복')
            if any(not t for t in o): e.append('빈 선택지')
            anss = [a for a in re.split(r'[,/ ]+', str(x.get('ans', ''))) if a]
            try:
                nums = [int(a) for a in anss]
            except ValueError:
                nums = []
                e.append('정답 형식 "%s"' % x.get('ans'))
            if nums and any(not 1 <= n <= len(o) for n in nums): e.append('정답 범위 %s' % x.get('ans'))
            m = re.search(r'정답\s*([①②③④⑤](?:\s*,\s*[①②③④⑤])*)', plain(exp)[:120])
            if m and nums:
                got = sorted(CIR.index(c) + 1 for c in re.findall(r'[①②③④⑤]', m.group(1)))
                if got != sorted(nums): e.append('해설 정답 %s ≠ ans %s' % (m.group(1), x.get('ans')))
    for t in ('u', 'b', 'sup', 'sub', 'table', 'div', 'p'):
        if not tag_bal(q, t): e.append('<%s> 짝(문항)' % t)
        if not tag_bal(exp, t): e.append('<%s> 짝(해설)' % t)
    txt = plain(q) + ' ' + plain(exp)
    for w in ('None', 'NaN', 'undefined', '%s', '%d', 'Traceback', '[object', '{{', '}}'):
        if w in txt: e.append('이상한 문자열 ' + w)
    for m in re.finditer(r'(?:src|href)="([^"]+)"', q + exp):
        u = m.group(1)
        if u.startswith(('data:', 'http', '#')): continue
        if not os.path.exists(os.path.join(ROOT, u.split('?')[0])): e.append('그림 없음 ' + u)
    if st in ('mc', 'top', 'bank') and not plain(exp): e.append('해설 없음')
    return e


def main():
    allf = '--all' in sys.argv
    total = 0
    for subj in SUBJ:
        items = load(subj)
        total += len(items)
        bad = collections.OrderedDict()
        seen = collections.defaultdict(list)
        for src, x in items:
            seen[x['code']].append(src)
            e = check(subj, src, x)
            if e: bad.setdefault(x['code'], []).extend(e)
        for c, L in seen.items():
            if len(L) > 1 and len(set(L)) == 1: bad.setdefault(c, []).append('코드 중복 %d회 (%s)' % (len(L), L[0]))
        kinds = collections.Counter(re.sub(r'[ "(].*', '', e) for es in bad.values() for e in es)
        print('== %s: 문항 %d · 문제 있는 문항 %d  %s' % (subj, len(items), len(bad), dict(kinds.most_common(8))))
        for c, es in list(bad.items())[: (10 ** 9 if allf else 12)]:
            print('   ', c, '|', ' ; '.join(es)[:200])
    print('전체 문항', total)


if __name__ == '__main__':
    main()


# ---------------------------------------------------------------- 해설 판정으로 정답 다시 계산
VERD = re.compile(r'(옳지\s*않다|적절하지\s*않다|맞지\s*않다|틀린\s*설명이다|틀리다|틀렸다|옳다|적절하다|맞다)')


def _v(seg):
    seg = re.sub(r'옳은 설명은 ".*?"(이다)?\.?', ' ', seg)  # 고쳐 쓴 문장 안의 낱말은 판정이 아니다
    ms = list(VERD.finditer(seg))
    if not ms: return None
    head = [m for m in ms if m.start() < 14]
    w = (head[0] if head else ms[-1]).group(1).replace(' ', '')
    return not any(k in w for k in ('않', '틀'))


def stem_of(q):
    t = re.sub(r'<div class="(?:psg|bogi)[^"]*".*?</div>', ' ', q.split('class="chs', 1)[0], flags=re.S)
    ps = [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', t, re.S)]
    ps = [x for x in ps if '?' in x] or ps
    return ps[-1] if ps else ''


def recompute(x):
    """해설에서 정답을 다시 계산. 반환: (계산된 정답 집합 또는 None, 근거)"""
    q, exp = x.get('q') or '', plain(x.get('exp') or '')
    o = chs(q)
    if not o or len(o) != 5: return None, ''
    stem = stem_of(q)
    neg = bool(re.search(r'(않은|아닌|틀린|어긋난|없는)\s*(것|설명|사례|예)', stem))
    body = re.split(r'풀이', exp, maxsplit=1)[-1]
    body = re.split(r'핵심 개념|출제 포인트|이 문제를 틀렸다면', body)[0]
    combo = all(re.fullmatch(r'[ㄱㄴㄷㄹ](, [ㄱㄴㄷㄹ])*', t) for t in o)
    if combo:
        segs = dict()
        for m in re.finditer(r'(?:^|\s)([ㄱㄴㄷㄹ])\s*[.:]\s*(.*?)(?=(?:\s[ㄱㄴㄷㄹ]\s*[.:]\s)|$)', body):
            if m.group(1) not in segs: segs[m.group(1)] = _v(m.group(2))
        letters = sorted({c for t in o for c in re.findall('[ㄱㄴㄷㄹ]', t)})
        if any(segs.get(c) is None for c in letters): return None, ''
        pick = [c for c in letters if segs[c] != neg] if re.search(r'모두|있는 대로', stem) else None
        if pick is None: return None, ''
        want = ', '.join(pick)
        idx = [i + 1 for i, t in enumerate(o) if t == want]
        return (set(idx) if idx else {0}), '보기 판정 ' + ''.join('%s%s' % (c, 'O' if segs[c] else 'X') for c in letters)
    segs = {}
    for m in re.finditer(r'([①②③④⑤])\s*(.*?)(?=[①②③④⑤]|$)', body):
        k = CIR.index(m.group(1)) + 1
        if k not in segs: segs[k] = _v(m.group(2))
    if len(segs) < 5 or any(v is None for v in segs.values()): return None, ''
    want = {k for k, v in segs.items() if (not v if neg else v)}
    return want, '선지 판정 ' + ''.join('%d%s' % (k, 'O' if segs[k] else 'X') for k in sorted(segs))


def semantic():
    for subj in SUBJ:
        n = bad = 0
        out = []
        for src, x in load(subj):
            if x.get('set') not in ('mc', 'top', 'bank'): continue
            want, why = recompute(x)
            if want is None: continue
            n += 1
            try:
                ans = {int(a) for a in re.split(r'[,/ ]+', str(x['ans'])) if a}
            except ValueError:
                continue
            if want != ans:
                bad += 1
                out.append('%s ans=%s 해설로 계산=%s (%s) | %s' % (x['code'], x['ans'], sorted(want), why, stem_of(x['q'])[-50:]))
        print('== %s 해설 판정 대조 %d문항 · 불일치 %d' % (subj, n, bad))
        for l in out[:400]: print('   ', l)


if __name__ == '__main__' and '--sem' in sys.argv:
    semantic()
