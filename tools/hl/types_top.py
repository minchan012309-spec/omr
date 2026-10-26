# -*- coding: utf-8 -*-
"""기초 확인(하) 11종 + 장문 지문 최상위·융합 6종 (hl100~hl116)"""
import re, itertools
from hllib import *
from speech_gen import ff, fill, IN_F, in_desc, IN_GENERIC, CX, cx_desc, cx_utter, ipron
from qlib import CIRC
import kb_speech as S, kb_speech2 as S2
import kb_gram_a, kb_tf_b, kb_tf, kb_word2
import types_old as O
import types_mix as MX
import types_speech_b as SB
import types_speech_c as SC
from orth_gen import tpl_tf

# ============================================================ 기초 확인 (하)
def _quoted(stmt):
    return re.findall(r"'([^']{1,14})'", stmt)

def _basic_tf(r, bank, lv='하', fam='b'):
    T_ = [x for x in bank if x[1]]; F_ = [x for x in bank if not x[1]]
    c = r.randrange(6)
    if c == 0 and len(F_) >= 4:
        return tpl_tf(r, bank, mode='ok', lv=lv, fam=fam + 'o', ref=[1])
    if c <= 2 and len(F_) >= 1 and len(T_) >= 4:
        return tpl_tf(r, bank, mode='bad', lv=lv, fam=fam + 'x', ref=[1])
    if c == 3:
        return tpl_tf(r, bank, three=True, lv=lv, fam=fam + 't', ref=[1])
    # 빈칸 고르기: 참인 진술의 따옴표 낱말
    pool = {}
    for st, tr, why in T_:
        for q in _quoted(st):
            pool.setdefault(q, []).append(st)
    cands = [(st, _quoted(st)) for st, tr, why in T_ if len(_quoted(st)) == 1]
    if len(cands) < 6 or len(pool) < 5: return None
    st, qs = r.choice(cands); ans = qs[0]
    ws = _same_kind(r, ans, [w for w in pool if w != ans])
    body = P('다음 글의 빈칸에 들어갈 말로 알맞은 것은?') + BOX([st.replace("'%s'" % ans, '(   )')])
    return mc(body, ans, ws, steps=['빈칸에는 "%s"이(가) 들어간다.' % ans], core='기본 개념 확인', lv=lv, fam=fam + 'b', r=r, ref=[1], vertical=False)

def _kind(w):
    """빈칸 낱말의 갈래: 어미·접사(-로 시작) / 조사처럼 짧은 말 / 용언(…다) / 문장·구 / 그 밖의 낱말"""
    if w.startswith('-') or re.search(r'/-', w): return 'end'
    if ' ' in w.strip(): return 'phrase'
    if len(w) <= 3 and not w.endswith('다'): return 'short'
    if w.endswith('다'): return 'verb'
    return 'word'


def _same_kind(r, ans, others):
    """오답 4개: 정답과 같은 갈래를 먼저, 모자라면 길이가 비슷한 것으로 채운다(갈래가 다른 선지만 있으면 정답이 바로 드러나므로)"""
    k = _kind(ans)
    same = [w for w in others if _kind(w) == k]
    pick = r.sample(same, min(4, len(same)))
    if len(pick) < 4:
        rest = sorted([w for w in others if w not in pick], key=lambda w: (abs(len(w) - len(ans)), r.random()))
        pick += rest[:4 - len(pick)]
    return pick


def _ban(*banks):
    out = []
    for b in banks: out += b
    return out

def _lazy_banks():
    return {
     'hl100': _ban(S2.TF_SPEECH), 'hl101': _ban(S2.TF_DISC), 'hl102': _ban(S2.TF_CONV),
     'hl103': _ban(kb_gram_a.TF_GA), 'hl104': _ban(kb_tf_b.TF_HON, kb_tf_b.TF_NEGEND, kb_tf_b.TF_TENSE, kb_tf_b.TF_VOICE),
     'hl105': _ban(kb_word2.TF_WORD),
     'hl106': _ban(O.ERA_TF, O.ORTH_OLD, O.TF_BODY, O.TF_VERB, O.TF_CASE, O.TF_HON, O.TF_TIME, O.TF_Q, O.TF_SEM),
     'hl107': _ban(kb_tf.ORTH_CONCEPT),
     'hl110': _ban(S2.TF_SPEECH, S2.TF_DISC, S2.TF_CONV, kb_tf.ORTH_CONCEPT, kb_gram_a.TF_GA),
    }
