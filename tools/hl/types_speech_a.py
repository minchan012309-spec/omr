# -*- coding: utf-8 -*-
"""Ⅰ-A 화법의 기초와 발표 (hl001~hl007)"""
from hllib import *
from gram_gen import CIRC
from speech_gen import *
import kb_speech as S, kb_speech2 as S2
from orth_gen import tpl_tf

TECH = S.TECH
ALL_T = list(TECH)

def desc_of(i): return TECH[i][0] + '.'


@T('hl001')
def g001(r, k):
    tp = r.choice(S.TOPICS)
    c = r.randrange(7)
    if c <= 2:
        ids = pick_ids(r, r.choice([4, 5]))
        sents = build_script(r, tp, ids)
        used = [i for i, _ in sents]
        unused = [i for i in ALL_T if i not in used]
        if len(unused) < 4: return None
        right = r.choice(used)
        body = P('다음은 발표문의 일부이다. 발표자의 말하기 방식으로 가장 적절한 것은?') + script_html(sents)
        return mc(body, desc_of(right), [desc_of(i) for i in r.sample(unused, 4)],
                  steps=['발표문에서 "%s"은(는) "%s" 방식이다.' % (dict(sents)[right], desc_of(right).rstrip('.'))] + ['%s: 발표문에 나타나지 않는다.' % desc_of(i) for i in r.sample(unused, 2)],
                  core='발표의 말하기 방식', lv='중' if c < 2 else '상', fam='A', r=r, ref=[3], vertical=True)
    if c == 3:
        ids = pick_ids(r, 5)
        sents = build_script(r, tp, ids)
        used = [i for i, _ in sents]; unused = [i for i in ALL_T if i not in used]
        if len(used) < 5 or not unused: return None
        right = r.choice(unused)
        body = P('다음은 발표문의 일부이다. 발표자의 말하기 방식으로 적절하지 않은 것은?') + script_html(sents)
        return mc(body, desc_of(right), [desc_of(i) for i in r.sample(used, 4)],
                  steps=['%s: 발표문에 나타나지 않는다.' % desc_of(right)] + ['%s: "%s"' % (desc_of(i), dict(sents)[i]) for i in r.sample(used, 2)],
                  core='발표의 말하기 방식', lv='상', fam='B', r=r, ref=[3], vertical=True)
    if c == 4 or c == 5:
        ids = pick_ids(r, 5)
        sents = build_script(r, tp, ids)
        if len(sents) < 5: return None
        labels = {n: CIRC[n] for n in range(5)}
        body = P('발표문의 ㉠~㉤에 대한 설명으로 적절하지 않은 것은?') + script_html(sents[:5], labels)
        bad = r.randrange(5)
        items, st = [], []
        for n, (i, s) in enumerate(sents[:5]):
            if n == bad:
                alt = r.choice([x for x in ALL_T if x != i])
                items.append(('%s은(는) %s' % (CIRC[n], desc_of(alt)), True)); st.append('%s의 실제 기능: %s 제시된 설명("%s")은 옳지 않다.' % (CIRC[n], desc_of(i), desc_of(alt).rstrip('.')))
            else:
                items.append(('%s은(는) %s' % (CIRC[n], desc_of(i)), False)); st.append('%s: %s' % (CIRC[n], desc_of(i)))
        return mcs(body, items, steps=st, core='발표 문장의 기능', lv='상' if c == 4 else '최', fam='C', r=r, ref=[3], vertical=True)
    if c == 6:
        return tpl_tf(r, S2.TF_SPEECH, r.choice(['ok', 'bad']), lv='중', fam='D', ref=[3])
    ids = pick_ids(r, 4)
    sents = build_script(r, tp, ids)
    used = [i for i, _ in sents]; unused = [i for i in ALL_T if i not in used]
    right = r.choice(used)
    return mc(P('발표자가 사용한 말하기 방식으로 알맞은 것은?') + script_html(sents), desc_of(right), [desc_of(i) for i in r.sample(unused, 4)], steps=['"%s"에서 %s' % (dict(sents)[right], desc_of(right))], core='발표의 말하기 방식', lv='하', fam='E', r=r, ref=[3], vertical=True)


