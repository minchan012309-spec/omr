# -*- coding: utf-8 -*-
"""Ⅰ-C 등가속도 직선 운동 (ph019~ph026) 생성기."""
from phlib import *
import math

G = 10  # 중력 가속도 m/s²

import re as _re


def fix(s):
    """'이(가)' '은(는)' '을(를)' 를 앞 글자에 맞게 바꾼다."""
    return _re.sub(r'(\S)(이\(가\)|은\(는\)|을\(를\))', lambda m: m.group(1) + _pick(m.group(1), m.group(2)), s)


def _pick(w, tag):
    a, b = {'이(가)': ('이', '가'), '은(는)': ('은', '는'), '을(를)': ('을', '를')}[tag]
    c = ord(w) - 0xAC00
    return a if (0 <= c < 11172 and c % 28 != 0) else b


def PP(*t):
    return P(fix(''.join(t)))


OBJ = ['자동차', '기차', '자전거', '수레', '오토바이', '썰매', '트럭', '전동 킥보드', '버스', '열차']


def J(w, a, b):
    """받침 있으면 a, 없으면 b (은/는, 이/가, 을/를)."""
    c = ord(w[-1]) - 0xAC00
    if 0 <= c < 11172 and c % 28 != 0:
        return w + a
    return w + b


def half(x):
    return abs(x * 2 - round(x * 2)) < 1e-9


def two(x):
    return abs(x * 100 - round(x * 100)) < 1e-6


def wl(right, cands, unit, nonneg=True):
    """오답 후보 -> 단위 붙은 문자열 목록(정답과 중복 제거, 필러 자동 추가)."""
    out, seen = [], {num(round(right, 2))}
    fill = [right * 2, right / 2, right + 1, right - 1, right + 2, right - 2, right * 1.5, right + 5, right * 3, right + 10, right - 5]
    for c in list(cands) + fill:
        if c is None: continue
        c = round(c, 2)
        if nonneg and c <= 0: continue
        s = num(c)
        if s in seen: continue
        seen.add(s); out.append(s + ' ' + unit)
    return out


def ans(x, unit):
    return num(round(x, 2)) + ' ' + unit


# ---------------------------------------------------------------- 그래프 도구
def segs_of(pts):
    out = []
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        out.append(dict(t0=t0, t1=t1, v0=v0, v1=v1, a=(v1 - v0) / (t1 - t0)))
    return out


def disp_area(pts):
    return sum((s['v0'] + s['v1']) / 2 * (s['t1'] - s['t0']) for s in segs_of(pts))


def disp_kin(pts):
    d = 0
    for s in segs_of(pts):
        dt = s['t1'] - s['t0']
        d += s['v0'] * dt + 0.5 * s['a'] * dt * dt
    return d


def dist_total(pts):
    d = 0
    for s in segs_of(pts):
        dt = s['t1'] - s['t0']
        if s['v0'] * s['v1'] < 0:
            tc = abs(s['v0']) / abs(s['a'])
            d += abs(s['v0']) * tc / 2 + abs(s['v1']) * (dt - tc) / 2
        else:
            d += abs(s['v0'] + s['v1']) / 2 * dt
    return d


def v_at(pts, t):
    for s in segs_of(pts):
        if s['t0'] - 1e-9 <= t <= s['t1'] + 1e-9:
            return s['v0'] + s['a'] * (t - s['t0'])
    return None


def x_at(pts, t):
    x = 0
    for s in segs_of(pts):
        if t >= s['t1'] - 1e-9:
            dt = s['t1'] - s['t0']
        elif t > s['t0']:
            dt = t - s['t0']
        else:
            break
        x += s['v0'] * dt + 0.5 * s['a'] * dt * dt
    return x


def ticks_ok(vals, span_px, minpx):
    vs = sorted(set(vals))
    return all((b - a) * span_px >= minpx for a, b in zip(vs, vs[1:]))


def vt_fig(pts, hide=None, w=300, h=190, xl='t(s)', yl='v(m/s)', shade=True, mark=None, yhide_label='v'):
    """v-t 그래프. 꼭짓점마다 점선과 눈금 값. hide: 값을 문자(yhide_label)로 가릴 v 값. 부적합하면 None."""
    tmax = max(t for t, _ in pts)
    vmax = max(v for _, v in pts)
    vmin = min(0, min(v for _, v in pts))
    ymax = vmax * 1.22 if vmax > 0 else 1
    ymin = vmin * 1.22 if vmin < 0 else 0
    p = Plot(w, h, tmax * 1.12, ymax, ymin=ymin, ml=46, mr=18, mt=16, mb=30)
    ypx = (h - p.mt - p.mb) / (ymax - ymin)
    xpx = (w - p.ml - p.mr) / (tmax * 1.12)
    xt = sorted(set(t for t, _ in pts if t > 0))
    yt = sorted(set(v for _, v in pts if v != 0))
    if not ticks_ok(xt + [0], xpx, 17) or not ticks_ok(yt + [0], ypx, 13): return None
    yf = (lambda y: yhide_label if hide is not None and abs(y - hide) < 1e-9 else num(y))
    if shade and vmin >= 0:
        p.fill_under(pts)
    p.axes(xl, yl, xt, yt, yfmt=yf)
    for t, v in pts:
        if t > 0 or v != 0:
            p.line(p.px(t), p.py(v), p.px(t), p.py(0), GR, 1, '4 3')
            p.line(p.px(t), p.py(v), p.px(0), p.py(v), GR, 1, '4 3')
    p.pl(pts, BL, 2.6)
    if mark:
        for t, v in mark:
            p.circ(p.px(t), p.py(v), 3.4, RD, RD, 1)
    return p.svg()


