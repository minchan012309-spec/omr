# -*- coding: utf-8 -*-
"""Ⅰ-E 등속 원운동 (ph035~ph041) 생성기."""
from phlib import *
import math, re as _re
from fractions import Fraction as Fr

G = 10
PI = 3  # 문제에서 π = 3 으로 준다


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


def tstr(x):
    q = Fr(x).limit_denominator(30)
    d = q.denominator
    while d % 2 == 0: d //= 2
    while d % 5 == 0: d //= 5
    if d == 1: return num(float(q))
    return '%d/%d' % (q.numerator, q.denominator)


def rstr(a, b):
    q = Fr(a).limit_denominator(1000) / Fr(b).limit_denominator(1000)
    return '%d : %d' % (q.numerator, q.denominator)


def ratio_opts(right, extra):
    opts = []
    for e in extra:
        if e != right and e not in opts: opts.append(e)
    for e in ('1 : 1', '1 : 2', '2 : 1', '1 : 4', '4 : 1', '1 : 3', '3 : 1', '2 : 3', '3 : 2', '1 : 8', '8 : 1', '4 : 3', '3 : 4'):
        if e != right and e not in opts: opts.append(e)
    return opts[:8]


# ---------------------------------------------------------------- 그림
def scene(theta=30, ccw=True, rl=None, vl=None, al=None, Fl=None, pname=None, w=240, h=215, R=74, objc=RD, show_path=True):
    """원운동 그림. 물체는 중심 O 에서 각 theta(도) 위치. 속도 접선(ccw 이면 반시계 방향), 구심 방향 화살표."""
    f = Fig(w, h)
    cx, cy = w / 2, h / 2 + 2
    f.circ(cx, cy, R, 'none', GR, 1.4, '5 3')
    f.circ(cx, cy, 3, INK, INK, 1)
    f.text(cx - 9, cy + 16, 'O', 13, bold=True, italic=True)
    th = math.radians(theta)
    px, py = cx + R * math.cos(th), cy - R * math.sin(th)
    f.line(cx, cy, px, py, GR, 1.3)
    if rl:
        mx, my = (cx + px) / 2, (cy + py) / 2
        f.text(mx + 15 * math.sin(th), my + 15 * math.cos(th) + 4, rl, 13, 'middle', True)
    s = 1 if ccw else -1
    tx, ty = -math.sin(th) * s, -math.cos(th) * s  # 화면 좌표 방향
    if vl is not None:
        f.arrow(px, py, px + 44 * tx, py + 44 * ty, RD, 2.4)
        lx = min(max(px + 58 * tx, 52), w - 52); ly = py + 56 * ty + 4
        f.text(lx, ly, vl, 13, 'middle', True, RD, True)
    if al is not None:
        ux, uy = (cx - px) / R, (cy - py) / R
        f.arrow(px, py, px + 38 * ux, py + 38 * uy, BL, 2.4)
        f.text(px + 50 * ux, py + 50 * uy + 4, al, 13, 'middle', True, BL, True)
    f.circ(px, py, 7, objc, INK, 1.3)
    if pname:
        f.text(px + 13 * math.cos(th), py - 13 * math.sin(th) + 5, pname, 13, 'middle', True)
    return f


def disk_fig(rA, rB, w=250, h=200):
    """회전 원판 위 두 점 A, B (중심에서 rA, rB 칸)."""
    f = Fig(w, h)
    cx, cy = 90, 100
    f.circ(cx, cy, 80, '#eef2f7', INK, 1.6)
    f.circ(cx, cy, 3, INK, INK, 1)
    f.line(cx, cy, cx + 78, cy, GR, 1.2, '4 3')
    ua = 78 * rA / max(rA, rB); ub = 78 * rB / max(rA, rB)
    for u_, nm, c in ((ua, 'A', BL), (ub, 'B', RD)):
        f.circ(cx + u_, cy, 6, c, INK, 1.2)
        f.text(cx + u_, cy - 12, nm, 13.5, bold=True, c=c, italic=True)
    f.text(cx - 10, cy + 16, 'O', 13, bold=True, italic=True)
    f.text(cx + 100, cy + 6, '(회전 원판)', 12, 'start', c=GR)
    return f.svg()


# ================================================================ ph035
@T('ph035')
def circ_basic(r, k):
    """주기·진동수·속력·각속도의 관계."""
    form = r.choice(['T_f', 'N', 'v', 'omega', 'vw', 'rr', 'T_v', 'ratio_disk', 'clock', 'rpm', 'fig_v', 'belt', 'belt', 'rpm_v'])
    cond = '(단, π = 3 으로 계산한다.)'
    ob = r.choice(['물체', '공', '장난감 자동차', '인공위성 모형'])
    if form == 'T_f':
        f = r.choice([0.25, 0.5, 2, 4, 5, 10, 20, 0.2, 1.25, 0.1, 8, 50])
        T_ = 1 / f
        if r.random() < .5:
            body = PP('등속 원운동하는 %s의 진동수(회전수)가 %s일 때 주기는?' % (ob, U(f, 'Hz')))
            wr = wl(T_, [f, 2 * f, T_ * 2, T_ / 2, f / 2, 1 / (2 * f)], 's')
            return mc(body, ans(T_, 's'), wr, r=r, lv='하', fam='a', steps=['주기 T = 1/f = 1/%s = %s s' % (num(f), num(T_))],
                      core='주기와 진동수는 서로 역수 관계이다: T = 1/f.', point='진동수를 주기로 바꾼다.')
        body = PP('등속 원운동하는 %s의 주기가 %s일 때 진동수(1초 동안의 회전수)는?' % (ob, U(T_, 's')))
        wr = wl(f, [T_, 2 * f, f / 2, 2 * f / 3, 1 / (2 * T_), f + 1], 'Hz')
        return mc(body, ans(f, 'Hz'), wr, r=r, lv='하', fam='a', steps=['진동수 f = 1/T = 1/%s = %s Hz' % (num(T_), num(f))],
                  core='주기와 진동수는 서로 역수 관계이다: f = 1/T.', point='주기를 진동수로 바꾼다.')
    if form == 'N':
        N = r.choice([5, 8, 10, 12, 15, 20, 30, 40, 60]); t = r.choice([2, 4, 5, 6, 10, 20, 30, 60])
        T_ = t / N
        if not two(T_): return None
        body = PP('등속 원운동하는 %s이(가) %s 동안 %d회 회전하였다. 이 %s의 주기는?' % (ob, U(t, '초'), N, ob))
        wr = wl(T_, [N / t, t * N, T_ * 2, T_ / 2, t / (N + 1), t - N], 's')
        return mc(body, ans(T_, 's'), wr, r=r, lv='하', fam='a', steps=['1회전하는 데 걸리는 시간이 주기이다.', 'T = %s s / %d = %s s' % (num(t), N, num(T_))],
                  core='주기 = (걸린 시간)/(회전수) 이다.', point='회전수와 시간으로 주기를 구한다.')
    if form == 'v':
        rr = r.choice([0.5, 1, 1.5, 2, 3, 4, 5, 10]); T_ = r.choice([1, 2, 3, 4, 5, 6, 10, 12])
        v = 2 * PI * rr / T_
        if not two(v): return None
        body = PP('반지름이 %s인 원 위를 주기 %s로 등속 원운동하는 %s의 속력은? %s' % (U(rr, 'm'), U(T_, 's'), ob, cond))
        wr = wl(v, [PI * rr / T_, 2 * PI * rr * T_, 2 * rr / T_, 2 * PI * T_ / rr if rr else None, v * 2, 4 * PI * rr / T_ * 0.5 * 2], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하', fam='b',
                  steps=['한 바퀴 도는 거리는 2πr 이고 걸리는 시간이 주기 T 이다.', 'v = 2πr/T = 2 × 3 × %s / %s = %s m/s' % (num(rr), num(T_), num(v))],
                  core='등속 원운동의 속력은 v = 2πr/T 이다.', point='원둘레를 주기로 나눈다.')
    if form == 'omega':
        T_ = r.choice([1, 2, 3, 4, 5, 6, 10, 12]); w_ = 2 * PI / T_
        if not two(w_): return None
        if r.random() < .5:
            body = PP('주기가 %s인 등속 원운동의 각속도는? %s' % (U(T_, 's'), cond))
            wr = wl(w_, [PI / T_, 2 * PI * T_, T_ / (2 * PI), 1 / T_, w_ * 2, 4 * PI / T_ * 0.5 * 0.5], 'rad/s')
            return mc(body, ans(w_, 'rad/s'), wr, r=r, lv='하', fam='c', steps=['각속도 ω = 2π/T = 2 × 3 / %s = %s rad/s' % (num(T_), num(w_))],
                      core='각속도는 단위 시간 동안 회전한 각으로 ω = 2π/T 이다.', point='주기로 각속도를 구한다.')
        f = 1 / T_
        body = PP('진동수가 %s인 등속 원운동의 각속도는? %s' % (U(f, 'Hz'), cond))
        wr = wl(w_, [PI * f, 2 * PI / f, f, w_ * 2, w_ / 2, 2 * f], 'rad/s')
        return mc(body, ans(w_, 'rad/s'), wr, r=r, lv='하', fam='c', steps=['각속도 ω = 2πf = 2 × 3 × %s = %s rad/s' % (num(f), num(w_))],
                  core='각속도는 ω = 2πf 이다.', point='진동수로 각속도를 구한다.')
    if form == 'vw':
        w_ = r.choice([0.5, 1, 1.5, 2, 3, 4, 5, 6]); rr = r.choice([0.5, 1, 2, 3, 4, 5, 10])
        v = w_ * rr
        if not two(v): return None
        body = PP('반지름 %s인 원 위를 각속도 %s로 등속 원운동하는 %s의 속력은?' % (U(rr, 'm'), U(w_, 'rad/s'), ob))
        wr = wl(v, [w_ / rr, rr / w_, w_ * rr * rr, w_ * w_ * rr, v * 2 * PI, 2 * PI * rr], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하', fam='c', steps=['v = rω = %s × %s = %s m/s' % (num(rr), num(w_), num(v))],
                  core='등속 원운동에서 v = rω 이다.', point='반지름과 각속도의 곱이 속력이다.')
    if form == 'rr':
        T_ = r.choice([2, 3, 4, 5, 6, 10]); rr = r.choice([1, 2, 3, 4, 5, 6, 10]); v = 2 * PI * rr / T_
        if not two(v): return None
        body = PP('등속 원운동하는 %s의 속력이 %s이고 주기가 %s일 때 원의 반지름은? %s' % (ob, U(v, 'm/s'), U(T_, 's'), cond))
        wr = wl(rr, [v * T_, v * T_ / PI, v * T_ / 2, v / T_, v * T_ * 2 / PI, v * T_ / (4 * PI)], 'm')
        return mc(body, ans(rr, 'm'), wr, r=r, lv='중', fam='b', steps=['v = 2πr/T 에서 r = vT/2π', 'r = %s × %s / (2 × 3) = %s m' % (num(v), num(T_), num(rr))],
                  core='v = 2πr/T 를 변형하여 반지름 r = vT/2π 를 구한다.', point='식을 변형해 반지름을 구한다.')
    if form == 'T_v':
        rr = r.choice([1, 2, 3, 4, 5, 6, 10]); v = r.choice([1, 2, 3, 4, 5, 6, 12]); T_ = 2 * PI * rr / v
        if not two(T_): return None
        body = PP('반지름 %s인 원 위를 %s의 속력으로 등속 원운동하는 %s의 주기는? %s' % (U(rr, 'm'), U(v, 'm/s'), ob, cond))
        wr = wl(T_, [rr / v, PI * rr / v, 2 * PI * v / rr, v / (2 * PI * rr), 2 * rr / v, T_ * 2], 's')
        return mc(body, ans(T_, 's'), wr, r=r, lv='중', fam='b', steps=['T = 2πr/v = 2 × 3 × %s / %s = %s s' % (num(rr), num(v), num(T_))],
                  core='주기 T = 2πr/v.', point='속력과 반지름으로 주기를 구한다.')
    if form == 'ratio_disk':
        a_, b_ = r.choice([(1, 2), (1, 3), (2, 3), (1, 4), (2, 4), (3, 4)])
        fig = disk_fig(a_, b_)
        ask = r.choice(['v', 'w', 'T'])
        if ask == 'v':
            right = rstr(a_, b_); nm = '속력의 비 v_A : v_B'
            st = ['같은 원판 위의 점은 각속도(주기)가 같다.', 'v = rω 이므로 v_A : v_B = r_A : r_B = %d : %d = %s' % (a_, b_, right)]
        elif ask == 'w':
            right = '1 : 1'; nm = '각속도의 비 ω_A : ω_B'
            st = ['같은 원판 위의 점은 같은 시간에 같은 각만큼 회전하므로 각속도가 같다.', 'ω_A : ω_B = 1 : 1']
        else:
            right = '1 : 1'; nm = '주기의 비 T_A : T_B'
            st = ['같은 원판 위의 점은 한 바퀴 도는 데 걸리는 시간이 같다.', 'T_A : T_B = 1 : 1']
        body = PP('그림은 일정한 각속도로 회전하는 원판 위의 두 점 A, B 를 나타낸 것이다. 중심 O 에서 A, B 까지의 거리는 각각 %s, %s이다. A, B 의 %s는?' % (U(a_, 'cm'), U(b_, 'cm'), nm)) + FIG(fig, '60%')
        wr = ratio_opts(right, [rstr(b_, a_), rstr(a_ * a_, b_ * b_), rstr(b_ * b_, a_ * a_)])
        return mc(body, right, wr[:6], r=r, lv='중', fam='d', sort='shuf', steps=st,
                  core='강체처럼 회전하는 원판 위의 점들은 각속도와 주기가 같고, 속력은 반지름에 비례한다.', point='각속도가 같을 때 v ∝ r 임을 이용한다.')
    if form == 'clock':
        hand = r.choice(['초침', '분침', '시침'])
        L = r.choice([10, 12, 15, 20, 24, 30])
        T_ = {'초침': 60, '분침': 3600, '시침': 43200}[hand]
        v = 2 * PI * L / T_
        if not two(v) or v <= 0: return None
        if hand == '시침' and v < 0.005: return None
        body = PP('길이가 %s인 시계의 %s 끝 점의 속력은? (단, π = 3 으로 계산한다.)' % (U(L, 'cm'), hand))
        wr = wl(v, [v * 60, v / 60, v * 2, v / 2, PI * L / T_ * 2 * 10, L / T_ * 10], 'cm/s')
        wr = [w for w in wr if not w.startswith('0 ')]
        return mc(body, ans(v, 'cm/s'), wr, r=r, lv='중', fam='e',
                  steps=['%s 은 한 바퀴를 도는 데 %s초가 걸린다 (주기 %s s).' % (hand, num(T_), num(T_)), 'v = 2πr/T = 2 × 3 × %s / %s = %s cm/s' % (num(L), num(T_), num(v))],
                  core='시계 바늘 끝의 속력은 v = 2πL/T 이다.', point='바늘의 주기를 알아 속력을 구한다.')
    if form == 'rpm':
        n = r.choice([30, 60, 90, 120, 150, 180, 240, 300]); rr = r.choice([0.2, 0.5, 1, 2])
        T_ = 60 / n; v = 2 * PI * rr / T_
        if not two(v) or not two(T_): return None
        body = PP('반지름 %s인 원판이 1분에 %d회 일정하게 회전한다. 원판 가장자리 한 점의 속력은? %s' % (U(rr, 'm'), n, cond))
        wr = wl(v, [v / 60, v * 60, 2 * PI * rr * n, PI * rr / T_, v * 2, v / 2], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='e',
                  steps=['1분(60초)에 %d회 회전하므로 주기 T = 60/%d = %s s' % (n, n, num(T_)), 'v = 2πr/T = 2 × 3 × %s / %s = %s m/s' % (num(rr), num(T_), num(v))],
                  core='분당 회전수로부터 주기를 구한 뒤 v = 2πr/T 를 쓴다.', point='단위(분 → 초)를 바꾸어 주기를 구한다.')
    if form == 'belt':
        rA, rB = r.choice([(1, 2), (1, 3), (2, 3), (1, 4), (2, 5), (3, 4), (2, 1), (3, 1), (4, 1)])
        TA = r.choice([1, 2, 3, 4, 6, 12]); TB = TA * rB / rA
        if not two(TB): return None
        f = Fig(300, 150)
        RA, RB = 26 * rA, 26 * rB
        ca, cb = (RA + 18, 80), (RA + 18 + RA + RB + 40, 80)
        f.circ(ca[0], ca[1], RA, '#eef2f7', INK, 1.6); f.circ(cb[0], cb[1], RB, '#eef2f7', INK, 1.6)
        f.line(ca[0], ca[1] - RA, cb[0], cb[1] - RB, GR, 2.4); f.line(ca[0], ca[1] + RA, cb[0], cb[1] + RB, GR, 2.4)
        for c_, nm in ((ca, 'A'), (cb, 'B')):
            f.circ(c_[0], c_[1], 3, INK, INK, 1); f.text(c_[0], c_[1] + 18, nm, 13.5, bold=True, italic=True)
        f.text(ca[0], 144, 'r_A = %s cm' % num(rA), 12.5, bold=True, c=BL); f.text(cb[0], 144, 'r_B = %s cm' % num(rB), 12.5, bold=True, c=RD)
        body = PP('그림은 벨트로 연결된 두 바퀴 A, B 를 나타낸 것이다. 벨트는 미끄러지지 않으며 A 의 반지름은 %s, B 의 반지름은 %s이다. A 가 %s의 주기로 회전할 때 B 의 주기는?' % (U(rA, 'cm'), U(rB, 'cm'), U(TA, 's'))) + FIG(f.svg(), '70%')
        wr = wl(TB, [TA * rA / rB, TA, TA * rB * rB / (rA * rA), TA * rA * rA / (rB * rB), TB * 2, TB + 1], 's')
        return mc(body, ans(TB, 's'), wr, r=r, lv='상', fam='g',
                  steps=['벨트로 연결된 두 바퀴의 가장자리 속력은 같다 : v_A = v_B', '2πr_A/T_A = 2πr_B/T_B 에서 T_B = T_A × r_B/r_A = %s × %s/%s = %s s' % (num(TA), num(rB), num(rA), num(TB))],
                  core='벨트로 연결된 두 바퀴는 가장자리의 속력이 같고, 주기는 반지름에 비례한다.', point='속력이 같은 조건에서 주기를 비교한다.')
    if form == 'rpm_v':
        v = r.choice([1, 2, 3, 4, 5, 6, 10, 12, 15, 30]); rr = r.choice([0.5, 1, 2, 3, 5, 10]); T_ = 2 * PI * rr / v
        n = 60 / T_
        if not two(n) or not half(n) or n <= 0: return None
        body = PP('반지름 %s인 원 위를 %s의 속력으로 등속 원운동하는 %s이 1분 동안 회전하는 횟수는? (단, π = 3 으로 계산한다.)' % (U(rr, 'm'), U(v, 'm/s'), ob))
        wr = wl(n, [n / 60, n * 60, 60 * v / rr, 30 * v / rr * 2 / PI, T_, n * 2], '회')
        return mc(body, ans(n, '회'), wr, r=r, lv='상', fam='h',
                  steps=['주기 T = 2πr/v = 2 × 3 × %s / %s = %s s' % (num(rr), num(v), num(T_)), '1분 = 60초 동안의 회전수 = 60/T = 60/%s = %s 회' % (num(T_), num(n))],
                  core='회전수 = (걸린 시간)/(주기) 이다.', point='속력 → 주기 → 회전수의 순서로 구한다.')
    # fig_v
    rr = r.choice([1, 2, 3, 4, 5]); T_ = r.choice([1, 2, 3, 4, 6, 12]); v = 2 * PI * rr / T_
    if not two(v): return None
    f = scene(30, True, 'r = %s m' % num(rr), None, None)
    f.text(120, 205, '주기 T = %s s' % num(T_), 13, bold=True, c=GR)
    body = PP('그림은 반지름 %s인 원 위를 일정한 속력으로 도는 %s을(를) 나타낸 것이다. 주기가 %s일 때 %s의 속력은? %s' % (U(rr, 'm'), ob, U(T_, 's'), ob, cond)) + FIG(f.svg(), '60%')
    wr = wl(v, [PI * rr / T_, 2 * PI * rr * T_, rr / T_, v * 2, v / 2, 2 * rr / T_], 'm/s')
    return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='f',
              steps=['v = 2πr/T = 2 × 3 × %s / %s = %s m/s' % (num(rr), num(T_), num(v))],
              core='등속 원운동의 속력은 v = 2πr/T 이다.', point='그림에서 반지름을 읽어 속력을 구한다.')


