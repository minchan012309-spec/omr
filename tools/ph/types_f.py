# -*- coding: utf-8 -*-
"""Ⅰ-F 케플러 법칙과 만유인력 (ph042~ph048)."""
from phlib import *
import math
from fractions import Fraction as Fr

G = 10


# ------------------------------------------------------------------ 공통 도구
def _F(x, nd=2):
    if isinstance(x, Fr): x = float(x)
    return num(x, nd)


def _fx(x):
    """분수는 a/b 형태의 글자로, 정수는 그대로."""
    x = Fr(x).limit_denominator(10000)
    return str(x.numerator) if x.denominator == 1 else '%d/%d' % (x.numerator, x.denominator)


def _rs(x):
    x = Fr(x)
    if x.denominator == 1: return '%sR' % ('' if x == 1 else x.numerator)
    return '(%s)R' % _fx(x)


def _ws(right, cands, fmt=None, pos=True):
    fmt = fmt or _F
    """오답 후보 -> 서식 문자열 목록(정답과 겹치는 것·중복 제거). 후보가 모자라면 흔한 배수로 채운다."""
    right = Fr(right).limit_denominator(10000)
    seen = {fmt(right)}
    out = []
    ex = [right * 2, right / 2, right * 3, right / 3, right * 4, right / 4, right + 1, right - 1, right + 2, right - 2, right * Fr(3, 2), right * Fr(2, 3)]
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


