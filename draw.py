#!/usr/bin/env python3
"""The World Today - Friday 20 November 2026: 38 stories, 7 regions.
v4: STRUCTURAL rebuild, not a polish pass. Lessons from v1-v3:
- v1 = v2 = 0.980686, v3 = 0.979552 (12-0-0): the huge visual leap
  (2x supersample, gradients, 65,396 colours) did NOT move the score.
  Visual richness is not the lever; CONTENT STRUCTURE and CLARITY are.
- What the current top 5 do that v3 did not (studied 2026-11-22):
  * a TIMELINE strip ("the day in order") - the day is verifiable at a glance
  * DATA INSIDE every picture: red banner labels with the core fact and a
    source chip on every card, so each story reads from its picture alone
    even at 300px; hero pictures carry their key numbers inside them
  * FEWER words: headlines <= 7 words, one-line card bodies
  * a smaller map with a caption explaining the numbering
- So v4 adds: a "FRIDAY IN ORDER" timeline, in-picture fact banners +
  source chips on all 11 small cards, data inside all 3 hero pictures,
  shorter headlines, a smaller map + wider list. Same 38 verified stories,
  same region bar, same DATE CHECK facts as v3.
Pillow only, deterministic (no random, no clock, no network).
Renders at 2048x2048, downscales to 1024x1024 with LANCZOS.
"""
import math
from PIL import Image, ImageDraw, ImageFont

SCALE = 2
W, H = 1024, 1024
SW, SH = W * SCALE, H * SCALE

LIB = "/usr/share/fonts/truetype/liberation/"

# ---------------------------------------------------------------- helpers
def S(v):
    return int(round(v * SCALE))

def B(x0, y0, x1, y1):
    return [S(x0), S(y0), S(x1), S(y1)]

def lerp(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))

def vgrad(dr, x0, y0, x1, y1, c1, c2):
    """Vertical gradient, line by line (1x coords)."""
    h = S(y1) - S(y0)
    if h <= 0:
        return
    for i in range(h):
        t = i / max(1, h - 1)
        dr.line([(S(x0), S(y0) + i), (S(x1), S(y0) + i)], fill=lerp(c1, c2, t))

def vgrad3(dr, x0, y0, x1, y1, c1, c2, c3):
    mid = (y0 + y1) / 2.0
    vgrad(dr, x0, y0, x1, mid, c1, c2)
    vgrad(dr, x0, mid, x1, y1, c2, c3)

def rr(dr, x0, y0, x1, y1, r, **kw):
    dr.rounded_rectangle(B(x0, y0, x1, y1), radius=S(r), **kw)

def ell(dr, x0, y0, x1, y1, **kw):
    dr.ellipse(B(x0, y0, x1, y1), **kw)

def oell(x0, y0, x1, y1, fill):
    """True-alpha ellipse on the overlay layer."""
    od.ellipse(B(x0, y0, x1, y1), fill=fill)

def orect(x0, y0, x1, y1, fill):
    od.rectangle(B(x0, y0, x1, y1), fill=fill)

def line(dr, pts, fill, w=1):
    dr.line([(S(x), S(y)) for x, y in pts], fill=fill, width=S(w))

def poly(dr, pts, **kw):
    dr.polygon([(S(x), S(y)) for x, y in pts], **kw)

def arc(dr, x0, y0, x1, y1, a0, a1, fill, w=1):
    dr.arc(B(x0, y0, x1, y1), a0, a1, fill=fill, width=S(w))

def txt(dr, x, y, s, f, fill, anchor="la"):
    dr.text((S(x), S(y)), s, font=f, fill=fill, anchor=anchor)

def tw(dr, s, f):
    return dr.textlength(s, font=f) / SCALE

def F(name, size):
    return ImageFont.truetype(LIB + name, S(size))

def serif_b(sz):
    return F("LiberationSerif-Bold.ttf", sz)

def serif(sz):
    return F("LiberationSerif-Regular.ttf", sz)

def serif_i(sz):
    return F("LiberationSerif-Italic.ttf", sz)

def sans_b(sz):
    return F("LiberationSans-Bold.ttf", sz)

def sans(sz):
    return F("LiberationSans-Regular.ttf", sz)

def sans_i(sz):
    return F("LiberationSans-Italic.ttf", sz)

def grain(dr, x0, y0, x1, y1, phase=0.0, step=5, base=(255, 255, 255),
          base2=(216, 206, 182)):
    """Deterministic speckle: sine-hash placement, two tones, no random."""
    gx = x0
    while gx < x1:
        gy = y0
        while gy < y1:
            h = math.sin(gx * 12.9898 + gy * 78.233 + phase * 43.7) * 43758.5453
            frac = h - math.floor(h)
            if frac < 0.30:
                c = base if frac < 0.15 else base2
                dr.rectangle([S(gx), S(gy), S(gx) + SCALE - 1, S(gy) + SCALE - 1],
                             fill=c + (255,))
            gy += step
        gx += step

def halo_txt(dr, x, y, s, f, fill, halo=(255, 255, 255), anchor="la"):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        txt(dr, x + dx, y + dy, s, f, halo, anchor=anchor)
    txt(dr, x, y, s, f, fill, anchor=anchor)

# ---------------------------------------------------------------- palette
PAPER_TOP = (248, 241, 222)
PAPER_BOT = (240, 229, 198)
INK = (26, 26, 26)
BODY = (64, 60, 52)
GREY = (96, 90, 78)
RED = (163, 18, 18)
RED_D = (122, 10, 10)
NAVY = (16, 41, 74)
NAVY_D = (10, 28, 52)
GOLD = (200, 144, 26)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- canvas
img = Image.new("RGBA", (SW, SH), PAPER_TOP + (255,))
d = ImageDraw.Draw(img)
ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
vgrad3(d, 0, 0, W, H, PAPER_TOP, (244, 235, 210), PAPER_BOT)
grain(d, 0, 0, W, H, phase=1.7, step=5, base2=(216, 206, 182))

M = 28            # side margin
CW = W - 2 * M    # 968 content width

# ---------------------------------------------------------------- top strip
txt(d, W / 2, 12, "38 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED FRIDAY 20 NOVEMBER 2026",
    sans_b(12), RED, anchor="ma")
line(d, [(M, 28), (M + 120, 28)], (170, 150, 120), 1)
line(d, [(W - M - 120, 28), (W - M, 28)], (170, 150, 120), 1)

# kicker
txt(d, W / 2, 30, "T H E   W O R L D   T O D A Y", sans_b(15), RED, anchor="ma")

# masthead (shrink until it fits)
_msize = 84
while tw(d, "Friday 20 November 2026", serif_b(_msize)) > 960 and _msize > 70:
    _msize -= 2
txt(d, W / 2, 44, "Friday 20 November 2026", serif_b(_msize), INK, anchor="ma")
line(d, [(M, 126), (W - M, 126)], (60, 50, 40), 2)

# subhead
txt(d, W / 2, 131, "Russian missiles hit Kyiv's bridges  ·  Cyclone Akvan strikes India  ·  "
                   "An AI sell-off sinks Asia's markets",
    serif_i(16), (58, 52, 44), anchor="ma")

# ---------------------------------------------------------------- timeline: FRIDAY IN ORDER
TL_Y0, TL_Y1 = 150, 178
rr(d, M, TL_Y0, W - M, TL_Y1, 2, outline=(198, 186, 164), width=1)
vgrad3(d, M, TL_Y0, W - M, TL_Y1, (255, 253, 246), (248, 244, 231), (240, 233, 214))
_lab_w = 118
rr(d, M, TL_Y0, M + _lab_w, TL_Y1, 2, fill=RED + (255,))
txt(d, M + _lab_w / 2, TL_Y0 + 5, "FRIDAY", sans_b(11), WHITE, anchor="ma")
txt(d, M + _lab_w / 2, TL_Y0 + 16, "IN ORDER", sans_b(11), WHITE, anchor="ma")
_beats = [
    ("OVERNIGHT", ["Kyiv bridges hit"]),
    ("~08:00", ["Akvan landfall,", "Gopalpur"]),
    ("MORNING", ["Italy general", "strike"]),
    ("AFTERNOON", ["Taiex \u22126.2%,", "Nvidia \u221214%"]),
    ("EVENING", ["Anthropic debut", "+17%"]),
    ("NIGHT", ["COP31 ends,", "no deal"]),
]
_cell = (CW - _lab_w) / 6.0
for i, (tm, labs) in enumerate(_beats):
    cx = M + _lab_w + _cell * i
    if i:
        line(d, [(cx, TL_Y0 + 4), (cx, TL_Y1 - 4)], (205, 194, 172), 1)
    txt(d, cx + 8, TL_Y0 + 3, tm, sans_b(10), RED, anchor="la")
    _yy = TL_Y0 + 14
    for ln in labs:
        txt(d, cx + 8, _yy, ln, sans(9), INK, anchor="la")
        _yy += 9.5

