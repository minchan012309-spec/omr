# -*- coding: utf-8 -*-
"""역학과 에너지 개념서 Ⅰ단원(Ⅰ-A ~ Ⅰ-H): 개념 정리 절(SECS_A)과 OX·빈칸 원천 쌍(PAIRS_A)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phlib import Fig, Plot, INK, GR, BL, RD, OR, GN, PU, LG
from outline import SUBS, TYPES


def _types(sub, n):
    return [t['label'] for t in TYPES if t['sub'] == sub and t['sec'] == n]


def FG(f, no, cap):
    return '<div class="fg">%s<div class="cap"><b>그림 %d</b> %s</div></div>' % (f.svg(), no, cap)


def NT(label, body, kind=''):
    return '<div class="nt%s"><span class="lb">%s</span>%s</div>' % (' ' + kind if kind else '', label, body)


def EQ(*lines):
    return ''.join('<div class="eqn">%s</div>' % l for l in lines)


def UL(*items):
    return '<ul class="l">' + ''.join('<li>%s</li>' % i for i in items) + '</ul>'


def TB(headers, rows):
    h = '<table class="tb"><thead><tr>' + ''.join('<th>%s</th>' % c for c in headers) + '</tr></thead><tbody>'
    for row in rows:
        h += '<tr>' + ''.join('<td class="b">%s</td>' % c if i == 0 else '<td>%s</td>' % c for i, c in enumerate(row)) + '</tr>'
    return h + '</tbody></table>'


def HL(s):
    return '<span class="hl">%s</span>' % s


def TWO(a, b):
    return '<div class="two-c"><div>%s</div><div>%s</div></div>' % (a, b)


def mk(sub, n, html):
    return dict(title=SUBS[sub]['secs'][n - 1], html=html, types=_types(sub, n))


def _pairs(sub, rows):
    labs = [t['label'] for t in TYPES if t['sub'] == sub]
    return [(t, f, labs[i - 1]) for (t, f, i) in rows]


# ============================================================== 그림 함수
def fig_parallelogram():
    f = Fig(320, 205)
    ox, oy = 50, 170
    f.arrow(ox, oy, 170, oy, BL, 2.6)
    f.arrow(ox, oy, ox + 45, oy - 78, GN, 2.6)
    f.arrow(ox, oy, 215, oy - 78, RD, 3)
    f.line(170, oy, 215, oy - 78, GR, 1.3, '5 4')
    f.line(ox + 45, oy - 78, 215, oy - 78, GR, 1.3, '5 4')
    f.path('M %s %s A 30 30 0 0 0 %s %s' % (ox + 30, oy, ox + 15, oy - 26), stroke=INK, sw=1.2)
    f.text(ox + 44, oy - 8, 'θ', 13, 'middle', True)
    f.text(110, 190, 'F₁', 13, 'middle', True, BL)
    f.text(ox + 12, oy - 60, 'F₂', 13, 'end', True, GN)
    f.text(162, 128, '합력 F', 13, 'end', True, RD)
    f.text(250, 112, '평행사변형의', 12, 'start', False, GR)
    f.text(250, 128, '대각선', 12, 'start', False, GR)
    return f


def fig_incline():
    f = Fig(320, 215)
    A, B, C = (30, 200), (270, 200), (270, 200 - 240 * math.tan(math.radians(30)))
    f.poly([A, B, C], '#eef2f8', GR, 1.6)
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    u, n = (c, -s), (-s, -c)
    P = (A[0] + 150 * c, A[1] - 150 * s)
    pts = [(P[0] - 24 * u[0], P[1] - 24 * u[1]), (P[0] + 24 * u[0], P[1] + 24 * u[1])]
    pts += [(pts[1][0] + 34 * n[0], pts[1][1] + 34 * n[1]), (pts[0][0] + 34 * n[0], pts[0][1] + 34 * n[1])]
    f.poly(pts, '#fff4d6', INK, 1.6)
    G = (P[0] + 17 * n[0], P[1] + 17 * n[1])
    f.circ(G[0], G[1], 2.6, INK, INK)
    f.arrow(G[0], G[1], G[0], G[1] + 66, INK, 2.4)
    f.arrow(G[0], G[1], G[0] - 33 * c, G[1] + 33 * s, RD, 2.2, '4 3')
    f.arrow(G[0], G[1], G[0] + 57 * s, G[1] + 57 * c, GN, 2.2, '4 3')
    f.arrow(G[0], G[1], G[0] + 62 * n[0], G[1] + 62 * n[1], BL, 2.4)
    f.line(G[0], G[1] + 66, G[0] - 33 * c, G[1] + 33 * s, GR, 1, '3 3')
    f.line(G[0], G[1] + 66, G[0] + 57 * s, G[1] + 57 * c, GR, 1, '3 3')
    f.text(G[0] - 8, G[1] + 84, 'mg', 13, 'end', True)
    f.text(G[0] - 33 * c - 6, G[1] + 33 * s + 8, 'mg sinθ', 12, 'end', True, RD)
    f.text(G[0] + 57 * s + 6, G[1] + 57 * c + 6, 'mg cosθ', 12, 'start', True, GN)
    f.text(G[0] + 62 * n[0] - 6, G[1] + 62 * n[1] - 4, 'N', 13, 'end', True, BL)
    f.path('M %s %s A 36 36 0 0 0 %s %s' % (A[0] + 36, A[1], A[0] + 36 * c, A[1] - 36 * s), stroke=INK, sw=1.2)
    f.text(A[0] + 52, A[1] - 6, 'θ', 13, 'middle', True)
    return f


def fig_actreact():
    f = Fig(320, 150)
    f.hatch(20, 110, 280)
    f.rect(100, 60, 60, 50, '#dbe9fb', INK, 1.6)
    f.rect(160, 60, 60, 50, '#fde2df', INK, 1.6)
    f.text(130, 91, 'A', 15, 'middle', True)
    f.text(190, 91, 'B', 15, 'middle', True)
    f.arrow(20, 85, 100, 85, GR, 2.4)
    f.text(60, 77, 'F', 13, 'middle', True, GR)
    f.arrow(160, 40, 95, 40, BL, 2.6)
    f.arrow(160, 40, 225, 40, RD, 2.6)
    f.line(160, 40, 160, 60, GR, 1, '3 3')
    f.text(156, 30, 'B가 A에 작용', 12, 'end', True, BL)
    f.text(164, 30, 'A가 B에 작용', 12, 'start', True, RD)
    f.text(160, 140, '크기 같고 방향 반대, 서로 다른 물체에 작용', 12, 'middle', False, GR)
    return f


def fig_table_pulley():
    f = Fig(320, 215)
    f.rect(30, 110, 205, 18, '#e3e9f1', GR, 1.4)
    f.rect(88, 78, 52, 32, '#dbe9fb', INK, 1.6)
    f.text(114, 99, 'm₁', 14, 'middle', True)
    f.line(140, 94, 245, 94, INK, 1.4)
    f.circ(245, 104, 10, '#fff', INK, 1.6)
    f.line(255, 104, 255, 150, INK, 1.4)
    f.rect(238, 150, 34, 34, '#fde2df', INK, 1.6)
    f.text(255, 172, 'm₂', 14, 'middle', True)
    f.arrow(114, 62, 160, 62, GN, 2.4)
    f.text(137, 54, 'a', 13, 'middle', True, GN)
    f.arrow(285, 150, 285, 190, GN, 2.4)
    f.text(298, 175, 'a', 13, 'middle', True, GN)
    f.text(172, 86, 'T', 13, 'middle', True, BL)
    f.text(267, 138, 'T', 13, 'start', True, BL)
    f.text(160, 205, 'a = m₂g ÷ (m₁ + m₂)', 13, 'middle', True, RD)
    return f


def fig_friction():
    p = Plot(320, 205, 10, 6.4, ml=50, mr=22, mt=18, mb=34)
    p.axes('F (N)', 'f (N)', (0, 5, 10), (0, 4, 5))
    p.pl([(0, 0), (5, 5)], BL, 2.6)
    p.line(p.px(5), p.py(5), p.px(5), p.py(4), GR, 1.4, '4 3')
    p.pl([(5, 4), (10, 4)], RD, 2.6)
    p.dash_to_axes(5, 5)
    p.line(p.px(0), p.py(4), p.px(5), p.py(4), GR, 1, '4 3')
    p.text(p.px(3.0), p.py(1.9), '정지 마찰력', 12, 'start', True, BL)
    p.text(p.px(3.0), p.py(1.2), 'f = F', 12, 'start', True, BL)
    p.text(p.px(5.3), p.py(5.35), '최대 정지 마찰력', 12, 'start', True, GR)
    p.text(p.px(7.5), p.py(3.2), '운동 마찰력(일정)', 12, 'middle', True, RD)
    return p


def fig_elevator():
    f = Fig(320, 200)
    f.rect(100, 20, 110, 150, '#f4f6fa', GR, 2)
    f.rect(130, 138, 50, 14, '#dbe9fb', INK, 1.4)
    f.text(155, 150, '저울', 11.5, 'middle', False, GR)
    f.circ(155, 82, 11, '#fff4d6', INK, 1.6)
    f.line(155, 93, 155, 124, INK, 1.8)
    f.line(155, 102, 141, 114, INK, 1.8)
    f.line(155, 102, 169, 114, INK, 1.8)
    f.line(155, 124, 146, 138, INK, 1.8)
    f.line(155, 124, 164, 138, INK, 1.8)
    f.arrow(155, 98, 155, 28, BL, 2.6)
    f.text(163, 40, 'N', 13, 'start', True, BL)
    f.arrow(240, 130, 240, 70, GN, 2.6)
    f.text(250, 100, 'a (위)', 12, 'start', True, GN)
    f.arrow(60, 100, 60, 160, RD, 2.6)
    f.text(60, 90, 'mg', 13, 'middle', True, RD)
    f.text(160, 190, '위로 가속: N − mg = ma → N = m(g + a)', 12, 'middle', True, GR)
    return f


def fig_vt_basic():
    p = Plot(320, 215, 5, 14, ml=50, mr=24, mt=18, mb=36)
    p.axes('t (s)', 'v (m/s)', (0, 1, 2, 3, 4), (0, 4, 8, 12))
    p.fill_under([(0, 4), (4, 12)], '#d9e8fa')
    p.line(p.px(0), p.py(4), p.px(4), p.py(4), GR, 1.2, '4 3')
    p.pl([(0, 4), (4, 12)], BL, 2.8)
    p.line(p.px(4), p.py(12), p.px(4), p.py(0), GR, 1, '4 3')
    p.text(p.px(2.6), p.py(5.6), '넓이 = 변위 s', 12, 'middle', True, BL)
    p.text(p.px(1.0), p.py(11), '기울기 = 가속도 a', 12, 'start', True, RD)
    p.text(p.px(0.3), p.py(4) - 6, 'v₀', 12, 'start', True, GR)
    p.text(p.px(4) + 4, p.py(12) - 5, 'v', 12, 'start', True, GR)
    return p


# ============================================================== Ⅰ-A 힘의 합성과 분해
SECS_A = {}

_A1 = (
    '<p>한 물체에 여러 힘이 동시에 작용할 때, 이 힘들과 똑같은 효과를 내는 하나의 힘을 ' + HL('합력(알짜힘)') + '이라 한다. '
    '힘은 크기와 방향을 모두 가진 벡터이므로 크기만 더해서는 안 되고, 화살표의 방향까지 함께 따져야 한다.</p>'
    + TWO(
        UL('같은 방향의 두 힘: 합력은 F<sub>1</sub> + F<sub>2</sub>이고 방향은 두 힘과 같다.',
           '반대 방향의 두 힘: 합력은 |F<sub>1</sub> − F<sub>2</sub>|이고 방향은 더 큰 힘 쪽이다.',
           '수직인 두 힘: 합력은 피타고라스 정리로 구한다. 3 N과 4 N이면 5 N이다.',
           '사이 각이 θ인 두 힘: ' + HL('평행사변형 법칙') + '으로 작도하고 대각선의 길이를 읽는다.')
        + EQ('F = √(F<sub>1</sub><sup>2</sup> + F<sub>2</sub><sup>2</sup> + 2F<sub>1</sub>F<sub>2</sub> cosθ)<small>사이 각 θ</small>',
             '크기가 같은 두 힘(F<sub>1</sub> = F<sub>2</sub>): F = 2F<sub>1</sub> cos(θ/2)',
             '힘의 평형: 합력 ΣF = 0'),
        FG(fig_parallelogram(), 1, '두 힘 F<sub>1</sub>, F<sub>2</sub>를 한 점에서 그린 뒤 평행사변형을 완성하면 대각선이 합력이다.'))
    + TB(['두 힘 사이 각 θ', '합력의 크기', '특징'],
         [['0°', 'F<sub>1</sub> + F<sub>2</sub>', '합력이 가장 크다'],
          ['90°', '√(F<sub>1</sub><sup>2</sup> + F<sub>2</sub><sup>2</sup>)', '성분별로 따로 계산한다'],
          ['120° (크기 같음)', 'F<sub>1</sub>', '합력의 크기가 각 힘과 같다'],
          ['180°', '|F<sub>1</sub> − F<sub>2</sub>|', '합력이 가장 작다']])
    + '<p>세 힘이 한 물체에 작용하며 평형을 이루면 그중 두 힘의 합력은 나머지 한 힘과 크기가 같고 방향이 반대이다. '
      '세 힘의 화살표를 머리와 꼬리로 이어 붙이면 <b>닫힌 삼각형</b>이 되므로, 실에 매달린 물체의 장력은 이 삼각형으로 구한다. '
      '격자 위의 벡터는 칸 수로 성분(→, ↑)을 읽어 더하거나 빼면 쉽다. 벡터의 차 A − B는 A + (−B), 즉 B의 방향을 뒤집어 더한 것이다.</p>'
    + NT('핵심 정리', UL('합력의 크기는 두 힘 사이 각이 클수록 작아지고, 0°에서 최대, 180°에서 최소이다.',
                          '평형이면 가속도가 0이므로 물체는 정지해 있거나 등속도 운동을 한다.',
                          '한 힘을 구할 때는 나머지 힘들의 합력과 크기가 같고 방향이 반대인 힘을 찾는다.'))
    + NT('혼동 주의', '<p><b>힘의 평형</b>은 한 물체에 작용하는 두 힘이 크기는 같고 방향이 반대인 경우이고, <b>작용 반작용</b>은 서로 다른 두 물체가 주고받는 한 쌍의 힘이다. '
         '또 합력이 0이라고 해서 물체가 반드시 정지해 있는 것은 아니다. 사이 각을 잴 때는 두 화살표의 <b>시작점을 한곳에 모은 뒤</b> 잰다.</p>', 'wa')
)
_A2 = (
    '<p>하나의 힘을 서로 수직인 두 방향의 힘으로 나누는 것을 ' + HL('힘의 분해') + '라 한다. 분해한 두 힘(성분)의 합력이 원래 힘과 같다. '
    '수평과 연직처럼 계산하기 쉬운 두 방향을 잡고, 힘의 화살표를 대각선으로 하는 직사각형을 그리면 된다.</p>'
    + EQ('F<sub>x</sub> = F cosθ, F<sub>y</sub> = F sinθ<small>θ는 x축과 이루는 각</small>',
         '빗면 위: 빗면 방향 mg sinθ, 빗면에 수직 mg cosθ')
    + TWO(
        '<p>경사각이 θ인 매끄러운 빗면 위의 물체에는 중력 mg, 빗면이 떠받치는 수직 항력 N이 작용한다. 중력을 빗면에 나란한 성분과 수직인 성분으로 나누면 '
        '수직 방향의 힘은 평형을 이루어 N = mg cosθ가 되고, 물체를 빗면 아래로 끄는 힘은 mg sinθ이다.</p>'
        + UL('물체가 빗면에서 정지하려면 빗면 방향 힘의 합이 0이어야 한다.',
             '각도가 커질수록 sinθ는 커지고 cosθ는 작아져 수직 항력은 줄어든다.'),
        FG(fig_incline(), 1, '빗면 위 물체에 작용하는 힘과 중력의 분해(점선은 성분)'))
    + TB(['각도 θ', 'sinθ', 'cosθ'],
         [['30°', '1/2', '√3/2'], ['37°', '0.6', '0.8'], ['45°', '√2/2', '√2/2'], ['53°', '0.8', '0.6'], ['60°', '√3/2', '1/2']])
    + '<p>도르래로 연결된 두 물체가 정지해 있으면 줄의 장력이 양쪽에서 같다. 빗면 위 물체(질량 m<sub>1</sub>)와 매달린 물체(질량 m<sub>2</sub>)가 정지한 경우 '
      '장력 T는 매달린 물체에서 T = m<sub>2</sub>g, 빗면 물체에서 T = m<sub>1</sub>g sinθ이므로 <b>m<sub>2</sub> = m<sub>1</sub> sinθ</b>가 성립한다. '
      '예를 들어 m<sub>1</sub> = 4 kg, θ = 30°이면 m<sub>2</sub> = 2 kg이고 장력은 20 N이다.</p>'
    + NT('핵심 정리', UL('각 θ와 이웃하는 성분은 cosθ, 마주 보는 성분은 sinθ를 곱한다.',
                          '빗면에서는 “빗면에 나란한 방향”과 “수직인 방향”으로 분해하고 방향마다 따로 식을 세운다.',
                          '정지 조건 하나로 질량 비나 각도를 구할 수 있다.'))
    + NT('혼동 주의', '<p>빗면에서 <b>수직 항력 N은 mg와 같지 않다.</b> N = mg cosθ이다. 또 mg sinθ와 mg cosθ는 중력의 성분일 뿐 물체에 따로 작용하는 새로운 힘이 아니므로, '
         '힘 그림에 중력과 함께 이중으로 그려 넣지 않는다. θ를 잰 위치(빗면과 수평면 사이 각)를 항상 확인한다.</p>', 'wa')
)
SECS_A['Ⅰ-A'] = [mk('Ⅰ-A', 1, _A1), mk('Ⅰ-A', 2, _A2)]

# ============================================================== Ⅰ-B 뉴턴 운동 법칙
_B1 = (
    '<p>뉴턴의 세 법칙은 힘과 운동의 관계를 설명한다.</p>'
    + UL('<b>제1법칙(관성 법칙)</b>: 물체에 작용하는 알짜힘이 0이면 정지한 물체는 계속 정지해 있고, 운동하는 물체는 등속 직선 운동을 한다. 이처럼 운동 상태를 유지하려는 성질을 ' + HL('관성') + '이라 하며 질량이 클수록 크다.',
         '<b>제2법칙(가속도 법칙)</b>: 물체의 가속도는 알짜힘에 비례하고 질량에 반비례하며, 방향은 알짜힘과 같다.',
         '<b>제3법칙(작용 반작용)</b>: 두 물체가 힘을 주고받을 때 두 힘은 크기가 같고 방향이 반대이다.')
    + EQ('F = ma<small>단위: N = kg·m/s²</small>', 'a = F ÷ m,  a ∝ F (m 일정),  a ∝ 1/m (F 일정)')
    + TWO(
        '<p>질량이 2 kg인 물체에 알짜힘 6 N이 작용하면 가속도는 3 m/s²이다. 같은 힘을 질량 3 kg인 물체에 작용하면 가속도는 2 m/s²가 되어 질량이 클수록 가속되기 어렵다. '
        'a-F 그래프는 원점을 지나는 직선이고 기울기가 1/m이며, a-m 그래프는 반비례 곡선이다.</p>',
        FG(fig_actreact(), 1, '접촉한 두 물체 A, B가 서로 미는 작용 반작용(크기 같고 방향 반대)'))
    + TB(['법칙', '핵심 내용', '일상 예'],
         [['제1법칙', '알짜힘 0 → 운동 상태 유지', '급정거 때 몸이 앞으로 쏠림'],
          ['제2법칙', 'F = ma', '같은 힘에서 가벼운 수레가 더 빨리 가속됨'],
          ['제3법칙', '작용과 반작용은 크기 같고 방향 반대', '벽을 밀면 내가 뒤로 밀림']])
    + NT('핵심 정리', UL('알짜힘이 한 방향이면 가속도도 그 방향이다. 속도의 방향과 같을 필요는 없다.',
                          '작용 반작용은 항상 크기가 같다. 질량이 달라도 마찬가지이다.',
                          '관성은 힘이 아니라 물체의 성질이며, 질량으로 정해진다.'))
    + NT('혼동 주의', '<p>작용 반작용은 <b>서로 다른 두 물체</b>에 작용하므로 합력을 구할 때 상쇄시키지 않는다. 한 물체에 작용하는 두 힘이 평형이면 그것은 작용 반작용이 아니라 힘의 평형이다. '
         '또 “운동 방향으로 힘이 작용해야 계속 운동한다”는 생각은 틀렸다. 등속 운동에는 알짜힘이 필요 없다.</p>', 'wa')
)
_B2 = (
    '<p>여러 물체가 줄로 연결되어 있으면 ' + HL('물체마다 운동 방정식을 따로 세운 뒤') + ' 연립한다. 줄이 늘어나지 않고 질량이 없으면 연결된 물체의 가속도의 크기는 같고, 줄의 장력은 줄 어디에서나 같다.</p>'
    + EQ('물체마다: 알짜힘 = 질량 × 가속도', '한 덩어리로 보면: 외력의 합 = (전체 질량) × a')
    + TWO(
        '<p><b>책상 위 물체와 매달린 물체.</b> 마찰이 없는 책상 위의 m<sub>1</sub>과 도르래에 매달린 m<sub>2</sub>를 생각하자. '
        '운동 방향으로 m<sub>2</sub>: m<sub>2</sub>g − T = m<sub>2</sub>a, m<sub>1</sub>: T = m<sub>1</sub>a이다. 두 식을 더하면 a = m<sub>2</sub>g ÷ (m<sub>1</sub> + m<sub>2</sub>), 장력 T = m<sub>1</sub>m<sub>2</sub>g ÷ (m<sub>1</sub> + m<sub>2</sub>)이다.</p>'
        + '<p>예: m<sub>1</sub> = 3 kg, m<sub>2</sub> = 2 kg이면 a = 20/5 = 4 m/s², T = 12 N이다. 장력은 m<sub>2</sub>g = 20 N보다 작다.</p>',
        FG(fig_table_pulley(), 1, '마찰 없는 책상 위 물체 m<sub>1</sub>과 매달린 물체 m<sub>2</sub>'))
    + TB(['상황', '가속도 a', '장력 T'],
         [['수평면에서 줄로 연결된 두 물체(힘 F로 당김)', 'F ÷ (m<sub>1</sub> + m<sub>2</sub>)', '뒤 물체: m<sub>2</sub>a'],
          ['아트우드 장치(m<sub>1</sub> &gt; m<sub>2</sub>)', '(m<sub>1</sub> − m<sub>2</sub>)g ÷ (m<sub>1</sub> + m<sub>2</sub>)', '2m<sub>1</sub>m<sub>2</sub>g ÷ (m<sub>1</sub> + m<sub>2</sub>)'],
          ['마찰 없는 빗면(경사각 θ)', 'g sinθ', '—']])
    + '<p>매끄러운 빗면에서 질량과 관계없이 물체의 가속도는 g sinθ이다. 예를 들어 θ = 30°이면 a = 5 m/s²이다. 빗면의 물체가 줄로 연결되어 있다면 줄 방향으로 알짜힘을 쓴다. '
      '표·그림 자료가 주어지면 서로 다른 조건의 가속도와 힘을 F = ma에 대입하여 질량 비나 힘의 크기를 비교한다.</p>'
    + NT('핵심 정리', UL('줄로 연결된 물체는 가속도의 크기가 같다. 단, 방향은 줄을 따라 바뀔 수 있다.',
                          '먼저 운동 방향을 정하고, 그 방향을 + 로 하여 각 물체의 식을 세운다.',
                          '장력은 가속하는 물체의 식에서 구한다. 이때 구한 T를 반대쪽 물체의 식에 다시 쓴다.'))
    + NT('혼동 주의', '<p>매달린 물체가 가속되면 장력은 <b>mg가 아니다.</b> 아래로 가속되는 물체는 T &lt; mg이다. '
         '아트우드 장치에서도 장력은 두 물체의 무게 사이의 값을 갖는다. 전체 질량로 a를 구할 때는 내부의 장력은 서로 상쇄되어 식에 나타나지 않는다.</p>', 'wa')
)
_B3 = (
    '<p><b>마찰력</b>은 접촉면에서 운동을 방해하는 방향으로 작용하는 힘이다. 물체가 미끄러지지 않을 때는 ' + HL('정지 마찰력') + '이 외력과 크기가 같아 물체가 정지해 있고, '
    '외력이 최대 정지 마찰력을 넘으면 미끄러지기 시작하여 ' + HL('운동 마찰력') + '이 작용한다.</p>'
    + EQ('f<sub>운동</sub> = μ<sub>k</sub>N,  f<sub>최대 정지</sub> = μ<sub>s</sub>N', '수평면: N = mg,  알짜힘 = F − f = ma')
    + TWO(
        UL('정지 마찰력은 외력에 따라 변하며, 0부터 최대값까지의 값을 가진다.',
           '운동 마찰력은 접촉면의 넓이, 속력과 관계없이 μ<sub>k</sub>N으로 거의 일정하다.',
           '보통 μ<sub>s</sub> &gt; μ<sub>k</sub>이다.')
        + '<p>질량 2 kg인 물체가 수평면 위를 μ<sub>k</sub> = 0.2인 면에서 미끄러지면 f = 0.2 × 20 = 4 N이다. 12 N으로 당기면 알짜힘 8 N, a = 4 m/s²이다.</p>',
        FG(fig_friction(), 1, '물체를 당기는 힘 F에 따른 마찰력 f의 변화'))
    + '<p><b>관성력.</b> 가속하는 관찰자(엘리베이터 안의 사람)의 입장에서는 가속도와 반대 방향의 힘이 작용하는 것처럼 느껴진다. 이를 관성력이라 하며 크기는 ma이다. '
      '저울이 가리키는 눈금은 저울이 물체를 떠받치는 힘, 즉 수직 항력 N이다.</p>'
    + TB(['엘리베이터의 운동', '질량 m인 사람의 N', '눈금 비교'],
         [['정지 또는 등속', 'mg', '실제 무게와 같다'],
          ['a로 가속 상승 / 감속 하강', 'm(g + a)', '더 무겁게 느낀다'],
          ['a로 가속 하강 / 감속 상승', 'm(g − a)', '더 가볍게 느낀다'],
          ['줄이 끊겨 자유 낙하(a = g)', '0', '무중력 상태처럼 느낀다']])
    + FG(fig_elevator(), 2, '위쪽으로 가속하는 엘리베이터 속 사람에게 작용하는 힘')
    + NT('핵심 정리', UL('눈금은 “속도”가 아니라 <b>가속도의 방향</b>으로 결정된다. 위로 가속이면 무겁고 아래로 가속이면 가볍다.',
                          '운동 마찰력이 있을 때의 알짜힘은 (당기는 힘 − 마찰력)이다.',
                          '눈금이 kg중이면 N 값을 10으로 나눈 값이다.'))
    + NT('혼동 주의', '<p>엘리베이터가 <b>올라가는 중</b>이라고 해서 눈금이 늘 커지는 것은 아니다. 등속이면 mg이고, 감속하며 올라가면 mg보다 작다. '
         '정지 마찰력은 항상 μ<sub>s</sub>N이 아니다. 최대값이 μ<sub>s</sub>N이고 실제 값은 외력과 같다.</p>', 'wa')
)
SECS_A['Ⅰ-B'] = [mk('Ⅰ-B', 1, _B1), mk('Ⅰ-B', 2, _B2), mk('Ⅰ-B', 3, _B3)]
