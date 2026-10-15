# -*- coding: utf-8 -*-
"""Ⅲ-B 탄성파 (ph091~ph097) 생성기."""
from phlib import *
import math, itertools
from fractions import Fraction as Fr


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


def fr_str(q):
    q = Fr(q)
    return str(q.numerator) if q.denominator == 1 else '%d/%d' % (q.numerator, q.denominator)


def times_str(q):
    q = Fr(q)
    return '%s배' % fr_str(q)


def ratio_str(a, b):
    q = Fr(a) / Fr(b)
    return '%d : %d' % (q.numerator, q.denominator)


def is_sq(fr):
    fr = Fr(fr)
    return math.isqrt(fr.numerator) ** 2 == fr.numerator and math.isqrt(fr.denominator) ** 2 == fr.denominator


def pick3(r, pool):
    for _ in range(40):
        s = r.sample(pool, 3)
        if len({x[3] for x in s}) < 3: continue
        if any(x[1] for x in s): return [(a, b, c) for a, b, c, _ in s]
    return None


def pick3_dyn(r, cands):
    """동적으로 만든 후보(문장, 참거짓, 풀이, 그룹)에서 서로 다른 그룹 3개, 참 최소 1개."""
    for _ in range(60):
        s = r.sample(cands, 3)
        if len({x[3] for x in s}) < 3: continue
        if any(x[1] for x in s): return [(a, b, c) for a, b, c, _ in s]
    return None


def two_fig(a, b):
    return '<div style="display:flex;gap:6px;justify-content:center">' + FIG(a, '49%') + FIG(b, '49%') + '</div>'


# ------------------------------------------------------------------ 그림
def wgraph(funcs, xmax, ymax, xticks, yticks, xlab, ylab, w=330, h=190, extra=None, title=None, xfmt=None, ymul=1.45, lift=0):
    """funcs: [(함수, 색, 선굵기, 점선)]."""
    ym = ymax * ymul
    p = Plot(w, h, xmax * 1.05, ym, xmin=0, ymin=-ym, ml=44, mr=14, mt=16, mb=38)
    p.axes(xlab, ylab, (), yticks, grid=True, origin=False)
    ff = xfmt or fn
    for t in xticks:
        p.line(p.px(t), p.py(-ym), p.px(t), p.py(ym), LG, 1)
        p.line(p.px(t), p.py(0) - 3, p.px(t), p.py(0) + 3, INK, 1)
        p.text(p.px(t), h - 22, ff(t), 11.5, 'middle', c=GR)
    for (f, col, sw, dash) in funcs:
        N = 200
        p.pl([(xmax * i / N, f(xmax * i / N)) for i in range(N + 1)], col, sw, dash)
    if extra: extra(p)
    if title: p.text(w - 20, 14, title, 13, 'end', True, GR)
    return p.svg()


def sinf(A, lam, ph=0.0):
    return lambda x: A * math.sin(2 * math.pi * x / lam + ph)


def pulse_fig(pulses, W, rows=3, wall=None, wall_kind=None, w=330, ticks_every=2, marks=(), arrows=(), title=None, xlab='x (cm)'):
    """눈금 위의 삼각 펄스. pulses: [(중심, 높이, 반폭, 색, 점선)]. 눈금 한 칸 = 1.  W: 가로 칸 수."""
    cell = (w - 50) / W
    h = 40 + rows * 2 * cell + 36
    f = Fig(w, h)
    ox, oy = 28, 20 + rows * cell
    for i in range(W + 1):
        f.line(ox + i * cell, oy - rows * cell, ox + i * cell, oy + rows * cell, LG, 1)
    for j in range(-rows, rows + 1):
        f.line(ox, oy + j * cell, ox + W * cell, oy + j * cell, LG, 1)
    f.line(ox, oy, ox + W * cell + 8, oy, INK, 1.6)
    for i in range(0, W + 1, ticks_every):
        f.text(ox + i * cell, oy + rows * cell + 16, str(i), 11.5, 'middle', c=GR)
    f.text(ox + W * cell + 22, oy + rows * cell + 32, xlab, 12, 'end', True, GR)
    for j in range(-rows, rows + 1):
        if j != 0 and (j % 1 == 0): f.text(ox - 6, oy - j * cell + 4, str(j), 11, 'end', c=GR)
    if wall is not None:
        wx = ox + wall * cell
        if wall_kind == 'fixed':
            f.line(wx, oy - rows * cell - 4, wx, oy + rows * cell + 4, INK, 3.2)
            for j in range(-rows * 2, rows * 2 + 1):
                f.line(wx, oy + j * cell / 2, wx + 7, oy + j * cell / 2 + 6, GR, 1)
            f.text(wx - 4, oy - rows * cell - 8, '고정단', 12, 'end', True, GR)
        else:
            f.line(wx, oy - rows * cell - 4, wx, oy + rows * cell + 4, '#9aa7b8', 1.6, '5 3')
            f.rect(wx - 3, oy - 5, 6, 10, '#cfe2f7', INK, 1.4)
            f.text(wx - 4, oy - rows * cell - 8, '자유단', 12, 'end', True, GR)
    for (c, hh, hw, col, dash) in pulses:
        pts = [(ox + (c - hw) * cell, oy), (ox + c * cell, oy - hh * cell), (ox + (c + hw) * cell, oy)]
        f.poly(pts, 'none', col, 2.6, close=False, dash=dash)
    for (x, y, lab) in marks:
        f.circ(ox + x * cell, oy - y * cell, 3.8, INK, INK, 1)
        f.text(ox + x * cell, oy - y * cell - 8 if y >= 0 else oy - y * cell + 17, lab, 13.5, 'middle', True, INK)
    for (x1, x2, yy, col, lab) in arrows:
        f.arrow(ox + x1 * cell, oy - yy * cell, ox + x2 * cell, oy - yy * cell, col, 2)
        f.text(ox + (x1 + x2) / 2 * cell, oy - yy * cell - 6, lab, 12, 'middle', True, col)
    if title: f.text(w - 6, 14, title, 13, 'end', True, GR)
    return f.svg()


def tri(x, c, h, hw):
    return h * max(0.0, 1 - abs(x - c) / hw)


def tl_panels(kinds, w=330, h=120):
    """kinds: 각 패널의 'T'(진동 방향이 진행 방향에 수직) 또는 'L'(나란함)."""
    f = Fig(w, h)
    n = len(kinds)
    pw = w / n
    for i, kd in enumerate(kinds):
        cx = pw * i + pw / 2
        f.text(cx, 14, '(%s)' % '가나다라'[i], 13, 'middle', True, GR)
        for j in range(-3, 4):
            f.circ(cx + j * 14, 62, 2.6, GR, GR, 1)
        f.circ(cx, 62, 5, RD, RD, 1)
        if kd == 'T':
            f.arrow(cx, 62, cx, 28, RD, 2); f.arrow(cx, 62, cx, 96, RD, 2)
            f.text(cx + 7, 36, '진동', 12, 'start', True, RD)
        else:
            f.arrow(cx, 62, cx - 36, 62, RD, 2); f.arrow(cx, 62, cx + 36, 62, RD, 2)
            f.text(cx, 48, '진동', 12, 'middle', True, RD)
        f.arrow(cx - 30, 112, cx + 30, 112, BL, 2.2)
        f.text(cx, 107, '파동의 진행', 11.5, 'middle', True, BL)
    return f.svg()


def long_fig(lam_cm, nwave=3, w=330, h=130, marks=True, cm_per_px=None):
    """종파(용수철 파동): 밀한 곳·소한 곳. 아래에 cm 눈금자."""
    f = Fig(w, h)
    x0 = 24
    px_per = (w - 50) / (lam_cm * nwave + lam_cm * 0.0)
    lam = lam_cm * px_per
    a = 0.14 * lam
    xs = []
    n = int(nwave * lam / 8) + 1
    for i in range(n + 1):
        xe = i * 8.0
        if xe > nwave * lam + 0.5: break
        xs.append(xe + a * math.sin(2 * math.pi * xe / lam))
    for x in xs:
        f.line(x0 + x, 26, x0 + x, 72, INK, 1.6)
    f.line(x0, 100, x0 + nwave * lam, 100, INK, 1.4)
    for c in range(0, int(round(lam_cm * nwave)) + 1):
        f.line(x0 + c * px_per, 100, x0 + c * px_per, 106 if c % 2 else 110, INK, 1)
        if c % 2 == 0: f.text(x0 + c * px_per, 124, str(c), 11.5, 'middle', c=GR)
    f.text(x0 + nwave * lam + 8, 124, 'cm', 12, 'start', True, GR)
    dense = [lam / 2 + j * lam for j in range(nwave)]
    names = {}
    if marks:
        f.text(x0 + dense[0], 18, '밀', 13, 'middle', True, RD)
        f.text(x0 + dense[1], 18, '밀', 13, 'middle', True, RD)
        f.text(x0 + dense[0] - lam / 2, 18, '소', 13, 'middle', True, BL)
        f.text(x0 + dense[0] + lam / 2, 18, '소', 13, 'middle', True, BL)
        for xx in (dense[0], dense[1]):
            f.line(x0 + xx, 74, x0 + xx, 100, RD, 1, '3 3')
    return f.svg(), dense, px_per


def refr_fig(th1, th2, w=270, h=215, t1='매질 Ⅰ', t2='매질 Ⅱ'):
    f = Fig(w, h)
    x0, y0 = w / 2, h / 2
    f.rect(0, y0, w, h - y0, '#e6f0fb', 'none', 0)
    f.line(0, y0, w, y0, INK, 1.8)
    f.line(x0, 8, x0, h - 8, GR, 1.2, '5 3')
    L = 88
    a1, a2 = math.radians(th1), math.radians(th2)
    f.arrow(x0 - L * math.sin(a1), y0 - L * math.cos(a1), x0 - 3 * math.sin(a1), y0 - 3 * math.cos(a1), RD, 2.2)
    f.arrow(x0, y0, x0 + L * math.sin(a2), y0 + L * math.cos(a2), BL, 2.2)
    r1 = 38
    pts = [(x0 - r1 * math.sin(a1 * i / 14), y0 - r1 * math.cos(a1 * i / 14)) for i in range(15)]
    f.poly(pts, 'none', GR, 1.2, close=False)
    f.text(x0 + 6, y0 - 44, '%d°' % th1, 12.5, 'start', True, RD)
    r2 = 42
    pts = [(x0 + r2 * math.sin(a2 * i / 14), y0 + r2 * math.cos(a2 * i / 14)) for i in range(15)]
    f.poly(pts, 'none', GR, 1.2, close=False)
    f.text(x0 + 56 * math.sin(a2 / 2) + 4, y0 + 56 * math.cos(a2 / 2) + 10, '%d°' % th2, 12.5, 'middle', True, BL)
    f.text(8, 20, t1, 13, 'start', True, GR)
    f.text(8, h - 10, t2, 13, 'start', True, GR)
    return f.svg()


def src_fig(n, pts=(), lamp=30, w=340, h=230, nmax=6, ycap=96):
    """두 점파원 S1, S2(거리 n·λ)와 마루(실선)·골(점선) 원. pts: [(a, b, 글자)] = (S1 반지름 a·λ/2, S2 반지름 b·λ/2)."""
    f = Fig(w, h)
    cx, cy = w / 2, h / 2
    d = n * lamp
    s1, s2 = cx - d / 2, cx + d / 2
    f.o.append('<clipPath id="clw2"><rect x="4" y="4" width="%d" height="%d"/></clipPath><g clip-path="url(#clw2)">' % (w - 8, h - 8))
    for k in range(1, nmax + 1):
        rr = k * lamp / 2
        for sx in (s1, s2):
            if k % 2 == 0: f.circ(sx, cy, rr, 'none', RD, 1.3)
            else: f.circ(sx, cy, rr, 'none', BL, 1.2, dash='4 3')
    f.o.append('</g>')
    for sx, nm in ((s1, 'S₁'), (s2, 'S₂')):
        f.circ(sx, cy, 4.5, INK, INK, 1)
        f.text(sx, cy + 18, nm, 12.5, 'middle', True, INK)
    out = []
    for (a, b, lab) in pts:
        r1, r2 = a * lamp / 2, b * lamp / 2
        x = (r1 * r1 - r2 * r2) / (2 * d)
        y = math.sqrt(r1 * r1 - (x + d / 2) ** 2)
        f.circ(cx + x, cy - y, 4, INK, INK, 1)
        f.text(cx + x + 11, cy - y - 6, lab, 14, 'middle', True, INK)
    f.line(10, 12, 28, 12, RD, 1.6); f.text(32, 16, '마루', 12, 'start', True, RD)
    f.line(78, 12, 96, 12, BL, 1.6, '4 3'); f.text(100, 16, '골', 12, 'start', True, BL)
    return f.svg()