# ---------------------------------------------------------------- number strip
NS_Y0, NS_Y1 = 182, 216
vgrad3(d, M, NS_Y0, W - M, NS_Y1, (255, 253, 246), (248, 244, 231), (240, 233, 214))
rr(d, M, NS_Y0, W - M, NS_Y1, 2, outline=(198, 186, 164), width=1)
stats = [
    ("3", "bridges hit in Kyiv"),
    ("300,000+", "evacuated before Akvan"),
    ("\u22126.2%", "Taiwan Taiex this week"),
    ("100,000", "youth visas a year, UK\u2013EU"),
    ("2.3%", "Japan inflation in October"),
    ("118", "Phillips runs vs India"),
]
cell_w = CW / 6.0
for i, (num, lab) in enumerate(stats):
    cx = M + cell_w * (i + 0.5)
    if i:
        line(d, [(M + cell_w * i, NS_Y0 + 6), (M + cell_w * i, NS_Y1 - 6)],
             (205, 194, 172), 1)
    txt(d, cx, 187, num, serif_b(21), RED, anchor="ma")
    txt(d, cx, 208, lab, sans(9), GREY, anchor="ma")

# ---------------------------------------------------------------- region bar
RB_Y0, RB_Y1 = 220, 238
regions = [
    ("EUROPE 8", 203.8, 10, (47, 93, 138), (30, 66, 104)),
    ("ASIA 8", 203.8, 10, (163, 51, 39), (120, 34, 26)),
    ("MIDDLE EAST 6", 152.8, 10, (185, 138, 29), (150, 108, 20)),
    ("AFRICA 4", 101.9, 10, (46, 125, 91), (30, 96, 68)),
    ("AMERICAS 9", 210.7, 10, (107, 63, 160), (80, 44, 128)),
    ("OCEANIA 2", 51.0, 9, (63, 125, 140), (44, 96, 112)),
    ("GLOBAL 1", 44.0, 8, (88, 84, 78), (64, 60, 56)),
]
_x = M
for j, (lab, wdt, fsz, c1, c2) in enumerate(regions):
    if j == len(regions) - 1:
        wdt = (W - M) - _x
    vgrad(d, _x, RB_Y0, _x + wdt, RB_Y1, c1, c2)
    txt(d, _x + wdt / 2, 224, lab, sans_b(fsz), WHITE, anchor="ma")
    _x += wdt

# ---------------------------------------------------------------- heroes
BEAMS = []  # (points, alpha) searchlight polygons, composited at the end
HERO_Y0, HERO_ART_H = 244, 100
HERO_W = (CW - 20) / 3.0
HERO_X = [M, M + HERO_W + 10, M + 2 * (HERO_W + 10)]

def hero_frame(ax, ay, aw, ah, banner, fact, src, stat):
    """Red banner + white fact chip + black source chip + dark stat strip."""
    bw = tw(d, banner, sans_b(11)) + 16
    rr(d, ax + 4, ay + 4, ax + 4 + bw, ay + 20, 2, fill=RED + (255,))
    txt(d, ax + 12, ay + 7, banner, sans_b(11), WHITE, anchor="la")
    fw = tw(d, fact, sans_b(9.5)) + 12
    rr(d, ax + 4, ay + 23, ax + 4 + fw, ay + 37, 2, fill=WHITE + (255,))
    txt(d, ax + 10, ay + 25.5, fact, sans_b(9.5), INK, anchor="la")
    sw = tw(d, src, sans(8)) + 10
    rr(d, ax + 4, ay + ah - 30, ax + 4 + sw, ay + ah - 18, 2,
       fill=(20, 20, 20, 235))
    txt(d, ax + 9, ay + ah - 28, src, sans(8), WHITE, anchor="la")
    orect(ax, ay + ah - 15, ax + aw, ay + ah, (10, 10, 10, 200))
    # stat text goes on the OVERLAY too, otherwise the dark strip above
    # (composited last) would dim it to ~22% brightness
    txt(od, ax + aw / 2, ay + ah - 12, stat, sans_b(9), WHITE, anchor="ma")

def bez(p0, p1, p2, n=14):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts

def hero_kyiv(ax, ay, aw, ah):
    # ONE motif: three bridges over a river under a missile sky
    vgrad3(d, ax, ay, ax + aw, ay + ah, (214, 110, 44), (120, 62, 80),
           (24, 32, 66))
    grain(d, ax, ay, ax + aw, ay + ah, phase=3.1, step=5,
          base=(255, 220, 170), base2=(140, 110, 140))
    # stars
    for i in range(26):
        sx = ax + 8 + ((i * 97) % int(aw - 16))
        sy = ay + 4 + ((i * 53) % 34)
        ell(d, sx, sy, sx + 1.5, sy + 1.5, fill=(255, 240, 200, 255))
    # searchlight beams (true alpha, composited at the end)
    BEAMS.append(([(ax + 40, ay + ah), (ax + 120, ay + 8), (ax + 128, ay + 8),
                   (ax + 60, ay + ah)], 16))
    BEAMS.append(([(ax + aw - 60, ay + ah), (ax + aw - 150, ay + 12),
                   (ax + aw - 142, ay + 12), (ax + aw - 40, ay + ah)], 13))
    # dotted missile trails
    for k, (x0, y0, x1, y1) in enumerate([(ax + 30, ay + 22, ax + 130, ay + 58),
                                          (ax + 90, ay + 10, ax + 200, ay + 52),
                                          (ax + 170, ay + 26, ax + 260, ay + 62)]):
        pts = bez((x0, y0), ((x0 + x1) / 2, min(y0, y1) - 14), (x1, y1), n=16)
        for px, py in pts[::2]:
            ell(d, px - 1.5, py - 1.5, px + 1.5, py + 1.5,
                fill=(255, 214, 120, 255))
    # skyline: dark buildings with lit windows
    for i, (bx, bw, bh) in enumerate([(ax + 6, 34, 34), (ax + 46, 26, 46),
                                      (ax + 78, 40, 28), (ax + 124, 30, 40),
                                      (ax + 160, 36, 30), (ax + 202, 28, 44),
                                      (ax + 236, 34, 36), (ax + 276, 30, 30)]):
        d.rectangle(B(bx, ay + ah - 34 - bh, bx + bw, ay + ah - 15),
                    fill=(14, 18, 34, 255))
        for wy in range(3):
            for wx in range(3):
                if (i * 7 + wy * 3 + wx) % 3 == 0:
                    ell(d, bx + 5 + wx * 9, ay + ah - 30 - bh + wy * 10,
                        bx + 8 + wx * 9, ay + ah - 27 - bh + wy * 10,
                        fill=(255, 210, 110, 255))
    # river
    vgrad(d, ax, ay + ah - 15, ax + aw, ay + ah, (30, 60, 110), (16, 34, 70))
    # three bridges: white arcs with orange fires
    for bx0 in (ax + 22, ax + 122, ax + 222):
        arc(d, bx0, ay + ah - 52, bx0 + 72, ay + ah - 8, 180, 360,
            (240, 240, 235, 255), 2)
        line(d, [(bx0, ay + ah - 30), (bx0 + 72, ay + ah - 30)],
             (240, 240, 235, 255), 2)
        fx, fy = bx0 + 36, ay + ah - 34
        ell(d, fx - 9, fy - 6, fx + 9, fy + 6, fill=(255, 140, 30, 255))
        ell(d, fx - 5, fy - 4, fx + 5, fy + 4, fill=(255, 210, 90, 255))
        # smoke: overlapping puffs stacked upward + a wispy tail
        ell(d, fx - 11, fy - 20, fx + 3, fy - 9, fill=(90, 90, 96, 255))
        ell(d, fx - 7, fy - 27, fx + 7, fy - 16, fill=(118, 118, 124, 255))
        ell(d, fx - 3, fy - 34, fx + 9, fy - 24, fill=(148, 148, 154, 255))
        arc(d, fx + 6, fy - 38, fx + 20, fy - 26, 270, 360,
            (150, 150, 156, 255), 1)
        ell(d, fx + 4, fy - 12, fx + 6, fy - 10, fill=(255, 170, 60, 255))

