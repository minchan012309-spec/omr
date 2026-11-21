"""물질과 에너지(해원고 부교재) 문항 조판 도구.
간단한 표기 → 기존 문제은행 HTML.  수식은 MathML(<math>)로 만들어 Latin Modern Math 글꼴로 그린다.
표기 규칙
  $...$          수식(TeX 일부: _ ^ {} \\frac \\text \\Delta \\times \\cdot \\to \\le \\ge \\approx)
  \\frac{a}{b}   수식 밖에서도 분수
  H2O, CO2       원소 기호 뒤 숫자는 아래 첨자(자동)
  ^{...} _{...}  수식 밖 위/아래 첨자
  (g)(l)(s)(aq)  상태 표시는 수식 글꼴 기울임
  -> <=>         화살표
"""
import re, html, hashlib

MI = {c: chr(0x1D44E + i) for i, c in enumerate('abcdefghijklmnopqrstuvwxyz')}
MI['h'] = 'ℎ'
MI.update({c: chr(0x1D434 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')})

def esc(s): return html.escape(s, quote=False)

# ---------- TeX 일부 → MathML ----------
class _P:
    def __init__(s, t): s.t, s.i = t, 0
    def peek(s): return s.t[s.i] if s.i < len(s.t) else ''
    def eof(s): return s.i >= len(s.t)

CMDS = {'\\Delta': ('mi', 'Δ', 'normal'), '\\times': ('mo', '×', None), '\\cdot': ('mo', '·', None),
        '\\to': ('mo', '→', None), '\\rightarrow': ('mo', '→', None), '\\le': ('mo', '≤', None), '\\ge': ('mo', '≥', None),
        '\\approx': ('mo', '≈', None), '\\rightleftharpoons': ('mo', '⇄', None), '\\infty': ('mi', '∞', None),
        '\\pm': ('mo', '±', None), '\\ne': ('mo', '≠', None), '\\quad': ('mspace', '', None), '\\Rightarrow': ('mo', '⇒', None),
        '\\%': ('mo', '%', None), '\\degC': ('mi', '℃', 'normal'), '\\prime': ('mo', '′', None), '\\lt': ('mo', '&lt;', None),
        '\\gt': ('mo', '&gt;', None), '\\cdots': ('mo', '⋯', None), '\\circ': ('mo', '∘', None), '\\sum': ('mo', '∑', None), '\\Sigma': ('mi', 'Σ', 'normal'), '\\propto': ('mo', '∝', None), '\\left': ('mspace', '', None), '\\right': ('mspace', '', None)}

def _atom(p):
    c = p.peek()
    if c == '{':
        p.i += 1; inner = _seq(p, '}'); p.i += 1
        return '<mrow>' + inner + '</mrow>'
    if c == '\\':
        m = re.match(r'\\([A-Za-z]+|.)', p.t[p.i:]); cmd = '\\' + m.group(1); p.i += len(m.group(0))
        if cmd == '\\frac':
            a = _atom(_skip(p)); b = _atom(_skip(p)); return f'<mfrac>{a}{b}</mfrac>'
        if cmd == '\\dfrac':
            a = _atom(_skip(p)); b = _atom(_skip(p)); return f'<mstyle displaystyle="true"><mfrac>{a}{b}</mfrac></mstyle>'
        if cmd == '\\sqrt':
            a = _atom(_skip(p)); return f'<msqrt>{a}</msqrt>'
        if cmd in ('\\text', '\\mathrm'):
            _skip(p); assert p.peek() == '{'; j = p.t.index('}', p.i); s = p.t[p.i + 1:j]; p.i = j + 1
            return f'<mtext>{esc(s)}</mtext>' if cmd == '\\text' else f'<mi mathvariant="normal">{esc(s)}</mi>'
        if cmd == '\\,': return '<mtext>\u2009</mtext>'
        if cmd == '\\ ': return '<mtext>\u00a0</mtext>'
        if cmd in CMDS:
            tg, v, var = CMDS[cmd]
            if tg == 'mspace': return '' if cmd in ('\\left', '\\right') else '<mtext>\u2003</mtext>'
            return f'<{tg}{" mathvariant=\"normal\"" if var else ""}>{v}</{tg}>'
        raise ValueError('알 수 없는 명령 ' + cmd)
    mc = re.match(r'\[([A-Z][A-Za-z0-9]*)\]', p.t[p.i:])
    if mc:
        p.i += len(mc.group(0))
        inner = ''.join(f'<msub><mi mathvariant="normal">{t}</mi><mn>{d}</mn></msub>' if d else f'<mi mathvariant="normal">{t}</mi>'
                        for t, d in re.findall(r'([A-Za-z]+)(\d*)', mc.group(1)))
        return f'<mrow><mo stretchy="false">[</mo>{inner}<mo stretchy="false">]</mo></mrow>'
    m = re.match(r'\d+(?:\.\d+)?', p.t[p.i:])
    if m: p.i += len(m.group(0)); return f'<mn>{m.group(0)}</mn>'
    p.i += 1
    if c == ' ': return ''
    if re.match(r'[A-Za-z]', c): return f'<mi>{c}</mi>'
    if c in 'Δ': return '<mi mathvariant="normal">Δ</mi>'
    if c in '+-−=<>(),/[]|:;!.×·→⇄≤≥≈′″%~∼':
        c = {'-': '−', '<': '&lt;', '>': '&gt;'}.get(c, c)
        stretch = ' stretchy="false"' if c in '()[]|' else ''
        return f'<mo{stretch}>{c}</mo>'
    return f'<mtext>{esc(c)}</mtext>'

def _skip(p):
    while p.peek() == ' ': p.i += 1
    return p

def _seq(p, end=''):
    out = []
    while not p.eof() and p.peek() != end:
        if p.peek() in '_^':
            a = '<mrow></mrow>'
        else:
            a = _atom(p)
        if not a: continue
        sub = sup = None
        while p.peek() in ('_', '^'):
            op = p.peek(); p.i += 1; x = _atom(_skip(p))
            if op == '_': sub = x
            else: sup = x
        if sub and sup: a = f'<msup><msub>{a}{sub}</msub>{sup}</msup>'
        elif sub: a = f'<msub>{a}{sub}</msub>'
        elif sup: a = f'<msup>{a}{sup}</msup>'
        out.append(a)
    return ''.join(out)

def tex(s, display=False):
    p = _P(s.strip()); body = _seq(p)
    assert p.eof(), s
    return f'<math{" display=\"block\"" if display else ""}>{body}</math>'

# ---------- 본문 표기 ----------
STATE = {'g': 'g', 'l': 'l', 's': 's', 'aq': 'aq'}
def _state(m):
    st = m.group(1); rest = m.group(2) or ''
    return '(<span class="mx">' + ''.join(MI[c] for c in st) + '</span>' + rest + ')'

def chem(s):
    """수식 밖 문자열: 화학식 첨자, 상태, 화살표."""
    s = s.replace('<=>', '⇄').replace('->', '→')
    s = re.sub(r'&(?!(?:lt|gt|amp|nbsp|quot|#\d+);)', '&amp;', s)
    s = re.sub(r'<(?!/?(?:b|u|i|small|sub|sup|br|strong|span)\b)', '&lt;', s)
    s = re.sub(r'\^\{([^}]*)\}', lambda m: '<sup>' + m.group(1).replace('-', '−') + '</sup>', s)
    s = re.sub(r'_\{([^}]*)\}', r'<sub>\1</sub>', s)
    s = re.sub(r'(?<=[A-Za-z\)\]])(\d+)(?![\d.,]*\s?(?:%|M\b|g\b|kJ|J\b|mL|L\b|초|분|s\b|℃|K\b|배|몰|mol|kPa|기압|atm|번))', r'<sub>\1</sub>', s)
    s = re.sub(r'\((aq|g|l|s)(, [^)]{1,12})?\)', _state, s)
    return s

def fmt(s):
    """$수식$·\\frac와 본문을 함께 변환."""
    out = []
    for i, part in enumerate(re.split(r'(\$[^$]+\$)', s)):
        if i % 2: out.append(tex(part[1:-1]))
        else:
            # 수식 밖 \frac{a}{b}
            segs = re.split(r'(\\frac\{[^}]*\}\{[^}]*\})', part)
            for j, g in enumerate(segs):
                out.append(tex(g) if j % 2 else chem(g).replace('\n', '<br>'))
    return ''.join(out)

CIRC = '①②③④⑤⑥⑦⑧'
def choices(chs, layout=None):
    if layout is None:
        L = max(len(re.sub(r'\$|\\frac|[{}_^]', '', c)) for c in chs)
        layout = '' if L <= 9 else ('w2' if L <= 22 else 'v')
    cls = 'chs' + ({'v': ' v', 'w2': ' w2', '': ''}[layout])
    return f'<div class="{cls}">' + ''.join(f'<div><b>{CIRC[i]}</b><span>{fmt(c)}</span></div>' for i, c in enumerate(chs)) + '</div>'

def bogi(items, title='보기'):
    return '<div class="bogi"><div class="bt">&lt;' + title + '&gt;</div>' + ''.join(f'<p>{fmt(x)}</p>' for x in items) + '</div>'

def box(lines):
    return '<div class="hwbox">' + ''.join(f'<p>{fmt(x)}</p>' for x in lines) + '</div>'

def table(rows, head=True, cls='tb'):
    h = f'<table class="{cls}">'
    for i, r in enumerate(rows):
        tag = 'th' if head and i == 0 else 'td'
        h += '<tr>' + ''.join(f'<{tag}>{fmt(str(c))}</{tag}>' for c in r) + '</tr>'
    return h + '</table>'

def fig(src, w=70):
    if '/' not in src: src = f'fig/hw/{src}.png'
    return f'<div class="fg"><img src="{src}" style="width:{w}%" alt=""></div>'

def p(s): return f'<p>{fmt(s)}</p>'

def qhtml(qid, no, pts, body):
    return (f'<div class="q" id="q-{qid}"><div class="qh"><b class="qn">{no}</b><span class="qp">[{pts}점]</span></div>'
            f'<div class="qs">{body}</div></div>')

ANSNAME = lambda a: ', '.join(CIRC[int(x) - 1] for x in str(a).split(',')) if re.fullmatch(r'[1-8](,[1-8])*', str(a)) else str(a)

def solhtml(qid, no, code, ans, src, steps, key='', point='', rv=None, ansText=None):
    h = (f'<div class="sol" id="s-{qid}"><div class="sh"><span class="sn">{no}</span><span class="sa">정답 {ansText or ANSNAME(ans)}</span>'
         f'<span class="sc2">{code}</span></div><div class="ss">출처 : {src}</div><p><span class="lb">풀이</span></p>')
    for s in steps:
        h += f'<p class="st">{fmt(s)}</p>'
    if key: h += f'<p><span class="lb">핵심 개념</span> {fmt(key)}</p>'
    if point: h += f'<p><span class="lb">출제 포인트</span> {fmt(point)}</p>'
    if rv: h += '<div class="rv"><span class="lb">이 문제를 틀렸다면 다시 공부할 부분</span>' + ''.join(f'<div class="st">→ {esc(t)} <span class="sm">(개념 정리 {esc(w)})</span></div>' for t, w in rv) + '</div>'
    return h + '</div>'

def h8(s): return hashlib.md5(s.encode()).hexdigest()[:8]

GIYEOK = 'ㄱㄴㄷㄹㅁ'
COMBO5 = [['ㄱ'], ['ㄴ'], ['ㄷ'], ['ㄱ', 'ㄴ'], ['ㄱ', 'ㄷ'], ['ㄴ', 'ㄷ'], ['ㄱ', 'ㄴ', 'ㄷ']]
