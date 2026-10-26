# -*- coding: utf-8 -*-
"""hl/ 문항 자동 검수.   python3 tools/hl/audit.py [--bank] [--all]
 - data.json(교재 문항)을 기본으로, --bank 를 주면 hl/hlNNN.json(문제 은행)도 훑는다.
 검사 항목
  1. 구조: 선택지 5개 · 서로 다름 · 정답 번호 · 풀이 있음 · 태그 짝 · 이상한 문자열
  2. 정답-해설 판정: 풀이가 ① ~ ⑤ 로 시작하는 문항은 발문의 방향(옳은/옳지 않은)과 정답 번호가 풀이의 판정과 맞는지
  3. 조사·표기: 풀려 있지 않은 '이(가)' 표기, 겹조사, 빈 괄호, 같은 말 반복
  4. 코드: 코드 중복, 지문(grp) 묶음에 지문이 있는지, 같은 묶음의 문항이 모두 같은 지문을 쓰는지
"""
import sys, os, re, json, glob, html as H, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CIR = '①②③④⑤'


def plain(h):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(h))).strip()


def parse(q):
    m = re.search(r'<div class="chs[^"]*">(.*)</div></div>\s*$', q, re.S) or re.search(r'<div class="chs[^"]*">(.*)', q, re.S)
    opts = [plain(o) for o in re.findall(r'<span>(.*?)</span></div>', q.split('class="chs', 1)[1])] if 'class="chs' in q else []
    stem_html = q.split('class="chs', 1)[0]
    return stem_html, opts


NEG = re.compile(r'(않은|않는|아닌|틀린|어긋난|없는|못한|부적절|알 수 없|확인할 수 없|보기 어려운|볼 수 없)')
POS_STEP = re.compile(r'(적절하다|옳다|맞다|알맞다|타당하다|일치한다)')
NEG_STEP = re.compile(r'(적절하지 않|옳지 않|맞지 않|알맞지 않|타당하지 않|일치하지 않|어긋|아니다|않다\.|않는다\.|틀리다|잘못)')


def _drop_divs(h, classes):
    """class 가 classes 로 시작하는 div 를 안쪽 div 까지 짝을 맞춰 지운다"""
    out, i = [], 0
    pat = re.compile(r'<div class="(?:%s)' % '|'.join(classes))
    while True:
        m = pat.search(h, i)
        if not m:
            out.append(h[i:]); return ' '.join(out)
        out.append(h[i:m.start()]); depth, j = 0, m.start()
        for t in re.finditer(r'<div\b|</div>', h[m.start():]):
            depth += 1 if t.group(0) != '</div>' else -1
            if depth == 0:
                j = m.start() + t.end(); break
        else:
            j = len(h)
        i = j


def stem_text(stem_html):
    """발문: 지문(psg)·보기(bogi)를 뺀 첫 문단"""
    t = _drop_divs(stem_html, ('psg', 'bogi'))  # 지문·보기 안의 중첩 div(표 묶음 · 발화 줄)까지 통째로 뺀다
    t = re.sub(r'<table.*?</table>', ' ', t, flags=re.S)
    ps = re.findall(r'<p>(.*?)</p>', t, re.S)
    ps = [plain(x) for x in ps if plain(x)]
    return (ps[0] if ps else plain(t)).strip()


