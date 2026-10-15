# -*- coding: utf-8 -*-
"""Ⅱ-A 열역학 제1법칙 (ph065~ph076) 생성기.  이상 기체: U ∝ T ∝ PV, W = PΔV, Q = ΔU + W."""
from phlib import *
import math
from fractions import Fraction

GAM = 5.0 / 3.0   # 단열 곡선(PV^γ = 일정) 모양용. 단원자 분자 이상 기체
UP, DN, ZE = '⊕', '⊖', '0'


# ============================================================ 공통 도구
def sgn(x, eps=1e-7):
    return UP if x > eps else (DN if x < -eps else ZE)

def sj(x, unit='J'):
    """부호 있는 값 문자열: +300 J / −300 J / 0 J"""
    if abs(x) < 1e-9: return '0 ' + unit
    return ('+' if x > 0 else '−') + num(abs(x)) + ' ' + unit

def mco(body, right, wrongs, *, steps, core='', point='', lv='중', fam='a', r=None, ref=None):
    """선택지를 주어진 순서(오답 4개를 r 로 뽑아 정답과 함께 고정 순서)로 놓는 mc. wrongs 는 정답 아닌 후보."""
    seen = {re.sub(r'\s+', '', plain(right))}
    ws = []
    for w in wrongs:
        k = re.sub(r'\s+', '', plain(w))
        if k in seen: continue
        seen.add(k); ws.append(w)
    if len(ws) < 4: return None
    return mc(body, right, ws, steps=steps, core=core, point=point, lv=lv, fam=fam, sort='shuf', r=r, ref=ref)

def mc_list(body, options, ans_idx, *, steps, core='', point='', lv='중', fam='a', ref=None):
    """선택지 5개를 순서 그대로 쓰는 문항(예: (가)~(마), 표 번호)."""
    assert len(options) == 5 and 0 <= ans_idx < 5
    return Item(body=body, opts=list(options), ans=ans_idx + 1, steps=steps, core=core, point=point, lv=lv, fam=fam, vertical=None, ref=ref)

def fr_str(x):
    """Fraction -> '3/2' 형태 문자열(정수면 그대로)."""
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else '%d/%d' % (x.numerator, x.denominator)

