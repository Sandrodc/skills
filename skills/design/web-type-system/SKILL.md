---
name: web-type-system
description: >-
  Build a web/product type system from scratch that is optically tuned to a
  specific typeface and locked to a baseline grid, tuned by eye rather than by a
  generic formula. The user picks the typeface and weights; this skill
  computes the base size, leading, repetition unit, full t-shirt scale, and
  baseline-aligned line-heights, then emits Figma tokens (DTCG) and a CSS/Tailwind
  config. When Figma is a target it also builds two visual views directly in the
  file — a type-scale specimen and a repetition-unit diagram — with a fixed design
  and only the contents driven by the computed system. Use this whenever someone
  wants to set up type scales, a typographic
  system, a type ramp, text tokens, a baseline/vertical rhythm grid, or "get
  typography right" for a website or app — even if they just name a font and ask
  what sizes to use. Prefer this over inventing round-number scales (16/24, 4px
  steps) or semantic size names, which this method deliberately rejects.
---

# Web type system

Build a type system that serves a specific typeface and context, rather than
reaching for generic tokens and round ratios. The guiding idea: **typography
serves language, not the convenience of a system.** Systemized defaults (4px
grids, `text-sm`/`text-lg` off the shelf, uniform 1.5 leading) are easy to
measure but ignore that each typeface renders differently and that CSS aligns
text by its bounding box, not its baseline. This skill encodes four moves that
fix that, and computes concrete values the user can tweak.

The one thing it cannot do is *see* the rendered font. It computes a principled
starting point from font metrics and marks the single step (a ±1px optical
nudge) that still needs the user's eye.

## When to use

Trigger for: setting up a new type scale/ramp, "what sizes should I use for
[font]", building text tokens or type styles, establishing vertical rhythm or a
baseline grid, or porting a brand typeface into a product/site. If the user only
has a font in mind, that is enough to start.

## What you need from the user

1. **Typeface name** (required).
2. **Weights** they'll use (e.g. Regular, Medium, Bold) — pass-through into tokens.
3. **Font metrics** — best accuracy comes from a font file. Ask for one of:
   - a `.ttf`/`.otf` file (the script reads real x-height/cap-height), or
   - raw metrics `unitsPerEm, xHeight, capHeight[, ascender, descender]`, or
   - nothing — the script falls back to a small built-in ratio table by name
     (fine for a first pass; note it's approximate).

Don't over-interview. A font name alone is a valid start.

## Workflow

### Step 1 — Compute the system

Run the script. It prints a table plus ready-to-paste CSS, Tailwind, and Figma
tokens. Add `--out <dir>` to also write files.

```bash
python scripts/compute_type_system.py --name "Akkurat" --weights Regular,Medium,Bold
# with a real font file (most accurate):
python scripts/compute_type_system.py --font ./Akkurat.otf --weights Regular,Bold --out ./tokens
# with manual metrics (font units):
python scripts/compute_type_system.py --metrics 1000,510,700 --name "MyFont"
```

Useful flags: `--body-leading` (base line-height ratio, default 1.40),
`--rows-per-unit` (base rows per repetition unit, default 4), `--steps` (JSON
dict of `token:multiplier` to redefine the scale).

### Step 2 — Explain what it produced (in these terms)

- **Optical body anchor.** The base size is *not* a round number chosen for
  tidiness. It's the size at which this font's x-height visually matches a neutral
  reference (Inter at 14px). A font with a lower x-height than Inter comes out at
  15px+, exactly like Akkurat did — because at 14px it would read crowded and
  spotty. Present this as "we sized to the letterforms, not the number."
- **Repetition unit.** A single fixed vertical measure (e.g. 84px) that every
  line-height divides into cleanly. This is the baseline grid. Each size "aligns
  every N rows" of the unit — that's what keeps rhythm consistent between a
  headline, a paragraph, and a caption.
- **The scale & line-heights.** Line-heights are chosen as clean divisors of the
  unit (84 → 42, 28, 21…), so bigger sizes get proportionally tighter leading and
  everything still locks to the grid. No awkward decimals.
- **T-shirt names, not roles.** Tokens are `xs, sm, base, md, lg` — visual scale,
  not `heading`/`body`. This is deliberate: it lets `lg` be a page title *or* a
  featured stat, and it survives responsive breakpoints and accessibility
  overrides. Never rename these back to semantic roles.

### Step 3 — The by-eye nudge (the part math can't finish)

The script flags this; make sure the user does it:

- Render the **base (sm) row** at 100% zoom in a real paragraph. Check the
  *color* (evenness of grey) and rhythm. If it reads crowded, nudge size +1px and
  loosen leading to the next grid-compatible value; if airy, the reverse. This
  mirrors the "+1px" optical nudge the method relies on.
- Check any row flagged as leading-loose/tight. In-between body sizes can land on
  a coarse divisor; either accept, drop a token, or adjust `--rows-per-unit` so
  the unit has finer divisors.
- Confirm cap-height/baseline alignment visually (see `references/methodology.md`
  on the CSS bounding-box problem — this is why alignment "floats" by default).

### Step 4 — Build the two Figma views (when Figma is a target)

If the user wants the system in Figma (a specimen, styles, or "put it in this
file"), build two visual views directly in the file, driven by the computed
scale. **The design is fixed; only the contents change** — read
`references/figma_specimen.md` and follow it exactly. It covers the required
font-fallback check (the system typeface may not be installed), the fixed
palette and layout constants, and the incremental `use_figma` calls.

- **View 1 — Specimen:** header + one row per token (chip · size/line-height ·
  "aligns every N rows" · a live sample at that setting) + a "how it was built"
  footer.
- **View 2 — Repetition unit:** three columns (a display, a mid, and the body
  size) sharing one dashed repetition-unit boundary with a left px measure,
  baseline hairlines per row, showing each size returning to the grid after a
  whole number of rows.

Always load the `figma-use` skill before calling `use_figma`, build
incrementally, and screenshot to verify. This step is automatic whenever Figma
output is requested — don't make the user ask for the views separately.

### Step 5 — Hand off the tokens

- **Figma:** the DTCG JSON imports via the Tokens Studio plugin as typography
  tokens. Weights map to the user's chosen list (first weight is the default).
- **CSS/Tailwind:** paste the custom properties, or merge the `fontSize` config
  (each entry is a `[size, {lineHeight}]` tuple). The repetition unit is exported
  as a spacing token (`grid-unit`) so layout can share the rhythm — anchor icons,
  checkboxes, and dividers to it, as the article does.

For deeper theory, the exact output schemas, and the worked example that
this generator reproduces, read `references/methodology.md`,
`references/output_formats.md`, and — for the Figma views — `references/figma_specimen.md`.

## Guardrails

- Do not silently "clean up" values into round numbers or a uniform ratio — the
  whole point is a system specific to the typeface.
- Do not reintroduce semantic token names.
- Present computed values as a tunable starting point, never as final truth; the
  eye has the last word.
- If metrics came from the fallback table, say so — it's approximate; a font file
  is better.