# ================================================================ ph036
@T('ph036')
def centripetal_acc(r, k):
    """구심 가속도의 크기."""
    form = r.choice(['a_vr', 'a_vr', 'a_wr', 'a_Tr', 'ratio_v', 'ratio_r', 'find_v', 'find_r', 'disk', 'graph', 'graph', 'fig_a'])
    ob = r.choice(['물체', '자동차', '공', '장난감 기차'])
    cond = '(단, π = 3 으로 계산한다.)'
    if form == 'a_vr':
        v = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20]); rr = r.choice([1, 2, 4, 5, 8, 10, 20, 25, 50])
        a = v * v / rr
        if not two(a): return None
        body = PP('반지름 %s인 원 위를 %s의 일정한 속력으로 운동하는 %s의 구심 가속도의 크기는?' % (U(rr, 'm'), U(v, 'm/s'), ob))
        wr = wl(a, [v * v * rr, v / rr, v * v / (2 * rr), 2 * v * v / rr, v * rr, v * v / (rr * rr)], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='하', fam='a', steps=['a = v²/r = %s² / %s = %s m/s²' % (num(v), num(rr), num(a))],
                  core='구심 가속도의 크기는 a = v²/r 이며 원의 중심을 향한다.', point='속력과 반지름으로 구심 가속도를 구한다.')
    if form == 'a_wr':
        w_ = r.choice([0.5, 1, 2, 3, 4, 5, 6]); rr = r.choice([0.5, 1, 2, 3, 4, 5, 10]); a = w_ * w_ * rr
        if not two(a): return None
        body = PP('반지름 %s인 원 위를 각속도 %s로 등속 원운동하는 %s의 구심 가속도의 크기는?' % (U(rr, 'm'), U(w_, 'rad/s'), ob))
        wr = wl(a, [w_ * rr, w_ * w_ / rr, w_ * rr * rr, 2 * w_ * rr, a * 2, a / 2], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='하', fam='a', steps=['a = rω² = %s × %s² = %s m/s²' % (num(rr), num(w_), num(a))],
                  core='구심 가속도의 크기는 a = rω² 이다.', point='각속도를 제곱하는 것에 주의한다.')
    if form == 'a_Tr':
        T_ = r.choice([1, 2, 3, 4, 5, 6, 10]); rr = r.choice([0.25, 0.5, 1, 2, 3, 4, 5, 10]); a = 4 * PI * PI * rr / T_ ** 2
        if not two(a): return None
        body = PP('반지름 %s인 원 위를 주기 %s로 등속 원운동하는 %s의 구심 가속도의 크기는? %s' % (U(rr, 'm'), U(T_, 's'), ob, cond))
        wr = wl(a, [2 * PI * rr / T_, 2 * PI * rr / T_ ** 2, 4 * PI * rr / T_, a * 2, a / 2, 4 * PI * PI * rr / T_], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='중', fam='b',
                  steps=['ω = 2π/T = 6/%s = %s rad/s' % (num(T_), num(6 / T_)), 'a = rω² = %s × %s² = %s m/s²' % (num(rr), num(6 / T_), num(a)), '(또는 a = 4π²r/T² = 36 × %s / %s² = %s m/s²)' % (num(rr), num(T_), num(a))],
                  core='구심 가속도는 a = 4π²r/T² 이다.', point='주기를 각속도로 바꾼 뒤 a = rω² 를 쓴다.')
    if form == 'ratio_v':
        n = r.choice([2, 3, 0.5, 4]); rr = r.choice([2, 4, 5, 10]); v = r.choice([4, 6, 8, 10])
        a1 = v * v / rr; a2 = a1 * n * n
        if not two(a1) or not two(a2): return None
        body = PP('반지름이 %s인 원 위를 %s의 속력으로 등속 원운동하는 %s의 구심 가속도의 크기가 %s이다. 반지름은 같고 속력이 %s가 되면 구심 가속도의 크기는?' % (U(rr, 'm'), U(v, 'm/s'), ob, U(a1, 'm/s²'), U(v * n, 'm/s')))
        wr = wl(a2, [a1 * n, a1 / n, a1 / (n * n), a1 * n * 2, a1 * 2, a1 + n], 'm/s²')
        return mc(body, ans(a2, 'm/s²'), wr, r=r, lv='중', fam='c', steps=['a = v²/r 이므로 반지름이 같으면 a ∝ v² 이다.', '속력이 %s배이므로 a 는 %s배 : %s × %s = %s m/s²' % (num(n), num(n * n), num(a1), num(n * n), num(a2))],
                  core='반지름이 같으면 구심 가속도는 속력의 제곱에 비례한다.', point='속력이 n배이면 구심 가속도는 n²배이다.')
    if form == 'ratio_r':
        n = r.choice([2, 3, 4]); w_ = r.choice([1, 2, 3]); rr = r.choice([1, 2, 3]); mode = r.choice(['w', 'v'])
        if mode == 'w':
            a1 = w_ * w_ * rr; a2 = a1 * n
            body = PP('각속도 %s로 등속 원운동하는 %s의 반지름이 %s이고 구심 가속도의 크기가 %s이다. 각속도는 그대로이고 반지름이 %s가 되면 구심 가속도의 크기는?' % (U(w_, 'rad/s'), ob, U(rr, 'm'), U(a1, 'm/s²'), U(rr * n, 'm')))
            wr = wl(a2, [a1 * n * n, a1 / n, a1 / (n * n), a1 + n, a1 * 2, a1 * 3], 'm/s²')
            return mc(body, ans(a2, 'm/s²'), wr, r=r, lv='중', fam='c', steps=['각속도가 같으면 a = rω² 에서 a ∝ r 이다.', '반지름이 %d배이므로 a = %s × %d = %s m/s²' % (n, num(a1), n, num(a2))],
                      core='각속도가 일정하면 구심 가속도는 반지름에 비례한다.', point='각속도가 같을 때와 속력이 같을 때를 구분한다.')
        v = r.choice([4, 6, 8, 12]); rr2 = r.choice([2, 3, 4, 6]); a1 = v * v / rr2; a2 = a1 / n
        if not two(a1) or not two(a2): return None
        body = PP('속력 %s로 등속 원운동하는 %s의 반지름이 %s이고 구심 가속도의 크기가 %s이다. 속력은 그대로이고 반지름이 %s가 되면 구심 가속도의 크기는?' % (U(v, 'm/s'), ob, U(rr2, 'm'), U(a1, 'm/s²'), U(rr2 * n, 'm')))
        wr = wl(a2, [a1 * n, a1 / (n * n), a1 * n * n, a1 + n, a1 / 2 if n != 2 else a1 / 3, a1 / 5], 'm/s²')
        return mc(body, ans(a2, 'm/s²'), wr, r=r, lv='중', fam='c', steps=['속력이 같으면 a = v²/r 에서 a ∝ 1/r 이다.', '반지름이 %d배이므로 a = %s / %d = %s m/s²' % (n, num(a1), n, num(a2))],
                  core='속력이 일정하면 구심 가속도는 반지름에 반비례한다.', point='속력이 같을 때 a ∝ 1/r 이다.')
    if form == 'find_v':
        v = r.choice([2, 3, 4, 5, 6, 8, 10]); rr = r.choice([2, 3, 4, 5, 8, 10, 20]); a = v * v / rr
        if not two(a): return None
        body = PP('반지름 %s인 원 위를 등속 원운동하는 %s의 구심 가속도의 크기가 %s일 때 %s의 속력은?' % (U(rr, 'm'), ob, U(a, 'm/s²'), ob))
        wr = wl(v, [a * rr, a / rr, math.sqrt(a / rr), a * rr / 2, math.sqrt(a * rr) * 2, v + 1], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='d', steps=['a = v²/r 에서 v² = ar = %s × %s = %s' % (num(a), num(rr), num(a * rr)), 'v = %s m/s' % num(v)],
                  core='v = √(ar) 이다.', point='제곱근을 취하는 것을 잊지 않는다.')
    if form == 'find_r':
        v = r.choice([4, 6, 8, 10, 12, 20]); a = r.choice([1, 2, 4, 5, 8, 10, 16]); rr = v * v / a
        if not two(rr): return None
        body = PP('속력 %s로 등속 원운동하는 %s의 구심 가속도의 크기가 %s일 때 원의 반지름은?' % (U(v, 'm/s'), ob, U(a, 'm/s²')))
        wr = wl(rr, [v / a, v * v * a, a * v, v * v / (2 * a), rr * 2, rr / 2], 'm')
        return mc(body, ans(rr, 'm'), wr, r=r, lv='중', fam='d', steps=['a = v²/r 에서 r = v²/a = %s² / %s = %s m' % (num(v), num(a), num(rr))],
                  core='r = v²/a 이다.', point='구심 가속도 식을 변형해 반지름을 구한다.')
    if form == 'disk':
        a_, b_ = r.choice([(1, 2), (1, 3), (2, 3), (1, 4)])
        mode = r.choice(['w', 'v'])
        fig = disk_fig(a_, b_) if mode == 'w' else None
        if mode == 'w':
            body = PP('그림은 일정한 각속도로 회전하는 원판 위의 두 점 A, B 를 나타낸 것이다. 중심 O 에서 A, B 까지의 거리는 각각 %s, %s이다. A, B 의 구심 가속도의 크기의 비 a_A : a_B 는?' % (U(a_, 'cm'), U(b_, 'cm'))) + FIG(fig, '60%')
            right = rstr(a_, b_)
            wr = ratio_opts(right, [rstr(b_, a_), rstr(a_ * a_, b_ * b_), rstr(b_ * b_, a_ * a_)])
            return mc(body, right, wr[:6], r=r, lv='중', fam='e', sort='shuf', steps=['각속도가 같으므로 a = rω² 에서 a ∝ r 이다.', 'a_A : a_B = r_A : r_B = %d : %d = %s' % (a_, b_, right)],
                      core='각속도가 같으면 구심 가속도는 반지름에 비례한다.', point='각속도가 같을 때 a ∝ r.')
        body = PP('두 물체 A, B 가 같은 속력으로 각각 반지름 %s, %s인 원 위를 등속 원운동한다. A, B 의 구심 가속도의 크기의 비 a_A : a_B 는?' % (U(a_, 'm'), U(b_, 'm')))
        right = rstr(b_, a_)
        wr = ratio_opts(right, [rstr(a_, b_), rstr(a_ * a_, b_ * b_), rstr(b_ * b_, a_ * a_)])
        return mc(body, right, wr[:6], r=r, lv='중', fam='e', sort='shuf', steps=['속력이 같으므로 a = v²/r 에서 a ∝ 1/r 이다.', 'a_A : a_B = 1/%d : 1/%d = %s' % (a_, b_, right)],
                  core='속력이 같으면 구심 가속도는 반지름에 반비례한다.', point='속력이 같을 때 a ∝ 1/r.')
    if form == 'graph':
        w_ = r.choice([1, 2, 3, 4]); rm = r.choice([2, 3, 4, 5]); am = w_ * w_ * rm
        if am > 40: return None
        p = Plot(280, 190, rm * 1.25, am * 1.25, ml=48, mr=18, mt=16, mb=40)
        ypx = (190 - 16 - 30) / (am * 1.25); xpx = (280 - 48 - 18) / (rm * 1.25)
        p.axes('r(m)', 'a(m/s²)', [rm], [am])
        p.line(p.px(rm), p.py(am), p.px(rm), p.py(0), GR, 1, '4 3'); p.line(p.px(rm), p.py(am), p.px(0), p.py(am), GR, 1, '4 3')
        p.pl([(0, 0), (rm * 1.2, am * 1.2)], BL, 2.6); p.circ(p.px(rm), p.py(am), 3.6, RD, RD, 1)
        body = PP('그림은 일정한 각속도로 등속 원운동하는 물체의 구심 가속도의 크기 a 를 원의 반지름 r 에 따라 나타낸 것이다. 이 물체의 각속도는?') + FIG(p.svg(), '58%')
        wr = wl(w_, [am / rm * 1.0 if am / rm != w_ else None, am, math.sqrt(am), rm, w_ * 2, w_ + 1, (am / rm) / 2], 'rad/s')
        return mc(body, ans(w_, 'rad/s'), wr, r=r, lv='상', fam='f', steps=['a = rω² 이므로 a-r 그래프의 기울기가 ω² 이다.', '기울기 = %s / %s = %s = ω² 이므로 ω = %s rad/s' % (num(am), num(rm), num(w_ * w_), num(w_))],
                  core='각속도가 일정하면 a-r 그래프는 원점을 지나는 직선이고 기울기는 ω² 이다.', point='기울기가 ω² 임을 이용한다.')
    # fig_a
    v = r.choice([2, 4, 6, 8, 10]); rr = r.choice([2, 4, 5, 8, 10]); a = v * v / rr
    if not two(a): return None
    f = scene(r.choice([30, 60, 120, 210, 300]), r.random() < .5, 'r = %s m' % num(rr), 'v = %s m/s' % num(v), 'a')
    body = PP('그림은 반지름 %s인 원 위를 %s의 속력으로 등속 원운동하는 %s의 모습을 나타낸 것이다. %s의 가속도(a)의 크기는?' % (U(rr, 'm'), U(v, 'm/s'), ob, ob)) + FIG(f.svg(), '60%')
    wr = wl(a, [v / rr, v * rr, v * v * rr, v * v / (2 * rr), 0.5 * v * v / rr * 2, a + 1], 'm/s²')
    return mc(body, ans(a, 'm/s²'), wr, r=r, lv='하', fam='g', steps=['a = v²/r = %s² / %s = %s m/s², 방향은 원의 중심 O 를 향한다.' % (num(v), num(rr), num(a))],
              core='등속 원운동의 가속도는 크기 v²/r, 방향은 중심 방향이다.', point='그림의 값을 읽어 구심 가속도를 구한다.')


