# -*- coding: utf-8 -*-
"""Ⅰ-B 토의와 토론 (hl008~hl016)"""
from hllib import *
from speech_gen import *
from qlib import *
import kb_speech as S, kb_speech2 as S2
from orth_gen import tpl_tf

MODES = ['one', 'one', 'not5', 'ok5', 'not5']
LVM = {'one': '중', 'not5': '상', 'ok5': '상'}


def _mode_lv(r):
    m = r.choice(MODES)
    return m, LVM[m]


def _disc_turns(r, tp, mc_ids, p_ids, who):
    ts = discussion(r, tp, mc_ids, p_ids)
    out = []
    for sp, s, kind, i in ts:
        out.append((sp, s, i if kind == who else None))
    return out


@T('hl008')
def g008(r, k):
    tp = r.choice(S.TOPICS)
    mode, lv = _mode_lv(r)
    n = 5 if mode != 'one' else r.choice([3, 4, 5])
    mc_ids = r.sample(list(MC_F), n)
    p_ids = r.sample(list(P_ACT), r.choice([3, 4]))
    turns = _disc_turns(r, tp, mc_ids, p_ids, 'mc')
    descs = {i: MC_F[i][0] for i in MC_F}
    it = lab_item(r, turns, {i: d for i, d in descs.items() if i in mc_ids}, intro='다음은 학생 토의이다. %s' % {'one': '㉠에서 사회자의 말하기 방식으로 가장 적절한 것은?', 'not5': '사회자의 발화 ㉠~㉤에 대한 설명으로 적절하지 않은 것은?', 'ok5': '사회자의 발화 ㉠~㉤에 대한 설명으로 적절한 것은?'}[mode],
                  mode=mode, extra=[MC_NEVER] + [descs[i] for i in descs if i not in mc_ids], ref=[1], core='토의 사회자의 역할: 주제 제시 · 의견 정리 · 발언 기회 분배 · 개념 확인 · 시간 안내', lv=lv, fam='A' + mode, title='토의')
    if it is None: return None
    return it


@T('hl009')
def g009(r, k):
    tp = r.choice(S.TOPICS)
    mode, lv = _mode_lv(r)
    if mode == 'one':
        p_ids = r.sample(list(P_ACT), r.choice([3, 4, 5]))
    else:
        p_ids = r.sample(list(P_ACT), 5) + r.sample(list(P_ACT), 1)
        p_ids = list(dict.fromkeys(p_ids))
        if len(p_ids) < 5: return None
        p_ids = p_ids[:5]
    mc_ids = r.sample(list(MC_F), 2)
    mc_ids = [m for m in mc_ids if m not in ('F5', 'F3')] or ['F1']
    turns = _disc_turns(r, tp, mc_ids, p_ids, 'p')
    descs = {i: P_ACT[i][0] for i in P_ACT}
    # 참여자 발화 가운데 같은 기능이 거듭되지 않도록 5개를 고르므로 id 별 첫 발화만 표시된다
    q = {'one': '㉠에 나타난 참여자의 말하기 방식으로 가장 적절한 것은?', 'not5': '토의 참여자의 발화 ㉠~㉤에 대한 설명으로 적절하지 않은 것은?', 'ok5': '토의 참여자의 발화 ㉠~㉤에 대한 설명으로 적절한 것은?'}[mode]
    return lab_item(r, turns, {i: descs[i] for i in p_ids}, intro='다음은 학생 토의이다. ' + q, mode=mode,
                    extra=['앞선 발언자의 의견을 그대로 반복하며 지지하고 있다.', '토의 주제와 무관한 사례를 들어 화제를 전환하고 있다.'] + [descs[i] for i in descs if i not in p_ids],
                    ref=[1], core='토의 참여자의 발언 방식: 제안 · 보완 · 한계 지적 · 공감 · 평가 · 질문', lv=lv, fam='B' + mode, title='토의')


