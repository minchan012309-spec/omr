# -*- coding: utf-8 -*-
"""화법과 언어(hl) 문제 생성 라이브러리.

생성기 파일(types_*.py)은 이 모듈의 도구만으로 문항을 만든다.

    from hllib import *

    @T('hl001')                       # outline.py 의 유형 번호(tag)
    def gen(r, k):                    # r: random.Random(고정 시드), k: 시도 번호(0,1,2…)
        ...
        return mc(body, right='…', wrongs=[…4개 이상…], steps=['…'], core='…', lv='하', fam='a', r=r)

반환값이 None 이면 그 시도는 건너뛴다. 러너(build.py)가 유형마다 n개가 모일 때까지 gen 을 반복 호출하고,
같은 문제(본문+선택지가 같은 것)는 자동으로 걸러낸다.
"""
import random, re, html as _html
from outline import SUBS, BYTAG, TYPES

CIR = '①②③④⑤'
REGISTRY = {}


def T(tag):
    def deco(f):
        assert tag in BYTAG, tag
        REGISTRY[tag] = f
        return f
    return deco


def esc(s):
    return _html.escape(str(s), quote=False)

def plain(h):
    h = _html.unescape(h)
    h = re.sub(r'</?(u|b|i|em|strong|mark|span|sub|sup)(\s[^>]*)?>', '', h)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)).strip()

def P(*t):
    return '<p>' + ''.join(t) + '</p>'

def U(s):
    """밑줄 친 부분."""
    return '<u>%s</u>' % s

def B(s):
    return '<b>%s</b>' % s

def HL(s):
    return '<span class="hl">%s</span>' % s


# ------------------------------------------------------------------ 조사 교정
_JO = {'은(는)': ('은', '는'), '이(가)': ('이', '가'), '을(를)': ('을', '를'), '와(과)': ('과', '와'), '으로(로)': ('으로', '로'), '이라(라)': ('이라', '라'), '(으)로': ('으로', '로'), '과(와)': ('과', '와'), '(이)란': ('이란', '란'), '(이)라고': ('이라고', '라고')}

_DIGIT_JONG = {'0': 21, '1': 8, '2': 0, '3': 16, '4': 0, '5': 0, '6': 1, '7': 8, '8': 8, '9': 0}   # 영·일·이·삼·사·오·육·칠·팔·구 의 받침


def _batchim(c):
    if '가' <= c <= '힣':
        return (ord(c) - 0xAC00) % 28
    if '㉠' <= c <= '㉭':          # ㉠(기역) ㉡(니은) … 자음 이름은 모두 받침으로 끝난다(㉣ 리을은 'ㄹ' 받침)
        return 8 if c == '㉣' else 1
    if c in _DIGIT_JONG:
        return _DIGIT_JONG[c]
    if '①' <= c <= '⑨':           # 원문자 숫자는 '일 이 삼 …'으로 읽는다
        return _DIGIT_JONG[str(ord(c) - 0x245F)]
    if c == '⑩':                   # 십
        return 17
    if '㉮' <= c <= '㉻' or 'ⓐ' <= c <= 'ⓩ':   # ㉮(가)…㉻(하) · ⓐ(에이)… 는 모음으로 끝난다(ⓛ 엘 · ⓜ 엠 · ⓝ 엔 · ⓡ 알 은 받침)
        return {'ⓛ': 8, 'ⓜ': 16, 'ⓝ': 4, 'ⓡ': 8}.get(c, 0)
    o = ord(c)
    if 0x11A8 <= o <= 0x11FF or 0xD7CB <= o <= 0xD7FB:   # 옛 한글 받침
        return 1
    if 0x1161 <= o <= 0x11A7 or 0xD7B0 <= o <= 0xD7C6:   # 옛 한글 모음으로 끝남
        return 0
    return -1

