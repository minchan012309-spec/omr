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
        fb = [right * 2, right / 2, right * 4, right / 4, right * 1.5, right * 3, right * 0.75, right * 1.25]
        if right < 10:
            fb += [right + 1, right + 2, right + 0.5]
        for c in fb:
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
        f.text(x1, y0 + 16, 'μ = ' + mu, 12.5, 'end', True, RD)
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
        f.text(xt + 2, yb + 22, 'μ₁ = ' + mu1 + ' (빗면)', 12.5, 'start', True, RD)
    if mu2:
        f.text(w - 10, yb + 22, 'μ = ' + mu2 + ' (수평면)', 12.5, 'end', True, RD)
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
    form = pick(r, ['easy'] * 6 + ['free'] * 3 + ['fric'] * 3 + ['up'] * 3 + ['spring'] * 2 + ['flat'] * 2 + ['bogi'] * 2)
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
            ask = r.choice(['S', 'h', 'h', 't'])
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
    ox, gy = (96 if h0 > 0 else 44), h - 28
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
        tx, ty = ox + L * vx / sp, sy - L * vy / sp
        if vy > 0:
            f.text(tx - 6, ty - 6, v0txt, 12.5, 'end', True, RD)
        else:
            f.text(tx + 4, ty - 8, v0txt, 12.5, 'start', True, RD)
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
    form = pick(r, ['hor'] * 3 + ['obl'] * 3 + ['cliff'] * 3 + ['at'] * 2 + ['bogi'] * 2 + ['ez'] * 5)
    m = r.choice([0.5, 1, 2, 3, 4, 5])
    if form == 'ez':
        sub_ = r.choice(['top', 'vy', 'cl'])
        if sub_ == 'top':
            th = r.choice([37, 53]); v0 = r.choice([5, 10, 15, 20, 25, 30, 40])
            vt = v0 * cx(th)
            if not cl(vt, 2): return None
            vx, vy = v0 * cx(th), v0 * sx(th)
            H = float(SIN2[th]) * v0 * v0 / 20
            assert abs(0.5 * v0 * v0 - (0.5 * vt * vt + G * H)) < 1e-6
            fig = FIG(fig_traj(vx, vy, 0, v0txt='%d m/s' % v0, thtxt='%d°' % th, Htxt='H', apex=True), '62%')
            body = P('그림과 같이 지면에서 공을 수평면과 %d°의 각으로 %d m/s의 속력으로 던졌다. 공이 최고점에 도달했을 때 공의 속력은? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)' % (th, v0)) + fig
            return mc(body, U(vt, 'm/s'), wr(vt, [v0 * sx(th), 0, v0, v0 * (cx(th) + sx(th)) / 2, v0 / 2, vt * 2], 'm/s'), r=r, lv='하', fam='f',
                      steps=['최고점에서는 연직 속도가 0이고 수평 속도만 남는다.', '수평 속도는 일정하므로 v = v₀ cos%d° = %d × %s = %s m/s' % (th, v0, CSS.get(th, ''), fs(vt)), '(검산) 에너지 : ½mv₀² = ½mv² + mgH, H = %s m → v² = %s' % (fs(H), fs(v0 * v0 - 2 * G * H))],
                      core='포물선 운동에서 수평 속도는 일정하고 최고점에서 속도는 수평 성분뿐이다.', point='최고점의 속력은 0이 아니다.')
        if sub_ == 'vy':
            v0, vyy, vv = r.choice(TRIPLES)
            h = vyy * vyy / 20.0
            fig = FIG(fig_traj(v0, 0, h, v0txt='v₀ = %d m/s' % v0, htxt='%s m' % fs(h)), '62%')
            body = P('그림과 같이 높이 %s m인 절벽 끝에서 공을 수평 방향으로 %d m/s의 속력으로 던졌다. 공이 지면에 닿는 순간 속도의 연직 성분의 크기는? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)' % (fs(h), v0)) + fig
            t = vyy / 10.0
            assert abs(vyy - G * t) < 1e-9 and abs(h - 0.5 * G * t * t) < 1e-9
            return mc(body, U(vyy, 'm/s'), wr(vyy, [v0, vv, math.sqrt(G * h), 2 * G * h, G * h, vyy / 2], 'm/s'), r=r, lv='하', fam='f',
                      steps=['수평 속도 %d m/s 는 변하지 않고 연직 방향은 자유 낙하이다.' % v0, '연직 속도 v_y = √(2gh) = √(2 × 10 × %s) = %d m/s' % (fs(h), vyy), '(검산) 낙하 시간 t = √(2h/g) = %s s, v_y = gt = %d m/s' % (fs(t), vyy)],
                      core='수평으로 던진 물체의 연직 방향 운동은 자유 낙하이다.', point='연직 속도는 에너지 보존(mgh = ½mv_y²)으로도 구한다.')
        v0, vyy, vv = r.choice(TRIPLES)
        h = vyy * vyy / 20.0
        fig = FIG(fig_traj(v0, 0, h, v0txt='%d m/s' % v0, htxt='%s m' % fs(h), vend='v'), '62%')
        body = P('그림과 같이 높이 %s m인 절벽 끝에서 공을 수평 방향으로 %d m/s의 속력으로 던졌다. 공이 지면에 닿는 순간의 속력은? (단, 중력 가속도는 10 m/s²이고, 공기 저항은 무시한다.)' % (fs(h), v0)) + fig
        return mc(body, U(vv, 'm/s'), wr(vv, [v0 + vyy, vyy, v0, math.sqrt(2 * G * h), abs(v0 - vyy) + 2, vv * 2], 'm/s'), r=r, lv='하', fam='f',
                  steps=['역학적 에너지 보존 : v² = v₀² + 2gh = %d² + 2 × 10 × %s = %s' % (v0, fs(h), fs(vv * vv)), 'v = %d m/s' % vv, '(검산) v_y = √(2gh) = %d m/s, √(%d² + %d²) = %d m/s' % (vyy, v0, vyy, vv)],
                  core='도달 속력은 에너지 보존으로 구한다.', point='속도의 합성은 벡터 합이다.')
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
    form = pick(r, ['wall'] * 5 + ['free'] * 3 + ['slope'] + ['rough'] * 2 + ['bogi'] * 2)
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
        ask = r.choice(['v', 'v', 'v', 'v', 'v', 'loss', 'x', 'k', 'x'])
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
    f.text(cx, cy + 20, Rtxt, 12.5, 'middle', True, GR)
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
    form = pick(r, ['pend'] * 5 + ['circ'] * 4 + ['loop'] * 2 + ['rope'] + ['bogi'] * 2)
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
        ask = r.choice(['v', 'v', 'v', 'KE', 'KE', 'T', 'ratio'])
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
        ask = r.choice(['vt', 'vt', 'Tt', 'Tb', 'Tb', 'diff', 'vmin'])
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
    f.rect(pxx - 12, 108, 48, 26, '#cfe2f7', INK, 1.7)
    f.text(pxx + 12, 126, Mtxt, 12.5, bold=True, italic=True)
    f.rect(pxx - 12, 178, 48, 26, 'none', GR, 1.2, 0, '4 3')
    f.line(pxx + 40, 108, pxx + 40, 178, GR, 1.2)
    f._head(pxx + 40, 108, pxx + 40, 178, GR, 1.2, 7)
    f._head(pxx + 40, 178, pxx + 40, 108, GR, 1.2, 7)
    f.text(pxx + 46, 148, Htxt, 12.5, 'start', True, GR)
    return f.svg()


