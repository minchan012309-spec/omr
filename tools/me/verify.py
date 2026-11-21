"""생성 문항 오류 검증. python3 tools/me/verify.py  (오류가 하나라도 있으면 종료 코드 1)"""
import sys, os, re, json, collections, html
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
import build, core, mk
from core import num, m

VOID = {'br', 'img', 'col', 'mspace', 'circle', 'line', 'polygon', 'path', 'hr'}
class Bal(HTMLParser):
    def __init__(s): super().__init__(); s.st = []; s.err = None
    def handle_starttag(s, t, a):
        if t not in VOID: s.st.append(t)
    def handle_startendtag(s, t, a): pass
    def handle_endtag(s, t):
        if t in VOID: return
        if not s.st or s.st[-1] != t: s.err = s.err or f'닫는 태그 불일치 </{t}> (열린 {s.st[-3:]})'; return
        s.st.pop()

def balanced(h):
    b = Bal(); b.feed(h); b.close()
    if b.err: return b.err
    if b.st: return f'닫히지 않은 태그 {b.st}'
    for mm in re.findall(r'<math.*?</math>', h, re.S):
        try: ET.fromstring(mm.replace('&nbsp;', ' '))
        except Exception as e: return f'MathML 오류 {e}: {mm[:80]}'
    return None

def plain(s): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', mk.fmt(s))).strip()

