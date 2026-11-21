"""Ⅳ-A 반응 속도: 표현·측정 · 평균/순간 속도와 계수비 · 속도식 결정 · 1차 반응 반감기 · 압력 자료"""
from core import *
import svg

UNIT = {0: 'M·s^{-1}', 1: 's^{-1}', 2: 'M^{-1}·s^{-1}', 3: 'M^{-2}·s^{-1}', 4: 'M^{-3}·s^{-1}'}

def eng_concept():
    S = [('반응 속도는 단위 시간 동안 반응물의 농도 감소량 또는 생성물의 농도 증가량으로 나타낸다.', True, '반응 속도의 정의이다.'),
         ('반응 속도의 단위로 mol/(L·s)를 쓸 수 있다.', True, '농도 변화(mol/L)를 시간(s)으로 나눈다.'),
         ('반응 속도의 단위는 mol/L이다.', False, '시간으로 나누어야 하므로 mol/(L·s) 등이다.'),
         ('순간 반응 속도는 농도−시간 그래프에서 그 시각의 접선의 기울기이다.', True, '접선의 기울기(의 절댓값)가 순간 반응 속도이다.'),
         ('평균 반응 속도는 두 시각의 농도를 이은 직선의 기울기이다.', True, '구간의 농도 변화량 ÷ 걸린 시간이다.'),
         ('반응이 진행될수록 반응물의 농도가 줄어 반응 속도는 대체로 느려진다.', True, '반응물의 농도가 감소하기 때문이다.'),
         ('초기 반응 속도는 반응이 진행되는 동안 가장 느리다.', False, '반응물의 농도가 가장 큰 처음이 대체로 가장 빠르다.'),
         ('기체가 발생하는 반응은 발생한 기체의 부피나 감소한 질량을 측정하여 반응 속도를 구할 수 있다.', True, '기체 주사기나 전자저울을 이용한다.'),
         ('앙금이 생기는 반응은 용액이 뿌옇게 되어 표시가 보이지 않을 때까지 걸린 시간으로 빠르기를 비교한다.', True, '싸이오황산 나트륨과 염산의 반응이 예이다.'),
         ('물에 잘 녹는 기체는 수상 치환으로 부피를 측정하는 것이 좋다.', False, '물에 녹으므로 기체 주사기를 쓴다.'),
         ('온도와 부피가 일정할 때 기체의 압력은 몰수에 비례한다.', True, '압력 변화로 반응 속도를 나타낼 수 있다.'),
         ('aA → bB 반응에서 A의 소모 속도와 B의 생성 속도는 항상 같다.', False, '계수비만큼 다르다. $-\\frac{1}{a}\\frac{\\Delta[\\mathrm{A}]}{\\Delta t}=\\frac{1}{b}\\frac{\\Delta[\\mathrm{B}]}{\\Delta t}$'),
         ('중화 반응과 연소 반응은 빠른 반응, 철의 부식과 석회 동굴의 생성은 느린 반응이다.', True, '반응마다 빠르기가 다르다.')]
    for i in range(500):
        rng = R(17000 + i)
        if i % 2:
            o = one_of(rng, S, rng.random() < 0.5)
            if not o: continue
            want = dict((x[0], x[1]) for x in S)[o['ch'][o['ans'] - 1]]
            add(typ='D1', lv='하', ono=217, hw='s', body=[p('반응 속도에 대한 설명으로 ' + ('옳은' if want else '옳지 <u>않은</u>') + ' 것은?')], ch=o['ch'], ans=o['ans'], sol=o['sol'], chl='v',
                key='반응 속도의 정의와 측정', chk=dict(t='one', want=want))
        else:
            b = bogi_item(rng, S, 3)
            if not b: continue
            add(typ='D1', lv='중', ono=225, hw='s', body=[p('반응 속도의 표현과 측정에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])], ch=b['ch'], ans=b['ans'], sol=b['sol'],
                key='반응 속도의 측정', chk=dict(t='combo', truth=b['truth']))
    # 기체 부피·질량 평균 속도(222)
    for i in range(400):
        rng = R(17500 + i)
        t = rng.choice([10, 20, 25, 30, 40, 50, 60]); kind = rng.choice(['V', 'm'])
        if kind == 'V':
            V = rng.choice([10, 15, 20, 24, 30, 36, 40, 45, 50, 60, 75, 90]); v = V / t
            body = [p(f'묽은 염산에 마그네슘 조각을 넣었더니 {t} 초 동안 수소 기체 {V} mL가 발생하였다. 이 시간 동안의 평균 반응 속도(mL/s)는?')]
            sol = [f'평균 반응 속도 $=\\frac{{\\text{{발생한 기체의 부피}}}}{{\\text{{시간}}}}=\\frac{{{V}}}{{{t}}}={m(round(v, 3), 3)}$ mL/s']; u = 'mL/s'
        else:
            w = rng.choice([0.22, 0.44, 0.66, 0.88, 1.1, 1.32]); v = w / t
            body = [p(f'충분한 양의 묽은 염산에 탄산 칼슘을 넣고 전자저울 위에서 반응시켰더니 {t} 초 동안 질량이 {num(w)} g 감소하였다. 이 시간 동안 이산화 탄소의 평균 생성 속도(g/s)는?')]
            sol = ['발생한 CO2가 빠져나간 만큼 질량이 감소한다.', f'평균 생성 속도 $=\\frac{{{m(w)}}}{{{t}}}={m(round(v, 4), 4)}$ g/s']; u = 'g/s'
        v = round(v, 4)
        cands = [v * 2, v / 2, round(t / (V if kind == 'V' else w), 4), v * 10, v / 10, v * 3]
        ch, ans = pick_numeric(rng, v, [round(c, 4) for c in cands], lambda x: num(x, 4) + ' ' + u)
        if not ch: continue
        add(typ='D1', lv='하', ono=222, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='평균 반응 속도 = 변화량 ÷ 시간', chk=dict(t='num', v=v))

RX = [('A -> 2B', 1, 2, 'A', 'B'), ('2A -> B', 2, 1, 'A', 'B'), ('N2O5(g) -> 2NO2(g) + \\frac{1}{2}O2(g)', 1, 2, 'N2O5', 'NO2'),
      ('N2(g) + 3H2(g) -> 2NH3(g)', 3, 2, 'H2', 'NH3'), ('2NO2(g) -> 2NO(g) + O2(g)', 2, 1, 'NO2', 'O2'), ('H2(g) + I2(g) -> 2HI(g)', 1, 2, 'H2', 'HI'),
      ('2N2O5(g) -> 4NO2(g) + O2(g)', 2, 4, 'N2O5', 'NO2'), ('N2O4(g) -> 2NO2(g)', 1, 2, 'N2O4', 'NO2'), ('2A(g) -> 3B(g)', 2, 3, 'A', 'B')]

def eng_avg():
    for i in range(900):
        rng = R(18000 + i); eq, a, b, X, Y = rng.choice(RX)
        c0 = rng.choice([0.8, 1.0, 1.2, 1.6, 2.0, 2.4, 3.2, 4.0]); frac = rng.choice([0.25, 0.5, 0.75, 0.4, 0.6])
        dc = round(c0 * frac, 3); t = rng.choice([10, 20, 40, 50, 100, 5]); unit = rng.choice(['s', 'min'])
        lvl = ['하', '중', '중', '상'][i % 4]
        vX = round(dc / t, 5); vY = round(vX * b / a, 5); vR = round(vX / a, 5)
        ask = ['X', 'Y', 'R'][i % 3]
        body = [p(f'다음은 어떤 반응의 화학 반응식이다.'), box([eq]),
                p(f'반응이 시작될 때 [{X}]는 {num(c0, 3)} M이었고 {t} {"초" if unit == "s" else "분"} 후 {num(round(c0 - dc, 3), 3)} M이 되었다. 이 시간 동안 ' +
                  {'X': f'{X}의 평균 소모 속도', 'Y': f'{Y}의 평균 생성 속도', 'R': '반응의 평균 반응 속도(계수로 나눈 값)'}[ask] + f'(M/{unit})는?')]
        v = {'X': vX, 'Y': vY, 'R': vR}[ask]
        sol = [f'$-\\frac{{\\Delta[\\mathrm{{{X}}}]}}{{\\Delta t}}=\\frac{{{m(c0, 3)}-{m(round(c0 - dc, 3), 3)}}}{{{t}}}={m(vX, 5)}$ M/{unit}',
               f'계수비 {X} : {Y} = {a} : {b}이므로 {Y}의 생성 속도 $={m(vX, 5)}\\times\\frac{{{b}}}{{{a}}}={m(vY, 5)}$ M/{unit}',
               f'반응 속도 $v=-\\frac{{1}}{{{a}}}\\frac{{\\Delta[\\mathrm{{{X}}}]}}{{\\Delta t}}={m(vR, 5)}$ M/{unit}']
        cands = [vX, vY, vR, round(vX * a, 5), round(vY * 2, 5), round(c0 / t, 5), round(vX / b, 5)]
        ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 5) + f' M/{unit}')
        if not ch: continue
        add(typ='D2', lv=lvl, ono=226 if ask == 'X' else 228, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='계수비 = 농도 변화 속도의 비', chk=dict(t='num', v=v))
    # 농도 표 해석(226형 보기)
    for i in range(500):
        rng = R(18500 + i)
        c0 = rng.choice([1.6, 2.0, 2.4, 3.2, 0.8]); hl = rng.choice([1, 2, 5, 10])
        ts = [0, hl, 2 * hl, 3 * hl]; cs = [round(c0 / 2 ** k, 3) for k in range(4)]
        S = [(f'{ts[1]}~{ts[2]} 초 동안 A의 평균 소모 속도는 ${m(round((cs[1] - cs[2]) / hl, 4), 4)}$ M/s이다.', True, f'$\\frac{{{m(cs[1], 3)}-{m(cs[2], 3)}}}{{{hl}}}={m(round((cs[1] - cs[2]) / hl, 4), 4)}$'),
             (f'{ts[1]}~{ts[2]} 초 동안 A의 평균 소모 속도는 ${m(round((cs[0] - cs[1]) / hl, 4), 4)}$ M/s이다.', False, f'$\\frac{{{m(cs[1], 3)}-{m(cs[2], 3)}}}{{{hl}}}={m(round((cs[1] - cs[2]) / hl, 4), 4)}$ M/s이다.'),
             ('시간이 지날수록 반응 속도는 점점 빨라진다.', False, '같은 시간 동안 감소량이 점점 줄어드므로 느려진다.'),
             ('시간이 지날수록 반응 속도는 점점 느려진다.', True, '같은 시간 동안 감소량이 줄어든다.'),
             (f'{4 * hl} 초일 때 A의 농도는 {num(round(c0 / 16, 4), 4)} M이다.', True, f'농도가 {hl} 초마다 절반이 되므로 {num(round(c0 / 16, 4), 4)} M'),
             (f'{4 * hl} 초일 때 A의 농도는 {num(round(cs[3] - (cs[2] - cs[3]), 4), 4)} M이다.' if cs[3] - (cs[2] - cs[3]) > 0 else f'{4 * hl} 초일 때 A의 농도는 0 M이다.', False, f'{hl} 초마다 절반 → {num(round(c0 / 16, 4), 4)} M'),
             ('이 반응은 1차 반응이다.', True, f'반감기가 {hl} 초로 일정하다.'),
             ('이 반응의 반감기는 점점 길어진다.', False, f'반감기는 {hl} 초로 일정하다.')]
        b = bogi_item(rng, S, 3)
        if not b: continue
        body = [p('표는 A → B 반응에서 시간에 따른 A의 농도를 나타낸 것이다.'), table([['시간(s)'] + [str(t) for t in ts], ['[A](M)'] + [num(c, 3) for c in cs]]), p(Q_BOGI), bogi(b['bogi'])]
        add(typ='D2', lv='중', ono=226, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='농도 자료로 평균 반응 속도', chk=dict(t='combo', truth=b['truth']))

