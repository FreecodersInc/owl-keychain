# Owl keychain v6: round owl from 4 gores + bottom disc + 2 ears (+ optional face appliques).
# Workshop drawings: 2-page A4 PDF at true 1:1 (300 dpi), DXF (mm, layers CUT/STITCH/HOLES/NOTCH/TEXT), SVG, PNG preview.
# Pillow only. All outputs go next to this file.
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(pt, b=False): return ImageFont.truetype(FB if b else F, int(pt * 300 / 72))

DPI = 300; PX = DPI / 25.4          # px per mm
W, H = 2480, 3508                   # A4 portrait @300 dpi
N = 4                               # gores
SA = 4.0                            # seam allowance, mm
PITCH = 3.0                         # stitch hole pitch, mm
RB = 14.0                           # bottom disc stitch radius, mm
INK, GREY, RED = (0, 0, 0), (110, 110, 110), (200, 30, 30)

# meridian profile (z, r) in mm, stitch line
CP = [(0, RB), (5, 20.5), (15, 24.5), (28, 25.5), (42, 23.5), (53, 19.5), (61, 12.5), (66, 0)]
def catmull(pts, n=40):
    out = []; P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    out.append(pts[-1]); return out
PROF = catmull(CP)
ARC = [0.0]
for a, b in zip(PROF, PROF[1:]): ARC.append(ARC[-1] + math.dist(a, b))
L = ARC[-1]; RMAX = max(r for _, r in PROF)
HMAX = 66.0
def half_w(r): return math.pi * r / N

# ---------- geometry (mm, y up, origin = piece local) ----------
def gore_stitch():
    right = [(half_w(r), s) for (z, r), s in zip(PROF, ARC)]
    left = [(-x, y) for x, y in reversed(right)]
    return right + left[1:-1]
def ear_stitch():   # base on y=0 (goes into seam), tip up-out
    return [(-5, 0), (5, 0), (3.5, 8), (1.5, 15), (-2.5, 9)]
def circle(cx, cy, r, n=96): return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
def ellipse(cx, cy, rx, ry, n=96): return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]

def offset(poly, d):
    # outward offset of a CCW-ish closed polygon via averaged edge normals
    n = len(poly); area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    out = []
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
        def nrm(a, b):
            dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1
            return (sgn * dy / l, -sgn * dx / l)
        n1, n2 = nrm(p0, p1), nrm(p1, p2)
        nx, ny = n1[0] + n2[0], n1[1] + n2[1]; ln = math.hypot(nx, ny) or 1
        nx, ny = nx / ln, ny / ln
        cosh = max(0.35, nx * n1[0] + ny * n1[1])
        k = d / cosh
        out.append((p1[0] + nx * k, p1[1] + ny * k))
    return out

def resample(path, step):
    pts = [path[0]]; acc = 0.0
    for a, b in zip(path, path[1:]):
        seg = math.dist(a, b); t0 = 0.0
        while acc + seg - t0 >= step:
            t0 += step - acc; acc = 0.0
            f = t0 / seg; pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
        acc += seg - t0
    return pts

def gore_edge_holes():
    right = [(half_w(r), s) for (z, r), s in zip(PROF, ARC)]
    return resample(right, PITCH)
HOLES_PER_SIDE = len(gore_edge_holes())
EAR_S = next(s for (z, r), s in zip(PROF, ARC) if z >= 54)    # ear base center on the seam (arc from bottom)

