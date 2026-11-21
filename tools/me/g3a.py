"""Ⅲ-A 반응 엔탈피와 열화학 반응식: 개념 · 엔탈피 도표 · 사례 · 열량 계산 · 열량계"""
from core import *
import svg

# 연소 반응(1 몰 기준): 화학식, 이름, 몰질량, ΔH(kJ/mol), 반응식
FUEL = [
 ('CH4', '메테인', 16, -890.8, 'CH4(g) + 2O2(g) -> CO2(g) + 2H2O(l)'),
 ('C2H2', '에타인', 26, -1300, 'C2H2(g) + \\frac{5}{2}O2(g) -> 2CO2(g) + H2O(l)'),
 ('C2H6', '에테인', 30, -1560, 'C2H6(g) + \\frac{7}{2}O2(g) -> 2CO2(g) + 3H2O(l)'),
 ('C3H8', '프로페인', 44, -2220, 'C3H8(g) + 5O2(g) -> 3CO2(g) + 4H2O(l)'),
 ('C4H10', '뷰테인', 58, -2878, 'C4H10(g) + \\frac{13}{2}O2(g) -> 4CO2(g) + 5H2O(l)'),
 ('C2H5OH', '에탄올', 46, -1367, 'C2H5OH(l) + 3O2(g) -> 2CO2(g) + 3H2O(l)'),
 ('CH3OH', '메탄올', 32, -726, 'CH3OH(l) + \\frac{3}{2}O2(g) -> CO2(g) + 2H2O(l)'),
 ('H2', '수소', 2, -285.8, 'H2(g) + \\frac{1}{2}O2(g) -> H2O(l)'),
 ('C6H12O6', '포도당', 180, -2802.5, 'C6H12O6(s) + 6O2(g) -> 6CO2(g) + 6H2O(l)'),
 ('C', '흑연', 12, -393.5, 'C(s, 흑연) + O2(g) -> CO2(g)'),
 ('CO', '일산화 탄소', 28, -283.0, 'CO(g) + \\frac{1}{2}O2(g) -> CO2(g)'),
]
# 여러 반응: 반응식, ΔH, 기준 물질(화학식, 이름, 몰질량, 반응식에서의 계수)
RXN = [
 ('N2(g) + O2(g) -> 2NO(g)', 181, ('N2', '질소', 28, 1)),
 ('CaCO3(s) -> CaO(s) + CO2(g)', 179.2, ('CaCO3', '탄산 칼슘', 100, 1)),
 ('2H2(g) + O2(g) -> 2H2O(g)', -483.6, ('H2', '수소', 2, 2)),
 ('N2(g) + 3H2(g) -> 2NH3(g)', -92.2, ('NH3', '암모니아', 17, 2)),
 ('4Fe(s) + 3O2(g) -> 2Fe2O3(s)', -1648.4, ('Fe', '철', 56, 4)),
 ('2HgO(s) -> 2Hg(l) + O2(g)', 181.6, ('HgO', '산화 수은(Ⅱ)', 217, 2)),
 ('H2O(l) -> H2O(g)', 44.0, ('H2O', '물', 18, 1)),
 ('2H2O2(l) -> 2H2O(l) + O2(g)', -196.0, ('H2O2', '과산화 수소', 34, 2)),
 ('NH4NO3(s) -> NH4^{+}(aq) + NO3^{-}(aq)', 25.7, ('NH4NO3', '질산 암모늄', 80, 1)),
 ('NaOH(s) -> Na^{+}(aq) + OH^{-}(aq)', -44.5, ('NaOH', '수산화 나트륨', 40, 1)),
 ('2NO2(g) -> N2O4(g)', -57.2, ('NO2', '이산화 질소', 46, 2)),
 ('C(s, 흑연) + H2O(g) -> CO(g) + H2(g)', 131.3, ('C', '흑연', 12, 1)),
]

def heat_s(x, nd=1): return num(round(x, nd), nd)