def rate_table(rng, m_, n_, k, nA='A', nB='B', sci_=False):
    base = rng.choice([0.01, 0.02, 0.1, 0.2, 0.05])
    rows = [(base, base), (base, base * 2), (base * 2, base)]
    if rng.random() < 0.5: rows = [(base, base), (base * 2, base), (base * 2, base * 2)]
    out = []
    for a, b in rows:
        v = k * a ** m_ * b ** n_
        out.append((a, b, v))
    return out

def eng_ratelaw():
    for i in range(1300):
        rng = R(19000 + i)
        m_, n_ = rng.choice([(1, 0), (0, 1), (1, 1), (2, 0), (2, 1), (1, 2), (0, 2), (2, 2)])
        k = rng.choice([0.5, 1, 2, 4, 5, 10, 20, 25, 40, 100, 200, 0.2, 0.25])
        names = rng.choice([('A', 'B'), ('X', 'Y'), ('NO', 'O2'), ('H2', 'I2'), ('NO2', 'O3')])
        rows = rate_table(rng, m_, n_, k)
        def vs(x): return f'${sci(x, 1)}$' if x < 0.001 or x >= 1000 else num(x, 6)
        tb = table([['실험', f'[{names[0]}](M)', f'[{names[1]}](M)', '초기 반응 속도(M/s)']] + [[str(j + 1), num(a, 3), num(b, 3), vs(v)] for j, (a, b, v) in enumerate(rows)])
        order = m_ + n_
        law = f'v=k[{names[0]}]' + (f'^{m_}' if m_ > 1 else '') if m_ else ''
        lawB = f'[{names[1]}]' + (f'^{n_}' if n_ > 1 else '') if n_ else ''
        lawS = f'$v=k' + (f'[{names[0]}]' + (f'^{m_}' if m_ > 1 else '') if m_ else '') + lawB + '$'
        lvl = LV[i % 4]
        # 차수 추론 풀이
        a1, b1, v1 = rows[0]
        def step(j1, j2):
            A1, B1, V1 = rows[j1]; A2, B2, V2 = rows[j2]
            if A1 == A2:
                r = round(V2 / V1, 6); f = B2 / B1
                return f'실험 {j1 + 1} → {j2 + 1}: [{names[1]}] {num(f)}배, 속도 {num(r)}배 → {names[1]}에 대해 {n_}차'
            r = round(V2 / V1, 6); f = A2 / A1
            if B1 == B2: return f'실험 {j1 + 1} → {j2 + 1}: [{names[0]}] {num(f)}배, 속도 {num(r)}배 → {names[0]}에 대해 {m_}차'
            return f'실험 {j1 + 1} → {j2 + 1}: [{names[0]}]와 [{names[1]}]가 모두 {num(f)}배, 속도 {num(r)}배 → 앞에서 구한 차수로 확인'
        sol = [step(0, 1), step(1, 2) if rows[1][0] != rows[2][0] or rows[1][1] != rows[2][1] else '', f'∴ 반응 속도식: {lawS} (전체 {order}차)',
               f'$k=\\frac{{v}}{{' + (f'[{names[0]}]' + (f'^{m_}' if m_ > 1 else '') if m_ else '') + lawB + f'}}=\\frac{{{sci(v1, 2) if v1 < 0.001 else m(v1, 6)}}}{{' +
               (f'({m(a1, 3)})' + (f'^{m_}' if m_ > 1 else '') if m_ else '') + (f'({m(b1, 3)})' + (f'^{n_}' if n_ > 1 else '') if n_ else '') + f'}}={m(k, 3)}$ ' + UNIT[order]]
        sol = [s for s in sol if s]
        if order == 0: continue
        if lvl == '하':
            # 속도식 고르기
            cand = set()
            for mm, nn in [(m_, n_), (1, 1), (n_, m_), (m_ + 1, n_), (m_, n_ + 1), (1, 0), (0, 1), (2, 1), (1, 2), (2, 0)]:
                if mm + nn == 0: continue
                s = '$v=k' + (f'[{names[0]}]' + (f'^{mm}' if mm > 1 else '') if mm else '') + (f'[{names[1]}]' + (f'^{nn}' if nn > 1 else '') if nn else '') + '$'
                cand.add(s)
            cand.discard(lawS); cand = list(cand)[:4]
            if len(cand) < 4: continue
            ch = cand + [lawS]; rng.shuffle(ch)
            body = [p(f'표는 {names[0]} + {names[1]} → 생성물 반응에서 반응물의 초기 농도에 따른 초기 반응 속도를 측정한 결과이다.'), tb, p('이 반응의 반응 속도식으로 옳은 것은?')]
            add(typ='D3', lv='하', ono=221, hw='v', body=body, ch=ch, ans=ch.index(lawS) + 1, sol=sol, key='한 반응물의 농도만 바꾼 두 실험을 비교', chk=dict(t='law', m=m_, n=n_, v=lawS))
        elif lvl == '중':
            body = [p(f'표는 {names[0]} + {names[1]} → 생성물 반응에서 반응물의 초기 농도에 따른 초기 반응 속도를 측정한 결과이다.'), tb, p('이 반응의 반응 속도 상수 $k$는?')]
            cands = [k * 2, k / 2, k * 10, k / 10, round(v1 / a1, 6), round(v1 / (a1 * b1), 6), k * 4]
            fm = lambda x: num(x, 4) + ' ' + fmt_unit(order)
            ch, ans = pick_numeric(rng, k, [c for c in cands if abs(c - k) > 1e-9], fm)
            if not ch: continue
            add(typ='D3', lv='중', ono=233, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='차수 결정 → 한 실험값 대입으로 $k$', chk=dict(t='k', v=k))
        elif lvl == '상':
            # 표의 빈칸 예측
            na, nb = rng.choice([2, 3, 0.5]), rng.choice([2, 3, 0.5])
            A4, B4 = rows[0][0] * na, rows[0][1] * nb; V4 = k * A4 ** m_ * B4 ** n_
            tb2 = table([['실험', f'[{names[0]}](M)', f'[{names[1]}](M)', '초기 반응 속도(M/s)']] + [[str(j + 1), num(a, 3), num(b, 3), vs(v)] for j, (a, b, v) in enumerate(rows)] +
                        [['4', num(A4, 4), num(B4, 4), '(가)']])
            body = [p(f'표는 {names[0]} + {names[1]} → 생성물 반응에서 반응물의 초기 농도에 따른 초기 반응 속도를 측정한 결과이다.'), tb2, p('(가)에 알맞은 값(M/s)은?')]
            sol2 = sol + [f'실험 4: 실험 1에 비해 [{names[0]}] {num(na)}배, [{names[1]}] {num(nb)}배 → 속도 ${m(na)}^{{{m_}}}\\times {m(nb)}^{{{n_}}}={m(round(na ** m_ * nb ** n_, 4), 4)}$배',
                          f'(가) $={vs(V4).strip("$")}$ M/s']
            cands = [V4 * 2, V4 / 2, rows[0][2] * na * nb, rows[0][2] * (na + nb), V4 * 4, V4 / 4, rows[0][2] * na ** 2 * nb ** 2]
            ch, ans = pick_numeric(rng, V4, [c for c in cands if abs(c - V4) > 1e-12], lambda x: vs(x))
            if not ch: continue
            add(typ='D3', lv='상', ono=233, hw='v', body=body, ch=ch, ans=ans, sol=sol2, key='반응 차수로 속도 예측', chk=dict(t='pred', v=V4))
        else:
            S = [(f'반응 속도식은 {lawS}이다.', True, f'차수 분석 결과 {lawS}이다.'),
                 (f'전체 반응 차수는 {order}차이다.', True, f'${m_}+{n_}={order}$'),
                 (f'전체 반응 차수는 {order + 1}차이다.', False, f'${m_}+{n_}={order}$차이다.'),
                 (f'반응 속도 상수의 단위는 {UNIT[order]}이다.', True, f'{order}차 반응이다.'),
                 (f'반응 속도 상수의 단위는 {UNIT[(order % 3) + 1 if order < 3 else 1]}이다.', False, f'{order}차 반응이므로 {UNIT[order]}이다.'),
                 (f'$k={m(k, 3)}$이다.', True, f'실험 1 대입: $k={m(k, 3)}$'),
                 (f'$k={m(k * 10, 3)}$이다.', False, f'$k={m(k, 3)}$이다.'),
                 (f'[{names[0]}]와 [{names[1]}]를 모두 2배로 하면 반응 속도는 {2 ** order}배가 된다.', True, f'${2}^{{{m_}}}\\times 2^{{{n_}}}={2 ** order}$'),
                 (f'[{names[0]}]와 [{names[1]}]를 모두 2배로 하면 반응 속도는 {2 ** order * 2}배가 된다.', False, f'{2 ** order}배이다.'),
                 (f'{names[1]}의 농도를 바꾸어도 반응 속도는 변하지 않는다.', n_ == 0, f'{names[1]}에 대해 {n_}차이다.')]
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p(f'표는 {names[0]} + {names[1]} → 생성물 반응에서 반응물의 초기 농도에 따른 초기 반응 속도를 측정한 결과이다.'), tb, p(Q_BOGI + ' (단, 온도는 일정하다.)'), bogi(b['bogi'])]
            add(typ='D3', lv='최', ono=232, hw='v', body=body, ch=b['ch'], ans=b['ans'], sol=sol + b['sol'], key='초기 속도법으로 반응 속도식 결정', chk=dict(t='combo', truth=b['truth']))