# ---------- page drawing ----------
class Page:
    def __init__(self):
        self.img = Image.new('RGB', (W, H), 'white'); self.d = ImageDraw.Draw(self.img)
        self.dxf = []   # (layer, kind, data) in page mm coords, y down
    def P(self, x, y): return (x * PX, y * PX)
    def poly(self, pts, ox, oy, width=0.35, color=INK, dash=None, layer=None, flip=True):
        q = [(ox + x, oy - y if flip else oy + y) for x, y in pts]
        if layer: self.dxf.append((layer, 'poly', q))
        px = [self.P(*p) for p in q] + [self.P(*q[0])]
        if dash:
            pts2 = resample([ (a / PX, b / PX) for a, b in px], dash)
            for i in range(0, len(pts2) - 1, 2):
                self.d.line([self.P(*pts2[i]), self.P(*pts2[i + 1])], fill=color, width=max(1, int(width * PX)))
        else:
            self.d.line(px, fill=color, width=max(1, int(width * PX)), joint='curve')
        return q
    def line(self, a, b, width=0.25, color=INK, layer=None):
        if layer: self.dxf.append((layer, 'line', [a, b]))
        self.d.line([self.P(*a), self.P(*b)], fill=color, width=max(1, int(width * PX)))
    def hole(self, x, y, r=0.5, layer='HOLES'):
        self.dxf.append((layer, 'circle', (x, y, r)))
        self.d.ellipse([self.P(x - r, y - r), self.P(x + r, y + r)], fill=INK)
    def text(self, x, y, s, pt=8, b=False, color=INK, layer=None, anchor='la'):
        self.d.text(self.P(x, y), s, font=font(pt, b), fill=color, anchor=anchor if '\n' not in s else None)
        if layer: self.dxf.append((layer, 'text', (x, y, s.split('\n')[0], pt * 0.3528)))
    def dim_h(self, x1, x2, y, s):
        self.line((x1, y), (x2, y), 0.18, GREY)
        for x in (x1, x2): self.line((x, y - 1.5), (x, y + 1.5), 0.18, GREY)
        self.text((x1 + x2) / 2, y - 1, s, 7, anchor='md', color=GREY)
    def dim_v(self, x, y1, y2, s):
        self.line((x, y1), (x, y2), 0.18, GREY)
        for y in (y1, y2): self.line((x - 1.5, y), (x + 1.5, y), 0.18, GREY)
        self.text(x + 1.5, (y1 + y2) / 2, s, 7, anchor='lm', color=GREY)
    def frame(self, sheet, title):
        self.d.rectangle([self.P(10, 10), self.P(200, 287)], outline=INK, width=int(0.5 * PX))
        # title block 190x22 at bottom
        y0 = 265
        self.d.rectangle([self.P(10, y0), self.P(200, 287)], outline=INK, width=int(0.35 * PX))
        for x in (95, 130, 165): self.line((x, y0), (x, 287), 0.25)
        self.line((95, 276), (200, 276), 0.25)
        self.text(13, y0 + 3, 'Брелок «Сова объёмная» v6', 10, True)
        self.text(13, y0 + 10, title, 8)
        self.text(13, y0 + 16, 'Проект owl-keychain · заказчик Л. Блохин', 6.5, color=GREY)
        for (x, y, s) in [(97, y0 + 2, 'Масштаб'), (97, y0 + 6, '1:1'), (132, y0 + 2, 'Ед. изм.'), (132, y0 + 6, 'мм'),
                          (167, y0 + 2, 'Лист'), (167, y0 + 6, f'{sheet} / 2'), (97, 278, 'Формат A4, печать 100%, без «вписать»'),]:
            self.text(x, y, s, 6.5 if y in (y0 + 2, 278) else 9, b=(y == y0 + 6))
    def check_square(self, x, y):
        self.d.rectangle([self.P(x, y), self.P(x + 50, y + 50)], outline=INK, width=int(0.3 * PX))
        self.text(x + 25, y + 25, 'контроль\n50×50 мм', 7)
        self.text(x, y + 53, 'Проверь линейкой после печати', 6, color=GREY)

def piece(pg, stitch, ox, oy, name, qty, mat, sa=SA, holes=True, notches=(), label_xy=(0, 0), grain=None):
    cut = offset(stitch, sa) if sa > 0 else stitch
    pg.poly(cut, ox, oy, 0.4, INK, layer='CUT')
    if sa > 0: pg.poly(stitch, ox, oy, 0.25, RED, dash=1.5, layer='STITCH')
    if holes and sa > 0:
        closed = stitch + [stitch[0]]
        for x, y in resample(closed, PITCH)[:-1]: pg.hole(ox + x, oy - y)
    for (x, y, nx, ny) in notches:   # notch: short line inward from cut line
        ln = math.hypot(nx, ny); nx, ny = nx / ln, ny / ln
        a = (ox + x + nx * sa, oy - (y + ny * sa)); b = (ox + x + nx * (sa - 2.5), oy - (y + ny * (sa - 2.5)))
        pg.line(a, b, 0.35, INK, layer='NOTCH')
    if grain:
        (gx1, gy1), (gx2, gy2) = grain
        pg.line((ox + gx1, oy - gy1), (ox + gx2, oy - gy2), 0.2, GREY)
        for e in ((gx1, gy1, 1), (gx2, gy2, -1)):
            pg.line((ox + e[0], oy - e[1]), (ox + e[0] - 1.2, oy - e[1] - 2.2 * e[2]), 0.2, GREY)
            pg.line((ox + e[0], oy - e[1]), (ox + e[0] + 1.2, oy - e[1] - 2.2 * e[2]), 0.2, GREY)
    lx, ly = label_xy
    pg.text(ox + lx, oy - ly, name, 9, True, anchor='mm', layer='TEXT')
    pg.text(ox + lx, oy - ly + 4.5, f'{qty}', 7.5, anchor='mm')
    pg.text(ox + lx, oy - ly + 8.5, mat, 6, anchor='mm', color=GREY)