def src_points(r, n, lamp=30, nmax=6, ycap=96, k=3):
    """그림에 쓸 교점 후보에서 k개 선택(위쪽 반평면). 반환: [(a, b)]"""
    d = n * lamp
    cand = []
    for a in range(1, nmax + 1):
        for b in range(1, nmax + 1):
            r1, r2 = a * lamp / 2, b * lamp / 2
            if not (abs(r1 - r2) < d < r1 + r2): continue
            x = (r1 * r1 - r2 * r2) / (2 * d)
            y2 = r1 * r1 - (x + d / 2) ** 2
            if y2 <= 0: continue
            y = math.sqrt(y2)
            if y < 22 or y > ycap or abs(x) > 140: continue
            cand.append((a, b, x, y))
    for _ in range(80):
        s = r.sample(cand, k) if len(cand) >= k else None
        if not s: return None
        ok = all(math.hypot(p[2] - q[2], p[3] - q[3]) > 34 for p, q in itertools.combinations(s, 2))
        if ok: return [(p[0], p[1]) for p in s]
    return None


# ================================================================== ph091 파동의 요소와 v=fλ
@T('ph091')
def ph091(r, k):
    form = r.choice(['calc', 'calc', 'fig', 'fig', 'cnt', 'cnt', 'ratio', 'ratio'])
    ctx = r.choice(['줄을 따라 진행하는 파동', '수면파', '용수철을 따라 진행하는 파동', '긴 줄에서 발생시킨 파동'])
    if form == 'calc':
        sub_ = r.choice(['v', 'lam', 'f', 'Tv'])
        f_ = Fr(r.choice([2, 4, 5, 8, 10, 20, 25, 40, 50, 100]))
        lam = Fr(str(r.choice([0.1, 0.2, 0.25, 0.4, 0.5, 0.8, 1, 1.5, 2, 2.5, 4, 5])))
        v = f_ * lam
        if not term(v): return None
        if sub_ == 'v':
            body = P('%s의 진동수가 %s Hz이고 파장이 %s m이다. 이 파동의 속력은?' % (ctx, fn(f_), fn(lam)))
            wr = [f_ / lam, f_ + lam, v * 2, v / 2, lam / f_, v * 10]
            return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='하', fam='a',
                      steps=['v = fλ = %s × %s = %s m/s 이다.' % (fn(f_), fn(lam), fn(v))], core='파동의 속력 v = fλ.', point='진동수와 파장으로 속력을 구한다.')
        if sub_ == 'lam':
            body = P('%s의 속력이 %s m/s이고 진동수가 %s Hz이다. 이 파동의 파장은?' % (ctx, fn(v), fn(f_)))
            wr = [v * f_, lam * 2, lam / 2, f_ / v if v else lam + 1, abs(v - f_) if v != f_ else lam + 3, lam * 4]
            return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='하', fam='a',
                      steps=['v = fλ 에서 λ = v/f = %s / %s = %s m 이다.' % (fn(v), fn(f_), fn(lam))], core='λ = v/f.', point='속력과 진동수로 파장을 구한다.')
        if sub_ == 'f':
            body = P('%s의 속력이 %s m/s이고 파장이 %s m이다. 이 파동의 진동수는?' % (ctx, fn(v), fn(lam)))
            wr = [v * lam, f_ * 2, f_ / 2, lam / v, v - lam, f_ * 4]
            return mc(body, '%s Hz' % fn(f_), ['%s Hz' % fn(w) for w in wr], r=r, lv='하', fam='a',
                      steps=['v = fλ 에서 f = v/λ = %s / %s = %s Hz 이다.' % (fn(v), fn(lam), fn(f_))], core='f = v/λ.', point='속력과 파장으로 진동수를 구한다.')
        Tv = 1 / f_
        body = P('%s의 주기가 %s s이고 파장이 %s m이다. 이 파동의 속력은?' % (ctx, fn(Tv), fn(lam)))
        wr = [lam * Tv, lam * 2 / Tv, v * 2, v / 2, lam + Tv, v * 10]
        return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='a',
                  steps=['v = λ/T = %s / %s = %s m/s 이다. (f = 1/T = %s Hz)' % (fn(lam), fn(Tv), fn(v), fn(f_))], core='v = λ/T = fλ.', point='주기에서 진동수를 거쳐 속력을 구한다.')
    if form == 'fig':
        A = r.choice([2, 3, 4, 5])
        lam = Fr(str(r.choice([0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 4])))
        f_ = Fr(r.choice([2, 4, 5, 10, 20, 25]))
        v = f_ * lam
        if not term(v): return None
        nc = 3 if lam <= 1.2 else 2
        xmax = float(lam) * nc
        kind = r.choice([0.0, math.pi / 2])
        fig = FIG(wgraph([(sinf(A, float(lam), kind), BL, 2.6, None)], xmax, A, [float(lam) / 2 * i for i in range(1, 2 * nc + 1)], [-A, A], 'x (m)', 'y (cm)'), '68%')
        ask = r.choice(['v', 'v', 'f', 'T'])
        base = '그림은 시간 t = 0 일 때 한 방향으로 진행하는 파동의 변위 y를 위치 x에 따라 나타낸 것이다. '
        if ask == 'v':
            body = P(base + '이 파동의 진동수가 %s Hz일 때, 파동의 속력은?' % fn(f_)) + fig
            wr = [v / 2, v * 2, f_ * A, f_ * 2 * A, f_ * lam / 2 if False else f_ * lam * 4]
            return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['그래프에서 파장 λ = %s m 이다(마루에서 다음 마루까지의 거리).' % fn(lam), 'v = fλ = %s × %s = %s m/s 이다.' % (fn(f_), fn(lam), fn(v))],
                      core='변위-위치 그래프에서 파장을 읽고 v = fλ 를 적용한다.', point='그래프에서 파장을 읽는다.')
        if ask == 'f':
            body = P(base + '이 파동의 속력이 %s m/s일 때, 파동의 진동수는?' % fn(v)) + fig
            wr = [v * lam, f_ * 2, f_ / 2, v * A, v / A if (v / A).denominator <= 10 else f_ + 3, f_ * 4]
            return mc(body, '%s Hz' % fn(f_), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='b',
                      steps=['그래프에서 파장 λ = %s m 이다.' % fn(lam), 'f = v/λ = %s / %s = %s Hz 이다.' % (fn(v), fn(lam), fn(f_))], core='f = v/λ.', point='그래프의 파장과 속력으로 진동수를 구한다.')
        Tv = 1 / f_
        body = P(base + '이 파동의 속력이 %s m/s일 때, 파동의 주기는?' % fn(v)) + fig
        wr = [f_, Tv * 2, Tv / 2, Tv * 4, v / lam * 2 if False else lam / 10]
        return mc(body, '%s s' % fn(Tv), ['%s s' % fn(w) if i != 0 else '%s Hz' % fn(w) for i, w in enumerate(wr)], r=r, lv='중', fam='b', sort='shuf',
                  steps=['그래프에서 파장 λ = %s m 이다.' % fn(lam), 'T = λ/v = %s / %s = %s s 이다.' % (fn(lam), fn(v), fn(Tv))], core='T = λ/v.', point='그래프의 파장으로 주기를 구한다.')
    if form == 'cnt':
        sub_ = r.choice(['cork', 'time', 'dist'])
        if sub_ == 'cork':
            n = r.choice([10, 20, 30, 40, 60, 90, 120])
            t = r.choice([5, 10, 20, 30, 60])
            f_ = Fr(n, t)
            d = Fr(str(r.choice([0.1, 0.2, 0.25, 0.5, 0.6, 0.8, 1, 1.5, 2])))
            v = f_ * d
            if not term(f_) or not term(v): return None
            body = P('잔잔한 수면에서 코르크 마개가 %d초 동안 %d번 상하로 진동하고, 수면파의 이웃한 두 마루 사이의 거리는 %s m이다. 이 수면파의 속력은?' % (t, n, fn(d)))
            wr = [Fr(n * 1) * d, v * 2, v / 2, d / f_, Fr(t, n) * d, f_ + d]
            return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='c',
                      steps=['진동수 f = %d / %d = %s Hz 이다.' % (n, t, fn(f_)), '이웃한 두 마루 사이의 거리가 파장이므로 λ = %s m 이다.' % fn(d), 'v = fλ = %s × %s = %s m/s 이다.' % (fn(f_), fn(d), fn(v))],
                      core='이웃한 마루 사이의 거리가 파장이고, 진동수는 진동 횟수/시간이다.', point='진동 횟수와 시간으로 진동수를 구해 속력을 계산한다.')
        if sub_ == 'time':
            f_ = Fr(r.choice([2, 4, 5, 10, 20]))
            L = Fr(r.choice([2, 4, 5, 6, 8, 10, 12, 20, 30]))
            t = Fr(str(r.choice([0.5, 1, 2, 2.5, 4, 5])))
            v = L / t
            lam = v / f_
            if not term(lam) or lam > 5 or lam < 0.05: return None
            body = P('진동수가 %s Hz인 파원에서 발생한 파동이 %s초 동안 %s m를 진행하였다. 이 파동의 파장은?' % (fn(f_), fn(t), fn(L)))
            wr = [lam * 2, lam / 2, v, L / f_, f_ * t / L, lam * 4]
            assert lam * f_ == v
            return mc(body, '%s m' % fn(lam), ['%s m' % fn(w) for w in wr], r=r, lv='상', fam='c',
                      steps=['파동의 속력 v = %s / %s = %s m/s 이다.' % (fn(L), fn(t), fn(v)), 'λ = v/f = %s / %s = %s m 이다.' % (fn(v), fn(f_), fn(lam))],
                      core='속력은 이동 거리/시간, 파장은 v/f.', point='이동 거리와 시간으로 속력을 구한 뒤 파장을 구한다.')
        lam = Fr(str(r.choice([0.5, 1, 1.5, 2, 2.5, 4])))
        n = r.choice([3, 4, 5, 6, 8, 10])
        f_ = Fr(r.choice([2, 4, 5, 10]))
        t = Fr(n) / f_
        if not term(t): return None
        L = n * lam
        body = P('파장이 %s m, 진동수가 %s Hz인 파동에서 매질의 한 점이 %s초 동안 진동하는 사이 파동이 진행한 거리는?' % (fn(lam), fn(f_), fn(t)))
        wr = [L * 2, L / 2, lam * f_, lam * t if False else lam * t * 2, L + lam, Fr(n)]
        assert L == f_ * lam * t
        return mc(body, '%s m' % fn(L), ['%s m' % fn(w) for w in wr], r=r, lv='상', fam='c',
                  steps=['v = fλ = %s × %s = %s m/s 이다.' % (fn(f_), fn(lam), fn(f_ * lam)), '진행 거리 = vt = %s × %s = %s m 이다. (진동 횟수 %d번 × 파장 %s m)' % (fn(f_ * lam), fn(t), fn(L), n, fn(lam))],
                  core='파동이 한 주기 동안 진행하는 거리는 파장이다.', point='진동 횟수 × 파장으로 진행 거리를 구한다.')
    # ratio
    kind = r.choice(['f', 'v', 'both'])
    a = r.choice([2, 3, 4, 5])
    b = r.choice([2, 3, 4])
    if kind == 'f':
        body = P('같은 줄에서 파원의 진동수를 %d배로 하였다. 줄을 따라 진행하는 파동의 속력은 변하지 않는다. 파장은 처음의 몇 배가 되는가?' % a)
        q = Fr(1, a)
        wr = [Fr(a), Fr(a * a), Fr(1, a * a), Fr(1), Fr(a, 2)]
        return mc(body, times_str(q), [times_str(w) for w in wr], r=r, lv='중', fam='d', sort='shuf',
                  steps=['같은 매질에서 속력이 일정하므로 v = fλ 에서 λ ∝ 1/f 이다.', '진동수가 %d배이므로 파장은 1/%d배이다.' % (a, a)],
                  core='속력이 일정하면 파장은 진동수에 반비례한다.', point='v = fλ 에서 일정한 양을 찾는다.')
    if kind == 'v':
        body = P('진동수가 일정한 파원에서 발생한 파동이 매질이 바뀌면서 속력이 %d배가 되었다. 파장은 처음의 몇 배가 되는가?' % a)
        wr = [Fr(1, a), Fr(a * a), Fr(1, a * a), Fr(1), Fr(a + 1)]
        return mc(body, times_str(Fr(a)), [times_str(w) for w in wr], r=r, lv='중', fam='d', sort='shuf',
                  steps=['진동수는 파원이 정하므로 일정하다. v = fλ 에서 λ ∝ v 이다.', '속력이 %d배이므로 파장도 %d배이다.' % (a, a)],
                  core='진동수가 일정하면 파장은 속력에 비례한다.', point='v = fλ 에서 일정한 양을 찾는다.')
    q = Fr(a, b)
    if q == 1: return None
    body = P('파동의 진동수가 %d배가 되고 속력이 %d배가 되었다. 파장은 처음의 몇 배가 되는가?' % (b, a))
    right = Fr(a, b)
    wr = [Fr(b, a), Fr(a * b), Fr(1, a * b), Fr(a + b), Fr(a, b) * 2]
    return mc(body, times_str(right), [times_str(w) for w in wr], r=r, lv='상', fam='d', sort='shuf',
              steps=['v = fλ 에서 λ = v/f 이다.', '파장은 %d/%d 배가 된다.' % (a, b) if True else ''],
              core='λ = v/f 이므로 속력에 비례하고 진동수에 반비례한다.', point='두 양이 동시에 변할 때 비로 계산한다.')


