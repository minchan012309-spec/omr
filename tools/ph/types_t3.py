# -*- coding: utf-8 -*-
"""Ⅱ-A / Ⅱ-B 열역학 추가 유형 (ph114~ph122) 생성기.
이상 기체: PV = nRT (T ∝ PV), 단원자 분자 U = (3/2)PV, W = PΔV, Q = ΔU + W.
눈금 단위: 압력 P₀, 부피 V₀, 절대 온도 T₀ (= P₀V₀/nR)."""
from phlib import *
import math, functools, itertools
from fractions import Fraction

GAM = 5.0 / 3.0
KR = {'P': '등압', 'V': '등적', 'T': '등온', 'A': '단열'}
NMS = 'ABCD'
PLN = {'PV': 'P-V', 'PT': 'P-T', 'VT': 'V-T'}
PLK = {'PV': '압력 P와 부피 V', 'PT': '압력 P와 절대 온도 T', 'VT': '부피 V와 절대 온도 T'}
AXN = {'PV': ('V (V₀)', 'P (P₀)'), 'PT': ('T (T₀)', 'P (P₀)'), 'VT': ('T (T₀)', 'V (V₀)')}
AXQ = {'PV': ('V', 'P'), 'PT': ('T', 'P'), 'VT': ('T', 'V')}
SHAPE = {
    'PV': {'P': 'V축에 나란한(수평) 직선', 'V': 'P축에 나란한(수직) 직선', 'T': '반비례 곡선(PV 일정)'},
    'PT': {'P': 'T축에 나란한(수평) 직선', 'V': '원점을 지나는 직선', 'T': 'P축에 나란한(수직) 직선'},
    'VT': {'V': 'T축에 나란한(수평) 직선', 'P': '원점을 지나는 직선', 'T': 'V축에 나란한(수직) 직선'},
}
WHY = {'P': '압력이 일정', 'V': '부피가 일정', 'T': 'PV(절대 온도)가 일정'}
CAP = ['(가)', '(나)', '(다)', '(라)', '(마)']


# ============================================================ 공통 도구
def mco(body, right, wrongs, *, steps, core='', point='', lv='중', fam='a', r=None, ref=None, sort='shuf'):
    seen = {re.sub(r'\s+', '', plain(right))}
    ws = []
    for w in wrongs:
        kk = re.sub(r'\s+', '', plain(w))
        if kk in seen: continue
        seen.add(kk); ws.append(w)
    if len(ws) < 4: return None
    return mc(body, right, ws, steps=steps, core=core, point=point, lv=lv, fam=fam, sort=sort, r=r, ref=ref)


def mc_list(body, options, ans_idx, *, steps, core='', point='', lv='중', fam='a', ref=None):
    assert len(options) == 5 and 0 <= ans_idx < 5
    return Item(body=body, opts=list(options), ans=ans_idx + 1, steps=steps, core=core, point=point, lv=lv, fam=fam, vertical=None, ref=ref)


