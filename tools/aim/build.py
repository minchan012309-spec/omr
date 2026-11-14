"""Rebuild the type-sharded AI mathematics bank with stable question IDs."""
import json
import random
import re
from collections import Counter
from fractions import Fraction
from html import escape
from itertools import combinations
from pathlib import Path

from problems import scenario
from build_exam import add_exam_items
from build_rewrite import add_rewrite
from explain import explanation, math

ROOT = Path(__file__).resolve().parents[2] / 'aim'
LABELS = 'ABCDE'
LEVELS = ('하', '중', '상', '최')
COUNTS = {'mc': 672, 'ox': 144, 'blank': 144}


def number(value, unit=''):
    if isinstance(value, Fraction) and value.denominator != 1:
        return f'{value.numerator}/{value.denominator}{unit}'
    return f'{value}{unit}'


def figure(s, labels):
    def pixel(row):
        cells = ''.join(
            f'<rect x="{i%4*10}" y="{i//4*10}" width="10" height="10" fill="{("#253646" if bit=="1" else "#fff")}" stroke="#68717c"/>'
            for i, bit in enumerate(''.join(row)))
        return (f'<svg width="41" height="21" viewBox="-.5 -.5 41 21" role="img" '
                f'aria-label="{row[0]} / {row[1]}">{cells}</svg>')

    cells = ''.join(f'<th scope="col">{h}</th>' for h in (('이진 영상',) if s.pixels else s.headers))
    rows = ''.join(f'<tr><th scope="row">{label}</th>' +
                   (f'<td>{pixel(row)}<br>{row[0]} / {row[1]}</td>' if s.pixels else
                    ''.join(f'<td>{escape(str(v))}</td>' for v in row)) +
                   '</tr>' for label, row in zip(labels, s.rows))
    return ('<figure class="fg" style="margin:4px 0;overflow-x:auto">'
            '<table border="1" cellpadding="2" style="border-collapse:collapse;width:100%;font-size:.85em;text-align:center">'
            f'<caption>후보별 자료</caption><thead><tr><th scope="col">후보</th>{cells}</tr></thead>'
            f'<tbody>{rows}</tbody></table></figure>')