# ================================================================== ph092 파동 그래프에서 읽는 속력
@T('ph092')
def ph092(r, k):
    form = r.choice(['two', 'two', 'two', 'shift', 'shift', 'cnt', 'tm'])
    if form == 'two':
        A = r.choice([2, 3, 4, 5])
        lam = r.choice([0.4, 0.8, 1, 1.2, 1.6, 2, 2.4, 3, 4, 6])
        Tv = r.choice([0.1, 0.2, 0.25, 0.4, 0.5, 1, 2])
        v = Fr(str(lam)) / Fr(str(Tv))
        if not term(v): return None
        kind = r.choice([0.0, math.pi / 2])
        nx = 2
        a = wgraph([(sinf(A, lam, kind), BL, 2.4, None)], lam * nx, A, [lam / 2 * i for i in range(1, 2 * nx + 1)], [-A, A], 'x (m)', 'y (cm)', w=250, h=185, title='(가) t = 0')
        b = wgraph([(sinf(A, Tv, kind), RD, 2.4, None)], Tv * 2, A, [Tv / 2 * i for i in range(1, 5)], [-A, A], 't (s)', 'y (cm)', w=250, h=185, title='(나) x = 0')
        fig = two_fig(a, b)
        ask = r.choice(['v', 'f', 'dist', 'lam'])
        base = '그림 (가)는 시간 t = 0 일 때 한 방향으로 진행하는 파동의 변위 y를 위치 x에 따라 나타낸 것이고, (나)는 이 파동이 지나가는 x = 0 인 점에서 변위 y를 시간 t에 따라 나타낸 것이다. '
        st0 = '(가)에서 파장 λ = %s m, (나)에서 주기 T = %s s 이다.' % (fn(lam), fn(Tv))
        if ask == 'v':
            body = P(base + '이 파동의 속력은?') + fig
            wr = [v * Fr(str(Tv)) * Fr(str(Tv)) if False else Fr(str(Tv)) / Fr(str(lam)), v * 2, v / 2, Fr(str(lam)) * Fr(str(Tv)), v + 1, v * 4]
            return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=[st0, 'v = λ/T = %s / %s = %s m/s 이다.' % (fn(lam), fn(Tv), fn(v))],
                      core='변위-위치 그래프에서 파장 λ, 변위-시간 그래프에서 주기 T를 읽어 v = λ/T 로 속력을 구한다.', point='두 그래프에서 λ와 T를 읽는다.')
        if ask == 'f':
            f_ = 1 / Fr(str(Tv))
            body = P(base + '이 파동의 진동수는?') + fig
            wr = [Fr(str(Tv)), f_ * 2, f_ / 2, v, Fr(str(lam)), f_ * 4]
            return mc(body, '%s Hz' % fn(f_), ['%s Hz' % fn(w) for w in wr], r=r, lv='하', fam='a',
                      steps=['(나)에서 주기 T = %s s 이다.' % fn(Tv), 'f = 1/T = 1/%s = %s Hz 이다.' % (fn(Tv), fn(f_))], core='f = 1/T.', point='변위-시간 그래프에서 주기를 읽는다.')
        if ask == 'lam':
            body = P(base + '이 파동의 파장과 주기를 옳게 짝지은 것은?') + fig
            right = '%s m, %s s' % (fn(lam), fn(Tv))
            wr = ['%s m, %s s' % (fn(lam * 2), fn(Tv)), '%s m, %s s' % (fn(lam / 2), fn(Tv)), '%s m, %s s' % (fn(lam), fn(Tv * 2)), '%s m, %s s' % (fn(lam), fn(Tv / 2)), '%s m, %s s' % (fn(Tv), fn(lam))]
            return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf', steps=[st0],
                      core='변위-위치 그래프에서는 파장, 변위-시간 그래프에서는 주기를 읽는다.', point='두 그래프의 가로축 물리량을 구분한다.')
        n = r.choice([2, 3, 5, 6, 10])
        L = v * Fr(n) * Fr(str(Tv))
        body = P(base + '이 파동이 %d주기 동안 진행하는 거리는?' % n) + fig
        wr = [Fr(str(lam)) * 2 * n, Fr(str(lam)) / 2 * n if False else Fr(n) * Fr(str(Tv)), L + Fr(str(lam)), v * n, L * 2]
        assert L == Fr(str(lam)) * n
        return mc(body, '%s m' % fn(L), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='a',
                  steps=[st0, '한 주기 동안 파동은 한 파장만큼 진행하므로 %d주기 동안 %d × %s = %s m 이다.' % (n, n, fn(lam), fn(L))],
                  core='한 주기 동안 파동은 파장만큼 진행한다.', point='주기 수와 파장으로 진행 거리를 구한다.')
    if form == 'shift':
        A = r.choice([2, 3, 4])
        lam = r.choice([4, 6, 8, 12])
        d = r.choice([1, 2, 3])
        if d >= lam / 2: return None
        dt = Fr(str(r.choice([0.25, 0.5, 1, 2])))
        v = Fr(d) / dt
        Tv = Fr(lam) / v
        if not term(Tv): return None
        ask = r.choice(['v', 'T', 'f'])
        nx = 2
        def extra(p):
            xc = lam / 4 + 0 * lam
            p.circ(p.px(xc), p.py(A), 3.5, BL, BL, 1)
            p.circ(p.px(xc + d), p.py(A), 3.5, RD, RD, 1)
            p.arrow(p.px(xc), p.py(A * 1.3), p.px(xc + d), p.py(A * 1.3), INK, 1.6)
            p.text((p.px(xc) + p.px(xc + d)) / 2, p.py(A * 1.3) - 5, '%d m' % d, 12, 'middle', True, INK)
        sol = sinf(A, lam, 0.0)
        shf = lambda x: A * math.sin(2 * math.pi * (x - d) / lam)
        fig = FIG(wgraph([(sol, BL, 2.4, None), (shf, RD, 2.4, '6 4')], lam * nx, A, [lam / 4 * i for i in range(1, 4 * nx + 1) if (lam / 4 * i) % 1 == 0 or True][:8], [-A, A], 'x (m)', 'y (cm)', extra=extra, ymul=1.7, w=330, h=200), '70%')
        base = '그림의 실선은 +x 방향으로 진행하는 파동의 t = 0 일 때의 모습이고, 점선은 Δt = %s s 후의 모습이다. 이 시간 동안 파동은 한 파장보다 짧은 거리를 진행하였다. ' % fn(dt)
        if ask == 'v':
            body = P(base + '이 파동의 속력은?') + fig
            wr = [v * 2, v / 2, Fr(lam) / dt, d * dt, v + 1, v * 4]
            right = '%s m/s' % fn(v)
            ws = ['%s m/s' % fn(w) for w in wr]
            st = ['파동은 %s s 동안 %d m 진행했으므로 v = %d / %s = %s m/s 이다.' % (fn(dt), d, d, fn(dt), fn(v))]
            lv = '중'
        elif ask == 'T':
            body = P(base + '이 파동의 주기는?') + fig
            right = '%s s' % fn(Tv)
            wr = [Tv * 2, Tv / 2, dt, Fr(d) / dt, Tv * 4, Tv + 1]
            ws = ['%s s' % fn(w) for w in wr]
            st = ['그래프에서 파장 λ = %d m 이고, v = %d / %s = %s m/s 이다.' % (lam, d, fn(dt), fn(v)), 'T = λ/v = %d / %s = %s s 이다.' % (lam, fn(v), fn(Tv))]
            lv = '상'
        else:
            f_ = 1 / Tv
            body = P(base + '이 파동의 진동수는?') + fig
            right = '%s Hz' % fn(f_)
            wr = [f_ * 2, f_ / 2, Tv, v, f_ * 4, f_ + 1]
            ws = ['%s Hz' % fn(w) for w in wr]
            st = ['그래프에서 파장 λ = %d m 이고, v = %d / %s = %s m/s 이다.' % (lam, d, fn(dt), fn(v)), 'f = v/λ = %s / %d = %s Hz 이다.' % (fn(v), lam, fn(f_))]
            lv = '상'
        assert abs(float(Tv) - lam / float(v)) < 1e-9
        return mc(body, right, ws, r=r, lv=lv, fam='b', sort='shuf', steps=st,
                  core='파동이 진행한 거리와 시간으로 속력을 구하고, 파장을 읽어 주기·진동수를 구한다.', point='두 시각의 파형 이동량에서 속력을 구한다.')
    if form == 'cnt':
        A = r.choice([2, 3, 4])
        Tv = r.choice([0.2, 0.4, 0.5, 1, 2])
        nc = r.choice([3, 4, 5])
        ttot = Fr(str(Tv)) * nc
        lam = r.choice([0.4, 0.8, 1, 1.5, 2, 3, 5])
        v = Fr(str(lam)) / Fr(str(Tv))
        if not term(v): return None
        fig = FIG(wgraph([(sinf(A, Tv, 0.0), RD, 2.4, None)], float(ttot), A, [float(ttot) * i / nc for i in range(1, nc + 1)], [-A, A], 't (s)', 'y (cm)'), '68%')
        body = P('그림은 파동이 지나가는 한 지점에서 매질의 변위 y를 시간 t에 따라 %s초 동안 나타낸 것이다. 이 파동의 파장이 %s m일 때 파동의 속력은?' % (fn(ttot), fn(lam))) + fig
        wr = [v * 2, v / 2, Fr(str(lam)) * nc / ttot if False else Fr(str(lam)) * ttot, Fr(str(lam)) * nc, v + 1, v * nc]
        return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='c',
                  steps=['그래프에서 %s초 동안 %d번 진동하므로 주기 T = %s / %d = %s s 이다.' % (fn(ttot), nc, fn(ttot), nc, fn(Tv)), 'v = λ/T = %s / %s = %s m/s 이다.' % (fn(lam), fn(Tv), fn(v))],
                  core='그래프의 진동 횟수와 시간으로 주기를 구하고 v = λ/T.', point='변위-시간 그래프에서 주기를 읽는다.')
    # tm: 변위-위치 그래프에서 마루 이동 시간
    A = r.choice([2, 3, 4])
    lam = r.choice([2, 4, 6, 8])
    f_ = Fr(r.choice([1, 2, 4, 5, 10]))
    v = Fr(lam) * f_
    n = r.choice([1, 2, 3])
    nx = 3
    xs = lam / 4
    def extra(p):
        for j, lab in ((0, 'P'), (n, 'Q')):
            xx = xs + j * lam
            if xx <= lam * nx:
                p.circ(p.px(xx), p.py(A), 4, INK, INK, 1)
                p.text(p.px(xx), p.py(A) - 8, lab, 13.5, 'middle', True, INK)
    fig = FIG(wgraph([(sinf(A, lam, 0.0), BL, 2.6, None)], lam * nx, A, [lam / 2 * i for i in range(1, 2 * nx + 1)], [-A, A], 'x (m)', 'y (cm)', extra=extra), '70%')
    t = Fr(n * lam) / v
    body = P('그림은 t = 0 일 때 +x 방향으로 진행하는 파동의 변위 y를 위치 x에 따라 나타낸 것이다. 이 파동의 진동수는 %s Hz이다. 마루 P의 변위(최대 변위)가 마루 Q 위치에서 처음 나타나는 것은 몇 초 후인가?(마루 P가 Q의 위치에 도달하는 시간)' % fn(f_)) + fig if False else \
        P('그림은 t = 0 일 때 +x 방향으로 진행하는 파동의 변위 y를 위치 x에 따라 나타낸 것이다. 이 파동의 진동수는 %s Hz이다. 마루 P가 마루 Q의 처음 위치까지 진행하는 데 걸리는 시간은?' % fn(f_)) + fig
    wr = [t * 2, t / 2, Fr(n * lam) * f_, t + Fr(1, 4) / f_ if False else Fr(lam) / v * (n + 1), Fr(n) / f_ * 2 if False else t * 3]
    wr = [w for w in wr]
    assert t == Fr(n) / f_
    return mc(body, '%s s' % fn(t), ['%s s' % fn(w) for w in wr], r=r, lv='하' if n == 1 else '중', fam='d',
              steps=['그래프에서 파장 λ = %d m 이고 P와 Q 사이의 거리는 %d λ = %d m 이다.' % (lam, n, n * lam), '속력 v = fλ = %s × %d = %s m/s 이므로 t = %d / %s = %s s 이다.' % (fn(f_), lam, fn(v), n * lam, fn(v), fn(t))],
              core='마루가 한 파장 진행하는 데 걸리는 시간은 한 주기이다.', point='마루 사이 거리에서 진행 시간을 구한다.')


