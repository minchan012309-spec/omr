# -*- coding: utf-8 -*-
"""화법 지문 세트(모의고사형): 처음부터 끝까지 이어지는 한 편의 지문 + ㉠~㉤ 표시 문항 3개.

문제 은행의 화법 유형(hl001~hl022)은 대본 일부만 잘라 한 문항씩 낸다. 이 모듈은 같은 생성 엔진으로
발표·토의·토론·협상·대화·면담·기사 지문을 '온전한 한 편'으로 만들고, 그 지문의 ㉠~㉤ 표지에 대해
문항 3개(기능 하나 고르기 · 적절하지 않은 것 · 적절한 것 또는 지문에 없는 것)를 묻는다.
교재에서는 수능특강 지문처럼 지문 한 번 + 이어지는 문항으로 실린다(필기 쪽 없음).
"""
import random, hashlib
from hllib import mcs, josa, esc, plain
import build as _build
_build.load_types()
import kb_speech as S
import speech_gen as G
import types_top as TT
import types_speech_c as SC
import types_speech_b as SB

CIRC = '㉠㉡㉢㉣㉤'
ITEMS = []
SETS = []


# ------------------------------------------------------------------ 지문 조립
# spec: noun(발표·토의…), head(발문), paras[(화자|None, [(문장, id|None)])], descs, extra, conf, base, sub, ref, core, subj

def _spec_speech(r):
    tp = r.choice(S.TOPICS)
    paras, ids = TT.long_speech_paras(r, tp)
    descs = {i: S.TECH[i][0] + '.' for i in S.TECH}
    head = josa('다음은 \'%s\'에 관한 학생의 발표이다.' % tp['name'])
    return dict(key=tp['name'], noun='발표', head=head, paras=[(None, p) for p in paras], descs=descs, conf={}, sub='Ⅰ-A', base='발표의 말하기 방식 파악', ref=[3],
                core='발표의 말하기 방식: 질문 · 청중 반응 확인 · 통계 · 전문가 견해 · 개념 설명 · 사례 · 비교 · 경험 · 자료 활용 · 요약 · 당부',
                extra=['자신의 입장을 철회하고 청중의 의견을 수용하고 있다.', '청중에게 질문하지 않고 일방적으로 설명하고 있다.', '다른 발표자의 견해를 비판하며 반론을 제기하고 있다.'])


def _spec_discussion(r):
    tp = r.choice(S.TOPICS)
    mc_ids = ['F1', 'F6', 'F3', 'F5', 'F2']
    p_ids = r.sample(list(G.P_ACT), 5)
    ts = G.discussion(r, tp, mc_ids, p_ids)
    paras = []
    for sp, s, kind, i in ts:
        paras.append((sp, [(s, i if kind in ('mc', 'p') else None)]))
    descs = {i: G.MC_F[i][0] for i in G.MC_F}
    descs.update({i: G.P_ACT[i][0] for i in G.P_ACT})
    head = josa('다음은 \'%s\'에 관한 학생 토의이다.' % tp['theme_q'].rstrip('?'))
    head = '다음은 \'%s\'를 주제로 한 학생 토의이다.' % tp['theme_q'].rstrip('?')
    head = josa(head).replace('를를', '를')
    return dict(key=tp['name'], noun='토의', head=head, paras=paras, descs=descs, conf={}, sub='Ⅰ-B', base='토의 참여자의 발언 분석', ref=[1],
                core='토의 사회자의 기능(주제 제시 · 시간 안내 · 순서 조정 · 개념 확인 · 정리)과 참여자의 발언 방식(제안 · 한계 지적 · 보강 · 공감 · 평가 · 질문)',
                extra=[G.MC_NEVER, '앞선 발언자의 의견을 그대로 반복하며 지지하고 있다.', '토의 주제와 무관한 사례를 들어 화제를 전환하고 있다.'])


def _spec_debate(r):
    tp, paras, ids, descs, speakers = TT._debate(r)
    head = '다음은 \'%s\'를 논제로 한 학생 토론이다.' % G.ff('{pol}', tp)
    return dict(key=tp['name'], noun='토론', head=josa(head), paras=list(zip(speakers, paras)), descs=descs, conf={}, sub='Ⅰ-B', base='반대 신문의 질문 의도', ref=[2, 3],
                core='입론 · 반대 신문 · 반박의 기능', extra=list(G.IN_GENERIC))


