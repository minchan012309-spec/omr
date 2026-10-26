# -*- coding: utf-8 -*-
"""화법 문제 엔진: 주제(TOPICS)와 발표 기법(TECH)으로 발표문·토의·토론·협상 대본을 조립한다."""
import random
from hllib import *
import kb_speech as S

def fill(tmpl, tp):
    st = tp['stat']
    return josa(tmpl.format(n=tp['name'], t=tp['thing'], st0=st[0], st1=st[1], sv=st[2], ex=tp['expert'], pc=tp['pro_claim'], cc=tp['con_claim'],
                            tn=tp['term'][0], td=tp['term'][1], eg=tp['example']))

def build_script(r, tp, ids):
    """ids: 기법 id 목록 → (문장 목록 [(기법, 문장)], 발표문 html)"""
    order = {'도입': 0, '전개': 1, '정리': 2}
    ids = sorted(ids, key=lambda i: (order[S.TECH[i][2]], r.random()))
    sents = []
    for i in ids:
        sents.append((i, fill(r.choice(S.TECH[i][3]), tp)))
    return sents

def script_html(sents, labels=None):
    """발표문 상자. labels: {문장 인덱스: '㉠'} 이면 밑줄과 기호를 붙인다."""
    labels = labels or {}
    parts = []
    for k, (i, s) in enumerate(sents):
        if k in labels:
            parts.append('%s<u>%s</u>' % (labels[k], s))
        else:
            parts.append(s)
    return '<div class="bogi"><p>%s</p></div>' % ' '.join(parts)

def pick_ids(r, n, need_stage=True):
    """도입 1~2, 전개 n-?, 정리 0~1 이 골고루 들어가는 기법 id 집합"""
    ids = []
    intro = r.sample(S.TECH_STAGE['도입'], r.choice([1, 2]))
    end = r.sample(S.TECH_STAGE['정리'], 1) if r.random() < .6 else []
    rest = n - len(intro) - len(end)
    mid = r.sample(S.TECH_STAGE['전개'], max(1, rest))
    ids = intro + mid + end
    return ids[:max(n, 4)]


# ---------------------------------------------------------------- 토의
def sol(tp, i):
    return tp['solutions'][i]

def ff(tmpl, tp, **kw):
    st = tp['stat']
    d = dict(n=tp['name'], t=tp['thing'], problem=tp['problem'], theme=tp['theme_q'], st0=st[0], st1=st[1], sv=st[2], tn=tp['term'][0], td=tp['term'][1],
             ex=tp['expert'], eg=tp['example'], pc=tp['pro_claim'], cc=tp['con_claim'], pr=tp['pro_reason'], cr=tp['con_reason'], pol=tp['policy'])
    for i, s in enumerate(tp['solutions']):
        d['s%d' % i] = s[0]; d['e%d' % i] = s[1]; d['l%d' % i] = s[2]
    d.update(kw)
    return josa(tmpl.format(**d))

# 사회자 기능: 설명 → 문장 틀
MC_F = {
 'F1': ('토의의 배경과 주제를 제시하며 토의를 시작한다.', '최근 {problem}이(가) 생기고 있습니다. 그래서 오늘은 \'{theme}\'라는 주제로 토의하겠습니다.'),
 'F2': ('토의자들의 발언 내용을 정리하며 토의를 이어 간다.', '지금까지 {s0}, {s1}, {s2} 이렇게 세 가지 의견이 제시되었습니다.'),
 'F3': ('토의자들의 발언 순서를 조정하여 발언 기회를 분배한다.', '먼저 학생 1이 의견을 말씀해 주시고, 이어서 학생 3이 말씀해 주십시오.'),
 'F4': ('토의 결과를 활용할 계획을 밝히고 토의 참여를 독려한다.', '오늘 나온 의견은 정리하여 학교에 건의하려고 합니다. 적극적으로 의견을 말씀해 주십시오.'),
 'F5': ('토의자에게 질문하여 발언에 사용된 용어의 개념을 확인한다.', '{tn}(이)란 무엇인가요?'),
 'F6': ('토의 시간을 안내하여 토의가 효율적으로 진행되게 한다.', '오늘 토의는 20분 동안 진행하겠습니다.'),
}
MC_NEVER = '토의자의 의견에 자신의 입장을 밝히며 한쪽 의견을 지지한다.'