_BANKS = None
def _banks():
    global _BANKS
    if _BANKS is None: _BANKS = _lazy_banks()
    return _BANKS

for _t in ('hl100', 'hl101', 'hl103', 'hl104', 'hl105', 'hl106', 'hl107', 'hl110'):
    def _mk(tag):
        @T(tag)
        def g(r, k):
            return _basic_tf(r, _banks()[tag], fam=tag[-2:])
        return g
    _mk(_t)

@T('hl102')
def _g102(r, k):
    return SC.g102(r, k)

# 맞춤법 기초 : 올바른 표기 고르기
def _spell(r, pool, tag):
    c = r.randrange(5)
    es = r.sample(pool, 5)
    if len({e[3] for e in es}) < 3: return None
    if c <= 2:
        a = es[0]; ws = [e[1] for e in es[1:]]
        return mc(P('다음 중 맞춤법에 맞게 쓴 것은?'), a[0], ws, steps=['"%s"이(가) 맞는 표기이다. %s' % (a[0], a[2])] + ['"%s"은(는) "%s"로 써야 한다.' % (e[1], e[0]) for e in es[1:3]], core=a[2], lv='하', fam='s', r=r, ref=[1], vertical=False)
    if c == 3:
        a = es[0]; ws = [e[0] for e in es[1:]]
        return mc(P('다음 중 맞춤법에 어긋난 것은?'), a[1], ws, steps=['"%s"은(는) "%s"로 써야 한다. %s' % (a[1], a[0], a[2])], core=a[2], lv='하', fam='t', r=r, ref=[1], vertical=False)
    a = es[0]
    return mc(P('"%s"의 바른 표기는?' % a[1]), a[0], [e[1] for e in es[1:]] , steps=[a[2]], core=a[2], lv='하', fam='u', r=r, ref=[1], vertical=False)

@T('hl108')
def g108(r, k):
    pool = [e for e in MX.SRC if e[3] in MX.NOUN_BANKS + ('SAI_Y',)]
    return _spell(r, pool, 'hl108')

import kb_orth4 as O4
@T('hl109')
def g109(r, k):
    c = r.randrange(3)
    if c == 0:
        pool = [e for e in MX.SRC if e[3] in MX.ADV_BANKS]
        return _spell(r, pool, 'hl109')
    items = O4.GUBUN + O4.EOMI2 + O4.COMMON
    e = r.choice(items)
    bads = list(e['bad'])
    others = [x for x in items if x is not e and x['ok'] != e['ok']]
    # 덧붙일 오답은 정답과 끝 음절이 같고 길이가 비슷한 틀린 표기부터(엉뚱한 낱말이 끼면 정답이 바로 드러난다)
    cand = list(dict.fromkeys(b for x in others for b in x['bad'] if b not in bads and b != e['ok']))
    cand.sort(key=lambda w: (w[-1:] != e['ok'][-1:], abs(len(w) - len(e['ok'])), r.random()))
    extra = cand[:6]
    ws = list(dict.fromkeys(bads + extra))
    ws = [w for w in ws if w != e['ok']]
    if len(ws) < 4: return None
    s = e['s'].replace('__', '(   )')
    return mc(P('다음 문장의 빈칸에 들어갈 말로 알맞은 것은?') + BOX([s]), e['ok'], ws[:4], steps=[e['why']], core=e['why'], lv='하', fam='v', r=r, ref=[2], vertical=False)


