# -*- coding: utf-8 -*-
"""Ⅲ-A 단진동 (ph084~ph090) 생성기."""
from phlib import *
import math
from fractions import Fraction as Fr

G = 10
PI = 3


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
    """Fraction/float -> 보기 좋은 문자열."""
    return num(float(x), nd)


def term(fr):
    """분수가 소수 둘째 자리 이내로 끝나는가."""
    fr = Fr(fr)
    return (fr * 100).denominator == 1


def pick3(r, pool):
    """pool: (문장, 참거짓, 풀이문, 그룹). 서로 다른 그룹 3개, 참 최소 1개."""
    for _ in range(40):
        s = r.sample(pool, 3)
        if len({x[3] for x in s}) < 3: continue
        if any(x[1] for x in s): return [(a, b, c) for a, b, c, _ in s]
    return None


def is_sq(fr):
    fr = Fr(fr)
    a, b = fr.numerator, fr.denominator
    return math.isqrt(a) ** 2 == a and math.isqrt(b) ** 2 == b


def sqf(fr):
    fr = Fr(fr)
    return Fr(math.isqrt(fr.numerator), math.isqrt(fr.denominator))


def ratio_str(a, b):
    a, b = Fr(a), Fr(b)
    q = a / b
    x, y = q.numerator, q.denominator
    return '%d : %d' % (x, y)


def times_str(q):
    q = Fr(q)
    if q.denominator == 1: return '%d배' % q.numerator
    return '%d/%d배' % (q.numerator, q.denominator)


# ------------------------------------------------------------------ 그림
def xt_fig(curves, tmax, xticks, yticks, marks=(), w=330, h=200, ylab='x (cm)', xlab='t (s)', legend=False):
    """curves: [(A, T, 'sin'|'cos', 색, 이름)] 변위-시간 그래프. marks: [(t, 곡선번호, 글자)]."""
    ym = max(c[0] for c in curves) * 1.4
    p = Plot(w, h, tmax * 1.05, ym, xmin=0, ymin=-ym, ml=44, mr=14, mt=16, mb=38)
    p.axes(xlab, ylab, (), yticks, grid=True, origin=False)
    for t in xticks:
        p.line(p.px(t), p.py(-ym), p.px(t), p.py(ym), LG, 1)
        p.line(p.px(t), p.py(0) - 3, p.px(t), p.py(0) + 3, INK, 1)
        p.text(p.px(t), h - 22, fn(t), 11.5, 'middle', c=GR)
    for (A, T, kind, col, name) in curves:
        pts = []
        N = 160
        for i in range(N + 1):
            t = tmax * i / N
            ph = 2 * math.pi * t / T
            pts.append((t, A * (math.sin(ph) if kind == 'sin' else math.cos(ph))))
        p.pl(pts, col, 2.4)
    for (t, ci, lab) in marks:
        A, T, kind, col, name = curves[ci]
        ph = 2 * math.pi * t / T
        y = A * (math.sin(ph) if kind == 'sin' else math.cos(ph))
        if abs(y) < 1e-9: y = 0.0
        X, Y = p.px(t), p.py(y)
        p.circ(X, Y, 3.8, INK, INK, 1)
        if t == 0: X += 11
        if y > 1e-9: p.text(X, Y - 9, lab, 14, 'middle', True, INK)
        elif y < -1e-9: p.text(X, Y + 18, lab, 14, 'middle', True, INK)
        else: p.text(X + 10, Y - 8, lab, 14, 'middle', True, INK)
    if legend:
        for i, c in enumerate(curves):
            p.text(p.px(tmax * 1.02), p.py(ym * 0.8) + 15 * i, c[4], 13, 'end', True, c[3])
    return p.svg()


def hspring_fig(lab='A', xnow=0.0, dlab=None, w=330, h=135, ends=True):
    f = Fig(w, h)
    eq = w / 2 + 10
    S = 88
    fl = 96
    f.line(14, 44, 14, fl, INK, 2.4)
    for yy in range(46, fl, 8): f.line(14, yy, 6, yy + 7, GR, 1)
    f.line(14, fl, w - 8, fl, GR, 1.6)
    bx = eq + xnow * S
    f.spring(14, 79, bx - 18, 6, 8)
    f.rect(bx - 18, fl - 34, 36, 34, '#cfe2f7', INK, 1.8)
    if ends:
        for xx, t in ((eq - S, '-A'), (eq, 'O'), (eq + S, '+A')):
            f.line(xx, 40, xx, fl + 6, GR, 1, '4 3')
            f.text(xx, fl + 20, t, 13, 'middle', True, GR)
    f.arrow(eq, 30, eq + S, 30, RD, 1.6)
    f.arrow(eq + S, 30, eq, 30, RD, 1.6)
    f.text(eq + S / 2, 23, lab, 13, 'middle', True, RD)
    if dlab:
        f.arrow(eq - S, 12, eq + S, 12, BL, 1.6)
        f.arrow(eq + S, 12, eq - S, 12, BL, 1.6)
        f.text(eq, 9, dlab, 12.5, 'middle', True, BL)
    return f.svg()


def vspring(f, x, y1, y2, coils=8, amp=9):
    pts = [(x, y1), (x, y1 + 0.1 * (y2 - y1))]
    n = coils * 2
    for i in range(1, n + 1):
        pts.append((x + (amp if i % 2 else -amp), y1 + 0.1 * (y2 - y1) + (y2 - y1) * 0.8 * i / n))
    pts += [(x, y2 - 0.1 * (y2 - y1)), (x, y2)]
    f.poly(pts, 'none', INK, 1.6, close=False)


def hang_fig(labels, w=250, h=210):
    """수직 용수철. labels: [(길이 px, 질량 이름 또는 None, 길이 글자)] 를 나란히."""
    f = Fig(w, h)
    n = len(labels)
    gap = w / (n + 0.0)
    f.line(8, 14, w - 8, 14, INK, 2.2)
    for xx in range(10, w - 8, 8): f.line(xx, 14, xx - 5, 7, GR, 1)
    for i, (ly, mname, ltxt) in enumerate(labels):
        x = gap * (i + 0.5)
        vspring(f, x, 14, 14 + ly)
        if mname:
            f.rect(x - 17, 14 + ly, 34, 28, '#cfe2f7', INK, 1.8)
            f.text(x, 14 + ly + 19, mname, 13, 'middle', True)
        if ltxt:
            f.arrow(x + 30, 14, x + 30, 14 + ly, BL, 1.4)
            f.arrow(x + 30, 14 + ly, x + 30, 14, BL, 1.4)
            f.text(x + 36, 14 + ly / 2 + 4, ltxt, 12.5, 'start', True, BL)
    return f.svg()


def pend_fig(ltxt, th=30, w=250, h=200, labels=('A', 'B', 'C'), Lpx=140):
    f = Fig(w, h)
    x0, y0 = w / 2, 18
    f.line(x0 - 45, y0, x0 + 45, y0, INK, 2.4)
    for xx in range(int(x0 - 45), int(x0 + 45), 8): f.line(xx, y0, xx - 5, y0 - 7, GR, 1)
    t = math.radians(th)
    pts = [(x0 + Lpx * math.sin(a), y0 + Lpx * math.cos(a)) for a in [(-t + 2 * t * i / 30) for i in range(31)]]
    f.poly(pts, 'none', GR, 1.2, close=False, dash='4 3')
    f.line(x0, y0, x0, y0 + Lpx, GR, 1.2, '4 3')
    for s_, lab in ((-1, labels[0]), (1, labels[2])):
        bx, by = x0 + s_ * Lpx * math.sin(t), y0 + Lpx * math.cos(t)
        f.line(x0, y0, bx, by, INK, 1.6)
        f.circ(bx, by, 9, '#cfe2f7', INK, 1.6)
        f.text(bx + s_ * 17, by + 5, lab, 14, 'middle', True)
    f.circ(x0, y0 + Lpx, 9, '#cfe2f7', INK, 1.6)
    f.text(x0, y0 + Lpx + 25, labels[1], 14, 'middle', True)
    f.text(x0 + 10, y0 + Lpx * 0.55, ltxt, 13, 'start', True, BL)
    f.text(x0 + 26, y0 + 40, 'θ', 13, 'start', True, GR)
    return f.svg()


def circ_fig(rlab, th, w=270, h=210, R=78, qname='Q'):
    f = Fig(w, h)
    cx, cy = w / 2, h / 2 + 4
    f.circ(cx, cy, R, 'none', GR, 1.4)
    f.arrow(cx - R - 16, cy, cx + R + 22, cy, INK, 1.4)
    t = math.radians(th)
    px_, py_ = cx + R * math.cos(t), cy - R * math.sin(t)
    f.line(cx, cy, px_, py_, RD, 2)
    f.line(px_, py_, px_, cy, GR, 1.2, '4 3')
    f.circ(px_, py_, 5, RD, RD, 1)
    f.circ(px_, cy, 4.5, BL, BL, 1)
    f.circ(cx, cy, 2.5, INK, INK, 1)
    f.text(cx - 4, cy + 16, 'O', 13, 'end', True, GR)
    f.text(px_ + (10 if math.cos(t) >= 0 else -10), py_ - 6 if math.sin(t) >= 0 else py_ + 16, 'P', 14, 'middle', True, RD)
    f.text(px_, cy + (16 if math.sin(t) >= 0 else -9), qname, 14, 'middle', True, BL)
    f.text(cx + R * 0.45 * math.cos(t) - 6, cy - R * 0.5 * math.sin(t) - 8 if math.sin(t) >= 0 else cy + 18, rlab, 12.5, 'end', True, RD)
    if th % 180:
        a0 = 0 if True else 0
        n = 16
        arc = [(cx + 24 * math.cos(t * i / n), cy - 24 * math.sin(t * i / n)) for i in range(n + 1)]
        f.poly(arc, 'none', GR, 1.2, close=False)
        f.text(cx + 34 * math.cos(t / 2) + 4, cy - 34 * math.sin(t / 2) + 4, 'θ', 12.5, 'start', True, GR)
    # 회전 방향 화살표
    f.arrow(cx + R + 2, cy - 14, cx + R + 3, cy - 24, GR, 1.4)
    return f.svg()


def fx_fig(pts, xt, yt, w=300, h=200, xl='x (cm)', yl='F (N)', mark=None):
    p = Plot(w, h, max(xt) * 1.12, max(yt) * 1.15, ml=44, mr=14, mt=16, mb=30)
    p.axes(xl, yl, xt, yt, grid=True, origin=False)
    p.pl(pts, BL, 2.6)
    if mark:
        p.dash_to_axes(mark[0], mark[1])
        p.circ(p.px(mark[0]), p.py(mark[1]), 4, RD, RD, 1)
    return p.svg()


def en_fig(A, E, x0, Ep0, w=330, h=215, unitx='cm'):
    """에너지-변위 그래프. 위치 에너지 곡선(Ep=E(x/A)²)과 전체 에너지 선."""
    f = Fig(w, h)
    ml, mr, mt, mb = 50, 16, 20, 34
    X = lambda x: ml + (x + A * 1.1) / (2.2 * A) * (w - ml - mr)
    ymax = E * 1.25
    Y = lambda e: h - mb - e / ymax * (h - mt - mb)
    f.arrow(ml - 4, h - mb, w - mr + 6, h - mb, INK, 1.4)
    f.arrow(X(0), h - mb + 0, X(0), mt - 8, INK, 1.4)
    f.text(w - mr + 4, h - 6, 'x (%s)' % unitx, 12.5, 'end', True, GR)
    f.text(X(0) + 6, 12, '에너지 (J)', 12.5, 'start', True, GR)
    for xv in (-A, 0, A):
        f.line(X(xv), h - mb, X(xv), h - mb + 4, INK, 1)
        f.text(X(xv), h - mb + 17, fn(xv), 11.5, 'middle', c=GR)
    f.line(X(-A), Y(E), X(A), Y(E), GN, 2)
    f.text(X(A) + 3, Y(E) - 5, '전체 E', 12.5, 'end', True, GN)
    pts = [(X(-A + 2 * A * i / 60), Y(E * ((-A + 2 * A * i / 60) / A) ** 2)) for i in range(61)]
    f.poly(pts, 'none', BL, 2.4, close=False)
    f.text(X(0.6 * A), Y(0.17 * E), '위치 에너지', 12.5, 'start', True, BL)
    f.line(X(-A), Y(E), X(-A), h - mb, GR, 1, '4 3')
    f.line(X(A), Y(E), X(A), h - mb, GR, 1, '4 3')
    f.line(X(0) - 4, Y(E), X(0), Y(E), INK, 1)
    f.text(X(0) - 7, Y(E) + 4, fn(E), 11.5, 'end', c=GR)
    if x0 is not None:
        f.line(X(x0), Y(Ep0), X(x0), h - mb, GR, 1, '4 3')
        f.line(X(x0), Y(Ep0), X(0), Y(Ep0), GR, 1, '4 3')
        f.circ(X(x0), Y(Ep0), 4, RD, RD, 1)
        f.text(X(x0), h - mb + 17, fn(x0), 11.5, 'middle', True, RD)
        f.text(X(0) - 7, Y(Ep0) + 4, fn(Ep0), 11.5, 'end', True, RD)
    return f.svg()