def hero_akvan(ax, ay, aw, ah):
    # ONE motif: one big spiral over a coast
    vgrad3(d, ax, ay, ax + aw, ay + ah, (190, 220, 235), (150, 195, 215),
           (60, 140, 150))
    grain(d, ax, ay, ax + aw, ay + ah, phase=7.7, step=5,
          base=(255, 255, 255), base2=(120, 170, 190))
    # clouds
    for cx, cy, cw in [(ax + 30, ay + 10, 44), (ax + 200, ay + 6, 52),
                       (ax + 120, ay + 16, 36)]:
        ell(d, cx, cy, cx + cw, cy + 12, fill=(255, 255, 255, 235))
        ell(d, cx + 10, cy - 5, cx + cw - 8, cy + 8, fill=(255, 255, 255, 235))
    # sea
    vgrad(d, ax, ay + 62, ax + aw, ay + ah, (40, 130, 140), (20, 90, 110))
    for wy in range(3):
        yy = ay + 68 + wy * 9
        for wx in range(6):
            x0 = ax + 10 + wx * 52 + (wy * 17) % 26
            line(d, [(x0, yy), (x0 + 26, yy)], (220, 245, 245, 255), 1)
    # sandy coast (left)
    poly(d, [(ax, ay + 62), (ax + 66, ay + 62), (ax + 52, ay + ah),
             (ax, ay + ah)], fill=(232, 205, 150, 255))
    # two palms
    for px, py in [(ax + 26, ay + 58), (ax + 48, ay + 64)]:
        line(d, [(px, py), (px + 4, py - 16)], (120, 84, 50, 255), 2)
        for a in (-50, -20, 10, 40):
            ex = px + 4 + 12 * math.cos(math.radians(a - 90))
            ey = py - 16 + 6 * math.sin(math.radians(a - 90))
            line(d, [(px + 4, py - 16), (ex, ey)], (40, 120, 70, 255), 2)
    # (no bus: it sat half-hidden behind the source chip + stat strip)
    # THE spiral: concentric arcs, one dominant motif
    cx, cy = ax + aw - 92, ay + 46
    for r in (34, 26, 18, 10):
        arc(d, cx - r, cy - r, cx + r, cy + r, 20, 330,
            (255, 255, 255, 255), 2)
    ell(d, cx - 5, cy - 5, cx + 5, cy + 5, fill=(200, 30, 30, 255))
    ell(d, cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5, fill=(255, 255, 255, 255))
    # Gopalpur dot + label
    ell(d, ax + 78, ay + 56, ax + 84, ay + 62, fill=(200, 30, 30, 255))
    txt(d, ax + 88, ay + 54, "Gopalpur", sans_b(9), INK, anchor="la")
    # rain streaks (right side)
    for i in range(10):
        rx = ax + aw - 60 + (i * 13) % 56
        ry = ay + 8 + (i * 29) % 40
        line(d, [(rx, ry), (rx - 3, ry + 9)], (200, 225, 235, 255), 1)

def hero_ai(ax, ay, aw, ah):
    # ONE motif: one big falling chart + a mini table of the four closes
    vgrad3(d, ax, ay, ax + aw, ay + ah, (18, 30, 58), (14, 24, 48),
           (10, 18, 38))
    grain(d, ax, ay, ax + aw, ay + ah, phase=11.2, step=5,
          base=(90, 110, 150), base2=(40, 55, 85))
    # faint grid
    for gx in range(int(ax + 24), int(ax + aw), 26):
        line(d, [(gx, ay + 6), (gx, ay + ah - 18)], (255, 255, 255, 26), 1)
    for gy in range(int(ay + 14), int(ay + ah - 18), 16):
        line(d, [(ax + 6, gy), (ax + aw - 6, gy)], (255, 255, 255, 26), 1)
    # volume bars along the bottom
    for i, vh in enumerate([7, 10, 6, 12, 9, 14, 8, 11]):
        vx = ax + 14 + i * 13
        d.rectangle(B(vx, ay + ah - 18 - vh, vx + 8, ay + ah - 18),
                    fill=(200, 60, 60, 255))
    # the falling line: one bold red line with dots
    pts = [(ax + 16, ay + 16), (ax + 62, ay + 26), (ax + 108, ay + 30),
           (ax + 154, ay + 44), (ax + 200, ay + 52), (ax + 246, ay + 62),
           (ax + 288, ay + 70)]
    line(d, pts, (230, 60, 60, 255), 3)
    for px, py in pts:
        ell(d, px - 3.5, py - 3.5, px + 3.5, py + 3.5,
            fill=(255, 255, 255, 255))
        ell(d, px - 1.5, py - 1.5, px + 1.5, py + 1.5,
            fill=(230, 60, 60, 255))
    # down arrow near the last dot
    poly(d, [(ax + 292, ay + 74), (ax + 300, ay + 74), (ax + 296, ay + 82)],
         fill=(230, 60, 60, 255))
    # mini table: the four Friday closes, inside the picture
    _rows = [("Taipei", "\u22126.2%"), ("Seoul", "\u22125.2%"),
             ("Tokyo", "\u22125.1%"), ("Hong Kong", "\u22121.9%")]
    _tx = ax + aw - 108
    rr(d, _tx - 6, ay + 4, ax + aw - 4, ay + 52, 2, fill=(8, 14, 30, 220))
    _ty = ay + 7
    for nm, val in _rows:
        txt(d, _tx, _ty, nm, sans(9), (220, 225, 235), anchor="la")
        txt(d, ax + aw - 10, _ty, val, sans_b(9), (255, 120, 120), anchor="ra")
        _ty += 11

def hero_text(x, loc, head_lines, body_lines, source):
    txt(d, x, 350, loc, sans_b(9.5), RED_D, anchor="la")
    y = 362
    for ln in head_lines:
        txt(d, x, y, ln, sans_b(15), INK, anchor="la")
        y += 16
    y = 396
    for ln in body_lines:
        txt(d, x, y, ln, sans(10), BODY, anchor="la")
        y += 11
    txt(d, x, 422, source, sans_i(8.5), GREY, anchor="la")

hero_kyiv(HERO_X[0], HERO_Y0, HERO_W, HERO_ART_H)
hero_frame(HERO_X[0], HERO_Y0, HERO_W, HERO_ART_H, "KYIV", "3 BRIDGES HIT",
           "Officials' count", "9 killed  \u00b7  3 bridges hit  \u00b7  power cut")
hero_akvan(HERO_X[1], HERO_Y0, HERO_W, HERO_ART_H)
hero_frame(HERO_X[1], HERO_Y0, HERO_W, HERO_ART_H, "CYCLONE AKVAN",
           "Landfall  \u00b7  8 am", "Weather office",
           "300,000+ evacuated  \u00b7  209mm rain")
hero_ai(HERO_X[2], HERO_Y0, HERO_W, HERO_ART_H)
hero_frame(HERO_X[2], HERO_Y0, HERO_W, HERO_ART_H, "AI SELL-OFF",
           "Asia, Friday's close", "Closing prices",
           "Taiex \u22126.2%  \u00b7  Kospi \u22125.2%  \u00b7  Nvidia \u221214%")

hero_text(HERO_X[0], "KYIV, UKRAINE \u00b7 WAR",
          ["Russian missiles hit three Kyiv", "bridges overnight"],
          ["~110 missiles and 400 drones; 9 killed", "across Ukraine, 3 in Kyiv; power and water cut."],
          "Kyiv Independent, BBC")
