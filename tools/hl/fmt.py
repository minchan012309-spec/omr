# -*- coding: utf-8 -*-
"""생성한 문항 HTML 마무리(make_hl.py 가 저장 직전에 모든 q·exp 에 적용).

1) 대화·토론 발화  <p>[<b>[A]</b>] <b>화자</b> : 내용</p>
   →  <div class="dl [mod|pro|con]" style="--spw:4.5em"><b class="sp">화자</b><span class="tx">[A] 내용</span></div>
   화자 열 너비(--spw)는 이어지는 발화 묶음에서 가장 긴 이름에 맞춘다.
2) 지문 안 범위 표지  [A] … ([A 끝])
   →  <span class="rng" data-k="A"><span class="rk">A</span> … <span class="re"></span></span>
   범위는 발화(문단) 단위로 정한다.
     - 발화·문단 맨 앞의 [A] : 그 발화 끝까지. 바로 다음 발화도 [A]로 시작하면 이어서 한 범위(발화 묶음).
     - [A 끝] 이 있으면 그 자리까지(사이의 발화는 통째로 범위).
     - 문단 맨 끝의 [A] : 그 문단 전체(시험지의 오른쪽 괄호 표시를 옮긴 것으로 본다) → 확신이 낮아 보고 목록에 남긴다.
   빈칸 자리(〈보기〉의 [A]에 들어갈 …)나 문장 가운데의 [A]는 건드리지 않는다.
"""
import re

SPK = re.compile(r'<p>((?:<b>\[[A-E]\]</b>\s*)?)<b>([^<\[\]]{1,14}?)</b>\s*:\s*(.*?)</p>', re.S)
REPORT = {'end': [], 'paragraph': [], 'utter': [], 'explicit': []}


def spk_cls(n):
    if '사회' in n or '진행' in n: return ' mod'
    if '찬성' in n: return ' pro'
    if '반대' in n: return ' con'
    return ''


def spk_w(n):
    w = sum(.55 if (c.isdigit() or c in ' ,.') else 1.0 for c in n) + .9  # 이름 + 콜론
    return max(3.2, min(7.5, round(w * 2) / 2))


def dialogue(h):
    """<p><b>화자</b> : …</p> 를 2열 발화 줄로 바꾸고, 이어지는 발화 묶음마다 화자 열 너비를 맞춘다."""
    if '</b> :' not in h and '</b>:' not in h: return h
    out, last, run = [], 0, []
    ms = list(SPK.finditer(h))
    if not ms: return h
    # 이어진(사이에 다른 글이 없는) 발화끼리 묶어 너비를 정한다
    groups, cur = [], [ms[0]]
    for a, b in zip(ms, ms[1:]):
        gap = h[a.end():b.start()]
        if re.fullmatch(r'\s*(?:</div>\s*<div class="bogi dl">\s*)?', gap): cur.append(b)
        else: groups.append(cur); cur = [b]
    groups.append(cur)
    for g in groups:
        w = max(spk_w(m.group(2)) for m in g)
        for m in g:
            out.append(h[last:m.start()])
            mk, name, tx = m.group(1), m.group(2).strip(), m.group(3)
            out.append('<div class="dl%s" style="--spw:%gem"><b class="sp">%s</b><span class="tx">%s%s</span></div>' % (spk_cls(name), w, name, mk, tx))
            last = m.end()
    out.append(h[last:])
    return ''.join(out)


def _psg_spans(h):
    """<div class="psg …"> … </div> 영역(중첩 div 고려)의 [시작, 끝) 목록"""
    res, i = [], 0
    while True:
        s = h.find('<div class="psg', i)
        if s < 0: return res
        depth, j = 0, s
        for m in re.finditer(r'<div\b|</div>', h[s:]):
            depth += 1 if m.group(0) != '</div>' else -1
            if depth == 0:
                j = s + m.end(); break
        res.append((s, j)); i = j


BLK = re.compile(r'(<p(?: class="[^"]*")?>)(.*?)(</p>)|(<div class="dl[^"]*"[^>]*><b class="sp">.*?</b><span class="tx">)(.*?)(</span></div>)', re.S)
MK = r'(?:<b>)?\[%s\](?:</b>)?'
TXT = lambda s: re.sub(r'<[^>]+>', '', s)