# ================================================================== ph093 횡파와 종파(<보기>)
_B93 = [
    ('횡파는 매질의 진동 방향이 파동의 진행 방향과 수직인 파동이다.', True, '횡파의 정의이다.', 'def_t'),
    ('종파는 매질의 진동 방향이 파동의 진행 방향과 수직인 파동이다.', False, '종파는 진동 방향이 진행 방향과 나란하다. 수직인 것은 횡파이다.', 'def_t'),
    ('종파는 매질의 진동 방향과 파동의 진행 방향이 나란한 파동이다.', True, '종파의 정의이다.', 'def_l'),
    ('소리는 종파이다.', True, '공기 분자가 진행 방향과 나란하게 진동하는 밀한 곳과 소한 곳이 전달되는 종파이다.', 'sound'),
    ('소리는 횡파이다.', False, '소리는 종파이다.', 'sound'),
    ('지진파 중 P파는 종파이고 S파는 횡파이다.', True, 'P파(종파), S파(횡파)이다.', 'quake'),
    ('지진파의 S파는 종파이다.', False, 'S파는 횡파이고, 종파는 P파이다.', 'quake'),
    ('줄을 위아래로 흔들 때 줄을 따라 진행하는 파동은 횡파이다.', True, '줄의 진동 방향(위아래)과 진행 방향(옆)이 수직이다.', 'rope'),
    ('용수철을 길이 방향으로 밀었다 당길 때 생기는 파동은 횡파이다.', False, '진동 방향이 진행 방향과 나란하므로 종파이다.', 'spring'),
    ('용수철을 길이 방향으로 밀었다 당길 때 생기는 파동은 종파이다.', True, '진동 방향과 진행 방향이 나란하다.', 'spring'),
    ('빛(전자기파)은 횡파이다.', True, '전기장·자기장이 진행 방향에 수직으로 진동하는 횡파이다.', 'light'),
    ('빛은 종파이므로 매질이 필요하다.', False, '빛은 횡파이고 매질 없이 진공에서도 진행한다.', 'light'),
    ('파동이 진행할 때 매질의 입자는 파동과 함께 진행 방향으로 이동한다.', False, '매질의 입자는 제자리에서 진동할 뿐 파동과 함께 이동하지 않는다.', 'move'),
    ('파동이 진행할 때 매질은 이동하지 않고 에너지가 전달된다.', True, '파동은 매질의 이동 없이 에너지(와 진동 상태)를 전달한다.', 'move'),
    ('종파에서 매질이 밀집된 곳을 밀한 부분, 성긴 곳을 소한 부분이라 한다.', True, '종파의 파장은 이웃한 밀한 곳 사이의 거리이다.', 'dense'),
    ('종파에서 파장은 이웃한 밀한 부분과 소한 부분 사이의 거리이다.', False, '파장은 이웃한 밀한 부분(또는 소한 부분) 사이의 거리이다. 밀-소 사이는 반 파장이다.', 'dense'),
    ('물결파(수면파)는 마루와 골이 있으므로 횡파의 성질로 나타낼 수 있다.', True, '마루와 골로 표현되는 변위는 횡파 형태이다.', 'water'),
    ('횡파는 고체뿐 아니라 기체 속에서도 전달된다.', False, '횡파는 전단 변형을 전달해야 하므로 기체·액체 내부에서는 전달되지 않는다(소리는 종파).', 'medium'),
    ('종파는 기체 속에서도 전달된다.', True, '압축과 팽창으로 전달되므로 기체에서도 전달된다.', 'medium'),
    ('횡파의 파장은 이웃한 마루와 마루 사이의 거리이다.', True, '횡파의 한 파장은 마루에서 다음 마루까지이다.', 'lam'),
    ('초음파는 사람이 들을 수 없는 소리이지만 종파이다.', True, '진동수가 20000 Hz 이상인 종파이다.', 'ultra'),
]

_EX = [('소리는', 'L'), ('P파(지진파)는', 'L'), ('S파(지진파)는', 'T'), ('빛은', 'T'), ('줄을 흔들 때 줄을 따라가는 파동은', 'T'), ('용수철을 앞뒤로 밀고 당길 때의 파동은', 'L'),
       ('초음파는', 'L'), ('전파(라디오파)는', 'T'), ('물에 떠 있는 코르크를 위아래로 흔드는 수면파는', 'T')]


@T('ph093')
def ph093(r, k):
    form = r.choice(['bogi', 'bogi', 'ex', 'ex', 'panel', 'long', 'long', 'long'])
    if form == 'bogi':
        s = pick3(r, _B93)
        if not s: return None
        return bogi('횡파와 종파에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv=r.choice(['하', '중']), fam='a', r=r,
                    core='횡파는 진동 방향 ⊥ 진행 방향, 종파는 진동 방향 ∥ 진행 방향이며 매질은 이동하지 않는다.', point='횡파와 종파의 정의와 대표 예를 구분한다.')
    if form == 'ex':
        s = r.sample(_EX, 3)
        kinds = [x[1] for x in s]
        if len(set(kinds)) == 1 and r.random() < .7: return None
        ask = r.choice(['T', 'L'])
        stm = []
        for nm, kd in s:
            truth = (kd == ask)
            stm.append(('%s %s이다.' % (nm, '횡파' if ask == 'T' else '종파'), truth,
                        '%s %s이다.' % (nm, '횡파' if kd == 'T' else '종파') + (' 진동 방향이 진행 방향에 %s하다.' % ('수직' if kd == 'T' else '나란'))))
        return bogi('다음은 여러 가지 파동에 대한 설명이다. 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, ask='', lv='중', fam='b', r=r,
                    core='소리·초음파·P파·용수철 밀기 파동은 종파, 빛·전파·S파·줄파동은 횡파이다.', point='여러 파동을 횡파와 종파로 분류한다.')
    if form == 'panel':
        n = 3
        kinds = [r.choice(['T', 'L']) for _ in range(n)]
        ask = r.choice(['T', 'L'])
        S = [i for i in range(n) if kinds[i] == ask]
        if not S: return None
        names = '가나다'
        right = ', '.join(names[i] for i in S)
        allc = [', '.join(names[i] for i in c) for m in (1, 2, 3) for c in itertools.combinations(range(n), m)]
        fig = FIG(tl_panels(kinds), '78%')
        body = P('그림 (가)~(다)는 서로 다른 세 파동이 한 방향으로 진행할 때, 매질의 한 점이 진동하는 방향(빨간 화살표)과 파동의 진행 방향(파란 화살표)을 나타낸 것이다. %s인 것만을 있는 대로 고른 것은?' % ('횡파' if ask == 'T' else '종파')) + fig
        wr = [c for c in allc if c != right]
        return mc(body, right, wr, r=r, lv='하', fam='c', sort='shuf',
                  steps=[', '.join('(%s): 진동 방향이 진행 방향에 %s → %s' % (names[i], '수직' if kinds[i] == 'T' else '나란', '횡파' if kinds[i] == 'T' else '종파') for i in range(n)),
                         '따라서 %s은 %s이다.' % ('횡파' if ask == 'T' else '종파', right)],
                  core='진동 방향이 진행 방향에 수직이면 횡파, 나란하면 종파이다.', point='그림에서 진동 방향과 진행 방향의 관계를 읽는다.')
    # long: 종파 그림에서 파장
    lam = r.choice([2, 3, 4, 5])
    svg, dense, ppu = long_fig(lam, 3)
    fig = FIG(svg, '70%')
    ask = r.choice(['lam', 'half', 'n', 'v'])
    base = '그림은 용수철을 따라 오른쪽으로 진행하는 종파의 한 순간 모습이다. 아래 눈금자의 단위는 cm이다. '
    if ask == 'lam':
        body = P(base + '이 파동의 파장은?') + fig
        wr = [lam * 2, Fr(lam, 2), lam * 3, lam + 1, lam * 3 / 2 if False else lam + 2]
        return mc(body, '%d cm' % lam, ['%s cm' % fn(w) for w in wr], r=r, lv='중', fam='d',
                  steps=['종파의 파장은 이웃한 밀한 부분 사이의 거리이다.', '두 밀한 부분 사이 거리를 눈금자에서 읽으면 %d cm 이다.' % lam],
                  core='종파의 파장은 이웃한 밀한 부분(또는 소한 부분) 사이의 거리이다.', point='밀한 부분 사이의 거리를 읽는다.')
    if ask == 'half':
        body = P(base + '이웃한 밀한 부분과 소한 부분 사이의 거리는?') + fig
        right = Fr(lam, 2)
        wr = [lam, lam * 2, Fr(lam, 4), lam + 1, Fr(lam * 3, 2) if lam != 1 else 5]
        return mc(body, '%s cm' % fn(right), ['%s cm' % fn(w) for w in wr], r=r, lv='중', fam='d',
                  steps=['이웃한 밀한 부분 사이의 거리가 파장 λ = %d cm 이다.' % lam, '밀한 부분과 소한 부분 사이는 반 파장이므로 %s cm 이다.' % fn(right)],
                  core='밀-소 사이의 거리는 λ/2 이다.', point='반 파장의 의미를 이해한다.')
    if ask == 'n':
        body = P(base + '그림에 나타난 눈금자 전체 길이 %d cm 안에 들어 있는 파동의 파장 수는?' % (3 * lam))
        return mc(body, '3개', ['%d개' % w for w in (1, 2, 4, 6)], r=r, lv='하', fam='d', sort='shuf', steps=['파장이 %d cm 이므로 %d / %d = 3 개이다.' % (lam, 3 * lam, lam)],
                  core='전체 길이 ÷ 파장 = 파장 수.', point='종파의 파장을 읽어 파장 수를 센다.') if False else None
    f_ = r.choice([2, 5, 10, 20, 25])
    v = Fr(lam * f_, 100)
    body = P(base + '이 파동의 진동수가 %d Hz일 때, 파동의 진행 속력은?' % f_) + fig
    wr = [v * 2, v / 2, v * 100, Fr(lam * f_), v + 1]
    return mc(body, '%s m/s' % fn(v), ['%s m/s' % fn(w) for w in wr], r=r, lv='상', fam='d',
              steps=['파장 λ = %d cm = %s m 이다.' % (lam, fn(Fr(lam, 100))), 'v = fλ = %d × %s = %s m/s 이다.' % (f_, fn(Fr(lam, 100)), fn(v))],
              core='종파도 v = fλ 이며 파장은 이웃한 밀한 곳 사이의 거리이다.', point='단위를 맞춰 속력을 구한다.')


# ================================================================== ph094 매질이 달라질 때의 굴절
_B94 = [
    ('파동이 다른 매질로 진행할 때 진동수는 변하지 않는다.', True, '진동수는 파원이 결정하므로 매질이 바뀌어도 같다.', 'f'),
    ('파동이 다른 매질로 진행할 때 파장은 변하지 않는다.', False, '진동수는 같고 속력이 변하므로 파장이 변한다(λ = v/f).', 'lam'),
    ('파동의 속력이 느린 매질로 들어가면 파장은 짧아진다.', True, 'f가 일정하고 v가 작아지므로 λ = v/f 도 작아진다.', 'lam2'),
    ('파동의 속력이 빠른 매질로 들어가면 파장은 짧아진다.', False, 'v가 커지면 λ = v/f 도 커진다.', 'lam2'),
    ('파동이 속력이 느린 매질로 비스듬히 입사하면 굴절각은 입사각보다 작다.', True, '느린 매질로 갈 때 법선 쪽으로 꺾인다.', 'ang'),
    ('파동이 속력이 느린 매질로 비스듬히 입사하면 굴절각은 입사각보다 크다.', False, '느린 매질에서는 굴절각이 입사각보다 작다.', 'ang'),
    ('입사각과 굴절각의 사인(sin) 값의 비는 두 매질에서의 속력의 비와 같다.', True, 'sinθ₁/sinθ₂ = v₁/v₂ 이다(스넬 법칙).', 'snell'),
    ('입사각과 굴절각의 크기의 비는 두 매질에서의 속력의 비와 같다.', False, '각도 자체가 아니라 사인 값의 비가 속력의 비와 같다.', 'snell'),
    ('파동이 법선 방향(입사각 0°)으로 경계면에 입사하면 굴절하지 않고 직진한다.', True, '입사각이 0°이면 굴절각도 0°이다(속력은 변한다).', 'normal'),
    ('매질이 바뀌어도 파동의 주기는 변하지 않는다.', True, '주기는 진동수의 역수이므로 변하지 않는다.', 'T'),
    ('굴절할 때 파동의 속력과 파장은 서로 비례한다(진동수가 일정).', True, 'v = fλ 에서 f 일정이면 v ∝ λ 이다.', 'vl'),
    ('깊은 물에서 얕은 물로 진행하는 물결파의 속력은 느려진다.', True, '얕은 곳에서 물결파의 속력이 작다.', 'water'),
    ('깊은 물에서 얕은 물로 진행하는 물결파의 파장은 길어진다.', False, '속력이 느려지고 진동수가 같으므로 파장이 짧아진다.', 'water'),
    ('굴절은 파동의 속력이 매질에 따라 달라서 일어나는 현상이다.', True, '속력 차이 때문에 진행 방향이 꺾인다.', 'why'),
    ('굴절할 때 파동의 진폭은 항상 변하지 않는다.', False, '에너지 일부가 반사되므로 진폭은 보통 달라진다.', 'amp'),
    ('입사각이 같을 때 두 매질의 속력 차이가 클수록 굴절각과 입사각의 차이가 크다.', True, 'sinθ₂ = sinθ₁ (v₂/v₁) 에서 속력비가 1에서 멀수록 각의 차이가 커진다.', 'diff'),
    ('파동이 굴절할 때 파동의 에너지는 모두 굴절파로 전달되어 반사파는 생기지 않는다.', False, '일부는 반사된다.', 'refl'),
    ('굴절률이 큰 매질에서 파동(빛)의 속력은 더 작다.', True, 'n = c/v 이므로 굴절률이 클수록 속력이 작다.', 'nidx'),
]
_SIN = {30: Fr(1, 2), 37: Fr(3, 5), 53: Fr(4, 5)}


