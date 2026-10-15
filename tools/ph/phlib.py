# -*- coding: utf-8 -*-
"""역학과 에너지(ph) 문제 생성 라이브러리.

생성기 파일(types_*.py)은 이 모듈의 도구만으로 문항을 만든다.

    from phlib import *

    @T('ph001')                       # outline.py 의 유형 번호(tag)
    def gen(r, k):                    # r: random.Random(고정 시드), k: 시도 번호(0,1,2…)
        F1 = r.choice([3, 6, 9]); ...
        return mc(P('…'), right='5 N', wrongs=['1 N', '7 N', '12 N', '2 N'],
                  steps=['…'], core='…', lv='하', fam='a')

반환값이 None 이면 그 시도는 건너뛴다. 러너(build.py)가 유형마다 n개가 모일 때까지 gen 을 반복 호출하고,
같은 문제(본문+선택지가 같은 것)는 자동으로 걸러낸다.
"""
import random, re, math, html as _html
from outline import SUBS, BYTAG, TYPES

CIR = '①②③④⑤'
INK, GR, BL, RD, OR, GN, PU, LG = '#1b2430', '#586476', '#2f7fd0', '#d6453d', '#f2b400', '#2f9d66', '#6d4cc4', '#e3e9f1'
FONT = 'Paperozi,Paperlogy,sans-serif'

REGISTRY = {}            # tag -> gen 함수


def T(tag):
    def deco(f):
        assert tag in BYTAG, tag
        REGISTRY[tag] = f
        return f
    return deco


# ------------------------------------------------------------------ 글자 도구
def esc(s):
    return _html.escape(str(s), quote=False)

def sub(s): return '<sub>%s</sub>' % s
def sup(s): return '<sup>%s</sup>' % s
def frac(a, b): return '<span class="fr"><span>%s</span><span>%s</span></span>' % (a, b)
def sq(x): return '√%s' % x

def num(x, nd=2):
    """숫자를 보기 좋게: 3.0 -> 3, 2.50 -> 2.5, 소수 nd자리 반올림."""
    if isinstance(x, int): return str(x)
    if abs(x - round(x)) < 1e-9: return str(int(round(x)))
    s = ('%.' + str(nd) + 'f') % x
    return s.rstrip('0').rstrip('.')

def U(x, unit, nd=2):
    return num(x, nd) + ' ' + unit

def rad(a, b):
    """a√b 를 간단히: rad(2,3) -> 2√3, rad(1,2) -> √2, 완전제곱이면 정수."""
    k = 1
    for d in range(int(math.isqrt(b)), 1, -1):
        if b % (d * d) == 0:
            k *= d; b //= d * d; break
    a *= k
    if b == 1: return str(a)
    return (str(a) if a != 1 else '') + '√' + str(b)

def P(*t):
    return '<p>' + ''.join(t) + '</p>'

def BR(): return ''

def plain(h):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)).strip()


# ------------------------------------------------------------------ 표 · 보기 · 그림
def table(headers, rows, first_bold=True, small=False):
    h = '<table class="tb"><thead><tr>' + ''.join('<th>%s</th>' % c for c in headers) + '</tr></thead><tbody>'
    for row in rows:
        h += '<tr>' + ''.join(('<td class="b">%s</td>' if (i == 0 and first_bold) else '<td>%s</td>') % c for i, c in enumerate(row)) + '</tr>'
    return h + '</tbody></table>'

def FIG(svg, width=None):
    st = ' style="width:%s"' % width if width else ''
    return '<div class="fg"%s>%s</div>' % (st, svg)

def BOGI(items):
    """<보기> 상자. items: 문장 3개(문자열)."""
    return '<div class="bogi"><div class="bt">&lt;보기&gt;</div>' + ''.join('<p>%s. %s</p>' % ('ㄱㄴㄷㄹ'[i], t) for i, t in enumerate(items)) + '</div>'

def BOX(lines):
    """[실험 과정] 같은 일반 상자(가운데 정렬 없이)."""
    return '<div class="bogi">' + ''.join('<p>%s</p>' % t for t in lines) + '</div>'


