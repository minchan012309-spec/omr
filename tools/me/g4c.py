"""Ⅳ-C 반응 속도에 영향을 주는 요인: 농도·압력·표면적 · 온도 · 촉매 · 실험 해석 · 생활과 산업의 촉매"""
from core import *
import svg

CASES = {
 '농도': ['풍구로 공기를 불어 넣으면 숯이 잘 탄다.', '강철솜은 산소가 든 집기병에서 더 빠르게 탄다.', '고압 산소 치료기로 상처 치료를 돕는다.', '진한 염산에서 마그네슘이 더 빨리 녹는다.',
          '산성비가 강해지면 대리석 건축물의 부식이 빨라진다.', '버스에 승객이 많을수록 서로 부딪히는 일이 잦다.'],
 '표면적': ['통나무를 잘게 쪼개면 더 잘 탄다.', '가루약은 알약보다 빨리 흡수된다.', '밀가루 공장에서는 분진 폭발이 일어나기 쉽다.', '석회석 가루가 덩어리보다 묽은 염산과 빨리 반응한다.',
           '폐의 폐포는 포도송이 모양이어서 기체 교환이 잘된다.', '고기를 잘게 썰면 빨리 익는다.'],
 '온도': ['음식을 냉장고에 보관하면 덜 상한다.', '비닐하우스에서 작물이 빨리 자란다.', '압력솥을 쓰면 음식이 빨리 익는다.', '겨울잠을 자는 변온 동물의 심장 박동이 느려진다.',
         '여름철에 음식이 쉽게 상한다.', '체온이 오르면 몸속 화학 반응이 빨라진다.'],
 '촉매': ['자동차의 촉매 변환기가 배기가스를 정화한다.', '과산화 수소에 이산화 망가니즈를 넣으면 산소가 빠르게 발생한다.', '소화 효소가 음식물의 분해를 돕는다.',
         '하버 공정에서 철 촉매를 사용해 암모니아를 합성한다.', '식품에 산화 방지제를 넣어 변질을 늦춘다.', '과산화 수소수에 인산을 넣어 분해를 늦춘다.'],
}

def eng_cases():
    for i in range(900):
        rng = R(26000 + i); k = i % 3
        if k == 0:
            f = rng.choice(list(CASES)); good = rng.choice(CASES[f])
            others = [c for g, L in CASES.items() if g != f for c in L]; bad = rng.sample(others, 4)
            ch = [good] + bad; rng.shuffle(ch)
            body = [p(f'다음 중 반응 속도에 영향을 미치는 요인 중 ‘{f}’와 가장 관계 깊은 현상은?')]
            sol = [f'{"①②③④⑤"[j]} {c} → ' + next(g for g, L in CASES.items() if c in L) for j, c in enumerate(ch)]
            add(typ='F1' if f in ('농도', '표면적') else ('F2' if f == '온도' else 'F3'), lv='하', ono=273 if f == '온도' else 279, hw='s', body=body, ch=ch, ans=ch.index(good) + 1, sol=sol, chl='v',
                key='농도·표면적·온도·촉매와 반응 속도', chk=dict(t='case', want=f))
        else:
            items = rng.sample([(c, g) for g, L in CASES.items() for c in L], 3)
            S = []
            for j, (c, g) in enumerate(items):
                L = f'({"가나다"[j]})'
                other = rng.choice([x for x in CASES if x != g])
                S.append((f'{L}에서 반응 속도가 달라지는 주된 요인은 {g}이다.', True, f'{L} {c} → {g}'))
                S.append((f'{L}에서 반응 속도가 달라지는 주된 요인은 {other}이다.', False, f'{L}의 주된 요인은 {g}이다.'))
            S += [('촉매를 쓰면 반응 엔탈피가 달라진다.', False, '촉매는 $\\Delta H$를 바꾸지 않는다.'),
                  ('표면적을 크게 해도 활성화 에너지는 변하지 않는다.', True, '접촉 면적만 커진다.')]
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('다음은 실생활에서 반응 속도가 달라지는 현상이다.'), box([f'({"가나다"[j]}) {c}' for j, (c, g) in enumerate(items)]), p(Q_BOGI), bogi(b['bogi'])]
            add(typ='F1', lv='중' if k == 1 else '상', ono=285, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='생활 속 반응 속도 요인', chk=dict(t='combo', truth=b['truth']))

