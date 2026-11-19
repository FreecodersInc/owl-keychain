# Owl keychain v3: boxing strip (variant 1). Pillow only. Writes layout-v3.png next to this file.
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(s, b=False): return ImageFont.truetype(FB if b else F, s)

S = 60  # px per cm
RED, BROWN, CREAM, DARK, LINE, BG = (196, 52, 46), (96, 60, 38), (243, 233, 210), (40, 28, 20), (35, 30, 25), (251, 246, 236)
H, W0 = 7.0, 5.0

ctrl = [(0, 0), (1.6, 0.25), (2.4, 1.2), (2.5, 3.0), (2.3, 4.8), (2.1, 6.2), (2.0, 7.0), (1.2, 6.2), (0, 6.0),
        (-1.2, 6.2), (-2.0, 7.0), (-2.1, 6.2), (-2.3, 4.8), (-2.5, 3.0), (-2.4, 1.2), (-1.6, 0.25)]
def chaikin(p, n=4):
    for _ in range(n):
        q = []
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        p = q
    return p
OUT = chaikin(ctrl)
ymin = min(p[1] for p in OUT); ymax = max(p[1] for p in OUT)
xmax = max(p[0] for p in OUT)
OUT = [(x * 2.5 / xmax, (y - ymin) * H / (ymax - ymin)) for x, y in OUT]

def gw(y):  # boxing strip width, cm: 2.0 at bottom -> 1.0 at ear tips
    return 2.0 - 1.0 * (y / H)
def puff(y):
    return 0.35 * math.sin(math.pi * min(max(y / 6.2, 0), 1))

# perimeter
seg = [math.dist(OUT[i], OUT[(i + 1) % len(OUT)]) for i in range(len(OUT))]
PER = sum(seg)

img = Image.new('RGB', (1800, 2900), BG)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 1800, 80], fill=(62, 44, 32))
d.text((30, 18), 'Сова-брелок v3: объём бочком. Три проекции, изометрия, развёртка', font=font(34, True), fill=(255, 250, 240))
d.text((30, 95), f'Вариант 1: перед + зад + бочок 2.0→1.0 см по контуру. Высота 7.0 см, ширина 5.0 см, периметр ≈ {PER:.1f} см. Шов по краю, припуск не нужен.', font=font(22), fill=LINE)

def tr(ox, oy, s=S):
    return lambda x, y: (ox + x * s, oy - y * s)

def appliques(P, front=True):
    # belly, head, eyes, beak, wings in front-view coords (cm)
    def ell(cx, cy, rx, ry, n=48):
        return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
    return [(ell(0, 2.0, 1.6, 1.9), CREAM), (ell(0, 5.0, 2.2, 1.3), BROWN), (ell(-1.0, 5.0, 0.75, 0.75), (255, 255, 255)),
            (ell(1.0, 5.0, 0.75, 0.75), (255, 255, 255)), (ell(-1.0, 5.0, 0.3, 0.3), DARK), (ell(1.0, 5.0, 0.3, 0.3), DARK),
            ([(-0.35, 4.3), (0.35, 4.3), (0, 3.65)], BROWN), (ell(-2.05, 2.6, 0.55, 1.2), BROWN), (ell(2.05, 2.6, 0.55, 1.2), BROWN)]

def dim_h(x1, x2, y, txt):
    d.line([x1, y, x2, y], fill=LINE, width=2)
    for x in (x1, x2): d.line([x, y - 8, x, y + 8], fill=LINE, width=2)
    tw = d.textlength(txt, font=font(20)); d.text(((x1 + x2) / 2 - tw / 2, y + 6), txt, font=font(20), fill=LINE)
def dim_v(x, y1, y2, txt):
    d.line([x, y1, x, y2], fill=LINE, width=2)
    for y in (y1, y2): d.line([x - 8, y, x + 8, y], fill=LINE, width=2)
    d.text((x + 10, (y1 + y2) / 2 - 12), txt, font=font(20), fill=LINE)

# ---- Row 1: three projections
top = 720
d.text((30, 135), 'Три проекции', font=font(26, True), fill=LINE)
# front
t = tr(260, top)
d.polygon([t(*p) for p in OUT], fill=RED, outline=LINE, width=3)
for poly, c in appliques(None):
    d.polygon([t(*p) for p in poly], fill=c, outline=LINE)