def fr_str(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else '%d/%d' % (x.numerator, x.denominator)


def ratio_list(vals):
    """정수·분수 목록을 가장 간단한 정수비 문자열로. '1 : 2 : 3'"""
    vals = [Fraction(v) for v in vals]
    L = 1
    for v in vals: L = L * v.denominator // math.gcd(L, v.denominator)
    xs = [int(v * L) for v in vals]
    g = 0
    for x in xs: g = math.gcd(g, abs(x))
    g = g or 1
    return ' : '.join(str(x // g) for x in xs)


def sg(x, eps=1e-9):
    return 1 if x > eps else (-1 if x < -eps else 0)


def sj(x, unit='J'):
    if abs(x) < 1e-9: return '0 ' + unit
    return ('+' if x > 0 else '−') + num(abs(x)) + ' ' + unit


def sgs(s):
    return {1: '+', -1: '−', 0: '0'}[s]


def pick_stmts(r, bank, n=3):
    """bank: (문장, 참거짓, 풀이문, 그룹). 그룹이 서로 다른 n개를 뽑는다. 참 1개 이상."""
    for _ in range(60):
        sel = r.sample(bank, n)
        if len({s[3] for s in sel}) == n and any(s[1] for s in sel):
            return [(s[0], s[1], s[2]) for s in sel]
    return None


# ============================================================ 이상 기체 과정 판정
def ptype(a, b):
    """두 상태 a=(P,V), b=(P,V) 를 잇는 과정 종류. 'P' 등압, 'V' 등적, 'T' 등온, 없으면 None."""
    (pa, va), (pb, vb) = a, b
    if abs(pa - pb) < 1e-9 and abs(va - vb) < 1e-9: return None
    if abs(pa - pb) < 1e-9: return 'P'
    if abs(va - vb) < 1e-9: return 'V'
    if abs(pa * va - pb * vb) < 1e-9: return 'T'
    return None


def seg_vals(kind, a, b):
    """(ΔU, W, Q) — P₀V₀ 단위. kind: P V T A."""
    (pa, va), (pb, vb) = a, b
    dU = 1.5 * (pb * vb - pa * va)
    if kind == 'P': W = pa * (vb - va)
    elif kind == 'V': W = 0.0
    elif kind == 'T': W = pa * va * math.log(vb / va)
    else: W = 1.5 * (pa * va - pb * vb)
    return dU, W, dU + W


def seg_signs(kind, a, b):
    """규칙으로 정한 (ΔU, W, Q) 부호를 수치 계산과 교차 검증해서 돌려준다."""
    dU, W, Q = seg_vals(kind, a, b)
    (pa, va), (pb, vb) = a, b
    dT, dV, dP = pb * vb - pa * va, vb - va, pb - pa
    if kind == 'P': rule = (sg(dT), sg(dV), sg(dV))
    elif kind == 'V': rule = (sg(dT), 0, sg(dP))
    elif kind == 'T': rule = (0, sg(dV), sg(dV))
    else: rule = (sg(dT), sg(dV), 0)
    got = (sg(dU, 1e-7), sg(W, 1e-7), sg(Q, 1e-7))
    assert got == rule, (kind, got, rule)
    return rule


def net_work(sts, kinds):
    return sum(seg_vals(kinds[i], sts[i], sts[(i + 1) % len(sts)])[1] for i in range(len(sts)))


def ccw_label(w):
    return '시계 방향' if w > 0 else '반시계 방향'


# ============================================================ 격자 순환 과정 목록
@functools.lru_cache(None)
def grid_cycles(seq, G=5):
    n = len(seq)
    pts = [(p, v) for p in range(1, G + 1) for v in range(1, G + 1)]
    nb = {a: {} for a in pts}
    for a in pts:
        for b in pts:
            t = ptype(a, b)
            if t: nb[a].setdefault(t, []).append(b)
    out = []

    def rec(path):
        i = len(path)
        if i == n:
            if ptype(path[-1], path[0]) == seq[-1]: out.append(tuple(path))
            return
        for b in nb[path[-1]].get(seq[i - 1], []):
            if b in path: continue
            rec(path + [b])
    for a in pts: rec([a])
    return out


SEQ3 = [''.join(p) for p in itertools.permutations('PVT')]
SEQ4 = [''.join(s) for s in itertools.product('PVT', repeat=4) if all(s[i] != s[(i + 1) % 4] for i in range(4))]


def _lg(s):
    return (math.log(s[1]), math.log(s[0]))


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _seg_hit(p1, p2, p3, p4):
    d1, d2, d3, d4 = _cross(p3, p4, p1), _cross(p3, p4, p2), _cross(p1, p2, p3), _cross(p1, p2, p4)
    if ((d1 > 1e-9 and d2 < -1e-9) or (d1 < -1e-9 and d2 > 1e-9)) and ((d3 > 1e-9 and d4 < -1e-9) or (d3 < -1e-9 and d4 > 1e-9)): return True
    if abs(d1) < 1e-9 and abs(d2) < 1e-9: return True   # 겹침(한 직선 위)
    return False


def loop_simple(sts):
    """로그 좌표에서 모든 과정이 직선이므로 선분 교차로 단순 폐곡선인지 검사."""
    n = len(sts)
    L = [_lg(s) for s in sts]
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1: continue
            if _seg_hit(L[i], L[(i + 1) % n], L[j], L[(j + 1) % n]): return False
    return True


def pick_cycle(r, n=3, need=None):
    """격자 순환 과정 하나를 뽑는다. 반환: (상태 리스트, 과정 종류 문자열). 못 찾으면 None."""
    for _ in range(30):
        seq = r.choice(SEQ3 if n == 3 else SEQ4)
        cs = grid_cycles(seq, 5)
        if not cs: continue
        c = list(r.choice(cs))
        if not loop_simple(c): continue
        if need and not need(c, seq): continue
        return c, seq
    return None


# ============================================================ 그래프 그리기
def to_xy(plane, s):
    P, V = s
    return {'PV': (V, P), 'PT': (P * V, P), 'VT': (P * V, V)}[plane]


def curve_xy(plane, a, b, kind, n=40):
    """plane 좌표계에서 a→b 의 점열. kind: P V T A(단열, P-V 에서만)."""
    if plane == 'PV' and kind in ('T', 'A'):
        (pa, va), (pb, vb) = a, b
        pts = []
        for i in range(n + 1):
            v = va + (vb - va) * i / n
            p = pa * va / v if kind == 'T' else pa * (va / v) ** GAM
            pts.append((v, p))
        return pts
    return [to_xy(plane, a), to_xy(plane, b)]


def _along(poly, f):
    """점열 위 길이 비율 f(0~1) 의 점."""
    L = [0.0]
    for i in range(1, len(poly)):
        L.append(L[-1] + math.hypot(poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]))
    t = L[-1] * f
    for i in range(1, len(poly)):
        if L[i] >= t - 1e-9:
            d = (t - L[i - 1]) / ((L[i] - L[i - 1]) or 1)
            return (poly[i - 1][0] + (poly[i][0] - poly[i - 1][0]) * d, poly[i - 1][1] + (poly[i][1] - poly[i - 1][1]) * d)
    return poly[-1]


def through_origin(p, q):
    """두 점을 잇는 직선이 원점을 지나는가(점이 서로 다르고 원점이 아님)."""
    return abs(p[0] * q[1] - p[1] * q[0]) < 1e-9 and (p != q)


def loop_fig(plane, names, sts, kinds, numbered=True, w=292, h=226, ext=True, color=BL, lab_off=None, hl=None):
    """순환 과정 그림. sts: [(P,V)], kinds: 각 과정 종류(P V T A). numbered: 눈금 표시."""
    n = len(sts)
    pts_all = []
    for i in range(n):
        pts_all += curve_xy(plane, sts[i], sts[(i + 1) % n], kinds[i])
    xm = max(x for x, _ in pts_all)
    ym = max(y for _, y in pts_all)
    if numbered:
        xmax = math.ceil(xm) + 0.9 if plane == 'PV' else xm + max(1.2, xm * 0.1)
        ymax = math.ceil(ym) + 0.8
    else:
        xmax, ymax = xm * 1.22, ym * 1.2
    p = Plot(w, h, xmax, ymax, ml=50 if numbered else 30, mr=16, mt=28, mb=34)
    xl, yl = AXN[plane] if numbered else AXQ[plane]
    if numbered:
        xs = sorted({to_xy(plane, s)[0] for s in sts})
        if plane == 'PV':
            xt = list(range(0, int(xmax) + 1)); yt = list(range(0, int(ymax) + 1))
        else:
            xt = [0] + xs; yt = list(range(0, int(ymax) + 1))
            pxs = [p.px(t) for t in xt[1:]]
            for i in range(1, len(pxs)):
                assert pxs[i] - pxs[i - 1] >= 17, '눈금 겹침'
            assert pxs[0] - p.px(0) >= 15, '눈금 겹침'
        p.axes('', '', xticks=xt, yticks=yt, grid=(plane == 'PV'))
        p.text(w - 12, h - 5, xl, 12.5, 'end', True, GR)
        p.text(p.ml + 8, 14, yl, 12.5, 'start', True, GR)
        if plane != 'PV':
            for s in sts:
                x, y = to_xy(plane, s)
                p.dash_to_axes(x, y)
    else:
        p.axes('', '', xticks=(), yticks=(), grid=False)
        p.text(w - 14, h - 14, xl, 14, 'end', True, GR, True)
        p.text(p.ml + 8, 16, yl, 14, 'start', True, GR, True)
        p.text(p.ml - 8, h - 21, 'O', 12, 'end', False, GR)
    cx = sum(to_xy(plane, s)[0] for s in sts) / n
    cy = sum(to_xy(plane, s)[1] for s in sts) / n
    for i in range(n):
        a, b = sts[i], sts[(i + 1) % n]
        poly = curve_xy(plane, a, b, kinds[i])
        col = (hl or {}).get(i, color)
        if ext and plane != 'PV' and through_origin(to_xy(plane, a), to_xy(plane, b)):
            q0, q1 = to_xy(plane, a), to_xy(plane, b)
            near = q0 if math.hypot(*q0) < math.hypot(*q1) else q1
            p.line(p.px(near[0]), p.py(near[1]), p.px(0), p.py(0), GR, 1.1, '2 3')
        p.pl(poly, col, 2.6)
        m1, m2 = _along(poly, 0.5 - 0.04), _along(poly, 0.5 + 0.04)
        p._head(p.px(m1[0]), p.py(m1[1]), p.px(m2[0]) , p.py(m2[1]), col, 2.2, 9.5)
    for i, nm in enumerate(names):
        x, y = to_xy(plane, sts[i])
        p.circ(p.px(x), p.py(y), 3.6, INK, INK, 1)
        dx, dy = (lab_off or {}).get(nm, (None, None))
        if dx is None:
            ox, oy = p.px(x) - p.px(cx), p.py(y) - p.py(cy)
            ln = math.hypot(ox, oy) or 1
            dx, dy = 13 * ox / ln, 13 * oy / ln + 5
        p.text(p.px(x) + dx, p.py(y) + dy, nm, 14.5, 'middle', True, INK, True)
    return p.svg()


def _sig(plane, labeled):
    """labeled: [(P,V)] 순환 순서. 그래프를 눈으로 구별하는 특징(종류·변화 방향)."""
    n = len(labeled)
    out = []
    for i in range(n):
        a, b = labeled[i], labeled[(i + 1) % n]
        (x1, y1), (x2, y2) = to_xy(plane, a), to_xy(plane, b)
        out.append((ptype(a, b), sg(x2 - x1), sg(y2 - y1)))
    return tuple(out)


def thumbs(plane, graphs, w=340, h=232):
    """graphs: 5개의 [(P,V) …](순환 순서). 각 그래프를 눈금 없이 작게 그린 한 장의 SVG. 라벨 (가)~(마)."""
    allp = []
    for g in graphs:
        for i in range(len(g)):
            allp.append(to_xy(plane, g[i]))
    xm = max(x for x, _ in allp) * 1.12
    ym = max(y for _, y in allp) * 1.12
    f = Fig(w, h)
    pw, ph = 108, 96
    xl, yl = AXQ[plane]
    for gi, g in enumerate(graphs):
        row, col = (0, gi) if gi < 3 else (1, gi - 3)
        x0 = 6 + col * 112 + (0 if row == 0 else 56)
        y0 = 4 + row * 114
        ox, oy = x0 + 16, y0 + ph - 14
        ex, ey = x0 + pw - 4, y0 + 12
        f.rect(x0 - 2, y0 - 2, pw + 4, ph + 20, 'none', '#d5dce8', 1, 6)
        f.arrow(ox, oy, ex, oy, INK, 1.3)
        f.arrow(ox, oy, ox, ey, INK, 1.3)
        f.text(ex - 2, oy + 13, xl, 12, 'end', True, GR, True)
        f.text(ox - 4, ey + 4, yl, 12, 'end', True, GR, True)
        f.text(ox - 3, oy + 12, 'O', 10.5, 'end', False, GR)
        sx = (ex - ox - 10) / xm
        sy = (oy - ey - 8) / ym
        mp = lambda s: (ox + to_xy(plane, s)[0] * sx, oy - to_xy(plane, s)[1] * sy)
        n = len(g)
        cxs = sum(mp(s)[0] for s in g) / n
        cys = sum(mp(s)[1] for s in g) / n
        for i in range(n):
            a, b = g[i], g[(i + 1) % n]
            t = ptype(a, b)
            poly = [mp_ for mp_ in (curve_xy(plane, a, b, t if t in ('T',) else 'L') if True else [])]
            # 화면 좌표로 변환
            pp = [(ox + x * sx, oy - y * sy) for (x, y) in poly]
            q0, q1 = to_xy(plane, a), to_xy(plane, b)
            if plane != 'PV' and through_origin(q0, q1):
                near = q0 if math.hypot(*q0) < math.hypot(*q1) else q1
                f.line(ox + near[0] * sx, oy - near[1] * sy, ox, oy, GR, 1, '2 3')
            f.poly(pp, 'none', BL, 2.0, close=False)
            m1, m2 = _along(pp, 0.46), _along(pp, 0.54)
            f._head(m1[0], m1[1], m2[0], m2[1], BL, 2, 8)
        for i, s in enumerate(g):
            x, y = mp(s)
            f.circ(x, y, 2.8, INK, INK, 1)
            ox2, oy2 = x - cxs, y - cys
            ln = math.hypot(ox2, oy2) or 1
            f.text(x + 10.5 * ox2 / ln, y + 10.5 * oy2 / ln + 4.5, NMS[i], 12.5, 'middle', True, INK, True)
        f.text(x0 + pw / 2, y0 + ph + 12, CAP[gi], 12.5, 'middle', True, INK)
    return f.svg()


def make_thumb_set(r, plane, states, nm):
    """정답 그래프(states 순서 그대로)와 라벨을 바꾼 오답 4개. (그래프 5개, 정답 위치) 또는 None."""
    n = len(states)
    good = _sig(plane, states)
    cands = []
    for perm in itertools.permutations(range(n)):
        if perm == tuple(range(n)): continue
        g = [states[perm[i]] for i in range(n)]
        if _sig(plane, g) == good: continue
        cands.append(g)
    if len(cands) < 4: return None
    ws = r.sample(cands, 4)
    pos = r.randrange(5)
    gs = ws[:pos] + [list(states)] + ws[pos:]
    return gs, pos


# ============================================================ 보기 문장 은행(순환 과정 공통)
def stmts_cycle(r, names, sts, kinds, plane):
    """순환 과정 그래프에 대한 <보기> 문장 후보들 (문장, 참거짓, 풀이, 그룹)."""
    n = len(sts)
    Ts = [p * v for p, v in sts]
    seg = lambda i: '%s→%s' % (names[i], names[(i + 1) % n])
    out = []
    # 과정 종류
    for i in range(n):
        t = kinds[i]
        c = t if r.random() < 0.5 else r.choice([x for x in 'PVT' if x != t])
        out.append(('%s 과정은 %s 과정이다.' % (seg(i), KR[c]), c == t, '%s에서는 %s하므로 %s 과정이다.' % (seg(i), WHY[t], KR[t]), 'type'))
    # 온도 변화
    i = r.randrange(n)
    dT = Ts[(i + 1) % n] - Ts[i]
    c = r.choice(['증가한다', '감소한다', '일정하다'])
    truth = {'증가한다': dT > 0, '감소한다': dT < 0, '일정하다': dT == 0}[c]
    real = '증가한다' if dT > 0 else ('감소한다' if dT < 0 else '일정하다')
    out.append(('%s 과정에서 기체의 온도는 %s.' % (seg(i), c), truth, '%s에서 PV 가 %d → %d (×P₀V₀) 이므로 기체의 온도는 %s.' % (seg(i), Ts[i], Ts[(i + 1) % n], real), 'temp'))
    # 최고 온도 상태
    mx = max(Ts)
    if Ts.count(mx) == 1:
        c = r.randrange(n)
        out.append(('기체의 온도가 가장 높은 상태는 %s이다.' % names[c], Ts[c] == mx, '각 상태의 PV 는 ' + ', '.join('%s: %d' % (names[j], Ts[j]) for j in range(n)) + ' (×P₀V₀) 이므로 온도가 가장 높은 상태는 %s이다.' % names[Ts.index(mx)], 'maxT'))
    mn = min(Ts)
    if Ts.count(mn) == 1:
        c = r.randrange(n)
        out.append(('기체의 온도가 가장 낮은 상태는 %s이다.' % names[c], Ts[c] == mn, '각 상태의 PV 는 ' + ', '.join('%s: %d' % (names[j], Ts[j]) for j in range(n)) + ' (×P₀V₀) 이므로 온도가 가장 낮은 상태는 %s이다.' % names[Ts.index(mn)], 'minT'))
    # 열 출입
    i = r.randrange(n)
    dU, W, Q = seg_signs(kinds[i], sts[i], sts[(i + 1) % n])
    c = r.choice(['흡수', '방출'])
    out.append(('%s 과정에서 기체는 열을 %s한다.' % (seg(i), c), (Q > 0) == (c == '흡수'),
                '%s에서 ΔU %s, W %s 이므로 Q = ΔU + W %s 이다. 기체는 열을 %s한다.' % (seg(i), _zs(dU), _zs(W), _zs(Q), '흡수' if Q > 0 else '방출'), 'Q'))
    # 일
    i = r.randrange(n)
    dU, W, Q = seg_signs(kinds[i], sts[i], sts[(i + 1) % n])
    c = r.choice(['외부에 일을 한다', '외부로부터 일을 받는다', '일을 하지도 받지도 않는다'])
    truth = {'외부에 일을 한다': W > 0, '외부로부터 일을 받는다': W < 0, '일을 하지도 받지도 않는다': W == 0}[c]
    real = {1: '외부에 일을 한다(팽창)', -1: '외부로부터 일을 받는다(압축)', 0: '일을 하지도 받지도 않는다(부피 일정)'}[W]
    out.append(('%s 과정에서 기체는 %s.' % (seg(i), c), truth, '%s에서 부피가 %s 기체는 %s.' % (seg(i), {1: '증가하므로', -1: '감소하므로', 0: '변하지 않으므로'}[W], real), 'W'))
    # 내부 에너지
    i = r.randrange(n)
    dU, W, Q = seg_signs(kinds[i], sts[i], sts[(i + 1) % n])
    c = r.choice(['증가한다', '감소한다', '변하지 않는다'])
    truth = {'증가한다': dU > 0, '감소한다': dU < 0, '변하지 않는다': dU == 0}[c]
    real = {1: '증가한다', -1: '감소한다', 0: '변하지 않는다'}[dU]
    out.append(('%s 과정에서 기체의 내부 에너지는 %s.' % (seg(i), c), truth, '내부 에너지는 온도에 비례하는데 %s에서 온도가 %s 내부 에너지는 %s.' % (seg(i), {1: '높아지므로', -1: '낮아지므로', 0: '변하지 않으므로'}[dU], real), 'dU'))
    # 같은 온도
    i, j = sorted(r.sample(range(n), 2))
    out.append(('%s와 %s에서 기체의 온도는 같다.' % (names[i], names[j]), Ts[i] == Ts[j], '%s의 PV = %d, %s의 PV = %d (×P₀V₀) 이므로 온도는 %s.' % (names[i], Ts[i], names[j], Ts[j], '같다' if Ts[i] == Ts[j] else '같지 않다'), 'eqT'))
    # 한 순환
    Wn = net_work(sts, kinds)
    assert abs(sum(seg_vals(kinds[i], sts[i], sts[(i + 1) % n])[0] for i in range(n))) < 1e-9
    c = r.choice(['양(+)', '음(−)'])
    out.append(('한 순환 동안 기체가 외부에 한 순 일은 %s이다.' % c, (Wn > 0) == (c == '양(+)'),
                'P-V 그래프에서 순환이 %s이므로 한 순환 동안 기체가 한 순 일은 %s이다.' % (ccw_label(Wn), '양(+)' if Wn > 0 else '음(−)'), 'net'))
    out.append(('한 순환을 마치고 처음 상태로 돌아오면 기체의 내부 에너지 변화는 0이다.', True, '내부 에너지는 상태(온도)에 따라 정해지므로 처음 상태로 돌아오면 변화량은 0이다.', 'cyc'))
    out.append(('한 순환 동안 기체가 흡수한 열의 합은 방출한 열의 합보다 %s.' % ('크다' if Wn > 0 else '작다'), True,
                '한 순환에서 ΔU = 0 이므로 순 흡수 열 = 한 일 = %s이다.' % ('양(+)' if Wn > 0 else '음(−)'), 'cyc2'))
    out.append(('한 순환 동안 기체가 흡수한 열의 합은 방출한 열의 합과 항상 같다.', False, '한 순환에서 Q = W 이므로 한 일이 0이 아니면 흡수한 열과 방출한 열은 다르다.', 'cyc2'))
    # 그래프 모양
    i = r.randrange(n)
    t = kinds[i]
    if plane == 'PV':
        c = r.choice(['P', 'V', 'T'])
        out.append(('%s 과정은 이 그래프에서 %s으로 나타난다.' % (seg(i), SHAPE['PV'][c]), c == t, '%s는 %s 과정이므로 P-V 그래프에서 %s으로 나타난다.' % (seg(i), KR[t], SHAPE['PV'][t]), 'geom'))
    else:
        q0, q1 = to_xy(plane, sts[i]), to_xy(plane, sts[(i + 1) % n])
        tr = through_origin(q0, q1)
        out.append(('%s 과정은 이 그래프에서 원점을 지나는 직선으로 나타난다.' % seg(i), tr,
                    '%s는 %s 과정이므로 %s 그래프에서 %s으로 나타난다.' % (seg(i), KR[t], PLN[plane], SHAPE[plane][t]), 'geom'))
    return out


def _zs(s):
    return {1: '> 0', -1: '< 0', 0: '= 0'}[s]


def state_tab(names, sts):
    return ', '.join('%s(P=%s, V=%s, PV=%s)' % (names[i], num(sts[i][0]), num(sts[i][1]), num(sts[i][0] * sts[i][1])) for i in range(len(sts)))
