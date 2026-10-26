"""Ⅲ-C 띄어쓰기와 구별하여 적는 말 (hl073~hl082)"""
from hllib import *
from orth_gen import *
import kb_orth2 as K2, kb_orth3 as K3, kb_orth4 as K4, kb_tf
SP = {}
for d in K4.SPACE:
    SP.setdefault(d['key'], []).append(d)

def _depk(block):
    out = []
    for ln in block.strip().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        a = [x.strip() for x in ln.split('|')]
        out.append(dict(s=a[0], kind=a[1], why=a[2]))
    return out
DEPK = _depk("\n그것은 너<u>뿐</u>이다.|조사|체언 뒤에서 '한정'의 뜻을 나타내는 조사이다.\n그는 웃을 <u>뿐</u>이다.|의존 명사|용언의 관형사형 뒤에서 수식을 받는 의존 명사이다.\n법<u>대로</u> 처리하겠다.|조사|체언 뒤에서 '그와 같이'의 뜻을 나타내는 조사이다.\n아는 <u>대로</u> 말해라.|의존 명사|용언의 관형사형 뒤에서 수식을 받는 의존 명사이다.\n키가 전봇대<u>만큼</u> 크다.|조사|체언 뒤에서 '앞말과 비슷한 정도'의 뜻을 나타내는 조사이다.\n애쓴 <u>만큼</u> 얻는다.|의존 명사|용언의 관형사형 뒤에서 수식을 받는 의존 명사이다.\n하나<u>만</u> 알고 둘은 모른다.|조사|체언 뒤에서 한정의 뜻을 나타내는 조사이다.\n떠난 지 사흘 <u>만</u>에 돌아왔다.|의존 명사|시간의 경과를 나타내는 의존 명사이다.\n집이 큰<u>지</u> 작은<u>지</u> 모르겠다.|어미|'-(으)ㄴ지'의 일부인 연결 어미이다.\n그가 떠난 <u>지</u> 보름이 지났다.|의존 명사|시간의 경과를 나타내는 의존 명사이다.\n<u>사업차</u> 외국에 나갔다.|접미사|명사 뒤에서 '목적'의 뜻을 더하는 접미사이다.\n마침 가려던 <u>차</u>였다.|의존 명사|용언의 관형사형 뒤에서 수식을 받는 의존 명사이다.\n남자<u>들</u>이 모였다.|접미사|복수를 나타내는 접미사이다.\n쌀, 보리, 콩, 조, 기장 <u>들</u>은 오곡이다.|의존 명사|열거하는 말 뒤에서 '그런 따위'의 뜻을 나타내는 의존 명사이다.\n먹을 <u>것</u>이 없다.|의존 명사|용언의 관형사형 뒤에 놓여 수식을 받는 의존 명사이다.\n너<u>만큼</u> 나도 할 수 있다.|조사|체언 뒤에서 '앞말과 비슷한 정도'를 나타내는 조사이다.\n시험이 어렵<u>더라도</u> 포기하지 마라.|어미|연결 어미 '-더라도'의 일부이다.\n이것<u>밖에</u> 없다.|조사|체언 뒤에서 '그것 말고는'의 뜻을 나타내는 조사이다.\n집이 크<u>든지</u> 작<u>든지</u> 상관없다.|어미|선택을 나타내는 어미이다.\n네가 뜻한 <u>바</u>를 알겠다.|의존 명사|용언의 관형사형 뒤에 놓여 수식을 받는 의존 명사이다.\n어디<u>까지</u>나 네 사정이다.|조사|체언 뒤에서 도달점을 나타내는 조사이다.\n나도 할 <u>수</u> 있다.|의존 명사|용언의 관형사형 뒤에서 수식을 받는 의존 명사이다.\n")
DEPW = {'조사': '체언 뒤에 붙는 조사', '의존 명사': '관형어의 꾸밈을 받아 쓰이는 의존 명사', '어미': '용언 어간에 붙는 어미의 일부', '접미사': '명사 뒤에 붙는 접미사'}

