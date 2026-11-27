import json,collections,html,sys
S=json.load(open('schema.json'));M=json.load(open('meta.json'))
G={'academy':'학원명','act':'행동','action':'동작','active':'사용 중','actor_id':'수행자 ID','added_at':'등록 시각','amount':'청구 금액','anchor_day':'기준일','assignee':'담당자','att_pin':'출석 PIN','audience':'받는 사람','billing_key':'청구 키','body':'내용','by_email':'수정자 이메일','by_name':'작성자','challenge':'챌린지 값','class_id':'반 ID','code':'문항 코드','color':'색','completed_at':'완료 시각','counter':'서명 횟수','created_at':'생성 시각','credential_id':'자격 증명 ID','data':'설정 값','day':'날짜','digest':'해시','done':'완료','due':'마감일','due_on':'마감일','email':'이메일','end_at':'게시 종료','ends_at':'끝 시각','expires_at':'만료 시각','grade':'학년·반','guardian':'보호자','guardian_phone':'보호자 연락처','hidden':'숨김','id':'ID','info':'부가 정보','items':'문항별 결과','joined_on':'입원일','key':'키','kind':'종류','label':'이름표','last_login':'최근 로그인','last_used':'최근 사용','left_on':'퇴원일','login':'아이디','manifest':'목록','member_id':'구성원 ID','memo':'메모','message':'문의 내용','meta':'문항·디자인','method':'결제 수단','missed_on':'결석일','msg':'내용','must_reset':'비밀번호 재설정','name':'이름','next_on':'다음 일정','next_todo':'다음 할 일','note':'메모','on_date':'날짜','open':'가입 허용','owner_id':'원장 ID','paid_amount':'납부액','paid_at':'납부 시각','parent_id':'학부모 ID','patch':'수정 내용','pay_key':'결제 키','phone':'연락처','photo':'풀이 사진','pinned':'고정','plan_at':'보강 일시','popup':'팝업','prefs':'개인 설정','previous_id':'이전 회차 ID','public_key':'공개키','purpose':'용도','pw_hash':'비밀번호 해시','reason':'사유','repeat_kind':'반복 주기','resolution':'처리 결과','resolved_at':'처리 시각','rng':'채점 범위','role':'역할','room':'강의실','row_id':'행 ID','sched':'시간표','school':'학교','set':'채점 종류','share':'학부모 공유','since':'소속일','start_at':'게시 시작','starts_at':'시작 시각','status':'상태','student_id':'학생 ID','students':'학생 수','sub':'학습지·단원','subject':'과목','subjects':'과목','t':'시각','t_in':'등원 시각','t_out':'하원 시각','table_name':'표 이름','tag':'분류','teacher':'강사','title':'제목','token_hash':'토큰 해시','topic':'문의 주제','transports':'연결 방식','tuition':'수강료','updated_at':'수정 시각','user_id':'교사 ID','value':'값','who':'작성자','wid':'학습지 번호'}
cols=collections.defaultdict(list);[cols[c['t']].append(c) for c in S['cols']]
pk=collections.defaultdict(set);[pk[p['t']].add(p['n']) for p in S['pks']]
rels=[dict(t=f['t'],n=f['n'],rt=f['rt'],rn=f['rn'],lg=False) for f in S['fks']]
def L(t,n,rt,rn):rels.append(dict(t=t,n=n,rt=rt,rn=rn,lg=True))
L('attempts','sub','worksheets','wid');L('assignments','wid','worksheets','wid')
for t,n in [('attempts','items'),('wrong_notes','code'),('q_reports','code'),('q_overrides','code')]:L(t,n,'question_bank','code')
L('ops_audit','actor_id','auth.users','id')
VIRT={'auth.users':'교사 계정','question_bank':'문항(JSON 문제은행)'}
VERB={'attempts':'채점','worksheets':'출제','assignments':'배정','passkeys':'등록','st_tokens':'발급','notices':'수신','bug_reports':'제보','signup_requests':'신청','parent_accounts':'보호','wrong_notes':'작성','q_reports':'신고','attendance':'출석','parent_notices':'알림','fees':'청구','class_members':'소속','counsels':'상담','makeups':'보강','ops_tasks':'담당','counsel_appointments':'예약','lesson_changes':'변경','pa_tokens':'발급'}
def verb(r):
    if r['lg']: return {'sub':'응시','wid':'배정'}.get(r['n'],'참조')
    if r['n']=='previous_id': return '이전 회차'
    if r['n'] in('user_id','owner_id'): return {'teacher_settings':'설정','teacher_join':'운영','developers':'지정','academy_members':'소속' if r['n']=='member_id' else '운영'}.get(r['t'],'소유')
    if r['n']=='member_id': return '소속'
    if r['n']=='class_id': return {'class_members':'구성','makeups':'보강','lesson_changes':'변경'}[r['t']]
    return VERB.get(r['t'],'관계')