# ---------------------------------------------------------------- A1·A3 개념 문장
def concept_stmts(rng):
    f = rng.choice(FUEL); r = rng.choice(RXN)
    dh = r[1]; exo = dh < 0
    S = [
     ('엔탈피($H$)는 일정한 온도와 압력에서 물질이 가지는 고유한 에너지이다.', True, '엔탈피는 물질이 특정 온도·압력에서 가지는 열 함량이다.'),
     ('반응 엔탈피($\\Delta H$)는 반응물의 엔탈피 합에서 생성물의 엔탈피 합을 뺀 값이다.', False, '$\\Delta H=H_{\\text{생성물}}-H_{\\text{반응물}}$이다.'),
     ('반응 엔탈피($\\Delta H$)는 생성물의 엔탈피 합에서 반응물의 엔탈피 합을 뺀 값이다.', True, '$\\Delta H=H_{\\text{생성물}}-H_{\\text{반응물}}$이다.'),
     ('같은 물질 1 몰의 엔탈피는 기체 > 액체 > 고체 순이다.', True, '상태 변화에서 고체 → 액체 → 기체로 갈 때 열을 흡수하므로 기체의 엔탈피가 가장 크다.'),
     ('같은 물질이면 상태에 관계없이 엔탈피가 같다.', False, '같은 물질이라도 상태에 따라 엔탈피가 다르다.'),
     ('열화학 반응식에서 계수를 2배로 하면 반응 엔탈피도 2배가 된다.', True, '반응 엔탈피는 반응하는 물질의 양에 비례한다.'),
     ('열화학 반응식에서 계수를 2배로 해도 반응 엔탈피는 변하지 않는다.', False, '반응 엔탈피는 물질의 양에 비례하므로 2배가 된다.'),
     ('역반응의 반응 엔탈피는 정반응과 크기가 같고 부호가 반대이다.', True, '정반응에서 방출(흡수)한 만큼 역반응에서 흡수(방출)한다.'),
     ('역반응의 반응 엔탈피는 정반응과 크기와 부호가 모두 같다.', False, '역반응의 $\\Delta H$는 정반응과 크기가 같고 부호가 반대이다.'),
     ('열화학 반응식에는 물질의 상태를 반드시 표시해야 한다.', True, '상태에 따라 엔탈피가 달라지므로 상태를 표시한다.'),
     ('반응 조건을 따로 쓰지 않은 열화학 반응식은 보통 25 ℃, 1 기압에서의 값이다.', True, '표시가 없으면 25 ℃, 1 기압(열역학 표준 상태)으로 본다.'),
     ('반응 엔탈피는 온도와 압력에 관계없이 항상 일정하다.', False, '반응 엔탈피는 온도와 압력에 따라 달라지므로 조건을 표시한다.'),
     ('열화학 반응식으로 각 물질이 가진 엔탈피의 크기를 알 수 있다.', False, '$\\Delta H$는 엔탈피의 차이일 뿐이며 각 물질의 엔탈피 값은 알 수 없다.'),
     ('열화학 반응식으로 반응물과 생성물의 엔탈피 차이를 알 수 있다.', True, '$\\Delta H$가 곧 생성물과 반응물의 엔탈피 차이이다.'),
     ('$\\Delta H>0$인 반응은 반응이 일어날 때 주위의 온도가 높아진다.', False, '$\\Delta H>0$은 흡열 반응이므로 주위의 온도가 낮아진다.'),
     ('$\\Delta H<0$인 반응은 생성물이 반응물보다 에너지 면에서 안정하다.', True, '발열 반응은 생성물의 엔탈피가 더 낮아 더 안정하다.'),
     ('발열 반응에서는 계의 엔탈피가 증가한다.', False, '발열 반응에서는 계의 엔탈피가 감소하고, 감소한 만큼 열로 방출된다.'),
     ('흡열 반응은 반응물의 엔탈피 합이 생성물의 엔탈피 합보다 작다.', True, '흡열 반응은 $H_{\\text{생성물}}>H_{\\text{반응물}}$이다.'),
     ('반응 엔탈피의 단위로는 kJ 또는 kJ/mol을 쓴다.', True, '반응 엔탈피는 에너지이므로 kJ(1 몰 기준이면 kJ/mol)로 나타낸다.'),
     ('물의 기화는 열을 방출하는 과정이다.', False, '기화는 열을 흡수하는 흡열 과정이다.'),
     ('수증기가 액화될 때 열이 방출된다.', True, '액화는 발열 과정이다.'),
     ('반응이 빠르게 일어나는 반응은 모두 발열 반응이다.', False, '반응 속도와 발열·흡열 여부는 관계가 없다.'),
     (f'{f[1]}의 연소 반응은 $\\Delta H<0$이다.', True, '연소 반응은 열과 빛을 내는 발열 반응이다.'),
     (fmt_rx(r) + '의 역반응은 ' + ('흡열' if exo else '발열') + ' 반응이다.', True, f'정반응의 $\\Delta H={m(dh, 1)}$ kJ이므로 역반응은 $\\Delta H={m(-dh, 1)}$ kJ이다.'),
     (fmt_rx(r) + '은(는) ' + ('흡열' if exo else '발열') + ' 반응이다.', False, f'$\\Delta H={m(dh, 1)}$ kJ ' + ('< 0이므로 발열' if exo else '> 0이므로 흡열') + ' 반응이다.'),
    ]
    return S

def fmt_rx(r): return f'{r[0]}, $\\Delta H={m(r[1], 1)}$ kJ'