def fmt_unit(order): return {0: 'M·s⁻¹', 1: 's⁻¹', 2: 'M⁻¹·s⁻¹', 3: 'M⁻²·s⁻¹', 4: 'M⁻³·s⁻¹'}[order]

def eng_half():
    for i in range(1300):
        rng = R(20000 + i); lvl = LV[i % 4]
        hl = rng.choice([5, 10, 20, 25, 30, 50, 100, 2, 3, 4, 15]); unit = rng.choice(['초', '분'])
        c0 = rng.choice([0.8, 1.6, 2.0, 2.4, 3.2, 4.0, 0.4, 0.64, 1.0])
        k_ = rng.choice([1, 2, 3, 4, 5])
        if lvl == '하':
            c1 = round(c0 / 2 ** k_, 4)
            body = [p(f'어떤 1차 반응에서 반응물 A의 반감기는 {hl} {unit}이다. A의 농도가 {num(c0, 3)} M에서 {num(c1, 4)} M이 될 때까지 걸리는 시간은?')]
            v = hl * k_
            sol = [f'1차 반응의 반감기는 농도와 관계없이 {hl} {unit}로 일정하다.', f'{num(c0, 3)} M → {num(c1, 4)} M: $\\frac{{1}}{{{2 ** k_}}}$ = 반감기 {k_}번', f'걸린 시간 $={k_}\\times {hl}={v}$ {unit}']
            cands = [hl * (k_ + 1), hl * max(1, k_ - 1), hl * 2 ** k_, hl / 2, hl * k_ * 2, hl * (k_ + 2)]
            ch, ans = pick_numeric(rng, v, cands, lambda x: num(x, 1) + ' ' + unit)
            if not ch: continue
            add(typ='D4', lv='하', ono=224, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='1차 반응: 반감기 일정', chk=dict(t='num', v=v))
        elif lvl == '중':
            t = hl * k_; c1 = round(c0 / 2 ** k_, 5)
            body = [p('표는 1차 반응인 A → B에서 시간에 따른 A의 농도를 나타낸 것이다.'),
                    table([[f'시간({unit})', '0', str(hl), str(2 * hl)], ['[A](M)', num(c0, 3), num(c0 / 2, 4), num(c0 / 4, 4)]]),
                    p(f'{t} {unit}일 때 A의 농도(M)는?')]
            sol = [f'표에서 {hl} {unit}마다 농도가 절반이 되므로 반감기는 {hl} {unit}이다.', f'{t} {unit} = 반감기 {k_}번 → $[\\mathrm{{A}}]={m(c0, 3)}\\times\\left(\\frac{{1}}{{2}}\\right)^{{{k_}}}$'.replace('\\left(', '(').replace('\\right)', ')'),
                   f'$={m(c1, 5)}$ M']
            cands = [round(c0 / 2 ** (k_ + 1), 5), round(c0 / 2 ** max(0, k_ - 1), 5), round(c0 - c0 / 2 * k_, 5) if c0 - c0 / 2 * k_ > 0 else round(c0 / 3, 5), round(c0 / (2 * k_), 5), round(c0 / 2 ** (k_ + 2), 5)]
            ch, ans = pick_numeric(rng, c1, cands, lambda x: num(x, 5) + ' M')
            if not ch: continue
            add(typ='D4', lv='중', ono=224, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='남은 양 = 처음 × (1/2)^(반감기 횟수)', chk=dict(t='num', v=c1))
        elif lvl == '상':
            # 2A → B 생성물 농도(242형)
            a_, b_ = rng.choice([(1, 2), (2, 1), (1, 1), (1, 3)])
            k2 = rng.choice([1, 2, 3])
            reacted = c0 * (1 - 1 / 2 ** k2); prod = round(reacted * b_ / a_, 5)
            eq = f'{"" if a_ == 1 else a_}A(g) -> {"" if b_ == 1 else b_}B(g)'
            body = [p(f'다음은 1차 반응의 화학 반응식이다.'), box([eq]), p(f'A의 초기 농도가 {num(c0, 3)} M이고 반감기가 {hl} {unit}일 때, {hl * k2} {unit} 후 B의 농도(M)는? (단, B의 초기 농도는 0이다.)')]
            sol = [f'{hl * k2} {unit} = 반감기 {k2}번 → 남은 A $={m(c0, 3)}\\times\\frac{{1}}{{{2 ** k2}}}={m(round(c0 / 2 ** k2, 5), 5)}$ M',
                   f'반응한 A $={m(round(reacted, 5), 5)}$ M', f'계수비 A : B = {a_} : {b_} → B $={m(round(reacted, 5), 5)}\\times\\frac{{{b_}}}{{{a_}}}={m(prod, 5)}$ M']
            cands = [round(reacted, 5), round(c0 / 2 ** k2, 5), round(prod * 2, 5), round(prod / 2, 5), round(c0 / 2 ** k2 * b_ / a_, 5), round(c0 * b_ / a_, 5)]
            ch, ans = pick_numeric(rng, prod, cands, lambda x: num(x, 5) + ' M')
            if not ch: continue
            add(typ='D4', lv='상', ono=242, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='반감기 + 계수비', chk=dict(t='num', v=prod))
        else:
            # 최: 두 조건 비교 보기
            hA = rng.choice([10, 20, 30]); hB = hA * rng.choice([2, 0.5]); cA = rng.choice([1.6, 3.2, 6.4]); cB = rng.choice([1.6, 3.2])
            T = hA * rng.choice([2, 3]) if hA <= hB else hB * rng.choice([2, 3])
            rA = round(cA / 2 ** (T / hA), 4); rB = round(cB / 2 ** (T / hB), 4)
            S = [(f'반응 속도 상수는 (가)에서가 (나)에서보다 {"크다" if hA < hB else "작다"}.', True, '반감기가 짧을수록 $k$가 크다.'),
                 (f'반응 속도 상수는 (가)에서가 (나)에서보다 {"작다" if hA < hB else "크다"}.', False, '반감기가 짧을수록 $k$가 크다.'),
                 (f'{num(T)} 분일 때 [A]는 (가)에서 {num(rA, 4)} M이다.', True, f'반감기 {num(T / hA)}번: ${m(cA)}\\times(\\frac{{1}}{{2}})^{{{m(T / hA)}}}={m(rA, 4)}$'),
                 (f'{num(T)} 분일 때 [A]는 (나)에서 {num(round(rB * 2, 4), 4)} M이다.', False, f'(나)는 반감기 {num(T / hB)}번 → {num(rB, 4)} M이다.'),
                 ('(가)와 (나)는 모두 1차 반응이다.', True, '각각 반감기가 일정하다.'),
                 ('(가)의 초기 농도를 2배로 하면 (가)의 반감기도 2배가 된다.', False, '1차 반응의 반감기는 초기 농도와 관계없다.'),
                 (f'초기 반응 속도는 (가)가 (나)의 {num(round((cA / hA) / (cB / hB), 3), 3)}배이다.', True, f'$v=k[\\mathrm{{A}}]$, $k\\propto\\frac{{1}}{{t_{{1/2}}}}$ → $\\frac{{{m(cA)}/{hA}}}{{{m(cB)}/{m(hB)}}}$')]
            b = bogi_item(rng, S, 3)
            if not b: continue
            body = [p('표는 서로 다른 온도에서 A(g) → B(g) 1차 반응이 일어날 때의 자료이다.'),
                    table([['실험', '[A]의 초기 농도(M)', '반감기(분)'], ['(가)', num(cA), num(hA)], ['(나)', num(cB), num(hB)]]), p(Q_BOGI), bogi(b['bogi'])]
            add(typ='D4', lv='최', ono=246, hw='s', body=body, ch=b['ch'], ans=b['ans'], sol=b['sol'], key='반감기와 반응 속도 상수', chk=dict(t='combo', truth=b['truth']))
    # 0차·1차 구분(236, 278)
    S0 = [('0차 반응은 반응물의 농도와 관계없이 반응 속도가 일정하다.', True, '$v=k$'), ('0차 반응의 농도−시간 그래프는 직선이다.', True, '일정한 속도로 감소한다.'),
          ('0차 반응의 반감기는 일정하다.', False, '농도가 줄수록 반감기가 짧아진다.'), ('1차 반응의 반감기는 초기 농도에 비례한다.', False, '1차 반응의 반감기는 일정하다.'),
          ('1차 반응의 반응 속도는 반응물의 농도에 비례한다.', True, '$v=k[\\mathrm{A}]$'), ('1차 반응에서 $k$의 단위는 s^{-1}이다.', True, '$\\frac{\\text{M/s}}{\\text{M}}$'),
          ('0차 반응에서 $k$의 단위는 M·s^{-1}이다.', True, '$v=k$이므로 $k$의 단위는 속도와 같다.'), ('반감기가 일정하면 1차 반응이다.', True, '1차 반응의 특징이다.'),
          ('반응 속도−[A] 그래프가 원점을 지나는 직선이면 0차 반응이다.', False, '원점을 지나는 직선이면 1차 반응이다.')]
    for i in range(400):
        rng = R(21000 + i)
        b = bogi_item(rng, S0, 3)
        if not b: continue
        add(typ='D4', lv='중', ono=236, hw='s', body=[p('반응 차수와 반감기에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'), bogi(b['bogi'])],
            ch=b['ch'], ans=b['ans'], sol=b['sol'], key='0차·1차 반응의 특징', chk=dict(t='combo', truth=b['truth']))