# ================================================================ ph037
@T('ph037')
def centripetal_force(r, k):
    """구심력의 크기 F = mv²/r."""
    form = r.choice(['F', 'F', 'F_w', 'F_T', 'find_m', 'find_v', 'find_r', 'ratio', 'ratio2', 'graph', 'fig_F', 'ride'])
    ob = r.choice(['물체', '공', '쇠구슬', '추'])
    cond = '(단, π = 3 으로 계산한다.)'
    if form == 'F':
        m = r.choice([0.5, 1, 2, 3, 4, 5]); v = r.choice([2, 3, 4, 5, 6, 8, 10]); rr = r.choice([1, 2, 4, 5, 10, 20])
        F = m * v * v / rr
        if not two(F): return None
        body = PP('질량 %s인 %s이(가) 반지름 %s인 원 위를 %s의 일정한 속력으로 운동한다. 이 %s에 작용하는 구심력의 크기는?' % (U(m, 'kg'), ob, U(rr, 'm'), U(v, 'm/s'), ob))
        wr = wl(F, [m * v / rr, m * v * v * rr, m * v * v / (2 * rr), v * v / rr, m * v * rr, F * 2], 'N')
        return mc(body, ans(F, 'N'), wr, r=r, lv='하', fam='a', steps=['F = mv²/r = %s × %s² / %s = %s N' % (num(m), num(v), num(rr), num(F))],
                  core='구심력의 크기는 F = mv²/r 이다.', point='속력을 제곱하고 반지름으로 나눈다.')
    if form == 'F_w':
        m = r.choice([0.5, 1, 2, 3, 4]); w_ = r.choice([1, 2, 3, 4, 5]); rr = r.choice([0.5, 1, 2, 3, 4]); F = m * w_ * w_ * rr
        if not two(F): return None
        body = PP('질량 %s인 %s이(가) 반지름 %s인 원 위를 각속도 %s로 등속 원운동한다. 이 %s에 작용하는 구심력의 크기는?' % (U(m, 'kg'), ob, U(rr, 'm'), U(w_, 'rad/s'), ob))
        wr = wl(F, [m * w_ * rr, m * w_ * w_ / rr, m * w_ * rr * rr, F * 2, F / 2, m * w_ * w_], 'N')
        return mc(body, ans(F, 'N'), wr, r=r, lv='하', fam='a', steps=['F = mrω² = %s × %s × %s² = %s N' % (num(m), num(rr), num(w_), num(F))],
                  core='구심력은 F = mrω² 으로도 쓴다.', point='각속도를 제곱한다.')
    if form == 'F_T':
        m = r.choice([0.5, 1, 2, 3]); rr = r.choice([0.5, 1, 2, 3, 4]); T_ = r.choice([1, 2, 3, 4, 6]); F = 4 * PI * PI * m * rr / T_ ** 2
        if not two(F): return None
        body = PP('질량 %s인 %s이(가) 반지름 %s인 원 위를 주기 %s로 등속 원운동한다. 이 %s에 작용하는 구심력의 크기는? %s' % (U(m, 'kg'), ob, U(rr, 'm'), U(T_, 's'), ob, cond))
        wr = wl(F, [2 * PI * m * rr / T_ ** 2, 4 * PI * m * rr / T_, 4 * PI * PI * m * rr / T_, F * 2, F / 2, 4 * PI * PI * m * T_ / rr], 'N')
        return mc(body, ans(F, 'N'), wr, r=r, lv='중', fam='a',
                  steps=['ω = 2π/T = 6/%s = %s rad/s' % (num(T_), num(6 / T_)), 'F = mrω² = %s × %s × %s² = %s N' % (num(m), num(rr), num(6 / T_), num(F))],
                  core='구심력은 F = 4π²mr/T² 이다.', point='주기를 각속도로 바꾸어 구심력을 구한다.')
    if form == 'find_m':
        v = r.choice([2, 4, 5, 6, 10]); rr = r.choice([1, 2, 4, 5, 10]); m = r.choice([0.5, 1, 2, 3, 4, 5]); F = m * v * v / rr
        if not two(F): return None
        body = PP('반지름 %s인 원 위를 %s의 속력으로 등속 원운동하는 %s에 작용하는 구심력의 크기가 %s이다. 이 %s의 질량은?' % (U(rr, 'm'), U(v, 'm/s'), ob, U(F, 'N'), ob))
        wr = wl(m, [F * v / rr, F * rr * v, F / v, F * v * v / rr, m * 2, m / 2], 'kg')
        return mc(body, ans(m, 'kg'), wr, r=r, lv='중', fam='b', steps=['F = mv²/r 에서 m = Fr/v² = %s × %s / %s² = %s kg' % (num(F), num(rr), num(v), num(m))],
                  core='m = Fr/v² 이다.', point='구심력 식을 변형한다.')
    if form == 'find_v':
        m = r.choice([0.5, 1, 2, 4]); rr = r.choice([1, 2, 4, 5, 10, 20]); v = r.choice([2, 4, 5, 6, 8, 10]); F = m * v * v / rr
        if not two(F): return None
        body = PP('질량 %s인 %s이(가) 반지름 %s인 원 위를 등속 원운동하는 데 필요한 구심력의 크기가 %s이다. %s의 속력은?' % (U(m, 'kg'), ob, U(rr, 'm'), U(F, 'N'), ob))
        wr = wl(v, [F * rr / m, F * rr, F / m, math.sqrt(F * rr), math.sqrt(F * rr / m) * 2, v + 1], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='b', steps=['F = mv²/r 에서 v² = Fr/m = %s × %s / %s = %s' % (num(F), num(rr), num(m), num(v * v)), 'v = %s m/s' % num(v)],
                  core='v = √(Fr/m) 이다.', point='제곱근을 취한다.')
    if form == 'find_r':
        m = r.choice([0.5, 1, 2, 3]); v = r.choice([2, 4, 5, 6, 10]); rr = r.choice([1, 2, 4, 5, 10]); F = m * v * v / rr
        if not two(F): return None
        body = PP('질량 %s인 %s이(가) %s의 속력으로 등속 원운동하는 데 필요한 구심력의 크기가 %s이다. 원의 반지름은?' % (U(m, 'kg'), ob, U(v, 'm/s'), U(F, 'N')))
        wr = wl(rr, [m * v / F, m * v * v * F, F / (m * v * v), m * v * v / (2 * F), rr * 2, rr / 2], 'm')
        return mc(body, ans(rr, 'm'), wr, r=r, lv='중', fam='b', steps=['F = mv²/r 에서 r = mv²/F = %s × %s² / %s = %s m' % (num(m), num(v), num(F), num(rr))],
                  core='r = mv²/F 이다.', point='반지름은 구심력에 반비례한다.')
    if form == 'ratio':
        m = r.choice([1, 2, 3]); v = r.choice([2, 4, 6]); rr = r.choice([2, 4, 6]); F = m * v * v / rr
        nm = r.choice([1, 2, 3]); nv = r.choice([1, 2, 3, 0.5]); nr = r.choice([1, 2, 0.5, 3])
        if (nm, nv, nr) == (1, 1, 1): return None
        F2 = F * nm * nv * nv / nr
        if not two(F) or not two(F2) or not two(v * nv) or not two(rr * nr): return None
        body = PP('질량 %s인 %s이(가) 반지름 %s인 원 위를 %s의 속력으로 등속 원운동할 때 구심력의 크기는 %s이다. 질량을 %s로, 속력을 %s로, 반지름을 %s로 바꾸어 등속 원운동시키면 구심력의 크기는?' % (U(m, 'kg'), ob, U(rr, 'm'), U(v, 'm/s'), U(F, 'N'), U(m * nm, 'kg'), U(v * nv, 'm/s'), U(rr * nr, 'm')))
        wr = wl(F2, [F * nm * nv / nr, F * nm * nv * nv * nr, F * nm * nv, F * nm * nv * nv, F * nv * nv / nr, F * nm * nr / nv], 'N')
        return mc(body, ans(F2, 'N'), wr, r=r, lv='상', fam='c',
                  steps=['F = mv²/r 이므로 F ∝ m v² / r', '변화 배수 = %s × %s² / %s = %s 배' % (num(nm), num(nv), num(nr), num(nm * nv * nv / nr)), '새 구심력 = %s × %s = %s N' % (num(F), num(nm * nv * nv / nr), num(F2))],
                  core='구심력은 질량과 속력의 제곱에 비례하고 반지름에 반비례한다.', point='세 양이 함께 변할 때 배수를 곱한다.')
    if form == 'ratio2':
        n = r.choice([2, 3, 4]); kind = r.choice(['v', 'r', 'm'])
        F = r.choice([4, 6, 8, 12, 16, 20])
        if kind == 'v':
            F2 = F * n * n; txt = '질량과 반지름은 그대로 두고 속력만 %d배로' % n; st = ['F ∝ v² 이므로 속력이 %d배이면 구심력은 %d배이다.' % (n, n * n)]
        elif kind == 'r':
            if F % n: return None
            F2 = F / n; txt = '질량과 속력은 그대로 두고 반지름만 %d배로' % n; st = ['F ∝ 1/r 이므로 반지름이 %d배이면 구심력은 1/%d배이다.' % (n, n)]
        else:
            F2 = F * n; txt = '속력과 반지름은 그대로 두고 질량만 %d배로' % n; st = ['F ∝ m 이므로 질량이 %d배이면 구심력도 %d배이다.' % (n, n)]
        body = PP('등속 원운동하는 %s에 작용하는 구심력의 크기가 %s이다. %s 바꾸면 구심력의 크기는?' % (ob, U(F, 'N'), txt))
        wr = wl(F2, [F * n, F * n * n, F / n, F / (n * n), F + n, F * 2], 'N')
        return mc(body, ans(F2, 'N'), wr, r=r, lv='중', fam='c', steps=st + ['따라서 %s × %s = %s N' % (num(F), num(F2 / F), num(F2))],
                  core='구심력은 질량에 비례, 속력의 제곱에 비례, 반지름에 반비례한다.', point='어떤 양이 바뀌는지에 따라 배수를 구한다.')
    if form == 'graph':
        m = r.choice([1, 2, 3, 4]); rr = r.choice([1, 2, 4, 5]); k_ = m / rr; vv = r.choice([4, 9, 16, 25, 36]); F = k_ * vv
        if not two(F) or F > 60: return None
        p = Plot(280, 190, vv * 1.25, F * 1.25, ml=48, mr=18, mt=16, mb=40)
        p.axes('v²(m²/s²)', 'F(N)', [vv], [F])
        p.line(p.px(vv), p.py(F), p.px(vv), p.py(0), GR, 1, '4 3'); p.line(p.px(vv), p.py(F), p.px(0), p.py(F), GR, 1, '4 3')
        p.pl([(0, 0), (vv * 1.2, F * 1.2)], BL, 2.6); p.circ(p.px(vv), p.py(F), 3.6, RD, RD, 1)
        body = PP('그림은 반지름이 %s인 원 위를 등속 원운동하는 물체에 작용하는 구심력의 크기 F 를 속력의 제곱 v² 에 따라 나타낸 것이다. 이 물체의 질량은?' % U(rr, 'm')) + FIG(p.svg(), '58%')
        wr = wl(m, [F / vv, F / vv * rr * rr, F * rr, F / rr, m * 2, m + 1], 'kg')
        return mc(body, ans(m, 'kg'), wr, r=r, lv='상', fam='d', steps=['F = (m/r)v² 이므로 F-v² 그래프의 기울기가 m/r 이다.', '기울기 = %s / %s = %s 이므로 m = 기울기 × r = %s × %s = %s kg' % (num(F), num(vv), num(k_), num(k_), num(rr), num(m))],
                  core='F-v² 그래프는 원점을 지나는 직선이며 기울기는 m/r 이다.', point='기울기의 의미를 알아 질량을 구한다.')
    if form == 'fig_F':
        m = r.choice([0.5, 1, 2, 3]); v = r.choice([2, 4, 6, 8]); rr = r.choice([1, 2, 4, 8]); F = m * v * v / rr
        if not two(F): return None
        f = scene(r.choice([30, 60, 150, 240, 330]), r.random() < .5, 'r = %s m' % num(rr), 'v = %s m/s' % num(v), 'F')
        body = PP('그림은 마찰이 없는 수평면에서 질량 %s인 %s이(가) 줄에 매달려 등속 원운동하는 것을 위에서 본 모습이다. 줄이 %s을(를) 당기는 힘 F 의 크기는?' % (U(m, 'kg'), ob, ob)) + FIG(f.svg(), '60%')
        wr = wl(F, [m * v / rr, m * v * v * rr, m * v * rr, F * 2, F / 2, v * v / rr], 'N')
        return mc(body, ans(F, 'N'), wr, r=r, lv='하', fam='e', steps=['줄의 장력이 구심력 역할을 한다.', 'F = mv²/r = %s × %s² / %s = %s N' % (num(m), num(v), num(rr), num(F))],
                  core='수평면에서 줄이 당기는 힘(장력)이 구심력이다.', point='구심력의 원천을 찾는다.')
    # ride
    m = r.choice([40, 50, 60, 70]); rr = r.choice([2, 3, 4, 5]); T_ = r.choice([2, 3, 4, 6]); F = 4 * PI * PI * m * rr / T_ ** 2
    if not two(F): return None
    body = PP('반지름 %s인 원통형 놀이기구가 일정한 주기 %s로 회전하고 있다. 벽에 붙어 함께 도는 질량 %s인 사람이 벽으로부터 받는 수직 항력의 크기는? %s' % (U(rr, 'm'), U(T_, 's'), U(m, 'kg'), cond))
    wr = wl(F, [m * rr * 2 * PI / T_, m * G, 4 * PI * m * rr / T_ ** 2, F * 2, F / 2, 2 * PI * m * rr / T_ ** 2], 'N')
    return mc(body, ans(F, 'N'), wr, r=r, lv='중', fam='f', steps=['벽의 수직 항력이 구심력 역할을 한다.', 'N = mrω² = m r (2π/T)² = %s × %s × (6/%s)² = %s N' % (num(m), num(rr), num(T_), num(F))],
              core='회전하는 원통 벽에서 수직 항력이 구심력이다: N = 4π²mr/T².', point='구심력을 제공하는 힘을 찾아 식에 대입한다.')


