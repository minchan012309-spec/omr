# -*- coding: utf-8 -*-
"""Ⅱ-C 단어의 관계 (hl050~hl055)"""
import itertools
from hllib import *
import kb_word as W
import kb_word2 as W2
from kb_word2 import DICT, TF_WORD
from orth_gen import tpl_tf


def senses(word):
    """[(묶음 번호, 묶음 안 뜻 번호, 뜻풀이, 예문들)]"""
    out = []
    for gi, g in enumerate(DICT[word]):
        for si, (gl, ex) in enumerate(g):
            out.append((gi, si, gl, ex))
    return out

def entry_box(word):
    gs = DICT[word]
    lines = []
    for gi, g in enumerate(gs):
        label = word + (str(gi + 1) if len(gs) > 1 else '')
        if len(g) == 1:
            lines.append('<b>%s</b> %s' % (label, g[0][0]))
        else:
            lines.append('<b>%s</b> ' % label + ' '.join('「%d」%s' % (i + 1, gl) for i, (gl, _) in enumerate(g)))
    return BOGI(lines, title='사 전', labels=None)

def under_word(sent, word):
    """예문에서 표제어를 포함한 어절을 밑줄 친다(못 찾으면 마지막 어절)."""
    import re
    stem = word[:-1] if word.endswith('다') and len(word) > 1 else word
    pat = re.compile(r'(%s[가-힣]*)' % re.escape(stem))
    m = pat.search(sent)
    if not m:
        m = re.search(r'([가-힣]+)(?=[.?!]?$)', sent)
        if not m: return sent
    s, e = m.span(1)
    return sent[:s] + '<u>' + sent[s:e] + '</u>' + sent[e:]

POLYW = [w for w in W.POLY if len(W.POLY[w]) >= 2]
MULTI = [w for w in DICT if len(DICT[w]) >= 3]       # 동음이의 3묶음 이상
GLOSS_ALL = [g for w in DICT for gi, g_ in enumerate(DICT[w]) for g, _ in g_]

def _sent_pool(word):
    out = []
    for gi, si, gl, ex in senses(word):
        for e in ex: out.append((gi, si, gl, e))
    return out

