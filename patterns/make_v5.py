# Owl keychain v5: minimal cuts. 2 identical bodies (ears built into outline) + 1 oval bottom. Writes layout-v5.png.
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(s, b=False): return ImageFont.truetype(FB if b else F, s)
S = 80  # px per cm
RED, BROWN, CREAM, DARK, LINE, BG = (196, 52, 46), (96, 60, 38), (243, 233, 210), (40, 28, 20), (35, 30, 25), (251, 246, 236)

def catmull(pts, n=24):
    out = []; P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    out.append(pts[-1]); return out
def plen(p): return sum(math.dist(a, b) for a, b in zip(p, p[1:]))

# right half of body outline, from bottom corner up to centre-top dip (cm); ears are part of the outline
BW = 2.2  # half bottom width
RIGHT = catmull([(BW, 0.0), (2.65, 0.9), (2.8, 2.4), (2.55, 4.2), (2.35, 5.6), (2.45, 6.6), (2.3, 7.25), (1.6, 6.55), (0.8, 6.2), (0.0, 6.1)])
LEFT = [(-x, y) for x, y in reversed(RIGHT)]
BODY = [(-BW, 0.0), (BW, 0.0)] + RIGHT[1:] + LEFT[1:]
H = max(y for _, y in BODY); W = 2 * max(x for x, _ in BODY)
EDGE = 2 * BW  # bottom edge length that meets the oval
# oval perimeter must be 2*EDGE (front bottom + back bottom); fix depth b, solve a
B = 0.95
def per(a, b): return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))
lo, hi = 0.5, 5.0
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if per(m, B) < 2 * EDGE else (lo, m)
A = lo
SEAM = plen(RIGHT) * 2

img = Image.new('RGB', (1800, 1500), BG); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 1800, 80], fill=(62, 44, 32))
d.text((30, 18), 'Сова-брелок v5: минимум резов, 3 детали', font=font(34, True), fill=(255, 250, 240))
d.text((30, 95), f'2 одинаковых корпуса (уши в контуре) + овальное дно {2*A:.1f}×{2*B:.1f} см. Корпус {W:.1f}×{H:.1f} см. Шов 3 мм от края, припуска нет.', font=font(22), fill=LINE)
def tr(ox, oy): return lambda x, y: (ox + x * S, oy - y * S)
def ell(cx, cy, rx, ry, n=60): return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
def dim_v(x, y1, y2, txt):
    d.line([x, y1, x, y2], fill=LINE, width=2)
    for y in (y1, y2): d.line([x - 8, y, x + 8, y], fill=LINE, width=2)
    d.text((x + 10, (y1 + y2) / 2 - 12), txt, font=font(20), fill=LINE)
def dim_h(x1, x2, y, txt):
    d.line([x1, y, x2, y], fill=LINE, width=2)
    for x in (x1, x2): d.line([x, y - 8, x, y + 8], fill=LINE, width=2)
    tw = d.textlength(txt, font=font(20)); d.text(((x1 + x2) / 2 - tw / 2, y + 6), txt, font=font(20), fill=LINE)
def inset(poly, k=0.3):
    cx = sum(x for x, _ in poly) / len(poly); cy = sum(y for _, y in poly) / len(poly)
    out = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = poly[i - 1], poly[i], poly[(i + 1) % n]
        tx, ty = x2 - x0, y2 - y0; l = math.hypot(tx, ty) or 1
        nx, ny = -ty / l, tx / l
        if (cx - x1) * nx + (cy - y1) * ny < 0: nx, ny = -nx, -ny
        out.append((x1 + nx * k, y1 + ny * k))
    return out

# ---- piece 1: body (cut x2)
oy = 820; t = tr(330, oy)
d.text((60, 150), 'Деталь A: корпус, кроить 2 шт', font=font(26, True), fill=LINE)
d.polygon([t(*p) for p in BODY], fill=RED, outline=LINE, width=3)
d.line([t(*p) for p in inset(BODY)] + [t(*inset(BODY)[0])], fill=(255, 220, 200), width=1)
# face marks only on front (stamp/burn, no cutting)
for sx in (-1, 1):
    d.ellipse([*t(sx * 0.95 - 0.75, 4.95 + 0.75), *t(sx * 0.95 + 0.75, 4.95 - 0.75)], outline=CREAM, width=3)
    d.ellipse([*t(sx * 0.95 - 0.28, 4.95 + 0.28), *t(sx * 0.95 + 0.28, 4.95 - 0.28)], fill=DARK)
