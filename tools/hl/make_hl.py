# -*- coding: utf-8 -*-
"""hl/ 폴더 전체를 만든다.
   python3 tools/hl/make_hl.py [--skip-bank] [--n 0]
  - hl/hlNNN.json, hl/index.json : 문제 은행(유형별 변형 문제)
  - hl/data.json                  : 교재 문항(자료 문항 + 제작 5지선다·최상위 + OX·빈칸·서술형)
  - hl/concept.json               : 개념서(절·요약 노트·OX 풀)
"""
import sys, os, json, re, collections, argparse, importlib, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build
import hllib
from hllib import render, pts_for, sig, plain, CIR, esc, REGISTRY, josa
from outline import TYPES, BYTAG, BYLABEL, SUBS, BUNDLE, SUB_ORDER
import srclib
import fmt

OUT = os.path.abspath(os.path.join(HERE, '..', '..', 'hl'))
PAL = {'p': '#d9622b', 'pd': '#b84d1d', 'pl': '#fdf1ea', 'pl2': '#f6d9c8', 'line': '#eec4ab'}
SUBID = {'Ⅰ-A': '1a', 'Ⅰ-B': '1b', 'Ⅰ-C': '1c', 'Ⅱ-A': '2a', 'Ⅱ-B': '2b', 'Ⅱ-C': '2c', 'Ⅱ-D': '2d', 'Ⅲ-A': '3a', 'Ⅲ-B': '3b', 'Ⅲ-C': '3c', '종합': 'zz'}
LVI = build.LVI


def dump(path, obj):
    if isinstance(obj, list):  # 문항 HTML 마무리: 대화 발화 2열 · 지문 범위 표지 [A]
        obj = [dict(d, q=fmt.finish(d['q'], d.get('code', ''))) if isinstance(d, dict) and d.get('q') else d for d in obj]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))


def optional(name):
    try:
        return importlib.import_module(name)
    except ImportError as e:
        print('  (경고) %s 없음: %s' % (name, e))
        return None


# ------------------------------------------------------------ 문제 은행
def make_bank(n_over=0):
    os.makedirs(OUT, exist_ok=True)
    index, bank_sigs, tot = {}, {}, 0
    lvt = collections.Counter()
    for ty in TYPES:
        tag = ty['tag']
        if tag not in REGISTRY:
            print(tag, '생성기 없음', ty['base']); continue
        n = n_over or ty['n']
        items, errs = build.gen_tag(tag, n)
        bank_sigs[tag] = {sig(i) for i in items}
        ent = build.to_entries(tag, items)
        lv = collections.Counter(e['lv'] for e in ent)
        lvt.update(lv)
        dump(os.path.join(OUT, tag + '.json'), ent)
        index[tag] = {'lv': dict(lv), 'label': ty['label'], 'sub': ty['sub'], 'subname': ty['subname'], 'sec': ty['sec'], 'style': ty['style'], 'n': len(ent)}
        tot += len(ent)
        print('%s %-34s %3d/%d  %s%s' % (tag, ty['base'][:32], len(ent), n, dict(lv), '  <<< 부족' if len(ent) < n else ''))
    order = {s: i for i, s in enumerate(SUB_ORDER)}
    keys = sorted(index, key=lambda t: (order[index[t]['sub']], t))
    dump(os.path.join(OUT, 'index.json'), {k: index[k] for k in keys})
    print('문제 은행 총', tot, dict(lvt))
    return bank_sigs, tot


# ------------------------------------------------------------ 교재 문항 (제작 5지선다 · 최상위)
def book_pool(bank_sigs, per=22):
    pool = collections.defaultdict(list)
    for ty in TYPES:
        tag = ty['tag']
        if tag not in REGISTRY: continue
        items, _ = build.gen_tag(tag, per, seed_extra='|book', exclude=bank_sigs.get(tag, ()))
        for it in items:
            it._tag = tag
            pool[ty['sub']].append(it)
    return pool


def pick_round(items, k, want_lv, used_fam):
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


