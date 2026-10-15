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
        f.text(mx + 12 * math.sin(th) * (1 if True else -1) - 4, my + 12 * math.cos(th) + 4, rl, 13, 'middle', True)
    s = 1 if ccw else -1
    tx, ty = -math.sin(th) * s, -math.cos(th) * s  # 화면 좌표 방향
    if vl is not None:
        f.arrow(px, py, px + 44 * tx, py + 44 * ty, RD, 2.4)
        f.text(px + 56 * tx + (6 if tx > 0.3 else -6 if tx < -0.3 else 0), py + 54 * ty + 4, vl, 13, 'start' if tx > 0.3 else 'end' if tx < -0.3 else 'middle', True, RD, True)
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
    f.arc = None
    f.text(cx - 10, cy + 16, 'O', 13, bold=True, italic=True)
    f.o.append('<path d="M %s %s A 40 40 0 0 1 %s %s" fill="none" stroke="%s" stroke-width="1.4"/>' % (cx + 0, cy - 40, cx + 40, cy, GR))
    f.arrow(cx + 38, cy - 12, cx + 42, cy - 6, GR, 1.4)
    f.text(cx + 100, cy + 6, '회전', 12, 'start', c=GR)
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
    body = PP('그림은 반지름 %s인 원 위를 일정한 속력으로 도는 %s을(를) 나타낸 것이다. 주기가 %s일 때 %s의 속력은? %s' % (U(rr, 'm'), ob, U(T_, 's'), ob, cond)) + FIG(f.svg(), '50%')
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
        p = Plot(280, 190, rm * 1.25, am * 1.25, ml=48, mr=18, mt=16, mb=30)
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
    body = PP('그림은 반지름 %s인 원 위를 %s의 속력으로 등속 원운동하는 %s의 모습을 나타낸 것이다. %s의 가속도(a)의 크기는?' % (U(rr, 'm'), U(v, 'm/s'), ob, ob)) + FIG(f.svg(), '50%')
    wr = wl(a, [v / rr, v * rr, v * v * rr, v * v / (2 * rr), 0.5 * v * v / rr * 2, a + 1], 'm/s²')
    return mc(body, ans(a, 'm/s²'), wr, r=r, lv='하', fam='g', steps=['a = v²/r = %s² / %s = %s m/s², 방향은 원의 중심 O 를 향한다.' % (num(v), num(rr), num(a))],
              core='등속 원운동의 가속도는 크기 v²/r, 방향은 중심 방향이다.', point='그림의 값을 읽어 구심 가속도를 구한다.')
