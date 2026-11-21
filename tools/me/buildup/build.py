# -*- coding: utf-8 -*-
"""2026학년도 2학기 해원고 물질과 에너지 기말고사 빌드업 문항 모음 (XeLaTeX)

문제은행(bank/hw*.json)의 해원고 부교재 원본 148문항(153~300번)을 1~148번으로 다시 매겨
「미적분 I 서바이벌 모의평가」 양식(표지 → 문제 → 뒷면 → 빠른 정답 → 정답 및 해설)으로 만든다.

  python3 tools/me/buildup/build.py --fonts <글꼴 폴더> --out <출력 폴더>

글꼴 폴더에 ShinMyeongjo.ttf, KoPubWorldBold.ttf, KoPubDotumMedium.ttf, HYHWPEQ.ttf,
latinmodern-math.otf 가 있어야 한다(latinmodern-math.otf 는 lib/latex/ 에 있음).
"""
import argparse, glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
import conv  # noqa: E402

PRESET = json.load(open(os.path.join(ROOT, 'presets', 'me-haewon-buildup.json'), encoding='utf-8'))
WSID = PRESET['id']
TITLE = PRESET['title']
SUBJ = '물질과 에너지'
QR_URL = "https://solvi.win/#ws=" + WSID
QR_TEX = QR_URL.replace("#", r"\#")
FMT_NO = WSID[:4] + '-' + WSID[4:]
PHRASE = PRESET['phrase']
ORG = '한국시험잘보고싶음협회'
UNITS = {'Ⅲ': 'Ⅲ. 화학 변화의 자발성', 'Ⅳ': 'Ⅳ. 반응 속도'}
MAXPER = 2
H1, H2 = 198.0, 232.0     # 1쪽 / 2쪽부터 단 높이(mm)
GMIN = 30.0               # 같은 단 두 문항 사이 최소 풀이 공간(mm)


def load():
    byc = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'bank', 'hw*.json'))):
        for x in json.load(open(f, encoding='utf-8')):
            byc[x['code']] = x
    items = [byc[c] for c in PRESET['codes']]
    assert len(items) == 148 and all(x.get('hw') == 'o' for x in items)
    return items


def unit_label(x):
    big = x['sub'].split('-')[0]
    no = '%02d' % ('ABC'.index(x['sub'].split('-')[1]) + 1)
    return '%s \\quad %s. %s' % (UNITS[big], no, x['subname'])


def block(n, x, label=''):
    s = ''
    if label:
        s += r'\unitbox{%s}' % label
    s += (r'\noindent{\bfseries\fontsize{11.5}{14}\selectfont %d.}\hfill{\fontsize{7.6}{10}\selectfont %s}\par\vspace{2.0mm}' % (n, x['code']))
    body = conv.question_body(x['q'])
    big = r'\dfrac' in body
    s += (r'\begingroup\lineskiplimit=0pt\lineskip=2.4pt\fontsize{8.5}{%s}\selectfont\RaggedRight ' % ('19.5' if big else '16.2')) + body + r'\par\endgroup'
    return s


def titlebox(w, size='12.5', lead='17.5'):
    t = TITLE
    f = r'\KoBold\fontsize{%s}{%s}\selectfont %s' % (size, lead, t)
    return r'\settowidth{\tmpw}{%s}\ifdim\tmpw>%s\scalebox{\fpeval{%s/\tmpw}}[1]{%s}\else{%s}\fi' % (f, w, w, f, f)


def head1(total):
    return (r'\par\vspace*{4.4mm}\noindent\makebox[\linewidth][c]{' + titlebox(r'150mm') + r'}\par\vspace{6.1mm}'
            r'\noindent\makebox[29mm][l]{\tikz[baseline=(k.base)]\node[draw,line width=.55pt,ellipse,inner xsep=7.5pt,inner ysep=3.1pt,font=\KoBold\fontsize{10.5}{13}\selectfont](k){빌드업};}'
            r'\makebox[\dimexpr\linewidth-58mm\relax][c]{\KoBold\fontsize{22}{27}\selectfont %s}\makebox[29mm][r]{\KoBold\fontsize{21}{25}\selectfont 1}\par\vspace{5mm}\hrule height .9pt\par\vspace{4.8mm}' % SUBJ +
            r'{\fontsize{9.8}{15}\selectfont 학번 \rule{25mm}{.4pt}\qquad 이름 \rule{28mm}{.4pt}\hfill 맞힌 개수 \rule{13mm}{.4pt} / %d}\par\vspace{4.4mm}' % total + '\n')