def track_fig(items, w=330, h=84):
    """직선 도로 위의 점들. items: [(frac(0~1), '라벨', '속력 라벨' or None, color)]. 구간 길이 라벨은 따로."""
    f = Fig(w, h)
    y = 50
    f.line(16, y, w - 16, y, INK, 2, arrow=True)
    for x, name, sp, c in items:
        X = 30 + x * (w - 80)
        f.circ(X, y, 5, c, INK, 1.4)
        f.text(X, y + 22, name, 13.5, bold=True)
        if sp:
            f.arrow(X, y - 10, X + 34, y - 10, RD, 2)
            f.text(X + 17, y - 18, sp, 12.5, bold=True, c=RD)
    return f


# ================================================================ ph019
@T('ph019')
def kin_formula(r, k):
    """v = v0 + at, s = v0 t + ½at² 계산."""
    ob = r.choice(OBJ)
    form = r.choice(['v', 'v', 's', 's', 'a', 'rest', 'nth', 'stop', 'pq', 'avg'])
    start = lambda v0: ('정지해 있던 %s' % ob) if v0 == 0 else ('직선 도로에서 %s 속력으로 달리던 %s' % (U(v0, 'm/s'), ob))
    if form == 'v':
        v0 = r.choice([0, 0, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20]); a = r.choice([0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6]); t = r.randint(2, 12)
        v = v0 + a * t
        if not two(v): return None
        body = PP('%s이(가) 일정한 가속도 %s로 %s 동안 속력이 증가하였다. 이때 나중 속력은?' % (start(v0), U(a, 'm/s²'), U(t, 's')) if v0 else
                 '정지해 있던 %s%s 일정한 가속도 %s로 출발하여 %s 후의 속력은?' % (ob, J(ob, '이', '가')[len(ob):], U(a, 'm/s²'), U(t, 's')))
        wr = wl(v, [v0 + a, a * t, v0 * t, v0 + a * t / 2, v0 + 2 * a * t, abs(v0 - a * t)], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하', fam='a',
                  steps=['v = v₀ + at 에 v₀ = %s m/s, a = %s m/s², t = %s s 를 넣는다.' % (num(v0), num(a), num(t)), 'v = %s + %s × %s = %s m/s' % (num(v0), num(a), num(t), num(v))],
                  core='등가속도 직선 운동에서 속도는 시간에 일정하게 변한다: v = v₀ + at.', point='속도 공식에 값을 바르게 대입한다.')
    if form == 's':
        v0 = r.choice([0, 2, 3, 4, 5, 6, 8, 10, 12, 15]); a = r.choice([1, 2, 3, 4, 5, 6, 0.5, 1.5]); t = r.randint(2, 10)
        s = v0 * t + 0.5 * a * t * t
        if not two(s): return None
        assert abs(s - (v0 + (v0 + a * t)) / 2 * t) < 1e-9
        body = PP('%s이(가) 일정한 가속도 %s로 %s 동안 달렸다. 이 시간 동안 이동한 거리는?' % (start(v0), U(a, 'm/s²'), U(t, 's')))
        wr = wl(s, [v0 * t + a * t * t, v0 * t, 0.5 * a * t * t, (v0 + a * t) * t, v0 * t + 0.5 * a * t, a * t * t], 'm')
        return mc(body, ans(s, 'm'), wr, r=r, lv='중', fam='b',
                  steps=['s = v₀t + ½at² = %s × %s + ½ × %s × %s²' % (num(v0), num(t), num(a), num(t)), '= %s + %s = %s m' % (num(v0 * t), num(0.5 * a * t * t), num(s))],
                  core='등가속도 직선 운동의 변위는 s = v₀t + ½at² 이다.', point='시간의 제곱과 ½ 계수를 빠뜨리지 않는다.')
    if form == 'a':
        v0 = r.choice([0, 2, 4, 5, 6, 8, 10, 12, 20]); a = r.choice([1, 2, 3, 4, 5, 0.5, 1.5, 2.5]); t = r.randint(2, 10)
        v = v0 + a * t
        if not two(v): return None
        acc = r.random() < 0.6
        if acc:
            body = PP('%s이(가) 속력 %s로 달리다가 일정한 가속도로 가속하여 %s 후 속력이 %s가 되었다. 가속도의 크기는?' % (ob, U(v0, 'm/s'), U(t, 's'), U(v, 'm/s'))) if v0 else \
                PP('정지해 있던 %s이(가) 일정한 가속도로 출발하여 %s 후 속력이 %s가 되었다. 가속도의 크기는?' % (ob, U(t, 's'), U(v, 'm/s')))
            top, bot = v, v0
        else:
            body = PP('%s이(가) 속력 %s로 달리다가 일정한 가속도로 감속하여 %s 후 속력이 %s가 되었다. 가속도의 크기는?' % (ob, U(v, 'm/s'), U(t, 's'), U(v0, 'm/s'))) if v0 else \
                PP('%s로 달리던 %s이(가) 일정한 가속도로 감속하여 %s 후에 정지하였다. 가속도의 크기는?' % (U(v, 'm/s'), ob, U(t, 's')))
            top, bot = v, v0
        wr = wl(a, [v / t if t else None, (v + v0) / t, (v - v0) / (t + 1), (v - v0) / (2 * t), 2 * (v - v0) / t, v0 / t if v0 else None], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='하' if v0 == 0 else '중', fam='c',
                  steps=['속도 변화 Δv = |%s - %s| = %s m/s' % (num(v), num(v0), num(v - v0)), 'a = Δv / t = %s / %s = %s m/s²' % (num(v - v0), num(t), num(a))],
                  core='가속도는 단위 시간 동안의 속도 변화량 a = Δv/t 이다.', point='나중 속도에서 처음 속도를 뺀 변화량을 시간으로 나눈다.')
    if form == 'rest':
        a = r.choice([1, 2, 3, 4, 5, 6, 8]); t1 = r.randint(2, 5); t2 = t1 * r.choice([2, 3]) if r.random() < .6 else r.randint(t1 + 1, 12)
        s1 = 0.5 * a * t1 * t1; s2 = 0.5 * a * t2 * t2
        if not two(s1): return None
        assert abs(s2 - s1 * (t2 / t1) ** 2) < 1e-9
        body = PP('정지해 있던 %s이(가) 일정한 가속도로 출발하여 처음 %s 동안 %s를 이동하였다. 출발한 후 %s 동안 이동한 총 거리는? (단, 가속도는 일정하다.)' % (ob, U(t1, 's'), U(s1, 'm'), U(t2, 's')))
        wr = wl(s2, [s1 * t2 / t1, s1 * t2 / t1 * 2, a * t2 * t2, s1 * (t2 - t1), s1 * (t2 / t1) ** 2 / 2, a * t2], 'm')
        return mc(body, ans(s2, 'm'), wr, r=r, lv='상', fam='d',
                  steps=['정지 상태에서 출발하므로 s = ½at² 에서 %s = ½ × a × %s² 이므로 a = %s m/s² 이다.' % (num(s1), num(t1), num(a)), '%s 동안 이동 거리 s = ½ × %s × %s² = %s m' % (U(t2, 's')[:-2] + ' s', num(a), num(t2), num(s2)),
                         '(정지에서 출발한 거리는 시간의 제곱에 비례한다: %s × (%s/%s)² = %s m)' % (num(s1), num(t2), num(t1), num(s2))],
                  core='정지에서 출발하는 등가속도 운동에서 이동 거리는 시간의 제곱에 비례한다.', point='처음 구간의 정보로 가속도를 구한 뒤 다른 시간에 적용한다.')
    if form == 'nth':
        v0 = r.choice([0, 2, 3, 4, 5, 8, 10]); a = r.choice([2, 4, 6, 1, 3, 5, 8]); n = r.randint(3, 8)
        sn = v0 * n + 0.5 * a * n * n; sm = v0 * (n - 1) + 0.5 * a * (n - 1) ** 2
        d = sn - sm
        assert abs(d - (v0 + a * (n - 0.5))) < 1e-9
        if not two(d): return None
        body = PP('%s이(가) 일정한 가속도 %s로 직선 운동을 한다. 운동을 시작한 순간의 속력이 %s일 때, %d초째(%d초 ~ %d초) 1초 동안 이동한 거리는?' % (ob, U(a, 'm/s²'), U(v0, 'm/s'), n, n - 1, n))
        wr = wl(d, [sn, sm, v0 + a * n, v0 + a * (n - 1), a * n, v0 + a * n * n / 2, a * (n - 0.5)], 'm')
        return mc(body, ans(d, 'm'), wr, r=r, lv='상', fam='e',
                  steps=['%d초 동안 이동 거리 : %s × %d + ½ × %s × %d² = %s m' % (n, num(v0), n, num(a), n, num(sn)), '%d초 동안 이동 거리 : %s × %d + ½ × %s × %d² = %s m' % (n - 1, num(v0), n - 1, num(a), n - 1, num(sm)), '%d초째 이동 거리 = %s - %s = %s m' % (n, num(sn), num(sm), num(d))],
                  core='n초째 이동 거리는 n초 동안의 변위에서 (n-1)초 동안의 변위를 뺀 값이다.', point='구간의 이동 거리를 두 시각의 변위 차로 구한다.')
    if form == 'stop':
        a = r.choice([2, 4, 5, 2.5, 1, 3]); ts = r.randint(2, 8); v0 = a * ts
        t = ts + r.randint(2, 5)
        s = v0 * ts - 0.5 * a * ts * ts
        assert abs(s - v0 ** 2 / (2 * a)) < 1e-9
        if not two(s): return None
        body = PP('%s로 달리던 %s이(가) 브레이크를 밟아 크기가 %s인 일정한 가속도로 감속하여 정지하였다. 브레이크를 밟은 순간부터 %s 동안 이동한 거리는?' % (U(v0, 'm/s'), ob, U(a, 'm/s²'), U(t, 's')))
        wrong_s = v0 * t - 0.5 * a * t * t
        wr = wl(s, [wrong_s, v0 * t, v0 * ts, v0 * ts / 2 + 5, 0.5 * a * ts * ts * 2, s + v0], 'm')
        return mc(body, ans(s, 'm'), wr, r=r, lv='상', fam='f',
                  steps=['정지하는 데 걸리는 시간 : t = v₀/a = %s/%s = %s s (< %s s)' % (num(v0), num(a), num(ts), num(t)), '정지한 뒤에는 움직이지 않으므로 %s 동안의 거리는 %s 동안의 거리와 같다.' % (U(t, 's'), U(ts, 's')),
                         's = v₀t - ½at² = %s × %s - ½ × %s × %s² = %s m' % (num(v0), num(ts), num(a), num(ts), num(s))],
                  core='감속 운동은 정지한 이후에는 이동하지 않으므로 정지 시각까지만 계산한다.', point='정지 시각이 문제의 시간보다 짧은지 먼저 확인한다.')
    if form == 'pq':
        a = r.choice([1, 2, 3, 4, 0.5, 1.5, 2.5]); t = r.randint(2, 10); vp = r.choice([0, 2, 4, 5, 6, 8, 10]); vq = vp + a * t
        if not two(vq) or not half(vq): return None
        s = (vp + vq) / 2 * t
        assert abs(s - (vp * t + 0.5 * a * t * t)) < 1e-9
        f = track_fig([(0.0, 'P', ('%s' % U(vp, 'm/s')) if vp else '정지', '#fff'), (0.62, 'Q', U(vq, 'm/s'), '#fff')])
        f.text(30 + 0.31 * 250, 78, '%s' % U(t, 's'), 12.5, bold=True, c=BL)
        body = PP('그림은 직선 도로 위의 %s이(가) 일정한 가속도로 운동하여 점 P 에서 점 Q 까지 %s 동안 이동했을 때, P 와 Q 를 지나는 순간의 속력을 나타낸 것이다. P 에서 Q 까지의 거리는?' % (ob, U(t, 's'))) + FIG(f.svg(), '78%')
        wr = wl(s, [vq * t, vp * t, (vq - vp) * t, a * t * t, vq * t / 2 + 1, s + t], 'm')
        return mc(body, ans(s, 'm'), wr, r=r, lv='중', fam='g',
                  steps=['가속도 a = (%s - %s)/%s = %s m/s²' % (num(vq), num(vp), num(t), num(a)), 's = v₀t + ½at² = %s × %s + ½ × %s × %s² = %s m' % (num(vp), num(t), num(a), num(t), num(s)),
                         '(평균 속력 × 시간 = (%s + %s)/2 × %s = %s m 로도 같다.)' % (num(vp), num(vq), num(t), num(s))],
                  core='등가속도 직선 운동에서 이동 거리는 평균 속력 × 시간 = (v₀+v)t/2 이다.', point='그림에서 두 지점의 속력을 읽어 가속도와 거리를 구한다.')
    # avg
    v0 = r.choice([2, 4, 6, 8, 10, 12, 16]); v = v0 + r.choice([4, 6, 8, 10, 12, 14]); t = r.randint(2, 10)
    s = (v0 + v) / 2 * t
    a = (v - v0) / t
    assert abs(s - (v0 * t + 0.5 * a * t * t)) < 1e-9
    if not two(s): return None
    body = PP('%s의 속력이 일정하게 증가하여 %s 동안 %s에서 %s가 되었다. 이 시간 동안 이동한 거리는?' % (ob, U(t, 's'), U(v0, 'm/s'), U(v, 'm/s')))
    wr = wl(s, [v * t, v0 * t, (v - v0) * t, v * t / 2, s + v0, (v - v0) * t / 2 + v0], 'm')
    return mc(body, ans(s, 'm'), wr, r=r, lv='중', fam='h',
              steps=['속력이 일정하게 변하므로 평균 속력 = (%s + %s)/2 = %s m/s' % (num(v0), num(v), num((v0 + v) / 2)), '이동 거리 = 평균 속력 × 시간 = %s × %s = %s m' % (num((v0 + v) / 2), num(t), num(s))],
              core='등가속도 직선 운동의 평균 속도는 처음 속도와 나중 속도의 평균이다.', point='가속도를 구하지 않고 평균 속력으로 거리를 구한다.')


