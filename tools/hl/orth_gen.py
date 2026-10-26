# -*- coding: utf-8 -*-
"""맞춤법 문제 엔진: 지식 표(kb_orth*.py)에서 여러 형식의 문항을 만든다."""
import random
from hllib import *

class E:
    """단어 항목: ok(옳은 표기), bads(틀린 표기들), why(근거), g(묶음 이름)"""
    def __init__(self, ok, bads, why, g='', sent=None):
        self.ok, self.bads, self.why, self.g, self.sent = ok, bads, why, g, sent

def ents(rows, g=''):
    return [E(a, b, c, g) for a, b, c in rows]

RULE = {
 'dos': '제5항 한 단어 안에서 뚜렷한 까닭 없이 나는 된소리는 다음 음절의 첫소리를 된소리로 적는다. 다만 \'ㄱ, ㅂ\' 받침 뒤에서 나는 된소리는, 같은 음절이나 비슷한 음절이 겹쳐 나는 경우가 아니면 된소리로 적지 아니한다.',
 'pal': '제6항 \'ㄷ, ㅌ\' 받침 뒤에 종속적 관계를 가진 \'-이(-)\'나 \'-히-\'가 올 적에는 그 \'ㄷ, ㅌ\'이 \'ㅈ, ㅊ\'으로 소리 나더라도 \'ㄷ, ㅌ\'으로 적는다.',
 'duum': '제10~12항 한자음 \'녀, 뇨, 뉴, 니\', \'랴, 려, 례, 료, 류, 리\', \'라, 래, 로, 뢰, 루, 르\'가 단어의 첫머리에 올 적에는 두음 법칙에 따라 적는다. 단어의 첫머리 이외의 경우에는 본음대로 적는다. 접두사처럼 쓰이는 한자가 붙어서 된 말이나 합성어에서 뒷말의 첫소리가 \'ㄴ, ㄹ\' 소리로 나더라도 두음 법칙에 따라 적는다.',
 'ryul': '제11항 붙임 1 단어의 첫머리 이외의 경우에는 본음대로 적는다. 다만, 모음이나 \'ㄴ\' 받침 뒤에 이어지는 \'렬, 률\'은 \'열, 율\'로 적는다.',
 'josa': '제14항 체언은 조사와 구별하여 적는다. 제15항 용언의 어간과 어미는 구별하여 적는다.',
 'noun': '제19항 어간에 \'-이\'나 \'-음/-ㅁ\'이 붙어서 명사로 된 것은 그 어간의 원형을 밝히어 적는다. 다만, 어간의 뜻과 멀어진 것은 원형을 밝히어 적지 아니한다.',
 'botim': '제19항 붙임 어간에 \'-이\'나 \'-음\' 이외의 모음으로 시작된 접미사가 붙어서 다른 품사로 바뀐 것은 그 어간의 원형을 밝히어 적지 아니한다.',
 'myeong': '제20항 명사 뒤에 \'-이\'가 붙어서 된 말은 그 명사의 원형을 밝히어 적는다. 붙임 \'-이\' 이외의 모음으로 시작된 접미사가 붙어서 된 말은 그 명사의 원형을 밝히어 적지 아니한다.',
 'hageri': '제23항 \'-하다\'나 \'-거리다\'가 붙는 어근에 \'-이\'가 붙어서 명사가 된 것은 그 원형을 밝히어 적는다. 붙임 \'-하다\'나 \'-거리다\'가 붙을 수 없는 어근에 \'-이\'나 다른 모음으로 시작되는 접미사가 붙어서 명사가 된 것은 그 원형을 밝히어 적지 아니한다.',
 'busa': '제25항 \'-하다\'가 붙는 어근에 \'-히\'나 \'-이\'가 붙어서 부사가 되거나, 부사에 \'-이\'가 붙어서 뜻을 더하는 경우에는 그 어근이나 부사의 원형을 밝히어 적는다. 붙임 \'-하다\'가 붙지 않는 경우에는 소리대로 적는다.',
 'ihi': '제51항 부사의 끝음절이 분명히 \'이\'로만 나는 것은 \'-이\'로 적고, \'히\'로만 나거나 \'이\'나 \'히\'로 나는 것은 \'-히\'로 적는다.',
 'gap': '제27항 둘 이상의 단어가 어울리거나 접두사가 붙어서 이루어진 말은 각각 그 원형을 밝히어 적는다. 붙임 1 어원은 분명하나 소리만 특이하게 변한 것은 변한 대로 적는다. 붙임 2 어원이 분명하지 아니한 것은 원형을 밝히어 적지 아니한다.',
 'sai': '제30항 사이시옷은 (1) 순우리말로 된 합성어로서 앞말이 모음으로 끝난 경우, (2) 순우리말과 한자어로 된 합성어로서 앞말이 모음으로 끝난 경우, 뒷말의 첫소리가 된소리로 나거나 \'ㄴ\' 소리가 덧나거나 \'ㄴㄴ\' 소리가 덧나는 것에 받치어 적는다. (3) 두 음절로 된 한자어 곳간, 셋방, 숫자, 찻간, 툇간, 횟수는 사이시옷을 받치어 적는다.',
 'jun': '제35항 모음 \'ㅗ, ㅜ\'로 끝난 어간에 \'-아/-어, -았-/-었-\'이 어울려 \'ㅘ/ㅝ, ㅘㅆ/ㅝㅆ\'으로 될 적에는 준 대로 적는다. 제36항 \'ㅣ\' 뒤에 \'-어\'가 와서 \'ㅕ\'로 줄 적에는 준 대로 적는다. 제37항 \'ㅏ, ㅕ, ㅗ, ㅜ, ㅡ\'로 끝난 어간에 \'-이\'가 와서 각각 \'ㅐ, ㅖ, ㅚ, ㅟ, ㅢ\'로 줄 적에는 준 대로 적는다.',
}

