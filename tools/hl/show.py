# -*- coding: utf-8 -*-
"""생성된 문항을 터미널에서 읽기 좋게 출력. python3 tools/hl/show.py hl056 [개수] [시작]"""
import sys, re, random
from build import *
load_types()
tag = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
s0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
items, errs = gen_tag(tag, max(n + s0, 12))
def t(h):
    h = re.sub(r'</p>|</div>|<br/?>', '\n', h)
    h = re.sub(r'<u>(.*?)</u>', r'[\1]', h)
    return re.sub(r'<[^>]+>', '', h).replace('&lt;', '<').replace('&gt;', '>').strip()
for it in items[s0:s0 + n]:
    print('─' * 70, it.lv, it.fam)
    print(t(it.body))
    for i, o in enumerate(it.opts): print(' ', '①②③④⑤'[i], t(o))
    print('  정답', it.ans)
    for s in it.steps[:6]: print('   ·', t(s))
print('len', len(items), dict(errs))