d.text((150, 175), 'Вид спереди', font=font(24, True), fill=LINE)
dim_h(t(-2.5, 0)[0], t(2.5, 0)[0], top + 25, '5.0')
dim_v(t(2.5, 0)[0] + 25, t(0, 7)[1], top, '7.0')

# side: depth = gusset + puff both sides
sx0 = 720
t = tr(sx0, top)
ys = [i * H / 60 for i in range(61)]
right = [(gw(y) / 2 + puff(y), y) for y in ys]
left = [(-gw(y) / 2 - puff(y), y) for y in reversed(ys)]
side = right + left
d.polygon([t(*p) for p in side], fill=RED, outline=LINE, width=3)
d.polygon([t(*p) for p in [(gw(y) / 2, y) for y in ys] + [(-gw(y) / 2, y) for y in reversed(ys)]], fill=BROWN, outline=LINE)
d.text((sx0 - 70, 175), 'Вид сбоку', font=font(24, True), fill=LINE)
dim_h(t(-1.0, 0)[0], t(1.0, 0)[0], top + 25, 'дно 2.0')
dim_h(t(-0.5, 7)[0], t(0.5, 7)[0], t(0, 7)[1] - 45, 'уши 1.0')
d.text((sx0 + 90, top - 220), 'набивка\n+3..4 мм\nс каждой\nстороны', font=font(18), fill=LINE)

# top view
tx0, ty0 = 1260, 480
t = tr(tx0, ty0)
dmid = gw(3.0) + 2 * puff(3.0)
topv = [(2.5 * math.copysign(abs(math.cos(a)) ** 0.6, math.cos(a)), dmid / 2 * math.copysign(abs(math.sin(a)) ** 0.8, math.sin(a))) for a in [2 * math.pi * k / 80 for k in range(80)]]
d.polygon([t(*p) for p in topv], fill=RED, outline=LINE, width=3)
for ex in (-2.0, 2.0):
    d.rounded_rectangle([t(ex - 0.25, 0.5)[0], t(0, 0.5)[1], t(ex + 0.25, -0.5)[0], t(0, -0.5)[1]], radius=8, fill=BROWN, outline=LINE)
d.text((tx0 - 80, 175), 'Вид сверху', font=font(24, True), fill=LINE)
d.text((tx0 - 160, ty0 + 90), 'перёд снизу на картинке', font=font(18), fill=LINE)
dim_h(t(-2.5, 0)[0], t(2.5, 0)[0], ty0 + 120, '5.0')
dim_v(t(2.5, 0)[0] + 20, t(0, dmid / 2)[1], t(0, -dmid / 2)[1], f'{dmid:.1f}')

# ---- Row 2: isometric
iy = 1360
d.text((30, 820), 'Изометрия', font=font(26, True), fill=LINE)
th, ph = math.radians(-35), math.radians(22)
def proj(x, y, z):
    x1 = x * math.cos(th) + z * math.sin(th); z1 = -x * math.sin(th) + z * math.cos(th)
    y2 = y * math.cos(ph) - z1 * math.sin(ph); z2 = y * math.sin(ph) + z1 * math.cos(ph)
    return (x1, y2, z2)
IS = 70
def scr(p, ox=520): return (ox + p[0] * IS, iy - p[1] * IS)
n = len(OUT)
fr = [proj(x, y, gw(y) / 2 + puff(y) * 0.5) for x, y in OUT]
bk = [proj(x, y, -gw(y) / 2 - puff(y) * 0.5) for x, y in OUT]
quads = []
for i in range(n):
    j = (i + 1) % n
    q = [fr[i], fr[j], bk[j], bk[i]]
    ax, ay = q[1][0] - q[0][0], q[1][1] - q[0][1]; bx, by = q[3][0] - q[0][0], q[3][1] - q[0][1]
    nz = ax * by - ay * bx
    quads.append((sum(p[2] for p in q) / 4, nz, q))
d.polygon([scr(p) for p in bk], fill=(70, 44, 28), outline=LINE)
for z, nz, q in sorted(quads, key=lambda t: t[0]):
    if nz < 0:
        d.polygon([scr(p) for p in q], fill=BROWN, outline=(70, 44, 28))
