#!/usr/bin/env python3
"""MAKE IT NEWS - dense broadsheet front page renderer.

Draws a colour vintage newspaper front page (1024x1024) carrying nine
verified news stories plus an IN BRIEF wire column, using Pillow only.
Output is deterministic: same inputs, same bytes.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (243, 234, 211)
PAPER_DARK = (233, 221, 192)
INK = (29, 26, 22)
MUTED = (96, 84, 66)
RED = (140, 30, 30)
BAR_RED = (124, 27, 27)
CREAM = (243, 234, 211)
NAVY = (17, 42, 64)
NAVY_LIGHT = (38, 74, 104)
WATER = (30, 62, 88)
STAR = (240, 236, 220)
FIRE = (232, 138, 30)
FIRE_CORE = (250, 205, 92)
GOLD_LINE = (172, 128, 52)

FONT_DIR_SERIF = "/usr/share/fonts/truetype/liberation"
FONT_DIR_NOTO = "/usr/share/fonts/truetype/noto"


def font(name, size, noto=False):
    base = FONT_DIR_NOTO if noto else FONT_DIR_SERIF
    return ImageFont.truetype(os.path.join(base, name), size)


def serif(size):
    return font("LiberationSerif-Regular.ttf", size)


def serif_bold(size):
    return font("LiberationSerif-Bold.ttf", size)


def serif_italic(size):
    return font("LiberationSerif-Italic.ttf", size)


def sans_bold(size):
    return font("LiberationSans-Bold.ttf", size)


def masthead_font(size):
    return font("NotoSerif-Bold.ttf", size, noto=True)


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_w(draw, trial, fnt) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    return lines


def draw_tracked(draw, cx, y, text, fnt, tracking, fill):
    """Draw letterspaced text centred on cx; returns total width."""
    widths = [text_w(draw, ch, fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += wch + tracking
    return total


def draw_centered(draw, cx, y, text, fnt, fill):
    w = text_w(draw, text, fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def fit_font(draw, text, base_size, max_w, max_lines, bold=False, minimum=9):
    """Largest font size (<= base) whose wrap fits max_lines."""
    size = base_size
    while size > minimum:
        fnt = serif_bold(size) if bold else serif(size)
        if len(wrap(draw, text, fnt, max_w)) <= max_lines:
            return fnt, size
        size -= 1
    fnt = serif_bold(minimum) if bold else serif(minimum)
    return fnt, minimum


# ---------------------------------------------------------------- stories

LEAD = {
    "kicker": "UKRAINE WAR \u2022 KYIV",
    "headline": "RUSSIA BATTERS KYIV\u2019S BRIDGES",
    "standfirst": (
        "Overnight ballistic missiles damage three crossings of the Dnipro, "
        "kill three people and cut the capital in two \u2014 Moscow\u2019s answer "
        "to Ukraine\u2019s strikes on the Crimean Bridge."
    ),
    "body": (
        "Russian ballistic missiles struck three of Kyiv\u2019s bridges over "
        "the Dnipro river in the early hours of Friday, in the largest attack "
        "on the capital\u2019s crossings since the war began. Mayor Vitali "
        "Klitschko said the Podilsko-Voskresenskyi, Darnytskyi and Pivdennyi "
        "bridges were all hit, killing three people and injuring about 15. "
        "Traffic across the river was closed or heavily restricted for the "
        "city\u2019s three million residents, and fires broke out in three "
        "districts as debris fell on buildings. The barrage came a day after "
        "President Vladimir Putin promised harsh retaliation for Ukraine\u2019s "
        "third strike this week on the bridge linking Russia to Crimea. "
        "Russian drones also wounded five people in the Dnipropetrovsk region "
        "and four more at a hospital in Kharkiv."
    ),
    "caption": (
        "Three bridges over the Dnipro were damaged in the largest attack "
        "on the capital\u2019s crossings of the war."
    ),
}

STORIES = [
    {
        "kicker": "MARKETS \u2022 TAIPEI",
        "headline": "TAIWAN STOCKS CRASH IN AI ROUT",
        "body": (
            "Taiwan\u2019s Taiex plunged 6.2 per cent on Friday, capping a "
            "weekly fall of some 17 per cent \u2014 its worst week since 1991 "
            "\u2014 as the global rout in AI shares deepened. TSMC, over 40 "
            "per cent of the index, slid about 5 per cent. Anthropic\u2019s "
            "record debut failed to calm fears, and regulators tightened "
            "short-selling curbs for a second time."
        ),
    },
    {
        "kicker": "CLIMATE \u2022 ANTALYA",
        "headline": "COP31 DEADLOCKED AS FOSSIL FUELS VANISH FROM DRAFT",
        "body": (
            "The UN climate summit in Antalya entered its final day with no "
            "deal in sight after a revised draft dropped every mention of "
            "fossil fuels and the $120 billion-a-year adaptation figure. The "
            "African Group of 54 nations wants adaptation finance tripled by "
            "2035; the EU says pledged money must be delivered first. Talks "
            "are expected to run into the weekend."
        ),
    },
    {
        "kicker": "MARKETS \u2022 BULLION",
        "headline": "GOLD BREAKS BELOW $3,600 IN WORST WEEK SINCE MARCH",
        "body": (
            "Spot gold fell 1.9 per cent to $3,551 an ounce on Friday, its "
            "lowest since September 2025, as bets on further Federal Reserve "
            "rate rises lifted the dollar to a 19-month high. Fed minutes "
            "showed nearly all officials backing more tightening. Investors "
            "also sold bullion to cover losses in AI stocks, dragging silver "
            "below $42."
        ),
    },
    {
        "kicker": "TECHNOLOGY \u2022 SEOUL",
        "headline": "SAMSUNG NAMES NEW GALAXY CHIEF",
        "body": (
            "Samsung Electronics has put Won-Joon Choi in charge of its "
            "mobile division, ending TM Roh\u2019s near seven-year run as "
            "Galaxy chief. Choi, the MX unit\u2019s chief operating officer "
            "since March 2025, led the Galaxy S26 and Z Fold 8 launches. Roh "
            "stays on as co-CEO and head of the wider DX division, while "
            "three chip veterans were promoted to president."
        ),
    },
    {
        "kicker": "PACIFIC \u2022 COOK ISLANDS",
        "headline": "RECORD CYCLONE XAVIER WEAKENS",
        "body": (
            "Cyclone Xavier, the strongest November storm ever recorded east "
            "of the date line, has weakened after peaking at 220 km/h and "
            "damaging homes across the northern Cook Islands. The Category 5 "
            "system cut power and drove hundreds into shelters on Pukapuka. "
            "Now down to Category 4, it tracks west with gale warnings still "
            "in force for the northern group."
        ),
    },
    {
        "kicker": "JUSTICE \u2022 THE HAGUE",
        "headline": "WORLD COURT RULES MYANMAR COMMITTED GENOCIDE",
        "body": (
            "The International Court of Justice has ruled that Myanmar "
            "committed genocide against its Rohingya minority, the first "
            "such finding against a state in the court\u2019s history. Judges "
            "voted nine to six that Myanmar bore state responsibility for "
            "genocide in northern Rakhine state during the 2017 crackdown. "
            "The ruling is binding, though the court has no means to enforce "
            "it."
        ),
    },
    {
        "kicker": "POLITICS \u2022 SHENZHEN",
        "headline": "TRUMP, XI AND PUTIN SIGN PEACE DECLARATION",
        "body": (
            "The presidents of the United States, China and Russia met in "
            "Shenzhen on Thursday for their first-ever three-way summit and "
            "signed a four-point joint declaration. The unprecedented "
            "gathering brought the three rival powers together in the "
            "southern Chinese tech hub, though the declaration\u2019s full "
            "text was not immediately published. Relations remain strained "
            "by war and trade disputes."
        ),
    },
    {
        "kicker": "BUSINESS \u2022 NEW YORK",
        "headline": "ANTHROPIC STUMBLES AFTER RECORD IPO",
        "body": (
            "Shares in Anthropic fell about 6 per cent before Friday\u2019s "
            "open, extending the fade from the largest IPO on record. The "
            "Claude chatbot maker opened 34 per cent above its $83 offer "
            "price on Thursday but closed up 17 per cent at $97.17. The $81 "
            "billion listing was meant to steady the AI trade; instead it "
            "has become its latest casualty."
        ),
    },
]

BRIEFS = [
    ("RIYADH",
     "Houthi missiles damaged the Saudi sovereign wealth fund\u2019s tower "
     "and other buildings in the capital\u2019s financial district."),
    ("BERLIN",
     "Ukraine\u2019s European allies, meeting in Berlin, said Europe is "
     "ready to open talks with Russia on ending the war."),
    ("WASHINGTON",
     "The White House dismissed its national cyber director after a wave "
     "of technology outages hit US systems."),
    ("TOKYO",
     "South Korea\u2019s Kospi and Japan\u2019s Nikkei both fell about 5 "
     "per cent as Asia\u2019s chip sell-off spread."),
    ("NEW YORK",
     "Silver crashed below $42 an ounce as the metals rout wiped roughly "
     "$1 trillion from gold and silver in six hours."),
]

ALSO_TODAY = [
    ("CRIMEA",
     "Ukraine struck the bridge linking Russia to Crimea for the third "
     "time this week, halting rail traffic across the Kerch Strait."),
    ("NAIROBI",
     "Kenya discharged its last Ebola patient, 37 days after the first "
     "case of the outbreak was confirmed."),
    ("WASHINGTON",
     "The Senate rejected an Iran war-powers resolution by 51 votes to "
     "48, a day after the measure passed the House."),
    ("LAS VEGAS",
     "Opening practice for the Las Vegas Grand Prix was washed out, "
     "leaving teams short of running before qualifying."),
]

MARKETS = [
    ("TAIEX", "36,033", "\u22126.2%"),
    ("KOSPI", "4,870", "\u22125.2%"),
    ("NIKKEI 225", "56,437", "\u22125.1%"),
    ("GOLD", "$3,551", "\u22121.9%"),
    ("SILVER", "$41.19", "low"),
    ("ANTHROPIC", "$91.24", "pre-mkt"),
]


# ---------------------------------------------------------------- drawing

def starburst(draw, cx, cy, r_out, r_in, fill):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_lead_image(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY, outline=INK, width=2)
    rng = random.Random(20261120)
    for _ in range(46):
        sx = x + rng.randint(4, w - 4)
        sy = y + rng.randint(4, int(h * 0.52))
        draw.point((sx, sy), fill=STAR)
        if rng.random() < 0.3:
            draw.point((sx + 1, sy), fill=STAR)
    water_y = y + int(h * 0.72)
    draw.rectangle([x, water_y, x + w, y + h], fill=WATER)
    for i in range(9):
        wy = water_y + 5 + i * 3
        draw.line([x + 6, wy, x + w - 6, wy], fill=NAVY_LIGHT, width=1)
    deck_y = y + int(h * 0.62)
    # three bridge spans
    span = w / 3.0
    for i in range(3):
        x0 = x + i * span + 6
        x1 = x + (i + 1) * span - 6
        mid = (x0 + x1) / 2
        draw.line([x0, deck_y, x1, deck_y], fill=CREAM, width=2)
        draw.arc([x0, deck_y - 16, mid, deck_y + 14], 180, 360, fill=CREAM, width=1)
        draw.arc([mid, deck_y - 16, x1, deck_y + 14], 180, 360, fill=CREAM, width=1)
        draw.line([x0, deck_y, x0, water_y + 4], fill=CREAM, width=1)
        draw.line([x1, deck_y, x1, water_y + 4], fill=CREAM, width=1)
    # missile trails and bursts
    draw.line([x + w * 0.30, y + 4, x + w * 0.44, deck_y - 12], fill=CREAM, width=2)
    draw.line([x + w * 0.86, y + 4, x + w * 0.76, deck_y - 12], fill=CREAM, width=2)
    starburst(draw, x + w * 0.44, deck_y - 10, 13, 5, FIRE)
    starburst(draw, x + w * 0.44, deck_y - 10, 6, 2, FIRE_CORE)
    starburst(draw, x + w * 0.76, deck_y - 10, 13, 5, FIRE)
    starburst(draw, x + w * 0.76, deck_y - 10, 6, 2, FIRE_CORE)


def story_block(draw, x, y, w, story, body_size=10, lh=13):
    """Draw one grid story; return height consumed."""
    cy = y
    kf = sans_bold(9)
    draw_tracked(draw, x + w / 2, cy, story["kicker"], kf, 1.2, RED)
    cy += 14
    hf, _ = fit_font(draw, story["headline"], 16, w, 3, bold=True, minimum=12)
    for ln in wrap(draw, story["headline"], hf, w):
        draw_centered(draw, x + w / 2, cy, ln, hf, INK)
        cy += 19
    cy += 2
    bf = serif(body_size)
    lines = wrap(draw, story["body"], bf, w)
    for ln in lines:
        draw.text((x, cy), ln, font=bf, fill=INK)
        cy += lh
    return cy - y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    margin = 30
    right = W - margin

    # ---- masthead
    draw.line([margin, 12, right, 12], fill=INK, width=3)
    draw.line([margin, 18, right, 18], fill=INK, width=1)
    mf = masthead_font(88)
    title = "MAKE IT NEWS"
    while text_w(draw, title, mf) > (W - 2 * margin) and mf.size > 40:
        mf = masthead_font(mf.size - 4)
    draw_centered(draw, W / 2, 22, title, mf, RED)
    sub = "THE WORLD ON FRIDAY, 20 NOVEMBER 2026"
    draw_tracked(draw, W / 2, 118, sub, serif_bold(15), 3.2, INK)
    # red bar
    draw.rectangle([margin, 142, right, 170], fill=BAR_RED)
    bar_f = serif_bold(13)
    draw.text((margin + 10, 149), "No. 19,412", font=bar_f, fill=CREAM)
    draw_centered(draw, W / 2, 149, "FRIDAY, 20 NOVEMBER 2026", bar_f, CREAM)
    rtxt = "PRICE: ONE PENNY"
    draw.text((right - 10 - text_w(draw, rtxt, bar_f), 149), rtxt,
              font=bar_f, fill=CREAM)
    draw.line([margin, 178, right, 178], fill=INK, width=1)

    # ---- lead story
    ly = 186
    draw_tracked(draw, W / 2, ly, LEAD["kicker"], sans_bold(11), 2.0, RED)
    ly += 19
    hf, _ = fit_font(draw, LEAD["headline"], 44, W - 2 * margin, 1,
                     bold=True, minimum=30)
    draw_centered(draw, W / 2, ly, LEAD["headline"], hf, INK)
    ly += 52
    sf = serif_italic(13)
    for ln in wrap(draw, LEAD["standfirst"], sf, W - 2 * margin - 120):
        draw_centered(draw, W / 2, ly, ln, sf, INK)
        ly += 18
    ly += 5
    # body in two columns + illustration at right
    img_w = 336
    img_x = right - img_w
    img_y = ly
    img_h = 118
    draw_lead_image(draw, img_x, img_y, img_w, img_h)
    cap_f = serif_italic(10)
    cap_lines = wrap(draw, LEAD["caption"], cap_f, img_w)
    cy = img_y + img_h + 4
    for ln in cap_lines:
        draw_centered(draw, img_x + img_w / 2, cy, ln, cap_f, MUTED)
        cy += 13
    text_w_avail = img_x - margin - 18
    col_w = (text_w_avail - 16) // 2
    bf = serif(12)
    body_lines = wrap(draw, LEAD["body"], bf, col_w)
    half = (len(body_lines) + 1) // 2
    for ci, chunk in enumerate((body_lines[:half], body_lines[half:])):
        cx = margin + ci * (col_w + 16)
        yy = ly
        for ln in chunk:
            draw.text((cx, yy), ln, font=bf, fill=INK)
            yy += 15
    lead_bottom = max(ly + half * 15, cy)
    gy = lead_bottom + 10
    draw.line([margin, gy, right, gy], fill=INK, width=2)
    gy += 12

    # ---- main grid: 3 story columns + IN BRIEF rail
    gutter = 16
    brief_w = 196
    col_w = (W - 2 * margin - brief_w - 3 * gutter) // 3
    cols_x = [margin + i * (col_w + gutter) for i in range(3)]
    brief_x = cols_x[2] + col_w + gutter
    grid_bottom = 968

    # vertical rules between columns
    for i in range(3):
        vx = cols_x[i] + col_w + gutter // 2
        draw.line([vx, gy + 2, vx, grid_bottom], fill=MUTED, width=1)

    columns = [STORIES[0:3], STORIES[3:6], STORIES[6:8]]
    bottoms = []
    for ci, col_stories in enumerate(columns):
        yy = gy
        for si, story in enumerate(col_stories):
            if si:
                yy += 7
                draw.line([cols_x[ci], yy, cols_x[ci] + col_w, yy],
                          fill=GOLD_LINE, width=1)
                yy += 7
            used = story_block(draw, cols_x[ci], yy, col_w, story)
            yy += used
        bottoms.append(yy)
    print("grid top:", gy, "column bottoms:", bottoms,
          "limit:", grid_bottom)

    # ---- ALSO TODAY filler box in the third column
    ax = cols_x[2]
    ay = bottoms[2] + 14
    draw.line([ax, ay, ax + col_w, ay], fill=INK, width=2)
    draw.line([ax, ay + 3, ax + col_w, ay + 3], fill=INK, width=1)
    ay += 8
    draw_centered(draw, ax + col_w // 2, ay, "ALSO TODAY",
                  serif_bold(13), INK)
    ay += 20
    afl = serif(10)
    afb = serif_bold(10)
    for place, txt in ALSO_TODAY:
        lead = place + " \u2014 "
        lead_w = text_w(draw, lead, afb)
        lines = []
        cur = ""
        maxw = col_w - lead_w
        for wd in txt.split():
            trial = wd if not cur else cur + " " + wd
            if text_w(draw, trial, afl) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
                maxw = col_w
        if cur:
            lines.append(cur)
        draw.text((ax, ay), lead, font=afb, fill=RED)
        draw.text((ax + lead_w, ay), lines[0], font=afl, fill=INK)
        ay += 13
        for ln in lines[1:]:
            draw.text((ax, ay), ln, font=afl, fill=INK)
            ay += 13
        ay += 6
    draw.line([ax, ay, ax + col_w, ay], fill=INK, width=1)
    print("also-today box bottom:", ay + 2)

    # ---- IN BRIEF rail
    bx = brief_x
    by = gy
    draw.rectangle([bx, by, bx + brief_w, by + 24], fill=BAR_RED)
    draw_centered(draw, bx + brief_w // 2, by + 5, "IN BRIEF",
                  serif_bold(13), CREAM)
    by += 32
    bfl = serif(10)
    bfb = serif_bold(10)
    for place, txt in BRIEFS:
        lead = place + " \u2014 "
        lead_w = text_w(draw, lead, bfb)
        # hanging-indent wrap: first line is narrower by the lead-in width
        lines = []
        cur = ""
        maxw = brief_w - lead_w
        for wd in txt.split():
            trial = wd if not cur else cur + " " + wd
            if text_w(draw, trial, bfl) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
                maxw = brief_w
        if cur:
            lines.append(cur)
        draw.text((bx, by), lead, font=bfb, fill=RED)
        draw.text((bx + lead_w, by), lines[0], font=bfl, fill=INK)
        by += 13
        for ln in lines[1:]:
            draw.text((bx, by), ln, font=bfl, fill=INK)
            by += 13
        by += 5
        draw.text((bx + brief_w // 2 - 4, by - 3), "\u2022", font=bfl,
                  fill=MUTED)
        by += 6
    # markets box
    by += 2
    draw.line([bx, by, bx + brief_w, by], fill=INK, width=2)
    by += 5
    draw_centered(draw, bx + brief_w // 2, by, "THE MARKETS",
                  serif_bold(12), INK)
    by += 19
    mfnt = serif(10)
    mfb = serif_bold(10)
    for name, val, chg in MARKETS:
        draw.text((bx, by), name, font=mfb, fill=INK)
        chg_w = text_w(draw, chg, mfnt)
        draw.text((bx + brief_w - chg_w, by), chg, font=mfnt, fill=RED)
        val_w = text_w(draw, val, mfnt)
        draw.text((bx + brief_w - chg_w - val_w - 8, by), val, font=mfnt,
                  fill=INK)
        by += 14
    draw.line([bx, by + 2, bx + brief_w, by + 2], fill=INK, width=1)

    # ---- footer
    draw.line([margin, 976, right, 976], fill=INK, width=2)
    draw.line([margin, 980, right, 980], fill=INK, width=1)
    foot = ("Make It News \u2022 All nine stories and the wire briefs "
            "verified from wire reports \u2022 Friday 20 November 2026")
    draw_centered(draw, W / 2, 988, foot, serif_italic(11), MUTED)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
