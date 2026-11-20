#!/usr/bin/env python3
"""Render the *Make It News* front page for Friday, 20 November 2026.

The whole page -- masthead, headlines, body copy and every illustration --
is drawn with Pillow primitives on a 1024x1024 canvas.  No photographs,
no model-generated art, no network access: the output is a deterministic
function of this file, so `entry.png` can be rebuilt byte-for-byte by
running the script again.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas and palette
# --------------------------------------------------------------------------

PAGE_W = 1024
PAGE_H = 1024
EDGE = 36                      # outer margin of the printed area
RIGHT = PAGE_W - EDGE          # right edge of the printed area

PAPER = (243, 234, 216)        # warm newsprint cream
INK = (28, 25, 21)             # near-black for headlines and body
SOFT_INK = (74, 68, 60)        # captions and small print
MASTHEAD_RED = (143, 29, 34)
BANNER_RED = (152, 31, 38)
RULE = (40, 36, 31)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF = os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf")

_font_cache = {}


def serif(size, bold=False, italic=False):
    """Return a cached Liberation Serif face at the given size."""
    path = SERIF_BOLD if bold else (SERIF_ITALIC if italic else SERIF)
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def width_of(draw, text, font, tracking=0):
    """Pixel width of a string, optionally with letter tracking."""
    w = draw.textlength(text, font=font)
    if tracking:
        w += tracking * max(0, len(text) - 1)
    return w


def draw_tracked(draw, cx, y, text, font, fill, tracking=2):
    """Draw text centred on cx with extra space between the letters."""
    total = width_of(draw, text, font, tracking)
    x = cx - total / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return total


def wrap_to_width(draw, text, font, limit):
    """Greedy word wrap: return the list of lines that fit `limit` px."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= limit or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def centred_lines(draw, cx, top, text, font, fill, limit, leading):
    """Wrap `text` and draw it centred; return the y below the block."""
    y = top
    for line in wrap_to_width(draw, text, font, limit):
        w = draw.textlength(line, font=font)
        draw.text((cx - w / 2, y), line, font=font, fill=fill)
        y += leading
    return y


def fit_font(draw, text, limit, start, bold=True):
    """Largest serif size (<= start) whose width fits `limit`."""
    size = start
    while size > 10 and draw.textlength(text, font=serif(size, bold=bold)) > limit:
        size -= 2
    return serif(size, bold=bold)


def rule(draw, y, weight=2):
    draw.line([(EDGE, y), (RIGHT, y)], fill=RULE, width=weight)


# --------------------------------------------------------------------------
# Illustration helpers
# --------------------------------------------------------------------------

def panel(draw, box, fill):
    """A bordered illustration box."""
    draw.rectangle(box, fill=fill, outline=(88, 82, 72), width=2)


def starburst(draw, cx, cy, r_out, r_in, fill):
    """A spiky explosion flash: alternating outer/inner points."""
    pts = []
    for i in range(16):
        ang = math.pi * i / 8 - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def spiral_points(cx, cy, turns, r_start, r_end, steps=140):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        ang = turns * 2 * math.pi * t
        r = r_start + (r_end - r_start) * t
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def bridge_scene(draw, box):
    """Night over the Dnipro: skyline, three bridges, two missile trails."""
    x0, y0, x1, y1 = box
    panel(draw, box, (17, 30, 54))
    rng = random.Random(20261120)
    for _ in range(46):  # stars
        sx = rng.uniform(x0 + 8, x1 - 8)
        sy = rng.uniform(y0 + 8, y0 + (y1 - y0) * 0.45)
        draw.point((sx, sy), fill=(210, 218, 235))
    horizon = y0 + (y1 - y0) * 0.60
    # city silhouette
    bx = x0 + 6
    while bx < x1 - 20:
        bw = rng.uniform(18, 44)
        bh = rng.uniform(10, 30)
        draw.rectangle([bx, horizon - bh, bx + bw, horizon], fill=(9, 15, 27))
        bx += bw + rng.uniform(2, 9)
    # river
    draw.rectangle([x0 + 2, horizon, x1 - 2, y1 - 2], fill=(34, 57, 88))
    for _ in range(9):
        sx = rng.uniform(x0 + 14, x1 - 60)
        sy = rng.uniform(horizon + 8, y1 - 10)
        draw.line([(sx, sy), (sx + rng.uniform(16, 42), sy)],
                  fill=(70, 98, 132), width=2)
    # three bridges: deck, two piers and a shallow arch each
    deck_y = horizon + 4
    span = (x1 - x0 - 40) / 3
    for i in range(3):
        cx = x0 + 26 + span * i + span / 2
        half = span / 2 - 6
        draw.line([(cx - half, deck_y), (cx + half, deck_y)],
                  fill=(205, 203, 192), width=3)
        draw.line([(cx - half, deck_y), (cx, deck_y + 26)],
                  fill=(205, 203, 192), width=2)
        draw.line([(cx + half, deck_y), (cx, deck_y + 26)],
                  fill=(205, 203, 192), width=2)
        draw.line([(cx - half + 4, deck_y + 26), (cx + half - 4, deck_y + 26)],
                  fill=(160, 158, 148), width=2)
    # missile trails and their flashes
    hits = [(x0 + (x1 - x0) * 0.60, y0 + (y1 - y0) * 0.52),
            (x0 + (x1 - x0) * 0.90, y0 + (y1 - y0) * 0.55)]
    starts = [(x0 + (x1 - x0) * 0.38, y0 + 8),
              (x0 + (x1 - x0) * 0.74, y0 + 8)]
    for (sx, sy), (hx, hy) in zip(starts, hits):
        draw.line([(sx, sy), (hx, hy)], fill=(235, 238, 245), width=3)
        starburst(draw, hx, hy, 17, 7, (243, 156, 44))
        draw.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=(252, 209, 96))


