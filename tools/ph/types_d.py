# -*- coding: utf-8 -*-
"""Ⅰ-D 포물선 운동 (ph027~ph034) 생성기."""
from phlib import *
import math, re as _re
from fractions import Fraction as Fr

G = 10  # 중력 가속도 m/s²


# ---------------------------------------------------------------- 글자·도우미
def _pick(w, tag):
    a, b = {'이(가)': ('이', '가'), '은(는)': ('은', '는'), '을(를)': ('을', '를')}[tag]
    c = ord(w) - 0xAC00
    return a if (0 <= c < 11172 and c % 28 != 0) else b


def fix(s):
    return _re.sub(r'(\S)(이\(가\)|은\(는\)|을\(를\))', lambda m: m.group(1) + _pick(m.group(1), m.group(2)), s)


def PP(*t):
    return P(fix(''.join(t)))


def half(x): return abs(x * 2 - round(x * 2)) < 1e-9
def two(x): return abs(x * 100 - round(x * 100)) < 1e-6


def wl(right, cands, unit, nonneg=True):
    out, seen = [], {num(round(right, 2))}
    fill = [right * 2, right / 2, right * 1.5, right + 10, right - 5, right + 5, right * 3, right + 3, right - 3, right + 1, right - 1, right + 2, right - 2]
    for c in list(cands) + fill:
        if c is None: continue
        c = round(c, 2)
        if nonneg and c <= 0: continue
        if abs(c * 10 - round(c * 10)) > 1e-6 and abs(right * 10 - round(right * 10)) < 1e-6 and len(out) >= 3 and c in fill: continue
        s = num(c)
        if s in seen: continue
        seen.add(s); out.append(s + ' ' + unit)
    return out


def ans(x, unit): return num(round(x, 2)) + ' ' + unit


def ticks_ok(vals, span_px, minpx):
    vs = sorted(set(vals))
    return all((b - a) * span_px >= minpx for a, b in zip(vs, vs[1:]))


# ---------------------------------------------------------------- 정확한 삼각비 (계수 × √근호)
def _sqfree(n):
    k = 1
    d = 2
    while d * d <= n:
        while n % (d * d) == 0:
            n //= d * d; k *= d
        d += 1
    return k, n


class Q:
    def __init__(s, c, rad=1):
        k, m = _sqfree(rad)
        s.c, s.r = Fr(c) * k, m
    def __mul__(s, o):
        if isinstance(o, Q): return Q(s.c * o.c, s.r * o.r)
        return Q(s.c * Fr(o), s.r)
    __rmul__ = __mul__
    def __float__(s): return float(s.c) * math.sqrt(s.r)
    def rational(s): return s.r == 1
    def term(s):
        d = s.c.denominator
        while d % 2 == 0: d //= 2
        while d % 5 == 0: d //= 5
        return d == 1
    def fmt(s):
        if not s.term(): return None
        if s.r == 1: return num(float(s.c))
        cs = '' if s.c == 1 else num(float(s.c))
        return cs + '√' + str(s.r)


SIN = {30: Q(Fr(1, 2)), 37: Q(Fr(3, 5)), 45: Q(Fr(1, 2), 2), 53: Q(Fr(4, 5)), 60: Q(Fr(1, 2), 3)}
COS = {30: Q(Fr(1, 2), 3), 37: Q(Fr(4, 5)), 45: Q(Fr(1, 2), 2), 53: Q(Fr(3, 5)), 60: Q(Fr(1, 2))}
SINS = {30: '1/2', 37: '3/5', 45: '√2/2', 53: '4/5', 60: '√3/2'}
COSS = {30: '√3/2', 37: '4/5', 45: '√2/2', 53: '3/5', 60: '1/2'}


def qs(q, unit=''):
    f = q.fmt()
    if f is None: return None
    return f + (' ' + unit if unit else '')


def wlq(right_q, cand_vals, unit, extra_q=()):
    """Q 형태의 정답에 대한 오답 목록(문자열). cand_vals: 같은 형태로 표현 가능한 Q 또는 수."""
    seen = {right_q.fmt()}
    out = []
    for c in list(cand_vals) + list(extra_q):
        if c is None: continue
        if not isinstance(c, Q): c = Q(Fr(c).limit_denominator(1000))
        f = c.fmt()
        if f is None or f in seen or float(c) <= 0: continue
        seen.add(f); out.append(f + ' ' + unit)
    return out


# ---------------------------------------------------------------- 그림 도구
def arc_label(f, x, y, r_, deg, text):
    th = math.radians(deg)
    f.o.append('<path d="M %s %s A %s %s 0 0 0 %s %s" fill="none" stroke="%s" stroke-width="1.3"/>' % (Fig._n(x + r_), Fig._n(y), r_, r_, Fig._n(x + r_ * math.cos(th)), Fig._n(y - r_ * math.sin(th)), GR))
    f.text(x + r_ + 6, y - r_ * math.sin(th) / 2 + 4, text, 13, 'start', True, GR)