def headk(pg):
    return (r'\noindent\makebox[29mm][l]{\KoBold\fontsize{10.4}{13}\selectfont 문항 모음}\makebox[\dimexpr\linewidth-58mm\relax][c]{\KoBold\fontsize{13.7}{17}\selectfont %s}'
            r'\makebox[29mm][r]{\KoBold\fontsize{16}{19}\selectfont %d}\par\vspace{2.0mm}\hrule height .68pt\par\vspace{5.2mm}' % (SUBJ, pg) + '\n')


def shipout(P, B):
    """문제 쪽: 가운데 세로줄 · 쪽 번호 상자 · QR(1쪽 위, 2쪽부터 아래 + 학습지 번호). 해설 쪽: 쪽 번호."""
    qr_top = (r'\node[anchor=north east,inner sep=0pt]at([xshift=-13mm,yshift=-7mm]current page.north east){\qrcode[height=15mm,level=M]{%s}};'
              r'\node[anchor=north east,inner sep=0pt,font=\fontsize{6.6}{8}\selectfont]at([xshift=-13mm,yshift=-22.8mm]current page.north east){%s};' % (QR_TEX, FMT_NO))
    qr_bot = (r'\node[anchor=south east,inner sep=0pt]at([xshift=-13mm,yshift=5mm]current page.south east){\qrcode[height=14mm,level=M]{%s}};'
              r'\node[anchor=south east,inner sep=0pt,align=right,font=\fontsize{7.4}{10}\selectfont]at([xshift=-29.5mm,yshift=5.4mm]current page.south east){학습지 번호\\{\bfseries %s}};'
              r'\node[anchor=south west,inner sep=0pt,align=left,font=\fontsize{7}{9.6}\selectfont,text=black!70]at([xshift=13mm,yshift=5.4mm]current page.south west){QR을 찍거나 학습지 번호를 입력하면\\Solvi에서 바로 채점할 수 있습니다.};' % (QR_TEX, FMT_NO))
    return (r'\AddToShipoutPictureBG{\ifnum\value{page}>0\relax\ifnum\value{page}<%d\relax' % (P + 1) +
            r'\begin{tikzpicture}[remember picture,overlay]'
            r'\ifnum\value{page}=1\draw[black!75,line width=.4pt]([yshift=-66mm]current page.north)--([yshift=24mm]current page.south);' + qr_top +
            r'\else\draw[black!75,line width=.4pt]([yshift=-31mm]current page.north)--([yshift=24mm]current page.south);' + qr_bot + r'\fi'
            r'\node[draw,line width=.45pt,minimum width=19mm,minimum height=6.4mm,inner sep=0pt,font=\fontsize{9.5}{11}\selectfont\bfseries,text height=1.9ex,text depth=0pt]at([yshift=11.5mm]current page.south){\thepage\ / %d};' % P +
            r'\end{tikzpicture}\else\ifnum\value{page}>%d\relax\begin{tikzpicture}[remember picture,overlay]\node[font=\fontsize{9.5}{11}\selectfont\bfseries]at([yshift=9mm]current page.south){\thepage};\end{tikzpicture}\fi\fi\fi}' % (P + 1 + B) + '\n')