# ===================== SHEET 1: cutting patterns 1:1 =====================
p1 = Page(); p1.frame(1, 'Лекала раскроя 1:1')
p1.text(14, 14, 'ЛЕКАЛА 1:1. Сплошная = линия реза. Красный пунктир = строчка. Точки = пробой шаг 3 мм. Засечки = метки совмещения.', 6.5)
p1.text(14, 18, f'Припуск на шов {SA:.0f} мм включён. Изделие шьётся наизнанку и выворачивается. Мех. тяга кожи по стрелке.', 6.5)
# gore K
gs = gore_stitch()
notK = []
for c in range(10, int(L), 10):
    s_target = c; i = min(range(len(ARC)), key=lambda j: abs(ARC[j] - s_target)); x = half_w(PROF[i][1])
    notK += [(x, ARC[i], 1, 0), (-x, ARC[i], -1, 0)]
iE = min(range(len(ARC)), key=lambda j: abs(ARC[j] - EAR_S)); xE = half_w(PROF[iE][1])
for dd in (-5, 5):
    j = min(range(len(ARC)), key=lambda k: abs(ARC[k] - (EAR_S + dd))); xx = half_w(PROF[j][1])
    notK += [(xx, ARC[j], 1, 0), (-xx, ARC[j], -1, 0)]
KX, KY = 45, 30 + L + 2 * SA
piece(p1, gs, KX, KY, 'K  Клин', '×4 (K1 перёд, K2 K4 бока, K3 спина)', 'кожа 0.8–1.0 мм', notches=notK,
      label_xy=(0, L * 0.58), grain=((0, 12), (0, L * 0.22)))
p1.dim_h(KX - half_w(RMAX), KX + half_w(RMAX), KY - ARC[[r for z, r in PROF].index(RMAX)] , f'{2*half_w(RMAX):.1f}')
p1.dim_v(KX + half_w(RMAX) + SA + 22, KY - L, KY, f'{L:.1f} по оси')
p1.dim_h(KX - half_w(RB), KX + half_w(RB), KY + SA + 5, f'{2*half_w(RB):.1f} низ')
p1.text(KX + 9, KY - L + 1, '▲ макушка', 6.5, color=GREY)
p1.text(KX + 16, KY - (EAR_S) - 2, '◄ ухо E\n(двойные\nзасечки)', 6, color=GREY)
p1.text(14, KY + SA + 12, f'Пробой по каждой стороне клина: {HOLES_PER_SIDE} отв., на всех 4 клиньях одинаково', 6.5)
# bottom disc D
DX, DY = 135, 62
dn = [(RB * math.cos(a), RB * math.sin(a), math.cos(a), math.sin(a)) for a in [math.pi / 2 + math.pi / 4 + k * math.pi / 2 for k in range(N)]]
piece(p1, circle(0, 0, RB), DX, DY, 'D  Дно', '×1', 'кожа 1.5–2 мм', notches=dn, label_xy=(0, 2))
p1.dim_h(DX - RB, DX + RB, DY + RB + SA + 5, f'Ø{2*RB:.0f} по строчке, Ø{2*RB+2*SA:.0f} рез')
p1.text(DX - 20, DY - RB - SA - 4, 'засечки = швы клиньев', 6, color=GREY)
# ear E
EX, EY = 175, 62
es = ear_stitch()
cutE = es
p1.poly(es, EX, EY, 0.4, INK, layer='CUT')
p1.line((EX - 5, EY + 0), (EX - 5, EY + SA), 0.4, layer='CUT'); p1.line((EX + 5, EY), (EX + 5, EY + SA), 0.4, layer='CUT')
p1.line((EX - 5, EY + SA), (EX + 5, EY + SA), 0.4, layer='CUT')
p1.poly([(-5, 0), (5, 0)], EX, EY, 0.25, RED, dash=1.2)
p1.text(EX, EY + 9, 'E  Ухо', 9, True, anchor='mm', layer='TEXT'); p1.text(EX, EY + 13.5, '×2, зеркально', 7.5, anchor='mm')
p1.text(EX, EY + 17.5, 'кожа 1.5–2 мм, в шов', 6, anchor='mm', color=GREY)
# appliques (net size, no allowance)
p1.text(100, 100, 'Аппликации, чистый размер без припуска', 7, True)
p1.text(100, 104, 'настрочить по краю 1.5 мм ДО сборки корпуса', 6.5, color=GREY)
AY = 135
apps = [('A1 Маска', ellipse(0, 0, 16, 10), '×1', 110, AY), ('A2 Глаз', circle(0, 0, 6), '×2', 140, AY),
        ('A3 Клюв', [(-3, 2), (3, 2), (0, -5)], '×1', 160, AY), ('A4 Пузо', ellipse(0, 0, 13, 15), '×1', 112, AY + 42),
        ('A5 Крыло', ellipse(0, 0, 5, 11.5), '×2', 145, AY + 42), ('A6 Пера', [(-6, 0), (6, 0), (0, -6)], '×1 (опц.)', 172, AY + 42)]
