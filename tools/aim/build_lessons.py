"""Update the concept lessons from the reviewed, textbook-aligned authoring text."""
import json
import re
from pathlib import Path
from itertools import groupby

from explain import equation, inline_equation, math
from rewrite_models import TYPES

ROOT = Path(__file__).resolve().parents[2]


def inline(text):
    return ''.join(inline_equation(part, rich=True) if i % 2 else math(part)
                   for i, part in enumerate(re.split(r'`([^`]+)`', text)))


def render(lines):
    for marker, group in groupby(lines, key=lambda line: line.split(' ', 1)[0]):
        entries = [line.split(' ', 1)[1] for line in group]
        if marker == '##':
            yield from (f'<h4>{inline(entry)}</h4>' for entry in entries)
        elif marker == '=':
            yield from (f'<div class="eqn aim-concept-formula">{equation(entry, rich=True)}</div>' for entry in entries)
        elif marker in ('-', '+', '!', '?'):
            items = ''.join(f'<li>{inline(entry)}</li>' for entry in entries)
            if marker == '+':
                yield f'<div class="ex"><span class="elb">풀이 예제</span><ol class="st">{items}</ol></div>'
            elif marker == '!':
                yield f'<div class="nt wa"><span class="lb">혼동 주의</span><ul class="l">{items}</ul></div>'
            elif marker == '?':
                yield f'<div class="nt ds"><span class="lb">시험 포인트</span><ul class="l">{items}</ul></div>'
            else:
                yield f'<ul class="l">{items}</ul>'
        elif marker == '|':
            rows = [entry.split(' :: ') for entry in entries]
            assert len(rows) >= 2 and all(len(row) == len(rows[0]) for row in rows)
            head = ''.join(f'<th scope="col">{inline(cell)}</th>' for cell in rows[0])
            body = ''.join('<tr>'+''.join(
                f'<td><b>{cell}</b></td>' if re.fullmatch(r'[A-Z]{2,5}', cell)
                else f'<td>{inline(cell)}</td>' for cell in row)+'</tr>'
                           for row in rows[1:])
            yield f'<table class="tb aim-concept-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
        else:
            raise ValueError(f'Unexpected lesson marker: {marker}')


def read_topics(name):
    chapters = {}
    source = Path(__file__).with_name(name)
    for line in source.read_text().splitlines():
        if line.startswith('# '):
            body = chapters.setdefault(line[2:], [])
        elif line:
            body.append(line)
    return chapters


def main():
    path = ROOT / 'aim' / 'concept.json'
    data = json.loads(path.read_text())
    chapters = read_topics('lesson_body.txt')
    assert set(chapters) == {sec['title'] for sec in data['secs']}
    for topic,sec in enumerate(data['secs'],1):
        sec['types'] = [label for parent,label in TYPES if parent==topic]
        sec['html'] = ''.join(render(chapters[sec['title']]))
        sec['bankTags'].pop('blank',None)
    summaries = read_topics('lesson_summary.txt')
    assert set(summaries) == {item['title'] for item in data['summary']}
    for summary in data['summary']:
        summary['html'] = ''.join(render(summaries[summary['title']]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
