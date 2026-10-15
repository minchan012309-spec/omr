# -*- coding: utf-8 -*-
"""종합 ph106~ph113 — 여러 단원 개념을 연결하는 복합 문제 생성기."""
from phlib import *
import math, random
from fractions import Fraction as F

G = 10
SN = {30: F(1, 2), 37: F(3, 5), 53: F(4, 5)}
SNS = {30: '1/2', 37: '3/5', 53: '4/5'}
CS = {37: F(4, 5), 53: F(3, 5)}
CSS = {37: '4/5', 53: '3/5'}


# ------------------------------------------------------------------ 공통 도우미
def cl(x, nd=2):
    x = float(x)
    return abs(x * 10 ** nd - round(x * 10 ** nd)) < 1e-6


def fs(x, nd=2):
    return num(float(x), nd)


def wr(right, cands, unit, nd=2):
    """오답 선택지 문자열 목록(정답과 겹치지 않고 깨끗한 값만)."""
    right = float(right)
    out, seen = [], {round(right, 6)}

    def add(c):
        try:
            c = float(c)
        except Exception:
            return
        if c <= 0 or not cl(c, nd):
            return
        c = round(c, 6)
        if c in seen:
            return
        seen.add(c)
        out.append(U(c, unit, nd) if unit else num(c, nd))
    for c in cands:
        add(c)
    if len(out) < 4:
        for c in (right * 2, right / 2, right * 4, right / 4, right + 1, right + 2, right * 1.5, right * 3, right + 0.5):
            add(c)
    return out


def topics_bogi(r, topics, intro, pre='', lv='중', fam='e', core='', point=''):
    """topics: [(참 문장, 거짓 문장, 참 풀이, 거짓 풀이)]. 3개를 골라 참/거짓을 무작위로 정한다."""
    ts = r.sample(topics, 3)
    tr = [r.random() < 0.5 for _ in ts]
    if not any(tr):
        tr[r.randrange(3)] = True
    stm = []
    for (tt, ft, te, fe), t in zip(ts, tr):
        stm.append((tt if t else ft, t, te if t else fe))
    return bogi(intro, stm, pre=pre, r=r, lv=lv, fam=fam, core=core, point=point)


_FORCE = [None]
_CHOSEN = [None]


def pick(r, names):
    """틀(form) 선택. balanced 가 같은 틀로 다시 시도하도록 고정할 수 있다."""
    f = _FORCE[0]
    if f is not None and f in names:
        return f
    c = r.choice(names)
    _CHOSEN[0] = c
    return c


def balanced(fn):
    """선택된 틀에서 결과가 나올 때까지 몇 번 다시 시도해 틀별 비율을 가중치대로 유지한다."""
    def wrap(r, k):
        _FORCE[0] = None
        res = None
        for i in range(60):
            rr = r if i == 0 else random.Random(r.getrandbits(48))
            try:
                res = fn(rr, k)
            except AssertionError:
                res = None
            if res is not None:
                break
            if i == 0:
                _FORCE[0] = _CHOSEN[0]
        _FORCE[0] = None
        return res
    wrap.__name__ = fn.__name__
    return wrap


def pt(x0, y0, th, u, v):
    """빗면 좌표(u: 빗면 따라 위, v: 빗면에서 수직 위)를 화면 좌표로(빗면이 오른쪽으로 올라가는 경우)."""
    t = math.radians(th)
    return (x0 + u * math.cos(t) - v * math.sin(t), y0 - u * math.sin(t) - v * math.cos(t))


def dim(f, a, b, c=GR):
    f.line(a[0], a[1], b[0], b[1], c, 1.2)
    f._head(b[0], b[1], a[0], a[1], c, 1.2, 7)
    f._head(a[0], a[1], b[0], b[1], c, 1.2, 7)


def fig_incline(th, Ltxt=None, spring=None, dtxt=None, mu=None, w=300, h=190, tpos=0.6, mtxt='m', vtxt=None):
    """빗면(오른쪽으로 올라감). spring: 용수철 상수 문자열이면 아래쪽 끝에 용수철을 그린다."""
    f = Fig(w, h)
    x0, y0 = 44, h - 22
    t = math.radians(th)
    Ld = min((w - x0 - 22) / math.cos(t), (h - 56) / math.sin(t))
    x1, y1 = pt(x0, y0, th, Ld, 0)
    f.poly([(x0, y0), (x1, y0), (x1, y1)], '#f1f4f8', INK, 1.8)
    us = 0
    if spring:
        a, b = pt(x0, y0, th, 0, 0), pt(x0, y0, th, 0, 40)
        f.line(a[0], a[1], b[0], b[1], GR, 3)
        for v in range(4, 40, 8):
            p, q = pt(x0, y0, th, 0, v), pt(x0, y0, th, -7, v - 7)
            f.line(p[0], p[1], q[0], q[1], GR, 1)
        us = Ld * 0.26
        n = 10
        pts = [pt(x0, y0, th, 0, 13), pt(x0, y0, th, 6, 13)]
        for i in range(1, n + 1):
            u = 6 + (us - 12) * i / n
            pts.append(pt(x0, y0, th, u, 13 + (6 if i % 2 else -6)))
        pts += [pt(x0, y0, th, us - 6, 13), pt(x0, y0, th, us, 13)]
        f.poly(pts, 'none', INK, 1.6, close=False)
        ub = us + Ld * 0.30
    else:
        ub = tpos * Ld
    bw, bh = 36, 26
    f.poly([pt(x0, y0, th, ub, 0), pt(x0, y0, th, ub + bw, 0), pt(x0, y0, th, ub + bw, bh), pt(x0, y0, th, ub, bh)], '#cfe2f7', INK, 1.7)
    c = pt(x0, y0, th, ub + bw / 2, bh / 2)
    f.text(c[0], c[1] + 4.5, mtxt, 13, bold=True, italic=True)
    if vtxt:
        a, b = pt(x0, y0, th, ub + bw + 4, bh / 2), pt(x0, y0, th, ub + bw + 44, bh / 2)
        f.arrow(a[0], a[1], b[0], b[1], RD, 2.2)
        q = pt(x0, y0, th, ub + bw + 26, bh / 2 + 16)
        f.text(q[0] - 2, q[1] - 4, vtxt, 12.5, 'start', True, RD)
    # 경사각
    ax, ay = x0 + 40, y0
    bx, by = x0 + 40 * math.cos(t), y0 - 40 * math.sin(t)
    f.path('M %s %s A 40 40 0 0 0 %s %s' % (Fig._n(ax), Fig._n(ay), Fig._n(bx), Fig._n(by)), 'none', GR, 1.2)
    f.text(x0 + 52, y0 - 6 if th < 45 else y0 - 4, '%d°' % th, 12.5, 'start', True, GR)
    if Ltxt:
        a, b = pt(x0, y0, th, 0, 54), pt(x0, y0, th, ub, 54)
        dim(f, a, b)
        m = pt(x0, y0, th, ub / 2, 70)
        f.text(m[0] - 4, m[1], Ltxt, 12.5, bold=True, c=GR)
    if dtxt:
        a, b = pt(x0, y0, th, us, 54), pt(x0, y0, th, ub, 54)
        dim(f, a, b)
        m = pt(x0, y0, th, (us + ub) / 2, 70)
        f.text(m[0] - 4, m[1], dtxt, 12.5, bold=True, c=GR)
    if spring:
        a = pt(x0, y0, th, us / 2, 44)
        f.text(a[0] - 26, a[1] - 6, ('k = ' + spring) if spring != 'k' else 'k', 12.5, bold=True, c=BL)
    if mu:
        f.text(x1 - 12, y0 - 8, 'μ = ' + mu, 12.5, 'end', True, RD)
    return f.svg()


def fig_slope_floor(th, Ltxt=None, mu1=None, mu2=None, stop=False, w=330, h=190):
    """왼쪽이 높은 빗면 + 오른쪽 수평면. 물체는 빗면 위쪽에 있다."""
    f = Fig(w, h)
    t = math.radians(th)
    yb = h - 30
    run = min(150.0, (h - 60) / math.tan(t))
    xt = 26
    xb = xt + run
    yt = yb - run * math.tan(t)
    f.poly([(xt, yt), (xb, yb), (xt, yb)], '#f1f4f8', INK, 1.8)
    f.line(xb, yb, w - 14, yb, INK, 1.8)
    for i in range(0, int(w - 14 - xb), 8):
        f.line(xb + i, yb, xb + i - 5, yb + 6, GR, 1)
    # 빗면 위 물체 (위에서 1/3 지점)
    u = (xb - xt) / math.cos(t)
    ub = 0.28 * u
    px, py = xt + ub * math.cos(t), yt + ub * math.sin(t)
    nx, ny = math.sin(t), -math.cos(t)  # 바깥 법선(위)
    dx, dy = math.cos(t), math.sin(t)
    bw, bh = 34, 24
    pts = [(px, py), (px + bw * dx, py + bw * dy), (px + bw * dx + bh * nx, py + bw * dy + bh * ny), (px + bh * nx, py + bh * ny)]
    f.poly(pts, '#cfe2f7', INK, 1.7)
    cx = px + bw / 2 * dx + bh / 2 * nx
    cy = py + bw / 2 * dy + bh / 2 * ny
    f.text(cx, cy + 4.5, 'm', 13, bold=True, italic=True)
    f.path('M %s %s A 36 36 0 0 0 %s %s' % (Fig._n(xb - 36), Fig._n(yb), Fig._n(xb - 36 * math.cos(t)), Fig._n(yb - 36 * math.sin(t))), 'none', GR, 1.2)
    f.text(xb - 62, yb - 5, '%d°' % th, 12.5, 'start', True, GR)
    if Ltxt:
        o = 22
        a = (xt + o * nx, yt + o * ny + 0)
        a = (xt + 0 * dx + 34 * nx + 0, yt + 34 * ny)
        b = (xb + 34 * nx, yb + 34 * ny)
        dim(f, a, b)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        f.text(mx + 16 * nx - 4, my + 16 * ny - 2, Ltxt, 12.5, bold=True, c=GR)
    if mu1:
        f.text(xt + 18, yb - 8, 'μ' + '₁' + ' = ' + mu1, 12.5, 'start', True, RD)
    if mu2:
        f.text(xb + 12, yb + 22, 'μ = ' + mu2 + ' (수평면)', 12.5, 'start', True, RD)
    if stop:
        f.line(w - 40, yb - 30, w - 40, yb, GR, 1, '4 3')
        f.text(w - 40, yb - 36, '정지', 12, bold=True, c=GR)
        dim(f, (xb, yb - 14), (w - 40, yb - 14))
        f.text((xb + w - 40) / 2, yb - 20, 's', 13, bold=True, italic=True, c=GR)
    return f.svg()


# ================================================================== ph106 빗면 · 운동 법칙 · 에너지
def _mfig(th, **kw):
    return FIG(fig_incline(th, **kw), '58%')