NB = {}
NS = {'Ⅱ-A': 30, 'Ⅱ-B': 30, 'Ⅲ-A': 20, 'Ⅲ-B': 24, 'Ⅲ-C': 24, 'Ⅱ-D': 24, 'Ⅰ-A': 16, 'Ⅰ-B': 20, 'Ⅰ-C': 16}


def book_items(bank_sigs, n_basic=8, n_std=14, n_top=14):
    pool = book_pool(bank_sigs)
    seq = collections.Counter()
    data = []
    chosen_top, used_fam = [], set()
    tops_by_sub = {s: [i for i in pool[s] if i.lv in ('상', '최')] for s in SUB_ORDER}
    ti = 0
    while len(chosen_top) < n_top and any(tops_by_sub.values()):
        s = SUB_ORDER[ti % len(SUB_ORDER)]; ti += 1
        if tops_by_sub[s]:
            x = tops_by_sub[s].pop(0)
            if (x._tag, x.fam) in used_fam and tops_by_sub[s]: x = tops_by_sub[s].pop(0)
            used_fam.add((x._tag, x.fam)); chosen_top.append(x)
    topset = {id(x) for x in chosen_top}
    tord = {t['tag']: i for i, t in enumerate(TYPES)}
    for s in SUB_ORDER:
        bundle = BUNDLE[s]
        rest = [i for i in pool[s] if id(i) not in topset]
        basic = pick_round(rest, NB.get(s, n_basic), ('하',), used_fam)
        bset = {id(x) for x in basic}
        std = pick_round([i for i in rest if id(i) not in bset], NS.get(s, n_std), ('중', '상'), used_fam)
        sel = sorted(basic + std, key=lambda x: (tord[x._tag], LVI[x.lv]))
        for it in sel:
            seq[s] += 1
            code = 'KP%d-%03d' % (bundle, seq[s])
            ty = BYTAG[it._tag]
            q, e = render(it, it._tag, seq[s], code, pts_for(it.lv, it._r), qid='q-KP%d%03d' % (bundle, seq[s]), sid='s-KP%d%03d' % (bundle, seq[s]), src='제작 문항')
            data.append({'code': code, 'no': seq[s], 'set': 'mc', 'sub': s, 'subname': SUBS[s]['name'], 'type': ty['label'], 'ans': str(it.ans), 'lv': it.lv, 'fam': 'b' + it._tag + it.fam, 'q': q, 'exp': e})
    for i, it in enumerate(chosen_top, 1):
        s = BYTAG[it._tag]['sub']
        code = 'KR-%03d' % i
        ty = BYTAG[it._tag]
        q, e = render(it, it._tag, i, code, 4, qid='q-KR%03d' % i, sid='s-KR%03d' % i, src='제작 문항')
        data.append({'code': code, 'no': i, 'set': 'top', 'sub': s, 'subname': SUBS[s]['name'], 'type': ty['label'], 'ans': str(it.ans), 'lv': '최', 'fam': 'b' + it._tag + it.fam, 'q': q, 'exp': e})
    return data


# ------------------------------------------------------------ 자료(src_*.py) 문항
SOUND = re.compile(r'발음|음운|반모음|경음화|비음화|구개음화|자음군|끝소리|음절|된소리|모음 조화|동화')


def fix_ref(d):
    """수능특강(EL) 문항은 만든 쪽이 쓴 '다시 공부할 절' 번호가 개념서 절 번호와 어긋나 있어, 유형이 가리키는 절로 되돌린다.
    음운 변동·발음 문항은 개념서에 전용 절이 없어 '소리에 관한 것(Ⅲ-A 2)'로 잇는다."""
    if not d['code'].startswith('EL'): return d
    d = dict(d)
    d.pop('ref', None)
    if d['sub'] == 'Ⅲ-A' and d['type'] in ('한글 맞춤법 조항의 적용',) and SOUND.search(plain(d['body']) + ' ' + (d.get('core') or '')):
        d['ref'] = [2]
    return d


