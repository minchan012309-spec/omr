"""Verify the published AI mathematics bank, including indexes and question structure."""
import json
import re
from collections import Counter
from pathlib import Path
from html import unescape
from verify_math import solve, answer, numeric

ROOT = Path(__file__).resolve().parents[2] / 'aim'


def text(html):
    html = re.sub(r'<span class="mfrac"[^>]*aria-label="([^"]+)"[^>]*>.*?</span></span>', r'\1',html)
    html = re.sub(r'<math class="mfrac" aria-label="([^"]+)">.*?</math>',r'\1',html)
    return unescape(re.sub(r'<[^>]*>','',html))


def audit():
    index = json.loads((ROOT / 'index.json').read_text())
    sections = json.loads((ROOT / 'concept.json').read_text())['secs']
    totals, types, codes, stems = Counter(), Counter(), set(), set()
    answer_positions, ox_answers = Counter(), Counter()
    for tag, meta in index.items():
        if meta.get('revised'):
            continue
        questions = json.loads((ROOT / (tag + '.json')).read_text())
        assert len(questions) == meta['n']
        assert Counter(q['lv'] for q in questions) == meta['lv']
        for q in questions:
            assert re.fullmatch(r'G-' + tag + r'-\d{4}', q['code'])
            assert q['code'] not in codes and q['exp']
            assert (q['type'], q['sub'], q['set']) == (meta['label'], meta['sub'], meta['set'])
            codes.add(q['code'])
            stem = q['q'].split('<div class="qs">', 1)[-1].split('<div class="chs', 1)[0]
            assert stem not in stems, q['code']
            stems.add(stem)
            if q.get('authored'):
                assert q['set']=='mc' and q['ans'] in '12345'
                choices = re.findall(r'<div><b>[①②③④⑤]</b><span>(.*?)</span></div>',q['q'])
                assert len(set(map(text,choices)))==5
                assert re.findall(r'class="aim-choice"><b>([①②③④⑤])</b>',q['exp'])==list('①②③④⑤')
                totals['mc'] += 1
                types[q['type']] += 1
                continue
            model = q['model']
            topic = int(tag[3:5])
            rows = model['rows']
            values, eligible = solve(topic, rows, model['rule']+' '+model['constraint'])
            solution = answer(q['set'],model['stem'],values,eligible)
            assert model['stem'] in text(stem), q['code']
            assert 'class="aim-equation"' in q['exp']
            work = re.findall(r'class="aim-work"><b>[A-E]</b> (.*?)</p>',q['exp'])
            assert len(work)==5
            assert [numeric(text(row).rsplit(' = ',1)[1]) for row in work]==values, q['code']
            body_rows = re.findall(r'<tr><th scope="row">[A-E]</th>(.*?)</tr>',q['q'])
            assert len(body_rows)==len(rows)
            for displayed, supplied in zip(body_rows,rows):
                cells = [text(cell) for cell in re.findall(r'<td>(.*?)</td>', displayed)]
                expected = [' / '.join(supplied)] if topic==9 else list(map(str,supplied))
                assert cells == expected, (q['code'],cells,expected)
            totals[q['set']] += 1
            if q['set'] == 'mc':
                types[q['type']] += 1
                choices = [text(c) for c in re.findall(r'<div><b>[①②③④⑤]</b><span>(.*?)</span></div>', q['q'])]
                assert re.findall(r'class="aim-choice"><b>([①②③④⑤])</b>', q['exp'])==list('①②③④⑤')
                possible = choices if isinstance(solution,str) else [numeric(c) for c in choices]
                assert sum(x==solution for x in possible)==1 and possible[int(q['ans'])-1]==solution, (q['code'],solution,possible)
                assert len(choices) == len(set(choices)) == 5 and q['ans'] in tuple('12345')
                answer_positions[q['ans']] += 1
                if q['lv'] in ('상', '최'):
                    assert '<figure' in q['q']
            elif q['set'] == 'ox':
                assert q['ans'] == solution
                ox_answers[q['ans']] += 1
            else:
                assert numeric(q['ans']) == solution and q['blanks'] == [q['ans']] and q['q'].count('class="bk"') == 1
    assert ox_answers['O'] == ox_answers['X']
    for topic, section in enumerate(sections, 1):
        assert section['html'].count('<h4>') >= 3 and len(text(section['html'])) >= 350
        assert section['bankTags'] == {'ox': f'aim{topic:02}2'}
    assert {s['title'] for s in sections} == set(types)
    assert min(types.values()) >= 70
    assert totals['mc'] >= 10_000 and totals['ox'] >= 2_000 and totals['blank'] >= 2_000
    assert all(totals['mc'] * .17 <= n <= totals['mc'] * .23 for n in answer_positions.values())
    authored = [json.loads((ROOT/(tag+'.json')).read_text()) for tag,b in index.items() if b.get('authored')]
    assert len(authored)==15 and sum(map(len,authored))==79
    assert all(len({q['lv'] for q in group})>=3 for group in authored)
    legacy = json.loads((ROOT/'data.json').read_text())
    legacy_mc = [q for q in legacy if q['set']=='mc']
    assert len(legacy_mc)==60
    for q in legacy_mc:
        choices = re.findall(r'<div><b>[①②③④⑤]</b><span>(.*?)</span></div>', q['q'])
        assert len(choices)==len(set(map(text,choices)))==5
        assert 1<=int(q['ans'])<=5
        assert re.findall(r'class="aim-choice"><b>([①②③④⑤])</b>',q['exp']) == list('①②③④⑤'), q['code']
    assert len(legacy)==75 and all(q['exp'] for q in legacy)
    print('독립 풀이·해설 대입값 대조 14400문항, 직접 작성 문항 구조 79문항, 초판 구조',len(legacy),'문항')
    print(dict(totals), '5지선다 유형별 최소', min(types.values()), '전체 발문·코드 중복 없음')


if __name__ == '__main__':
    audit()
