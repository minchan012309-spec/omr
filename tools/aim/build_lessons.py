"""Update the concept lessons from the reviewed, textbook-aligned authoring text."""
import json
from pathlib import Path

from explain import math, math_html
from rewrite_models import TYPES

ROOT = Path(__file__).resolve().parents[2]


def main():
    source = Path(__file__).with_name('lesson_body.txt')
    path = ROOT / 'aim' / 'concept.json'
    data = json.loads(path.read_text())
    chapters = {}
    for line in source.read_text().splitlines():
        if line.startswith('# '):
            body = chapters.setdefault(line[2:], [])
        elif line.startswith('## '):
            body.append(f'<h4>{math(line[3:])}</h4>')
        elif line:
            body.append(f'<p>{math(line)}</p>')
    assert set(chapters) == {sec['title'] for sec in data['secs']}
    for topic,sec in enumerate(data['secs'],1):
        sec['types'] = [label for parent,label in TYPES if parent==topic]
        sec['html'] = ''.join(chapters[sec['title']])
        sec['bankTags'].pop('blank',None)
    for summary in data['summary']:
        summary['html'] = math_html(summary['html'])
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