# ================================================================ ph038
def dir_fig(theta, ccw, letters, w=270, h=235, R=82):
    """물체에서 5개 방향 화살표(A~E). letters: 방향 키 -> 문자."""
    f = Fig(w, h)
    cx, cy = w / 2, h / 2 + 4
    f.circ(cx, cy, R, 'none', GR, 1.4, '5 3'); f.circ(cx, cy, 3, INK, INK, 1); f.text(cx + 11, cy + 4, 'O', 13, bold=True, italic=True)
    th = math.radians(theta)
    px, py = cx + R * math.cos(th), cy - R * math.sin(th)
    f.line(cx, cy, px, py, GR, 1.2)
    s = 1 if ccw else -1
    tx, ty = -math.sin(th) * s, -math.cos(th) * s          # 진행 방향(화면)
    ux, uy = (cx - px) / R, (cy - py) / R                   # 중심 방향
    dirs = {'fwd': (tx, ty), 'back': (-tx, -ty), 'in': (ux, uy), 'out': (-ux, -uy), 'diag': ((tx + ux) / math.sqrt(2), (ty + uy) / math.sqrt(2))}
    for key, (dx, dy) in dirs.items():
        L = 34
        f.arrow(px, py, px + L * dx, py + L * dy, RD if key == 'fwd' else BL, 2.2)
        f.text(px + (L + 10) * dx, py + (L + 10) * dy + 5, letters[key], 13, bold=True, c=INK)
    f.circ(px, py, 6.5, '#f2b400', INK, 1.3)
    return f.svg()


def hole_fig(w=270, h=190):
    f = Fig(w, h)
    f.line(20, 70, 250, 70, INK, 2.4)
    f.hatch(20, 70, 230) if False else None
    cx = 135
    f.rect(cx - 5, 66, 10, 8, '#fff', '#fff', 0)
    f.circ(cx, 70, 3, INK, INK, 1)
    f.circ(cx, 70, 60, 'none', GR, 1.2, '5 3')
    f.line(cx, 70, cx + 60, 70, GR, 1.4)
    f.circ(cx + 60, 70, 8, RD, INK, 1.3); f.text(cx + 60, 58, 'm', 13, bold=True, italic=True)
    f.line(cx, 70, cx, 140, INK, 1.6)
    f.rect(cx - 12, 140, 24, 22, '#cfe2f7', INK, 1.5); f.text(cx, 156, 'M', 13, bold=True, italic=True)
    f.text(cx + 28, 40, 'r', 13, bold=True, italic=True)
    f.text(cx + 40, 125, '정지', 12, 'start', c=GR)
    return f.svg()


def two_string_fig(w=300, h=130):
    f = Fig(w, h)
    O = (30, 70); A = (130, 70); B = (250, 70)
    f.circ(*O, 3, INK, INK, 1); f.text(O[0], 94, 'O', 13, bold=True, italic=True)
    f.line(O[0], 70, B[0], 70, INK, 2)
    f.circ(*A, 8, BL, INK, 1.3); f.text(A[0], 56, 'A', 13.5, bold=True, c=BL, italic=True)
    f.circ(*B, 8, RD, INK, 1.3); f.text(B[0], 56, 'B', 13.5, bold=True, c=RD, italic=True)
    f.arrow(O[0], 108, A[0], 108, GR, 1.3); f.arrow(A[0], 108, O[0], 108, GR, 1.3); f.text((O[0] + A[0]) / 2, 124, 'r_A', 12.5, bold=True)
    f.arrow(O[0], 98, B[0], 98, GR, 1.3) if False else None
    f.arrow(A[0], 108, B[0], 108, GR, 1.3); f.arrow(B[0], 108, A[0], 108, GR, 1.3); f.text((A[0] + B[0]) / 2, 124, 'Δr', 12.5, bold=True)
    f.text((O[0] + A[0]) / 2, 42, '줄 1', 12, c=GR); f.text((A[0] + B[0]) / 2, 42, '줄 2', 12, c=GR)
    return f.svg()


TR3 = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 6, 10), (12, 5, 13), (9, 12, 15), (4, 3, 5), (12, 16, 20), (8, 15, 17), (15, 8, 17), (16, 12, 20), (20, 15, 25)]