def _spec_nego(r):
    ng, paras, order, descs, speakers = TT._nego(r)
    head = josa('다음은 %s과(와) %s의 %s 사용에 관한 협상이다.' % (ng['a'], ng['b'], ng['thing']))
    return dict(key=ng['a'] + ng['b'], noun='협상', head=head, paras=list(zip(speakers, paras)), descs=descs, conf=SC.CONF19, sub='Ⅰ-C', base='협상 발화의 기능', ref=[2],
                core='협상 발화의 기능: 요구 · 이유 제시 · 이해 · 맞섬 · 절충안 · 조건부 수용 · 합의 확인', extra=list(SC.NEG_EXTRA))


def _spec_talk(r):
    tp = r.choice(S.TOPICS)
    drop = r.sample(['confirm', 'request', 'agree'], r.choice([0, 1]))
    ids = [i for i in SC.U_ORDER if i not in drop]
    A, B = r.choice([('민수', '지아'), ('서연', '준호'), ('하윤', '도현'), ('유진', '태민')])
    who = {'A': A, 'B': B}
    turns = [(A, G.ff('요즘 {problem}이(가) 고민이야. 나는 {s0}을(를) 해결 방법으로 제안하고 싶어.', tp), None)]
    for i in ids:
        sp = SC.UTT[i][2]
        if turns[-1][0] == who[sp]:
            prev = turns[-1][2]
            fl = SC.U_FILL.get(prev) if prev in SC.U_FILL else ''
            turns.append((who['B' if sp == 'A' else 'A'], G.ff(fl or '그래?', tp), None))
        turns.append((who[sp], G.ff(SC.UTT[i][1], tp), i))
    descs = {i: SC.UTT[i][0] for i in SC.UTT}
    paras = [(sp, [(s, i)]) for sp, s, i in turns]
    return dict(key=tp['name'], noun='대화', head='다음은 두 친구의 대화이다.', paras=paras, descs=descs, conf=SC.CONF17, sub='Ⅰ-C', base='대화의 흐름과 발화 의도', ref=[1],
                core='대화에서 발화의 기능: 확인 · 요청 · 동의 · 덧붙임 · 우려 · 제안',
                extra=['상대의 말을 부정하며 자신의 입장을 고집하고 있다.', '화제를 바꾸어 대화를 마무리하고 있다.', '자신의 경험을 길게 이야기하며 상대의 말을 끊고 있다.'])


def _spec_interview(r):
    it = r.choice(SC.INT)
    paras = []
    for i in SC.IORDER:
        paras.append(('학생', [(josa(SC.IQ[i][1].format(**it)), i)]))
        if SC.IANS[i]:
            paras.append((it['job'], [(josa(SC.IANS[i].format(**it)), None)]))
    descs = {i: SC.IQ[i][0] for i in SC.IQ}
    head = josa('다음은 학생이 %s을(를) 면담한 내용이다.' % it['job'])
    return dict(key=it['job'], noun='면담', head=head, paras=paras, descs=descs, conf=SC.CONF21, sub='Ⅰ-C', base='면담·인터뷰의 질문 전략', ref=[3],
                core='면담의 질문 전략: 개방형 · 폐쇄형 · 꼬리 질문 · 내용 확인 · 마무리',
                extra=['면담 대상자의 답변을 반박하며 자신의 의견을 길게 주장하고 있다.', '면담 주제와 관련 없는 개인적인 화제로 분위기를 바꾸고 있다.', '면담 대상자의 답변을 듣지 않고 준비한 질문만 이어 가고 있다.'])


