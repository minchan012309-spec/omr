"""Ⅱ-B 문법 요소와 표현 (hl035~hl049)"""
import itertools
from hllib import *
from ann import Ann
from gram_gen import *
import gram_fact as F
import kb_gram_b as B
import kb_gram_b2 as B2
import kb_tf_b as TFB
from orth_gen import tpl_tf

def pools_of(anns, label_of):
    """label_of(code) → 라벨 또는 None"""
    d = {}
    for a in anns:
        for i, t, c in a.segs:
            l = label_of(c)
            if l:
                d.setdefault(l, []).append((a, i))
    return d

def fresh(r, fn, n, *a):
    out, seen = ([], set())
    for _ in range(n * 4):
        x = fn(r, *a)
        if x.plain() in seen:
            continue
        seen.add(x.plain())
        out.append(x)
        if len(out) >= n:
            break
    return out

def hon_pool(r, n=30):
    xs = list(B.HON)
    xs += fresh(r, F.hon_sm, n // 2, r.choice(['합쇼', '해라']))
    xs += fresh(r, F.hon_obj_s, n // 2)
    xs += fresh(r, F.hon_hr, n // 2)
    xs += fresh(r, F.hon_all, n // 4)
    return xs
HONL = {'SJ': '주체 높임(조사 께서)', 'SM': '주체 높임(선어말 어미 -시-)', 'SL': '주체 높임(특수 어휘)', 'OJ': '객체 높임(조사 께)', 'OL': '객체 높임(특수 어휘)', 'HR': '상대 높임(종결 어미)'}
HOND = {'SJ': "주체를 높이는 주격 조사 '께서'이다.", 'SM': "주체를 높이는 선어말 어미 '-(으)시-'이다.", 'SL': '주체를 높이는 특수 어휘이다.', 'OJ': "객체를 높이는 부사격 조사 '께'이다.", 'OL': '객체를 높이는 특수 어휘이다.', 'HR': '상대(청자)를 높이거나 낮추는 종결 어미이다.'}
HONG = {'주체 높임': ['SJ', 'SM', 'SL'], '객체 높임': ['OJ', 'OL'], '상대 높임': ['HR']}

def hlabel(c):
    return c.split(':')[0]

@T('hl035')
def g035(r, k):
    xs = hon_pool(r)
    c = r.randrange(7)
    P1 = pools_of(xs, lambda c: {'SJ': '주체', 'SM': '주체', 'SL': '주체', 'OJ': '객체', 'OL': '객체', 'HR': '상대'}.get(hlabel(c)))
    D1 = {'주체': '주체 높임을 실현하는 부분이다.', '객체': '객체 높임을 실현하는 부분이다.', '상대': '상대 높임을 실현하는 종결 어미이다.'}
    if c == 0:
        return t1(r, P1, '주체', '밑줄 친 부분이 주체 높임을 실현하는 것은?', D1, '하', 'A', [1])
    if c == 1:
        P2 = pools_of(xs, lambda c: hlabel(c) if hlabel(c) in ('SJ', 'SM', 'SL') else 'X' if hlabel(c) in ('OJ', 'OL', 'HR') else None)
        t = r.choice(['SJ', 'SM', 'SL'])
        P2 = {t: P2[t], 'X': P2['X']}
        names = {'SJ': "주체를 높이는 조사('께서')가 쓰인 것", 'SM': "주체를 높이는 선어말 어미('-(으)시-')가 쓰인 것", 'SL': '주체를 높이는 특수 어휘가 쓰인 것'}
        return t1(r, P2, t, '밑줄 친 부분이 %s은?' % names[t], {**HOND, 'X': '주체 높임이 아니다.'}, '중', 'B', [1])
    if c == 2:
        a = r.choice([x for x in xs if any((hlabel(cc) in ('SJ', 'SM', 'SL') for _, _, cc in x.segs))])
        i, t, code = [s for s in a.segs if hlabel(s[2]) in ('SJ', 'SM', 'SL')][0]
        names = [HONL[x] for x in ('SJ', 'SM', 'SL', 'OJ', 'OL', 'HR')]
        return t_single(r, a, i, names, HONL[hlabel(code)], '밑줄 친 부분이 실현하는 높임법의 방법은?', ['%s: %s' % (t, HOND[hlabel(code)])], '중', 'C', [1], HOND[hlabel(code)])
    if c == 3:
        return tpl_tf(r, TFB.TF_HON, 'ok', lv='중', fam='D', ref=[1])
    if c == 4:
        return tpl_tf(r, TFB.TF_HON, 'bad', lv='중', fam='E', ref=[1])
    if c == 5:
        d = [('할머니께서 약속이 있으시다.', '간접 높임', "'약속'은 높일 대상의 소유(관련 대상)이므로 '-(으)시-'로 간접 높인다."), ('아버지께서 집에 오셨다.', '직접 높임', "'께서'와 '-시-'로 주체 '아버지'를 직접 높인다."), ('어머니께서는 손이 크시다.', '간접 높임', "'손'은 주체의 신체 일부이므로 '-(으)시-'로 간접 높인다."), ('선생님께서 방에 계신다.', '직접 높임', "특수 어휘 '계시다'로 주체를 직접 높인다."), ('할아버지께서는 귀가 어두우시다.', '간접 높임', "'귀'는 주체의 신체 일부이므로 '-(으)시-'로 간접 높인다."), ('교장 선생님께서 말씀하셨다.', '직접 높임', "'께서'와 '-시-'로 주체를 직접 높인다."), ('이모께서는 걱정이 많으시다.', '간접 높임', "'걱정'은 주체의 생각·감정과 관련된 것이므로 간접 높임이다."), ('아버지께서 진지를 드신다.', '직접 높임', "특수 어휘 '진지, 드시다'로 주체를 직접 높인다.")]
        a = r.choice(d)
        names = ['직접 높임', '간접 높임', '객체 높임', '상대 높임', '높임이 쓰이지 않음']
        body = P('다음 문장에 쓰인 주체 높임의 방식으로 알맞은 것은?') + '<div class="bogi"><p>%s</p></div>' % a[0]
        return mc(body, a[1], [n for n in names if n != a[1]], steps=[a[2]], core=a[2], lv='중', fam='F', r=r, ref=[1])
    return tpl_tf(r, TFB.TF_HON, 'ok', lv='하', fam='G', ref=[1])

@T('hl036')
def g036(r, k):
    xs = hon_pool(r)
    c = r.randrange(6)
    P1 = pools_of(xs, lambda c: {'SJ': '주체', 'SM': '주체', 'SL': '주체', 'OJ': '객체', 'OL': '객체', 'HR': '상대'}.get(hlabel(c)))
    D1 = {'주체': '주체 높임을 실현하는 부분이다.', '객체': '객체 높임을 실현하는 부분이다(목적어·부사어가 가리키는 대상을 높임).', '상대': '상대 높임을 실현하는 종결 어미이다.'}
    if c == 0:
        return t1(r, P1, '객체', '밑줄 친 부분이 객체 높임을 실현하는 것은?', D1, '하', 'A', [1])
    if c == 1:
        P2 = pools_of(xs, lambda c: hlabel(c) if hlabel(c) in ('OJ', 'OL') else 'X' if hlabel(c) in ('SJ', 'SM', 'SL', 'HR') else None)
        t = r.choice(['OJ', 'OL'])
        names = {'OJ': "객체를 높이는 부사격 조사('께')가 쓰인 것", 'OL': '객체를 높이는 특수 어휘가 쓰인 것'}
        return t1(r, {t: P2[t], 'X': P2['X']}, t, '밑줄 친 부분이 %s은?' % names[t], {**HOND, 'X': '객체 높임이 아니다.'}, '중', 'B', [1])
    if c == 2:
        pairs = [('데리다', '모시다'), ('주다', '드리다'), ('보다', '뵙다'), ('묻다', '여쭙다')]
        a = r.choice(pairs)
        wrongs = [x for p in pairs for x in p if x != a[1]]
        return mc(P("객체 높임을 실현하는 특수 어휘로, '%s'에 대응하는 것은?" % a[0]), a[1], ['잡수시다', '주무시다', '계시다', '돌아가시다'], steps=["'%s'의 객체 높임 특수 어휘는 '%s'이다." % (a[0], a[1]), '잡수시다·주무시다·계시다·돌아가시다는 주체 높임의 특수 어휘이다.'], core='객체 높임의 특수 어휘', lv='하', fam='C', r=r, ref=[1])
    if c == 3:
        return tpl_tf(r, TFB.TF_HON, 'ok', lv='중', fam='D', ref=[1])
    if c == 4:
        o = r.choice(F.OBJ_H)
        a = F.hon_obj_s(r)
        txt = a.plain()
        names = [x for x in F.OBJ_H]
        base = [x for x in F.OBJ_H if x in txt]
        if not base:
            return None
        ob = max(base, key=len)
        return mc(P('다음 문장에서 객체 높임의 대상이 되는 인물은?') + '<div class="bogi"><p>%s</p></div>' % txt, ob, ['나', '동생', '친구', '철수'], steps=["객체 높임의 대상은 '%s'이다. '께'나 특수 어휘(드리다·모시다·뵙다·여쭙다)가 높이는 대상이다." % ob], core='객체 높임', lv='중', fam='E', r=r, ref=[1])
    return tpl_tf(r, TFB.TF_HON, 'bad', lv='중', fam='F', ref=[1])
HRL = ['합쇼', '하오', '하게', '해라', '해요', '해']
HRDESC = {'합쇼': '하십시오체: 격식체에서 듣는 이를 아주 높인다.', '하오': '하오체: 격식체에서 듣는 이를 예사 높인다.', '하게': '하게체: 격식체에서 듣는 이를 예사 낮춘다.', '해라': '해라체: 격식체에서 듣는 이를 아주 낮춘다.', '해요': '해요체: 비격식체에서 듣는 이를 두루 높인다.', '해': '해체: 비격식체에서 듣는 이를 두루 낮춘다.'}
HRN = {k_: B_ for k_, B_ in zip(HRL, ['하십시오체', '하오체', '하게체', '해라체', '해요체', '해체'])}

@T('hl037')
def g037(r, k):
    xs = B.HON + [F.hon_hr(r, r.choice(HRL)) for _ in range(40)]
    P1 = {}
    for a in xs:
        for i, t, c in a.segs:
            if c.startswith('HR:'):
                P1.setdefault(c.split(':')[1], []).append((a, i))
    c = r.randrange(7)
    if c <= 1:
        t = r.choice(HRL)
        return t1(r, P1, t, '밑줄 친 종결 어미의 상대 높임 등급이 %s인 것은?' % HRN[t], HRDESC, '중', 'A', [1])
    if c == 2:
        t = r.choice(HRL)
        a, i = r.choice(P1[t])
        return t_single(r, a, i, [HRN[x] for x in HRL] + ['주체 높임'], HRN[t], '밑줄 친 부분에 나타난 상대 높임의 등급은?', [HRDESC[t]], '중', 'B', [1], HRDESC[t])
    if c == 3:
        gy = {'격식체': sum((P1[x] for x in ('합쇼', '하오', '하게', '해라') if x in P1), []), '비격식체': sum((P1[x] for x in ('해요', '해') if x in P1), [])}
        t = r.choice(['격식체', '비격식체'])
        return t1(r, gy, t, '밑줄 친 종결 어미가 %s에 해당하는 것은?' % t, {'격식체': '격식체: 하십시오체·하오체·하게체·해라체', '비격식체': '비격식체: 해요체·해체'}, '중', 'C', [1])
    if c == 4:
        hi = {'듣는 이를 높이는 등급': sum((P1[x] for x in ('합쇼', '하오', '해요') if x in P1), []), '듣는 이를 낮추는 등급': sum((P1[x] for x in ('하게', '해라', '해') if x in P1), [])}
        t = r.choice(list(hi))
        return t1(r, hi, t, '밑줄 친 종결 어미가 %s인 것은?' % t, {'듣는 이를 높이는 등급': '하십시오체·하오체·해요체는 듣는 이를 높인다.', '듣는 이를 낮추는 등급': '하게체·해라체·해체는 듣는 이를 낮춘다.'}, '상', 'D', [1])
    if c == 5:
        t = r.choice([x for x in HRL if len(P1.get(x, [])) >= 2])
        a, i = r.choice(P1[t])
        b, j = r.choice([p for p in P1[t] if p[0].s != a.s])
        others = [x for x in HRL if x != t and P1.get(x)]
        ws = [opt(*r.choice(P1[x])) for x in r.sample(others, 4)]
        return mc(P('다음 문장의 밑줄 친 종결 어미와 상대 높임 등급이 같은 것은?') + '<div class="bogi"><p>%s</p></div>' % a.html(under=[i]), opt(b, j), ws, steps=['두 종결 어미는 모두 %s이다.' % HRN[t]], core=HRDESC[t], lv='상', fam='E', r=r, ref=[1], vertical=True)
    return tpl_tf(r, TFB.TF_HON, r.choice(['ok', 'bad']), lv='중', fam='F', ref=[1])

def hon_roles_item(r, lv='상', fam='R'):
    """주체·객체·상대 짝짓기"""
    names = ['할머니', '할아버지', '어머니', '아버지', '선생님', '이모', '삼촌']
    sub, ob, hr = r.sample(names, 3)
    N = r.choice(['선물을', '꽃을', '편지를', '과일을'])
    P_ = r.choice(['큰댁', '병원', '시장', '공원'])
    end = r.choice(['합쇼', '해요'])
    e = HR_END_[end]
    s = '%s, %s{께서|SJ} %s{께|OJ} %s {드리|OL}러 %s에 가{셨|SM}{%s|HR:%s}.' % (hr, sub, ob, N, P_, e, end)
    a = F.mk(s)
    perms = list(itertools.permutations([sub, ob, hr]))
    right = '주체: %s, 객체: %s, 상대: %s' % (sub, ob, hr)
    wrongs = ['주체: %s, 객체: %s, 상대: %s' % p for p in perms if p != (sub, ob, hr)]
    wrongs = r.sample(wrongs, 4)
    body = P('문장 맨 앞의 호칭은 화자가 말을 건네는 상대(청자)이다. 밑줄 친 부분이 높이는 대상을 바르게 짝지은 것은?') + '<div class="bogi"><p>%s</p></div>' % a.html(under=[i for i, _, _ in a.segs])
    st = ["주체 높임('께서', '-시-')의 대상: %s" % sub, "객체 높임('께', '드리다')의 대상: %s" % ob, "상대 높임('-%s')의 대상(청자): %s" % (HR_END_[end], hr)]
    return mc(body, right, wrongs, steps=st, core='주체·객체·상대 높임의 대상 구별', lv=lv, fam=fam, r=r, ref=[1], vertical=True)
HR_END_ = F.HR_END

@T('hl038')
def g038(r, k):
    c = r.randrange(6)
    if c <= 1:
        return hon_roles_item(r, '상', 'R')
    if c == 2:
        a = F.hon_all(r)
        idxs = [i for i, _, _ in a.segs][:5]
        D = {'SJ': ('주체를 높이는 조사이다', ['객체를 높이는 조사이다', '상대를 높이는 어미이다', '주체를 높이는 어미이다']), 'SM': ('주체를 높이는 선어말 어미이다', ['객체를 높이는 특수 어휘이다', '상대를 높이는 종결 어미이다', '주체를 높이는 조사이다']), 'OJ': ('객체를 높이는 조사이다', ['주체를 높이는 조사이다', '상대를 높이는 종결 어미이다', '객체를 높이는 선어말 어미이다']), 'OL': ('객체를 높이는 특수 어휘이다', ['주체를 높이는 특수 어휘이다', '상대를 높이는 종결 어미이다', '객체를 높이는 조사이다']), 'HR': ('상대를 높이는 종결 어미이다', ['주체를 높이는 선어말 어미이다', '객체를 높이는 조사이다', '주체를 높이는 조사이다'])}
        return tf_stmts(r, a, idxs, lambda c_: D[hlabel(c_)], '㉠~㉤에 대한 설명으로 옳지 않은 것은?', 'bad', '상', 'A', [1], core='높임법의 세 종류와 실현 방법')
    if c == 3:
        xs = [F.hon_all(r) for _ in range(4)] + [F.hon_sm(r, r.choice(['합쇼', '해요'])) for _ in range(3)]
        a = r.choice(xs)
        flags = {'주체 높임': any((hlabel(c_) in ('SJ', 'SM', 'SL') for _, _, c_ in a.segs)), '객체 높임': any((hlabel(c_) in ('OJ', 'OL') for _, _, c_ in a.segs)), '상대 높임': any((hlabel(c_) == 'HR' for _, _, c_ in a.segs))}
        right = ', '.join((n for n, v in flags.items() if v))
        opts_all = ['주체 높임', '객체 높임', '상대 높임', '주체 높임, 객체 높임', '주체 높임, 상대 높임', '객체 높임, 상대 높임', '주체 높임, 객체 높임, 상대 높임']
        if right not in opts_all:
            return None
        ws = r.sample([o for o in opts_all if o != right], 4)
        return mc(P('다음 문장에 쓰인 높임법을 모두 고른 것은?') + '<div class="bogi"><p>%s</p></div>' % a.plain(), right, ws, steps=['이 문장에는 %s이(가) 쓰였다.' % right], core='높임법의 세 종류', lv='상', fam='B', r=r, ref=[1], vertical=False)
    if c == 4:
        return tpl_tf(r, TFB.TF_HON, 'bad', lv='상', fam='C', ref=[1])
    return hon_roles_item(r, '최', 'R2')
BADH = [('선생님은 머리가 하얗게 세었다.', '선생님께서는 머리가 하얗게 세셨다.', "높일 대상(선생님)의 신체 일부 '머리'와 관련된 서술어에도 '-(으)시-'를 써서 간접 높임을 해야 한다."), ('주문하신 상품은 품절이십니다.', '주문하신 상품은 품절입니다.', "'상품'은 높일 대상이 아니므로 '이십니다'가 아니라 '입니다'를 써야 한다."), ('고객님께서 문의하신 제품은 품절되셨습니다.', '고객님께서 문의하신 제품은 품절되었습니다.', "'제품'은 높일 대상이 아니므로 '-(으)시-'를 쓰지 않는다."), ('집에 가도 된다는 선생님의 말씀이 계셨니?', '집에 가도 된다는 선생님의 말씀이 있었니?', "'말씀'은 높임 대상이 아니라 높임 대상의 소유물이므로 간접 높임에서 '계시다'가 아닌 '있으시다/있다'를 쓴다."), ('할머니께서는 약속이 계시다.', '할머니께서는 약속이 있으시다.', "간접 높임에서는 특수 어휘 '계시다'를 쓰지 않고 '있으시다'를 쓴다."), ('커피 나오셨습니다.', '커피 나왔습니다.', "높일 대상이 아닌 '커피'에 높임의 '-(으)시-'를 썼다."), ('이 옷은 사이즈가 없으십니다.', '이 옷은 사이즈가 없습니다.', "높일 대상이 아닌 사물에 '-(으)시-'를 썼다."), ('사장님은 지금 자리에 없으십니다.', '사장님은 지금 자리에 계시지 않습니다.', "주체를 직접 높일 때는 '없으시다'가 아니라 특수 어휘 '계시다'를 쓴다."), ('나는 할아버지에게 용돈을 주었다.', '나는 할아버지께 용돈을 드렸다.', "객체 '할아버지'를 높이려면 조사 '께'와 특수 어휘 '드리다'를 써야 한다."), ('동생이 선생님을 데리고 갔다.', '동생이 선생님을 모시고 갔다.', "객체를 높이는 특수 어휘 '모시다'를 써야 한다."), ('어머니가 할머니에게 안부를 물었다.', '어머니가 할머니께 안부를 여쭈었다.', "객체 '할머니'를 높이려면 '께'와 '여쭈다'를 써야 한다."), ('나는 어제 선생님을 만나서 말했다.', '나는 어제 선생님을 만나 뵙고 말씀드렸다.', "객체 '선생님'을 높이려면 '뵙다, 말씀드리다'를 써야 한다."), ('아버지께서 밥을 먹었다.', '아버지께서 진지를 드셨다.', "주체 '아버지'를 높이려면 '-(으)시-'와 특수 어휘 '진지, 드시다'를 써야 한다."), ('할아버지께서 방에서 잔다.', '할아버지께서 방에서 주무신다.', "주체 '할아버지'를 높이려면 특수 어휘 '주무시다'를 써야 한다."), ('할머니께서 아프다.', '할머니께서 편찮으시다.', "주체 '할머니'를 높이려면 특수 어휘 '편찮으시다'를 써야 한다.")]
GOODH = ['할머니께서는 눈이 나쁘시다.', '아버지께서는 연세가 많으시다.', '선생님께서는 걱정이 많으시다.', '어머니께서는 손이 크시다.', '할아버지께서는 귀가 어두우시다.', '아버지께서는 다리가 아프시다.', '선생님께서 교실에 들어오셨다.', '할머니께서 약속이 있으시다.', '어머니께서는 마음이 넓으시다.', '선생님께서는 책이 많으시다.']

@T('hl039')
def g039(r, k):
    c = r.randrange(6)
    if c <= 1:
        a = r.choice(BADH)
        others = [x for x in BADH if x[0] != a[0]]
        ws = [x[1] for x in r.sample(others, 3)]
        wrong_fix = [a[0]]
        right = a[1]
        ws = [a[0]] + [x for x in r.sample(GOODH, 3)]
        return _fix_item(r, a)
    if c == 2:
        a = r.choice(BADH)
        gs = r.sample(GOODH, 4)
        return mc(P('높임 표현이 적절하지 않은 것은?'), a[0], gs, steps=['"%s": %s' % (a[0], a[2])] + ['"%s"은(는) 간접 높임이 적절하다.' % g for g in gs], core=a[2], lv='중', fam='B', r=r, ref=[1], vertical=True)
    if c == 3:
        bs = r.sample(BADH, 4)
        g = r.choice(GOODH)
        return mc(P('높임 표현이 적절한 것은?'), g, [b[0] for b in bs], steps=['"%s"은(는) 적절한 간접 높임이다.' % g] + ['"%s": %s' % (b[0], b[2]) for b in bs], core='높임법의 오류', lv='중', fam='C', r=r, ref=[1], vertical=True)
    if c == 4:
        a = r.choice(BADH)
        why_names = ['높일 대상이 아닌 대상을 높였다.', '높여야 할 대상을 높이지 않았다.', '간접 높임에서 특수 어휘를 잘못 썼다.', '객체 높임을 쓰지 않았다.', '상대 높임을 쓰지 않았다.']
        t = a[2]
        if '높일 대상이 아니' in t:
            right = why_names[0]
        elif '객체' in t:
            right = why_names[3]
        elif '계시다' in t or '없으시다' in t or '있으시다' in t:
            right = why_names[2]
        else:
            right = why_names[1]
        # '높일 대상이 아닌 대상을 높였다'와 '간접 높임에서 특수 어휘를 잘못 썼다'는 같은 오류를 달리 말한 것이 될 수 있어 서로의 오답으로 쓰지 않는다
        clash = {why_names[0]: why_names[2], why_names[2]: why_names[0]}
        extra = ['높임의 선어말 어미 \'-시-\'를 두 번 썼다.', '주격 조사 \'께서\' 대신 \'이/가\'를 써서 높이지 않았다.']
        ws = [w for w in why_names if w != right and w != clash.get(right)]
        ws += [x for x in extra if x not in ws][:4 - len(ws)]
        return mc(P('다음 문장이 어색한 이유로 가장 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % a[0], right, ws, steps=[a[2]], core=a[2], lv='상', fam='D', r=r, ref=[1], vertical=True)
    return tpl_tf(r, TFB.TF_HON, 'bad', lv='상', fam='E', ref=[1])

def _fix_item(r, a):
    others = [x for x in BADH if x[0] != a[0]]
    ws = [a[0]] + [x[0] for x in r.sample(others, 3)]
    ws = [w for w in ws]
    return mc(P('다음 문장을 높임법에 맞게 고친 것으로 가장 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % a[0], a[1], ws, steps=[a[2], '바르게 고치면: "%s"' % a[1]], core=a[2], lv='중', fam='A', r=r, ref=[1], vertical=True)

def tense_pool(r, n=40):
    xs = list(B.TENSE)
    xs += fresh(r, F.tense_s, n)
    xs += fresh(r, F.tense_rel, n // 2)
    return xs
TL = {'PA': '과거', 'PB': '과거', 'RA': '현재', 'RB': '현재', 'FA': '미래', 'FB': '미래'}
TD = {'PA': "선어말 어미 '-았/었-'으로 실현된 과거 시제이다.", 'PB': "관형사형 어미 '-(으)ㄴ/-던'으로 실현된 과거 시제이다.", 'RA': "선어말 어미 '-ㄴ/는-'으로 실현된 현재 시제이다.", 'RB': "관형사형 어미 '-는'으로 실현된 현재 시제이다.", 'FA': "선어말 어미 '-겠-/-리-'로 실현된 미래 시제이다.", 'FB': "관형사형 어미 '-(으)ㄹ'로 실현된 미래 시제이다."}

@T('hl040')
def g040(r, k):
    xs = tense_pool(r)
    c = r.randrange(8)
    P1 = pools_of(xs, lambda c: TL.get(c.split(':')[0]))
    D1 = {'과거': '과거 시제이다.', '현재': '현재 시제이다.', '미래': '미래 시제이다.'}
    if c <= 1:
        t = r.choice(['과거', '현재', '미래'])
        return t1(r, P1, t, '밑줄 친 부분이 %s 시제를 나타내는 것은?' % t, D1, '하' if c == 0 else '중', 'A', [2])
    if c == 2:
        P2 = pools_of(xs, lambda c: c.split(':')[0] if c.split(':')[0] in TD else None)
        t = r.choice(['PA', 'PB', 'RA', 'RB', 'FA', 'FB'])
        names = {'PA': "과거 시제 선어말 어미 '-았/었-'", 'PB': '과거 시제 관형사형 어미', 'RA': "현재 시제 선어말 어미 '-ㄴ/는-'", 'RB': "현재 시제 관형사형 어미 '-는'", 'FA': "미래 시제 선어말 어미 '-겠-'", 'FB': "미래 시제 관형사형 어미 '-(으)ㄹ'"}
        P3 = {t: P2.get(t, [])}
        for x in P2:
            if x != t:
                P3[x] = P2[x]
        return t1(r, P3, t, '밑줄 친 부분이 %s가 쓰인 것은?' % names[t], TD, '중', 'B', [2])
    if c == 3:
        a = r.choice([x for x in xs if any((c_.split(':')[0] in TD for _, _, c_ in x.segs))])
        i, t, code = [s for s in a.segs if s[2].split(':')[0] in TD][0]
        names = ['과거 시제 선어말 어미', '과거 시제 관형사형 어미', '현재 시제 선어말 어미', '현재 시제 관형사형 어미', '미래 시제 선어말 어미', '미래 시제 관형사형 어미']
        nm = {'PA': names[0], 'PB': names[1], 'RA': names[2], 'RB': names[3], 'FA': names[4], 'FB': names[5]}[code.split(':')[0]]
        return t_single(r, a, i, names, nm, '밑줄 친 부분에 나타난 시제의 실현 방법으로 알맞은 것은?', [TD[code.split(':')[0]]], '중', 'C', [2], TD[code.split(':')[0]])
    if c == 4:
        return tpl_tf(r, TFB.TF_TENSE, 'ok', lv='중', fam='D', ref=[2])
    if c == 5:
        return tpl_tf(r, TFB.TF_TENSE, 'bad', lv='중', fam='E', ref=[2])
    if c == 6:
        sents = [('어머니가 밥을 {먹는|RB} 아이를 불렀다.', '과거', '현재'), ('나는 책을 {읽는|RB} 친구를 보았다.', '과거', '현재'), ('우리는 노래를 {부르는|RB} 가수를 보았다.', '과거', '현재'), ('동생은 {웃는|RB} 아이를 안았다.', '과거', '현재'), ('선생님께서 {떠드는|RB} 학생을 부르셨다.', '과거', '현재'), ('그는 내가 {읽은|PB} 책을 빌려 갔다.', '과거', '과거'), ('나는 네가 {먹을|FB} 음식을 만들었다.', '과거', '미래'), ('우리는 내일 {떠날|FB} 사람을 배웅했다.', '과거', '미래')]
        s = r.choice(sents)
        a = Ann(s[0])
        opts_all = [('과거', '현재'), ('현재', '과거'), ('현재', '현재'), ('과거', '과거'), ('미래', '현재'), ('과거', '미래'), ('미래', '미래'), ('현재', '미래')]
        right = (s[1], s[2])
        ws = r.sample([o for o in opts_all if o != right], 4)
        fmt = lambda o: '절대 시제: %s, 상대 시제: %s' % o
        return mc(P('밑줄 친 관형사형 어미가 나타내는 시제를 절대 시제(발화시 기준)와 상대 시제(주절의 사건시 기준)로 나누어 설명한 것은?') + '<div class="bogi"><p>%s</p></div>' % a.html(under=[a.segs[0][0]]), fmt(right), [fmt(w) for w in ws], steps=['주절의 서술어가 과거이므로 절대 시제로는 %s이고, 주절의 사건시를 기준으로 하면 상대 시제는 %s이다.' % right], core='절대 시제와 상대 시제', lv='최', fam='F', r=r, ref=[2], vertical=True)
    return tpl_tf(r, TFB.TF_TENSE, 'bad', lv='상', fam='G', ref=[2])
SUBU = {
    '상황의 지속(현재 상태)': ['나는 아버지와 많이 {닮았|X}다.', '지금 보니 엄마와 나는 쌍둥이처럼 {닮았|X}다.', '그 아이는 제 어머니를 꼭 {닮았|X}다.', '이 건물은 지은 지 오래되어 아주 {낡았|X}다.'],
    '미래에 대한 확신': ['너 이제 언니한테 {혼났|X}다.', '너 이제 엄마한테 {죽었|X}다.'],
    '과거와 단절된 상황': ['나는 오늘 집에 일찍 {왔었|X}다.', '우리 가족은 청주에 {살았었|X}다.', '그 가게는 예전에 이 자리에 {있었었|X}다.'],
    '추측': ['서울에는 비가 많이 왔{겠|X}다.', '지금쯤 동생은 집에 도착했{겠|X}다.', '밖이 많이 춥{겠|X}다.', '그 소식을 들으면 부모님이 기뻐하시{겠|X}다.', '어제는 정말 힘들었{겠|X}다.'],
    '주체의 의지': ['나는 꼭 축구 선수가 되{겠|X}다.', '저는 내일부터 열심히 공부하{겠|X}습니다.', '이번 방학에는 책을 열 권 읽{겠|X}다.', '나는 이 일을 끝까지 해내{겠|X}다.'],
    '가능성·능력': ['그 정도는 나도 다 먹{겠|X}다.', '저 정도 높이는 나도 뛰어넘{겠|X}다.'],
    '단순한 미래': ['내일은 눈이 내리{겠|X}습니다.', '오늘 저녁에는 비가 오{겠|X}습니다.', '다음 열차는 곧 도착하{겠|X}습니다.'],
    '보편적 사실(현재 시제)': ['물은 위에서 아래로 {흐른|X}다.', '지구는 태양을 {돈|X}다.', '봄이 오면 꽃이 {핀|X}다.'],
    '확정된 미래(현재 시제)': ['나는 내일 프랑스에 {간|X}다.', '우리는 모레 서울로 {떠난|X}다.', '다음 달에 우리는 이사를 {간|X}다.'],
    '지난 일의 회상': ['영희가 식당에서 밥을 먹{더|X}라.', '그 아이는 참 착하{더|X}라.', '어제 보니 동생이 책을 읽{더|X}라.', '그곳은 경치가 참 좋{더|X}라.'],
}
SUBU_NAME = {'상황의 지속(현재 상태)': "'-았-'이 상황의 지속(현재 상태)을 나타낸다.", '미래에 대한 확신': "'-았-'이 미래에 대한 확신을 나타낸다.", '과거와 단절된 상황': "'-았었-'이 현재와 단절된 과거를 나타낸다.", '추측': "'-겠-'이 추측을 나타낸다.", '주체의 의지': "'-겠-'이 주체의 의지를 나타낸다.", '가능성·능력': "'-겠-'이 가능성이나 능력을 나타낸다.", '단순한 미래': "'-겠-'이 단순한 미래를 나타낸다.", '보편적 사실(현재 시제)': '현재 시제가 보편적 사실을 나타낸다.', '확정된 미래(현재 시제)': '현재 시제가 확정된 미래를 나타낸다.', '지난 일의 회상': "'-더-'가 지난 일의 회상을 나타낸다."}

@T('hl041')
def g041(r, k):
    c = r.randrange(6)
    items = [(m, Ann(s)) for m, ss in SUBU.items() for s in ss]
    items = [(m, a) for m, a in items if a.segs]
    pools = {}
    for m, a in items:
        pools.setdefault(m, []).append((a, a.segs[0][0]))
    if c <= 1:
        t = r.choice(list(pools))
        grp = r.choice([['추측', '주체의 의지', '가능성·능력'], ['상황의 지속(현재 상태)', '미래에 대한 확신', '과거와 단절된 상황', '지난 일의 회상'], ['보편적 사실(현재 시제)', '확정된 미래(현재 시제)', '단순한 미래']])   # '추측'과 '단순한 미래'(일기 예보 등)는 겹쳐 읽히므로 한 문항에 함께 두지 않는다
        if t not in grp:
            t = grp[0]
        P2 = {g: pools[g] for g in grp}
        return t1(r, P2, t, '밑줄 친 부분의 의미가 %s인 것은?' % t.replace('(현재 시제)', ''), SUBU_NAME, '중' if c == 0 else '상', 'A', [2])
    if c == 2:
        m = r.choice(list(pools))
        a, i = r.choice(pools[m])
        return t_single(r, a, i, [x for x in pools if {x, m} != {'추측', '단순한 미래'}], m, '밑줄 친 부분이 나타내는 의미로 알맞은 것은?', [SUBU_NAME[m]], '중', 'B', [2], SUBU_NAME[m])
    if c == 3:
        pairs = [('나는 오늘 집에 일찍 왔다.', '나는 오늘 집에 일찍 왔었다.', '왔다'), ('그는 서울에 살았다.', '그는 서울에 살았었다.', '살았다'), ('나는 어제 이 옷을 입었다.', '나는 어제 이 옷을 입었었다.', '입었다')]
        a = r.choice(pairs)
        right = '㉡은 ㉠과 달리 과거의 일이 현재와 단절되었음을 나타낸다.'
        wrongs = ['㉠은 ㉡과 달리 과거의 일이 현재와 단절되었음을 나타낸다.', '㉠과 ㉡은 모두 미래의 일을 나타낸다.', '㉠은 ㉡과 달리 상대 시제를 나타낸다.', '㉡은 ㉠과 달리 현재 시제를 나타낸다.']
        body = P('㉠, ㉡에 대한 설명으로 가장 적절한 것은?') + BOX(['㉠ ' + a[0], '㉡ ' + a[1]])
        return mc(body, right, wrongs, steps=["'-았었/었었-'은 과거의 일이 지금은 이어지지 않는 '단절'의 의미를 함의한다. '-았/었-'은 과거 이후 상태가 이어질 수 있다."], core="'-았었-'의 단절 의미", lv='상', fam='C', r=r, ref=[2], vertical=True)
    if c == 4:
        return tpl_tf(r, TFB.TF_TENSE, 'ok', lv='중', fam='D', ref=[2])
    return tpl_tf(r, TFB.TF_TENSE, 'bad', lv='상', fam='E', ref=[2])
ASP_L = {'PG': '진행상', 'CM': '완료상'}
ASP_D = {'PG': "진행상: '-고 있다', '-아/어 가다', '-(으)면서' 등으로 동작이 진행 중임을 나타낸다.", 'CM': "완료상: '-아/어 있다', '-아/어 버리다', '-고서' 등으로 동작이 완료되었음을 나타낸다."}

@T('hl042')
def g042(r, k):
    xs = list(B.ASPECT) + fresh(r, F.aspect_s, 40, 'PG') + fresh(r, F.aspect_s, 40, 'CM')
    P1 = pools_of(xs, lambda c: ASP_L.get(c.split(':')[0]))
    P1.update({})
    c = r.randrange(7)
    if c <= 1:
        return t1(r, P1, '진행상', '밑줄 친 부분이 진행상을 나타내는 것은?', {'진행상': ASP_D['PG'], '완료상': ASP_D['CM']}, '하', 'A', [2])
    if c == 2:
        return t1(r, P1, '완료상', '밑줄 친 부분이 완료상을 나타내는 것은?', {'진행상': ASP_D['PG'], '완료상': ASP_D['CM']}, '하', 'B', [2])
    if c == 3:
        t = r.choice(['진행상', '완료상'])
        a, i = r.choice(P1[t])
        return t_single(r, a, i, ['진행상', '완료상', '과거 시제', '현재 시제', '미래 시제'], t, '밑줄 친 부분이 나타내는 동작상은?', [ASP_D['PG' if t == '진행상' else 'CM']], '중', 'C', [2], ASP_D['PG' if t == '진행상' else 'CM'])
    if c == 4:
        conn = {'진행상': ['음악을 {들으면서|PG} 청소를 한다.', '노래를 {부르면서|PG} 걷는다.', '밥을 {먹으면서|PG} 텔레비전을 본다.'], '완료상': ['산책을 {하고서|CM} 집으로 갔다.', '밥을 {먹고서|CM} 학교에 갔다.', '손을 {씻고서|CM} 식사를 했다.']}
        t = r.choice(list(conn))
        a = Ann(r.choice(conn[t]))
        return t_single(r, a, a.segs[0][0], ['진행상', '완료상', '과거 시제', '피동 표현', '사동 표현'], t, '밑줄 친 연결 어미가 나타내는 동작상은?', [ASP_D['PG' if t == '진행상' else 'CM']], '상', 'D', [2], ASP_D['PG' if t == '진행상' else 'CM'])
    if c == 5:
        return tpl_tf(r, TFB.TF_TENSE, r.choice(['ok', 'bad']), lv='중', fam='E', ref=[2])
    stm = []
    for a in r.sample(xs, 3):
        i, t, code = a.segs[0]
        kd = code.split(':')[0]
        if kd not in ASP_L:
            return None
        truth = r.random() < 0.5
        n = kd if truth else 'CM' if kd == 'PG' else 'PG'
        stm.append(('「%s」의 밑줄 친 부분은 %s을 나타낸다.' % (a.html(under=[i]), ASP_L[n]), truth, "'%s'은(는) %s이다." % (t, ASP_L[kd])))
    return bogi('동작상에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='F', r=r, ref=[2], ask='')
VPL = {'PP': '파생적 피동', 'PT': '통사적 피동', 'PN': '피동', 'CD': '파생적 사동', 'CT': '통사적 사동', 'CN': '사동', 'AC': '능동', 'JD': '주동'}
VG = {'피동': ('PP', 'PT', 'PN'), '사동': ('CD', 'CT', 'CN'), '능동·주동': ('AC', 'JD')}

def vgroup(c):
    k_ = c.split(':')[0]
    for g, v in VG.items():
        if k_ in v:
            return g
VD = {'피동': '주어가 다른 주체에 의해 동작을 당하는 피동 표현이다.', '사동': '주어가 남에게 동작을 하도록 시키는 사동 표현이다.', '능동·주동': '주어가 동작을 직접 하는 능동(주동) 표현이다.'}

def voice_pool(r):
    xs = list(B.VOICE)
    for a, b, t, w in B2.PASS + B2.CAUSE:
        xs += [a, b]
    return xs

@T('hl043')
def g043(r, k):
    xs = voice_pool(r)
    P1 = pools_of(xs, vgroup)
    P2 = pools_of(xs, lambda c: {'PP': '파생적 피동', 'PT': '통사적 피동', 'PN': '파생적 피동', 'CD': '사동', 'CT': '사동', 'CN': '사동', 'AC': '능동', 'JD': '주동'}.get(c.split(':')[0]))
    c = r.randrange(8)
    if c <= 1:
        return t1(r, P1, '피동', '밑줄 친 부분이 피동 표현인 것은?', VD, '중', 'A', [3])
    if c == 2:
        P3 = {'파생적 피동': P2['파생적 피동'], '통사적 피동': P2['통사적 피동'], '사동': P2['사동'], '능동': P2['능동']}
        return t1(r, P3, '파생적 피동', '밑줄 친 부분이 파생적 피동 표현인 것은?', {'파생적 피동': "피동 접미사 '-이-, -히-, -리-, -기-'가 결합한 피동사이다.", '통사적 피동': "'-아/어지다'가 결합한 통사적 피동이다.", '사동': VD['사동'], '능동': VD['능동·주동']}, '중', 'B', [3])
    if c == 3:
        P3 = {'통사적 피동': P2['통사적 피동'], '파생적 피동': P2['파생적 피동'], '사동': P2['사동'], '능동': P2['능동']}
        return t1(r, P3, '통사적 피동', "밑줄 친 부분이 '-아/어지다' 등이 결합한 통사적 피동 표현인 것은?", {'파생적 피동': '피동 접미사가 결합한 피동사이다.', '통사적 피동': "'-아/어지다'가 결합한 통사적 피동이다.", '사동': VD['사동'], '능동': VD['능동·주동']}, '상', 'C', [3])
    if c == 4:
        a, b, t, w = r.choice(B2.PASS)
        names = ['능동문의 목적어가 피동문의 주어가 되고, 능동문의 주어는 부사어가 된다.', '능동문의 주어가 피동문의 목적어가 되고, 능동문의 목적어는 주어가 된다.', '능동문의 주어와 목적어가 모두 피동문에서 사라진다.', '능동문의 서술어는 그대로 쓰이고 조사만 바뀐다.', '능동문의 목적어가 피동문의 부사어가 되고, 주어는 그대로 주어가 된다.']
        body = P('(가)를 (나)로 바꿀 때 나타나는 문장 성분의 변화로 옳은 것은?') + BOX(['(가) ' + a.plain(), '(나) ' + b.plain()])
        return mc(body, names[0], names[1:], steps=[w], core='능동문을 피동문으로 바꿀 때의 성분 변화', lv='상', fam='D', r=r, ref=[3], vertical=True)
    if c == 5:
        pools = {'피동': P1['피동'], '비피동': P1['사동'] + P1['능동·주동']}
        return t1(r, pools, '비피동', '밑줄 친 부분이 피동 표현이 아닌 것은?', {'피동': VD['피동'], '비피동': '피동이 아닌 표현(사동 또는 능동·주동)이다.'}, '중', 'E', [3])
    if c == 6:
        return tpl_tf(r, TFB.TF_VOICE, 'ok', lv='중', fam='F', ref=[3])
    stm = []
    for a in r.sample([x for x in xs if x.segs and x.segs[0][2].split(':')[0] in VPL], 3):
        i, t, code = a.segs[0]
        kd = code.split(':')[0]
        truth = r.random() < 0.5
        # '피동'·'사동'처럼 넓은 이름은 그 아래 갈래(파생적·통사적)에도 맞는 말이므로 거짓 선택지로 쓰지 않는다
        fits = lambda n: n == kd or (VPL[n] == '피동' and kd in VG['피동']) or (VPL[n] == '사동' and kd in VG['사동']) or (n == 'PP' and kd == 'PN') or {n, kd} == {'AC', 'JD'}
        alts = [x for x in VPL if not fits(x)]
        n = kd if truth else r.choice(alts)
        stm.append(('「%s」의 밑줄 친 부분은 %s 표현이다.' % (a.html(under=[i]), VPL[n]), truth, "'%s'은(는) %s이다. %s" % (t, VPL[kd], '')))
    return bogi('다음 문장에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='G', r=r, ref=[3], ask='')

@T('hl044')
def g044(r, k):
    c = r.randrange(7)
    ok_s = [(s, w) for s, w in B.DBL_OK] + [(g, '적절한 표현이다.') for _, g, _ in B.DBL]
    if c <= 1:
        a = r.choice(B.DBL)
        ok = r.sample(ok_s, 4)
        return mc(P('다음 중 이중 피동이 쓰인 문장은?'), a[0], [o[0] for o in ok], steps=['"%s": %s' % (a[0], a[2])] + ['"%s": %s' % o for o in ok], core=a[2], lv='중', fam='A', r=r, ref=[3], vertical=True)
    if c == 2:
        a = r.choice(ok_s)
        bs = r.sample(B.DBL, 4)
        return mc(P('다음 중 이중 피동이 쓰이지 않은 문장은?'), a[0], [b[0] for b in bs], steps=['"%s": %s' % a] + ['"%s": %s' % (b[0], b[2]) for b in bs], core='이중 피동 판별', lv='중', fam='B', r=r, ref=[3], vertical=True)
    if c == 3:
        a = r.choice(B.DBL)
        wrongs = [x[0] for x in r.sample([y for y in B.DBL if y[0] != a[0]], 3)] + [a[0]]
        return mc(P('다음 문장을 올바르게 고친 것은?') + '<div class="bogi"><p>%s</p></div>' % a[0], a[1], wrongs, steps=[a[2], '바르게 고치면: "%s"' % a[1]], core=a[2], lv='중', fam='C', r=r, ref=[3], vertical=True)
    if c == 4:
        a = r.choice(B.SIDONG_BAD)
        gs = r.sample(ok_s, 4)
        return mc(P("다음 중 사동 접미사나 '-시키다'가 불필요하게 쓰인 문장은?"), a[0], [g[0] for g in gs], steps=['"%s": %s' % (a[0], a[2])], core=a[2], lv='상', fam='D', r=r, ref=[3], vertical=True)
    if c == 5:
        a = r.choice(B.DBL)
        verb = a[2].split("'")[1] if "'" in a[2] else ''
        names = ["이미 피동 표현이 된 말에 '-어지다'를 또 붙여 피동이 두 번 나타났다.", '피동사에 사동 접미사가 중복되었다.', '능동사에 피동 접미사가 중복되었다.', '주어와 서술어의 호응이 맞지 않는다.', '높임 표현이 중복되었다.']
        return mc(P('다음 문장이 잘못된 이유로 알맞은 것은?') + '<div class="bogi"><p>%s</p></div>' % a[0], names[0], names[1:], steps=[a[2]], core=a[2], lv='중', fam='E', r=r, ref=[3], vertical=True)
    return tpl_tf(r, TFB.TF_VOICE, 'bad', lv='상', fam='F', ref=[3])

@T('hl045')
def g045(r, k):
    xs = voice_pool(r)
    P2 = pools_of(xs, lambda c: {'PP': '피동', 'PT': '피동', 'PN': '피동', 'CD': '파생적 사동', 'CT': '통사적 사동', 'CN': '시키다 사동', 'AC': '능동', 'JD': '주동'}.get(c.split(':')[0]))
    P1 = pools_of(xs, vgroup)
    c = r.randrange(8)
    D = {'피동': VD['피동'], '파생적 사동': "사동 접미사 '-이-, -히-, -리-, -기-, -우-, -구-, -추-'가 결합한 사동사이다.", '통사적 사동': "'-게 하다'가 결합한 통사적 사동이다.", '시키다 사동': "명사에 '-시키다'가 붙은 사동 표현이다.", '능동': VD['능동·주동'], '주동': VD['능동·주동']}
    if c <= 1:
        return t1(r, P1, '사동', '밑줄 친 부분이 사동 표현인 것은?', VD, '중', 'A', [4])
    if c == 2:
        return t1(r, {x: P2[x] for x in ('파생적 사동', '통사적 사동', '피동', '주동')}, '파생적 사동', '밑줄 친 부분이 파생적 사동 표현인 것은?', D, '중', 'B', [4])
    if c == 3:
        return t1(r, {x: P2[x] for x in ('통사적 사동', '파생적 사동', '피동', '주동')}, '통사적 사동', "밑줄 친 부분이 '-게 하다'가 결합한 통사적 사동 표현인 것은?", D, '상', 'C', [4])
    if c == 4:
        a, b, t, w = r.choice(B2.CAUSE)
        names = ['새로운 주어가 도입되고, 주동문의 주어는 목적어나 부사어가 된다.', '주동문의 주어가 사동문에서 사라진다.', '주동문의 목적어가 사동문의 주어가 된다.', '주동문의 서술어는 바뀌지 않고 조사만 바뀐다.', '사동문에서는 목적어가 반드시 사라진다.']
        body = P('(가)를 (나)로 바꿀 때 나타나는 변화로 옳은 것은?') + BOX(['(가) ' + a.plain(), '(나) ' + b.plain()])
        return mc(body, names[0], names[1:], steps=[w], core='주동문을 사동문으로 바꿀 때의 성분 변화', lv='상', fam='D', r=r, ref=[4], vertical=True)
    if c == 5:
        pools = {'사동': P1['사동'], '비사동': P1['피동'] + P1['능동·주동']}
        return t1(r, pools, '비사동', '밑줄 친 부분이 사동 표현이 아닌 것은?', {'사동': VD['사동'], '비사동': '사동이 아닌 표현(피동 또는 능동·주동)이다.'}, '중', 'E', [4])
    if c == 6:
        return tpl_tf(r, TFB.TF_VOICE, 'ok', lv='중', fam='F', ref=[4])
    return tpl_tf(r, TFB.TF_VOICE, 'bad', lv='상', fam='G', ref=[4])
CAUS_AMB = [('어머니가 동생에게 옷을 입혔다.', '직접·간접', 'both'), ('어머니가 아기에게 밥을 먹였다.', '직접·간접', 'both'), ('어머니가 누나에게 책을 읽혔다.', '직접·간접', 'both'), ('선생님이 학생을 의자에 앉혔다.', '직접·간접', 'both'), ('엄마가 아기를 재웠다.', '직접·간접', 'both'), ('아버지가 아이를 버스에 태웠다.', '직접·간접', 'both'), ('어머니가 동생에게 옷을 입게 했다.', '간접', 'ind'), ('어머니가 아기에게 밥을 먹게 했다.', '간접', 'ind'), ('어머니가 누나에게 책을 읽게 했다.', '간접', 'ind'), ('선생님이 학생을 의자에 앉게 했다.', '간접', 'ind'), ('엄마가 아기를 자게 했다.', '간접', 'ind'), ('아버지가 아이를 버스에 타게 했다.', '간접', 'ind')]
CAU_OPT = ['직접 사동의 의미로만 해석된다.', '간접 사동의 의미로만 해석된다.', '직접 사동과 간접 사동의 의미로 모두 해석될 수 있다.', '사동의 의미가 없다.', '피동의 의미로 해석된다.']

@T('hl046')
def g046(r, k):
    c = r.randrange(6)
    if c <= 1:
        s, kd, f = r.choice(CAUS_AMB)
        right = CAU_OPT[2] if f == 'both' else CAU_OPT[1]
        return mc(P('다음 문장에 대한 설명으로 옳은 것은?') + '<div class="bogi"><p>%s</p></div>' % s, right, [o for o in CAU_OPT if o != right], steps=['파생적 사동(-이-, -히- 등)은 직접·간접 사동으로 모두 해석되는 중의성이 있지만, 통사적 사동(-게 하다)은 간접 사동으로만 해석된다.'], core='직접 사동과 간접 사동', lv='상', fam='A', r=r, ref=[4])
    if c == 2:
        both = [x for x in CAUS_AMB if x[2] == 'both']
        ind = [x for x in CAUS_AMB if x[2] == 'ind']
        a = r.choice(both)
        return mc(P('다음 중 간접 사동의 의미로만 해석되는 문장은?'), r.choice(ind)[0], [x[0] for x in r.sample(both, 4)], steps=["'-게 하다'가 쓰인 통사적 사동문은 간접 사동으로만 해석된다.", '파생적 사동문은 직접·간접 사동의 두 가지로 해석될 수 있다.'], core='통사적 사동은 간접 사동', lv='상', fam='B', r=r, ref=[4], vertical=True)
    if c == 3:
        both = [x for x in CAUS_AMB if x[2] == 'both']
        ind = [x for x in CAUS_AMB if x[2] == 'ind']
        return mc(P('다음 중 직접 사동과 간접 사동의 두 가지 의미로 해석될 수 있는 문장은?'), r.choice(both)[0], [x[0] for x in r.sample(ind, 4)], steps=['파생적 사동문은 직접·간접 사동으로 해석될 수 있다.', "'-게 하다' 사동문은 간접 사동의 의미만 갖는다."], core='파생적 사동의 중의성', lv='중', fam='C', r=r, ref=[4], vertical=True)
    if c == 4:
        stm = []
        for s, kd, f in r.sample(CAUS_AMB, 3):
            truth = r.random() < 0.5
            claim = '두 가지로 해석될 수 있다' if f == 'both' else '간접 사동으로만 해석된다'
            other = '간접 사동으로만 해석된다' if f == 'both' else '두 가지로 해석될 수 있다'
            stm.append(('「%s」는 %s.' % (s, claim if truth else other), truth, '이 문장은 %s' % ('파생적 사동문으로 직접·간접 사동으로 해석될 수 있다.' if f == 'both' else '통사적 사동문으로 간접 사동으로만 해석된다.')))
        return bogi('사동문의 의미에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='최', fam='D', r=r, ref=[4], ask='')
    return tpl_tf(r, TFB.TF_VOICE, 'ok', lv='중', fam='E', ref=[4])

@T('hl047')
def g047(r, k):
    c = r.randrange(6)
    if c <= 1:
        a, b, t, w = r.choice(B2.PASS)
        names = ['능동문의 목적어가 피동문의 주어가 되고, 능동문의 주어는 부사어가 된다.', '능동문의 주어가 피동문의 목적어가 되고, 능동문의 목적어는 주어가 된다.', '능동문의 주어와 목적어가 모두 그대로 유지된다.', '능동문의 서술어는 그대로 쓰이고 조사만 바뀐다.', '능동문의 목적어가 피동문의 부사어가 되고, 주어는 그대로 주어가 된다.']
        body = P('능동문 (가)를 피동문 (나)로 바꿀 때의 설명으로 옳은 것은?') + BOX(['(가) ' + a.plain(), '(나) ' + b.plain()])
        return mc(body, names[0], names[1:], steps=[w], core='능동문→피동문', lv='중', fam='A', r=r, ref=[3], vertical=True)
    if c == 2:
        a, b, t, w = r.choice(B2.CAUSE)
        names = ['새로운 주어가 도입되고, 주동문의 주어는 목적어나 부사어가 된다.', '주동문의 주어가 그대로 사동문의 주어가 된다.', '주동문의 목적어가 사동문의 주어가 된다.', '주동문의 서술어는 그대로 쓰인다.', '사동문에서는 부사어가 반드시 사라진다.']
        body = P('주동문 (가)를 사동문 (나)로 바꿀 때의 설명으로 옳은 것은?') + BOX(['(가) ' + a.plain(), '(나) ' + b.plain()])
        return mc(body, names[0], names[1:], steps=[w], core='주동문→사동문', lv='중', fam='B', r=r, ref=[3], vertical=True)
    if c == 3:
        a, b, t, w = r.choice(B2.PASS + B2.CAUSE)
        va = a.segs[-1][1]
        vb = b.segs[-1][1]
        sel = {'PP': '피동 접미사가 결합하여', 'PT': "'-어지다'가 결합하여", 'PN': "'-되다'로 바뀌어", 'CD': '사동 접미사가 결합하여', 'CT': "'-게 하다'가 결합하여", 'CN': "'-시키다'가 결합하여"}[t]
        right = "서술어가 '%s'에서 '%s'(으)로 %s 바뀌었다." % (va, vb, sel)
        wrongs = ["서술어가 '%s'에서 '%s'(으)로 %s 바뀌었다." % (va, vb, x) for x in ['사동 접미사가 결합하여', '피동 접미사가 결합하여', "'-게 되다'가 결합하여", "'-시키다'가 결합하여", "'-어지다'가 결합하여", "'-되다'로 바뀌어", "'-게 하다'가 결합하여"] if x != sel]
        return mc(P('(가)를 (나)로 바꿀 때 서술어에 나타난 변화로 옳은 것은?') + BOX(['(가) ' + a.plain(), '(나) ' + b.plain()]), right, r.sample(wrongs, 4), steps=["(나)의 서술어 '%s'은(는) %s 만들어진 표현이다." % (vb, sel)], core='서술어의 변화', lv='상', fam='C', r=r, ref=[3], vertical=True)
    if c == 4:
        ok = []
        for a, b, t, w in B2.PASS:
            ta = a.plain().rstrip('.').split(' ')
            tb = b.plain().rstrip('.').split(' ')
            if len(ta) == 3 and len(tb) == 3 and (t == 'PP'):
                ok.append((a, b, ta, tb, w))
        a, b, ta, tb, w = r.choice(ok)

        def base(x):
            return x[:-1]
        right = b.plain()
        wrongs = []
        n1 = ta[0][:-1]
        n2 = ta[1][:-1]
        va = ta[2]
        vb = tb[2].rstrip('.')
        j = lambda s, y, n: s + (y if (ord(s[-1]) - 44032) % 28 else n)
        wrongs = ['%s %s %s.' % (j(n1, '이', '가'), j(n2, '에게', '에게'), vb.rstrip('.')), '%s %s %s.' % (j(n2, '이', '가'), j(n1, '을', '를'), vb.rstrip('.')), '%s %s %s.' % (j(n2, '이', '가'), n1 + '에게', va.rstrip('.')), '%s %s %s.' % (j(n2, '이', '가'), n1 + '에게', vb.rstrip('.')[:-1] + '졌다')]
        if len({right} | set(wrongs)) < 5:
            return None
        return mc(P('다음 능동문을 피동문으로 바꾼 것으로 가장 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % a.plain(), right, wrongs, steps=[w], core='능동문→피동문', lv='상', fam='D', r=r, ref=[3], vertical=True)
    return tpl_tf(r, TFB.TF_VOICE, r.choice(['ok', 'bad']), lv='중', fam='E', ref=[3])
NEGL = {'NS': "짧은 '안' 부정문", 'NL': "긴 '-지 않다' 부정문", 'MS': "짧은 '못' 부정문", 'ML': "긴 '-지 못하다' 부정문", 'MA': "'-지 말다' 부정문"}
NEG_G = {'안 부정문': ('NS', 'NL'), '못 부정문': ('MS', 'ML'), '말다 부정문': ('MA',)}

@T('hl048')
def g048(r, k):
    xs = B.NEG
    P1 = pools_of(xs, lambda c: NEGL.get(c.split(':')[0]))
    PG_ = pools_of(xs, lambda c: next((g for g, v in NEG_G.items() if c.split(':')[0] in v), None))
    c = r.randrange(7)
    D = {v: B.NEG_CODE[k_][1] for k_, v in NEGL.items()}
    DG = {'안 부정문': '안 부정문: 단순 부정·의지 부정을 나타낸다.', '못 부정문': '못 부정문: 능력 부정·타의 부정을 나타낸다.', '말다 부정문': '말다 부정문: 명령문·청유문에서 금지를 나타낸다.'}
    if c <= 1:
        t = r.choice(list(DG))
        return t1(r, PG_, t, '밑줄 친 부분이 %s인 것은?' % t, DG, '하' if c == 0 else '중', 'A', [5])
    if c == 2:
        t = r.choice(list(NEGL.values()))
        return t1(r, P1, t, '밑줄 친 부분이 %s인 것은?' % t, D, '중', 'B', [5])
    if c == 3:
        a = r.choice(xs)
        i, tx, code = a.segs[0]
        return t_single(r, a, i, list(NEGL.values()), NEGL[code.split(':')[0]], '밑줄 친 부정 표현의 유형은?', [D[NEGL[code.split(':')[0]]]], '중', 'C', [5], D[NEGL[code.split(':')[0]]])
    if c == 4:
        right = r.choice(['학교에 안 가라.', '학교에 못 가라.', '이 책을 안 읽자.', '지금 집에 못 가자.'])
        ws = ['학교에 가지 마라.', '이 책을 읽지 말자.', '떠들지 마세요.', '여기서 담배를 피우지 마라.']
        return mc(P('다음 중 한글 문법에 맞지 않는 부정 표현은?'), right, ws, steps=["명령문과 청유문에서는 '안'이나 '못'을 쓰지 않고 '-지 말다'를 쓴다."], core='말다 부정문', lv='상', fam='D', r=r, ref=[5], vertical=True)
    if c == 5:
        ex = [('나는 다리를 다쳐서 달리기를 못 했다.', '능력·타의 부정'), ('그는 일부러 말을 안 했다.', '의지 부정'), ('어제는 비가 안 왔다.', '단순 부정'), ('감기에 걸려 학교에 못 갔다.', '타의에 의한 부정')]
        a = r.choice(ex)
        names = ['능력이 없거나 외부 원인 때문에 그렇게 하지 못했다는 부정', '하고자 하는 의지가 없어서 하지 않았다는 부정', '단순히 그런 일이 없었다는 부정', '금지·명령의 부정', '청유의 부정']
        right = {'능력·타의 부정': names[0], '타의에 의한 부정': names[0], '의지 부정': names[1], '단순 부정': names[2]}[a[1]]
        return mc(P('다음 문장에 쓰인 부정문의 의미로 알맞은 것은?') + '<div class="bogi"><p>%s</p></div>' % a[0], right, [n for n in names if n != right], steps=["'안'은 단순 부정·의지 부정, '못'은 능력 부정·타의 부정을 나타낸다."], core='부정문의 의미', lv='중', fam='E', r=r, ref=[5], vertical=True)
    return tpl_tf(r, TFB.TF_NEGEND, r.choice(['ok', 'bad']), lv='중', fam='F', ref=[5])
ENDL = {'EP': '평서문', 'EQ': '의문문', 'EC': '명령문', 'EH': '청유문', 'EX': '감탄문'}

@T('hl049')
def g049(r, k):
    xs = B.END
    P1 = pools_of(xs, lambda c: ENDL.get(c.split(':')[0]))
    D = {v: B.END_CODE[k_][1] for k_, v in ENDL.items()}
    c = r.randrange(7)
    if c <= 1:
        t = r.choice(list(D))
        return t1(r, P1, t, '밑줄 친 종결 어미가 %s을 만드는 것은?' % t, D, '하', 'A', [5])
    if c == 2:
        a = r.choice(xs)
        i, tx, code = a.segs[0]
        return t_single(r, a, i, list(D), ENDL[code.split(':')[0]], '밑줄 친 부분이 나타내는 문장의 종류는?', [D[ENDL[code.split(':')[0]]]], '하', 'B', [5], D[ENDL[code.split(':')[0]]])
    if c == 3:
        s, f, fn, w = r.choice(B.INDIRECT)
        names = ['창문을 닫아 달라는 요청', '길을 알려 달라는 요청', '조용히 해 달라는 요청', '소금을 건네 달라는 요청', '시간을 알려 달라는 요청', '치우라는 간접적 명령', '답변을 요구하지 않고 감탄·동의를 구함(수사 의문문)']
        fnn = fn.replace('(명령)', '')
        right = fn
        pool = [x[2] for x in B.INDIRECT if x[2] != fn]
        return mc(P('다음 문장의 실제 기능으로 가장 적절한 것은?') + '<div class="bogi"><p>%s</p></div>' % s, right, r.sample(pool, 4), steps=[w], core='문장의 형식과 기능', lv='상', fam='C', r=r, ref=[5], vertical=True)
    if c == 4:
        ex = [('개학이 언제지?', '설명 의문문', "의문사 '언제'를 사용하여 설명을 요구한다."), ('주말에 시간 있으세요?', '판정 의문문', '의문사 없이 긍정·부정의 대답을 요구한다.'), ('이 영화 정말 좋지 않니?', '수사 의문문', '답변을 요구하지 않고 서술·감탄의 효과를 낸다.'), ('너는 어디에 가니?', '설명 의문문', "의문사 '어디'를 사용하여 설명을 요구한다."), ('지금 비가 오니?', '판정 의문문', '의문사 없이 긍정·부정의 대답을 요구한다.'), ('이게 말이 되니?', '수사 의문문', '답변을 요구하지 않고 부정의 서술 효과를 낸다.'), ('누가 왔니?', '설명 의문문', "의문사 '누구(누가)'를 사용하여 설명을 요구한다."), ('밥 먹었니?', '판정 의문문', '의문사 없이 긍정·부정의 대답을 요구한다.')]
        a = r.choice(ex)
        names = ['설명 의문문', '판정 의문문', '수사 의문문', '명령문', '청유문']
        return mc(P('밑줄 친 문장은 어떤 의문문인가?') + '<div class="bogi"><p>%s</p></div>' % a[0], a[1], [n for n in names if n != a[1]], steps=[a[2]], core='의문문의 종류', lv='중', fam='D', r=r, ref=[5], vertical=False)
    if c == 5:
        return tpl_tf(r, TFB.TF_NEGEND, 'bad', lv='중', fam='E', ref=[5])
    return tpl_tf(r, TFB.TF_NEGEND, 'ok', lv='중', fam='F', ref=[5])
