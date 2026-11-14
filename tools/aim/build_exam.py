"""Add individually authored exam questions using independent question IDs."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from explain import math

ROOT = Path(__file__).resolve().parents[2] / 'aim'
MARKS = '①②③④⑤'


def display(text):
    return math(re.sub(r'\{\{([^;]+);([^}]+)\}\}', r'{{\1|\2}}', text))


def add_exam_items(index, concept):
    by_title = {sec['title']:(i,sec) for i,sec in enumerate(concept['secs'],1)}
    questions = defaultdict(list)
    source = Path(__file__).with_name('exam_items.txt')
    for line in source.read_text().splitlines():
        if line.startswith('# '):
            topic, sec = by_title[line[2:]]
            continue
        lv, stem, key, choices, proof, reasons = line.split('|')
        choices, reasons = choices.split('~'), reasons.split('~')
        assert len(set(choices)) == len(reasons) == 5 and key in '12345'
        tag = f'aim{topic:02}4'
        no = len(questions[tag])+1
        code = f'G-{tag}-{no:04}'
        choice_html = ''.join(f'<div><b>{mark}</b><span>{display(choice)}</span></div>'
                              for mark,choice in zip(MARKS, choices))
        exp = f'<p>{display(proof)}</p>'+''.join(
            f'<p class="aim-choice"><b>{mark}</b> {display(reason)}</p>'
            for mark,reason in zip(MARKS,reasons))
        questions[tag].append(dict(code=code,no=no,set='mc',sub=sec['sub'],
            subname=concept['subs'][sec['sub']]['name'],type=sec['title'],lv=lv,fam=code,
            ans=key, authored=True,
            q=f'<div class="q"><div class="qh"><b class="qn">{no}</b></div><div class="qs"><p>{display(stem)}</p><div class="chs">{choice_html}</div></div></div>',
            exp=exp))
    for tag,items in questions.items():
        first = items[0]
        index[tag] = dict(label=first['type'],sub=first['sub'],subname=first['subname'],
            sec=int(tag[3:5]),set='mc',authored=True,n=len(items),lv=dict(Counter(q['lv'] for q in items)))
        (ROOT/(tag+'.json')).write_text(json.dumps(items,ensure_ascii=False,separators=(',',':'))+'\n')
