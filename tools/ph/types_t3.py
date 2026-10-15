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
    'PV': {'P': 'V축에 나란한(수평) 직선', 'V': 'P축에 나란한(수직) 직선', 'T': '반비례 곡선(PV 일정)', 'A': '등온 곡선보다 가파른 곡선'},
    'PT': {'P': 'T축에 나란한(수평) 직선', 'V': '원점을 지나는 직선', 'T': 'P축에 나란한(수직) 직선'},
    'VT': {'V': 'T축에 나란한(수평) 직선', 'P': '원점을 지나는 직선', 'T': 'V축에 나란한(수직) 직선'},
}
WHY = {'P': '압력이 일정', 'V': '부피가 일정', 'T': 'PV(절대 온도)가 일정', 'A': '열 출입이 없음(Q=0)'}
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
            poly = curve_xy(plane, a, b, 'T' if t == 'T' else 'L')
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
        pool = 'PVTA' if 'A' in kinds else 'PVT'
        c = t if r.random() < 0.5 else r.choice([x for x in pool if x != t])
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
        c = r.choice(['P', 'V', 'T', 'A'] if 'A' in kinds else ['P', 'V', 'T'])
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


# ============================================================ ph114 P-V · P-T · V-T 그래프의 전환
def _intro(names, plane):
    n = len(names)
    path = '→'.join(names) + '→' + names[0]
    return '그림은 일정량의 이상 기체의 상태가 %s를 따라 변할 때 기체의 %s를 나타낸 것이다.' % (path, PLK[plane])


def _why_steps(names, sts, kinds, plane):
    n = len(sts)
    return ['과정 종류 : ' + ', '.join('%s→%s %s' % (names[i], names[(i + 1) % n], KR[kinds[i]]) for i in range(n)) + ' (%s)' % ', '.join(WHY[kinds[i]] for i in range(n)),
            '%s 그래프에서의 모양 : ' % PLN[plane] + ', '.join('%s→%s %s' % (names[i], names[(i + 1) % n], SHAPE[plane][kinds[i]]) for i in range(n))]


@T('ph114')
def g114(r, k):
    n = r.choice([3, 3, 3, 4])
    got = pick_cycle(r, n)
    if not got: return None
    sts, seq = got
    kinds = list(seq)
    names = list(NMS[:n])
    for i in range(n):
        assert ptype(sts[i], sts[(i + 1) % n]) == kinds[i]
    form = r.choice(['conv', 'conv', 'conv', 'pair', 'val', 'val', 'sign', 'bogi', 'bogi'])
    steps_state = '상태값 (P₀, V₀, T₀ 단위, T = PV) : ' + ', '.join('%s(%d, %d, %d)' % (names[i], sts[i][0], sts[i][1], sts[i][0] * sts[i][1]) for i in range(n))
    if form == 'conv':
        src, dst = r.choice([('PV', 'PT'), ('PV', 'PT'), ('PV', 'VT'), ('PV', 'VT'), ('PT', 'PV'), ('VT', 'PV'), ('PT', 'VT'), ('VT', 'PT')])
        try:
            fig = loop_fig(src, names, sts, kinds, numbered=True)
        except AssertionError:
            return None
        tset = make_thumb_set(r, dst, sts, names)
        if not tset: return None
        gs, pos = tset
        # 정답 그래프의 도착 좌표계 특징이 맞는지 한 번 더 확인
        for i in range(n):
            a, b = sts[i], sts[(i + 1) % n]
            q0, q1 = to_xy(dst, a), to_xy(dst, b)
            if kinds[i] == 'V' and dst == 'PT' or kinds[i] == 'P' and dst == 'VT':
                assert through_origin(q0, q1)
            if kinds[i] == 'T' and dst != 'PV':
                assert abs(q0[0] - q1[0]) < 1e-9
        body = P(_intro(names, src) + ' 이 과정을 %s 그래프로 나타낸 것으로 가장 적절한 것은?' % PLN[dst]) + FIG(fig, '66%') + FIG(thumbs(dst, gs), '100%')
        steps = _why_steps(names, sts, kinds, dst) + [steps_state, '이 모양과 상태 기호의 위치가 모두 일치하는 그래프는 %s이다.' % CAP[pos]]
        lv = '상' if (n == 4 or src != 'PV') and r.random() < 0.6 else '중'
        return mc_list(body, CAP, pos, steps=steps, lv=lv, fam='a',
                       core='등압·등적·등온 과정은 P-V, P-T, V-T 그래프에서 각각 고유한 모양(원점을 지나는 직선, 축에 나란한 직선, 반비례 곡선)으로 나타난다.',
                       point='과정의 종류를 먼저 판별하고 PV=nRT 로 다른 좌표계의 값을 구해 그래프를 바꾼다.')
    if form == 'pair':
        plane = r.choice(['PV', 'PT', 'VT'])
        try:
            fig = loop_fig(plane, names, sts, kinds, numbered=r.random() < 0.7)
        except AssertionError:
            return None
        seg = ['%s→%s' % (names[i], names[(i + 1) % n]) for i in range(n)]
        right = ', '.join(KR[c] for c in kinds)
        wrongs = []
        for _ in range(40):
            c = list(kinds)
            for j in r.sample(range(n), r.choice([1, 2])):
                c[j] = r.choice([x for x in 'PVT' if x != c[j]])
            wrongs.append(', '.join(KR[x] for x in c))
        body = P(_intro(names, plane) + ' %s 과정을 각각 옳게 나타낸 것은?' % ', '.join(seg)) + FIG(fig, '66%')
        steps = _why_steps(names, sts, kinds, plane)[::-1][:1] + ['따라서 %s 은(는) 차례로 %s 과정이다.' % (', '.join(seg), right)]
        steps = ['%s 그래프에서 ' % PLN[plane] + ', '.join('%s는 %s' % (seg[i], SHAPE[plane][kinds[i]]) for i in range(n)) + '이므로', '%s 은(는) 차례로 %s 과정이다.' % (', '.join(seg), right)]
        return mco(body, right, wrongs, steps=steps, lv='하' if plane == 'PV' else '중', fam='b', r=r,
                   core='P-V 그래프의 수평선은 등압, 수직선은 등적, 반비례 곡선은 등온이고, P-T·V-T 그래프에서는 원점을 지나는 직선이 각각 등적·등압이다.',
                   point='그래프의 모양으로 과정의 종류를 판별한다.')
    if form == 'val':
        sub_form = r.choice(['Tratio', 'Tratio', 'Vfrom', 'Pfrom'])
        if sub_form == 'Tratio':
            i, j = r.sample(range(n), 2)
            Ti, Tj = sts[i][0] * sts[i][1], sts[j][0] * sts[j][1]
            if Ti == Tj: return None
            ans = Fraction(Tj, Ti)
            try:
                fig = loop_fig('PV', names, sts, kinds, numbered=True)
            except AssertionError:
                return None
            body = P(_intro(names, 'PV') + ' 상태 %s에서 기체의 절대 온도는 상태 %s에서의 몇 배인가?' % (names[j], names[i])) + FIG(fig, '66%')
            pa, pb = Fraction(sts[j][0], sts[i][0]), Fraction(sts[j][1], sts[i][1])
            ws = [1 / ans, pa, pb, Fraction(sts[j][0] + sts[j][1], sts[i][0] + sts[i][1]), pa + pb, ans + 1, ans * 2]
            right = fr_str(ans) + '배'
            steps = ['PV = nRT 이므로 T ∝ PV 이다.', 'T%s ∝ %d × %d = %d, T%s ∝ %d × %d = %d' % (names[j], sts[j][0], sts[j][1], Tj, names[i], sts[i][0], sts[i][1], Ti),
                     'T%s / T%s = %d / %d = %s' % (names[j], names[i], Tj, Ti, fr_str(ans))]
            return mco(body, right, [fr_str(w) + '배' for w in ws if w > 0], steps=steps, lv='하', fam='c', r=r,
                       core='이상 기체의 절대 온도는 PV 에 비례한다.', point='그래프에서 P, V 눈금을 읽어 PV 의 비를 구한다.')
        if sub_form == 'Vfrom':
            plane = 'PT'
            try:
                fig = loop_fig(plane, names, sts, kinds, numbered=True)
            except AssertionError:
                return None
            i, j = r.sample(range(n), 2)
            Ti, Tj = sts[i][0] * sts[i][1], sts[j][0] * sts[j][1]
            Pi, Pj = sts[i][0], sts[j][0]
            Vi = sts[i][1]
            Vj = Fraction(Vi) * Fraction(Tj, Pj) / Fraction(Ti, Pi)
            assert Vj == sts[j][1]
            body = P(_intro(names, plane) + ' 상태 %s에서 기체의 부피가 %s V₀일 때, 상태 %s에서 기체의 부피는? (단, 눈금 단위는 P₀, T₀이다.)' % (names[i], num(Vi), names[j])) + FIG(fig, '66%')
            ws = [Fraction(Vi) * Fraction(Tj, Ti), Fraction(Vi) * Fraction(Pj, Pi), Fraction(Vi) * Fraction(Pi, Pj), Fraction(Vi) * Fraction(Ti, Tj), Vj + 1, Vj * 2, Vj + 2]
            steps = ['V = nRT/P 이므로 V ∝ T/P 이다.', 'V%s ∝ %d/%d, V%s ∝ %d/%d' % (names[i], Ti, Pi, names[j], Tj, Pj),
                     'V%s = %s V₀ × (%d/%d) ÷ (%d/%d) = %s V₀' % (names[j], num(Vi), Tj, Pj, Ti, Pi, fr_str(Vj))]
            return mco(body, fr_str(Vj) + ' V₀', [fr_str(w) + ' V₀' for w in ws if w > 0], steps=steps, lv='중', fam='c', r=r,
                       core='V ∝ T/P 이므로 P-T 그래프에서 원점과 이은 직선의 기울기(P/T)가 클수록 부피가 작다.', point='P-T 그래프의 값에서 V 를 구한다.')
        plane = 'VT'
        try:
            fig = loop_fig(plane, names, sts, kinds, numbered=True)
        except AssertionError:
            return None
        i, j = r.sample(range(n), 2)
        Ti, Tj = sts[i][0] * sts[i][1], sts[j][0] * sts[j][1]
        Vi, Vj_ = sts[i][1], sts[j][1]
        Pi = sts[i][0]
        Pj = Fraction(Pi) * Fraction(Tj, Vj_) / Fraction(Ti, Vi)
        assert Pj == sts[j][0]
        body = P(_intro(names, plane) + ' 상태 %s에서 기체의 압력이 %s P₀일 때, 상태 %s에서 기체의 압력은? (단, 눈금 단위는 V₀, T₀이다.)' % (names[i], num(Pi), names[j])) + FIG(fig, '66%')
        ws = [Fraction(Pi) * Fraction(Tj, Ti), Fraction(Pi) * Fraction(Vj_, Vi), Fraction(Pi) * Fraction(Vi, Vj_), Fraction(Pi) * Fraction(Ti, Tj), Pj + 1, Pj * 2, Pj + 2]
        steps = ['P = nRT/V 이므로 P ∝ T/V 이다.', 'P%s ∝ %d/%d, P%s ∝ %d/%d' % (names[i], Ti, Vi, names[j], Tj, Vj_),
                 'P%s = %s P₀ × (%d/%d) ÷ (%d/%d) = %s P₀' % (names[j], num(Pi), Tj, Vj_, Ti, Vi, fr_str(Pj))]
        return mco(body, fr_str(Pj) + ' P₀', [fr_str(w) + ' P₀' for w in ws if w > 0], steps=steps, lv='중', fam='c', r=r,
                   core='P ∝ T/V 이므로 V-T 그래프에서 원점과 이은 직선의 기울기(V/T)가 클수록 압력이 작다.', point='V-T 그래프의 값에서 P 를 구한다.')
    if form == 'sign':
        plane = r.choice(['PV', 'PT', 'VT'])
        try:
            fig = loop_fig(plane, names, sts, kinds, numbered=True)
        except AssertionError:
            return None
        i = r.randrange(n)
        a, b = sts[i], sts[(i + 1) % n]
        dU, W, Q = seg_signs(kinds[i], a, b)
        right = 'W %s 0, ΔU %s 0, Q %s 0' % tuple({1: '>', -1: '<', 0: '='}[x] for x in (W, dU, Q))
        wr = []
        for t in itertools.product([1, -1, 0], repeat=3):
            if t != (W, dU, Q):
                wr.append('W %s 0, ΔU %s 0, Q %s 0' % tuple({1: '>', -1: '<', 0: '='}[x] for x in (t[0], t[1], t[2])))
        r.shuffle(wr)
        # 그럴듯한 오답(부호 하나만 바꾼 것)을 앞으로
        near = [x for x in wr if sum(1 for u, v in zip(x.split(', '), right.split(', ')) if u != v) == 1]
        wr = near + [x for x in wr if x not in near]
        seg = '%s→%s' % (names[i], names[(i + 1) % n])
        body = P(_intro(names, plane) + ' %s 과정에서 기체가 외부에 한 일 W, 내부 에너지 변화량 ΔU, 기체가 흡수한 열량 Q 의 부호를 옳게 나타낸 것은? (단, 기체가 열을 흡수하면 Q > 0, 외부에 일을 하면 W > 0 이다.)' % seg) + FIG(fig, '66%')
        steps = ['%s 은(는) %s 과정이다 (%s).' % (seg, KR[kinds[i]], WHY[kinds[i]]), steps_state,
                 '부피 %s → W %s 0, 온도(PV) %d → %d → ΔU %s 0, Q = ΔU + W %s 0' % ('증가' if b[1] > a[1] else ('감소' if b[1] < a[1] else '일정'), {1: '>', -1: '<', 0: '='}[W], a[0] * a[1], b[0] * b[1], {1: '>', -1: '<', 0: '='}[dU], {1: '>', -1: '<', 0: '='}[Q])]
        return mco(body, right, wr[:8], steps=steps, lv='중' if kinds[i] != 'T' else '상', fam='d', r=r,
                   core='Q = ΔU + W. 팽창이면 W>0, 온도가 오르면 ΔU>0 이고, 등온이면 ΔU=0 이므로 Q=W 이다.', point='그래프에서 부피·온도 변화를 읽어 W, ΔU, Q 의 부호를 정한다.')
    # bogi
    plane = r.choice(['PV', 'PT', 'VT', 'PT', 'VT'])
    try:
        fig = loop_fig(plane, names, sts, kinds, numbered=r.random() < 0.7)
    except AssertionError:
        return None
    bank = stmts_cycle(r, names, sts, kinds, plane)
    sel = pick_stmts(r, bank)
    if not sel: return None
    return bogi(_intro(names, plane), sel, pre=FIG(fig, '66%'), r=r, lv='중' if n == 3 else '상', fam='e',
                core='그래프에서 각 과정의 종류를 판별하면 온도·부피 변화로 ΔU, W, Q 의 부호를 알 수 있다.', point='과정 판별 후 열역학 제1법칙으로 <보기>를 판단한다.')


