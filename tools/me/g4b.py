"""Ⅳ-B 유효 충돌과 활성화 에너지: 충돌 조건 · Ea/ΔH 도표 · 분포 곡선"""
from core import *
import svg

def eng_collision():
    S = [('화학 반응이 일어나려면 반응물 입자가 충돌해야 한다.', True, '충돌이 반응의 첫째 조건이다.'),
         ('충분한 에너지를 가진 입자들이 충돌하면 방향과 관계없이 항상 반응한다.', False, '반응에 알맞은 방향으로 충돌해야 한다.'),
         ('유효 충돌은 반응에 알맞은 방향으로 활성화 에너지 이상의 에너지를 가지고 일어나는 충돌이다.', True, '유효 충돌의 정의이다.'),
         ('활성화 에너지보다 작은 에너지를 가진 입자도 방향만 맞으면 반응할 수 있다.', False, '활성화 에너지 이상의 에너지가 필요하다.'),
         ('활성화 에너지가 작을수록 반응 속도가 빠르다.', True, '반응할 수 있는 입자가 많아진다.'),
         ('활성화 에너지가 클수록 반응 속도가 빠르다.', False, '활성화 에너지가 클수록 느리다.'),
         ('활성화 에너지는 반응이 일어나는 데 필요한 최소한의 에너지이다.', True, '에너지 장벽의 높이이다.'),
         ('활성화 에너지가 클수록 반응 엔탈피도 크다.', False, '활성화 에너지와 반응 엔탈피는 관계가 없다.'),
         ('활성화 상태는 반응물의 결합이 일부 끊어지고 새로운 결합이 일부 생긴 불안정한 상태이다.', True, '에너지가 가장 높은 상태이다.'),
         ('활성화물은 에너지가 가장 높으므로 가장 안정한 상태이다.', False, '에너지가 높을수록 불안정하다.'),
         ('온도를 높이면 유효 충돌 횟수가 증가한다.', True, '활성화 에너지 이상의 에너지를 가진 입자가 많아진다.'),
         ('반응물의 농도를 크게 하면 활성화 에너지가 작아진다.', False, '농도는 활성화 에너지를 바꾸지 않는다.'),
         ('발열 반응은 정반응의 활성화 에너지가 역반응의 활성화 에너지보다 작다.', True, '$E_a\'=E_a+|\\Delta H|$'),
         ('흡열 반응은 정반응의 활성화 에너지가 역반응의 활성화 에너지보다 작다.', False, '흡열 반응은 정반응의 활성화 에너지가 더 크다.'),
         ('정반응과 역반응의 활성화 에너지 차이는 반응 엔탈피의 크기와 같다.', True, '$\\Delta H=E_a-E_a\'$'),
         ('HI 분자 두 개가 H 원자끼리, I 원자끼리 만나는 방향으로 충분한 에너지로 충돌하면 H2와 I2가 생길 수 있다.', True, '알맞은 방향 + 충분한 에너지 = 유효 충돌'),
         ('A + BC → AC + B 반응에서 A는 BC의 B 쪽으로 충돌해야 AC가 생긴다.', False, 'A−C 결합이 생겨야 하므로 C 쪽으로 충돌해야 한다.')]
    for i in range(700):
        rng = R(23000 + i); k = i % 3
        if k == 0:
            o = one_of(rng, S, rng.random() < 0.5)
            if not o: continue
            want = dict((x[0], x[1]) for x in S)[o['ch'][o['ans'] - 1]]
            add(typ='E1', lv='하', ono=255, hw='s', body=[p('유효 충돌과 활성화 에너지에 대한 설명으로 ' + ('옳은' if want else '옳지 <u>않은</u>') + ' 것은?')], ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v',
                key='유효 충돌 = 알맞은 방향 + $E_a$ 이상의 에너지', chk=dict(t='one', want=want))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('화학 반응이 일어나기 위한 조건에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])]
            if k == 2: body.insert(0, fig('fig/hw/254.png', 60)); body.insert(0, p('그림은 HI 분자가 충돌할 때 충돌 전과 후의 변화를 나타낸 것이다. (다)에서만 반응이 일어났다.'))
            add(typ='E1', lv='중', ono=254 if k == 2 else 248, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='유효 충돌의 조건', chk=dict(t='combo', truth=b['truth']))

def eng_profile():
    for i in range(1200):
        rng = R(24000 + i); lvl = LV[i % 4]
        Ea = rng.choice([40, 60, 80, 100, 120, 150, 183, 185, 200, 210, 250, 90, 75]); dH = rng.choice([-180, -120, -80, -60, -40, -20, 13, 9.7, 20, 40, 60, -226, 30])
        if Ea <= max(dH, 0) + 5: continue
        Ear = round(Ea - dH, 1)
        g = svg.profile(0, dH, Ea, marks=[('Ea', 'Ea'), ('dH', 'ΔH')])
        if lvl == '하':
            ask = rng.choice(['rev', 'dH'])
            if ask == 'rev':
                body = [p(f'어떤 반응에서 정반응의 활성화 에너지는 {num(Ea)} kJ이고, 반응 엔탈피($\\Delta H$)는 ${m(dH, 1)}$ kJ이다. 역반응의 활성화 에너지(kJ)는?')]
                v = Ear; sol = ['$\\Delta H=E_a(\\text{정})-E_a(\\text{역})$', f'$E_a(\\text{{역}})=E_a(\\text{{정}})-\\Delta H={m(Ea)}-({m(dH, 1)})={m(Ear, 1)}$ kJ']
                cands = [round(Ea + dH, 1), round(-dH, 1), round(Ea, 1) * 2, round(abs(dH), 1), round(Ear + 10, 1), round(Ea - abs(dH) / 2, 1)]
            else:
                body = [p(f'어떤 반응에서 정반응의 활성화 에너지는 {num(Ea)} kJ이고, 역반응의 활성화 에너지는 {num(Ear)} kJ이다. 이 반응의 반응 엔탈피($\\Delta H$)는?')]
                v = dH; sol = [f'$\\Delta H=E_a(\\text{{정}})-E_a(\\text{{역}})={m(Ea)}-{m(Ear, 1)}={m(dH, 1)}$ kJ']
                cands = [-dH, round(Ea + Ear, 1), round(Ear - Ea + 5, 1), round(dH * 2, 1), round(dH / 2, 1)]
            ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 1) + ' kJ')
            if not ch: continue
            add(typ='E2', lv='하', ono=252 if ask == 'dH' else 251, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='$\\Delta H=E_a-E_a\'$', chk=dict(t='num', v=v))
        else:
            cat = round(Ea * rng.choice([0.5, 0.6, 0.4, 0.7]), 0) if lvl != '중' else None
            g = svg.profile(0, dH, Ea, marks=[('Ea', 'Ea'), ('dH', 'ΔH')], second=cat + max(dH, 0) * 0 if cat else None)
            S = [('정반응은 ' + ('발열' if dH < 0 else '흡열') + ' 반응이다.', True, f'$\\Delta H={m(dH, 1)}$ kJ'),
                 ('정반응은 ' + ('흡열' if dH < 0 else '발열') + ' 반응이다.', False, f'$\\Delta H={m(dH, 1)}$ kJ이므로 ' + ('발열' if dH < 0 else '흡열') + ' 반응이다.'),
                 (f'역반응의 활성화 에너지는 {num(Ear, 1)} kJ이다.', True, f'$E_a\'=E_a-\\Delta H={m(Ea)}-({m(dH, 1)})={m(Ear, 1)}$'),
                 (f'역반응의 활성화 에너지는 {num(round(Ea + dH, 1), 1)} kJ이다.' if round(Ea + dH, 1) != Ear else f'역반응의 활성화 에너지는 {num(Ea)} kJ이다.', False, f'$E_a\'={m(Ear, 1)}$ kJ이다.'),
                 ('정반응의 활성화 에너지가 역반응보다 ' + ('작다.' if dH < 0 else '크다.'), True, f'{num(Ea)} kJ과 {num(Ear, 1)} kJ을 비교한다.'),
                 ('온도를 높이면 활성화 에너지가 작아진다.', False, '온도는 활성화 에너지를 바꾸지 않는다.'),
                 ('반응물의 농도를 크게 하면 $\\Delta H$가 커진다.', False, '농도는 $\\Delta H$에 영향을 주지 않는다.'),
                 ('활성화물은 반응물보다 불안정하다.', True, '에너지가 가장 높은 상태이다.')]
            if cat:
                S += [(f'점선 경로는 정촉매를 사용한 경우로, 정반응의 활성화 에너지는 {num(cat)} kJ이다.', True, '언덕이 낮아졌으므로 정촉매이다.'),
                      ('촉매를 사용하면 반응 엔탈피가 작아진다.', False, '촉매는 $\\Delta H$를 바꾸지 않는다.'),
                      (f'촉매를 사용하면 역반응의 활성화 에너지는 {num(round(cat - dH, 1), 1)} kJ이 된다.', True, f'${m(cat)}-({m(dH, 1)})={m(round(cat - dH, 1), 1)}$')]
            b = bogi_item(rng, S, 3 if lvl != '최' else 4)
            if not b: continue
            body = [p(f'그림은 어떤 반응의 진행에 따른 에너지 변화를 나타낸 것이다. 정반응의 활성화 에너지($E_a$)는 {num(Ea)} kJ, 반응 엔탈피($\\Delta H$)는 ${m(dH, 1)}$ kJ이다.' +
                      (f' 점선은 같은 온도에서 물질 X를 넣었을 때의 경로이며, 이때 정반응의 활성화 에너지는 {num(cat)} kJ이다.' if cat else '')), g, p(Q_BOGI), bogi(b['bogi'])]
            add(typ='E2', lv=lvl, ono=264 if cat else 261, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='에너지 도표: $E_a$, $E_a\'$, $\\Delta H$', chk=dict(t='combo', truth=b['truth']))
    # 문자 도표(259, 262, 265) 기호형
    for i in range(500):
        rng = R(24800 + i)
        exo = rng.random() < 0.5
        a, b_ = ('a', 'b')
        ask = rng.choice(['Ea', 'Ear', 'dH'])
        if exo:
            g = svg.profile(0, -60, 80, marks=[('Ea', 'a'), ('Ea2', 'b')])
            corr = {'Ea': '$a$', 'Ear': '$b$', 'dH': '$a-b$'}[ask]
        else:
            g = svg.profile(0, 50, 110, marks=[('Ea', 'a'), ('Ea2', 'b')])
            corr = {'Ea': '$a$', 'Ear': '$b$', 'dH': '$a-b$'}[ask]
        ch = ['$a$', '$b$', '$a-b$', '$b-a$', '$a+b$']
        q = {'Ea': '정반응의 활성화 에너지', 'Ear': '역반응의 활성화 에너지', 'dH': '정반응의 반응 엔탈피($\\Delta H$)'}[ask]
        body = [p('그림은 어떤 반응의 진행에 따른 에너지 변화를 나타낸 것이다.'), g, p(f'{q}로 옳은 것은?')]
        sol = ['$a$: 반응물에서 활성화 상태까지 = 정반응의 활성화 에너지', '$b$: 생성물에서 활성화 상태까지 = 역반응의 활성화 에너지',
               '$\\Delta H=E_a(\\text{정})-E_a(\\text{역})=a-b$' + (' (발열이므로 음수)' if exo else ' (흡열이므로 양수)'), f'∴ {corr}']
        add(typ='E2', lv='중', ono=259, hw='v', body=body, ch=ch, ans=ch.index(corr) + 1, sol=sol, key='에너지 도표 읽기', chk=dict(t='sym', v=corr))