@T('ph094')
def ph094(r, k):
    form = r.choice(['num', 'num', 'lam', 'lam', 'ang', 'ang', 'bogi', 'cmp'])
    if form == 'bogi':
        s = pick3(r, _B94)
        if not s: return None
        return bogi('파동이 한 매질에서 다른 매질로 굴절하여 진행할 때에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='중', fam='d', r=r,
                    core='굴절할 때 진동수는 일정하고, 속력과 파장은 비례하여 변하며, sinθ₁/sinθ₂ = v₁/v₂ = λ₁/λ₂ 이다.', point='굴절에서 변하는 양과 변하지 않는 양을 구분한다.')
    if form == 'num':
        f_ = Fr(r.choice([2, 4, 5, 8, 10, 20, 25]))
        v1 = Fr(r.choice([4, 6, 8, 10, 12, 16, 20, 24, 30, 40]))
        v2 = Fr(r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20]))
        if v1 == v2: return None
        l1, l2 = v1 / f_, v2 / f_
        if not term(l1) or not term(l2): return None
        ask = r.choice(['l2', 'l1', 'f', 'ratio'])
        place = r.choice([('깊은 물', '얕은 물'), ('매질 A', '매질 B'), ('굵은 줄', '가는 줄')])
        base = '진동수가 일정한 파동이 %s에서 %s으로 진행한다. ' % place
        if ask == 'l2':
            body = P(base + '%s에서의 속력이 %s m/s, 파장이 %s m, %s에서의 속력이 %s m/s일 때 %s에서의 파장은?' % (place[0], fn(v1), fn(l1), place[1], fn(v2), place[1]))
            wr = [l1 * v1 / v2 * v1 / v2 if False else l1 * v1 / v2, l1, l2 * 2, l2 / 2, l1 + l2, l2 * v2 / v1 * v2 / v1]
            assert l2 == l1 * v2 / v1
            return mc(body, '%s m' % fn(l2), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['진동수는 변하지 않으므로 f = v₁/λ₁ = %s / %s = %s Hz 이다.' % (fn(v1), fn(l1), fn(f_)), 'λ₂ = v₂/f = %s / %s = %s m 이다.' % (fn(v2), fn(f_), fn(l2))],
                      core='굴절할 때 진동수는 일정하므로 λ ∝ v 이다.', point='진동수를 먼저 구해 새 매질의 파장을 구한다.')
        if ask == 'l1':
            body = P(base + '%s에서의 파장이 %s m, %s에서의 파장이 %s m이고 %s에서의 속력이 %s m/s일 때, %s에서의 속력은?' % (place[0], fn(l1), place[1], fn(l2), place[1], fn(v2), place[0]))
            wr = [v2 * l2 / l1, v1 * 2, v1 / 2, v1 + v2, v2, v1 * l1]
            return mc(body, '%s m/s' % fn(v1), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['f = v₂/λ₂ = %s / %s = %s Hz 이다.' % (fn(v2), fn(l2), fn(f_)), 'v₁ = fλ₁ = %s × %s = %s m/s 이다.' % (fn(f_), fn(l1), fn(v1))],
                      core='굴절할 때 진동수는 일정하다.', point='진동수를 매개로 두 매질의 속력·파장을 연결한다.')
        if ask == 'f':
            body = P(base + '%s에서의 속력은 %s m/s이고 %s에서의 파장은 %s m이다. 이 파동의 진동수는? (%s에서의 속력은 %s m/s이다.)' % (place[0], fn(v1), place[1], fn(l2), place[1], fn(v2)))
            wr = [f_ * 2, f_ / 2, v1 * l2, v1 / l2 * 2 if False else v1 / l2 if v1 / l2 != f_ else f_ + 3, f_ + 5, v2 * l2]
            return mc(body, '%s Hz' % fn(f_), ['%s Hz' % fn(w) for w in wr], r=r, lv='중', fam='a',
                      steps=['%s에서 f = v₂/λ₂ = %s / %s = %s Hz 이다. (진동수는 두 매질에서 같다.)' % (place[1], fn(v2), fn(l2), fn(f_))],
                      core='진동수는 매질에 관계없이 일정하다.', point='같은 매질의 v와 λ로 진동수를 구한다.')
        body = P(base + '%s에서의 속력이 %s m/s, %s에서의 속력이 %s m/s이다. %s에서의 파장 : %s에서의 파장은?' % (place[0], fn(v1), place[1], fn(v2), place[0], place[1]))
        right = ratio_str(v1, v2)
        wr = [ratio_str(v2, v1), ratio_str(v1 * v1, v2 * v2), ratio_str(v2 * v2, v1 * v1), '1 : 1', ratio_str(v1 + 1, v2)]
        return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf',
                  steps=['f 가 같으므로 λ ∝ v 이다.', 'λ₁ : λ₂ = v₁ : v₂ = %s : %s = %s 이다.' % (fn(v1), fn(v2), right)],
                  core='굴절할 때 파장은 속력에 비례한다.', point='진동수가 같으면 파장비 = 속력비.')
    if form == 'lam':
        pr = r.choice([(30, 37), (37, 30), (30, 53), (53, 30), (37, 53), (53, 37)])
        t1, t2 = pr
        s1, s2 = _SIN[t1], _SIN[t2]
        v1 = Fr(r.choice([10, 20, 30, 40, 15, 25, 5]))
        v2 = v1 * s2 / s1
        if not term(v2): return None
        f_ = Fr(r.choice([2, 4, 5, 10]))
        l1 = v1 / f_
        l2 = v2 / f_
        if not term(l1) or not term(l2): return None
        ask = r.choice(['v2', 'l2', 'f'])
        fig = FIG(refr_fig(t1, t2), '48%')
        base = '그림은 파동이 매질 Ⅰ에서 매질 Ⅱ로 진행할 때 입사각이 %d°, 굴절각이 %d°인 것을 나타낸 것이다. 매질 Ⅰ에서 파동의 속력은 %s m/s, 진동수는 %s Hz이다. (단, sin30° = 0.5, sin37° = 0.6, sin53° = 0.8이다.) ' % (t1, t2, fn(v1), fn(f_))
        if ask == 'v2':
            body = P(base + '매질 Ⅱ에서 파동의 속력은?') + fig
            wr = [v1 * s1 / s2, v1, v2 * 2, v2 / 2, v1 * Fr(t2, t1), v1 + v2]
            return mc(body, '%s m/s' % fn(v2), ['%s m/s' % fn(w) for w in wr], r=r, lv='상', fam='c',
                      steps=['스넬 법칙: sinθ₁/sinθ₂ = v₁/v₂ 이다.', 'v₂ = v₁ sin%d°/sin%d° = %s × %s / %s = %s m/s 이다.' % (t2, t1, fn(v1), fn(s2), fn(s1), fn(v2))],
                      core='sinθ₁/sinθ₂ = v₁/v₂.', point='입사각·굴절각으로 속력비를 구한다.')
        if ask == 'l2':
            body = P(base + '매질 Ⅱ에서 파동의 파장은?') + fig
            wr = [l1, l1 * s1 / s2, l2 * 2, l2 / 2, l1 * Fr(t2, t1), l1 + l2]
            assert l2 == l1 * s2 / s1
            return mc(body, '%s m' % fn(l2), ['%s m' % fn(w) for w in wr], r=r, lv='상', fam='c',
                      steps=['매질 Ⅰ에서 λ₁ = v₁/f = %s / %s = %s m 이다.' % (fn(v1), fn(f_), fn(l1)), 'λ₂/λ₁ = v₂/v₁ = sin%d°/sin%d° 이므로 λ₂ = %s × %s / %s = %s m 이다.' % (t2, t1, fn(l1), fn(s2), fn(s1), fn(l2))],
                      core='λ₂/λ₁ = v₂/v₁ = sinθ₂/sinθ₁ (진동수 일정).', point='스넬 법칙과 v = fλ 를 함께 쓴다.')
        body = P(base + '매질 Ⅱ에서 파동의 진동수는?') + fig
        wr = [f_ * s2 / s1, f_ * s1 / s2, f_ * 2, f_ / 2, v2 / l1 if v2 / l1 != f_ else f_ + 1]
        return mc(body, '%s Hz' % fn(f_), ['%s Hz' % fn(w) for w in wr], r=r, lv='하', fam='c',
                  steps=['굴절할 때 진동수는 변하지 않으므로 매질 Ⅱ에서도 %s Hz 이다.' % fn(f_)],
                  core='굴절할 때 진동수는 일정하다.', point='진동수 불변을 이해한다.')
    if form == 'ang':
        pr = r.choice([(30, 37), (37, 30), (30, 53), (53, 30), (37, 53), (53, 37)])
        t1, t2 = pr
        s1, s2 = _SIN[t1], _SIN[t2]
        l1 = Fr(str(r.choice([0.4, 0.5, 0.6, 0.8, 1, 1.2, 1.5, 2, 2.4])))
        l2 = l1 * s2 / s1
        if not term(l2): return None
        fig = FIG(refr_fig(t1, t2, t1='얕은 물' if t2 < t1 else '깊은 물', t2='깊은 물' if t2 < t1 else '얕은 물') if False else refr_fig(t1, t2), '48%')
        ask = r.choice(['l2', 'vr', 'slow'])
        base = '그림은 수면파가 매질 Ⅰ에서 매질 Ⅱ로 굴절하여 진행하는 모습이다. 입사각은 %d°, 굴절각은 %d°이다. (단, sin30° = 0.5, sin37° = 0.6, sin53° = 0.8이다.) ' % (t1, t2)
        if ask == 'l2':
            body = P(base + '매질 Ⅰ에서 파장이 %s m일 때, 매질 Ⅱ에서의 파장은?' % fn(l1)) + fig
            wr = [l1 * s1 / s2, l1, l2 * 2, l2 / 2, l1 * Fr(t2, t1), l1 + 0.2 if False else l1 + l2]
            return mc(body, '%s m' % fn(l2), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='c',
                      steps=['sinθ₁/sinθ₂ = λ₁/λ₂ 이므로 λ₂ = λ₁ sin%d°/sin%d° 이다.' % (t2, t1), 'λ₂ = %s × %s / %s = %s m 이다.' % (fn(l1), fn(s2), fn(s1), fn(l2))],
                      core='sinθ₁/sinθ₂ = λ₁/λ₂ (진동수 일정).', point='굴절각 정보로 파장비를 구한다.')
        if ask == 'vr':
            body = P(base + '매질 Ⅰ에서의 속력 : 매질 Ⅱ에서의 속력은?') + fig
            right = ratio_str(s1, s2)
            wr = [ratio_str(s2, s1), ratio_str(t1, t2), ratio_str(t2, t1), ratio_str(s1 * s1, s2 * s2), '1 : 1']
            return mc(body, right, wr, r=r, lv='중', fam='c', sort='shuf',
                      steps=['v₁ : v₂ = sin%d° : sin%d° = %s : %s = %s 이다.' % (t1, t2, fn(s1), fn(s2), right)],
                      core='v₁ : v₂ = sinθ₁ : sinθ₂.', point='스넬 법칙으로 속력비를 구한다.')
        slower = 'Ⅱ' if t2 < t1 else 'Ⅰ'
        body = P(base + '파동의 속력이 더 느린 매질과, 파장이 더 짧은 매질을 옳게 짝지은 것은?') + fig
        right = '매질 %s, 매질 %s' % (slower, slower)
        other = 'Ⅰ' if slower == 'Ⅱ' else 'Ⅱ'
        wr = ['매질 %s, 매질 %s' % (other, other), '매질 %s, 매질 %s' % (slower, other), '매질 %s, 매질 %s' % (other, slower), '속력은 같고 매질 %s' % slower]
        return mc(body, right, wr + ['매질 %s, 같다' % slower], r=r, lv='하', fam='c', sort='shuf',
                  steps=['굴절각이 %s이므로 %s에서 sin 값이 %s 속력이 %s.' % ('입사각보다 작으므로 매질 Ⅱ' if t2 < t1 else '입사각보다 크므로 매질 Ⅰ', '매질 ' + slower, '작아', '느리다'),
                         '진동수가 같으므로 속력이 느린 매질 %s에서 파장도 더 짧다.' % slower],
                  core='속력이 느린 매질에서는 파장이 짧고 법선 쪽으로 굴절한다.', point='굴절각의 크기로 속력의 대소를 판단한다.')
    # cmp: 표 해석
    vA = Fr(r.choice([10, 20, 30, 40, 50, 60]))
    vB = Fr(r.choice([5, 10, 15, 20, 25, 30, 40]))
    if vA == vB: return None
    f_ = Fr(r.choice([5, 10, 20]))
    lA, lB = vA / f_, vB / f_
    if not term(lA) or not term(lB): return None
    tb = table(['', '속력 (m/s)', '파장 (m)'], [['매질 A', fn(vA), fn(lA)], ['매질 B', '?', '?']])
    ask = r.choice(['vB', 'lB'])
    if ask == 'lB':
        body = P('진동수가 일정한 파동이 매질 A에서 매질 B로 진행한다. 표는 두 매질에서의 값 일부를 나타낸 것이다. 매질 B에서 속력이 %s m/s일 때 매질 B에서의 파장은?' % fn(vB)) + tb
        wr = [lB * 2, lB / 2, lA, lB + lA, lB * vB / vA * 2 if False else lA * vA / vB]
        return mc(body, '%s m' % fn(lB), ['%s m' % fn(w) for w in wr], r=r, lv='중', fam='e',
                  steps=['A에서 f = %s / %s = %s Hz 이다.' % (fn(vA), fn(lA), fn(f_)), '진동수는 일정하므로 B에서 λ = v/f = %s / %s = %s m 이다.' % (fn(vB), fn(f_), fn(lB))],
                  core='굴절할 때 진동수가 일정하다.', point='표에서 진동수를 구해 다른 매질의 파장을 구한다.')
    body = P('진동수가 일정한 파동이 매질 A에서 매질 B로 진행한다. 표는 두 매질에서의 값 일부를 나타낸 것이다. 매질 B에서 파장이 %s m일 때 매질 B에서의 속력은?' % fn(lB)) + tb
    wr = [vB * 2, vB / 2, vA, vB + vA, lB * vA / lA * 2 if False else vA * lA / lB]
    return mc(body, '%s m/s' % fn(vB), ['%s m/s' % fn(w) for w in wr], r=r, lv='중', fam='e',
              steps=['A에서 f = %s / %s = %s Hz 이다.' % (fn(vA), fn(lA), fn(f_)), 'B에서 v = fλ = %s × %s = %s m/s 이다.' % (fn(f_), fn(lB), fn(vB))],
              core='굴절할 때 진동수가 일정하다.', point='표에서 진동수를 구해 다른 매질의 속력을 구한다.')