def compose(s, level, kind, variant, rng):
    """Return a stem, exact answer, worked solution, and any direct distractors."""
    a = s.values
    ok = s.eligible
    labels = LABELS[:len(a)]
    chosen = rng.randrange(len(a))
    label = labels[chosen]
    values = ', '.join(f'{c} {number(x,s.unit)}' for c, x in zip(labels,a))
    detail = f'후보별 평가값은 {values}이다.'
    passers = [i for i, yes in enumerate(ok) if yes]
    eligible = '·'.join(labels[i] for i in passers) or '없음'
    if kind == 'ox':
        truth = variant % 2 == 0
        match variant % 3:
            case 0:
                claim = a[chosen] if truth else a[chosen]+rng.choice([1,2,3])
                question = f'{label}의 평가값은 {number(claim,s.unit)}이다.'
                proof = f'{label}의 평가값은 {number(a[chosen],s.unit)}이다.'
            case 1:
                i,j = rng.sample(range(len(a)),2)
                if a[i] == a[j]:
                    return None
                first,second = sorted((i,j),key=lambda k:a[k],reverse=not truth)
                question = f'{labels[first]}의 평가값은 {labels[second]}보다 작다.'
                proof = f'{labels[first]}는 {number(a[first],s.unit)}, {labels[second]}는 {number(a[second],s.unit)}이다.'
            case _:
                n = len(passers) if truth else (len(passers)+1)%(len(a)+1)
                question = f'{s.constraint}의 수는 {n}개다.'
                proof = f'조건을 만족하는 후보는 {eligible}이며 모두 {len(passers)}개다.'
        return question, ('O' if truth else 'X'), proof, []
    if kind == 'blank':
        if variant % 3 == 0:
            return f'{label}의 평가값을 구하시오. 단위 없이 기약분수 또는 정수로 쓴다.', number(a[chosen]), detail, []
        if variant % 3 == 1:
            return '평가값의 최댓값과 최솟값의 차를 구하시오. 단위 없이 기약분수 또는 정수로 쓴다.', number(max(a)-min(a)), detail, []
        return f'{s.constraint}의 개수를 구하시오.', str(len(passers)), f'조건을 만족한 후보는 {eligible}이다.', []
    if level == '하':
        if variant % 2 == 0:
            return f'{label}의 평가값은?', a[chosen], detail, [v for i,v in enumerate(a) if i != chosen]
        return f'다음 조건에 해당하는 후보는 몇 개인가? 조건: {s.constraint}.', len(passers), f'조건을 만족한 후보는 {eligible}이다.', list(range(len(a)+1))
    if level == '중':
        if variant % 2 == 0:
            i,j = rng.sample(range(len(a)),2)
            return f'{labels[i]}와 {labels[j]}의 평가값 차이의 절댓값은?', abs(a[i]-a[j]), detail, []
        if a.count(min(a)) != 1:
            return None
        return '평가값이 가장 작은 후보는?', labels[a.index(min(a))], detail, list(LABELS)
    if len(passers) < 2:
        return None
    condition = f'다음 조건에 해당하는 후보만 남긴다. 조건: {s.constraint}.'
    if level == '상':
        if variant % 2 == 0:
            best = min(a[i] for i in passers)
            winners = [i for i in passers if a[i]==best]
            if len(winners) != 1:
                return None
            return f'{condition} 그중 평가값이 최소인 후보는?', labels[winners[0]], f'남는 후보는 {eligible}이다. {detail}', list(LABELS)
        total = sum(a[i] for i in passers)
        return f'{condition} 남은 후보의 평가값 합은?', total, f'남는 후보는 {eligible}이다. {detail}', [sum(a), min(a), max(a), Fraction(total,len(passers))]
    pairs = list(combinations(passers,2))
    all_pairs = list(combinations(range(len(a)),2))
    if variant % 4 == 0:
        if len(pairs) < 3:
            return None
        scores = [(abs(a[i]-a[j]), i, j) for i,j in pairs]
        scores.sort()
        if scores[0][0] == scores[1][0]:
            return None
        _,i,j = scores[0]
        answer = labels[i]+'·'+labels[j]
        return f'{condition} 남은 후보 중 두 개를 고른다. 평가값 차이의 절댓값이 가장 작은 쌍은?', answer, f'남는 후보는 {eligible}이다. {detail} 최소 차이는 {number(scores[0][0],s.unit)}이다.', [labels[i]+'·'+labels[j] for i,j in all_pairs]
    if variant % 4 == 1:
        threshold = a[chosen]+a[(chosen+1)%len(a)]
        count = sum(a[i]+a[j]<=threshold for i,j in pairs)
        if not 0 < count < len(pairs):
            return None
        return f'{condition} 평가값 합이 {number(threshold,s.unit)} 이하인 서로 다른 후보의 쌍은 몇 개인가? 순서는 세지 않는다.', count, f'남는 후보는 {eligible}이다. {detail} 이들로 만든 {len(pairs)}쌍의 합을 비교하면 {count}쌍이다.', list(range(11))
    if variant % 4 == 2:
        triples = list(combinations(passers,3))
        if len(triples) < 4:
            return None
        target = sum(a[i] for i in rng.sample(range(len(a)),3))
        # Require every possible three-candidate selection to be considered at the threshold.
        passing = ['·'.join(labels[i] for i in t) for t in triples if sum(a[i] for i in t)<target]
        if not 0 < len(passing) < len(triples):
            return None
        return (f'{condition} 평가값 합이 {number(target,s.unit)} 미만인 세 후보 조합은 몇 개인가?',
                len(passing), f'남는 후보는 {eligible}이다. {detail} 조건을 만족하는 조합은 {", ".join(passing)}이다.',
                list(range(len(triples)+1)))
    target = Fraction(a[chosen]+a[(chosen+1)%len(a)],2)
    scores = sorted((abs(Fraction(a[i]+a[j],2)-target), i, j) for i,j in pairs)
    if len(scores) < 3 or scores[0][0] == scores[1][0]:
        return None
    _,i,j = scores[0]
    return f'{condition} 남은 후보 중 두 개를 고른다. 두 평가값의 평균이 {number(target,s.unit)}에 가장 가까운 쌍은?', labels[i]+'·'+labels[j], f'남는 후보는 {eligible}이다. {detail} 각 쌍의 평균을 비교하면 {labels[i]}·{labels[j]}의 차이가 {number(scores[0][0],s.unit)}로 가장 작다.', [labels[i]+'·'+labels[j] for i,j in all_pairs]


