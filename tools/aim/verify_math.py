"""Independently solve generated stems from the displayed figures and rules."""
import re
from fractions import Fraction as F
from itertools import combinations, product


def solve(topic, rows, text):
    nums = lambda pattern: tuple(map(int,re.search(pattern,text).groups()))
    match topic:
        case 1:
            p, = nums(r'실제 양성 (\d+)건')
            return [(p-t)*3+f*2 for t,f in rows], [F(t,t+f)>=F(2,3) for t,f in rows]
        case 2:
            y = nums(r'목표는 \((\d), (\d), (\d), (\d)\)')
            predictions = [tuple(int(a*x+b*z>=t) for x,z in product((0,1),repeat=2)) for a,b,t in rows]
            return [sum(x!=z for x,z in zip(y,q)) for q in predictions], [q[0]==y[0] for q in predictions]
        case 3:
            w,v = nums(r'각각 (\d+)%, (\d+)%')
            return [F(a,500)*w+F(b,500)*v for a,b,_ in rows], [c<=250 for _,_,c in rows]
        case 4:
            ref = nums(r'벡터는 \((\d+), (\d+), (\d+), (\d+)\)')
            return [sum(abs(F(b,sum(r))-F(a,sum(ref))) for a,b in zip(ref,r)) for r in rows], [r[-1]<=r[0] for r in rows]
        case 5:
            ref = set(re.search(r'단어는 ([a-z, ]+)다',text)[1].split(', '))
            docs = [set(r[0].split(', ')) for r in rows]
            return [F(len(ref^d),len(ref|d)) for d in docs], ['a' in d for d in docs]
        case 6:
            p,n,c = nums(r'\+(\d+), 부정 단어에는 −(\d+)을 준다\. 부정어가 붙은 긍정 단어는 대신 −(\d+)')
            return [abs((a-d)*p-b*n-d*c) for a,b,d in rows], [a+b>=15 for a,b,_ in rows]
        case 7:
            w,t = nums(r'\(R\+(\d+)G\+B\)/\d+다\. 평가값은 목표 밝기 (\d+)')
            return [abs(F(a+b*w+c,2+w)-t) for a,b,c in rows], [max(r)-min(r)<=150 for r in rows]
        case 8:
            s,t = nums(r'픽셀에 (\d+)를 더하되 .* 목표 (\d+)의 차이')
            matrices = [list(zip(*[list(map(lambda v:min(255,v+s),r[2:])),list(map(lambda v:min(255,v+s),r[:2]))])) for r in rows]
            return [abs(F(m[0][1]+m[1][1],2)-t) for m in matrices], [m[0][0]+m[1][0]>=220 for m in matrices]
        case 9:
            a,b,w = re.search(r'위쪽 행은 ([01]+), 아래쪽 행은 ([01]+)이다\..*?칸마다 (\d+)',text).groups()
            return [sum((int(w) if i<4 else 1) for i,(x,y) in enumerate(zip(a+b,''.join(r))) if x!=y) for r in rows], [''.join(r).count('1')<=5 for r in rows]
        case 10:
            p, = nums(r'고장 제품 (\d+)개')
            return [1-F(a,a+b) for a,b in rows], [F(a,p)>=F(2,3) for a,_ in rows]
        case 11:
            x,y,u,v = nums(r'관측점은 \((\d+), (\d+)\)와 \((\d+), (\d+)\)')
            return [abs(y-(a*x+b))+abs(v-(a*u+b)) for a,b in rows], [abs(v-(a*u+b))<=20 for a,b in rows]
        case 12:
            w, = nums(r'차례대로 1, (\d+), 1')
            return [sum(F(c*c*k,w+2) for c,k in zip(r,(1,w,1))) for r in rows], [abs(r[2])<=9 for r in rows]
        case 13:
            x,y,c = nums(r'초기점은 \((\d+), (\d+)\), 손실은 u²\+(\d+)v²')
            values = []
            for m,n in rows:
                u,v = F(x), F(y)
                for _ in range(n):
                    u -= F(m,16)*2*u
                    v -= F(m,16)*2*c*v
                values.append(u*u+c*v*v)
            return values, [abs(1-F(c*m,8))<1 for m,_ in rows]
        case 14:
            budget, = nums(r'비용이 (\d+) 이하')
            return [c-F(p,10)*b for c,p,b in rows], [c<=budget for c,_,_ in rows]
        case 15:
            goal,d = nums(r'목표 정확도는 (\d+)%.*최대와 최소 차이가 (\d+)%p')
            return [abs(F(a+b+c,3)-goal) for a,b,c in rows], [max(r)-min(r)<=d for r in rows]
    raise ValueError(topic)


def numeric(value):
    return F(value.rstrip('%점개').replace('−','-'))


def answer(kind, stem, values, eligible):
    v = dict(zip('ABCDE',values))
    valid = [c for c, ok in zip(v,eligible) if ok]
    if kind == 'ox':
        if m := re.search(r'^([A-E])의 평가값은 (\S+)이다\.$',stem):
            right = v[m[1]] == numeric(m[2])
        elif m := re.search(r'^([A-E])의 평가값은 ([A-E])보다 작다\.$',stem):
            right = v[m[1]] < v[m[2]]
        else:
            right = sum(eligible)==int(re.search(r'의 수는 (\d+)개다',stem)[1])
        return 'O' if right else 'X'
    if m := re.match(r'^([A-E])의 평가값(?:은\?|을 구하시오)',stem):
        return v[m[1]]
    if m := re.match(r'^([A-E])와 ([A-E])의 평가값 차이',stem):
        return abs(v[m[1]]-v[m[2]])
    if '다음 조건에 해당하는 후보는 몇 개인가' in stem or '의 개수를 구하시오' in stem:
        return len(valid)
    if stem.startswith('평가값의 최댓값과 최솟값'):
        return max(v.values())-min(v.values())
    if '평가값이 가장 작은 후보' in stem:
        chosen = [c for c in v if v[c]==min(v.values())]
    elif '평가값이 최소인 후보' in stem:
        chosen = [c for c in valid if v[c]==min(v[x] for x in valid)]
    elif '평가값 합은' in stem:
        return sum(v[x] for x in valid)
    elif '쌍은 몇 개인가' in stem:
        goal = numeric(re.search(r'평가값 합이 (\S+) 이하',stem)[1])
        return sum(v[a]+v[b]<=goal for a,b in combinations(valid,2))
    elif '세 후보 조합' in stem:
        goal = numeric(re.search(r'평가값 합이 (\S+) 미만',stem)[1])
        return sum(sum(v[x] for x in group)<goal for group in combinations(valid,3))
    elif '가장 작은 쌍은' in stem or '가장 가까운 쌍은' in stem:
        if '평균이' in stem:
            target = numeric(re.search(r'평균이 (\S+)에',stem)[1])
            pairs = {f'{a}·{b}':abs((F(v[a])+v[b])/2-target) for a,b in combinations(valid,2)}
        else:
            pairs = {f'{a}·{b}':abs(v[a]-v[b]) for a,b in combinations(valid,2)}
        chosen = [c for c in pairs if pairs[c]==min(pairs.values())]
    elif '개수' in stem or '몇 개인가' in stem:
        return len(valid)
    else:
        raise ValueError(stem)
    assert len(chosen)==1, (stem, chosen)
    return chosen[0]
