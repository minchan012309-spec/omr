# -*- coding: utf-8 -*-
"""Ⅱ-A 열역학 제1법칙 (ph065~ph076) 생성기.  이상 기체: U ∝ T ∝ PV, W = PΔV, Q = ΔU + W."""
from phlib import *
import math
from fractions import Fraction

from phlib import T as _T, num as _num


def num(x, nd=2):
    """phlib.num + 아주 작은 값(0.002 등)도 0 으로 반올림하지 않는다."""
    if not isinstance(x, int) and x != 0 and abs(x) < 0.1:
        s = ('%.9f' % x).rstrip('0').rstrip('.')
        return s
    return _num(x, nd)


def _san_str(t):
    """HTML 에서 '<' 가 태그로 읽히지 않게 하고, 음수의 하이픈을 '−' 로."""
    if not isinstance(t, str): return t
    t = re.sub(r'<(?![a-zA-Z/!])', '&lt;', t)
    t = re.sub(r'(?<![\w\)\]])-(?=\d)', '−', t)
    return t


def T(tag):
    """phlib.T 를 감싸서 문항 문자열을 정리한다."""
    def deco(f):
        def g(r, k):
            it = f(r, k)
            if it is None: return None
            it.body = _san_str(it.body)
            it.opts = [_san_str(o) for o in it.opts]
            it.steps = [_san_str(x) for x in it.steps]
            it.core = _san_str(it.core); it.point = _san_str(it.point)
            return it
        g.__name__ = f.__name__
        _T(tag)(g)
        return f
    return deco


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

def _unit_join(x, u):
    return (x if isinstance(x, str) else num(x)) + ('×' + u if u.startswith('10') else ' ' + u)
def vol_str(sc, v):
    return _unit_join(v * sc.vstep, sc.vl.split('(')[1][:-1])
