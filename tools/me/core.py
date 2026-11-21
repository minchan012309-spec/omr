"""변형·유사 문항 생성 공통 도구."""
import random, itertools, math
from mk import p, box, bogi, table, fig, fmt

ITEMS = []          # 생성된 문항
GIY = 'ㄱㄴㄷㄹㅁ'
LV = ['하', '중', '상', '최']

def num(x, nd=2, sign=False):
    """숫자 → 문자열(불필요한 0 제거). 음수는 −."""
    if isinstance(x, float) and abs(x - round(x)) < 1e-9: x = round(x)
    if isinstance(x, int): s = str(abs(x))
    else:
        s = f'{abs(x):.{nd}f}'.rstrip('0').rstrip('.')
    if x < 0 and s != '0': return '−' + s
    return ('+' + s) if sign and x > 0 else s

def m(x, nd=2, sign=False):
    """수식용 숫자 문자열($ 안)."""
    return num(x, nd, sign).replace('−', '-')

def sci(x, nd=1):
    """과학적 표기 a×10^n (수식 문자열)."""
    if x == 0: return '0'
    e = math.floor(math.log10(abs(x)) + 1e-12); a = x / 10 ** e
    a = round(a, nd)
    if abs(a) >= 10: a /= 10; e += 1
    a_s = f'{a:.{nd}f}'
    return a_s if e == 0 else f'{a_s}\\times 10^{{{e}}}'

LAST = {}
def add(**kw):
    if kw.get('chk', {}).get('t') == 'one' and LAST.get('truth'):
        kw['chk']['truth'] = LAST.pop('truth')
    kw.setdefault('figs', []); kw.setdefault('key', ''); kw.setdefault('chl', None)
    assert kw['lv'] in LV, kw['lv']
    ITEMS.append(kw)
    return kw

def pick_numeric(rng, correct, cands, fmtf, n=5):
    """정답 + 오답 후보에서 서로 다른 5개(표시 문자열 기준)를 골라 오름차순 정렬. (선지 목록, 정답 번호) 반환."""
    seen = {fmtf(correct): correct}
    pool = [c for c in cands if c is not None]
    rng.shuffle(pool)
    for c in pool:
        s = fmtf(c)
        if s not in seen and (not isinstance(c, (int, float)) or abs(c - correct) > 1e-9):
            seen[s] = c
        if len(seen) >= n: break
    if len(seen) < n: return None, None
    items = sorted(seen.items(), key=lambda kv: kv[1])
    labels = [k for k, _ in items]
    return labels, labels.index(fmtf(correct)) + 1

def near(rng, x, k=8, rel=(0.25, 2.0)):
    out = [x * f for f in (0.5, 2, 1.5, 0.25, 4, 3, 1 / 3, 0.75, 1.25, 10, 0.1)]
    out += [-x, x + x * rng.choice([0.2, 0.3, 0.4]), x - x * rng.choice([0.2, 0.3])]
    return out

# ---------- ㄱㄴㄷ 조합 ----------
def combo_choices(rng, truth, k=None):
    """truth: 보기별 참/거짓 목록. 5개 선지(조합)와 정답 번호."""
    n = len(truth); L = GIY[:n]
    corr = tuple(L[i] for i in range(n) if truth[i])
    if not corr: return None, None
    allc = [c for r in range(1, n + 1) for c in itertools.combinations(L, r)]
    if n == 3:
        others = [c for c in allc if c != corr]
        rng.shuffle(others); sel = others[:4] + [corr]
    else:
        others = [c for c in allc if c != corr and len(c) <= 3]
        rng.shuffle(others); sel = others[:4] + [corr]
    sel = sorted(set(sel), key=lambda c: (len(c), [L.index(x) for x in c]))
    labels = [', '.join(c) for c in sel]
    return labels, labels.index(', '.join(corr)) + 1

def bogi_item(rng, stmts, nsel=3, need_true=1):
    """stmts: (문장, 참거짓, 해설) 목록에서 nsel개를 골라 보기와 풀이를 만든다."""
    for _ in range(40):
        s = rng.sample(stmts, nsel)
        t = [x[1] for x in s]
        if sum(t) >= need_true: break
    else:
        return None
    ch, ans = combo_choices(rng, t)
    if not ch: return None
    items = [f'{GIY[i]}. {x[0]}' for i, x in enumerate(s)]
    sol = [f'{GIY[i]}. {x[2]} {"옳다." if x[1] else "옳지 않다."}' for i, x in enumerate(s)]
    sol.append('따라서 옳은 것은 ' + ', '.join(GIY[i] for i in range(nsel) if t[i]) + '이다.')
    return dict(bogi=items, ch=ch, ans=ans, sol=sol, truth=t)

def one_of(rng, stmts, want=True):
    """옳은(want=True) 것 하나 + 반대 4개 → '옳은 것은?' / '옳지 않은 것은?'"""
    good = [x for x in stmts if x[1] == want]; bad = [x for x in stmts if x[1] != want]
    if not good or len(bad) < 4: return None
    s = [rng.choice(good)] + rng.sample(bad, 4)
    rng.shuffle(s)
    ans = [i for i, x in enumerate(s) if x[1] == want][0] + 1
    sol = [f'{"①②③④⑤"[i]} {x[2]} {"옳다." if x[1] else "옳지 않다."}' for i, x in enumerate(s)]
    LAST['truth'] = [x[1] for x in s]
    return dict(ch=[x[0] for x in s], ans=ans, sol=sol)

Q_BOGI = '이에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'

def ox_item(rng, stmts, n=4):
    """O/X 판단 서답형(하)."""
    s = rng.sample(stmts, n)
    body = [p('다음 설명으로 옳은 것은 O, 옳지 않은 것은 ×로 표시하시오.')] + [p(f'({i + 1}) {x[0]}') for i, x in enumerate(s)]
    ans = ' '.join(f'({i + 1}) {"O" if x[1] else "×"}' for i, x in enumerate(s))
    sol = [f'({i + 1}) {x[2]} ({"O" if x[1] else "×"})' for i, x in enumerate(s)]
    return body, ans, sol

def R(seed):
    return random.Random(seed)
