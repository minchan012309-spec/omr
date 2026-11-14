"""Apply the editorial review to the original AI mathematics questions and lessons."""
import json
import re
from pathlib import Path

from explain import math, math_html

ROOT = Path(__file__).resolve().parents[2] / 'aim'
BASE_END = '<p class="aim-choice">'
CORRECTIONS = {
    'AM-004': ('A·A의 재현율은 90%, 65%로 탈락한다. 가능한 A·B, B·A, B·B의 정답 수는 각각 153, 169, 165건이므로 B·A의 정확도 84.5%가 최대다.',
               'A·A의 재현율 차이는 25%p로 탈락한다. 가능한 A·B, B·A, B·B의 정답 수는 각각 153, 169, 165건이다. B·A의 정확도 169/200=84.5%가 최대다.'),
    'AM-048': ('c=a+b라 두면 손실은 (2−c+a)²+2c²+(1−c−a)²이다. c=±2 이상이면 8 이상이고 c=−1도 양 끝 오차합 때문에 3보다 크다. c=0에서는 최소 5, c=1에서는 a=−1 또는 0으로 최소 3이다.',
               'c=a+b라 두면 L=(2−c+a)²+2c²+(1−c−a)²이다. |c|≥2이면 2c²≥8이다. c=−1, 0, 1에서 양 끝 제곱항의 합의 최솟값은 각각 13, 5, 1이다. 중간 항을 더한 최솟값은 15, 5, 3이므로 c=1, a=0 또는 −1일 때 최소 손실 3이다.'),
}
OX_REVIEW = [
 '학습 데이터의 예시를 사용해 분류 경계를 추정할 수 있다.',
 '입력 (1,0)도 합이 1이므로 이 규칙의 출력은 1이다. AND에서는 0이며 제시된 규칙은 OR이다.',
 '규모가 크고 생성이 빠르며 형식이 다양한 데이터는 기존 처리 방식으로 다루기 어려울 수 있다.',
 '0·1 벡터의 1은 한 번 이상 등장했다는 뜻이다. 1회와 3회는 같은 값 1로 표시된다.',
 '텍스트의 단어 빈도는 어떤 단어가 자주 등장하는지 판단하는 한 가지 근거다.',
 '부정어가 붙으면 단어의 감성이 뒤집힐 수 있다. 단순 점수 합은 이런 문맥을 빠뜨릴 수 있다.',
 '픽셀 위치와 행렬 성분이 대응한다. 각 성분은 밝기값을 저장한다.',
 '행과 열을 맞바꾸므로 2행 3열의 전치 결과는 3행 2열이다.',
 '두 문자열의 길이와 대응 위치를 같게 둔 뒤 값이 다른 자리의 수를 센다.',
 '검출률은 전체 고장 수가 분모이고, 양성 중 고장 비율은 전체 양성 수가 분모다.',
 '산점도는 관측 쌍을 좌표평면 위 점으로 나타낸다.',
 '평균제곱오차는 각 오차를 제곱한 후 평균을 낸다. 예를 들어 오차 1, −1의 평균제곱오차는 1이다.',
 '경사하강법의 갱신식은 w′=w−ηL′(w)이다.',
 '비용까지 빼면 순위가 바뀔 수 있다. 편익 10, 비용 9의 순편익은 1이고, 편익 8, 비용 2의 순편익은 6이다.',
 '먼저 탐구 질문과 평가 기준을 정하고 비교 조건을 통제해야 결과를 해석할 수 있다.',
]


def main():
    source = ROOT/'data.json'
    rows = json.loads(source.read_text())
    notes = json.loads(Path(__file__).with_name('legacy_notes.json').read_text())
    for q in rows:
        number = q['no']
        body = q['q']
        if q['set']=='ox':
            q['exp'] = f'<p>{math(OX_REVIEW[number-1])}</p>'
            continue
        base = q['exp'].split(BASE_END)[0]
        if q['code'] in CORRECTIONS:
            old,new = CORRECTIONS[q['code']]
            base = base.replace(old,new)
        if number==4:
            body = body.replace('B·B와 81.5%','B·B와 82.5%')
        if number==24:
            base = '<div class="ex"><p>행을 w=1,2,3, 열을 t=1,2,3 순서로 두면 정답 건수는 (4,4,3), (3,3,3), (2,3,3)이다. 최대 4건을 맞힌 조합은 (1,1), (1,2) 두 개다.</p></div>'
        if number==60:
            base = '<div class="ex"><p>정확도 차이 B−A는 −3/100 + (x/100)×(2/15) − ((80−x)/100)×(1/25) = (13x−465)/7500이다. 따라서 x&gt;465/13이고 가능한 정수는 36부터 70까지 35개다.</p></div>'
        if number==52:
            old = '<span>'+math('6/16')+'</span>'
            body = body.replace(old,'<span>'+math('5/16')+'</span>').replace('<span>6/16</span>','<span>5/16</span>')
        q['q'] = math_html(body)
        q['exp'] = math_html(base)+''.join(f'<p class="aim-choice"><b>{mark}</b> {math(note)}</p>'
            for mark,note in zip('①②③④⑤',notes[number-1]))
    source.write_text('[\n'+',\n'.join(json.dumps(q,ensure_ascii=False,separators=(',',':')) for q in rows)+'\n]')
    path = ROOT/'concept.json'
    data = json.loads(path.read_text())
    for section in data['secs']:
        section['html'] = math_html(section['html'])
    for section in data['summary']:
        section['html'] = math_html(section['html'])
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