hero_text(HERO_X[1], "ODISHA, INDIA \u00b7 CYCLONE",
          ["Cyclone Akvan slams Odisha", "coast at dawn"],
          ["Landfall near Gopalpur ~8am; 300,000+ evacuated;",
           "209mm rain in Ganjam; gusts 90 km/h; no deaths."],
          "IMD, Deccan Herald")
hero_text(HERO_X[2], "ASIAN MARKETS \u00b7 STOCKS",
          ["AI sell-off sinks Asia's markets"],
          ["Taiwan \u22126.2%, worst week since 1991; Seoul \u22125.2%,",
           "Tokyo \u22125.1%; Hong Kong \u22121.9%; Nvidia \u221214%."],
          "Al Jazeera, Anadolu")

# ---------------------------------------------------------------- small cards
CARD_H = 120
BAND_H = 52

def card(x, y0, w, num, loc, banner, src, head_lines, body, scene):
    vgrad3(d, x, y0, x + w, y0 + CARD_H, (255, 253, 246), (250, 246, 234),
           (244, 238, 222))
    rr(d, x, y0, x + w, y0 + CARD_H, 3, outline=(205, 192, 168), width=1)
    scene(x + 1, y0 + 1, w - 2, BAND_H)
    # red banner strip with the core fact, inside the picture (bottom)
    rr(d, x + 1, y0 + BAND_H - 15, x + w - 1, y0 + BAND_H + 1, 2,
       fill=RED + (255,))
    txt(d, x + 6, y0 + BAND_H - 12.5, banner, sans_b(11), WHITE, anchor="la")
    # number badge, top-left
    ell(d, x + 3, y0 + 3, x + 25, y0 + 25, fill=WHITE + (255,),
        outline=(40, 40, 40, 255), width=S(1))
    txt(d, x + 14, y0 + 8.5, str(num), sans_b(11), INK, anchor="ma")
    # source chip, top-right
    cw2 = tw(d, src, sans_b(8)) + 10
    rr(d, x + w - 5 - cw2, y0 + 4, x + w - 5, y0 + 18, 2,
       fill=(30, 30, 30, 230))
    txt(d, x + w - 5 - cw2 / 2, y0 + 7, src, sans_b(8), WHITE, anchor="ma")
    txt(d, x + 6, y0 + 57, loc, sans_b(9.5), RED_D, anchor="la")
    yy = y0 + 68
    for ln in head_lines:
        txt(d, x + 6, yy, ln, sans_b(12.5), INK, anchor="la")
        yy += 13
    txt(d, x + 6, y0 + 96, body, sans(9.5), BODY, anchor="la")

def sc_brussels(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (120, 160, 210), (90, 130, 190),
           (60, 100, 160))
    grain(d, bx, by, bx + bw, by + bh, phase=2.2, step=5,
          base=(200, 220, 245), base2=(80, 110, 150))
    # EU flag (left) + UK flag (right)
    rr(d, bx + 8, by + 6, bx + 52, by + 30, 2, fill=(30, 60, 150, 255))
    for i in range(8):
        a = 2 * math.pi * i / 8
        ell(d, bx + 28 + 12 * math.cos(a) - 1.5, by + 18 + 8 * math.sin(a) - 1.5,
            bx + 28 + 12 * math.cos(a) + 1.5, by + 18 + 8 * math.sin(a) + 1.5,
            fill=(255, 215, 60, 255))
    rr(d, bx + bw - 52, by + 6, bx + bw - 8, by + 30, 2, fill=(30, 60, 150, 255))
    line(d, [(bx + bw - 52, by + 6), (bx + bw - 8, by + 30)], WHITE, 2)
    line(d, [(bx + bw - 8, by + 6), (bx + bw - 52, by + 30)], WHITE, 2)
    line(d, [(bx + bw - 30, by + 6), (bx + bw - 30, by + 30)], WHITE, 3)
    line(d, [(bx + bw - 52, by + 18), (bx + bw - 8, by + 18)], WHITE, 3)
    # clasped hands in the middle: two distinct hands, one from each side
    ell(d, bx + bw / 2 - 20, by + 10, bx + bw / 2 + 2, by + 30,
        fill=(240, 200, 160, 255))
    ell(d, bx + bw / 2 - 2, by + 10, bx + bw / 2 + 20, by + 30,
        fill=(225, 180, 140, 255))
    line(d, [(bx + bw / 2 - 2, by + 10), (bx + bw / 2 - 2, by + 30)],
         (170, 120, 85, 255), 2)
    for i in range(3):
        line(d, [(bx + bw / 2 - 14 + i * 6, by + 13),
                 (bx + bw / 2 - 14 + i * 6, by + 27)], (180, 130, 95, 255), 1)
        line(d, [(bx + bw / 2 + 4 + i * 6, by + 13),
                 (bx + bw / 2 + 4 + i * 6, by + 27)], (165, 115, 80, 255), 1)
    ell(d, bx + bw / 2 - 6, by + 4, bx + bw / 2 + 6, by + 12,
        fill=(255, 215, 60, 255))
    # parliament silhouette at the bottom edge
    d.rectangle(B(bx + 60, by + bh - 12, bx + bw - 60, by + bh),
                fill=(16, 41, 74, 255))
    for wx in range(5):
        ell(d, bx + 66 + wx * 9, by + bh - 9, bx + 69 + wx * 9, by + bh - 6,
            fill=(255, 215, 60, 255))

def sc_poland(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (190, 220, 235), (160, 200, 190),
           (110, 170, 90))
    grain(d, bx, by, bx + bw, by + bh, phase=4.4, step=5,
          base=(230, 245, 235), base2=(90, 140, 80))
    # tree line at the back
    for i in range(7):
        tx = bx + 8 + i * (bw - 16) / 6
        poly(d, [(tx - 7, by + 22), (tx, by + 8), (tx + 7, by + 22)],
             fill=(40, 110, 60, 255))
    # green field
    d.rectangle(B(bx, by + 22, bx + bw, by + bh), fill=(120, 175, 95, 255))
    # fence posts
    for i in range(6):
        fx = bx + 10 + i * (bw - 20) / 5
        d.rectangle(B(fx, by + 30, fx + 2, by + 40), fill=(120, 90, 60, 255))
    line(d, [(bx, by + 33), (bx + bw, by + 33)], (120, 90, 60, 255), 1)
    # the missile, lying in the field
    poly(d, [(bx + bw / 2 - 46, by + 42), (bx + bw / 2 - 20, by + 36),
             (bx + bw / 2 + 30, by + 36), (bx + bw / 2 + 44, by + 42)],
         fill=(220, 225, 230, 255))
    poly(d, [(bx + bw / 2 + 30, by + 36), (bx + bw / 2 + 44, by + 42),
             (bx + bw / 2 + 30, by + 44)], fill=(180, 40, 40, 255))
    line(d, [(bx + bw / 2 - 20, by + 36), (bx + bw / 2 - 20, by + 28)],
         (200, 60, 60, 255), 2)

def sc_cop31(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (170, 210, 235), (140, 190, 220),
           (110, 170, 200))
    grain(d, bx, by, bx + bw, by + bh, phase=6.6, step=5,
          base=(220, 240, 250), base2=(90, 140, 170))
    # globe
    ell(d, bx + 10, by + 6, bx + 46, by + 42, fill=(70, 140, 200, 255))
    ell(d, bx + 16, by + 12, bx + 30, by + 24, fill=(90, 170, 110, 255))
    ell(d, bx + 28, by + 26, bx + 40, by + 36, fill=(90, 170, 110, 255))
    arc(d, bx + 10, by + 6, bx + 46, by + 42, 200, 340, (255, 255, 255, 255), 1)
    # thermometer
    rr(d, bx + bw - 34, by + 8, bx + bw - 26, by + 34, 3,
       fill=(255, 255, 255, 255))
    d.rectangle(B(bx + bw - 32, by + 12, bx + bw - 28, by + 30),
                fill=(220, 60, 60, 255))
    ell(d, bx + bw - 36, by + 30, bx + bw - 24, by + 42,
        fill=(220, 60, 60, 255))
    # flags
    for i, col in enumerate([(220, 60, 60), (255, 215, 60), (60, 140, 90)]):
        fx = bx + 58 + i * 26
        line(d, [(fx, by + 10), (fx, by + 34)], (80, 70, 60, 255), 1)
        poly(d, [(fx, by + 10), (fx + 18, by + 14), (fx, by + 18)],
             fill=col + (255,))
    # sea waves at the bottom
    for wx in range(5):
        x0 = bx + 6 + wx * (bw - 12) / 5
        arc(d, x0, by + bh - 12, x0 + 16, by + bh - 2, 180, 360,
            (255, 255, 255, 255), 1)