def ratio_str(a, b):
    a, b = Fraction(a), Fraction(b)
    L = a.denominator * b.denominator // math.gcd(a.denominator, b.denominator)
    x, y = int(a * L), int(b * L)
    g = math.gcd(x, y)
    return '%d : %d' % (x // g, y // g)

def pick_stmts(r, bank, n=3):
    """bank: (문장, 참거짓, 풀이문, 그룹). 그룹이 서로 다른 n개를 뽑는다."""
    for _ in range(50):
        sel = r.sample(bank, n)
        if len({s[3] for s in sel}) == n:
            return [(s[0], s[1], s[2]) for s in sel]
    return None


# ============================================================ 실린더 그림
def _cyl(f, x, yb, w, H, h, heat=None, wt=0, ins=False, fixed=False, tag='', dim=None, ndots=None, dotc=BL):
    """실린더+피스톤. x:왼쪽, yb:바닥 y, w:폭, H:벽 높이, h:기체 높이(피스톤 아랫면까지)."""
    yt = yb - h
    f.rect(x + 1, yt, w - 2, h, '#e8f1fb', 'none', 0)
    nd = ndots if ndots is not None else int(w * h / 330) + 3
    for i in range(nd):
        px = x + 7 + ((i * 37 + 11) % 97) / 97.0 * (w - 14)
        py = yt + 7 + ((i * 61 + 5) % 89) / 89.0 * max(h - 14, 1)
        f.circ(px, py, 2.4, dotc, 'none', 0)
    col, sw = (GR, 4.5) if ins else (INK, 2.4)
    f.line(x, yb - H, x, yb, col, sw)
    f.line(x + w, yb - H, x + w, yb, col, sw)
    f.line(x - sw / 2, yb, x + w + sw / 2, yb, col, sw)
    f.rect(x + 2, yt - 8, w - 4, 8, '#9aa7b8', INK, 1.4)
    f.line(x + w / 2, yt - 8, x + w / 2, yb - H - 6, INK, 2)
    f.line(x + w / 2 - 9, yb - H - 6, x + w / 2 + 9, yb - H - 6, INK, 2.4)
    if wt:
        for i in range(wt):
            f.rect(x + 8 + i * ((w - 16) / wt), yt - 8 - 9, (w - 16) / wt - 3, 9, '#cdd5e0', INK, 1.1)
    if fixed:
        f.rect(x + w / 2 - w * 0.35, yt - 16, 6, 8, INK, INK, 1)
        f.rect(x + w / 2 + w * 0.35 - 6, yt - 16, 6, 8, INK, INK, 1)
    if heat == 'in':
        f.arrow(x + w / 2, yb + 30, x + w / 2, yb + 5, RD, 2.6)
        f.text(x + w / 2 + 10, yb + 24, 'Q', 13, 'start', True, RD, True)
    elif heat == 'out':
        f.arrow(x + w / 2, yb + 5, x + w / 2, yb + 30, BL, 2.6)
        f.text(x + w / 2 + 10, yb + 24, 'Q', 13, 'start', True, BL, True)
    if ins:
        f.text(x + w / 2, yb + 22, '단열', 12, 'middle', True, GR)
    if dim:
        xx = x + w + 12
        f.arrow(xx, yt + 1, xx, yb - 1, GR, 1.1)
        f.arrow(xx, yb - 1, xx, yt + 1, GR, 1.1)
        f.text(xx + 5, (yt + yb) / 2 + 5, dim, 12.5, 'start', True, INK)
    if tag:
        f.text(x + w / 2, yb - H - 14, tag, 12.5, 'middle', True, GR)


def cyl_pair(h1, h2, d1='', d2='', heat=None, t1='', t2='', ins=False, fixed=False, wt=0, hmax=None):
    """처음/나중 두 실린더. h1,h2: 기체 높이(상대값 0~1)."""
    f = Fig(300, 168)
    H = 92
    for (x, hh, d, t) in ((26, h1, d1, t1), (186, h2, d2, t2)):
        _cyl(f, x, 124, 62, H, 12 + 66 * hh, heat=heat, wt=wt, ins=ins, fixed=fixed, tag=t, dim=d)
    f.arrow(130, 76, 168, 76, INK, 2.4)
    return f.svg()


def cyl_one(hh, dim='', heat=None, ins=False, fixed=False, wt=0, tag='', side=None):
    f = Fig(210, 168)
    _cyl(f, 52, 124, 70, 92, 12 + 66 * hh, heat=heat, wt=wt, ins=ins, fixed=fixed, tag=tag, dim=dim)
    return f.svg()


# ============================================================ P-V 그래프
class Sch:
    """눈금 단위 체계: 격자 한 칸 = (pstep, vstep). J = 한 칸 넓이당 일(J)."""
    def __init__(self, pl, vl, pf, vf, pstep, vstep, note):
        self.pl, self.vl, self.pf, self.vf, self.pstep, self.vstep, self.note = pl, vl, pf, vf, pstep, vstep, note
        self.J = pstep * vstep * pf * vf * 100.0     # (기압·L → 100 J)
        assert abs(self.J - round(self.J)) < 1e-9
        self.J = int(round(self.J))

def rand_sch(r, pmax_step=2, vmax_step=2):
    i = r.randrange(4)
    ps = r.choice([1, 1, 2][:pmax_step + 1])
    vs = r.choice([1, 1, 2][:vmax_step + 1])
    if i == 0: return Sch('P (기압)', 'V (L)', 1, 1, ps, vs, '1기압 = 1.0×10⁵ Pa, 1 L = 1.0×10⁻³ m³')
    if i == 1: return Sch('P (10⁵ Pa)', 'V (10⁻³ m³)', 1, 1, ps, vs, '')
    if i == 2: return Sch('P (kPa)', 'V (L)', 0.01, 1, 100 * ps, vs, '1 L = 1.0×10⁻³ m³')
    return Sch('P (10⁵ Pa)', 'V (L)', 1, 1, ps, vs, '1 L = 1.0×10⁻³ m³')

def unit_note(sc):
    return (' (단, ' + sc.note + '이다.)') if sc.note else ''

def vol_str(sc, v):
    return num(v * sc.vstep) + ' ' + sc.vl.split('(')[1][:-1]
def pre_str(sc, p):
    return num(p * sc.pstep) + ' ' + sc.pl.split('(')[1][:-1]


def curve_pts(kind, a, b, n=48):
    """a=(V,P) → b=(V,P). 'L' 직선, 'I' 등온(PV=일정), 'A' 단열(PV^γ=일정)."""
    (va, pa), (vb, pb) = a, b
    if kind == 'L':
        return [(va + (vb - va) * i / n, pa + (pb - pa) * i / n) for i in range(n + 1)]
    if kind == 'I':
        assert abs(pa * va - pb * vb) < 1e-6 * max(1, pa * va), 'iso'
        return [(va + (vb - va) * i / n, pa * va / (va + (vb - va) * i / n)) for i in range(n + 1)]
    if kind == 'A':
        assert abs(pa * va ** GAM - pb * vb ** GAM) < 1e-6 * pa * va ** GAM, 'adi'
        return [(va + (vb - va) * i / n, pa * (va / (va + (vb - va) * i / n)) ** GAM) for i in range(n + 1)]
    raise ValueError(kind)


def seg_energy(kind, a, b):
    """단원자 이상 기체로 본 한 구간의 (ΔU, W, Q) — PV 단위(기압·L 등 '그림 단위'). 교차 검증용."""
    (va, pa), (vb, pb) = a, b
    dU = 1.5 * (pb * vb - pa * va)
    if kind == 'L': W = (vb - va) * (pa + pb) / 2.0
    elif kind == 'I': W = pa * va * math.log(vb / va)
    else: W = 1.5 * (pa * va - pb * vb)
    return dU, W, dU + W


def pv_fig(sc, vmax, pmax, states, segs, numbered=True, grid=True, guides=(), w=300, h=228, colors=None, lab_off=None, arrows=True, nolabel=False):
    """states: {이름: (V,P)}  segs: [(이름1, 이름2, kind, color)]  — 격자 좌표(칸 단위)."""
    ml = 52 if numbered else 30
    p = Plot(w, h, vmax + 0.45, pmax + 0.5, ml=ml, mr=16, mt=28, mb=34)
    if numbered:
        p.axes('', '', xticks=list(range(0, vmax + 1)), yticks=list(range(0, pmax + 1)), grid=grid,
               xfmt=lambda t: num(t * sc.vstep), yfmt=lambda t: num(t * sc.pstep))
        p.text(w - 14, h - 5, sc.vl, 12.5, 'end', True, GR)
        p.text(ml + 8, 14, sc.pl, 12.5, 'start', True, GR)
    else:
        p.axes('', '', xticks=(), yticks=(), grid=False)
        p.text(w - 14, h - 14, 'V', 14, 'end', True, GR, True)
        p.text(ml + 8, 16, 'P', 14, 'start', True, GR, True)
        p.text(ml - 8, h - 21, 'O', 12, 'end', False, GR)
    for nm in guides:
        v, pp = states[nm]
        p.dash_to_axes(v, pp)
    for (n1, n2, kind, col) in segs:
        pts = curve_pts(kind, states[n1], states[n2])
        p.pl(pts, col, 2.6)
        if arrows:
            i = len(pts) // 2
            x1, y1 = p.px(pts[i - 1][0]), p.py(pts[i - 1][1])
            x2, y2 = p.px(pts[i][0]), p.py(pts[i][1])
            p._head(x1, y1, x2 + (x2 - x1) * 0.2, y2 + (y2 - y1) * 0.2, col, 2.2, 9.5)
    cx = sum(v for v, _ in states.values()) / len(states)
    cy = sum(pp for _, pp in states.values()) / len(states)
    if not nolabel:
        for nm, (v, pp) in states.items():
            p.circ(p.px(v), p.py(pp), 3.6, INK, INK, 1)
            dx, dy = (lab_off or {}).get(nm, (None, None))
            if dx is None:
                ox, oy = p.px(v) - p.px(cx), p.py(pp) - p.py(cy)
                ln = math.hypot(ox, oy) or 1
                dx, dy = 13 * ox / ln, 13 * oy / ln + 5
            p.text(p.px(v) + dx, p.py(pp) + dy, nm, 14.5, 'middle', True, INK, True)
    return p.svg()


# ============================================================ 정성적 과정(숫자 없는 P-V)
PROC = {   # kind: (이름, 팽창/증가 쪽 부호, 반대)
    'isobaric': '등압', 'isochoric': '등적', 'isothermal': '등온', 'adiabatic': '단열'}

def proc_end(kind, a, f):
    v, p = a
    if kind == 'isobaric': return (v * f, p)
    if kind == 'isochoric': return (v, p * f)
    if kind == 'isothermal': return (v * f, p / f)
    return (v * f, p * f ** (-GAM))

def proc_draw_kind(kind):
    return {'isobaric': 'L', 'isochoric': 'L', 'isothermal': 'I', 'adiabatic': 'A'}[kind]

def proc_name(kind, f):
    if kind == 'isobaric': return '등압 팽창' if f > 1 else '등압 압축'
    if kind == 'isochoric': return '등적 가열(압력 증가)' if f > 1 else '등적 냉각(압력 감소)'
    if kind == 'isothermal': return '등온 팽창' if f > 1 else '등온 압축'
    return '단열 팽창' if f > 1 else '단열 압축'

def proc_short(kind, f):
    if kind == 'isobaric': return '등압 팽창' if f > 1 else '등압 압축'
    if kind == 'isochoric': return '등적 가열' if f > 1 else '등적 냉각'
    if kind == 'isothermal': return '등온 팽창' if f > 1 else '등온 압축'
    return '단열 팽창' if f > 1 else '단열 압축'

def proc_signs(kind, f):
    """규칙으로 정한 (ΔU, W, Q) 부호."""
    up = f > 1
    if kind == 'isobaric': return (UP, UP, UP) if up else (DN, DN, DN)
    if kind == 'isochoric': return (UP, ZE, UP) if up else (DN, ZE, DN)
    if kind == 'isothermal': return (ZE, UP, UP) if up else (ZE, DN, DN)
    return (DN, UP, ZE) if up else (UP, DN, ZE)

def check_signs(kind, a, b, f):
    """수치로 계산한 부호가 규칙과 같은지 assert."""
    dU, W, Q = seg_energy(proc_draw_kind(kind), a, b)
    rule = proc_signs(kind, f)
    got = (sgn(dU, 1e-6), sgn(W, 1e-6), sgn(Q, 1e-6))
    assert got == rule, (kind, f, got, rule)
    return rule

def rand_path(r, kinds_n=2, vlim=(1.0, 9.0), plim=(1.0, 8.0), allow=None, start=None):
    """서로 다른 종류의 과정을 이어 붙인 경로. [(kind, f, a, b), ...]. 못 만들면 None."""
    allow = allow or ['isobaric', 'isochoric', 'isothermal', 'adiabatic']
    a = start or (r.uniform(2.5, 5.5), r.uniform(3.0, 5.5))
    out, last = [], None
    for _ in range(kinds_n):
        kind = r.choice([k for k in allow if k != last])
        f = r.choice([1.6, 1.8, 2.0, 2.2]) if r.random() < 0.5 else r.choice([1 / 1.6, 1 / 1.8, 1 / 2.0, 1 / 2.2])
        b = proc_end(kind, a, f)
        if not (vlim[0] <= b[0] <= vlim[1] and plim[0] <= b[1] <= plim[1]): return None
        if kind == 'adiabatic' and abs(b[1] - a[1]) < 0.8: return None
        if kind == 'isothermal' and abs(b[1] - a[1]) < 0.8: return None
        check_signs(kind, a, b, f)
        out.append((kind, f, a, b))
        a, last = b, kind
    return out


def pv_qual(path, names='ABCD', colors=None, w=270, h=210):
    """숫자 없는 P-V 경로 그림."""
    states = {names[0]: path[0][2]}
    for i, (kind, f, a, b) in enumerate(path):
        states[names[i + 1]] = b
    segs = [(names[i], names[i + 1], proc_draw_kind(path[i][0]), (colors or [BL, RD, GN])[i % 3]) for i in range(len(path))]
    vs = [v for v, _ in states.values()]
    ps = [p_ for _, p_ in states.values()]
    return pv_fig(None, 9, 8, states, segs, numbered=False, grid=False, w=w, h=h)



# ============================================================ ph065 이상 기체의 내부 에너지
def _dots_fig(boxes):
    """boxes: [(이름, 점 개수, 온도 문자열)]. 점 하나 = 분자 N₀개."""
    f = Fig(300, 150)
    n = len(boxes)
    wbox = 104
    gap = (300 - n * wbox) / (n + 1)
    for i, (nm, nd, tt) in enumerate(boxes):
        x = gap + i * (wbox + gap)
        f.rect(x, 22, wbox, 80, '#f4f8fd', INK, 2)
        for j in range(nd):
            px = x + 12 + ((j * 41 + 7) % 83) / 83.0 * (wbox - 24)
            py = 22 + 12 + ((j * 29 + 3) % 71) / 71.0 * 56
            f.circ(px, py, 3.6, BL, 'none', 0)
        f.text(x + wbox / 2, 16, nm, 14, 'middle', True, INK, True)
        f.text(x + wbox / 2, 124, tt, 13, 'middle', True, RD)
    f.text(150, 144, '● 1개 = 분자 N₀개', 11.5, 'middle', False, GR)
    return f.svg()


_B65 = [
    ('이상 기체의 내부 에너지는 분자들의 운동 에너지의 총합이다.', True, '이상 기체는 분자 사이의 힘이 없으므로 분자 퍼텐셜 에너지가 없고, 내부 에너지는 분자의 운동 에너지의 합이다.', 'def'),
    ('분자 수가 일정할 때 이상 기체의 내부 에너지는 절대 온도에 비례한다.', True, 'U ∝ NT 이므로 N이 일정하면 U ∝ T이다.', 'prop'),
    ('이상 기체의 내부 에너지는 압력에만 의해 결정된다.', False, '내부 에너지는 분자 수와 절대 온도로 결정된다. 압력만으로는 정해지지 않는다.', 'onlyP'),
    ('이상 기체의 온도가 27 °C에서 54 °C로 높아지면 내부 에너지는 2배가 된다.', False, '절대 온도는 300 K에서 327 K로 약 1.09배가 되므로 내부 에너지도 약 1.09배이다. 섭씨온도의 비를 쓰면 안 된다.', 'celsius'),
    ('분자 수가 일정한 이상 기체의 절대 온도가 2배가 되면 내부 에너지도 2배가 된다.', True, 'U ∝ T 이다.', 'double'),
    ('온도가 같은 같은 종류의 이상 기체에서 분자 수가 2배이면 내부 에너지도 2배이다.', True, 'U ∝ NT 에서 T가 같으면 U ∝ N이다.', 'Nprop'),
    ('이상 기체의 부피가 커지면 내부 에너지는 항상 증가한다.', False, '등온 팽창에서는 온도가 일정하므로 부피가 커져도 내부 에너지가 변하지 않는다.', 'vol'),
    ('이상 기체가 등온 과정을 거치면 내부 에너지는 변하지 않는다.', True, '온도가 일정하고 분자 수가 일정하면 U가 일정하다.', 'iso'),
    ('이상 기체 분자들은 서로 끌어당기는 힘에 의한 퍼텐셜 에너지를 가진다.', False, '이상 기체는 분자 사이의 힘을 무시하므로 분자 퍼텐셜 에너지가 없다.', 'pot'),
    ('이상 기체의 온도가 높아지면 분자의 평균 운동 에너지가 증가한다.', True, '절대 온도는 분자의 평균 운동 에너지에 비례한다.', 'avg'),
    ('온도가 같으면 분자 수가 달라도 이상 기체의 내부 에너지는 같다.', False, 'U ∝ NT 이므로 온도가 같아도 분자 수가 다르면 U가 다르다.', 'sameT'),
    ('분자 수가 일정한 이상 기체에서 PV가 변하지 않으면 내부 에너지도 변하지 않는다.', True, 'PV ∝ T 이므로 PV가 일정하면 T가 일정하고 U도 일정하다.', 'PV'),
    ('이상 기체의 내부 에너지는 섭씨온도에 비례한다.', False, '내부 에너지는 절대 온도(K)에 비례한다.', 'celsius2'),
    ('기체를 담은 용기 전체가 운동하면 그 운동 에너지도 기체의 내부 에너지에 포함된다.', False, '내부 에너지는 용기에 대한 분자들의 무질서한 운동 에너지만을 말한다.', 'cont'),
    ('분자 수가 일정할 때 내부 에너지의 변화량은 온도 변화에 의해서만 결정된다.', True, 'ΔU ∝ ΔT 이다.', 'dU'),
    ('분자 수가 일정한 이상 기체의 압력이 2배가 되면 내부 에너지는 항상 2배가 된다.', False, '부피도 변할 수 있으므로 PV가 2배라는 보장이 없다. 온도가 2배가 될 때만 U가 2배이다.', 'P2'),
    ('같은 온도의 같은 종류 기체 A(분자 수 N)와 B(분자 수 3N) 중 B의 내부 에너지가 더 크다.', True, 'T가 같으면 U ∝ N 이므로 분자 수가 더 많은 B가 더 크다.', 'cmp'),
    ('이상 기체의 온도가 내려가면 내부 에너지는 감소한다.', True, 'U ∝ T 이다.', 'down'),
    ('열을 흡수한 이상 기체의 내부 에너지는 항상 증가한다.', False, '기체가 흡수한 열보다 더 많은 일을 외부에 하면 내부 에너지가 감소할 수 있다. (등온 팽창에서는 변화 없음)', 'heat'),
    ('분자 수가 일정한 이상 기체에서 T가 1/2배가 되면 내부 에너지도 1/2배가 된다.', True, 'U ∝ T 이다.', 'half'),
]

_TC = [-73, -23, 27, 77, 127, 177, 227, 327]   # 섭씨 → K = +273 (200~600 K)

@T('ph065')
def g065(r, k):
    form = r.choice(['ratio', 'dots', 'dots', 'temp', 'temp', 'mixT', 'bogi', 'bogi', 'chain'])
    if form == 'ratio':
        NA, NB = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4, 6])
        TA, TB = r.choice([150, 200, 300, 400, 600]), r.choice([150, 200, 300, 400, 600])
        ua, ub = NA * TA, NB * TB
        if ua == ub: return None
        right = ratio_str(ua, ub)
        body = P('같은 종류의 이상 기체 A, B의 분자 수와 절대 온도가 표와 같다. 단, N%s는 상수이다.' % sub(0)) + \
            table(['기체', '분자 수', '절대 온도(K)'], [['A', '%sN%s' % (NA if NA > 1 else '', sub(0)), TA], ['B', '%sN%s' % (NB if NB > 1 else '', sub(0)), TB]]) + \
            P('A와 B의 내부 에너지를 각각 U%s, U%s라 할 때 U%s : U%s는?' % (sub('A'), sub('B'), sub('A'), sub('B')))
        wr = [ratio_str(ub, ua), ratio_str(NA, NB), ratio_str(TA, TB), ratio_str(NA * NA * TA, NB * NB * TB), ratio_str(NA * TB, NB * TA), ratio_str(NB * TA, NA * TB)]
        return mc(body, right, wr, r=r, lv='중', fam='a', sort='shuf',
                  steps=['이상 기체의 내부 에너지는 U ∝ NT 이다.', 'U%s : U%s = (%d × %d) : (%d × %d) = %d : %d = %s' % (sub('A'), sub('B'), NA, TA, NB, TB, ua, ub, right)],
                  core='이상 기체의 내부 에너지는 분자 수와 절대 온도의 곱에 비례한다(U ∝ NT).', point='분자 수와 절대 온도를 모두 반영해 내부 에너지를 비교한다.')
    if form == 'dots':
        nA, nB = r.randint(2, 8), r.randint(2, 8)
        TA, TB = r.choice([100, 200, 300, 400, 600]), r.choice([100, 200, 300, 400, 600])
        ua, ub = nA * TA, nB * TB
        if ua == ub or nA == nB and TA == TB: return None
        ask = r.choice(['AB', 'BA'])
        fig = FIG(_dots_fig([('A', nA, '%d K' % TA), ('B', nB, '%d K' % TB)]), '62%')
        if ask == 'AB':
            right = ratio_str(ua, ub); wr = [ratio_str(ub, ua), ratio_str(nA, nB), ratio_str(TA, TB), ratio_str(nA * TB, nB * TA), ratio_str(nA + TA, nB + TB)]
            q = 'U%s : U%s' % (sub('A'), sub('B'))
        else:
            right = ratio_str(ub, ua); wr = [ratio_str(ua, ub), ratio_str(nB, nA), ratio_str(TB, TA), ratio_str(nB * TA, nA * TB), ratio_str(nB + TB, nA + TA)]
            q = 'U%s : U%s' % (sub('B'), sub('A'))
        body = P('그림은 부피가 같은 두 용기 A, B에 같은 종류의 이상 기체가 들어 있는 모습을 모형으로 나타낸 것이다. 점 1개는 분자 N%s개를 뜻하며, 각 용기 아래에 절대 온도가 적혀 있다. 내부 에너지를 각각 U%s, U%s라 할 때 %s는?' % (sub(0), sub('A'), sub('B'), q)) + fig
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                  steps=['점의 개수가 분자 수에 비례한다. A : %d개, B : %d개.' % (nA, nB), 'U ∝ NT 이므로 U%s : U%s = (%d × %d) : (%d × %d) = %d : %d' % (sub('A'), sub('B'), nA, TA, nB, TB, ua, ub),
                         '따라서 %s = %s' % (q, right)],
                  core='U ∝ NT. 모형의 점 개수로 분자 수를 읽고 온도와 곱해 비교한다.', point='그림에서 분자 수를 세어 U ∝ NT 로 비교한다.')
    if form == 'temp':
        t1, t2 = r.sample(_TC, 2)
        T1, T2 = t1 + 273, t2 + 273
        g = math.gcd(T1, T2)
        U1 = (T1 // g) * r.choice([10, 20, 30, 50, 100])
        U2 = Fraction(U1 * T2, T1)
        if U2.denominator != 1: return None
        U2 = int(U2)
        what = r.choice(['U2', 'dU'])
        body = P('분자 수가 일정한 이상 기체의 온도가 %d °C일 때 내부 에너지는 %d J이다. 이 기체의 온도를 %d °C로 바꾸었을 때 %s는? (단, 0 °C = 273 K이다.)' % (t1, U1, t2, '내부 에너지' if what == 'U2' else '내부 에너지의 변화량'))
        if what == 'U2':
            right = '%d J' % U2
            wr = ['%d J' % (U1 * t2 / t1) if t1 and (U1 * t2) % t1 == 0 else '%d J' % (U1 + (t2 - t1)), '%d J' % (U1 * T1 // T2) if (U1 * T1) % T2 == 0 else '%d J' % (U1 + 100), '%d J' % abs(U2 - U1), '%d J' % (U1 + (t2 - t1)), '%d J' % (2 * U2), '%d J' % (U2 // 2 + 10)]
        else:
            d = U2 - U1
            if d == 0: return None
            right = ('%d J 증가' if d > 0 else '%d J 감소') % abs(d)
            wr = [('%d J 증가' if d < 0 else '%d J 감소') % abs(d), '%d J 증가' % U2, '%d J 감소' % U1, '%d J 증가' % abs(U1 * t2 // t1 - U1) if t1 and t2 != t1 else '%d J 증가' % (abs(d) + 20),
                  '%d J 증가' % (abs(d) + U1), '%d J 감소' % (abs(d) + 40)]
        return mc(body, right, wr, r=r, lv='중' if what == 'U2' else '상', fam='c', sort='shuf',
                  steps=['절대 온도로 바꾸면 T%s = %d K, T%s = %d K 이다.' % (sub(1), T1, sub(2), T2), '분자 수가 일정하므로 U ∝ T : U%s = %d × %d/%d = %d J' % (sub(2), U1, T2, T1, U2)] + (['ΔU = %d − %d = %d J' % (U2, U1, d)] if what == 'dU' else []),
                  core='내부 에너지는 섭씨온도가 아닌 절대 온도에 비례한다.', point='섭씨온도를 켈빈으로 바꾼 뒤 U ∝ T 를 쓴다.')
    if form == 'mixT':
        NA, NB = r.choice([1, 2, 3]), r.choice([1, 2, 3, 4])
        TA, TB = r.choice([200, 300, 400, 500, 600, 700]), r.choice([200, 300, 400, 500, 600, 700])
        if TA == TB: return None
        s = NA * TA + NB * TB
        if s % (NA + NB): return None
        Tf = s // (NA + NB)
        body = P('단열된 용기가 가는 관과 밸브로 연결된 두 부분 A, B로 나뉘어 있다. A에는 분자 수 %sN%s, 절대 온도 %d K인 이상 기체가, B에는 같은 종류의 이상 기체가 분자 수 %sN%s, 절대 온도 %d K로 들어 있다. 밸브를 열어 충분한 시간이 지난 후 열평형에 도달했을 때 기체의 절대 온도는? (단, 외부와의 열 출입과 일은 없고, 기체는 서로 반응하지 않는다.)' % (NA if NA > 1 else '', sub(0), TA, NB if NB > 1 else '', sub(0), TB))
        wr = [(TA + TB) // 2, max(TA, TB), min(TA, TB), (TA * NA + TB * NB) // (NA + NB) + 50, (TA + TB + 100) // 2 if (TA + TB) % 2 == 0 else TA, Tf + 100, Tf - 50]
        return mc(body, '%d K' % Tf, ['%d K' % w for w in wr], r=r, lv='상', fam='d',
                  steps=['외부와 열·일의 교환이 없으므로 전체 내부 에너지가 보존된다 : U ∝ NT 의 합이 일정하다.', '(%d × %d) + (%d × %d) = (%d + %d) × T' % (NA, TA, NB, TB, NA, NB), 'T = %d / %d = %d K' % (s, NA + NB, Tf)],
                  core='고립된 기체의 내부 에너지 총합은 보존되며 U ∝ NT 이다.', point='분자 수 가중 평균으로 나중 온도를 구한다.')
    if form == 'chain':
        t1 = r.choice([-73, 27, 127, 327])
        T1 = t1 + 273
        mult = r.choice([2, 3, Fraction(3, 2), Fraction(1, 2), Fraction(1, 3), 4])
        T2 = T1 * mult
        if Fraction(T2).denominator != 1: return None
        T2 = int(T2)
        nmul = r.choice([1, 2, 3])
        if nmul == 1: return None
        ratio = Fraction(T2, T1) * nmul
        right = fr_str(ratio) + '배'
        body = P('분자 수가 N인 이상 기체의 온도가 %d °C이다. 이 기체를 %d K으로 바꾼 뒤 분자 수를 %d배로 늘려(같은 온도 유지) 나중 내부 에너지가 처음의 몇 배가 되는지 구하시오. (단, 0 °C = 273 K이다.)' % (t1, T2, nmul))
        wr = [fr_str(Fraction(T2, T1)) + '배', fr_str(Fraction(T2, T1 - 273 if t1 == 27 else T1) * nmul) + '배' if t1 != 27 else fr_str(Fraction(T2, t1) * nmul) + '배', fr_str(ratio * 2) + '배', fr_str(ratio / 2) + '배', fr_str(Fraction(T1, T2) * nmul) + '배', fr_str(ratio + 1) + '배']
        return mc(body, right, wr, r=r, lv='상', fam='e', sort='shuf',
                  steps=['처음 : T%s = %d + 273 = %d K, 분자 수 N' % (sub(1), t1, T1), '나중 : T%s = %d K, 분자 수 %dN' % (sub(2), T2, nmul), 'U ∝ NT 이므로 U%s / U%s = (%d × %d) / (1 × %d) = %s' % (sub(2), sub(1), nmul, T2, T1, fr_str(ratio))],
                  core='U ∝ NT. 분자 수와 절대 온도의 변화를 곱해 배율을 구한다.', point='N과 T의 변화 배율을 곱한다.')
    # bogi
    stm = pick_stmts(r, _B65)
    return bogi('이상 기체의 내부 에너지에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv='하', fam='f',
                core='이상 기체의 내부 에너지는 분자 운동 에너지의 합이며 분자 수와 절대 온도의 곱에 비례한다.', point='내부 에너지가 온도·분자 수에만 의존함을 이해한다.')


# ============================================================ ph066 기체가 하는 일 W = PΔV
@T('ph066')
def g066(r, k):
    form = r.choice(['a', 'a', 'b', 'c', 'd', 'e', 'g', 'h'])
    if form == 'a':   # 등압 팽창 일 계산(단위 변환)
        mode = r.choice(['atm', 'kPa', 'Pa'])
        V1, V2 = sorted(r.sample([1, 2, 3, 4, 5, 6, 8, 10, 12], 2))
        if mode == 'atm':
            p = r.choice([1, 2, 3, 4, 5]); pstr = '%d기압(= %d.0×10%s Pa)' % (p, p, sup(5)); Pa = p * 1e5
        elif mode == 'kPa':
            p = r.choice([50, 100, 150, 200, 300]); pstr = '%d kPa' % p; Pa = p * 1e3
        else:
            p = r.choice([2, 3, 4, 5, 6]); pstr = '%d.0×10%s Pa' % (p, sup(5)); Pa = p * 1e5
        W = Pa * (V2 - V1) * 1e-3
        assert abs(W - int(round(W))) < 1e-6
        W = int(round(W))
        exp_ = r.choice(['L', 'L', 'm'])
        if exp_ == 'L':
            vtxt = '%d L에서 %d L' % (V1, V2); vsmall = '%d L' % V1
        else:
            vtxt = '%s m%s에서 %s m%s' % (num(V1 * 1e-3), sup(3), num(V2 * 1e-3), sup(3)); vsmall = ''
        fig = FIG(cyl_pair((V1) / V2 * 0.9 + 0.1, 1.0, 'V%s' % sub(1), 'V%s' % sub(2), heat='in', t1='처음', t2='나중'), '62%')
        body = P('그림과 같이 실린더 속 이상 기체가 압력 %s로 일정하게 유지되면서 부피가 %s로 팽창하였다. 이 과정에서 기체가 외부에 한 일은? (단, 1 L = 1.0×10%s m%s이다.)' % (pstr, vtxt, sup(-3), sup(3))) + fig
        wr = [W * 1000, W // 1000 if W >= 1000 else W / 1000.0, Pa * V2 * 1e-3, Pa * V1 * 1e-3, W // 2, W * 2, Pa * (V2 - V1)]
        wr = [num(w) + ' J' for w in wr]
        return mc(body, num(W) + ' J', wr, r=r, lv='중', fam='a',
                  steps=['압력이 일정하므로 W = PΔV 이다.', 'P = %s Pa, ΔV = (%d − %d) × 10%s = %s m%s' % (num(Pa), V2, V1, '⁻³', num((V2 - V1) * 1e-3), '³'), 'W = %s × %s = %s J' % (num(Pa), num((V2 - V1) * 1e-3), num(W))],
                  core='압력이 일정할 때 기체가 한 일 W = PΔV (Pa·m³ = J).', point='부피의 단위를 m³로 바꾸어 W = PΔV 를 계산한다.')
    if form == 'b':    # 일이 주어질 때 ΔV 또는 P 구하기
        p = r.choice([1, 2, 3, 4, 5]); dV = r.choice([1, 2, 3, 4, 5, 6, 8])
        W = p * 1e5 * dV * 1e-3
        ask = r.choice(['dV', 'P'])
        if ask == 'dV':
            body = P('압력이 %d.0×10%s Pa로 일정한 이상 기체가 팽창하면서 외부에 %s J의 일을 하였다. 기체의 부피 증가량은?' % (p, sup(5), num(W))) + \
                FIG(cyl_pair(0.4, 0.9, 'V', 'V+ΔV', heat='in', t1='처음', t2='나중'), '58%')
            right = '%d L' % dV
            wr = ['%d L' % (dV * 10), '%s L' % num(dV / 10.0), '%s L' % num(dV * 2), '%s L' % num(dV / 2.0), '%d L' % (dV + 2), '%d L' % (dV * 100)]
            st = ['W = PΔV 에서 ΔV = W/P = %s / (%d.0×10⁵) = %s m³' % (num(W), p, num(dV * 1e-3)), 'ΔV = %s m³ = %d L 이다.' % (num(dV * 1e-3), dV)]
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=st, core='W = PΔV 에서 ΔV = W/P.', point='일과 압력으로 부피 변화량을 구한다.')
        body = P('실린더 속 이상 기체가 압력이 일정하게 유지되면서 부피가 %d L 증가하는 동안 외부에 %s J의 일을 하였다. 이 기체의 압력은? (단, 1 L = 1.0×10%s m%s이다.)' % (dV, num(W), sup(-3), sup(3))) + \
            FIG(cyl_pair(0.4, 0.9, 'V', 'V+%dL' % dV, heat='in', t1='처음', t2='나중'), '58%')
        right = '%d.0×10%s Pa' % (p, sup(5))
        wr = ['%d.0×10%s Pa' % (p, sup(2)), '%d.0×10%s Pa' % (p, sup(8)), '%s×10%s Pa' % (num(p / 2.0), sup(5)), '%d.0×10%s Pa' % (p * 2, sup(5)), '%d.0×10%s Pa' % (p, sup(4)), '%d.0×10%s Pa' % (p, sup(6))]
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                  steps=['ΔV = %d L = %s m³ 이다.' % (dV, num(dV * 1e-3)), 'P = W/ΔV = %s / %s = %d.0×10⁵ Pa' % (num(W), num(dV * 1e-3), p)],
                  core='W = PΔV 에서 P = W/ΔV.', point='단위를 SI로 바꾸어 압력을 구한다.')
    if form == 'c':    # 압축: 기체가 한 일은 음수
        p = r.choice([1, 2, 3, 4]); V1, V2 = sorted(r.sample([2, 3, 4, 5, 6, 8, 9], 2), reverse=True)
        W = -p * 1e5 * (V1 - V2) * 1e-3
        fig = FIG(cyl_pair(1.0, (V2 / V1) * 0.9 + 0.1, 'V%s' % sub(1), 'V%s' % sub(2), heat='out', t1='처음', t2='나중'), '62%')
        body = P('실린더 속 이상 기체가 압력 %d.0×10%s Pa로 일정하게 유지되면서 부피가 %d L에서 %d L로 압축되었다. 이 과정에서 기체가 한 일은? (단, 1 L = 1.0×10%s m%s이며, 기체가 외부에 하는 일을 +로 한다.)' % (p, sup(5), V1, V2, sup(-3), sup(3))) + fig
        mag = abs(W)
        wr = ['+%s J' % num(mag), '+%s J' % num(mag / 2), '−%s J' % num(mag * 2), '−%s J' % num(mag * 1000), '−%s J' % num(p * 1e5 * V2 * 1e-3), '+%s J' % num(p * 1e5 * V2 * 1e-3), '0']
        return mc(body, '−%s J' % num(mag), wr, r=r, lv='중', fam='c', sort='shuf',
                  steps=['W = PΔV = %d.0×10⁵ × (%d − %d) × 10⁻³' % (p, V2, V1), '압축이므로 ΔV < 0 이고 W = −%s J 이다. (기체가 외부로부터 일을 받는다.)' % num(mag)],
                  core='압축 과정에서 기체가 한 일은 음(−)이다. 부피가 줄면 ΔV < 0.', point='ΔV의 부호로 일의 부호를 판단한다.')
    if form == 'd':    # 단면적과 피스톤 이동 거리, 또는 추의 무게로 압력 결정
        A = r.choice([20, 25, 40, 50, 100]); d = r.choice([2, 4, 5, 10, 20])
        with_m = r.random() < 0.55
        if with_m:
            m = r.choice([2, 4, 5, 10, 20])
            Pg = 1.0e5 + m * 10 / (A * 1e-4)
            W = Pg * A * 1e-4 * d * 1e-2
            if abs(W - round(W * 4) / 4.0) > 1e-6: return None
            body = P('그림과 같이 단면적 %d cm², 질량 %d kg인 매끄러운 피스톤으로 막은 실린더 속에 이상 기체가 들어 있다. 기체를 가열하였더니 피스톤이 천천히 %d cm 올라갔다. 이 과정에서 기체가 외부에 한 일은? (단, 대기압은 1.0×10%s Pa, 중력 가속도는 10 m/s²이다.)' % (A, m, d, sup(5))) + FIG(cyl_pair(0.4, 0.85, '', '', heat='in', t1='처음', t2='나중'), '58%')
            Pw = 1.0e5 + m * 10 / (A * 1e-4)
            wr = [1.0e5 * A * 1e-4 * d * 1e-2, m * 10 * d * 1e-2, Pw * A * 1e-4 * d, Pw * A * d * 1e-2, Pw * A * 1e-4 * d * 1e-2 * 2, Pw * (A * 1e-4) * d * 1e-2 + m * 10 * d * 1e-2]
            st = ['기체의 압력은 대기압과 피스톤 무게에 의한 압력의 합이다 : P = 1.0×10⁵ + (%d × 10)/(%d×10⁻⁴) = %s Pa' % (m, A, num(Pw)),
                  'ΔV = Ad = %d×10⁻⁴ × %d×10⁻² = %s m³' % (A, d, num(A * 1e-4 * d * 1e-2)), 'W = PΔV = %s × %s = %s J' % (num(Pw), num(A * 1e-4 * d * 1e-2), num(W))]
            right = num(W) + ' J'
            return mc(body, right, [num(w) + ' J' for w in wr], r=r, lv='상', fam='d', sort='shuf', steps=st,
                      core='피스톤이 매끄럽고 천천히 움직이면 기체의 압력은 일정하다(P = P₀ + mg/A). W = PΔV = PAd.', point='대기압과 피스톤 무게로 압력을 구하고 W = PΔV 를 적용한다.')
        Pp = r.choice([1, 2, 3]); Pg = Pp * 1e5
        W = Pg * A * 1e-4 * d * 1e-2
        body = P('그림과 같이 단면적 %d cm²인 피스톤으로 막은 실린더 속 이상 기체의 압력이 %d.0×10%s Pa로 일정하게 유지되면서 피스톤이 %d cm 이동하였다. 이 과정에서 기체가 한 일은?' % (A, Pp, sup(5), d)) + FIG(cyl_pair(0.4, 0.85, '', '', heat='in', t1='처음', t2='나중'), '58%')
        wr = [W * 100, W / 100, W * 10, W / 10, Pg * A * d * 1e-4, W * 2]
        return mc(body, num(W) + ' J', [num(w) + ' J' for w in wr], r=r, lv='중', fam='d',
                  steps=['ΔV = 단면적 × 이동 거리 = %d×10⁻⁴ m² × %d×10⁻² m = %s m³' % (A, d, num(A * 1e-4 * d * 1e-2)), 'W = PΔV = %d.0×10⁵ × %s = %s J' % (Pp, num(A * 1e-4 * d * 1e-2), num(W))],
                  core='W = PΔV, ΔV = 단면적 × 피스톤 이동 거리.', point='cm 단위를 m로 고쳐 ΔV를 구한다.')
    if form == 'e':    # 두 과정의 일 비교
        p1, p2 = r.choice([1, 2, 3, 4]), r.choice([1, 2, 3, 4])
        d1, d2 = r.choice([1, 2, 3, 4, 6]), r.choice([1, 2, 3, 4, 6])
        if p1 * d1 == p2 * d2: return None
        body = P('압력이 일정하게 유지되는 두 이상 기체 (가), (나)가 팽창한다. (가)는 압력 %d×10%s Pa에서 부피가 %d L 증가하고, (나)는 압력 %d×10%s Pa에서 부피가 %d L 증가한다. (가), (나)에서 기체가 한 일을 각각 W%s, W%s라 할 때 W%s : W%s는?' % (p1, sup(5), d1, p2, sup(5), d2, sub('가'), sub('나'), sub('가'), sub('나')))
        right = ratio_str(p1 * d1, p2 * d2)
        wr = [ratio_str(p2 * d2, p1 * d1), ratio_str(p1, p2), ratio_str(d1, d2), ratio_str(p1 * d2, p2 * d1), ratio_str(p1 + d1, p2 + d2)]
        return mc(body, right, wr, r=r, lv='중', fam='e', sort='shuf',
                  steps=['W = PΔV 이므로 W%s ∝ %d × %d = %d, W%s ∝ %d × %d = %d' % (sub('가'), p1, d1, p1 * d1, sub('나'), p2, d2, p2 * d2), '따라서 W%s : W%s = %s' % (sub('가'), sub('나'), right)],
                  core='등압 과정에서 W = PΔV 이므로 압력과 부피 변화량의 곱을 비교한다.', point='P와 ΔV를 모두 곱해 일을 비교한다.')
    if form == 'g':    # 등압 P-V 그래프 읽기
        sc = rand_sch(r)
        P0 = r.randint(1, 5); Va, Vb = r.sample(range(1, 8), 2)
        if Va > Vb and r.random() < 0.7: Va, Vb = Vb, Va
        st = {'A': (Va, P0), 'B': (Vb, P0)}
        fig = FIG(pv_fig(sc, 7, 5, st, [('A', 'B', 'L', BL)], guides=('A', 'B'), lab_off={'A': (0, -9) if True else None, 'B': (0, -9)}), '72%')
        W = P0 * (Vb - Va) * sc.J
        body = P('그림은 일정량의 이상 기체의 상태가 A에서 B로 변할 때의 압력과 부피를 나타낸 것이다. A → B 과정에서 기체가 한 일은?%s' % unit_note(sc)) + fig
        mag = abs(W)
        wr = ['%s J' % num(-W), '%s J' % num(P0 * Vb * sc.J), '%s J' % num(P0 * Va * sc.J), '%s J' % num(mag / 2), '%s J' % num(mag * 2), '%s J' % num(abs(W) / 100), '%s J' % num(mag * 10)]
        return mc(body, ('%s J' % num(W)) if W > 0 else ('−%s J' % num(mag)), [w.replace('-', '−') if False else w for w in wr], r=r, lv='중', fam='g', sort='shuf',
                  steps=['압력이 P = %s로 일정한 등압 과정이다. ΔV = (%d − %d) × %s = %s' % (pre_str(sc, P0), Vb, Va, vol_str(sc, 1), vol_str(sc, Vb - Va)),
                         'W = PΔV = %s J%s' % (num(W), '' if W > 0 else ' (압축이므로 음수)')],
                  core='등압 과정에서 W = PΔV. P-V 그래프에서 일은 곡선 아래 넓이이다.', point='그래프의 눈금에서 P와 ΔV를 읽어 W = PΔV 를 계산한다.')
    # h: 개념(<보기>)형이 아닌 정성 판단: 팽창/압축과 일의 부호
    cases = [('팽창', True), ('압축', False)]
    nm, ex = r.choice(cases)
    pa = r.choice([1, 2, 3])
    kind = r.choice(['W', 'who'])
    if kind == 'W':
        body = P('이상 기체가 %s하는 동안 기체가 한 일 W의 부호와 기체가 외부로부터 받은 일의 부호를 옳게 짝지은 것은? (단, 기체가 한 일은 +, 받은 일은 받는 쪽을 +로 한다.)' % nm)
        right = ('W > 0, 받은 일 < 0' if ex else 'W < 0, 받은 일 > 0')
        wr = [('W < 0, 받은 일 > 0' if ex else 'W > 0, 받은 일 < 0'), 'W > 0, 받은 일 > 0', 'W < 0, 받은 일 < 0', 'W = 0, 받은 일 > 0', 'W = 0, 받은 일 = 0']
        return mc(body, right, wr, r=r, lv='하', fam='h', sort='shuf',
                  steps=['%s 과정에서 ΔV %s 0 이므로 기체가 한 일 W = PΔV %s 0 이다.' % (nm, '>' if ex else '<', '>' if ex else '<'), '기체가 한 일과 받은 일은 크기가 같고 부호가 반대이다.'],
                  core='팽창하면 기체가 일을 하고(W > 0), 압축되면 기체가 일을 받는다(W < 0).', point='부피 변화의 방향으로 일의 부호를 정한다.')
    body = P('압력이 일정한 이상 기체의 부피가 V에서 %s로 변하였다. 이때 기체와 외부 사이의 일에 대한 설명으로 옳은 것은? (단, 압력은 P이다.)' % ('2V' if ex else 'V/2'))
    if ex:
        right = '기체가 외부에 PV의 일을 한다.'
        wr = ['기체가 외부에 2PV의 일을 한다.', '기체가 외부로부터 PV의 일을 받는다.', '기체가 외부에 PV/2의 일을 한다.', '기체가 외부에 한 일은 0이다.', '기체가 외부로부터 2PV의 일을 받는다.']
        stp = ['W = PΔV = P(2V − V) = PV > 0 이므로 기체가 외부에 PV의 일을 한다.']
    else:
        right = '기체가 외부로부터 PV/2의 일을 받는다.'
        wr = ['기체가 외부에 PV/2의 일을 한다.', '기체가 외부로부터 PV의 일을 받는다.', '기체가 외부에 PV의 일을 한다.', '기체가 외부로부터 2PV의 일을 받는다.', '기체가 한 일은 0이다.']
        stp = ['W = PΔV = P(V/2 − V) = −PV/2 < 0 이므로 기체가 외부로부터 PV/2의 일을 받는다.']
    return mc(body, right, wr, r=r, lv='중', fam='h', sort='shuf', steps=stp, core='등압 과정에서 W = PΔV. 부호는 부피 변화의 방향으로 정한다.', point='ΔV를 식으로 쓴 뒤 크기와 부호를 판단한다.')
