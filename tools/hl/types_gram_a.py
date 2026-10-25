"""Ⅱ-A 문장 성분과 문장의 짜임 (hl023~hl034)"""
from hllib import *
from ann import Ann
from gram_gen import *
import kb_gram_a as G
import kb_tf
from orth_gen import tpl_tf
ROLE = {'주': '주어', '서': '서술어', '목': '목적어', '보': '보어', '관': '관형어', '부': '부사어', '필': '부사어', '독': '독립어'}
ROLES7 = ['주어', '서술어', '목적어', '보어', '관형어', '부사어', '독립어']
RDESC = {'주어': '주어: 서술어의 동작·상태·성질의 주체이다.', '서술어': '서술어: 주어의 동작·상태·성질을 풀이한다.', '목적어': '목적어: 타동사가 나타내는 동작의 대상이다.', '보어': "보어: '되다·아니다' 앞에 오는 '이/가'가 붙은 성분이다.", '관형어': '관형어: 체언을 꾸며 준다.', '부사어': '부사어: 주로 용언을 꾸며 주거나 서술어가 요구하는 성분이다.', '독립어': '독립어: 다른 성분과 직접 관련이 없다.'}

def rname(code):
    return ROLE[code.split(':')[0]]

def by_role(sents, fn=None):
    """{역할명: [(Ann, 인덱스)]}"""
    d = {}
    for a in sents:
        for i, t, c in a.segs:
            if fn and (not fn(c)):
                continue
            d.setdefault(rname(c), []).append((a, i))
    return d
SENT = G.SENT
BYR = by_role(SENT)
SEN5 = [a for a in SENT if len(a.segs) >= 5]
SEN4 = [a for a in SENT if len(a.segs) >= 4]

@T('hl023')
def g023(r, k):
    c = r.randrange(6)
    if c <= 1:
        a = r.choice(SENT)
        i, t, code = r.choice(a.segs)
        rn = rname(code)
        return t_single(r, a, i, ROLES7, rn, '밑줄 친 부분의 문장 성분은?', ["'%s': %s" % (t, RDESC[rn])] + ([] if code.split(':')[0] != '필' else ['서술어가 요구하는 필수적 부사어이다.']), '하', 'A', [1], RDESC[rn])
    if c == 2:
        return _t1role(r, '중', 'B')
    if c == 3:
        return _t1role(r, '상', 'C')
    if c == 4:
        a = r.choice(SEN5)
        idxs = [i for i, _, _ in a.segs][:5]
        want = r.choice(['주어', '목적어', '서술어', '관형어', '부사어', '보어'])
        ks = [n for n, i in enumerate(idxs) if rname(a.toks[i][2]) == want]
        if len(ks) != 1:
            return None
        return t_circ(r, a, idxs, "다음 문장에서 ㉠~㉤ 중 '%s'에 해당하는 것은?" % want, ks[0], ["'%s'은(는) %s" % (a.toks[idxs[ks[0]]][1], RDESC[want])] + ["%s '%s'은(는) %s" % (CIRC[n], a.toks[i][1], rname(a.toks[i][2])) for n, i in enumerate(idxs) if n != ks[0]], '중', 'D', [1], RDESC[want])
    a = r.choice(SEN5)
    idxs = [i for i, _, _ in a.segs][:5]

    def lf(code):
        rn = rname(code)
        return ('%s이다.' % rn if rn != '서술어' else '서술어이다.', ['%s이다.' % x for x in ROLES7 if x != rn])
    return tf_stmts(r, a, idxs, lf, '㉠~㉤의 문장 성분에 대한 설명으로 옳지 않은 것은?', 'bad', '상', 'E', [1], core='문장 성분을 정확히 구분한다.')

def _t1role(r, lv, fam):
    pools = BYR
    target = r.choice(['목적어', '주어', '보어', '관형어', '부사어', '서술어'])
    grp = r.random() < 0.3
    if grp:
        P1 = {'주성분': sum((pools[x] for x in ['주어', '서술어', '목적어', '보어']), []), '부속 성분': pools['관형어'] + pools['부사어'], '독립 성분': pools['독립어']}
        t = r.choice(['주성분', '부속 성분'])
        return t1(r, P1, t, '밑줄 친 부분이 %s인 것은?' % t, {'주성분': '주성분: 문장의 핵심 골격(주어·서술어·목적어·보어)', '부속 성분': '부속 성분: 관형어·부사어', '독립 성분': '독립 성분: 독립어'}, lv, fam, [1])
    return t1(r, pools, target, "밑줄 친 부분이 '%s'인 것은?" % target, RDESC, lv, fam, [1])

