"""Ⅲ-B 헤스 법칙: 의미 · 식 조합(기호/수치) · 관계도 · 용해/중화 실험 · 결합 에너지 · 생성 엔탈피"""
from core import *
from fractions import Fraction as Fr
import svg

def frs(x):
    """분수 계수 → 수식 문자열."""
    x = Fr(x).limit_denominator(12)
    if x.denominator == 1: return str(x.numerator)
    return f'\\frac{{{x.numerator}}}{{{x.denominator}}}'

def expr(coefs, names=('\\Delta H_1', '\\Delta H_2', '\\Delta H_3')):
    """계수 목록 → aΔH1 + bΔH2 ... 수식."""
    out = ''
    for c, n in zip(coefs, names):
        c = Fr(c).limit_denominator(12)
        if c == 0: continue
        sgn = '-' if c < 0 else ('+' if out else '')
        a = abs(c)
        cs = '' if a == 1 else (frs(a))
        out += f'{sgn}{cs}{n}'
    return out or '0'

# 헤스 법칙 세트: (주어진 반응 목록[(식, ΔH)], 목표 반응, 계수, 설명용 이름)
SETS = [
 # C → CO
 ([('C(s, 흑연) + O2(g) -> CO2(g)', -393.5), ('CO(g) + \\frac{1}{2}O2(g) -> CO2(g)', -283.0)], 'C(s, 흑연) + \\frac{1}{2}O2(g) -> CO(g)', [1, -1]),
 ([('C(s, 흑연) + O2(g) -> CO2(g)', -393.5), ('2CO(g) + O2(g) -> 2CO2(g)', -566.0)], '2C(s, 흑연) + O2(g) -> 2CO(g)', [2, -1]),
 # 흑연 → 다이아몬드
 ([('C(s, 흑연) + O2(g) -> CO2(g)', -393.5), ('C(s, 다이아몬드) + O2(g) -> CO2(g)', -395.4)], 'C(s, 흑연) -> C(s, 다이아몬드)', [1, -1]),
 # N2H4
 ([('N2(g) + 3H2(g) -> 2NH3(g)', -92.2), ('N2H4(g) + H2(g) -> 2NH3(g)', -187.6)], 'N2(g) + 2H2(g) -> N2H4(g)', [1, -1]),
 # C2H2 + 2H2 → C2H6
 ([('2C(s) + 3H2(g) -> C2H6(g)', -85.0), ('2C(s) + H2(g) -> C2H2(g)', 227.0)], 'C2H2(g) + 2H2(g) -> C2H6(g)', [1, -1]),
 # CaCO3 + HCl
 ([('CaCO3(s) -> CaO(s) + CO2(g)', 179.2), ('CaO(s) + 2HCl(aq) -> CaCl2(aq) + H2O(l)', -193.5)], 'CaCO3(s) + 2HCl(aq) -> CaCl2(aq) + CO2(g) + H2O(l)', [1, 1]),
 # NaOH 용해 + 중화
 ([('NaOH(s) -> NaOH(aq)', -44.5), ('NaOH(aq) + HCl(aq) -> NaCl(aq) + H2O(l)', -56.0)], 'NaOH(s) + HCl(aq) -> NaCl(aq) + H2O(l)', [1, 1]),
 # 메테인 생성
 ([('C(s, 흑연) + O2(g) -> CO2(g)', -393.5), ('H2(g) + \\frac{1}{2}O2(g) -> H2O(l)', -285.8), ('CH4(g) + 2O2(g) -> CO2(g) + 2H2O(l)', -890.8)], 'C(s, 흑연) + 2H2(g) -> CH4(g)', [1, 2, -1]),
 # 에탄올 연소(189)
 ([('H2(g) + \\frac{1}{2}O2(g) -> H2O(l)', -285.8), ('C(s) + O2(g) -> CO2(g)', -393.5), ('2C(s) + 3H2(g) + \\frac{1}{2}O2(g) -> C2H5OH(l)', -277.7)], 'C2H5OH(l) + 3O2(g) -> 2CO2(g) + 3H2O(l)', [3, 2, -1]),
 # 에텐 생성
 ([('C(s, 흑연) + O2(g) -> CO2(g)', -393.5), ('H2(g) + \\frac{1}{2}O2(g) -> H2O(l)', -285.8), ('C2H4(g) + 3O2(g) -> 2CO2(g) + 2H2O(l)', -1411.0)], '2C(s, 흑연) + 2H2(g) -> C2H4(g)', [2, 2, -1]),
 # 물의 기화
 ([('H2(g) + \\frac{1}{2}O2(g) -> H2O(l)', -285.8), ('H2(g) + \\frac{1}{2}O2(g) -> H2O(g)', -241.8)], 'H2O(l) -> H2O(g)', [-1, 1]),
 # NO2
 ([('N2(g) + O2(g) -> 2NO(g)', 181.0), ('2NO(g) + O2(g) -> 2NO2(g)', -114.0)], 'N2(g) + 2O2(g) -> 2NO2(g)', [1, 1]),
 # SO3
 ([('S(s) + O2(g) -> SO2(g)', -296.8), ('2SO2(g) + O2(g) -> 2SO3(g)', -197.8)], 'S(s) + \\frac{3}{2}O2(g) -> SO3(g)', [1, Fr(1, 2)]),
 # 프로페인 생성
 ([('C(s, 흑연) + O2(g) -> CO2(g)', -393.5), ('H2(g) + \\frac{1}{2}O2(g) -> H2O(l)', -285.8), ('C3H8(g) + 5O2(g) -> 3CO2(g) + 4H2O(l)', -2220.0)], '3C(s, 흑연) + 4H2(g) -> C3H8(g)', [3, 4, -1]),
 # 메탄올
 ([('CO(g) + 2H2(g) -> CH3OH(l)', -128.1), ('C(s, 흑연) + \\frac{1}{2}O2(g) -> CO(g)', -110.5)], 'C(s, 흑연) + 2H2(g) + \\frac{1}{2}O2(g) -> CH3OH(l)', [1, 1]),
 # 철 제련
 ([('2Fe(s) + \\frac{3}{2}O2(g) -> Fe2O3(s)', -824.2), ('CO(g) + \\frac{1}{2}O2(g) -> CO2(g)', -283.0)], 'Fe2O3(s) + 3CO(g) -> 2Fe(s) + 3CO2(g)', [-1, 3]),
 # 암모니아 산화 비슷한
 ([('H2(g) + Cl2(g) -> 2HCl(g)', -184.6), ('H2(g) + \\frac{1}{2}O2(g) -> H2O(g)', -241.8)], '4HCl(g) + O2(g) -> 2Cl2(g) + 2H2O(g)', [-2, 2]),
]

