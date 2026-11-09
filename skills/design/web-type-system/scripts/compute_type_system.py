#!/usr/bin/env python3
"""
compute_type_system.py — derive an optically-anchored, baseline-locked web type system.

Given a chosen typeface (its metrics) and weights, this computes:
  1. An optically-anchored base body size  (match apparent size to a neutral reference)
  2. A base leading and a fixed "repetition unit" (the vertical grid measure)
  3. A t-shirt scale (xs..lg) whose line-heights are clean divisors of the unit
     (so every size locks to the baseline grid — "aligns every N rows")
  4. Baseline diagnostics (cap-height / baseline position inside each line box)

It then emits three artefacts:
  - a human-readable table
  - Figma design tokens (DTCG JSON, importable via Tokens Studio)
  - CSS custom properties + a Tailwind fontSize config

Everything is a *starting point* meant to be tweaked. The one step this cannot do
for you is the final by-eye nudge (±1px) — the script flags where to look.

Metrics can come from:
  --font path/to/Font.ttf         (extracted via fontTools if installed)
  --metrics upm,xHeight,capHeight,ascender,descender   (raw font units)
  (nothing)                        -> uses a small built-in table by --name

Usage examples:
  python compute_type_system.py --name "Akkurat" --weights Regular,Medium,Bold
  python compute_type_system.py --font ./Akkurat.otf --weights Regular,Bold
  python compute_type_system.py --metrics 1000,510,700,750,-250 --name "MyFont"
"""

import argparse
import json
import sys

# ---- Reference: Inter at 14px is the neutral benchmark the article starts from.
# Inter, unitsPerEm 2048: xHeight 1118, capHeight 1490.
REF = {"name": "Inter", "x_ratio": 1118 / 2048, "cap_ratio": 1490 / 2048, "base_px": 14}

# ---- Small fallback table of x-height / cap-height ratios (xHeight/upm, capHeight/upm).
# Rough, good enough to bootstrap; prefer --font or --metrics for accuracy.
KNOWN = {
    "akkurat":   {"x_ratio": 0.510, "cap_ratio": 0.700},
    "inter":     {"x_ratio": 0.546, "cap_ratio": 0.727},
    "helvetica": {"x_ratio": 0.523, "cap_ratio": 0.717},
    "arial":     {"x_ratio": 0.519, "cap_ratio": 0.716},
    "roboto":    {"x_ratio": 0.528, "cap_ratio": 0.711},
    "georgia":   {"x_ratio": 0.481, "cap_ratio": 0.692},
    "times":     {"x_ratio": 0.448, "cap_ratio": 0.662},
}

# Default t-shirt multipliers relative to the optically-derived body anchor.
# Order matches the article: xs < sm < base < md < lg. Tweak freely.
DEFAULT_STEPS = {"xs": 0.85, "sm": 1.00, "base": 1.20, "md": 1.55, "lg": 2.85}


def divisors(n):
    return sorted([d for d in range(1, n + 1) if n % d == 0], reverse=True)


def target_leading_ratio(size, anchor):
    """Body text wants generous leading; display tightens. Linear falloff, clamped."""
    return max(1.0, 1.40 - 0.008 * (size - anchor))


def nearest_divisor(value, divs):
    return min(divs, key=lambda d: abs(d - value))


def metrics_from_font(path):
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        sys.exit("fontTools not installed. Run: pip install fonttools --break-system-packages")
    f = TTFont(path)
    upm = f["head"].unitsPerEm
    os2 = f["OS/2"]
    x = getattr(os2, "sxHeight", 0) or 0
    cap = getattr(os2, "sCapHeight", 0) or 0
    asc = f["hhea"].ascent
    desc = f["hhea"].descent
    if not x or not cap:
        sys.exit("Font lacks sxHeight/sCapHeight in OS/2. Pass --metrics manually.")
    return {"x_ratio": x / upm, "cap_ratio": cap / upm,
            "asc_ratio": asc / upm, "desc_ratio": desc / upm}


