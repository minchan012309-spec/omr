"""Fixed-seed, synthetic 500-student sensitivity analysis for the released bank.

The response curve is a scenario assumption. Signs of improvement quantify the
scenario only; cognitive demand and distractor edits still need human review.
"""
from collections import defaultdict
from math import exp
from pathlib import Path
from random import Random
from statistics import NormalDist, mean
import json

ROOT = Path(__file__).resolve().parents[2] / 'aim'
CUTS = (20,55,115,200,300,385,445,480,500)
EDGES = (0,*CUTS)
LEVELS = {'하':-.85,'중':-.25,'상':.40,'최':1.05}


def responses(items, seed):
    rng=Random(seed)
    abilities=[NormalDist().inv_cdf(1-(i+.5)/500) for i in range(500)]
    d_by_type=defaultdict(list)
    p_by_type=defaultdict(list)
    grades=defaultdict(list)
    for q in items:
        m=q['model'];k=m['problem']
        # Anchors set from number of reasoning steps, not size of the integers.
        hardness=LEVELS[q['lv']]
        generic=sum('분자와 분모의 기준을 다시 확인' in row or '차이가 난다.' in row
                    for row in q['exp'].split('class="aim-choice"')[1:])
        slope=max(.35,1.18-.21*generic)
        correct=[rng.random()<.20+.80/(1+exp(-slope*(ability-hardness))) for ability in abilities]
        # Upper and lower 27%, with rank fixed independently of the responses.
        d_by_type[k].append(mean(correct[:135])-mean(correct[-135:]))
        p_by_type[k].append(mean(correct))
        for grade,(a,b) in enumerate(zip(EDGES,EDGES[1:]),1):
            grades[grade].append(mean(correct[a:b]))
    return {k:(mean(v),mean(p_by_type[k]),sum(d<.20 for d in v)) for k,v in d_by_type.items()}, [mean(v) for v in grades.values()]


def load(root):
    return [q for f in sorted(root.glob('aimr*.json')) for q in json.loads(f.read_text())]


def main():
    from argparse import ArgumentParser
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--seed',type=int,default=50040)
    args=parser.parse_args()
    for label,root in [('수정 전',args.baseline),('현재',ROOT)]:
        if root is None:
            continue
        items=load(root)
        assert len(items)==10_000
        scores,grades=responses(items,args.seed)
        print(label,'평균 변별',round(mean(d for d,p,n in scores.values()),3),
              '0.20 미만 문항',sum(n for d,p,n in scores.values()))
        print('등급별 가상 정답률', ' '.join(f'{g+1}등급 {v:.1%}' for g,v in enumerate(grades)))
        print('평균 변별 하위 유형',', '.join(f'{k:02} {vals[0]:.3f}' for k,vals in sorted(scores.items(),key=lambda row:row[1][0])[:8]))


if __name__=='__main__':
    main()