def eng_factor_concept():
    S = [('반응물의 농도가 증가하면 단위 부피당 입자 수가 늘어 충돌수가 증가한다.', True, '농도 증가 → 충돌수 증가 → 반응 속도 증가'),
         ('기체 반응에서 부분 압력을 높이면 반응 속도가 빨라진다.', True, '단위 부피당 분자 수가 늘어난다.'),
         ('고체의 표면적이 넓을수록 반응 속도가 빨라진다.', True, '접촉 면적이 커져 충돌수가 증가한다.'),
         ('온도가 높아지면 활성화 에너지 이상의 에너지를 가진 분자 수가 증가한다.', True, '분포 곡선이 오른쪽으로 퍼진다.'),
         ('온도가 높아지면 반응 속도 상수 $k$는 작아진다.', False, '온도가 높아지면 $k$는 커진다.'),
         ('온도가 높아지면 정반응 속도와 역반응 속도가 모두 빨라진다.', True, '정·역반응의 $k$가 모두 커진다.'),
         ('정촉매는 활성화 에너지를 낮추어 반응 속도를 빠르게 한다.', True, '새로운 반응 경로를 제공한다.'),
         ('부촉매는 활성화 에너지를 높인다.', True, '반응 속도를 느리게 한다.'),
         ('촉매는 반응 엔탈피를 변화시킨다.', False, '반응물과 생성물의 에너지는 그대로이다.'),
         ('촉매는 정반응의 속도만 빠르게 하고 역반응의 속도에는 영향을 주지 않는다.', False, '정반응과 역반응의 활성화 에너지를 모두 바꾼다.'),
         ('촉매는 반응 전후에 질량이 변하지 않는다.', True, '자신은 소모되지 않는다.'),
         ('촉매를 사용하면 생성물의 최종 양이 늘어난다.', False, '반응 속도만 바뀌고 생성물의 양은 그대로이다.'),
         ('표면적과 촉매는 최종 생성물의 양을 바꾸지 못한다.', True, '반응 속도만 변화시킨다.'),
         ('효소는 단백질로 이루어져 있어 온도와 pH의 영향을 받는다.', True, '최적 온도·pH에서 활성이 가장 크다.'),
         ('효소는 기질 특이성이 있어 특정 기질과만 반응한다.', True, '활성 부위에 맞는 기질과 결합한다.'),
         ('효소는 온도가 높을수록 항상 활성이 커진다.', False, '너무 높으면 단백질이 변성되어 활성을 잃는다.'),
         ('자동차의 촉매 변환기에는 백금, 팔라듐, 로듐 같은 금속이 쓰인다.', True, '표면 촉매(불균일 촉매)이다.'),
         ('광촉매인 이산화 타이타늄은 빛을 받으면 유기물을 분해할 수 있다.', True, '빛 에너지를 받아 촉매 작용을 한다.'),
         ('유기 촉매는 금속을 포함한 고체 상태의 촉매이다.', False, '유기 촉매는 유기물 형태의 촉매이다(예: 프롤린).'),
         ('금속 표면에 흡착된 수소 분자는 H−H 결합이 약해진다.', True, '금속−수소 결합이 생기며 반응이 쉬워진다.')]
    for i in range(1100):
        rng = R(27000 + i); k = i % 4
        typ = 'F3' if k < 2 else ('F5' if k == 2 else 'F1')
        if k == 0:
            o = one_of(rng, S, rng.random() < 0.5)
            if not o: continue
            want = dict((x[0], x[1]) for x in S)[o['ch'][o['ans'] - 1]]
            add(typ='F3', lv='하', ono=275, hw='s', body=[p('반응 속도에 영향을 주는 요인에 대한 설명으로 ' + ('옳은' if want else '옳지 <u>않은</u>') + ' 것은?')], ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v',
                key='반응 속도의 요인', chk=dict(t='one', want=want))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            add(typ=typ, lv='중' if k != 3 else '상', ono={1: 288, 2: 292, 3: 286}[k], hw='s', body=[p('반응 속도에 영향을 주는 요인에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])],
                ch=b['ch'], ans=b['ans'], sol=b['sol'], key='농도·온도·촉매의 영향', chk=dict(t='combo', truth=b['truth']))

def eng_temp_dist():
    """온도·촉매와 분포 곡선(272, 276, 290, 295, 299)."""
    for i in range(700):
        rng = R(28000 + i); k = i % 3
        hiT = rng.choice(['T1', 'T2'])
        curves = [('T1', 0.22 if hiT == 'T2' else 0.34, False), ('T2', 0.34 if hiT == 'T2' else 0.22, True)]
        g = svg.dist(curves, [(0.6, 'Ea')])
        lo = 'T2' if hiT == 'T1' else 'T1'
        S = [(f'온도는 ${hiT[0]}_{hiT[1]}$가 ${lo[0]}_{lo[1]}$보다 높다.', True, '봉우리가 낮고 오른쪽으로 퍼진 쪽이 고온이다.'),
             (f'온도는 ${lo[0]}_{lo[1]}$가 ${hiT[0]}_{hiT[1]}$보다 높다.', False, f'${hiT[0]}_{hiT[1]}$가 고온이다.'),
             (f'분자의 평균 운동 에너지는 ${hiT[0]}_{hiT[1]}$에서가 더 크다.', True, '고온일수록 크다.'),
             (f'반응할 수 있는 분자 수는 ${lo[0]}_{lo[1]}$에서가 더 많다.', False, f'$E_a$ 오른쪽 넓이는 ${hiT[0]}_{hiT[1]}$에서 더 크다.'),
             (f'반응 속도 상수는 ${hiT[0]}_{hiT[1]}$에서가 더 크다.', True, '고온에서 $k$가 크다.'),
             ('두 온도에서 활성화 에너지는 같다.', True, '온도는 활성화 에너지를 바꾸지 않는다.'),
             ('두 곡선 아래의 전체 넓이는 고온에서 더 크다.', False, '전체 분자 수는 같으므로 넓이도 같다.'),
             (f'${lo[0]}_{lo[1]}$에서 정촉매를 넣으면 곡선이 ${hiT[0]}_{hiT[1]}$의 곡선처럼 바뀐다.', False, '촉매는 곡선이 아니라 $E_a$를 바꾼다.')]
        if k == 0:
            o = one_of(rng, S, True)
            if not o: continue
            add(typ='F2', lv='하', ono=272, hw='v', body=[p('그림은 일정량의 기체 분자의 두 온도에서의 운동 에너지 분포를 나타낸 것이다.'), g, p('이에 대한 설명으로 옳은 것은?')],
                ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v', key='분포 곡선과 온도', chk=dict(t='one', want=True))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            add(typ='F2', lv='중' if k == 1 else '상', ono=295, hw='v', body=[p('그림은 일정량의 기체 분자의 두 온도에서의 운동 에너지 분포 곡선이고, $E_a$는 반응의 활성화 에너지이다.'), g, p(Q_BOGI), bogi(b['bogi'])],
                ch=b['ch'], ans=b['ans'], sol=b['sol'], key='온도와 반응 속도', chk=dict(t='combo', truth=b['truth']))
    # 촉매 에너지 도표 수치(290)
    for i in range(600):
        rng = R(28800 + i)
        Ea = rng.choice([60, 80, 100, 120, 150]); Ec = Ea - rng.choice([20, 30, 40, 50]); dH = rng.choice([-40, -60, -80, 30, 20, -20, 50])
        if Ec <= max(dH, 0) + 5: continue
        ask = rng.choice(['diff', 'revc', 'rev'])
        g = svg.profile(0, dH, Ea, second=Ec, marks=[('Ea', 'E1'), ('dH', 'ΔH')])
        v = {'diff': Ea - Ec, 'revc': Ec - dH, 'rev': Ea - dH}[ask]
        q = {'diff': '촉매를 사용했을 때 정반응의 활성화 에너지가 감소한 양', 'revc': '촉매를 사용했을 때 역반응의 활성화 에너지', 'rev': '촉매를 사용하지 않았을 때 역반응의 활성화 에너지'}[ask]
        body = [p(f'그림은 어떤 반응의 진행에 따른 에너지 변화를 나타낸 것이다. 실선은 촉매가 없을 때(정반응 활성화 에너지 {Ea} kJ), 점선은 촉매가 있을 때(정반응 활성화 에너지 {Ec} kJ)이고, $\\Delta H={m(dH)}$ kJ이다.'), g,
                p(f'{q}(kJ)는?')]
        sol = [f'촉매가 없을 때 $E_a={Ea}$ kJ, 있을 때 $E_a={Ec}$ kJ, $\\Delta H={m(dH)}$ kJ(촉매와 관계없이 같다)',
               {'diff': f'감소량 $={Ea}-{Ec}={Ea - Ec}$ kJ', 'revc': f'$E_a\'=E_a-\\Delta H={Ec}-({m(dH)})={Ec - dH}$ kJ', 'rev': f'$E_a\'={Ea}-({m(dH)})={Ea - dH}$ kJ'}[ask]]
        cands = [Ea - Ec, Ec - dH, Ea - dH, Ec + dH, Ea + dH, abs(dH), Ec, Ea]
        ch, ans = pick_numeric(rng, v, [c for c in cands if c > 0], lambda x: num(x) + ' kJ')
        if not ch: continue
        add(typ='F3', lv='중' if ask == 'diff' else '상', ono=290, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='촉매는 $E_a$만 바꾸고 $\\Delta H$는 그대로', chk=dict(t='num', v=v))

def eng_exp():
    """실험 조건 표 해석(281, 291, 298, 299)."""
    for i in range(800):
        rng = R(29000 + i); k = i % 2
        if k == 0:
            base = rng.choice([0.1, 0.2]); T = rng.choice([10, 20, 25, 30])
            rows = [(base, base, T, '사용 안 함'), (base * 2, base, T, '사용 안 함'), (base, base, T + 10, '사용 안 함'), (base, base, T, '사용함'), (base * 2, base * 2, T + 10, '사용함')]
            rng.shuffle(rows)
            fastest = max(range(5), key=lambda j: (rows[j][0] * rows[j][1], rows[j][2], rows[j][3] == '사용함'))
            pairT = [(a, b) for a in range(5) for b in range(a + 1, 5) if rows[a][:2] == rows[b][:2] and rows[a][3] == rows[b][3] and rows[a][2] != rows[b][2]]
            pairC = [(a, b) for a in range(5) for b in range(a + 1, 5) if rows[a][:3] == rows[b][:3] and rows[a][3] != rows[b][3]]
            pairN = [(a, b) for a in range(5) for b in range(a + 1, 5) if rows[a][2:] == rows[b][2:] and rows[a][:2] != rows[b][:2]]
            S = [(f'반응 속도가 가장 빠를 것으로 예상되는 것은 실험 {fastest + 1}이다.', True, '농도가 크고 온도가 높으며 정촉매를 사용했다.')]
            S.append((f'반응 속도가 가장 빠를 것으로 예상되는 것은 실험 {(fastest + 1) % 5 + 1}이다.', False, f'실험 {fastest + 1}이 가장 빠르다.'))
            for a, b in pairT[:1]: S.append((f'실험 {a + 1}과 {b + 1}을 비교하면 온도의 영향을 알 수 있다.', True, '온도만 다르다.'))
            for a, b in pairC[:1]:
                S.append((f'실험 {a + 1}과 {b + 1}을 비교하면 촉매의 영향을 알 수 있다.', True, '촉매 사용 여부만 다르다.'))
                ca = a if rows[a][3] == '사용함' else b; cb = b if ca == a else a
                S.append((f'활성화 에너지는 실험 {ca + 1}에서가 실험 {cb + 1}에서보다 크다.', False, '정촉매를 쓴 쪽의 활성화 에너지가 더 작다.'))
            for a, b in pairN[:1]: S.append((f'실험 {a + 1}과 {b + 1}을 비교하면 농도의 영향을 알 수 있다.', True, '농도만 다르다.'))
            S.append(('정촉매를 사용한 실험에서는 반응 엔탈피가 작아진다.', False, '촉매는 $\\Delta H$를 바꾸지 않는다.'))
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('A + B → C 반응에서 반응 속도에 영향을 미치는 요인을 알아보기 위해 표와 같은 조건으로 실험하였다.'),
                    table([['실험', 'A의 농도(M)', 'B의 농도(M)', '온도(℃)', '정촉매']] + [[str(j + 1), num(r[0]), num(r[1]), str(r[2]), r[3]] for j, r in enumerate(rows)]), p(Q_BOGI), bogi(b['bogi'])]
            add(typ='F4', lv='중', ono=291, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='변인 통제: 한 가지 조건만 다른 실험끼리 비교', chk=dict(t='combo', truth=b['truth']))
        else:
            # 298형: 초기 속도 비교
            r1 = rng.choice([2, 3, 4, 6]); r2 = rng.choice([1, 2]); r3 = rng.choice([1, 2, 3, 8])
            if r1 == r2 or r3 == r1: continue
            S = [(f'반응 속도 상수는 실험 Ⅰ에서가 Ⅲ에서보다 {"크다" if r1 > r3 else "작다"}.', True, f'같은 농도에서 초기 속도가 {r1}$v$와 {r3}$v$이므로 $k$도 같은 비로 다르다.'),
                 (f'반응 속도 상수는 실험 Ⅰ에서가 Ⅲ에서보다 {"작다" if r1 > r3 else "크다"}.', False, f'$k_Ⅰ:k_Ⅲ={r1}:{r3}$'),
                 ('반응 엔탈피는 실험 Ⅰ과 Ⅱ에서 같다.', True, '촉매는 $\\Delta H$를 바꾸지 않는다.'),
                 (f'X는 활성화 에너지를 {"증가" if r2 < r1 else "감소"}시킨다.', True, f'같은 온도에서 X를 넣은 Ⅱ가 {"느리" if r2 < r1 else "빠르"}므로 {"부" if r2 < r1 else "정"}촉매이다.'),
                 (f'X는 활성화 에너지를 {"감소" if r2 < r1 else "증가"}시킨다.', False, f'X는 {"부" if r2 < r1 else "정"}촉매이다.'),
                 (f'온도는 $T_2$가 $T_1$보다 {"높다" if r3 > r1 else "낮다"}.', True, '촉매가 없을 때 속도가 빠른 쪽이 고온이다.')]
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('표는 동일한 강철 용기에 같은 양의 A(g)를 각각 넣고 반응시킨 실험 Ⅰ~Ⅲ에 대한 자료이다.'),
                    table([['실험', '온도', '첨가한 물질', '초기 반응 속도'], ['Ⅰ', '$T_1$', '없음', f'${r1}v$'], ['Ⅱ', '$T_1$', 'X(s)', f'${r2}v$' if r2 > 1 else '$v$'], ['Ⅲ', '$T_2$', '없음', f'${r3}v$' if r3 > 1 else '$v$']]),
                    p(Q_BOGI), bogi(b['bogi'])]
            add(typ='F3', lv='상', ono=298, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='촉매와 온도가 반응 속도에 미치는 영향', chk=dict(t='combo', truth=b['truth']))
    # 농도·표면적 그래프(270, 277, 294)
    for i in range(500):
        rng = R(29800 + i)
        lim = rng.choice(['금속', '산']); change = rng.choice(['농도 2배 산', '가루 금속', '온도 높임', '촉매', '산의 양 2배'])
        same_final = not (lim == '산' and change in ('농도 2배 산', '산의 양 2배'))
        faster = change in ('농도 2배 산', '가루 금속', '온도 높임', '촉매')
        if change == '산의 양 2배': faster = False
        desc = {'농도 2배 산': '같은 부피의 진한(농도 2배) 염산을 사용한다', '가루 금속': '같은 질량의 아연 가루를 사용한다', '온도 높임': '반응 온도를 높인다', '촉매': '정촉매를 넣는다',
                '산의 양 2배': '같은 농도의 염산을 2배의 부피로 사용한다'}[change]
        ch = ['초기 반응 속도: 빨라짐, 최종 기체 양: 같음', '초기 반응 속도: 빨라짐, 최종 기체 양: 증가', '초기 반응 속도: 같음, 최종 기체 양: 증가', '초기 반응 속도: 느려짐, 최종 기체 양: 같음', '초기 반응 속도: 같음, 최종 기체 양: 같음']
        corr = f'초기 반응 속도: {"빨라짐" if faster else "같음"}, 최종 기체 양: {"같음" if same_final else "증가"}'
        if corr not in ch: continue
        body = [p(f'일정량의 아연 조각과 염산을 반응시켜 발생하는 수소 기체의 부피를 측정하였다. 이 실험에서 ' + ('아연이 모두 반응하고 염산은 남는다.' if lim == '금속' else '염산이 모두 반응하고 아연은 남는다.')),
                p(f'다른 조건은 같게 하고 {desc}면, 초기 반응 속도와 최종 수소 기체의 양은 어떻게 되는가?')]
        sol = [('수소의 최종 양은 모두 반응하는 아연의 양으로 정해진다.' if lim == '금속' else '수소의 최종 양은 모두 반응하는 염산(HCl)의 양으로 정해진다.'),
               f'{desc}: ' + ('반응 속도가 빨라진다.' if faster else '농도가 같으므로 반응 속도(초기)는 같다.'),
               '최종 기체 양: ' + ('같다.' if same_final else 'HCl의 양이 늘어 증가한다.')]
        add(typ='F4', lv='중' if change != '산의 양 2배' else '상', ono=277 if lim == '금속' else 270, hw='v', body=body, ch=ch, ans=ch.index(corr) + 1, sol=sol, chl='v',
            key='반응 속도 요인 vs 생성물의 양', chk=dict(t='sym', v=corr))