@T('ph106')
@balanced
def g106(r, k):
    form = pick(r, ['easy', 'free', 'free', 'fric', 'fric', 'fric', 'fric', 'up', 'up', 'up', 'spring', 'spring', 'spring', 'spring', 'flat', 'flat', 'flat', 'bogi', 'bogi'])
    m = r.choice([1, 2, 3, 4, 5, 6, 8, 10])
    if form == 'easy':
        th = r.choice([30, 37, 53]); s = SN[th]
        L = r.choice([1, 2, 3, 4, 5, 6, 8, 10])
        a = G * s
        h = L * s
        ask = r.choice(['a', 'ke', 'ke'])
        fig = _mfig(th, Ltxt='%d m' % L)
        base = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면의 아래 끝에서 %d m 떨어진 지점에 질량 %d kg인 물체를 가만히 놓았다. ' % (th, L, m)
        if ask == 'a':
            right = float(a)
            assert abs(right - m * G * float(s) / m) < 1e-9
            body = P(base + '물체가 빗면을 내려오는 동안 가속도의 크기는? (단, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(right, 'm/s²'), wr(right, [G, G * float(CS.get(th, 0.8)), right / 2, right * 2, m * right], 'm/s²'), r=r, lv='하', fam='a',
                      steps=['빗면 방향의 알짜힘은 mg sin%d° 이므로 ma = mg sin%d° 이다.' % (th, th), 'a = g sin%d° = 10 × %s = %s m/s²' % (th, SNS[th], fs(right))],
                      core='마찰이 없는 빗면에서 가속도는 g sinθ 이다(질량과 무관).', point='뉴턴 제2법칙에 빗면 방향 중력 성분을 대입한다.')
        ke = m * G * h
        v = math.sqrt(2 * float(a) * L)
        assert abs(0.5 * m * v * v - float(ke)) < 1e-6
        body = P(base + '물체가 빗면 아래 끝에 도달했을 때의 운동 에너지는? (단, 중력 가속도는 10 m/s²이다.)') + fig
        return mc(body, U(float(ke), 'J'), wr(ke, [m * G * L, m * G * L * float(CS.get(th, 0.8)), float(ke) / 2, float(ke) * 2, m * L], 'J'), r=r, lv='하', fam='a',
                  steps=['처음 높이 h = L sin%d° = %d × %s = %s m' % (th, L, SNS[th], fs(h)), '역학적 에너지 보존 : Ek = mgh = %d × 10 × %s = %s J' % (m, fs(h), fs(ke)),
                         '(검산) a = g sin%d° = %s m/s², v² = 2aL = %s, ½mv² = %s J' % (th, fs(a), fs(v * v), fs(0.5 * m * v * v))],
                  core='마찰이 없으면 역학적 에너지가 보존되어 줄어든 위치 에너지가 운동 에너지가 된다.', point='빗면 길이에서 높이를 구해 에너지 보존에 쓴다.')
    if form == 'free':
        th = r.choice([30, 37, 53]); s = SN[th]
        a = G * s
        v = r.choice([2, 3, 4, 5, 6, 8, 10])
        L = F(v * v) / (2 * a)
        if not cl(L, 1) or L < 1 or L > 12: return None
        L = float(L); a = float(a); h = L * float(s)
        ask = r.choice(['v', 'v', 't', 'm_v'])
        fig = _mfig(th, Ltxt='%s m' % fs(L, 1))
        base = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위에서 질량 %d kg인 물체를 가만히 놓았더니 길이 %s m인 빗면을 따라 미끄러져 내려왔다. ' % (th, m, fs(L, 1))
        if ask == 'v':
            assert abs(math.sqrt(2 * a * L) - math.sqrt(2 * G * h)) < 1e-9 and abs(math.sqrt(2 * a * L) - v) < 1e-9
            body = P(base + '빗면 아래 끝에서 물체의 속력은? (단, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(v, 'm/s'), wr(v, [math.sqrt(2 * G * L), math.sqrt(2 * a * L) / 2, v * v / 2, v * 2, math.sqrt(a * L), math.sqrt(2 * G * L * float(CS.get(th, 0.8)))], 'm/s'), r=r, lv='중', fam='b',
                      steps=['F=ma 에서 a = g sin%d° = 10 × %s = %s m/s²' % (th, SNS[th], fs(a)), 'v² = 2aL = 2 × %s × %s = %s, v = %d m/s' % (fs(a), fs(L, 1), fs(v * v), v),
                             '(검산) h = L sin%d° = %s m, mgh = ½mv² 에서 v = √(2gh) = √%s = %d m/s' % (th, fs(h), fs(2 * G * h), v)],
                      core='빗면에서 가속도 g sinθ 로 구한 속력은 에너지 보존으로 구한 √(2gh)와 같다.', point='운동 방정식과 에너지 보존 두 방법이 같은 결과를 줌을 이용한다.')
        if ask == 'm_v':
            m2 = r.choice([2, 3])
            assert m2 * 1 > 0
            body = P(base + '같은 빗면의 같은 지점에서 질량이 %d배인 물체를 가만히 놓으면 빗면 아래 끝에서 속력은? (단, 중력 가속도는 10 m/s²이다.)' % m2) + fig
            return mc(body, U(v, 'm/s'), wr(v, [v * m2, v / m2, v * m2 ** 0.5, v * v, v / 2], 'm/s'), r=r, lv='중', fam='b',
                      steps=['a = g sin%d° = %s m/s² 로 질량과 무관하다.' % (th, fs(a)), 'v² = 2aL = 2 × %s × %s = %s 이므로 v = %d m/s' % (fs(a), fs(L, 1), fs(v * v), v), '에너지 보존 mgh = ½mv² 에서도 m 이 약분되어 v 는 질량과 무관하다.'],
                      core='마찰이 없는 빗면에서 바닥 속력은 질량과 무관하다.', point='가속도와 에너지 보존 모두 질량이 소거된다.')
        t = v / a
        if not cl(t, 2): return None
        assert abs(0.5 * a * t * t - L) < 1e-9
        body = P(base + '물체가 빗면을 내려오는 데 걸린 시간은? (단, 중력 가속도는 10 m/s²이다.)') + fig
        return mc(body, U(t, 's'), wr(t, [math.sqrt(2 * L / G), v, L / v, 2 * t, t / 2, v / G], 's'), r=r, lv='중', fam='b',
                  steps=['a = g sin%d° = %s m/s²' % (th, fs(a)), '에너지 보존으로 아래 끝 속력 v = √(2gh) = √(2 × 10 × %s) = %d m/s' % (fs(h), v), 't = v/a = %d / %s = %s s' % (v, fs(a), fs(t)),
                         '(검산) L = ½at² = ½ × %s × %s² = %s m' % (fs(a), fs(t), fs(0.5 * a * t * t))],
                  core='등가속도 운동에서 v = at 이고, 속력은 에너지 보존으로도 구할 수 있다.', point='에너지로 속력을 구한 뒤 운동학으로 시간을 구한다.')
    if form == 'fric':
        th = r.choice([37, 53]); s, c = float(SN[th]), float(CS[th])
        mu = r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5])
        a = G * (s - mu * c)
        if a <= 0.5 or not cl(a, 2): return None
        L = r.choice([1, 2, 3, 4, 5, 6, 8, 10])
        v = math.sqrt(2 * a * L)
        if not cl(v, 1): return None
        h = L * s
        Q = mu * m * G * c * L
        ek = m * G * h - Q
        assert abs(ek - 0.5 * m * v * v) < 1e-6
        fig = _mfig(th, Ltxt='%d m' % L, mu=fs(mu))
        base = '그림과 같이 경사각이 %d°인 빗면 위에서 질량 %d kg인 물체를 가만히 놓았더니 길이 %d m인 빗면을 따라 미끄러져 내려왔다. 빗면과 물체 사이의 운동 마찰 계수는 %s이다. ' % (th, m, L, fs(mu))
        ask = r.choice(['v', 'Q', 'ek', 'mu'])
        st0 = '빗면 방향 가속도 a = g(sin%d° - μcos%d°) = 10 × (%s - %s × %s) = %s m/s²' % (th, th, fs(s), fs(mu), fs(c), fs(a))
        if ask == 'v':
            body = P(base + '빗면 아래 끝에서 물체의 속력은? (단, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(v, 'm/s'), wr(v, [math.sqrt(2 * G * h), math.sqrt(2 * G * (s + mu * c) * L), math.sqrt(2 * G * (s - mu) * L), math.sqrt(2 * G * s * L) - mu, math.sqrt(2 * G * c * L)], 'm/s', 1), r=r, lv='중', fam='c',
                      steps=[st0, 'v² = 2aL = 2 × %s × %d = %s, v = %s m/s' % (fs(a), L, fs(v * v), fs(v, 1)), '(검산) 에너지 : mgh - μmg cos%d° · L = ½mv² → %s - %s = %s J = ½ × %d × v²' % (th, fs(m * G * h), fs(Q), fs(ek), m)],
                      core='마찰이 있는 빗면에서 가속도는 g(sinθ - μcosθ)이고, 줄어든 위치 에너지 중 일부는 마찰열이 된다.', point='운동 방정식으로 구한 속력과 일·에너지 관계의 일치.')
        if ask == 'Q':
            body = P(base + '물체가 빗면을 내려오는 동안 마찰력에 의해 발생한 열에너지는? (단, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(Q, 'J'), wr(Q, [m * G * h, ek, mu * m * G * L, mu * m * G * s * L, mu * m * G * c * L * 2], 'J'), r=r, lv='중', fam='c',
                      steps=['수직 항력 N = mg cos%d° = %d × 10 × %s = %s N' % (th, m, fs(c), fs(m * G * c)), '마찰력 f = μN = %s × %s = %s N' % (fs(mu), fs(m * G * c), fs(mu * m * G * c)), '마찰열 Q = f·L = %s × %d = %s J' % (fs(mu * m * G * c), L, fs(Q)),
                             '(검산) mgh - ½mv² = %s - %s = %s J' % (fs(m * G * h), fs(0.5 * m * v * v), fs(m * G * h - 0.5 * m * v * v))],
                      core='마찰열은 마찰력과 이동 거리의 곱이며 줄어든 역학적 에너지와 같다.', point='수직 항력 → 마찰력 → 마찰열 순서로 구한다.')
        if ask == 'ek':
            body = P(base + '빗면 아래 끝에서 물체의 운동 에너지는? (단, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(ek, 'J'), wr(ek, [m * G * h, Q, m * G * h + Q, m * G * L, ek / 2], 'J'), r=r, lv='상', fam='c',
                      steps=['줄어든 위치 에너지 mgh = %d × 10 × (%d × %s) = %s J' % (m, L, fs(s), fs(m * G * h)), '마찰열 Q = μmg cos%d° · L = %s J' % (th, fs(Q)), 'Ek = mgh - Q = %s - %s = %s J' % (fs(m * G * h), fs(Q), fs(ek)),
                             '(검산) a = %s m/s², v² = 2aL = %s, ½mv² = %s J' % (fs(a), fs(v * v), fs(0.5 * m * v * v))],
                      core='마찰이 있을 때 Ek = mgh - (마찰열)이다.', point='위치 에너지 감소량에서 마찰열을 뺀다.')
        base2 = '그림과 같이 경사각이 %d°인 빗면 위에서 질량 %d kg인 물체를 가만히 놓았더니 길이 %d m인 빗면을 따라 내려와 아래 끝에서 속력이 %s m/s가 되었다. ' % (th, m, L, fs(v, 1))
        fig2 = _mfig(th, Ltxt='%d m' % L)
        body = P(base2 + '빗면과 물체 사이의 운동 마찰 계수는? (단, 중력 가속도는 10 m/s²이다.)') + fig2
        if not cl(mu, 2): return None
        return mc(body, fs(mu), wr(mu, [s - mu, c - mu, mu * 2, mu / 2, (s - a / G), a / G], '', 2), r=r, lv='상', fam='c',
                  steps=['v² = 2aL 에서 a = %s² / (2 × %d) = %s m/s²' % (fs(v, 1), L, fs(a)), 'ma = mg sin%d° - μ mg cos%d° 에서 μ = (g sin%d° - a)/(g cos%d°) = (%s - %s)/%s = %s' % (th, th, th, th, fs(G * s), fs(a), fs(G * c), fs(mu)),
                         '(검산) mgh - Q = %s - %s = %s J = ½mv² = %s J' % (fs(m * G * h), fs(Q), fs(ek), fs(0.5 * m * v * v))],
                  core='속력으로 가속도를 구하고 F = ma 로 마찰 계수를 구한다.', point='운동학과 뉴턴 법칙을 연결하여 μ를 역산한다.', sort='shuf')
    if form == 'up':
        fr = r.random() < 0.4
        v0 = r.choice([4, 5, 6, 8, 10, 12])
        th = r.choice([37, 53] if fr else [30, 37, 53]); s = float(SN[th])
        fig = FIG(fig_incline(th, tpos=0.14, vtxt='v₀ = %d m/s' % v0, mu=None), '58%')
        if not fr:
            S = v0 * v0 / (2 * G * s)
            hh = v0 * v0 / (2 * G)
            if not cl(S, 2): return None
            assert abs(S * s - hh) < 1e-9
            t = v0 / (G * s)
            base = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면의 아래쪽에서 질량 %d kg인 물체를 빗면을 따라 위로 %d m/s의 속력으로 밀어 올렸다. ' % (th, m, v0)
            ask = r.choice(['S', 'S', 'h', 't'])
            if ask == 'h':
                body = P(base + '물체가 올라가는 최고 지점의 처음 위치로부터의 높이는? (단, 중력 가속도는 10 m/s²이다.)') + fig
                return mc(body, U(hh, 'm'), wr(hh, [S, hh / s, hh * s, v0 / G, v0 * v0 / G, hh * 2], 'm'), r=r, lv='하', fam='d',
                          steps=['역학적 에너지 보존 : ½mv₀² = mgh', 'h = v₀²/(2g) = %d² / 20 = %s m' % (v0, fs(hh)), '(검산) 빗면을 올라간 거리 %s m × sin%d° = %s m' % (fs(S), th, fs(S * s))],
                          core='마찰이 없으면 최고 높이는 경사각과 무관하게 v₀²/2g 이다.', point='경사각이 주어져도 높이는 에너지 보존으로 바로 구한다.')
            if ask == 'S':
                body = P(base + '물체가 빗면을 따라 올라가는 최대 거리는? (단, 중력 가속도는 10 m/s²이다.)') + fig
                return mc(body, U(S, 'm'), wr(S, [hh, v0 * v0 / (2 * G * float(CS.get(th, 0.8))), S * 2, S / 2, v0 / (G * s)], 'm'), r=r, lv='중', fam='d',
                          steps=['올라가는 동안 가속도(감속)의 크기 a = g sin%d° = %s m/s²' % (th, fs(G * s)), 'v₀² = 2aS 에서 S = %d² / (2 × %s) = %s m' % (v0, fs(G * s), fs(S)), '(검산) 에너지 보존 ½mv₀² = mg·S sin%d° → S = %s m' % (th, fs(hh / s))],
                          core='빗면을 올라가며 운동 에너지가 위치 에너지로 바뀐다. 거리 = 높이 ÷ sinθ.', point='운동학과 에너지 보존 두 방법으로 올라간 거리를 구한다.')
            if not cl(t, 2): return None
            body = P(base + '물체가 출발하여 최고 지점에 도달할 때까지 걸리는 시간은? (단, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(t, 's'), wr(t, [v0 / G, 2 * t, t / 2, S / v0, S], 's'), r=r, lv='중', fam='d',
                      steps=['a = g sin%d° = %s m/s² (속력이 줄어드는 방향)' % (th, fs(G * s)), 't = v₀/a = %d / %s = %s s' % (v0, fs(G * s), fs(t)), '(검산) 올라간 거리 S = v₀t/2 = %s m = 에너지 보존으로 구한 h/sin%d° = %s m' % (fs(v0 * t / 2), th, fs(hh / s))],
                      core='감속 운동에서 v₀ = at 이고, 가속도는 g sinθ 이다.', point='빗면 가속도를 구한 뒤 시간을 계산한다.')
        mu = r.choice([0.1, 0.2, 0.25, 0.5]) if r.random() < 0.7 else 0.25
        c = float(CS[th])
        a1 = G * (s + mu * c); a2 = G * (s - mu * c)
        if a2 <= 0: return None
        S = v0 * v0 / (2 * a1)
        if not cl(S, 2): return None
        vr2 = 2 * a2 * S
        vr = math.sqrt(vr2)
        if not cl(vr, 2): return None
        # 에너지 검산 : 오르내리는 전 과정 마찰열 = 2 μ m g cos S, ½ m vr² = ½ m v0² - 2 μ m g c S
        assert abs(0.5 * m * vr2 - (0.5 * m * v0 * v0 - 2 * mu * m * G * c * S)) < 1e-6
        fig = FIG(fig_incline(th, tpos=0.14, vtxt='v₀ = %d m/s' % v0, mu=fs(mu)), '58%')
        body = P('그림과 같이 경사각이 %d°인 빗면의 아래쪽에서 질량 %d kg인 물체를 빗면을 따라 위로 %d m/s의 속력으로 밀어 올렸더니 물체가 올라갔다가 다시 내려와 출발 지점을 지났다. 빗면과 물체 사이의 운동 마찰 계수는 %s이다. 물체가 출발 지점으로 되돌아왔을 때의 속력은? (단, 중력 가속도는 10 m/s²이다.)' % (th, m, v0, fs(mu))) + fig
        return mc(body, U(vr, 'm/s'), wr(vr, [v0, math.sqrt(2 * a1 * S), math.sqrt(v0 * v0 / 2), v0 * math.sqrt(a2 / a1) * 2, v0 / 2, math.sqrt(2 * G * (s) * S)], 'm/s'), r=r, lv='상', fam='d',
                  steps=['올라갈 때 a₁ = g(sin%d° + μcos%d°) = %s m/s² → 최대 거리 S = v₀²/2a₁ = %d² / (2 × %s) = %s m' % (th, th, fs(a1), v0, fs(a1), fs(S)),
                         '내려올 때 a₂ = g(sin%d° - μcos%d°) = %s m/s²' % (th, th, fs(a2)), 'v² = 2a₂S = 2 × %s × %s = %s, v = %s m/s' % (fs(a2), fs(S), fs(vr2), fs(vr)),
                         '(검산) ½mv² = ½mv₀² - 2μmg cos%d°·S → v² = %s' % (th, fs(v0 * v0 - 4 * mu * G * c * S))],
                  core='오르내릴 때 마찰력의 방향이 달라 가속도가 다르며, 마찰열만큼 역학적 에너지가 줄어든다.', point='올라갈 때와 내려올 때의 가속도를 따로 구한다.')
    if form == 'spring':
        th = r.choice([30, 37, 53]); s = SN[th]
        Fg = m * G * s
        d = r.choice([F(1, 10), F(2, 10), F(3, 10), F(4, 10), F(5, 10), F(6, 10), F(8, 10), F(1), F(12, 10), F(3, 2), F(2)])
        x = r.choice([F(1, 10), F(2, 10), F(1, 4), F(3, 10), F(4, 10), F(1, 2)])
        kk = 2 * Fg * (d + x) / (x * x)
        if kk.denominator != 1 or kk < 20 or kk > 1500: return None
        kk = int(kk)
        dd, xx, FF = float(d), float(x), float(Fg)
        ask = r.choice(['k', 'x', 'vt', 'vmax'])
        fig = FIG(fig_incline(th, spring='%d N/m' % kk, dtxt='%s m' % fs(dd)), '60%')
        base = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위에서 질량 %d kg인 물체가 용수철에서 %s m 떨어진 지점에 정지해 있다. 물체를 가만히 놓았더니 빗면을 내려가 아래 끝에 고정된 용수철을 압축시켰다. ' % (th, m, fs(dd))
        base_nok = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위에서 질량 %d kg인 물체가 용수철에서 %s m 떨어진 지점에 정지해 있다. 물체를 가만히 놓았더니 빗면을 내려가 아래 끝에 고정된 용수철을 압축시켰고, 용수철은 최대 %s m 압축되었다. ' % (th, m, fs(dd), fs(xx))
        if ask == 'k':
            fig = FIG(fig_incline(th, spring='k', dtxt='%s m' % fs(dd)), '60%')
            vt2 = 2 * G * float(s) * dd
            kk2 = (0.5 * m * vt2 + FF * xx) * 2 / (xx * xx)
            assert abs(kk2 - kk) < 1e-6
            body = P(base_nok + '용수철 상수 k는? (단, 중력 가속도는 10 m/s²이고, 용수철의 질량은 무시한다.)') + fig
            return mc(body, U(kk, 'N/m'), wr(kk, [2 * FF * dd / xx ** 2, 2 * FF * xx / xx ** 2, FF * (dd + xx) / xx ** 2, 2 * FF * (dd + xx) / xx, 2 * m * G * dd / xx ** 2, kk / 2, kk * 2], 'N/m'), r=r, lv='상', fam='e',
                      steps=['용수철에 닿을 때까지 : v² = 2(g sin%d°)d = 2 × %s × %s = %s' % (th, fs(G * s), fs(dd), fs(vt2)),
                             '최대 압축 시 속력 0 : ½mv² + mg sin%d°·x = ½kx² → ½ × %d × %s + %s × %s = ½ × k × %s²' % (th, m, fs(vt2), fs(FF), fs(xx), fs(xx)),
                             '(전체 구간 에너지) mg sin%d°(d + x) = ½kx² → %s × %s = ½k × %s → k = %d N/m' % (th, fs(FF), fs(dd + xx), fs(xx * xx), kk)],
                      core='물체가 내려간 전체 높이만큼 줄어든 위치 에너지가 용수철의 탄성 에너지로 바뀐다.', point='빗면 거리에 용수철 압축 길이까지 더해 높이를 계산한다.')
        if ask == 'x':
            fig = FIG(fig_incline(th, spring='%d N/m' % kk, dtxt='%s m' % fs(dd)), '60%')
            body = P(base + '용수철 상수가 %d N/m일 때 용수철의 최대 압축 길이는? (단, 중력 가속도는 10 m/s²이고, 용수철의 질량은 무시한다.)' % kk) + fig
            return mc(body, U(xx, 'm'), wr(xx, [dd * FF / kk * 2, math.sqrt(2 * FF * dd / kk), FF / kk, 2 * FF / kk, xx * 2, xx / 2, dd], 'm'), r=r, lv='상', fam='e',
                      steps=['빗면을 내려간 전체 거리는 d + x 이므로 mg sin%d°(d + x) = ½kx² 이다.' % th, '%s(%s + x) = ½ × %d × x² → ½ × %d × x² - %s x - %s = 0' % (fs(FF), fs(dd), kk, kk, fs(FF), fs(FF * dd)),
                             '이차방정식의 양의 근 x = %s m' % fs(xx), '(검산) 좌변 %s × %s = %s J, 우변 ½ × %d × %s² = %s J' % (fs(FF), fs(dd + xx), fs(FF * (dd + xx)), kk, fs(xx), fs(0.5 * kk * xx * xx))],
                      core='속력이 0이 되는 순간의 에너지 보존 : mg sinθ(d + x) = ½kx².', point='이차 방정식 대신 주어진 선택지에 대입하여 확인하는 방법도 가능하다.')
        if ask == 'vt':
            vt2 = 2 * G * float(s) * dd
            vt = math.sqrt(vt2)
            if not cl(vt, 2): return None
            assert abs(0.5 * m * vt2 - FF * dd) < 1e-9
            body = P(base + '물체가 용수철에 처음 닿는 순간의 운동 에너지는? (단, 중력 가속도는 10 m/s²이고, 용수철의 질량은 무시한다.)') + fig
            ke = FF * dd
            return mc(body, U(ke, 'J'), wr(ke, [m * G * dd, FF * (dd + xx), 0.5 * kk * dd * dd, ke * 2, ke / 2], 'J'), r=r, lv='중', fam='e',
                      steps=['처음 높이 차 = d sin%d° = %s × %s = %s m' % (th, fs(dd), SNS[th], fs(dd * float(s))), 'Ek = mgh = %d × 10 × %s = %s J' % (m, fs(dd * float(s)), fs(ke)),
                             '(검산) a = g sin%d° = %s, v² = 2ad = %s, ½mv² = %s J' % (th, fs(G * s), fs(vt2), fs(0.5 * m * vt2))],
                      core='용수철에 닿기 전까지는 중력만 일을 하므로 줄어든 위치 에너지가 운동 에너지가 된다.', point='용수철이 작용하기 전 구간만 따로 떼어 계산한다.')
        x0 = FF / kk
        if not cl(x0, 3): return None
        KE = FF * (dd + x0) - 0.5 * kk * x0 * x0
        KE2 = FF * dd + 0.5 * FF * x0
        assert abs(KE - KE2) < 1e-6
        v = math.sqrt(2 * KE / m)
        if not cl(v, 2): return None
        body = P(base + '용수철 상수가 %d N/m일 때 물체의 속력이 최대가 되는 순간의 속력은? (단, 중력 가속도는 10 m/s²이고, 용수철의 질량은 무시한다.)' % kk) + fig
        return mc(body, U(v, 'm/s'), wr(v, [math.sqrt(2 * FF * dd / m), math.sqrt(2 * FF * (dd + x0) / m), v * 2, v / 2, math.sqrt(2 * FF * dd / m) + 1], 'm/s'), r=r, lv='상', fam='e',
                  steps=['속력이 최대인 곳은 알짜힘이 0인 곳 : kx₀ = mg sin%d° → x₀ = %s / %d = %s m' % (th, fs(FF), kk, fs(x0, 3)),
                         '에너지 보존 : ½mv² = mg sin%d°(d + x₀) - ½kx₀² = %s × %s - ½ × %d × %s² = %s J' % (th, fs(FF), fs(dd + x0, 3), kk, fs(x0, 3), fs(KE, 3)),
                         'v = √(2 × %s / %d) = %s m/s' % (fs(KE, 3), m, fs(v)), '(검산) ½mv² = mg sin%d°·d + ½·mg sin%d°·x₀ = %s J' % (th, th, fs(KE2, 3))],
                  core='속력 최대 지점은 용수철 힘과 빗면 방향 중력이 같아지는 평형점이다.', point='평형점의 압축 길이를 먼저 구한 뒤 에너지 보존을 적용한다.')
    if form == 'flat':
        th = r.choice([30, 37, 53]); s = float(SN[th])
        two = r.random() < 0.45 and th in (37, 53)
        mu1 = r.choice([0.1, 0.25, 0.5]) if two else 0
        c = float(CS.get(th, 0.8))
        mu2 = r.choice([0.2, 0.25, 0.4, 0.5])
        L = r.choice([1, 2, 3, 4, 5, 6, 8, 10])
        a1 = G * (s - mu1 * c)
        if a1 <= 0: return None
        v2 = 2 * a1 * L
        sd = v2 / (2 * mu2 * G)
        sd2 = L * (s - mu1 * c) / mu2
        assert abs(sd - sd2) < 1e-9
        if not cl(sd, 2) or sd < 0.5: return None
        v = math.sqrt(v2)
        fig = FIG(fig_slope_floor(th, Ltxt='%d m' % L, mu1=fs(mu1) if two else None, mu2=fs(mu2), stop=True), '70%')
        base = '그림과 같이 경사각이 %d°인 빗면 위에서 질량 %d kg인 물체를 가만히 놓았더니 길이 %d m인 빗면을 내려와 수평면에서 운동 마찰 계수가 %s인 구간을 지나 정지하였다. ' % (th, m, L, fs(mu2))
        base += ('빗면과 물체 사이의 운동 마찰 계수는 %s이다. ' % fs(mu1)) if two else '빗면은 마찰이 없다. '
        base += '빗면과 수평면이 이어지는 곳에서 속력 손실은 없다. '
        ask = r.choice(['s', 's', 'v', 'mu'])
        if ask == 's':
            body = P(base + '물체가 수평면에서 정지할 때까지 이동한 거리 s는? (단, 중력 가속도는 10 m/s²이다.)') + fig
            wl = [L * s / mu2 if two else L * s, L / mu2, L * (s + mu1 * c) / mu2, L * s * mu2, L * s / (2 * mu2), sd * 2, sd / 2]
            return mc(body, U(sd, 'm'), wr(sd, wl, 'm'), r=r, lv='상' if two else '중', fam='f',
                      steps=['빗면 아래 끝에서 속력 : v² = 2a₁L, a₁ = g(sin%d° - %scos%d°) = %s m/s² → v² = %s' % (th, fs(mu1) if two else '0×', th, fs(a1), fs(v2)),
                             '수평면 : a₂ = μg = %s × 10 = %s m/s², s = v²/(2a₂) = %s / %s = %s m' % (fs(mu2), fs(mu2 * G), fs(v2), fs(2 * mu2 * G), fs(sd)),
                             '(검산) 에너지 : mgL(sin%d° - μ₁cos%d°) = μ₂mg·s → s = %d × (%s)/%s = %s m' % (th, th, L, fs(s - mu1 * c), fs(mu2), fs(sd2))],
                      core='처음에 줄어든 위치 에너지가 두 구간의 마찰열로 모두 소모된다.', point='빗면에서 얻은 속력으로 수평면의 감속 운동을 해석한다.')
        if ask == 'v':
            if not cl(v, 2): return None
            body = P(base + '물체가 수평면에 들어서는 순간의 속력은? (단, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(v, 'm/s'), wr(v, [math.sqrt(2 * G * L * s), math.sqrt(2 * G * L), math.sqrt(2 * G * L * (s + mu1 * c)), v * 2, v / 2, math.sqrt(v2 / 2)], 'm/s'), r=r, lv='중', fam='f',
                      steps=['a₁ = g(sin%d° - μ₁cos%d°) = %s m/s²' % (th, th, fs(a1)), 'v² = 2a₁L = 2 × %s × %d = %s → v = %s m/s' % (fs(a1), L, fs(v2), fs(v)),
                             '(검산) mgL sin%d° - 마찰열 = ½mv² → v² = %s' % (th, fs(2 * G * L * s - 2 * mu1 * G * c * L))],
                      core='빗면 구간의 마찰 유무에 따라 가속도가 다르다.', point='빗면 구간만 따로 떼어 속력을 구한다.')
        # mu: 정지 거리로 수평면 마찰 계수 역산
        body = P('그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위에서 질량 %d kg인 물체를 가만히 놓았더니 길이 %d m인 빗면을 내려와 수평면의 거친 구간을 %s m 이동한 뒤 정지하였다. 빗면과 수평면이 이어지는 곳에서 속력 손실은 없다. 수평면과 물체 사이의 운동 마찰 계수는? (단, 중력 가속도는 10 m/s²이다.)' % (th, m, L, fs(sd))) + FIG(fig_slope_floor(th, Ltxt='%d m' % L, stop=True), '70%')
        if two: return None
        return mc(body, fs(mu2), wr(mu2, [s, L / sd, s * L / (2 * sd), mu2 * 2, mu2 / 2, sd / (L * s)], '', 2), r=r, lv='상', fam='f', sort='shuf',
                  steps=['빗면 아래 끝에서 속력 : v² = 2g sin%d°·L = 2 × %s × %d = %s' % (th, fs(G * s), L, fs(v2)), '수평면에서 v² = 2μg·s 이므로 μ = v²/(2gs) = %s / (2 × 10 × %s) = %s' % (fs(v2), fs(sd), fs(mu2)),
                         '(검산) mgL sin%d° = μmg·s → μ = %d × %s / %s = %s' % (th, L, SNS[th], fs(sd), fs(L * s / sd))],
                  core='빗면에서 줄어든 위치 에너지 mgh 는 수평면 마찰열 μmg·s 와 같다.', point='에너지 보존과 운동학을 번갈아 쓴다.')
    # ---- 보기형
    th = r.choice([30, 37, 53]); s = SN[th]
    a = float(G * s)
    v = r.choice([2, 3, 4, 5, 6, 8, 10])
    L = F(v * v) / (2 * G * s)
    if not cl(L, 1) or L < 1 or L > 12: return None
    L = float(L); h = L * float(s)
    t = v / a
    ke = m * G * h
    assert abs(0.5 * m * v * v - ke) < 1e-6
    fig = _mfig(th, Ltxt='%s m' % fs(L, 1))
    wa = r.choice([G, a * 2, a / 2]); wv = r.choice([v * 2, v / 2, v + 2, math.sqrt(2 * G * L)])
    if abs(wa - a) < 1e-9 or abs(wv - v) < 1e-9: return None
    tops = [
        ('물체의 가속도의 크기는 %s m/s²이다.' % fs(a), '물체의 가속도의 크기는 %s m/s²이다.' % fs(wa), 'a = g sin%d° = %s m/s² 이다.' % (th, fs(a)), '가속도는 g sin%d° = %s m/s² 이므로 %s m/s² 가 아니다.' % (th, fs(a), fs(wa))),
        ('빗면 아래 끝에서 물체의 속력은 %s m/s이다.' % fs(v), '빗면 아래 끝에서 물체의 속력은 %s m/s이다.' % fs(wv), 'v² = 2aL = %s 이므로 v = %s m/s 이다.' % (fs(2 * a * L), fs(v)), 'v² = 2aL = %s 이므로 속력은 %s m/s 이다.' % (fs(2 * a * L), fs(v))),
        ('질량이 더 큰 물체를 같은 지점에서 놓으면 빗면 아래 끝에서의 속력은 그대로이다.', '질량이 더 큰 물체를 같은 지점에서 놓으면 빗면 아래 끝에서의 속력은 더 커진다.', '가속도와 에너지 보존 모두에서 질량이 소거되어 속력은 질량과 무관하다.', '속력은 √(2gh)로 질량과 무관하므로 달라지지 않는다.'),
        ('빗면 아래 끝에서 물체의 운동 에너지는 %s J이다.' % fs(ke), '빗면 아래 끝에서 물체의 운동 에너지는 %s J이다.' % fs(m * G * L), 'Ek = mgh = %d × 10 × %s = %s J 이다.' % (m, fs(h), fs(ke)), '높이는 L이 아니라 L sin%d° = %s m 이므로 Ek = %s J 이다.' % (th, fs(h), fs(ke))),
        ('내려오는 동안 물체의 역학적 에너지는 일정하다.', '내려오는 동안 물체의 역학적 에너지는 계속 증가한다.', '마찰이 없으므로 역학적 에너지가 보존된다.', '마찰이 없으면 역학적 에너지는 보존되며 위치 에너지가 운동 에너지로 바뀔 뿐이다.'),
        ('빗면의 중간 지점에서 물체의 운동 에너지는 아래 끝에서의 운동 에너지의 절반이다.', '빗면의 중간 지점에서 물체의 속력은 아래 끝에서의 속력의 절반이다.', '중간 지점까지 내려온 높이가 절반이므로 줄어든 위치 에너지, 즉 운동 에너지가 절반이다.', '운동 에너지가 절반이면 속력은 1/√2 배이다. 속력이 절반이면 운동 에너지는 1/4이 된다.'),
        ('빗면 길이가 같고 경사각만 커지면 아래 끝에서 속력이 커진다.', '빗면 길이가 같고 경사각만 커지면 아래 끝에서 속력은 변하지 않는다.', '높이 h = L sinθ 가 커지므로 v = √(2gh)가 커진다.', '높이가 달라지므로 속력도 달라진다. 속력이 같으려면 높이가 같아야 한다.'),
        ('물체에 작용하는 알짜힘의 크기는 %s N이다.' % fs(m * a), '물체에 작용하는 알짜힘의 크기는 %s N이다.' % fs(m * G), 'F = ma = %d × %s = %s N 이다.' % (m, fs(a), fs(m * a)), '알짜힘은 ma = %s N 이다. %s N 은 중력 mg 이다.' % (fs(m * a), fs(m * G))),
    ]
    if cl(t, 2):
        tops.append(('빗면을 내려오는 데 걸린 시간은 %s s이다.' % fs(t), '빗면을 내려오는 데 걸린 시간은 %s s이다.' % fs(t * 2), 't = v/a = %d / %s = %s s 이다.' % (v, fs(a), fs(t)), 't = v/a = %s s 이다.' % fs(t)))
    return topics_bogi(r, tops, '그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위의 길이 %s m 지점에서 질량 %d kg인 물체를 가만히 놓았다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 중력 가속도는 10 m/s²이다.)' % (th, fs(L, 1), m),
                       pre=fig, fam='g', lv='중', core='빗면에서는 가속도 g sinθ, 에너지 보존, 질량 무관성을 함께 이해한다.', point='운동 법칙과 에너지 보존의 결과를 서로 연결해 판단한다.')