def measure(work, pre, blocks):
    body = pre + r'\begin{document}' + '\n'
    for i, b in enumerate(blocks):
        body += r'\sbox0{\begin{minipage}[t]{.475\textwidth}' + b + r'\end{minipage}}\typeout{HT:%d:\the\dimexpr\ht0+\dp0\relax}' % i + '\n'
    body += r'\end{document}'
    open(os.path.join(work, 'measure.tex'), 'w', encoding='utf-8').write(body)
    r = subprocess.run(['xelatex', '-interaction=nonstopmode', 'measure.tex'], cwd=work, capture_output=True, text=True, errors='replace')
    hs = {int(m[1]): float(m[2]) * 0.3514598 for m in re.finditer(r'HT:(\d+):([\d.]+)pt', r.stdout)}
    if len(hs) != len(blocks):
        print(r.stdout[-3000:]); raise SystemExit('measure fail %d/%d' % (len(hs), len(blocks)))
    errs = [l for l in r.stdout.split('\n') if l.startswith('!')]
    if errs: print('measure errors', errs[:5])
    return [hs[i] for i in range(len(blocks))]


def pack(hs):
    cols = []; cur = []; cs = 0.0; st = {'page': 1, 'ci': 0}
    cap = lambda page: H1 if page == 1 else H2
    def flush():
        nonlocal cur, cs
        if not cur: return
        cols.append((st['page'], cur)); st['ci'] += 1
        if st['ci'] % 2 == 0: st['page'] += 1
        cur = []; cs = 0.0
    for i, h in enumerate(hs):
        if h > cap(st['page']) + 1e-6 and st['page'] == 1 and not cur:
            print('경고: %d번 문항이 1쪽 단보다 깁니다(%.1fmm)' % (i + 1, h))
        need = h + (GMIN if cur else 0)
        if cur and (len(cur) >= MAXPER or cs + need > cap(st['page']) + 1e-6):
            flush(); need = h
        cur.append(i); cs += need
    flush()
    return cols


def probpages(blocks, hs, total):
    cols = pack(hs); pages = max(p for p, _ in cols); parts = []
    for pg in range(1, pages + 1):
        H = H1 if pg == 1 else H2
        cc = [c for p, c in cols if p == pg]
        s = head1(total) if pg == 1 else headk(pg)
        mcs = []
        for c in cc:
            tot = sum(hs[i] for i in c); left = H - tot; gap = min(max(left / len(c), 8.0), 150.0)
            body = ''.join(blocks[i] + r'\par\vspace{%.2fmm}' % gap for i in c)
            mcs.append(r'\begin{minipage}[t][%.1fmm][t]{.475\textwidth}\vspace{0pt}%s\par\vfill\end{minipage}' % (H, body))
        if len(mcs) == 1:
            mcs.append(r'\begin{minipage}[t][%.1fmm][t]{.475\textwidth}\vspace{0pt}\mbox{}\end{minipage}' % H)
        s += r'\hfill '.join(mcs) + r'\par\clearpage' + '\n'
        parts.append(s)
    return pages, '\n'.join(parts), cols