# ------------------------------------------------------------------ SVG
class Fig:
    def __init__(self, w, h):
        self.w, self.h, self.o = w, h, []
    @staticmethod
    def _n(v):
        return ('%.1f' % v).rstrip('0').rstrip('.')
    def line(self, x1, y1, x2, y2, c=INK, w=1.4, dash=None, arrow=False, cap='butt'):
        n = self._n
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s stroke-linecap="%s"/>' % (n(x1), n(y1), n(x2), n(y2), c, w, d, cap))
        if arrow:
            self._head(x1, y1, x2, y2, c, w)
        return self
    def _head(self, x1, y1, x2, y2, c, w, size=None):
        n = self._n
        a = math.atan2(y2 - y1, x2 - x1)
        L = size or (6 + w * 1.6)
        p = [(x2, y2), (x2 - L * math.cos(a - .38), y2 - L * math.sin(a - .38)), (x2 - L * math.cos(a + .38), y2 - L * math.sin(a + .38))]
        self.o.append('<polygon points="%s" fill="%s"/>' % (' '.join('%s,%s' % (n(x), n(y)) for x, y in p), c))
    def arrow(self, x1, y1, x2, y2, c=INK, w=2, dash=None):
        return self.line(x1, y1, x2, y2, c, w, dash, arrow=True)
    def rect(self, x, y, w, h, fill='none', stroke=INK, sw=1.4, r=0, dash=None):
        n = self._n
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.o.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>' % (n(x), n(y), n(w), n(h), n(r), fill, stroke, sw, d))
        return self
    def circ(self, cx, cy, r, fill='none', stroke=INK, sw=1.4, dash=None):
        n = self._n
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        self.o.append('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>' % (n(cx), n(cy), n(r), fill, stroke, sw, d))
        return self
    def ell(self, cx, cy, rx, ry, fill='none', stroke=INK, sw=1.4, dash=None, rot=0):
        n = self._n
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        t = ' transform="rotate(%s %s %s)"' % (n(rot), n(cx), n(cy)) if rot else ''
        self.o.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="%s" stroke-width="%s"%s%s/>' % (n(cx), n(cy), n(rx), n(ry), fill, stroke, sw, d, t))
        return self
    def poly(self, pts, fill='none', stroke=INK, sw=1.4, close=True, dash=None):
        n = self._n
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        tag = 'polygon' if close else 'polyline'
        self.o.append('<%s points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"%s/>' % (tag, ' '.join('%s,%s' % (n(x), n(y)) for x, y in pts), fill, stroke, sw, d))
        return self
    def path(self, d, fill='none', stroke=INK, sw=1.6, dash=None):
        dd = ' stroke-dasharray="%s"' % dash if dash else ''
        self.o.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round" stroke-linecap="round"%s/>' % (d, fill, stroke, sw, dd))
        return self
    def text(self, x, y, s, size=13, anchor='middle', bold=False, c=INK, italic=False, rot=0):
        n = self._n
        t = ' transform="rotate(%s %s %s)"' % (n(rot), n(x), n(y)) if rot else ''
        st = ' font-style="italic"' if italic else ''
        self.o.append('<text x="%s" y="%s" font-size="%s" text-anchor="%s" font-weight="%s" fill="%s" font-family="%s"%s%s>%s</text>' % (n(x), n(y), size, anchor, 700 if bold else 500, c, FONT, st, t, esc(s)))
        return self
    def sin_path(self, x0, y0, amp, wl, cycles, phase=0.0, steps=40, c=BL, sw=2.2):
        """x0 에서 시작, 중심선 y0, 진폭 amp(화면 단위, 위가 +), 파장 wl(화면 단위), phase: 라디안."""
        pts = []
        N = int(steps * cycles)
        for i in range(N + 1):
            x = x0 + wl * cycles * i / N
            y = y0 - amp * math.sin(2 * math.pi * (x - x0) / wl + phase)
            pts.append((x, y))
        return self.poly(pts, 'none', c, sw, close=False)
    def spring(self, x1, y, x2, coils=7, amp=7, c=INK, sw=1.6):
        """수평 용수철(y 고정)."""
        pts = [(x1, y)]
        L = x2 - x1
        pre = L * 0.12
        pts.append((x1 + pre, y))
        n = coils * 2
        for i in range(1, n + 1):
            xx = x1 + pre + (L - 2 * pre) * i / n
            pts.append((xx, y + (amp if i % 2 else -amp)))
        pts.append((x2 - pre, y)); pts.append((x2, y))
        return self.poly(pts, 'none', c, sw, close=False)
    def hatch(self, x, y, w, c=GR, side='down', step=7, ln=7):
        """바닥/벽 빗금: side 'down' 이면 선 아래쪽."""
        self.line(x, y, x + w, y, c, 1.6)
        i = 0.0
        while i <= w:
            if side == 'down': self.line(x + i, y, x + i - ln * .7, y + ln, c, 1)
            elif side == 'left': pass
            i += step
        return self
    def svg(self, scale=1.0):
        w, h = self.w, self.h
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s</svg>' % (w, h, w * scale, h * scale, ''.join(self.o))


