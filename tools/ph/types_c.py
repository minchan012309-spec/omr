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
    fill = [right * 2, right / 2, right * 1.5, right + 10, right - 5, right + 5, right * 3, right + 3, right - 3, right + 1, right - 1, right + 2, right - 2]
    for c in list(cands) + fill:
        if c is None: continue
        c = round(c, 2)
        if nonneg and c <= 0: continue
        if abs(c * 10 - round(c * 10)) > 1e-6 and abs(right * 10 - round(right * 10)) < 1e-6 and len(out) >= 3 and c in fill: continue
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


# ================================================================ ph022 (v-t 그래프 해석 <보기>)
VT_CONCEPT = [
    ('v-t 그래프에서 그래프의 기울기는 물체의 가속도를 나타낸다.', True, 'v-t 그래프의 기울기 Δv/Δt 가 가속도이다.', 'slope'),
    ('v-t 그래프와 시간 축 사이의 넓이는 그 시간 동안의 변위를 나타낸다.', True, '속도를 시간에 대해 합한 값이 변위이므로 그래프 넓이가 변위이다.', 'area'),
    ('v-t 그래프가 시간 축과 나란한 직선이면 물체는 정지해 있다.', False, '시간 축에 나란한 직선은 속도가 일정한(등속) 운동이다. 정지는 속도가 0인 경우뿐이다.', 'flat'),
    ('속도가 일정한 직선 운동의 v-t 그래프는 시간 축에 나란한 직선이다.', True, '속도가 변하지 않으므로 기울기가 0이다.', 'flat'),
    ('v-t 그래프가 원점을 지나는 직선이면 물체는 등속 직선 운동을 한다.', False, '원점을 지나는 기울어진 직선은 정지에서 출발해 속도가 일정하게 변하는 등가속도 운동이다.', 'origin'),
    ('속도가 시간에 따라 일정하게 증가하는 운동의 v-t 그래프는 기울어진 직선이다.', True, '가속도가 일정하면 v-t 그래프는 직선이다.', 'line'),
    ('v-t 그래프에서 속도가 음(-)의 값이면 속력은 감소하고 있다.', False, '속도의 부호는 운동 방향을 나타낼 뿐이며, 속력은 속도의 절댓값이다.', 'sign'),
    ('v-t 그래프가 시간 축과 만나는 순간 물체의 순간 속도는 0이다.', True, '시간 축 위의 점은 v = 0 이다.', 'zero'),
    ('v-t 그래프의 기울기가 음(-)이면 속력은 항상 감소한다.', False, '속도가 음(-)인 구간에서 기울기가 음이면 속력은 오히려 증가한다.', 'slopeneg'),
    ('v-t 그래프에서 속도가 +에서 -로 바뀌는 순간 물체의 운동 방향이 바뀐다.', True, '속도의 부호가 바뀌면 운동 방향이 반대가 된다.', 'turn'),
    ('v-t 그래프에서 시간 축 아래쪽의 넓이는 처음 방향과 반대 방향으로 이동한 거리를 나타낸다.', True, '속도가 음(-)이면 반대 방향으로 이동한다.', 'below'),
    ('이동 거리는 v-t 그래프의 위쪽 넓이에서 아래쪽 넓이를 뺀 값이다.', False, '위쪽 넓이에서 아래쪽 넓이를 뺀 값은 변위이다. 이동 거리는 두 넓이를 더한 값이다.', 'dist'),
    ('등가속도 직선 운동에서 평균 속도는 처음 속도와 나중 속도의 평균이다.', True, '속도가 일정하게 변하므로 평균 속도는 (v₀+v)/2 이다.', 'avg'),
    ('v-t 그래프에서 기울기의 절댓값이 클수록 가속도의 크기는 작다.', False, '기울기의 절댓값이 클수록 단위 시간당 속도 변화가 크므로 가속도의 크기가 크다.', 'slopebig'),
    ('두 물체의 v-t 그래프가 교차하는 순간 두 물체의 속도는 서로 같다.', True, '교차점에서는 같은 시각에 속도 값이 같다.', 'cross'),
    ('두 물체의 v-t 그래프가 교차하는 순간 두 물체는 같은 위치에 있다.', False, '교차점은 속도가 같은 순간일 뿐 위치가 같다는 뜻이 아니다. 위치는 그래프 넓이로 비교한다.', 'cross'),
    ('속도와 가속도의 방향이 같으면 물체의 속력은 증가한다.', True, '가속도가 속도와 같은 방향이면 속력이 커진다.', 'same'),
    ('가속도가 0이면 물체의 속도도 항상 0이다.', False, '가속도가 0이면 속도가 변하지 않을 뿐, 등속 운동을 할 수 있다.', 'a0'),
    ('속력이 감소하는 운동에서 가속도는 항상 음(-)의 값이다.', False, '운동 방향을 -로 잡으면 속력이 감소하는 운동의 가속도는 +이다. 가속도의 부호는 기준 방향에 따라 달라진다.', 'sign2'),
    ('출발점으로 되돌아온 물체의 변위는 0이지만 이동 거리는 0이 아니다.', True, '변위는 처음과 나중 위치의 차이고, 이동 거리는 실제 이동한 경로의 길이이다.', 'dist'),
    ('v-t 그래프에서 같은 시간 동안 이동한 거리는 그래프의 기울기에 비례한다.', False, '이동 거리는 그래프의 넓이로 구하며, 기울기는 가속도와 관련된다.', 'area'),
    ('v-t 그래프가 위로 볼록한 곡선이면 가속도가 일정한 운동이다.', False, '가속도가 일정하면 그래프는 직선이다. 곡선은 가속도가 변하는 운동이다.', 'line'),
]


def vt_two_fig(A, B, T_, w=300, h=190):
    vmax = max(A[0][1], A[1][1], B[0][1], B[1][1])
    p = Plot(w, h, T_ * 1.12, vmax * 1.2, ml=46, mr=18, mt=16, mb=30)
    ypx = (h - p.mt - p.mb) / (vmax * 1.2)
    yt = sorted(set([A[0][1], A[1][1], B[0][1], B[1][1]]) - {0})
    if not ticks_ok(yt + [0], ypx, 13): return None
    xt = list(range(1, int(T_) + 1))
    p.axes('t(s)', 'v(m/s)', xt, yt, grid=False)
    for t in xt:
        p.line(p.px(t), p.py(0), p.px(t), p.py(0) - 3, INK, 1)
    p.pl(A, BL, 2.6); p.pl(B, RD, 2.6)
    p.text(p.px(T_) + 3, p.py(A[1][1]) + (-6 if A[1][1] >= B[1][1] else 14), 'A', 14, 'start', True, BL, True)
    p.text(p.px(T_) + 3, p.py(B[1][1]) + (-6 if B[1][1] > A[1][1] else 14), 'B', 14, 'start', True, RD, True)
    return p.svg()