# ================================================================== ph107 포물선 운동과 역학적 에너지
def fig_traj(vx, vy, h0=0.0, v0txt=None, thtxt=None, htxt=None, Htxt=None, Rtxt=None, vend=None, w=320, h=200, apex=False):
    """던진 물체의 포물선 궤적(중력 10). vy>0 이면 위로. h0: 처음 높이(절벽)."""
    t_end = (vy + math.sqrt(vy * vy + 20 * h0)) / 10.0
    xe = vx * t_end
    ytop = h0 + (vy * vy / 20.0 if vy > 0 else 0)
    ox, gy = 44, h - 28
    sc = min((w - ox - 40) / max(xe, 1e-9), (gy - 36) / max(ytop, 1e-9))
    f = Fig(w, h)
    f.line(ox - 36, gy, w - 14, gy, INK, 1.6)
    for i in range(0, int(w - 14 - ox + 36), 8):
        f.line(ox - 36 + i, gy, ox - 36 + i - 5, gy + 6, GR, 1)
    sy = gy - h0 * sc
    if h0 > 0:
        f.rect(ox - 36, sy, 36, h0 * sc, '#f1f4f8', INK, 1.6)
    pts = []
    N = 60
    for i in range(N + 1):
        tt = t_end * i / N
        pts.append((ox + vx * tt * sc, gy - (h0 + vy * tt - 5 * tt * tt) * sc))
    f.poly(pts, 'none', BL, 2.2, close=False, dash='5 3')
    f.circ(ox, sy, 5, '#cfe2f7', INK, 1.5)
    sp = math.hypot(vx, vy)
    L = 44
    f.arrow(ox, sy, ox + L * vx / sp, sy - L * vy / sp, RD, 2.4)
    if v0txt:
        f.text(ox + L * vx / sp + 6, sy - L * vy / sp - (6 if vy >= 0 else -14), v0txt, 12.5, 'start', True, RD)
    if thtxt and vy != 0:
        th = math.degrees(math.atan2(abs(vy), vx))
        sg = 1 if vy > 0 else -1
        f.path('M %s %s A 26 26 0 0 %d %s %s' % (Fig._n(ox + 26), Fig._n(sy), 0 if sg > 0 else 1, Fig._n(ox + 26 * math.cos(math.radians(th))), Fig._n(sy - sg * 26 * math.sin(math.radians(th)))), 'none', GR, 1.2)
        f.text(ox + 31, sy - sg * 7 + (4 if sg < 0 else 0), thtxt, 12.5, 'start', True, GR)
    if apex and vy > 0:
        tp = vy / 10.0
        axp, ayp = ox + vx * tp * sc, gy - (h0 + vy * tp - 5 * tp * tp) * sc
        f.line(axp, ayp, axp, gy, GR, 1, '4 3')
        f.circ(axp, ayp, 3.2, RD, RD, 1)
        if Htxt:
            f.text(axp + 6, (ayp + gy) / 2, Htxt, 12.5, 'start', True, GR)
    if htxt and h0 > 0:
        f.line(ox - 44, sy, ox - 44, gy, GR, 1.2)
        f._head(ox - 44, sy, ox - 44, gy, GR, 1.2, 7)
        f._head(ox - 44, gy, ox - 44, sy, GR, 1.2, 7)
        f.text(ox - 48, (sy + gy) / 2 + 4, htxt, 12.5, 'end', True, GR)
    if Rtxt:
        dim(f, (ox, gy + 16), (ox + xe * sc, gy + 16))
        f.text(ox + xe * sc / 2, gy + 14 if False else gy + 28 if False else h - 2, Rtxt, 12.5, bold=True, c=GR)
    if vend:
        ex, ey = ox + xe * sc, gy
        f.circ(ex, ey, 4, RD, RD, 1)
        f.text(ex - 4, ey - 10, vend, 12.5, 'end', True, RD)
    return f.svg()


TRIPLES = [(3, 4, 5), (4, 3, 5), (6, 8, 10), (8, 6, 10), (5, 12, 13), (12, 5, 13), (8, 15, 17), (15, 8, 17), (12, 16, 20), (16, 12, 20), (9, 12, 15), (12, 9, 15), (10, 24, 26), (6, 8, 10), (20, 15, 25), (15, 20, 25), (7, 24, 25), (24, 7, 25)]
SIN2 = {0: F(0), 30: F(1, 4), 37: F(9, 25), 45: F(1, 2), 53: F(16, 25), 60: F(3, 4)}
SIN2S = {30: '1/4', 37: '9/25', 45: '1/2', 53: '16/25', 60: '3/4'}
COS2 = {th: 1 - v for th, v in SIN2.items()}


def cx(th): return math.sqrt(float(COS2[th]))


def sx(th): return math.sqrt(float(SIN2[th]))
COS2S = {0: '1', 30: '3/4', 37: '16/25', 45: '1/2', 53: '9/25', 60: '1/4'}