def hess_value(s):
    return round(sum(float(c) * dh for c, (_, dh) in zip(s[2], s[0])), 1)

def scale_set(rng, s):
    """목표 반응을 배수·역반응으로 바꾼 변형."""
    k = rng.choice([1, 1, 2, -1, Fr(1, 2)])
    if k == 1: return s[1], s[2], 1
    tgt = s[1]
    if k == -1:
        a, b = tgt.split(' -> '); tgt = b + ' -> ' + a
    elif k == 2:
        tgt = '2 × [' + tgt + ']'
    else:
        tgt = '\\frac{1}{2} × [' + tgt + ']'
    return tgt, [Fr(c) * k for c in s[2]], k

def eng_hess_symbol():
    names = ('\\Delta H_1', '\\Delta H_2', '\\Delta H_3')
    for i in range(900):
        rng = R(7000 + i); s = rng.choice(SETS); n = len(s[0])
        tgt, coefs, k = s[1], [Fr(c) for c in s[2]], 1
        lvl = '중' if n == 2 else '상'
        if i % 3 == 2:
            tgt0, coefs, k = scale_set(rng, s)
            if k != 1:
                a, b = s[1].split(' -> ')
                tgt = (b + ' -> ' + a) if k == -1 else (('2' if k == 2 else '\\frac{1}{2}') + '×(' + s[1] + ')')
                lvl = '상' if n == 2 else '최'
        correct = expr(coefs, names)
        wrong = set()
        for _ in range(60):
            c2 = [c * rng.choice([1, -1, 2, Fr(1, 2), 1, 1]) for c in coefs]
            e = expr(c2, names)
            if e != correct: wrong.add(e)
            if len(wrong) >= 6: break
        wrong = list(wrong)[:4]
        if len(wrong) < 4: continue
        ch = [f'${e}$' for e in wrong + [correct]]; rng.shuffle(ch); ans = ch.index(f'${correct}$') + 1
        body = [p('다음은 25 ℃, 1 기압에서 몇 가지 반응의 열화학 반응식이다.'), box([f'{e}, $\\Delta H_{j + 1}$' for j, (e, _) in enumerate(s[0])]),
                p('이 자료로부터 다음 반응의 반응 엔탈피($\\Delta H$)를 옳게 나타낸 것은?'), box([tgt.replace('×', '$\\times$')])]
        sol = ['목표 반응의 반응물·생성물이 되도록 주어진 반응식에 계수를 곱하거나 뒤집어(부호 반대) 더한다.']
        for j, (c, (e, _)) in enumerate(zip(coefs, s[0])):
            if c == 0: continue
            how = ('그대로' if c == 1 else f'${frs(c)}$배') if c > 0 else ('뒤집어서' if c == -1 else f'뒤집고 ${frs(-c)}$배')
            sol.append(f'반응식 {j + 1}: {how} → ${expr([c], (names[j],))}$')
        sol.append(f'∴ $\\Delta H={correct}$')
        add(typ='B2', lv=lvl, ono=189 if n == 3 else 186, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='헤스 법칙: 식을 더하면 $\\Delta H$도 더한다', chk=dict(t='expr', v=correct))

