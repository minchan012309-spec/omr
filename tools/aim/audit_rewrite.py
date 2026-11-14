"""Check released stems, exact answers, choice explanations and type counts."""
import json
import re
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from build_rewrite import TYPES, display, options
from random import Random
from rewrite_models import solve
from independent_rewrite import independent

ROOT = Path(__file__).resolve().parents[2] / 'aim'
CHOICES = re.compile(r'<div><b>[①②③④⑤]</b><span>(.*?)</span></div>')


def check_boundaries(k, p, mode, answer):
    """A second calculation for cases with exact bounds or iterative procedures."""
    a,b,c,d,e = p
    if k==4:
        rows = [(x,y,a*x+b*y) for x,y in product((0,1),repeat=2)]
        return answer==sum(all((score>=t)==bool(x and y if mode%2 else x or y) for x,y,score in rows)
                           for t in range(a+b+2))
    if k==18:
        shift=b*3+15
        forward=lambda x:max(0,min(255,x+shift)-shift)
        return answer==(sum(forward(x)==255-shift for x in range(256)) if mode>=2 and 200+a+shift>255 else forward(200+a))
    if k==29:
        m=a%5+1;y1=b+5;y2=y1+m+e%5-2;tol=d%4+1
        return answer==sum(x>=y1-(c%4+1) and abs(x-y1)<=tol and abs(m+x-y2)<=tol for x in range(y1-tol,y1+tol+1))
    if k==34:
        center=a%9+1;kappa=c%4+1
        w=F(center+b%7+2)
        for _ in range(d%4+1):
            w-=F(1,4*kappa)*(2*kappa*(w-center))
        return answer==w
    if k==7:
        possible=[F(a+2+x,a+b+c+6) for x in range(c+2)]
        return answer==(max(possible) if mode%2 else min(possible))
    return True


def audit():
    index = json.loads((ROOT/'index.json').read_text())
    chapters = json.loads((ROOT/'concept.json').read_text())['secs']
    seen_stems = set()
    positions = Counter()
    tags = [t for t,b in index.items() if b.get('revised')]
    assert len(tags)==40
    for i,(topic,label) in enumerate(TYPES,1):
        tag = f'aimr{i:02}'
        meta = index[tag]
        bank = json.loads((ROOT/(tag+'.json')).read_text())
        assert label in chapters[topic-1]['types']
        assert meta['label']==label and meta['sec']==topic and len(bank)==meta['n']==250
        assert dict(Counter(q['lv'] for q in bank))==meta['lv']
        for no,q in enumerate(bank,1):
            assert q['revised'] and q['set']=='mc' and q['type']==label
            assert q['code']==f'G-{tag}-{no:04}'
            model = q['model']
            assert model['problem']==i
            stem, answer, proof, alternatives = solve(i,model['params'],model['mode'])
            assert independent(i,model['params'],model['mode']) == answer,q['code']
            assert check_boundaries(i,model['params'],model['mode'],answer),q['code']
            assert stem not in seen_stems and f'<p>{display(stem)}</p>' in q['q']
            seen_stems.add(stem)
            choices = CHOICES.findall(q['q'])
            key = int(q['ans'])-1
            assert len(choices)==len(set(choices))==5
            assert choices.count(display(answer))==1 and choices[key]==display(answer)
            assert re.findall(r'class="aim-choice"><b>([①②③④⑤])</b>',q['exp'])==list('①②③④⑤')
            assert f'<p>{display(proof)}</p>' in q['exp']
            # Associate each explanation with the displayed option, not just its position.
            count_stem=bool(re.search(r'몇 (?:개|명|%)인가|몇 개인가|개수는',stem))
            valid=dict(options(Random(0),answer,alternatives,nonnegative=count_stem))
            reason_by_choice={display(value):display(reason) for value,reason in valid.items()}
            reasons=re.findall(r'class="aim-choice"><b>[①②③④⑤]</b> (.*?)</p>',q['exp'])
            assert len(reasons)==5 and all(reason_by_choice.get(choice)==reason for choice,reason in zip(choices,reasons)),q['code']
            assert all(n!=0 for n in map(int,re.findall(r'aria-label="[−-]?\d+/(\d+)"',q['q']+q['exp'])))
            positions[key]+=1
    assert len(seen_stems)==10_000
    assert all(1700<=positions[i]<=2300 for i in range(5))
    print('재출제 40유형 × 250문항, 정답·선지·해설 전수 대조 통과')


if __name__=='__main__':
    audit()