# ============================================================ 장문 지문 도우미
FILL = [
 '저는 이 주제를 정하려고 친구들과 이야기를 나누고 관련 자료를 찾아보았습니다.',
 '{problem}은(는) 우리 모두가 한 번쯤은 겪어 본 일이라고 생각합니다.',
 '이 문제를 놓고 {pc}는 의견과 {cc}는 의견이 함께 나오고 있습니다.',
 '먼저 {pc}는 입장은 {pr}이라는 점을 근거로 듭니다.',
 '반면 {cc}는 입장은 {cr}이라는 점을 근거로 듭니다.',
 '방안은 모두 세 가지입니다. 첫째, {s0}. 둘째, {s1}. 셋째, {s2}.',
 '{s0}은(는) {e0}는 장점이 있지만 {l0}는 점이 아쉽습니다.',
 '{s1}은(는) {e1}는 장점이 있지만 {l1}는 점은 보완이 필요합니다.',
 '{s2}은(는) {e2}는 장점이 있고 {l2}는 점은 감수해야 합니다.',
 '이렇게 살펴보면 어느 한 가지 방안만으로는 충분하지 않다는 생각이 듭니다.',
 '저는 이 가운데 학교 구성원이 함께 실천할 수 있는 방안이 무엇인지 계속 고민했습니다.',
]
def _f(t, tp): return ff(t, tp)

def long_speech_paras(r, tp, n_tech=8, extra_sents=None):
    """[[(문장, 기법 id 또는 None)…]…]  (문단 5개)"""
    ids = r.sample(S.TECH_STAGE['도입'], 2) + r.sample(S.TECH_STAGE['전개'], 4) + r.sample(S.TECH_STAGE['정리'], 2)
    ids = ids[:n_tech]
    def T_(i): return (fill(r.choice(S.TECH[i][3]), tp), i)
    fl = [(_f(t, tp), None) for t in FILL]
    intro = [T_(ids[0]), fl[0], T_(ids[1])]
    p2 = [fl[1], T_(ids[2]), fl[2], T_(ids[3])]
    p3 = [fl[3], T_(ids[4]), fl[4], T_(ids[5])]
    p4 = [fl[5], fl[6], fl[7], fl[8]]
    p5 = [T_(ids[6]), fl[9], T_(ids[7]), fl[10]]
    paras = [intro, p2, p3, p4, p5]
    if extra_sents:
        for sents, pi in extra_sents: paras[pi].extend(sents)
    return paras, ids

def render_long(paras, lab, speakers=None):
    seen = set(); out = []
    for pi, para in enumerate(paras):
        parts = []
        for text, i in para:
            if i is not None and i in lab and i not in seen:
                seen.add(i); parts.append('%s<u>%s</u>' % (lab[i], text))
            else:
                parts.append(text)
        sp = ('<b>%s</b>: ' % speakers[pi]) if speakers else ''
        out.append('<p>%s%s</p>' % (sp, ' '.join(parts)))
    return '<div class="bogi lp">' + ''.join(out) + '</div>'

