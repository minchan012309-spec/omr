# -*- coding: utf-8 -*-
"""문제은행 HTML(+MathML) → XeLaTeX 본문.

수식 규칙
- MathML, 화학식(C<sub>2</sub>H<sub>2</sub>), 숫자·단위·영문자, 기울인 변수(span.mx)는 모두 수식으로 만든다.
- 원소 기호·단위는 정자(\\mathrm), 변수(MathML mi 한 글자, span.mx)는 기울임.
- 글꼴 선택은 pre.tex 가 한다(HYHWPEQ 기호 → 나머지 Latin Modern Math).
"""
import re
from bs4 import BeautifulSoup, NavigableString, Tag

TEX_ESC = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
           '~': r'\textasciitilde{}', '^': r'\textasciicircum{}', '\\': r'\textbackslash{}'}

def tesc(s):
    return ''.join(TEX_ESC.get(c, c) for c in s)

# 수식으로 옮길 유니코드 기호
MSYM = {'−': '-', '-': '-', '×': r'\times', '·': r'\cdot', '⋅': r'\cdot', '→': r'\rightarrow', '⇄': r'\rightleftarrows',
        '≈': r'\approx', '∴': r'\therefore', '℃': '℃', '°': r'^{\circ}', 'Δ': r'\Delta', '≤': r'\le', '≥': r'\ge',
        '<': '<', '>': '>', '=': '=', '+': '+', '/': '/', '%': r'\%', '±': r'\pm', '∼': r'\sim', '✓': r'\checkmark'}
OPS = set('+-=<>') | {r'\times', r'\cdot', r'\rightarrow', r'\rightleftarrows', r'\approx', r'\le', r'\ge', r'\pm'}
ITAL = {'𝑎': 'a', '𝑔': 'g', '𝑙': 'l', '𝑞': 'q', '𝑠': 's'}

# 수식 문자: ASCII 영숫자·기호·공백 + 위 유니코드 기호
def is_mchar(c):
    return (c.isascii() and c.isprintable()) or c in MSYM or c in ITAL

def has_core(run):
    return any(c.isalnum() or (c in MSYM and c not in '()') for c in run if c.isascii() and c.isalnum() or c in MSYM)

def run_to_math(run):
    """ASCII/기호 문자열 → 수식 원본. 영문자 낱말은 정자."""
    if re.fullmatch(r'\d+-\d+', run):  # 3-1 같은 단원 번호
        a, b = run.split('-'); return a + r'\text{-}' + b
    out = []
    i = 0
    while i < len(run):
        c = run[i]
        if c.isascii() and c.isalpha():
            j = i
            while j < len(run) and run[j].isascii() and run[j].isalpha(): j += 1
            out.append(r'\mathrm{%s}' % run[i:j]); i = j; continue
        if c.isdigit():
            j = i
            while j < len(run) and (run[j].isdigit() or (run[j] == '.' and j + 1 < len(run) and run[j + 1].isdigit())): j += 1
            out.append(run[i:j]); i = j; continue
        if c == ' ':
            out.append(r'\ '); i += 1; continue
        if c in ITAL:
            out.append(ITAL[c]); i += 1; continue
        if c in MSYM:
            out.append(MSYM[c]); i += 1; continue
        if c in '{}':
            out.append('\\' + c); i += 1; continue
        if c in '&#$_^~\\':
            out.append({'&': r'\&', '#': r'\#', '$': r'\$', '_': r'\_', '^': r'\hat{}', '~': r'\sim', '\\': r'\backslash'}[c]); i += 1; continue
        if c == ',':
            out.append(',\\,'); i += 1; continue
        out.append(c); i += 1
    return clean_math(sjoin(out))

def sjoin(parts):
    out = ''
    for p in parts:
        if out and p and re.search(r'\\[a-zA-Z]+$', out) and re.match(r'[a-zA-Z0-9]', p):
            out += ' '
        out += p
    return out