def _spec_article(r):
    tp = r.choice([t for t in S.TOPICS if t['name'] in SC.ART_TOPIC])
    j = SC.ART_TOPIC[tp['name']]; sj, ej = tp['solutions'][j][0], tp['solutions'][j][1]
    sents = {i: (G.ff(SC.ART[i][1], tp, sj=sj, ej=ej), i) for i in SC.AORDER}
    paras = [(None, [sents['head']]), (None, [sents['lead'], sents['problem']]), (None, [sents['quote'], sents['case']]), (None, [sents['plan']])]
    descs = {i: SC.ART[i][0] for i in SC.ART}
    return dict(key=tp['name'], noun='기사', head='다음은 학교 신문 기사이다.', paras=paras, descs=descs, conf=SC.CONF22, sub='Ⅰ-C', base='매체 자료의 작성과 활용', ref=[3],
                core='기사문: 제목 · 핵심 내용 앞세우기 · 조사 결과 · 인용 · 사례 · 후속 계획',
                extra=['필자의 개인적인 감정을 드러내어 독자의 공감을 유도하고 있다.', '출처를 밝히지 않고 소문을 사실처럼 전달하고 있다.', '독자의 질문에 답하는 형식으로 내용을 전개하고 있다.'])


# ------------------------------------------------------------------ 문항 조립
def _ids_in(spec):
    used = []
    for sp, ps in spec['paras']:
        for t, i in ps:
            if i is not None and i in spec['descs'] and i not in used: used.append(i)
    return used


def _render_passage(spec, lab, nq):
    out = ['<p class="hd"><b>[1~%d]</b> %s 물음에 답하시오.</p>' % (nq, esc(spec['head']))]
    seen = set()
    for sp, ps in spec['paras']:
        parts = []
        for t, i in ps:
            if i is not None and i in lab and i not in seen:
                seen.add(i); parts.append('%s<u>%s</u>' % (lab[i], t))
            else:
                parts.append(t)
        pre = ('<b>%s</b> : ' % sp) if sp else ''
        out.append('<p>%s%s</p>' % (pre, ' '.join(parts)))
    return ''.join(out)


def _q(r, spec, kind, pick, order, used):
    """문항 하나. 반환 (stem, opts_items, steps, lv)  opts_items=[(선택지, 정답여부)]"""
    descs, conf, extra = spec['descs'], spec['conf'], spec['extra']
    C = CIRC

    def okd(i, d):
        return d != descs[i] and d not in {descs[c] for c in conf.get(i, ()) if c in descs}
    unused = list(dict.fromkeys([descs[x] for x in descs if x not in pick] + list(extra)))
    if kind == 'one':
        n = r.randrange(5); i = order[n]
        pool = list(dict.fromkeys([descs[x] for x in descs if x != i and okd(i, descs[x])] + [e for e in extra if okd(i, e)]))
        if len(pool) < 4: return None
        ws = r.sample(pool, 4)
        opts = [(descs[i], True)] + [(w, False) for w in ws]
        r.shuffle(opts)
        steps = ['%s에서는 %s' % (C[n], descs[i])] + ['"%s" — %s의 기능과 맞지 않는다.' % (w.rstrip('.'), C[n]) for w in ws[:2]]
        return '%s에 대한 설명으로 가장 적절한 것은?' % C[n], opts, steps, '중'
    if kind in ('not5', 'ok5'):
        bad = r.randrange(5)
        opts, steps_bad, steps_ok = [], [], []
        if kind == 'not5':
            cs = [u for u in unused if okd(order[bad], u)]
            if not cs: return None
            for n, i in enumerate(order):
                if n == bad:
                    d = r.choice(cs); opts.append(('%s: %s' % (C[n], d), True))
                    steps_bad.append('%s: 이 부분의 실제 기능은 「%s」이므로 제시된 설명은 적절하지 않다.' % (C[n], descs[i].rstrip('.')))
                else:
                    opts.append(('%s: %s' % (C[n], descs[i]), False)); steps_ok.append('%s: 적절한 설명이다.' % C[n])
            return '㉠~㉤에 대한 설명으로 적절하지 않은 것은?', opts, steps_bad + steps_ok[:3], '상'
        others = [n for n in range(5) if n != bad]
        for _ in range(60):
            ws = r.sample(unused, 4) if len(unused) >= 4 else None
            if ws and all(okd(order[n], d) for n, d in zip(others, ws)): break
        else:
            return None
        wi = 0
        for n, i in enumerate(order):
            if n == bad: opts.append(('%s: %s' % (C[n], descs[i]), True))
            else: opts.append(('%s: %s' % (C[n], ws[wi]), False)); wi += 1
        steps = ['%s: 적절한 설명이다.' % C[bad]] + ['%s: 이 부분의 실제 기능은 「%s」이므로 적절하지 않다.' % (C[n], descs[order[n]].rstrip('.')) for n in others][:3]
        return '㉠~㉤에 대한 설명으로 적절한 것은?', opts, steps, '상'
    if kind == 'unused':  # 지문에 나타나지 않은 것
        absent = [descs[x] for x in descs if x not in used]
        absent += list(extra)
        cs = [d for d in dict.fromkeys(absent) if not any(d in {descs[c] for c in conf.get(i, ()) if c in descs} for i in used)]
        if not cs or len(used) < 4: return None
        right = r.choice(cs)
        ws = [descs[i] for i in r.sample(used, 4)]
        opts = [(right, True)] + [(w, False) for w in ws]
        r.shuffle(opts)
        return '이 %s에서 확인할 수 없는 것은?' % spec['noun'], opts, ['지문에서 찾을 수 없는 것: %s' % right.rstrip('.')] + ['지문에 나타난다: %s' % w.rstrip('.') for w in ws[:2]], '상'
    return None