@T('ph038')
def string_circle(r, k):
    """수평면에서 줄에 매달려 도는 물체, 줄이 끊어지면 접선 방향 직진."""
    form = r.choice(['dir', 'dist', 'dist', 'dist', 'hole_v', 'hole_v', 'hole_M', 'two', 'two', 'T_f', 'break_v'])
    ob = r.choice(['물체', '공', '쇠구슬', '나무토막'])
    if form == 'dir':
        theta = r.choice([20, 45, 70, 110, 135, 160, 200, 225, 250, 290, 315, 340]); ccw = r.random() < 0.5
        keys = ['fwd', 'back', 'in', 'out', 'diag']; letters = dict(zip(keys, r.sample(['A', 'B', 'C', 'D', 'E'], 5)))
        fig = dir_fig(theta, ccw, letters)
        body = PP('그림은 마찰이 없는 수평면 위에서 줄에 매달려 점 O 를 중심으로 %s 방향으로 등속 원운동하는 %s을(를) 위에서 본 모습이다. 이 순간 줄이 끊어졌다. 줄이 끊어진 후 %s이(가) 운동하는 방향으로 옳은 것은? (단, 수평면에서 다른 힘은 작용하지 않는다.)' % ('시계 반대' if ccw else '시계', ob, ob)) + FIG(fig, '56%')
        right = letters['fwd']
        wr = [letters[x] for x in keys if x != 'fwd']
        return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf',
                  steps=['줄이 끊어지면 구심력이 사라져 물체에 힘이 작용하지 않는다.', '관성에 의해 끊어지는 순간의 속도 방향(원의 접선 방향, 진행 방향)으로 등속 직선 운동한다.', '따라서 %s 방향이다.' % right],
                  core='구심력이 사라지면 물체는 원의 접선 방향으로 등속 직선 운동한다.', point='줄이 끊어지는 순간의 속도 방향을 찾는다.')
    if form == 'dist':
        rr, leg, d = r.choice(TR3)
        ts = [t for t in (1, 2, 3, 4, 5, 6, 8) if leg % t == 0 and leg / t <= 20]
        if not ts: return None
        t = r.choice(ts); v = leg / t
        if rr > 20: return None
        body = PP('마찰이 없는 수평면에서 점 O 를 중심으로 반지름 %s인 원 위를 %s의 속력으로 등속 원운동하는 %s을(를) 줄이 끊어지는 순간부터 %s 후 O 로부터의 거리는? (단, 줄이 끊어진 뒤에는 수평면에서 힘이 작용하지 않는다.)' % (U(rr, 'm'), U(v, 'm/s'), ob, U(t, '초')) if False else
                 '마찰이 없는 수평면에서 점 O 를 중심으로 반지름 %s인 원 위를 %s의 속력으로 등속 원운동하던 %s의 줄이 끊어졌다. 줄이 끊어진 순간부터 %s 후 %s과(와) O 사이의 거리는? (단, 줄이 끊어진 뒤에는 수평면에서 힘이 작용하지 않는다.)' % (U(rr, 'm'), U(v, 'm/s'), ob, U(t, '초'), ob))
        assert abs(math.hypot(rr, v * t) - d) < 1e-9
        wr = wl(d, [rr + v * t, v * t, rr, abs(rr - v * t), d + 2, math.sqrt(rr * rr + v * v * t)], 'm')
        return mc(body, ans(d, 'm'), wr, r=r, lv='중', fam='b',
                  steps=['줄이 끊어지면 %s은 접선 방향으로 등속 직선 운동한다 : 이동 거리 = vt = %s × %s = %s m' % (ob, num(v), num(t), num(leg)), '접선은 반지름과 수직이므로 O 까지의 거리 = √(%s² + %s²) = %s m' % (num(rr), num(leg), num(d))],
                  core='끊어진 뒤의 직선 경로는 원의 접선이므로 반지름과 수직이고, 거리는 피타고라스 정리로 구한다.', point='접선과 반지름이 수직임을 이용한다.')
    if form in ('hole_v', 'hole_M'):
        m = r.choice([0.5, 1, 2, 0.4, 0.2]); M = r.choice([1, 2, 0.5, 0.8, 1.5, 4]); rr = r.choice([0.5, 1, 2, 0.4, 0.8, 1.6, 2.5, 5])
        v2 = M * G * rr / m
        v = math.sqrt(v2)
        if abs(v - round(v)) > 1e-9 or not two(v2): return None
        v = int(round(v))
        fig = hole_fig()
        if form == 'hole_v':
            body = PP('그림과 같이 마찰이 없는 수평면 위에서 질량 %s인 물체 m 이 구멍을 통과한 줄에 의해 질량 %s인 추 M 과 연결되어 있다. m 이 구멍 O 를 중심으로 반지름 %s인 원 위를 등속 원운동하고 M 은 정지해 있을 때, m 의 속력은? (단, 중력 가속도는 10 m/s²이고 줄의 질량은 무시한다.)' % (U(m, 'kg'), U(M, 'kg'), U(rr, 'm'))) + FIG(fig, '56%')
            wr = wl(v, [M * G * rr / m, math.sqrt(M * G * rr), math.sqrt(m * G * rr / M), v * 2, v / 2, math.sqrt(M * G / (m * rr))], 'm/s')
            return mc(body, ans(v, 'm/s'), wr, r=r, lv='상', fam='c',
                      steps=['M 이 정지해 있으므로 줄의 장력 T = Mg = %s × 10 = %s N' % (num(M), num(M * G)), '이 장력이 m 의 구심력이다 : T = mv²/r', 'v² = Tr/m = %s × %s / %s = %s 이므로 v = %s m/s' % (num(M * G), num(rr), num(m), num(v2), num(v))],
                      core='구멍 아래 추가 정지해 있으면 줄의 장력은 추의 무게 Mg 이고, 이 장력이 수평면 위 물체의 구심력이다.', point='장력 = Mg = mv²/r 로 연결한다.')
        body = PP('그림과 같이 마찰이 없는 수평면 위에서 질량 %s인 물체 m 이 구멍을 통과한 줄에 의해 추 M 과 연결되어 있다. m 이 구멍 O 를 중심으로 반지름 %s인 원 위를 %s의 속력으로 등속 원운동하고 M 이 정지해 있을 때, M 의 질량은? (단, 중력 가속도는 10 m/s²이고 줄의 질량은 무시한다.)' % (U(m, 'kg'), U(rr, 'm'), U(v, 'm/s'))) + FIG(fig, '56%')
        wr = wl(M, [m * v * v / rr, m * v * v / (rr * 100), m * v / rr, m * v * v * rr / G, M * 2, M / 2], 'kg')
        return mc(body, ans(M, 'kg'), wr, r=r, lv='중', fam='c',
                  steps=['m 의 구심력 : T = mv²/r = %s × %s² / %s = %s N' % (num(m), num(v), num(rr), num(m * v * v / rr)), 'M 이 정지해 있으므로 T = Mg 에서 M = T/g = %s / 10 = %s kg' % (num(m * v * v / rr), num(M))],
                  core='장력은 수평면 위 물체의 구심력이면서 추의 무게와 같다.', point='구심력과 추의 평형을 연결한다.')
    if form == 'two':
        mA = r.choice([1, 2, 3]); mB = r.choice([1, 2, 3]); rA = r.choice([0.5, 1, 2]); rB = rA * r.choice([2, 3]); w_ = r.choice([1, 2, 3, 4])
        T2 = mB * w_ * w_ * rB; T1 = T2 + mA * w_ * w_ * rA
        if not two(T1) or not two(T2): return None
        fig = two_string_fig()
        which = r.choice([1, 2])
        body = PP('그림은 마찰이 없는 수평면 위에서 점 O 를 중심으로 같은 각속도 %s로 등속 원운동하는 물체 A, B 를 위에서 본 모습이다. A, B 의 질량은 각각 %s, %s이고 O 로부터의 거리는 각각 %s, %s이다. 줄 %d 의 장력의 크기는? (단, 줄의 질량은 무시하고, 줄 1 은 O 와 A 를, 줄 2 는 A 와 B 를 연결한다.)' % (U(w_, 'rad/s'), U(mA, 'kg'), U(mB, 'kg'), U(rA, 'm'), U(rB, 'm'), which)) + FIG(fig, '66%')
        if which == 2:
            wr = wl(T2, [T1, mB * w_ * rB, mA * w_ * w_ * rA, T1 + T2, mB * w_ * w_ * rA, T2 * 2], 'N')
            return mc(body, ans(T2, 'N'), wr, r=r, lv='중', fam='d', steps=['줄 2 의 장력만이 B 의 구심력이다.', 'T₂ = m_B r_B ω² = %s × %s × %s² = %s N' % (num(mB), num(rB), num(w_), num(T2))],
                      core='가장 바깥 물체의 구심력은 바깥 줄의 장력이다.', point='물체별로 구심력을 구분한다.')
        wr = wl(T1, [T2, mA * w_ * w_ * rA, T1 + T2, T2 - mA * w_ * w_ * rA if T2 > mA * w_ * w_ * rA else None, (mA + mB) * w_ * w_ * rA, T1 * 2], 'N')
        return mc(body, ans(T1, 'N'), wr, r=r, lv='상', fam='d',
                  steps=['B : T₂ = m_B r_B ω² = %s × %s × %s² = %s N' % (num(mB), num(rB), num(w_), num(T2)), 'A : 구심력 = T₁ - T₂ = m_A r_A ω² = %s N 이므로' % num(mA * w_ * w_ * rA), 'T₁ = T₂ + m_A r_A ω² = %s + %s = %s N' % (num(T2), num(mA * w_ * w_ * rA), num(T1))],
                  core='안쪽 줄의 장력은 안쪽 물체의 구심력에 바깥 줄이 당기는 힘을 더한 값이다.', point='물체 A 의 알짜힘(구심력) = T₁ - T₂ 이다.')
    if form == 'T_f':
        m = r.choice([0.5, 1, 2, 3, 4]); v = r.choice([2, 4, 5, 6, 8, 10]); rr = r.choice([1, 2, 4, 5, 10]); F = m * v * v / rr
        if not two(F): return None
        body = PP('질량 %s인 %s이(가) 마찰이 없는 수평면 위에서 길이 %s의 줄에 매달려 줄의 한쪽 끝 O 를 중심으로 %s의 속력으로 등속 원운동한다. 줄의 장력의 크기는?' % (U(m, 'kg'), ob, U(rr, 'm'), U(v, 'm/s')))
        wr = wl(F, [m * v / rr, m * v * rr, m * G, F * 2, F / 2, m * v * v * rr], 'N')
        return mc(body, ans(F, 'N'), wr, r=r, lv='하', fam='e', steps=['수평면에서 줄의 장력이 구심력이다.', 'T = mv²/r = %s × %s² / %s = %s N' % (num(m), num(v), num(rr), num(F))],
                  core='마찰이 없는 수평면 위의 원운동에서 장력이 구심력이다.', point='장력 = 구심력임을 이용한다.')
    # break_v : 끊어진 후 이동 거리
    rr = r.choice([2, 3, 4, 5]); v = r.choice([2, 3, 4, 5]); t = r.choice([1, 2, 3]); leg = v * t
    body = PP('마찰이 없는 수평면에서 등속 원운동하던 %s의 줄이 끊어졌다. 줄이 끊어진 순간의 속력이 %s이었다면 끊어진 후 %s 동안 %s이(가) 이동한 거리는?' % (ob, U(v, 'm/s'), U(t, '초'), ob))
    wr = wl(leg, [leg * 2, v * v * t, v / t, leg / 2, leg + rr, math.hypot(rr, leg)], 'm')
    return mc(body, ans(leg, 'm'), wr, r=r, lv='하', fam='e', steps=['줄이 끊어지면 접선 방향으로 등속 직선 운동한다.', '이동 거리 = vt = %s × %s = %s m' % (num(v), num(t), num(leg))],
              core='구심력이 사라지면 속력은 변하지 않는 등속 직선 운동을 한다.', point='끊어진 뒤의 운동은 등속 직선 운동이다.')


# ================================================================ ph039
def cone_fig(deg, w=240, h=200):
    f = Fig(w, h)
    cx = w / 2 - 10; top = 24
    L = 120
    th = math.radians(deg)
    bx, by = cx + L * math.sin(th), top + L * math.cos(th)
    f.line(cx - 40, top, cx + 40, top, INK, 2.4)
    f.line(cx, top, cx, top + L + 20, GR, 1.2, '4 3')
    f.line(cx, top, bx, by, INK, 1.8)
    f.ell(cx, by, L * math.sin(th), 12, 'none', GR, 1.2, '4 3')
    f.circ(bx, by, 9, RD, INK, 1.3)
    f.o.append('<path d="M %s %s A 40 40 0 0 0 %s %s" fill="none" stroke="%s" stroke-width="1.3"/>' % (Fig._n(cx), Fig._n(top + 40), Fig._n(cx + 40 * math.sin(th)), Fig._n(top + 40 * math.cos(th)), GR))
    f.text(cx + 14, top + 62, 'θ', 14, 'start', True, GR, True)
    f.arrow(bx, by, bx - 34, by, BL, 2.2)
    return f.svg()


def bank_fig(deg, w=290, h=170):
    f = Fig(w, h)
    th = math.radians(deg)
    x0, y0 = 30, h - 24
    L = 220
    xe, ye = x0 + L * math.cos(th), y0 - L * math.sin(th)
    f.poly([(x0, y0), (xe, y0), (xe, ye)], '#eef2f7', INK, 1.8)
    t = 0.55
    px, py = x0 + (xe - x0) * t, y0 + (ye - y0) * t
    f.o.append('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="36" height="20" fill="#cfe2f7" stroke="%s" stroke-width="1.6"/></g>' % (Fig._n(-deg), Fig._n(px), Fig._n(py), Fig._n(px - 18), Fig._n(py - 20), INK))
    f.o.append('<path d="M %s %s A 40 40 0 0 0 %s %s" fill="none" stroke="%s" stroke-width="1.3"/>' % (Fig._n(x0 + 40), Fig._n(y0), Fig._n(x0 + 40 * math.cos(th)), Fig._n(y0 - 40 * math.sin(th)), GR))
    f.text(x0 + 52, y0 - 8, 'θ', 14, 'start', True, GR, True)
    return f.svg()