for name, poly, q, x, y in apps:
    p1.poly(poly, x, y, 0.4, INK, layer='CUT')
    p1.text(x, y + 19 if 'Пузо' in name or 'Крыло' in name else y + 14, f'{name} {q}', 6.5, True, anchor='mm', layer='TEXT')
p1.text(100, AY + 70, 'Зрачки: холнитены Ø6 мм ×2 через A2. Кольцо Ø20 мм в петлю H.', 6.5)
# loop H
HX, HY = 185, 240
loop = [(-4, 0), (4, 0), (4, 36), (-4, 36)]
piece(p1, loop, HX, HY, 'H Петля', '×1, сложить пополам', 'кожа 1.0 мм', sa=0, label_xy=(-14, 24))
p1.line((HX - 4, HY - 18), (HX + 4, HY - 18), 0.2, GREY)
p1.check_square(25, 200)
# scale bar 100 mm
p1.line((90, 255), (190, 255), 0.3)
for k in range(11): p1.line((90 + 10 * k, 253 if k % 5 else 251.5), (90 + 10 * k, 255), 0.3)
p1.text(140, 259, '100 мм', 6.5, anchor='mm')

# ===================== SHEET 2: assembly drawing + spec =====================
p2 = Page(); p2.frame(2, 'Сборочный чертёж, спецификация, техпроцесс')
SIL = [(r, z) for z, r in PROF] + [(-r, z) for z, r in reversed(PROF)][1:-1]
def draw_owl_front(pg, ox, oy):
    for sx in (-1, 1):
        ex = sx * half_w(1) * 0  # ears at seams +-45deg -> x = r*sin45
        zE = 54; rE = next(r for z, r in PROF if z >= zE)
        bx = sx * rE * math.sin(math.pi / 4)
        pg.poly([(bx - 4 * sx, zE - 1), (bx + 6 * sx, zE + 1), (bx + 4 * sx, zE + 13)], ox, oy, 0.35)
    pg.poly(SIL, ox, oy, 0.5)
    for sx in (-1, 1): pg.poly([(sx * r * math.sin(math.pi / 4), z) for z, r in PROF], ox, oy, 0.2, GREY, dash=1.0)
    pg.poly(ellipse(0, 44, 16, 10), ox, oy, 0.25); pg.poly(ellipse(0, 20, 13, 15), ox, oy, 0.25)
    for sx in (-1, 1): pg.poly(circle(sx * 7, 45, 6), ox, oy, 0.25); pg.poly(circle(sx * 7, 45, 3), ox, oy, 0.25)
    pg.poly([(-3, 40), (3, 40), (0, 33)], ox, oy, 0.25)
