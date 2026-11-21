"""Ⅲ-C 화학 변화의 자발성: 자발/비자발 · 엔트로피 증감 · ΔS계/주위/전체 · ΔH·ΔS와 자발성"""
from core import *

# 반응·변화: (식 또는 설명, ΔH 부호(+1/-1/0=모름), ΔS 부호, 설명)
CHG = [
 ('H2O(s) -> H2O(l)', 1, 1, '융해: 고체 → 액체'), ('H2O(l) -> H2O(g)', 1, 1, '기화: 액체 → 기체'), ('CO2(s) -> CO2(g)', 1, 1, '승화: 고체 → 기체'),
 ('I2(s) -> I2(g)', 1, 1, '승화: 고체 → 기체'), ('H2O(g) -> H2O(l)', -1, -1, '액화: 기체 → 액체'), ('H2O(l) -> H2O(s)', -1, -1, '응고: 액체 → 고체'),
 ('CaCO3(s) -> CaO(s) + CO2(g)', 1, 1, '기체 0 → 1 몰'), ('2HgO(s) -> 2Hg(l) + O2(g)', 1, 1, '기체 0 → 1 몰'),
 ('N2(g) + 3H2(g) -> 2NH3(g)', -1, -1, '기체 4 → 2 몰'), ('2SO2(g) + O2(g) -> 2SO3(g)', -1, -1, '기체 3 → 2 몰'),
 ('3O2(g) -> 2O3(g)', 1, -1, '기체 3 → 2 몰'), ('2H2(g) + O2(g) -> 2H2O(l)', -1, -1, '기체 3 몰 → 액체'),
 ('CH4(g) + 2O2(g) -> CO2(g) + 2H2O(l)', -1, -1, '기체 3 → 1 몰'), ('2H2O2(l) -> 2H2O(l) + O2(g)', -1, 1, '기체 0 → 1 몰'),
 ('C3H8(g) + 5O2(g) -> 3CO2(g) + 4H2O(g)', -1, 1, '기체 6 → 7 몰'), ('C6H12O6(s) + 6O2(g) -> 6CO2(g) + 6H2O(g)', -1, 1, '기체 6 → 12 몰'),
 ('2Cl(g) -> Cl2(g)', -1, -1, '기체 2 → 1 몰'), ('N2O4(g) -> 2NO2(g)', 1, 1, '기체 1 → 2 몰'), ('2NO2(g) -> N2O4(g)', -1, -1, '기체 2 → 1 몰'),
 ('CO2(g) -> C(s) + O2(g)', 1, -1, '기체 1 → 1 몰이지만 고체가 생김'), ('2N2O(g) -> 2N2(g) + O2(g)', -1, 1, '기체 2 → 3 몰'),
 ('N2H4(l) + O2(g) -> N2(g) + 2H2O(g)', -1, 1, '기체 1 → 3 몰'), ('4Fe(s) + 3O2(g) -> 2Fe2O3(s)', -1, -1, '기체 3 몰 → 고체'),
 ('NH4NO3(s) -> NH4^{+}(aq) + NO3^{-}(aq)', 1, 1, '고체가 녹아 이온이 퍼짐'), ('C4H8(g) + 6O2(g) -> 4CO2(g) + 4H2O(g)', -1, 1, '기체 7 → 8 몰'),
 ('2NH3(g) -> N2(g) + 3H2(g)', 1, 1, '기체 2 → 4 몰'), ('2KClO3(s) -> 2KCl(s) + 3O2(g)', -1, 1, '기체 0 → 3 몰'),
]
PHEN_UP = ['물에 떨어뜨린 잉크가 퍼져 나간다.', '향수병을 열면 향기가 방 안에 퍼진다.', '설탕이 물에 녹는다.', '드라이아이스의 크기가 점점 작아진다.', '젖은 빨래가 마른다.',
           '얼음이 녹는다.', '서로 다른 두 기체가 섞인다.', '물을 가열하여 온도가 높아진다.', '탄산음료의 마개를 열면 기체가 빠져나온다.', '나프탈렌이 승화한다.']
PHEN_DN = ['수증기가 응결하여 이슬이 맺힌다.', '물이 얼어 얼음이 된다.', '물에 퍼진 잉크가 다시 한 방울로 모인다.', '기체가 압축되어 부피가 줄어든다.', '수용액에서 앙금이 생긴다.',
           '물이 식어 온도가 낮아진다.']
