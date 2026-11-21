"""build.py 결과를 bank/에 반영한다.
- 새 문항(해원고 부교재 원본·변형·유사) 파일 쓰기
- 범위 밖 유형 삭제, 범위 안 기존 유형은 새 유형 체계로 재분류
- 기존 문항의 Δ𝐻·Δ𝑆·𝐸ₐ 표기를 수식 글꼴(Latin Modern Math)로 바꾼다
"""
import os, json, re, collections
import build
from orig_common import TYPES, SUBNAME

BANK = build.BANK
OLD = {  # 기존 유형 이름 → 새 유형(None = 삭제)
 '발열·흡열 반응과 ΔH의 부호': 'A2', '엔탈피·반응 엔탈피와 엔탈피 도표 해석': 'A2', '열화학 반응식의 표기(상태·조건·계수·역반응)': 'A3',
 '연소·생성·분해·용해·기화 엔탈피의 정의': 'A1', '간이 열량계 Q=cmΔt와 몰당 반응 엔탈피 계산': 'A5', '결합 에너지와 반응 엔탈피': 'B5',
 '생성 엔탈피로 반응 엔탈피 구하기': 'B6', '연료의 효율성 비교': None, '헤스 법칙의 의미': 'B1', '열화학 반응식의 조합(헤스 법칙 계산)': 'B2',
 '엔탈피 관계도 해석': 'B3', '자발적 변화와 비자발적 변화': 'C1', '엔트로피의 의미와 크기 비교': 'C2', '엔트로피가 증가·감소하는 경우': 'C2',
 'ΔS계·ΔS주위·ΔS전체와 자발성': 'C3', '열린계·닫힌계·고립계': 'C3', '엔탈피·엔트로피 변화와 자발성': 'C4', '상평형(동적 평형)과 엔트로피': None,
 '반응 속도의 정의와 단위': 'D1', '반응 속도 측정 방법': 'D1', '평균·순간·초기 반응 속도와 그래프': 'D2', '반응 계수와 농도 변화량의 관계': 'D2',
 '반응 속도식·반응 차수·반응 속도 상수': 'D3', '1차 반응과 반감기': 'D4', '유효 충돌의 조건': 'E1', '활성화 에너지와 활성화물': 'E2',
 '반응 진행에 따른 에너지(엔탈피) 도표 해석': 'E2', '분자 운동 에너지 분포 곡선': 'E3', '농도·압력과 반응 속도': 'F1', '표면적과 반응 속도': 'F1',
 '온도와 반응 속도': 'F2', '촉매와 반응 속도': 'F3', '촉매의 활용(촉매 변환기·효소)': 'F5', '반응 속도 요인 종합 비교': 'F4',
 'ΔH와 열량 계산(물질의 양·질량 비례)': 'A4', '결합 에너지 자료로 ΔH 계산하기': 'B5', '생성 엔탈피 자료로 ΔH 계산하기': 'B6',
 '용해 반응의 ΔH(몰당) 계산하기': 'A5', '헤스 법칙 계산(반응식 조합)': 'B2', 'ΔS주위·ΔS전체로 자발성 판단하기': 'C3',
 '엔트로피가 증가·감소하는 변화 고르기': 'C2', '평균 반응 속도와 계수비 계산': 'D2', '실험 자료로 반응 차수·속도 상수 구하기': 'D3',
 '1차 반응의 반감기 계산': 'D4', '속도 상수와 반감기의 관계': None, '에너지 도표로 활성화 에너지·ΔH 구하기': 'E2', '온도에 따른 반응 속도 변화 계산': None,
 '농도·부피 변화에 따른 반응 속도 계산': 'F1', '엔탈피와 열화학 반응식 개념 점검': 'A1', '열량계와 연료의 효율 개념 점검': 'A5',
 '헤스 법칙과 생성 엔탈피 개념 점검': 'B1', '엔트로피 개념 점검': 'C2', '자발성과 ΔS전체 개념 점검': 'C4', '반응 속도 개념 점검': 'D1',
 '활성화 에너지와 충돌 이론 개념 점검': 'E1', '촉매와 반응 속도 요인 개념 점검': 'F4'}
NEWLAB = {v[1] for v in TYPES.values()}
# 부교재에 없는 내용(문항 단위로 지움)
OUT = re.compile(r'10 ?℃[^.<]{0,25}(높아|올라|상승)[^.<]{0,30}2 ?배|ln ?2|0\.69|아레니우스|연료의 효율|연료 효율|상평형|동적 평형|증기 압력|발열량이 큰 연료')