def eng_hess_num():
    for i in range(1000):
        rng = R(8000 + i); s = rng.choice(SETS); n = len(s[0])
        # 값 살짝 바꾸기(변형)
        vals = [round(dh + rng.choice([0, 0, 0, -10, 10, -5, 5, -20, 20]), 1) for _, dh in s[0]]
        coefs = [Fr(c) for c in s[2]]; tgt = s[1]; lvl = '중' if n == 2 else '상'
        if i % 4 == 3:
            k = rng.choice([2, -1])
            coefs = [c * k for c in coefs]
            a, b = s[1].split(' -> ')
            tgt = (b + ' -> ' + a) if k == -1 else '2 × (' + s[1] + ')'
            lvl = '상' if n == 2 else '최'
        v = round(sum(float(c) * x for c, x in zip(coefs, vals)), 1)
        body = [p('다음은 25 ℃, 1 기압에서 몇 가지 반응의 열화학 반응식이다.'), box([f'{e}, $\\Delta H={m(x, 1)}$ kJ' for (e, _), x in zip(s[0], vals)]),
                p('이 자료를 이용하여 구한 다음 반응의 반응 엔탈피($\\Delta H$)는?'), box([tgt.replace('×', '$\\times$')])]
        terms = ' + '.join(f'({frs(c)})\\times({m(x, 1)})' for c, x in zip(coefs, vals) if c != 0)
        sol = ['목표 반응식에 맞게 각 반응식에 곱할 수(뒤집으면 음수)를 정한다: ' + ', '.join(f'식 {j + 1} → ${frs(c)}$' for j, c in enumerate(coefs)),
               f'$\\Delta H={terms}$', f'$={m(v, 1)}$ kJ']
        cands = [-v, round(sum(abs(float(c)) * x for c, x in zip(coefs, vals)), 1), round(sum(x for x in vals), 1), round(v * 2, 1), round(v / 2, 1),
                 round(sum(float(c) * x for c, x in zip([1] * n, vals)), 1), round(vals[0] - vals[-1], 1)]
        ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 1) + ' kJ')
        if not ch: continue
        add(typ='B2', lv=lvl, ono=185 if n == 2 else 189, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='헤스 법칙 계산', chk=dict(t='hess', coefs=[float(c) for c in coefs], vals=vals, v=v))

def eng_hess_diagram():
    """관계도(그림)로 주어진 헤스 법칙(182, 183, 190)."""
    for i in range(700):
        rng = R(9000 + i)
        a = rng.choice([-393.5, -400, -350, -300, -500, -450, -250])
        b = round(a * rng.choice([0.6, 0.7, 0.72, 0.5, 0.4, 0.8]), 1)
        mid = round(a - b, 1)   # 처음 → 중간
        kind = rng.choice(['C', 'X'])
        if kind == 'C':
            L = [('C(s)+O2(g)', 0, 40, 220), ('CO(g)+\\frac12O2(g)', mid, 170, 330), ('CO2(g)', a, 40, 330)]
            L = [('C(s, 흑연)+O2(g)', 0, 40, 220), ('CO(g)+½O2(g)', mid, 170, 330), ('CO2(g)', a, 40, 330)]
            nm = ('C(s, 흑연)+O2(g)', 'CO(g)+½O2(g)', 'CO2(g)')
        else:
            L = [('A(g)+B(g)', 0, 40, 220), ('C(g)', mid, 170, 330), ('D(g)', a, 40, 330)]
            nm = ('A(g)+B(g)', 'C(g)', 'D(g)')
        ask = rng.choice(['mid', 'b', 'a'])
        lab = {'a': f'ΔH₁={num(a, 1)}', 'b': f'ΔH₃={num(b, 1)}', 'mid': f'ΔH₂={num(mid, 1)}'}
        lab[ask] = {'a': 'ΔH₁=?', 'b': 'ΔH₃=?', 'mid': 'ΔH₂=?'}[ask]
        g = svg.levels(L, [(0, 2, 80, lab['a']), (0, 1, 200, lab['mid']), (1, 2, 290, lab['b'])])
        v = {'a': a, 'b': b, 'mid': mid}[ask]
        body = [p('그림은 25 ℃, 1 기압에서 어떤 반응의 엔탈피 관계를 나타낸 것이다. (단위: kJ)'), g, p({'a': '$\\Delta H_1$', 'b': '$\\Delta H_3$', 'mid': '$\\Delta H_2$'}[ask] + '의 값은?')]
        sol = ['헤스 법칙: 처음 상태와 나중 상태가 같으면 경로와 관계없이 $\\Delta H$의 합이 같다.', '$\\Delta H_1=\\Delta H_2+\\Delta H_3$',
               {'a': f'$\\Delta H_1={m(mid, 1)}+({m(b, 1)})={m(a, 1)}$ kJ', 'b': f'$\\Delta H_3=\\Delta H_1-\\Delta H_2={m(a, 1)}-({m(mid, 1)})={m(b, 1)}$ kJ',
                'mid': f'$\\Delta H_2=\\Delta H_1-\\Delta H_3={m(a, 1)}-({m(b, 1)})={m(mid, 1)}$ kJ'}[ask]]
        cands = [-v, round(a + b, 1), round(a + mid, 1), round(b - a, 1), round(-a - b, 1), round(v * 2, 1)]
        ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 1) + ' kJ')
        if not ch: continue
        add(typ='B3', lv=['하', '중'][i % 2], ono=182 if kind == 'C' else 180, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='관계도: 경로가 달라도 합은 같다', chk=dict(t='num', v=v))

