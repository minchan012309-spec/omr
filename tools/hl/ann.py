# -*- coding: utf-8 -*-
"""주석 문장 도구. 문장 안의 {글자|코드} 표시를 읽어 낱말 단위(분절)로 다룬다.
   예: '{철수가|주} {책을|목} {읽었다|서}'   코드는 'role' 또는 'role:detail'."""
import re
from hllib import esc

_RE = re.compile(r'\{([^{}|]+)\|([^{}]+)\}')

class Ann:
    def __init__(self, s, **meta):
        self.s = s
        self.meta = meta
        self.toks = []   # ('t', text) / ('s', text, code)
        pos = 0
        for m in _RE.finditer(s):
            if m.start() > pos: self.toks.append(('t', s[pos:m.start()]))
            self.toks.append(('s', m.group(1), m.group(2)))
            pos = m.end()
        if pos < len(s): self.toks.append(('t', s[pos:]))
    @property
    def segs(self):
        return [(i, t[1], t[2]) for i, t in enumerate(self.toks) if t[0] == 's']
    def codes(self):
        return [c for _, _, c in self.segs]
    def role(self, code): return code.split(':')[0]
    def detail(self, code): return code.split(':')[1] if ':' in code else ''
    def plain(self):
        return ''.join(t[1] for t in self.toks)
    def html(self, under=None, labels=None):
        """under: 밑줄 칠 분절 인덱스(toks 내 위치)들, labels: {인덱스: '㉠'}"""
        under = set(under or []); labels = labels or {}
        out = []
        for i, t in enumerate(self.toks):
            txt = esc(t[1])
            if t[0] == 's' and i in under:
                lab = labels.get(i, '')
                out.append('%s<u>%s</u>' % (lab, txt))
            else:
                out.append(txt)
        return ''.join(out)
    def seg_by_role(self, roles):
        return [(i, t, c) for i, t, c in self.segs if self.role(c) in roles]

def A(s, **meta):
    return Ann(s, **meta)

def anns(block, **meta):
    out = []
    for ln in block.strip().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        out.append(Ann(ln, **meta))
    return out
