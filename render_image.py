#!/usr/bin/env python3
"""MAKE IT NEWS — picture edition renderer.

Draws a 1024x1024 colour vintage newspaper front page for Friday
20 November 2026 with large hand-drawn Pillow illustrations: a night
scene of Kyiv's bridges under fire, a plunging stock chart, gold bars,
a cyclone spiral and a smartphone. Deterministic: all randomness is
seeded, so repeated runs produce byte-identical output.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024

# --- palette -------------------------------------------------------------
PAPER = (238, 228, 203)
PAPER_DARK = (226, 212, 178)
INK = (43, 33, 24)
INK_SOFT = (74, 60, 44)
RED = (126, 29, 29)
RED_DARK = (94, 20, 20)
GOLD = (198, 152, 62)
GOLD_LIGHT = (238, 205, 122)
GOLD_DARK = (146, 106, 40)
NIGHT = (30, 40, 58)
NIGHT_DEEP = (18, 26, 40)
WATER = (24, 44, 62)
CLOUD = (216, 208, 188)
SLATE = (88, 104, 120)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
NOTO_DIR = "/usr/share/fonts/truetype/noto"


def _font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise FileNotFoundError(candidates[0])


def serif(size):
    return _font([os.path.join(FONT_DIR, "DejaVuSerif.ttf")], size)


def serif_bold(size):
    return _font([os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")], size)


def serif_italic(size):
    return _font(
        [
            os.path.join(NOTO_DIR, "NotoSerif-Italic.ttf"),
            os.path.join(FONT_DIR, "DejaVuSerif.ttf"),
        ],
        size,
    )


def sans_bold(size):
    return _font([os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")], size)


def sans(size):
    return _font([os.path.join(FONT_DIR, "DejaVuSans.ttf")], size)


# --- text helpers ---------------------------------------------------------

def wrap(draw, text, font, width):
    """Greedy word wrap; returns list of lines that fit `width`."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def block(draw, text, x, y, width, font, line_h, color=INK, align="left"):
    """Draw wrapped text; returns the y just past the last line."""
    for line in wrap(draw, text, font, width):
        if align == "center":
            tw = draw.textlength(line, font=font)
            draw.text((x + (width - tw) / 2, y), line, font=font, fill=color)
        else:
            draw.text((x, y), line, font=font, fill=color)
        y += line_h
    return y


def centered(draw, text, cx, y, font, color=INK):
    tw = draw.textlength(text, font=font)
    draw.text((cx - tw / 2, y), text, font=font, fill=color)
    return y + font.size


def rule(draw, x0, x1, y, color=INK, width=2):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


# --- texture helpers ------------------------------------------------------

def grain(img, box, seed, dots=2600, alpha=26):
    """Sprinkle deterministic halftone-style dots over a panel."""
    rng = random.Random(seed)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = box
    for _ in range(dots):
        px = rng.uniform(x0, x1)
        py = rng.uniform(y0, y1)
        r = rng.uniform(0.5, 1.6)
        shade = rng.choice([(0, 0, 0), (255, 246, 220)])
        od.ellipse([px - r, py - r, px + r, py + r], fill=shade + (alpha,))
    img.alpha_composite(overlay)


def hatch(draw, box, seed, lines=46, color=(0, 0, 0), alpha=30, img=None):
    """Engraved diagonal hatch lines clipped to a box, via overlay."""
    rng = random.Random(seed)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = box
    step = max(4, (x1 - x0) // lines)
    for gx in range(int(x0) - int(y1 - y0), int(x1), step):
        jitter = rng.uniform(-1.5, 1.5)
        od.line(
            [(gx + jitter, y1), (gx + (y1 - y0) + jitter, y0)],
            fill=color + (alpha,),
            width=1,
        )
    img.alpha_composite(overlay)


def frame(draw, box, color=INK):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], outline=color, width=3)
    draw.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=color, width=1)


# --- illustrations ---------------------------------------------------------