@T('ph039')
def cone_and_road(r, k):
    """원뿔 진자와 곡선 도로."""
    form = r.choice(['cone_F', 'cone_T', 'cone_v', 'cone_th', 'road_f', 'road_f', 'road_mu', 'road_v', 'bank_th', 'bank_v', 'mu_ratio', 'road_f2', 'cone_F'])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    if form in ('cone_F', 'cone_T'):
        deg = r.choice([37, 45, 53, 60]) if form == 'cone_F' else r.choice([37, 60])
        m = r.choice([0.5, 1, 2, 3, 4]); tn = {37: 0.75, 45: 1, 53: 4 / 3, 60: None}[deg]
        if form == 'cone_F':
            if deg == 60: deg = 45; tn = 1
            if deg == 53 and (m * G * 4 / 3) % 1 > 1e-9 and not two(m * G * 4 / 3): return None
            Fc = m * G * tn
            if not two(Fc): return None
            fig = cone_fig(deg)
            body = PP('그림과 같이 질량 %s인 추가 길이가 일정한 줄에 매달려 연직선과 %d°를 이루며 수평면에서 등속 원운동하고 있다. 추에 작용하는 구심력의 크기는? (단, tan%d° = %s 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (U(m, 'kg'), deg, deg, {37: '3/4', 45: '1', 53: '4/3'}[deg])) + FIG(fig, '46%')
            wr = wl(Fc, [m * G, m * G / tn, m * G * math.sin(math.radians(deg)), m * G / math.cos(math.radians(deg)), Fc * 2, m * G * (1 - tn)], 'N')
            return mc(body, ans(Fc, 'N'), wr, r=r, lv='중', fam='a',
                      steps=['추에 작용하는 힘은 중력 mg(아래)와 장력 T(줄 방향)이다.', '연직 방향 : T cos%d° = mg, 수평 방향 : T sin%d° = F(구심력)' % (deg, deg), 'F = mg tan%d° = %s × 10 × %s = %s N' % (deg, num(m), tstr(tn), num(Fc))],
                      core='원뿔 진자에서 구심력은 mg tanθ 이다(장력의 수평 성분).', point='장력을 연직·수평 성분으로 나누어 구심력을 구한다.')
        ct = {37: 0.8, 60: 0.5}[deg]
        T_ = m * G / ct
        if not two(T_): return None
        fig = cone_fig(deg)
        body = PP('그림과 같이 질량 %s인 추가 길이가 일정한 줄에 매달려 연직선과 %d°를 이루며 수평면에서 등속 원운동하고 있다. 줄의 장력의 크기는? (단, cos%d° = %s 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (U(m, 'kg'), deg, deg, {37: '4/5', 60: '1/2'}[deg])) + FIG(fig, '46%')
        wr = wl(T_, [m * G, m * G * math.tan(math.radians(deg)), m * G * ct, m * G * (1 - ct) + m * G, T_ * 2, m * G * 1.5], 'N')
        return mc(body, ans(T_, 'N'), wr, r=r, lv='중', fam='a',
                  steps=['연직 방향의 힘의 평형 : T cos%d° = mg' % deg, 'T = mg / cos%d° = %s × 10 / %s = %s N' % (deg, num(m), num(ct), num(T_))],
                  core='원뿔 진자에서 줄의 장력의 연직 성분이 중력과 평형을 이룬다: T cosθ = mg.', point='연직 방향은 힘의 평형이다.')
    if form == 'cone_v':
        deg, rr = r.choice([(45, 2.5), (45, 10), (45, 22.5), (45, 40), (37, 1.2), (37, 4.8), (37, 10.8), (37, 19.2)])
        tn = 1 if deg == 45 else 0.75
        v = math.sqrt(rr * G * tn)
        if abs(v - round(v)) > 1e-9: return None
        v = int(round(v)); fig = cone_fig(deg)
        body = PP('그림과 같이 줄에 매달린 추가 연직선과 %d°를 이루며 반지름 %s인 수평 원 위를 등속 원운동하고 있다. 추의 속력은? (단, tan%d° = %s 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (deg, U(rr, 'm'), deg, '1' if deg == 45 else '3/4')) + FIG(fig, '46%')
        wr = wl(v, [rr * G * tn, math.sqrt(rr * G), rr * tn, math.sqrt(rr * G / tn), v * 2, v + 2], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='상', fam='a',
                  steps=['구심력 mg tanθ = mv²/r 이므로 v² = rg tanθ', 'v² = %s × 10 × %s = %s 이므로 v = %s m/s' % (num(rr), tstr(tn), num(v * v), num(v))],
                  core='원뿔 진자의 속력은 v² = rg tanθ 이다(질량과 무관).', point='mg tanθ = mv²/r 에서 질량이 약분된다.')
    if form == 'cone_th':
        v, rr, deg = r.choice([(6, 4.8, 37), (3, 1.2, 37), (9, 10.8, 37), (10, 10, 45), (5, 2.5, 45), (20, 40, 45), (10, 7.5, 53), (20, 30, 53)])
        tn = v * v / (rr * G)
        assert abs(tn - math.tan(math.radians(deg))) < 0.01
        body = PP('질량 m 인 추가 줄에 매달려 반지름 %s인 수평 원 위를 %s의 속력으로 등속 원운동하고 있다. 줄이 연직선과 이루는 각 θ 는? (단, tan37° = 3/4, tan45° = 1, tan53° = 4/3 이고, 공기 저항은 무시하며 중력 가속도는 10 m/s²이다.)' % (U(rr, 'm'), U(v, 'm/s')))
        wr = ['%d°' % a_ for a_ in (30, 37, 45, 53, 60) if a_ != deg]
        return mc(body, '%d°' % deg, wr, r=r, lv='중', fam='a', sort='shuf',
                  steps=['tanθ = v²/(rg) = %s² / (%s × 10) = %s' % (num(v), num(rr), tstr(tn)), 'tanθ = %s 이므로 θ = %d°' % ({37: '3/4', 45: '1', 53: '4/3'}[deg], deg)],
                  core='원뿔 진자에서 tanθ = v²/(rg) 이다.', point='구심력과 중력의 비로 각을 구한다.')
    if form in ('road_f', 'road_f2'):
        m = r.choice([500, 800, 1000, 1200, 1500, 2000]); v = r.choice([10, 15, 20, 25]); rr = r.choice([25, 50, 100, 125, 200])
        F = m * v * v / rr
        if not two(F): return None
        body = PP('질량 %s인 자동차가 수평한 곡선 도로(반지름 %s)를 %s의 일정한 속력으로 돌고 있다. 이 자동차가 바퀴와 도로 사이의 마찰력으로 받는 구심력의 크기는?' % (U(m, 'kg'), U(rr, 'm'), U(v, 'm/s')))
        wr = wl(F, [m * G, m * v / rr, m * v * v * rr, F * 2, F / 2, m * v * v / (2 * rr)], 'N')
        return mc(body, ans(F, 'N'), wr, r=r, lv='하', fam='b', steps=['수평한 곡선 도로에서는 마찰력이 구심력 역할을 한다.', 'f = mv²/r = %s × %s² / %s = %s N' % (num(m), num(v), num(rr), num(F))],
                  core='수평 곡선 도로에서 바퀴와 도로 사이의 (정지) 마찰력이 구심력이다.', point='마찰력이 구심력임을 이용한다.')
    if form == 'road_mu':
        mu = r.choice([0.2, 0.25, 0.4, 0.5, 0.8]); v = r.choice([10, 15, 20, 25, 30]); rr = v * v / (mu * G)
        if not two(rr) or rr > 400: return None
        body = PP('수평한 곡선 도로(반지름 %s)에서 자동차가 미끄러지지 않고 %s의 속력으로 돌려면 타이어와 도로 사이의 정지 마찰 계수는 최소 얼마이어야 하는가? (단, 중력 가속도는 10 m/s²이다.)' % (U(rr, 'm'), U(v, 'm/s')))
        wr = wl(mu, [v / (rr * G), v * v / rr, mu * 2, mu / 2, rr * G / (v * v), mu + 0.1], '')
        wr = [w.strip() for w in wr]
        return mc(body, num(mu), wr, r=r, lv='중', fam='c', steps=['마찰력이 구심력 : μmg = mv²/r', 'μ = v²/(rg) = %s² / (%s × 10) = %s' % (num(v), num(rr), num(mu))],
                  core='곡선 도로에서 미끄러지지 않을 조건은 μmg ≥ mv²/r 이며 최소 마찰 계수는 μ = v²/(rg) 이다.', point='질량이 약분됨을 이용한다.')
    if form == 'road_v':
        mu = r.choice([0.2, 0.25, 0.4, 0.5, 0.8, 0.9]); rr = r.choice([20, 45, 80, 125, 25, 36, 100, 180]); v2 = mu * G * rr
        v = math.sqrt(v2)
        if abs(v - round(v)) > 1e-9: return None
        v = int(round(v))
        body = PP('수평한 곡선 도로(반지름 %s)에서 타이어와 도로 사이의 정지 마찰 계수가 %s일 때 자동차가 미끄러지지 않고 돌 수 있는 최대 속력은? (단, 중력 가속도는 10 m/s²이다.)' % (U(rr, 'm'), num(mu)))
        wr = wl(v, [v2, mu * G * rr / 2, math.sqrt(mu * rr), mu * rr, v * 2, v / 2], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='c', steps=['최대 정지 마찰력 μmg 가 구심력 mv²/r 이상이어야 한다.', 'v² ≤ μgr = %s × 10 × %s = %s 이므로 v ≤ %s m/s' % (num(mu), num(rr), num(v2), num(v))],
                  core='곡선 도로에서의 최대 속력은 v = √(μgr) 이며 자동차의 질량과 무관하다.', point='최대 마찰력이 구심력과 같을 때의 속력이다.')
    if form == 'bank_th':
        v, rr, deg = r.choice([(10, 10, 45), (20, 40, 45), (15, 22.5, 45), (6, 4.8, 37), (9, 10.8, 37), (10, 7.5, 53), (20, 30, 53)])
        fig = bank_fig(deg)
        body = PP('그림과 같이 반지름 %s인 곡선 구간에서 도로가 수평면과 θ 의 각으로 기울어 있다. 자동차가 마찰력 없이도 미끄러지지 않고 %s의 속력으로 돌 수 있도록 하는 θ 는? (단, tan37° = 3/4, tan45° = 1, tan53° = 4/3 이고, 중력 가속도는 10 m/s²이다.)' % (U(rr, 'm'), U(v, 'm/s'))) + FIG(fig, '58%')
        wr = ['%d°' % a_ for a_ in (30, 37, 45, 53, 60) if a_ != deg]
        return mc(body, '%d°' % deg, wr, r=r, lv='상', fam='d', sort='shuf', steps=['마찰이 없을 때 수직 항력의 수평 성분이 구심력이다: N sinθ = mv²/r, N cosθ = mg', 'tanθ = v²/(rg) = %s² / (%s × 10) = %s' % (num(v), num(rr), tstr(v * v / (rr * G))), 'θ = %d°' % deg],
                  core='마찰이 없는 경사 도로에서 tanθ = v²/(rg) 이다.', point='수직 항력의 성분으로 구심력과 중력을 나눈다.')
    if form == 'bank_v':
        deg, rr = r.choice([(45, 10), (45, 22.5), (45, 40), (45, 2.5), (37, 4.8), (37, 10.8)])
        tn = 1 if deg == 45 else 0.75; v = math.sqrt(rr * G * tn)
        if abs(v - round(v)) > 1e-9: return None
        v = int(round(v)); fig = bank_fig(deg)
        body = PP('그림과 같이 반지름 %s인 곡선 구간에서 도로가 수평면과 %d°의 각으로 기울어 있다. 마찰력이 작용하지 않을 때 자동차가 도로 면을 따라 미끄러지지 않고 돌 수 있는 속력은? (단, tan%d° = %s 이고, 중력 가속도는 10 m/s²이다.)' % (U(rr, 'm'), deg, deg, '1' if deg == 45 else '3/4')) + FIG(fig, '58%')
        wr = wl(v, [rr * G * tn, math.sqrt(rr * G), v * 2, v / 2, rr * tn, v + 3], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='d', steps=['tanθ = v²/(rg) 에서 v² = rg tanθ = %s × 10 × %s = %s' % (num(rr), tstr(tn), num(v * v)), 'v = %s m/s' % num(v)],
                  core='경사 도로에서 마찰이 없을 때의 속력은 v = √(rg tanθ) 이다.', point='경사각과 반지름만으로 속력이 정해진다.')
    # mu_ratio : 개념적 비
    n = r.choice([2, 3]); mu = r.choice([0.2, 0.25, 0.4]); rr = r.choice([20, 25, 40, 50]); v = math.sqrt(mu * G * rr)
    if abs(v - round(v)) > 1e-9 or not two(mu * n * n): return None
    v = int(round(v))
    body = PP('수평한 곡선 도로(반지름 %s)에서 속력 %s로 달리던 자동차가 미끄러지지 않으려면 정지 마찰 계수가 최소 %s이어야 한다. 같은 도로에서 속력을 %s로 하여 미끄러지지 않고 돌려면 필요한 정지 마찰 계수의 최솟값은?' % (U(rr, 'm'), U(v, 'm/s'), num(mu), U(v * n, 'm/s')))
    new = mu * n * n
    wr = [num(x) for x in (mu * n, mu / n, mu / (n * n), mu * n * 2, mu + 0.1, new * 2) if num(x) != num(new)]
    return mc(body, num(new), wr, r=r, lv='중', fam='e', steps=['μ = v²/(rg) 이므로 μ ∝ v² 이다.', '속력이 %d배이면 μ 는 %d배 : %s × %d = %s' % (n, n * n, num(mu), n * n, num(new))],
              core='필요한 마찰 계수는 속력의 제곱에 비례한다.', point='속력 변화에 따른 배수를 제곱으로 적용한다.')


# ================================================================ ph040
def two_circ_fig(mA, rA, mB, rB, w=300, h=170):
    f = Fig(w, h)
    for cx, m, rr, nm, c in ((75, mA, rA, 'A', BL), (225, mB, rB, 'B', RD)):
        R = 22 + 14 * rr
        f.circ(cx, 85, R, 'none', GR, 1.3, '5 3'); f.circ(cx, 85, 3, INK, INK, 1)
        f.line(cx, 85, cx + R, 85, GR, 1.3)
        f.circ(cx + R, 85, 6 + 2 * m, c, INK, 1.2)
        f.text(cx + R / 2, 78, 'r = %s m' % num(rr), 12, bold=True)
        f.text(cx, 160, '%s (m = %s kg)' % (nm, num(m)), 12.5, bold=True, c=c)
    return f.svg()


@T('ph040')
def centripetal_compare(r, k):
    """구심력 비교(두 물체)."""
    form = r.choice(['F_ratio', 'F_ratio', 'a_ratio', 'table_max', 'table_max', 'same_w', 'same_v', 'same_T', 'fig_ratio', 'a_which', 'a_which', 'a_which'])
    cond = '(단, 두 물체는 각각 등속 원운동한다.)'
    if form == 'F_ratio':
        mA, mB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4]); rA, rB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4]); vA, vB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4])
        FA, FB = Fr(mA * vA * vA, rA), Fr(mB * vB * vB, rB)
        right = rstr(FA, FB)
        if right == '1 : 1' and r.random() < .6: return None
        tb = table(['', '질량(kg)', '반지름(m)', '속력(m/s)'], [['A', mA, rA, vA], ['B', mB, rB, vB]])
        body = PP('표는 두 물체 A, B 의 등속 원운동에 대한 자료이다. 구심력의 크기의 비 F_A : F_B 는?') + tb
        extra = [rstr(mA * vA * vA * rA, mB * vB * vB * rB), rstr(mA * vA * rB, mB * vB * rA), rstr(mA * vA * vA, mB * vB * vB), rstr(mA * rB, mB * rA), rstr(FB, FA)]
        wr = ratio_opts(right, extra)
        return mc(body, right, wr[:6], r=r, lv='중', fam='a', sort='shuf',
                  steps=['F = mv²/r 이므로 F_A = %d × %d² / %d = %s, F_B = %d × %d² / %d = %s' % (mA, vA, rA, num(float(FA)), mB, vB, rB, num(float(FB))), 'F_A : F_B = %s' % right],
                  core='구심력은 F = mv²/r 이다.', point='표에서 값을 읽어 각각 계산한 뒤 비를 구한다.')
    if form == 'a_ratio':
        vA, vB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4]); rA, rB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4])
        aA, aB = Fr(vA * vA, rA), Fr(vB * vB, rB)
        right = rstr(aA, aB)
        if right == '1 : 1' and r.random() < .5: return None
        body = PP('물체 A 는 반지름 %s인 원 위를 %s의 속력으로, 물체 B 는 반지름 %s인 원 위를 %s의 속력으로 운동한다. A, B 의 구심 가속도의 크기의 비 a_A : a_B 는?' % (U(rA, 'm'), U(vA, 'm/s'), U(rB, 'm'), U(vB, 'm/s')))
        wr = ratio_opts(right, [rstr(vA * rB, vB * rA), rstr(vA, vB), rstr(aB, aA), rstr(vA * vA * rA, vB * vB * rB)])
        return mc(body, right, wr[:6], r=r, lv='중', fam='b', sort='shuf', steps=['a = v²/r 이므로 a_A = %d²/%d, a_B = %d²/%d' % (vA, rA, vB, rB), 'a_A : a_B = %s' % right],
                  core='구심 가속도는 a = v²/r 이며 질량과 무관하다.', point='질량은 구심 가속도와 관계없다.')
    if form == 'table_max':
        for _ in range(30):
            rows = [(r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4])) for _ in range(3)]
            Fs = [Fr(m * v * v, rr) for m, rr, v in rows]
            if sorted(Fs)[-1] != sorted(Fs)[-2]: break
        else: return None
        mx = Fs.index(max(Fs)); nm = 'ABC'
        tb = table(['', '질량(kg)', '반지름(m)', '속력(m/s)'], [[nm[i], *rows[i]] for i in range(3)])
        body = PP('표는 세 물체 A, B, C 의 등속 원운동에 대한 자료이다. 구심력의 크기가 가장 큰 물체는?') + tb
        right = nm[mx]
        wr = [x for x in 'ABC' if x != right] + ['A 와 B 가 같다', 'B 와 C 가 같다']
        if Fs[0] == Fs[1]: wr = [w for w in wr if w != 'A 와 B 가 같다'] + ['A 와 C 가 같다']
        return mc(body, right, wr[:4], r=r, lv='중', fam='c', sort='shuf',
                  steps=['F = mv²/r 로 각각 구한다.'] + ['%s : %d × %d² / %d = %s N' % (nm[i], rows[i][0], rows[i][2], rows[i][1], num(float(Fs[i]))) for i in range(3)] + ['가장 큰 것은 %s 이다.' % right],
                  core='구심력 F = mv²/r.', point='세 물체의 구심력을 직접 계산하여 비교한다.')
    if form == 'same_w':
        mA, mB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4]); rA, rB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4])
        fig = disk_fig(rA, rB)
        right = rstr(mA * rA, mB * rB)
        if right == '1 : 1' and r.random() < .6: return None
        body = PP('그림은 일정한 각속도로 회전하는 원판 위에 놓인 두 물체 A, B 를 나타낸 것이다. A, B 의 질량은 각각 %s, %s이고, 회전 중심 O 로부터의 거리는 각각 %s, %s이다. 두 물체가 원판 위에서 미끄러지지 않을 때 A, B 에 작용하는 구심력의 크기의 비 F_A : F_B 는?' % (U(mA, 'kg'), U(mB, 'kg'), U(rA, 'cm'), U(rB, 'cm'))) + FIG(fig, '58%')
        wr = ratio_opts(right, [rstr(mA, mB), rstr(rA, rB), rstr(mA * rB, mB * rA), rstr(mB * rB, mA * rA), rstr(mA * rA * rA, mB * rB * rB)])
        return mc(body, right, wr[:6], r=r, lv='상', fam='d', sort='shuf', steps=['각속도가 같으므로 F = mrω² 에서 F ∝ mr 이다.', 'F_A : F_B = %d × %d : %d × %d = %s' % (mA, rA, mB, rB, right)],
                  core='각속도가 같으면 구심력은 질량과 반지름의 곱에 비례한다.', point='각속도가 같을 때 F = mrω² 를 쓴다.')
    if form == 'same_v':
        mA, mB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4]); rA, rB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4])
        right = rstr(Fr(mA, rA), Fr(mB, rB))
        if right == '1 : 1' and r.random() < .6: return None
        body = PP('질량이 각각 %s, %s인 두 물체 A, B 가 같은 속력으로 반지름 %s, %s인 원 위를 등속 원운동한다. A, B 의 구심력의 크기의 비 F_A : F_B 는?' % (U(mA, 'kg'), U(mB, 'kg'), U(rA, 'm'), U(rB, 'm')))
        wr = ratio_opts(right, [rstr(mA * rA, mB * rB), rstr(mA, mB), rstr(rB, rA), rstr(mA * rB, mB * rA) if False else rstr(mB * rA, mA * rB)])
        return mc(body, right, wr[:6], r=r, lv='중', fam='d', sort='shuf', steps=['속력이 같으므로 F = mv²/r 에서 F ∝ m/r 이다.', 'F_A : F_B = %d/%d : %d/%d = %s' % (mA, rA, mB, rB, right)],
                  core='속력이 같으면 구심력은 질량에 비례하고 반지름에 반비례한다.', point='속력이 같을 때 F ∝ m/r.')
    if form == 'same_T':
        mA, mB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4]); rA, rB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4])
        right = rstr(mA * rA, mB * rB)
        if right == '1 : 1' and r.random() < .6: return None
        body = PP('질량이 각각 %s, %s인 두 물체 A, B 가 같은 주기로 반지름 %s, %s인 원 위를 등속 원운동한다. A, B 의 속력의 비 v_A : v_B 와 구심력의 비 F_A : F_B 를 옳게 짝지은 것은?' % (U(mA, 'kg'), U(mB, 'kg'), U(rA, 'm'), U(rB, 'm')))
        vr = rstr(rA, rB)
        opts = [(vr, right), (right, vr), (rstr(rA * rA, rB * rB), right), (vr, rstr(mA * rA * rA, mB * rB * rB)), (rstr(rB, rA), rstr(mA * rB, mB * rA)), (vr, rstr(mA, mB)), (vr, rstr(mA * rB, mB * rA))]
        correct = '%s, %s' % (vr, right)
        wr = []
        for a_, b_ in opts:
            s_ = '%s, %s' % (a_, b_)
            if s_ != correct and s_ not in wr: wr.append(s_)
        return mc(body, correct, wr[:6], r=r, lv='상', fam='d', sort='shuf', steps=['주기가 같으므로 각속도가 같고 v = rω 에서 v ∝ r : v_A : v_B = %d : %d = %s' % (rA, rB, vr), 'F = mrω² 에서 F ∝ mr : F_A : F_B = %d×%d : %d×%d = %s' % (mA, rA, mB, rB, right)],
                  core='주기(각속도)가 같으면 v ∝ r, F ∝ mr 이다.', point='같은 주기에서 속력과 구심력의 비를 구분한다.')
    if form == 'fig_ratio':
        mA, mB = r.choice([1, 2, 3]), r.choice([1, 2, 3]); rA, rB = r.choice([1, 2, 3]), r.choice([1, 2, 3])
        vA, vB = r.choice([1, 2, 3]), r.choice([1, 2, 3])
        fig = two_circ_fig(mA, rA, mB, rB)
        right = rstr(Fr(mA * vA * vA, rA), Fr(mB * vB * vB, rB))
        body = PP('그림은 질량이 각각 %s, %s인 물체 A, B 가 반지름 %s, %s인 원 위를 각각 %s, %s의 속력으로 등속 원운동하는 모습을 나타낸 것이다. 구심력의 크기의 비 F_A : F_B 는?' % (U(mA, 'kg'), U(mB, 'kg'), U(rA, 'm'), U(rB, 'm'), U(vA, 'm/s'), U(vB, 'm/s'))) + FIG(fig, '66%')
        wr = ratio_opts(right, [rstr(mA * vA * vA * rA, mB * vB * vB * rB), rstr(mA * vA * rB, mB * vB * rA), rstr(mA * rB, mB * rA)])
        return mc(body, right, wr[:6], r=r, lv='중', fam='e', sort='shuf', steps=['F = mv²/r : F_A = %d × %d²/%d, F_B = %d × %d²/%d' % (mA, vA, rA, mB, vB, rB), 'F_A : F_B = %s' % right],
                  core='구심력 F = mv²/r.', point='그림의 값을 읽어 비를 구한다.')
    # a_which
    rA, rB, rC = r.sample([1, 2, 3, 4, 5, 6], 3); mode = r.choice(['w', 'v'])
    if mode == 'w':
        body = PP('같은 각속도로 등속 원운동하는 세 물체 A, B, C 의 반지름이 각각 %s, %s, %s이다. 구심 가속도의 크기가 가장 큰 물체는?' % (U(rA, 'm'), U(rB, 'm'), U(rC, 'm')))
        rs = [rA, rB, rC]; right = 'ABC'[rs.index(max(rs))]; st = ['각속도가 같으면 a = rω² 에서 a ∝ r 이므로 반지름이 가장 큰 물체의 구심 가속도가 가장 크다.']
    else:
        body = PP('같은 속력으로 등속 원운동하는 세 물체 A, B, C 의 반지름이 각각 %s, %s, %s이다. 구심 가속도의 크기가 가장 큰 물체는?' % (U(rA, 'm'), U(rB, 'm'), U(rC, 'm')))
        rs = [rA, rB, rC]; right = 'ABC'[rs.index(min(rs))]; st = ['속력이 같으면 a = v²/r 에서 a ∝ 1/r 이므로 반지름이 가장 작은 물체의 구심 가속도가 가장 크다.']
    wr = [x for x in 'ABC' if x != right] + ['A 와 B 가 같다', 'B 와 C 가 같다']
    return mc(body, right, wr, r=r, lv='하', fam='f', sort='shuf', steps=st + ['따라서 %s 이다.' % right],
              core='각속도가 같으면 a ∝ r, 속력이 같으면 a ∝ 1/r 이다.', point='어떤 양이 같은지에 따라 a 의 비례 관계가 달라진다.')