def _rt(a, b):
    a, b = Fr(a), Fr(b)
    x, y = a.numerator * b.denominator, b.numerator * a.denominator
    g = math.gcd(x, y)
    return '%d : %d' % (x // g, y // g)


def _rts(right, cands):
    """비 문자열 오답."""
    seen = {right}; out = []
    for c in cands:
        if c in seen: continue
        seen.add(c); out.append(c)
    return out


def _fm(x, sym):
    """계수 x(Fraction) 와 기호 sym -> 'F/4', '4F', '3F/4' 형태(HTML)."""
    x = Fr(x)
    if x.denominator == 1:
        return sym if x == 1 else '%d%s' % (x.numerator, sym)
    return frac(sym if x.numerator == 1 else '%d%s' % (x.numerator, sym), x.denominator)


def _pt(th, e, a, sx, sy):
    pp = a * (1 - e * e)
    rr = pp / (1 + e * math.cos(th))
    return sx + rr * math.cos(th), sy - rr * math.sin(th)


def _wedge_area(e, t1, t2, n=600):
    """초점에서 잰 각도 t1~t2 의 부채꼴 넓이 (p=1 단위): ½∫ dθ/(1+e cosθ)²."""
    s = 0.0
    h = (t2 - t1) / n
    for i in range(n + 1):
        t = t1 + i * h
        w = 1 if i in (0, n) else (4 if i % 2 else 2)
        s += w / (1 + e * math.cos(t)) ** 2
    return 0.5 * s * h / 3


def _orbit(e, w=310, h=190, labp=None, labq=None, dots=(), sectors=(), a=118., unit=''):
    """타원 궤도: 태양(오른쪽 초점), 근일점 P(오른쪽 꼭짓점), 원일점 Q(왼쪽 꼭짓점)."""
    a = min(a, (h / 2 - 22) / math.sqrt(1 - e * e))
    c = a * e
    b = a * math.sqrt(1 - e * e)
    cx, cy = w / 2, h / 2 + 2
    sx, sy = cx + c, cy
    f = Fig(w, h)
    for (t1, t2, col, lab) in sectors:
        pts = [(sx, sy)] + [_pt(t1 + (t2 - t1) * i / 40, e, a, sx, sy) for i in range(41)]
        f.poly(pts, col, INK, 1.2)
    f.ell(cx, cy, a, b, 'none', INK, 1.8)
    for (t1, t2, col, lab) in sectors:
        tm = (t1 + t2) / 2
        x0, y0 = _pt(tm, e, a, sx, sy)
        dx, dy = x0 - sx, y0 - sy
        L = math.hypot(dx, dy)
        f.text(x0 + dx / L * 16, y0 + dy / L * 16 + 5, lab, 13, 'middle', True, INK, True)
    # 축과 거리 표시
    if labp is not None:
        f.line(sx, sy, cx + a, cy, RD, 1.6, '4 3')
        f.text((sx + cx + a) / 2 - 6, cy - 12, labp, 12, 'middle', True, RD)
    if labq is not None:
        f.line(sx, sy, cx - a, cy, BL, 1.6, '4 3')
        f.text((sx + cx - a) / 2, cy - 8, labq, 12, 'middle', True, BL)
    f.circ(sx, sy, 6.5, OR, INK, 1.2)
    f.text(sx, sy + 20, '태양', 12, 'middle', True, GR)
    pos = {'P': (cx + a, cy, 14, 5), 'Q': (cx - a, cy, -14, 5), 'R': (cx, cy - b, 0, -9), 'S': (cx, cy + b, 0, 17)}
    for d in dots:
        if not isinstance(d[1], str):  # (이름, 각도)
            nm_, th = d
            x0, y0 = _pt(th, e, a, sx, sy)
            dx, dy = x0 - sx, y0 - sy; L = math.hypot(dx, dy)
            f.circ(x0, y0, 4.5, BL, INK, 1)
            f.text(x0 + dx / L * 14, y0 + dy / L * 14 + 5, nm_, 14, 'middle', True, BL, True)
            continue
        x0, y0, ox, oy = pos[d[1]]
        f.circ(x0, y0, 4.5, BL, INK, 1)
        f.text(x0 + ox, y0 + oy, d[0], 14, 'middle', True, BL, True)
    return f.svg()


# ================================================================== ph042
@T('ph042')
def kepler2(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        n = r.choice([2, 3, 4, 5, 6, 8])
        dp = r.randint(1, 6)
        da = n * dp
        va = r.randint(2, 15)
        vp = n * va
        assert dp * vp == da * va
        up = r.choice([True, False])
        base = '행성이 태양을 한 초점으로 하는 타원 궤도를 따라 공전한다. 태양에서 근일점까지의 거리는 %d억 km, 원일점까지의 거리는 %d억 km이다. ' % (dp, da)
        if up:
            body = P(base + '근일점에서 행성의 속력이 %d km/s일 때, 원일점에서 행성의 속력은?' % vp)
            right, ans_s = va, 'v원일'
            ws = _ws(va, [vp * n, vp * Fr(1, n * n), vp - 1, vp])
            steps = ['케플러 제2법칙(면적 속도 일정)에 의해 근일점과 원일점에서 ½rv가 같다 : %d × %d = %d × v' % (dp, vp, da),
                     'v = %d × %d ÷ %d = %d km/s' % (dp, vp, da, va)]
        else:
            body = P(base + '원일점에서 행성의 속력이 %d km/s일 때, 근일점에서 행성의 속력은?' % va)
            right = vp
            ws = _ws(vp, [va * n * n, va, Fr(va, n), va * (n - 1) if n > 2 else va * 5])
            steps = ['케플러 제2법칙에 의해 근일점과 원일점에서 rv가 같다 : %d × v = %d × %d' % (dp, da, va),
                     'v = %d × %d ÷ %d = %d km/s' % (da, va, dp, vp)]
        return mc(body, '%s km/s' % _F(right), ['%s km/s' % w for w in ws], r=r, lv='하' if up else '중', fam='a', sort='num', steps=steps,
                  core='행성과 태양을 잇는 선이 같은 시간에 쓸고 지나가는 면적은 일정하므로, 근일점·원일점에서는 거리와 속력의 곱이 같다.',
                  point='근일점·원일점에서 거리와 속력이 반비례함을 이용한다.')
    if fam == 'b':
        n = r.choice([2, 3, 4, 5, 6, 7])
        e = (n - 1) / (n + 1)
        d1 = r.randint(1, 4)
        d2 = n * d1
        fig = FIG(_orbit(e, labp='%d AU' % d1, labq='%d AU' % d2, dots=[('P', 'P'), ('Q', 'Q')]), '70%')
        what = r.choice(['v', 'w', 'w', 'S'])
        if what == 'v':
            q = '근일점 P, 원일점 Q에서 행성의 속력을 각각 v%s, v%s라 할 때 v%s : v%s는?' % (sub('P'), sub('Q'), sub('P'), sub('Q'))
            right = _rt(n, 1)
            wr = [_rt(1, n), _rt(n * n, 1), _rt(1, n * n), '1 : 1']
            steps = ['면적 속도가 일정하므로 ½ × %d × v%s = ½ × %d × v%s이다.' % (d1, sub('P'), d2, sub('Q')),
                     'v%s : v%s = %d : %d = %s' % (sub('P'), sub('Q'), d2, d1, right)]
            lv = '중'
        elif what == 'w':
            q = '근일점 P, 원일점 Q에서 태양을 중심으로 한 행성의 각속도를 각각 ω%s, ω%s라 할 때 ω%s : ω%s는? (단, P, Q에서 속도는 태양과 행성을 잇는 선에 수직이다.)' % (sub('P'), sub('Q'), sub('P'), sub('Q'))
            right = _rt(n * n, 1)
            wr = [_rt(n, 1), _rt(1, n), _rt(1, n * n), '1 : 1']
            steps = ['v = rω이고 rv가 일정하므로 r²ω가 일정하다 : %d²ω%s = %d²ω%s' % (d1, sub('P'), d2, sub('Q')),
                     'ω%s : ω%s = %d² : %d² = %s' % (sub('P'), sub('Q'), d2, d1, right)]
            lv = '상'
        else:
            q = '행성이 근일점 P 부근에서 일정한 짧은 시간 동안 쓸고 지나간 면적을 S%s, 원일점 Q 부근에서 같은 시간 동안 쓸고 지나간 면적을 S%s라 할 때 S%s : S%s는?' % (sub('P'), sub('Q'), sub('P'), sub('Q'))
            right = '1 : 1'
            wr = [_rt(n, 1), _rt(1, n), _rt(n * n, 1), _rt(1, n * n)]
            steps = ['케플러 제2법칙에 의해 같은 시간 동안 쓸고 지나가는 면적은 항상 같다.', 'S%s : S%s = 1 : 1' % (sub('P'), sub('Q'))]
            lv = '하'
        body = P('그림은 태양을 한 초점으로 하는 행성의 타원 궤도를 나타낸 것이다. 태양에서 P, Q까지의 거리는 각각 %d AU, %d AU이다. ' % (d1, d2) + q) + fig
        return mc(body, right, wr, r=r, lv=lv, fam='b', sort='shuf', steps=steps,
                  core='면적 속도 일정 : 근일점·원일점에서 r × v 가 같다.', point='궤도 그림에서 거리를 읽고 속력(각속도)의 비로 바꾼다.')
    if fam == 'c':
        n = r.choice([2, 3, 4, 5])
        e = (n - 1) / (n + 1)
        s1 = r.randint(1, 4)
        rho = r.choice([Fr(1, 2), Fr(3, 2), 2, 3, 4, Fr(5, 2), Fr(1, 1)])
        s2 = s1 * rho
        # 두 부채꼴을 실제 넓이 비로 그린다
        phi1 = 0.42
        A1 = _wedge_area(e, -phi1, phi1)
        target = A1 * float(rho)
        lo, hi = 0.01, 1.5
        if _wedge_area(e, math.pi - hi, math.pi + hi) < target: return None
        for _ in range(60):
            mid = (lo + hi) / 2
            if _wedge_area(e, math.pi - mid, math.pi + mid) < target: lo = mid
            else: hi = mid
        phi2 = lo
        assert abs(_wedge_area(e, math.pi - phi2, math.pi + phi2) / A1 - float(rho)) < 1e-3
        cols = ('#cfe2f7', '#fde3b0')
        sec = [(-phi1, phi1, cols[0], '(가)'), (math.pi - phi2, math.pi + phi2, cols[1], '(나)')]
        fig = FIG(_orbit(e, sectors=sec), '70%')
        t1 = r.choice([1, 2, 3, 4, 6]) 
        t2 = Fr(t1) * rho
        if t2.denominator not in (1, 2): return None
        mode = r.choice(['t', 't', 'S'])
        a1, a2 = Fr(s1), Fr(s2)
        if mode == 't':
            body = P('그림은 태양을 한 초점으로 하는 행성의 타원 궤도를 나타낸 것이다. 행성이 (가) 구간을 지나는 동안 태양과 행성을 잇는 선이 쓸고 지나간 넓이는 %sS, (나) 구간을 지나는 동안 쓸고 지나간 넓이는 %sS이다. 행성이 (가) 구간을 지나는 데 걸린 시간이 %d개월일 때, (나) 구간을 지나는 데 걸린 시간은?' % (_F(a1), _F(a2), t1)) + fig
            ws = _ws(t2, [t1 / rho, t1, t1 * rho * rho, t1 + (a2 - a1)])
            return mc(body, '%s개월' % _F(t2), ['%s개월' % w for w in ws], r=r, lv='상', fam='c', sort='num',
                      steps=['면적 속도가 일정하므로 걸린 시간은 쓸고 지나간 넓이에 비례한다.', '%d개월 : t = %sS : %sS 이므로 t = %d × %s ÷ %s = %s개월' % (t1, _F(a1), _F(a2), t1, _F(a2), _F(a1), _F(t2))],
                      core='행성이 쓸고 지나가는 넓이는 걸린 시간에 비례한다(케플러 제2법칙).', point='같은 시간에는 같은 넓이를 쓸고 지나간다.')
        else:
            body = P('그림은 태양을 한 초점으로 하는 행성의 타원 궤도를 나타낸 것이다. 행성이 (가) 구간과 (나) 구간을 지나는 데 걸린 시간은 각각 %d개월, %s개월이다. (가) 구간에서 태양과 행성을 잇는 선이 쓸고 지나간 넓이가 %sS일 때, (나) 구간에서 쓸고 지나간 넓이는?' % (t1, _F(t2), _F(a1))) + fig
            ws = _ws(a2, [a1 / rho, a1, a2 * rho, a1 + (t2 - t1)])
            return mc(body, '%sS' % _F(a2), ['%sS' % w for w in ws], r=r, lv='중', fam='c', sort='num',
                      steps=['넓이는 걸린 시간에 비례한다 : S%s : S%s = %d : %s' % (sub('가'), sub('나'), t1, _F(t2)), 'S%s = %s × %s ÷ %d = %sS' % (sub('나'), _F(a1), _F(t2), t1, _F(a2))],
                      core='행성이 쓸고 지나가는 넓이는 걸린 시간에 비례한다.', point='시간과 넓이의 정비례 관계로 구한다.')
    if fam == 'd':
        T = r.choice([12, 24, 36, 60, 48, 18])
        t = r.choice([x for x in (1, 2, 3, 4, 5, 6, 8, 9, 10) if x < T and (T % x == 0 or (x * 10) % T == 0 or True)])
        A = r.choice([6, 8, 10, 12, 15, 20, 24, 30])
        S = Fr(A * t, T)
        if S.denominator not in (1, 2, 4, 5): return None
        body = P('행성이 태양을 한 초점으로 하는 타원 궤도를 따라 공전한다. 이 행성의 공전 주기는 %d개월이고, 궤도(타원)로 둘러싸인 부분의 넓이는 %d×10%s km²이다. 이 행성과 태양을 잇는 선이 %d개월 동안 쓸고 지나가는 넓이는?' % (T, A, sup(16), t))
        ws = _ws(S, [Fr(A, 1) * Fr(T, t), Fr(A, 2), Fr(A * t * t, T), Fr(A * (T - t), T)])
        return mc(body, '%s×10%s km²' % (_F(S), sup(16)), ['%s×10%s km²' % (w, sup(16)) for w in ws], r=r, lv='중', fam='d', sort='num',
                  steps=['면적 속도는 일정하다 : 타원 전체 넓이 %d×10¹⁶ km²를 %d개월 동안에 한 바퀴 쓸고 지나간다.' % (A, T), '%d개월 동안의 넓이 = %d × %d/%d = %s×10¹⁶ km²' % (t, A, t, T, _F(S))],
                  core='면적 속도 = (타원의 넓이) ÷ (공전 주기)로 일정하다.', point='걸린 시간에 비례하여 넓이가 결정된다.')
    # e: 면적 속도 계산
    dp = r.randint(1, 8)
    vp = r.choice([10, 12, 15, 16, 20, 24, 25, 30, 40])
    n = r.choice([2, 4, 5])
    if vp % n: return None
    da = dp * n
    va = vp // n
    ar = Fr(dp * vp, 2)
    assert Fr(da * va, 2) == ar
    up = r.choice([True, False])
    if up:
        body = P('행성이 태양 둘레를 타원 궤도로 공전한다. 근일점에서 태양까지의 거리는 %d×10%s km이고 이때 속력은 %d km/s이다. 이 행성과 태양을 잇는 선이 단위 시간 동안 쓸고 지나가는 넓이(면적 속도)는? (단, 근일점에서 속도는 태양과 행성을 잇는 선에 수직이다.)' % (dp, sup(7), vp))
        ws = _ws(ar, [dp * vp, Fr(dp * vp, 4), dp + vp, dp * vp * 2])
        return mc(body, '%s×10%s km²/s' % (_F(ar), sup(7)), ['%s×10%s km²/s' % (w, sup(7)) for w in ws], r=r, lv='중', fam='e', sort='num',
                  steps=['근일점에서 속도가 반지름에 수직이므로 단위 시간 동안 쓸고 지나가는 넓이는 삼각형 넓이 ½ × r × v이다.', '½ × %d×10⁷ × %d = %s×10⁷ km²/s' % (dp, vp, _F(ar))],
                  core='면적 속도 = ½rv (속도가 반지름에 수직일 때)이며 궤도 전체에서 일정하다.', point='근일점(또는 원일점)에서 면적 속도를 ½rv로 구한다.')
    body = P('행성이 태양 둘레를 타원 궤도로 공전한다. 근일점에서 태양까지의 거리는 %d×10%s km이고 이때 속력은 %d km/s이다. 원일점에서 태양까지의 거리가 %d×10%s km일 때, 원일점에서 행성의 속력은? (단, 근일점과 원일점에서 속도는 태양과 행성을 잇는 선에 수직이다.)' % (dp, sup(7), vp, da, sup(7)))
    ws = _ws(va, [vp * n, vp, Fr(vp, n * n), vp - va])
    return mc(body, '%s km/s' % _F(va), ['%s km/s' % w for w in ws], r=r, lv='하', fam='e', sort='num',
              steps=['근일점과 원일점에서 면적 속도 ½rv가 같다 : %d × %d = %d × v' % (dp, vp, da), 'v = %d × %d ÷ %d = %d km/s' % (dp, vp, da, va)],
              core='면적 속도 ½rv 일정 → 거리와 속력은 반비례한다.', point='원일점에서는 속력이 느려진다.')


# ================================================================== ph043
_PQ = [(1, 2), (2, 1), (1, 3), (3, 1), (1, 4), (4, 1), (2, 3), (3, 2), (1, 5), (5, 1), (3, 4), (4, 3), (2, 5), (5, 2)]


@T('ph043')
def kepler3(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        p, q = r.choice(_PQ)
        ask = r.choice(['T', 'a'])
        if ask == 'T':
            body = P('같은 별 둘레를 공전하는 행성 A, B의 공전 궤도 긴반지름의 비가 a%s : a%s = %d : %d 이다. 공전 주기의 비 T%s : T%s는?' % (sub('A'), sub('B'), p * p, q * q, sub('A'), sub('B')))
            right = _rt(p ** 3, q ** 3)
            wr = _rts(right, [_rt(p * p, q * q), _rt(p, q), _rt(q ** 3, p ** 3), _rt(p ** 4, q ** 4), _rt(q * q, p * p)])
            steps = ['케플러 제3법칙 : T² ∝ a³ 이므로 T ∝ a^(3/2)이다.', 'T%s : T%s = (%d²)^(3/2) : (%d²)^(3/2) = %d : %d' % (sub('A'), sub('B'), p, q, p ** 3, q ** 3)]
        else:
            body = P('같은 별 둘레를 공전하는 행성 A, B의 공전 주기의 비가 T%s : T%s = %d : %d 이다. 공전 궤도 긴반지름의 비 a%s : a%s는?' % (sub('A'), sub('B'), p ** 3, q ** 3, sub('A'), sub('B')))
            right = _rt(p * p, q * q)
            wr = _rts(right, [_rt(p ** 3, q ** 3), _rt(p, q), _rt(q * q, p * p), _rt(p ** 4, q ** 4), _rt(p ** 6, q ** 6)])
            steps = ['케플러 제3법칙 : a³ ∝ T² 이므로 a ∝ T^(2/3)이다.', 'a%s : a%s = (%d³)^(2/3) : (%d³)^(2/3) = %d : %d' % (sub('A'), sub('B'), p, q, p * p, q * q)]
        return mc(body, right, wr, r=r, lv='중', fam='a', sort='shuf', steps=steps,
                  core='행성의 공전 주기의 제곱은 궤도 긴반지름의 세제곱에 비례한다(T² ∝ a³).', point='제곱·세제곱 관계를 비로 바꿔 계산한다.')
    if fam == 'b':
        s = r.choice([2, 3, 4, 5, 6, 7, 8])
        ask = r.choice(['T', 'a'])
        if ask == 'T':
            body = P('태양 둘레를 도는 소행성의 공전 궤도 긴반지름이 %d AU이다. 이 소행성의 공전 주기는? (단, 지구의 공전 궤도 긴반지름은 1 AU, 공전 주기는 1년이다.)' % (s * s))
            right = s ** 3
            ws = _ws(right, [s * s, s ** 4, s, s ** 3 * 2 if s < 6 else s * 3, s * s * s // 2 if (s ** 3) % 2 == 0 else s ** 3 + 5])
            steps = ['T² = a³ (단위: 년, AU) 이므로 T² = %d³ = %d' % (s * s, s ** 6), 'T = %d년' % right]
            return mc(body, '%d년' % right, ['%s년' % w for w in ws], r=r, lv='하', fam='b', sort='num', steps=steps,
                      core='태양 둘레를 도는 천체는 T²=a³ (T: 년, a: AU)을 만족한다.', point='지구를 기준으로 하면 T²=a³이다.')
        body = P('태양 둘레를 도는 혜성이 있다. 이 혜성의 공전 주기가 %d년일 때 공전 궤도의 긴반지름은? (단, 지구의 공전 궤도 긴반지름은 1 AU, 공전 주기는 1년이다.)' % (s ** 3))
        right = s * s
        ws = _ws(right, [s ** 3, s, s ** 6, s ** 3 // 2 if s % 2 == 0 else s * 2, s * s * 2])
        steps = ['T² = a³ 에서 a³ = %d² = %d' % (s ** 3, s ** 6), 'a = %d AU' % right]
        return mc(body, '%d AU' % right, ['%s AU' % w for w in ws], r=r, lv='하', fam='b', sort='num', steps=steps,
                  core='태양 둘레를 도는 천체는 T²=a³ (T: 년, a: AU)을 만족한다.', point='주기의 제곱을 세제곱근하여 긴반지름을 구한다.')
    if fam == 'c':
        s = r.choice([2, 3, 4, 5])
        tot = 2 * s * s
        rp = r.choice([x for x in range(1, s * s) if x != s * s])
        ra = tot - rp
        if rp >= s * s: return None
        e = (ra - rp) / (ra + rp)
        if e > 0.8: return None
        fig = FIG(_orbit(e, labp='%d AU' % rp, labq='%d AU' % ra, dots=[('P', 'P'), ('Q', 'Q')]), '70%')
        ask = r.choice(['T', 'ra'])
        if ask == 'T':
            body = P('그림은 태양을 한 초점으로 하는 어떤 혜성의 타원 궤도를 나타낸 것이다. 태양에서 근일점 P, 원일점 Q까지의 거리는 각각 %d AU, %d AU이다. 이 혜성의 공전 주기는? (단, 지구의 공전 궤도 긴반지름은 1 AU, 공전 주기는 1년이다.)' % (rp, ra)) + fig
            ws = _ws(s ** 3, [tot, tot * tot, s * s, s ** 4, (tot // 2) ** 2])
            steps = ['긴반지름 a = (근일점 거리 + 원일점 거리) ÷ 2 = (%d + %d) ÷ 2 = %d AU' % (rp, ra, s * s), 'T² = a³ = %d이므로 T = %d년' % (s ** 6, s ** 3)]
            return mc(body, '%d년' % s ** 3, ['%s년' % w for w in ws], r=r, lv='상', fam='c', sort='num', steps=steps,
                      core='타원 궤도의 긴반지름은 근일점 거리와 원일점 거리의 평균이며 T²=a³이다.', point='타원의 긴반지름 = (근일점+원일점)/2')
        body = P('그림은 태양을 한 초점으로 하는 어떤 혜성의 타원 궤도를 나타낸 것이다. 태양에서 근일점 P까지의 거리는 %d AU이고 이 혜성의 공전 주기는 %d년이다. 태양에서 원일점 Q까지의 거리는? (단, 지구의 공전 궤도 긴반지름은 1 AU, 공전 주기는 1년이다.)' % (rp, s ** 3)) + fig
        ws = _ws(ra, [s * s, s * s - rp, s ** 3 - rp, tot, 2 * s * s + rp])
        steps = ['T² = a³ 에서 a³ = %d²이므로 a = %d AU' % (s ** 3, s * s), '2a = 근일점 거리 + 원일점 거리이므로 원일점 거리 = 2 × %d - %d = %d AU' % (s * s, rp, ra)]
        return mc(body, '%d AU' % ra, ['%s AU' % w for w in ws], r=r, lv='상', fam='c', sort='num', steps=steps,
                  core='긴반지름 a = (근일점 거리 + 원일점 거리)/2 이고 T²=a³이다.', point='주기에서 긴반지름을 구한 뒤 원일점 거리를 찾는다.')
    if fam == 'd':
        s = r.choice([2, 3, 4, 5])
        a1 = r.choice([1, 2, 3, 4, 5, 6])
        T1 = r.choice([1, 2, 3, 4, 5, 6, 8])
        a2, T2 = a1 * s * s, T1 * s ** 3
        ask = r.choice(['T', 'a'])
        name = r.choice([('A', 'B'), ('가', '나'), ('X', 'Y')])
        if ask == 'T':
            tb = table(['행성', '긴반지름 (AU)', '공전 주기 (년)'], [[name[0], a1, T1], [name[1], a2, '?']])
            body = P('표는 같은 별 둘레를 공전하는 두 행성 %s, %s의 공전 궤도 긴반지름과 공전 주기를 나타낸 것이다. %s의 공전 주기는?' % (name[0], name[1], name[1])) + tb
            ws = _ws(T2, [T1 * s * s, T1 * s, T1 * s ** 4, T1 * (a2 // a1) ** 2])
            return mc(body, '%d년' % T2, ['%s년' % w for w in ws], r=r, lv='중', fam='d', sort='num',
                      steps=['긴반지름이 %d배(%d AU → %d AU)이므로 T² ∝ a³에서 주기는 %d^(3/2) = %d배이다.' % (s * s, a1, a2, s * s, s ** 3), 'T = %d × %d = %d년' % (T1, s ** 3, T2)],
                      core='같은 별을 도는 행성은 T²/a³이 같다.', point='긴반지름이 n²배이면 주기는 n³배이다.')
        tb = table(['행성', '긴반지름 (AU)', '공전 주기 (년)'], [[name[0], a1, T1], [name[1], '?', T2]])
        body = P('표는 같은 별 둘레를 공전하는 두 행성 %s, %s의 공전 궤도 긴반지름과 공전 주기를 나타낸 것이다. %s의 긴반지름은?' % (name[0], name[1], name[1])) + tb
        ws = _ws(a2, [a1 * s ** 3, a1 * s, a1 * s ** 4, a1 * s * s * 2])
        return mc(body, '%d AU' % a2, ['%s AU' % w for w in ws], r=r, lv='중', fam='d', sort='num',
                  steps=['주기가 %d배이므로 T² ∝ a³에서 긴반지름은 (%d²)^(1/3) = %d배이다.' % (s ** 3, s ** 3, s * s), 'a = %d × %d = %d AU' % (a1, s * s, a2)],
                  core='같은 별을 도는 행성은 T²/a³이 같다.', point='주기가 n³배이면 긴반지름은 n²배이다.')
    # e: 원궤도와 타원 궤도의 주기 비교
    q = r.choice([Fr(1, 2), Fr(2, 1), Fr(3, 1), Fr(3, 2), Fr(2, 3), Fr(1, 3)])
    rc = r.choice([1, 2, 3, 4, 6, 8, 9, 12])
    aB = rc * q * q
    if (2 * aB).denominator != 1: return None
    tot = int(2 * aB)
    rp = r.randint(1, tot - 1)
    ra = tot - rp
    if rp >= aB or ra <= aB: return None
    Tc = r.choice([2, 3, 4, 5, 6, 8, 10])
    TB = Fr(Tc) * q ** 3
    if TB.denominator not in (1, 2, 4): return None
    body = P('어떤 별 둘레를 위성 A는 반지름이 %d AU인 원 궤도로, 위성 B는 근일점 거리 %d AU, 원일점 거리 %d AU인 타원 궤도로 공전한다. A의 공전 주기가 %d년일 때 B의 공전 주기는?' % (rc, rp, ra, Tc))
    ws = _ws(TB, [Tc * q * q, Tc * q, Tc / q ** 3, Tc * (Fr(ra, rc)) ** Fr(3, 2) if False else Tc * 2])
    return mc(body, '%s년' % _F(TB), ['%s년' % w for w in ws], r=r, lv='상', fam='e', sort='num',
              steps=['B의 긴반지름 a%s = (%d + %d) ÷ 2 = %s AU, 원 궤도 A의 반지름(긴반지름)은 %d AU이다.' % (sub('B'), rp, ra, _F(aB), rc),
                     '긴반지름의 비 a%s : a%s = %s : 1이므로 주기의 비는 (%s)^(3/2) = %s : 1' % (sub('B'), sub('A'), _fx(q * q), _fx(q * q), _fx(q ** 3)),
                     'T%s = %d × %s = %s년' % (sub('B'), Tc, _fx(q ** 3), _F(TB))],
              core='원 궤도의 반지름은 긴반지름과 같게 취급하여 T²∝a³을 적용한다.', point='타원의 긴반지름을 구해 원 궤도와 비교한다.')


# ================================================================== ph044
def _three_fig(ma, mb, mc_, d1, d2, w=300, h=120):
    f = Fig(w, h)
    y = 52
    xa = 30
    unit = 62
    xb = xa + d1 * unit
    xc = xb + d2 * unit
    f.line(xa, y, xc, y, GR, 1, '3 3')
    for x, m_, nm_, col in ((xa, ma, 'A', RD), (xb, mb, 'B', GN), (xc, mc_, 'C', BL)):
        rr = 8 + 4 * m_ ** 0.5
        f.circ(x, y, rr, col, INK, 1.4)
        f.text(x, y - rr - 7, '%s (%sm)' % (nm_, m_ if m_ != 1 else ''), 13, 'middle', True, INK)
    for (x1, x2, d) in ((xa, xb, d1), (xb, xc, d2)):
        yy = 98
        f.line(x1, yy, x2, yy, INK, 1.2); f.line(x1, yy - 4, x1, yy + 4); f.line(x2, yy - 4, x2, yy + 4)
        f.text((x1 + x2) / 2, yy + 16, '%sd' % (d if d != 1 else ''), 13, 'middle', True, GR)
    return f.svg()


@T('ph044')
def grav_force(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'd', 'd', 'e'])
    if fam == 'a':
        kA = r.choice([1, 1, 2, 3, 4, Fr(1, 2)])
        kB = r.choice([1, 2, 3, Fr(1, 2), Fr(1, 3), 1])
        n = r.choice([Fr(1, 2), 2, 3, 4, Fr(3, 2), Fr(1, 3), 5])
        fac = Fr(kA) * Fr(kB) / (n * n)
        if fac == 1: return None
        change = []
        if kA != 1: change.append('질량 m%s을 %s배로' % (sub('A'), _fx(kA)))
        if kB != 1: change.append('질량 m%s를 %s배로' % (sub('B'), _fx(kB)))
        change.append('두 물체 사이의 거리를 %s배로' % _fx(n))
        txt = '하고, '.join(change)
        numeric = r.choice([True, False])
        base = '질량이 각각 m%s, m%s인 두 물체가 거리 r만큼 떨어져 있을 때 두 물체 사이에 작용하는 만유인력의 크기가 F이다. ' % (sub('A'), sub('B'))
        if numeric and (fac * 36).denominator == 1:
            F0 = r.choice([4, 8, 12, 16, 24, 36])
            F1 = fac * F0
            if F1.denominator not in (1, 2, 4): return None
            body = P(base.replace('이 F이다', '이 %d N이다' % F0) + txt + ' 바꾸면 만유인력의 크기는?')
            ws = _ws(F1, [F0 * kA * kB, F0 / (n * n), F0 * n * n, F0 * kA * kB / n, F0 * kA * kB * n])
            return mc(body, '%s N' % _F(F1), ['%s N' % w for w in ws], r=r, lv='하' if kA == kB == 1 else '중', fam='a', sort='num',
                      steps=['F = Gm%sm%s/r² 이므로 새로운 힘은 %s × %s ÷ %s² 배이다.' % (sub('A'), sub('B'), _fx(kA), _fx(kB), _fx(n)), 'F\' = %d × %s = %s N' % (F0, _fx(fac), _F(F1))],
                      core='만유인력은 두 질량의 곱에 비례하고 거리의 제곱에 반비례한다.', point='질량 변화는 곱하고, 거리 변화는 제곱의 역수로 반영한다.')
        body = P(base + txt + ' 바꾸면 만유인력의 크기는?')
        right = _fm(fac, 'F')
        cands = [kA * kB / n, kA * kB * n * n, kA * kB * n, 1 / (kA * kB * n * n), kA * kB / (2 * n), fac * 2, fac / 2]
        ws = [_fm(Fr(c).limit_denominator(1000), 'F') for c in cands]
        ws = [w for w in dict.fromkeys(ws) if w != right]
        return mc(body, right, ws[:5], r=r, lv='하' if kA == kB == 1 else '중', fam='a', sort='shuf',
                  steps=['F = Gm%sm%s/r² 이므로 질량 곱이 %s배, r²이 %s배가 된다.' % (sub('A'), sub('B'), _fx(Fr(kA) * Fr(kB)), _fx(n * n)), '새로운 힘 = %s × F ÷ %s = %sF' % (_fx(Fr(kA) * Fr(kB)), _fx(n * n), _fx(fac))],
                  core='만유인력은 두 질량의 곱에 비례하고 거리의 제곱에 반비례한다.', point='질량·거리 변화를 각각 반영한 배율을 곱한다.')
    if fam == 'b':
        ma, mb, mc_ = r.choice([1, 2, 3, 4]), r.choice([1, 2]), r.choice([1, 2, 3, 4])
        d1, d2 = r.choice([1, 2]), r.choice([1, 2])
        FA = Fr(ma * mb, d1 * d1)
        FC = Fr(mc_ * mb, d2 * d2)
        net = FC - FA  # +이면 오른쪽(C 쪽)
        if net == 0 and r.random() < .7: return None
        fig = FIG(_three_fig(ma, mb, mc_, d1, d2), '68%')
        body = P('그림은 일직선 위에 놓인 세 구형 물체 A, B, C를 나타낸 것이다. A, B, C의 질량은 각각 %sm, %sm, %sm이고 A와 B 사이의 거리는 %sd, B와 C 사이의 거리는 %sd이다. 질량 m인 두 물체가 거리 d만큼 떨어져 있을 때 서로 당기는 만유인력의 크기를 F0이라 할 때, B가 A와 C로부터 받는 알짜 만유인력의 방향과 크기는? (단, 다른 천체의 영향은 무시한다.)' % ('' if ma == 1 else ma, '' if mb == 1 else mb, '' if mc_ == 1 else mc_, '' if d1 == 1 else d1, '' if d2 == 1 else d2)) + fig
        def fmt(v):
            if v == 0: return '0'
            return ('오른쪽 ' if v > 0 else '왼쪽 ') + _fm(abs(v), 'F0')
        right = fmt(net)
        cands = [-net, FA + FC, FA, FC, net * 2, Fr(ma * mb) + Fr(mc_ * mb), net / 2]
        ws = []
        for c in cands:
            s = fmt(Fr(c).limit_denominator(100))
            if s != right and s not in ws: ws.append(s)
        for extra in (Fr(1, 4), Fr(3, 4), Fr(5, 4), Fr(1, 2), Fr(3, 2), 2):
            for sg in (1, -1):
                s = fmt(sg * extra)
                if s != right and s not in ws: ws.append(s)
        ws = ws[:5]
        steps = ['A가 B를 당기는 힘 = F0 × (%sm × %sm)/(%sd)² ÷ (m²/d²) = %sF0 (왼쪽)' % (ma, mb, d1, _F(FA)),
                 'C가 B를 당기는 힘 = %sF0 (오른쪽)' % _F(FC),
                 '알짜힘 = |%s - %s|F0 = %sF0, 방향은 힘이 더 큰 쪽(%s)이다.' % (_F(FC), _F(FA), _F(abs(net)), '오른쪽' if net > 0 else '왼쪽') if net != 0 else '두 힘의 크기가 같고 방향이 반대이므로 알짜힘은 0이다.']
        return mc(body, right, ws, r=r, lv='상', fam='b', sort='shuf', steps=steps,
                  core='만유인력은 각 천체가 따로 작용하고, 같은 직선 위에서는 방향을 고려해 벡터로 합한다.', point='두 힘을 각각 구한 뒤 방향을 따져 합한다.')
    if fam == 'c':
        pq = r.choice([(1, 2), (1, 3), (2, 3), (1, 4), (2, 1), (3, 1), (3, 2), (1, 5), (4, 1)])
        p, q = pq
        tot = p + q
        d = tot * r.choice([1, 2, 3, 4])
        x = Fr(d * p, tot)
        # 질량 p^2 M(왼쪽) , q^2 M(오른쪽): 영점은 왼쪽에서 d·p/(p+q)
        f = Fig(300, 110)
        xa, xb = 35, 265
        f.line(xa, 60, xb, 60, GR, 1, '3 3')
        for xx, m_, nm_, col in ((xa, p * p, 'A', RD), (xb, q * q, 'B', BL)):
            rr = 8 + 4 * m_ ** 0.5
            f.circ(xx, 60, rr, col, INK, 1.4)
            f.text(xx, 60 - rr - 8, '%s (%sM)' % (nm_, m_ if m_ != 1 else ''), 13, 'middle', True, INK)
        f.line(xa, 96, xb, 96); f.line(xa, 92, xa, 100); f.line(xb, 92, xb, 100)
        f.text((xa + xb) / 2, 106, '%d m' % d, 12.5, 'middle', True, GR)
        xp = xa + (xb - xa) * float(x) / d
        f.circ(xp, 60, 4, OR, INK, 1); f.text(xp, 80, 'P', 13, 'middle', True, GR)
        MA, MB = p * p, q * q
        assert abs(MA / float(x) ** 2 - MB / (d - float(x)) ** 2) < 1e-9
        body = P('그림과 같이 질량이 각각 %sM, %sM인 구형 물체 A, B가 %d m 떨어져 있다. A와 B를 잇는 직선 위의 점 P에 작은 물체를 놓았을 때, 이 물체에 작용하는 A, B의 만유인력의 합력이 0이 되었다. P는 A로부터 몇 m 떨어진 곳인가? (단, 다른 천체의 영향은 무시한다.)' % ('' if MA == 1 else MA, MB, d)) + FIG(f.svg(), '66%')
        ws = _ws(x, [Fr(d * MA, MA + MB), Fr(d, 2), d - x, Fr(d * q, tot), Fr(d * MB, MA + MB)], lambda c: _F(c) + ' m')
        return mc(body, '%s m' % _F(x), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['P가 A로부터 x 떨어져 있다고 하면 G(%sM)m/x² = G(%sM)m/(%d-x)²이다.' % (MA, MB, d), '양변의 제곱근을 취하면 %d/x = %d/(%d-x) 이므로 x = %d × %d ÷ %d = %s m' % (p, q, d, d, p, tot, _F(x))],
                  core='두 천체의 만유인력이 같으려면 거리는 √(질량)에 비례한다(질량이 큰 쪽에서 더 멀다).', point='합력이 0인 지점은 질량의 제곱근비로 거리를 나눈다.')
    if fam == 'd':
        r0 = r.choice([1, 2, 3, 4])
        F0 = r.choice([36, 72, 144, 18, 48, 96, 16, 32, 64])
        mult = r.choice([2, 3, 4, Fr(1, 2)])
        Fm = Fr(F0) / (mult * mult)
        if (Fm * 100).denominator != 1: return None
        pl = Plot(300, 215, 4.4, 4.6 * 1, xmin=0, ymin=0, ml=48, mb=32)
        # 세로축은 F/F0 단위(ymax 4.6)
        def yfmt(v):
            return {0: '0', 1: _F(F0), 2: _F(F0 * 2), 4: _F(F0 * 4)}.get(v, '')
        pl.axes('r (m)', 'F (N)', xticks=[1, 2, 3, 4], yticks=[1, 2, 4], xfmt=lambda v: _F(v * r0), yfmt=yfmt, grid=True)
        pts = [(x / 20, 1 / (x / 20) ** 2) for x in range(10, 89) if 1 / (x / 20) ** 2 <= 4.4]
        pl.pl(pts, BL, 2.4)
        pl.dash_to_axes(1, 1, RD)
        pl.circ(pl.px(1), pl.py(1), 4, RD, INK, 1)
        pl.text(pl.px(1) + 10, pl.py(1) - 9, 'P', 13, 'start', True, RD)
        if mult == Fr(1, 2):
            tx = '%s m' % _F(r0 * Fr(1, 2)); rr = Fr(1, 2)
        else:
            tx = '%s m' % _F(r0 * mult); rr = mult
        body = P('그림은 질량이 일정한 두 구형 물체 사이에 작용하는 만유인력의 크기 F를 두 물체 중심 사이의 거리 r에 따라 나타낸 것이다. 점 P는 r = %s m일 때 F = %s N임을 나타낸다. r = %s일 때 만유인력의 크기는?' % (_F(r0), _F(F0), tx)) + FIG(pl.svg(), '66%')
        F1 = Fr(F0) / (rr * rr)
        ws = _ws(F1, [Fr(F0) / rr, Fr(F0) * rr, Fr(F0) * rr * rr, Fr(F0) / (rr ** 3)], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(F1), ws, r=r, lv='중', fam='d', sort='num',
                  steps=['만유인력의 크기는 거리의 제곱에 반비례한다(F ∝ 1/r²).', '거리가 %s배가 되므로 힘은 1/%s배 : %s × %s = %s N' % (_fx(rr), _fx(rr * rr), _F(F0), _fx(1 / (rr * rr)), _F(F1))],
                  core='F ∝ 1/r² 이므로 F-r 그래프는 거리가 커질수록 급격히 감소하는 곡선이다.', point='그래프의 기준점에서 거리 배율의 제곱으로 힘을 구한다.')
    # e: 작용 반작용 / 지구와 물체
    m = r.choice([0.5, 1, 2, 3, 4, 5, 8, 10])
    who = r.choice([('사과', '지구'), ('공', '지구'), ('책', '지구')])
    Fv = m * G
    body = P('질량 %s kg인 %s이(가) 지표면 가까이에서 %s에 의해 받는 중력의 크기는 mg이다. %s이(가) %s를 당기는 만유인력의 크기는? (단, g = 10 m/s²이다.)' % (_F(m), who[0], who[1], who[0], who[1]))
    ws = _ws(Fv, [m, Fv * 10, Fv / 10, 0.1, Fv * 6], lambda c: _F(c) + ' N')
    ws = [w for w in ws if w != '0 N']
    return mc(body, '%s N' % _F(Fv), ws, r=r, lv='하', fam='e', sort='num',
              steps=['%s이(가) 받는 중력의 크기 = mg = %s × 10 = %s N' % (who[0], _F(m), _F(Fv)), '작용 반작용 법칙에 의해 %s이(가) %s를 당기는 힘의 크기도 %s N이다.' % (who[0], who[1], _F(Fv))],
              core='두 물체 사이의 만유인력은 작용 반작용 관계이므로 크기가 같고 방향이 반대이다.', point='질량이 달라도 서로 당기는 힘의 크기는 같다.')


# ================================================================== ph045
def _earth_fig(kR, w=300, h=180, lab='R'):
    """지구 중심 O, 지표면의 점 A, 높이 h 의 점 B(거리 kR 만큼 위)."""
    f = Fig(w, h)
    R = 42
    cx, cy = 55, 100
    f.circ(cx, cy, R, '#cfe2f7', INK, 1.6)
    f.circ(cx, cy, 2.5, INK)
    f.text(cx - 2, cy + 16, 'O', 12, 'middle', c=GR)
    f.line(cx, cy, cx + R, cy, GR, 1.2)
    f.text(cx + R / 2 + 2, cy - 6, 'R', 12.5, 'middle', True, GR)
    xb = cx + R + 30 + 22 * kR
    xb = min(xb, 280)
    f.line(cx + R, cy, xb, cy, RD, 1.4, '4 3')
    f.circ(cx + R, cy, 4.5, OR, INK, 1); f.text(cx + R + 4, cy + 17, 'A', 13, 'middle', True)
    f.circ(xb, cy, 5, BL, INK, 1); f.text(xb, cy + 18, 'B', 13, 'middle', True)
    f.line(cx + R, cy - 22, xb, cy - 22); f.line(cx + R, cy - 26, cx + R, cy - 18); f.line(xb, cy - 26, xb, cy - 18)
    f.text((cx + R + xb) / 2, cy - 29, 'h = %s' % _rs(Fr(kR).limit_denominator(100)), 12.5, 'middle', True, RD)
    return f.svg()


@T('ph045')
def g_height(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if fam == 'a':
        kR = r.choice([1, 2, 3, Fr(1, 2), Fr(1, 3), 4, 5, Fr(2, 1)])
        ask = r.choice(['g', 'g', 'h'])
        fac = 1 / (1 + Fr(kR)) ** 2
        fig = FIG(_earth_fig(float(kR)), '64%')
        if ask == 'g':
            body = P('그림은 지구(반지름 R)와 지표면의 점 A, 지표면으로부터 높이 h = %s인 점 B를 나타낸 것이다. 지표면에서의 중력 가속도의 크기를 g라 할 때, B에서의 중력 가속도의 크기는?' % _rs(kR)) + fig
            right = _fm(fac, 'g')
            cands = [1 / Fr(kR), Fr(1) / (Fr(kR) ** 2), 1 / (1 + Fr(kR)), Fr(kR) ** 2, (1 + Fr(kR)) ** 2, Fr(1, 2) * fac * 4]
            ws = [_fm(Fr(c).limit_denominator(1000), 'g') for c in cands]
            ws = [w for w in dict.fromkeys(ws) if w != right]
            return mc(body, right, ws[:5], r=r, lv='중', fam='a', sort='shuf',
                      steps=['중력 가속도 g = GM/r² 이므로 g ∝ 1/r²이다.', 'B는 지구 중심으로부터 R + %s = %s 떨어져 있으므로 g\' = g × (1/%s)² = %sg' % (_rs(kR), _rs(1 + Fr(kR)), _fx(1 + Fr(kR)), _fx(fac))],
                      core='중력 가속도는 지구 중심으로부터의 거리의 제곱에 반비례한다.', point='높이 h가 아니라 지구 중심으로부터의 거리 R+h를 쓴다.')
        # 높이를 묻기
        body = P('지표면에서의 중력 가속도의 크기를 g라 하자. 지표면으로부터 높이 h인 지점에서의 중력 가속도의 크기가 %s이다. h는? (단, 지구 반지름은 R이다.)' % _fm(fac, 'g'))
        right = _rs(kR)
        cands = [1 + Fr(kR), (1 + Fr(kR)) ** 2, (1 + Fr(kR)) ** 2 - 1, Fr(kR) ** 2, 1 / (1 + Fr(kR))]
        ws = _ws(Fr(kR), cands, _rs)
        return mc(body, right, ws, r=r, lv='중', fam='a', sort='num',
                  steps=['g\' = g(R/r)² = %sg 이므로 R/r = %s, r = %s이다.' % (_fx(fac), '1/%s' % _fx(1 + Fr(kR)), _rs(1 + Fr(kR))), 'h = r - R = %s - R = %s' % (_rs(1 + Fr(kR)), _rs(kR))],
                  core='중력 가속도 g ∝ 1/r² (r : 지구 중심으로부터의 거리).', point='r = R + h 이므로 높이는 r - R로 구한다.')
    if fam == 'b':
        Mx = r.choice([1, 2, 3, 4, 8, 9, 6])
        Rx = r.choice([1, 2, 3, Fr(1, 2), 4])
        g = Fr(Mx) / Fr(Rx) ** 2
        if (g * 10).denominator not in (1, 2) or g == 1: return None
        gp = 10 * g
        tb = table(['', '질량', '반지름'], [['지구', 'M', 'R'], ['행성 X', '%sM' % _F(Mx), '%sR' % _F(Rx)]])
        ask = r.choice(['g', 'w'])
        if ask == 'g':
            body = P('표는 지구와 행성 X의 질량과 반지름을 나타낸 것이다. 지구 표면에서의 중력 가속도가 10 m/s²일 때, 행성 X 표면에서의 중력 가속도의 크기는?') + tb
            ws = _ws(gp, [10 * Mx, 10 * Mx / Fr(Rx), 10 / Fr(Rx) ** 2, 10 * Fr(Rx) ** 2 * Mx, 10 * Mx * Fr(Rx)], lambda c: _F(c) + ' m/s²')
            return mc(body, '%s m/s²' % _F(gp), ws, r=r, lv='중', fam='b', sort='num',
                      steps=['g = GM/R² 이므로 g%s : g지구 = (%s/%s²) : 1 = %s : 1' % (sub('X'), _F(Mx), _F(Rx), _F(g)), 'g%s = 10 × %s = %s m/s²' % (sub('X'), _F(g), _F(gp))],
                      core='행성 표면의 중력 가속도는 g = GM/R²로 질량에 비례하고 반지름의 제곱에 반비례한다.', point='질량 배율을 반지름 배율의 제곱으로 나눈다.')
        m = r.choice([20, 30, 40, 50, 60])
        W = Fr(m) * gp
        body = P('표는 지구와 행성 X의 질량과 반지름을 나타낸 것이다. 지구 표면에서의 중력 가속도가 10 m/s²일 때, 질량 %d kg인 물체가 행성 X 표면에서 받는 중력(무게)의 크기는?' % m) + tb
        ws = _ws(W, [m * 10, W / 10 * 1, m * 10 * Mx, m * 10 / Fr(Rx) ** 2 if Mx != 1 else m * 20, m * gp * 2], lambda c: _F(c) + ' N')
        return mc(body, '%s N' % _F(W), ws, r=r, lv='상', fam='b', sort='num',
                  steps=['g%s = 10 × %s/%s² = %s m/s²' % (sub('X'), _F(Mx), _F(Rx), _F(gp)), '무게 = mg = %d × %s = %s N (질량은 장소에 따라 변하지 않는다.)' % (m, _F(gp), _F(W))],
                  core='물체의 무게 = 질량 × 그 장소의 중력 가속도이며 질량은 변하지 않는다.', point='먼저 행성 표면의 중력 가속도를 구한 뒤 무게를 구한다.')
    if fam == 'c':
        nn = r.choice([2, 3, 4])
        pl = Plot(300, 215, 4.4, 1.15, xmin=0, ymin=0, ml=48, mb=32)
        lab = {1: 'g₀', 0.25: 'g₀/4', 1 / 9: 'g₀/9', 1 / 16: 'g₀/16', 0.5: ''}
        pl.axes('r', 'g', xticks=[1, 2, 3, 4], yticks=[1], xfmt=lambda v: ('%dR' % v) if v > 1 else 'R', yfmt=lambda v: 'g₀', grid=True)
        pl.pl([(x / 20, 1 / (x / 20) ** 2) for x in range(20, 88)], BL, 2.4)
        pl.dash_to_axes(1, 1, RD)
        pl.circ(pl.px(1), pl.py(1), 4, RD, INK, 1)
        ask = r.choice(['g', 'g', 'r'])
        if ask == 'g':
            body = P('그림은 어떤 행성 둘레에서 중력 가속도의 크기 g를 행성 중심으로부터의 거리 r에 따라 나타낸 것이다. 행성의 반지름은 R이고, 행성 표면(r = R)에서의 중력 가속도는 g₀이다. r = %dR인 지점에서의 중력 가속도의 크기는?' % nn) + FIG(pl.svg(), '66%')
            right = _fm(Fr(1, nn * nn), 'g₀')
            ws = [_fm(Fr(c).limit_denominator(100), 'g₀') for c in (Fr(1, nn), Fr(1, nn * nn - 1), Fr(1, 2 * nn), Fr(1, nn ** 3), Fr(nn * nn))]
            ws = [w for w in dict.fromkeys(ws) if w != right]
            return mc(body, right, ws[:5], r=r, lv='하', fam='c', sort='shuf',
                      steps=['g ∝ 1/r² 이므로 r이 R에서 %dR로 %d배가 되면 g는 1/%d배가 된다.' % (nn, nn, nn * nn), 'g = g₀/%d' % (nn * nn)],
                      core='중력 가속도는 중심으로부터의 거리의 제곱에 반비례한다.', point='그래프의 기준점(r=R, g₀)에서 배율을 적용한다.')
        body = P('그림은 어떤 행성 둘레에서 중력 가속도의 크기 g를 행성 중심으로부터의 거리 r에 따라 나타낸 것이다. 행성의 반지름은 R이고, 행성 표면(r = R)에서의 중력 가속도는 g₀이다. 중력 가속도의 크기가 %s인 지점은 행성 중심으로부터 얼마나 떨어져 있는가?' % _fm(Fr(1, nn * nn), 'g₀')) + FIG(pl.svg(), '66%')
        right = '%dR' % nn
        ws = ['%sR' % x for x in (nn * nn, nn + 1, nn * 2 + 1, nn - 1 if nn > 2 else 5, 2 * nn * nn)]
        ws = [w for w in dict.fromkeys(ws) if w != right]
        return mc(body, right, ws[:5], r=r, lv='중', fam='c', sort='shuf',
                  steps=['g = g₀/%d = g₀ (R/r)² 에서 (R/r)² = 1/%d이므로 r = %dR이다.' % (nn * nn, nn * nn, nn)],
                  core='g ∝ 1/r² 이므로 g가 1/n²배이면 r은 n배이다.', point='g의 배율의 제곱근이 거리의 역수이다.')
    if fam == 'd':
        p, q = r.choice([(2, 1), (1, 2), (3, 1), (1, 3), (3, 2), (2, 3), (4, 1), (1, 4)])
        mode = r.choice(['rho', 'M'])
        if mode == 'rho':
            body = P('밀도가 같은 구형 행성 A, B의 반지름의 비가 R%s : R%s = %d : %d이다. 두 행성 표면에서의 중력 가속도의 크기의 비 g%s : g%s는?' % (sub('A'), sub('B'), p, q, sub('A'), sub('B')))
            right = _rt(p, q)
            wr = _rts(right, [_rt(q, p), _rt(p * p, q * q), _rt(q * q, p * p), _rt(p ** 3, q ** 3), '1 : 1'])
            steps = ['질량 M = 밀도 × (4/3)πR³ 이므로 g = GM/R² ∝ R이다 (밀도가 같을 때).', 'g%s : g%s = R%s : R%s = %s' % (sub('A'), sub('B'), sub('A'), sub('B'), right)]
            return mc(body, right, wr, r=r, lv='상', fam='d', sort='shuf', steps=steps,
                      core='밀도가 같은 구형 행성의 표면 중력 가속도는 반지름에 비례한다.', point='질량을 반지름의 세제곱으로 바꾸어 g = GM/R²에 대입한다.')
        body = P('질량이 같은 구형 행성 A, B의 반지름의 비가 R%s : R%s = %d : %d이다. 두 행성 표면에서의 중력 가속도의 크기의 비 g%s : g%s는?' % (sub('A'), sub('B'), p, q, sub('A'), sub('B')))
        right = _rt(q * q, p * p)
        wr = _rts(right, [_rt(p * p, q * q), _rt(q, p), _rt(p, q), _rt(q ** 3, p ** 3), '1 : 1'])
        steps = ['g = GM/R² 에서 M이 같으면 g ∝ 1/R²이다.', 'g%s : g%s = 1/%d² : 1/%d² = %s' % (sub('A'), sub('B'), p, q, right)]
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf', steps=steps,
                  core='같은 질량이면 표면 중력 가속도는 반지름의 제곱에 반비례한다.', point='반지름이 큰 행성의 표면 중력 가속도가 더 작다.')
    # e: 높이 h 에서 중력의 크기(N)
    m = r.choice([2, 4, 5, 8, 10, 20, 36, 45])
    kR = r.choice([1, 2, 3])
    F = Fr(m * G, (1 + kR) ** 2)
    if (F * 100).denominator != 1: return None
    body = P('지표면에서 질량 %d kg인 물체에 작용하는 중력의 크기는 %d N이다(g = 10 m/s²). 이 물체를 지표면으로부터 높이 %s(R: 지구 반지름)인 지점으로 옮겼을 때, 이 물체에 작용하는 중력의 크기는?' % (m, m * G, _rs(kR)))
    ws = _ws(F, [m * G / kR if kR != 1 else m * G / 2, m * G, Fr(m * G, kR * kR), m * G * (1 + kR), Fr(m * G, 1 + kR)], lambda c: _F(c) + ' N')
    return mc(body, '%s N' % _F(F), ws, r=r, lv='하', fam='e', sort='num',
              steps=['중력의 크기는 지구 중심으로부터 거리의 제곱에 반비례한다.', '거리가 R에서 %dR이 되므로 중력은 1/%d배 : %d × 1/%d = %s N' % (1 + kR, (1 + kR) ** 2, m * G, (1 + kR) ** 2, _F(F))],
              core='물체에 작용하는 중력은 F = GMm/r² 이므로 중심 거리의 제곱에 반비례한다.', point='질량은 그대로이고 중력만 감소한다.')


# ================================================================== ph046
def _sat_fig(rA, rB, w=300, h=200):
    f = Fig(w, h)
    cx, cy = w / 2, h / 2 + 4
    R = 11
    big = max(rA, rB)
    sc = 82 / big
    f.circ(cx, cy, R, '#cfe2f7', INK, 1.5)
    f.text(cx, cy + 4, '행성', 11.5, 'middle', c=GR)
    for rr, nm_, col, ang in ((rA, 'A', RD, -0.6), (rB, 'B', BL, 2.1)):
        rad_ = max(rr * sc, R + 12)
        f.circ(cx, cy, rad_, 'none', col, 1.4, '5 3')
        x, y = cx + rad_ * math.cos(ang), cy + rad_ * math.sin(ang)
        f.line(cx, cy, x, y, col, 1.2)
        f.circ(x, y, 5, col, INK, 1)
        f.text(x + 12 * math.cos(ang), y + 12 * math.sin(ang) + 5, nm_, 14, 'middle', True, INK, True)
        mx, my = cx + rad_ * .5 * math.cos(ang), cy + rad_ * .5 * math.sin(ang)
        f.text(mx + 8 * math.sin(ang) * -1 - 4, my + 8 * math.cos(ang) + 2, 'r%s' % ('A' if nm_ == 'A' else 'B'), 12, 'middle', True, col)
    return f.svg()


_QTY = {
    'v': ('속력', lambda p, q, u, w: _rt(q, p), '원운동 속력 v = √(GM/r) 이므로 v ∝ 1/√r'),
    'T': ('공전 주기', lambda p, q, u, w: _rt(p ** 3, q ** 3), '주기 T = 2πr/v ∝ r^(3/2)'),
    'a': ('구심 가속도의 크기', lambda p, q, u, w: _rt(q ** 4, p ** 4), 'a = GM/r² ∝ 1/r²'),
    'w': ('각속도', lambda p, q, u, w: _rt(q ** 3, p ** 3), 'ω = v/r ∝ r^(-3/2)'),
    'Ek': ('운동 에너지', lambda p, q, u, w: _rt(Fr(u, p * p), Fr(w, q * q)), 'E_k = ½mv² = GMm/(2r) ∝ m/r'),
    'F': ('행성이 위성에 작용하는 중력의 크기', lambda p, q, u, w: _rt(Fr(u, p ** 4), Fr(w, q ** 4)), 'F = GMm/r² ∝ m/r²'),
}


@T('ph046')
def satellite(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if fam in ('a', 'b'):
        p, q = r.choice([(1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2), (1, 4), (4, 1)] if fam == 'a' else [(1, 2), (2, 1), (2, 3), (3, 2), (1, 2), (2, 1)])
        key = r.choice(['v', 'T', 'a', 'w', 'Ek', 'F']) if fam == 'b' else r.choice(['v', 'T', 'a'])
        u, w_ = (1, 1)
        if key in ('Ek', 'F'):
            u, w_ = r.choice([(1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2)])
        nm_, fn, why = _QTY[key]
        right = fn(p, q, u, w_)
        # 오답: 다른 양의 비 + 뒤집기
        pool = []
        for kk, (n2, f2, w2) in _QTY.items():
            if kk == key: continue
            if kk in ('Ek', 'F') and key not in ('Ek', 'F'): continue
            pool.append(f2(p, q, u, w_))
        pool += [_rt(p, q), _rt(q, p), _rt(p * p, q * q), _rt(q * q, p * p)]
        a, b = right.split(' : ')
        pool.append('%s : %s' % (b, a))
        wr = _rts(right, pool)
        mass = ''
        if key in ('Ek', 'F'):
            mass = ' A, B의 질량은 각각 %dm, %dm이다.' % (u, w_)
        if fam == 'a':
            body = P('같은 행성 둘레를 원 궤도로 공전하는 인공위성 A, B의 궤도 반지름이 각각 %dr, %dr이다.%s A, B의 %s의 비 A : B는?' % (p * p, q * q, mass, nm_))
        else:
            body = P('그림은 행성 둘레를 원 궤도로 공전하는 인공위성 A, B를 나타낸 것이다. 궤도 반지름은 r%s : r%s = %d : %d 이다.%s A, B의 %s의 비 A : B는?' % (sub('A'), sub('B'), p * p, q * q, mass, nm_)) + FIG(_sat_fig(p * p, q * q), '60%')
        # 수치 검증: GM=1
        def vv(rr): return math.sqrt(1 / rr)
        rA, rB = p * p, q * q
        if key == 'v': chk = vv(rA) / vv(rB); assert abs(chk - q / p) < 1e-9
        if key == 'T': chk = (2 * math.pi * rA / vv(rA)) / (2 * math.pi * rB / vv(rB)); assert abs(chk - p ** 3 / q ** 3) < 1e-9
        if key == 'a': chk = (1 / rA ** 2) / (1 / rB ** 2); assert abs(chk - q ** 4 / p ** 4) < 1e-9
        if key == 'w': chk = (vv(rA) / rA) / (vv(rB) / rB); assert abs(chk - q ** 3 / p ** 3) < 1e-9
        if key == 'Ek': chk = (0.5 * u * vv(rA) ** 2) / (0.5 * w_ * vv(rB) ** 2); assert abs(chk - (u / rA) / (w_ / rB)) < 1e-9
        steps = ['%s이므로' % why, 'r%s : r%s = %d : %d (= %d² : %d²)이다.' % (sub('A'), sub('B'), p * p, q * q, p, q), '따라서 A : B = %s' % right]
        return mc(body, right, wr, r=r, lv=('하' if (fam == 'a' and key == 'v') else '중' if key in ('v', 'T', 'a', 'w') else '상'), fam=fam, sort='shuf', steps=steps,
                  core='같은 행성을 도는 원궤도 위성은 v∝1/√r, T∝r^(3/2), a∝1/r², ω∝r^(-3/2)이다.', point='제곱수 비로 주어진 반지름에서 필요한 거듭제곱을 계산한다.')
    if fam == 'c':
        v0 = r.choice([8, 12, 16, 24, 6, 20, 10])
        s = r.choice([2, 3, 4, 5])
        v = Fr(v0, s)
        if v.denominator not in (1, 2, 4, 5): return None
        ask = r.choice(['v', 'T'])
        body = P('행성 표면 가까이에서 원 궤도로 공전하는 인공위성의 속력은 %d km/s이다(궤도 반지름 = 행성 반지름 R). 이 행성 중심으로부터 %dR 떨어진 원 궤도로 공전하는 인공위성의 속력은?' % (v0, s * s))
        ws = _ws(v, [v0 * s, Fr(v0, s * s), v0 * s * s, v0 - s, Fr(v0, s * s * s)], lambda c: _F(c) + ' km/s')
        return mc(body, '%s km/s' % _F(v), ws, r=r, lv='중', fam='c', sort='num',
                  steps=['원궤도 속력 v = √(GM/r) 이므로 v ∝ 1/√r 이다.', '궤도 반지름이 %d배이므로 속력은 1/%d배 : %d ÷ %d = %s km/s' % (s * s, s, v0, s, _F(v))],
                  core='원 궤도 위성의 속력은 궤도 반지름의 제곱근에 반비례한다.', point='반지름이 n²배이면 속력은 1/n배이다.')
    if fam == 'd':
        p = r.choice([(1, 8), (1, 27), (8, 1), (27, 1), (1, 64), (64, 1), (8, 27), (27, 8)])
        n1, n2 = p
        r1 = {1: 1, 8: 2, 27: 3, 64: 4}[n1]
        r2 = {1: 1, 8: 2, 27: 3, 64: 4}[n2]
        ratio = Fr(r2 * r2, r1 * r1)   # r_B / r_A
        r0 = r.choice([2, 3, 4, 6, 8, 9, 12])
        rB = r0 * ratio
        if rB.denominator != 1: return None
        body = P('행성 둘레를 원 궤도로 공전하는 인공위성 A의 궤도 반지름이 %d×10%s km이고 공전 주기는 T이다. 같은 행성 둘레를 원 궤도로 공전하는 인공위성 B의 공전 주기가 %s일 때, B의 궤도 반지름은?' % (r0, sup(3), _fm(Fr(n2, n1), 'T')))
        ws = _ws(rB, [r0 * Fr(n2, n1), r0 * Fr(n1, n2), r0 * (ratio ** 2), r0 / ratio, r0 * (Fr(n2, n1)) ** Fr(1, 2) if False else r0 * 2], lambda c: '%s×10%s km' % (_F(c), sup(3)))
        if ratio == 1: return None
        return mc(body, '%s×10%s km' % (_F(rB), sup(3)), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['T² ∝ r³ 이므로 r ∝ T^(2/3)이다.', 'T%s/T%s = %s이므로 r%s/r%s = (%s)^(2/3) = %s' % (sub('B'), sub('A'), _fx(Fr(n2, n1)), sub('B'), sub('A'), _fx(Fr(n2, n1)), _fx(ratio)),
                             'r%s = %d × %s = %s×10³ km' % (sub('B'), r0, _fx(ratio), _fx(rB))],
                  core='위성의 공전 주기의 제곱은 궤도 반지름의 세제곱에 비례한다.', point='주기의 비에서 반지름의 비를 거꾸로 구한다.')
    # e: g0, R 이용
    kk = r.choice([2, 4, 5, 6, 8, 10])
    Rv = kk * kk   # ×10^5 m
    s = r.choice([1, 2, 3, 4])
    v1 = Fr(kk, 1)   # km/s ( g=10, R = kk² ×10^5 m -> v = 1000 kk m/s)
    v = v1 / s
    if v.denominator not in (1, 2, 5): return None
    n = s * s
    body = P('행성 표면에서의 중력 가속도의 크기는 10 m/s²이고 행성의 반지름은 %d×10%s m이다. 이 행성 중심으로부터 %s 떨어진 원 궤도로 공전하는 인공위성의 속력은? (단, 행성의 자전과 대기의 영향은 무시한다.)' % (Rv, sup(5), '%dR' % n if n > 1 else 'R(표면 바로 위)'))
    ws = _ws(v, [v1 * s, v1 / (s * s), v1 * 2, v1 + 1, Fr(kk, 2)], lambda c: _F(c) + ' km/s')
    assert abs(math.sqrt(10 * Rv * 1e5) / 1000 - kk) < 1e-9
    return mc(body, '%s km/s' % _F(v), ws, r=r, lv='상', fam='e', sort='num',
              steps=['표면에서 중력이 구심력 역할을 하므로 v₀ = √(gR) = √(10 × %d×10⁵) = %d×10³ m/s = %d km/s' % (Rv, kk, kk),
                     '반지름이 %d배이면 v ∝ 1/√r 에서 속력은 1/%d배 : %d ÷ %d = %s km/s' % (n, s, kk, s, _F(v))],
              core='표면 부근 원궤도 속력 √(gR)와 v ∝ 1/√r 을 함께 쓴다.', point='g와 R로 기준 속력을 구한 뒤 배율을 적용한다.')


# ================================================================== ph047
def _orbits_fig(rr1, rr2, w=300, h=200):
    f = Fig(w, h)
    cx, cy = w / 2, h / 2 + 2
    f.circ(cx, cy, 14, '#cfe2f7', INK, 1.5)
    sc = 84 / max(rr1, rr2)
    for rr, nm_, col, ang in ((rr1, 'A', RD, -0.5), (rr2, 'B', BL, 2.3)):
        R = rr * sc
        f.circ(cx, cy, R, 'none', col, 1.5, '5 3')
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        f.circ(x, y, 5, col, INK, 1)
        f.text(x + 14 * math.cos(ang), y + 14 * math.sin(ang) + 5, nm_, 14, 'middle', True, INK, True)
        mx, my = cx + R * .55 * math.cos(ang), cy + R * .55 * math.sin(ang)
        f.line(cx, cy, x, y, col, 1)
        f.text(mx + 10 * math.sin(ang) * -1, my + 10 * math.cos(ang) + 3, '%sR' % (num(rr) if rr != 1 else ''), 12, 'middle', True, col)
    return f.svg()


@T('ph047')
def potential_escape(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'd'])
    if fam == 'a':
        n = r.choice([2, 3, 4, 5, 6])
        ask = r.choice(['U', 'W', 'U'])
        E0 = r.choice([None, 12, 24, 30, 60, 36])
        if ask == 'U':
            body = P('질량 m인 물체가 질량 M, 반지름 R인 행성의 중심으로부터 거리 r만큼 떨어져 있을 때 중력 위치 에너지는 U = -GMm/r이다(무한히 먼 곳이 기준). 이 물체가 행성 표면에 있을 때의 중력 위치 에너지가 -E이다. 이 물체가 행성 중심으로부터 %dR 떨어진 곳에 있을 때의 중력 위치 에너지는?' % n)
            right = '-' + _fm(Fr(1, n), 'E')
            ws = ['-' + _fm(Fr(c).limit_denominator(100), 'E') for c in (Fr(1, n * n), n, n * n, Fr(n - 1, n), Fr(1, n + 1))]
            ws += ['+' + _fm(Fr(1, n), 'E')]
            ws = [w for w in dict.fromkeys(ws) if w != right]
            return mc(body, right, ws[:5], r=r, lv='하', fam='a', sort='shuf',
                      steps=['U = -GMm/r 이므로 U는 r에 반비례한다 (부호는 항상 음).', '표면(r=R)에서 -E이므로 r = %dR에서는 -E/%d이다.' % (n, n)],
                      core='중력 위치 에너지 U = -GMm/r은 항상 음수이며 r이 커질수록 0에 가까워진다.', point='U는 r에 반비례하지만 거리의 제곱이 아님에 주의한다.')
        if E0 is None: E0 = 12
        Wf = Fr(E0) * (1 - Fr(1, n))
        if (Wf * 100).denominator != 1: return None
        body = P('질량 m인 물체가 질량 M, 반지름 R인 행성의 표면에 있을 때의 중력 위치 에너지는 -%d J이다(무한히 먼 곳이 기준). 이 물체를 행성 표면에서 행성 중심으로부터 %dR 떨어진 곳까지 천천히 옮기려면 외부에서 해 주어야 하는 일은?' % (E0, n))
        ws = _ws(Wf, [E0, Fr(E0, n), E0 * (n - 1), E0 * (1 + Fr(1, n)), Fr(E0, n * n)], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(Wf), ws, r=r, lv='중', fam='a', sort='num',
                  steps=['표면에서 U = -%d J, %dR에서 U = -%d/%d = -%s J이다.' % (E0, n, E0, n, _F(Fr(E0, n))), '해 준 일 = 위치 에너지 증가량 = -%s - (-%d) = %s J' % (_F(Fr(E0, n)), E0, _F(Wf))],
                  core='천천히 옮길 때 외부가 한 일은 중력 위치 에너지의 증가량과 같다.', point='음수인 위치 에너지의 차이를 계산한다.')
    if fam == 'b':
        # 탈출 속도 비교
        a, b = r.choice([(4, 1), (1, 4), (9, 1), (1, 9), (8, 2), (2, 8), (9, 4), (4, 9), (16, 1), (18, 2), (12, 3), (3, 12), (2, 2), (8, 1)])
        # 행성 A: M=a M0, R = b R0 ?  비: 질량 a, 반지름 b
        a, b = int(a), int(b)
        ratio = Fr(a, b)
        # 제곱수여야 유리수 비
        num_ = ratio.numerator; den_ = ratio.denominator
        if math.isqrt(num_) ** 2 != num_ or math.isqrt(den_) ** 2 != den_: return None
        s = Fr(math.isqrt(num_), math.isqrt(den_))
        if s == 1: return None
        vB = r.choice([4, 5, 6, 8, 10, 12])
        vA = vB * s
        if vA.denominator not in (1, 2): return None
        tb = table(['', '질량', '반지름'], [['행성 A', '%dM' % a if a != 1 else 'M', '%dR' % b if b != 1 else 'R'], ['행성 B', 'M', 'R']])
        if r.random() < 0.5:
            body = P('표는 행성 A, B의 질량과 반지름을 나타낸 것이다. 행성 B 표면에서의 탈출 속도가 %d km/s일 때, 행성 A 표면에서의 탈출 속도는?' % vB) + tb
            ws = _ws(vA, [vB * ratio, vB * a, vB / s, vB * b, vB * a * b], lambda c: _F(c) + ' km/s')
            return mc(body, '%s km/s' % _F(vA), ws, r=r, lv='중', fam='b', sort='num',
                      steps=['탈출 속도 v = √(2GM/R) 이므로 v ∝ √(M/R)이다.', 'A와 B의 비는 √(%d/%d) = %s이므로 v%s = %d × %s = %s km/s' % (a, b, _fx(s), sub('A'), vB, _fx(s), _F(vA))],
                      core='탈출 속도 v = √(2GM/R) 는 √(M/R)에 비례하며 물체의 질량과 무관하다.', point='질량 비와 반지름 비를 √(M/R) 에 대입한다.')
        body = P('표는 행성 A, B의 질량과 반지름을 나타낸 것이다. 두 행성 표면에서의 탈출 속도의 비 v%s : v%s는?' % (sub('A'), sub('B'))) + tb
        right = _rt(s, 1)
        wr = _rts(right, [_rt(ratio, 1), _rt(1, s), _rt(a * b, 1), _rt(a, 1), _rt(b, 1), _rt(s * s * s, 1)])
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                  steps=['v = √(2GM/R) 이므로 v%s : v%s = √(%d/%d) : 1' % (sub('A'), sub('B'), a, b), '= %s' % right],
                  core='탈출 속도 v = √(2GM/R).', point='√(M/R)의 비로 비교한다.')
    if fam == 'c':
        n = r.choice([1, 2, 3, 4, 5, 6, 8])
        q = Fr(n, n + 1)
        ask = r.choice(['h', 'h', 'q'])
        # 운동 에너지 K0 = q * K_esc , K_esc = GMm/R : 최고점 r_max = (n+1)R
        # 검증: GM=m=R=1: K0 = q ; E=K0-1 = -1/r_max
        K0 = q
        rmax = -1 / (K0 - 1)
        assert rmax == n + 1
        if ask == 'h':
            body = P('질량 M, 반지름 R인 행성의 표면에서 질량 m인 물체를 연직 위로 발사한다. 발사 순간의 운동 에너지가 이 행성에서의 탈출에 필요한 최소 운동 에너지의 %s배일 때, 물체가 도달하는 최대 높이는 행성 표면으로부터 얼마인가? (단, 행성의 자전과 대기의 영향은 무시한다.)' % ('%d/%d' % (n, n + 1)))
            right = '%sR' % _F(n)
            ws = ['%sR' % _F(Fr(c).limit_denominator(100)) for c in (n + 1, Fr(n, n + 1), Fr(1, n), Fr(1, n + 1), n * 2, n * n if n > 1 else 3)]
            ws = [w for w in dict.fromkeys(ws) if w != right]
            return mc(body, right, ws[:5], r=r, lv='상', fam='c', sort='shuf',
                      steps=['탈출에 필요한 최소 운동 에너지는 GMm/R이다. 발사 시 운동 에너지 K = %s × GMm/R이다.' % ('%d/%d' % (n, n + 1)),
                             '최고점의 거리를 r라 하면 역학적 에너지 보존 : %s GMm/R - GMm/R = -GMm/r' % ('%d/%d' % (n, n + 1)),
                             '-GMm/((%d)R) = -GMm/r 이므로 r = %dR, 최대 높이 = r - R = %dR' % (n + 1, n + 1, n)],
                      core='역학적 에너지 E = K - GMm/r 이 보존되며 최고점에서는 K=0이다.', point='탈출 최소 에너지 GMm/R 를 기준으로 에너지 보존을 적용한다.')
        body = P('질량 M, 반지름 R인 행성의 표면에서 질량 m인 물체를 연직 위로 발사했더니 행성 표면으로부터 최대 높이 %dR까지 올라갔다. 발사 순간의 운동 에너지는 이 행성에서의 탈출에 필요한 최소 운동 에너지의 몇 배인가? (단, 행성의 자전과 대기의 영향은 무시한다.)' % n)
        right = _fm(q, '')  .replace('<span class="fr"><span></span>', '<span class="fr"><span>1</span>') if False else ('%d/%d배' % (n, n + 1))
        ws = ['%d/%d배' % (x, y) for x, y in ((1, n + 1), (1, n), (n + 1, n), (n, 2 * n + 1), (1, 2))]
        ws = [w for w in dict.fromkeys(ws) if w != right]
        if n == 1: ws = ['1/3배', '1/4배', '2배', '2/3배', '3/4배']
        return mc(body, right, ws[:5], r=r, lv='중', fam='c', sort='shuf',
                  steps=['최고점까지의 거리 r = R + %dR = %dR이고 최고점에서 K=0이므로 E = -GMm/(%dR)이다.' % (n, n + 1, n + 1),
                         '발사 시 E = K - GMm/R 이므로 K = GMm/R - GMm/(%dR) = %s GMm/R' % (n + 1, '%d/%d' % (n, n + 1)),
                         '탈출 최소 운동 에너지 GMm/R 의 %d/%d배이다.' % (n, n + 1)],
                  core='역학적 에너지 보존 : K - GMm/R = -GMm/r_max.', point='최고점에서 운동 에너지가 0임을 이용한다.')
    # d: 원궤도의 에너지
    n = r.choice([2, 3, 4])
    E0 = r.choice([6, 8, 12, 16, 20, 24, 30, 36, 40, 60])
    fig = FIG(_orbits_fig(1, n), '56%')
    ask = r.choice(['E2', 'W', 'K', 'U'])
    # 반지름 R 원궤도: E=-E0 (K=E0, U=-2E0) ; 반지름 nR: E=-E0/n
    if ask == 'E2':
        right = -Fr(E0, n)
        body = P('그림은 질량 M인 행성 둘레를 도는 질량 m인 인공위성의 두 원 궤도 A(반지름 R), B(반지름 %dR)를 나타낸 것이다. 위성이 A에서 운동할 때의 역학적 에너지가 -%d J일 때, B에서 운동할 때의 역학적 에너지는? (단, 중력 위치 에너지의 기준은 무한히 먼 곳이다.)' % (n, E0)) + fig
        ws = _ws(-right, [E0, Fr(E0, n * n), E0 * n, Fr(E0, n) , Fr(E0 * (n - 1), n)], lambda c: '-' + _F(c) + ' J')
        ws = [w for w in ws if w != '-%s J' % _F(Fr(E0, n))] + ['+%s J' % _F(Fr(E0, n))]
        return mc(body, '-%s J' % _F(Fr(E0, n)), ws[:5], r=r, lv='상', fam='d', sort='shuf',
                  steps=['원궤도 위성의 역학적 에너지 E = -GMm/(2r) 이므로 E ∝ -1/r이다.', 'r이 %d배이므로 E = -%d ÷ %d = -%s J' % (n, E0, n, _F(Fr(E0, n)))],
                  core='원 궤도 위성의 역학적 에너지는 E = -GMm/(2r) = -K 이다.', point='E는 r에 반비례하며 음수이다.')
    if ask == 'W':
        Wq = Fr(E0) * (1 - Fr(1, n))
        body = P('그림은 질량 M인 행성 둘레를 도는 질량 m인 인공위성의 두 원 궤도 A(반지름 R), B(반지름 %dR)를 나타낸 것이다. 위성이 A에서 운동할 때의 역학적 에너지가 -%d J이다. 이 위성을 A에서 B로 옮겨 B에서 원운동을 하게 하려면 위성의 역학적 에너지를 얼마나 증가시켜야 하는가?' % (n, E0)) + fig
        ws = _ws(Wq, [E0, Fr(E0, n), E0 * n, Fr(E0, n * n), E0 * (1 + Fr(1, n))], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(Wq), ws, r=r, lv='상', fam='d', sort='num',
                  steps=['E%s = -%d J, E%s = -%d/%d = -%s J' % (sub('A'), E0, sub('B'), E0, n, _F(Fr(E0, n))), '증가시켜야 할 에너지 = E%s - E%s = %s J' % (sub('B'), sub('A'), _F(Wq))],
                  core='원 궤도 위성의 역학적 에너지 E = -GMm/(2r).', point='두 궤도의 역학적 에너지 차이를 구한다.')
    if ask == 'K':
        right = Fr(E0, n)
        body = P('그림은 질량 M인 행성 둘레를 도는 질량 m인 인공위성의 두 원 궤도 A(반지름 R), B(반지름 %dR)를 나타낸 것이다. 위성이 A에서 운동할 때의 역학적 에너지가 -%d J일 때, 위성이 B에서 운동할 때의 운동 에너지는?' % (n, E0)) + fig
        ws = _ws(right, [E0, Fr(E0, n * n), E0 * n, Fr(2 * E0, n), Fr(E0 * (n - 1), n)], lambda c: _F(c) + ' J')
        return mc(body, '%s J' % _F(right), ws, r=r, lv='중', fam='d', sort='num',
                  steps=['원 궤도 위성에서 E = -K 이므로 A에서 K = %d J이다 (K = GMm/2r ∝ 1/r).' % E0, 'B에서는 반지름이 %d배이므로 K = %d ÷ %d = %s J' % (n, E0, n, _F(right))],
                  core='원 궤도 위성에서 K = -E = GMm/(2r), U = 2E = -GMm/r.', point='원궤도에서는 운동 에너지가 역학적 에너지의 크기와 같다.')
    right = -2 * Fr(E0)
    body = P('질량 M인 행성 둘레를 반지름 R인 원 궤도로 도는 질량 m인 인공위성의 운동 에너지가 %d J이다. 이 위성의 중력 위치 에너지는? (단, 기준은 무한히 먼 곳이다.)' % E0)
    ws = ['-%d J' % x for x in (E0, E0 // 2 if E0 % 2 == 0 else E0 + 1, E0 * 4, E0 * 3)] + ['%d J' % (2 * E0), '%d J' % E0]
    ws = [w for w in dict.fromkeys(ws) if w != '-%d J' % (2 * E0)]
    return mc(body, '-%d J' % (2 * E0), ws[:5], r=r, lv='중', fam='d', sort='shuf',
              steps=['원 궤도에서 중력이 구심력이므로 GMm/r² = mv²/r, 즉 K = ½mv² = GMm/(2r) = %d J이다.' % E0, 'U = -GMm/r = -2K = -%d J' % (2 * E0)],
              core='원 궤도 위성에서 U = -2K, E = -K 이다.', point='구심력 = 중력으로 K와 U의 관계를 얻는다.')


# ================================================================== ph048
# (문장, 참, 풀이, 그룹)
_BANK = [
    ('행성은 태양을 한 초점으로 하는 타원 궤도를 따라 공전한다.', True, '케플러 제1법칙(타원 궤도의 법칙)이다.', 'ell'),
    ('행성의 공전 궤도에서 태양은 타원의 중심에 위치한다.', False, '태양은 타원의 중심이 아니라 두 초점 중 한 곳에 있다.', 'ell'),
    ('태양과 행성을 잇는 선이 같은 시간 동안 쓸고 지나가는 넓이는 일정하다.', True, '케플러 제2법칙(면적 속도 일정)이다.', 'area'),
    ('행성의 면적 속도는 근일점에서가 원일점에서보다 크다.', False, '면적 속도는 궤도 어디에서나 같다.', 'area'),
    ('행성의 공전 주기의 제곱은 궤도 긴반지름의 세제곱에 비례한다.', True, '케플러 제3법칙(조화의 법칙)이다.', 'k3'),
    ('행성의 공전 주기는 행성의 질량이 클수록 길다.', False, '케플러 제3법칙에서 주기는 궤도 긴반지름에 의해 정해지며 행성의 질량과 무관하다.', 'k3'),
    ('같은 별을 공전하는 행성들은 T²/a³ 의 값이 모두 같다.', True, '케플러 제3법칙에 의해 T²/a³은 별의 질량에 의해서만 결정되는 상수이다.', 'k3'),
    ('행성이 근일점에서 원일점으로 이동하는 동안 속력은 계속 증가한다.', False, '태양에서 멀어지므로 속력은 계속 감소한다.', 'spd'),
    ('행성의 속력은 태양에 가장 가까운 지점에서 가장 크다.', True, '근일점에서 속력이 최대이다(면적 속도 일정).', 'spd'),
    ('행성이 원일점에서 받는 만유인력의 크기는 근일점에서보다 크다.', False, '만유인력은 거리의 제곱에 반비례하므로 멀리 있는 원일점에서 더 작다.', 'frc'),
    ('행성의 가속도의 방향은 항상 태양을 향한다.', True, '행성에 작용하는 만유인력이 태양을 향하기 때문이다.', 'acc'),
    ('두 물체 사이의 만유인력의 크기는 두 물체의 질량의 곱에 비례한다.', True, 'F = Gm₁m₂/r² 이다.', 'law'),
    ('두 물체 사이의 거리가 2배가 되면 만유인력의 크기는 ½배가 된다.', False, '거리의 제곱에 반비례하므로 ¼배가 된다.', 'law'),
    ('질량이 큰 물체가 질량이 작은 물체를 당기는 힘은 반대로 작은 물체가 큰 물체를 당기는 힘보다 크다.', False, '두 힘은 작용 반작용 관계이므로 크기가 같다.', 'react'),
    ('지구가 달을 당기는 힘과 달이 지구를 당기는 힘의 크기는 같다.', True, '작용 반작용 관계이다.', 'react'),
    ('달이 지구 둘레를 공전할 수 있는 것은 지구의 만유인력이 구심력 역할을 하기 때문이다.', True, '달에 작용하는 알짜힘이 지구의 만유인력이며 이것이 구심력이다.', 'cen'),
    ('지구 둘레를 도는 인공위성에는 중력이 작용하지 않는다.', False, '위성에도 중력이 작용하며 이 중력이 구심력 역할을 한다.', 'cen'),
    ('지표면에서 높이 올라갈수록 중력 가속도의 크기는 작아진다.', True, 'g = GM/r² 에서 r이 커지면 g는 작아진다.', 'g'),
    ('같은 행성을 원 궤도로 도는 인공위성은 궤도 반지름이 클수록 속력이 크다.', False, 'v = √(GM/r) 이므로 반지름이 클수록 속력은 작다.', 'sat'),
    ('같은 행성을 원 궤도로 도는 인공위성은 궤도 반지름이 클수록 공전 주기가 길다.', True, 'T² ∝ r³ 이므로 반지름이 클수록 주기가 길다.', 'sat'),
    ('지구 정지 위성의 공전 주기는 지구의 자전 주기와 같다.', True, '정지 위성은 지구 자전과 같은 주기로 공전해야 지표면에서 정지해 보인다.', 'geo'),
    ('탈출 속도는 탈출시키려는 물체의 질량이 클수록 크다.', False, '탈출 속도 √(2GM/R)은 물체의 질량과 무관하다.', 'esc'),
    ('행성 표면에서의 탈출 속도는 행성의 질량이 클수록, 반지름이 작을수록 크다.', True, 'v = √(2GM/R) 이다.', 'esc'),
    ('중력만 작용하는 행성의 타원 궤도 운동에서 역학적 에너지는 일정하게 보존된다.', True, '중력은 보존력이므로 운동 에너지와 위치 에너지의 합이 일정하다.', 'en'),
    ('케플러 법칙은 태양계 행성뿐만 아니라 지구 둘레를 도는 달이나 인공위성의 운동에도 적용된다.', True, '중심 천체의 중력을 받아 도는 물체에 일반적으로 성립한다.', 'gen'),
    ('원궤도를 도는 위성의 구심 가속도의 크기는 궤도 반지름에 비례한다.', False, 'a = GM/r² 이므로 반지름의 제곱에 반비례한다.', 'sat2'),
    ('행성이 원일점에서 근일점으로 이동하는 동안 운동 에너지는 증가하고 중력 위치 에너지는 감소한다.', True, '태양에 가까워지며 속력이 커지고 위치 에너지는 작아진다.', 'en'),
]

# 그림(P=근일점, R=단축 끝, Q=원일점, S) 에 대한 문장
_FIGB = [
    ('A에서 행성의 속력이 가장 크다.', True, 'A는 태양에 가장 가까운 근일점이므로 속력이 최대이다.', 'f1'),
    ('C에서 행성의 속력이 가장 크다.', False, 'C는 원일점이므로 속력이 가장 작다.', 'f1'),
    ('행성의 면적 속도는 A에서와 C에서가 같다.', True, '면적 속도는 궤도 전체에서 일정하다.', 'f2'),
    ('행성의 면적 속도는 A에서가 C에서보다 크다.', False, '면적 속도는 궤도 전체에서 일정하다.', 'f2'),
    ('행성의 가속도의 크기는 A에서가 C에서보다 크다.', True, '태양에 가까울수록 만유인력이 크므로 가속도도 크다.', 'f3'),
    ('행성에 작용하는 만유인력의 크기는 C에서가 A에서보다 크다.', False, '거리가 먼 C에서 만유인력이 더 작다.', 'f3'),
    ('A → B → C 로 가는 데 걸리는 시간은 C → D → A 로 가는 데 걸리는 시간과 같다.', True, '두 경로는 각각 공전 궤도의 반 바퀴이며, 같은 면적을 쓸고 지나가므로 시간이 같다(타원의 긴 축이 타원의 넓이를 이등분한다).', 'f4'),
    ('A → B 로 가는 데 걸리는 시간은 공전 주기의 ¼보다 길다.', False, 'A → B 구간이 쓸고 지나가는 넓이가 전체의 ¼보다 작으므로 걸린 시간은 공전 주기의 ¼보다 짧다.', 'f5'),
    ('A → B 로 가는 데 걸리는 시간은 B → C 로 가는 데 걸리는 시간보다 짧다.', True, 'A → B 가 쓸고 지나가는 넓이가 B → C 보다 작으므로 시간이 더 짧다.', 'f5'),
    ('태양은 타원의 중심에 위치한다.', False, '태양은 두 초점 중 한 곳에 있다.', 'f6'),
    ('B에서 행성의 속력은 A에서보다 작고 C에서보다 크다.', True, '태양까지의 거리가 A < B < C 이므로 속력은 A > B > C 이다.', 'f7'),
    ('행성의 운동 에너지는 C에서가 A에서보다 크다.', False, 'A에서 속력이 가장 크므로 운동 에너지도 A에서 가장 크다.', 'f1'),
    ('행성의 역학적 에너지는 B에서가 A에서보다 크다.', False, '중력만 작용하므로 역학적 에너지는 궤도 어디에서나 같다.', 'f8'),
    ('행성의 역학적 에너지는 A, B, C, D에서 모두 같다.', True, '중력만 작용하므로 역학적 에너지가 보존된다.', 'f8'),
]


def _pick3(r, bank):
    for _ in range(100):
        s = r.sample(bank, 3)
        if len({x[3] for x in s}) < 3: continue
        t = [x[1] for x in s]
        if not any(t): continue
        if all(t) and r.random() < 0.7: continue
        return s
    return None


@T('ph048')
def kepler_bogi(r, k):
    fam = r.choice(['a', 'a', 'b', 'b', 'c'])
    if fam == 'a':
        s = _pick3(r, _BANK)
        if s is None: return None
        intro = r.choice(['케플러 법칙과 만유인력에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', '행성의 운동과 만유인력에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'])
        return bogi(intro, [(x[0], x[1], x[2]) for x in s], r=r, ask='', lv='하' if r.random() < .5 else '중', fam='a',
                    core='케플러 제1·2·3법칙과 만유인력의 법칙(F=Gm₁m₂/r²)의 내용을 구분해 알아야 한다.', point='법칙의 이름과 내용, 작용 반작용을 정확히 구분한다.')
    if fam == 'b':
        n = r.choice([2, 3, 4])
        e = (n - 1) / (n + 1)
        fig = FIG(_orbit(e, dots=[('A', 'P'), ('B', 'R'), ('C', 'Q'), ('D', 'S')]), '66%')
        s = _pick3(r, _FIGB)
        if s is None: return None
        return bogi('그림은 태양을 한 초점으로 하여 공전하는 행성의 타원 궤도를 나타낸 것이다. A는 근일점, C는 원일점이고, B, D는 타원의 짧은 축의 양 끝점이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 행성에는 태양의 만유인력만 작용한다.)',
                    [(x[0], x[1], x[2]) for x in s], pre=fig, r=r, ask='', lv='상' if r.random() < .4 else '중', fam='b',
                    core='근일점에서 속력·가속도가 최대이고 면적 속도와 역학적 에너지는 항상 일정하다.', point='궤도 그림의 위치와 케플러 제2법칙을 연결해 판단한다.')
    # c: 위성/행성 비교 보기 (수치 포함)
    p, q = r.choice([(1, 2), (1, 3), (2, 3), (1, 4)])
    rA, rB = p * p, q * q
    ma, mb = r.choice([(1, 1), (2, 1), (1, 2), (3, 1)])
    fig = FIG(_sat_fig(rA, rB), '58%')
    cand = [
        ('속력은 A가 B보다 %s.' % ('크다' if rA < rB else '작다'), True, '궤도 반지름이 작은 위성의 속력이 크다(v ∝ 1/√r).', 's1'),
        ('속력은 A가 B보다 %s.' % ('작다' if rA < rB else '크다'), False, 'v = √(GM/r) 이므로 반지름이 작을수록 속력이 크다.', 's1'),
        ('공전 주기는 A가 B보다 %s.' % ('짧다' if rA < rB else '길다'), True, 'T ∝ r^(3/2) 이므로 반지름이 클수록 주기가 길다.', 's2'),
        ('공전 주기는 A가 B보다 %s.' % ('길다' if rA < rB else '짧다'), False, 'T ∝ r^(3/2) 이므로 반지름이 클수록 주기가 길다.', 's2'),
        ('구심 가속도의 크기는 A가 B보다 %s.' % ('크다' if rA < rB else '작다'), True, 'a = GM/r² 이므로 반지름이 작을수록 가속도가 크다.', 's3'),
        ('공전 주기의 제곱은 궤도 반지름의 세제곱에 비례한다.', True, '케플러 제3법칙은 원 궤도에도 적용된다.', 's4'),
        ('위성에 작용하는 중력의 크기는 두 위성의 질량이 같으면 A와 B가 같다.', False, '질량이 같아도 반지름이 다르면 중력은 r²에 반비례하여 다르다.', 's5'),
        ('행성이 위성 A를 당기는 힘의 크기와 위성 A가 행성을 당기는 힘의 크기는 같다.', True, '작용 반작용 관계이다.', 's6'),
        ('위성 B가 행성을 당기는 힘은 행성이 위성 B를 당기는 힘보다 작다.', False, '작용 반작용 관계이므로 크기가 같다.', 's6'),
        ('위성의 질량이 클수록 같은 궤도에서의 공전 속력이 크다.', False, '궤도 속력은 질량과 무관하게 반지름에 의해 정해진다.', 's7'),
    ]
    s = _pick3(r, cand)
    if s is None: return None
    return bogi('그림은 같은 행성 둘레를 원 궤도로 공전하는 인공위성 A, B를 나타낸 것이다. 궤도 반지름은 A가 %dr, B가 %dr이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % (rA, rB),
                [(x[0], x[1], x[2]) for x in s], pre=fig, r=r, ask='', lv='중', fam='c',
                core='원궤도 위성은 반지름이 클수록 속력·구심 가속도가 작고 주기는 길다.', point='반지름 크기를 비교하여 v, T, a의 대소를 판단한다.')
