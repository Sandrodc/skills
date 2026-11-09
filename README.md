# claude-skills

My [Claude Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills), grouped by what they're for. Each skill is a folder with a `SKILL.md` that Claude Code, Cowork or claude.ai reads and triggers on its own when a request matches.

## Skills

### Design

| Skill | What it does |
| --- | --- |
| [`web-type-system`](skills/design/web-type-system/SKILL.md) | Builds a web/product type system optically tuned to a specific typeface and locked to a baseline grid. Computes base size, leading, repetition unit and a t-shirt scale, then emits Figma tokens (DTCG), CSS and Tailwind config. It can also build a type specimen and a repetition-unit diagram in Figma. |

### Build in public

Three skills that cover a build-in-public post on X end to end: find the moment, make the visual, write the caption.

| Skill | What it does |
| --- | --- |
| [`build-in-public-ideas`](skills/build-in-public/build-in-public-ideas/SKILL.md) | Scans a project and proposes ranked post ideas, each with a format and the asset to make. |
| [`build-in-public-media`](skills/build-in-public/build-in-public-media/SKILL.md) | Produces the video or image: isolate a component, frame a screen recording on a background, punch-in zooms, export settings. |
| [`build-in-public-captions`](skills/build-in-public/build-in-public-captions/SKILL.md) | Writes the short, understated caption that goes with it. |

### Product

| Skill | What it does |
| --- | --- |
| [`product-thinking`](skills/product/product-thinking/SKILL.md) | Grills a product, startup, side-project or feature idea one sharp question at a time, drawing on how 12 top builders think, then gives a verdict and a validation plan. |

## Install

### Claude Code plugin marketplace

Each group above is also a plugin, so you can add the whole repo as a marketplace and install groups:

```
/plugin marketplace add Sandrodc/claude-skills
/plugin install build-in-public@sandrodc-skills
/plugin install design@sandrodc-skills
/plugin install product@sandrodc-skills
```

### npx

The CLI copies skills into a `.claude/skills` directory. It installs nothing else and has no dependencies.

```bash
# See what's available
npx github:Sandrodc/claude-skills --list

# One skill, into the current project (./.claude/skills/<skill>)
npx github:Sandrodc/claude-skills web-type-system

# A whole group
npx github:Sandrodc/claude-skills build-in-public

# Everything, globally (~/.claude/skills), available in every project
npx github:Sandrodc/claude-skills --all --global

# A custom parent directory
npx github:Sandrodc/claude-skills product-thinking --dir /path/to/skills

# Remove again
npx github:Sandrodc/claude-skills build-in-public --uninstall
```

### claude.ai

Zip a skill folder (for example `skills/product/product-thinking`) and upload it under Settings → Capabilities → Skills.

## Layout

```
skills/
├── design/
│   └── web-type-system/
│       ├── SKILL.md
│       ├── scripts/compute_type_system.py
│       └── references/
├── build-in-public/
│   ├── build-in-public-ideas/SKILL.md
│   ├── build-in-public-media/SKILL.md
│   └── build-in-public-captions/SKILL.md
└── product/
    └── product-thinking/SKILL.md
```

Groups are only for organising the repo. Installed skills land flat, as `.claude/skills/<skill>/`, which is where Claude looks for them.

To add a skill, drop its folder into a group under `skills/` (or make a new group). The npx installer finds it automatically. Add its path to [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) so the plugin install picks it up too.

### Notes on `web-type-system`

The Python script needs only the standard library. If [fontTools](https://github.com/fonttools/fonttools) is installed (`pip install fonttools`), it reads real metrics straight from a `.ttf`/`.otf` file.

## License

MIT © Sandro de Calonne
