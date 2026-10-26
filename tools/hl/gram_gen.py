# -*- coding: utf-8 -*-
"""문법 문제 엔진: 주석 문장(Ann)에서 여러 형식의 문항을 만든다."""
import random
from hllib import *
from ann import Ann

CIRC = '㉠㉡㉢㉣㉤㉥'

def opt(a, idx):
    return a.html(under=[idx])

def pick_seg(r, a, filt):
    c = [(i, t, c) for i, t, c in a.segs if filt(c)]
    return r.choice(c) if c else None


def t1(r, pools, target, ask, desc, lv='중', fam='A', ref=None, vertical=True, core=None, extra=''):
    """pools: {라벨: [(Ann, 분절 인덱스)]}. target 라벨의 문장 1 + 다른 라벨들에서 4(서로 다른 문장).
    desc: 라벨 → 설명(풀이)."""
    if not pools.get(target): return None
    others = [l for l in pools if l != target and pools[l]]
    if not others: return None
    a, i = r.choice(pools[target])
    right = opt(a, i)
    wrongs, wl, used = [], [], {a.s}
    tries = 0
    while len(wrongs) < 4 and tries < 40:
        tries += 1
        l = r.choice(others)
        b, j = r.choice(pools[l])
        if b.s in used: continue
        h = opt(b, j)
        if h in wrongs: continue
        used.add(b.s); wrongs.append(h); wl.append((b, j, l))
    if len(wrongs) < 4: return None
    st = ['%s: %s' % (plain(right), desc.get(target, target))]
    for (b, j, l) in wl:
        st.append('%s: %s' % (plain(opt(b, j)), desc.get(l, l)))
    return mc(P(ask) + extra, right, wrongs, steps=st, core=core or desc.get(target, ''), lv=lv, fam=fam, r=r, ref=ref, vertical=vertical)


def t_single(r, a, idx, names, right_name, ask, steps, lv='하', fam='B', ref=None, core='', k=5, extra=''):
    """한 문장의 한 부분을 밑줄 치고 이름 고르기(선택지는 용어)."""
    pool = [n for n in names if n != right_name]
    if len(pool) < 4: return None
    ws = r.sample(pool, 4)
    body = P(ask) + '<div class="bogi"><p>%s</p></div>' % a.html(under=[idx]) + extra
    return mc(body, right_name, ws, steps=steps, core=core, lv=lv, fam=fam, r=r, ref=ref, vertical=False)


def t_circ(r, a, idxs, ask, right_k, steps, lv='중', fam='C', ref=None, core=''):
    """분절 5개에 ㉠~㉤ 을 붙이고, 정답은 right_k 번째(0~4)."""
    labels = {ix: CIRC[n] for n, ix in enumerate(idxs)}
    body = P(ask) + '<div class="bogi"><p>%s</p></div>' % a.html(under=idxs, labels=labels)
    opts = [CIRC[n] for n in range(len(idxs))]
    return mcs(body, [(o, n == right_k) for n, o in enumerate(opts)], steps=steps, core=core, lv=lv, fam=fam, r=r, ref=ref, vertical=False)


def tf_stmts(r, a, idxs, label_fn, ask, mode='bad', lv='상', fam='D', ref=None, names=None, core='', fmt=None):
    """분절 5개에 대한 진술 5개(㉠~㉤ 각 하나) 중 옳지 않은(옳은) 것 하나.
    label_fn(code) → (참인 설명, [거짓 설명들])"""
    labels = {ix: CIRC[n] for n, ix in enumerate(idxs)}
    body = P(ask) + '<div class="bogi"><p>%s</p></div>' % a.html(under=idxs, labels=labels)
    k = r.randrange(len(idxs))
    items, st = [], []
    for n, ix in enumerate(idxs):
        code = a.toks[ix][2]
        tru, fal = label_fn(code)
        truth = (n != k) if mode == 'bad' else (n == k)
        txt = tru if truth else r.choice(fal)
        items.append(('%s은(는) %s' % (CIRC[n], txt), n == k))
        st.append('%s %s' % (CIRC[n], ('옳다. ' if truth else '옳지 않다. ') + '%s은(는) %s' % (a.toks[ix][1], tru)))
    return mcs(body, items, steps=st, core=core, lv=lv, fam=fam, r=r, ref=ref, vertical=True)