def kname(t): return VIRT.get(t) or M.get(t,[t])[0]
def tw(s,fs):
    return sum(fs*(1.0 if ord(ch)>0x1100 else .58) for ch in s)
E=lambda s:html.escape(str(s))
BLUE_F,BLUE_S='#dfeaf8','#3f6fb0'; ENT_F,ENT_S='#e6e8eb','#8c939c'; DIA_F,DIA_S='#f7b58e','#e08a5a'
def entity(x,y,w,h,t,main=False):
    k=kname(t);v=t in VIRT
    s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{ "#f4f5f6" if v else ENT_F}" stroke="{ENT_S}" stroke-width="{1.6 if main else 1.2}" {"stroke-dasharray=\"5 4\"" if v else ""}/>'
    s+=f'<text x="{x+w/2}" y="{y+h/2-3}" text-anchor="middle" font-size="{18 if main else 15}" font-weight="700" fill="#2a2f36">{E(k)}</text>'
    s+=f'<text x="{x+w/2}" y="{y+h/2+16}" text-anchor="middle" font-size="{12.5 if main else 11.5}" fill="#6b7480">{E(t)}</text>'
    return s
def page(t):
    out=[r for r in rels if r['t']==t]; inn=[r for r in rels if r['rt']==t and r['t']!=t]
    rows=[('out',r) for r in out]+[('in',r) for r in inn]
    fkset={r['n'] for r in out if not r['lg']}
    C=cols[t]; n=len(C); per=9 if n<=18 else 10; ncol=1 if n<=per else 2
    pills=[];maxw=[0]*ncol
    for i,c in enumerate(C):
        lab=G.get(c['n'],c['n']); w=tw(lab,13)+tw(c['n'],10.5)+34
        ci=i//per if ncol==2 else 0; maxw[ci]=max(maxw[ci],w); pills.append((ci,i%per if ncol==2 else i,lab,c['n'],w))
    PH,PG=28,9
    colh=[sum(1 for p in pills if p[0]==k) for k in range(ncol)]
    attrH=max(colh)*(PH+PG)
    RH=74; relH=len(rows)*RH
    H=max(attrH,relH,160)+40
    pad=30; x=pad; colx=[]
    for k in range(ncol): colx.append(x); x+=maxw[k]+18
    ex=x+70; ew,eh=max(170,tw(kname(t),18)+40),64
    ey=pad+H/2-eh/2
    svg=[]
    for ci,ri,lab,cn,w in pills:
        k=ci;cnt=colh[k];top=pad+H/2-cnt*(PH+PG)/2
        py=top+ri*(PH+PG); px=colx[k]+(maxw[k]-w)
        svg.insert(0,f'<line x1="{px+w}" y1="{py+PH/2}" x2="{ex}" y2="{ey+eh/2}" stroke="#a9c1e0" stroke-width="1"/>')
        isk=cn in pk[t]; isf=cn in fkset
        deco='text-decoration="underline"' if isk else ''
        svg.append(f'<rect x="{px}" y="{py}" width="{w}" height="{PH}" rx="{PH/2}" fill="{BLUE_F}" stroke="{BLUE_S}" stroke-width="1.1" {"stroke-dasharray=\"4 3\"" if isf and not isk else ""}/>')
        svg.append(f'<text x="{px+14}" y="{py+18.5}" font-size="13" font-weight="600" fill="#1d3557" {deco}>{E(lab)}<tspan font-size="10.5" font-weight="400" fill="#5b6f8c" dx="6">{E(cn)}{" (FK)" if isf else ""}</tspan></text>')
    svg.append(entity(ex,ey,ew,eh,t,True))
    dx=ex+ew+150; rx=dx+130; W=rx+40
    top=pad+H/2-relH/2
    for i,(d,r) in enumerate(rows):
        cy=top+i*RH+RH/2; other=r['rt'] if d=='out' else r['t']
        if r['t']==r['rt']: other=t
        one2one = d=='out' and pk[t]=={r['n']} or (d=='in' and pk[r['t']]=={r['n']})
        mine = '1' if one2one else ('n' if d=='out' else '1')
        theirs = '1' if one2one else ('1' if d=='out' else 'n')
        if t=='class_members' or (d=='in' and r['t']=='class_members'): pass
        dash='stroke-dasharray="6 4"' if r['lg'] else ''
        svg.insert(0,f'<path d="M{ex+ew} {ey+eh/2} C{ex+ew+70} {ey+eh/2},{dx-80} {cy},{dx-46} {cy}" fill="none" stroke="#555" stroke-width="1.2" {dash}/>')
        svg.insert(0,f'<line x1="{dx+46}" y1="{cy}" x2="{rx}" y2="{cy}" stroke="#555" stroke-width="1.2" {dash}/>')
        vb=verb(r); dw=max(46,tw(vb,12.5)/2+30)
        svg.append(f'<polygon points="{dx-dw},{cy} {dx},{cy-22} {dx+dw},{cy} {dx},{cy+22}" fill="{DIA_F if not r["lg"] else "#fde3d3"}" stroke="{DIA_S}" stroke-width="1.1" {dash}/>')
        svg.append(f'<text x="{dx}" y="{cy+4.5}" text-anchor="middle" font-size="12.5" font-weight="700" fill="#7a3510">{E(vb)}</text>')
        svg.append(f'<text x="{dx-dw-10}" y="{cy-12}" text-anchor="end" font-size="13" font-weight="700" fill="#333">{mine}</text>')
        svg.append(f'<text x="{dx+dw+10}" y="{cy-6}" font-size="13" font-weight="700" fill="#333">{theirs}</text>')
        ow=max(150,tw(kname(other),15)+30); W=max(W,rx+ow+pad)
        svg.append(entity(rx,cy-24,ow,48,other))
        svg.append(f'<text x="{rx+ow+8}" y="{cy+4}" font-size="10.5" fill="#8a929c">{E(r["n"])}</text>')
        W=max(W,rx+ow+pad+tw(r['n'],10.5)+10)
    if not rows: W=ex+ew+pad
    Ht=H+pad*2+30
    leg=f'<text x="{pad}" y="{Ht-14}" font-size="11.5" fill="#6b7480">밑줄 = 기본키(PK) · 점선 타원 = 외래키(FK) · 마름모 = 관계 · 1 / n = 관계의 대응 수 · 점선 연결 = 논리 참조(코드 값으로 연결, DB 제약 없음)</text>'
    W=max(W,760)
    return f'<!doctype html><meta charset=utf-8><style>body{{margin:0;background:#fff}}svg text{{font-family:Pretendard,sans-serif}}</style><svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Ht}" viewBox="0 0 {W} {Ht}"><rect width="100%" height="100%" fill="#fff"/>{"".join(svg)}{leg}</svg>'
import os;os.makedirs('chen',exist_ok=True)
for t in sorted(cols): open(f'chen/{t}.html','w').write(page(t))
json.dump(sorted(cols),open('chen/list.json','w'))
print(len(cols))
