# -*- coding: utf-8 -*-
"""Ⅲ-C 소리 (ph098~ph105) 생성기."""
from phlib import *
import math, itertools
from fractions import Fraction as Fr

V = 340  # 소리 속력 (m/s)


import hashlib as _hl
_mc0 = mc


def mc(body, right, wrongs, **kw):
    """오답을 본문(그림 포함)에서 정해지는 방식으로 고른다: 같은 문항이 선택지만 달리 중복되지 않게."""
    seen = {re.sub(r'\s+', '', plain(str(right)))}
    ws = []
    for w in wrongs:
        k = re.sub(r'\s+', '', plain(str(w)))
        if k in seen: continue
        seen.add(k); ws.append(w)
    if len(ws) > 4:
        rr = random.Random(int(_hl.md5((body + str(right)).encode('utf-8')).hexdigest()[:8], 16))
        ws = rr.sample(ws, 4)
    return _mc0(body, right, ws, **kw)


# ------------------------------------------------------------------ 공용 도구
def fn(x, nd=2):
    return num(float(x), nd)


def term(fr):
    return (Fr(fr) * 100).denominator == 1


def pick3(r, pool):
    for _ in range(40):
        s = r.sample(pool, 3)
        if len({x[3] for x in s}) < 3: continue
        if any(x[1] for x in s): return [(a, b, c) for a, b, c, _ in s]
    return None


def ratio_str(a, b):
    q = Fr(a) / Fr(b)
    return '%d : %d' % (q.numerator, q.denominator)


def times_str(q):
    q = Fr(q)
    return ('%d배' % q.numerator) if q.denominator == 1 else '%d/%d배' % (q.numerator, q.denominator)


# ------------------------------------------------------------------ 그림
def wf(shape, A, T, phase=0.0):
    """파형 함수 t -> 변위."""
    if shape == 'sin':
        return lambda t: A * math.sin(2 * math.pi * t / T + phase)
    if shape == 'tri':
        return lambda t: A * (2 / math.pi) * math.asin(math.sin(2 * math.pi * t / T + phase))
    return lambda t: A * (1 if math.sin(2 * math.pi * t / T + phase) >= 0 else -1)


def tr_fig(traces, nx=16, cell=14, H=3, w=330, xlab='t (ms)', ytick=True, title=None, u=1):
    """여러 개의 소리 파형(오실로스코프 모양). traces: [(이름, 모양, 진폭(칸), 주기(칸), 위상, 색)]. 세로·가로 한 칸은 1 단위."""
    n = len(traces)
    band = 2 * H * cell + 8
    h = n * band + 36
    f = Fig(w, h)
    ox = 62 if max(len(t[0]) for t in traces) > 1 else 40
    for i, (nm, shape, A, T, ph, col) in enumerate(traces):
        cy = 12 + i * band + H * cell + 4
        for c in range(nx + 1):
            f.line(ox + c * cell, cy - H * cell, ox + c * cell, cy + H * cell, LG, 1)
        for j in range(-H, H + 1):
            f.line(ox, cy + j * cell, ox + nx * cell, cy + j * cell, LG, 1)
        f.line(ox, cy, ox + nx * cell + 6, cy, INK, 1.4)
        f.line(ox, cy - H * cell, ox, cy + H * cell, INK, 1.4)
        f.text(ox - 8, cy + 5, nm, 14, 'end', True, col)
        g = wf(shape, A, T, ph)
        pts = []
        N = 400
        for k in range(N + 1):
            t = nx * k / N
            pts.append((ox + t * cell, cy - g(t) * cell))
        f.poly(pts, 'none', col, 2.4, close=False)
        if ytick:
            for j in range(1, H + 1):
                f.text(ox - 4, cy - j * cell + 4, str(j), 10.5, 'end', c=GR) if j == H else None
    yb = n * band + 16
    for c in range(0, nx + 1, 2):
        f.text(ox + c * cell, yb + 14, fn(c * u), 11.5, 'middle', c=GR)
    f.text(ox + nx * cell + 8, yb + 14, xlab, 12, 'start', True, GR)
    return f.svg()


def string_fig(n, Ltxt=None, w=330, h=130, labels=False):
    f = Fig(w, h)
    x0, x1 = 34, w - 34
    cy = 62
    A = 38
    f.line(x0, cy, x1, cy, LG, 1.2)
    up = [(x0 + (x1 - x0) * i / 120, cy - A * math.sin(n * math.pi * i / 120)) for i in range(121)]
    dn = [(x0 + (x1 - x0) * i / 120, cy + A * math.sin(n * math.pi * i / 120)) for i in range(121)]
    f.poly(up, 'none', BL, 2.4, close=False)
    f.poly(dn, 'none', BL, 1.6, close=False, dash='5 3')
    for xx in (x0, x1):
        f.line(xx, cy - 24, xx, cy + 24, INK, 3.4)
    if labels:
        for i in range(n + 1):
            xx = x0 + (x1 - x0) * i / n
            f.circ(xx, cy, 3.6, RD, RD, 1)
        for i in range(n):
            xx = x0 + (x1 - x0) * (i + 0.5) / n
            f.circ(xx, cy - A, 3.6, GN, GN, 1)
    if Ltxt:
        f.arrow(x0, h - 22, x1, h - 22, GR, 1.4); f.arrow(x1, h - 22, x0, h - 22, GR, 1.4)
        f.text((x0 + x1) / 2, h - 8, Ltxt, 13, 'middle', True, GR)
    return f.svg()


def pipe_fig(kind, n, Ltxt=None, w=330, h=140):
    """kind: 'closed'(왼쪽 닫힘, 오른쪽 열림) 또는 'open'(양쪽 열림). n: 닫힌 관은 L=(2n-1)λ/4, 열린 관은 L=nλ/2."""
    f = Fig(w, h)
    x0, x1 = 34, w - 34
    cy = 62
    A = 26
    f.line(x0, cy - 34, x1, cy - 34, INK, 2.2)
    f.line(x0, cy + 34, x1, cy + 34, INK, 2.2)
    if kind == 'closed':
        f.line(x0, cy - 34, x0, cy + 34, INK, 4)
        f.text(x0 + 4, cy + 52, '닫힌 끝', 12, 'start', True, GR)
        f.text(x1, cy + 52, '열린 끝', 12, 'end', True, GR)
        g = lambda s: math.sin((2 * n - 1) * math.pi * s / 2)
    else:
        f.text(x0, cy + 52, '열린 끝', 12, 'start', True, GR)
        f.text(x1, cy + 52, '열린 끝', 12, 'end', True, GR)
        g = lambda s: math.cos(n * math.pi * s)
    N = 160
    up = [(x0 + (x1 - x0) * i / N, cy - A * g(i / N)) for i in range(N + 1)]
    dn = [(x0 + (x1 - x0) * i / N, cy + A * g(i / N)) for i in range(N + 1)]
    f.line(x0, cy, x1, cy, LG, 1.2)
    f.poly(up, 'none', BL, 2.4, close=False)
    f.poly(dn, 'none', BL, 1.6, close=False, dash='5 3')
    if Ltxt:
        f.arrow(x0, h - 12, x1, h - 12, GR, 1.4); f.arrow(x1, h - 12, x0, h - 12, GR, 1.4)
        f.text((x0 + x1) / 2, h - 2, Ltxt, 13, 'middle', True, GR) if False else f.text((x0 + x1) / 2, h - 16, Ltxt, 13, 'middle', True, GR)
    return f.svg()


def scene_fig(dlab, car=None, two=None, w=330, h=120):
    """메아리 상황: 사람(또는 자동차)과 절벽."""
    f = Fig(w, h)
    cx = 40
    cw = w - 48
    f.line(8, 92, w - 8, 92, GR, 1.4)
    f.rect(cw, 24, 26, 68, '#cbd3df', INK, 1.6)
    for yy in range(28, 92, 9): f.line(cw, yy, cw + 26, yy - 8, GR, 1)
    f.text(cw + 13, 18, '절벽', 12.5, 'middle', True, GR)
    if car:
        f.rect(cx - 22, 66, 44, 20, '#cfe2f7', INK, 1.6)
        f.circ(cx - 12, 88, 5, INK, INK, 1); f.circ(cx + 12, 88, 5, INK, INK, 1)
        f.arrow(cx + 26, 56, cx + 26 + car[0], 56, RD, 2.2)
        f.text(cx + 26, 50, car[1], 12.5, 'start', True, RD)
    else:
        f.circ(cx, 64, 7, '#f0c9a0', INK, 1.5)
        f.line(cx, 71, cx, 88, INK, 2.2)
    xe = cw - 6
    f.arrow(cx + 50, 26, xe, 26, BL, 1.8); f.arrow(xe, 26, cx + 50, 26, BL, 1.8)
    f.text((cx + 50 + xe) / 2, 18, dlab, 13, 'middle', True, BL)
    return f.svg()


def dop_fig(src_dir, vs_lab, obs, w=340, h=200, moving=True):
    """도플러 개략도. src_dir: +1(오른쪽)/-1(왼쪽). obs: [(x, 이름, 방향(0 정지, +1/-1), 속도 글자)]."""
    f = Fig(w, h)
    cy = 118
    xs = 170
    step, u = 20, (0.33 * 20 if moving else 0)
    for k in range(1, 5):
        f.circ(xs - src_dir * u * k, cy, step * k, 'none', BL, 1.5)
    f.circ(xs, cy, 6, RD, RD, 1)
    f.text(xs, cy + 20, 'S', 13, 'middle', True, RD)
    if moving:
        f.arrow(xs, 30, xs + src_dir * 44, 30, RD, 2.4)
        f.text(xs + src_dir * 22, 20, vs_lab, 12.5, 'middle', True, RD)
        f.line(xs, 30, xs, cy - 8, RD, 1, '3 3')
    for (x, nm, d, lab) in obs:
        f.rect(x - 7, cy - 7, 14, 14, GN, INK, 1.4)
        f.text(x, cy + 28, nm, 14, 'middle', True, GN)
        if d:
            f.arrow(x, cy - 14, x + d * 36, cy - 14, GN, 2.4)
            f.text(x + d * 18, cy - 20, lab, 12.5, 'middle', True, GN)
    return f.svg()


def beat_fig(f1, f2, ticks_ms, nbeat=2, w=330, h=190):
    """합성음 y = sin(2π f1 t) + sin(2π f2 t) (시간 ms). 점선은 진폭(포락선)."""
    df = abs(f2 - f1)
    Tmax = nbeat / df * 1000  # ms
    p = Plot(w, h, Tmax * 1.04, 2.6, xmin=0, ymin=-2.6, ml=44, mr=14, mt=16, mb=38)
    p.axes('t (ms)', '변위', (), (), grid=False, origin=False)
    for t in ticks_ms:
        p.line(p.px(t), p.py(-2.6), p.px(t), p.py(2.6), LG, 1)
        p.line(p.px(t), p.py(0) - 3, p.px(t), p.py(0) + 3, INK, 1)
        p.text(p.px(t), h - 22, fn(t), 11.5, 'middle', c=GR)
    N = 600
    pts = [(Tmax * i / N, math.sin(2 * math.pi * f1 * Tmax / 1000 * i / N) + math.sin(2 * math.pi * f2 * Tmax / 1000 * i / N)) for i in range(N + 1)]
    p.pl([(Tmax * i / N, 2 * abs(math.cos(math.pi * df * Tmax / 1000 * i / N))) for i in range(N + 1)], RD, 1.4, '5 3')
    p.pl([(Tmax * i / N, -2 * abs(math.cos(math.pi * df * Tmax / 1000 * i / N))) for i in range(N + 1)], RD, 1.4, '5 3')
    p.pl(pts, BL, 1.8)
    return p.svg()


# ================================================================== ph098 소리의 성질과 세 요소(<보기>)
_B98 = [
    ('소리는 매질이 없는 진공에서는 전달되지 않는다.', True, '소리는 매질의 진동으로 전달되는 역학적 파동이다.', 'vac'),
    ('소리는 진공에서도 전달된다.', False, '소리는 매질이 필요하므로 진공에서는 전달되지 않는다.', 'vac'),
    ('소리는 공기 중에서 종파로 전달된다.', True, '공기 입자가 진행 방향과 나란하게 진동한다.', 'long'),
    ('소리는 공기 중에서 횡파로 전달된다.', False, '공기 중의 소리는 종파이다.', 'long'),
    ('소리의 높낮이(음높이)는 진동수에 의해 결정된다.', True, '진동수가 클수록 높은 소리이다.', 'pitch'),
    ('소리의 높낮이는 진폭에 의해 결정된다.', False, '높낮이는 진동수, 세기는 진폭에 의해 결정된다.', 'pitch'),
    ('소리의 세기(크기)는 진폭이 클수록 크다.', True, '진폭이 클수록 에너지가 커 큰 소리이다.', 'loud'),
    ('진동수가 클수록 소리는 커진다.', False, '소리의 크기는 진폭으로 결정되고, 진동수는 높낮이를 결정한다.', 'loud'),
    ('소리의 음색은 파형에 의해 결정된다.', True, '같은 높이·세기의 소리도 파형이 다르면 음색이 다르다.', 'tone'),
    ('같은 높이와 세기의 소리라도 악기에 따라 음색이 다르다.', True, '악기마다 파형이 달라 음색이 다르다.', 'tone2'),
    ('진동수가 같은 두 소리는 항상 파형이 같다.', False, '진동수가 같아도 파형이 다르면 음색이 다르다.', 'tone3'),
    ('소리의 속력은 고체 속에서보다 기체 속에서 더 빠르다.', False, '일반적으로 소리는 기체 < 액체 < 고체 순으로 빨라진다.', 'speed'),
    ('소리의 속력은 일반적으로 공기 중에서보다 물속에서 빠르다.', True, '물속에서 약 1500 m/s 로 공기 중(약 340 m/s)보다 빠르다.', 'speed2'),
    ('진동수가 20 Hz ~ 20000 Hz인 소리를 사람이 들을 수 있다.', True, '가청 진동수 범위이다.', 'audible'),
    ('진동수가 20000 Hz를 넘는 소리를 초음파라 하며 사람이 들을 수 있다.', False, '초음파는 가청 진동수보다 높아 사람이 들을 수 없다.', 'audible'),
    ('진폭이 2배가 되면 소리의 높이도 2배가 된다.', False, '진폭은 소리의 세기와 관련되며 높이와는 무관하다.', 'amp'),
    ('소리의 속력은 같은 매질에서 진동수에 관계없이 일정하다.', True, '속력은 매질(과 온도)이 결정한다.', 'v'),
    ('같은 매질에서 진동수가 클수록 소리의 파장은 짧아진다.', True, 'λ = v/f 에서 v가 일정하면 f가 클수록 λ가 짧다.', 'lam'),
    ('소리가 한 매질에서 다른 매질로 들어가면 진동수가 변한다.', False, '진동수는 변하지 않고 속력·파장이 변한다.', 'f'),
    ('높은 소리는 낮은 소리보다 파장이 길다(같은 매질).', False, '높은 소리는 진동수가 커 파장이 짧다.', 'high'),
    ('소리의 3요소는 높낮이, 세기, 음색이다.', True, '소리의 세 가지 요소이다.', 'three'),
]


