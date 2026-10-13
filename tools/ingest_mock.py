#!/usr/bin/env python3 -I
"""실전 동형 모의고사 HTML(출제 파일)을 앱 문항(cm/data.json) + cm/mocks.json 으로 변환한다.
사용: python3 -I tools/ingest_mock.py <mock.html> <회차>"""
import sys,re,json,base64,os,copy,html as H
from bs4 import BeautifulSoup, NavigableString
src,rd=sys.argv[1],int(sys.argv[2])
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
soup=BeautifulSoup(open(src,encoding='utf8').read(),'lxml')
CIR='①②③④⑤'
def save_img(img,code,k):
    m=re.match(r'data:image/(\w+);base64,(.*)',img['src'],re.S)
    if not m: return img['src']
    ext={'jpeg':'jpg'}.get(m.group(1),m.group(1))
    fn=f'cm/fig/{code}{"" if k==0 else "-"+str(k)}.{ext}'
    open(os.path.join(root,fn),'wb').write(base64.b64decode(m.group(2)));return fn
def inner(el):return ''.join(H.escape(str(c)) if isinstance(c,NavigableString) else str(c) for c in el.contents)
pages=soup.select('div.page')
qs={};order=[]
for pg in pages:
    t=pg.select_one('.hd .t2')
    if not t or '문제지' not in t.get_text():continue
    for q in pg.select('.q'):
        no=int(q.select_one('.no').get_text());qs[no]=q;order.append(no)
# 정답/해설
ans={};pts={};area={};ex={}
cur=None
for pg in pages:
    t=pg.select_one('.hd .t1')
    if not t or '정답 및 해설' not in t.get_text():continue
    for tb in pg.select('table.sum-t'):
        rows=tb.select('tr')
        if len(rows)==3:
            for n,a,p in zip(rows[0].select('th'),rows[1].select('td'),rows[2].select('td')):
                ans[int(n.get_text())]=CIR.index(a.get_text().strip())+1;pts[int(n.get_text())]=p.get_text().strip()
    for e in pg.select('.ex'):
        h=e.select_one('.exh')
        if h:
            cur=int(h.select_one('.no').get_text());area[cur]=h.select_one('.r').get_text().split('·')[0].strip()
            ex[cur]={'core':'','ch':[],'need':'','rv':'','src':''}
            b=e.select_one('.exb p')
            if b:ex[cur]['core']=inner(b)
            continue
        if cur is None:continue
        m=e.select_one('.exb.m')
        if not m:continue
        p=m.select_one('p')
        if p:ex[cur]['ch'].append(inner(p))
        nd=m.select_one('.nd');rv=m.select_one('.rv');sr=m.select_one('.src')
        if nd:ex[cur]['need']=nd.get_text().split(':',1)[-1].strip()
        if rv:ex[cur]['rv']=rv.get_text().split(':',1)[-1].strip()
        if sr:ex[cur]['src']=sr.get_text().split(':',1)[-1].strip()
data=json.load(open(os.path.join(root,'cm/data.json'),encoding='utf8'))
data=[d for d in data if not str(d['code']).startswith('M%d-'%rd)]
codes=[]
AREAMAP={'생명체의 구성 물질':('Ⅰ-A','생명체의 구성 물질'),'세포의 구조와 기능':('Ⅰ-B','세포의 구조와 기능'),'세포막 물질 이동':('Ⅰ-C','세포막을 통한 물질 이동'),'물질대사':('Ⅱ-A','물질대사와 에너지'),'세포 호흡과 ATP':('Ⅱ-B','세포 호흡과 ATP'),'에너지 대사량':('Ⅱ-C','에너지 대사량')}
for no in order:
    q=qs[no];code='M%d-%03d'%(rd,no);codes.append(code)
    q=copy.copy(q)
    pt=q.select_one('.pt').get_text().strip('[]점 ')
    q.select_one('.pt').decompose();q.select_one('.no').decompose()
    for k,img in enumerate(q.select('img')):img['src']=save_img(img,code,k);img['alt']=''
    # 변환
    for b in q.select('.box'):
        if b.select_one('.bt'):
            b['class']=['bogi'];
            for bi in b.select('.bi'):bi.name='p';bi.attrs={}
        else:
            b['class']=['bxx']
            for bi in b.select('.bi'):bi.name='p';bi.attrs={}
    for t in q.select('table.dt'):t['class']=['tb']
    for f in q.select('.fig'):f['class']=['fg']
    stem=q.select_one('.stem');ch=q.select_one('.ch')
    chs=[]
    cs=[c.get_text().strip() for c in ch.select('.c')]
    for c in cs:
        chs.append((c[0],c[1:].strip()))
    ch.decompose()
    stem_html=''.join(str(c) for c in stem.contents)
    # stem 외 요소(box/fig)는 stem 뒤 형제
    sib=''.join(str(c) for c in q.contents if c is not stem)
    # stem 내부에 직접 텍스트 + 중첩요소: 문단 텍스트/블록 분리
    sh=BeautifulSoup('<div>'+stem_html+'</div>','lxml').div
    lead='';rest=''
    for c in sh.contents:
        if isinstance(c,NavigableString) or c.name in('span','sub','sup','b','i','em'):
            sc=H.escape(str(c)) if isinstance(c,NavigableString) else str(c)
            if rest:rest+='<p>'+sc+'</p>'
            else:lead+=sc
        else:rest+=str(c)
    qs_html='<p>'+lead.strip()+'</p>'+rest+sib
    qh=f'<div class="qh"><b class="qn">{no}</b><span class="qp">[{pt}점]</span></div>'
    chh='<div class="chs">'+''.join(f'<div><b>{n}</b><span>{t}</span></div>' for n,t in chs)+'</div>'
    qhtml=f'<div class="q" id="q-{code.replace("-","")}">{qh}<div class="qs">{qs_html}{chh}</div></div>'
    e=ex[no]
    sol=f'<div class="sol" id="s-{code.replace("-","")}"><div class="sh"><span class="sn">{no}</span><span class="sa">정답 {CIR[ans[no]-1]}</span><span class="sc2">{code}</span></div><div class="ss">출처 : 실전 동형 모의고사 {rd}회 {no}번</div><p><span class="lb">핵심</span> {e["core"]}</p>'+''.join(f'<p class="st">{c}</p>' for c in e['ch'])+(f'<p><span class="lb">필요한 개념</span> {e["need"]}</p>' if e['need'] else '')+'</div>'
    sub,subname=AREAMAP.get(area[no],('',''))
    data.append({'code':code,'no':no,'set':'mc','sub':'','subname':'','type':'','ans':str(ans[no]),'lv':'중','fam':'m%d%02d'%(rd,no),'q':qhtml,'exp':sol,'mock':rd,'pt':float(pt)})
json.dump(data,open(os.path.join(root,'cm/data.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
mp=os.path.join(root,'cm/mocks.json')
M=json.load(open(mp,encoding='utf8')) if os.path.exists(mp) else {}
M[str(rd)]={'title':'세포와 물질대사 실전 동형 모의고사 %d회'%rd,'codes':codes,'pts':{c:pts[i+1] for i,c in enumerate(codes)},'area':{c:area[i+1] for i,c in enumerate(codes)},
 'ex':{c:ex[i+1] for i,c in enumerate(codes)}}
json.dump(M,open(mp,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(len(codes),'문항',sum(float(v) for v in pts.values()))
