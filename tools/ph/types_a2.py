# -*- coding: utf-8 -*-
"""Ⅰ-A 힘의 합성과 분해 (2) — ph002 평행사변형 법칙, ph003 세 힘의 평형, ph005 힘의 분해, ph007 도르래로 연결된 물체의 정지 조건."""
from phlib import *
import math
from math import gcd

G = 10
F1T, F2T, F3T = 'F' + sub(1), 'F' + sub(2), 'F' + sub(3)
OBJ = ['상자', '나무 블록', '수레', '공', '고리', '썰매', '쇳덩이']

SINC = {30: (1, 1, 2), 37: (3, 1, 5), 45: (1, 2, 2), 53: (4, 1, 5), 60: (1, 3, 2)}   # (분자 계수, 근호 안, 분모)
COSC = {30: (1, 3, 2), 37: (4, 1, 5), 45: (1, 2, 2), 53: (3, 1, 5), 60: (1, 1, 2)}
SINV = {30: .5, 37: .6, 45: math.sqrt(2) / 2, 53: .8, 60: math.sqrt(3) / 2}
COSV = {30: math.sqrt(3) / 2, 37: .8, 45: math.sqrt(2) / 2, 53: .6, 60: .5}
SINS = {30: '1/2', 37: '3/5', 45: '√2/2', 53: '4/5', 60: '√3/2'}
COSS = {30: '√3/2', 37: '4/5', 45: '√2/2', 53: '3/5', 60: '1/2'}


def cs(F, th, fn):
    """F sinθ(fn='s') 또는 F cosθ(fn='c') 를 (표시 문자열, 실수값) 으로. 정수 계수가 안 나오면 None."""
    n, rr, d = (SINC if fn == 's' else COSC)[th]
    if (F * n) % d: return None
    a = F * n // d
    return rad(a, rr), a * math.sqrt(rr)


def WR(right, cands, unit='', nd=2):
    """숫자 오답 목록: 정답과 같은 값·음수 제거, 4개 미만이면 보충."""
    out, seen = [], {round(float(right), 6)}
    def add(c):
        if c is None or c < 0: return
        key = round(float(c), 6)
        if key in seen: return
        seen.add(key); out.append(num(c, nd) + (' ' + unit if unit else ''))
    for c in cands: add(c)
    for c in (right * 2, right / 2, right + 1, right + 2, right - 1, right * 1.5, right + 5, right * 3):
        if len(out) >= 4: break
        add(c)
    return out


def rt(n):
    return rad(1, n)


def lab(f, x, y, s, c=INK, anchor='middle', size=12.5):
    f.text(x, y, s, size, anchor, True, c)


def arc(f, cx, cy, rr, a1, a2, c=GR, sw=1.3):
    """(cx,cy) 중심, 수학 각 a1→a2(도, 반시계) 호."""
    p1 = (cx + rr * math.cos(math.radians(a1)), cy - rr * math.sin(math.radians(a1)))
    p2 = (cx + rr * math.cos(math.radians(a2)), cy - rr * math.sin(math.radians(a2)))
    f.path('M %s %s A %s %s 0 0 0 %s %s' % (Fig._n(p1[0]), Fig._n(p1[1]), Fig._n(rr), Fig._n(rr), Fig._n(p2[0]), Fig._n(p2[1])), 'none', c, sw)


# ----------------------------------------------------------------- 공통 그림: 한 점에 작용하는 두 힘
def fig2(F1, F2, th, third=False, lmax=100, oy=140):
    f = Fig(290, 170 if not third else 185)
    ox = 145
    mx = max(F1, F2)
    S = lmax / mx
    a1, a2 = math.radians(90 - th / 2), math.radians(90 + th / 2)
    L1, L2 = S * F1, S * F2
    rr = max(12, min(30, 0.75 * min(L1, L2)))
    arc(f, ox, oy, rr, 90 - th / 2, 90 + th / 2)
    lab(f, ox, oy - rr - 5, '%d°' % th, GR)
    for F, a, L, c, nm, sd in ((F1, a1, L1, RD, 'F1', 1), (F2, a2, L2, BL, 'F2', -1)):
        x, y = ox + L * math.cos(a), oy - L * math.sin(a)
        f.arrow(ox, oy, x, y, c, 2.6)
        lab(f, x + 7 * sd, y - 3, '%s=%s N' % (nm, num(F)), c, 'start' if sd == 1 else 'end')
    if third:
        f.arrow(ox, oy, ox, oy + 62, GN, 2.6)
        lab(f, ox + 8, oy + 66, 'F3', GN, 'start')
    f.circ(ox, oy, 3.5, INK, INK)
    return f.svg()


def _pairs(th):
    c = {60: 1, 90: 0, 120: -1}[th]
    out = []
    for a in range(2, 25):
        for b in range(2, 25):
            R2 = a * a + b * b + c * a * b
            R = math.isqrt(R2)
            if R * R == R2: out.append((a, b, R))
    return out


PAIRS = {t: _pairs(t) for t in (60, 90, 120)}
COSTXT = {60: '1/2', 90: '0', 120: '-1/2'}
COSN = {60: .5, 90: 0., 120: -.5}


def law_steps(a, b, th):
    c = {60: 1, 90: 0, 120: -1}[th]
    R2 = a * a + b * b + c * a * b
    s1 = 'R² = %s² + %s² + 2%s%scosθ = %d² + %d² + 2×%d×%d×(%s)' % (F1T, F2T, F1T, F2T, a, b, a, b, COSTXT[th])
    s2 = '= %d + %d %s %d = %d' % (a * a, b * b, '+' if c >= 0 else '-', abs(c) * a * b, R2)
    return [s1, s2], R2


