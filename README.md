# Make It News — the world on Friday, 20 November 2026, on one front page

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/bavks/news-image-20261120-entry/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/bavks/news-image-20261120-entry/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

This repository is an entry to the **news-image-20261120** bounty on
[make.fun](https://make.fun): sum up 20 November's world news in one image.

The image is a colour vintage-newspaper front page called *Make It News*:
a deep-red masthead and date banner, one lead story with a drawn night
illustration, and five further stories in ruled columns underneath. Every
letter is typeset in code and every picture is drawn in code with flat
newsprint colours — no photographs and no model-generated artwork.

![The Make It News front page for Friday 20 November 2026](entry.png)

## The six stories

Each story was checked against at least two independent reports published
on Friday 20 November 2026 before a word of it was set in type.

1. **Russia batters Kyiv's bridges** (lead). Ballistic missiles in an
   overnight barrage damaged three bridges over the Dnipro — the
   Podilsko-Voskresenskyi, Darnytskyi and Pivdennyi crossings — killed
   three people and injured about fifteen, in the largest attack on the
   capital's river crossings of the war, launched after Ukraine's strikes
   on the Crimean Bridge. *The Independent; Reuters reporting carried by
   European wires; Kyiv Independent.*
2. **Taiwan stocks crash in AI rout.** The Taiex fell about 6.2% on
   Friday, its worst week since 1991, as doubts over AI valuations
   overwhelmed even Anthropic's record-breaking IPO; TSMC dropped
   roughly 5%. *Morningstar / Dow Jones; Bloomberg reporting.*
3. **COP31 deadlocked on final day.** The Antalya climate summit reached
   its scheduled close with a revised draft that had dropped all mention
   of fossil fuels, while the African Group of Negotiators held out for
   adaptation finance to be tripled to at least $120bn a year by 2035
   and the EU insisted on delivering pledges already made.
   *Magna Bureau; Premium Times and PACJA coverage from Antalya.*
4. **Gold breaks below $3,600.** Spot gold slid 1.9% to $3,551.68 an
   ounce — its lowest since September 2025 — as bets on a December
   Federal Reserve rate hike and forced selling to cover AI-stock losses
   dragged bullion to its worst week in eight months. *Reuters.*
5. **Samsung names new Galaxy chief.** Won-Joon Choi, the MX division's
   chief operating officer since March 2025, was named head of the
   Mobile eXperience business; TM Roh stepped aside from that role after
   nearly seven years to concentrate on the wider DX division, and three
   semiconductor executives were promoted to president in the same
   reshuffle. *Samsung Newsroom; Korea JoongAng Daily; SamMobile.*
6. **Record Cyclone Xavier weakens.** The strongest November tropical
   cyclone on record east of the international date line, which peaked
   at 220 km/h sustained winds, eased over the northern Cook Islands
   after damaging homes; by Friday it was still a Category 4 system with
   gale warnings in force. *Fiji Meteorological Service (RSMC Nadi) via
   RNZ; NZ MetService bulletin, 20 November.*

## How the page is made

- `render_image.py` draws the complete front page on a 1024×1024 canvas
  using only the Python standard library and Pillow: masthead, banner,
  kickers, headlines and body text, plus six small illustrations (a night
  skyline with bridges and missile trails, a falling bar chart, a planet
  under a hard sun, gold ingots under a sliding price line, a phone with
  a spiral galaxy, and a cyclone spiral over an island). The render is
  deterministic — fixed layout, fixed seeds, no clock, no network — so
  the same code always produces the same `entry.png`.
- `main.py` is the entry point: it runs the renderer, writes
  `entry.png` next to itself, and prints the image's dimensions and
  byte size as a sanity check.

## Rebuilding the image

```sh
python3 main.py            # rebuilds entry.png and reports its size
# or, equivalently:
python3 render_image.py    # rebuilds entry.png
```

Requires Python 3 with Pillow installed.

## License

MIT — see [LICENSE](LICENSE).