def eng_pressure():
    """기체 압력 자료(239, 245)."""
    for i in range(700):
        rng = R(22000 + i)
        a = rng.choice([1, 2]); b = rng.choice([1, 2, 3]); c = rng.choice([0, 1])
        if b + c == a: continue
        P0 = rng.choice([1.6, 2.4, 3.2, 4.0, 4.8, 6.4]); hl = rng.choice([5, 10, 20, 't'])
        eq = f'{"" if a == 1 else a}A(g) -> {"" if b == 1 else b}B(g)' + (f' + C(g)' if c else '')
        rows = []
        for kk in range(4):
            PA = P0 / 2 ** kk; x = (P0 - PA) / a
            rows.append(round(PA + b * x + c * x, 3))
        tl = ['0', 't', '2t', '3t'] if hl == 't' else ['0', str(hl), str(2 * hl), str(3 * hl)]
        lvl = ['상', '최'][i % 2]
        ask = rng.choice(['PA', 'PB', 'hl'])
        kk = rng.choice([1, 2, 3]); PA = round(P0 / 2 ** kk, 4); x = (P0 - PA) / a; PB = round(b * x, 4)
        body = [p('다음은 강철 용기에서 일어나는 A(g)의 분해 반응의 화학 반응식이다.'), box([eq]),
                p('표는 A(g)만 넣고 일정한 온도에서 반응시킬 때 시간에 따른 용기 속 전체 압력을 나타낸 것이다.'),
                table([[f'시간{"" if hl == "t" else "(s)"}'] + tl, ['전체 압력(기압)'] + [num(r, 3) for r in rows]])]
        sol = [f'A가 $x$ 기압 반응하면 전체 압력은 $({b + c}-{a})\\times\\frac{{x}}{{{a}}}$만큼 변한다.' if True else '',
               '각 시각의 A의 부분 압력: ' + ', '.join(f'{tl[q]}: {num(round(P0 / 2 ** q, 4), 4)}' for q in range(4)) + ' 기압',
               f'A의 부분 압력이 일정한 시간마다 절반 → 1차 반응, 반감기 = {tl[1]}{"" if hl == "t" else " s"}']
        if ask == 'PA':
            body.append(p(f'{tl[kk]}{"" if hl == "t" else " 초"}일 때 A의 부분 압력(기압)은?')); v = PA
            cands = [round(P0 / 2 ** (kk + 1), 4), round(P0 / 2 ** max(0, kk - 1), 4), round(rows[kk] - PA, 4), rows[kk], round(P0 - PA, 4)]
        elif ask == 'PB':
            body.append(p(f'{tl[kk]}{"" if hl == "t" else " 초"}일 때 B의 부분 압력(기압)은?')); v = PB
            sol.append(f'{tl[kk]}: A {num(round(P0 - PA, 4), 4)} 기압 반응 → B $={m(round(P0 - PA, 4), 4)}\\times\\frac{{{b}}}{{{a}}}={m(PB, 4)}$ 기압')
            cands = [round(P0 - PA, 4), round(PB * 2, 4), round(PB / 2, 4), PA, rows[kk], round(x, 4)]
        else:
            body.append(p('이 반응의 반감기는?')); v = 1
            ch = [f'{tl[1]}', f'{tl[2]}', f'{tl[3]}', '일정하지 않다', f'{tl[1]}의 절반']
            if hl == 't': ch = ['$t$', '$2t$', '$3t$', '일정하지 않다', '$\\frac{t}{2}$']
            else: ch = [f'{hl} s', f'{2 * hl} s', f'{3 * hl} s', '일정하지 않다', f'{num(hl / 2)} s']
            add(typ='D5', lv=lvl, ono=239, hw='v', body=body, ch=ch, ans=1, sol=sol, key='압력 자료: 부분 압력 ∝ 농도', chk=dict(t='hlP', v=1))
            continue
        ch, ans = pick_numeric(rng, v, [c for c in cands if c is not None], lambda q: num(q, 4) + ' 기압')
        if not ch: continue
        add(typ='D5', lv=lvl, ono=245 if c else 239, hw='v', body=body, ch=ch, ans=ans, sol=sol, key='압력 자료: 부분 압력 ∝ 농도', chk=dict(t='num', v=v))

def run():
    eng_concept(); eng_avg(); eng_ratelaw(); eng_half(); eng_pressure()
