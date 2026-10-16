# -*- coding: utf-8 -*-
"""Ⅱ-B 열기관과 열역학 제2법칙 (ph077~ph083) 생성기.  e = W/Q1 = 1 − Q2/Q1,  W = Q1 − Q2."""
from phlib import *
import math
from fractions import Fraction
from types_t1 import (T, num, mco, mc_list, ratio_str, fr_str, pick_stmts, sgn, UP, DN, ZE, rand_sch, pv_fig, unit_note,
                      pre_str, vol_str, area_seg, seg_energy, jstr, _cycle, _cyc_fig, cyc_work, _unit_join)


def pct(x):
    return num(float(x) * 100, 1) + ' %'

def eng_fig(q1='Q₁', w='W', q2='Q₂', t1='', t2='', wd=300, ht=214):
    f = Fig(wd, ht)
    f.rect(85, 8, 130, 34, '#fde8e6', RD, 1.8, 4); f.text(150, 30, '고열원' + (' ' + t1 if t1 else ''), 13.5, 'middle', True, RD)
    f.rect(85, 174, 130, 34, '#e3effb', BL, 1.8, 4); f.text(150, 196, '저열원' + (' ' + t2 if t2 else ''), 13.5, 'middle', True, BL)
    f.circ(150, 108, 32, '#f4f4f0', INK, 2); f.text(150, 113, '열기관', 13.5, 'middle', True, INK)
    f.arrow(150, 43, 150, 74, RD, 3); f.text(142, 62, q1, 13, 'end', True, RD)
    f.arrow(182, 108, 262, 108, GN, 3); f.text(222, 97, w, 13, 'middle', True, GN)
    f.arrow(150, 141, 150, 172, BL, 3); f.text(142, 162, q2, 13, 'end', True, BL)
    return f.svg()

def eng_fig2(a, b, wd=330, ht=206):
    """두 열기관 (가), (나): a, b = (q1, w, q2) 문자열."""
    f = Fig(wd, ht)
    for ox, (q1, w, q2), nm in ((0, a, '(가)'), (165, b, '(나)')):
        f.rect(ox + 38, 6, 90, 26, '#fde8e6', RD, 1.6, 4); f.text(ox + 83, 24, '고열원', 12.5, 'middle', True, RD)
        f.rect(ox + 38, 168, 90, 26, '#e3effb', BL, 1.6, 4); f.text(ox + 83, 186, '저열원', 12.5, 'middle', True, BL)
        f.circ(ox + 83, 99, 26, '#f4f4f0', INK, 1.8); f.text(ox + 83, 103, nm, 13, 'middle', True, INK)
        f.arrow(ox + 83, 33, ox + 83, 71, RD, 2.6); f.text(ox + 76, 56, q1, 12, 'end', True, RD)
        f.arrow(ox + 109, 99, ox + 158, 99, GN, 2.6); f.text(ox + 134, 90, w, 12, 'middle', True, GN)
        f.arrow(ox + 83, 126, ox + 83, 166, BL, 2.6); f.text(ox + 76, 152, q2, 12, 'end', True, BL)
    return f.svg()

def J_(x): return '%s J' % num(x)


