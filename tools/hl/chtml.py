# -*- coding: utf-8 -*-
"""개념서 HTML 조립 도구.  concept_*.py 가 이 함수들로 절 본문을 만든다.

본문 안의 간단한 표시
  **용어**        핵심 용어(노란 형광펜)
  __굵게__        굵은 글씨
  {말|표지}       예문 분석: 말 아래에 작은 글씨로 표지(예: 주어)를 붙인다
  {말|}           표지 없이 말에 밑줄만
  [[정답]]        빈칸 문제로 만들 때 쓰는 표시(여기서는 그냥 굵게)
"""
import re, html as _h


def esc(s):
    return _h.escape(s, quote=False)


def inline(s):
    # 이미 태그가 들어 있는 부분은 그대로 두고, 표시만 바꾼다
    s = re.sub(r'\{([^{}|]+)\|([^{}]*)\}', lambda m: '<span class="an"><u>%s</u>%s</span>' % (m.group(1), ('<i>%s</i>' % m.group(2)) if m.group(2) else ''), s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<span class="hl">\1</span>', s)
    s = re.sub(r'__(.+?)__', r'<b>\1</b>', s)
    s = re.sub(r'\[\[(.+?)\]\]', r'<b>\1</b>', s)
    return s


def P(t):
    return '<p>%s</p>' % inline(t)


def H(t):
    return '<h4>%s</h4>' % inline(t)


def UL(*items):
    """항목 목록. 하위 목록은 (문장, [하위 항목...]) 튜플로 넣는다."""
    out = '<ul class="l">'
    for it in items:
        if isinstance(it, tuple):
            out += '<li>%s%s</li>' % (inline(it[0]), UL(*it[1]))
        else:
            out += '<li>%s</li>' % inline(it)
    return out + '</ul>'


def OL(*items):
    return '<ol class="n">' + ''.join('<li>%s</li>' % inline(i) for i in items) + '</ol>'


def EX(*sentences, note=None, label=None):
    """예문 상자. 필기하기 좋게 줄 간격이 넓다."""
    out = '<div class="ex">'
    if label:
        out += '<span class="elb">%s</span>' % inline(label)
    for s in sentences:
        out += '<p class="s">%s</p>' % inline(s)
    if note:
        out += '<p class="n">%s</p>' % inline(note)
    return out + '</div>'


def TB(head, rows, cls='tb', left=()):
    """head: 머리 칸 목록, rows: 줄 목록(칸 목록).  칸 앞에 '~' 를 붙이면 굵게, '<' 를 붙이면 왼쪽 정렬.
    left: 왼쪽 정렬할 열 번호."""
    t = '<table class="%s"><thead><tr>%s</tr></thead><tbody>' % (cls, ''.join('<th>%s</th>' % inline(h) for h in head))
    for r in rows:
        t += '<tr>'
        for j, c in enumerate(r):
            k = ''
            if c.startswith('~'): k, c = 'b', c[1:]
            elif c.startswith('<'): k, c = 'l', c[1:]
            if j in left and not k: k = 'l'
            t += '<td%s>%s</td>' % (' class="%s"' % k if k else '', inline(c))
        t += '</tr>'
    return t + '</tbody></table>'


def NT(label, *body, kind=''):
    """상자.  kind: ''(핵심 정리) / 'wa'(혼동 주의) / 'ds'(기출 포인트) / 'es'(원리 더하기·쉽게 말해)"""
    inner = ''.join(b if b.startswith('<') else P(b) for b in body)
    return '<div class="nt%s"><span class="lb">%s</span>%s</div>' % (' ' + kind if kind else '', esc(label), inner)


def EASY(*body):
    return NT('쉽게 말해', *body, kind='es')


def WARN(*body):
    return NT('혼동 주의', *body, kind='wa')


def KEY(*body):
    return NT('핵심 정리', *body)


def PT(*body):
    return NT('시험에는 이렇게 나온다', *body, kind='ds')


def WHY(*body):
    return NT('왜 배울까요?', *body, kind='es')


def STEP(*steps):
    """풀이 순서(번호 목록)"""
    return '<ol class="st">' + ''.join('<li>%s</li>' % inline(s) for s in steps) + '</ol>'


def SEC(*parts):
    return ''.join(parts)
