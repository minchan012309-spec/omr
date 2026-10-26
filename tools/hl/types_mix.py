# -*- coding: utf-8 -*-
"""종합(융합) 유형 (hl083~hl086): 화법 자료 속 문법 · 맞춤법, 문법 요소 복합, 맞춤법 복합"""
import itertools
from hllib import *
from speech_gen import ff
from qlib import *
import kb_speech as S
import kb_orth1 as O1, kb_orth2 as O2, kb_orth3 as O3

# ------------------------------------------------------------------ hl083 화법과 문법의 융합
GM = {
 'sh': ('주어를 높이는 주체 높임 표현이 쓰였다.', '선생님께서 {n}에 대해 말씀하셨습니다.'),
 'oh': ('특수 어휘와 조사를 사용한 객체 높임 표현이 쓰였다.', '저는 선생님께 {n}에 대해 여쭈었습니다.'),
 'ps': ('접미사 "-되-"가 결합한 피동 표현이 쓰였다.', '{n}의 문제가 점차 해결되고 있습니다.'),
 'cs': ('"-게 하다"를 사용한 통사적 사동 표현이 쓰였다.', '학생회장은 친구들에게 {n}에 관한 규칙을 지키게 했습니다.'),
 'rc': ('관형사절을 안은문장이 쓰였다.', '학생들이 참여한 설문 조사가 {n}의 현황을 잘 나타냅니다.'),
 'qt': ('인용절을 안은문장이 쓰였다.', '친구는 "{n}은(는) 중요하다"고 말했습니다.'),
 'ng': ('"못"을 사용한 부정 표현이 쓰였다.', '저는 {n}의 효과를 아직 확인하지 못했습니다.'),
 'fu': ('미래의 일을 나타내는 "-겠-"이 쓰였다.', '다음 주부터 {n}에 대해 실천하겠습니다.'),
}
GM_EXTRA = ['부정 부사 "안"을 사용한 짧은 부정문이 쓰였다.', '접미사 "-이-"가 결합한 파생적 사동 표현이 쓰였다.', '서술절을 안은문장이 쓰였다.', '대등하게 이어진문장이 쓰였다.']

@T('hl083')
def g083(r, k):
    tp = r.choice(S.TOPICS)
    mode = r.choice(['one', 'not5', 'ok5', 'not5'])
    ids = list(GM); r.shuffle(ids)
    turns = [('발표자', ff(GM[i][1], tp), i) for i in ids]
    descs = {i: GM[i][0] for i in GM}
    q = {'one': '㉠에 쓰인 문법 요소에 대한 설명으로 가장 적절한 것은?', 'not5': '발표자의 말 ㉠~㉤에 대한 설명으로 적절하지 않은 것은?', 'ok5': '발표자의 말 ㉠~㉤에 대한 설명으로 적절한 것은?'}[mode]
    return lab_item(r, turns, descs, intro='다음은 학생의 발표 내용의 일부이다. ' + q, mode=mode, extra=GM_EXTRA, ref=[1],
                    core='높임 · 피동 · 사동 · 안은문장 · 부정 · 시제 표현의 판별', lv='상' if mode != 'one' else '중', fam='A' + mode, title='발표')


# ------------------------------------------------------------------ hl084 화법과 맞춤법의 융합
NOUN_BANKS = ('DUUM_HEAD', 'RYUL_Y', 'RYUL_N', 'RYEOL_Y', 'NOUN_EUM', 'GAP', 'SAI_N')
# 틀린 표기가 그 자체로 실제 단어여서 문맥 없이는 오해될 수 있는 것은 뺀다
REAL_OK = {'기차간', '전세방', '전셋방'}   # 사전·규정에서 사이시옷 표기가 갈리거나 예외(찻간 등)와 겹쳐 시비가 생기는 것
REAL = {'특이', '속이', '급이', '딱이', '족이', '극이', '조름', '아래집', '해수', '배길', '회배', '후날', '고간', '세방', '수자', '차간', '퇴간', '가외일', '피기', '이몸', '위집', '차집', '터세', '자리세', '모자리', '코구멍', '제사날', '해살', '내물', '비물', '매돌', '초불', '초국', '해볕'}
ADV_BANKS = ('IHI_I', 'IHI_H', 'BUSA_Y', 'BUSA_B', 'HAGERI_Y')
SRC = []
def _grab(nm):
    return getattr(O1, nm, None) or getattr(O2, nm, None) or getattr(O3, nm, None)
for nm in NOUN_BANKS + ADV_BANKS:
    for ok, bads, why in _grab(nm):
        if bads[0] not in REAL and ok not in REAL_OK: SRC.append((ok, bads[0], why, nm))