def eng_hess_concept():
    S = [('반응물과 생성물의 종류와 상태가 같으면 반응 경로에 관계없이 반응 엔탈피의 합은 일정하다.', True, '헤스 법칙(총열량 불변의 법칙)의 내용이다.'),
         ('반응 경로가 다르면 반응 엔탈피의 총합도 달라진다.', False, '처음과 나중 상태가 같으면 경로와 관계없이 같다.'),
         ('헤스 법칙을 이용하면 직접 측정하기 어려운 반응의 반응 엔탈피를 구할 수 있다.', True, 'C → CO처럼 측정이 어려운 반응의 $\\Delta H$를 계산으로 구한다.'),
         ('모든 화학 반응은 한 가지 경로로만 일어난다.', False, '같은 반응도 여러 단계(경로)로 일어날 수 있다.'),
         ('열화학 반응식을 더하거나 빼면 반응 엔탈피도 같은 방법으로 더하거나 뺀다.', True, '반응식의 조합대로 $\\Delta H$도 조합한다.'),
         ('열화학 반응식을 뒤집으면 반응 엔탈피의 부호도 바뀐다.', True, '역반응의 $\\Delta H$는 부호가 반대이다.'),
         ('열화학 반응식에 2를 곱해도 반응 엔탈피는 그대로이다.', False, '반응 엔탈피도 2배가 된다.'),
         ('헤스 법칙은 반응물과 생성물의 종류만 같으면 상태가 달라도 성립한다.', False, '상태가 다르면 엔탈피가 다르므로 상태까지 같아야 한다.'),
         ('엔탈피는 처음 상태와 나중 상태에 의해서만 결정되는 양이다.', True, '그래서 경로와 관계없이 엔탈피 변화가 같다.'),
         ('탄소가 일산화 탄소를 거쳐 이산화 탄소가 될 때의 반응 엔탈피 합은 탄소가 바로 이산화 탄소가 될 때와 같다.', True, '처음(C+O2)과 나중(CO2) 상태가 같다.'),
         ('탄산 칼슘이 분해된 뒤 염산과 반응하는 경로가 직접 반응하는 경로보다 열이 더 많이 출입한다.', False, '두 경로의 반응 엔탈피 합은 같다.'),
         ('고체 NaOH를 물에 녹인 뒤 염산과 반응시킬 때와 염산에 바로 녹일 때 출입하는 열의 총량은 같다.', True, '처음과 나중 상태가 같으므로 헤스 법칙이 성립한다.')]
    for i in range(500):
        rng = R(9500 + i); k = i % 3
        if k == 0:
            o = one_of(rng, S, rng.random() < 0.5)
            if not o: continue
            want = S[[x[0] for x in S].index(o['ch'][o['ans'] - 1])][1]
            body = [p('헤스 법칙에 대한 설명으로 ' + ('옳은' if want else '옳지 <u>않은</u>') + ' 것은?')]
            add(typ='B1', lv='하', ono=179, hw='s', body=body, ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v', key='헤스 법칙', chk=dict(t='one', want=want))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('헤스 법칙에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])]
            add(typ='B1', lv='중', ono=179, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='헤스 법칙', chk=dict(t='combo', truth=b['truth']))