def josa(s):
    """'이(가)' 같은 조사 표기를 앞 글자 받침에 맞게 고친다(태그는 건드리지 않음)."""
    def fix(m):
        pre = re.sub(r'<[^>]+>', '', s[:m.start()]).rstrip('"\'’” ')
        j = m.group(1)
        yes, no = _JO[j]
        b = _batchim(pre[-1]) if pre else -1
        if b < 0:
            return no
        if j in ('으로(로)', '(으)로'):
            return no if b in (0, 8) else yes
        return yes if b else no
    return re.sub('(' + '|'.join(re.escape(k) for k in _JO) + ')', fix, s)


# ------------------------------------------------------------------ 표 · 보기 · 지문 상자
def table(headers, rows, first_bold=True):
    h = '<table class="tb"><thead><tr>' + ''.join('<th>%s</th>' % c for c in headers) + '</tr></thead><tbody>'
    for row in rows:
        h += '<tr>' + ''.join(('<td class="b">%s</td>' if (i == 0 and first_bold) else '<td>%s</td>') % c for i, c in enumerate(row)) + '</tr>'
    return h + '</tbody></table>'

def BOGI(items, title='보 기', labels='ㄱㄴㄷㄹ'):
    """<보기> 상자. items: 문장들. labels 가 있으면 앞에 'ㄱ.' 을 붙이고, None 이면 붙이지 않는다."""
    if labels:
        body = ''.join('<p>%s. %s</p>' % (labels[i], t) for i, t in enumerate(items))
    else:
        body = ''.join('<p>%s</p>' % t for t in items)
    return '<div class="bogi"><div class="bt">&lt;%s&gt;</div>%s</div>' % (title, body)

def BOX(lines, title=None):
    t = '<div class="bt">%s</div>' % title if title else ''
    return '<div class="bogi">' + t + ''.join('<p>%s</p>' % x for x in lines) + '</div>'

def DLG(turns, title=None):
    """대화·토의 상자. turns: [(화자, 말)]"""
    t = '<div class="bt">%s</div>' % title if title else ''
    return '<div class="bogi">' + t + ''.join('<p><b>%s</b>: %s</p>' % (s, x) for s, x in turns) + '</div>'


# ------------------------------------------------------------------ 선택지 · 문항 조립
def _norm_choice(s):
    return re.sub(r'\s+', '', plain(str(s)))


class Item:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _pick_choices(r, right, wrongs):
    seen = {_norm_choice(right)}
    ws = []
    for w in wrongs:
        k = _norm_choice(w)
        if k in seen:
            continue
        seen.add(k); ws.append(w)
    if len(ws) < 4:
        return None
    ws = ws[:4] if len(ws) == 4 else r.sample(ws, 4)
    opts = [(right, True)] + [(w, False) for w in ws]
    r.shuffle(opts)
    return opts


def mc(body, right, wrongs, *, steps, core='', point='', lv='중', fam='a', r=None, ref=None, vertical=None, keep=False):
    """5지선다(정답 1개). keep=True 면 선택지를 right 다음 wrongs 순서 그대로(① 이 정답이 되지 않게 정렬은 하지 않음)."""
    r = r or random.Random(1)
    if keep:
        seen, opts = set(), []
        for o in [right] + list(wrongs):
            k = _norm_choice(o)
            if k in seen:
                continue
            seen.add(k); opts.append((o, o is right))
        if len(opts) != 5:
            return None
        opts = [(o, o == right) for o, _ in opts]
    else:
        opts = _pick_choices(r, right, wrongs)
    if opts is None:
        return None
    ans = [i for i, o in enumerate(opts) if o[1]][0] + 1
    return Item(body=body, opts=[o[0] for o in opts], ans=ans, steps=steps, core=core, point=point, lv=lv, fam=fam, vertical=vertical, ref=ref)


def mcs(body, items, *, steps, core='', point='', lv='중', fam='a', r=None, ref=None, vertical=None):
    """선택지가 이미 5개로 정해져 있고 정답 번호도 정해진 경우. items: [(선택지, 정답여부)] 5개, 정답 1개."""
    if len(items) != 5 or sum(1 for _, t in items if t) != 1:
        return None
    if len({_norm_choice(o) for o, _ in items}) != 5:
        return None
    ans = [i for i, o in enumerate(items) if o[1]][0] + 1
    return Item(body=body, opts=[o for o, _ in items], ans=ans, steps=steps, core=core, point=point, lv=lv, fam=fam, vertical=vertical, ref=ref)


