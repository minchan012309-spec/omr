# -*- coding: utf-8 -*-
"""Ⅲ-A 한글 맞춤법: 원리와 소리 (hl056~hl062)"""
from hllib import *
from orth_gen import *
import kb_orth1 as K1, kb_orth2 as K2, kb_orth3 as K3, kb_tf

# ---- 공용 풀
def _ents(rows, g): return ents(rows, g)

DOS_Y = _ents(K1.DOS_Y, 'dosy'); DOS_N = _ents(K1.DOS_N, 'dosn'); DOS_R = _ents(K1.DOS_R, 'dosr')
PAL = _ents(K1.PAL, 'pal')
DH = _ents(K1.DUUM_HEAD, 'head'); DB = _ents(K1.DUUM_BODY, 'body'); DA = _ents(K1.DUUM_AFFIX, 'aff')
RY = _ents(K1.RYUL_Y, 'ryuly'); RN = _ents(K1.RYUL_N, 'ryuln'); EY = _ents(K1.RYEOL_Y, 'ryeoly'); EN = _ents(K1.RYEOL_N, 'ryeoln')
NI = _ents(K2.NOUN_I, 'ni'); NE = _ents(K2.NOUN_EUM, 'ne'); FAR = _ents(K2.FAR, 'far'); BOT = _ents(K2.BOTIM, 'bot')
MI = _ents(K2.MYEONG_I, 'mi'); MX = _ents(K2.MYEONG_X, 'mx'); HY = _ents(K2.HAGERI_Y, 'hy'); HN = _ents(K2.HAGERI_N, 'hn')
BY = _ents(K2.BUSA_Y, 'by'); BB = _ents(K2.BUSA_B, 'bb'); BN = _ents(K2.BUSA_N, 'bn')
GP = _ents(K3.GAP, 'gap'); GX = _ents(K3.GAP_X, 'gapx'); TO = _ents(K3.TOOTH, 'tooth')
JO = _ents(K2.JOSA, 'josa'); EO = _ents(K2.EOMI, 'eomi')
SAI_WHY = {'된': '뒷말의 첫소리가 된소리로 나므로 사이시옷을 받쳐 적는다(제30항).', 'ㄴ': "뒷말의 첫소리 'ㄴ, ㅁ' 앞에서 'ㄴ' 소리가 덧나므로 사이시옷을 받쳐 적는다(제30항).", 'ㄴㄴ': "뒷말의 첫소리 모음 앞에서 'ㄴㄴ' 소리가 덧나므로 사이시옷을 받쳐 적는다(제30항)."}
SAI = [E(d['ok'], [d['bad']], '%s(%s) %s' % (d['ok'], d['hz'], SAI_WHY[d['typ']]), 'sai') for d in K3.SAI_Y]
SAIN = _ents(K3.SAI_N, 'sain')
SORI = BOT + MX + HN + BN + FAR + DOS_Y[:8]
OBEOP = NI + NE + MI + HY + BY + BB + GP + PAL + JO + EO
for e in SORI: e.cls = 'sori'
for e in OBEOP: e.cls = 'obeop'

DSORI = "소리대로 적은(원형을 밝히어 적지 않은) 말"
DOBEOP = "어법에 맞도록 원형을 밝히어 적은 말"

def _pick(r, *ws):
    return r.choices(range(len(ws)), weights=ws)[0]