d.polygon([scr(p) for p in fr], fill=RED, outline=LINE, width=3)
for poly, c in appliques(None):
    pts = []
    for x, y in poly:
        pts.append(scr(proj(x, y, gw(y) / 2 + puff(y) * 0.5 + 0.02)))
    d.polygon(pts, fill=c, outline=LINE)
# keyring loop
lp = scr(proj(0, 6.0, 0)); d.ellipse([lp[0] - 10, lp[1] - 70, lp[0] + 10, lp[1] - 5], outline=BROWN, width=8)
d.ellipse([lp[0] - 45, lp[1] - 150, lp[0] + 45, lp[1] - 60], outline=(150, 150, 150), width=7)
d.text((900, 880), 'Как работает объём:', font=font(24, True), fill=LINE)
for k, s in enumerate(['Перед и зад одной формы, между ними бочок.',
                      'Бочок шире внизу (2 см): сова стоит сама.',
                      'К ушам сужается до 1 см: голова не раздута.',
                      'Набивка выгибает перед и зад ещё на 3..4 мм.',
                      'Итог: толщина ~2.4 см в пузе, а не бутерброд.',
                      'Петля под кольцо в верхнем шве между ушами.']):
    d.text((900, 925 + k * 38), '• ' + s, font=font(21), fill=LINE)

# ---- Row 3: development
ry = 1500
d.rectangle([20, ry, 1780, 2880], outline=LINE, width=2)
d.text((40, ry + 15), 'Развёртка (кроить по этим деталям)', font=font(26, True), fill=LINE)
t = tr(230, ry + 520)
d.polygon([t(*p) for p in OUT], fill=RED, outline=LINE, width=3)
d.text((120, ry + 535), 'B1 Перед ×1 (красный)', font=font(20, True), fill=LINE)
t = tr(600, ry + 520)
d.polygon([t(*p) for p in OUT], fill=BROWN, outline=LINE, width=3)
d.text((500, ry + 535), 'B2 Зад ×1 (тёмно-кор.)', font=font(20, True), fill=LINE)
# match marks: every 1 cm of perimeter from bottom centre, on B1/B2
for ox, col in ((230, (255, 255, 255)), (600, (255, 255, 255))):
    t = tr(ox, ry + 520); acc = 0; nxt = 1.0
    for i in range(n):
        a, b = OUT[i], OUT[(i + 1) % n]; L = seg[i]
        while acc + L >= nxt:
            f = (nxt - acc) / L; p = (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))
            P = t(*p); d.ellipse([P[0] - 3, P[1] - 3, P[0] + 3, P[1] + 3], fill=col)
            nxt += 1.0
        acc += L