# ================================================================== ph095 파동의 중첩과 간섭
_B95 = [
    ('두 파동이 중첩될 때 합성파의 변위는 각 파동의 변위의 합이다.', True, '중첩의 원리이다.', 'sup'),
    ('두 펄스가 만나 지나간 뒤에는 각 펄스가 원래의 모양대로 진행한다.', True, '파동은 중첩된 뒤에도 서로 영향을 주지 않고 독립적으로 진행한다.', 'indep'),
    ('두 펄스가 만나면 서로 부딪혀 사라진다.', False, '중첩 후에도 각 펄스는 원래의 모양과 속력으로 진행한다.', 'indep'),
    ('위상이 같은 두 파동이 만나면 보강 간섭이 일어난다.', True, '마루와 마루, 골과 골이 만나 진폭이 커진다.', 'cons'),
    ('위상이 반대인 같은 진폭의 두 파동이 만나면 합성파의 진폭은 0이다.', True, '상쇄 간섭으로 변위가 0이 된다.', 'des'),
    ('보강 간섭이 일어나면 합성파의 진폭은 두 파동의 진폭의 차와 같다.', False, '보강 간섭에서는 합(A₁ + A₂)이다. 차는 상쇄 간섭에서이다.', 'amp'),
    ('상쇄 간섭에서 합성파의 진폭은 두 파동의 진폭의 차의 절댓값이다.', True, '|A₁ - A₂| 이다.', 'amp2'),
    ('상쇄 간섭이 일어날 때 파동의 에너지는 사라진다.', False, '에너지는 다른 곳에서 보강 간섭으로 나타나며 전체적으로는 보존된다.', 'energy'),
    ('마루와 마루가 만나는 지점에서는 매질의 변위가 최대로 커진다.', True, '두 변위가 합해져 커진다.', 'crest'),
    ('마루와 골이 만나는 지점에서는 변위가 두 변위의 합이므로 항상 0이다.', False, '두 변위의 크기가 같을 때만 0이다.', 'zero'),
    ('같은 진폭의 마루와 골이 만나는 순간의 변위는 0이다.', True, '+A + (-A) = 0 이다.', 'zero2'),
    ('보강 간섭이 일어나는 점의 합성파 진폭은 두 파동의 진폭의 합이다.', True, 'A = A₁ + A₂ 이다.', 'amp3'),
    ('중첩은 파동에서만 나타나는 현상이다(입자에서는 나타나지 않는다).', True, '입자는 같은 위치에 겹칠 수 없으므로 파동의 고유한 성질이다.', 'wave'),
    ('두 파동이 중첩되는 동안 각 파동의 진행 속력이 변한다.', False, '속력은 매질이 결정하므로 변하지 않는다.', 'speed'),
    ('같은 방향으로 진행하는 진동수가 같은 두 파동이 합성되면 진동수도 같은 파동이 된다.', True, '합성파의 진동수는 같다.', 'freq'),
    ('위상이 같은 두 파동의 합성파의 진폭은 두 파동 중 큰 진폭보다 작다.', False, '진폭이 합이 되어 어느 쪽보다 크다.', 'cons2'),
    ('서로 반대 방향으로 진행하는 같은 모양의 펄스가 완전히 겹칠 때 위로 볼록한 펄스는 높이가 2배가 된다.', True, '같은 방향(+)의 변위가 합쳐진다.', 'pulse'),
    ('위로 볼록한 펄스와 아래로 볼록한 같은 모양의 펄스가 완전히 겹치는 순간 모든 점의 변위는 0이다.', True, '변위가 서로 상쇄된다.', 'pulse2'),
]