def eng_kK():
    """정반응·역반응 속도 상수와 평형 상수(297)."""
    for i in range(300):
        rng = R(29500 + i)
        k1a, Ka = rng.choice([(1, 2.5), (2, 4), (1, 4), (3, 1.5), (2, 0.5)]); k1b, Kb = rng.choice([(2.5, 1), (5, 2), (6, 0.5), (4, 2), (8, 0.25)])
        if k1a == k1b or Ka == Kb: continue
        k2a, k2b = round(k1a / Ka, 3), round(k1b / Kb, 3)
        hot = 'T2' if k1b > k1a else 'T1'; Khot = Kb if hot == 'T2' else Ka; Kcold = Ka if hot == 'T2' else Kb
        exo = Khot < Kcold
        S = [('정반응은 ' + ('발열' if exo else '흡열') + ' 반응이다.', True, f'고온({hot})에서 $K$가 ' + ('작으므로 발열' if exo else '크므로 흡열') + ' 반응이다.'),
             ('정반응은 ' + ('흡열' if exo else '발열') + ' 반응이다.', False, '고온에서 $K$의 변화를 보면 ' + ('발열' if exo else '흡열') + ' 반응이다.'),
             (f'$T_1$에서 $k_2$는 {num(k2a, 3)} s^{{-1}}이다.', True, f'$k_2=\\frac{{k_1}}{{K}}=\\frac{{{m(k1a)}}}{{{m(Ka)}}}={m(k2a, 3)}$'),
             (f'$k_2$는 $T_1$에서가 $T_2$에서보다 ' + ('작다.' if k2a < k2b else '크다.'), True, f'${m(k2a, 3)}$와 ${m(k2b, 3)}$을 비교한다.'),
             (f'$T_1$에서 평형 상태일 때 $k_1$은 $k_2$보다 ' + ('크다.' if k1a > k2a else '작다.'), True, f'${m(k1a)}$와 ${m(k2a, 3)}$'),
             (f'$T_2$에서 평형 상태일 때 정반응 속도는 역반응 속도보다 크다.', False, '평형에서는 정반응 속도 = 역반응 속도이다.')]
        b = bogi_item(rng, S, 3)
        if not b: continue
        body = [p('다음은 정반응과 역반응의 반응 차수가 모두 1차인 화학 반응식이고, 표는 온도 $T_1$, $T_2$에서 정반응의 반응 속도 상수($k_1$)와 평형 상수($K$)이다.'),
                box(['A(g) <=> B(g)　(정반응 $k_1$, 역반응 $k_2$)']), table([['온도', '$k_1$(s^{-1})', '$K$'], ['$T_1$', num(k1a), num(Ka)], ['$T_2$', num(k1b), num(Kb)]]),
                p(Q_BOGI + ' (단, 평형에서 $K=\\frac{k_1}{k_2}$이다.)'), bogi(b['bogi'])]
        add(typ='F2', lv='최', ono=297, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='$K=\\frac{k_1}{k_2}$, 온도가 높으면 $k$ 증가', chk=dict(t='combo', truth=b['truth']))

def run():
    eng_cases(); eng_factor_concept(); eng_temp_dist(); eng_exp(); eng_kK()