# ---------------------------------------------------------------- B4 용해 + 중화 (184, 193)
BASES = [('NaOH', '수산화 나트륨', 40, -44.5), ('KOH', '수산화 칼륨', 56, -57.6), ('LiOH', '수산화 리튬', 24, -23.6)]
def eng_neutral():
    for i in range(900):
        rng = R(10000 + i); b = rng.choice(BASES); fm, name, M, dsol = b
        # 정수 온도 변화가 나오도록 몰수 고르기
        mol = rng.choice([0.05, 0.1, 0.025, 0.04, 0.02])
        msol = 100
        dsol_v = rng.choice([-42.0, -44.1, -46.2, -50.4]) if fm == 'NaOH' else round(dsol, 1)
        dneu = rng.choice([-56.7, -58.8, -54.6, -52.5, -57.12])
        Q1 = -dsol_v * mol * 1000; Q2 = -dneu * mol * 1000
        dT1 = Q1 / (4.2 * msol); dT2 = (Q1 + Q2) / (4.2 * msol); dT3 = Q2 / (4.2 * msol)
        if any(abs(x * 10 - round(x * 10)) > 1e-6 for x in (dT1, dT2, dT3)): continue
        w = round(mol * M, 3)
        lvl = ['중', '상', '최'][i % 3]
        ask = rng.choice(['neu', 'sol', 'x'])
        body = [p(f'다음은 염산(HCl)과 {name}({fm})의 반응에서 반응 엔탈피를 구하는 실험이다.'),
                box([f'(가) 25 ℃ 증류수 {num(100 - w, 3)} g이 담긴 열량계에 {fm}(s) {num(w, 3)} g을 넣어 모두 녹인 후 최고 온도를 측정한다.',
                     f'(나) 25 ℃ {num(mol * 10, 3)} M HCl(aq) {num(100 - w, 3)} g이 담긴 열량계에 {fm}(s) {num(w, 3)} g을 넣어 모두 녹인 후 최고 온도를 측정한다.',
                     f'(다) 25 ℃ {num(mol * 20, 3)} M HCl(aq) 50 mL에 25 ℃ {num(mol * 20, 3)} M {fm}(aq) 50 mL를 넣은 후 최고 온도를 측정한다.']),
                table([['실험', '(가)', '(나)', '(다)'], ['최고 온도(℃)', num(25 + dT1, 1), num(25 + dT2, 1), '$x$']])]
        cond = f'(단, {fm}의 화학식량은 {M}이고, 모든 용액의 비열은 4.2 J/(g·℃), 밀도는 1.0 g/mL이며, 발생한 열은 용액이 모두 흡수한다. HCl은 {fm}과 같은 몰수만큼 반응한다.)'
        sol = [f'{fm}의 양: $\\frac{{{m(w, 3)}}}{{{M}}}={m(mol, 3)}$ mol, 각 실험의 용액 질량은 100 g',
               f'(가) 용해: $Q_1=4.2\\times 100\\times {m(dT1, 1)}={m(round(Q1, 1), 1)}$ J → $\\Delta H_{{\\text{{용해}}}}=-\\frac{{{m(round(Q1, 1), 1)}}}{{{m(mol, 3)}}}$ J/mol $={m(dsol_v, 2)}$ kJ/mol',
               f'(나) 용해+중화: $Q_2=4.2\\times 100\\times {m(dT2, 1)}={m(round(Q1 + Q2, 1), 1)}$ J → 중화열 $={m(round(Q1 + Q2, 1), 1)}-{m(round(Q1, 1), 1)}={m(round(Q2, 1), 1)}$ J',
               f'$\\Delta H_{{\\text{{중화}}}}=-\\frac{{{m(round(Q2, 1), 1)}}}{{{m(mol, 3)}}}$ J/mol $={m(dneu, 2)}$ kJ/mol',
               f'(다) 중화만 일어남: 물 {m(mol, 3)} mol → $\\Delta t=\\frac{{{m(round(Q2, 1), 1)}}}{{4.2\\times 100}}={m(dT3, 1)}$ ℃ → $x={m(25 + dT3, 1)}$']
        if ask == 'neu':
            body.append(p(f'H2O 1 몰이 생성되는 중화 반응의 반응 엔탈피($\\Delta H$)는? ' + cond)); v = dneu
            cands = [-dneu, dsol_v, round(dsol_v + dneu, 2), round(dneu * 2, 2), round(dneu / 2, 2), round(-(Q1 + Q2) / mol / 1000, 2)]
            fmtf = lambda x: num(x, 2) + ' kJ/mol'
        elif ask == 'sol':
            body.append(p(f'{fm}(s) 1 몰이 물에 용해될 때의 반응 엔탈피($\\Delta H$)는? ' + cond)); v = dsol_v
            cands = [-dsol_v, dneu, round(dsol_v + dneu, 2), round(dsol_v * 2, 2), round(dsol_v / 2, 2), round(dsol_v * mol, 3)]
            fmtf = lambda x: num(x, 3) + ' kJ/mol'
        else:
            body.append(p(f'$x$는? ' + cond)); v = round(25 + dT3, 1)
            cands = [25 + dT2, 25 + dT1, 25 + dT2 - dT1 / 2, 25 + dT3 * 2, 25 + dT3 / 2, 25 + dT2 + dT1]
            cands = [round(c, 1) for c in cands]; fmtf = lambda x: num(x, 1)
        ch, ans = pick_numeric(rng, v, cands, fmtf)
        if not ch: continue
        add(typ='B4', lv=lvl, ono=193, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='(용해) + (중화) = (용해+중화) : 헤스 법칙', chk=dict(t='neut', v=v))
    # 184형 보기
    S = [('과정 (가)와 (나)에서 발생한 열량의 합은 과정 (다)에서 발생한 열량과 같다.', True, '처음과 나중 상태가 같으므로 헤스 법칙이 성립한다.'),
         ('과정 (가)에서 발생한 열량은 과정 (다)에서 발생한 열량과 같다.', False, '(가)는 용해만, (다)는 용해+중화이므로 (다)가 더 많다.'),
         ('(나)에서 생성된 물의 양(mol)과 (다)에서 생성된 물의 양(mol)은 같다.', True, '반응한 OH⁻의 양이 같으므로 생성된 물의 양도 같다.'),
         ('NaOH 대신 같은 질량의 KOH를 사용해도 같은 온도 결과를 얻는다.', False, '화학식량과 용해 엔탈피가 달라 결과가 달라진다.'),
         ('NaOH(s)의 용해는 발열 과정이다.', True, 'NaOH가 녹으면 온도가 올라간다.'),
         ('중화 반응은 흡열 반응이다.', False, '중화 반응은 발열 반응이다.'),
         ('열량계 밖으로 열이 빠져나가면 구한 반응 엔탈피의 크기가 실제보다 작아진다.', True, '측정되는 온도 변화가 작아진다.'),
         ('(다)에서 HCl과 NaOH의 몰수가 같아야 중화 반응이 완전히 일어난다.', True, 'H⁺와 OH⁻가 1 : 1로 반응한다.')]
    for i in range(300):
        rng = R(10500 + i)
        b = bogi_item(rng, S, 3)
        if not b: continue
        body = [p('다음은 헤스 법칙을 알아보기 위한 실험이다.'), fig('fig/hw/184.png', 26),
                box(['(가) 스타이로폼 컵에 증류수 100 mL를 넣고 NaOH 2.0 g을 녹여 최고 온도를 측정한다.', '(나) 상온으로 식힌 (가)의 수용액에 0.5 M HCl(aq) 100 mL를 섞은 후 최고 온도를 측정한다.',
                     '(다) 0.5 M HCl(aq) 100 mL와 증류수 100 mL, NaOH 2.0 g을 동시에 넣고 최고 온도를 측정한다.']),
                p('이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, 열 손실은 없다.)'), bogi(b['bogi'])]
        add(typ='B4', lv='중', ono=184, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='용해·중화와 헤스 법칙', chk=dict(t='combo', truth=b['truth']))

