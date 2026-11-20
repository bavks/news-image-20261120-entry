[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/bavks/news-image-20261120-entry/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/bavks/news-image-20261120-entry/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# Make It News — The World on Friday, 20 November 2026

A dense, colour, vintage-style broadsheet front page that sums up one day of
world news in a single 1024×1024 image. This repository is an entry for the
[make.fun](https://make.fun) bounty
[news-image-20261120](https://make.fun/bounty/news-image-20261120)
("Sum up 20 November's world news in one image").

## What's on the page

Nine verified stories from Friday 20 November 2026, researched from wire
reporting and cross-checked against second sources:

1. **Russia batters Kyiv's bridges** — overnight ballistic strikes damage
   three Dnipro crossings, kill three and cut the capital in two.
2. **Taiwan stocks crash in AI rout** — the Taiex falls 6.2% for its worst
   week since 1991 as TSMC slides.
3. **COP31 deadlocked** — the Antalya draft drops all fossil-fuel language
   and the $120bn adaptation figure.
4. **Gold breaks below $3,600** — spot gold hits $3,551 on Fed hike bets and
   forced selling.
5. **Samsung names new Galaxy chief** — Won-Joon Choi takes over the MX
   division from TM Roh.
6. **Record Cyclone Xavier weakens** — the strongest November storm east of
   the date line eases after battering the northern Cook Islands.
7. **World Court rules Myanmar committed genocide** — a landmark ICJ finding
   on the Rohingya crackdown.
8. **Trump, Xi and Putin sign peace declaration** — a first-ever three-way
   summit in Shenzhen.
9. **Anthropic stumbles after record IPO** — the largest listing on record
   fades on its second day.

Plus an **IN BRIEF** wire column (Riyadh, Berlin, Washington, Tokyo,
New York), a market-data box, and an **ALSO TODAY** panel.

## How it is built

- `render_image.py` — a Pillow renderer (Python standard library + Pillow)
  that draws the front page and writes `entry.png`. Its output is
  deterministic: same code, same bytes.
- `entry.png` — the finished front page, 1024×1024.
- `main.py` — a pure standard-library entry point. It locates the committed
  `entry.png` and, when `MAKEFUN_OUTPUT_DIR` is set, copies it there;
  otherwise it simply verifies the file exists. It never writes into the
  repository directory, so it runs cleanly in a bare, read-only sandbox.

## Running it

```sh
python3 render_image.py   # regenerate entry.png
python3 main.py           # verify / deliver entry.png
```

Built for the make.fun news-image-20261120 competition on make.fun.
Referral: [make.fun](https://make.fun) — join via the bounty page above.