@T('ph098')
def ph098(r, k):
    form = r.choice(['bogi', 'cmp', 'cmp', 'rat', 'shape', 'shape', 'shape'])
    if form == 'bogi':
        s = pick3(r, _B98)
        if not s: return None
        return bogi('소리의 성질과 세 요소에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='하', fam='a', r=r,
                    core='소리는 매질이 필요한 종파이며, 높낮이는 진동수, 세기는 진폭, 음색은 파형으로 결정된다.', point='소리의 세 요소와 결정 요인을 구분한다.')
    u = r.choice([0.5, 1, 2, 2.5, 4, 5])
    ut = fn(u)
    if form in ('cmp', 'rat'):
        nmset = r.choice([('A', 'B'), ('가', '나'), ('P', 'Q'), ('갑', '을')])
        nA, nB = nmset
        TA, TB = r.sample([2, 4, 5, 8, 10], 2) if r.random() < .8 else (4, 4)
        aA, aB = r.sample([1, 1.5, 2, 2.5, 3], 2) if r.random() < .8 else (2, 2)
        if (TA, aA) == (TB, aB): return None
        tr = [(nA, 'sin', aA, TA, 0.0, BL), (nB, 'sin', aB, TB, 0.0, RD)]
        fig = FIG(tr_fig(tr, nx=16, H=3, u=u), '72%')
        base = '그림은 소리 %s, %s를 오실로스코프로 측정한 파형이다. 가로 한 칸은 %s ms이고 세로 한 칸은 같은 소리 세기 단위이며 두 파형의 눈금은 같다. ' % (nA, nB, ut)
        pitch = nA if TA < TB else (nB if TB < TA else '같다')
        loud = nA if aA > aB else (nB if aB > aA else '같다')
        if form == 'cmp':
            ask = r.choice(['cmp', 'cmp', 'fA'])
            if ask == 'fA':
                fA = Fr(1000) / (TA * Fr(str(u)))
                if not term(fA): return None
                body = P(base + '소리 %s의 진동수는?' % nA) + fig
                wr = [fA * 2, fA / 2, Fr(1000) / (TB * Fr(str(u))), Fr(TA) * Fr(str(u)), fA * Fr(str(u)), fA * 4]
                return mc(body, '%s Hz' % fn(fA), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='b', sort='shuf',
                          steps=['그래프에서 %s의 주기는 %d칸 × %s ms = %s ms 이다.' % (nA, TA, ut, fn(TA * Fr(str(u)))), '진동수 f = 1/T = 1000/%s = %s Hz 이다.' % (fn(TA * Fr(str(u))), fn(fA))],
                          core='진동수는 주기의 역수이다.', point='파형에서 주기를 읽어 진동수를 구한다.')
            body = P(base + '두 소리를 비교한 설명으로 옳은 것은?') + fig
            def txt(p, l):
                return '높은 소리: %s, 큰 소리: %s' % (p if p != '같다' else '높이 같음', l if l != '같다' else '크기 같음')
            right = txt(pitch, loud)
            allc = [txt(p, l) for p in (nA, nB, '같다') for l in (nA, nB, '같다')]
            wr = [c for c in allc if c != right]
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                      steps=['주기: T%s = %d칸, T%s = %d칸 → 주기가 짧을수록 진동수가 커서 높은 소리이므로 높은 소리는 %s 이다.' % (nA, TA, nB, TB, pitch),
                             '진폭: %s = %s 칸, %s = %s 칸 → 진폭이 클수록 큰 소리이므로 큰 소리는 %s 이다.' % (nA, fn(aA), nB, fn(aB), loud)],
                      core='파형의 주기가 짧을수록 높은 소리, 진폭이 클수록 큰 소리이다.', point='파형에서 주기(높이)와 진폭(세기)을 읽는다.')
        if TA == TB: return None
        right = ratio_str(Fr(1, TA), Fr(1, TB))
        body = P(base + '소리 %s, %s의 진동수의 비 f%s : f%s는?' % (nA, nB, sub(nA), sub(nB))) + fig
        wr = [ratio_str(TA, TB), ratio_str(Fr(str(aA)), Fr(str(aB))), ratio_str(Fr(str(aB)), Fr(str(aA))), '1 : 1', ratio_str(TA * Fr(str(aA)), TB * Fr(str(aB)))]
        return mc(body, right, wr, r=r, lv='하', fam='b', sort='shuf',
                  steps=['T%s = %d칸, T%s = %d칸 이다.' % (nA, TA, nB, TB), 'f = 1/T 이므로 f%s : f%s = 1/%d : 1/%d = %s 이다.' % (nA, nB, TA, TB, right)],
                  core='진동수는 주기의 역수이다.', point='파형에서 주기를 읽어 진동수의 비를 구한다.')
    # shape: 세 파형의 음색/높이 비교
    shapes = ['sin', 'tri', 'sq']
    names = r.choice(['ABC', '가나다', 'PQR'])
    cols = [BL, RD, GN]
    pairs = list(itertools.combinations(range(3), 2))
    ask = r.choice(['samepitch', 'sametone'])
    for _try in range(60):
        items = [(r.choice(shapes), r.choice([2, 4, 5, 8, 10])) for _ in range(3)]
        if ask == 'samepitch':
            good = [p for p in pairs if items[p[0]][1] == items[p[1]][1] and items[p[0]][0] != items[p[1]][0]]
        else:
            good = [p for p in pairs if items[p[0]][0] == items[p[1]][0] and items[p[0]][1] != items[p[1]][1]]
        if len(good) == 1 or (len(good) == 0 and r.random() < 0.15): break
    else:
        return None
    tr = [(names[i], items[i][0], 1.5, items[i][1], 0.0, cols[i]) for i in range(3)]
    if ask == 'samepitch':
        txt = '높이가 같고 음색이 다른 두 소리'
        why = lambda p: '주기가 같아 높이가 같고 파형이 달라 음색이 다르다.'
    else:
        txt = '음색이 같고 높이가 다른 두 소리'
        why = lambda p: '파형이 같아 음색이 같고 주기가 달라 높이가 다르다.'
    fig = FIG(tr_fig(tr, nx=20, H=2, u=u), '72%')
    pn = lambda p: '%s와 %s' % (names[p[0]], names[p[1]])
    base = '그림은 세 소리 %s, %s, %s를 오실로스코프로 측정한 파형이다. 가로 한 칸은 %s ms이고, 세 소리의 진폭은 같다. ' % (names[0], names[1], names[2], ut)
    if good:
        right = pn(good[0])
        wr = [pn(p) for p in pairs if p != good[0]] + ['세 소리 모두', '해당하는 것 없음']
    else:
        right = '해당하는 것 없음'
        wr = [pn(p) for p in pairs] + ['세 소리 모두']
    body = P(base + '%s은?' % txt) + fig
    stp = ['주기와 파형: ' + ', '.join('%s: %s파, T = %d칸' % (names[i], {'sin': '사인', 'tri': '삼각', 'sq': '사각'}[items[i][0]], items[i][1]) for i in range(3)) + ' 이다.']
    stp.append((pn(good[0]) + '는 ' + why(good[0])) if good else '조건을 만족하는 짝이 없다.')
    return mc(body, right, wr, r=r, lv='상' if ask == 'sametone' else '중', fam='c', sort='shuf', steps=stp,
              core='높이는 주기(진동수), 음색은 파형으로 결정되며 세기는 진폭으로 결정된다.', point='파형에서 주기와 모양을 구분해 읽는다.')


# ================================================================== ph099 소리의 속력과 반사(메아리)
@T('ph099')
def ph099(r, k):
    form = r.choice(['echo', 'echo', 'rev', 'two', 'thunder', 'lam', 'car', 'temp', 'temp'])
    if form == 'echo':
        t = Fr(r.randint(1, 50), 10)
        d = Fr(V) * t / 2
        if not term(d): return None
        fig = FIG(scene_fig('d'), '70%') if r.random() < 0.6 else ''
        body = P('소리의 속력을 340 m/s라 할 때, 절벽을 향해 소리를 지르고 %s초 후에 메아리를 들었다. 사람과 절벽 사이의 거리는?' % fn(t)) + fig
        wr = [d * 2, d / 2, Fr(V) * t, Fr(V) / t, d + 100]
        return mc(body, '%s m' % fn(d), ['%s m' % fn(w) for w in wr], r=r, lv='하', fam='a',
                  steps=['소리는 절벽까지 갔다가 되돌아오므로 왕복 거리 = 340 × %s = %s m 이다.' % (fn(t), fn(Fr(V) * t)), '사람과 절벽 사이의 거리 = %s / 2 = %s m 이다.' % (fn(Fr(V) * t), fn(d))],
                  core='메아리는 소리가 왕복한 것이므로 거리 = vt/2 이다.', point='왕복 거리의 절반이 절벽까지의 거리임을 이용한다.')
    if form == 'rev':
        d = 17 * r.randint(1, 60)
        t = Fr(2 * d, V)
        if not term(t): return None
        fig = FIG(scene_fig('%d m' % d), '70%') if r.random() < 0.7 else ''
        body = P('소리의 속력이 340 m/s일 때, 절벽에서 %d m 떨어진 곳에서 손뼉을 쳤다. 메아리가 들리기까지 걸리는 시간은?' % d) + fig
        wr = [t / 2, t * 2, Fr(d, V), t + Fr(1, 2), t + 1]
        return mc(body, '%s s' % fn(t), ['%s s' % fn(w) for w in wr], r=r, lv='중', fam='a',
                  steps=['소리는 왕복 2 × %d = %d m 를 진행한다.' % (d, 2 * d), 't = 2d/v = %d / 340 = %s s 이다.' % (2 * d, fn(t))],
                  core='메아리가 들리는 시간 t = 2d/v.', point='왕복 거리를 속력으로 나눈다.')
    if form == 'two':
        t1 = Fr(r.randint(1, 20), 10)
        t2 = t1 + Fr(r.randint(1, 15), 10)
        d1, d2 = Fr(V) * t1 / 2, Fr(V) * t2 / 2
        if not term(d1) or not term(d2): return None
        ask = r.choice(['sum', 'diff'])
        if ask == 'sum':
            body = P('두 절벽 사이의 한 지점에서 손뼉을 쳤더니 %s초와 %s초 후에 각각 메아리가 들렸다. 소리의 속력이 340 m/s일 때, 두 절벽 사이의 거리는? (단, 두 절벽과 사람은 한 직선 위에 있다.)' % (fn(t1), fn(t2)))
            right = d1 + d2
            wr = [d2 - d1, d2, Fr(V) * (t1 + t2), (d1 + d2) / 2, d1 + d2 + 85]
            return mc(body, '%s m' % fn(right), ['%s m' % fn(w) for w in wr], r=r, lv='상', fam='b',
                      steps=['가까운 절벽까지 거리 d₁ = 340 × %s / 2 = %s m 이다.' % (fn(t1), fn(d1)), '먼 절벽까지 거리 d₂ = 340 × %s / 2 = %s m 이다.' % (fn(t2), fn(d2)), '두 절벽 사이의 거리 = d₁ + d₂ = %s m 이다.' % fn(right)],
                      core='각 메아리의 시간으로 각 절벽까지의 거리를 구해 더한다.', point='두 번의 메아리를 각각 처리한다.')
        body = P('한 지점에서 손뼉을 쳤더니 서로 다른 두 절벽에서 반사된 메아리가 %s초와 %s초 후에 들렸다. 두 절벽까지 거리의 차는? (단, 소리의 속력은 340 m/s이다.)' % (fn(t1), fn(t2)))
        right = d2 - d1
        wr = [d1 + d2, right * 2, right / 2, Fr(V) * (t2 - t1), d2]
        return mc(body, '%s m' % fn(right), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='b',
                  steps=['d₁ = %s m, d₂ = %s m 이다.' % (fn(d1), fn(d2)), '거리의 차 = %s - %s = %s m 이다.' % (fn(d2), fn(d1), fn(right))],
                  core='거리 = vt/2.', point='시간차의 절반에 속력을 곱해도 같다.')
    if form == 'thunder':
        t = r.randint(1, 15)
        d = V * t
        body = P('번개가 친 것을 본 뒤 %d초 후에 천둥소리를 들었다. 소리의 속력을 340 m/s로 하고 빛이 도달하는 시간은 무시할 때, 번개가 친 곳까지의 거리는?' % t)
        wr = [d / 2, d * 2, V / t if False else d + 340, d - 340 if d > 340 else d + 680, d * 3]
        return mc(body, '%d m' % d, ['%s m' % fn(w) for w in wr], r=r, lv='하', fam='c',
                  steps=['빛은 매우 빠르므로 도달 시간을 무시하면 소리가 이동한 시간이 %d s 이다.' % t, '거리 = vt = 340 × %d = %d m 이다. (왕복이 아닌 편도이다)' % (t, d)],
                  core='천둥소리는 편도이므로 거리 = vt 이다.', point='메아리(왕복)와 천둥(편도)을 구분한다.')
    if form == 'lam':
        f = r.choice([34 * i for i in range(1, 60)] + [170, 340, 425, 500, 680, 850, 1020, 1700, 272, 136, 68, 200, 400, 1000, 2000])
        lam = Fr(V, f)
        if not term(lam): return None
        body = P('진동수가 %d Hz인 소리가 공기 중(소리의 속력 340 m/s)에서 진행한다. 이 소리의 파장은?' % f)
        wr = [lam * 2, lam / 2, Fr(f * V), Fr(f, V), lam * 10]
        return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='d',
                  steps=['v = fλ 에서 λ = v/f = 340 / %d = %s m 이다.' % (f, fn(lam))], core='λ = v/f.', point='소리의 속력과 진동수로 파장을 구한다.')
    if form == 'car':
        u = r.choice([5, 10, 15, 20, 17, 34, 30, 25])
        t = Fr(r.randint(1, 12), 2)
        way = r.choice(['to', 'away'])
        if way == 'to':
            L = (V + u) * t / 2
            expl = ['소리가 간 거리 340 × %s = %s m 와 자동차가 간 거리 %d × %s = %s m 의 합이 처음 거리의 2배이다.' % (fn(t), fn(V * t), u, fn(t), fn(u * t)), 'L = (%s + %s)/2 = %s m 이다.' % (fn(V * t), fn(u * t), fn(L))]
            cond = '절벽을 향해'
        else:
            L = (V - u) * t / 2
            expl = ['소리가 간 거리 340 × %s = %s m 는 처음 거리 L 의 왕복(2L)에서 자동차가 멀어진 거리 %s m 를 더한 값이다: 2L + %s = %s.' % (fn(t), fn(V * t), fn(u * t), fn(u * t), fn(V * t)), 'L = (%s - %s)/2 = %s m 이다.' % (fn(V * t), fn(u * t), fn(L))]
            cond = '절벽에서 멀어지며'
        if not term(L): return None
        # 교차 검증: 시간으로 적분
        sound = V * t
        carpos = u * t
        if way == 'to': assert abs(float(sound + carpos - 2 * L)) < 1e-9
        else: assert abs(float(sound - carpos - 2 * L)) < 1e-9
        fig = FIG(scene_fig('L', car=(40, '%d m/s' % u) if way == 'to' else (40, '%d m/s' % u)), '70%') if way == 'to' else ''
        body = P('자동차가 %d m/s의 일정한 속력으로 %s 달리며 경적을 울렸더니 %s초 후에 운전자가 메아리를 들었다. 경적을 울린 순간 자동차와 절벽 사이의 거리는? (단, 소리의 속력은 340 m/s이다.)' % (u, cond, fn(t))) + fig
        alt = (V * t) / 2
        wr = [alt, (V - u) * t / 2 if way == 'to' else (V + u) * t / 2, (V + u) * t, V * t, L + u * t]
        return mc(body, '%s m' % fn(L), ['%s m' % fn(w) for w in wr], r=r, lv='상', fam='e', steps=expl,
                  core='움직이는 물체에서 낸 소리의 메아리는 소리의 이동 거리와 물체의 이동 거리를 함께 고려한다.', point='소리와 자동차가 이동한 거리의 관계를 세운다.')
    # temp
    T_ = r.choice([-5, 0, 5, 10, 15, 20, 25, 30, 35])
    v = Fr(331) + Fr(3, 5) * T_
    sub_ = r.choice(['v', 'd'])
    if sub_ == 'v':
        body = P('공기 중 소리의 속력은 기온이 t(℃)일 때 v = 331 + 0.6t (m/s)로 나타낼 수 있다. 기온이 %d℃일 때 소리의 속력은?' % T_)
        wr = [v + 6, v - 6, Fr(331) + T_, Fr(340), v + 12, Fr(331) * Fr(6, 5)]
        return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='f',
                  steps=['v = 331 + 0.6 × (%d) = %s m/s 이다.' % (T_, fn(v))], core='공기 중 소리의 속력은 온도가 높을수록 빠르다(v = 331 + 0.6t).', point='식에 온도를 대입한다.')
    t = Fr(2)
    d = v * t / 2
    body = P('공기 중 소리의 속력은 기온이 t(℃)일 때 v = 331 + 0.6t (m/s)이다. 기온이 %d℃인 날 절벽을 향해 소리를 질렀더니 %d초 후에 메아리가 들렸다. 절벽까지의 거리는?' % (T_, t))
    wr = [d * 2, d / 2, Fr(340) * t / 2, d + 6, d - 6]
    return mc(body, '%s m' % fn(d), ['%s m' % fn(w) for w in wr], r=r, lv='상', fam='f',
              steps=['기온 %d℃ 에서 v = 331 + 0.6 × (%d) = %s m/s 이다.' % (T_, T_, fn(v)), '거리 = vt/2 = %s × 2 / 2 = %s m 이다.' % (fn(v), fn(d))],
              core='온도에 따른 소리의 속력을 구한 뒤 메아리 거리 vt/2 에 적용한다.', point='속력을 먼저 구하고 왕복 거리를 처리한다.')