@T('ph107')
@balanced
def g107(r, k):
    form = pick(r, ['hor', 'hor', 'hor', 'obl', 'obl', 'obl', 'obl', 'cliff', 'cliff', 'cliff', 'at', 'at', 'bogi', 'bogi'])
    m = r.choice([0.5, 1, 2, 3, 4, 5])
    if form == 'hor':
        v0, vy, vv = r.choice(TRIPLES)
        h = vy * vy / 20.0
        if not cl(h, 2): return None
        ask = r.choice(['v', 'v', 'R', 'ke', 'ang'])
        t = vy / 10.0
        R = v0 * t
        # 교차 검증
        assert abs(0.5 * m * vv * vv - (0.5 * m * v0 * v0 + m * G * h)) < 1e-6
        assert abs(h - 0.5 * G * t * t) < 1e-9
        fig = FIG(fig_traj(v0, 0, h, v0txt='v₀ = %d m/s' % v0, htxt='%s m' % fs(h), vend='v' if ask in ('v', 'ang') else None, Rtxt='R' if ask == 'R' else None), '62%')
        base = '그림과 같이 높이 %s m인 절벽 끝에서 질량 %s kg인 공을 수평 방향으로 %d m/s의 속력으로 던졌다. ' % (fs(h), fs(m), v0)
        if ask == 'v':
            body = P(base + '공이 지면에 도달하는 순간의 속력은? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)') + fig
            return mc(body, U(vv, 'm/s'), wr(vv, [v0 + vy, math.sqrt(2 * G * h), vy, v0, abs(v0 - vy) + 1, math.sqrt(v0 ** 2 + G * h)], 'm/s'), r=r, lv='중', fam='a',
                      steps=['역학적 에너지 보존 : ½mv² = ½mv₀² + mgh → v² = v₀² + 2gh', 'v² = %d² + 2 × 10 × %s = %s, v = %d m/s' % (v0, fs(h), fs(vv * vv), vv),
                             '(검산) 낙하 시간 t = √(2h/g) = %s s, 연직 속도 v_y = gt = %d m/s → v = √(%d² + %d²) = %d m/s' % (fs(t), vy, v0, vy, vv)],
                      core='수평으로 던진 물체의 도달 속력은 에너지 보존으로 구하며, 속도 성분으로 검산할 수 있다.', point='수평 속도는 그대로이고 연직 속도만 중력으로 증가한다.')
        if ask == 'R':
            body = P(base + '공이 지면에 닿을 때까지 수평 방향으로 이동한 거리 R는? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)') + fig
            if not cl(R, 2): return None
            return mc(body, U(R, 'm'), wr(R, [v0 * math.sqrt(h / G), v0 * math.sqrt(2 * h / G) / 2, v0 * vv / 10, v0 * h / 10, vv * t, v0 * t * 2], 'm'), r=r, lv='중', fam='a',
                      steps=['연직 방향 자유 낙하 : h = ½gt² → t = √(2 × %s / 10) = %s s' % (fs(h), fs(t)), 'R = v₀t = %d × %s = %s m' % (v0, fs(t), fs(R)),
                             '(검산) 지면 도달 시 연직 속도 v_y = √(2gh) = %d m/s = gt = 10 × %s' % (vy, fs(t))],
                      core='수평 방향은 등속, 연직 방향은 자유 낙하이며 두 운동의 시간은 같다.', point='에너지로 구한 연직 속도가 시간 계산과 일치한다.')
        if ask == 'ke':
            ke = 0.5 * m * vv * vv
            body = P(base + '공이 지면에 도달하는 순간의 운동 에너지는? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)') + fig
            return mc(body, U(ke, 'J'), wr(ke, [0.5 * m * v0 * v0, m * G * h, 0.5 * m * (v0 + vy) ** 2, 0.5 * m * vv, 0.5 * m * vy * vy, ke * 2], 'J'), r=r, lv='중', fam='a',
                      steps=['던질 때 운동 에너지 ½mv₀² = ½ × %s × %d² = %s J' % (fs(m), v0, fs(0.5 * m * v0 * v0)), '줄어든 위치 에너지 mgh = %s × 10 × %s = %s J' % (fs(m), fs(h), fs(m * G * h)),
                             'Ek = %s + %s = %s J' % (fs(0.5 * m * v0 * v0), fs(m * G * h), fs(ke)), '(검산) ½mv² = ½ × %s × %d² = %s J' % (fs(m), vv, fs(ke))],
                      core='역학적 에너지 보존 : 지면에서의 운동 에너지 = 처음 운동 에너지 + 위치 에너지 감소량.', point='운동 에너지와 위치 에너지의 합이 일정하다.')
        # 도달 각도: tan = vy/v0
        tanv = F(vy, v0)
        body = P(base + '공이 지면에 도달하는 순간 속도의 방향이 수평면과 이루는 각 θ에 대하여 tanθ는? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)') + fig
        ts = '%d/%d' % (tanv.numerator, tanv.denominator) if tanv.denominator != 1 else str(tanv.numerator)
        cand = [F(v0, vy), F(vy, vv), F(v0, vv), F(vy, v0) * 2, F(vy, v0) / 2]
        wl = ['%d/%d' % (c.numerator, c.denominator) if c.denominator != 1 else str(c.numerator) for c in cand]
        return mc(body, ts, wl, r=r, lv='상', fam='a', sort='shuf',
                  steps=['지면 도달 시 연직 속도 v_y = √(2gh) = √(2 × 10 × %s) = %d m/s' % (fs(h), vy), '수평 속도는 v₀ = %d m/s 로 일정하다.' % v0, 'tanθ = v_y / v₀ = %d / %d = %s' % (vy, v0, ts),
                         '(검산) 에너지 보존 v = √(v₀² + v_y²) = %d m/s, sinθ = %d/%d' % (vv, vy, vv)],
                  core='속도의 연직 성분은 에너지 보존(또는 자유 낙하)으로, 수평 성분은 그대로이다.', point='에너지와 속도 성분을 함께 사용해 방향을 구한다.')
    if form == 'obl':
        th = r.choice([30, 37, 45, 53, 60])
        v0 = r.choice([4, 5, 6, 8, 10, 12, 15, 20, 25])
        H = float(SIN2[th]) * v0 * v0 / 20
        ktop = float(COS2[th]) * 0.5 * m * v0 * v0
        ask = r.choice(['H', 'H', 'vtop', 'ketop', 'v0'])
        vx = v0 * cx(th); vy = v0 * sx(th)
        # 에너지 검산(실수 계산)
        assert abs(0.5 * m * v0 * v0 - (ktop + m * G * H)) < 1e-6
        base = '그림과 같이 지면에서 질량 %s kg인 공을 수평면과 %d°의 각으로 %d m/s의 속력으로 던졌다. ' % (fs(m), th, v0)
        tail = ' (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)'
        if ask == 'H':
            if not cl(H, 2) or H <= 0: return None
            fig = FIG(fig_traj(vx, vy, 0, v0txt='%d m/s' % v0, thtxt='%d°' % th, Htxt='H', apex=True), '62%')
            body = P(base + '공이 올라간 최고점의 높이 H는?' + tail) + fig
            return mc(body, U(H, 'm'), wr(H, [v0 * v0 / 20, v0 * v0 * float(COS2[th]) / 20, v0 * v0 * float(SIN2[th]) / 10, v0 * v0 * sx(th) / 20, H * 2, H / 2], 'm'), r=r, lv='중', fam='b',
                      steps=['처음 연직 속도 v_y = v₀ sin%d°, 최고점에서 연직 속도는 0이다.' % th, '운동 에너지 중 연직 성분만 위치 에너지가 된다 : ½m(v₀ sin%d°)² = mgH' % th,
                             'H = v₀² sin²%d° / 2g = %d² × %s / 20 = %s m' % (th, v0, SIN2S[th], fs(H)), '(검산) 수평 성분 운동 에너지 %s J 는 최고점에서 그대로이고, ½mv₀² = %s J 에서 mgH = %s J 가 줄어든다.' % (fs(ktop), fs(0.5 * m * v0 * v0), fs(m * G * H))],
                      core='비스듬히 던진 물체는 최고점에서 수평 속도 성분만 남고 연직 성분의 운동 에너지가 위치 에너지가 된다.', point='v₀ sinθ 로 최고점 높이를 구한다.')
        if ask == 'vtop':
            if th not in (37, 53): return None
            vt = v0 * float(COS2[th]) ** 0.5
            if not cl(vt, 2): return None
            fig = FIG(fig_traj(vx, vy, 0, v0txt='%d m/s' % v0, thtxt='%d°' % th, Htxt='H', apex=True), '62%')
            body = P(base + '공이 최고점에 도달했을 때 공의 속력은?' + tail) + fig
            cs = cx(th); sn = sx(th)
            return mc(body, U(vt, 'm/s'), wr(vt, [v0 * sn, 0, v0, v0 * cs / 2, math.sqrt(v0 * v0 - 2 * G * H) if False else v0 * (cs + sn) / 2, v0 * sn * 2], 'm/s'), r=r, lv='하', fam='b',
                      steps=['수평 방향으로는 힘이 없으므로 수평 속도 v₀ cos%d° 가 일정하다.' % th, '최고점에서 연직 속도는 0 이므로 속력 = v₀ cos%d° = %d × %s = %s m/s' % (th, v0, CSS.get(th, ''), fs(vt)),
                             '(검산) ½mv₀² = ½mv² + mgH 에서 v² = %d² - 2 × 10 × %s = %s' % (v0, fs(H), fs(v0 * v0 - 2 * G * H))],
                      core='최고점에서 속도는 수평 성분만 남는다.', point='최고점의 속력은 0이 아니다.')
        if ask == 'ketop':
            fig = FIG(fig_traj(vx, vy, 0, v0txt='%d m/s' % v0, thtxt='%d°' % th, Htxt='H', apex=True), '62%')
            body = P(base + '공이 최고점에 도달했을 때 공의 운동 에너지는?' + tail) + fig
            return mc(body, U(ktop, 'J'), wr(ktop, [0.5 * m * v0 * v0, 0.5 * m * v0 * v0 * float(SIN2[th]), 0.5 * m * v0 * v0 - ktop + 0 if False else m * G * H, ktop * 2, ktop / 2], 'J'), r=r, lv='중', fam='b',
                      steps=['최고점에서는 수평 속도 v₀ cos%d° 만 남는다.' % th, 'Ek = ½m(v₀ cos%d°)² = ½ × %s × %d² × %s = %s J' % (th, fs(m), v0, COS2S[th], fs(ktop)),
                             '(검산) 처음 ½mv₀² = %s J 에서 위치 에너지 mgH = %s J 를 뺀 값 = %s J' % (fs(0.5 * m * v0 * v0), fs(m * G * H), fs(0.5 * m * v0 * v0 - m * G * H))],
                      core='최고점의 운동 에너지 = 처음 운동 에너지 × cos²θ 이다.', point='운동 에너지와 위치 에너지의 전환을 함께 본다.')
        # v0 구하기: H 와 θ 가 주어짐
        if not cl(H, 2) or H <= 0: return None
        fig = FIG(fig_traj(vx, vy, 0, v0txt='v₀', thtxt='%d°' % th, Htxt='%s m' % fs(H), apex=True), '62%')
        body = P('그림과 같이 지면에서 공을 수평면과 %d°의 각으로 던졌더니 최고점의 높이가 %s m였다. 공을 던진 속력 v₀는?' % (th, fs(H)) + tail) + fig
        cs = cx(th); sn = sx(th)
        return mc(body, U(v0, 'm/s'), wr(v0, [math.sqrt(2 * G * H), math.sqrt(2 * G * H) / cs, math.sqrt(2 * G * H) * sn, v0 * 2, v0 / 2, 2 * G * H / sn if False else math.sqrt(G * H) / sn], 'm/s'), r=r, lv='상', fam='b',
                  steps=['최고점에서 연직 속도 0 : ½m(v₀ sin%d°)² = mgH' % th, 'v₀² sin²%d° = 2gH = 2 × 10 × %s = %s' % (th, fs(H), fs(2 * G * H)), 'v₀² = %s / %s = %s → v₀ = %d m/s' % (fs(2 * G * H), SIN2S[th], fs(v0 * v0), v0),
                         '(검산) 연직 성분 v₀ sin%d° = %s m/s, 이로 H = %s²/20 = %s m' % (th, fs(vy), fs(vy), fs(vy * vy / 20))],
                  core='최고점 높이 H = (v₀ sinθ)²/2g 에서 v₀ 를 역으로 구한다.', point='각도와 높이로부터 처음 속력을 구한다.')
    if form == 'cliff':
        v0, vyy, _vv = r.choice(TRIPLES)
        ask = r.choice(['v', 'v', 'v', 'cmp', 'ke'])
        h = vyy * vyy / 20.0
        vv2 = v0 * v0 + 20 * h
        vv = math.sqrt(vv2)
        if not cl(vv, 2): return None
        al = r.choice([0, 0, 0, 30, 37, 45, 53, 60])
        sgn = r.choice([1, -1]) if al else 1
        # 교차 검증(성분)
        vx = v0 * cx(al); vy0 = sgn * v0 * sx(al)
        vyl2 = vy0 * vy0 + 2 * G * h
        assert abs(vx * vx + vyl2 - vv2) < 1e-6
        word = '수평 방향으로' if al == 0 else ('수평면 위쪽으로 %d°의 각으로' % al if sgn > 0 else '수평면 아래쪽으로 %d°의 각으로' % al)
        fig = FIG(fig_traj(vx, vy0, h, v0txt='v₀ = %d m/s' % v0, thtxt=('%d°' % al) if al else None, htxt='%s m' % fs(h)), '62%')
        base = '그림과 같이 높이 %s m인 절벽 끝에서 질량 %s kg인 공을 %s %d m/s의 속력으로 던졌다. ' % (fs(h), fs(m), word, v0)
        tail = ' (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)'
        if ask == 'v':
            body = P(base + '공이 지면에 도달하는 순간의 속력은?' + tail) + fig
            return mc(body, U(vv, 'm/s'), wr(vv, [v0 + math.sqrt(2 * G * h), math.sqrt(2 * G * h), v0, vv * 2, math.sqrt(v0 ** 2 + G * h), v0 * cx(al) + math.sqrt(2 * G * h)], 'm/s'), r=r, lv='하' if al == 0 else '중', fam='c',
                      steps=['역학적 에너지 보존 : ½mv₀² + mgh = ½mv², 던진 각도는 결과에 영향이 없다.', 'v² = %d² + 2 × 10 × %s = %s → v = %s m/s' % (v0, fs(h), fs(vv2), fs(vv)),
                             '(검산) 수평 성분² + 연직 성분² = %s + %s = %s' % (fs(vx * vx), fs(vyl2), fs(vx * vx + vyl2))],
                      core='같은 높이에서 같은 속력으로 던지면 방향과 관계없이 지면 도달 속력이 같다.', point='경사각이 주어져도 속력은 에너지 보존으로 구한다.')
        if ask == 'ke':
            ke = 0.5 * m * vv2
            body = P(base + '공이 지면에 도달하는 순간의 운동 에너지는?' + tail) + fig
            return mc(body, U(ke, 'J'), wr(ke, [0.5 * m * v0 * v0, m * G * h, 0.5 * m * v0 * v0 + m * G * h * 2, 0.5 * m * (v0 + math.sqrt(2 * G * h)) ** 2, ke * 2], 'J'), r=r, lv='중', fam='c',
                      steps=['처음 운동 에너지 ½mv₀² = %s J' % fs(0.5 * m * v0 * v0), '위치 에너지 감소 mgh = %s × 10 × %s = %s J' % (fs(m), fs(h), fs(m * G * h)), 'Ek = %s + %s = %s J' % (fs(0.5 * m * v0 * v0), fs(m * G * h), fs(ke)),
                             '(검산) ½mv² = ½ × %s × %s = %s J' % (fs(m), fs(vv2), fs(0.5 * m * vv2))],
                      core='역학적 에너지 보존 : 도달 시 Ek = 처음 Ek + mgh.', point='던진 방향과 무관하게 에너지만 계산한다.')
        # 세 방향 비교
        v1 = v0
        bd = '그림과 같이 높이 %s m인 절벽 끝에서 질량이 같은 세 공 A, B, C를 같은 속력 %d m/s로 각각 수평면 위쪽으로 %d°, 수평 방향, 수평면 아래쪽으로 %d°의 방향으로 던졌다. ' % (fs(h), v0, 37, 37)
        fig = FIG(fig_traj(v0 * 0.8, v0 * 0.6, h, v0txt='A', thtxt='37°', htxt='%s m' % fs(h)), '62%')
        body = P(bd + '세 공이 지면에 도달하는 순간의 속력 vA, vB, vC 사이의 관계로 옳은 것은? (단, 공기 저항은 무시한다.)') + fig
        opts = ['vA = vB = vC', 'vA > vB > vC', 'vA < vB < vC', 'vA = vC > vB', 'vB > vA = vC']
        right = opts[0]
        return mc(body, right, opts[1:], r=r, lv='중', fam='c', sort='shuf',
                  steps=['세 공 모두 처음 높이(위치 에너지)와 처음 속력(운동 에너지)이 같다.', '역학적 에너지 보존에 따라 지면 도달 순간의 운동 에너지가 같으므로 속력도 같다 : vA = vB = vC = √(%d² + 2 × 10 × %s) = %s m/s' % (v0, fs(h), fs(vv)),
                         '(참고) 도달 시간은 다르다 : 위로 던진 A가 가장 오래 걸린다.'],
                  core='에너지 보존에서 도달 속력은 던진 방향과 관계없다.', point='속력(에너지)과 시간(운동학)을 구분한다.')
    if form == 'at':
        th = r.choice([30, 37, 45, 53, 60])
        v0 = r.choice([10, 12, 15, 20, 25, 30, 40])
        H = float(SIN2[th]) * v0 * v0 / 20
        ask = r.choice(['y', 'y', 'eq'])
        vx = v0 * cx(th); vy = v0 * sx(th)
        base = '그림과 같이 지면에서 질량 %s kg인 공을 수평면과 %d°의 각으로 %d m/s의 속력으로 던졌다. ' % (fs(m), th, v0)
        tail = ' (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)'
        if ask == 'y':
            ta, tb, tc = r.choice(TRIPLES)
            v0 = tc; H = float(SIN2[th]) * v0 * v0 / 20
            y = tb * tb / 20.0
            if y >= H - 0.3: return None
            vy2 = v0 * v0 - 20 * y
            vv = math.sqrt(vy2)
            if not cl(vv, 2): return None
            vx = v0 * cx(th)
            # 교차 검증 : 성분
            vyy2 = (v0 * sx(th)) ** 2 - 20 * y
            assert abs(vx * vx + vyy2 - vy2) < 1e-6
            vx = v0 * cx(th); vy = v0 * sx(th)
            base = '그림과 같이 지면에서 질량 %s kg인 공을 수평면과 %d°의 각으로 %d m/s의 속력으로 던졌다. ' % (fs(m), th, v0)
            fig = FIG(fig_traj(vx, vy, 0, v0txt='%d m/s' % v0, thtxt='%d°' % th), '62%')
            body = P(base + '공이 높이 %s m인 지점을 지나는 순간의 속력은?' % fs(y) + tail) + fig
            return mc(body, U(vv, 'm/s'), wr(vv, [v0 - math.sqrt(2 * G * y), v0 - G * y / v0, math.sqrt(v0 * v0 + 20 * y), v0 * cx(th), math.sqrt(2 * G * y), vv / 2], 'm/s'), r=r, lv='상', fam='d',
                      steps=['역학적 에너지 보존 : ½mv₀² = ½mv² + mgy (각도와 무관)', 'v² = %d² - 2 × 10 × %s = %s, v = %s m/s' % (v0, fs(y), fs(vy2), fs(vv)),
                             '(검산) 수평 성분² %s + 연직 성분² %s = %s' % (fs(vx * vx), fs(vyy2), fs(vx * vx + vyy2))],
                      core='높이 y 에서의 속력은 v² = v₀² - 2gy 로 에너지 보존에서 구한다.', point='던진 각도는 속력 계산에 필요하지 않다.')
        # KE = PE 인 높이: 위치 에너지 = 운동 에너지 → mgy = ½mv₀² / 2
        y = v0 * v0 / 40
        if not cl(y, 2) or y >= H: return None
        assert abs(0.5 * m * (v0 * v0 - 20 * y) - m * G * y) < 1e-6
        fig = FIG(fig_traj(vx, vy, 0, v0txt='%d m/s' % v0, thtxt='%d°' % th), '62%')
        body = P(base + '공이 올라가는 도중 운동 에너지와 중력 위치 에너지(지면 기준)가 같아지는 지점의 높이는?' + tail) + fig
        return mc(body, U(y, 'm'), wr(y, [H, H / 2, v0 * v0 / 20, v0 * v0 / 80, v0 * v0 / 20 * float(SIN2[th]) / 2], 'm'), r=r, lv='상', fam='d',
                  steps=['역학적 에너지 총량 ½mv₀² = ½ × %s × %d² = %s J' % (fs(m), v0, fs(0.5 * m * v0 * v0)), '운동 에너지 = 위치 에너지이면 각각 총량의 절반 : mgy = ¼mv₀²', 'y = v₀²/(4g) = %d² / 40 = %s m' % (v0, fs(y)),
                         '(검산) 이때 속력² = v₀² - 2gy = %s, ½mv² = %s J = mgy = %s J' % (fs(v0 * v0 - 20 * y), fs(0.5 * m * (v0 * v0 - 20 * y)), fs(m * G * y))],
                  core='운동 에너지와 위치 에너지의 합이 일정하므로 둘이 같아지는 곳은 각각 총량의 절반이다.', point='던진 각도와 관계없이 y = v₀²/4g 이다.')
    # 보기형
    th = r.choice([30, 37, 45, 53, 60])
    v0 = r.choice([10, 20, 30, 40, 25, 15])
    H = float(SIN2[th]) * v0 * v0 / 20
    if not cl(H, 2): return None
    ktop = float(COS2[th]) * 0.5 * m * v0 * v0
    k0 = 0.5 * m * v0 * v0
    vx = v0 * cx(th); vy = v0 * sx(th)
    fig = FIG(fig_traj(vx, vy, 0, v0txt='%d m/s' % v0, thtxt='%d°' % th, Htxt='H', apex=True), '62%')
    tops = [
        ('최고점의 높이 H는 %s m이다.' % fs(H), '최고점의 높이 H는 %s m이다.' % fs(v0 * v0 / 20), 'H = (v₀ sin%d°)²/2g = %s m 이다.' % (th, fs(H)), '높이는 v₀²/2g 가 아니라 (v₀ sin%d°)²/2g = %s m 이다.' % (th, fs(H))),
        ('최고점에서 공의 운동 에너지는 %s J이다.' % fs(ktop), '최고점에서 공의 운동 에너지는 0이다.', '수평 속도 성분이 남아 Ek = ½m(v₀cos%d°)² = %s J 이다.' % (th, fs(ktop)), '최고점에서도 수평 속도 성분이 있어 운동 에너지는 %s J 이다.' % fs(ktop)),
        ('최고점에서 공의 가속도의 크기는 10 m/s²이다.', '최고점에서 공의 가속도는 0이다.', '던진 뒤에는 중력만 작용하므로 가속도는 항상 g = 10 m/s² 이다.', '최고점에서도 중력이 작용하므로 가속도는 10 m/s² 이다.'),
        ('지면에 다시 떨어지는 순간의 속력은 %d m/s이다.' % v0, '지면에 다시 떨어지는 순간의 속력은 %s m/s이다.' % fs(v0 * 0.5 if v0 % 2 == 0 else v0 + 5), '같은 높이에서 역학적 에너지 보존에 의해 속력이 같다.', '같은 높이이므로 처음 속력 %d m/s 와 같다.' % v0),
        ('던지는 속력이 같다면 각도가 커질수록(45° 이하에서) 최고점의 높이가 높아진다.', '던지는 속력이 같다면 각도가 달라도 최고점의 높이는 같다.', 'H = v₀² sin²θ/2g 이므로 θ 가 커지면 H 가 커진다.', 'H 는 sin²θ 에 비례하므로 각도에 따라 달라진다.'),
        ('최고점에서 공의 역학적 에너지는 처음 역학적 에너지와 같다.', '최고점에서 공의 역학적 에너지는 처음보다 mgH 만큼 증가한다.', '공기 저항이 없으면 역학적 에너지가 보존된다.', '운동 에너지가 줄어든 만큼 위치 에너지가 늘어 합은 일정하다.'),
        ('최고점에서 위치 에너지는 %s J이다.(지면 기준)' % fs(m * G * H), '최고점에서 위치 에너지는 %s J이다.(지면 기준)' % fs(k0), 'Ep = mgH = %s × 10 × %s = %s J 이다.' % (fs(m), fs(H), fs(m * G * H)), '위치 에너지는 mgH = %s J 이고 %s J 는 처음 운동 에너지이다.' % (fs(m * G * H), fs(k0))),
    ]
    return topics_bogi(r, tops, '그림과 같이 지면에서 질량 %s kg인 공을 수평면과 %d°의 각으로 %d m/s의 속력으로 던졌다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)' % (fs(m), th, v0),
                       pre=fig, fam='e', lv='중', core='포물선 운동에서 수평 속도는 일정하고 역학적 에너지는 보존된다.', point='속도 성분과 에너지 전환을 함께 판단한다.')


# ================================================================== ph108 충돌과 용수철
def _blk(f, x, y, w, h, txt, fill='#cfe2f7'):
    f.rect(x, y - h, w, h, fill, INK, 1.7)
    f.text(x + w / 2, y - h / 2 + 4.5, txt, 12.5, bold=True, italic=True)


def fig_coll(layout, m1, m2, v1=None, kt=None, h=None, mu=None, w=330, hh=165):
    """layout: 'wall'(벽에 고정된 용수철 + 정지한 m2), 'free'(m2 왼쪽에 용수철), 'slope'(빗면에서 내려와 충돌)."""
    f = Fig(w, hh)
    fy = hh - 44
    f.line(10, fy, w - 8, fy, INK, 1.7)
    for i in range(10, w - 8, 8):
        f.line(i, fy, i - 5, fy + 6, GR, 1)
    bw, bh = 40, 30
    if layout == 'wall':
        wx = w - 22
        f.line(wx, fy - 50, wx, fy, GR, 3)
        for v in range(fy - 48, fy, 8):
            f.line(wx, v, wx + 6, v - 6, GR, 1)
        b2 = wx - 66 - bw
        f.spring(b2 + bw, fy - bh / 2, wx, 7, 7)
        _blk(f, b2, fy, bw, bh, 'm₂', '#f6d9d6')
        b1 = 50
        _blk(f, b1, fy, bw, bh, 'm₁')
        f.arrow(b1 + bw / 2, fy - bh - 16, b1 + bw / 2 + 46, fy - bh - 16, RD, 2.4)
        if v1: f.text(b1 + bw / 2, fy - bh - 24, v1, 12.5, 'start', True, RD)
        if kt: f.text((b2 + bw + wx) / 2, fy - bh / 2 - 16, kt, 12.5, bold=True, c=BL)
        f.text(b1 + bw / 2, fy + 24, m1, 12.5, bold=True, c=GR)
        f.text(b2 + bw / 2, fy + 24, m2, 12.5, bold=True, c=GR)
        if mu:
            f.text(w / 2, fy + 38, mu, 12.5, bold=True, c=RD)
    elif layout == 'free':
        b2 = 190
        f.spring(b2 - 50, fy - bh / 2, b2, 6, 7)
        _blk(f, b2, fy, bw, bh, 'm₂', '#f6d9d6')
        b1 = 36
        _blk(f, b1, fy, bw, bh, 'm₁')
        f.arrow(b1 + bw / 2, fy - bh - 16, b1 + bw / 2 + 46, fy - bh - 16, RD, 2.4)
        if v1: f.text(b1 + bw / 2, fy - bh - 24, v1, 12.5, 'start', True, RD)
        if kt: f.text(b2 - 25, fy - bh / 2 - 16, kt, 12.5, bold=True, c=BL)
        f.text(b1 + bw / 2, fy + 24, m1, 12.5, bold=True, c=GR)
        f.text(b2 + bw / 2, fy + 24, m2, 12.5, bold=True, c=GR)
    else:  # slope
        import math as _m
        wx = w - 22
        f.line(wx, fy - 50, wx, fy, GR, 3)
        for v in range(fy - 48, fy, 8):
            f.line(wx, v, wx + 6, v - 6, GR, 1)
        b2 = wx - 58 - bw
        f.spring(b2 + bw, fy - bh / 2, wx, 6, 7)
        _blk(f, b2, fy, bw, bh, 'm₂', '#f6d9d6')
        x0, xb = 16, 112
        yt = 26
        f.poly([(x0, yt), (xb, fy), (x0, fy)], '#f1f4f8', INK, 1.8)
        t = _m.atan2(fy - yt, xb - x0)
        ux, uy = _m.cos(t), _m.sin(t)
        nx, ny = _m.sin(t), -_m.cos(t)
        px, py = x0 + 8 + 4 * ux, yt + 0.12 * (fy - yt) + 4 * uy
        px, py = x0 + 0.2 * (xb - x0), yt + 0.2 * (fy - yt)
        pts = [(px, py), (px + 30 * ux, py + 30 * uy), (px + 30 * ux + 22 * nx, py + 30 * uy + 22 * ny), (px + 22 * nx, py + 22 * ny)]
        f.poly(pts, '#cfe2f7', INK, 1.7)
        f.text(px + 15 * ux + 11 * nx, py + 15 * uy + 11 * ny + 4.5, 'm₁', 12, bold=True, italic=True)
        f.line(x0 - 8, yt, x0 - 8, fy, GR, 1.2)
        f._head(x0 - 8, yt, x0 - 8, fy, GR, 1.2, 7)
        f._head(x0 - 8, fy, x0 - 8, yt, GR, 1.2, 7)
        f.text(x0 + 2, (yt + fy) / 2 + 40, h or '', 12.5, 'start', True, GR) if False else f.text(x0 + 4, fy - 8, h or '', 12.5, 'start', True, GR)
        if kt: f.text((b2 + bw + wx) / 2, fy - bh / 2 - 16, kt, 12.5, bold=True, c=BL)
        f.text(b2 + bw / 2, fy + 24, m2, 12.5, bold=True, c=GR)
        f.text(70, fy + 24, m1, 12.5, bold=True, c=GR)
    return f.svg()


