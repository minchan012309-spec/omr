"""변형 문항용 그래프(SVG). 숫자가 바뀌는 변형 문항은 원본 그림 대신 이 그림을 쓴다."""
import math
INK = '#333'; SUB = '#586476'; ACC = '#2f7fd0'
TXT = "font-family=\"Pretendard,'Noto Sans KR',sans-serif\""
MATH = "font-family=\"'Latin Modern Math','LatinModernMath',serif\""
from mk import MI

def mt(s):
    """그림 속 기호: 영문 한 글자 변수는 수식 기울임(𝐻, 𝐸 …)."""
    out = ''
    for i, c in enumerate(s):
        if c.isascii() and c.isalpha() and (i == 0 or not s[i - 1].isalpha()) and (i == len(s) - 1 or not s[i + 1].isalpha()):
            out += MI[c]
        else:
            out += c
    return out

def _t(x, y, s, size=13, anchor='middle', weight=500, fill=INK, math=False, sub=None):
    fam = MATH if math else TXT
    s = s.replace('&', '&amp;').replace('<', '&lt;')
    sb = ''
    if sub is not None:
        sb = f'<tspan dy="3.5" font-size="{size * 0.72:.1f}">{sub}</tspan>'
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" {fam}>{s}{sb}</text>'

def chem_svg(s):
    """CH4(g) → tspan 첨자."""
    import re
    s = s.replace('&', '&amp;')
    s = re.sub(r'\\frac\{(\d+)\}\{(\d+)\}', lambda m: {('1', '2'): '½'}.get((m.group(1), m.group(2)), f'{m.group(1)}/{m.group(2)}'), s)
    s = s.replace('->', '→')
    s = re.sub(r'(?<=[A-Za-z\)])(\d+)', lambda m: f'<tspan dy="3" font-size="9.5">{m.group(1)}</tspan><tspan dy="-3"></tspan>', s)
    s = re.sub(r'\((g|l|s|aq)\)', lambda m: '(<tspan ' + MATH + '>' + ''.join(MI[c] for c in m.group(1)) + '</tspan>)', s)
    return s

def _ct(x, y, s, size=13, anchor='middle', weight=600):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{INK}" {TXT}>{chem_svg(s)}</text>'

def _arrow(x1, y1, x2, y2, col=INK, w=1.6, head=7):
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - head * math.cos(a), y2 - head * math.sin(a)
    l = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{col}" stroke-width="{w}"/>'
    p1 = (x2, y2); p2 = (hx + head * 0.5 * math.sin(a), hy - head * 0.5 * math.cos(a)); p3 = (hx - head * 0.5 * math.sin(a), hy + head * 0.5 * math.cos(a))
    return l + f'<polygon points="{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" fill="{col}"/>'

def _wrap(w, h, body):
    return f'<div class="fg"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="max-width:100%;height:auto">{body}</svg></div>'

def levels(lv, arrows, ylab='엔탈피', w=360, h=230):
    """엔탈피 관계도. lv: [(이름, 값, x0, x1)] 값이 클수록 위. arrows: [(i, j, x, 라벨)]"""
    vals = [v for _, v, *_ in lv]; lo, hi = min(vals), max(vals)
    sp = hi - lo or 1
    Y = lambda v: 30 + (hi - v) / sp * (h - 70)
    b = _arrow(24, h - 14, 24, 10, INK, 1.4) + _t(30, 20, ylab, 12, 'start', 500, SUB)
    b += f'<line x1="24" y1="{h - 14}" x2="{w - 8}" y2="{h - 14}" stroke="{INK}" stroke-width="1.2"/>'
    for name, v, x0, x1 in lv:
        y = Y(v)
        b += f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{INK}" stroke-width="2.2"/>'
        b += _ct((x0 + x1) / 2, y - 6, name)
    for i, j, x, lab in arrows:
        y1, y2 = Y(lv[i][1]), Y(lv[j][1])
        b += _arrow(x, y1 + (2 if y2 > y1 else -2), x, y2 - (2 if y2 > y1 else -2), ACC, 2)
        if lab:
            b += _t(x + 6, (y1 + y2) / 2 + 4, mt(lab), 13, 'start', 500, '#1d5ca6', True)
    return _wrap(w, h, b)

