# -*- coding: utf-8 -*-
"""tools/capture_intro.js 가 찍은 PNG 를 intro/*.webp 로 바꾼다(데스크톱 앱 화면은 왼쪽 메뉴를 잘라 냄).
   python3 tools/intro_webp.py <png 폴더>"""
import sys, os
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else 'intro_png'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'intro')
os.makedirs(OUT, exist_ok=True)
SIDEBAR = 236 * 2  # 2배로 찍은 사이드바 너비
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.png'): continue
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    name = f[:-4]
    if name.startswith('app-'):
        im = im.crop((SIDEBAR, 0, im.width, im.height))
        w = 1400
    elif name.startswith('phone-'):
        w = 780
    else:
        w = 1000
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.webp')
    im.save(p, 'WEBP', quality=78, method=6)
    print('%-22s %4dx%-4d %5.0fKB' % (name, im.width, im.height, os.path.getsize(p) / 1024))
