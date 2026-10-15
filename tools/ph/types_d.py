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
    fill = [right * 2, right / 2, right * 1.5, right * 0.75, right * 1.25, right * 3, right + 10, right - 5, right + 5, right * 0.9, right * 1.1, right + 3, right - 3, right + 1, right - 1, right + 2, right - 2]
    for c in list(cands) + fill:
        if c is None: continue
        c = round(c, 2)
        if nonneg and c <= 0: continue
        if right > 0 and (c < 0.2 * right or c > 12 * right): continue
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


def vec_fig(vx, vy, v, w=300, h=190):
    """착지 직전 속도 v 와 성분. 라벨은 문자열(값 또는 기호). 수평 오른쪽 vx, 아래 vy."""
    f = Fig(w, h)
    ox, oy = 30, 36
    sx, sy = 130, 110
    f.circ(ox, oy, 4, INK, INK, 1)
    f.line(ox, oy, ox + sx, oy, GR, 1.2, '4 3'); f.line(ox + sx, oy, ox + sx, oy + sy, GR, 1.2, '4 3')
    f.arrow(ox, oy, ox + sx - 3, oy, BL, 2.4)
    f.arrow(ox, oy, ox, oy + sy - 3, GN, 2.4) if False else None
    f.arrow(ox + sx, oy, ox + sx, oy + sy - 3, GN, 2.4)
    f.arrow(ox, oy, ox + sx - 3, oy + sy - 3, RD, 2.6)
    f.text(ox + sx / 2, oy - 8, vx, 13, bold=True, c=BL)
    f.text(ox + sx + 8, oy + sy / 2, vy, 13, 'start', True, GN)
    f.text(ox + sx / 2 - 36, oy + sy / 2 + 14, v, 13, 'start', True, RD)
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
    f.text(14, 18, v0l, 12.5, 'start', True, RD)
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


# ================================================================ ph030
SIN2 = {30: Q(Fr(1, 2), 3), 37: Q(Fr(24, 25)), 45: Q(1), 53: Q(Fr(24, 25)), 60: Q(Fr(1, 2), 3)}


def two_traj_fig(a1, a2, w=310, h=195):
    """같은 속력, 각도 a1, a2(=90-a1) 두 궤도. 사거리는 같다."""
    f = Fig(w, h)
    gy = h - 28; x0 = 30; R = 250
    f.hatch(14, gy, w - 28)
    for deg, c, nm in ((a1, BL, 'A'), (a2, RD, 'B')):
        H = min(R / 4 * math.tan(math.radians(deg)), 125)
        pts = [(x0 + R * u / 50, gy - 4 * H * (u / 50) * (1 - u / 50)) for u in range(51)]
        f.poly(pts, 'none', c, 2.2, close=False)
        f.text(x0 + R / 2 + 6, gy - H - 4, nm, 14, 'start', True, c, True)
        th = math.radians(deg)
        f.arrow(x0, gy, x0 + 44 * math.cos(th), gy - 44 * math.sin(th), c, 2)
        arc_label(f, x0, gy, 20 if deg < 45 else 30, deg, '%d°' % deg)
    f.circ(x0, gy, 4, INK, INK, 1)
    f.text(x0 + R / 2, gy + 20, '같은 속력 v₀ 로 던짐', 12, c=GR)
    return f.svg()


def ratio_str(a, b):
    a, b = Fr(a), Fr(b)
    q = a / b
    n, d = q.numerator, q.denominator
    return '%d : %d' % (n, d)