@T('hl050')
def g050(r, k):
    c = r.randrange(8)
    if c <= 1:
        w = r.choice([x for x in DICT if len(senses(x)) >= 3])
        sp = _sent_pool(w); gi, si, gl, e = r.choice(sp)
        others = [s[2] for s in senses(w) if s[2] != gl]
        extra = [g for g in GLOSS_ALL if g != gl and g not in others and g not in [x for x in others]]
        r.shuffle(extra)
        wrongs = others[:4]
        while len(wrongs) < 4: wrongs.append(extra.pop())
        body = P("〈보기〉의 사전 정보를 참고할 때, 밑줄 친 '%s'의 의미로 알맞은 것은?" % w) + entry_box(w) + '<div class="bogi"><p>%s</p></div>' % under_word(e, w)
        return mc(body, gl, wrongs[:4], steps=["문장 '%s'에서 '%s'은(는) '%s'의 뜻으로 쓰였다." % (e, w, gl)], core='사전의 뜻풀이로 의미를 판단한다.', lv='하' if c == 0 else '중', fam='A', r=r, ref=[1], vertical=True)
    if c == 2:
        # 두 용례의 관계
        w = r.choice([x for x in DICT])
        sp = _sent_pool(w)
        if len(sp) < 2: return None
        a, b = r.sample(sp, 2)
        if a[3] == b[3]: return None
        same_group = a[0] == b[0]
        if same_group and a[1] == b[1]: return None
        right = '다의 관계(중심적 의미와 주변적 의미의 관계)' if same_group else '동음이의 관계'
        opts = ['다의 관계(중심적 의미와 주변적 의미의 관계)', '동음이의 관계', '유의 관계', '반의 관계', '상하 관계']
        body = P("㉠, ㉡의 밑줄 친 '%s'의 의미 관계로 알맞은 것은?" % w) + BOX(['㉠ ' + under_word(a[3], w), '㉡ ' + under_word(b[3], w)])
        why = ("두 뜻이 하나의 표제어 안에서 의미가 확장된 관계이므로 다의 관계이다." if same_group else "두 뜻이 서로 연관이 없는 별개의 단어이므로 동음이의 관계이다.")
        return mc(body, right, [o for o in opts if o != right], steps=["㉠: %s" % a[2], "㉡: %s" % b[2], why], core='다의어와 동음이의어의 구별', lv='중', fam='B', r=r, ref=[1], vertical=True)
    if c == 3:
        w = r.choice(POLYW)
        sp = _sent_pool(w)
        cen = [x for x in sp if x[0] == 0 and x[1] == 0]; non = [x for x in sp if not (x[0] == 0 and x[1] == 0) and x[0] == 0]
        if not cen or len(non) < 4: return None
        a = r.choice(cen); ws = r.sample(non, 4)
        body = P("밑줄 친 '%s'이(가) 중심적 의미로 쓰인 것은?" % w)
        right = under_word(a[3], w)
        return mc(body, right, [under_word(x[3], w) for x in ws], steps=["'%s'의 중심적 의미는 '%s'이다." % (w, senses(w)[0][2])] + ["'%s': 주변적 의미 '%s'" % (x[3], x[2]) for x in ws], core='다의어의 중심적 의미와 주변적 의미', lv='중', fam='C', r=r, ref=[1], vertical=True)
    if c == 4:
        # 사전 번호 대응 ㉠~㉤
        w = r.choice([x for x in DICT if len(senses(x)) >= 4])
        ss = senses(w)
        tgt = r.choice(ss)
        sp = _sent_pool(w)
        cen = [x for x in sp if (x[0], x[1]) == (tgt[0], tgt[1])]
        non = [x for x in sp if (x[0], x[1]) != (tgt[0], tgt[1])]
        if not cen or len(non) < 4: return None
        a = r.choice(cen); ws = r.sample(non, 4)
        label = w + (str(tgt[0] + 1) if len(DICT[w]) > 1 else '') + (' 「%d」' % (tgt[1] + 1) if len(DICT[w][tgt[0]]) > 1 else '')
        body = P("〈보기〉의 '%s'의 뜻으로 쓰인 것은?" % label) + entry_box(w)
        return mc(body, under_word(a[3], w), [under_word(x[3], w) for x in ws], steps=["'%s'의 뜻풀이: %s" % (label, tgt[2])] + ["'%s'은(는) '%s'의 뜻이다." % (x[3], x[2]) for x in ws], core='사전 뜻풀이와 용례 대응', lv='상', fam='D', r=r, ref=[1], vertical=True)
    if c == 5:
        # 같은 단어(같은 묶음)
        w = r.choice([x for x in DICT if len(DICT[x]) >= 3])
        gs = DICT[w]
        gi = r.randrange(len(gs))
        mine = [(gi, s, g, e) for s, (g, ex) in enumerate(gs[gi]) for e in ex]
        if len(mine) < 2: return None
        a, b = r.sample(mine, 2)
        non = [(gj, s, g, e) for gj, grp in enumerate(gs) if gj != gi for s, (g, ex) in enumerate(grp) for e in ex]
        if len(non) < 4: return None
        ws = r.sample(non, 4)
        body = P("〈보기〉의 밑줄 친 '%s'과(와) 같은 단어(동음이의어가 아닌 같은 뜻의 말)로 쓰인 것은?" % w) + BOX([under_word(a[3], w)], title='보 기')
        return mc(body, under_word(b[3], w), [under_word(x[3], w) for x in ws], steps=["〈보기〉의 '%s'은(는) '%s'의 뜻이고 정답도 같은 뜻이다." % (w, a[2])] + ["'%s'은(는) '%s'의 뜻으로 다른 동음이의어이다." % (x[3], x[2]) for x in ws], core='동음이의어 구별', lv='상', fam='E', r=r, ref=[1], vertical=True)
    if c == 6: return tpl_tf(r, TF_WORD, r.choice(['ok', 'bad']), lv='중', fam='F', ref=[1])
    # 눈·다리: 다의 vs 동음
    w = r.choice(['눈', '다리'])
    gs = DICT[w]
    ref_e = r.choice([e for s, (g, ex) in enumerate(gs[0]) for e in ex])
    other = [e for g, ex in gs[1] for e in ex]
    same = [e for s, (g, ex) in enumerate(gs[0]) for e in ex if e != ref_e]
    if len(same) < 3: return None
    right = under_word(r.choice(other), w)
    ws = [under_word(x, w) for x in r.sample(same, min(4, len(same)))]
    if len(ws) < 4: return None
    return mc(P("〈보기〉의 밑줄 친 '%s'과(와) 동음이의 관계에 있는 것은?" % w) + BOX([under_word(ref_e, w)], title='보 기'), right, ws, steps=["동음이의어는 소리는 같지만 뜻이 연관되지 않는 별개의 단어이다.", "정답의 '%s'은(는) 다른 표제어(별개의 단어)이다." % w], core='다의어와 동음이의어', lv='상', fam='G', r=r, ref=[1], vertical=True)