FX, FY = 50, 95
p2.text(14, 16, 'ВИДЫ 1:1', 9, True)
draw_owl_front(p2, FX, FY); p2.text(FX, FY + 6, 'Вид спереди', 7, anchor='mm')
p2.dim_h(FX - RMAX, FX + RMAX, FY + 12, f'Ø{2*RMAX:.0f}'); p2.dim_v(FX + RMAX + 8, FY - HMAX, FY, f'{HMAX:.0f} (+уши 13)')
# side
SX = 120
p2.poly(SIL, SX, FY, 0.5); p2.poly([(0, z) for z, r in PROF], SX, FY, 0.2, GREY, dash=1.0)
p2.poly(ellipse(-12, 30, 5, 11.5), SX, FY, 0.25)
p2.text(SX, FY + 6, 'Вид сбоку', 7, anchor='mm')
# top
TX, TY = 172, 62
p2.poly(circle(0, 0, RMAX), TX, TY, 0.5)
for k in range(N):
    a = math.pi / 4 + k * math.pi / 2
    p2.line((TX, TY), (TX + RMAX * math.cos(a), TY - RMAX * math.sin(a)), 0.2, GREY)
for k, nm in enumerate(['K2', 'K1', 'K4', 'K3']):
    a = k * math.pi / 2
    p2.text(TX + 14 * math.cos(a), TY - 14 * math.sin(a), nm, 6.5, True, anchor='mm')
p2.text(TX, TY + RMAX + 4, 'Вид сверху, K1 = перёд ↓', 6.5, anchor='mm')
# spec table
ty = 112
p2.text(14, ty, 'СПЕЦИФИКАЦИЯ', 9, True)
rows = [('Поз.', 'Деталь', 'Кол.', 'Материал', 'Размер, мм'),
        ('K', 'Клин корпуса', '4', 'кожа мягкая (наппа) 0.8–1.0', f'{2*half_w(RMAX):.1f}×{L:.1f} + припуск 4'),
        ('D', 'Дно', '1', 'кожа 1.5–2.0', f'Ø{2*RB:.0f} + припуск 4'),
        ('E', 'Ухо', '2 (зерк.)', 'кожа 1.5–2.0', '10×15 + хвост 4 в шов'),
        ('A1', 'Маска', '1', 'кожа 0.8, контраст', '32×20'),
        ('A2', 'Глаз', '2', 'кожа 0.8, светлая', 'Ø12'),
        ('A3', 'Клюв', '1', 'кожа 1.0', '6×7'),
        ('A4', 'Пузо', '1', 'кожа 0.8, светлая', '26×30'),
        ('A5', 'Крыло', '2', 'кожа 0.8–1.0', '10×23'),
        ('H', 'Петля', '1', 'кожа 1.0', '8×36, сгиб'),
        ('—', 'Холнитен (зрачок)', '2', 'металл, тёмный', 'Ø6'),
        ('—', 'Кольцо брелока', '1', 'сталь', 'Ø20'),
        ('—', 'Нить', '~2.5 м', 'вощёная 0.45–0.55', ''),
        ('—', 'Набивка', '~6 г', 'синтепух / холлофайбер', '')]
cx = [14, 26, 62, 82, 132]
for i, r in enumerate(rows):
    y = ty + 6 + i * 5.2
    for c, s in zip(cx, r): p2.text(c, y, s, 6.5, b=(i == 0))
    p2.line((14, y + 4.3), (196, y + 4.3), 0.12, GREY)