def _mass_pairs():
    return [(a, b) for a in (1, 2, 3, 4, 5, 6) for b in (1, 2, 3, 4, 5, 6, 8)]


@T('ph108')
@balanced
def g108(r, k):
    form = pick(r, ['wall', 'wall', 'wall', 'free', 'free', 'free', 'slope', 'rough', 'rough', 'bogi', 'bogi'])
    m1, m2 = r.choice(_mass_pairs())
    M = m1 + m2
    tail = ' (단, 용수철의 질량과 모든 마찰은 무시한다.)'
    if form in ('wall', 'bogi'):
        v1 = r.choice([2, 3, 4, 5, 6, 8, 10, 12])
        v = F(m1 * v1, M)
        if not cl(v, 2): return None
        v = float(v)
        E = 0.5 * M * v * v
        xs = [0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5]
        x = r.choice(xs)
        kk = 2 * E / (x * x)
        if not cl(kk, 6) or abs(kk - round(kk)) > 1e-6 or kk < 20 or kk > 3000: return None
        kk = int(round(kk))
        # 교차 검증 : 운동량 보존 / 에너지 보존 / 환산 질량식
        assert abs(m1 * v1 - M * v) < 1e-9
        loss = 0.5 * m1 * v1 * v1 - E
        assert abs(loss - 0.5 * m1 * v1 * v1 * m2 / M) < 1e-6
        assert abs(0.5 * kk * x * x - E) < 1e-6
        ask = r.choice(['v', 'v', 'v', 'v', 'loss', 'x', 'k', 'x'])
        if form == 'bogi':
            ask = 'bogi'
        kt = '%d N/m' % kk
        fig = FIG(fig_coll('wall', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1, kt=kt), '66%')
        base = '그림과 같이 마찰이 없는 수평면에서 질량 %d kg인 물체 A가 %d m/s의 속력으로 운동하여, 벽에 고정된 용수철에 연결되어 정지해 있던 질량 %d kg인 물체 B와 충돌한 뒤 한 덩어리가 되어 용수철을 압축시킨다. ' % (m1, v1, m2)
        if ask == 'v':
            fig = FIG(fig_coll('wall', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1), '66%')
            body = P(base + '충돌 직후 두 물체의 속력은?' + tail) + fig
            return mc(body, U(v, 'm/s'), wr(v, [v1 / 2, m1 * v1 / m2, v1 * m2 / M, v1, math.sqrt(m1 / M) * v1, v1 * (m1 - m2) / M if m1 > m2 else v1 / 3], 'm/s'), r=r, lv='하', fam='a',
                      steps=['충돌 과정에서 운동량이 보존된다 : %d × %d = (%d + %d)v' % (m1, v1, m1, m2), 'v = %d / %d = %s m/s' % (m1 * v1, M, fs(v)), '(검산) 충돌 직후 운동량 %d × %s = %s = 충돌 전 %d' % (M, fs(v), fs(M * v), m1 * v1)],
                      core='완전 비탄성 충돌에서 운동량 보존으로 합체 후 속도를 구한다.', point='충돌 구간에는 운동량 보존을 쓴다.')
        if ask == 'loss':
            fig = FIG(fig_coll('wall', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1), '66%')
            body = P(base + '충돌 과정에서 손실된 역학적 에너지는?' + tail) + fig
            return mc(body, U(loss, 'J'), wr(loss, [0.5 * m1 * v1 * v1, E, 0.5 * m1 * v1 * v1 * m1 / M, loss * 2, 0.5 * m2 * v * v], 'J'), r=r, lv='중', fam='a',
                      steps=['충돌 직후 속력 v = m₁v₁/(m₁+m₂) = %d × %d / %d = %s m/s' % (m1, v1, M, fs(v)), '충돌 전 운동 에너지 ½ × %d × %d² = %s J, 충돌 직후 ½ × %d × %s² = %s J' % (m1, v1, fs(0.5 * m1 * v1 * v1), M, fs(v), fs(E)),
                             '손실 = %s - %s = %s J' % (fs(0.5 * m1 * v1 * v1), fs(E), fs(loss)), '(검산) 손실 = ½m₁v₁² × m₂/(m₁+m₂) = %s × %d/%d = %s J' % (fs(0.5 * m1 * v1 * v1), m2, M, fs(loss))],
                      core='완전 비탄성 충돌에서는 운동량만 보존되고 운동 에너지 일부가 열 등으로 손실된다.', point='충돌 전후의 운동 에너지 차이를 계산한다.')
        if ask == 'x':
            fig = FIG(fig_coll('wall', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1, kt=kt), '66%')
            body = P(base + '용수철이 최대로 압축되었을 때 압축된 길이는?' + tail) + fig
            return mc(body, U(x, 'm'), wr(x, [x * 2, x / 2, v1 * math.sqrt(m1 / kk), v * math.sqrt(m1 / kk), v * math.sqrt(M / kk) * math.sqrt(M / m1), x * math.sqrt(2)], 'm'), r=r, lv='중', fam='a',
                      steps=['충돌 직후 속력 v = %d × %d / %d = %s m/s (운동량 보존)' % (m1, v1, M, fs(v)), '용수철 압축 구간 에너지 보존 : ½(m₁+m₂)v² = ½kx² → ½ × %d × %s² = ½ × %d × x²' % (M, fs(v), kk),
                             'x² = %s / %d = %s → x = %s m' % (fs(M * v * v), kk, fs(x * x, 4), fs(x)), '(검산) 탄성 에너지 ½kx² = ½ × %d × %s² = %s J = %s J' % (kk, fs(x), fs(0.5 * kk * x * x), fs(E))],
                      core='충돌(운동량 보존) → 용수철 압축(에너지 보존)의 두 단계로 풀이한다.', point='충돌 구간과 압축 구간에 서로 다른 보존 법칙을 적용한다.')
        if ask == 'k':
            fig = FIG(fig_coll('wall', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1, kt='k'), '66%')
            body = P(base + '용수철이 최대로 %s m 압축되었다. 용수철 상수 k는?' % fs(x) + tail) + fig
            return mc(body, U(kk, 'N/m'), wr(kk, [2 * 0.5 * m1 * v1 * v1 / (x * x), kk * 2, kk / 2, M * v1 * v1 / (x * x), m1 * v * v / (x * x), kk * M / m1], 'N/m'), r=r, lv='중', fam='a',
                      steps=['충돌 직후 속력 v = %d × %d / %d = %s m/s' % (m1, v1, M, fs(v)), '운동 에너지 ½ × %d × %s² = %s J 가 모두 탄성 에너지로 : ½ × k × %s² = %s' % (M, fs(v), fs(E), fs(x), fs(E)),
                             'k = 2 × %s / %s = %d N/m' % (fs(E), fs(x * x, 4), kk), '(검산) 충돌 전 에너지 %s J 를 쓰면 틀린다. 충돌 후 에너지만 탄성 에너지가 된다.' % fs(0.5 * m1 * v1 * v1)],
                      core='합체 충돌에서 손실된 에너지를 제외한 운동 에너지가 용수철에 저장된다.', point='충돌 전 속력이 아니라 충돌 직후 속력을 쓴다.')
        # 보기형
        wl = r.choice([x * 2, x / 2, x * 1.5])
        tops = [
            ('충돌 직후 두 물체의 속력은 %s m/s이다.' % fs(v), '충돌 직후 두 물체의 속력은 %s m/s이다.' % fs(r.choice([v1 / 2, v * 2, v1])), '운동량 보존으로 v = m₁v₁/(m₁+m₂) = %s m/s 이다.' % fs(v), '운동량 보존으로 v = %s m/s 이다.' % fs(v)),
            ('충돌 과정에서 운동량은 보존된다.', '충돌 과정에서 운동 에너지가 보존된다.', '외력이 없으므로 충돌 전후 운동량이 같다.', '합체 충돌에서는 운동 에너지가 일부 손실되어 보존되지 않는다.'),
            ('충돌로 손실된 에너지는 %s J이다.' % fs(loss), '충돌로 손실된 에너지는 %s J이다.' % fs(r.choice([E, 0.5 * m1 * v1 * v1, loss * 2])), '손실 = ½m₁v₁² - ½(m₁+m₂)v² = %s J 이다.' % fs(loss), '손실은 %s J 이다.' % fs(loss)),
            ('용수철이 최대로 압축되었을 때 용수철에 저장된 탄성 에너지는 %s J이다.' % fs(E), '용수철이 최대로 압축되었을 때 용수철에 저장된 탄성 에너지는 %s J이다.' % fs(0.5 * m1 * v1 * v1), '압축 구간에서 역학적 에너지가 보존되므로 충돌 직후 운동 에너지 %s J 가 저장된다.' % fs(E), '충돌 직후 운동 에너지 %s J 가 저장되며 %s J 는 충돌 전 운동 에너지이다.' % (fs(E), fs(0.5 * m1 * v1 * v1))),
            ('용수철이 최대로 압축되었을 때 두 물체의 속력은 0이다.', '용수철이 최대로 압축되었을 때 두 물체의 속력은 충돌 직후와 같다.', '최대 압축 순간 물체가 잠시 멈춘다.', '최대 압축에서는 물체가 순간 정지하여 속력이 0이다.'),
            ('최대 압축 길이는 %s m이다.' % fs(x), '최대 압축 길이는 %s m이다.' % fs(wl), '½kx² = %s J 에서 x = %s m 이다.' % (fs(E), fs(x)), 'x = √(2E/k) = %s m 이다.' % fs(x)),
            ('용수철을 압축하는 동안 두 물체의 역학적 에너지의 합(운동+탄성)은 보존된다.', '용수철을 압축하는 동안 두 물체의 운동량은 보존된다.', '마찰이 없고 용수철이 한 일은 탄성 에너지로 저장되어 보존된다.', '벽이 용수철을 통해 힘을 주므로 운동량은 보존되지 않는다.'),
        ]
        return topics_bogi(r, tops, '그림과 같이 마찰이 없는 수평면에서 질량 %d kg인 물체 A가 %d m/s로 운동하여, 벽에 고정된 용수철에 연결된 정지해 있던 질량 %d kg인 물체 B와 충돌한 뒤 한 덩어리가 되어 용수철을 최대 %s m 압축시켰다(용수철 상수 %d N/m). 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 용수철의 질량과 마찰은 무시한다.)' % (m1, v1, m2, fs(x), kk),
                           pre=fig, fam='e', lv='중', core='충돌 구간은 운동량 보존, 용수철 압축 구간은 에너지 보존이다.', point='구간마다 보존되는 양을 구분한다.')
    if form == 'free':
        v1 = r.choice([2, 3, 4, 5, 6, 8, 10, 12])
        v = F(m1 * v1, M)
        if not cl(v, 2): return None
        v = float(v)
        Es = 0.5 * m1 * v1 * v1 - 0.5 * M * v * v
        assert abs(Es - 0.5 * (m1 * m2 / M) * v1 * v1) < 1e-6
        ask = r.choice(['vc', 'vc', 'Es', 'Es', 'Es', 'x', 'sep'])
        base = '그림과 같이 마찰이 없는 수평면에서 질량 %d kg인 물체 A가 %d m/s의 속력으로 운동하여, 왼쪽에 용수철이 달려 정지해 있는 질량 %d kg인 물체 B에 접근한다. A가 용수철과 충돌하며 용수철이 압축된다. ' % (m1, v1, m2)
        if ask == 'vc':
            fig = FIG(fig_coll('free', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1), '66%')
            body = P(base + '용수철이 최대로 압축된 순간 두 물체의 속력은?' + tail) + fig
            return mc(body, U(v, 'm/s'), wr(v, [v1 / 2, v1, m1 * v1 / m2, 0, v1 * m2 / M, v1 * (m1 - m2) / M if m1 > m2 else v1 / 3], 'm/s'), r=r, lv='하', fam='b',
                      steps=['용수철이 가장 많이 압축될 때 두 물체의 속도가 같아진다.', '운동량 보존 : %d × %d = (%d + %d)v' % (m1, v1, m1, m2), 'v = %d / %d = %s m/s' % (m1 * v1, M, fs(v))],
                      core='최대 압축 순간에는 두 물체의 속도가 같다.', point='속도가 같아지는 조건과 운동량 보존을 함께 쓴다.')
        if ask == 'Es':
            fig = FIG(fig_coll('free', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1), '66%')
            body = P(base + '용수철이 최대로 압축되었을 때 용수철에 저장된 탄성 에너지는?' + tail) + fig
            return mc(body, U(Es, 'J'), wr(Es, [0.5 * m1 * v1 * v1, 0.5 * M * v * v, Es * 2, 0.5 * m2 * v * v, 0.5 * m1 * v * v], 'J'), r=r, lv='중', fam='b',
                      steps=['최대 압축 순간 두 물체의 속도가 같다 : m₁v₁ = (m₁+m₂)v → v = %d × %d / %d = %s m/s' % (m1, v1, M, fs(v)), '에너지 보존 : ½m₁v₁² = ½(m₁+m₂)v² + E탄성',
                             'E탄성 = %s - %s = %s J' % (fs(0.5 * m1 * v1 * v1), fs(0.5 * M * v * v), fs(Es)), '(검산) E탄성 = ½·(m₁m₂/(m₁+m₂))·v₁² = ½ × %s × %d² = %s J' % (fs(m1 * m2 / M), v1, fs(0.5 * m1 * m2 / M * v1 * v1))],
                      core='용수철이 가장 많이 압축될 때 두 물체의 속도는 같고, 줄어든 운동 에너지가 탄성 에너지가 된다.', point='속도가 같아지는 순간에 운동량 보존과 에너지 보존을 함께 쓴다.')
        if ask == 'x':
            xs = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5]
            x = r.choice(xs)
            kk = 2 * Es / (x * x)
            if abs(kk - round(kk)) > 1e-6 or kk < 20 or kk > 3000: return None
            kk = int(round(kk))
            fig = FIG(fig_coll('free', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1, kt='%d N/m' % kk), '66%')
            body = P(base + '용수철 상수가 %d N/m일 때 용수철의 최대 압축 길이는?' % kk + tail) + fig
            return mc(body, U(x, 'm'), wr(x, [x * 2, x / 2, v1 * math.sqrt(m1 / kk), math.sqrt(2 * 0.5 * m1 * v1 * v1 / kk), x * math.sqrt(2), x * M / m1], 'm'), r=r, lv='상', fam='b',
                      steps=['최대 압축 시 두 물체의 속도 v = %d × %d / %d = %s m/s' % (m1, v1, M, fs(v)), '탄성 에너지 = ½ × %d × %d² - ½ × %d × %s² = %s J' % (m1, v1, M, fs(v), fs(Es)), '½kx² = %s → x² = 2 × %s / %d = %s, x = %s m' % (fs(Es), fs(Es), kk, fs(x * x, 4), fs(x)),
                             '(검산) ½ × %d × %s² = %s J' % (kk, fs(x), fs(0.5 * kk * x * x))],
                      core='최대 압축은 두 물체가 같은 속도가 될 때이다.', point='충돌 후 합체하는 경우(벽 고정)와 달리 자유로운 두 물체는 상대 운동 에너지만 저장된다.')
        # 용수철이 원래 길이로 돌아온 뒤(탄성 충돌) 속도
        va = (m1 - m2) / M * v1
        vb = 2 * m1 / M * v1
        if abs(va) < 1e-9: return None
        assert abs(m1 * va + m2 * vb - m1 * v1) < 1e-9
        assert abs(0.5 * m1 * va ** 2 + 0.5 * m2 * vb ** 2 - 0.5 * m1 * v1 ** 2) < 1e-6
        if not cl(va, 2) or not cl(vb, 2): return None
        fig = FIG(fig_coll('free', '%d kg' % m1, '%d kg' % m2, v1='%d m/s' % v1), '66%')
        body = P(base.replace('A가 용수철과 충돌하며 용수철이 압축된다. ', '') + '용수철이 최대로 압축되었다가 원래 길이로 돌아와 두 물체가 떨어진 뒤 B의 속력(오른쪽 방향)은? (단, 용수철의 질량과 모든 마찰은 무시한다.)') + fig
        return mc(body, U(vb, 'm/s'), wr(vb, [v1, abs(va), m1 * v1 / M, v1 * m1 / m2, vb / 2, 2 * v1], 'm/s'), r=r, lv='상', fam='b',
                  steps=['용수철이 원래 길이로 돌아오면 역학적 에너지가 보존된다(탄성 충돌과 같다).', '운동량 : %d × %d = %d·vA + %d·vB, 에너지 : ½ × %d × %d² = ½ × %d × vA² + ½ × %d × vB²' % (m1, v1, m1, m2, m1, v1, m1, m2),
                         '풀면 vB = 2m₁v₁/(m₁+m₂) = 2 × %d × %d / %d = %s m/s, vA = (m₁-m₂)v₁/(m₁+m₂) = %s m/s' % (m1, v1, M, fs(vb), fs(va)), '(검산) 에너지 %s J = %s J + %s J' % (fs(0.5 * m1 * v1 * v1), fs(0.5 * m1 * va * va), fs(0.5 * m2 * vb * vb))],
                  core='용수철을 통한 충돌은 탄성 충돌이므로 운동량과 역학적 에너지가 모두 보존된다.', point='두 보존 법칙을 연립하여 충돌 후 속도를 구한다.')
    if form == 'slope':
        vv = r.choice([2, 4, 5, 6, 8, 10])
        h = vv * vv / 20.0
        v = F(m1 * vv, M)
        if not cl(v, 2): return None
        v = float(v)
        E = 0.5 * M * v * v
        x = r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5])
        kk = 2 * E / (x * x)
        if abs(kk - round(kk)) > 1e-6 or kk < 20 or kk > 3000: return None
        kk = int(round(kk))
        assert abs(m1 * G * h - 0.5 * m1 * vv * vv) < 1e-9
        ask = r.choice(['x', 'k', 'k'])
        ht = '%s m' % fs(h)
        base = '그림과 같이 마찰이 없는 빗면 위 높이 %s m인 지점에서 질량 %d kg인 물체 A를 가만히 놓았더니 수평면에 내려와, 벽에 고정된 용수철 앞에 정지해 있던 질량 %d kg인 물체 B와 충돌한 뒤 한 덩어리가 되어 용수철을 압축시켰다. ' % (fs(h), m1, m2)
        if ask == 'x':
            fig = FIG(fig_coll('slope', '%d kg' % m1, '%d kg' % m2, kt='%d N/m' % kk, h=ht), '68%')
            body = P(base + '용수철 상수가 %d N/m일 때 용수철의 최대 압축 길이는? (단, 중력 가속도는 10 m/s²이고, 용수철의 질량과 모든 마찰은 무시한다.)' % kk) + fig
            return mc(body, U(x, 'm'), wr(x, [x * 2, x / 2, vv * math.sqrt(m1 / kk), math.sqrt(2 * m1 * G * h / kk), x * M / m1, x * math.sqrt(M / m1)], 'm'), r=r, lv='상', fam='c',
                      steps=['빗면 : 에너지 보존 m₁gh = ½m₁v₁² → v₁ = √(2 × 10 × %s) = %d m/s' % (fs(h), vv), '충돌 : 운동량 보존 %d × %d = (%d + %d)v → v = %s m/s' % (m1, vv, m1, m2, fs(v)),
                             '압축 : ½ × %d × %s² = ½ × %d × x² → x = %s m' % (M, fs(v), kk, fs(x)), '(검산) ½kx² = %s J = ½(m₁+m₂)v² = %s J' % (fs(0.5 * kk * x * x), fs(E))],
                      core='에너지 보존(빗면) → 운동량 보존(충돌) → 에너지 보존(용수철)의 세 단계로 풀이한다.', point='각 구간에 알맞은 보존 법칙을 순서대로 적용한다.')
        fig = FIG(fig_coll('slope', '%d kg' % m1, '%d kg' % m2, kt='k', h=ht), '68%')
        body = P(base + '용수철이 최대로 %s m 압축되었다. 용수철 상수 k는? (단, 중력 가속도는 10 m/s²이고, 용수철의 질량과 모든 마찰은 무시한다.)' % fs(x)) + fig
        return mc(body, U(kk, 'N/m'), wr(kk, [kk * 2, kk / 2, 2 * m1 * G * h / (x * x), kk * M / m1, 2 * 0.5 * m1 * vv * vv / (x * x) * m1 / M * 2, kk * (M / m1) ** 2], 'N/m'), r=r, lv='상', fam='c',
                  steps=['충돌 직전 속력 v₁ = √(2gh) = √(2 × 10 × %s) = %d m/s' % (fs(h), vv), '충돌 직후 v = m₁v₁/(m₁+m₂) = %d × %d / %d = %s m/s' % (m1, vv, M, fs(v)), '½kx² = ½(m₁+m₂)v² → k = %d × %s² / %s² = %d N/m' % (M, fs(v), fs(x), kk),
                         '(검산) 에너지 ½ × %d × %s² = %s J = ½ × %d × %s² = %s J' % (M, fs(v), fs(E), kk, fs(x), fs(0.5 * kk * x * x))],
                  core='충돌에서 줄어든 에너지 때문에 mgh 전부가 탄성 에너지가 되지 않는다.', point='처음 높이 → 충돌 전 속력 → 충돌 후 속력 → 탄성 에너지로 연결한다.')
    # rough: 합체 후 거친 수평면에서 용수철 압축 또는 정지 거리
    v1 = r.choice([2, 3, 4, 5, 6, 8, 10, 12])
    v = F(m1 * v1, M)
    if not cl(v, 2): return None
    v = float(v)
    E = 0.5 * M * v * v
    mu = r.choice([0.1, 0.2, 0.25, 0.4, 0.5])
    ask = r.choice(['d', 'd', 'k'])
    base = '그림과 같이 질량 %d kg인 물체 A가 %d m/s의 속력으로 운동하여 정지해 있던 질량 %d kg인 물체 B와 충돌한 뒤 한 덩어리가 되어 운동한다. 수평면과 물체 사이의 운동 마찰 계수는 %s이다. ' % (m1, v1, m2, fs(mu))
    if ask == 'd':
        d = v * v / (2 * mu * G)
        if not cl(d, 2): return None
        d2 = E / (mu * M * G)
        assert abs(d - d2) < 1e-6
        fig = FIG(_fig_rough(m1, m2, v1, mu), '66%')
        body = P(base + '한 덩어리가 된 두 물체가 정지할 때까지 이동한 거리는? (단, 중력 가속도는 10 m/s²이다.)') + fig
        return mc(body, U(d, 'm'), wr(d, [v1 * v1 / (2 * mu * G), d * 2, d / 2, E / (mu * m1 * G), d * M / m1, v * v / (mu * G)], 'm'), r=r, lv='중', fam='d',
                  steps=['충돌 : 운동량 보존 %d × %d = %d·v → v = %s m/s' % (m1, v1, M, fs(v)), '마찰력에 의한 감속 a = μg = %s × 10 = %s m/s², d = v²/2a = %s² / %s = %s m' % (fs(mu), fs(mu * G), fs(v), fs(2 * mu * G), fs(d)),
                         '(검산) 에너지 ½(m₁+m₂)v² = μ(m₁+m₂)g·d : %s J = %s × %d × 10 × %s = %s J' % (fs(E), fs(mu), M, fs(d), fs(mu * M * G * d))],
                  core='충돌 직후 운동 에너지는 마찰열로 모두 소모된다.', point='충돌(운동량)과 감속 운동(일·에너지)을 연결한다.')
    # k : 거친 면에서 용수철 압축
    x = r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5])
    kk = 2 * (E - mu * M * G * x) / (x * x)
    if kk < 20 or abs(kk - round(kk)) > 1e-6 or kk > 3000: return None
    kk = int(round(kk))
    assert abs(E - (0.5 * kk * x * x + mu * M * G * x)) < 1e-6
    fig = FIG(_fig_rough(m1, m2, v1, mu, spring=True), '66%')
    body = P(base.replace('한 덩어리가 되어 운동한다.', '한 덩어리가 되어 운동하다가 벽에 고정된 용수철을 최대 %s m 압축시켰다.' % fs(x)) + '용수철 상수 k는? (단, 중력 가속도는 10 m/s²이고, 용수철의 질량은 무시한다.)') + fig
    return mc(body, U(kk, 'N/m'), wr(kk, [2 * E / (x * x), kk * 2, kk / 2, 2 * (E + mu * M * G * x) / (x * x), 2 * (0.5 * m1 * v1 * v1 - mu * M * G * x) / (x * x)], 'N/m'), r=r, lv='상', fam='d',
              steps=['충돌 직후 속력 v = %d × %d / %d = %s m/s, 운동 에너지 ½ × %d × %s² = %s J' % (m1, v1, M, fs(v), M, fs(v), fs(E)), '압축하는 동안 마찰열 μ(m₁+m₂)g·x = %s × %d × 10 × %s = %s J' % (fs(mu), M, fs(x), fs(mu * M * G * x)),
                     '운동 에너지 = 탄성 에너지 + 마찰열 : %s = ½ × k × %s² + %s' % (fs(E), fs(x), fs(mu * M * G * x)), 'k = 2 × (%s - %s) / %s = %d N/m' % (fs(E), fs(mu * M * G * x), fs(x * x, 4), kk)],
              core='마찰이 있으면 운동 에너지가 탄성 에너지와 마찰열로 나뉜다.', point='충돌 직후 에너지에서 마찰열을 빼고 탄성 에너지를 구한다.')