MI = {c: chr(0x1D44E + i) for i, c in enumerate('abcdefghijklmnopqrstuvwxyz')}; MI['h'] = 'ℎ'
MI.update({c: chr(0x1D434 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')})
def mx(s): return f'<span class="mx">{s}</span>'
def mathify(h):
    """SVG 밖 본문의 Δ𝐻·Δ𝑆·Δ𝐺·𝐸ₐ·Δ𝑡 를 수식 글꼴로."""
    parts = re.split(r'(<svg.*?</svg>|<math.*?</math>|<span class="mx">.*?</span>)', h, flags=re.S)
    for i in range(0, len(parts), 2):
        s = parts[i]
        s = re.sub(r'Δ([HSGtTE])(?![a-zA-Z])', lambda m: mx('Δ' + MI[m.group(1)]), s)
        s = re.sub(r'(?<![A-Za-z>])E<sub>a</sub>', mx(MI['E']) + '<sub>a</sub>', s)
        s = re.sub(r'(?<![A-Za-z>])E<sub>a</sub>′', mx(MI['E']) + '<sub>a</sub>′', s)
        s = re.sub(r'(?<![A-Za-z])t<sub>1/2</sub>', mx(MI['t']) + '<sub>1/2</sub>', s)
        parts[i] = s
    return ''.join(parts)

def new_rv(typ):
    (t, w), = build.rv_of(typ)
    return f'<div class="rv"><span class="lb">이 문제를 틀렸다면 다시 공부할 부분</span><div class="st">→ {t} <span class="sm">(개념 정리 {w})</span></div></div>'

def fix_q(q, typ):
    sub = TYPES[typ][0]
    q['type'] = TYPES[typ][1]; q['sub'] = sub; q['subname'] = SUBNAME[sub]
    for k in ('q', 'exp'):
        if k in q and isinstance(q[k], str):
            q[k] = mathify(q[k])
    if isinstance(q.get('exp'), str):
        q['exp'] = re.sub(r'<div class="rv">.*?</div></div>(?=</div>$)', new_rv(typ), q['exp'], flags=re.S)
    return q

def write(files, index):
    idx_path = os.path.join(BANK, 'index.json')
    old_idx = json.load(open(idx_path, encoding='utf-8'))
    out_idx = {}; stats = collections.Counter()
    for tag, ent in old_idx.items():
        if ent.get('hw'): continue                     # 예전 빌드 결과는 새로 씀
        typ = OLD.get(ent['label'])
        path = os.path.join(BANK, tag + '.json')
        if typ is None:
            if ent['label'] in NEWLAB:  # 이미 재분류된 기존 유형
                typ = next(k for k, v in TYPES.items() if v[1] == ent['label'])
            else:
                if os.path.exists(path): os.remove(path)
                stats['삭제 유형'] += 1; stats['삭제 문항'] += ent['n']; continue
        qs = json.load(open(path, encoding='utf-8'))
        keep = []
        for q in qs:
            if OUT.search(re.sub(r'<[^>]+>', '', q.get('q', '') + q.get('exp', ''))): stats['범위 밖 문항 삭제'] += 1; continue
            keep.append(fix_q(q, typ))
        json.dump(keep, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        lv = collections.Counter(q['lv'] for q in keep)
        out_idx[tag] = {**ent, 'lv': dict(lv), 'label': TYPES[typ][1], 'sub': TYPES[typ][0], 'subname': SUBNAME[TYPES[typ][0]], 'n': len(keep)}
        stats['재분류 유형'] += 1
    for tag, qs in files.items():
        json.dump(qs, open(os.path.join(BANK, tag + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        out_idx[tag] = index[tag]
    # 정렬: 소단원 → 유형 번호
    order = {v[1]: k for k, v in TYPES.items()}
    out_idx = dict(sorted(out_idx.items(), key=lambda kv: (kv[1]['sub'], order.get(kv[1]['label'], 'Z'), not kv[1].get('hw'), kv[0])))
    json.dump(out_idx, open(idx_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    stats.update(fix_datajs())
    print(dict(stats))

def fix_datajs():
    p = os.path.join(BANK, 'data.js'); s = open(p, encoding='utf-8').read()
    m = re.match(r'(const DATA=)(\[.*\])(;?\s*)$', s, re.S)
    data = json.loads(m.group(2)); out = []; st = collections.Counter()
    for q in data:
        lab = q.get('type')
        typ = OLD.get(lab) if lab not in NEWLAB else next(k for k, v in TYPES.items() if v[1] == lab)
        if lab and typ is None and lab in OLD: st['교재 문항 삭제(범위 밖 유형)'] += 1; continue
        if OUT.search(re.sub(r'<[^>]+>', '', str(q.get('q', '')) + str(q.get('exp', '')))): st['교재 문항 삭제(범위 밖 내용)'] += 1; continue
        if typ: fix_q(q, typ)
        out.append(q)
    open(p, 'w', encoding='utf-8').write(m.group(1) + json.dumps(out, ensure_ascii=False) + m.group(3))
    st['교재 문항 남김'] = len(out)
    return st
