# -*- coding: utf-8 -*-
"""ph/ 폴더 전체를 만든다.
   python3 tools/ph/make_ph.py [--n 90] [--skip-bank]
  - ph/phNNN.json, ph/index.json : 문제 은행(유형별)
  - ph/data.json                  : 교재 문항(5지선다·최상위·OX·빈칸·서술형)
  - ph/concept.json               : 개념서(절·요약 노트·OX 풀)
"""
import sys, os, json, random, collections, re, argparse, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build
import phlib
from phlib import render, pts_for, sig, plain, CIR, esc, REGISTRY
from outline import TYPES, TYPES_ORD, BYTAG, SUBS, SUB_ORDER, BUNDLE, DEFAULT_SCOPE

OUT = os.path.abspath(os.path.join(HERE, '..', '..', 'ph'))
PAL = {'p': '#6d4cc4', 'pd': '#5a3bad', 'pl': '#f3effc', 'pl2': '#e4dbf8', 'line': '#cdbfef'}
SUBID = {'Ⅰ-A': '1a', 'Ⅰ-B': '1b', 'Ⅰ-C': '1c', 'Ⅰ-D': '1d', 'Ⅰ-E': '1e', 'Ⅰ-F': '1f', 'Ⅰ-G': '1g', 'Ⅰ-H': '1h',
         'Ⅱ-A': '2a', 'Ⅱ-B': '2b', 'Ⅲ-A': '3a', 'Ⅲ-B': '3b', 'Ⅲ-C': '3c', '종합': 'zz'}
LVI = build.LVI


def dump(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))


def optional(name):
    try:
        return importlib.import_module(name)
    except ImportError as e:
        print('  (경고) %s 없음: %s' % (name, e))
        return None


# --------------------------------------------------------------- 문제 은행
def make_bank(n):
    os.makedirs(OUT, exist_ok=True)
    index, bank_sigs = {}, {}
    tot = 0
    for ty in TYPES_ORD:
        tag = ty['tag']
        if tag not in REGISTRY:
            print(tag, '생성기 없음'); continue
        items, errs = build.gen_tag(tag, n)
        bank_sigs[tag] = {sig(i) for i in items}
        ent = build.to_entries(tag, items)
        lv = collections.Counter(e['lv'] for e in ent)
        dump(os.path.join(OUT, tag + '.json'), ent)
        index[tag] = {'lv': dict(lv), 'label': ty['label'], 'sub': ty['sub'], 'subname': ty['subname'], 'n': len(ent)}
        tot += len(ent)
        print('%s %-30s %3d  %s' % (tag, ty['label'][:28], len(ent), dict(errs.most_common(2)) if errs else ''))
    dump(os.path.join(OUT, 'index.json'), index)
    print('문제 은행 총', tot)
    return bank_sigs, tot


# --------------------------------------------------------------- 교재 문항
def book_pool(bank_sigs, per=22):
    """유형마다 은행과 겹치지 않는 별도 문항(교재용)을 만든다."""
    pool = collections.defaultdict(list)
    for ty in TYPES_ORD:
        tag = ty['tag']
        if tag not in REGISTRY: continue
        items, _ = build.gen_tag(tag, per, seed_extra='|book', exclude=bank_sigs.get(tag, ()))
        for it in items:
            it._tag = tag
            pool[ty['sub']].append(it)
    return pool


def pick_round(items, k, want_lv, used_fam):
    """유형이 골고루 나오도록 라운드 로빈으로 k개."""
    by = collections.OrderedDict()
    for it in items:
        if it.lv in want_lv: by.setdefault(it._tag, []).append(it)
    out = []
    while len(out) < k and any(by.values()):
        for tag in list(by):
            L = by[tag]
            if not L: continue
            j = next((i for i, x in enumerate(L) if (tag, x.fam) not in used_fam), 0)
            x = L.pop(j)
            used_fam.add((tag, x.fam))
            out.append(x)
            if len(out) >= k: break
    return out


# 기본 교재 범위(열역학 제1법칙~)는 문항을 더 두껍게, 앞 단원은 기본 분량
NB = {'Ⅱ-A': 12}
NS = {'Ⅱ-A': 44, 'Ⅱ-B': 28, 'Ⅲ-A': 20, 'Ⅲ-B': 20, 'Ⅲ-C': 20}