SPON = ['뜨거운 물이 공기 중에서 식는다.', '마그네슘 리본을 묽은 염산에 넣으면 수소 기체가 발생한다.', '철못이 공기 중에서 녹슨다.', '잉크가 물 전체로 퍼진다.', '얼음이 상온에서 녹는다.',
        '공에서 바람이 빠진다.', '높은 곳의 물이 낮은 곳으로 흐른다.']
NONSPON = ['25 ℃에서 물이 수소와 산소로 저절로 분해된다.', '물에 퍼진 잉크가 저절로 모인다.', '찬물이 저절로 뜨거워진다.', '녹슨 철이 저절로 철과 산소로 돌아간다.', '물이 낮은 곳에서 높은 곳으로 저절로 흐른다.',
           '상온에서 물이 저절로 언다.']

def sgn(x): return '(+)' if x > 0 else '(−)'

def eng_spon():
    for i in range(500):
        rng = R(13000 + i); k = i % 3
        if k == 0:
            want = rng.random() < 0.5
            good = rng.choice(SPON if want else NONSPON); bad = rng.sample(NONSPON if want else SPON, 4)
            ch = [good] + bad; rng.shuffle(ch); ans = ch.index(good) + 1
            body = [p(f'다음 중 {"자발적" if want else "비자발적"}인 변화(과정)는?')]
            sol = [f'{"①②③④⑤"[j]} {c} → {"자발적" if c in SPON else "비자발적"}' for j, c in enumerate(ch)]
            add(typ='C1', lv='하', ono=197, hw='s', body=body, ch=ch, ans=ans, sol=sol, chl='v', key='자발적 변화: 외부 도움 없이 스스로 일어나는 변화', chk=dict(t='case', want=want))
        else:
            S = [(x, True, '외부의 도움 없이 스스로 일어나는 자발적 변화이다.') for x in SPON] + [(x, False, '스스로 일어나지 않는 비자발적 변화이다.') for x in NONSPON]
            b = bogi_item(rng, S, 3)
            if not b: continue
            b['sol'] = [s.replace('옳다.', '→ 자발적').replace('옳지 않다.', '→ 비자발적') for s in b['sol'][:-1]] + [b['sol'][-1].replace('옳은 것은', '자발적인 것은')]
            body = [p('다음 중 자발적으로 일어나는 변화만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])]
            add(typ='C1', lv='중', ono=197, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='자발적 변화와 비자발적 변화', chk=dict(t='combo', truth=b['truth']))

def eng_entropy():
    for i in range(1300):
        rng = R(14000 + i); k = i % 5
        if k == 0:  # 엔트로피 증가하는 것(현상)
            want = rng.random() < 0.6
            good = rng.choice(PHEN_UP if want else PHEN_DN); bad = rng.sample(PHEN_DN if want else PHEN_UP, 4)
            ch = [good] + bad; rng.shuffle(ch); ans = ch.index(good) + 1
            body = [p(f'다음 중 엔트로피가 {"증가" if want else "감소"}하는 변화는?')]
            sol = [f'{"①②③④⑤"[j]} {c} → 엔트로피 {"증가" if c in PHEN_UP else "감소"}' for j, c in enumerate(ch)]
            add(typ='C2', lv='하', ono=203, hw='s', body=body, ch=ch, ans=ans, sol=sol, chl='v', key='무질서해지면 엔트로피 증가', chk=dict(t='case', want=want))
        elif k == 1:  # 반응식 ΔS 부호 표(204)
            rs = rng.sample(CHG, 3)
            signs = [sgn(r[2]) for r in rs]
            opts = {tuple(signs)}
            while len(opts) < 5:
                opts.add(tuple(rng.choice(['(+)', '(−)']) for _ in range(3)))
            opts = sorted(opts, key=lambda t: [x == '(−)' for x in t]); ans = opts.index(tuple(signs)) + 1
            body = [p('다음은 3가지 반응의 화학 반응식이다.'), box([f'({"가나다"[j]}) {r[0]}' for j, r in enumerate(rs)]),
                    p('반응 (가)~(다)가 일어날 때 계의 엔트로피 변화($\\Delta S$)의 부호를 옳게 나타낸 것은?'),
                    table([['', '(가)', '(나)', '(다)']] + [[('①②③④⑤')[j]] + list(o) for j, o in enumerate(opts)])]
            sol = [f'({"가나다"[j]}) {r[3]} → $\\Delta S$ {sgn(r[2])}' for j, r in enumerate(rs)]
            add(typ='C2', lv='중', ono=204, hw='v', body=body, ch=['①', '②', '③', '④', '⑤'], ans=ans, sol=sol, chl='', key='기체 분자 수가 늘면 엔트로피 증가', chk=dict(t='signs', v=signs))
        else:
            r1, r2, r3 = rng.sample(CHG, 3)
            S = [('엔트로피는 무질서도의 척도이며 기호 $S$로 나타낸다.', True, '엔트로피의 정의이다.'),
                 ('엔트로피의 기호는 $H$이다.', False, '$H$는 엔탈피, 엔트로피는 $S$이다.'),
                 ('같은 물질이면 고체 < 액체 < 기체 순으로 엔트로피가 크다.', True, '입자의 운동이 자유로울수록 무질서도가 크다.'),
                 ('같은 물질이면 상태와 관계없이 엔트로피가 같다.', False, '상태에 따라 엔트로피가 다르다.'),
                 ('같은 상태의 물질은 온도가 높을수록 엔트로피가 크다.', True, '분자 운동이 활발해져 무질서도가 커진다.'),
                 ('$\\Delta S=S_{\\text{최종}}-S_{\\text{초기}}$이다.', True, '엔트로피 변화의 정의이다.'),
                 ('$\\Delta S=S_{\\text{초기}}-S_{\\text{최종}}$이다.', False, '$\\Delta S=S_{\\text{최종}}-S_{\\text{초기}}$이다.'),
                 ('두 기체가 섞이는 과정에서 엔트로피가 증가한다.', True, '혼합되면 배열의 경우의 수가 늘어난다.'),
                 ('기체 분자 4개가 한쪽 용기에 모두 모여 있을 확률은 양쪽에 나뉘어 있을 확률보다 크다.', False, '한쪽에 모두 모이는 배열의 수가 가장 적어 확률이 작다.'),
                 ('대부분의 고체는 물에 녹을 때 엔트로피가 증가한다.', True, '입자가 퍼져 무질서도가 커진다(감소하는 경우도 있다).'),
                 (f'{r1[0]} 반응에서 계의 엔트로피는 ' + ('증가' if r1[2] > 0 else '감소') + '한다.', True, r1[3] + '.'),
                 (f'{r2[0]} 반응에서 계의 엔트로피는 ' + ('감소' if r2[2] > 0 else '증가') + '한다.', False, r2[3] + '이므로 ' + ('증가' if r2[2] > 0 else '감소') + '한다.'),
                 (f'{r3[0]} 반응의 $\\Delta S$는 ' + ('0보다 크다.' if r3[2] > 0 else '0보다 작다.'), True, r3[3] + '.')]
            if k == 2:
                o = one_of(rng, S, rng.random() < 0.5)
                if not o: continue
                want = dict((x[0], x[1]) for x in S)[o['ch'][o['ans'] - 1]]
                body = [p('엔트로피에 대한 설명으로 ' + ('옳은' if want else '옳지 <u>않은</u>') + ' 것은?')]
                add(typ='C2', lv='중', ono=202, hw='s', body=body, ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v', key='엔트로피', chk=dict(t='one', want=want))
            else:
                b = bogi_item(rng, S, 3)
                if not b: continue
                body = [p('엔트로피에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])]
                add(typ='C2', lv='중' if k == 3 else '상', ono=210 if k == 3 else 213, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='엔트로피 증감 판단', chk=dict(t='combo', truth=b['truth']))

def eng_total():
    """ΔS주위 = −ΔH/T, ΔS전체 = ΔS계 + ΔS주위 계산 (개념 노트 4-2)."""
    for i in range(900):
        rng = R(15000 + i)
        T = rng.choice([200, 250, 298, 300, 400, 500, 600, 1000])
        dH = rng.choice([-92.2, -57.2, -196.0, 44.0, 6.0, 181.0, -100.0, 50.0, 120.0, -250.0, 178.0, -40.0])
        dSs = rng.choice([-199, -176, 125, 118, 22, 25, 160, -80, 90, -120, 35, -30])
        dSsur = round(-dH * 1000 / T, 1); tot = round(dSs + dSsur, 1)
        lvl = LV[i % 4]
        if lvl == '하':
            body = [p(f'어떤 반응이 {T} K, 일정한 압력에서 일어날 때 계의 엔탈피 변화($\\Delta H$)는 ${m(dH, 1)}$ kJ이다. 이때 주위의 엔트로피 변화($\\Delta S_{{\\text{{주위}}}}$, J/K)는?')]
            v = dSsur
            sol = ['계가 방출한 열은 주위가 흡수하므로 $\\Delta S_{\\text{주위}}=-\\frac{\\Delta H}{T}$이다.', f'$\\Delta S_{{\\text{{주위}}}}=-\\frac{{{m(dH * 1000, 0)}\\text{{ J}}}}{{{T}\\text{{ K}}}}={m(v, 1)}$ J/K']
            cands = [-v, round(-dH / T, 3), round(dH * T, 0), round(v * 2, 1), round(v / 2, 1), round(-dH * 1000 / 298, 1)]
            ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 3) + ' J/K')
            if not ch: continue
            add(typ='C3', lv='하', ono=208, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='$\\Delta S_{\\text{주위}}=-\\frac{\\Delta H}{T}$', chk=dict(t='num', v=v))
        elif lvl in ('중', '상'):
            body = [p(f'어떤 반응이 {T} K에서 일어날 때 $\\Delta H={m(dH, 1)}$ kJ, $\\Delta S_{{\\text{{계}}}}={m(dSs)}$ J/K이다.'),
                    p('이 반응에서 우주 전체의 엔트로피 변화($\\Delta S_{\\text{전체}}$, J/K)와 자발성을 옳게 짝 지은 것은?')]
            v = tot; spon = tot > 0
            opts = [(v, spon), (v, not spon), (round(dSs - dSsur, 1), round(dSs - dSsur, 1) > 0), (round(-v, 1), -v > 0), (round(dSs + dH, 1), dSs + dH > 0)]
            seen = []; [seen.append(o) for o in opts if o not in seen]
            if len(seen) < 5: continue
            rng.shuffle(seen); ans = seen.index((v, spon)) + 1
            ch = [f'${m(a, 1)}$ J/K, {"자발적" if s else "비자발적"}' for a, s in seen]
            if len(set(ch)) < 5: continue
            sol = [f'$\\Delta S_{{\\text{{주위}}}}=-\\frac{{\\Delta H}}{{T}}=-\\frac{{{m(dH * 1000, 0)}}}{{{T}}}={m(dSsur, 1)}$ J/K',
                   f'$\\Delta S_{{\\text{{전체}}}}=\\Delta S_{{\\text{{계}}}}+\\Delta S_{{\\text{{주위}}}}={m(dSs)}+({m(dSsur, 1)})={m(tot, 1)}$ J/K',
                   ('$\\Delta S_{\\text{전체}}>0$이므로 자발적이다.' if spon else '$\\Delta S_{\\text{전체}}<0$이므로 비자발적이다.')]
            add(typ='C3', lv=lvl, ono=208, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='$\\Delta S_{\\text{전체}}=\\Delta S_{\\text{계}}+\\Delta S_{\\text{주위}}$', chk=dict(t='stot', dH=dH, dS=dSs, T=T, v=tot))
        else:
            # 최: 자발적이 되는 온도 경계
            if (dH > 0) != (dSs > 0): continue
            Tb = dH * 1000 / dSs
            if Tb <= 0 or abs(Tb - round(Tb)) > 1e-6:
                Tb = round(Tb, 1)
            body = [p(f'어떤 반응의 $\\Delta H={m(dH, 1)}$ kJ, $\\Delta S_{{\\text{{계}}}}={m(dSs)}$ J/K이고, 이 값들은 온도에 따라 변하지 않는다고 가정한다.'),
                    p('이 반응이 자발적으로 일어나는 온도 조건으로 옳은 것은?')]
            hi = dH > 0
            correct = f'$T>{m(Tb, 1)}$ K' if hi else f'$T<{m(Tb, 1)}$ K'
            ch = [f'$T>{m(Tb, 1)}$ K', f'$T<{m(Tb, 1)}$ K', '모든 온도에서 자발적', '모든 온도에서 비자발적', f'$T>{m(round(Tb / 1000, 3), 3)}$ K']
            rng.shuffle(ch); ans = ch.index(correct) + 1
            sol = ['자발적 조건: $\\Delta S_{\\text{전체}}=\\Delta S_{\\text{계}}-\\frac{\\Delta H}{T}>0$',
                   f'${m(dSs)}-\\frac{{{m(dH * 1000, 0)}}}{{T}}>0$', ('$\\Delta H>0$, $\\Delta S>0$: 높은 온도에서 자발적' if hi else '$\\Delta H<0$, $\\Delta S<0$: 낮은 온도에서 자발적'),
                   f'∴ {correct}']
            add(typ='C3', lv='최', ono=215, hw='s', body=body, ch=ch, ans=ans, sol=sol, key='경계 온도 $T=\\frac{\\Delta H}{\\Delta S}$', chk=dict(t='tb', v=correct))

def eng_hs():
    """ΔH·ΔS 부호와 자발성(201, 207, 208, 209, 212, 215)."""
    for i in range(1000):
        rng = R(16000 + i); k = i % 4
        if k == 0:
            r = rng.choice(CHG); h, s = r[1], r[2]
            res = '항상 자발적' if h < 0 < s else '항상 비자발적' if h > 0 > s else ('낮은 온도에서 자발적' if h < 0 else '높은 온도에서 자발적')
            opts = ['항상 자발적', '항상 비자발적', '낮은 온도에서 자발적', '높은 온도에서 자발적', '온도와 관계없이 평형 상태']
            body = [p('다음 반응의 자발성에 대한 설명으로 옳은 것은?'), box([f'{r[0]}, $\\Delta H{"<" if h < 0 else ">"}0$'])]
            sol = [f'{r[3]} → $\\Delta S_{{\\text{{계}}}}{">" if s > 0 else "<"}0$', f'$\\Delta H{"<" if h < 0 else ">"}0$ → $\\Delta S_{{\\text{{주위}}}}{">" if h < 0 else "<"}0$', f'∴ {res}']
            add(typ='C4', lv='하', ono=208, hw='v', body=body, ch=opts, ans=opts.index(res) + 1, sol=sol, chl='v', key='$\\Delta H$·$\\Delta S$ 부호 → 자발성', chk=dict(t='hs', h=h, s=s, v=res))
        elif k == 1:
            # 212형 매칭
            pick = []
            for want in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
                c = [x for x in CHG if (x[1], x[2]) == want]
                if c: pick.append(rng.choice(c))
            rng.shuffle(pick); pick = pick[:3]
            labs = ['A', 'B', 'C']; perm = pick[:]; rng.shuffle(perm)
            table_ = [['구분'] + labs, ['$\\Delta H$'] + [sgn(x[1]) for x in perm], ['$\\Delta S$'] + [sgn(x[2]) for x in perm]]
            correct = tuple(labs[perm.index(x)] for x in pick)
            import itertools
            allp = list(itertools.permutations(labs)); rng.shuffle(allp)
            opts = [correct] + [x for x in allp if x != correct][:4]; opts.sort(); ans = opts.index(correct) + 1
            body = [p('다음은 반응 (가)~(다)의 화학 반응식이다.'), box([f'({"가나다"[j]}) {x[0]}' for j, x in enumerate(pick)]),
                    p('표는 반응 A~C의 엔탈피 변화($\\Delta H$)와 엔트로피 변화($\\Delta S$)의 부호를 나타낸 것이다. A~C는 (가)~(다)를 순서 없이 나타낸 것이다.'), table(table_),
                    p('(가)~(다)를 A~C와 옳게 연결한 것은?'), table([['', '(가)', '(나)', '(다)']] + [['①②③④⑤'[j]] + list(o) for j, o in enumerate(opts)])]
            sol = [f'({"가나다"[j]}) {x[3]}: $\\Delta S$ {sgn(x[2])}, $\\Delta H$ {sgn(x[1])} → {labs[perm.index(x)]}' for j, x in enumerate(pick)]
            add(typ='C4', lv='상', ono=212, hw='v', body=body, ch=['①', '②', '③', '④', '⑤'], ans=ans, sol=sol, chl='', key='$\\Delta H$·$\\Delta S$ 부호 판단', chk=dict(t='match', v=correct))
        else:
            rs = rng.sample(CHG, 3)
            S = []
            for j, r in enumerate(rs):
                L = f'({"가나다"[j]})'; h, s = r[1], r[2]
                always = h < 0 < s; never = h > 0 > s
                S += [(f'{L}는 온도와 관계없이 항상 자발적이다.', always, f'{L}: $\\Delta H$ {sgn(h)}, $\\Delta S$ {sgn(s)} → ' + ('항상 자발적' if always else '항상 비자발적' if never else ('낮은' if h < 0 else '높은') + ' 온도에서 자발적') + '.'),
                      (f'{L}에서 계의 엔트로피는 ' + ('증가' if rng.random() < 0.5 else '감소') + '한다.', None, f'{L}: {r[3]}.'),
                      (f'{L}가 일어날 때 주위의 엔트로피는 ' + ('증가' if rng.random() < 0.5 else '감소') + '한다.', None, f'{L}: $\\Delta H$ {sgn(h)} → $\\Delta S_{{\\text{{주위}}}}$ {sgn(-h)}.')]
                S[-2] = (S[-2][0], ('증가' in S[-2][0]) == (s > 0), S[-2][2]); S[-1] = (S[-1][0], ('증가' in S[-1][0]) == (h < 0), S[-1][2])
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('다음은 3가지 반응의 열화학 반응식이다.'), box([f'({"가나다"[j]}) {r[0]}, $\\Delta H{"<" if r[1] < 0 else ">"}0$' for j, r in enumerate(rs)]), p(Q_BOGI), bogi(b['bogi'])]
            add(typ='C4', lv='중' if k == 2 else '최', ono=209 if k == 2 else 215, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='$\\Delta S_{\\text{전체}}$로 자발성 판단', chk=dict(t='combo', truth=b['truth']))
    # 계의 종류·열역학 법칙(개념 노트)
    S = [('열린계는 주위와 물질과 에너지를 모두 교환할 수 있다.', True, '사람의 몸, 자동차 엔진 등이 열린계이다.'),
         ('닫힌계는 주위와 에너지는 교환하지만 물질은 교환하지 않는다.', True, '건전지, 냉찜질용 팩 등이 닫힌계이다.'),
         ('고립계는 주위와 에너지만 교환할 수 있다.', False, '고립계는 물질과 에너지를 모두 교환하지 않는다.'),
         ('우주는 고립계로 볼 수 있다.', True, '우주 밖에는 교환할 주위가 없다.'),
         ('열역학 제1법칙은 에너지 보존 법칙이다.', True, '에너지는 형태만 바뀔 뿐 생기거나 없어지지 않는다.'),
         ('열역학 제2법칙에 따르면 자발적 과정에서 우주의 엔트로피는 증가한다.', True, '엔트로피 증가 법칙이다.'),
         ('계의 엔트로피가 감소하는 반응은 절대로 자발적일 수 없다.', False, '주위의 엔트로피가 더 크게 증가하면 자발적일 수 있다.'),
         ('같은 양의 열이 방출될 때 주위의 온도가 낮을수록 주위의 엔트로피 증가가 크다.', True, '$\\Delta S_{\\text{주위}}=-\\frac{\\Delta H}{T}$에서 $T$가 작을수록 크다.'),
         ('발열 반응이 일어나면 주위의 엔트로피는 감소한다.', False, '열을 받은 주위의 엔트로피는 증가한다.'),
         ('흡열 반응이 일어나면 주위의 엔트로피는 감소한다.', True, '주위가 열을 잃으므로 감소한다.'),
         ('$\\Delta S_{\\text{전체}}<0$인 과정은 자발적이다.', False, '$\\Delta S_{\\text{전체}}>0$이어야 자발적이다.'),
         ('밀폐된 단열 용기는 고립계에 가깝다.', True, '물질도 열도 드나들지 못한다.')]
    for i in range(500):
        rng = R(16800 + i)
        if i % 2:
            o = one_of(rng, S, rng.random() < 0.5)
            if not o: continue
            want = dict((x[0], x[1]) for x in S)[o['ch'][o['ans'] - 1]]
            body = [p('열역학 법칙과 계에 대한 설명으로 ' + ('옳은' if want else '옳지 <u>않은</u>') + ' 것은?')]
            add(typ='C3', lv='하', ono=201, hw='s', body=body, ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v', key='계의 종류와 열역학 법칙', chk=dict(t='one', want=want))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('열역학 법칙과 계에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])]
            add(typ='C3', lv='중', ono=201, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='열역학 제1·2법칙', chk=dict(t='combo', truth=b['truth']))

def run():
    eng_spon(); eng_entropy(); eng_total(); eng_hs()