def eng_dist():
    S = [('곡선 아래의 전체 넓이는 전체 분자 수를 나타낸다.', True, '분포 곡선 아래 넓이 = 분자 수'),
         ('활성화 에너지보다 오른쪽 영역의 분자들이 반응할 수 있다.', True, '$E_a$ 이상의 에너지를 가진 분자이다.'),
         ('활성화 에너지보다 왼쪽 영역의 분자도 유효 충돌을 할 수 있다.', False, '$E_a$보다 작은 에너지로는 반응하지 않는다.'),
         ('활성화 에너지가 작아지면 반응할 수 있는 분자 수가 증가한다.', True, '$E_a$ 오른쪽 넓이가 커진다.'),
         ('활성화 에너지가 커지면 반응 속도가 빨라진다.', False, '반응할 수 있는 분자가 줄어 느려진다.'),
         ('온도가 높아지면 곡선이 오른쪽으로 퍼지고 봉우리가 낮아진다.', True, '평균 운동 에너지가 커진다.'),
         ('온도가 높아져도 전체 분자 수는 변하지 않는다.', True, '곡선 아래 전체 넓이는 같다.'),
         ('온도가 높아지면 활성화 에너지가 작아진다.', False, '온도는 활성화 에너지를 바꾸지 않는다.'),
         ('정촉매를 넣으면 분포 곡선 자체가 오른쪽으로 이동한다.', False, '촉매는 분포 곡선이 아니라 활성화 에너지를 바꾼다.'),
         ('부촉매를 넣으면 활성화 에너지가 커져 반응할 수 있는 분자 수가 줄어든다.', True, '$E_a$가 오른쪽으로 이동한다.')]
    for i in range(700):
        rng = R(25000 + i); k = i % 3
        lines = [(0.55, 'Ea')] if k else [(0.42, "Ea'"), (0.55, 'Ea'), (0.7, 'Ea"')]
        g = svg.dist([('T', 0.28, False)], lines)
        if k == 0:
            want = rng.choice(['fast', 'slow'])
            corr = "$E_a'$" if want == 'fast' else "$E_a''$"
            ch = ["$E_a'$", '$E_a$', "$E_a''$", '모두 같다', '알 수 없다']
            body = [p('그림은 일정한 온도에서 어떤 기체 분자들의 운동 에너지 분포 곡선과 세 가지 활성화 에너지를 나타낸 것이다.'), g,
                    p('활성화 에너지가 다음 중 무엇일 때 반응 속도가 가장 ' + ('빠른가?' if want == 'fast' else '느린가?'))]
            sol = ['활성화 에너지보다 큰 에너지를 가진 분자(오른쪽 넓이)가 많을수록 반응 속도가 빠르다.', f"$E_a'<E_a<E_a''$이므로 가장 {'빠른 것은' if want == 'fast' else '느린 것은'} {corr}이다."]
            add(typ='E3', lv='하', ono=258, hw='v', body=body, ch=ch, ans=ch.index(corr) + 1, sol=sol, key='$E_a$가 작을수록 빠르다', chk=dict(t='sym', v=corr))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('그림은 일정한 온도에서 어떤 기체 분자들의 운동 에너지 분포 곡선을 나타낸 것이다. $E_a$는 반응의 활성화 에너지이다.'), g,
                    p('운동 에너지 분포 곡선에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])]
            add(typ='E3', lv='중' if k == 1 else '상', ono=263 if k == 1 else 265, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='분포 곡선과 활성화 에너지', chk=dict(t='combo', truth=b['truth']))

def run():
    eng_collision(); eng_profile(); eng_dist()
