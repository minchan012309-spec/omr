# -*- coding: utf-8 -*-
"""Ⅰ-G 역학적 에너지 (ph049~ph056)."""
from phlib import *
import math
from fractions import Fraction as Fr

G = 10
_COS = {0: Fr(1), 37: Fr(4, 5), 53: Fr(3, 5), 60: Fr(1, 2), 90: Fr(0), 180: Fr(-1)}
_SIN = {0: Fr(0), 30: Fr(1, 2), 37: Fr(3, 5), 53: Fr(4, 5), 60: None, 90: Fr(1), 180: Fr(0)}


# ------------------------------------------------------------------ 공통 도구
def _F(x, nd=2):
    if isinstance(x, Fr): x = float(x)
    return num(x, nd)


def _fx(x):
    x = Fr(x).limit_denominator(10000)
    return str(x.numerator) if x.denominator == 1 else '%d/%d' % (x.numerator, x.denominator)


def _ws(right, cands, fmt=None, pos=True):
    """오답 후보 -> 서식 문자열(정답·중복·무한소수 제외). 모자라면 흔한 배수로 채운다."""
    fmt = fmt or _F
    right = Fr(right).limit_denominator(10000)
    seen = {fmt(right)}
    out = []
    ex = [right * 2, right / 2, right * 3, right / 3, right * 4, right / 4, right + 1, right - 1, right + 2, right - 2, right * Fr(3, 2), right * Fr(2, 3), right + 5, right * 5, right / 5]
    for c in list(cands) + ex:
        c = Fr(c).limit_denominator(10000)
        if pos and c <= 0: continue
        dd = c.denominator
        while dd % 2 == 0: dd //= 2
        while dd % 5 == 0: dd //= 5
        if dd != 1: continue
        s = fmt(c)
        if s in seen: continue
        seen.add(s); out.append(s)
    return out[:5]


def _isq(x):
    """x(Fraction) 가 완전제곱수(정수)이면 그 제곱근(정수), 아니면 None."""
    x = Fr(x)
    if x.denominator != 1 or x < 0: return None
    q = math.isqrt(int(x))
    return q if q * q == x else None


def _ok(x, dens=(1, 2, 4, 5, 10, 20, 25, 100)):
    return Fr(x).denominator in dens


def _hatch(f, x, y, w, step=8):
    f.line(x, y, x + w, y, GR, 1.8)
    i = 0.0
    while i <= w:
        f.line(x + i, y, x + i - 5, y + 7, GR, 1)
        i += step


def _dim_v(f, x, y1, y2, label, c=INK, side='left'):
    """세로 치수선 y1(위) ~ y2(아래)."""
    f.line(x, y1, x, y2, c, 1.2)
    f.line(x - 4, y1, x + 4, y1, c, 1.2); f.line(x - 4, y2, x + 4, y2, c, 1.2)
    if side == 'left': f.text(x - 5, (y1 + y2) / 2 + 4, label, 12.5, 'end', True, c)
    else: f.text(x + 6, (y1 + y2) / 2 + 4, label, 12.5, 'start', True, c)


def _dim_h(f, x1, x2, y, label, c=INK):
    f.line(x1, y, x2, y, c, 1.2)
    f.line(x1, y - 4, x1, y + 4, c, 1.2); f.line(x2, y - 4, x2, y + 4, c, 1.2)
    f.text((x1 + x2) / 2, y + 15, label, 12.5, 'middle', True, c)


def _block(f, x, y, w=34, h=24, fill='#cfe2f7', label=None):
    f.rect(x - w / 2, y - h, w, h, fill, INK, 1.6)
    if label: f.text(x, y - h / 2 + 4.5, label, 12.5, 'middle', True, INK)


def _smooth_path(pts):
    """Catmull-Rom 곡선(열린)."""
    P_ = [pts[0]] + list(pts) + [pts[-1]]
    d = 'M %.1f %.1f' % pts[0]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += ' C %.1f %.1f, %.1f %.1f, %.1f %.1f' % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d


def _track_fig(points, w=320, h=215, unit='m', start_label=None):
    """points: [(이름, 높이)] 를 지나는 매끄러운 트랙. 왼쪽에 높이 눈금선을 그린다."""
    f = Fig(w, h)
    y0 = h - 24
    hmax = max(p[1] for p in points)
    sc = min(150.0 / hmax, 16)
    x_l, x_r = 52, w - 20
    n = len(points)
    xs = [x_l + 8 + (x_r - x_l - 16) * i / (n - 1) for i in range(n)]
    pts = [(xs[i], y0 - points[i][1] * sc) for i in range(n)]
    f.line(x_l - 4, y0, w - 10, y0, GR, 1.6)
    f.line(x_l - 4, y0, x_l - 4, y0 - hmax * sc - 14, GR, 1.2)
    # 트랙
    full = [(x_l, pts[0][1] - 0)] + pts + [(x_r + 6, pts[-1][1])]
    f.path(_smooth_path(full), 'none', INK, 2.4)
    for (nm_, hh), (x, y) in zip(points, pts):
        f.line(x_l - 4, y, x, y, '#9fb0c6', 1, '3 3')
        f.circ(x, y, 4.5, BL, INK, 1)
        f.text(x, y - 9, nm_, 13.5, 'middle', True, INK, True)
        f.text(x_l - 8, y + 4, num(hh), 12, 'end', True, GR)
    f.text(x_l - 8, y0 + 15, '0', 12, 'end', True, GR)
    f.text(14, 12, '높이(%s)' % unit, 12, 'start', True, GR)
    return f.svg()


def _incline_fig(theta, hlab=None, llab=None, w=300, h=190, ground='마찰 없음', rough=False, block=True):
    f = Fig(w, h)
    x0, y0 = 30, h - 22
    th = math.radians(theta)
    Lp = min(220 / math.cos(th), (h - 50) / math.sin(th))
    x1, y1 = x0 + Lp * math.cos(th), y0 - Lp * math.sin(th)
    f.poly([(x0, y0), (x1, y0), (x1, y1)], '#f1f4f8', INK, 1.8)
    if block:
        px, py = x1 - 0.12 * (x1 - x0), y1 + 0.12 * (y0 - y1)
        f.o.append('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="28" height="20" fill="#cfe2f7" stroke="%s" stroke-width="1.6"/></g>' % (Fig._n(-theta), Fig._n(px), Fig._n(py), Fig._n(px - 14), Fig._n(py - 20), INK))
    f.o.append('<path d="M %s %s A 34 34 0 0 0 %s %s" fill="none" stroke="%s" stroke-width="1.2"/>' % (Fig._n(x0 + 34), Fig._n(y0), Fig._n(x0 + 34 * math.cos(th)), Fig._n(y0 - 34 * math.sin(th)), GR))
    f.text(x0 + 44, y0 - 5, '%d°' % theta, 12.5, 'start', True, GR)
    if hlab: _dim_v(f, x1 + 12, y1, y0, hlab, RD, 'right')
    if llab:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        f.text(mx - 8 * math.sin(th) - 4, my - 8 * math.cos(th) - 2, llab, 12.5, 'end', True, BL, rot=-theta)
    return f.svg(), (x0, y0, x1, y1)


# ================================================================== ph049 일과 운동 에너지 정리
def _pull_fig(theta, F, s, w=300, h=150, f_lab=True):
    f = Fig(w, h)
    y0 = 100
    _hatch(f, 20, y0, w - 40)
    bx = 90
    _block(f, bx, y0, 44, 30, label='')
    cx, cy = bx + 22, y0 - 15
    th = math.radians(theta)
    L = 62
    f.arrow(cx if theta != 180 else bx - 22, cy, (cx if theta != 180 else bx - 22) + L * math.cos(th), cy - L * math.sin(th), RD, 2.6)
    ex = (cx if theta != 180 else bx - 22) + L * math.cos(th)
    ey = cy - L * math.sin(th)
    f.text(ex + (8 if theta != 180 else -8), ey - 4, 'F = %s N' % _F(F), 13, 'start' if theta != 180 else 'end', True, RD)
    if theta not in (0, 180):
        f.o.append('<path d="M %s %s A 30 30 0 0 0 %s %s" fill="none" stroke="%s" stroke-width="1.2"/>' % (Fig._n(cx + 30), Fig._n(cy), Fig._n(cx + 30 * math.cos(th)), Fig._n(cy - 30 * math.sin(th)), GR))
        f.text(cx + 36, cy - 6 if theta < 60 else cy - 12, '%d°' % theta, 12, 'start', True, GR)
    f.arrow(bx - 22, y0 + 24, bx - 22 + 120, y0 + 24, BL, 2)
    f.text(bx + 40, y0 + 42, '이동 거리 s = %s m' % _F(s), 12.5, 'middle', True, BL)
    return f.svg()


def _fs_fig(pts, w=300, h=190):
    smax = max(p[0] for p in pts)
    fmax = max(p[1] for p in pts)
    fmin = min(0, min(p[1] for p in pts))
    pl = Plot(w, h, smax * 1.12, fmax * 1.18, ymin=fmin * 1.4 if fmin < 0 else 0, ml=46, mb=30)
    xt = sorted({p[0] for p in pts})
    yt = sorted({p[1] for p in pts if p[1] != 0})
    pl.axes('s (m)', 'F (N)', xticks=xt, yticks=yt, grid=True)
    pl.pl(pts, BL, 2.6)
    return pl.svg()


def _area(pts):
    a = Fr(0)
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        a += Fr(x2 - x1) * (Fr(y1) + Fr(y2)) / 2
    return a


@T('ph049')
def work_energy(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'd', 'e'])
    if fam == 'a':
        th = r.choice([0, 37, 53, 60, 90, 180, 37, 53, 60])
        F = r.choice([10, 15, 20, 25, 30, 40, 50])
        s = r.randint(2, 10)
        W = F * s * _COS[th]
        if not _ok(W): return None
        fig = FIG(_pull_fig(th, F, s), '58%')
        body = P('그림과 같이 수평면 위의 물체에 크기가 %s N인 힘 F가 수평 방향과 %d°를 이루며 작용하여 물체가 오른쪽으로 %s m 이동하였다. 이 힘 F가 물체에 한 일은?' % (_F(F), th, _F(s)) if th not in (0, 90, 180) else
                 '그림과 같이 수평면 위의 물체에 크기가 %s N인 힘 F가 %s 작용하는 동안 물체가 오른쪽으로 %s m 이동하였다. 이 힘 F가 물체에 한 일은?' % (_F(F), {0: '이동 방향(오른쪽)으로', 90: '연직 위 방향으로', 180: '이동 방향과 반대인 왼쪽으로'}[th], _F(s))) + fig
        sinv = {0: 0, 37: Fr(3, 5), 53: Fr(4, 5), 60: Fr(87, 100), 90: 1, 180: 0}[th]
        cands = [F * s, -W if W else F * s * 2, F * s * (1 - _COS[th]) if th not in (0, 90) else F * s / 2, F * s * sinv, W * 2, F * s * Fr(1, 2)]
        ws = _ws(W, cands, lambda c: _F(c) + ' J', pos=False)
        assert W == F * s * _COS[th]
        lv = '하' if th in (0, 90, 180) else '중'
        return mc(body, '%s J' % _F(W), ws, r=r, lv=lv, fam='a', sort='num',
                  steps=['일 W = F s cosθ 이다.', 'W = %s × %s × cos%d° = %s J' % (_F(F), _F(s), th, _F(W))] + (['θ = 90°이면 힘이 이동 방향에 수직이므로 일을 하지 않는다.'] if th == 90 else []) + (['θ = 180°이므로 일은 음(-)이다.'] if th == 180 else []),
                  core='힘이 한 일 W = Fs cosθ (θ: 힘과 이동 방향이 이루는 각).', point='힘의 이동 방향 성분만 일을 한다.')
    if fam == 'b':
        for _ in range(300):
            th = r.choice([37, 53, 60])
            m = r.randint(1, 10)
            s = r.randint(2, 10)
            F = r.choice([10, 15, 20, 25, 30, 40, 50, 60])
            f = r.choice([2, 3, 4, 5, 6, 8, 10])
            Fh = F * _COS[th]
            Fn = Fh - f
            if Fn <= 0: continue
            v2 = 2 * Fn * s / m
            v = _isq(v2)
            if v is None or v == 0: continue
            break
        else:
            return None
        # 검증: 운동학
        a = Fn / m
        assert Fr(v * v) == 2 * a * s
        Wn = Fn * s
        assert Wn == Fr(1, 2) * m * v * v
        ask = r.choice(['v', 'f'])
        fig = FIG(_pull_fig(th, F, s), '58%')
        base = '그림과 같이 질량 %d kg인 물체가 정지해 있는 거친 수평면 위에서 수평 방향과 %d°를 이루는 크기 %s N의 힘으로 %s m 이동하는 동안 일정한 크기의 마찰력을 받았다. ' % (m, th, _F(F), _F(s))
        if ask == 'v':
            body = P(base + '마찰력의 크기가 %s N일 때, %s m 이동한 순간 물체의 속력은?' % (_F(f), _F(s))) + fig
            ws = _ws(v, [math.isqrt(int(2 * Fh * s / m)) if _isq(2 * Fh * s / m) else v + 1, v * 2, v + 2, v - 1 if v > 1 else v + 3, _isq(2 * F * s / m) or v + 4], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v), ws, r=r, lv='상', fam='b', sort='num',
                      steps=['힘 F가 한 일 = %s × %s × cos%d° = %s J' % (_F(F), _F(s), th, _F(Fh * s)), '마찰력이 한 일 = -%s × %s = -%s J' % (_F(f), _F(s), _F(f * s)),
                             '알짜힘이 한 일 = %s J = ½ × %d × v² 이므로 v² = %d, v = %d m/s' % (_F(Wn), m, v * v, v)],
                      core='알짜힘이 한 일은 운동 에너지의 변화량과 같다(W = ΔE_k).', point='힘과 마찰력이 한 일의 합이 운동 에너지 변화이다.')
        body = P(base + '%s m 이동한 순간 물체의 속력이 %d m/s였다. 마찰력의 크기는?' % (_F(s), v)) + fig
        ws = _ws(f, [Fh, Fh + f, F - f if F > f else f + 3, Fh - 2 * f if Fh > 2 * f else f + 1, f * 2], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(f), ws, r=r, lv='상', fam='b', sort='num',
                  steps=['운동 에너지 증가량 = ½ × %d × %d² = %s J' % (m, v, _F(Wn)), 'F가 한 일 = %s × %s × cos%d° = %s J이므로 마찰력이 한 일 = %s - %s = %s J' % (_F(F), _F(s), th, _F(Fh * s), _F(Fh * s), _F(Wn), _F(f * s)),
                             '마찰력의 크기 = %s ÷ %s = %s N' % (_F(f * s), _F(s), _F(f))],
                  core='알짜힘이 한 일(힘이 한 일 + 마찰력이 한 일)은 운동 에너지의 변화량이다.', point='마찰력이 한 일은 음(-)이다.')
    if fam == 'c':
        for _ in range(200):
            m = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 20, 50, 1000])
            v1, v2 = r.randint(0, 20), r.randint(2, 30)
            if v1 == v2: continue
            if m >= 1000 and (v1 > 10 or v2 > 10): continue
            W = Fr(1, 2) * m * (v2 * v2 - v1 * v1)
            s = r.choice([2, 4, 5, 10, 20, 25, 50, 100])
            if W % s and (W / s).denominator not in (1, 2): continue
            break
        else:
            return None
        Fn = W / s
        mk = '%d kg' % m
        a = Fr(v2 * v2 - v1 * v1, 2 * s)
        assert m * a == Fn
        ask = r.choice(['W', 'F'])
        up = v2 > v1
        mv = '속력이 %d m/s에서 %d m/s로 %s' % (v1, v2, '증가하였다' if up else '감소하였다')
        if ask == 'W':
            body = P('직선 도로에서 질량 %s인 물체의 %s. 이 동안 물체에 작용한 알짜힘이 한 일은?' % (mk, mv))
            cands = [abs(W), Fr(1, 2) * m * (v2 - v1) ** 2, m * (v2 * v2 - v1 * v1), Fr(1, 2) * m * (v2 + v1) ** 2, Fr(1, 2) * m * v2 * v2]
            ws = _ws(W, cands, lambda c: _F(c) + ' J', pos=False)
            return mc(body, '%s J' % _F(W), ws, r=r, lv='하' if v1 == 0 else '중', fam='c', sort='num',
                      steps=['W = ΔE_k = ½mv₂² - ½mv₁²', 'W = ½ × %d × %d² - ½ × %d × %d² = %s J' % (m, v2, m, v1, _F(W))],
                      core='알짜힘이 한 일은 운동 에너지의 변화량과 같다.', point='속력의 제곱의 차를 이용한다(속력의 차가 아니다).')
        body = P('직선 도로에서 질량 %s인 물체가 일정한 알짜힘을 받으며 %d m 이동하는 동안 %s. 물체에 작용한 알짜힘의 크기는?' % (mk, s, mv))
        ws = _ws(abs(Fn), [abs(W), Fr(1, 2) * m * (v2 - v1) ** 2 / s, m * abs(v2 - v1), Fn * 2 if Fn else 3, abs(W) * s], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(abs(Fn)), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['알짜힘이 한 일 W = ½ × %d × (%d² - %d²) = %s J' % (m, v2, v1, _F(W)), 'W = F s 이므로 F = %s ÷ %d = %s N%s' % (_F(W), s, _F(Fn), '(운동 반대 방향)' if not up else '')],
                  core='W = Fs = ΔE_k 로 알짜힘의 크기를 구할 수 있다.', point='운동 에너지 변화량을 이동 거리로 나눈다.')
    if fam == 'd':
        shape = r.choice(['rect_tri', 'ramp_flat', 'trap', 'neg'])
        s1 = r.choice([2, 4]); s2 = s1 + r.choice([2, 4]); s3 = s2 + r.choice([2, 4])
        F1 = r.choice([10, 20, 30, 40])
        if shape == 'rect_tri':
            pts = [(0, F1), (s1, F1), (s2, 0)]
        elif shape == 'ramp_flat':
            pts = [(0, 0), (s1, F1), (s2, F1)]
        elif shape == 'trap':
            pts = [(0, 0), (s1, F1), (s2, F1), (s3, 0)]
        else:
            F2 = r.choice([10, 20])
            pts = [(0, 0), (s1, F1), (s2, F1), (s2, -F2), (s3, -F2)]
        if shape == 'neg':
            pass
        W = _area(pts)
        # 수치 적분으로 검증
        N = 4000; smax = pts[-1][0]; tot = 0.0
        def Fat(x, up=True):
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                if x2 == x1: continue
                if x1 <= x <= x2: return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
            return 0
        for i in range(N):
            tot += Fat((i + .5) * smax / N) * smax / N
        assert abs(tot - float(W)) < 0.2 + 1e-3 * abs(float(W)), (tot, W)
        if W <= 0: return None
        v0 = r.choice([0, 0, 2, 4])
        for m in r.sample([1, 2, 3, 4, 5, 8, 10, 20], 8):
            v = _isq(v0 * v0 + 2 * W / m)
            if v: break
        else:
            return None
        ask = r.choice(['W', 'v', 'v'])
        fig = FIG(_fs_fig(pts), '62%')
        start = '정지해 있던' if v0 == 0 else '%d m/s의 속력으로 운동하던' % v0
        if ask == 'W':
            body = P('그림은 직선 위에서 %s 물체에 작용하는 힘의 크기를 이동 거리 s에 따라 나타낸 것이다. 힘의 방향은 물체의 운동 방향(+)과 같거나 반대(-)이다. s = 0에서 s = %d m까지 이 힘이 한 일은?' % (start, pts[-1][0])) + fig
            ws = _ws(W, [F1 * pts[-1][0], F1 * s2, sum(abs(a) for a in [W]) + 10, W / 2, F1 * s1 + 5], lambda c: _F(c) + ' J')
            return mc(body, '%s J' % _F(W), ws, r=r, lv='중', fam='d', sort='num',
                      steps=['힘-이동 거리 그래프의 넓이가 한 일이다.', '구간별 넓이를 더하면 W = %s J' % _F(W)] + (['(s = %d m 이후 힘이 음(-)이므로 그 넓이는 빼 준다.)' % s2] if shape == 'neg' else []),
                      core='F-s 그래프 아래 넓이는 힘이 한 일과 같다(음의 힘은 음의 일).', point='그래프를 도형으로 나누어 넓이를 구한다.')
        body = P('그림은 마찰이 없는 수평면에서 %s 질량 %d kg인 물체에 작용하는 힘의 크기를 이동 거리 s에 따라 나타낸 것이다. 힘의 방향은 물체의 운동 방향(+)과 같거나 반대(-)이다. s = %d m인 지점에서 물체의 속력은?' % (start, m, pts[-1][0])) + fig
        ws = _ws(v, [_isq(2 * W / m) or v + 1, v * 2, int(W / m) if W % m == 0 else v + 3, v + 2, v - 1 if v > 1 else v + 4], lambda c: _F(c) + ' m/s')
        Wst = '½ × %d × %d² = %s J' % (m, v, _F(Fr(m * v * v, 2)))
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['그래프의 넓이로 힘이 한 일을 구한다 : W = %s J' % _F(W),
                         'W = ½mv² - ½mv₀² 이므로 %s = ½ × %d × v² - ½ × %d × %d²' % (_F(W), m, m, v0),
                         'v² = %d, v = %d m/s' % (v * v, v)],
                  core='F-s 그래프의 넓이 = 일 = 운동 에너지의 변화량.', point='넓이로 일을 구하고 운동 에너지 변화로 속력을 구한다.')
    # e: 같은 힘, 각도가 다른 두 경우의 일의 비
    t1, t2 = r.sample([0, 37, 53, 60], 2)
    F = r.choice([10, 20, 30, 40]); s = r.choice([2, 3, 4, 5])
    W1, W2 = F * s * _COS[t1], F * s * _COS[t2]
    ratio = '%d : %d' % ((W1 / math.gcd(int(W1), int(W2))), (W2 / math.gcd(int(W1), int(W2)))) if W1 == int(W1) and W2 == int(W2) else None
    if ratio is None: return None
    a_, b_ = ratio.split(' : ')
    cands = ['%s : %s' % (b_, a_), '1 : 1', '%d : %d' % (t1 or 1, t2 or 1), '%d : %d' % (int(_SIN.get(t1) or 1) if False else 3, 4)]
    wr = [c for c in dict.fromkeys(cands + ['2 : 3', '3 : 5', '4 : 5', '5 : 6']) if c != ratio]
    body = P('수평면 위의 같은 물체를 크기가 같은 힘 F로 수평 방향과 각각 %d°, %d°를 이루게 하여 같은 거리만큼 끌었다. 두 경우 힘 F가 한 일의 비 W%s : W%s는? (cos37° = 0.8, cos53° = 0.6, cos60° = 0.5)' % (t1, t2, sub(1), sub(2)))
    return mc(body, ratio, wr[:5], r=r, lv='중', fam='e', sort='shuf',
              steps=['W = Fs cosθ 이고 F, s가 같으므로 W%s : W%s = cos%d° : cos%d°' % (sub(1), sub(2), t1, t2), '= %s : %s = %s' % (_fx(_COS[t1]), _fx(_COS[t2]), ratio)],
              core='같은 힘·같은 거리에서 일은 cosθ에 비례한다.', point='각도에 따른 cosθ 값을 비교한다.')