def book_items(bank_sigs, n_basic=8, n_std=12, n_top=21):
    pool = book_pool(bank_sigs)
    seq = collections.Counter()
    data = []
    chosen_top = []
    used_fam = set()
    # 최상위(하나라도 '상'인 것) — 소단원을 돌아가며
    tops_by_sub = {s: [i for i in pool[s] if i.lv == '상'] for s in SUB_ORDER}
    ti = 0
    while len(chosen_top) < n_top and any(tops_by_sub.values()):
        s = SUB_ORDER[ti % len(SUB_ORDER)]; ti += 1
        if tops_by_sub[s]:
            x = tops_by_sub[s].pop(0)
            if (x._tag, x.fam) in used_fam and len(tops_by_sub[s]) > 0: x = tops_by_sub[s].pop(0)
            used_fam.add((x._tag, x.fam)); x._top = True
            chosen_top.append(x)
    topset = {id(x) for x in chosen_top}
    tord = {t['tag']: i for i, t in enumerate(TYPES_ORD)}
    for s in SUB_ORDER:
        bundle = BUNDLE[s]
        rest = [i for i in pool[s] if id(i) not in topset]
        basic = pick_round(rest, NB.get(s, n_basic), ('하',), used_fam)
        bset = {id(x) for x in basic}
        std = pick_round([i for i in rest if id(i) not in bset], NS.get(s, n_std), ('중', '상'), used_fam)
        sel = sorted(basic + std, key=lambda x: (tord[x._tag], LVI[x.lv]))   # 유형 순서 → 난이도
        for it in sel:
            seq[s] += 1
            code = 'P%d-%03d' % (bundle, seq[s])
            ty = BYTAG[it._tag]
            q, e = render(it, it._tag, seq[s], code, s, pts_for(it.lv, it._r), qid='q-P%d%03d' % (bundle, seq[s]), sid='s-P%d%03d' % (bundle, seq[s]), src='제작 문항')
            data.append({'code': code, 'no': seq[s], 'set': 'mc', 'sub': s, 'subname': SUBS[s]['name'], 'type': ty['label'], 'ans': str(it.ans), 'lv': it.lv, 'fam': 'b' + it._tag + it.fam, 'q': q, 'exp': e})
    for i, it in enumerate(chosen_top, 1):
        s = BYTAG[it._tag]['sub']
        code = 'R-%03d' % i
        ty = BYTAG[it._tag]
        q, e = render(it, it._tag, i, code, s, 4, qid='q-R%03d' % i, sid='s-R%03d' % i, src='제작 문항')
        data.append({'code': code, 'no': i, 'set': 'top', 'sub': s, 'subname': SUBS[s]['name'], 'type': ty['label'], 'ans': str(it.ans), 'lv': '최', 'fam': 'b' + it._tag + it.fam, 'q': q, 'exp': e})
    return data


def pairs_all():
    P = {}
    for m, name in (('concept_a', 'PAIRS_A'), ('concept_b', 'PAIRS_B')):
        mod = optional(m)
        if mod and hasattr(mod, name):
            for k, v in getattr(mod, name).items(): P[k] = v
    return P


