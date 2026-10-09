#!/usr/bin/env python3
"""내 컴퓨터에서만 쓸 때의 간이 서버. 실행: python3 server.py  ->  http://localhost:8765
(온라인 저장을 쓰면 이 서버는 필요 없습니다.) 결과는 results.json 에 누적됩니다."""
import json,os,http.server
D=os.path.dirname(os.path.abspath(__file__));R=os.path.join(D,'results.json')
def rd():
    try: return json.load(open(R,encoding='utf8'))
    except Exception: return []
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=D,**k)
    def _j(s,o,c=200):
        b=json.dumps(o,ensure_ascii=False).encode();s.send_response(c);s.send_header('Content-Type','application/json');s.send_header('Content-Length',str(len(b)));s.end_headers();s.wfile.write(b)
    def do_GET(s):
        if s.path=='/api/results': return s._j(rd())
        super().do_GET()
    def do_POST(s):
        if s.path!='/api/results': return s._j({},404)
        n=int(s.headers.get('Content-Length',0));h=rd();h.append(json.loads(s.rfile.read(n)))
        json.dump(h,open(R,'w',encoding='utf8'),ensure_ascii=False);s._j({'ok':1})
    def do_DELETE(s):
        json.dump([],open(R,'w'));s._j({'ok':1})
if __name__=='__main__':
    print('http://localhost:8765  (종료: Ctrl+C)');http.server.ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()