def _fig_rough(m1, m2, v1, mu, spring=False, w=330, hh=165):
    f = Fig(w, hh)
    fy = hh - 44
    f.line(10, fy, w - 8, fy, INK, 1.7)
    for i in range(10, w - 8, 8):
        f.line(i, fy, i - 5, fy + 6, GR, 1)
    bw, bh = 40, 30
    b2 = 160 if not spring else 150
    b1 = 56
    _blk(f, b2, fy, bw, bh, 'B', '#f6d9d6')
    _blk(f, b1, fy, bw, bh, 'A')
    f.arrow(b1 + bw / 2, fy - bh - 16, b1 + bw / 2 + 46, fy - bh - 16, RD, 2.4)
    f.text(b1 + bw / 2, fy - bh - 24, '%d m/s' % v1, 12.5, 'start', True, RD)
    f.text(b1 + bw / 2, fy + 24, '%d kg' % m1, 12.5, bold=True, c=GR)
    f.text(b2 + bw / 2, fy + 24, '%d kg' % m2, 12.5, bold=True, c=GR)
    f.text(w - 14, fy + 38, 'μ = %s' % fs(mu), 12.5, 'end', True, RD)
    if spring:
        wx = w - 22
        f.line(wx, fy - 50, wx, fy, GR, 3)
        for v in range(fy - 48, fy, 8):
            f.line(wx, v, wx + 6, v - 6, GR, 1)
        f.spring(b2 + bw, fy - bh / 2, wx, 5, 7)
    return f.svg()


# ================================================================== ph109 원운동과 에너지(연직면)
COSV = {30: None, 37: F(4, 5), 53: F(3, 5), 60: F(1, 2), 90: F(0), 45: None}
COSS = {37: '4/5', 53: '3/5', 60: '1/2', 90: '0'}


def fig_pend(th, Ltxt=None, mtxt='m', vtxt=None, htxt=None, w=300, hh=200, show_ang=True):
    """줄에 매달린 추. th: 처음 줄이 연직과 이루는 각(왼쪽). vtxt: 최저점에서 속력 라벨."""
    f = Fig(w, hh)
    px, py = 175, 22
    L = 130
    f.line(px - 50, py, px + 50, py, GR, 3)
    for i in range(-50, 50, 8):
        f.line(px + i, py, px + i + 6, py - 7, GR, 1)
    t = math.radians(th)
    bx0, by0 = px - L * math.sin(t), py + L * math.cos(t)
    bx1, by1 = px, py + L
    # 호
    pts = []
    for i in range(41):
        a = -t + 2 * t * i / 40
        pts.append((px + L * math.sin(a), py + L * math.cos(a)))
    f.poly(pts, 'none', BL, 1.6, close=False, dash='5 3')
    f.line(px, py, px, py + L, GR, 1, '4 3')
    f.line(px, py, bx0, by0, INK, 1.8)
    f.circ(bx0, by0, 11, '#cfe2f7', INK, 1.7)
    f.text(bx0 - 16, by0 + 4, mtxt, 12.5, 'end', True, INK, True)
    f.circ(bx1, by1, 11, '#eef3fa', INK, 1.3, '3 2')
    f.circ(px, py, 3, INK, INK, 1)
    if th > 0 and show_ang:
        f.path('M %s %s A 40 40 0 0 0 %s %s' % (Fig._n(px), Fig._n(py + 40), Fig._n(px - 40 * math.sin(t)), Fig._n(py + 40 * math.cos(t))), 'none', GR, 1.2)
        f.text(px - 22 * math.sin(t / 2) - 10, py + 66, '%d°' % th, 12.5, 'end', True, GR)
    if Ltxt:
        mx, my = (px + bx0) / 2, (py + by0) / 2
        f.text(mx - 8, my - 4, Ltxt, 12.5, 'end', True, GR)
    if vtxt:
        f.arrow(bx1 - 4, by1 + 22, bx1 + 40, by1 + 22, RD, 2.2)
        f.text(bx1 + 8, by1 + 38, vtxt, 12.5, 'start', True, RD)
    if htxt:
        f.line(bx0 - 22, by0, bx0 - 22, by1, GR, 1.2)
        f._head(bx0 - 22, by0, bx0 - 22, by1, GR, 1.2, 7)
        f._head(bx0 - 22, by1, bx0 - 22, by0, GR, 1.2, 7)
        f.line(bx0 - 28, by1, bx1 - 14, by1, GR, 1, '4 3')
        f.text(bx0 - 28, (by0 + by1) / 2 + 4, htxt, 12.5, 'end', True, GR)
    return f.svg()


def fig_circle(Rtxt, vtxt, mtxt='m', w=300, hh=210):
    """연직 원운동 : 최저점에서 속력 v 로 지나는 추."""
    f = Fig(w, hh)
    cx, cy, R = 150, 90, 70
    f.circ(cx, cy, R, 'none', BL, 1.6, '5 3')
    f.line(cx, cy, cx, cy + R, INK, 1.8)
    f.circ(cx, cy, 3, INK, INK, 1)
    f.circ(cx, cy + R, 11, '#cfe2f7', INK, 1.7)
    f.text(cx - 16, cy + R + 4, mtxt, 12.5, 'end', True, INK, True)
    f.text(cx + 6, cy + R / 2 + 4, Rtxt, 12.5, 'start', True, GR)
    f.arrow(cx + 16, cy + R + 22, cx + 66, cy + R + 22, RD, 2.2)
    f.text(cx + 20, cy + R + 40, vtxt, 12.5, 'start', True, RD)
    f.circ(cx, cy - R, 4, RD, RD, 1)
    f.text(cx + 8, cy - R - 6, '최고점', 12, 'start', False, GR)
    return f.svg()


def fig_loop(htxt, Rtxt, w=330, hh=220):
    """빗면에서 내려와 연직 원형 레일(반지름 R)을 지나는 물체."""
    f = Fig(w, hh)
    R = 40
    fy = hh - 24
    top = 34
    cx, cy = 190, fy - R
    f.line(10, fy, w - 10, fy, INK, 1.6)
    for i in range(10, w - 10, 8):
        f.line(i, fy, i - 5, fy + 6, GR, 1)
    x0 = 26
    f.poly([(x0, top), (cx - 52, fy), (x0, fy)], '#f1f4f8', INK, 1.8)
    f.circ(cx, cy, R, 'none', INK, 2.2)
    f.circ(cx, cy, 2.5, GR, GR, 1)
    f.line(cx, cy, cx + R * math.cos(math.radians(40)), cy - R * math.sin(math.radians(40)), GR, 1.2)
    f.text(cx + 8, cy - 4, Rtxt, 12.5, 'start', True, GR)
    f.circ(x0 + 8, top - 7, 7, '#cfe2f7', INK, 1.7)
    f.line(x0 + 15, top - 14 + 7, cx + R + 8, top - 7, GR, 1, '4 3') if False else f.line(x0 + 8, top - 14, cx + R + 6, top - 14, GR, 1, '4 3')
    f.line(cx + R + 2, top - 14, cx + R + 2, fy, GR, 1.2)
    f._head(cx + R + 2, top - 14, cx + R + 2, fy, GR, 1.2, 7)
    f._head(cx + R + 2, fy, cx + R + 2, top - 14, GR, 1.2, 7)
    f.text(cx + R + 8, (top + fy) / 2, htxt, 12.5, 'start', True, GR)
    return f.svg()


CIRC = [(R_, v_) for R_ in (0.2, 0.25, 0.4, 0.5, 0.6, 0.8, 1, 1.2, 1.5, 2, 2.5, 3, 4) for v_ in range(3, 31) if v_ * v_ >= 50 * R_ and cl(math.sqrt(v_ * v_ - 40 * R_))]


