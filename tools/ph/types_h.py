# -*- coding: utf-8 -*-
"""Ⅰ-H 운동량과 충격량 (ph057~ph064)."""
from phlib import *
import math
from fractions import Fraction as Fr

G = 10


# ------------------------------------------------------------------ 공통 도구
def _F(x, nd=2):
    if isinstance(x, Fr): x = float(x)
    return num(x, nd)


def _fx(x):
    x = Fr(x).limit_denominator(10000)
    return str(x.numerator) if x.denominator == 1 else '%d/%d' % (x.numerator, x.denominator)


def _ws(right, cands, fmt=None, pos=True):
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
    x = Fr(x)
    if x.denominator != 1 or x < 0: return None
    q = math.isqrt(int(x))
    return q if q * q == x else None


def _ok(x, dens=(1, 2, 4, 5, 10, 20, 25, 100)):
    return Fr(x).denominator in dens


def _vel(v):
    """속도(부호: 오른쪽 +) 문장."""
    v = Fr(v)
    if v == 0: return '정지'
    return ('오른쪽으로 ' if v > 0 else '왼쪽으로 ') + _F(abs(v)) + ' m/s'


def _velw(v):
    return _vel(v)


def _vel_ws(right, cands):
    """속도 선택지(방향 포함) 오답 목록."""
    seen = {_vel(right)}
    out = []
    ex = [-right, right * 2, right / 2, right + 1, right - 1, right * 3, right + 2, -right * 2, right / 3]
    for c in list(cands) + ex:
        c = Fr(c).limit_denominator(1000)
        dd = c.denominator
        while dd % 2 == 0: dd //= 2
        while dd % 5 == 0: dd //= 5
        if dd != 1: continue
        s = _vel(c)
        if s in seen: continue
        seen.add(s); out.append(s)
    return out[:5]


# ------------------------------------------------------------------ 수레 그림
def _cart(f, cx, yb, m, name, v, w=60, h=28, col='#cfe2f7', vlabel=None, vscale=7):
    f.rect(cx - w / 2, yb - h - 6, w, h, col, INK, 1.6)
    f.circ(cx - w / 3, yb - 3, 4.5, '#fff', INK, 1.3); f.circ(cx + w / 3, yb - 3, 4.5, '#fff', INK, 1.3)
    f.text(cx, yb - h / 2 - 2, '%s %s kg' % (name, _F(m)) if m is not None else name, 12, 'middle', True, INK)
    ya = yb - h - 20
    if v is None or v in ('L?', 'R?'):
        sg = -1 if v == 'L?' else 1
        f.arrow(cx, ya, cx + sg * 36, ya, RD, 2.2)
        f.text(cx + sg * 18, ya - 6, 'v = ?', 12.5, 'middle', True, RD)
        return
    v = Fr(v)
    if v == 0:
        f.text(cx, ya, '정지', 12.5, 'middle', True, GR)
        return
    L = min(70, 14 + abs(float(v)) * vscale)
    sgn = 1 if v > 0 else -1
    f.arrow(cx, ya, cx + sgn * L, ya, RD, 2.2)
    f.text(cx + sgn * L / 2, ya - 6, vlabel or '%s m/s' % _F(abs(v)), 12.5, 'middle', True, RD)


def _cart_fig(before, after, merged=False, w=330, h=215, spring=False, unk_after=()):
    """before/after: [(이름, 질량, 속도)] (속도 None 이면 ? 표시)."""
    f = Fig(w, h)
    f.text(10, 20, '충돌 전' if not spring else '분리 전', 13, 'start', True, GR)
    f.text(10, 128, '충돌 후' if not spring else '분리 후', 13, 'start', True, GR)
    for yb in (92, 200):
        f.line(14, yb, w - 14, yb, GR, 1.6)
    n = len(before)
    xs = [95, 235] if n == 2 else [165]
    for (nm_, m, v), x in zip(before, xs):
        _cart(f, x, 92, m, nm_, v, col='#cfe2f7' if nm_ != 'B' else '#fde3b0')
    if spring and n == 2:
        f.spring(125, 92 - 20, 205, coils=5, amp=5)
    if merged:
        f.rect(165 - 62, 200 - 34, 124, 28, '#e3d9f6', INK, 1.6)
        for dx in (-40, -10, 25, 52): f.circ(165 + dx, 197, 4.5, '#fff', INK, 1.3)
        f.text(165, 183, '%s + %s' % (before[0][0], before[1][0]), 12, 'middle', True, INK)
        v = after[0][2]
        ya = 200 - 54
        if v is None:
            f.arrow(165, ya, 205, ya, RD, 2.2); f.text(185, ya - 6, 'v = ?', 12.5, 'middle', True, RD)
        elif Fr(v) == 0:
            f.text(165, ya, '정지', 12.5, 'middle', True, GR)
        else:
            sg = 1 if Fr(v) > 0 else -1
            L = min(70, 14 + abs(float(v)) * 7)
            f.arrow(165, ya, 165 + sg * L, ya, RD, 2.2); f.text(165 + sg * L / 2, ya - 6, '%s m/s' % _F(abs(Fr(v))), 12.5, 'middle', True, RD)
    else:
        xs2 = [95, 235] if len(after) == 2 else [165]
        for (nm_, m, v), x in zip(after, xs2):
            _cart(f, x, 200, m, nm_, v, col='#cfe2f7' if nm_ != 'B' else '#fde3b0')
    return f.svg()


def _unit_note():
    return '(단, 오른쪽을 +방향으로 한다.)'


# ================================================================== ph057 운동량과 충격량의 계산
def _wall_fig(m, v1, v2, w=300, h=150):
    f = Fig(w, h)
    y0 = 118
    f.line(240, 20, 240, y0, INK, 4)
    for i in range(20, 118, 9): f.line(240, i + 9, 247, i, GR, 1)
    f.line(14, y0, 240, y0, GR, 1.5)
    f.text(10, 16, '충돌 전', 12.5, 'start', True, GR)
    f.circ(120, y0 - 12, 11, BL, INK, 1.4); f.text(120, y0 - 8, 'm', 11, 'middle', True, '#fff')
    f.arrow(138, y0 - 12, 200, y0 - 12, RD, 2.4)
    f.text(170, y0 - 22, '%s m/s' % _F(v1), 12.5, 'middle', True, RD)
    f.circ(70, y0 - 12, 11, '#cfe2f7', INK, 1.2, '3 2')
    f.arrow(100, y0 - 52, 40, y0 - 52, GN, 2.4) if v2 else None
    f.text(70, y0 - 62, ('충돌 후 %s m/s' % _F(v2)) if v2 else '충돌 후 정지', 12.5, 'middle', True, GN)
    f.text(14, 144, '질량 m = %s kg' % _F(m), 12.5, 'start', True, INK)
    return f.svg()


