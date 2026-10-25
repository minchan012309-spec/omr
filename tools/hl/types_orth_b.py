"""Ⅲ-B 한글 맞춤법: 형태 (hl063~hl072)"""
from hllib import *
from orth_gen import *
from types_orth_a import *
import kb_orth1 as K1, kb_orth2 as K2, kb_orth3 as K3, kb_tf
IR = K2.IRR
CATS_IRR = ['ㅅ불규칙', 'ㅎ불규칙', 'ㄷ불규칙', 'ㅂ불규칙', 'ㅜ불규칙', '르불규칙', '러불규칙', '여불규칙']
CAT_NAME = {'ㄹ탈락': 'ㄹ 탈락', 'ㅅ불규칙': 'ㅅ 불규칙', 'ㅎ불규칙': 'ㅎ 불규칙', 'ㅜ불규칙': 'ㅜ 불규칙', 'ㅡ탈락': 'ㅡ 탈락', 'ㄷ불규칙': 'ㄷ 불규칙', 'ㅂ불규칙': 'ㅂ 불규칙', '여불규칙': '여 불규칙', '러불규칙': '러 불규칙', '르불규칙': '르 불규칙', '규칙': '규칙'}
GROUP_STEM = ['ㅅ불규칙', 'ㄷ불규칙', 'ㅂ불규칙', 'ㅜ불규칙', '르불규칙']
GROUP_END = ['여불규칙', '러불규칙']

def _disp(d):
    return '%s(%s)' % (d['verb'], d['fa'])

def irr_E(cat_list):
    out = []
    for d in IR:
        if d['cat'] in cat_list:
            out.append(E(_disp(d), [], "'%s' → '%s': %s. %s" % (d['verb'], d['fa'], CAT_NAME[d['cat']] + (' 활용' if d['cat'] == '규칙' else ' 활용'), d['note']), d['cat']))
    return out
IRR_ALL = {c: irr_E([c]) for c in CAT_NAME}
REG_ALL = IRR_ALL['규칙'] + IRR_ALL['ㄹ탈락'] + IRR_ALL['ㅡ탈락']
IRREG_ALL = sum((IRR_ALL[c] for c in CATS_IRR), [])
CATKEYS = {'ㅅ불규칙': "어간 끝 'ㅅ'이 줄어드는", 'ㅎ불규칙': "어간 끝 'ㅎ'이 줄고 어미도 바뀌는", 'ㄷ불규칙': "어간 끝 'ㄷ'이 'ㄹ'로 바뀌는", 'ㅂ불규칙': "어간 끝 'ㅂ'이 '우'로 바뀌는", 'ㅜ불규칙': "어간 끝 'ㅜ'가 줄어드는", '르불규칙': "어간 '르'가 'ㄹㄹ'로 바뀌는", '러불규칙': "어미 '-어'가 '-러'로 바뀌는", '여불규칙': "어미 '-아'가 '-여'로 바뀌는"}

def _vowel_ah(ch):
    c = ord(ch) - 44032
    jung = c % 588 // 28
    return '아' if jung in (0, 2, 8) else '어'

def irr_bad(d):
    v = d['verb'].split('[')[0]
    stem = v[:-1]
    cat = d['cat']
    fa = d['fa']
    out = []
    if cat == 'ㅅ불규칙':
        out = [stem + _vowel_ah(stem[-1])]
    elif cat == 'ㅎ불규칙':
        out = [stem + _vowel_ah(stem[-1])]
    elif cat == 'ㄷ불규칙' and v not in ('걷다',):
        out = [stem + _vowel_ah(stem[-1])]
    elif cat == 'ㅂ불규칙':
        if v in ('돕다', '곱다'):
            out = [stem[:-1] + {'돕': '도', '곱': '고'}[stem[-1:]] + '워']
        else:
            out = [stem + _vowel_ah(stem[-1]), fa[:-1] + '와']
    elif cat == '르불규칙':
        out = [stem[:-1] + {'아': '라', '어': '러'}[_vowel_ah(stem[-2])], stem + _vowel_ah(stem[-2])]
    elif cat == '러불규칙':
        out = [stem + '어']
    elif cat == 'ㅜ불규칙':
        out = ['푸어']
    elif cat == 'ㅡ탈락':
        out = [stem + _vowel_ah(stem[-1])]
    elif cat == '규칙':
        out = {'닫다': ['달아'], '입다': ['이워'], '좁다': ['조워'], '씻다': ['씨어'], '벗다': ['버어'], '웃다': ['우어'], '솟다': ['소아'], '놓다': ['노아'], '쌓다': ['싸아'], '접다': ['저워'], '씹다': ['씨워'], '잡다': ['자워'], '좋다': ['조아']}.get(v, [])
    return [x for x in out if x != fa and x]
IRR_SPELL = []
for d in IR:
    if d['cat'] in ('ㄹ탈락',):
        stem = d['verb'][:-1]
        bads = [stem + '니', stem + '으니']
        bads = [b for b in bads if b != d['fu']]
        IRR_SPELL.append(E(d['fu'], bads, "'%s'은(는) 어간 끝 'ㄹ'이 'ㄴ, ㅂ, ㅅ, 오, ㄹ' 앞에서 줄어 소리 나는 대로 '%s'로 적는다(제18항 1)." % (d['verb'], d['fu']), d['cat']))
        continue
    bs = irr_bad(d)
    if bs:
        IRR_SPELL.append(E(d['fa'], bs, "'%s'의 활용형은 '%s'이다. %s" % (d['verb'], d['fa'], d['note']), d['cat']))
