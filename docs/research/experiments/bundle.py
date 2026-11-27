# 발표 자료를 파일 하나로 묶기: python3 docs/research/experiments/bundle.py <출력.html>
# 글꼴은 발표에 쓰인 글자만 남겨(subset) base64로, 이미지 · CSS · 스크립트도 모두 안에 넣는다.
import base64, io, os, re, sys, json
from fontTools import subset
from fontTools.ttLib import TTFont

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = lambda *a: os.path.join(R, *a)
html = open(P('solvi-presentation.html'), encoding='utf-8').read()
css = open(P('lib/deck3.css'), encoding='utf-8').read()
ecss = open(P('lib/editor.css'), encoding='utf-8').read()
js = {n: open(P('lib', n), encoding='utf-8').read() for n in ('qrcode.js', 'data.js', 'deck3.js')}

# 쓰인 글자 모으기(문항 데이터 포함)
text = html + js['deck3.js'] + js['data.js']
chars = set(text)
chars |= set(''.join(chr(c) for c in range(0x20, 0x7f)))
chars |= set('①②③④⑤ㄱㄴㄷㄹ→←↑↓·…—–“”‘’「」『』×÷±≤≥√∞°%‰')
uni = sorted(ord(c) for c in chars if ord(c) > 0x1f)

def sub(path):
    f = TTFont(path)
    opt = subset.Options(); opt.flavor = 'woff2'; opt.layout_features = ['*']; opt.name_IDs = ['*']; opt.notdef_outline = True
    s = subset.Subsetter(opt); s.populate(unicodes=uni); s.subset(f)
    b = io.BytesIO(); f.flavor = 'woff2'; f.save(b)
    return 'data:font/woff2;base64,' + base64.b64encode(b.getvalue()).decode()

def font_repl(m):
    fn = m.group(1)
    return 'url(' + sub(P('fonts', fn)) + ')'
css = re.sub(r"url\(\.\./fonts/([^)]+)\)", font_repl, css)

# 이미지
imgs = {}
for p in re.findall(r"img/(?:app|erd|fig|cardnews)/[A-Za-z0-9_.-]+\.(?:webp|png|jpg)", html + js['deck3.js']):
    imgs[p] = p
for k in ['xdr-build', 'book-problem', 'mock-cover', 'xdr-dash', 'xdr-att', 'xdr-bill', 'xdr-cns', 'phone-omr', 'phone-result', 'phone-weak', 'phone-parent', 'xdr-weak', 'mac-thome']:
    imgs['img/app/%s.webp' % k] = 1
data = {}
for p in imgs:
    fp = P(p)
    if os.path.exists(fp):
        mime = 'image/webp' if p.endswith('.webp') else ('image/jpeg' if p.endswith('.jpg') else 'image/png')
        data[p] = 'data:%s;base64,%s' % (mime, base64.b64encode(open(fp, 'rb').read()).decode())
for p, d in data.items():
    html = html.replace('src="%s"' % p, 'src="%s"' % d)
fix = '''<script>window.IMGS=%s;(function(){function f(el){var s=el.getAttribute&&el.getAttribute('src');if(s&&window.IMGS[s])el.setAttribute('src',window.IMGS[s])}
new MutationObserver(function(ms){ms.forEach(function(m){if(m.type==='attributes'){f(m.target)}else m.addedNodes.forEach(function(n){if(n.nodeType!==1)return;if(n.tagName==='IMG')f(n);n.querySelectorAll&&n.querySelectorAll('img').forEach(f)})})}).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['src']});})();</script>''' % json.dumps(data)

html = html.replace('<link rel="stylesheet" href="lib/deck3.css">', '<style>' + css + '</style>')
html = html.replace('<link rel="stylesheet" href="lib/editor.css">', '<style>' + ecss + '</style>')
for n, src in js.items():
    html = html.replace('<script src="lib/%s"></script>' % n, '<script>' + src.replace('</script>', '<\\/script>') + '</script>')
html = html.replace('<body class="edit">', '<body class="edit">' + fix, 1)
out = sys.argv[1] if len(sys.argv) > 1 else P('solvi-presentation-single.html')
open(out, 'w', encoding='utf-8').write(html)
print(out, round(len(html.encode()) / 1048576, 2), 'MB', 'imgs', len(data))