def art_bridges(img, box):
    """Night over the Dnipro: two bridges, searchlights, smoke, bursts."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    w = x1 - x0
    h = y1 - y0
    horizon = y0 + int(h * 0.66)

    # sky gradient bands
    for i in range(horizon - y0):
        t = i / max(1, horizon - y0)
        col = tuple(
            int(NIGHT_DEEP[c] + (NIGHT[c] - NIGHT_DEEP[c]) * t) for c in range(3)
        )
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=col + (255,))
    # water
    d.rectangle([x0, horizon, x1, y1], fill=WATER + (255,))
    # stars
    rng = random.Random(41)
    for _ in range(90):
        sx = rng.uniform(x0 + 4, x1 - 4)
        sy = rng.uniform(y0 + 4, horizon - 30)
        r = rng.uniform(0.6, 1.7)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(240, 232, 200, 210))
    # moon
    mx, my = x0 + int(w * 0.82), y0 + int(h * 0.16)
    d.ellipse([mx - 17, my - 17, mx + 17, my + 17], fill=(232, 220, 180, 255))
    d.ellipse([mx - 8, my - 17, mx + 20, my + 17], fill=NIGHT_DEEP + (255,))

    # searchlight beams (translucent wedges from the far bank)
    beams = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(beams)
    for bx, ang in ((0.16, -0.5), (0.55, -0.18), (0.9, -0.85)):
        base = (x0 + int(w * bx), horizon)
        tip = (base[0] + int(w * 0.34 * math.sin(ang + 1.2)), y0 + 6)
        spread = 13
        bd.polygon(
            [
                (base[0] - spread, base[1]),
                (base[0] + spread, base[1]),
                (tip[0] + 4, tip[1]),
                (tip[0] - 4, tip[1]),
            ],
            fill=(245, 238, 200, 52),
        )
    img.alpha_composite(beams)
    d = ImageDraw.Draw(img, "RGBA")

    deck = horizon - int(h * 0.10)
    silhouette = (10, 13, 20, 255)

    # left bridge: shallow arch bridge
    ax0, ax1 = x0 + int(w * 0.03), x0 + int(w * 0.47)
    d.line([(ax0, deck), (ax1, deck)], fill=silhouette, width=7)
    d.arc([ax0, deck - int(h * 0.20), ax1, deck + int(h * 0.20)],
          start=180, end=360, fill=silhouette, width=5)
    for fx in range(ax0 + 14, ax1, 34):
        d.line([(fx, deck), (fx, horizon + 16)], fill=silhouette, width=4)
    # right bridge: cable-stayed, one tall pylon
    bx0, bx1 = x0 + int(w * 0.55), x0 + int(w * 0.97)
    pylon_x = x0 + int(w * 0.74)
    pylon_top = y0 + int(h * 0.10)
    d.line([(bx0, deck), (bx1, deck)], fill=silhouette, width=7)
    d.line([(pylon_x, pylon_top), (pylon_x, horizon + 16)],
           fill=silhouette, width=7)
    for t in (0.16, 0.38, 0.62, 0.86):
        fx = bx0 + int((pylon_x - bx0) * t)
        d.line([(pylon_x, pylon_top + 8), (fx, deck)], fill=silhouette, width=2)
        fx2 = pylon_x + int((bx1 - pylon_x) * t)
        d.line([(pylon_x, pylon_top + 8), (fx2, deck)], fill=silhouette, width=2)
    for fx in range(bx0 + 12, bx1, 38):
        d.line([(fx, deck), (fx, horizon + 16)], fill=silhouette, width=4)

    # smoke plumes rising from the deck
    for cx, cy, s in ((0.30, 0.34, 30), (0.66, 0.30, 36), (0.80, 0.40, 24)):
        for k in range(6):
            px = x0 + int(w * cx) + int(k * 7)
            py = y0 + int(h * cy) - int(k * 12)
            r = s - k * 3
            d.ellipse([px - r, py - r * 0.62, px + r, py + r * 0.62],
                      fill=(120, 116, 110, 120))

    # explosion starbursts over the bridges
    def burst(cx, cy, r):
        for a in range(0, 360, 24):
            rad = math.radians(a + 7)
            d.line(
                [(cx, cy), (cx + r * math.cos(rad), cy + r * math.sin(rad))],
                fill=(250, 176, 84, 235),
                width=3,
            )
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 226, 150, 255))

    burst(x0 + int(w * 0.30), deck - int(h * 0.16), 26)
    burst(x0 + int(w * 0.68), deck - int(h * 0.05), 20)

    # tracer arcs
    for sx, ex, peak in ((0.06, 0.34, 0.30), (0.97, 0.70, 0.22)):
        pts = []
        for i in range(25):
            t = i / 24
            px = x0 + w * (sx + (ex - sx) * t)
            py = horizon - (h * peak) * 4 * t * (1 - t) - int(h * 0.10)
            pts.append((px, py))
        d.line(pts, fill=(255, 120, 80, 200), width=2)

    # water reflections
    rng2 = random.Random(7)
    for _ in range(120):
        rx = rng2.uniform(x0 + 6, x1 - 26)
        ry = rng2.uniform(horizon + 5, y1 - 5)
        ln = rng2.uniform(6, 22)
        tone = rng2.choice([(210, 200, 160), (150, 170, 190), (240, 180, 110)])
        d.line([(rx, ry), (rx + ln, ry)], fill=tone + (110,), width=2)

    grain(img, box, seed=99, dots=2000, alpha=20)
    frame(ImageDraw.Draw(img), box)


def art_chart(img, box):
    """A stock index plunging off a cliff, engraved chart style."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle(box, fill=(243, 236, 214, 255))
    pad_l, pad_r, pad_t, pad_b = 16, 12, 12, 18
    gx0, gy0 = x0 + pad_l, y0 + pad_t
    gx1, gy1 = x1 - pad_r, y1 - pad_b
    # grid
    for i in range(5):
        gy = gy0 + (gy1 - gy0) * i / 4
        d.line([(gx0, gy), (gx1, gy)], fill=(150, 138, 112, 160), width=1)
    for i in range(6):
        gx = gx0 + (gx1 - gx0) * i / 5
        d.line([(gx, gy0), (gx, gy1)], fill=(150, 138, 112, 110), width=1)
    d.line([(gx0, gy0), (gx0, gy1)], fill=INK + (255,), width=2)
    d.line([(gx0, gy1), (gx1, gy1)], fill=INK + (255,), width=2)
    # the line: wobbles along the top, then falls off a cliff
    rng = random.Random(23)
    pts = []
    n = 34
    for i in range(n + 1):
        t = i / n
        px = gx0 + (gx1 - gx0) * t
        if t < 0.55:
            frac = 0.10 + 0.05 * math.sin(t * 22) + rng.uniform(-0.015, 0.015)
        else:
            u = (t - 0.55) / 0.45
            frac = 0.10 + 0.72 * (u ** 1.6) + rng.uniform(-0.012, 0.012)
        pts.append((px, gy0 + (gy1 - gy0) * frac))
    d.line(pts, fill=RED + (255,), width=4)
    # area hatch under the fallen tail
    tail = [p for p in pts if p[0] > gx0 + (gx1 - gx0) * 0.55]
    if tail:
        poly = tail + [(tail[-1][0], gy1), (tail[0][0], gy1)]
        d.polygon(poly, fill=RED + (36,))
    # arrowhead at the end
    ex, ey = pts[-1]
    d.polygon(
        [(ex, ey + 12), (ex - 13, ey - 4), (ex + 3, ey - 9)],
        fill=RED + (255,),
    )
    # volume bars
    for i in range(14):
        bx = gx0 + 6 + i * ((gx1 - gx0 - 12) / 14)
        bh = 6 + (i / 14) ** 2 * (pad_b + 16)
        d.rectangle([bx, gy1 - bh, bx + 7, gy1], fill=INK_SOFT + (200,))
    lab = "-6.2%"
    lf = sans_bold(21)
    d.text((gx1 - d.textlength(lab, font=lf) - 4, gy0 + 2), lab, font=lf,
           fill=RED + (255,))
    grain(img, box, seed=55, dots=700, alpha=16)
    frame(ImageDraw.Draw(img), box)