# 참여자 행위: 설명 → 문장 틀 (화자, 대상 방안 번호)
P_ACT = {
 'PROP': ('대안을 제시할 때 조사 내용을 근거로 삼아 자신의 의견을 피력하고 있다.', '{problem}을(를) 해결하기 위해 {s0}을(를) 제안합니다. {st0}에 따르면 {st1}이(가) {sv}%로 나타났기 때문입니다.'),
 'LIMIT': ('앞선 대안이 지닌 현실적인 어려움을 지적하고 있다.', '{s0}은(는) 효과가 있겠지만 {l0}는 점이 걱정됩니다.'),
 'AUG': ('자료를 찾아 알게 된 정보를 바탕으로 앞선 대안을 보강하고 있다.', '{s1}은(는) {e1}는 점에서도 효과가 있습니다. 자료를 찾아보니 {eg}이(가) 있었습니다. 이런 점도 함께 고려하면 좋겠습니다.'),
 'EMP': ('앞선 대안의 취지에 공감하며 자신의 대안을 제시하고 있다.', '앞서 말씀하신 {s0}의 취지에는 동의합니다. 다만 {l0}는 문제가 있으니 {s2}은(는) 어떨까요?'),
 'EVAL': ('앞선 대안을 효율성의 측면에서 긍정적으로 평가하고 있다.', '좋은 의견입니다. {s2}은(는) {e2}는 점에서 노력과 비용이 적게 들면서도 문제를 개선할 수 있는 방법이네요.'),
 'ASK': ('앞선 대안의 구체적인 실행 방법을 질문하고 있다.', '{s1}은(는) 구체적으로 어떻게 실행할 수 있을까요?'),
}

def discussion(r, tp, mc_ids, p_ids):
    """사회자 기능 id(MC_F)와 참여자 행위 id(P_ACT) 순서대로 대본(turns) 생성. 반환: turns=[(화자, 문장, 종류, id)]"""
    turns = []
    if 'F1' in mc_ids: turns.append(('사회자', ff(MC_F['F1'][1], tp), 'mc', 'F1'))
    if 'F6' in mc_ids: turns.append(('사회자', ff(MC_F['F6'][1], tp), 'mc', 'F6'))
    if 'F4' in mc_ids: turns.append(('사회자', ff(MC_F['F4'][1], tp), 'mc', 'F4'))
    names = ['학생 1', '학생 2', '학생 3', '학생 4']
    for k, a in enumerate(p_ids):
        sp = names[k % 4]
        turns.append((sp, ff(P_ACT[a][1], tp), 'p', a))
        if k == 0 and 'F5' in mc_ids:
            turns[-1] = (sp, turns[-1][1] + ' 특히 ' + ff('{tn}이(가)', tp) + ' 중요하다고 봅니다.', 'p', a)
            turns.append(('사회자', ff(MC_F['F5'][1], tp), 'mc', 'F5'))
            turns.append((sp, ff('{td}입니다.', tp), 'x', 'ans'))
        if k == 1 and 'F3' in mc_ids:
            turns.append(('사회자', ff(MC_F['F3'][1], tp), 'mc', 'F3'))
    if 'F2' in mc_ids: turns.append(('사회자', ff(MC_F['F2'][1], tp), 'mc', 'F2'))
    return turns

def turns_html(turns, labels=None):
    labels = labels or {}
    out = []
    for k, (sp, s, kind, i) in enumerate(turns):
        lab = labels.get(k)
        if lab:
            out.append('<p><b>%s</b>: %s<u>%s</u></p>' % (sp, lab, s))
        else:
            out.append('<p><b>%s</b>: %s</p>' % (sp, s))
    return '<div class="bogi">' + ''.join(out) + '</div>'