def sc_space(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (16, 24, 48), (12, 18, 38),
           (8, 12, 28))
    grain(d, bx, by, bx + bw, by + bh, phase=8.8, step=5,
          base=(120, 140, 180), base2=(40, 50, 80))
    for i in range(12):
        sx = bx + 6 + ((i * 53) % int(bw - 12))
        sy = by + 4 + ((i * 29) % int(bh - 12))
        ell(d, sx, sy, sx + 1.5, sy + 1.5, fill=(255, 255, 255, 255))
    # cratered moon (left)
    ell(d, bx + 8, by + 8, bx + 44, by + 44, fill=(190, 190, 195, 255))
    for cx, cy, cr in [(bx + 18, by + 18, 4), (bx + 30, by + 28, 5),
                       (bx + 22, by + 34, 3)]:
        ell(d, cx - cr, cy - cr, cx + cr, cy + cr, fill=(150, 150, 155, 255))
    # spacecraft with gold panels (right)
    d.rectangle(B(bx + bw - 62, by + 16, bx + bw - 46, by + 30),
                fill=(210, 215, 220, 255))
    d.rectangle(B(bx + bw - 84, by + 19, bx + bw - 62, by + 27),
                fill=(200, 160, 40, 255))
    d.rectangle(B(bx + bw - 46, by + 19, bx + bw - 24, by + 27),
                fill=(200, 160, 40, 255))
    ell(d, bx + bw - 58, by + 8, bx + bw - 50, by + 16,
        fill=(140, 180, 220, 255))
    # ringed planet, far right
    ell(d, bx + bw - 18, by + 34, bx + bw - 8, by + 44, fill=(200, 170, 120, 255))
    arc(d, bx + bw - 22, by + 36, bx + bw - 4, by + 42, 180, 360,
        (220, 200, 160, 255), 1)

def sc_italy(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (235, 225, 205), (220, 205, 180),
           (200, 185, 160))
    grain(d, bx, by, bx + bw, by + bh, phase=10.1, step=5,
          base=(255, 250, 240), base2=(170, 150, 120))
    # buildings behind
    for i, (wx0, ww, wh) in enumerate([(8, 30, 22), (44, 24, 30), (74, 34, 18),
                                       (114, 26, 26)]):
        d.rectangle(B(bx + wx0, by + bh - 14 - wh, bx + wx0 + ww, by + bh - 14),
                    fill=(120, 105, 85, 255))
        for wy in range(2):
            ell(d, bx + wx0 + 6, by + bh - 12 - wh + wy * 8,
                bx + wx0 + 10, by + bh - 8 - wh + wy * 8,
                fill=(255, 220, 130, 255))
    # protesters with placards
    for i, px in enumerate([bx + 22, bx + 62, bx + 102, bx + 140]):
        ell(d, px - 5, by + 22, px + 5, by + 32, fill=(40, 40, 40, 255))
        poly(d, [(px - 8, by + 46), (px - 6, by + 32), (px + 6, by + 32),
                 (px + 8, by + 46)], fill=(60, 60, 60, 255))
        if i % 2 == 0:
            d.rectangle(B(px + 8, by + 14, px + 26, by + 26),
                        fill=(255, 255, 255, 255))
            line(d, [(px + 17, by + 26), (px + 17, by + 32)], (80, 70, 60, 255), 1)

def sc_kenya(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (250, 215, 140), (240, 190, 110),
           (225, 160, 80))
    grain(d, bx, by, bx + bw, by + bh, phase=12.3, step=5,
          base=(255, 235, 190), base2=(200, 150, 80))
    # sun
    ell(d, bx + bw - 40, by + 6, bx + bw - 16, by + 30,
        fill=(255, 220, 90, 255))
    # hills
    poly(d, [(bx, by + 34), (bx + bw / 2, by + 24), (bx + bw, by + 34),
             (bx + bw, by + bh), (bx, by + bh)], fill=(200, 160, 90, 255))
    # oil derrick
    dx = bx + 22
    poly(d, [(dx - 12, by + bh - 14), (dx - 4, by + 10), (dx + 4, by + 10),
             (dx + 12, by + bh - 14)], fill=(40, 40, 40, 255))
    line(d, [(dx - 8, by + 26), (dx + 8, by + 26)], (40, 40, 40, 255), 2)
    line(d, [(dx, by + 10), (dx + 16, by + 18)], (40, 40, 40, 255), 2)
    ell(d, dx + 14, by + 16, dx + 20, by + 22, fill=(255, 140, 40, 255))
    # acacia tree
    line(d, [(bx + bw - 52, by + 34), (bx + bw - 52, by + 22)],
         (90, 60, 30, 255), 2)
    ell(d, bx + bw - 66, by + 18, bx + bw - 38, by + 26,
        fill=(80, 130, 60, 255))
    # birds
    for i in range(2):
        cx = bx + 70 + i * 22
        arc(d, cx - 5, by + 12, cx, by + 17, 180, 360, (60, 50, 40, 255), 1)
        arc(d, cx, by + 12, cx + 5, by + 17, 180, 360, (60, 50, 40, 255), 1)
    # grass tufts
    for i in range(5):
        gx = bx + 8 + i * (bw - 16) / 4
        line(d, [(gx, by + bh - 14), (gx - 2, by + bh - 20)],
             (60, 110, 50, 255), 1)
        line(d, [(gx, by + bh - 14), (gx + 2, by + bh - 20)],
             (60, 110, 50, 255), 1)

def sc_salvador(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (190, 215, 235), (160, 195, 220),
           (130, 175, 205))
    grain(d, bx, by, bx + bw, by + bh, phase=14.5, step=5,
          base=(225, 240, 250), base2=(100, 140, 170))
    # falling ballot papers + confetti
    for i, (px, py) in enumerate([(bx + 16, by + 8), (bx + 40, by + 4),
                                  (bx + bw - 46, by + 6), (bx + bw - 20, by + 12)]):
        d.rectangle(B(px, py, px + 10, py + 7), fill=(255, 255, 255, 255))
        line(d, [(px + 2, py + 3), (px + 8, py + 3)], (60, 90, 130, 255), 1)
    for i in range(6):
        cx = bx + 10 + (i * 37) % int(bw - 20)
        cy = by + 16 + (i * 17) % 12
        ell(d, cx, cy, cx + 2, cy + 2,
            fill=((220, 60, 60), (60, 140, 90), (255, 200, 60))[i % 3] + (255,))
    # ballot box
    rr(d, bx + bw / 2 - 30, by + 20, bx + bw / 2 + 30, by + bh - 14, 2,
       fill=(40, 80, 160, 255))
    d.rectangle(B(bx + bw / 2 - 34, by + 16, bx + bw / 2 + 34, by + 22),
                fill=(30, 60, 130, 255))
    d.rectangle(B(bx + bw / 2 - 8, by + 18, bx + bw / 2 + 8, by + 20),
                fill=(20, 20, 20, 255))
    # green tick
    line(d, [(bx + bw / 2 - 14, by + 30), (bx + bw / 2 - 4, by + 38),
             (bx + bw / 2 + 16, by + 24)], (90, 220, 120, 255), 3)
    # small flag on the box
    line(d, [(bx + bw / 2 + 22, by + 16), (bx + bw / 2 + 22, by + 6)],
         (80, 70, 60, 255), 1)
    poly(d, [(bx + bw / 2 + 22, by + 6), (bx + bw / 2 + 34, by + 9),
             (bx + bw / 2 + 22, by + 12)], fill=(60, 140, 90, 255))