def taiex_scene(draw, box):
    """Falling bars and a plunging index line."""
    x0, y0, x1, y1 = box
    panel(draw, box, (238, 230, 213))
    base = y1 - 16
    heights = [0.78, 0.70, 0.82, 0.62, 0.55, 0.42, 0.33, 0.24]
    bw = (x1 - x0 - 40) / len(heights)
    tops = []
    for i, frac in enumerate(heights):
        bx = x0 + 16 + i * bw
        top = base - frac * (y1 - y0 - 52)
        draw.rectangle([bx, top, bx + bw - 9, base], fill=(122, 119, 110))
        tops.append((bx + (bw - 9) / 2, top - 6))
    draw.line(tops, fill=(154, 32, 38), width=3)
    lx, ly = tops[-1]
    draw.polygon([(lx + 14, ly + 4), (lx - 2, ly - 4), (lx + 1, ly + 12)],
                 fill=(154, 32, 38))
    f = serif(21, bold=True)
    draw.text((x0 + 14, y0 + 8), "TAIEX", font=f, fill=INK)
    drop = "-6.2%"
    fw = draw.textlength(drop, font=serif(25, bold=True))
    draw.text((x1 - fw - 14, y0 + 6), drop, font=serif(25, bold=True),
              fill=(154, 32, 38))


def cop_scene(draw, box):
    """A planet, a hard sun, and negotiators on a bare horizon."""
    x0, y0, x1, y1 = box
    panel(draw, box, (197, 223, 239))
    cx, cy, r = x0 + (x1 - x0) * 0.36, y0 + (y1 - y0) * 0.48, 40
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 161, 206),
                 outline=(70, 110, 160), width=2)
    for dx, dy, rw, rh in [(-18, -14, 26, 16), (6, 4, 30, 18), (-6, 20, 18, 12)]:
        draw.ellipse([cx + dx, cy + dy, cx + dx + rw, cy + dy + rh],
                     fill=(96, 166, 96))
    sx, sy = x1 - 44, y0 + 30
    for i in range(8):
        ang = math.pi * i / 4
        draw.line([(sx + 22 * math.cos(ang), sy + 22 * math.sin(ang)),
                   (sx + 30 * math.cos(ang), sy + 30 * math.sin(ang))],
                  fill=(238, 138, 30), width=3)
    draw.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(243, 156, 44))
    ground = y1 - 16
    draw.rectangle([x0 + 2, ground, x1 - 2, y1 - 2], fill=(146, 104, 62))
    for fx in (0.52, 0.68, 0.84):
        px = x0 + (x1 - x0) * fx
        draw.ellipse([px - 6, ground - 12, px + 6, ground], fill=(24, 22, 20))
        draw.pieslice([px - 11, ground - 8, px + 11, ground + 8], 180, 360,
                      fill=(24, 22, 20))


def gold_scene(draw, box):
    """A sliding price line above a small stack of ingots."""
    x0, y0, x1, y1 = box
    panel(draw, box, (240, 233, 215))
    pts = [(x0 + 14, y0 + 18), (x0 + (x1 - x0) * 0.34, y0 + 26),
           (x0 + (x1 - x0) * 0.58, y0 + 40), (x0 + (x1 - x0) * 0.80, y0 + 62)]
    draw.line(pts, fill=(154, 32, 38), width=3)
    lx, ly = pts[-1]
    draw.polygon([(lx + 15, ly + 5), (lx - 1, ly - 5), (lx + 2, ly + 13)],
                 fill=(154, 32, 38))

    def ingot(ix, iy, w=56, h=17):
        inset = 8
        draw.polygon([(ix + inset, iy), (ix + w - inset, iy),
                      (ix + w, iy + h), (ix, iy + h)],
                     fill=(214, 166, 54), outline=(148, 108, 28))

    base = y1 - 14
    ingot(x0 + 16, base - 17)
    ingot(x0 + 78, base - 17)
    ingot(x0 + 47, base - 35)
    label = "$3,551"
    f = serif(25, bold=True)
    draw.text((x1 - draw.textlength(label, font=f) - 14, base - 30),
              label, font=f, fill=INK)