# ================================================================ ph041 (<보기>)
VEL_WORD = {(0, 1): '위쪽', (0, -1): '아래쪽', (-1, 0): '왼쪽', (1, 0): '오른쪽'}
PTS = {'A': 0, 'B': 90, 'C': 180, 'D': 270}


def ucm_fig(ccw, names='ABCD', w=250, h=225, R=70):
    f = Fig(w, h)
    cx, cy = w / 2, h / 2 + 2
    f.circ(cx, cy, R, 'none', GR, 1.6)
    f.circ(cx, cy, 3, INK, INK, 1); f.text(cx + 12, cy + 16, 'O', 13, bold=True, italic=True)
    for nm in names:
        th = math.radians(PTS[nm]); px, py = cx + R * math.cos(th), cy - R * math.sin(th)
        f.circ(px, py, 5.5, RD, INK, 1.2)
        f.text(px + 16 * math.cos(th), py - 16 * math.sin(th) + 5, nm, 14, bold=True, italic=True)
    # 운동 방향 표시(원 위 작은 화살표: 오른쪽 아래쪽 근처)
    th = math.radians(45); s = 1 if ccw else -1
    px, py = cx + R * math.cos(th), cy - R * math.sin(th)
    f.arrow(px, py, px - 22 * math.sin(th) * s, py - 22 * math.cos(th) * s, BL, 2.4)
    return f.svg()