def clean_math(s):
    # 연산자 둘레의 강제 공백 제거(연산자 간격은 TeX 가 넣는다)
    ops = r'(\+|-|=|<|>|\\times|\\cdot|\\rightarrow|\\rightleftarrows|\\approx|\\le|\\ge|\\pm|\\sim)'
    s = re.sub(r'(?:\\ )+' + ops, r'\1', s)
    s = re.sub(ops + r'(?:\\ )+', r'\1 ', s)
    s = re.sub(r',\\,(?:\\ )+', ',\\,', s)
    return s

# ---------------- MathML ----------------
MO = {'−': '-', '×': r'\times', '·': r'\cdot', '⋅': r'\cdot', '→': r'\rightarrow', '⇄': r'\rightleftarrows', '≈': r'\approx',
      '≤': r'\le', '≥': r'\ge', '±': r'\pm', '∴': r'\therefore', '…': r'\cdots', '%': r'\%', '{': r'\{', '}': r'\}', '∼': r'\sim',
      '∝': r'\propto', '°': r'^{\circ}', '′': "'", '|': '|'}

def mml(n):
    if isinstance(n, NavigableString):
        return ''
    t = n.name
    kids = [k for k in n.children if isinstance(k, Tag)]
    if t in ('math', 'mrow', 'mstyle', 'semantics'):
        return sjoin(mml(k) for k in kids)
    if t == 'mi':
        s = n.get_text()
        if s == 'Δ': return r'\Delta '
        if len(s) == 1 and s.isascii() and n.get('mathvariant') != 'normal':
            return s
        if s in ITAL: return ITAL[s]
        if s.isascii(): return r'\mathrm{%s}' % s
        return '{' + run_to_math(s) + '}' if all(is_mchar(c) for c in s) else r'\text{%s}' % tesc(s)
    if t == 'mn':
        return n.get_text()
    if t == 'mo':
        s = n.get_text().strip()
        return MO.get(s, s if s.isascii() else run_to_math(s))
    if t == 'mtext':
        s = n.get_text().replace('\u2009', ' ').replace('\u00a0', ' ')
        if not s.strip(): return r'\ '
        if all(is_mchar(c) for c in s) and s.strip():
            return run_to_math(s)
        return r'\text{%s}' % tesc(s)
    if t == 'msub':
        return '{%s}_{%s}' % (mml(kids[0]), mml(kids[1]))
    if t == 'msup':
        return '{%s}^{%s}' % (mml(kids[0]), mml(kids[1]))
    if t == 'msubsup':
        return '{%s}_{%s}^{%s}' % (mml(kids[0]), mml(kids[1]), mml(kids[2]))
    if t == 'mfrac':
        return r'\dfrac{%s}{%s}' % (mml(kids[0]), mml(kids[1]))
    if t == 'msqrt':
        return r'\sqrt{%s}' % ''.join(mml(k) for k in kids)
    raise ValueError('MathML 태그 미지원: ' + t)

# ---------------- 인라인 ----------------
# 토큰: ('t', 원본 TeX 글) / ('m', 수식) / ('s', 아래·위 첨자 수식) / ('w', 공백)

MRUN = r"[A-Za-z0-9+\-=<>/.,%:;!?'\[\]−×·⋅→⇄≈∴℃°Δ≤≥±∼✓𝑎𝑔𝑙𝑞𝑠]"
CORE = re.compile(r"[A-Za-z0-9−×·⋅→⇄≈∴℃°Δ≤≥±∼✓𝑎𝑔𝑙𝑞𝑠+=<>]")