def main():
    files, index, dup, items = build.build(write=False)
    errs = collections.Counter(); samples = collections.defaultdict(list)
    def bad(kind, code, msg=''):
        errs[kind] += 1
        if len(samples[kind]) < 5: samples[kind].append(f'{code} {msg}')
    codes = set(); n = 0
    by_code = {}
    for tag, qs in files.items():
        for q in qs:
            n += 1
            if q['code'] in codes: bad('코드 중복', q['code'])
            codes.add(q['code'])
            for part in ('q', 'exp'):
                e = balanced(q[part])
                if e: bad('HTML 구조', q['code'], e)
                if re.search(r'\b(None|nan|inf)\b', re.sub(r'<[^>]+>', ' ', q[part])): bad('None/nan 노출', q['code'])
                if re.search(r'\$|\\frac|\\Delta|-&gt;', q[part]): bad('변환 안 된 표기', q['code'], re.search(r'.{0,30}(\$|\\frac|\\Delta|-&gt;).{0,30}', q[part]).group(0))
    # 문항 단위 검증(생성 정보 이용)
    for it in items:
        code = f"{it['typ']}/{it.get('ono')}"
        if it['kind'] != 'mc': continue
        ch = it['ch']; ans = it['ans']
        if not ch or len(ch) != 5: bad('선지 수', code, str(len(ch or []))); continue
        P = [plain(c) for c in ch]
        if len(set(P)) != 5: bad('선지 중복', code, ' | '.join(P))
        if it['hw'] == 'o':
            if isinstance(ans, str):
                if not all(1 <= int(a) <= 5 for a in ans.split(',')): bad('정답 범위', code)
            elif not 1 <= ans <= 5: bad('정답 범위', code)
            # 원본: 해설의 ㄱㄴㄷ 판정과 정답 조합 일치
            if isinstance(ans, int) and re.fullmatch(r'[ㄱㄴㄷㄹ](, [ㄱㄴㄷㄹ])*', ch[ans - 1]):
                ok = []
                for s_ in it['sol']:
                    mm = re.match(r'([ㄱㄴㄷㄹ](?:, [ㄱㄴㄷㄹ])*)\.', s_)
                    if not mm: continue
                    ls = [x.strip() for x in mm.group(1).split(',')]
                    tail = s_.rstrip()
                    if tail.endswith('옳지 않다.'): continue
                    if tail.endswith('옳다.'): ok += ls
                    elif '옳다, ' in tail or '옳다.' in tail: ok += ls[:1]
                if ok and ', '.join(sorted(set(ok), key='ㄱㄴㄷㄹ'.index)) != ch[ans - 1]:
                    bad('원본 해설-정답 불일치', f"{it['ono']}", f"해설 {sorted(set(ok))} / 정답 {ch[ans - 1]}")
            continue
        if not 1 <= ans <= 5: bad('정답 범위', code); continue
        c = it.get('chk', {}); t = c.get('t')
        A = P[ans - 1]
        if t == 'combo':
            tr = c['truth']; corr = ', '.join('ㄱㄴㄷㄹㅁ'[i] for i, x in enumerate(tr) if x)
            if A != corr: bad('보기 조합 정답 불일치', code, f'{A} ≠ {corr}')
            if sum(1 for x in P if x == corr) != 1: bad('정답 조합 유일성', code)
        elif t == 'one':
            tr = c.get('truth')
            if tr is None: bad('판정 정보 없음', code)
            else:
                good = [i for i, x in enumerate(tr) if x == c['want']]
                if good != [ans - 1]: bad('단일 정답 아님', code, str(tr))
        elif t in ('num', 'neut', 'pred', 'k'):
            v = c['v']
            nums = [float(x.replace('−', '-')) for x in re.findall(r'[−-]?\d+(?:\.\d+)?', A.split('×')[0])]
            if 'times 10' in str(ch[ans - 1]) or '×' in A:
                mant = re.findall(r'[−-]?\d+(?:\.\d+)?', A)
                try:
                    val = float(mant[0].replace('−', '-')) * 10 ** float(mant[2].replace('−', '-'))
                    if abs(val - v) > abs(v) * 0.06: bad('수치 정답 불일치', code, f'{A} vs {v}')
                except Exception: bad('수치 해석 실패', code, A)
            elif not nums or min(abs(x - v) for x in nums) > max(1e-6, abs(v) * 0.006): bad('수치 정답 불일치', code, f'{A} vs {v}')
        elif t == 'calor':
            r = round(c['sign'] * 4.2 * (c['W'] + c['w']) * c['dT'] / c['mol'] / 1000, 1)
            if abs(r - c['v']) > 0.051 or num(r, 2) not in A.replace('−', '−'): bad('열량계 재계산 불일치', code, f'{A} vs {r}')
        elif t == 'bomb':
            r = round(-(4.2 * c['W'] + c['C']) * c['dT'] / c['mol'] / 1000, 0)
            if abs(r - c['v']) > 0.5 or num(r, 0) not in A: bad('통열량계 재계산 불일치', code, f'{A} vs {r}')
        elif t == 'hess':
            r = round(sum(a * b for a, b in zip(c['coefs'], c['vals'])), 1)
            if abs(r - c['v']) > 0.051 or num(r, 1) + ' kJ' != A: bad('헤스 재계산 불일치', code, f'{A} vs {r}')
        elif t == 'bond':
            r = c['Eb'] - c['Ef']
            if r != c['v'] or num(r, 1) + ' kJ' != A: bad('결합 에너지 재계산 불일치', code, f'{A} vs {r}')
        elif t == 'form':
            if num(c['v'], 1) + ' kJ' != A: bad('생성 엔탈피 정답 불일치', code, A)
        elif t == 'mix':
            if abs(c['na'] * c['Ma'] + c['nb'] * c['Mb'] - c['mass']) > 1e-6 or abs(-c['ha'] * c['na'] - c['hb'] * c['nb'] - c['Q']) > 0.01: bad('혼합물 조건 불일치', code)
            if num(c['v'], 3) + ' g' != A: bad('혼합물 정답 불일치', code, A)
        elif t == 'stot':
            r = round(c['dS'] - c['dH'] * 1000 / c['T'], 1)
            if abs(r - c['v']) > 0.051 or not A.startswith(num(r, 1)) or (('비자발적' in A) != (r < 0)): bad('엔트로피 재계산 불일치', code, f'{A} vs {r}')
        elif t == 'thermo':
            want = f"ΔH={num(c['dh'], 1)}".replace('ΔH=', '')
            if want not in A.replace(' ', ''): bad('열화학 반응식 정답 불일치', code, A)
        elif t in ('expr', 'law', 'sym', 'tb', 'case', 'hs', 'signs', 'match', 'hlP'):
            pass  # 선택지 문자열을 생성기에서 직접 지정(구성상 일치)
        else:
            bad('검증 유형 없음', code, str(t))
    print(f'검사한 문항 {n}개 (원본 {sum(1 for i in items if i["hw"] == "o")}, 생성 {sum(1 for i in items if i["hw"] != "o")})')
    if not errs:
        print('오류 0건'); return 0
    for k, v in errs.most_common():
        print(f'[{k}] {v}건'); [print('   ', s) for s in samples[k]]
    return 1

if __name__ == '__main__':
    sys.exit(main())