@T('ph022')
def vt_bogi(r, k):
    """v-t 그래프 해석 <보기>."""
    form = r.choice(['one', 'one', 'one', 'one', 'concept', 'two', 'two'])
    if form == 'concept':
        sel = r.sample(VT_CONCEPT, 3)
        if len({s[3] for s in sel}) < 3: return None
        return bogi('v-t 그래프에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', [(s[0], s[1], s[2]) for s in sel], r=r, ask='', lv='하', fam='b',
                    core='v-t 그래프의 기울기는 가속도, 넓이는 변위이며, 시간 축과 만나는 점은 속도가 0인 순간이다.', point='v-t 그래프의 기본 해석 규칙을 정확히 안다.')
    if form == 'two':
        T_ = r.randint(4, 8)
        tx = r.randint(1, T_ - 1)
        aA = r.choice([-2, -1, -0.5, 0, 0.5, 1, 2, 3]); aB = r.choice([-2, -1, -0.5, 0, 0.5, 1, 2, 3])
        if aA == aB: return None
        vc = r.choice([4, 6, 8, 10, 12, 14])
        vA0, vB0 = vc - aA * tx, vc - aB * tx
        vA1, vB1 = vA0 + aA * T_, vB0 + aB * T_
        if min(vA0, vB0, vA1, vB1) < 0 or max(vA0, vA1, vB0, vB1) > 24 or not two(vA0) or not two(vB0) or not two(vA1) or not two(vB1) or vA0 == vB0: return None
        A = [(0, vA0), (T_, vA1)]; B = [(0, vB0), (T_, vB1)]
        fig = vt_two_fig(A, B, T_)
        if not fig: return None
        SA, SB = (vA0 + vA1) / 2 * T_, (vB0 + vB1) / 2 * T_
        assert abs(SA - (vA0 * T_ + 0.5 * aA * T_ ** 2)) < 1e-9
        vx = vA0 + aA * tx
        assert abs(vx - (vB0 + aB * tx)) < 1e-9
        SAx = vA0 * tx + 0.5 * aA * tx ** 2; SBx = vB0 * tx + 0.5 * aB * tx ** 2
        cands = []
        cands.append(('A의 가속도의 크기는 B의 가속도의 크기보다 크다.', abs(aA) > abs(aB), '가속도의 크기는 그래프 기울기의 절댓값이다. |a%s| = %s m/s², |a%s| = %s m/s² 이므로 %s' % (sub('A'), num(abs(aA)), sub('B'), num(abs(aB)), 'A가 크다.' if abs(aA) > abs(aB) else 'B가 크거나 같다.')))
        cands.append(('%s초일 때 A와 B의 속력은 같다.' % num(tx), True, '두 그래프가 만나는 %s초에 두 속력은 %s m/s 로 같다.' % (num(tx), num(vx))))
        wrongt = tx + 1 if tx + 1 < T_ else tx - 1
        cands.append(('%s초일 때 A와 B의 속력은 같다.' % num(wrongt), False, '두 속력이 같은 순간은 그래프가 만나는 %s초이다.' % num(tx)))
        cands.append(('0 ~ %d초 동안 A가 이동한 거리는 B가 이동한 거리보다 크다.' % T_, SA > SB, '넓이를 비교하면 A는 %s m, B는 %s m 이므로 %s' % (num(SA), num(SB), 'A가 더 멀리 이동하였다.' if SA > SB else 'B가 더 멀리 이동했거나 같다.')))
        cands.append(('A의 속력은 시간에 따라 증가한다.', aA > 0, 'A의 속력은 %s m/s 에서 %s m/s 로 변한다.' % (num(vA0), num(vA1))))
        cands.append(('B의 속력은 시간에 따라 감소한다.', aB < 0, 'B의 속력은 %s m/s 에서 %s m/s 로 변한다.' % (num(vB0), num(vB1))))
        cands.append(('%s초일 때 A와 B는 같은 위치에 있다.' % num(tx), abs(SAx - SBx) < 1e-9, '0 ~ %s초 동안 A는 %s m, B는 %s m 이동했으므로 %s' % (num(tx), num(SAx), num(SBx), '위치가 같다.' if abs(SAx - SBx) < 1e-9 else '위치가 같지 않다(속력이 같을 뿐이다).')))
        cands.append(('%d초일 때 A는 B보다 앞서 있다.' % T_, SA > SB, '%d초까지의 이동 거리는 A %s m, B %s m 이다.' % (T_, num(SA), num(SB))))
        cands.append(('0 ~ %d초 동안 A의 평균 속력은 B의 평균 속력보다 작다.' % T_, SA < SB, '평균 속력은 이동 거리/시간이며 A %s m/s, B %s m/s 이다.' % (num(SA / T_), num(SB / T_))))
        sel = r.sample(cands, 3)
        if len({s[0] for s in sel}) < 3: return None
        intro = '그림은 직선 도로의 같은 지점에서 같은 방향으로 동시에 출발한 두 물체 A, B의 속력을 시간에 따라 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'
        return bogi(intro, [(s[0], s[1], s[2]) for s in sel], r=r, pre=FIG(fig, '66%'), ask='', lv='상', fam='c',
                    core='두 물체의 v-t 그래프에서 교점은 속력이 같은 순간이고, 위치 비교는 넓이로 한다.', point='속력이 같은 순간과 위치가 같은 순간을 구분한다.')
    # 한 물체 그래프
    kind = r.choice(['trap', 'tri', 'init', 'rev', 'rev2', 'trap', 'init'])
    pts = rand_prof(r, kind)
    if not pts: return None
    has_neg = any(v < 0 for _, v in pts)
    fig = vt_fig(pts, shade=not has_neg)
    if not fig: return None
    sg = segs_of(pts); T_ = pts[-1][0]
    cross = None
    for s in sg:
        if s['v0'] * s['v1'] < 0: cross = s['t0'] + abs(s['v0']) / abs(s['a']); break
    if has_neg and (cross is None or not half(cross)): return None
    xs = {t: x_at(pts, t) for t, _ in pts}
    segd = lambda s: dist_total([(s['t0'], s['v0']), (s['t1'], s['v1'])])
    nz = [s for s in sg if abs(s['a']) > 0]
    noncross = [s for s in nz if s['v0'] * s['v1'] >= 0]

    def pert(val, alts):
        c = [x for x in alts if x is not None and two(x) and abs(x - val) > 1e-9 and x > 0]
        return r.choice(c) if c else None

    def t_acc(want):
        if not nz: return None
        s = r.choice(nz); a = abs(s['a'])
        val = a if want else pert(a, [a * 2, a / 2, a + 1, abs(s['v1'] - s['v0']), abs(s['v1']), a + 0.5])
        if val is None: return None
        return ('%s 동안 가속도의 크기는 %s m/s²이다.' % (seg_name(s), num(val)), abs(val - a) < 1e-9, '%s 동안 속도가 %s m/s 에서 %s m/s 로 변하므로 가속도의 크기는 %s m/s² 이다.' % (seg_name(s), num(s['v0']), num(s['v1']), num(a)))

    def t_const(want):
        c = [s for s in sg if (s['a'] == 0) == want]
        if not c: return None
        s = r.choice(c)
        return ('%s 동안 물체는 등속 직선 운동을 한다.' % seg_name(s), s['a'] == 0, ('이 구간에서 속도가 %s m/s 로 일정하므로 등속 직선 운동이다.' % num(s['v0'])) if s['a'] == 0 else ('이 구간에서 속도가 %s m/s 에서 %s m/s 로 변하므로 등가속도 운동이다.' % (num(s['v0']), num(s['v1']))))

    def t_speedup(want):
        c = [s for s in noncross if (abs(s['v1']) > abs(s['v0'])) == want]
        if not c: return None
        s = r.choice(c)
        return ('%s 동안 물체의 속력은 증가한다.' % seg_name(s), want, '이 구간에서 속력이 %s m/s 에서 %s m/s 로 %s한다.' % (num(abs(s['v0'])), num(abs(s['v1'])), '증가' if want else '감소'))

    def t_vacc(want):
        c = [s for s in noncross if (abs(s['v1']) < abs(s['v0'])) == want]
        if not c: return None
        s = r.choice(c)
        return ('%s 동안 물체의 속도의 방향과 가속도의 방향은 서로 반대이다.' % seg_name(s), want, '이 구간에서 속력이 %s한다. 속력이 %s하면 속도와 가속도의 방향은 %s.' % ('감소' if want else '증가', '감소' if want else '증가', '반대이다' if want else '같다'))

    def t_dist(want):
        i = r.randint(1, len(pts) - 1); cut = pts[:i + 1]; Tx = cut[-1][0]; D = dist_total(cut)
        if not two(D): return None
        val = D if want else pert(D, [D * 2, D / 2, D + 2, abs(disp_area(cut)) if has_neg else None, D + Tx, D - 2])
        if val is None: return None
        return ('0 ~ %s초 동안 물체가 이동한 거리는 %s m이다.' % (num(Tx), num(val)), abs(val - D) < 1e-9, '0 ~ %s초 동안 그래프와 시간 축 사이의 넓이(절댓값의 합)는 %s m 이다.' % (num(Tx), num(D)))

    def t_avgsp(want):
        D = dist_total(pts); av = D / T_
        if not two(av): return None
        val = av if want else pert(av, [av * 2, av / 2, av + 1, abs(disp_area(pts)) / T_ if has_neg else None, max(abs(v) for _, v in pts) / 2])
        if val is None: return None
        return ('0 ~ %s초 동안 물체의 평균 속력은 %s m/s이다.' % (num(T_), num(val)), abs(val - av) < 1e-9, '이동 거리 %s m 를 %s초로 나누면 평균 속력은 %s m/s 이다.' % (num(D), num(T_), num(av)))

    def t_turn(want):
        if has_neg:
            if want: return ('물체의 운동 방향은 %s초일 때 바뀐다.' % num(cross), True, '속도가 0이 되며 부호가 바뀌는 %s초에 운동 방향이 바뀐다.' % num(cross))
            alt = [t for t, _ in pts if t > 0 and abs(t - cross) > 1e-9]
            if not alt: return None
            return ('물체의 운동 방향은 %s초일 때 바뀐다.' % num(r.choice(alt)), False, '속도의 부호가 바뀌는 순간은 %s초이다.' % num(cross))
        if want: return None
        return ('0 ~ %s초 동안 물체의 운동 방향이 바뀌는 순간이 있다.' % num(T_), False, '속도가 항상 0 이상이므로 운동 방향이 바뀌지 않는다.')

    def t_adir(want):
        pr = [(a, b) for a in nz for b in nz if a['t0'] < b['t0'] and ((a['a'] > 0) == (b['a'] > 0)) == want]
        if not pr: return None
        a, b = r.choice(pr)
        return ('%s 동안과 %s 동안 가속도의 방향은 서로 같다.' % (seg_name(a), seg_name(b)), want, '기울기의 부호가 %s 와 %s 이므로 가속도의 방향은 %s.' % ('양(+)' if a['a'] > 0 else '음(-)', '양(+)' if b['a'] > 0 else '음(-)', '같다' if want else '서로 반대이다'))

    def t_farther(want):
        pr = [(a, b) for a in sg for b in sg if a is not b and abs(segd(a) - segd(b)) > 1e-9 and (segd(a) > segd(b)) == want]
        if not pr: return None
        a, b = r.choice(pr)
        return ('%s 동안 이동한 거리는 %s 동안 이동한 거리보다 크다.' % (seg_name(a), seg_name(b)), want, '구간별 이동 거리(넓이)는 %s m 와 %s m 이다.' % (num(segd(a)), num(segd(b))))

    def t_azero(want):
        c = [s for s in sg if (s['a'] == 0) == want and half((s['t0'] + s['t1']) / 2)]
        if not c: return None
        s = r.choice(c); tm = (s['t0'] + s['t1']) / 2
        return ('%s초일 때 물체의 가속도는 0이다.' % num(tm), s['a'] == 0, '%s초는 %s 구간에 속하며 이 구간의 가속도는 %s m/s² 이다.' % (num(tm), seg_name(s), num(s['a'])))

    mx = max(abs(v) for _, v in pts)
    mxt = [t for t, v in pts if abs(v) == mx]

    def t_vmax(want):
        if len(mxt) != 1: return None
        if want: return ('속력이 가장 큰 순간은 %s초일 때이다.' % num(mxt[0]), True, '속력의 최댓값 %s m/s 는 %s초에 나타난다.' % (num(mx), num(mxt[0])))
        alt = [t for t, _ in pts if t not in mxt]
        if not alt: return None
        return ('속력이 가장 큰 순간은 %s초일 때이다.' % num(r.choice(alt)), False, '속력이 가장 큰 순간은 %s초이다.' % num(mxt[0]))

    far = max(xs, key=lambda t: abs(xs[t]))
    ties = [t for t in xs if abs(abs(xs[t]) - abs(xs[far])) < 1e-9]

    def t_far(want):
        if len(ties) != 1: return None
        if want: return ('출발점에서 가장 멀리 떨어져 있는 순간은 %s초일 때이다.' % num(far), True, '위치(넓이의 누적)의 절댓값이 %s m 로 최대인 순간은 %s초이다.' % (num(abs(xs[far])), num(far)))
        alt = [t for t, _ in pts if t > 0 and t != far]
        if not alt: return None
        return ('출발점에서 가장 멀리 떨어져 있는 순간은 %s초일 때이다.' % num(r.choice(alt)), False, '출발점에서 가장 먼 순간은 %s초이다.' % num(far))

    def t_same(want):
        if (not has_neg) == want:
            return ('0 ~ %s초 동안 이동 거리와 변위의 크기는 같다.' % num(T_), (not has_neg), ('속도의 방향이 바뀌지 않으므로 이동 거리와 변위의 크기가 같다.' if not has_neg else '운동 방향이 바뀌므로 이동 거리가 변위의 크기보다 크다.'))
        return None

    def t_speedat(want):
        tt = r.choice([x / 2 for x in range(1, int(2 * T_))])
        v = v_at(pts, tt)
        if v is None or not two(abs(v)): return None
        val = abs(v) if want else pert(abs(v), [abs(v) * 2, abs(v) + 1, abs(v) / 2, abs(v) + 2, mx])
        if val is None: return None
        return ('%s초일 때 물체의 속력은 %s m/s이다.' % (num(tt), num(val)), abs(val - abs(v)) < 1e-9, '%s초에서 그래프를 읽으면 속도는 %s m/s 이므로 속력은 %s m/s 이다.' % (num(tt), num(v), num(abs(v))))

    def t_ratio(want):
        pr = [(a, b) for a in nz for b in nz if a is not b]
        if not pr: return None
        a, b = r.choice(pr); q = abs(a['a']) / abs(b['a'])
        if not half(q) or q <= 0: return None
        val = q if want else pert(q, [q * 2, q / 2, q + 1, 1 / q if half(1 / q) else None, q + 0.5, 2, 3, 0.5])
        if val is None or not half(val): return None
        return ('%s 동안 가속도의 크기는 %s 동안 가속도의 크기의 %s배이다.' % (seg_name(a), seg_name(b), num(val)), abs(val - q) < 1e-9, '가속도의 크기는 각각 %s m/s², %s m/s² 이므로 비는 %s배이다.' % (num(abs(a['a'])), num(abs(b['a'])), num(q)))

    def t_speq(want):
        tl = [t for t, _ in pts]
        pr = [(a, b) for a in tl for b in tl if a < b and (abs(abs(v_at(pts, a)) - abs(v_at(pts, b))) < 1e-9) == want and not (a == 0 and want and False)]
        if not pr: return None
        a, b = r.choice(pr)
        return ('%s초일 때와 %s초일 때 물체의 속력은 서로 같다.' % (num(a), num(b)), want, '두 시각의 속력은 %s m/s, %s m/s 이다.' % (num(abs(v_at(pts, a))), num(abs(v_at(pts, b)))))

    def t_stop(want):
        zs = [t for t, v in pts if v == 0 and t > 0]
        if want:
            if not zs: return None
            t0_ = r.choice(zs)
        else:
            nzt = [t for t, v in pts if v != 0 and t > 0]
            if not nzt: return None
            t0_ = r.choice(nzt)
        return ('%s초일 때 물체의 순간 속도는 0이다.' % num(t0_), want, '%s초일 때 속도는 %s m/s 이다.' % (num(t0_), num(v_at(pts, t0_))))

    def t_avgseg(want):
        c = [s for s in noncross if s['a'] != 0]
        if not c: return None
        s = r.choice(c); av = abs(s['v0'] + s['v1']) / 2
        val = av if want else pert(av, [abs(s['v1']), abs(s['v0']), av + 1, av * 2])
        if val is None: return None
        return ('%s 동안 물체의 평균 속력은 %s m/s이다.' % (seg_name(s), num(val)), abs(val - av) < 1e-9, '직선 구간의 평균 속력은 (%s + %s)/2 = %s m/s 이다.' % (num(abs(s['v0'])), num(abs(s['v1'])), num(av)))

    TPL = [('acc', t_acc), ('const', t_const), ('spd', t_speedup), ('spd', t_vacc), ('dist', t_dist), ('avg', t_avgsp), ('turn', t_turn), ('adir', t_adir),
           ('far1', t_farther), ('azero', t_azero), ('vmax', t_vmax), ('far', t_far), ('same', t_same), ('spat', t_speedat), ('ratio', t_ratio),
           ('speq', t_speq), ('stop', t_stop), ('avgseg', t_avgseg)]
    r.shuffle(TPL)
    chosen, used, txt = [], set(), set()
    for g, f in TPL:
        if g in used: continue
        out = f(r.random() < 0.5)
        if out is None or out[0] in txt: continue
        used.add(g); txt.add(out[0]); chosen.append(out)
        if len(chosen) == 3: break
    if len(chosen) < 3: return None
    intro = '그림은 직선 도로 위에서 운동하는 물체의 %s를 시간에 따라 나타낸 것이다.%s 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % ('속도' if has_neg else '속력', ' (단, 처음 운동 방향을 +방향으로 한다.)' if has_neg else '')
    return bogi(intro, chosen, r=r, pre=FIG(fig, '66%'), ask='', lv='중', fam='a',
                core='v-t 그래프의 기울기는 가속도, 그래프와 시간 축 사이의 넓이는 변위이며, 속력은 속도의 절댓값이다.', point='그래프에서 기울기·넓이·부호를 읽어 설명의 참거짓을 판단한다.')