@T('ph030')
def oblique_range(r, k):
    """비스듬히 던진 물체의 수평 도달 거리."""
    form = r.choice(['R', 'R', 'R', 'pair', 'pair', 'ratio', 'fig_ratio', 'fig_ratio', 'fig_ratio', 'fig_ratio', 'rev', 'comp', 'sameang', 'sameang', 'maxang', 'maxang', 'maxR'])
    ob = r.choice(['공', '돌멩이', '창', '야구공'])
    th = r.choice(ANG_OK); v0 = r.choice([10, 15, 20, 25, 30, 40, 50])
    Rq = SIN2[th] * Fr(v0 * v0, 10)
    assert abs(float(Rq) - 2 * float(SIN[th]) * float(COS[th]) * v0 * v0 / 10) < 1e-9
    note = lambda t_: '(단, sin%d° = %s, cos%d° = %s 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (t_, SINS[t_], t_, COSS[t_])
    if form == 'R':
        right = qs(Rq, 'm')
        if not right: return None
        body = PP('평평한 지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 던졌다. %s이(가) 지면에 떨어질 때까지 수평으로 이동한 거리는? %s' % (ob, th, U(v0, 'm/s'), ob, note(th)))
        vx, vy = COS[th] * v0, SIN[th] * v0
        wr = wlq(Rq, [Q(Fr(v0 * v0, 10)), Rq * Fr(1, 2), Rq * 2, vx * vy * Fr(1, 10), vx * (vy * Fr(1, 10)), Q(Fr(v0 * v0, 20)), vx * Fr(1, 1) * 2], 'm')
        T_ = vy * Fr(1, 5)
        return mc(body, right, wr, r=r, lv='중', fam='a', sort='num',
                  steps=['v_x = v₀ cos%d° = %s m/s, v_y = v₀ sin%d° = %s m/s' % (th, qs(vx), th, qs(vy)), '체공 시간 T = 2v_y/g = %s s' % qs(T_), 'R = v_x T = %s × %s = %s m' % (qs(vx), qs(T_), qs(Rq)), '(R = v₀² sin2θ/g = %s²×%s/10 = %s m 로 확인)' % (num(v0), qs(SIN2[th]), qs(Rq))],
                  core='사거리 R = v₀² sin2θ / g = 2v_x v_y / g 이다.', point='수평 성분과 체공 시간의 곱으로 사거리를 구한다.')
    if form == 'rev':
        if th == 30 or th == 60: return None
        Rs = qs(Rq)
        if not Rs: return None
        body = PP('평평한 지면에서 %s을(를) 수평면과 %d°의 각으로 던졌더니 %s 떨어진 곳에 떨어졌다. %s을(를) 던진 속력은? %s' % (ob, th, U(float(Rq), 'm'), ob, note(th)))
        wr = wl(v0, [math.sqrt(10 * float(Rq)), math.sqrt(20 * float(Rq)), float(Rq) / 2, v0 * 2, v0 / 2, math.sqrt(float(Rq) * 10 * 0.96), v0 + 5], 'm/s')
        return mc(body, ans(v0, 'm/s'), wr, r=r, lv='상', fam='b',
                  steps=['R = v₀² sin2θ / g 에서 sin%d° = %s 이므로 sin2θ = 2 sin%d° cos%d° = %s' % (th, SINS[th], th, th, qs(SIN2[th])), 'v₀² = gR / sin2θ = 10 × %s / %s = %s' % (Rs, qs(SIN2[th]), num(v0 * v0)), 'v₀ = %s m/s' % num(v0)],
                  core='사거리 공식 R = v₀² sin2θ/g 를 거꾸로 풀어 처음 속력을 구한다.', point='sin2θ 의 값을 이용해 v₀² 를 구한다.')
    if form == 'pair':
        a1 = r.choice([37, 30]); a2 = 90 - a1
        kind = r.choice(['H', 'T', 'R'])
        s1, s2 = SIN[a1], SIN[a2]
        if kind == 'H':
            right = ratio_str((s1 * s1).c * (s1 * s1).r, (s2 * s2).c * (s2 * s2).r); nm = '최고점의 높이'
            core = '최고점의 높이는 sin²θ 에 비례한다.'; st = ['H ∝ v₀² sin²θ 이므로 H_A : H_B = sin²%d° : sin²%d° = %s : %s = %s' % (a1, a2, '(%s)²' % SINS[a1], '(%s)²' % SINS[a2], right)]
        elif kind == 'T':
            q = (s1.c * (1 if True else 0)) / (s2.c)
            if s1.r != s2.r:
                q = Fr(s1.c) / Fr(s2.c) / 1
                right = None
                # 근호 비
                right = ('%s : %s' % (SINS[a1], SINS[a2]))
            right = None
            # 정수비
            if s1.r == 1 and s2.r == 1: right = ratio_str(s1.c, s2.c)
            else: return None
            nm = '체공 시간'; core = '체공 시간은 sinθ 에 비례한다.'; st = ['T ∝ v₀ sinθ 이므로 T_A : T_B = sin%d° : sin%d° = %s : %s = %s' % (a1, a2, SINS[a1], SINS[a2], right)]
        else:
            right = '1 : 1'; nm = '수평 도달 거리'; core = '각도 θ 와 90°-θ 로 던진 사거리는 같다(sin2θ = sin(180°-2θ)).'
            st = ['R ∝ sin2θ 이고 sin%d° = sin%d° 이므로 R_A : R_B = 1 : 1' % (2 * a1, 2 * a2 if 2 * a2 <= 180 else 180)]
            st = ['R = v₀² sin2θ / g 이고 sin(2 × %d°) = sin(2 × %d°) = sin%d° 이다.' % (a1, a2, 2 * a1), '따라서 R_A : R_B = 1 : 1 이다.']
        body = PP('평평한 지면에서 같은 속력으로 %s을(를) 각각 수평면과 %d°(A), %d°(B)의 각으로 던졌다. 두 경우 %s의 비 A : B 는? (단, 공기 저항은 무시한다.)' % (ob, a1, a2, nm))
        opts = ['1 : 1', '3 : 4', '4 : 3', '9 : 16', '16 : 9', '1 : 2', '2 : 1', '3 : 5', '5 : 3']
        if a1 == 30: opts = ['1 : 1', '1 : 2', '2 : 1', '1 : 3', '3 : 1', '1 : 4', '4 : 1']
        wr = [o for o in opts if o != right]
        return mc(body, right, wr[:6], r=r, lv='중', fam='c', sort='shuf', steps=st, core=core, point='같은 속력일 때 각도에 따른 비를 구한다.')
    if form == 'maxR':
        a1 = r.choice([37, 53]); v = r.choice([10, 20, 25, 30, 40, 50]); R1 = 0.96 * v * v / 10; Rmax = v * v / 10
        if not two(R1) or not two(Rmax): return None
        body = PP('평평한 지면에서 %s을(를) 수평면과 %d°의 각으로 던졌더니 수평 도달 거리가 %s이었다. 같은 속력으로 던질 때 얻을 수 있는 수평 도달 거리의 최댓값은? (단, 공기 저항은 무시하고, sin%d° = %s, cos%d° = %s 이다.)' % (ob, a1, U(R1, 'm'), a1, SINS[a1], a1, COSS[a1]))
        wr = wl(Rmax, [R1, R1 * 2, R1 * 0.5, Rmax * 2, Rmax / 2, R1 / 0.96 * 1.2, R1 * 1.2], 'm')
        return mc(body, ans(Rmax, 'm'), wr, r=r, lv='상', fam='d',
                  steps=['R = v₀² sin2θ / g 이고 sin%d° = %s 이므로 v₀² sin2θ/g = %s m' % (2 * a1 if 2 * a1 <= 90 else 180 - 2 * a1, '24/25', num(R1)), '사거리 최대는 θ = 45°(sin90° = 1)일 때이다.', 'R_max = R / (24/25) = %s / 0.96 = %s m' % (num(R1), num(Rmax))],
                  core='같은 속력일 때 사거리는 θ = 45° 에서 최대이며 R_max = v₀²/g 이다.', point='sin2θ 의 값을 비교하여 최대 사거리를 구한다.')
    if form == 'ratio':
        a1 = r.choice([37, 45, 53]); v = r.choice([10, 20, 30]); n = r.choice([2, 3, 0.5, 1.5])
        R1 = float(SIN2[a1]) * v * v / 10; R2 = R1 * n * n
        if not two(R1) or not two(R2) or not two(v * n): return None
        body = PP('평평한 지면에서 %s을(를) 수평면과 %d°의 각으로 %s의 속력으로 던졌더니 수평 도달 거리가 %s이었다. 같은 각으로 속력을 %s로 던질 때의 수평 도달 거리는? (단, 공기 저항은 무시한다.)' % (ob, a1, U(v, 'm/s'), U(R1, 'm'), U(v * n, 'm/s')))
        wr = wl(R2, [R1 * n, R1 * n * 2, R1 * n * n * 2, R1 / n, R1 / (n * n), R1 * math.sqrt(n), R2 + 10], 'm')
        return mc(body, ans(R2, 'm'), wr, r=r, lv='중', fam='e',
                  steps=['R = v₀² sin2θ / g 이므로 각이 같으면 R ∝ v₀² 이다.', '속력이 %s배이므로 R 은 %s배 : %s × %s = %s m' % (num(n), num(n * n), num(R1), num(n * n), num(R2))],
                  core='각이 같으면 사거리는 처음 속력의 제곱에 비례한다.', point='속력이 n배이면 사거리는 n²배이다.')
    if form == 'fig_ratio':
        a1 = r.choice([30, 37]); a2 = 90 - a1
        fig = two_traj_fig(a1, a2)
        kind = r.choice(['H', 'R', 'T'])
        s1, s2 = SIN[a1], SIN[a2]
        if kind == 'R':
            body = PP('그림은 평평한 지면에서 같은 속력으로 던진 %s의 두 경로 A(%d°), B(%d°)를 나타낸 것이다. 수평 도달 거리의 비 R_A : R_B 는? (단, 공기 저항은 무시한다.)' % (ob, a1, a2)) + FIG(fig, '66%')
            right = '1 : 1'
            opts = ['1 : 1', '1 : 2', '2 : 1', '3 : 4', '4 : 3', '9 : 16', '16 : 9']
            return mc(body, right, [o for o in opts if o != right][:5], r=r, lv='중', fam='f', sort='shuf',
                      steps=['R = v₀² sin2θ / g 이고 sin%d° = sin%d° 이므로 R_A = R_B' % (2 * a1, 2 * a2 - 180 + 180 if False else 2 * a2), '비는 1 : 1 이다.'],
                      core='같은 속력으로 θ 와 90°-θ 로 던진 물체의 사거리는 같다.', point='보각 관계의 사거리가 같음을 이용한다.')
        if kind == 'H':
            if a1 == 37: ra, rb = '9 : 16', None
            else: ra = '1 : 3'
            body = PP('그림은 평평한 지면에서 같은 속력으로 던진 %s의 두 경로 A(%d°), B(%d°)를 나타낸 것이다. 최고점의 높이의 비 H_A : H_B 는? (단, 공기 저항은 무시한다.)' % (ob, a1, a2)) + FIG(fig, '66%')
            right = ra
            opts = ['1 : 1', '1 : 2', '1 : 3', '3 : 4', '4 : 3', '9 : 16', '16 : 9', '3 : 1']
            return mc(body, right, [o for o in opts if o != right][:5], r=r, lv='중', fam='f', sort='shuf',
                      steps=['H = (v₀ sinθ)²/2g ∝ sin²θ', 'H_A : H_B = sin²%d° : sin²%d° = (%s)² : (%s)² = %s' % (a1, a2, SINS[a1], SINS[a2], right)],
                      core='최고점의 높이는 sin²θ 에 비례한다.', point='각도에 따른 sin²θ 의 비를 구한다.')
        if a1 == 30: return None
        body = PP('그림은 평평한 지면에서 같은 속력으로 던진 %s의 두 경로 A(%d°), B(%d°)를 나타낸 것이다. 체공 시간의 비 T_A : T_B 는? (단, 공기 저항은 무시한다.)' % (ob, a1, a2)) + FIG(fig, '66%')
        right = '3 : 4'
        opts = ['1 : 1', '1 : 2', '4 : 3', '9 : 16', '16 : 9', '2 : 1']
        return mc(body, right, opts[:5], r=r, lv='중', fam='f', sort='shuf',
                  steps=['T = 2v₀ sinθ / g ∝ sinθ', 'T_A : T_B = sin37° : sin53° = 3/5 : 4/5 = 3 : 4'],
                  core='체공 시간은 sinθ 에 비례한다.', point='체공 시간이 수평 거리가 아니라 연직 성분으로 정해짐을 이해한다.')
    if form == 'comp':
        vx, vy, v = r.choice([(24, 10, 26), (15, 20, 25), (40, 30, 50), (30, 40, 50), (20, 15, 25), (12, 16, 20), (16, 12, 20), (9, 12, 15)])
        T_ = 2 * vy / 10; Rr = vx * T_
        if not two(T_) or not two(Rr): return None
        body = PP('평평한 지면에서 %s을(를) 비스듬히 던졌더니 %s 후에 던진 지점으로부터 수평으로 %s 떨어진 곳에 떨어졌다. %s을(를) 던진 속력은? (단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)' % (ob, U(T_, '초'), U(Rr, 'm'), ob))
        wr = wl(v, [vx + vy, vx, vy, Rr / T_ + 5 * T_, abs(vx - vy), (vx + vy) / 2, v + 5], 'm/s')
        assert abs(math.hypot(Rr / T_, 5 * T_) - v) < 1e-9
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='상', fam='g',
                  steps=['수평 속도 v_x = R/T = %s/%s = %s m/s' % (num(Rr), num(T_), num(vx)), '올라가는 시간 %s s 이므로 v_y = g × %s = %s m/s' % (num(T_ / 2), num(T_ / 2), num(vy)), 'v₀ = √(v_x² + v_y²) = √(%s² + %s²) = %s m/s' % (num(vx), num(vy), num(v))],
                  core='수평 성분은 R/T, 연직 성분은 gT/2 이며 처음 속력은 두 성분의 합성이다.', point='사거리와 체공 시간에서 두 성분을 구해 합성한다.')
    if form == 'sameang':
        a1 = r.choice([30, 37, 53, 60, 20, 25, 35, 40]); a2 = 90 - a1
        body = PP('평평한 지면에서 %s을(를) 같은 속력으로 수평면과 %d°의 각으로 던질 때와 같은 사거리를 얻으려면 수평면과 이루는 각을 몇 °로 해야 하는가? (단, 던지는 각 %d°가 아닌 다른 각이다.)' % (ob, a1, a1))
        wr = ['%d°' % a_ for a_ in (15, 30, 37, 45, 53, 60, 75, 20, 40, 25, 35, 50, 65, 70) if a_ not in (a2, a1)]
        return mc(body, '%d°' % a2, wr[:6], r=r, lv='하', fam='h', sort='shuf',
                  steps=['사거리 R ∝ sin2θ 이고 sin2θ = sin(180° - 2θ) 이므로 θ 와 90° - θ 에서 사거리가 같다.', '90° - %d° = %d°' % (a1, a2)],
                  core='같은 속력으로 θ 와 90°-θ 로 던진 물체는 사거리가 같다.', point='사거리가 같은 두 각은 서로 합이 90°이다.')
    body = PP('평평한 지면에서 같은 속력으로 %s을(를) 비스듬히 던질 때 수평 도달 거리가 가장 커지는 던지는 각(수평면과 이루는 각)은? (단, 공기 저항은 무시한다.)' % ob)
    return mc(body, '45°', ['15°', '30°', '37°', '53°', '60°', '75°', '90°'][:5] if False else ['30°', '37°', '53°', '60°', '90°'], r=r, lv='하', fam='h', sort='shuf',
              steps=['R = v₀² sin2θ / g 는 sin2θ = 1, 즉 2θ = 90° 일 때 최대이다.', '따라서 θ = 45° 이다.'],
              core='같은 속력일 때 사거리는 θ = 45° 에서 최대이다.', point='sin2θ 가 최대가 되는 각을 찾는다.')