# ---------------------------------------------------------------- B5 결합 에너지(191, 194, 195)
BE = {'H-H': 436, 'Cl-Cl': 243, 'F-F': 159, 'Br-Br': 193, 'I-I': 151, 'H-Cl': 432, 'H-F': 570, 'H-Br': 366, 'H-I': 299, 'O=O': 498, 'O-H': 463,
      'N≡N': 945, 'N-H': 391, 'C-H': 413, 'C=O': 799, 'C-C': 348, 'C=C': 614, 'C-Cl': 328}
# 반응: (식, 끊는 결합 {결합: 개수}, 생기는 결합)
BR = [('H2(g) + Cl2(g) -> 2HCl(g)', {'H-H': 1, 'Cl-Cl': 1}, {'H-Cl': 2}),
      ('H2(g) + F2(g) -> 2HF(g)', {'H-H': 1, 'F-F': 1}, {'H-F': 2}),
      ('H2(g) + Br2(g) -> 2HBr(g)', {'H-H': 1, 'Br-Br': 1}, {'H-Br': 2}),
      ('H2(g) + I2(g) -> 2HI(g)', {'H-H': 1, 'I-I': 1}, {'H-I': 2}),
      ('2H2(g) + O2(g) -> 2H2O(g)', {'H-H': 2, 'O=O': 1}, {'O-H': 4}),
      ('N2(g) + 3H2(g) -> 2NH3(g)', {'N≡N': 1, 'H-H': 3}, {'N-H': 6}),
      ('CH4(g) + 2O2(g) -> CO2(g) + 2H2O(g)', {'C-H': 4, 'O=O': 2}, {'C=O': 2, 'O-H': 4}),
      ('C2H4(g) + H2(g) -> C2H6(g)', {'C=C': 1, 'C-H': 4, 'H-H': 1}, {'C-C': 1, 'C-H': 6}),
      ('CH4(g) + Cl2(g) -> CH3Cl(g) + HCl(g)', {'C-H': 4, 'Cl-Cl': 1}, {'C-H': 3, 'C-Cl': 1, 'H-Cl': 1}),
      ('2HI(g) -> H2(g) + I2(g)', {'H-I': 2}, {'H-H': 1, 'I-I': 1})]