# ================================================================ ph023 (s-t · a-t 그래프)
def st_curve_fig(v0, a, T_, marks, hide=None, w=300, h=190):
    """s = v0 t + ½ a t² 포물선 그래프. marks: 점선·눈금으로 표시할 시각들. hide: 값을 문자로 가릴 시각."""
    smax = v0 * T_ + 0.5 * a * T_ * T_
    p = Plot(w, h, T_ * 1.12, smax * 1.15, ml=48, mr=18, mt=16, mb=30)
    ypx = (h - p.mt - p.mb) / (smax * 1.15); xpx = (w - p.ml - p.mr) / (T_ * 1.12)
    ts = sorted(set(marks)); ss = [v0 * t + 0.5 * a * t * t for t in ts]
    if not ticks_ok(ts + [0], xpx, 17) or not ticks_ok(ss + [0], ypx, 13): return None
    yf = lambda y: 's' if hide is not None and abs(y - hide) < 1e-9 else num(y)
    p.axes('t(s)', 'x(m)', ts, ss, yfmt=yf)
    for t, s in zip(ts, ss):
        p.line(p.px(t), p.py(s), p.px(t), p.py(0), GR, 1, '4 3'); p.line(p.px(t), p.py(s), p.px(0), p.py(s), GR, 1, '4 3')
    pts = [(T_ * i / 60, v0 * T_ * i / 60 + 0.5 * a * (T_ * i / 60) ** 2) for i in range(61)]
    p.pl(pts, BL, 2.6)
    for t, s in zip(ts, ss):
        p.circ(p.px(t), p.py(s), 3.4, RD, RD, 1)
    return p.svg()


def at_fig(segs, w=300, h=190):
    """a-t 그래프(구간별 일정). segs: [(t0, t1, a)]."""
    am = [a for _, _, a in segs]
    ymax = max(am) * 1.3 if max(am) > 0 else 1
    ymin = min(am) * 1.3 if min(am) < 0 else 0
    T_ = segs[-1][1]
    p = Plot(w, h, T_ * 1.12, ymax, ymin=ymin, ml=46, mr=18, mt=16, mb=30)
    ypx = (h - p.mt - p.mb) / (ymax - ymin); xpx = (w - p.ml - p.mr) / (T_ * 1.12)
    xt = sorted(set([0] + [s[1] for s in segs]) - {0}); yt = sorted(set(a for a in am if a != 0))
    if not ticks_ok(xt + [0], xpx, 17) or not ticks_ok(yt + [0], ypx, 13): return None
    for t0, t1, a in segs:
        if a != 0:
            p.o.insert(0, '<polygon points="%s" fill="%s" stroke="none"/>' % (' '.join('%s,%s' % (Fig._n(x), Fig._n(y)) for x, y in [(p.px(t0), p.py(0)), (p.px(t0), p.py(a)), (p.px(t1), p.py(a)), (p.px(t1), p.py(0))]), '#cfe2f7' if a > 0 else '#f6d3cf'))
    p.axes('t(s)', 'a(m/s²)', xt, yt)
    for t0, t1, a in segs:
        p.line(p.px(t0), p.py(a), p.px(t1), p.py(a), BL, 2.8)
        p.line(p.px(t0), p.py(a), p.px(0), p.py(a), GR, 1, '4 3')
        p.line(p.px(t0), p.py(0), p.px(t0), p.py(a), GR, 1, '4 3')
        p.line(p.px(t1), p.py(0), p.px(t1), p.py(a), GR, 1, '4 3')
    return p.svg()


def vt_from_at(v0, segs):
    pts = [(0, v0)]
    v = v0
    for t0, t1, a in segs:
        v += a * (t1 - t0); pts.append((t1, v))
    return pts


@T('ph023')
def st_at(r, k):
    form = r.choice(['stlin_v', 'stlin_v', 'stlin_v', 'stlin_avg', 'stlin_dist', 'stpar_a', 'stpar_a', 'stpar_v', 'stpar2', 'at_v', 'at_v', 'at_v', 'at_s', 'at_max'])
    ob = r.choice(['물체', '수레', '자동차', '전동차', '썰매'])
    if form.startswith('stlin'):
        n = r.choice([3, 3, 4]); durs = [r.randint(1, 4) for _ in range(n)]
        spd = [r.choice([-4, -3, -2, -1, 0, 0, 1, 2, 3, 4, 5, 6]) for _ in range(n)]
        if len(set(spd)) < n - 0 and False: return None
        if any(spd[i] == spd[i + 1] for i in range(n - 1)): return None
        s0 = r.choice([0, 0, 2, 4, 6, 8]); pts = [(0, s0)]
        for d, v in zip(durs, spd): pts.append((pts[-1][0] + d, pts[-1][1] + d * v))
        if min(s for _, s in pts) < 0 or max(s for _, s in pts) > 40 or pts[-1][0] > 11: return None
        fig = vt_fig(pts, xl='t(s)', yl='x(m)', shade=False)
        if not fig: return None
        sg = segs_of(pts)
        if form == 'stlin_v':
            s = r.choice(sg)
            if s['a'] == 0 and False: return None
            sp = s['a']
            body = PP('그림은 직선 도로 위의 %s의 위치를 시간에 따라 나타낸 것이다. %s 동안 %s의 속력은?' % (ob, seg_name(s), ob)) + FIG(fig, '66%')
            wr = wl(abs(sp), [abs(s['v1']), abs(s['v1']) / s['t1'] if s['t1'] else None, abs(s['v1'] - s['v0']) * (s['t1'] - s['t0']), abs(sp) * 2, abs(sp) + 1, (abs(s['v0']) + abs(s['v1'])) / 2], 'm/s', nonneg=(sp != 0)) if sp != 0 else None
            if sp == 0:
                wr = wl(1, [1, 2, 3, 4, 5, 6], 'm/s')
                wr = [w for w in wr if not w.startswith('0 ')]
                right = '0 m/s'
                wr = ['1 m/s', '2 m/s', '3 m/s', '4 m/s', '%s m/s' % num(s['v0'] if s['v0'] > 0 else 5)]
                if num(s['v0']) in ('1', '2', '3', '4'): wr[-1] = '6 m/s'
            else:
                right = ans(abs(sp), 'm/s')
            return mc(body, right, wr, r=r, lv='하', fam='a',
                      steps=['x-t 그래프의 기울기가 속도이다.', '%s 동안 위치가 %s m 에서 %s m 로 변했다.' % (seg_name(s), num(s['v0']), num(s['v1'])),
                             '속도 = (%s - %s)/(%s - %s) = %s m/s 이므로 속력은 %s m/s 이다.' % (num(s['v1']), num(s['v0']), num(s['t1']), num(s['t0']), num(sp), num(abs(sp)))],
                      core='위치-시간 그래프의 기울기는 속도이다. 기울기가 0이면 정지해 있다.', point='구간의 위치 변화를 시간으로 나누어 속도를 구한다.')
        T_ = pts[-1][0]
        if form == 'stlin_avg':
            S = pts[-1][1] - pts[0][1]
            if S == 0 or not two(S / T_): return None
            av = abs(S) / T_
            body = PP('그림은 직선 도로 위의 %s의 위치를 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 평균 속도의 크기는?' % (ob, num(T_))) + FIG(fig, '66%')
            D = sum(abs(s['v1'] - s['v0']) for s in sg)
            wr = wl(av, [D / T_, max(abs(s['a']) for s in sg), sum(abs(s['a']) for s in sg) / len(sg), av * 2, abs(pts[-1][1]) / T_ + 1, av + 1], 'm/s')
            return mc(body, ans(av, 'm/s'), wr, r=r, lv='중', fam='b',
                      steps=['평균 속도 = 변위 / 걸린 시간', '변위 = %s - %s = %s m' % (num(pts[-1][1]), num(pts[0][1]), num(S)), '평균 속도의 크기 = %s / %s = %s m/s' % (num(abs(S)), num(T_), num(av))],
                      core='평균 속도는 변위를 걸린 시간으로 나눈 값으로, x-t 그래프에서 처음과 나중을 잇는 직선의 기울기이다.', point='이동 경로가 아니라 처음과 나중 위치의 차(변위)를 쓴다.')
        D = sum(abs(s['v1'] - s['v0']) for s in sg); S = pts[-1][1] - pts[0][1]
        if D == abs(S): return None
        body = PP('그림은 직선 도로 위의 %s의 위치를 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 %s이(가) 이동한 거리(경로의 길이)는?' % (ob, num(T_), ob)) + FIG(fig, '66%')
        wr = wl(D, [abs(S), D + 2, D - 2, max(s for _, s in pts) , sum(abs(s['a']) for s in sg), D + abs(S)], 'm')
        return mc(body, ans(D, 'm'), wr, r=r, lv='상', fam='c',
                  steps=['구간별 위치 변화의 크기를 모두 더한다.'] + ['%s : |%s - %s| = %s m' % (seg_name(s), num(s['v1']), num(s['v0']), num(abs(s['v1'] - s['v0']))) for s in sg] + ['이동 거리 = %s m (변위의 크기는 %s m)' % (num(D), num(abs(S)))],
                  core='이동 거리는 구간별 위치 변화의 크기를 합한 것이고, 변위는 처음과 나중 위치의 차이다.', point='되돌아오는 구간이 있는 x-t 그래프에서 이동 거리를 구한다.')
    if form in ('stpar_a', 'stpar_v'):
        a = r.choice([1, 2, 3, 4, 5, 6, 0.5, 1.5, 2]); T_ = r.randint(2, 8)
        S = 0.5 * a * T_ * T_
        if not two(S) or not half(S): return None
        fig = st_curve_fig(0, a, T_, [T_])
        if not fig: return None
        if form == 'stpar_a':
            body = PP('그림은 정지해 있던 %s이(가) 직선 위를 일정한 가속도로 출발하여 운동할 때의 위치를 시간에 따라 나타낸 것이다(곡선의 꼭짓점이 원점이다). %s의 가속도의 크기는?' % (ob, ob)) + FIG(fig, '66%')
            wr = wl(a, [S / T_, S / T_ / 2, 2 * S / T_, S / (T_ * T_), S, 4 * S / (T_ * T_)], 'm/s²')
            return mc(body, ans(a, 'm/s²'), wr, r=r, lv='중', fam='d',
                      steps=['정지 상태에서 출발하므로 x = ½at² 이다.', '%s = ½ × a × %s² 에서 a = 2 × %s / %s² = %s m/s²' % (num(S), num(T_), num(S), num(T_), num(a))],
                      core='정지에서 출발한 등가속도 운동의 x-t 그래프는 x = ½at² 인 포물선이다.', point='그래프의 한 점으로 가속도를 구한다.')
        v = a * T_
        body = PP('그림은 정지해 있던 %s이(가) 직선 위를 일정한 가속도로 출발하여 운동할 때의 위치를 시간에 따라 나타낸 것이다(곡선의 꼭짓점이 원점이다). %s초일 때 %s의 속력은?' % (ob, num(T_), ob)) + FIG(fig, '66%')
        wr = wl(v, [S / T_, 2 * S / T_ / 2, S, a, v / 2, S * 2], 'm/s')
        assert abs(v - 2 * S / T_) < 1e-9
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='상', fam='e',
                  steps=['x = ½at² 에서 a = 2 × %s / %s² = %s m/s²' % (num(S), num(T_), num(a)), 'v = at = %s × %s = %s m/s' % (num(a), num(T_), num(v)), '(v = 2x/t = 2 × %s / %s = %s m/s 로도 구할 수 있다.)' % (num(S), num(T_), num(v))],
                  core='x-t 그래프의 접선 기울기가 그 순간의 속도이다. 정지에서 출발하면 v = 2x/t 이다.', point='가속도를 구한 뒤 순간 속도를 구한다.')
    if form == 'stpar2':
        v0 = r.choice([0, 2, 4, 6, 8]); a = r.choice([1, 2, 3, 4, 6, 0.5, 2.5]); t1 = r.randint(1, 4)
        if v0 == 0: return None
        T2 = 2 * t1
        s1 = v0 * t1 + 0.5 * a * t1 * t1; s2 = v0 * T2 + 0.5 * a * T2 * T2
        if not two(s1) or not two(s2): return None
        fig = st_curve_fig(v0, a, T2, [t1, T2])
        if not fig: return None
        a_calc = (s2 - 2 * s1) / (t1 * t1); v0_calc = (s1 - 0.5 * a_calc * t1 * t1) / t1
        assert abs(a_calc - a) < 1e-9 and abs(v0_calc - v0) < 1e-9
        ask = r.choice(['v0', 'a'])
        body = PP('그림은 직선 위를 운동하는 %s의 위치를 시간에 따라 나타낸 것이다. %s는 일정한 가속도 운동을 하며 t = 0 일 때 위치는 0이다. %s의 %s는?' % (ob, ob, ob, '처음 속력(t = 0 일 때의 속력)' if ask == 'v0' else '가속도의 크기')) + FIG(fig, '66%')
        if ask == 'v0':
            wr = wl(v0, [s1 / t1, s2 / T2, (s2 - s1) / t1, s1 / t1 / 2, a, s2 / T2 - a * T2 / 2 + 1], 'm/s')
            return mc(body, ans(v0, 'm/s'), wr, r=r, lv='상', fam='f',
                      steps=['x = v₀t + ½at² 에 두 점을 대입한다 : %s = %s v₀ + %s a, %s = %s v₀ + %s a' % (num(s1), num(t1), num(0.5 * t1 * t1), num(s2), num(T2), num(0.5 * T2 * T2)),
                             '둘째 식 - 첫째 식 × 2 : %s - %s = %s a 이므로 a = %s m/s²' % (num(s2), num(2 * s1), num(t1 * t1), num(a)), '첫째 식에서 v₀ = (%s - %s)/%s = %s m/s' % (num(s1), num(0.5 * a * t1 * t1), num(t1), num(v0))],
                      core='x = v₀t + ½at² 에 그래프의 두 점을 대입하면 v₀ 와 a 를 구할 수 있다.', point='연립 방정식으로 처음 속력과 가속도를 구한다.')
        wr = wl(a, [(s2 - s1) / (T2 - t1) / t1, (s2 - 2 * s1) / t1, 2 * s1 / (t1 * t1), (s2 - s1) / t1, 2 * (s2 - s1) / (t1 * t1), a * 2], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='상', fam='f',
                  steps=['x = v₀t + ½at² 에 두 점을 대입한다 : %s = %s v₀ + %s a, %s = %s v₀ + %s a' % (num(s1), num(t1), num(0.5 * t1 * t1), num(s2), num(T2), num(0.5 * T2 * T2)),
                         '둘째 식 - 첫째 식 × 2 : %s - %s = %s a' % (num(s2), num(2 * s1), num(t1 * t1)), 'a = %s m/s²' % num(a)],
                  core='x = v₀t + ½at² 에 그래프의 두 점을 대입하면 v₀ 와 a 를 구할 수 있다.', point='v₀t 항을 소거하여 가속도를 구한다.')
    # a-t
    n = r.choice([2, 2, 3]); durs = [r.randint(1, 4) for _ in range(n)]
    acc = [r.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]) for _ in range(n)]
    if any(acc[i] == acc[i + 1] for i in range(n - 1)) or all(a == 0 for a in acc): return None
    segs = []; t = 0
    for d, a in zip(durs, acc): segs.append((t, t + d, a)); t += d
    T_ = t
    if T_ > 10: return None
    fig = at_fig(segs)
    if not fig: return None
    if form == 'at_v':
        v0 = r.choice([0, 2, 4, 5, 6, 8, 10])
        pts = vt_from_at(v0, segs); vT = pts[-1][1]
        if vT < 0 or any(v < 0 for _, v in pts) or v0 == 0 and False: return None
        dv = sum(a * (t1 - t0) for t0, t1, a in segs)
        assert abs(vT - (v0 + dv)) < 1e-9
        body = PP('그림은 직선 위를 운동하는 %s의 가속도를 시간에 따라 나타낸 것이다. 처음 속력이 %s일 때, %s초일 때의 속력은? (단, 운동 방향은 변하지 않는다.)' % (ob, U(v0, 'm/s'), num(T_)) if v0 else
                  '그림은 정지해 있던 %s이(가) 직선 위를 운동할 때의 가속도를 시간에 따라 나타낸 것이다. %s초일 때의 속력은? (단, 운동 방향은 변하지 않는다.)' % (ob, num(T_))) + FIG(fig, '66%')
        wr = wl(vT, [dv, v0 + max(a for _, _, a in segs) * T_, v0 + sum(abs(a) * (t1 - t0) for t0, t1, a in segs), sum(a for _, _, a in segs) + v0, vT + 2, abs(v0 - dv)], 'm/s')
        return mc(body, ans(vT, 'm/s'), wr, r=r, lv='중', fam='g',
                  steps=['a-t 그래프와 시간 축 사이의 넓이가 속도 변화량이다(시간 축 아래는 -).'] + ['%s : %s × %s = %s m/s' % (seg_name({'t0': t0, 't1': t1}), num(a), num(t1 - t0), num(a * (t1 - t0))) for t0, t1, a in segs] + ['v = %s + (%s) = %s m/s' % (num(v0), num(dv), num(vT))],
                  core='a-t 그래프의 넓이는 속도 변화량이다.', point='가속도 그래프 넓이에 처음 속도를 더한다.')
    if form == 'at_s':
        pts = vt_from_at(0, segs)
        if any(v < -1e-9 for _, v in pts): return None
        S = disp_area(pts)
        S2 = 0; v = 0
        for t0, t1, a in segs:
            d = t1 - t0; S2 += v * d + 0.5 * a * d * d; v += a * d
        assert abs(S - S2) < 1e-9
        if not two(S) or S == 0: return None
        body = PP('그림은 정지해 있던 %s이(가) 직선 위를 운동할 때의 가속도를 시간에 따라 나타낸 것이다. 0 ~ %s초 동안 %s의 이동 거리는? (단, 운동 방향은 변하지 않는다.)' % (ob, num(T_), ob)) + FIG(fig, '66%')
        vT = pts[-1][1]
        wr = wl(S, [vT * T_, vT * T_ / 2, sum(0.5 * a * (t1 - t0) ** 2 for t0, t1, a in segs), vT, S + vT, S * 2], 'm')
        return mc(body, ans(S, 'm'), wr, r=r, lv='상', fam='h',
                  steps=['구간마다 속도 변화를 구해 v-t 그래프를 그린다 : ' + ', '.join('%s초 %s m/s' % (num(t_), num(v_)) for t_, v_ in pts)] + ['v-t 그래프의 넓이 = %s m' % num(S), '(구간별 s = v₀t + ½at² 의 합 = %s m 로 확인)' % num(S2)],
                  core='a-t 그래프로 속도 변화를 구하고, 이를 v-t 그래프로 옮겨 넓이로 이동 거리를 구한다.', point='a-t 그래프 → v-t 그래프 → 이동 거리의 순서로 푼다.')
    # at_max : 정지에서 출발, 가속도가 +에서 -로 바뀌는 시각이 속력 최대
    segs2 = []; t = 0
    a1 = r.choice([1, 2, 3, 4]); a2 = r.choice([-1, -2, -3]); a3 = r.choice([0, -1, -2, 1, 2])
    d1, d2 = r.randint(2, 4), r.randint(1, 3)
    if a3 == a2: return None
    segs2 = [(0, d1, a1), (d1, d1 + d2, a2), (d1 + d2, d1 + d2 + r.randint(1, 3), a3)]
    pts = vt_from_at(0, segs2)
    if any(v < -1e-9 for _, v in pts): return None
    mxv = max(v for _, v in pts)
    best = [t for t, v in pts if abs(v - mxv) < 1e-9]
    if len(best) != 1 or best[0] != d1: return None
    fig = at_fig(segs2)
    if not fig: return None
    body = PP('그림은 정지해 있던 %s이(가) 직선 위를 운동할 때의 가속도를 시간에 따라 나타낸 것이다. %s의 속력이 가장 큰 순간은 출발 후 몇 초일 때인가? (단, 운동 방향은 변하지 않는다.)' % (ob, ob)) + FIG(fig, '66%')
    others = [t for t, _ in pts if t not in (0, d1)] + [d1 - 1 if d1 > 1 else d1 + 1]
    wr = wl(d1, others + [d1 + d2 - 1, d1 + 1], 's')
    return mc(body, ans(d1, 's'), wr, r=r, lv='중', fam='i',
              steps=['가속도가 +인 동안 속력이 증가하고, -가 되면 속력이 감소한다.', '가속도의 부호가 +에서 -로 바뀌는 %s초일 때 속력이 최대이다(%s m/s).' % (num(d1), num(mxv)), '(그 후에도 속도는 0 이상이므로 속력은 줄어든다.)'],
              core='속도와 가속도의 방향이 같으면 속력이 증가하고, 반대이면 감소한다. 속력은 가속도 부호가 바뀌는 순간에 최대(또는 최소)이다.', point='a-t 그래프에서 부호 변화 시각을 찾는다.')