d.polygon([t(-0.3, 4.3), t(0.3, 4.3), t(0, 3.65)], outline=CREAM, width=3)
for y in (1.2, 1.8, 2.4):
    for x in (-0.7, 0, 0.7):
        d.arc([*t(x - 0.3, y + 0.3), *t(x + 0.3, y - 0.3)], 20, 160, fill=CREAM, width=2)
d.ellipse([*t(2.05 - 0.15, 6.75 + 0.15), *t(2.05 + 0.15, 6.75 - 0.15)], fill=BG, outline=LINE, width=2)
d.text(t(0.5, 7.45), 'дырка под кольцо', font=font(18), fill=LINE)
for sx in (-1, 1): d.text(t(sx * BW - (0.35 if sx < 0 else 0.0), -0.1), '●', font=font(18), fill=DARK)
dim_v(330 + 3.1 * S, oy - H * S, oy, f'{H:.1f} см')
dim_h(330 - W / 2 * S, 330 + W / 2 * S, oy + 40, f'{W:.1f} см')
dim_h(330 - BW * S, 330 + BW * S, oy + 95, f'низ {EDGE:.1f} см, ● метки под дно')

# ---- piece 2: oval bottom (cut x1)
t = tr(1050, 520)
d.text((830, 150), 'Деталь B: дно, кроить 1 шт', font=font(26, True), fill=LINE)
OV = ell(0, 0, A, B)
d.polygon([t(*p) for p in OV], fill=BROWN, outline=LINE, width=3)
for sx in (-1, 1): d.text(t(sx * A - 0.12, 0.15), '●', font=font(18), fill=CREAM)
dim_h(1050 - A * S, 1050 + A * S, 520 + B * S + 20, f'{2*A:.2f} см')
dim_v(1050 + A * S + 30, 520 - B * S, 520 + B * S, f'{2*B:.1f} см')
d.text((830, 700), f'Периметр овала = 2 × низ корпуса ({2*EDGE:.1f} см).\n● на концах овала совмещаешь с ● углов корпуса.', font=font(20), fill=LINE)

# ---- notes
notes = [
    'Резов: 3 контура (2 корпуса + 1 овал). Ни одного отдельного уха, глаза, клюва, петли.',
    'Уши выкроены в силуэте корпуса, рожки сова держат и без набивки.',
    'Совость без деталей: глаза оттиск круглым пробойником/кольцом + 2 холнитена',
    '  как зрачки, клюв и чешуйки пуза тиснением или выжигателем, только на переде.',
    'Сборка: 1) тиснение на переде  2) перёд + зад сшить по контуру от угла',
    '  до угла через уши  3) дно вшить по низу, совместив ●  4) оставить 2 см',
    '  на дне, набить плотно, дошить  5) кольцо в дырку в правом ухе (оба слоя).',
    f'Длина шва корпуса ~{SEAM:.1f} см + дно {2*EDGE:.1f} см. Для «совсем плоской» версии',
    '  дно выкинь: 2 детали, 2 реза, но стоять не будет.',
    'Печать 1:1 без «вписать в страницу», сверь линейку 5 см.',
]
y = 960
for n in notes:
    d.text((60, y), n, font=font(21), fill=LINE); y += 34
# scale bar
d.rectangle([1250, 1400, 1250 + 5 * S, 1412], fill=DARK); d.text((1250, 1420), '5 см (при печати 1:1)', font=font(18), fill=LINE)
img.save(os.path.join(HERE, 'layout-v5.png'))
print(f'W={W:.2f} H={H:.2f} oval={2*A:.2f}x{2*B:.2f} seam={SEAM:.1f}')