@T('ph110')
@balanced
def g110(r, k):
    form = pick(r, ['iso'] * 4 + ['joule'] * 3 + ['adia'] * 1 + ['fric'] * 3 + ['bogi'] * 3)
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
        ask = r.choice(['Ep', 'Ep', 'Ep', 'W', 'W', 'Watm', 'Q'])
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
        ask = r.choice(['dT', 'Q', 'Q', 'Q'])
        fig = FIG(fig_joule('%d kg' % Mk, '%s m' % fs(H)), '58%')
        base = '그림은 줄에 매달린 질량 %d kg인 추가 %s m 내려오면서 물속의 날개를 돌려 물을 젓는 장치를 나타낸 것이다. 추를 같은 높이에서 %d번 반복해서 내려오게 했다. 물의 질량은 %s kg이고 물의 비열은 4200 J/(kg·K)이다. ' % (Mk, fs(H), n, fs(mw))
        eta_s = '' if eta == 1 else '추가 잃은 역학적 에너지의 %d %%만 물의 내부 에너지로 전달된다고 할 때, ' % round(eta * 100)
        if ask == 'Q':
            body = P(base + eta_s + '물에 전달된 열에너지는? (단, 추의 처음과 나중 속력은 0이고, 중력 가속도는 10 m/s²이다.)') + fig
            return mc(body, U(Q, 'J'), wr(Q, [n * Mk * G * H, Q * 2, Q / 2, Mk * G * H, n * Mk * H, dT], 'J'), r=r, lv='하' if eta == 1 else '중', fam='b',
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
    if r.random() < 0.4:
        body = P(txt + '이때 발생한 열의 양은? (단, 중력 가속도는 10 m/s²이다.)')
        return mc(body, U(Qh, 'J'), wr(Qh, [mu * mm * G, mm * G * d if not use_v else mm * vv * vv, Qh * 2, Qh / 2, 0.5 * mm * vv * vv * 2 if use_v else mu * mm * d], 'J'), r=r, lv='하', fam='d',
                  steps=['마찰열 Q = ' + ('운동 에너지 ½mv² = ½ × %d × %d² = %s J (마찰력 × 거리와 같다)' % (mm, vv, fs(Qh)) if use_v else '마찰력 × 거리 = μmg × d = %s × %d × 10 × %d = %s J' % (fs(mu), mm, d, fs(Qh)))],
                  core='마찰로 줄어든 역학적 에너지(또는 마찰력 × 거리)가 열로 변한다.', point='마찰열을 마찰력과 이동 거리의 곱으로 구한다.')
    body = P(txt + '%s부피가 일정한 용기 속의 단원자 분자 이상 기체 %s mol에 전달되었다면 기체의 온도 상승량은? (단, 기체 상수는 8 J/(mol·K)이고, 중력 가속도는 10 m/s²이다.)' % (eta_s if eta_s else '발생한 열이 모두 ', fs(nmol)))
    wl = [dT * 2, dT / 2, Qh / (nmol * 8), Qh / (1.5 * nmol * 8) if eta != 1 else dT * 1.5, dT * 5 / 3, dT / eta if eta != 1 else dT * 4]
    return mc(body, U(dT, 'K'), wr(dT, wl, 'K'), r=r, lv='상' if use_v else '중', fam='d',
              steps=['마찰열 Q = ' + ('운동 에너지 ½mv² = ½ × %d × %d² = %s J (마찰력 × 거리와 같다)' % (mm, vv, fs(Qh)) if use_v else '마찰력 × 거리 = μmg × d = %s × %d × 10 × %d = %s J' % (fs(mu), mm, d, fs(Qh))),
                     '기체에 전달된 열 = 부피 일정이므로 W = 0, ΔU = %s × %s = %s J' % (fs(eta), fs(Qh), fs(dU)), 'ΔU = (3/2)nRΔT → ΔT = %s / (1.5 × %s × 8) = %s K' % (fs(dU), fs(nmol), fs(dT))],
              core='부피가 일정한 기체가 받은 열은 모두 내부 에너지 증가가 되며, 역학적 에너지가 마찰열로 전환된다.', point='역학적 에너지 → 열 → 내부 에너지의 전환 경로를 따라 계산한다.')


# ================================================================== ph111 용수철 진자와 에너지 · 진동수
def fig_sp_h(ktxt='k', mtxt='m', Atxt=None, xtxt=None, xfrac=None, w=330, hh=150):
    """수평 용수철 진자(평형 위치 O, 진폭 ±A 눈금)."""
    f = Fig(w, hh)
    fy = 92
    f.line(10, fy, w - 8, fy, INK, 1.6)
    for i in range(10, w - 8, 8):
        f.line(i, fy, i - 5, fy + 6, GR, 1)
    f.line(20, fy - 52, 20, fy, GR, 3)
    for v in range(fy - 50, fy, 8):
        f.line(20, v, 14, v + 6, GR, 1)
    xe = 190
    f.spring(20, fy - 15, xe - 28, 8, 8)
    f.rect(xe - 28, fy - 30, 56, 30, '#cfe2f7', INK, 1.7)
    f.text(xe, fy - 10, mtxt, 13, bold=True, italic=True)
    f.text(112, fy - 38, ktxt, 12.5, bold=True, c=BL)
    f.line(xe, fy - 62, xe, fy + 22, GR, 1, '4 3')
    f.text(xe, fy + 38, 'O', 12.5, bold=True, c=GR)
    s = 70
    for sg, lab in ((-1, '-A'), (1, 'A')):
        x = xe + sg * s
        f.line(x, fy + 10, x, fy + 22, INK, 1.4)
        f.text(x, fy + 38, lab, 12.5, bold=True, c=GR)
    f.line(xe - s, fy + 16, xe + s, fy + 16, GR, 1.2)
    if Atxt:
        f.text(xe + s + 8, fy + 20, 'A = ' + Atxt, 12.5, 'start', True, RD)
    if xfrac is not None:
        xx = xe + xfrac * s
        f.circ(xx, fy + 16, 4, RD, RD, 1)
        f.text(xx, fy + 58, 'x = ' + xtxt, 12.5, bold=True, c=RD)
    return f.svg()


def _vspring(f, x, y1, y2, coils=8, amp=8, c=INK, sw=1.6):
    pts = [(x, y1), (x, y1 + 8)]
    n = coils * 2
    for i in range(1, n + 1):
        pts.append((x + (amp if i % 2 else -amp), y1 + 8 + (y2 - y1 - 16) * i / n))
    pts += [(x, y2 - 8), (x, y2)]
    f.poly(pts, 'none', c, sw, close=False)


def fig_sp_v(ktxt='k', mtxt='m', x0txt=None, Atxt=None, w=300, hh=215):
    f = Fig(w, hh)
    f.line(60, 16, 170, 16, GR, 3)
    for i in range(60, 170, 8):
        f.line(i, 16, i + 6, 9, GR, 1)
    yn = 80     # 원래 길이에서 아래 끝
    ye = 130    # 평형 위치에서 블록 윗면
    _vspring(f, 115, 16, ye, 8, 9)
    f.rect(87, ye, 56, 30, '#cfe2f7', INK, 1.7)
    f.text(115, ye + 20, mtxt, 13, bold=True, italic=True)
    f.text(150, 70, ktxt, 12.5, 'start', True, BL)
    f.line(70, yn, 100, yn, GR, 1.2, '4 3')
    f.line(80, yn, 80, ye, GR, 1.2)
    f._head(80, yn, 80, ye, GR, 1.2, 7)
    f._head(80, ye, 80, yn, GR, 1.2, 7)
    if x0txt: f.text(74, (yn + ye) / 2 + 4, x0txt, 12.5, 'end', True, GR)
    f.line(87, ye + 15, 200, ye + 15, GR, 1, '4 3')
    f.text(206, ye + 19, 'O (평형)', 12, 'start', True, GR)
    if Atxt:
        s = 34
        f.line(95, ye + 15 + s, 200, ye + 15 + s, RD, 1, '4 3')
        f.line(95, ye + 15 - s, 200, ye + 15 - s, RD, 1, '4 3')
        f.line(190, ye + 15, 190, ye + 15 + s, RD, 1.2)
        f._head(190, ye + 15, 190, ye + 15 + s, RD, 1.2, 7)
        f.text(206, ye + 15 + s + 4, '최저점', 12, 'start', False, GR)
        f.text(206, ye + 15 - s + 4, '최고점', 12, 'start', False, GR)
        f.text(184, ye + 15 + s / 2 + 4, 'A = ' + Atxt, 12.5, 'end', True, RD)
    return f.svg()


def fig_xt(A, T, unit='cm', w=330, hh=200):
    p = Plot(w, hh, T * 1.35, A * 1.4, 0, -A * 1.4, ml=56, mr=16, mt=16, mb=28)
    p.axes('t (s)', 'x (%s)' % unit, xticks=[T / 4, T / 2, 3 * T / 4, T], yticks=[-A, A], xfmt=lambda v: num(v, 3), yfmt=lambda v: num(v, 2))
    p.pl([(T * i / 80.0 * 1.0, A * math.sin(2 * math.pi * i / 80.0)) for i in range(0, 81)], BL, 2.4)
    p.dash_to_axes(T / 4, A)
    return p.svg()


def _fr(q):
    """Fraction q 의 제곱근을 '배' 문자열로."""
    q = F(q)
    a, b = q.numerator, q.denominator
    ra, rb = math.isqrt(a), math.isqrt(b)
    if ra * ra == a and rb * rb == b:
        v = F(ra, rb)
        return ('%d배' % v.numerator) if v.denominator == 1 else '%d/%d배' % (v.numerator, v.denominator)
    if b == 1: return '√%d배' % a
    if a == 1 and rb * rb == b: return '1/%d√%d배' % (rb, 1) if False else '1/%d배' % rb
    if a == 1: return '1/√%d배' % b
    return '√(%d/%d)배' % (a, b)


def _fq(q):
    q = F(q)
    return ('%d배' % q.numerator) if q.denominator == 1 else '%d/%d배' % (q.numerator, q.denominator)


@T('ph111')
@balanced
def g111(r, k):
    form = pick(r, ['calc'] * 7 + ['atx'] * 1 + ['graph'] * 3 + ['chg'] * 3 + ['vert'] * 2 + ['bogi'] * 2)
    tail = ' (단, 용수철의 질량과 모든 마찰·공기 저항은 무시한다.)'
    if form in ('calc', 'atx', 'bogi'):
        om = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
        m = r.choice([0.1, 0.2, 0.25, 0.4, 0.5, 1, 2, 4])
        kk = m * om * om
        if not cl(kk, 2) or kk < 1: return None
        A = r.choice([0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5])
        T = 6.0 / om
        vmax = om * A
        E = 0.5 * kk * A * A
        assert abs(E - 0.5 * m * vmax * vmax) < 1e-9
        assert abs(om - math.sqrt(kk / m)) < 1e-9
        kt = '%s N/m' % fs(kk)
        mt = '%s kg' % fs(m)
        if form == 'calc':
            ask = r.choice(['T', 'T', 'T', 'T', 'vmax', 'vmax', 'E', 'amax'])
            fig = FIG(fig_sp_h(kt, mt, '%s m' % fs(A)), '62%')
            base = '그림과 같이 마찰이 없는 수평면에서 용수철 상수가 %s N/m인 용수철에 질량 %s kg인 물체를 연결하고, 평형 위치 O에서 %s m 당겼다가 가만히 놓았더니 물체가 단진동을 하였다. ' % (fs(kk), fs(m), fs(A))
            if ask == 'T':
                if not cl(T, 3): return None
                body = P(base + '진동 주기는? (단, π = 3으로 계산한다.)' + tail) + fig
                return mc(body, U(T, 's', 3), wr(T, [T / 2, T * 2, 1 / T, 2 * T / 3, 6 * T, om / 6, T * 3], 's', 3), r=r, lv='하', fam='a',
                          steps=['각진동수 ω = √(k/m) = √(%s / %s) = %d rad/s' % (fs(kk), fs(m), om), 'T = 2π/ω = 2 × 3 / %d = %s s' % (om, fs(T, 3)), '(검산) T = 2π√(m/k) = 6 × √(%s/%s) = %s s' % (fs(m), fs(kk), fs(6 * math.sqrt(m / kk), 3))],
                          core='용수철 진자의 주기 T = 2π√(m/k)는 진폭과 무관하다.', point='k와 m으로 ω, T를 구한다.')
            if ask == 'vmax':
                body = P(base + '물체의 최대 속력은?' + tail) + fig
                return mc(body, U(vmax, 'm/s'), wr(vmax, [A * math.sqrt(kk * m), A * kk / m, A * m / kk if False else A * math.sqrt(m / kk), vmax * 2, vmax / 2, A * kk], 'm/s'), r=r, lv='중', fam='a',
                          steps=['에너지 보존 : ½kA² = ½mv²max', 'v max = A√(k/m) = %s × √(%s/%s) = %s × %d = %s m/s' % (fs(A), fs(kk), fs(m), fs(A), om, fs(vmax)), '(검산) ω = √(k/m) = %d rad/s, v max = ωA = %d × %s = %s m/s' % (om, om, fs(A), fs(vmax))],
                          core='단진동의 최대 속력 v max = ωA = A√(k/m) 이며 평형 위치에서 나타난다.', point='에너지 보존 ½kA² = ½mv²을 이용한다.')
            if ask == 'amax':
                am = om * om * A
                body = P(base + '물체의 최대 가속도의 크기는?' + tail) + fig
                return mc(body, U(am, 'm/s²'), wr(am, [vmax, om * A * 2, kk * A, am * 2, am / 2, kk / m], 'm/s²'), r=r, lv='중', fam='a',
                          steps=['진폭 위치에서 용수철 힘이 최대 : F = kA = %s × %s = %s N' % (fs(kk), fs(A), fs(kk * A)), 'a max = F/m = %s / %s = %s m/s²' % (fs(kk * A), fs(m), fs(kk * A / m)), '(검산) ω²A = %d² × %s = %s m/s²' % (om, fs(A), fs(am))],
                          core='단진동의 최대 가속도는 양 끝점에서 ω²A = kA/m 이다.', point='힘 F = kx 와 F = ma 를 연결한다.')
            body = P(base + '진동하는 동안 물체의 최대 운동 에너지는?' + tail) + fig
            return mc(body, U(E, 'J', 3), wr(E, [kk * A * A, 0.5 * kk * A, E * 2, E / 2, 0.5 * m * A * A, kk * A], 'J', 3), r=r, lv='중', fam='a',
                      steps=['처음 용수철의 탄성 에너지 ½kA² = ½ × %s × %s² = %s J' % (fs(kk), fs(A), fs(E, 3)), '평형 위치에서 탄성 에너지가 모두 운동 에너지로 : Ek max = %s J' % fs(E, 3), '(검산) ½mv²max = ½ × %s × %s² = %s J' % (fs(m), fs(vmax), fs(0.5 * m * vmax * vmax, 3))],
                      core='진동하는 동안 역학적 에너지 ½kA² 가 일정하고, 평형 위치에서 운동 에너지가 최대이다.', point='처음 탄성 에너지를 구하면 곧 최대 운동 에너지이다.')
        if form == 'atx':
            s, (au, xn, yn_) = r.choice([0.01, 0.02, 0.04, 0.05, 0.1]), r.choice([(5, 3, 4), (5, 4, 3), (10, 6, 8), (13, 5, 12), (5, 3, 4)])
            A = au * s
            x = xn * s
            Av = A; xv = x
            y = math.sqrt(Av * Av - xv * xv)
            if not cl(y, 3): return None
            v = om * y
            if not cl(v, 3): return None
            Ex = 0.5 * m * v * v
            assert abs(Ex - 0.5 * kk * (Av * Av - xv * xv)) < 1e-9
            ask = r.choice(['v', 'v', 'Ek', 'Ep'])
            fig = FIG(fig_sp_h(kt, mt, '%s m' % fs(Av, 3), '%s m' % fs(xv, 3), xv / Av), '62%')
            base = '그림과 같이 마찰이 없는 수평면에서 용수철 상수가 %s N/m인 용수철에 질량 %s kg인 물체를 연결하고 평형 위치 O에서 %s m 늘였다가 가만히 놓았더니 단진동을 하였다. ' % (fs(kk), fs(m), fs(Av, 3))
            Ep = 0.5 * kk * xv * xv
            if ask == 'v':
                body = P(base + '물체가 평형 위치에서 %s m 떨어진 지점을 지날 때의 속력은?' % fs(xv, 3) + tail) + fig
                return mc(body, U(v, 'm/s', 3), wr(v, [om * Av, om * xv, om * (Av - xv), math.sqrt(om * om * (Av * Av + xv * xv)), v * 2, v / 2], 'm/s', 3), r=r, lv='상', fam='b',
                          steps=['역학적 에너지 보존 : ½kA² = ½mv² + ½kx²', 'v² = (k/m)(A² - x²) = %d × (%s² - %s²) = %s' % (om * om, fs(Av, 3), fs(xv, 3), fs(om * om * (Av * Av - xv * xv), 4)), 'v = %s m/s' % fs(v, 3),
                                 '(검산) v = ω√(A² - x²) = %d × %s = %s m/s' % (om, fs(y, 3), fs(v, 3))],
                          core='단진동의 위치 x 에서의 속력 v = ω√(A² - x²) 이다.', point='총 에너지 = 운동 에너지 + 탄성 에너지로 속력을 구한다.')
            if ask == 'Ek':
                body = P(base + '물체가 평형 위치에서 %s m 떨어진 지점을 지날 때의 운동 에너지는?' % fs(xv, 3) + tail) + fig
                return mc(body, U(Ex, 'J', 3), wr(Ex, [0.5 * kk * Av * Av, Ep, 0.5 * kk * (Av - xv) ** 2, Ex * 2, Ex / 2, 0.5 * m * om * om * xv * xv], 'J', 3), r=r, lv='중', fam='b',
                          steps=['총 에너지 ½kA² = ½ × %s × %s² = %s J' % (fs(kk), fs(Av, 3), fs(0.5 * kk * Av * Av, 3)), '탄성 에너지 ½kx² = ½ × %s × %s² = %s J' % (fs(kk), fs(xv, 3), fs(Ep, 3)), 'Ek = %s - %s = %s J' % (fs(0.5 * kk * Av * Av, 3), fs(Ep, 3), fs(Ex, 3)),
                                 '(검산) ½mv² = ½ × %s × %s² = %s J' % (fs(m), fs(v, 3), fs(0.5 * m * v * v, 3))],
                          core='단진동에서 Ek + Ep = ½kA² (일정)이다.', point='총 에너지에서 위치 x의 탄성 에너지를 뺀다.')
            body = P(base + '물체가 평형 위치에서 %s m 떨어진 지점을 지날 때 용수철에 저장된 탄성 에너지는 운동 에너지의 몇 배인가?' % fs(xv, 3) + tail) + fig
            ratio = F(xn * xn, yn_ * yn_)
            return mc(body, _fq(ratio), [_fq(q) for q in (1 / ratio, ratio * ratio if ratio != 1 else F(2), F(1), F(3, 5), F(5, 3), F(25, 9), F(9, 25), F(4, 3)) if q != ratio and q > 0], r=r, lv='상', fam='b', sort='shuf',
                      steps=['탄성 에너지 ½kx², 운동 에너지 ½k(A² - x²)', 'Ep : Ek = x² : (A² - x²) = %s² : %s² = %s' % (fs(xv, 3), fs(y, 3), '%d : %d' % (ratio.numerator, ratio.denominator)), 'Ep/Ek = %s' % _fq(ratio), '(검산) Ep %s J, Ek %s J, 합 %s J = ½kA²' % (fs(Ep, 3), fs(Ex, 3), fs(Ep + Ex, 3))],
                      core='단진동에서 위치 에너지(탄성)와 운동 에너지의 비는 x² : (A² - x²) 이다.', point='같은 에너지 보존식에서 비를 구한다.')
        # 보기형
        fig = FIG(fig_sp_h(kt, mt, '%s m' % fs(A)), '62%')
        tops = [
            ('물체의 최대 속력은 %s m/s이다.' % fs(vmax), '물체의 최대 속력은 %s m/s이다.' % fs(vmax * 2), 'v max = A√(k/m) = %s m/s 이다.' % fs(vmax), 'v max = A√(k/m) = %s m/s 이다.' % fs(vmax)),
            ('진동 주기는 %s s이다.(π = 3)' % fs(T, 3), '진동 주기는 %s s이다.(π = 3)' % fs(T * 2, 3), 'T = 2π√(m/k) = 6 × √(%s/%s) = %s s 이다.' % (fs(m), fs(kk), fs(T, 3)), 'T = 2π/ω = 6/%d = %s s 이다.' % (om, fs(T, 3))),
            ('진폭을 2배로 하면 진동 주기는 변하지 않는다.', '진폭을 2배로 하면 진동 주기도 2배가 된다.', 'T = 2π√(m/k)는 진폭과 무관하다.', '주기는 m과 k 로만 정해지고 진폭과 무관하다.'),
            ('평형 위치를 지날 때 운동 에너지가 최대이다.', '평형 위치를 지날 때 탄성 에너지가 최대이다.', '평형 위치에서 탄성 에너지가 0이므로 운동 에너지가 총 에너지와 같아 최대이다.', '평형 위치에서는 탄성 에너지가 0이다.'),
            ('물체의 역학적 에너지(운동 + 탄성)는 %s J이고 진동하는 동안 일정하다.' % fs(E, 3), '물체의 역학적 에너지(운동 + 탄성)는 %s J이고 진동하는 동안 일정하다.' % fs(E * 2, 3), '½kA² = ½ × %s × %s² = %s J 이다.' % (fs(kk), fs(A), fs(E, 3)), '½kA² = %s J 이다.' % fs(E, 3)),
            ('진폭 지점에서 물체의 속력은 0이다.', '진폭 지점에서 물체의 속력은 최대이다.', '진폭 지점은 운동 방향이 바뀌는 순간이므로 속력이 0이다.', '진폭 지점에서는 순간 정지한다.'),
            ('질량을 4배로 하면 주기는 2배가 된다.', '질량을 4배로 하면 주기는 4배가 된다.', 'T ∝ √m 이므로 4배의 질량에서 주기는 2배이다.', 'T ∝ √m 이므로 2배이다.'),
        ]
        return topics_bogi(r, tops, '그림과 같이 마찰이 없는 수평면에서 용수철 상수가 %s N/m인 용수철에 질량 %s kg인 물체를 연결하고 평형 위치에서 %s m 당겼다가 가만히 놓았더니 단진동을 하였다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, π = 3이고, 용수철의 질량과 모든 마찰은 무시한다.)' % (fs(kk), fs(m), fs(A)),
                           pre=fig, fam='f', lv='중', core='단진동에서 주기는 진폭과 무관하고, 평형 위치에서 운동 에너지가 최대이다.', point='진폭·주기·에너지의 관계를 종합한다.')
    if form == 'graph':
        T = r.choice([0.2, 0.3, 0.4, 0.5, 0.6, 1.0, 1.2, 1.5, 2.0])
        A_cm = r.choice([2, 3, 4, 5, 6, 8, 10])
        m = r.choice([0.1, 0.2, 0.25, 0.5, 1, 2])
        om = 6 / T
        kk = m * om * om
        vmax = om * A_cm / 100
        Em = 0.5 * m * vmax * vmax
        assert abs(Em - 0.5 * kk * (A_cm / 100) ** 2) < 1e-9
        ask = r.choice(['k', 'v', 'E'])
        fig = FIG(fig_xt(A_cm, T), '64%')
        base = '그림은 마찰이 없는 수평면에서 용수철에 연결된 질량 %s kg인 물체의 단진동에서 평형 위치로부터의 변위 x 를 시간 t 에 따라 나타낸 것이다. ' % fs(m)
        tail2 = ' (단, π = 3이고, 용수철의 질량은 무시한다.)'
        if ask == 'k':
            if not cl(kk, 2): return None
            body = P(base + '용수철 상수는?' + tail2) + fig
            return mc(body, U(kk, 'N/m'), wr(kk, [m * (12 / T) ** 2, m * 6 / T, m * 36 / T, kk / 2, kk * 2, kk / 4, m * om], 'N/m'), r=r, lv='중', fam='c',
                      steps=['그래프에서 주기 T = %s s, 진폭 A = %d cm 이다.' % (fs(T), A_cm), 'ω = 2π/T = 6/%s = %s rad/s' % (fs(T), fs(om)), 'k = mω² = %s × %s² = %s N/m' % (fs(m), fs(om), fs(kk)), '(검산) T = 2π√(m/k) = 6 × √(%s/%s) = %s s' % (fs(m), fs(kk), fs(6 * math.sqrt(m / kk)))],
                      core='그래프에서 주기를 읽어 ω = 2π/T, k = mω² 를 구한다.', point='단진동 그래프의 해석과 ω-k-m 관계를 연결한다.')
        if ask == 'v':
            if not cl(vmax, 3): return None
            body = P(base + '물체의 최대 속력은?' + tail2) + fig
            return mc(body, U(vmax, 'm/s', 3), wr(vmax, [A_cm / T / 100, om * A_cm, 2 * 3 * A_cm / 100 / (T / 2), vmax * 2, vmax / 2, A_cm / 100 * 6 * T], 'm/s', 3), r=r, lv='중', fam='c',
                      steps=['그래프에서 T = %s s, A = %d cm = %s m' % (fs(T), A_cm, fs(A_cm / 100, 3)), 'ω = 2π/T = 6/%s = %s rad/s' % (fs(T), fs(om)), 'v max = ωA = %s × %s = %s m/s' % (fs(om), fs(A_cm / 100, 3), fs(vmax, 3)),
                             '(검산) 에너지 ½kA² = ½mv²max 에서 v max = A√(k/m) = %s m/s' % fs(A_cm / 100 * math.sqrt(kk / m), 3)],
                      core='단진동의 최대 속력 v max = ωA = 2πA/T 이다.', point='그래프의 A, T 를 단위(cm → m)에 맞추어 읽는다.')
        if not cl(Em, 4): return None
        body = P(base + '물체의 최대 운동 에너지는?' + tail2) + fig
        return mc(body, U(Em, 'J', 4), wr(Em, [0.5 * kk * A_cm / 100, 0.5 * m * om * A_cm, Em * 2, Em / 2, 0.5 * m * (A_cm / 100) ** 2, 0.5 * m * (A_cm / 100 / T) ** 2], 'J', 4), r=r, lv='상', fam='c',
                  steps=['그래프에서 T = %s s, A = %s m' % (fs(T), fs(A_cm / 100, 3)), 'ω = 6/T = %s rad/s, k = mω² = %s N/m' % (fs(om), fs(kk)), '최대 운동 에너지 = ½kA² = ½ × %s × %s² = %s J' % (fs(kk), fs(A_cm / 100, 3), fs(Em, 4)), '(검산) ½mv²max = ½ × %s × %s² = %s J' % (fs(m), fs(vmax, 3), fs(0.5 * m * vmax * vmax, 4))],
                  core='그래프(A, T) → ω → v max → Ek max 로 연결한다.', point='에너지 보존과 단진동 식을 모두 사용한다.')
    if form == 'chg':
        A = r.choice([0.05, 0.1, 0.2])
        kind = r.choice(['m', 'k', 'par', 'ser', 'half', 'mk'])
        if kind == 'm':
            n = r.choice([2, 4, 9, 3]); qm, qk = F(n), F(1); desc = '질량이 %d배인 물체로 바꾸어' % n
        elif kind == 'k':
            n = r.choice([2, 4, 9, 3]); qm, qk = F(1), F(n); desc = '용수철 상수가 %d배인 용수철로 바꾸어' % n
        elif kind == 'par':
            qm, qk = F(1), F(2); desc = '똑같은 용수철 2개를 나란히(병렬) 연결하여 물체에 연결해'
        elif kind == 'ser':
            qm, qk = F(1), F(1, 2); desc = '똑같은 용수철 2개를 일렬로(직렬) 연결하여 물체에 연결해'
        elif kind == 'half':
            qm, qk = F(1), F(2); desc = '용수철을 절반 길이로 잘라 그 한 조각에 물체를 연결해'
        else:
            qm, qk = F(r.choice([2, 4, 3])), F(r.choice([2, 4, 3])); desc = '질량이 %d배인 물체를 용수철 상수가 %d배인 용수철에 연결해' % (qm, qk) if False else None
            if qm == qk: return None
            desc = '질량이 %d배인 물체를 용수철 상수가 %d배인 용수철에 연결해' % (qm, qk)
        what = r.choice(['T', 'f', 'v', 'E', 'amax'])
        # 같은 진폭에서
        qT = qm / qk   # T'^2/T^2
        qw2 = qk / qm  # ω'^2/ω^2
        lab = {'T': ('진동 주기', qT, 'sqrt'), 'f': ('진동수', qw2, 'sqrt'), 'v': ('최대 속력', qw2, 'sqrt'), 'E': ('진동 에너지(역학적 에너지)', qk, 'lin'), 'amax': ('최대 가속도의 크기', qk / qm, 'lin')}
        name, q, typ = lab[what]
        ans = _fr(q) if typ == 'sqrt' else _fq(q)
        # 교차 검증 : ω 로 직접
        w0, w1 = math.sqrt(1.0), math.sqrt(float(qk / qm))
        if what == 'T': assert abs(1 / w1 - math.sqrt(float(q))) < 1e-9
        if what in ('f', 'v'): assert abs(w1 - math.sqrt(float(q))) < 1e-9
        if what == 'E': assert abs(0.5 * float(qk) * A * A / (0.5 * A * A) - float(q)) < 1e-9
        if what == 'amax': assert abs(w1 ** 2 - float(q)) < 1e-9
        cands = []
        for c in [q, 1 / q, q * q, 1 / (q * q) if q * q != 0 else q, F(1), qm, qk, 1 / qm, 1 / qk, q * 2, q / 2]:
            cands.append(_fr(c) if typ == 'sqrt' else _fq(c))
            cands.append(_fq(c) if typ == 'sqrt' else _fr(c))
        wl = []
        for c in cands:
            if c != ans and c not in wl: wl.append(c)
        fig = FIG(fig_sp_h('k', 'm'), '58%')
        body = P('그림과 같이 마찰이 없는 수평면에서 용수철에 연결된 물체가 진폭 A 로 단진동을 하고 있다. 용수철과 물체를 %s 같은 진폭 A 로 단진동시킬 때, 처음에 비해 %s는 몇 배가 되는가? (단, 용수철의 질량과 모든 마찰은 무시한다.)' % (desc, name) + '') + fig
        ok = _wordlist_ok(wl)
        if not ok: return None
        stp = ['ω = √(k/m) 이므로 새 용수철 상수 k\' = %s k, 새 질량 m\' = %s m 에서 ω\'/ω = √(%s)' % (_fqs(qk), _fqs(qm), _fqs(qk / qm)),
               {'T': 'T = 2π/ω 이므로 T\'/T = √(%s) = %s' % (_fqs(qT), ans), 'f': 'f = ω/2π 이므로 f\'/f = √(%s) = %s' % (_fqs(qw2), ans), 'v': 'v max = ωA 이고 A 가 같으므로 v\'/v = √(%s) = %s' % (_fqs(qw2), ans),
                'E': '에너지 ½kA² 에서 A 가 같으므로 E\'/E = k\'/k = %s' % ans, 'amax': 'a max = kA/m 이므로 a\'/a = (k\'/k)/(m\'/m) = %s' % ans}[what],
               '(검산) 직접 계산 : %s' % ans]
        return mc(body, ans, wl, r=r, lv=('하' if what in ('T', 'f') and kind in ('m', 'k', 'par', 'ser', 'half') else '중') if what in ('T', 'f', 'v') else '상', fam='d', sort='shuf', steps=stp,
                  core='T = 2π√(m/k), v max = A√(k/m), E = ½kA² 로 k·m 변화에 따른 변화율을 구한다.', point='질량·용수철 상수의 변화가 주기와 에너지에 미치는 영향을 비교한다.')
    if form == 'vert':
        om = r.choice([2, 4, 5, 10, 20])
        x0 = 10.0 / om ** 2
        m = r.choice([0.1, 0.2, 0.25, 0.5, 1, 2])
        kk = m * G / x0
        if not cl(kk, 2) or not cl(x0, 3): return None
        T = 6.0 / om
        A = r.choice([0.01, 0.02, 0.03, 0.04, 0.05, 0.1])
        if A >= x0: return None
        vmax = om * A
        # 에너지로 검산 : 최저점 → 평형 위치
        Elow = 0.5 * kk * (x0 + A) ** 2
        Eeq = 0.5 * kk * x0 * x0
        assert abs(0.5 * m * vmax * vmax - (Elow - Eeq - m * G * A)) < 1e-9
        ask = r.choice(['T', 'v', 'Elow', 'ext'])
        fig = FIG(fig_sp_v('k', '%s kg' % fs(m), x0txt='%s m' % fs(x0, 3), Atxt='%s m' % fs(A, 3) if ask in ('v', 'Elow', 'ext') else None), '56%')
        base = '그림과 같이 천장에 매단 용수철에 질량 %s kg인 물체를 달았더니 용수철이 원래 길이보다 %s m 늘어난 상태로 정지하였다. ' % (fs(m), fs(x0, 3))
        if ask == 'T':
            if not cl(T, 3): return None
            body = P(base + '이 물체를 아래로 조금 당겼다 놓았을 때 단진동의 주기는? (단, π = 3이고, 중력 가속도는 10 m/s²이며, 용수철의 질량과 공기 저항은 무시한다.)') + FIG(fig_sp_v('k', '%s kg' % fs(m), x0txt='%s m' % fs(x0, 3)), '56%')
            return mc(body, U(T, 's', 3), wr(T, [T / 2, T * 2, 6 * math.sqrt(x0), 6 * math.sqrt(x0 / 10) * 2, 6 * x0, math.sqrt(x0), T * 3], 's', 3), r=r, lv='중', fam='e',
                      steps=['평형에서 mg = kx₀ → k = mg/x₀ = %s × 10 / %s = %s N/m' % (fs(m), fs(x0, 3), fs(kk)), 'ω = √(k/m) = √(g/x₀) = √(10/%s) = %d rad/s' % (fs(x0, 3), om), 'T = 2π/ω = 6/%d = %s s' % (om, fs(T, 3)), '(검산) T = 2π√(m/k) = 6 × √(%s/%s) = %s s' % (fs(m), fs(kk), fs(6 * math.sqrt(m / kk), 3))],
                      core='연직 용수철 진자의 주기 T = 2π√(x₀/g) 는 평형 늘어남 x₀ 로 구한다.', point='중력은 평형 위치를 옮길 뿐 주기를 바꾸지 않는다.')
        if ask == 'v':
            if not cl(vmax, 3): return None
            body = P(base + '이 물체를 평형 위치에서 아래로 %s m 더 당겼다가 가만히 놓았다. 물체의 최대 속력은? (단, 중력 가속도는 10 m/s²이며, 용수철의 질량과 공기 저항은 무시한다.)' % fs(A, 3)) + fig
            return mc(body, U(vmax, 'm/s', 3), wr(vmax, [math.sqrt(2 * G * A), A * math.sqrt(kk / m) * 2, math.sqrt(kk / m) * (A + x0), vmax * 2, vmax / 2, math.sqrt(kk * A * A / m + 2 * G * A)], 'm/s', 3), r=r, lv='상', fam='e',
                      steps=['k = mg/x₀ = %s N/m, ω = √(k/m) = %d rad/s' % (fs(kk), om), '평형 위치를 중심으로 진폭 A = %s m 의 단진동 → v max = ωA = %d × %s = %s m/s' % (fs(A, 3), om, fs(A, 3), fs(vmax, 3)),
                             '(검산) 최저점→평형 위치 에너지 : ½k(x₀+A)² - ½kx₀² - mgA = %s J = ½mv² = %s J' % (fs(Elow - Eeq - m * G * A, 5), fs(0.5 * m * vmax * vmax, 5))],
                      core='연직 진자도 평형 위치를 중심으로 한 단진동이며, 속력은 평형 위치에서 최대이다.', point='중력 위치 에너지가 포함된 에너지 보존과 ωA 의 일치.')
        if ask == 'ext':
            body = P(base + '이 물체를 평형 위치에서 아래로 %s m 더 당겼다가 가만히 놓았다. 물체가 가장 높은 지점에 있을 때 용수철이 늘어난 길이는? (단, 용수철의 질량과 공기 저항은 무시한다.)' % fs(A, 3)) + fig
            e = x0 - A
            return mc(body, U(e, 'm', 3), wr(e, [x0 + A, x0, A, 0, x0 - 2 * A, 2 * x0], 'm', 3), r=r, lv='중', fam='e',
                      steps=['단진동의 중심은 평형 위치이므로 위·아래로 같은 진폭 %s m 만큼 움직인다.' % fs(A, 3), '가장 높은 지점의 늘어난 길이 = x₀ - A = %s - %s = %s m' % (fs(x0, 3), fs(A, 3), fs(e, 3)), '(검산) 최저점 늘어남 %s m, 두 지점의 평균 = %s m = x₀' % (fs(x0 + A, 3), fs((x0 + A + e) / 2, 3))],
                      core='연직 용수철 진자는 평형 위치(늘어남 x₀)를 중심으로 대칭으로 진동한다.', point='진폭이 x₀보다 작으면 최고점에서도 용수철이 늘어난 상태이다.')
        body = P(base + '이 물체를 평형 위치에서 아래로 %s m 더 당긴 순간, 용수철에 저장된 탄성 에너지는? (단, 용수철의 질량은 무시한다.)' % fs(A, 3)) + fig
        return mc(body, U(Elow, 'J', 4), wr(Elow, [0.5 * kk * A * A, Eeq, 0.5 * kk * x0 * x0 + 0.5 * kk * A * A, Elow + m * G * A, Elow * 2, 0.5 * kk * (x0 - A) ** 2], 'J', 4), r=r, lv='상', fam='e',
                  steps=['k = mg/x₀ = %s × 10 / %s = %s N/m' % (fs(m), fs(x0, 3), fs(kk)), '늘어난 길이 x₀ + A = %s + %s = %s m' % (fs(x0, 3), fs(A, 3), fs(x0 + A, 3)), '탄성 에너지 ½k(x₀+A)² = ½ × %s × %s² = %s J' % (fs(kk), fs(x0 + A, 3), fs(Elow, 4)),
                         '(검산) ½kx₀² + kx₀A + ½kA² = %s + %s + %s = %s J' % (fs(Eeq, 4), fs(kk * x0 * A, 4), fs(0.5 * kk * A * A, 4), fs(Eeq + kk * x0 * A + 0.5 * kk * A * A, 4))],
                  core='연직 진자에서 탄성 에너지는 평형 늘어남 x₀ 가 포함된 전체 늘어난 길이로 계산한다.', point='진폭만이 아니라 평형에서의 늘어남을 더해야 한다.')


def _fqs(q):
    q = F(q)
    return str(q.numerator) if q.denominator == 1 else '%d/%d' % (q.numerator, q.denominator)


def _wordlist_ok(wl):
    return len(wl) >= 4


# ================================================================== ph112 도플러 효과와 단진동 · 원운동
def fig_dop_shm(Atxt, f0txt, w=340, hh=150, who='source'):
    """용수철에 매달려 단진동하는 음원(스피커)과 멀리 정지한 관측자."""
    f = Fig(w, hh)
    fy = 92
    f.line(10, fy, w - 8, fy, INK, 1.6)
    for i in range(10, w - 8, 8):
        f.line(i, fy, i - 5, fy + 6, GR, 1)
    f.line(20, fy - 52, 20, fy, GR, 3)
    for v in range(fy - 50, fy, 8):
        f.line(20, v, 14, v + 6, GR, 1)
    xe = 120
    f.spring(20, fy - 15, xe - 26, 7, 8)
    f.rect(xe - 26, fy - 30, 52, 30, '#cfe2f7', INK, 1.7)
    f.text(xe, fy - 10, '음원', 12.5, bold=True)
    f.line(xe, fy - 56, xe, fy + 20, GR, 1, '4 3')
    f.text(xe, fy + 36, 'O', 12.5, bold=True, c=GR)
    s = 44
    f.line(xe - s, fy + 12, xe + s, fy + 12, GR, 1.2)
    for sg in (-1, 1):
        f.line(xe + sg * s, fy + 6, xe + sg * s, fy + 18, INK, 1.4)
    f.text(xe + s + 4, fy + 34, 'A = ' + Atxt, 12.5, 'start', True, RD)
    # 관측자
    ox = w - 40
    f.circ(ox, fy - 44, 8, '#f6d9d6', INK, 1.5)
    f.line(ox, fy - 36, ox, fy - 12, INK, 1.8)
    f.line(ox, fy - 30, ox - 9, fy - 20, INK, 1.5)
    f.line(ox, fy - 30, ox + 9, fy - 20, INK, 1.5)
    f.line(ox, fy - 12, ox - 7, fy, INK, 1.5)
    f.line(ox, fy - 12, ox + 7, fy, INK, 1.5)
    f.text(ox, fy + 18, '관측자', 12, bold=True, c=GR)
    f.text(xe + 62, fy - 40, f0txt, 12.5, 'start', True, BL)
    f.arrow(xe + 62, fy - 30, xe + 100, fy - 30, BL, 1.8)
    return f.svg()


def fig_dop_circ(Rtxt, f0txt=None, mover='source', w=340, hh=180):
    """위에서 본 원운동 + 같은 평면에서 멀리 있는 관측자(또는 음원)."""
    f = Fig(w, hh)
    cx, cy, R = 110, 90, 58
    f.circ(cx, cy, R, 'none', BL, 1.8, '5 3')
    f.circ(cx, cy, 2.5, GR, GR, 1)
    ang = math.radians(-40)
    px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
    f.line(cx, cy, px, py, GR, 1.2)
    f.circ(px, py, 9, '#cfe2f7', INK, 1.7)
    f.text(px, py + 4, 'S' if mover == 'source' else 'P', 11.5, bold=True)
    f.text((cx + px) / 2 - 4, (cy + py) / 2 + 14, Rtxt, 12.5, 'end', True, GR)
    # 회전 화살표(반시계)
    a = math.radians(-40)
    f.arrow(px - 4, py + 16, px + 18, py + 34 - 12, RD, 2)
    f.line(cx - R - 14, cy, w - 10, cy, GR, 1, '4 3')
    ox = w - 52
    if mover == 'source':
        f.circ(ox, cy, 9, '#f6d9d6', INK, 1.7)
        f.text(ox, cy + 4, 'P', 11.5, bold=True)
        f.text(ox, cy + 26, '관측자', 12, bold=True, c=GR)
        if f0txt: f.text(cx, cy + R + 22, '음원 ' + f0txt, 12.5, bold=True, c=BL)
    else:
        f.circ(ox, cy, 9, '#d5eedf', INK, 1.7)
        f.text(ox, cy + 4, 'S', 11.5, bold=True)
        f.text(ox, cy + 26, '음원(정지)', 12, bold=True, c=GR)
        if f0txt: f.text(ox, cy - 18, f0txt, 12.5, bold=True, c=BL)
    f.text(cx, cy + R + 22, '위에서 본 그림', 12, bold=False, c=GR) if mover != 'source' else None
    return f.svg()


def fig_dop_graph(f0, v, vs, T, w=330, hh=200):
    fmax = f0 * v / (v - vs)
    fmin = f0 * v / (v + vs)
    lo, hi = fmin - (fmax - fmin) * 0.6, fmax + (fmax - fmin) * 0.5
    p = Plot(w, hh, T * 1.25, hi, 0, lo, ml=56, mr=16, mt=16, mb=28)
    p.axes('t (s)', 'f (Hz)', xticks=[T / 2, T], yticks=[], xfmt=lambda v_: num(v_, 3))
    pts = [(T * i / 100.0, f0 * v / (v - vs * math.sin(2 * math.pi * i / 100.0))) for i in range(0, 101)]
    p.pl(pts, BL, 2.4)
    for val in (fmax, fmin):
        p.line(p.px(0), p.py(val), p.px(T * 1.2), p.py(val), GR, 1, '4 3')
        p.text(p.px(0) - 6, p.py(val) + 4, num(round(val, 1), 1), 11.5, 'end', c=GR)
    return p.svg()


VS_OPTS = [5, 10, 17, 20, 30, 34, 40, 50, 60, 68, 85]


def _f0_for(r, v, vs, extra=None):
    cs = list(range(200, 1101, 10)); r.shuffle(cs)
    for f0 in cs:
        a, b = F(f0 * v, v - vs), F(f0 * v, v + vs)
        if cl(a, 1) and cl(b, 1) and a.denominator in (1, 2, 5, 10) and b.denominator in (1, 2, 5, 10):
            return f0
    return None


@T('ph112')
@balanced
def g112(r, k):
    form = pick(r, ['shm'] * 4 + ['circ'] * 3 + ['obs'] * 2 + ['inv'] * 1 + ['bogi'] * 2)
    v = r.choice([340, 340, 340, 300, 350, 330])
    tail = ' (단, 소리의 속력은 %d m/s이고, 관측자는 정지해 있다.)' % v
    if form in ('shm', 'bogi'):
        vs = r.choice(VS_OPTS)
        if vs >= v / 4: return None
        mode = r.choice(['om', 'T'])
        if mode == 'om':
            A = r.choice([0.05, 0.1, 0.2, 0.25, 0.5, 1, 2])
            om = vs / A
            if not cl(om, 2) or om < 2: return None
            spec = '각진동수 %s rad/s' % fs(om)
        else:
            A = r.choice([0.05, 0.1, 0.2, 0.25, 0.5, 1, 2])
            T = 6 * A / vs
            if not cl(T, 3) or T < 0.01: return None
            om = 6 / T
            spec = '주기 %s s' % fs(T, 3)
        assert abs(om * A - vs) < 1e-6
        f0 = _f0_for(r, v, vs)
        if f0 is None: return None
        fmax = f0 * v / (v - vs); fmin = f0 * v / (v + vs)
        # 교차 검증 : 파장·속력 관계
        lam_min = (v - vs) / f0
        assert abs(fmax * lam_min - v) < 1e-6
        fig = FIG(fig_dop_shm('%s m' % fs(A), 'f₀ = %d Hz' % f0), '66%')
        base = '그림은 용수철에 연결되어 진폭 %s m, %s로 직선 위를 단진동하는 음원(진동수 %d Hz)과, 이 직선의 연장선 위 멀리 정지해 있는 관측자를 나타낸 것이다. ' % (fs(A), spec, f0)
        pi_ = ' (단, π = 3이다.)' if mode == 'T' else ''
        tail_ = ' (단, 소리의 속력은 %d m/s이고, 관측자는 정지해 있다.)' % v if mode == 'om' else ' (단, 소리의 속력은 %d m/s이고 π = 3이며, 관측자는 정지해 있다.)' % v
        if form == 'bogi':
            tops = [
                ('음원이 평형 위치 O를 관측자 쪽으로 지날 때 관측자가 듣는 진동수가 가장 크다.', '음원이 진폭 끝에 있을 때 관측자가 듣는 진동수가 가장 크다.', '음원의 속력이 최대인 평형 위치에서 관측자 쪽으로 움직일 때 f = f₀v/(v - vs)가 최대이다.', '진폭 끝에서는 음원의 속력이 0이므로 f₀ 와 같은 진동수를 듣는다.'),
                ('관측자가 듣는 소리의 최대 진동수는 %s Hz이다.' % fs(fmax), '관측자가 듣는 소리의 최대 진동수는 %s Hz이다.' % fs(fmax - (fmax - f0) * 0.5 if False else f0 * (v + vs) / v), 'vs = ωA = %s m/s, f max = f₀v/(v - vs) = %s Hz 이다.' % (fs(vs), fs(fmax)), 'f max = f₀v/(v - vs) = %s Hz 이다.(f₀(v+vs)/v 가 아니다)' % fs(fmax)),
                ('관측자가 듣는 소리의 최소 진동수는 %s Hz이다.' % fs(fmin), '관측자가 듣는 소리의 최소 진동수는 %s Hz이다.' % fs(f0 * (v - vs) / v), 'f min = f₀v/(v + vs) = %s Hz 이다.' % fs(fmin), 'f min = f₀v/(v + vs) = %s Hz 이다.' % fs(fmin)),
                ('진폭을 크게 하면(진동수는 그대로) 관측자가 듣는 최대 진동수는 커진다.', '진폭을 크게 하면(진동수는 그대로) 관측자가 듣는 최대 진동수는 작아진다.', '음원의 최대 속력 vs = ωA 가 커져 f max = f₀v/(v - vs)가 커진다.', 'vs 가 커지면 f max 가 커진다.'),
                ('관측자가 듣는 진동수는 f₀ 보다 큰 값과 작은 값을 모두 가진다.', '관측자가 듣는 진동수는 항상 f₀ 보다 크다.', '음원이 다가올 때는 f₀ 보다 크고 멀어질 때는 f₀ 보다 작다.', '음원이 멀어지는 동안에는 f₀ 보다 작은 진동수가 들린다.'),
                ('음원의 최대 속력은 %s m/s이다.' % fs(vs), '음원의 최대 속력은 %s m/s이다.' % fs(vs * 2), 'vs = ωA = %s m/s 이다.' % fs(vs), 'vs = ωA = %s m/s 이다.' % fs(vs)),
                ('음원이 진폭 끝에 있는 순간 관측자는 진동수 f₀ 의 소리를 듣는다.', '음원이 진폭 끝에 있는 순간 관측자는 진동수가 가장 작은 소리를 듣는다.', '진폭 끝에서는 속력이 0이므로 도플러 효과가 없다.', '최소 진동수는 평형 위치를 관측자에서 멀어지며 지날 때 나타난다.'),
            ]
            return topics_bogi(r, tops, base + '이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' + tail_, pre=fig, fam='e', lv='중', core='단진동하는 음원은 평형 위치에서 속력이 최대이고, 이때 도플러 효과의 변화가 가장 크다.', point='단진동의 속도 변화와 도플러 효과를 연결한다.')
        ask = r.choice(['vs', 'vs', 'vs', 'vs', 'fmax', 'fmin', 'ratio', 'lam'])
        if ask == 'vs':
            body = P(base + '음원의 최대 속력은?' + pi_) + fig
            return mc(body, U(vs, 'm/s'), wr(vs, [om, A, vs * 2, vs / 2, om * A * 2, om / A if False else vs + 10], 'm/s'), r=r, lv='하', fam='a',
                      steps=['각진동수 ω = %s rad/s%s' % (fs(om), '' if mode == 'om' else ' (ω = 2π/T = 6/%s)' % fs(T, 3)), '단진동의 최대 속력 vs = ωA = %s × %s = %s m/s' % (fs(om), fs(A), fs(vs))],
                      core='단진동의 최대 속력은 vs = ωA 이고 평형 위치에서 나타난다.', point='단진동 식으로 음원의 속력을 구한다.')
        if ask == 'fmax':
            body = P(base + '관측자가 듣는 소리의 최대 진동수는?' + tail_) + fig
            return mc(body, U(fmax, 'Hz', 1), wr(fmax, [f0 * (v + vs) / v, f0 * v / (v + vs), f0 + vs, f0 * v / (v - 2 * vs), f0 * (v - vs) / v, f0 * (v + 2 * vs) / v], 'Hz', 1), r=r, lv='중', fam='a',
                      steps=['음원의 최대 속력 vs = ωA = %s m/s (평형 위치)' % fs(vs), '다가올 때 f max = f₀v/(v - vs) = %d × %d / (%d - %s) = %s Hz' % (f0, v, v, fs(vs), fs(fmax, 1)), '(검산) 파장 λ = (v - vs)/f₀ = %s m, f = v/λ = %s Hz' % (fs(lam_min, 4), fs(v / lam_min, 1))],
                      core='음원이 속력 vs 로 관측자에게 다가올 때 f = f₀v/(v - vs) 이다.', point='단진동의 최대 속력과 도플러 공식을 연결한다.')
        if ask == 'fmin':
            body = P(base + '관측자가 듣는 소리의 최소 진동수는?' + tail_) + fig
            return mc(body, U(fmin, 'Hz', 1), wr(fmin, [f0 * (v - vs) / v, f0 * v / (v - vs), f0 - vs, f0 * v / (v + 2 * vs), f0 * (v + vs) / v, f0 * (v - 2 * vs) / v], 'Hz', 1), r=r, lv='중', fam='a',
                      steps=['음원의 최대 속력 vs = ωA = %s m/s' % fs(vs), '멀어질 때 f min = f₀v/(v + vs) = %d × %d / (%d + %s) = %s Hz' % (f0, v, v, fs(vs), fs(fmin, 1)), '(검산) 파장 λ = (v + vs)/f₀ = %s m, f = v/λ = %s Hz' % (fs((v + vs) / f0, 4), fs(v / ((v + vs) / f0), 1))],
                      core='음원이 속력 vs 로 멀어질 때 f = f₀v/(v + vs) 이다.', point='멀어지는 경우는 분모가 v + vs 이다.')
        if ask == 'ratio':
            q = F(v + vs, v - vs)
            body = P(base + '관측자가 듣는 최대 진동수는 최소 진동수의 몇 배인가?' + tail_) + fig
            qs = '%d/%d배' % (q.numerator, q.denominator) if q.denominator != 1 else '%d배' % q.numerator
            wl = []
            for c in [F(v - vs, v + vs), F(v, v - vs), F(v + vs, v), F(v, v + vs), q * q, F(v, vs)]:
                s_ = '%d/%d배' % (c.numerator, c.denominator) if c.denominator != 1 else '%d배' % c.numerator
                if s_ != qs: wl.append(s_)
            assert abs(fmax / fmin - float(q)) < 1e-9
            return mc(body, qs, wl, r=r, lv='상', fam='a', sort='shuf',
                      steps=['vs = ωA = %s m/s' % fs(vs), 'f max / f min = [v/(v - vs)] / [v/(v + vs)] = (v + vs)/(v - vs) = %d/%d = %s' % (v + vs, v - vs, qs), '(검산) %s / %s = %s' % (fs(fmax, 1), fs(fmin, 1), fs(fmax / fmin, 3))],
                      core='단진동하는 음원의 최대·최소 진동수 비는 (v + vs)/(v - vs) 이다(f₀ 와 무관).', point='f₀ 가 소거되는 비를 이용한다.')
        lam = lam_min
        body = P(base + '관측자가 듣는 소리의 파장 중 가장 짧은 파장은?' + tail_) + fig
        return mc(body, U(lam, 'm', 3), wr(lam, [v / f0, (v + vs) / f0, v / fmin, lam * 2, (v - vs) / (f0 * 2), vs / f0], 'm', 3), r=r, lv='상', fam='a',
                  steps=['vs = ωA = %s m/s' % fs(vs), '음원이 다가오는 쪽으로 진행하는 소리의 파장 λ = (v - vs)/f₀ = (%d - %s)/%d = %s m' % (v, fs(vs), f0, fs(lam, 4)), '(검산) f max = v/λ = %s Hz = f₀v/(v - vs)' % fs(v / lam, 1)],
                  core='음원이 다가오면 파장이 (v - vs)/f₀ 로 짧아진다.', point='도플러 효과는 음원 앞쪽 파장의 변화로 설명된다.')
    if form in ('circ', 'obs'):
        vs = r.choice(VS_OPTS)
        if vs >= v / 4: return None
        Rr = r.choice([0.5, 1, 2, 3, 4, 5, 10])
        T = 6 * Rr / vs
        if not cl(T, 3) or T < 0.02: return None
        f0 = _f0_for(r, v, vs) if form == 'circ' else r.choice(range(200, 1001, 20))
        if f0 is None: return None
        om = 2 * 3 / T
        assert abs(om * Rr - vs) < 1e-6
        if form == 'circ':
            fmax = f0 * v / (v - vs); fmin = f0 * v / (v + vs)
            ask = r.choice(['vs', 'vs', 'vs', 'fmax', 'fmin', 'dpos'])
            fig = FIG(fig_dop_circ('R = %s m' % fs(Rr), 'f₀ = %d Hz' % f0), '64%')
            base = '그림은 위에서 본 모습으로, 진동수 %d Hz의 소리를 내는 음원이 반지름 %s m인 원 둘레를 주기 %s s로 등속 원운동하고, 같은 평면에서 원으로부터 멀리 떨어진 곳에 관측자가 정지해 있는 것을 나타낸 것이다. ' % (f0, fs(Rr), fs(T, 3))
            tl = ' (단, 소리의 속력은 %d m/s이고 π = 3이며, 관측자까지의 거리는 원의 반지름보다 매우 크다.)' % v
            if ask == 'vs':
                body = P(base + '음원의 속력은?' + ' (단, π = 3이다.)') + fig
                return mc(body, U(vs, 'm/s'), wr(vs, [2 * 3 * Rr, Rr / T, vs * 2, vs / 2, Rr * T, 3 * Rr / T * 4], 'm/s'), r=r, lv='하', fam='b',
                          steps=['한 바퀴 2πR = 2 × 3 × %s = %s m 를 주기 %s s 에 돈다.' % (fs(Rr), fs(6 * Rr), fs(T, 3)), 'vs = 2πR/T = %s / %s = %s m/s' % (fs(6 * Rr), fs(T, 3), fs(vs)), '(검산) vs = ωR = %s × %s = %s m/s' % (fs(om), fs(Rr), fs(om * Rr))],
                          core='등속 원운동의 속력은 v = 2πR/T = ωR 이다.', point='주기와 반지름으로 속력을 구한다.')
            if ask == 'dpos':
                body = P(base + '관측자가 듣는 소리의 최대 진동수와 최소 진동수의 차는?' + tl) + fig
                d = fmax - fmin
                return mc(body, U(d, 'Hz', 1), wr(d, [fmax - f0, f0 - fmin, 2 * vs, d / 2, f0 * 2 * vs / v, (fmax + fmin) / 2], 'Hz', 1), r=r, lv='상', fam='b',
                          steps=['vs = 2πR/T = %s m/s' % fs(vs), 'f max = f₀v/(v - vs) = %s Hz, f min = f₀v/(v + vs) = %s Hz' % (fs(fmax, 1), fs(fmin, 1)), '차 = %s - %s = %s Hz' % (fs(fmax, 1), fs(fmin, 1), fs(d, 1)), '(검산) f max - f min = 2f₀vvs/(v² - vs²) = %s Hz' % fs(2 * f0 * v * vs / (v * v - vs * vs), 1)],
                          core='원운동하는 음원은 관측자 방향 속도 성분이 변하므로 진동수가 최대와 최소 사이를 오간다.', point='최대·최소 진동수를 각각 구해 차를 계산한다.')
            if ask == 'fmax':
                body = P(base + '관측자가 듣는 소리의 최대 진동수는?' + tl) + fig
                return mc(body, U(fmax, 'Hz', 1), wr(fmax, [f0 * (v + vs) / v, f0 * v / (v + vs), f0 * v / (v - 2 * vs), f0 + vs, f0 * (v - vs) / v, f0 * v / (v - vs / 2)], 'Hz', 1), r=r, lv='중', fam='b',
                          steps=['음원의 속력 vs = 2πR/T = 2 × 3 × %s / %s = %s m/s' % (fs(Rr), fs(T, 3), fs(vs)), '관측자 쪽으로 향하는 순간 f max = f₀v/(v - vs) = %d × %d / (%d - %s) = %s Hz' % (f0, v, v, fs(vs), fs(fmax, 1)), '(검산) 파장 (v - vs)/f₀ = %s m, v/λ = %s Hz' % (fs((v - vs) / f0, 4), fs(v * f0 / (v - vs), 1))],
                          core='원운동하는 음원이 관측자를 향해 움직이는 순간 진동수가 최대이다.', point='원운동의 속력과 도플러 공식을 연결한다.')
            body = P(base + '관측자가 듣는 소리의 최소 진동수는?' + tl) + fig
            return mc(body, U(fmin, 'Hz', 1), wr(fmin, [f0 * (v - vs) / v, f0 * v / (v - vs), f0 * v / (v + 2 * vs), f0 - vs, f0 * (v + vs) / v], 'Hz', 1), r=r, lv='중', fam='b',
                      steps=['음원의 속력 vs = 2πR/T = %s m/s' % fs(vs), '관측자에서 멀어지는 순간 f min = f₀v/(v + vs) = %d × %d / (%d + %s) = %s Hz' % (f0, v, v, fs(vs), fs(fmin, 1)), '(검산) 파장 (v + vs)/f₀ = %s m, v/λ = %s Hz' % (fs((v + vs) / f0, 4), fs(v * f0 / (v + vs), 1))],
                      core='원운동하는 음원이 관측자에게서 멀어지는 순간 진동수가 최소이다.', point='멀어질 때는 v + vs 를 쓴다.')
        # obs : 원운동하는 관측자, 음원 정지
        fmax = F(f0 * (v + vs), v); fmin = F(f0 * (v - vs), v)
        if not (cl(fmax, 1) and cl(fmin, 1)): return None
        fmax, fmin = float(fmax), float(fmin)
        assert abs(fmax - f0 - (f0 - fmin)) < 1e-9
        ask = r.choice(['fmax', 'fmin', 'diff'])
        fig = FIG(fig_dop_circ('R = %s m' % fs(Rr), 'f₀ = %d Hz' % f0, mover='obs'), '64%')
        base = '그림은 위에서 본 모습으로, 반지름 %s m인 원 둘레를 주기 %s s로 등속 원운동하는 관측자 P와, 같은 평면에서 멀리 정지해 있는 진동수 %d Hz의 음원 S를 나타낸 것이다. ' % (fs(Rr), fs(T, 3), f0)
        tl = ' (단, 소리의 속력은 %d m/s이고 π = 3이며, 음원까지의 거리는 원의 반지름보다 매우 크다.)' % v
        if ask == 'fmax':
            body = P(base + 'P가 측정하는 소리의 최대 진동수는?' + tl) + fig
            return mc(body, U(fmax, 'Hz', 1), wr(fmax, [f0 * v / (v - vs), fmin, f0 + vs, f0 * v / (v + vs), f0 * (v + 2 * vs) / v], 'Hz', 1), r=r, lv='중', fam='c',
                      steps=['관측자의 속력 vo = 2πR/T = 2 × 3 × %s / %s = %s m/s' % (fs(Rr), fs(T, 3), fs(vs)), '음원 쪽으로 향하는 순간 f max = f₀(v + vo)/v = %d × (%d + %s)/%d = %s Hz' % (f0, v, fs(vs), v, fs(fmax, 1)), '(검산) 1초에 만나는 파면 수 = (v + vo)/λ, λ = v/f₀ = %s m → %s Hz' % (fs(v / f0, 4), fs((v + vs) / (v / f0), 1))],
                      core='관측자가 음원 쪽으로 움직이면 f = f₀(v + vo)/v 이다.', point='음원이 정지한 경우의 도플러 공식은 분모가 v 이다.')
        if ask == 'fmin':
            body = P(base + 'P가 측정하는 소리의 최소 진동수는?' + tl) + fig
            return mc(body, U(fmin, 'Hz', 1), wr(fmin, [f0 * v / (v + vs), fmax, f0 - vs, f0 * v / (v - vs), f0 * (v - 2 * vs) / v], 'Hz', 1), r=r, lv='중', fam='c',
                      steps=['관측자의 속력 vo = 2πR/T = %s m/s' % fs(vs), '음원에서 멀어지는 순간 f min = f₀(v - vo)/v = %d × (%d - %s)/%d = %s Hz' % (f0, v, fs(vs), v, fs(fmin, 1)), '(검산) λ = v/f₀ = %s m, (v - vo)/λ = %s Hz' % (fs(v / f0, 4), fs((v - vs) / (v / f0), 1))],
                      core='관측자가 음원에서 멀어지면 f = f₀(v - vo)/v 이다.', point='움직이는 쪽이 관측자이면 분자에 v ± vo 가 온다.')
        d = fmax - fmin
        body = P(base + 'P가 측정하는 소리의 최대 진동수와 최소 진동수의 차는?' + tl) + fig
        return mc(body, U(d, 'Hz', 1), wr(d, [d / 2, fmax - f0 + 0 if False else d * 2, f0 * vs / v, 2 * vs, f0 * 2 * vs / (v - vs)], 'Hz', 1), r=r, lv='상', fam='c',
                  steps=['vo = 2πR/T = %s m/s' % fs(vs), 'f max = f₀(v + vo)/v = %s Hz, f min = f₀(v - vo)/v = %s Hz' % (fs(fmax, 1), fs(fmin, 1)), '차 = 2f₀vo/v = 2 × %d × %s / %d = %s Hz' % (f0, fs(vs), v, fs(d, 1)), '(검산) %s - %s = %s Hz' % (fs(fmax, 1), fs(fmin, 1), fs(d, 1))],
                  core='관측자가 원운동하면 음원과의 상대 속도 성분이 ±vo 사이에서 변한다.', point='최대·최소 진동수의 차를 구한다.')
    # inv : 그래프(또는 표)의 최대·최소 진동수로부터 vs, f₀, A 를 구한다
    vs = r.choice(VS_OPTS)
    if vs >= v / 4: return None
    f0 = _f0_for(r, v, vs)
    if f0 is None: return None
    fmax = f0 * v / (v - vs); fmin = f0 * v / (v + vs)
    vs2 = v * (fmax - fmin) / (fmax + fmin)
    f02 = 2 / (1 / fmax + 1 / fmin)
    assert abs(vs2 - vs) < 1e-6 and abs(f02 - f0) < 1e-6
    T = r.choice([0.06, 0.1, 0.12, 0.2, 0.3, 0.6])
    A = vs * T / 6
    ask = r.choice(['vs', 'vs', 'f0', 'A'])
    if ask == 'A' and not cl(A, 3): return None
    fig = FIG(fig_dop_graph(f0, v, vs, T), '64%')
    base = '그림은 용수철에 연결되어 직선 위를 단진동하는 음원이 내는 소리를, 이 직선의 연장선 위 멀리 정지한 관측자가 측정한 진동수를 시간에 따라 나타낸 것이다(점선은 최댓값, 최솟값). 최대 진동수는 %s Hz, 최소 진동수는 %s Hz이고 단진동의 주기는 %s s이다. ' % (fs(fmax, 1), fs(fmin, 1), fs(T))
    tl = ' (단, 소리의 속력은 %d m/s이다.)' % v
    if ask == 'vs':
        body = P(base + '음원의 최대 속력은?' + tl) + fig
        return mc(body, U(vs, 'm/s'), wr(vs, [v * (fmax - fmin) / fmax, v * (fmax - fmin) / fmin, (fmax - fmin) / 2, v * (fmax - fmin) / (2 * (fmax + fmin)), vs * 2, vs / 2], 'm/s'), r=r, lv='상', fam='d',
                  steps=['f max = f₀v/(v - vs), f min = f₀v/(v + vs) 를 이용한다.', 'f max / f min = (v + vs)/(v - vs) = %s/%s → vs = v(f max - f min)/(f max + f min)' % (fs(fmax, 1), fs(fmin, 1)),
                         'vs = %d × (%s - %s)/(%s + %s) = %s m/s' % (v, fs(fmax, 1), fs(fmin, 1), fs(fmax, 1), fs(fmin, 1), fs(vs)), '(검산) f₀ = %d Hz 로 f₀v/(v - vs) = %s Hz' % (f0, fs(f0 * v / (v - vs), 1))],
                  core='최대·최소 진동수의 비 (v + vs)/(v - vs) 로 음원의 속력을 구한다.', point='그래프의 두 값에서 속력을 역으로 구한다.')
    if ask == 'f0':
        body = P(base + '음원이 내는 소리의 진동수 f₀는?' + tl) + fig
        return mc(body, U(f0, 'Hz'), wr(f0, [(fmax + fmin) / 2, math.sqrt(fmax * fmin), fmax - vs, fmin + vs, fmax / 2 + fmin / 2 + 10, f0 * 2], 'Hz'), r=r, lv='상', fam='d',
                  steps=['vs = v(f max - f min)/(f max + f min) = %s m/s' % fs(vs), 'f₀ = f max(v - vs)/v = %s × (%d - %s)/%d = %s Hz' % (fs(fmax, 1), v, fs(vs), v, fs(f0)), '(검산) f min(v + vs)/v = %s × (%d + %s)/%d = %s Hz' % (fs(fmin, 1), v, fs(vs), v, fs(fmin * (v + vs) / v))],
                  core='f₀ 는 최대·최소 진동수의 조화 평균 2/(1/f max + 1/f min) 이다(산술 평균이 아님).', point='속력을 구한 뒤 f₀ 를 역산한다.')
    body = P(base + '단진동의 진폭은? (단, π = 3이다.)' + ' (소리의 속력은 %d m/s이다.)' % v) + fig
    return mc(body, U(A, 'm', 3), wr(A, [vs * T, vs * T / 2, vs * T / 3, vs / T, A * 2, A / 2], 'm', 3), r=r, lv='상', fam='d',
              steps=['vs = v(f max - f min)/(f max + f min) = %s m/s' % fs(vs), 'ω = 2π/T = 6/%s = %s rad/s' % (fs(T), fs(6 / T)), '진폭 A = vs/ω = %s / %s = %s m' % (fs(vs), fs(6 / T), fs(A, 3)), '(검산) ωA = %s × %s = %s m/s = vs' % (fs(6 / T), fs(A, 3), fs(6 / T * A))],
              core='단진동의 최대 속력 vs = ωA = 2πA/T 로 진폭을 구한다.', point='도플러 → 속력 → 단진동 진폭으로 연결한다.')


# ================================================================== ph113 열기관과 일률(연료 소비)
def fig_engine(QH='Q_H', W='W', QC='Q_C', TH=None, TC=None, w=340, hh=230):
    """열기관 에너지 흐름도: 고열원 → 열기관 → 저열원, 일은 오른쪽으로."""
    f = Fig(w, hh)
    f.rect(70, 8, 150, 34, '#fbe3e0', INK, 1.6)
    f.text(145, 30, '고열원' + (' (%s)' % TH if TH else ''), 13, bold=True)
    f.arrow(145, 42, 145, 88, RD, 3)
    f.text(155, 70, QH, 13, 'start', True, RD)
    f.circ(145, 112, 26, '#fff4d6', INK, 1.8)
    f.text(145, 117, '열기관', 12.5, bold=True)
    f.arrow(171, 112, 240, 112, GN, 3)
    f.text(245, 106, W, 13, 'start', True, GN)
    f.arrow(145, 138, 145, 184, BL, 3)
    f.text(155, 166, QC, 13, 'start', True, BL)
    f.rect(70, 186, 150, 34, '#dcebfa', INK, 1.6)
    f.text(145, 208, '저열원' + (' (%s)' % TC if TC else ''), 13, bold=True)
    return f.svg()


def fig_engine2(w=330, hh=210):
    """두 열기관: 첫째 열기관의 방출열이 둘째 열기관의 입력이 된다."""
    f = Fig(w, hh)
    f.rect(40, 8, 110, 32, '#fbe3e0', INK, 1.6)
    f.text(95, 29, '고열원', 13, bold=True)
    f.arrow(95, 40, 95, 66, RD, 3)
    f.circ(95, 90, 24, '#fff4d6', INK, 1.8)
    f.text(95, 95, '기관 1', 12, bold=True)
    f.arrow(119, 90, 170, 90, GN, 3)
    f.text(174, 85, 'W₁', 13, 'start', True, GN)
    f.arrow(95, 114, 95, 142, BL, 3)
    f.circ(95, 166, 24, '#fff4d6', INK, 1.8)
    f.text(95, 171, '기관 2', 12, bold=True)
    f.arrow(119, 166, 170, 166, GN, 3)
    f.text(174, 161, 'W₂', 13, 'start', True, GN)
    f.arrow(95, 190, 95, 202, BL, 3)
    f.text(104, 202, '저열원으로 Q₂', 12, 'start', True, BL)
    f.text(104, 134, 'Q₁', 13, 'start', True, BL)
    f.text(104, 58, 'Q_H', 13, 'start', True, RD)
    return f.svg()


def kw(x):
    """W → 'x kW' 또는 'x W' 문자열."""
    return ('%s kW' % fs(x / 1000, 3)) if abs(x) >= 1000 and cl(x / 1000, 3) else ('%s W' % fs(x))


@T('ph113')
@balanced
def g113(r, k):
    form = pick(r, ['flow'] * 6 + ['fuel'] * 2 + ['mech'] * 2 + ['carnot'] * 1 + ['two'] + ['bogi'] * 2)
    if form == 'flow':
        QH = r.choice([200, 400, 500, 600, 800, 1000, 1200, 1500, 2000])
        e = r.choice([0.2, 0.25, 0.3, 0.4, 0.5, 0.6])
        W = e * QH
        if not cl(W, 1): return None
        QC = QH - W
        n = r.choice([1, 2, 5, 10, 20, 25, 50, 100])
        Pw = n * W
        assert abs(QH - W - QC) < 1e-9
        ask = r.choice(['e', 'e', 'e', 'P', 'P', 'QCd', 'W', 'W'])
        given = r.choice(['QC', 'W'])
        if ask == 'e' and given == 'W':
            given = 'QC'
        fig = FIG(fig_engine('Q_H = %s J' % fs(QH), '?' if given == 'QC' else 'W = %s J' % fs(W), 'Q_C = %s J' % fs(QC) if given == 'QC' else '?'), '52%')
        if given == 'QC':
            base = '그림은 어떤 열기관이 한 번의 순환 과정(1 사이클) 동안 고열원에서 %s J의 열을 흡수하고 저열원으로 %s J의 열을 방출하는 것을 나타낸 것이다. ' % (fs(QH), fs(QC))
        else:
            base = '그림은 어떤 열기관이 한 번의 순환 과정(1 사이클) 동안 고열원에서 %s J의 열을 흡수하여 %s J의 일을 하는 것을 나타낸 것이다. ' % (fs(QH), fs(W))
        if ask == 'e':
            body = P(base + '이 열기관의 열효율은?') + fig
            return mc(body, fs(e), wr(e, [QC / QH, W / QC, 1 - e - 0.1, e * 2, QH / W if False else 1 / e, e / 2], '', 2), r=r, lv='하', fam='a', sort='shuf',
                      steps=['제1법칙에 의해 1 사이클 동안 한 일 W = Q_H - Q_C = %s - %s = %s J' % (fs(QH), fs(QC), fs(W)), '열효율 e = W/Q_H = %s / %s = %s' % (fs(W), fs(QH), fs(e))],
                      core='열기관의 열효율 e = W/Q_H = 1 - Q_C/Q_H 이다.', point='일은 흡수한 열에서 방출한 열을 뺀 값이다.')
        if ask == 'W':
            body = P(base + '열기관이 1 사이클 동안 방출한 열은 몇 J인가?' if given == 'W' else base + '이 열기관이 1 사이클 동안 한 일은?') + fig
            ans = QC if given == 'W' else W
            return mc(body, U(ans, 'J'), wr(ans, [QH, W if given == 'W' else QC, QH + ans, QH * 0.5, ans * 2, QH - ans * 2], 'J'), r=r, lv='하', fam='a',
                      steps=['열기관은 1 사이클 후 처음 상태로 돌아오므로 ΔU = 0 이다.', 'W = Q_H - Q_C : %s = %s - %s' % (fs(W), fs(QH), fs(QC)), '답 : %s J' % fs(ans)],
                      core='순환 과정에서 ΔU = 0 이므로 W = Q_H - Q_C 이다.', point='제1법칙을 열기관에 적용한다.')
        if ask == 'QCd':
            body = P(base + '이 열기관이 매초 %d회 순환할 때 저열원으로 방출하는 열의 일률(1초당 방출하는 열)은?' % n) + fig
            return mc(body, kw(n * QC), [u for u in [kw(n * QH), kw(n * W), kw(QC), kw(n * QC * 2), kw(n * (QH + QC)), kw(n * QC / 2)] if u != kw(n * QC)], r=r, lv='중', fam='a', sort='num',
                      steps=['1 사이클당 방출열 Q_C = %s J' % fs(QC), '매초 %d회이므로 방출하는 열의 일률 = %d × %s = %s' % (n, n, fs(QC), kw(n * QC)), '(검산) 흡수 일률 %s - 출력 %s = %s' % (kw(n * QH), kw(n * W), kw(n * QH - n * W))],
                      core='단위 시간당 열량은 사이클당 열량 × 사이클 수이다.', point='사이클당 값을 일률로 바꾼다.')
        body = P(base + '이 열기관이 매초 %d회 순환할 때 열기관의 출력(일률)은?' % n) + fig
        return mc(body, kw(Pw), [u for u in [kw(n * QH), kw(n * QC), kw(W), kw(Pw * 2), kw(Pw / 2), kw(n * (QH + W))] if u != kw(Pw)], r=r, lv='중', fam='a', sort='num',
                  steps=['1 사이클당 한 일 W = Q_H - Q_C = %s J' % fs(W) if given == 'QC' else '1 사이클당 한 일 W = %s J' % fs(W), '출력 P = n·W = %d × %s = %s' % (n, fs(W), kw(Pw)), '(검산) e × (흡수 일률) = %s × %s = %s' % (fs(e), kw(n * QH), kw(e * n * QH))],
                  core='열기관의 출력 = 1 사이클의 일 × 초당 순환 횟수이다.', point='사이클당 일과 일률을 연결한다.')
    if form == 'fuel':
        Pw = r.choice([5000, 10000, 20000, 30000, 40000, 50000, 60000, 100000])
        e = r.choice([0.2, 0.25, 0.3, 0.4, 0.5])
        q = r.choice([10, 20, 40, 50]) * 1e6
        t = r.choice([10, 100, 600, 1000, 3600])
        mdot = Pw / (e * q)
        mkg = mdot * t
        QHrate = Pw / e
        QCrate = QHrate - Pw
        assert abs(QCrate - QHrate * (1 - e)) < 1e-6
        ask = r.choice(['m', 'm', 'm', 'QC', 'e'])
        qs = '%s×10%s J/kg' % (fs(q / 1e7), sup('7'))
        if ask == 'm':
            if not cl(mkg, 3) or mkg < 0.005: return None
            fig = FIG(fig_engine('Q_H', '출력 %s' % kw(Pw), 'Q_C', None, None), '52%')
            body = P('그림은 열효율이 %s인 열기관의 에너지 흐름을 나타낸 것이다. 이 열기관의 출력은 %s이며, 연료의 연소열(발열량)은 %s이다. 열기관이 %d초 동안 작동할 때 소비하는 연료의 질량은? (단, 연료가 연소하여 낸 열은 모두 고열원에서 기관으로 공급된다.)' % (fs(e), kw(Pw), qs, t)) + fig
            return mc(body, U(mkg, 'kg', 3), wr(mkg, [Pw * t / q, mkg * e, mkg * (1 - e), mkg / e if False else mkg * 2, mkg / 2, mkg * 10], 'kg', 3), r=r, lv='상', fam='b',
                      steps=['%d초 동안 한 일 W = Pt = %s × %d = %s J' % (t, fs(Pw), t, fs(Pw * t)), '흡수한 열 Q_H = W/e = %s / %s = %s J' % (fs(Pw * t), fs(e), fs(Pw * t / e)), '연료 질량 = Q_H / q = %s / %s = %s kg' % (fs(Pw * t / e), fs(q), fs(mkg, 3)),
                             '(검산) 연료 1초당 %s kg × %d초 = %s kg' % (fs(mdot, 6), t, fs(mkg, 3))],
                      core='연료가 낸 열 Q_H = e 로 나눈 일, 연료량 = Q_H/연소열 이다.', point='출력 → 일 → 흡수열 → 연료량의 순서로 구한다.')
        if ask == 'QC':
            fig = FIG(fig_engine('Q_H', '출력 %s' % kw(Pw), 'Q_C', None, None), '52%')
            body = P('그림은 열효율이 %s인 열기관의 에너지 흐름을 나타낸 것이다. 이 열기관의 출력이 %s일 때 저열원으로 방출하는 열의 일률(1초당 방출하는 열)은?' % (fs(e), kw(Pw))) + fig
            return mc(body, kw(QCrate), [u for u in [kw(QHrate), kw(Pw), kw(Pw * (1 - e)), kw(QCrate * 2), kw(QHrate + Pw), kw(QCrate / 2)] if u != kw(QCrate)], r=r, lv='중', fam='b', sort='num',
                      steps=['흡수 일률 Q_H = P/e = %s / %s = %s' % (fs(Pw), fs(e), kw(QHrate)), '방출 일률 Q_C = Q_H - P = %s - %s = %s' % (kw(QHrate), kw(Pw), kw(QCrate)), '(검산) Q_C = Q_H(1 - e) = %s × %s = %s' % (kw(QHrate), fs(1 - e), kw(QHrate * (1 - e)))],
                      core='흡수열 = 일 + 방출열 이고 e = W/Q_H 이다.', point='열효율로 흡수 일률을 먼저 구한다.')
        # e 구하기 : 연료 소비량과 출력으로
        if not cl(mkg, 3) or mkg < 0.005: return None
        fig = FIG(fig_engine('Q_H', '출력 %s' % kw(Pw), 'Q_C', None, None), '52%')
        body = P('그림과 같은 열기관이 %s의 일정한 출력으로 %d초 동안 작동하는 동안 연소열이 %s인 연료를 %s kg 소비하였다. 이 열기관의 열효율은? (단, 연료가 낸 열은 모두 기관에 공급된다.)' % (kw(Pw), t, qs, fs(mkg, 3))) + fig
        return mc(body, fs(e), wr(e, [1 - e, e / 2, e * 2, Pw * t / (mkg * q) * 2 if False else e * 1.5, e / 4, 1 - e / 2], '', 2), r=r, lv='상', fam='b', sort='shuf',
                  steps=['소비한 연료가 낸 열 Q_H = %s × %s = %s J' % (fs(mkg, 3), fs(q), fs(mkg * q)), '한 일 W = Pt = %s × %d = %s J' % (fs(Pw), t, fs(Pw * t)), 'e = W/Q_H = %s / %s = %s' % (fs(Pw * t), fs(mkg * q), fs(e)), '(검산) e = P/(ṁq) = %s' % fs(Pw / (mkg / t * q))],
                  core='열효율 e = (출력 × 시간)/(연료량 × 연소열) 이다.', point='연료의 열량과 일의 비로 열효율을 구한다.')
    if form == 'mech':
        kind = r.choice(['car', 'car', 'pump'])
        e = r.choice([0.2, 0.25, 0.3, 0.4, 0.5])
        q = r.choice([4, 5]) * 1e7
        if kind == 'car':
            Fr = r.choice([500, 800, 1000, 1200, 1500, 2000])
            vv = r.choice([10, 15, 20, 25, 30])
            Pw = Fr * vv
            km = r.choice([10, 50, 100])
            mass = Fr * km * 1000 / (e * q)
            mass2 = Pw / (e * q) * (km * 1000 / vv)
            assert abs(mass - mass2) < 1e-9
            if not cl(mass, 2) or mass < 0.02: return None
            ask = r.choice(['fuel', 'fuel', 'P'])
            qs = '%s×10%s J/kg' % (fs(q / 1e7), sup('7'))
            base = '질량이 같은 자동차가 수평 도로에서 일정한 속력 %d m/s로 달린다. 이때 자동차에 작용하는 저항력의 크기는 %d N이고, 자동차 기관의 열효율은 %s이다. ' % (vv, Fr, fs(e))
            if ask == 'P':
                body = P(base + '이 기관이 내는 출력은? (단, 일정한 속력으로 달리므로 기관의 힘과 저항력의 크기는 같다.)')
                return mc(body, kw(Pw), [u for u in [kw(Pw / e), kw(Pw * e), kw(Fr), kw(Pw * 2), kw(Pw / 2), kw(Fr / vv)] if u != kw(Pw)], r=r, lv='중', fam='c', sort='num',
                          steps=['등속 운동이므로 기관의 힘 F = 저항력 = %d N' % Fr, '출력 P = Fv = %d × %d = %s' % (Fr, vv, kw(Pw)), '(검산) 1초에 하는 일 = 힘 × 이동 거리 = %d × %d = %d J' % (Fr, vv, Pw)],
                          core='등속 운동하는 물체의 구동력은 저항력과 같고 출력은 P = Fv 이다.', point='역학의 일률 공식을 열기관 출력에 연결한다.')
            body = P(base + '연소열이 %s인 연료를 사용할 때 %d km를 달리는 동안 소비하는 연료의 질량은? (단, 연료가 낸 열은 모두 기관에 공급된다.)' % (qs, km))
            return mc(body, U(mass, 'kg', 2), wr(mass, [mass * e, mass / e * e * 2, mass * (1 - e), mass * 10, mass / 10, Fr * km * 1000 / q], 'kg', 2), r=r, lv='상', fam='c',
                      steps=['%d km 를 달리는 동안 기관이 한 일 W = Fs = %d × %d = %s J' % (km, Fr, km * 1000, fs(Fr * km * 1000)), '흡수해야 할 열 Q_H = W/e = %s / %s = %s J' % (fs(Fr * km * 1000), fs(e), fs(Fr * km * 1000 / e)), '연료 질량 = Q_H/q = %s / %s = %s kg' % (fs(Fr * km * 1000 / e), fs(q), fs(mass, 2)),
                             '(검산) 출력 %s, 연료 소비율 P/(eq) = %s kg/s, 걸린 시간 %s s → %s kg' % (kw(Pw), fs(Pw / (e * q), 8), fs(km * 1000 / vv), fs(mass2, 2))],
                      core='일 = 힘 × 거리, 연료량 = 일/(열효율 × 연소열) 이다.', point='역학적 일(Fs)과 열기관 효율을 연결한다.')
        # pump
        mw = r.choice([20, 50, 100, 200, 500])
        hh_ = r.choice([2, 5, 10, 20, 30])
        Pw = mw * G * hh_
        rate = Pw / (e * q)
        ask = r.choice(['QH', 'fuelh'])
        qs = '%s×10%s J/kg' % (fs(q / 1e7), sup('7'))
        base = '열기관으로 작동하는 양수기가 매초 %d kg의 물을 %d m 높이까지 끌어올린다(물의 운동 에너지 변화는 무시한다). 열기관의 열효율은 %s이다. ' % (mw, hh_, fs(e))
        if ask == 'QH':
            body = P(base + '이 열기관이 고열원에서 흡수하는 열의 일률(1초당 흡수하는 열)은? (단, 중력 가속도는 10 m/s²이고, 열기관의 출력은 모두 물을 끌어올리는 데 쓰인다.)')
            QHr = Pw / e
            return mc(body, kw(QHr), [u for u in [kw(Pw), kw(Pw * e), kw(QHr * 2), kw(QHr - Pw), kw(mw * hh_), kw(QHr / 2)] if u != kw(QHr)], r=r, lv='중', fam='c', sort='num',
                      steps=['1초에 물에 해 주는 일 = mgh = %d × 10 × %d = %s J → 출력 %s' % (mw, hh_, fs(Pw), kw(Pw)), '흡수 일률 Q_H = P/e = %s / %s = %s' % (fs(Pw), fs(e), kw(QHr)), '(검산) e × Q_H = %s × %s = %s' % (fs(e), kw(QHr), kw(e * QHr))],
                      core='출력 P = mgh/t, 흡수 일률 = P/e 이다.', point='위치 에너지 증가율을 출력으로 본다.')
        hours = r.choice([1, 2, 5])
        mass = rate * 3600 * hours
        if not cl(mass, 2) or mass < 0.05: return None
        body = P(base + '연소열이 %s인 연료로 이 양수기를 %d시간 작동할 때 소비하는 연료의 질량은? (단, 중력 가속도는 10 m/s²이고, 연료가 낸 열은 모두 기관에 공급된다.)' % (qs, hours))
        return mc(body, U(mass, 'kg', 2), wr(mass, [mass * e, mass / 3600, mass * (1 - e), mass * 2, mass / 2, Pw * 3600 * hours / q], 'kg', 2), r=r, lv='상', fam='c',
                  steps=['출력 P = mgh/t = %d × 10 × %d = %s W' % (mw, hh_, fs(Pw)), '흡수 일률 = P/e = %s W, 연료 소비율 = %s / %s = %s kg/s' % (fs(Pw / e), fs(Pw / e), fs(q), fs(rate, 8)), '%d시간 = %d s 동안 연료 = %s × %d = %s kg' % (hours, 3600 * hours, fs(rate, 8), 3600 * hours, fs(mass, 2)),
                         '(검산) 총 일 %s J ÷ e ÷ q = %s kg' % (fs(Pw * 3600 * hours), fs(Pw * 3600 * hours / e / q, 2))],
                  core='역학적 출력(mgh/t)과 열효율, 연소열로 연료 소비를 구한다.', point='위치 에너지 증가 → 출력 → 열 → 연료의 연결.')
    if form in ('carnot', 'bogi'):
        TH = r.choice([400, 500, 600, 800, 1000, 1200])
        TC = r.choice([200, 250, 300, 320, 400, 480])
        if TC >= TH: return None
        ec = 1 - TC / TH
        if not cl(ec, 3): return None
        QH = r.choice([200, 400, 500, 800, 1000, 2000, 5000])
        e = r.choice([0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6])
        W = e * QH
        if not cl(W, 1): return None
        QC = QH - W
        n = r.choice([1, 5, 10, 20, 50])
        if form == 'bogi':
            if e >= ec - 1e-9: return None
            fig = FIG(fig_engine('Q_H = %s J' % fs(QH), 'W = %s J' % fs(W), 'Q_C = %s J' % fs(QC), '%d K' % TH, '%d K' % TC), '52%')
            ok = e < ec - 1e-9
            tops = [
                ('이 열기관의 열효율은 %s이다.' % fs(e), '이 열기관의 열효율은 %s이다.' % fs(QC / QH), 'e = W/Q_H = %s / %s = %s 이다.' % (fs(W), fs(QH), fs(e)), 'e = W/Q_H = %s 이고 Q_C/Q_H = %s 는 방출열의 비율이다.' % (fs(e), fs(QC / QH))),
                ('이 열기관의 열효율은 같은 온도의 카르노 기관의 열효율(%s)보다 %s.' % (fs(ec, 3), '작다' if ok else '크다'), '이 열기관의 열효율은 같은 온도의 카르노 기관의 열효율(%s)보다 %s.' % (fs(ec, 3), '크다' if ok else '작다'), '카르노 효율 1 - T_C/T_H = 1 - %d/%d = %s 이고 e = %s 이므로 %s.' % (TC, TH, fs(ec, 3), fs(e), '작다' if ok else '크다'), '카르노 효율 %s 와 e = %s 를 비교하면 %s.' % (fs(ec, 3), fs(e), '작다' if ok else '크다')),
                ('이 열기관이 1 사이클 동안 방출하는 열은 %s J이다.' % fs(QC), '이 열기관이 1 사이클 동안 방출하는 열은 %s J이다.' % fs(W), 'Q_C = Q_H - W = %s J 이다.' % fs(QC), 'Q_C = Q_H - W = %s J 이고 %s J 는 한 일이다.' % (fs(QC), fs(W))),
                ('이 열기관의 열효율은 1(100 %)보다 작다.', '이 열기관은 흡수한 열을 모두 일로 바꿀 수 있다.', '열효율은 항상 1보다 작다(열역학 제2법칙).', '방출열이 반드시 존재하므로 열효율 100 %는 불가능하다.'),
                ('1 사이클 동안 기관의 내부 에너지 변화는 0이다.', '1 사이클 동안 기관의 내부 에너지는 %s J 증가한다.' % fs(W), '순환 과정에서는 처음 상태로 돌아오므로 ΔU = 0 이다.', '순환하면 내부 에너지가 처음과 같다. ΔU = 0 이다.'),
                ('매초 %d회 순환하면 이 열기관의 출력은 %s이다.' % (n, kw(n * W)), '매초 %d회 순환하면 이 열기관의 출력은 %s이다.' % (n, kw(n * QH)), 'P = nW = %d × %s = %s 이다.' % (n, fs(W), kw(n * W)), 'P = nW = %s 이며 %s 는 흡수 일률이다.' % (kw(n * W), kw(n * QH))),
            ]
            return topics_bogi(r, tops, '그림은 고열원의 온도가 %d K, 저열원의 온도가 %d K인 열기관의 에너지 흐름을 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % (TH, TC), pre=fig, fam='f', lv='중',
                               core='열기관에서 W = Q_H - Q_C, e = W/Q_H < 카르노 효율 1 - T_C/T_H 이다.', point='열역학 제1·제2법칙과 열효율, 일률을 종합한다.')
        ask = r.choice(['Pmax', 'Pmax', 'ratio', 'fuel'])
        Pin = r.choice([10000, 20000, 25000, 40000, 50000, 100000])
        if ask == 'Pmax':
            Pm = ec * Pin
            if not cl(Pm, 1): return None
            fig = FIG(fig_engine('Q_H = %s' % kw(Pin), 'P_max', 'Q_C', '%d K' % TH, '%d K' % TC), '52%')
            body = P('그림과 같이 고열원의 온도가 %d K, 저열원의 온도가 %d K인 열기관이 고열원에서 매초 %s의 열을 흡수한다. 이 열기관이 낼 수 있는 이론적인 최대 출력은?' % (TH, TC, kw(Pin))) + fig
            return mc(body, kw(Pm), [u for u in [kw(Pin * (TC / TH)), kw(Pin), kw(Pin * (1 - ec) * 0.5 + Pm * 0.5), kw(Pin * TH / (TH + TC)), kw(Pm / 2), kw(Pm * 2)] if u != kw(Pm)], r=r, lv='상', fam='d', sort='num',
                      steps=['최대 효율은 카르노 효율 e max = 1 - T_C/T_H = 1 - %d/%d = %s' % (TC, TH, fs(ec, 3)), '최대 출력 P = e max × Q_H(일률) = %s × %s = %s' % (fs(ec, 3), kw(Pin), kw(Pm)), '(검산) 방출열 Q_C = Q_H·T_C/T_H = %s, Pm = Q_H - Q_C = %s' % (kw(Pin * TC / TH), kw(Pin - Pin * TC / TH))],
                      core='열기관의 최대 효율은 카르노 효율 1 - T_C/T_H 이다.', point='온도로 최대 효율을 구한 뒤 흡수 일률에 곱한다.')
        if ask == 'ratio':
            Pout = e * Pin
            if not cl(Pout, 1): return None
            if e >= ec: return None
            fig = FIG(fig_engine('Q_H = %s' % kw(Pin), '출력 %s' % kw(Pout), 'Q_C', '%d K' % TH, '%d K' % TC), '52%')
            q_ = F(e).limit_denominator(1000) / F(ec).limit_denominator(1000)
            body = P('그림과 같이 고열원의 온도가 %d K, 저열원의 온도가 %d K인 열기관이 고열원에서 매초 %s의 열을 흡수하여 %s의 출력을 낸다. 이 열기관의 열효율은 같은 온도 조건의 카르노 기관 열효율의 몇 배인가?' % (TH, TC, kw(Pin), kw(Pout))) + fig
            qs_ = ('%d/%d배' % (q_.numerator, q_.denominator)) if q_.denominator != 1 else '%d배' % q_.numerator
            wl = []
            for c in [1 / q_, q_ * q_, F(e).limit_denominator(100), F(ec).limit_denominator(100), q_ / 2, q_ + F(1, 2), F(1, 2)]:
                c = F(c)
                s_ = ('%d/%d배' % (c.numerator, c.denominator)) if c.denominator != 1 else '%d배' % c.numerator
                if s_ != qs_ and c > 0 and s_ not in wl: wl.append(s_)
            return mc(body, qs_, wl, r=r, lv='상', fam='d', sort='shuf',
                      steps=['열효율 e = P/Q_H = %s / %s = %s' % (kw(Pout), kw(Pin), fs(e)), '카르노 효율 e_c = 1 - T_C/T_H = 1 - %d/%d = %s' % (TC, TH, fs(ec, 3)), 'e / e_c = %s / %s = %s' % (fs(e), fs(ec, 3), qs_), '(검산) 이 열기관은 e < e_c 이므로 열역학 제2법칙을 만족한다.'],
                      core='실제 열기관의 효율은 카르노 효율보다 작다.', point='열효율과 카르노 효율의 비를 계산한다.')
        # fuel : 카르노 기관이 낼 수 있는 최대 출력일 때 연료
        q = r.choice([2, 4, 5]) * 1e7
        t = r.choice([100, 1000, 3600])
        mfuel = Pin * t / q
        if not cl(mfuel, 3): return None
        Pm = ec * Pin
        if not cl(Pm, 1): return None
        Wtot = Pm * t
        fig = FIG(fig_engine('Q_H', '출력', 'Q_C', '%d K' % TH, '%d K' % TC), '52%')
        body = P('고열원의 온도가 %d K, 저열원의 온도가 %d K인 열기관이 연소열이 %s×10%s J/kg인 연료를 매초 %s kg씩 태워 얻은 열을 모두 고열원에서 공급받는다. 이 열기관이 %d초 동안 할 수 있는 일의 최댓값은?' % (TH, TC, fs(q / 1e7), sup('7'), fs(Pin / q, 6), t)) + fig
        return mc(body, U(Wtot, 'J'), wr(Wtot, [Pin * t, Pin * t * TC / TH, Wtot / 2, Wtot * 2, Pin * t * (1 - ec) / 2], 'J'), r=r, lv='상', fam='d',
                  steps=['매초 공급되는 열 = %s kg × %s J/kg = %s J' % (fs(Pin / q, 6), fs(q), fs(Pin)), '%d초 동안 공급된 열 Q_H = %s J' % (t, fs(Pin * t)), 'e max = 1 - %d/%d = %s → W max = %s × %s = %s J' % (TC, TH, fs(ec, 3), fs(ec, 3), fs(Pin * t), fs(Wtot)),
                         '(검산) 방출열 Q_C = Q_H·T_C/T_H = %s J, W = Q_H - Q_C = %s J' % (fs(Pin * t * TC / TH), fs(Pin * t - Pin * t * TC / TH))],
                  core='W max = (1 - T_C/T_H) × Q_H 이고 연료의 열이 Q_H 이다.', point='연료 소비를 열량으로 환산하고 카르노 효율을 적용한다.')
    # two : 두 열기관을 직렬로 연결
    e1 = r.choice([0.2, 0.25, 0.4, 0.5, 0.6])
    e2 = r.choice([0.2, 0.25, 0.4, 0.5])
    QH = r.choice([400, 500, 800, 1000, 2000])
    W1 = e1 * QH
    Q1 = QH - W1
    W2 = e2 * Q1
    Q2 = Q1 - W2
    etot = (W1 + W2) / QH
    assert abs(etot - (1 - (1 - e1) * (1 - e2))) < 1e-9
    if not (cl(W1, 1) and cl(W2, 1) and cl(etot, 3)): return None
    ask = r.choice(['etot', 'W2', 'Q2'])
    fig = FIG(fig_engine2(), '60%')
    base = '그림은 열기관 1이 고열원에서 한 사이클에 %s J의 열을 흡수하여 일 W₁을 하고, 방출한 열 Q₁을 모두 열기관 2가 흡수하여 일 W₂를 한 뒤 나머지 열 Q₂를 저열원으로 방출하는 것을 나타낸 것이다. 열기관 1과 2의 열효율은 각각 %s, %s이다. ' % (fs(QH), fs(e1), fs(e2))
    if ask == 'etot':
        body = P(base + '두 열기관 전체의 열효율은?') + fig
        return mc(body, fs(etot, 3), wr(etot, [e1 + e2, e1 * e2, (e1 + e2) / 2, 1 - e1 * e2, etot / 2, 1 - e1 - e2], '', 3), r=r, lv='상', fam='e', sort='shuf',
                  steps=['W₁ = e₁Q_H = %s × %s = %s J, Q₁ = Q_H - W₁ = %s J' % (fs(e1), fs(QH), fs(W1), fs(Q1)), 'W₂ = e₂Q₁ = %s × %s = %s J' % (fs(e2), fs(Q1), fs(W2)), '전체 e = (W₁ + W₂)/Q_H = (%s + %s)/%s = %s' % (fs(W1), fs(W2), fs(QH), fs(etot, 3)),
                         '(검산) 1 - (1 - e₁)(1 - e₂) = 1 - %s × %s = %s' % (fs(1 - e1), fs(1 - e2), fs(1 - (1 - e1) * (1 - e2), 3))],
                  core='열기관을 직렬 연결하면 방출열이 다음 기관의 입력이 되며 전체 효율은 1 - (1 - e₁)(1 - e₂) 이다.', point='효율을 단순히 더하거나 곱하지 않는다.')
    if ask == 'W2':
        body = P(base + '열기관 2가 한 사이클에 하는 일 W₂는?') + fig
        return mc(body, U(W2, 'J'), wr(W2, [e2 * QH, W1 * e2, e2 * Q2, Q1, W2 * 2, W2 / 2], 'J'), r=r, lv='중', fam='e',
                  steps=['W₁ = e₁Q_H = %s J → Q₁ = Q_H - W₁ = %s - %s = %s J' % (fs(W1), fs(QH), fs(W1), fs(Q1)), '열기관 2의 입력은 Q₁ 이므로 W₂ = e₂Q₁ = %s × %s = %s J' % (fs(e2), fs(Q1), fs(W2)), '(검산) Q₂ = Q₁ - W₂ = %s J, Q_H = W₁ + W₂ + Q₂ = %s J' % (fs(Q2), fs(W1 + W2 + Q2))],
                  core='첫째 기관의 방출열이 둘째 기관의 흡수열이다.', point='각 기관에 열효율을 순서대로 적용한다.')
    body = P(base + '저열원으로 방출하는 열 Q₂는?') + fig
    return mc(body, U(Q2, 'J'), wr(Q2, [Q1, QH - W2, QH * (1 - e2), QH - W1 - W2 + W1, Q2 * 2, Q2 / 2], 'J'), r=r, lv='중', fam='e',
              steps=['W₁ = %s J, Q₁ = %s J' % (fs(W1), fs(Q1)), 'W₂ = e₂Q₁ = %s J, Q₂ = Q₁ - W₂ = %s - %s = %s J' % (fs(W2), fs(Q1), fs(W2), fs(Q2)), '(검산) Q_H - (W₁ + W₂) = %s - %s = %s J' % (fs(QH), fs(W1 + W2), fs(QH - W1 - W2))],
              core='에너지 보존 : Q_H = W₁ + W₂ + Q₂ 이다.', point='두 단계의 에너지 수지를 계산한다.')