# ================================================================ ph024 (자유 낙하와 연직 투사)
def tower_fig(H, v0=None, up=True, w=250, h=190, ball2=None):
    """건물 꼭대기에서 던진 공. H: 높이 라벨."""
    f = Fig(w, h)
    gy = h - 20
    f.hatch(20, gy, w - 40)
    bx = 100; top = 48
    f.rect(bx - 28, top, 56, gy - top, '#eef2f7', INK, 1.6)
    f.circ(bx, top - 8, 7, RD, INK, 1.2)
    if v0 is not None:
        if up:
            f.arrow(bx + 18, top - 8, bx + 18, top - 38, BL, 2.4)
        else:
            f.arrow(bx + 18, top - 34, bx + 18, top - 6, BL, 2.4)
        f.text(bx + 28, top - 18, 'v₀ = %s m/s' % num(v0), 12.5, 'start', True, BL)
    f.line(bx + 40, top, bx + 40, gy, GR, 1.2, '4 3')
    f.line(bx + 34, top, bx + 46, top, GR, 1.2); f.line(bx + 34, gy, bx + 46, gy, GR, 1.2)
    f.text(bx + 50, (top + gy) / 2 + 4, 'H = %s m' % num(H), 13, 'start', True)
    f.text(bx, gy + 15, '지면', 11.5, c=GR)
    return f.svg()


def meet_fig(H, v0, w=250, h=200):
    f = Fig(w, h)
    gy = h - 22; top = 36
    f.hatch(20, gy, w - 40)
    xa, xb = 70, 170
    f.circ(xa, gy - 8, 7, BL, INK, 1.2); f.arrow(xa, gy - 18, xa, gy - 62, BL, 2.4)
    f.text(xa, gy - 70, 'A', 14, bold=True, c=BL, italic=True); f.text(xa + 10, gy - 38, 'v₀ = %s m/s' % num(v0), 12, 'start', True, BL)
    f.circ(xb, top, 7, RD, INK, 1.2); f.text(xb + 12, top + 5, 'B (정지)', 13, 'start', True, RD)
    f.line(xb, top + 10, xb, gy, GR, 1.2, '4 3')
    f.text(xb + 6, (top + gy) / 2 + 4, 'H = %s m' % num(H), 13, 'start', True)
    return f.svg()