def cover_tex(npages):
    PX = 0.297
    X = lambda px: '%.2f' % (px * PX)
    L = []; a = L.append
    a(r'\clearpage\thispagestyle{empty}')
    a(r'\begin{tikzpicture}[remember picture,overlay,x=1mm,y=-1mm,shift={(current page.north west)}]')
    a(r'\node[anchor=center] at (105,%.2f){%s};' % (100 * PX, titlebox('172mm', '15', '18')))
    a(r'\node[anchor=center] at (105,%.2f){\KoBold\fontsize{31}{36}\selectfont %s};' % (157 * PX, SUBJ))
    a(r'\draw[line width=.5pt](%s,%s)rectangle(%s,%s);' % (X(123), X(228), X(269), X(259)))
    a(r'\draw[line width=.5pt](%s,%s)--(%s,%s);' % (X(171), X(228), X(171), X(259)))
    a(r'\node[font=\KoMed\fontsize{11.5}{14}\selectfont] at (%s,%s){성명};' % (X(147), X(243.5)))
    a(r'\draw[line width=.5pt](%s,%s)rectangle(%s,%s);' % (X(286), X(228), X(582), X(259)))
    a(r'\draw[line width=.5pt](%s,%s)--(%s,%s);' % (X(369), X(228), X(369), X(259)))
    a(r'\node[font=\KoMed\fontsize{11.5}{14}\selectfont] at (%s,%s){수험 번호};' % (X(327), X(243.5)))
    for x in (391, 414, 437, 486, 510, 533, 556):
        a(r'\draw[dotted,line width=.5pt](%s,%s)--(%s,%s);' % (X(x), X(228), X(x), X(259)))
    a(r'\draw[line width=.5pt](%s,%s)--(%s,%s);' % (X(462), X(228), X(462), X(259)))
    a(r'\draw[line width=.5pt](%s,%s)--(%s,%s);' % (X(462), X(243.5), X(486), X(243.5)))
    a(r'\draw[line width=.5pt](%s,%s)rectangle(%s,%s);' % (X(81), X(278), X(627), X(549)))
    def line(y, txt, x=138, size='10.4'):
        a(r'\node[font=\KoMed\fontsize{%s}{13}\selectfont,anchor=west] at (%s,%s){%s};' % (size, X(x), X(y), txt))
    for y, t in ((302, '문제지의 해당란에 성명과 수험번호를 정확히 쓰시오.'), (330, '답안지의 필적 확인란에 다음의 문구를 정자로 기재하시오.'),
                 (397, '서술형 문항은 답만 쓰지 말고 풀이 과정을 함께 정'), (440, '각 문항 오른쪽 위의 문항 코드로 해설과 같은 유형 문항을 찾을 수 있습니다.'),
                 (469, 'QR을 찍거나 학습지 번호를 입력하면 Solvi에서 바로 채점할 수 있습니다. 학습지'), (517, '계산은 문제지의 여백을 활용하시오.')):
        a(r'\node[anchor=west] at (%s,%s){$\bigcirc$};' % (X(113), X(y))); line(y, t)
    line(418, '확히 쓰시오.'); line(491, '번호는 %s입니다.' % FMT_NO)
    a(r'\draw[line width=.5pt,fill=black!8](%s,%s)rectangle(%s,%s);' % (X(138), X(347), X(535), X(378)))
    a(r'\node[anchor=center,font=\KoMed\fontsize{10.4}{13}\selectfont] at (%s,%s){%s};' % (X(336.5), X(362.5), PHRASE))
    a(r'\draw[line width=.5pt](%s,%s)rectangle(%s,%s);' % (X(81), X(573), X(627), X(811)))
    line(599, '※ 소단원 순서대로 148문항을 이어서 실었습니다. 문제지를 확인하고, 답을 정확히 표시하시오.', x=96, size='9.6')
    a(r'\node[anchor=west] at (%s,%s){\KoMed $\bigcirc$ 문제지};' % (X(113), X(637)))
    a(r'\draw[dotted,line width=.6pt](%s,%s)--(%s,%s);' % (X(217), X(637), X(523), X(637)))
    a(r'\node[anchor=west,font=\KoMed\fontsize{10.4}{13}\selectfont] at (%s,%s){1$\sim$%d쪽};' % (X(532), X(637), npages))
    a(r'\node[anchor=west] at (%s,%s){\KoMed $\bigcirc$ 답안지};' % (X(113), X(675)))
    for y, lab, x0, rng in ((711, '빠른 정답', 147, r'\pageref{lbl:q1}$\sim$\pageref{lbl:q2}쪽'), (746, '정답 및 해설', 139, r'\pageref{lbl:h1}$\sim$\pageref{lbl:h2}쪽')):
        a(r'\node[anchor=west,font=\KoMed\fontsize{10.4}{13}\selectfont] at (%s,%s){%s};' % (X(x0), X(y), lab))
        a(r'\draw[dotted,line width=.6pt](%s,%s)--(%s,%s);' % (X(218), X(y), X(520), X(y)))
        a(r'\node[anchor=west,font=\KoMed\fontsize{10.4}{13}\selectfont] at (%s,%s){%s};' % (X(532), X(y), rng))
    a(r'\node[anchor=west,font=\KoMed\fontsize{9.6}{13}\selectfont,text=black!70] at (%s,%s){문항 수: 148문항 (Ⅲ단원 63 · Ⅳ단원 85)};' % (X(113), X(783)))
    a(r'\draw[line width=.5pt,fill=black!8](%s,%s)rectangle(%s,%s);' % (X(81), X(832), X(627), X(877)))
    a(r'\node[anchor=center,font=\KoMed\fontsize{12.5}{15}\selectfont] at (%s,%s){※ 시험이 시작되기 전까지 표지를 넘기지 마십시오.};' % (X(354), X(854.5)))
    a(r'\node[anchor=center,font=\KoMed\fontsize{19}{23}\selectfont] at (%s,%s){%s};' % (X(354), X(911), ORG))
    a(r'\end{tikzpicture}')
    return '\n'.join(L)