def sc_cricket(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (150, 200, 130), (120, 180, 100),
           (90, 150, 80))
    grain(d, bx, by, bx + bw, by + bh, phase=16.7, step=5,
          base=(200, 230, 180), base2=(70, 120, 60))
    # crowd dots in the background
    for i in range(10):
        cx = bx + 8 + (i * 41) % int(bw - 16)
        cy = by + 6 + (i * 13) % 8
        ell(d, cx, cy, cx + 3, cy + 3,
            fill=((220, 220, 220), (255, 200, 60), (200, 80, 80))[i % 3] + (255,))
    # pitch
    d.rectangle(B(bx + 20, by + 16, bx + bw - 20, by + bh - 14),
                fill=(220, 195, 140, 255))
    # stumps
    for sx in (bx + bw - 44, bx + bw - 38, bx + bw - 32):
        d.rectangle(B(sx, by + 24, sx + 2, by + 38), fill=(240, 210, 130, 255))
    # cricket bat: darker wood with a pale edge so it reads off the pitch
    poly(d, [(bx + 18, by + 20), (bx + 30, by + 16), (bx + 44, by + 34),
             (bx + 32, by + 40)], fill=(180, 140, 80, 255))
    line(d, [(bx + 20, by + 21), (bx + 31, by + 17)], (245, 225, 180, 255), 1)
    line(d, [(bx + 30, by + 16), (bx + 38, by + 8)], (150, 110, 70, 255), 2)
    # red ball + second ball
    ell(d, bx + 52, by + 30, bx + 62, by + 40, fill=(200, 40, 40, 255))
    ell(d, bx + 70, by + 38, bx + 76, by + 44, fill=(200, 40, 40, 255))
    # boundary rope
    for i in range(8):
        rx = bx + 6 + i * (bw - 12) / 7
        ell(d, rx, by + bh - 12, rx + 3, by + bh - 9,
            fill=(255, 255, 255, 255))

def sc_health(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (240, 235, 225), (225, 215, 200),
           (210, 200, 185))
    grain(d, bx, by, bx + bw, by + bh, phase=18.9, step=5,
          base=(255, 255, 255), base2=(170, 160, 140))
    # big red-white capsule
    cx, cy = bx + bw / 2, by + 22
    ell(d, cx - 34, cy - 9, cx, cy + 9, fill=(200, 40, 40, 255))
    ell(d, cx, cy - 9, cx + 34, cy + 9, fill=(255, 255, 255, 255))
    arc(d, cx - 34, cy - 9, cx + 34, cy + 9, 90, 270, (160, 30, 30, 255), 1)
    # blister pack + small pills
    rr(d, bx + 10, by + 36, bx + 44, by + 48, 2, fill=(200, 210, 220, 255))
    for i in range(3):
        ell(d, bx + 14 + i * 10, by + 39, bx + 20 + i * 10, by + 45,
            fill=(255, 255, 255, 255))
    ell(d, bx + bw - 26, by + 36, bx + bw - 16, by + 46,
        fill=(220, 90, 90, 255))
    ell(d, bx + bw - 40, by + 40, bx + bw - 32, by + 48,
        fill=(255, 255, 255, 255))

def sc_california(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (220, 230, 240), (200, 215, 230),
           (180, 200, 220))
    grain(d, bx, by, bx + bw, by + bh, phase=21.1, step=5,
          base=(245, 248, 252), base2=(150, 170, 190))
    # circuit traces across the whole band
    for i, (x0, y0, x1, y1) in enumerate([
            (bx + 6, by + 10, bx + 30, by + 10), (bx + 30, by + 10, bx + 30, by + 26),
            (bx + 6, by + 40, bx + 44, by + 40), (bx + 44, by + 40, bx + 44, by + 28),
            (bx + bw - 50, by + 12, bx + bw - 6, by + 12),
            (bx + bw - 50, by + 12, bx + bw - 50, by + 30)]):
        line(d, [(x0, y0), (x1, y1)], (60, 140, 90, 255), 1)
        ell(d, x1 - 2, y1 - 2, x1 + 2, y1 + 2, fill=(60, 140, 90, 255))
    # green chip
    rr(d, bx + 12, by + 14, bx + 48, by + 38, 2, fill=(40, 130, 70, 255))
    d.rectangle(B(bx + 22, by + 20, bx + 38, by + 32), fill=(20, 90, 50, 255))
    for i in range(3):
        line(d, [(bx + 12, by + 18 + i * 7), (bx + 6, by + 18 + i * 7)],
             (200, 200, 200, 255), 1)
        line(d, [(bx + 48, by + 18 + i * 7), (bx + 54, by + 18 + i * 7)],
             (200, 200, 200, 255), 1)
    # magnifier
    ell(d, bx + bw - 44, by + 8, bx + bw - 14, by + 38,
        outline=(40, 40, 40, 255), width=S(2))
    ell(d, bx + bw - 40, by + 12, bx + bw - 18, by + 34,
        fill=(190, 215, 235, 255))
    line(d, [(bx + bw - 16, by + 36), (bx + bw - 6, by + 46)],
         (40, 40, 40, 255), 2)

def sc_games(bx, by, bw, bh):
    vgrad3(d, bx, by, bx + bw, by + bh, (90, 60, 140), (70, 45, 115),
           (55, 35, 95))
    grain(d, bx, by, bx + bw, by + bh, phase=23.3, step=5,
          base=(150, 120, 200), base2=(50, 35, 85))
    # gold coins + stars scattered
    for i, (cx, cy) in enumerate([(bx + 12, by + 10), (bx + bw - 16, by + 8),
                                  (bx + 18, by + 38), (bx + bw - 22, by + 40)]):
        ell(d, cx, cy, cx + 10, cy + 10, fill=(255, 205, 60, 255))
        txt(d, cx + 5, cy + 1, "$", sans_b(7), (140, 100, 20), anchor="ma")
    for i in range(5):
        sx = bx + 30 + (i * 47) % int(bw - 60)
        sy = by + 4 + (i * 19) % 10
        ell(d, sx, sy, sx + 1.5, sy + 1.5, fill=(255, 230, 130, 255))
    # game controller
    cx, cy = bx + bw / 2, by + 24
    rr(d, cx - 34, cy - 10, cx + 34, cy + 12, 8, fill=(30, 30, 34, 255))
    ell(d, cx - 38, cy + 6, cx - 26, cy + 18, fill=(30, 30, 34, 255))
    ell(d, cx + 26, cy + 6, cx + 38, cy + 18, fill=(30, 30, 34, 255))
    line(d, [(cx - 22, cy), (cx - 14, cy)], (220, 220, 220, 255), 2)
    line(d, [(cx - 18, cy - 4), (cx - 18, cy + 4)], (220, 220, 220, 255), 2)
    for j, col in enumerate([(220, 60, 60), (60, 200, 90), (80, 140, 230),
                             (255, 200, 60)]):
        ang = math.pi * (0.25 + j * 0.5)
        ex = cx + 18 + 6 * math.cos(ang)
        ey = cy - 2 + 6 * math.sin(ang)
        ell(d, ex - 2.5, ey - 2.5, ex + 2.5, ey + 2.5, fill=col + (255,))

