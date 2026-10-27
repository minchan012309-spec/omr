# -*- coding: utf-8 -*-
"""tools/capture_intro.js 가 찍은 PNG 를 intro/*.webp 로 바꾼다(앱 화면은 찍을 때 왼쪽 메뉴를 잘라 냄, 화질 88).
   python3 tools/intro_webp.py <png 폴더>"""
import sys, os
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else 'intro_png'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'intro')
os.makedirs(OUT, exist_ok=True)
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.png'): continue
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    name = f[:-4]
    if name.startswith('app-'):
        w = 2032
    elif name == 'kiosk':
        w = 1800
    elif name.startswith('phone-'):
        w = 780
    else:
        w = 1200
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.webp')
    im.save(p, 'WEBP', quality=88, method=6)
    print('%-22s %4dx%-4d %5.0fKB' % (name, im.width, im.height, os.path.getsize(p) / 1024))