@T('hl024')
def g024(r, k):
    P3 = by_role(SENT, lambda c: c.split(':')[0] in ('주', '목', '보', '필', '부'))
    c = r.randrange(6)
    if c <= 1:
        return t1(r, P3, '보어', "밑줄 친 부분이 '보어'인 것은?", RDESC, '중', 'A', [1])
    if c == 2:
        return t1(r, P3, '목적어', "밑줄 친 부분이 '목적어'인 것은?", RDESC, '하', 'B', [1])
    if c == 3:
        return t1(r, P3, '주어', "밑줄 친 부분이 '주어'인 것은?", RDESC, '하', 'C', [1])
    if c == 4:
        P4 = by_role(SENT, lambda c: c.split(':')[0] in ('주', '목', '보', '필'))
        return tpl_odd(r, P3)
    return tpl_tf(r, kb_tf_ga(), 'ok' if r.random() < 0.5 else 'bad', lv='중', fam='T', ref=[1])

def kb_tf_ga():
    return G.TF_GA

def tpl_odd(r, pools):
    """네 개는 같은 성분, 하나만 다른 성분 → 다른 하나 찾기"""
    same = r.choice(['주어', '목적어', '보어', '관형어', '부사어'])
    diff = r.choice([x for x in ['주어', '목적어', '보어', '관형어', '부사어', '서술어'] if x != same])
    if len(pools.get(same, [])) < 4 or not pools.get(diff):
        return None
    xs = r.sample(pools[same], 4)
    if len({a.s for a, _ in xs}) < 4:
        return None
    a, i = r.choice(pools[diff])
    if a.s in {x.s for x, _ in xs}:
        return None
    wrongs = [opt(x, j) for x, j in xs]
    right = opt(a, i)
    st = ["'%s': %s이다(다른 하나)." % (a.toks[i][1], diff)] + ["'%s': %s이다." % (x.toks[j][1], same) for x, j in xs]
    return mc(P('밑줄 친 부분의 문장 성분이 나머지 넷과 다른 것은?'), right, wrongs, steps=st, core=RDESC[same], lv='상', fam='O', r=r, ref=[1], vertical=True)

@T('hl025')
def g025(r, k):
    c = r.randrange(7)
    P2 = by_role(SENT, lambda c: c.split(':')[0] in ('관', '부', '필', '주', '목'))
    if c == 0:
        return t1(r, P2, '관형어', "밑줄 친 부분이 '관형어'인 것은?", RDESC, '하', 'A', [1])
    if c == 1:
        return t1(r, P2, '부사어', "밑줄 친 부분이 '부사어'인 것은?", RDESC, '하', 'B', [1])
    det = {}
    DD = {'관:사': '관형사가 그대로 관형어가 된 것', '관:의': "체언에 관형격 조사 '의'가 붙은 관형어", '관:형': '용언의 관형사형이 관형어가 된 것', '부:사': '부사가 그대로 부사어가 된 것', '부:조': '체언에 부사격 조사가 붙은 부사어', '부:어': '용언의 부사형이 부사어가 된 것', '부:문': '문장 전체를 꾸미는 문장 부사어', '부:접': '접속 부사어', '필:조': '체언+부사격 조사로 된 필수적 부사어', '필:어': '용언의 부사형으로 된 필수적 부사어'}
    for a in SENT:
        for i, t, code in a.segs:
            if code in DD:
                det.setdefault(code, []).append((a, i))
    if c == 2:
        return _t1det(r, det, DD, ['관:사', '관:의', '관:형'], '관형어', '중', 'C')
    if c == 3:
        return _t1det(r, det, DD, ['부:사', '부:조', '부:어'], '부사어', '중', 'D')
    if c == 4:
        return _t1det(r, det, DD, ['부:문', '부:사', '부:조', '부:접'], '부사어', '상', 'E')
    if c == 5:
        return tpl_odd(r, P2)
    a = r.choice([x for x in SENT if any((c_ == '부:문' for _, _, c_ in x.segs))])
    i = [i for i, _, c_ in a.segs if c_ == '부:문'][0]
    names = ['문장 전체를 꾸미는 문장 부사어', '용언만 꾸미는 성분 부사어', '체언을 꾸미는 관형어', '주어를 꾸미는 관형어', '서술어를 요구하는 필수적 부사어']
    return t_single(r, a, i, names, names[0], '밑줄 친 부분에 대한 설명으로 가장 적절한 것은?', ['문장 전체를 꾸미는 문장 부사어이다.'], '상', 'F', [1], '문장 부사어')