def profile(Er, Ep, Epk, w=360, h=230, labels=('반응물', '생성물'), marks=(), second=None, ylab='에너지', xlab='반응의 진행'):
    """반응 경로에 따른 에너지 곡선. marks: [('Ea'|'dH'|'Ea2', 라벨)]"""
    hi = max(Epk, second or Epk); lo = min(Er, Ep, 0) if False else min(Er, Ep)
    sp = hi - lo or 1
    Y = lambda v: 28 + (hi - v) / sp * (h - 78)
    xr0, xr1, xp0, xp1, xm = 40, 120, 230, w - 20, 175
    def curve(pk):
        return (f'M{xr0},{Y(Er):.1f} L{xr1},{Y(Er):.1f} C{xr1 + 30},{Y(Er):.1f} {xm - 30},{Y(pk):.1f} {xm},{Y(pk):.1f} '
                f'C{xm + 30},{Y(pk):.1f} {xp0 - 30},{Y(Ep):.1f} {xp0},{Y(Ep):.1f} L{xp1},{Y(Ep):.1f}')
    b = _arrow(28, h - 22, 28, 8, INK, 1.4) + _t(34, 18, ylab, 12, 'start', 500, SUB)
    b += f'<line x1="28" y1="{h - 22}" x2="{w - 6}" y2="{h - 22}" stroke="{INK}" stroke-width="1.2"/>' + _t(w - 8, h - 6, xlab, 12, 'end', 500, SUB)
    b += f'<path d="{curve(Epk)}" fill="none" stroke="{INK}" stroke-width="2.2"/>'
    if second is not None:
        b += f'<path d="{curve(second)}" fill="none" stroke="{INK}" stroke-width="1.8" stroke-dasharray="5 4"/>'
    b += _t((xr0 + xr1) / 2, Y(Er) - 7, labels[0], 12, 'middle', 600) + _t((xp0 + xp1) / 2, Y(Ep) - 7, labels[1], 12, 'middle', 600)
    dash = lambda y, x0, x1: f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{SUB}" stroke-width="1" stroke-dasharray="3 3"/>'
    b += dash(Y(Epk), xm - 70, xm + 10)
    for kind, lab in marks:
        if kind == 'Ea':
            b += dash(Y(Er), xr1, xm + 10) + _arrow(xm - 52, Y(Er) - 1, xm - 52, Y(Epk) + 2, ACC, 1.6) + _arrow(xm - 52, Y(Epk) + 1, xm - 52, Y(Er) - 2, ACC, 1.6)
            b += _t(xm - 58, (Y(Er) + Y(Epk)) / 2 + 4, mt(lab), 13, 'end', 500, '#1d5ca6', True)
        if kind == 'Ea2':
            b += dash(Y(Epk), xm, xm + 80) + _arrow(xm + 62, Y(Ep) - 1, xm + 62, Y(Epk) + 2, ACC, 1.6) + _arrow(xm + 62, Y(Epk) + 1, xm + 62, Y(Ep) - 2, ACC, 1.6)
            b += _t(xm + 68, (Y(Ep) + Y(Epk)) / 2 + 4, mt(lab), 13, 'start', 500, '#1d5ca6', True)
        if kind == 'dH':
            x = xp1 - 18
            b += dash(Y(Er), xr1, x + 6) + _arrow(x, Y(Er), x, Y(Ep) + (-2 if Ep > Er else 2), ACC, 1.6)
            b += _t(x - 6, (Y(Er) + Y(Ep)) / 2 + 4, mt(lab), 13, 'end', 500, '#1d5ca6', True)
    return _wrap(w, h, b)

def plot(series, xlab, ylab, xt, yt, w=360, h=240, marks=()):
    """꺾은선/곡선 그래프. series: [(점 목록, 라벨, 점선?)]"""
    x0, y0, x1, y1 = 52, h - 34, w - 18, 18
    xmax, ymax = xt[-1], yt[-1]
    X = lambda x: x0 + x / xmax * (x1 - x0); Y = lambda y: y0 - y / ymax * (y0 - y1)
    b = _arrow(x0, y0, x0, y1 - 6, INK, 1.3) + _arrow(x0, y0, x1 + 6, y0, INK, 1.3)
    b += _t(x0 - 6, y1 - 8, ylab, 11.5, 'start', 500, SUB) + _t(x1 + 4, y0 + 28, xlab, 11.5, 'end', 500, SUB)
    for v in xt:
        b += _t(X(v), y0 + 15, num_s(v), 11, 'middle', 400, SUB)
        if v: b += f'<line x1="{X(v):.1f}" y1="{y0}" x2="{X(v):.1f}" y2="{y1}" stroke="#d5dbe3" stroke-width="0.8"/>'
    for v in yt:
        b += _t(x0 - 6, Y(v) + 4, num_s(v), 11, 'end', 400, SUB)
        if v: b += f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="#d5dbe3" stroke-width="0.8"/>'
    for pts, lab, dashed in series:
        d = 'M' + ' L'.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in pts)
        b += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2" {"stroke-dasharray=\"5 4\"" if dashed else ""}/>'
        if lab:
            lx, ly = pts[-1]
            b += _t(X(lx) - 2, Y(ly) - 7, lab, 12, 'end', 600)
    for x, y in marks:
        b += f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="2.8" fill="{INK}"/>'
    return _wrap(w, h, b)

def num_s(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return s

def dist(curves, lines, w=360, h=220):
    """운동 에너지 분포 곡선. curves: [(T 라벨, 봉우리 위치 0~1, 점선?)], lines: [(x 0~1, 라벨)]"""
    x0, y0, x1, y1 = 34, h - 30, w - 14, 16
    b = _arrow(x0, y0, x0, y1 - 4, INK, 1.3) + _arrow(x0, y0, x1 + 4, y0, INK, 1.3)
    b += _t(x0 + 6, y1 + 4, '분자 수', 11.5, 'start', 500, SUB) + _t(x1, y0 + 22, '운동 에너지', 11.5, 'end', 500, SUB)
    for lab, pk, dashed in curves:
        pts = []
        for i in range(0, 101):
            e = i / 100 * 1.0
            k = pk
            val = (e / k) ** 2 * math.exp(2 * (1 - e / k)) if e > 0 else 0
            val *= (0.35 / k) ** 0.5
            pts.append((x0 + e * (x1 - x0), y0 - val * (y0 - y1) * 0.92))
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        b += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2" {"stroke-dasharray=\"5 4\"" if dashed else ""}/>'
        top = min(pts, key=lambda q: q[1])
        b += _t(top[0] + 8, top[1] - 4, mt(lab[0]), 13, 'start', 500, INK, True, lab[1:] or None)
    for xv, lab in lines:
        X = x0 + xv * (x1 - x0)
        b += f'<line x1="{X:.1f}" y1="{y0}" x2="{X:.1f}" y2="{y1 + 30}" stroke="{SUB}" stroke-width="1" stroke-dasharray="3 3"/>'
        b += _t(X, y0 + 15, mt(lab[0]), 12.5, 'middle', 500, INK, True, lab[1:] or None)
    return _wrap(w, h, b)