def _pickn(r, pool, n):
    if len(pool) < n: return None
    return r.sample(pool, n)

def _fixline(e, w=None):
    return "'%s'(×) → '%s'(○)" % (w or e.bads[0], e.ok)

def _steps_choose(right_e, wrong_es, ok_mode=True, bad_used=None):
    st = []
    if ok_mode:
        st.append("옳은 표기는 '%s'이다. %s" % (right_e.ok, right_e.why))
        for e, w in wrong_es:
            st.append("'%s'은(는) 틀린 표기이다 → '%s'. %s" % (w, e.ok, e.why))
    else:
        w = bad_used
        st.append("'%s'은(는) 틀린 표기이다 → '%s'. %s" % (w, right_e.ok, right_e.why))
        for e in wrong_es:
            st.append("'%s'은(는) 옳은 표기이다. %s" % (e.ok, e.why))
    return st


# ---------------------------------------------------------------- 형식 A/B: 옳은(틀린) 표기 고르기
def tpl_choose(r, pool, mode='ok', rule=None, lv='중', fam='A', core='', ref=None, ask_ok=None, ask_bad=None):
    es = _pickn(r, pool, 5)
    if not es: return None
    pre = ''
    if rule and rule in RULE:
        pre = BOGI([RULE[rule]], title='규 정', labels=None)
    if mode == 'ok':
        ask = ask_ok or r.choice(['다음 중 한글 맞춤법에 맞게 표기한 것은?', '다음 중 표기가 옳은 것은?', '한글 맞춤법에 맞는 것은?'])
        if rule: ask = r.choice(['〈규정〉에 따라 바르게 표기한 것은?', '〈규정〉을 적용하여 바르게 표기한 것은?'])
        right = es[0].ok
        wrongs = []; wl = []
        for e in es[1:]:
            w = r.choice(e.bads); wrongs.append(w); wl.append((e, w))
        body = pre.replace('보 기', '규 정') + P(ask) if pre else P(ask)
        return mc(body, right, wrongs, steps=_steps_choose(es[0], wl), core=core or es[0].why, lv=lv, fam=fam, r=r, ref=ref)
    else:
        ask = ask_bad or r.choice(['다음 중 한글 맞춤법에 어긋나는 것은?', '다음 중 표기가 옳지 않은 것은?', '한글 맞춤법에 맞지 않는 것은?'])
        if rule: ask = r.choice(['〈규정〉에 따라 표기하지 않은 것은?', '〈규정〉을 잘못 적용한 것은?'])
        w = r.choice(es[0].bads)
        body = pre + P(ask) if pre else P(ask)
        return mc(body, w, [e.ok for e in es[1:]], steps=_steps_choose(es[0], es[1:], False, w), core=core or es[0].why, lv=lv, fam=fam, r=r, ref=ref)


