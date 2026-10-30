# -*- coding: utf-8 -*-
"""tools/capture_intro.js · tools/capture_cine.js 가 찍은 PNG 를 intro/*.webp 로 바꾼다.
   python3 tools/intro_webp.py <png 폴더>
   크기: xdr-* 2400×1350(Pro Display 속 앱 전체) · mac-* 1800×1169 · pad-* 1112×1592 · kiosk 1592×1112 · cover-* 800×1131 · phone-* 780×1688 · book-*/mock-* 1000×1414(A4)"""
import sys, os
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else 'intro_png'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'intro')
os.makedirs(OUT, exist_ok=True)
SKIP = ()
def save(im, name, q=86):
    p = os.path.join(OUT, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    print('%-18s %4dx%-4d %5.0fKB' % (name, im.width, im.height, os.path.getsize(p) / 1024))
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.png') or f.startswith(SKIP): continue
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    name = f[:-4]
    if name.startswith('xdr-'): size = (2400, 1350)
    elif name.startswith('mac-'): size = (1800, 1169)
    elif name.startswith('pad-'): size = (1112, 1592)
    elif name == 'kiosk': size = (1592, 1112)
    elif name.startswith('cover-'): size = (800, 1131)
    elif name.startswith('phone-'): size = (780, 1688)
    else: size = (1000, round(im.height * 1000 / im.width))
    save(im.resize(size, Image.LANCZOS), name, 82 if name.startswith(('xdr-', 'mac-')) else 86)