def resolve_metrics(args):
    if args.font:
        return metrics_from_font(args.font)
    if args.metrics:
        parts = [float(p) for p in args.metrics.split(",")]
        upm, x, cap = parts[0], parts[1], parts[2]
        asc = parts[3] if len(parts) > 3 else 0.75 * upm
        desc = parts[4] if len(parts) > 4 else -0.25 * upm
        return {"x_ratio": x / upm, "cap_ratio": cap / upm,
                "asc_ratio": asc / upm, "desc_ratio": desc / upm}
    key = (args.name or "").strip().lower()
    for k in KNOWN:
        if k in key:
            m = dict(KNOWN[k])
            m.setdefault("asc_ratio", 0.75)
            m.setdefault("desc_ratio", -0.25)
            return m
    sys.exit(f"No metrics for '{args.name}'. Pass --font or --metrics "
             f"(upm,xHeight,capHeight[,ascender,descender]).")


def compute(args):
    m = resolve_metrics(args)

    # 1. Optical base: the size at which this font's x-height matches Inter@14.
    target_x_px = REF["base_px"] * REF["x_ratio"]
    ideal_base = target_x_px / m["x_ratio"]
    anchor = round(ideal_base)

    # 2. Base leading + repetition unit.
    base_leading = round(anchor * args.body_leading)   # ~1.4 by default
    unit = base_leading * args.rows_per_unit            # fixed vertical measure
    divs = divisors(unit)

    # 3. Build the scale.
    steps = DEFAULT_STEPS if not args.steps else json.loads(args.steps)
    rows_out = []
    for token, mult in steps.items():
        size = round(anchor * mult)
        ideal_lh = size * target_leading_ratio(size, anchor)
        lh = nearest_divisor(ideal_lh, divs)
        rows_out.append({
            "token": token,
            "size": size,
            "line_height": lh,
            "aligns_every_rows": unit // lh,
            "lh_ratio": round(lh / size, 3),
            "cap_height_px": round(size * m["cap_ratio"], 2),
            "x_height_px": round(size * m["x_ratio"], 2),
        })
    return {"anchor": anchor, "base_leading": base_leading, "unit": unit,
            "metrics": m, "rows": rows_out}


# --------------------------- output renderers ---------------------------

def render_table(r, name, weights):
    out = []
    out.append(f"Font: {name}   Weights: {', '.join(weights)}")
    out.append(f"Optical body anchor: {r['anchor']}px  "
               f"(matches Inter@{REF['base_px']} apparent x-height)")
    out.append(f"Base leading: {r['base_leading']}px   "
               f"Repetition unit: {r['unit']}px "
               f"({r['unit']}/{r['base_leading']} = {r['unit']//r['base_leading']} base rows)")
    out.append("")
    out.append(f"{'token':<6}{'size':>6}{'  lh':>6}{'  ratio':>8}"
               f"{'  aligns':>10}{'  cap':>7}{'  x-ht':>7}")
    out.append("-" * 52)
    for row in r["rows"]:
        note = ""
        is_display = row["size"] > 2 * r["anchor"]
        if not is_display and row["lh_ratio"] > 1.5:
            note = "  <- leading loose, consider nudging size/unit"
        elif not is_display and row["lh_ratio"] < 1.1:
            note = "  <- leading tight, consider nudging size/unit"
        out.append(f"{row['token']:<6}{row['size']:>5}px{row['line_height']:>5}px"
                   f"{row['lh_ratio']:>8}{'every '+str(row['aligns_every_rows'])+'':>10}"
                   f"{row['cap_height_px']:>6}{row['x_height_px']:>7}{note}")
    out.append("")
    out.append("Note: sizes >2x the body anchor are display type; leading <=1.0 is intentional.")
    out.append("The base row (sm) is your body text; verify its color/rhythm by eye at 100% zoom.")
    return "\n".join(out)