# ================================================================ ph020
def _sq(n):
    s = int(round(math.sqrt(n)))
    return s if s * s == n else None


@T('ph020')
def kin_v2(r, k):
    """v² - v0² = 2as."""
    ob = r.choice(OBJ)
    form = r.choice(['v', 'v', 'brake', 'brake', 'a', 'ratio', 'fig3', 'time', 'kmh'])
    if form == 'v':
        v0 = r.choice([0, 0, 2, 4, 5, 6, 8, 10]); a = r.choice([1, 2, 3, 4, 5, 6]); v = r.randint(v0 + 2, 30)
        s = (v * v - v0 * v0) / (2 * a)
        if not two(s) or s <= 0 or not half(s): return None
        assert abs((v0 + (v0 ** 2 + 2 * a * s) ** .5 - v0) - v) < 1e-9
        body = PP('%s이(가) 일정한 가속도 %s로 직선 도로를 %s 이동하는 동안 속력이 증가하였다. 처음 속력이 %s일 때 나중 속력은?' % (ob, U(a, 'm/s²'), U(s, 'm'), U(v0, 'm/s')) if v0 else
                 '정지해 있던 %s이(가) 일정한 가속도 %s로 출발하여 %s 이동했을 때의 속력은?' % (ob, U(a, 'm/s²'), U(s, 'm')))
        wr = wl(v, [(v0 + 2 * a * s) ** .5 if v0 else None, (v0 * v0 + a * s) ** .5, v0 + 2 * a * s, 2 * a * s, a * s, math.sqrt(2 * a * s) + 0.0 if v0 else None, v0 + a * s], 'm/s')
        wr = [w for w in wr if True]
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하' if v0 == 0 else '중', fam='a',
                  steps=['시간이 주어지지 않았으므로 v² - v₀² = 2as 를 쓴다.', 'v² = %s² + 2 × %s × %s = %s' % (num(v0), num(a), num(s), num(v * v)), 'v = %s m/s' % num(v)],
                  core='시간 정보가 없을 때는 v² - v₀² = 2as 로 속력, 가속도, 변위를 연결한다.', point='시간 없이 속력과 거리만으로 속력을 구한다.')
    if form == 'brake':
        a = r.choice([2, 2.5, 4, 5, 6, 8]); v0 = r.choice([10, 12, 15, 16, 20, 24, 25, 30])
        s = v0 * v0 / (2 * a)
        if not two(s): return None
        body = PP('%s로 달리던 %s이(가) 브레이크를 밟아 크기가 %s로 일정한 가속도로 감속하여 정지하였다. 브레이크를 밟은 순간부터 정지할 때까지 이동한 거리(제동 거리)는?' % (U(v0, 'm/s'), ob, U(a, 'm/s²')))
        t = v0 / a
        assert abs(s - (v0 * t - 0.5 * a * t * t)) < 1e-9
        wr = wl(s, [v0 * v0 / a, v0 * v0 / (4 * a), v0 * t, v0 / a, v0 * v0 / 2, s * 2, v0 * v0 / (2 * a) / 2], 'm')
        return mc(body, ans(s, 'm'), wr, r=r, lv='하', fam='b',
                  steps=['정지하면 나중 속력 v = 0 이므로 0 - v₀² = 2(-a)s 이다.', 's = v₀² / 2a = %s² / (2 × %s) = %s m' % (num(v0), num(a), num(s))],
                  core='제동 거리는 s = v₀²/2a 로 처음 속력의 제곱에 비례한다.', point='나중 속력이 0인 감속 운동에 v²-v₀²=2as 를 적용한다.')
    if form == 'a':
        v0 = r.choice([4, 6, 8, 10, 12, 16, 20]); v = r.choice([0, 0, 2, 4, 6, 8]);
        if v >= v0: return None
        s = r.choice([10, 12, 16, 20, 24, 30, 36, 40, 50, 60])
        a = (v0 * v0 - v * v) / (2 * s)
        if not two(a) or a <= 0: return None
        body = PP('직선 도로에서 %s로 달리던 %s이(가) 일정한 가속도로 감속하여 %s를 이동하는 동안 속력이 %s로 줄었다. 가속도의 크기는?' % (U(v0, 'm/s'), ob, U(s, 'm'), U(v, 'm/s')) if v else
                 '직선 도로에서 %s로 달리던 %s이(가) 일정한 가속도로 감속하여 %s를 이동한 후 정지하였다. 가속도의 크기는?' % (U(v0, 'm/s'), ob, U(s, 'm')))
        wr = wl(a, [(v0 * v0 - v * v) / s, (v0 - v) / s, (v0 * v0 + v * v) / (2 * s), (v0 * v0 - v * v) / (4 * s), v0 * v0 / s, (v0 - v) ** 2 / (2 * s)], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='중', fam='c',
                  steps=['v² - v₀² = 2as 에서 a = (v² - v₀²)/2s 이다.', 'a = (%s² - %s²)/(2 × %s) = %s m/s²' % (num(v), num(v0), num(s), num(-a)), '가속도의 크기는 %s m/s² 이다.' % num(a)],
                  core='감속 운동의 가속도는 속도 변화의 방향과 반대(부호가 -)이며 크기는 (v₀²-v²)/2s 이다.', point='부호에 유의하여 가속도의 크기를 구한다.')
    if form == 'ratio':
        a = r.choice([2, 4, 5]); v1 = r.choice([5, 10, 15, 20]); n = r.choice([2, 3, 0.5, 1.5, 4])
        v2 = v1 * n
        s1 = v1 * v1 / (2 * a); s2 = v2 * v2 / (2 * a)
        if not two(s1) or not two(s2) or not two(v2): return None
        assert abs(s2 / s1 - n * n) < 1e-9
        body = PP('같은 도로에서 브레이크를 밟아 일정한 크기의 가속도로 감속하는 %s이(가) %s로 달릴 때의 제동 거리가 %s이다. 브레이크를 밟을 때의 속력이 %s라면 제동 거리는? (단, 감속하는 가속도의 크기는 같다.)' % (ob, U(v1, 'm/s'), U(s1, 'm'), U(v2, 'm/s')))
        wr = wl(s2, [s1 * n, s1 * n * 2, s1 * math.sqrt(n), s1 / n, s1 / (n * n), s1 * (n + 1)], 'm')
        return mc(body, ans(s2, 'm'), wr, r=r, lv='중', fam='d',
                  steps=['v² = 2as 에서 가속도가 같으면 제동 거리는 처음 속력의 제곱에 비례한다.', '속력이 %s배이므로 제동 거리는 %s배 : %s × %s = %s m' % (num(n), num(n * n), num(s1), num(n * n), num(s2))],
                  core='제동 거리는 속력의 제곱에 비례한다(같은 크기의 가속도일 때).', point='속력이 n배이면 제동 거리는 n²배가 된다.')
    if form == 'fig3':
        a = r.choice([1, 2, 3, 4]); vp = r.choice([0, 2, 4, 6, 8])
        cand = [(vq, vr) for vq in range(vp + 2, 20) for vr in range(vq + 2, 30)
                if (vq * vq - vp * vp) % (2 * a) == 0 and (vr * vr - vq * vq) % (2 * a) == 0 and 3 <= (vq * vq - vp * vp) // (2 * a) <= 60 and 3 <= (vr * vr - vq * vq) // (2 * a) <= 90]
        if not cand: return None
        vq, vr = r.choice(cand)
        L1 = (vq * vq - vp * vp) // (2 * a); L2 = (vr * vr - vq * vq) // (2 * a)
        assert abs(vr * vr - (vp * vp + 2 * a * (L1 + L2))) < 1e-9
        f = Fig(340, 86)
        f.line(16, 46, 326, 46, INK, 2, arrow=True)
        xs = [34, 150, 290]
        for x, nm in zip(xs, 'PQR'):
            f.circ(x, 46, 5, '#fff', INK, 1.4); f.text(x, 68, nm, 13.5, bold=True)
        f.text(xs[0], 26, ('P: %s' % U(vp, 'm/s')) if vp else 'P: 정지', 12.5, bold=True, c=RD)
        f.text((xs[0] + xs[1]) / 2, 82, '%s m' % L1, 12.5, bold=True, c=BL)
        f.text((xs[1] + xs[2]) / 2, 82, '%s m' % L2, 12.5, bold=True, c=BL)
        f.text(xs[1], 26, 'Q: %s' % U(vq, 'm/s'), 12.5, bold=True, c=RD)
        body = PP('그림과 같이 직선 도로 위의 %s이(가) 일정한 가속도로 운동하여 점 P, Q, R 를 차례로 지난다. P 와 Q 에서의 속력은 각각 %s, %s이고 PQ 사이의 거리는 %s m, QR 사이의 거리는 %s m 이다. R 에서의 속력은?' % (ob, U(vp, 'm/s') if vp else '0', U(vq, 'm/s'), L1, L2)) + FIG(f.svg(), '78%')
        wr = wl(vr, [vq + (vq - vp) * L2 / L1, vq + (vq - vp), vq * L2 / L1 + vq, math.sqrt(vq * vq + 2 * a * L2) + 1, (vq * vq + a * L2) ** .5, vp + (vq - vp) * (L1 + L2) / L1], 'm/s')
        return mc(body, ans(vr, 'm/s'), wr, r=r, lv='상', fam='e',
                  steps=['P→Q : vQ² - vP² = 2a·PQ 에서 %s² - %s² = 2a × %s 이므로 a = %s m/s²' % (num(vq), num(vp), num(L1), num(a)), 'Q→R : vR² = vQ² + 2a·QR = %s² + 2 × %s × %s = %s' % (num(vq), num(a), num(L2), num(vr * vr)), 'vR = %s m/s' % num(vr)],
                  core='등가속도 운동에서는 구간마다 v²-v₀²=2as 를 적용하여 가속도를 구하고 다음 구간에 쓸 수 있다.', point='앞 구간에서 가속도를 구한 뒤 뒤 구간에 적용한다.')
    if form == 'time':
        v0 = r.choice([2, 4, 6, 8, 10, 12]); a = r.choice([1, 2, 3, 4]); t = r.randint(2, 10)
        v = v0 + a * t; s = (v * v - v0 * v0) / (2 * a)
        if not two(s): return None
        assert abs(t - 2 * s / (v0 + v)) < 1e-9
        body = PP('%s이(가) 일정한 가속도로 직선 도로를 달리면서 %s를 이동하는 동안 속력이 %s에서 %s로 증가하였다. 이 거리를 이동하는 데 걸린 시간은?' % (ob, U(s, 'm'), U(v0, 'm/s'), U(v, 'm/s')))
        wr = wl(t, [s / v, s / v0, s / ((v - v0)), 2 * s / v, s / (v0 + v), (v - v0), s / ((v + v0) / 4)], 's')
        return mc(body, ans(t, 's'), wr, r=r, lv='상', fam='f',
                  steps=['평균 속력 = (%s + %s)/2 = %s m/s' % (num(v0), num(v), num((v0 + v) / 2)), 't = s / 평균 속력 = %s / %s = %s s' % (num(s), num((v0 + v) / 2), num(t)),
                         '(a = (v²-v₀²)/2s = %s m/s², t = (v-v₀)/a = %s s 로 확인)' % (num(a), num(t))],
                  core='평균 속력 = (v₀+v)/2 이므로 s = (v₀+v)t/2 에서 시간을 구할 수 있다.', point='가속도가 주어지지 않아도 속력과 거리로 시간을 구한다.')
    # kmh
    kmh = r.choice([36, 54, 72, 90, 108]); v0 = kmh / 3.6; a = r.choice([2, 2.5, 4, 5])
    s = v0 * v0 / (2 * a)
    if not two(s): return None
    body = PP('시속 %s km로 달리던 %s이(가) 브레이크를 밟아 크기가 %s로 일정하게 감속하여 정지하였다. 제동 거리는? (단, 1 km/h = %s m/s 로 계산한다.)' % (kmh, ob, U(a, 'm/s²'), '1/3.6'))
    wr = wl(s, [kmh * kmh / (2 * a), kmh * kmh / (2 * a) / 3.6, v0 * v0 / a, v0 / a, s / 2, s * 3.6, kmh / (2 * a)], 'm')
    return mc(body, ans(s, 'm'), wr, r=r, lv='중', fam='g',
              steps=['속력 단위 변환 : %s km/h = %s m/s' % (kmh, num(v0)), 's = v₀²/2a = %s² / (2 × %s) = %s m' % (num(v0), num(a), num(s))],
              core='km/h 를 m/s 로 바꿀 때는 3.6 으로 나눈다.', point='단위를 SI 로 환산한 뒤 공식에 대입한다.')


# ================================================================ ph021 (v-t 그래프: 가속도와 변위)
def rand_prof(r, kind):
    """v-t 꼭짓점 목록을 만든다(기울기가 0.5의 배수가 되도록)."""
    if kind == 'trap':
        t1 = r.randint(1, 5); t2 = t1 + r.randint(1, 6); t3 = t2 + r.randint(1, 4)
        v = r.choice([2, 4, 5, 6, 8, 10, 12, 15, 16, 20, 24, 30])
        if not (half(v / t1) and half(v / (t3 - t2))): return None
        return [(0, 0), (t1, v), (t2, v), (t3, 0)]
    if kind == 'tri':
        t1 = r.randint(1, 6); t2 = t1 + r.randint(1, 6)
        v = r.choice([2, 4, 5, 6, 8, 10, 12, 15, 16, 20, 24])
        if not (half(v / t1) and half(v / (t2 - t1))): return None
        return [(0, 0), (t1, v), (t2, 0)]
    if kind == 'init':
        v0 = r.choice([2, 4, 5, 6, 8, 10]); t1 = r.randint(1, 5); t2 = t1 + r.randint(1, 5)
        v1 = r.choice([4, 6, 8, 10, 12, 14, 16, 20]); v2 = r.choice([0, 2, 4, 6, 8, 12, 16])
        if v1 == v0 or v2 == v1 or not half((v1 - v0) / t1) or not half((v2 - v1) / (t2 - t1)): return None
        return [(0, v0), (t1, v1), (t2, v2)]
    if kind == 'rev':
        v0 = r.choice([4, 6, 8, 10, 12, 16, 20]); tc = r.randint(1, 6); a = v0 / tc
        if not half(a): return None
        t1 = tc + r.randint(1, 6); v1 = v0 - a * t1
        if not two(v1): return None
        return [(0, v0), (t1, v1)]
    if kind == 'rev2':
        v0 = r.choice([4, 6, 8, 10, 12]); tc = r.randint(1, 4); a = v0 / tc
        if not half(a): return None
        t1 = tc + r.randint(1, 4); v1 = v0 - a * t1
        t2 = t1 + r.randint(1, 4)
        if not two(v1): return None
        return [(0, v0), (t1, v1), (t2, v1)]


def seg_name(s):
    return '%s초 ~ %s초' % (num(s['t0']), num(s['t1']))


@T('ph021')
def vt_calc(r, k):
    """v-t 그래프에서 가속도와 변위."""
    ob = r.choice(['물체', '자동차', '수레', '기차', '전동차'])
    form = r.choice(['slope', 'slope', 'slope', 'area', 'area', 'avg', 'vat', 'vat', 'unk', 'rev', 'ret', 'ret'])
    if form == 'slope':
        pts = rand_prof(r, r.choice(['trap', 'tri', 'init']))
        if not pts: return None
        sg = segs_of(pts); s = r.choice([x for x in sg if abs(x['a']) > 0] or sg)
        fig = vt_fig(pts)
        if not fig: return None
        a = abs(s['a'])
        sign = '증가' if s['a'] > 0 else '감소'
        body = PP('그림은 직선 도로 위의 %s의 속력을 시간에 따라 나타낸 것이다. %s 동안 %s의 가속도의 크기는?' % (ob, seg_name(s), ob)) + FIG(fig, '66%')
        wr = wl(a, [s['v1'], s['v1'] - s['v0'] if s['v1'] != s['v0'] else None, s['v1'] / s['t1'], (s['v0'] + s['v1']) / 2, [abs(x['a']) for x in sg if abs(x['a']) != a][0] if [x for x in sg if abs(x['a']) != a] else None,
                     (s['v1'] - s['v0']) * (s['t1'] - s['t0'])], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='하', fam='a',
                  steps=['v-t 그래프의 기울기가 가속도이다.', '%s 동안 속력이 %s m/s 에서 %s m/s 로 %s하였다.' % (seg_name(s), num(s['v0']), num(s['v1']), sign),
                         'a = Δv/Δt = (%s - %s)/(%s - %s) = %s m/s², 크기는 %s m/s² 이다.' % (num(s['v1']), num(s['v0']), num(s['t1']), num(s['t0']), num(s['a']), num(a))],
                  core='v-t 그래프에서 기울기는 가속도이다.', point='구간의 속도 변화를 시간 변화로 나눈다.')
    if form in ('area', 'avg'):
        pts = rand_prof(r, r.choice(['trap', 'tri', 'init', 'trap']))
        if not pts: return None
        fig = vt_fig(pts)
        if not fig: return None
        T_ = pts[-1][0]
        S = disp_area(pts); assert abs(S - disp_kin(pts)) < 1e-9
        if not two(S): return None
        if form == 'area':
            body = PP('그림은 직선 도로 위의 %s의 속력을 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 %s이(가) 이동한 거리는?' % (ob, num(T_), ob)) + FIG(fig, '66%')
            vm = max(v for _, v in pts)
            wr = wl(S, [vm * T_, vm * T_ / 2, sum(abs(x['a']) for x in segs_of(pts)), S / 2, S + vm, pts[1][1] * pts[1][0], S * 2], 'm')
            return mc(body, ans(S, 'm'), wr, r=r, lv='중', fam='b',
                      steps=['v-t 그래프와 시간 축 사이의 넓이가 이동 거리(변위)이다.'] + ['%s : %s × (%s + %s) × %s = %s m' % (seg_name(x), '½', num(x['v0']), num(x['v1']), num(x['t1'] - x['t0']), num((x['v0'] + x['v1']) / 2 * (x['t1'] - x['t0']))) for x in segs_of(pts)] + ['합계 = %s m' % num(S)],
                      core='v-t 그래프 아래의 넓이는 변위이다.', point='구간을 삼각형·사다리꼴로 나누어 넓이를 합한다.')
        avg = S / T_
        if not two(avg): return None
        body = PP('그림은 직선 도로 위의 %s의 속력을 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 %s의 평균 속력은?' % (ob, num(T_), ob)) + FIG(fig, '66%')
        vm = max(v for _, v in pts)
        wr = wl(avg, [vm / 2, vm, (pts[0][1] + pts[-1][1]) / 2 if pts[0][1] + pts[-1][1] else None, S / (T_ - pts[1][0]) if T_ > pts[1][0] else None, S, avg * 2], 'm/s')
        return mc(body, ans(avg, 'm/s'), wr, r=r, lv='중', fam='c',
                  steps=['0 ~ %s초 동안의 이동 거리(그래프 넓이) = %s m' % (num(T_), num(S)), '평균 속력 = 이동 거리 / 걸린 시간 = %s / %s = %s m/s' % (num(S), num(T_), num(avg))],
                  core='평균 속력은 전체 이동 거리를 걸린 시간으로 나눈 값이다.', point='그래프 넓이로 거리를 구한 뒤 시간으로 나눈다.')
    if form == 'vat':
        pts = rand_prof(r, r.choice(['init', 'trap', 'tri']))
        if not pts: return None
        fig = vt_fig(pts)
        if not fig: return None
        sg = segs_of(pts); s = r.choice(sg)
        if abs(s['a']) == 0: return None
        tt = (s['t0'] + s['t1']) / 2
        if not half(tt) or tt in (s['t0'], s['t1']): return None
        v = v_at(pts, tt)
        if not two(v): return None
        assert abs(v - (s['v0'] + s['a'] * (tt - s['t0']))) < 1e-9
        body = PP('그림은 직선 도로 위의 %s의 속력을 시간에 따라 나타낸 것이다. %s초일 때 %s의 속력은?' % (ob, num(tt), ob)) + FIG(fig, '66%')
        wr = wl(v, [s['v0'], s['v1'], (s['v0'] + s['v1']) / 2 + 1, s['a'] * tt, s['a'] * (tt - s['t0']), v + s['a']], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='중', fam='d',
                  steps=['%s 에서 가속도 a = (%s - %s)/(%s - %s) = %s m/s²' % (seg_name(s), num(s['v1']), num(s['v0']), num(s['t1']), num(s['t0']), num(s['a'])),
                         'v = v₀ + a(t - t₀) = %s + %s × (%s - %s) = %s m/s' % (num(s['v0']), num(s['a']), num(tt), num(s['t0']), num(v))],
                  core='직선 구간에서는 기울기를 이용해 임의의 시각의 속도를 구할 수 있다.', point='기울기(가속도)와 구간 시작값으로 중간 시각의 속도를 구한다.')
    if form == 'unk':
        kind = r.choice(['trap', 'tri'])
        base = rand_prof(r, kind)
        if not base: return None
        # 속력 값을 가려서 변위로부터 구하기
        v = base[1][1]
        K = disp_area([(t, (vv / v)) for t, vv in base])
        v_new = r.choice([4, 6, 8, 10, 12, 16, 20])
        pts = [(t, vv / v * v_new) for t, vv in base]
        S = v_new * K
        if not two(S) or not half(S): return None
        fig = vt_fig(pts, hide=v_new)
        if not fig: return None
        assert abs(disp_area(pts) - S) < 1e-9
        body = PP('그림은 직선 도로 위의 %s의 속력을 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 %s이(가) 이동한 거리가 %s일 때, v 는?' % (ob, num(pts[-1][0]), ob, U(S, 'm'))) + FIG(fig, '66%')
        wr = wl(v_new, [S / pts[-1][0], 2 * S / pts[-1][0], S / K / 2, S / (pts[-1][0] - pts[1][0]), S / pts[1][0], S / (K + 1)], 'm/s')
        return mc(body, ans(v_new, 'm/s'), wr, r=r, lv='상', fam='e',
                  steps=['그래프의 넓이가 이동 거리 %s m 이다.' % num(S), '넓이를 v 로 나타내면 %s × v 이다(그래프의 모양과 시간 값으로 계산).' % num(K), '%s × v = %s 이므로 v = %s m/s' % (num(K), num(S), num(v_new))],
                  core='v-t 그래프의 넓이 = 변위 를 이용하면 그래프에서 모르는 속력을 구할 수 있다.', point='넓이를 모르는 값 v 에 대한 식으로 나타내 푼다.')
    if form == 'rev':
        pts = rand_prof(r, r.choice(['rev', 'rev2']))
        if not pts: return None
        fig = vt_fig(pts, shade=False)
        if not fig: return None
        T_ = pts[-1][0]
        S = disp_area(pts); D = dist_total(pts)
        assert abs(S - disp_kin(pts)) < 1e-9 and D > abs(S)
        if not two(S) or not two(D): return None
        which = r.choice(['disp', 'dist'])
        body = PP('그림은 직선 도로를 따라 운동하는 %s의 속도를 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 %s이(가) 이동한 거리(경로의 길이)는? (단, 처음 운동 방향을 +방향으로 한다.)' % (ob, num(T_), ob) if which == 'dist' else
                  '그림은 직선 도로를 따라 운동하는 %s의 속도를 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 %s의 변위의 크기는? (단, 처음 운동 방향을 +방향으로 한다.)' % (ob, num(T_), ob)) + FIG(fig, '66%')
        tc = pts[0][1] / (-segs_of(pts)[0]['a'])
        pos = pts[0][1] * tc / 2
        right = D if which == 'dist' else abs(S)
        other = abs(S) if which == 'dist' else D
        wr = wl(right, [other, pos, abs(S) + pos, D + pos, pts[0][1] * T_ / 2, abs(pts[-1][1]) * (T_ - tc) / 2], 'm')
        return mc(body, ans(right, 'm'), wr, r=r, lv='상', fam='f',
                  steps=['속도가 0이 되는 시각 t = %s초 이후에는 운동 방향이 반대(-)이다.' % num(tc), '+방향 이동 거리(넓이) = %s m, -방향 이동 거리(넓이) = %s m' % (num(pos), num(D - pos)),
                         ('경로의 길이 = %s + %s = %s m' % (num(pos), num(D - pos), num(D))) if which == 'dist' else ('변위 = %s - %s = %s m, 크기 %s m' % (num(pos), num(D - pos), num(S), num(abs(S))))],
                  core='v-t 그래프에서 시간 축 아래의 넓이는 반대 방향의 이동이다. 변위는 부호를 포함해 합하고, 이동 거리는 절댓값을 합한다.', point='변위와 이동 거리(경로의 길이)를 구분한다.')
    # ret : 출발점으로 되돌아오는 시각
    v0 = r.choice([4, 6, 8, 10, 12, 16, 20]); tc = r.randint(1, 6)
    a = v0 / tc
    if not half(a): return None
    pts = [(0, v0), (2 * tc, -v0)]
    fig = vt_fig(pts, shade=False)
    if not fig: return None
    assert abs(disp_area(pts)) < 1e-9
    body = PP('그림은 직선 도로를 따라 운동하는 %s의 속도를 시간에 따라 나타낸 것이다. %s이(가) 출발 지점으로 되돌아오는 순간은 출발 후 몇 초일 때인가? (단, 처음 운동 방향을 +방향으로 한다.)' % (ob, ob)) + FIG(fig, '66%')
    right = 2 * tc
    wr = wl(right, [tc, tc / 2, tc + 1, 2 * tc - 1, v0 / 2, 3 * tc], 's')
    return mc(body, ans(right, 's'), wr, r=r, lv='중', fam='g',
              steps=['속도가 +%s m/s 에서 -%s m/s 로 일정하게 변하므로 기울기 a = %s m/s²' % (num(v0), num(v0), num(-a)), '속도가 0이 되는 시각은 %s초이다.' % num(tc),
                     '넓이의 합이 0이 되려면 (+넓이) = (-넓이) 이어야 하므로 0 이후 같은 시간이 더 필요하다 : %s초' % num(2 * tc)],
              core='출발점으로 돌아오면 변위가 0이므로 v-t 그래프의 부호를 고려한 넓이의 합이 0이다.', point='+ 넓이와 - 넓이가 같아지는 시각을 찾는다.')