def pre_str(sc, p):
    return _unit_join(p * sc.pstep, sc.pl.split('(')[1][:-1])


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
        body = P('분자 수가 일정한 이상 기체의 온도가 %d °C일 때 내부 에너지는 %d J이다. 이 기체의 온도를 %d °C로 바꾸었을 때 %s? (단, 0 °C = 273 K이다.)' % (t1, U1, t2, '내부 에너지는' if what == 'U2' else '내부 에너지의 변화량은'))
        if what == 'U2':
            right = '%d J' % U2
            cand = [U1 * t2 / t1 if t1 > 0 else U1 + 40, U1 * T1 / T2, abs(U2 - U1), U1 + (t2 - t1) if U1 + (t2 - t1) > 0 else U1 + 60, 2 * U2, U2 // 2 + 10, U1 + U2]
            wr = ['%s J' % num(abs(x)) for x in cand if x > 0 and abs(x - U2) > 1e-9]
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
        body = P('분자 수가 N인 이상 기체의 온도가 %d °C이다. 이 기체를 %d K으로 바꾸고 분자 수를 %d배로 늘렸다. 나중 내부 에너지는 처음의 몇 배인가? (단, 0 °C = 273 K이다.)' % (t1, T2, nmul))
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
                  steps=['압력이 일정(P = %s)한 등압 과정이다. ΔV = (%d − %d) 칸 = %s' % (pre_str(sc, P0), Vb, Va, vol_str(sc, Vb - Va)),
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


# ============================================================ ph067 Q = ΔU + W
def _qw_words(Q, W):
    qs = '열 %d J을 흡수하면서' % Q if Q > 0 else '열 %d J을 방출하면서' % -Q
    ws = '외부에 %d J의 일을 하였다' % W if W > 0 else '외부로부터 %d J의 일을 받았다' % -W
    return qs, ws

def _dU_str(dU):
    return '%d J 증가' % dU if dU > 0 else ('%d J 감소' % -dU if dU < 0 else '변화 없음')

@T('ph067')
def g067(r, k):
    form = r.choice(['dU', 'dU', 'W', 'Q', 'Q', 'table', 'table', 'temp', 'cyl'])
    vals = [50, 100, 150, 200, 250, 300, 400, 500, 600, 800]
    if form in ('dU', 'cyl'):
        Q = r.choice(vals) * r.choice([1, -1]); W = r.choice(vals) * r.choice([1, -1])
        dU = Q - W
        if dU == 0: return None
        qs, ws = _qw_words(Q, W)
        fig = ''
        if form == 'cyl':
            fig = FIG(cyl_pair(0.4, 0.4 + (0.45 if W > 0 else -0.25), '', '', heat='in' if Q > 0 else 'out', t1='처음', t2='나중'), '58%')
        body = P('일정량의 이상 기체가 %s %s. 이 과정에서 기체의 내부 에너지 변화는?' % (qs, ws)) + fig
        wr = [_dU_str(Q + W), _dU_str(-dU), _dU_str(abs(Q) + abs(W)), _dU_str(Q - abs(W)) if Q - abs(W) else '%d J 증가' % Q, '%d J 증가' % abs(Q), '%d J 증가' % abs(W), _dU_str(W - Q)]
        wr = [x for x in wr]
        st = ['기체가 흡수한 열은 Q = %s J, 기체가 한 일은 W = %s J 이다.' % (sj(Q, '').strip(), sj(W, '').strip()) if True else '', 'ΔU = Q − W = (%s) − (%s) = %s J' % (num(Q), num(W), num(dU)), '따라서 내부 에너지는 %s이다.' % _dU_str(dU)]
        return mc(body, _dU_str(dU), wr, r=r, lv='중' if abs(Q) != abs(W) and Q * W > 0 else '하', fam='a', sort='shuf', steps=st,
                  core='열역학 제1법칙 Q = ΔU + W (Q: 흡수한 열, W: 기체가 한 일).', point='흡열·방열, 일을 한 것·받은 것의 부호를 구분해 ΔU를 구한다.')
    if form == 'W':
        Q = r.choice(vals) * r.choice([1, 1, -1]); dU = r.choice(vals) * r.choice([1, -1])
        W = Q - dU
        if W == 0: return None
        qs = '열 %d J을 흡수하고' % Q if Q > 0 else '열 %d J을 방출하고' % -Q
        us = '내부 에너지가 %d J 증가하였다' % dU if dU > 0 else '내부 에너지가 %d J 감소하였다' % -dU
        right = '기체가 외부에 %d J의 일을 하였다' % W if W > 0 else '기체가 외부로부터 %d J의 일을 받았다' % -W
        body = P('일정량의 이상 기체가 %s %s. 이 과정에서 기체와 외부 사이의 일에 대한 설명으로 옳은 것은?' % (qs, us))
        wr = ['기체가 외부에 %d J의 일을 하였다' % abs(W) if W < 0 else '기체가 외부로부터 %d J의 일을 받았다' % abs(W),
              '기체가 외부에 %d J의 일을 하였다' % (abs(Q) + abs(dU)) if abs(Q) + abs(dU) != abs(W) else '기체가 외부에 %d J의 일을 하였다' % (abs(W) + 100),
              '기체가 외부로부터 %d J의 일을 받았다' % (abs(Q) + abs(dU)) if abs(Q) + abs(dU) != abs(W) else '기체가 외부로부터 %d J의 일을 받았다' % (abs(W) + 100),
              '기체가 외부에 %d J의 일을 하였다' % abs(dU), '기체가 외부로부터 %d J의 일을 받았다' % abs(Q), '기체가 한 일은 0이다']
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf',
                  steps=['Q = %s J, ΔU = %s J 이다.' % (num(Q), num(dU)), 'W = Q − ΔU = (%s) − (%s) = %s J' % (num(Q), num(dU), num(W)), 'W %s 0 이므로 %s.' % ('>' if W > 0 else '<', right)],
                  core='W = Q − ΔU. W > 0 이면 기체가 외부에 일을 한 것, W < 0 이면 일을 받은 것이다.', point='Q와 ΔU의 부호를 반영해 W의 부호까지 구한다.')
    if form == 'Q':
        dU = r.choice(vals) * r.choice([1, -1]); W = r.choice(vals) * r.choice([1, -1])
        Q = dU + W
        if Q == 0: return None
        us = '내부 에너지가 %d J 증가하였다' % dU if dU > 0 else '내부 에너지가 %d J 감소하였다' % -dU
        ws = '외부에 %d J의 일을 하였다' % W if W > 0 else '외부로부터 %d J의 일을 받았다' % -W
        right = '열을 %d J 흡수' % Q if Q > 0 else '열을 %d J 방출' % -Q
        body = P('일정량의 이상 기체의 %s, 기체는 %s. 이 과정에서 기체와 외부 사이의 열 출입은?' % (us, ws))
        flip = lambda q: '열을 %d J 흡수' % q if q > 0 else '열을 %d J 방출' % -q
        wr = [flip(-Q), flip(abs(dU) - abs(W)) if abs(dU) != abs(W) else flip(abs(dU)), flip(-(dU - W)) if dU != W else flip(dU), flip(dU - W), flip(abs(dU) + abs(W)), flip(-(abs(dU) + abs(W)))]
        return mc(body, right, wr, r=r, lv='중', fam='c', sort='shuf',
                  steps=['ΔU = %s J, W = %s J 이다.' % (num(dU), num(W)), 'Q = ΔU + W = (%s) + (%s) = %s J' % (num(dU), num(W), num(Q)), 'Q %s 0 이므로 %s.' % ('>' if Q > 0 else '<', right)],
                  core='Q = ΔU + W. Q > 0 이면 열을 흡수, Q < 0 이면 열을 방출한다.', point='ΔU와 W의 부호를 반영하여 Q를 구한다.')
    if form == 'temp':
        Q = r.choice(vals); W = r.choice(vals)
        if Q == W: return None
        if r.random() < 0.5: Q = -Q
        if r.random() < 0.5: W = -W
        dU = Q - W
        if dU == 0: return None
        qs, ws = _qw_words(Q, W)
        body = P('일정량의 이상 기체가 %s %s. 이 과정에서 기체의 온도 변화로 옳은 것은?' % (qs, ws))
        right = '올라간다.' if dU > 0 else '내려간다.'
        wr = ['내려간다.' if dU > 0 else '올라간다.', '변하지 않는다.', '알 수 없다.', '처음에는 올라가다가 나중에 내려간다.', '처음에는 내려가다가 나중에 올라간다.']
        return mc(body, right, wr, r=r, lv='하', fam='d', sort='shuf',
                  steps=['ΔU = Q − W = (%s) − (%s) = %s J' % (num(Q), num(W), num(dU)), 'ΔU %s 0 이므로 내부 에너지가 %s하고 온도가 %s' % ('>' if dU > 0 else '<', '증가' if dU > 0 else '감소', right)],
                  core='이상 기체의 내부 에너지는 온도에 비례하므로 ΔU의 부호가 온도 변화의 부호이다.', point='ΔU = Q − W 의 부호로 온도 변화를 판단한다.')
    # table: (가)(나)(다)의 빈칸 채우기
    rows, blanks, truth = [], [], []
    for lab in ('(가)', '(나)', '(다)'):
        for _ in range(20):
            dU = r.choice(vals) * r.choice([1, -1]); W = r.choice(vals) * r.choice([1, -1])
            if dU + W != 0 and dU != 0 and W != 0: break
        Q = dU + W
        blank = r.choice([0, 1, 2])   # Q, ΔU, W
        rows.append([lab, Q, dU, W]); blanks.append(blank)
    names = ['가', '나', '다']
    if len(set(blanks)) < 2: return None
    cells, ans_vals = [], []
    for i, (row, b) in enumerate(zip(rows, blanks)):
        c = [row[0]] + [num(x) for x in row[1:]]
        ans_vals.append(row[1 + b])
        c[1 + b] = '(%s)' % ['x', 'y', 'z'][i]
        cells.append(c)
    body = P('표는 일정량의 이상 기체가 세 가지 과정 (가), (나), (다)를 거칠 때 기체가 흡수한 열량 Q, 내부 에너지 변화량 ΔU, 기체가 외부에 한 일 W를 나타낸 것이다. (단위 : J, 기체가 열을 방출하거나 내부 에너지가 감소하거나 외부로부터 일을 받으면 음수이다.) x, y, z로 옳은 것은?') + \
        table(['과정', 'Q', 'ΔU', 'W'], cells)
    right = 'x = %s, y = %s, z = %s' % tuple(num(v) for v in ans_vals)
    def mk(a, b, c): return 'x = %s, y = %s, z = %s' % (num(a), num(b), num(c))
    x, y, z = ans_vals
    wr = [mk(-x, y, z), mk(x, -y, z), mk(x, y, -z), mk(y, x, z), mk(-x, -y, -z), mk(x, z, y), mk(z, y, x)]
    st = []
    for i, (row, b) in enumerate(zip(rows, blanks)):
        Q, dU, W = row[1:]
        assert Q == dU + W
        st.append('%s : Q = ΔU + W 에서 %s = %s J' % (row[0], ['Q', 'ΔU', 'W'][b], num(row[1 + b])) + ('  (Q = %s + %s)' % (num(dU), num(W)) if b == 0 else '  (ΔU = Q − W = %s − %s)' % (num(Q), num(W)) if b == 1 else '  (W = Q − ΔU = %s − %s)' % (num(Q), num(dU))))
    return mc(body, right, wr, r=r, lv='상', fam='e', sort='shuf', steps=st,
              core='Q = ΔU + W 는 모든 과정에서 성립한다(부호 포함).', point='표에서 모르는 열 하나를 제1법칙으로 구한다.')


# ============================================================ ph068 등압 과정
_B68 = [
    ('기체가 등압 팽창하면 기체의 온도가 올라간다.', True, 'PV ∝ T 에서 P가 일정하고 V가 커지므로 T가 올라간다.', 'T'),
    ('기체가 등압 팽창하는 동안 기체는 열을 흡수한다.', True, 'ΔU > 0, W > 0 이므로 Q = ΔU + W > 0 이다.', 'Q'),
    ('기체가 등압 팽창할 때 기체가 흡수한 열은 기체가 한 일과 같다.', False, 'Q = ΔU + W 이고 ΔU > 0 이므로 Q > W 이다.', 'QW'),
    ('기체가 등압 팽창할 때 흡수한 열량은 내부 에너지 증가량보다 크다.', True, 'Q = ΔU + W 에서 W > 0 이므로 Q > ΔU 이다.', 'QU'),
    ('기체가 등압 팽창할 때 내부 에너지는 변하지 않는다.', False, '온도가 올라가므로 내부 에너지가 증가한다.', 'U'),
    ('기체가 등압 팽창할 때 기체는 외부에 일을 한다.', True, '부피가 증가하므로 W = PΔV > 0 이다.', 'W'),
    ('기체가 등압 압축될 때 기체는 열을 방출한다.', True, 'ΔU < 0, W < 0 이므로 Q < 0 이다.', 'Qc'),
    ('기체가 등압 압축될 때 기체의 온도는 올라간다.', False, 'P가 일정하고 V가 감소하므로 T가 내려간다.', 'Tc'),
    ('등압 과정에서 기체의 부피는 절대 온도에 비례한다.', True, 'P가 일정하면 V ∝ T 이다.', 'VT'),
    ('등압 과정에서 기체의 압력은 부피에 반비례한다.', False, '등압 과정에서는 압력이 일정하다. 압력이 부피에 반비례하는 것은 등온 과정이다.', 'PV'),
    ('등압 팽창하는 동안 기체가 한 일은 PΔV로 구할 수 있다.', True, 'P가 일정하므로 W = PΔV 이다.', 'WPV'),
    ('등압 팽창 과정을 P-V 그래프로 나타내면 P축에 나란한(수직인) 직선이다.', False, '압력이 일정하므로 V축에 나란한(수평인) 직선이다.', 'graph'),
    ('등압 팽창하는 동안 기체가 한 일은 P-V 그래프에서 직선 아래의 넓이와 같다.', True, 'W = PΔV 는 직사각형의 넓이이다.', 'area'),
    ('등압 과정에서 기체가 흡수한 열은 모두 내부 에너지 증가에 쓰인다.', False, '일부는 외부에 하는 일 W로 쓰이고 나머지가 ΔU가 된다.', 'allU'),
    ('피스톤이 자유롭게 움직이는 실린더 속 기체를 가열하면 대기압이 일정할 때 등압 팽창이 일어난다.', True, '피스톤에 작용하는 외부 압력이 일정하므로 기체의 압력도 일정하다.', 'cyl'),
    ('등압 과정에서 온도가 2배가 되면 부피도 2배가 된다.', True, 'V ∝ T (P 일정).', 'V2'),
    ('등압 팽창하는 동안 기체의 내부 에너지 증가량과 기체가 한 일은 항상 같다.', False, '두 양의 비는 기체의 종류에 따라 달라지며, 일반적으로 같다고 할 수 없다. 단원자 분자 기체에서는 ΔU가 W의 1.5배이다.', 'UW'),
    ('등압 냉각 과정에서 기체의 부피는 감소한다.', True, 'V ∝ T 이므로 T가 내려가면 V가 감소한다.', 'cool'),
]

@T('ph068')
def g068(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'bogi', 'bogi', 'e', 'f'])
    if form == 'a':   # W 와 ΔU 로 Q
        p = r.choice([1, 2, 3, 4]); dV = r.choice([1, 2, 3, 4, 5])
        W = p * 100 * dV
        dU = r.choice([50, 100, 150, 200, 300, 400, 450, 600])
        Q = W + dU
        body = P('그림과 같이 실린더 속 이상 기체가 %d기압(= %d.0×10%s Pa)으로 일정하게 유지되면서 부피가 %d L 증가하였고 이때 기체의 내부 에너지는 %d J 증가하였다. 이 과정에서 기체가 흡수한 열량은? (단, 1 L = 1.0×10%s m%s이다.)' % (p, p, sup(5), dV, dU, sup(-3), sup(3))) + FIG(cyl_pair(0.4, 0.4 + 0.1 * dV, '', '', heat='in', t1='처음', t2='나중'), '58%')
        wr = [dU - W if dU != W else dU + 2 * W, dU, W, Q + W, W * 1000 + dU, abs(dU - W) + 50]
        return mc(body, '%d J' % Q, ['%d J' % w for w in wr], r=r, lv='중', fam='a',
                  steps=['등압 과정이므로 W = PΔV = %d.0×10⁵ × %d×10⁻³ = %d J' % (p, dV, W), '제1법칙 Q = ΔU + W = %d + %d = %d J' % (dU, W, Q)],
                  core='등압 팽창에서 Q = ΔU + PΔV.', point='W = PΔV 를 구한 뒤 제1법칙을 적용한다.')
    if form == 'b':   # ΔU = 1.5W 주어진 경우
        p = r.choice([1, 2, 3, 4, 5]); dV = r.choice([2, 4, 6, 8])
        W = p * 100 * dV
        f_ = r.choice([Fraction(3, 2), Fraction(3, 2), Fraction(5, 2), Fraction(1, 2), 2, 3])
        dU = W * f_
        if dU.denominator != 1: return None
        dU = int(dU)
        Q = W + dU
        ask = r.choice(['Q', 'ratio'])
        body = P('이상 기체가 압력 %d×10%s Pa로 일정하게 유지되면서 팽창하여 부피가 %d L 증가하였다. 이 과정에서 기체의 내부 에너지 증가량은 기체가 한 일의 %s배였다. ' % (p, sup(5), dV, fr_str(f_)) + ('기체가 흡수한 열량은? (단, 1 L = 1.0×10%s m%s이다.)' % (sup(-3), sup(3)) if ask == 'Q' else '기체가 흡수한 열량은 기체가 한 일의 몇 배인가?'))
        if ask == 'Q':
            right = '%d J' % Q
            wr = ['%d J' % W, '%d J' % dU, '%d J' % (dU - W if dU != W else 2 * W), '%d J' % (Q * 2), '%d J' % (W * 1000), '%d J' % (Q + 100)]
            lv = '상'
        else:
            right = fr_str(1 + f_) + '배'
            wr = [fr_str(f_) + '배', fr_str(1 + f_ + 1) + '배', fr_str(abs(f_ - 1)) + '배' if f_ != 1 else '2배', fr_str(1 / f_) + '배', fr_str(1 + 1 / f_) + '배', fr_str(f_ + Fraction(1, 2)) + '배']
            lv = '중'
        return mc(body, right, wr, r=r, lv=lv, fam='b', sort='shuf',
                  steps=['W = PΔV = %d×10⁵ × %d×10⁻³ = %d J' % (p, dV, W), 'ΔU = %s × W = %d J' % (fr_str(f_), dU), 'Q = ΔU + W = %d + %d = %d J' % (dU, W, Q) + ('' if ask == 'Q' else ' → Q/W = %s' % fr_str(1 + f_))],
                  core='Q = ΔU + W. 등압 과정에서 W = PΔV.', point='주어진 비율로 ΔU를 구하고 Q = ΔU + W 로 합한다.')
    if form == 'c':   # V ∝ T
        T1 = r.choice([200, 250, 300, 400, 500]); n = r.choice([2, 3, Fraction(3, 2), Fraction(5, 2), Fraction(1, 2), Fraction(2, 3)])
        T2 = T1 * n
        if Fraction(T2).denominator != 1: return None
        T2 = int(T2)
        V1 = r.choice([2, 4, 6, 8, 10]); V2 = Fraction(V1) * n
        if V2.denominator != 1: return None
        V2 = int(V2)
        U1 = r.choice([100, 200, 300, 400, 600])
        U2 = Fraction(U1) * n
        if U2.denominator != 1: return None
        U2 = int(U2)
        ask = r.choice(['V', 'T', 'U'])
        if ask == 'V':
            body = P('압력이 일정한 이상 기체의 부피가 %d L, 절대 온도가 %d K이다. 압력을 일정하게 유지하며 온도를 %d K으로 바꾸었을 때 기체의 부피는?' % (V1, T1, T2))
            right = '%d L' % V2
            wr = ['%d L' % (V1 * T1 // T2) if (V1 * T1) % T2 == 0 else '%d L' % (V1 + 2), '%d L' % (V1 + (T2 - T1) // 100), '%d L' % (V1 * 2), '%d L' % (V2 + 2), '%d L' % (V1 // 2 if V1 % 2 == 0 else V1 + 1), '%d L' % (V2 * 2)]
            st = ['등압 과정에서 V ∝ T 이다.', 'V%s = V%s × T%s/T%s = %d × %d/%d = %d L' % (sub(2), sub(1), sub(2), sub(1), V1, T2, T1, V2)]
        elif ask == 'T':
            body = P('압력이 일정한 이상 기체의 부피가 %d L에서 %d L로 변하였다. 처음 절대 온도가 %d K이면 나중 절대 온도는?' % (V1, V2, T1))
            right = '%d K' % T2
            wr = ['%d K' % (T1 * V1 // V2) if (T1 * V1) % V2 == 0 else '%d K' % (T1 + 50), '%d K' % (T1 + (V2 - V1)), '%d K' % (T1 * 2), '%d K' % (T2 + 100), '%d K' % (T2 // 2 + 50)]
            st = ['등압 과정에서 V ∝ T 이므로 T%s = T%s × V%s/V%s' % (sub(2), sub(1), sub(2), sub(1)), 'T%s = %d × %d/%d = %d K' % (sub(2), T1, V2, V1, T2)]
        else:
            body = P('압력이 일정한 이상 기체의 부피가 %d L에서 %d L로 변하였다. 처음 내부 에너지가 %d J이면 나중 내부 에너지는?' % (V1, V2, U1))
            right = '%d J' % U2
            wr = ['%d J' % (U1 * V1 // V2) if (U1 * V1) % V2 == 0 else '%d J' % (U1 + 50), '%d J' % (U1 + (V2 - V1) * 10), '%d J' % (U1 * 2), '%d J' % (U2 + 100), '%d J' % (U2 * 2), '%d J' % (U2 // 2 + 30)]
            st = ['등압 과정에서 V ∝ T 이고 U ∝ T 이므로 U ∝ V 이다.', 'U%s = U%s × V%s/V%s = %d × %d/%d = %d J' % (sub(2), sub(1), sub(2), sub(1), U1, V2, V1, U2)]
        return mc(body, right, wr, r=r, lv='중', fam='c', sort='shuf', steps=st, core='등압 과정에서 V ∝ T, 내부 에너지 U ∝ T 이므로 U ∝ V.', point='등압 조건에서 부피-온도 비례 관계를 이용한다.')
    if form == 'd':   # 그래프: 등압선
        sc = rand_sch(r)
        P0 = r.randint(1, 5); Va, Vb = sorted(r.sample(range(1, 8), 2))
        st = {'A': (Va, P0), 'B': (Vb, P0)}
        U_A = r.choice([100, 150, 200, 300, 450])
        # U_B = U_A * Vb/Va
        UB = Fraction(U_A * Vb, Va)
        if UB.denominator != 1: return None
        UB = int(UB)
        W = P0 * (Vb - Va) * sc.J
        Q = (UB - U_A) + W
        fig = FIG(pv_fig(sc, 7, 5, st, [('A', 'B', 'L', BL)], guides=('A', 'B'), lab_off={'A': (0, -9), 'B': (0, -9)}), '72%')
        body = P('그림은 일정량의 이상 기체가 A에서 B로 변하는 과정을 나타낸 것이다. 상태 A에서 기체의 내부 에너지는 %d J이다. A → B 과정에서 기체가 흡수한 열량은?%s' % (U_A, unit_note(sc))) + fig
        wr = [UB - U_A, W, UB, Q + U_A, UB - U_A - W if UB - U_A != W else Q + W, W * 10]
        return mc(body, '%d J' % Q, ['%d J' % w for w in wr], r=r, lv='상', fam='d',
                  steps=['A → B 는 압력이 일정(%s)한 등압 팽창이다.' % pre_str(sc, P0), 'W = PΔV = %s J. 등압 과정에서 U ∝ T ∝ V 이므로 U%s = %d × %d/%d = %d J' % (num(W), sub('B'), U_A, Vb, Va, UB),
                         'ΔU = %d − %d = %d J, Q = ΔU + W = %d + %d = %d J' % (UB, U_A, UB - U_A, UB - U_A, W, Q)],
                  core='등압 과정: W = PΔV, U ∝ T ∝ V, Q = ΔU + W.', point='그래프에서 W를 구하고 온도(내부 에너지) 비례 관계로 ΔU를 구한다.')
    if form == 'e':   # 부호 표 채우기
        which = r.choice([('등압 팽창', (UP, UP, UP)), ('등압 압축', (DN, DN, DN))])
        other = [('등압 팽창', (UP, UP, UP)), ('등압 압축', (DN, DN, DN)), ('등적 가열', (UP, ZE, UP)), ('등온 팽창', (ZE, UP, UP))]
        rows = ['(가)', '(나)', '(다)']
        pr = r.sample(other, 3)
        tb = []
        for lab, (nm, sg) in zip(rows, pr):
            tb.append([lab, nm, '', '', ''])
        # 열 부호 질문: 등압 과정 하나를 골라 부호 문자열 묻기
        nm, sg = which
        body = P('이상 기체가 %s할 때 ΔU, W, Q의 부호(⊕: 양, ⊖: 음, 0: 영)를 순서대로 옳게 나타낸 것은? (ΔU: 내부 에너지 변화, W: 기체가 한 일, Q: 기체가 흡수한 열)' % nm.split(' ')[1].replace('팽창', '팽창(압력 일정)').replace('압축', '압축(압력 일정)'))
        right = ', '.join(sg)
        combos = [(UP, UP, UP), (DN, DN, DN), (UP, ZE, UP), (ZE, UP, UP), (DN, UP, ZE), (UP, DN, ZE), (UP, UP, DN), (DN, UP, UP), (UP, DN, UP), (DN, DN, UP), (UP, UP, ZE)]
        wr = [', '.join(c) for c in combos if c != sg]
        return mc(body, right, wr, r=r, lv='하', fam='e', sort='shuf',
                  steps=['%s : 부피 변화로 W의 부호를, 온도 변화로 ΔU의 부호를 정한다.' % nm, 'ΔU %s, W %s, Q = ΔU + W 이므로 Q %s' % (sg[0], sg[1], sg[2])],
                  core='등압 팽창: ΔU > 0, W > 0, Q > 0. 등압 압축: ΔU < 0, W < 0, Q < 0.', point='등압 과정의 ΔU, W, Q 부호를 구분한다.')
    if form == 'f':   # 열량 대소 비교
        ratio = r.choice([Fraction(3, 2), Fraction(3, 1), Fraction(1, 1), Fraction(5, 2)])
        W = r.choice([100, 200, 300, 400, 600])
        dU = W * ratio
        if dU.denominator != 1: return None
        dU = int(dU); Q = W + dU
        body = P('이상 기체가 등압 팽창하는 동안 흡수한 열량 Q를 기체가 한 일 W와 내부 에너지 증가량 ΔU로 나누어 쓴다. W = %d J, ΔU = %d J일 때 Q에서 W가 차지하는 비율은?' % (W, dU))
        right = fr_str(Fraction(W, Q))
        wr = [fr_str(Fraction(dU, Q)), fr_str(Fraction(W, dU)), fr_str(Fraction(Q, W)), fr_str(Fraction(dU, W)), '1/2' if Fraction(W, Q) != Fraction(1, 2) else '1/3', '1']
        return mc(body, right, wr, r=r, lv='중', fam='f', sort='shuf',
                  steps=['Q = ΔU + W = %d + %d = %d J' % (dU, W, Q), 'W/Q = %d/%d = %s' % (W, Q, fr_str(Fraction(W, Q)))],
                  core='흡수한 열 Q는 내부 에너지 증가 ΔU와 외부에 한 일 W로 나뉜다(Q = ΔU + W).', point='제1법칙으로 Q를 구한 뒤 비율을 계산한다.')
    stm = pick_stmts(r, _B68)
    return bogi('일정한 압력에서 이상 기체가 팽창·압축하는 등압 과정에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv='중', fam='g',
                core='등압 과정: W = PΔV, V ∝ T, 팽창 시 Q = ΔU + W > ΔU.', point='등압 과정에서 온도·일·열의 관계를 설명한다.')


# ============================================================ ph069 등적 과정
_B69 = [
    ('등적 과정에서 기체가 외부에 한 일은 0이다.', True, '부피가 변하지 않으므로 W = PΔV = 0 이다.', 'W0'),
    ('등적 과정에서 기체가 흡수한 열은 모두 내부 에너지 증가에 쓰인다.', True, 'W = 0 이므로 Q = ΔU 이다.', 'QU'),
    ('부피가 일정한 용기 속 기체를 가열하면 압력이 감소한다.', False, 'P ∝ T 이므로 가열하면 압력이 증가한다.', 'Pdec'),
    ('부피가 일정한 용기 속 기체를 가열하면 압력이 증가한다.', True, '등적 과정에서 P ∝ T 이다.', 'Pinc'),
    ('등적 과정에서 기체의 압력은 절대 온도에 비례한다.', True, 'PV ∝ T 에서 V가 일정하면 P ∝ T 이다.', 'PT'),
    ('등적 과정에서 기체의 압력은 섭씨온도에 비례한다.', False, '절대 온도(K)에 비례한다.', 'PC'),
    ('등적 냉각 과정에서 기체는 열을 방출한다.', True, 'ΔU < 0, W = 0 이므로 Q = ΔU < 0 이다.', 'cool'),
    ('등적 과정을 P-V 그래프로 나타내면 V축에 나란한(수평인) 직선이다.', False, '부피가 일정하므로 P축에 나란한(수직인) 직선이다.', 'graph'),
    ('등적 과정에서 P-V 그래프 아래의 넓이는 0이다.', True, 'ΔV = 0 이므로 기체가 한 일은 0이다.', 'area'),
    ('등적 과정에서 기체의 내부 에너지가 증가하면 기체의 온도도 올라간다.', True, 'U ∝ T 이다.', 'UT'),
    ('단단한 용기 속 기체에 열을 가해도 기체는 외부에 일을 한다.', False, '용기의 부피가 변하지 않으므로 일을 하지 않는다.', 'rigid'),
    ('등적 과정에서 기체가 방출한 열량은 내부 에너지 감소량과 같다.', True, 'Q = ΔU (W = 0).', 'rel'),
    ('압력이 2배가 되도록 등적 변화시키면 절대 온도도 2배가 된다.', True, 'P ∝ T.', 'P2'),
    ('압력이 2배가 되도록 등적 변화시키면 내부 에너지는 변하지 않는다.', False, 'T가 2배가 되므로 내부 에너지도 2배가 된다.', 'P2U'),
    ('밀폐된 용기 속 기체를 가열할 때 기체 분자가 용기 벽에 충돌하는 힘이 평균적으로 증가한다.', True, '온도가 높아지면 분자의 평균 속력이 증가해 압력이 커진다.', 'mol'),
    ('등적 과정에서 기체가 한 일과 기체가 받은 일은 모두 0이다.', True, '부피 변화가 없으므로 일의 출입이 없다.', 'both0'),
    ('등적 가열 과정에서 흡수한 열량이 같으면 기체의 종류에 관계없이 온도 상승량이 같다.', False, '내부 에너지와 온도의 관계는 분자 수·종류에 따라 다르다.', 'any'),
    ('등적 과정에서는 Q의 부호와 ΔU의 부호가 같다.', True, 'Q = ΔU 이기 때문이다.', 'sameSign'),
]

@T('ph069')
def g069(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'b', 'c', 'c', 'bogi', 'bogi', 'e', 'f'])
    if form == 'a':
        Q = r.choice([50, 100, 150, 200, 300, 400, 500, 600]); heat = r.choice([1, -1])
        ask = r.choice(['dU', 'Q', 'W'])
        hd = '흡수' if heat > 0 else '방출'
        fig = FIG(cyl_one(0.6, '', heat='in' if heat > 0 else 'out', fixed=True, tag='피스톤 고정'), '40%')
        if ask == 'dU':
            body = P('그림과 같이 피스톤이 고정된 실린더 속 이상 기체가 열 %d J을 %s하였다. 기체의 내부 에너지 변화는?' % (Q, hd)) + fig
            right = ('%d J 증가' if heat > 0 else '%d J 감소') % Q
            wr = [('%d J 감소' if heat > 0 else '%d J 증가') % Q, '변화 없음', '%d J 증가' % (Q * 2), '%d J 감소' % (Q // 2), '%d J 증가' % (Q // 2)]
            st = ['피스톤이 고정되어 부피가 일정하므로 W = 0 이다.', 'Q = ΔU + W 에서 ΔU = Q = %s%d J' % ('+' if heat > 0 else '−', Q), '따라서 ' + right + '이다.']
            return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf', steps=st, core='등적 과정에서는 W = 0 이므로 Q = ΔU.', point='부피가 일정하면 일을 하지 않는다는 점을 이용한다.')
        if ask == 'Q':
            dU = Q * heat
            body = P('그림과 같이 피스톤이 고정된 실린더 속 이상 기체의 내부 에너지가 %d J %s하였다. 이 과정에서 기체와 외부 사이의 열 출입은?' % (Q, '증가' if heat > 0 else '감소')) + fig
            right = ('열 %d J 흡수' if heat > 0 else '열 %d J 방출') % Q
            wr = [('열 %d J 방출' if heat > 0 else '열 %d J 흡수') % Q, '열의 출입이 없다', '열 %d J 흡수' % (Q * 2) if heat > 0 else '열 %d J 방출' % (Q * 2), '열 %d J 흡수' % (Q // 2), '열 %d J 방출' % (Q // 2)]
            return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf', steps=['부피가 일정하므로 W = 0, Q = ΔU = %s%d J 이다.' % ('+' if heat > 0 else '−', Q), right + '이다.'],
                      core='등적 과정에서 Q = ΔU.', point='W = 0 이면 Q = ΔU.')
        body = P('그림과 같이 피스톤이 고정된 실린더 속 이상 기체에 열 %d J을 %s하였더니 기체의 내부 에너지가 %d J %s하였다. 이때 기체가 외부에 한 일은?' % (Q, hd, Q, '증가' if heat > 0 else '감소')) + fig
        wr = ['%d J' % Q, '%d J' % (2 * Q), '%d J' % (Q // 2), '%d J' % (-Q) if False else '%d J' % (Q + 100), '−%d J' % Q]
        return mc(body, '0', wr, r=r, lv='하', fam='a', sort='shuf', steps=['W = Q − ΔU = %s%d − (%s%d) = 0' % ('+' if heat > 0 else '−', Q, '+' if heat > 0 else '−', Q), '부피가 변하지 않으므로 일을 하지 않는다.'],
                  core='등적 과정에서 W = PΔV = 0.', point='Q와 ΔU가 같으면 W = 0.')
    if form == 'b':
        mode = r.choice(['K', 'C'])
        P1 = r.choice([1.0, 1.5, 2.0, 3.0, 4.0]); 
        if mode == 'K':
            T1 = r.choice([200, 300, 400, 500]); n = r.choice([Fraction(3, 2), 2, Fraction(1, 2), Fraction(3, 1), Fraction(2, 3)])
            T2 = T1 * n
            if T2.denominator != 1: return None
            T2 = int(T2); P2 = P1 * float(n)
            body = P('부피가 일정한 밀폐 용기 속 이상 기체의 압력이 %s기압, 절대 온도가 %d K이다. 이 기체의 온도를 %d K으로 바꾸었을 때 압력은?' % (num(P1), T1, T2))
            right = '%s기압' % num(P2)
            wr = ['%s기압' % num(P1 * T1 / T2), '%s기압' % num(P1 + (T2 - T1) / 100.0), '%s기압' % num(P2 * 2), '%s기압' % num(P2 / 2), '%s기압' % num(P2 + 1), '%s기압' % num(P1)]
            st = ['부피가 일정하므로 P ∝ T 이다.', 'P%s = P%s × T%s/T%s = %s × %d/%d = %s기압' % (sub(2), sub(1), sub(2), sub(1), num(P1), T2, T1, num(P2))]
        else:
            t1, t2 = r.choice([(27, 327), (27, 127), (-73, 127), (127, 327), (27, 177), (-73, 27), (127, 527)])
            T1, T2 = t1 + 273, t2 + 273
            P2 = Fraction(P1).limit_denominator(10) * Fraction(T2, T1)
            if P2.denominator not in (1, 2, 4, 5, 10): return None
            P2 = float(P2)
            body = P('부피가 일정한 밀폐 용기 속 이상 기체의 압력이 %s기압, 온도가 %d °C이다. 이 기체의 온도를 %d °C로 바꾸었을 때 압력은? (단, 0 °C = 273 K이다.)' % (num(P1), t1, t2))
            right = '%s기압' % num(P2)
            wr = ['%s기압' % num(P1 * t2 / t1) if t1 > 0 else '%s기압' % num(P1 + 1), '%s기압' % num(P1 * t1 / t2) if t2 > 0 and t1 > 0 else '%s기압' % num(P2 + 1), '%s기압' % num(P1 * T1 / T2), '%s기압' % num(P2 * 2), '%s기압' % num(P1 + (t2 - t1) / 100.0), '%s기압' % num(P2 / 2)]
            st = ['절대 온도로 바꾸면 T%s = %d K, T%s = %d K 이다.' % (sub(1), T1, sub(2), T2), '등적 과정에서 P ∝ T 이므로 P%s = %s × %d/%d = %s기압' % (sub(2), num(P1), T2, T1, num(P2))]
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=st, core='등적 과정에서 압력은 절대 온도에 비례한다(샤를-게이뤼삭).', point='섭씨를 켈빈으로 고쳐 P ∝ T 를 쓴다.')
    if form == 'c':   # P-V 그래프(수직선)
        sc = rand_sch(r)
        V0 = r.randint(1, 6); Pa, Pb = r.sample(range(1, 7), 2)
        UA = r.choice([100, 150, 200, 300, 450, 600])
        UB = Fraction(UA * Pb, Pa)
        if UB.denominator != 1: return None
        UB = int(UB)
        Q = UB - UA
        st = {'A': (V0, Pa), 'B': (V0, Pb)}
        fig = FIG(pv_fig(sc, 7, 6, st, [('A', 'B', 'L', BL)], guides=('A', 'B'), lab_off={'A': (14, 4), 'B': (14, 4)}), '72%')
        ask = r.choice(['Q', 'UB'])
        if ask == 'Q':
            body = P('그림은 일정량의 이상 기체가 A에서 B로 변하는 과정을 나타낸 것이다. 상태 A에서 기체의 내부 에너지는 %d J이다. A → B 과정에서 기체가 %s 열량은?' % (UA, '흡수한' if Q > 0 else '방출한')) + fig
            right = '%d J' % abs(Q)
            wr = [UA, UB, abs(Q) * 2, abs(Q) // 2 + 10, UA + UB, abs(Q) + 100]
            st2 = ['A → B 는 부피가 일정한 등적 과정이므로 W = 0, Q = ΔU 이다.', 'U ∝ T ∝ P 이므로 U%s = %d × %s/%s = %d J' % (sub('B'), UA, num(Pb * sc.pstep), num(Pa * sc.pstep), UB), 'Q = ΔU = %d − %d = %d J (%s)' % (UB, UA, Q, '흡수' if Q > 0 else '방출')]
            return mc(body, right, ['%d J' % w for w in wr], r=r, lv='상', fam='c', sort='shuf', steps=st2, core='등적 과정: W = 0, Q = ΔU, U ∝ T ∝ P.', point='그래프에서 압력비를 읽어 내부 에너지 변화를 구한다.')
        body = P('그림은 일정량의 이상 기체가 A에서 B로 변하는 과정을 나타낸 것이다. 상태 A에서 기체의 내부 에너지가 %d J일 때 상태 B에서 내부 에너지는?' % UA) + fig
        wr = [UA, UB - UA if UB - UA != UA else UA + 100, UA * Pa // Pb if (UA * Pa) % Pb == 0 else UA + 50, UB * 2, UB + UA, abs(UB - UA) + 50]
        return mc(body, '%d J' % UB, ['%d J' % w for w in wr], r=r, lv='중', fam='c', sort='shuf',
                  steps=['A → B 는 등적 과정이므로 T ∝ P 이고 내부 에너지 U ∝ T 이다.', 'U%s = %d × %s/%s = %d J' % (sub('B'), UA, num(Pb * sc.pstep), num(Pa * sc.pstep), UB)],
                  core='부피가 일정하면 P ∝ T ∝ U.', point='압력비로 내부 에너지비를 구한다.')
    if form == 'e':   # 부호
        up = r.choice([True, False])
        sg = (UP, ZE, UP) if up else (DN, ZE, DN)
        body = P('부피가 일정한 용기 속 이상 기체를 %s할 때 ΔU, W, Q의 부호(⊕: 양, ⊖: 음, 0: 영)를 순서대로 옳게 나타낸 것은?' % ('가열' if up else '냉각'))
        combos = [(UP, UP, UP), (DN, DN, DN), (UP, ZE, UP), (DN, ZE, DN), (ZE, UP, UP), (DN, UP, ZE), (UP, DN, ZE), (UP, ZE, DN), (DN, ZE, UP), (ZE, ZE, ZE)]
        return mc(body, ', '.join(sg), [', '.join(c) for c in combos if c != sg], r=r, lv='하', fam='e', sort='shuf',
                  steps=['부피 변화가 없으므로 W = 0 이다.', '%s하면 온도가 %s므로 ΔU %s이고 Q = ΔU 이므로 Q %s이다.' % ('가열' if up else '냉각', '올라가' if up else '내려가', sg[0], sg[2])],
                  core='등적 과정: W = 0, Q = ΔU.', point='등적 과정의 부호를 구분한다.')
    if form == 'f':   # 두 기체 비교: 같은 열 → 같은 ΔU. 비율
        Q = r.choice([100, 200, 300, 400, 600]); dV = 0
        n = r.choice([2, 3, 4]); Pa_ = r.choice([1, 2])
        body = P('같은 종류의 이상 기체 A, B가 각각 부피가 변하지 않는 용기에 들어 있다. A, B의 내부 에너지가 각각 U%s = %d J, U%s = %d J일 때 같은 열량 %d J을 가했더니 내부 에너지가 모두 같은 양만큼 증가하였다. 가열 후 B의 내부 에너지가 A의 내부 에너지의 몇 배인가?' % (sub('A'), Q, sub('B'), Q * n, Q))
        a2, b2 = Q + Q, Q * n + Q
        right = fr_str(Fraction(b2, a2)) + '배'
        wr = [fr_str(Fraction(Q * n, Q)) + '배', fr_str(Fraction(a2, b2)) + '배', fr_str(Fraction(b2, a2) + 1) + '배', fr_str(Fraction(n)) + '배', fr_str(Fraction(b2 + 100, a2)) + '배']
        return mc(body, right, wr, r=r, lv='상', fam='f', sort='shuf',
                  steps=['등적 과정에서 W = 0 이므로 ΔU = Q = %d J 이다.' % Q, '가열 후 U%s = %d + %d = %d J, U%s = %d + %d = %d J' % (sub('A'), Q, Q, a2, sub('B'), Q * n, Q, b2), 'U%s / U%s = %d/%d = %s' % (sub('B'), sub('A'), b2, a2, fr_str(Fraction(b2, a2)))],
                  core='등적 과정에서 열을 가하면 모두 내부 에너지 증가가 된다.', point='처음 값에 증가량을 더한 뒤 비를 구한다.')
    stm = pick_stmts(r, _B69)
    return bogi('부피가 일정한 용기 속 이상 기체의 변화(등적 과정)에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv='하', fam='d',
                core='등적 과정: W = 0, Q = ΔU, P ∝ T.', point='등적 과정에서 일, 열, 압력, 온도의 관계를 이해한다.')


# ============================================================ ph070 등온 과정
_B70 = [
    ('이상 기체가 등온 팽창하는 동안 내부 에너지는 변하지 않는다.', True, '온도가 일정하므로 ΔU = 0 이다.', 'dU0'),
    ('이상 기체가 등온 팽창할 때 흡수한 열은 기체가 외부에 한 일과 같다.', True, 'ΔU = 0 이므로 Q = W 이다.', 'QW'),
    ('이상 기체가 등온 압축될 때 기체는 열을 흡수한다.', False, 'W < 0 이고 ΔU = 0 이므로 Q = W < 0 이다. 즉 열을 방출한다.', 'comp'),
    ('이상 기체가 등온 압축될 때 압력은 증가한다.', True, 'PV = 일정에서 V가 감소하면 P가 증가한다.', 'Pup'),
    ('등온 과정에서 기체의 압력과 부피는 서로 비례한다.', False, '압력과 부피는 반비례한다(PV = 일정, 보일 법칙).', 'prop'),
    ('등온 과정에서 압력과 부피의 곱은 일정하다.', True, '보일 법칙이다.', 'boyle'),
    ('등온 팽창하는 기체의 온도가 일정한 것은 기체가 열을 흡수하기 때문이다.', True, '일을 하면서 잃는 에너지를 흡수한 열이 채워 주기 때문이다.', 'why'),
    ('등온 팽창 과정에서 기체가 한 일은 P-V 그래프의 곡선 아래 넓이로 구할 수 있다.', True, '모든 과정에서 일 = P-V 곡선 아래 넓이이다.', 'area'),
    ('등온 과정에서는 기체와 외부 사이에 열의 출입이 없다.', False, '열의 출입이 없는 것은 단열 과정이다. 등온 과정에서는 Q = W 이다.', 'adia'),
    ('등온 과정의 P-V 그래프는 직선이다.', False, 'PV = 일정이므로 쌍곡선 모양의 곡선이다.', 'line'),
    ('절대 온도가 높은 등온선일수록 P-V 그래프에서 원점에서 멀리 떨어져 있다.', True, 'PV ∝ T 이므로 T가 클수록 PV 값이 크다.', 'far'),
    ('이상 기체가 등온 팽창하면 분자의 평균 운동 에너지가 감소한다.', False, '온도가 일정하므로 평균 운동 에너지가 변하지 않는다.', 'ke'),
    ('등온 팽창 중 기체가 한 일은 같은 부피 변화를 하는 등압 팽창(처음 압력 유지)에서의 일보다 작다.', True, '등온 팽창에서는 압력이 점점 감소하므로 곡선 아래 넓이가 처음 압력의 직사각형보다 작다.', 'cmpP'),
    ('부피가 2배가 되도록 등온 팽창하면 압력은 처음의 1/2배가 된다.', True, 'PV = 일정.', 'half'),
    ('부피가 2배가 되도록 등온 팽창하면 내부 에너지가 2배가 된다.', False, '온도가 일정하므로 내부 에너지는 변하지 않는다.', 'U2'),
    ('피스톤을 천천히 밀어 열전도가 잘되는 실린더 속 기체를 압축하면 등온 과정에 가깝다.', True, '느리게 변하면 열이 외부와 교환되어 온도가 일정하게 유지된다.', 'slow'),
    ('등온 과정에서 기체가 받은 일은 모두 내부 에너지로 저장된다.', False, 'ΔU = 0 이므로 받은 일은 열로 방출된다.', 'store'),
    ('등온 압축 과정에서 기체가 외부로부터 받은 일은 방출한 열과 같다.', True, 'Q = W 에서 W < 0, Q < 0.', 'rel'),
]

def _iso_pairs():
    out = []
    for c in (4, 6, 8, 9, 12, 16, 18, 24):
        for v in range(1, 9):
            if c % v == 0 and 1 <= c // v <= 8: out.append((c, v, c // v))
    return out

@T('ph070')
def g070(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'd', 'e', 'bogi', 'bogi', 'f'])
    if form == 'a':
        P1 = r.choice([1, 2, 3, 4, 6]); V1 = r.choice([2, 3, 4, 6, 8, 12]); V2 = r.choice([1, 2, 3, 4, 6, 8, 12, 16, 24])
        c = P1 * V1
        if V2 == V1 or (c % V2): return None
        P2 = c // V2
        ask = r.choice(['P', 'V'])
        if ask == 'P':
            body = P('온도가 일정하게 유지되는 실린더 속 이상 기체의 압력이 %d기압, 부피가 %d L이다. 이 기체의 부피를 %d L로 바꾸었을 때 압력은?' % (P1, V1, V2)) + FIG(cyl_pair(V1 / max(V1, V2) * 0.85 + 0.1, V2 / max(V1, V2) * 0.85 + 0.1, 'V%s' % sub(1), 'V%s' % sub(2), t1='처음', t2='나중'), '58%')
            right = '%d기압' % P2
            wr = ['%d기압' % (P1 + V2 - V1) if P1 + V2 - V1 > 0 else '%d기압' % (P2 + 2), '%s기압' % num(P1 * V2 / V1), '%d기압' % (P2 * 2), '%s기압' % num(P2 / 2.0), '%d기압' % P1, '%d기압' % (P1 * V1 * V2)]
            st = ['등온 과정이므로 보일 법칙 PV = 일정 이다.', '%d × %d = P%s × %d 에서 P%s = %d기압' % (P1, V1, sub(2), V2, sub(2), P2)]
            lv = '하'
        else:
            body = P('온도가 일정하게 유지되는 실린더 속 이상 기체의 압력이 %d기압, 부피가 %d L이다. 압력이 %d기압이 되었을 때 기체의 부피는?' % (P1, V1, P2))
            right = '%d L' % V2
            wr = ['%s L' % num(V1 * P2 / P1), '%d L' % (V1 + P2 - P1) if V1 + P2 - P1 > 0 else '%d L' % (V2 + 2), '%d L' % (V2 * 2), '%s L' % num(V2 / 2.0), '%d L' % V1, '%d L' % (P1 * V1 * P2)]
            st = ['등온 과정이므로 PV = 일정 이다.', '%d × %d = %d × V%s 에서 V%s = %d L' % (P1, V1, P2, sub(2), sub(2), V2)]
            lv = '하'
        return mc(body, right, wr, r=r, lv=lv, fam='a', sort='shuf', steps=st, core='등온 과정에서 PV = 일정(보일 법칙).', point='압력과 부피의 곱이 일정함을 이용한다.')
    if form == 'b':
        W = r.choice([100, 150, 200, 300, 400, 500, 800]); mode = r.choice(['ex', 'comp'])
        ask = r.choice(['Q', 'W', 'dU'])
        if mode == 'ex':
            if ask == 'Q':
                body = P('이상 기체가 일정한 온도에서 팽창하면서 외부에 %d J의 일을 하였다. 이 과정에서 기체가 흡수한 열량은?' % W)
                right = '%d J' % W; wr = ['0', '%d J' % (2 * W), '%d J' % (W // 2), '%d J' % (W + 100), '%d J' % (W * 10)]
                st = ['등온 과정이므로 ΔU = 0 이다.', 'Q = ΔU + W = 0 + %d = %d J (흡수)' % (W, W)]
            elif ask == 'W':
                body = P('이상 기체가 일정한 온도에서 팽창하면서 열 %d J을 흡수하였다. 이 과정에서 기체가 외부에 한 일은?' % W)
                right = '%d J' % W; wr = ['0', '%d J' % (2 * W), '%d J' % (W // 2), '%d J' % (W + 100), '%d J' % (W * 10)]
                st = ['등온 과정이므로 ΔU = 0 이다.', 'W = Q − ΔU = %d J' % W]
            else:
                body = P('이상 기체가 일정한 온도에서 팽창하면서 열 %d J을 흡수하고 외부에 일을 하였다. 이 과정에서 기체의 내부 에너지 변화는?' % W)
                right = '변화 없음'; wr = ['%d J 증가' % W, '%d J 감소' % W, '%d J 증가' % (2 * W), '%d J 감소' % (2 * W), '%d J 증가' % (W // 2)]
                st = ['온도가 일정하므로 U ∝ T 도 일정하다.', 'ΔU = 0 (Q = W = %d J)' % W]
        else:
            if ask == 'Q':
                body = P('이상 기체가 일정한 온도에서 압축되면서 외부로부터 %d J의 일을 받았다. 이 과정에서 기체가 방출한 열량은?' % W)
                right = '%d J' % W; wr = ['0', '%d J' % (2 * W), '%d J' % (W // 2), '%d J' % (W + 100), '%d J' % (W * 10)]
                st = ['등온 과정이므로 ΔU = 0 이다.', 'Q = ΔU + W = 0 + (−%d) = −%d J, 즉 열 %d J을 방출한다.' % (W, W, W)]
            elif ask == 'W':
                body = P('이상 기체가 일정한 온도에서 압축되면서 열 %d J을 방출하였다. 이 과정에서 기체가 외부로부터 받은 일은?' % W)
                right = '%d J' % W; wr = ['0', '%d J' % (2 * W), '%d J' % (W // 2), '%d J' % (W + 100), '%d J' % (W * 10)]
                st = ['등온 과정이므로 ΔU = 0, Q = W 이다.', 'Q = −%d J 이므로 W = −%d J, 즉 외부로부터 %d J의 일을 받는다.' % (W, W, W)]
            else:
                body = P('이상 기체가 일정한 온도에서 압축되면서 외부로부터 %d J의 일을 받았다. 이 과정에서 기체의 내부 에너지 변화는?' % W)
                right = '변화 없음'; wr = ['%d J 증가' % W, '%d J 감소' % W, '%d J 증가' % (2 * W), '%d J 감소' % (2 * W), '%d J 증가' % (W // 2)]
                st = ['온도가 일정하므로 ΔU = 0 이다.', '받은 일 %d J은 모두 열로 방출된다.' % W]
        return mc(body, right, wr, r=r, lv='하', fam='b', sort='shuf', steps=st, core='등온 과정에서 ΔU = 0 이므로 Q = W.', point='등온 과정에서 열과 일이 같음을 이용한다.')
    if form == 'c':   # 등온 그래프
        sc = rand_sch(r, 1, 1)
        c, va, pa = r.choice(_iso_pairs()); vb = r.choice([x for x in range(1, 9) if x != va and c % x == 0 and 1 <= c // x <= 7])
        pb = c // vb
        if pa > 7 or va > 7 or vb > 7: return None
        st = {'A': (va, pa), 'B': (vb, pb)}
        fig = FIG(pv_fig(sc, 8, 7, st, [('A', 'B', 'I', BL)], guides=('A', 'B'), w=310, h=232), '74%')
        ask = r.choice(['PB', 'VB'])
        pA, vA, vB, pB = pa * sc.pstep, va * sc.vstep, vb * sc.vstep, pb * sc.pstep
        pu, vu = sc.pl.split('(')[1][:-1], sc.vl.split('(')[1][:-1]
        if ask == 'PB':
            body = P('그림은 일정량의 이상 기체가 A에서 B로 변할 때의 P-V 그래프이다. 곡선은 온도가 일정한 변화를 나타낸다. 상태 A의 압력이 %s, 부피가 %s이고 상태 B의 부피가 %s일 때 상태 B의 압력은?' % (_unit_join(num(pA), pu), _unit_join(num(vA), vu), _unit_join(num(vB), vu))) + fig
            right = _unit_join(num(pB), pu)
            wr = [_unit_join(num(x), pu) for x in (pA * vB / vA * (vB / vA), pA, pA * vB / vA, pA + vA - vB, pB * 2, pB / 2.0, pB + pA)]
        else:
            body = P('그림은 일정량의 이상 기체가 A에서 B로 변할 때의 P-V 그래프이다. 곡선은 온도가 일정한 변화를 나타낸다. 상태 A의 압력이 %s, 부피가 %s이고 상태 B의 압력이 %s일 때 상태 B의 부피는?' % (_unit_join(num(pA), pu), _unit_join(num(vA), vu), _unit_join(num(pB), pu))) + fig
            right = _unit_join(num(vB), vu)
            wr = [_unit_join(num(x), vu) for x in (vA * pB / pA * (pB / pA), vA, vA * pB / pA, vA + pA - pB, vB * 2, vB / 2.0, vB + vA)]
        return mc(body, right, wr, r=r, lv='중', fam='c', sort='shuf',
                  steps=['곡선이 등온 과정이므로 PV = 일정 이다.', 'P%s V%s = %s × %s = %s' % (sub('A'), sub('A'), num(pA), num(vA), num(pA * vA)),
                         ('P%s = %s / %s = %s' % (sub('B'), num(pA * vA), num(vB), _unit_join(num(pB), pu))) if ask == 'PB' else ('V%s = %s / %s = %s' % (sub('B'), num(pA * vA), num(pB), _unit_join(num(vB), vu)))],
                  core='등온 과정의 P-V 그래프는 PV = 일정한 쌍곡선이다.', point='그래프 눈금과 보일 법칙으로 모르는 값을 구한다.')
    if form == 'd':   # 직선 경로와 등온 곡선의 일 비교 / 값의 범위
        sc = rand_sch(r, 1, 1)
        c, va, pa = r.choice([x for x in _iso_pairs() if x[0] in (6, 8, 12, 16, 18, 24)])
        cand = [x for x in range(1, 9) if x > va and c % x == 0 and 1 <= c // x <= 7]
        if not cand or pa > 7: return None
        vb = r.choice(cand); pb = c // vb
        if pb >= pa: return None
        st = {'A': (va, pa), 'B': (vb, pb)}
        sub_ = r.choice(['cmp', 'range'])
        segs = [('A', 'B', 'I', BL)]
        figs = pv_fig(sc, 8, 7, st, segs, guides=('A', 'B'), w=310, h=232)
        if sub_ == 'cmp':
            # 직선 경로와 등온 경로의 일 비교: 직선 W_L = (pa+pb)/2*(vb-va)
            sv = vb - va
            WL = (pa + pb) * sv / 2.0 * sc.J
            Wr = pb * sv * sc.J    # 아래 직사각형
            fig2 = Plot(310, 232, 8.45, 7.5, ml=52, mr=16, mt=28, mb=34)
            body = P('그림은 일정량의 이상 기체가 A에서 B로 변하는 두 가지 경로를 나타낸 것이다. 곡선은 온도가 일정한 변화이고 직선은 두 상태를 곧바로 연결한 것이다. 두 경로에서 기체가 한 일을 각각 W%s(곡선), W%s(직선)이라 할 때 옳은 것은?' % (sub('등온'), sub('직선')))
            f2 = pv_fig(sc, 8, 7, st, [('A', 'B', 'I', BL), ('A', 'B', 'L', RD)], guides=('A', 'B'), w=310, h=232, arrows=False)
            fig = FIG(f2, '74%')
            right = 'W%s > W%s' % (sub('직선'), sub('등온'))
            wr = ['W%s < W%s' % (sub('직선'), sub('등온')), 'W%s = W%s' % (sub('직선'), sub('등온')), 'W%s = 0' % sub('등온'), 'W%s = 0' % sub('직선'), 'W%s = 2W%s' % (sub('등온'), sub('직선'))]
            return mc(body + fig, right, wr, r=r, lv='상', fam='d', sort='shuf',
                      steps=['일은 P-V 그래프에서 경로 아래의 넓이이다.', '시점과 종점이 같을 때 직선 경로가 곡선(등온선)보다 위쪽에 있으므로(등온선은 아래로 볼록) 직선 아래 넓이가 더 크다.',
                             '직선: ½(%s+%s)×%s ×(눈금) 이 곡선보다 크다.' % (num(pa), num(pb), num(sv)) + ' 따라서 W직선 > W등온'],
                      core='일은 경로에 따라 다르며 P-V 그래프에서 경로 아래의 넓이이다.', point='등온 곡선과 직선 경로 아래 넓이를 비교한다.')
        # range: 등온 팽창에서 한 일의 범위로 가능한 값
        lo = pb * (vb - va) * sc.J       # 아래 직사각형
        hi = (pa + pb) * (vb - va) / 2.0 * sc.J
        ow = pa * va * math.log(vb / va) * sc.J
        assert lo < ow < hi
        step = 50 if sc.J < 200 else 100
        right_v = int(round(ow / step) * step)
        if not (lo < right_v < hi): return None
        fig = FIG(pv_fig(sc, 8, 7, st, [('A', 'B', 'I', BL)], guides=('A', 'B'), w=310, h=232), '74%')
        body = P('그림은 일정량의 이상 기체가 A에서 B까지 일정한 온도로 팽창할 때의 P-V 그래프이다. 곡선 아래 넓이를 위·아래의 직사각형·사다리꼴 넓이와 비교하여, 이 과정에서 기체가 한 일 W로 가장 적절한 값을 고르시오.%s' % unit_note(sc)) + fig
        cands = [lo - step * 2, lo - step, hi + step, hi + step * 3, int(lo * 0.5), int(hi * 1.5)]
        cands = [x for x in cands if x > 0 and not (lo < x < hi)]
        return mc(body, '%d J' % right_v, ['%d J' % x for x in cands], r=r, lv='상', fam='d',
                  steps=['곡선 아래 넓이는 B의 압력 높이의 직사각형(%s J)보다 크고 A와 B를 잇는 직선 아래 사다리꼴(%s J)보다 작다.' % (num(lo), num(hi)), '그러므로 %s J < W < %s J 이어야 하고, 이 범위 안에 있는 값은 %d J 뿐이다.' % (num(lo), num(hi), right_v)],
                  core='등온 곡선 아래 넓이는 직선 경로와 아래쪽 직사각형 넓이 사이의 값이다.', point='값을 직접 계산하지 않고 넓이의 상·하한으로 일의 크기를 추정한다.')
    if form == 'e':   # 두 등온선 비교(정성)
        n1 = r.choice([2.0, 2.5, 3.0]); n2 = r.choice([5.0, 6.0, 7.0])
        # 곡선 PV = c1 (낮은 T), c2 (높은 T). 점 A,B 가 c1 위, C,D 가 c2 위
        def hyper(c, v0, v1):
            return [(v0 + (v1 - v0) * i / 40.0, c / (v0 + (v1 - v0) * i / 40.0)) for i in range(41)]
        p = Plot(280, 220, 9.2, 7.6, ml=30, mr=16, mt=26, mb=30)
        p.axes('', '', xticks=(), yticks=(), grid=False)
        p.text(266, 207, 'V', 14, 'end', True, GR, True); p.text(40, 16, 'P', 14, 'start', True, GR, True)
        c1, c2 = 6.0, 12.0
        p.pl(hyper(c1, 1.0, 9.0), BL, 2.4); p.pl(hyper(c2, 1.7, 9.0), RD, 2.4)
        va, vb, vc = 1.8, 5.0, 3.0
        pts = {'A': (va, c1 / va, c1), 'B': (vb, c1 / vb, c1), 'C': (vc, c2 / vc, c2)}
        for nm, (vv, pp, cc) in pts.items():
            p.circ(p.px(vv), p.py(pp), 3.8, INK, INK, 1)
            p.text(p.px(vv) + 12, p.py(pp) - 7, nm, 14.5, 'middle', True, INK, True)
        p.text(p.px(8.7), p.py(c1 / 8.7) - 8, '(가)', 13, 'middle', True, BL)
        p.text(p.px(8.7), p.py(c2 / 8.7) - 8, '(나)', 13, 'middle', True, RD)
        body = P('그림은 일정량의 이상 기체의 두 등온 곡선 (가), (나)를 P-V 그래프에 나타낸 것이다. A, B는 (가) 위의 점이고 C는 (나) 위의 점이다. 세 상태의 내부 에너지 U%s, U%s, U%s를 옳게 비교한 것은?' % (sub('A'), sub('B'), sub('C'))) + FIG(p.svg(), '66%')
        right = 'U%s = U%s < U%s' % (sub('A'), sub('B'), sub('C'))
        wr = ['U%s < U%s < U%s' % (sub('A'), sub('B'), sub('C')), 'U%s = U%s > U%s' % (sub('A'), sub('B'), sub('C')), 'U%s > U%s = U%s' % (sub('A'), sub('B'), sub('C')), 'U%s < U%s = U%s' % (sub('A'), sub('B'), sub('C')), 'U%s = U%s = U%s' % (sub('A'), sub('B'), sub('C')), 'U%s > U%s > U%s' % (sub('A'), sub('B'), sub('C'))]
        return mc(body, right, wr, r=r, lv='중', fam='e', sort='shuf',
                  steps=['같은 등온 곡선 위의 점은 온도가 같으므로 U%s = U%s 이다.' % (sub('A'), sub('B')), '(나)는 (가)보다 원점에서 멀어 PV가 크므로 온도가 더 높다. 따라서 U%s > U%s = U%s' % (sub('C'), sub('A'), sub('B')) + ' 즉 ' + right],
                  core='등온 곡선에서 PV = nRT 이므로 원점에서 먼 곡선일수록 온도(내부 에너지)가 높다.', point='등온선의 위치로 온도·내부 에너지를 비교한다.')
    if form == 'f':   # 부피 두 배 등 비례
        n = r.choice([2, 3, 4]); P1 = r.choice([1, 2, 3, 4, 6]); expand = r.choice([True, False])
        if expand:
            body = P('온도가 일정한 이상 기체의 부피가 %d배가 되었다. 압력은 처음의 몇 배인가?' % n); right = '1/%d배' % n
            wr = ['%d배' % n, '%d배' % (n * n), '1/%d배' % (n * n), '1배', '%s배' % num(n / 2.0 + 0.5)]
            st = ['PV = 일정이므로 V가 %d배이면 P는 1/%d배이다.' % (n, n)]
        else:
            body = P('온도가 일정한 이상 기체의 압력이 %d배가 되었다. 부피는 처음의 몇 배인가?' % n); right = '1/%d배' % n
            wr = ['%d배' % n, '%d배' % (n * n), '1/%d배' % (n * n), '1배', '%s배' % num(n / 2.0 + 0.5)]
            st = ['PV = 일정이므로 P가 %d배이면 V는 1/%d배이다.' % (n, n)]
        return mc(body, right, wr, r=r, lv='하', fam='f', sort='shuf', steps=st, core='등온 과정에서 P와 V는 반비례한다.', point='보일 법칙의 비례 관계를 이해한다.')
    stm = pick_stmts(r, _B70)
    return bogi('일정한 온도에서 이상 기체가 변하는 등온 과정에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv='중', fam='g',
                core='등온 과정: ΔU = 0, Q = W, PV = 일정.', point='등온 과정에서 열·일·내부 에너지의 관계를 판단한다.')


# ============================================================ ph071 단열 과정
_B71 = [
    ('이상 기체가 단열 팽창하면 기체의 온도가 내려간다.', True, 'Q = 0 에서 W = −ΔU 이고 W > 0 이므로 ΔU < 0 이다.', 'cool'),
    ('이상 기체가 단열 압축되면 기체의 온도가 올라간다.', True, 'Q = 0 에서 W < 0 이므로 ΔU = −W > 0 이다.', 'heat'),
    ('단열 과정에서 기체와 외부 사이의 열 출입은 없다.', True, '단열 과정은 Q = 0 이다.', 'Q0'),
    ('단열 팽창하는 기체는 외부로부터 열을 흡수한다.', False, '단열이므로 열의 출입이 없고 내부 에너지가 일로 쓰인다.', 'abs'),
    ('단열 팽창 과정에서 기체가 한 일은 내부 에너지 감소량과 같다.', True, 'W = −ΔU 이다.', 'WU'),
    ('단열 압축 과정에서 기체가 받은 일은 내부 에너지 증가량과 같다.', True, '받은 일 = −W = ΔU.', 'WU2'),
    ('단열 과정에서 기체의 내부 에너지는 변하지 않는다.', False, 'ΔU = −W 이므로 일을 주고받으면 내부 에너지가 변한다.', 'dU0'),
    ('같은 부피까지 팽창할 때 단열 팽창 후의 압력이 등온 팽창 후의 압력보다 낮다.', True, '단열 팽창에서는 온도도 내려가므로 P-V 그래프에서 단열 곡선이 등온 곡선보다 가파르다.', 'steep'),
    ('P-V 그래프에서 같은 점을 지나는 단열 곡선은 등온 곡선보다 완만하다.', False, '단열 곡선이 더 가파르다.', 'gentle'),
    ('빠르게 팽창하는 기체는 열을 교환할 시간이 부족하여 단열 과정에 가깝다.', True, '열 교환이 거의 없다.', 'fast'),
    ('단열 팽창하는 기체의 압력은 부피에 반비례하여 변한다.', False, 'PV = 일정은 등온 과정이다. 단열 과정에서는 PV^γ = 일정으로 더 급격히 감소한다.', 'prop'),
    ('단열 압축 과정에서 기체의 압력은 증가한다.', True, '부피 감소와 온도 증가가 모두 압력을 높인다.', 'Pup'),
    ('단열 팽창하는 동안 기체 분자의 평균 운동 에너지는 감소한다.', True, '온도가 내려가기 때문이다.', 'ke'),
    ('단열 압축에서 기체가 한 일은 양(+)이다.', False, '압축되므로 기체가 한 일은 음(−)이다.', 'Wsign'),
    ('단열 용기 속 기체가 진공으로 자유 팽창하면 외부에 일을 한다.', False, '진공으로 팽창할 때는 밀어낼 외부 압력이 없어 일을 하지 않는다.', 'free'),
    ('단열된 용기 속 기체를 급히 압축하면 외부에서 해 준 일이 모두 기체의 내부 에너지로 저장된다.', True, 'Q = 0 이므로 ΔU = −W 이다.', 'store'),
    ('단열 과정에서 Q = 0 이므로 W와 ΔU의 부호는 서로 같다.', False, 'W = −ΔU 이므로 부호가 반대이다.', 'sign'),
    ('단열 팽창 후 기체의 내부 에너지는 처음보다 작다.', True, 'ΔU = −W < 0.', 'Uless'),
]

@T('ph071')
def g071(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'c', 'd', 'bogi', 'bogi', 'e', 'f'])
    if form in ('a', 'b'):
        exp_ = (form == 'a')
        W = r.choice([50, 100, 150, 200, 300, 400, 600]); T1 = r.choice([240, 300, 400, 500, 600]); U1 = r.choice([300, 400, 500, 600, 800, 1200])
        ask = r.choice(['U2', 'T2', 'dU'])
        dU = -W if exp_ else W
        U2 = U1 + dU
        if U2 <= 0: return None
        T2 = Fraction(T1 * U2, U1)
        if T2.denominator != 1: return None
        T2 = int(T2)
        fig = FIG(cyl_pair(0.4, 0.85, 'V%s' % sub(1), 'V%s' % sub(2), ins=True, t1='처음', t2='나중') if exp_ else cyl_pair(0.85, 0.4, 'V%s' % sub(1), 'V%s' % sub(2), ins=True, t1='처음', t2='나중'), '58%')
        base = '그림과 같이 단열된 실린더 속 이상 기체가 %s' % (('팽창하면서 외부에 %d J의 일을 하였다.' % W) if exp_ else ('압축되면서 외부로부터 %d J의 일을 받았다.' % W))
        if ask == 'dU':
            body = P(base + ' 이 과정에서 기체의 내부 에너지 변화는?') + fig
            right = ('%d J 감소' if exp_ else '%d J 증가') % W
            wr = [('%d J 증가' if exp_ else '%d J 감소') % W, '변화 없음', '%d J 증가' % (2 * W) if exp_ else '%d J 감소' % (2 * W), '%d J 감소' % (W // 2), '%d J 증가' % (W // 2)]
            return mc(body, right, wr, r=r, lv='하', fam='a' if exp_ else 'b', sort='shuf', steps=['단열 과정이므로 Q = 0 이다.', 'Q = ΔU + W 에서 ΔU = −W = %s%d J' % ('−' if exp_ else '+', W), right + '이다.'],
                      core='단열 과정에서 Q = 0, ΔU = −W.', point='단열 과정에서 일과 내부 에너지 변화의 관계를 이용한다.')
        if ask == 'U2':
            body = P(base + ' 처음 기체의 내부 에너지가 %d J이었다면 나중 내부 에너지는?' % U1) + fig
            right = '%d J' % U2
            wr = [U1 + W if exp_ else U1 - W, U1, W, U1 + 2 * W, abs(U1 - 2 * W) if U1 != 2 * W else U1 + 3 * W, U2 + 100]
            return mc(body, right, ['%d J' % w for w in wr], r=r, lv='중', fam='a' if exp_ else 'b', steps=['단열 과정이므로 Q = 0 이고 ΔU = −W = %s%d J 이다.' % ('−' if exp_ else '+', W), 'U%s = %d %s %d = %d J' % (sub(2), U1, '−' if exp_ else '+', W, U2)],
                      core='단열 과정: ΔU = −W.', point='일을 한 만큼 내부 에너지가 감소(받은 만큼 증가)한다.')
        body = P(base + ' 처음 기체의 내부 에너지는 %d J, 절대 온도는 %d K이었다. 나중 절대 온도는?' % (U1, T1)) + fig
        right = '%d K' % T2
        wr = [T1 + (W if not exp_ else -W) // 2, T1, T2 + 60, T1 * 2 - T2 if T1 * 2 - T2 > 0 else T2 + 120, int(T1 * (U1 + W) / U1) if not exp_ else int(T1 * (U1 + W) / U1), T2 * 2]
        return mc(body, right, ['%d K' % w for w in wr], r=r, lv='상', fam='a' if exp_ else 'b',
                  steps=['단열 과정이므로 ΔU = −W = %s%d J, U%s = %d %s %d = %d J' % ('−' if exp_ else '+', W, sub(2), U1, '−' if exp_ else '+', W, U2), 'U ∝ T 이므로 T%s = %d × %d/%d = %d K' % (sub(2), T1, U2, U1, T2)],
                  core='단열 과정에서 ΔU = −W 이고 U ∝ T.', point='ΔU를 구한 뒤 U ∝ T 로 나중 온도를 구한다.')
    if form == 'c':   # 등온 vs 단열 곡선 비교
        expand = r.choice([True, False])
        c1 = 6.0
        va, vb = (2.0, 5.5) if expand else (5.5, 2.0)
        pa = c1 / va
        p = Plot(290, 222, 9.2, 8.2, ml=30, mr=16, mt=26, mb=30)
        p.axes('', '', xticks=(), yticks=(), grid=False)
        p.text(276, 209, 'V', 14, 'end', True, GR, True); p.text(40, 16, 'P', 14, 'start', True, GR, True)
        iso = curve_pts('I', (va, pa), (vb, c1 / vb)); pb_iso = c1 / vb
        pb_ad = pa * (va / vb) ** GAM
        ad = curve_pts('A', (va, pa), (vb, pb_ad))
        p.pl(iso, BL, 2.5); p.pl(ad, RD, 2.5)
        for nm, (vv, pp) in {'A': (va, pa), 'B': (vb, pb_iso), 'C': (vb, pb_ad)}.items():
            p.circ(p.px(vv), p.py(pp), 3.8, INK, INK, 1)
            dx, dy = (-12, -6) if nm == 'A' else ((12, -6) if nm == 'B' else (12, 15))
            if not expand and nm == 'B': dx, dy = (-12, 0)
            if not expand and nm == 'C': dx, dy = (-12, -2)
            if not expand and nm == 'A': dx, dy = (12, 18)
            p.text(p.px(vv) + dx, p.py(pp) + dy, nm, 14.5, 'middle', True, INK, True)
        p.text(p.px(7.0 if expand else 7.2), p.py(c1 / 7.0) - 10 if expand else p.py(c1 / 7.2) - 10, '', 11)
        body = P('그림은 일정량의 이상 기체의 상태가 A에서 B(등온선, 파란색)와 C(단열 곡선, 붉은색)로 %s 과정을 나타낸 것이다. B와 C의 부피는 같다. 세 상태의 절대 온도 T%s, T%s, T%s를 옳게 비교한 것은?' % ('팽창하는' if expand else '압축되는', sub('A'), sub('B'), sub('C'))) + FIG(p.svg(), '66%')
        if expand:
            right = 'T%s = T%s > T%s' % (sub('A'), sub('B'), sub('C'))
            st = ['A → B는 등온 과정이므로 T%s = T%s 이다.' % (sub('A'), sub('B')), 'A → C는 단열 팽창이므로 온도가 내려가 T%s > T%s 이다. (같은 부피에서 압력도 P%s < P%s)' % (sub('A'), sub('C'), sub('C'), sub('B'))]
        else:
            right = 'T%s < T%s = T%s' % (sub('A'), sub('B'), sub('C')) if False else 'T%s = T%s < T%s' % (sub('A'), sub('B'), sub('C'))
            st = ['A → B는 등온 과정이므로 T%s = T%s 이다.' % (sub('A'), sub('B')), 'A → C는 단열 압축이므로 온도가 올라가 T%s > T%s 이다. (같은 부피에서 압력도 P%s > P%s)' % (sub('C'), sub('A'), sub('C'), sub('B'))]
        pairs = ['T%s = T%s > T%s' % (sub('A'), sub('B'), sub('C')), 'T%s = T%s < T%s' % (sub('A'), sub('B'), sub('C')), 'T%s < T%s < T%s' % (sub('A'), sub('B'), sub('C')), 'T%s > T%s > T%s' % (sub('A'), sub('B'), sub('C')), 'T%s = T%s = T%s' % (sub('A'), sub('B'), sub('C')), 'T%s < T%s = T%s' % (sub('A'), sub('B'), sub('C')), 'T%s > T%s = T%s' % (sub('A'), sub('B'), sub('C'))]
        return mc(body, right, [x for x in pairs if x != right], r=r, lv='중', fam='c', sort='shuf', steps=st, core='같은 점에서 출발하는 단열 곡선은 등온 곡선보다 가파르다. 팽창 시 단열은 온도 하강, 압축 시 온도 상승.', point='등온선과 단열 곡선을 구분해 상태 A, B, C의 온도를 비교한다.')
    if form == 'd':   # 표에서 단열 팽창 찾기
        procs = [('등온 팽창', (ZE, UP, UP)), ('등온 압축', (ZE, DN, DN)), ('단열 팽창', (DN, UP, ZE)), ('단열 압축', (UP, DN, ZE)), ('등적 가열', (UP, ZE, UP)), ('등적 냉각', (DN, ZE, DN)), ('등압 팽창', (UP, UP, UP)), ('등압 압축', (DN, DN, DN))]
        target = r.choice([2, 3])
        others = r.sample([i for i in range(8) if i != target], 4)
        idx = others + [target]; r.shuffle(idx)
        labs = ['(가)', '(나)', '(다)', '(라)', '(마)']
        rows = [[labs[i], procs[j][1][0], procs[j][1][1], procs[j][1][2]] for i, j in enumerate(idx)]
        body = P('표는 이상 기체가 다섯 가지 과정을 거칠 때 내부 에너지 변화 ΔU, 기체가 외부에 한 일 W, 기체가 흡수한 열 Q의 부호(⊕: 양, ⊖: 음, 0: 영)를 나타낸 것이다. 이 중 %s에 해당하는 것은?' % procs[target][0]) + table(['과정', 'ΔU', 'W', 'Q'], rows)
        ai = idx.index(target)
        return mc_list(body, labs, ai, steps=['%s : ΔU %s, W %s, Q %s' % (procs[target][0], *procs[target][1]), '이와 같은 부호를 가진 행은 %s이다.' % labs[ai]],
                       lv='중', fam='d', core='단열 팽창은 Q = 0, W > 0, ΔU < 0 이다. 단열 압축은 Q = 0, W < 0, ΔU > 0.', point='부호 표에서 Q = 0인 행으로 단열 과정을 찾고 W의 부호로 팽창·압축을 구분한다.')
    if form == 'e':   # 수치: 단열 팽창 후 압력 비교 (정성) — P-V 그래프 눈금 읽기
        sc = rand_sch(r, 1, 1)
        W = r.choice([100, 200, 300, 400]); Vm = r.choice([2, 4, 6, 8])
        body = P('단열 용기 속 이상 기체를 압축하는 동안 외부가 기체에 %d J의 일을 하였다. 이 압축 과정에서 기체의 온도 변화와 열 출입을 옳게 짝지은 것은?' % W)
        right = '온도 상승, 열의 출입 없음'
        wr = ['온도 하강, 열의 출입 없음', '온도 일정, 열 %d J 방출' % W, '온도 일정, 열 %d J 흡수' % W, '온도 상승, 열 %d J 흡수' % W, '온도 하강, 열 %d J 방출' % W]
        return mc(body, right, wr, r=r, lv='하', fam='e', sort='shuf', steps=['단열이므로 Q = 0 이다.', '기체가 받은 일 %d J이 내부 에너지 증가로 바뀌어 온도가 상승한다.' % W],
                  core='단열 압축에서는 외부가 해 준 일이 내부 에너지(온도)를 높인다.', point='Q = 0 일 때 W와 ΔU의 부호 관계를 이용한다.')
    if form == 'f':   # 실험 상황: 단열 팽창 시 ΔU/Q 같은 선택
        a_ = r.choice([('단열 팽창', '내려간다', '감소', '일을 한다')])
        U1 = r.choice([200, 300, 400, 500, 600, 800]); T1 = r.choice([300, 400, 500, 600])
        frac_ = r.choice([Fraction(3, 4), Fraction(1, 2), Fraction(2, 3), Fraction(4, 5), Fraction(3, 5)])
        if (U1 * frac_).denominator != 1 or (T1 * frac_).denominator != 1: return None
        U2 = int(U1 * frac_); W = U1 - U2; T2 = int(T1 * frac_)
        body = P('단열된 실린더 속 이상 기체가 팽창하여 절대 온도가 %d K에서 %d K으로 내려갔다. 처음 내부 에너지가 %d J일 때 기체가 외부에 한 일은?' % (T1, T2, U1))
        wr = [U1, U2, U1 + U2, U1 * 2, W // 2 if W % 2 == 0 else W + 50, 0]
        return mc(body, '%d J' % W, ['%d J' % w for w in wr], r=r, lv='상', fam='f',
                  steps=['U ∝ T 이므로 나중 내부 에너지 U%s = %d × %d/%d = %d J' % (sub(2), U1, T2, T1, U2), 'ΔU = %d − %d = −%d J' % (U2, U1, W), '단열(Q = 0)이므로 W = −ΔU = %d J' % W],
                  core='단열 과정: W = −ΔU, U ∝ T.', point='온도비로 내부 에너지 변화를 구하고 W = −ΔU 로 일을 구한다.')
    stm = pick_stmts(r, _B71)
    return bogi('열의 출입이 없는 단열 과정에서 이상 기체의 변화에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv='중', fam='g',
                core='단열 과정: Q = 0, W = −ΔU. 팽창하면 온도 하강, 압축하면 온도 상승.', point='단열 과정에서 일·내부 에너지·온도의 관계를 판단한다.')


# ============================================================ ph072 P-V 그래프에서 기체가 한 일
def area_seg(a, b):
    """(V,P) → (V,P) 직선 구간의 '그림 단위' 일(기체가 한 일, 부피 증가 +)."""
    return (b[0] - a[0]) * (a[1] + b[1]) / 2.0

def jnum(x, sc):
    return x * sc.J

def jstr(x):
    """부호 있는 일 값 문자열: 음수는 −."""
    x = round(x, 6)
    return ('−' if x < 0 else '') + num(abs(x)) + ' J'

_B72 = [
    ('P-V 그래프에서 기체가 한 일은 그래프 아래의 넓이와 같다.', True, '일 W = ∫P dV 는 곡선(직선) 아래 넓이이다.', 'area'),
    ('부피가 감소하는 과정에서 기체가 한 일은 음(−)이다.', True, 'ΔV < 0 이므로 W < 0 이다.', 'neg'),
    ('부피가 변하지 않는 과정에서 기체가 한 일은 0이다.', True, '넓이가 0이다.', 'zero'),
    ('같은 처음 상태와 나중 상태를 잇는 서로 다른 경로에서 기체가 한 일은 항상 같다.', False, '일은 경로 아래의 넓이로, 경로에 따라 다르다.', 'path'),
    ('압력이 일정한 과정에서 기체가 한 일은 압력과 부피 변화량의 곱이다.', True, 'W = PΔV 는 직사각형 넓이이다.', 'rect'),
    ('P-V 그래프에서 같은 부피 변화라면 압력이 더 큰 과정에서 기체가 한 일이 더 크다.', True, '넓이가 더 크다.', 'bigP'),
    ('팽창하는 과정에서 압력이 감소하면 기체가 한 일은 처음 압력 × 부피 변화량보다 크다.', False, '압력이 처음보다 작아지므로 넓이가 처음 압력의 직사각형보다 작다.', 'dec'),
    ('기체가 외부로부터 일을 받는 과정에서는 부피가 증가한다.', False, '일을 받으면 부피가 감소(압축)한다.', 'recv'),
    ('P-V 그래프에서 같은 경로를 반대 방향으로 진행하면 기체가 한 일의 부호가 바뀐다.', True, '부피 변화의 방향이 바뀌므로 W의 부호가 반대가 된다.', 'rev'),
    ('P-V 그래프에서 일을 구할 때 온도는 필요하지 않다.', True, '일은 압력과 부피만으로 구한다.', 'noT'),
]

def _pv_pts(r, n=2, vmax=7, pmax=5):
    """n+1 개의 상태 (V,P) 정수 좌표. 인접 상태는 서로 달라야 한다."""
    pts = []
    for _ in range(40):
        pts = [(r.randint(1, vmax), r.randint(1, pmax)) for _ in range(n + 1)]
        if all(pts[i] != pts[i + 1] for i in range(n)): return pts
    return None

@T('ph072')
def g072(r, k):
    form = r.choice(['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c', 'd', 'd', 'e', 'g'])
    sc = rand_sch(r)
    if form in ('a', 'e'):
        for _ in range(30):
            A = (r.randint(1, 6), r.randint(1, 5)); B = (r.randint(1, 7), r.randint(1, 5))
            if A[0] != B[0] and A[1] != B[1]: break
        else:
            return None
        W = area_seg(A, B) * sc.J
        names = r.choice([('A', 'B'), ('A', 'B'), ('B', 'A')])
        st = {names[0]: A, names[1]: B}
        s1, s2 = names
        fig = FIG(pv_fig(sc, 7, 5, st, [(s1, s2, 'L', BL)], guides=(s1, s2)), '72%')
        ask = r.choice(['by', 'recv']) if W < 0 else 'by'
        if ask == 'by':
            body = P('그림은 일정량의 이상 기체의 상태가 %s에서 %s로 직선을 따라 변하는 과정을 P-V 그래프로 나타낸 것이다. 이 과정에서 기체가 한 일은?%s' % (s1, s2, unit_note(sc))) + fig
            right = jstr(W)
            wr = [jstr(-W), jstr(W / 2.0), jstr(W * 2), jstr(A[1] * (B[0] - A[0]) * sc.J), jstr(B[1] * (B[0] - A[0]) * sc.J), jstr(max(A[1], B[1]) * abs(B[0] - A[0]) * sc.J), jstr(A[1] * A[0] * sc.J)]
        else:
            body = P('그림은 일정량의 이상 기체의 상태가 %s에서 %s로 직선을 따라 변하는 과정을 P-V 그래프로 나타낸 것이다. 이 과정에서 기체가 외부로부터 받은 일은?%s' % (s1, s2, unit_note(sc))) + fig
            right = jstr(-W)
            wr = [jstr(W), jstr(W / 2.0), jstr(W * 2), jstr(A[1] * abs(B[0] - A[0]) * sc.J), jstr(B[1] * abs(B[0] - A[0]) * sc.J), jstr(max(A[1], B[1]) * abs(B[0] - A[0]) * sc.J)]
        sgnw = W if ask == 'by' else -W
        # 풀이
        dv = (B[0] - A[0]) * sc.vstep
        st_ = ['A 와 B 의 좌표를 읽으면 %s : (V, P) = (%s, %s), %s : (%s, %s) 이다.' % (s1, vol_str(sc, A[0]), pre_str(sc, A[1]), s2, vol_str(sc, B[0]), pre_str(sc, B[1])),
               '일 = 직선 아래 사다리꼴 넓이 = ½ × (%s + %s) × %s' % (num(A[1] * sc.pstep), num(B[1] * sc.pstep), num(abs(dv))) + ' (눈금 1칸 = %s J)' % num(sc.J / (sc.pstep * sc.vstep) * 1 if False else sc.J),
               '격자 넓이로 계산하면 ½ × (%d + %d) × %d = %s 칸 → %s J%s' % (A[1], B[1], abs(B[0] - A[0]), num((A[1] + B[1]) * abs(B[0] - A[0]) / 2.0), num(abs(W)), '' if (B[0] > A[0]) == (ask == 'by') else ' (부피가 감소하므로 기체가 한 일은 음수이다)')]
        if ask != 'by': st_.append('외부로부터 받은 일 = −(기체가 한 일) = %s' % right)
        return mc(body, right, wr, r=r, lv='중', fam='a', sort='shuf', steps=st_,
                  core='P-V 그래프에서 기체가 한 일은 경로 아래의 넓이이며, 부피가 증가하면 +, 감소하면 −이다.', point='격자 눈금을 읽어 사다리꼴 넓이로 일을 구하고 부호를 정한다.')
    if form == 'b':
        for _ in range(40):
            pts = _pv_pts(r, 2)
            if pts is None: continue
            A, B, C = pts
            if A[0] == B[0] == C[0]: continue
            if (B[0] - A[0]) * (C[0] - B[0]) == 0 and False: continue
            break
        else:
            return None
        W1, W2 = area_seg(A, B) * sc.J, area_seg(B, C) * sc.J
        W = W1 + W2
        if abs(W) < 1e-9 and r.random() < 0.7: return None
        st = {'A': A, 'B': B, 'C': C}
        segs = [('A', 'B', 'L', BL), ('B', 'C', 'L', RD)]
        fig = FIG(pv_fig(sc, 7, 5, st, segs, guides=('A', 'B', 'C')), '72%')
        body = P('그림은 일정량의 이상 기체의 상태가 A → B → C로 변하는 과정을 P-V 그래프로 나타낸 것이다. A → B → C 과정에서 기체가 한 일은?%s' % unit_note(sc)) + fig
        wr = [jstr(W1), jstr(W2), jstr(abs(W1) + abs(W2)), jstr(W1 - W2), jstr(-W), jstr(max(A[1], B[1], C[1]) * (abs(C[0] - A[0])) * sc.J), jstr(W * 2)]
        return mc(body, jstr(W), wr, r=r, lv='중' if W1 * W2 == 0 or (B[0] - A[0]) * (C[0] - B[0]) > 0 else '상', fam='b', sort='shuf',
                  steps=['A → B : 일 = %s J (사다리꼴 넓이 %s칸)' % (num(W1), num(area_seg(A, B))), 'B → C : 일 = %s J (넓이 %s칸)' % (num(W2), num(area_seg(B, C))), '전체 W = (%s) + (%s) = %s J' % (num(W1), num(W2), num(W))],
                  core='구간별 일(부호 포함)을 더하면 전체 일이다.', point='부피가 증가하는 구간은 +, 감소하는 구간은 −로 넓이를 합한다.')
    if form == 'c':   # 두 경로 비교
        for _ in range(40):
            A = (r.randint(1, 3), r.randint(3, 5)); C = (r.randint(4, 7), r.randint(1, 2))
            break
        # 경로 1: A → B(오른쪽 수평) → C(수직), 경로 2: A → D(수직) → C(수평)
        B = (C[0], A[1]); D = (A[0], C[1])
        W1 = A[1] * (C[0] - A[0]) * sc.J         # 위쪽 수평 길
        W2 = C[1] * (C[0] - A[0]) * sc.J         # 아래쪽 수평 길
        st = {'A': A, 'B': B, 'C': C, 'D': D}
        segs = [('A', 'B', 'L', BL), ('B', 'C', 'L', BL), ('A', 'D', 'L', RD), ('D', 'C', 'L', RD)]
        fig = FIG(pv_fig(sc, 7, 5, st, segs, guides=('A', 'B', 'C', 'D'), arrows=False, lab_off={'A': (-10, -5), 'B': (10, -6), 'C': (10, 14), 'D': (-10, 14)}), '74%')
        ask = r.choice(['diff', 'ratio', 'W1'])
        if ask == 'diff':
            body = P('그림은 일정량의 이상 기체가 상태 A에서 C로 변하는 두 가지 경로 A → B → C(파란색)와 A → D → C(붉은색)를 P-V 그래프에 나타낸 것이다. 두 경로에서 기체가 한 일의 차는?%s' % unit_note(sc)) + fig
            right = jstr(W1 - W2)
            wr = [jstr(W1 + W2), jstr(W1), jstr(W2), jstr((W1 - W2) / 2.0), jstr((W1 - W2) * 2), jstr(0)]
            st_ = ['A → B → C : 부피가 증가하는 구간은 A → B (압력 %s) 뿐이므로 W%s = %s × %s = %s J' % (pre_str(sc, A[1]), sub(1), num(A[1] * sc.pstep), num((C[0] - A[0]) * sc.vstep), num(W1)),
                   'A → D → C : 부피가 증가하는 구간은 D → C (압력 %s) 뿐이므로 W%s = %s J' % (pre_str(sc, C[1]), sub(2), num(W2)), '차 = %s − %s = %s J' % (num(W1), num(W2), num(W1 - W2))]
            core_ = '일은 경로에 따라 다르다. 부피가 변하지 않는 구간의 일은 0.'
        elif ask == 'ratio':
            g = math.gcd(int(A[1]), int(C[1]))
            body = P('그림은 일정량의 이상 기체가 상태 A에서 C로 변하는 두 가지 경로 A → B → C(파란색)와 A → D → C(붉은색)를 P-V 그래프에 나타낸 것이다. 파란색 경로에서 한 일 W%s과 붉은색 경로에서 한 일 W%s의 비 W%s : W%s는?' % (sub(1), sub(2), sub(1), sub(2))) + fig
            right = '%d : %d' % (A[1] // g, C[1] // g)
            wr = ['%d : %d' % (C[1] // g, A[1] // g), '%d : %d' % (A[0], C[0]), '1 : 1', '%d : %d' % (A[1] + 1, C[1] + 1), '%d : %d' % (A[1] * A[0], C[1] * C[0])]
            st_ = ['두 경로 모두 부피 변화량 ΔV는 같다. W%s = %d × ΔV(칸), W%s = %d × ΔV(칸)' % (sub(1), A[1], sub(2), C[1]), 'W%s : W%s = %d : %d = %s' % (sub(1), sub(2), A[1], C[1], right)]
            core_ = '압력이 일정한 구간의 일은 PΔV 이므로 같은 ΔV에서는 압력의 비가 일의 비이다.'
        else:
            body = P('그림은 일정량의 이상 기체가 상태 A에서 C로 변하는 두 가지 경로 A → B → C(파란색)와 A → D → C(붉은색)를 P-V 그래프에 나타낸 것이다. 파란색 경로에서 기체가 한 일은?%s' % unit_note(sc)) + fig
            right = jstr(W1)
            wr = [jstr(W2), jstr(W1 + W2), jstr(W1 - W2), jstr(-W1), jstr(W1 / 2.0), jstr((A[1] + C[1]) * (C[0] - A[0]) / 2.0 * sc.J)]
            st_ = ['A → B 는 압력 %s의 등압 팽창이다 : W = %s × %s = %s J' % (pre_str(sc, A[1]), num(A[1] * sc.pstep), num((C[0] - A[0]) * sc.vstep), num(W1)), 'B → C 는 부피가 일정하므로 일이 0이다.', '따라서 W = %s J' % num(W1)]
            core_ = '등압 구간은 직사각형 넓이, 등적 구간의 일은 0이다.'
        return mc(body, right, wr, r=r, lv='중' if ask != 'diff' else '상', fam='c', sort='shuf', steps=st_, core=core_, point='경로에 따라 P-V 그래프 아래 넓이가 달라짐을 확인한다.')
    if form == 'd':   # 구간 일의 비
        for _ in range(40):
            pts = _pv_pts(r, 2)
            if pts is None: continue
            A, B, C = pts
            if (B[0] - A[0]) * (C[0] - B[0]) <= 0: continue
            break
        else:
            return None
        W1, W2 = area_seg(A, B), area_seg(B, C)
        if abs(W1) < 1e-9 or abs(W2) < 1e-9: return None
        st = {'A': A, 'B': B, 'C': C}
        fig = FIG(pv_fig(sc, 7, 5, st, [('A', 'B', 'L', BL), ('B', 'C', 'L', RD)], guides=('A', 'B', 'C')), '72%')
        body = P('그림은 일정량의 이상 기체의 상태가 A → B → C로 변하는 과정을 P-V 그래프로 나타낸 것이다. A → B 과정에서 기체가 한 일 W%s과 B → C 과정에서 기체가 한 일 W%s의 비 W%s : W%s는?' % (sub(1), sub(2), sub(1), sub(2))) + fig
        right = ratio_str(Fraction(W1).limit_denominator(4), Fraction(W2).limit_denominator(4))
        a_, b_ = Fraction(W1).limit_denominator(4), Fraction(W2).limit_denominator(4)
        if abs(a_) != abs(W1) and abs(float(a_) - W1) > 1e-9: return None
        a_, b_ = abs(a_), abs(b_)
        right = ratio_str(a_, b_)
        wr = [ratio_str(b_, a_), ratio_str(abs(B[0] - A[0]), abs(C[0] - B[0])), ratio_str(abs(A[1] + B[1]), abs(B[1] + C[1])) if (B[1] + C[1]) else '1 : 1', ratio_str(max(A[1], B[1]) * abs(B[0] - A[0]), max(B[1], C[1]) * abs(C[0] - B[0])), '1 : 1', ratio_str(a_ + 1, b_)]
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf',
                  steps=['A → B : 사다리꼴 넓이 = ½ × (%d + %d) × %d = %s 칸' % (A[1], B[1], abs(B[0] - A[0]), num(a_)), 'B → C : ½ × (%d + %d) × %d = %s 칸' % (B[1], C[1], abs(C[0] - B[0]), num(b_)), 'W%s : W%s = %s' % (sub(1), sub(2), right)],
                  core='구간별 일은 그래프 아래 넓이이다.', point='사다리꼴 넓이를 격자에서 구해 비를 낸다.')
    # g: bogi — 그래프에서 읽는 비교
    for _ in range(40):
        pts = _pv_pts(r, 2)
        if pts is None: continue
        A, B, C = pts
        break
    st = {'A': A, 'B': B, 'C': C}
    WAB, WBC = area_seg(A, B), area_seg(B, C)
    WAC = area_seg(A, C)
    cand = []
    def add(txt, truth, why): cand.append((txt, truth, why))
    add('A → B 과정에서 기체는 외부에 일을 한다.', WAB > 0, 'A → B에서 부피가 %s하므로 W %s 0 이다.' % ('증가' if WAB > 0 else '감소', '>' if WAB > 0 else '<') if A[0] != B[0] else '부피가 변하지 않아 W = 0 이다.')
    add('B → C 과정에서 기체가 한 일은 0이 아니다.', B[0] != C[0], '부피가 %s.' % ('변하므로 W ≠ 0' if B[0] != C[0] else '변하지 않아 W = 0'))
    if abs(WAB) != abs(WBC): add('A → B 과정에서 기체가 한 일의 크기는 B → C 과정에서 한 일의 크기보다 크다.', abs(WAB) > abs(WBC), '|W%s| = %s칸, |W%s| = %s칸.' % (sub('AB'), num(abs(WAB)), sub('BC'), num(abs(WBC))))
    if abs(WAB + WBC - WAC) > 1e-9 or True:
        add('A → B → C 과정에서 기체가 한 일은 A에서 C로 직선을 따라 변할 때 한 일과 같다.', abs(WAB + WBC - WAC) < 1e-9, 'A → B → C : %s칸, A → C 직선 : %s칸.' % (num(WAB + WBC), num(WAC)))
    add('A → B → C 과정에서 기체가 한 일은 양(+)이다.', (WAB + WBC) > 1e-9, 'W = %s 칸 이다.' % num(WAB + WBC))
    if len(cand) < 3: return None
    cand = r.sample(cand, 3)
    fig = FIG(pv_fig(sc, 7, 5, st, [('A', 'B', 'L', BL), ('B', 'C', 'L', RD)], guides=('A', 'B', 'C')), '72%')
    return bogi('그림은 일정량의 이상 기체의 상태가 A → B → C로 변하는 과정을 P-V 그래프로 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', cand, pre=fig, r=r, ask='', lv='중', fam='g',
                core='P-V 그래프에서 일은 경로 아래의 넓이이며 부피 변화의 방향으로 부호가 정해진다.', point='그래프의 좌표를 읽고 구간별 일을 비교한다.')


# ============================================================ ph073 P-V 그래프의 과정 판별과 부호
ALL_PROC = [('isobaric', 1.6), ('isobaric', 1 / 1.6), ('isochoric', 1.7), ('isochoric', 1 / 1.7),
            ('isothermal', 1.6), ('isothermal', 1 / 1.6), ('adiabatic', 1.6), ('adiabatic', 1 / 1.6)]

def _star_fig(procs, names, w=290, h=225):
    """한 점 A 에서 여러 과정으로 뻗는 숫자 없는 P-V 그래프."""
    A = (4.6, 3.8)
    states = {'A': A}
    segs = []
    for (kind, f), nm in zip(procs, names):
        b = proc_end(kind, A, f)
        check_signs(kind, A, b, f)
        states[nm] = b
        segs.append(('A', nm, proc_draw_kind(kind), BL))
    off = {'A': (-14, 18)}
    return pv_fig(None, 9, 9, states, segs, numbered=False, grid=False, w=w, h=h, lab_off=off)

_PROP = [
    ('열의 출입이 없는', lambda s: s[2] == ZE),
    ('내부 에너지가 변하지 않는', lambda s: s[0] == ZE),
    ('기체가 외부에 일을 하지 않는', lambda s: s[1] == ZE),
    ('기체가 열을 방출하는', lambda s: s[2] == DN),
    ('기체가 열을 흡수하는', lambda s: s[2] == UP),
    ('기체의 온도가 올라가는', lambda s: s[0] == UP),
    ('기체의 온도가 내려가는', lambda s: s[0] == DN),
    ('기체가 외부에 일을 하는', lambda s: s[1] == UP),
    ('기체가 외부로부터 일을 받는', lambda s: s[1] == DN),
    ('기체가 외부에 일을 하면서 내부 에너지가 감소하는', lambda s: s[1] == UP and s[0] == DN),
    ('기체가 열을 흡수하면서 외부로부터 일을 받는', lambda s: s[2] == UP and s[1] == DN),
    ('기체가 열을 방출하면서 내부 에너지가 감소하는', lambda s: s[2] == DN and s[0] == DN),
]

def _stmt_for(r, step_name, kind, f, force=None):
    """한 구간에 대한 (문장, 참거짓, 풀이문)."""
    dU, W, Q = proc_signs(kind, f)
    pname = proc_short(kind, f)
    why_base = '%s는 %s이므로 ΔU %s, W %s, Q %s 이다.' % (step_name, pname, dU, W, Q)
    qty = force or r.choice(['T', 'U', 'W', 'Wr', 'Q', 'Q0'])
    claim = r.random() < 0.5
    if qty == 'T':
        word = {UP: '올라간다', DN: '내려간다', ZE: '변하지 않는다'}
        ws = r.choice(['올라간다', '내려간다', '변하지 않는다'])
        return ('%s에서 기체의 온도는 %s.' % (step_name, ws), word[dU] == ws, why_base)
    if qty == 'U':
        word = {UP: '증가한다', DN: '감소한다', ZE: '변하지 않는다'}
        ws = r.choice(['증가한다', '감소한다', '변하지 않는다'])
        return ('%s에서 기체의 내부 에너지는 %s.' % (step_name, ws), word[dU] == ws, why_base)
    if qty == 'W':
        return ('%s에서 기체는 외부에 일을 한다.' % step_name, W == UP, why_base)
    if qty == 'Wr':
        return ('%s에서 기체는 외부로부터 일을 받는다.' % step_name, W == DN, why_base)
    if qty == 'Q':
        ws = r.choice(['흡수한다', '방출한다'])
        return ('%s에서 기체는 열을 %s.' % (step_name, ws), (Q == UP) == (ws == '흡수한다') and Q != ZE, why_base)
    return ('%s에서 기체와 외부 사이의 열 출입은 없다.' % step_name, Q == ZE, why_base)

def _sign_cell(s): return s

@T('ph073')
def g073(r, k):
    form = r.choice(['a', 'a', 'a', 'b', 'b', 'b', 'c', 'c', 'c', 'g', 'g', 'h'])
    if form == 'a':
        procs = r.sample(ALL_PROC, 5)
        # 서로 같은 종류 두 개(팽창·압축 반대 방향)는 허용하나 곡선이 겹치는 동종·동방향은 없음
        names = r.sample('BCDEF', 5)
        names = sorted(names)
        sub_ = r.choice(['name', 'prop', 'prop'])
        if sub_ == 'name':
            i = r.randrange(5)
            kind, f = procs[i]
            fig = FIG(_star_fig(procs, names), '76%')
            body = P('그림은 일정량의 이상 기체가 처음 상태 A에서 서로 다른 다섯 가지 과정을 거쳐 B, C, D, E, F 중 한 상태로 변하는 것을 P-V 그래프에 나타낸 것이다. 곡선은 등온선 또는 단열 곡선이고 직선은 등압 또는 등적 과정이다. A → %s 과정은?' % names[i]) + fig
            right = proc_short(kind, f)
            names_all = [proc_short(kd, ff) for kd, ff in ALL_PROC]
            wr = [n_ for n_ in names_all if n_ != right]
            exp = {'isobaric': 'P가 일정한 수평선이다.', 'isochoric': 'V가 일정한 수직선이다.', 'isothermal': 'PV = 일정한 완만한 곡선이다.', 'adiabatic': '같은 부피 변화에서 압력이 더 크게 변하는 가파른 곡선이다.'}[kind]
            return mc(body, right, wr, r=r, lv='중', fam='a', sort='shuf',
                      steps=['A → %s 의 모양 : %s' % (names[i], exp), '부피가 %s하므로 %s이다.' % ('증가' if (f > 1 and kind != 'isochoric') else ('감소' if kind != 'isochoric' else '변하지 않음'), right)],
                      core='수평선=등압, 수직선=등적, 쌍곡선 PV=일정=등온, 이보다 가파른 곡선=단열.', point='곡선의 모양과 방향으로 과정을 구분한다.')
        # prop
        for _ in range(12):
            text, pred = r.choice(_PROP)
            match = [i for i, (kd, ff) in enumerate(procs) if pred(proc_signs(kd, ff))]
            if len(match) == 1: break
        else:
            return None
        i = match[0]
        fig = FIG(_star_fig(procs, names), '76%')
        body = P('그림은 일정량의 이상 기체가 처음 상태 A에서 서로 다른 다섯 가지 과정을 거쳐 B, C, D, E, F 중 한 상태로 변하는 것을 P-V 그래프에 나타낸 것이다. 곡선은 등온선 또는 단열 곡선이고 직선은 등압 또는 등적 과정이다. A → B ~ A → F 중 %s 과정은?' % text) + fig
        opts = ['A → ' + n_ for n_ in names]
        kd, ff = procs[i]
        sg = proc_signs(kd, ff)
        st = ['A → %s 는 %s이다. ΔU %s, W %s, Q %s' % (names[i], proc_short(kd, ff), *sg)]
        st += ['다른 과정은 : ' + ', '.join('A → %s(%s)' % (names[j], proc_short(*procs[j])) for j in range(5) if j != i) + ' — 조건에 맞지 않는다.']
        return mc_list(body, opts, i, steps=st, lv='상', fam='a', core='과정마다 ΔU, W, Q의 부호가 정해져 있다: 등압 팽창(⊕⊕⊕), 등적 가열(⊕0⊕), 등온 팽창(0⊕⊕), 단열 팽창(⊖⊕0).', point='그래프의 과정을 판별한 뒤 ΔU·W·Q의 부호 조건을 확인한다.')
    if form == 'b':   # 부호 표 채우기
        for _ in range(30):
            path = rand_path(r, 2)
            if path: break
        else:
            return None
        fig = FIG(pv_qual(path, 'ABC'), '70%')
        sg = [proc_signs(kd, f) for kd, f, a_, b_ in path]
        rows = [['A → B', sg[0][0], sg[0][1], sg[0][2]], ['B → C', sg[1][0], sg[1][1], sg[1][2]]]
        cells = [(i, j) for i in range(2) for j in range(3)]
        blanks = r.sample(cells, 3)
        letters = ['(가)', '(나)', '(다)']
        tb = [[rw[0]] + list(rw[1:]) for rw in rows]
        ans = []
        for lab, (i, j) in zip(letters, blanks):
            ans.append(tb[i][1 + j]); tb[i][1 + j] = lab
        body = P('그림은 일정량의 이상 기체가 A → B → C로 변하는 과정을 P-V 그래프로 나타낸 것이다. 표는 각 과정에서 내부 에너지 변화 ΔU, 기체가 외부에 한 일 W, 기체가 흡수한 열 Q의 부호를 나타낸 것이다. (가), (나), (다)에 해당하는 부호를 옳게 짝지은 것은? (⊕: 양, ⊖: 음, 0: 영)') + fig + table(['과정', 'ΔU', 'W', 'Q'], tb)
        right = ', '.join('%s %s' % (l, a) for l, a in zip(letters, ans))
        import itertools
        ops = []
        for combo in itertools.product([UP, DN, ZE], repeat=3):
            o = ', '.join('%s %s' % (l, a) for l, a in zip(letters, combo))
            if o != right: ops.append(o)
        # 오답: 정답과 1~2곳만 다른 것을 우선
        near = [o for o in ops if sum(1 for x, y in zip(o.split(', '), right.split(', ')) if x != y) <= 2]
        r.shuffle(near)
        st = ['A → B 는 %s, B → C 는 %s 이다.' % (proc_short(path[0][0], path[0][1]), proc_short(path[1][0], path[1][1])),
              'A → B : ΔU %s, W %s, Q %s' % sg[0], 'B → C : ΔU %s, W %s, Q %s' % sg[1],
              '따라서 ' + right]
        return mc(body, right, near[:8], r=r, lv='상', fam='b', sort='shuf', steps=st, core='ΔU는 온도 변화, W는 부피 변화, Q = ΔU + W 로 부호를 정한다.', point='그래프로 두 과정을 판별하고 부호 표의 빈칸을 채운다.')
    if form == 'g':   # 단일 과정의 부호 묻기
        for _ in range(30):
            path = rand_path(r, 1)
            if path: break
        else:
            return None
        kind, f, a_, b_ = path[0]
        fig = FIG(pv_qual(path, 'AB', w=250, h=200), '62%')
        sg = proc_signs(kind, f)
        body = P('그림은 일정량의 이상 기체가 A에서 B로 변하는 과정을 P-V 그래프로 나타낸 것이다. A → B 과정에서 내부 에너지 변화 ΔU, 기체가 외부에 한 일 W, 기체가 흡수한 열 Q의 부호(⊕: 양, ⊖: 음, 0: 영)를 순서대로 옳게 나타낸 것은?') + fig
        combos = [(UP, UP, UP), (DN, DN, DN), (UP, ZE, UP), (DN, ZE, DN), (ZE, UP, UP), (ZE, DN, DN), (DN, UP, ZE), (UP, DN, ZE), (UP, UP, DN), (DN, UP, UP), (UP, DN, UP), (DN, DN, UP)]
        right = ', '.join(sg)
        near = [', '.join(c) for c in combos if c != sg]
        return mc(body, right, near, r=r, lv='중', fam='g', sort='shuf',
                  steps=['그래프의 모양으로 A → B 는 %s임을 알 수 있다.' % proc_short(kind, f), 'ΔU %s, W %s, Q = ΔU + W 이므로 Q %s 이다.' % (sg[0], sg[1], sg[2])],
                  core='각 과정의 ΔU, W, Q 부호: 등압 팽창(⊕⊕⊕), 등적 냉각(⊖0⊖), 등온 압축(0⊖⊖), 단열 팽창(⊖⊕0) 등.', point='과정을 판별해 ΔU, W, Q의 부호를 모두 답한다.')
    if form == 'h':   # 과정 이름 + 단일 질문 (두 단계)
        for _ in range(30):
            path = rand_path(r, 2)
            if path: break
        else:
            return None
        fig = FIG(pv_qual(path, 'ABC'), '70%')
        i = r.randrange(2)
        kd, ff, a_, b_ = path[i]
        step = ['A → B', 'B → C'][i]
        pn = proc_short(kd, ff)
        body = P('그림은 일정량의 이상 기체가 A → B → C로 변하는 과정을 P-V 그래프로 나타낸 것이다. %s 과정은 어떤 과정인가?' % step) + fig
        names_all = [proc_short(k_, f_) for k_, f_ in ALL_PROC]
        return mc(body, pn, [n_ for n_ in names_all if n_ != pn], r=r, lv='하', fam='h', sort='shuf',
                  steps=['%s 의 곡선 모양과 진행 방향으로 %s임을 알 수 있다.' % (step, pn)],
                  core='수평선=등압, 수직선=등적, 쌍곡선=등온, 더 가파른 곡선=단열.', point='P-V 그래프에서 과정의 종류를 판별한다.')
    # c: bogi 3단계
    for _ in range(40):
        path = rand_path(r, 3)
        if path: break
    else:
        return None
    fig = FIG(pv_qual(path, 'ABCD'), '70%')
    names = ['A → B', 'B → C', 'C → D']
    cand = []
    for _ in range(40):
        picks = r.sample(range(3), 3) if r.random() < 0.5 else [r.randrange(3) for _ in range(3)]
        cand = [_stmt_for(r, names[i], path[i][0], path[i][1]) for i in picks]
        txts = [c[0] for c in cand]
        if len(set(txts)) == 3 and any(c[1] for c in cand): break
    else:
        return None
    return bogi('그림은 일정량의 이상 기체가 A → B → C → D로 변하는 과정을 P-V 그래프로 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', cand, pre=fig, r=r, ask='', lv='상', fam='c',
                core='곡선의 모양으로 과정을 판별하고, 각 과정의 ΔU(온도), W(부피), Q = ΔU + W 의 부호를 따진다.', point='여러 과정으로 이어진 P-V 그래프를 해석한다.')


# ============================================================ ph074 순환 과정 한 바퀴
def _cycle(r, kind=None, ccw=None):
    """(states dict, 순서 이름, 구간 종류들) — 격자 좌표 상태."""
    kind = kind or r.choice(['rect', 'rect', 'tri', 'tri', 'trap'])
    v1 = r.randint(1, 3); v2 = v1 + r.randint(1, 4)
    p1 = r.randint(1, 2); p2 = p1 + r.randint(1, 3)
    if v2 > 7 or p2 > 5: return None
    if kind == 'rect':
        pts = [(v1, p1), (v1, p2), (v2, p2), (v2, p1)]
    elif kind == 'tri':
        tp = r.choice([0, 1, 2, 3])
        base = [(v1, p1), (v1, p2), (v2, p1)]
        if tp == 1: base = [(v1, p2), (v2, p2), (v2, p1)]
        if tp == 2: base = [(v1, p1), (v2, p2), (v2, p1)]
        if tp == 3: base = [(v1, p1), (v1, p2), (v2, p2)]
        pts = base
    else:
        v3 = v1 + 1; v4 = v2 - 1
        if v4 <= v3: return None
        pts = [(v1, p1), (v3, p2), (v4, p2), (v2, p1)]
    # 시계 방향이 되도록 정렬 후 필요시 뒤집기
    def sarea(pp):
        s = 0.0
        for i in range(len(pp)):
            a_, b_ = pp[i], pp[(i + 1) % len(pp)]
            s += area_seg(a_, b_)
        return s
    if sarea(pts) < 0: pts = pts[::-1]
    # 시작점을 임의로 회전
    sh = r.randrange(len(pts)); pts = pts[sh:] + pts[:sh]
    if ccw is None: ccw = r.random() < 0.3
    if ccw: pts = pts[::-1]
    names = 'ABCD'[:len(pts)]
    st = {nm: p_ for nm, p_ in zip(names, pts)}
    return st, names

def _cyc_fig(sc, st, names, cols=None, w=300, h=230):
    segs = []
    for i, nm in enumerate(names):
        segs.append((nm, names[(i + 1) % len(names)], 'L', (cols or [BL, RD, GN, PU])[i % 4] if cols else BL))
    offs = {}
    return pv_fig(sc, 7, 5, st, segs, guides=tuple(names), w=w, h=h)

def cyc_work(st, names):
    """한 순환에서 기체가 한 일(그림 단위 칸)."""
    tot = 0.0
    for i, nm in enumerate(names):
        tot += area_seg(st[nm], st[names[(i + 1) % len(names)]])
    return tot

def cyc_seg_data(st, names, UA_cells=None):
    """구간별 (W, dU, Q)  단위: 그림 칸(기압·L 이면 100 J)  — dU = 1.5 Δ(PV)."""
    out = []
    for i, nm in enumerate(names):
        a_, b_ = st[nm], st[names[(i + 1) % len(names)]]
        dU, W, Q = seg_energy('L', a_, b_)
        out.append((W, dU, Q))
    return out

_B74 = [
    ('한 번 순환하는 동안 기체의 내부 에너지 변화는 0이다.', True, '처음 상태로 되돌아오므로 온도가 같고 ΔU = 0 이다.', 'dU0'),
    ('한 번 순환하는 동안 기체가 흡수한 열의 합은 방출한 열의 합과 항상 같다.', False, 'Q = W 이므로 알짜 일이 0이 아니면 두 열량은 다르다.', 'Qeq'),
    ('P-V 그래프에서 시계 방향으로 순환하면 기체가 외부에 알짜 일을 한다.', True, '팽창할 때의 압력이 압축할 때의 압력보다 크므로 W > 0 이다.', 'cw'),
    ('P-V 그래프에서 시계 반대 방향으로 순환하면 기체가 한 알짜 일은 양(+)이다.', False, '시계 반대 방향은 W < 0 으로 외부가 기체에 일을 한다.', 'ccw'),
    ('한 번 순환하는 동안 기체가 한 알짜 일은 순환 곡선이 둘러싼 넓이와 같다.', True, '팽창 구간 넓이에서 압축 구간 넓이를 뺀 값이다.', 'area'),
    ('한 번 순환하는 동안 기체가 흡수한 알짜 열량은 기체가 한 알짜 일과 같다.', True, 'Q = ΔU + W 이고 ΔU = 0 이므로 Q = W 이다.', 'QW'),
    ('순환 과정이 끝나면 기체의 온도는 처음 상태의 온도와 같다.', True, '처음 상태로 돌아오기 때문이다.', 'T'),
    ('순환 과정의 도중에 기체의 온도는 항상 일정하다.', False, '중간 상태의 PV 값이 다르면 온도도 다르다.', 'Tconst'),
    ('순환 과정에서 기체가 한 번 순환하는 동안 일을 하지 않는다.', False, '시계 방향이면 알짜 일이 양수이고 반시계 방향이면 음수이다. 넓이가 0이 아니면 알짜 일이 0이 아니다.', 'nowork'),
    ('순환 곡선의 넓이가 클수록 한 번 순환하는 동안 기체가 한 알짜 일이 크다.', True, '알짜 일의 크기 = 넓이.', 'bigarea'),
    ('시계 방향으로 순환하는 과정에서 기체는 열을 흡수만 하고 방출하지는 않는다.', False, '일부 구간에서는 열을 방출한다. 흡수한 열의 일부가 일로 바뀌고 나머지는 방출된다.', 'absonly'),
    ('같은 경로를 반대 방향으로 한 번 순환하면 알짜 일의 부호가 바뀐다.', True, '진행 방향이 반대이면 W의 부호가 반대이다.', 'rev'),
]

@T('ph074')
def g074(r, k):
    form = r.choice(['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'c', 'd', 'e', 'e', 'f'])
    sc = rand_sch(r)
    cyc = _cycle(r)
    if not cyc: return None
    st, names = cyc
    nn = len(names)
    Wc = cyc_work(st, names)
    # 교차 검증: 신발끈 공식
    sh = 0.0
    for i, nm in enumerate(names):
        (x1, y1), (x2, y2) = st[nm], st[names[(i + 1) % nn]]
        sh += x1 * y2 - x2 * y1
    assert abs(Wc + sh / 2.0) < 1e-9, (Wc, sh)           # 시계 방향이 +일: W = −(신발끈/2)
    if abs(Wc) < 1e-9: return None
    order = ' → '.join(list(names) + [names[0]])
    fig = FIG(_cyc_fig(sc, st, names), '74%')
    W = Wc * sc.J
    ccw = Wc < 0
    if form == 'a' or form == 'f':
        ask = r.choice(['by', 'ext']) if ccw else 'by'
        if ask == 'by':
            body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 한 번 순환하는 동안 기체가 한 알짜 일은?%s' % (order, unit_note(sc))) + fig
            right = jstr(W)
        else:
            body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 한 번 순환하는 동안 기체가 외부로부터 받은 알짜 일은?%s' % (order, unit_note(sc))) + fig
            right = jstr(-W)
        mx = max(p[0] for p in st.values()) - min(p[0] for p in st.values()); my = max(p[1] for p in st.values()) - min(p[1] for p in st.values())
        wr = [jstr(-W if ask == 'by' else W), jstr(W * 2), jstr(W / 2.0), jstr(mx * my * sc.J), jstr(abs(W) + sc.J), jstr(abs(W) - sc.J) if abs(W) > sc.J else jstr(abs(W) + 2 * sc.J), jstr(mx * max(p[1] for p in st.values()) * sc.J)]
        shape = {4: '직사각형' if len({p[0] for p in st.values()}) == 2 and len({p[1] for p in st.values()}) == 2 else '사다리꼴', 3: '직각삼각형'}[nn]
        st_ = ['순환 과정에서 기체가 한 알짜 일은 그래프가 둘러싼 도형의 넓이이다.', '넓이 = %s칸 (눈금 1칸 = %s J)이므로 |W| = %s J' % (num(abs(Wc)), num(sc.J), num(abs(W))),
               '진행 방향이 %s이므로 기체가 한 알짜 일은 %s이다.' % ('시계 방향' if not ccw else '시계 반대 방향', '양(+)' if not ccw else '음(−)'), '답 : ' + right]
        return mc(body, right, wr, r=r, lv='중' if (nn == 4 and form == 'a') else ('하' if form == 'f' and nn == 3 and not ccw else '중'), fam='a', sort='shuf', steps=st_,
                  core='순환 과정에서 한 일 = 순환 곡선이 둘러싼 넓이. 시계 방향이면 +, 반시계 방향이면 −.', point='진행 방향으로 알짜 일의 부호를 정하고 넓이로 크기를 구한다.')
    if form == 'b':
        ask = r.choice(['Qnet', 'dUQ'])
        if ask == 'Qnet':
            body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 한 번 순환하는 동안 기체가 흡수한 열량 총합에서 방출한 열량 총합을 뺀 알짜 열량은?%s' % (order, unit_note(sc))) + fig
            right = jstr(W)
            st_ = ['한 번 순환하면 처음 상태로 돌아오므로 ΔU = 0 이다.', 'Q = ΔU + W = W 이고 W = 순환 곡선의 넓이 %s칸 × %s J = %s J (%s)' % (num(abs(Wc)), num(sc.J), num(abs(W)), '시계 방향 +' if not ccw else '시계 반대 방향 −'), '알짜 열량 = %s' % right]
            wr = [jstr(-W), '0', jstr(W * 2), jstr(W / 2.0), jstr(abs(W) + sc.J), jstr(abs(W) + 2 * sc.J)]
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=st_, core='한 순환에서 ΔU = 0 이므로 알짜 열 Q = W.', point='ΔU = 0 이면 알짜 열량이 알짜 일과 같다.')
        body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 한 번 순환하는 동안 기체의 내부 에너지 변화 ΔU와 기체가 흡수한 알짜 열량 Q를 옳게 짝지은 것은?%s' % (order, unit_note(sc))) + fig
        right = 'ΔU = 0, Q = %s' % jstr(W)
        wr = ['ΔU = 0, Q = %s' % jstr(-W), 'ΔU = 0, Q = 0', 'ΔU = %s, Q = 0' % jstr(W), 'ΔU = %s, Q = %s' % (jstr(W), jstr(W)), 'ΔU = %s, Q = %s' % (jstr(-W), jstr(W)), 'ΔU = 0, Q = %s' % jstr(W * 2)]
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=['처음 상태로 돌아오므로 ΔU = 0.', 'Q = W = 넓이 %s칸 × %s J = %s' % (num(abs(Wc)), num(sc.J), jstr(W))],
                  core='순환 과정: ΔU = 0, Q = W.', point='순환 후 내부 에너지 변화가 0임을 이용한다.')
    if form == 'c':    # 구간별 열량 — 직사각형 순환(등적/등압)이나 삼각형이면 일반 직선 구간은 제외
        if nn != 4 or len({p[0] for p in st.values()}) != 2 or len({p[1] for p in st.values()}) != 2: return None
        UAcells = None
        # 모든 상태의 U = 1.5 P V (그림 단위), U_A 를 J 로 제시
        nA = names[0]
        pvA = st[nA][0] * st[nA][1]
        U_A = 1.5 * pvA * sc.J
        if abs(U_A - round(U_A)) > 1e-9: return None
        U_A = int(round(U_A))
        segi = r.randrange(4)
        a_, b_ = st[names[segi]], st[names[(segi + 1) % 4]]
        n1, n2 = names[segi], names[(segi + 1) % 4]
        # U ∝ PV 비례 관계로 계산
        UX = lambda p_: Fraction(U_A) * Fraction(int(p_[0] * p_[1]), int(pvA))
        dU = UX(b_) - UX(a_)
        Wseg = area_seg(a_, b_) * sc.J
        Q = dU + Wseg
        # 교차 검증: 단원자 ΔU=1.5Δ(PV)J
        dU2, W2, Q2 = seg_energy('L', a_, b_)
        assert abs(float(dU) - dU2 * sc.J) < 1e-6 and abs(float(Q) - Q2 * sc.J) < 1e-6
        if Q == 0: return None
        body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 상태 %s에서 기체의 내부 에너지는 %d J이다. %s → %s 과정에서 기체가 %s 열량은? (단, 이상 기체의 내부 에너지는 절대 온도에 비례한다.)%s' % (order, nA, U_A, n1, n2, '흡수한' if Q > 0 else '방출한', unit_note(sc))) + fig
        mag = abs(Q)
        dUf, Wf = float(dU), Wseg
        wr = [abs(dUf), abs(Wf), abs(dUf) + abs(Wf) + 0.5 * sc.J, abs(dUf - Wf) if abs(dUf - Wf) != mag else mag + sc.J, mag * 2, mag / 2.0 if mag % 2 == 0 else mag + 50, U_A]
        right = '%s J' % num(mag)
        why = '%s → %s : ' % (n1, n2)
        if a_[0] == b_[0]: why += '부피가 일정(등적)하므로 W = 0, Q = ΔU'
        else: why += '압력이 %s로 일정(등압)하므로 W = PΔV = %s J' % (pre_str(sc, a_[1]), num(Wseg))
        st_ = ['U ∝ T ∝ PV 이므로 U%s = U%s × (P%sV%s)/(P%sV%s) 이다.' % (sub(n2), sub(nA), sub(n2), sub(n2), sub(nA), sub(nA)),
               'U%s = %s J, U%s = %s J → ΔU = %s J' % (sub(n1), num(float(UX(a_))), sub(n2), num(float(UX(b_))), num(dUf)), why, 'Q = ΔU + W = %s + %s = %s J (%s)' % (num(dUf), num(Wf), num(float(Q)), '흡수' if Q > 0 else '방출')]
        return mc(body, right, ['%s J' % num(w) for w in wr], r=r, lv='상', fam='c', sort='shuf', steps=st_, core='U ∝ PV. 구간별로 ΔU = U₂ − U₁, W = (넓이), Q = ΔU + W.', point='PV 비로 내부 에너지 변화를 구하고 제1법칙으로 열량을 구한다.')
    if form == 'd':   # 꼭짓점 온도 비교
        vals = {nm: st[nm][0] * st[nm][1] for nm in names}
        nm1, nm2 = r.sample(list(names), 2)
        a_, b_ = vals[nm1], vals[nm2]
        ask = r.choice(['ratio', 'order'])
        if ask == 'ratio':
            body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 상태 %s의 절대 온도를 T%s, 상태 %s의 절대 온도를 T%s라 할 때 T%s : T%s는?' % (order, nm1, sub(nm1), nm2, sub(nm2), sub(nm1), sub(nm2))) + fig
            right = ratio_str(a_, b_)
            wr = [ratio_str(b_, a_), ratio_str(st[nm1][0], st[nm2][0]), ratio_str(st[nm1][1], st[nm2][1]), ratio_str(st[nm1][0] + st[nm1][1], st[nm2][0] + st[nm2][1]), '1 : 1']
            return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf',
                      steps=['PV = nRT 이므로 T ∝ PV 이다.', '%s : P V = %s × %s = %d, %s : P V = %s × %s = %d' % (nm1, num(st[nm1][1]), num(st[nm1][0]), a_, nm2, num(st[nm2][1]), num(st[nm2][0]), b_), 'T%s : T%s = %s' % (sub(nm1), sub(nm2), right)],
                      core='이상 기체에서 T ∝ PV. P-V 그래프의 좌표 곱으로 온도를 비교한다.', point='좌표의 곱 PV로 온도비를 구한다.')
        order_ = sorted(names, key=lambda n_: vals[n_])
        if len(set(vals.values())) < nn: return None
        hi = order_[-1]; lo = order_[0]
        body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 순환하는 동안 기체의 온도가 가장 높은 상태와 가장 낮은 상태를 옳게 짝지은 것은?' % order) + fig
        right = '가장 높은 상태 : %s, 가장 낮은 상태 : %s' % (hi, lo)
        wr = ['가장 높은 상태 : %s, 가장 낮은 상태 : %s' % (a, b) for a in names for b in names if a != b and (a, b) != (hi, lo)]
        st_ = ['T ∝ PV 이므로 ' + ', '.join('%s : %d' % (n_, vals[n_]) for n_ in names)]
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf', steps=st_ + ['최고 %s, 최저 %s' % (hi, lo)], core='T ∝ PV.', point='각 꼭짓점의 PV 값을 비교한다.')
    # e: bogi
    if True:
        cand = []
        sg_seg = []
        for i, nm in enumerate(names):
            a_, b_ = st[nm], st[names[(i + 1) % nn]]
            dU, W_, Q_ = seg_energy('L', a_, b_)
            sg_seg.append((nm + ' → ' + names[(i + 1) % nn], sgn(dU), sgn(W_), sgn(Q_), a_, b_))
        comp = []
        for lab, sd, sw, sq_, a_, b_ in sg_seg:
            if a_[0] != b_[0] or a_[1] != b_[1]:
                why = '%s에서 ΔU %s, W %s, Q %s 이다.' % (lab, sd, sw, sq_)
                comp.append(('%s 과정에서 기체의 온도는 %s.' % (lab, r.choice(['올라간다', '내려간다'])), None, why, 'T', sd, lab))
        ss = []
        for lab, sd, sw, sq_, a_, b_ in sg_seg:
            why = '%s에서 ΔU %s, W %s, Q %s 이다.' % (lab, sd, sw, sq_)
            wd = r.choice(['T', 'W', 'Q'])
            if wd == 'T':
                ws = r.choice(['올라간다', '내려간다', '변하지 않는다']); tru = {UP: '올라간다', DN: '내려간다', ZE: '변하지 않는다'}[sd] == ws
                ss.append(('%s 과정에서 기체의 온도는 %s.' % (lab, ws), tru, why))
            elif wd == 'W':
                if sw == ZE: ss.append(('%s 과정에서 기체가 한 일은 0이다.' % lab, True, why))
                else: ss.append(('%s 과정에서 기체는 외부에 일을 한다.' % lab, sw == UP, why))
            else:
                ws = r.choice(['흡수한다', '방출한다'])
                ss.append(('%s 과정에서 기체는 열을 %s.' % (lab, ws), (sq_ == UP) == (ws == '흡수한다') and sq_ != ZE, why))
        gen = [(t, tr, w, 'g%d' % i) for i, (t, tr, w) in enumerate(ss)]
        static = [(s[0], s[1], s[2], s[3]) for s in _B74]
        # 정적 문장 1~2개 + 계산 문장
        nstat = r.choice([1, 2, 2])
        pool = r.sample(static, nstat) + r.sample(gen, 3 - nstat)
        # 정적 문장 중 시계/반시계 방향 의존 문장은 현재 그림에 맞게 판정
        fixed = []
        for t, tr, w, g in pool:
            if g == 'cw': tr = (not ccw); w = ('순환이 %s이므로 기체가 한 알짜 일은 %s이다.' % ('시계 방향' if not ccw else '시계 반대 방향', '양(+)' if not ccw else '음(−)'))
            if g == 'ccw': tr = ccw; w = ('순환이 %s이므로 알짜 일은 %s이다.' % ('시계 방향' if not ccw else '시계 반대 방향', '양(+)' if not ccw else '음(−)'))
            fixed.append((t, tr, w, g))
        if len({f_[3] for f_ in fixed}) < 3 or len({f_[0] for f_ in fixed}) < 3: return None
        fixed = [(a, b, c) for a, b, c, d in fixed]
        return bogi('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % order, fixed, pre=fig, r=r, ask='', lv='중', fam='e',
                    core='순환 과정: ΔU = 0, Q = W = 넓이(시계 방향 +).', point='순환 그래프에서 구간별 ΔU·W·Q와 전체 관계를 판단한다.')


# ============================================================ ph075 상태 변화와 PV/T 비교
def _states3(r):
    """세 상태 (V,P) — 서로 다른 PV 값 3개."""
    for _ in range(100):
        ps = [r.randint(1, 5) for _ in range(3)]; vs = [r.randint(1, 7) for _ in range(3)]
        pv = [p_ * v_ for p_, v_ in zip(ps, vs)]
        if len(set(zip(vs, ps))) == 3:
            return [(v_, p_) for v_, p_ in zip(vs, ps)]
    return None

def _stmt75(r, st, names, T0):
    """계산해서 만드는 문장 목록 [(문장, 참거짓, 풀이, 그룹)]."""
    pv = {n_: st[n_][0] * st[n_][1] for n_ in names}
    out = []
    for a_ in names:
        for b_ in names:
            if a_ >= b_: continue
            wa, wb = sub(a_), sub(b_)
            if pv[a_] == pv[b_]:
                out.append(('T%s = T%s 이다.' % (wa, wb), True, 'PV가 같으므로 온도가 같다.', 'eq'))
                out.append(('U%s < U%s 이다.' % (wa, wb), False, 'PV가 같으므로 U%s = U%s 이다.' % (wa, wb), 'eq2'))
                out.append(('%s에서 %s로 등온 과정을 거쳐 변할 수 있다.' % (a_, b_), True, 'PV가 같아 두 상태는 같은 등온선 위에 있다.', 'iso'))
            else:
                hi, lo = (a_, b_) if pv[a_] > pv[b_] else (b_, a_)
                out.append(('T%s > T%s 이다.' % (sub(hi), sub(lo)), True, 'T ∝ PV : %s의 PV = %d, %s의 PV = %d' % (hi, pv[hi], lo, pv[lo]), 'gt'))
                out.append(('T%s > T%s 이다.' % (sub(lo), sub(hi)), False, 'T ∝ PV 이므로 T%s > T%s 이다.' % (sub(hi), sub(lo)), 'gt2'))
                out.append(('U%s > U%s 이다.' % (sub(hi), sub(lo)), True, 'U ∝ T ∝ PV, %d > %d' % (pv[hi], pv[lo]), 'ugt'))
                out.append(('%s에서 %s로 등온 과정을 거쳐 변할 수 있다.' % (a_, b_), False, 'PV가 %d, %d로 달라 온도가 다르므로 등온 과정이 아니다.' % (pv[a_], pv[b_]), 'iso2'))
                g = math.gcd(pv[hi], pv[lo])
                rt = '%d : %d' % (pv[hi] // g, pv[lo] // g)
                out.append(('T%s : T%s = %s 이다.' % (sub(hi), sub(lo), rt), True, 'T ∝ PV 이므로 %d : %d = %s' % (pv[hi], pv[lo], rt), 'ratio'))
                bad = '%d : %d' % (pv[hi] // g + 1, pv[lo] // g)
                out.append(('T%s : T%s = %s 이다.' % (sub(hi), sub(lo), bad), False, '온도비는 PV의 비 %s 이다.' % rt, 'ratio2'))
    mx = max(names, key=lambda n_: pv[n_])
    if sorted(pv.values())[-1] != sorted(pv.values())[-2]:
        out.append(('세 상태 중 기체의 내부 에너지가 가장 큰 상태는 %s이다.' % mx, True, 'PV가 가장 큰 %s이다 (U ∝ PV).' % mx, 'max'))
        other = r.choice([n_ for n_ in names if n_ != mx])
        out.append(('세 상태 중 기체의 내부 에너지가 가장 큰 상태는 %s이다.' % other, False, 'PV가 가장 큰 %s에서 U가 가장 크다.' % mx, 'max2'))
    out.append(('세 상태에서 PV/T 의 값은 모두 같다.', True, '분자 수가 일정하므로 PV/T = nR 로 일정하다.', 'pvt'))
    out.append(('압력이 같은 두 상태에서는 부피가 큰 상태의 절대 온도가 더 높다.', True, 'PV ∝ T 에서 P가 같으면 T ∝ V 이다.', 'sameP'))
    return out

def pv_all_same_p(st, names):
    return len({st[n_][1] for n_ in names}) == 1

@T('ph075')
def g075(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'c', 'd', 'e', 'f'])
    sts = _states3(r)
    if not sts: return None
    names = 'ABC'
    st = dict(zip(names, sts))
    sc = rand_sch(r)
    pv = {n_: st[n_][0] * st[n_][1] for n_ in names}
    show = r.choice(['table', 'graph'])
    def info():
        if show == 'table':
            rows = [[n_, pre_str(sc, st[n_][1]), vol_str(sc, st[n_][0])] for n_ in names]
            return table(['상태', '압력', '부피'], rows), '표'
        fig = FIG(pv_fig(sc, 7, 5, st, [], guides=tuple(names), arrows=False, lab_off={n_: (12, -7) for n_ in names}), '72%')
        return fig, '그래프'
    inf, kind_ = info()
    lead = '표는 일정량의 이상 기체의 세 상태 A, B, C에서의 압력과 부피를 나타낸 것이다.' if show == 'table' else '그림은 일정량의 이상 기체의 세 상태 A, B, C의 압력과 부피를 P-V 그래프에 나타낸 것이다.'
    if form == 'a':
        pvs = [pv[n_] for n_ in names]
        g = pvs[0]
        for x in pvs[1:]: g = math.gcd(g, x)
        right = ' : '.join(str(x // g) for x in pvs)
        body = P(lead + ' A, B, C의 절대 온도를 각각 T%s, T%s, T%s라 할 때 T%s : T%s : T%s는?' % (sub('A'), sub('B'), sub('C'), sub('A'), sub('B'), sub('C'))) + inf
        wr = [' : '.join(str(x // g) for x in reversed(pvs)), ' : '.join(str(st[n_][1]) for n_ in names), ' : '.join(str(st[n_][0]) for n_ in names), ' : '.join(str(st[n_][0] + st[n_][1]) for n_ in names), ' : '.join(str((pv[n_] // g) + 1) for n_ in names), ' : '.join(str(pv[names[(i + 1) % 3]] // g) for i in range(3))]
        return mc(body, right, wr, r=r, lv='중', fam='a', sort='shuf',
                  steps=['일정량의 이상 기체에서 PV = nRT 이므로 T ∝ PV 이다.', 'PV 값(눈금 단위) : A = %d, B = %d, C = %d' % (pvs[0], pvs[1], pvs[2]), 'T%s : T%s : T%s = %s' % (sub('A'), sub('B'), sub('C'), right)],
                  core='일정량의 이상 기체에서 PV/T = 일정, 즉 T ∝ PV.', point='압력과 부피의 곱으로 절대 온도를 비교한다.')
    if form == 'b':
        na, nb = r.sample(names, 2)
        Ta = r.choice([100, 150, 200, 250, 300, 400, 500, 600])
        Tb = Fraction(Ta * pv[nb], pv[na])
        if Tb.denominator != 1: return None
        Tb = int(Tb)
        body = P(lead + ' 상태 %s의 절대 온도가 %d K일 때 상태 %s의 절대 온도는?' % (na, Ta, nb)) + inf
        wr = [Ta * pv[na] // pv[nb] if (Ta * pv[na]) % pv[nb] == 0 else Ta + 50, Ta, Tb + 100, Tb * 2, Tb // 2 + 20, Ta * st[nb][0] // st[na][0] if (Ta * st[nb][0]) % st[na][0] == 0 else Tb + 50, Ta * st[nb][1] // st[na][1] if (Ta * st[nb][1]) % st[na][1] == 0 else Tb + 30]
        return mc(body, '%d K' % Tb, ['%d K' % w for w in wr], r=r, lv='중', fam='b',
                  steps=['PV/T = 일정 이므로 T%s = T%s × (PV)%s/(PV)%s' % (sub(nb), sub(na), sub(nb), sub(na)), '(PV)%s = %d, (PV)%s = %d (눈금 단위) 이므로 T%s = %d × %d/%d = %d K' % (sub(na), pv[na], sub(nb), pv[nb], sub(nb), Ta, pv[nb], pv[na], Tb)],
                  core='PV/T = 일정 (분자 수 일정).', point='보일-샤를 법칙으로 나중 온도를 구한다.')
    if form == 'd':
        if len(set(pv.values())) < 3: return None
        order_ = sorted(names, key=lambda n_: -pv[n_])
        right = ' > '.join('U%s' % sub(n_) for n_ in order_)
        body = P(lead + ' 세 상태에서 기체의 내부 에너지 U%s, U%s, U%s의 대소를 옳게 나타낸 것은?' % (sub('A'), sub('B'), sub('C'))) + inf
        import itertools
        wr = [' > '.join('U%s' % sub(n_) for n_ in p_) for p_ in itertools.permutations(names) if list(p_) != order_]
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf',
                  steps=['U ∝ T ∝ PV 이다.', 'PV : ' + ', '.join('%s = %d' % (n_, pv[n_]) for n_ in names), '따라서 ' + right],
                  core='이상 기체의 내부 에너지는 PV에 비례한다.', point='PV 값의 크기 순서로 내부 에너지를 비교한다.')
    if form == 'e':   # 같은 온도 상태 찾기 / 가장 높은 온도
        pairs = [(a_, b_) for a_ in names for b_ in names if a_ < b_ and pv[a_] == pv[b_]]
        ask = r.choice(['same', 'max'])
        if ask == 'same' and not pairs:
            return None
        if ask == 'same':
            a_, b_ = pairs[0]
            right = '%s, %s' % (a_, b_)
            body = P(lead + ' 세 상태 중 기체의 온도가 같은 두 상태는?') + inf
            wr = ['%s, %s' % (x, y) for x in names for y in names if x < y and (x, y) != (a_, b_)]
            wr += ['모두 같다', '없다']
            return mc(body, right, wr, r=r, lv='하', fam='e', sort='shuf', steps=['T ∝ PV : ' + ', '.join('%s = %d' % (n_, pv[n_]) for n_ in names), '%s와 %s의 PV가 같으므로 온도가 같다.' % (a_, b_)],
                      core='T ∝ PV.', point='좌표의 곱이 같은 두 상태는 온도가 같다.')
        hi = max(names, key=lambda n_: pv[n_])
        if sorted(pv.values())[-1] == sorted(pv.values())[-2]: return None
        body = P(lead + ' 세 상태 중 기체의 절대 온도가 가장 높은 상태는?') + inf
        return mc_list(body, ['A', 'B', 'C', 'A와 B', 'B와 C'], names.index(hi), steps=['T ∝ PV : ' + ', '.join('%s = %d' % (n_, pv[n_]) for n_ in names), '가장 큰 값은 %s이다.' % hi],
                       lv='하', fam='e', core='T ∝ PV.', point='PV가 가장 큰 상태가 온도가 가장 높다.')
    if form == 'f':   # 같은 압력/부피에서 두 상태 비교
        a_, b_ = r.sample(names, 2)
        ask = r.choice(['U', 'T'])
        ratio = ratio_str(pv[a_], pv[b_])
        body = P(lead + ' 상태 %s의 내부 에너지가 U%s, 상태 %s의 내부 에너지가 U%s일 때 U%s : U%s는?' % (a_, sub(a_), b_, sub(b_), sub(a_), sub(b_))) + inf
        wr = [ratio_str(pv[b_], pv[a_]), ratio_str(st[a_][1], st[b_][1]), ratio_str(st[a_][0], st[b_][0]), ratio_str(st[a_][0] + st[a_][1], st[b_][0] + st[b_][1]), ratio_str(pv[a_] + 1, pv[b_])]
        return mc(body, ratio, wr, r=r, lv='중', fam='f', sort='shuf', steps=['U ∝ T ∝ PV', 'U%s : U%s = %d : %d = %s' % (sub(a_), sub(b_), pv[a_], pv[b_], ratio)],
                  core='U ∝ T ∝ PV.', point='좌표의 곱의 비로 내부 에너지의 비를 구한다.')
    # c: bogi
    pool = _stmt75(r, st, names, 0)
    for _ in range(60):
        sel = r.sample(pool, 3)
        if len({s[3] for s in sel}) == 3 and len({s[0] for s in sel}) == 3 and any(s[1] for s in sel): break
    else:
        return None
    stm = [(s[0], s[1], s[2]) for s in sel]
    pre = inf
    return bogi(lead + ' 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, pre=pre, r=r, ask='', lv='중', fam='c',
                core='일정량의 이상 기체: PV/T = 일정, U ∝ T ∝ PV.', point='PV 값으로 온도·내부 에너지를 비교하는 <보기>.')


# ============================================================ ph076 일상 속 열역학 과정
_PN = {   # 과정: (ΔU, W, Q) 부호, 온도 변화, 일 설명
    '단열 팽창': ((DN, UP, ZE), '내려간다', '외부에 일을 한다'),
    '단열 압축': ((UP, DN, ZE), '올라간다', '외부로부터 일을 받는다'),
    '등적 가열': ((UP, ZE, UP), '올라간다', '일을 하지 않는다'),
    '등적 냉각': ((DN, ZE, DN), '내려간다', '일을 하지 않는다'),
    '등압 팽창': ((UP, UP, UP), '올라간다', '외부에 일을 한다'),
    '등압 압축': ((DN, DN, DN), '내려간다', '외부로부터 일을 받는다'),
    '등온 팽창': ((ZE, UP, UP), '변하지 않는다', '외부에 일을 한다'),
    '등온 압축': ((ZE, DN, DN), '변하지 않는다', '외부로부터 일을 받는다'),
}

_SCN = [
    ('상승하는 공기 덩어리가 주위의 기압이 낮아져 열을 교환할 시간 없이 팽창하면서 온도가 내려가 수증기가 응결하여 구름이 생긴다.', '단열 팽창', '구름이 생길 때 공기 덩어리의 변화'),
    ('흔들어 둔 탄산음료 병의 뚜껑을 갑자기 열었더니 병 입구에 하얀 김이 서렸다. 병 속 기체가 빠르게 팽창한 것이다.', '단열 팽창', '병뚜껑을 갑자기 열 때 병 속 기체의 변화'),
    ('디젤 엔진의 실린더 속 공기를 피스톤이 매우 빠르게 압축하여 온도가 높아지면 연료가 저절로 점화된다.', '단열 압축', '디젤 엔진에서 공기가 빠르게 압축될 때의 변화'),
    ('자전거 타이어에 공기를 넣으려고 펌프를 빠르게 여러 번 눌렀더니 펌프 몸통이 따뜻해졌다. 펌프 속 공기가 열을 교환할 시간이 없이 압축된 것이다.', '단열 압축', '자전거 펌프 속 공기의 변화'),
    ('뚜껑을 꼭 닫은 압력솥을 가열하면 솥 안의 기체의 압력과 온도가 올라간다. (솥의 부피 변화는 무시한다.)', '등적 가열', '압력솥을 가열할 때 솥 속 기체의 변화'),
    ('햇볕을 받은 풍선이 대기압과 거의 같은 압력을 유지하면서 천천히 부풀어 올랐다.', '등압 팽창', '햇볕을 받아 부푸는 풍선 속 기체의 변화'),
    ('유리 실린더 속 솜뭉치에 불이 붙는 장치에서 피스톤을 아주 빠르게 눌렀더니 솜이 타올랐다. 실린더 속 공기가 열을 교환할 시간 없이 압축된 것이다.', '단열 압축', '피스톤을 빠르게 눌러 솜이 타오를 때 실린더 속 공기의 변화'),
    ('피스톤을 급히 당겨 실린더 속 공기를 팽창시켰더니 안에 넣어 둔 온도계의 눈금이 내려갔다. (열 교환은 무시한다.)', '단열 팽창', '피스톤을 급히 당길 때 실린더 속 공기의 변화'),
    ('열이 잘 전달되는 주사기의 입구를 막고 피스톤을 매우 천천히 눌렀더니 주사기 속 공기가 주위와 같은 온도를 유지하면서 압축되었다.', '등온 압축', '주사기 속 공기를 천천히 누를 때의 변화'),
    ('수온이 일정한 호수 바닥에서 올라오는 공기 방울이 주위 물과 온도가 같도록 천천히 커졌다.', '등온 팽창', '물속에서 커지는 공기 방울의 변화'),
    ('가솔린 엔진에서 점화 플러그의 불꽃으로 연료가 연소하는 짧은 순간, 피스톤이 거의 움직이지 않아 부피는 일정하고 압력과 온도가 급격히 높아졌다.', '등적 가열', '연소 순간 실린더 속 기체의 변화'),
    ('뚜껑을 닫은 단단한 캔을 냉동실에 넣었더니 캔 속 기체의 압력이 낮아졌다. (캔의 부피 변화는 무시한다.)', '등적 냉각', '냉동실에 넣은 캔 속 기체의 변화'),
    ('산을 넘은 공기가 비탈을 내려오면서 주위의 기압이 높아져 열 교환 없이 압축되어 따뜻하고 건조한 바람이 불었다.', '단열 압축', '산비탈을 내려오는 공기의 변화'),
    ('증기 기관에서 고온 고압의 기체가 열을 거의 잃지 않고 피스톤을 밀어내며 팽창한다.', '단열 팽창', '피스톤을 밀며 팽창하는 기체의 변화'),
    ('실린더 위의 피스톤에 추를 올려 두고 기체를 가열하였더니 압력이 일정하게 유지되면서 피스톤이 올라갔다.', '등압 팽창', '추가 올려진 피스톤 아래 기체의 변화'),
    ('실린더 위의 피스톤에 추를 올려 둔 채 기체를 냉각하였더니 압력이 일정하게 유지되면서 피스톤이 내려갔다.', '등압 압축', '추가 올려진 피스톤 아래 기체를 냉각할 때의 변화'),
    ('온도가 일정한 항온조에 잠긴 실린더 속 기체가 열을 흡수하면서 천천히 팽창하여 피스톤을 밀어 올렸다.', '등온 팽창', '항온조 속 실린더 기체의 변화'),
    ('한여름 햇볕에 놓인 자동차 안의 밀폐된 빈 페트병의 부피가 거의 변하지 않은 채 병 속 공기의 압력이 올라갔다.', '등적 가열', '밀폐된 페트병 속 공기의 변화'),
    ('물과 공기를 조금 넣은 페트병을 세게 눌러 압축했다가 갑자기 놓았더니 병 속에 안개가 생겼다. 공기가 빠르게 팽창하여 온도가 내려간 것이다.', '단열 팽창', '눌렀다 놓은 페트병 속 공기의 변화'),
    ('자동차 타이어를 오래 달리면 타이어 안 공기의 온도와 압력이 올라간다. (타이어의 부피 변화는 무시한다.)', '등적 가열', '달리는 자동차 타이어 속 공기의 변화'),
    ('열기관의 압축 행정에서 열 교환이 거의 없이 피스톤이 연료와 공기 혼합 기체를 빠르게 압축한다.', '단열 압축', '압축 행정에서 혼합 기체의 변화'),
    ('열이 잘 통하는 용기에 든 공기를 피스톤으로 매우 천천히 압축하면서 용기 밖으로 열이 빠져나가 온도가 일정하게 유지되었다.', '등온 압축', '천천히 압축되는 용기 속 공기의 변화'),
]
_PROCS = list(_PN.keys())

_B76 = []
def _b76_stmts(sc_idx, r):
    """시나리오에서 문장 하나 (참/거짓 무작위). 반환 (문장, 참거짓, 풀이문)"""
    text, proc, topic = _SCN[sc_idx]
    (dU, W, Q), tchg, wdesc = _PN[proc]
    tag = '(%s)' % '가나다라마'[sc_idx % 5]
    kind = r.choice(['proc', 'proc', 'temp', 'work', 'heat', 'U'])
    why_base = '%s는 %s 과정이다. ΔU %s, W %s, Q %s.' % (topic, proc, dU, W, Q)
    return kind, proc, why_base, (dU, W, Q), tchg, wdesc

def _scn_stmt(r, idx):
    text, proc, topic = _SCN[idx]
    (dU, W, Q), tchg, wdesc = _PN[proc]
    kind = r.choice(['proc', 'proc', 'temp', 'work', 'heat', 'U'])
    claim_true = r.random() < 0.5
    why = '%s : %s. (ΔU %s, W %s, Q %s)' % (topic, proc, dU, W, Q)
    if kind == 'proc':
        if claim_true: cp = proc
        else: cp = r.choice([p_ for p_ in _PROCS if p_ != proc])
        return ('%s는 %s 과정으로 볼 수 있다.' % (topic, cp), cp == proc, why)
    if kind == 'temp':
        ws = r.choice(['올라간다', '내려간다', '변하지 않는다'])
        return ('%s에서 기체의 온도는 %s.' % (topic, ws), ws == tchg, why)
    if kind == 'work':
        ws = r.choice(['외부에 일을 한다', '외부로부터 일을 받는다', '일을 하지 않는다'])
        return ('%s에서 기체는 %s.' % (topic, ws), ws == wdesc, why)
    if kind == 'heat':
        ws = r.choice(['열을 흡수한다', '열을 방출한다', '열의 출입이 없다'])
        truth = {UP: '열을 흡수한다', DN: '열을 방출한다', ZE: '열의 출입이 없다'}[Q] == ws
        return ('%s에서 기체는 %s.' % (topic, ws), truth, why)
    ws = r.choice(['증가한다', '감소한다', '변하지 않는다'])
    truth = {UP: '증가한다', DN: '감소한다', ZE: '변하지 않는다'}[dU] == ws
    return ('%s에서 기체의 내부 에너지는 %s.' % (topic, ws), truth, why)

@T('ph076')
def g076(r, k):
    form = r.choice(['a', 'a', 'a', 'b', 'b', 'c', 'c', 'd', 'e', 'f'])
    idx = r.randrange(len(_SCN))
    text, proc, topic = _SCN[idx]
    (dU, W, Q), tchg, wdesc = _PN[proc]
    if form == 'a':
        body = P('다음은 일상생활에서 볼 수 있는 현상이다.') + BOX_(text) + P('이 현상에서 기체가 거치는 과정으로 가장 적절한 것은?')
        wr = [p_ for p_ in _PROCS if p_ != proc]
        return mc(body, proc, wr, r=r, lv='하', fam='a', sort='shuf',
                  steps=['현상의 핵심 조건을 찾는다 : ' + _hint(proc), '따라서 이 과정은 %s이다.' % proc],
                  core='등압: 압력 일정, 등적: 부피 일정, 등온: 온도 일정, 단열: 열 출입 없음(빠른 변화).', point='현상의 조건에서 열역학 과정을 판별한다.')
    if form == 'b':
        ask = r.choice(['T', 'W', 'Q'])
        if ask == 'T':
            body = P('다음은 일상생활에서 볼 수 있는 현상이다.') + BOX_(text) + P('이 현상에서 기체의 온도 변화는?')
            right = tchg.rstrip('.') ; opts = ['올라간다', '내려간다', '변하지 않는다']
            wr = [o for o in opts if o != right] + ['처음에는 올라갔다가 내려간다', '알 수 없다']
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=['이 현상은 %s 과정이다.' % proc, '%s에서 ΔU %s 이므로 온도는 %s.' % (proc, dU, tchg)],
                      core='단열 팽창은 온도 하강, 단열 압축은 온도 상승, 등온은 온도 일정.', point='과정 판별 후 온도 변화를 추론한다.')
        if ask == 'W':
            body = P('다음은 일상생활에서 볼 수 있는 현상이다.') + BOX_(text) + P('이 현상에서 기체가 외부와 주고받는 일에 대한 설명으로 옳은 것은?')
            opts = ['기체가 외부에 일을 한다', '기체가 외부로부터 일을 받는다', '기체가 일을 하지 않는다']
            right = {UP: opts[0], DN: opts[1], ZE: opts[2]}[W]
            wr = [o for o in opts if o != right] + ['기체가 일을 하면서 동시에 일을 받는다', '일의 출입은 알 수 없다']
            return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=['이 현상은 %s 과정이다.' % proc, '%s에서 W %s 이므로 %s.' % (proc, W, right)],
                      core='팽창하면 기체가 일을 하고(W > 0), 압축되면 일을 받는다(W < 0), 부피가 일정하면 W = 0.', point='부피 변화로 일의 방향을 판단한다.')
        body = P('다음은 일상생활에서 볼 수 있는 현상이다.') + BOX_(text) + P('이 현상에서 기체와 외부 사이의 열의 출입에 대한 설명으로 옳은 것은?')
        opts = ['기체가 열을 흡수한다', '기체가 열을 방출한다', '열의 출입이 거의 없다']
        right = {UP: opts[0], DN: opts[1], ZE: opts[2]}[Q]
        wr = [o for o in opts if o != right] + ['처음에는 흡수하다가 나중에는 방출한다', '알 수 없다']
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=['이 현상은 %s 과정이다.' % proc, '%s에서 Q %s 이므로 %s.' % (proc, Q, right)],
                  core='단열 과정은 Q = 0, 등적 가열은 Q > 0, 등온 압축은 Q < 0.', point='과정 판별 후 열의 출입을 판단한다.')
    if form == 'e':   # ΔU W Q 부호
        body = P('다음은 일상생활에서 볼 수 있는 현상이다.') + BOX_(text) + P('이 현상에서 기체의 내부 에너지 변화 ΔU, 기체가 외부에 한 일 W, 기체가 흡수한 열 Q의 부호(⊕: 양, ⊖: 음, 0: 영)를 순서대로 옳게 나타낸 것은?')
        combos = [v[0] for v in _PN.values()]
        right = ', '.join((dU, W, Q))
        wr = [', '.join(c) for c in combos if c != (dU, W, Q)] + [', '.join((UP, UP, DN)), ', '.join((DN, UP, UP))]
        return mc(body, right, wr, r=r, lv='상', fam='e', sort='shuf', steps=['이 현상은 %s 과정이다.' % proc, '%s : ΔU %s, W %s, Q %s' % (proc, dU, W, Q)],
                  core='과정별 부호: 단열 팽창(⊖⊕0), 단열 압축(⊕⊖0), 등적 가열(⊕0⊕), 등압 팽창(⊕⊕⊕), 등온 팽창(0⊕⊕).', point='일상 현상을 과정으로 바꾸어 ΔU·W·Q의 부호를 구한다.')
    if form == 'd':   # 세 현상과 세 과정 짝짓기
        for _ in range(30):
            ids = r.sample(range(len(_SCN)), 3)
            ps = [_SCN[i][1] for i in ids]
            if len(set(ps)) == 3: break
        else:
            return None
        labs = ['(가)', '(나)', '(다)']
        body = P('다음은 일상생활에서 볼 수 있는 세 가지 현상이다.') + BOX3([(l, _SCN[i][0]) for l, i in zip(labs, ids)]) + P('(가), (나), (다)에서 기체가 거치는 과정을 옳게 짝지은 것은?')
        right = '%s, %s, %s' % tuple(ps)
        pool = r.sample([p_ for p_ in _PROCS if p_ not in ps], 3) if len([p_ for p_ in _PROCS if p_ not in ps]) >= 3 else []
        import itertools
        wr = []
        perms = [list(p_) for p_ in itertools.permutations(ps) if list(p_) != ps]
        for p_ in perms: wr.append(', '.join(p_))
        for q_ in pool:
            wr.append(', '.join([q_] + ps[1:])); wr.append(', '.join([ps[0], q_, ps[2]]))
        return mc(body, right, wr, r=r, lv='상', fam='d', sort='shuf',
                  steps=['(가) %s' % _hint(ps[0]) + ' → ' + ps[0], '(나) %s' % _hint(ps[1]) + ' → ' + ps[1], '(다) %s' % _hint(ps[2]) + ' → ' + ps[2]],
                  core='현상의 조건(압력·부피·온도 일정, 열 교환 없음)으로 과정을 판별한다.', point='여러 현상을 열역학 과정으로 분류한다.')
    if form == 'f':   # 과정에 해당하지 않는 현상 찾기 (5개 중)
        target = r.choice(_PROCS[:6])
        cand_ids = [i for i, s in enumerate(_SCN) if s[1] == target]
        if not cand_ids: return None
        others = [i for i, s in enumerate(_SCN) if s[1] != target]
        wr_ids = r.sample(others, 4)
        ans_i = r.choice(cand_ids)
        ids = wr_ids + [ans_i]
        r.shuffle(ids)
        opts = [_SCN[i][0] for i in ids]
        ai = ids.index(ans_i)
        body = P('다음 중 기체가 %s 과정을 거치는 것으로 볼 수 있는 현상은?' % target)
        return mc_list(body, opts, ai, steps=['%s : %s' % (_SCN[i][2], _SCN[i][1]) for i in ids if True][:5] if False else ['정답 : ' + _hint(target), '다른 현상은 ' + ', '.join('%s(%s)' % (_SCN[i][2], _SCN[i][1]) for i in ids if i != ans_i) + '이다.'],
                       lv='중', fam='f', core='현상의 조건으로 과정을 판별한다.', point='과정에 해당하는 일상 현상을 고른다.')
    # c: bogi
    for _ in range(60):
        ids = r.sample(range(len(_SCN)), 3)
        stm = [_scn_stmt(r, i) for i in ids]
        if any(s[1] for s in stm): break
    else:
        return None
    intro = '다음은 일상생활에서 볼 수 있는 세 가지 현상이다.'
    labs = ['(가)', '(나)', '(다)']
    ans_stm = []
    # 문장 앞에 (가) 현상 표시: 현상 설명을 상자로 주고 문장에는 (가)~(다)로 지칭
    texts = [(l, _SCN[i][0], _SCN[i][2]) for l, i in zip(labs, ids)]
    new = []
    for l, i, s in zip(labs, ids, stm):
        t = s[0].replace(_SCN[i][2], l, 1)
        new.append((t, s[1], s[2]))
    return bogi(intro, new, pre=BOX3([(l, t) for l, t, _ in texts]) + P('이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), r=r, ask='', lv='중', fam='c',
                core='단열(빠른 변화)에서는 Q = 0 이고 팽창하면 냉각, 압축하면 가열된다.', point='일상 현상을 열역학 과정으로 해석하는 <보기>.')

def BOX_(t):
    return '<div class="bogi"><p>%s</p></div>' % t

def BOX3(items):
    return '<div class="bogi">' + ''.join('<p>%s %s</p>' % (l, t) for l, t in items) + '</div>'

def _hint(proc):
    return {'단열 팽창': '기체가 빠르게 팽창하여 열 교환이 거의 없고 온도가 내려간다',
            '단열 압축': '기체가 빠르게 압축되어 열 교환이 거의 없고 온도가 올라간다',
            '등적 가열': '부피가 변하지 않은 채 열을 받아 압력과 온도가 올라간다',
            '등적 냉각': '부피가 변하지 않은 채 열을 잃어 압력과 온도가 내려간다',
            '등압 팽창': '압력이 일정하게 유지되며 가열되어 부피가 커진다',
            '등압 압축': '압력이 일정하게 유지되며 냉각되어 부피가 줄어든다',
            '등온 팽창': '온도가 일정하게 유지되며 열을 흡수하여 팽창한다',
            '등온 압축': '온도가 일정하게 유지되며 열을 방출하며 압축된다'}[proc]