def art_gold(img, box):
    """Pyramid of gold bars with coins, on a dark vault backdrop."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle(box, fill=(52, 40, 26, 255))
    # soft radial glow behind the stack
    cx, cy = (x0 + x1) // 2, y0 + int((y1 - y0) * 0.52)
    for r in range(64, 8, -8):
        a = int(44 * (1 - r / 74))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 120, max(0, a)))
    d = ImageDraw.Draw(img, "RGBA")
    floor = y1 - 16

    def bar(bx, by, bw, bh):
        top = [(bx + 8, by), (bx + bw - 8, by), (bx + bw, by + bh * 0.42),
               (bx, by + bh * 0.42)]
        front = [(bx, by + bh * 0.42), (bx + bw, by + bh * 0.42),
                 (bx + bw, by + bh), (bx, by + bh)]
        d.polygon(top, fill=GOLD_LIGHT + (255,))
        d.polygon(front, fill=GOLD + (255,))
        d.line([(bx, by + bh * 0.42), (bx + bw, by + bh * 0.42)],
               fill=GOLD_DARK + (255,), width=2)
        d.polygon(front, outline=GOLD_DARK + (255,))

    bw, bh = 86, 26
    base_y = floor - bh
    for i in range(3):  # bottom row
        bar(x0 + 26 + i * (bw + 8), base_y, bw, bh)
    for i in range(2):  # middle row
        bar(x0 + 26 + (bw // 2 + 4) + i * (bw + 8), base_y - bh - 7, bw, bh)
    bar(x0 + 26 + bw + 8, base_y - 2 * bh - 14, bw, bh)  # top bar

    # coins spilling at the sides
    rng = random.Random(5)
    for i in range(9):
        side = rng.choice([-1, 1])
        ccx = cx + side * rng.uniform(105, 138)
        ccy = floor - rng.uniform(0, 12)
        r = rng.uniform(9, 13)
        d.ellipse([ccx - r, ccy - r * 0.42, ccx + r, ccy + r * 0.42],
                  fill=GOLD_LIGHT + (255,), outline=GOLD_DARK + (255,))
    # sparkles
    for sx, sy in ((x0 + 40, y0 + 26), (x1 - 44, y0 + 20), (cx + 60, y0 + 40)):
        for dx, dy in ((0, -9), (0, 9), (-9, 0), (9, 0)):
            d.line([(sx, sy), (sx + dx, sy + dy)], fill=(255, 240, 190, 230),
                   width=2)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 246, 210, 255))
    grain(img, box, seed=77, dots=800, alpha=18)
    frame(ImageDraw.Draw(img), box)


def art_cyclone(img, box):
    """Satellite-style spiral of a cyclone, engraved cloud bands."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    # sea-sky backdrop
    for i in range(y1 - y0):
        t = i / max(1, y1 - y0)
        col = tuple(int(58 + (34 - 58) * t + 0 * c) for c in range(3))
        col = (int(66 - 26 * t), int(88 - 30 * t), int(110 - 34 * t))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=col + (255,))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 4
    max_r = min(x1 - x0, y1 - y0) * 0.52
    # spiral arms: several archimedean bands of cloud
    for arm in range(3):
        offset = arm * (2 * math.pi / 3)
        pts = []
        steps = 130
        for i in range(steps + 1):
            t = i / steps
            ang = offset + t * math.pi * 3.4
            r = 8 + (max_r - 8) * t
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.82))
        for j in range(len(pts) - 1):
            t = j / len(pts)
            width = max(2, int(13 * (1 - t) + 3))
            tone = int(226 - 60 * t)
            d.line([pts[j], pts[j + 1]],
                   fill=(tone, tone - 4, tone - 16, 235), width=width)
    # outer cloud wisps
    rng = random.Random(31)
    for _ in range(26):
        ang = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(max_r * 0.75, max_r * 1.12)
        wx, wy = cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.82
        ln = rng.uniform(14, 34)
        d.arc([wx - ln, wy - ln * 0.4, wx + ln, wy + ln * 0.4],
              start=rng.uniform(0, 180), end=rng.uniform(180, 360),
              fill=(205, 205, 195, 170), width=3)
    # the eye
    d.ellipse([cx - 13, cy - 11, cx + 13, cy + 11], fill=(24, 34, 48, 255))
    d.ellipse([cx - 13, cy - 11, cx + 13, cy + 11], outline=(235, 232, 215, 255),
              width=3)
    grain(img, box, seed=63, dots=900, alpha=16)
    frame(ImageDraw.Draw(img), box)