def long_q(r, paras, ids, descs, extra, intro_txt, *, core, ref, fam, speakers=None, modes=('one', 'not5', 'ok5', 'ok5', 'unused', 'combo', 'not5')):
    """ids: 지문에 나타난 표지 목록(첫 등장 순서) / descs: {id: 설명}"""
    mode = r.choice(modes)
    used = []
    for p in paras:
        for t, i in p:
            if i is not None and i not in used: used.append(i)
    if mode == 'unused':
        un = [d for i, d in descs.items() if i not in used] + list(extra)
        un = list(dict.fromkeys(un))
        if not un or len(used) < 4: return None
        right = r.choice(un); ws = [descs[i] for i in r.sample(used, 4)]
        body = P(intro_txt + ' 지문에 나타나지 않은 것은?') + render_long(paras, {}, speakers)
        return mc(body, right, ws, steps=['"%s"은(는) 지문에 나타나지 않는다.' % right.rstrip('.')], core=core, lv='최', fam=fam + 'u', r=r, ref=ref, vertical=True)
    if len(used) < 5: return None
    pick = r.sample(used, 5)
    order = [i for i in used if i in pick]
    lab = {i: CIRC[n] for n, i in enumerate(order)}
    box = render_long(paras, lab, speakers)
    unusedD = list(dict.fromkeys([descs[i] for i in descs if i not in pick] + list(extra)))
    if mode == 'one':
        k = r.choice(order); lab = {k: '㉠'}; box = render_long(paras, lab, speakers)
        ws = r.sample([descs[i] for i in descs if i != k] + list(extra), 4)
        return mc(P(intro_txt + ' ㉠에서 나타난 방식으로 가장 적절한 것은?') + box, descs[k], ws, steps=['㉠에서는 %s' % descs[k]], core=core, lv='상', fam=fam + 'a', r=r, ref=ref, vertical=True)
    if mode == 'combo':
        st = []
        for n, i in enumerate(order[:3]):
            truth = r.random() < .5
            d = descs[i] if truth else r.choice(unusedD)
            st.append(('%s에서는 %s' % (CIRC[n], d), truth, '%s: 실제로는 %s' % (CIRC[n], descs[i]) if not truth else descs[i]))
        if all(x[1] for x in st) or not any(x[1] for x in st): st[0] = (st[0][0], not st[0][1], st[0][2])
        if not any(x[1] for x in st) or all(x[1] for x in st): return None
        # 첫 문장을 뒤집었으면 문장과 진위를 다시 맞춘다
        fixed = []
        for n, i in enumerate(order[:3]):
            truth = st[n][1]
            d = descs[i] if truth else r.choice(unusedD)
            fixed.append(('%s에서는 %s' % (CIRC[n], d), truth, (descs[i] if truth else '실제로는 %s' % descs[i])))
        it = bogi(intro_txt, fixed, pre=box, lv='최', fam=fam + 'c', r=r, core=core, ref=ref, ask='㉠~㉢에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?')
        return it
    badi = r.randrange(5)
    if mode == 'not5':
        opts = []
        for n, i in enumerate(order):
            opts.append('%s: %s' % (CIRC[n], r.choice(unusedD) if n == badi else descs[i]))
        right = opts[badi]; ws = [o for j, o in enumerate(opts) if j != badi]
        st = ['%s: 실제 기능은 「%s」이므로 이 선택지가 옳지 않다.' % (CIRC[badi], descs[order[badi]].rstrip('.'))] + ['%s: 「%s」 — 옳은 설명이다.' % (CIRC[n], descs[i].rstrip('.')) for n, i in enumerate(order) if n != badi][:2]
        ask = '㉠~㉤에 대한 설명으로 적절하지 않은 것은?'
    else:
        opts = []
        pool = list(unusedD)
        for n, i in enumerate(order):
            opts.append('%s: %s' % (CIRC[n], descs[i] if n == badi else r.choice(pool)))
        right = opts[badi]; ws = [o for j, o in enumerate(opts) if j != badi]
        st = ['%s: 「%s」 — 옳은 설명이다.' % (CIRC[badi], descs[order[badi]].rstrip('.'))] + ['%s: 실제 기능은 「%s」이므로 이 선택지는 옳지 않다.' % (CIRC[n], descs[i].rstrip('.')) for n, i in enumerate(order) if n != badi][:2]
        ask = '㉠~㉤에 대한 설명으로 적절한 것은?'
    return mc(P(intro_txt + ' ' + ask) + box, right, ws, steps=st, core=core, lv='최', fam=fam + mode, r=r, ref=ref, vertical=True)


# ============================================================ hl111 장문 발표
@T('hl111')
def g111(r, k):
    tp = r.choice(S.TOPICS)
    paras, ids = long_speech_paras(r, tp)
    descs = {i: S.TECH[i][0] + '.' for i in S.TECH}
    return long_q(r, paras, ids, descs, ['자신의 입장을 철회하고 청중의 의견을 수용하고 있다.', '청중에게 질문하지 않고 일방적으로 설명하고 있다.'],
                  '다음은 학생의 발표문이다.', core='발표의 말하기 방식', ref=[3], fam='L')