@T('hl056')
def g056(r, k):
    c = r.randrange(7)
    if c == 0: return tpl_class(r, (DSORI, SORI), (DOBEOP, OBEOP), 'ok', '중', 'K1', [1])
    if c == 1: return tpl_class(r, (DSORI, SORI), (DOBEOP, OBEOP), 'bad', '하', 'K2', [1])
    if c == 2: return tpl_class(r, (DOBEOP, OBEOP), (DSORI, SORI), 'bad', '중', 'K3', [1])
    if c == 3: return tpl_class(r, (DOBEOP, OBEOP), (DSORI, SORI), 'ok', '하', 'K4', [1])
    if c == 4:
        # ㄱㄴㄷ: 소리대로 / 어법
        xs = r.sample(SORI + OBEOP, 3)
        stm = []
        for e in xs:
            truth = r.random() < .5
            cl = e.cls if truth else ('obeop' if e.cls == 'sori' else 'sori')
            txt = "'%s'은(는) %s이다." % (e.ok, DSORI if cl == 'sori' else DOBEOP)
            stm.append((txt, truth, ("" if truth else "'%s'은(는) %s이다. " % (e.ok, DSORI if e.cls == 'sori' else DOBEOP)) + e.why))
        return bogi('한글 맞춤법 제1항의 두 가지 원리에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?', stm, lv='상', fam='K5', r=r, ref=[1], ask='')
    if c == 5:
        rules = [("어간에 '-이'나 '-음/-ㅁ'이 붙어 명사로 된 것은 그 어간의 원형을 밝히어 적는다.", NI + NE, '원형을 밝히어 적은 것이다'),
                 ("어간의 뜻과 멀어진 것은 원형을 밝히어 적지 않는다.", FAR, '소리대로 적은 것이다'),
                 ("'-이/-음' 이외의 모음으로 시작된 접미사가 붙어 다른 품사로 바뀐 것은 원형을 밝히어 적지 않는다.", BOT, '소리대로 적은 것이다')]
        return tpl_label(r, rules, '최', 'R1', [1], mode=r.choice(['bad', 'ok']))
    return tpl_tf(r, kb_tf.ORTH_CONCEPT, mode=r.choice(['ok', 'bad']), lv='중', fam='T1', ref=[1])


@T('hl057')
def g057(r, k):
    c = r.randrange(7)
    P1 = DOS_Y + DOS_N + DOS_R
    if c == 0: return tpl_choose(r, DOS_Y, 'ok', None, '하', 'A1', ref=[2])
    if c == 1: return tpl_choose(r, DOS_N, 'ok', None, '하', 'A2', ref=[2]) if len(DOS_N) >= 5 else tpl_choose(r, P1, 'ok', None, '중', 'A2', ref=[2])
    if c == 2: return tpl_choose(r, P1, 'bad', None, '중', 'B1', ref=[2])
    if c == 3: return tpl_choose(r, P1, 'ok', 'dos', '상', 'D1', ref=[2])
    if c == 4: return tpl_stmt3(r, P1, 'dos', '상', 'C1', [2])
    if c == 5: return tpl_same(r, [('y', DOS_Y), ('n', DOS_N), ('r', DOS_R), ('p', PAL), ('h', DH)], '상', 'G1', [2])
    return tpl_choose(r, DOS_Y + DOS_N, 'bad', 'dos', '최', 'D2', ref=[2])


@T('hl058')
def g058(r, k):
    c = r.randrange(5)
    if c == 0: return tpl_choose(r, PAL, 'ok', None, '중', 'A1', ref=[2])
    if c == 1: return tpl_choose(r, PAL, 'bad', None, '중', 'B1', ref=[2])
    if c == 2: return tpl_choose(r, PAL, 'ok', 'pal', '상', 'D1', ref=[2])
    if c == 3: return tpl_stmt3(r, PAL, 'pal', '상', 'C1', [2])
    return tpl_choose(r, PAL, 'bad', 'pal', '최', 'D2', ref=[2])


@T('hl059')
def g059(r, k):
    P1 = DH + DB + DA
    c = r.randrange(7)
    if c == 0: return tpl_choose(r, DH, 'ok', None, '하', 'A1', ref=[3])
    if c == 1: return tpl_choose(r, DB, 'ok', None, '중', 'A2', ref=[3])
    if c == 2: return tpl_choose(r, P1, 'bad', None, '중', 'B1', ref=[3])
    if c == 3: return tpl_choose(r, P1, 'ok', 'duum', '상', 'D1', ref=[3])
    if c == 4: return tpl_stmt3(r, P1, 'duum', '상', 'C1', [3])
    if c == 5: return tpl_same(r, [('h', DH), ('b', DB), ('a', DA), ('ry', RY + RN), ('pal', PAL)], '상', 'G1', [3])
    return tpl_choose(r, DA, 'ok', 'duum', '최', 'D2', ref=[3]) if len(DA) >= 5 else tpl_choose(r, P1, 'ok', 'duum', '상', 'D3', ref=[3])


