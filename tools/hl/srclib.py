# -*- coding: utf-8 -*-
"""교재 문항(자료에서 가져온 문항) 조립 도구.
src_*.py 파일이 ITEMS 목록에 문항을 넣고, make_hl.py 가 render_src 로 data.json 항목을 만든다.

문항 사전 필드
  code    'H26-001'  (고유 번호)
  sub     'Ⅰ-A' …
  type    유형 이름(outline 의 base 이름)  — 유형 라벨은 '(수능형)' 처럼 뒤에 붙는다
  lv      '하' '중' '상' '최'
  src     출처 표시. 예 '2026학년도 화법과 언어 모의고사 1번'
  grp     같은 지문을 공유하는 문항 묶음 이름 (선택)
  passage 지문 HTML (선택). 같은 grp 의 문항마다 지문이 들어가고, 교재 쪽 나누기에서는 처음 한 번만 찍는다
  body    문제 줄글 HTML
  opts    선택지 5개(텍스트)
  ans     정답 번호 1~5
  exp     풀이 HTML 조각 목록(문장)
"""
import re
from hllib import CIR, esc, plain, josa
from outline import BYLABEL, SUBS


def render_src(d, no, pts=3):
    code = d['code']
    qid = 'q-' + re.sub(r'[^A-Za-z0-9]', '', code)
    sid = 's-' + re.sub(r'[^A-Za-z0-9]', '', code)
    opts = d['opts']
    longest = max(len(plain(o)) for o in opts)
    v = d.get('vertical')
    if v is None:
        v = longest > 17
    chs = '<div class="chs%s">' % (' v' if v else '') + ''.join('<div><b>%s</b><span>%s</span></div>' % (CIR[i], o) for i, o in enumerate(opts)) + '</div>'
    psg = ''
    if d.get('passage'):
        psg = '<div class="psg sp" data-g="%s">%s</div>' % (esc(d.get('grp', code)), d['passage'])
    q = '<div class="q" id="%s"><div class="qh"><b class="qn">%d</b><span class="qp">[%d점]</span></div><div class="qs">%s%s%s</div></div>' % (qid, no, pts, psg, d['body'], chs)
    secs = SUBS[d['sub']]['secs']
    ty = BYLABEL.get(d['type'])
    rl = d.get('ref') or ([ty['sec']] if ty else [1])
    refs = '<div class="rv"><span class="lb">이 문제를 틀렸다면 다시 공부할 부분</span>' + ''.join(
        '<div class="st">→ %s <span class="sm">(개념 정리 %s %d)</span></div>' % (esc(secs[n - 1]), d['sub'], n) for n in rl) + '</div>'
    e = '<div class="sol" id="%s"><div class="sh"><span class="sn">%d</span><span class="sa">정답 %s</span><span class="sc2">%s</span></div><div class="ss">출처 : %s</div><p><span class="lb">풀이</span></p>' % (sid, no, CIR[d['ans'] - 1], code, esc(d['src']))
    e += ''.join('<p class="st">%s</p>' % s for s in d['exp'])
    if d.get('core'):
        e += '<p><span class="lb">핵심 개념</span> %s</p>' % d['core']
    e += refs + '</div>'
    return josa(q), josa(e)


# ---- 작은 HTML 도우미
def p(t):
    return '<p>%s</p>' % t


def bogi(lines, title='보 기'):
    return '<div class="bogi"><div class="bt">%s</div>%s</div>' % (esc(title), ''.join('<p>%s</p>' % l for l in lines))


def box(lines, title=None):
    return '<div class="bogi">%s%s</div>' % (('<div class="bt">%s</div>' % esc(title)) if title else '', ''.join('<p>%s</p>' % l for l in lines))


def dlg(turns):
    return '<div class="bogi dl">' + ''.join('<p><b>%s</b> : %s</p>' % (sp, t) for sp, t in turns) + '</div>'


def tbl(head, rows):
    t = '<table class="tb"><thead><tr>' + ''.join('<th>%s</th>' % h for h in head) + '</tr></thead><tbody>'
    for r in rows:
        t += '<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>'
    return t + '</tbody></table>'


def u(t):
    return '<u>%s</u>' % t