# ================================================================== ph100 도플러 효과
def dop(f, so, vo, ss, vs):
    """so: 관찰자가 음원 쪽으로 이동(+1)/멀어짐(-1)/정지(0), ss: 음원이 관찰자 쪽으로 이동(+1)/멀어짐(-1)/정지(0)."""
    return Fr(f) * (Fr(V) + so * vo) / (Fr(V) - ss * vs)


_B100 = [
    ('음원이 정지한 관찰자에게 다가오면 관찰자가 듣는 소리의 진동수는 음원의 진동수보다 크다.', True, '파장이 짧아져 진동수가 커진다.', 'a1'),
    ('음원이 정지한 관찰자에게서 멀어지면 관찰자가 듣는 소리의 진동수는 음원의 진동수보다 크다.', False, '음원이 멀어지면 파장이 길어져 진동수가 작아진다.', 'a1'),
    ('관찰자가 정지한 음원에 다가가면 관찰자가 측정하는 진동수는 커진다.', True, '단위 시간에 받는 파면의 수가 늘어난다.', 'b1'),
    ('관찰자가 정지한 음원에서 멀어지면 관찰자가 측정하는 진동수는 커진다.', False, '단위 시간에 받는 파면의 수가 줄어 진동수가 작아진다.', 'b1'),
    ('음원이 움직이면 음원 앞쪽의 파장은 짧아지고 뒤쪽의 파장은 길어진다.', True, '파면이 앞쪽에서는 압축되고 뒤쪽에서는 늘어난다.', 'c1'),
    ('음원이 움직여도 소리의 속력은 변하지 않는다.', True, '소리의 속력은 매질이 결정한다.', 'd1'),
    ('음원이 움직이면 소리의 속력이 음원의 속력만큼 달라진다.', False, '소리의 속력은 매질에 의해서만 결정된다.', 'd1'),
    ('도플러 효과는 음원이나 관찰자가 움직여서 진동수가 달리 측정되는 현상이다.', True, '상대 운동에 의한 진동수 변화이다.', 'e1'),
    ('구급차가 다가올 때 사이렌 소리가 높게 들리다가 지나가면 낮게 들리는 것은 도플러 효과이다.', True, '접근할 때 f′ > f, 멀어질 때 f′ < f 이다.', 'f1'),
    ('음원과 관찰자가 같은 속도로 같은 방향으로 움직이면 관찰자가 듣는 진동수는 음원의 진동수와 같다.', True, '상대 속도가 0이므로 진동수가 변하지 않는다(무풍 시).', 'g1'),
    ('음원이 관찰자를 향해 속력 v_s로 다가올 때 진동수는 f′ = f·v/(v − v_s) 이다.', True, '앞쪽 파장이 (v − v_s)/f 로 짧아진다.', 'h1'),
    ('음원이 관찰자에게서 멀어질 때 진동수는 f′ = f·v/(v − v_s) 이다.', False, '멀어질 때는 f′ = f·v/(v + v_s) 이다.', 'h1'),
    ('도플러 효과에서 음원의 속력이 소리의 속력에 가까워질수록 앞쪽 소리의 진동수는 매우 커진다.', True, 'v − v_s → 0 이면 f′ → ∞ 이다.', 'i1'),
    ('음원이 원 궤도를 돌면 관찰자가 듣는 소리의 진동수는 변하지 않는다.', False, '다가올 때와 멀어질 때 진동수가 달라진다.', 'j1'),
    ('관찰자가 음원 쪽으로 이동할 때 측정한 파장은 정지했을 때보다 짧아진다.', False, '파장은 매질 속에서 변하지 않는다. 관찰자가 받는 파면 수만 늘어난다.', 'k1'),
    ('음원이 정지해 있을 때 관찰자의 속력이 클수록 가까워지며 듣는 진동수 변화량이 크다.', True, 'f′ - f = f·v_o/v 로 v_o에 비례한다.', 'l1'),
    ('경찰차가 가까워지면서 소리가 높아지는 것은 음원의 진동수 자체가 커지기 때문이다.', False, '음원의 진동수는 일정하고, 관찰자가 측정하는 진동수가 커진다.', 'm1'),
    ('도플러 효과는 빛이나 전자기파에서도 나타난다.', True, '파동이면 상대 운동에 의한 진동수 변화가 나타난다(적색·청색 편이).', 'n1'),
]


def _dop_pick(r, mode):
    """깨끗한 값을 가진 (f, vs, vo, f') 를 고른다."""
    for _ in range(300):
        vs = r.choice([10, 17, 20, 34, 68, 85])
        vo = r.choice([10, 17, 20, 34, 68, 85])
        f = r.randrange(100, 1001, 10)
        so = ss = 0
        if mode in ('obs', 'both'): so = r.choice([1, -1])
        if mode in ('src', 'both'): ss = r.choice([1, -1])
        if mode == 'src': vo = 0
        if mode == 'obs': vs = 0
        fp = dop(f, so, vo, ss, vs)
        if fp.denominator == 1:
            return f, vs, vo, so, ss, int(fp)
    return None


