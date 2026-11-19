# Owl keychain v4: round plush owl from 6 gores + bottom disc. Pillow only. Writes layout-v4.png next to this file.
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(s, b=False): return ImageFont.truetype(FB if b else F, s)

S = 60  # px per cm
RED, BROWN, CREAM, DARK, LINE, BG = (196, 52, 46), (96, 60, 38), (243, 233, 210), (40, 28, 20), (35, 30, 25), (251, 246, 236)
N = 6          # gores
H = 6.6        # body height without ears, cm
RB = 1.4       # bottom disc radius, cm

# meridian profile r(z), Catmull-Rom through control points
CP = [(0.0, RB), (0.5, 2.05), (1.5, 2.45), (2.8, 2.55), (4.2, 2.35), (5.3, 1.95), (6.1, 1.25), (6.6, 0.0)]
def catmull(pts, n=30):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    out.append(pts[-1])
    return out
PROF = catmull(CP)
# arc length along meridian
ARC = [0.0]
for a, b in zip(PROF, PROF[1:]): ARC.append(ARC[-1] + math.dist(a, b))
L = ARC[-1]
RMAX = max(r for _, r in PROF)
GW = 2 * math.pi * RMAX / N

img = Image.new('RGB', (1800, 2700), BG)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 1800, 80], fill=(62, 44, 32))
d.text((30, 18), 'Сова-брелок v4: совсем совообразная, клиньями', font=font(34, True), fill=(255, 250, 240))
d.text((30, 95), f'{N} клиньев + круглое дно Ø{2*RB:.1f} см + 2 уха. Высота тела {H} см (+уши 1.1), Ø пуза {2*RMAX:.1f} см. Клин: длина {L:.1f} см, ширина {GW:.2f} см.', font=font(22), fill=LINE)

def tr(ox, oy):
    return lambda x, y: (ox + x * S, oy - y * S)
def ell(cx, cy, rx, ry, n=48):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
def dim_v(x, y1, y2, txt):
    d.line([x, y1, x, y2], fill=LINE, width=2)
    for y in (y1, y2): d.line([x - 8, y, x + 8, y], fill=LINE, width=2)
    d.text((x + 10, (y1 + y2) / 2 - 12), txt, font=font(20), fill=LINE)
def dim_h(x1, x2, y, txt):
    d.line([x1, y, x2, y], fill=LINE, width=2)
    for x in (x1, x2): d.line([x, y - 8, x, y + 8], fill=LINE, width=2)
    tw = d.textlength(txt, font=font(20)); d.text(((x1 + x2) / 2 - tw / 2, y + 6), txt, font=font(20), fill=LINE)

SIL = [(r, z) for z, r in PROF] + [(-r, z) for z, r in reversed(PROF)]
def ears(t, side=1.0):
    for sx in (-1, 1):
        x0 = sx * 0.55 * side
        d.polygon([t(x0 - 0.5 * sx * side, 6.2), t(x0 + sx * 0.9 * side, 7.7), t(x0 + sx * 0.85 * side, 6.0)], fill=BROWN, outline=LINE)

# ---- Row 1: front, side, top
top = 780
d.text((30, 140), 'Три проекции', font=font(26, True), fill=LINE)
t = tr(300, top)
ears(t)
d.polygon([t(*p) for p in SIL], fill=RED, outline=LINE, width=3)
for poly, c in [(ell(0, 2.0, 1.7, 1.75), CREAM), (ell(0, 4.5, 2.0, 1.25), BROWN), (ell(-0.85, 4.55, 0.7, 0.7), (255, 255, 255)),
                (ell(0.85, 4.55, 0.7, 0.7), (255, 255, 255)), (ell(-0.85, 4.55, 0.28, 0.28), DARK), (ell(0.85, 4.55, 0.28, 0.28), DARK),
                ([(-0.3, 3.95), (0.3, 3.95), (0, 3.35)], BROWN), (ell(-2.2, 2.6, 0.45, 1.1), BROWN), (ell(2.2, 2.6, 0.45, 1.1), BROWN)]:
    d.polygon([t(*p) for p in poly], fill=c, outline=LINE)
# seams visible from front: at ±30° -> x = r*sin(30)
for sgn in (-1, 1):
    d.line([t(sgn * r * 0.5, z) for z, r in PROF], fill=(120, 30, 26), width=2)
