# -*- coding: utf-8 -*-
"""Ⅰ-B 뉴턴 운동 법칙 — ph009 ~ ph018."""
from phlib import *
import math
from math import gcd
from fractions import Fraction

G = 10
OBJ = ['상자', '나무 블록', '수레', '썰매', '벽돌', '쇳덩이']
SINV = {30: .5, 37: .6, 45: math.sqrt(2) / 2, 53: .8, 60: math.sqrt(3) / 2}
COSV = {30: math.sqrt(3) / 2, 37: .8, 45: math.sqrt(2) / 2, 53: .6, 60: .5}
SINS = {30: '1/2', 37: '3/5', 45: '√2/2', 53: '4/5', 60: '√3/2'}
COSS = {30: '√3/2', 37: '4/5', 45: '√2/2', 53: '3/5', 60: '1/2'}


def isnice(x, nd=2):
    return abs(x * 10 ** nd - round(x * 10 ** nd)) < 1e-7


def WR(right, cands, unit='', nd=2):
    out, seen = [], {round(float(right), 6)}
    def add(c):
        if c is None or c < 0 or not isnice(c, nd): return
        key = round(float(c), 6)
        if key in seen: return
        seen.add(key); out.append(num(c, nd) + (' ' + unit if unit else ''))
    for c in cands: add(c)
    for c in (right * 2, right / 2, right + 1, right + 2, right - 1, right * 1.5, right + 5, right * 3, right + 10, right / 4):
        if len(out) >= 4: break
        add(c)
    return out


def lab(f, x, y, s, c=INK, anchor='middle', size=12.5):
    f.text(x, y, s, size, anchor, True, c)


def arc(f, cx, cy, rr, a1, a2, c=GR, sw=1.3):
    p1 = (cx + rr * math.cos(math.radians(a1)), cy - rr * math.sin(math.radians(a1)))
    p2 = (cx + rr * math.cos(math.radians(a2)), cy - rr * math.sin(math.radians(a2)))
    f.path('M %s %s A %s %s 0 0 0 %s %s' % (Fig._n(p1[0]), Fig._n(p1[1]), Fig._n(rr), Fig._n(rr), Fig._n(p2[0]), Fig._n(p2[1])), 'none', c, sw)


def fr(x):
    x = Fraction(x).limit_denominator(1000)
    return str(x.numerator) if x.denominator == 1 else '%d/%d' % (x.numerator, x.denominator)


def pick3(S, r):
    groups = {}
    for s in S: groups.setdefault(s[0], []).append(s[1:])
    gs = r.sample(sorted(groups), 3)
    return [r.choice(groups[g]) for g in gs]


def block(f, x, y, w, h, l1, l2=None, fill='#cfe2f7'):
    f.rect(x, y, w, h, fill, INK, 1.6)
    if l2 is None:
        f.text(x + w / 2, y + h / 2 + 4.5, l1, 13, 'middle', True)
    else:
        f.text(x + w / 2, y + h / 2 - 2, l1, 13, 'middle', True)
        f.text(x + w / 2, y + h / 2 + 13, l2, 12, 'middle', False, GR)


def floor(f, x1, x2, y):
    f.line(x1, y, x2, y, GR, 1.8)
    for i in range(int(x1), int(x2), 8):
        f.line(i, y, i - 5, y + 6, GR, 1)


FILLS = ['#cfe2f7', '#fbe3c3', '#d5f0e0', '#e6dcf7']


def fig_row(items, links, fmode='right', Ftxt='F', w=330):
    """items: [(문자, '2 kg'), ...] 왼쪽→오른쪽. links: 사이 연결 'rope'|'touch'."""
    f = Fig(w, 130)
    bw, bh, gap = 52, 44, 36
    total = sum(bw for _ in items) + sum(gap if l == 'rope' else 0 for l in links)
    x = 40 if fmode != 'left' else 80
    fy = 100
    floor(f, 8, w - 8, fy)
    xs = []
    for i, (a, b) in enumerate(items):
        xs.append(x)
        block(f, x, fy - bh, bw, bh, a, b, FILLS[i % 4])
        if i < len(links):
            if links[i] == 'rope':
                f.line(x + bw, fy - bh / 2, x + bw + gap, fy - bh / 2, INK, 2)
                x += bw + gap
            else:
                x += bw
    last = xs[-1] + bw
    if fmode == 'right':
        f.arrow(last, fy - bh / 2, last + 58, fy - bh / 2, RD, 3)
        lab(f, last + 30, fy - bh / 2 - 8, Ftxt, RD, 'middle', 14)
    elif fmode == 'left':
        f.arrow(xs[0], fy - bh / 2, xs[0] - 58, fy - bh / 2, RD, 3)
        lab(f, xs[0] - 30, fy - bh / 2 - 8, Ftxt, RD, 'middle', 14)
    else:  # push: 첫 물체를 오른쪽으로 민다
        f.arrow(xs[0] - 58, fy - bh / 2, xs[0], fy - bh / 2, RD, 3)
        lab(f, xs[0] - 30, fy - bh / 2 - 8, Ftxt, RD, 'middle', 14)
    return f.svg()


def fig_forces(m, rights, lefts):
    f = Fig(300, 130)
    bx, bw, bh, fy = 120, 60, 46, 104
    floor(f, 8, 292, fy)
    block(f, bx, fy - bh, bw, bh, '%d kg' % m)
    sc = 3.2
    for side, lst in ((1, rights), (-1, lefts)):
        for i, (nm, v) in enumerate(lst):
            y = fy - bh / 2 + (i - (len(lst) - 1) / 2) * 18
            L = min(sc * v, 100)
            if side == 1:
                f.arrow(bx + bw, y, bx + bw + L, y, RD if nm[0] != 'f' else GN, 2.6)
                lab(f, bx + bw + L + 5, y + 4, '%s=%s N' % (nm, num(v)), RD if nm[0] != 'f' else GN, 'start', 12)
            else:
                f.arrow(bx, y, bx - L, y, BL if nm[0] != 'f' else GN, 2.6)
                lab(f, bx - L - 5, y + 4, '%s=%s N' % (nm, num(v)), BL if nm[0] != 'f' else GN, 'end', 12)
    return f.svg()


def fig_atwood(la, lb, lb2=None, lb3=None):
    f = Fig(300, 200)
    f.line(90, 14, 210, 14, GR, 2)
    for i in range(0, 120, 8): f.line(90 + i, 14, 95 + i, 8, GR, 1)
    cx, cy, R = 150, 62, 20
    f.line(cx, 14, cx, cy, INK, 1.8)
    f.circ(cx, cy, R, '#fff', INK, 1.8)
    f.circ(cx, cy, 2.5, INK, INK)
    yb = 130
    f.line(cx - R, cy, cx - R, yb, INK, 1.8)
    f.line(cx + R, cy, cx + R, yb, INK, 1.8)
    block(f, cx - R - 28, yb, 56, 42, la, lb, FILLS[0])
    block(f, cx + R - 28, yb, 56, 42, lb2, lb3, FILLS[1])
    return f.svg()


def fig_table(M_l1, M_l2, m_l1, m_l2):
    f = Fig(300, 205)
    ty = 100
    f.rect(12, ty, 196, 10, '#e9dcc3', INK, 1.5)
    f.line(30, ty + 10, 30, 196, INK, 1.4); f.line(190, ty + 10, 190, 196, INK, 1.4)
    block(f, 60, ty - 42, 56, 42, M_l1, M_l2, FILLS[0])
    px, py, R = 224, ty - 34, 8
    f.line(208, ty, px, py + R, GR, 1.6)
    f.line(116, ty - 21, px, ty - 21 - 0, INK, 1.8) if False else None
    rope_y = py - R
    f.line(116, ty - 21, 116, ty - 21)
    f.line(116, ty - 21, px, ty - 21, INK, 1.8)
    return f


def fig_table_full(Ml1, Ml2, ml1, ml2):
    f = Fig(300, 205)
    ty = 112
    bh = 42
    f.rect(12, ty, 200, 10, '#e9dcc3', INK, 1.5)
    f.line(30, ty + 10, 30, 198, INK, 1.4); f.line(192, ty + 10, 192, 198, INK, 1.4)
    block(f, 60, ty - bh, 56, bh, Ml1, Ml2, FILLS[0])
    ry = ty - bh / 2
    R = 8
    px, py = 226, ry + R
    f.line(116, ry, px, ry, INK, 1.8)
    f.path('M %s %s A %s %s 0 0 1 %s %s' % (px, ry, R, R, px + R, py), 'none', INK, 1.8)
    f.line(px + R, py, px + R, py + 52, INK, 1.8)
    f.circ(px, py, R, '#fff', INK, 1.6)
    f.line(212, ty, px - 4, py + 6, GR, 1.6)
    block(f, px + R - 26, py + 52, 52, 40, ml1, ml2, FILLS[1])
    return f.svg()


def fig_incline(th, label=None, hlabel=None, v0=False, w=290, h=175):
    f = Fig(w, h)
    x0, y0 = 20, h - 16
    tn = math.tan(math.radians(th))
    hh = min(h - 40, (w - 70) * tn)
    x1 = x0 + hh / tn
    y1 = y0 - hh
    f.poly([(x0, y0), (x1, y0), (x1, y1)], '#f1f4f8', INK, 1.8)
    t = 0.5
    P0 = (x0 + t * (x1 - x0), y0 - t * hh)
    n = Fig._n
    f.o.append('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="34" height="24" fill="#cfe2f7" stroke="%s" stroke-width="1.6"/></g>' % (n(-th), n(P0[0]), n(P0[1]), n(P0[0] - 17), n(P0[1] - 24), INK))
    arc(f, x0, y0, 36, 0, th)
    lab(f, x0 + 54, y0 - 7, '%d°' % th, GR)
    if label:
        mx, my = (x0 + x1) / 2 - 16 * math.sin(math.radians(th)) - 14, (y0 + y1) / 2 - 16 * math.cos(math.radians(th)) - 2
        f.o.append('<text x="%s" y="%s" font-size="12.5" text-anchor="middle" font-weight="700" fill="%s" font-family="%s" transform="rotate(%s %s %s)">%s</text>' % (n(mx - 18), n(my - 22), GR, FONT, n(-th), n(mx - 18), n(my - 22), esc(label)))
    if hlabel:
        lab(f, x1 + 6, (y0 + y1) / 2 + 4, hlabel, GR, 'start')
    if v0:
        ax, ay = P0[0] - 8 * math.sin(math.radians(th)) * 5 - 0, P0[1] - 8 * math.cos(math.radians(th)) * 5
        sx, sy = P0[0] + (-40 * math.sin(math.radians(th))), P0[1] + (-40 * math.cos(math.radians(th)))
        f.arrow(sx, sy, sx + 40 * math.cos(math.radians(th)), sy - 40 * math.sin(math.radians(th)), RD, 2.6)
        lab(f, sx + 40 * math.cos(math.radians(th)) + 4, sy - 40 * math.sin(math.radians(th)) - 4, 'v0', RD, 'start')
    return f.svg()


def fig_incline_pulley(th, ta='A', tb='B'):
    f = Fig(300, 190)
    R = 7
    x0, y0 = 12, 172
    hh = min(105, 190 * math.tan(math.radians(th)))
    x1, y1 = x0 + hh / math.tan(math.radians(th)), y0 - hh
    f.poly([(x0, y0), (x1, y0), (x1, y1)], '#f1f4f8', INK, 1.8)
    n = (-math.sin(math.radians(th)), -math.cos(math.radians(th)))
    u = (math.cos(math.radians(th)), -math.sin(math.radians(th)))
    t = 0.42
    P0 = (x0 + t * (x1 - x0), y0 - t * hh)
    N = Fig._n
    f.o.append('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="38" height="28" fill="#cfe2f7" stroke="%s" stroke-width="1.6"/><text x="%s" y="%s" font-size="12.5" text-anchor="middle" font-weight="700" fill="%s" font-family="%s">%s</text></g>' % (N(-th), N(P0[0]), N(P0[1]), N(P0[0] - 19), N(P0[1] - 28), INK, N(P0[0]), N(P0[1] - 9.5), INK, FONT, ta))
    A = (P0[0] + n[0] * 14, P0[1] + n[1] * 14)
    C = (x1 + n[0] * R + 24 * u[0], y1 + n[1] * R + 24 * u[1])
    T1 = (C[0] + n[0] * R, C[1] + n[1] * R)
    T2 = (C[0] + R, C[1])
    f.line(x1, y1, C[0], C[1], GR, 1.6)
    f.line(A[0], A[1], T1[0], T1[1], INK, 1.8)
    f.path('M %s %s A %s %s 0 0 1 %s %s' % (N(T1[0]), N(T1[1]), R, R, N(T2[0]), N(T2[1])), 'none', INK, 1.8)
    f.line(T2[0], T2[1], T2[0], T2[1] + 52, INK, 1.8)
    f.rect(T2[0] - 17, T2[1] + 52, 34, 28, '#fbe3c3', INK, 1.6)
    f.text(T2[0], T2[1] + 71, tb, 12.5, 'middle', True)
    f.circ(C[0], C[1], R, '#fff', INK, 1.6)
    arc(f, x0, y0, 36, 0, th)
    lab(f, x0 + 52, y0 - 8, '%d°' % th, GR)
    return f.svg()


def ticks(vmax, step):
    return [round(i * step, 4) for i in range(0, int(round(vmax / step)) + 1)]