@T('ph100')
def ph100(r, k):
    form = r.choice(['src', 'obs', 'obs', 'both', 'fig', 'fig', 'fig', 'inv', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B100)
        if not s: return None
        return bogi('도플러 효과에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='하', fam='f', r=r,
                    core='음원이나 관찰자가 서로 가까워지면 진동수가 커지고 멀어지면 작아진다. f′ = f(v ± v_o)/(v ∓ v_s).', point='도플러 효과의 방향과 원인을 판단한다.')
    if form in ('src', 'obs', 'both'):
        p = _dop_pick(r, form)
        if not p: return None
        f, vs, vo, so, ss, fp = p
        parts = []
        if ss: parts.append('음원이 %s %d m/s의 속력으로 %s' % ('정지한 관찰자 쪽으로' if ss == 1 else '관찰자에게서 멀어지는 방향으로', vs, '움직인다'))
        if so: parts.append('관찰자가 %s %d m/s의 속력으로 %s' % ('정지한 음원 쪽으로' if so == 1 else '음원에게서 멀어지는 방향으로', vo, '움직인다'))
        if form == 'src':
            sent = '진동수 %d Hz인 소리를 내는 음원이 %s 관찰자가 정지해 있다.' % (f, '%s %d m/s의 속력으로 %s.' % ('관찰자 쪽으로' if ss == 1 else '관찰자에게서 멀어지는 방향으로', vs, '움직이고'))
        elif form == 'obs':
            sent = '진동수 %d Hz인 소리를 내는 음원이 정지해 있고, 관찰자가 %s %d m/s의 속력으로 움직인다.' % (f, '음원 쪽으로' if so == 1 else '음원에게서 멀어지는 방향으로', vo)
        else:
            sent = '진동수 %d Hz인 소리를 내는 음원이 %s %d m/s의 속력으로 움직이고, 관찰자는 %s %d m/s의 속력으로 움직인다.' % (f, '관찰자 쪽으로' if ss == 1 else '관찰자에게서 멀어지는 방향으로', vs, '음원 쪽으로' if so == 1 else '음원에게서 멀어지는 방향으로', vo)
        body = P(sent.replace('움직이고 관찰자가 정지해 있다.', '움직이고 있고, 관찰자는 정지해 있다.') + ' 소리의 속력이 340 m/s일 때, 관찰자가 측정하는 소리의 진동수는?')
        cands = [dop(f, -so, vo, -ss, vs), dop(f, so, vo, -ss, vs), dop(f, -so, vo, ss, vs), Fr(f) * (V + so * vo) / V, Fr(f) * V / (V + ss * vs),
                 Fr(f) * (V + ss * vs) / V, Fr(f) * (V - ss * vs) / V, Fr(f) * (V - so * vo) / V, Fr(f) * V / (V - so * vo) if so else Fr(f) * 2 - fp, Fr(f) * V / (V + so * vo) if so else Fr(f) * 2 - fp, Fr(f) * 2 - fp, Fr(f)]
        cands = [c for c in cands if c > 0]
        right = '%s Hz' % fn(fp)
        wr = ['%s Hz' % fn(c) for c in cands if c != fp]
        # 풀이
        num_ = 'v %s v_o' % ('+' if so == 1 else '-') if so else 'v'
        den_ = 'v %s v_s' % ('-' if ss == 1 else '+') if ss else 'v'
        nv = V + so * vo
        dv = V - ss * vs
        stp = ['도플러 효과: f′ = f (v ± v_o)/(v ∓ v_s). 관찰자가 음원 쪽이면 분자에 +, 음원이 관찰자 쪽이면 분모에 -를 쓴다.',
               'f′ = %d × %d / %d = %d Hz 이다.' % (f, nv, dv, fp)]
        assert Fr(f * nv, dv) == fp
        wi = [w for w in wr if Fr(w.split()[0]).denominator == 1]
        if len(wi) >= 4: wr = wi
        return mc(body, right, wr, r=r, lv={'src': '하', 'obs': '중', 'both': '상'}[form], fam='a' if form == 'src' else ('b' if form == 'obs' else 'c'), sort='shuf', steps=stp,
                  core='f′ = f (v ± v_o)/(v ∓ v_s) (가까워지면 f′ 증가).', point='이동 방향에 따라 부호를 정해 f′을 구한다.')
    if form == 'fig':
        vs = r.choice([17, 20, 34, 68, 85])
        sd = r.choice([1, -1])
        f = None
        for _ in range(200):
            f_ = r.randrange(100, 1001, 10)
            if dop(f_, 0, 0, 1, vs).denominator == 1 and dop(f_, 0, 0, -1, vs).denominator == 1:
                f = f_
                break
        if f is None: return None
        fa = dop(f, 0, 0, 1, vs)   # 앞쪽 관찰자
        fb = dop(f, 0, 0, -1, vs)  # 뒤쪽 관찰자
        xa, xb = (318, 20) if sd == 1 else (20, 318)
        obs = [(xa, 'A', 0, ''), (xb, 'B', 0, '')]
        # 앞쪽 = 이동 방향 쪽
        front = 'A'
        fig = FIG(dop_fig(sd, 'v_s = %d m/s' % vs, obs), '88%')
        base = '그림은 진동수 %d Hz인 소리를 내는 음원 S가 %d m/s의 속력으로 %s으로 움직이며 만드는 파면을 개략적으로 나타낸 것이다. 관찰자 A, B는 정지해 있다. 소리의 속력은 340 m/s이다. ' % (f, vs, '오른쪽' if sd == 1 else '왼쪽')
        ask = r.choice(['fa', 'fb', 'ratio'])
        wrp = lambda lst, u: ['%s %s' % (fn(c), u) for c in lst]
        if ask == 'fa':
            body = P(base + 'A가 측정하는 소리의 진동수는?') + fig
            wr = [fb, Fr(f), Fr(f) * (V + vs) / V, Fr(f) * V / (V + vs) if False else Fr(f) * (V - vs) / V, Fr(f) * 2 - fb]
            return mc(body, '%s Hz' % fn(fa), wrp(wr, 'Hz'), r=r, lv='중', fam='d', sort='shuf',
                      steps=['A는 음원이 다가오는 쪽에 있으므로 f′ = f·v/(v - v_s) = %d × 340 / (340 - %d) = %s Hz 이다.' % (f, vs, fn(fa))],
                      core='다가오는 음원 앞에서는 f′ = f v/(v - v_s) 로 진동수가 커진다.', point='파면이 촘촘한 쪽이 높은 진동수임을 이용한다.')
        if ask == 'fb':
            body = P(base + 'B가 측정하는 소리의 진동수는?') + fig
            wr = [fa, Fr(f), Fr(f) * (V - vs) / V, Fr(f) * (V + vs) / V, Fr(f) * 2 - fa]
            return mc(body, '%s Hz' % fn(fb), wrp(wr, 'Hz'), r=r, lv='중', fam='d', sort='shuf',
                      steps=['B는 음원이 멀어지는 쪽에 있으므로 f′ = f·v/(v + v_s) = %d × 340 / (340 + %d) = %s Hz 이다.' % (f, vs, fn(fb))],
                      core='멀어지는 음원 뒤에서는 f′ = f v/(v + v_s) 로 진동수가 작아진다.', point='파면이 성긴 쪽이 낮은 진동수임을 이용한다.')
        right = ratio_str(fa, fb)
        body = P(base + 'A와 B가 측정하는 진동수의 비 f%s : f%s는?' % (sub('A'), sub('B'))) + fig
        wr = [ratio_str(fb, fa), ratio_str(V + vs, V - vs), ratio_str(V - vs, V + vs) if False else ratio_str(V, V - vs), ratio_str(V + vs, V), '1 : 1']
        assert Fr(fa) / Fr(fb) == Fr(V + vs, V - vs)
        return mc(body, right, wr, r=r, lv='상', fam='d', sort='shuf',
                  steps=['f%s = f v/(v - v_s), f%s = f v/(v + v_s) 이다.' % (sub('A'), sub('B')), 'f%s : f%s = (v + v_s) : (v - v_s) = %d : %d = %s 이다.' % (sub('A'), sub('B'), V + vs, V - vs, right)],
                  core='음원 앞뒤의 진동수 비는 (v + v_s) : (v - v_s) 이다.', point='앞·뒤 관찰자의 진동수를 비로 비교한다.')
    # inv: f' 주어지고 속력 구하기
    for _ in range(300):
        f = r.randrange(100, 1001, 10)
        vs = r.choice([10, 17, 20, 34, 68, 85])
        kind = r.choice(['src', 'obs'])
        so = 1 if kind == 'obs' else 0
        ss = 1 if kind == 'src' else 0
        if kind == 'obs': vo, vs_ = vs, 0
        else: vo, vs_ = 0, vs
        fp = dop(f, so, vo, ss, vs_)
        if fp.denominator == 1: break
    else:
        return None
    fp = int(fp)
    if kind == 'src':
        body = P('진동수 %d Hz인 소리를 내는 음원이 정지한 관찰자에게 일정한 속력으로 다가오고 있다. 관찰자가 측정한 진동수가 %d Hz일 때 음원의 속력은? (단, 소리의 속력은 340 m/s이다.)' % (f, fp))
        wr = [Fr(V) * (fp - f) / f, Fr(V) * (fp - f) / fp * 2, Fr(V) * f / fp, Fr(fp - f), Fr(V) * (fp - f) / (fp + f) * 2 if False else vs * 2]
        # 풀이: f' = f v/(v - vs) -> vs = v (1 - f/f')
        assert Fr(V) * (1 - Fr(f, fp)) == vs
        wr = [Fr(V) * (fp - f) / f, Fr(V) * f / fp, Fr(fp - f), vs * 2, Fr(V) * (fp - f) / (fp + f)]
        return mc(body, '%d m/s' % vs, ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='e',
                  steps=['f′ = f v/(v - v_s) 에서 v_s = v (1 - f/f′) 이다.', 'v_s = 340 × (1 - %d/%d) = %d m/s 이다.' % (f, fp, vs)],
                  core='음원이 다가올 때 f′ = f v/(v - v_s).', point='도플러 식을 변형해 음원의 속력을 구한다.')
    body = P('진동수 %d Hz인 소리를 내는 정지한 음원을 향해 관찰자가 일정한 속력으로 다가가고 있다. 관찰자가 측정한 진동수가 %d Hz일 때 관찰자의 속력은? (단, 소리의 속력은 340 m/s이다.)' % (f, fp))
    assert Fr(V) * (Fr(fp, f) - 1) == vo
    wr = [Fr(V) * (fp - f) / fp, Fr(V) * f / fp, Fr(fp - f), vo * 2, Fr(V) * (fp - f) / (fp + f)]
    return mc(body, '%d m/s' % vo, ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='e',
              steps=['f′ = f (v + v_o)/v 에서 v_o = v (f′/f - 1) 이다.', 'v_o = 340 × (%d/%d - 1) = %d m/s 이다.' % (fp, f, vo)],
              core='관찰자가 다가갈 때 f′ = f (v + v_o)/v.', point='도플러 식을 변형해 관찰자의 속력을 구한다.')


# ================================================================== ph101 맥놀이
_B101 = [
    ('진동수가 약간 다른 두 소리가 중첩되면 소리의 세기가 주기적으로 커졌다 작아졌다 한다.', True, '이것이 맥놀이이다.', 'def'),
    ('맥놀이는 진동수가 같은 두 소리가 중첩될 때 나타난다.', False, '진동수가 약간 달라야 맥놀이가 생긴다.', 'def'),
    ('맥놀이 진동수는 두 소리의 진동수의 차이다.', True, 'f_beat = |f₁ - f₂| 이다.', 'f'),
    ('맥놀이 진동수는 두 소리의 진동수의 합이다.', False, '맥놀이 진동수는 진동수의 차이다.', 'f'),
    ('두 소리의 진동수 차가 클수록 맥놀이가 빨라진다.', True, '맥놀이 진동수가 진동수 차와 같다.', 'speed'),
    ('두 소리의 진동수 차가 클수록 맥놀이 주기가 길어진다.', False, '맥놀이 주기 = 1/|f₁ - f₂| 이므로 차가 클수록 주기가 짧다.', 'speed'),
    ('맥놀이 현상은 소리의 간섭의 한 예이다.', True, '진동수가 다른 두 파동의 중첩에 의한 간섭이다.', 'interf'),
    ('맥놀이에서 소리가 가장 커지는 순간은 두 소리가 같은 위상으로 중첩될 때이다.', True, '보강 간섭이다.', 'loud'),
    ('맥놀이에서 소리가 가장 작아지는 순간은 두 소리가 반대 위상으로 중첩될 때이다.', True, '상쇄 간섭이다.', 'quiet'),
    ('두 소리의 진동수가 440 Hz, 444 Hz일 때 1초에 4번의 맥놀이가 들린다.', True, '444 - 440 = 4 Hz 이다.', 'ex1'),
    ('두 소리의 진동수가 440 Hz, 444 Hz일 때 맥놀이 주기는 4초이다.', False, '맥놀이 주기는 1/4 = 0.25 초이다.', 'ex1'),
    ('맥놀이 진동수가 0이면 두 소리의 진동수가 같다.', True, '|f₁ - f₂| = 0 이다.', 'zero'),
    ('악기를 조율할 때 기준음과의 맥놀이가 없어지도록 줄의 장력을 조절한다.', True, '맥놀이가 없으면 진동수가 같다.', 'tune'),
    ('줄의 장력을 크게 하면 줄이 내는 소리의 진동수는 작아진다.', False, '장력이 커지면 파동의 속력이 커져 진동수가 커진다.', 'tension'),
    ('맥놀이 때 합성된 소리의 진동수는 두 소리의 평균 진동수와 같다.', True, '합성음의 진동수는 (f₁ + f₂)/2 이다.', 'avg'),
    ('맥놀이는 횡파에서만 나타나고 종파에서는 나타나지 않는다.', False, '소리(종파)에서도 나타난다.', 'wave'),
    ('맥놀이에서 소리의 크기가 변하는 주기는 두 소리 각각의 주기보다 길다.', True, '맥놀이 주기 1/|Δf| 는 각 소리의 주기보다 크다(Δf가 작을 때).', 'period'),
    ('진동수가 같고 진폭이 다른 두 소리가 중첩되면 맥놀이가 생긴다.', False, '진동수가 같으면 맥놀이가 없다.', 'amp'),
]


@T('ph101')
def ph101(r, k):
    form = r.choice(['calc', 'calc', 'calc', 'graph', 'graph', 'tune', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B101)
        if not s: return None
        return bogi('맥놀이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='하', fam='d', r=r,
                    core='진동수가 약간 다른 두 소리가 중첩되면 맥놀이가 생기며 맥놀이 진동수는 |f₁ - f₂| 이다.', point='맥놀이의 원인과 진동수를 판단한다.')
    if form == 'calc':
        sub_ = r.choice(['fb', 'f2', 'period', 'count'])
        f1 = r.choice([256, 264, 330, 392, 440, 480, 512, 523, 600, 660])
        d = r.choice([1, 2, 3, 4, 5, 6, 8, 10])
        f2 = f1 + d
        if sub_ == 'fb':
            body = P('진동수가 %d Hz, %d Hz인 두 소리를 동시에 낼 때 1초 동안 들리는 맥놀이의 횟수는?' % (f1, f2))
            wr = [f1 + f2, d * 2, Fr(d, 2) if d % 2 == 0 else d + 1, Fr(1, d), d + 2, f1 - d]
            return mc(body, '%d회' % d, ['%s회' % fn(w) for w in wr], r=r, lv='하', fam='a',
                      steps=['맥놀이 진동수 = |f₁ - f₂| = |%d - %d| = %d Hz 이므로 1초에 %d번이다.' % (f1, f2, d, d)],
                      core='맥놀이 진동수 f_b = |f₁ - f₂|.', point='진동수 차로 맥놀이 횟수를 구한다.')
        if sub_ == 'f2':
            body = P('진동수가 %d Hz인 소리 A와 진동수를 모르는 소리 B를 동시에 냈더니 1초에 %d번의 맥놀이가 들렸다. B의 진동수가 A보다 클 때 B의 진동수는?' % (f1, d))
            wr = [f1 - d, f1 + 2 * d, f1 - 2 * d, d, f1 + d + 1, f1 * d]
            return mc(body, '%d Hz' % f2, ['%d Hz' % w for w in wr], r=r, lv='중', fam='a',
                      steps=['|f_B - %d| = %d 이고 f_B > %d 이므로 f_B = %d + %d = %d Hz 이다.' % (f1, d, f1, f1, d, f2)],
                      core='f_b = |f₁ - f₂| 이므로 f₂ = f₁ ± f_b.', point='진동수 차에서 미지의 진동수를 구한다.')
        if sub_ == 'period':
            d = r.choice([1, 2, 4, 5, 8, 10, 20, 25])
            body = P('진동수가 %d Hz, %d Hz인 두 소리를 동시에 낼 때 맥놀이의 주기는?' % (f1, f1 + d))
            tb = Fr(1, d)
            wr = [Fr(d), tb * 2, tb / 2, tb * 4, tb + Fr(1, 2)]
            return mc(body, '%s s' % fn(tb), ['%s s' % fn(w) for w in wr], r=r, lv='중', fam='a', sort='shuf',
                      steps=['맥놀이 진동수 = %d Hz 이다.' % d, '맥놀이 주기 = 1/f_b = 1/%d = %s s 이다.' % (d, fn(tb))],
                      core='맥놀이 주기 = 1/|f₁ - f₂|.', point='맥놀이 진동수의 역수가 맥놀이 주기이다.')
        t = r.choice([2, 3, 5, 10, 20])
        n = d * t
        body = P('진동수가 %d Hz, %d Hz인 두 소리를 동시에 낼 때 %d초 동안 들리는 맥놀이의 횟수는?' % (f1, f2, t))
        wr = [d, d * t * 2, n + d, t, n // 2 if n % 2 == 0 else n + 1, (f1 + f2) * t]
        return mc(body, '%d회' % n, ['%d회' % w for w in wr], r=r, lv='중', fam='a',
                  steps=['맥놀이 진동수 = %d - %d = %d Hz 이다.' % (f2, f1, d), '%d초 동안의 횟수 = %d × %d = %d회 이다.' % (t, d, t, n)],
                  core='맥놀이 횟수 = |f₁ - f₂| × 시간.', point='맥놀이 진동수에 시간을 곱한다.')
    if form == 'graph':
        f1 = r.choice([100, 120, 150, 200])
        df = r.choice([20, 25, 30, 40, 50])
        if (f1 + df / 2) / df > 7.5: return None
        f2 = f1 + df
        Tb = Fr(1000, df)
        ticks = [float(Tb) * i / 2 for i in range(1, 5)]
        ticks = [round(t, 3) for t in ticks]
        fig = FIG(beat_fig(f1, f2, ticks, 2), '74%')
        ask = r.choice(['fb', 'f2', 'Tb'])
        base = '그림은 진동수가 약간 다른 두 소리 A, B가 동시에 날 때 합성된 소리의 변위(파란색)와 그 진폭의 변화(빨간 점선)를 시간에 따라 나타낸 것이다. 소리 A의 진동수는 %d Hz이고 B의 진동수는 A보다 크다. ' % f1
        if ask == 'fb':
            body = P(base + '이때 맥놀이 진동수는?') + fig
            wr = [Fr(df, 2), df * 2, f1 + df, Fr(df + f1), df + 10]
            return mc(body, '%d Hz' % df, ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['소리가 가장 커지는 순간은 t = 0 과 t = %s ms 이므로 맥놀이 주기 = %s ms = %s s 이다.' % (fn(Tb), fn(Tb), fn(Tb / 1000)), '맥놀이 진동수 = 1/%s = %d Hz 이다.' % (fn(Tb / 1000), df)],
                      core='합성음의 진폭이 최대가 되는 시간 간격이 맥놀이 주기이다.', point='그래프에서 맥놀이 주기를 읽어 진동수로 환산한다.')
        if ask == 'f2':
            body = P(base + 'B의 진동수는?') + fig
            wr = [f1 - df, f1 + 2 * df, f1 + df // 2, df, f1 + df + 10]
            return mc(body, '%d Hz' % f2, ['%d Hz' % w for w in wr], r=r, lv='상', fam='b',
                      steps=['소리가 가장 커지는 시간 간격(맥놀이 주기)이 %s ms 이므로 맥놀이 진동수는 %d Hz 이다.' % (fn(Tb), df), 'f_B = f_A + %d = %d + %d = %d Hz 이다.' % (df, f1, df, f2)],
                      core='f_B = f_A + f_beat (B가 더 클 때).', point='그래프에서 맥놀이 진동수를 읽어 B의 진동수를 구한다.')
        body = P(base + '이 맥놀이가 한 번 반복되는 데 걸리는 시간은?') + fig
        wr = [Tb * 2, Tb / 2, Tb * 4, Fr(1000, f1), Tb + 10]
        return mc(body, '%s ms' % fn(Tb), ['%s ms' % fn(w) for w in wr], r=r, lv='중', fam='b',
                  steps=['합성음의 진폭이 최대인 순간은 t = 0, %s ms, %s ms 이다.' % (fn(Tb), fn(Tb * 2)), '맥놀이 주기 = %s ms 이다. (= 1/|f_B - f_A| = 1/%d s)' % (fn(Tb), df)],
                  core='맥놀이 주기는 합성음의 진폭이 최대가 되는 시간 간격이다.', point='그래프에서 맥놀이 주기를 읽는다.')
    # tune
    f0 = r.choice([256, 330, 440, 523])
    n = r.choice([2, 3, 4, 5, 6])
    ev = r.choice(['tighten', 'loosen', 'wax'])
    if ev == 'tighten':
        more = r.choice([True, False])
        # 줄을 조이면 f 증가. 맥놀이가 증가 → f>f0 이어서 더 멀어짐 → 원래 f = f0 + n. 감소 → f<f0 → f = f0 - n.
        orig = f0 + n if more else f0 - n
        body = P('진동수 %d Hz인 소리굽쇠와 현악기의 줄을 동시에 울렸더니 1초에 %d번의 맥놀이가 들렸다. 줄의 장력을 조금 크게 했더니 맥놀이가 %s. 장력을 조절하기 전 줄이 내는 소리의 진동수는?' % (f0, n, '더 빨라졌다' if more else '더 느려졌다'))
        stp = ['처음 줄의 진동수는 %d ± %d Hz 이다.' % (f0, n), '장력을 크게 하면 줄의 진동수가 커진다.',
               ('맥놀이가 빨라졌으므로 진동수 차가 커진 것이다 → 줄의 진동수가 소리굽쇠보다 컸다.' if more else '맥놀이가 느려졌으므로 진동수 차가 작아진 것이다 → 줄의 진동수가 소리굽쇠보다 작았다.'), '따라서 처음 진동수는 %d Hz 이다.' % orig]
    elif ev == 'loosen':
        more = r.choice([True, False])
        # 장력을 줄이면 f 감소. 맥놀이 증가 → f < f0 → orig = f0 - n; 감소 → f > f0 → orig = f0 + n.
        orig = f0 - n if more else f0 + n
        body = P('진동수 %d Hz인 소리굽쇠와 현악기의 줄을 동시에 울렸더니 1초에 %d번의 맥놀이가 들렸다. 줄의 장력을 조금 작게 했더니 맥놀이가 %s. 장력을 조절하기 전 줄이 내는 소리의 진동수는?' % (f0, n, '더 빨라졌다' if more else '더 느려졌다'))
        stp = ['처음 줄의 진동수는 %d ± %d Hz 이다.' % (f0, n), '장력을 작게 하면 줄의 진동수가 작아진다.',
               ('맥놀이가 빨라졌으므로 진동수 차가 커진 것이다 → 줄의 진동수가 소리굽쇠보다 작았다.' if more else '맥놀이가 느려졌으므로 진동수 차가 작아진 것이다 → 줄의 진동수가 소리굽쇠보다 컸다.'), '따라서 처음 진동수는 %d Hz 이다.' % orig]
    else:
        more = r.choice([True, False])
        # 소리굽쇠에 왁스를 붙이면 f0 감소. 맥놀이 증가 → 줄 진동수가 f0 보다 작았다.
        orig = f0 - n if more else f0 + n
        body = P('진동수가 %d Hz인 소리굽쇠와 진동수를 모르는 소리 X를 동시에 냈더니 1초에 %d번의 맥놀이가 들렸다. 소리굽쇠의 가지에 작은 왁스 덩어리를 붙여 진동수를 조금 낮추었더니 맥놀이가 %s. 소리 X의 진동수는?' % (f0, n, '더 빨라졌다' if more else '더 느려졌다'))
        stp = ['소리 X의 진동수는 %d ± %d Hz 이다.' % (f0, n), '왁스를 붙이면 소리굽쇠의 진동수가 작아진다.',
               ('맥놀이가 빨라졌으므로 진동수 차가 커진 것이다 → X의 진동수가 소리굽쇠보다 작다.' if more else '맥놀이가 느려졌으므로 진동수 차가 작아진 것이다 → X의 진동수가 소리굽쇠보다 크다.'), '따라서 X의 진동수는 %d Hz 이다.' % orig]
    wr = [f0 + n if orig != f0 + n else f0 - n, f0, f0 + 2 * n, f0 - 2 * n, n, f0 + n + 1]
    return mc(body, '%d Hz' % orig, ['%d Hz' % w for w in wr], r=r, lv='상', fam='c', steps=stp,
              core='진동수를 바꿨을 때 맥놀이 진동수가 증가하면 진동수 차가 커진 것이고 감소하면 차가 작아진 것이다.', point='진동수 변화 방향과 맥놀이 변화로 원래 진동수를 추론한다.')


# ================================================================== ph102 줄의 정상파와 진동수
@T('ph102')
def ph102(r, k):
    form = r.choice(['calc', 'calc', 'fig', 'fig', 'fig', 'cond', 'cond', 'succ'])
    if form == 'calc':
        sub_ = r.choice(['f', 'v', 'n', 'lam'])
        L = Fr(str(r.choice([0.5, 0.6, 0.8, 1, 1.2, 1.5, 2, 2.4])))
        n = r.choice([1, 2, 3, 4, 5])
        v = Fr(r.choice([40, 60, 80, 100, 120, 150, 200, 240, 300]))
        f = n * v / (2 * L)
        lam = 2 * L / n
        if not term(f) or not term(lam): return None
        if sub_ == 'f':
            body = P('양 끝이 고정된 길이 %s m의 줄에서 파동의 속력이 %s m/s일 때, %d배 진동(n = %d)의 정상파가 만들어지는 진동수는?' % (fn(L), fn(v), n, n) if False else
                     '양 끝이 고정된 길이 %s m의 줄에서 파동의 속력이 %s m/s이다. 줄에 n = %d 인 정상파(배가 %d개)가 생길 때 진동수는?' % (fn(L), fn(v), n, n))
            wr = [f * 2, f / 2, v / (2 * L) if n != 1 else f + 10, n * v / L, v / L * n * 2 if False else f + v / 10, f + 20]
            return mc(body, '%s Hz' % fn(f), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['정상파의 파장 λ = 2L/n = 2 × %s / %d = %s m 이다.' % (fn(L), n, fn(lam)), 'f = v/λ = %s / %s = %s Hz 이다. (f = nv/2L)' % (fn(v), fn(lam), fn(f))],
                      core='양 끝 고정 줄: λ = 2L/n, f = nv/2L.', point='정상파의 파장 조건에서 진동수를 구한다.')
        if sub_ == 'v':
            body = P('양 끝이 고정된 길이 %s m의 줄에 n = %d 인 정상파(배가 %d개)가 생겼고 진동수는 %s Hz이다. 줄을 따라 진행하는 파동의 속력은?' % (fn(L), n, n, fn(f)))
            wr = [v * 2, v / 2, f * L, f * L * 2 / 1 if False else f * L / n, f * 2 * L * n, v + 20]
            return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['λ = 2L/n = 2 × %s / %d = %s m 이다.' % (fn(L), n, fn(lam)), 'v = fλ = %s × %s = %s m/s 이다.' % (fn(f), fn(lam), fn(v))],
                      core='v = fλ, λ = 2L/n.', point='진동수와 파장 조건으로 속력을 구한다.')
        if sub_ == 'n':
            body = P('양 끝이 고정된 길이 %s m의 줄에서 파동의 속력이 %s m/s이다. 진동수 %s Hz로 줄을 진동시킬 때 생기는 정상파에서 배의 개수는?' % (fn(L), fn(v), fn(f)))
            wr = [n + 1, n - 1 if n > 1 else n + 2, n * 2, n + 2, max(n // 2, 1) if n // 2 != n else n + 3]
            return mc(body, '%d개' % n, ['%d개' % w for w in wr], r=r, lv='중', fam='a',
                      steps=['λ = v/f = %s / %s = %s m 이다.' % (fn(v), fn(f), fn(v / f)), 'L = nλ/2 에서 n = 2L/λ = 2 × %s / %s = %d 이므로 배는 %d개이다.' % (fn(L), fn(v / f), n, n)],
                      core='줄 길이 L = nλ/2 (배의 수 n).', point='파장으로 배의 개수를 구한다.')
        body = P('양 끝이 고정된 길이 %s m의 줄에 n = %d 인 정상파(배가 %d개)가 생겼다. 이 정상파의 파장은?' % (fn(L), n, n))
        wr = [lam * 2, lam / 2, L, L / n * 2 if False else L * n, L / n * 4 if False else lam + 0.5]
        return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='하', fam='a',
                  steps=['L = nλ/2 에서 λ = 2L/n = 2 × %s / %d = %s m 이다.' % (fn(L), n, fn(lam))],
                  core='양 끝 고정 줄의 정상파는 L = nλ/2.', point='배의 수로 파장을 구한다.')
    if form == 'fig':
        n = r.choice([1, 2, 3, 4, 5])
        L = Fr(str(r.choice([0.6, 0.8, 1, 1.2, 1.5, 2, 2.4, 3])))
        lam = 2 * L / n
        if not term(lam): return None
        fig = FIG(string_fig(n, 'L = %s m' % fn(L)), '70%')
        ask = r.choice(['v', 'f', 'lam', 'cnt'])
        base = '그림은 양 끝이 고정된 줄에 생긴 정상파를 나타낸 것이다. 줄의 길이는 %s m이다. ' % fn(L)
        if ask == 'lam':
            body = P(base + '이 정상파의 파장은?') + fig
            wr = [lam * 2, lam / 2, L, L * 2, L / (n + 1) * 2]
            return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['그림에서 배가 %d개(반 파장이 %d개)이므로 L = %d × λ/2 이다.' % (n, n, n), 'λ = 2L/%d = %s m 이다.' % (n, fn(lam))],
                      core='배 1개가 반 파장이다.', point='그림의 배의 수로 파장을 구한다.')
        if ask == 'cnt':
            body = P(base + '이 정상파에서 마디의 수(양 끝 포함)와 배의 수를 옳게 짝지은 것은?') + fig
            right = '마디 %d개, 배 %d개' % (n + 1, n)
            wr = ['마디 %d개, 배 %d개' % (n, n + 1), '마디 %d개, 배 %d개' % (n, n), '마디 %d개, 배 %d개' % (n + 1, n + 1), '마디 %d개, 배 %d개' % (n + 2, n), '마디 %d개, 배 %d개' % (n + 1, n - 1 if n > 1 else n + 2)]
            return mc(body, right, wr, r=r, lv='하', fam='b', sort='shuf',
                      steps=['그림에서 배(진폭이 최대인 곳)는 %d개, 마디(변위가 항상 0인 곳)는 양 끝을 포함해 %d개이다.' % (n, n + 1)],
                      core='양 끝 고정 줄의 정상파에서 마디 수 = 배 수 + 1.', point='그림에서 마디와 배를 센다.')
        if ask == 'v':
            f = Fr(r.choice([20, 30, 40, 50, 60, 80, 100, 120, 150, 200]))
            v = f * lam
            if not term(v): return None
            body = P(base + '이 정상파의 진동수가 %s Hz일 때 줄을 따라 진행하는 파동의 속력은?' % fn(f)) + fig
            wr = [v * 2, v / 2, f * L, f * L * 2 / n * 2 if False else f * L / n, f * L * n, v + 10]
            return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['배가 %d개이므로 λ = 2L/%d = %s m 이다.' % (n, n, fn(lam)), 'v = fλ = %s × %s = %s m/s 이다.' % (fn(f), fn(lam), fn(v))],
                      core='그림에서 파장을 구한 뒤 v = fλ.', point='정상파 그림으로 파장을 읽어 속력을 구한다.')
        v = Fr(r.choice([40, 60, 80, 100, 120, 150, 200, 240, 300]))
        f = v / lam
        if not term(f): return None
        body = P(base + '줄을 따라 진행하는 파동의 속력이 %s m/s일 때 이 정상파의 진동수는?' % fn(v)) + fig
        wr = [f * 2, f / 2, v / L, v / (2 * L) if n != 1 else f + 5, f + 10]
        return mc(body, '%s Hz' % fn(f), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='b',
                  steps=['배가 %d개이므로 λ = 2L/%d = %s m 이다.' % (n, n, fn(lam)), 'f = v/λ = %s / %s = %s Hz 이다.' % (fn(v), fn(lam), fn(f))],
                  core='그림에서 파장을 구한 뒤 f = v/λ.', point='정상파 그림으로 파장을 읽어 진동수를 구한다.')
    if form == 'cond':
        kind = r.choice(['T', 'L', 'n', 'mu'])
        if kind == 'T':
            a = r.choice([4, 9, 16, 25])
            body = P('양 끝이 고정된 줄에서 기본 진동수는 f₁이다. 줄의 길이와 단위 길이당 질량은 그대로 두고 줄을 팽팽하게 당겨 장력을 %d배로 하면 기본 진동수는?' % a)
            q = Fr(math.isqrt(a))
            right = '%sf₁' % fn(q)
            wr = ['%sf₁' % fn(w) for w in (Fr(a), q * 2, 1 / q, Fr(1, a), q + 1)]
            return mc(body, right, wr, r=r, lv='상', fam='c', sort='shuf',
                      steps=['v = √(T/μ) 이므로 장력이 %d배이면 파동의 속력은 √%d = %s배이다.' % (a, a, fn(q)), 'f₁ = v/2L 이므로 기본 진동수도 %s배, 즉 %sf₁ 이다.' % (fn(q), fn(q))],
                      core='줄의 파동 속력 v = √(T/μ), 기본 진동수 f₁ = v/2L.', point='장력 변화가 속력과 진동수에 주는 영향을 구한다.')
        if kind == 'L':
            a = r.choice([2, 3, 4, 5])
            body = P('양 끝이 고정된 줄의 기본 진동수가 f₁이다. 줄의 중간을 손가락으로 눌러 진동하는 줄의 길이를 처음의 1/%d로 하면(장력은 일정) 기본 진동수는?' % a)
            right = '%df₁' % a
            wr = ['%df₁' % w for w in (a * a, a + 1, a * 2 if a != 2 else 5)] + ['f₁/%d' % a, 'f₁']
            return mc(body, right, wr, r=r, lv='중', fam='c', sort='shuf',
                      steps=['v는 일정하므로 f₁ = v/2L 은 L에 반비례한다.', 'L이 1/%d배이므로 f₁은 %d배가 된다.' % (a, a)],
                      core='f₁ = v/2L 이므로 줄이 짧아질수록 진동수가 커진다.', point='줄의 길이와 기본 진동수의 반비례 관계.')
        if kind == 'n':
            n = r.choice([2, 3, 4, 5])
            f1 = Fr(r.choice([20, 30, 40, 50, 60, 100]))
            body = P('양 끝이 고정된 줄의 기본 진동수가 %s Hz이다. 같은 줄에서 진동수가 %s Hz인 정상파가 생길 때 배의 수는?' % (fn(f1), fn(f1 * n)))
            wr = [n + 1, n - 1, n * 2, n + 2, max(n // 2, 1) if n // 2 != n else n + 3]
            return mc(body, '%d개' % n, ['%d개' % w for w in wr], r=r, lv='중', fam='c',
                      steps=['f_n = n f₁ 이므로 n = %s / %s = %d 이다.' % (fn(f1 * n), fn(f1), n), '배의 수는 n = %d 개(마디는 %d개)이다.' % (n, n + 1)],
                      core='양 끝 고정 줄의 정상파 진동수 f_n = n f₁ (n = 배의 수).', point='진동수 비로 배의 수를 구한다.')
        a = r.choice([4, 9, 16])
        body = P('양 끝이 고정되고 장력이 같은 두 줄 A, B가 있다. 길이는 같고 줄의 단위 길이당 질량은 B가 A의 %d배이다. 각 줄의 기본 진동수의 비 f%s : f%s는?' % (a, sub('A'), sub('B')))
        q = Fr(math.isqrt(a))
        right = ratio_str(q, 1)
        wr = [ratio_str(1, q), ratio_str(a, 1), ratio_str(1, a), '1 : 1', ratio_str(q + 1, 1)]
        return mc(body, right, wr, r=r, lv='상', fam='c', sort='shuf',
                  steps=['v = √(T/μ) 이고 μ%s = %dμ%s 이므로 v%s : v%s = √%d : 1 = %s : 1 이다.' % (sub('B'), a, sub('A'), sub('A'), sub('B'), a, fn(q)), '길이가 같으므로 f₁ = v/2L 에 의해 f%s : f%s = %s 이다.' % (sub('A'), sub('B'), right)],
                  core='v = √(T/μ), f₁ = v/2L.', point='선밀도 변화가 진동수에 주는 영향을 비로 구한다.')
    # succ: 인접한 두 공명 진동수
    f1 = Fr(r.choice([20, 25, 30, 40, 50, 60, 80, 100]))
    n = r.choice([2, 3, 4, 5, 6])
    L = Fr(str(r.choice([0.5, 0.6, 0.8, 1, 1.2, 1.5, 2])))
    fa, fb = n * f1, (n + 1) * f1
    v = 2 * L * f1
    if not term(v): return None
    ask = r.choice(['v', 'f1'])
    base = '양 끝이 고정된 길이 %s m의 줄에서 정상파가 생기는 진동수 중 인접한 두 진동수가 %s Hz와 %s Hz이다. ' % (fn(L), fn(fa), fn(fb))
    if ask == 'f1':
        body = P(base + '이 줄의 기본 진동수는?')
        wr = [fa + fb, f1 * 2, f1 / 2, fa, fb]
        return mc(body, '%s Hz' % fn(f1), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='d',
                  steps=['f_n = n f₁ 이므로 인접한 두 진동수의 차가 f₁ 이다.', 'f₁ = %s - %s = %s Hz 이다.' % (fn(fb), fn(fa), fn(f1))],
                  core='양 끝 고정 줄에서 인접한 공명 진동수의 차는 기본 진동수와 같다.', point='인접한 두 진동수의 차이로 기본 진동수를 구한다.')
    body = P(base + '이 줄을 따라 진행하는 파동의 속력은?')
    wr = [v * 2, v / 2, f1 * L, fa * 2 * L / n * 2 if False else fb * L, v + 10]
    return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='상', fam='d',
              steps=['기본 진동수 f₁ = %s - %s = %s Hz 이다.' % (fn(fb), fn(fa), fn(f1)), 'f₁ = v/2L 에서 v = 2Lf₁ = 2 × %s × %s = %s m/s 이다.' % (fn(L), fn(f1), fn(v))],
              core='f₁ = v/2L 과 인접 진동수 차 = f₁.', point='기본 진동수를 구한 뒤 속력을 구한다.')


# ================================================================== ph103 관의 공명(닫힌 관·열린 관)
_B103 = [
    ('닫힌 관에서 닫힌 끝은 정상파의 마디가 된다.', True, '닫힌 끝에서는 공기가 움직일 수 없어 변위가 0이다.', 'closed'),
    ('닫힌 관에서 닫힌 끝은 정상파의 배가 된다.', False, '닫힌 끝은 마디, 열린 끝은 배이다.', 'closed'),
    ('열린 끝은 정상파의 배가 된다.', True, '열린 끝에서 공기가 자유롭게 진동한다.', 'open'),
    ('닫힌 관에서 가장 낮은 공명 진동수(기본 진동수)의 파장은 관 길이의 4배이다.', True, 'L = λ/4 이므로 λ = 4L 이다.', 'lam4'),
    ('닫힌 관에서 기본 진동수의 파장은 관 길이의 2배이다.', False, '닫힌 관에서는 L = λ/4 이므로 λ = 4L 이다.', 'lam4'),
    ('양 끝이 열린 관에서 기본 진동수의 파장은 관 길이의 2배이다.', True, 'L = λ/2 이므로 λ = 2L 이다.', 'lam2'),
    ('같은 길이의 열린 관과 닫힌 관에서 열린 관의 기본 진동수가 더 크다.', True, 'f 열림 = v/2L, f 닫힘 = v/4L 이므로 열린 관이 2배이다.', 'cmp'),
    ('같은 길이의 닫힌 관의 기본 진동수는 열린 관의 2배이다.', False, '닫힌 관은 v/4L 로 열린 관(v/2L)의 절반이다.', 'cmp'),
    ('닫힌 관에서는 기본 진동수의 짝수 배 진동수에서도 공명이 일어난다.', False, '닫힌 관은 홀수 배(f₁, 3f₁, 5f₁, …)에서만 공명한다.', 'odd'),
    ('닫힌 관에서는 기본 진동수의 홀수 배 진동수에서만 공명한다.', True, 'f = (2n - 1) v/4L 이다.', 'odd'),
    ('열린 관에서는 기본 진동수의 정수 배 진동수에서 공명한다.', True, 'f = n v/2L 이다.', 'int'),
    ('공명은 관 속 공기 기둥의 고유 진동수와 외부 소리의 진동수가 같을 때 소리가 크게 들리는 현상이다.', True, '고유 진동수와 일치할 때 공명한다.', 'res'),
    ('기주 공명 실험에서 연이은 두 공명 위치 사이의 거리는 반 파장이다.', True, '닫힌 관에서 L₂ - L₁ = 3λ/4 - λ/4 = λ/2 이다.', 'exp'),
    ('기주 공명 실험에서 연이은 두 공명 위치 사이의 거리는 한 파장이다.', False, '연이은 공명 위치 사이의 거리는 반 파장이다.', 'exp'),
    ('관의 길이가 길수록 기본 진동수는 작아진다.', True, 'f₁ ∝ 1/L 이다.', 'len'),
    ('관의 열린 끝에서는 압력 변화가 최대이다.', False, '열린 끝은 변위의 배이며 압력 변화는 최소(마디)이다.', 'press'),
    ('관 안의 공기의 온도가 높아지면 같은 관의 기본 진동수는 커진다.', True, '소리의 속력이 커져 f = v/4L 가 커진다.', 'temp'),
    ('관악기는 관 속 공기 기둥의 공명을 이용해 소리를 낸다.', True, '관의 길이를 조절해 음높이를 바꾼다.', 'inst'),
]


@T('ph103')
def ph103(r, k):
    form = r.choice(['calc', 'exp', 'exp', 'exp', 'fig', 'fig', 'ratio', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B103)
        if not s: return None
        return bogi('관의 공명에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='e', r=r,
                    core='닫힌 관: 닫힌 끝 마디·열린 끝 배, L = (2n-1)λ/4. 열린 관: 양 끝 배, L = nλ/2.', point='관의 끝 조건과 공명 조건을 판단한다.')
    if form == 'calc':
        kind = r.choice(['closed', 'open'])
        L = Fr(str(r.choice([0.17, 0.2, 0.25, 0.34, 0.425, 0.5, 0.68, 0.85, 1.7])))
        f1 = Fr(V) / (4 * L) if kind == 'closed' else Fr(V) / (2 * L)
        if not term(f1): return None
        ask = r.choice(['f', 'L'])
        nm = '한쪽 끝이 막힌 닫힌 관' if kind == 'closed' else '양 끝이 열린 관'
        fm = 'f₁ = v/4L' if kind == 'closed' else 'f₁ = v/2L'
        if ask == 'f':
            body = P('길이 %s m의 %s에서 소리의 속력이 340 m/s일 때, 기본 진동수(가장 낮은 공명 진동수)는?' % (fn(L), nm))
            alt = Fr(V) / (2 * L) if kind == 'closed' else Fr(V) / (4 * L)
            wr = [alt, f1 * 2 if kind == 'closed' else f1 * 3, f1 * 4, Fr(V) / L, Fr(V) * L, f1 + 50]
            return mc(body, '%s Hz' % fn(f1), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['%s의 기본 진동수는 %s 이다.' % (nm, fm), 'f₁ = 340 / (%s × %s) = %s Hz 이다.' % ('4' if kind == 'closed' else '2', fn(L), fn(f1))],
                      core='닫힌 관 f₁ = v/4L, 열린 관 f₁ = v/2L.', point='관의 종류에 맞는 공식을 쓴다.')
        body = P('%s에서 소리의 속력이 340 m/s이고 기본 진동수가 %s Hz이다. 관의 길이는?' % (nm, fn(f1)))
        alt = Fr(V) / (2 * f1) if kind == 'closed' else Fr(V) / (4 * f1)
        wr = [alt, L * 2, L / 2, L * 4, Fr(V) / f1]
        return mc(body, '%s m' % fn(L), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='a',
                  steps=['%s: %s 에서 L = v/%sf₁ 이다.' % (nm, fm, '4' if kind == 'closed' else '2'), 'L = 340 / (%s × %s) = %s m 이다.' % ('4' if kind == 'closed' else '2', fn(f1), fn(L))],
                  core='닫힌 관 L = λ/4, 열린 관 L = λ/2 (기본음).', point='기본 진동수로 관의 길이를 구한다.')
    if form == 'exp':
        f = r.choice([25, 50, 85, 100, 125, 170, 250, 340, 500, 850, 1700])
        lam = Fr(V, f)
        L1 = lam / 4
        L2 = 3 * lam / 4
        if not term(L1) or not term(L2): return None
        ask = r.choice(['v', 'lam', 'L2', 'L1'])
        head = '그림과 같이 한쪽이 열린 유리관의 물 높이를 조절하며 진동수 %d Hz인 소리굽쇠를 관 입구에 대고 공명 위치를 찾았다. ' % f
        if ask == 'v':
            vv = Fr(V)
            body = P(head + '물 높이를 낮추어 가며 첫 번째 공명이 일어난 공기 기둥의 길이가 %s m, 두 번째 공명이 일어난 길이가 %s m 이었다. 이 실험으로 구한 소리의 속력은? (단, 관 끝의 보정은 무시한다.)' % (fn(L1), fn(L2)))
            v_ = 2 * f * (L2 - L1)
            assert v_ == vv
            wr = [f * (L2 - L1), 4 * f * L1 * 2 if False else 4 * f * (L2 - L1), f * L1 * 2, f * L2 * 2, f * (L2 + L1)]
            return mc(body, '%s m/s' % fn(vv), ['%s m/s' % fn(w) for w in wr], r=r, lv='상', fam='b',
                      steps=['연이은 두 공명 위치 사이의 거리는 반 파장이다 : λ/2 = %s - %s = %s m → λ = %s m 이다.' % (fn(L2), fn(L1), fn(L2 - L1), fn(lam)), 'v = fλ = %d × %s = %s m/s 이다.' % (f, fn(lam), fn(vv))],
                      core='닫힌 관에서 L₂ - L₁ = λ/2, v = fλ.', point='두 공명 위치의 차로 파장과 속력을 구한다.')
        if ask == 'lam':
            body = P(head + '첫 번째 공명이 일어난 공기 기둥의 길이가 %s m일 때 소리의 파장은? (단, 관 끝의 보정은 무시한다.)' % fn(L1))
            wr = [L1 * 2, L1 * 8, L1 * 3, L1, L1 * 4 / 3]
            return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['첫 번째 공명에서 L₁ = λ/4 이므로 λ = 4L₁ = 4 × %s = %s m 이다.' % (fn(L1), fn(lam))],
                      core='닫힌 관의 첫 공명: L₁ = λ/4.', point='첫 공명에서 파장을 구한다.')
        if ask == 'L2':
            body = P(head + '소리의 속력이 340 m/s일 때, 첫 번째 공명과 두 번째 공명이 일어나는 공기 기둥의 길이 L₁, L₂를 각각 구한 것은?')
            right = '%s m, %s m' % (fn(L1), fn(L2))
            wr = ['%s m, %s m' % (fn(L1), fn(2 * L1)), '%s m, %s m' % (fn(lam / 2), fn(lam)), '%s m, %s m' % (fn(L1), fn(5 * lam / 4)), '%s m, %s m' % (fn(lam / 2), fn(3 * lam / 2)), '%s m, %s m' % (fn(L2), fn(L1))]
            return mc(body, right, wr, r=r, lv='상', fam='b', sort='shuf',
                      steps=['λ = v/f = 340 / %d = %s m 이다.' % (f, fn(lam)), 'L₁ = λ/4 = %s m, L₂ = 3λ/4 = %s m 이다.' % (fn(L1), fn(L2))],
                      core='닫힌 관의 공명: L = λ/4, 3λ/4, 5λ/4, ….', point='진동수에서 파장을 구해 공명 길이를 구한다.')
        body = P(head + '소리의 속력이 340 m/s일 때, 두 번째 공명이 일어나는 공기 기둥의 길이는? (단, 관 끝의 보정은 무시한다.)')
        wr = [L1, lam / 2, lam, 5 * lam / 4, L2 * 2]
        return mc(body, '%s m' % fn(L2), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='b',
                  steps=['λ = v/f = 340 / %d = %s m 이다.' % (f, fn(lam)), '두 번째 공명: L₂ = 3λ/4 = %s m 이다.' % fn(L2)],
                  core='닫힌 관의 두 번째 공명 L₂ = 3λ/4.', point='공명 조건 L = (2n-1)λ/4 를 쓴다.') if ask == 'L1' else None
    if form == 'fig':
        kind = r.choice(['closed', 'open'])
        n = r.choice([1, 2, 3]) if kind == 'closed' else r.choice([1, 2, 3, 4])
        L = Fr(str(r.choice([0.17, 0.34, 0.5, 0.68, 0.85, 1.7, 1, 2])))
        lam = 4 * L / (2 * n - 1) if kind == 'closed' else 2 * L / n
        f = Fr(V) / lam
        if not term(f) or not term(lam): return None
        fig = FIG(pipe_fig(kind, n, 'L = %s m' % fn(L)), '70%')
        ask = r.choice(['lam', 'f', 'cnt'])
        nm = '한쪽 끝이 막힌 관' if kind == 'closed' else '양 끝이 열린 관'
        base = '그림은 %s 속에 정상파(공기 입자의 변위)가 생긴 모습을 나타낸 것이다. 관의 길이는 %s m이고 소리의 속력은 340 m/s이다. ' % (nm, fn(L))
        if ask == 'lam':
            body = P(base + '이 소리의 파장은?') + fig
            alt = 2 * L / n if kind == 'closed' else 4 * L / (2 * n - 1)
            wr = [alt, lam * 2, lam / 2, L, L * 4]
            fm = ('L = (2n - 1)λ/4, n = %d' % n) if kind == 'closed' else 'L = nλ/2, n = %d' % n
            return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='c',
                      steps=['그림에서 %s이므로 %s 이다.' % ('닫힌 끝은 마디, 열린 끝은 배이고 배가 %d개' % n if kind == 'closed' else '양 끝이 배이고 마디가 %d개' % n, fm), 'λ = %s m 이다.' % fn(lam)],
                      core='관의 끝 조건(닫힌 끝: 마디, 열린 끝: 배)과 그림의 배·마디 수로 L과 λ의 관계를 구한다.', point='그림에서 L과 파장의 관계를 읽는다.')
        if ask == 'f':
            body = P(base + '이 정상파의 진동수는?') + fig
            alt = Fr(V) / (4 * L) if kind == 'closed' else Fr(V) / (2 * L)
            wr = [alt, f * 2, f / 2, Fr(V) / L, f + 50]
            return mc(body, '%s Hz' % fn(f), ['%s Hz' % fn(w) for w in wr], r=r, lv='상', fam='c',
                      steps=['그림에서 %s. 따라서 λ = %s m 이다.' % (('L = (2n - 1)λ/4 (n = %d)' % n) if kind == 'closed' else 'L = nλ/2 (n = %d)' % n, fn(lam)), 'f = v/λ = 340 / %s = %s Hz 이다.' % (fn(lam), fn(f))],
                      core='f = v/λ 와 관의 공명 조건.', point='그림으로 파장을 구해 진동수를 계산한다.')
        if kind == 'closed':
            right = '마디 %d개, 배 %d개' % (n, n)
        else:
            right = '마디 %d개, 배 %d개' % (n, n + 1)
        body = P(base + '이 정상파에서 마디의 수와 배의 수(관의 양 끝 포함)를 옳게 짝지은 것은?') + fig
        pool = ['마디 %d개, 배 %d개' % (a, b) for a in range(max(n - 1, 1), n + 3) for b in range(max(n - 1, 1), n + 3)]
        wr = [p for p in pool if p != right]
        return mc(body, right, wr, r=r, lv='하', fam='c', sort='shuf',
                  steps=['그림에서 변위가 항상 0인 마디와 진폭이 최대인 배를 센다.', right + ' 이다.'],
                  core='닫힌 관은 한쪽 끝이 마디·다른 쪽이 배, 열린 관은 양 끝이 배이다.', point='그림에서 마디와 배의 개수를 센다.')
    # ratio
    sub_ = r.choice(['same', 'second', 'cl_op'])
    if sub_ == 'same':
        a = r.choice([2, 3, 4])
        body = P('길이가 L로 같은 닫힌 관 A와 열린 관 B에서 각각 기본 진동수로 공명한다. 기본 진동수의 비 f%s : f%s는?' % (sub('A'), sub('B')))
        right = '1 : 2'
        wr = ['2 : 1', '1 : 1', '1 : 4', '4 : 1', '1 : 3']
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf', steps=['닫힌 관 f₁ = v/4L, 열린 관 f₁ = v/2L 이므로 f%s : f%s = 1/4 : 1/2 = 1 : 2 이다.' % (sub('A'), sub('B'))],
                  core='같은 길이에서 열린 관의 기본 진동수가 닫힌 관의 2배이다.', point='두 관의 기본 진동수를 비교한다.')
    if sub_ == 'second':
        kind = r.choice(['closed', 'open'])
        f1 = Fr(r.choice([85, 100, 125, 170, 200, 250, 340]))
        if kind == 'closed':
            body = P('한쪽 끝이 막힌 관의 기본 진동수가 %s Hz이다. 이 관에서 두 번째로 낮은 공명 진동수는?' % fn(f1))
            f2 = 3 * f1
            wr = [2 * f1, 4 * f1, 5 * f1, f1 + 100, f1 / 2]
            return mc(body, '%s Hz' % fn(f2), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='d',
                      steps=['닫힌 관은 홀수 배 진동수에서 공명한다: f₁, 3f₁, 5f₁, … ', '두 번째로 낮은 공명 진동수 = 3 × %s = %s Hz 이다.' % (fn(f1), fn(f2))],
                      core='닫힌 관의 공명 진동수는 f₁의 홀수 배이다.', point='닫힌 관과 열린 관의 공명열을 구분한다.')
        body = P('양 끝이 열린 관의 기본 진동수가 %s Hz이다. 이 관에서 두 번째로 낮은 공명 진동수는?' % fn(f1))
        f2 = 2 * f1
        wr = [3 * f1, 4 * f1, f1 / 2, f1 + 100, 5 * f1]
        return mc(body, '%s Hz' % fn(f2), ['%s Hz' % fn(w) for w in wr], r=r, lv='하', fam='d',
                  steps=['열린 관은 정수 배 진동수에서 공명한다: f₁, 2f₁, 3f₁, … ', '두 번째로 낮은 공명 진동수 = 2 × %s = %s Hz 이다.' % (fn(f1), fn(f2))],
                  core='열린 관의 공명 진동수는 f₁의 정수 배이다.', point='열린 관의 공명열을 안다.')
    L = Fr(str(r.choice([0.5, 0.85, 1, 1.7])))
    fc = Fr(V) / (4 * L)
    fo = Fr(V) / (2 * L)
    if not term(fc): return None
    body = P('길이 %s m의 닫힌 관의 기본 진동수와, 같은 길이의 열린 관의 기본 진동수의 차는? (단, 소리의 속력은 340 m/s이다.)' % fn(L))
    right = fo - fc
    wr = [fo + fc, fc, fo, right * 2, right / 2]
    return mc(body, '%s Hz' % fn(right), ['%s Hz' % fn(w) for w in wr], r=r, lv='상', fam='d',
              steps=['닫힌 관: f₁ = 340/(4 × %s) = %s Hz 이다.' % (fn(L), fn(fc)), '열린 관: f₁ = 340/(2 × %s) = %s Hz 이다.' % (fn(L), fn(fo)), '차 = %s - %s = %s Hz 이다.' % (fn(fo), fn(fc), fn(right))],
              core='닫힌 관 f₁ = v/4L, 열린 관 f₁ = v/2L.', point='두 관의 기본 진동수를 각각 구해 비교한다.')


# ================================================================== ph104 초음파와 소리의 간섭 응용
_B104 = [
    ('초음파는 진동수가 20000 Hz보다 큰 소리로 사람이 들을 수 없다.', True, '가청 진동수 범위(20~20000 Hz)를 넘는다.', 'def'),
    ('초음파는 진동수가 20 Hz보다 작은 소리이다.', False, '20 Hz 미만은 초저주파이고 초음파는 20000 Hz 이상이다.', 'def'),
    ('초음파는 종파이다.', True, '소리의 한 종류로 종파이다.', 'long'),
    ('초음파는 진공에서도 전달된다.', False, '소리이므로 매질이 필요하다.', 'vac'),
    ('박쥐는 초음파를 내어 반사되어 오는 소리로 물체의 위치를 알아낸다.', True, '반사된 초음파의 시간차로 거리를 안다.', 'bat'),
    ('초음파 진단기는 초음파가 조직 경계면에서 반사되는 것을 이용한다.', True, '반사 신호로 내부 영상을 만든다.', 'med'),
    ('초음파의 속력은 같은 매질에서 가청음의 속력보다 빠르다.', False, '같은 매질에서 소리의 속력은 진동수와 무관하게 같다.', 'speed'),
    ('같은 매질에서 초음파는 가청음보다 파장이 짧다.', True, '진동수가 크므로 λ = v/f 가 짧다.', 'lam'),
    ('소리의 파장이 짧을수록 더 작은 물체의 위치를 구분하기에 유리하다.', True, '파장이 짧을수록 분해능이 좋다.', 'res'),
    ('잡음 제거(노이즈 캔슬링) 헤드폰은 소음과 같은 진폭, 반대 위상의 소리를 내어 소음을 줄인다.', True, '상쇄 간섭을 이용한다.', 'nc'),
    ('노이즈 캔슬링은 소음과 같은 위상의 소리를 더해 소음을 줄인다.', False, '같은 위상이면 보강 간섭으로 소음이 커진다. 반대 위상을 써야 한다.', 'nc'),
    ('노이즈 캔슬링은 소리의 보강 간섭을 이용한 기술이다.', False, '노이즈 캔슬링은 상쇄 간섭을 이용한다.', 'nc2'),
    ('소음과 정확히 같은 진폭·반대 위상의 소리를 내면 이론적으로 합성된 소리의 진폭은 0이다.', True, 'A - A = 0 이다.', 'nc3'),
    ('콘서트홀에서 소리가 벽에 반사되어 생기는 울림(잔향)은 반사의 한 예이다.', True, '반사된 소리가 늦게 도달해 울림이 생긴다.', 'room'),
    ('건물 내부의 흡음재는 소리의 반사를 줄이기 위해 사용한다.', True, '소리 에너지를 흡수해 반사를 줄인다.', 'absorb'),
    ('두 스피커에서 같은 소리를 낼 때 경로차가 반파장의 홀수 배인 위치에서는 소리가 작게 들린다.', True, '상쇄 간섭이다.', 'spk'),
    ('두 스피커에서 같은 위상의 소리를 낼 때 경로차가 파장의 정수 배인 위치에서는 소리가 작게 들린다.', False, '정수 배이면 보강 간섭으로 크게 들린다.', 'spk'),
    ('음파 탐지기(소나)는 물속에서 초음파의 반사를 이용해 거리를 잰다.', True, '왕복 시간으로 거리를 구한다.', 'sonar'),
    ('초음파는 진동수가 높아 투과력이 작으므로 인체에 사용할 수 없다.', False, '의료용 초음파 진단·치료에 널리 쓰인다.', 'misc'),
    ('초음파 세척기는 초음파의 진동으로 물체 표면의 오염 물질을 떼어 낸다.', True, '진동 에너지를 이용한다.', 'clean'),
]


@T('ph104')
def ph104(r, k):
    form = r.choice(['sonar', 'nc', 'nc', 'lam', 'spk', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B104)
        if not s: return None
        return bogi('초음파와 소리의 간섭의 응용에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv=r.choice(['하', '중']), fam='d', r=r,
                    core='초음파는 20000 Hz 이상의 소리로 반사를 이용한 거리 측정에 쓰이고, 노이즈 캔슬링은 반대 위상의 소리로 상쇄 간섭을 일으킨다.', point='초음파와 간섭 기술의 원리를 판단한다.')
    if form == 'sonar':
        medium = r.choice([('바닷물', 1500), ('물속', 1500), ('공기', 340), ('인체 조직', 1500)])
        nm, v = medium
        t = Fr(str(r.choice([0.02, 0.04, 0.1, 0.2, 0.4, 0.6, 1, 2, 4])))
        d = Fr(v) * t / 2
        if not term(d): return None
        if nm == '공기':
            body = P('박쥐가 초음파를 내고 %s초 후에 벽에서 반사된 초음파를 받았다. 소리의 속력이 340 m/s일 때 박쥐에서 벽까지의 거리는?' % fn(t))
        elif nm == '인체 조직':
            body = P('초음파 진단기가 인체 조직 속으로 초음파를 보내고 %s초 후에 장기 표면에서 반사된 초음파를 받았다. 초음파의 속력이 1500 m/s일 때 장기 표면까지의 깊이는?' % fn(t))
        else:
            body = P('배에서 %s 바닥을 향해 초음파를 발사하고 %s초 후에 반사파를 받았다. %s에서 초음파의 속력이 1500 m/s일 때 바닥까지의 깊이는?' % (nm, fn(t), nm))
        wr = [d * 2, d / 2, Fr(v) * t, Fr(v) / t, d + 10]
        return mc(body, '%s m' % fn(d), ['%s m' % fn(w) for w in wr], r=r, lv='하', fam='a',
                  steps=['초음파는 왕복했으므로 이동 거리 = %d × %s = %s m 이다.' % (v, fn(t), fn(Fr(v) * t)), '거리(깊이) = %s / 2 = %s m 이다.' % (fn(Fr(v) * t), fn(d))],
                  core='초음파 거리 측정: d = vt/2.', point='왕복 시간을 반으로 나눠 거리를 구한다.')
    if form == 'nc':
        A = r.choice([2, 3, 4])
        B = r.choice([1, 2, 3, 4])
        T_ = r.choice([4, 8])
        tr = [('소음', 'sin', A, T_, 0.0, BL), ('보정음', 'sin', B, T_, math.pi, RD)]
        fig = FIG(tr_fig(tr, nx=16, H=4), '72%')
        res = abs(A - B)
        ask = r.choice(['amp', 'amp', 'conc'])
        base = '그림은 헤드폰이 소음과 보정음을 내는 상황에서 소음과 보정음의 파형을 같은 눈금으로 나타낸 것이다. 가로 한 칸은 1 ms이다. '
        if ask == 'amp':
            body = P(base + '두 소리가 귀에서 합성될 때 합성음의 진폭은 몇 칸인가?') + fig
            wr = [A + B, A * B, max(A, B), A, B, res + 2]
            return mc(body, '%d칸' % res, ['%d칸' % w for w in wr], r=r, lv='중', fam='b',
                      steps=['소음의 진폭은 %d칸, 보정음의 진폭은 %d칸이고 두 소리는 서로 반대 위상이다.' % (A, B), '합성음의 진폭 = |%d - %d| = %d칸 이다.' % (A, B, res)],
                      core='반대 위상인 같은 진동수의 두 소리의 합성음 진폭은 진폭의 차이다.', point='파형에서 진폭과 위상을 읽는다.') if res != 0 else None
        if A == B: return None
        body = P(base + '소음을 완전히 없애려면 보정음의 진폭을 몇 칸으로 해야 하는가? (단, 보정음의 위상은 그림과 같이 소음과 반대이다.)') + fig
        wr = [A + B, abs(A - B), A * 2, A // 2 if A % 2 == 0 else A + 3, 0]
        return mc(body, '%d칸' % A, ['%d칸' % w for w in wr], r=r, lv='중', fam='b',
                  steps=['합성음의 진폭이 0이 되려면 반대 위상에서 진폭이 같아야 한다.', '소음의 진폭이 %d칸이므로 보정음의 진폭도 %d칸이어야 한다.' % (A, A)],
                  core='상쇄 간섭으로 소음을 없애려면 같은 진폭, 반대 위상이어야 한다.', point='노이즈 캔슬링의 조건을 안다.')
    if form == 'lam':
        f = r.choice([20000, 25000, 34000, 40000, 50000, 68000, 85000, 100000])
        lam = Fr(V, f) * 1000  # mm
        if not term(lam): return None
        body = P('진동수가 %d Hz인 초음파가 공기 중(소리의 속력 340 m/s)에서 진행할 때 파장은?' % f)
        wr = [lam * 10, lam / 10, lam * 2, lam / 2, lam * 100]
        return mc(body, '%s mm' % fn(lam), ['%s mm' % fn(w) for w in wr], r=r, lv='중', fam='c',
                  steps=['λ = v/f = 340 / %d = %s m = %s mm 이다.' % (f, fn(Fr(V, f), 5), fn(lam))],
                  core='λ = v/f (초음파는 파장이 짧다).', point='단위(m→mm)를 환산해 파장을 구한다.')
    # spk
    lam = Fr(str(r.choice([0.2, 0.4, 0.5, 0.6, 0.8, 1, 1.7])))
    m = r.choice([0, 1, 2, 3])
    diff = (m + Fr(1, 2)) * lam
    if not term(diff): return None
    f = Fr(V) / lam
    s1 = r.choice([2, 3, 4, 5])
    s2 = s1 + diff
    body = P('같은 위상으로 같은 소리를 내는 두 스피커 S₁, S₂가 있다. 소리의 속력은 340 m/s이고 소리의 진동수는 %s Hz이다. 점 P는 S₁로부터 %s m, S₂로부터 %s m 떨어져 있다. P에서의 소리는?' % (fn(f), fn(s1), fn(s2)))
    right = '상쇄 간섭하여 작게 들린다'
    wr = ['보강 간섭하여 크게 들린다', '소리가 전혀 들리지 않지만 진동수는 변한다', '경로차가 0이므로 크게 들린다', '진동수가 달라져 맥놀이가 생긴다']
    return mc(body, right, wr + ['소리의 높이가 낮아진다'], r=r, lv='상', fam='e', sort='shuf',
              steps=['파장 λ = v/f = 340 / %s = %s m 이다.' % (fn(f), fn(lam)), '경로차 = %s - %s = %s m = %s λ 이다.' % (fn(s2), fn(s1), fn(diff), fn(diff / lam)), '경로차가 반파장의 홀수 배이므로 상쇄 간섭이 일어나 소리가 작게 들린다.'],
              core='같은 위상의 두 소리원에서 경로차가 (m + ½)λ 이면 상쇄, mλ 이면 보강 간섭이다.', point='경로차를 파장으로 환산해 간섭을 판정한다.')


# ================================================================== ph105 정상파 그림 해석
@T('ph105')
def ph105(r, k):
    form = r.choice(['str', 'str', 'two', 'two', 'pipe', 'pipe', 'cnt', 'cnt', 'cnt'])
    if form == 'str':
        n = r.choice([2, 3, 4, 5, 6])
        L = Fr(str(r.choice([0.6, 0.9, 1.2, 1.5, 1.8, 2.4, 3])))
        lam = 2 * L / n
        if not term(lam): return None
        f = Fr(r.choice([40, 50, 60, 75, 80, 100, 120, 150, 200]))
        v = f * lam
        if not term(v): return None
        fig = FIG(string_fig(n, 'L = %s m' % fn(L), labels=False), '70%')
        ask = r.choice(['v', 'lam', 'f'])
        base = '그림은 길이 %s m인 줄의 양 끝을 고정하고 줄을 진동시켜 만든 정상파를 나타낸 것이다. ' % fn(L)
        if ask == 'v':
            body = P(base + '진동수가 %s Hz일 때 줄을 따라 진행하는 파동의 속력은?' % fn(f)) + fig
            wr = [v * 2, v / 2, f * L, f * L * 2, f * L / n * 2 if False else v * n / (n - 1), f * L * n]
            return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='상', fam='a',
                      steps=['그림에서 배가 %d개(반 파장 %d개)이므로 L = %d × λ/2 → λ = %s m 이다.' % (n, n, n, fn(lam)), 'v = fλ = %s × %s = %s m/s 이다.' % (fn(f), fn(lam), fn(v))],
                      core='정상파 그림에서 파장을 구한 뒤 v = fλ.', point='그림의 배의 수로 파장·속력을 구한다.')
        if ask == 'lam':
            body = P(base + '이 정상파를 만든 파동의 파장은?') + fig
            wr = [lam * 2, lam / 2, L / (n - 1) * 2 if n > 1 else L, L, L / n * 4 if False else L * 2 / (n + 1)]
            return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['그림에서 배는 %d개이므로 L = %d × λ/2 이다.' % (n, n), 'λ = 2L/%d = %s m 이다.' % (n, fn(lam))],
                      core='배 1개 = 반 파장.', point='그림의 배의 수로 파장을 구한다.')
        body = P(base + '줄을 따라 진행하는 파동의 속력이 %s m/s일 때 정상파의 진동수는?' % fn(v)) + fig
        wr = [f * 2, f / 2, v / L, v / (2 * L), f + 10]
        return mc(body, '%s Hz' % fn(f), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='a',
                  steps=['그림에서 배가 %d개이므로 λ = 2L/%d = %s m 이다.' % (n, n, fn(lam)), 'f = v/λ = %s / %s = %s Hz 이다.' % (fn(v), fn(lam), fn(f))],
                  core='정상파 그림에서 파장을 구한 뒤 f = v/λ.', point='그림의 배의 수로 파장을 구해 진동수를 계산한다.')
    if form == 'two':
        n1, n2 = r.sample([1, 2, 3, 4, 5], 2)
        f1 = Fr(r.choice([20, 30, 40, 50, 60, 100]))
        f2 = f1 * Fr(n2, n1)
        if not term(f2): return None
        a = string_fig(n1, labels=False, w=250, h=110)
        b = string_fig(n2, labels=False, w=250, h=110)
        fig = '<div style="display:flex;gap:6px;justify-content:center">' + FIG(a, '49%') + FIG(b, '49%') + '</div>'
        base = '그림 (가), (나)는 길이와 장력이 같은 한 줄의 양 끝을 고정하고 서로 다른 진동수로 진동시켜 만든 정상파를 나타낸 것이다. (가)에서 진동수는 %s Hz이다. ' % fn(f1)
        ask = r.choice(['f2', 'ratio', 'lam'])
        if ask == 'f2':
            body = P(base + '(나)에서 진동수는?') + fig
            wr = [f1 * Fr(n1, n2), f1 * (n2 - n1) if n2 != n1 + 1 else f1 + 10, f1 * n2, f1 + 20, f1 * Fr(n2 * n2, n1 * n1) if f1 * Fr(n2 * n2, n1 * n1) != f2 else f2 + 30]
            return mc(body, '%s Hz' % fn(f2), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['(가)는 배 %d개, (나)는 배 %d개이다. 같은 줄에서 속력이 같으므로 f = nv/2L 에서 f ∝ n 이다.' % (n1, n2), 'f(나) = %s × %d/%d = %s Hz 이다.' % (fn(f1), n2, n1, fn(f2))],
                      core='같은 줄에서 정상파의 진동수는 배의 수에 비례한다.', point='그림의 배의 수 비로 진동수를 구한다.')
        if ask == 'ratio':
            body = P(base + '(가)와 (나)의 파장의 비 λ(가) : λ(나)는?') + fig
            right = ratio_str(n2, n1)
            wr = [ratio_str(n1, n2), ratio_str(n1 * n1, n2 * n2), ratio_str(n2 * n2, n1 * n1), '1 : 1', ratio_str(n1 + 1, n2 + 1)]
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                      steps=['λ = 2L/n 이므로 λ(가) : λ(나) = 1/%d : 1/%d = %d : %d = %s 이다.' % (n1, n2, n2, n1, right)],
                      core='λ = 2L/n 이므로 파장은 배의 수에 반비례한다.', point='그림의 배의 수 비로 파장비를 구한다.')
        body = P(base + '(나)에서 배의 수 - (가)에서 배의 수는? 또는 두 정상파의 진동수의 비 f(가) : f(나)는?'.replace('(나)에서 배의 수 - (가)에서 배의 수는? 또는 ', '')) + fig
        right = ratio_str(n1, n2)
        wr = [ratio_str(n2, n1), ratio_str(n1 * n1, n2 * n2), ratio_str(n2 * n2, n1 * n1), '1 : 1', ratio_str(n1 + 1, n2 + 1)]
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                  steps=['f ∝ n 이므로 f(가) : f(나) = %d : %d = %s 이다.' % (n1, n2, right)],
                  core='같은 줄에서 f ∝ n.', point='배의 수 비가 진동수 비이다.')
    if form == 'pipe':
        kind = 'closed'
        n = r.choice([1, 2, 3])
        L = Fr(str(r.choice([0.17, 0.2, 0.25, 0.34, 0.4, 0.5, 0.68, 0.85, 1, 1.7, 2, 2.5, 3.4, 4])))
        lam = 4 * L / (2 * n - 1)
        f = Fr(V) / lam
        if f.denominator != 1 or not term(lam): return None
        fig = FIG(pipe_fig('closed', n, 'L = %s m' % fn(L)), '70%')
        base = '그림은 한쪽 끝이 막힌 관 속에 생긴 정상파(공기 입자의 변위)를 나타낸 것이다. 관의 길이는 %s m이고 소리의 속력은 340 m/s이다. ' % fn(L)
        ask = r.choice(['lam', 'f'])
        if ask == 'lam':
            body = P(base + '이 정상파의 파장은?') + fig
            wr = [2 * L / n, lam * 2, lam / 2, L, 4 * L]
            return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='c',
                      steps=['그림에서 닫힌 끝은 마디, 열린 끝은 배이며 L = %s × λ/4 이다.' % (2 * n - 1), 'λ = 4L/%d = %s m 이다.' % (2 * n - 1, fn(lam))],
                      core='닫힌 관의 정상파: L = (2n - 1)λ/4.', point='그림에서 L과 λ의 관계를 읽는다.')
        body = P(base + '이 정상파의 진동수는?') + fig
        wr = [f * 2, f / 2, Fr(V) / (4 * L) if (2 * n - 1) != 1 else f * 3, Fr(V) / (2 * L) if n != 1 or True else f + 1, f + 50]
        return mc(body, '%s Hz' % fn(f), ['%s Hz' % fn(w) for w in wr], r=r, lv='상', fam='c',
                  steps=['그림에서 L = %s × λ/4 이므로 λ = 4L/%d = %s m 이다.' % (2 * n - 1, 2 * n - 1, fn(lam)), 'f = v/λ = 340 / %s = %s Hz 이다.' % (fn(lam), fn(f))],
                  core='닫힌 관: f = (2n - 1)v/4L.', point='그림으로 파장을 구해 진동수를 계산한다.')
    # cnt: 마디와 배의 수 / 인접 공명
    if r.random() < 0.6:
        n = r.choice([2, 3, 4, 5, 6])
        Lc = Fr(str(r.choice([0.6, 0.8, 1, 1.2, 1.5, 2, 2.4, 3])))
        fig = FIG(string_fig(n, 'L = %s m' % fn(Lc), labels=True), '70%')
        base = '그림은 길이 %s m인 줄의 양 끝을 고정하여 만든 정상파를 나타낸 것이다. 빨간 점은 마디, 초록 점은 배의 위치이다. ' % fn(Lc)
        ask = r.choice(['pair', 'node', 'anti', 'lam'])
        if ask == 'pair':
            body = P(base + '이 정상파의 마디(양 끝 포함) 수와 배의 수를 옳게 짝지은 것은?') + fig
            right = '마디 %d개, 배 %d개' % (n + 1, n)
            wr = ['마디 %d개, 배 %d개' % (n, n + 1), '마디 %d개, 배 %d개' % (n, n), '마디 %d개, 배 %d개' % (n + 1, n + 1), '마디 %d개, 배 %d개' % (n + 2, n), '마디 %d개, 배 %d개' % (n - 1, n)]
            return mc(body, right, wr, r=r, lv='하', fam='d', sort='shuf', steps=['빨간 점(마디)은 양 끝을 포함해 %d개, 초록 점(배)은 %d개이다.' % (n + 1, n)],
                      core='양 끝이 고정된 줄에서 마디 수 = 배 수 + 1.', point='정상파 그림에서 마디와 배를 센다.')
        if ask == 'node':
            body = P(base + '이 정상파에서 줄의 양 끝을 제외하고 항상 정지해 있는 지점은 모두 몇 곳인가?') + fig
            return mc(body, '%d곳' % (n - 1), ['%d곳' % w for w in (n, n + 1, n - 2 if n > 2 else n + 2, n + 2, 2 * n)], r=r, lv='하', fam='d', sort='shuf',
                      steps=['마디는 양 끝을 포함해 %d개이므로 양 끝을 제외하면 %d곳이다.' % (n + 1, n - 1)],
                      core='마디는 변위가 항상 0인 지점이다.', point='양 끝을 제외한 마디의 수를 센다.')
        if ask == 'anti':
            body = P(base + '이 정상파에서 진폭이 최대인 지점은 모두 몇 곳인가?') + fig
            return mc(body, '%d곳' % n, ['%d곳' % w for w in (n + 1, n - 1, n + 2, 2 * n, n * n + 1)], r=r, lv='하', fam='d', sort='shuf',
                      steps=['그림에서 초록 점(배)은 %d개이다.' % n], core='배는 진폭이 최대인 지점이다.', point='정상파 그림에서 배를 센다.')
        lam = 2 * Lc / n
        if not term(lam): return None
        body = P(base + '이 정상파의 파장은?') + fig
        wr = [lam * 2, lam / 2, Lc, Lc * 2, Lc / (n + 1) * 2]
        return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='하', fam='d', steps=['배가 %d개이므로 L = %d × λ/2 이다.' % (n, n), 'λ = 2L/%d = %s m 이다.' % (n, fn(lam))],
                  core='배 1개는 반 파장이다.', point='배의 수로 파장을 구한다.')
    n = r.choice([1, 2, 3, 4])
    f1 = Fr(r.choice([85, 100, 170, 200, 340]))
    kind = r.choice(['closed', 'open'])
    if kind == 'closed':
        fa, fb = (2 * n - 1) * f1, (2 * n + 1) * f1
        body = P('한쪽 끝이 막힌 관에서 공명이 일어나는 연속한 두 진동수가 %s Hz, %s Hz이다. 이 관의 기본 진동수는?' % (fn(fa), fn(fb)))
        right = f1
        wr = [fb - fa, (fb - fa) * 2 if (fb - fa) * 2 != f1 else f1 + 5, fa, fb, f1 / 2]
        wr = [w for w in wr if w != f1]
        return mc(body, '%s Hz' % fn(right), ['%s Hz' % fn(w) for w in wr] + ['%s Hz' % fn(f1 * 3)], r=r, lv='상', fam='d',
                  steps=['닫힌 관의 공명 진동수는 f₁의 홀수 배이므로 연속한 두 진동수의 차는 2f₁ 이다.', '2f₁ = %s - %s = %s Hz 이므로 f₁ = %s Hz 이다.' % (fn(fb), fn(fa), fn(fb - fa), fn(f1))],
                  core='닫힌 관에서 연속한 공명 진동수의 차는 2f₁ 이다.', point='연속한 두 공명 진동수로 기본 진동수를 구한다.')
    fa, fb = n * f1, (n + 1) * f1
    body = P('양 끝이 열린 관에서 공명이 일어나는 연속한 두 진동수가 %s Hz, %s Hz이다. 이 관의 기본 진동수는?' % (fn(fa), fn(fb)))
    wr = [fb - fa + f1, fa, fb, f1 * 2, f1 / 2]
    return mc(body, '%s Hz' % fn(f1), ['%s Hz' % fn(w) for w in wr], r=r, lv='상', fam='d',
              steps=['열린 관의 공명 진동수는 f₁의 정수 배이므로 연속한 두 진동수의 차가 f₁ 이다.', 'f₁ = %s - %s = %s Hz 이다.' % (fn(fb), fn(fa), fn(f1))],
              core='열린 관에서 연속한 공명 진동수의 차는 f₁ 이다.', point='연속한 두 공명 진동수로 기본 진동수를 구한다.')