# ================================================================ ph031 (<보기>)
def pts_fig(deg=45, labels=True, kind='oblique', w=310, h=200):
    """궤도 위에 점 P(출발), A(상승), B(최고점), C(하강, A 와 같은 높이), Q(착지)."""
    f = Fig(w, h)
    gy = h - 30; x0 = 30; R = 250
    H = min(R / 4 * math.tan(math.radians(deg)), 120)
    f.hatch(14, gy, w - 28)
    pts = [(x0 + R * u / 50, gy - 4 * H * (u / 50) * (1 - u / 50)) for u in range(51)]
    f.poly(pts, 'none', BL, 2.2, close=False, dash='5 3')
    def pos(u): return x0 + R * u, gy - 4 * H * u * (1 - u)
    for u, nm, dx, dy in ((0, 'P', -4, 18), (0.2, 'A', -16, -2), (0.5, 'B', 0, -12), (0.8, 'C', 12, -2), (1.0, 'Q', 4, 18)):
        x, y = pos(u)
        f.circ(x, y, 4.2, RD, INK, 1.2)
        f.text(x + dx, y + dy, nm, 14, bold=True, italic=True)
    xa, ya = pos(0.2); xc, yc = pos(0.8)
    f.line(xa, ya, xc, yc, GR, 1, '3 3')
    f.arrow(x0, gy, x0 + 36 * math.cos(math.radians(deg)), gy - 36 * math.sin(math.radians(deg)), RD, 2)
    return f.svg()


def horiz_pts_fig(w=300, h=200):
    f = Fig(w, h)
    gy = h - 24; top = 40; x0 = 40
    f.hatch(14, gy, w - 28)
    pts = [(x0 + 200 * u / 40, top + (gy - top - 6) * (u / 40) ** 2) for u in range(41)]
    f.poly(pts, 'none', BL, 2.2, close=False, dash='5 3')
    for u, nm, dx, dy in ((0, 'A', -10, 4), (0.5, 'B', -14, -4), (0.8, 'C', -14, -2), (1.0, 'D', 12, 4)):
        x = x0 + 200 * u; y = top + (gy - top - 6) * u * u
        f.circ(x, y, 4.2, RD, INK, 1.2); f.text(x + dx, y + dy, nm, 14, bold=True, italic=True)
    f.arrow(x0, top, x0 + 40, top, RD, 2)
    return f.svg()


OBL = [  # (문장, 참거짓, 풀이문, 그룹)
    ('B 에서 물체의 속력은 0이다.', False, '최고점 B 에서 연직 속도 성분만 0이고 수평 속도 성분은 남아 있으므로 속력은 0이 아니다.', 'topv'),
    ('B 에서 물체의 속도의 방향은 수평 방향이다.', True, '최고점에서는 연직 속도가 0이므로 속도는 수평 방향이다.', 'topv'),
    ('B 에서 물체의 가속도의 크기는 0이다.', False, '물체에는 항상 중력만 작용하므로 가속도는 B 에서도 g(연직 아래)이다.', 'topa'),
    ('물체의 가속도는 모든 지점에서 연직 아래 방향이고 크기가 같다.', True, '공기 저항이 없으므로 중력만 작용하여 가속도는 g 로 일정하다.', 'acc'),
    ('A 에서와 C 에서 물체의 속력은 같다.', True, 'A 와 C 는 높이가 같으므로 속력이 같다(수평 성분 같고 연직 성분의 크기 같음).', 'AC'),
    ('A 에서와 C 에서 물체의 속도는 같다.', False, 'A 와 C 에서 속력은 같지만 연직 속도 성분의 방향이 반대이므로 속도는 같지 않다.', 'AC'),
    ('P 에서 Q 까지 물체의 수평 방향 속도 성분은 일정하다.', True, '수평 방향으로는 힘이 작용하지 않으므로 등속 운동이다.', 'hor'),
    ('P 에서 B 까지 올라가는 동안 물체의 연직 방향 속도 성분의 크기는 감소한다.', True, '중력 가속도가 아래로 작용하므로 올라갈수록 연직 속도의 크기는 감소한다.', 'vy'),
    ('B 에서 Q 까지 내려가는 동안 물체의 속력은 계속 감소한다.', False, '내려가는 동안 연직 속도의 크기가 증가하므로 속력은 증가한다.', 'spd'),
    ('A 에서 B 까지 걸린 시간은 B 에서 C 까지 걸린 시간과 같다.', True, 'A 와 C 는 최고점 B 에 대해 대칭이므로 걸린 시간이 같다.', 'sym'),
    ('C 에서 물체의 가속도의 방향은 A 에서와 반대이다.', False, '가속도는 항상 연직 아래 방향이므로 A 에서와 같다.', 'acc'),
    ('B 에서 물체에 작용하는 알짜힘은 0이다.', False, '중력이 작용하므로 알짜힘은 0이 아니다.', 'topa'),
    ('물체의 속력은 B 에서 가장 작다.', True, '연직 속도가 0인 B 에서 속력이 최소이다.', 'spd'),
    ('Q 에서 속도의 연직 성분의 크기는 P 에서와 같다.', True, '같은 높이에서는 연직 속도 성분의 크기가 같다.', 'vy'),
    ('물체가 올라가는 동안 가속도의 방향은 위쪽이다.', False, '올라가는 동안에도 가속도는 연직 아래(중력 방향)이다.', 'acc'),
    ('A 에서 C 까지 평균 속도의 방향은 수평 방향이다.', True, 'A 와 C 는 같은 높이이므로 변위가 수평 방향이다.', 'avg'),
    ('B 에서 물체의 연직 방향 속도 성분은 0이다.', True, '최고점에서 올라가던 운동이 내려가는 운동으로 바뀌므로 연직 속도는 0이다.', 'topv'),
    ('수평 방향으로는 물체에 알짜힘이 작용하지 않는다.', True, '중력은 연직 아래로만 작용한다.', 'hor'),
    ('P 에서 Q 까지 걸린 시간은 연직 방향 운동만으로 결정된다.', True, '지면으로 돌아오는 때는 연직 방향 변위가 0이 되는 때이다.', 'time'),
    ('물체가 내려가는 동안 연직 속도 성분의 크기는 일정하다.', False, '가속도 g 로 연직 속도가 증가한다.', 'vy'),
]

HZ = [
    ('A 에서 D 까지 수평 방향 속도 성분은 일정하다.', True, '수평 방향으로는 알짜힘이 0이므로 등속이다.', 'hor'),
    ('A 에서 D 까지 연직 방향 속도 성분은 일정하다.', False, '연직 방향은 자유 낙하이므로 속도가 증가한다.', 'vy'),
    ('B 에서 D 로 갈수록 물체의 속력은 증가한다.', True, '수평 성분은 일정하고 연직 성분이 증가하므로 속력이 증가한다.', 'spd'),
    ('물체의 가속도는 A 에서 D 까지 크기와 방향이 변하지 않는다.', True, '중력만 작용하므로 가속도는 g(연직 아래)로 일정하다.', 'acc'),
    ('C 에서 가속도의 방향은 속도의 방향과 같다.', False, '가속도는 연직 아래이고 속도는 비스듬한 방향이므로 서로 같지 않다.', 'dir'),
    ('A 에서 물체의 속도의 방향은 수평 방향이다.', True, '수평으로 던졌으므로 처음 속도는 수평이다.', 'startv'),
    ('A 에서 물체의 가속도는 0이다.', False, '던지는 순간에도 중력 가속도 g 가 작용한다.', 'acc'),
    ('D 에서 속도의 방향은 수평 방향이다.', False, '연직 속도 성분이 있으므로 속도는 비스듬한 아래 방향이다.', 'startv'),
    ('A 에서 B 까지 걸린 시간은 B 에서 D 까지 걸린 시간과 같다.', True, '수평 방향은 등속이고 B 는 수평 거리의 중간 지점이므로 두 구간에 걸린 시간이 같다.', 'time'),
    ('물체가 날아가는 동안 연직 방향의 운동은 자유 낙하와 같다.', True, '연직 방향은 처음 속도가 0인 중력 가속도의 운동이다.', 'free'),
    ('물체에 작용하는 알짜힘은 운동 방향과 항상 같다.', False, '알짜힘(중력)은 연직 아래이고 운동 방향은 점점 아래로 기울 뿐 같지 않다.', 'dir'),
    ('수평 속력을 크게 하면 지면에 닿는 시간이 길어진다.', False, '낙하 시간은 높이로만 결정되므로 수평 속력과 무관하다.', 'time2'),
]