# ============================================================ hl112 장문 토론
ANS = {
 'prob': '그 문제는 {s1}을(를) 함께 시행하면 보완할 수 있습니다.',
 'ev': '해당 조사는 전체 학생을 대상으로 한 것이어서 대표성이 충분합니다.',
 'src': '{ex}이(가) 공개 강연에서 밝힌 내용이며 출처는 자료집에 실려 있습니다.',
 'case': '학교의 규모와 여건이 비슷해 우리 학교에도 적용할 수 있습니다.',
 'def': '여기서는 학생이 직접 참여하는 범위로 한정해서 말씀드린 것입니다.',
}
def _debate(r):
    tp = r.choice(S.TOPICS)
    descs = {}; paras = []; speakers = []
    sides = [('pro', '찬성 측'), ('con', '반대 측')]
    def side_feats(sd, feats):
        out = []
        head = ipron(tp, sd, [])
        out.append((head, None))
        for f in feats:
            i = 'f:%s:%s' % (f, sd); descs[i] = in_desc(f, sd)
            out.append((josa(ff(IN_F[f][0 if sd == 'pro' else 1], tp)), i))
        return out
    pf = r.sample(['def', 'eff', 'stat', 'case', 'urg'], 4); cf = r.sample(['def', 'eff', 'stat', 'case', 'opp'], 3)
    paras.append(side_feats('pro', pf)); speakers.append('찬성 측 입론')
    keys = r.sample(list(CX), 3)
    q = []
    for key in keys:
        u = cx_utter(tp, key, 'pro'); i = 'x:%s:con' % key; descs[i] = cx_desc(key, '찬성 측')
        q.append((u if not q else u.split('말씀하셨는데, ', 1)[1], i)); q.append((josa(ff(ANS[key], tp)), None))
    paras.append(q); speakers.append('반대 측 반대 신문과 찬성 측 답변')
    paras.append(side_feats('con', cf)); speakers.append('반대 측 입론')
    keys2 = r.sample(list(CX), 2); q2 = []
    for key in keys2:
        u = cx_utter(tp, key, 'con'); i = 'x:%s:pro' % key; descs[i] = cx_desc(key, '반대 측')
        q2.append((u if not q2 else u.split('말씀하셨는데, ', 1)[1], i)); q2.append((josa(ff(ANS[key], tp)), None))
    paras.append(q2); speakers.append('찬성 측 반대 신문과 반대 측 답변')
    rb = []
    for j in r.sample(list(SB.REB), 2):
        i = 'r:' + j; descs[i] = SB.REB[j][0]; rb.append((josa(ff(SB.REB[j][1], tp, inv=100 - tp['stat'][2])), i))
    paras.append(rb); speakers.append('반대 측 반박')
    # 설명이 같은 기능이 서로 다른 측에서 겹치지 않도록 이미 측별 문구에 반영돼 있다
    ids = [i for p in paras for _, i in p if i]
    return tp, paras, ids, descs, speakers

@T('hl112')
def g112(r, k):
    tp, paras, ids, descs, speakers = _debate(r)
    return long_q(r, paras, ids, descs, IN_GENERIC, '다음은 토론이다.', core='입론 · 반대 신문 · 반박의 기능', ref=[3], fam='D', speakers=speakers)