CRIT = {'효과성': '이 방안은 문제를 얼마나 잘 해결할 수 있는가?', '실현 가능성': '이 방안을 실제로 실행할 수 있는 여건이 마련되어 있는가?', '효율성': '이 방안은 들이는 비용과 노력에 비해 얻는 성과가 큰가?', '수용성': '이 방안을 구성원들이 기꺼이 받아들일 수 있는가?', '지속 가능성': '이 방안을 오랫동안 꾸준히 이어 갈 수 있는가?'}
STAGES = [
 ('문제 확인', '{problem}이(가) 실제로 얼마나 심각한지부터 확인해 봅시다.'),
 ('원인 분석', '이런 문제가 생기는 원인이 무엇인지 따져 보면 좋겠습니다.'),
 ('해결 방안 모색', '이 문제를 해결할 수 있는 방안을 자유롭게 말씀해 주십시오.'),
 ('해결 방안 평가·선택', '제시된 방안을 효과와 실현 가능성을 기준으로 비교하여 가장 알맞은 방안을 고릅시다.'),
 ('실행 계획 수립', '선택한 방안을 누가, 언제까지 실행할지 정해 봅시다.'),
]

@T('hl010')
def g010(r, k):
    tp = r.choice(S.TOPICS)
    c = r.randrange(6)
    if c <= 2:
        i = r.randrange(5)
        line = ff(STAGES[i][1], tp)
        pre = r.choice([ff('오늘의 주제는 \'{theme}\'입니다.', tp), ff('{n}에 대해 이야기하겠습니다.', tp)])
        body = P('다음은 학생 토의이다. 밑줄 친 발화가 속하는 토의 단계로 가장 적절한 것은?') + DLG([('사회자', pre), ('사회자', U(line))])
        return mc(body, STAGES[i][0], [s[0] for j, s in enumerate(STAGES) if j != i],
                  steps=['"%s"은(는) %s 단계의 발화이다.' % (line, STAGES[i][0])] + ['토의 절차: 문제 확인 → 원인 분석 → 해결 방안 모색 → 해결 방안 평가·선택 → 실행 계획 수립'], core='토의의 절차', lv=r.choice(['하', '중']), fam='A', r=r, ref=[1], vertical=False)
    if c == 3:
        i, j = r.sample(range(3), 2)
        s = tp['solutions']
        right = josa('\'%s\'은(는) %s는 점에서 효과성이 있지만 %s는 점에서 실현 가능성이 낮아 보완이 필요하다.' % (s[i][0], s[i][1], s[i][2]))
        ws = [josa('\'%s\'은(는) %s는 점에서 효과성이 있지만 %s는 점에서 실현 가능성이 낮아 보완이 필요하다.' % (s[a][0], s[b][1], s[b][2])) for a, b in ((i, j), (j, i), (j, j))]
        ws += [josa('\'%s\'은(는) 어떤 문제도 없으므로 평가 기준을 따로 세울 필요 없이 바로 채택해야 한다.' % s[i][0])]
        body = P('다음은 해결 방안 평가표이다. 평가 내용으로 가장 적절한 것은?') + table(['해결 방안', '기대 효과', '한계'], [[s[x][0], s[x][1], s[x][2]] for x in range(3)])
        return mc(body, right, ws, steps=['표에서 "%s"의 기대 효과는 "%s", 한계는 "%s"이다.' % (s[i][0], s[i][1], s[i][2]), '다른 방안의 효과나 한계를 가져다 쓴 선택지는 표와 맞지 않는다.'], core='해결 방안 평가 기준: 효과성 · 실현 가능성 · 효율성', lv='상', fam='B', r=r, ref=[1], vertical=True)
    crit = list(CRIT.items())
    k1, d1 = r.choice(crit)
    if c == 4:
        ws = [n for n, _ in crit if n != k1]
        return mc(P('해결 방안을 평가할 때 \'%s\'을(를) 따지는 질문으로 가장 알맞은 것은?' % k1) if False else P('다음 질문이 따지고 있는 해결 방안의 평가 기준은?') + BOX([d1]), k1, ws, steps=['"%s"은(는) %s의 기준에 해당한다.' % (d1, k1)], core='해결 방안의 평가 기준: 효과성 · 실현 가능성 · 효율성 · 수용성 · 지속 가능성', lv='중', fam='C', r=r, ref=[1], vertical=False)
    ws = [d for n, d in crit if n != k1]
    return mc(P('해결 방안을 평가하는 기준 \'%s\'에 해당하는 질문은?' % k1), d1, ws, steps=['%s: %s' % (k1, d1)], core='해결 방안의 평가 기준', lv='중', fam='D', r=r, ref=[1], vertical=True)


