---
name: "build-in-public-ideas"
description: "Scan a project Sandro is building and propose ranked build-in-public post ideas for X, each with a format and asset to make. Use for 'what can I post about this', 'post ideas', 'build in public'."
---

# Build-in-public post ideas

The reference posts this skill is tuned to (Robert van Klinken's chat cards and "Little details", Emil Kowalski's animated icons, the ElevenReader ship post) share one thing: each post shows exactly one visible thing, polished, with almost no words. Your job is to find those moments in a project, not to summarise the project.

## Step 1 — Gather evidence before asking anything

Run these first, in the project root:

- `git log --since="14 days ago" --stat --oneline` — what changed recently. Recent work is what Sandro can still talk about with energy.
- List UI files touched in that window (SwiftUI views, components, CSS/TSX). UI changes are the raw material; backend-only commits rarely make a post.
- Look for existing media in the repo or Desktop (`*.mov`, `*.mp4`, `*.png` from CleanShot). Existing footage cuts production time to minutes.
- Read the README / any roadmap or TODO for what is about to ship.

Ask Sandro a question only if the scan finds fewer than 3 visible changes.

## Step 2 — Turn each change into a candidate by walking this tree

```
Is the change visible on screen?
├── No → Does it carry a surprising number, decision or lesson?
│        ├── Yes → PROCESS post (text + one supporting image: diagram, terminal, before/after metric)
│        └── No  → drop it
└── Yes
    ├── Does it move? (animation, transition, hover, state change)
    │   └── Yes → DETAIL clip (video, punch-in on the moment)
    ├── Is it one component with several states/variants?
    │   └── Yes → COMPONENT set (isolated component cycling through states)
    ├── Is it a whole screen or flow that changed and is shipping?
    │   └── Yes → SHIP post (device frame, cropped to the changed area)
    └── Otherwise → STILL (one framed image)
```

Why a tree: the format decides how much work the asset takes and how it reads in a 2-second scroll. Picking format by mood produces a different answer every run.

## Step 3 — Filter strictly

Drop a candidate if any is true:

- It needs more than one sentence of context to understand. The timeline gives ~2 seconds; if the viewer needs a setup, it fails.
- It shows more than one idea. Split it into two posts instead.
- It is client work from Yummygum or any client, unless Sandro confirms in this conversation that it is public and approved. NDAs outrank engagement.
- It shows a feature as finished when it isn't. Label WIP honestly ("wip" is fine — the references do it).
- It is generic (a login screen, a settings list) with no detail that is specific to this project.

## Step 4 — Rank

Score each survivor 0–2 on three axes and sort by total:

1. **Readable in 2s** — 2 = obvious at phone size without sound or caption.
2. **Craft signal** — 2 = a detail a designer would save or repost (easing, micro-interaction, typography, a clever state). Craft is what Sandro is building a reputation on; feature lists aren't.
3. **Cheap to produce** — 2 = asset doable in under 30 min (existing footage, or a component that can be isolated).

## Step 5 — Output

Return at most 5 ideas, as a table:

| # | Moment | Format | Why it's interesting (1 line) | Asset to make | Draft caption |

- "Asset to make" is concrete: which view/component, which states, which canvas (see build-in-public-media).
- Draft caption follows build-in-public-captions.
- End with one line: **Post first:** #N, and why (highest score, or cheapest if tied).
- If a project yields 3+ ideas, suggest an order spread over 1–2 weeks: component → detail → ship. A recurring project in the feed builds recognition; three posts in one day cannibalise each other.