def cliff_fig(hl, v0l, xl, w=300, h=200, cliff=True):
    """절벽 위에서 수평 투사. hl/v0l/xl: 라벨 문자열(알려진 값 또는 '?')."""
    f = Fig(w, h)
    gy = h - 30; top = 52; bx = 84
    f.hatch(14, gy, w - 28)
    f.poly([(14, top), (bx, top), (bx, gy), (14, gy)], '#eef2f7', INK, 1.6)
    ex = w - 36
    pts = [(bx + (ex - bx) * u / 40, top + (gy - top) * (u / 40) ** 2) for u in range(41)]
    f.poly(pts, 'none', BL, 2.2, close=False, dash='5 3')
    f.circ(bx, top - 7, 6.5, RD, INK, 1.2)
    f.arrow(bx + 8, top - 7, bx + 52, top - 7, RD, 2.2)
    f.text(bx + 58, top - 12, v0l, 12.5, 'start', True, RD)
    f.circ(ex, gy - 7, 6.5, RD, INK, 1.2)
    f.line(30, top, 30, gy, GR, 1.2); f.line(24, top, 36, top, GR, 1.2); f.line(24, gy, 36, gy, GR, 1.2)
    f.text(42, (top + gy) / 2 + 4, hl, 13, 'start', True)
    f.arrow(bx, gy + 14, ex, gy + 14, GR, 1.4); f.arrow(ex, gy + 14, bx, gy + 14, GR, 1.4)
    f.text((bx + ex) / 2, gy + 26, xl, 13, bold=True)
    return f.svg()


def vec_fig(vx, vy, v, w=270, h=200):
    """착지 직전 속도 v 와 성분. 라벨은 문자열(값 또는 기호). 수평 오른쪽 vx, 아래 vy."""
    f = Fig(w, h)
    ox, oy = 44, 40
    sx, sy = 150, 110
    f.circ(ox, oy, 4, INK, INK, 1)
    f.line(ox, oy, ox + sx, oy, GR, 1.2, '4 3'); f.line(ox + sx, oy, ox + sx, oy + sy, GR, 1.2, '4 3')
    f.arrow(ox, oy, ox + sx - 3, oy, BL, 2.4)
    f.arrow(ox, oy, ox, oy + sy - 3, GN, 2.4) if False else None
    f.arrow(ox + sx, oy, ox + sx, oy + sy - 3, GN, 2.4)
    f.arrow(ox, oy, ox + sx - 3, oy + sy - 3, RD, 2.6)
    f.text(ox + sx / 2, oy - 8, vx, 13, bold=True, c=BL)
    f.text(ox + sx + 8, oy + sy / 2, vy, 13, 'start', True, GN)
    f.text(ox + 6, oy + sy / 2 + 26, v, 13, 'start', True, RD)
    arc_label(f, ox, oy, 0, 0, '') if False else None
    return f.svg()


def traj_fig(deg, v0l='v₀', thl='θ', Hl=None, Tl=None, Rl=None, w=310, h=195, pts_mark=None):
    """비스듬히 던진 물체의 궤도(모양은 sinθ 에 따른 개략도)."""
    f = Fig(w, h)
    gy = h - 28; x0 = 30; R = 250
    H = R / 4 * math.tan(math.radians(deg)); H = min(H, 118)
    f.hatch(14, gy, w - 28)
    pts = [(x0 + R * u / 50, gy - 4 * H * (u / 50) * (1 - u / 50)) for u in range(51)]
    f.poly(pts, 'none', BL, 2.2, close=False, dash='5 3')
    L = 54
    th = math.radians(deg)
    f.arrow(x0, gy, x0 + L * math.cos(th), gy - L * math.sin(th), RD, 2.4)
    f.text(x0 + L * math.cos(th) + 4, gy - L * math.sin(th) - 2, v0l, 12.5, 'start', True, RD)
    arc_label(f, x0, gy, 24, deg, thl)
    f.circ(x0, gy, 4, INK, INK, 1)
    if Hl:
        ax = x0 + R / 2
        f.line(ax, gy, ax, gy - H, GR, 1.2, '4 3')
        f.text(ax + 6, gy - H / 2 + 4, Hl, 13, 'start', True)
        f.circ(ax, gy - H, 4, RD, INK, 1)
    if Rl:
        f.arrow(x0, gy + 15, x0 + R, gy + 15, GR, 1.4); f.arrow(x0 + R, gy + 15, x0, gy + 15, GR, 1.4)
        f.text(x0 + R / 2, gy + 26, Rl, 13, bold=True)
    if Tl:
        f.text(x0 + R - 4, gy - 30, Tl, 12.5, 'end', True, GR)
    return f.svg()


# ================================================================ ph027
TS = [1, 2, 3, 4, 5, 6, 7, 8]