THESES = {
 '정책': ['교복 착용을 폐지해야 한다', '야간 자율 학습을 폐지해야 한다', '학교 앞 도로의 제한 속도를 낮추어야 한다', '고등학교 수행 평가의 비율을 높여야 한다', '일회용 컵 사용을 금지해야 한다', '학생의 휴대 전화 소지를 금지해야 한다', '급식 메뉴 선정에 학생 투표를 도입해야 한다', '도서관 개방 시간을 연장해야 한다'],
 '사실': ['스마트폰 사용 시간이 늘면 학업 성적이 떨어진다', '인터넷 실명제는 악성 댓글을 줄인다', '체벌은 학생의 행동 개선에 효과가 있다', '온라인 수업은 대면 수업보다 학습 효과가 낮다', '게임은 청소년의 폭력성을 높인다', '조기 영어 교육은 외국어 능력을 높인다', '아침 식사는 집중력을 높인다'],
 '가치': ['인공지능은 인류에게 이롭다', '경쟁은 사회 발전에 도움이 된다', '소셜 미디어는 인간관계를 풍요롭게 한다', '예술은 과학보다 가치 있다', '성공에는 노력보다 재능이 중요하다', '개인의 자유는 공동체의 이익보다 우선한다', '외모는 개인의 경쟁력이다'],
}

@T('hl011')
def g011(r, k):
    c = r.randrange(8)
    if c <= 2:
        typ = r.choice(list(THESES)); others = [t for t in THESES if t != typ]
        mode = r.choice(['same', 'one'])
        if mode == 'one':
            right = r.choice(THESES[typ]); ws = r.sample(THESES[others[0]] + THESES[others[1]], 4)
            ask = '다음 중 %s 논제인 것은?' % typ
            st = ['"%s": %s' % (right, {'정책': '"~해야 한다"로 정책의 실행 여부를 다루는 정책 논제이다.', '사실': '참·거짓을 입증할 수 있는 사실 논제이다.', '가치': '옳고 그름, 좋고 나쁨을 판단하는 가치 논제이다.'}[typ])]
            return mc(P(ask), right, ws, steps=st, core='논제의 유형: 정책 · 사실 · 가치', lv='하', fam='A', r=r, ref=[2], vertical=True)
        o = r.choice(others)
        right = r.choice(THESES[o]); ws = r.sample(THESES[typ], 4)
        return mc(P('다음 중 논제의 유형이 나머지와 다른 하나는?'), right, ws, steps=['"%s"만 %s 논제이고 나머지는 %s 논제이다.' % (right, o, typ)], core='논제의 유형: 정책 · 사실 · 가치', lv='중', fam='B', r=r, ref=[2], vertical=True)
    tp = r.choice(S.TOPICS); side = r.choice(['pro', 'con'])
    feats = r.sample(['def', 'eff', 'stat', 'case', 'urg', 'opp'], 5)
    sents = []
    head = ipron(tp, side, [])
    turns = [(('찬성 측 입론' if side == 'pro' else '반대 측 입론'), head, None)]
    for f in feats:
        turns.append((None, josa(ff(IN_F[f][0 if side == 'pro' else 1], tp)), f))
    descs = {f: in_desc(f, side) for f in feats}
    mode, lv = _mode_lv(r)
    q = {'one': '㉠에 나타난 입론의 말하기 방식으로 가장 적절한 것은?', 'not5': '입론 ㉠~㉤에 대한 설명으로 적절하지 않은 것은?', 'ok5': '입론 ㉠~㉤에 대한 설명으로 적절한 것은?'}[mode]
    if mode == 'one':
        turns = [t for t in turns]
    return lab_item(r, turns, descs, intro='다음은 토론의 입론이다. ' + q, mode=mode, extra=IN_GENERIC, ref=[2], core='입론의 구성: 입장 · 개념 정의 · 근거(통계·사례) · 예상 반론 반박', lv=lv, fam='C' + mode, title='토론')