def _t1det(r, det, DD, codes, role, lv, fam):
    avail = [c for c in codes if c in det]
    if len(avail) < 2:
        return None
    t = r.choice(avail)
    pools = {c: det[c] for c in avail}
    names = {'관:사': '관형사', '관:의': "체언+'의'", '관:형': '용언의 관형사형', '부:사': '부사', '부:조': '체언+부사격 조사', '부:어': '용언의 부사형', '부:문': '문장 부사어', '부:접': '접속 부사어'}
    return t1(r, pools, t, '밑줄 친 %s가 %s로 실현된 것은?' % (role, names[t]), DD, lv, fam, [1])

@T('hl026')
def g026(r, k):
    c = r.randrange(6)
    PD = by_role(SENT)
    if c == 0:
        return t1(r, PD, '독립어', "밑줄 친 부분이 '독립어'인 것은?", RDESC, '하', 'A', [1])
    if c == 1:
        req = sum((PD[x] for x in ['주어', '목적어', '보어']), [])
        P1 = {'필수 성분': req, '수의 성분': PD['관형어'] + PD['독립어'] + [(a, i) for a in SENT for i, t, c_ in a.segs if c_.startswith('부:')]}
        t = r.choice(['필수 성분', '수의 성분'])
        return t1(r, P1, t, '밑줄 친 부분이 %s인 것은?' % t, {'필수 성분': '필수 성분: 문장이 성립하는 데 반드시 필요한 성분', '수의 성분': '수의 성분: 생략해도 문장이 성립하는 성분(관형어·수의적 부사어·독립어)'}, '중', 'B', [1])
    if c == 2:
        P1 = {'독립어': PD['독립어'], '비독립어': PD['관형어'] + PD['부사어'] + PD['주어']}
        return t1(r, P1, '독립어', '밑줄 친 부분 중 독립 성분에 해당하는 것은?', {'독립어': '독립어: 감탄사·호격 조사가 붙은 체언 등', '비독립어': '독립어가 아니다'}, '하', 'C', [1])
    if c == 3:
        P1 = {'독립어': PD['독립어'], '비독립어': PD['관형어'] + PD['부사어'] + PD['주어']}
        return tpl_odd(r, PD)
    return tpl_tf(r, kb_tf_ga(), 'ok' if r.random() < 0.5 else 'bad', lv='중', fam='T', ref=[1])

def valency(a):
    return sum((1 for _, _, c in a.segs if c.split(':')[0] in ('주', '목', '보', '필')))
PRED = [a for a in SENT if any((c.split(':')[0] == '서' for _, _, c in a.segs)) and any((c.split(':')[0] == '주' for _, _, c in a.segs))]
VNAME = {1: '한 자리', 2: '두 자리', 3: '세 자리'}

def pred_idx(a):
    return [i for i, _, c in a.segs if c.split(':')[0] == '서'][0]

