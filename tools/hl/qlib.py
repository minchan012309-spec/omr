# -*- coding: utf-8 -*-
"""㉠~㉤ 표시 대본 문항 도우미: 대본(turns)의 일부에 기호를 붙이고, 기호별 기능 설명을 고르는 문항을 만든다."""
from hllib import *

CIRC = '㉠㉡㉢㉣㉤'


def turns_box(turns, lab, title=None):
    """turns: [(화자 또는 None, 문장, id)], lab: {인덱스: 기호}"""
    out = []
    for k, (sp, s, _) in enumerate(turns):
        t = ('%s<u>%s</u>' % (lab[k], s)) if k in lab else s
        out.append(('<p><b>%s</b>: %s</p>' % (sp, t)) if sp else '<p>%s</p>' % t)
    bt = '<div class="bt">%s</div>' % title if title else ''
    return '<div class="bogi">' + bt + ''.join(out) + '</div>'


def lab_item(r, turns, descs, *, intro, mode, extra=(), ref=None, core='', lv='중', fam='a', title=None, subject='발화', clash=None):
    """descs: {id: 설명}. mode: one(기호 하나의 기능 고르기) / not5(5개 중 적절하지 않은 것) / ok5(5개 중 적절한 것).
    clash: {id: [다른 id …]} — 그 발화에도 맞는 설명(충돌 사전). 'one'의 오답 후보에서 뺀다."""
    clash = clash or {}
    cand = [k for k, t in enumerate(turns) if t[2] in descs]
    ids = []
    for k in cand:
        if turns[k][2] not in ids: ids.append(turns[k][2])
    if mode == 'one':
        if len(cand) < 1: return None
        k = r.choice(cand); i = turns[k][2]
        pool = [descs[x] for x in descs if x != i and x not in clash.get(i, ())] + list(extra)
        pool = list(dict.fromkeys(pool))
        if len(pool) < 4: return None
        ws = r.sample(pool, 4)
        body = P(intro) + turns_box(turns, {k: '㉠'}, title)
        steps = ['㉠은 「%s」이므로 %s' % (turns[k][1], descs[i])] + ['「%s」라는 설명은 ㉠에 해당하지 않는다.' % w.rstrip('.') for w in ws[:2]]
        return mc(body, descs[i], ws, steps=steps, core=core, lv=lv, fam=fam, r=r, ref=ref, vertical=True)
    if len(ids) < 5: return None
    pick_ids = r.sample(ids, 5)
    ks = sorted(next(k for k in cand if turns[k][2] == i) for i in pick_ids)
    lab = {k: CIRC[n] for n, k in enumerate(ks)}
    body_t = turns_box(turns, lab, title)
    unused = [descs[x] for x in descs if x not in pick_ids] + list(extra)
    unused = list(dict.fromkeys(unused))
    if mode == 'not5':
        if not unused: return None
        bad = r.randrange(5)
        opts, steps = [], []
        for n, k in enumerate(ks):
            if n == bad:
                d = r.choice(unused)
                opts.append('%s: %s' % (CIRC[n], d)); steps.append('%s: 이 발화의 실제 기능은 「%s」이므로 제시된 설명은 옳지 않다.' % (CIRC[n], descs[turns[k][2]].rstrip('.')))
            else:
                d = descs[turns[k][2]]
                opts.append('%s: %s' % (CIRC[n], d)); steps.append('%s: 옳은 설명이다.' % CIRC[n])
        right = opts[bad]; ws = [o for j, o in enumerate(opts) if j != bad]
        return _with_body(r, body_t, intro, right, ws, [steps[bad]] + [x for j, x in enumerate(steps) if j != bad][:2], core, lv, fam, ref)
    if mode == 'ok5':
        if len(unused) < 4: return None
        good = r.randrange(5)
        ws_d = r.sample(unused, 4)
        opts = []; wi = 0
        for n, k in enumerate(ks):
            if n == good:
                opts.append('%s: %s' % (CIRC[n], descs[turns[k][2]]))
            else:
                opts.append('%s: %s' % (CIRC[n], ws_d[wi])); wi += 1
        right = opts[good]; ws = [o for j, o in enumerate(opts) if j != good]
        st = ['%s: 「%s」는 이 발화의 기능과 일치하므로 옳다.' % (CIRC[good], descs[turns[ks[good]][2]].rstrip('.'))] + ['%s: 이 발화의 실제 기능은 「%s」이므로 옳지 않다.' % (CIRC[n], descs[turns[k][2]].rstrip('.')) for n, k in enumerate(ks) if n != good][:2]
        return _with_body(r, body_t, intro, right, ws, st, core, lv, fam, ref)
    return None


def _with_body(r, body_t, intro, right, ws, steps, core, lv, fam, ref):
    return mc(P(intro) + body_t, right, ws, steps=steps, core=core, lv=lv, fam=fam, r=r, ref=ref, vertical=True)