def check_item(d, src):
    errs = []
    q = d['q']
    stem_html, opts = parse(q)
    if d.get('set') in ('ox', 'blank', 'essay'):
        return errs
    if len(opts) != 5: errs.append('선택지 %d개' % len(opts))
    if len({re.sub(r'\s+', '', o) for o in opts}) != len(opts): errs.append('선택지 중복')
    try:
        ans = int(d['ans'])
    except Exception:
        ans = 0
    if not 1 <= ans <= 5: errs.append('정답 번호 %s' % d['ans'])
    if q.count('<u>') != q.count('</u>'): errs.append('u 태그 짝')
    if len(re.findall(r'<b[ >]', q)) != q.count('</b>'): errs.append('b 태그 짝')
    txt = re.sub(r'\{[^{}/]{1,40}/[^{}]{1,40}\}', '', plain(q) + plain(d['exp']))  # {옳다. / 옳지 않다.} 같은 고르기 표기는 원문 형식
    for w in ('None', 'nan', '{', '}', '%s', '%d', 'Traceback', '[object', 'undefined', '??', 'NaN'):
        if w in txt: errs.append('이상한 문자열 ' + w)
    for m in re.finditer(r'(이\(가\)|은\(는\)|을\(를\)|와\(과\)|\(으\)로|\(이\)란|\(이\)라|으로\(로\))', plain(q)):
        # 문항 본문에 풀리지 않은 조사 표기 (보기 용어 설명 속 일부러 쓴 것은 건너뜀)
        errs.append('조사 표기 미해결 ' + m.group(1)); break
    for pat, name in ((r'(를를|을을|때문에에|에에서)', '겹조사'), (r'([가-힣]{3,})\s+\1\s+\1', '같은 말 3회 반복')):
        m = re.search(pat, plain(q))
        if m and not (name == '겹조사' and m.group(0) == '을을' and '아래마을' in plain(q)): errs.append(name + ' "%s"' % m.group(0)[:20])
    # 정답-해설 판정
    steps = re.findall(r'<p class="st">(.*?)</p>', d['exp'], re.S)
    st = [plain(s) for s in steps]
    mark = {}
    for s in st:
        m = re.match(r'([①②③④⑤])\s*(.*)', s)
        if m: mark[CIR.index(m.group(1)) + 1] = m.group(2)
    if len(mark) >= 4 and 1 <= ans <= 5:
        stem = stem_text(stem_html)
        neg = bool(NEG.search(stem))
        def verdict(t):
            head = t[:12]
            if NEG_STEP.search(head): return False
            if POS_STEP.search(head): return True
            return None
        vs = {k: verdict(v) for k, v in mark.items()}
        want_ans = (False if not neg else True)  # 정답 선지가 가져야 할 '적절함' 값: 긍정 발문이면 적절한 것(True)
        want_ans = True if not neg else False
        if vs.get(ans) is not None and vs[ans] != want_ans:
            errs.append('정답 ⑤ 판정 불일치: 발문 "%s" / 정답 %d 풀이 "%s"' % (stem[-26:], ans, mark[ans][:30]))
        for k, v in vs.items():
            if k != ans and v is not None and v == want_ans:
                errs.append('오답 선지 %d 가 정답 판정: 발문 "%s" / 풀이 "%s"' % (k, stem[-26:], mark[k][:30])); break
    return errs


def load_book():
    return json.load(open(os.path.join(ROOT, 'hl', 'data.json'), encoding='utf-8'))


def main():
    bank = '--bank' in sys.argv or '--all' in sys.argv
    data = load_book()
    bad = collections.OrderedDict()
    codes = collections.Counter(d['code'] for d in data)
    for c, n in codes.items():
        if n > 1: bad.setdefault(c, []).append('코드 중복 %d회' % n)
    grp = collections.defaultdict(list)
    for d in data:
        if d.get('grp'): grp[d['grp']].append(d)
        e = check_item(d, 'data')
        if e: bad.setdefault(d['code'], []).extend(e)
    for g, L in grp.items():
        ps = [re.search(r'<div class="psg[^"]*"[^>]*>(.*?)</div>', x['q'], re.S) for x in L]
        have = [p for p in ps if p]
        if not have: bad.setdefault(L[0]['code'], []).append('묶음 %s 에 지문 없음' % g)
        elif len({plain(p.group(1)) for p in have}) > 1: bad.setdefault(L[0]['code'], []).append('묶음 %s 의 지문이 문항마다 다름' % g)
    nb = 0
    if bank:
        for f in sorted(glob.glob(os.path.join(ROOT, 'hl', 'hl[0-9][0-9][0-9].json'))):
            for d in json.load(open(f, encoding='utf-8')):
                nb += 1
                e = check_item(d, 'bank')
                if e: bad.setdefault(d['code'], []).extend(e)
    print('검사 문항: 교재 %d%s' % (len(data), ' + 은행 %d' % nb if bank else ''))
    print('문제 있는 문항: %d' % len(bad))
    kinds = collections.Counter()
    for c, es in bad.items():
        for e in es: kinds[re.sub(r'["\'].*', '', e)[:24]] += 1
    for k, n in kinds.most_common(): print('  %4d  %s' % (n, k))
    lim = 60 if '--all' not in sys.argv else 10**9
    for c, es in list(bad.items())[:lim]:
        print(c, '|', ' ; '.join(es)[:230])


if __name__ == '__main__':
    main()