def plan_html(plan):
    """plan: [(단계, 기법 id)] → 계획 메모 상자"""
    out, last = [], None
    n = 0
    for st, i in plan:
        if st != last:
            out.append('<p><b>[%s]</b></p>' % st); last = st
        n += 1
        out.append('<p>○ %s</p>' % (TECH[i][1] + '.'))
    return '<div class="bogi">' + ''.join(out) + '</div>'


@T('hl002')
def g002(r, k):
    tp = r.choice(S.TOPICS)
    c = r.randrange(5)
    intro = r.sample(S.TECH_STAGE['도입'], 1)
    mid = r.sample(S.TECH_STAGE['전개'], 3)
    end = r.sample(S.TECH_STAGE['정리'], 1)
    plan_ids = intro + mid + end
    miss = r.choice(plan_ids)
    real = [i for i in plan_ids if i != miss]
    # 발표문에는 계획 밖 기법 하나를 더 넣어 변별력을 높인다
    extra = [i for i in ALL_T if i not in plan_ids]
    real_all = real + ([r.choice(extra)] if c >= 3 else [])
    sents = build_script(r, tp, real_all)
    plan = [(TECH[i][2], i) for i in plan_ids]
    plan = sorted(plan, key=lambda x: {'도입': 0, '전개': 1, '정리': 2}[x[0]])
    body = P('다음은 학생이 발표를 하기 위해 세운 계획이다. 발표에 반영되지 않은 것은?') + plan_html(plan) + P('〈발표문〉') + script_html(sents) if c >= 2 else \
        P('다음은 학생이 발표를 하기 위해 세운 계획과 발표문의 일부이다. 발표에 반영되지 않은 것은?') + plan_html(plan) + script_html(sents)
    # 선택지: 계획 항목 5개
    opts = [(TECH[i][1] + '.', i == miss) for i in plan_ids]
    return mcs(body, opts, steps=['%s: 발표문에 반영되지 않았다.' % TECH[miss][1]] + ['%s: "%s"에 반영되었다.' % (TECH[i][1], dict(sents)[i]) for i in real[:3]],
               core='계획과 실제 발표의 대응', lv='중' if c < 3 else '상', fam='A', r=r, ref=[2], vertical=True)


@T('hl003')
def g003(r, k):
    aud = r.choice(list(S.AUD))
    good, bad = S.AUD[aud]
    c = r.randrange(5)
    if c <= 2:
        right = r.choice(bad); ws = r.sample(good, 4)
        return mc(P("'%s'을(를) 청중으로 하는 발표에서 청중을 고려한 전략으로 적절하지 않은 것은?" % aud), right, ws, steps=['"%s"은(는) 이 청중의 특성에 맞지 않는다.' % right] + ['"%s"은(는) 청중의 특성을 고려한 적절한 전략이다.' % g for g in ws[:2]], core='청중 분석과 발표 전략', lv='중', fam='A', r=r, ref=[2], vertical=True)
    if c == 3:
        right = r.choice(good); ws = r.sample(bad, 4)
        return mc(P("'%s'을(를) 청중으로 하는 발표 전략으로 가장 적절한 것은?" % aud), right, ws, steps=['"%s"은(는) 청중의 특성을 고려한 적절한 전략이다.' % right] + ['"%s"은(는) 부적절하다.' % b for b in ws[:2]], core='청중 분석과 발표 전략', lv='하', fam='B', r=r, ref=[2], vertical=True)
    other = r.choice([a for a in S.AUD if a != aud])
    right = r.choice(S.AUD[other][0])
    ws = r.sample(S.AUD[aud][0], 4)
    return mc(P("'%s'을(를) 청중으로 하는 발표 전략으로 적절하지 않은 것은?" % aud), right, ws, steps=["\"%s\"은(는) '%s'에게 알맞은 전략이어서 이 청중에게는 어울리지 않는다." % (right, other)], core='청중 분석과 발표 전략', lv='상', fam='C', r=r, ref=[2], vertical=True)