# ---------------------------------------------------------------- 형식 C: ㄱㄴㄷ
def tpl_stmt3(r, pool, rule=None, lv='상', fam='C', ref=None, mode='spell'):
    es = _pickn(r, pool, 3)
    if not es: return None
    truth = [r.random() < .5 for _ in range(3)]
    if all(truth) or not any(truth):
        truth[r.randrange(3)] = not truth[0] if all(truth) else True
    stmts = []
    for e, t in zip(es, truth):
        w = e.ok if t else r.choice(e.bads)
        form = r.choice(['\'%s\'(으)로 적는 것이 옳다.', '\'%s\'(으)로 표기해야 한다.', '\'%s\'은(는) 바른 표기이다.'])
        stmts.append((form % w, t, ("'%s'이(가) 옳은 표기이다. %s" % (e.ok, e.why)) if t else ("'%s'은(는) 틀린 표기이다 → '%s'. %s" % (w, e.ok, e.why))))
    intro = r.choice(['한글 맞춤법에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?'])
    pre = BOGI([RULE[rule]], title='규 정', labels=None) if rule and rule in RULE else ''
    it = bogi('', stmts, pre=pre, ask=intro if not pre else '〈규정〉을 참고할 때, 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', lv=lv, fam=fam, r=r, ref=ref, core=es[0].why)
    return it


# ---------------------------------------------------------------- 형식 G: 같은 규정이 적용된 말
def tpl_same(r, groups, lv='상', fam='G', ref=None, rule=None):
    """groups: [(이름, 항목들)] — 이름이 다른 두 묶음 이상. 한 묶음에서 2개, 나머지에서 1개씩."""
    names = [g for g in groups if len(g[1]) >= 2]
    if len(names) < 1 or len(groups) < 5: return None
    gi = r.randrange(len(groups))
    gname, gpool = groups[gi]
    if len(gpool) < 2: return None
    a, b = r.sample(gpool, 2)
    others = [g for i, g in enumerate(groups) if i != gi]
    r.shuffle(others)
    wrongs = []
    for nm, pl in others[:4]:
        wrongs.append(r.choice(pl).ok)
    body = P("'%s'에 적용된 맞춤법 규정이 같은 것은?" % a.ok)
    return mc(body, b.ok, wrongs, steps=["'%s'와 '%s'는 모두 같은 규정이 적용된 말이다. %s" % (a.ok, b.ok, a.why)] + ["'%s'은(는) %s" % (w, next(e.why for nm, pl in others for e in pl if e.ok == w)) for w in wrongs], core=a.why, lv=lv, fam=fam, r=r, ref=ref)


# ---------------------------------------------------------------- 형식 L: ㉠~㉤ 중 틀린 표기 (문장 속)
def tpl_circled(r, items, mode='bad', lv='상', fam='L', ref=None, ask=None):
    """items: [(문장({0}에 단어를 넣음), ok, bad, why, 설명용 이름)] 5개를 뽑아 ㉠~㉤ 로 표시. mode bad: 틀린 것 하나를 찾는다 / ok: 바른 것 하나."""
    if len(items) < 5: return None
    xs = r.sample(items, 5)
    k = r.randrange(5)
    CIRC = '㉠㉡㉢㉣㉤'
    lines = []
    steps = []
    for i, (s, ok, bad, why, nm) in enumerate(xs):
        use_bad = (i == k) if mode == 'bad' else (i != k)
        form = bad if use_bad else ok
        lines.append('%s %s' % (CIRC[i], s.replace('{0}', '<u>%s</u>' % form)))
        if use_bad:
            steps.append('%s \'%s\'은(는) 틀렸다 → \'%s\'. %s' % (CIRC[i], form, ok, why))
        else:
            steps.append('%s \'%s\'은(는) 옳다. %s' % (CIRC[i], form, why))
    ask = ask or ('㉠~㉤ 중 밑줄 친 부분의 표기가 옳지 않은 것은?' if mode == 'bad' else '㉠~㉤ 중 밑줄 친 부분의 표기가 옳은 것은?')
    body = BOX(lines) if False else '<div class="bogi">' + ''.join('<p>%s</p>' % l for l in lines) + '</div>'
    body = P(ask) + body
    opts = ['㉠', '㉡', '㉢', '㉣', '㉤']
    right = opts[k]
    return mcs(body, [(o, i == k) for i, o in enumerate(opts)], steps=steps, core=xs[k][3], lv=lv, fam=fam, r=r, ref=ref, vertical=False)


