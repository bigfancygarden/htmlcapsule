# HTML Capsule design system

> Handoff bundle from Claude Design (`claude.ai/design`), received 2026-05-22.
> Canonical design system for the project.

## Origin

The maintainer asked Claude Design to *"propose visual enhancements for all of these"* — referring to the seven HTML Capsule sketches in flight at the time (`index.html`, `landing-sketch.html`, `landing-sketch-v2.html`, `research-sketch.html`, `research-sketch-v2.html`, `positioning-sketch.html`, `notes.html`).

Two proposals were generated. The maintainer asked Claude Design to "decide for me" on direction, and Claude Design first committed to an *editorial-archival* direction (newsreader display serif + Geist + Geist Mono, warm cream paper, oxide accent). The maintainer rejected that with:

> *"i just don't really like that proposal. i would prefer something like what's on htmlcapsule.org already, something more accessible, modern, clean, sans serif, using colour and type weight to clean up ideas/sections."*

Claude Design then redid the proposal in the modern-sans direction. That second version is **canonical**.

| File | Status |
|---|---|
| `proposal.html` | **canonical** — modern-sans direction, all Geist (300→800), cool fog paper, five semantic hues mapped to section kinds |
| `proposal-v1-editorial.html` | **rejected** — editorial-archival direction, preserved for record |

## The system

### Typography

- Family: **Geist** (web) with system-sans fallback for Capsule compliance with Core rule 2 (no network).
- Weights: **300, 400, 500, 600, 700, 800**.
- Pattern: **weight contrast replaces italic emphasis.** Headlines mix 300 (the "light" connective phrases) with 800 (the "punch" word) — e.g., `<span class="light">HTML you can</span> <span class="keep">keep.</span>`.
- Mono: **Geist Mono** for metadata (version tags, timestamps, section labels).

### Paper system (cool fog)

| Token | Hex | Use |
|---|---|---|
| `--paper` | `#f5f6f8` | Page background |
| `--paper-soft` | `#ebedf1` | Secondary surfaces |
| `--paper-deep` | `#dee1e7` | Tertiary surfaces |
| `--paper-page` | `#ffffff` | Cards, mock chrome |

### Ink scale

| Token | Hex | Use |
|---|---|---|
| `--ink` | `#0c0e13` | Body text, headlines |
| `--ink-soft` | `#2a2e38` | Subtitles, secondary copy |
| `--ink-mute` | `#5d6470` | Mono metadata, captions |
| `--ink-faint` | `#8a909c` | Disabled, tertiary |
| `--ink-quiet` | `#b0b5be` | Decorative only |

### Rule scale

| Token | Hex | Use |
|---|---|---|
| `--rule` | `#dde0e6` | Standard borders |
| `--rule-soft` | `#e8eaef` | Hairline dividers |
| `--rule-strong` | `#c8ccd4` | Card hover, emphasis |

### Five semantic hues — the taxonomy

The project's central design insight: **every visible section type gets its own color.** The eye learns to skim by color in two scrolls.

| Hue | Base | Soft | Edge | Deep | Use |
|---|---|---|---|---|---|
| **Indigo** | `#4f46e5` | `#eef0fe` | `#c7cbf6` | `#3730a3` | brand · primary CTA · headline emphasis · spec material |
| **Violet** | `#7c3aed` | `#f3edff` | `#d6c5fa` | `#5b21b6` | **Questions** · open work · research-flagged |
| **Teal** | `#0d9488` | `#e0f5f1` | `#a8dcd1` | `#115e59` | **Observations** · evidence · quotes |
| **Amber** | `#b45309` | `#fbeed5` | `#ecd09b` | `#7c2d12` | **Answers** · maintainer voice · essay |
| **Rose** | `#be123c` | `#fce4ea` | `#efb7c2` | `#831843` | **Pain** · negation · "shouldn't die" framing |

### Radii

- `--radius-sm` (8px) — controls, buttons, inputs
- `--radius` (14px) — cards, panels
- `--radius-pill` (999px) — eyebrows, tags, status chips

### Shell width

- `--shell-w` (1240px) — page container max-width

## How to apply (Capsule compliance)

Capsules must follow Core rule 2 (no network dependencies). To use this design system in a Capsule:

1. **Inline the font stack with system fallback.** Do not link to Google Fonts:
   ```css
   --sans: "Geist", -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", system-ui, sans-serif;
   --mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
   ```
   If the reader has Geist installed locally, it renders in Geist; otherwise it falls back to the system stack — which is what the project already uses and what the maintainer endorsed in chat (*"Set in system sans"*).

2. **Inline the tokens** into the `<style id="capsule-style">` block. Use `tokens.css` in this folder as a reference; copy the `:root` block verbatim into each Capsule's style block.

3. **Apply the semantic hues** to existing section classes:
   - `.is-observation` → teal background + edge
   - `.is-question` → violet background + edge
   - `.is-answer` → amber background + edge
   - Brand emphasis, primary CTAs → indigo
   - Pain framing ("shouldn't die", "context loss") → rose

4. **Use weight contrast for emphasis, not italics.** Headlines mix weight 300 + weight 800 within the same `<h1>`. The "light" parts are connective phrases; the "punch" word is the load-bearing claim.

## Mapping to the existing landing pages

| Page | Lead color | Key applications |
|---|---|---|
| `index.html` (research-narrative hybrid) | mixed by section | Observation cards → teal; Question cards → violet; Answer cards → amber; brand/primary CTAs → indigo |
| `landing-sketch-v2.html` (Linear/Stripe) | indigo | Hero "keep" emphasis → indigo 800; anatomy card with manifest row highlighted in indigo |
| `research-sketch-v2.html` (NeRF/paper) | teal | Findings (O1-O5) as a grid, each card in its taxonomy color; teal eyebrow for "Research note" |
| `positioning-sketch.html` (synthesis) | rose → indigo | Headline "die" in rose, "seal" in indigo; rose eyebrow ("The pain · anti-context-loss") |
| `notes.html` (essay) | amber | Amber category chip, margin numerals in amber 700, amber pull quote |

## Files in this folder

- `proposal.html` — **canonical** design memo from Claude Design with mockups of all four target pages. Contains the design's CSS in context. Uses Google Fonts directly — *not Capsule-compliant on its own*; this is a design tool output, not a Capsule.
- `proposal-v1-editorial.html` — **rejected** first version (editorial-archival direction). Preserved for record.
- `tokens.css` — extracted CSS variables for copy-paste into Capsule `<style>` blocks. System-font fallback only; no network calls; Capsule-compliant.
- `README.md` — this file.

## Provenance

- **Bundle origin:** `https://api.anthropic.com/v1/design/h/1h9LEWoDBWZgTL3Fqnnz6w` (received 2026-05-22)
- **Bundle path:** `html-capsule-improvements/`
- **Design tool:** Claude Design (`claude.ai/design`)
- **Maintainer chat transcript:** `html-capsule-improvements/chats/chat1.md` in the original bundle (the chat where direction was decided)