d.text((180, top + 20), 'Спереди', font=font(22, True), fill=LINE)
dim_v(460, top - H * S, top, f'{H} см')
dim_h(300 - RMAX * S, 300 + RMAX * S, top + 60, f'{2*RMAX:.1f} см')
# side
t = tr(800, top)
d.polygon([t(*p) for p in SIL], fill=RED, outline=LINE, width=3)
d.polygon([t(0.2, 6.3), t(0.5, 7.7), t(0.9, 6.1)], fill=BROWN, outline=LINE)
d.polygon([t(*p) for p in ell(0.6, 2.6, 0.45, 1.1)], fill=BROWN, outline=LINE)
d.line([t(0, z) for z, r in PROF], fill=(120, 30, 26), width=2)
for z, r in PROF[::1]:
    pass
d.line([t(-r * math.sin(math.radians(60)), z) for z, r in PROF], fill=(120, 30, 26), width=2)
d.line([t(r * math.sin(math.radians(60)), z) for z, r in PROF], fill=(120, 30, 26), width=2)
d.text((720, top + 20), 'Сбоку', font=font(22, True), fill=LINE)
# top
cx, cy = 1350, top - 3.2 * S
d.ellipse([cx - RMAX * S, cy - RMAX * S, cx + RMAX * S, cy + RMAX * S], fill=RED, outline=LINE, width=3)
for k in range(N):
    a = math.radians(90 + 30 + 60 * k)
    d.line([cx, cy, cx + RMAX * S * math.cos(a), cy - RMAX * S * math.sin(a)], fill=(120, 30, 26), width=2)
for sx in (-1, 1):
    d.polygon([(cx + sx * 0.3 * S, cy - 0.2 * S), (cx + sx * 1.3 * S, cy - 0.45 * S), (cx + sx * 1.0 * S, cy + 0.25 * S)], fill=BROWN, outline=LINE)
d.text((cx - 120, cy + RMAX * S + 15), 'Сверху: 6 швов сходятся\nв макушке, клюв вперёд ↓', font=font(20), fill=LINE)

# ---- Row 2: gore pattern
gy = top + 140
d.text((30, gy), f'Развёртка: клин G ×{N} (одинаковые). Риски через 1 см по оси, точка ● = макушка, низ = к дну', font=font(26, True), fill=LINE)
gbase = gy + 60 + L * S  # bottom of gores (z=0) in px
def gore_poly(ox):
    left, right = [], []
    for (z, r), s in zip(PROF, ARC):
        w = math.pi * r / N
        right.append((ox + w * S, gbase - s * S)); left.append((ox - w * S, gbase - s * S))
    return right + left[::-1]
for k in range(N):
    ox = 140 + k * 200
    d.polygon(gore_poly(ox), fill=RED if k < 2 else (220, 120, 100), outline=LINE, width=3)
    d.line([ox, gbase, ox, gbase - L * S], fill=(255, 230, 220), width=1)
    for c in range(int(L) + 1):
        d.line([ox - 6, gbase - c * S, ox + 6, gbase - c * S], fill=LINE, width=2)
    d.ellipse([ox - 5, gbase - L * S - 5, ox + 5, gbase - L * S + 5], fill=DARK)
    d.text((ox - 20, gbase + 10), f'G{k+1}', font=font(22, True), fill=LINE)
# mark ear slots on G1/G2 seam, wing spots
es = next(s for (z, r), s in zip(PROF, ARC) if z >= 6.0)
d.text((140 + 6 * 200 - 60, gy + 70), f'Ширина max {GW:.2f} см\nна высоте ~2.8 см\nДлина по оси {L:.1f} см\nДно-край клина = {2*math.pi*RB/N:.2f} см\n\nG1+G2 (тёмные) = перед,\nна них морда и пузо.\nУши: в швы G6|G1 и G2|G3\nна {es:.1f} см от низа клина.', font=font(20), fill=LINE)
dim_h(140 - GW / 2 * S, 140 + GW / 2 * S, gbase + 45, f'{GW:.2f}')

# ---- Row 3: small parts
py = gbase + 110
d.text((30, py), 'Мелкие детали', font=font(26, True), fill=LINE)
cy2 = py + 150
x = 120
d.ellipse([x - RB * S, cy2 - RB * S, x + RB * S, cy2 + RB * S], fill=RED, outline=LINE, width=3)
for k in range(N):
    a = 2 * math.pi * k / N
    d.line([x + (RB - 0.2) * S * math.cos(a), cy2 + (RB - 0.2) * S * math.sin(a), x + RB * S * math.cos(a), cy2 + RB * S * math.sin(a)], fill=LINE, width=3)