IRR_SPELL = [e for e in IRR_SPELL if len(e.bads) > 0]

def _sort_ok(t):
    return t

@T('hl063')
def g063(r, k):
    P1 = JO + EO
    c = r.randrange(8)
    if c == 0:
        return tpl_choose(r, JO, 'ok', None, '하', 'A1', ref=[1])
    if c == 1:
        return tpl_choose(r, EO, 'ok', None, '하', 'A2', ref=[1]) if len(EO) >= 5 else tpl_choose(r, P1, 'ok', None, '하', 'A2', ref=[1])
    if c == 2:
        return tpl_choose(r, P1, 'bad', None, '중', 'B1', ref=[1])
    if c == 3:
        return tpl_choose(r, P1, 'ok', 'josa', '중', 'D1', ref=[1])
    if c == 4:
        return tpl_stmt3(r, P1, 'josa', '상', 'C1', [1])
    if c == 5:
        d = r.sample(K2.OH, 5)
        rows = [dict(s=x[0], ok=x[0], bad=[x[1]], why=x[2]) for x in d]
        xs = [(x[0], x[0], x[1], x[2], x[0]) for x in d]
        k2 = r.randrange(5)
        lines = []
        steps = []
        for i, x in enumerate(xs):
            use_bad = i == k2
            form = x[2] if use_bad else x[1]
            lines.append('%s %s' % ('㉠㉡㉢㉣㉤'[i], '<u>%s</u>' % form))
            steps.append('%s %s: %s' % ('㉠㉡㉢㉣㉤'[i], '틀리다 → ' + x[1] if use_bad else '옳다', x[3]))
        body = P('㉠~㉤ 중 한글 맞춤법에 어긋난 것은?') + '<div class="bogi">' + ''.join(('<p>%s</p>' % l for l in lines)) + '</div>'
        return mcs(body, [(o, i == k2) for i, o in enumerate(['㉠', '㉡', '㉢', '㉣', '㉤'])], steps=steps, core="종결형의 '-오'는 '오'로, 연결형의 '이요'는 '이요'로 적는다(제15항 붙임 2·3).", lv='상', fam='L1', r=r, ref=[1], vertical=False)
    if c == 6:
        return tpl_class(r, ('체언과 조사를 구별하여 적은 말', JO), ('어간과 어미를 구별하여 적은 말', EO), r.choice(['ok', 'bad']), '중', 'K1', [1])
    return tpl_tf(r, kb_tf.ORTH_CONCEPT, 'bad', lv='중', fam='T1', ref=[1])