@T('ph024')
def free_fall(r, k):
    form = r.choice(['free_t', 'free_v', 'up_h', 'up_h', 'up_pos', 'up_pos', 'tower', 'tower', 'down', 'graph', 'graph', 'two', 'twice', 'twice'])
    cond = '(단, 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)'
    if form == 'free_t':
        t = r.randint(1, 9); h = 5 * t * t
        if r.random() < 0.5:
            body = PP('높이 %s m 에서 공을 가만히 놓았다. 공이 지면에 닿을 때까지 걸리는 시간은? %s' % (num(h), cond))
            assert abs(math.sqrt(2 * h / G) - t) < 1e-9
            wr = wl(t, [h / 10, h / 5, math.sqrt(h) / 2, h / 2 / 10 * 2, t + 1, t - 1, 2 * t], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='하', fam='a',
                      steps=['처음 속력이 0인 자유 낙하이므로 h = ½gt² 이다.', '%s = ½ × 10 × t² 에서 t² = %s 이므로 t = %s s' % (num(h), num(t * t), num(t))],
                      core='자유 낙하 운동에서 낙하 거리는 h = ½gt² 이다.', point='낙하 거리로 낙하 시간을 구한다.')
        body = PP('가만히 놓은 공이 %s 동안 자유 낙하하였다. 이 시간 동안 낙하한 거리는? %s' % (U(t, '초').replace('초', '초'), cond))
        wr = wl(h, [10 * t * t, 10 * t, 5 * t, 5 * (t + 1) ** 2, 5 * t * t * 2, 5 * (t - 1) ** 2], 'm')
        return mc(body, ans(h, 'm'), wr, r=r, lv='하', fam='a',
                  steps=['h = ½gt² = ½ × 10 × %s² = %s m' % (num(t), num(h))],
                  core='자유 낙하 운동에서 낙하 거리는 h = ½gt² 이다.', point='낙하 시간으로 낙하 거리를 구한다.')
    if form == 'free_v':
        t = r.randint(1, 9); h = 5 * t * t; v = 10 * t
        assert abs(v - math.sqrt(2 * G * h)) < 1e-9
        body = PP('높이 %s m 에서 공을 가만히 놓았다. 공이 지면에 닿는 순간의 속력은? %s' % (num(h), cond))
        wr = wl(v, [h, h / 2, math.sqrt(h), 2 * v, v / 2, 5 * t, v + 10], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하', fam='a',
                  steps=['v² = 2gh = 2 × 10 × %s = %s 이므로 v = %s m/s' % (num(h), num(v * v), num(v)), '(낙하 시간 t = %s s, v = gt = 10 × %s = %s m/s 로 확인)' % (num(t), num(t), num(v))],
                  core='자유 낙하의 속력은 v = gt = √(2gh) 이다.', point='낙하 높이로 지면 도달 속력을 구한다.')
    if form == 'up_h':
        v0 = r.choice([10, 15, 20, 25, 30, 35, 40]); H = v0 * v0 / 20; tt = v0 / 10
        which = r.choice(['H', 'T', 'tt'])
        if which == 'H':
            body = PP('지면에서 공을 연직 위로 %s의 속력으로 던졌다. 공이 올라가는 최고점의 지면으로부터의 높이는? %s' % (U(v0, 'm/s'), cond))
            wr = wl(H, [v0 * v0 / 10, v0 / 10, v0 * v0 / 40, v0 / 2, 2 * H, v0], 'm')
            assert abs(H - (v0 * tt - 5 * tt * tt)) < 1e-9
            return mc(body, ans(H, 'm'), wr, r=r, lv='하', fam='b',
                      steps=['최고점에서 속력이 0이므로 0 - v₀² = 2(-g)H 이다.', 'H = v₀²/2g = %s²/20 = %s m' % (num(v0), num(H))],
                      core='연직 투사에서 최고점의 높이는 H = v₀²/2g 이다.', point='최고점에서 속력이 0임을 이용한다.')
        if which == 'T':
            T_ = 2 * tt
            body = PP('지면에서 공을 연직 위로 %s의 속력으로 던졌다. 공을 던진 순간부터 다시 지면에 떨어질 때까지 걸리는 시간은? %s' % (U(v0, 'm/s'), cond))
            wr = wl(T_, [tt, v0 / 5 * 2, v0, v0 / 20, T_ + 1, T_ * 2], 's')
            return mc(body, ans(T_, 's'), wr, r=r, lv='하', fam='b',
                      steps=['올라가는 시간 t = v₀/g = %s/10 = %s s' % (num(v0), num(tt)), '내려오는 시간도 같으므로 체공 시간은 2 × %s = %s s' % (num(tt), num(T_))],
                      core='연직 투사에서 올라가는 시간과 내려오는 시간은 같고, 체공 시간은 2v₀/g 이다.', point='올라가는 시간의 2배가 체공 시간이다.')
        body = PP('지면에서 공을 연직 위로 던졌더니 %s 후에 최고점에 도달하였다. 공을 던진 속력은? %s' % (U(tt, '초'), cond))
        v = 10 * tt
        wr = wl(v, [tt, 5 * tt, 20 * tt, tt * tt * 5, v / 2 + 5, 2 * v], 'm/s')
        return mc(body, ans(v, 'm/s'), wr, r=r, lv='하', fam='b',
                  steps=['최고점에서 v = 0 이므로 0 = v₀ - gt 에서 v₀ = gt = 10 × %s = %s m/s' % (num(tt), num(v))],
                  core='최고점에서는 속도가 0이므로 v₀ = gt 이다.', point='최고점 도달 시간으로 처음 속력을 구한다.')
    if form == 'up_pos':
        v0 = r.choice([20, 25, 30, 40]); t = r.choice([1, 2, 3, 4, 5, 6, 0.5, 1.5, 2.5, 3.5])
        v = v0 - 10 * t; hh = v0 * t - 5 * t * t
        if v == 0 or hh < 0 or not two(hh) or t * 10 > 2 * v0 - 1: return None
        assert abs(v * v - (v0 * v0 - 20 * hh)) < 1e-9
        direction = '위쪽' if v > 0 else '아래쪽'
        flip = '아래쪽' if v > 0 else '위쪽'
        body = PP('지면에서 공을 연직 위로 %s의 속력으로 던졌다. 던진 지 %s 후 공의 속력과 운동 방향을 옳게 짝지은 것은? %s' % (U(v0, 'm/s'), U(t, '초'), cond))
        right = '%s m/s, %s' % (num(abs(v)), direction)
        wr = ['%s m/s, %s' % (num(abs(v)), flip), '%s m/s, %s' % (num(v0 + 10 * t), direction), '%s m/s, %s' % (num(v0 - 5 * t), direction), '%s m/s, %s' % (num(abs(v) + 10), flip), '%s m/s, %s' % (num(v0 - 10 * (t + 1)) if v0 - 10 * (t + 1) != 0 else '5', direction)]
        return mc(body, right, wr, r=r, lv='중', fam='c', sort='shuf',
                  steps=['v = v₀ - gt = %s - 10 × %s = %s m/s' % (num(v0), num(t), num(v)), ('v > 0 이므로 아직 올라가고 있다(위쪽).' if v > 0 else 'v < 0 이므로 이미 최고점을 지나 내려오고 있다(아래쪽).'), '속력은 %s m/s 이다.' % num(abs(v))],
                  core='연직 투사에서 위쪽을 +로 하면 v = v₀ - gt 이며, 부호가 -이면 아래로 운동한다.', point='속도의 부호로 올라가는지 내려오는지 판단한다.')
    if form == 'tower':
        v0 = r.choice([5, 10, 15, 20, 25, 30]); t = r.randint(3, 8); H = 5 * t * t - v0 * t
        if H <= 0 or H > 200 or v0 >= 10 * t: return None
        vend = 10 * t - v0
        assert abs(vend ** 2 - (v0 * v0 + 20 * H)) < 1e-9
        ask = r.choice(['t', 'v'])
        fig = tower_fig(H, v0, True)
        body = PP('그림과 같이 높이 %s m 인 건물 꼭대기에서 공을 연직 위로 %s의 속력으로 던졌다. 공이 %s? %s' % (num(H), U(v0, 'm/s'), '지면에 떨어질 때까지 걸리는 시간은' if ask == 't' else '지면에 닿는 순간의 속력은', cond)) + FIG(fig, '56%')
        if ask == 't':
            wr = wl(t, [t - 1, t + 1, math.sqrt(H / 5), (v0 + 10 * 0) / 10 + math.sqrt(2 * H / 10), 2 * v0 / 10, t + 2, 2 * t], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='중', fam='d',
                      steps=['위 방향을 +로 하면 지면 도달 시 변위는 -%s m 이다.' % num(H), '-%s = %s t - 5t² 에서 5t² - %s t - %s = 0' % (num(H), num(v0), num(v0), num(H)), 't = %s s (양의 해)' % num(t)],
                      core='위로 던진 공이 처음 높이보다 낮은 곳에 도달하면 변위가 음(-)이다. h = v₀t - ½gt² 의 해를 구한다.', point='변위의 부호를 정하고 이차 방정식을 푼다.')
        wr = wl(vend, [v0 + 10 * t, 10 * t, math.sqrt(20 * H), math.sqrt(2 * 10 * H) + v0, v0, vend + 10, vend - 10], 'm/s')
        return mc(body, ans(vend, 'm/s'), wr, r=r, lv='중', fam='d',
                  steps=['던진 높이로 돌아왔을 때 속력은 v₀ = %s m/s (아래 방향)' % num(v0), '이후 H = %s m 를 더 내려가므로 v² = v₀² + 2gH = %s² + 2 × 10 × %s = %s' % (num(H), num(v0), num(H), num(vend * vend)), 'v = %s m/s' % num(vend)],
                  core='위로 던진 공은 출발점을 되돌아 지날 때 속력이 처음 속력과 같다. 에너지·운동 공식 v² = v₀² + 2gH 로 도달 속력을 구한다.', point='위로 던졌어도 지면 도달 속력은 v² = v₀² + 2gH 로 구한다.')
    if form == 'down':
        v0 = r.choice([5, 10, 15, 20]); t = r.randint(1, 6); H = v0 * t + 5 * t * t
        vend = v0 + 10 * t
        assert abs(vend ** 2 - (v0 * v0 + 20 * H)) < 1e-9
        if H > 200: return None
        fig = tower_fig(H, v0, False)
        ask = r.choice(['t', 'v'])
        body = PP('그림과 같이 높이 %s m 인 건물 꼭대기에서 공을 연직 아래로 %s의 속력으로 던졌다. 공이 %s? %s' % (num(H), U(v0, 'm/s'), '지면에 닿을 때까지 걸리는 시간은' if ask == 't' else '지면에 닿는 순간의 속력은', cond)) + FIG(fig, '56%')
        if ask == 't':
            wr = wl(t, [t + 1, t - 1, H / v0, math.sqrt(H / 5), H / (v0 + 10), 2 * t], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='중', fam='e',
                      steps=['아래 방향을 +로 하면 H = v₀t + ½gt² 이다.', '%s = %s t + 5t² 에서 t² + %s t - %s = 0' % (num(H), num(v0), num(v0 / 5), num(H / 5)), 't = %s s' % num(t)],
                      core='연직 아래로 던진 공은 처음 속력이 있는 등가속도 운동이며 H = v₀t + ½gt² 이다.', point='처음 속력이 있을 때의 낙하 시간을 구한다.')
        wr = wl(vend, [math.sqrt(20 * H), v0 + math.sqrt(20 * H), 10 * t, v0 * t + 10, vend + 5, vend - 5], 'm/s')
        return mc(body, ans(vend, 'm/s'), wr, r=r, lv='중', fam='e',
                  steps=['v² = v₀² + 2gH = %s² + 2 × 10 × %s = %s' % (num(v0), num(H), num(vend * vend)), 'v = %s m/s' % num(vend)],
                  core='시간 정보가 없으면 v² = v₀² + 2gH 로 속력을 구한다.', point='처음 속력이 있는 낙하에서 v² 공식을 쓴다.')
    if form == 'graph':
        tt = r.randint(1, 5); v0 = 10 * tt
        pts = [(0, v0), (2 * tt, -v0)]
        fig = vt_fig(pts, shade=False)
        if not fig: return None
        H = v0 * v0 / 20
        assert abs(H - 0.5 * v0 * tt) < 1e-9
        ask = r.choice(['H', 'back'])
        body = PP('그림은 지면에서 연직 위로 던져 올린 공의 속도를 시간에 따라 나타낸 것이다. 위쪽을 +방향으로 한다. 공이 올라간 최고점의 높이는? %s' % cond) + FIG(fig, '66%') if ask == 'H' else \
            PP('그림은 지면에서 연직 위로 던져 올린 공의 속도를 시간에 따라 나타낸 것이다. 위쪽을 +방향으로 한다. 공이 올라가는 동안의 가속도의 크기는? %s' % cond) + FIG(fig, '66%')
        if ask == 'H':
            wr = wl(H, [v0 * 2 * tt / 2, v0 * tt, H * 2, H / 2, v0, 5 * (2 * tt) ** 2], 'm')
            return mc(body, ans(H, 'm'), wr, r=r, lv='중', fam='f',
                      steps=['속도가 0이 되는 시각은 그래프가 0을 지나는 %s초이다(대칭).' % num(tt), '0 ~ %s초 동안 그래프 넓이 = ½ × %s × %s = %s m' % (num(tt), num(tt), num(v0), num(H))],
                      core='연직 투사의 v-t 그래프는 기울기가 -g 인 직선이고, 올라가는 구간의 넓이가 최고점의 높이이다.', point='그래프에서 속도가 0인 시각을 찾아 삼각형 넓이를 구한다.')
        a = v0 / tt
        wr = wl(a, [v0 / (2 * tt), v0, 2 * v0 / tt, a / 2, a * 2, a + 5], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='하', fam='f',
                  steps=['기울기 = (-%s - %s)/(%s - 0) = %s m/s² 이므로 크기는 %s m/s² 이다.' % (num(v0), num(v0), num(2 * tt), num(-a), num(a)), '(중력 가속도 g 와 같다.)'],
                  core='연직 투사에서 가속도는 중력 가속도 g 로 일정하다.', point='v-t 그래프의 기울기로 가속도를 구한다.')
    if form == 'two':
        v0 = r.choice([10, 20, 30, 40]); t = r.randint(1, int(v0 / 5) - 1) if v0 > 5 else 1
        H = v0 * t
        hmeet = v0 * t - 5 * t * t
        if hmeet <= 0 or H > 160: return None
        assert abs(hmeet - (H - 5 * t * t)) < 1e-9
        fig = meet_fig(H, v0)
        ask = r.choice(['t', 'h'])
        body = PP('그림과 같이 높이 %s m 의 지점에서 공 B 를 가만히 놓는 순간, 지면에서 공 A 를 연직 위로 %s의 속력으로 던졌다. 두 공이 %s? (단, 두 공은 같은 연직선 위에서 운동하며 공기 저항은 무시하고, 중력 가속도는 10 m/s²이다.)' % (num(H), U(v0, 'm/s'), '던진 후 몇 초일 때 만나는가' if ask == 't' else '만나는 지점의 지면으로부터의 높이는 얼마인가')) + FIG(fig, '56%')
        if ask == 't':
            wr = wl(t, [t + 1, t - 1, math.sqrt(H / 5), H / (2 * v0), 2 * t, H / v0 + 1.5], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='상', fam='g',
                      steps=['A 의 높이 : v₀t - 5t², B 의 높이 : H - 5t²', '두 높이가 같으므로 v₀t = H 에서 t = H/v₀ = %s/%s = %s s' % (num(H), num(v0), num(t)), '(두 공 모두 중력 가속도로 운동하므로 서로에 대한 상대 속도는 v₀ 로 일정하다.)'],
                      core='같은 가속도로 운동하는 두 물체의 상대 운동은 등속이다. 만나는 시간은 H/v₀ 이다.', point='중력의 효과가 상쇄되는 상대 운동을 이용한다.')
        wr = wl(hmeet, [H - 5 * t, H / 2, hmeet + 5, v0 * t, H - hmeet + 5, 5 * t * t, hmeet * 2], 'm')
        return mc(body, ans(hmeet, 'm'), wr, r=r, lv='상', fam='g',
                  steps=['만나는 시각 t = H/v₀ = %s/%s = %s s' % (num(H), num(v0), num(t)), 'A 의 높이 = v₀t - 5t² = %s × %s - 5 × %s² = %s m' % (num(v0), num(t), num(t), num(hmeet)), '(B 의 높이 = %s - 5 × %s² = %s m 로 확인)' % (num(H), num(t), num(H - 5 * t * t))],
                  core='두 공이 만날 때 높이가 같다. 먼저 만나는 시각을 구한 뒤 높이를 계산한다.', point='만나는 시각을 구한 뒤 그 시각의 높이를 구한다.')
    # twice
    t1 = r.randint(1, 4); t2 = t1 + r.randint(1, 5)
    v0 = 5 * (t1 + t2); h = 5 * t1 * t2
    if (t1 + t2) % 2 == 1 and False: return None
    assert abs(h - (v0 * t1 - 5 * t1 * t1)) < 1e-9 and abs(h - (v0 * t2 - 5 * t2 * t2)) < 1e-9
    ask = r.choice(['h', 'v0', 'Hmax'])
    if ask == 'h':
        body = PP('지면에서 공을 연직 위로 던졌더니 던진 후 %s와 %s에 같은 높이의 지점을 지났다. 이 지점의 지면으로부터의 높이는? %s' % (U(t1, '초'), U(t2, '초'), cond))
        wr = wl(h, [5 * t2 * t2, 5 * t1 * t1, 5 * (t1 + t2) ** 2 / 4, 5 * t1 * t2 * 2, 5 * (t2 - t1) ** 2, v0, h + 10], 'm')
        return mc(body, ans(h, 'm'), wr, r=r, lv='상', fam='h',
                  steps=['올라갈 때와 내려올 때 같은 높이를 지나는 시각의 중간이 최고점 도달 시각이다 : (%s + %s)/2 = %s s' % (num(t1), num(t2), num((t1 + t2) / 2)),
                         '처음 속력 v₀ = g × %s = %s m/s' % (num((t1 + t2) / 2), num(v0)), 'h = v₀t₁ - 5t₁² = %s × %s - 5 × %s² = %s m' % (num(v0), num(t1), num(t1), num(h))],
                  core='올라갈 때와 내려올 때 같은 높이를 지나는 두 시각의 중간 시각이 최고점 도달 시각이다.', point='시간 대칭성으로 처음 속력을 구한 뒤 높이를 계산한다.')
    if ask == 'v0':
        body = PP('지면에서 공을 연직 위로 던졌더니 던진 후 %s와 %s에 같은 높이의 지점을 지났다. 공을 던진 속력은? %s' % (U(t1, '초'), U(t2, '초'), cond))
        wr = wl(v0, [5 * t2, 10 * t2, 5 * (t2 - t1), 10 * (t1 + t2), 5 * t1 * t2, v0 + 10], 'm/s')
        return mc(body, ans(v0, 'm/s'), wr, r=r, lv='중', fam='h',
                  steps=['두 시각의 중간 (%s + %s)/2 = %s s 가 최고점 도달 시각이다.' % (num(t1), num(t2), num((t1 + t2) / 2)), 'v₀ = g t = 10 × %s = %s m/s' % (num((t1 + t2) / 2), num(v0))],
                  core='최고점 도달 시각은 같은 높이를 지나는 두 시각의 중간이다.', point='시간 대칭성으로 처음 속력을 구한다.')
    Hm = v0 * v0 / 20
    body = PP('지면에서 공을 연직 위로 던졌더니 던진 후 %s와 %s에 같은 높이의 지점을 지났다. 공이 도달하는 최고점의 높이는? %s' % (U(t1, '초'), U(t2, '초'), cond))
    wr = wl(Hm, [h, 5 * t2 * t2, 5 * t1 * t2 * 2, v0, Hm + 5, Hm * 2], 'm')
    return mc(body, ans(Hm, 'm'), wr, r=r, lv='상', fam='h',
              steps=['최고점 도달 시각 = (%s + %s)/2 = %s s' % (num(t1), num(t2), num((t1 + t2) / 2)), 'v₀ = 10 × %s = %s m/s' % (num((t1 + t2) / 2), num(v0)), 'H = v₀²/2g = %s²/20 = %s m' % (num(v0), num(Hm))],
              core='최고점 도달 시각은 같은 높이를 지나는 두 시각의 중간이며, H = v₀²/2g 이다.', point='대칭성과 최고점 높이 공식을 함께 쓴다.')