for e in O3.SAI_Y:
    if e['bad'] not in REAL and e['ok'] not in REAL_OK: SRC.append((e['ok'], e['bad'], '사이시옷을 받쳐 적는 합성어이다(제30항).', 'SAI_Y'))
FRAME = ['저희 모둠은 {w}에 주목했습니다.', '조사 결과에서 {w}이(가) 가장 눈에 띄었습니다.', '발표 자료에 {w}을(를) 따로 표시해 두었습니다.', '이 점에서 {w}은(는) 중요한 단서가 됩니다.', '오늘 발표에서는 {w}을(를) 짚어 보겠습니다.']
FRAME_ADV = ['발표문에서 "{w}"(이)란 부사를 사용했습니다.', '이 문장에서는 "{w}"(이)란 부사가 쓰였습니다.', '발표 자료에 "{w}"(이)란 부사를 따로 표시해 두었습니다.']
FRAME_VB = ['"{w}"(이)란 낱말의 쓰임을 짚어 보겠습니다.', '이 점에서 "{w}"(이)란 낱말은 중요한 단서가 됩니다.', '조사 결과에서 "{w}"(이)란 낱말이 가장 눈에 띄었습니다.']
NOUN_IN_ADV = {'오뚝이', '오뚜기'}   # BUSA_B 에 섞여 있는 명사

def frame_text(r, ent):
    """표제어 종류(명사·부사·용언)에 맞는 문장 틀로 ent 의 틀린 표기를 넣은 문장을 만든다."""
    ok, bad, why, nm = ent[:4]
    if (nm in ADV_BANKS and nm != 'HAGERI_Y' and ok not in NOUN_IN_ADV) or ok == '삐죽이': fr = r.choice(FRAME_ADV)   # HAGERI_Y 는 대부분 명사
    elif ok.endswith('다'): fr = r.choice(FRAME_VB)
    else: fr = r.choice(FRAME)
    return josa(fr.format(w=bad))

def _clean(w): return w.replace(' ', '') if False else w

@T('hl084')
def g084(r, k):
    ent = r.sample(SRC, 5)
    if len({e[3] for e in ent}) < 4: return None
    labs = '㉠㉡㉢㉣㉤'
    lines = []
    for i, (ok, bad, why, nm) in enumerate(ent):
        lines.append('%s<u>%s</u>' % (labs[i], frame_text(r, (ok, bad, why, nm))))
    box = '<div class="bogi"><div class="bt">발표 원고</div><p>%s</p></div>' % ' '.join(lines)
    mode = r.choice(['not', 'ok'])
    badi = r.randrange(5)
    opts, st = [], []
    for i, (ok, bad, why, nm) in enumerate(ent):
        wrong_fix = (mode == 'not' and i == badi) or (mode == 'ok' and i != badi)
        if wrong_fix:
            opts.append('%s: "%s"은(는) 맞는 표기이므로 고치지 않고 그대로 둔다.' % (labs[i], bad))
            st.append('%s: 바른 표기는 "%s"이다. %s' % (labs[i], ok, why))
        else:
            opts.append('%s: "%s"을(를) "%s"(으)로 고쳐 쓴다.' % (labs[i], bad, ok))
            st.append('%s: "%s"(으)로 고치는 것이 맞다. %s' % (labs[i], ok, why))
    right = opts[badi]; ws = [o for i, o in enumerate(opts) if i != badi]
    ask = '㉠~㉤을 바르게 고쳐 쓴 것으로 적절하지 않은 것은?' if mode == 'not' else '㉠~㉤을 바르게 고쳐 쓴 것으로 적절한 것은?'
    return mc(P('다음은 학생이 쓴 발표 원고이다. ' + ask) + box, right, ws, steps=[st[badi]] + [s for i, s in enumerate(st) if i != badi][:2], core='한글 맞춤법의 여러 조항 적용', lv='상' if mode == 'ok' else '최', fam='B' + mode, r=r, ref=[1], vertical=True)