def text_tokens(s):
    toks = []
    pat = re.compile(r'([^\S　]+)|([()])|(%s+(?: %s+)*)|(.)' % (MRUN, MRUN), re.S)
    prev_char = ''
    for m in pat.finditer(s):
        if m.group(1) is not None:
            toks.append(('w', ' '))
        elif m.group(2) is not None:
            toks.append(('p', m.group(2)))
        elif m.group(3) is not None:
            run = m.group(3)
            lead = re.match(r"^[.,;:!?' ]*", run).group(0)
            if run[len(lead):].startswith('-') and prev_char and not prev_char.isspace() and prev_char not in '()':
                lead += '-'
            tail = re.search(r"[.,;:!?' ]*$", run[len(lead):]).group(0)
            body = run[len(lead):len(run) - len(tail)]
            if lead.strip(): toks.append(('t', tesc(lead.strip())))
            if lead.endswith(' '): toks.append(('w', ' '))
            if body:
                if CORE.search(body):
                    # 「(2) × (3)」처럼 홀로 쓴 ×(틀림 표시)는 연산자가 아니다
                    if body == '×': toks.append(('m', r'{\times}'))
                    else: toks.append(('m', run_to_math(body)))
                else:
                    toks.append(('t', tesc(body)))
            if tail.startswith(' ') and not tail.strip(): toks.append(('w', ' '))
            elif tail:
                if tail.startswith(' '): toks.append(('w', ' '))
                toks.append(('t', tesc(tail.strip())))
                if tail.endswith(' '): toks.append(('w', ' '))
        else:
            c = m.group(4)
            toks.append(('t', tesc(c) if c != '　' else '　'))
        prev_char = m.group(0)[-1:]
    return toks

def inline_tokens(node):
    toks = []
    for k in node.children:
        if isinstance(k, NavigableString):
            toks += text_tokens(str(k)); continue
        t = k.name
        cls = k.get('class') or []
        if t == 'math':
            toks.append(('m', mml(k)))
        elif t in ('sub', 'sup'):
            inner = ''.join(v for kind, v in inline_tokens(k) if kind in ('m', 't', 's'))
            s = k.get_text()
            body = run_to_math(s) if all(is_mchar(c) for c in s) else r'\text{%s}' % tesc(s)
            toks.append(('s', ('_{%s}' if t == 'sub' else '^{%s}') % body))
        elif t == 'span' and 'mx' in cls:
            s = k.get_text()
            toks.append(('m', ''.join(ITAL.get(c, c) for c in s)))
        elif t == 'u':
            toks.append(('t', r'\underline{%s}' % join_tokens(inline_tokens(k))))
        elif t == 'b':
            toks.append(('t', r'{\bfseries %s}' % join_tokens(inline_tokens(k))))
        elif t == 'small':
            toks.append(('t', r'{\fontsize{7.2}{12}\selectfont %s}' % join_tokens(inline_tokens(k))))
        elif t == 'br':
            toks.append(('t', r'\newline '))
        elif t in ('span', 'em', 'i', 'strong'):
            toks += inline_tokens(k)
        elif t == 'img':
            toks.append(('t', img_tex(k, inline=True)))
        else:
            raise ValueError('인라인 태그 미지원: %s %s' % (t, cls))
    return toks

def _is_m(t):
    return t is not None and t[0] in ('m', 's')

def join_tokens(toks):
    n = len(toks)
    # 괄호: 바로 옆(공백 건너) 토큰이 수식이면 수식으로
    def nb(i, d):
        j = i + d
        while 0 <= j < n and toks[j][0] == 'w': j += d
        return toks[j] if 0 <= j < n else None
    kinds = []
    for i, (k, v) in enumerate(toks):
        if k == 'p':
            a, b = nb(i, -1), nb(i, 1)
            if v == '(' and (_is_m(b) or (b and b[0] == 'p' and _is_m(nb(i + 1, 1)))): k = 'm'
            elif v == ')' and (_is_m(a) or (a and a[0] == 'p' and _is_m(nb(i - 1, -1)))): k = 'm'
            else: k = 't'
        kinds.append(k)
    out = []
    i = 0
    while i < n:
        k, v = kinds[i], toks[i][1]
        if k in ('m', 's'):
            grp = []
            j = i
            while j < n:
                kj, vj = kinds[j], toks[j][1]
                if kj in ('m', 's'):
                    if kj == 's' and not grp: grp.append('{}')
                    if grp and re.search(r'\\[a-zA-Z]+$', grp[-1]) and re.match(r'[a-zA-Z0-9]', vj): grp.append(' ')
                    grp.append(vj); j += 1; continue
                if kj == 'w' and j + 1 < n and kinds[j + 1] in ('m', 's'):
                    grp.append(r'\ '); j += 1; continue
                break
            pre, post = '', ''
            # 짝 없는 바깥 괄호는 글로
            while grp and grp[0] in ('(', r'\ '):
                body = ''.join(grp)
                if grp[0] == r'\ ': grp.pop(0); continue
                if body.count('(') > body.count(')'): pre += '('; grp.pop(0); continue
                break
            while grp and grp[-1] in (')', r'\ '):
                body = ''.join(grp)
                if grp[-1] == r'\ ': grp.pop(); continue
                if body.count(')') > body.count('('): post = ')' + post; grp.pop(); continue
                break
            m = clean_math(''.join(grp))
            if re.fullmatch(r'\((\d+)\)', m):
                out.append(pre + m + post)
            elif m:
                out.append(pre + '$%s$' % m + post)
            else:
                out.append(pre + post)
            i = j
            continue
        out.append(' ' if k == 'w' else v)
        i += 1
    s = ''.join(out)
    s = re.sub(r' {2,}', ' ', s)
    return s.strip()