# ============================================================ ph115 피스톤으로 나뉜 두 기체
def _dots(f, x, y, w, h, n, col, seed):
    for i in range(n):
        px = x + 6 + ((i * 37 + seed * 11 + 5) % 97) / 97.0 * max(w - 12, 1)
        py = y + 6 + ((i * 61 + seed * 7 + 3) % 89) / 89.0 * max(h - 12, 1)
        f.circ(px, py, 2.7, col, 'none', 0)


def piston_fig(nA, nB, vA, vB, tA='', tB='', fixed=False, conduct=True, labels=('A', 'B'), nmA='', nmB='', w=330, h=150):
    """가로 실린더(단열 벽)와 피스톹. 부피 vA, vB 는 상대값(길이 비례)."""
    f = Fig(w, h)
    x0, x1 = 22, w - 22
    L = x1 - x0 - 12
    yt, yb = 46, 104
    xp = x0 + 6 + L * vA / (vA + vB)
    f.rect(x0, yt, xp - x0 - 3, yb - yt, '#e8f1fb', 'none', 0)
    f.rect(xp + 3, yt, x1 - xp - 3, yb - yt, '#fdecea', 'none', 0)
    _dots(f, x0, yt, xp - x0 - 3, yb - yt, nA, BL, 1)
    _dots(f, xp + 3, yt, x1 - xp - 3, yb - yt, nB, RD, 2)
    f.line(x0, yt - 2, x1, yt - 2, GR, 5)
    f.line(x0, yb + 2, x1, yb + 2, GR, 5)
    f.line(x0 - 2, yt - 4, x0 - 2, yb + 4, GR, 5)
    f.line(x1 + 2, yt - 4, x1 + 2, yb + 4, GR, 5)
    f.rect(xp - 3, yt, 6, yb - yt, '#9aa7b8' if conduct else '#586476', INK, 1.2)
    if fixed:
        f.rect(xp - 8, yt - 12, 16, 8, INK, INK, 1)
        f.text(xp, yt - 17, '고정 핀', 11.5, 'middle', True, INK)
    f.text((x0 + xp) / 2, yb + 24, labels[0] + (' ' + nmA if nmA else ''), 13, 'middle', True, BL)
    f.text((xp + x1) / 2, yb + 24, labels[1] + (' ' + nmB if nmB else ''), 13, 'middle', True, RD)
    if tA: f.text((x0 + xp) / 2, yb + 41, tA, 12, 'middle', False, GR)
    if tB: f.text((xp + x1) / 2, yb + 41, tB, 12, 'middle', False, GR)
    f.text(w / 2, 17, '(실린더 벽은 단열)', 11.5, 'middle', False, GR)
    f.text(xp, yt - 26 if fixed else yt - 8, '' if fixed else ('열전도 피스톤' if conduct else '단열 피스톤'), 11.5, 'middle', True, GR)
    return f.svg()


NRAT = [(1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2), (1, 4), (4, 1)]


def _nn(n):
    return ('N' if n == 1 else '%dN' % n)


def _eq_stmts(r, a, b, nA, nB):
    """열평형·힘의 평형 상태(열전도 피스톤, 단열 실린더)에서의 <보기> 후보."""
    out = []
    big = 'A' if nA > nB else 'B'
    q = Fraction(nB, nA)
    out.append(('A와 B의 압력은 같다.', True, '피스톤이 정지해 있으므로 두 기체가 피스톤을 미는 힘이 같고 단면적이 같으므로 압력이 같다.', 'P'))
    out.append(('A의 압력이 B의 압력보다 크다.', False, '피스톤이 정지해 있으므로 두 기체의 압력은 같다.', 'P'))
    out.append(('A와 B의 온도는 같다.', True, '열전도 피스톤을 통해 열평형에 도달했으므로 온도가 같다.', 'T'))
    out.append(('A의 온도가 B의 온도보다 높다.', False, '열평형 상태이므로 두 기체의 온도는 같다.', 'T'))
    out.append(('기체 분자 1개의 평균 운동 에너지는 A와 B가 같다.', True, '평균 운동 에너지는 절대 온도에 비례하는데 온도가 같다.', 'KE'))
    out.append(('기체 분자 1개의 평균 운동 에너지는 분자 수가 많은 쪽이 더 크다.', False, '분자 1개의 평균 운동 에너지는 온도에만 비례하며 분자 수와 무관하다. 두 기체의 온도가 같으므로 같다.', 'KE'))
    out.append(('A와 B의 내부 에너지의 비는 분자 수의 비와 같다(U<sub>A</sub> : U<sub>B</sub> = %d : %d).' % (nA, nB), True, '내부 에너지 U ∝ NT 이고 온도가 같으므로 분자 수의 비 %d : %d 와 같다.' % (nA, nB), 'U'))
    out.append(('A와 B의 내부 에너지는 같다.', nA == nB, '내부 에너지 U ∝ NT 이고 온도가 같으므로 U<sub>A</sub> : U<sub>B</sub> = %d : %d 이다.' % (nA, nB) + (' 같다.' if nA == nB else ' 같지 않다.'), 'U'))
    out.append(('부피는 분자 수가 많은 쪽 기체가 더 크다.', True, 'PV = NkT 에서 P, T 가 같으므로 V ∝ N 이다. 분자 수가 많은 %s의 부피가 더 크다.' % big, 'V'))
    out.append(('부피는 분자 수가 많은 쪽 기체가 더 작다.', False, 'P, T 가 같으면 V ∝ N 이므로 분자 수가 많은 쪽의 부피가 더 크다.', 'V'))
    out.append(('단위 부피당 분자 수는 A와 B가 같다.', True, 'N/V = P/kT 이고 P, T 가 같으므로 단위 부피당 분자 수가 같다.', 'rho'))
    out.append(('단위 부피당 분자 수는 분자 수가 많은 쪽이 더 많다.', False, 'N/V = P/kT 로 P, T 가 같으면 N/V 도 같다.', 'rho'))
    out.append(('A와 B의 부피의 비는 %d : %d 이다.' % (nA, nB), True, 'V ∝ N 이므로 V<sub>A</sub> : V<sub>B</sub> = %d : %d 이다.' % (nA, nB), 'Vr'))
    out.append(('A와 B의 부피의 비는 %d : %d 이다.' % (nB, nA), nA == nB, 'V ∝ N 이므로 V<sub>A</sub> : V<sub>B</sub> = %d : %d 이다.' % (nA, nB), 'Vr'))
    return out