@T('ph109')
@balanced
def g109(r, k):
    form = pick(r, ['pend', 'pend', 'pend', 'circ', 'circ', 'circ', 'circ', 'circ', 'circ', 'loop', 'loop', 'rope', 'bogi', 'bogi'])
    m = r.choice([0.5, 1, 2, 3, 4, 5])
    tail = ' (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)'
    if form in ('pend', 'rope', 'bogi'):
        th = r.choice([37, 53, 60, 90])
        c = float(COSV[th])
        Lv = r.choice([0.4, 0.5, 0.8, 1, 1.2, 1.5, 2, 2.5])
        v2 = 2 * G * Lv * (1 - c)
        if v2 <= 0: return None
        v = math.sqrt(v2)
        if form != 'rope' and not cl(v, 2): return None
        T = m * G * (3 - 2 * c)
        assert abs(T - (m * G + m * v2 / Lv)) < 1e-6
        ask = r.choice(['v', 'v', 'T', 'T', 'KE', 'ratio'])
        if form == 'pend':
            fig = FIG(fig_pend(th, Ltxt='%s m' % fs(Lv)), '58%')
            base = '그림과 같이 길이 %s m인 가벼운 줄에 질량 %s kg인 추를 매달고 줄이 연직 방향과 %d°를 이루는 위치에서 가만히 놓았더니 추가 원호를 따라 운동하였다. ' % (fs(Lv), fs(m), th)
            if ask == 'v':
                body = P(base + '추가 가장 낮은 지점을 지날 때의 속력은?' + tail) + fig
                return mc(body, U(v, 'm/s'), wr(v, [math.sqrt(2 * G * Lv), math.sqrt(2 * G * Lv * c), math.sqrt(G * Lv * (1 - c)), v * 2, v / 2, math.sqrt(2 * G * Lv * (1 - c)) * c], 'm/s'), r=r, lv='하', fam='a',
                          steps=['내려온 높이 h = L(1 - cos%d°) = %s × (1 - %s) = %s m' % (th, fs(Lv), COSS[th], fs(Lv * (1 - c))), '역학적 에너지 보존 : v = √(2gh) = √(2 × 10 × %s) = %s m/s' % (fs(Lv * (1 - c)), fs(v)),
                                 '(검산) 구한 속력으로 ½mv² = %s J = mgh = %s J' % (fs(0.5 * m * v2), fs(m * G * Lv * (1 - c)))],
                          core='진자의 높이 차는 L(1 - cosθ)이며, 줄의 장력은 일을 하지 않아 역학적 에너지가 보존된다.', point='각도로부터 높이를 구해 에너지 보존을 쓴다.')
            if ask == 'T':
                body = P(base + '추가 가장 낮은 지점을 지날 때 줄이 추를 당기는 힘의 크기는?' + tail) + fig
                return mc(body, U(T, 'N'), wr(T, [m * G, m * v2 / Lv, m * G * (2 - c), m * G * (3 - 2 * c) * 2 / 3, m * G * 3, m * G * (1 + 2 * c)], 'N'), r=r, lv='중', fam='a',
                          steps=['최저점 속력 : v² = 2gL(1 - cos%d°) = 2 × 10 × %s × %s = %s' % (th, fs(Lv), fs(1 - c), fs(v2)), '원운동의 구심력 : T - mg = mv²/L → T = %s × 10 + %s × %s / %s = %s N' % (fs(m), fs(m), fs(v2), fs(Lv), fs(T)),
                                 '(검산) T = mg(3 - 2cos%d°) = %s × (3 - %s) = %s N' % (th, fs(m * G), fs(2 * c), fs(T))],
                          core='최저점에서 장력과 중력의 합력이 구심력이므로 T = mg + mv²/L 이다.', point='에너지 보존으로 속력을 구한 뒤 구심력 식에 대입한다.')
            if ask == 'KE':
                ke = 0.5 * m * v2
                body = P(base + '추가 가장 낮은 지점을 지날 때 추의 운동 에너지는?' + tail) + fig
                return mc(body, U(ke, 'J'), wr(ke, [m * G * Lv, m * G * Lv * c, ke * 2, ke / 2, m * G * Lv * (1 + c)], 'J'), r=r, lv='하', fam='a',
                          steps=['높이 차 h = L(1 - cos%d°) = %s × %s = %s m' % (th, fs(Lv), fs(1 - c), fs(Lv * (1 - c))), 'Ek = mgh = %s × 10 × %s = %s J' % (fs(m), fs(Lv * (1 - c)), fs(ke)), '(검산) v = %s m/s, ½mv² = %s J' % (fs(v), fs(0.5 * m * v * v))],
                          core='위치 에너지 감소량이 운동 에너지 증가량이다.', point='높이 차를 올바르게 구한다.')
            body = P(base + '추가 가장 낮은 지점을 지날 때 줄의 장력의 크기는 추의 무게의 몇 배인가?' + tail) + fig
            ratio = 3 - 2 * c
            wl = [fs(y) + '배' for y in [3, 1, 2 - c, 3 - c, 1 + 2 * c, 2 * (1 - c), 3 + 2 * c] if abs(y - ratio) > 1e-9 and y > 0 and cl(y)]
            return mc(body, fs(ratio) + '배', wl, r=r, lv='중', fam='a', sort='shuf',
                      steps=['v² = 2gL(1 - cosθ), T - mg = mv²/L = 2mg(1 - cosθ)', 'T = mg(3 - 2cosθ) = mg × (3 - 2 × %s) = %s mg' % (COSS[th], fs(ratio)), '(검산) v² = %s, mv²/L = %s mg' % (fs(v2), fs(v2 / (Lv * G)))],
                      core='진자 최저점의 장력은 T = mg(3 - 2cosθ)로 줄의 길이와 무관하다.', point='에너지와 구심력의 결합에서 L이 소거된다.')
        if form == 'rope':
            # 줄의 최대 장력으로부터 최대 처음 각도 (높이)
            Tmax = T
            hmax = Lv * (1 - c)
            fig = FIG(fig_pend(th, Ltxt='%s m' % fs(Lv), show_ang=False), '58%')
            body = P('길이 %s m인 가벼운 줄에 질량 %s kg인 추를 매달고 줄이 연직 방향과 일정한 각을 이루는 위치에서 가만히 놓는다. 이 줄은 장력이 %s N을 넘으면 끊어진다. 줄이 끊어지지 않고 추를 놓을 수 있는 가장 높은 위치는 가장 낮은 지점보다 몇 m 높은가?' % (fs(Lv), fs(m), fs(Tmax)) + tail) + fig
            return mc(body, U(hmax, 'm'), wr(hmax, [Lv * c, Lv, Lv * (1 - c) * 2, Lv * (1 - c) / 2, Lv * (3 * m * G - Tmax) / (2 * m * G) * 2, Lv * (2 - c)], 'm'), r=r, lv='상', fam='d',
                      steps=['최저점에서 장력이 가장 크다 : T = mg + mv²/L = %s N' % fs(Tmax), 'mv²/L = %s - %s = %s N → v² = %s' % (fs(Tmax), fs(m * G), fs(Tmax - m * G), fs((Tmax - m * G) * Lv / m)),
                             '에너지 보존 : h = v²/2g = %s / 20 = %s m' % (fs((Tmax - m * G) * Lv / m), fs(hmax)), '(검산) cosθ = (3mg - T)/(2mg) = %s, h = L(1 - cosθ) = %s m' % (fs((3 * m * G - Tmax) / (2 * m * G), 3), fs(hmax))],
                      core='진자의 장력은 최저점에서 최대이며, 최저점 장력과 속력, 높이가 에너지 보존으로 연결된다.', point='장력 조건에서 속력, 다시 높이를 역으로 구한다.')
        # 보기형
        c1 = c
        tops = [
            ('추가 가장 낮은 지점을 지날 때 속력은 %s m/s이다.' % fs(v), '추가 가장 낮은 지점을 지날 때 속력은 %s m/s이다.' % fs(math.sqrt(2 * G * Lv)), 'h = L(1 - cos%d°) 이므로 v = √(2gh) = %s m/s 이다.' % (th, fs(v)), '높이 차는 L 이 아니라 L(1 - cos%d°) 이므로 v = %s m/s 이다.' % (th, fs(v))),
            ('최저점에서 줄의 장력은 추의 무게보다 크다.', '최저점에서 줄의 장력은 추의 무게와 같다.', 'T - mg = mv²/L > 0 이므로 T > mg 이다.', '원운동의 구심력이 위쪽으로 필요하므로 T = mg + mv²/L > mg 이다.'),
            ('최저점에서 줄의 장력은 %s N이다.' % fs(T), '최저점에서 줄의 장력은 %s N이다.' % fs(m * G), 'T = mg + mv²/L = %s N 이다.' % fs(T), 'mg = %s N 은 중력이며 장력은 mg + mv²/L = %s N 이다.' % (fs(m * G), fs(T))),
            ('줄의 장력은 추에 일을 하지 않는다.', '줄의 장력은 추에 양(+)의 일을 한다.', '장력은 운동 방향과 항상 수직이므로 일이 0이다.', '장력은 추의 이동 방향과 수직이라 일을 하지 않는다.'),
            ('추가 내려오는 동안 추의 역학적 에너지는 보존된다.', '추가 내려오는 동안 추의 운동량은 보존된다.', '중력만 일을 하므로 역학적 에너지가 보존된다.', '중력과 장력이 작용하여 운동량은 변한다.'),
            ('최저점에서 추의 가속도의 방향은 위쪽(연직 위)이다.', '최저점에서 추의 가속도는 0이다.', '구심 가속도가 원의 중심(위쪽)을 향한다.', '원운동 중이므로 구심 가속도 v²/L = %s m/s² 이 있다.' % fs(v2 / Lv)),
            ('같은 높이에서 질량이 더 큰 추를 놓아도 최저점 속력은 같다.', '같은 높이에서 질량이 더 큰 추를 놓으면 최저점 속력은 더 크다.', 'mgh = ½mv² 에서 m 이 소거된다.', '속력은 √(2gh)로 질량과 무관하다.'),
        ]
        fig = FIG(fig_pend(th, Ltxt='%s m' % fs(Lv)), '58%')
        return topics_bogi(r, tops, '그림과 같이 길이 %s m인 가벼운 줄에 질량 %s kg인 추를 매달고 줄이 연직 방향과 %d°를 이루는 위치에서 가만히 놓았다. 추가 원호를 따라 운동할 때 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)' % (fs(Lv), fs(m), th),
                           pre=fig, fam='e', lv='중', core='진자 운동에서 역학적 에너지는 보존되고 최저점 장력은 mg + mv²/L 이다.', point='에너지와 구심력을 함께 판단한다.')
    if form == 'circ':
        R, v0 = r.choice(CIRC)
        if v0 * v0 < 50 * R + 1e-9: return None
        vt2 = v0 * v0 - 40 * R
        vt = math.sqrt(vt2)
        if not cl(vt, 2): return None
        Tt = m * (vt2 / R - G)
        Tb = m * (v0 * v0 / R + G)
        assert abs((Tb - Tt) - 6 * m * G) < 1e-6
        # 에너지 교차 검증 : ½mv0² = ½mvt² + mg(2R)
        assert abs(0.5 * m * v0 * v0 - (0.5 * m * vt2 + m * G * 2 * R)) < 1e-6
        ask = r.choice(['vt', 'vt', 'Tt', 'Tb', 'diff', 'vmin'])
        fig = FIG(fig_circle('R = %s m' % fs(R), 'v₀ = %d m/s' % v0), '56%')
        base = '그림과 같이 길이 %s m인 가벼운 줄에 질량 %s kg인 추를 매달고 연직면에서 원운동시킨다. 추가 최저점을 지날 때의 속력은 %d m/s이다. ' % (fs(R), fs(m), v0)
        if ask == 'vt':
            body = P(base + '추가 최고점을 지날 때의 속력은? (단, 줄은 항상 팽팽하다.)' + tail) + fig
            return mc(body, U(vt, 'm/s'), wr(vt, [v0, v0 - 2 * math.sqrt(G * R), math.sqrt(v0 * v0 - 20 * R), math.sqrt(v0 * v0 - 80 * R) if v0 * v0 > 80 * R else vt + 1, vt / 2, v0 / 2], 'm/s'), r=r, lv='중', fam='b',
                      steps=['최저점과 최고점의 높이 차는 2R = %s m' % fs(2 * R), '역학적 에너지 보존 : ½mv₀² = ½mv² + mg(2R) → v² = v₀² - 4gR = %d² - 40 × %s = %s' % (v0, fs(R), fs(vt2)), 'v = %s m/s' % fs(vt),
                             '(검산) ½mv² + mg·2R = %s + %s = %s J = ½mv₀²' % (fs(0.5 * m * vt2), fs(m * G * 2 * R), fs(0.5 * m * v0 * v0))],
                      core='연직 원운동에서 최저점과 최고점의 높이 차는 지름 2R 이다.', point='에너지 보존으로 최고점 속력을 구한다.')
        if ask == 'Tt':
            body = P(base + '추가 최고점을 지날 때 줄의 장력의 크기는?' + tail) + fig
            return mc(body, U(Tt, 'N'), wr(Tt, [Tb, m * vt2 / R, m * (vt2 / R + G), m * (v0 * v0 / R - G), m * G, Tt + 2 * m * G], 'N'), r=r, lv='상', fam='b',
                      steps=['최고점 속력 : v² = v₀² - 4gR = %d² - 40 × %s = %s' % (v0, fs(R), fs(vt2)), '최고점에서 장력과 중력이 모두 아래(중심) 방향 : T + mg = mv²/R', 'T = %s × %s / %s - %s × 10 = %s N' % (fs(m), fs(vt2), fs(R), fs(m), fs(Tt)),
                             '(검산) 최저점 장력 T₀ = mg + mv₀²/R = %s N, T₀ - T = %s N = 6mg' % (fs(Tb), fs(Tb - Tt))],
                      core='최고점에서는 중력도 구심력 방향이므로 T + mg = mv²/R 이다.', point='에너지 보존 후 최고점에서 구심력 식을 세운다.')
        if ask == 'Tb':
            body = P(base + '추가 최저점을 지날 때 줄의 장력의 크기는?' + tail) + fig
            return mc(body, U(Tb, 'N'), wr(Tb, [m * v0 * v0 / R, m * (v0 * v0 / R - G), m * G, Tt, Tb * 2], 'N'), r=r, lv='하', fam='b',
                      steps=['최저점에서 구심력은 위쪽 : T - mg = mv₀²/R', 'T = mg + mv₀²/R = %s × 10 + %s × %d² / %s = %s N' % (fs(m), fs(m), v0, fs(R), fs(Tb))],
                      core='최저점에서 장력은 구심력과 중력의 합이다.', point='장력과 중력의 방향을 구분한다.')
        if ask == 'diff':
            body = P(base + '추가 최저점과 최고점을 지날 때 줄의 장력의 크기 차는? (단, 줄은 항상 팽팽하다.)' + tail) + fig
            d = 6 * m * G
            return mc(body, U(d, 'N'), wr(d, [4 * m * G, 2 * m * G, 5 * m * G, 3 * m * G, 8 * m * G, m * G], 'N'), r=r, lv='중', fam='b',
                      steps=['최저점 : T₁ = mg + mv₀²/R, 최고점 : T₂ = mv²/R - mg, v² = v₀² - 4gR', 'T₁ - T₂ = 2mg + m(v₀² - v²)/R = 2mg + 4mg = 6mg = %s N' % fs(d), '(검산) T₁ = %s N, T₂ = %s N, 차 = %s N' % (fs(Tb), fs(Tt), fs(Tb - Tt))],
                      core='연직 원운동에서 최저점과 최고점의 장력 차는 속력과 관계없이 6mg 이다.', point='에너지 보존과 구심력 식을 연립하면 속력이 소거된다.')
        # vmin
        R2 = r.choice([0.5, 2, 4.5, 8])
        vm = math.sqrt(5 * G * R2)
        assert cl(vm)
        fig = FIG(fig_circle('R = %s m' % fs(R2), 'v₀'), '56%')
        body = P('그림과 같이 길이 %s m인 가벼운 줄에 질량 %s kg인 추를 매달고 연직면에서 원운동시킨다. 줄이 느슨해지지 않고 추가 한 바퀴 돌려면 최저점에서 가져야 하는 최소 속력 v₀는?' % (fs(R2), fs(m)) + tail) + fig
        return mc(body, U(vm, 'm/s'), wr(vm, [math.sqrt(G * R2), math.sqrt(2 * G * R2), math.sqrt(4 * G * R2), math.sqrt(3 * G * R2), math.sqrt(6 * G * R2)], 'm/s'), r=r, lv='중', fam='b',
                  steps=['최고점에서 장력이 0일 때의 속력이 최소 : mg = mv²/R → v² = gR = %s' % fs(G * R2), '에너지 보존 : ½mv₀² = ½mv² + mg(2R) → v₀² = gR + 4gR = 5gR = %s' % fs(5 * G * R2), 'v₀ = %s m/s' % fs(vm),
                         '(검산) 최고점 장력 T = m(v²/R - g) = %s N' % fs(m * (G * R2 / R2 - G))],
                  core='연직 원운동 완주의 조건은 최고점에서 v ≥ √(gR)이고, 이때 최저점 속력은 √(5gR) 이상이다.', point='최고점 조건과 에너지 보존을 연결한다.')
    # loop
    R = r.choice([0.2, 0.4, 0.5, 0.8, 1, 1.2, 1.5, 2])
    h = r.choice([0.5, 0.8, 1, 1.2, 1.5, 2, 2.4, 3, 4, 5])
    if h < 2.5 * R + 1e-9: return None
    vt2 = 2 * G * (h - 2 * R)
    Nt = m * (vt2 / R - G)
    Nb = m * G * (1 + 2 * h / R)
    assert abs(Nb - (m * G + m * 2 * G * h / R)) < 1e-6
    assert abs(Nt - (m * G * (2 * h / R - 5))) < 1e-6
    if not cl(Nt, 2) or not cl(Nb, 2) or Nt < 0: return None
    ask = r.choice(['Nt', 'Nt', 'Nb', 'hmin', 'vt'])
    fig = FIG(fig_loop('h = %s m' % fs(h) if ask != 'h' else 'h', 'R = %s m' % fs(R)), '62%')
    base = '그림과 같이 마찰이 없는 빗면 위 높이 %s m인 지점에서 질량 %s kg인 물체를 가만히 놓았더니, 물체가 빗면을 내려와 반지름 %s m인 연직 원형 레일의 안쪽을 따라 운동한다. ' % (fs(h), fs(m), fs(R))
    if ask == 'vt':
        vt = math.sqrt(vt2)
        if not cl(vt, 2): return None
        body = P(base + '물체가 원형 레일의 최고점을 지날 때의 속력은?' + tail) + fig
        return mc(body, U(vt, 'm/s'), wr(vt, [math.sqrt(2 * G * h), math.sqrt(2 * G * (h - R)), math.sqrt(G * R), math.sqrt(2 * G * (h - 2 * R)) / 2, math.sqrt(2 * G * (h + 2 * R))], 'm/s'), r=r, lv='하', fam='c',
                  steps=['처음 위치와 최고점의 높이 차 = h - 2R = %s - %s = %s m' % (fs(h), fs(2 * R), fs(h - 2 * R)), '에너지 보존 : v = √(2g(h - 2R)) = √(2 × 10 × %s) = %s m/s' % (fs(h - 2 * R), fs(vt))],
                  core='마찰이 없으면 처음 높이와의 차이만큼 운동 에너지가 생긴다.', point='원형 레일의 최고점 높이는 2R 이다.')
    if ask == 'Nt':
        body = P(base + '물체가 원형 레일의 최고점을 지날 때 레일이 물체에 작용하는 수직 항력의 크기는?' + tail) + fig
        return mc(body, U(Nt, 'N'), wr(Nt, [m * vt2 / R, m * (vt2 / R + G), Nb, m * G, m * (2 * G * h / R - G)], 'N'), r=r, lv='상', fam='c',
                  steps=['최고점 속력 : v² = 2g(h - 2R) = 2 × 10 × (%s - %s) = %s' % (fs(h), fs(2 * R), fs(vt2)), '최고점에서 수직 항력 N 과 중력 mg 모두 아래 방향 : N + mg = mv²/R', 'N = %s × %s / %s - %s × 10 = %s N' % (fs(m), fs(vt2), fs(R), fs(m), fs(Nt)),
                         '(검산) N = mg(2h/R - 5) = %s × (%s - 5) = %s N' % (fs(m * G), fs(2 * h / R), fs(Nt))],
                  core='최고점에서 N + mg = mv²/R, 속력은 에너지 보존으로 구한다.', point='에너지 보존과 구심력을 연결한다.')
    if ask == 'Nb':
        body = P(base + '물체가 원형 레일의 최저점을 지날 때 레일이 물체에 작용하는 수직 항력의 크기는?' + tail) + fig
        return mc(body, U(Nb, 'N'), wr(Nb, [m * G, m * G * 2 * h / R, Nb - 2 * m * G, m * G * (2 * h / R - 1), Nt], 'N'), r=r, lv='중', fam='c',
                  steps=['최저점 속력 : v² = 2gh = 2 × 10 × %s = %s' % (fs(h), fs(2 * G * h)), '최저점에서 N - mg = mv²/R → N = %s × 10 + %s × %s / %s = %s N' % (fs(m), fs(m), fs(2 * G * h), fs(R), fs(Nb)),
                         '(검산) N = mg(1 + 2h/R) = %s × %s = %s N' % (fs(m * G), fs(1 + 2 * h / R), fs(Nb))],
                  core='최저점에서 수직 항력은 N = mg + mv²/R 이다.', point='높이 → 속력 → 수직 항력의 순서로 구한다.')
    # hmin
    fig = FIG(fig_loop('h', 'R = %s m' % fs(R)), '62%')
    hm = 2.5 * R
    body = P('그림과 같이 마찰이 없는 빗면 위의 높이 h인 지점에서 질량 %s kg인 물체를 가만히 놓았다. 물체가 반지름 %s m인 연직 원형 레일의 최고점을 레일에서 떨어지지 않고 통과하기 위한 h의 최솟값은?' % (fs(m), fs(R)) + tail) + fig
    return mc(body, U(hm, 'm'), wr(hm, [2 * R, 3 * R, 2 * R + 0.5 * R * 0.5, 4 * R, 5 * R, 1.5 * R], 'm'), r=r, lv='중', fam='c',
              steps=['최고점에서 수직 항력이 0 일 때가 한계 : mg = mv²/R → v² = gR = %s' % fs(G * R), '에너지 보존 : mgh = mg(2R) + ½mv² → h = 2R + R/2 = %s m' % fs(hm), '(검산) v² = 2g(h - 2R) = 2 × 10 × %s = %s = gR' % (fs(hm - 2 * R), fs(2 * G * (hm - 2 * R)))],
              core='원형 레일을 완주하려면 최고점에서 v² ≥ gR 이고, 이를 위한 최소 높이는 h = 2.5R 이다.', point='한계 조건(N = 0)과 에너지 보존을 연결한다.')


# ================================================================== ph110 기체의 일과 역학적 에너지
P0 = 100000  # 대기압 (Pa)


def fig_piston(expanded=True, wtxt='M', dtxt=None, Atxt=None, heater=True, ins=False, gas='기체', w=310, hh=225):
    """실린더 + 피스톤 + 추. expanded 이면 점선(처음 위치)과 현재 위치를 함께 그린다."""
    f = Fig(w, hh)
    xl, xr = 100, 200
    yb = 168
    yt = 36
    g0 = 50
    g1 = 82 if expanded else 50
    f.rect(xl, yb - g1, xr - xl, g1, '#fdeaea', 'none', 0)
    wc = '#d9dee6' if ins else INK
    f.line(xl, yt, xl, yb, wc, 5 if ins else 2.4)
    f.line(xr, yt, xr, yb, wc, 5 if ins else 2.4)
    f.line(xl, yb, xr, yb, wc, 5 if ins else 2.4)
    yp = yb - g1
    f.rect(xl + 1, yp - 7, xr - xl - 2, 7, '#aab4c3', INK, 1.4)
    f.rect(xl + 20, yp - 7 - 26, 60, 26, '#cfe2f7', INK, 1.7)
    f.text((xl + xr) / 2, yp - 7 - 8, wtxt, 13, bold=True, italic=True)
    if expanded:
        f.line(xl - 6, yb - g0 - 7, xl + 22, yb - g0 - 7, GR, 1.2, '4 3')
        f.line(xr + 6, yb - g0 - 7, xr + 22, yb - g0 - 7, GR, 1.2, '4 3')
        f.line(xr + 16, yb - g0 - 7, xr + 16, yp - 7, GR, 1.2)
        f._head(xr + 16, yb - g0 - 7, xr + 16, yp - 7, GR, 1.2, 7)
        f._head(xr + 16, yp - 7, xr + 16, yb - g0 - 7, GR, 1.2, 7)
        if dtxt: f.text(xr + 22, (yp + yb - g0) / 2 - 2, dtxt, 12.5, 'start', True, GR)
    f.text((xl + xr) / 2, yb - 14, gas, 12.5, bold=True, c=RD)
    if Atxt:
        f.text(xl - 8, yb - 24, Atxt, 12, 'end', True, GR)
        f.line(xl - 4, yb - 14, xl - 4, yb - 14, GR, 1)
    for x in (xl + 14, (xl + xr) / 2, xr - 14):
        f.arrow(x, 10, x, 28, GR, 1.6)
    f.text(xl - 8, 22, 'P₀', 13, 'end', True, GR, True)
    if heater:
        for x in (xl + 22, (xl + xr) / 2, xr - 22):
            f.path('M %s %s q -5 -8 0 -14 q 3 5 6 0 q 4 8 -6 14 z' % (Fig._n(x), Fig._n(yb + 24)), RD, RD, 1)
        f.text(xr + 14, yb + 22, '가열', 12.5, 'start', True, RD)
    if ins:
        f.text(xl - 8, 120, '단열', 12.5, 'end', True, GR)
    return f.svg()