def art_phone(img, box):
    """A Galaxy-style smartphone silhouette, three-quarter upright."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle(box, fill=(238, 230, 206, 255))
    # backdrop rays
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for a in range(0, 360, 30):
        rad = math.radians(a)
        d.line(
            [(cx, cy), (cx + 120 * math.cos(rad), cy + 120 * math.sin(rad))],
            fill=(214, 198, 158, 160),
            width=5,
        )
    ph = (y1 - y0) - 12
    pw = int(ph * 0.52)
    px0, py0 = x0 + ((x1 - x0) - pw) // 2, y0 + 6
    px1, py1 = px0 + pw, py0 + ph
    # shadow
    d.ellipse([px0 + 4, py1 - 6, px1 - 2, py1 + 8], fill=(120, 104, 74, 120))
    # body
    d.rounded_rectangle([px0, py0, px1, py1], radius=13,
                        fill=(24, 24, 30, 255), outline=(70, 62, 48, 255),
                        width=2)
    # screen
    sx0, sy0, sx1, sy1 = px0 + 6, py0 + 6, px1 - 6, py1 - 6
    for i in range(sy1 - sy0):
        t = i / max(1, sy1 - sy0)
        col = (int(38 + 60 * t), int(52 + 66 * t), int(84 + 70 * t))
        d.line([(sx0, sy0 + i), (sx1, sy0 + i)], fill=col + (255,))
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=9, outline=(10, 10, 14, 255))
    # screen glow diagonal
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.polygon(
        [(sx0 + 6, sy1 - 30), (sx0 + 34, sy0 + 4), (sx0 + 62, sy0 + 4),
         (sx0 + 30, sy1 - 26)],
        fill=(255, 255, 255, 40),
    )
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img, "RGBA")
    # camera punch-hole + rear lenses hint on the frame edge
    ccx = (sx0 + sx1) // 2
    d.ellipse([ccx - 4, sy0 + 8, ccx + 4, sy0 + 16], fill=(8, 8, 12, 255))
    # side buttons
    d.rectangle([px1, py0 + 34, px1 + 3, py0 + 62], fill=(24, 24, 30, 255))
    d.rectangle([px1, py0 + 70, px1 + 3, py0 + 88], fill=(24, 24, 30, 255))
    # sparkles
    for sx, sy in ((x0 + 14, y0 + 16), (x1 - 14, y0 + 30)):
        for dx, dy in ((0, -7), (0, 7), (-7, 0), (7, 0)):
            d.line([(sx, sy), (sx + dx, sy + dy)], fill=GOLD_DARK + (220,),
                   width=2)
    grain(img, box, seed=88, dots=300, alpha=14)
    frame(ImageDraw.Draw(img), box)


# --- story furniture -------------------------------------------------------

MX = 36            # outer margin
RIGHT = W - MX     # 988
COL_GAP = 22


def kicker(draw, text, x, y, size=12):
    draw.text((x, y), text, font=sans_bold(size), fill=RED)
    return y + size + 5


def headline(draw, text, x, y, width, size=19, align="left"):
    f = serif_bold(size)
    lh = int(size * 1.14)
    for line in wrap(draw, text, f, width):
        if align == "center":
            tw = draw.textlength(line, font=f)
            draw.text((x + (width - tw) / 2, y), line, font=f, fill=INK)
        else:
            draw.text((x, y), line, font=f, fill=INK)
        y += lh
    return y + 3


def body(draw, text, x, y, width, size=12, lh=16):
    return block(draw, text, x, y, width, serif(size), lh, INK)


def place(img, art_fn, box):
    """Render an illustration on its own tile and paste it, so artwork
    can never spill outside its box onto neighbouring text."""
    x0, y0, x1, y1 = box
    tile = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    art_fn(tile, (0, 0, x1 - x0, y1 - y0))
    img.alpha_composite(tile, (x0, y0))


# --- the page --------------------------------------------------------------

def build():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img, "RGBA")

    # aged paper speckle
    rng = random.Random(2026)
    for _ in range(2600):
        px, py = rng.uniform(0, W), rng.uniform(0, H)
        tone = rng.choice([(214, 198, 158), (246, 240, 218)])
        d.point((px, py), fill=tone + (120,))

    # outer frame
    d.rectangle([14, 14, W - 14, H - 14], outline=INK, width=3)
    d.rectangle([20, 20, W - 20, H - 20], outline=INK, width=1)

    # ===== masthead (28-196) =====
    centered(d, "MAKE IT NEWS", W // 2, 30, serif_bold(92), RED_DARK)
    centered(d, "T H E   W O R L D   O N   F R I D A Y ,   2 0   N O V E M B E R   2 0 2 6",
             W // 2, 140, serif_bold(17), INK)
    d.rectangle([MX, 168, RIGHT, 196], fill=RED)
    d.text((MX + 12, 175), "No. 19,412", font=sans_bold(13),
           fill=(245, 238, 220))
    centered(d, "FRIDAY, 20 NOVEMBER 2026", W // 2, 175, sans_bold(13),
             (245, 238, 220))
    t = "PRICE: ONE PENNY"
    d.text((RIGHT - 12 - d.textlength(t, font=sans_bold(13)), 175), t,
           font=sans_bold(13), fill=(245, 238, 220))

    # ===== lead headline zone (206-296) =====
    ly = 208
    f = sans_bold(12)
    kt = "UKRAINE WAR  •  KYIV"
    d.text(((W - d.textlength(kt, font=f)) / 2, ly), kt, font=f, fill=RED)
    ly = headline(d, "RUSSIA BATTERS KYIV'S BRIDGES", MX, ly + 19, RIGHT - MX,
                  size=40, align="center")
    block(d, "Overnight ballistic strikes damage three Dnipro crossings, "
             "kill three people and cut the capital in two",
          MX, ly + 1, RIGHT - MX, serif_italic(15), 20, INK_SOFT, "center")

    # ===== band A: lead art + lead text + Samsung (300-540) =====
    ay = 300
    art_box = (MX, ay, 632, ay + 224)
    place(img, art_bridges, art_box)
    d = ImageDraw.Draw(img, "RGBA")
    block(d, "The capital's three Dnipro crossings, hit in the largest "
             "such attack of the war.",
          MX, ay + 230, 596, serif_italic(11), 14, INK_SOFT)

    tx, tw = 656, RIGHT - 656
    ty = body(d, "Russian ballistic missiles struck three of Kyiv's bridges "
                 "over the Dnipro in the early hours of Friday, in the "
                 "largest attack on the capital's crossings since the war "
                 "began. Mayor Vitali Klitschko said the Podilsko-"
                 "Voskresenskyi, Darnytskyi and Pivdennyi bridges were all "
                 "hit, killing three people and injuring about 15. Traffic "
                 "across the river was closed or heavily restricted.",
              tx, ay, tw, size=12, lh=16)
    rule(d, tx, RIGHT, ty + 6, RED, 1)

    # Samsung compact, phone art floated left
    sy = ty + 14
    pb = (tx, sy, tx + 66, 540)
    place(img, art_phone, pb)
    d = ImageDraw.Draw(img, "RGBA")
    sx, sw = tx + 78, RIGHT - (tx + 78)
    sy = kicker(d, "TECHNOLOGY  •  SEOUL", sx, sy)
    sy = headline(d, "SAMSUNG NAMES NEW GALAXY CHIEF", sx, sy, sw, size=15)
    body(d, "Samsung has put Won-Joon Choi in charge of its mobile "
            "division, ending TM Roh's seven-year run as Galaxy chief. "
            "Roh stays on as co-CEO.", sx, sy, sw, size=10.5, lh=13.5)

    # ===== markets ticker (550-578) =====
    d.rectangle([MX, 550, RIGHT, 578], outline=INK, width=2)
    d.rectangle([MX, 550, MX + 128, 578], fill=RED)
    d.text((MX + 10, 557), "THE MARKETS", font=sans_bold(12),
           fill=(245, 238, 220))
    block(d, "TAIEX 36,033  -6.2%    KOSPI 4,870  -5.2%    NIKKEI 225 "
             "56,437  -5.1%    GOLD $3,551  -1.9%    SILVER $41.19  low    "
             "ANTHROPIC $91.24  pre-mkt",
          MX + 140, 557, RIGHT - MX - 148, sans(11), 15, INK)

    # ===== band B: three illustrated stories (588-814) =====
    col_w = (RIGHT - MX - 2 * COL_GAP) // 3  # 302
    xs = [MX, MX + col_w + COL_GAP, MX + 2 * (col_w + COL_GAP)]
    by2 = 588

    def art_story(idx, kick, head, art_fn, text):
        x = xs[idx]
        y = kicker(d, kick, x, by2)
        y = headline(d, head, x, y, col_w, size=16)
        ab = (x, y + 2, x + col_w, y + 2 + 108)
        place(img, art_fn, ab)
        d2 = ImageDraw.Draw(img, "RGBA")
        body(d2, text, x, ab[3] + 7, col_w, size=11, lh=13.5)

    art_story(0, "MARKETS  •  TAIPEI", "TAIWAN STOCKS CRASH IN AI ROUT",
              art_chart,
              "Taiwan's Taiex plunged 6.2 per cent on Friday, capping a "
              "weekly fall of some 17 per cent — its worst week since "
              "1991. TSMC, over 40 per cent of the index, slid about "
              "5 per cent.")
    art_story(1, "MARKETS  •  BULLION", "GOLD BREAKS BELOW $3,600",
              art_gold,
              "Spot gold fell to $3,551 an ounce, its lowest since "
              "September 2025, in the worst week since March as bets on "
              "Federal Reserve rate rises lifted the dollar. Silver was "
              "dragged below $42.")
    art_story(2, "PACIFIC  •  COOK ISLANDS", "CYCLONE XAVIER WEAKENS",
              art_cyclone,
              "Cyclone Xavier, the strongest November storm on record "
              "east of the date line, has weakened after peaking at "
              "220 km/h and damaging homes in the northern Cook Islands. "
              "Now Category 4; gale warnings in force.")

    d = ImageDraw.Draw(img, "RGBA")
    for gx in (xs[1] - COL_GAP // 2 - 1, xs[2] - COL_GAP // 2 - 1):
        d.line([(gx, by2), (gx, 814)], fill=INK_SOFT, width=1)
    rule(d, MX, RIGHT, 822, INK, 3)
    rule(d, MX, RIGHT, 827, INK, 1)

    # ===== band C: four text stories (834-940) =====
    cy = 834
    cgap = 16
    ccw = (RIGHT - MX - 3 * cgap) // 4  # 226
    cxs = [MX + i * (ccw + cgap) for i in range(4)]

    def compact(idx, kick, head, text):
        x = cxs[idx]
        y = kicker(d, kick, x, cy, size=11)
        y = headline(d, head, x, y, ccw, size=15)
        body(d, text, x, y, ccw, size=10.5, lh=13.5)

    compact(0, "CLIMATE  •  ANTALYA",
            "COP31 DEADLOCKED OVER FOSSIL FUELS",
            "The UN summit entered its final day deadlocked after a "
            "revised draft dropped every mention of fossil fuels and "
            "the $120bn adaptation figure.")
    compact(1, "JUSTICE  •  THE HAGUE",
            "WORLD COURT: MYANMAR GENOCIDE",
            "The ICJ ruled Myanmar committed genocide against its "
            "Rohingya minority — the first such finding against a "
            "state. Judges voted nine to six.")
    compact(2, "POLITICS  •  SHENZHEN",
            "TRUMP, XI, PUTIN SIGN PEACE PACT",
            "The presidents of the United States, China and Russia met "
            "in Shenzhen for their first-ever three-way summit and "
            "signed a four-point joint declaration.")
    compact(3, "BUSINESS  •  NEW YORK",
            "ANTHROPIC STUMBLES AFTER IPO",
            "Shares in Anthropic fell about 6 per cent before Friday's "
            "open, extending the fade from the largest IPO on record. "
            "It closed its debut up 17 per cent at $97.17.")

    for gx in (cxs[1] - cgap // 2 - 1, cxs[2] - cgap // 2 - 1,
               cxs[3] - cgap // 2 - 1):
        d.line([(gx, cy), (gx, 940)], fill=INK_SOFT, width=1)

    # ===== in brief strip (948-982) =====
    d.rectangle([MX, 948, RIGHT, 982], fill=PAPER_DARK)
    d.rectangle([MX, 948, RIGHT, 982], outline=INK_SOFT, width=1)
    block(d, "IN BRIEF — RIYADH: Houthi missiles damaged the Saudi wealth "
             "fund's tower.  •  BERLIN: allies say Europe is ready for "
             "talks with Russia.  •  WASHINGTON: White House dismisses its "
             "cyber director.  •  TOKYO: Kospi and Nikkei both fell 5%.  "
             "•  NEW YORK: silver's crash wiped $1tn from metals.",
          MX + 10, 954, RIGHT - MX - 20, sans(10), 13, INK)

    # ===== footer =====
    rule(d, MX, RIGHT, 990, INK, 1)
    centered(d, "Make It News  •  All nine stories verified from wire "
                "reports  •  Friday 20 November 2026",
             W // 2, 994, serif_italic(10), INK_SOFT)

    img.convert("RGB").save(OUT, "PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    build()
