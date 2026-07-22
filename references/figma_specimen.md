# Figma views — exact build recipe

When the output target includes Figma, build **two views** from the computed
system. The design below is fixed — reproduce it exactly. Only the *contents*
change: font name, sizes, line-heights, repetition unit, row counts, sample copy.

- **View 1 — Specimen:** the full t-shirt scale, one row per token.
- **View 2 — Repetition unit:** three columns showing how each size returns to
  the same grid after a whole number of rows.

The examples below are the proven scripts (they built the Aspekta reference).
Keep every constant — palette, sizes, positions, spacing — identical.

## Preconditions (do these first)

1. **Load the figma-use skill** before any `use_figma` call, and pass
   `skillNames: "resource:figma-use"`. Writes are atomic; on error, STOP, read
   it, fix, retry. Work incrementally (one `use_figma` call per block below) and
   `return` created node IDs each time.
2. **Resolve a render font.** The system's typeface may not be installed in the
   Figma file — `loadFontAsync` on a missing font aborts the whole script. Run a
   read-only check first and pick the family to render with:

```js
const fonts = await figma.listAvailableFontsAsync();
const has = (fam,style)=>fonts.some(f=>f.fontName.family===fam && f.fontName.style===style);
const SYSTEM_FONT = "Aspekta"; // the system's actual typeface
const installed = fonts.some(f=>f.fontName.family===SYSTEM_FONT);
const chain=[SYSTEM_FONT,"Inter","Roboto","Arial","Helvetica Neue","Helvetica"];
let family = chain.find(f=>has(f,"Regular")) || fonts.find(f=>f.fontName.style==="Regular").fontName.family;
const pick=(...c)=>c.find(s=>has(family,s))||"Regular";
const reg=pick("Regular"), med=pick("Medium","Regular"), bold=pick("Bold","Semi Bold","Medium");
```

   If `installed` is false, note it in the specimen meta line ("rendered in
   {family} (Aspekta not installed)") and tell the user the line-heights are
   correct but the glyphs are a stand-in until the real font is added.
3. **Target frame.** If the user points at an existing frame, build View 1 into
   it — but first inspect and remove any pre-existing children that aren't part
   of the specimen (converting a frame to auto-layout absorbs stray nodes). View
   2 is always a **new** frame, positioned one gap below View 1.

## Fixed palette (RGB 0–1 — never change)

```js
const C = {
  bg:      {r:1,     g:1,     b:1},       // white
  ink:     {r:0.110, g:0.106, b:0.094},   // near-black
  muted:   {r:0.604, g:0.580, b:0.533},   // secondary text
  hair:    {r:0.871, g:0.859, b:0.827},   // dividers (grey)
  chip:    {r:0.039, g:0.035, b:0.157},   // token chip bg (deep navy)
  cream:   {r:0.957, g:0.949, b:0.933},   // chip label
  blue:    {r:0.201, g:0.508, b:1.000},   // measure bar, ticks, and its labels
  blueLine:{r:0.691, g:0.809, b:1.000},   // repetition-unit dashed boundaries (light)
  red:     {r:1.000, g:0.074, b:0.290},   // "aligns every N rows" labels
  redLine: {r:1.000, g:0.783, b:0.833},   // baseline hairlines (light pink)
};
```

## Inputs from the computed system

Map the compute-script output to these:
- `family, reg, med` — resolved above.
- `SYSTEM_FONT` — display name shown on labels ("Aspekta").
- `unit` — repetition unit px (e.g. 168).
- `base, baseLH` — body token size/line-height (the `sm` row, e.g. 15 / 21).
- `tokens` — full scale, ordered small→large:
  `[{tok, size, lh, rows}]` where `rows = unit / lh`. Include a `role` + a
  `sample` sentence per token (see copy guidance).
- `repCols` — the 3 tokens to show in View 2: pick a display/heading size, a
  mid size, and the body size (e.g. lg, md, sm). Each has `{tok,size,lh,rows}`.

## View 1 — Specimen

### 1a. Container + header + divider (one call)

```js
const base = await figma.getNodeByIdAsync(TARGET_FRAME_ID);
base.layoutMode="VERTICAL"; base.resize(880, base.height);
base.primaryAxisSizingMode="AUTO"; base.counterAxisSizingMode="FIXED";
base.paddingTop=56; base.paddingBottom=56; base.paddingLeft=56; base.paddingRight=56;
base.itemSpacing=36; base.fills=[{type:"SOLID",color:C.bg}];
base.name=SYSTEM_FONT+" — Type System";
const mk=(txt,style,size,color,lh)=>{const t=figma.createText();t.fontName={family,style};
  t.characters=txt;t.fontSize=size;t.fills=[{type:"SOLID",color}];
  if(lh)t.lineHeight={unit:"PIXELS",value:lh};return t;};
const head=figma.createAutoLayout("VERTICAL"); head.name="Header"; head.itemSpacing=8; head.fills=[];
base.appendChild(head); head.layoutSizingHorizontal="FILL";
head.appendChild(mk(SYSTEM_FONT,med,28,C.ink,32));
head.appendChild(mk("Web type system · optically anchored · "+unit+"px baseline grid",reg,15,C.muted,21));
head.appendChild(mk("Body "+base_+"/"+baseLH+" · grid unit "+unit+" · rendered in "+family+FONT_NOTE,reg,13,C.muted,21));
const rule=figma.createRectangle(); rule.resize(1,1); rule.fills=[{type:"SOLID",color:C.hair}];
base.appendChild(rule); rule.layoutSizingHorizontal="FILL"; rule.layoutSizingVertical="FIXED"; rule.resize(rule.width,1);
```
`FONT_NOTE` is `""` when installed, else `" ("+SYSTEM_FONT+" not installed)"`.

### 1b. Token rows (split across 2 calls, ~3 rows each)

Each row = left meta column (fixed 150: chip + "size / lh" + "aligns every N
rows") and a wrapping sample at the token's size/line-height.

```js
function row(tok,size,lh,aligns,sample){
  const r=figma.createAutoLayout("HORIZONTAL"); r.name="row/"+tok; r.itemSpacing=32;
  r.counterAxisAlignItems="MIN"; r.fills=[];
  base.appendChild(r); r.layoutSizingHorizontal="FILL"; r.layoutSizingVertical="HUG";
  const col=figma.createAutoLayout("VERTICAL"); col.itemSpacing=6; col.fills=[]; col.name="meta";
  r.appendChild(col); col.layoutSizingHorizontal="FIXED"; col.resize(150,col.height); col.layoutSizingVertical="HUG";
  const chip=figma.createAutoLayout("HORIZONTAL"); chip.paddingLeft=7;chip.paddingRight=7;chip.paddingTop=3;chip.paddingBottom=3;
  chip.cornerRadius=5; chip.fills=[{type:"SOLID",color:C.chip}]; chip.name="chip";
  col.appendChild(chip); chip.layoutSizingHorizontal="HUG"; chip.layoutSizingVertical="HUG";
  const cl=figma.createText(); cl.fontName={family,style:med}; cl.characters=tok; cl.fontSize=11;
  cl.fills=[{type:"SOLID",color:C.cream}]; chip.appendChild(cl);
  const m1=figma.createText(); m1.fontName={family,style:reg}; m1.characters=size+" / "+lh; m1.fontSize=13;
  m1.fills=[{type:"SOLID",color:C.ink}]; m1.lineHeight={unit:"PIXELS",value:18}; col.appendChild(m1);
  const m2=figma.createText(); m2.fontName={family,style:reg}; m2.characters="aligns every "+aligns; m2.fontSize=12;
  m2.fills=[{type:"SOLID",color:C.muted}]; m2.lineHeight={unit:"PIXELS",value:18}; col.appendChild(m2);
  const s=figma.createText(); s.fontName={family,style:reg}; s.characters=sample; s.fontSize=size;
  s.fills=[{type:"SOLID",color:C.ink}]; s.lineHeight={unit:"PIXELS",value:lh};
  r.appendChild(s); s.textAutoResize="HEIGHT"; s.layoutSizingHorizontal="FILL";
  return r.id;
}
```
Call `row(t.tok, t.size, t.lh, t.rows+" rows", t.sample)` for every token. `aligns`
is `rows`. Sample copy: caption/label text for `xs`; a body sentence for the
body token; lead-paragraph copy for the next; short evocative phrases for
headings/display (2–5 words for display so it doesn't wrap oddly at 880 wide).

### 1c. Footer (one call)

Divider rect (as 1a) then a notes column:
```js
const foot=figma.createAutoLayout("VERTICAL"); foot.itemSpacing=6; foot.fills=[]; foot.name="notes";
base.appendChild(foot); foot.layoutSizingHorizontal="FILL"; foot.layoutSizingVertical="HUG";
foot.appendChild(mk("How it was built",med,13,C.ink));           // heading
// three muted lines (reg 13, lh 20, FILL width, textAutoResize HEIGHT):
//  - base size is optical, tied to the font's x-height (why it isn't a round number)
//  - every line-height divides the {unit}px unit, so all sizes share one grid
//  - any display-leading tightening done by eye
await base.screenshot({scale:1});
```

## View 2 — Repetition unit

### 2a. Frame + boundaries + measure + caption (one call)

```js
const base = await figma.getNodeByIdAsync(VIEW1_FRAME_ID);   // to position below it
const FW=1260, FH=580, unitTop=300, unitH=unit, unitBottom=unitTop+unitH;
const view=figma.createFrame(); view.name="Repetition unit — how it works";
view.resize(FW,FH); view.x=base.x; view.y=base.y+base.height+140;
view.fills=[{type:"SOLID",color:C.bg}]; view.clipsContent=true;
const txt=(t,style,size,color,x,y,lh)=>{const n=figma.createText();n.fontName={family,style};
  n.characters=t;n.fontSize=size;n.fills=[{type:"SOLID",color}];n.x=x;n.y=y;
  if(lh)n.lineHeight={unit:"PIXELS",value:lh};view.appendChild(n);return n;};
txt("How the repetition unit works",med,24,C.ink,40,44,28);
txt("Every size returns to the same "+unit+"px grid — after a different number of rows.",reg,15,C.muted,40,84,21);
const dline=(y)=>{const l=figma.createLine();view.appendChild(l);l.x=40;l.y=y;l.resize(1180,0);
  l.strokes=[{type:"SOLID",color:C.blueLine}];l.strokeWeight=1;l.dashPattern=[5,4];};
dline(unitTop); dline(unitBottom);
txt("Repetition unit",reg,12,C.blue,40,unitTop-34,16);
const bar=figma.createRectangle();view.appendChild(bar);bar.x=92;bar.y=unitTop;bar.resize(2,unitH);
bar.fills=[{type:"SOLID",color:C.blue}];
const tick=(y)=>{const r=figma.createRectangle();view.appendChild(r);r.x=84;r.y=y;r.resize(18,2);
  r.fills=[{type:"SOLID",color:C.blue}];};
tick(unitTop); tick(unitBottom-2);
txt(String(unit),med,13,C.blue,52,unitTop+unitH/2-9,16);
txt("One repetition unit = "+unit+"px. Each size fills it in a whole number of rows — "+EXAMPLES+" — so every size shares the same baseline grid.",
    reg,13,C.muted,40,unitBottom+40,20).resize(1180,40);
```
`EXAMPLES` e.g. `"lg in 4, md in 6, sm in 8"` from `repCols`.

### 2b. Three columns (one call per column)

`colX` = `[160, 540, 920]`, `colW=300`. Baseline hairlines at every row; sample
clipped to exactly one unit.

```js
function column(colX,tok,size,lh,rows,sample){
  const chip=figma.createAutoLayout("HORIZONTAL");chip.x=colX;chip.y=150;
  chip.paddingLeft=7;chip.paddingRight=7;chip.paddingTop=3;chip.paddingBottom=3;
  chip.cornerRadius=5;chip.fills=[{type:"SOLID",color:C.chip}];view.appendChild(chip);
  chip.layoutSizingHorizontal="HUG";chip.layoutSizingVertical="HUG";
  const cl=figma.createText();cl.fontName={family,style:med};cl.characters=tok;cl.fontSize=11;
  cl.fills=[{type:"SOLID",color:C.cream}];chip.appendChild(cl);
  const lab=figma.createText();lab.fontName={family,style:reg};lab.characters=SYSTEM_FONT+"\n"+size+" / "+lh;
  lab.fontSize=14;lab.fills=[{type:"SOLID",color:C.ink}];lab.lineHeight={unit:"PIXELS",value:20};
  lab.x=colX;lab.y=192;view.appendChild(lab);
  const al=figma.createText();al.fontName={family,style:reg};al.characters="Aligns every "+rows+" rows";
  al.fontSize=14;al.fills=[{type:"SOLID",color:C.red}];al.x=colX;al.y=unitTop-32;view.appendChild(al);
  const clip=figma.createFrame();clip.x=colX;clip.y=unitTop;clip.resize(colW,unitH);
  clip.fills=[];clip.clipsContent=true;clip.name="col/"+tok;view.appendChild(clip);
  for(let k=1;k<=rows;k++){const h=figma.createRectangle();clip.appendChild(h);
    h.x=0;h.y=k*lh;h.resize(colW,1);h.fills=[{type:"SOLID",color:C.redLine}];}
  const s=figma.createText();s.fontName={family,style:reg};s.characters=sample;s.fontSize=size;
  s.fills=[{type:"SOLID",color:C.ink}];s.lineHeight={unit:"PIXELS",value:lh};
  clip.appendChild(s);s.x=0;s.y=0;s.textAutoResize="HEIGHT";s.resize(colW,s.height);
  return clip.id;
}
```
Give each column enough sample copy to overflow its row count (clip hides the
rest). Screenshot the view after the last column to verify.

## After building

Tell the user both views are in the file, which font is actually rendering, and
that importing the DTCG tokens via Tokens Studio creates the real type styles.
Offer: swap to the real font once installed, add base/xs columns to View 2, or
show the unit repeating twice.
