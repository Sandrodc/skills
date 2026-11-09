# Output formats

The script emits three artefacts. All are starting points; edit freely.

## Figma tokens (DTCG / Tokens Studio)

Shape:

```json
{
  "type": {
    "sm": {
      "$type": "typography",
      "$value": {
        "fontFamily": "Akkurat",
        "fontWeight": "Regular",
        "fontSize": "15px",
        "lineHeight": "21px",
        "letterSpacing": "0"
      },
      "$description": "aligns every 4 rows on the 84px grid"
    }
  },
  "grid": {
    "repetitionUnit": { "$type": "dimension", "$value": "84px" },
    "baseLeading":    { "$type": "dimension", "$value": "21px" }
  }
}
```

To use in Figma: install the **Tokens Studio** plugin, create/select a token
set, and import this JSON. The `type.*` tokens become typography styles you can
apply to text layers; `grid.*` are dimension tokens for spacing/layout. Only the
first weight is set as default — duplicate a token and change `fontWeight` for
additional weights (e.g. a `md.strong` at Medium).

Native Figma text styles (not via plugin) don't import JSON directly; either use
Tokens Studio, or create the styles by hand from the printed table.

## CSS custom properties

```css
:root {
  --type-repetition-unit: 84px;
  --font-family: "Akkurat", sans-serif;
  --text-sm: 15px;
  --leading-sm: 21px;
  /* ... */
}
```

Apply as `font-size: var(--text-sm); line-height: var(--leading-sm);`. Keep the
size and its leading paired — they were tuned together for grid alignment, so
mixing a size with a different token's leading breaks the rhythm.

## Tailwind config

```js
module.exports = {
  theme: {
    extend: {
      fontFamily: { sans: ["Akkurat", "sans-serif"] },
      fontSize: {
        sm: ["15px", { lineHeight: "21px" }],
        md: ["23px", { lineHeight: "28px" }]
        // ...
      },
      spacing: { "grid-unit": "84px" }
    }
  }
}
```

Each `fontSize` entry is a `[size, { lineHeight }]` tuple, so `text-sm` sets both
size and its paired leading in one class. `spacing.grid-unit` exposes the
repetition unit for layout (`gap-grid-unit`, `py-grid-unit`, etc.) so components
share the text rhythm. Note this replaces Tailwind's default `fontSize` keys —
that's intended; the point is a bespoke scale, not the stock one.

## Keeping the two in sync

Figma tokens and the CSS/Tailwind values come from the same computation, so they
match at generation time. If the user hand-tunes one (e.g. the by-eye +1px nudge
on the body row), apply the same change to the other, or re-run the script with
adjusted flags and re-export both.