ROW1 = [
    (4, "BRUSSELS \u00b7 DIPLOMACY", "RESET DEAL SEALED", "Reuters",
     ["UK and EU seal a 'reset' deal"], "Food trade, youth visas, carbon link.",
     sc_brussels),
    (5, "POLAND \u00b7 SECURITY", "MISSILE LANDS", "Reuters",
     ["Russian missile lands", "in Polish field"],
     "It fell in a field; two airports paused.", sc_poland),
    (6, "ANTALYA \u00b7 CLIMATE", "NO DEAL AT COP31", "UN News",
     ["COP31 ends last day", "with no deal"],
     "The draft text leaves out fossil fuels.", sc_cop31),
    (7, "SPACE \u00b7 MERCURY", "8 YEARS TO MERCURY", "ESA \u00b7 BBC",
     ["BepiColombo reaches", "Mercury after 8 years"],
     "Orbit entry set for Saturday.", sc_space),
    (8, "ROME \u00b7 LABOUR", "STRIKE OVER BUDGET", "CGIL",
     ["Italy hit by general strike"], "Workers and students march.",
     sc_italy),
]
ROW2 = [
    (9, "TURKANA \u00b7 ENERGY", "FIRST OIL DRILLED", "allAfrica",
     ["Kenya drills its first oil"], "First crude due 1 December.",
     sc_kenya),
    (10, "SAN SALVADOR \u00b7 POLITICS", "THIRD TERM FILED", "AP",
     ["Bukele files to run", "for third term"],
     "The vote is on 28 February 2027.", sc_salvador),
    (11, "CRICKET \u00b7 OCEANIA", "118 OFF PHILLIPS", "ICC",
     ["Phillips hits 118", "as NZ make 368"],
     "NZ make 368 vs India.", sc_cricket),
    (12, "HEALTH \u00b7 TRIAL", "60.7% RESPOND", "Trial data",
     ["Cancer pill shrinks", "tumours in trial"],
     "60.7% respond in trial.", sc_health),
    (13, "CALIFORNIA \u00b7 TECH", "CHIPS PROBE", "California",
     ["California probes Nvidia", "over chips"],
     "State asks if investors were misled.", sc_california),
    (14, "GAMES \u00b7 LAUNCH", "$2.36BN LAUNCH", "Sensor Tower",
     ["GTA VI sales top $2.36bn", "at launch"],
     "About 24 million copies sold.", sc_games),
]

def draw_row(y0, items):
    n = len(items)
    w = (CW - (n - 1) * 8) / n
    x = M
    for (num, loc, banner, src, hl, body, scene) in items:
        card(x, y0, w, num, loc, banner, src, hl, body, scene)
        x += w + 8

draw_row(436, ROW1)
draw_row(562, ROW2)

# ---------------------------------------------------------------- map + list (smaller map, wider list)
MAP_X, MAP_Y, MAP_W, MAP_H = M, 688, 440, 266
LIST_X = 480

def ll(lon, lat):
    return (MAP_X + (lon + 170) / 360.0 * MAP_W,
            MAP_Y + (75 - lat) / 130.0 * MAP_H)

vgrad3(d, MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H, (20, 50, 90), (16, 40, 74),
       (10, 28, 54))
for gx in range(MAP_X + 37, MAP_X + MAP_W, 37):
    line(d, [(gx, MAP_Y), (gx, MAP_Y + MAP_H)], (255, 255, 255, 22), 1)
for gy in range(MAP_Y + 44, MAP_Y + MAP_H, 44):
    line(d, [(MAP_X, gy), (MAP_X + MAP_W, gy)], (255, 255, 255, 22), 1)
grain(d, MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H, phase=13.5, step=5,
      base2=(120, 140, 170))
orect(MAP_X, MAP_Y, MAP_X + 14, MAP_Y + MAP_H, (6, 14, 30, 16))
orect(MAP_X + MAP_W - 14, MAP_Y, MAP_X + MAP_W, MAP_Y + MAP_H, (6, 14, 30, 16))
orect(MAP_X, MAP_Y, MAP_X + MAP_W, MAP_Y + 12, (6, 14, 30, 14))
orect(MAP_X, MAP_Y + MAP_H - 12, MAP_X + MAP_W, MAP_Y + MAP_H, (6, 14, 30, 12))

CONT = (201, 180, 137)
CONT_D = (168, 146, 106)

def continent(pts, fill=CONT):
    poly(d, [ll(lon, lat) for lon, lat in pts], fill=fill + (255,),
         outline=CONT_D + (255,))

# Asia
continent([(30, 70), (40, 68), (60, 69), (80, 72), (100, 76), (120, 72),
           (140, 72), (160, 70), (170, 66), (178, 65), (170, 60), (162, 55),
           (158, 50), (150, 45), (142, 40), (135, 35), (130, 32), (127, 35),
           (122, 38), (120, 32), (115, 25), (110, 20), (108, 10), (105, 8),
           (100, 8), (97, 15), (95, 20), (90, 22), (85, 20), (80, 15),
           (75, 10), (72, 20), (65, 25), (60, 25), (55, 26), (50, 28),
           (48, 30), (42, 35), (38, 36), (35, 36), (30, 36), (30, 42),
           (28, 45), (30, 50), (30, 60)])
# Africa
continent([(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31),
           (35, 28), (43, 12), (48, 11), (51, 10), (44, 0), (40, -10),
           (35, -20), (32, -28), (20, -35), (15, -30), (12, -18), (9, -2),
           (9, 4), (-8, 5), (-13, 10), (-17, 15)])