# ================================================================ ph025 (두 물체의 만남·추월)
def two_vt_fig(lines, mark=None, w=300, h=190, T_=None):
    """lines: [(pts, color, name)] 를 한 v-t 그래프에. mark: (t, v) 교점 표시."""
    allp = [p_ for ln in lines for p_ in ln[0]]
    tmax = T_ or max(t for t, _ in allp); vmax = max(v for _, v in allp)
    p = Plot(w, h, tmax * 1.12, vmax * 1.2, ml=46, mr=22, mt=16, mb=30)
    ypx = (h - p.mt - p.mb) / (vmax * 1.2); xpx = (w - p.ml - p.mr) / (tmax * 1.12)
    xt = sorted(set(t for t, _ in allp if t > 0)); yt = sorted(set(v for _, v in allp if v > 0))
    if not ticks_ok(xt + [0], xpx, 17) or not ticks_ok(yt + [0], ypx, 13): return None
    p.axes('t(s)', 'v(m/s)', xt, yt)
    for pts, c, nm in lines:
        p.pl(pts, c, 2.6)
        p.text(p.px(pts[-1][0]) + 4, p.py(pts[-1][1]) + 4, nm, 14, 'start', True, c, True)
    if mark:
        p.line(p.px(mark[0]), p.py(mark[1]), p.px(mark[0]), p.py(0), GR, 1, '4 3'); p.line(p.px(mark[0]), p.py(mark[1]), p.px(0), p.py(mark[1]), GR, 1, '4 3')
        p.circ(p.px(mark[0]), p.py(mark[1]), 3.6, RD, RD, 1)
    return p.svg()