# ================================================================= ph009
@T('ph009')
def fma(r, k):
    fam = r.choice(['a'] * 3 + ['b'] * 3 + ['c'] * 3 + ['d'] * 3 + ['e'] * 2 + ['f'] * 2)
    obj = r.choice(OBJ)
    if fam == 'a':
        m, a = r.randint(1, 12), r.randint(1, 9)
        F = m * a
        ask = r.choice(['a', 'F', 'm'])
        if ask == 'a':
            body = P('수평면 위에서 질량이 %d kg인 %s에 수평 방향으로 크기가 %d N인 알짜힘이 작용한다. 가속도의 크기는?' % (m, obj, F))
            wr = WR(a, [m / F, F + m, F - m, F * m / 2, a + 1, a * 2], 'm/s²')
            return mc(body, U(a, 'm/s²'), wr, r=r, lv='하', fam='a', steps=['F = ma 이므로 a = F ÷ m = %d ÷ %d = %d m/s²' % (F, m, a)], core='물체의 가속도는 알짜힘에 비례하고 질량에 반비례한다(F = ma).', point='알짜힘과 질량으로 가속도를 구한다.')
        if ask == 'F':
            body = P('질량이 %d kg인 %s가 일직선 위에서 %d m/s²의 가속도로 운동한다. 이 물체에 작용하는 알짜힘의 크기는?' % (m, obj, a))
            wr = WR(F, [m + a, m / a if m % a == 0 else None, F / 2, F + m, F - a, abs(m - a)], 'N')
            return mc(body, U(F, 'N'), wr, r=r, lv='하', fam='a', steps=['F = ma = %d × %d = %d N' % (m, a, F)], core='알짜힘은 질량과 가속도의 곱이다(F = ma).', point='가속도로부터 알짜힘을 구한다.')
        body = P('%s에 크기가 %d N인 알짜힘이 작용하여 %d m/s²의 가속도가 생겼다. 이 물체의 질량은?' % (obj, F, a))
        wr = WR(m, [a, F * a if False else None, F - a, F + a, m + 2, m * 2], 'kg')
        return mc(body, U(m, 'kg'), wr, r=r, lv='하', fam='a', steps=['F = ma 이므로 m = F ÷ a = %d ÷ %d = %d kg' % (F, a, m)], core='F = ma 에서 질량 m = F/a 이다.', point='알짜힘과 가속도로 질량을 구한다.')
    if fam == 'b':
        m = r.choice([2, 3, 4, 5, 6, 8])
        nr = r.choice([1, 1, 2])
        rights = [('F%s' % sub(i + 1), r.randint(2, 20)) for i in range(nr)]
        lefts = [('F%s' % sub(nr + 1), r.randint(2, 20))] if r.random() < .6 else [('f', r.randint(2, 12))]
        net = sum(v for _, v in rights) - sum(v for _, v in lefts)
        if net == 0 or not isnice(abs(net) / m, 2): return None
        a = abs(net) / m
        direc = '오른쪽' if net > 0 else '왼쪽'
        assert abs(m * a - abs(net)) < 1e-9
        tx = ', '.join('%s의 크기는 %d N' % (n.replace('f', '마찰력 f') if n == 'f' else n, v) for n, v in rights + lefts)
        body = P('그림은 수평면 위에서 질량 %d kg인 물체에 수평 방향의 힘이 작용하는 모습을 나타낸 것이다. 물체의 가속도의 크기와 방향을 옳게 짝지은 것은?' % m) + FIG(fig_forces(m, rights, lefts), '66%')
        other = '왼쪽' if direc == '오른쪽' else '오른쪽'
        tot = sum(v for _, v in rights) + sum(v for _, v in lefts)
        right = '%s m/s², %s' % (num(a), direc)
        wrongs = ['%s m/s², %s' % (num(a), other), '%s m/s², %s' % (num(tot / m), direc), '%s m/s², %s' % (num(abs(net) / m + 1), direc), '%s m/s², %s' % (num(max(v for _, v in rights + lefts) / m), direc), '%s m/s², %s' % (num(abs(net) / m * 2), other)]
        wrongs = [w for w in wrongs if isnice(float(w.split(' ')[0])) and w != right]
        return mc(body, right, wrongs, r=r, lv='중', fam='b', sort='shuf',
                  steps=['오른쪽을 +로 하면 알짜힘 = %s - %s = %d N 이다.' % (' + '.join(str(v) for _, v in rights), ' - '.join(str(v) for _, v in lefts) if False else str(sum(v for _, v in lefts)), net),
                         'a = 알짜힘 ÷ m = %d ÷ %d = %s m/s², 방향은 알짜힘 방향인 %s이다.' % (abs(net), m, num(a), direc)],
                  core='가속도의 방향은 알짜힘의 방향과 같고 크기는 알짜힘/질량이다.', point='반대 방향의 힘은 부호를 달리해 합한 뒤 F = ma 를 적용한다.')
    if fam == 'c':
        mA, aA = r.randint(1, 6), r.randint(1, 6)
        FA = mA * aA
        mB, aB = r.randint(1, 8), r.randint(1, 6)
        FB = mB * aB
        mC, aC = r.randint(1, 8), r.randint(1, 6)
        FC = mC * aC
        if len({aA, aB, aC}) < 3 or len({mA, mB, mC}) < 3: return None
        ask = r.choice(['aB', 'mC', 'FA'])
        rows = [['A', mA, FA, aA], ['B', mB, FB, aB], ['C', mC, FC, aC]]
        if ask == 'aB':
            rows[1][3] = '①'; right, unit = aB, 'm/s²'; ttl = '가속도 ①의 값은?'
            wr = WR(aB, [FB, mB, FB - mB, FB + mB, aB + 1, aB * 2], unit)
            st = ['물체 B : F = ma 에서 a = F ÷ m = %d ÷ %d = %d m/s²' % (FB, mB, aB)]
        elif ask == 'mC':
            rows[2][1] = '①'; right, unit = mC, 'kg'; ttl = '질량 ①의 값은?'
            wr = WR(mC, [FC, aC, FC - aC, FC + aC, mC + 1, mC * 2], unit)
            st = ['물체 C : m = F ÷ a = %d ÷ %d = %d kg' % (FC, aC, mC)]
        else:
            rows[0][2] = '①'; right, unit = FA, 'N'; ttl = '알짜힘 ①의 값은?'
            wr = WR(FA, [mA + aA, mA * aA * 2, aA, mA, FA + 2, FA - 1], unit)
            st = ['물체 A : F = ma = %d × %d = %d N' % (mA, aA, FA)]
        body = P('표는 수평면에서 운동하는 물체 A, B, C의 질량, 물체에 작용하는 알짜힘, 가속도를 나타낸 것이다. %s' % ttl) + table(['물체', '질량(kg)', '알짜힘(N)', '가속도(m/s²)'], rows)
        return mc(body, U(right, unit), wr, r=r, lv='중', fam='c', steps=st, core='각 물체에서 알짜힘 = 질량 × 가속도 관계가 성립한다.', point='표의 두 값으로 나머지 하나를 구한다.')
    if fam == 'd':
        m, a, t = r.randint(1, 8), r.randint(1, 6), r.randint(2, 6)
        F = m * a
        ask = r.choice(['v', 's', 'v'])
        if ask == 'v':
            v = a * t
            body = P('마찰이 없는 수평면에서 정지해 있던 질량 %d kg인 물체에 수평 방향으로 일정한 힘 %d N을 %d초 동안 작용했다. 힘을 작용한 %d초 후 물체의 속력은?' % (m, F, t, t))
            wr = WR(v, [F * t, F / m, v / 2, a + t, F, m * t], 'm/s')
            assert abs(F * t / m - v) < 1e-9
            return mc(body, U(v, 'm/s'), wr, r=r, lv='중', fam='d', steps=['가속도 a = F ÷ m = %d ÷ %d = %d m/s²' % (F, m, a), '정지에서 출발했으므로 v = at = %d × %d = %d m/s' % (a, t, v)], core='일정한 알짜힘이 작용하면 등가속도 운동을 하며 v = at 이다.', point='F = ma 로 가속도를 구한 뒤 운동 공식에 적용한다.')
        s = a * t * t / 2
        body = P('마찰이 없는 수평면에서 정지해 있던 질량 %d kg인 물체에 수평 방향으로 일정한 힘 %d N을 작용했다. 힘을 작용한 후 %d초 동안 물체가 이동한 거리는?' % (m, F, t))
        wr = WR(s, [a * t * t, a * t, F * t, s / 2, s + t, a * t / 2], 'm')
        return mc(body, U(s, 'm'), wr, r=r, lv='상', fam='d', steps=['a = F ÷ m = %d ÷ %d = %d m/s²' % (F, m, a), 's = ½at² = ½ × %d × %d² = %s m' % (a, t, num(s))], core='정지에서 출발한 등가속도 운동에서 s = ½at² 이다.', point='가속도를 먼저 구하고 변위 공식을 쓴다.')
    if fam == 'e':
        p = r.choice([Fraction(1, 2), 2, 3, Fraction(3, 2), 4])
        q = r.choice([Fraction(1, 2), 2, 3, 4, Fraction(3, 2)])
        res = Fraction(q) / Fraction(p)
        if res == 1: return None
        ptxt = {Fraction(1, 2): '1/2배', 2: '2배', 3: '3배', Fraction(3, 2): '3/2배', 4: '4배'}
        body = P('어떤 물체에 알짜힘 F가 작용할 때 가속도의 크기가 a였다. 이 물체의 질량을 %s로, 알짜힘을 %s로 바꾸면 가속도의 크기는?' % (ptxt[p], ptxt[q]))
        cands = [Fraction(p) * q, Fraction(p) / q, Fraction(1) / (Fraction(p) * q), Fraction(p), Fraction(q), Fraction(p) + q, Fraction(q) - p if q > p else Fraction(p) - q]
        right = fr(res) + '배'
        wrongs = [fr(c) + '배' for c in cands if c > 0 and c != res]
        return mc(body, right, wrongs, r=r, lv='중', fam='e', sort='shuf', steps=['a = F/m 이므로 a\' = (%s F) ÷ (%s m) = %s × a' % (fr(q), fr(p), fr(res))], core='가속도는 알짜힘에 비례하고 질량에 반비례한다.', point='비례·반비례 관계를 한꺼번에 적용한다.')
    # f
    mode = r.choice(['mass', 'force'])
    if mode == 'mass':
        x, y = r.choice([(2, 3), (1, 2), (3, 4), (2, 5), (1, 3), (3, 5), (4, 5)])
        body = P('같은 크기의 알짜힘을 받아 운동하는 두 물체 A, B의 질량비가 m%s : m%s = %d : %d이다. 두 물체의 가속도의 크기의 비 a%s : a%s는?' % (sub('A'), sub('B'), x, y, sub('A'), sub('B')))
        right = '%d : %d' % (y, x)
        wrongs = ['%d : %d' % (x, y), '%d : %d' % (x * x, y * y), '%d : %d' % (y * y, x * x), '1 : 1', '%d : %d' % (x + y, abs(y - x) or 1)]
        return mc(body, right, wrongs, r=r, lv='하', fam='f', sort='shuf', steps=['알짜힘이 같으면 a = F/m 이므로 a%s : a%s = 1/m%s : 1/m%s' % (sub('A'), sub('B'), sub('A'), sub('B')), '= 1/%d : 1/%d = %d : %d' % (x, y, y, x)], core='알짜힘이 같으면 가속도는 질량에 반비례한다.', point='질량비를 뒤집어 가속도비를 구한다.')
    x, y = r.choice([(2, 3), (1, 2), (3, 4), (2, 5), (1, 3), (3, 5), (4, 5)])
    body = P('질량이 같은 두 물체 A, B에 각각 크기가 %d N, %d N인 알짜힘이 작용한다. 두 물체의 가속도의 크기의 비 a%s : a%s는?' % (x * 2, y * 2, sub('A'), sub('B')))
    right = '%d : %d' % (x, y)
    wrongs = ['%d : %d' % (y, x), '%d : %d' % (x * x, y * y), '%d : %d' % (y * y, x * x), '1 : 1', '%d : %d' % (x + y, abs(y - x) or 1)]
    return mc(body, right, wrongs, r=r, lv='하', fam='f', sort='shuf', steps=['질량이 같으면 a = F/m 에서 a는 F에 비례한다.', 'a%s : a%s = %d : %d = %d : %d' % (sub('A'), sub('B'), x * 2, y * 2, x, y)], core='질량이 같으면 가속도는 알짜힘에 비례한다.', point='같은 질량에서 힘의 비가 곧 가속도의 비이다.')


# ================================================================= ph010
def _aF_plot(lines, F0, xmax, ymax, ystep, pts, w=300, h=225):
    """lines: [(m, color, name)]. pts: 강조할 점 목록 [(x, y)]."""
    p = Plot(w, h, xmax, ymax, ml=46, mr=28, mt=18, mb=32)
    p.axes('F (N)', 'a (m/s²)', ticks(xmax, 2 if xmax > 6 else 1), ticks(ymax, ystep), grid=True)
    for m, c, nm in lines:
        xe = min(xmax, m * ymax * .96)
        p.pl([(0, 0), (xe, xe / m)], c, 2.6)
        lab(p, p.px(xe) + 2, p.py(xe / m) - 6, nm, c, 'end', 13)
    for (x, y) in pts:
        p.dash_to_axes(x, y)
        p.circ(p.px(x), p.py(y), 3.5, INK, INK)
    return p.svg()