@T('hl027')
def g027(r, k):
    c = r.randrange(6)
    byv = {v: [(a, pred_idx(a)) for a in PRED if valency(a) == v] for v in (1, 2, 3)}
    if c <= 1:
        v = r.choice([1, 2, 3])
        pools = {x: byv[x] for x in (1, 2, 3)}
        names = {1: '한 자리 서술어', 2: '두 자리 서술어', 3: '세 자리 서술어'}
        return t1(r, {names[x]: pools[x] for x in pools}, names[v], '밑줄 친 서술어가 %s인 것은?' % names[v].replace(' 서술어', '') + ' 서술어', {names[x]: '%s이다(요구하는 성분: 서술어를 제외한 필수 성분의 수 = %d).' % (names[x], x) for x in pools}, '중', 'A', [2])
    if c == 2:
        a = r.choice(PRED)
        v = valency(a)
        return t_single(r, a, pred_idx(a), ['한 자리', '두 자리', '세 자리', '네 자리', '다섯 자리'], VNAME[v], '밑줄 친 서술어의 자릿수는?', ['서술어가 요구하는 필수 성분(주어·목적어·보어·필수적 부사어)의 수를 센다 → %d개 → %s 서술어이다.' % (v, VNAME[v])], '하', 'B', [2], '서술어의 자릿수')
    if c == 3:
        xs = r.sample(PRED, 3)
        stm = []
        for a in xs:
            truth = r.random() < 0.5
            v = valency(a)
            vv = v if truth else r.choice([x for x in (1, 2, 3) if x != v])
            stm.append(("'%s'는 %s 서술어이다." % (a.plain() and a.toks[pred_idx(a)][1], VNAME[vv]), truth, '문장 「%s」에서 필수 성분은 %d개이다.' % (a.plain(), v)))
        return bogi('서술어의 자릿수에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='C', r=r, ref=[2], ask='')
    if c == 4:
        for _ in range(30):
            a2 = r.sample(PRED, 4)
            vs = [valency(x) for x in a2]
            from collections import Counter
            cnt = Counter(vs)
            if sorted(cnt.values()) == [1, 1, 2]:
                break
        else:
            return None
        pairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
        right = [p for p in pairs if vs[p[0]] == vs[p[1]]][0]
        wrongs = [p for p in pairs if p != right]
        lines = ['%s %s' % (CIRC[n], x.html(under=[pred_idx(x)])) for n, x in enumerate(a2)]
        body = P('㉠~㉣의 밑줄 친 서술어 중 자릿수가 같은 것끼리 짝지은 것은?') + '<div class="bogi">' + ''.join(('<p>%s</p>' % l for l in lines)) + '</div>'
        fmt = lambda p: '%s, %s' % (CIRC[p[0]], CIRC[p[1]])
        st = ['%s의 서술어 자릿수: %d' % (CIRC[n], v) for n, v in enumerate(vs)]
        return mc(body, fmt(right), [fmt(p) for p in r.sample(wrongs, 4)], steps=st, core='서술어의 자릿수', lv='상', fam='D', r=r, ref=[2], vertical=False)
    return tpl_tf(r, kb_tf_ga(), 'ok' if r.random() < 0.5 else 'bad', lv='중', fam='T', ref=[2])

@T('hl028')
def g028(r, k):
    c = r.randrange(6)
    P2 = {'필수적 부사어': [], '수의적 부사어': [], '관형어': []}
    for a in SENT:
        for i, t, code in a.segs:
            if code.startswith('필:'):
                P2['필수적 부사어'].append((a, i))
            elif code.startswith('부:') and code != '부:문':
                P2['수의적 부사어'].append((a, i))
            elif code.startswith('관'):
                P2['관형어'].append((a, i))
    D = {'필수적 부사어': '필수적 부사어: 서술어가 요구하여 생략하면 문장이 불완전해진다.', '수의적 부사어': '수의적 부사어: 생략해도 문장이 성립한다.', '관형어': '관형어: 체언을 꾸미는 수의 성분이다.'}
    if c == 0:
        return t1(r, P2, '필수적 부사어', "밑줄 친 부분이 '필수적 부사어'인 것은?", D, '중', 'A', [2])
    if c == 1:
        return t1(r, P2, '수의적 부사어', "밑줄 친 부분이 '수의적 부사어'인 것은?", D, '중', 'B', [2])
    if c == 2:
        need = [('닮다', '어머니와'), ('같다', '그것과'), ('다르다', '아버지와'), ('생기다', '예쁘게'), ('다니다', '병원에'), ('삼다', '사위로'), ('주다', '영희에게'), ('넣다', '가방에'), ('두다', '책상에'), ('보내다', '친구에게')]
        notn = ['먹다', '읽다', '자다', '울다', '웃다', '피다', '놀다', '달리다', '마시다']
        right = r.choice(need)[0]
        ws = r.sample(notn, 4)
        return mc(P('다음 중 필수적 부사어를 요구하는 서술어는?'), right, ws, steps=["'%s'는 주어 외에 필수적 부사어를 요구하는 서술어이다." % right] + ["'%s'는 필수적 부사어가 없어도 문장이 성립한다." % w for w in ws], core='필수적 부사어를 요구하는 서술어', lv='중', fam='C', r=r, ref=[2])
    if c == 3:
        need = ['닮다', '같다', '다르다', '생기다', '다니다', '삼다', '주다', '넣다', '두다', '보내다', '여기다', '일컫다']
        notn = ['먹다', '읽다', '자다', '울다', '웃다', '피다', '놀다', '달리다', '마시다', '열다', '짓다', '보다']
        right = r.choice(notn)
        ws = r.sample(need, 4)
        return mc(P('다음 중 필수적 부사어를 요구하지 않는 서술어는?'), right, ws, steps=["'%s'는 주어와 목적어만으로 문장이 성립한다." % right] + ["'%s'는 필수적 부사어를 요구한다." % w for w in ws], core='필수적 부사어를 요구하는 서술어', lv='중', fam='D', r=r, ref=[2])
    if c == 4:
        a = r.choice([x for x in SENT if any((c_.startswith('필') for _, _, c_ in x.segs))])
        i = [i for i, _, c_ in a.segs if c_.startswith('필')][0]
        names = ['필수적 부사어이므로 생략할 수 없다', '수의적 부사어이므로 생략할 수 있다', '관형어이므로 생략할 수 있다', '독립어이므로 생략할 수 있다', '목적어이므로 생략할 수 없다']
        return t_single(r, a, i, names, names[0], '밑줄 친 부분에 대한 설명으로 가장 적절한 것은?', ['이 부분은 서술어가 요구하는 필수적 부사어이므로 생략하면 문장이 불완전해진다.'], '상', 'E', [2], '필수적 부사어')
    return tpl_tf(r, kb_tf_ga(), 'bad', lv='중', fam='T', ref=[2])
CL = G.CLAUSE

def clause_plain(a):
    return a.plain()

def clause_html(a, only_types=None):
    return a.html(under=[i for i, _, c in a.segs])

@T('hl029')
def g029(r, k):
    simple = [a for a in SENT if len(a.plain()) > 6 and (not any((c_ in ('관:형', '부:어', '필:어') for _, _, c_ in a.segs)))]
    inner = [a for a in SENT if any((c_ in ('관:형', '부:어', '필:어') for _, _, c_ in a.segs))]

    def _inner_why(a):
        for _, t, c_ in a.segs:
            if c_ == '관:형':
                return "'%s'은(는) 용언의 관형사형이므로 관형절을 안은 겹문장이다." % t
            if c_ in ('부:어', '필:어'):
                return "'%s'은(는) 용언의 부사형이므로 부사절을 안은 겹문장이다." % t
    honf = [(a.plain(), '홑', '주어와 서술어의 관계가 한 번만 나타나는 홑문장이다.') for a in simple]
    gyeop = [(a.plain(), '겹', '안은문장이다: 문장 속에 주어와 서술어를 갖춘 절이 안겨 있다.') for a in CL] + [(a.plain(), '겹', _inner_why(a)) for a in inner] + [(a.plain(), '겹', '이어진문장이다: 연결 어미로 두 홑문장이 이어져 있다.') for a in G.COORD] + [(s, '겹', ex) for s, kd, ex in G.WAGWA if kd == '접속']
    honf += [(s, '홑', ex) for s, kd, ex in G.WAGWA if kd == '부사격']
    c = r.randrange(5)
    if c <= 1 or c == 3:
        if c == 3:
            tgt = '홑'
        else:
            tgt = r.choice(['홑', '겹'])
        right = r.choice(honf if tgt == '홑' else gyeop)
        ws = r.sample(gyeop if tgt == '홑' else honf, 4)
        name = '홑문장' if tgt == '홑' else '겹문장'
        return mc(P('다음 중 %s인 것은?' % name), right[0], [w[0] for w in ws], steps=['%s: %s' % (right[0], right[2])] + ['%s: %s' % (w[0], w[2]) for w in ws], core=right[2], lv='하' if c != 3 else '중', fam='A', r=r, ref=[3], vertical=True)
    if c == 2:
        right = r.choice(gyeop)
        ws = r.sample(honf, 4)
        return mc(P('다음 중 홑문장이 아닌 것은?'), right[0], [w[0] for w in ws], steps=['%s: %s' % (right[0], right[2])] + ['%s: %s' % (w[0], w[2]) for w in ws], core=right[2], lv='중', fam='B', r=r, ref=[3], vertical=True)
    stm = []
    xs = r.sample(honf + gyeop, 3)
    for s, kd, ex in xs:
        truth = r.random() < 0.5
        name = {'홑': '홑문장', '겹': '겹문장'}
        n = kd if truth else '겹' if kd == '홑' else '홑'
        stm.append(('「%s」은(는) %s이다.' % (s, name[n]), truth, ex))
    return bogi('문장의 짜임에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='C', r=r, ref=[3], ask='')
CLNAME = {'명사절': '명사절을 안은 문장', '관형절': '관형절을 안은 문장', '부사절': '부사절을 안은 문장', '서술절': '서술절을 안은 문장', '인용절': '인용절을 안은 문장'}
CLD = {'명사절': "명사절: 명사형 어미 '-(으)ㅁ, -기'로 실현되어 주어·목적어·부사어 등으로 쓰인다.", '관형절': "관형절: 관형사형 어미 '-(으)ㄴ, -는, -(으)ㄹ, -던'으로 실현되어 체언을 꾸민다.", '부사절': "부사절: 부사형 어미 '-이, -게, -도록' 등으로 실현되어 부사어로 쓰인다.", '서술절': '서술절: 전체 주어에 대한 서술어 구실을 하며 절임을 나타내는 표지가 없다.', '인용절': "인용절: 인용한 말을 절로 안은 것으로 '라고'(직접)·'고'(간접)가 붙는다."}

def cl_type(code):
    return code.split(':')[0].replace('절', '') + '절'

def cl_pools(sents, keyf):
    d = {}
    for a in sents:
        for i, t, c in a.segs:
            d.setdefault(keyf(c), []).append((a, i))
    return d

@T('hl030')
def g030(r, k):
    pools = cl_pools(CL, lambda c: c.split(':')[0])
    c = r.randrange(7)
    if c <= 2:
        tgt = r.choice(list(CLD))
        return t1(r, pools, tgt, '밑줄 친 부분이 %s인 것은?' % tgt, CLD, '중' if c else '하', 'A', [3])
    if c == 3:
        a = r.choice(CL)
        i, t, code = a.segs[0]
        tp = code.split(':')[0]
        return t_single(r, a, i, list(CLD), tp, '밑줄 친 절의 종류는?', [CLD[tp]], '하', 'B', [3], CLD[tp])
    if c == 4:
        tgt = r.choice(list(CLD))
        P1 = {x: pools[x] for x in pools}
        return tpl_cl_odd(r, pools)
    if c == 5:
        pl = [(a, i) for a in CL for i, t, code in a.segs if code.startswith('명사절')]
        a, i = r.choice(pl)
        code = a.toks[i][2]
        role = code.split(':')[1]
        return t_single(r, a, i, ['주어', '목적어', '부사어', '관형어', '서술어'], role, '밑줄 친 명사절이 문장에서 하는 역할은?', ['이 명사절은 %s로 쓰였다.' % role], '중', 'D', [3], CLD['명사절'])
    mark = {'명사절': ['-(으)ㅁ, -기', '-(으)ㄴ, -는', '-게, -도록', '-고, -며', '-라고, -고'], '관형절': ['-(으)ㄴ, -는, -(으)ㄹ, -던', '-(으)ㅁ, -기', '-게, -도록', '-고, -며', '-라고, -고'], '부사절': ['-게, -도록', '-(으)ㅁ, -기', '-(으)ㄴ, -는', '-고, -며', '-라고, -고'], '인용절': ['-라고, -고', '-(으)ㅁ, -기', '-(으)ㄴ, -는', '-게, -도록', '-고, -며']}
    tg = r.choice(list(mark))
    a, i = r.choice(pools[tg])
    right = mark[tg][0]
    return _mark_item(r, a, i, tg, mark)

def _mark_item(r, a, i, tg, mark):
    right = mark[tg][0]
    ws = r.sample(mark[tg][1:], 4)
    body = P('밑줄 친 절을 안긴절로 만든 것은 어떤 어미(조사)인가?') + '<div class="bogi"><p>%s</p></div>' % a.html(under=[i])
    return mc(body, right, ws, steps=['%s: %s' % (tg, CLD[tg])], core=CLD[tg], lv='중', fam='E', r=r, ref=[3])

def tpl_cl_odd(r, pools):
    """밑줄 친 안긴절의 종류가 나머지와 다른 하나"""
    tps = list(CLD)
    same = r.choice(tps)
    diff = r.choice([x for x in tps if x != same])
    if len(pools.get(same, [])) < 4 or not pools.get(diff):
        return None
    xs = r.sample(pools[same], 4)
    if len({a.s for a, _ in xs}) < 4:
        return None
    a, i = r.choice(pools[diff])
    wr = [opt(x, j) for x, j in xs]
    st = ['%s: %s' % (plain(opt(a, i)), '%s이다(다른 하나).' % diff)] + ['%s: %s이다.' % (plain(opt(x, j)), same) for x, j in xs]
    return mc(P('밑줄 친 안긴절의 종류가 나머지 넷과 다른 것은?'), opt(a, i), wr, steps=st, core=CLD[same], lv='상', fam='O', r=r, ref=[3], vertical=True)

@T('hl031')
def g031(r, k):
    gr = [a for a in CL if a.segs[0][2].startswith('관형절:관계')]
    dg = [a for a in CL if a.segs[0][2].startswith('관형절:동격')]
    c = r.randrange(6)
    D = {'관계': '관계 관형절: 꾸밈을 받는 체언이 관형절 안의 한 성분으로 대응된다.', '동격': '동격 관형절: 관형절 전체가 꾸밈을 받는 체언의 내용이다.'}
    pools = {'관계': [(a, a.segs[0][0]) for a in gr], '동격': [(a, a.segs[0][0]) for a in dg]}
    if c <= 1:
        return _kwan_t1(r, pools, D, '중', 'A')
    if c == 2:
        return _kwan_t1(r, pools, D, '상', 'B')
    if c == 3:
        a = r.choice(gr)
        i, t, code = a.segs[0]
        om = code.split(':')[2]
        return t_single(r, a, i, ['주어', '목적어', '부사어', '보어', '서술어'], om, '밑줄 친 관계 관형절에서 꾸밈을 받는 체언과 대응하여 생략된 성분은?', ["관형절 안에서 꾸밈을 받는 체언이 '%s'로 쓰였으므로 이 성분이 생략된 것이다." % om], '상', 'C', [3], D['관계'])
    if c == 4:
        a = r.choice(gr + dg)
        i, t, code = a.segs[0]
        kd = code.split(':')[1]
        names = ['관계 관형절', '동격 관형절', '명사절', '부사절', '서술절']
        return t_single(r, a, i, names, kd + ' 관형절', '밑줄 친 절의 종류로 가장 적절한 것은?', [D[kd]], '중', 'D', [3], D[kd])
    xs = r.sample(gr + dg, 3)
    stm = []
    for a in xs:
        kd = a.segs[0][2].split(':')[1]
        truth = r.random() < 0.5
        n = kd if truth else '동격' if kd == '관계' else '관계'
        stm.append(('「%s」의 밑줄 친 관형절은 %s 관형절이다.' % (a.html(under=[a.segs[0][0]]), n), truth, D[kd]))
    return bogi('관형절에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='E', r=r, ref=[3], ask='')

def _kwan_t1(r, pools, D, lv, fam):
    t = r.choice(['관계', '동격'])
    return t1(r, pools, t, '밑줄 친 관형절이 %s 관형절인 것은?' % t, D, lv, fam, [3])

@T('hl032')
def g032(r, k):
    pools = cl_pools(CL, lambda c: c.split(':')[0])
    sub = {k_: pools[k_] for k_ in ('서술절', '인용절', '명사절', '부사절', '관형절')}
    c = r.randrange(6)
    if c <= 1:
        return t1(r, sub, '서술절', '밑줄 친 부분이 서술절인 것은?', CLD, '중', 'A', [3])
    if c == 2:
        return t1(r, sub, '인용절', '밑줄 친 부분이 인용절인 것은?', CLD, '하', 'B', [3])
    if c == 3:
        d = {'직접': [], '간접': []}
        for a in CL:
            for i, t, code in a.segs:
                if code.startswith('인용절'):
                    d.setdefault(code.split(':')[1], []).append((a, i))
        D2 = {'직접': "직접 인용절: 인용한 말을 그대로 큰따옴표 안에 넣고 '라고'를 붙인다.", '간접': "간접 인용절: 인용하는 사람의 말로 바꾸고 '고'를 붙인다."}
        t = r.choice(['직접', '간접'])
        return t1(r, d, t, '밑줄 친 인용절이 %s 인용절인 것은?' % t, D2, '중', 'C', [3])
    if c == 4:
        d = {'서술절': sub['서술절'], '관형절': sub['관형절'], '부사절': sub['부사절']}
        return tpl_cl_odd(r, sub)
    return tpl_tf(r, kb_tf_ga(), 'ok' if r.random() < 0.5 else 'bad', lv='중', fam='T', ref=[3])
CO = G.COORD

def co_kind(a):
    return a.segs[0][2].split(':')[0]

def co_end(a):
    return a.segs[0][2].split(':')[1]

def co_mean(a):
    return a.segs[0][2].split(':')[2]

@T('hl033')
def g033(r, k):
    pools = {'대등': [(a, a.segs[0][0]) for a in CO if co_kind(a) == '대등'], '종속': [(a, a.segs[0][0]) for a in CO if co_kind(a) == '종속']}
    D = {'대등': '대등하게 이어진 문장: 앞뒤 절의 의미가 대등하여 순서를 바꾸어도 의미가 크게 달라지지 않는다.', '종속': '종속적으로 이어진 문장: 앞 절이 뒤 절에 종속되어 순서를 바꾸면 의미가 달라진다.'}
    c = r.randrange(7)
    if c <= 1:
        return _co_t1(r, pools, D, '중', 'A')
    if c == 2:
        return _co_t1(r, pools, D, '상', 'B')
    if c == 3:
        a = r.choice(CO)
        names = ['대등적 연결 어미', '종속적 연결 어미', '종결 어미', '전성 어미', '선어말 어미']
        right = '대등적 연결 어미' if co_kind(a) == '대등' else '종속적 연결 어미'
        return _co_end_item(r, a)
    if c == 4:
        a = r.choice(CO)
        means = ['나열', '대조', '선택', '원인', '이유', '조건', '양보', '의도', '목적', '배경', '전환', '정도의 심화']
        m = co_mean(a)
        names = [x for x in means if x != m]
        ws = r.sample(names, 4)
        body = P("밑줄 친 연결 어미 '%s'가 나타내는 의미는?" % co_end(a)) + '<div class="bogi"><p>%s</p></div>' % a.html(under=[a.segs[0][0]])
        return mc(body, m, ws, steps=['연결 어미 %s는 %s의 의미를 나타낸다(%s).' % (co_end(a), m, co_kind(a))], core='연결 어미의 의미', lv='중', fam='D', r=r, ref=[4])
    if c == 5:
        d = pools['대등']
        e = pools['종속']
        right = r.choice(d)[0].plain()
        ws = [x[0].plain() for x in r.sample(e, 4)]
        return mc(P('앞 절과 뒤 절의 순서를 바꾸어도 의미가 크게 달라지지 않는 문장은?'), right, ws, steps=['%s: 대등적으로 이어진 문장이다.' % right] + ['%s: 종속적으로 이어진 문장이다.' % w for w in ws], core=D['대등'], lv='상', fam='E', r=r, ref=[4], vertical=True)
    xs = r.sample(CO, 3)
    stm = []
    for a in xs:
        truth = r.random() < 0.5
        kd = co_kind(a)
        n = kd if truth else '종속' if kd == '대등' else '대등'
        stm.append(('「%s」의 밑줄 친 부분은 %s 연결 어미로 이어진 절이다.' % (a.html(under=[a.segs[0][0]]), n), truth, '%s는 %s 연결 어미(%s)이다.' % (co_end(a), kd, co_mean(a))))
    return bogi('이어진문장에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='F', r=r, ref=[4], ask='')

def _co_t1(r, pools, D, lv, fam):
    t = r.choice(['대등', '종속'])
    return t1(r, pools, t, '밑줄 친 부분이 %s적으로 이어진 문장의 앞 절인 것은?' % t, D, lv, fam, [4])

def _co_end_item(r, a):
    names = ['대등적 연결 어미', '종속적 연결 어미', '종결 어미', '명사형 전성 어미', '선어말 어미']
    right = '대등적 연결 어미' if co_kind(a) == '대등' else '종속적 연결 어미'
    body = P("밑줄 친 어미 '%s'의 갈래는?" % co_end(a)) + '<div class="bogi"><p>%s</p></div>' % a.html(under=[a.segs[0][0]])
    return mc(body, right, [n for n in names if n != right], steps=['%s: %s(%s의 의미)' % (co_end(a), right, co_mean(a))], core='연결 어미', lv='중', fam='C', r=r, ref=[4], vertical=False)

@T('hl034')
def g034(r, k):
    jub = [x for x in G.WAGWA if x[1] == '접속']
    bu = [x for x in G.WAGWA if x[1] == '부사격']
    c = r.randrange(5)
    if c <= 1:
        tgt = r.choice(['접속', '부사격'])
        right = r.choice(jub if tgt == '접속' else bu)
        ws = r.sample(bu if tgt == '접속' else jub, 4)
        name = "접속 조사 '와/과'로 이어진 겹문장" if tgt == '접속' else "부사격 조사 '와/과'가 쓰인 홑문장"
        return mc(P('다음 중 %s인 것은?' % name), right[0], [w[0] for w in ws], steps=['%s: %s' % (right[0], right[2])] + ['%s: %s' % (w[0], w[2]) for w in ws], core=right[2], lv='중', fam='A', r=r, ref=[4], vertical=True)
    if c == 2:
        a = r.choice(jub + bu)
        names = ['접속 조사가 쓰인 겹문장', '부사격 조사가 쓰인 홑문장', '안은문장', '서술절을 안은 문장', '인용절을 안은 문장']
        right = names[0] if a[1] == '접속' else names[1]
        return mc(P('「%s」에 대한 설명으로 가장 적절한 것은?' % a[0]), right, [n for n in names if n != right], steps=[a[2]], core=a[2], lv='중', fam='B', r=r, ref=[4], vertical=True)
    if c == 3:
        xs = r.sample(jub + bu, 3)
        stm = []
        for s, kd, ex in xs:
            truth = r.random() < 0.5
            n = kd if truth else '부사격' if kd == '접속' else '접속'
            stm.append(("「%s」의 '와/과'는 %s이다." % (s, '접속 조사' if n == '접속' else '부사격 조사'), truth, ex))
        return bogi("'와/과'에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?", stm, lv='상', fam='C', r=r, ref=[4], ask='')
    return tpl_tf(r, kb_tf_ga(), 'bad' if r.random() < 0.5 else 'ok', lv='중', fam='T', ref=[4])