def _wrap(body, k, first, last, start=None, end=None):
    """body 안 [start, end) 를 범위 span 으로 감싼다(start/end 는 문자 위치, None 이면 처음/끝)."""
    a = 0 if start is None else start
    b = len(body) if end is None else end
    inner = body[a:b].strip()
    sp = '<span class="rng" data-k="%s">%s%s%s</span>' % (k, '<span class="rk">%s</span>' % k if first else '', inner, '<span class="re"></span>' if last else '')
    return body[:a] + ('' if a == 0 or body[:a].endswith(' ') else ' ') + sp + body[b:]


def ranges(h, code=''):
    if '[' not in h or 'class="psg' not in h: return h
    for s, e in reversed(_psg_spans(h)):
        h = h[:s] + _ranges_in(h[s:e], code) + h[e:]
    return h


def _ranges_in(ps, code):
    blks = list(BLK.finditer(ps))
    if not blks: return ps
    info = []
    for m in blks:
        o, body, c = (m.group(1), m.group(2), m.group(3)) if m.group(1) else (m.group(4), m.group(5), m.group(6))
        info.append([m, o, body, c])
    keys = sorted(set(re.findall(r'\[([A-E])\]', ps)))
    plan = {}  # 블록 번호 -> [(k, first, last, start, end)]
    for k in keys:
        mk = re.compile(MK % k)
        endmk = re.compile(r'(?:<b>)?\[%s 끝\](?:</b>)?' % k)
        has_end = bool(endmk.search(ps))
        i = 0
        while i < len(info):
            body = info[i][2]
            m = mk.search(body)
            if m and 'class="hd"' in info[i][1]:  # 지시문 줄에는 범위를 두지 않는다
                i += 1; continue
            if not m: i += 1; continue
            pre, post = TXT(body[:m.start()]).strip(), TXT(body[m.end():]).strip()
            if pre == '' and len(post) > 8 and not re.match(r'^(?:에|은|는|을|를|의|와|과|이|가|로|으로)\b', post):
                # 발화·문단 맨 앞 : 이어지는 같은 표지 발화를 묶고, [K 끝] 이 있으면 거기까지
                j, segs = i, []
                while True:
                    bj = info[j][2]
                    mj = mk.search(bj) if j > i else m
                    st = mj.end() if (mj and TXT(bj[:mj.start()]).strip() == '') else None
                    em = endmk.search(bj)
                    if em:
                        segs.append((j, st, em.start(), em)); break
                    segs.append((j, st, None, None))
                    nx = j + 1
                    if nx >= len(info): break
                    nb = info[nx][2]
                    nm = mk.search(nb)
                    if (nm and TXT(nb[:nm.start()]).strip() == '') or (has_end and not endmk.search(ps[:info[j][0].end()])):
                        j = nx; continue
                    break
                kind = 'explicit' if any(sg[3] for sg in segs) else ('utter' if 'class="dl' in info[i][1] else 'paragraph')
                REPORT[kind].append(code)
                for n, (j, st, en, em) in enumerate(segs):
                    plan.setdefault(j, []).append((k, n == 0, n == len(segs) - 1, st, en, em))
                i = segs[-1][0] + 1
            elif post == '' and len(pre) > 30:
                REPORT['end'].append(code)
                plan.setdefault(i, []).append((k, True, True, 'pre', m.start(), None))
                i += 1
            else:
                i += 1
    if not plan: return ps
    out, last = [], 0
    for idx, (m, o, body, c) in enumerate(info):
        if idx not in plan: continue
        for (k, first, lst, st, en, em) in plan[idx]:
            mk = re.search(MK % k, body)
            if st == 'pre':  # 문단 끝 표지: 표지를 지우고 문단(발화) 내용 전체를 범위로
                body = _wrap((body[:mk.start()] + body[mk.end():]).rstrip(), k, True, True)
                continue
            if mk and TXT(body[:mk.start()]).strip() == '':
                body = (body[:mk.start()] + body[mk.end():]).lstrip()
            emk = re.search(r'(?:<b>)?\[%s 끝\](?:</b>)?' % k, body)
            if emk: body = _wrap(body[:emk.start()].rstrip(), k, first, lst) + body[emk.end():]
            else: body = _wrap(body, k, first, lst)
        out.append(ps[last:m.start()])
        out.append(o + body + c)
        last = m.end()
    out.append(ps[last:])
    return ''.join(out)


def finish(h, code=''):
    return ranges(dialogue(h), code)


def report():
    def u(a):
        s, o = set(), []
        for x in a:
            if x not in s: s.add(x); o.append(x)
        return o
    return {k: u(v) for k, v in REPORT.items()}