# ============================================================ hl113 장문 협상
FIL = {
 'ask': ['그다음에 저희 입장도 차례로 말씀드리겠습니다.'],
 'demand': ['저희 {a}은(는) 이번 학기 내내 그렇게 사용해 왔습니다.'],
 'reason': ['이 점을 꼭 헤아려 주셨으면 합니다.', '저희에게는 포기하기 어려운 사정입니다.'],
 'understand': ['저희도 {a}이(가) 얼마나 애써 왔는지 알고 있습니다.'],
 'counter': ['이 부분은 저희도 쉽게 물러서기 어렵습니다.'],
 'compromise': ['이렇게 하면 양쪽 모두 큰 손해 없이 지낼 수 있을 것입니다.', '서로 한 걸음씩 물러서는 방법이라고 생각합니다.'],
 'cond': ['다만 이 약속은 반드시 지켜져야 합니다.'],
 'confirm': [],
}
NEG_ASK = ('상대에게 원하는 바와 사정을 물어 협상의 방향을 잡고 있다.', 'B', '먼저 {a}은(는) {thing}을(를) 어떻게 쓰고 싶으신지 말씀해 주시겠습니까?')
def _nego(r):
    ng = r.choice(SC.NEG)
    descs = {i: SC.NF[i][0] for i in SC.NF}; descs['ask'] = NEG_ASK[0]
    paras = []; speakers = []
    order = ['ask'] + SC.ORDER
    for i in order:
        who = ng['b'] if i == 'ask' else (ng['a'] if SC.NF[i][1] == 'A' else ng['b'])
        main = josa((NEG_ASK[2] if i == 'ask' else SC.NF[i][2]).format(**ng))
        if i == 'ask': main = josa(NEG_ASK[2].format(**ng))
        sents = [(main, i)] + [(josa(t.format(**ng)), None) for t in FIL[i]]
        # 말한 사람이 바뀔 때만 새 문단
        if paras and speakers[-1] == who:
            paras[-1].extend(sents)
        else:
            paras.append(sents); speakers.append(who)
    return ng, paras, order, descs, speakers

@T('hl113')
def g113(r, k):
    ng, paras, ids, descs, speakers = _nego(r)
    return long_q(r, paras, ids, descs, SC.NEG_EXTRA,
                  josa('다음은 %s과(와) %s의 %s 사용에 관한 협상이다.' % (ng['a'], ng['b'], ng['thing'])), core='협상 발화의 기능', ref=[2], fam='N', speakers=speakers,
                  modes=('one', 'not5', 'ok5', 'ok5', 'not5'))


# ============================================================ hl114 화법 지문 + 문법
@T('hl114')
def g114(r, k):
    tp = r.choice(S.TOPICS)
    gid = r.sample(list(MX.GM), 6)
    gs = [(josa(ff(MX.GM[i][1], tp)), i) for i in gid]
    paras, _ = long_speech_paras(r, tp, extra_sents=[([gs[0], gs[1]], 1), ([gs[2], gs[3]], 2), ([gs[4], gs[5]], 3)])
    # 기법 표지는 표시하지 않고 문법 표지만 문항에 쓴다
    paras = [[(t, i if i in MX.GM else None) for t, i in p] for p in paras]
    descs = {i: MX.GM[i][0] for i in MX.GM}
    return long_q(r, paras, gid, descs, MX.GM_EXTRA, '다음은 학생의 발표문이다.', core='높임 · 피동 · 사동 · 안은문장 · 부정 · 시제 표현의 판별', ref=[1], fam='G',
                  modes=('one', 'not5', 'ok5', 'ok5', 'combo', 'not5'))


