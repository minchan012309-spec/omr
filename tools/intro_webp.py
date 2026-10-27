# -*- coding: utf-8 -*-
"""tools/capture_intro.js 가 찍은 PNG 를 intro/*.webp 로 바꾼다.
   python3 tools/intro_webp.py <png 폴더>
   크기: display 2400×1350(모니터 속 앱 전체) · app-* 1600×1000(본문만, 모두 같은 크기) · phone-* 780×1688 · book-*/mock-* 1000×1414(A4)
   app-mock 은 앱 화면 대신 모의고사 표지와 첫 쪽을 1600×1000 판에 나란히 놓아 다른 앱 화면과 크기를 맞춘다"""
import sys, os
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else 'intro_png'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'intro')
os.makedirs(OUT, exist_ok=True)
SKIP = ('kiosk', 'app-mock')  # 출결 단말은 소개 페이지에서 직접 눌러 보는 체험판으로 그린다
def save(im, name, q=86):
    p = os.path.join(OUT, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    print('%-18s %4dx%-4d %5.0fKB' % (name, im.width, im.height, os.path.getsize(p) / 1024))
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.png') or f.startswith(SKIP): continue
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    name = f[:-4]
    if name == 'display': size = (2400, 1350)
    elif name.startswith('app-'): size = (1600, 1000)
    elif name.startswith('phone-'): size = (780, 1688)
    else: size = (1000, round(im.height * 1000 / im.width))
    save(im.resize(size, Image.LANCZOS), name, 82 if name == 'display' else 86)
# 전범위 모의고사: 표지 + 첫 쪽을 앱 화면과 같은 1600×1000 판에
c, pg = os.path.join(SRC, 'mock-cover.png'), os.path.join(SRC, 'mock-page.png')
if os.path.exists(c) and os.path.exists(pg):
    board = Image.new('RGB', (1600, 1000), (236, 240, 246))
    h = 880; w = round(h / 1.4142)
    for i, src in enumerate((c, pg)):
        im = Image.open(src).convert('RGB').resize((w, h), Image.LANCZOS)
        board.paste(im, (800 - w - 24 + i * (w + 48), 60))
    save(board, 'app-mock')