@T('ph031')
def proj_bogi(r, k):
    """포물선 운동에서 속도와 가속도(<보기>)."""
    form = r.choice(['fig_obl', 'fig_obl', 'fig_hz', 'fig_hz', 'fig_hz', 'fig_hz', 'text_obl', 'text_obl', 'text_hz'])
    if form == 'fig_obl' or form == 'text_obl':
        pool = OBL
    else:
        pool = HZ
    sel = r.sample(pool, 3)
    if len({s[3] for s in sel}) < 3: return None
    if form == 'fig_obl':
        deg = r.choice([30, 37, 45, 53, 60])
        fig = pts_fig(deg)
        intro = '그림은 지면의 점 P 에서 비스듬히 던져 올린 물체가 점 Q 에 떨어질 때까지의 경로를 나타낸 것이다. 점 B 는 최고점이고 A, C 는 높이가 같은 점이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)'
        return bogi(intro, [(s[0], s[1], s[2]) for s in sel], r=r, pre=FIG(fig, '66%'), ask='', lv='상', fam='a',
                    core='포물선 운동에서 수평 방향은 등속, 연직 방향은 가속도 g 의 등가속도 운동이며 최고점에서는 연직 속도만 0이다.', point='지점별 속도와 가속도의 방향·크기를 구분한다.')
    if form == 'fig_hz':
        fig = horiz_pts_fig()
        intro = '그림은 물체를 점 A 에서 수평 방향으로 던졌을 때 점 D 의 지면에 떨어질 때까지의 경로를 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)'
        return bogi(intro, [(s[0], s[1], s[2]) for s in sel], r=r, pre=FIG(fig, '60%'), ask='', lv='중', fam='b',
                    core='수평 투사에서 수평 방향은 등속 운동, 연직 방향은 자유 낙하이다.', point='수평 투사의 속도와 가속도를 성분별로 판단한다.')
    # 그림 없는 개념형: 지점 기호가 없는 문장만 사용
    if form == 'text_obl':
        intro = '비스듬히 던져 올린 물체의 운동에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)'
        txt = []
        for s in sel:
            t = s[0]
            for a, b in (('A 에서 C 까지', '같은 높이의 두 지점 사이'), ('A 에서와 C 에서', '올라갈 때와 내려올 때 같은 높이에서'), ('A 에서 B 까지 걸린 시간은 B 에서 C 까지 걸린 시간과', '최고점까지 올라가는 시간은 최고점에서 같은 높이로 내려오는 시간과'),
                         ('P 에서 Q 까지', '던진 순간부터 지면에 떨어질 때까지'), ('P 에서 B 까지', '던진 순간부터 최고점까지'), ('B 에서 Q 까지', '최고점에서 지면에 떨어질 때까지'),
                         ('Q 에서', '지면에 닿는 순간'), ('P 에서와', '던지는 순간과'), ('B 에서', '최고점에서'), ('C 에서', '내려오는 도중'), ('A 에서', '올라가는 도중')):
                t = t.replace(a, b)
            txt.append((t, s[1], s[2].replace('A 와 C', '같은 높이의 두 지점').replace('B 에서', '최고점에서').replace('B', '최고점').replace('A', '올라가는 점').replace('C', '내려오는 점'), s[3]))
        return bogi(intro, [(t[0], t[1], t[2]) for t in txt], r=r, ask='', lv='하', fam='c',
                    core='포물선 운동에서 수평 방향은 등속, 연직 방향은 가속도 g 의 등가속도 운동이다.', point='최고점의 속도·가속도와 대칭성을 정확히 안다.')
    intro = '수평으로 던진 물체의 운동에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)'
    txt = []
    for s in sel:
        t = s[0]
        for a, b in (('A 에서 D 까지', '던진 순간부터 지면에 닿을 때까지'), ('B 에서 D 로 갈수록', '날아가는 동안'), ('A 에서 B 까지 걸린 시간은 B 에서 D 까지 걸린 시간과 같다.', '수평 거리의 앞 절반을 가는 데 걸린 시간은 뒤 절반을 가는 데 걸린 시간과 같다.'), ('C 에서', '날아가는 도중'), ('A 에서', '던지는 순간'), ('D 에서', '지면에 닿는 순간')):
            t = t.replace(a, b)
        txt.append((t, s[1], s[2].replace('A 에서 B', '위쪽').replace('B 에서 D', '아래쪽'), s[3]))
    return bogi(intro, [(t[0], t[1], t[2]) for t in txt], r=r, ask='', lv='하', fam='d',
                core='수평 투사에서 수평 방향은 등속, 연직 방향은 자유 낙하이며 낙하 시간은 높이만으로 정해진다.', point='수평·연직 성분을 따로 판단한다.')


# ================================================================ ph032 (수평 투사와 자유 낙하 비교)
def strobe_fig(n=4, w=300, h=215, labelA='A', labelB='B'):
    """같은 높이에서 동시에 출발한 A(수평 투사)와 B(자유 낙하)의 일정한 시간 간격 위치."""
    f = Fig(w, h)
    top = 44; gy = h - 22; xb = 60
    f.hatch(14, gy, w - 28)
    for i in range(n + 1):
        u = i / n
        y = top + (gy - top - 8) * u * u
        xa = xb + 190 * u
        f.line(xb, y, xa, y, '#c9d1dc', 1, '4 3')
        f.circ(xa, y, 5, BL, INK, 1.2)
        f.circ(xb, y, 5, RD, INK, 1.2)
    f.text(xb - 16, top - 22, labelB, 14, bold=True, c=RD, italic=True)
    f.arrow(xb + 8, top - 20, xb + 44, top - 20, BL, 2)
    f.text(xb + 50, top - 16, labelA, 14, 'start', True, BL, True)
    f.text(xb - 16, top + 3, '', 12)
    return f.svg()


SM = [
    ('같은 높이에서 동시에 출발한 A 와 B 는 동시에 지면에 닿는다.', True, '낙하 시간은 연직 방향 운동(자유 낙하)으로만 정해지므로 같다.', 'time'),
    ('A 의 연직 방향 운동은 B 의 운동과 같다.', True, '수평으로 던진 물체도 연직 방향으로는 처음 속도 0인 자유 낙하를 한다.', 'vert'),
    ('A 는 수평 속도가 있으므로 B 보다 늦게 지면에 닿는다.', False, '낙하 시간은 수평 속도와 무관하므로 A 와 B 는 동시에 닿는다.', 'time'),
    ('수평 방향의 속력이 클수록 낙하 시간이 길어진다.', False, '낙하 시간은 높이로만 정해지며 수평 속력과 무관하다.', 'time2'),
    ('같은 시각에 A 와 B 의 연직 속도 성분의 크기는 같다.', True, '두 물체 모두 연직 방향으로 자유 낙하 하므로 같다.', 'vy'),
    ('지면에 닿는 순간 A 와 B 의 속력은 같다.', False, 'A 는 수평 속도 성분이 더 있으므로 속력이 B 보다 크다.', 'speed'),
    ('지면에 닿는 순간 A 의 속력은 B 의 속력보다 크다.', True, '연직 속도 성분은 같고 A 에는 수평 속도 성분이 더해진다.', 'speed'),
    ('같은 시각에 A 와 B 는 같은 높이에 있다.', True, '연직 방향 운동이 같으므로 같은 시각에 같은 높이이다.', 'height'),
    ('A 의 가속도의 크기는 B 의 가속도의 크기보다 크다.', False, '두 물체 모두 가속도는 중력 가속도 g 로 같다.', 'acc'),
    ('A 와 B 의 가속도는 크기와 방향이 같다.', True, '두 물체에는 모두 중력만 작용한다.', 'acc'),
    ('A 의 수평 방향 속도는 운동하는 동안 변하지 않는다.', True, '수평 방향으로는 힘이 작용하지 않는다.', 'hor'),
    ('B 에는 수평 방향의 알짜힘이 작용한다.', False, 'B 는 중력만 받으며 수평 방향의 힘은 없다.', 'hor'),
    ('질량이 서로 다르더라도 같은 높이에서 동시에 놓은 두 물체는 동시에 지면에 닿는다.', True, '공기 저항이 없으면 낙하 가속도는 질량과 무관하게 g 이다.', 'mass'),
    ('A 의 수평 속도를 2배로 하면 낙하 시간도 2배가 된다.', False, '낙하 시간은 수평 속도와 무관하다.', 'time2'),
    ('A 의 수평 속도를 2배로 하면 수평 도달 거리도 2배가 된다.', True, '낙하 시간이 같으므로 x = v₀t 는 v₀ 에 비례한다.', 'xr'),
    ('낙하하는 높이를 4배로 하면 낙하 시간은 2배가 된다.', True, 'h = ½gt² 이므로 t ∝ √h 이다.', 'hscale'),
    ('A 가 지면에 닿는 순간 연직 속도 성분의 크기는 B 보다 크다.', False, '두 물체의 연직 속도 성분의 크기는 같다.', 'vy'),
    ('B 가 지면에 닿는 순간 A 는 B 의 바로 옆 높이에 있다.', True, '두 물체의 높이가 같은 순간에 지면에 닿는다.', 'height'),
]