# ================================================================= ph002
@T('ph002')
def parallelogram(r, k):
    fam = r.choice(['a'] * 4 + ['b'] * 3 + ['c'] * 3 + ['d'] * 2 + ['e'] * 3 + ['f'] * 3)
    obj = r.choice(OBJ)
    if fam == 'a':
        th = r.choice([60, 90, 120])
        a, b, R = r.choice(PAIRS[th])
        if r.random() < .5: a, b = b, a
        st, R2 = law_steps(a, b, th)
        x, y = a + b * math.cos(math.radians(th)), b * math.sin(math.radians(th))
        assert abs(math.hypot(x, y) - R) < 1e-9 and R2 == R * R
        body = P('그림은 %s에 작용하는 두 힘 %s, %s를 나타낸 것이다. %s의 크기는 %d N, %s의 크기는 %d N이고 두 힘 사이의 각은 %d°이다. 두 힘의 합력의 크기는?' % (obj, F1T, F2T, F1T, a, F2T, b, th)) + FIG(fig2(a, b, th), '60%')
        c = {60: 1, 90: 0, 120: -1}[th]
        wr = [a + b, abs(a - b), R + 1, R - 1]
        for n in (a * a + b * b - c * a * b, a * a + b * b):
            if n > 0 and n != R2: wr.append(None); wr.append(n)
        wrongs = [U(w, 'N') for w in wr[:4] if w is not None]
        for n in (a * a + b * b - c * a * b, a * a + b * b):
            if n > 0 and n != R2: wrongs.append(rt(n) + ' N')
        wrongs += [U(R + 2, 'N'), U((a + b) / 2, 'N')]
        return mc(body, U(R, 'N'), wrongs, r=r, lv='중', fam='a',
                  steps=['두 힘 사이의 각이 %d°이므로 평행사변형 법칙(코사인 법칙)을 쓴다.' % th] + st + ['R = √%d = %d N' % (R2, R)],
                  core='두 힘의 합력 크기 R = √(F1² + F2² + 2F1F2cosθ) (θ는 두 힘 사이의 각).', point='두 힘 사이의 각에 따라 cosθ 항의 부호가 달라진다.')
    if fam == 'b':
        F = r.randint(2, 20)
        th = r.choice([60, 90, 120])
        val = {60: rad(F, 3), 90: rad(F, 2), 120: str(F)}[th]
        fl = {60: F * math.sqrt(3), 90: F * math.sqrt(2), 120: F}[th]
        assert abs(2 * F * math.cos(math.radians(th / 2)) - fl) < 1e-9
        body = P('크기가 각각 %d N으로 같은 두 힘이 한 점에 작용한다. 두 힘 사이의 각이 %d°일 때 두 힘의 합력의 크기는?' % (F, th))
        wrongs = [U(2 * F, 'N'), rad(F, 2) + ' N' if th != 90 else rad(F, 3) + ' N', rad(F, 3) + ' N' if th != 60 else rad(F, 2) + ' N', U(F, 'N') if th != 120 else rad(F, 3) + ' N', U(F / 2, 'N') if F % 2 == 0 else U(F + 1, 'N'), U(F * 2 + 2, 'N')]
        wrongs = [w for w in wrongs if w != val + ' N']
        return mc(body, val + ' N', wrongs, r=r, lv='하', fam='b', sort='shuf',
                  steps=['크기가 같은 두 힘의 합력은 R = 2Fcos(θ/2) 이다.', 'R = 2 × %d × cos%d° = %s N' % (F, th // 2, val)],
                  core='크기가 F로 같은 두 힘이 θ를 이룰 때 합력의 크기는 2Fcos(θ/2)이다.', point='사잇각 60°, 90°, 120°에서 √3F, √2F, F가 된다.')
    if fam == 'c':
        F = r.randint(2, 18)
        th = r.choice([0, 60, 90, 120, 180])
        txt = {0: str(2 * F), 60: rad(F, 3), 90: rad(F, 2), 120: str(F), 180: '0'}[th]
        if th == 180:
            q = '합력이 0이 되었다.'
        elif th == 120 and r.random() < .5:
            q = '합력의 크기가 한 힘의 크기와 같았다.'
        else:
            q = '합력의 크기가 %s N이었다.' % txt
        body = P('크기가 %d N으로 같은 두 힘을 한 점에 작용시켰더니 %s 두 힘 사이의 각은?' % (F, q))
        cand = [0, 30, 60, 90, 120, 150, 180]
        wrongs = ['%d°' % t for t in cand if t != th]
        return mc(body, '%d°' % th, wrongs, r=r, lv='중', fam='c',
                  steps=['합력의 크기 R = 2Fcos(θ/2) 이므로 cos(θ/2) = R/(2F) 이다.', {0: 'R = 2F 이므로 cos(θ/2) = 1, θ = 0°', 60: 'R = √3F 이므로 cos(θ/2) = √3/2, θ/2 = 30°, θ = 60°', 90: 'R = √2F 이므로 cos(θ/2) = √2/2, θ/2 = 45°, θ = 90°', 120: 'R = F 이므로 cos(θ/2) = 1/2, θ/2 = 60°, θ = 120°', 180: 'R = 0 이므로 cos(θ/2) = 0, θ = 180°'}[th], '따라서 사잇각은 %d°이다.' % th],
                  core='크기가 같은 두 힘의 합력 R = 2Fcos(θ/2) 에서 사잇각을 거꾸로 구할 수 있다.', point='합력과 한 힘의 크기 비로 사잇각을 판단한다.')
    if fam == 'd':
        a, b = r.randint(2, 14), r.randint(2, 14)
        if a == b: return None
        lo, hi = abs(a - b), a + b
        if r.random() < .5:
            out = [x for x in (lo - 1, lo - 2, hi + 1, hi + 2, hi + 3) if x >= 0]
            right = r.choice(out)
            ins = [x for x in range(lo, hi + 1)]
            wrongs = r.sample(ins, 4) if len(ins) >= 4 else None
            if wrongs is None: return None
            body = P('크기가 %d N, %d N인 두 힘이 한 점에 작용한다. 두 힘 사이의 각을 바꿀 때 합력의 크기가 될 수 <b>없는</b> 값은?' % (a, b))
            return mc(body, U(right, 'N'), [U(w, 'N') for w in wrongs], r=r, lv='하', fam='d',
                      steps=['합력의 크기는 같은 방향일 때 최대 %d + %d = %d N, 반대 방향일 때 최소 |%d - %d| = %d N 이다.' % (a, b, hi, a, b, lo), '따라서 합력은 %d N 이상 %d N 이하이므로 %d N은 될 수 없다.' % (lo, hi, right)],
                      core='크기가 a, b인 두 힘의 합력 R 은 |a-b| ≤ R ≤ a+b 이다.', point='합력의 최댓값과 최솟값으로 범위를 정한다.')
        mode = r.choice(['max', 'min'])
        right = hi if mode == 'max' else lo
        body = P('크기가 %d N, %d N인 두 힘이 한 점에 작용한다. 두 힘 사이의 각을 바꿀 때 합력의 크기의 %s은?' % (a, b, '최댓값' if mode == 'max' else '최솟값'))
        wrongs = WR(right, [a * b % 40 if a * b % 40 != right else None, max(a, b), min(a, b), math.hypot(a, b) if math.hypot(a, b) % 1 == 0 else None, lo if mode == 'max' else hi, right + 2], 'N')
        return mc(body, U(right, 'N'), wrongs, r=r, lv='하', fam='g', steps=['두 힘이 %s일 때 합력이 %s이다.' % ('같은 방향' if mode == 'max' else '반대 방향', '최대' if mode == 'max' else '최소'), '%s = %d N' % ('%d + %d' % (a, b) if mode == 'max' else '|%d - %d|' % (a, b), right)],
                  core='합력은 사잇각 0°에서 최대(a+b), 180°에서 최소(|a-b|)이다.', point='합력 크기의 최대·최소는 같은 방향·반대 방향일 때이다.')
    if fam == 'e':
        th = r.choice([60, 90, 120])
        a, b, R = r.choice(PAIRS[th])
        if r.random() < .5: a, b = b, a
        c = {60: 1, 90: 0, 120: -1}[th]
        assert R * R == a * a + b * b + c * a * b
        body = P('한 점에 작용하는 두 힘 %s, %s 사이의 각은 %d°이다. %s의 크기가 %d N이고 두 힘의 합력의 크기가 %d N일 때, %s의 크기는?' % (F1T, F2T, th, F1T, a, R, F2T))
        wrongs = [U(R - a, 'N'), U(R + a, 'N'), U(b + 1, 'N'), U(max(b - 1, 1), 'N'), U(a, 'N') if a != b else U(b + 2, 'N'), U(round(math.sqrt(abs(R * R - a * a))) if th != 90 else b + 3, 'N')]
        return mc(body, U(b, 'N'), wrongs, r=r, lv='상', fam='e',
                  steps=['R² = %s² + %s² + 2%s%scos%d° 에 %s=%d, R=%d 를 대입한다.' % (F1T, F2T, F1T, F2T, th, F1T, a, R),
                         '%d = %d + %s² %s %s%s 이므로 %s² %s %s%s - %d = 0 이다.' % (R * R, a * a, F2T, '+' if c >= 0 else '-', '' if c == 0 else '%d×' % a, '' if c == 0 else F2T, F2T, '+' if c > 0 else '-', '' if c == 0 else '%d×' % a, '' if c == 0 else F2T, R * R - a * a) if c != 0 else '%d = %d + %s² 이므로 %s² = %d' % (R * R, a * a, F2T, F2T, R * R - a * a),
                         '%s = %d N 이 조건을 만족한다. (%d² + %d² %s %d×%d = %d)' % (F2T, b, a, b, '+' if c >= 0 else '-', a, b, R * R) if c != 0 else '%s = √%d = %d N' % (F2T, R * R - a * a, b)],
                  core='합력 R, 한 힘, 사잇각이 주어지면 R² = F1² + F2² + 2F1F2cosθ 로 나머지 힘을 구한다.', point='식을 세운 뒤 선택지를 대입하거나 방정식을 푼다.')
    # f: 개념+수치 <보기>
    a, b = r.sample(range(3, 13), 2)
    a, b = max(a, b), min(a, b)
    hi, lo = a + b, a - b
    h90 = a * a + b * b
    S = [
        ('g1', '두 힘 사이의 각이 0°일 때 합력의 크기는 %d N이다.' % hi, True, '같은 방향이므로 %d + %d = %d N이다.' % (a, b, hi)),
        ('g1', '두 힘 사이의 각이 0°일 때 합력의 크기는 %d N이다.' % lo, False, '같은 방향이므로 합력은 두 힘의 합 %d N이다.' % hi),
        ('g2', '두 힘 사이의 각이 180°일 때 합력의 크기는 %d N이다.' % lo, True, '반대 방향이므로 %d - %d = %d N이다.' % (a, b, lo)),
        ('g2', '두 힘 사이의 각이 180°일 때 합력의 크기는 %d N이다.' % hi, False, '반대 방향이면 합력은 두 힘의 차 %d N이다.' % lo),
        ('g3', '두 힘 사이의 각이 90°일 때 합력의 크기는 %s N이다.' % rt(h90), True, '√(%d² + %d²) = √%d = %s N이다.' % (a, b, h90, rt(h90))),
        ('g3', '두 힘 사이의 각이 90°일 때 합력의 크기는 %d N이다.' % hi, False, '90°일 때는 √(%d² + %d²) = %s N이고, %d N은 0°일 때의 값이다.' % (a, b, rt(h90), hi)),
        ('g4', '두 힘 사이의 각을 0°에서 180°까지 키우면 합력의 크기는 계속 감소한다.', True, '각이 커질수록 cosθ가 작아져 합력이 작아진다.'),
        ('g4', '두 힘 사이의 각을 0°에서 180°까지 키우면 합력의 크기는 계속 증가한다.', False, '각이 커질수록 합력은 감소한다.'),
        ('g5', '합력의 크기는 %d N보다 크거나 같고 %d N보다 작거나 같다.' % (lo, hi), True, '합력의 범위는 |a-b| 이상 a+b 이하이다.'),
        ('g5', '두 힘 사이의 각을 조절하면 합력의 크기를 %d N보다 크게 만들 수 있다.' % hi, False, '합력의 최댓값은 두 힘이 같은 방향일 때의 %d N이다.' % hi),
        ('g6', '합력의 크기는 두 힘의 크기 %d N, %d N 중 큰 값보다 항상 크다.' % (a, b), False, '사잇각이 크면 합력이 %d N보다 작아질 수 있다(180°에서 %d N).' % (a, lo)),
        ('g6', '합력의 크기가 %d N보다 작아지는 경우가 있다.' % a, True, '사잇각이 크면 합력이 작아져 180°에서는 %d N이 된다.' % lo),
    ]
    groups = {}
    for s in S: groups.setdefault(s[0], []).append(s)
    gs = r.sample(sorted(groups), 3)
    stm = [r.choice(groups[g])[1:] for g in gs]
    stm = [(t, v, e) for t, v, e in stm]
    return bogi('크기가 %d N, %d N인 두 힘이 한 점에 작용한다. 두 힘 사이의 각을 바꿀 때 합력에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % (a, b), stm, r=r, ask='', lv='중', fam='f',
                core='합력의 크기는 사잇각 0°에서 최대, 180°에서 최소이며 그 사이에서는 각이 클수록 작아진다.', point='사잇각에 따른 합력의 크기 변화를 수치로 확인한다.')


# ================================================================= ph003
def fig3_perp(F1, F2, show_vals=(True, True)):
    f = Fig(300, 200)
    ox, oy = 130, 105
    S = 80 / max(F1, F2)
    f.arrow(ox, oy, ox + S * F1, oy, RD, 2.6)
    f.arrow(ox, oy, ox, oy - S * F2, BL, 2.6)
    f.arrow(ox, oy, ox - S * F1, oy + S * F2, GN, 2.6)
    lab(f, ox + S * F1 + 6, oy + 4, 'F1' + ('=%s N' % num(F1) if show_vals[0] else ''), RD, 'start')
    lab(f, ox + 8, oy - S * F2 - 4, 'F2' + ('=%s N' % num(F2) if show_vals[1] else ''), BL, 'start')
    lab(f, ox - S * F1 - 4, oy + S * F2 + 14, 'F3', GN, 'end')
    f.circ(ox, oy, 3.5, INK, INK)
    return f.svg()


def fig_two_ropes(al, mtxt):
    f = Fig(300, 175)
    cx, cy, ty = 150, 100, 22
    dx = (cy - ty) / math.tan(math.radians(al))
    f.hatch(10, ty, 280, GR, 'up') if False else None
    f.line(10, ty, 290, ty, GR, 2)
    for i in range(0, 280, 8):
        f.line(10 + i, ty, 10 + i + 5, ty - 6, GR, 1)
    f.line(cx - dx, ty, cx, cy, INK, 2)
    f.line(cx + dx, ty, cx, cy, INK, 2)
    f.line(cx, cy, cx, cy + 16, INK, 1.8)
    f.rect(cx - 26, cy + 16, 52, 34, '#cfe2f7', INK, 1.6)
    f.text(cx, cy + 38, mtxt, 13, 'middle', True)
    for sd in (-1, 1):
        px = cx + sd * dx
        a1, a2 = (0, -al) if sd == -1 else (180, 180 + al)
        # 수학 각(y 위) 기준: 줄이 아래로 향하므로 -al
        if sd == -1:
            arc(f, px, ty, 26, -al, 0)
            lab(f, px + 44, ty + 15, '%d°' % al, GR)
        else:
            arc(f, px, ty, 26, 180, 180 + al)
            lab(f, px - 44, ty + 15, '%d°' % al, GR)
    f.circ(cx, cy, 3.5, INK, INK)
    return f.svg()


def fig_ball_pull(th, mtxt):
    f = Fig(300, 190)
    ox, oy, L = 90, 20, 128
    bx, by = ox + L * math.sin(math.radians(th)), oy + L * math.cos(math.radians(th))
    f.line(30, oy, 200, oy, GR, 2)
    for i in range(0, 170, 8):
        f.line(30 + i, oy, 30 + i + 5, oy - 6, GR, 1)
    f.line(ox, oy, ox, oy + 150, GR, 1, '4 3')
    f.line(ox, oy, bx, by, INK, 2)
    f.circ(bx, by, 15, '#cfe2f7', INK, 1.8)
    f.text(bx, by + 5, mtxt, 12, 'middle', True)
    f.arrow(bx + 15, by, bx + 85, by, RD, 2.8)
    lab(f, bx + 92, by + 5, 'F', RD, 'start', 14)
    arc(f, ox, oy, 46, -90, -90 + th)
    lab(f, ox + 22, oy + 66, '%d°' % th, GR)
    return f.svg()


@T('ph003')
def three_forces(r, k):
    fam = r.choice(['a'] * 4 + ['b'] * 3 + ['c'] * 3 + ['d'] * 3 + ['e'] * 2 + ['f'] * 3)
    if fam == 'a':
        a, b, c = r.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (12, 16, 20), (15, 20, 25), (7, 24, 25), (20, 21, 29)])
        if r.random() < .5: a, b = b, a
        ask = r.choice(['F3', 'F3', 'F2'])
        assert a * a + b * b == c * c
        if ask == 'F3':
            body = P('그림은 한 점에 작용하는 세 힘 %s, %s, %s가 평형을 이루고 있는 것을 나타낸 것이다. %s과 %s는 서로 수직이고 크기는 각각 %d N, %d N이다. %s의 크기는?' % (F1T, F2T, F3T, F1T, F2T, a, b, F3T)) + FIG(fig3_perp(a, b), '62%')
            right, ex = c, [a + b, abs(a - b), max(a, b), c + 2]
            st = ['세 힘이 평형이므로 %s는 %s과 %s의 합력과 크기가 같고 방향이 반대이다.' % (F3T, F1T, F2T), '%s = √(%d² + %d²) = √%d = %d N' % (F3T, a, b, c * c, c)]
        else:
            body = P('그림은 한 점에 작용하는 세 힘이 평형을 이루고 있는 것을 나타낸 것이다. %s과 %s는 서로 수직이고, %s의 크기는 %d N, %s의 크기는 %d N이다. %s의 크기는?' % (F1T, F2T, F1T, a, F3T, c, F2T)) + FIG(fig3_perp(a, b, (True, False)), '62%')
            right, ex = b, [c - a, c + a, c, a]
            st = ['평형이므로 %s² = %s² + %s² 이다.' % (F3T, F1T, F2T), '%s = √(%d² - %d²) = √%d = %d N' % (F2T, c, a, b * b, b)]
        wrongs = [U(x, 'N') for x in ex if x != right] + [U(right + 1, 'N'), U(right + 3, 'N')]
        return mc(body, U(right, 'N'), wrongs, r=r, lv='중', fam='a', steps=st,
                  core='세 힘이 평형이면 두 힘의 합력은 나머지 한 힘과 크기가 같고 방향이 반대이다.', point='수직인 두 힘의 합력(피타고라스)을 이용한다.')
    if fam == 'b':
        al = r.choice([30, 37, 45, 53, 60])
        m = r.choice([2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20])
        W = m * G
        n, rr, d = SINC[al]
        # T = W/(2 sinα) = W d /(2 n sqrt(rr)) -> rationalize
        num_ = W * d
        den = 2 * n
        if rr == 1:
            if num_ % den: return None
            T = num_ // den; Ts = str(T); Tv = T
        else:
            # W d/(2 n √rr) = W d √rr /(2 n rr)
            if (num_) % (den * rr): return None
            Ts = rad(num_ // (den * rr), rr); Tv = num_ / (den * math.sqrt(rr))
        assert abs(2 * Tv * SINV[al] - W) < 1e-6
        ask = r.choice(['T', 'T', 'N'])
        body = P('그림과 같이 질량이 %d kg인 물체가 가벼운 두 줄에 매달려 정지해 있다. 두 줄이 천장과 이루는 각은 모두 %d°이다. 한 줄이 물체를 당기는 힘의 크기는? (단, 중력 가속도는 10 m/s²이다.)' % (m, al)) + FIG(fig_two_ropes(al, '%d kg' % m), '64%')
        wrongs = [U(W, 'N'), U(W / 2, 'N'), (rad(W // 2, 3) if W % 2 == 0 else '%s√3/2' % W) + ' N', cs(W, al, 'c')[0] + ' N' if cs(W, al, 'c') else None, cs(W, al, 's')[0] + ' N' if cs(W, al, 's') else None, U(W / (2 * COSV[al]), 'N') if (W / (2 * COSV[al])) % 1 == 0 else None]
        wrongs = [w for w in wrongs if w and w != Ts + ' N']
        return mc(body, Ts + ' N', wrongs, r=r, lv='중', fam='b', sort='shuf',
                  steps=['물체가 정지해 있으므로 연직 방향 힘의 합이 0이다.', '2T sin%d° = mg = %d × 10 = %d N' % (al, m, W), 'T = %d ÷ (2 × %s) = %s N' % (W, SINS[al], Ts)],
                  core='대칭인 두 줄에 매달린 물체는 2T sinα = mg 로 평형을 이룬다(α는 줄과 수평면이 이루는 각).', point='줄의 장력을 연직 성분으로 나누어 중력과 비교한다.')
    if fam == 'c':
        th = r.choice([37, 53, 45])
        m = r.choice([2, 3, 4, 6, 8, 9, 12])
        W = m * G
        F = {37: W * 3 / 4, 53: W * 4 / 3, 45: W}[th]
        Tn = {37: W * 5 / 4, 53: W * 5 / 3, 45: None}[th]
        if abs(F - round(F)) > 1e-9 and abs(F * 2 - round(F * 2)) > 1e-9: return None
        Ts = num(Tn) if Tn is not None else rad(W, 2)
        Tv = Tn if Tn is not None else W * math.sqrt(2)
        assert abs(math.hypot(F, W) - Tv) < 1e-9
        ask = r.choice(['F', 'T'])
        base = '그림과 같이 질량이 %d kg인 공이 가벼운 줄에 매달려 수평 방향의 힘 F를 받아 연직선과 %d°의 각을 이루며 정지해 있다. ' % (m, th)
        if ask == 'F':
            body = P(base + 'F의 크기는? (단, 중력 가속도는 10 m/s²이다.)') + FIG(fig_ball_pull(th, '%d kg' % m), '58%')
            wrongs = [U(W, 'N'), U(Tv, 'N') if Tn else rad(W, 2) + ' N', U(W / 2, 'N'), U(W * 4 / 3 if th == 37 else W * 3 / 4, 'N') if th != 45 else rad(W // 2, 2) + ' N' if W % 2 == 0 else U(W + 10, 'N'), U(W * .6 if th == 37 else W * .8, 'N') if th != 45 else U(W * 2, 'N')]
            right = num(F) + ' N'
            wrongs = [w for w in wrongs if w != right]
            st = ['줄의 장력을 T라 하면 연직 방향 : T cos%d° = mg = %d N, 수평 방향 : T sin%d° = F' % (th, W, th), 'F = mg tan%d° = %d × %s = %s N' % (th, W, {37: '3/4', 53: '4/3', 45: '1'}[th], num(F))]
            return mc(body, right, wrongs, r=r, lv='중', fam='c', steps=st, core='세 힘(중력, 장력, 수평력)이 평형이면 F = mg tanθ, T = mg/cosθ 이다.', point='장력을 수평·연직 성분으로 나누어 평형 조건을 쓴다.')
        body = P(base + '줄이 공을 당기는 힘의 크기는? (단, 중력 가속도는 10 m/s²이다.)') + FIG(fig_ball_pull(th, '%d kg' % m), '58%')
        wrongs = [U(W, 'N'), U(F, 'N'), U(W + F, 'N'), U(W * 1.5, 'N') if th != 45 else U(W * 2, 'N'), U(W * 1.2 if th == 37 else W * 1.6, 'N') if th != 45 else rad(W // 2, 2) + ' N' if W % 2 == 0 else U(W + 5, 'N')]
        wrongs = [w for w in wrongs if w != Ts + ' N']
        return mc(body, Ts + ' N', wrongs, r=r, lv='상', fam='c', sort='shuf',
                  steps=['연직 방향 : T cos%d° = mg = %d N' % (th, W), '수평 방향 : T sin%d° = F = %s N' % (th, num(F)), 'T = √(F² + (mg)²) = √(%s² + %d²) = %s N' % (num(F), W, Ts)],
                  core='줄의 장력 T 는 수평력 F 와 중력 mg 의 합력과 크기가 같다.', point='T = √(F² + (mg)²) 또는 T = mg/cosθ 로 구한다.')
    if fam == 'd':
        for _ in range(30):
            a, b, c = r.randint(2, 16), r.randint(2, 16), r.randint(2, 16)
            if a + b > c and a + c > b and b + c > a: break
        else:
            return None
        ok = (a, b, c)
        bad = []
        while len(bad) < 4:
            x, y, z = r.randint(1, 16), r.randint(1, 16), r.randint(1, 30)
            t = sorted((x, y, z))
            if t[0] + t[1] <= t[2]:
                tt = tuple(r.sample([x, y, z], 3))
                if tt not in bad: bad.append(tt)
        fmt = lambda t: '%d N, %d N, %d N' % t
        if r.random() < .6:
            body = P('한 점에 작용하는 세 힘의 크기가 각각 다음과 같을 때, 세 힘이 평형을 이룰 수 있는 경우만을 고른 것은? (단, 세 힘은 한 평면 위에 있다.)')
            return mc(body, fmt(ok), [fmt(t) for t in bad], r=r, lv='중', fam='d', sort='shuf',
                      steps=['세 힘이 평형을 이루려면 가장 큰 힘이 나머지 두 힘의 합보다 작아야 한다(힘의 삼각형이 만들어져야 함).', '%d N, %d N, %d N : %d < %d + %d 이므로 가능하다.' % (a, b, c, max(a, b, c), sorted((a, b, c))[0], sorted((a, b, c))[1])] + ['나머지는 가장 큰 힘이 다른 두 힘의 합 이상이라 평형이 될 수 없다.'],
                      core='세 힘이 평형이면 세 힘으로 닫힌 삼각형을 만들 수 있어야 한다.', point='가장 큰 힘 < 나머지 두 힘의 합 인지 확인한다.')
        goods = []
        while len(goods) < 4:
            x, y, z = r.randint(2, 16), r.randint(2, 16), r.randint(2, 16)
            if x + y > z and x + z > y and y + z > x and (x, y, z) not in goods: goods.append((x, y, z))
        body = P('한 점에 작용하는 세 힘의 크기가 각각 다음과 같을 때, 세 힘이 평형을 이룰 수 <b>없는</b> 것은? (단, 세 힘은 한 평면 위에 있다.)')
        return mc(body, fmt(bad[0]), [fmt(t) for t in goods], r=r, lv='하', fam='d', sort='shuf',
                  steps=['세 힘이 평형을 이루려면 가장 큰 힘이 나머지 두 힘의 합보다 작아야 한다.', '%d N, %d N, %d N : 가장 큰 힘 %d N ≥ %d + %d = %d 이므로 평형이 될 수 없다.' % (bad[0] + (max(bad[0]), sorted(bad[0])[0], sorted(bad[0])[1], sorted(bad[0])[0] + sorted(bad[0])[1]))],
                  core='세 힘이 평형이면 세 힘으로 닫힌 삼각형을 만들 수 있어야 한다.', point='가장 큰 힘 < 나머지 두 힘의 합 인지 확인한다.')
    if fam == 'e':
        th = r.choice([60, 120])
        a, b, R = r.choice(PAIRS[th])
        if r.random() < .5: a, b = b, a
        st, R2 = law_steps(a, b, th)
        assert R * R == R2
        body = P('그림은 한 점에 작용하는 세 힘 %s, %s, %s가 평형을 이루고 있는 것을 나타낸 것이다. %s의 크기는 %d N, %s의 크기는 %d N이고 %s과 %s 사이의 각은 %d°이다. %s의 크기는?' % (F1T, F2T, F3T, F1T, a, F2T, b, F1T, F2T, th, F3T)) + FIG(fig2(a, b, th, third=True, lmax=75, oy=92), '62%')
        c = 1 if th == 60 else -1
        wrongs = [U(a + b, 'N'), U(abs(a - b), 'N'), U(R + 1, 'N'), U(R - 1, 'N')]
        n2 = a * a + b * b - c * a * b
        if n2 > 0 and n2 != R2: wrongs.append(rt(n2) + ' N')
        wrongs.append(rt(a * a + b * b) + ' N') if a * a + b * b != R2 else None
        return mc(body, U(R, 'N'), wrongs, r=r, lv='상', fam='e',
                  steps=['평형이므로 %s의 크기는 %s과 %s의 합력의 크기와 같다.' % (F3T, F1T, F2T)] + st + ['%s = R = √%d = %d N' % (F3T, R2, R)],
                  core='세 힘이 평형이면 한 힘은 나머지 두 힘의 합력과 크기가 같고 방향이 반대이다.', point='평행사변형 법칙으로 두 힘의 합력을 구한 뒤 평형 조건을 쓴다.')
    # f: 줄 장력으로 각 구하기
    al = r.choice([30, 37, 45, 53, 60])
    m = r.choice([3, 4, 6, 8, 9, 12, 16, 18, 24])
    W = m * G
    n, rr, d = SINC[al]
    if rr == 1:
        if (W * d) % (2 * n): return None
        Ts = str((W * d) // (2 * n))
    else:
        if (W * d) % (2 * n * rr): return None
        Ts = rad((W * d) // (2 * n * rr), rr)
    body = P('질량이 %d kg인 물체가 가벼운 두 줄에 대칭으로 매달려 정지해 있다. 각 줄의 장력의 크기가 %s N일 때, 줄이 천장과 이루는 각은? (단, 중력 가속도는 10 m/s²이다.)' % (m, Ts))
    wrongs = ['%d°' % t for t in (30, 37, 45, 53, 60, 75) if t != al]
    return mc(body, '%d°' % al, wrongs, r=r, lv='중', fam='f',
              steps=['연직 방향 평형 : 2T sinα = mg = %d × 10 = %d N' % (m, W), 'sinα = %d ÷ (2 × %s) = %s' % (W, Ts, SINS[al]), '따라서 α = %d°이다.' % al],
              core='대칭인 두 줄의 장력 T 와 중력 사이에는 2T sinα = mg 가 성립한다.', point='연직 방향 평형 조건에서 삼각비를 구한 뒤 각을 찾는다.')


# ================================================================= ph005
def fig_decomp(F, th, frm):
    f = Fig(270, 175)
    ox, oy, L = 36, 148, 118
    d = (math.cos(math.radians(th)), math.sin(math.radians(th))) if frm == 'h' else (math.sin(math.radians(th)), math.cos(math.radians(th)))
    tx, ty = ox + L * d[0], oy - L * d[1]
    f.arrow(ox, oy, ox + 190, oy, GR, 1.2)
    f.arrow(ox, oy, ox, oy - 135, GR, 1.2)
    lab(f, ox + 196, oy + 4, 'x', GR, 'start'); lab(f, ox - 4, oy - 140, 'y', GR, 'end')
    f.line(tx, ty, tx, oy, GR, 1, '4 3')
    f.line(tx, ty, ox, ty, GR, 1, '4 3')
    f.arrow(ox, oy, tx, ty, RD, 2.8)
    lab(f, tx + 8, ty - 4, 'F=%s N' % num(F), RD, 'start')
    if frm == 'h':
        arc(f, ox, oy, 38, 0, th); lab(f, ox + 54, oy - 12, '%d°' % th, GR)
    else:
        arc(f, ox, oy, 38, 90 - th, 90); lab(f, ox + 15, oy - 54, '%d°' % th, GR)
    return f.svg()


def fig_pull(th, mtxt, down=False):
    f = Fig(280, 160)
    fy = 128
    f.hatch(10, fy, 260, GR)
    bx, bw, bh = 115, 62, 40
    f.rect(bx, fy - bh, bw, bh, '#cfe2f7', INK, 1.7)
    f.text(bx + bw / 2, fy - bh / 2 + 5, mtxt, 13, 'middle', True)
    if not down:
        sx, sy = bx + bw, fy - bh / 2
        ex, ey = sx + 82 * math.cos(math.radians(th)), sy - 82 * math.sin(math.radians(th))
        f.line(sx, sy, sx + 100, sy, GR, 1, '4 3')
        f.arrow(sx, sy, ex, ey, RD, 2.8)
        lab(f, ex + 6, ey - 2, 'F', RD, 'start', 14)
        arc(f, sx, sy, 40, 0, th); lab(f, sx + 56, sy - 6, '%d°' % th, GR)
    else:
        sx, sy = bx, fy - bh
        tx, ty = sx - 82 * math.cos(math.radians(th)), sy - 82 * math.sin(math.radians(th))
        f.line(sx, sy, sx - 100, sy, GR, 1, '4 3')
        f.arrow(tx, ty, sx, sy, RD, 2.8)
        lab(f, tx - 4, ty - 2, 'F', RD, 'end', 14)
        arc(f, sx, sy, 40, 180 - th, 180); lab(f, sx - 58, sy - 8, '%d°' % th, GR)
    return f.svg()


ANGF = {30: [10, 20, 40, 60, 80], 37: [10, 20, 30, 40, 50, 60], 45: [10, 20, 30, 40, 50], 53: [10, 20, 30, 40, 50, 60], 60: [10, 20, 40, 60, 80]}


def _ratio_txt(a, ra, b, rb):
    g = gcd(a, b)
    a, b = a // g, b // g
    if ra == rb: return '%d : %d' % (a, b)
    return '%s : %s' % (rad(a, ra), rad(b, rb))


@T('ph005')
def decompose(r, k):
    fam = r.choice(['a'] * 4 + ['b'] * 3 + ['c'] * 4 + ['d'] * 3 + ['e'] * 5)
    if fam == 'a':
        th = r.choice([30, 37, 45, 53, 60])
        F = r.choice(ANGF[th])
        frm = r.choice(['h', 'v'])
        c_, s_ = cs(F, th, 'c'), cs(F, th, 's')
        if not c_ or not s_: return None
        H, V = (c_, s_) if frm == 'h' else (s_, c_)
        assert abs(math.hypot(H[1], V[1]) - F) < 1e-9
        ref = '수평선(x축)' if frm == 'h' else '연직선(y축)'
        body = P('그림은 크기가 %d N인 힘 F를 나타낸 것이다. F는 %s과 %d°의 각을 이루고 있다. F의 x축 방향 성분과 y축 방향 성분의 크기를 차례대로 구한 것은?' % (F, ref, th)) + FIG(fig_decomp(F, th, frm), '60%')
        right = '%s N, %s N' % (H[0], V[0])
        wrongs = ['%s N, %s N' % (V[0], H[0]), '%s N, %s N' % (H[0], H[0]), '%s N, %s N' % (V[0], V[0]), '%s N, %s N' % (num(F), V[0]), '%s N, %s N' % (H[0], num(F))]
        wrongs = [w for w in wrongs if w != right]
        if H[0] == V[0]:
            wrongs += ['%s N, %s N' % (num(F / 2), num(F / 2)), '%s N, %s N' % (num(F), num(F))]
        st = ['x축 방향 성분 = F %s%d° = %d × %s = %s N' % ('cos' if frm == 'h' else 'sin', th, F, COSS[th] if frm == 'h' else SINS[th], H[0]),
              'y축 방향 성분 = F %s%d° = %d × %s = %s N' % ('sin' if frm == 'h' else 'cos', th, F, SINS[th] if frm == 'h' else COSS[th], V[0])]
        return mc(body, right, wrongs, r=r, lv='중', fam='a', sort='shuf', steps=st,
                  core='각 θ를 이루는 방향의 성분은 각이 붙은 쪽에 cosθ, 반대쪽에 sinθ를 곱한다.', point='각을 어느 축에서 쟀는지 확인해 sin·cos를 고른다.')
    if fam == 'b':
        th = r.choice([30, 37, 45, 53, 60])
        F = r.choice(ANGF[th])
        c_, s_ = cs(F, th, 'c'), cs(F, th, 's')
        if not c_ or not s_: return None
        which = r.choice(['수평', '연직'])
        known = c_ if which == '수평' else s_
        fn = 'cos' if which == '수평' else 'sin'
        obj = r.choice(OBJ)
        body = P('%s을(를) 수평면과 %d°의 각을 이루는 위쪽 방향으로 힘 F로 당겼다. F의 %s 성분의 크기가 %s N일 때 F의 크기는?' % (obj, th, which, known[0]))
        coefs = {30: 2, 60: 2, 45: 2, 37: 5, 53: 5}
        wrongs = [num(F * (COSV[th] if which == '연직' else SINV[th])) if False else None]
        other = s_ if which == '수평' else c_
        wr = [U(other[1], 'N') if abs(other[1] - round(other[1])) < 1e-9 else other[0] + ' N', U(known[1], 'N') if abs(known[1] - round(known[1])) < 1e-9 else known[0] + ' N', U(F * 2, 'N'), U(F / 2, 'N'), U(F + 10, 'N'), U(F - 10, 'N') if F > 10 else None]
        wr = [w for w in wr if w and w != U(F, 'N')]
        return mc(body, U(F, 'N'), wr, r=r, lv='하', fam='b',
                  steps=['%s 성분 = F %s%d° 이므로 %s = F × %s' % (which, fn, th, known[0], COSS[th] if which == '수평' else SINS[th]),
                         'F = %s ÷ %s = %d N' % (known[0], COSS[th] if which == '수평' else SINS[th], F)],
                  core='힘의 성분은 F cosθ(수평), F sinθ(연직)이므로 거꾸로 F = 성분 ÷ (cosθ 또는 sinθ) 이다.', point='성분과 각이 주어졌을 때 원래 힘의 크기를 구한다.')
    if fam == 'c':
        th = r.choice([30, 37, 45, 53, 60])
        m = r.choice([2, 3, 4, 5, 6, 8, 10])
        F = r.choice(ANGF[th])
        down = r.random() < .35
        s_, c_ = cs(F, th, 's'), cs(F, th, 'c')
        if not s_ or not c_: return None
        W = m * G
        mode = r.choice(['N', 'N', 'a'])
        base = '그림과 같이 질량 %d kg인 물체를 수평면과 %d°를 이루는 %s 방향으로 크기 %d N의 힘 F로 %s. ' % (m, th, '아래쪽' if down else '위쪽', F, '밀었더니 수평면 위에서 움직이지 않았다' if down else '당겼더니 물체가 수평면에서 떨어지지 않은 채 움직였다')
        fig = FIG(fig_pull(th, '%d kg' % m, down), '60%')
        if mode == 'N':
            Nv = W + s_[1] if down else W - s_[1]
            if Nv <= 0 or abs(Nv - round(Nv * 100) / 100) > 1e-9: return None
            if abs(s_[1] - round(s_[1])) > 1e-9: return None
            body = P(base + '수평면이 물체에 작용하는 수직 항력의 크기는? (단, 중력 가속도는 10 m/s²이다.)') + fig
            wrongs = [U(W, 'N'), U(W + s_[1] if not down else W - s_[1], 'N'), U(W - c_[1] if abs(c_[1] - round(c_[1])) < 1e-9 else W + 3, 'N'), U(W + c_[1] if abs(c_[1] - round(c_[1])) < 1e-9 else W + 7, 'N'), U(W - F if W > F else W + F, 'N')]
            return mc(body, U(Nv, 'N'), [w for w in wrongs if w != U(Nv, 'N')], r=r, lv='중', fam='c',
                      steps=['F의 연직 성분 = F sin%d° = %d × %s = %s N (%s)' % (th, F, SINS[th], s_[0], '아래쪽' if down else '위쪽'),
                             '연직 방향 힘의 평형 : N %s %s = mg = %d N' % ('-' if down else '+', s_[0], W),
                             'N = %d %s %s = %s N' % (W, '+' if down else '-', s_[0], num(Nv))],
                      core='비스듬한 힘의 연직 성분은 수직 항력을 변화시킨다(위로 당기면 감소, 아래로 밀면 증가).', point='힘을 수평·연직으로 분해해 연직 방향 평형식을 세운다.')
        # 수평 가속도(마찰 없음)
        a_ = c_[1] / m
        if abs(c_[1] - round(c_[1])) > 1e-9 or abs(a_ * 100 - round(a_ * 100)) > 1e-9 or down: return None
        base2 = '그림과 같이 마찰이 없는 수평면 위에 놓인 질량 %d kg인 물체를 수평면과 %d°를 이루는 위쪽 방향으로 크기 %d N의 힘 F로 당겼더니 물체가 수평면에서 떨어지지 않은 채 움직였다. ' % (m, th, F)
        body = P(base2 + '물체의 가속도의 크기는?') + fig
        wrongs = [U(F / m, 'm/s²') if (F / m) != a_ else None, U(s_[1] / m, 'm/s²') if abs(s_[1] / m * 100 - round(s_[1] / m * 100)) < 1e-9 else None, U(a_ * 2, 'm/s²'), U(a_ / 2, 'm/s²'), U((c_[1] - W) / m, 'm/s²') if False else None, U(c_[1], 'm/s²')]
        wrongs = [w for w in wrongs if w and w != U(a_, 'm/s²')]
        return mc(body, U(a_, 'm/s²'), wrongs, r=r, lv='상', fam='c',
                  steps=['물체를 움직이는 수평 방향의 힘 = F cos%d° = %d × %s = %s N' % (th, F, COSS[th], c_[0]), '마찰이 없으므로 알짜힘 = %s N, a = %s ÷ %d = %s m/s²' % (c_[0], c_[0], m, num(a_))],
                  core='수평 방향 운동에 기여하는 것은 힘의 수평 성분 F cosθ 뿐이다.', point='비스듬한 힘은 수평 성분만 가속에 쓰인다.')
    if fam == 'd':
        pairs = [(37, 53), (53, 37), (37, 37), (53, 53), (30, 60), (60, 30)]
        tA, tB = r.choice(pairs)
        FA, FB = r.choice([10, 20, 30, 40, 50]), r.choice([10, 20, 30, 40, 50])
        dirn = r.choice(['수평', '연직'])
        fn = 'c' if dirn == '수평' else 's'
        A, B = cs(FA, tA, fn), cs(FB, tB, fn)
        if not A or not B: return None
        ia, ib = int(round(A[1] / math.sqrt((SINC if fn == 's' else COSC)[tA][1]))), int(round(B[1] / math.sqrt((SINC if fn == 's' else COSC)[tB][1])))
        ra, rb = (SINC if fn == 's' else COSC)[tA][1], (SINC if fn == 's' else COSC)[tB][1]
        right = _ratio_txt(ia, ra, ib, rb)
        # 비교용 오답: 반대 성분, 힘만의 비, 각만의 비
        ca, cb = cs(FA, tA, 'c' if fn == 's' else 's'), cs(FB, tB, 'c' if fn == 's' else 's')
        if not ca or not cb: return None
        ra2, rb2 = (COSC if fn == 's' else SINC)[tA][1], (COSC if fn == 's' else SINC)[tB][1]
        ja, jb = int(round(ca[1] / math.sqrt(ra2))), int(round(cb[1] / math.sqrt(rb2)))
        wrongs = [_ratio_txt(ja, ra2, jb, rb2), _ratio_txt(FA, 1, FB, 1), _ratio_txt(ib, rb, ia, ra), _ratio_txt(FB, 1, FA, 1), _ratio_txt(ia + 1, ra, ib, rb), _ratio_txt(ia * 2, ra, ib, rb)]
        wrongs = [w for w in wrongs if w != right]
        body = P('수평면과 각각 %d°, %d°를 이루는 위쪽 방향으로 크기가 %d N인 힘 F%s, %d N인 힘 F%s를 물체에 작용시킨다. F%s, F%s의 %s 성분의 크기를 각각 f%s, f%s라 할 때 f%s : f%s는?' % (tA, tB, FA, sub('A'), FB, sub('B'), sub('A'), sub('B'), dirn, sub('A'), sub('B'), sub('A'), sub('B')))
        return mc(body, right, wrongs, r=r, lv='중', fam='d', sort='shuf',
                  steps=['f%s = F%s %s%d° = %d × %s = %s N' % (sub('A'), sub('A'), 'cos' if fn == 'c' else 'sin', tA, FA, (COSS if fn == 'c' else SINS)[tA], A[0]),
                         'f%s = F%s %s%d° = %d × %s = %s N' % (sub('B'), sub('B'), 'cos' if fn == 'c' else 'sin', tB, FB, (COSS if fn == 'c' else SINS)[tB], B[0]),
                         'f%s : f%s = %s N : %s N = %s' % (sub('A'), sub('B'), A[0], B[0], right)],
                  core='%s 성분은 F%s이므로 힘의 크기와 각이 모두 비에 영향을 준다.' % (dirn, 'cosθ' if fn == 'c' else 'sinθ'), point='두 힘의 성분을 각각 구한 뒤 비를 간단히 한다.')
    # e: 한 힘은 x축, 다른 힘은 비스듬 — 합력의 크기
    th = r.choice([37, 53])
    F2 = r.choice([10, 15, 20, 25, 30, 35, 40])
    c_, s_ = cs(F2, th, 'c'), cs(F2, th, 's')
    if not c_ or not s_: return None
    cx, cy = int(c_[1]), int(s_[1])
    F1 = r.randint(-20, 30)
    if F1 == 0: return None
    X, Y = cx + F1, cy
    R2 = X * X + Y * Y
    R = math.isqrt(R2)
    if R * R != R2: return None
    dirw = '+x 방향' if F1 > 0 else '-x 방향'
    body = P('xy 평면의 원점에 있는 물체에 %s으로 크기 %d N인 힘 F%s과, +x 방향과 %d°를 이루며 위로 향하는 크기 %d N인 힘 F%s가 작용한다. 두 힘의 합력의 크기는?' % (dirw, abs(F1), sub(1), th, F2, sub(2)))
    wrongs = [U(abs(F1) + F2, 'N'), U(abs(F1 - F2), 'N'), U(R + 2, 'N'), U(abs(cx - F1) , 'N') if False else None, U(math.hypot(abs(F1) + cx, cy) if (math.hypot(abs(F1) + cx, cy) % 1 == 0) else R + 3, 'N'), U(abs(X) + Y, 'N')]
    wrongs = [w for w in wrongs if w and w != U(R, 'N')]
    return mc(body, U(R, 'N'), wrongs, r=r, lv='상', fam='e',
              steps=['F%s의 성분 : x 방향 %s N, y 방향 %s N' % (sub(2), c_[0], s_[0]),
                     '합력의 x 성분 = %d %s %d = %d N, y 성분 = %d N' % (F1, '+', cx, X, Y),
                     '합력의 크기 = √(%d² + %d²) = √%d = %d N' % (X, Y, R2, R)],
              core='여러 힘의 합력은 x, y 성분을 각각 더한 뒤 피타고라스 정리로 크기를 구한다.', point='비스듬한 힘을 성분으로 나눈 뒤 같은 방향끼리 합한다.')


# ================================================================= ph007
def _rot_block(f, px, py, ang, w, h, txt, fill='#cfe2f7'):
    n = Fig._n
    f.o.append('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" stroke-width="1.6"/><text x="%s" y="%s" font-size="12.5" text-anchor="middle" font-weight="700" fill="%s" font-family="%s">%s</text></g>' % (n(ang), n(px), n(py), n(px - w / 2), n(py - h), n(w), n(h), fill, INK, n(px), n(py - h / 2 + 4.5), INK, FONT, esc(txt)))


def fig_incline_pulley(th, ta='A', tb='B', rough=False):
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
    _rot_block(f, P0[0], P0[1], -th, 38, 28, ta)
    A = (P0[0] + n[0] * 14, P0[1] + n[1] * 14)
    C = (x1 + n[0] * R + 24 * u[0], y1 + n[1] * R + 24 * u[1])
    T1 = (C[0] + n[0] * R, C[1] + n[1] * R)
    T2 = (C[0] + R, C[1])
    f.line(x1, y1, C[0], C[1], GR, 1.6)
    f.line(A[0], A[1], T1[0], T1[1], INK, 1.8)
    f.path('M %s %s A %s %s 0 0 1 %s %s' % (Fig._n(T1[0]), Fig._n(T1[1]), R, R, Fig._n(T2[0]), Fig._n(T2[1])), 'none', INK, 1.8)
    ln = 52
    f.line(T2[0], T2[1], T2[0], T2[1] + ln, INK, 1.8)
    f.rect(T2[0] - 17, T2[1] + ln, 34, 28, '#fbe3c3', INK, 1.6)
    f.text(T2[0], T2[1] + ln + 19, tb, 12.5, 'middle', True)
    f.circ(C[0], C[1], R, '#fff', INK, 1.6)
    arc(f, x0, y0, 36, 0, th)
    lab(f, x0 + 52, y0 - 8, '%d°' % th, GR)
    return f.svg()


def fig_two_inclines(t1, t2, ta='A', tb='B'):
    f = Fig(300, 185)
    R = 7
    wd = 250
    h = min(110, wd / (1 / math.tan(math.radians(t1)) + 1 / math.tan(math.radians(t2))))
    x0, y0 = 22, 172
    xa = x0 + h / math.tan(math.radians(t1))
    x1 = xa + h / math.tan(math.radians(t2))
    ya = y0 - h
    f.poly([(x0, y0), (x1, y0), (xa, ya)], '#f1f4f8', INK, 1.8)
    r1, r2 = math.radians(t1), math.radians(t2)
    n1, n2 = (-math.sin(r1), -math.cos(r1)), (math.sin(r2), -math.cos(r2))
    u1, u2 = (-math.cos(r1), math.sin(r1)), (math.cos(r2), math.sin(r2))     # Q 에서 아래로 내려가는 방향
    p1 = (xa + 14 * n1[0], ya + 14 * n1[1]); p2 = (xa + 14 * n2[0], ya + 14 * n2[1])
    # p1 + s u1 = p2 + t u2
    det = u1[0] * (-u2[1]) - u1[1] * (-u2[0])
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    s = (dx * (-u2[1]) - dy * (-u2[0])) / det
    Q = (p1[0] + s * u1[0], p1[1] + s * u1[1])
    bx, by = u1[0] + u2[0], u1[1] + u2[1]
    bl = math.hypot(bx, by); bx, by = bx / bl, by / bl
    phi = math.acos(max(-1, min(1, u1[0] * bx + u1[1] * by)))
    C = (Q[0] + bx * R / math.sin(phi), Q[1] + by * R / math.sin(phi))
    T1 = (Q[0] + u1[0] * R / math.tan(phi), Q[1] + u1[1] * R / math.tan(phi))
    T2 = (Q[0] + u2[0] * R / math.tan(phi), Q[1] + u2[1] * R / math.tan(phi))
    f.line(xa, ya, C[0], C[1], GR, 1.6)
    # 왼쪽 물체
    tl = 0.45
    PL = (x0 + tl * (xa - x0), y0 - tl * h)
    _rot_block(f, PL[0], PL[1], -t1, 36, 28, ta)
    A1 = (PL[0] + 14 * n1[0], PL[1] + 14 * n1[1])
    tr = 0.45
    PR = (x1 + tr * (xa - x1), y0 - tr * h)
    _rot_block(f, PR[0], PR[1], t2, 36, 28, tb, '#fbe3c3')
    A2 = (PR[0] + 14 * n2[0], PR[1] + 14 * n2[1])
    f.line(A1[0], A1[1], T1[0], T1[1], INK, 1.8)
    f.line(A2[0], A2[1], T2[0], T2[1], INK, 1.8)
    f.path('M %s %s A %s %s 0 0 1 %s %s' % (Fig._n(T1[0]), Fig._n(T1[1]), R, R, Fig._n(T2[0]), Fig._n(T2[1])), 'none', INK, 1.8)
    f.circ(C[0], C[1], R, '#fff', INK, 1.6)
    arc(f, x0, y0, 34, 0, t1); lab(f, x0 + 50, y0 - 8, '%d°' % t1, GR)
    arc(f, x1, y0, 34, 180 - t2, 180); lab(f, x1 - 50, y0 - 8, '%d°' % t2, GR)
    return f.svg()


def fig_movable(mtxt, fixed=False, pm=None):
    f = Fig(300, 200)
    f.line(40, 16, 270, 16, GR, 2)
    for i in range(0, 230, 8): f.line(40 + i, 16, 45 + i, 10, GR, 1)
    px, py, R = 130, 96, 15
    xl, xr = px - R, px + R
    f.line(xl, 16, xl, py, INK, 1.8)
    f.path('M %s %s A %s %s 0 0 0 %s %s' % (xl, py, R, R, xr, py), 'none', INK, 1.8)
    if not fixed:
        f.line(xr, py, xr, 52, INK, 1.8)
        f.arrow(xr, 62, xr, 30, RD, 2.8)
        lab(f, xr + 8, 38, 'F', RD, 'start', 14)
    else:
        fx, fy, fr = xr + 11, 42, 11
        f.line(xr, py, xr, fy, INK, 1.8)
        f.line(fx, 16, fx, fy, GR, 1.6)
        f.path('M %s %s A %s %s 0 0 1 %s %s' % (xr, fy, fr, fr, xr + 2 * fr, fy), 'none', INK, 1.8)
        f.circ(fx, fy, fr, 'none', INK, 1.4)
        f.line(xr + 2 * fr, fy, xr + 2 * fr, 100, INK, 1.8)
        f.arrow(xr + 2 * fr, 100, xr + 2 * fr, 134, RD, 2.8)
        lab(f, xr + 2 * fr + 8, 130, 'F', RD, 'start', 14)
    f.circ(px, py, R, '#fff', INK, 1.6)
    f.circ(px, py, 2.5, INK, INK)
    f.line(px, py, px, py + 34, INK, 1.8)
    f.rect(px - 30, py + 34, 60, 38, '#cfe2f7', INK, 1.7)
    f.text(px, py + 58, mtxt, 13, 'middle', True)
    if pm:
        f.text(px - R - 6, py + 4, pm, 11.5, 'end', True, GR)
    return f.svg()


def _dir(f_up):
    return '빗면 위 방향' if f_up else '빗면 아래 방향'


@T('ph007')
def pulley_static(r, k):
    fam = r.choice(['a'] * 5 + ['b'] * 4 + ['c'] * 3 + ['d'] * 4 + ['e'] * 3)
    if fam == 'a':
        th = r.choice([30, 37, 53])
        m1 = {30: r.choice([2, 4, 6, 8, 10, 12]), 37: r.choice([5, 10, 15, 20]), 53: r.choice([5, 10, 15, 20])}[th]
        sn = SINV[th]
        m2 = m1 * sn
        assert abs(m2 - round(m2)) < 1e-9
        m2 = int(round(m2))
        ask = r.choice(['m2', 'm2', 'm1', 'T', 'N'])
        fig = FIG(fig_incline_pulley(th), '64%')
        base = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위의 물체 A와 도르래에 연결된 물체 B가 줄로 연결되어 정지해 있다. ' % th
        gtxt = ' (단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량은 무시한다.)'
        if ask == 'm2':
            body = P(base + 'A의 질량이 %d kg일 때 B의 질량은?' % m1 + gtxt) + fig
            right, unit = m2, 'kg'
            wr = [m1, m1 * COSV[th] if abs(m1 * COSV[th] - round(m1 * COSV[th])) < 1e-9 else None, m1 / 2 if th != 30 else m1 * 2, m1 + m2 if th != 30 else None, m2 + 1, m2 * 2]
            st = ['B가 줄을 당기는 힘 = A의 중력의 빗면 방향 성분이므로 m%s g = m%s g sin%d° 이다.' % (sub('B'), sub('A'), th), 'm%s = %d × %s = %d kg' % (sub('B'), m1, SINS[th], m2)]
            pt = '정지 조건에서 B의 무게와 A의 mg sinθ 가 같음을 이용한다.'
        elif ask == 'm1':
            body = P(base + 'B의 질량이 %d kg일 때 A의 질량은?' % m2 + gtxt) + fig
            right, unit = m1, 'kg'
            wr = [m2, m2 * SINV[th] if abs(m2 * SINV[th] - round(m2 * SINV[th])) < 1e-9 else None, m2 / COSV[th] if abs(m2 / COSV[th] - round(m2 / COSV[th])) < 1e-9 else None, m1 + 2, m1 - 1 if m1 > 1 else None, m1 * 2]
            st = ['정지해 있으므로 m%s g sin%d° = m%s g 이다.' % (sub('A'), th, sub('B')), 'm%s = %d ÷ %s = %d kg' % (sub('A'), m2, SINS[th], m1)]
            pt = '정지 조건에서 B의 무게와 A의 mg sinθ 가 같음을 이용한다.'
        elif ask == 'T':
            body = P(base + 'A의 질량이 %d kg일 때 줄에 걸리는 장력의 크기는?' % m1 + gtxt) + fig
            right, unit = m2 * G, 'N'
            wr = [m1 * G, m1 * G * COSV[th], m2, m1 * G * (SINV[th] + COSV[th]), m2 * G / 2, m1 * G - m2 * G]
            wr = [w if (abs(w - round(w)) < 1e-9) else None for w in wr]
            st = ['A가 정지해 있으므로 줄의 장력 T = m%s g sin%d° = %d × 10 × %s = %d N' % (sub('A'), th, m1, SINS[th], m2 * G), '(B에서도 T = m%s g = %d × 10 = %d N 으로 같다.)' % (sub('B'), m2, m2 * G)]
            pt = '정지한 물체에서 줄의 장력은 B의 무게와 같다.'
        else:
            body = P(base + 'A의 질량이 %d kg일 때 빗면이 A에 작용하는 수직 항력의 크기는?' % m1 + gtxt) + fig
            Nv = m1 * G * COSV[th]
            if abs(Nv - round(Nv)) > 1e-9: return None
            right, unit = Nv, 'N'
            wr = [m1 * G, m2 * G, m1 * G * SINV[th], m1 * G * (COSV[th] + SINV[th]), m1 * G - m2 * G, Nv + 10]
            wr = [w if (abs(w - round(w)) < 1e-9) else None for w in wr]
            st = ['빗면에 수직인 방향의 힘은 평형이므로 N = m%s g cos%d° = %d × 10 × %s = %s N' % (sub('A'), th, m1, COSS[th], num(Nv))]
            pt = '줄은 빗면과 나란하므로 수직 방향 평형식에는 장력이 들어가지 않는다.'
        wrongs = WR(right, wr, unit)
        return mc(body, U(right, unit), wrongs, r=r, lv='하' if ask == 'm2' else '상' if ask == 'N' else '중', fam='a', steps=st,
                  core='도르래로 연결된 물체가 정지하면 줄의 장력은 매달린 물체의 무게와 같고, 빗면 위 물체에서는 T = mg sinθ 이다.', point=pt)
    if fam == 'b':
        t1, t2 = r.choice([(30, 37), (30, 53), (37, 30), (37, 53), (53, 30), (53, 37)])
        m1 = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 16, 20, 24])
        m2 = m1 * SINV[t1] / SINV[t2]
        if abs(m2 - round(m2)) > 1e-9: return None
        m2 = int(round(m2))
        assert abs(m1 * SINV[t1] - m2 * SINV[t2]) < 1e-9
        ask = r.choice(['m2', 'm2', 'T'])
        base = '그림과 같이 경사각이 각각 %d°, %d°인 마찰이 없는 두 빗면 위에 물체 A, B가 줄로 연결되어 정지해 있다. A의 질량은 %d kg이다. ' % (t1, t2, m1)
        fig = FIG(fig_two_inclines(t1, t2), '66%')
        gt = '(단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량은 무시한다.)'
        if ask == 'm2':
            body = P(base + 'B의 질량은? ' + gt) + fig
            right, unit = m2, 'kg'
            wr = [m1, m1 * SINV[t1] / COSV[t2] if abs(m1 * SINV[t1] / COSV[t2] - round(m1 * SINV[t1] / COSV[t2])) < 1e-9 else None, m1 * SINV[t2] / SINV[t1] if abs(m1 * SINV[t2] / SINV[t1] - round(m1 * SINV[t2] / SINV[t1])) < 1e-9 else None, m1 * COSV[t1] / COSV[t2] if abs(m1 * COSV[t1] / COSV[t2] - round(m1 * COSV[t1] / COSV[t2])) < 1e-9 else None, m1 * (SINV[t1] + SINV[t2]) if abs(m1 * (SINV[t1] + SINV[t2]) - round(m1 * (SINV[t1] + SINV[t2]))) < 1e-9 else None]
            st = ['줄의 장력 T 는 양쪽에서 같다 : T = m%s g sin%d° = m%s g sin%d°' % (sub('A'), t1, sub('B'), t2), '%d × %s = m%s × %s 이므로 m%s = %d kg' % (m1, SINS[t1], sub('B'), SINS[t2], sub('B'), m2)]
            pt = '두 물체 모두 mg sinθ 가 장력과 같다는 점을 이용한다.'
        else:
            T = m1 * G * SINV[t1]
            body = P(base + '줄에 걸리는 장력의 크기는? ' + gt) + fig
            right, unit = T, 'N'
            wr = [m1 * G, m2 * G, m1 * G * COSV[t1], m2 * G * COSV[t2], (m1 + m2) * G * 0.5, T + 10]
            wr = [w if abs(w - round(w)) < 1e-9 else None for w in wr]
            st = ['A가 정지해 있으므로 T = m%s g sin%d° = %d × 10 × %s = %s N' % (sub('A'), t1, m1, SINS[t1], num(T)), '(B : T = %d × 10 × %s = %s N 으로 같다.)' % (m2, SINS[t2], num(m2 * G * SINV[t2]))]
            pt = '줄의 장력은 어느 쪽 물체로 계산해도 같다.'
        wrongs = WR(right, wr, unit)
        return mc(body, U(right, unit), wrongs, r=r, lv='중', fam='b', steps=st,
                  core='도르래 양쪽 물체가 빗면에서 정지하면 m%s sinθ%s = m%s sinθ%s 이다.' % (sub('A'), sub('A'), sub('B'), sub('B')), point=pt)
    if fam == 'c':
        th = r.choice([30, 37, 53])
        m1 = r.choice([2, 4, 5, 6, 8, 10, 15, 20])
        m2 = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 12])
        W1 = m1 * G * SINV[th]
        W2 = m2 * G
        if abs(W1 - round(W1)) > 1e-9 or abs(W1 - W2) < 1e-9: return None
        f_ = abs(W2 - W1)
        up = W2 < W1   # 빗면 방향 중력 성분이 더 크면 마찰력은 빗면 위 방향
        right = '%s N, %s' % (num(f_), _dir(up))
        assert (W2 + (0 if up else 0)) is not None
        # 평형 검증: 빗면 위 방향을 +로
        net = W2 - W1 + (f_ if up else -f_)
        assert abs(net) < 1e-9
        wrongs = ['%s N, %s' % (num(f_), _dir(not up)), '%s N, %s' % (num(W1 + W2), _dir(up)), '%s N, %s' % (num(W1), _dir(up)), '%s N, %s' % (num(W2), _dir(not up)), '%s N, %s' % (num(f_ + 10), _dir(up))]
        body = P('그림과 같이 경사각이 %d°인 거친 빗면 위의 물체 A(질량 %d kg)와 도르래에 연결된 물체 B(질량 %d kg)가 줄로 연결되어 정지해 있다. A에 작용하는 마찰력의 크기와 방향을 옳게 짝지은 것은? (단, 중력 가속도는 10 m/s²이고, 줄과 도르래의 질량은 무시한다.)' % (th, m1, m2)) + FIG(fig_incline_pulley(th), '64%')
        return mc(body, right, wrongs, r=r, lv='상', fam='c', sort='shuf',
                  steps=['줄의 장력 T = B의 무게 = %d × 10 = %d N, A의 중력의 빗면 방향 성분 = %d × 10 × %s = %s N' % (m2, W2, m1, SINS[th], num(W1)),
                         ('A는 빗면 아래로 더 크게 당겨지므로 마찰력은 빗면 위 방향이다.' if up else 'A는 줄에 의해 빗면 위로 더 크게 당겨지므로 마찰력은 빗면 아래 방향이다.'),
                         '빗면 방향 평형 : %s N 이므로 f = |%s - %s| = %s N, %s' % (num(f_), num(W2), num(W1), num(f_), _dir(up))],
                  core='정지해 있는 물체의 마찰력은 빗면 방향의 다른 힘들의 합과 크기가 같고 방향이 반대이다.', point='장력과 mg sinθ 의 크기를 비교해 마찰력의 방향과 크기를 정한다.')
    if fam == 'd':
        fixed = r.random() < .5
        m = r.choice([2, 4, 6, 8, 10, 12, 16, 20])
        pmass = r.choice([0, 0, 2, 4]) if True else 0
        tot = m + pmass
        T = tot * G / 2
        Lh = r.choice([0.5, 1, 1.5, 2])
        ask = r.choice(['F', 'F', 'L', 'ceil'])
        pm = '(도르래 %d kg)' % pmass if pmass else None
        fig = FIG(fig_movable('%d kg' % m, fixed, '%d kg' % pmass if pmass else None), '60%')
        base = '그림과 같이 움직도르래%s에 질량 %d kg인 물체를 매달고 줄을 %s 당겨 정지 상태를 유지하고 있다. ' % (' 와 고정 도르래' if fixed else '', m, '아래로' if fixed else '위로')
        if pmass: base += '움직도르래의 질량은 %d kg이고 ' % pmass
        base += '줄의 질량과 마찰은 무시한다. '
        gt = '(단, 중력 가속도는 10 m/s²이다.)'
        if ask == 'F':
            body = P(base + '줄을 당기는 힘 F의 크기는? ' + gt) + fig
            right, unit = T, 'N'
            wr = [tot * G, tot * G / 4, m * G if pmass else (m * G) / 4, T + 10, T * 1.5, m * G / 2 if pmass else T + 5]
            st = ['움직도르래와 물체를 받치는 줄은 2가닥이고 장력은 모두 F 이다.', '2F = (m + m%s) g = (%d + %d) × 10 = %d N' % ('도르래', m, pmass, tot * G), 'F = %s N' % num(T)]
            pt = '움직도르래는 힘을 반으로 줄이지만 줄을 당기는 거리는 2배가 된다.'
        elif ask == 'ceil':
            if fixed: return None
            body = P(base + '천장에 고정된 줄의 끝이 천장에 작용하는 힘의 크기는? ' + gt) + fig
            right, unit = T, 'N'
            wr = [tot * G, tot * G / 4, T * 2 + 10, T + 10, m * G if pmass else T * 3]
            st = ['줄의 장력은 어디서나 F 로 같고, 2F = (m + m도르래) g = %d N 이므로 F = %s N' % (tot * G, num(T)), '천장에 연결된 줄 끝은 장력과 같은 %s N 의 힘으로 천장을 당긴다.' % num(T)]
            pt = '한 줄에 걸리는 장력은 같다는 점을 이용한다.'
        else:
            body = P(base + '물체를 %s m 끌어올리려면 줄을 몇 m 당겨야 하는가?' % num(Lh)) + fig
            right, unit = 2 * Lh, 'm'
            wr = [Lh, Lh / 2, 4 * Lh, 3 * Lh, 2 * Lh + 1]
            st = ['움직도르래를 받치는 줄이 2가닥이므로 물체가 h 올라가면 줄은 2h 당겨야 한다.', '2 × %s = %s m' % (num(Lh), num(2 * Lh))]
            pt = '움직도르래에서 힘은 1/2, 이동 거리는 2배이다.'
        wrongs = WR(right, wr, unit)
        return mc(body, U(right, unit), wrongs, r=r, lv='중' if (pmass or ask == 'ceil') else '하', fam='d', steps=st,
                  core='움직도르래를 쓰면 힘은 1/2 로 줄고 줄을 당기는 거리는 2배가 된다(일의 이득은 없다).', point=pt)
    # e: 각도 구하기
    k_ = r.choice([1, 2, 3, 4, 5, 6])
    th, (a, b) = r.choice([(30, (2, 1)), (37, (5, 3)), (53, (5, 4))])
    m1, m2 = a * k_, b * k_
    assert abs(m2 / m1 - SINV[th]) < 1e-9
    body = P('빗면 위의 물체 A(질량 %d kg)와 도르래에 매달린 물체 B(질량 %d kg)가 줄로 연결되어 마찰이 없는 빗면 위에서 정지해 있다. 빗면의 경사각은? (단, 줄과 도르래의 질량은 무시한다.)' % (m1, m2)) + FIG(fig_incline_pulley(th, 'A', 'B').replace('%d°' % th, '?'), '60%')
    wrongs = ['%d°' % t for t in (30, 37, 45, 53, 60) if t != th]
    return mc(body, '%d°' % th, wrongs, r=r, lv='중', fam='e',
              steps=['정지 조건 : m%s g = m%s g sinθ 이므로 sinθ = m%s ÷ m%s = %d ÷ %d = %s' % (sub('B'), sub('A'), sub('B'), sub('A'), m2, m1, SINS[th]), '따라서 θ = %d°이다.' % th],
              core='줄로 연결된 물체가 빗면에서 정지하면 sinθ = (매달린 물체의 질량) ÷ (빗면 위 물체의 질량) 이다.', point='질량비로 sinθ 를 구하고 각을 찾는다.')
