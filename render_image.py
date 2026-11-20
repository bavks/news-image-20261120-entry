#!/usr/bin/env python3
"""Render 'Make It News' — colour vintage newspaper front page.

Summarises the world news of Friday, 20 November 2026 in six verified
stories. Every letter is typeset with PIL and every picture is drawn in
code with flat newsprint colours. Output is fully deterministic: no
randomness, no timestamps, no network access.

Run:  python3 render_image.py        -> writes entry.png next to this file
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
LEFT = MARGIN
RIGHT = W - MARGIN
CW = RIGHT - LEFT  # 952

# ---- palette: warm newsprint paper, deep-red masthead, flat inks ----
PAPER = (247, 241, 227)
INK = (26, 24, 22)
RED = (143, 29, 29)
GOLD = (201, 158, 60)
BLUE = (58, 74, 90)
BLUE_PALE = (207, 224, 234)
BLUE_SEA = (127, 168, 201)
GREEN = (46, 125, 72)
GREY = (120, 116, 108)
RULE = (60, 52, 44)

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
SERIF = str(FONT_DIR / "LiberationSerif-Regular.ttf")
SERIF_BOLD = str(FONT_DIR / "LiberationSerif-Bold.ttf")
SERIF_ITALIC = str(FONT_DIR / "LiberationSerif-Italic.ttf")
SANS = str(FONT_DIR / "LiberationSans-Regular.ttf")
SANS_BOLD = str(FONT_DIR / "LiberationSans-Bold.ttf")


def f(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_h(font, lines, leading):
    """Total height of `lines` lines at `leading` spacing."""
    if not lines:
        return 0
    asc, desc = font.getmetrics()
    return (len(lines) - 1) * leading + asc + desc


def draw_centred(draw, cx, y, text, font, fill, leading=None):
    """Draw possibly multi-line text centred on cx, top at y. Returns bottom."""
    lines = text.split("\n")
    lead = leading or int(font.size * 1.18)
    for i, line in enumerate(lines):
        draw.text((cx, y + i * lead), line, font=font, fill=fill, anchor="ma")
    return y + text_h(font, lines, lead)


def draw_left(draw, x, y, text, font, fill, leading=None):
    lines = text.split("\n")
    lead = leading or int(font.size * 1.18)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lead), line, font=font, fill=fill, anchor="la")
    return y + text_h(font, lines, lead)


def rule(draw, y, weight=2, x0=LEFT, x1=RIGHT):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=weight)


# ----------------------------------------------------------------------
# The six verified stories of Friday, 20 November 2026.
# ----------------------------------------------------------------------
LEAD_HEADLINE = "RUSSIA BATTERS\nKYIV'S BRIDGES"
LEAD_KICKER = "UKRAINE WAR  •  KYIV"
LEAD_STAND = (
    "Overnight missile barrage damages three bridges over the Dnipro and kills "
    "three in the capital — the largest attack on Kyiv's crossings of the war, "
    "in answer to Ukraine's strikes on the Crimean Bridge."
)

STORIES = [
    dict(
        kicker="MARKETS  •  TAIPEI",
        headline="TAIWAN STOCKS CRASH IN AI ROUT",
        sub="Taiex falls 6.2% on Friday, capping a 16% weekly rout — its worst "
            "week since 1991 — as Anthropic's record IPO fails to calm AI fears.",
        art="chart",
    ),
    dict(
        kicker="CLIMATE  •  ANTALYA",
        headline="COP31 DEADLOCKED ON FINAL DAY",
        sub="Draft deal drops all mention of fossil fuels and Africa's $120bn "
            "adaptation target as the summit runs into its final hours.",
        art="globe",
    ),
    dict(
        kicker="MARKETS  •  GOLD",
        headline="GOLD BREAKS BELOW $3,600",
        sub="Spot gold falls 1.9% to $3,551 an ounce, a 14-month low, as "
            "investors dump bullion to cover losses in AI stocks.",
        art="gold",
    ),
    dict(
        kicker="TECHNOLOGY  •  SEOUL",
        headline="SAMSUNG NAMES NEW GALAXY CHIEF",
        sub="Won-Joon Choi takes over the mobile division from TM Roh after "
            "nearly seven years, in a reshuffle that also promotes three chip "
            "veterans to president.",
        art="phone",
    ),
    dict(
        kicker="PACIFIC  •  COOK ISLANDS",
        headline="RECORD CYCLONE XAVIER WEAKENS",
        sub="The strongest November cyclone on record east of the date line, "
            "with peak winds of 220 km/h, eases over the northern Cooks after "
            "damaging homes; gale warnings remain in force.",
        art="cyclone",
    ),
]


# ----------------------------------------------------------------------
# Flat illustrations, drawn in code.
# ----------------------------------------------------------------------
def art_lead(draw, x0, y0, x1, y1):
    """Kyiv at night: the Dnipro, three bridges, missile streaks, bursts."""
    import math

    draw.rectangle([x0, y0, x1, y1], fill=(22, 30, 52))
    # stars
    stars = [(20, 14), (58, 30), (104, 10), (150, 26), (206, 12), (252, 32),
             (300, 14), (330, 30), (40, 48), (180, 44), (286, 52)]
    for sx, sy in stars:
        draw.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                     fill=(255, 255, 255))
    # missile streaks diving toward the river line
    river_y = y0 + (y1 - y0) * 0.66
    for sx, tx in ((x0 + 60, x0 + 130), (x0 + 210, x0 + 258), (x0 + 316, x0 + 290)):
        draw.line([(sx, y0 + 8), (tx, river_y - 26)], fill=(255, 255, 255), width=2)
        draw.polygon([(tx, river_y - 26), (tx - 7, river_y - 38), (tx + 6, river_y - 39)],
                     fill=(232, 126, 32))
    # bursts above two bridges
    for bx, by in ((x0 + 130, river_y - 44), (x0 + 290, river_y - 40)):
        for r, col in ((17, (232, 126, 32)), (10, (255, 226, 120))):
            pts = []
            for k in range(12):
                ang = k * math.pi / 6
                rr = r if k % 2 == 0 else r * 0.55
                pts.append((bx + rr * math.cos(ang), by + rr * math.sin(ang)))
            draw.polygon(pts, fill=col)
    # city silhouette on the far bank
    draw.rectangle([x0, river_y - 22, x1, river_y], fill=(10, 12, 20))
    for bx, bh in ((14, 14), (66, 20), (128, 12), (238, 16), (296, 12)):
        draw.rectangle([x0 + bx, river_y - 22 - bh, x0 + bx + 34, river_y - 22],
                       fill=(10, 12, 20))
    # the river
    draw.rectangle([x0, river_y, x1, y1], fill=(38, 62, 92))
    # three bridges: decks with pylons, drawn over the river
    for bx in (x0 + 62, x0 + 168, x0 + 274):
        deck = river_y + 14
        draw.rectangle([bx - 44, deck, bx + 44, deck + 5], fill=(196, 188, 172))
        draw.rectangle([bx - 3, deck - 30, bx + 3, deck], fill=(196, 188, 172))
        draw.line([(bx, deck - 30), (bx - 44, deck)], fill=(196, 188, 172), width=1)
        draw.line([(bx, deck - 30), (bx + 44, deck)], fill=(196, 188, 172), width=1)
        # reflection
        draw.line([(bx - 30, deck + 14), (bx + 30, deck + 14)],
                  fill=(110, 140, 170), width=2)


def art_chart(draw, x0, y0, x1, y1):
    """A stock chart in freefall: red bars, plunging line, -6.2% tag."""
    draw.rectangle([x0, y0, x1, y1], fill=(238, 234, 226))
    base = y1 - 14
    bars = [(16, 84), (52, 78), (88, 82), (124, 64), (160, 52), (196, 34), (232, 16)]
    for bx, bh in bars:
        draw.rectangle([x0 + bx, base - bh, x0 + bx + 26, base], fill=(120, 116, 108))
    pts = [(x0 + 20, y0 + 18), (x0 + 66, y0 + 24), (x0 + 112, y0 + 20),
           (x0 + 158, y0 + 38), (x0 + 204, y0 + 52), (x0 + 250, y0 + 76)]
    draw.line(pts, fill=RED, width=4, joint="curve")
    hx, hy = pts[-1]
    draw.polygon([(hx, hy), (hx - 15, hy - 3), (hx - 5, hy - 14)], fill=RED)
    draw.text((x0 + 12, y0 + 8), "TAIEX", font=f(SANS_BOLD, 18), fill=INK, anchor="la")
    draw.text((x1 - 12, y0 + 8), "-6.2%", font=f(SANS_BOLD, 22), fill=RED, anchor="ra")


def art_globe(draw, x0, y0, x1, y1):
    """A warming world: globe, hot sun, rising heat waves, conference table."""
    import math

    draw.rectangle([x0, y0, x1, y1], fill=BLUE_PALE)
    cx, cy, r = x0 + 88, y0 + (y1 - y0) // 2, 44
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE_SEA)
    # crude continents
    draw.ellipse([cx - 30, cy - 26, cx - 4, cy - 6], fill=GREEN)
    draw.ellipse([cx + 2, cy + 2, cx + 30, cy + 24], fill=GREEN)
    draw.ellipse([cx - 16, cy + 12, cx + 2, cy + 30], fill=GREEN)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=2)
    # hot sun, top right
    sx, sy = x1 - 44, y0 + 30
    draw.ellipse([sx - 17, sy - 17, sx + 17, sy + 17], fill=(232, 126, 32))
    for k in range(8):
        ang = k * math.pi / 4
        draw.line([(sx + 22 * math.cos(ang), sy + 22 * math.sin(ang)),
                   (sx + 29 * math.cos(ang), sy + 29 * math.sin(ang))],
                  fill=(232, 126, 32), width=3)
    # negotiating table along the bottom
    ty = y1 - 22
    draw.rectangle([x0 + 130, ty, x1 - 14, ty + 8], fill=(110, 74, 40))
    for px in (x0 + 152, x0 + 196, x0 + 240):
        draw.ellipse([px - 5, ty - 12, px + 5, ty - 2], fill=INK)
        draw.rectangle([px - 6, ty - 2, px + 6, ty], fill=INK)


def art_gold(draw, x0, y0, x1, y1):
    """Gold bars on a falling scale: stacked ingots, sinking price arrow."""
    draw.rectangle([x0, y0, x1, y1], fill=(240, 234, 216))
    base = y1 - 16
    # stacked ingots, lower left
    def ingot(ix, iy):
        draw.polygon([(ix, iy), (ix + 14, iy - 10), (ix + 58, iy - 10), (ix + 72, iy)],
                     fill=GOLD, outline=(150, 116, 40))
        draw.rectangle([ix, iy, ix + 72, iy + 9], fill=(178, 138, 50),
                       outline=(150, 116, 40))
    ingot(x0 + 18, base - 9)
    ingot(x0 + 98, base - 9)
    ingot(x0 + 58, base - 27)
    # falling arrow across the top
    pts = [(x0 + 24, y0 + 16), (x0 + 96, y0 + 28), (x0 + 168, y0 + 24),
           (x0 + 240, y0 + 48)]
    draw.line(pts, fill=RED, width=4, joint="curve")
    hx, hy = pts[-1]
    draw.polygon([(hx, hy), (hx - 15, hy - 3), (hx - 5, hy - 14)], fill=RED)
    draw.text((x1 - 12, y1 - 34), "$3,551", font=f(SANS_BOLD, 20), fill=INK, anchor="ra")


def art_phone(draw, x0, y0, x1, y1):
    """A Galaxy handset with a swirling star field and a new-captain star."""
    import math

    draw.rectangle([x0, y0, x1, y1], fill=(24, 26, 44))
    # stars
    stars = [(16, 12), (52, 26), (240, 16), (276, 34), (30, 62), (262, 66),
             (120, 10), (196, 24)]
    for sx, sy in stars:
        draw.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                     fill=(255, 255, 255))
    # handset, centre
    px0, py0, px1, py1 = x0 + 108, y0 + 10, x0 + 188, y1 - 10
    draw.rounded_rectangle([px0, py0, px1, py1], radius=12, fill=(16, 18, 30),
                           outline=(200, 200, 210), width=2)
    draw.rounded_rectangle([px0 + 7, py0 + 12, px1 - 7, py1 - 12], radius=8,
                           fill=(52, 74, 120))
    # galaxy swirl on the screen
    cx, cy = (px0 + px1) // 2, (py0 + py1) // 2
    for rr, col in ((22, (127, 168, 201)), (14, (178, 205, 226)), (6, (255, 255, 255))):
        draw.ellipse([cx - rr, cy - rr * 0.62, cx + rr, cy + rr * 0.62], outline=col, width=2)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))
    # camera dot
    draw.ellipse([cx - 2, py0 + 5, cx + 2, py0 + 9], fill=(200, 200, 210))
    # a bright new-captain star, top left of the phone
    bx, by = x0 + 56, y0 + 34
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = 15 if k % 2 == 0 else 6
        pts.append((bx + rr * math.cos(ang), by + rr * math.sin(ang)))
    draw.polygon(pts, fill=GOLD)


def art_cyclone(draw, x0, y0, x1, y1):
    """Cyclone Xavier from above: spiral bands, calm eye, island below."""
    import math

    draw.rectangle([x0, y0, x1, y1], fill=(30, 62, 96))
    cx, cy = x0 + (x1 - x0) // 2, y0 + (y1 - y0) // 2 - 6
    # spiral arms (radius capped so the spiral stays inside its box:
    # max vertical reach 46 * 0.82 = 38px around cy, box half-height 48)
    for arm in range(3):
        pts = []
        for t in range(41):
            ang = arm * 2.1 + t * 0.16
            rr = 6 + t * 1.0
            pts.append((cx + rr * math.cos(ang), cy + rr * 0.82 * math.sin(ang)))
        draw.line(pts, fill=(235, 240, 245), width=6, joint="curve")
    # eye
    draw.ellipse([cx - 11, cy - 9, cx + 11, cy + 9], fill=(30, 62, 96),
                 outline=(255, 255, 255), width=2)
    # island, bottom right, with two palms
    ix, iy = x1 - 74, y1 - 18
    draw.ellipse([ix - 34, iy - 7, ix + 40, iy + 9], fill=(214, 192, 130))
    for px in (ix - 8, ix + 16):
        draw.line([(px, iy - 2), (px, iy - 20)], fill=(90, 64, 32), width=3)
        for ang in (-50, -20, 10, 40):
            a = math.radians(ang)
            draw.line([(px, iy - 20), (px + 13 * math.cos(a), iy - 20 - 6 + 7 * math.sin(a))],
                      fill=GREEN, width=2)
    draw.text((x0 + 12, y0 + 8), "XAVIER", font=f(SANS_BOLD, 18),
              fill=(255, 255, 255), anchor="la")


ART = {
    "chart": art_chart,
    "globe": art_globe,
    "gold": art_gold,
    "phone": art_phone,
    "cyclone": art_cyclone,
}


# ----------------------------------------------------------------------
# Page build.
# ----------------------------------------------------------------------
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top double rule ---------------------------------------------
    rule(d, 24, 2)
    rule(d, 29, 1)

    # --- masthead ------------------------------------------------------
    y = 36
    y = draw_centred(d, W // 2, y, "MAKE IT NEWS",
                     f(SERIF_BOLD, 92), RED) + 2
    y = draw_centred(d, W // 2, y, "THE WORLD ON FRIDAY, 20 NOVEMBER 2026",
                     f(SANS_BOLD, 14), INK) + 8

    # --- red dateline band ---------------------------------------------
    d.rectangle([LEFT, y, RIGHT, y + 34], fill=RED)
    d.text((LEFT + 12, y + 17), "No. 19,412", font=f(SANS_BOLD, 13),
           fill=(255, 255, 255), anchor="lm")
    d.text((RIGHT - 12, y + 17), "PRICE: ONE PENNY", font=f(SANS_BOLD, 13),
           fill=(255, 255, 255), anchor="rm")
    d.text((W // 2, y + 17), "FRIDAY, 20 NOVEMBER 2026",
           font=f(SERIF_BOLD, 21), fill=(255, 255, 255), anchor="mm")
    y += 34 + 12

    # --- lead story: headline left, picture right ----------------------
    lead_w = 560
    lead_x1 = LEFT + lead_w
    pic_x0, pic_x1 = lead_x1 + 16, RIGHT
    pic_y0 = y
    y = draw_centred(d, LEFT + lead_w // 2, y, LEAD_KICKER,
                     f(SANS_BOLD, 14), RED) + 6
    y = draw_centred(d, LEFT + lead_w // 2, y, LEAD_HEADLINE,
                     f(SERIF_BOLD, 46), INK, leading=50) + 8
    stand_lines = wrap(d, LEAD_STAND, f(SERIF_ITALIC, 18), lead_w)
    y = draw_centred(d, LEFT + lead_w // 2, y, "\n".join(stand_lines),
                     f(SERIF_ITALIC, 18), INK, leading=23) + 4
    lead_bottom = y
    pic_y1 = pic_y0 + 196
    art_lead(d, pic_x0, pic_y0, pic_x1, pic_y1)
    d.rectangle([pic_x0, pic_y0, pic_x1, pic_y1], outline=INK, width=1)
    cap_lines = wrap(d, "Three bridges over the Dnipro were damaged in the "
                        "largest attack on the capital's crossings of the war.",
                     f(SERIF_ITALIC, 13), pic_x1 - pic_x0)
    cap_y = draw_centred(d, pic_x0 + (pic_x1 - pic_x0) // 2, pic_y1 + 6,
                         "\n".join(cap_lines), f(SERIF_ITALIC, 13), GREY,
                         leading=16)
    y = max(lead_bottom, cap_y + 6)
    rule(d, y, 2)
    y += 12

    # --- three-column row: stories 1-3 ---------------------------------
    gap = 16
    col_w = (CW - 2 * gap) // 3
    row_y = y
    row_bottom = row_y
    for i, st in enumerate(STORIES[:3]):
        x0 = LEFT + i * (col_w + gap)
        x1 = x0 + col_w
        cy = row_y
        ART[st["art"]](d, x0, cy, x1, cy + 104)
        d.rectangle([x0, cy, x1, cy + 104], outline=INK, width=1)
        cy += 104 + 8
        cy = draw_left(d, x0, cy, st["kicker"], f(SANS_BOLD, 12), RED) + 4
        hl = wrap(d, st["headline"], f(SERIF_BOLD, 24), col_w)
        cy = draw_left(d, x0, cy, "\n".join(hl), f(SERIF_BOLD, 24), INK,
                       leading=27) + 5
        sub = wrap(d, st["sub"], f(SERIF, 15), col_w)
        cy = draw_left(d, x0, cy, "\n".join(sub), f(SERIF, 15), INK,
                       leading=19) + 4
        row_bottom = max(row_bottom, cy)
    y = row_bottom + 6
    rule(d, y, 2)
    y += 12

    # --- two-column row: stories 4-5 -----------------------------------
    col2_w = (CW - gap) // 2
    row_y = y
    row_bottom = row_y
    for i, st in enumerate(STORIES[3:]):
        x0 = LEFT + i * (col2_w + gap)
        x1 = x0 + col2_w
        cy = row_y
        ART[st["art"]](d, x0, cy, x1, cy + 96)
        d.rectangle([x0, cy, x1, cy + 96], outline=INK, width=1)
        cy += 96 + 8
        cy = draw_left(d, x0, cy, st["kicker"], f(SANS_BOLD, 12), RED) + 4
        hl = wrap(d, st["headline"], f(SERIF_BOLD, 26), col2_w)
        cy = draw_left(d, x0, cy, "\n".join(hl), f(SERIF_BOLD, 26), INK,
                       leading=30) + 5
        sub = wrap(d, st["sub"], f(SERIF, 16), col2_w)
        cy = draw_left(d, x0, cy, "\n".join(sub), f(SERIF, 16), INK,
                       leading=20) + 4
        row_bottom = max(row_bottom, cy)
    y = row_bottom + 8

    # --- footer ----------------------------------------------------------
    rule(d, y, 1)
    y += 8
    draw_centred(
        d, W // 2, y,
        "Make It News  •  All six stories verified from wire reports, Friday 20 November 2026",
        f(SANS, 13), GREY)
    return img


def main():
    out = Path(__file__).resolve().parent / "entry.png"
    img = build()
    img.save(out, format="PNG")
    print(f"wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
