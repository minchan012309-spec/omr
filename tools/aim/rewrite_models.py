"""Forty curriculum-specific problem families for the replacement bank."""
from fractions import Fraction as F
from itertools import combinations, product

TYPES = (
 (1,'일반화 성능과 데이터 분리'),(1,'혼동행렬과 분류 지표'),
 (2,'논리 연산과 진리표'),(2,'퍼셉트론 임계값 역산'),(2,'규칙 기반 추론의 도달 가능성'),
 (3,'표본 편향과 가중 비율'),(3,'미응답과 추정 범위'),
 (4,'단어 집합과 등장 벡터'),(4,'빈도 벡터의 역추론'),(4,'정규화와 정보 손실'),
 (5,'말뭉치 합산과 대표어'),(5,'문서 빈도와 상대빈도'),
 (6,'부정 표현과 감성 점수'),(6,'자카드 유사도'),(6,'코사인과 유클리드 거리'),
 (7,'해상도와 채널 성분'),(7,'회색조 가중치와 이진화'),
 (8,'밝기 제한과 연산 순서'),(8,'영상 혼합과 가중치'),(8,'전치·반전·좌표 이동'),
 (9,'가중 해밍 거리'),(9,'픽셀 반전과 최근접 분류'),(9,'합성곱과 최대 풀링'),
 (10,'조건부확률의 분모'),(10,'연속 검사와 조건부확률'),(10,'조건부확률에서 사전확률 역산'),
 (11,'산점도와 추세선 복원'),(11,'잔차 비교와 외삽'),(11,'오차를 제한하는 추세선'),
 (12,'절대오차와 제곱오차'),(12,'가중 손실의 최적 상수'),(12,'손실 순위가 바뀌는 경계'),
 (13,'극한으로 구한 순간변화율'),(13,'경사하강 갱신과 반복'),(13,'학습률과 수렴·진동 조건'),
 (14,'기대 순편익과 자원 제약'),(14,'중복 효과와 최적 조합'),(14,'불확실성과 집단별 공정성'),
 (15,'검증 설계와 데이터 누출'),(15,'같은 표본의 비교와 결론'),
)


