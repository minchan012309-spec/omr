#!/usr/bin/env python3 -I
"""기존 교재 HTML(세포와 물질대사·물질과 에너지)에서 디자인(CSS)과 표지·구분 쪽 서식을 뽑아 books/old-*.json 으로 저장한다.
사용: python3 -I tools/extract_old.py <cm교재.html> <me교재.html>"""
import sys,re,json,os
from bs4 import BeautifulSoup
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def strip(s):return re.sub(r'data:[^"\')]{200,}','DATA',s)
def conv_css(css):
    css=re.sub(r"@font-face\{[^}]*\}\s*",'',css)
    css=css.replace("'Paperozi','Paperlogy',","Pretendard,").replace("'Paperozi'","Pretendard").replace("Paperozi","Pretendard")
    css=re.sub(r'(^|\})\s*:root\{',r'\1.bko{',css)
    css=re.sub(r'(^|\})\s*body\{',r'\1.bko{',css)
    css=re.sub(r'(^|\})\s*html\{',r'\1.bko{',css)
    css=css.replace('@media print{body{','@media print{.bko{').replace('@media print{html,body{','@media print{.bko{')
    css=css.replace(':root',' .bko')
    return css
def inner(el):return ''.join(str(c) for c in el.contents)
def build(path,tag):
    s=strip(open(path,encoding='utf8').read())
    soup=BeautifulSoup(s,'lxml')
    css=s[s.find('<style>')+7:s.find('</style>')]
    pages=soup.select('section.page')
    T={'css':conv_css(css)}
    # 학교·책 이름
    h=pages[5].select_one('.hdr b').get_text()
    T['hdr']=h
    T['school']=h.split(' ')[0]
    def page_inner(p):return inner(p)
    # 표지
    T['cfront']=inner(pages[0])
    T['cover2']=inner(pages[1])
    T['backc']=inner(pages[-1]) if 'backc' in pages[-1].get('class',[]) else ''
    # 차례·사용법
    T['toc']=inner(pages[2]);T['guide']=inner(pages[3])
    # 구분 쪽(old 챕터번호 → html)
    div={};sub=[]
    for p in pages:
        c=p.get('class',[])
        if 'divp' in c:
            no=p.select_one('.bigno').get_text().strip()
            div[no]=inner(p)
        if 'subp' in c: sub.append(inner(p))
    T['divp']=div;T['subp']=sub
    # 소단원 머리 블록 (h2.sec 가 있는 .blk)
    subhead={}
    for p in pages:
        for h2 in p.select('h2.sec'):
            no=h2.select_one('.no')
            if not no: continue
            k=no.get_text().strip()
            if re.match(r'^[ⅠⅡⅢⅣⅤ]+-[A-Z]$',k) and k not in subhead:
                blk=h2.find_parent(class_='blk')
                small=blk.select_one('h2.sec small')
                if small: small.clear(); small.string='[[REFSUB:'+k+']]'
                subhead[k]=inner(blk)
    T['subhead']=subhead
    return T
a,b=sys.argv[1],sys.argv[2]
for tag,path in (('cm',a),('me',b)):
    T=build(path,tag)
    json.dump(T,open(os.path.join(root,'books/old-%s.json'%tag),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(tag,{k:(len(v) if hasattr(v,'__len__') else v) for k,v in T.items()},list(T['divp']),list(T['subhead']))
