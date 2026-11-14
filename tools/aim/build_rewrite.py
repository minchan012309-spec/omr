"""Build the replacement bank under new codes so old answer records remain valid."""
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import random
import re

from explain import math
from rewrite_models import TYPES, solve

ROOT = Path(__file__).resolve().parents[2] / 'aim'
LEVELS = ('하','중','상','최')
N = 250


def display(value):
    return math(str(value).replace(' / ','/'))


def model_figure(i, params):
    a,b,c,d,e = params
    if i == 23:
        rows = ((a,b,c),(d,e,a+b),(b+c,c+d,d+e))
        caption = '원본 영상의 픽셀값'
    elif i == 21:
        rows = [tuple(f'{v:010b}') for v in ((a*17+b)%1024,(c*17+d)%1024)]
        caption = '두 영상의 이진 픽셀'
    else:
        return ''
    labels = ['A','B'] if i == 21 else ['1행','2행','3행']
    html = []
    for label, row in zip(labels, rows):
        cells = ''.join(f'<td style="border:1px solid #7e929e;text-align:center;min-width:1.1em">{v}</td>' for v in row)
        html.append(f'<tr><th scope="row">{label}</th>{cells}</tr>')
    return f'<figure class="fg"><table style="margin:auto;border-collapse:collapse"><caption>{caption}</caption><tbody>{"".join(html)}</tbody></table></figure>'


def options(rng, value, alternatives, nonnegative=False):
    seen = {value}
    items = []
    for option, reason in alternatives:
        if option in seen or (nonnegative and not isinstance(option,str) and option<0):
            continue
        seen.add(option)
        items.append((option,reason))
    if isinstance(value,str) and re.fullmatch('[01]{4}',value):
        for item in product('01',repeat=4):
            key=''.join(item)
            if key not in seen:
                seen.add(key)
                items.append((key,'점수와 임계값을 비교한 출력과 일부 자리가 다르다.'))
    if isinstance(value,int):
        for delta in (1,-1,2,-2,3,-3,4,5):
            key=value+delta
            if key in seen or (nonnegative and key<0):
                continue
            seen.add(key)
            items.append((key,f'조건에 맞게 계산한 {value}와 {abs(delta)} 차이가 난다.'))
    if isinstance(value,Fraction):
        for delta in (1,-1,2,-2,3,-3,4,5):
            key=value+Fraction(delta,value.denominator)
            if key in seen or (nonnegative and key<0):
                continue
            seen.add(key)
            items.append((key,f'계산 결과 {value}와 다른 값이다. 분자와 분모의 기준을 다시 확인한다.'))
    if len(items)<4:
        return None
    take=items[:4]+[(value,'위의 계산과 일치하므로 옳다.')]
    rng.shuffle(take)
    return take


def add_rewrite(index, concept):
    used_stems=set()
    for i,(topic,label) in enumerate(TYPES,1):
        tag=f'aimr{i:02}'
        sec=concept['secs'][topic-1]
        sub=sec['sub']
        rng=random.Random(13300+i)
        bank=[]
        for no in range(1,N+1):
            for _ in range(30000):
                params=[rng.randint(1,39) for _ in range(5)]
                mode=rng.randrange(4)
                data=solve(i,params,mode)
                if not data:
                    continue
                stem, value, proof, alternatives=data
                if stem in used_stems:
                    continue
                count_stem = bool(re.search(r'몇 (?:개|명|%)인가|몇 개인가|개수는',stem))
                choices=options(rng,value,alternatives,nonnegative=count_stem)
                if choices:
                    break
            else:
                raise ValueError(f'{label} {no} 생성 한도 초과')
            used_stems.add(stem)
            # Difficulty belongs to the argument, rather than to a larger random integer.
            lv=('최' if i in (5,22,26,29,32,35,38,40) else
                '상' if i in (4,7,9,11,14,15,19,20,21,23,25,27,31,33,34,37) else
                '하' if i in (1,3,8,16,18,24,28,39) else '중')
            code=f'G-{tag}-{no:04}'
            choice_html=''.join(f'<div><b>{s}</b><span>{display(v)}</span></div>'
                               for s,(v,_) in zip('①②③④⑤',choices))
            exp=f'<p>{display(proof)}</p>'+''.join(f'<p class="aim-choice"><b>{s}</b> {display(reason)}</p>'
              for s,(_,reason) in zip('①②③④⑤',choices))
            bank.append(dict(code=code,no=no,set='mc',sub=sub,subname=concept['subs'][sub]['name'],type=label,
                lv=lv,fam=f'{tag}-{mode}',revised=True,ans=str(next(j for j,(v,_) in enumerate(choices,1) if v==value)),
                q=f'<div class="q"><div class="qh"><b class="qn">{no}</b></div><div class="qs">{model_figure(i,params)}<p>{display(stem)}</p><div class="chs">{choice_html}</div></div></div>',
                exp=exp,model={'problem':i,'params':params,'mode':mode}))
        index[tag]=dict(label=label,sub=sub,subname=bank[0]['subname'],sec=topic,set='mc',
            revised=True,n=N,lv=dict(Counter(q['lv'] for q in bank)))
        (ROOT/(tag+'.json')).write_text('[\n'+',\n'.join(json.dumps(q,ensure_ascii=False,separators=(',',':')) for q in bank)+'\n]\n')