@T('ph027')
def horiz_throw(r, k):
    """수평으로 던진 물체의 낙하 시간과 도달 거리."""
    form = r.choice(['t', 't', 'x', 'x', 'v0', 'h', 'ratio', 'dist', 'fig_x', 'fig_v0', 'fig_t'])
    ob = r.choice(['공', '돌멩이', '야구공', '구슬', '쇠구슬'])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    t = r.choice(TS); h = 5 * t * t
    v0 = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25])
    x = v0 * t
    if form == 't':
        if r.random() < .5:
            body = PP('높이 %s m 인 지점에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 지면에 닿을 때까지 걸리는 시간은? %s' % (num(h), ob, U(v0, 'm/s'), ob, cond))
        else:
            body = PP('수평면으로부터 %s 높이에서 %s을(를) 수평 방향으로 던졌다. %s의 처음 속력이 %s일 때, 지면에 닿을 때까지 걸리는 시간은? %s' % (U(h, 'm'), ob, ob, U(v0, 'm/s'), cond))
        assert abs(math.sqrt(2 * h / G) - t) < 1e-9
        wr = wl(t, [h / v0, math.sqrt(h) / 2, h / 10, x / (2 * v0), t + 1, t - 1, 2 * t], 's')
        return mc(body, ans(t, 's'), wr, r=r, lv='하', fam='a',
                  steps=['연직 방향은 자유 낙하와 같으므로 h = ½gt² 이다.', '%s = ½ × 10 × t² 에서 t² = %s 이므로 t = %s s' % (num(h), num(t * t), num(t)), '(낙하 시간은 처음 수평 속력과 무관하다.)'],
                  core='수평 투사에서 낙하 시간은 연직 방향 자유 낙하로 결정되며 t = √(2h/g) 이다.', point='낙하 시간은 수평 속력과 관계없이 높이만으로 정해진다.')
    if form == 'x':
        body = PP('높이 %s m 에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 지면에 닿은 지점은 던진 지점의 바로 아래 지면으로부터 수평으로 몇 m 떨어져 있는가? %s' % (num(h), ob, U(v0, 'm/s'), ob, cond))
        wr = wl(x, [v0 * math.sqrt(h), v0 * h / 10, h, v0 * t / 2, v0 * t * 2, x + v0, math.sqrt(x * x + h * h)], 'm')
        return mc(body, ans(x, 'm'), wr, r=r, lv='중', fam='a',
                  steps=['낙하 시간 : h = ½gt² 에서 %s = 5t² 이므로 t = %s s' % (num(h), num(t)), '수평 방향은 등속 운동이므로 x = v₀t = %s × %s = %s m' % (num(v0), num(t), num(x))],
                  core='수평 투사에서 수평 도달 거리는 x = v₀t = v₀√(2h/g) 이다.', point='낙하 시간을 먼저 구한 뒤 수평 등속 운동으로 거리를 구한다.')
    if form == 'v0':
        body = PP('높이 %s m 에서 %s을(를) 수평 방향으로 던졌더니 던진 지점의 바로 아래 지면으로부터 %s 떨어진 곳에 떨어졌다. %s을(를) 던진 속력은? %s' % (num(h), ob, U(x, 'm'), ob, cond))
        wr = wl(v0, [x / h, x / math.sqrt(h), x / 2, x / (t + 1), x / (t - 1) if t > 1 else None, x * t, math.sqrt(x * x / h)], 'm/s')
        return mc(body, ans(v0, 'm/s'), wr, r=r, lv='중', fam='b',
                  steps=['낙하 시간 : %s = 5t² 에서 t = %s s' % (num(h), num(t)), 'x = v₀t 에서 v₀ = x/t = %s / %s = %s m/s' % (num(x), num(t), num(v0))],
                  core='수평 방향 등속 운동 x = v₀t 와 연직 방향 자유 낙하 h = ½gt² 를 연결한다.', point='낙하 시간을 구한 뒤 처음 속력을 구한다.')
    if form == 'h':
        body = PP('절벽 위에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌더니 절벽 끝의 바로 아래 지면으로부터 %s 떨어진 곳에 떨어졌다. 절벽의 높이는? %s' % (ob, U(v0, 'm/s'), U(x, 'm'), cond))
        wr = wl(h, [x, x * x / 20, 5 * t, 10 * t * t, 5 * t * t / 2, x / 2 * t, h + 5], 'm')
        assert abs(h - 5 * (x / v0) ** 2) < 1e-9
        return mc(body, ans(h, 'm'), wr, r=r, lv='중', fam='c',
                  steps=['낙하 시간 : x = v₀t 에서 t = %s/%s = %s s' % (num(x), num(v0), num(t)), '높이 : h = ½gt² = ½ × 10 × %s² = %s m' % (num(t), num(h))],
                  core='수평 거리와 속력으로 낙하 시간을 구하고, 그 시간으로 높이를 구한다.', point='수평 방향에서 시간을, 연직 방향에서 높이를 구한다.')
    if form == 'ratio':
        v2 = v0 * r.choice([2, 3, 0.5]); h2 = h * r.choice([4, 9, 1, 0.25]) if h * 0.25 == int(h * 0.25) else h * 4
        t2 = math.sqrt(2 * h2 / G); x2 = v2 * t2
        if not two(x2) or not two(t2) or not two(v2): return None
        body = PP('높이 h 에서 수평으로 속력 v 로 던진 %s의 수평 도달 거리가 %s이다. 같은 장소에서 %s을(를) 높이 %s에서 수평으로 속력 %s로 던질 때의 수평 도달 거리는? %s' % (ob, U(x, 'm'), ob, U(h2, 'm'), U(v2, 'm/s'), cond) if False else
                 '높이 %s에서 %s을(를) 수평으로 %s의 속력으로 던졌더니 수평 도달 거리가 %s였다. 같은 %s을(를) 높이 %s에서 수평으로 %s의 속력으로 던질 때 수평 도달 거리는? %s' % (U(h, 'm'), ob, U(v0, 'm/s'), U(x, 'm'), ob, U(h2, 'm'), U(v2, 'm/s'), cond))
        wr = wl(x2, [x * v2 / v0, x * h2 / h, x * (v2 / v0) * (h2 / h), x * math.sqrt(h2 / h), x2 * 2, x2 / 2], 'm')
        return mc(body, ans(x2, 'm'), wr, r=r, lv='상', fam='d',
                  steps=['x = v₀√(2h/g) 이므로 x ∝ v₀√h 이다.', '속력은 %s배, 높이는 %s배이므로 수평 도달 거리는 %s × %s = %s배 : %s × %s = %s m' % (num(v2 / v0), num(h2 / h), num(v2 / v0), num(math.sqrt(h2 / h)), num(v2 / v0 * math.sqrt(h2 / h)), num(x), num(v2 / v0 * math.sqrt(h2 / h)), num(x2))],
                  core='수평 도달 거리는 처음 속력에 비례하고 높이의 제곱근에 비례한다.', point='속력과 높이가 함께 바뀔 때 비례 관계를 곱한다.')
    if form == 'dist':
        cand = [(4, 15, 100), (2, 7.5, 25), (6, 22.5, 225), (6, 40, 300), (4, 37.5, 170), (4, 20, 100 * math.sqrt(2) / 1)]
        cand = [c for c in cand if abs(c[2] - round(c[2])) < 1e-9 and c[2] in (100, 25, 225, 300, 170)]
        tt, vv, dd = r.choice(cand); tt = int(tt)
        assert abs(math.hypot(vv * tt, 5 * tt * tt) - dd) < 1e-9
        body = PP('%s을(를) 수평 방향으로 %s의 속력으로 던졌다. 던진 지 %s 후 %s의 위치는 처음 위치로부터 직선거리로 몇 m 떨어져 있는가? %s' % (ob, U(vv, 'm/s'), U(tt, '초'), ob, cond))
        wr = wl(dd, [vv * tt + 5 * tt * tt, vv * tt, 5 * tt * tt, abs(vv * tt - 5 * tt * tt), dd - 10, dd + 10], 'm')
        return mc(body, ans(dd, 'm'), wr, r=r, lv='상', fam='e',
                  steps=['수평 이동 거리 x = v₀t = %s × %s = %s m' % (num(vv), num(tt), num(vv * tt)), '연직 낙하 거리 y = ½gt² = 5 × %s² = %s m' % (num(tt), num(5 * tt * tt)), '직선거리 = √(%s² + %s²) = %s m' % (num(vv * tt), num(5 * tt * tt), num(dd))],
                  core='수평 투사한 물체의 위치는 수평 성분 v₀t 와 연직 성분 ½gt² 로 나타내며, 직선거리는 피타고라스 정리로 구한다.', point='두 방향의 이동 거리를 따로 구한 뒤 합성한다.')
    if form == 'fig_x':
        fig = cliff_fig('h = %s m' % num(h), 'v₀ = %s m/s' % num(v0), 'x')
        body = PP('그림은 절벽 위에서 %s을(를) 수평으로 던져 지면에 떨어질 때까지의 경로를 나타낸 것이다. x 는? %s' % (ob, cond)) + FIG(fig, '66%')
        wr = wl(x, [v0 * math.sqrt(h), h, v0 * h / 10, x * 2, x / 2, x + v0], 'm')
        return mc(body, ans(x, 'm'), wr, r=r, lv='중', fam='f',
                  steps=['t = √(2h/g) = √(2 × %s / 10) = %s s' % (num(h), num(t)), 'x = v₀t = %s × %s = %s m' % (num(v0), num(t), num(x))],
                  core='수평 투사에서 수평 도달 거리는 x = v₀t = v₀√(2h/g) 이다.', point='그림의 값을 읽어 낙하 시간과 수평 거리를 구한다.')
    if form == 'fig_v0':
        fig = cliff_fig('h = %s m' % num(h), 'v₀', 'x = %s m' % num(x))
        body = PP('그림은 절벽 위에서 %s을(를) 수평으로 던져 지면에 떨어질 때까지의 경로를 나타낸 것이다. 던진 속력 v₀ 는? %s' % (ob, cond)) + FIG(fig, '66%')
        wr = wl(v0, [x / h, x / math.sqrt(h), x / 2, x / (t + 1), x * t, v0 + 5], 'm/s')
        return mc(body, ans(v0, 'm/s'), wr, r=r, lv='중', fam='f',
                  steps=['t = √(2h/g) = %s s' % num(t), 'v₀ = x/t = %s / %s = %s m/s' % (num(x), num(t), num(v0))],
                  core='수평 방향은 등속이므로 v₀ = x/t 이다.', point='그림에서 높이와 수평 거리를 읽는다.')
    fig = cliff_fig('h = %s m' % num(h), 'v₀ = %s m/s' % num(v0), 'x = %s m' % num(x))
    body = PP('그림은 절벽 위에서 %s을(를) 수평으로 던져 지면에 떨어질 때까지의 경로를 나타낸 것이다. 던진 순간부터 지면에 닿을 때까지 걸린 시간은? %s' % (ob, cond)) + FIG(fig, '66%')
    wr = wl(t, [x / h, h / v0, x / v0 + 1, math.sqrt(h) / 2, t + 1, t * 2], 's')
    assert abs(x / v0 - t) < 1e-9
    return mc(body, ans(t, 's'), wr, r=r, lv='하', fam='f',
              steps=['연직 방향 : h = ½gt² 에서 t = √(2 × %s / 10) = %s s' % (num(h), num(t)), '(수평 방향으로 확인 : t = x/v₀ = %s/%s = %s s)' % (num(x), num(v0), num(t))],
              core='낙하 시간은 높이로 구하며, 수평 방향 x = v₀t 로 확인할 수 있다.', point='그림의 두 값 중 시간을 쉽게 구할 수 있는 방향을 고른다.')


