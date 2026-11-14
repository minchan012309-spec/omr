"""Math notation and individual choice explanations for AI mathematics."""
import re
from fractions import Fraction
from html import escape

FRACTION = re.compile(r'(?<![\d/])([−-]?\d+)/(\d+)(?![\d/])')
FORMULAE = {
    1:'E = 3(P − TP) + 2FP',
    2:'ŷ = 1[ax + by ≥ t], E = Σ 1[ŷ ≠ y]',
    3:'p = w × p갑 + (1 − w) × p을',
    4:'D = Σ |rᵢ − cᵢ|, rᵢ = fᵢ / Σf',
    5:'D = 1 − |A ∩ B| / |A ∪ B|',
    6:'E = |p(a − 2c) − nb|',
    7:'D = |(R + wG + B) / (w + 2) − T|',
    8:'I′ = min(255, I + s), D = |(I′₁₁ + I′₁₂) / 2 − T|',
    9:'D = Σ wᵢ × 1[xᵢ ≠ yᵢ]',
    10:'P(정상 | 양성) = FP / (TP + FP)',
    11:'E = |ax₁ + b − y₁| + |ax₂ + b − y₂|',
    12:'MSE = (e₁² + we₂² + e₃²) / (w + 2)',
    13:'Lₖ = u₀²(1 − 2η)²ᵏ + cv₀²(1 − 2cη)²ᵏ',
    14:'E = C − pB',
    15:'D = |(a₁ + a₂ + a₃) / 3 − T|',
}


def math(text):
    """Render unambiguous numeric fractions as accessible, dependency-free HTML."""
    safe = escape(str(text))
    def fraction(m):
        a,b = m.groups()
        return (f'<span class="mfrac" style="display:inline-grid;vertical-align:middle;text-align:center;line-height:1.05;margin-inline:.13em" role="math" aria-label="{a}/{b}">'
                f'<span style="border-bottom:1px solid currentColor;padding-inline:.15em">{a}</span><span>{b}</span></span>')
    return re.sub(r'\^(\d+)',r'<sup>\1</sup>',FRACTION.sub(fraction,safe)).replace('²ᵏ','<sup>2k</sup>')


def math_html(fragment):
    """Preserve existing HTML, including the literal pixel rows in SVG figures."""
    parts = re.split(r'(<figure\b.*?</figure>|<span class="mfrac".*?</span></span>|<[^>]+>)',fragment,flags=re.S)
    return ''.join(s if s.startswith('<') else FRACTION.sub(
        lambda m:math(m.group()),s).replace('²ᵏ','<sup>2k</sup>') for s in parts)


def choice_reason(value, answer, values, eligible, stem):
    labels = 'ABCDE'
    if isinstance(value,str):
        group = value.split('·')
        parts = [labels.index(c) for c in group]
        needs_filter = '만 남긴다' in stem
        if needs_filter and not all(eligible[i] for i in parts):
            excluded = '·'.join(labels[i] for i in parts if not eligible[i])
            return f'{excluded}는 제약을 충족하지 않아 이 선지는 제외한다.'
        if len(parts)==1:
            x = values[parts[0]]
            best = values[labels.index(answer)]
            return f'{value}의 평가값은 {x}이다. '+(
                '비교 대상 중 가장 작다.' if value==answer else f'{answer}의 평가값 {best}보다 크다.')
        i,j = parts
        if '평균이' in stem:
            target = re.search(r'평균이 ([−\d/-]+)',stem)[1].replace('−','-')
            distance = abs((Fraction(values[i])+values[j])/2-Fraction(target))
            result = f'{value} 평균과 목표 {target}의 차이는 {distance}이다.'
        else:
            distance = abs(values[i]-values[j])
            result = f'{value} 평가값 차이는 |{values[i]} − ({values[j]})| = {distance}이다.'
        return result+(' 가능한 쌍 중 가장 작다.' if value==answer else f'최소인 {answer}보다 크다.')
    if value == answer:
        return f'위 계산에서 얻은 결과는 {answer}이다. 이 선지가 정확하다.'
    if abs(value) < abs(answer) and value < answer:
        return f'계산 결과 {answer}보다 {answer-value} 작으므로 일치하지 않는다.'
    relation = '크다' if value > answer else '작다'
    return f'계산 결과는 {answer}이며, 이 선지의 값 {value}는 그보다 {abs(value-answer)} {relation}.'