@T('hl012')
def g012(r, k):
    tp = r.choice(S.TOPICS); asked = r.choice(['pro', 'con'])
    opp = '찬성 측' if asked == 'pro' else '반대 측'
    me = '반대 측' if asked == 'pro' else '찬성 측'
    keys = ['prob', 'ev', 'src', 'case', 'def']
    turns = [('%s 입론' % opp, ipron(tp, asked, ['def', 'stat', 'case']), None)]
    qs = r.sample(keys, 5)
    for n, key in enumerate(qs):
        u = cx_utter(tp, key, asked)
        if n:
            u = u.split('말씀하셨는데, ', 1)[1]
        turns.append(('%s 반대 신문' % me, u, key))
    descs = {key: cx_desc(key, opp) for key in keys}
    mode, lv = _mode_lv(r)
    q = {'one': '㉠에 나타난 질문의 의도로 가장 적절한 것은?', 'not5': '반대 신문 ㉠~㉤에 대한 설명으로 적절하지 않은 것은?', 'ok5': '반대 신문 ㉠~㉤에 대한 설명으로 적절한 것은?'}[mode]
    return lab_item(r, turns, descs, intro='다음은 토론의 입론과 반대 신문이다. ' + q, mode=mode, extra=[
        '%s이(가) 앞서 진술한 내용을 철회하도록 요구하고 있다.' % opp, '자신의 주장을 새로운 근거로 입증하고 있다.', '토론의 논제를 다른 논제로 바꾸자고 제안하고 있다.'], ref=[3], core='반대 신문: 상대 발언을 확인한 뒤 근거의 신뢰성 · 적용 가능성 · 문제점을 질문으로 드러낸다', lv=lv, fam='D' + mode, title='토론')


@T('hl013')
def g013(r, k):
    tp = r.choice(S.TOPICS)
    c = r.randrange(6)
    if c <= 2:
        side = r.choice(['pro', 'con'])
        claim = tp['pro_claim'] if side == 'pro' else tp['con_claim']; reason = tp['pro_reason'] if side == 'pro' else tp['con_reason']
        nm = '찬성' if side == 'pro' else '반대'
        sent = '<u>㉠%s</u>. 왜냐하면 <u>㉡%s</u>이다.' % (claim, reason.replace(' 때문', '') + ' 때문' if reason.endswith('때문') else reason)
        sent = '<u>㉠%s</u>. 왜냐하면 <u>㉡%s</u>입니다.' % (claim, reason)
        body = P('다음은 %s 측 토론자의 발언이다. ㉠, ㉡의 논증상 역할로 알맞은 것은?' % nm) + '<div class="bogi"><p>%s</p></div>' % sent
        right = '㉠: 주장, ㉡: 근거'
        ws = ['㉠: 근거, ㉡: 주장', '㉠: 논제, ㉡: 주장', '㉠: 쟁점, ㉡: 근거', '㉠: 반박, ㉡: 논제']
        return mc(josa(body), right, ws, steps=['㉠은 말하는 이가 내세우는 의견이므로 주장이고, 이를 뒷받침하는 ㉡은 근거이다.'], core='논증의 구성: 주장과 근거', lv='하', fam='A', r=r, ref=[4], vertical=False)
    if c <= 4:
        claim, reason = tp['pro_claim'], tp['pro_reason']
        cr = tp['con_reason']
        body = P('다음은 학생 토론이다. 반대 측의 반박으로 가장 적절한 것은?') + DLG([('찬성 측', josa(ff('{pc}. {pr}입니다.', tp))), ('반대 측', '(반박)')])
        assert tp['con_reason'].endswith('때문')
        right = josa('찬성 측은 \'%s\'고 하셨지만, %s에 \'%s\'는 점도 함께 살펴보아야 합니다.' % (claim, tp['con_reason'], tp['con_claim']))
        ws = ['찬성 측 토론자는 평소 약속을 잘 지키지 않으므로 그 주장을 신뢰할 수 없습니다.', '많은 사람이 찬성 측과 같이 생각하므로 그 주장은 옳다고 보아야 합니다.', '지금까지 말씀하신 내용을 모두 인정하며, 우리 측 입장을 철회하겠습니다.', '그 문제와 관계없이, 다른 학교에서도 논란이 있었다는 점을 말씀드립니다.']
        return mc(body.replace('(반박)', '(    )'), right, ws, steps=['반박은 상대 주장의 문제점을 논거로 지적해야 한다.', '인신공격 · 대중 호소 · 입장 철회 · 화제 전환은 반박이 아니다.'], core='반박: 상대 주장의 근거나 결과를 논리적으로 따진다', lv='중', fam='B', r=r, ref=[3], vertical=True)
    xs = r.sample(S2.TF_DISC, 3)
    return tpl_tf(r, S2.TF_DISC, three=True, lv='중', fam='C', ref=[4], intro='토론과 논증에 대한 학습 내용이다.')