class Plot(Fig):
    """좌표 그래프. 데이터 좌표 → 화면 좌표 변환을 px(), py() 로 한다."""
    def __init__(self, w, h, xmax, ymax, xmin=0, ymin=0, ml=46, mr=16, mt=14, mb=30):
        super().__init__(w, h)
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.ml, self.mr, self.mt, self.mb = ml, mr, mt, mb
    def px(self, x): return self.ml + (x - self.xmin) / (self.xmax - self.xmin) * (self.w - self.ml - self.mr)
    def py(self, y): return self.h - self.mb - (y - self.ymin) / (self.ymax - self.ymin) * (self.h - self.mt - self.mb)
    def axes(self, xlabel='', ylabel='', xticks=(), yticks=(), xfmt=None, yfmt=None, grid=False, origin=True, zero_line=True):
        fx = xfmt or num
        fy = yfmt or num
        x0, y0 = self.px(self.xmin), self.py(self.ymin)
        if grid:
            for t in xticks:
                self.line(self.px(t), self.py(self.ymin), self.px(t), self.py(self.ymax), LG, 1)
            for t in yticks:
                self.line(self.px(self.xmin), self.py(t), self.px(self.xmax), self.py(t), LG, 1)
        self.arrow(x0, y0, self.px(self.xmax) + 6, y0, INK, 1.4)
        self.arrow(x0, y0, x0, self.py(self.ymax) - 6, INK, 1.4)
        if zero_line and self.ymin < 0:
            self.line(x0, self.py(0), self.px(self.xmax), self.py(0), INK, 1.2)
        for t in xticks:
            if t == self.xmin and not origin: continue
            self.line(self.px(t), y0 if self.ymin >= 0 else self.py(0), self.px(t), (y0 if self.ymin >= 0 else self.py(0)) + 4, INK, 1)
            self.text(self.px(t), self.h - self.mb + 17 if self.ymin >= 0 else self.py(0) + 17, fx(t), 11.5, c=GR)
        for t in yticks:
            if t == self.ymin and not origin: continue
            self.line(x0, self.py(t), x0 - 4, self.py(t), INK, 1)
            self.text(x0 - 7, self.py(t) + 4, fy(t), 11.5, 'end', c=GR)
        if xlabel: self.text(self.w - self.mr + 4, self.h - 4, xlabel, 12.5, 'end', True, GR)
        if ylabel: self.text(self.ml - 6, 11, ylabel, 12.5, 'end', True, GR)
        return self
    def pl(self, pts, c=BL, sw=2.4, dash=None):
        return self.poly([(self.px(x), self.py(y)) for x, y in pts], 'none', c, sw, close=False, dash=dash)
    def dash_to_axes(self, x, y, c=GR):
        self.line(self.px(x), self.py(y), self.px(x), self.py(self.ymin), c, 1, '4 3')
        self.line(self.px(x), self.py(y), self.px(self.xmin), self.py(y), c, 1, '4 3')
        return self
    def fill_under(self, pts, c='#cfe2f7', base=0):
        P2 = [(self.px(x), self.py(y)) for x, y in pts]
        P2 = [(P2[0][0], self.py(base))] + P2 + [(P2[-1][0], self.py(base))]
        self.o.insert(0, '<polygon points="%s" fill="%s" stroke="none"/>' % (' '.join('%s,%s' % (self._n(x), self._n(y)) for x, y in P2), c))
        return self


# ------------------------------------------------------------------ 선택지 · 문항 조립
def _numval(s):
    m = re.match(r'^\s*(-?\d+(?:\.\d+)?)', re.sub(r'<[^>]+>', '', str(s)))
    return float(m.group(1)) if m else None

def _norm_choice(s):
    return re.sub(r'\s+', '', plain(str(s)))


class Item:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _pick_choices(r, right, wrongs, sort):
    """정답 1개 + 오답 4개로 5지선다 구성. 중복 제거. sort: 'num'(작은 값 순) / 'shuf'."""
    seen = {_norm_choice(right)}
    ws = []
    for w in wrongs:
        k = _norm_choice(w)
        if k in seen: continue
        seen.add(k); ws.append(w)
    if len(ws) < 4: return None
    ws = ws[:] if len(ws) == 4 else r.sample(ws, 4)
    opts = [(right, True)] + [(w, False) for w in ws]
    if sort == 'num':
        vals = [_numval(o[0]) for o in opts]
        if None in vals or len(set(vals)) < 5:
            r.shuffle(opts)
        else:
            opts = [o for _, _, o in sorted(zip(vals, range(5), opts), key=lambda z: (z[0], z[1]))]
    else:
        r.shuffle(opts)
    return opts