def fig_joule(Mtxt, Htxt, w=320, hh=215):
    f = Fig(w, hh)
    f.rect(36, 120, 100, 70, 'none', INK, 2)
    f.rect(37, 138, 98, 51, '#cfe2f7', 'none', 0)
    f.text(86, 182, '물', 12.5, bold=True, c=BL)
    f.line(86, 70, 86, 172, INK, 2.2)
    f.rect(66, 168, 40, 6, '#aab4c3', INK, 1.4)
    f.circ(86, 60, 12, '#f1f4f8', INK, 1.6)
    f.line(86, 60, 86, 60, INK, 1)
    pxx, pyy = 176, 40
    f.circ(pxx, pyy, 12, '#f1f4f8', INK, 1.6)
    f.line(98, 56, pxx - 12, pyy + 2, GR, 1.6)
    f.line(pxx + 12, pyy, pxx + 12, 108, GR, 1.6)
    f.rect(pxx - 2, 108, 28, 26, '#cfe2f7', INK, 1.7)
    f.text(pxx + 12, 126, Mtxt, 12.5, bold=True, italic=True)
    f.rect(pxx - 2, 178, 28, 26, 'none', GR, 1.2, 0, '4 3')
    f.line(pxx + 40, 108, pxx + 40, 178, GR, 1.2)
    f._head(pxx + 40, 108, pxx + 40, 178, GR, 1.2, 7)
    f._head(pxx + 40, 178, pxx + 40, 108, GR, 1.2, 7)
    f.text(pxx + 46, 148, Htxt, 12.5, 'start', True, GR)
    return f.svg()


@T('ph110')
@balanced
def g110(r, k):
    form = pick(r, ['iso', 'iso', 'iso', 'iso', 'joule', 'joule', 'adia', 'adia', 'fric', 'fric', 'bogi', 'bogi', 'bogi'])
    tail = ' (단, 중력 가속도는 10 m/s²이다.)'
    if form in ('iso', 'bogi'):
        A = r.choice([0.005, 0.01, 0.02])
        Mk = r.choice([2, 4, 5, 6, 8, 10, 12, 15, 20])
        dh = r.choice([0.05, 0.1, 0.2, 0.25, 0.4, 0.5])
        Mg = Mk * G
        Pg = P0 + Mg / A
        dV = A * dh
        W = Pg * dV
        W2 = (P0 * A + Mg) * dh
        assert abs(W - W2) < 1e-6
        Watm = P0 * A * dh
        Ep = Mg * dh
        assert abs(Watm + Ep - W) < 1e-6
        dU = 1.5 * Pg * dV
        Q = dU + W
        assert abs(Q - 2.5 * W) < 1e-6
        if not (cl(W, 2) and cl(Q, 2) and cl(Watm, 2) and cl(Ep, 2)): return None
        Atxt = 'S = %s m²' % fs(A, 3)
        fig = FIG(fig_piston(True, '%d kg' % Mk, 'Δh = %s m' % fs(dh), Atxt), '56%')
        base = '그림과 같이 단면적이 %s m²인 실린더에 단원자 분자 이상 기체가 들어 있고, 질량 %d kg인 추와 피스톤이 위에 놓여 있다(피스톤의 질량은 무시). 대기압은 1.0×10%s Pa이다. 기체에 열을 서서히 가했더니 피스톤이 %s m 올라갔다. ' % (fs(A, 3), Mk, sup('5'), fs(dh))
        if form == 'bogi':
            tops = [
                ('기체가 한 일은 %s J이다.' % fs(W), '기체가 한 일은 %s J이다.' % fs(Ep), '압력 P = P₀ + Mg/S = %s Pa 로 일정하므로 W = PΔV = %s J 이다.' % (fs(Pg), fs(W)), 'W = PΔV = %s J 이며 %s J 는 추의 위치 에너지 증가량일 뿐이다.' % (fs(W), fs(Ep))),
                ('기체의 압력은 팽창하는 동안 일정하다.', '기체의 압력은 팽창하는 동안 계속 감소한다.', '피스톤이 천천히 움직이면 추와 대기압이 누르는 힘과 평형을 이루어 압력이 일정하다.', '피스톤에 작용하는 힘이 일정하므로 압력은 P₀ + Mg/S 로 일정하다.'),
                ('기체가 흡수한 열량은 기체가 한 일보다 크다.', '기체가 흡수한 열량은 기체가 한 일과 같다.', 'Q = ΔU + W 이고 온도가 올라 ΔU > 0 이므로 Q > W 이다.', '등압 팽창에서는 온도가 상승하여 내부 에너지가 증가하므로 Q = ΔU + W > W 이다.'),
                ('기체가 한 일 중 추의 위치 에너지 증가량은 %s J이다.' % fs(Ep), '기체가 한 일은 모두 추의 위치 에너지 증가량으로 전환된다.', 'Mg·Δh = %d × 10 × %s = %s J 이다. 나머지는 대기를 밀어내는 일이다.' % (Mk, fs(dh), fs(Ep)), '기체가 한 일 %s J 중 %s J 는 대기를 밀어내는 데 쓰인다.' % (fs(W), fs(Watm))),
                ('기체의 내부 에너지 증가량은 %s J이다.' % fs(dU), '기체의 내부 에너지 증가량은 %s J이다.' % fs(W), '단원자 분자 이상 기체의 ΔU = (3/2)PΔV = %s J 이다.' % fs(dU), 'ΔU = (3/2)PΔV = %s J 로 기체가 한 일과 같지 않다.' % fs(dU)),
                ('기체의 온도는 상승한다.', '기체의 온도는 변하지 않는다.', '압력이 일정하고 부피가 늘어나므로 PV 가 커져 온도가 올라간다.', '등압 팽창에서 V/T 가 일정하므로 부피가 늘면 온도도 오른다.'),
                ('기체가 흡수한 열량은 %s J이다.' % fs(Q), '기체가 흡수한 열량은 %s J이다.' % fs(dU), 'Q = ΔU + W = %s + %s = %s J 이다.' % (fs(dU), fs(W), fs(Q)), 'Q = ΔU + W = %s J 이고 %s J 는 내부 에너지 증가량만이다.' % (fs(Q), fs(dU))),
            ]
            return topics_bogi(r, tops, base + '이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 중력 가속도는 10 m/s²이다.)', pre=fig, fam='e', lv='중',
                               core='등압 팽창에서 기체가 한 일은 PΔV 이고, 열량은 내부 에너지 증가와 한 일의 합이다.', point='기체의 일과 역학적 에너지(추의 위치 에너지)의 관계를 구분한다.')
        ask = r.choice(['Ep', 'Ep', 'W', 'W', 'Watm', 'Q', 'Q'])
        if ask == 'Ep':
            body = P(base + '이 과정에서 추의 중력 위치 에너지의 증가량은?' + tail) + fig
            return mc(body, U(Ep, 'J'), wr(Ep, [W, Watm, Pg * dV * 0.5, Mg * dh * 2, Mk * dh], 'J'), r=r, lv='하', fam='a',
                      steps=['추가 올라간 높이는 피스톤이 올라간 높이 %s m 와 같다.' % fs(dh), 'ΔEp = mgh = %d × 10 × %s = %s J' % (Mk, fs(dh), fs(Ep))],
                      core='위치 에너지 증가량은 mgΔh 이다.', point='추의 에너지와 기체가 한 일을 구분한다.')
        if ask == 'W':
            body = P(base + '이 과정에서 기체가 한 일은?' + tail) + fig
            return mc(body, U(W, 'J'), wr(W, [Ep, Watm, P0 * dV * 0, Mg * dh + P0 * dh, Pg * A, W * 2, W / 2], 'J'), r=r, lv='중', fam='a',
                      steps=['기체의 압력 P = P₀ + Mg/S = 1.0×10⁵ + %d × 10 / %s = %s Pa (일정)' % (Mk, fs(A, 3), fs(Pg)), '부피 변화 ΔV = SΔh = %s × %s = %s m³' % (fs(A, 3), fs(dh), fs(dV, 5)), 'W = PΔV = %s × %s = %s J' % (fs(Pg), fs(dV, 5), fs(W)),
                             '(검산) 대기에 한 일 P₀SΔh = %s J + 추의 위치 에너지 %s J = %s J' % (fs(Watm), fs(Ep), fs(Watm + Ep))],
                      core='등압 팽창에서 기체가 한 일은 PΔV 이며, 대기를 밀어낸 일과 추를 올린 일의 합과 같다.', point='압력을 먼저 구한 뒤 부피 변화를 곱한다.')
        if ask == 'Watm':
            body = P(base + '이 과정에서 기체가 한 일 중 대기를 밀어내는 데 쓰인 일은?' + tail) + fig
            return mc(body, U(Watm, 'J'), wr(Watm, [W, Ep, Ep + 0.5 * Watm, Watm * 2, Watm / 2, P0 * dh], 'J'), r=r, lv='중', fam='a',
                      steps=['기체가 한 일 W = (P₀S + Mg)Δh = (%s + %s) × %s = %s J' % (fs(P0 * A), fs(Mg), fs(dh), fs(W)), '추의 위치 에너지 증가 Mgh = %s J' % fs(Ep), '대기에 한 일 = W - Mgh = %s - %s = %s J' % (fs(W), fs(Ep), fs(Watm)),
                             '(검산) P₀SΔh = %s × %s = %s J' % (fs(P0 * A), fs(dh), fs(Watm))],
                      core='기체가 한 일 = 대기압을 이기는 일 + 추의 위치 에너지 증가.', point='에너지 전환의 경로를 추적한다.')
        body = P(base + '이 과정에서 기체가 흡수한 열량은?' + tail) + fig
        return mc(body, U(Q, 'J'), wr(Q, [W, dU, Q - Ep, 1.5 * W + Ep, 2 * W, 3 * W], 'J'), r=r, lv='상', fam='a',
                  steps=['W = PΔV = (P₀ + Mg/S)SΔh = %s J' % fs(W), 'ΔU = (3/2)nRΔT = (3/2)PΔV = 1.5 × %s = %s J' % (fs(W), fs(dU)), 'Q = ΔU + W = %s + %s = %s J' % (fs(dU), fs(W), fs(Q)), '(검산) 등압 과정에서 단원자 분자 Q = (5/2)PΔV = 2.5 × %s = %s J' % (fs(W), fs(2.5 * W))],
                  core='열역학 제1법칙 Q = ΔU + W, 단원자 분자 이상 기체의 ΔU = 3/2 PΔV 이다.', point='압력(역학) → 일 → 내부 에너지 → 열량의 순서로 연결한다.')
    if form == 'joule':
        Mk = r.choice([2, 4, 5, 8, 10, 20, 21, 25, 42])
        H = r.choice([1, 1.5, 2, 2.5, 4, 5])
        n = r.choice([5, 10, 12, 20, 25, 30, 40, 50, 100])
        mw = r.choice([0.5, 1, 2, 3, 5])
        c = 4200
        eta = r.choice([1, 1, 0.5, 0.8, 0.6, 0.4, 0.25, 0.75])
        Q = eta * n * Mk * G * H
        dT = Q / (mw * c)
        if not cl(dT, 2) or dT <= 0 or dT > 20: return None
        assert abs(dT * mw * c - eta * n * Mk * G * H) < 1e-6
        ask = r.choice(['dT', 'dT', 'dT', 'Q'])
        fig = FIG(fig_joule('%d kg' % Mk, '%s m' % fs(H)), '58%')
        base = '그림은 줄에 매달린 질량 %d kg인 추가 %s m 내려오면서 물속의 날개를 돌려 물을 젓는 장치를 나타낸 것이다. 추를 같은 높이에서 %d번 반복해서 내려오게 했다. 물의 질량은 %s kg이고 물의 비열은 4200 J/(kg·K)이다. ' % (Mk, fs(H), n, fs(mw))
        eta_s = '' if eta == 1 else '추가 잃은 역학적 에너지의 %d %%만 물의 내부 에너지로 전달된다고 할 때, ' % round(eta * 100)
        if ask == 'Q':
            body = P(base + eta_s + '물에 전달된 열에너지는? (단, 추의 처음과 나중 속력은 0이고, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(Q, 'J'), wr(Q, [n * Mk * G * H, Q * 2, Q / 2, Mk * G * H, n * Mk * H, dT], 'J'), r=r, lv='중', fam='b',
                      steps=['추가 한 번 내려올 때 잃는 위치 에너지 Mgh = %d × 10 × %s = %s J' % (Mk, fs(H), fs(Mk * G * H)), '%d번이면 %s J' % (n, fs(n * Mk * G * H)), '전달된 열 = %s × %s = %s J' % (fs(eta), fs(n * Mk * G * H), fs(Q))],
                      core='역학적 에너지가 마찰(젓는 일)로 열에너지가 된다(줄의 실험).', point='위치 에너지 감소량을 열로 환산한다.')
        body = P(base + eta_s + '물의 온도 변화는? (단, 추의 처음과 나중 속력은 0이고, 중력 가속도는 10 m/s²이며, 열은 물에만 전달된다.)') + fig
        return mc(body, U(dT, 'K'), wr(dT, [dT * 2, dT / 2, dT / eta if eta != 1 else dT * 4, dT * eta if eta != 1 else dT * 10, Mk * G * H / (mw * c), dT * 100], 'K'), r=r, lv='중', fam='b',
                  steps=['추의 위치 에너지 감소 : %d × (%d × 10 × %s) = %s J' % (n, Mk, fs(H), fs(n * Mk * G * H)), '물이 받은 열 Q = %s × %s = %s J' % (fs(eta), fs(n * Mk * G * H), fs(Q)), 'Q = mcΔT → ΔT = %s / (%s × 4200) = %s K' % (fs(Q), fs(mw), fs(dT)),
                         '(검산) mcΔT = %s × 4200 × %s = %s J = Q' % (fs(mw), fs(dT), fs(mw * c * dT))],
                  core='줄의 실험 : 역학적 에너지 감소량 = 열에너지 증가량 = mcΔT.', point='에너지 전환량을 비열 공식에 대입한다.')
    if form == 'adia':
        A = r.choice([0.005, 0.01, 0.02])
        Mk = r.choice([2, 4, 5, 6, 8, 10, 12, 15, 20])
        dh = r.choice([0.05, 0.1, 0.2, 0.25, 0.4, 0.5])
        nmol = r.choice([0.5, 1, 2, 0.25])
        Pext = P0 + Mk * G / A
        W = Pext * A * dh
        dU = -W
        dT = W / (1.5 * nmol * 8)
        if not cl(W, 2) or not cl(dT, 2): return None
        assert abs(W - ((P0 * A + Mk * G) * dh)) < 1e-6
        fig = FIG(fig_piston(True, '%d kg' % Mk, 'Δh = %s m' % fs(dh), 'S = %s m²' % fs(A, 3), heater=False, ins=True), '56%')
        base = '그림과 같이 단면적 %s m²인 단열된 실린더에 단원자 분자 이상 기체 %s mol이 들어 있고, 마찰 없이 움직이는 질량이 무시되는 단열 피스톤 위에 질량 %d kg인 추가 놓여 있다. 대기압은 1.0×10%s Pa이다. 처음에 고정되어 있던 피스톤을 가만히 놓았더니 기체가 팽창하여 피스톤과 추가 %s m 올라간 뒤 정지하였다. ' % (fs(A, 3), fs(nmol), Mk, sup('5'), fs(dh))
        body = P(base + '기체의 온도는 몇 K 낮아졌는가? (단, 기체 상수는 8 J/(mol·K)이고, 중력 가속도는 10 m/s²이다. 추와 피스톤이 정지한 상태에서의 운동 에너지 변화는 무시한다.)') + fig
        return mc(body, U(dT, 'K'), wr(dT, [dT * 2, dT / 2, Mk * G * dh / (1.5 * nmol * 8), W / (nmol * 8), W / (2.5 * nmol * 8), dT * 1.5, dT * 2 / 3], 'K'), r=r, lv='상', fam='c',
                  steps=['기체가 외부에 한 일 W = (P₀S + Mg)Δh = (%s + %d × 10) × %s = %s J' % (fs(P0 * A), Mk, fs(dh), fs(W)), '단열 과정 Q = 0 이므로 ΔU = -W = %s J' % fs(dU),
                         'ΔU = (3/2)nRΔT 에서 |ΔT| = %s / (1.5 × %s × 8) = %s K' % (fs(W), fs(nmol), fs(dT)), '(검산) 대기에 한 일 %s J + 추의 위치 에너지 증가 %s J = %s J' % (fs(P0 * A * dh), fs(Mk * G * dh), fs(W))],
                  core='단열 팽창에서 기체가 한 일만큼 내부 에너지가 감소하며, 이 일은 대기와 추에 전달된다.', point='역학적 일(위치 에너지)을 열역학 제1법칙에 연결한다.')
    # fric : 마찰열 → 기체 내부 에너지
    mm = r.choice([1, 2, 3, 4, 5])
    mu = r.choice([0.2, 0.25, 0.4, 0.5])
    d = r.choice([2, 4, 5, 8, 10, 12, 20])
    v = None
    use_v = r.random() < 0.5
    if use_v:
        vv = r.choice([2, 4, 5, 6, 8, 10])
        Qh = 0.5 * mm * vv * vv
        dd = vv * vv / (2 * mu * G)
        if not cl(dd, 2): return None
        # 교차 검증 : 마찰력 × 이동 거리
        assert abs(mu * mm * G * dd - Qh) < 1e-6
    else:
        vv = None
        Qh = mu * mm * G * d
    eta = r.choice([1, 0.5, 0.4, 0.8, 0.25])
    nmol = r.choice([0.5, 1, 2, 0.25])
    dU = eta * Qh
    dT = dU / (1.5 * nmol * 8)
    if not cl(dT, 2) or dT <= 0: return None
    eta_s = '' if eta == 1 else '발생한 열의 %d %%가 ' % round(eta * 100)
    if use_v:
        txt = '수평면 위에서 질량 %d kg인 물체가 %d m/s의 속력으로 미끄러지기 시작하여 운동 마찰 계수가 %s인 거친 면을 지나 멈출 때까지 마찰력에 의해 열이 발생한다. ' % (mm, vv, fs(mu))
    else:
        txt = '수평면 위에서 질량 %d kg인 물체가 운동 마찰 계수가 %s인 거친 면 위를 일정한 속력으로 %d m만큼 끌려 이동하는 동안 마찰력에 의해 열이 발생한다. ' % (mm, fs(mu), d)
    body = P(txt + '%s부피가 일정한 용기 속의 단원자 분자 이상 기체 %s mol에 전달되었다면 기체의 온도 상승량은? (단, 기체 상수는 8 J/(mol·K)이고, 중력 가속도는 10 m/s²이다.)' % (eta_s if eta_s else '발생한 열이 모두 ', fs(nmol)))
    wl = [dT * 2, dT / 2, Qh / (nmol * 8), Qh / (1.5 * nmol * 8) if eta != 1 else dT * 1.5, dT * 5 / 3, dT / eta if eta != 1 else dT * 4]
    return mc(body, U(dT, 'K'), wr(dT, wl, 'K'), r=r, lv='상' if use_v else '중', fam='d',
              steps=['마찰열 Q = ' + ('운동 에너지 ½mv² = ½ × %d × %d² = %s J (마찰력 × 거리와 같다)' % (mm, vv, fs(Qh)) if use_v else '마찰력 × 거리 = μmg × d = %s × %d × 10 × %d = %s J' % (fs(mu), mm, d, fs(Qh))),
                     '기체에 전달된 열 = 부피 일정이므로 W = 0, ΔU = %s × %s = %s J' % (fs(eta), fs(Qh), fs(dU)), 'ΔU = (3/2)nRΔT → ΔT = %s / (1.5 × %s × 8) = %s K' % (fs(dU), fs(nmol), fs(dT))],
              core='부피가 일정한 기체가 받은 열은 모두 내부 에너지 증가가 되며, 역학적 에너지가 마찰열로 전환된다.', point='역학적 에너지 → 열 → 내부 에너지의 전환 경로를 따라 계산한다.')