def _release_stmts(r, nA, nB, TA, TB, VA, VB):
    """고정 핀 제거 직후 (열전도 피스톤, 처음 온도·부피가 다름)."""
    out = []
    PA, PB = Fraction(nA * TA, VA), Fraction(nB * TB, VB)
    Tf = Fraction(nA * TA + nB * TB, nA + nB)
    VAf = Fraction(VA + VB) * nA / (nA + nB)
    hot = 'A' if TA > TB else 'B'
    cold = 'B' if hot == 'A' else 'A'
    right = PA > PB
    out.append(('핀을 제거한 직후 피스톤은 %s 쪽으로 이동한다.' % ('B' if right else 'A'), True,
                '처음 압력은 P<sub>A</sub> : P<sub>B</sub> = %s : %s 이므로 압력이 큰 %s의 기체가 피스톤을 밀어 %s 쪽으로 이동한다.' % (fr_str(PA), fr_str(PB), 'A' if right else 'B', 'B' if right else 'A'), 'move'))
    out.append(('핀을 제거한 직후 피스톤은 %s 쪽으로 이동한다.' % ('A' if right else 'B'), False,
                '압력이 큰 쪽 기체가 피스톤을 밀어 압력이 작은 쪽으로 이동한다. 처음 압력은 P<sub>A</sub> : P<sub>B</sub> = %s : %s 이다.' % (fr_str(PA), fr_str(PB)), 'move'))
    out.append(('열은 %s에서 %s로 이동한다.' % (hot, cold), True, '열은 온도가 높은 %s(%d K)에서 낮은 %s(%d K)로 이동한다.' % (hot, max(TA, TB), cold, min(TA, TB)), 'heat'))
    out.append(('열은 %s에서 %s로 이동한다.' % (cold, hot), False, '열은 온도가 높은 쪽에서 낮은 쪽으로 이동한다. 높은 쪽은 %s이다.' % hot, 'heat'))
    out.append(('충분한 시간이 지난 뒤 A와 B의 온도는 같다.', True, '열전도 피스톤을 통해 열평형에 도달하므로 온도가 같아진다.', 'Tf'))
    out.append(('충분한 시간이 지난 뒤 A와 B의 압력은 같다.', True, '피스톤이 정지하려면 힘이 평형이어야 하므로 압력이 같다.', 'Pf'))
    out.append(('충분한 시간이 지난 뒤 기체 전체의 내부 에너지는 처음보다 증가한다.', False, '실린더가 단열이고 외부에 일을 하지 않으므로 전체 내부 에너지는 일정하다.', 'Utot'))
    out.append(('충분한 시간이 지난 뒤 기체 전체의 내부 에너지는 처음과 같다.', True, '단열 실린더 안에서 외부와 열·일을 주고받지 않으므로 A와 B의 내부 에너지의 합은 일정하다.', 'Utot'))
    out.append(('충분한 시간이 지난 뒤 나중 온도는 %s의 처음 온도와 %s의 처음 온도 사이의 값이다.' % ('A', 'B'), True, '나중 온도 %s K 는 처음 온도 %d K 와 %d K 사이이다.' % (fr_str(Tf), TA, TB), 'Tmid'))
    out.append(('충분한 시간이 지난 뒤 A의 부피는 %s이다.' % ('처음보다 크다' if VAf > VA else '처음보다 작다'), True, '나중 부피 V<sub>A</sub>′ = (V<sub>A</sub>+V<sub>B</sub>) × N<sub>A</sub>/(N<sub>A</sub>+N<sub>B</sub>) = %s 이고 처음 %d 이다.' % (fr_str(VAf), VA), 'VAf'))
    out.append(('충분한 시간이 지난 뒤 A의 부피는 %s이다.' % ('처음보다 작다' if VAf > VA else '처음보다 크다'), False, '나중 부피 V<sub>A</sub>′ = %s 이고 처음 %d 이므로 반대이다.' % (fr_str(VAf), VA), 'VAf'))
    return out