def back_tex():
    return (r'\clearpage\thispagestyle{empty}\begin{tikzpicture}[remember picture,overlay]'
            r'\draw[line width=.5pt,fill=black!8]([xshift=-73mm,yshift=-7.5mm]current page.center)rectangle([xshift=73mm,yshift=7.5mm]current page.center);'
            r'\node[font=\KoMed\fontsize{12.5}{15}\selectfont]at(current page.center){※ 시험이 시작되기 전까지 표지를 넘기지 마십시오.};\end{tikzpicture}\null')


def anshead(title):
    return (r'\noindent\makebox[29mm][l]{\KoBold\fontsize{10.4}{13}\selectfont 문항 모음}\makebox[\dimexpr\linewidth-58mm\relax][c]{\KoBold\fontsize{13.7}{17}\selectfont %s}'
            r'\makebox[29mm][r]{\KoBold\fontsize{10.4}{13}\selectfont %s}\par\vspace{2.0mm}\hrule height .68pt\par\vspace{4.5mm}' % (title, SUBJ) + '\n')


CIRC = {'①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5}

def circ_tex(s, big=False):
    return re.sub('[①②③④⑤]', lambda m: (r'\circhL{%d}' if big else r'\circh{%d}') % CIRC[m.group(0)], s)


def quick_tex(items, sols):
    s = anshead('빠른 정답') + r'\label{lbl:q1}'
    s += (r'\setlength{\columnseprule}{.4pt}\setlength{\columnsep}{9mm}\begin{multicols}{2}\fontsize{8.5}{14}\selectfont\RaggedRight\setlength{\parskip}{1.6mm}' + '\n')
    prev = None
    for k, (x, sol) in enumerate(zip(items, sols)):
        if x['sub'] != prev:
            s += r'\par\vspace{1.2mm}{\KoBold\fontsize{8.6}{12}\selectfont %s}\par\vspace{.6mm}' % unit_label(x).replace(r'\quad', '·')
            prev = x['sub']
        a_tex = circ_tex(sol[0]) if re.fullmatch(r'[①②③④⑤,\s]+', sol[0]) else sol[0]
        s += r'\par\noindent\hangindent=8mm\hangafter=1\makebox[8mm][l]{\bfseries %d.}%s' % (k + 1, a_tex)
    s += r'\label{lbl:q2}\end{multicols}\clearpage' + '\n'
    return s


def sol_tex(items, sols):
    s = anshead('정답 및 해설') + (r'\setlength{\columnseprule}{.4pt}\setlength{\columnsep}{9mm}\begin{multicols}{2}\label{lbl:h1}\relpenalty=300 \binoppenalty=500 '
                               r'\fontsize{8.5}{15}\selectfont\RaggedRight\setlength{\parskip}{1.1mm}' + '\n')
    for k, (x, (ans, src, steps, core, review)) in enumerate(zip(items, sols)):
        st = ''.join(r'\par\noindent %s' % t for t in steps)
        a_tex = circ_tex(ans) if re.fullmatch(r'[①②③④⑤,\s]+', ans) else ans
        plain = re.sub(r'\\[a-zA-Z]+|[\$\{\}_^]', '', ans)
        if len(plain) <= 26:
            s += r'\par\noindent{\bfseries\fontsize{10.5}{14}\selectfont %d.}\quad 정답 \ansbox{%s}\par' % (k + 1, a_tex)
        else:
            s += (r'\par\noindent{\bfseries\fontsize{10.5}{14}\selectfont %d.}\quad 정답\par\noindent\colorbox{black!16}{\parbox{\dimexpr\linewidth-2\fboxsep\relax}{\RaggedRight\bfseries %s}}\par' % (k + 1, a_tex))
        s += r'{\fontsize{7.6}{11.5}\selectfont\RaggedRight 출처: %s\hfill %s}\par\vspace{.6mm}' % (src, x['code'])
        if core:
            s += r'\noindent{\bfseries [핵심 개념]} %s\par\vspace{.4mm}' % core
        s += r'\noindent{\bfseries [풀이]}%s' % st
        if review:
            s += r'\par\vspace{.4mm}\noindent{\bfseries [다시 공부할 부분]} %s' % '; '.join(r.replace(r'$\rightarrow$ ', '') for r in review)
        s += r'\par\vspace{4.2mm}' + '\n'
    s += r'\label{lbl:h2}\end{multicols}' + '\n'
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fonts', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    fdst = os.path.join(out, 'fonts'); os.makedirs(fdst, exist_ok=True)
    for f in ('ShinMyeongjo.ttf', 'KoPubWorldBold.ttf', 'KoPubDotumMedium.ttf', 'HYHWPEQ.ttf', 'latinmodern-math.otf'):
        src = os.path.join(a.fonts, f)
        if not os.path.exists(src): raise SystemExit('글꼴 없음: ' + src)
        shutil.copy(src, fdst)
    figd = os.path.join(out, 'fig'); os.makedirs(figd, exist_ok=True)
    items = load()
    for x in items:
        for m in re.finditer(r'fig/hw/([\w.]+\.png)', x['q'] + x['exp']):
            shutil.copy(os.path.join(ROOT, 'fig', 'hw', m.group(1)), figd)
    from fontTools.ttLib import TTFont
    cm = TTFont(os.path.join(fdst, 'HYHWPEQ.ttf')).getBestCmap()
    rng = ','.join('"%04X' % k for k in sorted(cm) if not 0xE000 <= k < 0xF900 and not 0x2500 <= k < 0x2580 and k not in (0x203B, 0x2302, 0x2317))
    pre = open(os.path.join(HERE, 'pre.tex'), encoding='utf-8').read().replace('@HYRANGE@', rng).replace('@BOTTOM@', '22')
    blocks = []
    prev = None
    for k, x in enumerate(items):
        lab = unit_label(x) if x['sub'] != prev else ''
        prev = x['sub']
        blocks.append(block(k + 1, x, lab))
    hs = measure(out, pre, blocks)
    P, body, cols = probpages(blocks, hs, len(items))
    B = P % 2
    sols = [conv.solution_parts(x['exp']) for x in items]
    doc = pre + shipout(P, B) + r'\begin{document}\setcounter{page}{0}' + '\n'
    doc += cover_tex(P) + '\n' + r'\clearpage\setcounter{page}{1}' + '\n' + body
    doc += (r'\null\clearpage' + '\n' if B else '') + back_tex() + '\n' + r'\clearpage' + '\n'
    doc += quick_tex(items, sols) + sol_tex(items, sols)
    doc += r'\end{document}'
    fn = 'buildup'
    open(os.path.join(out, fn + '.tex'), 'w', encoding='utf-8').write(doc)
    for _ in range(3):
        r = subprocess.run(['xelatex', '-interaction=nonstopmode', fn + '.tex'], cwd=out, capture_output=True, text=True, errors='replace')
    errs = [l for l in r.stdout.split('\n') if l.startswith('!')]
    miss = sorted(set(re.findall(r'Missing character: There is no (.) ', open(os.path.join(out, fn + '.log'), encoding='utf-8', errors='replace').read())))
    pages = {pg: [i + 1 for p, c in cols if p == pg for i in c] for pg in range(1, P + 1)}
    json.dump({'problem_pages': P, 'pages': pages, 'heights': hs}, open(os.path.join(out, 'layout.json'), 'w'), ensure_ascii=False)
    print('문제 쪽', P, '오류', errs[:5], '없는 글자', miss)


if __name__ == '__main__':
    main()