@T('ph025')
def meet_chase(r, k):
    form = r.choice(['same', 'same', 'late', 'ahead', 'gap', 'graph', 'graph', 'toward', 'toward', 'const1', 'const2', 'const1'])
    A, B = r.choice([('자동차 A', '오토바이 B'), ('트럭 A', '자동차 B'), ('수레 A', '수레 B'), ('열차 A', '열차 B'), ('물체 A', '물체 B')])
    if form == 'same':
        v = r.choice([4, 5, 6, 8, 10, 12, 15, 20]); a = r.choice([1, 2, 2.5, 3, 4, 5]); t = 2 * v / a
        if not half(t) or t > 20: return None
        d = v * t
        assert abs(d - 0.5 * a * t * t) < 1e-9
        ask = r.choice(['t', 'd', 'vB'])
        q = {'t': '출발 후 몇 초일 때 B 가 A 를 따라잡는가?', 'd': 'B 가 A 를 따라잡는 순간 출발점으로부터의 거리는?', 'vB': 'B 가 A 를 따라잡는 순간 B 의 속력은?'}[ask]
        body = PP('직선 도로의 같은 지점에서 정지해 있던 %s가 일정한 가속도 %s로 출발하는 순간, %s가 같은 지점을 일정한 속력 %s로 같은 방향으로 지나갔다. %s' % (B, U(a, 'm/s²'), A, U(v, 'm/s'), q))
        if ask == 't':
            wr = wl(t, [v / a, t / 2, 2 * t, d / a, v, t + 2], 's')
            return mc(body, ans(t, 's'), wr, r=r, lv='중', fam='a',
                      steps=['A 의 이동 거리 = vt, B 의 이동 거리 = ½at²', '만나면 두 거리가 같다 : %s t = ½ × %s × t² 에서 t = 2v/a = %s s' % (num(v), num(a), num(t))],
                      core='같은 지점에서 출발해 만나면 이동 거리(변위)가 같다. v t = ½ a t² 에서 t = 2v/a 이다.', point='만난다 = 변위가 같다는 조건을 세운다.')
        if ask == 'd':
            wr = wl(d, [d / 2, 2 * d, v * t / 2 + 5, v * v / (2 * a), v * v / a / 2, d + v], 'm')
            return mc(body, ans(d, 'm'), wr, r=r, lv='중', fam='a',
                      steps=['만나는 시각 t = 2v/a = %s s' % num(t), '거리 = vt = %s × %s = %s m (= ½at² = %s m)' % (num(v), num(t), num(d), num(0.5 * a * t * t))],
                      core='만나는 시각을 먼저 구한 뒤 그 시각까지의 이동 거리를 구한다.', point='만나는 시각 → 이동 거리의 순서로 푼다.')
        wr = wl(2 * v, [v, 3 * v, v / 2, a * t / 2, 4 * v, 2 * v + 5], 'm/s')
        return mc(body, ans(2 * v, 'm/s'), wr, r=r, lv='중', fam='a',
                  steps=['만나는 시각 t = 2v/a = %s s' % num(t), 'B 의 속력 = at = %s × %s = %s m/s (A 속력의 2배)' % (num(a), num(t), num(a * t))],
                  core='정지에서 출발한 물체가 등속 물체를 따라잡는 순간 속력은 등속 물체의 2배이다.', point='만나는 시각의 속력을 v = at 로 구한다.')
    if form == 'late':
        v = r.choice([4, 5, 6, 8, 10, 12]); a = r.choice([1, 2, 3, 4, 5]); tau = r.randint(2, 12)
        t0 = a * tau * tau / (2 * v) - tau
        if t0 <= 0 or abs(t0 - round(t0)) > 1e-9: return None
        t0 = int(round(t0)); dist = v * (t0 + tau)
        assert abs(dist - 0.5 * a * tau * tau) < 1e-9
        ask = r.choice(['tau', 'dist'])
        body = PP('직선 도로 위의 점 P 에 정지해 있던 %s는 %s가 P 를 일정한 속력 %s로 지나간 %s 후에 일정한 가속도 %s로 같은 방향으로 출발하였다. %s' % (B, A, U(v, 'm/s'), U(t0, '초'), U(a, 'm/s²'), 'B 가 출발한 후 A 를 따라잡을 때까지 걸리는 시간은?' if ask == 'tau' else 'B 가 A 를 따라잡는 지점은 P 로부터 얼마나 떨어져 있는가?'))
        if ask == 'tau':
            wr = wl(tau, [tau + t0, tau - 1, tau + 1, 2 * v / a, tau * 2, t0 + 2 * v / a], 's')
            return mc(body, ans(tau, 's'), wr, r=r, lv='상', fam='b',
                      steps=['B 가 출발한 후 t 초 뒤 만난다고 하면 A 는 (t + %s)초 동안 움직였다.' % num(t0), 'v(t + %s) = ½at² : %s(t + %s) = %s t² 이므로 t² - %s t - %s = 0' % (num(t0), num(v), num(t0), num(a / 2), num(2 * v / a), num(2 * v * t0 / a)), 't = %s s' % num(tau)],
                      core='늦게 출발한 물체가 따라잡을 때 두 물체의 이동 거리가 같다. 각자의 운동 시간을 구분한다.', point='두 물체의 운동 시간이 다름에 유의하여 식을 세운다.')
        wr = wl(dist, [v * tau, 0.5 * a * (tau + t0) ** 2, v * t0, dist + v, v * tau * 2, dist / 2], 'm')
        return mc(body, ans(dist, 'm'), wr, r=r, lv='상', fam='b',
                  steps=['B 가 출발한 후 만날 때까지 걸린 시간을 t 라 하면 v(t + %s) = ½at² 에서 t = %s s' % (num(t0), num(tau)), '거리 = ½at² = ½ × %s × %s² = %s m (A 는 %s × %s = %s m)' % (num(a), num(tau), num(dist), num(v), num(t0 + tau), num(v * (t0 + tau)))],
                  core='만나는 지점까지의 거리는 어느 물체에서 계산해도 같다.', point='만나는 시각을 구한 뒤 거리를 구한다.')
    if form in ('ahead', 'gap'):
        v = r.choice([4, 5, 6, 8, 10]); a = r.choice([1, 2, 3, 4]); t = r.randint(3, 12)
        d = 0.5 * a * t * t - v * t
        if d <= 0 or d > 120 or not two(d): return None
        assert abs(0.5 * a * t * t - (d + v * t)) < 1e-9
        if form == 'ahead':
            ask = r.choice(['t', 'vB'])
            body = PP('직선 도로에서 정지해 있던 %s가 일정한 가속도 %s로 출발하는 순간, 같은 방향으로 %s 앞에 있던 %s가 일정한 속력 %s로 달리고 있었다. %s' % (B, U(a, 'm/s²'), U(d, 'm'), A, U(v, 'm/s'), 'B 가 A 를 따라잡는 것은 B 가 출발한 후 몇 초일 때인가?' if ask == 't' else 'B 가 A 를 따라잡는 순간 B 의 속력은?'))
            if ask == 't':
                wr = wl(t, [t + 1, t - 1, d / v, 2 * v / a, math.sqrt(2 * d / a), t * 2], 's')
                return mc(body, ans(t, 's'), wr, r=r, lv='상', fam='c',
                          steps=['출발 후 t 초에 따라잡는다면 B 의 이동 거리 = A 의 이동 거리 + %s m' % num(d), '½ × %s × t² = %s + %s t 이므로 %s t² - %s t - %s = 0' % (num(a), num(d), num(v), num(a / 2), num(v), num(d)), 't = %s s' % num(t)],
                          core='앞서 있는 물체를 따라잡을 때 B 의 이동 거리는 A 의 이동 거리에 처음 간격을 더한 값이다.', point='처음 간격을 포함하여 이동 거리 식을 세운다.')
            vb = a * t
            wr = wl(vb, [v, 2 * v, vb + v, vb / 2, a * t + a, math.sqrt(2 * a * d)], 'm/s')
            return mc(body, ans(vb, 'm/s'), wr, r=r, lv='상', fam='c',
                      steps=['따라잡는 시각 : ½ × %s × t² = %s + %s t 에서 t = %s s' % (num(a), num(d), num(v), num(t)), 'B 의 속력 = at = %s × %s = %s m/s' % (num(a), num(t), num(vb))],
                      core='따라잡는 시각을 구한 뒤 v = at 로 그 순간의 속력을 구한다.', point='먼저 시각을 구하고 속력을 계산한다.')
        tm = v / a; gmax = d + v * v / (2 * a)
        assert abs(gmax - (d + v * tm - 0.5 * a * tm * tm)) < 1e-9
        ask = r.choice(['t', 'gap'])
        body = PP('직선 도로에서 정지해 있던 %s가 일정한 가속도 %s로 출발하는 순간, 같은 방향으로 %s 앞에 있던 %s가 일정한 속력 %s로 달리고 있었다. %s' % (B, U(a, 'm/s²'), U(d, 'm'), A, U(v, 'm/s'), 'B 가 출발한 후 두 물체 사이의 거리가 최대가 되는 순간은 몇 초일 때인가?' if ask == 't' else 'B 가 A 를 따라잡기 전, 두 물체 사이의 거리의 최댓값은?'))
        if ask == 't':
            wr = wl(tm, [2 * v / a, v * a, t, tm + 1, tm / 2, d / v], 's')
            return mc(body, ans(tm, 's'), wr, r=r, lv='상', fam='d',
                      steps=['두 물체 사이의 거리는 B 의 속력이 A 의 속력보다 작을 때 커지고, 같아지는 순간 최대가 된다.', 'at = v 에서 t = v/a = %s/%s = %s s' % (num(v), num(a), num(tm))],
                      core='뒤쫓는 물체의 속력이 앞 물체의 속력과 같아지는 순간 두 물체 사이의 거리가 최대이다.', point='속력이 같아지는 순간을 찾는다.')
        wr = wl(gmax, [d, d + v * v / a, d + v * tm, v * v / (2 * a), d + v * v / (4 * a), gmax + 5], 'm')
        return mc(body, ans(gmax, 'm'), wr, r=r, lv='상', fam='d',
                  steps=['거리가 최대인 순간 t = v/a = %s s' % num(tm), 'A 는 %s m, B 는 ½at² = %s m 이동했으므로 거리 = %s + %s - %s = %s m' % (num(v * tm), num(0.5 * a * tm * tm), num(d), num(v * tm), num(0.5 * a * tm * tm), num(gmax))],
                  core='거리가 최대인 순간은 두 물체의 속력이 같을 때이다.', point='그 순간의 처음 간격과 이동 거리 차를 합한다.')
    if form == 'graph':
        vA = r.choice([4, 6, 8, 10, 12, 16]); tc = r.randint(1, 6); vB0 = r.choice([0, 0, 2, 4]) 
        if vB0 >= vA: return None
        aB = (vA - vB0) / tc
        if not half(aB): return None
        te = 2 * tc
        Aline = [(0, vA), (te + 1, vA)]; Bline = [(0, vB0), (te + 1, vB0 + aB * (te + 1))]
        if Bline[1][1] > 40: return None
        fig = two_vt_fig([(Aline, BL, 'A'), (Bline, RD, 'B')], mark=(tc, vA), T_=te + 1)
        if not fig: return None
        dist = vA * te
        assert abs(dist - (vB0 * te + 0.5 * aB * te * te)) < 1e-9
        ask = r.choice(['t', 'd'])
        body = PP('그림은 직선 도로의 같은 지점에서 동시에 같은 방향으로 출발한 물체 A, B 의 속력을 시간에 따라 나타낸 것이다. 두 물체의 그래프는 %s초일 때 만난다. %s' % (num(tc), 'B 가 A 를 따라잡는 순간은 출발 후 몇 초일 때인가?' if ask == 't' else 'B 가 A 를 따라잡는 지점은 출발점으로부터 얼마나 떨어져 있는가?')) + FIG(fig, '66%')
        if ask == 't':
            wr = wl(te, [tc, tc + 1, te + 1, te - 1, 3 * tc, tc * 1.5], 's')
            return mc(body, ans(te, 's'), wr, r=r, lv='중', fam='e',
                      steps=['따라잡으려면 두 물체의 이동 거리(그래프 넓이)가 같아야 한다.', '0 ~ %s초에서 A 의 넓이 = %s × t, B 의 넓이 = ½(%s + %s + ...)' % (num(tc), num(vA), num(vB0), num(vA)) if False else 'B 의 속력이 A 와 같아지는 %s초까지는 A 가 더 멀리 가 있고, 이후 B 가 격차를 줄여 %s초에 같아진다.' % (num(tc), num(te)),
                             'B 의 가속도 = (%s - %s)/%s = %s m/s², vt = vB0 t + ½at² 에서 t = 2(%s - %s)/%s = %s s' % (num(vA), num(vB0), num(tc), num(aB), num(vA), num(vB0), num(aB), num(te))],
                      core='속력 그래프가 만나는 시각은 속력이 같은 순간이지 만나는 순간이 아니다. 같은 점에서 출발할 때 따라잡는 시각은 그래프 교점 시각의 2배이다.', point='교점(속력 같음)과 만남(변위 같음)을 구분한다.')
        wr = wl(dist, [vA * tc, dist / 2, dist + vA, vA * (te + 1), 0.5 * vA * te, dist - vA], 'm')
        return mc(body, ans(dist, 'm'), wr, r=r, lv='중', fam='e',
                  steps=['B 가 A 를 따라잡는 시각 t = %s초 (교점 시각의 2배)' % num(te), '거리 = A 의 이동 거리 = %s × %s = %s m' % (num(vA), num(te), num(dist)), '(B : %s × %s + ½ × %s × %s² = %s m 로 확인)' % (num(vB0), num(te), num(aB), num(te), num(dist))],
                  core='같은 점에서 출발한 두 물체는 그래프의 넓이가 같아질 때 만난다.', point='만나는 시각을 구한 뒤 A 의 이동 거리를 구한다.')
    if form == 'const1':
        vA, vB = r.choice([2, 3, 4, 5, 6, 8, 10]), r.choice([2, 3, 4, 5, 6, 8, 10]); t = r.randint(2, 12)
        L = (vA + vB) * t
        if L > 200: return None
        body = PP('직선 도로 위에서 %s 떨어진 두 지점에서 %s와 %s가 서로를 향해 동시에 출발하여 각각 일정한 속력 %s, %s로 달린다. 두 물체가 만나는 것은 출발 후 몇 초일 때인가?' % (U(L, 'm'), A, B, U(vA, 'm/s'), U(vB, 'm/s')))
        wr = wl(t, [L / abs(vA - vB) if vA != vB else None, L / vA, L / vB, L / (vA * vB), t + 1, t - 1, t * 2], 's')
        return mc(body, ans(t, 's'), wr, r=r, lv='하', fam='g',
                  steps=['서로 마주 보고 달리므로 두 물체의 이동 거리의 합이 %s m 이다.' % num(L), '(%s + %s) t = %s 에서 t = %s s' % (num(vA), num(vB), num(L), num(t))],
                  core='마주 보고 등속으로 접근하는 두 물체는 상대 속력 vA + vB 로 가까워진다.', point='이동 거리의 합이 처음 거리와 같아지는 때를 구한다.')
    if form == 'const2':
        vA = r.choice([4, 5, 6, 8, 10]); dv = r.choice([1, 2, 3, 4, 5]); vB = vA + dv; t = r.randint(2, 15); d = dv * t
        if d > 120: return None
        body = PP('직선 도로에서 %s는 %s 앞에서 일정한 속력 %s로 달리고 있고, 뒤쪽의 %s는 같은 방향으로 일정한 속력 %s로 달린다. 두 물체가 동시에 위치를 확인한 순간부터 B 가 A 를 따라잡기까지 걸리는 시간은?' % (A, U(d, 'm'), U(vA, 'm/s'), B, U(vB, 'm/s')))
        wr = wl(t, [d / vB, d / vA, d / (vA + vB), t + 1, t - 1, t * 2, d / (vB * dv)], 's')
        return mc(body, ans(t, 's'), wr, r=r, lv='하', fam='h',
                  steps=['같은 방향으로 달리므로 B 는 A 에 대해 상대 속력 %s - %s = %s m/s 로 다가간다.' % (num(vB), num(vA), num(dv)), 't = 거리/상대 속력 = %s / %s = %s s' % (num(d), num(dv), num(t))],
                  core='같은 방향으로 등속 운동하는 두 물체의 상대 속력은 속력의 차이다.', point='상대 속력으로 따라잡는 시간을 구한다.')
    # toward
    vA = r.choice([2, 3, 4, 5, 6, 8, 10]); a = r.choice([1, 2, 3, 4]); t = r.randint(2, 10)
    L = vA * t + 0.5 * a * t * t
    if not two(L) or L > 200: return None
    ask = r.choice(['t', 'x'])
    body = PP('직선 도로 위에서 %s 떨어진 두 지점에서 %s와 %s가 서로를 향해 동시에 출발한다. A 는 일정한 속력 %s로 달리고, 정지해 있던 B 는 일정한 가속도 %s로 출발한다. %s' % (U(L, 'm'), A, B, U(vA, 'm/s'), U(a, 'm/s²'), '두 물체가 만나는 것은 출발 후 몇 초일 때인가?' if ask == 't' else '두 물체가 만나는 지점은 A 의 출발점으로부터 얼마나 떨어져 있는가?'))
    if ask == 't':
        wr = wl(t, [t + 1, t - 1, L / (vA + a), L / vA, math.sqrt(2 * L / a), t * 2], 's')
        return mc(body, ans(t, 's'), wr, r=r, lv='중', fam='f',
                  steps=['A 의 이동 거리 + B 의 이동 거리 = 처음 거리 : %s t + ½ × %s × t² = %s' % (num(vA), num(a), num(L)), '%s t² + %s t - %s = 0 의 양의 해 t = %s s' % (num(a / 2), num(vA), num(L), num(t))],
                  core='마주 보고 운동하는 두 물체가 만나면 두 이동 거리의 합이 처음 거리와 같다.', point='이동 거리의 합 = 처음 거리라는 조건을 세운다.')
    x = vA * t
    wr = wl(x, [L - x, 0.5 * a * t * t, L / 2, vA * t + 5, x * 2, L], 'm')
    return mc(body, ans(x, 'm'), wr, r=r, lv='중', fam='f',
              steps=['만나는 시각 : %s t + ½ × %s × t² = %s 에서 t = %s s' % (num(vA), num(a), num(L), num(t)), 'A 의 이동 거리 = %s × %s = %s m (B 는 %s m)' % (num(vA), num(t), num(x), num(L - x))],
              core='마주 보고 운동하는 두 물체가 만나면 두 이동 거리의 합이 처음 거리와 같다.', point='만나는 시각을 구한 뒤 한 물체의 이동 거리를 구한다.')