# process
py = ty + 6 + len(rows) * 5.2 + 6
p2.text(14, py, 'ТЕХПРОЦЕСС', 9, True)
steps = [
    '1. Раскрой по листу 1. Клинья K вдоль хребта (тяга по стрелке), все 4 из одного участка шкуры, чтоб тянулись одинаково.',
    '2. Пробой строчки шаг 3 мм по точкам (пробойник 2–3 зуба). Количество отверстий на сторонах клиньев одинаковое.',
    '3. На K1 (перёд) настрочить A4 пузо, A1 маску, A2 глаза, A3 клюв, поставить холнитены. На K2 и K4 настрочить крылья A5.',
    '4. Сшить K1+K2 и K1+K4 лицом к лицу, вложив уши E между двойными засечками, хвост уха 4 мм в припуск.',
    '5. Сшить K2+K3 и K3+K4. Петлю H сгибом наружу вложить в макушку, где сходятся 4 клина, прошить крестом.',
    '6. Вшить дно D, засечки дна к швам клиньев. Один шов дна (≈ четверть) оставить открытым.',
    '7. Вывернуть, расправить швы. Набить плотно, формуя шар. Зашить потайным швом. Кольцо Ø20 в петлю.',
    'Нужна жёсткая сова без выворота: тот же крой, кожа 1.2–1.5, сшивать край в край седельным швом наружу, срез торцевать.',
]
for k, s in enumerate(steps): p2.text(14, py + 6 + k * 5, s, 6.2)
p2.text(14, py + 6 + len(steps) * 5 + 3, 'Файлы: owl-v6.pdf (печать 1:1), owl-v6.dxf (лазер/нож, слои CUT, STITCH, HOLES, NOTCH, TEXT, мм), owl-v6.svg.', 6.2, color=GREY)

# ---------- outputs ----------
for pg in (p1, p2): pg.img.info['dpi'] = (DPI, DPI)
p1.img.save(os.path.join(HERE, 'owl-v6.pdf'), 'PDF', resolution=DPI, save_all=True, append_images=[p2.img])
prev = Image.new('RGB', (W * 2 + 40, H), (230, 230, 230)); prev.paste(p1.img, (0, 0)); prev.paste(p2.img, (W + 40, 0))
prev = prev.resize((prev.width * 2 // 5, prev.height * 2 // 5), Image.LANCZOS)
prev.save(os.path.join(HERE, 'layout-v6.png'))
p1.img.resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(HERE, 'layout-v6-sheet1.png'))
p2.img.resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(HERE, 'layout-v6-sheet2.png'))

def dxf_write(path, ents):
    o = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', '4', '0', 'ENDSEC', '0', 'SECTION', '2', 'ENTITIES']
    for layer, kind, data in ents:
        if kind in ('poly', 'line'):
            pts = data + ([data[0]] if kind == 'poly' else [])
            for a, b in zip(pts, pts[1:]):
                o += ['0', 'LINE', '8', layer, '10', f'{a[0]:.3f}', '20', f'{297-a[1]:.3f}', '11', f'{b[0]:.3f}', '21', f'{297-b[1]:.3f}']
        elif kind == 'circle':
            x, y, r = data; o += ['0', 'CIRCLE', '8', layer, '10', f'{x:.3f}', '20', f'{297-y:.3f}', '40', f'{r:.3f}']
        elif kind == 'text':
            x, y, s, h = data; o += ['0', 'TEXT', '8', layer, '10', f'{x:.3f}', '20', f'{297-y:.3f}', '40', f'{h:.2f}', '1', s]
    o += ['0', 'ENDSEC', '0', 'EOF']
    open(path, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
dxf_write(os.path.join(HERE, 'owl-v6.dxf'), p1.dxf)

col = {'CUT': '#000', 'STITCH': '#c81e1e', 'HOLES': '#000', 'NOTCH': '#000', 'TEXT': '#444'}
sv = ['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">']
for layer, kind, data in p1.dxf:
    if kind in ('poly', 'line'):
        pts = ' '.join(f'{x:.2f},{y:.2f}' for x, y in data)
        tag = 'polygon' if kind == 'poly' else 'polyline'
        dash = ' stroke-dasharray="1.5,1.5"' if layer == 'STITCH' else ''
        sv.append(f'<{tag} points="{pts}" fill="none" stroke="{col[layer]}" stroke-width="0.25"{dash} class="{layer}"/>')
    elif kind == 'circle':
        x, y, r = data; sv.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#000" class="HOLES"/>')
    elif kind == 'text':
        x, y, s, h = data; sv.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{h:.2f}" text-anchor="middle" class="TEXT">{s}</text>')
sv.append('</svg>'); open(os.path.join(HERE, 'owl-v6.svg'), 'w', encoding='utf-8').write('\n'.join(sv))
print(f'L={L:.1f} gore_w={2*half_w(RMAX):.1f} bottom_edge={2*half_w(RB):.1f} holes/side={HOLES_PER_SIDE} disc_holes={int(2*math.pi*RB/PITCH)} ear_s={EAR_S:.1f} Dmax={2*RMAX:.0f}')