@T('ph032')
def horiz_vs_free(r, k):
    """수평 투사와 자유 낙하의 비교."""
    form = r.choice(['bogi_fig', 'bogi_fig', 'bogi', 'bogi', 'x', 'dist', 'speed', 'hratio', 'ratio_x', 'same_t', 'same_t', 'x'])
    ob1, ob2 = r.choice([('공 A', '공 B'), ('물체 A', '물체 B'), ('쇠구슬 A', '쇠구슬 B')])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    if form in ('bogi', 'bogi_fig'):
        sel = r.sample(SM, 3)
        if len({s[3] for s in sel}) < 3: return None
        if form == 'bogi_fig':
            n = r.choice([3, 4, 5])
            fig = strobe_fig(n)
            intro = '그림은 같은 높이에서 동시에 출발한 물체 A(수평으로 던짐)와 물체 B(가만히 놓음)의 위치를 일정한 시간 간격으로 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)'
            return bogi(intro, [(s[0], s[1], s[2]) for s in sel], r=r, pre=FIG(fig, '66%'), ask='', lv='중', fam='a',
                        core='수평으로 던진 물체와 자유 낙하하는 물체는 연직 방향 운동이 같아 같은 시각에 같은 높이에 있고 동시에 지면에 닿는다.', point='같은 높이의 점들을 이어 연직 운동이 같음을 읽는다.')
        intro = '같은 높이에서 동시에 물체 A 를 수평으로 던지고 물체 B 를 가만히 놓았다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)'
        return bogi(intro, [(s[0], s[1], s[2]) for s in sel], r=r, ask='', lv='중', fam='b',
                    core='수평 방향 운동은 연직 방향 운동에 영향을 주지 않는다. 낙하 시간은 높이만으로 정해진다.', point='수평 투사와 자유 낙하의 낙하 시간이 같음을 이해한다.')
    t = r.choice([1, 2, 3, 4, 5, 6]); h = 5 * t * t; v0 = r.choice([4, 5, 6, 8, 10, 12, 15, 20])
    if form == 'x':
        body = PP('높이 %s 에서 %s를 수평 방향으로 %s의 속력으로 던짐과 동시에 %s를 가만히 놓았다. %s가 지면에 닿는 순간 %s가 이동한 수평 거리는? %s' % (U(h, 'm'), ob1, U(v0, 'm/s'), ob2, ob2, ob1, cond))
        wr = wl(v0 * t, [v0 * t * 2, h, v0, v0 * t / 2, math.hypot(v0 * t, h), v0 * h / 10], 'm')
        return mc(body, ans(v0 * t, 'm'), wr, r=r, lv='중', fam='c',
                  steps=['B 의 낙하 시간 : h = ½gt² 에서 t = √(2 × %s/10) = %s s' % (num(h), num(t)), 'A 도 같은 시간 후 지면에 닿으므로 수평 거리 = v₀t = %s × %s = %s m' % (num(v0), num(t), num(v0 * t))],
                  core='수평 투사한 물체와 자유 낙하하는 물체의 낙하 시간은 같다.', point='자유 낙하 시간으로 수평 투사의 수평 거리를 구한다.')
    if form == 'dist':
        tm = r.choice([0.5, 1, 1.5, 2, 2.5, 3])
        if 5 * tm * tm >= h: return None
        body = PP('높이 %s 에서 %s를 수평 방향으로 %s의 속력으로 던짐과 동시에 %s를 가만히 놓았다. 출발한 지 %s 후 두 물체 사이의 거리는? (두 물체는 모두 아직 지면에 닿지 않았다.) %s' % (U(h, 'm'), ob1, U(v0, 'm/s'), ob2, U(tm, '초'), cond))
        d = v0 * tm
        wr = wl(d, [5 * tm * tm, math.hypot(v0 * tm, 5 * tm * tm), v0 * tm * 2, v0 + 10 * tm, v0 * tm + 5 * tm * tm, d + 5], 'm')
        return mc(body, ans(d, 'm'), wr, r=r, lv='중', fam='c',
                  steps=['두 물체의 연직 방향 운동이 같으므로 같은 시각에 같은 높이에 있다.', '따라서 두 물체 사이의 거리는 A 의 수평 이동 거리와 같다 : v₀t = %s × %s = %s m' % (num(v0), num(tm), num(d))],
                  core='같은 시각에 두 물체는 같은 높이에 있으므로 거리는 수평 이동 거리뿐이다.', point='연직 거리 차가 0임을 이용한다.')
    if form == 'speed':
        vx, vy, v = r.choice(TRI)
        hh = vy * vy / 20; tt = vy / 10
        body = PP('높이 %s 에서 %s를 수평 방향으로 %s의 속력으로 던짐과 동시에 %s를 가만히 놓았다. 두 물체가 지면에 닿는 순간의 속력의 비 v_A : v_B 는? %s' % (U(hh, 'm'), ob1, U(vx, 'm/s'), ob2, cond))
        g_ = math.gcd(v, vy); right = '%d : %d' % (v // g_, vy // g_)
        opts = ['%d : %d' % (a_ // math.gcd(a_, b_), b_ // math.gcd(a_, b_)) for a_, b_ in ((vy, v), (vx, vy), (vy, vx), (1, 1), (v, vx), (vx + vy, vy))]
        wr = [o for o in dict.fromkeys(opts) if o != right]
        return mc(body, right, wr, r=r, lv='상', fam='d', sort='shuf',
                  steps=['연직 속도 : v_y = √(2gh) = %s m/s (A, B 같음)' % num(vy), 'B 의 속력 v_B = %s m/s' % num(vy), 'A 의 속력 v_A = √(%s² + %s²) = %s m/s' % (num(vx), num(vy), num(v)), 'v_A : v_B = %s : %s = %s' % (num(v), num(vy), right)],
                  core='A 는 수평 성분이 더해져 합속도가 B 보다 크며 연직 성분은 같다.', point='연직 성분이 같음을 이용해 두 속력을 비교한다.')
    if form == 'hratio':
        n = r.choice([4, 9, 0.25]); h2 = h * n
        if not two(h2): return None
        tr = math.sqrt(n); 
        t2 = math.sqrt(2 * h2 / 10)
        if not two(t2): return None
        body = PP('높이 %s 에서 수평으로 %s의 속력으로 던진 물체 A 가 지면에 닿는 데 걸린 시간이 %s이다. 높이 %s 에서 같은 속력으로 수평으로 던진 물체 B 가 지면에 닿는 데 걸리는 시간은? %s' % (U(h, 'm'), U(v0, 'm/s'), U(t, '초'), U(h2, 'm'), cond))
        wr = wl(t2, [t * n, t * n * n, t / n, t / math.sqrt(n), t * 2, t + 1], 's')
        return mc(body, ans(t2, 's'), wr, r=r, lv='중', fam='e',
                  steps=['낙하 시간 t = √(2h/g) 이므로 t ∝ √h 이다.', '높이가 %s배이므로 시간은 %s배 : %s × %s = %s s' % (num(n), num(tr), num(t), num(tr), num(t2))],
                  core='낙하 시간은 높이의 제곱근에 비례하고 수평 속력과 무관하다.', point='높이 비로 낙하 시간 비를 구한다.')
    if form == 'same_t':
        body = PP('높이 %s 에서 물체 A 를 수평 방향으로 %s의 속력으로 던짐과 동시에 물체 B 를 가만히 놓았다. 물체 A 가 지면에 닿을 때까지 걸리는 시간은? %s' % (U(h, 'm'), U(v0, 'm/s'), cond))
        wr = wl(t, [h / v0, t + 1, t * 2, math.sqrt(h), h / 10, t - 1 if t > 1 else None], 's')
        return mc(body, ans(t, 's'), wr, r=r, lv='하', fam='f',
                  steps=['A 의 연직 방향 운동은 B 의 자유 낙하와 같다.', 'h = ½gt² 에서 %s = 5t² 이므로 t = %s s' % (num(h), num(t))],
                  core='수평 투사의 낙하 시간은 자유 낙하의 낙하 시간과 같다.', point='수평 속력은 낙하 시간에 영향을 주지 않는다.')
    # ratio_x
    v2 = v0 * r.choice([2, 3, 0.5]); h2 = h * r.choice([4, 9, 1])
    t2 = math.sqrt(2 * h2 / 10); x1 = v0 * t; x2 = v2 * t2
    if not two(x2) or not two(v2) or not two(t2) or not two(h2): return None
    body = PP('높이 %s 에서 수평으로 %s의 속력으로 던진 물체의 수평 도달 거리가 %s이다. 높이 %s 에서 수평으로 %s의 속력으로 던질 때의 수평 도달 거리는? %s' % (U(h, 'm'), U(v0, 'm/s'), U(x1, 'm'), U(h2, 'm'), U(v2, 'm/s'), cond))
    wr = wl(x2, [x1 * v2 / v0, x1 * h2 / h, x1 * (v2 / v0) * (h2 / h), x1 * (v2 / v0) ** 2, x2 + 10, x2 / 2], 'm')
    return mc(body, ans(x2, 'm'), wr, r=r, lv='상', fam='e',
              steps=['낙하 시간 t = √(2h/g) : %s s → %s s' % (num(t), num(t2)), 'x = v₀t = %s × %s = %s m' % (num(v2), num(t2), num(x2))],
              core='수평 도달 거리는 x = v₀t 이고 t 는 높이로 정해진다.', point='속력과 높이를 각각 반영해 낙하 시간과 수평 거리를 구한다.')


# ================================================================ ph033 (절벽·빗면에서 던진 물체)
def step_fig(h1, h2, v0l, xl, dl, w=310, h=205):
    """절벽 위(높이 h1)에서 수평으로 던져 아래 평지(높이 h2, 지면 기준)에 떨어진다."""
    f = Fig(w, h)
    gy = h - 28; top = 44; bx = 80
    lowy = gy - (gy - top) * h2 / h1 if h1 else gy
    f.hatch(14, gy, bx - 14)
    f.line(bx, top, bx, lowy, INK, 1.6); f.line(14, top, bx, top, INK, 1.6)
    f.poly([(14, top), (bx, top), (bx, gy), (14, gy)], '#eef2f7', INK, 1.6)
    f.poly([(bx, lowy), (w - 14, lowy), (w - 14, gy), (bx, gy)], '#eef2f7', INK, 1.6)
    ex = w - 46
    pts = [(bx + (ex - bx) * u / 40, top + (lowy - top) * (u / 40) ** 2) for u in range(41)]
    f.poly(pts, 'none', BL, 2.2, close=False, dash='5 3')
    f.circ(bx, top - 7, 6.5, RD, INK, 1.2); f.arrow(bx + 8, top - 7, bx + 50, top - 7, RD, 2.2)
    f.text(bx + 56, top - 12, v0l, 12.5, 'start', True, RD)
    f.circ(ex, lowy - 7, 6.5, RD, INK, 1.2)
    f.line(40, top, 40, lowy, GR, 1.2); f.line(34, top, 46, top, GR, 1.2); f.line(34, lowy, 46, lowy, GR, 1.2)
    f.text(48, (top + lowy) / 2 + 4, dl, 12.5, 'start', True)
    f.arrow(bx, lowy + 14, ex, lowy + 14, GR, 1.4); f.arrow(ex, lowy + 14, bx, lowy + 14, GR, 1.4)
    f.text((bx + ex) / 2, lowy + 28, xl, 13, bold=True)
    return f.svg()


def slope_fig(deg, v0l, w=300, h=210):
    th = math.radians(deg); tn = math.tan(th)
    f = Fig(w, h)
    x0, y0 = 34, 40
    xl = min(180, 150 / tn)
    xe, ye = x0 + xl, y0 + xl * tn
    f.poly([(x0, y0), (xe + 50, y0 + (xl + 50) * tn), (x0, y0 + (xl + 50) * tn)], '#eef2f7', INK, 1.6)
    pts = [(x0 + xl * u / 40, y0 + xl * tn * (u / 40) ** 2) for u in range(41)]
    f.poly(pts, 'none', BL, 2.2, close=False, dash='5 3')
    f.circ(x0, y0 - 7, 6.5, RD, INK, 1.2); f.arrow(x0 + 8, y0 - 7, x0 + 50, y0 - 7, RD, 2.2)
    f.text(x0 + 56, y0 - 12, v0l, 12.5, 'start', True, RD)
    f.circ(xe, ye - 7, 6.5, RD, INK, 1.2)
    f.line(x0, y0, x0 + 60, y0, GR, 1, '4 3')
    f.o.append('<path d="M %s %s A 30 30 0 0 1 %s %s" fill="none" stroke="%s" stroke-width="1.3"/>' % (Fig._n(x0 + 30 * math.cos(th) * 0 + 30), Fig._n(y0 + 0.0), Fig._n(x0 + 30 * math.cos(th)), Fig._n(y0 + 30 * math.sin(th)), GR) if False else '')
    f.text(x0 + 40, y0 + 22, '%d°' % deg, 13, 'start', True, GR)
    return f.svg()


TAN = {37: Fr(3, 4), 45: Fr(1), 53: Fr(4, 3)}
COSF = {37: Fr(4, 5), 45: None, 53: Fr(3, 5)}


@T('ph033')
def cliff_slope(r, k):
    """절벽·빗면에서 던진 물체."""
    form = r.choice(['diff', 'diff', 'step_x', 'step_x', 'step_v0', 'up', 'up', 'slope_t', 'slope_t', 'slope_x', 'slope_L', 'slope_v0', 'slope_h'])
    ob = r.choice(['공', '돌멩이', '야구공', '구슬'])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    if form in ('diff', 'step_x', 'step_v0'):
        d = r.choice([5, 20, 45, 80, 125]); t = math.sqrt(2 * d / 10)
        h1 = d + r.choice([0, 20, 40, 55, 80]); h2 = h1 - d
        v0 = r.choice([4, 5, 8, 10, 12, 15, 20])
        x = v0 * t
        if h2 == 0:
            fig = step_fig(h1, 0, 'v₀ = %s m/s' % num(v0), 'x = ?', 'h = %s m' % num(d)) if False else None
        if form == 'diff':
            body = PP('그림과 같이 지면으로부터 높이 %s인 평평한 언덕 위에서 %s을(를) 수평 방향으로 던졌더니 던진 지점보다 %s 낮은 평평한 지면에 떨어졌다. 던진 순간부터 떨어질 때까지 걸린 시간은? %s' % (U(h1, 'm'), ob, U(d, 'm'), cond)) if False else \
                PP('그림과 같이 높은 단 위에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌더니 던진 지점보다 %s 낮은 아래쪽 평지에 떨어졌다. 던진 순간부터 떨어질 때까지 걸린 시간은? %s' % (ob, U(v0, 'm/s'), U(d, 'm'), cond)) + FIG(step_fig(2 * d, d, 'v₀ = %s m/s' % num(v0), 'x', 'd = %s m' % num(d)), '56%')
            wr = wl(t, [d / v0, math.sqrt(d), d / 10, t + 1, t * 2, 2 * d / 10 * 2], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='하', fam='a',
                      steps=['낙하 거리는 던진 지점과 떨어진 지점의 높이 차 %s m 이다.' % num(d), 'd = ½gt² 에서 %s = 5t² 이므로 t = %s s' % (num(d), num(t))],
                      core='수평 투사한 물체의 낙하 시간은 던진 지점과 도달 지점의 높이 차로 결정된다.', point='지면이 아니라 도달한 평지까지의 높이 차를 쓴다.')
        fig = step_fig(h1 if h1 != d else 2 * d, h2 if h1 != d else d, 'v₀ = %s m/s' % num(v0), 'x' if form == 'step_x' else 'x = %s m' % num(x), 'd = %s m' % num(d))
        if form == 'step_x':
            body = PP('그림과 같이 높은 단 위의 끝에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌더니 던진 지점보다 %s 낮은 아래쪽 평지에 떨어졌다. 단의 벽으로부터 떨어진 지점까지의 수평 거리 x 는? %s' % (ob, U(v0, 'm/s'), U(d, 'm'), cond)) + FIG(fig, '56%')
            wr = wl(x, [v0 * math.sqrt(h1) if h1 != d else v0 * d / 10, v0 * math.sqrt(2 * h1 / 10), v0 * d / 10, x * 2, x / 2, x + v0, v0 * math.sqrt(d)], 'm')
            return mc(body, ans(x, 'm'), wr, r=r, lv='중', fam='a',
                      steps=['낙하 시간 : %s = ½ × 10 × t² 에서 t = %s s' % (num(d), num(t)), 'x = v₀t = %s × %s = %s m' % (num(v0), num(t), num(x))],
                      core='낙하 높이는 던진 지점과 도달 지점의 높이 차이며, x = v₀√(2d/g) 이다.', point='높이 차로 시간을 구한 뒤 수평 거리를 구한다.')
        body = PP('그림과 같이 높은 단 위의 끝에서 %s을(를) 수평 방향으로 던졌더니 던진 지점보다 %s 낮은 아래쪽 평지에서 단의 벽으로부터 %s 떨어진 곳에 떨어졌다. %s을(를) 던진 속력은? %s' % (ob, U(d, 'm'), U(x, 'm'), ob, cond)) + FIG(step_fig(2 * d, d, 'v₀', 'x = %s m' % num(x), 'd = %s m' % num(d)), '56%')
        wr = wl(v0, [x / d, x / math.sqrt(d), x / 2, x / (t + 1), x * t, v0 + 5], 'm/s')
        return mc(body, ans(v0, 'm/s'), wr, r=r, lv='중', fam='a',
                  steps=['낙하 시간 : %s = 5t² 에서 t = %s s' % (num(d), num(t)), 'v₀ = x/t = %s / %s = %s m/s' % (num(x), num(t), num(v0))],
                  core='x = v₀t, 낙차 d = ½gt² 를 연립한다.', point='높이 차로 시간을 구하고 속력을 구한다.')
    if form == 'up':
        vy = r.choice([20, 25, 30, 40, 50]); vx = r.choice([6, 8, 10, 12, 15, 20])
        ts = [x_ / 2 for x_ in range(1, 25) if vy / 10 < x_ / 2 < vy / 5 and half(x_ / 2)]
        if not ts: return None
        t = r.choice(ts); d = vy * t - 5 * t * t
        if d <= 0 or not two(d): return None
        x = vx * t
        assert abs(vy * t - 5 * t * t - d) < 1e-9
        body = PP('지면에서 %s을(를) 수평 방향 속력 %s, 연직 위 방향 속력 %s로 던졌다. %s이(가) 지면으로부터 높이 %s인 평평한 옥상에 내려오면서 도달했다. 던진 지점에서 옥상에 도달한 지점까지의 수평 거리는? (단, 옥상의 높이는 %s이고 %s)' % (ob, U(vx, 'm/s'), U(vy, 'm/s'), ob, U(d, 'm'), U(d, 'm'), cond[4:]))
        t_up = vy / 10
        wr = wl(x, [vx * t_up, vx * 2 * t_up, vx * t_up * 2 - vx, vx * (t + 1), vx * (t - 1), x * 2], 'm')
        return mc(body, ans(x, 'm'), wr, r=r, lv='상', fam='b',
                  steps=['연직 방향 : %s = %s t - 5t² 에서 5t² - %s t + %s = 0' % (num(d), num(vy), num(vy), num(d)), '내려오면서 도달하므로 큰 해 t = %s s (올라가면서 지나는 시각은 %s s)' % (num(t), num(vy / 5 - t)), '수평 거리 x = v_x t = %s × %s = %s m' % (num(vx), num(t), num(x))],
                  core='높이 d 인 옥상에 도달하는 시각은 연직 방향 식 d = v_y t - ½gt² 의 해이며, 내려오며 도달하면 큰 해를 택한다.', point='이차 방정식의 두 해 중 문제의 조건에 맞는 해를 고른다.')
    # 빗면
    deg = r.choice([37, 45, 53]); tn = TAN[deg]
    v0 = r.choice([5, 10, 15, 20, 25, 30]); t = 2 * v0 * float(tn) / 10
    if not two(t): return None
    x = v0 * t; y = 5 * t * t
    assert abs(y - x * float(tn)) < 1e-9
    note = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    fig = slope_fig(deg, 'v₀ = %s m/s' % num(v0) if form != 'slope_v0' else 'v₀')
    L = None
    if deg != 45: L = x / float(COSF[deg])
    if form == 'slope_t':
        body = PP('그림과 같이 경사각이 %d°인 매우 긴 빗면의 꼭대기에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 빗면에 떨어질 때까지 걸리는 시간은? (단, tan%d° = %s 이고, %s' % (deg, ob, U(v0, 'm/s'), ob, deg, {37: '3/4', 45: '1', 53: '4/3'}[deg], note[4:])) + FIG(fig, '60%')
        wr = wl(t, [v0 / 10, 2 * v0 / 10, 2 * v0 / 10 * float(tn) * 2, t + 1, 2 * v0 / 10 / float(tn) if float(tn) else None, t / 2, math.sqrt(2 * v0 / 10)], 's')
        return mc(body, ans(t, 's'), wr, r=r, lv='중', fam='c',
                  steps=['빗면에 떨어질 때 연직 낙하 거리와 수평 거리의 비가 tan%d° 이다 : ½gt² / (v₀t) = tan%d°' % (deg, deg), '5t² / (%s t) = %s 에서 t = 2 × %s × %s / 10 = %s s' % (num(v0), num(float(tn)), num(v0), num(float(tn)), num(t))],
                  core='수평 투사한 물체가 경사각 θ 의 빗면에 떨어지면 ½gt² / (v₀t) = tanθ 이므로 t = 2v₀ tanθ / g 이다.', point='낙하 거리와 수평 거리의 비가 tanθ 임을 이용한다.')
    if form == 'slope_x':
        body = PP('그림과 같이 경사각이 %d°인 매우 긴 빗면의 꼭대기에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 빗면에 닿는 순간까지 수평으로 이동한 거리는? (단, tan%d° = %s 이고, %s' % (deg, ob, U(v0, 'm/s'), ob, deg, {37: '3/4', 45: '1', 53: '4/3'}[deg], note[4:])) + FIG(fig, '60%')
        wr = wl(x, [y, v0 * t * float(tn), math.hypot(x, y), x * 2, x / 2, v0 * 2 * float(tn)], 'm')
        return mc(body, ans(x, 'm'), wr, r=r, lv='중', fam='c',
                  steps=['t = 2v₀ tan%d° / g = 2 × %s × %s / 10 = %s s' % (deg, num(v0), num(float(tn)), num(t)), 'x = v₀t = %s × %s = %s m' % (num(v0), num(t), num(x))],
                  core='빗면에 닿는 시각은 t = 2v₀ tanθ / g 이다.', point='빗면 도달 시각을 구한 뒤 수평 거리를 구한다.')
    if form == 'slope_L':
        if deg == 45: return None
        if not two(L): return None
        body = PP('그림과 같이 경사각이 %d°인 매우 긴 빗면의 꼭대기에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 떨어진 지점은 던진 지점으로부터 빗면을 따라 몇 m 떨어져 있는가? (단, sin%d° = %s, cos%d° = %s, tan%d° = %s 이고, %s' % (deg, ob, U(v0, 'm/s'), ob, deg, SINS[deg], deg, COSS[deg], deg, {37: '3/4', 53: '4/3'}[deg], note[4:])) + FIG(fig, '60%')
        wr = wl(L, [x, y, x + y, math.hypot(x, y) * 1.2, L / 2, x / float(SIN[deg]) if True else None, y / float(COSF[deg])], 'm')
        assert abs(L - math.hypot(x, y)) < 1e-9
        return mc(body, ans(L, 'm'), wr, r=r, lv='상', fam='d',
                  steps=['t = 2v₀ tanθ / g = %s s 이므로 수평 거리 x = %s m, 낙하 높이 y = ½gt² = %s m' % (num(t), num(x), num(y)), '빗면을 따라 이동한 거리 = x / cos%d° = %s / %s = %s m' % (deg, num(x), COSS[deg], num(L)), '(√(x² + y²) = √(%s² + %s²) = %s m 로 확인)' % (num(x), num(y), num(L))],
                  core='빗면을 따른 거리는 수평 거리 / cosθ = √(x² + y²) 이다.', point='수평·연직 이동 거리를 합성한다.')
    if form == 'slope_h':
        body = PP('그림과 같이 경사각이 %d°인 매우 긴 빗면의 꼭대기에서 %s을(를) 수평 방향으로 %s의 속력으로 던졌다. %s이(가) 빗면에 닿는 순간 던진 지점으로부터 연직 아래로 내려간 높이는? (단, tan%d° = %s 이고, %s' % (deg, ob, U(v0, 'm/s'), ob, deg, {37: '3/4', 45: '1', 53: '4/3'}[deg], note[4:])) + FIG(fig, '60%')
        wr = wl(y, [x, 5 * t, v0 * t * float(tn) * 2, y * 2, y / 2, x * float(tn) * 2], 'm')
        return mc(body, ans(y, 'm'), wr, r=r, lv='상', fam='d',
                  steps=['t = 2v₀ tanθ / g = %s s' % num(t), '낙하 높이 y = ½gt² = 5 × %s² = %s m (= x tanθ = %s × %s)' % (num(t), num(y), num(x), num(float(tn)))],
                  core='낙하 높이 y = ½gt² 이고 y = x tanθ 이다.', point='도달 시각을 구한 뒤 연직 낙하 거리를 구한다.')
    # slope_v0 : 걸린 시간 주어짐
    body = PP('그림과 같이 경사각이 %d°인 매우 긴 빗면의 꼭대기에서 %s을(를) 수평 방향으로 던졌더니 %s 후에 빗면에 떨어졌다. %s을(를) 던진 속력 v₀ 는? (단, tan%d° = %s 이고, %s' % (deg, ob, U(t, '초'), ob, deg, {37: '3/4', 45: '1', 53: '4/3'}[deg], note[4:])) + FIG(fig, '60%')
    wr = wl(v0, [5 * t, 10 * t, 5 * t / float(tn), 5 * t * float(tn), v0 * 2, v0 + 5, 10 * t * float(tn)], 'm/s')
    return mc(body, ans(v0, 'm/s'), wr, r=r, lv='상', fam='d',
              steps=['t = 2v₀ tan%d° / g 에서 v₀ = g t / (2 tan%d°)' % (deg, deg), 'v₀ = 10 × %s / (2 × %s) = %s m/s' % (num(t), num(float(tn)), num(v0))],
              core='빗면에 닿는 시각 t = 2v₀ tanθ / g 를 거꾸로 풀어 v₀ 를 구한다.', point='tanθ 조건식을 처음 속력에 대해 푼다.')


# ================================================================ ph034 (속도 벡터 그림)
def grid_panel(f, ox, oy, vx, vy, cols=7, up=4, down=3, cell=18, title='', color=RD, comp=True):
    """원점 (ox, oy) 에서 속도 벡터 (vx, vy)[칸 수]. 위쪽이 +. 격자 칸 수 cols × (up+down)."""
    for i in range(cols + 1):
        f.line(ox + i * cell, oy - up * cell, ox + i * cell, oy + down * cell, LG, 1)
    for j in range(-down, up + 1):
        f.line(ox, oy - j * cell, ox + cols * cell, oy - j * cell, LG, 1)
    f.line(ox, oy, ox + cols * cell, oy, '#aeb9c8', 1.2, '4 3')
    f.arrow(ox, oy, ox + vx * cell, oy - vy * cell, color, 2.6)
    f.circ(ox, oy, 3.4, INK, INK, 1)
    if comp:
        f.line(ox + vx * cell, oy, ox + vx * cell, oy - vy * cell, GR, 1, '3 3')
    f.text(ox + cols * cell / 2, oy - up * cell - 7, title, 12.5, bold=True)


@T('ph034')
def vec_grid(r, k):
    """속도 벡터 그림으로 구하는 포물선 운동."""
    form = r.choice(['one_H', 'one_T', 'one_R', 'two_t', 'two_dh', 'two_dx', 'land_h', 'land_t', 'land_x', 'speed', 'speed', 'speed', 'angle'])
    ob = r.choice(['공', '야구공', '돌멩이', '축구공'])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    u = r.choice([5, 10])
    if form.startswith('one'):
        vx = r.randint(2, 6); vy = r.randint(1, 4)
        f = Fig(200, 160); grid_panel(f, 30, 100, vx, vy, cols=7, up=4, down=2, title='처음 속도')
        vyr, vxr = vy * u, vx * u
        H = vyr ** 2 / 20; T_ = 2 * vyr / 10; R = vxr * T_
        if not (two(H) and two(T_) and two(R)): return None
        assert abs(R - 2 * vxr * vyr / 10) < 1e-9
        base = '그림은 평평한 지면에서 %s을(를) 비스듬히 던진 순간의 속도를 눈금 한 칸이 %s인 모눈종이에 나타낸 것이다. ' % (ob, U(u, 'm/s'))
        if form == 'one_H':
            body = PP(base + '%s이(가) 도달하는 최고점의 높이는? %s' % (ob, cond)) + FIG(f.svg(), '46%')
            wr = wl(H, [vyr ** 2 / 10, vyr / 10, H * 2, H / 2, math.hypot(vxr, vyr) ** 2 / 20, vxr ** 2 / 20], 'm')
            return mc(body, ans(H, 'm'), wr, r=r, lv='중', fam='a',
                      steps=['그림에서 연직 성분 %s칸 = %s m/s, 수평 성분 %s칸 = %s m/s' % (num(vy), num(vyr), num(vx), num(vxr)), 'H = v_y²/2g = %s²/20 = %s m' % (num(vyr), num(H))],
                      core='최고점의 높이는 연직 속도 성분만으로 정해진다: H = v_y²/2g.', point='격자에서 연직 성분을 읽어 최고점 높이를 구한다.')
        if form == 'one_T':
            body = PP(base + '%s이(가) 던져진 순간부터 지면에 다시 닿을 때까지 걸리는 시간은? %s' % (ob, cond)) + FIG(f.svg(), '46%')
            wr = wl(T_, [vyr / 10, vyr / 5 * 2, vxr / 5, T_ * 1.5, T_ / 2, math.hypot(vxr, vyr) / 5], 's')
            return mc(body, ans(T_, 's'), wr, r=r, lv='중', fam='a',
                      steps=['연직 성분 v_y = %s칸 × %s = %s m/s' % (num(vy), num(u), num(vyr)), 'T = 2v_y/g = 2 × %s / 10 = %s s' % (num(vyr), num(T_))],
                      core='체공 시간 T = 2v_y/g.', point='격자에서 연직 성분을 읽는다.')
        body = PP(base + '%s이(가) 지면에 닿는 지점까지의 수평 거리는? %s' % (ob, cond)) + FIG(f.svg(), '46%')
        wr = wl(R, [vxr * vyr / 10, vxr * vyr / 5 * 2, vxr * T_ / 2, vxr * vyr / 20, math.hypot(vxr, vyr) * T_, R * 2], 'm')
        return mc(body, ans(R, 'm'), wr, r=r, lv='중', fam='a',
                  steps=['v_x = %s m/s, v_y = %s m/s' % (num(vxr), num(vyr)), 'T = 2v_y/g = %s s' % num(T_), 'R = v_x T = %s × %s = %s m' % (num(vxr), num(T_), num(R))],
                  core='사거리 R = v_x × T = 2v_x v_y / g.', point='두 성분을 모두 읽어 체공 시간과 수평 거리를 구한다.')
    if form.startswith('two'):
        vx = r.randint(2, 6); vyA = r.randint(2, 4); vyB = r.choice([x_ for x_ in range(-2, vyA) if x_ != 0])
        if vyB < -2: return None
        f = Fig(340, 160)
        grid_panel(f, 14, 90, vx, vyA, cols=7, up=4, down=2, title='점 A', color=RD)
        grid_panel(f, 14 + 7 * 18 + 28, 90, vx, vyB, cols=7, up=4, down=2, title='점 B', color=BL)
        dvy = (vyA - vyB) * u; dt = dvy / 10; dh = ((vyA * u) ** 2 - (vyB * u) ** 2) / 20; dx = vx * u * dt
        if not (two(dt) and two(dh) and two(dx)) or dt <= 0: return None
        assert abs(dh - ((vyA * u) * dt - 5 * dt * dt)) < 1e-9
        base = '그림은 %s이(가) 포물선 경로를 따라 운동할 때 점 A, B 를 지나는 순간의 속도를 눈금 한 칸이 %s인 모눈종이에 나타낸 것이다(위쪽이 연직 위 방향). ' % (ob, U(u, 'm/s'))
        sol = ['A 의 연직 성분 v_yA = %s칸 × %s = %s m/s, B 의 연직 성분 v_yB = %s칸 × %s = %s m/s (수평 성분 %s m/s 는 같다)' % (num(vyA), num(u), num(vyA * u), num(vyB), num(u), num(vyB * u), num(vx * u))]
        if form == 'two_t':
            body = PP(base + '%s이(가) A 에서 B 까지 운동하는 데 걸린 시간은? %s' % (ob, cond)) + FIG(f.svg(), '70%')
            wr = wl(dt, [(vyA + vyB) * u / 10, abs(vyA * u) / 10, dt * 2, dt / 2, dvy / 5, vx * u / 10], 's')
            return mc(body, ans(dt, 's'), wr, r=r, lv='중', fam='b', steps=sol + ['Δv_y = g Δt 에서 Δt = (%s - (%s))/10 = %s s' % (num(vyA * u), num(vyB * u), num(dt))],
                      core='연직 속도 변화량은 가속도 g 와 시간의 곱이다: Δv_y = gΔt.', point='두 속도의 연직 성분 차로 시간을 구한다.')
        if form == 'two_dh':
            body = PP(base + 'A 와 B 의 높이 차는? %s' % cond) + FIG(f.svg(), '70%')
            wr = wl(dh, [(vyA * u - vyB * u) / 2, dh * 2, dh / 2, ((vyA - vyB) * u) ** 2 / 20 * 2, (vyA * u) * dt, abs(vyA ** 2 + vyB ** 2) * u * u / 20], 'm')
            return mc(body, ans(dh, 'm'), wr, r=r, lv='상', fam='b', steps=sol + ['v_yA² - v_yB² = 2g Δh 에서 Δh = (%s² - (%s)²)/20 = %s m' % (num(vyA * u), num(vyB * u), num(dh))],
                      core='연직 방향은 v_y² 가 2g × (높이 변화) 만큼 변한다.', point='연직 성분의 제곱의 차로 높이 차를 구한다.')
        body = PP(base + 'A 에서 B 까지 수평으로 이동한 거리는? %s' % cond) + FIG(f.svg(), '70%')
        wr = wl(dx, [vx * u * dvy / 10 * 2, vx * u, vx * u * (vyA * u) / 10, dx / 2, dx * 2, vx * u * dh / 5], 'm')
        return mc(body, ans(dx, 'm'), wr, r=r, lv='상', fam='b', steps=sol + ['걸린 시간 Δt = %s s' % num(dt), '수평 거리 = v_x Δt = %s × %s = %s m' % (num(vx * u), num(dt), num(dx))],
                  core='수평 방향은 등속이므로 Δx = v_x Δt 이다.', point='연직 성분으로 시간을 구한 뒤 수평 거리를 구한다.')
    if form.startswith('land'):
        vx = r.randint(2, 6); vy = r.randint(2, 5)
        f = Fig(200, 160); grid_panel(f, 30, 40, vx, -vy, cols=7, up=1, down=5, title='지면에 닿는 순간의 속도', color=RD)
        vxr, vyr = vx * u, vy * u; h = vyr ** 2 / 20; t = vyr / 10; x = vxr * t
        if not (two(h) and two(t) and two(x)): return None
        base = '그림은 높은 곳에서 수평으로 던진 %s이(가) 지면에 닿는 순간의 속도를 눈금 한 칸이 %s인 모눈종이에 나타낸 것이다(위쪽이 연직 위 방향). ' % (ob, U(u, 'm/s'))
        sol = ['수평 성분 %s칸 × %s = %s m/s, 연직 성분 %s칸 × %s = %s m/s' % (num(vx), num(u), num(vxr), num(vy), num(u), num(vyr))]
        if form == 'land_h':
            body = PP(base + '%s을(를) 던진 지점의 지면으로부터의 높이는? %s' % (ob, cond)) + FIG(f.svg(), '46%')
            wr = wl(h, [vyr ** 2 / 10, vyr / 10, h * 2, h / 2, vxr * t, math.hypot(vxr, vyr) ** 2 / 20], 'm')
            return mc(body, ans(h, 'm'), wr, r=r, lv='중', fam='c', steps=sol + ['v_y² = 2gh 에서 h = %s²/20 = %s m' % (num(vyr), num(h))],
                      core='수평 투사한 물체의 낙하 높이는 지면 도달 시 연직 속도로부터 h = v_y²/2g 이다.', point='격자에서 연직 성분을 읽어 높이를 구한다.')
        if form == 'land_t':
            body = PP(base + '%s을(를) 던진 순간부터 지면에 닿을 때까지 걸린 시간은? %s' % (ob, cond)) + FIG(f.svg(), '46%')
            wr = wl(t, [vyr / 5, vxr / 10, t * 2, t / 2, math.hypot(vxr, vyr) / 10, t + 1], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='중', fam='c', steps=sol + ['v_y = gt 에서 t = %s/10 = %s s' % (num(vyr), num(t))],
                      core='수평 투사에서 연직 속도 v_y = gt.', point='연직 성분으로 시간을 구한다.')
        body = PP(base + '%s을(를) 던진 지점의 바로 아래 지면으로부터 %s이(가) 떨어진 지점까지의 수평 거리는? %s' % (ob, ob, cond)) + FIG(f.svg(), '46%')
        wr = wl(x, [vxr * vyr / 10 * 2, vxr, vxr * t * 2, x / 2, vyr * t, h], 'm')
        return mc(body, ans(x, 'm'), wr, r=r, lv='중', fam='c', steps=sol + ['낙하 시간 t = v_y/g = %s s' % num(t), '수평 거리 x = v_x t = %s × %s = %s m' % (num(vxr), num(t), num(x))],
                  core='수평 속도는 일정하므로 x = v_x t 이다.', point='시간을 구한 뒤 수평 거리를 구한다.')
    if form == 'speed':
        a_, b_, c_ = r.choice([(3, 4, 5), (4, 3, 5), (6, 8, 10), (5, 12, 13), (8, 6, 10)])
        if a_ > 6 or b_ > 6: a_, b_, c_ = 3, 4, 5
        f = Fig(200, 170); grid_panel(f, 30, 120, a_, b_, cols=7, up=5, down=2, title='처음 속도')
        v = c_ * u
        body = PP('그림은 지면에서 비스듬히 던진 %s의 처음 속도를 눈금 한 칸이 %s인 모눈종이에 나타낸 것이다. %s의 처음 속력은?' % (ob, U(u, 'm/s'), ob)) + FIG(f.svg(), '46%')
        wr = wl(v, [(a_ + b_) * u, a_ * u, b_ * u, abs(a_ - b_) * u, (a_ + b_) * u / 2, v + u], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하', fam='d',
                  steps=['수평 성분 %s칸 = %s m/s, 연직 성분 %s칸 = %s m/s' % (num(a_), num(a_ * u), num(b_), num(b_ * u)), '속력 = √(%s² + %s²) = %s m/s' % (num(a_ * u), num(b_ * u), num(v))],
                  core='속도의 크기는 수평·연직 성분의 합성 √(v_x² + v_y²) 이다.', point='격자에서 성분을 읽어 피타고라스 정리로 합성한다.')
    # angle: 비 → 최고점 높이 같은 높이 비교
    vx = r.randint(2, 6); vy = r.randint(1, 4)
    vx2 = r.randint(2, 6); vy2 = r.randint(1, 4)
    if vy == vy2 or (vx, vy) == (vx2, vy2): return None
    f = Fig(340, 160)
    grid_panel(f, 14, 100, vx, vy, cols=7, up=4, down=2, title='물체 A', color=RD)
    grid_panel(f, 14 + 7 * 18 + 28, 100, vx2, vy2, cols=7, up=4, down=2, title='물체 B', color=BL)
    HA, HB = (vy * u) ** 2 / 20, (vy2 * u) ** 2 / 20
    g_ = math.gcd(vy * vy, vy2 * vy2); right = '%d : %d' % (vy * vy // g_, vy2 * vy2 // g_)
    body = PP('그림은 평평한 지면에서 비스듬히 던진 두 물체 A, B 의 처음 속도를 눈금 한 칸이 %s인 모눈종이에 나타낸 것이다. 두 물체가 도달하는 최고점의 높이의 비 H_A : H_B 는? (단, 공기 저항은 무시한다.)' % U(u, 'm/s')) + FIG(f.svg(), '70%')
    opts = ['%d : %d' % (a_ // math.gcd(a_, b_), b_ // math.gcd(a_, b_)) for a_, b_ in ((vy, vy2), (vx, vx2), (vy2 * vy2, vy * vy), (vx * vx, vx2 * vx2), (vy + vx, vy2 + vx2), (vy2, vy))]
    wr = [o for o in dict.fromkeys(opts) if o != right]
    return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf',
              steps=['최고점의 높이는 연직 성분만으로 정해진다: H = v_y²/2g ∝ v_y²', 'A 의 연직 성분 %s칸, B 의 연직 성분 %s칸이므로 H_A : H_B = %s² : %s² = %s' % (num(vy), num(vy2), num(vy), num(vy2), right)],
              core='최고점의 높이는 연직 속도 성분의 제곱에 비례한다.', point='수평 성분은 높이와 무관하다는 점에 유의한다.')