def galaxy_scene(draw, box):
    """A phone under a night sky, a spiral galaxy on its screen."""
    x0, y0, x1, y1 = box
    panel(draw, box, (13, 22, 44))
    rng = random.Random(99)
    for _ in range(26):
        draw.point((rng.uniform(x0 + 6, x1 - 6), rng.uniform(y0 + 6, y1 - 6)),
                   fill=(190, 200, 225))
    starburst(draw, x0 + 52, y0 + 34, 15, 5, (240, 190, 70))
    ph = (y1 - y0) - 14
    pw = ph * 0.78
    px = x0 + (x1 - x0) / 2 - pw / 2
    py = y0 + ((y1 - y0) - ph) / 2
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=10,
                           outline=(205, 210, 224), width=3)
    cx, cy = px + pw / 2, py + ph / 2
    draw.line(spiral_points(cx, cy, 2.2, 2, ph * 0.30, 120),
              fill=(168, 198, 240), width=2)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(235, 242, 255))


def cyclone_scene(draw, box):
    """A white spiral storm over dark water, one small island."""
    x0, y0, x1, y1 = box
    panel(draw, box, (23, 54, 92))
    f = serif(20, bold=True)
    draw.text((x0 + 14, y0 + 10), "XAVIER", font=f, fill=(240, 244, 250))
    cx, cy = x0 + (x1 - x0) * 0.58, y0 + (y1 - y0) * 0.52
    draw.line(spiral_points(cx, cy, 2.6, 3, 34, 160),
              fill=(238, 243, 250), width=4)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(23, 54, 92),
                 outline=(238, 243, 250), width=2)
    ix, iy = x1 - 74, y1 - 22
    draw.ellipse([ix - 34, iy - 7, ix + 34, iy + 7], fill=(203, 182, 122))
    for lean in (-7, 5):
        tx, ty = ix + lean, iy - 2
        draw.line([(tx, ty), (tx + lean, ty - 17)], fill=(120, 88, 50),
                  width=3)
        for ang in (200, 250, 300, 340):
            a = math.radians(ang)
            draw.line([(tx + lean, ty - 17),
                       (tx + lean + 13 * math.cos(a), ty - 17 + 9 * math.sin(a))],
                      fill=(74, 150, 74), width=3)


# --------------------------------------------------------------------------
# Page furniture
# --------------------------------------------------------------------------

def masthead(draw):
    draw.line([(EDGE, 24), (RIGHT, 24)], fill=RULE, width=3)
    draw.line([(EDGE, 31), (RIGHT, 31)], fill=RULE, width=1)
    name = "MAKE IT NEWS"
    f = fit_font(draw, name, RIGHT - EDGE - 30, 100)
    w = draw.textlength(name, font=f)
    draw.text(((PAGE_W - w) / 2, 38), name, font=f, fill=MASTHEAD_RED)
    draw_tracked(draw, PAGE_W / 2, 146,
                 "THE WORLD ON FRIDAY, 20 NOVEMBER 2026",
                 serif(16, bold=True), INK, tracking=2)
    # the red date banner
    top, bottom = 172, 208
    draw.rectangle([EDGE, top, RIGHT, bottom], fill=BANNER_RED)
    f = serif(16, bold=True)
    mid = (top + bottom) / 2 - 10
    draw.text((EDGE + 14, mid), "No. 19,412", font=f, fill=(250, 246, 238))
    centre = "FRIDAY, 20 NOVEMBER 2026"
    cw = draw.textlength(centre, font=f)
    draw.text(((PAGE_W - cw) / 2, mid), centre, font=f, fill=(250, 246, 238))
    right = "PRICE: ONE PENNY"
    draw.text((RIGHT - draw.textlength(right, font=f) - 14, mid),
              right, font=f, fill=(250, 246, 238))
    return bottom


def kicker(draw, cx, y, text):
    draw_tracked(draw, cx, y, text, serif(15, bold=True), MASTHEAD_RED,
                 tracking=1)


