# -*- coding: utf-8 -*-
"""역학과 에너지(ph) 개념서 Ⅱ·Ⅲ단원·종합: 개념 절(SECS_B) · 요약 노트(SUMMARY) · OX/빈칸 원천 문장(PAIRS_B)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phlib import Fig, Plot, INK, GR, BL, RD, OR, GN, PU, LG
from outline import SUBS, TYPES

_LAB = {}
for _t in TYPES:
    _LAB.setdefault(_t['sub'], []).append(_t['label'])
def L(sub, *idx):
    return [_LAB[sub][i] for i in idx]

# ------------------------------------------------------------ HTML 조각
def hl(s): return '<span class="hl">%s</span>' % s
def eqn(main, small=''): return '<div class="eqn">%s%s</div>' % (main, '<small>%s</small>' % small if small else '')
def nt(label, inner, cls=''): return '<div class="nt%s"><span class="lb">%s</span>%s</div>' % (' ' + cls if cls else '', label, inner)
def ul(*items): return '<ul class="l">' + ''.join('<li>%s</li>' % i for i in items) + '</ul>'
def fg(svg, cap, n=1): return '<div class="fg">%s<div class="cap"><b>그림 %d</b> %s</div></div>' % (svg, n, cap)
def two(a, b): return '<div class="two-c"><div>%s</div><div>%s</div></div>' % (a, b)
def p(s): return '<p>%s</p>' % s
def tb(heads, rows, f=False, left_from=1):
    h = '<table class="tb%s"><thead><tr>' % (' f' if f else '') + ''.join('<th>%s</th>' % c for c in heads) + '</tr></thead><tbody>'
    for row in rows:
        h += '<tr>'
        for i, c in enumerate(row):
            if i == 0: h += '<td class="b">%s</td>' % c
            elif f and i >= left_from: h += '<td class="l">%s</td>' % c
            else: h += '<td>%s</td>' % c
        h += '</tr>'
    return h + '</tbody></table>'
def sb(s): return '<sub>%s</sub>' % s
def sp(s): return '<sup>%s</sup>' % s
def fr(a, b): return '<span class="fr"><span>%s</span><span>%s</span></span>' % (a, b)

# ------------------------------------------------------------ 그림
def _dims(o):
    return o

def fig_work():
    """실린더 + P-V 직사각형."""
    f = Plot(340, 200, 4, 3.4, ml=214, mr=14, mt=18, mb=34)
    f.axes('V', 'P', xticks=(1, 3), yticks=(2,), xfmt=lambda t: {1: 'V₁', 3: 'V₂'}[t], yfmt=lambda t: 'P')
    f.o.append('<polygon points="%s" fill="#cfe2f7" stroke="none"/>' % ' '.join('%.1f,%.1f' % (f.px(x), f.py(y)) for x, y in [(1, 0), (3, 0), (3, 2), (1, 2)]))
    f.line(f.px(1), f.py(2), f.px(3), f.py(2), BL, 2.6)
    f.arrow(f.px(1.6), f.py(2), f.px(2.4), f.py(2), BL, 2.6)
    f.dash_to_axes(1, 2); f.line(f.px(3), f.py(2), f.px(3), f.py(0), GR, 1, '4 3')
    f.text(f.px(2), f.py(1.0), '일 W', 13, bold=True, c=BL)
    f.text(f.px(2), f.py(0.45), '= PΔV', 12.5, c=BL)
    # 실린더
    x1, x2, yb = 30, 130, 172
    f.line(x1, 30, x1, yb, INK, 2.2); f.line(x2, 30, x2, yb, INK, 2.2); f.line(x1, yb, x2, yb, INK, 2.2)
    f.rect(x1 + 1.5, 70, x2 - x1 - 3, 9, '#b9c3d0', INK, 1.2)
    f.rect(x1 + 1.5, 100, x2 - x1 - 3, 9, 'none', GR, 1, dash='4 3')
    f.arrow(x1 + 16, 108, x1 + 16, 76, RD, 1.8)
    f.text(x1 + 22, 94, 'Δh', 12.5, 'start', True, RD)
    f.line(x2 + 8, 70, x2 + 8, 100, GR, 1)
    f.text(x2 + 12, 62, '나중', 11.5, 'start', c=GR)
    f.text(x2 + 12, 120, '처음', 11.5, 'start', c=GR)
    pts = [(46, 130), (70, 150), (96, 138), (60, 160), (110, 158), (84, 124), (118, 130), (50, 112), (100, 118), (74, 112)]
    for x, y in pts: f.circ(x, y, 2.6, BL, BL, 1)
    f.text((x1 + x2) / 2, 20, '압력 P 일정', 12, bold=True, c=GR)
    return f.svg()

def _panel_axes(f, ox, oy, lab):
    f.arrow(ox, oy, ox + 138, oy, INK, 1.3); f.arrow(ox, oy, ox, oy - 78, INK, 1.3)
    f.text(ox + 140, oy - 6, 'V', 12.5, 'end', True, GR); f.text(ox - 4, oy - 74, 'P', 12.5, 'end', True, GR)
    f.text(ox + 60, oy - 86 - 6, lab, 13, 'middle', True, INK)

def fig_processes():
    f = Fig(340, 236)
    def X(ox, V): return ox + V * 40
    def Y(oy, P): return oy - P * 22
    ox1, ox2 = 28, 190
    oy1, oy2 = 112, 228
    # 등압
    _panel_axes(f, ox1, oy1, '등압 (P 일정)')
    f.line(X(ox1, 0.9), Y(oy1, 1.8), X(ox1, 2.5), Y(oy1, 1.8), BL, 2.6); f._head(X(ox1, 2.1), Y(oy1, 1.8), X(ox1, 2.5), Y(oy1, 1.8), BL, 2.6)
    f.text(X(ox1, 1.7), Y(oy1, 1.8) - 7, 'W>0, 온도↑', 11.5, c=BL)
    # 등적
    _panel_axes(f, ox2, oy1, '등적 (V 일정)')
    f.line(X(ox2, 1.6), Y(oy1, 0.6), X(ox2, 1.6), Y(oy1, 2.8), RD, 2.6); f._head(X(ox2, 1.6), Y(oy1, 2.2), X(ox2, 1.6), Y(oy1, 2.8), RD, 2.6)
    f.text(X(ox2, 1.75), Y(oy1, 1.4), 'W=0', 11.5, 'start', c=RD)
    # 등온
    _panel_axes(f, ox1, oy2, '등온 (T 일정)')
    pts = [(X(ox1, v), Y(oy2, 3.0 / v)) for v in [1 + 0.05 * i for i in range(0, 41)]]
    f.poly(pts, 'none', GN, 2.6, close=False); f._head(*pts[-4], *pts[-1], GN, 2.6)
    f.text(X(ox1, 2.3), Y(oy2, 2.6), 'PV 일정', 11.5, 'start', c=GN)
    f.text(X(ox1, 2.3), Y(oy2, 2.05), 'ΔU=0', 11.5, 'start', c=GN)
    # 단열
    _panel_axes(f, ox2, oy2, '단열 (Q=0)')
    pts0 = [(X(ox2, v), Y(oy2, 3.0 / v)) for v in [1 + 0.05 * i for i in range(0, 29)]]
    f.poly(pts0, 'none', GR, 1.6, close=False, dash='4 3')
    pts = [(X(ox2, v), Y(oy2, 3.0 / v ** 1.67)) for v in [1 + 0.05 * i for i in range(0, 29)]]
    f.poly(pts, 'none', PU, 2.6, close=False); f._head(*pts[-4], *pts[-1], PU, 2.6)
    f.text(X(ox2, 2.45), Y(oy2, 1.55), '등온', 11.5, 'start', c=GR)
    f.text(X(ox2, 2.45), Y(oy2, 0.55), '단열', 11.5, 'start', True, PU)
    f.text(X(ox2, 1.0), Y(oy2, 3.0) - 6, '온도↓', 11.5, 'start', c=PU)
    return f.svg()

def fig_cycle():
    f = Plot(340, 214, 4.4, 4.0, ml=52, mr=14, mt=16, mb=34)
    f.axes('V', 'P', xticks=(1, 3), yticks=(1, 3), xfmt=lambda t: {1: 'V₀', 3: '3V₀'}[t], yfmt=lambda t: {1: 'P₀', 3: '3P₀'}[t])
    f.o.append('<polygon points="%s" fill="#cfe2f7" stroke="none"/>' % ' '.join('%.1f,%.1f' % (f.px(x), f.py(y)) for x, y in [(1, 1), (3, 1), (3, 3), (1, 3)]))
    A, B, C, D = (1, 3), (3, 3), (3, 1), (1, 1)
    for a, b in [(A, B), (B, C), (C, D), (D, A)]:
        f.line(f.px(a[0]), f.py(a[1]), f.px(b[0]), f.py(b[1]), BL, 2.4)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = (b[0] - a[0]) * .1, (b[1] - a[1]) * .1
        f._head(f.px(mx - dx), f.py(my - dy), f.px(mx + dx), f.py(my + dy), BL, 2.4)
    for nm, (x, y), dx, dy in [('A', A, -9, -7), ('B', B, 10, -7), ('C', C, 10, 14), ('D', D, -9, 14)]:
        f.circ(f.px(x), f.py(y), 3.4, INK, INK, 1); f.text(f.px(x) + dx, f.py(y) + dy, nm, 13.5, bold=True)
    f.dash_to_axes(1, 3); f.dash_to_axes(3, 1)
    f.text(f.px(2), f.py(2.05), '넓이 = 알짜 일', 12.5, bold=True, c=BL)
    f.text(f.px(2), f.py(1.55), '(시계 방향 → W>0)', 11.5, c=GR)
    f.text(f.px(2), f.py(3) - 7, '등압 팽창', 11.5, c=GR); f.text(f.px(2), f.py(1) + 15, '등압 압축', 11.5, c=GR)
    return f.svg()

def fig_engine():
    f = Fig(340, 224)
    f.rect(100, 6, 140, 36, '#fde3e0', RD, 1.8, 6); f.text(170, 29, '고열원  T₁', 13.5, bold=True, c=RD)
    f.arrow(170, 42, 170, 80, RD, 2.4); f.text(180, 66, 'Q₁ (흡수)', 12.5, 'start', True, RD)
    f.circ(170, 112, 32, '#eef3fa', INK, 2); f.text(170, 117, '열기관', 13.5, bold=True)
    f.arrow(202, 112, 300, 112, GN, 2.8); f.text(251, 102, '일 W', 13, bold=True, c=GN)
    f.arrow(170, 144, 170, 180, BL, 2.4); f.text(180, 168, 'Q₂ (방출)', 12.5, 'start', True, BL)
    f.rect(100, 182, 140, 36, '#dcebfa', BL, 1.8, 6); f.text(170, 205, '저열원  T₂', 13.5, bold=True, c=BL)
    f.text(10, 100, 'Q₁ = W + Q₂', 12.5, 'start', True, GR)
    f.text(10, 120, 'e = W/Q₁', 12.5, 'start', True, GR)
    f.text(10, 140, '= 1 − Q₂/Q₁', 12.5, 'start', True, GR)
    return f.svg()

def fig_diffusion():
    f = Fig(340, 160)
    f.rect(10, 28, 120, 90, '#fafcff', INK, 1.8); f.line(70, 28, 70, 118, GR, 1.6, '4 3')
    for x, y in [(20, 40), (34, 60), (48, 44), (24, 84), (42, 100), (56, 74), (58, 108), (30, 108), (52, 56), (18, 62)]: f.circ(x, y, 3.4, BL, BL, 1)
    f.text(70, 18, '칸막이 제거 전', 12, bold=True, c=GR)
    f.arrow(138, 74, 202, 74, RD, 2.4); f.text(170, 64, '자발적', 12.5, bold=True, c=RD)
    f.text(170, 94, '(S 증가)', 12, c=RD)
    f.rect(210, 28, 120, 90, '#fafcff', INK, 1.8)
    for x, y in [(222, 42), (254, 60), (288, 44), (236, 88), (272, 104), (306, 76), (318, 108), (240, 112), (300, 50), (264, 80)]: f.circ(x, y, 3.4, BL, BL, 1)
    f.text(270, 18, '골고루 퍼진 상태', 12, bold=True, c=GR)
    f.text(170, 142, '되돌아가는 과정은 저절로 일어나지 않는다 (비가역)', 12, c=INK)
    return f.svg()

def fig_shm_xt():
    f = Plot(340, 214, 2.15, 1.5, ymin=-1.5, ml=44, mr=16, mt=14, mb=34)
    f.axes('t', 'x', xticks=(0.5, 1, 1.5, 2), yticks=(1, -1), xfmt=lambda t: {0.5: 'T/2', 1: 'T', 1.5: '3T/2', 2: '2T'}[t], yfmt=lambda t: 'A' if t > 0 else '−A')
    pts = [(i / 100, math.cos(2 * math.pi * i / 100)) for i in range(0, 201)]
    f.pl(pts, BL, 2.6)
    f.line(f.px(0), f.py(1), f.px(2), f.py(1), GR, 1, '4 3'); f.line(f.px(0), f.py(-1), f.px(2), f.py(-1), GR, 1, '4 3')
    for t, y, lab, dy in [(0.25, 0, '속력 최대·가속도 0', -10), (0.5, -1, '속력 0·가속도 최대', 16)]:
        f.circ(f.px(t), f.py(y), 3.4, RD, RD, 1)
    f.text(f.px(0.27), f.py(0) - 8, '평형: v 최대, a=0', 11.5, 'start', c=RD)
    f.text(f.px(0.62), f.py(-1) + 16, '끝점: v=0, a 최대', 11.5, 'start', c=RD)
    y = f.py(1.28)
    f.line(f.px(0), y, f.px(1), y, GN, 1.4); f._head(f.px(0.04), y, f.px(0), y, GN, 1.4); f._head(f.px(0.96), y, f.px(1), y, GN, 1.4)
    f.text(f.px(0.5), y - 4, '주기 T', 12, bold=True, c=GN)
    return f.svg()

def fig_pendulums():
    f = Fig(340, 206)
    # 용수철 진자
    f.hatch(14, 150, 150, GR); f.line(14, 150, 14, 150, GR)
    f.line(16, 64, 16, 150, GR, 3)
    for i in range(0, 90, 8): f.line(16, 64 + i, 8, 72 + i, GR, 1)
    f.spring(16, 112, 92, coils=6, amp=9)
    f.rect(92, 92, 40, 40, '#dfe7f2', INK, 1.8); f.text(112, 117, 'm', 14, bold=True)
    f.line(112, 74, 112, 88, GR, 1.2, '3 3'); f.text(112, 70, 'x=0', 12, c=GR)
    f.arrow(150, 112, 120 + 60, 112, BL, 2.2); f.text(166, 104, '+x', 12, bold=True, c=BL)
    f.arrow(92, 146, 62, 146, RD, 2.4); f.text(78, 138, 'F', 12.5, bold=True, c=RD)
    f.text(86, 180, 'F = −kx', 13, bold=True, c=RD)
    f.text(86, 198, 'T = 2π√(m/k)', 12.5, c=INK)
    # 단진자
    px, py_ = 250, 22
    f.line(240, py_, 284, py_, INK, 3)
    th = math.radians(28); Lh = 120
    bx, by = px + Lh * math.sin(th), py_ + Lh * math.cos(th)
    f.line(px, py_, px, py_ + Lh, GR, 1.2, '4 3')
    f.line(px, py_, bx, by, INK, 1.8); f.circ(bx, by, 10, '#dfe7f2', INK, 1.8)
    f.path('M %.1f %.1f A 38 38 0 0 0 %.1f %.1f' % (px, py_ + 38, px + 38 * math.sin(th), py_ + 38 * math.cos(th)), 'none', RD, 1.6)
    f.text(px + 12, py_ + 54, 'θ', 13, 'start', True, RD)
    f.text(px - 8, py_ + 70, 'L', 13, 'end', True)
    f.arrow(bx, by + 10, bx, by + 40, GN, 2); f.text(bx - 6, by + 38, 'mg', 12.5, 'end', True, GN)
    f.text(250, 198, 'T = 2π√(L/g)', 12.5, c=INK)
    return f.svg()

def fig_shm_energy():
    f = Plot(340, 214, 1.35, 1.35, xmin=-1.35, ml=20, mr=14, mt=16, mb=34)
    x0, y0 = f.px(-1.35), f.py(0)
    f.arrow(x0, y0, f.px(1.35) + 6, y0, INK, 1.4); f.arrow(f.px(0), y0, f.px(0), f.py(1.35) - 6, INK, 1.4)
    f.text(f.px(1.35) + 4, y0 + 17, 'x', 12.5, 'end', True, GR); f.text(f.px(0) + 8, f.py(1.35) + 4, 'E', 12.5, 'start', True, GR)
    for t, lab in [(-1, '−A'), (0, '0'), (1, 'A')]:
        f.line(f.px(t), y0, f.px(t), y0 + 4, INK, 1); f.text(f.px(t), y0 + 17, lab, 11.5, c=GR)
    ep = [(i / 50, (i / 50) ** 2) for i in range(-65, 66)]
    ek = [(i / 50, 1 - (i / 50) ** 2) for i in range(-50, 51)]
    f.pl([p_ for p_ in ep if abs(p_[0]) <= 1.16], BL, 2.6)
    f.pl(ek, GN, 2.6)
    f.line(f.px(-1.2), f.py(1), f.px(1.2), f.py(1), RD, 2, '6 4')
    f.dash_to_axes(-1, 1) if False else None
    f.line(f.px(-1), f.py(1), f.px(-1), y0, GR, 1, '4 3'); f.line(f.px(1), f.py(1), f.px(1), y0, GR, 1, '4 3')
    f.text(f.px(-0.72), f.py(1) - 6, 'E = ½kA² (일정)', 12.5, 'start', True, RD)
    f.text(f.px(1.0) + 6, f.py(0.5), 'Eₚ', 13, 'start', True, BL)
    f.text(f.px(-0.36), f.py(0.5), 'Eₖ', 13, 'start', True, GN)
    return f.svg()

def fig_wave_graphs():
    f = Fig(340, 212)
    def panel(ox, title, xl, per, perlab, amp_arrow):
        oy = 104
        f.arrow(ox, oy, ox + 132, oy, INK, 1.3); f.arrow(ox, oy + 62, ox, oy - 66, INK, 1.3)
        f.text(ox + 132, oy + 16, xl, 12.5, 'end', True, GR); f.text(ox - 5, oy - 60, 'y', 12.5, 'end', True, GR)
        f.sin_path(ox, oy, 38, per, 2, 0, 40, BL, 2.6)
        f.line(ox, oy - 38, ox + 2 * per, oy - 38, GR, 1, '4 3')
        yb = oy + 52
        f.line(ox + per * 0.25, yb, ox + per * 1.25, yb, GN, 1.4); f._head(ox + per * .29, yb, ox + per * .25, yb, GN, 1.4); f._head(ox + per * 1.21, yb, ox + per * 1.25, yb, GN, 1.4)
        f.line(ox + per * 0.25, oy - 38, ox + per * .25, yb, GR, 1, '3 3'); f.line(ox + per * 1.25, oy - 38, ox + per * 1.25, yb, GR, 1, '3 3')
        f.text(ox + per * .75, yb + 15, perlab, 12.5, bold=True, c=GN)
        f.text(ox + 64, 20, title, 12, bold=True)
        return oy
    oy = panel(30, '변위-위치 (t 고정)', 'x', 62, '파장 λ', True)
    panel(200, '변위-시간 (x 고정)', 't', 62, '주기 T', True)
    for ox in (30, 200):
        f.arrow(ox + 14, oy, ox + 14, oy - 36, RD, 1.6); f.text(ox + 20, oy - 12, 'A', 12.5, 'start', True, RD)
    return f.svg()

def _pulse(f, x, y, up=True, c=BL, w=22, h=16):
    s = -1 if up else 1
    f.poly([(x - w, y), (x, y + s * h), (x + w, y)], 'none', c, 2.2, close=False)

def fig_refl_refr():
    f = Fig(340, 228)
    y0 = 52
    f.sin_path(14, y0, 20, 56, 3, 0, 40, BL, 2.4); f.sin_path(182, y0, 20, 32, 4.5, 0, 40, RD, 2.4)
    f.line(182, 12, 182, 96, GR, 1.4, '5 4')
    f.text(98, 14, '매질 Ⅰ (빠름)', 12, bold=True, c=BL); f.text(262, 14, '매질 Ⅱ (느림)', 12, bold=True, c=RD)
    f.line(14, 84, 70, 84, BL, 1.4); f._head(18, 84, 14, 84, BL, 1.4); f._head(66, 84, 70, 84, BL, 1.4); f.text(42, 98, 'λ₁', 12.5, bold=True, c=BL)
    f.line(182, 84, 214, 84, RD, 1.4); f._head(186, 84, 182, 84, RD, 1.4); f._head(210, 84, 214, 84, RD, 1.4); f.text(198, 98, 'λ₂', 12.5, bold=True, c=RD)
    f.text(170, 118, 'f 불변,  v₁ > v₂  →  λ₁ > λ₂', 12.5, bold=True)
    # 반사
    f.text(85, 136, '고정단 반사', 12.5, bold=True); f.text(255, 136, '자유단 반사', 12.5, bold=True)
    for ox, fixed in [(20, True), (190, False)]:
        for yy, lab, right in [(170, '입사', True), (206, '반사', False)]:
            f.line(ox, yy, ox + 130, yy, GR, 1.4)
            if fixed: f.line(ox + 130, yy - 16, ox + 130, yy + 16, INK, 3.5)
            else: f.circ(ox + 130, yy, 4, 'none', INK, 1.6)
            up = True if (right or not fixed) else False
            _pulse(f, ox + 56, yy, up, RD if not right else BL, 20, 15)
            ax = ox + 92 if right else ox + 18
            f.arrow(ax - (14 if right else -14), yy - 20, ax + (14 if right else -14), yy - 20, GN, 1.6) if False else None
            f.text(ox + 4, yy - 20, lab, 11.5, 'start', c=GR)
            if right: f.arrow(ox + 86, yy, ox + 108, yy, GN, 1.8)
            else: f.arrow(ox + 36, yy + 0, ox + 14, yy, GN, 1.8)
    return f.svg()

def fig_interference():
    f = Fig(340, 214)
    def col(ox, ph, title, sumamp):
        f.text(ox + 70, 14, title, 12.5, bold=True)
        for y0, c, pp, lab in [(46, BL, 0, '파 1'), (92, RD, ph, '파 2')]:
            f.line(ox, y0, ox + 140, y0, LG, 1)
            f.sin_path(ox, y0, 15, 46, 3, pp, 40, c, 2.2)
            f.text(ox - 4, y0 - 20, lab, 11.5, 'start', c=c)
        y0 = 160
        f.line(ox, y0, ox + 140, y0, LG, 1)
        f.sin_path(ox, y0, 15 * sumamp, 46, 3, 0, 40, GN, 2.8)
        f.text(ox - 4, 126, '합성파', 11.5, 'start', True, GN)
    col(14, 0, '보강 간섭', 2)
    col(186, math.pi, '상쇄 간섭', 0)
    f.text(84, 206, '진폭 2A', 12.5, bold=True, c=GN); f.text(256, 206, '진폭 0', 12.5, bold=True, c=GN)
    return f.svg()

def fig_doppler():
    f = Fig(340, 196)
    cy = 92
    for k in range(4, 0, -1):
        cx = 206 - 7 * k
        f.circ(cx, cy, 20 * k, 'none', BL, 1.6)
    f.circ(206, cy, 5, RD, RD, 1)
    f.arrow(214, cy, 250, cy, RD, 2.4); f.text(236, cy - 10, 'vₛ', 12.5, bold=True, c=RD)
    f.text(210, 182, '음원', 12, c=RD)
    f.circ(312, cy, 4, INK, INK, 1); f.text(312, cy - 10, 'A', 13, bold=True)
    f.circ(30, cy, 4, INK, INK, 1); f.text(30, cy - 10, 'B', 13, bold=True)
    f.text(312, cy + 22, '파면 촘촘', 11.5, c=BL); f.text(312, cy + 38, 'λ↓ f↑', 12, bold=True, c=BL)
    f.text(30, cy + 22, '파면 성김', 11.5, c=BL); f.text(30, cy + 38, 'λ↑ f↓', 12, bold=True, c=BL)
    f.text(170, 14, '음원 앞쪽 f′ > f,  뒤쪽 f′ < f', 12, bold=True)
    return f.svg()

def fig_strings():
    f = Fig(340, 220)
    x1, x2 = 56, 270
    Lw = x2 - x1
    for n, y0, lab in [(1, 40, 'L = λ/2'), (2, 110, 'L = λ'), (3, 180, 'L = 3λ/2')]:
        pts = [(x1 + Lw * i / 80, y0 - 24 * math.sin(n * math.pi * i / 80)) for i in range(81)]
        pts2 = [(x, 2 * y0 - y) for x, y in pts]
        f.poly(pts, 'none', BL, 2.4, close=False); f.poly(pts2, 'none', BL, 1.4, close=False, dash='4 3')
        f.circ(x1, y0, 3.6, INK, INK, 1); f.circ(x2, y0, 3.6, INK, INK, 1)
        f.text(8, y0 + 4, 'n=%d' % n, 12.5, 'start', True)
        f.text(x2 + 12, y0 + 4, lab, 12, 'start', c=GR)
    return f.svg()

def fig_pipes():
    f = Fig(340, 214)
    f.text(84, 14, '닫힌 관 (한쪽 막힘)', 12.5, bold=True); f.text(256, 14, '열린 관 (양쪽 열림)', 12.5, bold=True)
    Lw = 132
    for k, (y0, lab_c, lab_o, nc, no) in enumerate([(56, 'L = λ/4', 'L = λ/2', 1, 1), (140, 'L = 3λ/4', 'L = λ', 3, 2)]):
        # 닫힌 관
        x0 = 18
        f.line(x0, y0 - 22, x0 + Lw, y0 - 22, INK, 2); f.line(x0, y0 + 22, x0 + Lw, y0 + 22, INK, 2)
        f.line(x0, y0 - 22, x0, y0 + 22, INK, 4)
        pts = [(x0 + Lw * i / 80, y0 - 20 * math.sin(nc * math.pi * i / 160)) for i in range(81)]
        f.poly(pts, 'none', BL, 2.2, close=False); f.poly([(x, 2 * y0 - y) for x, y in pts], 'none', BL, 1.3, close=False, dash='4 3')
        f.text(x0 + Lw / 2, y0 + 40, lab_c, 12, c=GR)
        # 열린 관
        x0 = 190
        f.line(x0, y0 - 22, x0 + Lw, y0 - 22, INK, 2); f.line(x0, y0 + 22, x0 + Lw, y0 + 22, INK, 2)
        pts = [(x0 + Lw * i / 80, y0 - 20 * math.cos(no * math.pi * i / 80)) for i in range(81)]
        f.poly(pts, 'none', BL, 2.2, close=False); f.poly([(x, 2 * y0 - y) for x, y in pts], 'none', BL, 1.3, close=False, dash='4 3')
        f.text(x0 + Lw / 2, y0 + 40, lab_o, 12, c=GR)
    f.text(170, 208, '실선·점선: 반 주기 간격의 두 순간의 매질 변위', 11.5, c=GR)
    return f.svg()

def fig_beats():
    f = Plot(340, 214, 1.08, 2.7, ymin=-2.7, ml=40, mr=14, mt=16, mb=32)
    f.axes('t(s)', '', xticks=(), yticks=())
    N = 700
    pts = [(i / N, math.sin(2 * math.pi * 12 * i / N) + math.sin(2 * math.pi * 14 * i / N)) for i in range(N + 1)]
    f.pl(pts, GN, 1.8)
    env = [(i / 200, abs(2 * math.cos(2 * math.pi * i / 200))) for i in range(201)]
    f.pl(env, RD, 1.6, '5 3'); f.pl([(a, -b) for a, b in env], RD, 1.6, '5 3')
    y = f.py(2.45)
    f.line(f.px(0), y, f.px(0.5), y, INK, 1.4); f._head(f.px(0.03), y, f.px(0), y, INK, 1.4); f._head(f.px(0.47), y, f.px(0.5), y, INK, 1.4)
    f.text(f.px(0.25), y - 4, '맥놀이 주기', 12, bold=True)
    f.text(f.px(0.75), f.py(-2.2) + 12, 'f₁=12 Hz, f₂=14 Hz → 맥놀이 2 Hz', 11.5, c=GR) if False else None
    f.text(f.px(1.08), f.py(-2.2) + 12, '12 Hz + 14 Hz → 맥놀이 2 Hz', 11.5, 'end', c=GR)
    return f.svg()

def num_(t):
    return ('%g' % t)

def fig_strategy():
    f = Fig(340, 214)
    rows = [('힘·가속도·시간', 'F = ma + 운동 공식'), ('속력·높이·거리', '역학적 에너지 보존'), ('충돌·분열·반동', '운동량 보존'), ('원운동의 장력', '구심력 ΣF = mv²/r')]
    cols = [BL, GN, OR, PU]
    for i, (a, b) in enumerate(rows):
        y = 8 + i * 50
        f.rect(8, y, 140, 38, '#f2f5fa', cols[i], 1.8, 6); f.text(78, y + 24, a, 12.5, bold=True)
        f.arrow(150, y + 19, 184, y + 19, cols[i], 2.4)
        f.rect(188, y, 146, 38, '#ffffff', cols[i], 1.8, 6); f.text(261, y + 24, b, 12.5, bold=True, c=cols[i] if cols[i] != OR else '#9a6f00')
    return f.svg()

def fig_hub():
    f = Fig(340, 224)
    f.rect(100, 92, 140, 40, '#eef3fa', INK, 2, 8); f.text(170, 117, 'v = fλ', 15, bold=True)
    boxes = [(6, 6, '굴절', 'f 불변, v₁/v₂ = λ₁/λ₂', BL), (178, 6, '정상파', 'f = nv/(2L)', GN),
             (6, 170, '도플러', 'f′ = f(v±vₒ)/(v∓vₛ)', RD), (178, 170, '맥놀이', 'f_b = |f₁ − f₂|', PU)]
    for x, y, t1, t2, c in boxes:
        f.rect(x, y, 156, 46, '#ffffff', c, 1.8, 6); f.text(x + 78, y + 19, t1, 13, bold=True, c=c); f.text(x + 78, y + 37, t2, 11.5)
    f.line(84, 52, 130, 92, GR, 1.4); f.line(256, 52, 210, 92, GR, 1.4); f.line(84, 170, 130, 132, GR, 1.4); f.line(256, 170, 210, 132, GR, 1.4)
    return f.svg()

def fig_graph3():
    f = Fig(340, 178)
    cols = {'p': BL, 'v': RD, 't': GN}
    def panel(ox, title, xl, yl, items):
        oy = 140
        f.arrow(ox, oy, ox + 96, oy, INK, 1.3); f.arrow(ox, oy, ox, oy - 100, INK, 1.3)
        f.text(ox + 96, oy + 15, xl, 12.5, 'end', True, GR); f.text(ox - 4, oy - 94, yl, 12.5, 'end', True, GR)
        f.text(ox + 50, 14, title, 13, bold=True)
        for kind, pts in items:
            P_ = [(ox + x, oy - y) for x, y in pts]
            f.poly(P_, 'none', cols[kind], 2.6, close=False); f._head(*P_[-2], *P_[-1], cols[kind], 2.6)
    hy = [(30 + i * 2.5, 1200 / (30 + i * 2.5)) for i in range(21)]
    panel(16, 'P-V', 'V', 'P', [('p', [(30, 40), (82, 40)]), ('v', [(30, 40), (30, 80)]), ('t', hy)])
    panel(126, 'P-T', 'T', 'P', [('v', [(40, 40), (80, 80)]), ('p', [(40, 40), (86, 40)]), ('t', [(40, 40), (40, 12)])])
    panel(236, 'V-T', 'T', 'V', [('p', [(40, 40), (80, 80)]), ('v', [(40, 40), (86, 40)]), ('t', [(40, 40), (40, 80)])])
    for ox in (126, 236):
        f.line(ox, 140, ox + 40, 100, GR, 1, '3 3')
    f.text(60, 170, '등압', 12.5, bold=True, c=BL); f.text(170, 170, '등적', 12.5, bold=True, c=RD); f.text(280, 170, '등온', 12.5, bold=True, c=GN)
    return f.svg()

def fig_carnot():
    f = Fig(340, 214)
    def panel(ox, title, A, B, C, D, kinds, lab):
        oy = 176
        f.arrow(ox, oy, ox + 140, oy, INK, 1.3); f.arrow(ox, oy, ox, oy - 140, INK, 1.3)
        f.text(ox + 142, oy + 15, 'V', 12.5, 'end', True, GR); f.text(ox - 4, oy - 134, 'P', 12.5, 'end', True, GR)
        f.text(ox + 70, 14, title, 13, bold=True)
        sx, sy = 38, 36
        def pt(v, p_): return (ox + v * sx, oy - p_ * sy)
        for (s, e), kd in zip([(A, B), (B, C), (C, D), (D, A)], kinds):
            n = 20; pts = []
            for i in range(n + 1):
                t = i / n
                if kd == 'iso':
                    v = s[0] + (e[0] - s[0]) * t; c0 = s[0] * s[1]; p_ = c0 / v
                elif kd == 'ad':
                    v = s[0] + (e[0] - s[0]) * t; p_ = s[1] * (s[0] / v) ** 1.67
                else:
                    v = s[0] + (e[0] - s[0]) * t; p_ = s[1] + (e[1] - s[1]) * t
                pts.append(pt(v, p_))
            col = {'iso': RD if s[1] > 1.2 and s[0] < e[0] and kinds[0] == 'iso' else BL}.get(kd, GN)
            f.poly(pts, 'none', {'iso': RD, 'ad': PU, 'isv': GN}[kd] if False else (PU if kd == 'ad' else (GN if kd == 'isv' else BL)), 2.4, close=False)
            m = pts[n // 2]; q = pts[n // 2 + 1]
            f._head(m[0] - (q[0] - m[0]) * .2, m[1] - (q[1] - m[1]) * .2, q[0], q[1], PU if kd == 'ad' else (GN if kd == 'isv' else BL), 2.4)
        for nm, (v, p_), dx, dy in [('A', A, -9, -6), ('B', B, 8, -6), ('C', C, 9, 14), ('D', D, -9, 14)]:
            x, y = pt(v, p_); f.circ(x, y, 3, INK, INK, 1); f.text(x + dx, y + dy, nm, 13, bold=True)
        for i, s in enumerate(lab): f.text(ox + 70, 196 + i * 0, '', 11)
    # 카르노
    A = (1.0, 3.0); B = (2.0, 1.5); C = (3.0, 1.5 * 2 ** 1.67 / 3 ** 1.67)
    K1 = 1.5 * 2 ** 1.67
    vD = 3.0 * (3.0 / K1) ** (1 / 0.67)
    D = (vD, 3.0 / vD ** 1.67)
    panel(24, '카르노 순환', A, B, C, D, ['iso', 'ad', 'iso', 'ad'], '')
    # 스털링
    A2 = (1.0, 3.0); B2 = (2.0, 1.5); C2 = (2.0, 1.0); D2 = (1.0, 2.0)
    panel(192, '스털링 순환', A2, B2, C2, D2, ['iso', 'isv', 'iso', 'isv'], '')
    f.text(94, 206, '파랑 등온 · 보라 단열', 11.5, c=GR); f.text(262, 206, '파랑 등온 · 초록 등적', 11.5, c=GR)
    return f.svg()

# ============================================================ 개념 절
def _s(sub, i, html, *tidx):
    return dict(title=SUBS[sub]['secs'][i], html=html, types=L(sub, *tidx))

# ------------------------------------------------------------ Ⅱ-A
_A1 = two(
    p('이상 기체는 분자 사이의 인력과 분자 자체의 부피를 무시할 수 있는 기체이다. 이때 분자가 가진 에너지는 거의 운동 에너지뿐이므로, ' + hl('이상 기체의 내부 에너지는 분자들의 운동 에너지의 합') + '이다. 단원자 분자 이상 기체 n몰의 내부 에너지는 U = (3/2)nRT 이고, 분자 수 N으로는 U = (3/2)NkT 이다.')
    + ul('온도가 같으면 분자 한 개의 평균 운동 에너지가 같고, 분자 수가 많을수록 U가 크다.',
         '같은 기체라면 ' + hl('U는 절대 온도 T에 비례') + '한다. 온도가 오르면 U가 증가하고, 온도가 같으면 U도 같다.',
         '상태 방정식 PV = nRT 에서 U = (3/2)PV 이므로 PV의 비가 곧 U의 비이다.')
    + p('기체가 팽창하면서 피스톤을 밀어 올릴 때 기체는 외부에 일을 한다. 압력 P가 일정하면 피스톤의 단면적 A, 이동 거리 Δh에 대해 W = PAΔh = PΔV 이다.'),
    fg(fig_work(), '피스톤이 Δh만큼 밀려 올라가는 동안 기체가 한 일은 P-V 그래프의 직사각형 넓이와 같다.'))
_A1 += eqn('U = (3/2)nRT  (U ∝ T)　　W = P·ΔV', '압력 일정 · 팽창 W>0 · 압축 W<0 · 1 L = 10' + sp('−3') + ' m' + sp('3') + ',  1기압 ≈ 1.0×10' + sp('5') + ' Pa')
_A1 += tb(['구분', '부피 변화', '기체가 한 일 W', '에너지의 이동'], [
    ['팽창', 'ΔV > 0', 'W > 0 (기체가 일을 함)', '기체 → 외부로 에너지 이동'],
    ['압축', 'ΔV < 0', 'W < 0 (기체가 일을 받음)', '외부 → 기체로 에너지 이동'],
    ['부피 일정', 'ΔV = 0', 'W = 0', '일의 형태의 이동 없음']])
_A1 += p('<b>단위 변환</b>은 일의 계산에서 가장 흔한 실수 지점이다. 압력은 Pa(= N/m²)로, 부피는 m³로 바꾸어 곱한다. 열량은 1 kcal = 4200 J 로 J에 맞춘다.')
_A1 += tb(['양', '환산', '예'], [
    ['압력', '1기압 = 1.0×10' + sp('5') + ' Pa', '2기압 = 2.0×10' + sp('5') + ' Pa'],
    ['부피', '1 L = 10' + sp('−3') + ' m' + sp('3'), '5 L = 5×10' + sp('−3') + ' m' + sp('3')],
    ['일', '1 Pa·m' + sp('3') + ' = 1 J', '1기압에서 1 L 팽창 = 100 J'],
    ['열량', '1 kcal = 4200 J', '0.5 kcal = 2100 J']])
_A1 += p('<b>피스톤으로 나뉜 두 기체의 비교</b>: 같은 종류의 기체라면 U ∝ NT 이다. 분자 수가 N, 2N 인 두 기체의 온도가 같으면 내부 에너지는 1 : 2 이고, 온도(K)의 비가 1 : 2 인 같은 수의 기체는 1 : 2 이다. 피스톤이 자유롭게 움직여 멈춘 상태에서는 두 기체의 압력이 같고, 오랜 시간 두면 열 평형으로 온도가 같아진다. 고정 핀을 빼면 압력이 큰 쪽이 팽창하여 압력이 같아질 때까지 움직인다.')
_A1 += nt('핵심 정리', ul('이상 기체의 내부 에너지는 온도(절대 온도)와 분자 수만으로 정해지는 상태량이다.', '단위: Pa·m' + sp('3') + ' = N·m = J. 부피를 L로 줄 때는 m' + sp('3') + '로 바꾼 뒤 곱한다. 예: 2.0×10' + sp('5') + ' Pa에서 3 L 팽창 시 W = 2.0×10' + sp('5') + '×3×10' + sp('−3') + ' = 600 J.', '압력이 변하면 W는 P-V 그래프 아래 넓이로 구한다.'))
_A1 += nt('혼동 주의', p('<b>온도가 올랐다고 일을 한 것은 아니다.</b> 부피가 그대로이면 W = 0 이다. 또 "압력이 높을수록 내부 에너지가 크다"는 분자 수와 부피가 같을 때만 말할 수 있다. 내부 에너지의 기준은 압력이 아니라 <b>절대 온도(K)</b>이다. 섭씨 온도에 비례한다고 쓰지 않도록 한다.'), 'wa')

_A2 = two(
    p(hl('열역학 제1법칙') + '은 에너지 보존을 열까지 넓힌 법칙이다. 기체가 흡수한 열 Q는 내부 에너지 증가 ΔU와 기체가 외부에 한 일 W의 합과 같다.')
    + p('부호 약속: Q > 0 은 열 흡수, ΔU > 0 은 온도 상승, W > 0 은 팽창(기체가 일을 함)이다. 부호만 정확히 읽으면 네 가지 과정이 모두 이 한 식으로 정리된다.')
    + ul('<b>등압</b>: P 일정, V∝T. 팽창하면 온도↑, 열을 흡수하며 Q = ΔU + PΔV.', '<b>등적</b>: V 일정, P∝T. W = 0 이므로 Q = ΔU.', '<b>등온</b>: T 일정, PV 일정(보일 법칙). ΔU = 0 이므로 Q = W.', '<b>단열</b>: 열 출입 없음. Q = 0 이므로 ΔU = −W.'),
    fg(fig_processes(), '네 가지 열역학 과정의 P-V 그래프. 화살표는 팽창 방향의 예이다.'))
_A2 += eqn('Q = ΔU + W', '등압: Q=ΔU+PΔV · 등적: Q=ΔU · 등온: Q=W · 단열: ΔU=−W')
_A2 += tb(['과정', '조건', 'ΔU', 'W', 'Q'], [
    ['등압 팽창', 'P 일정', '+ (T 상승)', '+', '+ (흡열)'],
    ['등적 가열', 'V 일정', '+', '0', '+ (흡열)'],
    ['등온 팽창', 'T 일정', '0', '+', '+ (흡열)'],
    ['단열 팽창', 'Q = 0', '−  (T 하강)', '+', '0'],
    ['단열 압축', 'Q = 0', '+  (T 상승)', '−', '0']])
_A2 += p('상태가 둘 주어지면 PV/T 가 같음을 이용해 절대 온도의 비를 구하고, 이를 U의 비로 이어 간다. 일상 현상과 실험은 아래 표처럼 과정으로 판별한다.')
_A2 += tb(['사례', '과정', '근거'], [
    ['구름 생성(상승 기류)', '단열 팽창', '팽창하며 일을 해 온도↓, 수증기가 응결'],
    ['압력밥솥', '등적 가열', '부피 일정, 열을 받아 온도·압력↑'],
    ['스프레이·병마개가 열릴 때', '단열 팽창', '빠른 팽창, 온도↓, 차가워지거나 김이 서림'],
    ['디젤 기관의 점화·자전거 펌프', '단열 압축', '일을 받아 온도↑, 연료가 점화'],
    ['유리관 속 솜 점화 실험', '단열 압축', '피스톤을 급히 눌러 온도↑'],
    ['끓는 물에 넣은 풍선이 부풂', '등압 팽창(근사)', '대기압 일정, 온도↑, V↑']])
_A2 += nt('핵심 정리', ul('과정을 판별하면 ΔU, W, Q 중 알려진 것에서 나머지가 결정된다.', '온도 변화의 방향 = ΔU의 부호이고, 부피 변화의 방향 = W의 부호이다.', '등온: 흡수한 열 전부가 일로, 단열: 한 일만큼 내부 에너지가 감소.'))
_A2 += nt('혼동 주의', p('<b>단열 과정은 "온도가 일정"한 과정이 아니다.</b> 열의 출입이 없을 뿐, 팽창하면 내부 에너지가 줄어 온도가 내려간다. 온도가 일정한 것은 등온 과정이다. 또 등온 과정에서 ΔU = 0 이므로 열을 받아도 온도는 오르지 않는다.'), 'wa')

_A3 = two(
    p(hl('P-V 그래프에서 곡선과 부피 축 사이의 넓이는 기체가 한 일') + '이다. 부피가 늘어나는 방향이면 W > 0, 줄어드는 방향이면 W < 0 이다. 직선 경로는 사다리꼴 넓이로 계산한다.')
    + ul('수평선은 등압, 수직선은 등적, 반비례 곡선은 등온이다. 단열 곡선은 같은 점에서 등온선보다 더 가파르다.', '원점에서 멀수록(PV가 클수록) 온도가 높으므로 ΔU의 부호도 PV의 증감으로 읽는다.')
    + p('기체가 처음 상태로 돌아오는 ' + hl('순환 과정') + '에서는 ΔU = 0 이므로 Q = W 이다. 알짜 일은 폐곡선이 둘러싼 넓이이고, 시계 방향으로 돌면 W > 0, 반시계 방향이면 W < 0 이다.'),
    fg(fig_cycle(), '네 과정으로 이루어진 직사각형 순환. 시계 방향이므로 알짜 일은 양(+)이다.'))
_A3 += eqn('순환 과정:  ΔU = 0,  Q = W = (폐곡선의 넓이)', '직사각형 순환: W = (2V₀)(2P₀) = 4P₀V₀')
_A3 += tb(['과정', '종류', '기체가 한 일 W', 'PV (온도에 비례)'], [
    ['A → B', '등압 팽창', '3P₀ × 2V₀ = 6P₀V₀', '3P₀V₀ → 9P₀V₀ (↑)'],
    ['B → C', '등적 냉각', '0', '9P₀V₀ → 3P₀V₀ (↓)'],
    ['C → D', '등압 압축', '−P₀ × 2V₀ = −2P₀V₀', '3P₀V₀ → P₀V₀ (↓)'],
    ['D → A', '등적 가열', '0', 'P₀V₀ → 3P₀V₀ (↑)'],
    ['합계', '한 바퀴', '6 − 2 = 4P₀V₀', '처음과 같음 → ΔU = 0']])
_A3 += p('같은 과정을 서로 다른 좌표로 나타내면 모양이 달라진다. 원점을 지나는 직선은 P ∝ T(등적) 또는 V ∝ T(등압)를 뜻한다. 아래 그림은 처음 상태에서 출발한 세 과정이 세 그래프에서 어떻게 보이는지 보여 준다.')
_A3 += fg(fig_graph3(), '같은 상태에서 시작하는 등압·등적·등온 과정의 P-V, P-T, V-T 그래프.', 2)
_A3 += tb(['과정', 'P-V', 'P-T', 'V-T'], [
    ['등압', 'V축에 나란한 수평선', 'T축에 나란한 수평선', '원점을 지나는 직선'],
    ['등적', 'P축에 나란한 수직선', '원점을 지나는 직선', 'T축에 나란한 수평선'],
    ['등온', '반비례 곡선(쌍곡선)', 'P축에 나란한 수직선', 'V축에 나란한 수직선']])
_A3 += p('<b>흡열·방열 찾기</b>: 순환 과정의 각 구간에서 ΔU는 PV의 증감(온도 변화), W는 부피 변화로 정한 뒤 Q = ΔU + W 의 부호를 본다. 등적 가열·등압 팽창은 흡열이고, 등적 냉각·등압 압축은 방열이다. 순환에서 온도가 같은 두 상태(PV가 같은 점)의 내부 에너지는 같고, A → B 와 B → A 의 ΔU는 크기가 같고 부호가 반대이다. 위 직사각형 예에서 A와 C는 PV가 같아 온도가 같다.')
_A3 += nt('핵심 정리', ul('일은 경로에 따라 달라지고, 내부 에너지는 처음·나중 상태만으로 정해진다.', '부호 표를 채울 때는 ① 부피 변화로 W, ② PV 변화로 ΔU, ③ Q = ΔU + W 순서로 구한다.'))
_A3 += nt('혼동 주의', p('같은 A → B 라도 <b>경로가 다르면 W와 Q가 달라진다.</b> 그러나 ΔU는 처음·나중 온도가 같으면 경로와 무관하게 같다. 또 순환 과정에서 "일을 한 번 하고 되돌아오니 일이 0"이라고 하면 안 된다. 되돌아오는 경로가 다르면 넓이만큼 알짜 일이 남는다.'), 'wa')

SECS_B_A = [
    _s('Ⅱ-A', 0, _A1, 0, 1, 13),
    _s('Ⅱ-A', 1, _A2, 2, 3, 4, 5, 6, 10, 11, 14, 17),
    _s('Ⅱ-A', 2, _A3, 7, 8, 9, 12, 15, 16),
]

# ------------------------------------------------------------ Ⅱ-B
_B1 = two(
    p(hl('열기관') + '은 고열원에서 열 Q₁을 흡수해 일 W를 하고, 나머지 열 Q₂를 저열원으로 방출하는 장치이다. 한 순환이 끝나면 처음 상태로 돌아오므로 ΔU = 0 이고, 제1법칙에서 W = Q₁ − Q₂ 이다.')
    + p(hl('열효율') + ' e는 흡수한 열 중 일로 바뀐 비율이다. 방출열 Q₂는 반드시 존재하므로 e는 언제나 1(100 %)보다 작다.')
    + ul('예: Q₁ = 500 J, Q₂ = 300 J 이면 W = 200 J, e = 200/500 = 0.4 = 40 %.', 'P-V 순환에서는 Q₁ = 열을 흡수하는 과정의 Q의 합, Q₂ = 열을 방출하는 과정의 |Q|의 합이다.'),
    fg(fig_engine(), '열기관의 에너지 흐름. 화살표 굵기를 에너지의 크기로 읽는다.'))
_B1 += eqn('W = Q₁ − Q₂　　e = W/Q₁ = 1 − Q₂/Q₁  (e < 1)', '같은 두 열원 사이의 최대 효율은 e = 1 − T₂/T₁ (T는 절대 온도)')
_B1 += p('앞 단원의 직사각형 순환에서 단원자 분자 기체라 가정하면 A → B 에서 Q = 15P₀V₀, D → A 에서 Q = 3P₀V₀ 로 열을 흡수하고, B → C 에서 9P₀V₀, C → D 에서 5P₀V₀ 를 방출한다. Q₁ = 18P₀V₀, Q₂ = 14P₀V₀ 이므로 W = 4P₀V₀ 이고 e = 4/18 ≈ 22 % 이다. 가열되는 두 구간의 열을 모두 Q₁에 넣는 것이 핵심이다.')
_B1 += p(hl('카르노 기관') + '은 같은 두 열원 사이에서 작동하는 열기관 중 열효율이 가장 큰 이상적 기관으로, 순환이 ' + '등온 팽창 → 단열 팽창 → 등온 압축 → 단열 압축' + '이다. 열효율은 e = 1 − T' + sb('L') + '/T' + sb('H') + ' (T는 절대 온도)이며, 고열원 500 K, 저열원 300 K 이면 e = 1 − 300/500 = 0.4 = 40 % 이다. ' + hl('스털링 기관') + '은 등온 팽창 → 등적 냉각 → 등온 압축 → 등적 가열로 순환한다.')
_B1 += fg(fig_carnot(), '카르노 순환(왼쪽)과 스털링 순환(오른쪽)의 P-V 그래프.', 2)
_B1 += tb(['열기관이 미친 영향', '내용'], [
    ['긍정', '증기 기관·내연 기관으로 산업과 교통이 발달하고, 발전소로 전기를 대량 생산하게 됨'],
    ['부정', '화석 연료 사용으로 대기 오염과 온실 기체가 늘고, 방출열로 인한 열 오염이 생김']])
_B1 += tb(['구분', '내용', '제1법칙', '제2법칙'], [
    ['제1종 영구기관', '에너지를 공급받지 않고 계속 일을 하는 기관', '위반', '—'],
    ['제2종 영구기관', '열을 모두 일로 바꾸는 (e = 100 %) 기관', '위반 아님', '위반'],
    ['실제 열기관', '가솔린·디젤 기관, 화력 발전 등 (e는 대략 20~40 %)', '만족', '만족']])
_B1 += nt('핵심 정리', ul('열기관의 일은 W = Q₁ − Q₂ 이고, 열효율은 e = W/Q₁ 이다.', '열효율 100 %인 열기관은 만들 수 없다. 이를 제2종 영구기관의 불가능이라 한다.'))
_B1 += nt('혼동 주의', p('<b>Q₂는 손실이 아니라 반드시 버려야 하는 열이다.</b> 마찰을 완전히 없앤다고 해서 e가 1이 되지 않는다. 또 e = W/Q₂ 로 쓰는 실수가 많다. 분모는 <b>흡수한 열 Q₁</b>이다.'), 'wa')

_B2 = two(
    p(hl('가역 과정') + '은 주변에 아무 변화도 남기지 않고 거꾸로 되돌릴 수 있는 과정이고, ' + hl('비가역 과정') + '은 그렇지 못한 과정이다. 열의 전도, 기체의 확산, 마찰, 단열 자유 팽창 등 자연에서 저절로 일어나는 변화는 거의 비가역이다.')
    + p('열역학 제2법칙은 변화의 방향을 말해 준다. 열은 저절로 고온에서 저온으로만 이동하며, 열을 전부 일로 바꾸는 순환 기관은 없다. 이를 수치로 나타내는 양이 ' + hl('엔트로피') + '(무질서한 정도의 척도)이다.'),
    fg(fig_diffusion(), '칸막이를 없애면 기체는 저절로 퍼지지만, 다시 한쪽으로 모이지는 않는다.', 1))
_B2 += eqn('고립계의 엔트로피:  ΔS ≥ 0', '가역 과정 ΔS = 0 · 비가역 과정 ΔS > 0 (전체 합)')
_B2 += tb(['현상', '가역 여부', '엔트로피(전체)'], [
    ['뜨거운 물과 찬 물이 섞여 미지근해짐', '비가역', '증가'],
    ['잉크가 물속에 퍼짐 · 향수 냄새가 퍼짐', '비가역', '증가'],
    ['마찰로 운동 에너지가 열로 바뀜', '비가역', '증가'],
    ['마찰 없이 천천히 하는 이상적 팽창·압축', '가역(이상적)', '변화 없음']])
_B2 += eqn('ΔS = Q/T  (T: 절대 온도, 열을 받으면 +, 잃으면 −)', '고온 물체 ΔS = −Q/T' + sb('H') + ' · 저온 물체 ΔS = +Q/T' + sb('L') + ' · 전체 ΔS > 0 이면 자발적')
_B2 += p('예를 들어 400 K 물체에서 300 K 물체로 1200 J의 열이 이동하면 고온 물체는 −1200/400 = −3 J/K, 저온 물체는 +1200/300 = +4 J/K 이므로 전체 엔트로피는 1 J/K 증가하여 자발적인 방향이다. 반대 방향이면 전체가 −1 J/K 이므로 저절로 일어나지 않는다.')
_B2 += p('<b>확률로 본 확산</b>: 입자 N개가 있는 칸막이 용기에서 칸막이를 제거하면 입자 각각이 어느 쪽에 있을 확률이 1/2 이므로 모두 한쪽에 모일 확률은 (1/2)' + sp('N') + ' 이다. N = 10 이면 약 1/1000 이고, N이 아주 크면 사실상 0이다. 입자가 골고루 퍼진 상태가 경우의 수가 가장 많아 확률이 높으므로 자연스러운 변화는 확률이 높은 방향(엔트로피가 커지는 방향)으로 일어난다.')
_B2 += tb(['제2법칙의 표현', '내용'], [
    ['엔트로피', '고립계에서 엔트로피는 줄어들지 않는다.'],
    ['열의 이동', '열은 저절로 저온에서 고온으로 이동하지 않는다.'],
    ['확률', '자발적 변화는 확률이 높은 방향으로 진행한다.'],
    ['열기관', '열효율이 1인 열기관(제2종 영구기관)은 불가능하다.']])
_B2 += p('제1·제2법칙 종합 판단은 순서가 있다. 먼저 W = Q₁ − Q₂ 인지 확인하고(제1법칙), 다음에 Q₂ > 0 이고 W < Q₁ 인지 확인한다(제2법칙). 예컨대 Q₁ = 100 J, W = 100 J, Q₂ = 0 이라면 에너지는 맞지만 제2법칙에 어긋난다. Q₁ = 100 J, W = 120 J 이면 제1법칙부터 어긋난다.')
_B2 += nt('핵심 정리', ul('자발적 변화는 엔트로피가 증가하는 방향으로 일어난다.', '냉장고 속의 엔트로피는 줄지만 바깥으로 버린 열을 포함한 전체 엔트로피는 늘어난다.'))
_B2 += nt('혼동 주의', p('<b>엔트로피가 감소하는 일이 절대 없는 것이 아니다.</b> 일을 해 주면 계의 일부는 질서를 높일 수 있다. 단, 주변을 포함한 전체 엔트로피는 줄지 않는다. 또 제2법칙은 "에너지가 사라진다"는 뜻이 아니라 쓸모 있는 에너지로 바뀌기 어려워진다는 뜻이다.'), 'wa')

SECS_B_B = [
    _s('Ⅱ-B', 0, _B1, 0, 1, 2, 5, 7),
    _s('Ⅱ-B', 1, _B2, 3, 4, 6, 8, 9),
]

# ------------------------------------------------------------ Ⅲ-A
_C1 = two(
    p(hl('단진동') + '은 평형 위치를 중심으로 일정한 주기로 왕복하는 운동으로, 변위에 비례하고 방향이 반대인 복원력이 작용할 때 나타난다.')
    + ul('<b>진폭 A</b>: 평형 위치에서 최대 변위의 크기. 한 번 왕복하는 동안 움직인 거리는 4A.', '<b>주기 T</b>: 한 번 왕복하는 데 걸리는 시간. <b>진동수</b> f = 1/T (단위 Hz).', '변위 x(t) = A cos(2πt/T) 꼴. 원운동의 ' + hl('정사영') + '이 단진동이다.')
    + p('변위-시간 그래프의 기울기가 속도이다. 변위가 0인 평형 위치를 지날 때 기울기가 가장 가파르므로 속력이 최대이고, 가속도는 0이다. 변위가 최대인 끝점에서는 기울기가 0이므로 속력이 0이고 가속도의 크기가 최대이다.'),
    fg(fig_shm_xt(), '단진동의 변위-시간 그래프. 평형 위치와 끝점에서 속력·가속도가 반대로 나타난다.'))
_C1 += eqn('f = 1/T　　v' + sb('max') + ' = Aω = 2πA/T　　a' + sb('max') + ' = Aω² ', 'ω = 2π/T (각진동수), 반지름 A인 등속 원운동의 정사영과 주기가 같다')
_C1 += tb(['위치', '변위 x', '속력', '가속도·복원력'], [
    ['평형 위치', '0', '최대', '0'],
    ['끝점(±A)', '±A (최대)', '0', '최대 (평형 위치 쪽)'],
    ['그 사이', '0 < |x| < A', '중간', '|x|에 비례']])
_C1 += nt('핵심 정리', ul('반지름 A, 주기 T인 등속 원운동의 정사영은 진폭 A, 주기 T인 단진동이다.', '원운동의 속력 2πA/T 가 단진동의 최대 속력이다.', '그래프에서 가로축이 시간이면 주기, 곡선의 최댓값이 진폭이다.'))
_C1 += nt('혼동 주의', p('<b>진폭과 한 번 왕복 거리를 혼동하지 않는다.</b> 한 번 왕복 거리는 4A이다. 또 "속력이 클 때 가속도도 크다"는 틀렸다. 속력과 가속도는 시간 그래프에서 위상이 어긋나 한쪽이 최대일 때 다른 쪽은 0이다.'), 'wa')

_C2 = two(
    p('복원력이 F = −kx 인 용수철에서 k(N/m)는 용수철 상수이다. F-x 그래프의 기울기의 크기가 k이다. 이때 ' + hl('용수철 진자의 주기는 T = 2π√(m/k)') + ' 로, 진폭과 무관하다. 용수철을 수직으로 걸어도 평형 위치만 아래로 내려갈 뿐 주기는 같다.')
    + p(hl('단진자') + '(줄의 길이 L)는 각이 작을 때(약 10° 이하) 복원력이 mg sinθ ≈ mgθ 로 변위에 비례해 단진동한다. 주기는 T = 2π√(L/g) 이다.')
    + ul('단진자의 주기는 추의 질량과 진폭(작은 각)에 무관하다.', '줄 길이를 4배로 하면 주기는 2배, g가 1/6인 달에서는 √6배가 된다.', '같은 재질의 용수철을 반으로 자르면 한 조각의 k는 2배이다.'),
    fg(fig_pendulums(), '용수철 진자(왼쪽)와 단진자(오른쪽)의 복원력과 주기.'))
_C2 += eqn('용수철 진자 T = 2π√(m/k)　　단진자 T = 2π√(L/g)', '주기 비는 √ 안의 비의 제곱근으로 구한다')
_C2 += tb(['구분', '복원력', '주기가 의존하는 양', '주기와 무관한 양'], [
    ['용수철 진자', 'F = −kx', '질량 m, 용수철 상수 k', '진폭, 중력 가속도'],
    ['단진자', 'mg sinθ ≈ mgθ', '줄 길이 L, 중력 가속도 g', '질량, 진폭(작은 각)']])
_C2 += p('예: 질량 m인 추를 단 용수철 진자의 주기가 1 s 이면 질량을 4m으로 바꿀 때 주기는 2 s, 용수철 상수를 4배로 하면 주기는 0.5 s 이다.')
_C2 += nt('핵심 정리', ul('용수철 진자: 질량이 클수록 주기 길어지고, k가 클수록 짧아진다.', '단진자: 길수록 길어지고, g가 클수록 짧아진다.', 'F-x 그래프에서 기울기의 크기 = k 를 구해 주기에 넣는 문제가 자주 나온다.'))
_C2 += nt('혼동 주의', p('<b>용수철 진자의 주기는 중력 가속도와 무관</b>하지만, <b>단진자의 주기는 질량과 무관</b>하다. 둘을 서로 바꿔 외우기 쉽다. 또 T ∝ √m, T ∝ √L 이므로 질량·길이를 4배 하면 4배가 아니라 2배가 된다.'), 'wa')

_C3 = two(
    p('마찰이 없을 때 단진동하는 물체의 ' + hl('역학적 에너지 E = ½kA²') + ' 는 일정하다. 변위가 x일 때 탄성 위치 에너지는 ½kx², 운동 에너지는 ½k(A² − x²) 이다.')
    + ul('평형 위치(x = 0): E는 모두 운동 에너지, 속력 최대.', '끝점(x = ±A): E는 모두 위치 에너지, 속력 0.', 'Eₖ = Eₚ 인 지점은 x = ±A/√2 이다.', '에너지가 변하는 주기는 진동 주기의 절반(T/2)이다.')
    + p('최대 속력은 ½mv' + sb('max') + sp('2') + ' = ½kA² 에서 v' + sb('max') + ' = A√(k/m) = Aω 이다. 진폭이 2배가 되면 E는 4배, 최대 속력은 2배가 된다. 단진자에서는 최저점에서 운동 에너지가 최대이며 최고점 높이 h에 대해 mgh 와 같다.'),
    fg(fig_shm_energy(), '단진동의 에너지-변위 그래프. 위치 에너지와 운동 에너지의 합은 언제나 E.'))
_C3 += eqn('E = ½kA² = ½mv' + sb('max') + sp('2'), 'Eₚ = ½kx²,  Eₖ = E − Eₚ,  v' + sb('max') + ' = A√(k/m)')
_C3 += tb(['위치', 'x', 'Eₖ', 'Eₚ', '속력'], [
    ['평형 위치', '0', 'E (최대)', '0', '최대'],
    ['x = ±A/√2', '±0.71A', 'E/2', 'E/2', 'v' + sb('max') + '/√2'],
    ['끝점', '±A', '0', 'E (최대)', '0']])
_C3 += nt('핵심 정리', ul('E ∝ A² (k 일정). 진폭이 같은 두 진동은 k가 클수록 E가 크다.', '에너지 그래프에서 두 곡선의 교점이 x = ±A/√2 이다.'))
_C3 += nt('혼동 주의', p('<b>"위치 에너지가 최대일 때 속력도 최대"가 아니다.</b> 끝점에서 위치 에너지가 최대이고 속력은 0이다. 또 질량을 바꾸어도 E = ½kA² 는 변하지 않는다(진폭이 같다면). 질량은 최대 속력만 바꾼다.'), 'wa')

SECS_B_C = [
    _s('Ⅲ-A', 0, _C1, 0, 1, 6),
    _s('Ⅲ-A', 1, _C2, 2, 3, 4),
    _s('Ⅲ-A', 2, _C3, 5),
]

# ------------------------------------------------------------ Ⅲ-B
_D1 = two(
    p(hl('파동') + '은 매질이 진동하며 에너지가 전달되는 현상이다. 매질의 각 입자는 제자리에서 진동할 뿐 파동과 함께 이동하지 않는다.')
    + ul('<b>진폭</b> A: 중심에서 마루(골)까지. <b>파장</b> λ: 이웃한 마루 사이 거리.', '<b>주기</b> T와 <b>진동수</b> f = 1/T.', '파동의 속력은 v = fλ = λ/T 이다. 같은 매질에서 v는 일정하므로 f가 커지면 λ가 짧아진다.')
    + p('그래프를 읽을 때는 가로축을 먼저 본다. 변위-위치 그래프에서는 가로 길이가 파장, 변위-시간 그래프에서는 가로 길이가 주기이다. 속력을 구하려면 두 그래프에서 λ와 T를 각각 읽어 v = λ/T 로 계산한다.'),
    fg(fig_wave_graphs(), '같은 파동을 위치(왼쪽)와 시간(오른쪽)으로 나타낸 그래프. 읽는 양이 다르다.'))
_D1 += eqn('v = fλ = λ/T　　f = 1/T', '예: λ = 2 m, T = 0.5 s 이면 v = 4 m/s')
_D1 += tb(['구분', '횡파', '종파'], [
    ['진동 방향과 진행 방향', '서로 수직', '서로 나란함'],
    ['모양', '마루와 골', '밀한 부분과 소한 부분'],
    ['예', '줄의 파동, 물결, 빛, 지진의 S파', '소리, 용수철의 압축파, 지진의 P파'],
    ['공통', '에너지를 전달한다', '매질 자체는 이동하지 않는다']])
_D1 += p('예를 들어 변위-위치 그래프에서 λ = 4 m, 변위-시간 그래프에서 T = 2 s 를 읽었다면 v = 4/2 = 2 m/s 이다. 같은 줄에서 속력은 일정하므로 진동수를 2배로 하면 파장은 절반이 된다.')
_D1 += nt('핵심 정리', ul('파동의 속력은 매질이 결정하고, 진동수는 파원이 결정한다.', '두 그래프에서 읽은 λ와 T로 v = λ/T 를 구한다.'))
_D1 += nt('혼동 주의', p('<b>파동의 속력 v와 매질 입자의 진동 속력은 다르다.</b> 입자의 속력은 위치마다 달라지지만 파동의 속력은 매질이 같으면 일정하다. 또 변위-위치 그래프의 가로 길이를 주기로 읽는 실수를 주의한다.'), 'wa')

_D2 = two(
    p('파동이 매질의 경계에서 일부가 되돌아오는 것이 ' + hl('반사') + '이고, 다른 매질로 들어가면서 진행 방향이 꺾이는 것이 ' + hl('굴절') + '이다. 반사 법칙은 입사각 = 반사각이며, 반사할 때 진동수·파장·속력은 변하지 않는다.')
    + ul('<b>고정단 반사</b>: 위상이 반대로 바뀌어(위상 π 변화) 펄스가 뒤집혀 돌아온다.', '<b>자유단 반사</b>: 위상이 그대로이므로 같은 방향의 펄스가 돌아온다.')
    + p('굴절하는 동안 진동수는 파원이 정하므로 변하지 않는다. 속력이 바뀌면 파장도 속력에 비례해 바뀐다. 속력이 느린 매질에서는 파장이 짧아지고 진행 방향이 법선 쪽으로 가까워진다.'),
    fg(fig_refl_refr(), '위: 매질이 바뀔 때 파장이 짧아진다. 아래: 고정단과 자유단에서의 펄스 반사.'))
_D2 += p('예를 들어 물결파가 깊은 곳에서 얕은 곳으로 들어가 속력이 3/4배가 되면 파장도 3/4배가 되고 진동수는 그대로이다. 소리가 공기에서 물로 들어가면 속력이 훨씬 커지므로 같은 진동수에서 파장이 길어진다.')
_D2 += eqn('sinθ₁ / sinθ₂ = v₁ / v₂ = λ₁ / λ₂　　(f₁ = f₂)', 'θ₁: 입사각, θ₂: 굴절각 (법선과 이루는 각)')
_D2 += tb(['양', '반사', '굴절'], [
    ['진동수 f', '불변', '불변'],
    ['파장 λ', '불변', '속력에 비례하여 변함'],
    ['속력 v', '불변', '매질에 따라 변함'],
    ['진행 방향', '입사각 = 반사각', '속력이 느린 쪽으로 법선에 가까워짐']])
_D2 += nt('핵심 정리', ul('굴절에서 변하지 않는 것은 진동수, 변하는 것은 속력과 파장이다.', '물결파는 깊은 곳에서 빠르고 얕은 곳에서 느리다. 얕은 곳에서 파장이 짧아진다.'))
_D2 += nt('혼동 주의', p('<b>굴절할 때 파장이 같다고 하면 안 된다.</b> 파장이 변하고 진동수가 같다. 또 고정단 반사에서 위상이 반대이므로 마루로 들어간 펄스는 골로 돌아온다. 자유단에서는 마루가 마루로 돌아온다.'), 'wa')

_D3 = two(
    p(hl('중첩 원리') + '에 따르면 두 파동이 만나는 곳의 변위는 각 파동의 변위를 더한 것이다. 만난 뒤에는 서로 영향 없이 각자의 모양으로 진행한다.')
    + ul('<b>보강 간섭</b>: 마루와 마루(골과 골)가 만나 진폭이 커진다(진폭 A₁ + A₂).', '<b>상쇄 간섭</b>: 마루와 골이 만나 진폭이 작아진다(진폭 |A₁ − A₂|).')
    + p('같은 위상으로 진동하는 두 파원에서 나온 파동은 점 P에서 만난다. 두 파원까지의 경로차 Δ가 정수 배 파장이면 보강, 반정수 배 파장이면 상쇄가 일어난다. 보강이 계속 일어나는 점을 이은 선이 배선, 상쇄가 계속 일어나는 점을 이은 선이 마디선이다.'),
    fg(fig_interference(), '같은 진폭의 두 파동이 같은 위상(왼쪽), 반대 위상(오른쪽)으로 만날 때의 합성파.'))
_D3 += eqn('보강: Δ = mλ　　상쇄: Δ = (m + ½)λ　(m = 0, 1, 2, …)', '두 파원이 같은 위상일 때 · 반대 위상이면 조건이 서로 바뀐다')
_D3 += tb(['경로차 Δ', '두 파동의 위상 관계', '합성 결과'], [
    ['0, λ, 2λ …', '같은 위상', '보강 (진폭 최대)'],
    ['λ/2, 3λ/2 …', '반대 위상', '상쇄 (진폭 최소)'],
    ['그 외', '중간', '진폭이 그 사이']])
_D3 += p('예: 파장이 2 cm 인 같은 위상의 두 파원에서 어떤 점까지의 거리가 각각 10 cm, 15 cm 이면 경로차 Δ = 5 cm = 2.5λ 이므로 그 점에서는 상쇄 간섭이 일어난다.')
_D3 += nt('핵심 정리', ul('경로차는 거리의 차이의 절댓값으로 구해 파장과 비교한다.', '두 파원 사이의 보강선(배선) 수는 파원 간격 d와 파장의 관계로 정해진다.'))
_D3 += nt('혼동 주의', p('<b>상쇄 간섭이 일어나는 지점에서 파동이 사라지는 것은 아니다.</b> 그 지점에서만 변위가 서로 지워지고, 파동의 에너지는 다른 곳(보강 지점)으로 재분배된다. 또 경로차가 파장의 정수 배일 때를 상쇄로 착각하지 않는다.'), 'wa')

SECS_B_D = [
    _s('Ⅲ-B', 0, _D1, 0, 1, 2),
    _s('Ⅲ-B', 1, _D2, 3, 5),
    _s('Ⅲ-B', 2, _D3, 4, 6),
]

# ------------------------------------------------------------ Ⅲ-C
_E1 = two(
    p('소리는 공기 같은 매질의 밀한 부분과 소한 부분이 퍼져 나가는 ' + hl('종파') + '로, 진공에서는 전달되지 않는다. 공기 중 소리의 속력은 약 340 m/s 이고, 온도가 높을수록 빠르다. 일반적으로 고체에서 가장 빠르다.')
    + ul('세기: 진폭이 클수록 크다.', '높이: 진동수가 클수록 높은 소리.', '음색: 파형이 결정한다.')
    + p('메아리처럼 소리가 반사되어 돌아오는 데 걸린 시간 t로 거리를 구하면 왕복이므로 d = vt/2 이다. ' + hl('도플러 효과') + '는 음원이나 관찰자가 움직여 관찰되는 진동수가 달라지는 현상이다. 서로 가까워지면 f′가 커지고 멀어지면 작아진다.'),
    fg(fig_doppler(), '오른쪽으로 움직이는 음원이 낸 파면. 앞쪽(A)은 파장이 짧고 뒤쪽(B)은 길다.'))
_E1 += eqn('f′ = f · (v ± vₒ)/(v ∓ vₛ)', '분자 +: 관찰자가 음원에 접근 · 분모 −: 음원이 관찰자에 접근 (반대로 멀어지면 부호 반대)')
_E1 += tb(['상황', '진동수 f′', '파장 λ′', '소리 속력'], [
    ['정지한 음원, 관찰자 접근 (속력 vₒ)', 'f(v + vₒ)/v', '불변', '관찰자에게는 v + vₒ'],
    ['음원이 정지한 관찰자에 접근 (속력 vₛ)', 'f·v/(v − vₛ)', '(v − vₛ)/f 로 짧아짐', '매질이 정하므로 v'],
    ['서로 멀어짐', '작아짐', '길어짐', '—']])
_E1 += nt('핵심 정리', ul('소리의 속력 v는 매질이 정하며 음원의 운동으로 변하지 않는다.', '음원이 움직이면 파장이, 관찰자가 움직이면 파동을 만나는 상대 속력이 달라져 진동수가 변한다.'))
_E1 += nt('혼동 주의', p('<b>도플러 효과는 소리의 높이 변화이지 음원이 낸 소리의 진동수가 변한 것이 아니다.</b> 음원은 같은 f로 진동한다. 또 접근할 때는 f′ > f, 멀어질 때는 f′ < f 이다. 부호를 외우기보다 "가까워지면 크게"를 먼저 정한 뒤 식을 쓴다.'), 'wa')

_E2 = two(
    p('진폭과 파장이 같고 진행 방향이 반대인 두 파동이 겹치면 한 자리에서 진동하는 ' + hl('정상파') + '가 생긴다. 진폭이 0인 곳이 마디, 최대인 곳이 배이며, 이웃한 마디 사이는 λ/2, 마디와 배 사이는 λ/4 이다.')
    + p('양 끝이 고정된 줄에서는 양 끝이 마디이므로 L = nλ/2, 진동수 f = nv/(2L) 이다. n = 1 이 기본 진동수이고, 마디는 끝점을 포함해 n + 1개, 배는 n개이다.'),
    fg(fig_strings(), '양 끝이 고정된 줄의 정상파 (n = 1, 2, 3).'))
_E2 += p('관에서는 닫힌 끝이 마디, 열린 끝이 배이다. ' + hl('닫힌 관') + '은 한쪽이 마디, 다른 쪽이 배이므로 L = (2n − 1)λ/4 이고 홀수 배 진동수만 나온다. ' + hl('열린 관') + '은 양 끝이 배이므로 L = nλ/2 이다. 같은 진동수의 소리에 관이 공명하면 소리가 크게 들린다.')
_E2 += fg(fig_pipes(), '닫힌 관과 열린 관의 정상파(공기 입자의 변위). 닫힌 끝은 마디, 열린 끝은 배.', 2)
_E2 += eqn('줄·열린 관: f = nv/(2L)　　닫힌 관: f = (2n − 1)v/(4L)', '관 끝 보정은 무시 · 공명 실험에서 연속한 두 공명 길이의 차 = λ/2')
_E2 += tb(['구분', '끝 조건', '파장 조건', '진동수'], [
    ['양 끝 고정 줄', '마디 – 마디', 'L = nλ/2', 'nv/(2L)'],
    ['열린 관', '배 – 배', 'L = nλ/2', 'nv/(2L)'],
    ['닫힌 관', '마디 – 배', 'L = (2n−1)λ/4', '(2n−1)v/(4L)']])
_E2 += nt('핵심 정리', ul('그림에서 마디(또는 배)의 수를 세어 L과 λ의 관계를 쓰고 f = v/λ 에 넣는다.', '닫힌 관의 두 번째로 낮은 공명 진동수는 기본 진동수의 3배이다.'))
_E2 += nt('혼동 주의', p('<b>닫힌 관의 기본 진동수는 같은 길이의 열린 관의 절반이다.</b> 열린 관과 달리 닫힌 관은 홀수 배 진동수만 낸다. 또 마디와 마디 사이는 λ가 아니라 <b>λ/2</b>이다.'), 'wa')

_E3 = two(
    p('진동수가 조금 다른 두 소리가 겹치면 진폭이 주기적으로 커졌다 작아져 소리의 세기가 주기적으로 변한다. 이 현상이 ' + hl('맥놀이') + '이다. 1초 동안 소리가 커지는 횟수가 맥놀이 진동수이다.')
    + p('맥놀이 진동수는 두 진동수의 차 f_b = |f₁ − f₂| 이고, 맥놀이 주기는 그 역수이다. 합성음의 진동수는 두 진동수의 평균 (f₁ + f₂)/2 이다. 악기를 조율할 때 기준음과 비교해 맥놀이가 느려지거나 없어지도록 맞춘다.'),
    fg(fig_beats(), '12 Hz와 14 Hz의 소리를 합성한 파형. 점선은 진폭의 변화이다.'))
_E3 += eqn('f_b = |f₁ − f₂|　　T_b = 1/f_b', '예: 440 Hz 와 444 Hz → 맥놀이 4 Hz → 1초에 4번 커졌다 작아짐')
_E3 += tb(['응용', '이용하는 원리', '핵심'], [
    ['초음파 거리 측정(어군 탐지, 의료 영상)', '반사', 'd = vt/2 (왕복 시간), 직진성이 좋은 20 kHz 이상'],
    ['노이즈 캔슬링 헤드폰', '상쇄 간섭', '소음과 반대 위상의 소리를 내보냄'],
    ['악기 조율', '맥놀이', '진동수 차가 작을수록 맥놀이가 느림'],
    ['건물 음향 설계', '반사·흡수·공명', '흡음재로 반사를 줄이고 공명을 피함']])
_E3 += p('초음파는 파장이 짧아 직진성이 좋고 작은 물체에서도 반사되므로 의료 영상·비파괴 검사에 쓰인다. 공기 중(340 m/s)에서 초음파를 보내고 0.1 s 후 반사파를 받았다면 거리는 340×0.1/2 = 17 m 이다.')
_E3 += nt('핵심 정리', ul('초음파는 가청 주파수 범위(약 20 Hz ~ 20 kHz)를 넘는 진동수의 소리이다.', '초음파 반사 시간으로 거리를 구할 때는 반드시 2로 나눈다.'))
_E3 += nt('혼동 주의', p('<b>맥놀이 진동수는 두 진동수의 합이 아니라 차이다.</b> 또 맥놀이로 들리는 소리의 높이는 두 진동수의 평균에 가까우며 f_b와 같지 않다. 노이즈 캔슬링은 소음을 없애는 것이 아니라 <b>간섭으로 상쇄</b>하는 것이다.'), 'wa')

SECS_B_E = [
    _s('Ⅲ-C', 0, _E1, 0, 1, 2),
    _s('Ⅲ-C', 1, _E2, 4, 5, 7),
    _s('Ⅲ-C', 2, _E3, 3, 6),
]

# ------------------------------------------------------------ 종합
_F1 = two(
    p('역학 문제는 "무엇을 묻는가"로 도구를 고른다. 아래 네 가지 질문을 순서대로 던져 보면 풀이 방향이 거의 정해진다.')
    + ul('<b>힘·가속도·시간</b>을 묻는다 → 운동 방정식 F = ma 와 등가속도 공식(또는 포물선의 두 성분).', '<b>속력·높이·거리</b>를 묻고 시간이 필요 없다 → ' + hl('역학적 에너지 보존') + '(마찰이 있으면 W = ΔE).', '<b>충돌·분열·반동</b> → ' + hl('운동량 보존') + '(외력의 합이 0, 또는 충돌 시간이 아주 짧을 때).', '<b>원운동의 장력·항력</b> → 구심력 ΣF = mv²/r, 속력은 에너지 보존으로.'),
    fg(fig_strategy(), '묻는 양에 따른 풀이 도구 선택.'))
_F1 += eqn('mgh = ½mv²  (낙하·빗면)　　m₁v₁ + m₂v₂ = m₁v₁′ + m₂v₂′', '높이 1.8 m의 마찰 없는 빗면 바닥에서 v = √(2×10×1.8) = 6 m/s')
_F1 += tb(['상황', '쓸 법칙', '조건·주의'], [
    ['빗면 · 운동 법칙 · 에너지', 'a = g sinθ 와 v² = 2as, 또는 mgh = ½mv²', '질량과 각도는 속력에 무관(마찰 없음)'],
    ['포물선 운동과 역학적 에너지', '속력은 에너지로, 시간·거리는 성분 분해', '수평 속도 일정, 높이가 같으면 속력 같음'],
    ['충돌과 용수철', '충돌: 운동량 보존, 압축: 에너지 보존', '완전 비탄성 충돌의 에너지는 보존되지 않음'],
    ['연직 원운동과 에너지', '최저점 속력은 에너지로, 장력은 구심력으로', 'T − mg = mv²/r (최저점)'],
    ['용수철 진자와 에너지', 'ω = √(k/m), v' + sb('max') + ' = Aω, E = ½kA²', 'k·m 변화는 √ 비례']])
_F1 += nt('핵심 정리', ul('한 문제 안에서 구간마다 법칙을 바꿔 쓴다. 충돌 순간은 운동량, 충돌 후 용수철·빗면에서는 에너지.', '에너지는 스칼라(부호 없음), 운동량은 벡터(방향에 부호)이다.'))
_F1 += nt('혼동 주의', p('<b>모든 충돌에서 역학적 에너지가 보존된다고 쓰면 안 된다.</b> 운동량은 외력이 없으면 보존되지만 운동 에너지는 탄성 충돌에서만 보존된다. 반대로 에너지 보존은 마찰 같은 비보존력이 일하지 않을 때만 쓴다. 속력은 방향을 따지지 않고 에너지로 구한 뒤 방향은 따로 판단한다.'), 'wa')

_F2 = two(
    p('열역학 제1법칙은 에너지 보존 법칙의 확장이다. 마찰열처럼 역학적 에너지가 줄어든 만큼 열이 생기고, 기체가 한 일은 피스톤·추의 위치 에너지, 운동 에너지, 대기에 한 일로 나뉜다. 에너지가 사라지는 것이 아니라 형태가 바뀌어 전체는 보존된다.')
    + ul('<b>기체의 일과 역학적 에너지</b>: 기체가 한 일 W = (추의 위치 에너지 증가) + (대기압에 한 일) + (운동 에너지 증가).', '<b>열기관의 일률</b>: 출력 P = e × (공급 열의 비율). 출력 20 kW, e = 0.25 이면 공급 열은 80 kW, 연료 발열량으로 소비량을 구한다.')
    + p('파동 단원에서는 v = fλ 가 모든 풀이의 중심이다. 어떤 현상이든 먼저 어느 양이 불변인지 정하고, 식을 선택한다. 소리의 속력은 문제에 값이 없으면 340 m/s 로 놓는다.'),
    fg(fig_hub(), '파동 현상별로 정해지는 불변량과 사용할 식. 중심은 v = fλ.', 1))
_F2 += eqn('굴절: f 불변　　정상파: λ 조건 → f = v/λ　　도플러: f′ = f(v ± vₒ)/(v ∓ vₛ)', '진동하는 음원: 접근하는 속력이 최대일 때 f′ 최대, 멀어지는 속력이 최대일 때 f′ 최소')
_F2 += tb(['단원', '핵심 아이디어', '공통 연결'], [
    ['열역학', 'Q = ΔU + W, 순환 ΔU = 0', '에너지 보존'],
    ['단진동', 'E = ½kA² 일정', '에너지 보존, 원운동의 정사영'],
    ['파동·소리', 'v = fλ, 중첩과 간섭', '주기성, 매질이 v 결정'],
    ['도플러 + 단진동·원운동', '음원의 속도 성분만 영향', '평형점에서 최대 속력']])
_F2 += p('진동하는 음원은 평형 위치를 지나는 순간 속력이 최대이므로, 그때 관찰자 쪽으로 오는 방향이면 f′가 최대, 멀어지는 방향이면 최소이다. 등속 원운동하는 음원은 속력이 일정해도 관찰자 방향의 속도 성분이 달라진다. 관찰자가 원의 평면 위 먼 곳에 있으면, 속도가 관찰자를 향하는 지점에서 최대 진동수가, 멀어지는 지점에서 최소 진동수가 관측된다.')
_F2 += nt('핵심 정리', ul('열기관: W = Q₁ − Q₂, e = W/Q₁, 일률 = W/t.', '정상파 → 파장 조건 → v = fλ, 도플러 → f′ 식 → 진동수 비교.'))
_F2 += nt('혼동 주의', p('<b>도플러 효과에서 음원 속력 vₛ가 소리 속력 v 보다 크다고 생각하지 않는다.</b> 문제의 음원은 v보다 훨씬 느리다. 또 진동수가 바뀌어도 소리 속력은 매질이 같으면 340 m/s 로 일정하다.'), 'wa')

SECS_B_F = [
    _s('종합', 0, _F1, 0, 1, 2, 3, 5),
    _s('종합', 1, _F2, 4, 6, 7),
]

SECS_B = {'Ⅱ-A': SECS_B_A, 'Ⅱ-B': SECS_B_B, 'Ⅲ-A': SECS_B_C, 'Ⅲ-B': SECS_B_D, 'Ⅲ-C': SECS_B_E, '종합': SECS_B_F}

# ============================================================ 요약 노트
def _ftb(rows, heads=('용어', '식', '조건')):
    return tb(list(heads), rows, f=True)

_S1 = ('<h4>역학</h4>' + _ftb([
    ['운동 법칙', 'ΣF = ma', '알짜힘의 방향이 가속도의 방향'],
    ['등가속도', 'v = v₀ + at,  s = v₀t + ½at²,  v² − v₀² = 2as', 'a 일정, 일직선'],
    ['원운동', 'a = v²/r = rω²,  F = mv²/r', '속력 일정, 방향은 중심'],
    ['에너지', 'W = Fs cosθ,  Eₖ = ½mv²,  Eₚ = mgh,  ½kx²', '비보존력이 없으면 E 보존'],
    ['충격량', 'I = FΔt = Δp,  p = mv', '외력 없으면 총 p 보존']])
 + '<h4>열</h4>' + _ftb([
    ['내부 에너지', 'U = (3/2)nRT', '단원자 이상 기체, U ∝ T'],
    ['기체가 한 일', 'W = PΔV', 'P 일정, 팽창 +, 압축 −'],
    ['제1법칙', 'Q = ΔU + W', '순환: ΔU = 0, Q = W'],
    ['열효율', 'e = W/Q₁ = 1 − Q₂/Q₁', 'e < 1']])
 + '<h4>파동·소리</h4>' + _ftb([
    ['단진동', 'T = 2π√(m/k),  T = 2π√(L/g),  E = ½kA²', '단진자는 작은 각'],
    ['파동', 'v = fλ,  f = 1/T', '속력은 매질이 결정'],
    ['굴절', 'sinθ₁/sinθ₂ = v₁/v₂ = λ₁/λ₂', 'f 불변'],
    ['간섭', '보강 Δ = mλ,  상쇄 Δ = (m+½)λ', '같은 위상의 두 파원'],
    ['정상파', '줄·열린 관 f = nv/2L,  닫힌 관 (2n−1)v/4L', '끝 조건 확인'],
    ['도플러', 'f′ = f(v ± vₒ)/(v ∓ vₛ)', '가까워지면 f′ 증가'],
    ['맥놀이', 'f_b = |f₁ − f₂|', '진동수 차 작을 때']]))

_S2 = ( tb(['그래프', '읽는 법', '주의'], [
    ['v-t', '기울기 = 가속도, 넓이 = 변위', 't축 아래 넓이는 (−)변위'],
    ['a-t', '넓이 = 속도 변화', '시작 속도를 따로 확인'],
    ['F-t', '넓이 = 충격량 = Δp', '평균 힘 = 넓이/시간'],
    ['F-x', '넓이 = 한 일, 용수철은 기울기 = k', '부호 있는 면적'],
    ['P-V', '곡선 아래 넓이 = 기체가 한 일', '팽창 +, 압축 −, 순환은 폐곡선 넓이'],
    ['x-t (단진동)', '기울기 = 속도, 최댓값 = 진폭', '끝점에서 기울기 0'],
    ['y-x (파동)', '가로 길이 = 파장', '시간 고정된 순간 모양'],
    ['y-t (파동)', '가로 길이 = 주기', '한 지점의 진동'],
    ['E-x (단진동)', 'Eₖ + Eₚ = 일정', '교점은 x = ±A/√2']], f=True)
 + nt('요령', ul('가로축 이름과 단위부터 확인한다.', '기울기를 묻는지 넓이를 묻는지 먼저 정한다.', 'P-V 에서는 PV가 클수록 온도가 높고, 원점에서 멀수록 온도가 높은 등온선이다.', '파동은 두 그래프를 한 쌍으로 읽어 v = λ/T.'), 'es'))

_S3 = (tb(['틀리기 쉬운 말', '바른 개념', '이유'], [
    ['단열 = 온도 일정', '단열 = 열 출입 없음', '팽창하면 ΔU = −W 로 온도 변화'],
    ['온도 오르면 일을 한다', '일은 부피 변화로만 결정', '등적 가열은 W = 0'],
    ['열기관 e = W/Q₂', 'e = W/Q₁', '분모는 흡수한 열'],
    ['등온 팽창은 열이 필요 없다', 'Q = W > 0, 열을 흡수', 'ΔU = 0 이므로'],
    ['용수철 진자는 g에 의존', 'T = 2π√(m/k)', 'g 는 평형 위치만 이동'],
    ['단진자는 질량에 의존', 'T = 2π√(L/g)', '질량은 약분됨'],
    ['굴절하면 파장 불변', 'f 불변, λ 변화', 'v 는 매질에 의존'],
    ['도플러: 음원 소리 속력 변함', 'v 불변, λ와 f′ 변함', '매질이 v 를 결정'],
    ['충돌 모두 E 보존', '운동량만 보존이 일반적', '탄성 충돌만 Eₖ 보존'],
    ['맥놀이 = 진동수의 합', 'f_b = |f₁ − f₂|', '느린 세기 변화']], f=True))

_S4 = ('<h4>상수·환산</h4>' + tb(['항목', '값', '참고'], [
    ['중력 가속도 g', '10 m/s²', '문제에 주어진 값 우선(9.8)'],
    ['소리의 속력(공기)', '340 m/s', '온도 높으면 빨라짐'],
    ['1기압', '1.0×10⁵ Pa', '1 Pa·m³ = 1 J'],
    ['부피', '1 L = 10⁻³ m³', 'P·ΔV 계산 전에 변환'],
    ['절대 온도', 'T(K) = t(℃) + 273', '0 ℃ = 273 K'],
    ['가청 진동수', '약 20 Hz ~ 20 kHz', '초음파는 20 kHz 초과'],
    ['에너지', '1 kWh = 3.6×10⁶ J', '1 cal ≈ 4.2 J']], f=True)
 + '<h4>삼각비</h4>' + tb(['각', '30°', '37°', '45°', '53°', '60°'], [
    ['sin', '1/2', '0.6', '√2/2', '0.8', '√3/2'],
    ['cos', '√3/2', '0.8', '√2/2', '0.6', '1/2'],
    ['tan', '1/√3', '0.75', '1', '4/3', '√3']]))

SUMMARY = [
    {'title': '1 핵심 공식 정리', 'html': _S1},
    {'title': '2 그래프 해석 요령', 'html': _S2},
    {'title': '3 자주 틀리는 개념 모음', 'html': _S3},
    {'title': '4 단위·수치·삼각비 암기표', 'html': _S4},
]

# ============================================================ OX · 빈칸 원천 문장 (참, 거짓, 유형 label)
def _pairs(sub, rows):
    return [(t, f, _LAB[sub][i]) for i, t, f in rows]

PAIRS_B = {}
PAIRS_B['Ⅱ-A'] = _pairs('Ⅱ-A', [
    (0, '이상 기체의 [[내부 에너지]]는 절대 온도에 비례한다.', '이상 기체의 내부 에너지는 섭씨 온도에 비례한다.'),
    (0, '같은 종류의 이상 기체는 분자 수가 많을수록 같은 온도에서 [[내부 에너지]]가 크다.', '같은 종류의 이상 기체는 분자 수가 많을수록 같은 온도에서 내부 에너지가 작다.'),
    (1, '압력이 일정할 때 기체가 하는 일은 압력과 [[부피 변화량]]의 곱이다.', '압력이 일정할 때 기체가 하는 일은 압력과 처음 부피의 곱이다.'),
    (1, '기체가 압축될 때 기체가 한 일은 [[음(−)]]의 값이다.', '기체가 압축될 때 기체가 한 일은 양(+)의 값이다.'),
    (2, '열역학 제1법칙에서 흡수한 열은 내부 에너지 증가량과 [[기체가 한 일]]의 합이다.', '열역학 제1법칙에서 흡수한 열은 내부 에너지 증가량과 기체가 한 일의 차이다.'),
    (2, '기체가 외부에 일을 하고 열을 방출하면 내부 에너지는 [[감소]]한다.', '기체가 외부에 일을 하고 열을 방출하면 내부 에너지는 증가한다.'),
    (3, '등압 팽창에서 기체의 온도는 상승하고 기체는 열을 [[흡수]]한다.', '등압 팽창에서 기체의 온도는 상승하고 기체는 열을 방출한다.'),
    (3, '등압 과정에서 이상 기체의 부피는 절대 온도에 [[비례]]한다.', '등압 과정에서 이상 기체의 부피는 절대 온도에 반비례한다.'),
    (4, '등적 과정에서 기체가 한 일은 [[0]]이므로 흡수한 열은 모두 내부 에너지로 바뀐다.', '등적 과정에서 기체가 한 일은 0이므로 흡수한 열은 모두 일로 바뀐다.'),
    (4, '부피가 일정한 용기 속 이상 기체의 압력은 [[절대 온도]]에 비례한다.', '부피가 일정한 용기 속 이상 기체의 압력은 절대 온도에 반비례한다.'),
    (5, '등온 과정에서 이상 기체의 [[내부 에너지]] 변화는 0이다.', '등온 과정에서 이상 기체의 내부 에너지 변화는 기체가 한 일과 같다.'),
    (5, '등온 팽창하는 이상 기체는 흡수한 열을 모두 [[일]]로 바꾼다.', '등온 팽창하는 이상 기체는 흡수한 열을 모두 내부 에너지로 저장한다.'),
    (6, '단열 팽창하는 이상 기체는 열 출입이 없고 온도가 [[낮아진다]].', '단열 팽창하는 이상 기체는 열 출입이 없고 온도가 높아진다.'),
    (6, '단열 압축에서는 기체가 받은 일만큼 [[내부 에너지]]가 증가한다.', '단열 압축에서는 기체가 받은 일만큼 열을 방출한다.'),
    (7, 'P-V 그래프에서 곡선과 부피 축 사이의 [[넓이]]는 기체가 한 일과 같다.', 'P-V 그래프에서 곡선의 기울기는 기체가 한 일과 같다.'),
    (7, 'P-V 그래프에서 부피가 증가하는 과정은 기체가 [[일을 하는]] 팽창이다.', 'P-V 그래프에서 부피가 증가하는 과정은 기체가 일을 받는 압축이다.'),
    (8, 'P-V 그래프에서 수직선으로 나타나는 과정은 [[등적 과정]]이다.', 'P-V 그래프에서 수직선으로 나타나는 과정은 등압 과정이다.'),
    (8, '같은 점에서 출발한 단열 곡선은 등온 곡선보다 더 [[가파르게]] 내려간다.', '같은 점에서 출발한 단열 곡선은 등온 곡선보다 더 완만하게 내려간다.'),
    (9, '기체가 한 번 순환하면 내부 에너지 변화는 [[0]]이다.', '기체가 한 번 순환하면 내부 에너지 변화는 기체가 한 일과 같다.'),
    (9, '시계 방향으로 도는 순환 과정에서 기체가 한 [[알짜 일]]은 양(+)이다.', '시계 방향으로 도는 순환 과정에서 기체가 한 알짜 일은 음(−)이다.'),
    (10, '물질량이 일정한 이상 기체의 [[PV/T]] 값은 상태가 변해도 일정하다.', '물질량이 일정한 이상 기체의 PV/T 값은 상태가 변하면 항상 증가한다.'),
    (10, '이상 기체 상태 A, B에서 PV 값이 같으면 두 상태의 [[절대 온도]]가 같다.', '이상 기체 상태 A, B에서 PV 값이 같으면 두 상태의 압력이 같다.'),
    (11, '구름은 상승하는 공기가 [[단열 팽창]]하며 냉각되어 생긴다.', '구름은 상승하는 공기가 단열 압축되며 냉각되어 생긴다.'),
    (11, '자전거 펌프로 공기를 빠르게 누르면 단열 [[압축]]으로 온도가 오른다.', '자전거 펌프로 공기를 빠르게 누르면 단열 팽창으로 온도가 오른다.'),
    (12, 'P-T 그래프에서 원점을 지나는 직선은 [[등적 과정]]을 나타낸다.', 'P-T 그래프에서 원점을 지나는 직선은 등압 과정을 나타낸다.'),
    (12, 'V-T 그래프에서 원점을 지나는 직선은 [[등압 과정]]을 나타낸다.', 'V-T 그래프에서 원점을 지나는 직선은 등적 과정을 나타낸다.'),
    (12, 'P-V 그래프의 등온 과정은 P-T 그래프에서 [[T축에 수직]]인 선이다.', 'P-V 그래프의 등온 과정은 P-T 그래프에서 T축에 나란한 선이다.'),
    (13, '피스톤이 자유롭게 움직여 멈추었을 때 두 기체의 [[압력]]은 같다.', '피스톤이 자유롭게 움직여 멈추었을 때 두 기체의 부피는 항상 같다.'),
    (13, '온도가 같을 때 분자 수가 2N인 기체의 내부 에너지는 N인 기체의 [[2배]]이다.', '온도가 같을 때 분자 수가 2N인 기체의 내부 에너지는 N인 기체의 절반이다.'),
    (13, '열 평형에 도달한 두 기체는 [[온도]]가 같다.', '열 평형에 도달한 두 기체는 내부 에너지가 항상 같다.'),
    (14, '1기압은 약 [[1.0×10⁵ Pa]]이고 1 L는 10⁻³ m³이다.', '1기압은 약 1.0×10³ Pa이고 1 L는 10⁻³ m³이다.'),
    (14, '2×10⁵ Pa에서 부피가 3 L 팽창하면 기체가 한 일은 [[600 J]]이다.', '2×10⁵ Pa에서 부피가 3 L 팽창하면 기체가 한 일은 6000 J이다.'),
    (14, '열량 1 kcal는 약 [[4200 J]]에 해당한다.', '열량 1 kcal는 약 420 J에 해당한다.'),
    (15, 'P-V 그래프에서 등적 과정으로 압력이 증가하면 기체는 열을 [[흡수]]한다.', 'P-V 그래프에서 등적 과정으로 압력이 증가하면 기체는 열을 방출한다.'),
    (15, '등압 압축 과정에서 기체는 열을 [[방출]]한다.', '등압 압축 과정에서 기체는 열을 흡수한다.'),
    (16, '순환 과정에서 온도가 같은 두 상태의 내부 에너지는 [[같다]].', '순환 과정에서 온도가 같은 두 상태의 내부 에너지는 서로 다르다.'),
    (16, 'A→B와 B→A의 내부 에너지 변화는 크기가 같고 [[부호]]가 반대이다.', 'A→B와 B→A의 내부 에너지 변화는 크기가 같고 부호도 같다.'),
    (17, '유리관 속 솜이 타는 실험은 공기의 [[단열 압축]]으로 온도가 오르기 때문이다.', '유리관 속 솜이 타는 실험은 공기의 단열 팽창으로 온도가 오르기 때문이다.'),
    (17, '압력밥솥은 부피가 거의 일정한 상태로 가열해 [[압력]]을 높이는 장치이다.', '압력밥솥은 부피가 거의 일정한 상태로 가열해 압력을 낮추는 장치이다.'),
    (17, '스프레이를 분사하면 기체가 단열 [[팽창]]하여 온도가 내려간다.', '스프레이를 분사하면 기체가 단열 압축되어 온도가 내려간다.'),
])

PAIRS_B['Ⅱ-B'] = _pairs('Ⅱ-B', [
    (0, '열기관의 [[열효율]]은 한 순환 동안 한 일을 흡수한 열로 나눈 값이다.', '열기관의 열효율은 한 순환 동안 한 일을 방출한 열로 나눈 값이다.'),
    (0, '열기관의 열효율은 1에서 [[Q₂/Q₁]]을 뺀 값이다.', '열기관의 열효율은 1에 Q₂/Q₁을 더한 값이다.'),
    (0, '같은 Q₁을 흡수하는 열기관은 방출열이 [[작을수록]] 한 일이 크다.', '같은 Q₁을 흡수하는 열기관은 방출열이 작을수록 한 일이 작다.'),
    (1, '고열원에서 500 J을 흡수해 300 J을 방출하는 열기관이 한 [[일]]은 200 J이다.', '고열원에서 500 J을 흡수해 300 J을 방출하는 열기관이 한 일은 800 J이다.'),
    (1, '에너지 흐름도에서 열기관이 한 일은 흡수열에서 [[방출열]]을 뺀 값이다.', '에너지 흐름도에서 열기관이 한 일은 흡수열에 방출열을 더한 값이다.'),
    (2, '열효율이 [[100 %]]인 열기관은 제2법칙에 어긋나 만들 수 없다.', '열효율이 50 %인 열기관은 제2법칙에 어긋나 만들 수 없다.'),
    (2, '에너지를 공급받지 않고 일하는 [[제1종 영구기관]]은 제1법칙에 어긋난다.', '에너지를 공급받지 않고 일하는 제1종 영구기관은 제1법칙을 만족한다.'),
    (3, '마찰이 있는 면에서 물체가 미끄러져 멈추는 과정은 [[비가역]] 과정이다.', '마찰이 있는 면에서 물체가 미끄러져 멈추는 과정은 가역 과정이다.'),
    (3, '잉크 방울이 물속에서 [[확산]]하는 현상은 비가역 과정이다.', '잉크 방울이 물속에서 확산하는 현상은 가역 과정이다.'),
    (4, '열은 저절로 [[고온]]의 물체에서 저온의 물체로 이동한다.', '열은 저절로 저온의 물체에서 고온의 물체로 이동한다.'),
    (4, '고립계에서 자발적 변화가 일어나면 [[엔트로피]]는 증가한다.', '고립계에서 자발적 변화가 일어나면 엔트로피는 감소한다.'),
    (4, '냉장고가 저온의 열을 고온으로 보내려면 [[일]]을 해 주어야 한다.', '냉장고가 저온의 열을 고온으로 보내는 데는 일이 필요 없다.'),
    (5, '순환 과정의 열효율은 알짜 일을 [[흡수한 열]]의 합으로 나눈 값이다.', '순환 과정의 열효율은 알짜 일을 방출한 열의 합으로 나눈 값이다.'),
    (5, 'P-V 그래프의 순환 과정에서 알짜 일은 폐곡선의 [[넓이]]와 같다.', 'P-V 그래프의 순환 과정에서 알짜 일은 폐곡선의 둘레 길이와 같다.'),
    (6, 'Q₁ = 100 J, Q₂ = 30 J, W = 70 J 인 열기관은 [[제1법칙]]을 만족한다.', 'Q₁ = 100 J, Q₂ = 30 J, W = 80 J 인 열기관은 제1법칙을 만족한다.'),
    (6, '흡수한 열을 모두 일로 바꾸는 열기관은 [[제2법칙]]에 어긋난다.', '흡수한 열을 모두 일로 바꾸는 열기관은 제1법칙에 어긋난다.'),
    (7, '카르노 기관의 열효율은 1에서 저열원과 고열원의 [[절대 온도]] 비를 뺀 값이다.', '카르노 기관의 열효율은 1에서 저열원과 고열원의 섭씨 온도 비를 뺀 값이다.'),
    (7, '카르노 순환은 등온 팽창, 단열 팽창, 등온 압축, [[단열 압축]]으로 이루어진다.', '카르노 순환은 등온 팽창, 단열 팽창, 등온 압축, 등적 가열로 이루어진다.'),
    (7, '고열원 500 K, 저열원 300 K 인 카르노 기관의 열효율은 [[40 %]]이다.', '고열원 500 K, 저열원 300 K 인 카르노 기관의 열효율은 60 %이다.'),
    (7, '스털링 기관의 순환은 등온 과정 두 개와 [[등적 과정]] 두 개로 이루어진다.', '스털링 기관의 순환은 등온 과정 두 개와 단열 과정 두 개로 이루어진다.'),
    (8, '고온 물체가 열 Q를 잃으면 그 물체의 엔트로피는 [[감소]]한다.', '고온 물체가 열 Q를 잃으면 그 물체의 엔트로피는 증가한다.'),
    (8, '열이 고온에서 저온으로 이동할 때 전체 엔트로피 변화는 [[0보다 크다]].', '열이 고온에서 저온으로 이동할 때 전체 엔트로피 변화는 0보다 작다.'),
    (8, '400 K에서 300 K로 1200 J이 이동하면 전체 엔트로피는 [[1 J/K]] 증가한다.', '400 K에서 300 K로 1200 J이 이동하면 전체 엔트로피는 7 J/K 증가한다.'),
    (9, '입자 N개가 모두 한쪽 용기에 모일 확률은 [[(1/2)^N]]이다.', '입자 N개가 모두 한쪽 용기에 모일 확률은 1/(2N)이다.'),
    (9, '입자 10개가 모두 한쪽에 모일 확률은 약 [[1/1000]]이다.', '입자 10개가 모두 한쪽에 모일 확률은 약 1/10이다.'),
    (9, '기체는 확률이 [[높은]] 방향으로 확산한다.', '기체는 확률이 낮은 방향으로 확산한다.'),
])

PAIRS_B['Ⅲ-A'] = _pairs('Ⅲ-A', [
    (0, '단진동하는 물체의 [[진동수]]는 주기의 역수이다.', '단진동하는 물체의 진동수는 주기와 같은 값이다.'),
    (0, '진폭이 A인 단진동에서 한 번 왕복하는 동안 이동한 거리는 [[4A]]이다.', '진폭이 A인 단진동에서 한 번 왕복하는 동안 이동한 거리는 2A이다.'),
    (1, '변위가 [[최대]]인 순간 단진동하는 물체의 속력은 0이다.', '변위가 0인 순간 단진동하는 물체의 속력은 0이다.'),
    (1, '변위-시간 그래프에서 곡선의 [[기울기]]는 속도를 나타낸다.', '변위-시간 그래프에서 곡선 아래 넓이는 속도를 나타낸다.'),
    (2, '용수철 진자의 주기는 질량이 [[클수록]] 길다.', '용수철 진자의 주기는 질량이 클수록 짧다.'),
    (2, '용수철 상수가 4배가 되면 용수철 진자의 주기는 [[절반]]이 된다.', '용수철 상수가 4배가 되면 용수철 진자의 주기는 2배가 된다.'),
    (3, '단진자의 주기는 추의 [[질량]]과 무관하다.', '단진자의 주기는 추의 질량에 비례한다.'),
    (3, '줄의 길이를 4배로 하면 단진자의 주기는 [[2배]]가 된다.', '줄의 길이를 4배로 하면 단진자의 주기는 4배가 된다.'),
    (3, '달에서 단진자의 주기는 지구에서보다 [[길다]].', '달에서 단진자의 주기는 지구에서보다 짧다.'),
    (4, '용수철의 복원력의 크기는 늘어난 길이에 [[비례]]한다.', '용수철의 복원력의 크기는 늘어난 길이에 반비례한다.'),
    (4, '힘-변위 그래프에서 직선의 [[기울기]]는 용수철 상수를 나타낸다.', '힘-변위 그래프에서 직선과 축 사이의 넓이는 용수철 상수를 나타낸다.'),
    (5, '단진동에서 [[평형 위치]]를 지날 때 운동 에너지가 최대이다.', '단진동에서 끝점을 지날 때 운동 에너지가 최대이다.'),
    (5, '마찰이 없는 단진동에서 [[역학적 에너지]]는 일정하게 보존된다.', '마찰이 없는 단진동에서 역학적 에너지는 변위에 따라 증가한다.'),
    (5, '진폭이 2배가 되면 단진동의 역학적 에너지는 [[4배]]가 된다.', '진폭이 2배가 되면 단진동의 역학적 에너지는 2배가 된다.'),
    (6, '등속 원운동하는 물체의 [[정사영]]은 단진동을 한다.', '등속 원운동하는 물체의 정사영은 등속 직선 운동을 한다.'),
    (6, '등속 원운동의 반지름은 단진동의 [[진폭]]에 해당한다.', '등속 원운동의 반지름은 단진동의 주기에 해당한다.'),
])

PAIRS_B['Ⅲ-B'] = _pairs('Ⅲ-B', [
    (0, '파동의 속력은 진동수와 [[파장]]의 곱이다.', '파동의 속력은 진동수와 진폭의 곱이다.'),
    (0, '파동의 [[주기]]가 길어지면 진동수는 작아진다.', '파동의 주기가 길어지면 진동수는 커진다.'),
    (1, '변위-위치 그래프에서는 [[파장]]을, 변위-시간 그래프에서는 주기를 읽는다.', '변위-위치 그래프에서는 주기를, 변위-시간 그래프에서는 파장을 읽는다.'),
    (1, '파장이 4 m, 주기가 2 s 인 파동의 속력은 [[2 m/s]]이다.', '파장이 4 m, 주기가 2 s 인 파동의 속력은 8 m/s이다.'),
    (2, '소리는 진동 방향과 진행 방향이 나란한 [[종파]]이다.', '소리는 진동 방향과 진행 방향이 수직인 횡파이다.'),
    (2, '파동이 진행할 때 매질의 입자는 제자리에서 [[진동]]한다.', '파동이 진행할 때 매질의 입자는 파동과 함께 멀리 이동한다.'),
    (2, '빛과 지진의 S파는 진행 방향에 수직으로 진동하는 [[횡파]]이다.', '빛과 지진의 S파는 진행 방향에 나란하게 진동하는 종파이다.'),
    (3, '파동이 다른 매질로 굴절할 때 [[진동수]]는 변하지 않는다.', '파동이 다른 매질로 굴절할 때 파장은 변하지 않는다.'),
    (3, '물결파가 깊은 곳에서 얕은 곳으로 가면 파장이 [[짧아진다]].', '물결파가 깊은 곳에서 얕은 곳으로 가면 파장이 길어진다.'),
    (4, '두 파동이 중첩될 때 합성파의 변위는 각 변위의 [[합]]이다.', '두 파동이 중첩될 때 합성파의 변위는 각 변위의 곱이다.'),
    (4, '마루와 골이 만나는 곳에서는 [[상쇄 간섭]]이 일어난다.', '마루와 골이 만나는 곳에서는 보강 간섭이 일어난다.'),
    (5, '고정단에서 반사한 펄스는 위상이 [[반대]]가 된다.', '고정단에서 반사한 펄스는 위상이 그대로 유지된다.'),
    (5, '자유단에서 반사한 펄스는 위상이 [[그대로]] 유지된다.', '자유단에서 반사한 펄스는 위상이 반대로 바뀐다.'),
    (5, '같은 매질에서 반사할 때 파동의 [[속력]]은 변하지 않는다.', '같은 매질에서 반사할 때 파동의 속력은 변한다.'),
    (6, '같은 위상의 두 파원에서 경로차가 파장의 [[정수 배]]이면 보강 간섭이 일어난다.', '같은 위상의 두 파원에서 경로차가 파장의 정수 배이면 상쇄 간섭이 일어난다.'),
    (6, '같은 위상의 두 파원에서 경로차가 [[0.5λ]]인 지점은 상쇄 간섭이 일어난다.', '같은 위상의 두 파원에서 경로차가 0.5λ인 지점은 보강 간섭이 일어난다.'),
])

PAIRS_B['Ⅲ-C'] = _pairs('Ⅲ-C', [
    (0, '소리는 [[진공]] 속에서는 전달되지 않는다.', '소리는 진공 속에서도 전달된다.'),
    (0, '소리의 [[높이]]는 진동수가 클수록 높다.', '소리의 높이는 진폭이 클수록 높다.'),
    (0, '소리의 [[음색]]은 파형에 따라 달라진다.', '소리의 음색은 속력에 따라 달라진다.'),
    (1, '공기 중에서 소리의 속력은 약 [[340 m/s]]이다.', '공기 중에서 소리의 속력은 약 3400 m/s이다.'),
    (1, '메아리가 0.2초 후 돌아오면 반사면까지 거리는 [[34 m]]이다.', '메아리가 0.2초 후 돌아오면 반사면까지 거리는 68 m이다.'),
    (1, '소리의 속력은 공기의 온도가 높을수록 [[빠르다]].', '소리의 속력은 공기의 온도가 높을수록 느리다.'),
    (2, '음원이 관찰자에게 가까워지면 관찰되는 진동수는 [[커진다]].', '음원이 관찰자에게 가까워지면 관찰되는 진동수는 작아진다.'),
    (2, '도플러 효과에서 음원이 움직여도 소리의 [[속력]]은 변하지 않는다.', '도플러 효과에서 음원이 움직이면 소리의 속력은 음원 속력만큼 증가한다.'),
    (2, '음원이 관찰자에게 접근할 때 관찰자 쪽의 파장은 [[짧아진다]].', '음원이 관찰자에게 접근할 때 관찰자 쪽의 파장은 길어진다.'),
    (3, '맥놀이 진동수는 두 소리의 진동수의 [[차]]이다.', '맥놀이 진동수는 두 소리의 진동수의 합이다.'),
    (3, '440 Hz 와 444 Hz 의 소리를 함께 내면 맥놀이는 초당 [[4번]] 생긴다.', '440 Hz 와 444 Hz 의 소리를 함께 내면 맥놀이는 초당 8번 생긴다.'),
    (4, '양 끝이 고정된 줄의 기본 진동의 파장은 줄 길이의 [[2배]]이다.', '양 끝이 고정된 줄의 기본 진동의 파장은 줄 길이의 절반이다.'),
    (4, '정상파에서 이웃한 마디 사이의 거리는 [[반파장]]이다.', '정상파에서 이웃한 마디 사이의 거리는 한 파장이다.'),
    (4, '양 끝이 고정된 줄의 진동수는 기본 진동수의 [[정수 배]]이다.', '양 끝이 고정된 줄의 진동수는 기본 진동수의 홀수 배만 가능하다.'),
    (5, '한쪽이 막힌 관에서 막힌 끝은 [[마디]], 열린 끝은 배이다.', '한쪽이 막힌 관에서 막힌 끝은 배, 열린 끝은 마디이다.'),
    (5, '닫힌 관의 기본 진동의 파장은 관 길이의 [[4배]]이다.', '닫힌 관의 기본 진동의 파장은 관 길이의 2배이다.'),
    (5, '열린 관의 기본 진동수는 같은 길이의 닫힌 관의 [[2배]]이다.', '열린 관의 기본 진동수는 같은 길이의 닫힌 관의 절반이다.'),
    (6, '초음파는 진동수가 [[20 kHz]]를 넘는 소리이다.', '초음파는 진동수가 20 Hz에 못 미치는 소리이다.'),
    (6, '노이즈 캔슬링은 소음과 [[반대 위상]]의 소리를 내 상쇄시킨다.', '노이즈 캔슬링은 소음과 같은 위상의 소리를 내 상쇄시킨다.'),
    (7, '양 끝 고정 줄에 배가 3개 생기면 줄 길이는 [[1.5λ]]이다.', '양 끝 고정 줄에 배가 3개 생기면 줄 길이는 3λ이다.'),
    (7, '정상파에서 마디와 이웃한 배 사이의 거리는 [[λ/4]]이다.', '정상파에서 마디와 이웃한 배 사이의 거리는 λ/2이다.'),
])

PAIRS_B['종합'] = _pairs('종합', [
    (0, '마찰 없는 빗면에서 물체의 가속도는 [[g sinθ]]이다.', '마찰 없는 빗면에서 물체의 가속도는 g cosθ이다.'),
    (0, '마찰 없는 빗면에서 바닥에서의 속력은 물체의 [[질량]]과 무관하다.', '마찰 없는 빗면에서 바닥에서의 속력은 물체의 질량에 비례한다.'),
    (0, '마찰 없는 빗면에서 [[역학적 에너지]]는 보존된다.', '마찰 없는 빗면에서 역학적 에너지는 점점 증가한다.'),
    (1, '같은 높이에서 같은 속력으로 던진 물체는 [[방향]]과 무관하게 지면 도달 속력이 같다.', '같은 높이에서 같은 속력으로 던진 물체는 방향에 따라 지면 도달 속력이 다르다.'),
    (1, '포물선 운동의 최고점에서 속력은 [[수평 성분]]의 크기와 같다.', '포물선 운동의 최고점에서 속력은 0이다.'),
    (1, '공기 저항이 없으면 던진 물체의 수평 속도는 [[일정]]하다.', '공기 저항이 없으면 던진 물체의 수평 속도는 점점 증가한다.'),
    (2, '완전 비탄성 충돌에서 [[운동량]]은 보존되지만 운동 에너지는 감소한다.', '완전 비탄성 충돌에서 운동량은 보존되고 운동 에너지도 보존된다.'),
    (2, '충돌 후 용수철이 최대로 압축될 때 운동 에너지는 [[탄성 위치 에너지]]로 전환된다.', '충돌 후 용수철이 최대로 압축될 때 운동 에너지는 중력 위치 에너지로 전환된다.'),
    (2, '탄성 충돌에서는 운동량과 [[운동 에너지]]가 모두 보존된다.', '탄성 충돌에서는 운동량만 보존되고 운동 에너지는 보존되지 않는다.'),
    (3, '줄에 매달려 연직 원운동하는 물체의 줄의 장력은 [[최저점]]에서 가장 크다.', '줄에 매달려 연직 원운동하는 물체의 줄의 장력은 최고점에서 가장 크다.'),
    (3, '연직 원운동의 최저점에서 장력은 mg에 [[구심력]]의 크기를 더한 값이다.', '연직 원운동의 최저점에서 장력은 mg에서 구심력의 크기를 뺀 값이다.'),
    (4, '기체가 피스톤을 밀어 올리면 기체는 외부에 일을 [[한다]].', '기체가 피스톤을 밀어 올리면 기체는 외부로부터 일을 받는다.'),
    (4, '마찰로 줄어든 역학적 에너지는 [[열]]로 전환되어 전체 에너지는 보존된다.', '마찰로 줄어든 역학적 에너지는 사라져 전체 에너지가 감소한다.'),
    (5, '용수철 진자의 최대 속력은 진폭에 [[비례]]한다.', '용수철 진자의 최대 속력은 진폭에 반비례한다.'),
    (5, '질량과 진폭이 같을 때 용수철 상수가 클수록 최대 속력은 [[크다]].', '질량과 진폭이 같을 때 용수철 상수가 클수록 최대 속력은 작다.'),
    (6, '진동하는 음원이 평형 위치에서 관찰자 쪽으로 움직일 때 [[최대 진동수]]가 관찰된다.', '진동하는 음원이 평형 위치에서 관찰자 쪽으로 움직일 때 최소 진동수가 관찰된다.'),
    (6, '등속 원운동하는 음원의 진동수는 속도의 [[관찰자 방향 성분]]에 따라 달라진다.', '등속 원운동하는 음원의 진동수는 음원의 질량에 따라 달라진다.'),
    (7, '열기관의 일률은 열효율과 단위 시간당 [[흡수한 열]]의 곱이다.', '열기관의 일률은 열효율과 단위 시간당 방출한 열의 곱이다.'),
    (7, '열효율이 높을수록 같은 일을 하는 데 필요한 [[연료]]는 적다.', '열효율이 높을수록 같은 일을 하는 데 필요한 연료는 많다.'),
    (7, '열기관이 한 일을 걸린 시간으로 나눈 값이 [[일률]]이다.', '열기관이 한 일을 걸린 시간으로 곱한 값이 일률이다.'),
])
