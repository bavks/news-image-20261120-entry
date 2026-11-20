[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/bavks/news-image-20261120-entry/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/bavks/news-image-20261120-entry/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# Make It News — The World on Friday, 20 November 2026 (Picture Edition)

A colour vintage newspaper front page for the make.fun **news-image-20261120**
competition, rebuilt as a picture edition: the same nine verified stories of
Friday 20 November 2026, told with far more artwork and far less wall of text.

## What's on the page

- A large night illustration of Kyiv's bridges over the Dnipro under
  searchlights and fire, leading the paper.
- Spot illustrations woven through the columns: a plunging stock chart for
  the Taiwan AI rout, a pyramid of gold bars as bullion breaks below
  $3,600, a satellite-style spiral for record Cyclone Xavier, and a
  smartphone for Samsung's new Galaxy chief.
- All nine stories with trimmed summaries, an IN BRIEF wire strip
  (Riyadh, Berlin, Washington, Tokyo, New York) and a THE MARKETS ticker
  (Taiex, Kospi, Nikkei 225, gold, silver, Anthropic).

## Files

- `entry.png` — the submitted front page, 1024×1024.
- `render_image.py` — the Pillow renderer that draws the page and every
  illustration from scratch (deterministic, seeded).
- `main.py` — a pure-standard-library entrypoint that hands over the
  committed `entry.png` (copying it to `$MAKEFUN_OUTPUT_DIR` when set);
  it never writes into its own directory, so it runs cleanly in the
  grader's read-only sandbox.

Built for the make.fun news-image-20261120 bounty.
