# 전체(핵심) ERD — Chen 표기, 손으로 배치
import html
E=html.escape
def tw(s,fs): return sum(fs*(1.0 if ord(c)>0x1100 else .58) for c in s)
ent={ # key:(x,y,ko,en)
'auth':(80,90,'교사 계정','auth.users'),'stu':(560,330,'학생','students'),'ws':(1040,90,'학습지','worksheets'),
'att':(1040,330,'채점 기록','attempts'),'qb':(1520,330,'문항','question_bank (JSON)'),'asg':(1000,600,'과제 배정','assignments'),
'wn':(1520,560,'오답 메모','wrong_notes'),'cls':(80,560,'반','classes'),'pa':(560,760,'학부모 계정','parent_accounts'),
'atd':(80,760,'출결·수납·상담','attendance · fees · counsels'),'set':(560,90,'학원 설정','teacher_settings')}
W,H=180,62
def c(k): x,y,_,_=ent[k];return x+W/2,y+H/2
rels=[('auth','set','설정','1','1'),('auth','stu','소유','1','n'),('auth','cls','운영','1','n'),('stu','ws','출제','1','n'),('stu','att','채점','1','n'),
('ws','att','응시','1','n'),('att','qb','포함','m','n'),('stu','asg','배정','1','n'),('stu','wn','작성','1','n'),('wn','qb','대상','n','1'),
('cls','stu','반 소속','m','n'),('stu','pa','보호','1','n'),('stu','atd','기록','1','n')]
s=[]
for a,b,v,ca,cb in rels:
    (x1,y1),(x2,y2)=c(a),c(b);mx,my=(x1+x2)/2,(y1+y2)/2
    dash='stroke-dasharray="6 4"' if v in('응시','포함','대상') else ''
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#555" stroke-width="1.3" {dash}/>')
    dw=max(44,tw(v,13)/2+28)
    s.append(f'<polygon points="{mx-dw},{my} {mx},{my-22} {mx+dw},{my} {mx},{my+22}" fill="#f7b58e" stroke="#e08a5a" stroke-width="1.1"/><text x="{mx}" y="{my+5}" text-anchor="middle" font-size="13" font-weight="700" fill="#7a3510">{E(v)}</text>')
    # cardinality near ends (25% along)
    for (px,py),lab in (((x1+(x2-x1)*.2,y1+(y2-y1)*.2),ca),((x1+(x2-x1)*.8,y1+(y2-y1)*.8),cb)):
        s.append(f'<text x="{px+8}" y="{py-8}" font-size="14" font-weight="800" fill="#222" style="paint-order:stroke" stroke="#fff" stroke-width="4">{lab}</text>')
for k,(x,y,ko,en) in ent.items():
    v=k in('auth','qb')
    s.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="4" fill="{"#f4f5f6" if v else "#e6e8eb"}" stroke="#8c939c" stroke-width="1.3" {"stroke-dasharray=\"5 4\"" if v else ""}/><text x="{x+W/2}" y="{y+27}" text-anchor="middle" font-size="16" font-weight="700" fill="#2a2f36">{E(ko)}</text><text x="{x+W/2}" y="{y+46}" text-anchor="middle" font-size="11.5" fill="#6b7480">{E(en)}</text>')
TW,TH=1780,900
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}"><rect width="100%" height="100%" fill="#fff"/>{"".join(s)}<text x="80" y="{TH-20}" font-size="12.5" fill="#6b7480">핵심 표 11개의 관계(전체 36개 표 중). 점선 = 문항 코드 · 학습지 번호처럼 값으로 잇는 논리 관계. 「반 소속」은 class_members 표로 구현한 N:M 관계, 「포함」은 attempts.items(jsonb) 배열로 구현한 M:N 관계.</text></svg>'
open('overview.svg','w').write(svg)
open('chen/overview.html','w').write('<!doctype html><meta charset=utf-8><style>body{margin:0}svg text{font-family:Pretendard,sans-serif}</style>'+svg)