def source_items():
    out, seq = [], collections.Counter()
    import glob as _g
    ebs = sorted(os.path.basename(f)[:-3] for f in _g.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src_ebs_*.py')))
    for name in ('src_mock', 'src_var', 'src_nn1', 'src_nn2', 'src_nn3', 'src_school', 'src_extra', 'src_set', *ebs):
        m = optional(name)
        if not m: continue
        for d in m.ITEMS:
            ty = BYLABEL.get(d['type'])
            if not ty:
                print('  (경고) 유형 없음:', d['code'], d['type']); continue
            seq[d['code'][:3]] += 1
            no = d.get('no') or int(re.sub(r'\D', '', d['code'].split('-')[-1]) or 0)
            d = fix_ref(d)
            q, e = srclib.render_src(d, no, d.get('pts', {'하': 2, '중': 3, '상': 4, '최': 4}.get(d['lv'], 3)))
            out.append({'code': d['code'], 'no': no, 'set': d.get('set', 'mc'), 'sub': d['sub'], 'subname': SUBS[d['sub']]['name'], 'type': ty['label'], 'ans': str(d['ans']), 'lv': d['lv'],
                        'fam': 'src' + d['code'], 'q': q, 'exp': e, 'src': d['src'], **({'grp': d['grp']} if d.get('grp') else {})})
    return out


def essay_items():
    m = optional('src_school')
    out = []
    if not m or not hasattr(m, 'ESSAY'): return out
    for i, d in enumerate(m.ESSAY, 1):
        ty = BYLABEL[d['typ']]
        sub = ty['sub']
        code = d['code']
        qid = 'q-' + re.sub(r'[^A-Za-z0-9]', '', code); sid = 's-' + re.sub(r'[^A-Za-z0-9]', '', code)
        q = '<div class="q" id="%s"><div class="qh"><b class="qn">%d</b><span class="qp">[4점]</span></div><div class="qs">%s</div></div>' % (qid, i, d['body'])
        e = ('<div class="sol" id="%s"><div class="sh"><span class="sn">%d</span><span class="sa t">정답 아래 참고</span><span class="sc2">%s</span></div><div class="ss">출처 : %s</div>'
             '<p><span class="lb">정답</span> %s</p><div class="gr"><div class="gh">채점 핵심 (이 답안에 반드시 들어가야 하는 내용)</div>%s</div>'
             '<p><span class="lb">핵심 개념</span> %s</p></div>') % (sid, i, code, esc(d['src']), esc(d['answer']), ''.join('<div class="gi">%s</div>' % esc(r) for r in d['rubric']), d['core'])
        out.append({'code': code, 'no': i, 'set': 'essay', 'sub': sub, 'subname': SUBS[sub]['name'], 'type': ty['label'], 'ans': d['answer'], 'lv': d['lv'], 'fam': 'ess' + code, 'q': josa(q), 'exp': josa(e), 'src': d['src']})
    return out


# ------------------------------------------------------------ OX · 빈칸 (TF 은행에서)
TFSRC = [('kb_gram_a', 'TF_GA', 'Ⅱ-A'), ('kb_tf_b', 'TF_HON', 'Ⅱ-B'), ('kb_tf_b', 'TF_NEGEND', 'Ⅱ-B'), ('kb_tf_b', 'TF_TENSE', 'Ⅱ-B'), ('kb_tf_b', 'TF_VOICE', 'Ⅱ-B'),
         ('kb_word2', 'TF_WORD', 'Ⅱ-C'), ('kb_tf', 'ORTH_CONCEPT', 'Ⅲ-A'), ('kb_speech2', 'TF_SPEECH', 'Ⅰ-A'), ('kb_speech2', 'TF_DISC', 'Ⅰ-B'), ('kb_speech2', 'TF_CONV', 'Ⅰ-C')]
# 절 번호를 문장 속 낱말로 가른다 (위에서부터 맞는 첫 규칙)
SECKEY = {
    'Ⅰ-A': [(r'확신|듯|믿|단언|부사', 4), (r'계획|청중|도입|정리', 2), (r'비언어|반언어|억양|시선|몸짓|말하기 방식|실연|질문', 3)],
    'Ⅰ-B': [(r'사회자|토의', 1), (r'반대 신문|신문|반박', 3), (r'오류|논증|일반화|인신|흑백', 4), (r'입론|논제|토론', 2)],
    'Ⅰ-C': [(r'협상|양보|절충', 2), (r'면담|인터뷰|기사|매체|보도|SNS', 3)],
    'Ⅱ-A': [(r'독립어|감탄사|호격', 6), (r'안은문장|안긴|명사절|관형사절|관형절|부사절|서술절|인용절|동격|관계', 8), (r'이어진|대등|종속|연결 어미', 9), (r'홑문장|겹문장', 7), (r'관형어|부사어|필수적 부사어', 5), (r'서술어|자릿수', 4), (r'목적어|보어', 3), (r'주어', 2)],
    'Ⅱ-B': [(r'높임|께서|-시-|객체|주체|상대|하십시오|해요', 2), (r'시제|-겠-|-더-|-았|-었|과거|현재|미래|선어말', 3), (r'진행|완료|동작상', 4), (r'피동', 5), (r'사동|-게 하다', 6), (r'부정|안 |못 |말다', 7), (r'종결|평서|의문|명령|청유|감탄|간접', 1)],
    'Ⅱ-C': [(r'다의어|동음이의어|중심적|주변적', 1), (r'파생|합성|접사|어근|접두사|접미사', 3)],
    'Ⅲ-A': [(r'두음|렬|률|열|율', 3), (r'된소리|구개음화|ㄷ, ?ㅌ|맏이|해돋이', 2)],
}


def secno(sub, stmt):
    for rx, n in SECKEY.get(sub, []):
        if re.search(rx, stmt): return n
    return 1


def types_of(sub, sec):
    return [t for t in TYPES if t['sub'] == sub and t['sec'] == sec]


def ox_items():
    data, pools = [], {}
    by_sec = collections.defaultdict(list)
    seq = 0
    for modname, var, sub in TFSRC:
        m = importlib.import_module(modname)
        for stmt, truth, expl in getattr(m, var):
            by_sec[(sub, secno(sub, stmt))].append((stmt, truth, expl))
    sec_ox = collections.defaultdict(list)
    trues, falses = collections.defaultdict(list), collections.defaultdict(list)
    for (sub, no), L in sorted(by_sec.items(), key=lambda z: (SUB_ORDER.index(z[0][0]), z[0][1])):
        ts = types_of(sub, no)
        label = ts[0]['label'] if ts else BYTAG[[t['tag'] for t in TYPES if t['sub'] == sub][0]]['label']
        base = ts[0]['base'] if ts else None
        for stmt, truth, expl in L:
            seq += 1
            code = 'KV-%03d' % seq
            exp = ('<p><b>O</b> 옳은 설명이다. %s</p>' % esc(expl)) if truth else ('<p><b>X</b> 옳지 않은 설명이다. %s</p>' % esc(expl))
            data.append({'code': code, 'no': seq, 'set': 'ox', 'sub': sub, 'subname': SUBS[sub]['name'], 'type': label, 'ans': 'O' if truth else 'X', 'lv': '',
                         'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % esc(stmt), 'exp': exp})
            sec_ox[(sub, no)].append(code)
            (trues if truth else falses)[sub].append(stmt)
    # 자료의 OX
    m = optional('src_school')
    if m and hasattr(m, 'OX'):
        for sub, no, stmt, truth, expl in m.OX:
            seq += 1
            code = 'KV-%03d' % seq
            exp = ('<p><b>O</b> 옳은 설명이다. %s</p>' % esc(expl)) if truth else ('<p><b>X</b> 옳지 않은 설명이다. %s</p>' % esc(expl))
            label = (types_of(sub, no) or [BYTAG[[t['tag'] for t in TYPES if t['sub'] == sub][0]]])[0]['label']
            data.append({'code': code, 'no': seq, 'set': 'ox', 'sub': sub, 'subname': SUBS[sub]['name'], 'type': label, 'ans': 'O' if truth else 'X', 'lv': '',
                         'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % esc(stmt), 'exp': exp, 'src': '학교 교재 O/X'})
            sec_ox[(sub, no)].append(code)
            (trues if truth else falses)[sub].append(stmt)
    for sub in SUB_ORDER:
        T, F = trues[sub], falses[sub]
        k = min(len(T), len(F))
        if k: pools['__' + sub] = [[T[i], F[i]] for i in range(k)]
    return data, pools, sec_ox


def blank_items(start=0, per_sub=14):
    """TF 은행의 참인 문장 중 따옴표 낱말이 있는 것을 빈칸 문제로 만든다."""
    data, seq = [], start
    sec_bl = collections.defaultdict(list)
    cnt = collections.Counter()
    for modname, var, sub in TFSRC:
        m = importlib.import_module(modname)
        for stmt, truth, expl in getattr(m, var):
            if not truth or cnt[sub] >= per_sub: continue
            terms = re.findall(r"'([^']{1,14})'", stmt)
            if not 1 <= len(terms) <= 2: continue
            terms = [t for t in terms if not re.search(r'[?!]', t)]
            if not terms: continue
            cnt[sub] += 1
            seq += 1
            k = [0]
            def sb(mm):
                if mm.group(1) not in terms: return mm.group(0)
                i = k[0]; k[0] += 1
                return '<span class="bk">%s</span>' % '㉠㉡㉢㉣'[i]
            s2 = re.sub(r"'([^']{1,14})'", sb, esc(stmt).replace('&#x27;', "'"))
            ans_t = re.sub(r"'([^']{1,14})'", lambda mm: '&lt;&lt;%s&gt;&gt;' % mm.group(1) if mm.group(1) in terms else mm.group(0), esc(stmt).replace('&#x27;', "'"))
            code = 'KL-%03d' % seq
            no = secno(sub, stmt)
            label = (types_of(sub, no) or [BYTAG[[t['tag'] for t in TYPES if t['sub'] == sub][0]]])[0]['label']
            data.append({'code': code, 'no': seq, 'set': 'blank', 'sub': sub, 'subname': SUBS[sub]['name'], 'type': label, 'ans': ', '.join(terms), 'lv': '',
                         'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % s2, 'exp': '<p>%s</p>' % ans_t, 'blanks': terms})
            sec_bl[(sub, no)].append(code)
    m = optional('src_short')
    if m:
        for sub, no, stem, answers, expl in m.BLANKS:
            seq += 1
            code = 'KL-%03d' % seq
            parts = stem.split('___')
            if len(parts) - 1 != len(answers):
                print('  (경고) 빈칸 수 불일치:', stem); continue
            qs = ''.join(esc(parts[i]) + ('<span class="bk">%s</span>' % '㉠㉡㉢㉣㉤'[i] if i < len(answers) else '') for i in range(len(parts)))
            ans_t = ''.join(esc(parts[i]) + ('&lt;&lt;%s&gt;&gt;' % answers[i] if i < len(answers) else '') for i in range(len(parts)))
            label = (types_of(sub, no) or [BYTAG[[t['tag'] for t in TYPES if t['sub'] == sub][0]]])[0]['label']
            data.append({'code': code, 'no': seq, 'set': 'blank', 'sub': sub, 'subname': SUBS[sub]['name'], 'type': label, 'ans': ', '.join(answers), 'lv': '',
                         'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % qs, 'exp': '<p>%s</p><p>%s</p>' % (ans_t, esc(expl)), 'blanks': answers, 'src': '국어의 원리 확인 문제'})
            sec_bl[(sub, no)].append(code)
    return data, sec_bl


def derived_tf(start_ox, start_bl, per_sub=240, per_sub_bl=70):
    """문제 은행의 '옳은/옳지 않은 것' 5지선다에서 선지를 떼어 OX·빈칸 문항을 만든다 (선지마다 참·거짓이 정해져 있다)."""
    import glob, html as H
    sec_of = {t['label']: t['sec'] for t in TYPES}
    seen, pool = set(), collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(OUT, 'hl[0-9][0-9][0-9].json'))):
        j = json.load(open(f, encoding='utf-8'))
        for x in (j if isinstance(j, list) else j.get('items', [])):
            q = x['q']
            if 'bogi' in q or '<table' in q or 'class="chs' not in q: continue
            m = re.search(r'<div class="qs">(.*?)<div class="chs', q, re.S)
            stem = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''
            if not re.fullmatch(r'(다음 중 )?(.{0,12})?옳(지 않)?은 것은\?', stem): continue
            ops = [H.unescape(o) for o in re.findall(r'<span>(.*?)</span></div>', q.split('class="chs')[1])]
            if len(ops) != 5 or any(re.search(r'[㉠㉡㉢㉣㉤ⓐⓑ]|\(가\)|\(나\)|보기', o) or len(o) < 10 for o in ops): continue
            neg = '옳지 않' in stem; ans = int(x['ans']) - 1
            lines = [H.unescape(re.sub(r'<[^>]+>', '', l)) for l in re.findall(r'<p class="st">(.*?)</p>', x['exp'])]
            for i, o in enumerate(ops):
                if o in seen: continue
                seen.add(o)
                truth = (i != ans) if neg else (i == ans)
                note = ''
                for l in lines:
                    k = l.find(o)
                    if k >= 0: note = l[k + len(o):].strip(); break
                pool[x['sub']].append((sec_of.get(x['type'], 1), x['type'], o, truth, note))
    ox, bl = [], []
    rnd = random.Random(7)
    for sub in SUB_ORDER:
        L = pool.get(sub, [])
        rnd.shuffle(L)
        T = [z for z in L if z[3]]; F = [z for z in L if not z[3]]
        pick = []
        for a, b in zip(T, F):
            pick += [a, b]
            if len(pick) >= per_sub: break
        rnd.shuffle(pick)
        for sec, label, stmt, truth, note in pick:
            start_ox += 1
            exp = ('<p><b>O</b> 옳은 설명이다. %s</p>' if truth else '<p><b>X</b> 옳지 않은 설명이다. %s</p>') % esc(note)
            ox.append({'code': 'KV-%04d' % start_ox, 'no': start_ox, 'set': 'ox', 'sub': sub, 'subname': SUBS[sub]['name'], 'type': label, 'ans': 'O' if truth else 'X', 'lv': '',
                       'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % esc(stmt), 'exp': exp})
        nb = 0
        for sec, label, stmt, truth, note in L:
            if nb >= per_sub_bl: break
            if not truth: continue
            terms = re.findall(r'"([^"]{1,12})"', stmt)
            if len(terms) != 1 or re.search(r'[?!]', terms[0]): continue
            es = esc(stmt); key = esc(terms[0])
            tgt = [k for k in ('&quot;%s&quot;' % key, '"%s"' % key) if k in es]
            if not tgt: continue
            nb += 1; start_bl += 1
            s2 = es.replace(tgt[0], '<span class="bk">㉠</span>')
            ans_t = es.replace(tgt[0], '&lt;&lt;%s&gt;&gt;' % key)
            bl.append({'code': 'KL-%04d' % start_bl, 'no': start_bl, 'set': 'blank', 'sub': sub, 'subname': SUBS[sub]['name'], 'type': label, 'ans': terms[0], 'lv': '',
                       'q': '<div class="q"><div class="qs"><p>%s</p></div></div>' % s2, 'exp': '<p>%s</p>' % ans_t, 'blanks': terms})
    return ox, bl


# ------------------------------------------------------------ 개념서
def make_concept(pools, sec_ox, sec_bl):
    SECS = collections.defaultdict(list)
    for m, names in (('concept_sp', ('SECS_A', 'SECS_B', 'SECS_C')), ('concept_ga1', None), ('concept_ga2', None), ('concept_gb', None), ('concept_gc', None), ('concept_gd', None),
                     ('concept_oa', ('SECS_A', 'SECS_B')), ('concept_oc', None), ('concept_zz', None)):
        mod = optional(m)
        if not mod: continue
        if m == 'concept_sp':
            SECS['Ⅰ-A'] += mod.SECS_A; SECS['Ⅰ-B'] += mod.SECS_B; SECS['Ⅰ-C'] += mod.SECS_C
        elif m in ('concept_ga1', 'concept_ga2'):
            SECS['Ⅱ-A'] += mod.SECS
        elif m == 'concept_gb': SECS['Ⅱ-B'] += mod.SECS
        elif m == 'concept_gc': SECS['Ⅱ-C'] += mod.SECS
        elif m == 'concept_gd': SECS['Ⅱ-D'] += mod.SECS
        elif m == 'concept_oa':
            SECS['Ⅲ-A'] += mod.SECS_A; SECS['Ⅲ-B'] += mod.SECS_B
        elif m == 'concept_oc': SECS['Ⅲ-C'] += mod.SECS
        elif m == 'concept_zz': SECS['종합'] += mod.SECS
    summary = optional('concept_zz').SUMMARY
    subs = {k: {'name': v['name'], 'goal': v['goal']} for k, v in SUBS.items()}
    secs = []
    label_ok = {t['base'] for t in TYPES}
    for s in SUB_ORDER:
        exp_titles = SUBS[s]['secs']
        got = SECS.get(s, [])
        if len(got) != len(exp_titles):
            print('  (경고) 절 수 불일치', s, len(got), '!=', len(exp_titles))
        for no, sec in enumerate(got, 1):
            if no <= len(exp_titles) and sec['title'] != exp_titles[no - 1]:
                print('  (경고) 절 제목 불일치', s, no, sec['title'], '!=', exp_titles[no - 1])
            types = []
            for t in sec.get('types') or []:
                if t not in label_ok: print('  (경고) 유형 이름 없음:', s, no, t); continue
                types.append(BYLABEL[t]['label'])
            ox = list(sec_ox.get((s, no), []))
            bl = list(sec_bl.get((s, no), []))
            secs.append({'id': 'c-%s%d' % (SUBID[s], no), 'sub': s, 'no': str(no), 'title': sec['title'], 'html': sec['html'], 'types': types, 'ox': ox[:5], 'blank': bl[:5]})
    # 풀: 유형별 풀은 소단원 풀을 그대로 쓴다
    conc = {'pal': PAL, 'subs': subs, 'secs': secs, 'summary': summary, 'pools': pools, 'noDefaultBooks': True}
    dump(os.path.join(OUT, 'concept.json'), conc)
    print('개념서: 절 %d개, 요약 %d개, 풀 %d개, 글자 %dK' % (len(secs), len(summary), len(pools), sum(len(x['html']) for x in secs) // 1000))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=0)
    ap.add_argument('--skip-bank', action='store_true')
    a = ap.parse_args()
    build.load_types()
    os.makedirs(OUT, exist_ok=True)
    if a.skip_bank:
        bank_sigs = {}
        for ty in TYPES:
            if ty['tag'] in REGISTRY:
                items, _ = build.gen_tag(ty['tag'], a.n or ty['n'])
                bank_sigs[ty['tag']] = {sig(i) for i in items}
    else:
        bank_sigs, _ = make_bank(a.n)
    src = source_items()
    ox, pools, sec_ox = ox_items()
    bl, sec_bl = blank_items()
    dox, dbl = derived_tf(5000, 5000)
    ox += dox; bl += dbl
    data = src + book_items(bank_sigs) + ox + bl + essay_items()
    ess = optional('src_essay')
    if ess: data += ess.items(render_src=srclib.render_src)
    dump(os.path.join(OUT, 'data.json'), data)
    print('교재 문항', dict(collections.Counter(d['set'] for d in data)))
    make_concept(pools, sec_ox, sec_bl)
    rp = fmt.report()
    print('범위 표지 [A]: 끝 표지 %d · 발화 묶음 %d · 문단 %d · 문단 끝 표지(확인 필요) %d %s' % (len(rp['explicit']), len(rp['utter']), len(rp['paragraph']), len(rp['end']), ' '.join(rp['end'] + rp['paragraph'])))


if __name__ == '__main__':
    main()