# ---------------------------------------------------------------- 토론
IN_F = {  # 입론 특징: (찬성 문장 틀, 반대 문장 틀, 설명(-고 있다))
 'def': ('여기서 {tn}(이)란 {td}을(를) 뜻합니다.', '여기서 {tn}(이)란 {td}을(를) 뜻합니다.', '용어의 개념을 정의하여 논의의 범위를 정하고 있다.'),
 'eff': ('{pc}고 봅니다. {pr}입니다.', '{cc}고 봅니다. {cr}입니다.', None),
 'stat': ('{st0}에 따르면 {st1}이(가) {sv}%입니다.', '{st0}에 따르면 {st1}이(가) {sv}%입니다.', '통계 자료를 근거로 제시하고 있다.'),
 'case': ('실제로 {eg}이(가) 있습니다.', '실제로 {eg}이(가) 있습니다.', '구체적인 사례를 근거로 제시하고 있다.'),
 'urg': ('{problem}은(는) 더 이상 미룰 수 없는 문제입니다.', '{problem}은(는) 신중하게 접근해야 하는 문제입니다.', None),
 'opp': ('반대 측에서는 {cc}고 하시겠지만, 이는 충분히 보완할 수 있습니다.', '찬성 측에서는 {pc}고 하시겠지만, 그 효과는 일시적일 수 있습니다.', '상대 측의 예상 반론을 언급하며 반박하고 있다.'),
}
def in_desc(f, side):
    if f == 'eff': return '논제를 실현했을 때의 기대 효과를 근거로 주장하고 있다.' if side == 'pro' else '논제를 실현했을 때 생길 부정적인 측면을 근거로 반대하고 있다.'
    if f == 'urg': return '문제 해결의 시급성을 강조하고 있다.' if side == 'pro' else '문제에 신중하게 접근해야 한다는 점을 강조하고 있다.'
    return IN_F[f][2]
IN_GENERIC = ['상대 측에게 질문하여 근거의 출처를 요구하고 있다.', '자신의 주장을 철회하고 상대의 의견을 수용하고 있다.', '논제와 관련 없는 다른 화제로 논의를 전환하고 있다.', '상대 측 발언 속의 모순을 지적하고 있다.', '다른 나라의 사례만을 근거로 논제의 범위를 넓히고 있다.']

def ipron(tp, side, feats):
    """입론 본문: 입장 문장 + 특징 문장들"""
    pol = ff('{pol}', tp)
    head = ('저희는 \'%s\'라는 논제에 찬성합니다.' % pol) if side == 'pro' else ('저희는 \'%s\'라는 논제에 반대합니다.' % pol)
    body = [head]
    for f in feats:
        body.append(ff(IN_F[f][0 if side == 'pro' else 1], tp))
    return ' '.join(josa(x) for x in body)

# 반대 신문
CX = {
 'prob': ('{cc}는 문제가 생길 수 있지 않을까요?', '해당 방식을 도입할 경우 생길 문제점을 제기하고 있다.'),
 'ev': ('{st0}의 결과가 전체를 대표한다고 볼 수 있습니까?', '근거로 제시된 자료의 신뢰성(대표성)에 의문을 제기하고 있다.'),
 'src': ('{ex}의 견해라고 하셨는데, 그 출처를 밝혀 주실 수 있습니까?', '근거로 제시된 견해의 출처를 제시할 것을 요구하고 있다.'),
 'case': ('{eg}이(가) 우리 학교의 상황에도 그대로 적용될 수 있습니까?', '제시된 사례가 논제 상황에 적합한지에 대해 의문을 제기하고 있다.'),
 'def': ('{tn}(이)란 {td}을(를) 뜻한다고 하셨는데, 그 범위는 어디까지입니까?', '용어의 범위를 구체적으로 밝힐 것을 요구하고 있다.'),
}
def cx_utter(tp, key, opp_side='pro'):
    claim = tp['pro_claim'] if opp_side == 'pro' else tp['con_claim']
    conf = ff("'{c}'고 말씀하셨는데,".replace('{c}', claim), tp)
    q = ff(CX[key][0], tp)
    if key == 'prob' and opp_side == 'con':
        q = ff('그 방식을 도입하지 않으면 {problem}이(가) 계속되지 않을까요?', tp)
    return conf + ' ' + q
def cx_desc(key, opp='상대 측'):
    return '%s이(가) 앞서 진술한 내용의 일부를 확인하고, %s' % (opp, CX[key][1])