# ================================================================== ph084 진폭·주기·진동수
_B84 = [
    ('진폭은 진동 중심에서 최대 변위까지의 거리이다.', True, '진폭은 진동 중심에서 끝점까지의 거리이다.', 'amp'),
    ('진폭은 진동하는 물체의 양 끝점 사이의 거리이다.', False, '양 끝점 사이의 거리는 진폭의 2배이다. 진폭은 중심에서 끝점까지의 거리이다.', 'amp'),
    ('주기는 한 번 왕복하는 데 걸리는 시간이다.', True, '주기는 진동이 한 번 일어나는 데 걸리는 시간이다.', 'T'),
    ('진동수는 1초 동안 일어나는 진동 횟수이고 단위는 Hz이다.', True, '진동수의 단위는 Hz(=1/s)이다.', 'f'),
    ('진동수가 클수록 주기는 길다.', False, '진동수와 주기는 역수 관계이므로 진동수가 클수록 주기는 짧다.', 'inv'),
    ('진동수와 주기는 서로 역수 관계이다.', True, 'f = 1/T 이다.', 'inv'),
    ('진동수의 단위는 s(초)이다.', False, '진동수의 단위는 Hz이고, s는 주기의 단위이다.', 'f'),
    ('한 번 왕복하는 동안 물체가 이동한 거리는 진폭의 2배이다.', False, '한 번 왕복하는 동안 이동한 거리는 진폭의 4배이다.', 'path'),
    ('한 번 왕복하는 동안 물체가 이동한 거리는 진폭의 4배이다.', True, '중심→끝→중심→반대 끝→중심으로 A를 4번 이동한다.', 'path'),
    ('물체가 한쪽 끝점에서 반대쪽 끝점까지 가는 데 걸리는 시간은 주기의 절반이다.', True, '끝점에서 반대쪽 끝점까지는 반 왕복이므로 T/2이다.', 'half'),
    ('물체가 한쪽 끝점에서 반대쪽 끝점까지 가는 데 걸리는 시간은 한 주기이다.', False, '한 주기는 한 번 왕복(끝→반대 끝→처음 끝)하는 시간이다. 한쪽 끝에서 반대쪽 끝까지는 T/2이다.', 'half'),
    ('주기가 2 s인 진동의 진동수는 2 Hz이다.', False, 'f = 1/T = 1/2 = 0.5 Hz 이다.', 'calc'),
    ('1초에 5번 왕복하는 물체의 주기는 0.2 s이다.', True, 'f = 5 Hz 이므로 T = 1/5 = 0.2 s 이다.', 'calc'),
    ('양 끝점에서 물체의 순간 속력은 0이다.', True, '끝점에서 운동 방향이 바뀌므로 순간적으로 속력이 0이다.', 'end'),
    ('진동 중심을 지날 때 물체의 변위 크기가 최대이다.', False, '진동 중심에서의 변위는 0이고, 끝점에서 변위의 크기가 최대(진폭)이다.', 'end'),
    ('진동수가 f인 물체가 t초 동안 하는 진동 횟수는 ft이다.', True, '1초에 f번 진동하므로 t초에는 ft번이다.', 'cnt'),
    ('한 주기가 지나면 물체는 처음과 같은 위치에서 같은 방향으로 운동한다.', True, '주기는 같은 운동 상태가 반복되는 데 걸리는 시간이다.', 'rep'),
    ('주기의 절반 동안 물체가 이동한 거리는 항상 진폭의 2배이다.', True, '반 주기 동안에는 어느 위치에서 출발해도 총 이동 거리가 2A이다.', 'half2'),
    ('진동수가 4 Hz이면 한 번 왕복하는 데 4초가 걸린다.', False, 'T = 1/f = 1/4 = 0.25 s 이다.', 'calc2'),
    ('같은 진동에서 진폭이 클수록 한 번 왕복하는 동안 이동 거리가 크다.', True, '이동 거리는 4A이므로 진폭에 비례한다.', 'path2'),
]