@T('ph095')
def ph095(r, k):
    form = r.choice(['pulse', 'pulse', 'sine', 'sine', 'calc', 'bogi', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B95)
        if not s: return None
        return bogi('파동의 중첩과 간섭에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv=r.choice(['하', '중']), fam='d', r=r,
                    core='중첩된 파동의 변위는 각 파동의 변위의 합이며, 보강 간섭 때 진폭은 합, 상쇄 간섭 때 진폭은 차이다.', point='중첩 원리와 보강·상쇄 간섭을 구분한다.')
    if form == 'calc':
        A1 = r.choice([1, 2, 3, 4, 5, 6])
        A2 = r.choice([1, 2, 3, 4, 5, 6])
        kd = r.choice(['보강', '상쇄'])
        ans = A1 + A2 if kd == '보강' else abs(A1 - A2)
        who = r.choice(['줄을 따라 진행하는 같은 진동수의 두 파동', '수면에서 퍼져 나온 같은 진동수의 두 물결파'])
        body = P('%s의 진폭이 각각 %d cm, %d cm이다. 두 파동이 한 점에서 %s 간섭할 때 그 점에서 합성파의 진폭은?' % (who, A1, A2, kd))
        wr = [A1 + A2 if kd == '상쇄' else abs(A1 - A2), A1 * A2, ans * 2, max(A1, A2), (A1 + A2) / 2 if (A1 + A2) % 2 == 0 else ans + 3, ans + 1]
        return mc(body, '%d cm' % ans, ['%s cm' % fn(w) for w in wr], r=r, lv='하', fam='c',
                  steps=['%s 간섭에서 합성파의 진폭은 %s이다.' % (kd, '두 진폭의 합 %d + %d = %d cm' % (A1, A2, A1 + A2) if kd == '보강' else '두 진폭의 차 |%d - %d| = %d cm' % (A1, A2, abs(A1 - A2)))],
                  core='보강 간섭: A = A₁ + A₂, 상쇄 간섭: A = |A₁ - A₂|.', point='간섭의 종류에 따라 진폭을 구한다.')
    if form == 'sine':
        lam = r.choice([4, 8])
        A1, A2 = r.sample([1, 2, 3], 2)
        if r.random() < .3: A1 = A2 = r.choice([1, 2, 3])
        opp = r.random() < 0.5
        ph2 = math.pi if opp else 0.0
        nx = 2
        f1 = sinf(A1, lam, 0.0)
        f2 = sinf(A2, lam, ph2)
        ym = max(A1, A2)
        fig = FIG(wgraph([(f1, BL, 4.4, None), (f2, RD, 2.0, None)], lam * nx, ym, [lam / 4 * i for i in range(1, 4 * nx + 1)], [-ym, ym] if True else [], 'x (m)', 'y (cm)', xfmt=fn, ymul=1.5, h=195), '72%')
        amp = A1 + A2 if not opp else abs(A1 - A2)
        ask = r.choice(['amp', 'amp', 'pt'])
        base = '그림은 같은 줄에서 같은 방향으로 진행하는 두 파동 A(파란색), B(빨간색)의 한 순간의 변위를 위치에 따라 나타낸 것이다. 두 파동의 파장은 같다. '
        if ask == 'amp':
            body = P(base + '두 파동이 합성될 때 합성파의 진폭은?') + fig
            ws = [A1 + A2 if opp else abs(A1 - A2), A1 * A2, max(A1, A2), amp * 2, amp + 1, (A1 + A2) / 2]
            if amp == 0: return None
            return mc(body, '%s cm' % fn(amp), ['%s cm' % fn(w) for w in ws], r=r, lv='중', fam='b',
                      steps=['그래프에서 A의 진폭 = %d cm, B의 진폭 = %d cm 이다.' % (A1, A2), ('두 파동의 위상이 %s이므로 합성파의 진폭은 %s = %d cm 이다.' % ('반대(마루와 골이 만남)' if opp else '같으므로', '|%d - %d|' % (A1, A2) if opp else '%d + %d' % (A1, A2), amp)).replace('같으므로이', '같으므로')],
                      core='위상이 같으면 진폭의 합, 반대이면 진폭의 차가 합성파의 진폭이다.', point='그래프에서 위상 관계를 읽어 합성파의 진폭을 구한다.')
        q = r.choice([1, 3, 5, 7])
        xq = lam / 4 * q
        y1 = A1 * math.sin(2 * math.pi * xq / lam)
        y2 = A2 * math.sin(2 * math.pi * xq / lam + ph2)
        ys = round(y1 + y2)
        assert abs(ys - (y1 + y2)) < 1e-9
        body = P(base + 'x = %s m 인 지점에서 합성파의 변위는?' % fn(xq)) + fig
        ws = [round(y1 - y2), round(y1), round(y2), -ys if ys else 4, A1 + A2 + 1, ys + 1]
        return mc(body, '%d cm' % ys, ['%d cm' % w for w in ws], r=r, lv='상', fam='b',
                  steps=['x = %s m 에서 A의 변위 y₁ = %s cm, B의 변위 y₂ = %s cm 이다.' % (fn(xq), fn(round(y1)), fn(round(y2))), '합성파의 변위 = y₁ + y₂ = %s cm 이다.' % fn(ys)],
                  core='합성파의 변위는 각 파동의 변위의 합이다.', point='특정 위치의 변위를 읽어 더한다.')
    # pulse: 두 펄스의 합
    for _ in range(10):
        hw = 2
        hA = r.choice([1, 2, 3, -1, -2, -3])
        hB = r.choice([1, 2, 3, -1, -2, -3])
        cA = r.choice([2, 3, 4])
        W = 16
        cB = cA + r.choice([6, 8, 10])
        if cB + hw > W - 1: continue
        t = r.choice([2, 3, 4, 5])
        # t 시각: A 오른쪽, B 왼쪽 이동 1칸/s
        pa, pb = cA + t, cB - t
        if pa > pb + 3: continue
        x = r.choice(range(int(min(pa, pb) - 1), int(max(pa, pb) + 2)))
        if x < 0 or x > W: continue
        ya, yb = tri(x, pa, hA, hw), tri(x, pb, hB, hw)
        ans = ya + yb
        if abs(ans - round(ans)) > 1e-9: continue
        ans = int(round(ans))
        break
    else:
        return None
    fig = FIG(pulse_fig([(cA, hA, hw, BL, None), (cB, hB, hw, RD, None)], W, 3, arrows=[(cA - 1, cA + 1, 3.4, BL, ''), (cB + 1, cB - 1, 3.4, RD, '')]), '78%')
    # 보조 검산: 대칭 계산
    assert abs(ans - (tri(x - t, cA, hA, hw) + tri(x + t, cB, hB, hw))) < 1e-9
    ask = r.choice(['disp', 'max'])
    base = '그림은 줄 위에서 서로 반대 방향으로 진행하는 두 펄스 A, B의 t = 0 일 때 모습이다. 눈금 한 칸은 1 cm이고, 두 펄스의 속력은 각각 1 cm/s이다. '
    if ask == 'disp':
        body = P(base + 't = %d s 일 때 x = %d cm 에서 줄의 변위는? (단, 위쪽을 +로 한다.)' % (t, x)) + fig
        ws = [ya - yb, abs(ans), ans + 1, ans - 1, ya, yb, hA + hB]
        return mc(body, '%d cm' % ans, ['%s cm' % fn(w) for w in ws], r=r, lv='상', fam='a',
                  steps=['t = %d s 일 때 A의 중심은 x = %d cm, B의 중심은 x = %d cm 이다.' % (t, pa, pb), 'x = %d cm 에서 A에 의한 변위 %s cm, B에 의한 변위 %s cm 이다.' % (x, fn(ya), fn(yb)), '중첩의 원리에 의해 변위 = %s + %s = %d cm 이다.' % (fn(ya), fn(yb), ans)],
                  core='중첩된 구간의 변위는 각 펄스의 변위의 합이다.', point='시간이 지난 뒤 각 펄스의 위치를 구해 변위를 합한다.')
    # max: 두 펄스가 완전히 겹치는 순간(cA+t==cB-t) 최대 변위 크기
    if (cB - cA) % 2: return None
    tm = (cB - cA) // 2
    mx = hA + hB
    body = P(base + '두 펄스가 완전히 겹치는 순간의 줄의 변위가 가장 큰 곳의 변위는? (단, 위쪽을 +로 한다. 변위가 0이면 0으로 답한다.)') + fig
    ws = [hA, hB, hA - hB, abs(hA) + abs(hB), 2 * max(abs(hA), abs(hB)), mx + 1]
    return mc(body, '%d cm' % mx, ['%s cm' % fn(w) for w in ws], r=r, lv='중', fam='a',
              steps=['t = %d s 에서 두 펄스의 중심이 x = %d cm 에서 만나 완전히 겹친다.' % (tm, cA + tm), '중심에서 변위 = %d + (%d) = %d cm 이다.' % (hA, hB, mx)],
              core='완전히 겹칠 때 변위는 두 펄스의 높이(부호 포함)의 합이다.', point='부호를 고려해 중첩된 높이를 구한다.')


# ================================================================== ph096 파동의 반사(고정단·자유단)
_B96 = [
    ('고정단에서 반사된 펄스는 위상이 반대로 바뀐다(위로 볼록하던 펄스가 아래로 볼록해진다).', True, '고정단에서는 위상이 π 바뀐다.', 'fix'),
    ('고정단에서 반사된 펄스의 위상은 입사 펄스와 같다.', False, '고정단 반사 시 위상이 반대로 바뀐다.', 'fix'),
    ('자유단에서 반사된 펄스의 위상은 입사 펄스와 같다.', True, '자유단에서는 위상이 바뀌지 않는다.', 'free'),
    ('자유단에서 반사된 펄스는 위상이 반대로 바뀐다.', False, '자유단에서는 위상이 그대로이다.', 'free'),
    ('고정단에서 펄스가 반사될 때 고정된 점의 변위는 항상 0이다.', True, '입사파와 반사파가 상쇄되어 고정단의 변위는 0이다.', 'zero'),
    ('자유단에서 펄스가 완전히 반사되는 순간 자유단의 변위는 입사 펄스 높이의 2배이다.', True, '입사파와 반사파가 같은 위상으로 겹쳐 2배가 된다.', 'two'),
    ('반사된 펄스의 속력은 입사 펄스의 속력과 같다.', True, '같은 매질에서 진행하므로 속력이 같다.', 'speed'),
    ('반사된 펄스의 속력은 입사 펄스의 속력보다 작다.', False, '같은 줄에서 속력은 같다.', 'speed'),
    ('고정단에서 반사해도 펄스의 모양(높이·폭)은 변하지 않는다(위상만 반대).', True, '이상적인 경우 높이와 폭이 그대로이다.', 'shape'),
    ('반사 시 파동의 진동수와 파장은 변하지 않는다.', True, '같은 매질이므로 진동수·파장 모두 변하지 않는다.', 'fl'),
    ('줄의 끝이 벽에 단단히 고정되어 있으면 반사 펄스의 높이가 입사 펄스보다 2배가 된다.', False, '높이는 같고 위상만 반대가 된다.', 'h2'),
    ('줄의 끝이 자유롭게 움직일 수 있는 링에 연결되어 있으면 자유단 반사이다.', True, '마찰 없는 막대에 끼워진 링은 자유단이다.', 'ring'),
    ('고정단 반사에서 펄스가 위로 볼록하게 입사하면 반사 펄스는 아래로 볼록하게 진행한다.', True, '위상이 반대로 바뀐다.', 'fix2'),
    ('자유단 반사에서 펄스가 위로 볼록하게 입사하면 반사 펄스는 아래로 볼록하게 진행한다.', False, '자유단에서는 위상이 바뀌지 않아 위로 볼록한 채 반사된다.', 'free2'),
    ('반사된 펄스의 진행 방향은 입사 펄스의 반대 방향이다.', True, '벽에서 되돌아오므로 진행 방향이 반대이다.', 'dir'),
    ('반사된 펄스는 입사 펄스와 서로 영향을 주지 않고 겹칠 때 중첩된다.', True, '반사된 펄스와 입사 펄스가 겹칠 때 중첩의 원리가 적용된다.', 'sup'),
    ('고정단에서는 입사파와 반사파가 같은 위상으로 만나 보강 간섭한다.', False, '고정단에서는 위상이 반대인 두 파동이 만나 상쇄된다.', 'cancel'),
    ('줄의 끝이 고정되어 있을 때 정상파의 고정단은 마디가 된다.', True, '고정단에서는 변위가 항상 0이므로 마디이다.', 'node'),
]


@T('ph096')
def ph096(r, k):
    form = r.choice(['disp', 'disp', 'disp', 'shape', 'time', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B96)
        if not s: return None
        return bogi('줄에서 펄스가 끝점에서 반사될 때에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', s, ask='', lv='하', fam='d', r=r,
                    core='고정단 반사는 위상이 반대로 바뀌고 자유단 반사는 위상이 그대로이며, 반사 후에도 속력과 모양은 같다.', point='고정단과 자유단의 반사를 구분한다.')
    kind = r.choice(['fixed', 'free'])
    kname = '고정단' if kind == 'fixed' else '자유단'
    Rr = -1 if kind == 'fixed' else 1
    hw = 2
    h = r.choice([1, 2, 3, -1, -2, -3])
    W = 14
    wall = r.choice([10, 11, 12])
    c0 = r.choice([2, 3, 4, 5])
    if c0 + hw > wall: return None
    base = '그림은 줄을 따라 오른쪽으로 진행하는 펄스의 t = 0 일 때 모습이다. 줄의 오른쪽 끝은 %s이다. 눈금 한 칸은 1 cm이고 펄스의 속력은 1 cm/s이다. ' % kname
    fig = FIG(pulse_fig([(c0, h, hw, BL, None)], W, 3, wall=wall, wall_kind=kind, arrows=[(c0 - 1, c0 + 1, abs(h) + 0.6 if h > 0 else 0.7, BL, '')]), '78%')
    if form == 'disp':
        t = r.choice([6, 7, 8, 9, 10, 11, 12])
        x = r.choice(range(5, wall + 1))
        pc = c0 + t
        refl_c = 2 * wall - pc
        y = tri(x, pc, h, hw) + Rr * tri(x, refl_c, h, hw) if pc - hw < wall + 0 or True else 0
        # 파동이 벽 오른쪽에 있는 입사 펄스 성분은 존재하지 않음(x ≤ wall)
        y = tri(x, pc, h, hw) + Rr * tri(x, refl_c, h, hw)
        if abs(y * 2 - round(y * 2)) > 1e-9: return None
        y = round(y * 2) / 2
        # 이중 검산: 파동 방정식 해(영상법)과 직접 경로 길이 비교
        y2 = tri(x - t, c0, h, hw) + Rr * tri(2 * wall - x - t, c0, h, hw)
        assert abs(y2 - y) < 1e-9 or True
        if abs(y2 - y) > 1e-9: return None
        # 흥미로운 값만
        body = P(base + 't = %d s 일 때 x = %d cm 에서 줄의 변위는? (단, 위쪽을 +로 한다.)' % (t, x)) + fig
        hh = abs(h)
        ws = [-y if y else hh, tri(x, pc, h, hw), tri(x, refl_c, h, hw), h, -h, y + hh, 2 * h]
        both_ = tri(x, pc, h, hw) != 0 and tri(x, refl_c, h, hw) != 0
        return mc(body, '%s cm' % fn(y), ['%s cm' % fn(w) for w in ws], r=r, lv='상' if both_ else '중', fam='a',
                  steps=['반사 후 펄스는 속력이 같고, %s이므로 %s 반사된다.' % (kname, '위상이 반대로(높이의 부호가 바뀌어)' if kind == 'fixed' else '위상이 그대로')],
                  core='반사파는 끝점에 대해 대칭인 위치에서 (고정단: 부호 반전, 자유단: 부호 유지) 진행하는 펄스로 생각하여 중첩한다.', point='반사 펄스의 위치와 부호를 구해 변위를 합한다.') if False else \
            mc(body, '%d cm' % y, ['%s cm' % fn(w) for w in ws], r=r, lv='상', fam='a',
               steps=['t = %d s 일 때 입사 펄스의 중심은 x = %d cm 이다(벽을 넘어선 부분은 반사파가 대신한다).' % (t, pc), '반사된 펄스의 중심은 벽(x = %d cm)에 대칭인 x = 2 × %d - %d = %d cm 에 있고, %s이므로 높이는 %s cm 이다.' % (wall, wall, pc, refl_c, kname, fn(Rr * h)),
                      'x = %d cm 에서 입사 펄스에 의한 변위 %s cm, 반사 펄스에 의한 변위 %s cm 이므로 합은 %s cm 이다.' % (x, fn(tri(x, pc, h, hw)), fn(Rr * tri(x, refl_c, h, hw)), fn(y))],
               core='반사 펄스는 벽에 대칭인 위치에서 반대 방향으로 진행하며, 고정단에서는 부호가 반전, 자유단에서는 부호가 유지된다.', point='반사 펄스의 위치와 부호를 구해 변위를 합한다.')
    if form == 'shape':
        t = r.choice([10, 11, 12, 13, 14])
        if c0 + t - wall < hw + 1: return None
        pc = c0 + t
        refl_c = 2 * wall - pc
        if refl_c - hw < 0: return None
        hr = Rr * h
        body = P(base + 't = %d s 일 때 반사된 펄스의 꼭대기(꼭짓점)의 위치와 높이를 옳게 짝지은 것은? (단, 위쪽을 +로 한다.)' % t) + fig
        right = 'x = %d cm, %d cm' % (refl_c, hr)
        ws = ['x = %d cm, %d cm' % (refl_c, -hr), 'x = %d cm, %d cm' % (pc, hr), 'x = %d cm, %d cm' % (pc, -hr), 'x = %d cm, %d cm' % (refl_c, hr * 2), 'x = %d cm, %d cm' % (refl_c + 2, hr), 'x = %d cm, %d cm' % (refl_c - 2, -hr)]
        return mc(body, right, ws, r=r, lv='중', fam='b', sort='shuf',
                  steps=['펄스는 t = 0 에 x = %d cm 에 있고 %d s 동안 %d cm 진행하므로 벽을 지나 반사되었다(벽 x = %d cm).' % (c0, t, t, wall),
                         '반사된 펄스의 중심은 벽에 대칭인 x = 2 × %d - (%d + %d) = %d cm 이다.' % (wall, c0, t, refl_c), '%s이므로 높이는 %s cm 이다.' % (kname + ' 반사' + ('(위상 반전)' if kind == 'fixed' else '(위상 유지)'), fn(hr))],
                  core='반사된 펄스는 벽에 대칭인 위치에서 진행하고 고정단은 위상이 반전, 자유단은 유지된다.', point='반사 후 펄스의 위치와 모양을 정한다.')
    # time: 꼭짓점이 점 x에 도달하는 시각
    x = r.choice(range(3, wall - 1))
    if x <= c0: return None
    t = (wall - c0) + (wall - x)
    body = P(base + '이 펄스가 벽에서 반사되어 되돌아올 때, 반사된 펄스의 꼭대기가 x = %d cm 에 도달하는 시각은?' % x) + fig
    ws = [wall - c0, x - c0, t + 2, t - 2, 2 * wall - x - c0 + 2 if False else (wall - c0) * 2, t * 2]
    assert t == (2 * wall - x) - c0
    return mc(body, '%d s' % t, ['%d s' % w for w in ws], r=r, lv='하', fam='c',
              steps=['펄스의 꼭대기는 x = %d cm 에서 벽(x = %d cm)까지 %d cm 진행한 뒤 x = %d cm 까지 %d cm 되돌아온다.' % (c0, wall, wall - c0, x, wall - x), '총 이동 거리 %d cm 를 속력 1 cm/s 로 진행하므로 %d s 이다.' % (t, t)],
              core='반사 펄스의 속력은 입사 펄스와 같다.', point='벽까지의 왕복 거리로 시간을 구한다.')


# ================================================================== ph097 두 파원의 간섭과 경로차
_B97 = [
    ('두 파원에서 같은 위상으로 퍼져 나온 파동의 경로차가 반파장의 짝수 배이면 보강 간섭이 일어난다.', True, '경로차 = mλ 이면 마루와 마루(골과 골)가 만난다.', 'cons'),
    ('경로차가 반파장의 홀수 배이면 보강 간섭이 일어난다.', False, '경로차가 (m + ½)λ 이면 마루와 골이 만나 상쇄 간섭이 일어난다.', 'cons'),
    ('경로차가 (m + ½)λ(m = 0, 1, 2, …)이면 상쇄 간섭이 일어난다.', True, '마루와 골이 만나 변위가 상쇄된다.', 'des'),
    ('두 점파원의 위상이 같을 때 두 파원을 잇는 선분의 수직이등분선 위의 점은 항상 보강 간섭한다.', True, '경로차가 0이다.', 'perp'),
    ('두 점파원의 위상이 같을 때 수직이등분선 위의 점은 상쇄 간섭한다.', False, '경로차가 0이므로 보강 간섭이다.', 'perp'),
    ('마디선은 두 파동이 상쇄 간섭하는 점들을 이은 선이다.', True, '진폭이 0인 점들의 집합이 마디선이다.', 'node'),
    ('배선(보강선)은 두 파동이 보강 간섭하는 점들을 이은 선이다.', True, '진폭이 최대인 점들의 집합이다.', 'anti'),
    ('마디선 위의 점에서는 시간이 지나도 변위가 항상 0이다(같은 진폭일 때).', True, '두 파동의 변위가 항상 반대여서 합이 0이다.', 'node2'),
    ('파장이 길수록 두 파원 사이에서 생기는 마디선의 수는 많아진다.', False, '파장이 길면 경로차 조건을 만족하는 m의 개수가 줄어 마디선의 수가 적어진다.', 'num'),
    ('두 파원 사이의 거리가 멀수록(파장 일정) 마디선의 수는 많아진다.', True, '가능한 경로차의 범위가 커져 조건을 만족하는 선이 늘어난다.', 'num2'),
    ('보강 간섭하는 점에서는 합성파의 진폭이 한 파동의 진폭의 2배(같은 진폭일 때)이다.', True, 'A + A = 2A 이다.', 'amp'),
    ('상쇄 간섭하는 점에서는 파동의 에너지가 완전히 사라진다.', False, '에너지는 보강 간섭하는 곳으로 재분배되며 전체적으로 보존된다.', 'energy'),
    ('두 파원의 위상이 서로 반대이면 수직이등분선 위의 점에서는 상쇄 간섭이 일어난다.', True, '경로차가 0이어도 위상차가 반파장이므로 상쇄된다.', 'opp'),
    ('경로차가 한 파장이면 두 파동은 같은 위상으로 만나 보강 간섭한다.', True, 'mλ 이므로 보강이다.', 'lam'),
    ('경로차가 한 파장의 1.5배이면 보강 간섭한다.', False, '1.5λ = (1 + ½)λ 이므로 상쇄 간섭이다.', 'lam2'),
    ('간섭무늬는 두 파동이 중첩되어 진폭이 위치에 따라 달라져 생긴다.', True, '위치에 따른 보강·상쇄의 분포이다.', 'pattern'),
    ('간섭 현상은 파동에서만 나타나므로 빛이 파동임을 보여 주는 증거가 된다.', True, '입자는 간섭하지 않는다.', 'wave'),
    ('수면파에서 마루와 마루가 만나는 점은 상쇄 간섭하는 점이다.', False, '마루와 마루가 만나면 보강 간섭이다.', 'cc'),
]


def _count_points(d_over_lam, kind):
    """두 파원(같은 위상)을 잇는 선분 위(파원 제외)의 보강 또는 상쇄 점의 수."""
    d = Fr(d_over_lam)
    cnt = 0
    for m2 in range(-40, 41):
        pd = Fr(m2, 2)  # 경로차를 λ 단위로 (반정수)
        if kind == 'con' and m2 % 2 == 0 and abs(pd) < d: cnt += 1
        if kind == 'des' and m2 % 2 != 0 and abs(pd) < d: cnt += 1
    return cnt


@T('ph097')
def ph097(r, k):
    form = r.choice(['fig', 'fig', 'fig', 'num', 'num', 'count', 'count', 'bogi'])
    if form == 'bogi':
        s = pick3(r, _B97)
        if not s: return None
        return bogi('두 점파원에서 같은 위상으로 퍼져 나가는 파동의 간섭에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' if False else '두 파원에서 퍼져 나가는 파동의 간섭에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?',
                    s, ask='', lv=r.choice(['하', '중']), fam='d', r=r, core='두 파원이 같은 위상이면 경로차가 mλ 일 때 보강, (m + ½)λ 일 때 상쇄 간섭이 일어난다.', point='경로차와 간섭 조건을 연결한다.')
    if form == 'fig':
        n = r.choice([2, 3, 4])
        ps = src_points(r, n)
        if not ps: return None
        names = 'PQR'
        res = []
        for (a, b) in ps:
            diff = abs(a - b)
            res.append('con' if diff % 2 == 0 else 'des')
        fig = FIG(src_fig(n, [(a, b, names[i]) for i, (a, b) in enumerate(ps)]), '82%')
        ask = r.choice(['con', 'des', 'one', 'diff'])
        base = '그림은 같은 위상으로 진동하는 두 점파원 S₁, S₂에서 발생한 물결파의 마루(실선)와 골(점선)을 어느 순간에 나타낸 것이다. 인접한 실선과 점선 사이의 거리는 반파장이다. 점 P, Q, R는 두 파가 만나는 지점이다. '
        if ask in ('con', 'des'):
            S = [i for i in range(3) if res[i] == ask]
            if not S: return None
            right = ', '.join(names[i] for i in S)
            allc = [', '.join(names[i] for i in c) for m_ in (1, 2, 3) for c in itertools.combinations(range(3), m_)]
            wr = [c for c in allc if c != right]
            nm = '보강' if ask == 'con' else '상쇄'
            body = P(base + '%s 간섭이 일어나는 점만을 있는 대로 고른 것은?' % nm) + fig
            stp = ['점 %s: S₁에서 %d × λ/2, S₂에서 %d × λ/2 이므로 경로차는 |%d - %d| × λ/2 = %s λ → %s' % (names[i], ps[i][0], ps[i][1], ps[i][0], ps[i][1], fn(Fr(abs(ps[i][0] - ps[i][1]), 2)), '보강' if res[i] == 'con' else '상쇄') for i in range(3)]
            return mc(body, right, wr, r=r, lv='중', fam='a', sort='shuf', steps=stp + ['%s 간섭하는 점은 %s 이다.' % (nm, right)],
                      core='같은 위상의 두 파원에서 경로차가 λ의 정수배이면 보강, 반정수배이면 상쇄 간섭이다.', point='마루·골 원의 교점에서 경로차를 읽는다.')
        i = r.randrange(3)
        a, b = ps[i]
        if ask == 'one':
            diffl = Fr(abs(a - b), 2)
            body = P(base + '점 %s에서 두 파동의 경로차는? (파장을 λ라 한다.)' % names[i]) + fig
            right = ('%sλ' % fn(diffl)) if diffl != 0 else '0'
            cands = {Fr(1, 2), Fr(1), Fr(3, 2), Fr(2), Fr(5, 2), Fr(0), Fr(3), Fr(1, 4)}
            wr = [('%sλ' % fn(c)) if c else '0' for c in cands if c != diffl]
            return mc(body, right, wr, r=r, lv='하' if diffl in (0, 1) else '중', fam='a', sort='shuf',
                      steps=['점 %s는 S₁에서 반파장의 %d배, S₂에서 반파장의 %d배 거리에 있다.' % (names[i], a, b), '경로차 = |%d - %d| × λ/2 = %s λ 이다.' % (a, b, fn(diffl)) if diffl else '경로차는 0 이다.'],
                      core='경로차 = |S₁P - S₂P|.', point='그림에서 두 파원까지의 거리를 읽어 경로차를 구한다.')
        Aa = r.choice([1, 2, 3, 4])
        amp = 2 * Aa if res[i] == 'con' else 0
        body = P(base + '각 파원에서 발생한 파동의 진폭이 %d cm일 때, 점 %s에서 합성파의 진폭은?' % (Aa, names[i])) + fig
        wr = [Aa * 2 if res[i] != 'con' else 0, Aa, Aa * 4, Aa + 1, Aa / 2 if Aa % 2 == 0 else Aa + 3]
        return mc(body, '%d cm' % amp, ['%s cm' % fn(w) for w in wr], r=r, lv='중', fam='a', sort='shuf',
                  steps=['점 %s의 경로차는 %s λ 이므로 %s 간섭이다.' % (names[i], fn(Fr(abs(a - b), 2)), '보강' if res[i] == 'con' else '상쇄'), '합성파의 진폭 = %s cm 이다.' % ('%d + %d = %d' % (Aa, Aa, 2 * Aa) if res[i] == 'con' else '|%d - %d| = 0' % (Aa, Aa))],
                  core='보강 간섭에서는 진폭의 합 2A, 상쇄 간섭에서는 0이다.', point='간섭의 종류로 합성파의 진폭을 구한다.')
    if form == 'num':
        lam = r.choice([1, 2, 3, 4, 5])
        samep = r.random() < 0.75
        m = r.choice([0, 1, 2, 3, 4])
        half = r.random() < 0.5
        diff = Fr(lam) * (m + (Fr(1, 2) if half else 0))
        if diff == 0 and r.random() < .5: pass
        s1 = r.randint(4, 12)
        s2 = s1 + int(diff) if diff.denominator == 1 else None
        if s2 is None:
            lam = r.choice([2, 4])
            diff = Fr(lam) * (m + (Fr(1, 2) if half else 0))
            if diff.denominator != 1: return None
            s2 = s1 + int(diff)
        d = abs(s2 - s1)
        con_same = (not half)
        con = con_same if samep else (not con_same)
        who = '같은 위상' if samep else '서로 반대 위상'
        body = P('%s으로 진동하는 두 점파원 S₁, S₂에서 발생한 파장 %d m인 물결파가 점 P에서 만난다. S₁P = %d m, S₂P = %d m 일 때, P에서 일어나는 간섭은?' % (who, lam, s1, s2))
        right = '보강 간섭' if con else '상쇄 간섭'
        wr = ['상쇄 간섭' if con else '보강 간섭', '간섭이 일어나지 않는다', '경로차가 0이므로 보강 간섭', '경로차가 %d m이므로 항상 상쇄 간섭' % d]
        if right in wr: wr.remove(right)
        wr = [w for w in wr if w != right]
        wr += ['변위가 항상 최대']
        pd_l = Fr(d, lam)
        stp = ['경로차 = |%d - %d| = %d m = %s λ 이다.' % (s1, s2, d, fr_str(pd_l))]
        if samep:
            stp.append('같은 위상이므로 경로차가 %s이면 %s 간섭이다.' % ('λ의 정수배' if not half else 'λ의 반정수배', right))
        else:
            stp.append('위상이 반대이므로 경로차가 %s이어도 위상차 반파장이 더해져 %s 간섭이다.' % ('λ의 정수배' if not half else 'λ의 반정수배', right))
        return mc(body, right, wr, r=r, lv='중' if samep else '상', fam='b', sort='shuf', steps=stp,
                  core='같은 위상의 파원: 경로차 = mλ 보강, (m + ½)λ 상쇄. 반대 위상이면 조건이 서로 바뀐다.', point='경로차를 파장으로 환산해 판정한다.')
    # count
    d = Fr(r.choice([2, 3, 4, 5, 6, 7, 8])) / r.choice([1, 2])
    lam = Fr(1)
    kd = r.choice(['con', 'des'])
    Lm = r.choice([1, 2, 3])
    dm = d * Lm
    cnt = _count_points(d, kd)
    # 이중 검산: 직접 위치 계산
    xs = []
    for m2 in range(-80, 81):
        pd = Fr(m2, 2)
        if (kd == 'con') == (m2 % 2 == 0):
            x = (dm + pd * Lm) / 2
            if 0 < x < dm: xs.append(x)
    assert len(xs) == cnt
    fig = FIG(src_fig(int(d) if d.denominator == 1 else 3, nmax=9), '70%') if False else ''
    body = P('같은 위상으로 진동하는 두 점파원 S₁, S₂가 %s m 떨어져 있고 파장은 %s m이다. 두 파원을 잇는 선분 위에서(S₁, S₂는 제외) %s 간섭이 일어나는 지점은 모두 몇 개인가?' % (fn(dm), fn(Fr(Lm)), '보강' if kd == 'con' else '상쇄'))
    ws = [cnt + 1, cnt - 1, cnt + 2, cnt * 2, max(cnt // 2, 0) if cnt // 2 != cnt else cnt + 3, cnt + 3]
    ws = [w for w in ws if w >= 0]
    ratio = Fr(dm, Lm)
    return mc(body, '%d개' % cnt, ['%d개' % w for w in ws], r=r, lv='상', fam='c',
              steps=['선분 위의 점 P가 S₁에서 x 만큼 떨어져 있으면 경로차는 |x - (%s - x)| = |2x - %s| 이고, 이 값은 0 이상 %s m 미만이다(파원 제외).' % (fn(dm), fn(dm), fn(dm)),
                     '%s 조건: 경로차 = %s 이다. 파장 %s m 이므로 가능한 경로차는 %s 이다.' % ('보강' if kd == 'con' else '상쇄', 'mλ' if kd == 'con' else '(m + ½)λ', fn(Fr(Lm)), '0, ±%s, ±%s, … (%s m 미만)' % (fn(Fr(Lm)), fn(Fr(2 * Lm)), fn(dm)) if kd == 'con' else '±%s, ±%s, … (%s m 미만)' % (fn(Fr(Lm, 2)), fn(Fr(3 * Lm, 2)), fn(dm))),
                     '이를 만족하는 지점은 모두 %d개이다.' % cnt],
              core='두 파원 사이에서 경로차가 mλ(보강) 또는 (m + ½)λ(상쇄)이고 절댓값이 파원 사이 거리보다 작은 지점의 수를 센다.', point='경로차의 범위에서 조건을 만족하는 정수 m을 센다.')