@T('hl060')
def g060(r, k):
    P1 = RY + RN + EY + EN
    c = r.randrange(6)
    if c == 0: return tpl_choose(r, RY + RN, 'ok', None, '중', 'A1', ref=[3])
    if c == 1: return tpl_choose(r, RY + RN, 'bad', None, '중', 'B1', ref=[3])
    if c == 2: return tpl_choose(r, P1, 'ok', 'ryul', '상', 'D1', ref=[3])
    if c == 3: return tpl_stmt3(r, P1, 'ryul', '상', 'C1', [3])
    if c == 4: return tpl_choose(r, EY + EN, 'ok', 'ryul', '상', 'D2', ref=[3]) if len(EY + EN) >= 5 else tpl_choose(r, P1, 'bad', 'ryul', '최', 'D3', ref=[3])
    return tpl_choose(r, P1, 'bad', 'ryul', '최', 'D4', ref=[3])


@T('hl061')
def g061(r, k):
    c = r.randrange(11)
    if c == 0: return tpl_choose(r, PAL, 'ok', 'pal', '상', 'D1', ref=[1])
    if c == 1: return tpl_choose(r, DOS_Y + DOS_N + DOS_R, 'bad', 'dos', '상', 'D2', ref=[1])
    if c == 2: return tpl_choose(r, DH + DB + DA, 'ok', 'duum', '상', 'D3', ref=[1])
    if c == 3: return tpl_choose(r, NI + NE, 'ok', 'noun', '중', 'D4', ref=[1])
    if c == 4: return tpl_choose(r, MI + MX, 'bad', 'myeong', '상', 'D5', ref=[1])
    if c == 5: return tpl_choose(r, HY + HN, 'ok', 'hageri', '상', 'D6', ref=[1])
    if c == 6: return tpl_choose(r, BY + BB + BN, 'bad', 'busa', '상', 'D7', ref=[1])
    if c == 7: return tpl_choose(r, GP + GX + TO, 'ok', 'gap', '상', 'D8', ref=[1])
    if c == 8:
        rules = [("어간에 '-이'나 '-음/-ㅁ'이 붙어 명사로 된 것은 그 어간의 원형을 밝히어 적는다.", NI + NE, '원형을 밝히어 적은 것이다'),
                 ("어간의 뜻과 멀어진 것은 원형을 밝히어 적지 않는다.", FAR, '소리대로 적은 것이다'),
                 ("'-이/-음' 이외의 모음으로 시작된 접미사가 붙어 다른 품사로 바뀐 것은 원형을 밝히어 적지 않는다.", BOT, '소리대로 적은 것이다')]
        return tpl_label(r, rules, '최', 'R1', [1], mode=r.choice(['bad', 'ok']))
    if c == 9:
        rules = [("명사 뒤에 '-이'가 붙어서 된 말은 그 명사의 원형을 밝히어 적는다.", MI, '원형을 밝히어 적은 것이다'),
                 ("'-하다'나 '-거리다'가 붙는 어근에 '-이'가 붙어 명사가 된 것은 그 어근의 원형을 밝히어 적는다.", HY, '어근의 원형을 밝히어 적은 것이다'),
                 ("'-하다'나 '-거리다'가 붙을 수 없는 어근에 접미사가 붙어 명사가 된 것은 원형을 밝히어 적지 않는다.", HN, '소리대로 적은 것이다'),
                 ("명사 뒤에 '-이' 이외의 모음으로 시작된 접미사가 붙은 말은 명사의 원형을 밝히어 적지 않는다.", MX, '소리대로 적은 것이다')]
        return tpl_label(r, rules, '최', 'R2', [1], mode=r.choice(['bad', 'ok']))
    return tpl_jun(r, K3.JUN, '최', 'J1', [1], mode=r.choice(['bad', 'ok']))


# ---- 한글 맞춤법의 개념과 구성 (내신)
@T('hl062')
def g062(r, k):
    c = r.randrange(5)
    bank = kb_tf.ORTH_CONCEPT
    if c in (0, 1): return tpl_tf(r, bank, 'ok', lv='하', fam='T1', ref=[1])
    if c == 2: return tpl_tf(r, bank, 'bad', lv='중', fam='T2', ref=[1])
    if c == 3: return tpl_tf(r, bank, three=True, lv='중', fam='T3', ref=[1], intro='한글 맞춤법에 대한 설명으로 옳은 것만을 〈보기〉에서 있는 대로 고른 것은?')
    return tpl_tf(r, bank, 'bad', lv='상', fam='T4', ref=[1])
