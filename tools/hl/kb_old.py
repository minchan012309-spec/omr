# -*- coding: utf-8 -*-
"""Ⅱ-D 중세 국어 지식 표와 옛 한글 조립기."""
import unicodedata

CHO = dict(zip('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ', range(0x1100, 0x1113)))
CHO.update({'ㅿ': 0x1140, 'ㅸ': 0x112B, 'ㆁ': 0x114C, 'ㆆ': 0x1158})
JUNG = dict(zip('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ', range(0x1161, 0x1176)))
JUNG['ㆍ'] = 0x119E
_JO = 'ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'
JONG = dict(zip(_JO, [0x11A8, 0x11A9, 0x11AA, 0x11AB, 0x11AC, 0x11AD, 0x11AE, 0x11AF, 0x11B0, 0x11B1, 0x11B2, 0x11B3, 0x11B4, 0x11B5, 0x11B6, 0x11B7, 0x11B8, 0x11B9, 0x11BA, 0x11BB, 0x11BC, 0x11BD, 0x11BE, 0x11BF, 0x11C0, 0x11C1, 0x11C2]))
JONG.update({'ㅿ': 0x11EB, 'ㆁ': 0x11F0})


def syl(c, v, j=''):
    s = chr(CHO[c]) + chr(JUNG[v]) + (chr(JONG[j]) if j else '')
    return s


def W(*sylls):
    """W(('ㅅ','ㅏ'), ('ㄹ','ㆍ','ㅁ')) -> 조립된 문자열(현대 음절은 NFC)"""
    return unicodedata.normalize('NFC', ''.join(syl(*s) for s in sylls))


MERGE = {'ㅏ': 'ㅐ', 'ㅓ': 'ㅔ', 'ㅗ': 'ㅚ', 'ㅜ': 'ㅟ', 'ㅕ': 'ㅖ', 'ㅑ': 'ㅒ'}


class Word:
    """체언: syls=[(초,중,종)…] (종 없으면 ''), gloss=현대어, yang=양성 모음 끝음절인가, kind=보통/존칭/무정, ij=끝이 ㅣ 또는 반모음 ㅣ인가"""
    def __init__(self, syls, gloss, yang, kind='평칭', ij=False):
        self.syls, self.gloss, self.yang, self.kind, self.ij = syls, gloss, yang, kind, ij

    @property
    def coda(self): return self.syls[-1][2]
    @property
    def plain(self): return W(*self.syls)

    def with_part(self, part):
        """part: 'ㅣ주격' 'ㅣ' 이외에는 (초,중,종) 목록으로 이루어진 조사. 모음 조사는 받침을 이어 적는다(연철)."""
        base = list(self.syls)
        if part == '∅': return W(*base)
        if part == 'ㅅ': return W(*base) + 'ㅅ'
        if part == 'ㅣ':
            c, v, j = base[-1]
            if j or v not in MERGE: return None
            base[-1] = (c, MERGE[v], '')
            return W(*base)
        ps = part
        if ps[0][0] == 'ㅇ' and base[-1][2]:        # 모음으로 시작하는 조사: 연철
            c, v, j = base[-1]
            base[-1] = (c, v, '')
            first = (j, ps[0][1], ps[0][2])
            return W(*(base + [first] + ps[1:]))
        return W(*(base + ps))

    def split(self, part):
        """분철(끊어 적기)"""
        return self.plain + W(*part)


def P_(*s): return list(s)
PART = {
 'ᄋᆞᆯ': P_(('ㅇ', 'ㆍ', 'ㄹ')), 'ᄅᆞᆯ': P_(('ㄹ', 'ㆍ', 'ㄹ')), '을': P_(('ㅇ', 'ㅡ', 'ㄹ')), '를': P_(('ㄹ', 'ㅡ', 'ㄹ')),
 '이': P_(('ㅇ', 'ㅣ', '')), 'ᄋᆡ': P_(('ㅇ', 'ㆍ', ''),)[:0] + [('ㅇ', 'ㆍ', '')],
}
PART['ᄋᆡ'] = [('ㅇ', 'ㆍㅣ', '')] if False else [('ㅇ', 'ㆍ', '')]
PART['의'] = [('ㅇ', 'ㅢ', '')]
PART['가'] = [('ㄱ', 'ㅏ', '')]
PART['ᄋᆞᆯ_'] = PART['ᄋᆞᆯ']