# ============================================================ ph077 열효율 계산
@T('ph077')
def g077(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e', 'f', 'g'])
    Q1 = r.choice([200, 300, 400, 500, 600, 800, 1000, 1200, 2000])
    e = Fraction(r.choice([10, 20, 25, 30, 40, 50, 60, 15, 35, 45]), 100)
    W = Q1 * e; Q2 = Q1 - W
    if W.denominator != 1: return None
    W, Q2 = int(W), int(Q2)
    assert W + Q2 == Q1 and abs(Fraction(W, Q1) - (1 - Fraction(Q2, Q1))) == 0
    if form == 'a':
        body = P('어떤 열기관이 한 번 순환하는 동안 고열원에서 %d J의 열을 흡수하고 저열원으로 %d J의 열을 방출한다. 이 열기관의 열효율은?' % (Q1, Q2))
        wr = [pct(Fraction(Q2, Q1)), pct(Fraction(Q2, W)) if W else '0 %', pct(Fraction(W, Q2)), pct(Fraction(Q1, Q2)), pct(1 - e + Fraction(1, 10))]
        return mc(body, pct(e), wr, r=r, lv='하', fam='a', sort='shuf',
                  steps=['한 번 순환하는 동안 한 일 W = Q%s − Q%s = %d − %d = %d J' % (sub(1), sub(2), Q1, Q2, W), 'e = W/Q%s = %d/%d = %s' % (sub(1), W, Q1, pct(e))],
                  core='열효율 e = W/Q₁ = 1 − Q₂/Q₁.', point='흡열량과 방열량으로 일을 구해 열효율을 계산한다.')
    if form == 'b':
        body = P('열효율이 %s인 열기관이 한 번 순환하는 동안 고열원에서 %d J의 열을 흡수한다. 이 열기관이 한 일 W는?' % (pct(e), Q1))
        wr = [Q2, Q1, int(Q1 * e * 2), Q1 + W, int(Q1 / e) if (Q1 / e) == int(Q1 / e) else W + 50, W * 10 if False else int(Q1 * (1 - e)) + 50]
        return mc(body, J_(W), [J_(x) for x in wr], r=r, lv='하', fam='b', steps=['e = W/Q%s 에서 W = eQ%s = %s × %d = %d J' % (sub(1), sub(1), num(float(e)), Q1, W)], core='W = e·Q₁.', point='열효율 정의를 이용해 일을 구한다.')
    if form == 'c':
        body = P('열효율이 %s인 열기관이 한 번 순환하는 동안 고열원에서 %d J의 열을 흡수한다. 저열원으로 방출하는 열량 Q%s는?' % (pct(e), Q1, sub(2)))
        wr = [W, Q1, Q1 + W, int(Q1 * e / (1 - e)) if (Q1 * e / (1 - e)) == int(Q1 * e / (1 - e)) else W + 100, Q2 + 100]
        return mc(body, J_(Q2), [J_(x) for x in wr], r=r, lv='중', fam='c',
                  steps=['W = eQ%s = %s × %d = %d J' % (sub(1), num(float(e)), Q1, W), 'Q%s = Q%s − W = %d − %d = %d J' % (sub(2), sub(1), Q1, W, Q2)], core='Q₂ = Q₁(1 − e).', point='일을 구한 뒤 에너지 보존으로 방열량을 구한다.')
    if form == 'd':
        a_, b_ = Q1 // math.gcd(Q1, Q2), Q2 // math.gcd(Q1, Q2)
        body = P('어떤 열기관이 고열원에서 흡수한 열량 Q%s과 저열원으로 방출한 열량 Q%s의 비가 Q%s : Q%s = %d : %d이다. 이 열기관의 열효율은?' % (sub(1), sub(2), sub(1), sub(2), a_, b_))
        wr = [pct(Fraction(b_, a_)), pct(Fraction(b_, a_ - b_)), pct(Fraction(a_ - b_, b_)), pct(Fraction(a_, b_)) if a_ < b_ * 2 else pct(Fraction(a_, a_ + b_)), pct(Fraction(b_, a_ + b_))]
        return mc(body, pct(e), wr, r=r, lv='중', fam='d', sort='shuf', steps=['Q%s = %d k, Q%s = %d k 라 하면 W = %d k' % (sub(1), a_, sub(2), b_, a_ - b_), 'e = W/Q%s = %d/%d = %s' % (sub(1), a_ - b_, a_, pct(e))], core='e = 1 − Q₂/Q₁.', point='열량의 비로 열효율을 구한다.')
    if form == 'e':
        body = P('한 번 순환하는 동안 %d J의 일을 하는 열기관의 열효율이 %s이다. 이 열기관이 고열원에서 흡수하는 열량 Q%s은?' % (W, pct(e), sub(1)))
        wr = [Q2, int(W * e) if (W * e) == int(W * e) else W + 100, W + Q1, W // 2 if W % 2 == 0 else W + 50, Q1 + 200]
        return mc(body, J_(Q1), [J_(x) for x in wr], r=r, lv='중', fam='e', steps=['e = W/Q%s 에서 Q%s = W/e = %d / %s = %d J' % (sub(1), sub(1), W, num(float(e)), Q1)], core='Q₁ = W/e.', point='열효율 정의를 거꾸로 이용한다.')
    if form == 'f':   # 단위 kJ
        body = P('열기관이 한 번 순환하는 동안 고열원에서 %s kJ의 열을 흡수하고 %s kJ의 일을 한다. 저열원으로 방출하는 열량과 열효율을 옳게 짝지은 것은?' % (num(Q1 / 1000), num(W / 1000)))
        right = '%s kJ, %s' % (num(Q2 / 1000), pct(e))
        wr = ['%s kJ, %s' % (num(Q2 / 1000), pct(1 - e)), '%s kJ, %s' % (num(W / 1000), pct(e)), '%s kJ, %s' % (num(Q1 / 1000 + W / 1000), pct(e)), '%s kJ, %s' % (num(Q2 / 1000), pct(Fraction(Q2, Q1) + Fraction(1, 10))), '%s kJ, %s' % (num((Q1 + W) / 1000), pct(1 - e))]
        return mc(body, right, wr, r=r, lv='중', fam='f', sort='shuf', steps=['Q%s = Q%s − W = %s − %s = %s kJ' % (sub(2), sub(1), num(Q1 / 1000), num(W / 1000), num(Q2 / 1000)), 'e = W/Q%s = %s' % (sub(1), pct(e))], core='W = Q₁ − Q₂, e = W/Q₁.', point='kJ 단위로도 같은 식을 적용한다.')
    # g: 두 열기관 비교
    Q1b = r.choice([200, 400, 500, 600, 1000]); eb = Fraction(r.choice([10, 20, 25, 30, 40, 50]), 100)
    Wb = Q1b * eb
    if Wb.denominator != 1 or eb == e: return None
    Wb = int(Wb)
    body = P('열기관 A는 고열원에서 %d J을 흡수해 %d J의 일을 하고, 열기관 B는 고열원에서 %d J을 흡수해 저열원으로 %d J을 방출한다. 열효율이 더 큰 열기관과 그 값을 옳게 짝지은 것은?' % (Q1, W, Q1b, Q1b - Wb))
    ea, eb_ = e, eb
    bigger = 'A' if ea > eb_ else 'B'
    right = '%s, %s' % (bigger, pct(max(ea, eb_)))
    wr = ['%s, %s' % (('B' if bigger == 'A' else 'A'), pct(max(ea, eb_))), '%s, %s' % (bigger, pct(min(ea, eb_))), '%s, %s' % (('B' if bigger == 'A' else 'A'), pct(min(ea, eb_))), '같다, %s' % pct(ea), 'A, %s' % pct(1 - ea), 'B, %s' % pct(1 - eb_)]
    return mc(body, right, wr, r=r, lv='상', fam='g', sort='shuf', steps=['e%s = %d/%d = %s' % (sub('A'), W, Q1, pct(ea)), 'B의 일 W = %d − %d = %d J, e%s = %d/%d = %s' % (Q1b, Q1b - Wb, Wb, sub('B'), Wb, Q1b, pct(eb_)), '따라서 %s' % right], core='열효율은 흡수한 열 중 일로 바뀐 비율이다.', point='두 열기관의 열효율을 각각 구해 비교한다.')


# ============================================================ ph078 열기관의 에너지 흐름도
@T('ph078')
def g078(r, k):
    form = r.choice(['a', 'a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    Q1 = r.choice([100, 200, 300, 400, 500, 600, 800, 1000, 1200])
    e = Fraction(r.choice([10, 20, 25, 30, 40, 50, 60, 75]), 100)
    W = Q1 * e
    if W.denominator != 1: return None
    W = int(W); Q2 = Q1 - W
    if W <= 0 or Q2 <= 0: return None
    unk = r.choice(['W', 'Q2', 'Q1'])
    if form in ('a', 'b'):
        labs = {'Q1': 'Q₁=%d J' % Q1, 'W': 'W=%d J' % W, 'Q2': 'Q₂=%d J' % Q2}
        shown = dict(labs); shown[unk] = {'Q1': 'Q₁=?', 'W': 'W=?', 'Q2': 'Q₂=?'}[unk]
        fig = FIG(eng_fig(shown['Q1'], shown['W'], shown['Q2']), '64%')
        if form == 'a':
            ans = {'Q1': Q1, 'W': W, 'Q2': Q2}[unk]
            name = {'Q1': '고열원에서 흡수하는 열량 Q₁', 'W': '열기관이 한 일 W', 'Q2': '저열원으로 방출하는 열량 Q₂'}[unk]
            body = P('그림은 한 열기관이 한 번 순환하는 동안의 에너지 흐름을 나타낸 것이다. %s의 값은?' % name) + fig
            known = [x for x in ('Q1', 'W', 'Q2') if x != unk]
            wr = [Q1 + W if unk != 'Q1' else Q2 + W + 50, abs(Q2 - W) if abs(Q2 - W) != ans else ans + 100, Q1 if unk != 'Q1' else W, W if unk != 'W' else Q2, Q2 if unk != 'Q2' else Q1, ans + 100, ans // 2 + 20]
            ex = {'Q1': 'Q₁ = W + Q₂ = %d + %d = %d J' % (W, Q2, Q1), 'W': 'W = Q₁ − Q₂ = %d − %d = %d J' % (Q1, Q2, W), 'Q2': 'Q₂ = Q₁ − W = %d − %d = %d J' % (Q1, W, Q2)}[unk]
            return mc(body, J_(ans), [J_(x) for x in wr], r=r, lv='하', fam='a', steps=['한 번 순환하면 내부 에너지 변화가 없으므로 Q₁ = W + Q₂ 이다.', ex], core='열기관에서 Q₁ = W + Q₂ (에너지 보존).', point='에너지 흐름도에서 모르는 양을 구한다.')
        # b: 효율 퍼센트
        body = P('그림은 한 열기관이 한 번 순환하는 동안의 에너지 흐름을 나타낸 것이다. 이 열기관의 열효율은?') + FIG(eng_fig(labs['Q1'], labs['W'], '?' if False else 'Q₂=?'), '64%') if False else P('그림은 한 열기관이 한 번 순환하는 동안의 에너지 흐름을 나타낸 것이다. 이 열기관의 열효율은?') + FIG(eng_fig('Q₁=%d J' % Q1, 'W=?', 'Q₂=%d J' % Q2), '64%')
        wr = [pct(Fraction(Q2, Q1)), pct(Fraction(W, Q2)), pct(Fraction(Q1, W)) if False else pct(Fraction(Q2, W)), pct(Fraction(Q1 - Q2, Q1 + Q2)), pct(e + Fraction(1, 10))]
        return mc(body, pct(e), wr, r=r, lv='중', fam='b', sort='shuf', steps=['W = Q₁ − Q₂ = %d − %d = %d J' % (Q1, Q2, W), 'e = W/Q₁ = %d/%d = %s' % (W, Q1, pct(e))], core='e = (Q₁ − Q₂)/Q₁.', point='흐름도에서 일을 구하고 열효율을 계산한다.')
    if form == 'c':
        Q1b = r.choice([200, 400, 500, 800, 1000]); eb = Fraction(r.choice([20, 25, 30, 40, 50]), 100); Wb = Q1b * eb
        if Wb.denominator != 1 or eb == e: return None
        Wb = int(Wb); Q2b = Q1b - Wb
        fig = FIG(eng_fig2(('Q₁=%d J' % Q1, 'W=%d J' % W, 'Q₂=?'), ('Q₁=%d J' % Q1b, 'W=?', 'Q₂=%d J' % Q2b)), '78%')
        body = P('그림은 두 열기관 (가), (나)가 한 번 순환하는 동안의 에너지 흐름을 나타낸 것이다. (가), (나)의 열효율을 각각 e%s, e%s라 할 때 옳은 것은?' % (sub('가'), sub('나'))) + fig
        e1, e2 = e, eb
        sg = '>' if e1 > e2 else '<'
        right = 'e%s %s e%s' % (sub('가'), sg, sub('나'))
        wr = ['e%s %s e%s' % (sub('가'), '<' if sg == '>' else '>', sub('나')), 'e%s = e%s' % (sub('가'), sub('나')), 'e%s = 2e%s' % (sub('가'), sub('나')), 'e%s = 2e%s' % (sub('나'), sub('가')), 'e%s = 0' % sub('나')]
        return mc(body, right, wr, r=r, lv='상', fam='c', sort='shuf', steps=['(가) : e = W/Q₁ = %d/%d = %s' % (W, Q1, pct(e1)), '(나) : W = %d − %d = %d J, e = %d/%d = %s' % (Q1b, Q2b, Wb, Wb, Q1b, pct(e2)), '따라서 ' + right], core='e = W/Q₁.', point='모르는 양을 채운 뒤 열효율을 비교한다.')
    if form == 'd':   # 퍼센트로 주어진 효율로 빈칸
        fig = FIG(eng_fig('Q₁=%d J' % Q1, 'W=?', 'Q₂=?'), '64%')
        body = P('그림은 열효율이 %s인 열기관이 한 번 순환하는 동안의 에너지 흐름을 나타낸 것이다. 이 열기관이 하는 일 W와 저열원으로 방출하는 열량 Q₂를 옳게 짝지은 것은?' % pct(e)) + fig
        right = '%d J, %d J' % (W, Q2)
        wr = ['%d J, %d J' % (Q2, W), '%d J, %d J' % (W, Q1 + W), '%d J, %d J' % (Q1, Q2), '%d J, %d J' % (W, W), '%d J, %d J' % (Q2, Q2)]
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf', steps=['W = eQ₁ = %s × %d = %d J' % (num(float(e)), Q1, W), 'Q₂ = Q₁ − W = %d − %d = %d J' % (Q1, W, Q2)], core='W = eQ₁, Q₂ = Q₁ − W.', point='열효율로 일과 방열량을 구한다.')
    # e: 두 번 순환/ 퍼센트 해석
    n = r.choice([2, 3, 5, 10])
    body = P('그림은 한 열기관이 한 번 순환하는 동안의 에너지 흐름을 나타낸 것이다. 이 열기관이 %d번 순환하는 동안 저열원으로 방출하는 열량은?' % n) + FIG(eng_fig('Q₁=%d J' % Q1, 'W=%d J' % W, 'Q₂=?'), '64%')
    wr = [Q2, W * n, Q1 * n, (Q1 + W) * n, Q2 * n + 100]
    return mc(body, J_(Q2 * n), [J_(x) for x in wr], r=r, lv='중', fam='e', steps=['한 번 순환 : Q₂ = Q₁ − W = %d − %d = %d J' % (Q1, W, Q2), '%d번 순환 : %d × %d = %d J' % (n, n, Q2, n * Q2)], core='한 번 순환 동안 Q₂ = Q₁ − W.', point='한 번 순환의 값에 순환 횟수를 곱한다.')


# ============================================================ ph079 열효율과 영구기관
_B79 = [
    ('열효율이 100 %인 열기관은 열역학 제2법칙에 의해 만들 수 없다.', True, '열을 모두 일로 바꾸는 열기관은 불가능하다(켈빈-플랑크 표현).', 'e100'),
    ('실제 열기관의 열효율은 항상 100 %보다 작다.', True, '일부 열은 반드시 저열원으로 방출되어야 한다.', 'elt'),
    ('열기관은 고열원에서 흡수한 열을 전부 일로 바꿀 수 있다.', False, '저열원으로 열을 방출하는 부분이 반드시 있다. e < 1.', 'allW'),
    ('저열원이 없어도 고열원 하나만으로 계속 일을 하는 열기관을 만들 수 있다.', False, '이는 제2종 영구기관으로 열역학 제2법칙에 위배된다.', 'one'),
    ('제2종 영구기관은 열역학 제2법칙에 위배되어 만들 수 없다.', True, '열효율 100 %의 열기관이기 때문이다.', 'perp2'),
    ('제1종 영구기관은 에너지를 공급받지 않고 일을 계속하는 기관으로, 에너지 보존 법칙에 위배된다.', True, '에너지가 새로 생겨날 수 없다.', 'perp1'),
    ('제2종 영구기관은 에너지 보존 법칙에는 위배되지 않는다.', True, '열을 일로 바꿀 뿐 에너지의 총량은 변하지 않지만 제2법칙을 어긴다.', 'perp2b'),
    ('열기관이 한 번 순환하는 동안 한 일은 Q₁ + Q₂ 이다.', False, 'W = Q₁ − Q₂ (Q₂는 방출한 열량의 크기).', 'wsum'),
    ('열효율이 같은 두 열기관은 같은 양의 열을 흡수하면 같은 양의 일을 한다.', True, 'W = eQ₁ 이므로 e와 Q₁이 같으면 W가 같다.', 'same'),
    ('열기관의 열효율은 한 일을 방출한 열량으로 나눈 값이다.', False, '열효율은 한 일을 흡수한 열량 Q₁로 나눈 값이다.', 'def'),
    ('방열량 Q₂가 작을수록 같은 Q₁에서 열효율이 크다.', True, 'e = 1 − Q₂/Q₁.', 'q2'),
    ('열기관이 방출하는 열은 낭비되는 에너지이며 에너지 보존 법칙에 위배된다.', False, '방출된 열도 에너지이며 Q₁ = W + Q₂ 로 에너지는 보존된다.', 'waste'),
    ('열효율이 40 %인 열기관은 흡수한 열의 60 %를 저열원으로 방출한다.', True, 'Q₂/Q₁ = 1 − e = 0.6.', 'e40'),
    ('기술이 발달하면 열효율이 100 %인 열기관도 만들 수 있다.', False, '기술의 문제가 아니라 열역학 제2법칙에 의한 원리적 한계이다.', 'tech'),
    ('열기관이 한 번 순환한 뒤 기체의 내부 에너지는 처음과 같다.', True, '처음 상태로 돌아오므로 ΔU = 0, 따라서 W = Q₁ − Q₂ 이다.', 'dU0'),
    ('흡수한 열이 같을 때 한 일이 큰 열기관일수록 열효율이 크다.', True, 'e = W/Q₁ 에서 Q₁이 같으면 W에 비례한다.', 'Wbig'),
    ('열효율이 높은 열기관은 같은 일을 하는 데 더 적은 열을 흡수한다.', True, 'Q₁ = W/e.', 'less'),
    ('주위의 열을 흡수하여 이를 모두 일로 바꾸는 배는 에너지 보존 법칙에는 맞지만 열역학 제2법칙에 위배된다.', True, '열을 단일 열원에서 흡수해 전부 일로 바꾸는 장치는 제2종 영구기관이다.', 'ship'),
]

@T('ph079')
def g079(r, k):
    form = r.choice(['a', 'a', 'a', 'b', 'b', 'c', 'd'])
    if form == 'a':
        stm = pick_stmts(r, _B79)
        return bogi('열기관과 열효율에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv=r.choice(['하','중']), fam='a', core='열효율 e = W/Q₁ < 1. 열효율 100 %의 열기관(제2종 영구기관)은 열역학 제2법칙에 위배된다.', point='열기관의 열효율과 영구기관의 의미를 설명한다.')
    if form == 'b':   # 가능/불가능 열기관
        cases = []
        def add(q1, w, q2): cases.append((q1, w, q2))
        base = r.choice([(500, 200, 300), (400, 100, 300), (600, 300, 300), (800, 200, 600), (1000, 400, 600), (200, 50, 150)])
        q1, w, q2 = base
        imp = r.choice(['e100', 'e100', 'gt', 'first'])
        descs = []
        if imp == 'e100':
            bad = (q1, q1, 0); why = '열을 모두 일로 바꾸므로 열효율 100 %이다(제2법칙 위배).'
        elif imp == 'gt':
            bad = (q1, q1 + 100, 0); why = '흡수한 열보다 많은 일을 하므로 에너지 보존 법칙에 위배된다.'
        else:
            bad = (q1, w, q2 - 100); why = 'Q₁ ≠ W + Q₂ 이므로 에너지 보존 법칙에 위배된다.'
        goods = r.sample([(500, 200, 300), (400, 100, 300), (600, 300, 300), (800, 200, 600), (1000, 400, 600), (200, 50, 150), (300, 100, 200), (900, 300, 600)], 4)
        pos = r.randrange(5)
        allc = goods[:pos] + [bad] + goods[pos:]
        labs = ['(가)', '(나)', '(다)', '(라)', '(마)']
        rows = [[labs[i], c[0], c[1], c[2]] for i, c in enumerate(allc)]
        body = P('표는 다섯 가지 열기관 (가)~(마)가 한 번 순환하는 동안 고열원에서 흡수한 열량 Q₁, 한 일 W, 저열원으로 방출한 열량 Q₂를 나타낸 것이다. 이 중 만들 수 없는 열기관은?') + table(['열기관', 'Q₁(J)', 'W(J)', 'Q₂(J)'], rows)
        return mc_list(body, labs, pos, steps=['가능한 열기관은 Q₁ = W + Q₂ 이고 Q₂ > 0 (e < 100 %)이어야 한다.', '%s : Q₁ = %d, W = %d, Q₂ = %d → %s' % (labs[pos], bad[0], bad[1], bad[2], why)],
                       lv='중', fam='b', core='열기관은 에너지 보존(Q₁ = W + Q₂)과 열역학 제2법칙(Q₂ > 0)을 모두 만족해야 한다.', point='제1·2법칙으로 불가능한 열기관을 가려낸다.')
    if form == 'c':
        items = [('고열원 하나에서 열을 흡수해 그 열을 전부 일로 바꾸며 순환하는 열기관', '제2종 영구기관'),
                 ('에너지를 공급받지 않고 계속 일을 하는 기관', '제1종 영구기관'),
                 ('열효율이 100 %인 열기관', '제2종 영구기관'),
                 ('주위 바닷물의 열만을 흡수하여 그 열로 계속 배를 움직이는 기관', '제2종 영구기관'),
                 ('연료 없이 스스로 에너지를 만들어 내며 계속 돌아가는 바퀴', '제1종 영구기관')]
        t, ans = r.choice(items)
        body = P('다음 설명에 해당하는 것은? (단, 그러한 기관은 실제로 만들 수 없다.)') + '<div class="bogi"><p>%s</p></div>' % t + P('이 기관이 위배하는 법칙을 옳게 짝지은 것은?')
        if ans == '제2종 영구기관':
            right = '제2종 영구기관 - 열역학 제2법칙'
            wr = ['제2종 영구기관 - 에너지 보존 법칙', '제1종 영구기관 - 열역학 제2법칙', '제1종 영구기관 - 에너지 보존 법칙', '제2종 영구기관 - 보일 법칙', '제1종 영구기관 - 보일 법칙']
        else:
            right = '제1종 영구기관 - 에너지 보존 법칙(열역학 제1법칙)'
            wr = ['제1종 영구기관 - 열역학 제2법칙', '제2종 영구기관 - 열역학 제2법칙', '제2종 영구기관 - 에너지 보존 법칙(열역학 제1법칙)', '제1종 영구기관 - 보일 법칙', '제2종 영구기관 - 보일 법칙']
        return mc(body, right, wr, r=r, lv='중', fam='c', sort='shuf', steps=['해당하는 기관은 %s이다.' % ans, '제1종은 에너지 보존(제1법칙)에, 제2종은 열역학 제2법칙에 위배된다.'], core='제1종 영구기관: 에너지 보존 위배, 제2종 영구기관: 열역학 제2법칙 위배.', point='영구기관의 종류와 위배 법칙을 구분한다.')
    # d: 열효율 값 판단
    q1 = r.choice([200, 400, 500, 600, 1000]); e = r.choice([0.2, 0.25, 0.3, 0.4, 0.5, 0.6])
    w = int(q1 * e)
    body = P('어떤 열기관이 한 번 순환하는 동안 고열원에서 %d J을 흡수하여 %d J의 일을 한다. 이 열기관에 대한 설명으로 옳은 것은?' % (q1, w))
    right = '저열원으로 %d J의 열을 방출하며 열효율은 %s이다.' % (q1 - w, pct(Fraction(w, q1)))
    wr = ['저열원으로 %d J의 열을 방출하며 열효율은 %s이다.' % (w, pct(Fraction(w, q1))), '저열원으로 열을 방출하지 않으며 열효율은 100 %이다.', '저열원으로 %d J의 열을 방출하며 열효율은 %s이다.' % (q1 - w, pct(Fraction(q1 - w, q1))), '저열원으로 %d J의 열을 방출하며 열효율은 %s이다.' % (q1 + w, pct(Fraction(w, q1 + w))), '저열원에서 %d J의 열을 흡수한다.' % (q1 - w)]
    return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf', steps=['Q₂ = Q₁ − W = %d − %d = %d J' % (q1, w, q1 - w), 'e = W/Q₁ = %d/%d = %s' % (w, q1, pct(Fraction(w, q1)))], core='Q₂ = Q₁ − W, e = W/Q₁.', point='제1법칙과 열효율 정의를 함께 적용한다.')


# ============================================================ ph080 가역 과정과 비가역 과정
_IRR = [
    ('잉크 한 방울이 물속에서 퍼져 나가는 것', '확산은 스스로 되돌아가지 않는다.'),
    ('뜨거운 물체와 차가운 물체를 접촉시켰을 때 열이 고온에서 저온으로 이동하는 것', '열은 저절로 저온에서 고온으로 이동하지 않는다.'),
    ('거친 바닥에서 미끄러지던 물체가 마찰열을 내며 멈추는 것', '마찰로 생긴 열이 저절로 운동 에너지로 돌아오지 않는다.'),
    ('진공 속으로 기체가 단열 자유 팽창하는 것', '퍼진 기체가 저절로 한쪽으로 모이지 않는다.'),
    ('칸막이를 열었을 때 서로 다른 두 기체가 섞이는 것', '섞인 기체가 저절로 분리되지 않는다.'),
    ('떨어져 깨진 달걀이 저절로 원래대로 되돌아가는 현상의 반대(달걀이 깨지는 것)', '깨진 달걀이 저절로 복원되지 않는다.'),
    ('컵의 뜨거운 커피가 식어서 방 온도가 되는 것', '식은 커피가 저절로 데워지지 않는다.'),
    ('각설탕이 물에 녹는 것', '녹은 설탕이 저절로 다시 결정이 되지 않는다.'),
    ('높은 곳에서 떨어진 공이 바닥에서 소리와 열을 내며 멈추는 것', '열과 소리가 저절로 공을 튀어 오르게 하지 않는다.'),
]
_REV = [
    ('마찰과 공기 저항이 없는 진자의 왕복 운동', '에너지 손실이 없어 되돌릴 수 있는 이상적인 과정이다.'),
    ('마찰이 없는 용수철에 매달린 물체의 진동', '에너지가 손실되지 않으므로 가역 과정이다.'),
    ('온도 차가 거의 없는 열원과 접촉한 기체가 매우 천천히 하는 등온 팽창(이상적인 경우)', '평형 상태를 유지하며 아주 천천히 진행되므로 가역 과정으로 볼 수 있다.'),
    ('마찰이 없는 수평면 위에서 두 물체가 하는 완전 탄성 충돌', '운동 에너지가 보존되어 되돌릴 수 있다.'),
]

def _irr_text(s): return s

_B80 = [(t + '은(는) 비가역 과정이다.' if False else '%s은 비가역 과정이다.' % t, True, w, 'i%d' % i) for i, (t, w) in enumerate(_IRR)]
_B80 += [('%s은 가역 과정이다.' % t, True, w, 'r%d' % i) for i, (t, w) in enumerate(_REV)]
_B80 += [('%s은 가역 과정이다.' % t, False, '이 현상은 ' + w.replace('않는다.', '않으므로') + ' 비가역 과정이다.' if False else '이 과정은 비가역 과정이다. ' + w, 'f%d' % i) for i, (t, w) in enumerate(_IRR[:8])]
_B80 += [
    ('자연 현상은 대부분 비가역 과정이다.', True, '열의 이동, 확산, 마찰 등 대부분의 자연 현상은 한쪽 방향으로만 일어난다.', 'nat'),
    ('가역 과정은 열역학 제2법칙에 의해 스스로 일어난 뒤 되돌려도 주변에 변화를 남기지 않는 과정이다.', True, '가역 과정의 정의이다.', 'def'),
    ('비가역 과정이 일어난 뒤 그 과정을 거꾸로 일어나게 하면 주변에 변화가 남지 않는다.', False, '비가역 과정은 거꾸로 되돌리면 주변에 변화가 남는다.', 'defb'),
    ('마찰이 있는 경우의 열기관의 순환 과정은 가역 과정이다.', False, '마찰로 열이 발생하므로 비가역이다.', 'fric'),
]


@T('ph080')
def g080(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd'])
    if form == 'a':
        stm = pick_stmts(r, _B80)
        return bogi('가역 과정과 비가역 과정에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv=r.choice(['하','중']), fam='a', core='비가역 과정은 저절로 되돌아가지 않는 과정(열의 이동, 확산, 마찰 등)이다.', point='가역·비가역 과정을 구분한다.')
    if form == 'b':
        ai = r.randrange(5)
        irr = _IRR[r.randrange(len(_IRR))]
        revs = r.sample(_REV, 4)
        opts = [x[0] for x in revs[:ai]] + [irr[0]] + [x[0] for x in revs[ai:]]
        body = P('다음 중 비가역 과정인 것은? (단, 각 과정은 이상적인 조건에서만 가역으로 본다.)') if False else P('다음 중 비가역 과정인 것은?')
        return mc_list(body, opts, ai, steps=['정답 : ' + irr[0] + ' — ' + irr[1], '나머지는 에너지 손실 없이 되돌릴 수 있는 이상적인 가역 과정으로 다룬다.'], lv='하', fam='b', core='열의 이동·확산·마찰·자유 팽창은 비가역 과정이다.', point='현상에서 비가역 과정을 찾는다.')
    if form == 'c':
        ai = r.randrange(5)
        rev = r.choice(_REV)
        irrs = r.sample(_IRR, 4)
        opts = [x[0] for x in irrs[:ai]] + [rev[0]] + [x[0] for x in irrs[ai:]]
        body = P('다음 중 가역 과정으로 간주할 수 있는 것은?')
        return mc_list(body, opts, ai, steps=['정답 : ' + rev[0] + ' — ' + rev[1], '나머지는 ' + ', '.join(x[0] for x in irrs) + ' 로, 모두 저절로 되돌아가지 않는 비가역 과정이다.'], lv='중', fam='c', core='마찰·열전도·확산이 없는 이상적 과정은 가역 과정이다.', point='가역 과정의 조건을 이해한다.')
    # d: ㄱㄴㄷ 에서 비가역 고르기 (mc)
    k3 = r.sample(_IRR, 2) + r.sample(_REV, 1)
    r.shuffle(k3)
    labs = ['ㄱ', 'ㄴ', 'ㄷ']
    body = P('다음은 세 가지 현상이다.') + BOX_t([(labs[i], k3[i][0]) for i in range(3)]) + P('비가역 과정만을 있는 대로 고른 것은?')
    truth = [k3[i] in _IRR for i in range(3)]
    right = ', '.join(labs[i] for i in range(3) if truth[i])
    combos = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄱ, ㄴ', 'ㄱ, ㄷ', 'ㄴ, ㄷ', 'ㄱ, ㄴ, ㄷ']
    opts = [c for c in combos if c != right]
    ws = r.sample(opts, 4)
    allo = sorted(ws + [right], key=lambda c: (len(c), combos.index(c)))
    return mc_list(body, allo, allo.index(right), steps=['%s : %s' % (labs[i], '비가역 — ' + k3[i][1] if truth[i] else '가역(이상적) — ' + k3[i][1]) for i in range(3)], lv='중', fam='d', core='열 이동·확산·마찰은 비가역, 이상적 진자 운동은 가역이다.', point='여러 현상을 가역·비가역으로 분류한다.')

def BOX_t(items):
    return '<div class="bogi">' + ''.join('<p>%s. %s</p>' % (l, t) for l, t in items) + '</div>'


# ============================================================ ph081 열의 이동 방향과 엔트로피
def _blocks_fig(ta, tb, label_a='A', label_b='B', arrow=None):
    f = Fig(300, 130)
    f.rect(26, 28, 100, 64, '#fde8e6' if ta >= tb else '#e3effb', INK, 2); f.text(76, 56, label_a, 16, 'middle', True, INK, True); f.text(76, 80, '%d °C' % ta, 14, 'middle', True, RD if ta >= tb else BL)
    f.rect(174, 28, 100, 64, '#fde8e6' if tb > ta else '#e3effb', INK, 2); f.text(224, 56, label_b, 16, 'middle', True, INK, True); f.text(224, 80, '%d °C' % tb, 14, 'middle', True, RD if tb > ta else BL)
    f.line(126, 60, 174, 60, GR, 1.4, '4 3')
    f.text(150, 116, '두 물체를 접촉시킴', 12.5, 'middle', False, GR)
    return f.svg()

_ENT = [
    ('얼음이 녹아 물이 되는 것', '증가', '고체가 액체로 되며 분자 배열이 더 무질서해진다.'),
    ('물이 끓어 수증기가 되는 것', '증가', '액체가 기체로 되며 무질서도가 증가한다.'),
    ('수증기가 응결하여 물이 되는 것', '감소', '기체가 액체로 되며 계의 무질서도가 감소한다(주위의 엔트로피는 증가).'),
    ('물이 얼어 얼음이 되는 것', '감소', '액체가 고체로 되며 계의 무질서도가 감소한다(주위의 엔트로피는 증가).'),
    ('진공 속으로 기체가 자유 팽창하는 것', '증가', '기체가 퍼져 무질서도가 증가한다.'),
    ('잉크가 물속에서 퍼지는 것', '증가', '분자 배열이 더 무질서해진다.'),
    ('정돈된 책상이 어지러워지는 것', '증가', '무질서도가 증가한다.'),
    ('섞여 있던 두 기체가 스스로 분리되는 것', '감소', '무질서도가 감소하는 방향은 저절로 일어나지 않는다.'),
    ('고온의 물체에서 저온의 물체로 열이 이동하여 두 물체의 온도가 같아지는 것', '증가', '고립계 전체의 엔트로피가 증가한다.'),
]

_B81 = [
    ('열은 저절로 저온의 물체에서 고온의 물체로 이동하지 않는다.', True, '클라우지우스의 표현이다.', 'cl'),
    ('열은 고온의 물체에서 저온의 물체로 저절로 이동한다.', True, '자연스러운 방향이다.', 'nat'),
    ('외부에서 일을 해 주면 열을 저온에서 고온으로 옮길 수 있다.', True, '냉장고·에어컨이 그 예이다.', 'work'),
    ('고립계에서 자발적인 변화가 일어나면 엔트로피는 증가한다.', True, '엔트로피 증가 법칙이다.', 'inc'),
    ('고립계의 엔트로피는 시간이 지나면 저절로 감소한다.', False, '고립계의 엔트로피는 감소하지 않고 증가하거나 같다.', 'dec'),
    ('엔트로피는 계의 무질서한 정도를 나타내는 양이다.', True, '엔트로피의 정의이다.', 'def'),
    ('열평형 상태에 도달한 두 물체 사이에서는 열의 이동이 일어나지 않는다.', True, '온도가 같기 때문이다.', 'eq'),
    ('물이 얼어 얼음이 될 때 물의 엔트로피는 증가한다.', False, '물의 무질서도가 줄어 물의 엔트로피는 감소한다(주위 포함 전체는 증가).', 'ice'),
    ('얼음이 녹아 물이 될 때 엔트로피는 증가한다.', True, '고체 → 액체로 무질서도가 증가한다.', 'melt'),
    ('냉장고는 외부 일 없이 저온의 내부 열을 고온의 외부로 보낸다.', False, '압축기가 일을 해 주기 때문에 가능하다.', 'fridge'),
    ('엔트로피가 감소하는 변화는 어떤 경우에도 일어날 수 없다.', False, '계의 엔트로피가 감소해도 주위의 엔트로피가 더 크게 증가하면 가능하다.', 'local'),
    ('온도가 다른 두 물체를 접촉시키면 높은 쪽의 엔트로피가 증가하는 것으로 열 이동이 설명된다.', False, '열을 잃는 고온 물체의 엔트로피는 감소하고 얻는 저온 물체는 증가하며 전체는 증가한다.', 'two'),
    ('열의 이동에서 전체 엔트로피는 증가하는 방향으로 일어난다.', True, '자발적 변화의 방향이다.', 'tot'),
    ('기체가 진공으로 자유 팽창한 뒤에는 저절로 한쪽으로 모이지 않는다.', True, '엔트로피가 감소하는 방향이기 때문이다.', 'gas'),
]

@T('ph081')
def g081(r, k):
    form = r.choice(['a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    if form == 'a':
        ta, tb = r.sample([10, 20, 30, 40, 50, 60, 70, 80, 90], 2)
        fig = FIG(_blocks_fig(ta, tb), '62%')
        hi, lo = ('A', 'B') if ta > tb else ('B', 'A')
        body = P('그림은 온도가 다른 두 물체 A, B를 접촉시킨 것이다. 열이 이동하는 방향과 두 물체를 합한 전체 엔트로피 변화를 옳게 짝지은 것은? (단, 외부와의 열 출입은 없다.)') + fig
        right = '%s에서 %s로 이동, 전체 엔트로피 증가' % (hi, lo)
        wr = ['%s에서 %s로 이동, 전체 엔트로피 증가' % (lo, hi), '%s에서 %s로 이동, 전체 엔트로피 감소' % (hi, lo), '%s에서 %s로 이동, 전체 엔트로피 감소' % (lo, hi), '%s에서 %s로 이동, 전체 엔트로피 불변' % (hi, lo), '열이 이동하지 않음, 전체 엔트로피 불변']
        return mc(body, right, wr, r=r, lv='하', fam='a', sort='shuf', steps=['열은 고온(%s : %d °C)에서 저온(%s : %d °C)으로 저절로 이동한다.' % (hi, max(ta, tb), lo, min(ta, tb)), '고립계의 자발적 변화이므로 전체 엔트로피는 증가한다.'], core='열은 고온에서 저온으로 이동하며 고립계의 엔트로피는 증가한다.', point='열 이동 방향과 엔트로피 변화를 함께 판단한다.')
    if form == 'b':
        s = r.choice(_ENT)
        body = P('%s을 계(물질)의 엔트로피 변화로 옳게 나타낸 것은?' % s[0].replace('것', '변화'))
        body = P('다음 변화에서 물질(계)의 엔트로피 변화로 옳은 것은?') + BOX_(s[0])
        right = '엔트로피가 %s한다' % s[1]
        opts = ['엔트로피가 증가한다', '엔트로피가 감소한다', '엔트로피가 변하지 않는다', '엔트로피가 0이 된다', '엔트로피를 정의할 수 없다']
        wr = [o for o in opts if o != right]
        return mc(body, right, wr, r=r, lv='중', fam='b', sort='shuf', steps=[s[2]], core='엔트로피는 무질서도의 척도이다: 고체 < 액체 < 기체.', point='상태 변화·퍼짐에서 엔트로피의 증감을 판단한다.')
    if form == 'c':
        stm = pick_stmts(r, _B81)
        return bogi('열의 이동 방향과 엔트로피에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', stm, r=r, ask='', lv=r.choice(['하','중']), fam='c', core='고립계에서 자발적 변화는 엔트로피가 증가하는 방향으로 일어난다.', point='열의 이동과 엔트로피의 관계를 설명한다.')
    if form == 'd':   # 같은 질량 물이 섞였을 때 나중 온도
        m1, m2 = r.choice([1, 2, 3]), r.choice([1, 2, 3])
        t1, t2 = r.sample([10, 20, 30, 40, 50, 60, 70, 80, 90], 2)
        if (m1 * t1 + m2 * t2) % (m1 + m2): return None
        tf = (m1 * t1 + m2 * t2) // (m1 + m2)
        body = P('질량이 각각 %d kg, %d kg인 물 A, B의 온도가 각각 %d °C, %d °C이다. 두 물을 섞어 열평형에 도달하게 했을 때 나중 온도와 열의 이동 방향을 옳게 짝지은 것은? (단, 외부와의 열 출입은 없다.)' % (m1, m2, t1, t2))
        hi, lo = ('A', 'B') if t1 > t2 else ('B', 'A')
        right = '%d °C, %s → %s' % (tf, hi, lo)
        avg = (t1 + t2) // 2 if (t1 + t2) % 2 == 0 else t1
        wr = ['%d °C, %s → %s' % (tf, lo, hi), '%d °C, %s → %s' % (avg, hi, lo) if avg != tf else '%d °C, %s → %s' % (tf + 10, hi, lo), '%d °C, %s → %s' % (max(t1, t2), hi, lo), '%d °C, %s → %s' % (min(t1, t2), lo, hi), '%d °C, %s → %s' % (tf + 10, lo, hi)]
        return mc(body, right, wr, r=r, lv='상', fam='d', sort='shuf', steps=['열평형 : 잃은 열 = 얻은 열이므로 m₁(t₁ − t) = m₂(t − t₂)', '%d×%d + %d×%d = (%d + %d) t → t = %d °C' % (m1, t1, m2, t2, m1, m2, tf), '열은 고온(%s)에서 저온(%s)으로 이동한다.' % (hi, lo)], core='열평형 온도는 (m₁t₁ + m₂t₂)/(m₁ + m₂) (같은 물질). 열은 고온에서 저온으로.', point='열평형 온도를 구하고 열 이동 방향을 판단한다.')
    # e: 세 현상 ㄱㄴㄷ 엔트로피 증가
    k3 = r.sample(_ENT, 3)
    labs = ['ㄱ', 'ㄴ', 'ㄷ']
    body = P('다음은 세 가지 변화이다.') + BOX_t([(labs[i], k3[i][0]) for i in range(3)]) + P('물질(계)의 엔트로피가 증가하는 변화만을 있는 대로 고른 것은?')
    truth = [x[1] == '증가' for x in k3]
    if not any(truth): return None
    right = ', '.join(labs[i] for i in range(3) if truth[i])
    combos = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄱ, ㄴ', 'ㄱ, ㄷ', 'ㄴ, ㄷ', 'ㄱ, ㄴ, ㄷ']
    ws = r.sample([c for c in combos if c != right], 4)
    allo = sorted(ws + [right], key=lambda c: (len(c), combos.index(c)))
    return mc_list(body, allo, allo.index(right), steps=['%s : 엔트로피 %s — %s' % (labs[i], k3[i][1], k3[i][2]) for i in range(3)], lv='중', fam='e', core='무질서도가 커지는 변화(융해, 기화, 확산)는 엔트로피가 증가한다.', point='여러 변화에서 엔트로피 증가를 가려낸다.')

def BOX_(t):
    return '<div class="bogi"><p>%s</p></div>' % t


# ============================================================ ph082 P-V 순환 그래프에서 구하는 열효율
@T('ph082')
def g082(r, k):
    form = r.choice(['a', 'a', 'b', 'c', 'd', 'd'])
    sc = rand_sch(r)
    cyc = _cycle(r, 'rect', False)
    if not cyc: return None
    st, names = cyc
    segs = []
    for i, nm in enumerate(names):
        a_, b_ = st[nm], st[names[(i + 1) % 4]]
        dU, W, Q = seg_energy('L', a_, b_)
        segs.append((nm, names[(i + 1) % 4], dU * sc.J, W * sc.J, Q * sc.J))
    Q1 = sum(s[4] for s in segs if s[4] > 0); Q2 = -sum(s[4] for s in segs if s[4] < 0)
    Wn = cyc_work(st, names) * sc.J
    assert abs(Q1 - Q2 - Wn) < 1e-6 and Wn > 0
    for s in segs: assert abs(s[4] - (s[2] + s[3])) < 1e-9
    e = Fraction(Wn).limit_denominator(100000) / Fraction(Q1).limit_denominator(100000)
    if (e * 1000).denominator != 1: return None
    if abs(Q1 - round(Q1)) > 1e-9 or abs(Q2 - round(Q2)) > 1e-9: return None
    Q1, Q2, Wn = int(round(Q1)), int(round(Q2)), int(round(Wn))
    order = ' → '.join(list(names) + [names[0]])
    fig = FIG(_cyc_fig(sc, st, names), '74%')
    nA = names[0]
    pvA = st[nA][0] * st[nA][1]
    U_A = 1.5 * pvA * sc.J
    if abs(U_A - round(U_A)) > 1e-9: return None
    U_A = int(round(U_A))
    absorb = [s for s in segs if s[4] > 0]
    absn = ', '.join('%s → %s' % (s[0], s[1]) for s in absorb)
    reln = ', '.join('%s → %s' % (s[0], s[1]) for s in segs if s[4] < 0)
    steps = ['U ∝ T ∝ PV 이므로 각 상태의 내부 에너지를 구해 ΔU 를 얻는다. (상태 %s : %d J)' % (nA, U_A)]
    for s in segs:
        steps.append('%s → %s : ΔU = %s J, W = %s J, Q = ΔU + W = %s J (%s)' % (s[0], s[1], num(s[2]), num(s[3]), num(s[4]), '흡수' if s[4] > 0 else '방출'))
    steps.append('Q₁ = %d J (%s), Q₂ = %d J (%s), W = Q₁ − Q₂ = %d J = 곡선이 둘러싼 넓이' % (Q1, absn, Q2, reln, Wn))
    steps.append('e = W/Q₁ = %d/%d = %s' % (Wn, Q1, pct(e)))
    pre = '그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 상태 %s의 내부 에너지는 %d J이고, 이상 기체의 내부 에너지는 절대 온도에 비례한다.%s' % (order, nA, U_A, unit_note(sc))
    if form == 'a':
        body = P(pre + ' 이 순환 과정을 하는 열기관의 열효율은?') + fig
        wr = [pct(Fraction(Q2, Q1)), pct(Fraction(Wn, Q2)) if Q2 else '0 %', pct(Fraction(Wn, Q1 + Q2)), pct(Fraction(Q2, Wn)) if Wn > Q2 else pct(Fraction(Q1 - Wn, Q1 + Wn)), pct(e + Fraction(1, 10)), pct(Fraction(Wn, Q1 + Wn))]
        return mc(body, pct(e), wr, r=r, lv='상', fam='a', sort='shuf', steps=steps, ref=[1], core='e = W/Q₁. 순환 과정에서 열을 흡수하는 구간의 Q 합이 Q₁, 방출하는 구간의 합이 Q₂.', point='구간별 Q를 구해 흡열량만 더한 Q₁과 일 W로 열효율을 계산한다.')
    if form == 'b':
        ask = r.choice(['Q1', 'Q2'])
        body = P(pre + ' 한 번 순환하는 동안 기체가 %s 열량은?' % ('흡수한' if ask == 'Q1' else '방출한')) + fig
        ans = Q1 if ask == 'Q1' else Q2
        wr = [Q2 if ask == 'Q1' else Q1, Wn, Q1 + Q2, abs(ans - Wn) if abs(ans - Wn) != ans else ans + 100, ans + sc.J]
        return mc(body, J_(ans), [J_(x) for x in wr], r=r, lv='중', fam='b', steps=steps, ref=[1], core='흡열 구간의 Q 합 = Q₁, 방열 구간의 Q 합 = Q₂.', point='구간별 열의 출입을 구분해 합산한다.')
    if form == 'd':
        body = P('그림은 일정량의 이상 기체가 %s로 변하는 순환 과정을 P-V 그래프로 나타낸 것이다. 이 열기관이 한 번 순환하는 동안 고열원에서 흡수한 열량이 %d J일 때 열효율은?%s' % (order, Q1, unit_note(sc))) + fig
        wr = [pct(Fraction(Q2, Q1)), pct(Fraction(Wn, Q2)) if Q2 else '0 %', pct(Fraction(Wn, Q1 + Q2)), pct(e + Fraction(1, 10)), pct(Fraction(Wn + sc.J, Q1))]
        return mc(body, pct(e), wr, r=r, lv='하', fam='d', sort='shuf', steps=['W = 순환 곡선이 둘러싼 넓이 = %s칸 × %s J = %d J' % (num(cyc_work(st, names)), num(sc.J), Wn), 'e = W/Q₁ = %d/%d = %s' % (Wn, Q1, pct(e))], ref=[1], core='e = W/Q₁, W = 순환 곡선의 넓이.', point='넓이로 일을 구하고 주어진 Q₁으로 열효율을 계산한다.')
    # c: bogi
    cand = []
    for s in segs:
        why = '%s → %s : Q = %s J (%s)' % (s[0], s[1], num(s[4]), '흡수' if s[4] > 0 else '방출')
        cand.append(('%s 과정에서 기체는 열을 흡수한다.' % ('%s → %s' % (s[0], s[1])), s[4] > 0, why))
    cand.append(('이 열기관의 열효율은 %s 보다 크다.' % '50 %', e > Fraction(1, 2), 'e = %s 이다.' % pct(e)))
    cand.append(('이 열기관의 열효율은 %s 보다 작다.' % '20 %', e < Fraction(1, 5), 'e = %s 이다.' % pct(e)))
    cand.append(('방출한 열량 Q₂는 한 일 W보다 %s.' % r.choice(['크다', '작다']), None, ''))
    cand = [c for c in cand if c[1] is not None]
    cand.append(('한 번 순환하는 동안 한 일은 흡수한 열량 Q₁과 같다.', False, 'W = Q₁ − Q₂ < Q₁ 이다 (Q₂ > 0).'))
    cand.append(('한 번 순환하는 동안 기체의 내부 에너지 변화는 0이다.', True, '처음 상태로 돌아온다.'))
    cand.append(('방출한 열량 Q₂는 %d J이다.' % Q2, True, 'Q₂ = %d J' % Q2))
    cand.append(('방출한 열량 Q₂는 %d J이다.' % (Q2 + sc.J), False, 'Q₂ = %d J 이다.' % Q2))
    for _ in range(40):
        sel = r.sample(cand, 3)
        if len({s[0] for s in sel}) == 3 and any(s[1] for s in sel): break
    else:
        return None
    return bogi(pre + ' 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?', sel, pre=fig, r=r, ask='', lv='중', fam='c', ref=[1],
                core='순환 과정: ΔU = 0, W = Q₁ − Q₂ = 넓이, e = W/Q₁ < 1.', point='구간별 열의 출입과 열효율을 판단한다.')


# ============================================================ ph083 열역학 법칙 종합 판단
def _law_check(q1, w, q2):
    ok1 = (q1 == w + q2)
    ok2 = (q2 > 0)
    return ok1, ok2

@T('ph083')
def g083(r, k):
    form = r.choice(['a', 'a', 'a', 'b', 'b', 'c', 'c', 'd', 'e'])
    pool_good = [(500, 200, 300), (400, 100, 300), (600, 300, 300), (800, 200, 600), (1000, 400, 600), (200, 50, 150), (300, 100, 200), (900, 300, 600), (700, 200, 500), (600, 150, 450)]
    def make(kind):
        if kind == 'ok': return r.choice(pool_good)
        if kind == 'v1a':
            q1, w, q2 = r.choice(pool_good); return (q1, w + 100, q2)
        if kind == 'v1b':
            q1, w, q2 = r.choice(pool_good); return (q1, w, q2 + 100)
        if kind == 'v2':
            q1 = r.choice([300, 400, 500, 600, 800]); return (q1, q1, 0)
        if kind == 'v2b':
            q1 = r.choice([300, 400, 500, 600, 800]); return (q1, q1 + 0, 0)
    if form in ('a', 'b'):
        kinds = ['ok', 'v1a', 'v1b', 'v2', 'ok']
        r.shuffle(kinds)
        cs = [make(kd) for kd in kinds]
        labs = ['(가)', '(나)', '(다)', '(라)', '(마)']
        rows = [[labs[i], cs[i][0], cs[i][1], cs[i][2]] for i in range(5)]
        tbl = table(['열기관', 'Q₁(J)', 'W(J)', 'Q₂(J)'], rows)
        if form == 'a':
            want = r.choice(['ok', 'v1', 'v2'])
            if want == 'ok':
                idx = [i for i, kd in enumerate(kinds) if kd == 'ok']
                if len(idx) != 2: return None
                ai = idx[0]
                # 가능한 것이 2개이면 문항이 모호 — 하나만 'ok' 가 되도록 하나를 변형
                cs[idx[1]] = make('v1b'); kinds[idx[1]] = 'v1b'
                rows = [[labs[i], cs[i][0], cs[i][1], cs[i][2]] for i in range(5)]; tbl = table(['열기관', 'Q₁(J)', 'W(J)', 'Q₂(J)'], rows)
                q = '다섯 가지 열기관 중 열역학 제1법칙과 제2법칙을 모두 만족하여 만들 수 있는 것은?'
            elif want == 'v1':
                idx = [i for i, kd in enumerate(kinds) if kd in ('v1a', 'v1b')]
                if len(idx) != 2: return None
                cs[idx[1]] = make('ok'); kinds[idx[1]] = 'ok'
                rows = [[labs[i], cs[i][0], cs[i][1], cs[i][2]] for i in range(5)]; tbl = table(['열기관', 'Q₁(J)', 'W(J)', 'Q₂(J)'], rows)
                ai = idx[0]
                q = '다섯 가지 열기관 중 에너지 보존 법칙(열역학 제1법칙)에 위배되는 것은?'
            else:
                ai = kinds.index('v2')
                q = '다섯 가지 열기관 중 에너지 보존 법칙에는 맞지만 열역학 제2법칙에 위배되는 것은?'
            body = P('표는 다섯 가지 열기관 (가)~(마)가 한 번 순환하는 동안 고열원에서 흡수한 열량 Q₁, 한 일 W, 저열원으로 방출한 열량 Q₂를 나타낸 것이다. ' + q) + tbl
            res = []
            for i, c in enumerate(cs):
                o1, o2 = _law_check(*c)
                res.append('%s : Q₁ %s W + Q₂ (%d %s %d + %d), Q₂ %s 0 → 제1법칙 %s, 제2법칙 %s' % (labs[i], '=' if o1 else '≠', c[0], '=' if o1 else '≠', c[1], c[2], '>' if o2 else '=', 'O' if o1 else '위배', 'O' if o2 else '위배'))
            o1, o2 = _law_check(*cs[ai])
            if want == 'ok': assert o1 and o2 and sum(1 for c in cs if all(_law_check(*c))) == 1
            if want == 'v1': assert not o1 and sum(1 for c in cs if not _law_check(*c)[0]) == 1
            if want == 'v2': assert o1 and not o2 and sum(1 for c in cs if _law_check(*c)[0] and not _law_check(*c)[1]) == 1
            return mc_list(body, labs, ai, steps=res, lv='중', fam='a', core='열기관은 Q₁ = W + Q₂ (제1법칙)이고 Q₂ > 0 (제2법칙, 열효율 100 % 불가)이어야 한다.', point='표의 값으로 제1·2법칙 위배 여부를 판정한다.')
        # b: bogi
        kinds3 = r.sample(['ok', 'v1a', 'v1b', 'v2'], 3)
        cs = [make(kd) for kd in kinds3]
        labs3 = ['(가)', '(나)', '(다)']
        rows = [[labs3[i], cs[i][0], cs[i][1], cs[i][2]] for i in range(3)]
        cand = []
        for i, c in enumerate(cs):
            o1, o2 = _law_check(*c)
            claims = [('%s는 열역학 제1법칙에 위배된다.' % labs3[i], not o1, 'Q₁ = %d, W + Q₂ = %d 이므로 제1법칙을 %s.' % (c[0], c[1] + c[2], '만족한다' if o1 else '위배한다')),
                      ('%s는 열역학 제2법칙에 위배된다.' % labs3[i], o1 and not o2 or ((not o2)), 'Q₂ = %d J 이므로 제2법칙을 %s.' % (c[2], '만족한다' if o2 else '위배한다')),
                      ('%s는 만들 수 있다.' % labs3[i], o1 and o2, '제1법칙 %s, 제2법칙 %s.' % ('O' if o1 else '위배', 'O' if o2 else '위배'))]
            cand += claims
        for _ in range(60):
            sel = r.sample(cand, 3)
            if len({s[0] for s in sel}) == 3 and any(s[1] for s in sel): break
        else:
            return None
        body_intro = '표는 세 열기관 (가)~(다)가 한 번 순환하는 동안 고열원에서 흡수한 열량 Q₁, 한 일 W, 저열원으로 방출한 열량 Q₂를 나타낸 것이다. 이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'
        return bogi(body_intro, sel, pre=table(['열기관', 'Q₁(J)', 'W(J)', 'Q₂(J)'], rows), r=r, ask='', lv='상', fam='b', core='제1법칙: Q₁ = W + Q₂. 제2법칙: Q₂ > 0.', point='표의 수치로 법칙 위배 여부를 판정하는 <보기>.')
    if form == 'c':   # 한 값이 주어질 때 가능한 값
        q1, w, q2 = r.choice(pool_good)
        which = r.choice(['W', 'Q2'])
        if which == 'W':
            body = P('어떤 열기관이 한 번 순환하는 동안 고열원에서 %d J의 열을 흡수하고 저열원으로 %d J의 열을 방출하였다. 이 열기관이 한 일 W로 옳은 것은? (단, 열역학 제1법칙이 성립한다.)' % (q1, q2))
            wr = [q1, q1 + q2, q2, w + 100, 0]
            return mc(body, J_(w), [J_(x) for x in wr if x != w], r=r, lv='하', fam='c', steps=['제1법칙에 의해 W = Q₁ − Q₂ = %d − %d = %d J' % (q1, q2, w)], core='Q₁ = W + Q₂.', point='제1법칙으로 한 일을 구한다.')
        body = P('어떤 열기관이 한 번 순환하는 동안 고열원에서 %d J의 열을 흡수하여 %d J의 일을 한다. 열역학 제1법칙과 제2법칙에 맞는 저열원으로 방출하는 열량 Q₂는?' % (q1, w))
        wr = [0, q1, q1 + w, w, q2 + 100]
        return mc(body, J_(q2), [J_(x) for x in wr if x != q2], r=r, lv='중', fam='c', steps=['Q₂ = Q₁ − W = %d − %d = %d J' % (q1, w, q2), 'Q₂ > 0 이므로 제2법칙에도 맞다 (Q₂ = 0 이면 열효율 100 %로 불가능).'], core='Q₂ = Q₁ − W > 0.', point='제1법칙으로 Q₂를 구하고 제2법칙 만족을 확인한다.')
    if form == 'd':   # 서술형 상황 판단
        sit = [
            ('외부에서 일을 해 주지 않고 저온의 물체에서 고온의 물체로 열을 이동시키는 장치', '열역학 제2법칙', False),
            ('외부에서 일을 해 주어 저온의 내부에서 고온의 외부로 열을 퍼내는 냉장고', '(위배되지 않음)', True),
            ('흡수한 열 500 J 중 200 J을 일로 바꾸고 300 J을 저열원으로 방출하는 열기관', '(위배되지 않음)', True),
            ('에너지를 공급받지 않고 계속해서 일을 하는 기관', '에너지 보존 법칙(열역학 제1법칙)', False),
            ('고열원에서 흡수한 열 전부를 일로 바꾸는 열기관', '열역학 제2법칙', False),
            ('열을 흡수한 양보다 많은 일을 하는 열기관(저열원으로 방출 열량 0 이상)', '에너지 보존 법칙(열역학 제1법칙)', False),
        ]
        i = r.randrange(len(sit)); t, law, possible = sit[i]
        body = P('다음 장치에 대한 설명으로 옳은 것은?') + BOX_(t)
        if possible:
            right = '열역학 제1법칙과 제2법칙에 모두 위배되지 않아 만들 수 있다.'
            wr = ['열역학 제1법칙에 위배되어 만들 수 없다.', '열역학 제2법칙에 위배되어 만들 수 없다.', '제1법칙과 제2법칙에 모두 위배된다.', '열효율이 100 %이다.', '일을 하지 않고도 열을 만들어 낸다.']
        elif law.startswith('열역학 제2'):
            right = '에너지 보존 법칙에는 맞지만 열역학 제2법칙에 위배되어 만들 수 없다.'
            wr = ['열역학 제1법칙에 위배되어 만들 수 없다.', '제1법칙과 제2법칙에 모두 위배되지 않아 만들 수 있다.', '열역학 제1법칙과 제2법칙에 모두 위배된다.', '보일 법칙에 위배되어 만들 수 없다.', '열효율이 100 %보다 커서 가능하다.']
        else:
            right = '에너지 보존 법칙(열역학 제1법칙)에 위배되어 만들 수 없다.'
            wr = ['에너지 보존 법칙에는 맞지만 열역학 제2법칙에 위배되어 만들 수 없다.', '제1법칙과 제2법칙에 모두 위배되지 않아 만들 수 있다.', '열효율이 100 %이므로 만들 수 있다.', '보일 법칙에 위배되어 만들 수 없다.', '열역학 제2법칙에는 맞지만 제1법칙은 알 수 없다.']
        return mc(body, right, wr, r=r, lv='중', fam='d', sort='shuf', steps=['장치의 에너지 수지(Q₁ = W + Q₂)와 열의 방향·열효율 100 % 여부를 따진다.', right], core='에너지는 보존되어야 하고(제1법칙), 열을 전부 일로 바꾸거나 일 없이 저온에서 고온으로 열을 옮길 수 없다(제2법칙).', point='장치가 어느 법칙에 위배되는지 판단한다.')
    # e: 효율이 큰 순서/가능한 최대 일
    q1 = r.choice([400, 500, 600, 800, 1000]); q2 = r.choice([100, 200, 300])
    if q2 >= q1: return None
    w = q1 - q2
    body = P('열기관 A는 한 번 순환하는 동안 고열원에서 %d J을 흡수하고 저열원으로 %d J을 방출한다고 한다. 이 열기관의 한 일과 열효율이 열역학 법칙에 맞는지에 대한 설명으로 옳은 것은?' % (q1, q2))
    right = '한 일은 %d J이고 열효율은 %s로 두 법칙에 모두 위배되지 않는다.' % (w, pct(Fraction(w, q1)))
    wr = ['한 일은 %d J이고 열효율은 %s이다.' % (q1 + q2, pct(Fraction(q1 + q2, q1))), '한 일은 %d J이며 열효율이 100 %%이다.' % q1, '한 일은 %d J이고 열효율은 %s이므로 제2법칙에 위배된다.' % (w, pct(Fraction(w, q1))), '한 일은 %d J이고 제1법칙에 위배된다.' % q2, '한 일은 %d J이고 열효율은 %s로 두 법칙에 모두 위배되지 않는다.' % (q2, pct(Fraction(q2, q1)))]
    return mc(body, right, wr, r=r, lv='중', fam='e', sort='shuf', steps=['제1법칙 : W = Q₁ − Q₂ = %d − %d = %d J' % (q1, q2, w), '제2법칙 : Q₂ = %d J > 0 이므로 e = W/Q₁ = %s < 100 %% 로 가능하다.' % (q2, pct(Fraction(w, q1)))], core='제1법칙 W = Q₁ − Q₂, 제2법칙 e < 100 %.', point='주어진 값에서 일과 열효율을 구하고 법칙 위배 여부를 확인한다.')