LINES = ['이 점이 오늘 발표의 핵심입니다.', '{n}에 대해 함께 생각해 보면 좋겠습니다.', '방법은 모두 세 가지입니다.', '여기서 가장 중요한 것은 실천입니다.']

@T('hl004')
def g004(r, k):
    tp = r.choice(S.TOPICS)
    keys = list(S.PARA)
    c = r.randrange(6)
    if c <= 1:
        key = r.choice(keys); typ, el, fn = S.PARA[key]
        line = key + ' ' + fill(r.choice(LINES), tp)
        ws = [S.PARA[x][2] for x in r.sample([y for y in keys if S.PARA[y][2] != fn], 4)]
        return mc(P('발표문의 밑줄 친 부분이 발표에서 하는 기능으로 가장 적절한 것은?') + '<div class="bogi"><p><u>%s</u> %s</p></div>' % (key, line.split(' ', 1)[1] if ' ' in line else line), fn, ws, steps=['%s은(는) %s(%s)로서 %s' % (key, typ, el, fn)], core='비언어·반언어적 표현의 기능', lv='중', fam='A', r=r, ref=[3], vertical=True)
    if c == 2:
        non = [x for x in keys if S.PARA[x][0] == '비언어적 표현']; para = [x for x in keys if S.PARA[x][0] == '반언어적 표현']
        if r.random() < .5:
            right = r.choice(para); ws = r.sample(non, 4)
            return mc(P('다음 중 반언어적 표현이 아닌 것은?') if False else P('다음 중 비언어적 표현이 아닌 것은?'), right, ws, steps=['%s은(는) 반언어적 표현(%s)이다.' % (right, S.PARA[right][1])] + ['%s은(는) 비언어적 표현이다.' % x for x in ws[:2]], core='비언어적·반언어적 표현의 구분', lv='중', fam='B', r=r, ref=[3], vertical=False)
        right = r.choice(non); ws = r.sample(para, 4)
        return mc(P('다음 중 반언어적 표현이 아닌 것은?'), right, ws, steps=['%s은(는) 비언어적 표현(%s)이다.' % (right, S.PARA[right][1])] + ['%s은(는) 반언어적 표현이다.' % x for x in ws[:2]], core='비언어적·반언어적 표현의 구분', lv='중', fam='C', r=r, ref=[3], vertical=False)
    if c == 3:
        key = r.choice(keys); typ, el, fn = S.PARA[key]
        names = ['목소리의 크기', '말의 속도', '쉼', '억양', '시선', '표정', '몸짓']
        ws = [x for x in names if x != el]
        return mc(P("'%s'이(가) 활용한 표현 요소로 알맞은 것은?" % key), el, r.sample(ws, 4), steps=['%s: %s' % (key, el)], core='비언어·반언어적 표현의 요소', lv='하', fam='D', r=r, ref=[3], vertical=False)
    if c == 4:
        xs = r.sample(keys, 3); stm = []
        for key in xs:
            typ, el, fn = S.PARA[key]; truth = r.random() < .5
            n = typ if truth else ('비언어적 표현' if typ == '반언어적 표현' else '반언어적 표현')
            stm.append(("'%s'은(는) %s이다." % (key, n), truth, "'%s'은(는) %s(%s)이다." % (key, typ, el)))
        return bogi('발표 중에 사용한 표현에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='E', r=r, ref=[3], ask='')
    return tpl_tf(r, S2.TF_SPEECH, r.choice(['ok', 'bad']), lv='중', fam='F', ref=[3])


@T('hl005')
def g005(r, k):
    P_ = S2.PUBLIC
    c = r.randrange(6)
    if c <= 1:
        a = r.choice(P_)
        ws = [x['bad'] for x in r.sample([y for y in P_ if y['bad'] != a['bad']], 4)]
        return mc(P("다음 상황(%s)에서 쓰는 표현으로 가장 적절한 것은?" % a['ctx']), a['ok'], ws, steps=['"%s": %s' % (a['ok'], a['why'])] + ['"%s"은(는) 부적절하다.' % w for w in ws[:2]], core='언어의 공공성과 표현의 적절성', lv='하' if c == 0 else '중', fam='A', r=r, ref=[1], vertical=True)
    if c == 2:
        a = r.choice(P_)
        ws = [x['ok'] for x in r.sample([y for y in P_ if y['ok'] != a['ok']], 4)]
        return mc(P('공적인 담화에서 쓰는 표현으로 적절하지 않은 것은?'), a['bad'], ws, steps=['"%s": %s' % (a['bad'], a['why'])], core='언어의 공공성과 표현의 적절성', lv='중', fam='B', r=r, ref=[1], vertical=True)
    if c == 3:
        a = r.choice(P_)
        kinds = ['유행어', '비속어', '외국어 남용', '비격식', '존중', '높임', '인신공격', '줄임말', '인터넷 은어']
        names = {'유행어': '유행어를 사용하여 공식적인 자리에 어울리지 않는다.', '비속어': '비속어를 사용하여 공적 담화의 품위를 해친다.', '외국어 남용': '불필요한 외국어를 사용하여 청자가 이해하기 어렵다.', '비격식': '격식에 맞지 않는 구어적 표현을 사용하였다.',
                 '존중': '상대나 특정 집단을 존중하지 않는 표현을 사용하였다.', '높임': '높임 표현을 알맞게 사용하지 않았다.', '인신공격': '주장이 아닌 사람을 공격하는 표현을 사용하였다.', '줄임말': '지나친 줄임말을 사용하여 의미 전달이 불분명하다.', '인터넷 은어': '인터넷 은어와 웃음 표기를 사용하여 공공 게시글에 어울리지 않는다.'}
        right = names[a['kind']]
        ws = [names[x] for x in r.sample([y for y in kinds if y != a['kind']], 4)]
        return mc(P("다음 상황(%s)에서 밑줄 친 표현이 적절하지 않은 이유로 가장 알맞은 것은?" % a['ctx']) + '<div class="bogi"><p><u>%s</u></p></div>' % a['bad'], right, ws, steps=[a['why']], core='표현의 적절성', lv='상', fam='C', r=r, ref=[1], vertical=True)
    if c == 4:
        a = r.choice(P_)
        return mc(P("다음 문장을 상황(%s)에 맞게 고친 것으로 적절한 것은?" % a['ctx']) + '<div class="bogi"><p>%s</p></div>' % a['bad'], a['ok'], [x['ok'] for x in r.sample([y for y in P_ if y['ok'] != a['ok'] and y['kind'] != a['kind']], 4)], steps=[a['why']], core='표현의 적절성', lv='상', fam='D', r=r, ref=[1], vertical=True)
    return tpl_tf(r, S2.TF_SPEECH, r.choice(['ok', 'bad']), lv='중', fam='E', ref=[1])


def _conf_item(r, mode='bad', lv='상', fam='A'):
    prop = r.choice(S2.PROP)
    # 같은 품사 짝이 반드시 들어가도록 4개 틀을 뽑는다
    cls = r.choice(['부사', '의존 명사', '인용절', '보조 용언'])
    same = [e for e in S2.EXPR if e[1] == cls]
    if len(same) < 2: return None
    a, b = r.sample(same, 2)
    if a[2] == b[2]: return None
    others = [e for e in S2.EXPR if e[1] != cls]
    c_, d_ = r.sample(others, 2)
    if c_[1] == d_[1]: d_ = r.choice([e for e in others if e[1] != c_[1]])
    frames = [a, b, c_, d_]
    r.shuffle(frames)
    labels = 'ⓐⓑⓒⓓ'
    lines = []
    for L, f in zip(labels, frames):
        lines.append('%s %s' % (L, f[0].format(**prop)))
    # 진술 5개: 같은 품사 쌍 1, 다른 품사 쌍 4
    stm = []
    pairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
    r.shuffle(pairs)
    chosen = []
    for (i, j) in pairs:
        if len(chosen) >= 5: break
        chosen.append((i, j))
    k = r.randrange(len(chosen))
    items, st = [], []
    for n, (i, j) in enumerate(chosen):
        fi, fj = frames[i], frames[j]
        Li, Lj = labels[i], labels[j]
        truth = (n != k) if mode == 'bad' else (n == k)
        if fi[1] == fj[1] and fi[2] != fj[2]:
            hi = Li if fi[2] > fj[2] else Lj
            lo = Lj if hi == Li else Li
            txt = '%s와(과) %s는 모두 %s을(를) 썼는데, %s이(가) 나타내는 확신의 정도는 %s가 더 높아요.' % (Li, Lj, fi[1], fi[1], hi if truth else lo)
            why = '%s(%s %d)와(과) %s(%s %d): %s가 확신의 정도가 더 높다.' % (Li, fi[3], fi[2], Lj, fj[3], fj[2], hi)
        elif fi[1] != fj[1]:
            claimed = fi[1] if truth else fj[1]
            txt = '%s는 %s와 달리 %s을(를) 써서 확신의 정도를 드러냈어요.' % (Li, Lj, claimed)
            why = '%s는 %s을(를), %s는 %s을(를) 써서 확신의 정도를 드러냈다.' % (Li, fi[1], Lj, fj[1])
        else:
            return None
        items.append((txt, n == k)); st.append('%s %s' % ('옳다.' if truth else '옳지 않다.', why))
    ask = '위 문장들에 대한 설명으로 적절하지 않은 것은?' if mode == 'bad' else '위 문장들에 대한 설명으로 적절한 것은?'
    body = P('다음은 "%s"라는 내용에 어휘와 문법 요소를 달리하여 확신의 정도에 변화를 준 문장들이다. %s' % (prop['hap'].replace('입니다', '이다').replace('합니다', '하다').replace('됩니다', '된다').replace('이롭습니다', '이롭다').replace('높입니다', '높인다').replace('있습니다', '있다').replace('시급합니다', '시급하다').replace('중요합니다', '중요하다').replace('공정합니다', '공정하다').replace('효과적입니다', '효과적이다'), ask)) + '<div class="bogi">' + ''.join('<p>%s</p>' % l for l in lines) + '</div>'
    return mcs(body, items, steps=st, core='확신의 정도를 드러내는 표현', lv=lv, fam=fam, r=r, ref=[3], vertical=True)


@T('hl006')
def g006(r, k):
    c = r.randrange(6)
    if c <= 1: return _conf_item(r, 'bad', '상', 'A')
    if c == 2: return _conf_item(r, 'ok', '상', 'B')
    if c == 3:
        prop = r.choice(S2.PROP)
        e1, e2 = r.sample([e for e in S2.EXPR if e[1] == r.choice(['부사', '인용절', '의존 명사'])], 2) if False else (None, None)
        same_cls = r.choice(['부사', '인용절', '의존 명사'])
        pool = [e for e in S2.EXPR if e[1] == same_cls]
        a, b = r.sample(pool, 2)
        if a[2] == b[2]: return None
        hi = a if a[2] > b[2] else b
        body = P('다음 두 문장 가운데 말하는 내용에 대한 확신의 정도가 더 높은 것은?') + BOX(['㉠ ' + a[0].format(**prop), '㉡ ' + b[0].format(**prop)])
        right = '㉠' if hi is a else '㉡'
        return mcs(body, [(o, o == right) for o in ['㉠', '㉡', '㉠과 ㉡의 확신 정도가 같다', '비교할 수 없다', '두 문장 모두 확신을 나타내지 않는다']], steps=['%s(%d)와 %s(%d): %s이 확신의 정도가 더 높다.' % (a[3], a[2], b[3], b[2], hi[3])], core='확신 표현의 정도', lv='중', fam='C', r=r, ref=[3], vertical=False)
    if c == 4:
        # 품사 판별
        e = r.choice(S2.EXPR); prop = r.choice(S2.PROP)
        names = ['부사', '의존 명사', '보조 용언', '인용절']
        ws = [n for n in names if n != e[1]] + ['관형사']
        body = P('다음 문장에서 확신의 정도를 드러내는 데 쓰인 표현은 무엇인가?') + '<div class="bogi"><p>%s</p></div>' % e[0].format(**prop)
        return mc(body, e[1], ws[:4], steps=["'%s'은(는) 확신의 정도를 드러내는 %s 표현이다." % (e[3], e[1])], core='확신 표현의 종류', lv='중', fam='D', r=r, ref=[3], vertical=False)
    return tpl_tf(r, S2.TF_SPEECH, r.choice(['ok', 'bad']), lv='중', fam='E', ref=[3])


DEFS = {'발표': '한 사람이 여러 청중에게 정보나 의견을 전달하는 말하기', '토의': '공동의 문제를 해결하기 위해 협력하여 최선의 방안을 찾는 말하기', '토론': '찬반 입장이 나뉜 논제에 대해 논증으로 상대를 설득하는 말하기',
        '협상': '서로 다른 입장을 가진 당사자가 의견 차이를 조정하여 합의에 이르는 말하기', '면담': '목적을 가지고 특정한 사람에게 질문하고 답을 들으며 정보를 얻는 말하기', '대화': '둘 이상의 사람이 일상적으로 말을 주고받으며 생각과 감정을 나누는 말하기'}

@T('hl007')
def g007(r, k):
    c = r.randrange(6)
    if c <= 1:
        t = r.choice(list(DEFS))
        return mc(P("다음 설명에 해당하는 담화(말하기)의 유형은?") + '<div class="bogi"><p>%s</p></div>' % DEFS[t], t, [x for x in DEFS if x != t][:4] if False else r.sample([x for x in DEFS if x != t], 4), steps=['%s: %s' % (t, DEFS[t])], core='담화의 유형', lv='하', fam='A', r=r, ref=[1], vertical=False)
    if c == 2:
        t = r.choice(list(DEFS)); ws = r.sample([x for x in DEFS if x != t], 4)
        return mc(P("'%s'에 대한 설명으로 알맞은 것은?" % t), DEFS[t], [DEFS[x] for x in ws], steps=['%s: %s' % (t, DEFS[t])], core='담화의 유형', lv='중', fam='B', r=r, ref=[1], vertical=True)
    if c == 3:
        elems = [('화자', '말하는 사람'), ('청자', '듣는 사람'), ('메시지', '전달하는 내용'), ('맥락', '말하는 때, 장소, 관계 등 담화가 이루어지는 상황'), ('매체', '말이 전달되는 수단')]
        e = r.choice(elems); ws = [x for x in elems if x[0] != e[0]]
        return mc(P("화법의 구성 요소 중 '%s'에 해당하는 설명으로 알맞은 것은?" % e[0]), e[1], [w[1] for w in ws][:4], steps=['%s: %s' % e], core='화법의 구성 요소', lv='하', fam='C', r=r, ref=[1], vertical=False)
    if c == 4: return tpl_tf(r, S2.TF_SPEECH, 'ok', lv='하', fam='D', ref=[1])
    return tpl_tf(r, S2.TF_SPEECH, 'bad', lv='중', fam='E', ref=[1])