# North America
continent([(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
           (-80, 60), (-75, 45), (-70, 42), (-75, 35), (-80, 26), (-84, 30),
           (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
           (-125, 49), (-140, 60), (-155, 58), (-165, 60)])
# South America
continent([(-80, 10), (-75, 5), (-70, 10), (-60, 5), (-50, 0), (-40, -5),
           (-35, -10), (-40, -20), (-48, -28), (-55, -35), (-65, -45),
           (-70, -52), (-73, -40), (-73, -30), (-80, -20), (-80, -10),
           (-77, 0)])
# Europe
continent([(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
           (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
           (30, 70), (20, 70), (18, 66), (12, 65), (5, 60), (0, 55),
           (-5, 50), (-10, 45)])
# Australia
continent([(114, -22), (114, -30), (120, -35), (130, -32), (140, -38),
           (150, -37), (153, -27), (146, -19), (142, -11), (136, -12),
           (132, -11), (126, -14), (122, -17), (114, -22)])
# Greenland + UK + Japan
continent([(-55, 60), (-45, 60), (-40, 70), (-30, 70), (-25, 76), (-55, 76)])
continent([(-5, 50), (-3, 53), (-5, 58), (-2, 58), (0, 53), (-1, 50)])
continent([(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
           (140, 44), (142, 44), (143, 42), (141, 39), (139, 36), (136, 33),
           (132, 31)])
# Indonesia islands
for ilon, ilat in [(95, 5), (100, 0), (105, -2), (110, -5), (115, -7),
                   (120, -8), (125, -8), (130, -5), (135, -4), (140, -6)]:
    x0, y0 = ll(ilon, ilat)
    ell(d, x0 - 3, y0 - 2, x0 + 3, y0 + 2, fill=CONT + (255,))

_tw = tw(d, "WHERE IT HAPPENED", sans_b(11)) + 16
rr(d, MAP_X + 6, MAP_Y + 6, MAP_X + 6 + _tw, MAP_Y + 22, 2,
   fill=(10, 28, 52, 255))
txt(d, MAP_X + 14, MAP_Y + 8, "WHERE IT HAPPENED", sans_b(11), WHITE, anchor="la")
_pw = tw(d, "38 PINS \u2014 ONE PER STORY", sans(9)) + 14
rr(d, MAP_X + MAP_W - 8 - _pw, MAP_Y + 6, MAP_X + MAP_W - 8, MAP_Y + 22, 2,
   fill=(10, 28, 52, 255))
txt(d, MAP_X + MAP_W - 15, MAP_Y + 8, "38 PINS \u2014 ONE PER STORY", sans(9),
    (210, 220, 235), anchor="ra")

# space badge (story 7) in the ocean, bottom-left
_sb = "7 \u00b7 SPACE \u2014 Mercury"
_sbw = tw(d, _sb, sans_b(9)) + 16
rr(d, MAP_X + 10, MAP_Y + MAP_H - 26, MAP_X + 10 + _sbw, MAP_Y + MAP_H - 8, 7,
   fill=RED + (255,))
txt(d, MAP_X + 18, MAP_Y + MAP_H - 21.5, _sb, sans_b(9), WHITE, anchor="la")

# compass rose in the Indian Ocean (clear of pins)
_ccx, _ccy = MAP_X + 318, MAP_Y + MAP_H - 21
ell(d, _ccx - 10, _ccy - 10, _ccx + 10, _ccy + 10,
    outline=(255, 255, 255, 200), width=S(1))
poly(d, [(_ccx, _ccy - 8), (_ccx + 3, _ccy + 4), (_ccx - 3, _ccy + 4)],
     fill=(255, 255, 255, 230))
txt(d, _ccx, _ccy - 20, "N", sans_b(9), WHITE, anchor="ma")

# pins with greedy badge solver (deterministic)
PINS = [
    (1, 30.5, 50.4), (2, 84.9, 19.3), (3, 121.5, 25.0), (4, 4.4, 50.8),
    (5, 22.6, 51.2), (6, 30.7, 36.9), (8, 12.5, 41.9), (9, 35.6, 3.5),
    (10, -89.2, 13.7), (11, 174.8, -41.3), (12, -0.1, 51.5),
    (13, -121.9, 37.35), (14, -80.2, 25.8), (15, 139.7, 35.7),
    (16, 127.0, 37.5), (17, -122.4, 37.8), (18, -74.0, 40.7),
    (19, -77.0, 38.9), (20, -77.0, 38.9), (21, 46.7, 24.7),
    (22, 24.7, 59.4), (23, 57.0, 25.5), (24, 56.3, 26.6),
    (25, 34.5, 31.5), (26, 77.2, 28.6), (27, -58.4, -34.6),
    (28, 149.1, -35.3), (29, 92.0, 21.4), (30, 24.0, 49.8),
    (31, 35.5, 33.9), (32, 29.5, 12.5), (33, 33.8, -13.96),
    (34, -4.0, 5.3), (35, -115.1, 36.2), (36, 127.0, 37.5),
    (37, 139.7, 35.7), (38, 7.7, 45.07),
]
_OFFSETS = [(0, -17), (15, -11), (17, 0), (15, 11), (0, 17), (-15, 11),
            (-17, 0), (-15, -11), (0, -27), (26, -19), (26, 19), (-26, -19),
            (-26, 19), (0, 27), (34, 0), (-34, 0)]
_placed = []
for num, lon, lat in PINS:
    px, py = ll(lon, lat)
    bx, by = px, py - 17
    for dx, dy in _OFFSETS:
        cx, cy = px + dx, py + dy
        if not (MAP_X + 10 <= cx <= MAP_X + MAP_W - 10 and
                MAP_Y + 30 <= cy <= MAP_Y + MAP_H - 32):
            continue
        if all((cx - ox) ** 2 + (cy - oy) ** 2 >= 15 ** 2 for ox, oy in _placed):
            bx, by = cx, cy
            break
    _placed.append((bx, by))
    # red pin dot at the true location
    ell(d, px - 3, py - 3, px + 3, py + 3, fill=(200, 30, 30, 255))
    line(d, [(px, py), (bx, by)], (255, 255, 255, 220), 1)
    _r = 7.0 if num in (1, 4, 5, 6, 8, 12, 22, 30, 38) else 7.5
    _fs = 7.5 if num in (1, 4, 5, 6, 8, 12, 22, 30, 38) else 8
    ell(d, bx - _r, by - _r, bx + _r, by + _r, fill=WHITE + (255,),
        outline=(180, 30, 30, 255), width=S(1))
    txt(d, bx, by - _fs / 2 - 0.5, str(num), sans_b(_fs), INK, anchor="ma")

# ---------------------------------------------------------------- list panel
vgrad3(d, LIST_X, MAP_Y, W - M, MAP_Y + MAP_H, (255, 253, 246), (250, 246, 234),
       (244, 238, 222))
rr(d, LIST_X, MAP_Y, W - M, MAP_Y + MAP_H, 2, outline=(205, 192, 168), width=1)
txt(d, LIST_X + 8, MAP_Y + 6, "ALSO ON FRIDAY 20 NOVEMBER \u2014 24 MORE STORIES",
    sans_b(11), RED, anchor="la")
LIST = [
    (15, "Japan inflation 2.3%, core 2.2%; Dec rate rise in view. (Reuters)"),
    (16, "Seoul ruling party moves to impeach top judge. (Korea Herald)"),
    (17, "Anthropic Nasdaq debut: $83 \u2192 $97.17 (+17%); $81.3B, largest IPO ever."),
    (18, "Bitcoin near $61,700, lowest since July, third day down."),
    (19, "US Senate blocks Iran war-powers resolution 51-48."),
    (20, "Trump in no rush on Iran: \u2018see what happens after January 1\u2019."),
    (21, "Houthi missile damages Riyadh\u2019s tallest tower; no injuries."),
    (22, "Estonia to shut Russia border from 1 Dec, for at least 6 months."),
    (23, "Tanker ablaze off Oman near Hormuz, no casualties. (UKMTO)"),
    (24, "Hormuz: Brent $92.50; 46 ships waiting."),
    (25, "Gaza: Israeli strikes kill 6 despite truce."),
    (26, "Pakistan minister visits New Delhi, first since May 2025. (PTI)"),
    (27, "Argentina country risk jumps to 1,070, up 15%. (JPM)"),
    (28, "Australia: Xi hails \u2018full turnaround\u2019 in China ties."),
    (29, "Rohingya camps weep and pray after ICJ ruling. (Al Jazeera)"),
    (30, "Lviv railway station strike kills 2. (BBC)"),
    (31, "Lebanon: Israeli strikes hit south and east."),
    (32, "Sudan army claims gains in West Kordofan."),
    (33, "Malawi fuel crisis brings night-long petrol queues. (Al Jazeera)"),
    (34, "AfDB: 22 African states near debt distress. (allAfrica)"),
    (35, "Las Vegas: Russell fastest in wet Grand Prix practice. (Autosport)"),
    (36, "Seoul: 111 students caught cheating in Suneung exam."),
    (37, "Tokyo: SoftBank shares fall 14% in a day. (Al Jazeera)"),
    (38, "Turin: ATP backs plan to lift player pay past $350m. (Anadolu)"),
]
_ly = MAP_Y + 24
for num, s in LIST:
    txt(d, LIST_X + 8, _ly, str(num), sans_b(9.5), RED, anchor="la")
    txt(d, LIST_X + 8 + tw(d, str(num) + "  ", sans_b(9.5)), _ly, s, sans(9.5),
        INK, anchor="la")
    _ly += 10.1

# ---------------------------------------------------------------- date check + footer
DC_Y0, DC_Y1 = 960, 992
vgrad3(d, M, DC_Y0, W - M, DC_Y1, (253, 238, 232), (251, 233, 226), (248, 228, 220))
rr(d, M, DC_Y0, W - M, DC_Y1, 2, outline=RED, width=1)
txt(d, M + 8, DC_Y0 + 3, "DATE CHECK \u2014 WHAT WE LEFT OUT", sans_b(10), RED,
    anchor="la")
txt(d, M + 8, DC_Y0 + 14,
    "Left out as Thursday 19 November's news: World Court ruling on Myanmar \u00b7 "
    "three-leader declaration in Shenzhen \u00b7 Tonga drought emergency \u00b7 Anthropic $83 IPO pricing.",
    sans(9), BODY, anchor="la")
txt(d, M + 8, DC_Y0 + 24,
    "Not yet happened, so not shown: BepiColombo\u2019s Mercury orbit entry "
    "\u00b7 COP31 final text \u00b7 ATP Finals final.",
    sans(9), BODY, anchor="la")

txt(d, W / 2, 998,
    "Every story here happened, or was first reported, on Friday 20 November 2026. "
    "Officials\u2019 counts are attributed. Claims are attributed, not stated as fact.",
    sans(8.5), GREY, anchor="ma")
txt(d, W / 2, 1007,
    "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Kyiv Independent, IMD, Deccan Herald, "
    "ESA, UN News \u2014 original vector drawings.",
    sans(8.5), GREY, anchor="ma")

# ---------------------------------------------------------------- downscale + save
import os
if BEAMS:
    _ov = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    _od = ImageDraw.Draw(_ov)
    for _pts, _al in BEAMS:
        _od.polygon([(S(x), S(y)) for x, y in _pts],
                    fill=(255, 240, 200, _al))
    img = Image.alpha_composite(img, _ov)
img = Image.alpha_composite(img, ov)
out = img.convert("RGB").resize((W, H), Image.LANCZOS)
out.save("entry.png", optimize=True)
print("saved entry.png", out.size)