def solve(k, p, mode):
    """Return the student-facing task, solution, and alternatives tied to specific errors."""
    a,b,c,d,e = p
    q = F
    match k:
        case 1:
            n=a+8
            g=b+2
            z=c%(n-1)+1
            if mode==1:
                total=n*g
                return (f'원본당 프레임 수가 같은 영상 {n}개에서 총 {total}개 프레임을 추출했다. 원본 {z}개를 검증용으로 통째로 뺀다. 빠지는 프레임 수는?',z*g,f'원본마다 {total}/{n}={g}개다. 검증 원본 {z}개에 {g}를 곱한다.',[(z,'원본 수만 셌다.'),(g,'원본 하나의 프레임 수다.'),(total-z*g,'남는 훈련 프레임 수다.'),(total,'분리 전 전체다.')])
            if mode==2:
                return (f'영상 {n}개에서 각 {g}개 프레임을 뽑았다. 프레임을 하나씩 섞지 않고 원본을 통째로 골라 검증 프레임을 최소 {z*g-1}개 확보하려면 검증 원본은 최소 몇 개인가?',z,f'원본 {z-1}개의 프레임은 {(z-1)*g}개로 부족하다. {z}개를 고르면 {z*g}개가 된다.',[(z-1,'필요 프레임보다 적다.'),(z+1,'충분하나 최소가 아니다.'),(z*g-1,'프레임 수와 원본 수를 혼동했다.'),(n,'훈련에 쓸 원본을 남길 수 있다.')])
            return (f'원본 영상 {n}개에서 각각 프레임 {g}개를 뽑았다. 원본이 겹치지 않도록 {z}개 원본 전체를 시험에 사용한다. 훈련 프레임은 몇 개인가?',
                    (n-z)*g, f'시험에 속한 원본을 통째로 빼면 훈련 원본은 {n}−{z}={n-z}개다. 각 원본의 프레임 수를 곱한다.',
                    [(n*g-z,'원본마다 프레임이 여러 개라는 조건을 빠뜨렸다.'),(z*g,'시험 프레임 수다.'),(n*g,'분리 전 전체다.'),(n-z,'원본 수에 프레임 수를 곱해야 한다.')])
        case 2:
            tp,fn,fp,tn = a+5,b+1,c+1,d+6
            stem=f'분류 결과 참양성 {tp}건, 거짓음성 {fn}건, 거짓양성 {fp}건, 참음성 {tn}건이다.'
            metrics=[q(tp,tp+fp),q(tp,tp+fn),q(tp+tn,tp+tn+fn+fp),q(fp,fp+tn)]
            names=['정밀도','재현율','정확도','거짓양성률']
            return (stem+f' {names[mode]}는?',metrics[mode],f'정밀도는 양성 판정, 재현율은 실제 양성, 정확도는 전체, 거짓양성률은 실제 음성을 각각 분모로 삼는다. {names[mode]}는 {metrics[mode]}이다.',[(v,f'{name}에 해당한다.') for name,v in zip(names,metrics)])
        case 3:
            w,z,t=a,b,c
            scores=(0,w,z,w+z)
            bits=tuple(int(s>=t) for s in scores)
            orders=('(0,0), (1,0), (0,1), (1,1)','(1,0), (0,1), (1,1), (0,0)','(0,1), (1,1), (0,0), (1,0)','(1,1), (0,0), (1,0), (0,1)')
            idx=tuple((mode+i)%4 for i in range(4))
            return (f'점수 {w}x+{z}y가 {t} 이상이면 1이다. 입력 순서가 {orders[mode]}일 때 출력은?', ''.join(str(bits[i]) for i in idx),f'입력 순서대로 점수는 {tuple(scores[i] for i in idx)}다. 각 점수를 임계값 {t}와 비교한다.',[])
        case 4:
            u,v=a,b
            if mode%2:
                hi,lo=max(u,v),u+v
                task='두 입력이 모두 1일 때만 1'
            else:
                hi,lo=0,min(u,v)
                task='한 입력이라도 1이면 1'
            return (f'이진 입력의 점수는 {u}x+{v}y다. 점수가 정수 임계값 t 이상일 때 1이다. {task}이 되게 하는 정수 t의 개수는?',lo-hi,f'0이어야 하는 입력의 최대는 {hi}, 1이어야 하는 입력의 최소는 {lo}다. 따라서 {hi}<t≤{lo}다.',[(lo-hi+1,'아래 경계도 포함했다.'),(lo-hi-1,'위쪽 동점을 제외했다.'),(lo,'아래 경계를 빼지 않았다.'),(hi,'이는 0이어야 하는 입력의 최대 점수다.')])
        case 5:
            n=a+6
            step=b%4+2
            start=c%step+1
            # Cyclic rule graph includes chains, multiple components and cycles.
            start2=(start+d-1)%n+1
            edges=[(i,(i+step-1)%n+1) for i in range(1,n+1)]
            seeds={start,start2} if mode%2 else {start}
            seen=set(seeds)
            for _ in range(n):
                seen.update(y for x,y in edges if x in seen)
            return (f'사실 번호는 1~{n}이다. 규칙은 i가 참이면 {step}칸 뒤 번호가 참이 되는 것이다. {n} 다음은 다시 1이다. 처음 참은 {sorted(seeds)}이다. 추론을 끝냈을 때 처음 사실을 포함한 참의 수는?',len(seen),f'이미 참인 번호에서 반복적으로 {step}칸 이동한다. 중복을 빼면 {sorted(seen)}에 도달한다.',[(len(seeds),'최초 사실만 셌다.'),(n,'모든 사실이 도달 가능하다고 가정했다.'),(len(seen)-len(seeds),'최초 사실을 빼고 셌다.'),(step,'이동 간격은 사실 개수가 아니다.'),(n//step,'번호 순환의 나머지 연결을 무시했다.'),(len(seen)+len(seeds),'첫 사실을 두 번 셌다.'),(len(seen)-1,'순환 경로의 끝에 도달하기 전 하나를 빼었다.')])
        case 6:
            r,s=a+5,b+25
            w=c%7+2
            pooled=q(w*r+(10-w)*s,10)
            if mode>=2 and r!=s:
                return f'갑 오류율 {r}%, 을 오류율 {s}%인 집단의 전체 오류율이 {pooled}%다. 갑의 비중은 몇 %인가?',w*10,f'갑의 비중을 x로 두면 {r}x+{s}(1−x)={pooled}로부터 x={w}/10이다.',[((10-w)*10,'을의 비중이다.'),(50,'두 집단의 비중이 같다고 가정했다.'),(r,'갑의 오류율이다.'),(s,'을의 오류율이다.')]
            return (f'갑 집단의 오류율은 {r}%, 을은 {s}%다. 모집단에서 갑 비중이 {w*10}%일 때 전체 오류율의 백분율 값은?',pooled,f'갑의 기여는 {w*10}%×{r}%, 을의 기여는 {(10-w)*10}%×{s}%이다. 두 값을 더한다.',[(q(r+s,2),'집단 비중을 각각 절반으로 두었다.'),(q(w*s+(10-w)*r,10),'집단 비중을 바꿔 곱했다.'),(s,'을 집단만 사용했다.'),(r,'갑 집단만 사용했다.')])
        case 7:
            y,n,m=a+2,b+3,c+1
            size=y+n+m
            end=(y+m if mode%2 else y)
            return (f'조사에서 이용 {y}명, 비이용 {n}명, 미응답 {m}명이다. 전체 조사 대상 중 이용률의 가능한 {"최댓값" if mode%2 else "최솟값"}은?',q(end,size),f'모든 미응답을 {"이용" if mode%2 else "비이용"}으로 두면 분자는 {end}명, 분모는 {size}명이다.',[(q(y,y+n),'미응답을 분모에서 뺐다.'),(q(m,size),'미응답률이다.'),(q(n,size),'확인된 비이용 비율이다.'),(q(end,y+n),'극단값을 구하면서 대상 수를 줄였다.')])
        case 8:
            x=(a%7,b%5,c%3,d%3,e%2)
            y=(b%4,c%4,d%4,e%4,a%4)
            aa={i for i,v in enumerate(x) if v}
            bb={i for i,v in enumerate(y) if v}
            sets=[aa&bb,aa|bb,aa-bb,aa^bb]
            names=['두 문서 모두에','적어도 한 문서에','A에만','정확히 한 문서에만']
            return (f'어휘 순서를 맞춘 A,B 문서의 빈도 벡터는 {x}, {y}다. {names[mode]} 등장하는 단어의 종류는 몇 개인가?',len(sets[mode]),f'양수 성분의 위치 집합은 {sorted(i+1 for i in aa)}, {sorted(i+1 for i in bb)}다. 요구한 집합의 크기는 {len(sets[mode])}이다.',[(len(v),f'{name} 등장하는 어휘 수다.') for v,name in zip(sets,names)]+[(len(aa),'A에 등장한 종류만 센 값이다.'),(len(bb),'B에 등장한 종류만 센 값이다.'),(len(bb-aa),'B에만 등장하는 종류 수다.')])
        case 9:
            total=a+b+c+6
            known=a+1
            delta=b%5+1
            t=total-known
            ans=(t+delta)//2
            if (t+delta)%2 or ans>=t:return None
            return (f'총 빈도 {total}인 벡터 (x,y,z)에서 x={known}, y−z={delta}다. y는?',ans,f'y+z={t}와 y−z={delta}를 더하면 2y={t+delta}이다.',[(t,'y와 z의 합이다.'),(delta,'두 성분의 차다.'),(t-ans,'z에 해당한다.'),(total-known+delta,'양변을 2로 나누기 전이다.')])
        case 10:
            u,v,w=a,b,c
            sc=mode+2
            if mode>=2:
                return (f'문서의 어휘 (a,b,c) 빈도는 ({u},{v},{w})다. c를 모두 제거한 후 a의 상대빈도가 원래보다 얼마나 커지는가?',q(u,u+v)-q(u,u+v+w),f'새 상대빈도 {q(u,u+v)}에서 원래 상대빈도 {q(u,u+v+w)}를 뺀다.',[(q(u,u+v),'증가량이 아닌 변경 후 비율이다.'),(q(u,u+v+w),'변경 전 비율이다.'),(q(w,u+v+w),'제거한 단어의 비율이다.'),(q(u,u+v+w)-q(u,u+v),'빼는 순서가 반대다.')])
            return (f'문서 A의 빈도는 ({u},{v},{w})다. B는 A의 모든 빈도를 {sc}배 한 결과다. B에서 첫 단어의 상대빈도는?',q(u,u+v+w),f'B의 분자와 분모를 모두 {sc}배 한다. 공통인 양의 배율을 약분한다.',[(q(u*sc,u+v+w),'분자만 확대했다.'),(q(u,(u+v+w)*sc),'분모만 확대했다.'),(q(u,u+v),'세 번째 단어를 뺐다.'),(q(v,u+v+w),'두 번째 단어의 상대빈도다.')])
        case 11:
            x,y=a,b+2
            u,v=c+3,d
            # A and B are mixed k:1; one word overtakes the other.
            lo,hi=min(x,y),max(x,y)+1
            n=e+1
            return (f'A 원고에서 p는 {lo}회, q는 {hi}회다. B 원고에서는 p가 q보다 {n}회 많다. A를 k부, B를 1부 합칠 때 q가 p보다 앞서는 최소 양의 정수 k는?',n//(hi-lo)+1,f'합친 q−p는 ({hi}−{lo})k−{n}이다. 이 값이 0보다 커지는 첫 정수를 고른다.',[(n//(hi-lo),'경계 바로 아래 값이거나 동률이다.'),(n,'A 한 부당 빈도 차를 반영하지 않았다.'),(hi-lo,'한 부당 차이다.'),(n//(hi-lo)+2,'조건은 만족하나 더 작은 정수가 있다.')])
        case 12:
            m,n=a+b+3,c+d+3
            x,y=a,c
            return (f'문서 A는 {m}단어 중 표제어가 {x}회, B는 {n}단어 중 {y}회다. 두 문서를 합한 표제어 상대빈도는?',q(x+y,m+n),f'같은 어휘의 횟수와 전체 단어 수를 각각 합쳐 {{%s|%s}}을 계산한다.'%(x+y,m+n),[(q(x,m),'A만 사용했다.'),(q(y,n),'B만 사용했다.'),((q(x,m)+q(y,n))/2,'문서 크기에 무관한 단순 평균이다.'),(q(x+y,max(m,n)),'두 문서의 전체 단어 수를 더해야 한다.')])
        case 13:
            pos=a+3
            rev=min(pos,b)
            neg=c
            w=e%4+1
            r=d%3+1
            return (f'긍정 단어 {pos}개 중 {rev}개에는 부정어가 붙었고 부정 단어는 {neg}개다. 긍정 +{w}, 부정 −{r}, 부정어가 붙은 긍정은 −{w}다. 감성 점수는?',w*(pos-2*rev)-r*neg,f'부정어가 붙은 긍정 {rev}개는 원래 양수 대신 음수로 센다. {w}×({pos}−{rev})−{w}×{rev}−{r}×{neg}이다.',[(w*pos-r*neg,'부정어에 의한 반전을 빠뜨렸다.'),(w*(pos-rev)-r*neg,'반전 단어를 0점으로 처리했다.'),(w*(pos-2*rev)+r*neg,'부정 단어에 양수 점수를 주었다.'),(w*(pos-2*rev),'부정 단어를 누락했다.')])
        case 14:
            common,aonly,bonly=a+1,b+1,c+1
            move=min(aonly,d%5+1)
            return (f'A와 B의 공통 어휘는 {common}개, A에만 {aonly}개, B에만 {bonly}개다. A에만 있던 단어 {move}개를 B에도 넣을 때 새 자카드 유사도는?',q(common+move,common+aonly+bonly),f'같은 단어를 다른 문서에 추가해도 합집합은 그대로이고 교집합만 {move}개 커진다.',[(q(common,common+aonly+bonly),'추가 전 유사도다.'),(q(common+move,common+aonly+bonly+move),'이미 합집합에 있는 단어를 중복해 셌다.'),(q(common,common+aonly+bonly+move),'분자와 분모의 변화를 모두 잘못 적용했다.'),(q(common+move,common+aonly+bonly-move),'합집합에서 단어가 사라지지 않는다.')])
        case 15:
            u=(a,b);v=(c,d)
            h=(a+c,b+d)
            u2=a*a+b*b;v2=c*c+d*d
            dot=a*c+b*d
            if mode%2:
                return (f'문서 벡터 {u}, {v}의 코사인 유사도의 제곱은?',q(dot**2,u2*v2),f'내적은 {dot}, 두 벡터의 길이 제곱은 {u2}, {v2}이다. 내적의 제곱을 길이 제곱의 곱으로 나눈다.',[(q(dot,u2*v2),'내적을 제곱하지 않았다.'),(q(dot**2,u2+v2),'길이 제곱을 더했다.'),(q(dot**2,u2*u2),'첫 벡터의 길이를 두 번 사용했다.'),(q((a*d+b*c)**2,u2*v2),'서로 다른 좌표를 곱했다.')])
            return (f'벡터 {u}, {v}의 유클리드 거리를 제곱하면?',(a-c)**2+(b-d)**2,f'같은 순서의 성분 차를 각각 제곱해 더한다. ({a}−{c})²+({b}−{d})²이다.',[(abs(a-c)+abs(b-d),'절댓값을 더한 거리다.'),((a-c+b-d)**2,'성분을 먼저 더했다.'),(dot,'두 벡터의 내적이다.'),(sum(x*x for x in h),'차 벡터 대신 합 벡터를 사용했다.')])
        case 16:
            h,w=a+3,b+3
            cut=min(h-1,c%5+1)
            ch=3 if mode%2 else 1
            if mode>=2:
                total=(h-cut)*w*ch
                return f'너비 {w}인 RGB 영상에서 {cut}행을 잘라 낸 후 {"RGB를 유지" if ch==3 else "회색조로 변환"}했다. 결과의 채널 성분 수가 {total}이면 원본의 높이는 몇 행인가?',h,f'{total}을 한 행의 성분 수 {w*ch}로 나누면 남은 높이 {h-cut}다. 삭제한 {cut}행을 복원해 더한다.',[(h-cut,'결과 높이다.'),(h+cut,'삭제한 행을 중복 복원했다.'),(total//w,'채널 수와 삭제 행을 모두 고려해야 한다.'),(cut,'잘라 낸 행 수다.')]
            return f'{h}×{w} RGB 영상에서 {cut}행을 잘라 내고 {"RGB로 유지" if ch==3 else "회색조로 변환"}한다. 결과의 채널 성분 수는?',(h-cut)*w*ch,f'남은 픽셀 수는 ({h}−{cut})×{w}이다. 픽셀마다 성분이 {ch}개다.',[(h*w*ch,'잘라 낸 행을 남겼다.'),((h-cut)*w*(1 if ch==3 else 3),'채널 수를 변환 조건과 반대로 적용했다.'),((h-cut+w)*ch,'높이와 너비는 곱해야 한다.'),(cut*w*ch,'삭제된 부분을 계산했다.')]
        case 17:
            r,g,bl=6*a,6*b,6*c
            w=d%4+2
            target=q(r+w*g+bl,w+2)
            return f'픽셀 RGB는 ({r},{g},{bl})다. 회색조 밝기가 {{{{R+wG+B|w+2}}}}이고 w={w}이면 결과 밝기는?',target,f'채널의 가중합 {r+w*g+bl}을 가중치 합 {w+2}로 나눈다.',[(q(r+g+bl,3),'세 채널을 같은 비중으로 봤다.'),(q(w*r+g+bl,w+2),'녹색 대신 빨강에 가중치를 줬다.'),(q(r+w*g+bl,3),'채널 수로 나눴다.'),(q(r+w*g+bl,w),'양끝 채널의 가중치를 누락했다.')]
        case 18:
            n=200+a;s=b*3+15
            x=min(255,n+s)
            back=max(0,x-s)
            if mode>=2 and n+s>255:
                lo=255-s
                return f'픽셀값 x는 0~255의 정수다. {s}을 더해 255에서 자른 뒤 {s}을 뺐더니 {lo}였다. 가능한 x의 개수는?',s+1,f'첫 결과가 255여야 한다. x+{s}≥255이므로 x={lo}부터 255까지 모두 가능하다.',[(s,'양 끝 중 하나를 빼었다.'),(1,'밝기 제한 때문에 원본이 하나로 정해지지 않는다.'),(lo,'가능한 가장 작은 밝기다.'),(255,'가능한 가장 큰 밝기다.')]
            return f'밝기 {n}인 픽셀에 {s}을 더한 뒤 {s}을 뺀다. 각 단계에서 0~255로 제한한다. 두 번째 단계의 밝기는?',back,f'첫 단계는 min(255,{n}+{s})={x}이다. 여기에 다시 {s}을 뺀다.',[(n,'제한 전후를 구별하지 않았다.'),(x,'첫 단계 결과다.'),(n-s,'첫 번째 연산을 누락했다.'),(255,'최댓값에서 마지막 감소를 적용해야 한다.')]
        case 19:
            low=a+5; high=low+b+c+5
            den=d%6+3
            num=e%(den-1)+1
            k=q(num,den)
            alpha=k if mode%2 else 1-k
            y=alpha*high+(1-alpha)*low
            return f'픽셀 A={high}, B={low}를 C=αA+(1−α)B로 혼합했다. 측정된 C={y}이면 A의 가중치 α는?',alpha,f'C−B=α(A−B)이므로 α={alpha}이다. 혼합 결과는 두 원본 밝기 사이에 있다.',[(1-alpha,'B의 가중치를 구했다.'),(q(y,high),'B 항을 무시했다.'),(q(y-low,high),'차의 분모가 A가 아니라 A−B다.'),(q(high-low,y-low),'분자와 분모를 바꿨다.')]
        case 20:
            h,w=a+3,b+3;i,j=c%h+1,d%w+1
            answer=(j,h+1-i) if mode%2 else (w+1-j,i)
            order='전치한 뒤 좌우 반전' if mode%2 else '좌우 반전한 뒤 전치'
            return f'{h}행 {w}열 영상의 ({i},{j}) 픽셀에 {order}을 적용한다. 새 좌표는?',str(answer),f'전치는 (i,j)를 (j,i)로, 좌우 반전은 현재 열 수를 t라 할 때 열 j를 t+1−j로 보낸다. 적용 순서를 지키면 {answer}이다.',[(str(x),reason) for x,reason in [((j,i),'전치만 적용했다.'),((i,w+1-j),'좌우 반전만 적용했다.'),((j,w+1-i),'전치 뒤 현재 열 수를 잘못 사용했다.'),((w+1-j,i) if mode%2 else (j,h+1-i),'두 연산의 순서를 바꿨다.')]]
        case 21:
            x=f'{(a*17+b)%1024:010b}';y=f'{(c*17+d)%1024:010b}'
            weight=e%6+2
            u=sum(m!=n for m,n in zip(x[:5],y[:5]))
            v=sum(m!=n for m,n in zip(x[5:],y[5:]))
            return f'두 이진 문자열은 {x}, {y}다. 앞 다섯 자리의 불일치에 {weight}점, 뒤 다섯 자리에는 1점을 준다. 가중 해밍 거리는?',weight*u+v,f'앞부분에서 {u}자리, 뒷부분에서 {v}자리가 다르다. {weight}×{u}+{v}를 계산한다.',[(u+v,'가중치 없이 셌다.'),(u+weight*v,'가중치를 뒤쪽에 적용했다.'),(weight*(u+v),'두 부분 모두 같은 가중치를 줬다.'),(weight*u,'뒤쪽 불일치를 빼먹었다.')]
        case 22:
            from math import comb
            n=a%19+6
            t=b%(n-2)+1
            u=c%(t+1)
            v=d%(n-t+1)
            if u+v<1:return None
            dist=t-u+v
            return f'{n}자리 이진 영상의 기준 A는 모두 0, 기준 B는 처음 {t}자리만 1이다. 입력은 A에서 처음 {t}자리 중 {u}자리, 나머지 중 {v}자리를 반전해 만든다. 가능한 입력 수는?',comb(t,u)*comb(n-t,v),f'두 부분에서 반전 위치를 독립적으로 고른다. 각각 {comb(t,u)}가지, {comb(n-t,v)}가지이므로 곱한다. 모든 입력과 B의 거리는 {dist}이다.',[(comb(n,u+v),'부분별 개수 조건을 빼고 골랐다.'),(comb(t,u)+comb(n-t,v),'두 선택은 동시에 해야 한다.'),(comb(t,u),'앞부분만 골랐다.'),(comb(n-t,v),'뒷부분만 골랐다.'),(comb(t,u)*comb(n-t,v)*(u+v),'같은 입력을 반전 순서 때문에 중복 계수했다.'),(2**n,'반전 조건을 적용하기 전의 모든 패턴 수다.')]
        case 23:
            arr=((a,b,c),(d,e,a+b),(b+c,c+d,d+e))
            vals=[arr[i][j+1]-arr[i][j]+arr[i+1][j+1]-arr[i+1][j] for i,j in product(range(2),repeat=2)]
            stem=f'3×3 영상의 각 행은 {arr[0]}, {arr[1]}, {arr[2]}다. 행이 (−1,1), (−1,1)인 필터를 뒤집지 않고, 패딩 없이 한 칸씩 적용한다.'
            value=max(vals) if mode%2 else min(vals)
            return stem+f' 결과 네 값의 {"최댓값" if mode%2 else "최솟값"}은?',value,f'각 창에서 오른쪽 열 합에서 왼쪽 열 합을 빼면 {vals}이다.',[(val,'해당 창의 응답이지만 요구한 극값인지 비교해야 한다.') for val in vals]
        case 24:
            p,n=a+b,c+d
            t,f=b,d
            pos=mode%2
            ans=q(t,t+f) if pos else q(t,p)
            given='경보가 울린 제품 중 고장' if pos else '고장 제품 중 경보'
            return f'고장 {p}개 중 {t}개, 정상 {n}개 중 {f}개에서 경보가 울렸다. {given}의 비율은?',ans,f'두 사건에 모두 해당하는 수는 {t}개다. 주어진 조건에 해당하는 전체만 분모로 사용한다.',[(q(t,p),'고장 제품 전체를 분모로 삼았다.'),(q(t,t+f),'경보가 울린 전체를 분모로 삼았다.'),(q(t,p+n),'검사 전체를 분모로 삼았다.'),(q(f,t+f),'경보 중 정상 비율이다.'),(q(f,n),'정상 중 경보 비율이다.')]
        case 25:
            t,f=a+b,c+d
            u,v=b,d
            return f'1차 양성은 고장품 {t}개, 정상품 {f}개다. 그중 2차도 양성인 것은 각각 {u}개, {v}개다. 두 번 양성인 제품 중 고장 비율은?',q(u,u+v),f'2차까지 통과한 제품만 남긴다. 고장 {u}개, 정상 {v}개를 더한 {u+v}개가 분모다.',[(q(t,t+f),'1차 결과만 비교했다.'),(q(u,t),'1차 양성 고장품의 2차 통과율이다.'),(q(u,t+f),'1차 양성 전체를 분모로 삼았다.'),(q(v,u+v),'두 번 양성 중 정상 비율이다.')]
        case 26:
            s=q(a%9+11,20);f=q(b%8+1,20);z=q(c%10+8,20)
            p=z*f/(s*(1-z)+z*f)
            return f'고장률을 p라 하자. 고장품 양성률은 {s}, 정상품 양성률은 {f}다. 양성 중 고장 확률이 {z}일 때 p는?',p,f'{s}×p를 고장 양성 비율로 두고 전체 양성 비율은 여기에 {f}×(1−p)를 더한다. 조건부확률을 {z}와 같게 놓으면 p={p}다.',[(z,'조건부확률을 전체 확률로 사용했다.'),(f,'정상 제품의 양성률이다.'),(1-p,'정상 제품의 비율이다.'),(z*f/s,'양성 분모의 고장 항을 반영하지 않았다.')]
        case 27:
            x=a+1;gap=b+1;m=q(c+1,d%5+1);y=e+3
            ny=y+gap*m;target=x+gap+1+mode
            return f'점 ({x},{y})와 ({x+gap},{ny})를 지나는 추세선에서 x={target}의 예측값은?',y+(target-x)*m,f'기울기는 y의 차를 x의 차로 나눈 {m}이다. 첫 점에서 x가 {target-x} 증가하므로 y는 그만큼의 기울기 배수만큼 증가한다.',[(y+target*m,'첫 점의 x를 빼지 않았다.'),(y+(target-x)/m,'기울기 대신 역수를 썼다.'),(ny,'두 번째 관측점의 y다.'),(y-(target-x)*m,'증가량을 빼었다.')]
        case 28:
            x=a+c; m=b%5+1; intercept=d+1; obs=e+x
            pred=m*x+intercept
            return f'추세선 ŷ={m}x+{intercept}에서 x={x}의 관측값 y는 {obs}다. 잔차 y−ŷ는?',obs-pred,f'예측값은 {pred}이므로 관측값 {obs}에서 뺀다.',[(pred-obs,'잔차 부호를 뒤집었다.'),(obs-m*x,'절편을 뺄셈에 반영하지 않았다.'),(obs+pred,'잔차는 합이 아니다.'),(pred,'예측값 자체다.')]
        case 29:
            m=a%5+1;k=b+5; delta=c%4+1
            y1=k;y2=k+m+(e%5-2);tol=d%4+1
            # Two data points bound the intercept; calculate exact feasible integers.
            low=max(y1-tol,y2-m-tol)
            high=min(y1+tol,y2-m+tol)
            if high<max(low,k-delta):return None
            return f'직선 y={m}x+b에서 x=0,1의 관측값은 각각 {y1}, {y2}이다. 두 관측점의 절대오차가 각각 {tol} 이하이고 b≥{k-delta}일 때 가능한 정수 b는 몇 개인가?',high-max(low,k-delta)+1,f'첫 관측의 허용 구간은 {y1-tol}~{y1+tol}, 둘째는 {y2-m-tol}~{y2-m+tol}이다. 두 구간의 교집합은 {low}≤b≤{high}다. 추가 하한까지 적용하면 b≥{max(low,k-delta)}이므로 양 끝을 포함해 센다.',[(high-low+1,'추가 하한을 생략했다.'),(high-max(low,k-delta),'양 끝 중 하나를 빼었다.'),(high,'상한 자체다.'),(2*tol,'범위 폭만 썼다.'),(2*tol+1,'한 관측점의 오차 구간만 셌다.'),(max(0,min(y1-tol,y2-m-tol)+2*tol-max(low,k-delta)+1),'두 구간의 교집합 경계를 잘못 적용했다.'),(high-max(low,k-delta)+2,'경계 밖 정수를 한 개 더 셌다.')]
        case 30:
            vals=(a,-b,c,-d)
            mae=q(sum(abs(x) for x in vals),4)
            mse=q(sum(x*x for x in vals),4)
            if mode>=2:
                return f'잔차가 {vals}인 모형에서 잔차의 부호만 모두 반대로 기록했다. 수정 전 평균제곱오차와 수정 후 평균제곱오차의 차는?',0,f'각 잔차의 제곱은 부호를 뒤집어도 같다. 두 제곱평균은 모두 {mse}다.',[(mse,'이는 양쪽의 손실 자체다.'),(mae,'평균절대오차 자체다.'),(2*mse,'두 손실을 더했다.'),(q(sum(vals),4),'부호가 있는 오차 평균이다.')]
            return f'모형의 잔차가 {vals}이다. {"평균제곱오차" if mode%2 else "평균절대오차"}는?',mse if mode%2 else mae,f'각 잔차에 {"제곱" if mode%2 else "절댓값"}을 적용한 뒤 4개를 평균한다.',[(mae if mode%2 else mse,'다른 종류의 손실을 구했다.'),(q(sum(vals),4),'부호 있는 오차를 평균했다.'),(q(sum(vals),4)**2,'평균을 먼저 냈다.'),(sum(abs(x) for x in vals),'개수로 나누지 않았다.')]
        case 31:
            x,y,z=a,b,c+15;w=d%6+2
            target=q(x+y+w*z,w+2)
            return f'세 관측값 {x}, {y}, {z}를 하나의 상수 u로 예측한다. 세 번째 관측값의 제곱오차에 가중치 {w}, 나머지에 1을 줄 때 손실을 최소로 하는 u는?',target,f'도함수를 0으로 두면 ({w}+2)u={x}+{y}+{w}×{z}이다. 이차항 계수가 양수이므로 이 해에서 최소다.',[(q(x+y+z,3),'가중치를 적용하지 않았다.'),(q(x+y+w*z,3),'분모는 가중치의 합이어야 한다.'),(q(x+y+w*z,w),'다른 두 가중치를 누락했다.'),(q(x+y,2),'세 번째 관측을 빼었다.')]
        case 32:
            u,v=a%7+2,b%7+1
            x,y=c%6+1,d%6+1
            if u==x or ((y*y-v*v)*(u*u-x*x))<=0:return None
            root=q(y*y-v*v,u*u-x*x)
            return f'A의 절대오차는 ({u},{v}), B는 ({x},{y})다. 첫 오차 제곱에만 양의 가중치 w를 줄 때 두 제곱오차 합이 같아지는 w는?',root,f'{u*u}w+{v*v}={x*x}w+{y*y}를 풀면 w={root}다.',[(1/root,'차의 비율을 뒤집었다.'),(q(y-v,u-x),'오차를 제곱하기 전에 차를 냈다.'),(q(y*y+v*v,abs(u*u-x*x)),'상수항을 더했다.'),(q(abs(y*y-v*v),u*u+x*x),'가중치 항의 차 대신 합을 썼다.')]
        case 33:
            u=a%8+1;v=b%7+1;x=c%9+1
            answer=2*u*x+v
            return f'f(x)={u}x²+{v}x이다. x={x}에서 순간변화율은?',answer,f'차분의 분자는 h({2*u*x+v}+{u}h)이다. h≠0에서 약분한 뒤 h→0을 적용한다.',[(u*x*x+v*x,'함숫값을 계산했다.'),(u*x+v,'제곱항 미분의 계수 2를 빼었다.'),(2*u*x,'일차항의 미분을 빠뜨렸다.'),(2*u+v,'미분 후 x를 대입하지 않았다.')]
        case 34:
            center=a%9+1;delta=b%7+2;k=c%4+1
            steps=d%4+1
            eta=q(1,4*k);r=1-2*k*eta
            ans=center+delta*r**steps
            return f'L(w)={k}(w−{center})², 초기값 w={center+delta}, 학습률 {eta}이다. 같은 학습률로 {steps}번 갱신한 값은?',ans,f'최적점과의 차는 {delta}에서 시작해 매번 {r}배가 된다. 중심 {center}를 마지막에 더한다.',[(delta*r**steps,'최적점과의 차만 구했다.'),(center+delta*r**(steps+1),'한 번을 더 갱신했다.'),(center+delta*r**(steps-1),'한 번의 갱신을 빼었다.'),(center-delta*r**steps,'갱신 인자는 양수이므로 중심의 반대편으로 가지 않는다.')]
        case 35:
            k=a%9+1;t=b%5+1;r=q(1,t+1)
            ans=(1+r)/(2*k) if mode%2 else (1-r)/(2*k)
            sign='바뀐다' if mode%2 else '유지된다'
            return f'L(w)={k}(w−{c})²에서 초기값은 최적점과 다르다. 최적점과의 차의 크기가 매번 {r}배가 되고 부호는 {sign}. 학습률은?',ans,f'갱신 인자는 1−{2*k}η이다. 부호 조건을 적용하면 인자가 {"−" if mode%2 else ""}{r}이므로 η를 역산한다.',[(q(1,2*k),'이 값은 한 번에 최적점에 도달한다.'),((1-r)/(2*k) if mode%2 else (1+r)/(2*k),'부호 조건을 반대로 골랐다.'),(r,'오차 배율과 학습률은 서로 다른 값이다.'),(q(1,k),'갱신 인자가 −1로 크기가 유지된다.')]
        case 36:
            p=q(a%8+1,10);win=b+12;loss=c+2;cost=d+1
            ans=p*win-(1-p)*loss-cost
            return f'정책 성공 확률은 {p}, 성공 편익은 {win}점이다. 실패 시 {loss}점을 잃고 결과와 관계없이 비용 {cost}점을 낸다. 기대 순편익은?',ans,f'성공 항은 {p}×{win}, 실패 항은 (1−{p})×(−{loss})이며 공통 비용을 뺀다.',[(p*win-cost,'실패 손실을 누락했다.'),(p*win-(1-p)*loss,'공통 비용을 누락했다.'),(p*win+(1-p)*loss-cost,'실패를 편익으로 처리했다.'),(p*(win-cost)-(1-p)*loss,'공통 비용을 성공한 경우에만 적용했다.')]
        case 37:
            A,B,C=a+10,b+9,c+6
            overlap=d+2
            candidates={'A·B':A+B-overlap,'A·C':A+C,'B·C':B+C,'A만':A,'B만':B}
            best=max(candidates.values())
            winners=[key for key,val in candidates.items() if val==best]
            if len(winners)!=1:return None
            label=winners[0]
            return f'A,B,C의 순편익은 {A},{B},{C}점이다. 최대 두 정책을 고를 수 있다. A와 B를 같이 하면 효과가 겹쳐 {overlap}점을 뺀다. 순편익이 가장 큰 선택은?',label,f'조합별 결과는 '+', '.join(f'{key} {val}' for key,val in candidates.items())+f'점이다. {label}이 최대다.',[(key,f'이 선택의 순편익은 {val}점이다.') for key,val in candidates.items()]
        case 38:
            win=a+15;loss=b+1;low=q(c%5+1,10);high=low+q(d%4+1,10)
            fixed=e
            w1=(win+loss)*low-loss;w2=(win+loss)*high-loss
            if w1==fixed:return None
            return f'정책 A의 성공 편익 {win}, 실패 편익 −{loss}이고 성공 확률 p는 {low}~{high}다. 정책 B는 항상 {fixed}를 얻는다. 각 정책의 가능한 기대값 중 최솟값이 큰 쪽의 그 최솟값은?',max(w1,fixed),f'A의 기대값은 ({win}+{loss})p−{loss}로 증가한다. A의 최솟값은 {w1}, B는 {fixed}다.',[(min(w1,fixed),'최솟값이 더 작은 정책을 선택했다.'),(w2,'A의 낙관적인 상한을 사용했다.'),((w1+w2)/2,'확률 범위의 중간값을 사용했다.'),(win,'성공할 때의 편익만 사용했다.')]
        case 39:
            alln=a+12;test=b+c+2;similar=c%12+2
            cases=['학습','검증','최종 시험','외부 재평가','자료 전처리 규칙 고정']
            m=mode%4
            scenarios=[
                f'{alln}개 문서를 정답과 함께 주고 입력 특징 {d}개로 모형의 가중치를 계산했다.',
                f'{alln}개 문서에서 서로 다른 {d}개 기준의 성능을 비교해 후보 {similar}개 중 최적 모형을 골랐다.',
                f'모형과 문턱값을 확정하고 서로 다른 {d}개 기관의 미사용 문서 {test}개에서 성능을 한 번만 계산했다.',
                f'최종 시험을 마친 뒤 다른 {d}개 기관이 수집한 {alln}개 문서로 성능을 다시 측정했다.']
            explanations=['정답으로 모형 자체의 가중치를 맞췄다.','자료를 써서 여러 후보 중 하나를 골랐다.','이미 확정된 모형을 독립 자료에 적용했다.','기관이 다른 새 자료에서 결과가 유지되는지 본다.','토큰화나 정규화 방법만 정하는 절차를 말한다.']
            return scenarios[m]+' 이 단계는?',cases[m],explanations[m],list(zip(cases,explanations))
        case 40:
            n=a+b+c+d
            A,B=a+b,a+c
            upper,lower=min(A,B),max(0,A+B-n)
            mode=mode%2
            return f'같은 {n}개 사례에서 A는 {A}개, B는 {B}개를 맞혔다. 두 모형 모두 맞힌 사례 수의 가능한 {"최댓값" if mode else "최솟값"}은?',upper if mode else lower,f'정답 집합의 교집합은 어느 쪽 정답 수도 넘지 못하고, 합집합이 {n} 이하이므로 적어도 {lower}개다. 따라서 가능한 범위는 {lower}~{upper}개다.',[(abs(A-B),'정답 수 차이이다.'),(upper if not mode else lower,'요구한 극값의 반대쪽이다.'),(max(A,B),'두 모형 중 큰 정답 수다.'),(A+B,'공통 사례를 중복 계수했다.')]
    raise ValueError(k)