def explanation(topic, stem, proof, values, eligible, model, opts=(), answer=None):
    core = f'<p><b>계산식</b> {math(FORMULAE[topic])}</p><p>{math(proof)}</p>'
    rows = ''.join(f'<p class="aim-choice"><b>{symbol}</b> {math(choice_reason(value,answer,values,eligible,stem))}</p>'
                   for symbol,value in zip('①②③④⑤',opts))
    return core+substitutions(topic,model,values)+rows


def substitutions(topic, model, values):
    """Show the intermediate arithmetic for each candidate in the published solution."""
    text, rows = model['rule'], model['rows']
    nums = lambda pattern: tuple(map(int,re.search(pattern,text).groups()))
    lines = []
    for label,row,value in zip('ABCDE',rows,values):
        match topic:
            case 1:
                p, = nums(r'실제 양성 (\d+)건')
                t,f = row
                work = f'3×({p}−{t}) + 2×{f}'
            case 2:
                a,b,t = row
                target = nums(r'목표는 \((\d), (\d), (\d), (\d)\)')
                pred = [int(z>=t) for z in (0,b,a,a+b)]
                work = f'출력 {tuple(pred)}, 목표 {target}, 불일치 수'
            case 3:
                a,b,_ = row
                w,v = nums(r'각각 (\d+)%, (\d+)%')
                work = f'{w}×({a}/500) + {v}×({b}/500)'
            case 4:
                ref = nums(r'벡터는 \((\d+), (\d+), (\d+), (\d+)\)')
                work = ' + '.join(f'|{a}/{sum(ref)} − {b}/{sum(row)}|' for a,b in zip(ref,row))
            case 5:
                ref = set(re.search(r'단어는 ([a-z, ]+)다',text)[1].split(', '))
                doc = set(row[0].split(', '))
                work = f'1 − {len(ref&doc)}/{len(ref|doc)}'
            case 6:
                p,n = nums(r'\+(\d+), 부정 단어에는 −(\d+)')
                a,b,c = row
                work = f'|{p}×({a}−2×{c})−{n}×{b}|'
            case 7:
                w,t = nums(r'\(R\+(\d+)G\+B\)/\d+다\. 평가값은 목표 밝기 (\d+)')
                a,b,c = row
                work = f'|({a}+{w}×{b}+{c})/{w+2} − {t}|'
            case 8:
                s,t = nums(r'픽셀에 (\d+)를 더하되 .* 목표 (\d+)의 차이')
                a,b,*_ = row
                work = f'|({min(255,a+s)}+{min(255,b+s)})/2 − {t}|'
            case 9:
                a,b,w = re.search(r'위쪽 행은 ([01]+), 아래쪽 행은 ([01]+)이다\..*?칸마다 (\d+)',text).groups()
                upper,lower = (sum(x!=y for x,y in zip(ref,candidate)) for ref,candidate in zip((a,b),row))
                work = f'{w}×{upper}+{lower}'
            case 10:
                a,b = row
                work = f'{b}/({a}+{b})'
            case 11:
                x,y,u,v = nums(r'관측점은 \((\d+), (\d+)\)와 \((\d+), (\d+)\)')
                a,b = row
                work = f'|{a}×{x}+{b}−{y}| + |{a}×{u}+{b}−{v}|'
            case 12:
                w, = nums(r'차례대로 1, (\d+), 1')
                a,b,c = row
                work = f'(({a})²+{w}×({b})²+({c})²)/{w+2}'
            case 13:
                u,v,c = nums(r'초기점은 \((\d+), (\d+)\), 손실은 u²\+(\d+)v²')
                m,k = row
                work = f'{u}²×(1−{m}/8)^{2*k} + {c}×{v}²×(1−{c*m}/8)^{2*k}'
            case 14:
                c,p,b = row
                work = f'{c} − ({p}/10)×{b}'
            case 15:
                t, = nums(r'목표 정확도는 (\d+)%')
                a,b,c = row
                work = f'|({a}+{b}+{c})/3 − {t}|'
        lines.append(f'<p class="aim-work"><b>{label}</b> {math(work)} = {math(value)}</p>')
    return ''.join(lines)