@T('hl051')
def g051(r, k):
    c = r.randrange(7)
    if c <= 1:
        d = r.choice(W.SYNS)
        right = r.choice(d['ok'])
        wrongs = list(d['no'])
        pool = [w for e in W.SYNS for w in e['ok'] if w not in d['ok'] and w not in d['no']]
        r.shuffle(pool)
        for p in pool:
            if len(wrongs) >= 4: break
            if p not in wrongs: wrongs.append(p)
        body = P('다음 문장의 빈칸에 들어갈 말로 가장 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % d['s'].replace('__', '(      )')
        return mc(body, right, wrongs[:4], steps=[d['why']], core='유의어의 쓰임', lv='중', fam='A', r=r, ref=[2], vertical=False)
    if c == 2:
        right = r.choice(W.SYNP)
        pairs = [('%s – %s' % p, '유의') for p in r.sample(W.SYNP, 4)]
        a = r.choice(W.ANT)
        ws = ['%s – %s' % (x[0], x[1]) for x in r.sample(W.ANT, 4)]
        return mc(P('다음 중 두 단어가 유의 관계인 것은?'), '%s – %s' % right, ws, steps=["'%s'과(와) '%s'은(는) 의미가 매우 비슷한 유의 관계이다." % right] + ['%s은(는) 반의 관계이다.' % w for w in ws], core='유의 관계', lv='하', fam='B', r=r, ref=[2], vertical=False)
    if c == 3:
        a = r.choice(W.ANT); ys = r.sample(W.SYNP, 4)
        return mc(P('다음 중 두 단어가 유의 관계가 아닌 것은?'), '%s – %s' % (a[0], a[1]), ['%s – %s' % y for y in ys], steps=["'%s – %s'은(는) 반의 관계이다." % (a[0], a[1])] + ["'%s – %s'은(는) 유의 관계이다." % y for y in ys], core='유의 관계', lv='중', fam='C', r=r, ref=[2], vertical=False)
    if c == 4:
        base, syns = r.choice(W.SYN_SETS)
        s = r.choice(syns)
        ants = [a[1] if a[0] == base else a[0] for a in W.ANT if base in a[:2]] or []
        wrong_pool = [x for x in ['먹다', '가다', '보다', '짓다', '놓다', '던지다', '붙이다', '쓰다', '높다', '넓다'] if x != base]
        right = r.choice(wrong_pool)
        ws = [x for x in r.sample(syns, min(4, len(syns)))]
        pool = [x for _, ss in W.SYN_SETS for x in ss if x not in ws and x not in syns]
        r.shuffle(pool)
        while len(ws) < 4: ws.append(pool.pop())
        return mc(P("다음 중 '%s'의 유의어가 아닌 것은?" % base), right, [w.split('(')[0] for w in ws[:4]], steps=["'%s'은(는) '%s'과(와) 뜻이 다른 말이다." % (right, base)], core='유의어', lv='중', fam='D', r=r, ref=[2], vertical=False) if False else _syn_not(r)
    if c == 5: return tpl_tf(r, TF_WORD, r.choice(['ok', 'bad']), lv='중', fam='E', ref=[2])
    # 높임 유의어
    ex = [('할머니께서 진지를 (      ).', '잡수신다', ['먹는다', '먹으신다', '마신다', '드린다']), ('아버지께서 방에서 (      ).', '주무신다', ['잔다', '누우신다', '자신다', '쉰다']),
          ('할아버지께서는 지금 댁에 (      ).', '계신다', ['있다', '있으신다', '살신다', '머문다']), ('선생님께서 편지를 읽고 (      ).', '계신다', ['있다', '있으시다', '있다가', '읽는다']),
          ('어머니께서 편찮아서 병원에 (      ).', '가셨다', ['갔다', '가신다', '오셨다', '돌아갔다'])]
    a = r.choice(ex)
    return mc(P('다음 문장의 빈칸에 들어갈 말로 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % a[0], a[1], a[2], steps=['높임의 대상에 맞는 유의어(높임 표현)를 골라야 한다.'], core='유의어와 높임 표현', lv='하', fam='F', r=r, ref=[2], vertical=False)


def _syn_not(r):
    base, syns = r.choice([x for x in W.SYN_SETS if len(x[1]) >= 2])
    ok = [s.split('(')[0] for s in syns]
    wrong_pool = [x for x in ['먹다', '가다', '보다', '짓다', '놓다', '던지다', '붙이다', '쓰다', '높다', '넓다', '느리다', '멀다', '자다'] if x != base]
    right = r.choice(wrong_pool)
    ws = list(ok)
    pool = [x.split('(')[0] for _, ss in W.SYN_SETS for x in ss if x.split('(')[0] not in ws]
    r.shuffle(pool)
    while len(ws) < 4 and pool: ws.append(pool.pop())
    if len(ws) < 4: return None
    return mc(P("다음 중 '%s'의 유의어가 아닌 것은?" % base), right, ws[:4], steps=["'%s'은(는) '%s'과(와) 뜻이 다른 말이다." % (right, base)] + ["'%s'은(는) '%s'의 유의어이다." % (w, base) for w in ws[:4]], core='유의어', lv='중', fam='D', r=r, ref=[2], vertical=False)


ANTN = {'상보': '상보 반의어', '등급': '등급 반의어', '방향': '방향 반의어'}
ANTD = {'상보': '상보 반의어: 두 단어의 영역이 배타적이어서 중간 지대가 없다.', '등급': '등급 반의어: 정도나 등급을 나타내며 중간 단계가 있다.', '방향': '방향 반의어: 방향이나 관계상 서로 반대 위치에 있다.'}
ANT_CAND = [('소년', '소녀', True, "'사람'과 '어림'은 공통이고 '성별'만 다르다."), ('총각', '처녀', True, "'사람'과 '미혼'은 공통이고 '성별'만 다르다."), ('아저씨', '아주머니', True, "'사람'과 '어른'은 공통이고 '성별'만 다르다."),
            ('아이', '어른', True, "'사람'은 공통이고 '나이'만 다르다."), ('소년', '할머니', False, "'성별'과 '나이' 두 자질이 모두 다르다."), ('삼촌', '이모', False, "'성별'과 '친족 계통' 두 자질이 모두 다르다."),
            ('남자 아이', '여자 어른', False, "'성별'과 '나이' 두 자질이 모두 다르다."), ('총각', '할머니', False, "'성별'과 '나이'·'혼인 여부' 등 여러 자질이 다르다."), ('소녀', '할아버지', False, "'성별'과 '나이' 두 자질이 모두 다르다.")]

@T('hl052')
def g052(r, k):
    c = r.randrange(8)
    if c <= 1:
        a, b, t = r.choice(W.ANT)
        names = ['상보 반의어', '등급 반의어', '방향 반의어', '유의 관계', '상하 관계']
        return mc(P("'%s'과(와) '%s'의 의미 관계로 알맞은 것은?" % (a, b)), ANTN[t], [n for n in names if n != ANTN[t]], steps=[ANTD[t]], core=ANTD[t], lv='중', fam='A', r=r, ref=[2], vertical=False)
    if c == 2:
        t = r.choice(list(ANTN)); xs = [x for x in W.ANT if x[2] == t]; ys = [x for x in W.ANT if x[2] != t]
        right = r.choice(xs); ws = r.sample(ys, 4)
        return mc(P('다음 중 %s의 예로 적절한 것은?' % ANTN[t]), '%s – %s' % (right[0], right[1]), ['%s – %s' % (w[0], w[1]) for w in ws], steps=['%s – %s: %s' % (right[0], right[1], ANTD[t])] + ['%s – %s: %s' % (w[0], w[1], ANTD[w[2]]) for w in ws], core=ANTD[t], lv='중', fam='B', r=r, ref=[2], vertical=False)
    if c == 3:
        t = r.choice(list(ANTN)); xs = [x for x in W.ANT if x[2] == t]; ys = [x for x in W.ANT if x[2] != t]
        right = r.choice(ys); ws = r.sample(xs, 4)
        return mc(P('다음 중 %s에 해당하지 않는 것은?' % ANTN[t]), '%s – %s' % (right[0], right[1]), ['%s – %s' % (w[0], w[1]) for w in ws], steps=['%s – %s은(는) %s이다.' % (right[0], right[1], ANTN[right[2]])] + ['%s – %s은(는) %s이다.' % (w[0], w[1], ANTN[t]) for w in ws], core=ANTD[t], lv='상', fam='C', r=r, ref=[2], vertical=False)
    if c == 4:
        w = r.choice(list(W.ANT_MULTI))
        cs = W.ANT_MULTI[w]
        a = r.choice(cs)
        pool = []
        for x in cs:
            if x[1] not in pool: pool.append(x[1])
        extra = ['닫다', '다물다', '넣다', '벗기다', '매다', '끼우다', '풀다', '신다', '입다', '쓰다', '끼다']
        r.shuffle(extra)
        for e in extra:
            if len(pool) >= 5: break
            if e not in pool and e != w: pool.append(e)
        right = a[1]
        ws = [x for x in pool if x != right][:4]
        if len(ws) < 4: return None
        return mc(P("'%s %s'의 '%s'과(와) 반의 관계에 있는 말로 알맞은 것은?" % (a[0], w, w)), right, ws, steps=["하나의 단어는 문맥에 따라 여러 반의어를 가질 수 있다. '%s %s'의 반의어는 '%s'이다." % (a[0], w, right)], core='여러 개의 반의어를 가진 단어', lv='상', fam='D', r=r, ref=[2], vertical=False)
    if c == 5:
        a = r.choice(ANT_CAND)
        ok = [x for x in ANT_CAND if x[2]]; no = [x for x in ANT_CAND if not x[2]]
        if r.random() < .5:
            right = r.choice(ok); ws = r.sample(no, 4)
            body = P('다음 중 두 단어가 반의 관계인 것은?')
            return mc(body, '%s – %s' % (right[0], right[1]), ['%s – %s' % (w[0], w[1]) for w in ws], steps=['%s – %s: %s' % (right[0], right[1], right[3])] + ['%s – %s: %s' % (w[0], w[1], w[3]) for w in ws], core='반의어는 하나의 의미 자질만 다르다.', lv='상', fam='E', r=r, ref=[2], vertical=False)
        right = r.choice(no); ws = r.sample(ok, 4)
        body = P('다음 중 두 단어가 반의 관계가 아닌 것은?')
        return mc(body, '%s – %s' % (right[0], right[1]), ['%s – %s' % (w[0], w[1]) for w in ws], steps=['%s – %s: %s' % (right[0], right[1], right[3])] + ['%s – %s: %s' % (w[0], w[1], w[3]) for w in ws], core='반의어는 하나의 의미 자질만 다르다.', lv='상', fam='F', r=r, ref=[2], vertical=False)
    if c == 6:
        stm = []
        for a, b, t in r.sample(W.ANT, 3):
            truth = r.random() < .5
            n = t if truth else r.choice([x for x in ANTN if x != t])
            stm.append(("'%s'과(와) '%s'은(는) %s이다." % (a, b, ANTN[n]), truth, ANTD[t]))
        return bogi('반의 관계에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='G', r=r, ref=[2], ask='')
    return tpl_tf(r, TF_WORD, r.choice(['ok', 'bad']), lv='중', fam='H', ref=[2])


@T('hl053')
def g053(r, k):
    H = W.HIER
    c = r.randrange(7)
    if c == 0:
        up, mid, lows = r.choice(H)
        a = r.choice(lows)
        others = [x for x in H if x[1] != mid]
        ws = [r.choice(x[2]) for x in r.sample(others, 4)]
        names = ['동물 – 식물']
        return mc(P("'%s'의 상위어로 알맞은 것은?" % a), mid, [x[1] for x in r.sample(others, 4)], steps=["'%s'은(는) '%s'에 포함되는 하위어이다." % (a, mid)], core='상하 관계', lv='하', fam='A', r=r, ref=[2], vertical=False)
    if c == 1:
        up, mid, lows = r.choice([x for x in H if len(x[2]) >= 4])
        ws = r.sample(lows, 4)
        others = [x for x in H if x[1] != mid]
        right = r.choice(r.choice(others)[2])
        return mc(P("다음 중 '%s'의 하위어가 아닌 것은?" % mid), right, ws, steps=["'%s'은(는) '%s'에 포함되지 않는다." % (right, mid)] + ["'%s'은(는) '%s'의 하위어이다." % (w, mid) for w in ws], core='하위어와 상위어', lv='중', fam='B', r=r, ref=[2], vertical=False)
    if c == 2:
        right = r.choice(H); ws = r.sample([x for x in H if x[1] != right[1]], 4)
        a = r.choice(right[2])
        return mc(P('다음 중 두 단어가 상하 관계인 것은?'), '%s – %s' % (right[1], a), ['%s – %s' % (w[1], r.choice(r.choice([x for x in H if x[1] != w[1]])[2])) for w in ws], steps=["'%s'은(는) '%s'의 하위어이다." % (a, right[1])], core='상하 관계', lv='중', fam='C', r=r, ref=[2], vertical=False)
    if c == 3:
        # 상대적 관계
        up, mid, lows = r.choice(H); low = r.choice(lows)
        right = "'%s'은(는) '%s'의 하위어이면서 '%s'의 상위어이다." % (mid, up, low)
        wrongs = ["'%s'은(는) '%s'의 상위어이면서 '%s'의 하위어이다." % (mid, up, low), "'%s'은(는) '%s'과(와) '%s'의 하위어이다." % (mid, up, low), "'%s'은(는) '%s'과(와) '%s'의 상위어이다." % (mid, up, low), "'%s'과(와) '%s'은(는) 의미상 관련이 없다." % (up, mid)]
        return mc(P("'%s – %s – %s'의 관계에 대한 설명으로 옳은 것은?" % (up, mid, low)), right, wrongs, steps=['상위어와 하위어의 관계는 상대적이다. 중간 단계의 말은 위에 대해서는 하위어, 아래에 대해서는 상위어가 된다.'], core='상하 관계의 상대성', lv='상', fam='D', r=r, ref=[2], vertical=True)
    if c == 4:
        up, mid, lows = r.choice(H)
        a = r.choice(lows)
        wrongs = [x[1] for x in r.sample([x for x in H if x[1] != mid], 4)]
        # 가장 포괄적인 말(최상위)
        return mc(P("'%s'과(와) '%s' 중 더 포괄적인 의미를 가진 상위어를 포함하는 설명으로, '%s'의 최상위 단어로 알맞은 것은?" % (mid, a, a)), up, [x[0] for x in r.sample([y for y in H if y[0] != up], 4)] if len({y[0] for y in H if y[0] != up}) >= 4 else wrongs, steps=["'%s ⊃ %s ⊃ %s' 순으로 포함된다." % (up, mid, a)], core='상하 관계', lv='상', fam='E', r=r, ref=[2], vertical=False)
    if c == 5: return tpl_tf(r, TF_WORD, r.choice(['ok', 'bad']), lv='중', fam='F', ref=[2])
    xs = r.sample(H, 3); stm = []
    for up, mid, lows in xs:
        truth = r.random() < .5
        low = r.choice(lows)
        txt = "'%s'은(는) '%s'의 하위어이다." % (low, mid) if truth else "'%s'은(는) '%s'의 상위어이다." % (low, mid)
        stm.append((txt, truth, "'%s'은(는) '%s'의 하위어이고 '%s'은(는) 그 상위어이다." % (low, mid, mid)))
    return bogi('상하 관계에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='G', r=r, ref=[2], ask='')


REL_DEF = {
 '유의 관계': '서로 다른 단어가 매우 비슷한 의미를 지니고 있는 관계',
 '상보 반의 관계': '두 단어의 개념 영역이 서로 배타적이어서 중간 지대가 없는 반의 관계',
 '등급 반의 관계': '정도나 등급을 나타내며 두 단어 사이에 중간 단계가 있는 반의 관계',
 '방향 반의 관계': '방향이나 관계상 서로 반대되는 위치를 나타내는 반의 관계',
 '상하 관계': '한 단어가 의미상 다른 단어를 포함하거나 다른 단어에 포함되는 관계',
}
def rel_pair(r, rel):
    if rel == '유의 관계': a = r.choice(W.SYNP); return '%s – %s' % a
    if rel == '상하 관계':
        up, mid, lows = r.choice(W.HIER); return '%s – %s' % (mid, r.choice(lows))
    t = {'상보 반의 관계': '상보', '등급 반의 관계': '등급', '방향 반의 관계': '방향'}[rel]
    a = r.choice([x for x in W.ANT if x[2] == t]); return '%s – %s' % (a[0], a[1])

@T('hl054')
def g054(r, k):
    c = r.randrange(5)
    rels = list(REL_DEF)
    if c <= 1:
        rel = r.choice(rels)
        box = BOGI(['%s: %s.' % (rel, REL_DEF[rel])], title='보 기', labels=None)
        ps = {x: rel_pair(r, x) for x in rels}
        if len(set(ps.values())) < 5: return None
        return mc(P('〈보기〉의 설명에 해당하는 단어 쌍으로 알맞은 것은?') + box, ps[rel], [v for x, v in ps.items() if x != rel], steps=['%s: %s' % (rel, ps[rel])] + ['%s은(는) %s이다.' % (v, x) for x, v in ps.items() if x != rel], core=REL_DEF[rel], lv='중', fam='A', r=r, ref=[2], vertical=False)
    if c == 2:
        rel = r.choice(rels); pair = rel_pair(r, rel)
        box = BOGI(['%s: %s.' % (x, REL_DEF[x]) for x in rels], title='보 기', labels=None)
        wrongs = [x for x in rels if x != rel]
        return mc(P("〈보기〉를 참고할 때, '%s'의 의미 관계로 가장 적절한 것은?" % pair) + box, rel, wrongs, steps=["'%s'은(는) %s이다: %s" % (pair, rel, REL_DEF[rel])], core=REL_DEF[rel], lv='중', fam='B', r=r, ref=[2], vertical=False)
    if c == 3:
        # ㉠~㉤ 짝 중 관계가 다른 하나
        rel = r.choice(rels)
        same = []
        for _ in range(8):
            p = rel_pair(r, rel)
            if p not in same: same.append(p)
            if len(same) == 4: break
        if len(same) < 4: return None
        other = r.choice([x for x in rels if x != rel]); op = rel_pair(r, other)
        return mc(P('다음 단어 쌍 중 의미 관계가 나머지와 다른 것은?'), op, same, steps=['%s은(는) %s이다.' % (op, other)] + ['%s은(는) %s이다.' % (p, rel) for p in same], core='단어의 의미 관계 구별', lv='상', fam='C', r=r, ref=[2], vertical=False)
    xs = r.sample(rels, 3)
    stm = []
    for x in xs:
        p = rel_pair(r, x); truth = r.random() < .5
        n = x if truth else r.choice([y for y in rels if y != x])
        stm.append(("'%s'은(는) %s이다." % (p, n), truth, "'%s'은(는) %s이다: %s" % (p, x, REL_DEF[x])))
    return bogi('단어의 의미 관계에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='최', fam='D', r=r, ref=[2], ask='')


WFK = {'파생(접두)': '접두사가 결합한 파생어', '파생(접미)': '접미사가 결합한 파생어', '합성(대등)': '대등 합성어', '합성(종속)': '종속 합성어', '합성(융합)': '융합 합성어'}
WFD = {'파생(접두)': '접두사가 어근 앞에 붙어 만들어진 파생어이다.', '파생(접미)': '어근 뒤에 접미사가 붙어 만들어진 파생어이다.', '합성(대등)': '두 어근이 대등한 관계로 결합한 합성어이다.', '합성(종속)': '앞 어근이 뒤 어근을 꾸미는 종속 관계의 합성어이다.', '합성(융합)': '두 어근이 결합하면서 새로운 의미가 만들어진 융합 합성어이다.'}

def wf_pool(kind_prefix):
    return [d for d in W.WF if d['kind'].startswith(kind_prefix)]

@T('hl055')
def g055(r, k):
    c = r.randrange(9)
    der = wf_pool('파생'); com = wf_pool('합성')
    def st(d): return "'%s'(%s): %s" % (d['w'], d['parts'], WFD[d['kind']])
    if c <= 1:
        a = r.choice(der); ws = r.sample(com, 4)
        return mc(P('다음 중 파생어인 것은?'), a['w'], [w['w'] for w in ws], steps=[st(a)] + [st(w) for w in ws], core='파생어: 어근+접사 / 합성어: 어근+어근', lv='하', fam='A', r=r, ref=[3], vertical=False)
    if c == 2:
        a = r.choice(com); ws = r.sample(der, 4)
        return mc(P('다음 중 합성어인 것은?'), a['w'], [w['w'] for w in ws], steps=[st(a)] + [st(w) for w in ws], core='파생어: 어근+접사 / 합성어: 어근+어근', lv='하', fam='B', r=r, ref=[3], vertical=False)
    if c == 3:
        pre = wf_pool('파생(접두)'); suf = wf_pool('파생(접미)')
        if r.random() < .5:
            a = r.choice(pre); ws = r.sample(suf, 4); nm = '접두사가 쓰인 파생어'
        else:
            a = r.choice(suf); ws = r.sample(pre, 4); nm = '접미사가 쓰인 파생어'
        return mc(P('다음 중 %s인 것은?' % nm), a['w'], [w['w'] for w in ws], steps=[st(a)] + [st(w) for w in ws], core='접두사 파생어와 접미사 파생어', lv='중', fam='C', r=r, ref=[3], vertical=False)
    if c == 4:
        eq = wf_pool('합성(대등)'); sub = wf_pool('합성(종속)')
        if r.random() < .5:
            a = r.choice(eq); ws = r.sample(sub, 4); nm = '대등 합성어'
        else:
            a = r.choice(sub); ws = r.sample(eq, 4); nm = '종속 합성어'
        return mc(P('다음 중 %s인 것은?' % nm), a['w'], [w['w'] for w in ws], steps=[st(a)] + [st(w) for w in ws], core='합성어의 유형', lv='상', fam='D', r=r, ref=[3], vertical=False)
    if c == 5:
        a = r.choice(der + com); ws = r.sample([x for x in W.WF if x['kind'] != a['kind']], 4)
        return mc(P("다음 중 '%s'과(와) 단어 형성 방식이 같은 것은?" % a['w']), r.choice([x for x in W.WF if x['kind'] == a['kind'] and x['w'] != a['w']])['w'], [w['w'] for w in ws], steps=[st(a)], core='단어 형성법', lv='상', fam='E', r=r, ref=[3], vertical=False)
    if c == 6:
        stm = []
        for d in r.sample(W.WF, 3):
            truth = r.random() < .5
            n = d['kind'] if truth else r.choice([x for x in WFK if x != d['kind']])
            stm.append(("'%s'은(는) %s이다." % (d['w'], WFK[n]), truth, st(d)))
        return bogi('단어의 짜임에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='F', r=r, ref=[3], ask='')
    if c == 7:
        a = r.choice(W.WF)
        names = [WFK[x] for x in WFK]
        return mc(P("'%s'의 짜임으로 가장 적절한 것은?" % a['w']), WFK[a['kind']], [n for n in names if n != WFK[a['kind']]], steps=[st(a)], core='단어의 짜임', lv='중', fam='G', r=r, ref=[3], vertical=False)
    # 어근 + 접사 분석
    # 선택지는 모두 같은 단어를 달리 분석한 것(합성어로 봄 · 어근과 접사를 바꿈 · 단일어로 봄 · 접사 갈래를 잘못 봄)
    a = r.choice(der)
    ps = [x for x in a['parts'].split('+') if x != '-다']
    if len(ps) != 2: return None
    q = lambda t: "'%s'" % t
    if a['kind'] == '파생(접두)':
        pre, rt = ps; p0 = pre.rstrip('-'); r0 = rt.rstrip('-')
        right = '접두사 %s + 어근 %s' % (q(pre), q(rt))
        ws = ['어근 %s + 어근 %s' % (q(p0), q(rt)), '어근 %s + 접미사 %s' % (q(p0 + ('-' if rt.endswith('-') else '')), q('-' + r0)), '어근 %s 하나(접사 없음)' % q(p0 + r0 + ('-' if rt.endswith('-') else '')), '접미사 %s + 어근 %s' % (q('-' + p0), q(rt))]
    else:
        rt, suf = ps; r0 = rt.rstrip('-'); core = suf.strip('-'); tr = '-' if suf.endswith('-') else ''
        right = '어근 %s + 접미사 %s' % (q(rt), q(suf))
        ws = ['어근 %s + 어근 %s' % (q(rt), q(core + tr)), '접두사 %s + 어근 %s' % (q(r0 + '-'), q(core + tr)), '어근 %s 하나(접사 없음)' % q(r0 + core + tr), '어근 %s + 접두사 %s' % (q(rt), q(core + '-'))]
    return mc(P("'%s'을(를) 어근과 접사로 분석한 것으로 알맞은 것은?" % a['w']), right, ws, steps=[st(a)], core='파생어의 분석', lv='중', fam='H', r=r, ref=[3], vertical=True)