# ============================================================ hl115 화법 지문 + 맞춤법
@T('hl115')
def g115(r, k):
    tp = r.choice(S.TOPICS)
    ent = r.sample(MX.SRC, 6)
    if len({e[3] for e in ent}) < 4: return None
    labs = '㉠㉡㉢㉣㉤'
    sents = []
    for i, e in enumerate(ent):
        sents.append((MX.frame_text(r, e), i))
    paras, _ = long_speech_paras(r, tp, extra_sents=[(sents[:2], 1), (sents[2:4], 2), (sents[4:], 3)])
    paras = [[(t, i if isinstance(i, int) else None) for t, i in p] for p in paras]
    five = r.sample(range(6), 5); five.sort()
    lab = {e: labs[n] for n, e in enumerate(five)}
    box = render_long(paras, lab)
    mode = r.choice(['not', 'ok', 'not'])
    badi = r.randrange(5); opts = []; st = []
    for n, e in enumerate(five):
        ok, bad, why, nm = ent[e]
        wrong = (mode == 'not' and n == badi) or (mode == 'ok' and n != badi)
        if wrong:
            opts.append('%s: "%s"은(는) 맞는 표기이므로 고치지 않고 그대로 둔다.' % (labs[n], bad)); st.append('%s: 바른 표기는 "%s"이다. %s' % (labs[n], ok, why))
        else:
            opts.append('%s: "%s"을(를) "%s"(으)로 고쳐 쓴다.' % (labs[n], bad, ok)); st.append('%s: "%s"(으)로 고치는 것이 맞다. %s' % (labs[n], ok, why))
    right = opts[badi]; ws = [o for j, o in enumerate(opts) if j != badi]
    ask = '㉠~㉤을 바르게 고쳐 쓴 것으로 적절하지 않은 것은?' if mode == 'not' else '㉠~㉤을 바르게 고쳐 쓴 것으로 적절한 것은?'
    return mc(P('다음은 학생의 발표 원고이다. ' + ask) + box, right, ws, steps=[st[badi]] + [x for j, x in enumerate(st) if j != badi][:2], core='한글 맞춤법의 여러 조항 적용', lv='최', fam='M' + mode, r=r, ref=[1], vertical=True)


# ============================================================ hl116 〈보기〉 복합 판단
_TECH_AMBIG = {'G', 'V', 'R'}
def _facts_all(r):
    F = []
    for kind, shown, true, falses, why in O.FACTS:
        F.append(('중세 국어', shown, true, falses, why))
    for ok, bad, why, nm in MX.SRC:
        F.append(('맞춤법', '표기 "%s"' % bad, josa('"%s"은(는) "%s"(으)로 고쳐 써야 한다.' % (bad, ok)), [josa('"%s"은(는) 맞는 표기이다.' % bad), josa('"%s"은(는) 고치지 않아도 된다.' % bad)], why))
    for sent, feats in MX.SENT:
        f = r.choice(sorted(feats)); others = [x for x in MX.FEATS if x not in feats]
        F.append(('문법', '"%s"' % sent, '%s에는 %s 표현이 나타난다.' % ('이 문장', f), ['이 문장에는 %s 표현이 나타난다.' % o for o in others], '이 문장에 나타나는 요소: ' + ', '.join(sorted(feats))))
    for i, v in S.TECH.items():
        if i in _TECH_AMBIG: continue   # G(몸짓)·V(자료 가리킴)·R(반응 확인)은 서로 겹쳐 해석될 수 있다
        F.append(('화법', '발표 문장: "%s"' % fill(r.choice(v[3]), r.choice(S.TOPICS)), '이 문장은 %s.' % v[0], ['이 문장은 %s.' % w[0] for j, w in S.TECH.items() if j != i and j not in _TECH_AMBIG], v[0]))
    return F

_FA = None
@T('hl116')
def g116(r, k):
    F = _facts_all(r)
    kinds = ['중세 국어', '맞춤법', '문법', '화법']
    pick = r.sample(kinds, 3)
    stmts = []
    for n, kd in enumerate(pick):
        f = r.choice([x for x in F if x[0] == kd]); truth = r.random() < .5
        text = josa(f[1] + ' ⇒ ' + (f[2] if truth else r.choice(f[3])))
        why = f[4].rstrip('. ') + '.'
        stmts.append((text, truth, '%s: %s' % (kd, why) + ('' if truth else ' 바른 설명: ' + f[2])))
    if all(x[1] for x in stmts) or not any(x[1] for x in stmts): return None
    return bogi('다음 〈보기〉는 화법과 언어의 여러 영역에서 가져온 자료와 그에 대한 설명이다.', stmts, lv='최', fam='K', r=r, core='화법 · 문법 · 맞춤법 · 중세 국어 종합', ref=[2],
                ask='각 설명이 옳은지 판단하여, 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?')
