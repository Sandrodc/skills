# Methodology — the method in depth

This is the reasoning behind `compute_type_system.py`. Read this when you need to explain
*why* a value is what it is, or when a system needs hand-tuning beyond defaults.

Core premise: **typography serves language, not the convenience of a system.**
The web breaks the steady environment of print — text wraps unpredictably and
paragraphs break in odd places — so designers reach for measurable systems (4px
grids, component libraries, uniform ratios) because tools reward tidy numbers.
But legibility rests on the eye: perception, balance, and adjustments a quick
calculation can't capture. The strongest systems are specific and opinionated,
tuned to one typeface and context. The four moves below operationalize that.

## 1. Balancing texture and tone (the optical base size)

Different typefaces render at different apparent sizes at the same point size,
mostly because of **x-height** and **cap-height**, plus counter openness and
glyph intricacy. Set the base size by matching apparent size, not by picking a
round number.

- **Benchmark** against a neutral reference: Inter at 14px/20px (Tailwind's
  default body). This is the "what good, plain body text looks like" control.
- **Direct-translate**: swap in the real typeface at the same 14/20. A font with
  a lower x-height and more intricate forms (like Akkurat) now reads crowded,
  spotty, uneven in color.
- **Optically adjust**: nudge the size up — often just **+1px** — and loosen the
  leading proportionally (14/20 → 15/21). This opens counters and restores an
  even color without the looseness you'd get from adding leading alone or the
  crowding from adding size alone.

The script approximates this by computing the size at which the chosen font's
x-height equals Inter's x-height at 14px: `size = (14 x Inter_xRatio) / font_xRatio`,
rounded. The rounding is the "+1px" instinct. Verify by eye — this is the one
step arithmetic can't finish.

Tradeoffs the article tested and rejected: more line-height alone → loose and
disconnected; smaller size → illegible; larger size without more leading →
denser, worse.

## 2. Vertical rhythm (the repetition unit)

Vertical rhythm is the spacing that carries the eye down the page — how lines and
paragraphs connect in sequence. To make it consistent, define **one fixed
vertical measure** ("repetition unit") that every size relates back to.

- Pick a unit that subdivides cleanly across sizes with no awkward decimals.
- Choose each size's line-height as an integer divisor of the unit. Each size
  then "aligns every N rows": with unit 84, a 42px line aligns every 2 rows, 28px
  every 3, 21px every 4.
- Bigger sizes naturally take proportionally tighter leading (display can even go
  below 1.0), while body sizes stay generous — yet all remain grid-locked.

The script sets `unit = base_leading x rows_per_unit` (default 21 x 4 = 84),
computes an ideal leading per size (`~1.4` for body, easing toward `1.0` for
display), and snaps it to the nearest divisor of the unit.

## 3. Bringing baselines to the web (why alignment "floats")

In print, leading is measured baseline-to-baseline: clean and predictable. On the
web, `line-height` is measured from the font's **bounding box**, which adds space
above ascenders and below descenders. Because most layouts use flex alignment,
things align by that bounding box, not the baseline — so text appears to float
inside its container and baselines between adjacent elements don't line up.
(Even polished sites like Linear show this.) The `text-box-trim` CSS property
would help but isn't widely supported.

The fix is to build around the letterforms rather than wait for CSS: tune
`font-size` and `line-height` per token so the **cap-height and baseline land on
the grid**, while accounting for the extra ascender/descender space. The result
is optical precision using standard CSS. Extend the same baseline line-height
into layout: anchor icons, checkboxes, and dividers to it so components align to
the text grid.

The script reports each token's `cap_height_px` and `x_height_px` to support this
check; final alignment is confirmed visually.

## 4. Naming the tokens (scale, not role)

Semantic names ("heading", "body", "caption") weld a size to a function — large
can only ever be a header, small only ever body. Instead use a Tailwind-style
**t-shirt scale**: `xs, sm, base, md, lg`. These describe visual scale, so a `lg`
token can be a page title or a featured stat, and `sm` a caption or a card
callout. Decoupling scale from function avoids shoehorning and is what makes the
system hold up across responsive breakpoints (same content, different treatment)
and accessibility overrides (assistive tech, user size preferences).

## Worked example — Akkurat, which the generator reproduces

Inputs: Akkurat, x-height ratio ~0.510 (lower than Inter's ~0.546).

- Optical anchor: `(14 x 0.546) / 0.510 = 14.98 -> 15px`. (The 14→15 optical nudge.)
- Base leading: `15 x 1.4 = 21px`. Repetition unit: `21 x 4 = 84px`.
- Scale (size / line-height / aligns):
  - `sm  15 / 21` — every 4 rows (body)
  - `md  23 / 28` — every 3 rows
  - `lg  43 / 42` — every 2 rows (display; leading just under 1.0 by design)

These match the reference figures exactly, which is the check that the method —
not just a lookalike — has been captured.

## When to hand-tune

- **Coarse body divisors.** If several body sizes (13–18px) cluster, the unit's
  divisors may be too widely spaced (e.g. 84 jumps 14 → 21 → 28). Options: reduce
  the number of body tokens, or raise `--rows-per-unit` for a larger unit with
  finer divisors.
- **Very high or low x-height fonts** shift the whole anchor; that's correct, not
  a bug — the grid should differ per typeface.
- **Multiple optical sizes / variable fonts**: consider distinct tokens for
  display vs text cuts; the method is unchanged.