def tpl_dep(r, lv='중', fam='D', ref=None):
    kind = r.choice(['조사', '의존 명사'])
    pool = [d for d in DEPK if d['kind'] == kind]
    others = [d for d in DEPK if d['kind'] != kind]
    if len(pool) < 1 or len(others) < 4:
        return None
    a = r.choice(pool)
    ws = r.sample(others, 4)
    ask = '밑줄 친 말이 %s인 것은?' % ('조사' if kind == '조사' else '의존 명사')
    st = ['"%s": %s' % (plain(a['s']), a['why'])] + ['"%s": %s' % (plain(w['s']), w['why']) for w in ws]
    return mc(P(ask), a['s'], [w['s'] for w in ws], steps=st, core=a['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)

def tpl_dep_pair(r, ref=None):
    """같은 형태가 다른 쓰임: 짝이 되는 두 문장 중 띄어쓰기 설명이 옳은 것"""
    forms = ['뿐', '대로', '만큼', '만', '지', '차']
    f = r.choice(forms)
    ds = [d for d in DEPK if '<u>%s</u>' % f in d['s'] or '<u>%s</u>' % f in d['s'].replace('사업차', '차')]
    if len(ds) < 2:
        return None
    a = [d for d in DEPK if ('>' + f + '<' in d['s'] or d['s'].count('<u>' + f)) and d['kind'] == '의존 명사']
    b = [d for d in DEPK if ('>' + f + '<' in d['s'] or d['s'].count('<u>' + f)) and d['kind'] != '의존 명사']
    if not a or not b:
        return None
    x = r.choice(a)
    y = r.choice(b)
    right = "'%s'은(는) 의존 명사이므로 띄어 쓰고, '%s'은(는) %s이므로 붙여 쓴다." % (f, f, '조사' if y['kind'] == '조사' else y['kind'] + '의 일부')
    wrongs = ["'%s'은(는) 두 문장에서 모두 의존 명사이므로 띄어 쓴다." % f, "'%s'은(는) 두 문장에서 모두 조사이므로 붙여 쓴다." % f, "'%s'은(는) 의존 명사이므로 두 문장 모두 붙여 쓴다." % f, "'%s'은(는) 앞말에 따라 항상 붙여 쓰는 것이 허용된다." % f]
    body = P("다음 두 문장의 밑줄 친 '%s'의 띄어쓰기에 대한 설명으로 옳은 것은?" % f) + BOX(['㉠ ' + x['s'], '㉡ ' + y['s']])
    right = "㉠의 '%s'은(는) 의존 명사이므로 띄어 쓰고, ㉡의 '%s'은(는) %s이므로 붙여 쓴다." % (f, f, {'조사': '조사', '어미': '어미의 일부', '접미사': '접미사'}[y['kind']])
    wrongs = ["㉠과 ㉡의 '%s'은(는) 모두 의존 명사이므로 띄어 쓴다." % f, "㉠과 ㉡의 '%s'은(는) 모두 조사이므로 붙여 쓴다." % f, "㉠의 '%s'은(는) 조사이므로 붙여 쓰고, ㉡의 '%s'은(는) 의존 명사이므로 띄어 쓴다." % (f, f), "㉠과 ㉡의 '%s'은(는) 모두 앞말에 붙여 쓰는 것이 원칙이다." % f]
    return mc(body, right, wrongs, steps=['㉠ %s' % x['why'], '㉡ %s' % y['why']], core=x['why'], lv='상', fam='E', r=r, ref=ref, vertical=True)

@T('hl073')
def g073(r, k):
    rows = SP['josa'] + [dict(ok=d['ok'], bad=d['bad'], why=d['why']) for d in SP['dep'][:0]]
    c = r.randrange(6)
    if c == 0:
        return tpl_space5(r, rows, 'ok', '하', 'A', [1])
    if c == 1:
        return tpl_space5(r, rows, 'bad', '하', 'B', [1])
    if c == 2:
        return tpl_space_circ(r, rows, '중', 'Q', [1])
    if c == 3:
        return tpl_space5(r, rows + SP['dep'], 'ok', '중', 'C', [1])
    if c == 4:
        return tpl_dep(r, '중', 'D', [1])
    return tpl_tf(r, kb_tf.ORTH_CONCEPT, 'ok', lv='중', fam='T', ref=[1])

@T('hl074')
def g074(r, k):
    rows = SP['dep']
    c = r.randrange(7)
    if c == 0:
        return tpl_space5(r, rows, 'ok', '하', 'A', [1])
    if c == 1:
        return tpl_space5(r, rows, 'bad', '중', 'B', [1])
    if c == 2:
        return tpl_space_circ(r, rows + SP['josa'], '상', 'Q', [1])
    if c == 3:
        return tpl_dep(r, '중', 'D', [1])
    if c == 4:
        return tpl_dep(r, '상', 'D2', [1])
    if c == 5:
        return tpl_dep_pair(r, [1]) or tpl_dep(r, '상', 'D3', [1])
    return tpl_space5(r, rows + SP['josa'], 'bad', '상', 'C', [1])

@T('hl075')
def g075(r, k):
    rows = SP['unit']
    c = r.randrange(4)
    if c == 0:
        return tpl_space5(r, rows, 'ok', '하', 'A', [1])
    if c == 1:
        return tpl_space5(r, rows, 'bad', '중', 'B', [1])
    if c == 2:
        return tpl_space_circ(r, rows, '상', 'Q', [1])
    return tpl_space5(r, rows + SP['dep'], 'bad', '중', 'C', [1])
BJ = K4.BOJO

def _valid_forms(d):
    return [d['w']] + ([d['allow']] if d['allow'] else [])

def tpl_bojo(r, mode='ok', kinds=None, lv='상', fam='E', ref=None):
    valid = BJ
    invalid = [d for d in BJ if d['bad'] and d['kind'] != 'basic' or (d['bad'] and d['kind'] == 'basic')]
    if mode == 'ok':
        a = r.choice(BJ)
        right = r.choice(_valid_forms(a))
        ws = r.sample(invalid, 4)
        wrongs = [r.choice(w['bad']) for w in ws]
        if right in wrongs:
            return None
        st = ['옳은 것: "%s" %s' % (right, a['why'])] + ['"%s"은(는) 틀렸다 → "%s". %s' % (b, w['w'], w['why']) for b, w in zip(wrongs, ws)]
        return mc(P(r.choice(['보조 용언의 띄어쓰기가 옳은 것은?', '다음 중 띄어쓰기가 옳은 문장은?'])), right, wrongs, steps=st, core=a['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)
    else:
        a = r.choice(invalid)
        b = r.choice(a['bad'])
        ws = [r.choice(_valid_forms(x)) for x in r.sample(BJ, 4)]
        if b in ws:
            return None
        st = ['틀린 것: "%s" → "%s". %s' % (b, a['w'], a['why'])]
        return mc(P(r.choice(['보조 용언의 띄어쓰기가 옳지 않은 것은?', '다음 중 띄어쓰기가 틀린 문장은?'])), b, ws, steps=st + ['나머지는 원칙 또는 허용 규정에 맞게 쓴 문장이다.'], core=a['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)
KINDS_WHY = {'derived': '본용언이 파생어(-하다 파생 등)이다', 'compound': '본용언이 합성 용언이다', 'josa': '본용언이나 보조 용언 앞뒤에 조사가 들어간다', 'ending': "본용언의 어미가 '-ㄴ가, -나, -ㄹ까, -지' 등의 종결 어미이다"}

def tpl_bojo_why(r, lv='상', fam='W', ref=None):
    cand = [d for d in BJ if d['kind'] in KINDS_WHY]
    a = r.choice(cand)
    right = '%s' % KINDS_WHY[a['kind']] + '(이)므로 보조 용언은 본용언과 띄어 써야 한다.'
    right = right.replace('(이)므로', '므로') if KINDS_WHY[a['kind']].endswith('다') else right
    right = '%s. 그러므로 보조 용언은 띄어 써야 한다.' % KINDS_WHY[a['kind']]
    ws = ['%s. 그러므로 보조 용언은 띄어 써야 한다.' % v for kk, v in KINDS_WHY.items() if kk != a['kind']]
    ws.append('보조 용언은 어떤 경우에도 붙여 쓸 수 없다. 그러므로 보조 용언은 띄어 써야 한다.')
    ws.append('본용언과 보조 용언이 모두 한 음절이다. 그러므로 보조 용언은 띄어 써야 한다.')
    ws = r.sample(ws, 4)
    body = P("'%s'에서 보조 용언을 본용언과 붙여 쓰지 않고 띄어 쓰는 이유로 가장 적절한 것은?" % a['w'].rstrip('.'))
    return mc(body, right, ws, steps=[a['why']], core=a['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)

@T('hl076')
def g076(r, k):
    c = r.randrange(7)
    if c == 0:
        return tpl_bojo(r, 'ok', None, '중', 'A', [2])
    if c == 1:
        return tpl_bojo(r, 'bad', None, '중', 'B', [2])
    if c == 2:
        return tpl_bojo(r, 'ok', None, '상', 'C', [2])
    if c == 3:
        return tpl_bojo_why(r, '상', 'W', [2])
    if c == 4:
        rows = [dict(ok=d['w'], bad=d['bad'], why=d['why']) for d in BJ if d['bad']]
        return tpl_space_circ(r, rows, '상', 'Q', [2], ask='㉠~㉤ 중 보조 용언의 띄어쓰기가 옳지 않은 것은?')
    if c == 5:
        a = r.choice([d for d in BJ if d['allow']])
        right = "'%s'과(와) '%s' 모두 허용된다." % (a['w'].rstrip('.'), a['allow'].rstrip('.'))
        b = r.choice([d for d in BJ if d['kind'] in ('derived', 'compound')])
        body = P('한글 맞춤법 제47항에 대한 설명으로 옳은 것은?')
        ws = ['본용언이 합성 용언이어도 보조 용언은 항상 붙여 쓸 수 있다.', '보조 용언은 항상 본용언과 붙여 쓰는 것이 원칙이다.', "'-아/-어 지다'는 본용언과 띄어 쓰는 것이 원칙이다.", '중간에 조사가 들어가도 보조 용언은 붙여 쓸 수 있다.']
        r_ = '보조 용언은 띄어 씀을 원칙으로 하되 경우에 따라 붙여 씀도 허용한다.'
        return mc(body, r_, ws, steps=['제47항: 보조 용언은 띄어 씀을 원칙으로 하되 경우에 따라 붙여 씀도 허용한다. 다만 앞말에 조사가 붙거나 앞말이 합성 동사이거나 중간에 조사가 들어갈 때에는 띄어 쓴다.'], core='제47항', lv='중', fam='F', r=r, ref=[2], vertical=True)
    return tpl_bojo(r, 'bad', None, '상', 'D', [2])

@T('hl077')
def g077(r, k):
    PNL = K4.PN
    c = r.randrange(5)
    rows = [dict(ok=d['ok'], bad=d['bad'], why=d['why']) for d in PNL]
    if c == 0:
        return tpl_space5(r, rows, 'ok', '중', 'A', [2], ask='띄어쓰기가 옳은 것은?')
    if c == 1:
        return tpl_space5(r, rows, 'bad', '중', 'B', [2])
    if c == 2:
        return tpl_space_circ(r, rows, '상', 'Q', [2])
    if c == 3:
        a = r.choice([d for d in PNL if d['allow']])
        right = "'%s'과(와) '%s' 모두 허용된다." % (a['ok'], a['allow'])
        wrongs = ["'%s'만 허용된다." % a['ok'], "'%s'만 허용된다." % a['allow'], '둘 다 허용되지 않는다.', "'%s'을(를) 더 띄어 써야 한다." % a['ok']]
        return mc(P("다음 표기에 대한 설명으로 옳은 것은? ('%s')" % a['ok']), right, wrongs, steps=[a['why']], core=a['why'], lv='중', fam='C', r=r, ref=[2], vertical=True)
    return tpl_tf(r, kb_tf.ORTH_CONCEPT, 'ok', lv='중', fam='T', ref=[2])

@T('hl078')
def g078(r, k):
    I1 = ents(K2.IHI_I, 'i')
    H1 = ents(K2.IHI_H, 'h')
    BB1 = ents(K2.BUSA_B, 'bb')
    BY1 = ents(K2.BUSA_Y, 'by')
    from types_orth_a import BN, BY, BB
    c = r.randrange(8)
    P1 = I1 + H1
    if c == 0:
        return tpl_choose(r, I1, 'ok', None, '하', 'A1', ref=[3])
    if c == 1:
        return tpl_choose(r, H1, 'ok', None, '하', 'A2', ref=[3])
    if c == 2:
        return tpl_choose(r, P1, 'bad', None, '중', 'B1', ref=[3])
    if c == 3:
        return tpl_choose(r, P1, 'ok', 'ihi', '중', 'D1', ref=[3])
    if c == 4:
        return tpl_stmt3(r, P1, 'ihi', '상', 'C1', [3])
    if c == 5:
        return tpl_class(r, ("부사의 끝음절을 '-이'로 적는 말", I1), ("부사의 끝음절을 '-히'로 적는 말", H1), r.choice(['ok', 'bad']), '중', 'K1', [3])
    if c == 6:
        return tpl_choose(r, P1 + BY + BB, 'bad', 'ihi', '상', 'D2', ref=[3])
    return tpl_same(r, [('i', I1), ('h', H1), ('bn', BN), ('bb', BB), ('far', ents(K2.FAR, 'far'))], '상', 'G1', [3])

@T('hl079')
def g079(r, k):
    rows = K4.EOMI2
    c = r.randrange(6)
    if c <= 1:
        return tpl_sent5(r, rows, 'ok', '중', 'S1', [3], ask=r.choice(['밑줄 친 부분의 표기가 옳은 것은?', '다음 중 맞춤법에 맞게 쓴 문장은?']))
    if c == 2:
        return tpl_sent5(r, rows, 'bad', '중', 'S2', [3])
    if c == 3:
        return tpl_circled(r, sent_items(rows), 'bad', '상', 'L', [3])
    if c == 4:
        return tpl_circled(r, sent_items(rows), 'ok', '상', 'L2', [3])
    return tpl_tf(r, kb_tf.ORTH_CONCEPT, 'ok', lv='중', fam='T', ref=[3])

@T('hl080')
def g080(r, k):
    rows = K4.GUBUN
    c = r.randrange(7)
    if c <= 1:
        return tpl_sent5(r, rows, 'ok', '중', 'S1', [4])
    if c == 2:
        return tpl_sent5(r, rows, 'bad', '중', 'S2', [4])
    if c == 3:
        return tpl_circled(r, sent_items(rows), 'bad', '상', 'L1', [4])
    if c == 4:
        return tpl_circled(r, sent_items(rows), 'ok', '상', 'L2', [4])
    if c == 5:
        d = r.choice(rows)
        word_pairs = [(x['ok'], x['bad'][0]) for x in rows]
        a = r.choice(rows)
        right = "'%s'은(는) '%s'(으)로 쓰고, 뜻이 다른 말과 구별하여 적는다." % (a['ok'], a['ok'])
        return tpl_sent5(r, rows, 'ok', '상', 'S3', [4])
    return tpl_circled(r, sent_items(rows + K4.COMMON), 'bad', '최', 'L3', [4])
MJ = _sent_rows = None
from kb_orth3 import _sent
MJ = _sent("\n정답을 __ 상품을 받았다.|맞혀|맞춰|'맞히다'는 문제에 대한 답을 틀리지 않게 한다는 뜻이다.\n문짝을 문틀에 __.|맞췄다|맞혔다|'맞추다'는 떨어져 있는 부분을 제자리에 맞게 붙인다는 뜻이다.\n행사 인원을 100명으로 __.|맞췄다|맞혔다|'맞추다'는 일정한 수량이 되게 한다는 뜻이다.\n그는 구두를 새로 __.|맞췄다|맞혔다|'맞추다'는 규격에 맞게 물건을 주문한다는 뜻이다.\n시험지를 정답과 __ 보았다.|맞춰|맞혀|'맞추다'는 둘 이상의 대상을 나란히 놓고 비교한다는 뜻이다.\n화살을 과녁에 정확히 __.|맞혔다|맞췄다|'맞히다'는 쏜 것이 목표에 닿게 한다는 뜻이다.\n의사가 아이에게 주사를 __.|맞혔다|맞췄다|'맞히다'는 치료를 받게 한다는 뜻의 사동사이다.\n화분에 비를 __ 마라.|맞히지|맞추지|'맞히다'는 비·눈이 닿게 한다는 뜻의 '맞다'의 사동사이다.\n아이는 엄마의 볼에 입을 __.|맞췄다|맞혔다|'맞추다'는 다른 대상에 닿게 한다는 뜻이다.\n시계를 5시에 __.|맞췄다|맞혔다|'맞추다'는 기준에 어긋나지 않게 조정한다는 뜻이다.\n약속 시간에 __ 도착했다.|맞춰|맞혀|'맞추다'는 약속 시간을 넘기지 않는다는 뜻이다.\n신에게 제물을 __.|바쳤다|받쳤다|'바치다'는 신이나 웃어른에게 정중하게 드린다는 뜻이다.\n국가에 세금을 __.|바쳤다|받쳤다|'바치다'는 반드시 내야 할 것을 가져다준다는 뜻이다.\n그는 평생을 연구에 몸을 __.|바쳤다|받쳤다|'바치다'는 모든 것을 아낌없이 내놓는다는 뜻이다.\n쟁반에 커피를 __ 걸어왔다.|받치고|바치고|'받치다'는 물건의 밑에 다른 물체를 댄다는 뜻이다.\n그는 우산을 __ 걸었다.|받치고|바치고|'받치다'는 우산·양산을 펴 든다는 뜻이다.\n양복 속에 두꺼운 내복을 __ 입었다.|받쳐|바쳐|'받치다'는 옷을 조화롭게 함께 입는다는 뜻이다.\n'가'에 'ㅁ'을 __ '감'이 된다.|받치면|바치면|'받치다'는 모음 글자 밑에 자음 글자를 붙여 적는다는 뜻이다.\n마을 이장이 소에게 __ 크게 다쳤다.|받혀|받쳐|'받히다'는 '받다'의 피동사로 세차게 부딪힌다는 뜻이다.\n승용차에 __ 병원에 실려 갔다.|받혀|받쳐|'받히다'는 '받다'의 피동사이다.\n삶은 국수를 체에 __.|밭쳤다|받쳤다|'밭치다'는 건더기를 건져 물기를 뺀다는 뜻이다.\n술을 체에 __.|밭쳤다|받쳤다|'밭치다'는 '밭다'를 강조한 말이다.\n친구에게 편지를 __.|부쳤다|붙였다|'부치다'는 편지·물건을 보낸다는 뜻이다.\n아들에게 학비를 __.|부쳤다|붙였다|'부치다'는 돈·물건을 보낸다는 뜻이다.\n어머니는 빈대떡을 __.|부치셨다|붙이셨다|'부치다'는 기름에 음식을 익혀 만든다는 뜻이다.\n안건을 회의에 __.|부쳤다|붙였다|'부치다'는 문제를 다른 기회에 넘겨 맡긴다는 뜻이다.\n그는 부채를 __.|부쳤다|붙였다|'부치다'는 부채를 흔들어 바람을 일으킨다는 뜻이다.\n이 일은 내 힘에 __.|부친다|붙인다|'부치다'는 모자라거나 미치지 못한다는 뜻이다.\n남의 땅을 __ 먹고 산다.|부쳐|붙여|'부치다'는 논밭을 이용해 농사짓는다는 뜻이다.\n봉투에 우표를 __.|붙였다|부쳤다|'붙이다'는 맞닿아 떨어지지 않게 한다는 뜻이다.\n연탄에 불을 __.|붙였다|부쳤다|'붙이다'는 불을 일으켜 타게 한다는 뜻이다.\n계약에 조건을 __.|붙였다|부쳤다|'붙이다'는 조건·이유를 딸리게 한다는 뜻이다.\n순우리말 이름을 상품에 __.|붙였다|부쳤다|'붙이다'는 이름이 생기게 한다는 뜻이다.\n공부에 흥미를 __.|붙였다|부쳤다|'붙이다'는 어떤 감정을 생기게 한다는 뜻이다.\n옆 사람에게 농담을 __.|붙였다|부쳤다|'붙이다'는 말을 걸거나 가까이 다가선다는 뜻이다.\n가구를 벽에 __.|붙였다|부쳤다|'붙이다'는 물체를 바짝 가깝게 한다는 뜻이다.\n두 사람의 싸움을 __.|붙였다|부쳤다|'붙이다'는 겨루는 일을 시작하게 한다는 뜻이다.\n")

@T('hl081')
def g081(r, k):
    c = r.randrange(6)
    if c <= 1:
        return tpl_sent5(r, MJ, 'ok', '중', 'S1', [4], ask=r.choice(['밑줄 친 부분이 문맥에 맞게 쓰인 것은?', '밑줄 친 말의 표기가 옳은 것은?']))
    if c == 2:
        return tpl_sent5(r, MJ, 'bad', '중', 'S2', [4], ask='밑줄 친 말이 문맥에 맞지 않게 쓰인 것은?')
    if c == 3:
        return tpl_circled(r, sent_items(MJ), 'bad', '상', 'L1', [4], ask='㉠~㉤ 중 밑줄 친 부분이 문맥에 맞지 않게 쓰인 것은?')
    if c == 4:
        return tpl_circled(r, sent_items(MJ), 'ok', '상', 'L2', [4], ask='㉠~㉤ 중 밑줄 친 부분이 문맥에 맞게 쓰인 것은?')
    a = r.choice(MJ)
    others = [x for x in MJ if x['ok'] != a['ok']]
    ws = r.sample(others, 4)
    body = P('다음 문장의 빈칸에 들어갈 말로 알맞은 것은?') + BOX([a['s'].replace('__', '(      )')])
    return mc(body, a['ok'], [a['bad'][0]] + [w['ok'] for w in ws[:3] if w['ok'] != a['bad'][0] and w['ok'] != a['ok']] + [w['bad'][0] for w in ws if w['bad'][0] not in (a['ok'], a['bad'][0])][:2], steps=[a['why']], core=a['why'], lv='중', fam='F', r=r, ref=[4])

@T('hl082')
def g082(r, k):
    allrows = K4.GUBUN + K4.COMMON + K4.EOMI2 + K3.DOE
    c = r.randrange(6)
    if c == 0:
        return tpl_sent5(r, allrows, 'ok', '중', 'S1', [4])
    if c == 1:
        return tpl_sent5(r, allrows, 'bad', '중', 'S2', [4])
    if c == 2:
        return tpl_circled(r, sent_items(allrows), 'bad', '상', 'L1', [4])
    if c == 3:
        return tpl_circled(r, sent_items(allrows), 'ok', '상', 'L2', [4])
    if c == 4:
        return tpl_circled(r, sent_items(K4.COMMON), 'bad', '상', 'L3', [4]) if len(sent_items(K4.COMMON)) >= 5 else tpl_sent5(r, allrows, 'bad', '상', 'S3', [4])
    return tpl_sent5(r, K4.COMMON, 'bad', '상', 'S4', [4])