def eng_bond():
    for i in range(1000):
        rng = R(11000 + i); r = rng.choice(BR); eq, brk, mk_ = r
        be = {k: BE[k] + rng.choice([0, 0, 0, 2, -2, 4, -3]) for k in set(brk) | set(mk_)}
        Eb = sum(be[k] * n for k, n in brk.items()); Ef = sum(be[k] * n for k, n in mk_.items())
        dh = Eb - Ef
        tb = [['결합'] + list(be.keys()), ['결합 에너지(kJ/mol)'] + [str(v) for v in be.values()]]
        lvl = LV[i % 4]
        if lvl in ('하', '중'):
            body = [p('표는 몇 가지 결합의 결합 에너지를 나타낸 것이다.'), table(tb), p(f'이 자료를 이용하여 구한 다음 반응의 반응 엔탈피($\\Delta H$)는?'), box([eq])]
            sol = ['$\\Delta H=$(끊어지는 결합 에너지 합) − (생성되는 결합 에너지 합)',
                   '끊어지는 결합: ' + ' + '.join(f'{k} {n}몰' for k, n in brk.items()) + f' $={m(Eb)}$ kJ',
                   '생성되는 결합: ' + ' + '.join(f'{k} {n}몰' for k, n in mk_.items()) + f' $={m(Ef)}$ kJ',
                   f'$\\Delta H={m(Eb)}-{m(Ef)}={m(dh)}$ kJ']
            cands = [-dh, Eb + Ef, Ef - Eb + 50, dh * 2, round(dh / 2, 1), dh + 100, dh - 100]
            ch, ans = pick_numeric(rng, dh, cands, lambda x: num(x, 1) + ' kJ')
            if not ch: continue
            add(typ='B5', lv=lvl, ono=195, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='$\\Delta H=\\sum E_{\\text{끊는 결합}}-\\sum E_{\\text{생기는 결합}}$', chk=dict(t='bond', Eb=Eb, Ef=Ef, v=dh))
        else:
            # 미지 결합 에너지 구하기(상) / 보기(최)
            ks = list(mk_.keys()) if rng.random() < 0.5 else list(brk.keys())
            unk = rng.choice(ks)
            tb2 = [['결합'] + [k for k in be if k != unk], ['결합 에너지(kJ/mol)'] + [str(be[k]) for k in be if k != unk]]
            if lvl == '상':
                body = [p('다음은 어떤 반응의 열화학 반응식이고, 표는 몇 가지 결합의 결합 에너지이다.'), box([f'{eq}, $\\Delta H={m(dh)}$ kJ']), table(tb2),
                        p(f'{unk} 결합의 결합 에너지(kJ/mol)는?')]
                v = be[unk]
                sol = ['$\\Delta H=$(끊어지는 결합 에너지 합) − (생성되는 결합 에너지 합)', f'{unk} 결합 에너지를 $x$라 하고 식을 세운다.',
                       f'끊어지는 결합 합 $={m(Eb)}$, 생성되는 결합 합 $={m(Ef)}$이 되어야 $\\Delta H={m(dh)}$ kJ이다.', f'∴ $x={v}$ kJ/mol']
                nb = brk.get(unk, 0) + mk_.get(unk, 0)
                cands = [v + 50, v - 50, round(v * 2), round(v / 2), v + abs(dh), v - abs(dh) // 2]
                ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 0) + ' kJ/mol')
                if not ch: continue
                add(typ='B5', lv='상', ono=194, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='결합 에너지로 $\\Delta H$ 역산', chk=dict(t='num', v=v))
            else:
                atoms = sum(n for n in brk.values())
                S = [(f'반응물의 결합을 모두 끊는 데 {m(Eb)} kJ이 필요하다.', True, f'끊는 결합 에너지 합 $={m(Eb)}$ kJ'),
                     (f'반응물의 결합을 모두 끊는 데 {m(Ef)} kJ이 필요하다.', False, f'반응물 쪽은 $={m(Eb)}$ kJ이다.'),
                     ('이 반응은 ' + ('발열' if dh < 0 else '흡열') + ' 반응이다.', True, f'$\\Delta H={m(dh)}$ kJ'),
                     ('이 반응은 ' + ('흡열' if dh < 0 else '발열') + ' 반응이다.', False, f'$\\Delta H={m(dh)}$ kJ'),
                     (f'결합이 생성될 때 에너지를 흡수한다.', False, '결합이 생성될 때는 에너지를 방출한다.'),
                     (f'생성물의 결합 에너지 합이 반응물보다 ' + ('크다.' if dh < 0 else '작다.'), True, '$\\Delta H<0$이면 생성물의 결합 에너지 합이 더 크다.' if dh < 0 else '$\\Delta H>0$이면 생성물의 결합 에너지 합이 더 작다.'),
                     (f'역반응의 반응 엔탈피는 ${m(-dh)}$ kJ이다.', True, '역반응은 부호가 반대이다.')]
                b = bogi_item(rng, S, 3)
                if not b: continue
                body = [p('표는 몇 가지 결합의 결합 에너지이다.'), table(tb), p(f'다음 반응에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), box([eq]), bogi(b['bogi'])]
                add(typ='B5', lv='최', ono=191, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='결합 에너지와 반응 엔탈피', chk=dict(t='combo', truth=b['truth']))

# ---------------------------------------------------------------- B6 생성 엔탈피
HF = {'CO2(g)': -393.5, 'H2O(l)': -285.8, 'H2O(g)': -241.8, 'CH4(g)': -74.8, 'C2H6(g)': -84.7, 'C3H8(g)': -103.8, 'C2H5OH(l)': -277.7, 'CO(g)': -110.5,
      'NH3(g)': -46.1, 'NO(g)': 90.3, 'NO2(g)': 33.2, 'C2H2(g)': 226.7, 'C2H4(g)': 52.3, 'SO2(g)': -296.8, 'SO3(g)': -395.7, 'CaO(s)': -635.1,
      'CaCO3(s)': -1206.9, 'Fe2O3(s)': -824.2, 'HCl(g)': -92.3, 'CH3OH(l)': -238.7, 'C6H12O6(s)': -1273.0, 'N2O4(g)': 9.2}
FR = [({'CH4(g)': 1, 'O2(g)': 2}, {'CO2(g)': 1, 'H2O(l)': 2}), ({'C3H8(g)': 1, 'O2(g)': 5}, {'CO2(g)': 3, 'H2O(l)': 4}),
      ({'C2H5OH(l)': 1, 'O2(g)': 3}, {'CO2(g)': 2, 'H2O(l)': 3}), ({'C2H2(g)': 1, 'O2(g)': Fr(5, 2)}, {'CO2(g)': 2, 'H2O(l)': 1}),
      ({'C2H4(g)': 1, 'H2(g)': 1}, {'C2H6(g)': 1}), ({'CaCO3(s)': 1}, {'CaO(s)': 1, 'CO2(g)': 1}), ({'Fe2O3(s)': 1, 'CO(g)': 3}, {'Fe(s)': 2, 'CO2(g)': 3}),
      ({'2NO2(g)': 0}, {}), ({'NO2(g)': 2}, {'N2O4(g)': 1}), ({'SO2(g)': 2, 'O2(g)': 1}, {'SO3(g)': 2}), ({'CH3OH(l)': 1, 'O2(g)': Fr(3, 2)}, {'CO2(g)': 1, 'H2O(l)': 2}),
      ({'NH3(g)': 4, 'O2(g)': 5}, {'NO(g)': 4, 'H2O(g)': 6}), ({'C6H12O6(s)': 1, 'O2(g)': 6}, {'CO2(g)': 6, 'H2O(l)': 6})]
FR = [r for r in FR if r[1]]
ELEM = {'O2(g)', 'H2(g)', 'Fe(s)', 'N2(g)', 'C(s, 흑연)'}

def side(d): return ' + '.join(('' if c == 1 else (frs(c) if Fr(c).denominator > 1 else str(c))) + k for k, c in d.items())

def eng_form():
    for i in range(900):
        rng = R(12000 + i); r = rng.choice(FR); R_, P_ = r
        hf = {k: round(HF[k] + rng.choice([0, 0, 0.2, -0.2, 1, -1]), 1) for k in list(R_) + list(P_) if k not in ELEM}
        hf2 = dict(hf)
        dh = round(sum(float(c) * hf.get(k, 0) for k, c in P_.items()) - sum(float(c) * hf.get(k, 0) for k, c in R_.items()), 1)
        eq = side(R_) + ' -> ' + side(P_)
        lvl = LV[i % 4]
        tb = [['물질'] + list(hf.keys()), ['$\\Delta H_f^{\\circ}$(kJ/mol)'] + [m(v, 1) for v in hf.values()]]
        if lvl in ('하', '중', '상'):
            body = [p('표는 25 ℃, 1 기압에서 몇 가지 물질의 표준 생성 엔탈피($\\Delta H_f^{\\circ}$)이다.'), table(tb), p('이 자료를 이용하여 구한 다음 반응의 반응 엔탈피($\\Delta H$)는?'), box([eq])]
            ps = ' + '.join(f'({frs(c)})({m(hf.get(k, 0), 1)})' for k, c in P_.items()); rs = ' + '.join(f'({frs(c)})({m(hf.get(k, 0), 1)})' for k, c in R_.items())
            sol = ['$\\Delta H=\\sum(\\text{생성물의 }\\Delta H_f^{\\circ})-\\sum(\\text{반응물의 }\\Delta H_f^{\\circ})$', '가장 안정한 원소(O2(g), H2(g) 등)의 표준 생성 엔탈피는 0이다.',
                   f'$\\Delta H=[{ps}]-[{rs}]$', f'$={m(dh, 1)}$ kJ']
            rev = -dh; plain = round(sum(hf.get(k, 0) for k in P_) - sum(hf.get(k, 0) for k in R_), 1)
            cands = [rev, plain, round(dh * 2, 1), round(dh / 2, 1), round(sum(float(c) * hf.get(k, 0) for k, c in P_.items()), 1), round(dh + 100, 1)]
            ch, ans = pick_numeric(rng, dh, cands, lambda x: num(x, 1) + ' kJ')
            if not ch: continue
            add(typ='B6', lv=lvl, ono=190, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='$\\Delta H=\\sum\\Delta H_f(\\text{생성물})-\\sum\\Delta H_f(\\text{반응물})$', chk=dict(t='form', v=dh))
        else:
            # 최: 연소 엔탈피에서 생성 엔탈피 역산
            cmp_ = [k for k in R_ if k not in ELEM and k != 'O2(g)']
            if not cmp_: continue
            unk = cmp_[0]
            known = {k: v for k, v in hf.items() if k != unk}
            body = [p('다음은 어떤 반응의 열화학 반응식이고, 표는 25 ℃, 1 기압에서 몇 가지 물질의 표준 생성 엔탈피($\\Delta H_f^{\\circ}$)이다.'), box([f'{eq}, $\\Delta H={m(dh, 1)}$ kJ']),
                    table([['물질'] + list(known.keys()), ['$\\Delta H_f^{\\circ}$(kJ/mol)'] + [m(v, 1) for v in known.values()]]), p(f'{unk.split("(")[0]}의 표준 생성 엔탈피(kJ/mol)는?')]
            v = hf[unk]; c = float(R_[unk])
            sol = ['$\\Delta H=\\sum\\Delta H_f(\\text{생성물})-\\sum\\Delta H_f(\\text{반응물})$에 $\\Delta H_f(\\text{' + unk.split('(')[0] + '})=x$를 넣는다.',
                   f'${m(dh, 1)}={m(round(sum(float(c2) * hf.get(k, 0) for k, c2 in P_.items()), 1), 1)}-({m(round(sum(float(c2) * hf.get(k, 0) for k, c2 in R_.items() if k != unk), 1), 1)}+{frs(c)}x)$',
                   f'∴ $x={m(v, 1)}$ kJ/mol']
            cands = [-v, round(v + dh, 1), round(v * 2, 1), round(v - 100, 1), round(-v - dh, 1), round(v / 2, 1)]
            ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 1) + ' kJ/mol')
            if not ch: continue
            add(typ='B6', lv='최', ono=190, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='생성 엔탈피 역산', chk=dict(t='num', v=v))

def run():
    eng_hess_symbol(); eng_hess_num(); eng_hess_diagram(); eng_hess_concept(); eng_neutral(); eng_bond(); eng_form()