def write(path, data):
    path.write_text('[\n'+',\n'.join(json.dumps(q, ensure_ascii=False, separators=(',',':')) for q in data)+'\n]\n')


def main():
    concept = json.loads((ROOT/'concept.json').read_text())
    index = {}
    for topic, sec in enumerate(concept['secs'],1):
        for suffix, kind in enumerate(COUNTS,1):
            tag = f'aim{topic:02}{suffix}'
            rng = random.Random(420260000+topic*10+suffix)
            seen = set()
            questions = []
            for no in range(1, COUNTS[kind]+1):
                level = LEVELS[(no-1)//168] if kind == 'mc' else LEVELS[(no-1)//48]
                while True:
                    s = scenario(topic,rng)
                    if len(set(s.rows)) != len(s.rows):
                        continue
                    hit = compose(s,level,kind,no,rng)
                    if hit is None:
                        continue
                    stem, answer, exp, foils = hit
                    rule = s.metric
                    if topic == 7:
                        rule = re.sub(r'\(R\+(\d+)G\+B\)/(\d+)',r'{{R+\1G+B|\2}}',rule)
                    body = figure(s,LABELS[:len(s.rows)]) + '<p>'+math(rule)+'</p><p>'+math(stem)+'</p>'
                    if body not in seen:
                        break
                seen.add(body)
                code = f'G-{tag}-{no:04}'
                q = dict(code=code,no=no,set=kind,sub=sec['sub'],subname=concept['subs'][sec['sub']]['name'],
                    type=sec['title'],lv=level,fam=f'{tag}-{level}-{no%(4 if level=='최' else 3 if kind!='mc' else 2)}')
                choices = ''
                opts = []
                if kind == 'mc':
                    unit = s.unit if '평가값' in stem and '몇 개' not in stem and isinstance(answer,(int,Fraction)) else ''
                    # Use nearby exact values or competing candidates rather than duplicate choices.
                    pool = [x for x in dict.fromkeys(foils) if x != answer]
                    if isinstance(answer,(int,Fraction)):
                        step = Fraction(1, answer.denominator) if isinstance(answer,Fraction) else 1
                        extras = [answer+step*d for d in (-4,-3,-2,-1,1,2,3,4,5,6)]
                        if answer >= 0:
                            extras = [x for x in extras if x >= 0]
                        pool += [x for x in extras if x not in pool and x != answer]
                    opts = rng.sample(pool[:max(4,len(foils))],4)
                    pos = (no-1+topic)%5
                    opts.insert(pos,answer)
                    q['ans'] = str(pos+1)
                    choices = '<div class="chs">' + ''.join(
                        f'<div><b>{symbol}</b><span>{math(number(value,unit))}</span></div>'
                        for symbol,value in zip('①②③④⑤',opts)) + '</div>'
                else:
                    q['ans'] = answer
                    if kind == 'blank':
                        body += ' 답: <span class="bk"></span>'
                        q['blanks'] = [answer]
                q['model'] = {'rows':s.rows,'rule':s.metric,'constraint':s.constraint,'stem':stem}
                q['exp'] = explanation(topic,stem,exp,s.values,s.eligible,q['model'],opts,answer)
                q['q'] = f'<div class="q"><div class="qh"><b class="qn">{no}</b></div><div class="qs">{body}{choices}</div></div>'
                questions.append(q)
            index[tag] = dict(label=sec['title'],sub=sec['sub'],subname=questions[0]['subname'],
                sec=topic,set=kind,n=len(questions),lv=dict(Counter(q['lv'] for q in questions)))
            write(ROOT/(tag+'.json'),questions)
    add_exam_items(index,concept)
    add_rewrite(index,concept)
    (ROOT/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')


if __name__ == '__main__':
    main()