def sent_items(rows, key='s'):
    """kb 문장 항목(dict: s, ok, bad[list], why) -> tpl_circled 용 튜플"""
    out = []
    for d in rows:
        for b in d['bad']:
            out.append((d['s'].replace('__', '{0}'), d['ok'], b, d['why'], d['ok']))
    return out


# ---------------------------------------------------------------- 형식 S: 5문장 중 옳은/틀린 것 (문장 단위)
def tpl_sent5(r, rows, mode='ok', lv='중', fam='S', ref=None, ask=None):
    rows = [d for d in rows]
    if len(rows) < 5: return None
    xs = r.sample(rows, 5)
    def fill(d, form): return d['s'].replace('__', '<u>%s</u>' % form)
    if mode == 'ok':
        opts_right = fill(xs[0], xs[0]['ok'])
        wrongs, st = [], ["옳은 문장은 \"%s\"이다. %s" % (plain(opts_right), xs[0]['why'])]
        for d in xs[1:]:
            b = r.choice(d['bad']); wrongs.append(fill(d, b))
            st.append("\"%s\"은(는) '%s'(이)가 아니라 '%s'(으)로 써야 한다. %s" % (plain(fill(d, b)), b, d['ok'], d['why']))
        ask = ask or r.choice(['밑줄 친 부분의 표기가 옳은 것은?', '다음 중 맞춤법에 맞게 쓴 문장은?'])
        return mc(P(ask), opts_right, wrongs, steps=st, core=xs[0]['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)
    else:
        b = r.choice(xs[0]['bad'])
        right = fill(xs[0], b)
        st = ["틀린 문장은 \"%s\"이다 → '%s'. %s" % (plain(right), xs[0]['ok'], xs[0]['why'])]
        wrongs = []
        for d in xs[1:]:
            wrongs.append(fill(d, d['ok']))
            st.append("\"%s\"은(는) 옳다. %s" % (plain(fill(d, d['ok'])), d['why']))
        ask = ask or r.choice(['밑줄 친 부분의 표기가 옳지 않은 것은?', '다음 중 맞춤법에 어긋난 문장은?'])
        return mc(P(ask), right, wrongs, steps=st, core=xs[0]['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)


# ---------------------------------------------------------------- 형식 T: 참/거짓 진술 은행
def tpl_tf(r, bank, mode='ok', lv='중', fam='T', ref=None, ask=None, three=False, intro=''):
    """mode ok: 옳은 진술 1 + 거짓 4 / bad: 거짓 1 + 참 4 / three: ㄱㄴㄷ"""
    T_ = [x for x in bank if x[1]]; F_ = [x for x in bank if not x[1]]
    if three:
        for _ in range(8):
            xs = r.sample(bank, 3)
            if any(x[1] for x in xs) and not all(x[1] for x in xs): break
        else:
            return None
        stmts = [(x[0], x[1], x[2]) for x in xs]
        return bogi(intro, stmts, lv=lv, fam=fam, r=r, ref=ref, ask=ask or '설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?')
    if mode == 'ok':
        if len(T_) < 1 or len(F_) < 4: return None
        a = r.choice(T_); bs = r.sample(F_, 4)
        steps = ['옳은 설명: %s %s' % (a[0], a[2])] + ['옳지 않은 설명: %s %s' % (b[0], b[2]) for b in bs]
        return mc(P(intro) + P(ask or r.choice(['설명으로 옳은 것은?', '다음 중 옳은 것은?'])), a[0], [b[0] for b in bs], steps=steps, core=a[2], lv=lv, fam=fam, r=r, ref=ref, vertical=True)
    else:
        if len(F_) < 1 or len(T_) < 4: return None
        a = r.choice(F_); bs = r.sample(T_, 4)
        steps = ['옳지 않은 설명: %s %s' % (a[0], a[2])] + ['옳은 설명: %s %s' % (b[0], b[2]) for b in bs]
        return mc(P(intro) + P(ask or r.choice(['설명으로 옳지 않은 것은?', '다음 중 옳지 않은 것은?'])), a[0], [b[0] for b in bs], steps=steps, core=a[2], lv=lv, fam=fam, r=r, ref=ref, vertical=True)


# ---------------------------------------------------------------- 형식 K: 두 갈래로 분류하기
def tpl_class(r, A, B, mode='ok', lv='중', fam='K', ref=None, ask_fmt=None):
    """A, B: (설명, 항목들[E]) — 'A 에 해당하지 않는 것'(A 4개 + B 1개) 또는 'A 에 해당하는 것'(A 1 + B 4)"""
    (da, pa), (db, pb) = A, B
    if len(pa) < 4 or len(pb) < 4: return None
    if mode == 'ok':
        a = r.choice(pa); bs = r.sample(pb, 4)
        body = P('다음 중 %s에 해당하는 것은?' % da)
        st = ["'%s'은(는) %s. %s" % (a.ok, da + '에 해당한다', a.why)] + ["'%s'은(는) %s에 해당한다. %s" % (b.ok, db, b.why) for b in bs]
        return mc(body, a.ok, [b.ok for b in bs], steps=st, core=a.why, lv=lv, fam=fam, r=r, ref=ref)
    else:
        b = r.choice(pb); as_ = r.sample(pa, 4)
        body = P('다음 중 %s에 해당하지 않는 것은?' % da)
        st = ["'%s'은(는) %s에 해당한다. %s" % (b.ok, db, b.why)] + ["'%s'은(는) %s에 해당한다. %s" % (a.ok, da, a.why) for a in as_]
        return mc(body, b.ok, [a.ok for a in as_], steps=st, core=b.why, lv=lv, fam=fam, r=r, ref=ref)


# ---------------------------------------------------------------- 형식 R: 〈보기〉의 ㉠~㉢ 규정과 적용(수능형)
def tpl_label(r, rules, lv='최', fam='R', ref=None, mode='bad', title='보 기', head=''):
    """rules: [(규정 설명문, 항목들[E], 서술구)] 2~4개. 항목은 E.ok 만 쓴다.
    선택지 5개: 각 '‘단어’는 ㉠에 따라 서술구'. mode 'bad': 잘못 짝지은 것 1개를 찾는다. 'ok': 바른 것 1개."""
    CIRC = '㉠㉡㉢㉣'
    n = len(rules)
    # 5 개 진술에 쓸 (규정 인덱스, 항목)
    idx = [r.randrange(n) for _ in range(5)]
    if len(set(idx)) < 2: return None
    used, picks = set(), []
    for i in idx:
        pool = [e for e in rules[i][1] if e.ok not in used]
        if not pool: return None
        e = r.choice(pool); used.add(e.ok); picks.append((i, e))
    k = r.randrange(5)
    stm, st = [], []
    for j, (i, e) in enumerate(picks):
        truth = (j != k) if mode == 'bad' else (j == k)
        ii = i if truth else r.choice([x for x in range(n) if x != i])
        phr = rules[ii][2]
        stm.append("'%s'은(는) %s에 따라 %s" % (e.ok, CIRC[ii], phr))
        if truth:
            st.append("'%s'은(는) %s에 해당하므로 %s. 이 설명은 옳다. %s" % (e.ok, CIRC[i], rules[i][2], e.why))
        else:
            st.append("'%s'은(는) %s이(가) 아니라 %s에 해당한다. %s" % (e.ok, CIRC[ii], CIRC[i], e.why))
    box = BOGI(['%s %s' % (CIRC[i], rules[i][0]) for i in range(n)], title=title, labels=None)
    ask = '〈보기〉의 규정을 적용한 설명으로 적절하지 않은 것은?' if mode == 'bad' else '〈보기〉의 규정을 적용한 설명으로 적절한 것은?'
    body = P(head) + box + P(ask) if head else P(ask) + box
    items = [(s + '.', (j == k)) for j, s in enumerate(stm)]
    return mcs(body, items, steps=st, core=picks[k][1].why, lv=lv, fam=fam, r=r, ref=ref, vertical=True)


def tpl_jun(r, JUN, lv='상', fam='J', ref=None, mode='bad'):
    """제35~39항 준말 규정(㉠~㉣)과 적용 진술"""
    arts = ['제35항', '제35항 붙임 2', '제36항', '제37항']
    labels = {'제35항': '㉠', '제35항 붙임 1': '㉠', '제35항 붙임 2': '㉡', '제36항': '㉢', '제37항': '㉣'}
    desc = {'㉠': "'ㅗ, ㅜ'로 끝난 어간에 '-아/-어, -았-/-었-'이 어울려 'ㅘ/ㅝ, ㅘㅆ/ㅝㅆ'으로 될 적에는 준 대로 적는다.",
            '㉡': "'ㅚ' 뒤에 '-어, -었-'이 어울려 'ㅙ, ㅙㅆ'으로 될 적에도 준 대로 적는다.",
            '㉢': "'ㅣ' 뒤에 '-어'가 와서 'ㅕ'로 줄 적에는 준 대로 적는다.",
            '㉣': "'ㅏ, ㅗ, ㅜ, ㅡ'로 끝난 어간에 '-이'가 와서 각각 'ㅐ, ㅚ, ㅟ, ㅢ'로 줄 적에는 준 대로 적는다."}
    pool = [d for d in JUN if d['art'] in labels]
    if len(pool) < 5: return None
    xs = r.sample(pool, 5)
    k = r.randrange(5)
    stm, st = [], []
    for j, d in enumerate(xs):
        true_l = labels[d['art']]
        truth = (j != k) if mode == 'bad' else (j == k)
        l = true_l if truth else r.choice([x for x in '㉠㉡㉢㉣' if x != true_l])
        stm.append("'%s'을(를) '%s'(으)로 쓴 것은 %s에 따른 것이다." % (d['full'], d['short'], l))
        if truth: st.append("'%s'→'%s': %s에 해당한다(%s). 옳다." % (d['full'], d['short'], true_l, d['art']))
        else: st.append("'%s'→'%s'는 %s이(가) 아니라 %s(%s)에 따른 것이다." % (d['full'], d['short'], l, true_l, d['art']))
    box = BOGI(['%s %s' % (l, desc[l]) for l in '㉠㉡㉢㉣'], title='보 기', labels=None)
    ask = '〈보기〉의 규정을 잘못 적용한 것은?' if mode == 'bad' else '〈보기〉의 규정을 올바르게 적용한 것은?'
    items = [(s, j == k) for j, s in enumerate(stm)]
    return mcs(P(ask) + box, items, steps=st, core=xs[k]['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)


# ---------------------------------------------------------------- 띄어쓰기 형식
def tpl_space5(r, rows, mode='ok', lv='중', fam='P', ref=None, ask=None, pool_bad=None):
    """rows: dict(ok, bad[list], why). ok: 옳은 문장 1 + 틀린 문장 4 / bad: 틀린 문장 1 + 옳은 문장 4"""
    if len(rows) < 5: return None
    xs = r.sample(rows, 5)
    if mode == 'ok':
        a = xs[0]; right = a['ok']
        wrongs = [r.choice(x['bad']) for x in xs[1:]]
        st = ["옳은 문장: \"%s\" %s" % (right, a['why'])] + ["\"%s\"은(는) 띄어쓰기가 틀렸다 → \"%s\". %s" % (w, x['ok'], x['why']) for w, x in zip(wrongs, xs[1:])]
        return mc(P(ask or r.choice(['띄어쓰기가 옳은 것은?', '다음 중 띄어쓰기가 바른 문장은?'])), right, wrongs, steps=st, core=a['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)
    else:
        a = xs[0]; b = r.choice(a['bad'])
        wrongs = [x['ok'] for x in xs[1:]]
        st = ["띄어쓰기가 틀린 문장: \"%s\" → \"%s\". %s" % (b, a['ok'], a['why'])] + ["\"%s\"은(는) 옳다. %s" % (x['ok'], x['why']) for x in xs[1:]]
        return mc(P(ask or r.choice(['띄어쓰기가 옳지 않은 것은?', '다음 중 띄어쓰기가 틀린 문장은?'])), b, wrongs, steps=st, core=a['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=True)


def tpl_space_circ(r, rows, lv='상', fam='Q', ref=None, ask=None):
    """㉠~㉤ 다섯 문장 중 띄어쓰기가 틀린 것 하나"""
    if len(rows) < 5: return None
    xs = r.sample(rows, 5); k = r.randrange(5)
    lines, st = [], []
    for i, x in enumerate(xs):
        form = r.choice(x['bad']) if i == k else x['ok']
        lines.append('%s %s' % ('㉠㉡㉢㉣㉤'[i], form))
        st.append('%s %s' % ('㉠㉡㉢㉣㉤'[i], ("\"%s\"은(는) 틀렸다 → \"%s\". %s" % (form, x['ok'], x['why'])) if i == k else ("옳다. %s" % x['why'])))
    body = P(ask or '㉠~㉤ 중 띄어쓰기가 옳지 않은 것은?') + '<div class="bogi">' + ''.join('<p>%s</p>' % l for l in lines) + '</div>'
    return mcs(body, [(o, i == k) for i, o in enumerate(['㉠', '㉡', '㉢', '㉣', '㉤'])], steps=st, core=xs[k]['why'], lv=lv, fam=fam, r=r, ref=ref, vertical=False)