COMBOS = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄱ, ㄴ', 'ㄱ, ㄷ', 'ㄴ, ㄷ', 'ㄱ, ㄴ, ㄷ']

def bogi(intro, stmts, *, pre='', post='', lv='중', fam='a', r=None, core='', point='', ref=None,
         ask='이에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?'):
    """ㄱㄴㄷ 형. stmts: [(문장, 참/거짓(bool), 풀이문)] 3개. 참이 1개 이상, 거짓이 1개 이상이어야 한다."""
    assert len(stmts) == 3
    r = r or random.Random(1)
    truth = [s[1] for s in stmts]
    if not any(truth) or all(truth):
        return None
    right = ', '.join('ㄱㄴㄷ'[i] for i in range(3) if truth[i])
    others = [c for c in COMBOS if c != right]
    ws = r.sample(others, 4)
    opts = sorted([right] + ws, key=lambda c: (len(c), COMBOS.index(c)))
    ans = opts.index(right) + 1
    body = (P(intro) if intro else '') + pre + (P(ask) if ask else '') + BOGI([s[0] for s in stmts]) + post
    # 풀이문이 이미 '옳다.'·'옳지 않다.'로 시작하면 판정을 두 번 쓰지 않는다
    steps = ['%s. %s %s' % ('ㄱㄴㄷ'[i], '옳다.' if stmts[i][1] else '옳지 않다.', re.sub(r'^\s*(?:옳다|옳지 않다|적절하다|적절하지 않다)\.\s*', '', stmts[i][2])) for i in range(3)]
    return Item(body=body, opts=opts, ans=ans, steps=steps, core=core, point=point, lv=lv, fam=fam, vertical=False, ref=ref)


# ------------------------------------------------------------------ HTML 출력
def render(it, tag, no, code, pts, qid=None, sid=None, src='문제 은행 · 제작 문항', head=''):
    """Item -> (q_html, exp_html)"""
    qid = qid or 'q-bk%s%04d' % (tag, no)
    sid = sid or 's-bk%s%04d' % (tag, no)
    longest = max(len(plain(o)) for o in it.opts)
    v = it.vertical if it.vertical is not None else longest > 17
    chs = '<div class="chs%s">' % (' v' if v else '') + ''.join('<div><b>%s</b><span>%s</span></div>' % (CIR[i], o) for i, o in enumerate(it.opts)) + '</div>'
    q = '<div class="q" id="%s"><div class="qh"><b class="qn">%d</b><span class="qp">[%d점]</span></div><div class="qs">%s%s%s</div></div>' % (qid, no, pts, head, it.body, chs)
    ty = BYTAG[tag]
    secs = SUBS[ty['sub']]['secs']
    rl = it.ref if it.ref else [ty['sec']]
    refs = '<div class="rv"><span class="lb">이 문제를 틀렸다면 다시 공부할 부분</span>' + ''.join(
        '<div class="st">→ %s <span class="sm">(개념 정리 %s %d)</span></div>' % (esc(secs[n - 1]), ty['sub'], n) for n in rl) + '</div>'
    e = '<div class="sol" id="%s"><div class="sh"><span class="sn">%d</span><span class="sa">정답 %s</span><span class="sc2">%s</span></div><div class="ss">출처 : %s</div><p><span class="lb">풀이</span></p>' % (sid, no, CIR[it.ans - 1], code, src)
    e += ''.join('<p class="st">%s</p>' % s for s in it.steps)
    if it.core:
        e += '<p><span class="lb">핵심 개념</span> %s</p>' % it.core
    if it.point:
        e += '<p><span class="lb">출제 포인트</span> %s</p>' % it.point
    e += refs + '</div>'
    return josa(q), josa(e)


def pts_for(lv, r):
    return {'하': 2, '중': 3, '상': r.choice([3, 4]), '최': 4}.get(lv, 3)


def sig(it):
    return _norm_choice(it.body) + '|' + '|'.join(sorted(_norm_choice(o) for o in it.opts))
