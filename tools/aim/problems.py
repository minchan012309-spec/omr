"""Data and exact scoring rules for the fifteen AI mathematics topics."""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product


@dataclass
class Scenario:
    headers: tuple
    rows: list
    metric: str
    values: list
    eligible: list
    constraint: str
    unit: str = ''
    pixels: bool = False


def scenario(topic, rng):
    """Construct a problem instance with quantities in the curriculum's domain."""
    ri = rng.randint
    match topic:
        case 1:
            p, n = ri(30, 66), ri(40, 95)
            rows = [(ri(8, p), ri(0, n//2)) for _ in range(5)]
            return Scenario(('참양성', '거짓양성'), rows,
                f'실제 양성 {p}건, 실제 음성 {n}건이다. 오분류 비용은 거짓음성 3점, 거짓양성 2점이다. 평가값은 오분류 비용의 합이다.',
                [3*(p-t)+2*f for t,f in rows], [t >= 2*f for t,f in rows], '정밀도가 2/3 이상인 후보', '점')
        case 2:
            target = rng.choice([(0,0,0,1), (0,1,1,1), (0,1,1,0), (1,0,0,1)])
            rows = [tuple(ri(-9, 9) for _ in range(3)) for _ in range(5)]
            predictions = [[int(a*x+b*y >= t) for x,y in product((0,1), repeat=2)] for a,b,t in rows]
            return Scenario(('가중치 a', '가중치 b', '임계값 t'), rows,
                f'퍼셉트론은 ax+by≥t일 때 1을 출력한다. 입력 (0,0), (0,1), (1,0), (1,1)의 목표는 {target}이다. 평가값은 목표와 다른 출력의 수다.',
                [sum(a!=b for a,b in zip(pred,target)) for pred in predictions],
                [pred[0] == target[0] for pred in predictions], '(0,0) 입력에서 목표를 맞힌 후보', '개')
        case 3:
            weight = ri(3, 7)
            rows = [(ri(40, 180), ri(20, 240), ri(30, 400)) for _ in range(5)]
            return Scenario(('갑 표본 이용자(500명 중)', '을 표본 이용자(500명 중)', '중복 레코드 수'), rows,
                f'갑과 을의 모집단 비중은 각각 {weight*10}%, {(10-weight)*10}%다. 평가값은 두 표본 이용률을 이 모집단 비중으로 가중평균한 백분율 값이다.',
                [F(weight*a+(10-weight)*b,50) for a,b,_ in rows],
                [d <= 250 for _,_,d in rows], '중복 레코드가 250건 이하인 조사', '%')
        case 4:
            ref = tuple(ri(1, 10) for _ in range(4))
            rows = [tuple([ri(1,12), *(ri(0,12) for _ in range(3))]) for _ in range(5)]
            return Scenario(('단어 a', '단어 b', '단어 c', '단어 d'), rows,
                f'기준 문서의 단어 빈도 벡터는 {ref}다. 평가값은 기준과 후보의 상대빈도 벡터에서 성분별 차이 절댓값의 합이다. 상대빈도는 각 문서의 전체 빈도로 나누어 구한다.',
                [sum(abs(F(a,sum(ref))-F(b,sum(row))) for a,b in zip(ref,row)) for row in rows],
                [r[3] <= r[0] for r in rows], '단어 d의 빈도가 a 이하인 문서')
        case 5:
            ref = set(rng.sample(list('abcdefghij'), ri(3, 7)))
            docs = [set(rng.sample(list('abcdefghij'),ri(2,8))) for _ in range(5)]
            return Scenario(('등장 단어 집합',), [(', '.join(sorted(s)),) for s in docs],
                f'기준 문서의 단어는 {", ".join(sorted(ref))}다. 자카드 유사도는 공통 단어 수를 전체 고유 단어 수로 나눈 값이다. 평가값은 1−자카드 유사도이다.',
                [1-F(len(ref&s),len(ref|s)) for s in docs], ['a' in s for s in docs], '단어 a가 등장한 문서')
        case 6:
            p, n = ri(2, 6), ri(2, 6)
            rows = [(ri(3, 15), ri(0, 13), ri(0, 3)) for _ in range(5)]
            return Scenario(('긍정 단어 수', '부정 단어 수', '부정어가 붙은 긍정 단어 수'), rows,
                f'긍정 단어에는 +{p}, 부정 단어에는 −{n}을 준다. 부정어가 붙은 긍정 단어는 대신 −{p}로 계산한다. 평가값은 감성 점수와 중립 점수 0 사이의 거리다.',
                [abs((a-2*c)*p-b*n) for a,b,c in rows],
                [a+b >= 15 for a,b,_ in rows], '긍정·부정 단어를 합해 15개 이상인 문서')
        case 7:
            rows = [tuple(ri(15, 240) for _ in range(3)) for _ in range(5)]
            target = ri(70, 185)
            w = ri(2, 5)
            return Scenario(('R', 'G', 'B'), rows,
                f'회색조 밝기는 (R+{w}G+B)/{w+2}다. 평가값은 목표 밝기 {target}과의 차이의 절댓값이다.',
                [abs(F(r+w*g+b,w+2)-target) for r,g,b in rows], [max(a)-min(a) <= 150 for a in rows],
                'RGB 최댓값과 최솟값 차이가 150 이하인 픽셀')
        case 8:
            target, shift = ri(40, 165), ri(10, 65)
            rows = [tuple(ri(15, 240) for _ in range(4)) for _ in range(5)]
            return Scenario(('첫째 행 왼쪽', '첫째 행 오른쪽', '둘째 행 왼쪽', '둘째 행 오른쪽'), rows,
                f'2×2 영상의 모든 픽셀에 {shift}를 더하되 255에서 자른 뒤 시계 방향으로 90° 회전한다. 평가값은 회전 뒤 오른쪽 열의 평균 밝기와 목표 {target}의 차이의 절댓값이다.',
                [abs(F(min(255,a+shift)+min(255,b+shift),2)-target) for a,b,_,_ in rows],
                [min(255,c+shift)+min(255,d+shift) >= 220 for _,_,c,d in rows],
                '변환 뒤 왼쪽 열의 평균 밝기가 110 이상인 영상')
        case 9:
            ref = tuple(ri(0,1) for _ in range(8))
            rows = rng.sample(list(product((0,1),repeat=8)),5)
            w = ri(2, 8)
            return Scenario(('위쪽 행', '아래쪽 행'), [(''.join(map(str,r[:4])), ''.join(map(str,r[4:]))) for r in rows],
                f'입력 영상 위쪽 행은 {"".join(map(str,ref[:4]))}, 아래쪽 행은 {"".join(map(str,ref[4:]))}이다. 평가값은 입력 영상과의 가중 해밍 거리다. 위쪽 행 불일치는 칸마다 {w}, 아래쪽 행 불일치는 칸마다 1을 더한다.',
                [sum((w if i<4 else 1) for i,(a,b) in enumerate(zip(ref,r)) if a!=b) for r in rows],
                [sum(r) <= 5 for r in rows], '켜진 픽셀이 5개 이하인 영상', '', True)
        case 10:
            p,n = ri(35,95),ri(150,500)
            rows = [(ri(10,p),ri(1,n//2)) for _ in range(5)]
            return Scenario(('실제 고장 중 양성', '실제 정상 중 양성'), rows,
                f'고장 제품 {p}개와 정상 제품 {n}개를 검사했다. 평가값은 양성 제품 중 실제로 정상인 비율이다.',
                [F(b,a+b) for a,b in rows], [3*a>=2*p for a,_ in rows], '고장 검출률이 2/3 이상인 검사')
        case 11:
            x = ri(2,7)
            y,z = ri(15,65),ri(35,110)
            rows = [(ri(1,12),ri(0,20)) for _ in range(5)]
            return Scenario(('기울기 a','절편 b'), rows,
                f'관측점은 ({x}, {y})와 ({x+3}, {z})다. 후보 직선은 y=ax+b이다. 평가값은 두 관측점의 절대오차 합이다.',
                [abs(a*x+b-y)+abs(a*(x+3)+b-z) for a,b in rows],
                [abs(a*(x+3)+b-z)<=20 for a,b in rows], '두 번째 점의 절대오차가 20 이하인 직선')
        case 12:
            w = ri(2,6)
            rows = [tuple(ri(-15,15) for _ in range(3)) for _ in range(5)]
            return Scenario(('오차 1', '오차 2', '오차 3'), rows,
                f'평가값은 가중 평균제곱오차다. 세 오차의 가중치는 차례대로 1, {w}, 1이며 가중치의 합으로 나눈다.',
                [F(a*a+w*b*b+c*c,w+2) for a,b,c in rows], [abs(c)<=9 for _,_,c in rows],
                '세 번째 절대오차가 9 이하인 모형')
        case 13:
            u,v = ri(3,24),ri(3,24)
            k = ri(2,6)
            rows = [(x,ri(1,3)) for x in rng.sample(range(1,13),5)]
            return Scenario(('학습률 분자 m (η=m/16)', '갱신 횟수'), rows,
                f'초기점은 ({u}, {v}), 손실은 u²+{k}v²이다. 두 좌표에 같은 학습률 η로 경사하강을 적용한다. 평가값은 표에 주어진 횟수만큼 갱신한 뒤의 손실이다.',
                [u*u*(1-F(x,8))**(2*j)+k*v*v*(1-F(k*x,8))**(2*j) for x,j in rows],
                [0 < F(k*x,8) < 2 for x,_ in rows], 'v 좌표가 0으로 수렴하는 학습률의 후보')
        case 14:
            budget = ri(14,32)
            rows = [(ri(5,32),ri(2,9),ri(30,99)) for _ in range(5)]
            return Scenario(('비용','성공 확률 분자 (분모 10)','성공 시 편익'), rows,
                '실패 시 편익은 0이며 비용은 항상 지불한다. 평가값은 비용에서 편익의 기댓값을 뺀 값이다.',
                [c-F(p*b,10) for c,p,b in rows], [c<=budget for c,_,_ in rows], f'비용이 {budget} 이하인 정책')
        case 15:
            target, d = ri(78,95),ri(4,12)
            rows = [tuple(ri(65,100) for _ in range(3)) for _ in range(5)]
            return Scenario(('검증 1 정확도(%)','검증 2 정확도(%)','검증 3 정확도(%)'), rows,
                f'탐구 목표 정확도는 {target}%다. 평가값은 세 검증 정확도의 평균과 목표 정확도 사이의 거리다.',
                [abs(F(sum(r),3)-target) for r in rows], [max(r)-min(r)<=d for r in rows],
                f'세 정확도의 최대와 최소 차이가 {d}%p 이하인 모형')
    raise ValueError(topic)