def vert_fig(w=250, h=235, R=66):
    f = Fig(w, h)
    cx, cy = w / 2, h / 2
    f.circ(cx, cy, R, 'none', GR, 1.5, '5 3'); f.circ(cx, cy, 3, INK, INK, 1)
    f.text(cx + 12, cy + 16, 'O', 13, bold=True, italic=True)
    f.line(cx, cy, cx, cy - R, INK, 1.8); f.line(cx, cy, cx, cy + R, INK, 1.8)
    f.circ(cx, cy - R, 8, RD, INK, 1.3); f.text(cx + 16, cy - R + 4, 'P', 14, 'start', True, italic=True)
    f.circ(cx, cy + R, 8, BL, INK, 1.3); f.text(cx + 16, cy + R + 4, 'Q', 14, 'start', True, italic=True)
    return f.svg()


def ucm_stmts(r, ccw):
    """그림(점 A~D)이 있는 문항용 문장 후보 목록 [(문장, 참거짓, 풀이문, 그룹)]."""
    out = []
    s = 1 if ccw else -1
    def vdir(nm):
        th = math.radians(PTS[nm]); return (round(-math.sin(th) * s), round(math.cos(th) * s))
    nm = r.choice('ABCD'); words = list(VEL_WORD.values()); true_w = VEL_WORD[vdir(nm)]
    claim_true = r.random() < .5
    cw = true_w if claim_true else r.choice([w for w in words if w != true_w])
    out.append(('%s 에서 물체의 속도의 방향은 %s이다.' % (nm, cw), cw == true_w, '속도는 원의 접선 방향이고 운동 방향은 %s 방향이므로 %s 에서 속도의 방향은 %s이다.' % ('시계 반대' if ccw else '시계', nm, true_w), 'vdir'))
    a_, b_ = r.sample('ABCD', 2)
    out.append(('%s 와 %s 에서 물체의 속력은 같다.' % (a_, b_), True, '등속 원운동이므로 속력은 일정하다.', 'speed'))
    out.append(('%s 와 %s 에서 물체의 속도는 같다.' % (a_, b_), False, '속력은 같지만 속도의 방향이 서로 다르므로 속도는 같지 않다.', 'speed'))
    out.append(('%s 와 %s 에서 물체의 가속도의 크기는 같다.' % (a_, b_), True, '구심 가속도의 크기는 v²/r 로 일정하다.', 'acc'))
    out.append(('%s 와 %s 에서 물체의 가속도는 같다.' % (a_, b_), False, '크기는 같지만 방향이 각각 원의 중심을 향해 서로 다르므로 가속도는 같지 않다.', 'acc'))
    nm2 = r.choice('ABCD')
    out.append(('%s 에서 물체의 가속도의 방향은 원의 중심 O 를 향한다.' % nm2, True, '등속 원운동의 가속도는 항상 중심 방향이다.', 'accdir'))
    out.append(('%s 에서 물체의 가속도의 방향은 속도의 방향과 같다.' % nm2, False, '가속도는 중심을 향하고 속도는 접선 방향이므로 서로 수직이다.', 'accdir'))
    out.append(('%s 에서 줄이 끊어지면 물체는 중심 O 방향으로 날아간다.' % nm2, False, '끊어지면 속도 방향인 접선 방향으로 등속 직선 운동한다.', 'cut'))
    out.append(('%s 에서 물체에 작용하는 알짜힘의 방향은 속도의 방향과 수직이다.' % nm2, True, '알짜힘(구심력)은 중심 방향이고 속도는 접선 방향이다.', 'force'))
    out.append(('%s 에서 %s 까지 평균 속도의 크기는 평균 속력과 같다.' % (a_, b_), False, '이동한 경로(원호)의 길이가 변위의 크기보다 길므로 평균 속력이 평균 속도의 크기보다 크다.', 'avg'))
    return out


UCM_TXT = [
    ('등속 원운동하는 물체의 속력은 일정하다.', True, '속력은 변하지 않는다.', 'speed'),
    ('등속 원운동하는 물체의 속도는 일정하다.', False, '속도의 방향이 계속 변하므로 속도는 일정하지 않다.', 'speed'),
    ('등속 원운동하는 물체의 가속도의 방향은 원의 중심을 향한다.', True, '구심 가속도이다.', 'accdir'),
    ('등속 원운동하는 물체의 가속도는 0이다.', False, '속도의 방향이 변하므로 가속도가 있다.', 'a0'),
    ('등속 원운동하는 물체에 작용하는 알짜힘의 방향은 운동 방향과 수직이다.', True, '알짜힘은 중심 방향이고 속도는 접선 방향이다.', 'force'),
    ('등속 원운동하는 물체에는 운동 방향으로 알짜힘이 작용한다.', False, '운동 방향의 알짜힘이 있으면 속력이 변한다. 알짜힘은 중심 방향이다.', 'force'),
    ('속력이 일정하므로 등속 원운동하는 물체에 작용하는 알짜힘은 0이다.', False, '속도의 방향이 변하므로 구심력(알짜힘)이 필요하다.', 'force0'),
    ('등속 원운동은 가속도가 일정한 등가속도 운동이다.', False, '가속도의 크기는 일정하지만 방향이 계속 변하므로 등가속도 운동이 아니다.', 'eqa'),
    ('구심력은 물체의 속력을 변화시키지 않고 운동 방향만 바꾼다.', True, '구심력은 속도에 수직이므로 방향만 바꾼다.', 'dirnot'),
    ('한 바퀴 도는 동안 물체의 평균 속도는 0이다.', True, '출발점으로 돌아오므로 변위가 0이다.', 'avg'),
    ('한 바퀴 도는 동안 물체가 이동한 거리는 0이다.', False, '이동 거리는 원둘레 2πr 이다(변위가 0).', 'avg'),
    ('같은 속력으로 도는 물체의 반지름이 커지면 구심 가속도는 커진다.', False, 'a = v²/r 이므로 반지름이 커지면 구심 가속도는 작아진다.', 'rdep'),
    ('같은 각속도로 도는 두 물체 중 반지름이 큰 물체의 속력이 더 크다.', True, 'v = rω 이므로 반지름에 비례한다.', 'rdep'),
    ('주기가 길수록 각속도는 작다.', True, 'ω = 2π/T 이다.', 'wT'),
    ('주기가 길수록 진동수는 크다.', False, 'f = 1/T 이므로 주기가 길수록 진동수는 작다.', 'wT'),
    ('구심력은 중력, 장력 등과는 별도로 물체에 추가로 작용하는 새로운 힘이다.', False, '구심력은 실제로 작용하는 힘들의 합력(알짜힘)을 중심 방향으로 나타낸 이름이다.', 'fc'),
    ('줄에 매달려 원운동하는 물체의 줄이 끊어지면 물체는 접선 방향으로 날아간다.', True, '관성에 의해 속도 방향으로 등속 직선 운동한다.', 'cut'),
    ('줄에 매달려 원운동하는 물체의 줄이 끊어지면 물체는 중심 방향으로 날아간다.', False, '구심력이 사라지면 접선 방향으로 직진한다.', 'cut'),
    ('구심 가속도의 크기는 질량에 비례한다.', False, 'a = v²/r 이므로 질량과 무관하다(구심력이 질량에 비례한다).', 'mass'),
    ('질량이 큰 물체일수록 같은 조건에서 필요한 구심력이 크다.', True, 'F = mv²/r 이므로 질량에 비례한다.', 'mass'),
    ('등속 원운동하는 물체의 운동 에너지(속력)는 변하지 않는다.', True, '속력이 일정하다.', 'speed'),
    ('같은 속력으로 도는 물체는 반지름이 클수록 주기가 길다.', True, 'T = 2πr/v 이므로 반지름에 비례한다.', 'T'),
]

VERT = [
    ('Q 에서 줄이 물체를 당기는 힘의 크기는 물체의 무게 mg 보다 크다.', True, '최저점에서는 T - mg = mv²/r 이므로 T = mg + mv²/r > mg 이다.', 'Tq'),
    ('Q 에서 물체에 작용하는 알짜힘의 방향은 위쪽(중심 방향)이다.', True, '최저점에서 구심력은 위쪽(중심 O 방향)이다.', 'netq'),
    ('P 에서 물체에 작용하는 알짜힘의 방향은 아래쪽(중심 방향)이다.', True, '최고점에서 중심 O 는 아래쪽이므로 구심력은 아래쪽이다.', 'netp'),
    ('속력이 일정할 때 줄의 장력은 P 에서가 Q 에서보다 크다.', False, '최고점에서 T = mv²/r - mg, 최저점에서 T = mv²/r + mg 이므로 Q 에서가 더 크다.', 'tcmp'),
    ('속력이 일정할 때 줄의 장력은 Q 에서가 P 에서보다 크다.', True, '최저점에서는 T_Q = mv²/r + mg, 최고점에서는 T_P = mv²/r - mg 이므로 Q 에서 장력이 더 크다.', 'tcmp'),
    ('P 에서 줄이 물체를 당기는 힘의 크기는 구심력의 크기와 같다.', False, '최고점에서는 장력과 중력이 모두 아래쪽이므로 T + mg = mv²/r 이다. 구심력은 T 보다 크다.', 'Tp'),
    ('Q 에서 물체에 작용하는 중력은 구심력의 방향과 같다.', False, '중력은 아래쪽, 구심력은 위쪽(중심 방향)이다.', 'gq'),
    ('P 에서 물체에 작용하는 중력은 구심력의 방향과 같다.', True, '최고점에서 중력과 구심력 모두 아래쪽(중심 방향)이다.', 'gp'),
    ('Q 에서 물체의 속도의 방향은 수평이다.', True, '원운동의 속도는 접선 방향이며 최저점의 접선은 수평이다.', 'vq'),
    ('Q 에서 물체의 가속도는 0이다.', False, '구심 가속도 v²/r 가 있다.', 'aq'),
]


@T('ph041')
def ucm_bogi(r, k):
    """등속 원운동의 속도·가속도·힘 방향(<보기>)."""
    form = r.choice(['fig', 'fig', 'fig', 'text', 'text', 'vert', 'vert'])
    if form == 'text':
        sel = r.sample(UCM_TXT, 3)
        if len({s[3] for s in sel}) < 3: return None
        return bogi('등속 원운동에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', [(s[0], s[1], s[2]) for s in sel], r=r, ask='', lv='하', fam='b',
                    core='등속 원운동에서 속력은 일정하고 속도의 방향은 변하며, 가속도와 알짜힘은 항상 중심을 향한다.', point='속력과 속도, 가속도와 힘의 방향을 구분한다.')
    if form == 'fig':
        ccw = r.random() < 0.5
        fig = ucm_fig(ccw)
        cand = ucm_stmts(r, ccw)
        r.shuffle(cand)
        sel, used = [], set()
        for c in cand:
            if c[3] in used: continue
            used.add(c[3]); sel.append(c)
            if len(sel) == 3: break
        if len(sel) < 3: return None
        intro = '그림은 점 O 를 중심으로 %s 방향으로 일정한 속력으로 원운동하는 물체의 원궤도와 궤도 위의 네 점 A, B, C, D 를 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 그림에서 위쪽을 위로 한다.)' % ('시계 반대' if ccw else '시계')
        return bogi(intro, [(s[0], s[1], s[2]) for s in sel], r=r, pre=FIG(fig, '50%'), ask='', lv='중', fam='a',
                    core='등속 원운동에서 속도는 접선 방향(운동 방향), 가속도와 알짜힘은 중심 방향이며 속력은 일정하다.', point='그림의 점에서 속도 방향을 판단하고 속도와 속력을 구분한다.')
    sel = r.sample(VERT, 3)
    if len({s[3] for s in sel}) < 3: return None
    if {s[3] for s in sel} & {'tcmp'} and sum(1 for s in sel if s[3] == 'tcmp') > 1: return None
    fig = vert_fig()
    intro = '그림은 연직면에서 질량 m 인 물체가 길이가 일정한 줄에 매달려 점 O 를 중심으로 일정한 속력으로 원운동하는 것을 나타낸 것이다. P 는 최고점, Q 는 최저점이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)'
    return bogi(intro, [(s[0], s[1], s[2]) for s in sel], r=r, pre=FIG(fig, '46%'), ask='', lv='상', fam='c',
                core='연직 원운동에서 구심력은 장력과 중력의 합력의 중심 방향 성분이다. 최저점에서 T = mg + mv²/r, 최고점에서 T = mv²/r - mg 이다.', point='최고점과 최저점에서 구심력을 이루는 힘을 구분한다.')