def render_css(r, name, weights):
    lines = [":root {",
             f"  /* {name} — grid unit {r['unit']}px */",
             f"  --type-repetition-unit: {r['unit']}px;",
             f"  --font-family: \"{name}\", sans-serif;"]
    for row in r["rows"]:
        t = row["token"]
        lines.append(f"  --text-{t}: {row['size']}px;")
        lines.append(f"  --leading-{t}: {row['line_height']}px;")
    lines.append("}")
    lines.append("")
    lines.append("/* usage: font-size: var(--text-sm); line-height: var(--leading-sm); */")
    return "\n".join(lines)


def render_tailwind(r, name):
    fs = {}
    for row in r["rows"]:
        fs[row["token"]] = [f"{row['size']}px", {"lineHeight": f"{row['line_height']}px"}]
    cfg = {
        "theme": {
            "extend": {
                "fontFamily": {"sans": [name, "sans-serif"]},
                "fontSize": fs,
                "spacing": {"grid-unit": f"{r['unit']}px"},
            }
        }
    }
    return "/** tailwind.config — merge into your config */\n" + \
           "module.exports = " + json.dumps(cfg, indent=2) + ";"


def render_figma_tokens(r, name, weights):
    """DTCG-style tokens (importable via Tokens Studio for Figma)."""
    primary_weight = weights[0] if weights else "Regular"
    typo = {}
    for row in r["rows"]:
        typo[row["token"]] = {
            "$type": "typography",
            "$value": {
                "fontFamily": name,
                "fontWeight": primary_weight,
                "fontSize": f"{row['size']}px",
                "lineHeight": f"{row['line_height']}px",
                "letterSpacing": "0",
            },
            "$description": f"aligns every {row['aligns_every_rows']} rows on the "
                            f"{r['unit']}px grid",
        }
    tokens = {
        "type": typo,
        "grid": {
            "repetitionUnit": {"$type": "dimension", "$value": f"{r['unit']}px"},
            "baseLeading": {"$type": "dimension", "$value": f"{r['base_leading']}px"},
        },
    }
    return json.dumps(tokens, indent=2)


def main():
    p = argparse.ArgumentParser(description="Compute an optically-anchored web type system.")
    p.add_argument("--name", default="", help="typeface name (also used for fallback metrics)")
    p.add_argument("--weights", default="Regular", help="comma list, e.g. Regular,Medium,Bold")
    p.add_argument("--font", help="path to .ttf/.otf to read real metrics")
    p.add_argument("--metrics", help="upm,xHeight,capHeight[,ascender,descender] in font units")
    p.add_argument("--body-leading", type=float, default=1.40, help="base line-height ratio")
    p.add_argument("--rows-per-unit", type=int, default=4, help="base rows per repetition unit")
    p.add_argument("--steps", help="JSON dict of token:multiplier to override defaults")
    p.add_argument("--out", default="", help="directory to also write css/tailwind/figma files")
    args = p.parse_args()

    weights = [w.strip() for w in args.weights.split(",") if w.strip()]
    name = args.name or (args.font.split("/")[-1].rsplit(".", 1)[0] if args.font else "Custom")

    r = compute(args)
    print(render_table(r, name, weights))
    print("\n--- CSS ---\n")
    print(render_css(r, name, weights))
    print("\n--- Tailwind ---\n")
    print(render_tailwind(r, name))
    print("\n--- Figma tokens (DTCG) ---\n")
    print(render_figma_tokens(r, name, weights))

    if args.out:
        import os
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "type.css"), "w") as f:
            f.write(render_css(r, name, weights) + "\n")
        with open(os.path.join(args.out, "tailwind.type.js"), "w") as f:
            f.write(render_tailwind(r, name) + "\n")
        with open(os.path.join(args.out, "figma.tokens.json"), "w") as f:
            f.write(render_figma_tokens(r, name, weights) + "\n")
        print(f"\nWrote type.css, tailwind.type.js, figma.tokens.json -> {args.out}")


if __name__ == "__main__":
    main()
