# -*- coding: utf-8 -*-
"""Ⅰ-A 힘의 합성과 분해 — 기준(예시) 생성기. 다른 생성기 파일은 이 파일의 문체·구조를 따른다."""
from phlib import *
import math

G = 10  # 중력 가속도 m/s²


@T('ph001')
def same_line_and_perp(r, k):
    """같은 직선 위의 힘 / 수직인 두 힘의 합력."""
    form = r.choice(['same', 'opp', 'perp', 'perp', 'three'])
    if form == 'same':
        a, b = r.randint(2, 15), r.randint(2, 15)
        right = a + b
        body = P('수평면 위의 물체에 오른쪽 방향으로 크기가 %s인 힘 F%s과 같은 방향으로 크기가 %s인 힘 F%s가 작용한다. 두 힘의 합력의 크기는?' % (U(a, 'N'), sub(1), U(b, 'N'), sub(2)))
        wrongs = [U(abs(a - b), 'N'), U(int(math.hypot(a, b)) if math.hypot(a, b) % 1 == 0 else a * b, 'N'), U(a + b + 2, 'N'), U(max(a, b), 'N'), U(a + b - 1, 'N'), U(a + b + 5, 'N')]
        return mc(body, U(right, 'N'), wrongs, r=r, lv='하', fam='a',
                  steps=['같은 방향의 두 힘의 합력은 크기를 더한다 : %d + %d = %d N' % (a, b, right)],
                  core='같은 방향의 힘은 크기를 더하고, 반대 방향의 힘은 크기를 뺀다.', point='힘의 방향을 확인하고 합력의 크기를 구한다.')
    if form == 'opp':
        a, b = r.randint(6, 20), r.randint(2, 12)
        if a == b: return None
        big, small = max(a, b), min(a, b)
        right = big - small
        body = P('한 직선 위에서 물체에 서로 반대 방향으로 크기가 %s인 힘과 %s인 힘이 작용한다. 두 힘의 합력의 크기는?' % (U(a, 'N'), U(b, 'N')))
        wrongs = [U(a + b, 'N'), U(big, 'N'), U(small, 'N'), U(right + 2, 'N'), U(abs(right - 3), 'N'), U(round(math.hypot(a, b)), 'N')]
        return mc(body, U(right, 'N'), wrongs, r=r, lv='하', fam='b',
                  steps=['반대 방향의 힘의 합력은 큰 힘에서 작은 힘을 뺀 값이다 : %d - %d = %d N' % (big, small, right), '방향은 큰 힘의 방향이다.'],
                  core='반대 방향의 두 힘의 합력의 크기는 두 힘의 크기의 차이다.', point='같은 직선 위의 힘은 방향을 먼저 구분한다.')
    if form == 'perp':
        a, b, c = r.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (12, 16, 20), (4, 3, 5), (12, 5, 13)])
        body = P('물체에 서로 수직인 두 힘 F%s, F%s가 작용한다. F%s의 크기는 %s이고 F%s의 크기는 %s일 때, 두 힘의 합력의 크기는?' % (sub(1), sub(2), sub(1), U(a, 'N'), sub(2), U(b, 'N')))
        wrongs = [U(a + b, 'N'), U(abs(a - b), 'N'), U(a * b // math.gcd(a, b), 'N'), U(c + 2, 'N'), U(c - 1, 'N'), U(max(a, b), 'N')]
        return mc(body, U(c, 'N'), wrongs, r=r, lv='중', fam='c',
                  steps=['수직인 두 힘의 합력의 크기는 피타고라스 정리로 구한다.', '√(%d² + %d²) = √%d = %d N' % (a, b, a * a + b * b, c)],
                  core='서로 수직인 두 힘의 합력의 크기는 √(F%s² + F%s²)이다.' % (sub(1), sub(2)), point='직각삼각형의 빗변으로 합력의 크기를 구한다.')
    # three: 같은 직선 위 세 힘
    a, b, c = r.randint(2, 12), r.randint(2, 12), r.randint(2, 12)
    right = abs(a + b - c)
    if right == 0: return None
    body = P('수평면 위의 물체에 오른쪽으로 %s, %s의 힘이, 왼쪽으로 %s의 힘이 작용한다. 세 힘의 합력의 크기는? (단, 세 힘은 한 직선 위에 있다.)' % (U(a, 'N'), U(b, 'N'), U(c, 'N')))
    wrongs = [U(a + b + c, 'N'), U(abs(a - b - c), 'N'), U(abs(a + c - b), 'N'), U(abs(b + c - a), 'N'), U(right + 1, 'N'), U(right + 3, 'N')]
    return mc(body, U(right, 'N'), wrongs, r=r, lv='중', fam='d',
              steps=['오른쪽을 +로 하면 합력 = %d + %d - %d = %d N' % (a, b, c, a + b - c), '합력의 크기는 %d N이다.' % right],
              core='같은 직선 위의 여러 힘은 방향에 부호를 주어 더한다.', point='방향별로 부호를 붙여 합산한다.')


def _vec_fig(ax, ay, bx, by, w=250, h=210, grid=24, show='AB'):
    """눈금(격자) 위의 두 벡터 A(ax,ay), B(bx,by)를 원점에서 그린다."""
    f = Fig(w, h)
    ox, oy = 30, h - 28
    nx, ny = int((w - 40) / grid), int((h - 40) / grid)
    for i in range(nx + 1):
        f.line(ox + i * grid, oy, ox + i * grid, oy - ny * grid, LG, 1)
    for j in range(ny + 1):
        f.line(ox, oy - j * grid, ox + nx * grid, oy - j * grid, LG, 1)
    f.arrow(ox, oy, ox + ax * grid, oy - ay * grid, RD, 2.4)
    f.arrow(ox, oy, ox + bx * grid, oy - by * grid, BL, 2.4)
    f.text(ox + ax * grid + 8, oy - ay * grid - 4, 'A', 14, 'start', True, RD, True)
    f.text(ox + bx * grid + 8, oy - by * grid - 4, 'B', 14, 'start', True, BL, True)
    f.text(ox - 8, oy + 15, '0', 11, 'end', c=GR)
    return f.svg()


@T('ph004')
def grid_vectors(r, k):
    """눈금 그림으로 읽는 벡터의 합과 차."""
    ax, ay = r.randint(1, 6), r.randint(0, 5)
    bx, by = r.randint(0, 6), r.randint(1, 5)
    if (ax, ay) == (bx, by) or (ax == 0 and ay == 0): return None
    if ax + bx > 8 or ay + by > 7: return None
    kind = r.choice(['sum', 'diff', 'comp'])
    fig = FIG(_vec_fig(ax, ay, bx, by), '55%')
    if kind == 'sum':
        sx, sy = ax + bx, ay + by
        val = sx * sx + sy * sy
        right = rad(1, val)
        d1 = (ax - bx) ** 2 + (ay - by) ** 2
        body = P('그림은 눈금 한 칸이 1 N인 모눈종이 위에 두 힘 A, B를 나타낸 것이다. 두 힘의 합력 A+B의 크기는?') + fig
        wrongs = [rad(1, d1) if d1 else '0', rad(1, ax * ax + ay * ay + bx * bx + by * by), str(sx + sy), str(abs(sx - sy) + 1), rad(1, val + 1), rad(1, val + 4)]
        return mc(body, right + ' N', [w + ' N' for w in wrongs], r=r, lv='중', fam='a', sort='shuf',
                  steps=['A = (%d, %d), B = (%d, %d)이므로 A+B = (%d, %d)이다.' % (ax, ay, bx, by, sx, sy), '|A+B| = √(%d² + %d²) = √%d = %s N' % (sx, sy, val, right)],
                  core='벡터의 합은 성분별로 더한 뒤 피타고라스 정리로 크기를 구한다.', point='모눈 눈금에서 가로·세로 성분을 읽는다.')
    if kind == 'diff':
        dx, dy = ax - bx, ay - by
        val = dx * dx + dy * dy
        if val == 0: return None
        right = rad(1, val)
        s2 = (ax + bx) ** 2 + (ay + by) ** 2
        body = P('그림은 눈금 한 칸이 1 N인 모눈종이 위에 두 힘 A, B를 나타낸 것이다. A-B의 크기는?') + fig
        wrongs = [rad(1, s2), str(abs(dx) + abs(dy)), rad(1, val + 1), rad(1, val + 3), rad(1, ax * ax + ay * ay)]
        return mc(body, right + ' N', [w + ' N' for w in wrongs], r=r, lv='상', fam='b', sort='shuf',
                  steps=['A-B = (%d-%d, %d-%d) = (%d, %d)이다.' % (ax, bx, ay, by, dx, dy), '|A-B| = √(%d² + %d²) = √%d = %s N' % (dx, dy, val, right)],
                  core='벡터의 차는 성분별로 빼고, 크기는 피타고라스 정리로 구한다.', point='A-B는 A+(-B)와 같다.')
    # comp: x,y 성분 합 묻기
    sx, sy = ax + bx, ay + by
    body = P('그림은 눈금 한 칸이 1 N인 모눈종이 위에 두 힘 A, B를 나타낸 것이다. 두 힘의 합력의 수평 성분과 연직 성분의 크기를 각각 구한 것은?') + fig
    right = '%d N, %d N' % (sx, sy)
    wrongs = ['%d N, %d N' % (sy, sx), '%d N, %d N' % (abs(ax - bx), abs(ay - by)), '%d N, %d N' % (sx, sy + 1), '%d N, %d N' % (sx + 1, sy), '%d N, %d N' % (ax, by), '%d N, %d N' % (bx, ay)]
    if sx == sy: return None
    return mc(body, right, wrongs, r=r, lv='하', fam='c', sort='shuf',
              steps=['수평 성분 : %d + %d = %d N, 연직 성분 : %d + %d = %d N' % (ax, bx, sx, ay, by, sy)],
              core='합력의 성분은 각 힘의 같은 방향 성분을 더한 값이다.', point='가로·세로 성분을 따로 합한다.')


def _incline_fig(theta, w=260, h=170):
    """빗면 위의 물체(경사각 theta). 그림 높이에 맞도록 빗면 길이를 줄여 그린다."""
    f = Fig(w, h)
    x0, y0 = 28, h - 18
    th = math.radians(theta)
    L = min(200 / math.cos(th), (h - 40) / math.sin(th))
    x1, y1 = x0 + L * math.cos(th), y0 - L * math.sin(th)
    f.poly([(x0, y0), (x1, y0), (x1, y1)], '#f1f4f8', INK, 1.8)
    t = 0.5
    px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    f.o.append('<g transform="rotate(%s %s %s)"><rect x="%s" y="%s" width="30" height="22" fill="#cfe2f7" stroke="%s" stroke-width="1.6"/></g>' % (Fig._n(-theta), Fig._n(px), Fig._n(py), Fig._n(px - 15), Fig._n(py - 22), INK))
    f.o.append('<path d="M %s %s A 34 34 0 0 0 %s %s" fill="none" stroke="%s" stroke-width="1.2"/>' % (Fig._n(x0 + 34), Fig._n(y0), Fig._n(x0 + 34 * math.cos(th)), Fig._n(y0 - 34 * math.sin(th)), GR))
    f.text(x0 + 46, y0 - 6, '%d°' % theta, 12.5, 'start', True, GR)
    return f.svg()


@T('ph006')
def incline_forces(r, k):
    """빗면 위 물체에 작용하는 힘."""
    theta = r.choice([30, 37, 45, 53, 60])
    m = r.choice([1, 2, 3, 4, 5, 6, 8, 10])
    s, c = {30: (0.5, math.sqrt(3) / 2), 37: (0.6, 0.8), 45: (math.sqrt(2) / 2, math.sqrt(2) / 2), 53: (0.8, 0.6), 60: (math.sqrt(3) / 2, 0.5)}[theta]
    W = m * G
    kind = r.choice(['par', 'perp', 'both', 'ratio'])
    fig = FIG(_incline_fig(theta), '56%')
    def val(x, kind_):  # 값 문자열(√ 포함)
        if theta in (37, 53): return num(W * x)
        if theta == 30: return num(W * x) if kind_ == 's' else rad(W // 2, 3) if W % 2 == 0 else '%s√3/2' % W
        if theta == 60: return rad(W // 2, 3) if W % 2 == 0 and kind_ == 's' else num(W * 0.5) if kind_ == 'c' else '%s√3/2' % W
        return rad(W // 2, 2) if W % 2 == 0 else '%s√2/2' % W
    base = '그림과 같이 경사각이 %d°인 마찰이 없는 빗면 위에 질량 %d kg인 물체가 정지해 있다. ' % (theta, m)
    if theta in (30, 37, 53) or (theta == 60) or theta == 45:
        pass
    if kind == 'par':
        rs = val(s, 's')
        body = P(base + '중력이 빗면 아래 방향으로 작용하는 성분의 크기는? (단, 중력 가속도는 10 m/s²이다.)') + fig
        wr = [val(c, 'c'), num(W), num(m * 5), num(W * 0.2), num(W + 10)]
        return mc(body, rs + ' N', [w + ' N' for w in wr], r=r, lv='중', fam='a', sort='shuf',
                  steps=['물체에 작용하는 중력의 크기는 mg = %d × 10 = %d N이다.' % (m, W), '빗면에 나란한 성분은 mg sin%d° = %d × sin%d° = %s N이다.' % (theta, W, theta, rs)],
                  core='경사각이 θ인 빗면에서 중력의 빗면 방향 성분은 mg sinθ, 수직 성분은 mg cosθ이다.', point='빗면에 나란한 성분과 수직인 성분을 구분한다.')
    if kind == 'perp':
        rs = val(c, 'c')
        body = P(base + '빗면이 물체를 수직으로 떠받치는 힘(수직 항력)의 크기는? (단, 중력 가속도는 10 m/s²이다.)') + fig
        wr = [val(s, 's'), num(W), num(m * 5), num(W * 0.2), num(W + 10)]
        return mc(body, rs + ' N', [w + ' N' for w in wr], r=r, lv='중', fam='b', sort='shuf',
                  steps=['물체가 정지해 있으므로 빗면에 수직인 방향의 합력은 0이다.', '수직 항력 N = mg cos%d° = %d × cos%d° = %s N' % (theta, W, theta, rs)],
                  core='빗면에서 수직 항력의 크기는 mg cosθ이다.', point='정지한 물체에서 수직 방향 힘의 평형을 이용한다.')
    if kind == 'both':
        rs, rc = val(s, 's'), val(c, 'c')
        body = P(base + '물체에 작용하는 마찰력의 크기와 수직 항력의 크기를 각각 구한 것은? (단, 중력 가속도는 10 m/s²이고, 빗면과 물체 사이에는 마찰력이 작용한다.)') + fig
        right = '%s N, %s N' % (rs, rc)
        wrongs = ['%s N, %s N' % (rc, rs), '%s N, %s N' % (num(W), rs), '%s N, %s N' % (rs, num(W)), '%s N, %s N' % (num(W * 0.5), rc), '%s N, %s N' % (rc, num(W))]
        return mc(body, right, wrongs, r=r, lv='상', fam='c', sort='shuf',
                  steps=['정지해 있으므로 빗면 방향 힘의 합이 0이다 : 정지 마찰력 = mg sin%d° = %s N' % (theta, rs), '수직 방향 : 수직 항력 = mg cos%d° = %s N' % (theta, rc)],
                  core='정지한 물체의 정지 마찰력은 빗면 방향 중력 성분과 같다.', point='빗면 방향과 수직 방향을 나누어 힘의 평형을 쓴다.')
    # ratio: 각도가 다른 두 빗면의 비교
    th2 = r.choice([t for t in (30, 37, 45, 53, 60) if t != theta])
    A, B = _SIN[theta], _SIN[th2]
    right = _ratio(A, B)
    wrongs = [_ratio(B, A), _ratio(_COS[theta], _COS[th2]), _ratio(_COS[th2], _COS[theta]), '1 : 1', _ratio(A, A) if False else '%d : %d' % (theta, th2)]
    body = P('경사각이 각각 %d°, %d°인 마찰이 없는 두 빗면에 질량이 같은 물체 A, B를 놓았다. 중력의 빗면 방향 성분의 크기를 각각 F%s, F%s라 할 때 F%s : F%s는?' % (theta, th2, sub('A'), sub('B'), sub('A'), sub('B')))
    return mc(body, right, wrongs, r=r, lv='상', fam='d', sort='shuf',
              steps=['F = mg sinθ 이므로 질량이 같으면 F%s : F%s = sin%d° : sin%d° 이다.' % (sub('A'), sub('B'), theta, th2), 'sin%d° = %s, sin%d° = %s 이므로 %s이다.' % (theta, _SINS[theta], th2, _SINS[th2], right)],
              core='중력의 빗면 방향 성분은 mg sinθ이므로 같은 질량이면 sinθ에 비례한다.', point='각도에 따른 sinθ 값을 비교한다.')


_SIN = {30: (1, 1, 2), 37: (3, 1, 5), 45: (1, 2, 2), 53: (4, 1, 5), 60: (1, 3, 2)}   # (분자 계수, 근호 안, 분모)
_COS = {30: (1, 3, 2), 37: (4, 1, 5), 45: (1, 2, 2), 53: (3, 1, 5), 60: (1, 1, 2)}
_SINS = {30: '1/2', 37: '3/5', 45: '√2/2', 53: '4/5', 60: '√3/2'}


def _ratio(A, B):
    """(n, rad, d) 두 값의 비 A : B 를 간단한 문자열로."""
    na, ra, da = A
    nb, rb, db = B
    x, y = na * db, nb * da
    g = math.gcd(x, y)
    x, y = x // g, y // g
    if ra == rb:
        return '%d : %d' % (x, y)
    def f(c, rr):
        return ('%s' % c if c != 1 or rr == 1 else '') + ('√%d' % rr if rr > 1 else '')
    return '%s : %s' % (f(x, ra), f(y, rb))


@T('ph008')
def balance_vs_reaction(r, k):
    """힘의 평형과 작용 반작용 구분(<보기>)."""
    pool = [
        ('책상 위에 놓인 책에 작용하는 중력과 책상이 책을 떠받치는 힘은 크기가 같고 방향이 반대이므로 작용 반작용 관계이다.', False, '두 힘은 모두 책에 작용하므로 힘의 평형 관계이다. 작용 반작용은 서로 다른 두 물체 사이에서 작용한다.'),
        ('책이 책상을 누르는 힘과 책상이 책을 떠받치는 힘은 작용 반작용 관계이다.', True, '두 힘은 책과 책상이 서로에게 작용하는 한 쌍의 힘이다.'),
        ('작용 반작용의 두 힘은 크기가 같고 방향이 반대이다.', True, '뉴턴 제3법칙이다.'),
        ('작용 반작용의 두 힘은 같은 물체에 작용하므로 합력이 0이다.', False, '작용 반작용의 두 힘은 서로 다른 물체에 작용하므로 합할 수 없다.'),
        ('물체가 등속 직선 운동을 하면 물체에 작용하는 알짜힘은 0이다.', True, '속도가 변하지 않으면 가속도가 0이므로 알짜힘이 0이다.'),
        ('물체에 작용하는 두 힘이 힘의 평형을 이루면 두 힘은 같은 물체에 작용한다.', True, '힘의 평형은 한 물체에 작용하는 힘의 합력이 0인 상태이다.'),
        ('정지해 있는 물체에는 힘이 작용하지 않는다.', False, '정지한 물체에도 여러 힘이 작용하며 그 합력이 0일 뿐이다.'),
        ('지구가 사과를 당기는 힘과 사과가 지구를 당기는 힘은 크기가 같다.', True, '작용 반작용 관계이므로 크기가 같다.'),
        ('사과가 지구로 떨어질 때 지구가 사과를 당기는 힘이 사과가 지구를 당기는 힘보다 크다.', False, '두 힘은 작용 반작용이므로 크기가 같다. 가속도가 다른 것은 질량이 다르기 때문이다.'),
        ('줄다리기에서 이긴 팀이 진 팀을 당기는 힘은 진 팀이 이긴 팀을 당기는 힘보다 크다.', False, '두 팀이 줄을 당기는 힘은 작용 반작용이므로 크기가 같다. 승패는 땅과의 마찰력으로 결정된다.'),
        ('물체에 작용하는 알짜힘이 0이면 물체는 반드시 정지해 있다.', False, '알짜힘이 0이면 정지하거나 등속 직선 운동을 한다.'),
        ('로켓이 가스를 뒤로 분출하면 가스가 로켓을 앞으로 미는 힘이 작용한다.', True, '로켓과 가스 사이의 작용 반작용이다.'),
        ('벽을 손으로 밀면 벽도 손을 같은 크기의 힘으로 민다.', True, '작용 반작용 법칙이다.'),
        ('마찰이 없는 수평면에서 등속으로 미끄러지는 물체에는 운동 방향으로 힘이 계속 작용한다.', False, '알짜힘이 0이면 등속 운동을 유지하므로 운동 방향의 알짜힘은 필요 없다.'),
    ]
    sel = r.sample(pool, 3)
    intro = '힘의 평형과 작용 반작용에 대한 설명으로 옳은 것만을 &lt;보기&gt;에서 있는 대로 고른 것은?'
    stm = [(s[0], s[1], s[2]) for s in sel]
    return bogi(intro, stm, r=r, ask='', lv='하', fam='a', core='힘의 평형은 한 물체에 작용하는 힘의 합이 0인 상태, 작용 반작용은 서로 다른 두 물체 사이의 한 쌍의 힘이다.', point='두 힘이 작용하는 물체가 같은지 다른지를 구분한다.')