d.text((x - 70, cy2 + RB * S + 10), f'D Дно ×1 Ø{2*RB:.1f}\nриски = 6 клиньев', font=font(18), fill=LINE)
x = 330
d.polygon([(x, cy2 + 0.6 * S), (x + 1.2 * S, cy2 + 0.6 * S), (x + 1.0 * S, cy2 - 0.9 * S)], fill=BROWN, outline=LINE, width=2)
d.text((x - 10, cy2 + 0.6 * S + 10), 'E Ухо ×4\n(по 2 склеить)\n1.2×1.5 см', font=font(18), fill=LINE)
parts = [('A1 Пузо ×1', ell(0, 0, 1.7, 1.75), CREAM, '3.4×3.5'), ('A2 Маска ×1', ell(0, 0, 2.0, 1.25), BROWN, '4.0×2.5'),
         ('A3 Глаз ×2', ell(0, 0, 0.7, 0.7), (255, 255, 255), 'Ø1.4'), ('A4 Зрачок ×2', ell(0, 0, 0.28, 0.28), DARK, 'Ø0.56'),
         ('A5 Крыло ×2', ell(0, 0, 0.45, 1.1), BROWN, '0.9×2.2')]
x = 520
for name, poly, c, sz in parts:
    w = max(p[0] for p in poly)
    d.polygon([(x + w * S + px * S, cy2 - py_ * S) for px, py_ in poly], fill=c, outline=LINE, width=2)
    d.text((x, cy2 + 1.9 * S), f'{name}\n{sz} см', font=font(18), fill=LINE)
    x += max(2 * w * S + 50, 150)
d.polygon([(x, cy2 + 0.3 * S), (x + 0.6 * S, cy2 + 0.3 * S), (x + 0.3 * S, cy2 - 0.3 * S)], fill=BROWN, outline=LINE, width=2)
d.text((x - 10, cy2 + 1.9 * S), 'A6 Клюв ×1\n0.6 см', font=font(18), fill=LINE)
x += 140
d.rectangle([x, cy2 - 1.75 * S, x + 1.2 * S, cy2 + 1.75 * S], fill=BROWN, outline=LINE, width=2)
d.text((x - 10, cy2 + 1.9 * S), 'H Петля ×1\n1.2×3.5', font=font(18), fill=LINE)

# ---- assembly + scale
by = cy2 + 2.9 * S
d.text((40, by), 'Сборка:', font=font(22, True), fill=LINE)
steps = ['1. Сшей G1+G2 по длинному краю: это перед. На него, пока плоский, пришей пузо, маску, глаза, клюв.',
         '2. Пришей крылья A5 на G6 и G3 (бочка), верх крыла на высоте ~3.5 см от низа клина.',
         '3. Сшивай клинья по кругу G2|G3, G3|G4 ... риски к рискам, вставляя уши E в швы G6|G1 и G2|G3.',
         '4. Последний шов G6|G1 оставь открытым на ~2 см снизу. Петлю H сгибом вверх вложи в макушку.',
         '5. Вшей дно D, риски на дне к швам клиньев. Набей плотно через дырку и зашей её.',
         'Кожа тонкая (0.6–0.8 мм), шов по краю наружу или выверни, если кожа мягкая. Макушку прошей крестом.']
for k, s in enumerate(steps):
    d.text((40, by + 40 + k * 32), s, font=font(20), fill=LINE)
bx, byy = 1250, gy + 440
d.rectangle([bx, byy, bx + 5 * S, byy + 14], outline=LINE, width=2)
for c in range(6): d.line([bx + c * S, byy, bx + c * S, byy + 22], fill=LINE, width=2)
d.text((bx, byy + 26), 'линейка 5 см: подгони масштаб\nпечати, чтоб была ровно 5 см', font=font(18), fill=LINE)
img = img.crop((0, 0, 1800, int(by + 40 + len(steps) * 32 + 30)))
img.save(os.path.join(HERE, 'layout-v4.png'))
print('L', round(L, 2), 'GW', round(GW, 2), 'bottom edge', round(2 * math.pi * RB / N, 2), 'ear s', round(es, 2))
