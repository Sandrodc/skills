---
name: "build-in-public-media"
description: "Produce polished videos and images of UI work for X posts: isolate components, frame screen recordings on a background, punch-in zooms, export settings. Use when making a build-in-public visual or framing a CleanShot recording."
---

# Build-in-public media

The subject is the UI. Everything else — background, padding, cursor, timing — exists to make one detail readable at phone size in 2 seconds.

## Step 1 — Pick the recipe

```
What is being shown?
├── One component, several states (cards, icons, buttons)
│   └── A. STAGE: render the component alone and cycle states
├── A small interaction inside a real screen (hover, typing, a transition)
│   └── B. PUNCH-IN: record the real window, zoom into the detail, zoom out
├── A shipped screen or flow on mobile
│   └── C. DEVICE CROP: device frame, cropped to the area that changed
└── Static polish (type, layout, an illustration)
    └── D. STILL: same framing as A/B, exported as PNG
```

## Step 2 — Build the source

**A. Stage.** Create a stage that renders only the component, centred:
- Web: a single `stage.html` (or a route) importing the real component, nothing else on the page.
- SwiftUI: a `#Preview` or a debug-only screen with just the component on a fixed background; run in the simulator.
- Cycle states automatically every 1.5–2.5 s with the component's real transitions, or script a hover. Auto-cycling makes the recording repeatable; hand-clicking gives uneven timing.
- Background: `#F5F5F5` (light) or `#0E0E0E` (dark). Pick the mode the component looks best in; never both in one clip.

**B/C.** Record the real app with CleanShot at Retina resolution. Hide everything that isn't the product: debug overlays, other windows, notifications, dev badges. On iOS, set status bar to 9:41, full battery, full signal (`xcrun simctl status_bar booted override --time 9:41 --batteryLevel 100 --batteryState charged --cellularBars 4`).

**Placeholder content — always:**
- Invent plausible content (book titles, names, numbers) and keep it consistent across all frames, like the references' "Salt and Static — Theo Marchetti".
- Never lorem ipsum: it reads as unfinished.
- Never real user data or client data: one leaked name ends the post.
- Artwork/thumbnails: soft blurred gradients, not stock photos. They read as "cover art" without pulling focus.

## Step 3 — Frame it (strict specs)

| Content | Canvas |
|---|---|
| Component / icon / card | 1600×1600 (1:1) |
| Phone screen | 1600×2000 (4:5) |
| Desktop window / browser | 1920×1080 (16:9) |

Square and portrait take more timeline height than landscape, so use landscape only when the content is landscape.

- Content fills 60–75% of canvas width. Less looks lost; more looks cramped and loses the "presented" feel.
- Background: flat neutral or one soft 2-stop gradient (e.g. `#E9EEF2 → #D6E4DA`). Never more than 2 colours, never a busy wallpaper — it competes with the UI.
- Framed windows get 16–28 px corner radius at canvas scale.
- Smallest text must be readable when the frame is viewed at 600 px wide. If not, crop tighter or punch in.

Frame a recording (tested; set `W H PAD R` per the table above):

```bash
W=1600; H=1600; PAD=160; R=24
ffmpeg -y -f lavfi -i "gradients=s=${W}x${H}:c0=0xE9EEF2:c1=0xD6E4DA:x0=0:y0=0:x1=${W}:y1=${H}:d=60,format=yuv420p" -i in.mp4 -filter_complex "\
[1:v]scale=$((W-2*PAD)):$((H-2*PAD)):force_original_aspect_ratio=decrease,format=rgba,\
geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(gt(abs(W/2-X),W/2-$R)*gt(abs(H/2-Y),H/2-$R),if(lte(hypot($R-(W/2-abs(W/2-X)),$R-(H/2-abs(H/2-Y))),$R),255,0),255)'[fg];\
[0:v][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,fps=60,format=yuv420p[v]" \
-map "[v]" -an -c:v libx264 -crf 18 -preset veryfast -movflags +faststart framed.mp4
```

Punch-in zoom for recipe B (tested; eased in/out, hold on the detail). `FX FY` = focus point as 0–1 fractions, `Z` = zoom, `T1–T2` zoom in, `T3–T4` zoom out:

```bash
FX=0.72; FY=0.45; Z=2.2; T1=0.8; T2=1.6; T3=3.6; T4=4.4
P="if(lt(t,$T1),0,if(lt(t,$T2),(1-cos(PI*(t-$T1)/($T2-$T1)))/2,if(lt(t,$T3),1,if(lt(t,$T4),(1+cos(PI*(t-$T3)/($T4-$T3)))/2,0))))"
ffmpeg -y -i framed.mp4 -vf "crop=w='iw/(1+($Z-1)*$P)':h='ih/(1+($Z-1)*$P)':x='(iw-ow)*$FX':y='(ih-oh)*$FY':exact=1,scale=1600:1600:flags=lanczos,setsar=1,format=yuv420p" -an -c:v libx264 -crf 18 -preset veryfast -movflags +faststart zoom.mp4
```

Zoom moves take 0.6–0.9 s; hold on the detail for at least 1.5 s. Faster feels jumpy; a shorter hold means the viewer misses the thing you zoomed for.

## Step 4 — Timing and export

- Length 4–12 s for details and components; up to 30 s only for a set of 4+ states (like the animated-icons reference). Viewers should see the full arc before scrolling past.
- First frame already shows the subject — no blank or loading intro. The autoplay thumbnail is the first frame.
- Last frame matches the first so the loop is seamless. Trim with `-ss`/`-t` until it does.
- Cursor: visible only when the post is about a hover or click; moves in slow, straight, eased paths. Otherwise hide it — a wandering cursor steals focus.
- Export: H.264, 60 fps, CRF 18, `yuv420p`, no audio track, `+faststart`. Never GIF: it bands gradients and gets recompressed badly.
- Stills: PNG at 2× the canvas.

## Step 5 — Check before handing over

Extract the first, middle and last frame at 600 px wide and look at them:

```bash
for t in 0 50% end; do :; done  # use: ffmpeg -ss <sec> -i out.mp4 -frames:v 1 -vf scale=600:-1 f_<sec>.jpg
```

Reject and redo if: the subject isn't obvious in the middle frame, any text is unreadable, placeholder data is inconsistent between frames, or anything that isn't the product is visible.