@T('ph010')
def aF_graph(r, k):
    fam = r.choice(['a'] * 3 + ['b'] * 3 + ['c'] * 3 + ['d'] * 2 + ['e'] * 3)
    if fam == 'a':
        m = r.choice([1, 2, 4, 5, 0.5, 2.5])
        xmax = 10
        ymax = {1: 10, 2: 5, 4: 3, 5: 2, 0.5: 10, 2.5: 4}[m]
        if m == 0.5: ymax = 10; xmax = 6
        F0 = r.choice([2, 4, 6, 8]) if m != 0.5 else r.choice([2, 4])
        a0 = F0 / m
        step = 1 if ymax >= 4 else 0.5
        if a0 > ymax * .95 or abs(a0 / step - round(a0 / step)) > 1e-9 or F0 > xmax: return None
        if m == 0.5 and ymax > 10: return None
        body = P('그림은 마찰이 없는 수평면에서 물체 A에 작용하는 알짜힘 F에 따른 가속도 a를 나타낸 그래프이다. 물체 A의 질량은?') + FIG(_aF_plot([(m, RD, 'A')], F0, xmax, ymax, step, [(F0, a0)]), '66%')
        wr = WR(m, [F0, a0, F0 * a0, F0 + a0, m * 2, m + 1], 'kg')
        return mc(body, U(m, 'kg'), wr, r=r, lv='중', fam='a', steps=['그래프에서 F = %d N 일 때 a = %s m/s² 이다.' % (F0, num(a0)), '질량 m = F ÷ a = %d ÷ %s = %s kg (그래프 기울기의 역수)' % (F0, num(a0), num(m))], core='a-F 그래프의 기울기는 1/m 이므로 기울기가 클수록 질량이 작다.', point='그래프의 한 점에서 F와 a를 읽어 질량을 구한다.')
    if fam in ('b', 'e'):
        mA, mB = r.choice([(1, 2), (2, 4), (1, 4), (2, 1), (4, 2), (4, 1), (2, 5), (5, 2), (1, 5), (5, 1), (4, 5)]) if False else r.choice([(1, 2), (2, 4), (1, 4), (2, 1), (4, 2), (4, 1), (2.5, 5), (5, 2.5), (1, 5), (5, 1), (2, 5), (5, 2)])
        F0 = r.choice([2, 4, 6, 8, 10]) if True else 4
        xmax = 10
        amax = max(F0 / mA, F0 / mB)
        ymax = 5 if amax <= 5 else 10
        if F0 / min(mA, mB) > ymax * .96: return None
        aA, aB = F0 / mA, F0 / mB
        step = 1 if ymax >= 5 else 0.5
        if abs(aA - round(aA)) > 1e-9 or abs(aB - round(aB)) > 1e-9: return None
        if mA == mB: return None
        fig = FIG(_aF_plot([(mA, RD, 'A'), (mB, BL, 'B')], F0, xmax, ymax, step, [(F0, aA), (F0, aB)]), '66%')
        if fam == 'b':
            ask = r.choice(['ratio', 'mB', 'aB'])
            if ask == 'ratio':
                x, y = int(round(mA * 2)), int(round(mB * 2)); g = gcd(x, y); x, y = x // g, y // g
                body = P('그림은 마찰이 없는 수평면에서 물체 A, B에 작용하는 알짜힘 F에 따른 가속도 a를 나타낸 그래프이다. 두 물체의 질량비 m%s : m%s는?' % (sub('A'), sub('B'))) + fig
                right = '%d : %d' % (x, y)
                wrongs = ['%d : %d' % (y, x), '%d : %d' % (x * x, y * y), '%d : %d' % (y * y, x * x), '1 : 1', '%d : %d' % (x + 1, y + 1)]
                if x == y: return None
                return mc(body, right, wrongs, r=r, lv='중', fam='b', sort='shuf', steps=['F = %d N 일 때 a%s = %s m/s², a%s = %s m/s² 이다.' % (F0, sub('A'), num(aA), sub('B'), num(aB)), '같은 힘에서 m ∝ 1/a 이므로 m%s : m%s = a%s : a%s = %s : %s = %d : %d' % (sub('A'), sub('B'), sub('B'), sub('A'), num(aB), num(aA), x, y)], core='같은 힘에서 질량은 가속도에 반비례한다(기울기가 큰 쪽의 질량이 작다).', point='같은 F에서 두 가속도를 읽어 질량비를 구한다.')
            if ask == 'mB':
                body = P('그림은 마찰이 없는 수평면에서 물체 A, B에 작용하는 알짜힘 F에 따른 가속도 a를 나타낸 그래프이다. A의 질량이 %s kg일 때 B의 질량은?' % num(mA)) + fig
                wr = WR(mB, [mA, aA, aB, mA * 2, mB * 2, F0], 'kg')
                return mc(body, U(mB, 'kg'), wr, r=r, lv='중', fam='b', steps=['F = %d N 일 때 a%s = %s, a%s = %s m/s² 이다.' % (F0, sub('A'), num(aA), sub('B'), num(aB)), 'm%s = F ÷ a%s = %d ÷ %s = %s kg' % (sub('B'), sub('B'), F0, num(aB), num(mB))], core='a-F 그래프에서 m = F/a 이다.', point='그래프에서 읽은 값으로 질량을 구한다.')
            F2 = r.choice([4, 6, 8, 10])
            aB2 = F2 / mB
            if not isnice(aB2, 2) or F2 == F0: return None
            body = P('그림은 마찰이 없는 수평면에서 물체 A, B에 작용하는 알짜힘 F에 따른 가속도 a를 나타낸 그래프이다. B에 크기가 %d N인 알짜힘이 작용할 때 B의 가속도의 크기는?' % F2) + fig
            wr = WR(aB2, [F2 / mA, aB, aA, F2, aB2 * 2], 'm/s²')
            return mc(body, U(aB2, 'm/s²'), wr, r=r, lv='중', fam='b', steps=['그래프에서 B는 F = %d N 일 때 a = %s m/s² 이므로 m%s = %d ÷ %s = %s kg' % (F0, num(aB), sub('B'), F0, num(aB), num(mB)), 'F = %d N 일 때 a = %d ÷ %s = %s m/s²' % (F2, F2, num(mB), num(aB2))], core='a-F 그래프는 원점을 지나는 직선이며 기울기는 1/m 이다.', point='기울기로 질량을 구한 뒤 새로운 힘에서의 가속도를 구한다.')
        # e: <보기>
        big = 'A' if mA > mB else 'B'
        small = 'B' if big == 'A' else 'A'
        mbig, msmall = max(mA, mB), min(mA, mB)
        S = [
            ('g1', '질량은 %s가 %s보다 크다.' % (big, small), True, '같은 힘에서 가속도가 작은 %s의 질량이 더 크다.' % big),
            ('g1', '질량은 %s가 %s보다 크다.' % (small, big), False, '그래프에서 같은 힘일 때 가속도가 작은 %s의 질량이 더 크다.' % big),
            ('g2', 'A의 질량은 %s kg이다.' % num(mA), True, 'F = %d N 일 때 a = %s m/s² 이므로 m = %d ÷ %s = %s kg 이다.' % (F0, num(aA), F0, num(aA), num(mA))),
            ('g2', 'A의 질량은 %s kg이다.' % num(mA * 2), False, 'F = %d N, a = %s m/s² 이므로 m = %s kg 이다.' % (F0, num(aA), num(mA))),
            ('g3', 'B의 질량은 %s kg이다.' % num(mB), True, 'F = %d N 일 때 a = %s m/s² 이므로 m = %s kg 이다.' % (F0, num(aB), num(mB))),
            ('g3', 'B의 질량은 %s kg이다.' % num(mB + 1), False, 'F = %d N 일 때 a = %s m/s² 이므로 m = %s kg 이다.' % (F0, num(aB), num(mB))),
            ('g4', '그래프의 기울기는 질량에 비례한다.', False, '기울기 a/F = 1/m 이므로 기울기는 질량에 반비례한다.'),
            ('g4', '그래프의 기울기는 질량의 역수와 같다.', True, 'a = F/m 이므로 기울기는 1/m 이다.'),
            ('g5', 'A, B에 같은 크기의 힘을 작용하면 가속도는 %s가 더 크다.' % small, True, '질량이 작은 %s의 가속도가 더 크다.' % small),
            ('g5', 'A, B에 같은 크기의 힘을 작용하면 가속도는 %s가 더 크다.' % big, False, '같은 힘일 때 질량이 작은 %s의 가속도가 더 크다.' % small),
            ('g6', 'A, B에 같은 크기의 가속도를 주려면 %s에 더 큰 힘을 작용해야 한다.' % big, True, 'F = ma 에서 같은 a 라면 질량이 큰 %s에 큰 힘이 필요하다.' % big),
            ('g6', 'A, B에 같은 크기의 가속도를 주려면 %s에 더 큰 힘을 작용해야 한다.' % small, False, '같은 a 라면 질량이 큰 %s에 더 큰 힘이 필요하다.' % big),
        ]
        stm = pick3(S, r)
        return bogi('그림은 마찰이 없는 수평면에서 물체 A, B에 작용하는 알짜힘 F에 따른 가속도 a를 나타낸 그래프이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, pre=fig, r=r, ask='', lv='중' if r.random() < .5 else '상', fam='e', core='a-F 그래프의 기울기는 1/m 이므로 기울기가 클수록 질량이 작다.', point='그래프에서 같은 힘에서의 가속도를 비교하고 값을 읽는다.')
    if fam == 'c':
        Fv = r.choice([6, 8, 10, 12, 16, 20, 24])
        m0 = r.choice([2, 3, 4, 5, 6, 8])
        a0 = Fv / m0
        if not isnice(a0, 2) or abs(a0 * 2 - round(a0 * 2)) > 1e-9: return None
        mmax = 8
        ymax = Fv  # m=1 에서 a = F
        step = {6: 1, 8: 2, 10: 2, 12: 2, 16: 4, 20: 4, 24: 4}[Fv]
        if abs(a0 / step - round(a0 / step)) > 1e-9: return None
        p = Plot(300, 225, mmax, ymax * 1.05, ml=46, mr=28, mt=18, mb=32)
        p.axes('m (kg)', 'a (m/s²)', ticks(mmax, 1), ticks(ymax, step), grid=True)
        pts = [(m_ / 10, Fv / (m_ / 10)) for m_ in range(10, 81, 2)]
        p.pl(pts, RD, 2.6)
        p.dash_to_axes(m0, a0); p.circ(p.px(m0), p.py(a0), 3.5, INK, INK)
        fig = FIG(p.svg(), '66%')
        ask = r.choice(['F', 'a2'])
        if ask == 'F':
            body = P('그림은 마찰이 없는 수평면에서 크기가 일정한 알짜힘을 받아 운동하는 물체의 질량 m에 따른 가속도 a를 나타낸 그래프이다. 물체에 작용하는 알짜힘의 크기는?') + fig
            wr = WR(Fv, [m0 + a0, a0, m0, Fv / 2, Fv * 2, Fv + 2], 'N')
            return mc(body, U(Fv, 'N'), wr, r=r, lv='중', fam='c', steps=['그래프에서 m = %d kg 일 때 a = %s m/s² 이다.' % (m0, num(a0)), 'F = ma = %d × %s = %d N (m과 a의 곱은 일정하다.)' % (m0, num(a0), Fv)], core='힘이 일정하면 a = F/m 이므로 a-m 그래프는 반비례 곡선이고 ma = F 이다.', point='그래프 위 한 점의 질량과 가속도를 곱해 알짜힘을 구한다.')
        m2 = r.choice([x for x in (1, 2, 3, 4, 5, 6, 8) if x != m0 and isnice(Fv / x, 2)])
        a2 = Fv / m2
        body = P('그림은 마찰이 없는 수평면에서 크기가 일정한 알짜힘을 받아 운동하는 물체의 질량 m에 따른 가속도 a를 나타낸 그래프이다. 같은 알짜힘이 질량 %d kg인 물체에 작용할 때 가속도의 크기는?' % m2) + fig
        wr = WR(a2, [a0, Fv / m2 + 1, a0 * m2 / m0 if False else a0 * m2 / m0, m2 * a0, Fv, a2 * 2], 'm/s²')
        return mc(body, U(a2, 'm/s²'), wr, r=r, lv='상', fam='c', steps=['그래프에서 m = %d kg 일 때 a = %s m/s² 이므로 F = ma = %d N' % (m0, num(a0), Fv), 'm = %d kg 이면 a = F ÷ m = %d ÷ %d = %s m/s²' % (m2, Fv, m2, num(a2))], core='알짜힘이 같으면 가속도는 질량에 반비례한다.', point='그래프로 힘을 구한 뒤 다른 질량의 가속도를 구한다.')
    # d: a - 1/m 그래프
    Fv = r.choice([4, 6, 8, 10, 12])
    x0 = r.choice([0.5, 1, 1.5, 2])
    a0 = Fv * x0
    xmax = 2.5
    ymax = Fv * 2.5
    step = {4: 2, 6: 3, 8: 4, 10: 5, 12: 6}[Fv]
    if abs(a0 / step - round(a0 / step)) > 1e-9 and not isnice(a0): return None
    p = Plot(300, 225, xmax, ymax * 1.02, ml=46, mr=28, mt=18, mb=32)
    p.axes('1/m (1/kg)', 'a (m/s²)', [0, 0.5, 1, 1.5, 2, 2.5], ticks(ymax, step), grid=True)
    p.pl([(0, 0), (xmax * .96, xmax * .96 * Fv)], RD, 2.6)
    p.dash_to_axes(x0, a0); p.circ(p.px(x0), p.py(a0), 3.5, INK, INK)
    mm = 1 / x0
    ask = r.choice(['F', 'm'])
    body = P('그림은 마찰이 없는 수평면에서 일정한 알짜힘을 받는 물체의 가속도 a를 질량의 역수 1/m에 대해 나타낸 그래프이다. ' + ('물체에 작용하는 알짜힘의 크기는?' if ask == 'F' else '가속도가 %s m/s²일 때 물체의 질량은?' % num(a0))) + FIG(p.svg(), '66%')
    if ask == 'F':
        wr = WR(Fv, [a0, x0, a0 + x0, Fv * 2, Fv / 2, a0 * x0 * 2], 'N')
        return mc(body, U(Fv, 'N'), wr, r=r, lv='상', fam='d', steps=['a = F × (1/m) 이므로 그래프의 기울기가 알짜힘이다.', '1/m = %s 일 때 a = %s 이므로 F = %s ÷ %s = %d N' % (num(x0), num(a0), num(a0), num(x0), Fv)], core='a-(1/m) 그래프는 원점을 지나는 직선이며 기울기가 알짜힘 F 이다.', point='기울기를 읽어 알짜힘을 구한다.')
    wr = WR(mm, [x0, a0, Fv, mm * 2, mm / 2, a0 / Fv * 2], 'kg')
    return mc(body, U(mm, 'kg'), wr, r=r, lv='중', fam='d', steps=['그래프에서 a = %s m/s² 일 때 1/m = %s kg⁻¹ 이다.' % (num(a0), num(x0)), 'm = 1 ÷ %s = %s kg' % (num(x0), num(mm))], core='가로축이 1/m 이므로 읽은 값의 역수가 질량이다.', point='가로축이 질량의 역수임에 유의한다.')


# ================================================================= ph011
@T('ph011')
def two_blocks(r, k):
    fam = r.choice(['a'] * 4 + ['c'] * 3 + ['d'] * 3 + ['e'] * 2 + ['f'] * 2 + ['g'] * 2)
    if fam == 'a':
        m1, m2, a = r.randint(1, 6), r.randint(1, 6), r.randint(1, 5)
        F = (m1 + m2) * a
        side = r.choice(['right', 'left'])
        ask = r.choice(['a', 'T', 'T'])
        # 물체 A(왼쪽, m1), B(오른쪽, m2)
        pulled = 'B' if side == 'right' else 'A'
        behind_m = m1 if side == 'right' else m2
        T = behind_m * a
        assert abs(T - (F * behind_m / (m1 + m2))) < 1e-9
        fig = FIG(fig_row([('A', '%d kg' % m1), ('B', '%d kg' % m2)], ['rope'], side, 'F'), '70%')
        base = '그림과 같이 마찰이 없는 수평면에서 질량이 각각 %d kg, %d kg인 물체 A, B를 줄로 연결하고 %s에 크기 %d N의 힘 F를 %s 방향으로 작용시켰다. ' % (m1, m2, '오른쪽 물체 B' if side == 'right' else '왼쪽 물체 A', F, '수평 오른쪽' if side == 'right' else '수평 왼쪽')
        if ask == 'a':
            body = P(base + '두 물체의 가속도의 크기는? (단, 줄의 질량은 무시한다.)') + fig
            wr = WR(a, [F / m1, F / m2, F / (m1 + m2) + 1, F, F * (m1 + m2) / 10 if False else None, a * 2], 'm/s²')
            return mc(body, U(a, 'm/s²'), wr, r=r, lv='하', fam='a', steps=['A, B는 한 덩어리로 운동하므로 알짜힘 F = (m%s + m%s)a 이다.' % (sub('A'), sub('B')), 'a = %d ÷ (%d + %d) = %d m/s²' % (F, m1, m2, a)], core='줄로 연결된 두 물체는 같은 가속도로 운동하며, 전체에 F = (m1 + m2)a 를 적용한다.', point='전체 질량으로 가속도를 구한다.')
        body = P(base + '두 물체를 연결한 줄이 물체를 당기는 힘(장력)의 크기는? (단, 줄의 질량은 무시한다.)') + fig
        other = 'A' if side == 'right' else 'B'
        wr = WR(T, [F, F / 2, pulled and (m2 if side == 'right' else m1) * a, F - T, T + 2, a], 'N')
        return mc(body, U(T, 'N'), wr, r=r, lv='중', fam='a', steps=['전체의 가속도 a = F ÷ (m%s + m%s) = %d ÷ %d = %d m/s²' % (sub('A'), sub('B'), F, m1 + m2, a), '물체 %s만 보면 장력이 알짜힘이다 : T = m%s a = %d × %d = %d N' % (other, sub(other), behind_m, a, T)], core='줄을 당기지 않은 쪽 물체에는 장력만 작용하므로 T = (그 물체의 질량) × a 이다.', point='전체로 a를 구한 뒤 한 물체에 F = ma 를 적용한다.')
    if fam == 'c':
        mA, mB, mC, a = r.randint(1, 4), r.randint(1, 4), r.randint(1, 4), r.randint(1, 4)
        F = (mA + mB + mC) * a
        T1, T2 = mA * a, (mA + mB) * a
        assert abs(T2 - F * (mA + mB) / (mA + mB + mC)) < 1e-9
        fig = FIG(fig_row([('A', '%d kg' % mA), ('B', '%d kg' % mB), ('C', '%d kg' % mC)], ['rope', 'rope'], 'right', 'F', 340), '78%')
        base = '그림과 같이 마찰이 없는 수평면에서 질량이 각각 %d kg, %d kg, %d kg인 물체 A, B, C를 줄 p, q로 연결하고 C에 크기 %d N의 힘 F를 수평 방향으로 작용시켰다. ' % (mA, mB, mC, F)
        ask = r.choice(['p', 'q', 'q', 'ratio'])
        if ask == 'ratio':
            g = gcd(T1, T2)
            right = '%d : %d' % (T1 // g, T2 // g)
            body = P(base + '줄 p, q가 당기는 힘의 크기를 각각 T%s, T%s라 할 때 T%s : T%s는? (단, 줄의 질량은 무시한다.)' % (sub('p'), sub('q'), sub('p'), sub('q'))) + fig
            wrongs = ['%d : %d' % (T2 // g, T1 // g), '%d : %d' % (mA, mA + mB + mC if False else mB), '%d : %d' % (mA, mB), '1 : 1', '%d : %d' % (mA + 1, mB + mC + 2)]
            if T1 == T2: return None
            return mc(body, right, wrongs, r=r, lv='상', fam='c', sort='shuf', steps=['전체 가속도 a = %d ÷ %d = %d m/s²' % (F, mA + mB + mC, a), 'T%s = m%s a = %d N, T%s = (m%s + m%s)a = %d N' % (sub('p'), sub('A'), T1, sub('q'), sub('A'), sub('B'), T2), 'T%s : T%s = %d : %d = %s' % (sub('p'), sub('q'), T1, T2, right)], core='C에서 멀수록 줄이 끌어야 할 질량이 작아 장력이 작다.', point='각 줄이 당기는 물체들의 질량 합으로 장력을 구한다.')
        T = T1 if ask == 'p' else T2
        body = P(base + '줄 %s가 당기는 힘의 크기는? (단, 줄의 질량은 무시한다.)' % ask) + fig
        wr = WR(T, [F, F / 3, T1 if ask == 'q' else T2, mB * a, mC * a, T + 2], 'N')
        return mc(body, U(T, 'N'), wr, r=r, lv='중', fam='c', steps=['전체 가속도 a = F ÷ (m%s + m%s + m%s) = %d ÷ %d = %d m/s²' % (sub('A'), sub('B'), sub('C'), F, mA + mB + mC, a), ('줄 p는 A만 당기므로 T%s = m%s a = %d × %d = %d N' % (sub('p'), sub('A'), mA, a, T1)) if ask == 'p' else ('줄 q는 A, B를 함께 당기므로 T%s = (m%s + m%s)a = %d × %d = %d N' % (sub('q'), sub('A'), sub('B'), mA + mB, a, T2))], core='줄이 당기는 힘 = 그 줄 뒤쪽에 있는 물체들의 질량 합 × 가속도.', point='어느 물체들을 한 덩어리로 볼지 정해 F = ma 를 적용한다.')
    if fam == 'd':
        m1, m2, a = r.randint(1, 6), r.randint(1, 6), r.randint(1, 5)
        F = (m1 + m2) * a
        N = m2 * a
        fig = FIG(fig_row([('A', '%d kg' % m1), ('B', '%d kg' % m2)], ['touch'], 'push', 'F'), '66%')
        base = '그림과 같이 마찰이 없는 수평면에서 질량이 각각 %d kg, %d kg인 물체 A, B가 접촉해 있고 A를 크기 %d N의 힘 F로 수평 방향으로 밀었다. ' % (m1, m2, F)
        if r.random() < .5:
            body = P(base + 'A가 B를 미는 힘의 크기는?') + fig
            wr = WR(N, [F, m1 * a, F / 2, N + 2, F - N + 1 if F - N + 1 != N else None, a], 'N')
            return mc(body, U(N, 'N'), wr, r=r, lv='중', fam='d', steps=['전체 가속도 a = F ÷ (m%s + m%s) = %d ÷ %d = %d m/s²' % (sub('A'), sub('B'), F, m1 + m2, a), 'B에 작용하는 알짜힘은 A가 미는 힘뿐이다 : N = m%s a = %d × %d = %d N' % (sub('B'), m2, a, N)], core='접촉한 두 물체가 함께 가속할 때 뒤 물체가 앞 물체를 미는 힘은 (앞 물체의 질량) × a 이다.', point='B에 작용하는 알짜힘이 A가 미는 힘임을 이용한다.')
        body = P(base + 'B가 A를 미는 힘의 크기는?') + fig
        wr = WR(N, [F, m1 * a, F / 2, F - N + 1 if F - N != N else F + 1, a], 'N')
        return mc(body, U(N, 'N'), wr, r=r, lv='상', fam='d', steps=['전체 가속도 a = %d ÷ %d = %d m/s²' % (F, m1 + m2, a), 'B가 A를 미는 힘과 A가 B를 미는 힘은 작용 반작용이므로 크기가 같다.', 'N = m%s a = %d × %d = %d N' % (sub('B'), m2, a, N), '(A : F - N = %d - %d = %d = m%s a = %d N 으로 확인)' % (F, N, F - N, sub('A'), m1 * a)], core='접촉한 두 물체 사이의 힘은 작용 반작용 관계이다.', point='작용 반작용을 이용해 B에 대해 식을 세운다.')
    if fam == 'e':
        m1, m2, a = r.randint(1, 6), r.randint(1, 6), r.randint(1, 5)
        T = m1 * a
        F = (m1 + m2) * a
        fig = FIG(fig_row([('A', '%d kg' % m1), ('B', '%d kg' % m2)], ['rope'], 'right', 'F'), '70%')
        body = P('그림과 같이 마찰이 없는 수평면에서 질량이 각각 %d kg, %d kg인 물체 A, B를 줄로 연결하고 B에 수평 방향의 힘 F를 작용시켰더니 줄이 A를 당기는 힘의 크기가 %d N이었다. F의 크기는? (단, 줄의 질량은 무시한다.)' % (m1, m2, T)) + fig
        wr = WR(F, [T, T + m2 * 1, T * 2, m2 * a, F - m1, T * m2 / m1 if False else T + m2], 'N')
        return mc(body, U(F, 'N'), wr, r=r, lv='상', fam='e', steps=['A에는 장력만 작용하므로 a = T ÷ m%s = %d ÷ %d = %d m/s²' % (sub('A'), T, m1, a), 'A, B 전체에 F = (m%s + m%s)a = (%d + %d) × %d = %d N' % (sub('A'), sub('B'), m1, m2, a, F)], core='한 물체에서 가속도를 구하면 전체에 F = (m1 + m2)a 를 적용할 수 있다.', point='장력으로 가속도를 구한 뒤 전체 운동 방정식을 쓴다.')
    if fam == 'f':
        m1, m2 = r.randint(1, 8), r.randint(1, 8)
        x, y = m1, m1 + m2
        g_ = gcd(x, y)
        body = P('그림과 같이 마찰이 없는 수평면에서 질량이 각각 %d kg, %d kg인 물체 A, B를 줄로 연결하고 B에 수평 방향의 힘 F를 작용시켰다. 줄의 장력의 크기 T와 F의 크기의 비 T : F는? (단, 줄의 질량은 무시한다.)' % (m1, m2)) + FIG(fig_row([('A', '%d kg' % m1), ('B', '%d kg' % m2)], ['rope'], 'right', 'F'), '70%')
        right = '%d : %d' % (x // g_, y // g_)
        if x // g_ == y // g_: return None
        wrongs = ['%d : %d' % (y // g_, x // g_), '%d : %d' % (m2 // gcd(m2, y) if False else m2 // gcd(m2, y), y // gcd(m2, y)), '1 : 1', '1 : 2', '%d : %d' % (x // g_ + 1, y // g_)]
        return mc(body, right, wrongs, r=r, lv='하', fam='f', sort='shuf', steps=['a = F ÷ (%d + %d), T = m%s a = %d × F ÷ %d' % (m1, m2, sub('A'), m1, m1 + m2), 'T : F = %d : %d = %s' % (m1, m1 + m2, right)], core='장력은 F 에 (줄 뒤쪽 물체의 질량)/(전체 질량)을 곱한 값이다.', point='T = F × m(뒤)/(m1 + m2) 로 비를 구한다.')
    # g: 줄이 끊어짐
    m1, m2, a = r.randint(1, 5), r.randint(1, 5), r.randint(1, 4)
    F = (m1 + m2) * a
    a2 = F / m2
    if not isnice(a2, 2): return None
    body = P('그림과 같이 마찰이 없는 수평면에서 질량이 각각 %d kg, %d kg인 물체 A, B를 줄로 연결하고 B에 수평 방향으로 크기 %d N의 힘 F를 작용시켜 함께 운동하고 있다. 줄이 끊어진 직후 B의 가속도의 크기는? (단, 줄의 질량은 무시한다.)' % (m1, m2, F)) + FIG(fig_row([('A', '%d kg' % m1), ('B', '%d kg' % m2)], ['rope'], 'right', 'F'), '70%')
    wr = WR(a2, [a, F / m1, F, a2 + 1, a2 * 2, m2 * a], 'm/s²')
    return mc(body, U(a2, 'm/s²'), wr, r=r, lv='중', fam='g', steps=['끊어지기 전 가속도 a = %d ÷ (%d + %d) = %d m/s²' % (F, m1, m2, a), '끊어진 뒤 B에는 F만 작용하므로 a\' = F ÷ m%s = %d ÷ %d = %s m/s²' % (sub('B'), F, m2, num(a2)), '(A의 가속도는 0이 된다.)'], core='줄이 끊어지면 B에는 F 만 작용하므로 가속도가 커지고 A는 알짜힘이 0이 된다.', point='달라진 알짜힘과 질량으로 다시 F = ma 를 적용한다.')


# ================================================================= ph012
@T('ph012')
def atwood(r, k):
    fam = r.choice(['a'] * 3 + ['b'] * 3 + ['c'] * 2 + ['d'] * 3 + ['e'] * 3 + ['f'] * 2)
    for _ in range(40):
        m1, m2 = r.randint(2, 9), r.randint(1, 8)
        if m1 > m2 and isnice(G * (m1 - m2) / (m1 + m2)) and isnice(2 * G * m1 * m2 / (m1 + m2)): break
    else:
        return None
    a = G * (m1 - m2) / (m1 + m2)
    T = 2 * G * m1 * m2 / (m1 + m2)
    # 교차 검증: 각 물체의 운동 방정식
    assert abs(m1 * G - T - m1 * a) < 1e-9 and abs(T - m2 * G - m2 * a) < 1e-9
    swap = r.random() < .5
    nL, nR = ('A', 'B') if not swap else ('B', 'A')
    ml, mr_ = (m1, m2) if not swap else (m2, m1)
    big = 'A' if (m1 == max(m1, m2)) == (not swap) else 'B'
    # 위 big 은 무거운 쪽의 이름: 왼쪽이 무거우면 왼쪽 이름
    big = nL if ml > mr_ else nR
    fig = FIG(fig_atwood(nL, '%d kg' % ml, nR, '%d kg' % mr_), '58%')
    base = '그림과 같이 질량이 각각 %d kg, %d kg인 물체 %s, %s를 가벼운 줄로 연결해 마찰이 없는 가벼운 도르래에 걸고 가만히 놓았다. ' % (ml, mr_, nL, nR)
    gt = ' (단, 중력 가속도는 10 m/s²이고, 줄은 늘어나지 않는다.)'
    if fam == 'a':
        body = P(base + '물체의 가속도의 크기는?' + gt) + fig
        wr = WR(a, [G * (m1 + m2) / (m1 - m2), G * m1 / (m1 + m2), G * (m1 - m2) / 2, G * (m1 - m2) / m1, G, a / 2], 'm/s²')
        return mc(body, U(a, 'm/s²'), wr, r=r, lv='중', fam='a', steps=['무거운 물체(%d kg)는 내려가고 가벼운 물체(%d kg)는 올라가며 가속도의 크기는 같다.' % (m1, m2), 'a = (m%s - m%s)g ÷ (m%s + m%s) = (%d - %d) × 10 ÷ (%d + %d) = %s m/s²' % (sub(1), sub(2), sub(1), sub(2), m1, m2, m1, m2, num(a))], core='아트우드 장치에서 a = (m1 - m2)g/(m1 + m2) 이다.', point='두 물체를 한 덩어리로 보고 알짜힘(무게 차)을 전체 질량으로 나눈다.')
    if fam == 'b':
        body = P(base + '줄에 걸리는 장력의 크기는?' + gt) + fig
        wr = WR(T, [m1 * G, m2 * G, (m1 + m2) * G / 2, (m1 + m2) * G, T + 5, 2 * T], 'N')
        return mc(body, U(T, 'N'), wr, r=r, lv='중', fam='b', steps=['가속도 a = (%d - %d) × 10 ÷ (%d + %d) = %s m/s²' % (m1, m2, m1, m2, num(a)), '가벼운 물체 : T - m%sg = m%sa 에서 T = %d × (10 + %s) = %s N' % (sub(2), sub(2), m2, num(a), num(T))], core='장력 T = 2m1m2g/(m1 + m2) 이며 두 물체의 무게 사이의 값이다.', point='한 물체의 운동 방정식으로 장력을 구한다.')
    if fam == 'c':
        body = P(base + '두 물체가 운동하는 동안 도르래를 매단 천장이 도르래를 받치는 힘의 크기는? (단, 도르래의 질량은 무시한다.)' + gt) + fig
        wr = WR(2 * T, [T, (m1 + m2) * G, (m1 + m2) * G / 2, 2 * m1 * G, (m1 + m2) * G + a, 4 * T], 'N')
        return mc(body, U(2 * T, 'N'), wr, r=r, lv='상', fam='c', steps=['장력 T = 2m%sm%sg ÷ (m%s + m%s) = %s N' % (sub(1), sub(2), sub(1), sub(2), num(T)), '도르래는 두 줄이 아래로 당기는 힘 2T 를 받으므로 2 × %s = %s N' % (num(T), num(2 * T)), '(두 물체의 무게 합 %d N 보다 작다.)' % ((m1 + m2) * G)], core='가벼운 도르래를 지탱하는 힘은 줄의 장력의 2배(2T)이며, 가속 중에는 두 물체 무게의 합보다 작다.', point='가속 운동 중에는 장력이 무게와 다르다는 점에 유의한다.')
    if fam == 'd':
        # 가속도가 주어지고 m2 구하기
        body = P('질량 %d kg인 물체와 질량이 다른 물체 B를 가벼운 줄로 연결해 마찰이 없는 가벼운 도르래에 걸고 가만히 놓았더니 %d kg인 물체가 %s m/s²의 가속도로 내려갔다. B의 질량은? (단, 중력 가속도는 10 m/s²이다.)' % (m1, m1, num(a))) + FIG(fig_atwood('', '%d kg' % m1, 'B', '?').replace('<text', '<text'), '58%')
        wr = WR(m2, [m1 - a, m1 - m2 + 1, m1 / 2, m1 + 1, m2 + 1, m2 * 2], 'kg')
        return mc(body, U(m2, 'kg'), wr, r=r, lv='상', fam='d', steps=['무거운 물체와 B를 한 덩어리로 보면 (m%s - m%s)g = (m%s + m%s)a 이다.' % (sub(1), sub('B'), sub(1), sub('B')), '(%d - m%s) × 10 = (%d + m%s) × %s' % (m1, sub('B'), m1, sub('B'), num(a)), 'm%s = %d kg' % (sub('B'), m2)], core='(m1 - m2)g = (m1 + m2)a 에서 미지의 질량을 구할 수 있다.', point='가속도로부터 질량을 구하는 역방향 계산이다.')
    if fam == 'e':
        t = r.choice([1, 2, 3, 4])
        ask = r.choice(['v', 's'])
        if ask == 'v':
            v = a * t
            body = P(base + '가만히 놓은 %d초 후 물체의 속력은?' % t + gt) + fig
            wr = WR(v, [G * t, a * t * t / 2, v / 2, v + 2, G * (m1 - m2) * t / m1], 'm/s')
            return mc(body, U(v, 'm/s'), wr, r=r, lv='상', fam='e', steps=['a = (%d - %d) × 10 ÷ (%d + %d) = %s m/s²' % (m1, m2, m1, m2, num(a)), 'v = at = %s × %d = %s m/s' % (num(a), t, num(v))], core='가속도를 구한 뒤 정지에서 출발한 등가속도 운동 공식을 적용한다.', point='아트우드 장치의 가속도와 운동 공식을 연결한다.')
        s = a * t * t / 2
        body = P(base + '가만히 놓은 %d초 동안 각 물체가 이동한 거리는?' % t + gt) + fig
        wr = WR(s, [G * t * t / 2, a * t, s * 2, s / 2, s + 1], 'm')
        return mc(body, U(s, 'm'), wr, r=r, lv='상', fam='e', steps=['a = %s m/s²' % num(a), 's = ½at² = ½ × %s × %d² = %s m' % (num(a), t, num(s))], core='정지에서 출발한 등가속도 운동에서 s = ½at² 이다.', point='가속도를 구한 뒤 변위 공식을 쓴다.')
    # f: 장력과 무게 비교
    body = P(base + '줄의 장력의 크기를 T라 할 때 옳은 것은?' + gt) + fig
    heavy = m1 * G
    light = m2 * G
    right = 'm%sg > T > m%sg' % (sub(big), sub(nR if big == nL else nL))
    hv, lt = big, (nR if big == nL else nL)
    right = '%s의 무게 > T > %s의 무게' % (hv, lt)
    wrongs = ['T = %s의 무게' % hv, 'T = %s의 무게' % lt, 'T > %s의 무게' % hv, 'T < %s의 무게' % lt]
    return mc(body, right, wrongs, r=r, lv='하', fam='f', sort='shuf', steps=['장력 T = %s N, %s의 무게 = %d N, %s의 무게 = %d N' % (num(T), hv, heavy, lt, light), '%d > %s > %d 이므로 %s' % (heavy, num(T), light, right)],
              core='가속 중인 아트우드 장치에서 줄의 장력은 두 물체의 무게 사이의 값이다.', point='무거운 쪽은 알짜힘이 아래로, 가벼운 쪽은 위로 향한다.')


# ================================================================= ph013
@T('ph013')
def table_hang(r, k):
    fam = r.choice(['a'] * 3 + ['b'] * 3 + ['c'] * 3 + ['d'] * 2 + ['e'] * 3 + ['f'] * 2)
    for _ in range(40):
        M, m = r.randint(1, 9), r.randint(1, 9)
        a = G * m / (M + m)
        T = G * M * m / (M + m)
        if isnice(a) and isnice(T): break
    else:
        return None
    assert abs(T - M * a) < 1e-9 and abs(m * G - T - m * a) < 1e-9
    fig = FIG(fig_table_full('A', '%d kg' % M, 'B', '%d kg' % m), '60%')
    base = '그림과 같이 마찰이 없는 수평 책상 위의 물체 A(질량 %d kg)와 책상 옆에 매달린 물체 B(질량 %d kg)를 가벼운 줄로 연결하여 가만히 놓았다. ' % (M, m)
    gt = ' (단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량 및 도르래의 마찰은 무시한다.)'
    if fam == 'a':
        body = P(base + '물체의 가속도의 크기는?' + gt) + fig
        wr = WR(a, [G, G * m / M, G * M / (M + m), G * (M - m) / (M + m) if M > m else None, a / 2, a + 1], 'm/s²')
        return mc(body, U(a, 'm/s²'), wr, r=r, lv='중', fam='a', steps=['A, B를 한 덩어리로 보면 알짜힘은 B의 무게 m%sg = %d N 이다.' % (sub('B'), m * G), 'a = m%sg ÷ (m%s + m%s) = %d ÷ (%d + %d) = %s m/s²' % (sub('B'), sub('A'), sub('B'), m * G, M, m, num(a))], core='책상 위 물체와 매달린 물체의 가속도는 a = mg/(M + m) 이다.', point='구동하는 힘은 매달린 물체의 무게뿐이고 질량은 둘의 합이다.')
    if fam == 'b':
        body = P(base + '줄에 걸리는 장력의 크기는?' + gt) + fig
        wr = WR(T, [m * G, M * G, (M + m) * G, m * a if False else m * a, T / 2, T + 2], 'N')
        return mc(body, U(T, 'N'), wr, r=r, lv='중', fam='b', steps=['a = m%sg ÷ (m%s + m%s) = %s m/s²' % (sub('B'), sub('A'), sub('B'), num(a)), 'A에는 장력만 수평으로 작용하므로 T = m%sa = %d × %s = %s N' % (sub('A'), M, num(a), num(T)), '(B : m%sg - T = m%sa → %d - %s = %s N 로 확인)' % (sub('B'), sub('B'), m * G, num(T), num(m * a))], core='책상 위 물체에서 T = Ma, 매달린 물체에서 mg - T = ma 이다.', point='두 물체에 각각 운동 방정식을 세워 장력을 구한다.')
    if fam == 'c':
        ask = r.choice(['m', 'M'])
        if ask == 'm':
            body = P('그림과 같이 마찰이 없는 수평 책상 위의 물체 A(질량 %d kg)와 책상 옆에 매달린 물체 B를 가벼운 줄로 연결하여 가만히 놓았더니 가속도의 크기가 %s m/s²였다. B의 질량은? (단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량 및 도르래의 마찰은 무시한다.)' % (M, num(a))) + FIG(fig_table_full('A', '%d kg' % M, 'B', '?'), '60%')
            wr = WR(m, [a, M - m + 1, M, M * a / G, m + 1, m * 2], 'kg')
            return mc(body, U(m, 'kg'), wr, r=r, lv='상', fam='c', steps=['m%sg = (m%s + m%s)a 이므로 10m%s = (%d + m%s) × %s' % (sub('B'), sub('A'), sub('B'), sub('B'), M, sub('B'), num(a)), '(10 - %s)m%s = %s 이므로 m%s = %d kg' % (num(a), sub('B'), num(M * a), sub('B'), m)], core='mg = (M + m)a 에서 미지의 질량을 구한다.', point='가속도로부터 매달린 물체의 질량을 구하는 역방향 계산이다.')
        body = P('그림과 같이 마찰이 없는 수평 책상 위의 물체 A와 책상 옆에 매달린 물체 B(질량 %d kg)를 가벼운 줄로 연결하여 가만히 놓았더니 가속도의 크기가 %s m/s²였다. A의 질량은? (단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량 및 도르래의 마찰은 무시한다.)' % (m, num(a))) + FIG(fig_table_full('A', '?', 'B', '%d kg' % m), '60%')
        wr = WR(M, [m, a, m * G / a - m + 1 if False else m * a, m + a, M + 1, M * 2], 'kg')
        return mc(body, U(M, 'kg'), wr, r=r, lv='상', fam='c', steps=['m%sg = (m%s + m%s)a 이므로 %d × 10 = (m%s + %d) × %s' % (sub('B'), sub('A'), sub('B'), m, sub('A'), m, num(a)), 'm%s + %d = %s 이므로 m%s = %d kg' % (sub('A'), m, num(m * G / a), sub('A'), M)], core='mg = (M + m)a 에서 미지의 질량을 구한다.', point='가속도로부터 책상 위 물체의 질량을 구한다.')
    if fam == 'd':
        M2, m2 = r.randint(1, 9), r.randint(1, 9)
        a2 = G * m2 / (M2 + m2)
        if not isnice(a2) or (M2, m2) == (M, m): return None
        ratio = Fraction(a2).limit_denominator(100) / Fraction(a).limit_denominator(100)
        body = P('마찰이 없는 수평 책상 위의 물체 A와 책상 옆에 매달린 물체 B를 가벼운 줄로 연결해 가만히 놓는 실험을 했다. (가) 에서는 A, B의 질량이 각각 %d kg, %d kg이고, (나) 에서는 각각 %d kg, %d kg이다. (나) 에서 가속도의 크기는 (가) 에서의 몇 배인가? (단, 줄과 도르래의 질량 및 도르래의 마찰은 무시한다.)' % (M, m, M2, m2))
        if ratio == 1: return None
        right = fr(ratio) + '배'
        cands = [1 / ratio, Fraction(m2, m) if m else None, Fraction(M, M2), ratio + 1, Fraction(M2 + m2, M + m), ratio * 2]
        wrongs = [fr(c) + '배' for c in cands if c and c > 0 and c != ratio]
        return mc(body, right, wrongs, r=r, lv='상', fam='d', sort='shuf', steps=['(가) a = %d × 10 ÷ (%d + %d) = %s m/s²' % (m, M, m, num(a)), '(나) a = %d × 10 ÷ (%d + %d) = %s m/s²' % (m2, M2, m2, num(a2)), '비 = %s ÷ %s = %s' % (num(a2), num(a), right)], core='a = mg/(M + m) 이므로 매달린 물체가 무겁고 전체 질량이 작을수록 가속도가 크다.', point='두 경우의 가속도를 각각 구해 비를 낸다.')
    if fam == 'e':
        h = r.choice([1, 2, 3, 4, 5, 0.5, 1.5, 2.5])
        v2 = 2 * a * h
        vv = math.sqrt(v2)
        if abs(vv - round(vv)) > 1e-9: return None
        vv = int(round(vv))
        body = P(base + 'B가 정지 상태에서 %s m 내려온 순간 B의 속력은? (단, B는 바닥에 닿지 않았다.)' % num(h) + gt) if False else P(base + 'B가 %s m 내려온 순간 B의 속력은?' % num(h) + gt) + fig
        wr = WR(vv, [vv * vv, math.sqrt(2 * G * h) if abs(math.sqrt(2 * G * h) - round(math.sqrt(2 * G * h))) < 1e-9 else None, a * h, vv * 2, vv / 2, vv + 1], 'm/s')
        return mc(body, U(vv, 'm/s'), wr, r=r, lv='상', fam='e', steps=['a = m%sg ÷ (m%s + m%s) = %s m/s²' % (sub('B'), sub('A'), sub('B'), num(a)), 'v² = 2as = 2 × %s × %s = %s 이므로 v = %d m/s' % (num(a), num(h), num(v2), vv)], core='등가속도 운동에서 v² = 2as 이다.', point='가속도를 구한 뒤 시간 없는 운동 공식을 쓴다.')
    # f: 장력 / 무게
    right_f = Fraction(M, M + m)
    body = P(base + '줄의 장력의 크기는 B의 무게의 몇 배인가?' + gt) + fig
    right = fr(right_f) + '배'
    cands = [Fraction(m, M + m), Fraction(1), Fraction(1, 2), Fraction(M, m), Fraction(m, M), Fraction(M + m, M)]
    wrongs = [fr(c) + '배' for c in cands if c != right_f and c > 0]
    if right_f == Fraction(1, 2) or right_f == 1: return None
    return mc(body, right, wrongs, r=r, lv='중', fam='f', sort='shuf', steps=['T = Ma = M × mg/(M + m) = %s N, B의 무게 = %d N' % (num(T), m * G), 'T ÷ (mg) = %s ÷ %d = %s' % (num(T), m * G, fr(right_f))], core='장력 T = Mmg/(M + m) 이므로 T/(mg) = M/(M + m) < 1 이다.', point='장력은 매달린 물체의 무게보다 작다.')


# ================================================================= ph014
@T('ph014')
def incline_motion(r, k):
    fam = r.choice(['a'] * 3 + ['b'] * 3 + ['c'] * 2 + ['d'] * 3 + ['e'] * 3 + ['f'] * 2)
    if fam == 'a':
        th = r.choice([30, 37, 45, 53, 60])
        m = r.choice([1, 2, 3, 5, 10])
        val = {30: '5', 37: '6', 45: '5√2', 53: '8', 60: '5√3'}[th]
        fl = G * SINV[th]
        body = P('그림과 같이 경사각이 %d°인 마찰이 없는 빗면에서 질량 %d kg인 물체를 가만히 놓았다. 물체가 빗면을 따라 내려갈 때 가속도의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (th, m)) + FIG(fig_incline(th), '56%')
        cos_ = {30: '5√3', 37: '8', 45: '5√2', 53: '6', 60: '5'}[th]
        wrongs = ['%s m/s²' % w for w in (cos_, '10', '5', str(m * 5), '%d' % (m * 10), '%s' % (val if False else '4'), '7')]
        wrongs = [w for w in wrongs if w != val + ' m/s²']
        return mc(body, val + ' m/s²', wrongs, r=r, lv='하', fam='a', sort='shuf', steps=['빗면 방향의 알짜힘은 mg sin%d° 이다.' % th, 'a = g sin%d° = 10 × %s = %s m/s² (질량과 무관)' % (th, SINS[th], val)], core='마찰이 없는 빗면에서 가속도의 크기는 g sinθ 로 질량과 무관하다.', point='빗면 방향 성분 mg sinθ 를 m 으로 나눈다.')
    if fam == 'b':
        th = r.choice([30, 37, 53])
        a = G * SINV[th]
        ask = r.choice(['v', 't', 'L'])
        v = r.randint(2, 12)
        L = v * v / (2 * a)
        t = v / a
        if not isnice(L, 2): return None
        if ask == 'v':
            body = P('그림과 같이 경사각이 %d°인 마찰이 없는 빗면의 윗부분에서 물체를 가만히 놓았다. 물체가 빗면을 따라 %s m 미끄러져 내려왔을 때 속력은? (단, 중력 가속도는 10 m/s²이다.)' % (th, num(L))) + FIG(fig_incline(th, 'L = %s m' % num(L)), '58%')
            wr = WR(v, [math.sqrt(2 * G * L) if abs(math.sqrt(2 * G * L) - round(math.sqrt(2 * G * L))) < 1e-9 else None, a * L, v * 2, v / 2, v + 2, L], 'm/s')
            assert abs(math.sqrt(2 * a * L) - v) < 1e-9
            return mc(body, U(v, 'm/s'), wr, r=r, lv='중', fam='b', steps=['a = g sin%d° = %s m/s²' % (th, num(a)), 'v² = 2aL = 2 × %s × %s = %d 이므로 v = %d m/s' % (num(a), num(L), v * v, v)], core='빗면 아래로 가속하는 물체는 a = g sinθ 인 등가속도 운동을 하며 v² = 2aL 이다.', point='빗면 방향 가속도를 구한 뒤 v² = 2as 를 쓴다.')
        if ask == 't':
            if not isnice(t, 2): return None
            body = P('그림과 같이 경사각이 %d°인 마찰이 없는 빗면의 윗부분에서 물체를 가만히 놓았더니 %s m 미끄러져 내려왔다. 이때 걸린 시간은? (단, 중력 가속도는 10 m/s²이다.)' % (th, num(L))) + FIG(fig_incline(th, 'L = %s m' % num(L)), '58%')
            wr = WR(t, [v, L / a, math.sqrt(2 * L / G) if isnice(math.sqrt(2 * L / G)) else None, t * 2, t / 2, t + 1], 's')
            return mc(body, U(t, 's'), wr, r=r, lv='상', fam='b', steps=['a = g sin%d° = %s m/s²' % (th, num(a)), 'L = ½at² 이므로 t = √(2L/a) = √(2 × %s ÷ %s) = %s s' % (num(L), num(a), num(t))], core='정지에서 출발한 등가속도 운동에서 L = ½at² 이다.', point='빗면 가속도를 구한 뒤 변위 공식에서 시간을 구한다.')
        body = P('그림과 같이 경사각이 %d°인 마찰이 없는 빗면의 윗부분에서 물체를 가만히 놓았더니 빗면을 따라 내려가 속력이 %d m/s가 되었다. 미끄러진 거리는? (단, 중력 가속도는 10 m/s²이다.)' % (th, v)) + FIG(fig_incline(th, 'L = ?'), '58%')
        wr = WR(L, [v * v / (2 * G), v * v / a, v / a, L * 2, L / 2, v], 'm')
        return mc(body, U(L, 'm'), wr, r=r, lv='중', fam='b', steps=['a = g sin%d° = %s m/s²' % (th, num(a)), 'v² = 2aL 이므로 L = %d² ÷ (2 × %s) = %s m' % (v, num(a), num(L))], core='빗면 위의 가속도 g sinθ 로 등가속도 운동 공식을 쓴다.', point='v² = 2aL 에서 거리를 구한다.')
    if fam == 'c':
        h = r.choice([0.8, 1.25, 1.8, 3.2, 5, 4.05, 2.45, 7.2, 0.45, 2.45])
        v = math.sqrt(2 * G * h)
        if abs(v - round(v)) > 1e-9: return None
        v = int(round(v))
        t1, t2 = r.sample([30, 37, 45, 53, 60], 2)
        body = P('그림과 같이 높이가 %s m로 같고 경사각이 %d°, %d°인 마찰이 없는 두 빗면의 꼭대기에서 같은 물체를 가만히 놓았다. 두 물체가 빗면 아래에 도달했을 때 속력은? (단, 중력 가속도는 10 m/s²이다.)' % (num(h), t1, t2)) + FIG(fig_two(t1, t2, num(h)), '66%')
        wr = WR(v, [v * 2, v / 2, v + 2, h * G, math.sqrt(2 * G * h * SINV[t1]) if isnice(math.sqrt(2 * G * h * SINV[t1])) else None, v + 1], 'm/s')
        return mc(body, U(v, 'm/s'), wr, r=r, lv='상', fam='c', steps=['빗면의 길이는 L = h/sinθ 이고 a = g sinθ 이므로 v² = 2aL = 2gh 이다.', 'v = √(2 × 10 × %s) = %d m/s (두 빗면에서 같다.)' % (num(h), v)], core='마찰이 없는 빗면에서 도달 속력은 높이 h 만으로 정해진다(v = √(2gh)).', point='경사각이 달라도 같은 높이면 속력이 같다.')
    if fam == 'd':
        th = r.choice([30, 37, 53])
        for _ in range(40):
            m1, m2 = r.randint(1, 10), r.randint(1, 10)
            w1 = m1 * G * SINV[th]
            net = m2 * G - w1
            a = net / (m1 + m2)
            T = m2 * (G - a)
            if net > 0 and isnice(a) and isnice(T): break
        else:
            return None
        assert abs(T - m1 * G * SINV[th] - m1 * a) < 1e-9
        ask = r.choice(['a', 'T'])
        base = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위의 물체 A(질량 %d kg)와 도르래에 매달린 물체 B(질량 %d kg)를 줄로 연결해 가만히 놓았더니 B가 내려갔다. ' % (th, m1, m2)
        gt = '(단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량 및 마찰은 무시한다.)'
        fig = FIG(fig_incline_pulley(th), '64%')
        if ask == 'a':
            body = P(base + '물체의 가속도의 크기는? ' + gt) + fig
            wr = WR(a, [m2 * G / (m1 + m2), (m2 * G - m1 * G) / (m1 + m2) if m2 > m1 else None, m1 * G * SINV[th] / (m1 + m2), a / 2, a + 1, G * SINV[th]], 'm/s²')
            return mc(body, U(a, 'm/s²'), wr, r=r, lv='상', fam='d', steps=['A, B를 한 덩어리로 보면 알짜힘 = m%sg - m%sg sin%d° = %d - %s = %s N' % (sub('B'), sub('A'), th, m2 * G, num(w1), num(net)), 'a = %s ÷ (%d + %d) = %s m/s²' % (num(net), m1, m2, num(a))], core='빗면 위 물체와 매달린 물체의 가속도 a = (m2g - m1g sinθ)/(m1 + m2) 이다.', point='구동력은 B의 무게에서 A의 빗면 방향 성분을 뺀 값이다.')
        body = P(base + '줄에 걸리는 장력의 크기는? ' + gt) + fig
        wr = WR(T, [m2 * G, m1 * G * SINV[th], m1 * a, (m1 + m2) * a, T + 5, T - 5 if T > 5 else T + 7], 'N')
        return mc(body, U(T, 'N'), wr, r=r, lv='상', fam='d', steps=['a = (%d - %s) ÷ (%d + %d) = %s m/s²' % (m2 * G, num(w1), m1, m2, num(a)), 'B : m%sg - T = m%sa 에서 T = %d × (10 - %s) = %s N' % (sub('B'), sub('B'), m2, num(a), num(T))], core='연결된 두 물체는 각각 운동 방정식을 세워 장력을 구한다.', point='가속도를 먼저 구한 뒤 한 물체에 F = ma 를 적용한다.')
    if fam == 'e':
        th = r.choice([30, 37, 53])
        a = G * SINV[th]
        v0 = r.choice([2, 4, 6, 8, 10, 12])
        s = v0 * v0 / (2 * a)
        t = v0 / a
        mode = r.choice(['s', 't'])
        if mode == 's':
            if not isnice(s, 2): return None
            body = P('그림과 같이 경사각이 %d°인 마찰이 없는 빗면의 아래에서 물체를 빗면을 따라 위로 %d m/s의 속력으로 밀어 올렸다. 물체가 순간 정지할 때까지 빗면을 따라 올라간 거리는? (단, 중력 가속도는 10 m/s²이다.)' % (th, v0)) + FIG(fig_incline(th, v0=True), '58%')
            wr = WR(s, [v0 * v0 / (2 * G), v0 * v0 / a, v0 / a, s * 2, s / 2, v0], 'm')
            return mc(body, U(s, 'm'), wr, r=r, lv='중', fam='e', steps=['올라갈 때 가속도는 빗면 아래 방향으로 크기 g sin%d° = %s m/s² 이다.' % (th, num(a)), '0 - v0² = -2as 에서 s = %d² ÷ (2 × %s) = %s m' % (v0, num(a), num(s))], core='빗면을 올라가는 물체는 크기 g sinθ 로 감속한다.', point='감속 운동에 v² - v0² = 2as 를 쓴다.')
        if not isnice(t, 2): return None
        body = P('그림과 같이 경사각이 %d°인 마찰이 없는 빗면의 아래에서 물체를 빗면을 따라 위로 %d m/s의 속력으로 밀어 올렸다. 물체가 순간 정지할 때까지 걸리는 시간은? (단, 중력 가속도는 10 m/s²이다.)' % (th, v0)) + FIG(fig_incline(th, v0=True), '58%')
        wr = WR(t, [v0 / G, v0 * a, v0 * v0 / (2 * a), t * 2, t / 2, t + 1], 's')
        return mc(body, U(t, 's'), wr, r=r, lv='중', fam='e', steps=['올라갈 때 가속도는 빗면 아래 방향으로 크기 g sin%d° = %s m/s² 이다.' % (th, num(a)), '0 = v0 - at 에서 t = %d ÷ %s = %s s' % (v0, num(a), num(t))], core='빗면을 올라가는 물체는 크기 g sinθ 로 감속한다.', point='v = v0 - at 에서 정지까지의 시간을 구한다.')
    # f: 두 각도 비교
    t1, t2 = r.sample([30, 37, 53], 2)
    s1, s2 = SINV[t1], SINV[t2]
    ask = r.choice(['a', 't'])
    g_ = gcd(int(round(s1 * 10)), int(round(s2 * 10)))
    x, y = int(round(s1 * 10)) // g_, int(round(s2 * 10)) // g_
    if ask == 'a':
        right = '%d : %d' % (x, y)
        wrongs = ['%d : %d' % (y, x), '1 : 1', '%d : %d' % (x * x, y * y), '%d : %d' % (t1, t2)]
        body = P('경사각이 각각 %d°, %d°인 마찰이 없는 두 빗면에서 물체 A, B가 미끄러져 내려간다. A, B의 가속도의 크기의 비 a%s : a%s는? (단, 질량은 무시할 수 있는 영향이 없다.)' % (t1, t2, sub('A'), sub('B'))).replace(' (단, 질량은 무시할 수 있는 영향이 없다.)', '') + FIG(fig_two(t1, t2, None), '66%')
        wrongs.append('%d : %d' % (x + 1, y))
        return mc(body, right, wrongs, r=r, lv='하', fam='f', sort='shuf', steps=['a = g sinθ 이므로 a%s : a%s = sin%d° : sin%d° = %s : %s = %d : %d' % (sub('A'), sub('B'), t1, t2, SINS[t1], SINS[t2], x, y)], core='빗면에서 가속도는 g sinθ 이므로 sinθ 에 비례한다.', point='각도에 따른 sinθ 값을 비교한다.')
    # 같은 길이 L 을 내려오는 데 걸리는 시간 비 t ∝ 1/√a — 대신 같은 거리에서 속력 비
    right = '%d : %d' % (x, y)
    # v = √(2 a L) ∝ √a : 값이 무리수가 되므로 가속도 비의 제곱근 형태 대신 '속력의 제곱비'를 묻는다.
    body = P('경사각이 각각 %d°, %d°인 마찰이 없는 두 빗면에서 물체 A, B를 가만히 놓았더니 빗면을 따라 같은 거리만큼 미끄러졌다. 이때 속력의 제곱의 비 v%s² : v%s²는?' % (t1, t2, sub('A'), sub('B'))) + FIG(fig_two(t1, t2, None), '66%')
    wrongs = ['%d : %d' % (y, x), '1 : 1', '%d : %d' % (x * x, y * y), '%d : %d' % (t1, t2), '%d : %d' % (x + 1, y)]
    return mc(body, right, wrongs, r=r, lv='중', fam='f', sort='shuf', steps=['v² = 2aL, a = g sinθ 이고 L 이 같으므로 v%s² : v%s² = a%s : a%s = sin%d° : sin%d°' % (sub('A'), sub('B'), sub('A'), sub('B'), t1, t2), '= %s : %s = %d : %d' % (SINS[t1], SINS[t2], x, y)], core='같은 거리를 내려오면 v² ∝ a ∝ sinθ 이다.', point='속력의 제곱은 가속도에 비례한다.')


def fig_two(t1, t2, hl):
    """높이가 같은 두 빗면(왼쪽: 오른쪽 위로 올라가는 t1, 오른쪽: t2). 꼭대기에 물체 없음."""
    f = Fig(300, 175)
    h = min(110, 250 / (1 / math.tan(math.radians(t1)) + 1 / math.tan(math.radians(t2))))
    x0, y0 = 20, 160
    xa = x0 + h / math.tan(math.radians(t1))
    x1 = xa + h / math.tan(math.radians(t2))
    f.poly([(x0, y0), (x1, y0), (xa, y0 - h)], '#f1f4f8', INK, 1.8)
    arc(f, x0, y0, 34, 0, t1); lab(f, x0 + 50, y0 - 7, '%d°' % t1, GR)
    arc(f, x1, y0, 34, 180 - t2, 180); lab(f, x1 - 50, y0 - 7, '%d°' % t2, GR)
    n = Fig._n
    for (px, py, ang, nm, fill) in ((x0 + .55 * (xa - x0), y0 - .55 * h, -t1, 'A', '#cfe2f7'), (x1 + .55 * (xa - x1), y0 - .55 * h, t2, 'B', '#fbe3c3')):
        f.o.append('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="26" height="20" fill="%s" stroke="%s" stroke-width="1.6"/><text x="%s" y="%s" font-size="12" text-anchor="middle" font-weight="700" fill="%s" font-family="%s">%s</text></g>' % (n(ang), n(px), n(py), n(px - 13), n(py - 20), fill, INK, n(px), n(py - 6), INK, FONT, nm))
    if hl:
        f.line(xa, y0 - h, xa, y0, GR, 1, '4 3')
        lab(f, xa + 5, y0 - h / 2 + 4, 'h = %s m' % hl, GR, 'start')
    return f.svg()


# ================================================================= ph015
GEN = [
    ('i_ex', '버스가 갑자기 출발하면 서 있던 승객의 몸이 뒤로 쏠리는 것은 관성 때문이다.', True, '승객은 정지 상태를 유지하려는 관성이 있어 몸이 뒤로 쏠린다.'),
    ('i_ex', '식탁보를 빠르게 잡아당겨도 그릇이 제자리에 남는 것은 관성으로 설명할 수 있다.', True, '그릇은 정지 상태를 유지하려는 관성이 있다.'),
    ('i_all', '정지해 있는 물체는 관성이 없고 운동하는 물체만 관성이 있다.', False, '관성은 모든 물체가 가진 성질이다.'),
    ('i_all', '관성은 물체에 힘이 작용할 때만 나타나는 성질이다.', False, '관성은 힘의 작용 여부와 상관없이 물체가 가진 성질이다.'),
    ('i_mass', '질량이 클수록 관성이 크다.', True, '관성의 크기는 질량으로 나타낸다.'),
    ('i_mass', '질량이 큰 물체일수록 운동 상태를 변화시키기 쉽다.', False, '질량이 클수록 관성이 커서 운동 상태를 변화시키기 어렵다.'),
    ('i_mass', '질량이 작은 물체는 관성이 더 크다.', False, '관성은 질량이 클수록 크다.'),
    ('free', '알짜힘이 0인 물체는 반드시 정지해 있다.', False, '알짜힘이 0이면 정지해 있거나 등속 직선 운동을 한다.'),
    ('free', '마찰이 없는 수평면에서 미끄러지는 물체는 힘을 주지 않아도 등속 직선 운동을 계속한다.', True, '알짜힘이 0이면 속도가 변하지 않는다(관성 법칙).'),
    ('free', '운동하는 물체가 계속 운동하려면 운동 방향으로 항상 힘이 작용해야 한다.', False, '물체는 알짜힘이 0이어도 등속 직선 운동을 계속한다.'),
    ('free', '물체에 작용하는 알짜힘이 0이면 물체의 속도는 변하지 않는다.', True, '뉴턴 제1법칙(관성 법칙)이다.'),
    ('a_mass', '같은 크기의 알짜힘이 작용할 때 질량이 큰 물체일수록 가속도가 작다.', True, 'a = F/m 이므로 질량에 반비례한다.'),
    ('a_mass', '질량이 같은 두 물체에 작용하는 알짜힘이 2배가 되면 가속도는 1/2배가 된다.', False, '가속도는 알짜힘에 비례하므로 2배가 된다.'),
    ('a_dir', '물체의 가속도의 방향은 알짜힘의 방향과 같다.', True, '가속도의 방향은 알짜힘의 방향이다.'),
    ('a_dir', '물체의 가속도의 방향은 속도의 방향과 항상 같다.', False, '속력이 줄어드는 운동에서는 가속도가 속도와 반대 방향이다.'),
    ('a_f', '물체의 속력이 클수록 물체에 작용하는 알짜힘도 크다.', False, '알짜힘은 속력이 아니라 가속도에 비례한다.'),
    ('a_f', '물체에 작용하는 알짜힘이 일정하면 물체의 가속도도 일정하다.', True, '질량이 일정할 때 a = F/m 은 일정하다.'),
    ('ar_eq', '두 물체가 서로 밀 때 서로에게 작용하는 힘의 크기는 같다.', True, '작용 반작용 법칙이다.'),
    ('ar_eq', '충돌한 트럭과 승용차에서 트럭이 승용차에 작용하는 힘이 승용차가 트럭에 작용하는 힘보다 크다.', False, '두 힘은 작용 반작용이므로 크기가 같다.'),
    ('ar_eq', '사과가 지구를 당기는 힘과 지구가 사과를 당기는 힘은 크기가 같다.', True, '작용 반작용의 두 힘은 크기가 같다.'),
    ('ar_obj', '작용 반작용의 두 힘은 같은 물체에 작용한다.', False, '작용 반작용의 두 힘은 서로 다른 물체에 작용한다.'),
    ('ar_obj', '작용 반작용의 두 힘은 크기가 같으므로 합력이 0이 되어 두 물체는 가속되지 않는다.', False, '두 힘은 서로 다른 물체에 작용하므로 합할 수 없다.'),
    ('ar_ex', '로켓이 가스를 뒤로 분출하며 앞으로 가속하는 것은 작용 반작용으로 설명할 수 있다.', True, '가스가 로켓을 미는 반작용으로 가속한다.'),
    ('ar_ex', '수영할 때 물을 뒤로 밀면 몸이 앞으로 나아가는 것은 작용 반작용 때문이다.', True, '물이 몸을 앞으로 미는 반작용이 작용한다.'),
    ('ar_ex', '스케이트 선수가 벽을 밀면 벽도 선수를 반대 방향으로 민다.', True, '작용 반작용 법칙이다.'),
]
INERT = [
    ('x1', '달리던 사람이 돌부리에 걸리면 앞으로 넘어지는 것은 관성 때문이다.', True, '발은 멈추지만 상체는 계속 운동하려는 관성이 있다.'),
    ('x1', '달리던 사람이 돌부리에 걸려 앞으로 넘어지는 것은 사람의 관성이 사라졌기 때문이다.', False, '관성은 사라지지 않는다. 상체가 계속 운동하려는 관성 때문에 넘어진다.'),
    ('x2', '버스가 급정거하면 승객이 앞으로 쏠린다.', True, '승객은 계속 앞으로 운동하려는 관성이 있다.'),
    ('x2', '버스가 급정거할 때 승객이 앞으로 쏠리는 것은 버스가 승객을 앞으로 밀기 때문이다.', False, '승객이 앞으로 쏠리는 것은 관성 때문이며 앞쪽으로 미는 힘이 있는 것은 아니다.'),
    ('x3', '망치 자루를 바닥에 내리치면 망치 머리가 자루에 단단히 박힌다.', True, '자루가 멈춰도 망치 머리는 계속 운동하려는 관성이 있다.'),
    ('x4', '이불을 막대로 두드리면 먼지가 떨어져 나가는 것은 관성으로 설명할 수 있다.', True, '이불은 움직이지만 먼지는 그 자리에 있으려는 관성이 있다.'),
    ('x5', '질량이 큰 수레가 질량이 작은 수레보다 밀기 어려운 것은 관성이 크기 때문이다.', True, '질량이 클수록 관성이 크다.'),
    ('x5', '질량이 큰 수레가 질량이 작은 수레보다 밀기 어려운 것은 관성이 작기 때문이다.', False, '질량이 클수록 관성이 크다.'),
    ('x6', '관성은 물체가 현재의 운동 상태를 유지하려는 성질이다.', True, '관성의 정의이다.'),
    ('x6', '관성은 외부에서 힘을 가해야만 생기는 성질이다.', False, '관성은 모든 물체가 원래 가진 성질이다.'),
    ('x7', '우주 공간에서 힘을 받지 않는 우주선은 등속 직선 운동을 한다.', True, '알짜힘이 0이면 관성에 따라 등속 직선 운동을 한다.'),
    ('x8', '관성의 크기는 물체의 속력에 비례한다.', False, '관성의 크기는 속력이 아니라 질량으로 나타낸다.'),
    ('x8', '관성의 크기는 물체의 질량으로 나타낸다.', True, '질량이 클수록 관성이 크다.'),
    ('x9', '정지해 있는 물체에는 관성이 작용하지 않는다.', False, '정지한 물체도 정지 상태를 유지하려는 관성을 가진다.'),
]
ARR = [
    ('y1', '책이 책상을 누르는 힘과 책상이 책을 떠받치는 힘은 작용 반작용 관계이다.', True, '서로 다른 두 물체가 서로에게 작용하는 한 쌍의 힘이다.'),
    ('y2', '로켓이 가스를 뒤로 분출하면 가스가 로켓을 앞으로 미는 힘이 작용한다.', True, '로켓과 가스 사이의 작용 반작용이다.'),
    ('y3', '벽을 손으로 밀면 벽도 손을 같은 크기의 힘으로 민다.', True, '작용 반작용 법칙이다.'),
    ('y4', '작용 반작용의 두 힘은 크기가 같고 방향이 반대이다.', True, '뉴턴 제3법칙이다.'),
    ('y4', '작용 반작용의 두 힘은 크기가 같고 방향도 같다.', False, '작용 반작용의 두 힘은 방향이 서로 반대이다.'),
    ('y5', '줄다리기에서 이긴 팀이 진 팀을 당기는 힘이 진 팀이 이긴 팀을 당기는 힘보다 크다.', False, '두 팀이 줄을 당기는 힘은 작용 반작용이므로 크기가 같다.'),
    ('y6', '질량이 큰 사람이 질량이 작은 사람을 밀 때 큰 사람이 미는 힘이 더 크다.', False, '서로 미는 힘은 작용 반작용이므로 크기가 같다.'),
    ('y7', '작용 반작용의 두 힘은 서로 다른 물체에 작용한다.', True, '그래서 두 힘은 서로 상쇄되지 않는다.'),
    ('y7', '작용 반작용의 두 힘은 같은 물체에 작용하므로 서로 상쇄된다.', False, '두 힘은 서로 다른 물체에 작용하므로 합력을 구할 수 없다.'),
    ('y8', '총을 쏘면 총알이 앞으로 나가는 동시에 총이 뒤로 밀리는 것은 작용 반작용 때문이다.', True, '총이 총알을 미는 힘의 반작용으로 총알이 총을 민다.'),
    ('y9', '지구가 달을 당기는 힘과 달이 지구를 당기는 힘은 크기가 같다.', True, '작용 반작용의 두 힘이다.'),
    ('y9', '지구가 달을 당기는 힘이 달이 지구를 당기는 힘보다 크다.', False, '두 힘은 작용 반작용이므로 크기가 같다.'),
    ('y10', '보트에서 노로 물을 뒤로 밀면 보트가 앞으로 나아가는 것은 작용 반작용으로 설명할 수 있다.', True, '물이 노를 앞으로 미는 힘이 작용한다.'),
    ('y11', '작용 반작용 관계의 두 힘은 한 힘이 작용한 뒤에야 다른 힘이 나타난다.', False, '두 힘은 동시에 작용한다.'),
    ('y11', '작용 반작용의 두 힘은 동시에 작용하고 동시에 사라진다.', True, '한 힘이 있으면 항상 반작용이 동시에 존재한다.'),
]
INERT_EX = ['달리던 사람이 돌부리에 걸려 앞으로 넘어진다.', '정지해 있던 버스가 갑자기 출발하자 서 있던 승객이 뒤로 쏠린다.', '망치 자루를 바닥에 내리치면 망치 머리가 자루에 단단히 박힌다.', '먼지 묻은 이불을 막대로 두드려 먼지를 턴다.', '컵 아래의 종이를 빠르게 잡아당기면 컵이 제자리에 남는다.', '자전거 페달을 멈춰도 자전거가 한동안 앞으로 나아간다.', '달리던 버스가 급정거하면 승객이 앞으로 쏠린다.', '물이 담긴 컵을 든 채 갑자기 멈추면 물이 앞으로 쏟아진다.']
AR_EX = ['로켓이 연료를 뒤로 분출하며 위로 날아오른다.', '수영 선수가 물을 뒤로 밀며 앞으로 나아간다.', '바람이 빠지는 풍선이 바람이 나오는 반대 방향으로 날아간다.', '벽을 밀면 몸이 뒤로 밀려난다.', '대포를 쏘면 대포가 뒤로 밀려난다.', '보트에서 노로 물을 뒤로 밀면 보트가 앞으로 나아간다.', '스케이트 선수가 서로 밀면 두 사람이 반대 방향으로 멀어진다.', '배에서 육지를 향해 뛰어내리면 배가 뒤로 밀린다.']
ACC_EX = ['같은 힘으로 밀 때 빈 수레가 짐을 실은 수레보다 더 빨리 빨라진다.', '같은 공을 더 센 힘으로 차면 공이 더 큰 가속도를 얻는다.', '질량이 큰 트럭은 같은 힘으로 가속시킬 때 승용차보다 가속도가 작다.', '일정한 힘을 받는 물체의 속도가 일정하게 증가한다.']


def _bogi15(r, pool, intro, fam, lv):
    stm = pick3(pool, r)
    return bogi(intro, stm, r=r, ask='', lv=lv, fam=fam, core='뉴턴 제1법칙(관성), 제2법칙(F = ma), 제3법칙(작용 반작용)의 내용을 정확히 구분한다.', point='각 설명이 어느 법칙에 해당하는지, 힘이 작용하는 물체가 무엇인지 따진다.')


def fig_skaters(mA, mB):
    f = Fig(320, 150)
    fy = 126
    f.line(10, fy, 310, fy, '#9fc4e8', 3)
    for cx, nm, mm, c in ((90, 'A', mA, RD), (230, 'B', mB, BL)):
        f.circ(cx, fy - 70, 11, '#fde9d8', INK, 1.6)
        f.line(cx, fy - 59, cx, fy - 25, INK, 2.2)
        f.line(cx, fy - 25, cx - 9, fy - 2, INK, 2.2); f.line(cx, fy - 25, cx + 9, fy - 2, INK, 2.2)
        f.line(cx, fy - 50, cx + (14 if cx == 90 else -14), fy - 46, INK, 2.2)
        lab(f, cx, fy - 88, '%s (%d kg)' % (nm, mm), INK, 'middle', 12.5)
    f.arrow(114, fy - 60, 150, fy - 60, RD, 2.8) if False else None
    f.arrow(118, 40, 156, 40, BL, 2.8)
    f.arrow(202, 24, 164, 24, RD, 2.8)
    lab(f, 160, 14, '', INK)
    return f.svg()


@T('ph015')
def inertia_ar(r, k):
    fam = r.choice(['a'] * 3 + ['b'] * 2 + ['c'] * 2 + ['d'] * 3 + ['e'] * 3)
    if fam == 'a':
        return _bogi15(r, GEN, '뉴턴의 운동 법칙에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', 'a', r.choice(['하', '중']))
    if fam == 'b':
        return _bogi15(r, INERT, '관성과 관성 법칙에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', 'b', '하')
    if fam == 'c':
        return _bogi15(r, ARR, '작용 반작용에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', 'c', '중')
    if fam == 'd':
        which = r.choice(['inert', 'ar', 'acc'])
        if which == 'inert':
            right = r.choice(INERT_EX); wrongs = r.sample(AR_EX + ACC_EX, 4); nm = '관성 법칙'
            expl = '정지(또는 운동) 상태를 유지하려는 관성으로 설명된다.'
        elif which == 'ar':
            right = r.choice(AR_EX); wrongs = r.sample(INERT_EX + ACC_EX, 4); nm = '작용 반작용 법칙'
            expl = '두 물체가 서로에게 같은 크기의 힘을 반대 방향으로 작용하기 때문이다.'
        else:
            right = r.choice(ACC_EX); wrongs = r.sample(INERT_EX + AR_EX, 4); nm = '가속도 법칙(F = ma)'
            expl = '알짜힘, 질량, 가속도의 관계(a = F/m)로 설명된다.'
        body = P('다음 현상 중 %s으로 설명할 수 있는 것은?' % nm if which != 'acc' else '다음 현상 중 %s으로 설명할 수 있는 것은?' % nm)
        return mc(body, right, wrongs, r=r, lv='하', fam='d', sort='shuf', steps=['"%s"은(는) %s' % (right, expl), '나머지는 다른 법칙으로 설명되는 현상이다.'], core='제1법칙은 관성, 제2법칙은 F = ma, 제3법칙은 작용 반작용이다.', point='현상이 세 법칙 중 무엇과 관련되는지 구분한다.')
    # e: 스케이트 선수
    mA, mB = r.sample([40, 50, 60, 70, 80, 45, 55, 65], 2)
    lighter = 'A' if mA < mB else 'B'
    heavier = 'B' if lighter == 'A' else 'A'
    g_ = gcd(mA, mB)
    pa, pb = mB // g_, mA // g_  # aA : aB = mB : mA
    S = [
        ('g1', '서로 밀 때 A가 B에 작용하는 힘의 크기와 B가 A에 작용하는 힘의 크기는 같다.', True, '작용 반작용 관계이므로 크기가 같다.'),
        ('g1', '서로 밀 때 %s가 %s에 작용하는 힘이 %s가 %s에 작용하는 힘보다 크다.' % (heavier, lighter, lighter, heavier), False, '두 힘은 작용 반작용이므로 크기가 같다.'),
        ('g2', '밀려난 직후 가속도의 크기는 %s가 %s보다 크다.' % (lighter, heavier), True, '힘의 크기가 같으므로 질량이 작은 %s의 가속도가 크다.' % lighter),
        ('g2', '밀려난 직후 가속도의 크기는 %s가 %s보다 크다.' % (heavier, lighter), False, '힘의 크기가 같으므로 질량이 작은 %s의 가속도가 더 크다.' % lighter),
        ('g3', 'A와 B의 가속도의 크기의 비는 a%s : a%s = %d : %d 이다.' % (sub('A'), sub('B'), pa, pb), True, 'a ∝ 1/m 이므로 a%s : a%s = m%s : m%s = %d : %d 이다.' % (sub('A'), sub('B'), sub('B'), sub('A'), pa, pb)),
        ('g3', 'A와 B의 가속도의 크기의 비는 a%s : a%s = %d : %d 이다.' % (sub('A'), sub('B'), pb, pa), False, '가속도는 질량에 반비례하므로 a%s : a%s = %d : %d 이다.' % (sub('A'), sub('B'), pa, pb)),
        ('g4', '두 사람이 받는 알짜힘의 방향은 서로 반대이다.', True, '작용 반작용이므로 방향이 반대이다.'),
        ('g4', '두 사람이 받는 알짜힘의 방향은 서로 같다.', False, '작용 반작용의 두 힘은 방향이 반대이다.'),
        ('g5', '두 사람이 서로 미는 힘은 힘의 평형 관계이다.', False, '두 힘은 서로 다른 물체에 작용하므로 힘의 평형이 아니라 작용 반작용이다.'),
        ('g5', '두 사람이 서로 미는 힘은 작용 반작용 관계이다.', True, '서로 다른 두 물체 사이의 한 쌍의 힘이다.'),
    ]
    stm = pick3(S, r)
    return bogi('그림과 같이 마찰이 없는 얼음판 위에 정지해 있던 두 스케이트 선수 A(질량 %d kg), B(질량 %d kg)가 서로 밀어 반대 방향으로 멀어졌다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % (mA, mB), stm, pre=FIG(fig_skaters(mA, mB), '62%'), r=r, ask='', lv='중', fam='e', core='서로 미는 두 힘은 작용 반작용이므로 크기가 같고, 가속도는 질량에 반비례한다.', point='같은 크기의 힘에서 질량이 작은 쪽의 가속도가 크다.')


# ================================================================= ph016
def fig_elev(v_up=None, label='', mtxt='', show_a=None):
    f = Fig(290, 190)
    f.line(145, 4, 145, 38, GR, 2)
    f.rect(90, 38, 110, 130, '#f1f4f8', INK, 2)
    f.rect(108, 150, 74, 12, '#e3e9f1', INK, 1.4)
    f.circ(145, 78, 11, '#fde9d8', INK, 1.6)
    f.line(145, 89, 145, 124, INK, 2.2)
    f.line(145, 124, 133, 150, INK, 2.2); f.line(145, 124, 157, 150, INK, 2.2)
    f.line(145, 98, 130, 112, INK, 2.2); f.line(145, 98, 160, 112, INK, 2.2)
    f.text(145, 181, '저울', 11.5, 'middle', False, GR)
    if mtxt: lab(f, 145, 58, mtxt, INK, 'middle', 12.5)
    if v_up is not None:
        if v_up:
            f.arrow(40, 130, 40, 70, BL, 3)
        else:
            f.arrow(40, 70, 40, 130, BL, 3)
        lab(f, 40, 150, 'v', BL, 'middle', 14)
    if show_a is not None:
        if show_a == 'up':
            f.arrow(245, 130, 245, 70, RD, 3)
        elif show_a == 'down':
            f.arrow(245, 70, 245, 130, RD, 3)
        lab(f, 245, 150, 'a', RD, 'middle', 14)
    return f.svg()


STATE = [('위로 올라가면서 속력이 증가', 'up', True), ('위로 올라가면서 속력이 감소', 'up', False), ('아래로 내려가면서 속력이 증가', 'down', True), ('아래로 내려가면서 속력이 감소', 'down', False)]


def adir(vdir, speeding):
    """가속도 방향: +1 위, -1 아래."""
    if vdir == 'up': return +1 if speeding else -1
    return -1 if speeding else +1


@T('ph016')
def elevator(r, k):
    fam = r.choice(['a'] * 4 + ['c'] * 3 + ['d'] * 3 + ['e'] * 3 + ['f'] * 2 + ['g'] * 2)
    m = r.choice([40, 45, 50, 55, 60, 65, 70, 80])
    a = r.choice([1, 2, 2.5, 3, 4, 0.5, 1.5])
    if fam == 'a':
        txt, vd, sp = r.choice(STATE)
        ad = adir(vd, sp)
        N = m * (G + ad * a)
        # 교차: 위 방향 +, 운동 방정식 N - mg = m a_signed
        assert abs(N - m * G - m * ad * a) < 1e-9
        body = P('그림은 질량 %d kg인 사람이 엘리베이터 안의 체중계(저울) 위에 서 있는 모습을 나타낸 것이다. 엘리베이터가 %s하는 동안 가속도의 크기가 %s m/s²일 때, 체중계가 가리키는 눈금(사람이 체중계를 누르는 힘)의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (m, txt, num(a))) + FIG(fig_elev(vd == 'up', '', '%d kg' % m), '50%')
        wr = WR(N, [m * G, m * (G - ad * a), m * a, m * (G + a) if ad < 0 else m * (G - a), m * G + a, N + m], 'N')
        return mc(body, U(N, 'N'), wr, r=r, lv='중', fam='a', steps=['%s하므로 가속도의 방향은 %s이다.' % (txt, '위쪽' if ad > 0 else '아래쪽'), '위쪽을 +로 하면 N - mg = ma 에서 N = m(g %s a) = %d × (10 %s %s)' % ('+' if ad > 0 else '-', m, '+' if ad > 0 else '-', num(a)), 'N = %s N' % num(N)], core='엘리베이터 안의 저울 눈금 N = m(g ± a): 가속도가 위쪽이면 +, 아래쪽이면 -.', point='속력 변화와 운동 방향으로 가속도 방향을 먼저 정한다.')
    if fam == 'c':
        up = r.random() < .5
        N = m * (G + a) if up else m * (G - a)
        ask = r.choice(['dir', 'mag'])
        body = P('질량 %d kg인 사람이 엘리베이터 안의 체중계 위에 서 있다. 엘리베이터가 운동하는 동안 체중계의 눈금이 %s N이었다. 이때 엘리베이터의 가속도의 크기와 방향을 옳게 짝지은 것은? (단, 중력 가속도는 10 m/s²이다.)' % (m, num(N)))
        right = '%s m/s², %s' % (num(a), '위쪽' if up else '아래쪽')
        wrongs = ['%s m/s², %s' % (num(a), '아래쪽' if up else '위쪽'), '%s m/s², %s' % (num(N / m), '위쪽'), '%s m/s², %s' % (num(N / m), '아래쪽'), '%s m/s², %s' % (num(a * 2), '위쪽' if up else '아래쪽'), '0 m/s², 없음']
        wrongs = [w for w in wrongs if w != right and isnice(float(w.split(' ')[0]))]
        return mc(body, right, wrongs, r=r, lv='중', fam='c', sort='shuf', steps=['정지(등속) 때의 눈금은 mg = %d N 인데 눈금이 %s N 으로 %s.' % (m * G, num(N), '더 크다' if up else '더 작다'), 'N - mg = ma 에서 a = (%s - %d) ÷ %d = %s m/s² (%s)' % (num(N), m * G, m, num((N - m * G) / m), '양수이므로 위쪽' if up else '음수이므로 아래쪽'), '가속도의 크기는 %s m/s², 방향은 %s이다.' % (num(a), '위쪽' if up else '아래쪽')], core='눈금이 mg 보다 크면 가속도가 위쪽, 작으면 아래쪽이다.', point='눈금과 mg 를 비교해 가속도의 방향을 먼저 정한다.')
    if fam == 'd':
        txt, vd, sp = r.choice(STATE)
        ad = adir(vd, sp)
        kg = m * (G + ad * a) / G
        if not isnice(kg, 2): return None
        body = P('질량 %d kg인 사람이 엘리베이터 안의 체중계 위에 서 있다. 엘리베이터가 %s하는 동안 가속도의 크기가 %s m/s²일 때 체중계의 눈금은 몇 kg중인가? (단, 중력 가속도는 10 m/s²이다.)' % (m, txt, num(a))) + FIG(fig_elev(vd == 'up', '', '%d kg' % m), '50%')
        wr = WR(kg, [m, m * (G - ad * a) / G, m * a, m * (1 + a), kg + 5, kg - 5], 'kg중')
        return mc(body, U(kg, 'kg중'), wr, r=r, lv='중', fam='d', steps=['가속도의 방향은 %s이다.' % ('위쪽' if ad > 0 else '아래쪽'), 'N = m(g %s a) = %d × %s = %s N' % ('+' if ad > 0 else '-', m, num(G + ad * a), num(m * (G + ad * a))), '1 kg중 = 10 N 이므로 %s ÷ 10 = %s kg중' % (num(m * (G + ad * a)), num(kg))], core='저울 눈금은 N 을 g 로 나눈 kg중으로도 나타내며 m(1 ± a/g) 이다.', point='N 을 10 으로 나누어 kg중으로 바꾼다.')
    if fam == 'e':
        a1 = r.choice([1, 2])
        t1 = r.choice([2, 4])
        v1 = a1 * t1
        tc = r.choice([2, 4])
        a3 = r.choice([1, 2])
        if v1 % a3: return None
        td = v1 // a3
        t2 = t1 + tc
        t3 = t2 + td
        if t3 > 14: return None
        p = Plot(300, 200, t3 + 1, v1 + 1, ml=44, mr=26, mt=20, mb=32)
        p.axes('t (s)', 'v (m/s)', [0, 2, 4, 6, 8, 10, 12, 14][:int((t3 + 1) // 2) + 1], ticks(v1, 1 if v1 <= 4 else 2), grid=True)
        p.pl([(0, 0), (t1, v1), (t2, v1), (t3, 0)], BL, 2.8)
        for (tx_, tl) in ((t1 / 2, '(가)'), ((t1 + t2) / 2, '(나)'), ((t2 + t3) / 2, '(다)')):
            vy = v1 / 2 if tl != '(나)' else v1
            lab(p, p.px(tx_), p.py(vy) + (22 if tl == '(나)' else -4) if False else (p.py(v1) - 8 if tl == '(나)' else p.py(vy) - 6), tl, GR, 'middle', 12) if True else None
        idx = r.choice([0, 1, 2])
        nm = ['(가)', '(나)', '(다)'][idx]
        acc = [a1, 0, -a3][idx]
        N = m * (G + acc)
        body = P('그림은 질량 %d kg인 사람이 탄 엘리베이터가 연직 방향으로 운동할 때 속도를 시간에 따라 나타낸 것이다(위쪽이 +). 구간 %s에서 체중계의 눈금은? (단, 중력 가속도는 10 m/s²이다.)' % (m, nm)) + FIG(p.svg(), '64%')
        wr = WR(N, [m * G, m * (G + a1), m * (G - a3), m * (G - acc) if acc else m * (G + a1 + 1), m * acc, N + m], 'N')
        stp = ['%s 구간 : 기울기(가속도) = %s m/s²' % (nm, num(acc))]
        stp.append('N = m(g + a) = %d × (10 %s %s) = %s N' % (m, '+' if acc >= 0 else '-', num(abs(acc)), num(N)))
        return mc(body, U(N, 'N'), wr, r=r, lv='상' if idx == 2 else '중', fam='e', steps=stp, core='v-t 그래프의 기울기가 가속도이며, 눈금 N = m(g + a) (위쪽 +).', point='그래프 기울기로 각 구간의 가속도를 구한다.')
    if fam == 'f':
        M = r.choice([200, 300, 400, 500])
        txt, vd, sp = r.choice(STATE)
        ad = adir(vd, sp)
        T = (M + m) * (G + ad * a)
        body = P('질량 %d kg인 엘리베이터 안에 질량 %d kg인 사람이 타고 있다. 엘리베이터가 줄에 매달려 %s하고 있고 가속도의 크기가 %s m/s²일 때 줄이 엘리베이터를 당기는 힘의 크기는? (단, 중력 가속도는 10 m/s²이고, 줄의 질량은 무시한다.)' % (M, m, txt, num(a))) + FIG(fig_elev(vd == 'up', '', '%d kg' % m), '50%')
        wr = WR(T, [(M + m) * G, (M + m) * (G - ad * a), M * (G + ad * a), (M + m) * a, T + m * 10, T - 100], 'N')
        return mc(body, U(T, 'N'), wr, r=r, lv='상', fam='f', steps=['사람과 엘리베이터를 한 덩어리로 보면 질량 %d kg 이다.' % (M + m), '가속도는 %s이므로 T - (M + m)g = (M + m)(%s%s)' % ('위쪽' if ad > 0 else '아래쪽', '+' if ad > 0 else '-', num(a)), 'T = %d × (10 %s %s) = %s N' % (M + m, '+' if ad > 0 else '-', num(a), num(T))], core='엘리베이터와 탑승자 전체에 대해 T - (M + m)g = (M + m)a (위쪽 +) 이다.', point='전체를 한 물체로 보아 장력을 구한다.')
    # g: 상황별 눈금 비교(개념)
    mm = r.choice([40, 50, 60, 70])
    ans_state = r.choice(['up_acc', 'up_dec', 'down_acc', 'const', 'free'])
    names = {'up_acc': '위로 올라가며 속력이 증가한다.', 'up_dec': '위로 올라가며 속력이 감소한다.', 'down_acc': '아래로 내려가며 속력이 증가한다.', 'const': '일정한 속력으로 올라간다.', 'free': '줄이 끊어져 자유 낙하한다.'}
    base = {'up_acc': 1, 'up_dec': -1, 'down_acc': -1, 'const': 0, 'free': -10}
    # 가속도 크기가 a 로 같을 때(자유 낙하 제외) 눈금이 mg 보다 큰 것을 고르게 함
    right = names['up_acc'] if r.random() < .5 else None
    mode = r.choice(['big', 'zero', 'mg'])
    if mode == 'big':
        right = names['up_acc']; wr = [names['up_dec'], names['down_acc'], names['const'], names['free']]
        ask = '속력 변화의 크기(가속도의 크기)가 같을 때 체중계의 눈금이 정지해 있을 때보다 커지는 경우는?'
        st = ['눈금이 mg 보다 커지려면 가속도가 위쪽이어야 한다.', '위로 올라가며 속력이 증가하면 가속도가 위쪽이다. (나머지는 가속도가 아래쪽이거나 0)']
    elif mode == 'zero':
        right = names['free']; wr = [names['up_acc'], names['up_dec'], names['down_acc'], names['const']]
        ask = '체중계의 눈금이 0이 되는 경우는? (단, 공기 저항과 마찰은 무시한다.)'
        st = ['자유 낙하하면 가속도가 g 이므로 N = m(g - g) = 0 이다.']
    else:
        right = names['const']; wr = [names['up_acc'], names['up_dec'], names['down_acc'], names['free']]
        ask = '체중계의 눈금이 정지해 있을 때와 같은 경우는?'
        st = ['등속 운동이면 가속도가 0 이므로 N = mg 로 정지해 있을 때와 같다.']
    body = P('질량 %d kg인 사람이 엘리베이터 안의 체중계 위에 서 있다. %s' % (mm, ask))
    return mc(body, right, wr, r=r, lv='하', fam='g', sort='shuf', steps=st, core='눈금 N = m(g + a): a가 위쪽이면 커지고 아래쪽이면 작아지며, 등속이면 mg 이다.', point='운동 상태로 가속도의 방향을 판단한다.')


# ================================================================= ph017
def fig_pull_floor(mtxt, Ftxt='F', rough=True):
    f = Fig(300, 130)
    fy = 100
    floor(f, 8, 292, fy)
    block(f, 110, fy - 48, 70, 48, mtxt)
    f.arrow(180, fy - 24, 245, fy - 24, RD, 3)
    lab(f, 245, fy - 32, Ftxt, RD, 'middle', 13)
    f.arrow(110, fy - 8, 68, fy - 8, GN, 2.4)
    lab(f, 68, fy - 14, 'f', GN, 'middle', 13)
    return f.svg()


@T('ph017')
def friction(r, k):
    fam = r.choice(['a'] * 3 + ['b'] * 3 + ['c'] * 2 + ['d'] * 3 + ['e'] * 3 + ['f'] * 2)
    if fam == 'a':
        m = r.choice([2, 4, 5, 10, 20])
        mus = r.choice([0.3, 0.4, 0.5, 0.6])
        fmax = mus * m * G
        F = r.choice([x for x in range(2, int(fmax)) if x < fmax - 0.5] or [None])
        if F is None: return None
        body = P('그림과 같이 거친 수평면 위에 질량 %d kg인 물체가 놓여 있다. 물체와 수평면 사이의 정지 마찰 계수는 %s이다. 물체를 수평 방향으로 %d N의 힘으로 당겼지만 물체가 움직이지 않았다. 이때 물체에 작용하는 마찰력의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (m, num(mus), F)) + FIG(fig_pull_floor('%d kg' % m), '62%')
        wr = WR(F, [fmax, mus * F, m * G, fmax - F if fmax - F != F else None, F + 5, F / 2], 'N')
        return mc(body, U(F, 'N'), wr, r=r, lv='중', fam='a', steps=['최대 정지 마찰력 = μs·mg = %s × %d × 10 = %s N 이다.' % (num(mus), m, num(fmax)), '당기는 힘 %d N 은 최대 정지 마찰력보다 작아 물체가 정지해 있다.' % F, '정지해 있으므로 마찰력은 당기는 힘과 같은 %d N 이다.' % F], core='정지한 물체의 정지 마찰력은 외력과 크기가 같고 최댓값 μs·N 을 넘지 못한다.', point='정지 상태에서는 μN 이 아니라 외력과 같은 값이다.')
    if fam == 'b':
        m = r.choice([2, 4, 5, 10, 20])
        muk = r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5])
        fk = muk * m * G
        a = r.randint(1, 5)
        F = fk + m * a
        if not isnice(F, 2) or not isnice(fk): return None
        ask = r.choice(['a', 'a', 'f'])
        if ask == 'a':
            body = P('그림과 같이 거친 수평면 위에 질량 %d kg인 물체가 놓여 있다. 물체와 수평면 사이의 운동 마찰 계수는 %s이다. 물체를 수평 방향으로 %s N의 힘으로 당겼더니 물체가 미끄러지며 운동하였다. 물체의 가속도의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (m, num(muk), num(F))) + FIG(fig_pull_floor('%d kg' % m), '62%')
            wr = WR(a, [F / m, (F + fk) / m, fk / m, (F - fk) / (2 * m), a + 1, a * 2], 'm/s²')
            return mc(body, U(a, 'm/s²'), wr, r=r, lv='중', fam='b', steps=['운동 마찰력 f = μk·mg = %s × %d × 10 = %s N' % (num(muk), m, num(fk)), '알짜힘 = F - f = %s - %s = %s N' % (num(F), num(fk), num(F - fk)), 'a = %s ÷ %d = %d m/s²' % (num(F - fk), m, a)], core='마찰이 있는 수평면에서 ma = F - μk·mg 이다.', point='운동 마찰력을 구해 알짜힘에서 뺀다.')
        body = P('그림과 같이 거친 수평면 위에 질량 %d kg인 물체가 놓여 있다. 물체와 수평면 사이의 운동 마찰 계수는 %s이다. 물체가 미끄러지는 동안 물체에 작용하는 운동 마찰력의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (m, num(muk))) + FIG(fig_pull_floor('%d kg' % m), '62%')
        wr = WR(fk, [m * G, muk * m, fk * 2, F, fk / 2, m * a], 'N')
        return mc(body, U(fk, 'N'), wr, r=r, lv='하', fam='b', steps=['수평면 위이므로 수직 항력 N = mg = %d × 10 = %d N' % (m, m * G), 'f = μk·N = %s × %d = %s N' % (num(muk), m * G, num(fk))], core='운동 마찰력은 f = μk·N 이며 속력에 관계없이 일정하다.', point='수직 항력과 마찰 계수의 곱으로 구한다.')
    if fam == 'c':
        m = r.choice([2, 3, 4, 5, 10])
        a = r.randint(1, 4)
        muk = r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5])
        F = muk * m * G + m * a
        if not isnice(F, 2) or abs(F - round(F)) > 1e-9 or isnice(muk * m * G) is False: return None
        F = int(round(F))
        body = P('거친 수평면 위에 놓인 질량 %d kg인 물체를 수평 방향으로 %d N의 힘으로 당겼더니 %d m/s²의 가속도로 운동하였다. 물체와 수평면 사이의 운동 마찰 계수는? (단, 중력 가속도는 10 m/s²이다.)' % (m, F, a))
        wr = WR(muk, [F / (m * G), a / G, (F + m * a) / (m * G), muk * 2, muk / 2, muk + 0.1], '')
        wr = [w.strip() for w in wr]
        return mc(body, num(muk), wr, r=r, lv='상', fam='c', steps=['알짜힘 = ma = %d × %d = %d N' % (m, a, m * a), '운동 마찰력 f = F - ma = %d - %d = %d N' % (F, m * a, F - m * a), 'μk = f ÷ mg = %d ÷ %d = %s' % (F - m * a, m * G, num(muk))], core='F - μk·mg = ma 에서 μk = (F - ma)/(mg) 이다.', point='알짜힘으로 마찰력을 구한 뒤 마찰 계수를 구한다.')
    if fam == 'd':
        m = r.choice([2, 4, 5, 10])
        mus = r.choice([0.4, 0.5, 0.6, 0.3, 0.8])
        muk = r.choice([0.2, 0.25, 0.3, 0.4])
        if muk >= mus: return None
        fs, fk = mus * m * G, muk * m * G
        if not isnice(fs) or not isnice(fk): return None
        xmax = math.ceil((fs + 6) / 2) * 2
        ymax = math.ceil(fs / 2) * 2 + 2
        p = Plot(300, 215, xmax, ymax, ml=46, mr=26, mt=18, mb=32)
        stx = 2 if xmax <= 24 else 4
        p.axes('F (N)', 'f (N)', ticks(xmax, stx), ticks(ymax, 2 if ymax <= 16 else 4), grid=True)
        p.pl([(0, 0), (fs, fs)], RD, 2.8)
        p.pl([(fs, fs), (fs, fk)], RD, 2.0, '4 3')
        p.pl([(fs, fk), (xmax * .95, fk)], RD, 2.8)
        p.dash_to_axes(fs, fs); p.dash_to_axes(xmax * .95, fk) if False else None
        p.line(p.px(0), p.py(fk), p.px(fs), p.py(fk), GR, 1, '4 3')
        lab(p, p.px(0) - 7, p.py(fk) + 4, num(fk), GR, 'end', 11.5) if fk not in ticks(ymax, 2) else None
        p.circ(p.px(fs), p.py(fs), 3.5, INK, INK)
        fig = FIG(p.svg(), '66%')
        base = '그림은 거친 수평면 위에 놓인 질량 %d kg인 물체를 수평 방향의 힘 F로 당길 때 물체에 작용하는 마찰력 f를 F에 따라 나타낸 것이다. ' % m
        gt = '(단, 중력 가속도는 10 m/s²이다.)'
        ask = r.choice(['mus', 'muk', 'a'])
        if ask == 'mus':
            body = P(base + '물체와 수평면 사이의 정지 마찰 계수는? ' + gt) + fig
            wr = WR(mus, [muk, fs / 10, fk / (m * G) * 2, mus + 0.1, mus / 2, mus * 2], '')
            return mc(body, num(mus), [w.strip() for w in wr], r=r, lv='중', fam='d', steps=['F = %s N 까지 마찰력이 F 와 같다가 이때 최대(최대 정지 마찰력)가 된다.' % num(fs), 'μs = fmax ÷ mg = %s ÷ %d = %s' % (num(fs), m * G, num(mus))], core='마찰력 그래프의 최댓값이 최대 정지 마찰력(μs·N)이다.', point='그래프의 꼭짓점 값을 읽어 μs 를 구한다.')
        if ask == 'muk':
            body = P(base + '물체와 수평면 사이의 운동 마찰 계수는? ' + gt) + fig
            wr = WR(muk, [mus, fk / 10, mus / 2, muk + 0.1, muk * 2, muk / 2], '')
            return mc(body, num(muk), [w.strip() for w in wr], r=r, lv='중', fam='d', steps=['물체가 움직이기 시작한 뒤 마찰력은 일정하게 %s N 이다.' % num(fk), 'μk = f ÷ mg = %s ÷ %d = %s' % (num(fk), m * G, num(muk))], core='물체가 미끄러지기 시작하면 마찰력은 운동 마찰력으로 일정해진다.', point='그래프에서 F가 커진 뒤의 일정한 마찰력이 운동 마찰력이다.')
        F2 = fs + r.choice([2, 4, 6])
        a2 = (F2 - fk) / m
        if not isnice(a2, 2) or F2 > xmax: return None
        body = P(base + 'F = %s N로 당길 때 물체의 가속도의 크기는? ' % num(F2) + gt) + fig
        wr = WR(a2, [F2 / m, (F2 - fs) / m, fk / m, (F2 + fk) / m, a2 + 1, a2 * 2], 'm/s²')
        return mc(body, U(a2, 'm/s²'), wr, r=r, lv='상', fam='d', steps=['F = %s N 는 최대 정지 마찰력 %s N 보다 크므로 물체가 미끄러지며 마찰력은 %s N 이다.' % (num(F2), num(fs), num(fk)), 'a = (F - f) ÷ m = (%s - %s) ÷ %d = %s m/s²' % (num(F2), num(fk), m, num(a2))], core='움직이는 동안의 마찰력은 일정한 운동 마찰력이다.', point='그래프에서 운동 마찰력을 읽어 알짜힘을 구한다.')
    if fam == 'e':
        th = r.choice([37, 53])
        m = r.choice([1, 2, 3, 4, 5])
        mode = r.choice(['rest', 'a', 'slide?'])
        fig = FIG(fig_incline(th), '56%')
        if mode == 'rest':
            fv = m * G * SINV[th]
            body = P('그림과 같이 경사각이 %d°인 거친 빗면 위에 질량 %d kg인 물체가 정지해 있다. 물체에 작용하는 마찰력의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (th, m)) + fig
            wr = WR(fv, [m * G * COSV[th], m * G, fv * 2, fv / 2, m * G * (SINV[th] + COSV[th]), fv + 5], 'N')
            return mc(body, U(fv, 'N'), wr, r=r, lv='중', fam='e', steps=['정지해 있으므로 빗면 방향의 힘이 평형이다 : f = mg sin%d°' % th, 'f = %d × 10 × %s = %s N' % (m, SINS[th], num(fv))], core='빗면에서 정지한 물체의 정지 마찰력은 mg sinθ 와 같다.', point='정지 상태이므로 마찰력은 μN 이 아니라 mg sinθ 이다.')
        if mode == 'a':
            mu = r.choice([0.25, 0.5])
            av = G * (SINV[th] - mu * COSV[th])
            if av <= 0 or not isnice(av): return None
            body = P('그림과 같이 경사각이 %d°인 거친 빗면 위에서 질량 %d kg인 물체가 미끄러져 내려온다. 물체와 빗면 사이의 운동 마찰 계수가 %s일 때 물체의 가속도의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (th, m, num(mu))) + fig
            Nv = m * G * COSV[th]
            fk = mu * Nv
            assert abs((m * G * SINV[th] - fk) / m - av) < 1e-9
            wr = WR(av, [G * SINV[th], G * (SINV[th] + mu * COSV[th]), G * (COSV[th] - mu * SINV[th]) if COSV[th] > mu * SINV[th] else None, mu * G, av + 1, av / 2], 'm/s²')
            return mc(body, U(av, 'm/s²'), wr, r=r, lv='상', fam='e', steps=['수직 항력 N = mg cos%d° = %s N, 운동 마찰력 f = μN = %s × %s = %s N' % (th, num(Nv), num(mu), num(Nv), num(fk)), '빗면 방향 : ma = mg sin%d° - f = %s - %s = %s N' % (th, num(m * G * SINV[th]), num(fk), num(m * G * SINV[th] - fk)), 'a = %s ÷ %d = %s m/s²' % (num(m * G * SINV[th] - fk), m, num(av))], core='거친 빗면에서 a = g(sinθ - μ cosθ) 이다.', point='수직 항력에서 마찰력을 구해 빗면 방향 알짜힘에 반영한다.')
        mu = r.choice([0.5, 0.6, 0.75, 1.0, 1.2])
        tanv = SINV[th] / COSV[th]
        if abs(mu - tanv) < 1e-9: return None
        slides = tanv > mu
        body = P('경사각이 %d°인 빗면 위에 물체를 가만히 놓았다. 물체와 빗면 사이의 정지 마찰 계수가 %s일 때 물체의 운동에 대한 설명으로 옳은 것은? (단, 정지 마찰 계수와 운동 마찰 계수는 같다고 본다.)' % (th, num(mu))) + fig
        right = '미끄러져 내려간다.' if slides else '정지해 있는다.'
        wrongs = ['미끄러져 내려가지만 가속도는 g sin%d° 이다.' % th if False else '빗면 위로 올라간다.', '일정한 속력으로 미끄러진다.' if slides else '미끄러져 내려간다.', '가속도가 g sin%d° 로 미끄러진다.' % th, '운동 상태를 알 수 없다.']
        wrongs = [w for w in wrongs if w != right]
        return mc(body, right, wrongs, r=r, lv='상', fam='e', sort='shuf', steps=['빗면 방향 중력 성분 mg sin%d° 과 최대 정지 마찰력 μmg cos%d° 를 비교한다 : tan%d° = %s, μ = %s' % (th, th, th, fr(Fraction(SINV[th] / COSV[th]).limit_denominator(10)) if True else '', num(mu)), ('tan%d° > μ 이므로 미끄러진다.' if slides else 'tan%d° < μ 이므로 정지해 있는다.') % th], core='빗면에서 tanθ > μs 이면 미끄러지고 tanθ ≤ μs 이면 정지한다.', point='tanθ 와 정지 마찰 계수를 비교한다.')
    # f: μs, μk 쌍
    m = r.choice([2, 4, 5, 10])
    mus = r.choice([0.4, 0.5, 0.6, 0.3])
    muk = r.choice([0.2, 0.25, 0.3, 0.1])
    if muk >= mus: return None
    fs, fk = mus * m * G, muk * m * G
    if not isnice(fs) or not isnice(fk): return None
    body = P('거친 수평면 위에 놓인 질량 %d kg인 물체를 수평 방향으로 당기는 힘을 서서히 증가시켰더니 힘이 %s N일 때 물체가 움직이기 시작했다. 움직이기 시작한 후에는 %s N의 힘으로 당길 때 물체가 등속도로 운동하였다. 물체와 수평면 사이의 정지 마찰 계수 μs 와 운동 마찰 계수 μk 를 차례대로 구한 것은? (단, 중력 가속도는 10 m/s²이다.)' % (m, num(fs), num(fk)))
    right = '%s, %s' % (num(mus), num(muk))
    wrongs = ['%s, %s' % (num(muk), num(mus)), '%s, %s' % (num(fs), num(fk)), '%s, %s' % (num(mus), num(mus)), '%s, %s' % (num(mus * 2), num(muk)), '%s, %s' % (num(mus), num(muk * 2))]
    return mc(body, right, wrongs, r=r, lv='중', fam='f', sort='shuf', steps=['움직이기 시작하는 순간의 힘 = 최대 정지 마찰력 = %s N 이므로 μs = %s ÷ %d = %s' % (num(fs), num(fs), m * G, num(mus)), '등속 운동 중에는 알짜힘이 0 이므로 운동 마찰력 = %s N, μk = %s ÷ %d = %s' % (num(fk), num(fk), m * G, num(muk))], core='최대 정지 마찰력 = μs·mg, 등속 운동 때의 힘 = 운동 마찰력 = μk·mg 이다.', point='움직이기 시작하는 순간과 등속 운동 때의 힘을 구분한다.')


# ================================================================= ph018
def _tbl(rows, hdr):
    return table(hdr, rows)


@T('ph018')
def eq_analysis(r, k):
    fam = r.choice(['a'] * 4 + ['b'] * 3 + ['c'] * 3 + ['d'] * 3)
    if fam == 'a':
        for _ in range(30):
            m1, m2, m3 = r.sample([1, 2, 3, 4, 5, 6], 3)
            a1, a2, a3 = r.sample([1, 2, 3, 4, 5, 6], 3)
            F1, F2, F3 = m1 * a1, m2 * a2, m3 * a3
            break
        rows = [['Ⅰ', m1, F1, a1], ['Ⅱ', m2, F2, 'ⓐ'], ['Ⅲ', 'ⓑ', F3, a3]]
        # 모든 실험은 마찰 없는 수평면에서 같은 물체가 아닌 서로 다른 물체의 운동이라고 가정
        S = [
            ('g1', 'ⓐ는 %d이다.' % a2, True, '실험 Ⅱ : a = F ÷ m = %d ÷ %d = %d 이다.' % (F2, m2, a2)),
            ('g1', 'ⓐ는 %d이다.' % (a2 + r.choice([1, 2])), False, '실험 Ⅱ : a = F ÷ m = %d ÷ %d = %d 이다.' % (F2, m2, a2)),
            ('g2', 'ⓑ는 %d이다.' % m3, True, '실험 Ⅲ : m = F ÷ a = %d ÷ %d = %d 이다.' % (F3, a3, m3)),
            ('g2', 'ⓑ는 %d이다.' % (m3 + r.choice([1, 2])), False, '실험 Ⅲ : m = F ÷ a = %d ÷ %d = %d 이다.' % (F3, a3, m3)),
            ('g3', '실험 Ⅰ, Ⅱ, Ⅲ 중 알짜힘이 가장 큰 것은 Ⅰ이다.', max(F1, F2, F3) == F1, '알짜힘은 Ⅰ : %d N, Ⅱ : %d N, Ⅲ : %d N 이다.' % (F1, F2, F3)),
            ('g3', '실험 Ⅰ, Ⅱ, Ⅲ 중 알짜힘이 가장 큰 것은 Ⅲ이다.', max(F1, F2, F3) == F3, '알짜힘은 Ⅰ : %d N, Ⅱ : %d N, Ⅲ : %d N 이다.' % (F1, F2, F3)),
            ('g4', '질량이 가장 큰 물체는 Ⅰ이다.', max(m1, m2, m3) == m1, '질량은 Ⅰ : %d kg, Ⅱ : %d kg, Ⅲ : %d kg 이다.' % (m1, m2, m3)),
            ('g4', '가속도가 가장 큰 실험은 Ⅱ이다.', max(a1, a2, a3) == a2, '가속도는 Ⅰ : %d, Ⅱ : %d, Ⅲ : %d m/s² 이다.' % (a1, a2, a3)),
            ('g5', '각 실험에서 (알짜힘) ÷ (가속도)는 물체의 질량과 같다.', True, 'F = ma 이므로 F/a = m 이다.'),
            ('g5', '각 실험에서 (알짜힘) × (질량)은 가속도와 같다.', False, 'a = F/m 이므로 (알짜힘) ÷ (질량)이 가속도이다.'),
        ]
        stm = pick3(S, r)
        return bogi('표는 마찰이 없는 수평면에서 운동하는 물체 Ⅰ, Ⅱ, Ⅲ에 대한 질량, 알짜힘, 가속도를 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, pre=_tbl(rows, ['실험', '질량(kg)', '알짜힘(N)', '가속도(m/s²)']), r=r, ask='', lv='중', fam='a', core='각 실험에서 F = ma 가 성립하므로 표의 두 값으로 나머지 값을 구한다.', point='표의 값으로 F = ma 를 적용하고 선택지를 하나씩 검증한다.')
    if fam == 'b':
        m1, m2, a = r.randint(1, 6), r.randint(1, 6), r.randint(1, 5)
        F = (m1 + m2) * a
        T = m1 * a
        side = r.choice(['right'])
        fig = FIG(fig_row([('A', '%d kg' % m1), ('B', '%d kg' % m2)], ['rope'], 'right', 'F'), '70%')
        S = [
            ('g1', 'A, B의 가속도의 크기는 %d m/s²이다.' % a, True, 'a = F ÷ (m%s + m%s) = %d ÷ %d = %d m/s² 이다.' % (sub('A'), sub('B'), F, m1 + m2, a)),
            ('g1', 'A, B의 가속도의 크기는 %d m/s²이다.' % (F // m2 if F % m2 == 0 and F // m2 != a else a + 1), False, '전체 질량 %d kg 으로 나눈 a = %d m/s² 이다.' % (m1 + m2, a)),
            ('g2', '줄이 A를 당기는 힘의 크기는 %d N이다.' % T, True, '줄이 A를 당기는 힘 T = m%sa = %d × %d = %d N 이다.' % (sub('A'), m1, a, T)),
            ('g2', '줄이 A를 당기는 힘의 크기는 %d N이다.' % F, False, 'T = m%sa = %d × %d = %d N 이다. %d N 은 F 의 크기이다.' % (sub('A'), m1, a, T, F)),
            ('g3', '줄이 A를 당기는 힘의 크기와 줄이 B를 당기는 힘의 크기는 같다.', True, '가벼운 줄의 장력은 양 끝에서 같다.'),
            ('g3', '줄이 B를 당기는 힘의 크기는 줄이 A를 당기는 힘의 크기보다 작다.', False, '줄의 질량을 무시하면 줄의 장력은 어디서나 같다.'),
            ('g4', '줄에 걸리는 장력은 F 보다 작다.', True, 'B에는 F 와 장력이 반대로 작용해 가속시키므로 T = F - m%sa < F 이다.' % sub('B')),
            ('g4', '줄에 걸리는 장력은 F 와 같다.', False, 'T = %d N 이고 F = %d N 으로 T < F 이다.' % (T, F)),
            ('g5', 'A와 B에 작용하는 알짜힘의 크기의 비는 %d : %d 이다.' % (m1 // gcd(m1, m2), m2 // gcd(m1, m2)), True, '두 물체의 가속도가 같으므로 알짜힘의 비는 질량의 비 %d : %d 이다.' % (m1, m2)),
            ('g5', 'A와 B에 작용하는 알짜힘의 크기는 서로 같다.', m1 == m2, '두 물체의 가속도가 같으므로 알짜힘의 비는 질량의 비 %d : %d 이다.' % (m1, m2)),
        ]
        stm = pick3(S, r)
        return bogi('그림과 같이 마찰이 없는 수평면에서 질량이 각각 %d kg, %d kg인 물체 A, B를 가벼운 줄로 연결하고 B에 수평 방향으로 크기 %d N의 힘 F를 작용시켰다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % (m1, m2, F), stm, pre=fig, r=r, ask='', lv='중', fam='b', core='줄로 연결된 두 물체는 가속도가 같고, 줄의 장력은 양 끝에서 같다.', point='전체와 개별 물체에 F = ma 를 적용해 선택지를 검증한다.')
    if fam == 'c':
        for _ in range(40):
            M, m = r.randint(1, 8), r.randint(1, 8)
            a = G * m / (M + m)
            T = G * M * m / (M + m)
            if isnice(a) and isnice(T): break
        else:
            return None
        fig = FIG(fig_table_full('A', '%d kg' % M, 'B', '%d kg' % m), '60%')
        S = [
            ('g1', '가속도의 크기는 %s m/s²이다.' % num(a), True, 'a = mg ÷ (M + m) = %d ÷ %d = %s m/s² 이다.' % (m * G, M + m, num(a))),
            ('g1', '가속도의 크기는 %s m/s²이다.' % num(G), False, '10 m/s² 은 B가 자유 낙하할 때의 가속도이다. 실제 a = %s m/s² 이다.' % num(a)),
            ('g2', '줄의 장력의 크기는 %s N이다.' % num(T), True, 'T = Ma = %d × %s = %s N 이다.' % (M, num(a), num(T))),
            ('g2', '줄의 장력의 크기는 %d N이다.' % (m * G), False, 'B의 무게는 %d N 이지만 가속 중이므로 T = %s N 이다.' % (m * G, num(T))),
            ('g3', '줄의 장력의 크기는 B의 무게보다 작다.', True, 'B는 아래로 가속하므로 mg > T 이다.'),
            ('g3', '줄의 장력의 크기는 B의 무게와 같다.', False, 'B가 가속하므로 장력은 B의 무게보다 작다.'),
            ('g4', 'A에 작용하는 알짜힘의 크기는 줄의 장력과 같다.', True, '수평 방향으로는 장력만 작용한다.'),
            ('g4', 'A에 작용하는 알짜힘의 크기는 A의 무게와 같다.', False, 'A의 무게는 수직 항력과 평형을 이루며 알짜힘은 장력이다.'),
            ('g5', 'A와 B의 가속도의 크기는 같다.', True, '줄이 늘어나지 않으므로 같다.'),
            ('g5', 'A의 가속도의 크기가 B보다 크다.', False, '줄로 연결되어 가속도가 같다.'),
        ]
        stm = pick3(S, r)
        return bogi('그림과 같이 마찰이 없는 수평 책상 위의 물체 A(질량 %d kg)와 책상 옆에 매달린 물체 B(질량 %d kg)를 줄로 연결해 가만히 놓았다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량 및 도르래의 마찰은 무시한다.)' % (M, m), stm, pre=fig, r=r, ask='', lv='상' if r.random() < .5 else '중', fam='c', core='책상 위 물체에서는 T = Ma, 매달린 물체에서는 mg - T = ma 이다.', point='두 물체의 운동 방정식을 세워 선택지를 검증한다.')
    # d: 마찰이 있는 수평면 — 두 실험으로 질량과 마찰력 구하기
    m = r.choice([2, 3, 4, 5])
    f = r.choice([2, 3, 4, 5, 6, 8])
    Fa, Fb = f + m * r.randint(1, 3), f + m * r.randint(4, 7)
    aa, ab = (Fa - f) // m, (Fb - f) // m
    Fc = f + m * r.randint(8, 10)
    ac = (Fc - f) // m
    rows = [['(가)', Fa, aa], ['(나)', Fb, ab], ['(다)', Fc, 'ⓐ']]
    S = [
        ('g1', '물체의 질량은 %d kg이다.' % m, True, '(나)-(가) : ΔF = mΔa 에서 m = (%d - %d) ÷ (%d - %d) = %d kg 이다.' % (Fb, Fa, ab, aa, m)),
        ('g1', '물체의 질량은 %d kg이다.' % (m + r.choice([1, 2])), False, '(나)-(가) : m = ΔF ÷ Δa = (%d - %d) ÷ (%d - %d) = %d kg 이다.' % (Fb, Fa, ab, aa, m)),
        ('g2', '물체에 작용하는 마찰력의 크기는 %d N이다.' % f, True, 'F - f = ma 에서 f = %d - %d × %d = %d N 이다.' % (Fa, m, aa, f)),
        ('g2', '물체에 작용하는 마찰력의 크기는 %d N이다.' % (f + m), False, 'f = F - ma = %d - %d × %d = %d N 이다.' % (Fa, m, aa, f)),
        ('g3', 'ⓐ는 %d이다.' % ac, True, 'a = (F - f) ÷ m = (%d - %d) ÷ %d = %d m/s² 이다.' % (Fc, f, m, ac)),
        ('g3', 'ⓐ는 %d이다.' % (ac + 1), False, 'a = (F - f) ÷ m = (%d - %d) ÷ %d = %d m/s² 이다.' % (Fc, f, m, ac)),
        ('g4', '가속도는 당기는 힘 F 에 비례한다.', False, 'a = (F - f)/m 이므로 a 는 F 에 일차 함수 관계이지만 정비례하지는 않는다.'),
        ('g4', '당기는 힘이 %d N 이하이면 물체는 가속되지 않는다.' % f, True, 'F ≤ f 이면 알짜힘이 0 이하이므로 가속되지 않는다.'),
        ('g5', '(가)~(다) 에서 물체에 작용하는 마찰력의 크기는 모두 같다.', True, '운동 마찰력은 속력과 힘의 크기에 관계없이 일정하다.'),
        ('g5', '당기는 힘이 클수록 물체에 작용하는 마찰력도 커진다.', False, '운동 마찰력은 일정하며 당기는 힘과 무관하다.'),
    ]
    stm = pick3(S, r)
    return bogi('표는 거친 수평면에서 같은 물체를 수평 방향의 힘 F로 당겼을 때 물체의 가속도를 나타낸 것이다(물체는 계속 미끄러진다). 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, pre=_tbl(rows, ['실험', 'F (N)', '가속도 (m/s²)']), r=r, ask='', lv='상', fam='d', core='마찰이 있는 수평면에서 F - f = ma 이며 두 실험으로 질량과 마찰력을 구할 수 있다.', point='두 실험의 식을 연립해 질량과 마찰력을 구한 뒤 선택지를 검증한다.')