# ================================================================ ph026 (제동 거리와 안전 거리)
@T('ph026')
def stop_dist(r, k):
    ob = r.choice(['자동차', '버스', '트럭', '택시', '승용차'])
    form = r.choice(['react', 'react', 'brake', 'brake', 'stop', 'stop', 'kmh', 'tr', 'a', 'ratio', 'graph', 'graph', 'safe', 'wet'])
    v = r.choice([10, 15, 20, 25, 30]); tr = r.choice([0.4, 0.5, 0.6, 0.8, 1, 1.2, 1.5, 2]); a = r.choice([2, 2.5, 4, 5, 6, 8])
    sr = v * tr; sb = v * v / (2 * a); S = sr + sb
    if not two(S) or not two(sb) or not two(sr): return None
    if form == 'react':
        body = PP('%s이(가) %s로 달리다가 운전자가 앞에 놓인 장애물을 발견하고 %s 후에 브레이크를 밟았다. 장애물을 발견한 순간부터 브레이크를 밟기 시작할 때까지 %s이(가) 이동한 거리는? (단, 반응 시간 동안은 속력이 변하지 않는다.)' % (ob, U(v, 'm/s'), U(tr, '초'), ob))
        wr = wl(sr, [sb, S, v / tr, v * tr * 2, v + tr, 0.5 * v * tr], 'm')
        return mc(body, ans(sr, 'm'), wr, r=r, lv='하', fam='a',
                  steps=['반응 시간 동안은 등속 운동이므로 이동 거리 = 속력 × 시간', '%s × %s = %s m' % (num(v), num(tr), num(sr))],
                  core='반응 시간 동안 자동차는 등속으로 움직이며, 이때 이동한 거리가 공주 거리(반응 거리)이다.', point='반응 시간 동안은 등속 운동이다.')
    if form == 'brake':
        body = PP('%s이(가) %s로 달리다가 브레이크를 밟아 크기가 %s인 일정한 가속도로 감속하여 정지하였다. 브레이크를 밟은 순간부터 정지할 때까지 %s이(가) 이동한 거리는?' % (ob, U(v, 'm/s'), U(a, 'm/s²'), ob))
        wr = wl(sb, [v * v / a, v / a, v * v / (4 * a), sr + sb, v * (v / a), sb + 5], 'm')
        return mc(body, ans(sb, 'm'), wr, r=r, lv='하', fam='h',
                  steps=['제동 거리 s = v²/2a = %s²/(2 × %s) = %s m' % (num(v), num(a), num(sb))],
                  core='제동 거리는 s = v²/2a 이다.', point='나중 속력이 0인 감속 운동의 거리를 구한다.')
    if form == 'stop':
        body = PP('%s이(가) %s로 달리다가 운전자가 앞에 장애물을 발견하고 %s 후에 브레이크를 밟아 크기가 %s인 일정한 가속도로 감속하여 정지하였다. 장애물을 발견한 순간부터 정지할 때까지 %s이(가) 이동한 거리는?' % (ob, U(v, 'm/s'), U(tr, '초'), U(a, 'm/s²'), ob))
        assert abs(S - (v * tr + v * (v / a) - 0.5 * a * (v / a) ** 2)) < 1e-9
        wr = wl(S, [sb, sr, v * tr + v * v / a, v * (tr + v / a), sr + sb / 2, S + 5], 'm')
        return mc(body, ans(S, 'm'), wr, r=r, lv='중', fam='a',
                  steps=['공주 거리 : %s × %s = %s m' % (num(v), num(tr), num(sr)), '제동 거리 : v²/2a = %s²/(2 × %s) = %s m' % (num(v), num(a), num(sb)), '정지 거리 = %s + %s = %s m' % (num(sr), num(sb), num(S))],
                  core='정지 거리 = 공주 거리(등속, vt) + 제동 거리(v²/2a) 이다.', point='두 구간(등속 + 감속)을 나누어 더한다.')
    if form == 'kmh':
        kmh = r.choice([36, 54, 72, 90, 108]); vv = kmh / 3.6
        sr2, sb2 = vv * tr, vv * vv / (2 * a); S2 = sr2 + sb2
        if not two(S2) or not two(sb2) or not two(sr2): return None
        body = PP('시속 %s km 로 달리던 %s이(가) 위험을 발견하고 %s 후에 브레이크를 밟아 크기가 %s인 일정한 가속도로 감속하여 정지하였다. 위험을 발견한 순간부터 정지할 때까지 이동한 거리는? (단, 1 km/h = 1/3.6 m/s 이다.)' % (kmh, ob, U(tr, '초'), U(a, 'm/s²')))
        wr = wl(S2, [kmh * tr + kmh * kmh / (2 * a), sb2, kmh * tr + sb2, sr2 + kmh * kmh / (2 * a) / 3.6, S2 + 10, sr2 + sb2 * 2], 'm')
        return mc(body, ans(S2, 'm'), wr, r=r, lv='중', fam='b',
                  steps=['%s km/h = %s m/s' % (kmh, num(vv)), '공주 거리 %s × %s = %s m, 제동 거리 %s²/(2 × %s) = %s m' % (num(vv), num(tr), num(sr2), num(vv), num(a), num(sb2)), '정지 거리 = %s m' % num(S2)],
                  core='속력 단위를 m/s 로 바꾼 뒤 정지 거리 = vt + v²/2a 를 계산한다.', point='단위 환산 후 두 구간의 거리를 합한다.')
    if form == 'tr':
        body = PP('%s이(가) %s로 달리다가 운전자가 위험을 발견한 순간부터 정지할 때까지 %s를 이동하였다. 브레이크를 밟은 뒤의 감속 가속도의 크기는 %s이었다면 운전자의 반응 시간은? (단, 반응 시간 동안은 속력이 변하지 않는다.)' % (ob, U(v, 'm/s'), U(S, 'm'), U(a, 'm/s²')))
        wr = wl(tr, [S / v, sb / v, (S - sb) / v / 2, (S + sb) / v, tr + 0.5, tr * 2], 's')
        return mc(body, ans(tr, 's'), wr, r=r, lv='중', fam='c',
                  steps=['제동 거리 = v²/2a = %s²/(2 × %s) = %s m' % (num(v), num(a), num(sb)), '공주 거리 = %s - %s = %s m' % (num(S), num(sb), num(sr)), '반응 시간 = 공주 거리 / 속력 = %s / %s = %s s' % (num(sr), num(v), num(tr))],
                  core='정지 거리에서 제동 거리를 빼면 반응 시간 동안 등속으로 이동한 거리이다.', point='전체 거리에서 제동 거리를 빼서 반응 거리를 구한다.')
    if form == 'a':
        body = PP('%s이(가) %s로 달리다가 운전자가 위험을 발견하고 %s 후에 브레이크를 밟았다. 위험을 발견한 순간부터 정지할 때까지 이동한 거리가 %s일 때, 브레이크를 밟은 뒤 감속 가속도의 크기는? (단, 감속 가속도는 일정하다.)' % (ob, U(v, 'm/s'), U(tr, '초'), U(S, 'm')))
        wr = wl(a, [v * v / (2 * S), v * v / (2 * (S + sr)), v * v / S, v / tr, (v * v) / (2 * sr) if sr else None, a * 2, a + 1], 'm/s²')
        return mc(body, ans(a, 'm/s²'), wr, r=r, lv='상', fam='c',
                  steps=['반응 시간 동안의 거리 = %s × %s = %s m' % (num(v), num(tr), num(sr)), '제동 거리 = %s - %s = %s m' % (num(S), num(sr), num(sb)), 'a = v²/2s = %s²/(2 × %s) = %s m/s²' % (num(v), num(sb), num(a))],
                  core='제동 거리 = 전체 이동 거리 - 반응 거리 이고, a = v²/2s 이다.', point='반응 거리를 먼저 빼고 제동 거리로 가속도를 구한다.')
    if form == 'ratio':
        n = r.choice([2, 3, 1.5]); v2 = v * n
        sr2, sb2 = v2 * tr, v2 * v2 / (2 * a); S2 = sr2 + sb2
        if not two(S2) or not two(v2) or not two(sb2): return None
        body = PP('%s이(가) %s로 달릴 때, 위험을 발견하고 %s 후에 브레이크를 밟아 크기가 %s인 일정한 가속도로 감속하여 정지한다. 같은 조건에서 속력이 %s일 때 위험을 발견한 순간부터 정지할 때까지 이동한 거리는?' % (ob, U(v, 'm/s'), U(tr, '초'), U(a, 'm/s²'), U(v2, 'm/s')))
        wr = wl(S2, [S * n, S * n * n, sr2 + sb, sr + sb2, S2 + 10, sb2], 'm')
        return mc(body, ans(S2, 'm'), wr, r=r, lv='중', fam='d',
                  steps=['공주 거리는 속력에 비례 : %s × %s = %s m' % (num(v2), num(tr), num(sr2)), '제동 거리는 속력의 제곱에 비례 : %s²/(2 × %s) = %s m' % (num(v2), num(a), num(sb2)), '정지 거리 = %s m' % num(S2)],
                  core='속력이 n배가 되면 공주 거리는 n배, 제동 거리는 n²배가 된다.', point='공주 거리와 제동 거리가 속력에 다르게 의존함을 구분한다.')
    if form == 'graph':
        ts = tr + v / a
        pts = [(0, v), (tr, v), (ts, 0)]
        fig = vt_fig(pts)
        if not fig: return None
        assert abs(disp_area(pts) - S) < 1e-9
        body = PP('그림은 직선 도로를 달리던 %s이(가) 위험을 발견한 순간부터 정지할 때까지 속력을 시간에 따라 나타낸 것이다. 이 시간 동안 %s이(가) 이동한 거리는?' % (ob, ob)) + FIG(fig, '66%')
        wr = wl(S, [v * ts, v * ts / 2, sb, sr, 0.5 * v * tr + sb, S + v], 'm')
        return mc(body, ans(S, 'm'), wr, r=r, lv='중', fam='e',
                  steps=['그래프의 넓이가 이동 거리이다.', '직사각형(0 ~ %s초) : %s × %s = %s m' % (num(tr), num(v), num(tr), num(sr)), '삼각형(%s ~ %s초) : ½ × %s × %s = %s m' % (num(tr), num(ts), num(ts - tr), num(v), num(sb)), '합 = %s m' % num(S)],
                  core='v-t 그래프에서 등속 구간(직사각형)과 감속 구간(삼각형)의 넓이를 더하면 정지 거리이다.', point='그래프를 직사각형과 삼각형으로 나누어 넓이를 구한다.')
    if form == 'safe':
        vc = r.choice([x for x in range(2, int(v)) if x < v and (v * v - x * x) % (2 * a) == 0] or [None])
        if vc is None: return None
        x = (v * v - vc * vc) / (2 * a); d = sr + x
        if not two(d) or x <= 0: return None
        assert abs(vc ** 2 - (v * v - 2 * a * (d - sr))) < 1e-9
        body = PP('%s이(가) %s로 달리다가 앞쪽 %s 지점에 정지해 있는 장애물을 발견하였다. 운전자는 %s 후에 브레이크를 밟아 크기가 %s인 일정한 가속도로 감속하였지만 정지하지 못하고 장애물과 충돌하였다. 충돌 직전 %s의 속력은?' % (ob, U(v, 'm/s'), U(d, 'm'), U(tr, '초'), U(a, 'm/s²'), ob))
        wr = wl(vc, [v - a * (d / v - tr) if v - a * (d / v - tr) > 0 else None, v - a * tr, math.sqrt(max(v * v - 2 * a * d, 0)) or None, v / 2, vc + 2, vc - 1], 'm/s')
        return mc(body, ans(vc, 'm/s'), wr, r=r, lv='상', fam='f',
                  steps=['반응 시간 동안 이동한 거리 = %s × %s = %s m' % (num(v), num(tr), num(sr)), '브레이크를 밟은 뒤 충돌까지 거리 = %s - %s = %s m' % (num(d), num(sr), num(x)), 'v² = v₀² - 2as = %s² - 2 × %s × %s = %s 이므로 v = %s m/s' % (num(v), num(a), num(x), num(vc * vc), num(vc))],
                  core='반응 시간 동안은 등속이므로 남은 거리에서부터 v² = v₀² - 2as 를 적용한다.', point='반응 거리를 뺀 나머지 거리에서 감속 운동을 계산한다.')
    # wet
    a2 = a / 2
    if a2 < 1: return None
    sb2 = v * v / (2 * a2); diff = sb2 - sb
    if not two(diff) or not two(sb2): return None
    body = PP('%s이(가) %s로 달리다가 브레이크를 밟아 정지한다. 마른 도로에서는 감속 가속도의 크기가 %s이고, 비에 젖은 도로에서는 감속 가속도의 크기가 마른 도로의 절반이다. 젖은 도로에서의 제동 거리는 마른 도로에서보다 몇 m 더 긴가?' % (ob, U(v, 'm/s'), U(a, 'm/s²')))
    wr = wl(diff, [sb, sb2, sb / 2, 2 * sb, sb2 + sb, diff + 5], 'm')
    return mc(body, ans(diff, 'm'), wr, r=r, lv='상', fam='g',
              steps=['마른 도로 : s₁ = v²/2a = %s²/(2 × %s) = %s m' % (num(v), num(a), num(sb)), '젖은 도로 : s₂ = v²/2(a/2) = %s²/(2 × %s) = %s m' % (num(v), num(a2), num(sb2)), '차이 = %s - %s = %s m' % (num(sb2), num(sb), num(diff))],
              core='제동 거리는 감속 가속도의 크기에 반비례한다.', point='가속도가 절반이면 제동 거리는 2배가 된다.')
