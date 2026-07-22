# web-type-system

A [Claude Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) that builds a web/product type system from scratch — optically tuned to a specific typeface and locked to a baseline grid, rather than reached for from generic round-number scales.

Give it a typeface (and optionally a font file or weights), and it computes:

- an optically-anchored base body size (matched to the letterforms, not a round number)
- a base leading and a fixed "repetition unit" (the vertical/baseline grid)
- a full t-shirt scale (`xs`–`lg`) whose line-heights are clean divisors of that unit
- Figma design tokens (DTCG JSON) and a CSS/Tailwind config
- optionally, two visual views built directly in Figma: a type-scale specimen and a repetition-unit diagram

See [`SKILL.md`](./SKILL.md) for the full methodology and workflow.

## Install

This is a Claude Agent Skill, not an npm library — the CLI just copies the skill files into a `.claude/skills` directory where Claude Code or Cowork will discover them.

```bash
# Install into the current project (./.claude/skills/web-type-system)
npx github:Sandrodc/web-type-system

# Install globally, available in every project (~/.claude/skills/web-type-system)
npx github:Sandrodc/web-type-system --global

# Install into a custom parent directory
npx github:Sandrodc/web-type-system --dir /path/to/parent

# Remove it again
npx github:Sandrodc/web-type-system --uninstall
```

No dependencies are installed — the CLI just copies files.

Once installed, ask Claude something like *"set up a type scale for Akkurat"* or *"get typography right for my site"* and it will trigger this skill automatically.

## What gets installed

```
.claude/skills/web-type-system/
├── SKILL.md               # the skill definition Claude reads
├── scripts/
│   └── compute_type_system.py
└── references/
    ├── methodology.md
    ├── output_formats.md
    └── figma_specimen.md
```

The Python script has no hard dependencies beyond the standard library; if [fontTools](https://github.com/fonttools/fonttools) is installed, it can read real metrics directly from a `.ttf`/`.otf` file (`pip install fonttools`).

## License

MIT © Sandro de Calonne