@T('ph057')
def momentum_impulse(r, k):
    fam = r.choice(['a', 'b', 'b', 'c', 'c', 'd', 'e', 'f'])
    if fam == 'a':
        m = r.choice([0.2, 0.5, 1, 2, 3, 4, 5, 10, 50, 1000])
        v = r.choice([2, 3, 4, 5, 6, 8, 10, 15, 20, 25])
        if m >= 50 and v > 10: return None
        p = Fr(m).limit_denominator(10) * v
        ask = r.choice(['p', 'p', 'v', 'm'])
        mm = Fr(m).limit_denominator(10)
        if ask == 'p':
            body = P('질량 %s kg인 물체가 %d m/s의 속력으로 운동하고 있다. 이 물체의 운동량의 크기는?' % (_F(m), v))
            ws = _ws(p, [mm * v * v / 2, mm * v * v, mm + v, mm * v * 2, mm / v if v else 1], lambda c: _F(c) + ' kg·m/s')
            return mc(body, '%s kg·m/s' % _F(p), ws, r=r, lv='하', fam='a', sort='num',
                      steps=['운동량 p = mv = %s × %d = %s kg·m/s' % (_F(m), v, _F(p))],
                      core='운동량 p = mv (단위 kg·m/s), 방향은 속도의 방향이다.', point='운동 에너지(½mv²)와 혼동하지 않는다.')
        if ask == 'v':
            body = P('질량 %s kg인 물체의 운동량의 크기가 %s kg·m/s이다. 이 물체의 속력은?' % (_F(m), _F(p)))
            ws = _ws(v, [p * mm, p / (mm * mm) if mm else 1, p, v * 2, math.sqrt(float(2 * p / mm)) if _isq(2 * p / mm) else v + 3], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v), ws, r=r, lv='하', fam='a', sort='num',
                      steps=['p = mv 이므로 v = p/m = %s ÷ %s = %d m/s' % (_F(p), _F(m), v)],
                      core='p = mv.', point='운동량을 질량으로 나누면 속력이다.')
        m2 = r.choice([1, 2, 3, 4, 6]); v2 = r.choice([2, 3, 4, 5, 6, 8])
        p2 = m2 * v2
        if p2 == p: return None
        right = '%s : %s' % (_fx(p / math.gcd(int(p * 10), int(p2 * 10)) * 10 if False else (p * 10) / math.gcd(int(p * 10), p2 * 10)), _fx(p2 * 10 / math.gcd(int(p * 10), p2 * 10)))
        a_, b_ = right.split(' : ')
        body = P('물체 A(질량 %s kg, 속력 %d m/s)와 물체 B(질량 %d kg, 속력 %d m/s)의 운동량의 크기의 비 p%s : p%s는?' % (_F(m), v, m2, v2, sub('A'), sub('B')))
        ek1, ek2 = mm * v * v / 2, m2 * v2 * v2 / 2
        def rs(x, y):
            x, y = Fr(x), Fr(y)
            g = math.gcd(x.numerator * y.denominator, y.numerator * x.denominator)
            return '%d : %d' % (x.numerator * y.denominator // g, y.numerator * x.denominator // g)
        right = rs(p, p2)
        wr = [rs(p2, p), rs(ek1, ek2), rs(mm, m2), rs(v, v2), rs(ek2, ek1)]
        wr = [c for c in dict.fromkeys(wr) if c != right]
        return mc(body, right, wr[:5], r=r, lv='하', fam='a', sort='shuf',
                  steps=['p%s = %s × %d = %s kg·m/s, p%s = %d × %d = %d kg·m/s' % (sub('A'), _F(m), v, _F(p), sub('B'), m2, v2, p2), '비 = %s : %d = %s' % (_F(p), p2, right)],
                  core='운동량 p = mv.', point='질량과 속력의 곱으로 비교한다.')
    if fam == 'b':
        m = r.choice([0.1, 0.2, 0.5, 1, 2, 0.4, 0.15])
        mm = Fr(m).limit_denominator(100)
        v1 = r.choice([4, 5, 6, 8, 10, 12, 15, 20, 30])
        v2 = r.choice([0, 2, 4, 5, 6, 8, 10, 12, 20])
        dt = r.choice([Fr(1, 100), Fr(1, 50), Fr(1, 20), Fr(1, 10), Fr(1, 5), Fr(1, 25)])
        dp = mm * (v1 + v2)
        Fav = dp / dt
        if not (_ok(dp) and _ok(Fav)): return None
        # 검증 : 오른쪽 + 로 입사 v1 (벽쪽), 반사 -v2
        p_i, p_f = mm * v1, -mm * v2
        assert p_i - p_f == dp
        fig = FIG(_wall_fig(m, v1, v2), '58%')
        ask = r.choice(['I', 'F', 'F'])
        mot = '튕겨 나왔다' if v2 else '정지하였다'
        base = '그림과 같이 질량 %s kg인 공이 %d m/s의 속력으로 벽에 수직으로 충돌한 후 %s. ' % (_F(m), v1, ('%d m/s의 속력으로 튕겨 나왔다' % v2) if v2 else '정지하였다')
        if ask == 'I':
            body = P(base + '충돌하는 동안 벽이 공에 가한 충격량의 크기는?') + fig
            ws = _ws(dp, [mm * abs(v1 - v2), mm * v1, mm * v2 if v2 else dp * 2, dp * 2, Fr(1, 2) * mm * (v1 * v1 - v2 * v2) if v2 != v1 else dp + 1], lambda c: _F(c) + ' N·s')
            return mc(body, '%s N·s' % _F(dp), ws, r=r, lv='중' if v2 else '하', fam='b', sort='num',
                      steps=['오른쪽을 +로 하면 처음 운동량 p%s = %s × %d = %s kg·m/s' % (sub('i'), _F(m), v1, _F(p_i)), '나중 운동량 p%s = %s × (-%d) = %s kg·m/s' % (sub('f'), _F(m), v2, _F(p_f)),
                             '충격량 = 운동량의 변화량 = p%s - p%s = %s N·s (크기)' % (sub('f'), sub('i'), _F(dp))],
                      core='충격량 I = Δp = mv₂ - mv₁ (방향을 고려한 운동량의 변화량).', point='튕겨 나오면 운동량의 방향이 바뀌므로 크기를 더한다.')
        body = P(base + '공과 벽이 접촉한 시간이 %s초일 때, 벽이 공에 가한 평균 힘의 크기는?' % _F(dt)) + fig
        ws = _ws(Fav, [mm * abs(v1 - v2) / dt, mm * v1 / dt, dp * dt, dp, Fav * 2], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(Fav), ws, r=r, lv='상' if v2 else '중', fam='b', sort='num',
                  steps=['운동량의 변화량 Δp = %s × (%d + %d) = %s kg·m/s' % (_F(m), v1, v2, _F(dp)), '충격량 I = F̄Δt = Δp 이므로 F̄ = %s ÷ %s = %s N' % (_F(dp), _F(dt), _F(Fav))],
                  core='평균 힘 F̄ = Δp/Δt (충격량 = 평균 힘 × 시간).', point='방향이 반대로 바뀌면 Δp = m(v₁ + v₂).')
    if fam == 'c':
        for _ in range(300):
            m = r.choice([0.5, 1, 2, 3, 4, 5, 10])
            mm = Fr(m).limit_denominator(10)
            F = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 20])
            dt = r.choice([1, 2, 3, 4, 5, 6, 8, 10])
            v0 = r.choice([0, 0, 2, 4, 5, 6])
            I = F * dt
            dv = Fr(I) / mm
            if _ok(dv): break
        v = v0 + dv
        # 운동학 검증
        a = Fr(F) / mm
        assert v0 + a * dt == v
        ask = r.choice(['v', 'v', 'F', 'I'])
        base = '마찰이 없는 수평면에서 %s질량 %s kg인 물체에 운동 방향으로 일정한 힘을 작용했다. ' % ('정지해 있던 ' if v0 == 0 else '%d m/s로 운동하던 ' % v0, _F(m))
        if ask == 'I':
            body = P(base + '힘의 크기가 %d N이고 %d초 동안 작용했을 때, 물체가 받은 충격량의 크기는?' % (F, dt))
            ws = _ws(I, [F / dt if dt else 1, F + dt, I * 2, I / mm, Fr(1, 2) * F * dt * dt], lambda c: _F(c) + ' N·s')
            return mc(body, '%s N·s' % _F(I), ws, r=r, lv='하', fam='c', sort='num',
                      steps=['충격량 I = FΔt = %d × %d = %d N·s' % (F, dt, I)],
                      core='충격량 I = FΔt (힘이 일정할 때).', point='힘과 시간의 곱이다.')
        if ask == 'v':
            body = P(base + '힘의 크기가 %d N이고 %d초 동안 작용했을 때, 힘이 작용한 직후 물체의 속력은?' % (F, dt))
            ws = _ws(v, [dv, I, v0 + I, v0 + I * mm if mm != 1 else v + 2, v0 + Fr(F, 1) * 0 + F / mm], lambda c: _F(c) + ' m/s')
            return mc(body, '%s m/s' % _F(v), ws, r=r, lv='중', fam='c', sort='num',
                      steps=['충격량 I = FΔt = %d × %d = %d N·s' % (F, dt, I), 'I = Δp = m(v - v₀) 이므로 %d = %s × (v - %d)' % (I, _F(m), v0), 'v = %s m/s (확인: a = F/m = %s m/s², v = v₀ + at = %s)' % (_F(v), _F(a), _F(v))],
                      core='I = FΔt = Δp = mΔv.', point='충격량은 운동량의 변화량과 같다.')
        body = P(base + '이 힘이 %d초 동안 작용하여 물체의 속력이 %s m/s가 되었다. 힘의 크기는?' % (dt, _F(v)))
        ws = _ws(F, [Fr(F * dt), Fr(F, dt), F + 2, Fr(1, 2) * mm * v * v / dt if False else mm * v, F * 2], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(F), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['운동량의 변화량 Δp = %s × (%s - %d) = %s kg·m/s' % (_F(m), _F(v), v0, _F(I)), 'F = Δp/Δt = %s ÷ %d = %d N' % (_F(I), dt, F)],
                  core='F = Δp/Δt.', point='운동량 변화를 시간으로 나눈다.')
    if fam == 'd':
        ask = r.choice(['p', 'k'])
        m1, m2 = r.choice([(1, 4), (4, 1), (1, 9), (9, 1), (1, 2), (2, 1), (1, 3), (3, 1), (4, 9), (9, 4), (2, 3), (3, 2)])
        if ask == 'p':
            # 운동 에너지가 같을 때 운동량 비 : p = sqrt(2mEk) ∝ sqrt(m)
            s1, s2 = math.isqrt(m1), math.isqrt(m2)
            if s1 * s1 != m1 or s2 * s2 != m2: return None
            g = math.gcd(s1, s2)
            right = '%d : %d' % (s1 // g, s2 // g)
            body = P('질량이 각각 %d kg, %d kg인 물체 A, B의 운동 에너지가 같다. A, B의 운동량의 크기의 비 p%s : p%s는?' % (m1, m2, sub('A'), sub('B')))
            wr = ['%d : %d' % (s2 // g, s1 // g), '%d : %d' % (m1 // math.gcd(m1, m2), m2 // math.gcd(m1, m2)), '%d : %d' % (m2 // math.gcd(m1, m2), m1 // math.gcd(m1, m2)), '1 : 1', '%d : %d' % (s1 // g * 2, s2 // g)]
            wr = [c for c in dict.fromkeys(wr) if c != right]
            return mc(body, right, wr[:5], r=r, lv='상', fam='d', sort='shuf',
                      steps=['운동 에너지 E_k = p²/2m 이므로 p = √(2mE_k)이다.', 'E_k가 같으면 p ∝ √m 이므로 p%s : p%s = √%d : √%d = %s' % (sub('A'), sub('B'), m1, m2, right)],
                      core='E_k = p²/(2m) 이므로 운동량이 같으면 E_k는 질량에 반비례, E_k가 같으면 p는 √m에 비례한다.', point='운동량과 운동 에너지의 관계식을 이용한다.')
        g = math.gcd(m2, m1)
        right = '%d : %d' % (m2 // g, m1 // g)
        body = P('질량이 각각 %d kg, %d kg인 물체 A, B의 운동량의 크기가 같다. A, B의 운동 에너지의 비 E_k(A) : E_k(B)는?' % (m1, m2))
        wr = ['%d : %d' % (m1 // g, m2 // g), '1 : 1', '%d : %d' % (m2 * m2 // math.gcd(m1 * m1, m2 * m2), m1 * m1 // math.gcd(m1 * m1, m2 * m2)), '%d : %d' % (m1 * m1 // math.gcd(m1 * m1, m2 * m2), m2 * m2 // math.gcd(m1 * m1, m2 * m2))]
        wr += ['%d : %d' % (m1 + 1, m2 + 1)]
        wr = [c for c in dict.fromkeys(wr) if c != right]
        return mc(body, right, wr[:5], r=r, lv='상', fam='d', sort='shuf',
                  steps=['E_k = p²/2m 이고 p가 같으므로 E_k ∝ 1/m 이다.', 'E_k(A) : E_k(B) = 1/%d : 1/%d = %d : %d = %s' % (m1, m2, m2, m1, right)],
                  core='E_k = p²/(2m).', point='운동량이 같으면 질량이 작은 쪽의 운동 에너지가 크다.')
    if fam == 'e':
        for _ in range(100):
            mA, mB = r.randint(1, 6), r.randint(1, 6)
            vA, vB = r.randint(1, 8), r.randint(1, 8)
            P_ = mA * vA - mB * vB
            if P_ != 0 or r.random() < .1: break
        P_ = mA * vA - mB * vB
        right = ('오른쪽으로 %d kg·m/s' % P_) if P_ > 0 else ('왼쪽으로 %d kg·m/s' % -P_) if P_ < 0 else '0'
        body = P('한 직선 위에서 물체 A(질량 %d kg)는 오른쪽으로 %d m/s로, 물체 B(질량 %d kg)는 왼쪽으로 %d m/s로 운동하고 있다. 두 물체 전체(A+B)의 운동량은?' % (mA, vA, mB, vB))
        cs = [mA * vA + mB * vB, mA * vA, mB * vB, P_ * 2, -P_]
        def f_(x):
            return ('오른쪽으로 %d kg·m/s' % x) if x > 0 else ('왼쪽으로 %d kg·m/s' % -x) if x < 0 else '0'
        wr = []
        for c in cs + [P_ + 3, P_ - 3, P_ + 7]:
            s_ = f_(c)
            if s_ != right and s_ not in wr: wr.append(s_)
        return mc(body, right, wr[:5], r=r, lv='중', fam='e', sort='shuf',
                  steps=['오른쪽을 +로 하면 p = %d × %d + %d × (-%d) = %d kg·m/s' % (mA, vA, mB, vB, P_), '운동량은 벡터이므로 반대 방향은 부호가 반대이다.' + ('' if P_ else ' (합이 0이다.)')],
                  core='운동량은 벡터량이므로 방향을 고려하여 합한다.', point='반대 방향의 운동량은 서로 빼 준다.')
    # f: 수직인 두 방향
    a_, b_, c_ = r.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 6, 10), (12, 5, 13), (4, 3, 5)])
    k_ = r.choice([1, 2])
    m = r.choice([1, 2, 3, 4, 5])
    body = P('질량 %d kg인 물체가 수평면에서 동쪽으로 운동하다가 어떤 힘을 받아 북쪽으로 운동하게 되었다. 처음 운동량의 크기는 %d kg·m/s, 나중 운동량의 크기는 %d kg·m/s로 크기가 달라졌다. 운동량의 변화량의 크기는?' % (m, a_ * k_ * 1, b_ * k_))
    ws = _ws(c_ * k_, [(a_ + b_) * k_, abs(a_ - b_) * k_, (c_ + 1) * k_, c_ * k_ * 2, a_ * k_ * b_ // math.gcd(a_, b_)], lambda c: _F(c) + ' kg·m/s')
    return mc(body, '%d kg·m/s' % (c_ * k_), ws, r=r, lv='중', fam='f', sort='num',
              steps=['운동량의 변화량 Δp = p₂ - p₁ (벡터 차)이다. 두 운동량이 서로 수직이므로 크기는 √(p₁² + p₂²)이다.', 'Δp = √(%d² + %d²) = %d kg·m/s' % (a_ * k_, b_ * k_, c_ * k_)],
              core='운동량의 변화량은 벡터 차이며, 수직인 두 벡터의 차의 크기는 피타고라스 정리로 구한다.', point='크기만 빼는 것이 아니라 벡터로 계산한다.')


# ================================================================== ph058 F-t 그래프와 충격량
def _ft_fig(pts, w=310, h=190, tunit='s', mark=None):
    tmax = max(p[0] for p in pts)
    fmax = max(p[1] for p in pts)
    fmin = min(0, min(p[1] for p in pts))
    pl = Plot(w, h, tmax * 1.15, fmax * 1.22, ymin=fmin * 1.35 if fmin < 0 else 0, ml=48, mb=30)
    xt = sorted({p[0] for p in pts if p[0] > 0})
    yt = sorted({p[1] for p in pts if p[1] != 0})
    pl.axes('t (%s)' % tunit, 'F (N)', xticks=xt, yticks=yt, grid=True)
    pl.fill_under(pts, '#cfe2f7') if min(p[1] for p in pts) >= 0 else None
    pl.pl(pts, BL, 2.6)
    return pl.svg()


def _area(pts):
    a = Fr(0)
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        a += Fr(x2 - x1) * (Fr(y1) + Fr(y2)) / 2
    return a


@T('ph058')
def ft_graph(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd'])
    shape = r.choice(['rect', 'tri', 'trap', 'ramp', 'neg', 'stair'])
    t1 = r.choice([1, 2, 3, 4]); t2 = t1 + r.choice([1, 2, 3]); t3 = t2 + r.choice([1, 2, 3])
    F1 = r.choice([2, 4, 5, 6, 8, 10, 12, 20]); F2 = r.choice([2, 4, 6, 10])
    if shape == 'rect': pts = [(0, 0), (0, F1), (t2, F1), (t2, 0)]
    elif shape == 'tri': pts = [(0, 0), (t1, F1), (t2, 0)] if t2 > t1 else None
    elif shape == 'trap': pts = [(0, 0), (t1, F1), (t2, F1), (t3, 0)]
    elif shape == 'ramp': pts = [(0, 0), (t2, F1)]
    elif shape == 'neg': pts = [(0, 0), (t1, F1), (t2, F1), (t2, -F2), (t3, -F2), (t3, 0)]
    else: pts = [(0, 0), (0, F1), (t1, F1), (t1, F2), (t2, F2), (t2, 0)]
    if pts is None: return None
    if shape == 'stair' and F1 == F2: return None
    I = _area(pts)
    if I <= 0: return None
    # 수치 적분 검증
    def Fat(x):
        best = None
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if x2 == x1: continue
            if x1 <= x <= x2: return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        return 0
    T_ = pts[-1][0]; N = 6000
    tot = sum(float(Fat((i + .5) * T_ / N)) * T_ / N for i in range(N))
    assert abs(tot - float(I)) < 0.05 + 1e-3 * float(I), (tot, I)
    fig = FIG(_ft_fig(pts), '62%')
    base = '그림은 직선 위에서 운동하는 물체에 작용하는 힘 F를 시간 t에 따라 나타낸 것이다(힘의 방향이 운동 방향일 때 +). '
    if fam == 'a':
        body = P(base + '0초부터 %d초까지 물체가 받은 충격량의 크기는?' % T_) + fig
        ws = _ws(I, [max(p[1] for p in pts) * T_, I / 2, I * 2, max(p[1] for p in pts), sum(abs(p[1]) for p in pts)], lambda c: _F(c) + ' N·s')
        steps = ['F-t 그래프 아래 넓이가 충격량이다.', '넓이를 도형으로 나누어 구하면 I = %s N·s' % _F(I)] + (['(F가 음(-)인 구간의 넓이는 빼 준다.)'] if shape == 'neg' else [])
        return mc(body, '%s N·s' % _F(I), ws, r=r, lv='하' if shape in ('rect', 'tri', 'ramp') else '중', fam='a', sort='num', steps=steps,
                  core='F-t 그래프 아래 넓이는 충격량(= 운동량 변화량)이다.', point='그래프의 모양을 삼각형·사각형으로 나누어 넓이를 구한다.')
    if fam == 'b':
        avg = I / T_
        if not _ok(avg): return None
        body = P(base + '0초부터 %d초까지 이 힘의 평균 크기(평균 힘)는?' % T_) + fig
        ws = _ws(avg, [max(p[1] for p in pts), I, avg * 2, avg / 2, Fr(max(p[1] for p in pts), 2)], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(avg), ws, r=r, lv='중', fam='b', sort='num',
                  steps=['충격량 = 그래프의 넓이 = %s N·s' % _F(I), '평균 힘 = 충격량 ÷ 시간 = %s ÷ %d = %s N' % (_F(I), T_, _F(avg))],
                  core='평균 힘 F̄ = I/Δt.', point='최대 힘이 아니라 넓이를 시간으로 나눈다.')
    if fam == 'c':
        for m in r.sample([1, 2, 3, 4, 5, 10], 6):
            v0 = r.choice([0, 0, 0, 2, 4])
            v = Fr(I, m) + v0
            if _ok(v) and v > 0: break
        else:
            return None
        start = '정지해 있던' if v0 == 0 else '%d m/s로 운동하던' % v0
        body = P(base + '%s 질량 %d kg인 물체에 이 힘이 작용했을 때, %d초일 때 물체의 속력은? (단, 다른 힘은 작용하지 않는다.)' % (start, m, T_)) + fig
        ws = _ws(v, [Fr(I), Fr(I, m), I / m + 2 if v0 == 0 else Fr(I, m), v0 + I, v * 2], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v), ws, r=r, lv='상' if v0 else '중', fam='c', sort='num',
                  steps=['그래프의 넓이 = 충격량 I = %s N·s' % _F(I), 'I = mv - mv₀ 이므로 %s = %d × v - %d × %d' % (_F(I), m, m, v0), 'v = %s m/s' % _F(v)],
                  core='충격량 = 운동량의 변화량 : I = mv - mv₀.', point='넓이로 충격량을 구하고 속도 변화를 구한다.')
    # d : 삼각형 최대 힘 / 접촉 시간
    tt = r.choice([2, 4, 5, 10, 20, 50]); Fm = r.choice([10, 20, 40, 50, 100, 200])
    I2 = Fr(1, 2) * Fm * tt
    pts2 = [(0, 0), (Fr(tt, 2), Fm), (tt, 0)]
    pts2f = [(float(a), float(b)) for a, b in pts2]
    unit = 'ms'
    if unit == 'ms': I2s = I2 / 1000
    else: I2s = I2
    fig2 = FIG(_ft_fig(pts2f, tunit=unit), '62%')
    if not _ok(I2s): return None
    body = P('그림은 공이 배트에 맞는 동안 공이 받은 힘의 크기를 시간에 따라 나타낸 것이다. 힘은 %d%s 동안 작용했으며 최대 %d N이었다. 공이 받은 충격량의 크기는?' % (tt, unit, Fm)) + fig2
    ws = _ws(I2s, [Fm * tt / (1000 if unit == 'ms' else 1), I2s * 1000 if unit == 'ms' else I2s * 2, I2s / 1000 if unit == 'ms' else I2s / 2, Fm, I2s * 2], lambda c: _F(c) + ' N·s')
    return mc(body, '%s N·s' % _F(I2s), ws, r=r, lv='하', fam='d', sort='num',
              steps=['삼각형 넓이 = ½ × %d N × %d %s%s' % (Fm, tt, unit, ' (= %s s)' % _F(Fr(tt, 1000)) if unit == 'ms' else ''), 'I = ½ × %d × %s = %s N·s' % (Fm, _F(Fr(tt, 1000)) if unit == 'ms' else tt, _F(I2s))],
              core='F-t 그래프 아래 넓이 = 충격량 (시간 단위를 초로 바꾼다).', point='ms를 s로 바꾸는 단위 환산에 유의한다.')


# ================================================================== ph059 합쳐지는 충돌
def _vt_merge_fig(v1, V, t0, w=300, h=190):
    pl = Plot(w, h, 6, float(v1) * 1.3, ml=46, mb=30)
    pl.axes('t (s)', 'v (m/s)', xticks=[0, t0, 6 if False else 5], yticks=[V, v1], grid=True)
    pl.pl([(0, float(v1)), (t0, float(v1)), (t0, float(V)), (5.5, float(V))], RD, 2.8)
    pl.pl([(0, 0), (t0, 0), (t0, float(V)), (5.5, float(V))], BL, 2.8, '6 3')
    pl.text(pl.px(0.6), pl.py(float(v1)) - 7, 'A', 14, 'middle', True, RD, True)
    pl.text(pl.px(0.6), pl.py(0) - 7, 'B', 14, 'middle', True, BL, True)
    return pl.svg()


@T('ph059')
def perfectly_inelastic(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'd', 'e'])
    if fam == 'a':
        for _ in range(300):
            m1, m2 = r.randint(1, 6), r.randint(1, 6)
            v1 = r.randint(2, 12)
            V = Fr(m1 * v1, m1 + m2)
            if _ok(V): break
        else:
            return None
        ask = r.choice(['V', 'V', 'V', 'v1', 'm2'])
        if ask == 'V':
            fig = FIG(_cart_fig([('A', m1, v1), ('B', m2, 0)], [('A+B', None, None)], merged=True), '62%')
            fig = FIG(_cart_fig([('A', m1, v1), ('B', m2, 0)], [('AB', m1 + m2, None)], merged=True), '62%')
            body = P('그림과 같이 마찰이 없는 수평면에서 질량 %d kg인 수레 A가 %d m/s의 속력으로 운동하여 정지해 있던 질량 %d kg인 수레 B와 충돌한 뒤 한 덩어리가 되어 운동하였다. 충돌 후 속력 v는?' % (m1, v1, m2)) + fig
            ws = _ws(V, [Fr(v1, 2), v1, Fr(m1 * v1, m2), Fr(m2 * v1, m1 + m2), Fr(v1 * (m1 + m2), m1)], lambda c: _F(c) + ' m/s')
            assert m1 * v1 == (m1 + m2) * V
            return mc(body, '%s m/s' % _F(V), ws, r=r, lv='하', fam='a', sort='num',
                      steps=['충돌 전후 운동량 보존 : m₁v₁ = (m₁ + m₂)V', '%d × %d = (%d + %d) × V 이므로 V = %d ÷ %d = %s m/s' % (m1, v1, m1, m2, m1 * v1, m1 + m2, _F(V))],
                      core='합쳐지는 충돌(완전 비탄성 충돌)에서도 운동량은 보존된다.', point='충돌 후 질량은 두 물체의 합이다.')
        if ask == 'v1':
            body = P('마찰이 없는 수평면에서 질량 %d kg인 물체 A가 일정한 속력 v로 운동하여 정지해 있던 질량 %d kg인 물체 B와 충돌한 뒤 한 덩어리가 되어 %s m/s로 운동하였다. 충돌 전 A의 속력 v는?' % (m1, m2, _F(V)))
            ws = _ws(v1, [V, V * m2 / m1, V * (m1 + m2), V * 2, V * m1 / (m1 + m2)], lambda c: _F(c) + ' m/s')
            return mc(body, '%d m/s' % v1, ws, r=r, lv='중', fam='a', sort='num',
                      steps=['운동량 보존 : %d × v = (%d + %d) × %s' % (m1, m1, m2, _F(V)), 'v = %s ÷ %d = %d m/s' % (_F((m1 + m2) * V), m1, v1)],
                      core='운동량 보존 : m₁v₁ = (m₁ + m₂)V.', point='충돌 후의 총 질량을 사용한다.')
        body = P('마찰이 없는 수평면에서 질량 %d kg인 물체 A가 %d m/s의 속력으로 운동하여 정지해 있던 물체 B와 충돌한 뒤 한 덩어리가 되어 %s m/s로 운동하였다. B의 질량은?' % (m1, v1, _F(V)))
        ws = _ws(m2, [m1, m1 * V, (m1 + m2), m2 * 2, Fr(m1 * V, v1)], lambda c: _F(c) + ' kg')
        return mc(body, '%d kg' % m2, ws, r=r, lv='중', fam='a', sort='num',
                  steps=['운동량 보존 : %d × %d = (%d + m) × %s' % (m1, v1, m1, _F(V)), '%d + m = %s 이므로 m = %d kg' % (m1, _F(m1 * v1 / V), m2)],
                  core='운동량 보존 : m₁v₁ = (m₁ + m₂)V.', point='전체 질량에서 A의 질량을 뺀다.')
    if fam == 'b':
        for _ in range(500):
            m1, m2 = r.randint(1, 6), r.randint(1, 6)
            v1, v2 = r.randint(1, 10), r.randint(1, 10)   # 마주 보고 운동 : A는 +, B는 -
            V = Fr(m1 * v1 - m2 * v2, m1 + m2)
            if _ok(V) and (V != 0 or r.random() < .1): break
        else:
            return None
        fig = FIG(_cart_fig([('A', m1, v1), ('B', m2, -v2)], [('AB', m1 + m2, None)], merged=True), '62%')
        body = P('그림과 같이 마찰이 없는 수평면에서 서로 마주 보고 운동하던 수레 A(질량 %d kg, 속력 %d m/s)와 수레 B(질량 %d kg, 속력 %d m/s)가 충돌하여 한 덩어리가 되었다. 충돌 직후 두 수레의 속도는?' % (m1, v1, m2, v2)) + fig
        cands = [Fr(m1 * v1 + m2 * v2, m1 + m2), -V, Fr(v1 - v2, 2), Fr(m1 * v1 - m2 * v2, m1) if m1 else 1, Fr(m2 * v2 - m1 * v1, m2)]
        ws = _vel_ws(V, cands)
        assert m1 * v1 + m2 * (-v2) == (m1 + m2) * V
        return mc(body, _vel(V), ws, r=r, lv='상', fam='b', sort='shuf',
                  steps=['오른쪽을 +로 하면 운동량 보존 : %d × %d + %d × (-%d) = (%d + %d) × V' % (m1, v1, m2, v2, m1, m2), '%d = %d V 이므로 V = %s m/s → %s' % (m1 * v1 - m2 * v2, m1 + m2, _F(V), _vel(V))],
                  core='운동량은 벡터이므로 방향에 부호를 붙여 보존식을 세운다.', point='마주 보는 물체는 부호가 반대이다.')
    if fam == 'c':
        # 사람·물체가 수레에 올라탐 / 진흙
        for _ in range(300):
            M = r.choice([10, 20, 30, 40, 50, 60]); m = r.choice([5, 10, 20, 30, 40, 60])
            v = r.choice([2, 3, 4, 5, 6, 8])
            V = Fr(M * v, M + m)
            if _ok(V): break
        else:
            return None
        what = r.choice([('수레', '모래 주머니', '위에서 수직으로 떨어져'), ('얼음 위를 미끄러지는 썰매', '사람', '뒤에서 가만히 올라타'), ('수레', '진흙 덩어리', '수직으로 떨어져 달라붙')])
        body = P('마찰이 없는 수평면 위를 질량 %d kg인 %s가 %d m/s로 운동하고 있다. 여기에 질량 %d kg인 %s이(가) %s 함께 운동하게 되었다. 이후 속력은? (단, %s의 처음 수평 속도는 0이다.)' % (M, what[0], v, m, what[1], what[2], what[1]))
        ws = _ws(V, [Fr(v, 2), v, Fr(M * v, m), Fr(m * v, M + m), Fr(v * (M + m), M)], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(V), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['수평 방향으로 외력이 없으므로 수평 운동량이 보존된다.', '%d × %d + %d × 0 = (%d + %d) × V 이므로 V = %d ÷ %d = %s m/s' % (M, v, m, M, m, M * v, M + m, _F(V))],
                  core='수평 방향의 운동량이 보존된다(수직으로 떨어지는 물체의 수평 속도는 0).', point='달라붙은 뒤 질량은 합이다.')
    if fam == 'd':
        for _ in range(300):
            m1 = r.randint(1, 5); m2 = r.randint(1, 5); v1 = r.choice([4, 6, 8, 10, 12])
            V = Fr(m1 * v1, m1 + m2)
            if _ok(V) and V != v1: break
        t0 = r.choice([2, 3, 4])
        fig = FIG(_vt_merge_fig(v1, V, t0), '62%')
        ask = r.choice(['m2', 'm2'])
        body = P('그림은 마찰이 없는 수평면에서 일직선 위를 운동하는 물체 A, B의 속도를 시간에 따라 나타낸 것이다. 정지해 있던 B에 A가 %d초일 때 충돌하여 이후 두 물체는 한 덩어리가 되어 운동하였다. A의 질량이 %d kg일 때, B의 질량은?' % (t0, m1)) + fig
        ws = _ws(m2, [m1, m1 * V / v1, Fr(m1 * V, v1 - V) if v1 != V else m1, m1 * 2, m1 + m2 + 1], lambda c: _F(c) + ' kg')
        steps = ['그래프에서 충돌 전 A의 속도 %d m/s, 충돌 후 속도 %s m/s이다.' % (v1, _F(V)), '운동량 보존 : %d × %d = (%d + m) × %s' % (m1, v1, m1, _F(V)), '%d + m = %s 이므로 m = %d kg' % (m1, _F(m1 * v1 / V), m2)]
        assert Fr(m1 * v1) == (m1 + m2) * V
        return mc(body, '%d kg' % m2, ws, r=r, lv='상', fam='d', sort='num', steps=steps,
                  core='v-t 그래프에서 충돌 전후 속도를 읽어 운동량 보존식에 대입한다.', point='충돌 후 두 물체의 속도가 같다(한 덩어리).')
    # e: 충돌 후 속력이 처음의 몇 배
    for _ in range(100):
        n = r.choice([2, 3, 4, 5, 6])
        m = r.choice([1, 2, 3, 4])
        m2 = (n - 1) * m
    ratio = Fr(1, n)
    body = P('마찰이 없는 수평면에서 질량 %d kg인 물체 A가 속력 v로 운동하여 정지해 있던 질량 %d kg인 물체 B와 충돌한 뒤 한 덩어리가 되어 운동하였다. 충돌 후 속력은 v의 몇 배인가?' % (m, m2))
    right = '%s배' % _fx(ratio) if n != 1 else '1배'
    ws = ['%s배' % x for x in dict.fromkeys([_fx(Fr(1, n - 1) if n > 2 else Fr(1, 3)), _fx(Fr(n - 1, n)), '1/2' if n != 2 else '1/3', _fx(Fr(n, 1)), _fx(Fr(2, n))]) if '%s배' % x != right]
    return mc(body, right, ws[:5], r=r, lv='중', fam='e', sort='shuf',
              steps=['운동량 보존 : %d × v = (%d + %d) × V' % (m, m, m2), 'V = %d v ÷ %d = v/%d (%s배)' % (m, m + m2, n, _fx(ratio))],
              core='운동량 보존 : mv = (m + M)V → V = mv/(m + M).', point='충돌 후 질량은 합이므로 속력이 줄어든다.')


# ================================================================== ph060 1차원 탄성 충돌
def _elastic(m1, v1, m2, v2):
    u1 = Fr((m1 - m2) * v1 + 2 * m2 * v2, m1 + m2)
    u2 = Fr((m2 - m1) * v2 + 2 * m1 * v1, m1 + m2)
    assert m1 * v1 + m2 * v2 == m1 * u1 + m2 * u2
    assert m1 * v1 * v1 + m2 * v2 * v2 == m1 * u1 * u1 + m2 * u2 * u2
    assert u2 - u1 == v1 - v2
    return u1, u2


@T('ph060')
def elastic_collision(r, k):
    fam = r.choice(['a', 'a', 'a', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        for _ in range(300):
            m1, m2 = r.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2), (1, 4), (4, 1), (2, 1), (3, 5)])
            v1 = r.randint(1, 8) * (m1 + m2) // math.gcd(m1 + m2, 2) if False else r.choice([2, 3, 4, 5, 6, 8, 10, 12]) 
            u1, u2 = _elastic(m1, v1, m2, 0)
            if _ok(u1) and _ok(u2): break
        else:
            return None
        ask = r.choice(['u1', 'u2', 'both'])
        fig = FIG(_cart_fig([('A', m1, v1), ('B', m2, 0)], [('A', m1, u1 if ask == 'u2' else None), ('B', m2, u2 if ask == 'u1' else None)] if ask != 'both' else [('A', m1, None), ('B', m2, None)]), '64%')
        base = '그림과 같이 마찰이 없는 수평면에서 질량 %d kg인 수레 A가 %d m/s의 속력으로 운동하여 정지해 있던 질량 %d kg인 수레 B와 탄성 충돌하였다. ' % (m1, v1, m2)
        if ask == 'u1':
            body = P(base + '충돌 직후 A의 속도는? (오른쪽이 +방향이다.)') + fig
            ws = _vel_ws(u1, [Fr(v1, 2), Fr(m1 * v1, m1 + m2), Fr(m2 * v1, m1 + m2), -Fr(m2 - m1, m1 + m2) * v1 * 2, u2])
            return mc(body, _vel(u1), ws, r=r, lv='중', fam='a', sort='shuf',
                      steps=['운동량 보존 : %d × %d = %d × u₁ + %d × u₂' % (m1, v1, m1, m2), '탄성 충돌이므로 상대 속도의 크기가 같다 : u₂ - u₁ = v₁ - 0 = %d' % v1,
                             '두 식을 풀면 u₁ = %s m/s, u₂ = %s m/s이므로 A의 속도는 %s' % (_F(u1), _F(u2), _vel(u1)), '(확인) 운동 에너지 합 : ½ × %d × %d² = %s J = ½ × %d × %s² + ½ × %d × %s² = %s J' % (m1, v1, _F(Fr(m1 * v1 * v1, 2)), m1, _F(u1), m2, _F(u2), _F(Fr(m1 * u1 * u1 + m2 * u2 * u2, 2)))],
                      core='1차원 탄성 충돌에서 운동량과 운동 에너지가 모두 보존되며, 충돌 전후 상대 속도의 크기가 같다.', point='운동량 보존식과 상대 속도 관계식을 연립한다.')
        if ask == 'u2':
            body = P(base + '충돌 직후 B의 속도는? (오른쪽이 +방향이다.)') + fig
            ws = _vel_ws(u2, [Fr(v1, 2), Fr(m1 * v1, m1 + m2), v1, u1, Fr(m1 * v1, m2)])
            return mc(body, _vel(u2), ws, r=r, lv='하', fam='a', sort='shuf',
                      steps=['탄성 충돌 : u₂ = 2m₁v₁/(m₁ + m₂) = 2 × %d × %d ÷ %d = %s m/s' % (m1, v1, m1 + m2, _F(u2)), '(확인) u₁ = (m₁ - m₂)v₁/(m₁ + m₂) = %s m/s 이고 u₂ - u₁ = v₁ = %d 이다.' % (_F(u1), v1)],
                      core='정지한 물체에 탄성 충돌 : u₁ = (m₁ - m₂)v₁/(m₁ + m₂), u₂ = 2m₁v₁/(m₁ + m₂).', point='A의 질량이 작으면 되튀고, 크면 계속 같은 방향이다.')
        right = 'A : %s, B : %s' % (_vel(u1), _vel(u2))
        body = P(base + '충돌 직후 A, B의 속도를 옳게 짝지은 것은? (오른쪽이 +방향이다.)') + fig
        wr = []
        for a_, b_ in [(u2, u1), (-u1, u2), (u1, -u2), (Fr(v1, 2), Fr(v1, 2)), (Fr(m1 * v1, m1 + m2), Fr(m1 * v1, m1 + m2)), (u1 + 1, u2), (u1, u2 + 1)]:
            s_ = 'A : %s, B : %s' % (_vel(a_), _vel(b_))
            if s_ != right and s_ not in wr: wr.append(s_)
        return mc(body, right, wr[:5], r=r, lv='중', fam='a', sort='shuf',
                  steps=['운동량 보존과 상대 속도 관계로 u₁ = %s m/s, u₂ = %s m/s를 얻는다.' % (_F(u1), _F(u2)), '(검산) 운동량 : %d × %d = %d × %s + %d × %s' % (m1, v1, m1, _F(u1), m2, _F(u2))],
                  core='탄성 충돌에서는 운동량과 운동 에너지가 모두 보존된다.', point='두 속도를 모두 구하고 부호(방향)를 확인한다.')
    if fam == 'b':
        m = r.choice([1, 2, 3, 4, 5])
        v1 = r.choice([2, 3, 4, 5, 6, 8])
        v2 = r.choice([-6, -5, -4, -3, -2, 0, 2, 3, 4]) if True else 0
        if v1 == v2: return None
        u1, u2 = _elastic(m, v1, m, v2)
        assert (u1, u2) == (v2, v1)
        fig = FIG(_cart_fig([('A', m, v1), ('B', m, v2)], [('A', m, None), ('B', m, None)]), '64%')
        body = P('그림과 같이 마찰이 없는 수평면에서 질량이 같은 수레 A, B가 각각 %s, %s의 속도로 운동하다가 탄성 충돌하였다. 충돌 직후 B의 속도는? (오른쪽이 +방향이다.)' % (_vel(v1), _vel(v2))) + fig
        ws = _vel_ws(u2, [v2, -v1, Fr(v1 + v2, 2), -v2, Fr(v1 - v2, 2)])
        return mc(body, _vel(u2), ws, r=r, lv='하', fam='b', sort='shuf',
                  steps=['질량이 같은 두 물체가 1차원 탄성 충돌하면 속도를 서로 교환한다.', '운동량 보존과 상대 속도 관계로 확인 : u₁ = %s, u₂ = %s' % (_F(u1), _F(u2)), '따라서 B의 속도는 %s' % _vel(u2)],
                  core='질량이 같은 두 물체의 1차원 탄성 충돌에서는 속도가 서로 바뀐다.', point='부호(방향)까지 교환된다.')
    if fam == 'c':
        for _ in range(500):
            m1, m2 = r.randint(1, 5), r.randint(1, 5)
            v1, v2 = r.randint(2, 10), r.randint(-6, 4)
            if v1 <= v2 or m1 == m2: continue
            u1, u2 = _elastic(m1, v1, m2, v2)
            if _ok(u1) and _ok(u2): break
        else:
            return None
        who = r.choice(['A', 'B'])
        body = P('마찰이 없는 수평면에서 질량 %d kg인 물체 A가 %s, 질량 %d kg인 물체 B가 %s로 운동하다가 A가 B와 정면으로 탄성 충돌하였다. 충돌 직후 %s의 속도는? (오른쪽이 +방향이다.)' % (m1, _vel(v1), m2, _vel(v2), who))
        ans = u1 if who == 'A' else u2
        oth = u2 if who == 'A' else u1
        ws = _vel_ws(ans, [oth, -ans, Fr(m1 * v1 + m2 * v2, m1 + m2), v1 if who == 'A' else v2, v2 if who == 'A' else v1])
        return mc(body, _vel(ans), ws, r=r, lv='상', fam='c', sort='shuf',
                  steps=['운동량 보존 : %d × %d + %d × (%d) = %d u₁ + %d u₂' % (m1, v1, m2, v2, m1, m2), '상대 속도 : u₂ - u₁ = v₁ - v₂ = %d' % (v1 - v2),
                         '연립하면 u₁ = %s m/s, u₂ = %s m/s이므로 %s의 속도는 %s' % (_F(u1), _F(u2), who, _vel(ans))],
                  core='탄성 충돌 : 운동량 보존 + (u₂ - u₁ = v₁ - v₂).', point='부호를 붙여 두 식을 연립한다.')
    if fam == 'd':
        # 질량 비를 구하기 : A 가 정지한 B 에 충돌 후 속도 u1 주어짐
        for _ in range(100):
            n = r.choice([2, 3, 4, 5, Fr(1, 2), Fr(1, 3), 3])
            v1 = r.choice([6, 8, 10, 12, 15, 20])
            n = Fr(n)
            u1 = (1 - n) / (1 + n) * v1
            if _ok(u1): break
        m1 = 1
        fz = Fr(n)
        u1, u2 = _elastic(Fr(1).numerator * fz.denominator, v1, fz.numerator, 0)
        body = P('마찰이 없는 수평면에서 물체 A가 %d m/s의 속력으로 운동하여 정지해 있던 물체 B와 정면으로 탄성 충돌하였다. 충돌 직후 A의 속도는 %s이었다. B의 질량은 A의 질량의 몇 배인가?' % (v1, _vel(u1)))
        right = '%s배' % _fx(n)
        ws = ['%s배' % x for x in dict.fromkeys([_fx(1 / n), _fx(n + 1), _fx(n * 2), _fx(abs(n - 1) if n != 1 else 2), _fx(n * n)]) if '%s배' % x != right]
        ws = ws + ['%s배' % x for x in ('1/4', '5', '6') if '%s배' % x != right and '%s배' % x not in ws]
        return mc(body, right, ws[:5], r=r, lv='상', fam='d', sort='shuf',
                  steps=['A의 질량을 m, B의 질량을 nm이라 하면 u₁ = (1 - n)/(1 + n) × v₁ 이다.', '%s = (1 - n)/(1 + n) × %d 에서 n = %s' % (_F(u1), v1, _fx(n)), '(확인) u₂ = 2/(1 + n) × v₁ = %s m/s' % _F(u2)],
                  core='정지한 물체에 탄성 충돌 : u₁ = (m₁ - m₂)v₁/(m₁ + m₂).', point='되튀면 충돌한 물체가 더 가볍다.')
    # e: 상대 속도 반전
    for _ in range(200):
        v1, v2 = r.randint(3, 12), r.randint(-6, 2)
        u1 = r.randint(-6, v1 - 1)
        u2 = u1 + (v1 - v2)
        if v1 > v2 and u2 != v1: break
    body = P('마찰이 없는 수평면에서 두 물체 A, B가 정면으로 탄성 충돌하였다. 충돌 전 A, B의 속도는 각각 %s, %s이고, 충돌 직후 A의 속도는 %s이었다. 충돌 직후 B의 속도는? (오른쪽이 +방향이며, 질량은 주어지지 않았다.)' % (_vel(v1), _vel(v2), _vel(u1)))
    ws = _vel_ws(u2, [-u2, u1 + v1 + v2, v1 - u1 + v2, u1 - v2 + v1 if False else v1 + u1, v2 - u1])
    return mc(body, _vel(u2), ws, r=r, lv='중', fam='e', sort='shuf',
              steps=['탄성 충돌에서는 충돌 전후 두 물체의 상대 속도의 크기가 같고 방향이 반대이다.', 'v₁ - v₂ = u₂ - u₁ : %d - (%d) = u₂ - (%d)' % (v1, v2, u1), 'u₂ = %d m/s → %s' % (u2, _vel(u2))],
              core='탄성 충돌에서 (v₁ - v₂) = (u₂ - u₁).', point='질량을 몰라도 상대 속도 관계로 구할 수 있다.')


# ================================================================== ph061 분열과 반동
@T('ph061')
def explosion_recoil(r, k):
    fam = r.choice(['a', 'a', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        for _ in range(300):
            m1, m2 = r.randint(1, 6), r.randint(1, 6)
            if m1 == m2 and r.random() < .6: continue
            u1 = r.randint(1, 8)
            u2 = Fr(m1 * u1, m2)
            if _ok(u2): break
        else:
            return None
        assert m1 * u1 == m2 * u2
        ask = r.choice(['u2', 'u2', 'ratio', 'u1'])
        if ask == 'ratio':
            g = math.gcd(m1, m2)
            right = '%d : %d' % (m2 // g, m1 // g)
            fig = FIG(_cart_fig([('A+B', m1 + m2, 0)], [('A', m1, 'L?'), ('B', m2, 'R?')], spring=True), '62%')
            body = P('마찰이 없는 수평면에서 정지해 있던 물체가 내부의 폭발로 질량이 각각 %d kg, %d kg인 두 조각 A, B로 갈라져 서로 반대 방향으로 운동하였다. A, B의 속력의 비 v%s : v%s는?' % (m1, m2, sub('A'), sub('B'))) + fig
            wr = ['%d : %d' % (m1 // g, m2 // g), '1 : 1', '%d : %d' % (m2 * m2 // math.gcd(m1 * m1, m2 * m2), m1 * m1 // math.gcd(m1 * m1, m2 * m2)), '%d : %d' % (m1 * m1 // math.gcd(m1 * m1, m2 * m2), m2 * m2 // math.gcd(m1 * m1, m2 * m2)), '%d : %d' % (m1 + m2, m1)]
            wr = [c for c in dict.fromkeys(wr) if c != right]
            if m1 == m2: return None
            return mc(body, right, wr[:5], r=r, lv='중', fam='a', sort='shuf',
                      steps=['분열 전 운동량이 0이므로 분열 후 운동량의 합도 0이다 : %d v%s = %d v%s' % (m1, sub('A'), m2, sub('B')), 'v%s : v%s = %d : %d = %s' % (sub('A'), sub('B'), m2, m1, right)],
                      core='정지한 물체가 분열하면 운동량의 합이 0이므로 속력은 질량에 반비례한다.', point='질량이 작은 조각의 속력이 크다.')
        if ask == 'u1':
            u1_, u2_ = u2, u1
            nm1, nm2 = 'B', 'A'
            body = P('마찰이 없는 수평면에서 정지해 있던 물체가 폭발하여 질량 %d kg인 조각 A와 질량 %d kg인 조각 B로 갈라져 서로 반대 방향으로 운동하였다. A의 속력이 %s m/s일 때 B의 속력은?' % (m1, m2, _F(u1)))
        else:
            body = P('마찰이 없는 수평면에서 정지해 있던 물체가 폭발하여 질량 %d kg인 조각 A와 질량 %d kg인 조각 B로 갈라져 서로 반대 방향으로 운동하였다. A의 속력이 %d m/s일 때 B의 속력은?' % (m1, m2, u1))
        fig = FIG(_cart_fig([('A+B', m1 + m2, 0)], [('A', m1, -u1), ('B', m2, 'R?')], spring=True), '62%')
        body += fig
        ws = _ws(u2, [u1, Fr(m2 * u1, m1), u1 * (m1 + m2), Fr(m1 * u1, m1 + m2), u2 * 2], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(u2), ws, r=r, lv='하', fam='a', sort='num',
                  steps=['분열 전 운동량 = 0 이므로 m%s v%s = m%s v%s' % (sub('A'), sub('A'), sub('B'), sub('B')), '%d × %d = %d × v%s 이므로 v%s = %s m/s' % (m1, u1, m2, sub('B'), sub('B'), _F(u2))],
                  core='분열 전후 운동량 보존 : 0 = m₁v₁ + m₂v₂ (속도는 서로 반대 방향).', point='속력은 질량에 반비례한다.')
    if fam == 'b':
        for _ in range(300):
            mb = r.choice([0.01, 0.02, 0.05, 0.1, 0.2]); vb = r.choice([100, 200, 300, 400, 500, 600, 800])
            M = r.choice([1, 2, 2.5, 4, 5, 8, 10, 20])
            mbb = Fr(mb).limit_denominator(100)
            V = mbb * vb / Fr(M).limit_denominator(10)
            if _ok(V) and V <= 10: break
        else:
            return None
        body = P('질량 %s kg인 총이 정지해 있다가 질량 %s kg인 총알을 %d m/s의 속력으로 수평 방향으로 발사하였다. 총이 반동하여 뒤로 물러나는 속력은? (단, 총과 총알의 질량은 총알의 질량을 포함하지 않은 총의 질량으로 하며, 마찰은 무시한다.)' % (_F(M), _F(mb), vb))
        ws = _ws(V, [mbb * vb, vb / Fr(M).limit_denominator(10), V * 2, V / 2, Fr(M).limit_denominator(10) * V * 5], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(V), ws, r=r, lv='하', fam='b', sort='num',
                  steps=['발사 전 운동량 0 = 발사 후 총알의 운동량 + 총의 운동량', 'm%s v%s = M V 이므로 V = %s × %d ÷ %s = %s m/s' % (sub('총알'), sub('총알'), _F(mb), vb, _F(M), _F(V))],
                  core='총과 총알 사이의 내력에 의해 전체 운동량(0)이 보존되므로 총은 총알과 반대 방향으로 반동한다.', point='질량이 큰 쪽의 속력이 작다.')
    if fam == 'c':
        for _ in range(300):
            M = r.choice([40, 45, 50, 60, 65, 70, 80]); m = r.choice([1, 2, 4, 5, 8, 10, 20])
            u = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15])
            V = Fr(m * u, M)
            if _ok(V): break
        else:
            return None
        what = r.choice([('공을', '던졌다'), ('물체를', '던졌다'), ('돌멩이를', '던졌다')])
        body = P('마찰이 없는 얼음판 위에 정지해 있던 질량 %d kg인 사람이 질량 %d kg인 %s 수평 방향으로 %d m/s의 속력(지면 기준)으로 %s. 사람이 반대 방향으로 미끄러지는 속력은? (단, 사람의 질량은 던진 물체의 질량을 제외한 값이다.)' % (M, m, what[0], u, what[1]))
        ws = _ws(V, [Fr(m * u, M + m), Fr(M * u, m) if M * u % m == 0 else V * 3, u, V * 2, Fr(u, 2)], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(V), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['외력이 없으므로 운동량이 보존된다 : 0 = %d × %d - %d × V' % (m, u, M), 'V = %d ÷ %d = %s m/s' % (m * u, M, _F(V))],
                  core='정지해 있던 계에서 한 쪽이 운동량을 얻으면 다른 쪽은 반대 방향으로 같은 크기의 운동량을 얻는다.', point='던진 물체의 속도는 지면 기준이다.')
    if fam == 'd':
        # 상대 속도 (보트 위 사람)
        for _ in range(300):
            M = r.choice([30, 40, 50, 60, 100, 120, 200]); m = r.choice([40, 50, 60, 20, 30, 80, 100])
            u = r.choice([1, 2, 3, 4, 5])
            vb = Fr(m * u, m + M)
            if _ok(vb): break
        else:
            return None
        vp = Fr(M * u, m + M)
        assert m * vp == M * vb and vp + vb == u
        ask = r.choice(['boat', 'person'])
        body = P('마찰이 없는 호수 위에 정지해 있는 질량 %d kg인 보트 위에 질량 %d kg인 사람이 서 있다. 사람이 보트에 대해 %d m/s의 속력으로 보트의 앞쪽으로 걸어갈 때, %s의 속력(지면 기준)은?' % (M, m, u, '보트' if ask == 'boat' else '사람'))
        ans = vb if ask == 'boat' else vp
        ws = _ws(ans, [u, Fr(m * u, M), Fr(M * u, m), vb if ask == 'person' else vp, Fr(u, 2)], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(ans), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['지면 기준으로 사람의 속력을 v₁, 보트의 속력을 v₂(반대 방향)라 하면 운동량 보존 : %d v₁ = %d v₂' % (m, M), '상대 속력 v₁ + v₂ = %d m/s' % u, '연립하면 v₁ = %s m/s, v₂ = %s m/s이므로 %s의 속력은 %s m/s' % (_F(vp), _F(vb), '보트' if ask == 'boat' else '사람', _F(ans))],
                  core='사람이 보트에 대해 움직일 때는 지면 기준 속도로 운동량 보존식을 세우고, 상대 속도 관계를 함께 쓴다.', point='보트에 대한 속력은 지면 기준 두 속력의 합이다.')
    # e: 분열 후 운동 에너지
    for _ in range(300):
        m1, m2 = r.choice([(1, 3), (3, 1), (1, 2), (2, 1), (1, 4), (4, 1), (2, 3), (3, 2), (1, 5), (3, 5)])
        E = r.choice([20, 40, 60, 80, 120, 160, 200])
        E1 = Fr(E * m2, m1 + m2)
        if _ok(E1): break
    else:
        return None
    E2 = E - E1
    # 검증 : p 동일 -> Ek = p^2/2m
    p2 = 2 * m1 * E1
    assert p2 == 2 * m2 * E2
    ask = r.choice(['ratio', 'E1'])
    if ask == 'ratio':
        g = math.gcd(m2, m1)
        right = '%d : %d' % (m2 // g, m1 // g)
        body = P('정지해 있던 물체가 폭발하여 질량이 각각 %d kg, %d kg인 두 조각 A, B로 갈라져 서로 반대 방향으로 운동하였다. 폭발 직후 A, B의 운동 에너지의 비 E_k(A) : E_k(B)는?' % (m1, m2))
        wr = ['%d : %d' % (m1 // g, m2 // g), '1 : 1', '%d : %d' % (m2 * m2 // math.gcd(m1 * m1, m2 * m2), m1 * m1 // math.gcd(m1 * m1, m2 * m2)), '%d : %d' % (m1 * m1 // math.gcd(m1 * m1, m2 * m2), m2 * m2 // math.gcd(m1 * m1, m2 * m2)), '%d : %d' % (m1 + m2, m1)]
        wr = [c for c in dict.fromkeys(wr) if c != right]
        if m1 == m2: return None
        return mc(body, right, wr[:5], r=r, lv='중', fam='e', sort='shuf',
                  steps=['운동량의 크기 p가 같으므로 E_k = p²/2m ∝ 1/m 이다.', 'E_k(A) : E_k(B) = 1/%d : 1/%d = %d : %d = %s' % (m1, m2, m2, m1, right)],
                  core='분열한 두 조각의 운동량 크기는 같으므로 운동 에너지는 질량에 반비례한다.', point='가벼운 조각이 운동 에너지를 더 많이 가진다.')
    body = P('정지해 있던 물체가 폭발하여 질량이 각각 %d kg, %d kg인 두 조각 A, B로 갈라져 서로 반대 방향으로 운동하였다. 폭발로 두 조각이 얻은 운동 에너지의 합이 %d J일 때, A의 운동 에너지는?' % (m1, m2, E))
    ws = _ws(E1, [E2, Fr(E, 2), Fr(E * m1, m1 + m2), E, E1 * 2], lambda c: _F(c) + ' J')
    return mc(body, '%s J' % _F(E1), ws, r=r, lv='상', fam='e', sort='num',
              steps=['운동량의 크기가 같으므로 E_k ∝ 1/m : E_k(A) : E_k(B) = %d : %d' % (m2, m1), 'E_k(A) = %d × %d/%d = %s J (B는 %s J)' % (E, m2, m1 + m2, _F(E1), _F(E2))],
              core='분열 후 두 조각의 운동량 크기가 같으므로 에너지는 질량에 반비례하여 나뉜다.', point='에너지 비는 질량 비의 역수이다.')


# ================================================================== ph062 충돌에서 운동 에너지의 변화
def _collide(m1, v1, m2, v2, e):
    e = Fr(e)
    P_ = m1 * v1 + m2 * v2
    u1 = (P_ - m2 * e * (v1 - v2)) / Fr(m1 + m2)
    u2 = (P_ + m1 * e * (v1 - v2)) / Fr(m1 + m2)
    assert m1 * v1 + m2 * v2 == m1 * u1 + m2 * u2
    return u1, u2


def _ek(m1, v1, m2, v2):
    return Fr(1, 2) * (m1 * Fr(v1) ** 2 + m2 * Fr(v2) ** 2)


@T('ph062')
def collision_energy(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'd', 'e'])
    if fam == 'a':
        for _ in range(300):
            m1, m2 = r.randint(1, 6), r.randint(1, 6)
            v1 = r.randint(2, 10)
            V = Fr(m1 * v1, m1 + m2)
            dE = _ek(m1, v1, 0, 0) - _ek(m1 + m2, V, 0, 0)
            if _ok(dE) and _ok(V): break
        else:
            return None
        assert dE == _ek(m1, v1, 0, 0) * Fr(m2, m1 + m2)
        ask = r.choice(['dE', 'dE', 'pct'])
        fig = FIG(_cart_fig([('A', m1, v1), ('B', m2, 0)], [('AB', m1 + m2, V)], merged=True), '62%')
        base = '그림과 같이 마찰이 없는 수평면에서 질량 %d kg인 수레 A가 %d m/s로 운동하여 정지해 있던 질량 %d kg인 수레 B와 충돌한 뒤 한 덩어리가 되어 운동하였다. ' % (m1, v1, m2)
        if ask == 'dE':
            body = P(base + '충돌로 손실된 운동 에너지는?') + fig
            ws = _ws(dE, [_ek(m1, v1, 0, 0), _ek(m1 + m2, V, 0, 0), _ek(m1, v1, 0, 0) - _ek(m1, V, 0, 0), dE * 2, _ek(m1 + m2, V, 0, 0) * 2])
            ws = _ws(dE, [_ek(m1, v1, 0, 0), _ek(m1 + m2, V, 0, 0), _ek(m1, v1, 0, 0) - _ek(m1, V, 0, 0), dE * 2, _ek(m1 + m2, V, 0, 0) * 2], lambda c: _F(c) + ' J')
            return mc(body, '%s J' % _F(dE), ws, r=r, lv='중', fam='a', sort='num',
                      steps=['충돌 후 속력 V = %d × %d ÷ %d = %s m/s (운동량 보존)' % (m1, v1, m1 + m2, _F(V)), '충돌 전 운동 에너지 = ½ × %d × %d² = %s J' % (m1, v1, _F(_ek(m1, v1, 0, 0))), '충돌 후 운동 에너지 = ½ × %d × %s² = %s J' % (m1 + m2, _F(V), _F(_ek(m1 + m2, V, 0, 0))),
                             '손실된 운동 에너지 = %s - %s = %s J' % (_F(_ek(m1, v1, 0, 0)), _F(_ek(m1 + m2, V, 0, 0)), _F(dE))],
                      core='완전 비탄성 충돌에서는 운동량은 보존되지만 운동 에너지는 감소한다(열 등으로 전환).', point='속력을 먼저 구한 뒤 충돌 전후의 운동 에너지를 비교한다.')
        frac_ = Fr(m2, m1 + m2) * 100
        body = P(base + '충돌로 손실된 운동 에너지는 충돌 전 운동 에너지의 몇 %인가?') + fig
        ws = _ws(frac_, [100 - frac_, Fr(m1, m1 + m2) * 100, 50, Fr(100 * m2, m1) if m2 * 100 % m1 == 0 else frac_ + 10, frac_ / 2], lambda c: _F(c) + '%')
        return mc(body, '%s%%' % _F(frac_), ws, r=r, lv='중', fam='a', sort='num',
                  steps=['충돌 후 V = m₁v₁/(m₁ + m₂)이므로 충돌 후 운동 에너지/충돌 전 운동 에너지 = m₁/(m₁ + m₂) = %d/%d' % (m1, m1 + m2), '손실 비율 = 1 - %d/%d = %d/%d = %s%%' % (m1, m1 + m2, m2, m1 + m2, _F(frac_))],
                  core='정지한 물체에 부딪혀 합쳐지면 손실 비율은 m₂/(m₁ + m₂)이다.', point='운동 에너지 비 = 질량 비(속력의 제곱 비가 아님).')
    if fam == 'b':
        for _ in range(500):
            m1, m2 = r.randint(1, 5), r.randint(1, 5)
            v1, v2 = r.randint(2, 10), r.choice([0, 0, -2, -3, 1, -1])
            if v1 <= v2: continue
            e = r.choice([Fr(1), Fr(1, 2), Fr(0)])
            u1, u2 = _collide(m1, v1, m2, v2, e)
            if not (_ok(u1) and _ok(u2)) or Fr(u1).denominator > 2 or Fr(u2).denominator > 2: continue
            dE = _ek(m1, v1, m2, v2) - _ek(m1, u1, m2, u2)
            if _ok(dE): break
        else:
            return None
        kinds = {Fr(1): '탄성 충돌', Fr(1, 2): '비탄성 충돌', Fr(0): '완전 비탄성 충돌'}
        tb = table(['', '질량 (kg)', '충돌 전 속도 (m/s)', '충돌 후 속도 (m/s)'], [['A', m1, _F(v1), _F(u1)], ['B', m2, _F(v2), _F(u2)]])
        body = P('표는 마찰이 없는 수평면에서 한 직선 위를 운동하는 두 물체 A, B가 충돌하기 전과 후의 질량과 속도를 나타낸 것이다(오른쪽이 +방향). 이 충돌의 종류와 충돌로 손실된 운동 에너지를 옳게 짝지은 것은?') + tb
        right = '%s, %s J' % (kinds[e], _F(dE))
        wr = []
        for e2 in kinds:
            for loss in (dE, dE + 2, dE * 2, Fr(0), dE + 5):
                if (e2 == Fr(1)) != (loss == 0) and not (e2 == e and loss == dE): pass
                s_ = '%s, %s J' % (kinds[e2], _F(loss))
                if s_ != right and s_ not in wr and (loss != dE) != (e2 != e): wr.append(s_)
        wr = [w for w in wr if w != right]
        r.shuffle(wr)
        Ek0, Ek1 = _ek(m1, v1, m2, v2), _ek(m1, u1, m2, u2)
        return mc(body, right, wr[:5], r=r, lv='중' if e == 1 else '상', fam='b', sort='shuf',
                  steps=['운동량 확인 : 전 %d × %s + %d × %s = %s, 후 %d × %s + %d × %s = %s 로 보존된다.' % (m1, _F(v1), m2, _F(v2), _F(m1 * v1 + m2 * v2), m1, _F(u1), m2, _F(u2), _F(m1 * u1 + m2 * u2)),
                         '운동 에너지 : 전 %s J, 후 %s J → 손실 %s J' % (_F(Ek0), _F(Ek1), _F(dE)),
                         '손실이 ' + ('없으므로 탄성 충돌이다.' if e == 1 else '있고 충돌 후 두 물체의 속도가 같으므로 완전 비탄성 충돌이다.' if e == 0 else '있으며 두 물체가 따로 운동하므로 (완전 비탄성이 아닌) 비탄성 충돌이다.')],
                  core='탄성 충돌은 운동 에너지가 보존되고, 비탄성 충돌은 운동 에너지가 감소하며, 완전 비탄성 충돌은 충돌 후 한 덩어리가 된다.', point='충돌 전후의 운동 에너지 합을 직접 비교한다.')
    if fam == 'c':
        m1, m2 = r.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (1, 4), (3, 2), (1, 5)])
        frac_ = Fr(m2, m1 + m2) * 100
        body = P('질량이 각각 %d kg, %d kg인 두 물체 중 질량 %d kg인 물체가 정지해 있는 다른 물체와 충돌하여 한 덩어리가 되었다. 충돌 과정에서 손실되는 운동 에너지는 처음 운동 에너지의 몇 %%인가? (단, 정지해 있던 물체의 질량은 %d kg이다.)' % (m1, m2, m1, m2))
        ws = _ws(frac_, [100 - frac_, 50, Fr(m1, m2) * 100 if Fr(m1, m2) * 100 < 1000 else 25, frac_ / 2 if _ok(frac_ / 2) else 40, 100 * Fr(m2, m1) if m2 != m1 else 25], lambda c: _F(c) + '%')
        return mc(body, '%s%%' % _F(frac_), ws, r=r, lv='하', fam='c', sort='num',
                  steps=['V = m₁v/(m₁ + m₂) 이므로 나중 운동 에너지/처음 운동 에너지 = m₁/(m₁ + m₂) = %d/%d' % (m1, m1 + m2), '손실 비율 = %d/%d = %s%%' % (m2, m1 + m2, _F(frac_))],
                  core='완전 비탄성 충돌의 손실률 = m₂/(m₁ + m₂) (정지한 표적의 질량 비율).', point='같은 질량이면 절반을 잃는다.')
    if fam == 'd':
        for _ in range(500):
            m1, m2 = r.randint(1, 5), r.randint(1, 5)
            v1 = r.randint(3, 10)
            u1 = r.randint(-3, v1 - 1)
            u2 = Fr(m1 * (v1 - u1), m2)
            if u2 <= u1: continue
            dE = _ek(m1, v1, m2, 0) - _ek(m1, u1, m2, u2)
            if _ok(u2) and _ok(dE) and dE > 0: break
        else:
            return None
        assert m1 * v1 == m1 * u1 + m2 * u2
        fig = FIG(_cart_fig([('A', m1, v1), ('B', m2, 0)], [('A', m1, u1), ('B', m2, None)]), '64%')
        body = P('그림과 같이 마찰이 없는 수평면에서 질량 %d kg인 수레 A가 %d m/s로 운동하여 정지해 있던 질량 %d kg인 수레 B와 충돌하였다. 충돌 후 A의 속도는 %s이었다. 이 충돌에서 손실된 운동 에너지는? (오른쪽이 +방향이다.)' % (m1, v1, m2, _vel(u1))) + fig
        ws = _ws(dE, [_ek(m1, v1, m2, 0), _ek(m1, u1, m2, u2), _ek(m1, v1, 0, 0) - _ek(m1, u1, 0, 0), dE * 2, dE + 3], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(dE), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['운동량 보존 : %d × %d = %d × %s + %d × u 이므로 u = %s m/s (B의 속도)' % (m1, v1, m1, _F(u1), m2, _F(u2)), '충돌 전 E_k = %s J, 충돌 후 E_k = ½ × %d × %s² + ½ × %d × %s² = %s J' % (_F(_ek(m1, v1, m2, 0)), m1, _F(u1), m2, _F(u2), _F(_ek(m1, u1, m2, u2))),
                         '손실 = %s - %s = %s J' % (_F(_ek(m1, v1, m2, 0)), _F(_ek(m1, u1, m2, u2)), _F(dE))],
                  core='운동량 보존으로 모르는 속도를 구한 뒤 충돌 전후 운동 에너지를 비교한다.', point='A의 에너지 변화만 보지 않고 두 물체의 합을 본다.')
    # e: 탄성 충돌에서 에너지 전달 비율
    m1, m2 = r.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (1, 4), (2, 3), (3, 2), (1, 5)])
    v1 = r.choice([5, 6, 8, 10, 12, 15])
    u1, u2 = _elastic(m1, v1, m2, 0)
    frac_ = _ek(0, 0, m2, u2) / _ek(m1, v1, 0, 0) * 100
    if not _ok(frac_): return None
    body = P('마찰이 없는 수평면에서 질량 %d kg인 물체가 %d m/s의 속력으로 운동하여 정지해 있던 질량 %d kg인 물체와 정면으로 탄성 충돌하였다. 충돌 후 처음에 정지해 있던 물체가 가진 운동 에너지는 처음 운동하던 물체의 충돌 전 운동 에너지의 몇 %%인가?' % (m1, v1, m2))
    ws = _ws(frac_, [100 - frac_, 50, 100, Fr(100 * m1, m1 + m2), frac_ / 2], lambda c: _F(c) + '%')
    return mc(body, '%s%%' % _F(frac_), ws, r=r, lv='중', fam='e', sort='num',
              steps=['탄성 충돌 후 정지했던 물체의 속도 u₂ = 2m₁v/(m₁ + m₂) = %s m/s' % _F(u2), '그 물체의 운동 에너지 = ½ × %d × %s² = %s J, 처음 운동 에너지 = ½ × %d × %d² = %s J' % (m2, _F(u2), _F(_ek(0, 0, m2, u2)), m1, v1, _F(_ek(m1, v1, 0, 0))),
                     '비율 = %s%% (= 4m₁m₂/(m₁ + m₂)² × 100 %%)' % _F(frac_)],
              core='1차원 탄성 충돌에서 정지한 물체가 얻는 운동 에너지 비율은 4m₁m₂/(m₁ + m₂)²이다.', point='질량이 같으면 모든 에너지가 전달된다.')


# ================================================================== ph063 충격량과 충격력의 응용(<보기>)
_IBANK = [
    ('에어백은 충돌 시간을 길게 하여 사람이 받는 평균 힘을 줄인다.', True, '충격량이 같을 때 충돌 시간이 길수록 평균 힘 F = I/Δt가 작아진다.', 'air'),
    ('에어백은 충돌 시 사람이 받는 충격량을 크게 줄여 준다.', False, '운동량 변화량(충격량)은 같고, 충돌 시간을 늘려 평균 힘을 줄이는 것이다.', 'air'),
    ('같은 충격량을 받을 때 충돌 시간이 길수록 평균 힘은 작다.', True, 'F = I/Δt 이므로 시간이 길면 힘이 작아진다.', 'rel'),
    ('물체가 받는 충격량은 물체의 운동량의 변화량과 같다.', True, 'I = FΔt = Δp 이다.', 'imp'),
    ('힘이 클수록 충격량은 항상 크다.', False, '충격량은 힘과 시간의 곱이므로 시간이 짧으면 힘이 커도 충격량이 작을 수 있다.', 'imp2'),
    ('높은 곳에서 뛰어내려 착지할 때 무릎을 굽히면 받는 충격량이 줄어든다.', False, '운동량 변화(충격량)는 같고, 충돌 시간이 늘어 평균 힘이 줄어드는 것이다.', 'knee'),
    ('높은 곳에서 뛰어내려 착지할 때 무릎을 굽히면 충돌 시간이 길어져 평균 힘이 줄어든다.', True, '충격량이 같을 때 시간이 길면 평균 힘이 작다.', 'knee'),
    ('자동차 범퍼가 충돌 때 찌그러지는 것은 충돌 시간을 늘려 충격력을 줄이는 효과가 있다.', True, '찌그러지며 충돌 시간이 길어져 평균 힘이 작아진다.', 'bump'),
    ('야구공을 잡을 때 손을 뒤로 빼며 받으면 충돌 시간이 길어져 손이 받는 평균 힘이 줄어든다.', True, '같은 운동량 변화에서 시간이 길수록 힘이 작아진다.', 'glove'),
    ('달걀을 같은 높이에서 떨어뜨릴 때 방석 위에서 깨지지 않는 것은 충격량이 작기 때문이다.', False, '충격량은 같고 충돌 시간이 길어 평균 힘이 작기 때문이다.', 'egg'),
    ('달걀을 같은 높이에서 떨어뜨릴 때 방석 위에서 깨지지 않는 것은 충돌 시간이 길어 평균 힘이 작기 때문이다.', True, '평균 힘 F = Δp/Δt에서 Δt가 클수록 F가 작다.', 'egg'),
    ('벽에 부딪혀 같은 속력으로 되튀어 나온 공의 운동량 변화량은 0이다.', False, '운동량은 방향이 반대로 바뀌므로 변화량의 크기는 2mv이다.', 'bounce'),
    ('같은 속력으로 날아온 공이 벽에 부딪혀 정지할 때보다 같은 속력으로 되튈 때 받는 충격량이 더 크다.', True, '정지: Δp = mv, 되튐: Δp = 2mv이다.', 'bounce2'),
    ('운동량은 크기와 방향을 모두 가지는 벡터량이다.', True, 'p = mv 이므로 속도의 방향이 곧 운동량의 방향이다.', 'vec'),
    ('충격량의 단위 N·s와 운동량의 단위 kg·m/s는 서로 같다.', True, '1 N·s = 1 (kg·m/s²)·s = 1 kg·m/s 이다.', 'unit'),
    ('F-t 그래프에서 그래프 아래의 넓이는 힘이 한 일이다.', False, 'F-t 그래프의 넓이는 충격량이다(힘이 한 일은 F-s 그래프의 넓이).', 'area'),
    ('F-t 그래프에서 그래프 아래의 넓이는 물체가 받은 충격량이다.', True, 'I = FΔt 이므로 넓이가 충격량이다.', 'area'),
    ('운동량이 같은 두 물체를 같은 크기의 일정한 힘으로 정지시키면 걸리는 시간은 서로 같다.', True, 'I = FΔt = Δp 에서 Δp와 F가 같으므로 Δt가 같다.', 'stop'),
    ('질량이 큰 물체의 운동량이 항상 더 크다.', False, '운동량은 mv이므로 속도에 따라 달라진다.', 'mass'),
    ('평균 힘은 충격량을 충돌 시간으로 나눈 값이다.', True, 'F̄ = I/Δt 이다.', 'avg'),
    ('충돌 시간이 같을 때 평균 힘이 클수록 충격량도 크다.', True, 'I = F̄Δt 에서 Δt가 같으면 F̄가 클수록 I가 크다.', 'rel2'),
    ('포장 완충재를 쓰는 것은 충돌 시간을 줄여 물체가 받는 충격량을 늘리기 위해서이다.', False, '충돌 시간을 늘려 평균 힘(충격력)을 줄이기 위해서이다.', 'pack'),
]


def _two_tri_fig(Fa, ta, Fb, tb, w=320, h=200):
    tmax = max(ta, tb)
    pl = Plot(w, h, tmax * 1.15, max(Fa, Fb) * 1.2, ml=48, mb=30)
    xt = sorted({ta, tb}); yt = sorted({Fa, Fb})
    pl.axes('t (s)', 'F (N)', xticks=xt, yticks=yt, grid=True)
    pl.pl([(0, 0), (ta / 2, Fa), (ta, 0)], RD, 2.6)
    pl.pl([(0, 0), (tb / 2, Fb), (tb, 0)], BL, 2.6)
    pl.text(pl.px(ta / 2) - 10, pl.py(Fa) - 4, 'A', 15, 'end', True, RD, True)
    pl.text(pl.px(tb / 2) + 12, pl.py(Fb) - 4, 'B', 15, 'start', True, BL, True)
    return pl.svg()


@T('ph063')
def impulse_bogi(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c'])
    if fam == 'a':
        for _ in range(100):
            s = r.sample(_IBANK, 3)
            if len({x[3] for x in s}) < 3: continue
            t = [x[1] for x in s]
            if not any(t): continue
            break
        else:
            return None
        return bogi(r.choice(['충격량과 충격력에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', '운동량과 충격량에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?']),
                    [(x[0], x[1], x[2]) for x in s], r=r, ask='', lv=r.choice(['하', '중']), fam='a',
                    core='충격량 I = FΔt = Δp 이며, 충격량이 같으면 충돌 시간이 길수록 평균 힘이 작다.', point='충격량과 평균 힘(충격력)을 구분한다.')
    if fam == 'b':
        for _ in range(200):
            Fa, Fb = r.choice([20, 30, 40, 50, 60, 80, 100]), r.choice([10, 15, 20, 25, 30, 40, 50])
            ta, tb = r.choice([2, 3, 4, 5, 6]), r.choice([4, 6, 8, 10])
            if Fa <= Fb or tb <= ta: continue
            same = r.random() < .5
            if same:
                # Fa*ta == Fb*tb
                if Fa * ta % tb: continue
                Fb = Fa * ta // tb
                if Fb in (0,) or Fb >= Fa: continue
            Ia, Ib = Fa * ta // 2, Fb * tb // 2
            if Fa * ta % 2 or Fb * tb % 2: continue
            break
        else:
            return None
        Ia, Ib = Fr(Fa * ta, 2), Fr(Fb * tb, 2)
        fig = FIG(_two_tri_fig(Fa, ta, Fb, tb), '64%')
        cand = [
            ('충격량의 크기는 A가 B보다 크다.', Ia > Ib, '그래프의 넓이: A = %s N·s, B = %s N·s이다.' % (_F(Ia), _F(Ib)), 'i1'),
            ('두 물체가 받은 충격량의 크기는 같다.', Ia == Ib, '그래프의 넓이: A = %s N·s, B = %s N·s이다.' % (_F(Ia), _F(Ib)), 'i1'),
            ('힘이 작용한 시간은 B가 A보다 길다.', tb > ta, '그래프에서 A는 %d초, B는 %d초 동안 힘이 작용했다.' % (ta, tb), 't1'),
            ('힘이 작용한 시간은 A가 B보다 길다.', ta > tb, '그래프에서 A는 %d초, B는 %d초 동안 힘이 작용했다.' % (ta, tb), 't1'),
            ('힘의 최댓값은 A가 B보다 크다.', Fa > Fb, '최댓값은 A가 %d N, B가 %d N이다.' % (Fa, Fb), 'f1'),
            ('평균 힘의 크기는 A가 B보다 크다.', Ia / ta > Ib / tb, '평균 힘 = 충격량/시간 : A = %s N, B = %s N이다.' % (_F(Ia / ta), _F(Ib / tb)), 'a1'),
            ('평균 힘의 크기는 B가 A보다 크다.', Ib / tb > Ia / ta, '평균 힘 = 충격량/시간 : A = %s N, B = %s N이다.' % (_F(Ia / ta), _F(Ib / tb)), 'a1'),
            ('A가 받은 충격량의 크기는 %s N·s이다.' % _F(Ia), True, '삼각형 넓이 = ½ × %d × %d = %s N·s이다.' % (Fa, ta, _F(Ia)), 'i2'),
            ('B가 받은 충격량의 크기는 %s N·s이다.' % _F(Ib + r.choice([5, 10])), False, '삼각형 넓이 = ½ × %d × %d = %s N·s이다.' % (Fb, tb, _F(Ib)), 'i3'),
            ('B가 받은 충격량의 크기는 %s N·s이다.' % _F(Ib), True, '삼각형 넓이 = ½ × %d × %d = %s N·s이다.' % (Fb, tb, _F(Ib)), 'i3'),
        ]
        for _ in range(100):
            s = r.sample(cand, 3)
            if len({x[3] for x in s}) < 3: continue
            t = [x[1] for x in s]
            if not any(t): continue
            break
        else:
            return None
        return bogi('그림은 질량이 같은 두 물체 A, B가 각각 어떤 물체와 충돌하는 동안 받은 힘의 크기를 시간에 따라 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', [(x[0], x[1], x[2]) for x in s], pre=fig, r=r, ask='', lv='중', fam='b',
                    core='F-t 그래프의 넓이가 충격량이고, 평균 힘 = 충격량 ÷ 시간이다.', point='그래프의 넓이·높이·폭을 각각 구분하여 비교한다.')
    # c: 공이 벽에 충돌
    for _ in range(200):
        m = r.choice([0.1, 0.2, 0.4, 0.5, 1, 2])
        mm = Fr(m).limit_denominator(10)
        v1 = r.choice([5, 10, 15, 20, 25, 30]); v2 = r.choice([0, 5, 10, 15, 20])
        dt = r.choice([Fr(1, 100), Fr(1, 50), Fr(1, 20), Fr(1, 10)])
        dp = mm * (v1 + v2)
        F = dp / dt
        if _ok(dp) and _ok(F): break
    else:
        return None
    wf = lambda x: x + r.choice([2, 5, 10])
    cand = [
        ('공이 받은 충격량의 크기는 %s N·s이다.' % _F(dp), True, '충격량 = Δp = %s × (%d + %d) = %s N·s이다.' % (_F(m), v1, v2, _F(dp)), 'p1'),
        ('공이 받은 충격량의 크기는 %s N·s이다.' % _F(mm * abs(v1 - v2) if v1 != v2 and v2 else mm * v1 * 2), False, '벽에 반대 방향으로 튕기면 Δp = m(v₁ + v₂) = %s N·s이다(크기를 더한다).' % _F(dp), 'p1') if v2 else ('공이 받은 충격량의 크기는 %s N·s이다.' % _F(mm * v1 * 2), False, '정지하였으므로 Δp = mv₁ = %s N·s이다.' % _F(dp), 'p1'),
        ('벽이 공에 작용한 평균 힘의 크기는 %s N이다.' % _F(F), True, '평균 힘 = Δp/Δt = %s ÷ %s = %s N이다.' % (_F(dp), _F(dt), _F(F)), 'f1'),
        ('벽이 공에 작용한 평균 힘의 크기는 %s N이다.' % _F(F * 2), False, '평균 힘 = Δp/Δt = %s N이다.' % _F(F), 'f1'),
        ('공이 벽에 작용한 평균 힘의 크기는 벽이 공에 작용한 평균 힘의 크기와 같다.', True, '작용 반작용 관계이다.', 'r1'),
        ('공이 벽에 작용한 평균 힘의 크기는 벽이 공에 작용한 평균 힘의 크기보다 작다.', False, '작용 반작용이므로 크기가 같다.', 'r1'),
        ('충돌 시간이 2배가 되면 같은 충돌에서 평균 힘은 ½배가 된다.', True, '충격량이 같으므로 F = Δp/Δt에서 Δt가 2배이면 F는 ½배이다.', 't1'),
        ('충돌 시간이 2배가 되면 같은 충돌에서 공이 받는 충격량도 2배가 된다.', False, '충격량은 운동량의 변화량으로 일정하다.', 't1'),
    ]
    if v2:
        cand.append(('충돌 전후 공의 운동량의 방향은 서로 반대이다.', True, '공이 되튀었으므로 운동량의 방향이 반대로 바뀐다.', 'd1'))
        cand.append(('충돌 전후 공의 운동량의 변화량은 %s kg·m/s이다.' % _F(mm * abs(v1 - v2)), False, '반대 방향이므로 Δp = m(v₁ + v₂) = %s kg·m/s이다.' % _F(dp), 'p2'))
    for _ in range(100):
        s = r.sample(cand, 3)
        if len({x[3] for x in s}) < 3: continue
        t = [x[1] for x in s]
        if not any(t): continue
        break
    else:
        return None
    return bogi('질량 %s kg인 공이 %d m/s의 속력으로 벽에 수직으로 충돌한 후 %s. 공과 벽의 접촉 시간은 %s초이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 공기 저항은 무시한다.)' % (_F(m), v1, ('%d m/s의 속력으로 되튀었다' % v2) if v2 else '정지하였다', _F(dt)),
                [(x[0], x[1], x[2]) for x in s], r=r, ask='', lv='상' if r.random() < .5 else '중', fam='c',
                core='I = Δp = F̄Δt이며, 공과 벽이 서로 작용하는 힘은 작용 반작용이다.', point='되튈 때는 운동량 변화를 크기의 합으로 계산한다.')


# ================================================================== ph064 운동량 보존 응용(수레·사람)
@T('ph064')
def momentum_apps(r, k):
    fam = r.choice(['a', 'a', 'b', 'c', 'c', 'd', 'e', 'f'])
    if fam == 'a':
        for _ in range(300):
            m1, m2 = r.randint(1, 6), r.randint(1, 6)
            if m1 == m2 and r.random() < .5: continue
            v1 = r.randint(1, 8)
            v2 = Fr(m1 * v1, m2)
            if _ok(v2): break
        else:
            return None
        E = Fr(1, 2) * m1 * v1 * v1 + Fr(1, 2) * m2 * v2 * v2
        ask = r.choice(['v2', 'v2', 'ratio', 'E'])
        fig = FIG(_cart_fig([('A', m1, 0), ('B', m2, 0)], [('A', m1, -v1 if ask != 'ratio' else 'L?'), ('B', m2, 'R?')], spring=True), '64%')
        if ask == 'E':
            fig = FIG(_cart_fig([('A', m1, 0), ('B', m2, 0)], [('A', m1, -v1), ('B', m2, v2)], spring=True), '64%')
            body = P('그림과 같이 마찰이 없는 수평면에서 용수철로 연결되어 압축된 채 정지해 있던 수레 A(질량 %d kg), B(질량 %d kg)를 놓았더니 용수철이 풀리며 두 수레가 서로 반대 방향으로 운동하였다. 분리 후 속력은 각각 A가 %d m/s, B가 %s m/s였다. 용수철에 저장되어 있던 탄성 위치 에너지는? (단, 용수철의 질량은 무시한다.)' % (m1, m2, v1, _F(v2))) + fig
            assert m1 * v1 == m2 * v2
            ws = _ws(E, [Fr(1, 2) * m1 * v1 * v1, Fr(1, 2) * m2 * v2 * v2, m1 * v1 * v1 + m2 * v2 * v2, E * 2, E / 2], lambda c: _F(c) + ' J')
            return mc(body, '%s J' % _F(E), ws, r=r, lv='중', fam='a', sort='num',
                      steps=['탄성 위치 에너지가 모두 두 수레의 운동 에너지로 전환된다.', 'E = ½ × %d × %d² + ½ × %d × %s² = %s + %s = %s J' % (m1, v1, m2, _F(v2), _F(Fr(1, 2) * m1 * v1 * v1), _F(Fr(1, 2) * m2 * v2 * v2), _F(E))],
                      core='용수철의 탄성 위치 에너지 = 분리 후 두 수레의 운동 에너지의 합(마찰 없음).', point='두 수레의 운동 에너지를 모두 더한다.')
        if ask == 'ratio':
            g = math.gcd(m1, m2)
            if m1 == m2: return None
            right = '%d : %d' % (m2 // g, m1 // g)
            body = P('그림과 같이 마찰이 없는 수평면에서 용수철로 연결되어 압축된 채 정지해 있던 수레 A(질량 %d kg), B(질량 %d kg)를 놓았더니 용수철이 풀리며 두 수레가 서로 반대 방향으로 운동하였다. 분리 직후 A, B의 속력의 비 v%s : v%s는?' % (m1, m2, sub('A'), sub('B'))) + fig
            wr = ['%d : %d' % (m1 // g, m2 // g), '1 : 1', '%d : %d' % (m2 * m2 // math.gcd(m1 * m1, m2 * m2), m1 * m1 // math.gcd(m1 * m1, m2 * m2)), '%d : %d' % (m1 * m1 // math.gcd(m1 * m1, m2 * m2), m2 * m2 // math.gcd(m1 * m1, m2 * m2)), '%d : %d' % (m1 + m2, m1)]
            wr = [c for c in dict.fromkeys(wr) if c != right]
            return mc(body, right, wr[:5], r=r, lv='하', fam='a', sort='shuf',
                      steps=['운동량 보존 : 0 = m%s v%s - m%s v%s' % (sub('A'), sub('A'), sub('B'), sub('B')), 'v%s : v%s = m%s : m%s = %d : %d = %s' % (sub('A'), sub('B'), sub('B'), sub('A'), m2, m1, right)],
                      core='정지 상태에서 용수철로 분리되면 두 물체의 운동량 크기가 같다.', point='속력은 질량에 반비례한다.')
        body = P('그림과 같이 마찰이 없는 수평면에서 용수철로 연결되어 압축된 채 정지해 있던 수레 A(질량 %d kg), B(질량 %d kg)를 놓았더니 용수철이 풀리며 두 수레가 서로 반대 방향으로 운동하였다. 분리 후 A의 속력이 %d m/s일 때 B의 속력은?' % (m1, m2, v1)) + fig
        ws = _ws(v2, [v1, Fr(m2 * v1, m1), Fr(m1 * v1, m1 + m2), v2 * 2, v1 + v2], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(v2), ws, r=r, lv='하', fam='a', sort='num',
                  steps=['운동량 보존 : 0 = m%s v%s - m%s v%s' % (sub('A'), sub('A'), sub('B'), sub('B')), '%d × %d = %d × v%s 이므로 v%s = %s m/s' % (m1, v1, m2, sub('B'), sub('B'), _F(v2))],
                  core='처음에 정지해 있던 두 물체가 분리되면 운동량의 합이 0이다.', point='반대 방향이므로 크기가 같다고 놓는다.')
    if fam == 'b':
        for _ in range(300):
            M = r.choice([10, 20, 30, 40, 50, 60, 100]); m = r.choice([5, 10, 20, 30, 40, 50, 60, 100])
            v = r.choice([2, 3, 4, 5, 6, 8, 10])
            V = Fr(M * v, M + m)
            if _ok(V): break
        else:
            return None
        body = P('마찰이 없는 수평면에서 질량 %d kg인 수레가 %d m/s의 속력으로 달리고 있다. 이 수레 위로 질량 %d kg인 모래 주머니가 연직 아래로 떨어져 수레에 실렸다. 이후 수레의 속력은?' % (M, v, m))
        ws = _ws(V, [Fr(v, 2), v, Fr(m * v, M + m), Fr(M * v, m) if M * v % m == 0 else V * 3, Fr(v * (M + m), M)], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(V), ws, r=r, lv='하', fam='b', sort='num',
                  steps=['수평 방향으로 외력이 없으므로 수평 방향의 운동량이 보존된다.', '%d × %d = (%d + %d) × V 이므로 V = %d ÷ %d = %s m/s' % (M, v, M, m, M * v, M + m, _F(V))],
                  core='수평 방향 운동량 보존 : 연직으로 떨어지는 물체는 수평 운동량이 0이다.', point='얹힌 물체의 질량만큼 전체 질량이 늘어난다.')
    if fam == 'c':
        # 수레 위에서 물체를 뒤로 던짐 (지면 기준 속력 w)
        for _ in range(500):
            M = r.choice([20, 30, 40, 50, 60, 100]); m = r.choice([2, 4, 5, 10])
            v0 = r.choice([0, 0, 2, 3, 4, 5])
            w = r.choice([4, 5, 6, 8, 10, 15, 20])
            V = (Fr(M + m) * v0 + m * w) / M      # 뒤쪽(-)으로 w 던지면 지면 기준 -w 
            # 던진 물체가 지면 기준 -w 이면 (M+m)v0 = M V - m w -> V = ((M+m)v0 + m w)/M
            if _ok(V) and V > 0: break
        else:
            return None
        assert (M + m) * v0 == M * V + m * (-w)
        start = '정지해 있는' if v0 == 0 else '%d m/s로 앞으로 달리고 있는' % v0
        body = P('마찰이 없는 수평면에서 %s 질량 %d kg인 수레(사람 포함) 위에서 사람이 질량 %d kg인 공을 수레의 뒤쪽으로 수평하게 던졌다. 공이 지면에 대해 %d m/s의 속력으로 뒤쪽으로 나아갔다면, 던진 직후 수레의 속력은? (단, 수레의 질량은 던진 공을 제외한 값이다.)' % (start, M, m, w))
        ws = _ws(V, [Fr(m * w, M) , Fr(m * w, M + m) + v0, v0 + Fr(m * w, M + m), V - v0 * 2 if V > v0 * 2 else V + 1, v0 - Fr(m * w, M) if v0 > Fr(m * w, M) else V * 2], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(V), ws, r=r, lv='상' if v0 else '중', fam='c', sort='num',
                  steps=['외력이 없으므로 운동량이 보존된다(앞쪽을 +).', '던지기 전 : (%d + %d) × %d = %d kg·m/s' % (M, m, v0, (M + m) * v0), '던진 후 : %d × V + %d × (-%d) = %d V - %d' % (M, m, w, M, m * w),
                         'V = (%d + %d) ÷ %d = %s m/s' % ((M + m) * v0, m * w, M, _F(V))],
                  core='수레와 공 전체의 운동량이 보존된다(속도는 지면 기준).', point='던진 공의 방향이 반대이므로 부호가 음(-)이다.')
    if fam == 'd':
        # 사람이 뒤로 뛰어내림
        for _ in range(500):
            M = r.choice([20, 30, 40, 50, 60]); m = r.choice([40, 50, 60, 30, 20])
            v0 = r.choice([2, 3, 4, 5, 6])
            u = r.choice([0, 1, 2, 3, 4])    # 사람이 뛰어내린 후 지면 기준 앞쪽 속력(0이면 정지)
            V = ((M + m) * v0 - m * u) / Fr(M)
            if _ok(V) and V > 0: break
        else:
            return None
        assert (M + m) * v0 == M * V + m * u
        who = ('수레의 뒤쪽으로 뛰어내려 지면에 대해 정지한 상태로 착지하였다' if u == 0 else '수레에서 뛰어내렸더니 뛰어내린 직후 사람의 속도는 지면에 대해 앞쪽으로 %d m/s였다' % u)
        body = P('마찰이 없는 수평면에서 질량 %d kg인 수레 위에 질량 %d kg인 사람이 타고 %d m/s로 달리고 있다. 사람이 %s. 이때 사람이 뛰어내린 직후 수레의 속력은?' % (M, m, v0, who))
        ws = _ws(V, [v0, Fr(m * v0, M), V - 1 if V > 1 else V + 2, Fr((M + m) * v0, M + m) + u, Fr(m * (v0 - u), M) + v0 if False else v0 + Fr(m * u, M)], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(V), ws, r=r, lv='중', fam='d', sort='num',
                  steps=['운동량 보존(앞쪽 +) : (%d + %d) × %d = %d × V + %d × %d' % (M, m, v0, M, m, u), '%d = %d V + %d 이므로 V = %s m/s' % ((M + m) * v0, M, m * u, _F(V))],
                  core='사람과 수레 전체의 운동량이 보존된다.', point='뛰어내린 사람의 속도는 지면 기준으로 넣는다.')
    if fam == 'e':
        # 수레에 대한 상대 속도로 걷기 (상)
        for _ in range(300):
            M = r.choice([20, 30, 40, 60, 100]); m = r.choice([20, 30, 40, 50, 60])
            u = r.choice([1, 2, 3, 4, 5])
            vc = Fr(m * u, M + m)
            if _ok(vc): break
        else:
            return None
        vp = u - vc
        assert m * vp == M * vc
        body = P('마찰이 없는 수평면에 정지해 있는 질량 %d kg인 수레 위에 질량 %d kg인 사람이 서 있다. 사람이 수레에 대해 %d m/s의 속력으로 앞쪽으로 걸어가기 시작했을 때, 수레의 속력(지면 기준)은?' % (M, m, u))
        ws = _ws(vc, [u, Fr(m * u, M), Fr(M * u, M + m), vp if vp != vc else vc * 2, Fr(u, 2)], lambda c: _F(c) + ' m/s')
        return mc(body, '%s m/s' % _F(vc), ws, r=r, lv='상', fam='e', sort='num',
                  steps=['지면 기준으로 사람의 속력을 v₁, 수레의 속력을 v₂(반대 방향)라 하면 %d v₁ = %d v₂ (운동량 보존)' % (m, M), 'v₁ + v₂ = %d (수레에 대한 상대 속력)' % u, '연립하여 v₂ = %d × %d ÷ (%d + %d) = %s m/s' % (m, u, M, m, _F(vc))],
                  core='상대 속도로 주어지면 지면 기준 속도로 바꿔 운동량 보존식과 연립한다.', point='수레가 뒤로 밀려나므로 사람의 지면 속력은 u보다 작다.')
    # f: 두 수레 충돌 후 분리 — 속도 구하기 (비탄성 + 용수철 범퍼)
    for _ in range(500):
        m1, m2 = r.randint(1, 5), r.randint(1, 5)
        v1 = r.randint(2, 10)
        V = Fr(m1 * v1, m1 + m2)
        if _ok(V) and m1 != m2: break
    else:
        return None
    mid = r.choice(['max', 'max'])
    # 용수철 최대 압축 순간: 두 수레 속도 같음, E_spring = 손실
    E = _ek(m1, v1, m2, 0) - _ek(m1 + m2, V, 0, 0)
    if not _ok(E): return None
    body = P('마찰이 없는 수평면에서 질량 %d kg인 수레 A가 %d m/s로 운동하여, 용수철이 달려 정지해 있는 질량 %d kg인 수레 B와 충돌하였다. 용수철이 가장 많이 압축된 순간 두 수레는 같은 속도로 운동한다. 이때 용수철에 저장된 탄성 위치 에너지는? (단, 용수철의 질량은 무시한다.)' % (m1, v1, m2))
    ws = _ws(E, [_ek(m1, v1, 0, 0), _ek(m1 + m2, V, 0, 0), E * 2, E / 2, _ek(m1, v1, 0, 0) - _ek(m1, V, 0, 0)], lambda c: _F(c) + ' J')
    return mc(body, '%s J' % _F(E), ws, r=r, lv='상', fam='f', sort='num',
              steps=['최대 압축 순간 두 수레의 속도가 같으므로 운동량 보존 : %d × %d = (%d + %d) V, V = %s m/s' % (m1, v1, m1, m2, _F(V)),
                     '에너지 보존 : 처음 운동 에너지 = 나중 운동 에너지 + 탄성 위치 에너지', '탄성 위치 에너지 = %s - %s = %s J' % (_F(_ek(m1, v1, 0, 0)), _F(_ek(m1 + m2, V, 0, 0)), _F(E))],
              core='용수철이 가장 압축된 순간 두 물체의 속도가 같으며, 줄어든 운동 에너지가 탄성 위치 에너지로 저장된다.', point='운동량 보존으로 공통 속도를, 에너지 보존으로 저장된 에너지를 구한다.')