def eng_concept():
    for i in range(700):
        rng = R(1000 + i); S = concept_stmts(rng)
        k = i % 7
        if k in (0, 1):     # 옳은 것은 / 옳지 않은 것은 (하)
            want = k == 0; o = one_of(rng, S, want)
            if not o: continue
            body = [p('엔탈피와 열화학 반응식에 대한 설명으로 ' + ('옳은' if want else '옳지 <u>않은</u>') + ' 것은?')]
            add(typ='A1' if i % 2 else 'A3', lv='하', ono=161 if i % 2 else 158, hw='s', body=body, ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v',
                key='$\\Delta H=H_{\\text{생성물}}-H_{\\text{반응물}}$', chk=dict(t='one', want=want))
        else:
            b = bogi_item(rng, S, 3 if k < 5 else 4)
            if not b: continue
            body = [p('반응 엔탈피와 열화학 반응식에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])]
            add(typ='A3' if k % 2 else 'A1', lv='중' if k < 5 else '상', ono=171 if k % 2 else 161, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'],
                key='열화학 반응식의 표기 규칙', chk=dict(t='combo', truth=b['truth']))

# ---------------------------------------------------------------- A3 열화학 반응식 고르기·쓰기(155,159,170)
def eng_write():
    n = 0
    for i in range(900):
        rng = R(2000 + i)
        f = rng.choice(FUEL[:9])
        name, M, dh, eq = f[1], f[2], f[3], f[4]
        mol = rng.choice([0.1, 0.2, 0.25, 0.5, 2, 1.5, 0.4, 0.05])
        mass = round(mol * M, 3); Q = round(-dh * mol, 2)
        lvl = ['하', '중', '중', '상'][i % 4]
        # 정답·오답 반응식
        def eqs(c, v):
            if c == 1: return f'{eq}, $\\Delta H={m(v, 1)}$ kJ'
            return f'{c}' + eq.replace(' + ', f' + ', 1) if False else None
        wrong_q = Q
        opts = [(f'{eq}, $\\Delta H={m(dh, 1)}$ kJ', True),
                (f'{eq}, $\\Delta H={m(-dh, 1)}$ kJ', False),
                (f'{eq}, $\\Delta H={m(-Q, 1)}$ kJ', False),
                (f'{eq}, $\\Delta H={m(Q, 1)}$ kJ', False),
                (f'{eq.replace("(l)", "(g)")}, $\\Delta H={m(dh, 1)}$ kJ' if '(l)' in eq else f'{eq}, $\\Delta H={m(dh * 2, 1)}$ kJ', False)]
        if abs(Q + dh) < 1e-6:  # mol=1이면 중복 → 다른 오답
            continue
        if opts[2][0] == opts[0][0] or opts[3][0] == opts[1][0]: continue
        rng.shuffle(opts); ans = [k for k, o in enumerate(opts) if o[1]][0] + 1
        if lvl == '하':
            body = [p(f'25 ℃, 1 기압에서 {name}({f[0]}) 1 몰이 완전 연소할 때 {heat_s(-dh)} kJ의 열이 발생한다. {name}의 연소 반응을 열화학 반응식으로 옳게 나타낸 것은?')]
            opts = [(f'{eq}, $\\Delta H={m(dh, 1)}$ kJ', True), (f'{eq}, $\\Delta H={m(-dh, 1)}$ kJ', False),
                    (f'{eq}, $\\Delta H={m(2 * dh, 1)}$ kJ', False), (f'{eq}, $\\Delta H={m(dh / 2, 1)}$ kJ', False),
                    (f'{eq.replace("(l)", "(g)") if "(l)" in eq else eq.replace("(g)", "(l)", 1)}, $\\Delta H={m(dh, 1)}$ kJ', False)]
            rng.shuffle(opts); ans = [k for k, o in enumerate(opts) if o[1]][0] + 1
            sol = [f'{name} 1 몰이 연소할 때 열이 발생(발열)하므로 $\\Delta H={m(dh, 1)}$ kJ이다.', '연소 생성물인 물은 25 ℃에서 액체이므로 H2O(l)로 쓴다.',
                   '열을 방출하는 반응의 $\\Delta H$는 음수로, 1 몰 기준이므로 계수와 $\\Delta H$를 그대로 쓴다.']
        else:
            body = [p(f'{name}({f[0]}) {num(mass, 3)} g이 완전 연소하면 {heat_s(Q, 2)} kJ의 열이 발생한다. 다음 중 {name}의 연소 반응을 열화학 반응식으로 옳게 나타낸 것은? (단, {f[0]}의 몰질량은 {M} g/mol이다.)')]
            sol = [f'{f[0]} {num(mass, 3)} g의 양: $\\frac{{{m(mass, 3)}}}{{{M}}}={m(mol, 3)}$ mol',
                   f'{m(mol, 3)} mol에서 {heat_s(Q, 2)} kJ이 발생하므로 1 mol이면 $\\frac{{{m(Q, 2)}}}{{{m(mol, 3)}}}={m(-dh, 1)}$ kJ이 발생한다.',
                   f'열이 발생(발열)하므로 $\\Delta H={m(dh, 1)}$ kJ이다.']
            if lvl == '상':
                body[0] = p(f'{name}({f[0]}) {num(mass, 3)} g이 완전 연소할 때 발생한 열량은 {heat_s(Q, 2)} kJ이었다. 이 결과로부터 {name} 1 몰의 연소 반응을 나타낸 열화학 반응식으로 옳은 것은? (단, 25 ℃, 1 기압이며 {f[0]}의 몰질량은 {M} g/mol이고, 생성된 물은 모두 액체이다.)')
        add(typ='A3', lv=lvl, ono=170 if lvl != '하' else 155, hw='v' if lvl != '하' else 's', body=body, ch=[o[0] for o in opts], ans=ans, sol=sol, chl='v',
            key='열화학 반응식은 1 몰 기준 · 발열이면 $\\Delta H<0$', chk=dict(t='thermo', dh=dh, Q=Q, mol=mol))
        n += 1

# ---------------------------------------------------------------- A4 열량 계산(165)
def eng_heat():
    for i in range(1100):
        rng = R(3000 + i); lvl = LV[i % 4]
        if lvl in ('하', '중'):
            pool = FUEL + [(r[2][0], r[2][1], r[2][2], r[1] / r[2][3], r[0]) for r in RXN]
            f = rng.choice(pool)
            fm, name, M, dh1, eq = f
            mol = rng.choice([0.1, 0.2, 0.25, 0.4, 0.5, 1.5, 2, 2.5, 3, 0.05])
            mass = round(mol * M, 3); Q = abs(dh1) * mol
            word = '방출' if dh1 < 0 else '흡수'
            given = eq if f in FUEL else next(r[0] for r in RXN if r[2][0] == fm)
            dhgiven = dh1 if f in FUEL else next(r[1] for r in RXN if r[2][0] == fm)
            coef = 1 if f in FUEL else next(r[2][3] for r in RXN if r[2][0] == fm)
            if lvl == '하':
                body = [p('다음은 어떤 반응의 열화학 반응식이다.'), box([f'{given}, $\\Delta H={m(dhgiven, 1)}$ kJ']),
                        p(f'{fm} {num(mol, 3)} 몰이 반응할 때 {word}하는 열량(kJ)은?')]
                sol = [f'열화학 반응식에서 {fm} {coef} 몰이 반응할 때 {heat_s(abs(dhgiven))} kJ을 {word}한다.',
                       f'{fm} 1 몰당 $\\frac{{{m(abs(dhgiven), 1)}}}{{{coef}}}={m(abs(dh1), 2)}$ kJ' if coef != 1 else f'{fm} 1 몰당 {heat_s(abs(dh1))} kJ',
                       f'{num(mol, 3)} 몰이면 $' + m(mol, 3) + '\\times ' + m(abs(dh1), 2) + '=' + m(round(Q, 2), 2) + '$ kJ']
                cands = [abs(dhgiven) * mol, abs(dh1), Q * 2, Q / 2, abs(dhgiven) / mol if mol else None, Q * coef if coef > 1 else Q * 3, Q * 4]
            else:
                body = [p('다음은 어떤 반응의 열화학 반응식이다.'), box([f'{given}, $\\Delta H={m(dhgiven, 1)}$ kJ']),
                        p(f'{fm} {num(mass, 3)} g이 반응할 때 {word}하는 열량(kJ)은? (단, {fm}의 몰질량은 {M} g/mol이다.)')]
                sol = [f'{fm}의 양: $\\frac{{{m(mass, 3)}}}{{{M}}}={m(mol, 3)}$ mol',
                       f'{fm} 1 몰당 {word} 열량: ' + (f'$\\frac{{{m(abs(dhgiven), 1)}}}{{{coef}}}={m(abs(dh1), 2)}$ kJ' if coef != 1 else f'{heat_s(abs(dh1))} kJ'),
                       f'$Q={m(mol, 3)}\\times {m(abs(dh1), 2)}={m(round(Q, 2), 2)}$ kJ']
                cands = [abs(dhgiven) * mol, mass * abs(dh1), Q * 2, Q / 2, abs(dh1), Q * coef if coef > 1 else Q * 4, Q * 10]
            ch, ans = pick_numeric(rng, round(Q, 2), [round(c, 2) for c in cands if c], lambda v: num(v, 2) + ' kJ')
            if not ch: continue
            add(typ='A4', lv=lvl, ono=165, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='열량 = 물질의 양(mol) × 1 몰당 반응 엔탈피', chk=dict(t='num', v=round(Q, 2)))
        elif lvl == '상':
            # 연소열로 물 데우기
            f = rng.choice(FUEL[:8]); fm, name, M, dh, eq = f
            mol = rng.choice([0.01, 0.02, 0.025, 0.04, 0.05, 0.1]); mass = round(mol * M, 3)
            eff = rng.choice([100, 80, 60, 50, 40]); W = rng.choice([500, 1000, 2000, 250, 400])
            Qj = -dh * mol * 1000 * eff / 100
            dT = Qj / (4.2 * W)
            if abs(dT * 10 - round(dT * 10)) > 1e-6 or dT > 90: continue
            body = [p(f'{name}({fm})의 연소 반응의 열화학 반응식은 다음과 같다.'), box([f'{eq}, $\\Delta H={m(dh, 1)}$ kJ']),
                    p(f'{name} {num(mass, 3)} g을 완전 연소시켜 발생한 열의 {eff} %가 물 {W} g에 흡수되었을 때, 물의 온도 변화(℃)는? (단, {fm}의 몰질량은 {M} g/mol, 물의 비열은 4.2 J/(g·℃)이다.)' if eff < 100 else
                      f'{name} {num(mass, 3)} g을 완전 연소시켜 발생한 열이 모두 물 {W} g에 흡수되었을 때, 물의 온도 변화(℃)는? (단, {fm}의 몰질량은 {M} g/mol, 물의 비열은 4.2 J/(g·℃)이다.)')]
            sol = [f'{fm}의 양: $\\frac{{{m(mass, 3)}}}{{{M}}}={m(mol, 3)}$ mol',
                   f'발생한 열: ${m(mol, 3)}\\times {m(-dh, 1)}={m(round(-dh * mol, 3), 3)}$ kJ $={m(round(-dh * mol * 1000, 1), 1)}$ J',
                   (f'물이 흡수한 열: ${m(round(-dh * mol * 1000, 1), 1)}\\times {m(eff / 100, 2)}={m(round(Qj, 1), 1)}$ J' if eff < 100 else '물이 흡수한 열 = 발생한 열'),
                   f'$\\Delta t=\\frac{{Q}}{{cm}}=\\frac{{{m(round(Qj, 1), 1)}}}{{4.2\\times {W}}}={m(round(dT, 1), 1)}$ ℃']
            cands = [dT * 2, dT / 2, dT * 100 / eff if eff < 100 else dT * 1.25, dT * eff / 100 if eff < 100 else dT * 0.8, dT * 4.2, dT / 4.2, dT * 10]
            ch, ans = pick_numeric(rng, round(dT, 1), [round(c, 1) for c in cands], lambda v: num(v, 1) + ' ℃')
            if not ch: continue
            add(typ='A4', lv='상', ono=165, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='연소열과 $Q=cm\\Delta t$의 연결', chk=dict(t='num', v=round(dT, 1)))
        else:
            # 최: 두 연료 혼합물
            a, b = rng.sample(FUEL[:7], 2)
            na = rng.choice([0.1, 0.2, 0.3, 0.4, 0.5]); nb = rng.choice([0.1, 0.2, 0.3, 0.5])
            mass = round(na * a[2] + nb * b[2], 3); Q = round(-a[3] * na - b[3] * nb, 2)
            ask = rng.choice(['a', 'b'])
            body = [p('다음은 25 ℃, 1 기압에서 두 물질의 연소 반응에 대한 열화학 반응식이다.'), box([f'{a[4]}, $\\Delta H={m(a[3], 1)}$ kJ', f'{b[4]}, $\\Delta H={m(b[3], 1)}$ kJ']),
                    p(f'{a[1]}({a[0]})과 {b[1]}({b[0]})의 혼합물 {num(mass, 3)} g을 완전 연소시켰더니 {num(Q, 2)} kJ의 열이 발생하였다. 혼합물 속 ' + (f'{a[1]}의 질량(g)은?' if ask == 'a' else f'{b[1]}의 질량(g)은?') + f' (단, {a[0]}, {b[0]}의 몰질량은 각각 {a[2]}, {b[2]} g/mol이다.)')]
            ans_v = round(na * a[2], 3) if ask == 'a' else round(nb * b[2], 3)
            sol = [f'{a[0]}를 $x$ mol, {b[0]}를 $y$ mol이라 하면',
                   f'질량: ${a[2]}x+{b[2]}y={m(mass, 3)}$ … ①', f'열량: ${m(-a[3], 1)}x+{m(-b[3], 1)}y={m(Q, 2)}$ … ②',
                   f'①, ②를 연립하면 $x={m(na, 2)}$, $y={m(nb, 2)}$',
                   f'구하는 질량 = ' + (f'${m(na, 2)}\\times {a[2]}={m(ans_v, 3)}$ g' if ask == 'a' else f'${m(nb, 2)}\\times {b[2]}={m(ans_v, 3)}$ g')]
            other = round(nb * b[2], 3) if ask == 'a' else round(na * a[2], 3)
            cands = [other, mass / 2, ans_v * 2, ans_v / 2, round(na if ask == 'a' else nb, 2) * 10, mass - ans_v / 2]
            ch, ans = pick_numeric(rng, ans_v, [round(c, 3) for c in cands], lambda v: num(v, 3) + ' g')
            if not ch: continue
            add(typ='A4', lv='최', ono=165, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='혼합물: 질량식과 열량식을 연립', chk=dict(t='mix', na=na, nb=nb, Ma=a[2], Mb=b[2], ha=a[3], hb=b[3], mass=mass, Q=Q, ask=ask, v=ans_v))

# ---------------------------------------------------------------- A5 열량계(173,174,177)
SOLUTES = [('NH4NO3', '질산 암모늄', 80, 25.7), ('NaOH', '수산화 나트륨', 40, -44.5), ('KNO3', '질산 칼륨', 101, 34.9), ('CaCl2', '염화 칼슘', 111, -81.3),
           ('KCl', '염화 칼륨', 74.5, 17.2), ('NH4Cl', '염화 암모늄', 53.5, 14.8), ('LiCl', '염화 리튬', 42.5, -37.0), ('KOH', '수산화 칼륨', 56, -57.6)]

def eng_calor():
    for i in range(1200):
        rng = R(4000 + i); lvl = LV[i % 4]
        c = 4.2
        if lvl == '하':
            W = rng.choice([50, 100, 150, 200, 250, 500]); dT = rng.choice([2, 3, 4, 5, 6, 7, 8, 10, 12, 15]); unit = rng.choice(['J', 'kJ'])
            Q = c * W * dT
            body = [p(f'물 {W} g의 온도를 {dT} ℃ 높이는 데 필요한 열량({unit})은? (단, 물의 비열은 4.2 J/(g·℃)이다.)')]
            v = Q if unit == 'J' else Q / 1000
            sol = [f'$Q=cm\\Delta t=4.2\\times {W}\\times {dT}={m(Q, 1)}$ J' + ('' if unit == 'J' else f' $={m(Q / 1000, 3)}$ kJ')]
            cands = [v * 2, v / 2, W * dT if unit == 'J' else W * dT / 1000, v * 10, v / 10, v / 4.2 * 4.18 * 0 + v * 1.5]
            ch, ans = pick_numeric(rng, round(v, 3), [round(x, 3) for x in cands], lambda x: num(x, 3) + ' ' + unit)
            if not ch: continue
            add(typ='A5', lv='하', ono=173, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='$Q=cm\\Delta t$', chk=dict(t='num', v=round(v, 3)))
        elif lvl == '중':
            s = rng.choice(SOLUTES); fm, name, M, dh = s
            mol = rng.choice([0.05, 0.1, 0.02, 0.04, 0.025, 0.2]); w = round(mol * M, 3)
            W = rng.choice([100, 150, 200, 96, 190, 250])
            msol = W + w
            Qj = abs(dh) * mol * 1000
            dT = Qj / (c * msol)
            dT = round(dT, 1)
            if dT < 0.5: continue
            Qr = c * msol * dT; dhm = round(Qr / mol / 1000 * (1 if dh > 0 else -1), 1)
            t1 = rng.choice([20, 22, 24, 25]); t2 = round(t1 + (dT if dh < 0 else -dT), 1)
            body = [p(f'그림과 같은 간이 열량계에 물 {W} g을 넣고 {name}({fm}) {num(w, 3)} g을 넣어 모두 녹였더니 용액의 온도가 {t1} ℃에서 {num(t2, 1)} ℃로 변하였다.'), fig('fig/hw/173.png', 26),
                    p(f'{fm} 1 몰이 물에 용해될 때의 반응 엔탈피($\\Delta H$)는? (단, {fm}의 화학식량은 {num(M, 1)}이고, 용액의 비열은 4.2 J/(g·℃)이며, 열량계와 외부 사이의 열 출입은 무시한다.)')]
            sol = [f'온도가 ' + ('올라갔으므로 용해 과정에서 열을 방출(발열, $\\Delta H<0$)' if dh < 0 else '내려갔으므로 용해 과정에서 열을 흡수(흡열, $\\Delta H>0$)') + '한다.',
                   f'용액의 질량 $={W}+{m(w, 3)}={m(msol, 3)}$ g, $\\Delta t={m(dT, 1)}$ ℃',
                   f'$Q=4.2\\times {m(msol, 3)}\\times {m(dT, 1)}={m(round(Qr, 1), 1)}$ J',
                   f'{fm}의 양 $=\\frac{{{m(w, 3)}}}{{{num(M, 1)}}}={m(mol, 3)}$ mol',
                   f'$\\Delta H=' + ('-' if dh < 0 else '+') + f'\\frac{{{m(round(Qr, 1), 1)}}}{{{m(mol, 3)}}}$ J/mol $={m(dhm, 1)}$ kJ/mol']
            wrong_w = round(c * W * dT / mol / 1000 * (1 if dh > 0 else -1), 1)
            cands = [-dhm, wrong_w, -wrong_w, round(dhm * mol, 2), round(dhm * 2, 1), round(dhm / 2, 1)]
            ch, ans = pick_numeric(rng, dhm, cands, lambda x: num(x, 2) + ' kJ/mol')
            if not ch: continue
            add(typ='A5', lv='중', ono=173, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='용액 전체 질량으로 $Q=cm\\Delta t$ → 1 몰당 $\\Delta H$', chk=dict(t='calor', W=W, w=w, dT=dT, mol=mol, sign=1 if dh > 0 else -1, v=dhm))
        elif lvl == '상':
            # 통열량계: 물 + 열량계 열용량
            f = rng.choice(FUEL[:8] + [('C10H8', '나프탈렌', 128, -5156, '')]); fm, name, M, dh, eq = f
            mol = rng.choice([0.01, 0.005, 0.02, 0.004, 0.0125]); w = round(mol * M, 4)
            W = rng.choice([1000, 1500, 2000, 2500]); Cc = rng.choice([500, 800, 1000, 1200, 840])
            Qj = -dh * mol * 1000
            dT = Qj / (c * W + Cc); dT = round(dT, 2)
            if dT < 0.5 or dT > 40: continue
            Qr = (c * W + Cc) * dT; dhm = round(-Qr / mol / 1000, 0)
            body = [p(f'다음은 {name}({fm})의 연소 엔탈피를 구하기 위한 실험이다.'), fig('fig/hw/174.png', 30),
                    box([f'(가) 통열량계에 물 {W} g을 넣고 처음 온도를 측정한다.', f'(나) {name} {num(w, 4)} g을 시료 접시에 넣고 완전 연소시킨 후 최고 온도를 측정하였더니 처음보다 {num(dT, 2)} ℃ 높아졌다.']),
                    p(f'{fm} 1 몰의 연소 엔탈피($\\Delta H$)에 가장 가까운 값은? (단, 물의 비열은 4.2 J/(g·℃), 열량계의 열용량은 {Cc} J/℃, {fm}의 몰질량은 {M} g/mol이다.)')]
            sol = [f'물이 얻은 열: $4.2\\times {W}\\times {m(dT, 2)}={m(round(c * W * dT, 1), 1)}$ J', f'열량계가 얻은 열: ${Cc}\\times {m(dT, 2)}={m(round(Cc * dT, 1), 1)}$ J',
                   f'발생한 열 $Q={m(round(Qr, 1), 1)}$ J', f'{fm}의 양: $\\frac{{{m(w, 4)}}}{{{M}}}={m(mol, 4)}$ mol',
                   f'$\\Delta H=-\\frac{{{m(round(Qr, 1), 1)}}}{{{m(mol, 4)}}}$ J/mol $\\approx {m(dhm, 0)}$ kJ/mol']
            noC = round(-c * W * dT / mol / 1000, 0)
            cands = [-dhm, noC, round(dhm * mol, 1), round(dhm * 2, 0), round(dhm / 2, 0), -noC]
            ch, ans = pick_numeric(rng, dhm, cands, lambda x: num(x, 0) + ' kJ/mol')
            if not ch: continue
            add(typ='A5', lv='상', ono=174, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='통열량계: $Q=(cm+C)\\Delta t$', chk=dict(t='bomb', W=W, C=Cc, dT=dT, mol=mol, v=dhm))
        else:
            # 최: 열량계 자료 해석 보기형 (177형)
            s = rng.choice(SOLUTES); fm, name, M, dh = s
            mol = rng.choice([0.05, 0.1, 0.02, 0.04]); w = round(mol * M, 3); W = rng.choice([100, 200, 96, 150])
            msol = W + w; dT = round(abs(dh) * mol * 1000 / (c * msol), 1)
            if dT < 0.5: continue
            Qr = c * msol * dT; dhm = round(Qr / mol / 1000, 1) * (1 if dh > 0 else -1)
            up = dh < 0
            S = [(f'{fm}이 물에 녹는 과정은 ' + ('발열' if up else '흡열') + ' 과정이다.', True, '온도가 ' + ('올라갔으므로 발열' if up else '내려갔으므로 흡열') + '이다.'),
                 (f'{fm}이 물에 녹는 과정은 ' + ('흡열' if up else '발열') + ' 과정이다.', False, '온도가 ' + ('올라갔으므로 발열' if up else '내려갔으므로 흡열') + '이다.'),
                 (f'용액이 ' + ('얻은' if up else '잃은') + f' 열량은 ${m(round(Qr, 1), 1)}$ J이다.', True, f'$Q=4.2\\times {m(msol, 3)}\\times {m(dT, 1)}={m(round(Qr, 1), 1)}$ J'),
                 (f'용액이 ' + ('얻은' if up else '잃은') + f' 열량은 ${m(round(c * W * dT, 1), 1)}$ J이다.', False, f'질량은 용액 전체 {m(msol, 3)} g으로 계산해야 하므로 ${m(round(Qr, 1), 1)}$ J이다.'),
                 (f'{fm} 1 몰이 녹을 때 $\\Delta H={m(dhm, 1)}$ kJ/mol이다.', True, f'$\\Delta H=\\frac{{{m(round(Qr, 1), 1)}\\text{{ J}}}}{{{m(mol, 3)}\\text{{ mol}}}}$, 부호 ' + ('−' if up else '+') + f' → ${m(dhm, 1)}$ kJ/mol'),
                 (f'{fm} 1 몰이 녹을 때 $\\Delta H={m(-dhm, 1)}$ kJ/mol이다.', False, f'부호가 반대이다. ${m(dhm, 1)}$ kJ/mol이다.'),
                 (f'{fm}을 {num(2 * w, 3)} g 녹이면 1 몰당 반응 엔탈피도 2배가 된다.', False, '1 몰당 반응 엔탈피는 녹인 양과 관계없이 일정하다(전체 열량만 2배).'),
                 (f'{fm}이 다 녹지 않았다면 측정한 온도 변화는 실제보다 작다.', True, '녹은 양만큼만 열이 출입하므로 온도 변화가 작아진다.'),
                 ('열량계 밖으로 열이 빠져나가면 구한 $\\Delta H$의 절댓값이 실제보다 작아진다.', True, '손실된 열만큼 온도 변화가 작게 측정된다.')]
            b = bogi_item(rng, S, 3)
            if not b: continue
            t1 = 25; t2 = round(t1 + (dT if up else -dT), 1)
            body = [p(f'다음은 {name}({fm})의 용해 과정에서 출입하는 열량을 알아보기 위한 실험이다.'),
                    box([f'(가) 간이 열량계에 25 ℃ 물 {W} g을 넣는다.', f'(나) {fm} {num(w, 3)} g을 넣어 모두 녹인 후 용액의 최고(또는 최저) 온도를 측정하였더니 {num(t2, 1)} ℃였다.']),
                    p(f'이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은? (단, {fm}의 화학식량은 {num(M, 1)}, 용액의 비열은 4.2 J/(g·℃)이다.)'), bogi(b['bogi'])]
            add(typ='A5', lv='최', ono=177, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='열량계 실험 해석', chk=dict(t='combo', truth=b['truth']))

# ---------------------------------------------------------------- A2 엔탈피 도표(162,163,166,167,168,175)
def eng_diagram():
    for i in range(900):
        rng = R(5000 + i)
        r = rng.choice(RXN + [(f[4], f[3], (f[0], f[1], f[2], 1)) for f in FUEL[:8]])
        eq, dh, base = r
        reac, prod = eq.split(' -> ')
        exo = dh < 0
        Hr, Hp = (100, 100 + dh * 0.0) if False else (0, dh)
        top, bot = (reac, prod) if exo else (prod, reac)
        lv = [(reac, 0 if exo else -abs(dh), 60, 260), (prod, -abs(dh) if exo else 0, 120, 320)]
        g = svg.levels([(reac, 0, 50, 230), (prod, dh, 140, 330)], [(0, 1, 300 if exo else 90, f'ΔH={num(dh, 1)} kJ')])
        lvl = ['하', '중', '중', '상'][i % 4]
        fm, nm, M, coef = base
        mol2 = rng.choice([0.5, 2, 0.25, 3]);
        S = [('이 반응은 ' + ('발열' if exo else '흡열') + ' 반응이다.', True, '생성물의 엔탈피가 반응물보다 ' + ('낮다' if exo else '높다') + '.'),
             ('이 반응은 ' + ('흡열' if exo else '발열') + ' 반응이다.', False, '생성물의 엔탈피가 반응물보다 ' + ('낮으므로 발열' if exo else '높으므로 흡열') + ' 반응이다.'),
             ('반응이 일어날 때 주변의 온도가 ' + ('높아진다.' if exo else '낮아진다.'), True, ('발열' if exo else '흡열') + ' 반응이다.'),
             ('반응이 일어날 때 주변의 온도가 ' + ('낮아진다.' if exo else '높아진다.'), False, ('발열 반응이므로 높아진다' if exo else '흡열 반응이므로 낮아진다') + '.'),
             ('생성물이 반응물보다 에너지 면에서 안정하다.', exo, '에너지가 낮은 쪽이 안정하다. ' + ('생성물이 더 낮다.' if exo else '반응물이 더 낮다.')),
             (f'역반응의 반응 엔탈피는 ${m(-dh, 1)}$ kJ이다.', True, '역반응은 크기가 같고 부호가 반대이다.'),
             (f'역반응의 반응 엔탈피는 ${m(dh, 1)}$ kJ이다.', False, f'역반응은 부호가 반대이므로 ${m(-dh, 1)}$ kJ이다.'),
             (f'{fm} {num(mol2 * coef, 2)} 몰이 반응하면 {num(abs(dh) * mol2, 1)} kJ의 열을 ' + ('방출' if exo else '흡수') + '한다.', True,
              f'{fm} {coef} 몰당 {num(abs(dh), 1)} kJ이므로 {num(mol2 * coef, 2)} 몰이면 {num(abs(dh) * mol2, 1)} kJ이다.'),
             (f'{fm} {num(mol2 * coef, 2)} 몰이 반응하면 {num(abs(dh), 1)} kJ의 열을 ' + ('방출' if exo else '흡수') + '한다.', False,
              f'반응 엔탈피는 양에 비례하므로 {num(abs(dh) * mol2, 1)} kJ이다.'),
             ('반응물의 엔탈피 합은 ' + ('생성물보다 크다.' if exo else '생성물보다 작다.'), True, '그림에서 확인할 수 있다.'),
             (f'{fm} 1 몰의 엔탈피는 ${m(dh / coef, 1)}$ kJ이다.', False, '$\\Delta H$는 엔탈피의 차이일 뿐 각 물질의 엔탈피 값은 알 수 없다.')]
        if lvl == '하':
            o = one_of(rng, S, True)
            if not o: continue
            body = [p('그림은 25 ℃, 1 기압에서 어떤 반응의 엔탈피 변화를 나타낸 것이다.'), g, p('이에 대한 설명으로 옳은 것은?')]
            add(typ='A2', lv='하', ono=162, hw='v', body=body, ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v', key='엔탈피 도표: 아래로 = 발열', chk=dict(t='one', want=True))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('그림은 25 ℃, 1 기압에서 어떤 반응의 엔탈피 변화를 나타낸 것이다.'), g, p(Q_BOGI), bogi(b['bogi'])]
            add(typ='A2', lv=lvl, ono=167 if exo else 163, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='엔탈피 도표 해석', chk=dict(t='combo', truth=b['truth']))

# 동소체·상태 비교(166,175,176): 흑연/다이아몬드, 얼음/물/수증기
def eng_allotrope():
    for i in range(400):
        rng = R(5500 + i)
        a = round(rng.choice([-393.5, -394.0, -393.0, -395.0]), 1); d = round(a - rng.choice([1.9, 2.1, 1.5, 2.4, 3.0]), 1)
        diff = round(a - d, 1)
        mol = rng.choice([1, 2, 0.5, 3])
        g = svg.levels([('C(다이아몬드)+O2(g)', -d, 50, 250), ('C(흑연)+O2(g)', -a, 60, 240), ('CO2(g)', 0, 50, 330)],
                       [(0, 2, 300, f'ΔH={num(d, 1)}'), (1, 2, 85, f'ΔH={num(a, 1)}')], ylab='엔탈피', w=360, h=230)
        g = svg.levels([('C(다이아몬드)+O2(g)', -d + 0, 40, 250), ('C(흑연)+O2(g)', -a + 0, 60, 240), ('CO2(g)', 0, 40, 330)],
                       [(0, 2, 300, f'ΔH={num(d, 1)}'), (1, 2, 84, f'ΔH={num(a, 1)}')])
        S = [('흑연이 다이아몬드보다 에너지 면에서 안정하다.', True, f'흑연의 엔탈피가 {num(diff, 1)} kJ 더 낮다.'),
             ('다이아몬드가 흑연보다 에너지 면에서 안정하다.', False, f'다이아몬드의 엔탈피가 {num(diff, 1)} kJ 더 높으므로 덜 안정하다.'),
             ('흑연이 다이아몬드로 변할 때 열을 흡수한다.', True, '엔탈피가 낮은 흑연 → 높은 다이아몬드이므로 흡열이다.'),
             ('흑연이 다이아몬드로 변할 때 열을 방출한다.', False, '엔탈피가 증가하는 변화이므로 흡열이다.'),
             (f'C(s, 흑연) -> C(s, 다이아몬드)의 $\\Delta H={m(diff, 1)}$ kJ이다.', True, f'헤스 법칙: ${m(a, 1)}-({m(d, 1)})={m(diff, 1)}$ kJ'),
             (f'C(s, 흑연) -> C(s, 다이아몬드)의 $\\Delta H={m(-diff, 1)}$ kJ이다.', False, f'${m(a, 1)}-({m(d, 1)})=+{m(diff, 1)}$ kJ이다.'),
             (f'흑연 {num(12 * mol, 1)} g이 완전 연소하면 {num(-a * mol, 1)} kJ의 열이 발생한다.', True, f'흑연 {num(mol, 1)} 몰 × {num(-a, 1)} kJ'),
             (f'다이아몬드 {num(12 * mol, 1)} g이 완전 연소하면 {num(-a * mol, 1)} kJ의 열이 발생한다.', False, f'다이아몬드는 몰당 {num(-d, 1)} kJ이므로 {num(-d * mol, 1)} kJ이다.'),
             ('같은 질량을 연소시키면 다이아몬드가 흑연보다 많은 열을 낸다.', True, '다이아몬드의 엔탈피가 더 높아 생성물(CO2)과의 차이가 더 크다.'),
             ('흑연과 다이아몬드는 모두 분자 결정이다.', False, '둘 다 탄소 원자가 공유 결합으로 연결된 공유 결정이다.')]
        lvl = ['중', '중', '상'][i % 3]
        b = bogi_item(rng, S, 3)
        if not b: continue
        body = [p('그림은 흑연과 다이아몬드가 각각 산소(O2)와 반응하여 이산화 탄소(CO2)를 생성하는 반응의 엔탈피 변화를 나타낸 것이다. (단위: kJ, C의 원자량은 12이다.)'), g, p(Q_BOGI), bogi(b['bogi'])]
        add(typ='A2', lv=lvl, ono=166 if i % 2 else 175, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='엔탈피가 낮을수록 안정', chk=dict(t='combo', truth=b['truth']))

# ---------------------------------------------------------------- A2 사례 분류(164,169,172,176)
EXO = ['메테인의 연소', '철 가루와 산소의 반응(손난로)', '산화 칼슘과 물의 반응(발열 도시락)', '염산과 수산화 나트륨 수용액의 중화 반응', '생물의 호흡',
       '수증기의 액화', '물의 응고', '수산화 나트륨의 용해', '염화 칼슘의 용해', '나무의 연소', '마그네슘과 묽은 염산의 반응', '산소와 수소의 반응']
ENDO = ['질산 암모늄의 용해(냉찜질 주머니)', '물의 기화', '얼음의 융해', '탄산 칼슘의 열분해', '광합성', '드라이아이스의 승화', '물의 전기 분해',
        '탄산수소 나트륨의 열분해', '질소와 산소가 반응하여 일산화 질소가 생성되는 반응', '염화 암모늄의 용해']

def eng_cases():
    for i in range(700):
        rng = R(6000 + i); lvl = ['하', '중', '중', '상'][i % 4]
        if lvl == '하':
            want = rng.random() < 0.5
            good = rng.choice(EXO if want else ENDO); bad = rng.sample(ENDO if want else EXO, 4)
            ch = [good] + bad; rng.shuffle(ch); ans = ch.index(good) + 1
            body = [p(f'다음 중 {"발열" if want else "흡열"} 반응(과정)에 해당하는 것은?')]
            sol = [f'{"①②③④⑤"[k]} {c}: {"발열" if c in EXO else "흡열"}' for k, c in enumerate(ch)]
            add(typ='A2', lv='하', ono=164, hw='s', body=body, ch=ch, ans=ans, sol=sol, chl='v', key='발열: 열 방출·주위 온도↑ / 흡열: 열 흡수·주위 온도↓', chk=dict(t='case', want=want))
        else:
            k = 3 if lvl == '중' else 4
            items = rng.sample(EXO, rng.randint(1, k - 1)); items += rng.sample(ENDO, k - len(items)); rng.shuffle(items)
            nexo = sum(x in EXO for x in items)
            labels = ['(가)', '(나)', '(다)', '(라)'][:k]
            S = [(f'발열 반응은 {nexo}가지이다.', True, f'발열: ' + ', '.join(l for l, x in zip(labels, items) if x in EXO) + '.'),
                 (f'발열 반응은 {nexo + 1 if nexo < k else nexo - 1}가지이다.', False, f'발열 반응은 {nexo}가지이다.'),
                 (f'반응이 일어날 때 주위의 온도가 낮아지는 것은 {k - nexo}가지이다.', True, '흡열 반응에서 주위 온도가 낮아진다.'),
                 (f'$\\Delta H>0$인 것은 {k - nexo + 1 if k - nexo < k else k - nexo - 1}가지이다.', False, f'$\\Delta H>0$(흡열)은 {k - nexo}가지이다.')]
            for l, x in zip(labels, items):
                ex = x in EXO
                S.append((f'{l}에서 생성물의 엔탈피 합이 반응물의 엔탈피 합보다 ' + ('작다.' if rng.random() < 0.5 else '크다.'), None, ''))
                t = S[-1][0].endswith('작다.') == ex
                S[-1] = (S[-1][0], t, f'{l}는 {"발열" if ex else "흡열"}이므로 생성물의 엔탈피가 {"작다" if ex else "크다"}.')
                S.append((f'{l}가 일어날 때 열을 ' + ('방출' if rng.random() < 0.5 else '흡수') + '한다.', None, ''))
                t = ('방출' in S[-1][0]) == ex
                S[-1] = (S[-1][0], t, f'{l}는 {"발열" if ex else "흡열"} 반응(과정)이다.')
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('다음은 우리 주변에서 일어나는 몇 가지 반응(과정)이다.'), box([f'{l} {x}' for l, x in zip(labels, items)]), p(Q_BOGI), bogi(b['bogi'])]
            add(typ='A2', lv=lvl, ono=172 if lvl == '상' else 164, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='생활 속 발열·흡열 반응', chk=dict(t='combo', truth=b['truth']))

def run():
    eng_concept(); eng_write(); eng_heat(); eng_calor(); eng_diagram(); eng_allotrope(); eng_cases()