def build_set(r, spec, no):
    used = _ids_in(spec)
    if len(used) < 5: return None
    pick = r.sample(used, 5)
    order = [i for i in used if i in pick]
    lab = {i: CIRC[n] for n, i in enumerate(order)}
    kinds = ['one', 'not5', r.choice(['ok5', 'unused'])]
    qs = []
    for kd in kinds:
        q = None
        for _ in range(25):
            q = _q(r, spec, kd, pick, order, used)
            if q:
                it = mcs('', q[1], steps=q[2], lv=q[3], r=r)
                if it: break
            q = None
        if not q: return None
        qs.append(q)
    passage = _render_passage(spec, lab, len(qs))
    sub = spec['sub']
    grp = 'KJ-%02d' % no
    out = []
    for n, (stem, opts, steps, lv) in enumerate(qs, 1):
        ans = [i for i, o in enumerate(opts) if o[1]][0] + 1
        out.append(dict(code='KJ-%02d%d' % (no, n), sub=sub, type=spec['base'], lv=lv, src='제작 지문 · %s (모의고사형)' % spec['noun'],
                        body='<p>%s</p>' % esc(stem), opts=[o for o, _ in opts], ans=ans, exp=steps, passage=passage if n == 1 else passage, grp=grp,
                        ref=spec['ref'], core=spec['core'], vertical=True))
    return out


# 종류별 세트 수 (발표 · 토의 · 토론 · 협상 · 대화 · 면담 · 기사)
PLAN = [(_spec_speech, 5), (_spec_discussion, 5), (_spec_debate, 5), (_spec_nego, 5), (_spec_talk, 3), (_spec_interview, 3), (_spec_article, 3)]


def _make():
    no = 0
    for fn, cnt in PLAN:
        seen = set(); made = 0; k = 0
        while made < cnt and k < 400:
            k += 1
            seed = int(hashlib.md5(('set|%s|%d' % (fn.__name__, k)).encode()).hexdigest()[:8], 16)
            r = random.Random(seed)
            try:
                spec = fn(r)
            except AssertionError:
                continue
            if spec is None or spec['key'] in seen: continue
            res = build_set(r, spec, no + 1)
            if not res: continue
            seen.add(spec['key']); no += 1; made += 1
            ITEMS.extend(res)
            SETS.append((no, spec['noun'], spec['key']))


_make()

if __name__ == '__main__':
    import re
    for n, noun, key in SETS: print(n, noun, key)
    print(len(ITEMS))
    d = ITEMS[0]
    print(re.sub(r'<[^>]+>', ' ', d['passage'])[:1200])
    for d in ITEMS[:3]:
        print(d['code'], re.sub(r'<[^>]+>', ' ', d['body']), d['opts'], d['ans'], d['exp'])