def S_(str_): return str_

# 체언 목록 (끝음절 모음의 성질과 받침 유무)
WORDS = {
 '사람': Word([('ㅅ', 'ㅏ', ''), ('ㄹ', 'ㆍ', 'ㅁ')], '사람', True),
 '나라': Word([('ㄴ', 'ㅏ', ''), ('ㄹ', 'ㅏ', '')], '나라', True, '무정'),
 '믈': Word([('ㅁ', 'ㅡ', 'ㄹ')], '물', False, '무정'),
 '부텨': Word([('ㅂ', 'ㅜ', ''), ('ㅌ', 'ㅕ', '')], '부처', False, '존칭'),
 '나모': Word([('ㄴ', 'ㅏ', ''), ('ㅁ', 'ㅗ', '')], '나무', True, '무정'),
 '님금': Word([('ㄴ', 'ㅣ', 'ㅁ'), ('ㄱ', 'ㅡ', 'ㅁ')], '임금', False, '존칭'),
 '마음': Word([('ㅁ', 'ㆍ', ''), ('ㅿ', 'ㆍ', 'ㅁ')], '마음', True, '무정'),
 '아들': Word([('ㅇ', 'ㅏ', ''), ('ㄷ', 'ㆍ', 'ㄹ')], '아들', True),
 '말씀': Word([('ㅁ', 'ㅏ', 'ㄹ'), ('ㅆ', 'ㆍ', 'ㅁ')], '말씀', True, '무정'),
 '글': Word([('ㄱ', 'ㅡ', 'ㄹ')], '글', False, '무정'),
 '눈': Word([('ㄴ', 'ㅜ', 'ㄴ')], '눈', False, '무정'),
 '불휘': Word([('ㅂ', 'ㅜ', 'ㄹ'), ('ㅎ', 'ㅟ', '')], '뿌리', False, '무정', True),
}

# ------------------------------------------------------------------ 체언 목록 정리 (곡용 체언과 ㅎ 종성 체언은 따로 다룬다)
for _k in ('나라', '나모'):
    WORDS.pop(_k, None)
WORDS['벼로'] = Word([('ㅂ', 'ㅕ', ''), ('ㄹ', 'ㅗ', '')], '벼루', True, '무정')


def obj_part(w):
    """목적격 조사 선택 규칙: 받침 O/X, 양성/음성 모음"""
    if w.coda:
        return 'ᄋᆞᆯ' if w.yang else '을'
    return 'ᄅᆞᆯ' if w.yang else '를'


def nom_form(w):
    """주격 형태 규칙: 자음 뒤 '이', ㅣ·반모음 ㅣ 뒤 '∅', 그 밖의 모음 뒤 'ㅣ'"""
    if w.coda: return 'ᄋ', w.with_part(PART['이'])
    if w.ij: return '∅', w.with_part('∅')
    return 'ㅣ', w.with_part('ㅣ')

# ------------------------------------------------------------------ ㅎ 종성 체언
HW = {
 '하늘': [('ㅎ', 'ㅏ', ''), ('ㄴ', 'ㆍ', 'ㄹ')],
 '돌': [('ㄷ', 'ㅗ', 'ㄹ')],
 '나라': [('ㄴ', 'ㅏ', ''), ('ㄹ', 'ㅏ', '')],
 '길': [('ㄱ', 'ㅣ', 'ㄹ')],
}
HW_GLOSS = {'하늘': '하늘', '돌': '돌', '나라': '나라', '길': '길'}
HPART = {
 '이': [('ㅎ', 'ㅣ', '')], 'ᄋᆞᆯ': [('ㅎ', 'ㆍ', 'ㄹ')], '과': [('ㅋ', 'ㅘ', '')], '도': [('ㅌ', 'ㅗ', '')],
}
HPART_NAME = {'이': '주격 조사 이', 'ᄋᆞᆯ': '목적격 조사 ᄋᆞᆯ', '과': '접속 조사 과', '도': '보조사 도'}

def hform(word, part, hjong=True):
    base = list(HW[word])
    if word == '하늘':
        base = [('ㅎ', 'ㅏ', ''), ('ㄴ', 'ㆍ', 'ㄹ')]
    return W(*(base + HPART[part]))

def hplain(word): return W(*HW[word])