# ================================================================ ph028
TRI = [(24, 10, 26), (15, 20, 25), (40, 30, 50), (30, 40, 50), (45, 60, 75), (21, 20, 29), (48, 20, 52), (60, 80, 100), (80, 60, 100), (20, 15, 25), (36, 15, 39), (30, 40, 50), (10, 24, 26), (20, 48, 52), (35, 12, 37)]
TRI = [t for t in TRI if t[1] % 5 == 0]


@T('ph028')
def horiz_land_vel(r, k):
    """수평 투사 물체의 도달 속도(크기·방향)."""
    form = r.choice(['speed', 'speed', 'angle', 'angle', 'v0', 'fig_t', 'fig_h', 'fig_speed', 'fig_speed', 'at45', 'vy', 'vy', 'speed'])
    ob = r.choice(['공', '돌멩이', '야구공', '구슬'])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    vx, vy, v = r.choice(TRI); t = vy / 10; h = 5 * t * t
    if not two(h): return None
    assert abs(math.hypot(vx, vy) - v) < 1e-9 and abs(vy ** 2 - 2 * G * h) < 1e-9
    if form == 'speed':
        body = PP('높이 %s에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 지면에 닿는 순간의 속력은? %s' % (U(h, 'm'), ob, U(vx, 'm/s'), ob, cond))
        wr = wl(v, [vx + vy, vx, vy, abs(vx - vy), math.sqrt(vx * vx + 2 * G * h * 2), (vx + vy) / 2, v + 5], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='a',
                  steps=['연직 속도 : v_y² = 2gh = 2 × 10 × %s = %s 이므로 v_y = %s m/s' % (num(h), num(vy * vy), num(vy)), '수평 속도는 변하지 않아 v_x = %s m/s' % num(vx), 'v = √(v_x² + v_y²) = √(%s² + %s²) = %s m/s' % (num(vx), num(vy), num(v))],
                  core='수평 투사한 물체의 지면 도달 속력은 수평 성분(일정)과 연직 성분(√2gh)의 합성이다.', point='두 속도 성분을 구한 뒤 피타고라스 정리로 합성한다.')
    if form == 'angle':
        ang = r.choice([37, 45, 53])
        vxx = {37: 40, 45: 30, 53: 30}[ang] * r.choice([1, 1]) if False else None
        # 방향각 : tanθ = vy/vx
        pairs = {37: [(40, 30), (20, 15)], 45: [(10, 10), (20, 20), (30, 30), (40, 40)], 53: [(15, 20), (30, 40)]}
        vx2, vy2 = r.choice(pairs[ang]); t2 = vy2 / 10; h2 = 5 * t2 * t2
        body = PP('높이 %s에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 지면에 닿는 순간의 속도가 수평면과 이루는 각 θ 는? (단, sin37° = 0.6, cos37° = 0.8 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (U(h2, 'm'), ob, U(vx2, 'm/s'), ob))
        assert abs(math.degrees(math.atan2(vy2, vx2)) - ang) < 0.5
        wr = ['%d°' % a_ for a_ in (30, 37, 45, 53, 60) if a_ != ang]
        return mc(body, '%d°' % ang, wr, r=r, lv='중', fam='b', sort='shuf',
                  steps=['v_y = √(2gh) = √(2 × 10 × %s) = %s m/s, v_x = %s m/s' % (num(h2), num(vy2), num(vx2)), 'tanθ = v_y/v_x = %s/%s = %s' % (num(vy2), num(vx2), num(vy2 / vx2)), 'θ = %d°' % ang],
                  core='속도의 방향은 tanθ = v_y/v_x 로 구한다.', point='연직·수평 성분의 비로 방향각을 구한다.')
    if form == 'v0':
        body = PP('높이 %s에서 %s을(를) 수평 방향으로 던졌더니 지면에 닿는 순간의 속력이 %s이었다. %s을(를) 던진 속력은? %s' % (U(h, 'm'), ob, U(v, 'm/s'), ob, cond))
        wr = wl(vx, [v - vy, v - math.sqrt(2 * G * h), vy, v / 2, math.sqrt(v * v - h), v - 10, vx + 5], 'm/s')
        return mc(body, ans(vx, 'm/s'), wr, r=r, lv='상', fam='c',
                  steps=['v_y² = 2gh = 2 × 10 × %s = %s' % (num(h), num(vy * vy)), 'v² = v₀² + v_y² 에서 v₀² = %s² - %s = %s' % (num(v), num(vy * vy), num(vx * vx)), 'v₀ = %s m/s' % num(vx)],
                  core='도달 속력의 제곱은 수평 성분의 제곱과 연직 성분의 제곱의 합이다.', point='제곱의 합 관계를 거꾸로 이용한다.')
    if form in ('fig_t', 'fig_h', 'fig_speed'):
        which = {'fig_t': 't', 'fig_h': 'h', 'fig_speed': 's'}[form]
        lab = ['v_x = %s m/s' % num(vx), 'v_y', 'v = %s m/s' % num(v)]
        if which == 'h': lab = ['v_x = %s m/s' % num(vx), 'v_y', 'v = %s m/s' % num(v)]
        if which == 's': lab = ['v_x = %s m/s' % num(vx), 'v_y = %s m/s' % num(vy), 'v']
        fig = vec_fig(*lab)
        base = '그림은 수평으로 던진 %s이(가) 지면에 닿는 순간의 속도 v 와 수평·연직 성분을 나타낸 것이다. ' % ob
        if which == 't':
            body = PP(base + '%s을(를) 던진 순간부터 지면에 닿을 때까지 걸린 시간은? %s' % (ob, cond)) + FIG(fig, '56%')
            wr = wl(t, [vy / 5, vy, h / 10, t + 1, vx / 10, v / 10 + 0.5, math.sqrt(h)], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='중', fam='d',
                      steps=['v_y² = v² - v_x² = %s² - %s² = %s 이므로 v_y = %s m/s' % (num(v), num(vx), num(vy * vy), num(vy)), 'v_y = gt 에서 t = %s/10 = %s s' % (num(vy), num(t))],
                      core='연직 속도 성분은 v_y = gt 이고, 합속도는 v² = v_x² + v_y² 이다.', point='그림에서 연직 속도 성분을 구해 시간을 구한다.')
        if which == 'h':
            body = PP(base + '%s을(를) 던진 지점의 높이는? %s' % (ob, cond)) + FIG(fig, '56%')
            wr = wl(h, [vy, vy * vy / 10, vy * vy / 40, 5 * vy, vx * vx / 20, h * 2], 'm')
            return mc(body, ans(h, 'm'), wr, r=r, lv='상', fam='d',
                      steps=['v_y = √(v² - v_x²) = √(%s² - %s²) = %s m/s' % (num(v), num(vx), num(vy)), 'v_y² = 2gh 에서 h = %s²/20 = %s m' % (num(vy), num(h))],
                      core='연직 방향은 v_y² = 2gh 이다.', point='합속도와 수평 성분으로 연직 성분을 구한 뒤 높이를 구한다.')
        body = PP(base + '지면에 닿는 순간의 속력 v 는? %s' % cond) + FIG(fig, '56%')
        wr = wl(v, [vx + vy, vx, vy, abs(vx - vy), (vx + vy) / 2, v + 5], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하', fam='d',
                  steps=['v = √(v_x² + v_y²) = √(%s² + %s²) = %s m/s' % (num(vx), num(vy), num(v))],
                  core='수직인 두 속도 성분의 합속도는 피타고라스 정리로 구한다.', point='속도 성분을 합성한다.')
    if form == 'at45':
        v0 = r.choice([10, 15, 20, 25, 30]); t = v0 / 10; hh = 5 * t * t; xx = v0 * t
        body = PP('%s을(를) 수평 방향으로 %s의 속력으로 던졌다. 던진 순간부터 속도의 방향이 수평면과 45°를 이루는 순간까지 %s이(가) 낙하한 높이는? %s' % (ob, U(v0, 'm/s'), ob, cond))
        wr = wl(hh, [v0, xx, hh * 2, hh / 2, 5 * v0, v0 * v0 / 10 * 2], 'm')
        assert abs(hh - v0 ** 2 / 20) < 1e-9
        return mc(body, ans(hh, 'm'), wr, r=r, lv='상', fam='e',
                  steps=['45°일 때 v_y = v_x = v₀ = %s m/s' % num(v0), '이때 시각 t = v_y/g = %s s' % num(t), '낙하 높이 = ½gt² = 5 × %s² = %s m (또는 v_y²/2g = %s²/20)' % (num(t), num(hh), num(v0))],
                  core='속도가 수평면과 45°를 이루면 v_y = v_x 이다.', point='각도 조건을 속도 성분 사이의 관계로 바꾼다.')
    # vy
    t3 = r.choice([1, 2, 3, 4, 5]); v0 = r.choice([5, 10, 15, 20, 30])
    vyy = 10 * t3; vv = math.hypot(v0, vyy)
    body = PP('%s을(를) 수평 방향으로 %s의 속력으로 던졌다. 던진 지 %s 후 %s의 속도의 연직 성분의 크기는? %s' % (ob, U(v0, 'm/s'), U(t3, '초'), ob, cond))
    wr = wl(vyy, [v0, v0 + vyy, vv, 5 * t3, 5 * t3 * t3, vyy / 2], 'm/s')
    return mc(body, ans(vyy, 'm/s'), wr, r=r, lv='하', fam='e',
              steps=['수평 투사에서 연직 방향은 자유 낙하이므로 v_y = gt = 10 × %s = %s m/s' % (num(t3), num(vyy)), '(수평 성분 %s m/s 는 변하지 않는다.)' % num(v0)],
              core='수평 투사에서 연직 속도 성분은 v_y = gt 로 증가하고 수평 성분은 일정하다.', point='연직 성분은 처음 속력과 무관하다.')


# ================================================================ ph029
ANG_OK = [30, 37, 45, 53, 60]


def _vcands(th):
    """각도 th 에서 깔끔한 결과가 나오는 v0 후보."""
    if th in (37, 53): return [10, 15, 20, 25, 30, 40, 50]
    if th == 30: return [10, 20, 30, 40, 50]
    if th == 45: return [10, 20, 30, 40]
    return [10, 20, 30, 40]


@T('ph029')
def oblique_top(r, k):
    """비스듬히 던진 물체의 최고점과 체공 시간."""
    form = r.choice(['H', 'H', 'T', 'T', 'tt', 'vtop', 'revH', 'revT', 'figH', 'figT', 'vy_t', 'ret'])
    ob = r.choice(['공', '돌멩이', '야구공', '창'])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    trig = '(단, sin%d° = %s, cos%d° = %s 이고, ' 
    th = r.choice(ANG_OK); v0 = r.choice(_vcands(th))
    sn, cs = SIN[th], COS[th]
    vy0, vx0 = sn * v0, cs * v0
    Hq = Q(vy0.c * vy0.c * vy0.r / 20)             # 최고점 높이 v0²sin²/20 (유리수)
    Tq = vy0 * Fr(1, 5)                             # 체공 시간 2 v0 sinθ/g
    ttq = vy0 * Fr(1, 10)
    H = float(Hq); T_ = float(Tq); tt = float(ttq)
    assert abs(H - (float(vy0) ** 2) / 20) < 1e-9 and abs(T_ - 2 * tt) < 1e-9 and abs(H - (float(vy0) * tt - 5 * tt * tt)) < 1e-9
    note = '(단, sin%d° = %s, cos%d° = %s 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (th, SINS[th], th, COSS[th])
    if form == 'H':
        right = qs(Hq, 'm')
        if not right: return None
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 비스듬히 던졌다. 최고점의 지면으로부터의 높이는? %s' % (ob, th, U(v0, 'm/s'), note))
        wr = wlq(Hq, [Hq * 2, Hq * Fr(1, 2), vx0 * vx0 * Fr(1, 20) if True else None, Q(Fr(v0 * v0, 20)), Q(Fr(v0 * v0, 10)), Q(float_to_fr(float(vy0) / 10) if vy0.rational() else Fr(v0, 10)), Hq * 4], 'm')
        return mc(body, right, wr, r=r, lv='중', fam='a', sort='shuf' if False else 'num',
                  steps=['처음 속도의 연직 성분 v_y = v₀ sin%d° = %s × %s = %s m/s' % (th, num(v0), SINS[th], qs(vy0)), '최고점에서 연직 속도가 0이므로 H = v_y²/2g = (%s)²/20 = %s m' % (qs(vy0), qs(Hq))],
                  core='비스듬히 던진 물체의 최고점 높이는 H = (v₀ sinθ)²/2g 이다.', point='연직 성분만으로 최고점 높이를 구한다.')
    if form == 'T':
        right = qs(Tq, 's')
        if not right: return None
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 비스듬히 던졌다. 던진 순간부터 지면에 떨어질 때까지 걸리는 시간은? %s' % (ob, th, U(v0, 'm/s'), note))
        wr = wlq(Tq, [ttq, Tq * 2, vx0 * Fr(2, 10), Q(Fr(v0, 5)), Q(Fr(v0, 10)), Tq * Fr(1, 2) * 3, vy0 * Fr(1, 20)], 's')
        return mc(body, right, wr, r=r, lv='중', fam='a', sort='num',
                  steps=['연직 성분 v_y = v₀ sin%d° = %s m/s' % (th, qs(vy0)), '올라가는 데 걸리는 시간 t = v_y/g = %s s' % qs(ttq), '체공 시간 = 2t = %s s' % qs(Tq)],
                  core='체공 시간은 T = 2v₀ sinθ/g 이다(올라가는 시간의 2배).', point='연직 성분으로 올라가는 시간을 구한 뒤 2배 한다.')
    if form == 'tt':
        right = qs(ttq, 's')
        if not right: return None
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 비스듬히 던졌다. %s이(가) 최고점에 도달할 때까지 걸리는 시간은? %s' % (ob, th, U(v0, 'm/s'), ob, note))
        wr = wlq(ttq, [Tq, ttq * 2, Q(Fr(v0, 10)), Q(Fr(v0, 5)), vx0 * Fr(1, 10), ttq * Fr(1, 2), Q(Fr(v0, 20))], 's')
        return mc(body, right, wr, r=r, lv='하', fam='a', sort='num',
                  steps=['최고점에서 연직 속도가 0이므로 0 = v₀ sin%d° - gt' % th, 't = v₀ sin%d° / g = %s / 10 = %s s' % (th, qs(vy0), qs(ttq))],
                  core='최고점에서는 연직 속도가 0이므로 올라가는 시간은 t = v₀ sinθ / g 이다.', point='연직 속도가 0이 되는 시간을 구한다.')
    if form == 'vtop':
        right = qs(vx0, 'm/s')
        if not right: return None
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 비스듬히 던졌다. %s이(가) 최고점에 있을 때의 속력은? %s' % (ob, th, U(v0, 'm/s'), ob, note))
        wr = wlq(vx0, [vy0, Q(Fr(v0)), Q(0 + Fr(1)), vx0 * 2, vx0 * Fr(1, 2), vy0 + vx0 if False else None, Q(Fr(v0, 2))], 'm/s')
        return mc(body, right, wr, r=r, lv='하', fam='b', sort='num',
                  steps=['최고점에서 연직 속도는 0이고 수평 속도만 남는다.', '수평 속도는 일정하므로 v = v₀ cos%d° = %s × %s = %s m/s' % (th, num(v0), COSS[th], qs(vx0))],
                  core='최고점에서 속도는 수평 방향이며 크기는 v₀ cosθ 이다.', point='최고점의 속력은 0이 아니라 수평 성분이다.')
    if form == 'revH':
        if th in (30, 60, 45): 
            pass
        right = qs(Q(Fr(v0)), 'm/s')
        Hs = qs(Hq)
        if not Hs: return None
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 비스듬히 던졌더니 최고점의 높이가 %s이었다. %s을(를) 던진 속력은? %s' % (ob, th, U(float(Hq), 'm'), ob, note))
        wr = wl(v0, [math.sqrt(20 * float(Hq)), math.sqrt(20 * float(Hq)) * float(sn) if False else None, v0 * 2, v0 / 2, float(Hq) * 2, v0 + 10, v0 * float(cs)], 'm/s')
        return mc(body, ans(v0, 'm/s'), wr, r=r, lv='상', fam='c',
                  steps=['H = (v₀ sin%d°)²/2g 에서 (v₀ sin%d°)² = 20 × %s = %s' % (th, th, Hs, num(20 * float(Hq))), 'v₀ sin%d° = %s m/s 이고 sin%d° = %s 이므로 v₀ = %s m/s' % (th, qs(vy0), th, SINS[th], num(v0))],
                  core='최고점 높이로부터 연직 성분을 구한 뒤 각도로 처음 속력을 구한다.', point='H 로 v_y 를 구하고 sinθ 로 나눈다.')
    if form == 'revT':
        Ts = qs(Tq)
        if not Ts: return None
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 비스듬히 던졌더니 %s 후에 지면에 떨어졌다. %s을(를) 던진 속력은? %s' % (ob, th, U(T_, 's'), ob, note))
        wr = wl(v0, [5 * T_, 10 * T_, 5 * T_ * float(sn), 5 * T_ / float(cs), v0 * 2, v0 / 2, 10 * T_ * float(cs)], 'm/s')
        return mc(body, ans(v0, 'm/s'), wr, r=r, lv='상', fam='c',
                  steps=['올라가는 시간 = %s/2 = %s s 이므로 v_y = g × %s = %s m/s' % (num(T_), num(tt), num(tt), qs(vy0)), 'v₀ = v_y / sin%d° = %s / %s = %s m/s' % (th, qs(vy0), SINS[th], num(v0))],
                  core='체공 시간의 절반이 올라가는 시간이며, v_y = g × (올라가는 시간) 이다.', point='체공 시간으로 연직 성분을 구한 뒤 처음 속력을 구한다.')
    if form in ('figH', 'figT'):
        if form == 'figH':
            fig = traj_fig(th, 'v₀ = %s m/s' % num(v0), '%d°' % th, Hl='H')
            right = qs(Hq, 'm')
            if not right: return None
            body = PP('그림은 지면에서 %d°의 각으로 속력 %s로 던진 %s의 경로이다. 최고점의 높이 H 는? %s' % (th, U(v0, 'm/s'), ob, note)) + FIG(fig, '66%')
            wr = wlq(Hq, [Hq * 2, Hq * Fr(1, 2), Q(Fr(v0 * v0, 20)), Q(Fr(v0 * v0, 10)), Hq * 4, vx0 * vx0 * Fr(1, 20)], 'm')
            return mc(body, right, wr, r=r, lv='중', fam='d', sort='num',
                      steps=['v_y = v₀ sin%d° = %s m/s' % (th, qs(vy0)), 'H = v_y²/2g = %s m' % qs(Hq)],
                      core='최고점 높이 H = (v₀ sinθ)²/2g.', point='그림에서 주어진 값을 읽어 최고점 높이를 구한다.')
        fig = traj_fig(th, 'v₀ = %s m/s' % num(v0), '%d°' % th, Tl='T')
        right = qs(Tq, 's')
        if not right: return None
        body = PP('그림은 지면에서 %d°의 각으로 속력 %s로 던진 %s의 경로이다. 던져서 다시 지면에 닿을 때까지 걸린 시간 T 는? %s' % (th, U(v0, 'm/s'), ob, note)) + FIG(fig, '66%')
        wr = wlq(Tq, [ttq, Tq * 2, Q(Fr(v0, 5)), Q(Fr(v0, 10)), Tq * Fr(1, 2) * 3, vx0 * Fr(1, 5)], 's')
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='num',
                  steps=['v_y = v₀ sin%d° = %s m/s' % (th, qs(vy0)), 'T = 2v_y/g = 2 × %s / 10 = %s s' % (qs(vy0), qs(Tq))],
                  core='체공 시간 T = 2v₀ sinθ / g.', point='그림에서 주어진 값을 읽어 체공 시간을 구한다.')
    if form == 'vy_t':
        th2 = r.choice([37, 53]); v02 = r.choice([25, 50, 30, 40, 20]); vy = float(SIN[th2] * v02); vx = float(COS[th2] * v02)
        tm = r.choice([0.5, 1, 1.5, 2, 2.5, 3, 4, 5]); vyt = vy - 10 * tm
        if vyt == 0 or not two(vyt): return None
        note2 = '(단, sin%d° = %s, cos%d° = %s 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (th2, SINS[th2], th2, COSS[th2])
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 비스듬히 던졌다. 던진 지 %s 후 %s의 속도의 연직 성분의 크기와 방향을 옳게 짝지은 것은? %s' % (ob, th2, U(v02, 'm/s'), U(tm, '초'), ob, note2))
        d = '위쪽' if vyt > 0 else '아래쪽'; fd = '아래쪽' if vyt > 0 else '위쪽'
        right = '%s m/s, %s' % (num(abs(vyt)), d)
        wr = ['%s m/s, %s' % (num(abs(vyt)), fd), '%s m/s, %s' % (num(vy + 10 * tm), d), '%s m/s, %s' % (num(vx - 10 * tm) if vx - 10 * tm != abs(vyt) else '5', d), '%s m/s, %s' % (num(vy), d), '%s m/s, %s' % (num(abs(vyt) + 10), fd)]
        return mc(body, right, wr, r=r, lv='중', fam='e', sort='shuf',
                  steps=['v_y0 = v₀ sin%d° = %s × %s = %s m/s' % (th2, num(v02), SINS[th2], num(vy)), 'v_y = v_y0 - gt = %s - 10 × %s = %s m/s' % (num(vy), num(tm), num(vyt)), ('양수이므로 위쪽' if vyt > 0 else '음수이므로 아래쪽') + ', 크기는 %s m/s' % num(abs(vyt))],
                  core='연직 방향은 가속도 -g 의 등가속도 운동이므로 v_y = v₀ sinθ - gt 이다.', point='부호로 올라가는지 내려가는지 판단한다.')
    # ret : 같은 높이로 돌아올 때의 속력
    th2 = r.choice([37, 53]); v02 = r.choice([10, 20, 30, 40, 50]); tm2 = float(SIN[th2] * v02) / 10
    t_ = r.choice([1, 2, 3])
    if True:
        body = PP('지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 던졌다. 던진 높이로 다시 돌아와 지면에 닿는 순간 %s의 속력은? (단, 공기 저항은 무시한다.)' % (ob, th2, U(v02, 'm/s'), ob))
        wr = wl(v02, [v02 * float(COS[th2]), v02 * float(SIN[th2]), 2 * v02, v02 / 2, v02 + 10, v02 - 10, v02 * 1.2], 'm/s')
        return mc(body, ans(v02, 'm/s'), wr, r=r, lv='중', fam='f',
                  steps=['수평 속도는 v₀ cosθ 로 일정하고, 연직 속도는 크기가 같고 방향이 반대(-v₀ sinθ)가 된다.', '따라서 속력은 처음과 같은 %s m/s 이다.' % num(v02)],
                  core='같은 높이로 돌아오면 속력(운동 에너지)이 처음과 같다. 수평 성분은 같고 연직 성분은 방향만 반대이다.', point='같은 높이에서는 속력이 같음을 이용한다.')


def float_to_fr(x):
    return Fr(x).limit_denominator(1000)