def inl(node):
    return join_tokens(inline_tokens(node))

# ---------------- 블록 ----------------
FIGDIR = 'fig/hw/'

def img_tex(img, inline=False, frac=None):
    src = img['src']
    name = src.split('/')[-1]
    m = re.search(r'width:\s*([\d.]+)%', img.get('style', ''))
    w = float(m.group(1)) / 100 if m else 0.6
    if frac: w = frac
    return r'\includegraphics[width=%.3f\linewidth]{%s}' % (min(w, 1.0), name)

ITEM = re.compile(r'^\s*(\(\d+\)|\([가-하]\)|[①-⑤]|[ㄱ-ㅎ]\.)\s*')

def para(p):
    s = inl(p)
    m = ITEM.match(s)
    if m and not s.startswith('$'):
        lab = m.group(1)
        return r'\qitem{%s}{%s}' % (lab, s[m.end():])
    # 수식으로 바뀐 (1) 같은 번호
    m2 = re.match(r'^\$\((\d+)\)\$\s*', s)
    if m2:
        return r'\qitem{(%s)}{%s}' % (m2.group(1), s[m2.end():])
    return s + r'\par'

def opts_macro(items, cls):
    # 대략의 폭(한글 1, 그 밖 0.55, 쉼표·공백 0.4)
    def w(x):
        x = re.sub(r'\\(mathrm|text)\{([^}]*)\}', r'\2', x)
        x = re.sub(r'\\[a-zA-Z]+|[\$\{\}_^]', '', x)
        return sum(1.0 if ord(c) > 0x2E80 else (0.4 if c in ', ' else 0.55) for c in x)
    mx = max(w(x) for x in items)
    if 'v' in cls: return 'examoptsvertical'
    if 'w2' in cls: return 'examoptstwo'
    if mx <= 4.0: return 'examoptsfive'
    if mx <= 8.5: return 'examoptstwo'
    return 'examoptsvertical'

def table_tex(tb):
    rows = tb.find_all('tr')
    grid = []
    for r in rows:
        cells = r.find_all(['th', 'td'])
        grid.append([(c.name, inl(c)) for c in cells])
    ncol = max(len(r) for r in grid)
    head = all(k == 'th' for k, _ in grid[0])
    rowhead = all(r[0][0] == 'th' for r in grid[1:]) if len(grid) > 1 else False
    spec = 'c|' + 'c' * (ncol - 1)
    lines = [r'\hline']
    for i, r in enumerate(grid):
        cells = [v for _, v in r] + [''] * (ncol - len(r))
        lines.append(' & '.join(cells) + r' \\')
        if i == 0 and head and len(grid) > 1: lines.append(r'\hline')
    lines.append(r'\hline')
    return (r'\par\vspace{2.2mm}\nointerlineskip\begingroup\centering\fontsize{8.2}{12}\selectfont\renewcommand{\arraystretch}{1.45}'
            r'\setbox0\hbox{\begin{tabular}{%s}%s\end{tabular}}\ifdim\wd0>\linewidth\resizebox{\linewidth}{!}{\box0}\else\box0\fi\par\endgroup\vspace{1.6mm}' % (spec, '\n'.join(lines)))