@T('hl014')
def g014(r, k):
    c = r.randrange(7)
    pool = S2.FALLACY
    names = list(S2.FALLACY_DESC)
    if c <= 2:
        s, typ = r.choice(pool)
        ws = r.sample([n for n in names if n != typ], 4)
        body = P('다음 글에 나타난 논증의 오류로 가장 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % s
        return mc(body, typ, ws, steps=['"%s"은(는) %s: %s' % (s, typ, S2.FALLACY_DESC[typ])], core='논증의 오류 유형', lv=r.choice(['하', '중']), fam='A', r=r, ref=[4], vertical=False)
    if c <= 4:
        typ = r.choice(names)
        right = r.choice([s for s, t in pool if t == typ])
        others = [(s, t) for s, t in pool if t != typ]
        ws = []
        seen = set()
        r.shuffle(others)
        for s, t in others:
            if t in seen: continue
            seen.add(t); ws.append(s)
            if len(ws) == 4: break
        if len(ws) < 4: return None
        body = P('다음 중 \'%s\'에 해당하는 것은?' % typ)
        return mc(body, right, ws, steps=['%s: %s' % (typ, S2.FALLACY_DESC[typ]), '"%s"이(가) 이에 해당한다.' % right], core=S2.FALLACY_DESC[typ], lv='중', fam='B', r=r, ref=[4], vertical=True)
    if c == 5:
        tp = r.choice(S.TOPICS); s, typ = r.choice(pool)
        body = P('다음 토론에서 밑줄 친 발언에 나타난 논증상의 문제로 가장 적절한 것은?') + DLG([('찬성 측', josa(ff('{pc}고 생각합니다. {pr}입니다.', tp))), ('반대 측', U(s))])
        ws = r.sample([n for n in names if n != typ], 4)
        return mc(body, typ, ws, steps=['밑줄 친 발언은 %s이다. %s' % (typ, S2.FALLACY_DESC[typ])], core='논증의 오류 유형', lv='상', fam='C', r=r, ref=[4], vertical=False)
    s, typ = r.choice(pool)
    wrong_desc = [S2.FALLACY_DESC[n] for n in names if n != typ]
    return mc(P('다음 발언에 나타난 논증의 오류를 설명한 것으로 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % s, S2.FALLACY_DESC[typ], r.sample(wrong_desc, 4), steps=['%s이다.' % typ], core=S2.FALLACY_DESC[typ], lv='중', fam='D', r=r, ref=[4], vertical=True)


FEAT = {
 '토의': ['공동의 문제를 협력하여 해결하는 것이 목적이다', '최선의 해결 방안을 찾기 위해 의견을 모은다', '참여자들이 협력적인 태도로 의견을 보완한다', '사회자가 의견을 정리하며 해결 방안으로 이끈다', '해결 방안의 평가 · 선택 절차를 거친다', '결론은 참여자들의 합의로 도출한다'],
 '토론': ['논제에 대한 찬성과 반대의 입장이 나뉜다', '논증과 근거로 상대를 설득하는 것이 목적이다', '상대 주장에 대한 반박이 이루어진다', '반대 신문이라는 질문 단계가 있다', '판정단이나 청중이 설득력을 판단하기도 한다', '정해진 발언 시간과 순서를 지킨다'],
}

@T('hl015')
def g015(r, k):
    c = r.randrange(5)
    a = r.choice(['토의', '토론']); b = '토론' if a == '토의' else '토의'
    if c <= 2:
        right = r.choice(FEAT[b]); ws = r.sample(FEAT[a], 4)
        return mc(P('다음 중 %s에 해당하지 않는 설명은?' % a), right, ws, steps=['"%s"는 %s의 특징이다.' % (right, b)] + ['"%s"는 %s의 특징이다.' % (w, a) for w in ws[:2]], core='토의: 협력적 문제 해결 / 토론: 논증을 통한 설득', lv='하' if c == 0 else '중', fam='A', r=r, ref=[1], vertical=True)
    if c == 3:
        right = r.choice(FEAT[a]); ws = r.sample(FEAT[b], 4)
        return mc(P('다음 중 %s의 특징으로 알맞은 것은?' % a), right, ws, steps=['"%s"는 %s의 특징이다.' % (right, a)] + ['"%s"는 %s의 특징이다.' % (w, b) for w in ws[:2]], core='토의: 협력적 문제 해결 / 토론: 논증을 통한 설득', lv='하', fam='B', r=r, ref=[1], vertical=True)
    return tpl_tf(r, S2.TF_DISC, three=True, lv='상', fam='C', ref=[1], intro='토의와 토론에 대한 학습 내용이다.')


REB = {
 'rep': ('자료의 조사 대상이 한정되어 있어 결과를 일반화하기 어렵다고 지적하고 있다.', '{st0}은(는) 일부 학생만을 대상으로 한 것이어서 전체의 의견으로 보기 어렵습니다.'),
 'inv': ('상대가 제시한 수치를 다른 관점에서 해석하여 반박하고 있다.', '{st1}이(가) {sv}%라는 것은 거꾸로 {inv}%는 그렇지 않다는 뜻이기도 합니다.'),
 'rel': ('자료가 상대의 주장을 직접 뒷받침하지 못한다고 지적하고 있다.', '그 수치만으로는 \'{pc}\'는 주장이 입증된다고 보기 어렵습니다.'),
 'cnt': ('상대와 다른 전문가의 견해를 제시하여 반박하고 있다.', '그러나 {ex}은(는) 이와 다르게 보고 있습니다.'),
 'cmp': ('상대 우려를 인정하면서 보완책을 제시하여 재반박하고 있다.', '그 우려는 타당하지만, {s1}을(를) 함께 시행하면 보완할 수 있습니다.'),
}

@T('hl016')
def g016(r, k):
    tp = r.choice(S.TOPICS)
    mode, lv = _mode_lv(r)
    ids = list(REB)
    # 반박 5개를 이어 붙여 ㉠~㉤ 로 표시
    turns = [('찬성 측', josa(ff('{st0}에 따르면 {st1}이(가) {sv}%입니다. 그러므로 {pc}고 주장합니다.', tp)), None)]
    for i in r.sample(ids, 5):
        t = ff(REB[i][1], tp, inv=100 - tp['stat'][2])
        turns.append(('반대 측', josa(t), i))
    descs = {i: REB[i][0] for i in ids}
    q = {'one': '㉠에서 반대 측이 자료를 활용한 방식으로 가장 적절한 것은?', 'not5': '반대 측의 반박 ㉠~㉤에 대한 설명으로 적절하지 않은 것은?', 'ok5': '반대 측의 반박 ㉠~㉤에 대한 설명으로 적절한 것은?'}[mode]
    return lab_item(r, turns, descs, intro='다음은 학생 토론이다. ' + q, mode=mode, extra=['상대가 제시한 자료의 출처를 밝히지 않았다고 비판하고 있다.', '자신의 입장을 철회하고 상대의 자료를 수용하고 있다.', '자료를 인용하지 않고 자신의 경험만으로 주장을 펴고 있다.'], ref=[3], core='자료 활용과 반박: 대표성 · 해석 · 관련성 · 다른 자료 · 재반박', lv=lv, fam='E' + mode, title='토론')