def story_block(draw, cx, top, col_w, kick, headline, body, head_size=26,
                body_size=15, body_leading=21):
    """Kicker, headline and body, all centred in a column; returns end y."""
    kicker(draw, cx, top, kick)
    y = centred_lines(draw, cx, top + 20, headline, serif(head_size, bold=True),
                      INK, col_w, int(head_size * 1.16))
    return centred_lines(draw, cx, y + 4, body, serif(body_size), INK, col_w,
                         body_leading)


# --------------------------------------------------------------------------
# The page itself
# --------------------------------------------------------------------------

def build_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)
    y = masthead(draw)

    # ---- lead story ------------------------------------------------------
    lead_top = y + 12                       # y is the banner's bottom edge
    text_cx, text_w = EDGE + 280, 540
    img_box = [610, lead_top - 2, RIGHT, lead_top + 182]
    bridge_scene(draw, img_box)
    cap_y = img_box[3] + 7
    centred_lines(draw, (img_box[0] + img_box[2]) / 2, cap_y,
                  "Three bridges over the Dnipro were damaged in the "
                  "largest attack on the capital's crossings of the war.",
                  serif(13, italic=True), SOFT_INK, img_box[2] - img_box[0] - 8,
                  18)
    kicker(draw, text_cx, lead_top + 2, "UKRAINE WAR \u2022 KYIV")
    hy = centred_lines(draw, text_cx, lead_top + 24,
                       "RUSSIA BATTERS KYIV'S BRIDGES",
                       serif(50, bold=True), INK, text_w, 56)
    centred_lines(draw, text_cx, hy + 6,
                  "Overnight missiles damage three bridges over the Dnipro "
                  "and kill three in the capital \u2014 the largest attack on "
                  "Kyiv's crossings of the war, in answer to Ukraine's "
                  "strikes on the Crimean Bridge.",
                  serif(18, italic=True), INK, 520, 24)
    y = 450
    rule(draw, y)

    # ---- three-column row -------------------------------------------------
    row_top = y + 12
    col_w = 296
    col_x = [EDGE, EDGE + 328, EDGE + 656]
    scenes = [taiex_scene, cop_scene, gold_scene]
    stories = [
        ("MARKETS \u2022 TAIPEI", "TAIWAN STOCKS CRASH IN AI ROUT",
         "Taiex falls 6.2% on Friday, capping a 16% weekly rout \u2014 its "
         "worst week since 1991 \u2014 as Anthropic's record IPO fails to calm "
         "AI fears."),
        ("CLIMATE \u2022 ANTALYA", "COP31 DEADLOCKED ON FINAL DAY",
         "The draft deal drops all mention of fossil fuels and Africa's "
         "$120bn adaptation target as the summit runs into its final hours."),
        ("MARKETS \u2022 GOLD", "GOLD BREAKS BELOW $3,600",
         "Spot gold falls 1.9% to $3,551 an ounce, a 14-month low, as "
         "investors dump bullion to cover losses in AI stocks."),
    ]
    for cx0, scene, (kick, head, body) in zip(col_x, scenes, stories):
        scene(draw, [cx0, row_top, cx0 + col_w, row_top + 104])
        story_block(draw, cx0 + col_w / 2, row_top + 114, col_w,
                    kick, head, body)
    y = 733
    rule(draw, y)

    # ---- bottom row --------------------------------------------------------
    bot_top = y + 12
    half_w = 460
    left_x, right_x = EDGE, EDGE + 492
    galaxy_scene(draw, [left_x, bot_top, left_x + half_w, bot_top + 96])
    story_block(draw, left_x + half_w / 2, bot_top + 106, half_w,
                "TECHNOLOGY \u2022 SEOUL", "SAMSUNG NAMES NEW GALAXY CHIEF",
                "Won-Joon Choi takes over the mobile division from TM Roh "
                "after nearly seven years, in a reshuffle that also promotes "
                "three chip veterans to president.", head_size=28,
                body_leading=20)
    cyclone_scene(draw, [right_x, bot_top, right_x + half_w, bot_top + 96])
    story_block(draw, right_x + half_w / 2, bot_top + 106, half_w,
                "PACIFIC \u2022 COOK ISLANDS",
                "RECORD CYCLONE XAVIER WEAKENS",
                "The strongest November cyclone on record east of the "
                "date line, with peak winds of 220 km/h, eases over "
                "the northern Cooks after damaging homes; gale "
                "warnings remain in force.", head_size=28, body_leading=20)

    # ---- footer -------------------------------------------------------------
    rule(draw, PAGE_H - 22, weight=1)
    centred_lines(draw, PAGE_W / 2, PAGE_H - 16,
                  "Make It News \u2022 All six stories verified from wire "
                  "reports, Friday 20 November 2026",
                  serif(12), SOFT_INK, RIGHT - EDGE, 14)
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    build_page().save(out, format="PNG", optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