def block_tex(n):
    """div.qs 의 자식들 → TeX"""
    out = []
    for k in n.children:
        if isinstance(k, NavigableString):
            if k.strip(): out.append(inl_str(k))
            continue
        t = k.name
        cls = k.get('class') or []
        if t == 'p':
            out.append(para(k))
        elif t == 'div' and 'hwbox' in cls:
            out.append(r'\pbox{%s}' % r'\par '.join(inner_paras(k)))
        elif t == 'div' and 'bogi' in cls:
            ps = []
            for p in k.find_all('p', recursive=False):
                s = inl(p)
                m = re.match(r'^([ㄱ-ㅎ])\.\s*', s)
                ps.append(r'\bogi{%s}{%s}' % (m.group(1), s[m.end():]) if m else s + r'\par')
            out.append(r'\choices{%s}' % ''.join(ps))
        elif t == 'div' and 'chs' in cls:
            items = [inl(d.find('span')) for d in k.find_all('div', recursive=False)]
            assert len(items) == 5, items
            out.append('\\%s{%s}{%s}{%s}{%s}{%s}' % ((opts_macro(items, cls),) + tuple(items)))
        elif t == 'div' and 'fg' in cls:
            imgs = k.find_all('img')
            out.append(r'\par\vspace{1.6mm}\nointerlineskip{\centering %s\par}\vspace{1.2mm}' % r'\hspace{2mm}'.join(img_tex(i) for i in imgs))
        elif t == 'table':
            out.append(table_tex(k))
        elif t == 'div':
            out.append(block_tex(k))
        else:
            raise ValueError('블록 태그 미지원: %s %s' % (t, cls))
    return '\n'.join(out)

def inl_str(s):
    return join_tokens(text_tokens(str(s)))

def inner_paras(div):
    ps = div.find_all('p', recursive=False)
    if not ps: return [inl(div)]
    return [inl(p) for p in ps]

def question_body(qhtml):
    soup = BeautifulSoup(qhtml, 'html.parser')
    qs = soup.find('div', class_='qs')
    return block_tex(qs)

def solution_parts(ehtml):
    """해설 HTML → (정답 글, 출처, [풀이 단계], 핵심 개념, 다시 공부할 부분)"""
    soup = BeautifulSoup(ehtml, 'html.parser')
    sa = soup.find('span', class_='sa')
    ans = inl(sa)
    ans = re.sub(r'^정답\s*', '', ans)
    ss = soup.find('div', class_='ss')
    src = inl(ss) if ss else ''
    src = re.sub(r'^출처\s*:\s*', '', src)
    steps, core, review, figs = [], '', [], []
    sol = soup.find('div', class_='sol')
    for k in sol.children:
        if not isinstance(k, Tag): continue
        cls = k.get('class') or []
        if k.name == 'p' and 'st' in cls:
            steps.append(inl(k))
        elif k.name == 'p':
            lb = k.find('span', class_='lb')
            lab = lb.get_text() if lb else ''
            if lb: lb.extract()
            body = inl(k)
            if lab == '풀이' and not body: continue
            if lab == '핵심 개념': core = body
            elif lab: steps.append(r'{\bfseries [%s]} %s' % (lab, body))
            elif body: steps.append(body)
        elif k.name == 'div' and 'rv' in cls:
            lb = k.find('span', class_='lb')
            if lb: lb.extract()
            review = [inl(d) for d in k.find_all('div', class_='st')]
        elif k.name == 'div' and 'fg' in cls:
            steps.append(r'{\centering %s\par}' % ''.join(img_tex(i) for i in k.find_all('img')))
        elif k.name == 'table':
            steps.append(table_tex(k))
    return ans, src, steps, core, review