# ================================================================== ph050 중력 위치 에너지와 운동 에너지
def _levels_fig(levels, ball=0, w=290, h=210, base_label=None):
    """levels: [(이름, 높이m)] (높이 큰 것부터). 가장 위 수준에 공."""
    f = Fig(w, h)
    y0 = h - 24
    hmax = max(l[1] for l in levels)
    sc = min(150.0 / hmax, 40)
    x0 = 110
    f.line(x0, y0, x0, y0 - hmax * sc - 12, GR, 1.2)
    _hatch(f, 60, y0, 140)
    for nm_, hh in levels:
        y = y0 - hh * sc
        f.line(60, y, 200, y, '#9fb0c6', 1.2, '4 3')
        f.text(206, y + 4, nm_, 13.5, 'start', True, INK, True)
        if hh:
            _dim_v(f, 232, y, y0, '%s m' % num(hh), RD, 'right') if False else f.text(54, y + 4, '%s m' % num(hh), 12, 'end', True, GR)
    ytop = y0 - levels[ball][1] * sc
    f.circ(x0, ytop - 8, 8, BL, INK, 1.4)
    f.text(54, y0 + 15, '0', 12, 'end', True, GR) if False else None
    return f.svg()


@T('ph050')
def potential_kinetic(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        m = r.choice([0.5, 1, 2, 3, 4, 5])
        hA = r.choice([8, 10, 12, 15, 20]); hB = r.choice([2, 3, 4, 5, 6]); 
        if hB >= hA: return None
        lev = [('A', hA), ('B', hB), ('C', 0)]
        refn, refh = r.choice([('B', hB), ('C', 0), ('A', hA)])
        tgt = r.choice([x for x in ('A', 'B', 'C') if x != refn] + [x for x in ('A', 'B', 'C') if x != refn])
        hh = dict(lev)[tgt] - refh
        Ep = m * G * hh
        fig = FIG(_levels_fig(lev), '56%')
        body = P('그림과 같이 질량 %s kg인 물체가 지면(C)으로부터 높이 %d m인 A점에 있다. 점 B는 지면으로부터 %d m 높이이다. 기준면을 %s점의 높이로 할 때, %s점에서 물체의 중력 위치 에너지는? (단, g = 10 m/s²이다.)' % (_F(m), hA, hB, refn, tgt)) + fig
        cands = [m * G * dict(lev)[tgt], m * G * abs(dict(lev)[tgt] - refh), -Ep, m * G * hA, m * G * (hA - hB), m * dict(lev)[tgt]]
        ws = _ws(Ep, cands, lambda c: _F(c) + ' J', pos=False)
        return mc(body, '%s J' % _F(Ep), ws, r=r, lv='중', fam='a', sort='num',
                  steps=['중력 위치 에너지 E_p = mgh 에서 h는 기준면으로부터의 높이이다.', '%s점은 기준면(%s점)보다 %s m %s에 있으므로 h = %s m' % (tgt, refn, _F(abs(hh)), '높은 곳' if hh >= 0 else '낮은 곳', _F(hh)),
                         'E_p = %s × 10 × (%s) = %s J' % (_F(m), _F(hh), _F(Ep))] ,
                  core='중력 위치 에너지 E_p = mgh 는 기준면에 따라 값이 달라지며, 기준면보다 낮으면 음수이다.', point='기준면으로부터의 높이를 부호까지 구한다.')
    if fam == 'b':
        for _ in range(100):
            H = r.choice([5, 10, 12, 15, 20, 25, 30, 40, 45])
            y = r.choice([0, 0, 2, 5, 8, 10, 15, 20, 25])
            if y >= H: continue
            d = H - y
            m = r.choice([0.5, 1, 2, 3, 4, 5])
            v2 = 2 * G * d
            Ek = m * G * d
            assert Fr(1, 2) * Fr(m).limit_denominator(10) * v2 == Ek
            break
        ask = r.choice(['Ek', 'v'])
        v = _isq(v2)
        if ask == 'v' and v is None: ask = 'Ek'
        lev = [('A', H)] + ([('B', y)] if y else []) + [('C', 0)] if y else [('A', H), ('C', 0)]
        tgt = 'B' if y else 'C'
        fig = FIG(_levels_fig(lev), '56%')
        if ask == 'Ek':
            body = P('그림과 같이 지면으로부터 높이 %d m인 A점에서 질량 %s kg인 물체를 가만히 놓았다. 물체가 %s점%s을 지날 때의 운동 에너지는? (단, g = 10 m/s²이며 공기 저항은 무시한다.)' % (H, _F(m), tgt, (' (높이 %d m)' % y) if y else '(지면)')) + fig
            ws = _ws(Ek, [m * G * H, m * G * y if y else m * G * H * 2, m * G * d / 2, m * d, m * G * (H + y)], lambda c: _F(c) + ' J')
            return mc(body, '%s J' % _F(Ek), ws, r=r, lv='중', fam='b', sort='num',
                      steps=['A → %s 로 내려오는 동안 중력이 한 일 = mg × (%d - %d) = %s × 10 × %d = %s J' % (tgt, H, y, _F(m), d, _F(Ek)), '이 일이 운동 에너지로 바뀌므로 E_k = %s J (처음에 정지)' % _F(Ek),
                             '(확인) v² = 2gd = %d, ½mv² = ½ × %s × %d = %s J' % (v2, _F(m), v2, _F(Ek))],
                      core='중력이 한 일 = 위치 에너지 감소량 = 운동 에너지 증가량.', point='높이 차이 H - y를 사용한다.')
        body = P('그림과 같이 지면으로부터 높이 %d m인 A점에서 질량 %s kg인 물체를 가만히 놓았다. 물체가 %s점%s을 지날 때의 속력은? (단, g = 10 m/s²이며 공기 저항은 무시한다.)' % (H, _F(m), tgt, (' (높이 %d m)' % y) if y else '(지면)')) + fig
        ws = _ws(v, [math.isqrt(int(G * d)) if _isq(G * d) else v + 1, v * 2, int(d), _isq(2 * G * H) or v + 2, v / 2 if v % 2 == 0 else v + 3], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='b', sort='num',
                  steps=['역학적 에너지 보존 : mg × %d = mg × %d + ½mv²' % (H, y), 'v² = 2g(%d - %d) = 2 × 10 × %d = %d' % (H, y, d, v2), 'v = %d m/s (질량과 무관하다.)' % v],
                  core='역학적 에너지 보존으로 mgΔh = ½mv² 이므로 v = √(2gΔh)이다.', point='질량은 약분되어 속력에 영향을 주지 않는다.')
    if fam == 'c':
        for _ in range(100):
            v0 = r.choice([4, 6, 8, 10, 12, 14, 16, 20])
            hmax = Fr(v0 * v0, 2 * G)
            if not _ok(hmax): continue
            m = r.choice([0.2, 0.5, 1, 2, 3, 4])
            y = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 12])
            if y >= hmax: continue
            Ek = Fr(1, 2) * Fr(m).limit_denominator(10) * v0 * v0 - Fr(m).limit_denominator(10) * G * y
            if not _ok(Ek): continue
            break
        else:
            return None
        ask = r.choice(['hmax', 'Ek', 'Ek'])
        mm = Fr(m).limit_denominator(10)
        # 운동학 검증: v_y^2 = v0^2 - 2 g y
        vy2 = v0 * v0 - 2 * G * y
        assert Fr(1, 2) * mm * vy2 == Ek
        if ask == 'hmax':
            body = P('지면에서 질량 %s kg인 물체를 연직 위로 %d m/s의 속력으로 던졌다. 물체가 올라갈 수 있는 최고 높이는? (단, g = 10 m/s²이며 공기 저항은 무시한다.)' % (_F(m), v0))
            ws = _ws(hmax, [Fr(v0 * v0, G), Fr(v0, G), Fr(v0, 2), Fr(v0 * v0, 4 * G), Fr(1, 2) * m * v0 * v0], lambda c: _F(c) + ' m')
            return mc(body, '%s m' % _F(hmax), ws, r=r, lv='하', fam='c', sort='num',
                      steps=['최고점에서 속력이 0이므로 ½mv₀² = mgh', 'h = v₀²/(2g) = %d² ÷ 20 = %s m' % (v0, _F(hmax))],
                      core='처음 운동 에너지가 모두 위치 에너지로 바뀐 곳이 최고점이다.', point='최고점에서는 운동 에너지가 0이다.')
        body = P('지면에서 질량 %s kg인 물체를 연직 위로 %d m/s의 속력으로 던졌다. 물체가 높이 %d m인 지점을 지날 때의 운동 에너지는? (단, g = 10 m/s²이며 공기 저항은 무시한다.)' % (_F(m), v0, y))
        ws = _ws(Ek, [Fr(1, 2) * mm * v0 * v0, mm * G * y, Fr(1, 2) * mm * v0 * v0 + mm * G * y, Ek / 2, Fr(1, 2) * mm * v0 * v0 - mm * y], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(Ek), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['처음 운동 에너지 = ½ × %s × %d² = %s J' % (_F(m), v0, _F(Fr(1, 2) * mm * v0 * v0)), '높이 %d m에서 위치 에너지 = %s × 10 × %d = %s J' % (y, _F(m), y, _F(mm * G * y)),
                         '역학적 에너지 보존 : E_k = %s - %s = %s J' % (_F(Fr(1, 2) * mm * v0 * v0), _F(mm * G * y), _F(Ek))],
                  core='역학적 에너지 E = E_k + E_p 가 일정하다.', point='처음 에너지에서 위치 에너지를 뺀다.')
    if fam == 'd':
        for _ in range(100):
            H = r.choice([6, 8, 10, 12, 15, 20, 24, 30])
            y = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15])
            if y >= H: continue
            break
        ratio = '%d : %d' % ((H - y) // math.gcd(H - y, y), y // math.gcd(H - y, y))
        lev = [('A', H), ('B', y), ('C', 0)]
        fig = FIG(_levels_fig(lev), '56%')
        body = P('그림과 같이 지면으로부터 높이 %d m인 A점에서 물체를 가만히 놓았다. 지면을 기준으로 높이 %d m인 B점을 지날 때 물체의 운동 에너지와 위치 에너지의 비 E_k : E_p는? (단, 공기 저항은 무시한다.)' % (H, y)) + fig
        a_, b_ = ratio.split(' : ')
        wr = [c for c in dict.fromkeys(['%s : %s' % (b_, a_), '1 : 1', '%d : %d' % (H, y), '%d : %d' % (y, H), '%d : %d' % (H - y, H), '%d : %d' % (y, H - y)]) if c != ratio]
        return mc(body, ratio, wr[:5], r=r, lv='중', fam='d', sort='shuf',
                  steps=['역학적 에너지는 mg × %d (A점에서 모두 위치 에너지)이다.' % H, 'B점에서 E_p = mg × %d, E_k = mg × (%d - %d) = mg × %d' % (y, H, y, H - y), 'E_k : E_p = %d : %d = %s' % (H - y, y, ratio)],
                  core='낙하 중 E_k = mg(H - h), E_p = mgh 이다.', point='감소한 높이가 운동 에너지, 남은 높이가 위치 에너지에 대응한다.')
    # e: 질량이 다른 두 물체
    m1, m2 = r.choice([(1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2), (1, 4), (4, 1)])
    H = r.choice([5, 10, 20])
    y = r.choice([0, H // 2])
    ask = r.choice(['Ek', 'v', 'Ep'])
    if ask == 'Ek':
        right = '%d : %d' % (m1, m2); q = '같은 높이(지면)에 도달하는 순간 두 물체의 운동 에너지의 비 E_k(A) : E_k(B)는?' if y == 0 else '높이 %d m를 지나는 순간 두 물체의 운동 에너지의 비 E_k(A) : E_k(B)는?' % y
        steps = ['낙하한 높이가 같으므로 E_k = mg(H - y)는 질량에 비례한다.', 'E_k(A) : E_k(B) = %d : %d' % (m1, m2)]
        wr = ['%d : %d' % (m2, m1), '1 : 1', '%d : %d' % (m1 * m1, m2 * m2), '%d : %d' % (m2 * m2, m1 * m1), '%d : %d' % (m1 + 1, m2 + 1)]
    elif ask == 'v':
        right = '1 : 1'; q = '낙하하여 높이 %d m를 지나는 순간 두 물체의 속력의 비 v(A) : v(B)는?' % y
        steps = ['v = √(2g(H - y)) 로 질량과 무관하다.', 'v(A) : v(B) = 1 : 1']
        wr = ['%d : %d' % (m1, m2), '%d : %d' % (m2, m1), '%d : %d' % (m1 * m1, m2 * m2), '%d : %d' % (m2 * m2, m1 * m1)]
    else:
        right = '%d : %d' % (m1, m2); q = '처음 위치(높이 %d m)에서 두 물체의 중력 위치 에너지의 비 E_p(A) : E_p(B)는? (지면 기준)' % H
        steps = ['E_p = mgh 에서 높이가 같으므로 질량에 비례한다.', 'E_p(A) : E_p(B) = %d : %d' % (m1, m2)]
        wr = ['%d : %d' % (m2, m1), '1 : 1', '%d : %d' % (m1 * m1, m2 * m2), '%d : %d' % (m2 * m2, m1 * m1), '%d : %d' % (m1 + 1, m2 + 1)]
    if right in wr: wr.remove(right)
    if m1 == m2: return None
    body = P('질량이 각각 %d kg, %d kg인 물체 A, B를 지면으로부터 같은 높이 %d m에서 가만히 놓았다. %s (단, 공기 저항은 무시한다.)' % (m1, m2, H, q))
    return mc(body, right, wr[:5], r=r, lv='하', fam='e', sort='shuf', steps=steps,
              core='E_p = mgh, E_k = mg(낙하 높이)는 질량에 비례하고, 낙하 속력은 질량과 무관하다.', point='질량과 속력의 관계를 구분한다.')


# ================================================================== ph051 역학적 에너지 보존(낙하·빗면)
_SINV = {30: Fr(1, 2), 37: Fr(3, 5), 53: Fr(4, 5), 45: None}


@T('ph051')
def conserve_slide(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'd', 'd', 'e'])
    if fam == 'a':
        th = r.choice([30, 37, 53])
        v = r.randint(2, 15)
        h = Fr(v * v, 20)
        L = h / _SINV[th]
        if not _ok(h) or not _ok(L): return None
        # 운동학 검증
        a = G * _SINV[th]
        assert 2 * a * L == v * v
        ask = r.choice(['v_h', 'v_L', 'h'])
        if ask == 'v_h':
            svg, _ = _incline_fig(th, '%s m' % _F(h))
            body = P('그림과 같이 경사각 %d°인 마찰이 없는 빗면의 높이 %s m인 지점에서 물체를 가만히 놓았다. 물체가 빗면 아래 끝에 도달했을 때의 속력은? (단, g = 10 m/s²이다.)' % (th, _F(h))) + FIG(svg, '60%')
            ws = _ws(v, [math.isqrt(int(10 * h)) if _isq(10 * h) else v + 1, v * 2, v + 2, v - 1 if v > 1 else v + 3, int(h * 10)], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v), ws, r=r, lv='하', fam='a', sort='num',
                      steps=['역학적 에너지 보존 : mgh = ½mv²', 'v = √(2gh) = √(2 × 10 × %s) = √%d = %d m/s' % (_F(h), v * v, v), '(빗면의 경사각과 무관하다.)'],
                      core='마찰이 없으면 역학적 에너지가 보존되어 바닥 속력은 높이만으로 결정된다(v = √2gh).', point='경사각은 속력에 영향을 주지 않는다.')
        if ask == 'v_L':
            svg, _ = _incline_fig(th, None, '%s m' % _F(L))
            body = P('그림과 같이 경사각 %d°인 마찰이 없는 빗면에서 빗면을 따라 %s m 떨어진 위쪽 지점에서 물체를 가만히 놓았다. 물체가 빗면 아래 끝에 도달했을 때의 속력은? (단, sin%d° = %s, g = 10 m/s²이다.)' % (th, _F(L), th, _F(_SINV[th]))) + FIG(svg, '60%')
            ws = _ws(v, [_isq(20 * L) or v + 1, int(math.sqrt(float(2 * G * L * (1 - _SINV[th]))) // 1) or v + 2, v * 2, v + 2, v - 1 if v > 1 else v + 3], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='a', sort='num',
                      steps=['처음 높이 h = L sin%d° = %s × %s = %s m' % (th, _F(L), _F(_SINV[th]), _F(h)), '역학적 에너지 보존 : v = √(2gh) = √(2 × 10 × %s) = %d m/s' % (_F(h), v),
                             '(확인) a = g sin%d° = %s m/s², v² = 2aL = 2 × %s × %s = %d' % (th, _F(a), _F(a), _F(L), v * v)],
                      core='높이는 h = L sinθ 이며 v = √(2gh)이다.', point='빗면 길이를 높이로 바꾼 뒤 에너지 보존을 쓴다.')
        svg, _ = _incline_fig(th, None, None)
        body = P('그림과 같이 경사각 %d°인 마찰이 없는 빗면의 위쪽에서 물체를 가만히 놓았더니 빗면 아래 끝에서의 속력이 %d m/s였다. 물체를 놓은 지점의 바닥으로부터의 높이는? (단, g = 10 m/s²이다.)' % (th, v)) + FIG(svg, '60%')
        ws = _ws(h, [Fr(v * v, 10), Fr(v, 10), Fr(v * v, 20) / _SINV[th], Fr(v * v, 40), Fr(v, 2)], lambda c: _F(c) + ' m')
        return mc(body, '%s m' % _F(h), ws, r=r, lv='하', fam='a', sort='num',
                  steps=['mgh = ½mv² 이므로 h = v²/(2g)', 'h = %d² ÷ 20 = %s m' % (v, _F(h))],
                  core='mgh = ½mv² (마찰 없음).', point='빗면의 각도에 관계없이 높이만 구한다.')
    if fam == 'b':
        for _ in range(300):
            hA = r.randint(6, 20)
            others = r.sample(range(0, hA + 4), 3)
            names = ['B', 'C', 'D']
            hs = dict(zip(names, others))
            if len({hA, *others}) < 4: continue
            if any(abs(a - b) < 2 for a in [hA] + others for b in [hA] + others if a != b): continue
            tgt = r.choice([n for n in names if hs[n] < hA])
            v0 = r.choice([0, 0, 2, 4, 6, 8])
            v2 = v0 * v0 + 2 * G * (hA - hs[tgt])
            v = _isq(v2)
            if v: break
        else:
            return None
        pts = [('A', hA)] + [(n, hs[n]) for n in names]
        # 검증
        assert Fr(1, 2) * v0 * v0 + G * hA == Fr(1, 2) * v * v + G * hs[tgt]
        fig = FIG(_track_fig(pts), '70%')
        start = '가만히 놓았다' if v0 == 0 else '%d m/s의 속력으로 출발시켰다' % v0
        body = P('그림은 마찰이 없는 트랙의 점 A, B, C, D의 높이를 나타낸 것이다. 질량 m인 물체를 점 A에서 %s. 물체가 점 %s을 지날 때의 속력은? (단, g = 10 m/s²이며 물체는 트랙을 따라 운동한다.)' % (start, tgt)) + fig
        d = hA - hs[tgt]
        ws = _ws(v, [_isq(2 * G * d) or v + 1, int(d), v + 2, v * 2, _isq(v0 * v0 + G * d) or v - 1 if v > 1 else v + 4], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중' if v0 == 0 else '상', fam='b', sort='num',
                  steps=['역학적 에너지 보존 : ½mv₀² + mg × %d = ½mv² + mg × %d' % (hA, hs[tgt]), 'v² = %d² + 2 × 10 × (%d - %d) = %d' % (v0, hA, hs[tgt], v * v), 'v = %d m/s' % v],
                  core='마찰이 없는 트랙에서는 높이 차이에 의한 위치 에너지 변화가 운동 에너지 변화가 된다.', point='트랙 모양이 아니라 높이만 본다.')
    if fam == 'c':
        for _ in range(100):
            v0 = r.choice([4, 6, 8, 10, 12, 14, 16, 20])
            hm = Fr(v0 * v0, 20)
            y = hm * r.choice([Fr(1, 4), Fr(1, 2), Fr(3, 4)])
            if not (_ok(hm) and _ok(y)): continue
            break
        else:
            return None
        kk = (hm - y) / hm
        v = _isq(v0 * v0 - 20 * y)
        if v is None: return None
        assert Fr(v * v) == v0 * v0 - 2 * G * y
        body = P('지면에서 연직 위로 %d m/s의 속력으로 던진 공이 최고점에 도달하기 전 높이 %s m인 지점을 지날 때의 속력은? (단, g = 10 m/s²이며 공기 저항은 무시한다.)' % (v0, _F(y)))
        ws = _ws(v, [v0 - int(y), v0 / 2, _isq(v0 * v0 - 10 * y) or v + 1, v + 2, v0 - 2 * y if v0 > 2 * y else v + 3], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['역학적 에너지 보존 : ½mv₀² = ½mv² + mgy', 'v² = %d² - 2 × 10 × %s = %d' % (v0, _F(y), v * v), 'v = %d m/s' % v,
                         '(확인) 운동학 v² = v₀² - 2gy = %d' % (v0 * v0 - 20 * y)],
                  core='연직 운동에서도 역학적 에너지가 보존된다.', point='v² = v₀² - 2gy 와 같은 결과이다.')
    if fam == 'd':
        # 높이가 같은 두 빗면 : 속력 비 / 시간 비 / 가속도 비
        t1, t2 = r.sample([30, 37, 53], 2)
        h = r.choice([0.8, 1.25, 1.8, 3.2, 5])
        ask = r.choice(['v', 't', 'a'])
        s1, s2 = _SINV[t1], _SINV[t2]
        f = Fig(320, 170)
        x0, y0 = 20, 150
        H = 100
        for (th, nm_, xo, col) in ((t1, 'A', 20, RD), (t2, 'B', 170, BL)):
            ln = H / math.sin(math.radians(th))
            xr = xo + ln * math.cos(math.radians(th))
            f.poly([(xo, y0), (xr, y0), (xr, y0 - H)], '#f1f4f8', INK, 1.6)
            f.circ(xr - 8, y0 - H + 8 * math.tan(math.radians(th)) + 2, 5, col, INK, 1)
            f.text(xr - 8, y0 - H - 6 + 0, nm_, 13, 'middle', True, col, True)
            f.text(xo + 38, y0 - 4, '%d°' % th, 12, 'start', True, GR)
            _dim_v(f, xr + 8, y0 - H, y0, '%s m' % _F(h), GR, 'right') if xr < 300 else None
        fig = FIG(f.svg(), '62%')
        base = '그림은 높이가 %s m로 같고 경사각이 각각 %d°, %d°인 마찰이 없는 두 빗면 A, B의 꼭대기에서 물체를 동시에 가만히 놓는 것을 나타낸 것이다. ' % (_F(h), t1, t2)
        if ask == 'v':
            q = '두 물체가 빗면 아래 끝에 도달하는 순간의 속력의 비 v%s : v%s는?' % (sub('A'), sub('B'))
            right = '1 : 1'
            wr = ['%s : %s' % (_fx(s1 / s2).split('/')[0] if False else (s1 / s2).numerator, (s1 / s2).denominator), '%s : %s' % ((s2 / s1).numerator, (s2 / s1).denominator), '%d : %d' % (t1, t2), '%d : %d' % (t2, t1), '1 : 2']
            steps = ['높이가 같으므로 mgh = ½mv²에서 v = √(2gh)로 같다.', 'v%s : v%s = 1 : 1' % (sub('A'), sub('B'))]
            lv = '중'
        elif ask == 'a':
            q = '두 물체의 가속도의 크기의 비 a%s : a%s는? (단, sin%d° = %s, sin%d° = %s)' % (sub('A'), sub('B'), t1, _fx(s1), t2, _fx(s2))
            rr = s1 / s2
            right = '%d : %d' % (rr.numerator, rr.denominator)
            rv = s2 / s1
            wr = ['%d : %d' % (rv.numerator, rv.denominator), '1 : 1', '%d : %d' % (t1, t2), '%d : %d' % (rr.numerator ** 2, rr.denominator ** 2), '%d : %d' % (rv.numerator ** 2, rv.denominator ** 2)]
            steps = ['a = g sinθ 이므로 a%s : a%s = sin%d° : sin%d° = %s : %s' % (sub('A'), sub('B'), t1, t2, _fx(s1), _fx(s2)), '= %s' % right]
            lv = '중'
        else:
            q = '두 물체가 빗면 아래 끝에 도달하는 데 걸리는 시간의 비 t%s : t%s는? (단, sin%d° = %s, sin%d° = %s)' % (sub('A'), sub('B'), t1, _fx(s1), t2, _fx(s2))
            rr = s2 / s1
            right = '%d : %d' % (rr.numerator, rr.denominator)
            rv = s1 / s2
            wr = ['%d : %d' % (rv.numerator, rv.denominator), '1 : 1', '%d : %d' % (t2, t1), '%d : %d' % (rr.numerator ** 2, rr.denominator ** 2), '%d : %d' % (rv.numerator ** 2, rv.denominator ** 2)]
            # 검증 : L = h / sin, a = g sin, t = sqrt(2L/a)
            tA = math.sqrt(2 * (h / float(s1)) / (G * float(s1)))
            tB = math.sqrt(2 * (h / float(s2)) / (G * float(s2)))
            assert abs(tA / tB - float(rr)) < 1e-9
            steps = ['빗면 길이 L = h/sinθ, 가속도 a = g sinθ 이고 L = ½at² 이므로 t = (1/sinθ)√(2h/g) 이다.', 't%s : t%s = 1/sin%d° : 1/sin%d° = sin%d° : sin%d° = %s : %s' % (sub('A'), sub('B'), t1, t2, t2, t1, _fx(s2), _fx(s1)), '= %s' % right]
            lv = '상'
        wr = [c for c in dict.fromkeys(wr) if c != right]
        body = P(base + q) + fig
        return mc(body, right, wr[:5], r=r, lv=lv, fam='d', sort='shuf', steps=steps,
                  core='같은 높이의 마찰 없는 빗면에서 바닥 속력은 같고, 가속도는 sinθ에 비례하며 걸리는 시간은 sinθ에 반비례한다.', point='속력은 에너지 보존, 시간은 운동학으로 구한다.')
    # e: 빗면 중간 지점의 속력 / 높이
    for _ in range(100):
        v = r.choice([4, 6, 8, 10, 12, 16, 20])
        h = Fr(v * v, 20)
        q_ = r.choice([Fr(1, 2), Fr(3, 4), Fr(1, 4), Fr(3, 5), Fr(1, 5)])
        vq = v * q_      # 속력 = 바닥 속력의 q_ 배
        if not _ok(h) or not _ok(vq): continue
        drop = Fr(vq * vq, 20)   # 처음 위치에서 내려온 높이
        if not _ok(drop) or drop >= h: continue
        y = h - drop
        break
    else:
        return None
    assert Fr(vq * vq) == 2 * G * drop
    svg, _ = _incline_fig(r.choice([30, 37, 53]), '%s m' % _F(h))
    body = P('그림과 같이 마찰이 없는 빗면의 높이 %s m인 지점에서 물체를 가만히 놓았다. 물체의 속력이 %s m/s가 되는 지점의 바닥으로부터의 높이는? (단, g = 10 m/s²이다.)' % (_F(h), _F(vq))) + FIG(svg, '60%')
    ws = _ws(y, [drop, h - vq / 10, Fr(vq, 10), h / 2, h + drop], lambda c: _F(c) + ' m')
    return mc(body, '%s m' % _F(y), ws, r=r, lv='상', fam='e', sort='num',
              steps=['내려온 높이 d : mgd = ½mv² 이므로 d = %s² ÷ 20 = %s m' % (_F(vq), _F(drop)), '바닥으로부터의 높이 = %s - %s = %s m' % (_F(h), _F(drop), _F(y))],
              core='속력이 v인 지점까지 내려온 높이는 d = v²/(2g)이다.', point='처음 높이에서 내려온 높이를 빼서 현재 높이를 구한다.')


# ================================================================== ph052 용수철의 탄성 위치 에너지
def _spring_fig(x, k, m, w=300, h=150, label_x=True, compressed=True):
    f = Fig(w, h)
    y0 = 108
    f.line(24, y0, w - 16, y0, GR, 1.8)
    f.line(40, y0 - 56, 40, y0, GR, 2.4)
    for i in range(0, 56, 8): f.line(40, y0 - 56 + i + 8, 33, y0 - 56 + i + 15, GR, 1)
    L0 = 120; xx = 34 if False else 0
    xl = 150.0
    px = 40 + 66   # 압축된 상태 용수철 끝
    f.spring(40, y0 - 14, px, coils=6, amp=8)
    _block(f, px + 22, y0, 44, 28, label='m')
    f.line(40 + L0, y0 - 40, 40 + L0, y0, GR, 1, '4 3')
    f.text(40 + L0, y0 - 44, '자연 길이', 11.5, 'middle', c=GR)
    _dim_h(f, px, 40 + L0, y0 + 14, 'x = %s m' % _F(x), RD)
    f.text(150, 22, 'k = %s N/m,  m = %s kg' % (_F(k), _F(m)), 13, 'middle', True, INK)
    return f.svg()


def _vspring_fig(h, w=240, h_=210):
    f = Fig(w, h_)
    y0 = h_ - 20
    _hatch(f, 60, y0, 120)
    f.spring(120, y0, 120, 0) if False else None
    # 연직 용수철
    pts = [(120, y0), (120, y0 - 18)]
    nn = 14
    for i in range(1, nn + 1):
        pts.append((120 + (9 if i % 2 else -9), y0 - 18 - 62 * i / nn))
    pts.append((120, y0 - 84)); pts.append((120, y0 - 96))
    f.poly(pts, 'none', INK, 1.8, close=False)
    f.circ(120, 44, 11, BL, INK, 1.5)
    f.text(148, 48, 'm', 13, 'start', True, INK, True)
    _dim_v(f, 70, 56, y0 - 96, 'h', RD, 'left')
    f.text(120, y0 - 100 + 0, '', 10)
    return f.svg()


@T('ph052')
def spring_energy(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        for _ in range(100):
            m = r.choice([0.5, 1, 2, 4, 5, 8])
            s_ = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 20])
            kk = Fr(m).limit_denominator(10) * s_ * s_
            x = r.choice([Fr(1, 10), Fr(1, 5), Fr(3, 10), Fr(2, 5), Fr(1, 2), Fr(1, 20)])
            if kk.denominator != 1 or kk > 2000: continue
            v = x * s_
            if not _ok(v): continue
            break
        else:
            return None
        Ep = Fr(1, 2) * kk * x * x
        assert Ep == Fr(1, 2) * Fr(m).limit_denominator(10) * v * v
        ask = r.choice(['Ep', 'v', 'v'])
        fig = FIG(_spring_fig(x, kk, m), '62%')
        base = '그림과 같이 마찰이 없는 수평면에서 용수철 상수가 %s N/m인 용수철을 %s m 압축하여 질량 %s kg인 물체를 놓았다. ' % (_F(kk), _F(x), _F(m))
        if ask == 'Ep':
            body = P(base + '용수철에 저장된 탄성 위치 에너지는?') + fig
            ws = _ws(Ep, [kk * x * x, kk * x, Fr(1, 2) * kk * x, Fr(1, 2) * kk * x * x * 2, kk * x / 4], lambda c: _F(c) + ' J')
            return mc(body, '%s J' % _F(Ep), ws, r=r, lv='하', fam='a', sort='num',
                      steps=['탄성 위치 에너지 E = ½kx²', 'E = ½ × %s × %s² = %s J' % (_F(kk), _F(x), _F(Ep))],
                      core='탄성 위치 에너지 E = ½kx² (x : 변형된 길이).', point='변형 길이는 제곱한다.')
        body = P(base + '물체가 용수철에서 분리되는 순간(자연 길이)의 속력은?') + fig
        ws = _ws(v, [x * math.sqrt(float(kk)) if False else x * kk / Fr(m).limit_denominator(10), x * s_ * 2, x * s_ / 2, x * s_ * s_, math.sqrt(float(Ep)) if _isq(Ep) else v + 1], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='a', sort='num',
                  steps=['역학적 에너지 보존 : ½kx² = ½mv²', '½ × %s × %s² = ½ × %s × v² 이므로 v² = %s' % (_F(kk), _F(x), _F(m), _F(v * v)), 'v = %s m/s' % _F(v)],
                  core='탄성 위치 에너지가 모두 운동 에너지로 바뀐다 : ½kx² = ½mv².', point='v = x√(k/m)')
    if fam == 'b':
        for _ in range(100):
            x1 = r.choice([Fr(1, 10), Fr(1, 5), Fr(3, 10), Fr(2, 5), Fr(1, 2)])
            kk = r.choice([20, 40, 50, 60, 80, 100, 120, 200, 250, 400])
            F1 = kk * x1
            x2 = x1 * r.choice([2, 3, Fr(1, 2)])
            if not (_ok(F1) and _ok(x2)): continue
            break
        ask = r.choice(['Ep', 'k', 'Ep2'])
        xmax = x1 * 1.0
        pl = Plot(300, 190, float(x1) * 1.5, float(F1) * 1.35, ml=50, mb=32)
        pl.axes('x (m)', 'F (N)', xticks=[0, float(x1)], yticks=[0, float(F1)], grid=False)
        pl.pl([(0, 0), (float(x1) * 1.4, float(F1) * 1.4)], BL, 2.6)
        pl.dash_to_axes(float(x1), float(F1), RD)
        pl.circ(pl.px(float(x1)), pl.py(float(F1)), 4, RD, INK, 1)
        fig = FIG(pl.svg(), '60%')
        head = '그림은 어떤 용수철을 늘이거나 압축할 때 용수철에 가해 준 힘의 크기 F를 변형된 길이 x에 따라 나타낸 것이다. '
        if ask == 'k':
            body = P(head + '이 용수철의 용수철 상수는?') + fig
            ws = _ws(kk, [F1 * x1, F1 / 2, kk * 2, kk / 2, F1], lambda c: _F(c) + ' N/m')
            return mc(body, '%s N/m' % _F(kk), ws, r=r, lv='하', fam='b', sort='num',
                      steps=['F = kx 이므로 그래프의 기울기가 용수철 상수이다.', 'k = %s N ÷ %s m = %s N/m' % (_F(F1), _F(x1), _F(kk))],
                      core='훅의 법칙 F = kx 에서 F-x 그래프의 기울기는 용수철 상수 k이다.', point='그래프의 기울기를 읽는다.')
        if ask == 'Ep':
            body = P(head + '용수철을 %s m만큼 변형시켰을 때 용수철에 저장된 탄성 위치 에너지는?' % _F(x1)) + fig
            Ep = Fr(1, 2) * F1 * x1
            assert Ep == Fr(1, 2) * kk * x1 * x1
            ws = _ws(Ep, [F1 * x1, F1, Fr(1, 2) * F1, kk * x1, Ep * 2], lambda c: _F(c) + ' J')
            return mc(body, '%s J' % _F(Ep), ws, r=r, lv='중', fam='b', sort='num',
                      steps=['그래프 아래 넓이가 용수철에 한 일 = 탄성 위치 에너지이다.', 'E = ½ × %s N × %s m = %s J' % (_F(F1), _F(x1), _F(Ep))],
                      core='F-x 그래프 아래 넓이 = 탄성 위치 에너지 = ½kx².', point='삼각형의 넓이로 에너지를 구한다.')
        Ep2 = Fr(1, 2) * kk * x2 * x2
        body = P(head + '이 용수철을 %s m만큼 변형시켰을 때 용수철에 저장된 탄성 위치 에너지는?' % _F(x2)) + fig
        ws = _ws(Ep2, [kk * x2 * x2, Fr(1, 2) * kk * x2, Fr(1, 2) * F1 * x1 * (x2 / x1), Fr(1, 2) * kk * x1 * x1, kk * x2], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(Ep2), ws, r=r, lv='상', fam='b', sort='num',
                  steps=['그래프의 기울기 k = %s ÷ %s = %s N/m' % (_F(F1), _F(x1), _F(kk)), 'E = ½kx² = ½ × %s × %s² = %s J' % (_F(kk), _F(x2), _F(Ep2))],
                  core='k는 F-x 그래프의 기울기이고 E = ½kx²이다.', point='그래프에 없는 변형 길이에서는 k를 먼저 구한다.')
    if fam == 'c':
        for _ in range(300):
            m = r.choice([0.5, 1, 2, 4])
            mm = Fr(m).limit_denominator(10)
            x = r.choice([Fr(1, 10), Fr(1, 5), Fr(2, 5), Fr(1, 2), Fr(3, 10)])
            hh = r.choice([Fr(1, 5), Fr(2, 5), Fr(3, 5), Fr(4, 5), 1, Fr(3, 2), 2, Fr(1, 2)])
            kk = 2 * mm * G * (hh + x) / (x * x)
            if kk.denominator == 1 and kk <= 3000 and kk % 5 == 0: break
        else:
            return None
        ask = r.choice(['k', 'v'])
        fig = FIG(_vspring_fig(hh), '44%')
        if ask == 'k':
            body = P('그림과 같이 질량 %s kg인 물체를 연직으로 세워 놓은 용수철의 윗끝으로부터 높이 h = %s m에서 가만히 놓았더니, 용수철이 최대 %s m 압축되었다. 용수철 상수는? (단, g = 10 m/s²이고 용수철의 질량과 공기 저항은 무시한다.)' % (_F(m), _F(hh), _F(x))) + fig
            ws = _ws(kk, [2 * mm * G * hh / (x * x), 2 * mm * G * (hh + x) / x, mm * G * (hh + x) / (x * x), 2 * mm * G * x / (x * x) if False else mm * G / x, kk * 2], lambda c: _F(c) + ' N/m')
            assert Fr(1, 2) * kk * x * x == mm * G * (hh + x)
            return mc(body, '%s N/m' % _F(kk), ws, r=r, lv='상', fam='c', sort='num',
                      steps=['처음(정지)과 최대 압축 순간(정지)의 운동 에너지가 모두 0이므로 중력 위치 에너지 감소 = 탄성 위치 에너지 증가', 'mg(h + x) = ½kx² : %s × 10 × (%s + %s) = ½ × k × %s²' % (_F(m), _F(hh), _F(x), _F(x)),
                             'k = %s N/m' % _F(kk)],
                      core='용수철이 최대 압축된 순간 물체는 정지하며, 물체가 내려간 전체 높이(h + x)만큼의 위치 에너지가 탄성 에너지가 된다.', point='압축된 길이 x도 물체가 내려간 높이에 포함시킨다.')
        v = _isq(2 * G * hh)
        if v is None: return None
        body = P('그림과 같이 질량 %s kg인 물체를 연직으로 세워 놓은 용수철의 윗끝으로부터 높이 h = %s m에서 가만히 놓았다. 물체가 용수철의 윗끝에 닿는 순간의 속력은? (단, g = 10 m/s²이고 용수철의 질량과 공기 저항은 무시한다.)' % (_F(m), _F(hh))) + fig
        ws = _ws(v, [v * 2, v / 2 if v % 2 == 0 else v + 2, int(hh * 10), v + 1, v - 1 if v > 1 else v + 3], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='하', fam='c', sort='num',
                  steps=['용수철에 닿기 전까지는 자유 낙하이다 : mgh = ½mv²', 'v = √(2gh) = √(2 × 10 × %s) = %s m/s' % (_F(hh), _F(v))],
                  core='용수철에 닿기 전까지는 중력만 작용하는 자유 낙하이다.', point='닿는 순간의 속력은 높이 h만으로 결정된다.')
    if fam == 'd':
        th = r.choice([30, 37, 53])
        for _ in range(300):
            m = r.choice([0.5, 1, 2, 4])
            mm = Fr(m).limit_denominator(10)
            kk = r.choice([100, 200, 300, 400, 500, 800, 1000, 1500])
            x = r.choice([Fr(1, 10), Fr(1, 5), Fr(2, 5), Fr(1, 2), Fr(3, 10)])
            Ep = Fr(1, 2) * kk * x * x
            hh = Ep / (mm * G)
            d = hh / _SINV[th]
            if _ok(hh) and _ok(d) and hh >= Fr(1, 5): break
        else:
            return None
        f = Fig(300, 170)
        svg, (x0, y0, x1, y1) = _incline_fig(th, None, None, w=300, h=170, block=False)
        body = P('그림과 같이 경사각 %d°인 마찰이 없는 빗면의 아래 끝에 용수철 상수 %d N/m인 용수철이 고정되어 있다. 용수철을 %s m 압축시키고 질량 %s kg인 물체를 용수철에 붙이지 않고 놓았더니 물체가 빗면을 따라 올라갔다. 물체가 올라간 최고 높이는? (단, g = 10 m/s²이며, 용수철이 압축되기 전의 위치를 기준으로 한다.)' % (th, kk, _F(x), _F(m))) + FIG(svg, '56%')
        ask_h = True
        ws = _ws(hh, [Ep, Ep / m if False else Ep / (mm * 5), hh * 2, d, hh / 2], lambda c: _F(c) + ' m')
        return mc(body, '%s m' % _F(hh), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['탄성 위치 에너지 ½kx² = ½ × %d × %s² = %s J' % (kk, _F(x), _F(Ep)), '최고점에서 속력이 0이므로 ½kx² = mgh', 'h = %s ÷ (%s × 10) = %s m (빗면 길이 %s m, 각도는 높이에 영향이 없다.)' % (_F(Ep), _F(m), _F(hh), _F(d))],
                  core='탄성 위치 에너지 → 중력 위치 에너지로 전환 : ½kx² = mgh.', point='빗면의 각도와 관계없이 높이는 에너지 보존으로 결정된다.')
    # e: 같은 용수철, 다른 압축 길이 / 질량
    x1, x2 = r.choice([(1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2), (1, 4), (4, 1)])
    m1, m2 = r.choice([(1, 1), (1, 4), (4, 1), (1, 9), (9, 1), (4, 9), (9, 4), (1, 1)])
    ask = r.choice(['E', 'v'])
    if ask == 'E':
        right = '%d : %d' % (x1 * x1 // math.gcd(x1 * x1, x2 * x2), x2 * x2 // math.gcd(x1 * x1, x2 * x2))
        body = P('용수철 상수가 같은 두 용수철을 각각 %d cm, %d cm 압축시켰다. 두 용수철에 저장된 탄성 위치 에너지의 비는? (단, 처음 압축한 용수철의 에너지를 앞에 쓴다.)' % (x1 * 5, x2 * 5))
        wr = ['%d : %d' % (x2 * x2 // math.gcd(x1 * x1, x2 * x2), x1 * x1 // math.gcd(x1 * x1, x2 * x2)), '%d : %d' % (x1, x2), '%d : %d' % (x2, x1), '%d : %d' % (x1 ** 3, x2 ** 3), '1 : 1']
        wr = [c for c in dict.fromkeys(wr) if c != right]
        if x1 == x2: return None
        return mc(body, right, wr[:5], r=r, lv='하', fam='e', sort='shuf',
                  steps=['E = ½kx² 이므로 k가 같으면 E ∝ x²이다.', 'E%s : E%s = %d² : %d² = %s' % (sub(1), sub(2), x1, x2, right)],
                  core='탄성 위치 에너지는 변형된 길이의 제곱에 비례한다.', point='길이 비를 제곱한다.')
    # v 비 : v = x sqrt(k/m)
    a, b = x1, x2
    # v1 : v2 = x1/sqrt(m1) : x2/sqrt(m2)
    sm1, sm2 = math.isqrt(m1), math.isqrt(m2)
    vr = Fr(a * sm2, sm1) / Fr(b * sm1 * 0 + b * sm1 / sm1 if False else 1)
    r1, r2 = Fr(a, sm1), Fr(b, sm2)
    g_ = Fr(r1 / r2)
    right = '%d : %d' % (g_.numerator, g_.denominator)
    # 검증 에너지
    v1s = Fr(a * a, m1); v2s = Fr(b * b, m2)
    assert v1s / v2s == g_ * g_
    if g_ == 1: return None
    body = P('마찰이 없는 수평면에서 용수철 상수가 같은 두 용수철을 각각 %d cm, %d cm 압축시킨 뒤 질량이 각각 %d kg, %d kg인 물체 A, B를 놓았다. 용수철이 원래 길이가 되는 순간 A, B의 속력의 비 v%s : v%s는?' % (a * 5, b * 5, m1, m2, sub('A'), sub('B')))
    wr = []
    for c in (Fr(g_.denominator, g_.numerator), g_ * g_, Fr(a, b), Fr(b, a), Fr(a * sm1, b * sm2), g_ * 2):
        s_ = '%d : %d' % (Fr(c).numerator, Fr(c).denominator)
        if s_ != right and s_ not in wr: wr.append(s_)
    return mc(body, right, wr[:5], r=r, lv='상', fam='e', sort='shuf',
              steps=['½kx² = ½mv² 이므로 v = x√(k/m) → v ∝ x/√m', 'v%s : v%s = %d/√%d : %d/√%d = %d/%d : %d/%d = %s' % (sub('A'), sub('B'), a, m1, b, m2, a, sm1, b, sm2, right)],
              core='용수철이 한 일 ½kx² = ½mv² 이므로 v는 x에 비례하고 √m에 반비례한다.', point='질량 비는 제곱근으로 반영한다.')


# ================================================================== ph053 진자 운동과 에너지 전환
def _pendulum_fig(L, th0, mid=None, w=300, h=200):
    f = Fig(w, h)
    px, py = w / 2, 24
    Lp = 135
    f.line(px - 60, py, px + 60, py, GR, 3)
    for i in range(-60, 60, 10): f.line(px + i, py, px + i + 6, py - 7, GR, 1)
    f.line(px, py, px, py + Lp, GR, 1, '4 3')
    t = math.radians(th0)
    bx, by = px - Lp * math.sin(t), py + Lp * math.cos(t)
    f.line(px, py, bx, by, INK, 1.8)
    f.circ(bx, by, 9, BL, INK, 1.4); f.text(bx - 14, by + 4, 'A', 13, 'end', True, INK, True)
    f.circ(px, py + Lp, 9, '#cfe2f7', INK, 1.2, '3 2'); f.text(px, py + Lp + 24, 'B', 13, 'middle', True, INK, True)
    f.o.append('<path d="M %s %s A 44 44 0 0 1 %s %s" fill="none" stroke="%s" stroke-width="1.2"/>' % (Fig._n(px), Fig._n(py + 44), Fig._n(px - 44 * math.sin(t)), Fig._n(py + 44 * math.cos(t)), GR))
    f.text(px - 26 * math.sin(t / 2) * 2 - 6, py + 62, '%d°' % th0, 12.5, 'end', True, GR)
    f.text(px + 8, py + Lp / 2, 'L = %s m' % _F(L), 12.5, 'start', True, RD)
    f.line(px + 40, by, px + 40, py + Lp, GR, 1, '3 3') if False else None
    return f.svg()


def _loop_fig(hR, R, w=300, h=230):
    f = Fig(w, h)
    y0 = h - 16
    Rp = 36.0
    cx = 175
    hp = hR * Rp
    xs = 30
    f.line(xs, y0 - hp, 50, y0 - hp, GR, 2)
    # 경사 내리막(곡선)
    f.path('M %s %s C %s %s, %s %s, %s %s' % (50, y0 - hp, 90, y0 - hp * .1 - 20, 110, y0, cx - Rp * 1.0, y0), 'none', INK, 2.4)
    f.line(cx - Rp, y0, w - 8, y0, INK, 2.4)
    f.circ(cx, y0 - Rp, Rp, 'none', INK, 2.4)
    f.circ(cx, y0 - 2 * Rp, 4.5, RD, INK, 1); f.text(cx + 12, y0 - 2 * Rp - 6, '최고점', 12, 'start', True, RD)
    f.line(cx, y0 - Rp, cx + Rp * .7, y0 - Rp - Rp * .7, GR, 1.2); f.text(cx + 10, y0 - Rp * 1.0 + 16, 'R', 12.5, 'start', True, GR)
    f.circ(60, y0 - hp - 7, 6, BL, INK, 1.2)
    f.line(24, y0, 50, y0, GR, 1)
    _dim_v(f, 22, y0 - hp, y0, 'h', RD, 'left')
    f.line(24, y0 - hp, 60, y0 - hp, '#9fb0c6', 1, '3 3')
    return f.svg()


@T('ph053')
def pendulum_energy(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'd'])
    cosv = {37: Fr(4, 5), 53: Fr(3, 5), 60: Fr(1, 2), 90: Fr(0)}
    if fam == 'a':
        for _ in range(300):
            th = r.choice([37, 53, 60, 90])
            v = r.randint(2, 10)
            hh = Fr(v * v, 20)
            L = hh / (1 - cosv[th])
            if _ok(L) and _ok(hh) and L >= Fr(1, 2): break
        else:
            return None
        assert Fr(v * v) == 2 * G * L * (1 - cosv[th])
        ask = r.choice(['v', 'v', 'h'])
        fig = FIG(_pendulum_fig(float(L), th), '52%')
        base = '그림과 같이 길이 %s m인 가벼운 실에 질량 m인 물체를 매달아 실이 연직선과 %d°를 이루는 점 A에서 가만히 놓았다. ' % (_F(L), th)
        if ask == 'v':
            body = P(base + '물체가 가장 낮은 점 B를 지날 때의 속력은? (단, g = 10 m/s²이며 공기 저항은 무시한다. cos37° = 0.8, cos53° = 0.6)') + fig
            ws = _ws(v, [_isq(2 * G * L) or v + 1, _isq(20 * L * cosv[th]) or v + 2, v * 2, v - 1 if v > 1 else v + 3, _isq(10 * L * (1 - cosv[th])) or v + 4], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='a', sort='num',
                      steps=['A와 B의 높이 차 h = L - L cos%d° = %s × (1 - %s) = %s m' % (th, _F(L), _F(cosv[th]), _F(hh)), '역학적 에너지 보존 : mgh = ½mv²', 'v = √(2 × 10 × %s) = %d m/s' % (_F(hh), v)],
                      core='진자의 높이 변화 h = L(1 - cosθ)이며 mgh = ½mv²로 최저점 속력을 구한다.', point='실의 길이가 아니라 높이 차를 사용한다.')
        body = P(base + '점 A는 가장 낮은 점 B보다 얼마나 높은 곳인가? (단, 연직선과 이루는 각 %d°는 cos%d° = %s이다.)' % (th, th, _fx(cosv[th]))) + fig
        ws = _ws(hh, [L, L * cosv[th], L * (1 - cosv[th]) * 2, L * (1 - cosv[th]) / 2, L * (1 + cosv[th])], lambda c: _F(c) + ' m')
        return mc(body, '%s m' % _F(hh), ws, r=r, lv='하', fam='a', sort='num',
                  steps=['높이 차 h = L(1 - cosθ)', 'h = %s × (1 - %s) = %s m' % (_F(L), _fx(cosv[th]), _F(hh))],
                  core='진자의 높이 변화 h = L(1 - cosθ).', point='그림에서 높이 차를 삼각비로 구한다.')
    if fam == 'b':
        th = r.choice([37, 53, 60, 90])
        m = r.choice([0.5, 1, 2, 3, 4, 5])
        mm = Fr(m).limit_denominator(10)
        L = r.choice([Fr(1, 2), 1, Fr(3, 2), 2, Fr(5, 2), 4])
        v2 = 2 * G * L * (1 - cosv[th])
        T = mm * G + mm * v2 / L
        assert T == mm * G * (3 - 2 * cosv[th])
        if not _ok(T): return None
        fig = FIG(_pendulum_fig(float(L), th), '52%')
        body = P('그림과 같이 길이 %s m인 가벼운 실에 질량 %s kg인 물체를 매달아 실이 연직선과 %d°를 이루는 점 A에서 가만히 놓았다. 물체가 가장 낮은 점 B를 지날 때 실이 물체를 당기는 힘의 크기는? (단, g = 10 m/s²이며 공기 저항은 무시한다. cos37° = 0.8, cos53° = 0.6)' % (_F(L), _F(m), th)) + fig
        ws = _ws(T, [mm * G, mm * v2 / L, 2 * mm * G, mm * G * (3 - cosv[th]), mm * G * (2 - cosv[th]) , mm * G * (1 + 2 * (1 - cosv[th]))], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(T), ws, r=r, lv='상', fam='b', sort='num',
                  steps=['B에서의 속력 : v² = 2gL(1 - cos%d°) = 2 × 10 × %s × %s = %s' % (th, _F(L), _fx(1 - cosv[th]), _F(v2)),
                         'B에서 구심력 : T - mg = mv²/L 이므로 T = mg + mv²/L',
                         'T = %s × 10 + %s × %s ÷ %s = %s N' % (_F(m), _F(m), _F(v2), _F(L), _F(T))],
                  core='최저점에서 (장력 - 중력) = 구심력 = mv²/L 이며 v는 에너지 보존으로 구한다.', point='에너지 보존과 원운동의 힘의 관계를 연결한다.')
    if fam == 'c':
        for _ in range(300):
            hA = r.randint(4, 14)
            hs = r.sample(range(0, hA + 8), 3)
            hB, hC, hD = hs
            pts = [('A', hA), ('B', hB), ('C', hC), ('D', hD)]
            if len(set(x[1] for x in pts)) < 4: continue
            if any(abs(a[1] - b[1]) < 2 for a in pts for b in pts if a is not b): continue
            break
        ask = r.choice(['v0', 'v0', 'max'])
        # A 에서 정지 출발. 언덕 : hD > hA 이면 못 넘음.
        top = max(hB, hC, hD)
        fig = FIG(_track_fig(pts), '70%')
        if ask == 'v0':
            hi = max(hB, hC, hD)
            if hi <= hA: return None
            tgt = [n for n, hh in (('B', hB), ('C', hC), ('D', hD)) if hh == hi][0]
            v0 = None
            d = hi - hA
            v0 = _isq(2 * G * d)
            if v0 is None: return None
            body = P('그림은 마찰이 없는 롤러코스터 트랙의 점 A, B, C, D의 높이를 나타낸 것이다. 수레를 점 A에서 트랙을 따라 출발시켜 점 %s(가장 높은 점)를 지나가게 하려면 점 A에서 최소한 얼마의 속력으로 출발시켜야 하는가? (단, g = 10 m/s²이며 수레는 트랙을 이탈하지 않는다.)' % tgt) + fig
            ws = _ws(v0, [d, _isq(10 * d) or v0 + 1, v0 * 2, v0 + 2, v0 - 1 if v0 > 1 else v0 + 3], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v0), ws, r=r, lv='상', fam='c', sort='num',
                      steps=['점 %s(높이 %d m)를 간신히 통과할 때 그곳에서 속력이 0이다.' % (tgt, hi), '½mv₀² = mg(%d - %d) 이므로 v₀² = 2 × 10 × %d = %d' % (hi, hA, d, v0 * v0), 'v₀ = %d m/s' % v0],
                      core='언덕을 넘으려면 처음 역학적 에너지가 언덕 꼭대기의 위치 에너지 이상이어야 한다.', point='가장 높은 언덕과의 높이 차로 최소 속력을 구한다.')
        # 가장 낮은 점의 속력 (정지 출발)
        lo = min(hB, hC, hD)
        if lo >= hA: return None
        tgt = [n for n, hh in (('B', hB), ('C', hC), ('D', hD)) if hh == lo][0]
        d = hA - lo
        v = _isq(2 * G * d)
        if v is None: return None
        body = P('그림은 마찰이 없는 롤러코스터 트랙의 점 A, B, C, D의 높이를 나타낸 것이다. 수레를 점 A에서 가만히 놓았을 때 수레가 가장 낮은 점 %s를 지나는 순간의 속력은? (단, g = 10 m/s²이며 수레는 트랙을 이탈하지 않고 도중에 A보다 높은 곳은 없다고 한다.)' % tgt) + fig
        if top > hA: return None
        ws = _ws(v, [_isq(10 * d) or v + 1, d, v * 2, v + 2, v - 1 if v > 1 else v + 3], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['점 %s는 A보다 %d m 낮다.' % (tgt, d), 'mgd = ½mv² 이므로 v = √(2 × 10 × %d) = %d m/s' % (d, v)],
                  core='마찰이 없는 트랙에서 속력은 높이 차이만으로 결정된다.', point='경로의 모양과 무관하게 높이 차를 본다.')
    # d: 원형 트랙
    for _ in range(300):
        R = r.choice([Fr(1, 2), 1, Fr(3, 2), 2, Fr(5, 2)])
        hR = r.choice([Fr(5, 2), 3, Fr(7, 2), 4, 5])
        hh = hR * R
        m = r.choice([0.5, 1, 2, 3])
        mm = Fr(m).limit_denominator(10)
        v2 = 2 * G * (hh - 2 * R)
        N = mm * v2 / R - mm * G
        if _ok(hh) and _ok(N) and N >= 0 and _ok(R) and hR <= 5: break
    else:
        return None
    fig = FIG(_loop_fig(float(hR), float(R)), '56%')
    ask = r.choice(['N', 'N', 'min'])
    if ask == 'min':
        body = P('그림과 같이 마찰이 없는 트랙의 높이 h인 지점에서 질량 m인 물체를 가만히 놓았더니 반지름 %s m인 원형 트랙의 최고점을 간신히 통과하여 돌아 나왔다(최고점에서 트랙이 물체에 작용하는 힘이 0). h는? (단, g = 10 m/s²이다.)' % _F(R)) + fig
        hmin = Fr(5, 2) * R
        ws = _ws(hmin, [2 * R, 3 * R, 2 * R + R / 2 * 0 + Fr(1, 2), Fr(3, 2) * R, 5 * R], lambda c: _F(c) + ' m')
        return mc(body, '%s m' % _F(hmin), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['최고점에서 중력이 구심력 : mg = mv²/R 이므로 v² = gR = %s' % _F(G * R), '역학적 에너지 보존 : mgh = mg(2R) + ½mv²', 'h = 2R + R/2 = %s m' % _F(hmin)],
                  core='원형 트랙 최고점을 통과하는 최소 조건은 mg = mv²/R 이며 이때 h = 2.5R이다.', point='최고점에서 수직 항력이 0이 되는 조건을 쓴다.')
    body = P('그림과 같이 마찰이 없는 트랙의 높이 h = %s m인 지점에서 질량 %s kg인 물체를 가만히 놓았더니 반지름 %s m인 원형 트랙을 따라 운동하였다. 원형 트랙의 최고점에서 트랙이 물체에 작용하는 수직 항력의 크기는? (단, g = 10 m/s²이다.)' % (_F(hh), _F(m), _F(R))) + fig
    ws = _ws(N, [mm * G, mm * v2 / R, mm * G * 2, mm * v2 / R + mm * G, N + mm * G * 2], lambda c: _F(c) + ' N') if N else ['10 N', '20 N', '5 N', '15 N', '30 N']
    if N == 0: ws = [w for w in ws if w != '0 N']
    return mc(body, '%s N' % _F(N), ws, r=r, lv='상', fam='d', sort='num',
              steps=['최고점의 속력 : mg(%s) = mg(2 × %s) + ½mv² 이므로 v² = 2 × 10 × (%s - %s) = %s' % (_F(hh), _F(R), _F(hh), _F(2 * R), _F(v2)),
                     '최고점에서 N + mg = mv²/R 이므로 N = %s × %s ÷ %s - %s × 10' % (_F(m), _F(v2), _F(R), _F(m)), 'N = %s N' % _F(N)],
              core='원형 트랙 최고점에서 (수직 항력 + 중력) = mv²/R 이다.', point='에너지 보존으로 속력을 구한 뒤 구심력 식에 대입한다.')


# ================================================================== ph054 마찰이 있을 때의 에너지 손실
def _rough_fig(h_lab=None, d_lab=None, rough=(0.45, 0.85), w=320, h=190, mu_lab=None, start='curve'):
    f = Fig(w, h)
    y0 = h - 36
    f.line(130, y0, w - 14, y0, INK, 2.2)
    xa, xb = 130 + rough[0] * (w - 14 - 130), 130 + rough[1] * (w - 14 - 130)
    f.rect(xa, y0, xb - xa, 8, '#e8d7b8', GR, 1)
    for i in range(int(xa), int(xb), 8): f.line(i, y0 + 8, i + 5, y0, GR, 1)
    f.path('M 30 30 C 80 36, 100 %s, 130 %s' % (y0, y0), 'none', INK, 2.4)
    f.circ(36, 24, 7, BL, INK, 1.2)
    _dim_v(f, 18, 24, y0, h_lab or 'h', RD, 'left')
    f.line(18, 24, 36, 24, '#9fb0c6', 1, '3 3')
    if d_lab: _dim_h(f, xa, xb, y0 + 28, d_lab, GR)
    if mu_lab: f.text((xa + xb) / 2, y0 + 8 + 18 - 36 + 0, '', 10)
    f.text((xa + xb) / 2, y0 - 8, '거친 구간' if mu_lab is None else '거친 구간 (μ = %s)' % mu_lab, 12.5, 'middle', True, GR)
    return f.svg()


@T('ph054')
def friction_loss(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'd', 'd', 'e', 'e'])
    if fam == 'a':
        for _ in range(300):
            v0 = r.choice([2, 4, 5, 6, 8, 10, 12, 15, 20])
            mu = r.choice([Fr(1, 10), Fr(1, 5), Fr(1, 4), Fr(2, 5), Fr(1, 2), Fr(3, 10)])
            s = Fr(v0 * v0, 2 * G) / mu
            if _ok(s) and s >= 1: break
        else:
            return None
        m = r.choice([1, 2, 3, 4, 5])
        assert 2 * mu * G * s == v0 * v0
        ask = r.choice(['s', 's', 'mu', 'Q'])
        base = '거친 수평면에서 질량 %d kg인 물체가 %d m/s의 속력으로 미끄러지기 시작했다. ' % (m, v0)
        if ask == 's':
            body = P(base + '물체와 면 사이의 운동 마찰 계수가 %s일 때, 물체가 정지할 때까지 미끄러진 거리는? (단, g = 10 m/s²이다.)' % _F(mu))
            ws = _ws(s, [Fr(v0 * v0, 2 * G), s * mu if False else s * 2, Fr(v0 * v0, G) / mu, s / 2, Fr(v0, 1) / mu], lambda c: _F(c) + ' m')
            return mc(body, '%s m' % _F(s), ws, r=r, lv='중', fam='a', sort='num',
                      steps=['운동 에너지가 모두 마찰력이 한 일로 소모된다 : ½mv₀² = μmg s', 's = v₀²/(2μg) = %d² ÷ (2 × %s × 10) = %s m' % (v0, _F(mu), _F(s)),
                             '(확인) a = μg = %s m/s², s = v₀²/2a = %s m' % (_F(mu * G), _F(Fr(v0 * v0) / (2 * mu * G)))],
                      core='마찰력이 한 일 = 감소한 운동 에너지 : μmgs = ½mv₀².', point='질량은 약분된다.')
        if ask == 'mu':
            body = P(base + '물체가 %s m를 미끄러진 후 정지하였다. 물체와 면 사이의 운동 마찰 계수는? (단, g = 10 m/s²이다.)' % _F(s))
            ws = _ws(mu, [mu * 2, mu / 2, Fr(v0 * v0, 2 * G) / (s * s) if False else Fr(v0, 10), mu * 5 if mu * 5 < 1 else mu / 5, Fr(1, 2) if mu != Fr(1, 2) else Fr(3, 5)], lambda c: _F(c))
            return mc(body, _F(mu), ws, r=r, lv='중', fam='a', sort='num',
                      steps=['½mv₀² = μmgs 에서 μ = v₀²/(2gs)', 'μ = %d² ÷ (2 × 10 × %s) = %s' % (v0, _F(s), _F(mu))],
                      core='μmgs = ½mv₀² 에서 μ를 구한다.', point='질량 m이 약분되는 것을 이용한다.')
        Q = Fr(1, 2) * m * v0 * v0
        f = mu * m * G
        body = P(base + '물체가 정지할 때까지 마찰력이 물체에 한 일의 크기는? (단, 정지할 때까지 마찰력만 일을 하며 g = 10 m/s²이다.)')
        ws = _ws(Q, [f * s * 2 if False else f * s * 2, m * v0, f, m * v0 * v0, Q / 2], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(Q), ws, r=r, lv='하', fam='a', sort='num',
                  steps=['마찰력이 한 일의 크기 = 감소한 운동 에너지 = ½mv₀²', '= ½ × %d × %d² = %s J' % (m, v0, _F(Q))],
                  core='마찰력이 한 일의 크기는 손실된 역학적 에너지(열로 전환)와 같다.', point='미끄러진 거리를 몰라도 운동 에너지 변화로 구한다.')
    if fam == 'b':
        for _ in range(300):
            h = r.choice([Fr(1, 2), 1, Fr(3, 2), 2, Fr(5, 2), 3, 4, 5])
            mu = r.choice([Fr(1, 10), Fr(1, 5), Fr(1, 4), Fr(2, 5), Fr(1, 2)])
            s = h / mu
            if _ok(s): break
        else:
            return None
        f = Fig(310, 170)
        y0 = 140
        f.path('M 30 30 C 70 36, 90 %s, 120 %s' % (y0, y0), 'none', INK, 2.4)
        f.rect(120, y0, 175, 8, '#e8d7b8', GR, 1)
        for i in range(120, 295, 8): f.line(i, y0 + 8, i + 5, y0, GR, 1)
        f.line(120, y0, 295, y0, INK, 2.2)
        f.circ(36, 24, 7, BL, INK, 1.2)
        _dim_v(f, 16, 24, y0, 'h = %s m' % _F(h), RD, 'left')
        f.line(16, 24, 36, 24, '#9fb0c6', 1, '3 3')
        f.text(210, y0 - 8, '거친 수평면 (μ = %s)' % _F(mu), 12.5, 'middle', True, GR)
        fig = FIG(f.svg(), '62%')
        body = P('그림과 같이 마찰이 없는 곡면의 높이 %s m인 지점에서 물체를 가만히 놓았더니 곡면을 내려와 거친 수평면에서 미끄러지다가 정지하였다. 수평면과 물체 사이의 운동 마찰 계수가 %s일 때, 물체가 수평면에서 미끄러진 거리는? (단, g = 10 m/s²이다.)' % (_F(h), _F(mu))) + fig
        assert mu * G * s == G * h
        ws = _ws(s, [h * mu, h, h / (mu * 2), s * 2, Fr(h, 1) * 10 * mu], lambda c: _F(c) + ' m')
        return mc(body, '%s m' % _F(s), ws, r=r, lv='중', fam='b', sort='num',
                  steps=['처음 위치 에너지가 마찰에 의해 모두 소모된다 : mgh = μmg s', 's = h/μ = %s ÷ %s = %s m' % (_F(h), _F(mu), _F(s))],
                  core='손실된 역학적 에너지 = 마찰력이 한 일 : mgh = μmgs.', point='곡면 구간은 마찰이 없으므로 수평면 마찰로만 에너지가 줄어든다.')
    if fam == 'c':
        th = r.choice([37, 53, 45])
        cot = {37: Fr(4, 3), 53: Fr(3, 4), 45: Fr(1)}[th]
        for _ in range(500):
            v = r.randint(2, 12)
            mu = r.choice([Fr(1, 10), Fr(1, 5), Fr(1, 4), Fr(3, 10), Fr(2, 5), Fr(1, 2)])
            if mu * cot >= 1: continue
            h = Fr(v * v, 20) / (1 - mu * cot)
            if _ok(h) and h <= 15: break
        else:
            return None
        sinv = {37: Fr(3, 5), 53: Fr(4, 5), 45: None}[th]
        if sinv is None:
            return None
        L = h / sinv
        a = G * (sinv - mu * (1 - sinv * sinv).limit_denominator() ) if False else None
        cosv = {37: Fr(4, 5), 53: Fr(3, 5)}[th]
        acc = G * (sinv - mu * cosv)
        assert 2 * acc * L == v * v
        m = r.choice([1, 2, 4, 5])
        loss = mu * m * G * cosv * L
        assert loss == m * G * h - Fr(1, 2) * m * v * v
        fig_svg, _ = _incline_fig(th, '%s m' % _F(h), None)
        body = P('그림과 같이 경사각 %d°인 거친 빗면의 높이 %s m인 지점에서 질량 %d kg인 물체를 가만히 놓았더니 빗면 아래 끝에서의 속력이 %d m/s였다. 빗면에서 물체의 역학적 에너지가 줄어든 양은? (단, g = 10 m/s²이다.)' % (th, _F(h), m, v)) + FIG(fig_svg, '58%')
        ws = _ws(loss, [m * G * h, Fr(1, 2) * m * v * v, loss * 2, m * G * h + Fr(1, 2) * m * v * v, loss / 2], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(loss), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['처음 역학적 에너지 = mgh = %d × 10 × %s = %s J' % (m, _F(h), _F(m * G * h)), '나중 운동 에너지 = ½ × %d × %d² = %s J' % (m, v, _F(Fr(1, 2) * m * v * v)),
                         '줄어든 양(마찰열) = %s - %s = %s J' % (_F(m * G * h), _F(Fr(1, 2) * m * v * v), _F(loss))],
                  core='마찰이 있으면 줄어든 역학적 에너지 = 마찰력이 한 일(열에너지).', point='처음과 나중의 역학적 에너지 차이를 구한다.')
    if fam == 'd':
        # 빗면 : 마찰력 크기 구하기 / 마찰계수
        th = r.choice([37, 53])
        sinv = {37: Fr(3, 5), 53: Fr(4, 5)}[th]
        cosv = {37: Fr(4, 5), 53: Fr(3, 5)}[th]
        for _ in range(500):
            m = r.choice([1, 2, 3, 4, 5, 10])
            L = r.choice([2, 3, 4, 5, 6, 8, 10])
            mu = r.choice([Fr(1, 10), Fr(1, 5), Fr(1, 4), Fr(3, 10), Fr(2, 5)])
            if sinv <= mu * cosv: continue
            acc = G * (sinv - mu * cosv)
            v = _isq(2 * acc * L)
            if v and v > 0: break
        else:
            return None
        h = L * sinv
        fk = mu * m * G * cosv
        assert fk * L == m * G * h - Fr(1, 2) * m * v * v
        svg, _ = _incline_fig(th, '%s m' % _F(h), '%s m' % _F(L))
        body = P('그림과 같이 경사각 %d°인 거친 빗면의 위쪽에서 질량 %d kg인 물체를 가만히 놓았더니 길이 %d m인 빗면을 미끄러져 내려와 아래 끝에서 속력이 %d m/s가 되었다. 물체가 빗면에서 받은 마찰력의 크기는? (단, g = 10 m/s²이고 마찰력은 일정하다.)' % (th, m, L, v)) + FIG(svg, '58%')
        ws = _ws(fk, [fk * L, m * G * sinv, m * G * sinv - fk if m * G * sinv > fk else fk + 2, fk / 2, m * G * cosv], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(fk), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['mgh = %d × 10 × %s = %s J, 나중 운동 에너지 = ½ × %d × %d² = %s J' % (m, _F(h), _F(m * G * h), m, v, _F(Fr(1, 2) * m * v * v)), '마찰력이 한 일 = 줄어든 에너지 = %s J' % _F(fk * L),
                         '마찰력의 크기 f = %s ÷ %d m = %s N' % (_F(fk * L), L, _F(fk)), '(확인) f = μmg cos%d° = %s × %d × 10 × %s = %s N' % (th, _F(mu), m, _F(cosv), _F(fk))],
                  core='마찰력이 한 일 fL = 줄어든 역학적 에너지.', point='빗면 길이 L과 높이 h를 구분한다(h = L sinθ).')
    # e: 거친 구간
    for _ in range(500):
        h = r.choice([1, Fr(5, 4), Fr(9, 5), Fr(8, 5), 2, 3, Fr(5, 2), 4, 5])
        mu = r.choice([Fr(1, 10), Fr(1, 5), Fr(1, 4), Fr(2, 5), Fr(1, 2)])
        d = r.choice([1, 2, 3, 4, 5])
        v2 = 2 * G * (h - mu * d)
        if v2 > 0 and _isq(v2): break
    else:
        return None
    v = _isq(v2)
    # 검증 : 거친 구간 감속
    a = mu * G
    assert Fr(v * v) == 2 * G * h - 2 * a * d
    fig = FIG(_rough_fig('h = %s m' % _F(h), '%s m' % _F(d), mu_lab=_F(mu)), '62%')
    ask = r.choice(['v', 'v', 'n'])
    if ask == 'v':
        body = P('그림과 같이 마찰이 없는 곡면의 높이 %s m인 지점에서 물체를 가만히 놓았다. 수평면에는 길이 %s m의 거친 구간(운동 마찰 계수 %s)이 있다. 물체가 이 구간을 지나 나왔을 때의 속력은? (단, g = 10 m/s²이다.)' % (_F(h), _F(d), _F(mu))) + fig
        ws = _ws(v, [_isq(2 * G * h) or v + 1, _isq(2 * G * (h - d)) or v + 2, v * 2, v - 1 if v > 1 else v + 3, _isq(2 * G * mu * d) or v + 4], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='상', fam='e', sort='num',
                  steps=['거친 구간에서 마찰력이 한 일 = -μmgd = -%s × m × 10 × %s' % (_F(mu), _F(d)), 'mgh - μmgd = ½mv² 이므로 v² = 2 × 10 × (%s - %s × %s) = %d' % (_F(h), _F(mu), _F(d), v * v), 'v = %d m/s' % v],
                  core='마찰 구간을 지날 때 줄어드는 역학적 에너지는 μmgd이다.', point='위치 에너지 감소분에서 마찰열을 뺀 것이 운동 에너지이다.')
    # n : 정지하기 전 거친 구간을 몇 번 지나는가 (정수 배)
    cnt = h / (mu * d)
    if cnt.denominator != 1 or cnt < 2 or cnt > 12: return None
    body = P('그림과 같이 마찰이 없는 곡면의 높이 %s m인 지점에서 물체를 가만히 놓았다. 수평면에는 길이 %s m의 거친 구간(운동 마찰 계수 %s)이 있고, 양 끝은 마찰이 없는 곡면이어서 물체는 거친 구간을 왕복하며 운동한다. 물체가 정지할 때까지 거친 구간을 지난 총 횟수(한 번 통과를 1회로 센다)는? (단, 정지는 거친 구간의 끝에서 이루어진다.)' % (_F(h), _F(d), _F(mu))) + fig
    right = '%d회' % cnt
    wr = ['%d회' % x for x in (cnt - 1, cnt + 1, cnt * 2, max(1, cnt // 2), cnt + 2) if x != cnt]
    return mc(body, right, wr[:5], r=r, lv='상', fam='e', sort='num',
              steps=['정지할 때까지 마찰력이 한 총일 = mgh : μmg × (총 이동 거리) = mgh', '총 거리 = h/μ = %s ÷ %s = %s m' % (_F(h), _F(mu), _F(h / mu)), '횟수 = %s ÷ %s = %d회' % (_F(h / mu), _F(d), cnt)],
              core='처음 위치 에너지가 모두 마찰열이 될 때까지 거친 구간을 지난다 : mgh = μmg × (총 거리).', point='총 이동 거리를 구간 길이로 나눈다.')


# ================================================================== ph055 일률과 효율
def _flow_fig(Ein, Eout, Eloss, unk='out', w=320, h=170, unit='J'):
    f = Fig(w, h)
    f.rect(115, 50, 90, 60, '#e8eefb', INK, 1.8, 6)
    f.text(160, 85, '기계', 15, 'middle', True, INK)
    f.arrow(20, 80, 112, 80, BL, 5)
    f.text(66, 62, '공급 에너지', 12, 'middle', True, BL)
    f.text(66, 104, '%s %s' % (_F(Ein), unit), 13, 'middle', True, BL)
    f.arrow(205, 80, 300, 80, GN, 5 if unk != 'out' else 5)
    f.text(255, 62, '유용한 일', 12, 'middle', True, GN)
    f.text(255, 104, ('%s %s' % (_F(Eout), unit)) if unk != 'out' else '?', 13, 'middle', True, GN)
    f.arrow(160, 112, 160, 158, RD, 3)
    f.text(214, 138, '열 손실', 12, 'start', True, RD)
    f.text(214, 154, ('%s %s' % (_F(Eloss), unit)) if unk != 'loss' else '?', 13, 'start', True, RD)
    return f.svg()


@T('ph055')
def power_efficiency(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        for _ in range(300):
            m = r.choice([5, 10, 20, 25, 30, 40, 50, 100])
            h = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15])
            t = r.choice([2, 4, 5, 8, 10, 20, 25])
            Wk = m * G * h
            Pout = Fr(Wk, t)
            eff = r.choice([Fr(1, 2), Fr(4, 5), Fr(3, 5), Fr(1, 4), Fr(2, 5), Fr(3, 4), Fr(8, 10), Fr(9, 10)])
            Pin = Pout / eff
            if _ok(Pout) and _ok(Pin): break
        else:
            return None
        ask = r.choice(['Pout', 'Pin', 'eff', 'Ein'])
        base = '모터가 질량 %d kg인 물체를 일정한 속력으로 %d m 끌어올리는 데 %d초가 걸렸다. ' % (m, h, t)
        if ask == 'Pout':
            body = P(base + '모터가 물체에 한 일의 일률(유용한 일률)은? (단, g = 10 m/s²이다.)')
            ws = _ws(Pout, [Wk, Pout * t, Fr(m * h, t), Fr(m * G, t), Pout / 2], lambda c: _F(c) + ' W')
            return mc(body, '%s W' % _F(Pout), ws, r=r, lv='하', fam='a', sort='num',
                      steps=['등속으로 올리므로 모터가 한 일 = mgh = %d × 10 × %d = %d J' % (m, h, Wk), '일률 P = W/t = %d ÷ %d = %s W' % (Wk, t, _F(Pout))],
                      core='일률 P = W/t, 등속으로 올릴 때 한 일은 mgh이다.', point='한 일을 걸린 시간으로 나눈다.')
        if ask == 'Pin':
            body = P(base + '이 모터의 효율이 %s%%일 때 모터가 공급받은 전력(입력 일률)은? (단, g = 10 m/s²이다.)' % _F(eff * 100))
            ws = _ws(Pin, [Pout, Pout * eff, Pout * (1 + eff), Pout / eff / 2, Wk / eff], lambda c: _F(c) + ' W')
            return mc(body, '%s W' % _F(Pin), ws, r=r, lv='상', fam='a', sort='num',
                      steps=['유용한 일률 = mgh/t = %d ÷ %d = %s W' % (Wk, t, _F(Pout)), '효율 = 유용한 일률 ÷ 입력 일률 이므로 입력 일률 = %s ÷ %s = %s W' % (_F(Pout), _F(eff), _F(Pin))],
                      core='효율 = (유용한 일률) ÷ (공급한 일률) × 100 %.', point='효율로 나누어 입력 일률을 구한다(곱하지 않는다).')
        if ask == 'eff':
            body = P(base + '이 모터가 소비한 전력이 %s W일 때 모터의 효율은? (단, g = 10 m/s²이다.)' % _F(Pin))
            right = '%s%%' % _F(eff * 100)
            ws = _ws(eff * 100, [Pin / Pout * 100 if Pin / Pout * 100 <= 100 else Pin / Pout, eff * 50, 100 - eff * 100, Pout, eff * 10], lambda c: _F(c) + '%')
            ws = [w.replace('%', '%') for w in ws]
            return mc(body, right, ws, r=r, lv='중', fam='a', sort='num',
                      steps=['유용한 일률 = %d ÷ %d = %s W' % (Wk, t, _F(Pout)), '효율 = %s ÷ %s × 100 = %s%%' % (_F(Pout), _F(Pin), _F(eff * 100))],
                      core='효율 = 유용한 일률/입력 일률 × 100 %.', point='출력과 입력을 바꾸어 나누지 않는다.')
        Ein = Pin * t
        body = P(base + '이 모터의 효율이 %s%%일 때 모터가 %d초 동안 공급받은 에너지는? (단, g = 10 m/s²이다.)' % (_F(eff * 100), t))
        ws = _ws(Ein, [Wk, Wk * eff, Pin, Wk / eff / 2, Wk + Ein * 0 + 100], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(Ein), ws, r=r, lv='상', fam='a', sort='num',
                  steps=['유용한 에너지(한 일) = mgh = %d J' % Wk, '효율 = 유용한 에너지 ÷ 공급 에너지 이므로 공급 에너지 = %d ÷ %s = %s J' % (Wk, _F(eff), _F(Ein))],
                  core='효율 = (유용한 에너지) ÷ (공급된 에너지).', point='열 손실 때문에 공급 에너지가 더 크다.')
    if fam == 'b':
        kind = r.choice(['flat', 'flat', 'slope'])
        for _ in range(300):
            v = r.choice([2, 4, 5, 6, 8, 10, 15, 20, 25])
            if kind == 'flat':
                Fm = r.choice([50, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 2000])
            else:
                m = r.choice([100, 200, 500, 1000, 50])
                th = r.choice([30, 37])
                sn = {30: Fr(1, 2), 37: Fr(3, 5)}[th]
                fr_ = r.choice([0, 50, 100, 200, 300])
                Fm = m * G * sn + fr_
            Pw = Fm * v
            if Pw <= 200000: break
        ask = r.choice(['P', 'F', 'v'])
        if kind == 'flat':
            base = '자동차가 수평 도로에서 일정한 속력으로 달리고 있다. 자동차가 받는 저항력(마찰·공기 저항)의 크기는 %d N이다. ' % Fm
            if ask == 'P':
                body = P(base + '속력이 %d m/s일 때 엔진이 내는 일률은?' % v)
                ws = _ws(Pw, [Fm, Fm / v if Fm % v == 0 else Fm * 2, Fm * v * v, Fm + v, Pw * 2], lambda c: _F(c) + ' W')
                return mc(body, '%s W' % _F(Pw), ws, r=r, lv='하', fam='b', sort='num',
                          steps=['등속이므로 엔진의 견인력 = 저항력 = %d N' % Fm, '일률 P = Fv = %d × %d = %d W' % (Fm, v, Pw)],
                          core='일률 P = Fv (힘과 속력의 곱).', point='등속 운동에서는 구동력과 저항력이 같다.')
            if ask == 'F':
                body = P('자동차가 수평 도로에서 %d m/s의 일정한 속력으로 달릴 때 엔진의 일률이 %d W이다. 자동차가 받는 저항력의 크기는?' % (v, Pw))
                ws = _ws(Fm, [Pw, Pw * v, Fm * 2, Fm / 2, Pw / v / 2], lambda c: _F(c) + ' N')
                return mc(body, '%s N' % _F(Fm), ws, r=r, lv='중', fam='b', sort='num',
                          steps=['P = Fv 이므로 F = P/v = %d ÷ %d = %d N' % (Pw, v, Fm), '등속이므로 저항력의 크기도 %d N이다.' % Fm],
                          core='P = Fv, 등속 운동에서 구동력 = 저항력.', point='일률을 속력으로 나누면 힘이 된다.')
            body = P('수평 도로에서 엔진의 일률이 %d W로 일정한 자동차가 크기 %d N의 저항력을 받으며 등속으로 달린다. 이때의 속력은?' % (Pw, Fm))
            ws = _ws(v, [Pw, Fm, Pw * Fm, v * 2, v / 2 if v % 2 == 0 else v + 3], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='b', sort='num',
                      steps=['등속이므로 견인력 = 저항력 = %d N' % Fm, 'v = P/F = %d ÷ %d = %d m/s' % (Pw, Fm, v)],
                      core='P = Fv 에서 v = P/F.', point='등속일 때 F는 저항력과 같다.')
        # slope
        body = P('질량 %d kg인 수레가 경사각 %d°인 빗면 위로 일정한 속력 %d m/s로 올라가고 있다. 수레가 받는 마찰력의 크기는 %d N(빗면 아래 방향)이다. 이때 수레를 끄는 힘의 일률은? (단, sin%d° = %s, g = 10 m/s²이다.)' % (m, th, v, fr_, th, _F(sn)))
        Fpull = m * G * sn + fr_
        ws = _ws(Pw, [m * G * sn * v, fr_ * v, m * G * v, (m * G * sn - fr_) * v if m * G * sn > fr_ else Pw + 100, Pw * 2], lambda c: _F(c) + ' W')
        return mc(body, '%s W' % _F(Pw), ws, r=r, lv='상', fam='b', sort='num',
                  steps=['등속이므로 끄는 힘 = (중력의 빗면 성분) + 마찰력 = %d × 10 × %s + %d = %s N' % (m, _F(sn), fr_, _F(Fpull)), 'P = Fv = %s × %d = %s W' % (_F(Fpull), v, _F(Pw))],
                  core='등속으로 빗면을 오를 때 끄는 힘 = mg sinθ + 마찰력, P = Fv.', point='힘의 평형으로 끄는 힘을 먼저 구한다.')
    if fam == 'c':
        for _ in range(300):
            Ein = r.choice([100, 200, 250, 400, 500, 800, 1000, 1200, 2000])
            eff = r.choice([Fr(1, 5), Fr(1, 4), Fr(2, 5), Fr(1, 2), Fr(3, 5), Fr(3, 4), Fr(4, 5), Fr(9, 10)])
            Eout = Ein * eff
            Eloss = Ein - Eout
            if _ok(Eout): break
        ask = r.choice(['eff', 'out', 'loss'])
        if ask == 'eff':
            fig = FIG(_flow_fig(Ein, Eout, Eloss, unk='none'), '62%')
            body = P('그림은 어떤 기계에 공급된 에너지가 유용한 일과 열로 전환되는 것을 나타낸 것이다. 이 기계의 효율은?') + fig
            right = '%s%%' % _F(eff * 100)
            ws = _ws(eff * 100, [Eloss / Ein * 100, Eout / Eloss * 100 if Eout / Eloss <= 1 else Eloss / Eout * 100, 100 - eff * 100 + 5, Eout, eff * 10], lambda c: _F(c) + '%')
            return mc(body, right, ws, r=r, lv='하', fam='c', sort='num',
                      steps=['공급 에너지 %d J = 유용한 일 %s J + 열 손실 %s J' % (Ein, _F(Eout), _F(Eloss)), '효율 = %s ÷ %d × 100 = %s%%' % (_F(Eout), Ein, _F(eff * 100))],
                      core='효율 = 유용한 일 ÷ 공급 에너지 × 100 %. (에너지 보존: 공급 = 유용한 일 + 손실)', point='분모는 공급된 전체 에너지이다.')
        if ask == 'out':
            fig = FIG(_flow_fig(Ein, Eout, Eloss, unk='out'), '62%')
            body = P('그림은 효율이 %s%%인 기계에 에너지가 공급되어 유용한 일과 열로 전환되는 것을 나타낸 것이다. 이 기계가 한 유용한 일(?)은?' % _F(eff * 100)) + fig
            ws = _ws(Eout, [Eloss, Ein, Ein * (1 - eff) + 0, Ein / 2, Ein * eff * 2 if Ein * eff * 2 < Ein * 2 else Ein * 3], lambda c: _F(c) + ' J')
            return mc(body, '%s J' % _F(Eout), ws, r=r, lv='중', fam='c', sort='num',
                      steps=['유용한 일 = 공급 에너지 × 효율 = %d × %s = %s J' % (Ein, _F(eff), _F(Eout)), '(확인) 열 손실 = %d - %s = %s J' % (Ein, _F(Eout), _F(Eloss))],
                      core='유용한 일 = 공급 에너지 × 효율.', point='효율을 곱해 유용한 에너지를 구한다.')
        fig = FIG(_flow_fig(Ein, Eout, Eloss, unk='loss'), '62%')
        body = P('그림은 효율이 %s%%인 기계에 에너지가 공급되어 유용한 일과 열로 전환되는 것을 나타낸 것이다. 열 손실(?)은?' % _F(eff * 100)) + fig
        ws = _ws(Eloss, [Eout, Ein, Ein * eff * eff, Ein / 2, Ein * 2], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(Eloss), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['유용한 일 = %d × %s = %s J' % (Ein, _F(eff), _F(Eout)), '에너지 보존에 의해 열 손실 = 공급 에너지 - 유용한 일 = %d - %s = %s J' % (Ein, _F(Eout), _F(Eloss))],
                  core='공급 에너지 = 유용한 일 + 열 손실.', point='손실은 공급에서 유용한 일을 뺀 값이다.')
    if fam == 'd':
        # 두 기계 비교 표
        for _ in range(300):
            EA = r.choice([200, 300, 400, 500, 600, 800, 1000])
            WA = EA * r.choice([Fr(1, 2), Fr(3, 5), Fr(4, 5), Fr(1, 4), Fr(3, 4)])
            EB = r.choice([200, 300, 400, 500, 600, 800, 1000])
            WB = EB * r.choice([Fr(1, 2), Fr(3, 5), Fr(4, 5), Fr(1, 4), Fr(3, 4)])
            tA, tB = r.choice([2, 4, 5, 10, 20]), r.choice([2, 4, 5, 10, 20])
            effA, effB = WA / EA, WB / EB
            PA, PB = WA / tA, WB / tB
            if effA == effB or PA == PB: continue
            if _ok(WA) and _ok(WB): break
        else:
            return None
        tb = table(['기계', '공급 에너지 (J)', '유용한 일 (J)', '걸린 시간 (s)'], [['A', EA, _F(WA), tA], ['B', EB, _F(WB), tB]])
        body = P('표는 두 기계 A, B가 일을 할 때의 공급 에너지, 한 유용한 일, 걸린 시간을 나타낸 것이다. 효율과 유용한 일의 일률을 비교한 것으로 옳은 것은?') + tb
        def cmp(a, b): return '크다' if a > b else '작다'
        right = '효율은 A가 B보다 %s, 일률은 A가 B보다 %s.' % (cmp(effA, effB), cmp(PA, PB))
        wr = []
        for c1 in ('크다', '작다'):
            for c2 in ('크다', '작다'):
                t_ = '효율은 A가 B보다 %s, 일률은 A가 B보다 %s.' % (c1, c2)
                if t_ != right: wr.append(t_)
        wr.append('효율은 A와 B가 같고, 일률은 A가 B보다 %s.' % cmp(PA, PB))
        return mc(body, right, wr[:5], r=r, lv='상', fam='d', sort='shuf',
                  steps=['효율 : A = %s ÷ %d = %s, B = %s ÷ %d = %s' % (_F(WA), EA, _F(effA), _F(WB), EB, _F(effB)), '일률 : A = %s ÷ %d = %s W, B = %s ÷ %d = %s W' % (_F(WA), tA, _F(PA), _F(WB), tB, _F(PB)),
                         '따라서 ' + right],
                  core='효율 = 유용한 일/공급 에너지, 일률 = 유용한 일/시간으로 서로 다른 개념이다.', point='효율과 일률을 각각 계산해 비교한다.')
    # e: 일정한 힘으로 가속 : 평균 일률, 순간 일률
    for _ in range(300):
        m = r.choice([1, 2, 4, 5, 10, 20])
        F = r.choice([10, 20, 30, 40, 50, 100])
        t = r.choice([2, 4, 5, 10])
        a = Fr(F, m); vt = a * t; s = Fr(1, 2) * a * t * t
        W = F * s; Pavg = W / t; Pins = F * vt
        if _ok(Pavg) and _ok(Pins) and vt.denominator == 1: break
    else:
        return None
    assert Pins == 2 * Pavg
    assert W == Fr(1, 2) * m * vt * vt
    ask = r.choice(['avg', 'ins'])
    base = '마찰이 없는 수평면에서 정지해 있던 질량 %d kg인 물체에 수평 방향으로 일정한 힘 %d N을 %d초 동안 작용했다. ' % (m, F, t)
    if ask == 'avg':
        body = P(base + '이 %d초 동안 힘이 한 일의 평균 일률은?' % t)
        ws = _ws(Pavg, [Pins, F * vt / 4 if False else Pins * 2, W, F * t, Pavg / 2], lambda c: _F(c) + ' W')
        return mc(body, '%s W' % _F(Pavg), ws, r=r, lv='상', fam='e', sort='num',
                  steps=['가속도 a = F/m = %d ÷ %d = %s m/s², 이동 거리 s = ½at² = %s m' % (F, m, _F(a), _F(s)), '한 일 W = Fs = %d × %s = %s J (= 운동 에너지 ½mv² = %s J)' % (F, _F(s), _F(W), _F(Fr(1, 2) * m * vt * vt)), '평균 일률 = W/t = %s ÷ %d = %s W' % (_F(W), t, _F(Pavg))],
                  core='평균 일률 = (한 일)/(걸린 시간), W = Fs = ΔE_k.', point='가속도로 이동 거리를 구한 뒤 일을 구한다.')
    body = P(base + '%d초가 되는 순간 힘이 물체에 하는 일의 순간 일률(P = Fv)은?' % t)
    ws = _ws(Pins, [Pavg, W, F * t, Pins * 2, Pins / 4], lambda c: _F(c) + ' W')
    return mc(body, '%s W' % _F(Pins), ws, r=r, lv='상', fam='e', sort='num',
              steps=['a = F/m = %s m/s²이므로 %d초 후 속력 v = at = %s m/s' % (_F(a), t, _F(vt)), '순간 일률 P = Fv = %d × %s = %s W' % (F, _F(vt), _F(Pins)), '(평균 일률은 %s W로 순간 일률의 절반이다.)' % _F(Pavg)],
              core='순간 일률 P = Fv (그 순간의 속력을 곱한다).', point='등가속도 운동에서 순간 일률은 평균 일률의 2배(정지에서 출발)이다.')


# ================================================================== ph056 에너지 그래프 해석(<보기>)
def _eg_fig(m, H, mode, assign, lam=None, w=320, h=230):
    """높이-에너지 그래프. assign: 곡선 이름 -> 'Ep'/'Ek'/'E'. mode: 'cons' 또는 'fric'."""
    E0 = m * G * H
    pl = Plot(w, h, H * 1.12, E0 * 1.22, ml=52, mb=34)
    xt = list(range(0, H + 1, max(1, H // 5)))
    if xt[-1] != H: xt.append(H)
    yt = [0, E0 // 2, E0] if E0 % 2 == 0 else [0, E0]
    pl.axes('높이 h (m)', '에너지 (J)', xticks=xt, yticks=yt, grid=True)
    curves = {}
    curves['Ep'] = [(0, 0), (H, m * G * H)]
    if mode == 'cons':
        curves['Ek'] = [(0, E0), (H, 0)]
        curves['E'] = [(0, E0), (H, E0)]
    else:
        Ek0 = (1 - lam) * E0
        curves['Ek'] = [(0, Ek0), (H, 0)]
        curves['E'] = [(0, Ek0), (H, E0)]
    cols = {'Ep': RD, 'Ek': BL, 'E': GN}
    pos = {'A': 0.28, 'B': 0.62, 'C': 0.18}
    for nm_, kind in assign.items():
        pts = curves[kind]
        pl.pl(pts, cols[kind], 2.6, None if kind != 'E' else None)
    for nm_, kind in assign.items():
        pts = curves[kind]
        fx = {'Ep': 0.82, 'Ek': 0.2, 'E': 0.55}[kind]
        x = H * fx
        (x1, y1), (x2, y2) = pts
        y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        off = {'Ep': (6, 14), 'Ek': (8, -8), 'E': (0, -8)}[kind]
        pl.text(pl.px(x) + off[0], pl.py(y) + off[1], nm_, 15, 'middle', True, cols[kind], True)
    return pl.svg()


_EBANK = [
    ('마찰이 없을 때 낙하하는 물체의 역학적 에너지는 일정하다.', True, '중력만 작용하면 운동 에너지와 위치 에너지의 합이 보존된다.', 'c1'),
    ('낙하하는 물체의 운동 에너지가 증가하는 만큼 위치 에너지가 증가한다.', False, '운동 에너지가 증가하는 만큼 위치 에너지는 감소한다.', 'c2'),
    ('연직 위로 던진 물체가 올라가는 동안 운동 에너지는 감소하고 위치 에너지는 증가한다.', True, '속력이 줄어 운동 에너지가 감소하고 높아져 위치 에너지가 증가한다.', 'c3'),
    ('연직 위로 던진 물체가 최고점에 도달했을 때 운동 에너지는 최대이다.', False, '최고점에서는 속력이 0이어서 운동 에너지가 0이다.', 'c3'),
    ('마찰이 있는 빗면을 미끄러져 내려오는 물체의 역학적 에너지는 줄어든다.', True, '마찰력이 한 일만큼 열로 전환되어 역학적 에너지가 감소한다.', 'c4'),
    ('마찰이 있는 빗면을 내려올 때에도 역학적 에너지는 보존된다.', False, '비보존력인 마찰력이 일을 하므로 역학적 에너지가 감소한다.', 'c4'),
    ('에너지는 다른 형태로 전환될 뿐 전체 에너지의 총량은 일정하게 보존된다.', True, '에너지 보존 법칙이다.', 'c5'),
    ('마찰로 줄어든 역학적 에너지는 사라진다.', False, '열에너지 등 다른 형태로 전환될 뿐 사라지지 않는다.', 'c5'),
    ('같은 높이에서 가만히 놓은 질량이 다른 두 물체는 마찰이 없다면 바닥에 닿는 순간의 속력이 같다.', True, 'v = √(2gh)로 질량과 무관하다.', 'c6'),
    ('같은 높이에서 가만히 놓은 질량이 다른 두 물체는 바닥에 닿는 순간의 운동 에너지가 같다.', False, '운동 에너지는 mgh이므로 질량이 큰 물체가 더 크다.', 'c6'),
    ('물체의 중력 위치 에너지는 기준면을 어디로 잡느냐에 따라 달라진다.', True, 'E_p = mgh 에서 h는 기준면으로부터 잰 높이이다.', 'c7'),
    ('진자가 최저점을 지날 때 운동 에너지가 최대이다.', True, '가장 낮아 위치 에너지가 최소이므로 운동 에너지가 최대이다(마찰 무시).', 'c8'),
    ('진자가 최고점(양 끝)에 있을 때 운동 에너지는 최대이다.', False, '최고점에서는 속력이 0이므로 운동 에너지가 0이고 위치 에너지가 최대이다.', 'c8'),
    ('용수철 진동에서 용수철이 가장 많이 압축된 순간 탄성 위치 에너지가 최대이다.', True, 'E = ½kx² 이므로 변형이 최대일 때 최대이다.', 'c9'),
    ('용수철이 원래 길이를 지날 때 탄성 위치 에너지는 최대이다.', False, '원래 길이에서 변형이 0이므로 탄성 위치 에너지는 0이다.', 'c9'),
    ('롤러코스터가 가장 높은 곳에서 가장 낮은 곳으로 내려오면 위치 에너지가 운동 에너지로 전환된다.', True, '높이가 낮아지며 속력이 커진다.', 'c10'),
    ('물체를 일정한 속력으로 끌어올리면 물체의 역학적 에너지는 감소한다.', False, '운동 에너지는 일정하고 위치 에너지는 증가하므로 역학적 에너지는 증가한다.', 'c11'),
    ('물체가 같은 높이만큼 내려오면 경로가 달라도 중력이 한 일은 같다.', True, '중력이 한 일은 높이 변화만으로 결정된다(보존력).', 'c12'),
    ('마찰이 없는 빗면에서 경사각이 클수록 바닥에서의 속력이 크다.', False, '같은 높이이면 경사각과 무관하게 바닥 속력은 같다.', 'c13'),
    ('운동 에너지와 위치 에너지의 합이 일정하면 운동 에너지가 증가할 때 위치 에너지는 감소한다.', True, 'E_k + E_p = 일정 이므로 한쪽이 늘면 다른 쪽은 줄어든다.', 'c2'),
]


@T('ph056')
def energy_graph(r, k):
    fam = r.choice(['a', 'b', 'b', 'c', 'c'])
    if fam == 'a':
        for _ in range(100):
            s = r.sample(_EBANK, 3)
            if len({x[3] for x in s}) < 3: continue
            t = [x[1] for x in s]
            if not any(t): continue
            break
        else:
            return None
        return bogi('역학적 에너지에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', [(x[0], x[1], x[2]) for x in s], r=r, ask='', lv=r.choice(['하', '중']), fam='a',
                    core='마찰이 없으면 역학적 에너지는 보존되고, 마찰이 있으면 줄어든 만큼 열에너지로 전환된다.', point='에너지 전환과 보존 조건을 구분한다.')
    mode = 'cons' if fam == 'b' else 'fric'
    for _ in range(300):
        m = r.choice([1, 2, 3, 4, 5])
        H = r.choice([2, 4, 5, 6, 8, 10])
        lam = r.choice([Fr(1, 5), Fr(1, 4), Fr(2, 5), Fr(1, 2)]) if mode == 'fric' else None
        E0 = m * G * H
        if mode == 'fric' and not _ok(lam * E0): continue
        break
    names = r.sample(['A', 'B', 'C'], 3)
    kinds = ['Ep', 'Ek', 'E']
    r.shuffle(kinds)
    assign = dict(zip(names, kinds))
    nm = {kd: n for n, kd in assign.items()}
    kor = {'Ep': '중력 위치 에너지', 'Ek': '운동 에너지', 'E': '역학적 에너지'}
    fig = FIG(_eg_fig(m, H, mode, assign, lam), '66%')
    hs = [x for x in range(1, H) if x % 1 == 0]
    hq = r.choice(hs)
    Ep_q = m * G * hq
    if mode == 'cons':
        Ek_q = E0 - Ep_q
        Etot = E0
        loss = 0
    else:
        Ek_q = (1 - lam) * E0 * Fr(H - hq, H) if False else None
        # E(h) = E0 - lam*m*g*(H-h)*... : 역학적 에너지는 h 에 대해 선형 (H 에서 E0, 0 에서 (1-lam)E0)
        Etot_q = (1 - lam) * E0 + lam * E0 * Fr(hq, H)
        Ek_q = Etot_q - Ep_q
        loss = lam * E0
    wrongE = lambda x: x + r.choice([10, 20, -10, 5]) if x > 15 else x + 10
    cand = []
    # 1) 곡선 이름 맞추기
    for kd in ('Ep', 'Ek', 'E'):
        n1 = nm[kd]
        wrong = r.choice([x for x in ('Ep', 'Ek', 'E') if x != kd])
        if r.random() < .5: cand.append(('곡선 %s는 %s를 나타낸다.' % (n1, kor[kd]), True, '그래프에서 %s' % {'Ep': '높이에 비례해 증가하는 직선이므로 중력 위치 에너지이다.', 'Ek': '높이가 낮을수록 커지는 직선이므로 운동 에너지이다.', 'E': ('높이와 무관하게 일정한 수평선이므로 역학적 에너지이다.' if mode == 'cons' else '운동 에너지와 위치 에너지의 합으로 높이가 낮아질수록 감소하므로 역학적 에너지이다.')}[kd], 'n%s' % kd))
        else: cand.append(('곡선 %s는 %s를 나타낸다.' % (n1, kor[wrong]), False, '곡선 %s는 %s이다.' % (n1, kor[kd]), 'n%s' % kd))
    # 2) 수치
    right_v = Ek_q
    wr_v = Ek_q + r.choice([10, 20, -10, 15]) * (1 if Ek_q > 15 else 1)
    cand.append(('높이 %d m인 지점에서 운동 에너지는 %s J이다.' % (hq, _F(Ek_q)), True, '운동 에너지 = 역학적 에너지 - 위치 에너지 = %s - %s = %s J이다.' % (_F(Etot if mode == 'cons' else Etot_q), _F(Ep_q), _F(Ek_q)), 'val'))
    cand.append(('높이 %d m인 지점에서 운동 에너지는 %s J이다.' % (hq, _F(wr_v)), False, '이 높이에서 운동 에너지는 %s J이다.' % _F(Ek_q), 'val'))
    # 3) 질량
    cand.append(('물체의 질량은 %d kg이다. (g = 10 m/s²)' % m, True, '높이 %d m에서 위치 에너지 %s J이므로 m = %s ÷ (10 × %d) = %d kg이다.' % (hq, _F(Ep_q), _F(Ep_q), hq, m), 'mass'))
    wm = m + r.choice([1, 2, -1]) if m > 1 else m + 2
    cand.append(('물체의 질량은 %d kg이다. (g = 10 m/s²)' % wm, False, '위치 에너지 mgh로 구하면 질량은 %d kg이다.' % m, 'mass'))
    # 4) 보존/감소
    if mode == 'cons':
        cand.append(('물체가 내려오는 동안 역학적 에너지는 일정하다.', True, '역학적 에너지를 나타내는 그래프가 수평선이므로 일정하다.', 'cons'))
        cand.append(('물체가 내려오는 동안 마찰력이 한 일은 0이 아니다.', False, '역학적 에너지가 일정하므로 마찰력이 한 일은 0이다.', 'cons'))
        cand.append(('높이 %s m에서 운동 에너지와 위치 에너지는 같다.' % _F(Fr(H, 2)), True, 'H/2에서 E_p = E_k = %s J이다.' % _F(E0 // 2 if E0 % 2 == 0 else Fr(E0, 2)), 'half'))
        cand.append(('높이 %d m에서 운동 에너지가 위치 에너지의 %d배이다.' % (hq, 2), (E0 - Ep_q) == 2 * Ep_q, '실제 비는 E_k : E_p = %s : %s이다.' % (_F(E0 - Ep_q), _F(Ep_q)), 'ratio'))
        cand.append(('지면에 닿는 순간의 운동 에너지는 %s J이다.' % _F(E0), True, '지면(h = 0)에서 E_p = 0이므로 E_k = 역학적 에너지 = %s J이다.' % _F(E0), 'ground'))
        cand.append(('지면에 닿는 순간의 운동 에너지는 %s J이다.' % _F(E0 + 20), False, '지면에서 운동 에너지는 처음 위치 에너지 %s J와 같다.' % _F(E0), 'ground'))
    else:
        cand.append(('물체가 내려오는 동안 역학적 에너지는 일정하다.', False, '역학적 에너지를 나타내는 그래프가 높이가 낮아질수록 감소하므로 마찰에 의해 줄어든다.', 'cons'))
        cand.append(('물체가 내려오는 동안 역학적 에너지는 감소한다.', True, '마찰력이 한 일만큼 열로 전환되어 감소한다.', 'cons'))
        cand.append(('지면에 닿는 순간의 운동 에너지는 %s J이다.' % _F((1 - lam) * E0), True, '지면에서 E_p = 0이므로 운동 에너지 = 역학적 에너지 = %s J이다(그래프 h = 0).' % _F((1 - lam) * E0), 'ground'))
        cand.append(('지면에 닿는 순간의 운동 에너지는 %s J이다.' % _F(E0), False, '마찰 때문에 처음 위치 에너지 %s J보다 작은 %s J이다.' % (_F(E0), _F((1 - lam) * E0)), 'ground'))
        cand.append(('높이 %d m에서 지면까지 내려오는 동안 감소한 역학적 에너지는 %s J이다.' % (H, _F(lam * E0)), True, '처음 %s J에서 지면에서 %s J로 줄었으므로 %s J 감소했다.' % (_F(E0), _F((1 - lam) * E0), _F(lam * E0)), 'loss'))
        cand.append(('높이 %d m에서 지면까지 내려오는 동안 감소한 역학적 에너지는 %s J이다.' % (H, _F(lam * E0 + 10)), False, '감소한 양은 %s J이다.' % _F(lam * E0), 'loss'))
        cand.append(('물체가 내려오는 동안 감소한 역학적 에너지는 열에너지 등으로 전환된다.', True, '에너지는 사라지지 않고 열 등으로 전환된다.', 'heat'))
        cand.append(('물체가 내려오는 동안 중력 위치 에너지의 감소량은 운동 에너지의 증가량과 같다.', False, '일부가 마찰열이 되므로 운동 에너지 증가량은 위치 에너지 감소량보다 작다.', 'dv'))
    for _ in range(100):
        s = r.sample(cand, 3)
        if len({x[3] for x in s}) < 3: continue
        t = [x[1] for x in s]
        if not any(t): continue
        break
    else:
        return None
    intro = ('그림은 마찰이 없는 빗면 위에서 질량 m인 물체를 높이 %d m에서 가만히 놓았을 때, 물체의 높이에 따른 중력 위치 에너지, 운동 에너지, 역학적 에너지를 A, B, C로 나타낸 것이다.' % H if mode == 'cons'
             else '그림은 마찰이 있는 빗면 위에서 질량 m인 물체를 높이 %d m에서 가만히 놓았을 때, 물체의 높이에 따른 중력 위치 에너지, 운동 에너지, 역학적 에너지를 A, B, C로 나타낸 것이다(물체는 높이가 낮아지는 방향, 즉 그래프의 오른쪽에서 왼쪽으로 진행한다).' % H)
    intro += ' 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, g = 10 m/s²이고 공기 저항은 무시한다.)'
    return bogi(intro, [(x[0], x[1], x[2]) for x in s], pre=fig, r=r, ask='', lv='중' if mode == 'cons' else '상', fam=fam,
                core='높이-에너지 그래프에서 E_p는 높이에 비례하고, E_k = E - E_p 이며 마찰이 없으면 E가 일정하다.', point='그래프의 값을 읽어 에너지 관계를 판단한다.')