def ox_blank_items(P, n_ox=10, n_bl=10):
    data, pools = [], {}
    ox_i = bl_i = 0
    sec_ox = collections.defaultdict(list)
    sec_bl = collections.defaultdict(list)
    for s in SUB_ORDER:
        pairs = P.get(s, [])
        if not pairs: continue
        types = [t['label'] for t in TYPES_ORD if t['sub'] == s]
        bytype = collections.OrderedDict((t, []) for t in types)
        for k, (tr, fa, ty) in enumerate(pairs):
            bytype.setdefault(ty, []).append(k)
        # 풀(pairs): 유형별, 소단원 공통
        plain_pairs = [[re.sub(r'\[\[(.+?)\]\]', r'\1', tr), fa] for tr, fa, ty in pairs]
        pools['__' + s] = plain_pairs
        for t, ks in bytype.items():
            if ks: pools[t] = [plain_pairs[k] for k in ks]
        # OX: 유형을 돌아가며 n_ox 개, 참/거짓 번갈아
        order, used = [], set()
        lists = [list(v) for v in bytype.values() if v]
        while len(order) < min(n_ox, len(pairs)) and any(lists):
            for L in lists:
                if L and len(order) < n_ox:
                    order.append(L.pop(0))
        for j, k in enumerate(order):
            tr, fa, ty = pairs[k]
            true_txt = re.sub(r'\[\[(.+?)\]\]', r'\1', tr)
            is_true = (j % 2 == 0)
            ox_i += 1
            code = 'V-%03d' % ox_i
            stmt = true_txt if is_true else fa
            exp = '<p><b>O</b> 옳은 설명이다. %s</p>' % true_txt if is_true else '<p><b>X</b> 옳은 설명 → %s</p>' % true_txt
            data.append({'code': code, 'no': ox_i, 'set': 'ox', 'sub': s, 'subname': SUBS[s]['name'], 'type': ty, 'ans': 'O' if is_true else 'X', 'lv': '',
                         'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % stmt, 'exp': exp})
            sec_ox[(s, ty)].append(code)
            used.add(k)
        # 빈칸: [[ ]] 표시가 있는 쌍(앞쪽은 OX 와 겹치지 않게)
        cand = [k for k, (tr, fa, ty) in enumerate(pairs) if '[[' in tr]
        cand = [k for k in cand if k not in used] + [k for k in cand if k in used]
        order2, lists = [], [[k for k in cand if pairs[k][2] == t] for t in bytype]
        while len(order2) < min(n_bl, len(cand)) and any(lists):
            for L in lists:
                if L and len(order2) < n_bl: order2.append(L.pop(0))
        for k in order2:
            tr, fa, ty = pairs[k]
            terms = re.findall(r'\[\[(.+?)\]\]', tr)
            cnt = [0]
            def sub_bk(m):
                i = cnt[0]; cnt[0] += 1
                return '<span class="bk">%s</span>' % '㉠㉡㉢㉣'[i]
            stmt = re.sub(r'\[\[(.+?)\]\]', sub_bk, tr)
            ans_t = re.sub(r'\[\[(.+?)\]\]', r'&lt;&lt;\1&gt;&gt;', tr)
            bl_i += 1
            code = 'L-%03d' % bl_i
            data.append({'code': code, 'no': bl_i, 'set': 'blank', 'sub': s, 'subname': SUBS[s]['name'], 'type': ty, 'ans': ', '.join(terms), 'lv': '',
                         'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % stmt, 'exp': '<p>%s</p>' % ans_t, 'blanks': terms})
            sec_bl[(s, ty)].append(code)
    return data, pools, sec_ox, sec_bl


def essay_items():
    mod = optional('essay')
    if not mod: return []
    out = []
    for i, d in enumerate(mod.ESSAYS, 1):
        s = d['sub']
        code = 'S-%03d' % i
        q = '<div class="q" id="q-S%03d"><div class="qh"><b class="qn">%d</b><span class="qp">[%d점]</span></div><div class="qs">%s</div></div>' % (i, i, d.get('pts', 4), d['body'])
        gr = '<div class="gr"><div class="gh">채점 핵심 (이 답안에 반드시 들어가야 하는 내용)</div>' + ''.join('<div class="gi">%s</div>' % c for c in d['criteria']) + '</div>'
        e = ('<div class="sol" id="s-S%03d"><div class="sh"><span class="sn">%d</span><span class="sa t">정답 아래 참고</span><span class="sc2">%s</span></div>' % (i, i, code) +
             '<div class="ss">출처 : 제작 문항</div><p><span class="lb">정답</span> %s</p><p><span class="lb">풀이</span></p>' % d['ans'] +
             ''.join('<p class="st">%s</p>' % x for x in d['steps']) + gr +
             '<p><span class="lb">핵심 개념</span> %s</p><p><span class="lb">출제 포인트</span> %s</p></div>' % (d['core'], d['point']))
        out.append({'code': code, 'no': i, 'set': 'essay', 'sub': s, 'subname': SUBS[s]['name'], 'type': d['type'], 'ans': d['ans'], 'lv': '상', 'fam': 'e%02d' % i, 'q': q, 'exp': e})
    return out


# --------------------------------------------------------------- 개념서
def make_concept(P, pools, sec_ox, sec_bl):
    SECS = {}
    SUMMARY = []
    for m, name in (('concept_a', 'SECS_A'), ('concept_b', 'SECS_B')):
        mod = optional(m)
        if mod and hasattr(mod, name): SECS.update(getattr(mod, name))
    mb = optional('concept_b')
    if mb and hasattr(mb, 'SUMMARY'): SUMMARY = mb.SUMMARY
    subs = {k: {'name': v['name'], 'goal': v['goal']} for k, v in SUBS.items()}
    secs = []
    for s in SUB_ORDER:
        for no, sec in enumerate(SECS.get(s, []), 1):
            exp_title = SUBS[s]['secs'][no - 1]
            if sec['title'] != exp_title:
                print('  (경고) 절 제목 불일치', s, no, sec['title'], '!=', exp_title)
            types = sec.get('types') or []
            ox, bl = [], []
            for t in types:
                ox += sec_ox.get((s, t), []); bl += sec_bl.get((s, t), [])
            secs.append({'id': 'c-%s%d' % (SUBID[s], no), 'sub': s, 'no': str(no), 'title': sec['title'], 'html': sec['html'], 'types': types, 'ox': ox[:4], 'blank': bl[:5]})
    conc = {'pal': PAL, 'scope': DEFAULT_SCOPE, 'subs': subs, 'secs': secs, 'summary': SUMMARY, 'pools': pools}
    dump(os.path.join(OUT, 'concept.json'), conc)
    print('개념서: 절 %d개, 요약 %d개, 풀 %d개' % (len(secs), len(SUMMARY), len(pools)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=90)
    ap.add_argument('--skip-bank', action='store_true')
    a = ap.parse_args()
    build.load_types()
    os.makedirs(OUT, exist_ok=True)
    if a.skip_bank:
        # 은행 서명은 재생성으로 얻는다(결정적)
        bank_sigs = {}
        for ty in TYPES_ORD:
            if ty['tag'] in REGISTRY:
                items, _ = build.gen_tag(ty['tag'], a.n)
                bank_sigs[ty['tag']] = {sig(i) for i in items}
    else:
        bank_sigs, _ = make_bank(a.n)
    P = pairs_all()
    ox, pools, sec_ox, sec_bl = ox_blank_items(P)
    data = book_items(bank_sigs) + ox + essay_items()
    dump(os.path.join(OUT, 'data.json'), data)
    print('교재 문항', collections.Counter(d['set'] for d in data))
    make_concept(P, pools, sec_ox, sec_bl)


if __name__ == '__main__':
    main()