@T('hl064')
def g064(r, k):
    c = r.randrange(9)
    if c <= 1:
        cat = r.choice(CATS_IRR)
        right = r.choice(IRR_ALL[cat])
        wrongs_pool = [e for e in IRREG_ALL + REG_ALL if e.g != cat]
        ws = r.sample(wrongs_pool, 4)
        body = P('다음 중 %s 불규칙 활용을 하는 용언은?' % CATKEYS[cat])
        st = ["'%s': %s" % (right.ok, right.why)] + ["'%s': %s" % (w.ok, w.why) for w in ws]
        return mc(body, right.ok, [w.ok for w in ws], steps=st, core=right.why, lv=r.choice(['중', '상']), fam='A' + cat[0], r=r, ref=[2])
    if c == 2:
        right = r.choice(REG_ALL)
        ws = r.sample(IRREG_ALL, 4)
        body = P('다음 중 규칙 활용을 하는 용언은?')
        st = ["'%s': %s" % (right.ok, right.why)] + ["'%s': %s" % (w.ok, w.why) for w in ws]
        return mc(body, right.ok, [w.ok for w in ws], steps=st, core=right.why, lv='중', fam='B', r=r, ref=[2])
    if c == 3:
        right = r.choice(IRREG_ALL)
        ws = r.sample(REG_ALL, 4)
        body = P('다음 중 불규칙 활용을 하는 용언은?')
        st = ["'%s': %s" % (right.ok, right.why)] + ["'%s': %s" % (w.ok, w.why) for w in ws]
        return mc(body, right.ok, [w.ok for w in ws], steps=st, core=right.why, lv='하', fam='C', r=r, ref=[2])
    if c == 4:
        a_end = sum((IRR_ALL[x] for x in GROUP_END), [])
        a_stem = sum((IRR_ALL[x] for x in GROUP_STEM), [])
        if r.random() < 0.5:
            right = r.choice(a_end)
            ws = r.sample(a_stem + REG_ALL, 4)
            body = P('다음 중 어간은 그대로이고 어미가 바뀌는 불규칙 활용을 하는 용언은?')
        else:
            right = r.choice(a_stem)
            ws = r.sample(a_end + REG_ALL, 4)
            body = P('다음 중 어간의 모양이 바뀌는 불규칙 활용을 하는 용언은?')
        st = ["'%s': %s" % (right.ok, right.why)] + ["'%s': %s" % (w.ok, w.why) for w in ws]
        return mc(body, right.ok, [w.ok for w in ws], steps=st, core=right.why, lv='상', fam='D', r=r, ref=[2])
    if c == 5:
        rules = [("어간 끝 'ㅅ'이 줄거나 'ㄷ'이 'ㄹ'로, 'ㅂ'이 '우'로 바뀌는 불규칙 활용(어간이 바뀜).", IRR_ALL['ㅅ불규칙'] + IRR_ALL['ㄷ불규칙'] + IRR_ALL['ㅂ불규칙'], '어간이 바뀌는 불규칙 활용이다'), ("어미 '-어'가 '-러'로, '-아'가 '-여'로 바뀌는 불규칙 활용(어미가 바뀜).", IRR_ALL['러불규칙'] + IRR_ALL['여불규칙'], '어미가 바뀌는 불규칙 활용이다'), ('어간의 모양이 달라지지만 예외가 없는 규칙 활용(ㄹ 탈락, ㅡ 탈락).', IRR_ALL['ㄹ탈락'] + IRR_ALL['ㅡ탈락'], '규칙 활용이다')]
        return tpl_label(r, rules, '최', 'R1', [2], mode=r.choice(['bad', 'ok']), head='')
    if c == 6:
        xs = r.sample(IR, 3)
        stm = []
        for d in xs:
            truth = r.random() < 0.5
            cat = d['cat'] if truth else r.choice([x for x in CAT_NAME if x != d['cat']])
            txt = "'%s'의 '%s'은(는) %s 활용이다." % (d['verb'], d['fa'], CAT_NAME[cat])
            stm.append((txt, truth, d['note']))
        return bogi('용언의 활용에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='E', r=r, ref=[2], ask='')
    if c == 7:
        ex = [('이르러', '러 불규칙', "'이르다(도달하다)'는 어간 '이르-'에 어미 '-어'가 '-러'로 바뀐 '이르러'가 된다."), ('일러', '르 불규칙', "'이르다(말하다)'는 '르'의 'ㅡ'가 줄고 'ㄹ'이 덧나 '일러'가 된다."), ('치러', '규칙(ㅡ 탈락)', "'치르다'는 'ㅡ'가 탈락하고 'ㄹ'이 연음된 규칙 활용이다."), ('따라', '규칙(ㅡ 탈락)', "'따르다'는 'ㅡ'가 탈락하는 규칙 활용이다."), ('불러', '르 불규칙', "'부르다'는 '르'의 'ㅡ'가 줄고 'ㄹ'이 덧나 '불러'가 된다."), ('푸르러', '러 불규칙', "'푸르다'는 어미 '-어'가 '-러'로 바뀌어 '푸르러'가 된다.")]
        a = r.choice(ex)
        others = [e for e in ex if e[1] != a[1]]
        if len(others) < 2:
            return None
        kinds = ['러 불규칙', '르 불규칙', '규칙(ㅡ 탈락)', 'ㅂ 불규칙', 'ㅅ 불규칙', '여 불규칙']
        right = "'%s'은(는) %s 활용이다." % (a[0], a[1])
        wrongs = ["'%s'은(는) %s 활용이다." % (a[0], x) for x in kinds if x != a[1]]
        return mc(P("활용형 '%s'에 대한 설명으로 옳은 것은?" % a[0]), right, wrongs, steps=[a[2]], core=a[2], lv='상', fam='F', r=r, ref=[2], vertical=True)
    return _irr_pair(r)

def _irr_pair(r):
    cat = r.choice(['ㅂ불규칙', 'ㄷ불규칙', 'ㅅ불규칙', 'ㅎ불규칙', '르불규칙'])
    a, b = r.sample(IRR_ALL[cat], 2)
    ws = r.sample([e for e in IRREG_ALL + REG_ALL if e.g != cat], 4)
    body = P("'%s'와 활용 방식이 같은 것은?" % a.ok.split('(')[0])
    st = ["'%s'와 '%s'은(는) 모두 %s 활용이다. %s" % (a.ok, b.ok, CAT_NAME[cat], a.why)] + ["'%s': %s" % (w.ok, w.why) for w in ws]
    return mc(body, b.ok, [w.ok for w in ws], steps=st, core=a.why, lv='중', fam='H', r=r, ref=[2])

@T('hl065')
def g065(r, k):
    c = r.randrange(5)
    if c <= 1:
        return tpl_choose(r, IRR_SPELL, 'ok', None, '중', 'A', ref=[2], ask_ok='다음 중 용언의 활용형 표기가 옳은 것은?')
    if c == 2:
        return tpl_choose(r, IRR_SPELL, 'bad', None, '중', 'B', ref=[2], ask_bad='다음 중 용언의 활용형 표기가 옳지 않은 것은?')
    if c == 3:
        return tpl_stmt3(r, IRR_SPELL, None, '상', 'C', [2])
    rows = []
    for d in IR:
        if d['cat'] in ('ㅂ불규칙', 'ㄷ불규칙', 'ㅅ불규칙', 'ㅎ불규칙', '르불규칙') and irr_bad(d):
            rows.append((d, irr_bad(d)[0]))
    xs = r.sample(rows, 5)
    k2 = r.randrange(5)
    lines = []
    st = []
    tm = ['이 책은 {0} 읽기에 좋다.', '그 일이 {0} 걱정이다.', '오늘따라 그가 {0} 보인다.', '창밖의 풍경이 {0} 아름답다.', '나는 그것을 {0} 알고 있었다.']
    for i, (d, b) in enumerate(xs):
        form = b if i == k2 else d['fa']
        lines.append('%s %s' % ('㉠㉡㉢㉣㉤'[i], '<u>%s</u>(%s)' % (form, d['verb'])))
        st.append('%s %s' % ('㉠㉡㉢㉣㉤'[i], "'%s'은(는) 틀렸다 → '%s'. %s" % (form, d['fa'], d['note']) if i == k2 else "'%s'은(는) 옳다. %s" % (form, d['note'])))
    body = P('㉠~㉤ 중 활용형의 표기가 옳지 않은 것은? (괄호 안은 기본형)') + '<div class="bogi">' + ''.join(('<p>%s</p>' % l for l in lines)) + '</div>'
    return mcs(body, [(o, i == k2) for i, o in enumerate(['㉠', '㉡', '㉢', '㉣', '㉤'])], steps=st, core=xs[k2][0]['note'], lv='상', fam='L', r=r, ref=[2], vertical=False)

@T('hl066')
def g066(r, k):
    P1 = NI + NE
    c = r.randrange(8)
    if c == 0:
        return tpl_choose(r, P1, 'ok', None, '하', 'A1', ref=[3])
    if c == 1:
        return tpl_choose(r, P1, 'bad', None, '중', 'B1', ref=[3])
    if c == 2:
        return tpl_choose(r, P1, 'ok', 'noun', '중', 'D1', ref=[3])
    if c == 3:
        return tpl_stmt3(r, P1, 'noun', '상', 'C1', [3])
    if c == 4:
        rules = [("어간에 '-이'나 '-음/-ㅁ'이 붙어 명사로 된 것은 그 어간의 원형을 밝히어 적는다.", P1, '원형을 밝히어 적은 것이다'), ('어간의 뜻과 멀어진 것은 원형을 밝히어 적지 않는다.', FAR, '소리대로 적은 것이다'), ("'-이/-음' 이외의 모음으로 시작된 접미사가 붙어 다른 품사로 바뀐 것은 원형을 밝히어 적지 않는다.", BOT, '소리대로 적은 것이다')]
        return tpl_label(r, rules, '최', 'R1', [3], mode=r.choice(['bad', 'ok']))
    if c == 5:
        return tpl_class(r, ('어간의 원형을 밝히어 적은 명사', P1), ('어간의 원형을 밝히지 않고 소리대로 적은 말', BOT + FAR), r.choice(['ok', 'bad']), '중', 'K1', [3])
    if c == 6:
        return tpl_same(r, [('ni', NI), ('ne', NE), ('bot', BOT), ('far', FAR), ('mi', MI)], '상', 'G1', [3])
    return tpl_class(r, ("'-이/-음' 이외의 모음으로 시작된 접미사가 붙어 소리대로 적은 말", BOT), ('어간의 원형을 밝히어 적은 명사', P1), 'bad', '상', 'K2', [3])

@T('hl067')
def g067(r, k):
    c = r.randrange(9)
    if c == 0:
        return tpl_choose(r, MI + MX, 'ok', None, '중', 'A1', ref=[3])
    if c == 1:
        return tpl_choose(r, HY + HN, 'ok', None, '중', 'A2', ref=[3])
    if c == 2:
        return tpl_choose(r, BY + BB + BN, 'ok', None, '중', 'A3', ref=[3])
    if c == 3:
        return tpl_choose(r, MI + HY + BY, 'bad', None, '중', 'B1', ref=[3])
    if c == 4:
        return tpl_choose(r, HY + HN, 'ok', 'hageri', '상', 'D1', ref=[3])
    if c == 5:
        return tpl_choose(r, BY + BB + BN, 'bad', 'busa', '상', 'D2', ref=[3])
    if c == 6:
        rules = [("명사 뒤에 '-이'가 붙어서 된 말은 그 명사의 원형을 밝히어 적는다.", MI, '원형을 밝히어 적은 것이다'), ("'-하다'나 '-거리다'가 붙는 어근에 '-이'가 붙어 명사가 된 것은 그 어근의 원형을 밝히어 적는다.", HY, '어근의 원형을 밝히어 적은 것이다'), ("'-하다'나 '-거리다'가 붙을 수 없는 어근에 접미사가 붙어 명사가 된 것은 원형을 밝히어 적지 않는다.", HN, '소리대로 적은 것이다'), ("명사 뒤에 '-이' 이외의 모음으로 시작된 접미사가 붙은 말은 명사의 원형을 밝히어 적지 않는다.", MX, '소리대로 적은 것이다')]
        return tpl_label(r, rules, '최', 'R1', [3], mode=r.choice(['bad', 'ok']))
    if c == 7:
        rules = [("'-하다'가 붙는 어근에 '-히'나 '-이'가 붙어 부사가 된 것은 어근의 원형을 밝히어 적는다.", BY, '어근의 원형을 밝히어 적은 것이다'), ("부사에 '-이'가 붙어 역시 부사가 된 것은 그 부사의 원형을 밝히어 적는다.", BB, '부사의 원형을 밝히어 적은 것이다'), ("'-하다'가 붙지 않는 어근에서 된 부사는 소리대로 적는다.", BN, '소리대로 적은 것이다')]
        return tpl_label(r, rules, '최', 'R2', [3], mode=r.choice(['bad', 'ok']))
    return tpl_same(r, [('mi', MI), ('mx', MX), ('hy', HY), ('hn', HN), ('by', BY), ('bb', BB)], '상', 'G1', [3])
FARS = [('할머니는 감기 끝에 __가 덧났다.', '목거리', '목걸이', "'목거리'는 목병을 뜻하며 어간의 뜻에서 멀어져 소리대로 적는다. '목걸이'는 목에 거는 장신구이다."), ('어머니는 생일에 금__를 선물로 받으셨다.', '목걸이', '목거리', "'목걸이'는 목에 거는 물건으로 '걸다'의 뜻이 살아 있어 원형을 밝혀 적는다."), ('그는 __에 빠져 재산을 모두 날렸다.', '노름', '놀음', "'노름'은 도박을 뜻하며 '놀다'의 뜻에서 멀어져 소리대로 적는다."), ('아이들은 즐거운 __에 시간 가는 줄 몰랐다.', '놀음', '노름', "'놀음'은 '놀이'의 뜻으로 '놀다'의 뜻이 살아 있어 원형을 밝혀 적는다."), ('봄이 되자 밭에 __을 뿌렸다.', '거름', '걸음', "'거름'은 식물의 양분이 되는 물질로 '걸다'의 뜻에서 멀어져 소리대로 적는다."), ('그는 급한 __으로 길을 나섰다.', '걸음', '거름', "'걸음'은 걷는 동작으로 '걷다'의 뜻이 살아 있어 원형을 밝혀 적는다."), ('상처에서 __이 나온다.', '고름', '곯음', "'고름'은 곪아서 생긴 액체로 어간의 뜻에서 멀어져 소리대로 적는다."), ('고개 __로 산책을 갔다.', '너머', '넘어', "'너머'는 '넘다'에서 뜻이 멀어진 명사로 소리대로 적는다. '넘어'는 동사 '넘다'의 활용형이다."), ('고개를 __ 마을로 갔다.', '넘어', '너머', "'넘어'는 동사 '넘다'의 활용형이므로 원형을 밝혀 적는다."), ('그 __ 마을에는 사람이 없다.', '너머', '넘어', "'너머'는 어떤 공간의 저쪽을 뜻하는 명사이다."), ('그것은 __가 아니라 도리이다.', '이치', '이치', '')]
FARS = [x for x in FARS if x[3] and x[1] != x[2]]

@T('hl068')
def g068(r, k):
    c = r.randrange(7)
    if c == 0:
        return tpl_class(r, ('어간의 뜻에서 멀어져 소리대로 적는 말', BOT + FAR), ('어간의 원형을 밝히어 적는 말', NI + NE + MI), 'ok', '중', 'K1', [3])
    if c == 1:
        return tpl_class(r, ('소리대로 적는 말', BOT + FAR + MX + HN), ('원형을 밝히어 적는 말', NI + NE + MI + HY), 'bad', '중', 'K2', [3])
    if c == 2:
        rows = [dict(s=s, ok=ok, bad=[bd], why=w) for s, ok, bd, w in FARS]
        return tpl_sent5(r, rows, r.choice(['ok', 'bad']), '상', 'S', [3], ask='밑줄 친 말이 문맥에 맞게 쓰인 것은?') if len(rows) >= 5 else None
    if c == 3:
        rows = [dict(s=s, ok=ok, bad=[bd], why=w) for s, ok, bd, w in FARS]
        a = r.choice(rows)
        right = a['s'].replace('__', '<u>%s</u>' % a['ok'])
        wr = [a['s'].replace('__', '<u>%s</u>' % a['bad'][0])]
        return None if len(rows) < 5 else tpl_circled(r, sent_items(rows), 'bad', '상', 'L', [3], ask='㉠~㉤ 중 문맥에 맞지 않게 쓰인 것은?')
    if c == 4:
        return tpl_tf(r, kb_tf.ORTH_CONCEPT, 'ok', lv='하', fam='T', ref=[3])
    if c == 5:
        return tpl_choose(r, BOT + MX, 'bad', 'botim', '상', 'D', ref=[3])
    return tpl_class(r, ('소리대로 적는 말', BOT + FAR), ('원형을 밝히어 적는 말', NI + NE), 'ok', '하', 'K3', [3])

@T('hl069')
def g069(r, k):
    P1 = GP + GX + TO
    c = r.randrange(8)
    if c == 0:
        return tpl_choose(r, GP, 'ok', None, '하', 'A1', ref=[4])
    if c == 1:
        return tpl_choose(r, GX + TO, 'ok', None, '중', 'A2', ref=[4])
    if c == 2:
        return tpl_choose(r, P1, 'bad', None, '중', 'B1', ref=[4])
    if c == 3:
        return tpl_choose(r, P1, 'ok', 'gap', '상', 'D1', ref=[4])
    if c == 4:
        return tpl_stmt3(r, P1, 'gap', '상', 'C1', [4])
    if c == 5:
        return tpl_same(r, [('gp', GP), ('gx', GX), ('tooth', TO), ('mx', MX), ('bot', BOT), ('sai', SAI)], '상', 'G1', [4])
    if c == 6:
        return tpl_class(r, ('합성어·접두사 파생어로서 각각의 원형을 밝히어 적은 말', GP + TO), ('원형을 밝히지 않고 소리 나는 대로(변한 대로) 적은 말', GX + BOT[:6]), r.choice(['ok', 'bad']), '상', 'K1', [4])
    return tpl_choose(r, GP + GX + TO + MX, 'bad', 'gap', '최', 'D2', ref=[4])

@T('hl070')
def g070(r, k):
    c = r.randrange(9)
    SA = SAI + SAIN
    if c == 0:
        return tpl_choose(r, SAI, 'ok', None, '하', 'A1', ref=[4])
    if c == 1:
        return tpl_choose(r, SAIN, 'ok', None, '중', 'A2', ref=[4])
    if c == 2:
        return tpl_choose(r, SA, 'bad', None, '중', 'B1', ref=[4])
    if c == 3:
        return tpl_choose(r, SA, 'ok', 'sai', '상', 'D1', ref=[4])
    if c == 4:
        return tpl_stmt3(r, SA, 'sai', '상', 'C1', [4])
    if c == 5:
        return tpl_class(r, ('사이시옷을 받쳐 적는 말', SAI), ('사이시옷을 받쳐 적지 않는 말', SAIN), r.choice(['ok', 'bad']), '중', 'K1', [4])
    if c == 6:
        hz = [e for e in SAI if '예외' in e.why or '한자어' in e.why]
        return tpl_choose(r, SAIN, 'bad', 'sai', '최', 'D2', ref=[4])
    if c == 7:
        t1 = [e for e, d in zip(SAI, K3.SAI_Y) if d['typ'] == '된']
        t2 = [e for e, d in zip(SAI, K3.SAI_Y) if d['typ'] == 'ㄴ']
        t3 = [e for e, d in zip(SAI, K3.SAI_Y) if d['typ'] == 'ㄴㄴ']
        groups = [('된소리', t1), ('ㄴ덧남', t2), ('ㄴㄴ덧남', t3), ('p', PAL), ('g', GP), ('s', SAIN)]
        gi = r.randrange(3)
        a = r.choice(groups[gi][1])
        mine = [e for e in groups[gi][1] if e is not a]
        if not mine:
            return None
        b = r.choice(mine)
        ws = [r.choice(groups[x][1]) for x in range(3) if x != gi]
        ws2 = [r.choice(SAIN), r.choice(SAIN)]
        ws = [w for w in ws] + ws2
        names = {0: '뒷말의 첫소리가 된소리로 나는', 1: "뒷말의 첫소리 'ㄴ, ㅁ' 앞에서 'ㄴ' 소리가 덧나는", 2: "뒷말의 첫소리 모음 앞에서 'ㄴㄴ' 소리가 덧나는"}
        body = P('다음 중 %s 경우로 사이시옷을 받쳐 적은 말은?' % names[gi])
        wrongs = [w.ok for w in ws[:2]] + [x.ok for x in ws2]
        return mc(body, b.ok, wrongs, steps=["'%s': %s" % (b.ok, b.why)] + ["'%s'은(는) 다른 경우이다." % w for w in wrongs], core=b.why, lv='상', fam='G', r=r, ref=[4])
    return tpl_choose(r, SAI + SAIN, 'ok', 'sai', '최', 'D3', ref=[4])

@T('hl071')
def g071(r, k):
    c = r.randrange(8)
    J = K3.JUN
    if c <= 1:
        d = r.choice(J)
        others = [x for x in J if x['short'] != d['short']]
        ws = r.sample(others, 4)
        body = P("'%s'의 준말로 옳은 것은?" % d['full'])
        return mc(body, d['short'], [w['short'] for w in ws], steps=["'%s'의 준말은 '%s'이다(%s). %s" % (d['full'], d['short'], d['art'], d['why'])], core=d['why'], lv='중', fam='A', r=r, ref=[5])
    if c == 2:
        d = r.choice(J)
        others = [x for x in J if x['short'] != d['short']]
        ws = r.sample(others, 4)
        body = P("'%s'(으)로 줄여 쓴 본말로 옳은 것은?" % d['short'])
        return mc(body, d['full'], [w['full'] for w in ws], steps=["'%s'은(는) '%s'의 준말이다(%s). %s" % (d['short'], d['full'], d['art'], d['why'])], core=d['why'], lv='중', fam='B', r=r, ref=[5])
    if c == 3:
        xs = r.sample(J, 5)
        k2 = r.randrange(5)
        items = []
        st = []
        for i, d in enumerate(xs):
            if i == k2:
                alt = r.choice([x for x in J if x['short'] != d['short'] and x['art'] != d['art']])
                items.append(("'%s'의 준말은 '%s'이다." % (d['full'], alt['short']), True))
                st.append("'%s'의 준말은 '%s'이지 '%s'이(가) 아니다. %s" % (d['full'], d['short'], alt['short'], d['why']))
            else:
                items.append(("'%s'의 준말은 '%s'이다." % (d['full'], d['short']), False))
                st.append("'%s'→'%s'는 옳다(%s)." % (d['full'], d['short'], d['art']))
        return mcs(P('본말과 준말의 연결이 옳지 않은 것은?'), items, steps=st, core=xs[k2]['why'], lv='중', fam='C', r=r, ref=[5], vertical=True)
    if c == 4:
        return tpl_jun(r, J, '상', 'J1', [5], mode=r.choice(['bad', 'ok']))
    if c == 5:
        rows = [dict(s=d['s'], ok=d['ok'], bad=d['bad'], why=d['why']) for d in K3.DOE]
        return tpl_sent5(r, rows, r.choice(['ok', 'bad']), '상', 'S', [5], ask=r.choice(['밑줄 친 부분의 표기가 옳은 것은?', '다음 중 맞춤법에 맞게 쓴 문장은?'])) if len(rows) >= 5 else tpl_jun(r, J, '상', 'J2', [5])
    if c == 6:
        rows = [dict(s=d['s'], ok=d['ok'], bad=d['bad'], why=d['why']) for d in K3.DOE]
        return tpl_circled(r, sent_items(rows), 'bad', '상', 'L', [5]) if len(sent_items(rows)) >= 5 else tpl_jun(r, J, '상', 'J3', [5])
    return tpl_tf(r, kb_tf.ORTH_CONCEPT, 'ok', lv='하', fam='T', ref=[5])

def _dw(block):
    out = []
    for ln in block.strip().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        w, parts, pron, st, cell = [x.strip() for x in ln.split('|')]
        out.append(dict(w=w, parts=parts, pron=pron, st=st, cell=cell))
    return out
DW = _dw('\n이파리|잎+아리|[이파리]|파생|A\n지붕|집+웅|[지붕]|파생|A\n마중|맞+웅|[마중]|파생|A\n무덤|묻+엄|[무덤]|파생|A\n마개|막+애|[마개]|파생|A\n바가지|박+아지|[바가지]|파생|A\n쓰레기|쓸+에기|[쓰레기]|파생|A\n올가미|옭+아미|[올가미]|파생|A\n따님|딸+님|[따님]|파생|A\n아드님|아들+님|[아드님]|파생|A\n바느질|바늘+질|[바느질]|파생|A\n하느님|하늘+님|[하느님]|파생|A\n얼음|얼-+-음|[어름]|파생|B\n웃음|웃-+-음|[우슴]|파생|B\n믿음|믿-+-음|[미듬]|파생|B\n깊이|깊-+-이|[기피]|파생|B\n먹이|먹-+-이|[머기]|파생|B\n높이|높-+-이|[노피]|파생|B\n걸음|걷-+-음|[거름]|파생|B\n죽음|죽-+-음|[주금]|파생|B\n넓이|넓-+-이|[널비]|파생|B\n덧신|덧-+신|[덛씬]|파생|B\n엿듣다|엿-+듣-|[엳뜯따]|파생|B\n짓밟다|짓-+밟-|[짇빱따]|파생|B\n풋사랑|풋-+사랑|[푿싸랑]|파생|B\n헛웃음|헛-+웃음|[허두슴]|파생|B\n꿈|꾸-+-ㅁ|[꿈]|파생|AB\n춤|추-+-ㅁ|[춤]|파생|AB\n지우개|지우-+-개|[지우개]|파생|AB\n날개|날-+-개|[날개]|파생|AB\n가리개|가리-+-개|[가리개]|파생|AB\n맨손|맨-+손|[맨손]|파생|AB\n군말|군-+말|[군말]|파생|AB\n맨발|맨-+발|[맨발]|파생|AB\n개살구|개-+살구|[개살구]|파생|AB\n마소|말+소|[마소]|합성|A\n소나무|솔+나무|[소나무]|합성|A\n부삽|불+삽|[부삽]|합성|A\n화살|활+살|[화살]|합성|A\n싸전|쌀+전|[싸전]|합성|A\n무논|물+논|[무논]|합성|A\n밥알|밥+알|[바발]|합성|B\n옷소매|옷+소매|[옫쏘매]|합성|B\n꽃잎|꽃+잎|[꼰닙]|합성|B\n낮잠|낮+잠|[낟짬]|합성|B\n칼날|칼+날|[칼랄]|합성|B\n앞문|앞+문|[암문]|합성|B\n밭일|밭+일|[반닐]|합성|B\n부엌일|부엌+일|[부엉닐]|합성|B\n국물|국+물|[궁물]|합성|B\n닭장|닭+장|[닥짱]|합성|B\n물난리|물+난리|[물랄리]|합성|B\n밑천|밑+천|[믿천]|합성|B\n끝장|끝+장|[끋짱]|합성|B\n눈물|눈+물|[눈물]|합성|AB\n손목|손+목|[손목]|합성|AB\n봄비|봄+비|[봄비]|합성|AB\n가을비|가을+비|[가을비]|합성|AB\n강물|강+물|[강물]|합성|AB\n손수건|손+수건|[손수건]|합성|AB\n물고기|물+고기|[물고기]|합성|AB\n')
DWW = {'A': 'ⓐ만 충족(소리대로 적었으나 원형은 밝히지 않음)', 'B': 'ⓑ만 충족(원형은 밝혀 적었으나 표기가 소리와 다름)', 'AB': 'ⓐ·ⓑ를 모두 충족(소리와 표기가 같고 원형도 밝힘)'}

def _dwwhy(d):
    sound = {'A': '표기가 소리와 같지만 어근의 본모양을 밝히지 않았으므로', 'B': '어근의 본모양을 밝혀 적었으나 표기와 소리가 달라', 'AB': '표기가 소리와 같고 어근의 본모양도 밝혀 적었으므로'}[d['cell']]
    return "'%s'(%s, %s %s)은(는) %s %s이다." % (d['w'], d['parts'], d['st'] + '어', d['pron'], sound, DWW[d['cell']].split('(')[0])

@T('hl072')
def g072(r, k):
    c = r.randrange(7)
    if c <= 2:
        st = r.choice(['파생', '합성'])
        cell = r.choice(['A', 'B', 'AB'])
        pool = [d for d in DW if d['st'] == st and d['cell'] == cell]
        others = [d for d in DW if not (d['st'] == st and d['cell'] == cell)]
        if len(pool) < 2:
            return None
        pair = r.sample(pool, 2)
        wrongs = []
        for _ in range(4):
            a = r.choice(others)
            b = r.choice(pool if r.random() < 0.5 else others)
            wrongs.append('%s, %s' % (a['w'], b['w']) if r.random() < 0.5 else '%s, %s' % (b['w'], a['w']))
        right = '%s, %s' % (pair[0]['w'], pair[1]['w'])
        box = BOGI(['한글 맞춤법 제1항은 표준어를 ⓐ소리대로 적되, ⓑ어법에 맞도록 함을 원칙으로 한다.', 'ⓐ만 충족: 표기가 소리와 같지만 어근·접사의 본모양을 밝히지 않은 경우', 'ⓑ만 충족: 본모양을 밝혀 적었으나 표기가 소리와 다른 경우', 'ⓐ, ⓑ 모두 충족: 표기가 소리와 같고 본모양도 밝혀 적은 경우'], title='보 기', labels=None)
        body = P('다음 표의 빈칸에 들어갈 예로 적절한 것은? (%s어 − %s)' % (st, DWW[cell].split('(')[0])) + box
        pron = r.sample(pool, 0)
        steps = [_dwwhy(pair[0]), _dwwhy(pair[1])] + ["'%s' 등 나머지 쌍은 이 칸에 해당하지 않는 말이 섞여 있다." % wrongs[0]]
        return mc(body, right, wrongs, steps=steps, core='파생어·합성어를 ⓐ·ⓑ 기준으로 분류한다.', lv='최' if c == 2 else '상', fam='T', r=r, ref=[1])
    if c == 3:
        return tpl_class(r, ('소리대로 적은(원형을 밝히지 않은) 말', SORI), ('어법에 맞도록 원형을 밝히어 적은 말', OBEOP), 'bad', '상', 'K1', [1])
    if c == 4:
        xs = r.sample(DW, 3)
        stm = []
        for d in xs:
            truth = r.random() < 0.5
            cell = d['cell'] if truth else r.choice([x for x in 'A B AB'.split() if x != d['cell']])
            stm.append(("'%s'은(는) %s이다." % (d['w'], DWW[cell].split('(')[0]), truth, _dwwhy(d)))
        return bogi('한글 맞춤법 제1항(ⓐ소리대로, ⓑ어법에 맞도록)에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='U', r=r, ref=[1], ask='')
    if c == 5:
        cell = r.choice(['A', 'B', 'AB'])
        st = r.choice(['파생', '합성'])
        pool = [d for d in DW if d['cell'] == cell and d['st'] == st]
        if len(pool) < 1:
            return None
        right = r.choice(pool)
        ws = r.sample([d for d in DW if d['cell'] != cell], 4)
        body = P('다음 중 %s어이면서 %s에 해당하는 것은?' % (st, DWW[cell].split('(')[0]))
        return mc(body, right['w'], [w['w'] for w in ws], steps=[_dwwhy(right)] + [_dwwhy(w) for w in ws], core=_dwwhy(right), lv='상', fam='V', r=r, ref=[1])
    cell = r.choice(['A', 'B', 'AB'])
    pool = [d for d in DW if d['cell'] == cell]
    right = r.choice(pool)
    ws = r.sample([d for d in DW if d['cell'] != cell], 4)
    body = P('다음 중 %s에 해당하는 것은?' % DWW[cell].split('(')[0])
    return mc(body, right['w'], [w['w'] for w in ws], steps=[_dwwhy(right)] + [_dwwhy(w) for w in ws], core=_dwwhy(right), lv='중', fam='W', r=r, ref=[1])