# strip G1/G2: half perimeter each, from bottom centre to top centre
half = PER / 2
pts_s = [0.0]; ys_s = [OUT[0][1]]
for i in range(n // 2):
    pts_s.append(pts_s[-1] + seg[i]); ys_s.append(OUT[(i + 1) % n][1])
sx, sy0 = 900, ry + 160
SS = S
top_e = []; bot_e = []
for s, y in zip(pts_s, ys_s):
    w = gw(y)
    top_e.append((sx + s * SS, sy0 + (1.0 - w / 2) * SS)); bot_e.append((sx + s * SS, sy0 + (1.0 + w / 2) * SS))
strip_len = pts_s[-1]
# fold to fit: draw in two rows if too long
maxw = 1760 - sx
if strip_len * SS > maxw:
    cut = maxw / SS - 0.3
    rows = []
    for r in range(2):
        a, b = r * cut, min(strip_len, (r + 1) * cut)
        te = [(x - r * cut * SS, y + r * 3.2 * SS) for (x, y), s in zip(top_e, pts_s) if a <= s <= b]
        be = [(x - r * cut * SS, y + r * 3.2 * SS) for (x, y), s in zip(bot_e, pts_s) if a <= s <= b]
        rows.append((te, be, a, b))
else:
    rows = [(top_e, bot_e, 0, strip_len)]
for k, (te, be, a, b) in enumerate(rows):
    d.polygon(te + list(reversed(be)), fill=BROWN, outline=LINE, width=3)
    for c in range(int(a) + 1, int(b) + 1):
        X = sx + (c - a) * SS
        d.line([X, te[0][1] + 0 if False else sy0 + k * 3.2 * SS + 0.0 * SS + 30, X, sy0 + k * 3.2 * SS + 2.0 * SS - 30], fill=(230, 210, 190), width=1)
        d.text((X - 8, sy0 + k * 3.2 * SS + 2.0 * SS + 4), str(c), font=font(14), fill=LINE)
    if k < len(rows) - 1:
        d.text((te[-1][0] + 6, te[-1][1] + 20), '→ продолж.', font=font(16), fill=LINE)
d.text((sx, ry + 60), f'G1 + G2 Бочок ×2 (зеркально), каждая ≈ {strip_len:.1f} см + 0.5 см на стык', font=font(21, True), fill=LINE)
d.text((sx, ry + 95), 'Широкий край 2.0 см = низ (центр дна), узкий 1.0 см = верх между ушами.', font=font(19), fill=LINE)
d.text((sx, ry + 120), 'Цифры = см вдоль бочка, совмещай с белыми рисками на B1/B2.', font=font(19), fill=LINE)
# appliques row
ay = ry + 760
d.text((40, ay - 60), 'Аппликации на B1 (как в v2):', font=font(22, True), fill=LINE)
t = tr(160, ay + 160)
for poly, c in appliques(None):
    pass
items = [('A1 Брюшко ×1', 1.6, 1.9, CREAM), ('A2 Голова ×1', 2.2, 1.3, BROWN), ('A3 Глаз ×2', 0.75, 0.75, (255, 255, 255)), ('A4 Крыло ×2', 0.55, 1.2, BROWN)]
x = 60
for name, rx, ryy, c in items:
    cx = x + rx * S; cy = ay + 140
    d.ellipse([cx - rx * S, cy - ryy * S, cx + rx * S, cy + ryy * S], fill=c, outline=LINE, width=2)
    d.text((x, cy + ryy * S + 10), f'{name}\n{2*rx:.1f}×{2*ryy:.1f} см', font=font(18), fill=LINE)
    x += 2 * rx * S + 60
cx = x + 30; cy = ay + 140
d.polygon([(cx - 0.35 * S, cy - 0.35 * S), (cx + 0.35 * S, cy - 0.35 * S), (cx, cy + 0.35 * S)], fill=BROWN, outline=LINE)
d.text((x, cy + 40), 'A5 Клюв ×1\n0.7 см', font=font(18), fill=LINE)
x += 160
d.rectangle([x, cy - 1.75 * S, x + 1.2 * S, cy + 1.75 * S], fill=BROWN, outline=LINE, width=2)
d.text((x - 10, cy + 1.75 * S + 10), 'H1 Петля ×1\n1.2×3.5 см', font=font(18), fill=LINE)
# assembly
by = ay + 380
d.text((40, by), 'Сборка:', font=font(22, True), fill=LINE)
steps = ['1. Пришей аппликации на B1, пока он плоский.',
         '2. Сшей G1 и G2 широкими концами: это центр дна.',
         '3. Пришей бочок к B1 по контуру, риски к рискам, узкие концы сойдутся между ушами.',
         '4. Вложи петлю H1 сгибом вверх в стык бочков между ушами.',
         '5. Пришей B2 к другому краю бочка, оставь дырку ~2 см на боку.',
         '6. Набей плотно (пузо выгнется само), зашей дырку. Кольцо на петлю.']
for k, s in enumerate(steps):
    d.text((40, by + 40 + k * 32), s, font=font(20), fill=LINE)
# scale bar 5 cm
bx, byy = 1180, by + 60
d.rectangle([bx, byy, bx + 5 * S, byy + 14], outline=LINE, width=2)
for c in range(6): d.line([bx + c * S, byy, bx + c * S, byy + 22], fill=LINE, width=2)
d.text((bx, byy + 26), 'линейка 5 см (на экране)', font=font(18), fill=LINE)
d.text((bx, byy + 60), 'Для печати 1:1 подгони\nмасштаб, чтоб линейка = 5 см.\nВсе детали в одном масштабе.', font=font(18), fill=LINE)
img.save(os.path.join(HERE, 'layout-v3.png'))
print('perimeter', round(PER, 2), 'strip', round(strip_len, 2))