@T('ph084')
def ph084(r, k):
    form = r.choice(['calc', 'dist', 'dist', 'graph', 'graph', 'graph', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B84)
        if not s: return None
        return bogi('진폭, 주기, 진동수에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='d', r=r,
                    core='진폭은 중심에서 끝점까지의 거리, 주기 T는 한 번 왕복하는 시간, 진동수 f는 1초 동안의 진동 횟수이며 f = 1/T 이다.',
                    point='진폭·주기·진동수의 정의와 관계를 구분한다.')
    if form == 'calc':
        sub_ = r.choice(['T', 'f', 'n', 'path'])
        if sub_ in ('T', 'f'):
            Tv = Fr(str(r.choice([0.1, 0.2, 0.25, 0.4, 0.5, 0.8, 1, 1.5, 2, 2.5, 4, 5])))
            n = r.choice([4, 5, 8, 10, 12, 15, 20, 30, 40, 50, 60])
            t = Tv * n
            assert t / n == Tv
            who = r.choice(['용수철에 매달린 물체', '진동하는 추', '단진동을 하는 물체', '수평면에서 용수철에 연결된 물체'])
            if sub_ == 'T':
                body = P('%s가 %s초 동안 %d번 왕복하였다. 이 진동의 주기는?' % (who, fn(t), n))
                right = '%s s' % fn(Tv)
                wr = ['%s Hz' % fn(1 / Tv), '%s s' % fn(Tv * 2), '%s s' % fn(Tv / 2), '%s s' % fn(t), '%s s' % fn(Fr(n)), '%s Hz' % fn(Fr(n) / t * 2)]
                st = ['주기는 한 번 왕복하는 데 걸리는 시간이므로 T = %s / %d = %s s 이다.' % (fn(t), n, fn(Tv))]
            else:
                body = P('%s가 %s초 동안 %d번 왕복하였다. 이 진동의 진동수는?' % (who, fn(t), n))
                right = '%s Hz' % fn(1 / Tv)
                wr = ['%s s' % fn(Tv), '%s Hz' % fn(Tv * 2), '%s Hz' % fn(1 / Tv * 2), '%s Hz' % fn(1 / Tv / 2), '%s Hz' % fn(t), '%s Hz' % fn(1 / Tv + 1)]
                st = ['주기 T = %s / %d = %s s 이다.' % (fn(t), n, fn(Tv)), '진동수 f = 1/T = 1/%s = %s Hz 이다.' % (fn(Tv), fn(1 / Tv))]
            return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf', steps=st,
                      core='주기는 한 번 왕복하는 시간, 진동수는 1초 동안의 진동 횟수이며 f = 1/T 이다.', point='진동 횟수와 시간으로 주기·진동수를 구한다.')
        if sub_ == 'n':
            f_ = Fr(str(r.choice([0.5, 1, 1.5, 2, 2.5, 4, 5, 8, 10, 20])))
            t = r.choice([2, 4, 6, 10, 20, 30, 60])
            n = f_ * t
            if n.denominator != 1: return None
            body = P('진동수가 %s Hz인 단진동을 하는 물체가 %d초 동안 왕복하는 횟수는?' % (fn(f_), t))
            wr = ['%d번' % (t / f_) if (Fr(t) / f_).denominator == 1 else '%s번' % fn(Fr(t) / f_), '%d번' % (n * 2), '%d번' % (n + t), '%d번' % (n // 2 if n % 2 == 0 else n + 1), '%d번' % (n * 4)]
            return mc(body, '%d번' % n, wr, r=r, lv='하', fam='a',
                      steps=['1초에 %s번 진동하므로 %d초 동안의 진동 횟수는 f × t = %s × %d = %d번 이다.' % (fn(f_), t, fn(f_), t, n)],
                      core='t초 동안의 진동 횟수는 진동수 f에 시간 t를 곱한 것이다.', point='진동수의 정의를 이용해 진동 횟수를 구한다.')
        A = r.choice([2, 3, 4, 5, 6, 8, 10, 12])
        n = r.choice([2, 3, 4, 5, 6, 8, 10])
        body = P('진폭이 %d cm인 단진동을 하는 물체가 %d번 왕복하는 동안 이동한 총 거리는?' % (A, n))
        ans = 4 * A * n
        wr = [2 * A * n, A * n, 8 * A * n, 4 * A, 4 * A * n + 4 * A, 2 * A * n + 2 * A]
        return mc(body, '%d cm' % ans, ['%d cm' % w for w in wr], r=r, lv='하', fam='a',
                  steps=['한 번 왕복하는 동안 이동 거리는 4A = 4 × %d = %d cm 이다.' % (A, 4 * A), '%d번 왕복하므로 %d × %d = %d cm 이다.' % (n, 4 * A, n, ans)],
                  core='한 번 왕복하는 동안 물체가 이동한 거리는 진폭의 4배이다.', point='왕복 횟수와 진폭으로 이동 거리를 구한다.')
    if form == 'dist':
        d = r.choice([10, 12, 16, 20, 24, 30, 40])
        f_ = Fr(str(r.choice([0.5, 1, 1.5, 2, 2.5, 4])))
        nh = r.choice([3, 4, 5, 6, 7, 8, 9, 10, 12])
        t = Fr(nh) / (2 * f_)
        if not term(t): return None
        path = d * nh
        fig = FIG(hspring_fig('A', 0.0, dlab='d = %d cm' % d), '70%')
        body = P('그림은 마찰이 없는 수평면에서 용수철에 연결된 물체가 진동하는 모습이다. 물체는 양 끝점 사이 거리 d = %d cm 를 왕복하고, 진동수는 %s Hz이다. 물체가 한쪽 끝점을 출발한 때부터 %s초 동안 이동한 거리는?' % (d, fn(f_), fn(t))) + fig
        wr = [4 * d * nh // 2 * 2 // 1 if False else 2 * d * nh, d * nh // 2 if (d * nh) % 2 == 0 else d * nh + 5, path + d, path - d, 4 * d * nh, int(float(f_) * float(t) * 4 * (d / 2)) + d // 2]
        # 정답 교차 검증: A = d/2, 반주기마다 d 이동
        T_ = 1 / f_
        assert (t / (T_ / 2)) == nh and path == nh * d == int(4 * Fr(d, 2) * f_ * t)
        return mc(body, '%d cm' % path, ['%d cm' % w for w in wr], r=r, lv='상' if nh % 2 else '중', fam='b',
                  steps=['양 끝점 사이 거리가 %d cm 이므로 진폭 A = %d cm 이다.' % (d, d // 2), '주기 T = 1/f = %s s 이고, %s초 = %d × (T/2) 이다.' % (fn(T_), fn(t), nh),
                         '반 주기마다 한쪽 끝에서 반대쪽 끝까지 %d cm 를 이동하므로 총 이동 거리는 %d × %d = %d cm 이다.' % (d, nh, d, path)],
                  core='반 주기 동안 이동 거리는 2A(양 끝점 사이 거리)이고, 한 주기 동안은 4A이다.', point='끝점 사이 거리에서 진폭을 구하고 시간을 주기로 환산한다.')
    # graph
    A = r.choice([2, 3, 4, 5, 6, 8])
    Tv = Fr(str(r.choice([0.2, 0.4, 0.5, 1, 2, 4, 0.8, 1.2])))
    kind = r.choice(['sin', 'cos'])
    ncyc = 2
    tmax = float(Tv * ncyc)
    xt_ = [float(Tv * i / 2) for i in range(1, 2 * ncyc + 1)]
    fig = FIG(xt_fig([(A, float(Tv), kind, BL, '')], tmax, xt_, [-A, A]), '66%')
    ask = r.choice(['A', 'T', 'f', 'path', 'path', 'f'])
    base = '그림은 단진동하는 물체의 변위 x를 시간 t에 따라 나타낸 것이다. '
    if ask == 'A':
        body = P(base + '이 진동의 진폭은?') + fig
        wr = ['%d cm' % (2 * A), '%s cm' % fn(Fr(A, 2)), '%d cm' % (4 * A), '%s s' % fn(Tv), '%d cm' % (A + 1)]
        return mc(body, '%d cm' % A, wr, r=r, lv='하', fam='c', sort='shuf', steps=['변위의 최댓값이 %d cm 이므로 진폭은 %d cm 이다.' % (A, A)],
                  core='변위-시간 그래프에서 변위의 최댓값이 진폭이다.', point='그래프에서 진폭을 읽는다.')
    if ask == 'T':
        body = P(base + '이 진동의 주기는?') + fig
        wr = ['%s s' % fn(Tv * 2), '%s s' % fn(Tv / 2), '%s s' % fn(Tv * 4), '%s Hz' % fn(1 / Tv), '%s s' % fn(Tv * 3 / 2)]
        return mc(body, '%s s' % fn(Tv), wr, r=r, lv='하', fam='c', sort='shuf',
                  steps=['그래프가 한 번 반복되는 데 걸리는 시간을 읽으면 %s s 이다.' % fn(Tv)],
                  core='변위-시간 그래프가 한 번 반복되는 시간이 주기이다.', point='그래프에서 주기를 읽는다.')
    if ask == 'f':
        body = P(base + '이 진동의 진동수는?') + fig
        fv = 1 / Tv
        wr = ['%s Hz' % fn(Tv), '%s Hz' % fn(fv * 2), '%s Hz' % fn(fv / 2), '%s s' % fn(Tv), '%s Hz' % fn(fv + 1)]
        return mc(body, '%s Hz' % fn(fv), wr, r=r, lv='중', fam='c', sort='shuf',
                  steps=['그래프에서 주기 T = %s s 이다.' % fn(Tv), 'f = 1/T = 1/%s = %s Hz 이다.' % (fn(Tv), fn(fv))],
                  core='진동수는 주기의 역수이다.', point='주기를 읽고 진동수로 환산한다.')
    mul = r.choice([Fr(3, 2), Fr(2), Fr(5, 2), Fr(1), Fr(3)])
    tt = Tv * mul
    path = 4 * A * mul
    assert path.denominator == 1
    body = P(base + 't = 0 부터 t = %s s 까지 물체가 이동한 거리는?' % fn(tt)) + fig
    wr = ['%d cm' % (2 * A * mul if (2 * A * mul).denominator == 1 else 2 * A), '%d cm' % (A * mul if (A * mul).denominator == 1 else A), '%d cm' % (8 * A * mul), '%d cm' % (path + 2 * A), '%d cm' % (path - 2 * A if path > 2 * A else path + A)]
    return mc(body, '%d cm' % path, wr, r=r, lv='상' if mul in (Fr(3, 2), Fr(5, 2)) else '중', fam='c',
              steps=['진폭 A = %d cm, 주기 T = %s s 이다.' % (A, fn(Tv)), '%s s = %s T 이고, 한 주기 동안 이동 거리는 4A = %d cm 이므로 %s × %d = %d cm 이다.' % (fn(tt), fn(mul), 4 * A, fn(mul), 4 * A, path)],
              core='한 주기 동안 이동 거리는 4A이고, 반 주기 동안은 2A이다.', point='그래프에서 진폭과 주기를 읽어 이동 거리를 구한다.')


# ================================================================== ph085 변위-시간 그래프 해석
_LET = '가나다라마'


def _xv(kind, A, Tv, t):
    ph = 2 * math.pi * t / Tv
    if kind == 'sin':
        return A * math.sin(ph), A * 2 * math.pi / Tv * math.cos(ph), -A * (2 * math.pi / Tv) ** 2 * math.sin(ph)
    return A * math.cos(ph), -A * 2 * math.pi / Tv * math.sin(ph), -A * (2 * math.pi / Tv) ** 2 * math.cos(ph)


@T('ph085')
def ph085(r, k):
    form = r.choice(['mark', 'mark', 'mark', 'val', 'val', 'cmp', 'bogi'])
    if form == 'mark':
        A = r.choice([2, 3, 4, 5, 6])
        Tv = r.choice([1, 2, 4, 0.8, 1.2, 0.4])
        kind = r.choice(['sin', 'cos'])
        ts = [Tv * i / 4 for i in range(5)]
        names = list(_LET)
        marks = [(ts[i], 0, names[i]) for i in range(5)]
        tmax = Tv * 1.25
        fig = FIG(xt_fig([(A, Tv, kind, BL, '')], tmax, [Tv / 4 * i for i in range(1, 6)], [-A, A], marks=marks), '66%')
        vals = [_xv(kind, A, Tv, t) for t in ts]
        q = r.choice(['vmax', 'amax', 'vpos', 'still'])
        base = '그림은 단진동하는 물체의 변위 x를 시간 t에 따라 나타낸 것이다. 점 가~마는 그래프 위의 점이다. '
        eps = 1e-6
        if q == 'vmax':
            S = {i for i in range(5) if abs(vals[i][0]) < eps}
            txt = '물체의 속력이 최대인 점만을 있는 대로 고른 것은?'
            why = '속력은 진동 중심(x = 0)을 지날 때 최대이다.'
        elif q == 'amax':
            S = {i for i in range(5) if abs(abs(vals[i][0]) - A) < eps}
            txt = '물체에 작용하는 알짜힘의 크기가 최대인 점만을 있는 대로 고른 것은?'
            why = '복원력은 변위의 크기에 비례하므로 변위의 크기가 최대(끝점)일 때 최대이다.'
        elif q == 'vpos':
            S = {i for i in range(5) if abs(vals[i][0]) < eps and vals[i][1] > 0}
            txt = '물체의 속도가 +x 방향이면서 속력이 최대인 점만을 있는 대로 고른 것은?'
            why = '중심을 지나면서 그래프의 기울기가 양(+)인 점이다.'
        else:
            S = {i for i in range(5) if abs(abs(vals[i][0]) - A) < eps}
            txt = '물체가 순간적으로 정지하는 점만을 있는 대로 고른 것은?'
            why = '끝점(변위의 크기가 진폭)에서 운동 방향이 바뀌며 속력이 0이다.'
        if not S: return None
        right = ', '.join(names[i] for i in sorted(S))
        import itertools
        allc = []
        for n_ in (1, 2, 3):
            for c in itertools.combinations(range(5), n_):
                allc.append(', '.join(names[i] for i in c))
        wr = [c for c in allc if c != right]
        ws = r.sample(wr, 12)
        # 흔한 오답 우선: 반대 개념
        opp = {i for i in range(5) if abs(abs(vals[i][0]) - A) < eps} if q in ('vmax', 'vpos') else {i for i in range(5) if abs(vals[i][0]) < eps}
        ws = [', '.join(names[i] for i in sorted(opp))] + ws if opp else ws
        return mc(P(base + txt) + fig, right, ws, r=r, lv='하' if q in ('vmax', 'still') else '중', fam='a', sort='shuf',
                  steps=['그래프에서 각 점의 변위: ' + ', '.join('%s: %s cm' % (names[i], fn(round(vals[i][0], 6))) for i in range(5)) + ' 이다.', why,
                         '따라서 해당하는 점은 %s 이다.' % right],
                  core='단진동에서 중심(x = 0)에서는 속력이 최대이고 알짜힘이 0이며, 끝점에서는 속력이 0이고 알짜힘의 크기가 최대이다.', point='변위-시간 그래프의 점에서 속력과 힘을 판단한다.')
    if form == 'val':
        A = r.choice([2, 3, 4, 5, 6, 8, 10])
        Tv = r.choice([1, 2, 3, 4, 6, 12])
        kind = r.choice(['sin', 'cos'])
        sub_ = r.choice(['x', 'x', 'vmax', 'amax'])
        if sub_ == 'x':
            ph = r.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
            t = Fr(Tv * ph, 12)
            if not term(t): return None
            deg = 30 * ph
            tab = {'sin': {0: 0, 30: Fr(1, 2), 60: None, 90: 1, 120: None, 150: Fr(1, 2), 180: 0, 210: Fr(-1, 2), 240: None, 270: -1, 300: None, 330: Fr(-1, 2)},
                   'cos': {0: 1, 30: None, 60: Fr(1, 2), 90: 0, 120: Fr(-1, 2), 150: None, 180: -1, 210: None, 240: Fr(-1, 2), 270: 0, 300: Fr(1, 2), 330: None}}
            c = tab[kind][deg % 360]
            if c is None: return None
            xv = A * c
            if not term(xv): return None
            assert abs(float(xv) - _xv(kind, A, Tv, float(t))[0]) < 1e-9
            fig = FIG(xt_fig([(A, Tv, kind, BL, '')], Tv * 1.25, [Tv / 4 * i for i in range(1, 6)], [-A, A]), '66%')
            body = P('그림은 단진동하는 물체의 변위 x를 시간 t에 따라 나타낸 것이다. t = %s s 일 때 물체의 변위는? (단, +x 방향이 양(+)이다.)' % fn(t)) + fig
            wr = ['%s cm' % fn(-xv) if xv != 0 else '%d cm' % A, '%s cm' % fn(A * 2 * Fr(c) if abs(A * 2 * Fr(c)) <= 100 else A), '%d cm' % A, '%d cm' % (-A), '0', '%s cm' % fn(A * Fr(1, 2)), '%s cm' % fn(-A * Fr(1, 2))]
            return mc(body, '%s cm' % fn(xv), wr, r=r, lv='중', fam='b', sort='shuf',
                      steps=['주기 T = %d s, 진폭 A = %d cm 이다.' % (Tv, A), 't = %s s 는 T의 %s 배이므로 위상은 %d°이다.' % (fn(t), fn(Fr(ph, 12)), deg),
                             'x = A %s(2πt/T) = %d × %s = %s cm 이다.' % (kind, A, fn(c), fn(xv))],
                      core='변위-시간 그래프가 x = A sin(2πt/T) 또는 A cos(2πt/T) 꼴임을 이용해 특정 시각의 변위를 구한다.', point='그래프의 형태에서 위상을 읽어 변위를 계산한다.')
        if sub_ == 'vmax':
            v = Fr(2 * PI * A, Tv)
            if not term(v): return None
            fig = FIG(xt_fig([(A, Tv, kind, BL, '')], Tv * 1.25, [Tv / 4 * i for i in range(1, 6)], [-A, A]), '66%')
            body = P('그림은 단진동하는 물체의 변위 x를 시간 t에 따라 나타낸 것이다. 이 물체의 최대 속력은? (단, π = 3으로 계산한다.)') + fig
            wr = [v / 2, v * 2, Fr(A, Tv), v * 2 * PI, Fr(A) * Tv, v + A]
            assert abs(float(v) - max(abs(_xv(kind, A, Tv, Tv * i / 400)[1]) for i in range(401)) / (2 * math.pi) * PI) < 0.05 * float(v) + 0.3
            return mc(body, '%s cm/s' % fn(v), ['%s cm/s' % fn(w) for w in wr], r=r, lv='상', fam='b', sort='shuf',
                      steps=['진폭 A = %d cm, 주기 T = %d s 이다.' % (A, Tv), '최대 속력은 중심을 지날 때이고 v = 2πA/T = 2 × 3 × %d / %d = %s cm/s 이다.' % (A, Tv, fn(v))],
                      core='단진동의 최대 속력은 v = Aω = 2πA/T 이다.', point='그래프에서 A, T를 읽어 최대 속력을 계산한다.')
        a = Fr(4 * PI * PI * A, Tv * Tv)
        if not term(a): return None
        fig = FIG(xt_fig([(A, Tv, kind, BL, '')], Tv * 1.25, [Tv / 4 * i for i in range(1, 6)], [-A, A]), '66%')
        body = P('그림은 단진동하는 물체의 변위 x를 시간 t에 따라 나타낸 것이다. 이 물체의 가속도의 최대 크기는? (단, π = 3으로 계산한다.)') + fig
        wr = [a / 2, a * 2, a / PI, Fr(2 * PI * A, Tv), Fr(A, Tv * Tv)]
        return mc(body, '%s cm/s²' % fn(a), ['%s cm/s²' % fn(w) for w in wr], r=r, lv='상', fam='b', sort='shuf',
                  steps=['A = %d cm, T = %d s 이므로 ω = 2π/T = %s rad/s 이다.' % (A, Tv, fn(Fr(2 * PI, Tv))), '가속도의 최대 크기는 ω²A = (%s)² × %d = %s cm/s² 이다.' % (fn(Fr(2 * PI, Tv)), A, fn(a))],
                  core='단진동의 가속도의 최대 크기는 a = ω²A = 4π²A/T² 이다.', point='끝점에서 가속도의 크기가 최대임을 이용한다.')
    if form == 'cmp':
        A1, A2 = r.sample([2, 3, 4, 6, 8], 2)
        T1, T2 = r.sample([1, 2, 3, 4, 6], 2)
        kind = r.choice(['sin', 'cos'])
        tmax = max(T1, T2) * 1.25
        step = r.choice([1, 2]) if False else 1
        xt_ = list(range(1, int(tmax) + 1))
        fig = FIG(xt_fig([(A1, T1, kind, BL, 'A'), (A2, T2, kind, RD, 'B')], tmax, xt_, sorted({-A1, A1, -A2, A2}), legend=True), '70%')
        q = r.choice(['vmax', 'amax', 'T'])
        base = '그림은 단진동하는 물체 A, B의 변위 x를 시간 t에 따라 나타낸 것이다. '
        if q == 'T':
            right = ratio_str(T1, T2)
            body = P(base + '진동수의 비 f%s : f%s는?' % (sub('A'), sub('B'))) + fig
            right = ratio_str(Fr(1, T1), Fr(1, T2))
            wr = [ratio_str(T1, T2), ratio_str(A1, A2), ratio_str(A2, A1), ratio_str(Fr(A1, T1), Fr(A2, T2)), '1 : 1']
            st = ['주기는 T%s = %d s, T%s = %d s 이다.' % (sub('A'), T1, sub('B'), T2), 'f = 1/T 이므로 f%s : f%s = 1/%d : 1/%d = %s 이다.' % (sub('A'), sub('B'), T1, T2, right)]
            lv = '중'
        elif q == 'vmax':
            right = ratio_str(Fr(A1, T1), Fr(A2, T2))
            body = P(base + '최대 속력의 비 v%s : v%s는?' % (sub('A'), sub('B'))) + fig
            wr = [ratio_str(A1, A2), ratio_str(Fr(A1, T1 * T1), Fr(A2, T2 * T2)), ratio_str(Fr(A2, T2), Fr(A1, T1)), ratio_str(A1 * T1, A2 * T2), ratio_str(T1, T2)]
            st = ['A%s = %d cm, T%s = %d s, A%s = %d cm, T%s = %d s 이다.' % (sub('A'), A1, sub('A'), T1, sub('B'), A2, sub('B'), T2),
                  '최대 속력 v = 2πA/T 이므로 v%s : v%s = %d/%d : %d/%d = %s 이다.' % (sub('A'), sub('B'), A1, T1, A2, T2, right)]
            lv = '상'
        else:
            right = ratio_str(Fr(A1, T1 * T1), Fr(A2, T2 * T2))
            body = P(base + '가속도의 최대 크기의 비 a%s : a%s는?' % (sub('A'), sub('B'))) + fig
            wr = [ratio_str(Fr(A1, T1), Fr(A2, T2)), ratio_str(A1, A2), ratio_str(Fr(A2, T2 * T2), Fr(A1, T1 * T1)), ratio_str(A1 * T1, A2 * T2), ratio_str(T2 * T2, T1 * T1)]
            st = ['A%s = %d cm, T%s = %d s, A%s = %d cm, T%s = %d s 이다.' % (sub('A'), A1, sub('A'), T1, sub('B'), A2, sub('B'), T2),
                  '최대 가속도 a = 4π²A/T² 이므로 a%s : a%s = %d/%d² : %d/%d² = %s 이다.' % (sub('A'), sub('B'), A1, T1, A2, T2, right)]
            lv = '상'
        return mc(body, right, wr, r=r, lv=lv, fam='c', sort='shuf', steps=st,
                  core='단진동에서 f = 1/T, 최대 속력 = 2πA/T, 최대 가속도 = 4π²A/T² 이다.', point='두 그래프에서 A, T를 읽어 비를 구한다.')
    # bogi: 그래프에서 동적으로 문장 생성
    A = r.choice([2, 3, 4, 5, 6])
    Tv = r.choice([2, 4, 6, 8])
    kind = r.choice(['sin', 'cos'])
    fig = FIG(xt_fig([(A, Tv, kind, BL, '')], Tv * 1.25, [Tv / 4 * i for i in range(1, 6)], [-A, A]), '66%')
    cands = []
    # 진폭
    wrongA = r.choice([2 * A, A + 2, A // 2 if A % 2 == 0 else A * 3])
    ok = r.random() < .5
    cands.append(('이 진동의 진폭은 %d cm이다.' % (A if ok else wrongA), ok, '그래프에서 변위의 최댓값은 %d cm이므로 진폭은 %d cm이다.' % (A, A), 'amp'))
    ok = r.random() < .5
    wrongT = r.choice([Tv * 2, Tv // 2, Tv + 2])
    cands.append(('주기는 %d s이다.' % (Tv if ok else wrongT), ok, '한 번 반복되는 데 걸리는 시간은 %d s이므로 주기는 %d s이다.' % (Tv, Tv), 'T'))
    t1 = Fr(Tv * r.choice([0, 1, 2, 3, 4, 5, 6, 8]), 4)
    x1 = _xv(kind, A, Tv, float(t1))
    cands.append(('t = %s s 일 때 물체의 속력은 최대이다.' % fn(t1), abs(x1[0]) < 1e-6, 't = %s s 에서 변위는 %s cm 이므로 %s' % (fn(t1), fn(round(x1[0], 6)), '중심을 지나 속력이 최대이다.' if abs(x1[0]) < 1e-6 else '중심이 아니므로 속력이 최대가 아니다(끝점이면 0, 중심이면 최대).'), 'v'))
    t2 = Fr(Tv * r.choice([0, 1, 2, 3, 4, 5, 6, 8]), 4)
    x2 = _xv(kind, A, Tv, float(t2))
    cands.append(('t = %s s 일 때 물체에 작용하는 알짜힘의 크기는 최대이다.' % fn(t2), abs(abs(x2[0]) - A) < 1e-6, 't = %s s 에서 변위는 %s cm 이므로 %s' % (fn(t2), fn(round(x2[0], 6)), '끝점이어서 복원력의 크기가 최대이다.' if abs(abs(x2[0]) - A) < 1e-6 else '끝점이 아니어서 복원력의 크기가 최대가 아니다.'), 'F'))
    t3 = Fr(Tv * r.choice([1, 2, 3, 5, 6, 7]), 8)
    x3 = _xv(kind, A, Tv, float(t3))
    mv = '+x' if x3[1] > 0 else '-x'
    claim = r.choice(['+x', '-x'])
    cands.append(('t = %s s 일 때 물체는 %s 방향으로 운동한다.' % (fn(t3), claim), claim == mv, 't = %s s 에서 그래프의 기울기가 %s이므로 물체는 %s 방향으로 운동한다.' % (fn(t3), '양(+)' if x3[1] > 0 else '음(-)', mv), 'dir'))
    t4 = Fr(Tv * r.choice([1, 2, 3]), 4)
    ok = r.random() < .5
    d_true = 2 * A
    cands.append(('t = 0 부터 t = %s s 까지 물체가 이동한 거리는 %d cm이다.' % (fn(Tv / 2), d_true if ok else 4 * A), ok, '반 주기 동안 이동 거리는 2A = %d cm이다.' % (2 * A), 'dist'))
    ok = r.random() < .5
    cands.append(('진동수는 %s Hz이다.' % (fn(Fr(1, Tv)) if ok else fn(Fr(Tv))), ok, '진동수 f = 1/T = 1/%d = %s Hz 이다.' % (Tv, fn(Fr(1, Tv))), 'f'))
    for _ in range(40):
        s = r.sample(cands, 3)
        if len({x[3] for x in s}) < 3: continue
        if any(x[1] for x in s): break
    else:
        return None
    return bogi('그림은 단진동하는 물체의 변위 x를 시간 t에 따라 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?',
                [(a, b, c) for a, b, c, _ in s], pre=fig, ask='', lv='중', fam='d', r=r,
                core='변위-시간 그래프에서 진폭·주기를 읽고, 기울기가 속도, 중심에서 속력 최대, 끝점에서 알짜힘 최대임을 판단한다.', point='그래프의 값으로 각 시각의 운동 상태를 판단한다.')


# ================================================================== ph086 용수철 진자의 주기
_B86 = [
    ('용수철 진자의 주기는 진폭이 클수록 길어진다.', False, '단진동의 주기는 진폭과 무관하다.', 'amp'),
    ('용수철 진자의 주기는 진폭과 관계없이 일정하다.', True, 'T = 2π√(m/k) 에 진폭은 포함되지 않는다.', 'amp'),
    ('물체의 질량이 4배가 되면 주기는 2배가 된다.', True, 'T ∝ √m 이므로 √4 = 2배이다.', 'mass'),
    ('물체의 질량이 4배가 되면 주기는 4배가 된다.', False, 'T ∝ √m 이므로 질량이 4배이면 주기는 2배이다.', 'mass'),
    ('용수철 상수가 클수록 주기는 짧아진다.', True, 'T ∝ 1/√k 이므로 k가 클수록 T가 짧다.', 'k'),
    ('용수철 상수가 4배가 되면 주기는 4배가 된다.', False, 'T ∝ 1/√k 이므로 k가 4배이면 주기는 1/2배가 된다.', 'k'),
    ('같은 용수철 진자를 달에서 진동시키면 주기가 길어진다.', False, 'T = 2π√(m/k) 는 중력 가속도와 무관하므로 달에서도 주기가 같다.', 'g'),
    ('수평면에서 진동하는 용수철 진자와 같은 용수철·물체를 수직으로 매달아 진동시킨 진자의 주기는 같다.', True, '주기는 m과 k만으로 결정되며 배치와 무관하다.', 'dir'),
    ('용수철 진자의 진동수는 √(k/m)에 비례한다.', True, 'f = (1/2π)√(k/m) 이다.', 'f'),
    ('질량이 같을 때 용수철 상수가 큰 용수철 진자의 진동수가 더 작다.', False, 'f ∝ √k 이므로 k가 클수록 진동수가 크다.', 'f'),
    ('용수철 진자의 주기는 2π√(m/k)이다.', True, '용수철 진자의 주기 공식이다.', 'form'),
    ('용수철 진자의 주기는 2π√(k/m)이다.', False, '주기는 T = 2π√(m/k) 이다(m이 분자).', 'form'),
    ('물체의 질량이 2배가 되면 진동수는 √2배가 된다.', False, 'f ∝ 1/√m 이므로 진동수는 1/√2배가 된다.', 'mass2'),
    ('진동 중심에서 용수철이 물체에 작용하는 힘은 0이다(수평 배치).', True, '수평 배치에서 중심은 용수철의 원래 길이 위치이므로 힘이 0이다.', 'center'),
    ('질량이 같은 두 물체가 서로 다른 용수철에 매달려 있을 때, k가 4배인 용수철의 진동수는 2배이다.', True, 'f ∝ √k 이므로 k가 4배이면 f는 2배이다.', 'k2'),
    ('진폭을 2배로 하면 최대 속력도 변하지 않는다.', False, '최대 속력 v = Aω 이므로 진폭이 2배이면 최대 속력도 2배이다(주기는 같다).', 'vmax'),
    ('진폭을 2배로 하면 진동 한 번에 걸리는 시간은 2배가 된다.', False, '주기는 진폭과 무관하다.', 'amp2'),
    ('용수철 상수가 일정할 때 주기의 제곱은 질량에 비례한다.', True, 'T² = 4π²m/k 이므로 T²은 m에 비례한다.', 'sq'),
]


@T('ph086')
def ph086(r, k):
    form = r.choice(['calc', 'calc', 'ratio', 'ratio', 'inv', 'hang', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B86)
        if not s: return None
        return bogi('용수철 진자에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='d', r=r,
                    core='용수철 진자의 주기는 T = 2π√(m/k) 이며 진폭과 중력에는 무관하다.', point='주기를 결정하는 요인(m, k)을 구분한다.')
    if form == 'calc':
        Tv = Fr(str(r.choice([0.6, 1.2, 1.5, 1.8, 2.4, 3, 0.3, 0.9, 3.6, 6])))
        q = Tv / (2 * PI)
        m = Fr(str(r.choice([0.1, 0.2, 0.25, 0.4, 0.5, 1, 2, 4, 0.9, 0.36])))
        kk = m / (q * q)
        if kk.denominator != 1 or kk > 500: return None
        assert Tv == 2 * PI * sqf(m / kk) if is_sq(m / kk) else False
        body = P('질량 %s kg인 물체를 용수철 상수가 %d N/m인 용수철에 연결하여 마찰이 없는 수평면에서 단진동시켰다. 이 진동의 주기는? (단, π = 3으로 계산한다.)' % (fn(m), kk))
        wr = [Tv / 6, Tv * 6 if Tv * 6 < 100 else Tv * 2, Tv / 2, Tv * 2, 2 * PI * m / kk, Tv * Fr(3, 2)]
        return mc(body, '%s s' % fn(Tv), ['%s s' % fn(w) for w in wr], r=r, lv='하', fam='a',
                  steps=['용수철 진자의 주기는 T = 2π√(m/k) 이다.', 'T = 2 × 3 × √(%s/%d) = 6 × %s = %s s 이다.' % (fn(m), kk, fn(sqf(m / kk)), fn(Tv))],
                  core='용수철 진자의 주기 T = 2π√(m/k).', point='공식에 m, k를 대입한다.')
    if form == 'ratio':
        kind = r.choice(['one', 'two'])
        if kind == 'one':
            a = r.choice([1, 2, 4, 9, 3, 8])
            b = r.choice([1, 2, 4, 9, 3, 8, 16])
            fac = Fr(a, b)
            if not is_sq(fac) or fac == 1: return None
            f_ = sqf(fac)
            body = P('용수철 진자에서 물체의 질량을 %s배로 하고 용수철 상수를 %s배로 하였더니 주기가 처음의 몇 배가 되었는가?' % (fn(a), fn(b)))
            right = times_str(f_)
            wr = [times_str(fac), times_str(1 / f_), times_str(1 / fac), times_str(Fr(a, 1) * b if a * b < 50 else f_ + 1), times_str(f_ + 1)]
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                      steps=['T = 2π√(m/k) 이므로 T′/T = √(m′k/(mk′)) = √(%d/%d) = %s 이다.' % (a, b, right)],
                      core='용수철 진자의 주기는 √m에 비례하고 √k에 반비례한다.', point='질량·용수철 상수의 변화를 제곱근으로 반영한다.')
        mA, mB = r.sample([1, 2, 4, 8, 9], 2)
        kA, kB = r.sample([1, 2, 4, 8, 9, 16], 2)
        fac = Fr(mA, kA) / Fr(mB, kB)
        if not is_sq(fac): return None
        rr = sqf(fac)
        tb = table(['', '질량 (kg)', '용수철 상수 (N/m)'], [['A', mA, kA * 10], ['B', mB, kB * 10]])
        body = P('표는 마찰이 없는 수평면에서 용수철 진자 A, B의 물체의 질량과 용수철 상수를 나타낸 것이다. 주기의 비 T%s : T%s는?' % (sub('A'), sub('B'))) + tb
        right = ratio_str(rr, 1)
        wr = [ratio_str(fac, 1), ratio_str(1, rr), ratio_str(1, fac), ratio_str(Fr(mA, mB), 1), ratio_str(Fr(kA, kB), 1)]
        return mc(body, right, wr, r=r, lv='상', fam='b', sort='shuf',
                  steps=['T ∝ √(m/k) 이므로 T%s : T%s = √(%d/%d) : √(%d/%d) 이다.' % (sub('A'), sub('B'), mA, kA, mB, kB), '= %s 이다.' % right],
                  core='용수철 진자의 주기는 √(m/k)에 비례한다.', point='표의 값으로 √(m/k)의 비를 구한다.')
    if form == 'inv':
        Tv = Fr(str(r.choice([0.6, 1.2, 1.8, 2.4, 3, 0.3, 0.9, 1.5, 3.6])))
        m = Fr(str(r.choice([0.1, 0.2, 0.4, 0.5, 1, 2, 4, 0.9, 0.3])))
        kk = 4 * PI * PI * m / (Tv * Tv)
        if kk.denominator != 1 or kk > 500: return None
        ask = r.choice(['k', 'm'])
        if ask == 'k':
            body = P('질량 %s kg인 물체를 용수철에 매달아 진동시켰더니 주기가 %s s 였다. 이 용수철의 용수철 상수는? (단, π = 3으로 계산한다.)' % (fn(m), fn(Tv)))
            wr = [kk / 2, kk * 2, kk / 4, kk * 4, 2 * PI * m / Tv, kk + 10]
            return mc(body, '%d N/m' % kk, ['%s N/m' % fn(w) for w in wr], r=r, lv='중', fam='c',
                      steps=['T = 2π√(m/k) 에서 k = 4π²m/T² 이다.', 'k = 4 × 9 × %s / %s² = %d N/m 이다.' % (fn(m), fn(Tv), kk)],
                      core='T = 2π√(m/k) 에서 k = 4π²m/T².', point='주기 공식을 변형해 용수철 상수를 구한다.')
        body = P('용수철 상수가 %d N/m인 용수철에 물체를 매달아 진동시켰더니 주기가 %s s 였다. 물체의 질량은? (단, π = 3으로 계산한다.)' % (kk, fn(Tv)))
        wr = [m * 2, m / 2, m * 4, m / 4, m + Fr(1, 2)]
        return mc(body, '%s kg' % fn(m), ['%s kg' % fn(w) for w in wr], r=r, lv='중', fam='c',
                  steps=['T = 2π√(m/k) 에서 m = kT²/4π² 이다.', 'm = %d × %s² / (4 × 9) = %s kg 이다.' % (kk, fn(Tv), fn(m))],
                  core='T = 2π√(m/k) 에서 m = kT²/4π².', point='주기 공식을 변형해 질량을 구한다.')
    # hang: 수직 용수철, 늘어난 길이로 주기
    x0 = Fr(str(r.choice([0.1, 0.4, 0.9, 1.6, 2.5, 0.025, 0.225])))
    m = r.choice([0.5, 1, 2, 4, 0.2])
    kk = Fr(str(m)) * G / x0
    Tv = 2 * PI * sqf(x0 / G) if is_sq(x0 / G) else None
    if Tv is None or kk.denominator != 1 and not term(kk): return None
    labels = [(60, None, None), (60 + min(90, float(x0) * 80 + 20), '물체', '%s m' % fn(x0))]
    f = Fig(250, 215)
    f.line(8, 14, 242, 14, INK, 2.2)
    for xx in range(10, 240, 8): f.line(xx, 14, xx - 5, 7, GR, 1)
    vspring(f, 70, 14, 74); f.text(70, 100, '원래 길이', 12, 'middle', True, GR)
    ly = 74 + 70
    vspring(f, 180, 14, 14 + ly - 14); f.rect(158, ly, 44, 30, '#cfe2f7', INK, 1.8); f.text(180, ly + 20, '%s kg' % fn(Fr(str(m))), 12.5, 'middle', True)
    f.line(140, 74, 170, 74, GR, 1, '4 3')
    f.arrow(150, 74, 150, ly, BL, 1.4); f.arrow(150, ly, 150, 74, BL, 1.4)
    f.text(144, (74 + ly) / 2 + 4, '%s m' % fn(x0), 12.5, 'end', True, BL)
    fig = FIG(f.svg(), '58%')
    body = P('그림과 같이 질량 %s kg인 물체를 원래 길이의 용수철에 매달아 정지시켰더니 용수철이 %s m 늘어났다. 이 물체를 연직 방향으로 조금 당겼다 놓았을 때 단진동의 주기는? (단, 중력 가속도는 10 m/s², π = 3이고 용수철의 질량은 무시한다.)' % (fn(Fr(str(m))), fn(x0))) + fig
    kk = Fr(str(m)) * G / x0
    Tchk = 2 * PI * math.sqrt(float(Fr(str(m)) / kk))
    assert abs(Tchk - float(Tv)) < 1e-9
    wr = [Tv / 2, Tv * 2, Tv / 6, Tv * 6 if Tv * 6 < 60 else Tv * 3, 2 * PI * float(x0) if False else Tv * Fr(3, 2)]
    return mc(body, '%s s' % fn(Tv), ['%s s' % fn(w) for w in wr], r=r, lv='중', fam='e',
              steps=['정지했을 때 힘의 평형: kx₀ = mg 이므로 k = mg/x₀ = %s × 10 / %s = %s N/m 이다.' % (fn(Fr(str(m))), fn(x0), fn(kk)),
                     'T = 2π√(m/k) = 2 × 3 × √(%s/%s) = %s s 이다.' % (fn(Fr(str(m))), fn(kk), fn(Tv)), '(참고: T = 2π√(x₀/g) 로도 구해진다.)'],
              core='정지 상태에서 kx₀ = mg 이고, 주기는 T = 2π√(m/k) = 2π√(x₀/g) 이다.', point='늘어난 길이로 k를 구한 뒤 주기를 계산한다.')


# ================================================================== ph087 단진자의 주기
_B87 = [
    ('단진자의 주기는 추의 질량이 클수록 길어진다.', False, '단진자의 주기는 추의 질량과 무관하다.', 'mass'),
    ('단진자의 주기는 추의 질량과 관계없다.', True, 'T = 2π√(L/g) 에 질량이 없다.', 'mass'),
    ('줄의 길이가 4배가 되면 주기는 2배가 된다.', True, 'T ∝ √L 이므로 √4 = 2배이다.', 'L'),
    ('줄의 길이가 4배가 되면 주기는 4배가 된다.', False, 'T ∝ √L 이므로 길이가 4배이면 주기는 2배이다.', 'L'),
    ('진폭(각)이 작을 때 단진자의 주기는 진폭에 거의 무관하다.', True, '작은 각에서 T = 2π√(L/g) 로 진폭과 무관하다.', 'amp'),
    ('중력 가속도가 큰 곳일수록 단진자의 주기는 길다.', False, 'T ∝ 1/√g 이므로 g가 클수록 주기가 짧다.', 'g'),
    ('달에서는 같은 단진자의 주기가 지구에서보다 길어진다.', True, '달의 g가 더 작으므로 T = 2π√(L/g) 가 커진다.', 'g'),
    ('단진자의 주기는 2π√(L/g)이다.', True, '단진자의 주기 공식이다.', 'form'),
    ('단진자의 주기는 2π√(g/L)이다.', False, '주기는 T = 2π√(L/g) 이다(L이 분자).', 'form'),
    ('진동의 가장 낮은 지점에서 추의 속력이 최대이다.', True, '위치 에너지가 최소인 곳에서 운동 에너지가 최대이다.', 'low'),
    ('진동의 양 끝점에서 추의 속력이 최대이다.', False, '끝점에서는 속력이 0이고 가장 낮은 지점에서 최대이다.', 'low'),
    ('줄의 길이가 같은 두 단진자의 주기는 추의 재질이 달라도 같다.', True, '주기는 L과 g로만 결정된다.', 'mat'),
    ('엘리베이터가 가속하며 올라가면 단진자의 주기는 길어진다.', False, '유효 중력 가속도가 g + a 로 커져 주기가 짧아진다.', 'elev'),
    ('엘리베이터가 가속하며 내려가면 단진자의 주기는 길어진다.', True, '유효 중력 가속도가 g - a 로 작아져 주기가 길어진다.', 'elev'),
    ('줄의 길이를 9배로 하면 주기는 3배가 된다.', True, 'T ∝ √L 이므로 √9 = 3배이다.', 'L2'),
    ('주기가 같은 두 단진자는 줄의 길이가 같다(같은 장소).', True, '같은 장소에서 T가 같으면 L이 같다.', 'same'),
    ('단진자의 진동수는 줄이 길수록 크다.', False, 'f = (1/2π)√(g/L) 이므로 줄이 길수록 진동수가 작다.', 'f'),
    ('단진자의 주기는 추가 올라가는 높이(진폭)에 정비례한다.', False, '주기는 진폭에 거의 무관하다.', 'amp2'),
]


@T('ph087')
def ph087(r, k):
    form = r.choice(['calc', 'calc', 'ratio', 'ratio', 'inv', 'elev', 'fig', 'fig', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B87)
        if not s: return None
        return bogi('단진자에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='d', r=r,
                    core='단진자의 주기는 T = 2π√(L/g) 이며 추의 질량·진폭(작은 각)과 무관하다.', point='주기를 결정하는 요인(L, g)을 구분한다.')
    if form == 'calc':
        g = r.choice([10, 10, 10, 5, 20, 2.5, 40])
        q = Fr(str(r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6])))
        L = q * q * Fr(str(g))
        if not term(L): return None
        Tv = 2 * PI * q
        assert Tv == 2 * PI * sqf(L / Fr(str(g)))
        place = '지구' if g == 10 else '어떤 행성'
        gtxt = '' if g == 10 else ' (이 행성의 중력 가속도는 %s m/s²이다.)' % fn(g)
        body = P('%s에서 길이 %s m인 실에 질량 %s kg인 추를 매달아 작은 각으로 진동시킨다. 이 단진자의 주기는? (단, 중력 가속도는 %s m/s², π = 3으로 계산한다.)' % (place, fn(L), r.choice(['0.1', '0.2', '0.5', '1', '2']), fn(g)))
        wr = [Tv / 2, Tv * 2, Tv / 6, 2 * PI * float(L) if False else Tv * 3, 2 * PI * float(L) / g * 2, Tv * Fr(3, 2)]
        return mc(body, '%s s' % fn(Tv), ['%s s' % fn(w) for w in wr], r=r, lv='하', fam='a',
                  steps=['T = 2π√(L/g) = 2 × 3 × √(%s/%s) 이다.' % (fn(L), fn(g)), '= 6 × %s = %s s 이다.' % (fn(q), fn(Tv))],
                  core='단진자의 주기 T = 2π√(L/g).', point='공식에 L, g를 대입한다(질량은 무관).')
    if form == 'ratio':
        kind = r.choice(['L', 'both'])
        if kind == 'L':
            a = r.choice([4, 9, 16, 25, 2, 8, 18])
            b = r.choice([1, 2, 4, 9, 16])
            fac = Fr(a, b)
            if not is_sq(fac) or fac == 1: return None
            f_ = sqf(fac)
            body = P('단진자의 줄의 길이를 %d배로 하고 추의 질량을 %d배로 하였다. 이때 주기는 처음의 몇 배가 되는가? (단, 같은 장소이며 진폭은 작다.)' % (a, b) if b > 1 else '단진자의 줄의 길이를 처음의 %s로 하였다. 같은 장소에서 주기는 처음의 몇 배가 되는가? (단, 진폭은 작다.)' % ('%d배' % a))
            right = times_str(f_)
            wr = [times_str(fac), times_str(1 / f_), times_str(1 / fac), times_str(f_ + 1), times_str(f_ * 2)]
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                      steps=['T ∝ √L 이고 질량은 주기와 무관하다.', 'T′/T = √%d = %s 이다.' % (a, right)],
                      core='단진자의 주기는 줄 길이의 제곱근에 비례하고 질량과 무관하다.', point='L의 변화만 제곱근으로 반영한다.')
        a = r.choice([2, 4, 9, 3])
        gb = r.choice([1, 2, 4, 9, 3, 8, 16])
        fac = Fr(a, gb)
        if not is_sq(fac) or fac == 1: return None
        f_ = sqf(fac)
        body = P('지구에서 주기가 T인 단진자의 줄의 길이를 %d배로 늘려, 중력 가속도가 지구의 %s인 행성에서 진동시켰다. 이 단진자의 주기는? (단, 진폭은 작다.)' % (a, '1/%d' % gb if gb > 1 else '같은 크기'))
        if gb == 1: return None
        right = '%sT' % (fn(f_) if f_ != 1 else '')
        right = ('%s T' % fn(f_)) if f_.denominator == 1 else '%d/%d T' % (f_.numerator, f_.denominator)
        wr = ['%s T' % (fn(w) if Fr(w).denominator == 1 else '%d/%d' % (Fr(w).numerator, Fr(w).denominator)) for w in [fac, 1 / f_, 1 / fac, f_ + 1, f_ * 2]]
        ans_chk = float(f_)
        assert abs(math.sqrt(a * gb) - ans_chk) > 0 or True
        # g' = g/gb -> T' = T*sqrt(a*gb)
        fac = Fr(a * gb)
        if not is_sq(fac): return None
        f_ = sqf(fac)
        right = ('%s T' % fn(f_))
        wr = ['%s T' % fn(w) for w in [Fr(a), Fr(gb), f_ * 2, f_ + 1, 1 / f_, Fr(a, gb) if a != gb else f_ + 3]]
        return mc(body, right, wr, r=r, lv='상', fam='b', sort='shuf',
                  steps=['T = 2π√(L/g) 이다. L′ = %dL, g′ = g/%d 이므로' % (a, gb), 'T′/T = √(L′g/(Lg′)) = √(%d × %d) = %s 이다.' % (a, gb, fn(f_))],
                  core='단진자의 주기는 √(L/g)에 비례한다.', point='L과 g를 동시에 바꿀 때 제곱근 안에서 함께 계산한다.')
    if form == 'inv':
        Tv = Fr(str(r.choice([0.6, 1.2, 1.8, 2.4, 3, 3.6])))
        L = 10 * Tv * Tv / (4 * PI * PI)
        if not term(L): return None
        ask = r.choice(['L', 'g'])
        if ask == 'L':
            body = P('어떤 단진자가 한 번 왕복하는 데 %s초가 걸린다. 이 단진자의 줄의 길이는? (단, 중력 가속도는 10 m/s², π = 3이고 진폭은 작다.)' % fn(Tv))
            wr = [L * 2, L / 2, L * 4, L / 4, 10 * Tv / (2 * PI)]
            return mc(body, '%s m' % fn(L), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='c',
                      steps=['T = 2π√(L/g) 에서 L = gT²/(4π²) 이다.', 'L = 10 × %s² / (4 × 9) = %s m 이다.' % (fn(Tv), fn(L))],
                      core='T = 2π√(L/g) 에서 L = gT²/4π².', point='주기 공식을 변형해 길이를 구한다.')
        g_ = r.choice([10, 5, 4, 2.5, 20])
        Lg = Fr(str(g_)) * Tv * Tv / (4 * PI * PI)
        if not term(Lg): return None
        gv = 4 * PI * PI * Lg / (Tv * Tv)
        assert gv == Fr(str(g_))
        body = P('줄의 길이가 %s m인 단진자가 어느 행성에서 주기 %s초로 진동하였다. 이 행성의 중력 가속도는? (단, π = 3이고 진폭은 작다.)' % (fn(Lg), fn(Tv)))
        wr = [gv * 2, gv / 2, gv * 4, gv / 4, gv + 5]
        return mc(body, '%s m/s²' % fn(gv), ['%s m/s²' % fn(w) for w in wr], r=r, lv='중', fam='c',
                  steps=['T = 2π√(L/g) 에서 g = 4π²L/T² 이다.', 'g = 4 × 9 × %s / %s² = %s m/s² 이다.' % (fn(Lg), fn(Tv), fn(gv))],
                  core='T = 2π√(L/g) 에서 g = 4π²L/T².', point='주기 공식을 변형해 중력 가속도를 구한다.')
    if form == 'elev':
        cases = [(30, 'up', Fr(1, 2)), (12.5, 'up', Fr(2, 3)), (7.5, 'down', Fr(2)), (80, 'up', Fr(1, 3)), (10, 'down', None)]
        a, d, fac = r.choice(cases[:4])
        geff = 10 + a if d == 'up' else 10 - a
        assert abs(math.sqrt(10 / geff) - float(fac)) < 1e-9
        txt = '가속도 %s m/s²으로 %s하는' % (fn(a), '올라가며 속력이 증가' if d == 'up' else '내려가며 속력이 증가')
        direction = '위쪽' if d == 'up' else '아래쪽'
        body = P('엘리베이터 천장에 단진자를 매달았다. 엘리베이터가 정지해 있을 때의 주기를 T라 하면, 엘리베이터가 %s 동안의 주기는? (단, 중력 가속도는 10 m/s²이고, 엘리베이터의 가속도 방향은 %s이다.)' % (txt, direction))
        right = '%sT' % (fn(fac)) if fac.denominator == 1 else '%d/%d T' % (fac.numerator, fac.denominator)
        right = ('%s T' % fn(fac)) if fac.denominator == 1 else '%d/%d T' % (fac.numerator, fac.denominator)
        def fm(w):
            w = Fr(w)
            return ('%s T' % fn(w)) if w.denominator == 1 else '%d/%d T' % (w.numerator, w.denominator)
        wr = [fm(1 / fac), fm(fac * fac), fm(1 / (fac * fac)), fm(1), fm(fac * 2), fm(fac + 1)]
        return mc(body, right, wr, r=r, lv='상', fam='e', sort='shuf',
                  steps=['엘리베이터 안에서 유효 중력 가속도는 g′ = 10 %s %s = %s m/s² 이다.' % ('+' if d == 'up' else '-', fn(a), fn(geff)),
                         'T′/T = √(g/g′) = √(10/%s) = %s 이다.' % (fn(geff), fn(fac) if fac.denominator == 1 else '%d/%d' % (fac.numerator, fac.denominator))],
                  core='가속하는 계에서 단진자의 주기는 유효 중력 가속도 g′ (위로 가속: g + a, 아래로 가속: g - a)로 계산한다.', point='가속도 방향에 따라 유효 중력 가속도를 구한다.')
    # fig: 진자 그림과 시간
    q = Fr(str(r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5])))
    L = q * q * 10
    if not term(L): return None
    Tv = 2 * PI * q
    th = r.choice([20, 25, 30, 35])
    fig = FIG(pend_fig('L = %s m' % fn(L), th), '55%')
    ask = r.choice(['quarter', 'half', 'count'])
    base = '그림은 길이 L = %s m인 단진자가 점 A와 C 사이를 왕복하는 모습이다. B는 가장 낮은 점이다. ' % fn(L)
    if ask == 'quarter':
        body = P(base + '추가 A에서 B까지 가는 데 걸리는 시간은? (단, 중력 가속도는 10 m/s², π = 3이고 공기 저항은 무시한다.)') + fig
        t = Tv / 4
        wr = [Tv / 2, Tv, Tv / 8, Tv * 3 / 4, Tv * 2]
        return mc(body, '%s s' % fn(t), ['%s s' % fn(w) for w in wr], r=r, lv='상', fam='f',
                  steps=['주기 T = 2π√(L/g) = 6 × √(%s/10) = %s s 이다.' % (fn(L), fn(Tv)), 'A에서 B까지는 1/4 주기이므로 %s / 4 = %s s 이다.' % (fn(Tv), fn(t))],
                  core='끝점에서 가장 낮은 점까지 걸리는 시간은 T/4 이다.', point='주기를 구한 뒤 1/4 주기를 계산한다.')
    if ask == 'half':
        body = P(base + '추가 A를 출발하여 C에 처음 도달하는 데 걸리는 시간은? (단, 중력 가속도는 10 m/s², π = 3이고 공기 저항은 무시한다.)') + fig
        t = Tv / 2
        wr = [Tv / 4, Tv, Tv * 2, Tv * 3 / 4, Tv / 8]
        return mc(body, '%s s' % fn(t), ['%s s' % fn(w) for w in wr], r=r, lv='중', fam='f',
                  steps=['주기 T = 2π√(L/g) = 6 × √(%s/10) = %s s 이다.' % (fn(L), fn(Tv)), 'A에서 C까지는 반 주기이므로 %s / 2 = %s s 이다.' % (fn(Tv), fn(t))],
                  core='한쪽 끝점에서 반대쪽 끝점까지는 T/2 이다.', point='주기를 구한 뒤 반 주기를 계산한다.')
    n = r.choice([2, 3, 4, 5, 6, 10])
    tt = Tv * n
    if not term(tt): return None
    body = P(base + '추가 A를 출발하여 C를 거쳐 다시 A로 돌아오는 것을 1회 왕복이라 할 때, %s초 동안 추가 왕복하는 횟수는? (단, 중력 가속도는 10 m/s², π = 3이다.)' % fn(tt)) + fig
    wr = [n * 2, max(1, n // 2) if n > 1 else 3, n + 1, n - 1, n * 3]
    return mc(body, '%d회' % n, ['%d회' % w for w in wr], r=r, lv='중', fam='f',
              steps=['주기 T = 6 × √(%s/10) = %s s 이다.' % (fn(L), fn(Tv)), '%s / %s = %d회 이다.' % (fn(tt), fn(Tv), n)],
              core='진동 횟수는 시간을 주기로 나눈 값이다.', point='주기를 구한 뒤 시간과의 비를 구한다.')


# ================================================================== ph088 복원력과 용수철 상수
_B88 = [
    ('복원력의 방향은 항상 변위의 방향과 같다.', False, '복원력은 평형 위치로 되돌리는 힘이므로 변위와 반대 방향이다.', 'dir'),
    ('복원력의 방향은 항상 변위와 반대 방향이다.', True, 'F = -kx 에서 음의 부호는 변위와 반대 방향임을 뜻한다.', 'dir'),
    ('복원력의 크기는 변위의 크기에 비례한다.', True, 'F = kx 이므로 변위에 비례한다.', 'prop'),
    ('복원력의 크기는 변위의 제곱에 비례한다.', False, '훅의 법칙에 의해 복원력은 변위의 크기에 비례한다.', 'prop'),
    ('평형 위치에서 복원력은 0이다.', True, '변위가 0이므로 F = 0 이다.', 'eq'),
    ('끝점에서 복원력의 크기가 최대이다.', True, '변위의 크기가 진폭으로 최대이므로 복원력도 최대이다.', 'end'),
    ('진동 중심에서 복원력의 크기가 최대이다.', False, '진동 중심에서는 복원력이 0이다.', 'end'),
    ('힘-변위 그래프의 기울기는 용수철 상수와 같다.', True, 'F = kx 이므로 기울기가 k이다.', 'slope'),
    ('용수철 상수가 클수록 같은 변위에서 복원력이 작다.', False, 'F = kx 이므로 k가 클수록 같은 변위에서 복원력이 크다.', 'k'),
    ('용수철 상수의 단위는 N/m이다.', True, 'k = F/x 이므로 N/m이다.', 'unit'),
    ('용수철 상수의 단위는 N·m이다.', False, 'k = F/x 이므로 단위는 N/m이다.', 'unit'),
    ('같은 용수철을 반으로 자르면 각 조각의 용수철 상수는 원래의 2배가 된다.', True, '같은 힘에서 늘어나는 길이가 1/2이 되므로 k가 2배이다.', 'cut'),
    ('같은 용수철을 반으로 자르면 각 조각의 용수철 상수는 원래의 1/2배가 된다.', False, '길이가 짧을수록 단단해져 k가 커진다(2배).', 'cut'),
    ('용수철을 2배로 늘리면 복원력의 크기도 2배가 된다.', True, 'F = kx 이므로 x가 2배이면 F도 2배이다(탄성 한계 이내).', 'dbl'),
    ('복원력의 크기가 변위에 비례하는 운동은 단진동이다.', True, 'F = -kx 꼴의 힘을 받는 운동이 단진동이다.', 'sh'),
    ('복원력이 클수록 주기가 항상 길어진다.', False, '같은 질량에서는 k가 클수록 복원력이 크고 주기는 짧다.', 'T'),
    ('x = 0 에서 알짜힘이 0이므로 물체는 반드시 정지해 있다.', False, '진동 중심에서도 속력은 최대이다. 알짜힘이 0일 뿐이다.', 'zero'),
    ('수직으로 매달린 용수철에서 물체가 정지한 위치에서는 복원력과 중력의 합이 0이다.', True, 'kx₀ = mg 이며 이 위치가 진동 중심이다.', 'hang'),
]


@T('ph088')
def ph088(r, k):
    form = r.choice(['calc', 'calc', 'graph', 'graph', 'hang', 'cut', 'cut', 'cut', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B88)
        if not s: return None
        return bogi('복원력과 용수철 상수에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='d', r=r,
                    core='복원력은 F = -kx 이며 크기는 변위에 비례하고 방향은 변위와 반대이다.', point='훅의 법칙과 복원력의 성질을 이해한다.')
    if form == 'calc':
        kk = r.choice([20, 40, 50, 100, 150, 200, 250, 400, 500])
        xcm = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
        F = Fr(kk * xcm, 100)
        if not term(F): return None
        ask = r.choice(['F', 'x', 'k'])
        if ask == 'F':
            body = P('용수철 상수가 %d N/m인 용수철을 평형 위치에서 %d cm 늘렸다. 용수철이 물체에 작용하는 복원력의 크기는?' % (kk, xcm))
            wr = [F * 100, F / 100, Fr(kk, xcm), F * 2, F / 2, Fr(kk * xcm)]
            return mc(body, '%s N' % fn(F), ['%s N' % fn(w) for w in wr], r=r, lv='하', fam='a',
                      steps=['x = %d cm = %s m 이다.' % (xcm, fn(Fr(xcm, 100))), 'F = kx = %d × %s = %s N 이다.' % (kk, fn(Fr(xcm, 100)), fn(F))],
                      core='복원력의 크기 F = kx (x는 평형 위치로부터의 변위).', point='단위(cm→m)를 맞춰 훅의 법칙을 적용한다.')
        if ask == 'x':
            body = P('용수철 상수가 %d N/m인 용수철이 물체에 %s N의 복원력을 작용하고 있다. 용수철이 평형 위치에서 늘어난 길이는?' % (kk, fn(F)))
            wr = [xcm * 10, Fr(xcm, 10), xcm * 2, Fr(xcm, 2), xcm + 5]
            return mc(body, '%d cm' % xcm, ['%s cm' % fn(w) for w in wr], r=r, lv='하', fam='a',
                      steps=['x = F/k = %s / %d = %s m = %d cm 이다.' % (fn(F), kk, fn(F / kk), xcm)],
                      core='x = F/k.', point='훅의 법칙을 변형하고 단위를 환산한다.')
        body = P('어떤 용수철을 평형 위치에서 %d cm 늘렸더니 복원력의 크기가 %s N 이었다. 이 용수철의 용수철 상수는?' % (xcm, fn(F)))
        wr = [kk * 100, Fr(kk, 100), kk * 2, Fr(kk, 2), Fr(kk, 10)]
        return mc(body, '%d N/m' % kk, ['%s N/m' % fn(w) for w in wr], r=r, lv='하', fam='a',
                  steps=['k = F/x = %s / %s = %d N/m 이다.' % (fn(F), fn(Fr(xcm, 100)), kk)],
                  core='k = F/x.', point='힘과 변위로 용수철 상수를 구한다.')
    if form == 'graph':
        kk = r.choice([20, 40, 50, 100, 200, 250])
        xmax = r.choice([4, 5, 6, 8, 10])
        F1x = r.choice([x for x in range(1, xmax + 1) if (kk * x) % 100 == 0 or True])
        pts = [(0, 0), (xmax, Fr(kk * xmax, 100))]
        Fm = Fr(kk * xmax, 100)
        xt_ = [i for i in range(0, xmax + 1) if i % (2 if xmax > 5 else 1) == 0 and i > 0]
        yt_ = [float(Fm) / 2, float(Fm)] if float(Fm) / 2 != int(Fm / 2) else [float(Fm) / 2, float(Fm)]
        fig = FIG(fx_fig([(0, 0), (xmax, float(Fm))], [xmax // 2, xmax] if xmax % 2 == 0 else [xmax], [float(Fm)], mark=(xmax, float(Fm))), '62%')
        ask = r.choice(['k', 'F', 'x'])
        base = '그림은 어떤 용수철이 늘어난 길이 x에 따라 용수철에 가해진 힘 F를 나타낸 것이다. '
        if ask == 'k':
            body = P(base + '이 용수철의 용수철 상수는?') + fig
            wr = [Fr(kk, 100), kk * 100, kk * 2, Fr(kk, 2), Fm]
            return mc(body, '%d N/m' % kk, ['%s N/m' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['그래프의 기울기가 용수철 상수이다.', 'k = F/x = %s N / %s m = %d N/m 이다. (x = %d cm = %s m)' % (fn(Fm), fn(Fr(xmax, 100)), kk, xmax, fn(Fr(xmax, 100)))],
                      core='F-x 그래프의 기울기는 용수철 상수 k이다.', point='그래프 기울기와 단위 환산.')
        x2 = r.choice([2, 3, 5, 7, 9, 1, 4])
        if x2 > xmax * 1.5: return None
        F2 = Fr(kk * x2, 100)
        if not term(F2): return None
        if ask == 'F':
            body = P(base + '이 용수철을 %d cm 늘렸을 때 용수철이 작용하는 복원력의 크기는? (단, 탄성 한계 이내이다.)' % x2) + fig
            wr = [F2 * 2, F2 / 2, Fr(x2) * 10, F2 + 1, Fr(kk * x2)]
            return mc(body, '%s N' % fn(F2), ['%s N' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['기울기에서 k = %s N/%s m = %d N/m 이다.' % (fn(Fm), fn(Fr(xmax, 100)), kk), 'F = kx = %d × %s = %s N 이다.' % (kk, fn(Fr(x2, 100)), fn(F2))],
                      core='F-x 그래프의 기울기로 k를 구하고 F = kx 를 적용한다.', point='그래프에서 k를 읽어 다른 변위에서의 힘을 구한다.')
        body = P(base + '이 용수철에 %s N의 힘을 가하면 늘어나는 길이는? (단, 탄성 한계 이내이다.)' % fn(F2)) + fig
        wr = [x2 * 2, Fr(x2, 2), x2 * 10, x2 + 2, Fr(x2, 10)]
        return mc(body, '%d cm' % x2, ['%s cm' % fn(w) for w in wr], r=r, lv='중', fam='b',
                  steps=['기울기에서 k = %d N/m 이다.' % kk, 'x = F/k = %s / %d = %s m = %d cm 이다.' % (fn(F2), kk, fn(F2 / kk), x2)],
                  core='F-x 그래프의 기울기로 k를 구하고 x = F/k.', point='그래프에서 k를 읽어 늘어난 길이를 구한다.')
    if form == 'hang':
        m1 = r.choice([0.1, 0.2, 0.3, 0.5, 1, 2])
        x1 = r.choice([2, 4, 5, 8, 10])
        kk = Fr(str(m1)) * G * 100 / x1
        if not term(kk): return None
        m2 = r.choice([x for x in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1, 1.5, 2, 3] if x != m1])
        x2 = Fr(str(m2)) * G * 100 / kk
        if not term(x2): return None
        f = Fig(260, 228)
        f.line(8, 14, 252, 14, INK, 2.2)
        for xx in range(10, 250, 8): f.line(xx, 14, xx - 5, 7, GR, 1)
        for xc, ly, mn, txt in ((70, 78, '%s kg' % fn(Fr(str(m1))), '%d cm' % x1), (190, 78 + 1.6 * (float(x2) - x1) if False else 120, '?', None)):
            pass
        L0 = 70
        ratio = float(x2) / x1
        if not (0.4 <= ratio <= 2.2): return None
        ext1 = 40.0
        ext2 = 40.0 * ratio
        vspring(f, 70, 14, 14 + L0 + ext1); f.rect(48, 14 + L0 + ext1, 44, 28, '#cfe2f7', INK, 1.8); f.text(70, 14 + L0 + ext1 + 19, fn(Fr(str(m1))) + ' kg', 11.5, 'middle', True)
        vspring(f, 190, 14, 14 + L0 + ext2); f.rect(168, 14 + L0 + ext2, 44, 28, '#cfe2f7', INK, 1.8); f.text(190, 14 + L0 + ext2 + 19, fn(Fr(str(m2))) + ' kg', 11.5, 'middle', True)
        f.line(104, 14 + L0, 126, 14 + L0, GR, 1, '4 3'); f.line(214, 14 + L0, 236, 14 + L0, GR, 1, '4 3')
        f.arrow(115, 14 + L0, 115, 14 + L0 + ext1, BL, 1.4); f.arrow(115, 14 + L0 + ext1, 115, 14 + L0, BL, 1.4)
        f.text(121, 14 + L0 + ext1 / 2 + 4, '%d cm' % x1, 12, 'start', True, BL)
        f.arrow(228, 14 + L0, 228, 14 + L0 + ext2, RD, 1.4); f.arrow(228, 14 + L0 + ext2, 228, 14 + L0, RD, 1.4)
        f.text(232, 14 + L0 + ext2 / 2 + 4, 'x', 13, 'start', True, RD)
        f.text(70, 222, '(가)', 12.5, 'middle', True, GR); f.text(190, 222, '(나)', 12.5, 'middle', True, GR)
        fig = FIG(f.svg(), '66%')
        body = P('그림 (가)는 질량 %s kg인 물체를 원래 길이의 용수철에 매달았더니 용수철이 %d cm 늘어나 정지한 모습이다. (나)는 같은 용수철에 질량 %s kg인 물체를 매달아 정지한 모습이다. (나)에서 용수철이 늘어난 길이 x는? (단, 중력 가속도는 10 m/s²이고 용수철의 질량은 무시한다.)' % (fn(Fr(str(m1))), x1, fn(Fr(str(m2))))) + fig
        assert abs(float(x2) - x1 * m2 / m1) < 1e-9
        wr = [x2 * Fr(str(m1)) / Fr(str(m2)), Fr(str(m2)) * 10, x2 * 2, x2 / 2, x2 + x1]
        return mc(body, '%s cm' % fn(x2), ['%s cm' % fn(w) for w in wr], r=r, lv='중', fam='c',
                  steps=['(가)에서 kx = mg 이므로 k = %s × 10 / %s = %s N/m 이다.' % (fn(Fr(str(m1))), fn(Fr(x1, 100)), fn(kk)),
                         '(나)에서 x = mg/k = %s × 10 / %s = %s m = %s cm 이다.' % (fn(Fr(str(m2))), fn(kk), fn(x2 / 100), fn(x2))],
                  core='정지한 물체에서 kx = mg 이므로 늘어난 길이는 질량에 비례한다.', point='힘의 평형으로 k를 구하고 다른 질량에 적용한다.')
    # cut: 용수철을 잘라 k 변화
    kk = r.choice([20, 30, 40, 60, 80, 100, 120])
    frac_ = r.choice([(1, 2), (1, 3), (1, 4), (2, 3), (3, 4)])
    a, b = frac_
    piece = Fr(a, b)
    k_new = kk / piece
    if k_new.denominator != 1: return None
    F = r.choice([2, 3, 4, 6, 8, 12])
    x_new = Fr(F) / k_new * 100
    if not term(x_new): return None
    ask = r.choice(['k', 'x'])
    if ask == 'k':
        body = P('용수철 상수가 %d N/m이고 원래 길이가 L인 용수철을 같은 용수철 재질로 길이 %s로 잘랐다. 잘라 낸 용수철의 용수철 상수는? (단, 용수철 상수는 길이에 반비례한다.)' % (kk, 'L의 %d/%d배' % (a, b) if b != 1 else 'L'))
        wr = [kk * piece, kk * 2, kk / 2, kk * b, kk + 10, kk * Fr(b, a) * Fr(b, a)]
        return mc(body, '%d N/m' % k_new, ['%s N/m' % fn(w) for w in wr], r=r, lv='중', fam='e',
                  steps=['용수철 상수는 길이에 반비례하므로 길이가 %d/%d배이면 k는 %d/%d배가 된다.' % (a, b, b, a), 'k′ = %d × %d/%d = %d N/m 이다.' % (kk, b, a, k_new)],
                  core='같은 재질의 용수철은 길이가 짧아질수록 용수철 상수가 길이에 반비례하여 커진다.', point='자른 용수철의 k를 길이 비로 구한다.')
    body = P('용수철 상수가 %d N/m이고 원래 길이가 L인 용수철을 길이 %d/%d L인 조각으로 잘랐다. 이 조각을 %d N의 힘으로 당길 때 늘어나는 길이는? (단, 용수철 상수는 길이에 반비례하고 탄성 한계 이내이다.)' % (kk, a, b, F))
    wr = [Fr(F * 100, kk), x_new * piece * piece, x_new * 2, x_new / 2, x_new + 5]
    return mc(body, '%s cm' % fn(x_new), ['%s cm' % fn(w) for w in wr], r=r, lv='상', fam='e',
              steps=['조각의 용수철 상수는 k′ = %d × %d/%d = %d N/m 이다.' % (kk, b, a, k_new), 'x = F/k′ = %d / %d = %s m = %s cm 이다.' % (F, k_new, fn(Fr(F) / k_new), fn(x_new))],
              core='자른 용수철의 k′ = k × (원래 길이/조각 길이).', point='k를 먼저 바꾼 뒤 훅의 법칙을 적용한다.')


# ================================================================== ph089 단진동의 에너지
_B89 = [
    ('단진동하는 물체의 역학적 에너지는 운동 에너지와 탄성 위치 에너지의 합이다.', True, '마찰이 없으면 E = Ek + Ep 이다.', 'sum'),
    ('진동하는 동안 운동 에너지와 탄성 위치 에너지의 합은 일정하다.', True, '역학적 에너지 보존이다.', 'const'),
    ('진동 중심에서 운동 에너지가 최대이다.', True, '중심에서 탄성 위치 에너지가 0이므로 운동 에너지가 전체 에너지와 같다.', 'center'),
    ('진동 중심에서 탄성 위치 에너지가 최대이다.', False, '중심에서 변형이 0이므로 탄성 위치 에너지는 0이다.', 'center'),
    ('끝점에서 운동 에너지는 0이다.', True, '속력이 0이므로 운동 에너지가 0이고 탄성 위치 에너지가 전체 에너지이다.', 'end'),
    ('끝점에서 탄성 위치 에너지는 0이다.', False, '끝점에서 변형이 최대이므로 탄성 위치 에너지가 최대이다.', 'end'),
    ('전체 역학적 에너지는 진폭의 제곱에 비례한다.', True, 'E = ½kA² 이다.', 'A2'),
    ('진폭이 2배가 되면 전체 역학적 에너지는 2배가 된다.', False, 'E ∝ A² 이므로 진폭이 2배이면 에너지는 4배이다.', 'A2'),
    ('진폭이 2배가 되면 최대 속력은 2배가 된다.', True, '½mv² = ½kA² 에서 v = A√(k/m) 이므로 A에 비례한다.', 'vmax'),
    ('탄성 위치 에너지는 변위의 크기에 비례한다.', False, 'Ep = ½kx² 이므로 변위의 제곱에 비례한다.', 'ep'),
    ('변위가 진폭의 1/2일 때 탄성 위치 에너지는 전체 에너지의 1/4이다.', True, 'Ep/E = (x/A)² = 1/4 이다.', 'half'),
    ('변위가 진폭의 1/2일 때 운동 에너지는 전체 에너지의 1/2이다.', False, 'Ek = E - Ep = E - E/4 = 3E/4 이다.', 'half'),
    ('운동 에너지가 최대일 때 알짜힘의 크기도 최대이다.', False, '운동 에너지가 최대인 중심에서는 알짜힘이 0이다.', 'force'),
    ('탄성 위치 에너지가 최대일 때 가속도의 크기도 최대이다.', True, '끝점에서 변위가 최대이므로 복원력과 가속도의 크기가 모두 최대이다.', 'force'),
    ('용수철 상수가 2배인 용수철 진자에서 같은 진폭이면 전체 에너지는 2배이다.', True, 'E = ½kA² 이므로 k에 비례한다.', 'k'),
    ('운동 에너지가 최대가 되는 시각은 한 주기에 한 번뿐이다.', False, '중심을 한 주기에 두 번 지나므로 두 번이다.', 'cnt'),
    ('물체의 질량이 달라도 진폭과 용수철 상수가 같으면 전체 에너지는 같다.', True, 'E = ½kA² 에 질량이 없다.', 'm'),
    ('운동 에너지와 탄성 위치 에너지가 같아지는 곳의 변위는 진폭의 1/2이다.', False, 'Ek = Ep 이면 ½kx² = ¼kA² 이므로 x = A/√2 이다.', 'eq'),
]


@T('ph089')
def ph089(r, k):
    form = r.choice(['E', 'E', 'Ek', 'v', 'ratio', 'graph', 'graph', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B89)
        if not s: return None
        return bogi('마찰이 없는 수평면에서 용수철 진자가 단진동할 때의 에너지에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='e', r=r,
                    core='단진동의 역학적 에너지 E = ½kA² 는 일정하고, 중심에서는 운동 에너지, 끝점에서는 탄성 위치 에너지만 가진다.', point='위치에 따른 에너지 분배를 판단한다.')
    if form == 'E':
        kk = r.choice([20, 50, 100, 200, 400, 500, 800])
        A = r.choice([2, 4, 5, 10, 20, 25])
        E = Fr(kk * A * A, 2 * 10000)
        if not term(E): return None
        body = P('용수철 상수가 %d N/m인 용수철에 연결된 물체가 진폭 %d cm로 단진동하고 있다. 이 진동의 전체 역학적 에너지는? (단, 마찰은 무시한다.)' % (kk, A))
        wr = [E * 100, E / 100, E * 2, E / 2, Fr(kk * A, 100)]
        wr = [Fr(str(w)) for w in wr]
        return mc(body, '%s J' % fn(E), ['%s J' % fn(w) for w in wr], r=r, lv='하', fam='a',
                  steps=['A = %d cm = %s m 이다.' % (A, fn(Fr(A, 100))), 'E = ½kA² = ½ × %d × (%s)² = %s J 이다.' % (kk, fn(Fr(A, 100)), fn(E))],
                  core='단진동의 역학적 에너지 E = ½kA².', point='진폭을 m로 바꿔 E = ½kA² 에 대입한다.')
    if form == 'Ek':
        kk = r.choice([40, 100, 200, 250, 400, 500])
        A, x = r.choice([(10, 6), (10, 8), (5, 3), (5, 4), (20, 12), (20, 16), (10, 5), (10, 2), (4, 2), (20, 10)])
        E = Fr(kk * A * A, 20000)
        Ep = Fr(kk * x * x, 20000)
        Ek = E - Ep
        if not term(E) or not term(Ep) or Ek == 0: return None
        ask = r.choice(['Ek', 'Ep'])
        body = P('용수철 상수가 %d N/m인 용수철 진자가 진폭 %d cm로 단진동하고 있다. 중심에서 %d cm 떨어진 지점에서 물체의 %s는? (단, 마찰은 무시한다.)' % (kk, A, x, '운동 에너지' if ask == 'Ek' else '탄성 위치 에너지'))
        ans = Ek if ask == 'Ek' else Ep
        oth = Ep if ask == 'Ek' else Ek
        wr = [oth, E, ans * 2, ans / 2, Fr(kk * (A - x) * (A - x), 20000) if (A - x) else ans + 1, E + ans]
        assert Ek + Ep == E
        return mc(body, '%s J' % fn(ans), ['%s J' % fn(w) for w in wr], r=r, lv='중', fam='b',
                  steps=['전체 에너지 E = ½kA² = ½ × %d × (%s)² = %s J 이다.' % (kk, fn(Fr(A, 100)), fn(E)), 'Ep = ½kx² = ½ × %d × (%s)² = %s J 이다.' % (kk, fn(Fr(x, 100)), fn(Ep)),
                         ('Ek = E - Ep = %s - %s = %s J 이다.' % (fn(E), fn(Ep), fn(Ek))) if ask == 'Ek' else 'Ep = %s J 이다.' % fn(Ep)],
                  core='위치 x에서 Ep = ½kx², Ek = ½k(A² - x²).', point='전체 에너지에서 위치 에너지를 빼 운동 에너지를 구한다.')
    if form == 'v':
        m = r.choice([0.5, 1, 2, 4, 0.2, 0.1])
        q = Fr(str(r.choice([1, 2, 3, 4, 5, 10, 6])))
        kk = Fr(str(m)) * q * q
        if kk.denominator != 1 or kk > 600: return None
        A = r.choice([0.1, 0.2, 0.3, 0.05, 0.4])
        vmax = Fr(str(A)) * q
        if not term(vmax): return None
        assert abs(0.5 * m * float(vmax) ** 2 - 0.5 * float(kk) * A * A) < 1e-9
        body = P('질량 %s kg인 물체가 용수철 상수 %d N/m인 용수철에 연결되어 진폭 %s m로 단진동한다. 이 물체의 최대 속력은? (단, 마찰은 무시한다.)' % (fn(Fr(str(m))), kk, fn(Fr(str(A)))))
        wr = [vmax / 2, vmax * 2, vmax * q, vmax / q if q > 1 else vmax + 1, vmax * vmax]
        return mc(body, '%s m/s' % fn(vmax), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='c',
                  steps=['중심에서 탄성 위치 에너지가 모두 운동 에너지로 바뀌므로 ½mv² = ½kA² 이다.', 'v = A√(k/m) = %s × √(%d/%s) = %s × %s = %s m/s 이다.' % (fn(Fr(str(A))), kk, fn(Fr(str(m))), fn(Fr(str(A))), fn(q), fn(vmax))],
                  core='단진동의 최대 속력은 ½mv² = ½kA² 에서 v = A√(k/m).', point='역학적 에너지 보존으로 최대 속력을 구한다.')
    if form == 'ratio':
        pick = r.choice([(Fr(1, 2), 'x=A/2'), (Fr(1, 3), 'x=A/3'), (Fr(1, 4), 'x=A/4'), (Fr(2, 3), 'x=2A/3'), (Fr(3, 5), 'x=3A/5'), (Fr(4, 5), 'x=4A/5')])
        fr_, name = pick
        ep = fr_ * fr_
        ek = 1 - ep
        right = ratio_str(ek, ep)
        xs = '%d/%d' % (fr_.numerator, fr_.denominator)
        body = P('용수철 진자가 진폭 A로 단진동한다. 중심으로부터의 변위가 %sA인 지점에서 운동 에너지와 탄성 위치 에너지의 비 Ek : Ep는? (단, 마찰은 무시한다.)' % xs)
        wr = [ratio_str(ep, ek), ratio_str(1 - fr_, fr_), ratio_str(fr_, 1 - fr_), ratio_str(1 - ep, 1), '1 : 1']
        return mc(body, right, wr, r=r, lv='상' if fr_.denominator > 3 else '중', fam='b', sort='shuf',
                  steps=['Ep/E = (x/A)² = (%s)² = %s 이다.' % (xs, '%d/%d' % (ep.numerator, ep.denominator)), 'Ek/E = 1 - %d/%d = %d/%d 이므로 Ek : Ep = %s 이다.' % (ep.numerator, ep.denominator, ek.numerator, ek.denominator, right)],
                  core='Ep = E (x/A)², Ek = E [1 - (x/A)²].', point='변위 비로 에너지 비를 구한다.')
    # graph
    A = r.choice([2, 4, 5, 10])
    E = r.choice([4, 8, 16, 20, 24, 32, 40])
    c = r.choice([Fr(1, 2), Fr(1, 4), Fr(3, 4)])
    x0 = A * c
    Ep0 = E * c * c
    if not term(x0) or not term(Ep0): return None
    fig = FIG(en_fig(A, E, float(x0), float(Ep0)), '70%')
    ask = r.choice(['Ek', 'k', 'v'])
    base = '그림은 용수철 진자의 전체 역학적 에너지 E(초록선)와 탄성 위치 에너지(파란 곡선)를 변위 x에 따라 나타낸 것이다. '
    if ask == 'Ek':
        body = P(base + 'x = %s cm 에서 물체의 운동 에너지는? (단, 마찰은 무시한다.)' % fn(x0)) + fig
        Ek = E - Ep0
        wr = [Ep0, E, Ek * 2, Ek / 2, E + Ep0]
        return mc(body, '%s J' % fn(Ek), ['%s J' % fn(w) for w in wr], r=r, lv='중', fam='d',
                  steps=['그래프에서 전체 에너지 E = %s J, x = %s cm 에서 탄성 위치 에너지는 %s J 이다.' % (fn(E), fn(x0), fn(Ep0)), 'Ek = E - Ep = %s - %s = %s J 이다.' % (fn(E), fn(Ep0), fn(Ek))],
                  core='역학적 에너지 E = Ek + Ep 이다.', point='그래프에서 E와 Ep를 읽어 Ek를 구한다.')
    if ask == 'k':
        kk = Fr(2 * E) / (Fr(A, 100) ** 2)
        if kk.denominator != 1 or kk > 10 ** 7: return None
        body = P(base + '이 용수철의 용수철 상수는?') + fig
        wr = [kk / 2, kk * 2, kk / 100, Fr(2 * E, A), kk / 4]
        return mc(body, '%d N/m' % kk, ['%s N/m' % fn(w) for w in wr], r=r, lv='상', fam='d',
                  steps=['끝점(x = ±%d cm)에서 Ep = E 이므로 ½kA² = %s J 이다.' % (A, fn(E)), 'k = 2E/A² = 2 × %s / (%s)² = %d N/m 이다.' % (fn(E), fn(Fr(A, 100)), kk)],
                  core='E = ½kA² 이므로 k = 2E/A².', point='끝점에서 전체 에너지가 탄성 위치 에너지임을 이용한다.')
    kk = Fr(2 * E) / (Fr(A, 100) ** 2)
    m = r.choice([1, 2, 4, 0.5])
    vmax2 = Fr(2 * E) / Fr(str(m))
    if not is_sq(vmax2): return None
    vmax = sqf(vmax2)
    body = P(base + '물체의 질량이 %s kg이라면 진동 중심에서의 속력은? (단, 마찰은 무시한다.)' % fn(Fr(str(m)))) + fig
    wr = [vmax / 2, vmax * 2, vmax2, Fr(E) / Fr(str(m)), vmax + 1]
    return mc(body, '%s m/s' % fn(vmax), ['%s m/s' % fn(w) for w in wr], r=r, lv='상', fam='d',
              steps=['중심에서 Ek = E = %s J 이다.' % fn(E), '½mv² = E 에서 v = √(2E/m) = √(2 × %s / %s) = %s m/s 이다.' % (fn(E), fn(Fr(str(m))), fn(vmax))],
              core='중심에서 운동 에너지가 전체 에너지와 같다.', point='그래프의 전체 에너지로 최대 속력을 구한다.')


# ================================================================== ph090 등속 원운동과 단진동
_B90 = [
    ('등속 원운동하는 물체를 한 지름 위로 정사영시킨 점의 운동은 단진동이다.', True, '원운동의 정사영은 단진동이다.', 'proj'),
    ('정사영의 운동은 등속 직선 운동이다.', False, '정사영의 속도는 위치에 따라 변하므로 등속이 아니라 단진동이다.', 'proj'),
    ('단진동의 진폭은 원운동의 반지름과 같다.', True, '정사영의 최대 변위가 반지름이다.', 'amp'),
    ('단진동의 주기는 원운동의 주기와 같다.', True, '원이 한 바퀴 도는 동안 정사영은 한 번 왕복한다.', 'T'),
    ('단진동의 주기는 원운동의 주기의 절반이다.', False, '정사영은 원이 한 바퀴 돌 때 한 번 왕복하므로 주기가 같다.', 'T'),
    ('단진동의 최대 속력은 원운동의 속력과 같다.', True, '중심을 지날 때 정사영의 속도가 원운동의 속도와 나란하다.', 'vmax'),
    ('정사영이 진동 중심을 지날 때 속력이 최대이다.', True, '이때 원 위의 물체의 속도가 정사영 방향과 나란하다.', 'center'),
    ('정사영이 끝점에 있을 때 속력이 최대이다.', False, '끝점에서는 원 위의 물체의 속도가 정사영 방향에 수직이므로 속력이 0이다.', 'center'),
    ('단진동의 가속도의 최대 크기는 원운동의 구심 가속도의 크기와 같다.', True, '끝점에서 구심 가속도가 정사영 방향과 나란하다.', 'amax'),
    ('단진동의 가속도는 항상 원운동의 구심 가속도와 같다.', False, '정사영의 가속도는 구심 가속도의 성분이므로 같지 않다(최대일 때만 같다).', 'amax'),
    ('원운동의 각속도는 단진동의 각진동수와 같다.', True, 'ω = 2π/T 로 같다.', 'omega'),
    ('원운동의 반지름이 2배가 되고 주기가 같으면 단진동의 최대 속력은 2배이다.', True, 'v = 2πA/T 에서 A에 비례한다.', 'r2'),
    ('원운동의 반지름이 2배가 되면 단진동의 주기도 2배가 된다(각속도 일정).', False, '각속도가 같으면 주기가 같다.', 'r2b'),
    ('원운동의 속력이 일정하므로 정사영의 속력도 일정하다.', False, '정사영의 속력은 sinθ에 비례해 변한다.', 'const'),
    ('원 위의 물체가 한 바퀴 도는 동안 정사영은 반지름의 4배를 이동한다.', True, '정사영은 4A를 이동한다.', 'path'),
    ('원운동의 진동수가 f이면 단진동의 진동수는 2f이다.', False, '단진동의 진동수도 f이다.', 'f'),
    ('원 위의 물체가 반 바퀴 도는 동안 정사영은 지름만큼 이동한다.', True, '반 바퀴 동안 정사영은 한쪽 끝에서 반대쪽 끝으로 이동하여 2A를 이동한다.', 'half'),
    ('정사영이 중심을 지나는 순간 원 위의 물체의 위치는 정사영 축에 수직인 반지름의 끝이다.', True, '정사영 위치가 0이면 물체는 축에 수직인 지름 위에 있다.', 'pos'),
]


@T('ph090')
def ph090(r, k):
    form = r.choice(['calc', 'calc', 'fig', 'fig', 'graph', 'graph', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B90)
        if not s: return None
        return bogi('등속 원운동하는 물체를 한 지름 위에 정사영시킨 점의 운동에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='d', r=r,
                    core='등속 원운동의 정사영은 단진동이며, 진폭은 반지름, 주기는 원운동의 주기, 최대 속력은 원운동의 속력과 같다.', point='원운동과 단진동의 대응 관계를 판단한다.')
    if form == 'calc':
        Rr = r.choice([2, 3, 4, 5, 6, 8, 10, 12])
        Tv = r.choice([1, 2, 3, 4, 6, 12, 5, 10])
        ask = r.choice(['v', 'a', 'amp'])
        v = Fr(2 * PI * Rr, Tv)
        a = Fr(4 * PI * PI * Rr, Tv * Tv)
        if not term(v) or not term(a): return None
        fig = FIG(circ_fig('%d cm' % Rr, r.choice([0, 60, 120, 45])), '48%')
        base = '그림과 같이 반지름이 %d cm인 원 위에서 점 P가 주기 %d s로 등속 원운동을 한다. 점 Q는 P에서 지름 위로 내린 수선의 발이다. ' % (Rr, Tv)
        if ask == 'v':
            body = P(base + 'Q의 최대 속력은? (단, π = 3으로 계산한다.)') + fig
            wr = [v / 2, v * 2, Fr(Rr, Tv), v * 3, Fr(2 * PI * Rr)]
            return mc(body, '%s cm/s' % fn(v), ['%s cm/s' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['P의 속력 v = 2πR/T = 2 × 3 × %d / %d = %s cm/s 이다.' % (Rr, Tv, fn(v)), 'Q의 최대 속력은 P의 속력과 같으므로 %s cm/s 이다.' % fn(v)],
                      core='단진동의 최대 속력은 원운동의 속력 2πA/T 와 같다.', point='정사영의 최대 속력 = 원운동 속력.')
        if ask == 'a':
            body = P(base + 'Q의 가속도의 최대 크기는? (단, π = 3으로 계산한다.)') + fig
            wr = [a / 2, a * 2, v, Fr(Rr, Tv * Tv), a * 3]
            return mc(body, '%s cm/s²' % fn(a), ['%s cm/s²' % fn(w) for w in wr], r=r, lv='상', fam='a',
                      steps=['P의 구심 가속도 a = 4π²R/T² = 4 × 9 × %d / %d² = %s cm/s² 이다.' % (Rr, Tv, fn(a)), 'Q의 가속도의 최대 크기는 구심 가속도의 크기와 같으므로 %s cm/s² 이다.' % fn(a)],
                      core='단진동의 최대 가속도는 원운동의 구심 가속도 4π²R/T² 와 같다.', point='정사영의 최대 가속도 = 구심 가속도.')
        body = P(base + 'Q의 진동의 진폭과 주기는?') + fig
        right = '%d cm, %d s' % (Rr, Tv)
        wr = ['%d cm, %d s' % (2 * Rr, Tv), '%d cm, %s s' % (Rr, fn(Fr(Tv, 2))), '%d cm, %d s' % (Rr, 2 * Tv), '%d cm, %d s' % (Rr * 2, 2 * Tv), '%s cm, %d s' % (fn(Fr(Rr, 2)), Tv)]
        return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf',
                  steps=['정사영의 진폭은 원의 반지름 %d cm 와 같다.' % Rr, '원이 한 바퀴 도는 동안 Q는 한 번 왕복하므로 주기는 %d s 이다.' % Tv],
                  core='정사영의 진폭 = 원의 반지름, 주기 = 원운동의 주기.', point='원운동과 단진동의 대응.')
    if form == 'fig':
        Rr = r.choice([5, 10, 15, 20, 25, 30, 40])
        th = r.choice([37, 53, 127, 143, 217, 233, 307, 323, 60, 120])
        Tv = r.choice([2, 4, 5, 6, 10, 12, 3])
        ask = r.choice(['x', 'x', 'v', 't'])
        c = {37: Fr(4, 5), 53: Fr(3, 5), 127: Fr(-3, 5), 143: Fr(-4, 5), 217: Fr(-4, 5), 233: Fr(-3, 5), 307: Fr(3, 5), 323: Fr(4, 5), 60: Fr(1, 2), 120: Fr(-1, 2)}[th]
        s = {37: Fr(3, 5), 53: Fr(4, 5), 127: Fr(4, 5), 143: Fr(3, 5), 217: Fr(-3, 5), 233: Fr(-4, 5), 307: Fr(-4, 5), 323: Fr(-3, 5)}.get(th)
        fig = FIG(circ_fig('%d cm' % Rr, th, qname='Q'), '50%')
        base = '그림은 반지름 %d cm인 원 위에서 등속 원운동하는 점 P와, P에서 지름 위로 내린 수선의 발 Q를 나타낸 것이다. 그림의 순간 OP가 지름과 이루는 각은 %d°이고, 이때 sin·cos 값은 sin37° = 0.6, cos37° = 0.8, sin53° = 0.8, cos53° = 0.6 이다. ' % (Rr, th if th < 180 else th)
        if ask == 'x' and th not in (60, 120):
            xv = Rr * c
            if not term(xv): return None
            assert abs(float(xv) - Rr * math.cos(math.radians(th))) < 0.3 * Rr * 0.05 + 0.5
            body = P('그림은 반지름 %d cm인 원 위에서 등속 원운동하는 점 P와, P에서 지름 위로 내린 수선의 발 Q를 나타낸 것이다. 원의 중심 O를 원점으로 하고 오른쪽을 +x로 할 때, OP가 +x 방향과 이루는 각이 %d°인 순간 Q의 위치 x는? (단, sin37° = 0.6, cos37° = 0.8이다.)' % (Rr, th)) + fig
            wr = [-xv, Rr * (s if s else c) if s else Rr, abs(xv), Rr * Fr(1, 2) * (1 if xv > 0 else -1), Fr(Rr * (th % 180), 100), xv * 2 if abs(xv * 2) <= 2 * Rr else xv / 2, Rr * (Fr(3, 5) if abs(c) == Fr(4, 5) else Fr(4, 5)) * (1 if xv > 0 else -1)]
            return mc(body, '%s cm' % fn(xv), ['%s cm' % fn(w) for w in wr], r=r, lv='중', fam='b', sort='shuf',
                      steps=['Q의 위치는 P의 x좌표이므로 x = R cosθ 이다.', 'θ = %d° 에서 cos%d° = %s 이므로 x = %d × %s = %s cm 이다.' % (th, th, fn(c), Rr, fn(c), fn(xv))],
                      core='정사영의 위치는 x = R cosθ 이다.', point='각도로 정사영의 위치를 구한다.')
        if ask == 'v' and s is not None:
            vc = Fr(2 * PI * Rr, Tv)
            vq = abs(vc * s)
            if not term(vq) or not term(vc): return None
            body = P('그림은 반지름 %d cm인 원 위에서 주기 %d s로 등속 원운동하는 점 P와, P에서 지름 위로 내린 수선의 발 Q를 나타낸 것이다. OP가 지름과 이루는 각이 %d°인 순간 Q의 속력은? (단, π = 3, sin37° = 0.6, cos37° = 0.8이다.)' % (Rr, Tv, th)) + fig
            wr = [vc, vc * abs(c), vc * Fr(1, 2), vc * 2, vc * (1 - abs(s))]
            return mc(body, '%s cm/s' % fn(vq), ['%s cm/s' % fn(w) for w in wr], r=r, lv='상', fam='b', sort='shuf',
                      steps=['P의 속력 v = 2πR/T = 2 × 3 × %d / %d = %s cm/s 이다.' % (Rr, Tv, fn(vc)), 'Q의 속력은 P의 속도의 지름 방향 성분이므로 v|sinθ| = %s × %s = %s cm/s 이다.' % (fn(vc), fn(abs(s)), fn(vq))],
                      core='정사영의 속력은 원운동의 속력에 |sinθ| 를 곱한 값이다.', point='속도를 성분으로 분해한다.')
        # t: 몇 초 걸리나
        deg = r.choice([60, 90, 120, 180, 270, 45, 30])
        t = Fr(Tv * deg, 360)
        if not term(t): return None
        body = P('반지름이 %d cm인 원 위의 점 P가 주기 %d s로 등속 원운동을 한다. 점 Q는 P에서 지름 위로 내린 수선의 발이다. P가 +x축 위(Q가 한쪽 끝점)에서 출발하여 %d° 회전하는 데 걸리는 시간은?' % (Rr, Tv, deg)) + FIG(circ_fig('%d cm' % Rr, 0), '48%')
        wr = [Fr(Tv * deg, 180), t / 2, Tv - t if Tv != 2 * t else t + 1, Fr(Tv), t * 3, Fr(deg, Tv)]
        return mc(body, '%s s' % fn(t), ['%s s' % fn(w) for w in wr], r=r, lv='중', fam='b',
                  steps=['P는 %d s 동안 360° 회전하므로 %d° 회전하는 데 %d × %d/360 = %s s 이다.' % (Tv, deg, Tv, deg, fn(t))],
                  core='등속 원운동에서 회전 각은 시간에 비례한다.', point='회전 각과 시간의 비례 관계.')
    # graph: x-t 그래프에서 원운동 읽기
    A = r.choice([2, 3, 4, 5, 6, 10])
    Tv = r.choice([1, 2, 3, 4, 6, 12])
    kind = r.choice(['sin', 'cos'])
    fig = FIG(xt_fig([(A, Tv, kind, BL, '')], Tv * 1.25, [Tv / 4 * i for i in range(1, 6)], [-A, A]), '66%')
    ask = r.choice(['R', 'v', 'w'])
    base = '그림은 단진동하는 물체의 변위 x를 시간 t에 따라 나타낸 것이다. 이 물체는 어떤 등속 원운동하는 점을 지름 위에 정사영시킨 점의 운동과 같다. '
    if ask == 'R':
        body = P(base + '이 원운동의 반지름과 주기를 옳게 짝지은 것은?') + fig
        right = '%d cm, %d s' % (A, Tv)
        wr = ['%d cm, %d s' % (2 * A, Tv), '%d cm, %d s' % (A, 2 * Tv), '%d cm, %s s' % (A, fn(Fr(Tv, 2))), '%d cm, %d s' % (2 * A, 2 * Tv), '%s cm, %d s' % (fn(Fr(A, 2)), Tv)]
        return mc(body, right, wr, r=r, lv='하', fam='c', sort='shuf',
                  steps=['그래프에서 진폭 A = %d cm, 주기 T = %d s 이다.' % (A, Tv), '원운동의 반지름은 진폭과 같은 %d cm, 주기는 %d s 이다.' % (A, Tv)],
                  core='원운동의 반지름 = 단진동의 진폭, 원운동의 주기 = 단진동의 주기.', point='그래프에서 원운동의 반지름과 주기를 읽는다.')
    v = Fr(2 * PI * A, Tv)
    if not term(v): return None
    if ask == 'v':
        body = P(base + '이 원운동하는 점의 속력은? (단, π = 3으로 계산한다.)') + fig
        wr = [v / 2, v * 2, Fr(A, Tv), v * 3, Fr(A * Tv)]
        return mc(body, '%s cm/s' % fn(v), ['%s cm/s' % fn(w) for w in wr], r=r, lv='중', fam='c',
                  steps=['반지름 R = A = %d cm, 주기 T = %d s 이다.' % (A, Tv), 'v = 2πR/T = 2 × 3 × %d / %d = %s cm/s 이다.' % (A, Tv, fn(v))],
                  core='원운동의 속력 v = 2πR/T 는 단진동의 최대 속력과 같다.', point='그래프에서 R, T를 읽어 속력을 구한다.')
    w_ = Fr(2 * PI, Tv)
    body = P(base + '이 원운동의 각속도는? (단, π = 3으로 계산한다.)') + fig
    wr = [w_ / 2, w_ * 2, Fr(1, Tv), w_ * A, Fr(2 * PI * A, Tv)]
    return mc(body, '%s rad/s' % fn(w_), ['%s rad/s' % fn(w) for w in wr], r=r, lv='중', fam='c',
              steps=['그래프에서 주기 T = %d s 이다.' % Tv, 'ω = 2π/T = 2 × 3 / %d = %s rad/s 이다.' % (Tv, fn(w_))],
              core='각속도 ω = 2π/T.', point='주기에서 각속도를 구한다.')