@T('ph115')
def g115(r, k):
    nA, nB = r.choice(NRAT)
    form = r.choice(['eq', 'eq', 'rel', 'rel', 'ins', 'bogi', 'bogi', 'bogi'])
    nmA, nmB = _nn(nA), _nn(nB)
    q = Fraction(nB, nA)
    if form == 'eq':
        ask = r.choice(['V', 'U', 'P', 'T', 'KE', 'rho', 'Vnum'])
        Vt = r.choice([30, 60, 90, 120, 150])
        if ask == 'Vnum' and Vt % (nA + nB): return None
        vA = Fraction(nA, nA + nB)
        fig = piston_fig(nA * 2, nB * 2, nA, nB, nmA=nmA, nmB=nmB, conduct=True) if nA + nB <= 6 else piston_fig(nA, nB, nA, nB, nmA=nmA, nmB=nmB)
        base = '그림은 단열된 실린더가 열전도가 잘 되는 움직이는 피스톤으로 나뉘어 있는 것을 나타낸 것이다. 기체 A, B는 같은 종류의 이상 기체이고 분자 수는 각각 %s, %s이다. 피스톤이 정지해 있고 열평형 상태이다. ' % (nmA, nmB)
        if ask == 'V':
            right, ws = '%d : %d' % (nA, nB), ['%d : %d' % (nB, nA), '1 : 1', '%d : %d' % (nA * nA, nB * nB), '%d : %d' % (nB * nB, nA * nA), '%d : %d' % (nA + 1, nB), '%d : %d' % (nA, nB + 1)]
            q_ = '기체의 부피의 비 V<sub>A</sub> : V<sub>B</sub> 는?'
            st = ['피스톤이 정지하므로 P<sub>A</sub> = P<sub>B</sub>, 열평형이므로 T<sub>A</sub> = T<sub>B</sub> 이다.', 'PV = NkT 에서 V ∝ N 이므로 V<sub>A</sub> : V<sub>B</sub> = %d : %d' % (nA, nB)]
            core = '압력과 온도가 같은 같은 종류의 기체는 부피가 분자 수에 비례한다.'
        elif ask == 'U':
            right, ws = '%d : %d' % (nA, nB), ['%d : %d' % (nB, nA), '1 : 1', '%d : %d' % (nA * nA, nB * nB), '%d : %d' % (nA + nB, nB), '%d : %d' % (nA, nA + nB)]
            q_ = '내부 에너지의 비 U<sub>A</sub> : U<sub>B</sub> 는?'
            st = ['열평형이므로 T<sub>A</sub> = T<sub>B</sub> 이고, 이상 기체의 내부 에너지는 U ∝ NT 이다.', 'U<sub>A</sub> : U<sub>B</sub> = N<sub>A</sub> : N<sub>B</sub> = %d : %d' % (nA, nB)]
            core = '이상 기체의 내부 에너지는 분자 수와 절대 온도에 비례한다.'
        elif ask == 'P':
            right, ws = '1 : 1', ['%d : %d' % (nA, nB), '%d : %d' % (nB, nA), '%d : %d' % (nA * nA, nB * nB), '%d : %d' % (nA + 1, nB), '%d : %d' % (nA, nB + 1)]
            q_ = '압력의 비 P<sub>A</sub> : P<sub>B</sub> 는?'
            st = ['피스톤이 정지해 있으므로 피스톤이 받는 힘이 평형이다. 단면적이 같으므로 P<sub>A</sub> = P<sub>B</sub>', 'P<sub>A</sub> : P<sub>B</sub> = 1 : 1']
            core = '정지한 피스톤의 양쪽 기체 압력은 같다.'
        elif ask == 'T':
            right, ws = '1 : 1', ['%d : %d' % (nA, nB), '%d : %d' % (nB, nA), '%d : %d' % (nA * nA, nB * nB), '%d : %d' % (nA + 1, nB), '%d : %d' % (nA, nB + 1)]
            q_ = '절대 온도의 비 T<sub>A</sub> : T<sub>B</sub> 는?'
            st = ['열전도 피스톤으로 열이 이동하여 열평형에 도달했으므로 온도가 같다.', 'T<sub>A</sub> : T<sub>B</sub> = 1 : 1']
            core = '열평형 상태에서는 온도가 같다.'
        elif ask == 'KE':
            right, ws = '1 : 1', ['%d : %d' % (nA, nB), '%d : %d' % (nB, nA), '%d : %d' % (nA * nA, nB * nB), '%d : %d' % (nA + 1, nB), '%d : %d' % (nA, nB + 1)]
            q_ = '기체 분자 1개의 평균 운동 에너지의 비 A : B 는?'
            st = ['분자 1개의 평균 운동 에너지는 절대 온도에만 비례한다(분자 수와 무관).', '열평형이므로 T<sub>A</sub> = T<sub>B</sub> 이다. 따라서 1 : 1']
            core = '기체 분자 1개의 평균 운동 에너지는 절대 온도에 비례한다.'
        elif ask == 'rho':
            right, ws = '1 : 1', ['%d : %d' % (nA, nB), '%d : %d' % (nB, nA), '%d : %d' % (nA * nA, nB * nB), '%d : %d' % (nA + 1, nB), '%d : %d' % (nA, nB + 1)]
            q_ = '단위 부피당 분자 수의 비 A : B 는?'
            st = ['N/V = P/(kT) 이고 P, T 가 같다.', '따라서 단위 부피당 분자 수의 비는 1 : 1']
            core = '압력과 온도가 같으면 단위 부피당 분자 수가 같다.'
        else:
            tot = Vt
            vAn = Fraction(Vt * nA, nA + nB)
            right = fr_str(vAn) + ' cm³'
            ws = [fr_str(Fraction(Vt * nB, nA + nB)) + ' cm³', fr_str(Fraction(Vt, 2)) + ' cm³', fr_str(Fraction(Vt, nA)) + ' cm³', fr_str(Fraction(Vt, nB)) + ' cm³', fr_str(vAn + 10) + ' cm³', fr_str(Fraction(Vt * nA, nB)) + ' cm³']
            q_ = '두 기체의 부피의 합이 %d cm³ 일 때, A의 부피는?' % Vt
            st = ['V<sub>A</sub> : V<sub>B</sub> = N<sub>A</sub> : N<sub>B</sub> = %d : %d (P, T 같음)' % (nA, nB), 'V<sub>A</sub> = %d × %d/%d = %s cm³' % (Vt, nA, nA + nB, fr_str(vAn))]
            core = '압력과 온도가 같은 기체의 부피는 분자 수에 비례한다.'
        body = P(base + q_) + FIG(fig, '78%')
        return mco(body, right, ws, steps=st, core=core, point='피스톤의 힘의 평형(압력 같음)과 열평형(온도 같음)을 이용한다.', lv='하' if ask in ('P', 'T', 'KE', 'rho') else '중', fam='a', r=r,
                   sort='num' if ask == 'Vnum' else 'shuf')
    if form == 'rel':
        TA, TB = r.choice([100, 200, 300, 400, 500, 600]), r.choice([100, 200, 300, 400, 500, 600])
        if TA == TB or (nA * TA + nB * TB) % (nA + nB): return None
        VA, VB = r.choice([1, 2, 3, 4, 5, 6]), r.choice([1, 2, 3, 4, 5, 6])
        PA, PB = Fraction(nA * TA, VA), Fraction(nB * TB, VB)
        Tf = Fraction(nA * TA + nB * TB, nA + nB)
        VAf = Fraction((VA + VB) * nA, nA + nB)
        if PA == PB or VAf == VA: return None
        ask = r.choice(['Tf', 'VAf', 'dir'])
        fig = piston_fig(nA * 2 if nA + nB <= 6 else nA, nB * 2 if nA + nB <= 6 else nB, VA, VB, tA='%d K, %d L' % (TA, VA), tB='%d K, %d L' % (TB, VB), fixed=True, nmA=nmA, nmB=nmB)
        base = '그림은 단열된 실린더 안의 같은 종류의 이상 기체 A(분자 수 %s)와 B(분자 수 %s)가 열전도 피스톤으로 나뉘어 고정 핀으로 고정되어 있는 것을 나타낸 것이다. 고정 핀을 제거하여 충분한 시간이 지난 뒤 두 기체는 열평형 상태가 되어 피스톤이 정지하였다. ' % (nmA, nmB)
        st0 = '처음 온도·부피 : A %d K, %d L / B %d K, %d L' % (TA, VA, TB, VB)
        if ask == 'Tf':
            right = num(float(Tf)) + ' K'
            ws = [num((TA + TB) / 2) + ' K', num(TA) + ' K', num(TB) + ' K', num(float(Fraction(nB * TA + nA * TB, nA + nB))) + ' K', num(TA + TB) + ' K', num(abs(TA - TB)) + ' K']
            body = P(base + '나중 두 기체의 온도는? (단, 외부와의 열 출입은 없고, 피스톤의 열용량은 무시한다.)') + FIG(fig, '78%')
            steps = [st0, '단열 실린더이므로 전체 내부 에너지가 일정하다 : N<sub>A</sub>T<sub>A</sub> + N<sub>B</sub>T<sub>B</sub> = (N<sub>A</sub> + N<sub>B</sub>)T', '(%d × %d + %d × %d) = %d T 에서 T = %s K' % (nA, TA, nB, TB, nA + nB, fr_str(Tf))]
            return mco(body, right, ws, steps=steps, lv='중', fam='b', r=r, sort='num', core='단열된 계에서 열평형이 될 때 내부 에너지의 합(∝ΣNT)이 보존된다.', point='U ∝ NT 의 합이 일정함을 이용한다.')
        if ask == 'VAf':
            right = fr_str(VAf) + ' L'
            ws = [fr_str(VA) + ' L', fr_str(Fraction(VA + VB, 2)) + ' L', fr_str(Fraction((VA + VB) * nB, nA + nB)) + ' L', fr_str(VB) + ' L', fr_str(VAf + 1) + ' L', fr_str(VA + VB) + ' L']
            body = P(base + '나중 A의 부피는? (단, 외부와의 열 출입은 없다.)') + FIG(fig, '78%')
            steps = [st0, '나중에는 압력과 온도가 같으므로 V ∝ N 이다 : V<sub>A</sub>′ : V<sub>B</sub>′ = %d : %d' % (nA, nB),
                     '전체 부피 %d + %d = %d L 이므로 V<sub>A</sub>′ = %d × %d/%d = %s L' % (VA, VB, VA + VB, VA + VB, nA, nA + nB, fr_str(VAf))]
            return mco(body, right, ws, steps=steps, lv='중', fam='b', r=r, core='열평형·힘의 평형 후에는 P, T 가 같아 부피가 분자 수에 비례한다.', point='전체 부피를 분자 수의 비로 나눈다.')
        mv = 'B 쪽(오른쪽)' if PA > PB else 'A 쪽(왼쪽)'
        hv = 'A에서 B로' if TA > TB else 'B에서 A로'
        right = '피스톤 : %s, 열 : %s' % (mv, hv)
        ws = ['피스톤 : %s, 열 : %s' % (mv2, hv2) for mv2 in ('B 쪽(오른쪽)', 'A 쪽(왼쪽)') for hv2 in ('A에서 B로', 'B에서 A로')] + ['피스톤 : 움직이지 않음, 열 : 이동하지 않음']
        body = P(base.split(' 고정 핀을 제거하여')[0] + ' 핀을 제거한 직후 피스톤이 이동하는 방향과 열이 이동하는 방향을 옳게 짝지은 것은? (그림에서 왼쪽이 A이다.)') + FIG(fig, '78%')
        steps = [st0, '압력 P ∝ NT/V : P<sub>A</sub> ∝ %d×%d/%d = %s, P<sub>B</sub> ∝ %d×%d/%d = %s' % (nA, TA, VA, fr_str(PA), nB, TB, VB, fr_str(PB)),
                 '압력이 큰 쪽이 피스톤을 밀어 %s으로 이동하고, 열은 온도가 높은 쪽(%s)에서 낮은 쪽으로 이동한다.' % (mv, 'A' if TA > TB else 'B')]
        return mco(body, right, ws, steps=steps, lv='상', fam='b', r=r, core='압력이 큰 쪽이 피스톤을 밀고, 열은 고온에서 저온으로 이동한다.', point='처음 압력과 온도를 각각 비교한다.')
    if form == 'ins':
        TA, TB = r.choice([100, 200, 300, 400, 600]), r.choice([100, 200, 300, 400, 600])
        if TA == TB: return None
        wA, wB = nA * TA, nB * TB
        g = math.gcd(wA, wB)
        Vt = r.choice([20, 24, 30, 36, 40, 48, 60])
        ask = r.choice(['V', 'U', 'KE', 'Vn'])
        vAn = Fraction(Vt * wA, wA + wB)
        if ask == 'Vn' and vAn.denominator != 1: return None
        fig = piston_fig(nA * 2 if nA + nB <= 6 else nA, nB * 2 if nA + nB <= 6 else nB, wA, wB, tA='%d K' % TA, tB='%d K' % TB, conduct=False, nmA=nmA, nmB=nmB)
        base = '그림은 단열된 실린더가 움직이는 단열 피스톤으로 나뉘어 있는 것을 나타낸 것이다. 같은 종류의 이상 기체 A(분자 수 %s, 온도 %d K)와 B(분자 수 %s, 온도 %d K)가 있고, 피스톤은 정지해 있다. ' % (nmA, TA, nmB, TB)
        if ask == 'V':
            right = '%d : %d' % (wA // g, wB // g)
            ws = ['%d : %d' % (nA, nB), '%d : %d' % (TA // math.gcd(TA, TB), TB // math.gcd(TA, TB)), '%d : %d' % (wB // g, wA // g), '1 : 1', '%d : %d' % (nB * TA // math.gcd(nB * TA, nA * TB), nA * TB // math.gcd(nB * TA, nA * TB))]
            body = P(base + '부피의 비 V<sub>A</sub> : V<sub>B</sub> 는?') + FIG(fig, '78%')
            steps = ['피스톤이 정지하므로 P<sub>A</sub> = P<sub>B</sub> = P 이다.', 'V = NkT/P 이므로 V<sub>A</sub> : V<sub>B</sub> = N<sub>A</sub>T<sub>A</sub> : N<sub>B</sub>T<sub>B</sub> = %d×%d : %d×%d = %s' % (nA, TA, nB, TB, right)]
            return mco(body, right, ws, steps=steps, lv='중', fam='c', r=r, core='압력이 같을 때 이상 기체의 부피는 NT 에 비례한다.', point='단열 피스톤이면 온도가 달라도 압력은 같다.')
        if ask == 'U':
            right = '%d : %d' % (wA // g, wB // g)
            ws = ['%d : %d' % (nA, nB), '%d : %d' % (TA // math.gcd(TA, TB), TB // math.gcd(TA, TB)), '%d : %d' % (wB // g, wA // g), '1 : 1', '%d : %d' % (nB, nA)]
            body = P(base + '내부 에너지의 비 U<sub>A</sub> : U<sub>B</sub> 는?') + FIG(fig, '78%')
            steps = ['내부 에너지 U ∝ NT 이므로 U<sub>A</sub> : U<sub>B</sub> = %d×%d : %d×%d' % (nA, TA, nB, TB), '= %s' % right]
            return mco(body, right, ws, steps=steps, lv='하', fam='c', r=r, core='이상 기체의 내부 에너지는 NT 에 비례한다.', point='분자 수와 온도를 곱해 비교한다.')
        if ask == 'KE':
            tg = math.gcd(TA, TB)
            right = '%d : %d' % (TA // tg, TB // tg)
            ws = ['%d : %d' % (TB // tg, TA // tg), '%d : %d' % (nA, nB), '1 : 1', '%d : %d' % (wA // g, wB // g), '%d : %d' % (nB, nA)]
            body = P(base + '기체 분자 1개의 평균 운동 에너지의 비 A : B 는?') + FIG(fig, '78%')
            steps = ['분자 1개의 평균 운동 에너지는 절대 온도에 비례한다.', 'A : B = T<sub>A</sub> : T<sub>B</sub> = %d : %d = %s' % (TA, TB, right)]
            return mco(body, right, ws, steps=steps, lv='하', fam='c', r=r, core='분자 1개의 평균 운동 에너지는 절대 온도에만 비례한다.', point='분자 수가 달라도 평균 운동 에너지는 온도로 비교한다.')
        right = fr_str(vAn) + ' L'
        ws = [fr_str(Fraction(Vt * wB, wA + wB)) + ' L', fr_str(Fraction(Vt * nA, nA + nB)) + ' L', fr_str(Fraction(Vt, 2)) + ' L', fr_str(Fraction(Vt * TA, TA + TB)) + ' L', fr_str(Fraction(Vt * nB, nA + nB)) + ' L']
        body = P(base + '두 기체의 부피의 합이 %d L 일 때 A의 부피는?' % Vt) + FIG(fig, '78%')
        steps = ['P 가 같으므로 V<sub>A</sub> : V<sub>B</sub> = N<sub>A</sub>T<sub>A</sub> : N<sub>B</sub>T<sub>B</sub> = %d : %d' % (wA, wB), 'V<sub>A</sub> = %d × %d/%d = %s L' % (Vt, wA, wA + wB, fr_str(vAn))]
        return mco(body, right, ws, steps=steps, lv='중', fam='c', r=r, sort='num', core='압력이 같을 때 부피는 NT 에 비례한다.', point='NT 의 비로 전체 부피를 나눈다.')
    # bogi
    setup = r.choice(['eq', 'eq', 'rel'])
    if setup == 'eq':
        fig = piston_fig(nA * 2 if nA + nB <= 6 else nA, nB * 2 if nA + nB <= 6 else nB, nA, nB, nmA=nmA, nmB=nmB)
        bank = _eq_stmts(r, 'A', 'B', nA, nB)
        sel = pick_stmts(r, bank)
        if not sel: return None
        intro = '그림은 단열된 실린더가 열전도가 잘 되는 움직이는 피스톤으로 나뉘어 있는 것을 나타낸 것이다. 같은 종류의 이상 기체 A, B의 분자 수는 각각 %s, %s이고, 피스톤은 정지해 있으며 두 기체는 열평형 상태이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?' % (nmA, nmB)
        return bogi(intro, sel, pre=FIG(fig, '78%'), ask='', r=r, lv='하' if r.random() < 0.5 else '중', fam='d', core='정지한 피스톤은 양쪽 압력이 같고, 열평형이면 온도가 같다. 이때 V ∝ N, U ∝ NT.', point='압력·온도가 같은 두 기체의 부피, 내부 에너지, 평균 운동 에너지를 비교한다.')
    TA, TB = r.choice([100, 200, 300, 400, 500, 600]), r.choice([100, 200, 300, 400, 500, 600])
    if TA == TB or (nA * TA + nB * TB) % (nA + nB): return None
    VA, VB = r.choice([1, 2, 3, 4, 5, 6]), r.choice([1, 2, 3, 4, 5, 6])
    if Fraction(nA * TA, VA) == Fraction(nB * TB, VB) or Fraction((VA + VB) * nA, nA + nB) == VA: return None
    fig = piston_fig(nA * 2 if nA + nB <= 6 else nA, nB * 2 if nA + nB <= 6 else nB, VA, VB, tA='%d K, %d L' % (TA, VA), tB='%d K, %d L' % (TB, VB), fixed=True, nmA=nmA, nmB=nmB)
    bank = _release_stmts(r, nA, nB, TA, TB, VA, VB)
    sel = pick_stmts(r, bank)
    if not sel: return None
    intro = '그림은 단열된 실린더 안의 같은 종류의 이상 기체 A(분자 수 %s), B(분자 수 %s)가 열전도 피스톤으로 나뉘어 고정 핀으로 고정되어 있는 것을 나타낸 것이다. 고정 핀을 제거하였더니 피스톤이 움직이다가 충분한 시간이 지난 뒤 정지하였다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 그림에서 왼쪽이 A이다.)' % (nmA, nmB)
    return bogi(intro, sel, pre=FIG(fig, '78%'), ask='', r=r, lv='상' if r.random() < 0.5 else '중', fam='e', core='고정 핀 제거 후 압력이 큰 쪽이 피스톤을 밀고, 열은 고온에서 저온으로 이동하며, 단열 실린더 안 전체 내부 에너지는 보존된다.', point='처음 압력과 온도를 비교하고 평형 상태의 성질을 적용한다.')


# ============================================================ ph116 열량·압력·부피의 단위 변환
KCAL = 4200


def _jf(x):
    """J 값 문자열(정수)."""
    return '%d J' % round(x)


def _pv_work_fig(P1, P2, V1, V2, unit_p='기압', unit_v='L'):
    """P-V 그래프(직선 경로). 점 (V1,P1)→(V2,P2)."""
    pm, vm = max(P1, P2), max(V1, V2)
    p = Plot(300, 210, vm * 1.25, pm * 1.3, ml=52, mr=16, mt=26, mb=34)
    xt = sorted({0, V1, V2}); yt = sorted({0, P1, P2})
    p.axes('', '', xticks=xt, yticks=yt)
    p.text(288, 205, 'V (%s)' % unit_v, 12.5, 'end', True, GR)
    p.text(60, 14, 'P (%s)' % unit_p, 12.5, 'start', True, GR)
    p.fill_under([(V1, P1), (V2, P2)], '#d5e6f8', 0)
    p.dash_to_axes(V1, P1); p.dash_to_axes(V2, P2)
    p.pl([(V1, P1), (V2, P2)], BL, 2.8)
    m1, m2 = _along([(p.px(V1), p.py(P1)), (p.px(V2), p.py(P2))], 0.46), _along([(p.px(V1), p.py(P1)), (p.px(V2), p.py(P2))], 0.56)
    p._head(m1[0], m1[1], m2[0], m2[1], BL, 2.4, 10)
    for (v, pp, nm) in ((V1, P1, 'A'), (V2, P2, 'B')):
        p.circ(p.px(v), p.py(pp), 3.6, INK, INK, 1)
        p.text(p.px(v) + (-11 if nm == 'A' else 11), p.py(pp) - 8, nm, 14, 'middle', True, INK, True)
    return p.svg()


@T('ph116')
def g116(r, k):
    form = r.choice(['W', 'W', 'WV', 'QU', 'QU', 'dV', 'kcal', 'fig', 'comp', 'W2'])
    Pn = r.choice([1, 2, 3, 4, 5, 6, 8])          # ×10⁵ Pa
    if form == 'W':
        V1 = r.choice([5, 10, 15, 20, 25, 30, 40]); dV = r.choice([2, 4, 5, 6, 8, 10, 12, 15, 20])
        V2 = V1 + dV
        W = Pn * 1e5 * dV * 1e-3
        useatm = r.random() < 0.5
        pstr = ('%d기압' % Pn) if useatm else ('%d × 10⁵ Pa' % Pn)
        body = P('일정한 압력 %s 에서 이상 기체가 %d L 에서 %d L 로 팽창하였다. 이 과정에서 기체가 외부에 한 일은? (단, 1기압 = 1.0 × 10⁵ Pa, 1 L = 1.0 × 10⁻³ m³ 이다.)' % (pstr, V1, V2))
        right = _jf(W)
        wr = [_jf(W * 1000), _jf(W / 1000), _jf(W / 10), _jf(W * 10), _jf(Pn * 1e5 * V2 * 1e-3), _jf(Pn * 1e5 * V1 * 1e-3)]
        steps = ['압력 P = %d × 10⁵ Pa, 부피 변화 ΔV = %d - %d = %d L = %d × 10⁻³ m³' % (Pn, V2, V1, dV, dV), 'W = PΔV = %d × 10⁵ × %d × 10⁻³ = %d J' % (Pn, dV, W)]
        assert abs(W - Pn * dV * 100) < 1e-6
        return mco(body, right, wr, steps=steps, lv='하', fam='a', r=r, sort='num', core='등압 과정에서 기체가 한 일은 W = PΔV 이다. 1기압·1 L = 100 J.', point='L 를 m³ 로 바꾸어 압력과 곱한다.')
    if form == 'W2':
        # 압축: 외부가 한 일
        V1 = r.choice([20, 30, 40, 50, 60]); dV = r.choice([4, 5, 8, 10, 12, 15])
        W = Pn * dV * 100
        body = P('피스톤이 달린 실린더 속 이상 기체에 %d × 10⁵ Pa 의 일정한 압력을 유지하며 부피를 %d L 에서 %d L 로 줄였다. 이 과정에서 외부가 기체에 한 일은? (단, 1 L = 1.0 × 10⁻³ m³ 이다.)' % (Pn, V1, V1 - dV))
        right = _jf(W)
        wr = [_jf(-W), _jf(W * 1000), _jf(W / 1000), _jf(Pn * 1e5 * V1 * 1e-3), _jf(W * 10)]
        steps = ['ΔV = %d - %d = -%d L = -%d × 10⁻³ m³ (기체가 한 일 W = PΔV = %d × 10⁵ × (-%d × 10⁻³) = -%d J)' % (V1 - dV, V1, dV, dV, Pn, dV, W),
                 '외부가 기체에 한 일은 기체가 한 일의 부호를 바꾼 값이므로 %d J 이다.' % W]
        return mco(body, right, wr, steps=steps, lv='중', fam='a', r=r, sort='num', core='압축될 때 기체가 한 일은 음(−)이며, 외부가 기체에 한 일은 그 크기와 같다.', point='부호와 단위(L→m³)에 주의한다.')
    if form == 'WV':
        dVm = r.choice([0.002, 0.004, 0.005, 0.01, 0.02, 0.03, 0.05])
        W = Pn * 1e5 * dVm
        body = P('압력이 %d × 10⁵ Pa 로 일정한 기체의 부피가 %s m³ 만큼 증가하였다. 기체가 한 일은 몇 kJ 인가?' % (Pn, num(dVm, 3)))
        right = num(W / 1000, 3) + ' kJ'
        wr = [num(W, 3) + ' kJ', num(W / 1e6, 4) + ' kJ', num(W * 1000 / 1000 * 10, 3) + ' kJ', num(W / 100, 3) + ' kJ', num(W / 10000, 4) + ' kJ']
        steps = ['W = PΔV = %d × 10⁵ Pa × %s m³ = %s J' % (Pn, num(dVm, 3), num(W, 3)), '1 kJ = 1000 J 이므로 %s kJ' % num(W / 1000, 3)]
        return mco(body, right, wr, steps=steps, lv='중', fam='a', r=r, core='W = PΔV 에서 Pa·m³ = J 이다.', point='J 를 kJ 로 환산한다.')
    if form == 'QU':
        Qk = r.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
        V1 = r.choice([10, 20, 30]); dV = r.choice([5, 10, 15, 20])
        W = Pn * dV * 100
        Qj = Qk * KCAL
        if Qj <= W: return None
        dU = Qj - W
        body = P('일정한 압력 %d × 10⁵ Pa 인 기체에 열량 %d kcal 를 가했더니 기체의 부피가 %d L 에서 %d L 로 팽창하였다. 기체의 내부 에너지 증가량은? (단, 1 kcal = 4200 J, 1 L = 1.0 × 10⁻³ m³ 이다.)' % (Pn, Qk, V1, V1 + dV))
        right = _jf(dU)
        wr = [_jf(Qj + W), _jf(Qk - W), _jf(Qk * 4.2 - W), _jf(W), _jf(Qj), _jf(Qk * 4200 - W * 1000)]
        steps = ['Q = %d × 4200 = %d J, W = PΔV = %d × 10⁵ × %d × 10⁻³ = %d J' % (Qk, Qj, Pn, dV, W), '제1법칙 Q = ΔU + W 에서 ΔU = Q - W = %d - %d = %d J' % (Qj, W, dU)]
        return mco(body, right, wr, steps=steps, lv='중' if W < Qj / 3 else '상', fam='b', r=r, sort='num', core='열역학 제1법칙 Q = ΔU + W. 열량(kcal)을 J 로 바꾼 뒤 일(J)과 같은 단위로 계산한다.', point='kcal→J, L→m³ 단위를 맞추어 제1법칙을 적용한다.')
    if form == 'dV':
        Qk = r.choice([2, 3, 4, 5, 6, 8, 10])
        Qj = Qk * KCAL
        dUk = r.choice([0.5, 1, 1.5, 2, 3, 4, 5])
        if dUk >= Qk: return None
        dUj = dUk * KCAL
        W = Qj - dUj
        dV = W / (Pn * 100)
        if abs(dV - round(dV)) > 1e-9 or dV < 1 or dV > 200: return None
        dV = int(round(dV))
        body = P('압력이 %d × 10⁵ Pa 로 일정한 상태에서 이상 기체가 %d kcal 의 열을 흡수하여 내부 에너지가 %s kcal 증가하였다. 기체의 부피 증가량은? (단, 1 kcal = 4200 J, 1 L = 1.0 × 10⁻³ m³ 이다.)' % (Pn, Qk, num(dUk)))
        right = '%d L' % dV
        wr = ['%d L' % (dV * 10), '%s L' % num(dV / 10), '%d L' % (dV * 1000), '%s L' % num(Qj / (Pn * 100)), '%s L' % num(dUj / (Pn * 100)), '%d L' % (dV + 5)]
        steps = ['Q = %d × 4200 = %d J, ΔU = %s × 4200 = %d J' % (Qk, Qj, num(dUk), dUj), 'W = Q - ΔU = %d - %d = %d J' % (Qj, dUj, W),
                 'W = PΔV 에서 ΔV = %d / (%d × 10⁵) = %s × 10⁻³ m³ = %d L' % (W, Pn, num(W / Pn / 100), dV)]
        return mco(body, right, wr, steps=steps, lv='상', fam='c', r=r, sort='num', core='Q = ΔU + W, W = PΔV.', point='열량에서 내부 에너지를 뺀 일로 부피 변화를 구한다.')
    if form == 'kcal':
        Wk = r.choice([0.5, 1, 1.5, 2, 3, 4, 5, 6, 10])
        Wj = Wk * KCAL
        body = P('이상 기체가 외부에 %d J 의 일을 하는 동안 내부 에너지는 변하지 않았다. 이 과정에서 기체가 흡수한 열량은 몇 kcal 인가? (단, 1 kcal = 4200 J 이다.)' % Wj)
        right = num(Wk) + ' kcal'
        wr = [num(Wk * 1000) + ' kcal', num(Wk / 4.2) + ' kcal', num(Wk * 4.2) + ' kcal', '0 kcal', num(Wk * 2) + ' kcal', num(Wk / 2) + ' kcal']
        steps = ['내부 에너지 변화가 없으므로 ΔU = 0, Q = W = %d J' % Wj, '%d J ÷ 4200 J/kcal = %s kcal' % (Wj, num(Wk))]
        return mco(body, right, wr, steps=steps, lv='하', fam='d', r=r, core='ΔU = 0 이면 Q = W 이고, 1 kcal = 4200 J 이다.', point='J 를 kcal 로 환산한다.')
    if form == 'fig':
        P1 = r.choice([1, 2, 3, 4]); P2 = P1 if r.random() < 0.5 else r.choice([2, 3, 4, 5, 6])
        V1 = r.choice([1, 2, 3, 5]) * r.choice([1, 2, 5]); V2 = V1 + r.choice([2, 4, 6, 8, 10])
        area = (P1 + P2) / 2.0 * (V2 - V1)
        W = area * 100
        if abs(W - round(W)) > 1e-9: return None
        fig = _pv_work_fig(P1, P2, V1, V2)
        body = P('그림은 일정량의 이상 기체의 상태가 A에서 B로 변할 때 압력 P 와 부피 V 를 나타낸 것이다. A→B 과정에서 기체가 외부에 한 일은? (단, 1기압 = 1.0 × 10⁵ Pa, 1 L = 1.0 × 10⁻³ m³ 이다.)') + FIG(fig, '66%')
        right = _jf(W)
        wr = [_jf(W * 1000), _jf(W / 1000), _jf(W / 10), _jf(W * 10), _jf(P2 * V2 * 100), _jf(P1 * (V2 - V1) * 100 if P1 != P2 else P1 * V2 * 100), _jf(max(P1, P2) * (V2 - V1) * 100 + 100)]
        steps = ['그래프 아래 넓이가 기체가 한 일이다 : (%s + %s)/2 × (%d - %d) = %s 기압·L' % (num(P1), num(P2), V2, V1, num(area)), '1기압·L = 10⁵ Pa × 10⁻³ m³ = 100 J 이므로 W = %s × 100 = %d J' % (num(area), W)]
        return mco(body, right, wr, steps=steps, lv='중', fam='e', r=r, sort='num', core='P-V 그래프 아래 넓이는 기체가 한 일이며 1기압·L = 100 J 이다.', point='그래프 눈금(기압, L)에서 넓이를 구해 J 로 환산한다.')
    # comp: 부호 조합(압축 + 방열)
    Qk = r.choice([2, 3, 5, 10]); V1 = r.choice([20, 30, 40]); dV = r.choice([5, 10])
    W = Pn * dV * 100
    Qj = Qk * KCAL
    dU = -Qj + W
    body = P('압력이 %d × 10⁵ Pa 로 일정한 이상 기체가 %d kcal 의 열을 방출하면서 부피가 %d L 에서 %d L 로 줄어들었다. 이 과정에서 기체의 내부 에너지 변화량 ΔU 는? (단, 1 kcal = 4200 J, 1 L = 1.0 × 10⁻³ m³ 이다.)' % (Pn, Qk, V1, V1 - dV))
    right = sj(dU)
    wr = [sj(-Qj - W), sj(Qj - W), sj(Qj + W), sj(-Qj), sj(-(Qj - W) / 10)]
    steps = ['열 방출이므로 Q = -%d × 4200 = -%d J' % (Qk, Qj), '압축이므로 W = PΔV = %d × 10⁵ × (-%d × 10⁻³) = -%d J' % (Pn, dV, W),
            'ΔU = Q - W = -%d - (-%d) = %s' % (Qj, W, sj(dU))]
    return mco(body, right, wr, steps=steps, lv='상', fam='f', r=r, core='Q = ΔU + W 에서 방출은 Q<0, 압축은 W<0 으로 넣는다.', point='열 방출·압축의 부호와 단위를 모두 맞춘다.')


# ============================================================ 정성적 순환 과정(P-V, 단열 포함)
LDIR = {'P': (1.0, 0.0), 'V': (0.0, 1.0), 'T': (1.0, -1.0), 'A': (1.0, -GAM)}   # (ln V, ln P) 평면에서의 방향


def qual_cycle(r, kinds, vmax=7.0, pmax=9.0):
    """과정 종류(kinds) 순서로 이루어진 단순 폐곡선. 반환 [(P,V)…] 또는 None."""
    n = len(kinds)
    ls = [r.choice([-1, 1]) * r.choice([0.35, 0.5, 0.7, 0.9]) for _ in range(n - 2)]
    d = [LDIR[c] for c in kinds]
    sx = -sum(ls[i] * d[i][0] for i in range(n - 2))
    sy = -sum(ls[i] * d[i][1] for i in range(n - 2))
    (a, b), (c, e) = d[n - 2], d[n - 1]
    det = a * e - b * c
    if abs(det) < 1e-6: return None
    l1 = (sx * e - sy * c) / det
    l2 = (a * sy - b * sx) / det
    ls += [l1, l2]
    if min(abs(x) for x in ls) < 0.25: return None
    pts = [(0.0, 0.0)]
    for i in range(n - 1):
        pts.append((pts[-1][0] + ls[i] * d[i][0], pts[-1][1] + ls[i] * d[i][1]))
    lx = [p[0] for p in pts]; ly = [p[1] for p in pts]
    v0 = r.uniform(1.0, 1.8); p0 = r.uniform(1.0, 1.8)
    sts = [(p0 * math.exp(y - min(ly)), v0 * math.exp(x - min(lx))) for (x, y) in pts]
    if max(s[1] for s in sts) > vmax or max(s[0] for s in sts) > pmax: return None
    if not loop_simple(sts): return None
    # 닫힘 검사
    for i in range(n):
        a_, b_ = sts[i], sts[(i + 1) % n]
        k = kinds[i]
        if k == 'P': assert abs(a_[0] - b_[0]) < 1e-9
        elif k == 'V': assert abs(a_[1] - b_[1]) < 1e-9
        elif k == 'T': assert abs(a_[0] * a_[1] - b_[0] * b_[1]) < 1e-9
        else: assert abs(a_[0] * a_[1] ** GAM - b_[0] * b_[1] ** GAM) < 1e-7
    return sts


def qual_fig(names, sts, kinds, w=270, h=214):
    return loop_fig('PV', names, sts, kinds, numbered=False, w=w, h=h, ext=False)


def sign_table(sts, kinds):
    n = len(sts)
    return [seg_signs(kinds[i], sts[i], sts[(i + 1) % n]) for i in range(n)]   # (dU, W, Q)


PROPS = [
    ('열을 흡수하는', lambda s: s[2] > 0, 'Q > 0'),
    ('열을 방출하는', lambda s: s[2] < 0, 'Q < 0'),
    ('내부 에너지가 증가하는', lambda s: s[0] > 0, 'ΔU > 0 (온도 상승)'),
    ('내부 에너지가 감소하는', lambda s: s[0] < 0, 'ΔU < 0 (온도 하강)'),
    ('기체가 외부에 일을 하는', lambda s: s[1] > 0, 'W > 0 (부피 증가)'),
    ('기체가 외부로부터 일을 받는', lambda s: s[1] < 0, 'W < 0 (부피 감소)'),
    ('열의 출입이 없는', lambda s: s[2] == 0, 'Q = 0'),
    ('기체가 일을 하지도 받지도 않는', lambda s: s[1] == 0, 'W = 0'),
    ('내부 에너지가 변하지 않는', lambda s: s[0] == 0, 'ΔU = 0'),
    ('열을 흡수하면서 내부 에너지가 증가하는', lambda s: s[2] > 0 and s[0] > 0, 'Q > 0 이고 ΔU > 0'),
    ('열을 방출하면서 외부로부터 일을 받는', lambda s: s[2] < 0 and s[1] < 0, 'Q < 0 이고 W < 0'),
    ('외부에 일을 하면서 내부 에너지가 감소하는', lambda s: s[1] > 0 and s[0] < 0, 'W > 0 이고 ΔU < 0'),
    ('흡수한 열이 모두 기체가 하는 일로 쓰이는', lambda s: s[0] == 0 and s[1] > 0, 'ΔU = 0 이고 W > 0'),
    ('받은 일이 모두 내부 에너지로 쓰이는', lambda s: s[2] == 0 and s[1] < 0, 'Q = 0 이고 W < 0'),
]

KSET4 = [''.join(p) for p in itertools.permutations('PVTA')]
KSET3 = [''.join(p) for p in itertools.permutations('PVTA', 3)]


def _sets_str(idx, names, n):
    return ', '.join('%s→%s' % (names[i], names[(i + 1) % n]) for i in idx)


def _kind_text(kind, sg_):
    dU, W, Q = sg_
    up = W > 0
    return {'P': '등압 %s' % ('팽창' if up else '압축'), 'V': '등적 %s' % ('가열' if dU > 0 else '냉각'),
            'T': '등온 %s' % ('팽창' if up else '압축'), 'A': '단열 %s' % ('팽창' if up else '압축')}[kind]


@T('ph117')
def g117(r, k):
    n = r.choice([3, 4, 4, 4])
    kinds = list(r.choice(KSET4 if n == 4 else KSET3))
    sts = qual_cycle(r, kinds)
    if not sts: return None
    names = list(NMS[:n])
    tab = sign_table(sts, kinds)
    fig = FIG(qual_fig(names, sts, kinds), '62%')
    seglab = ['%s→%s' % (names[i], names[(i + 1) % n]) for i in range(n)]
    kd = ' / '.join('%s %s' % (seglab[i], _kind_text(kinds[i], tab[i])) for i in range(n))
    form = r.choice(['set', 'set', 'tri', 'tri', 'bogi', 'bogi', 'cnt', 'cnt'])
    path = '→'.join(names) + '→' + names[0]
    intro = '그림은 일정량의 이상 기체의 상태가 %s를 따라 변할 때 압력 P 와 부피 V 를 나타낸 것이다. 곡선 중 하나는 단열 과정, 하나는 등온 과정이다.' % path if ('A' in kinds and 'T' in kinds) else '그림은 일정량의 이상 기체의 상태가 %s를 따라 변할 때 압력 P 와 부피 V 를 나타낸 것이다.' % path
    if 'A' in kinds and 'T' not in kinds:
        intro = '그림은 일정량의 이상 기체의 상태가 %s를 따라 변할 때 압력 P 와 부피 V 를 나타낸 것이다. 곡선으로 나타낸 과정은 단열 과정이다.' % path
    if 'T' in kinds and 'A' not in kinds:
        intro = '그림은 일정량의 이상 기체의 상태가 %s를 따라 변할 때 압력 P 와 부피 V 를 나타낸 것이다. 곡선으로 나타낸 과정은 등온 과정이다.' % path
    if form == 'set':
        pr = r.choice(PROPS)
        S = [i for i in range(n) if pr[1](tab[i])]
        if not S or len(S) == n: return None
        right = _sets_str(S, names, n)
        cands = []
        for sz in (1, 2, 3):
            for c in itertools.combinations(range(n), sz):
                if list(c) != S: cands.append(_sets_str(c, names, n))
        r.shuffle(cands)
        near = [_sets_str(c, names, n) for c in ([x for x in range(n) if x not in S] ,) if c]
        wrongs = near + cands
        body = P(intro + ' %s 과정만을 있는 대로 고른 것은?' % pr[0]) + fig
        steps = ['과정 : ' + kd + '.', '각 과정의 (ΔU, W, Q) 부호 : ' + ', '.join('%s (%s, %s, %s)' % (seglab[i], sgs(tab[i][0]), sgs(tab[i][1]), sgs(tab[i][2])) for i in range(n)),
                 '%s 조건(%s)을 만족하는 과정은 %s 이다.' % (pr[0], pr[2], right)]
        return mco(body, right, wrongs, steps=steps, lv='중' if len(pr[0]) < 14 else '상', fam='a', r=r,
                   core='팽창이면 W>0, 온도 상승이면 ΔU>0, Q=ΔU+W. 단열이면 Q=0, 등온이면 ΔU=0, 등적이면 W=0.', point='과정별 ΔU·W·Q 부호표를 만들어 조건에 맞는 과정을 찾는다.')
    if form == 'tri':
        i = r.randrange(n)
        dU, W, Q = tab[i]
        f = lambda x: {1: '+', -1: '−', 0: '0'}[x]
        right = '(%s, %s, %s)' % (f(dU), f(W), f(Q))
        wr = ['(%s, %s, %s)' % (f(a), f(b), f(c)) for a in (1, -1, 0) for b in (1, -1, 0) for c in (1, -1, 0) if (a, b, c) != (dU, W, Q)]
        wr.sort(key=lambda x: sum(1 for u, v in zip(x.strip('()').split(', '), right.strip('()').split(', ')) if u != v))
        body = P(intro + ' %s 과정에서 기체의 내부 에너지 변화량 ΔU, 기체가 외부에 한 일 W, 기체가 흡수한 열량 Q 의 부호를 (ΔU, W, Q) 순서로 옳게 나타낸 것은? (기체가 열을 흡수하면 Q > 0, 외부에 일을 하면 W > 0 이다.)' % seglab[i]) + fig
        steps = ['%s 은(는) %s 과정이다.' % (seglab[i], _kind_text(kinds[i], tab[i])), '부피 %s → W %s, 온도 %s → ΔU %s' % ({1: '증가', -1: '감소', 0: '일정'}[W], f(W), {1: '상승', -1: '하강', 0: '일정'}[dU], f(dU)),
                 'Q = ΔU + W %s' % ('= 0 (단열)' if kinds[i] == 'A' else '→ %s' % f(Q)), '따라서 %s' % right]
        return mco(body, right, wr[:8], steps=steps, lv='하' if kinds[i] in 'PV' else ('중' if kinds[i] == 'T' else '상'), fam='b', r=r, core='ΔU ∝ ΔT, W 의 부호는 ΔV 의 부호, Q = ΔU + W.', point='과정의 종류를 알면 ΔU, W, Q 의 부호가 정해진다.')
    if form == 'cnt':
        which = r.choice([0, 1, 2])
        label, fn, why = [('열을 흡수하는', lambda s: s[2] > 0, 'Q > 0'), ('외부에 일을 하는', lambda s: s[1] > 0, 'W > 0'), ('내부 에너지가 증가하는', lambda s: s[0] > 0, 'ΔU > 0')][which]
        cnt = sum(1 for s in tab if fn(s))
        body = P(intro + ' %s 과정은 모두 몇 개인가?' % label) + fig
        ws = [str(x) + '개' for x in range(0, 5) if x != cnt]
        steps = ['각 과정의 (ΔU, W, Q) 부호 : ' + ', '.join('%s (%s, %s, %s)' % (seglab[i], sgs(tab[i][0]), sgs(tab[i][1]), sgs(tab[i][2])) for i in range(n)), '%s 조건(%s)을 만족하는 과정은 %d개이다.' % (label, why, cnt)]
        return mco(body, '%d개' % cnt, ws, steps=steps, lv='하', fam='c', r=r, sort='num', core='각 과정의 ΔU, W, Q 부호를 표로 정리하면 조건에 맞는 과정을 센다.', point='부호표 작성.')
    bank = stmts_cycle(r, names, sts, kinds, 'PV')
    # 단열 관련 문장 추가
    for i in range(n):
        if kinds[i] == 'A':
            out_ = '%s 과정에서 기체와 외부 사이의 열 출입은 없다.' % seglab[i]
            bank.append((out_, True, '단열 과정이므로 Q = 0 이다.', 'adi'))
            up = tab[i][1] > 0
            bank.append(('%s 과정에서 기체의 온도는 %s.' % (seglab[i], '낮아진다' if up else '높아진다'), True, '단열 %s 에서는 Q=0 이므로 ΔU = -W 이다. %s하므로 온도가 %s.' % ('팽창' if up else '압축', '기체가 일을 ' if up else '외부가 일을 ', '낮아진다' if up else '높아진다'), 'adi2'))
            bank.append(('%s 과정에서 기체의 온도는 일정하다.' % seglab[i], False, '단열 과정은 Q = 0 이므로 W 만큼 내부 에너지가 변해 온도가 변한다. 온도가 일정한 것은 등온 과정이다.', 'adi2'))
        if kinds[i] == 'T':
            bank.append(('%s 과정에서 기체가 흡수(방출)한 열은 기체가 한(받은) 일과 같다.' % seglab[i], True, '등온 과정은 ΔU = 0 이므로 Q = W 이다.', 'iso'))
            bank.append(('%s 과정에서 기체의 내부 에너지가 변한다.' % seglab[i], False, '등온 과정은 온도가 일정하므로 ΔU = 0 이다.', 'iso'))
    sel = pick_stmts(r, bank)
    if not sel: return None
    return bogi(intro + ' 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', sel, pre=fig, ask='', r=r, lv='중' if n == 3 else '상', fam='d',
                core='각 과정의 (ΔU, W, Q) 부호: 등압 팽창 (+,+,+), 등적 가열 (+,0,+), 등온 팽창 (0,+,+), 단열 팽창 (−,+,0).', point='과정 종류를 판별하고 부호표로 <보기>를 판단한다.')


# ============================================================ ph118 내부 에너지 변화량과 온도 비교(순환 과정)
def _pairs(names, idx):
    return '와 '.join(names[i] for i in idx) if False else '%s와 %s' % (names[idx[0]], names[idx[1]])


@T('ph118')
def g118(r, k):
    form = r.choice(['eqT', 'eqT', 'ratio', 'ratio', 'dU', 'dU', 'close', 'cmp', 'bogi', 'bogi'])
    n = r.choice([3, 4, 4])
    if form == 'eqT':
        got = pick_cycle(r, n, need=lambda c, s: len({p * v for p, v in c}) == len(c) - 1)
    elif form == 'cmp':
        got = pick_cycle(r, 4, need=lambda c, s: True)
    else:
        got = pick_cycle(r, n)
    if not got: return None
    sts, seq = got
    n = len(sts)
    kinds = list(seq)
    names = list(NMS[:n])
    Ts = [p * v for p, v in sts]
    try:
        fig = FIG(loop_fig('PV', names, sts, kinds, numbered=True), '66%')
    except AssertionError:
        return None
    path = '→'.join(names) + '→' + names[0]
    intro = '그림은 일정량의 이상 기체의 상태가 %s를 따라 변할 때 압력 P 와 부피 V 를 나타낸 것이다.' % path
    tabs = '각 상태의 PV (P₀V₀ 단위) : ' + ', '.join('%s = %d' % (names[i], Ts[i]) for i in range(n)) + '. 절대 온도는 PV 에 비례한다.'
    seg = lambda i: '%s→%s' % (names[i], names[(i + 1) % n])
    dUs = [Fraction(3, 2) * (Ts[(i + 1) % n] - Ts[i]) for i in range(n)]   # P₀V₀ 단위
    assert sum(dUs) == 0
    for i in range(n):
        assert abs(float(dUs[i]) - seg_vals(kinds[i], sts[i], sts[(i + 1) % n])[0]) < 1e-9
    if form == 'eqT':
        pairs = list(itertools.combinations(range(n), 2))
        good = [p for p in pairs if Ts[p[0]] == Ts[p[1]]]
        if len(good) != 1: return None
        g = good[0]
        right = '%s와 %s' % (names[g[0]], names[g[1]])
        wr = ['%s와 %s' % (names[p[0]], names[p[1]]) for p in pairs if p != g]
        if n == 3: wr += ['A, B, C 모두 같다', '온도가 같은 상태는 없다']
        else: wr += ['온도가 같은 상태는 없다', '네 상태의 온도가 모두 같다']
        body = P(intro + ' 기체의 온도가 서로 같은 두 상태는?') + fig
        steps = [tabs, '%s 의 PV 는 %d 로 같다(등온 곡선 위). 다른 상태는 PV 가 모두 다르다.' % (right, Ts[g[0]])]
        return mco(body, right, wr, steps=steps, lv='하', fam='a', r=r, core='이상 기체의 절대 온도는 PV 에 비례하므로 PV 가 같은 상태는 온도가 같다.', point='눈금에서 P×V 값을 구해 비교한다.')
    if form == 'ratio':
        right = ' : '.join(num(0)) if False else ratio_list(Ts)
        tl = ' : '.join('T%s' % names[i] for i in range(n))
        wr = [ratio_list([p for p, v in sts]), ratio_list([v for p, v in sts]), ratio_list([p + v for p, v in sts]), ratio_list(Ts[::-1]), ratio_list([Fraction(p, v) for p, v in sts]), ratio_list([t + 1 for t in Ts]), ratio_list([Ts[(i + 1) % n] for i in range(n)])]
        body = P(intro + ' 상태 %s의 절대 온도의 비 %s 는?' % (', '.join(names), tl.replace('T', 'T')) ) + fig
        steps = [tabs, 'T ∝ PV 이므로 %s = %s' % (tl, ' : '.join(str(t) for t in Ts)), '간단히 하면 %s' % right]
        return mco(body, right, wr, steps=steps, lv='중', fam='b', r=r, core='PV = nRT 이므로 T ∝ PV 이다.', point='각 상태의 P, V 눈금을 곱해 온도 비를 구한다.')
    if form == 'dU':
        u = r.choice([100, 200, 400, 500, 600, 800])
        i = r.randrange(n)
        val = float(dUs[i]) * u
        if abs(val - round(val)) > 1e-9 or val == 0: return None
        right = sj(val)
        wr = [sj(-val), sj(val * 2 / 3), sj(val * 2), sj(float(Ts[(i + 1) % n] - Ts[i]) * u), sj(float(Ts[(i + 1) % n]) * u * 1.5), sj(val + u)]
        body = P(intro + ' P₀V₀ = %d J 이고, 이 기체의 내부 에너지는 U = (3/2)PV 이다. %s 과정에서 기체의 내부 에너지 변화량은?' % (u, seg(i))) + fig
        steps = [tabs, 'ΔU = (3/2)(P<sub>%s</sub>V<sub>%s</sub> - P<sub>%s</sub>V<sub>%s</sub>) = (3/2)(%d - %d) P₀V₀ = %s P₀V₀' % (names[(i + 1) % n], names[(i + 1) % n], names[i], names[i], Ts[(i + 1) % n], Ts[i], fr_str(dUs[i])),
                 '= %s × %d J = %s' % (fr_str(dUs[i]), u, sj(val))]
        return mco(body, right, wr, steps=steps, lv='중', fam='c', r=r, core='단원자 분자 이상 기체의 내부 에너지는 U = (3/2)PV 이므로 ΔU = (3/2)Δ(PV).', point='시작·끝 상태의 PV 로 ΔU 를 구한다.')
    if form == 'close':
        u = r.choice([100, 200, 400, 600])
        vals = [float(d) * u for d in dUs]
        if any(abs(v - round(v)) > 1e-9 for v in vals): return None
        miss = r.randrange(n)
        given = [i for i in range(n) if i != miss]
        ans = vals[miss]
        if abs(ans) < 1e-9: return None
        ph = ', '.join('%s %s' % (seg(i), sj(vals[i])) for i in given)
        right = sj(ans)
        wr = [sj(-ans), sj(sum(vals[i] for i in given)), sj(abs(ans) + u), sj(ans + u), sj(ans / 2), sj(0)]
        body = P(intro + ' 한 순환 동안 과정별 내부 에너지 변화량이 %s 일 때, %s 과정에서 기체의 내부 에너지 변화량은?' % (ph, seg(miss))) + fig
        steps = ['한 순환 후 처음 상태로 돌아오므로 내부 에너지 변화량의 합은 0이다.', '%s = -(%s) = %s' % (seg(miss), ' + '.join('(%s)' % sj(vals[i]) for i in given), sj(ans)),
                 '(검산) (3/2)(PV₍%s₎ - PV₍%s₎) = %s' % (names[(miss + 1) % n], names[miss], sj(float(dUs[miss]) * u))]
        return mco(body, right, wr, steps=steps, lv='중', fam='d', r=r, core='한 순환에서 ΔU = 0 이므로 모든 과정의 ΔU 를 더하면 0이다.', point='순환 후 내부 에너지 변화 0 을 이용한다.')
    if form == 'cmp':
        # A→B 와 C→D 비교(4상태)
        i, j = 0, 2
        di, dj = dUs[i], dUs[j]
        if di == 0 or dj == 0: return None
        right = ratio_list([di, dj]) if (di > 0) == (dj > 0) else ratio_list([abs(di), abs(dj)]).replace(' : ', ' : −')
        if (di > 0) != (dj > 0):
            right = ('' if di > 0 else '−') + ratio_list([abs(di), abs(dj)]).split(' : ')[0] + ' : ' + ('' if dj > 0 else '−') + ratio_list([abs(di), abs(dj)]).split(' : ')[1]
        else:
            a_, b_ = ratio_list([abs(di), abs(dj)]).split(' : ')
            right = ('−' if di < 0 else '') + a_ + ' : ' + ('−' if dj < 0 else '') + b_
        a_, b_ = ratio_list([abs(di), abs(dj)]).split(' : ')
        wr = ['%s : %s' % (a_, b_), '−%s : %s' % (a_, b_), '%s : −%s' % (a_, b_), '−%s : −%s' % (a_, b_), '%s : %s' % (b_, a_), '−%s : %s' % (b_, a_), '%s : −%s' % (b_, a_), '%d : %d' % (abs(Ts[1] - Ts[0]), abs(Ts[3] - Ts[2]))]
        body = P(intro + ' %s 과정과 %s 과정에서 기체의 내부 에너지 변화량의 비 ΔU<sub>%s</sub> : ΔU<sub>%s</sub> 는?' % (seg(i), seg(j), seg(i).replace('→', ''), seg(j).replace('→', ''))) + fig
        steps = [tabs, 'ΔU<sub>%s</sub> ∝ %d - %d = %d, ΔU<sub>%s</sub> ∝ %d - %d = %d' % (seg(i).replace('→', ''), Ts[1], Ts[0], Ts[1] - Ts[0], seg(j).replace('→', ''), Ts[3], Ts[2], Ts[3] - Ts[2]), '비는 %s' % right]
        return mco(body, right, wr, steps=steps, lv='상', fam='e', r=r, core='ΔU 는 온도 변화(PV 변화)에 비례하며 온도가 올라가면 +, 내려가면 −이다.', point='부호까지 포함하여 두 과정의 ΔU 를 비교한다.')
    # bogi
    bank = stmts_cycle(r, names, sts, kinds, 'PV')
    i, j = r.sample(range(n), 2)
    if abs(dUs[i]) == abs(dUs[j]) and dUs[i] != 0:
        eq = dUs[i] == -dUs[j]
        bank.append(('%s 과정과 %s 과정에서 기체의 내부 에너지 변화량은 크기가 같고 부호가 반대이다.' % (seg(i), seg(j)), eq, '%s의 ΔU ∝ %d, %s의 ΔU ∝ %d (×(3/2)P₀V₀) 이므로 %s.' % (seg(i), Ts[(i + 1) % n] - Ts[i], seg(j), Ts[(j + 1) % n] - Ts[j], '크기가 같고 부호가 반대이다' if eq else '크기가 같고 부호도 같다'), 'cmp'))
    else:
        bank.append(('%s 과정과 %s 과정에서 기체의 내부 에너지 변화량은 크기가 같다.' % (seg(i), seg(j)), abs(dUs[i]) == abs(dUs[j]), '%s의 |ΔU| ∝ %d, %s의 |ΔU| ∝ %d (×(3/2)P₀V₀) 이므로 %s.' % (seg(i), abs(Ts[(i + 1) % n] - Ts[i]), seg(j), abs(Ts[(j + 1) % n] - Ts[j]), '같다' if abs(dUs[i]) == abs(dUs[j]) else '같지 않다'), 'cmp'))
    if list(dUs).count(max(dUs)) == 1:
        c = r.randrange(n)
        bank.append(('기체의 내부 에너지 변화량(ΔU)이 가장 큰 과정은 %s이다.' % seg(c), dUs[c] == max(dUs), '각 과정의 ΔU(단위 (3/2)P₀V₀) : ' + ', '.join('%s %s' % (seg(x), fr_str(dUs[x] * Fraction(2, 3))) for x in range(n)) + ' 이므로 ΔU 가 가장 큰 과정은 %s이다.' % seg(max(range(n), key=lambda x: dUs[x])), 'maxdU'))
    bank = [b for b in bank if b[1] is not None]
    sel = pick_stmts(r, bank)
    if not sel: return None
    return bogi(intro + ' 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', sel, pre=fig, ask='', r=r, lv='중' if n == 3 else '상', fam='f',
                core='절대 온도는 PV 에 비례하고 ΔU ∝ ΔT 이므로, 눈금의 P×V 값으로 온도와 ΔU 를 비교한다. 한 순환에서 ΔU = 0 이다.', point='PV 눈금을 곱해 온도·ΔU 를 비교하고 순환 과정의 성질을 적용한다.')