# ------------------------------------------------------------------ hl085 문법 요소 복합
FEATS = ['주체 높임', '객체 높임', '피동', '사동', '부정', '관형사절', '인용절', '진행상', '미래 시제']
SENT = [
 ('선생님께서 우리를 부르셨다.', {'주체 높임'}), ('나는 선생님께 책을 드렸다.', {'객체 높임'}), ('도둑이 경찰에게 잡혔다.', {'피동'}), ('어머니께서 아이에게 옷을 입히셨다.', {'주체 높임', '사동'}),
 ('철수가 숙제를 하지 못했다.', {'부정'}), ('내가 어제 읽은 책이 재미있다.', {'관형사절'}), ('그는 내일 떠나겠다고 말했다.', {'인용절', '미래 시제'}), ('동생이 방에서 책을 읽고 있다.', {'진행상'}),
 ('할머니께서 마당에서 꽃을 가꾸고 계신다.', {'주체 높임', '진행상'}), ('나는 할아버지를 모시고 병원에 갔다.', {'객체 높임'}), ('그가 보낸 편지가 도착하지 않았다.', {'관형사절', '부정'}),
 ('선생님께서는 학생들이 제출한 보고서를 읽으셨다.', {'주체 높임', '관형사절'}), ('동생이 형에게 책을 읽게 했다.', {'사동'}), ('문이 바람에 열렸다.', {'피동'}), ('철수는 학교에 가지 않았다.', {'부정'}),
 ('내일은 비가 오겠다.', {'미래 시제'}), ('아버지께서 어머니께 선물을 드리셨다.', {'주체 높임', '객체 높임'}), ('아이들이 선생님께 꽃을 드리고 있다.', {'객체 높임', '진행상'}), ('동생은 언니가 사 준 책을 읽고 있다.', {'관형사절', '진행상'}),
 ('어머니는 아이에게 우유를 먹이셨다.', {'주체 높임', '사동'}), ('경찰이 도둑을 잡았다고 신문에 났다.', {'인용절'}), ('선생님께서 "내일 시험을 보겠다"고 말씀하셨다.', {'주체 높임', '인용절', '미래 시제'}), ('동생이 공을 던지게 했다.', {'사동'}),
 ('그는 아직 결정하지 못했다.', {'부정'}), ('우리가 만든 포스터가 벽에 걸렸다.', {'관형사절', '피동'}),
]

@T('hl085')
def g085(r, k):
    a, b = r.sample(FEATS, 2)
    both = [s for s, f in SENT if a in f and b in f]
    only = [s for s, f in SENT if (a in f) != (b in f)]
    none = [s for s, f in SENT if a not in f and b not in f]
    c = r.randrange(4)
    if c <= 2:
        if not both or len(only) < 3: return None
        right = r.choice(both)
        ws = r.sample(only, 3) + (r.sample(none, 1) if none else [])
        if len(ws) < 4: return None
        ft = dict(SENT)
        steps = ['"%s": %s' % (right, ', '.join(sorted(ft[right])))] + ['"%s": %s' % (w, ', '.join(sorted(ft[w]))) for w in ws[:3]]
        return mc(P('다음 중 "%s"과(와) "%s"이(가) 모두 나타나는 문장은?' % (a, b)), right, ws, steps=steps, core='높임 · 시제 · 동작상 · 피동 · 사동 · 부정 · 안은문장의 복합 판별', lv='상' if c < 2 else '최', fam='A', r=r, ref=[1], vertical=True)
    if not none: return None
    pool = [s for s, f in SENT if a in f or b in f]
    if len(pool) < 4: return None
    right = r.choice(none); ws = r.sample(pool, 4)
    ft = dict(SENT)
    return mc(P('다음 중 "%s"과(와) "%s" 중 어느 것도 나타나지 않는 문장은?' % (a, b)), right, ws, steps=['"%s": %s' % (right, ', '.join(sorted(ft[right])))] + ['"%s": %s' % (w, ', '.join(sorted(ft[w]))) for w in ws[:3]], core='문법 요소의 판별', lv='상', fam='B', r=r, ref=[1], vertical=True)


# ------------------------------------------------------------------ hl086 맞춤법 복합
@T('hl086')
def g086(r, k):
    n = r.choice([3, 3, 4])
    ent = r.sample(SRC, n)
    if len({e[3] for e in ent}) < n: return None
    right = ', '.join(e[0] for e in ent)
    ws = []
    for t in range(6):
        cnt = r.choice([1, 1, 2]) if n >= 3 else 1
        idx = r.sample(range(n), min(cnt, n))
        parts = [(ent[i][1] if i in idx else ent[i][0]) for i in range(n)]
        ws.append(', '.join(parts))
    ws = [w for w in dict.fromkeys(ws) if w != right]
    if len(ws) < 4: return None
    st = ['%s의 바른 표기는 "%s": %s' % (e[1], e[0], e[2]) for e in ent]
    return mc(P('다음 중 맞춤법에 맞게 적은 단어로만 짝지어진 것은?'), right, ws[:4], steps=st + ['따라서 바르게 적은 단어로만 이루어진 선택지는 "%s"이다.' % right], core='여러 조항(된소리 · 구개음화 · 두음 법칙 · 형태 · 사이시옷 등)의 복합 적용', lv='상' if n == 3 else '최', fam='A', r=r, ref=[1], vertical=True)