def mc(body, right, wrongs, *, steps, core='', point='', lv='중', fam='a', sort='num', vertical=None, r=None, ref=None):
    """5지선다(정답 1개). body: 문제 본문 HTML(P/FIG/table/BOGI 조합). right/wrongs: 선택지 문자열(HTML 가능).
    r 는 선택지 순서를 정할 random.Random(생성기에서 받은 r 를 넘긴다)."""
    opts = _pick_choices(r or random.Random(1), right, wrongs, sort)
    if opts is None: return None
    ans = [i for i, o in enumerate(opts) if o[1]][0] + 1
    return Item(body=body, opts=[o[0] for o in opts], ans=ans, steps=steps, core=core, point=point, lv=lv, fam=fam, vertical=vertical, ref=ref)


COMBOS = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄱ, ㄴ', 'ㄱ, ㄷ', 'ㄴ, ㄷ', 'ㄱ, ㄴ, ㄷ']

def bogi(intro, stmts, *, pre='', post='', lv='중', fam='a', r=None, core='', point='', ref=None, ask='이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'):
    """<보기> ㄱㄴㄷ 형. stmts: [(문장, 참/거짓(bool), 풀이문), ...] 3개. 참이 1개 이상이어야 한다.
    intro: 문제 첫 문단(HTML, P() 로 감싸지 않은 일반 문자열), pre: 그림·표 HTML(문단 뒤), post: 보기 뒤에 붙일 것."""
    assert len(stmts) == 3
    r = r or random.Random(1)
    truth = [s[1] for s in stmts]
    if not any(truth): return None
    right = ', '.join('ㄱㄴㄷ'[i] for i in range(3) if truth[i])
    # 5지: 정답 + 오답 4개(7개 조합 중)
    others = [c for c in COMBOS if c != right]
    ws = r.sample(others, 4)
    opts = sorted([right] + ws, key=lambda c: (len(c), COMBOS.index(c)))
    ans = opts.index(right) + 1
    # 질문 문장은 보기 앞의 마지막 문단으로 넣는다
    body = P(intro) + pre + (P(ask) if ask else '') + BOGI([s[0] for s in stmts]) + post
    steps = ['%s. %s %s' % ('ㄱㄴㄷ'[i], '옳다.' if stmts[i][1] else '옳지 않다.', stmts[i][2]) for i in range(3)]
    return Item(body=body, opts=opts, ans=ans, steps=steps, core=core, point=point, lv=lv, fam=fam, vertical=False, ref=ref)


def numbered(opts):
    return opts


# ------------------------------------------------------------------ HTML 출력
def render(it, tag, no, code, sub_key, pts, qid=None, sid=None, src='문제 은행 · 제작 문항'):
    """Item -> (q_html, exp_html)"""
    qid = qid or 'q-bk%s%04d' % (tag, no)
    sid = sid or 's-bk%s%04d' % (tag, no)
    longest = max(len(plain(o)) for o in it.opts)
    v = it.vertical if it.vertical is not None else longest > 17
    chs = '<div class="chs%s">' % (' v' if v else '') + ''.join('<div><b>%s</b><span>%s</span></div>' % (CIR[i], o) for i, o in enumerate(it.opts)) + '</div>'
    q = '<div class="q" id="%s"><div class="qh"><b class="qn">%d</b><span class="qp">[%d점]</span></div><div class="qs">%s%s</div></div>' % (qid, no, pts, it.body, chs)
    refs = ''
    ty = BYTAG[tag]
    secs = SUBS[ty['sub']]['secs']
    rl = it.ref if it.ref else [ty['sec']]
    refs = '<div class="rv"><span class="lb">이 문제를 틀렸다면 다시 공부할 부분</span>' + ''.join(
        '<div class="st">→ %s <span class="sm">(개념 정리 %s %d)</span></div>' % (esc(secs[n - 1]), ty['sub'], n) for n in rl) + '</div>'
    e = '<div class="sol" id="%s"><div class="sh"><span class="sn">%d</span><span class="sa">정답 %s</span><span class="sc2">%s</span></div><div class="ss">출처 : %s</div><p><span class="lb">풀이</span></p>' % (sid, no, CIR[it.ans - 1], code, src)
    e += ''.join('<p class="st">%s</p>' % s for s in it.steps)
    if it.core: e += '<p><span class="lb">핵심 개념</span> %s</p>' % it.core
    if it.point: e += '<p><span class="lb">출제 포인트</span> %s</p>' % it.point
    e += refs + '</div>'
    return q, e


def pts_for(lv, r):
    return {'하': 2, '중': 3, '상': r.choice([3, 4]), '최': 4}.get(lv, 3)


def sig(it):
    return _norm_choice(it.body) + '|' + '|'.join(sorted(_norm_choice(o) for o in it.opts))
