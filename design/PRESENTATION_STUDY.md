# Capsule Presentation Study

Status: exploratory design note

This study captures the presentation pressure discovered while dogfooding
Capsules in HTML Vault and while testing LLM-generated Capsules. The core
question is not "how many views can a Capsule have?" The better question is:

```text
What is the smallest durable content structure that can compile into the four
presentation surfaces people actually need?
```

## Scope Boundary

This study is not a new Capsule rule. It sits between the spec and the compiler.

```text
Capsule spec
  -> declares identity, provenance, readable root, data, capabilities,
     presentations, and validation rules

Presentation study
  -> studies how information should be structured so presentation renderers can
     derive multiple surfaces from one content layer

Reference compiler / HTML Vault
  -> turns that structure into polished scroll, slide, story, print, or mobile
     outputs while preserving the original artifact
```

The Capsule spec should not become a full presentation framework. It should name
the contract and carry enough structured content for compilers and hosts to do
the presentation work honestly.

## The 2x2

Most current pressure fits a simple 2x2:

| Surface | Scroll mode | One-screen mode |
|---|---|---|
| Desktop | `reader` | `slides` |
| Mobile | `mobile` | `reel` |

This is the useful center of gravity:

- `reader`: desktop/web scrolling document. This is the default durable view.
- `mobile`: phone-oriented scrolling document. This is optional; responsive CSS
  alone does not require a separate declared presentation.
- `slides`: desktop one-screen-at-a-time deck.
- `reel`: mobile one-screen-at-a-time story sequence.

Everything else should be treated carefully:

- `print-letter` is a production/export surface, not a fifth reading mode.
- `interactive` is a capability-bearing enhanced view, not a basic layout mode.
- domain renderers such as maps, timelines, galleries, and dashboards should use
  namespaced extensions until repeated pressure justifies core vocabulary.

## Working Hypothesis

A good Capsule needs two related structures:

```text
sections = durable document structure
cards    = presentation beats derived from sections
```

`sections` make the artifact readable, searchable, quotable, and useful with
JavaScript off. `cards` make the artifact compilable into one-screen surfaces
without asking an LLM to hand-author four parallel documents.

The relationship is one-way:

```text
sections -> cards -> renderers
```

Cards should not introduce independent facts. A card may compress, sequence,
label, quote, or emphasize canonical content, but it should trace back to one or
more source sections.

## Proposed Source Model

The current spec now recommends optional `presentation_model.cards[]` in
`capsule-data`. This study treats that as the bridge shape to test.

Minimal shape:

```json
{
  "sections": [
    {
      "id": "summary",
      "title": "Summary",
      "body": "The durable reader content."
    }
  ],
  "assets": [
    {
      "id": "hero",
      "media_type": "image/jpeg",
      "src": "data:image/jpeg;base64,...",
      "alt": "Short description of the image."
    }
  ],
  "presentation_model": {
    "cards": [
      {
        "id": "cover",
        "role": "cover",
        "title": "Briefing Title",
        "body": "Short opening frame.",
        "asset_refs": ["hero"],
        "source_sections": ["summary"]
      },
      {
        "id": "point_1",
        "role": "story",
        "title": "One idea",
        "body": "A single beat derived from the reader content.",
        "source_sections": ["summary"]
      },
      {
        "id": "end",
        "role": "end",
        "title": "End",
        "body": "Closing frame or next action.",
        "action": "restart",
        "source_sections": ["summary"]
      }
    ]
  }
}
```

Open question: should `sections` become a recommended top-level shape in
`capsule-data`, or should the spec leave document sections domain-specific and
only recommend `presentation_model.cards[]`? The conservative answer for now is:
recommend card references to stable section ids, but do not require a universal
section schema.

## Asset Deduplication

Multi-view Capsules should not duplicate heavy media per presentation.

The preferred source model is:

```text
substance lives once:
  sections[]
  presentation_model.cards[]
  assets[]
  sources/provenance

presentations duplicate only small chrome:
  reader markup
  mobile markup
  slides markup
  reel markup
```

For semantic media, prefer asset records with stable ids, alt text, media type,
and optional provenance/hash metadata. Cards and sections reference those assets
by id:

```json
{
  "id": "point_1",
  "title": "One idea",
  "body": "A single beat.",
  "asset_refs": ["hero"],
  "source_sections": ["summary"]
}
```

Renderer templates may emit the same asset in different ways:

- as a semantic `<figure><img>` in the reader
- as a slide background or figure in `slides`
- as a card visual in `reel`
- as a responsive image in `mobile`

CSS custom properties can be useful for presentation-only images, but substantial
media should not live only inside CSS. If an image, audio clip, or video is part
of the artifact's substance, it should be represented in data/assets with enough
metadata for readers, validators, LLMs, and future compilers to understand it.

This changes the size intuition. A four-view Capsule is not four copies of the
artifact. It should be closer to:

```text
1x substance and media
+ small renderer chrome
+ small duplicated text markup where pre-rendered views need it
```

Bundle remains the answer for substance size, not presentation count: large
rasters, long video, LiDAR, many files, or project-shaped assets.

## UUID Decision Rules

The rule of thumb:

```text
One UUID per sealed Capsule package.
Multiple presentations inside one package when generated together.
New UUID when an existing sealed package is compiled into a new package.
```

Use the same Capsule UUID when:

- the reader, mobile, slides, and reel views are generated together as part of
  one export/seal operation
- all presentations render the same declared substance
- cards, sections, assets, and sources are shared
- views differ in layout, pacing, navigation, or chrome, but not in facts

Mint a new Capsule UUID when:

- Vault or another tool adds presentations after the source Capsule was already
  sealed
- the output has a different generator/trust story
- the presentation introduces new claims, commentary, ordering, or editorial
  emphasis that is not traceable to the source sections/cards
- the result is intended to stand alone as a derived work, such as a public slide
  deck made from a longer private report
- the artifact crosses Capsule's single-file ceiling and must become a Bundle

Recommended mental model:

```text
Same sealed package, many views      -> one Capsule UUID
New sealed package from old package  -> new Capsule UUID + derived_from/parents
Project-shaped file set              -> Bundle UUID
Vault grouping                       -> local artifact family, not the spec id
```

This preserves both user ergonomics and artifact integrity. Users can think "one
thing, many ways to view it" when the views were packaged together. Tools can
still verify that a later compiler pass produced new bytes with its own UUID,
digest, generator metadata, scan result, and provenance.

## Renderer Defaults

Reference renderers are examples, not conformance targets:

| Renderer | Current example | Notes |
|---|---|---|
| Mobile story | `demos/presentation-surfaces/stories.html` | Native-ish phone surface with progress, tap/swipe, hold-to-pause, replay/end state, and safe-area handling. |
| Desktop slides | `demos/presentation-surfaces/slides.html` | 16:9 deck surface with one idea per frame. |
| Valid story Capsule | `spec/examples/presentations/demo_stories_capsule.html` | Declares `profile: "reel"` and includes `presentation_model.cards[]`. |
| Valid slides Capsule | `spec/examples/presentations/demo_slides_capsule.html` | Declares `profile: "slides"` and keeps reader content intact. |

The important distinction:

```text
Spec = what the artifact declares and preserves.
Renderer = how a host/compiler presents declared content.
```

## Chrome Ownership

HTML Vault dogfooding on iOS exposed a real host/capsule failure mode: a mobile
story Capsule can draw its own progress bars, title/avatar row, play/pause,
close, and replay controls while the host app also draws back, title,
presentation, play/pause, and menu controls. The result is double chrome.

The `presentations[].chrome` hint exists to keep one owner for those controls:

```text
chrome: "capsule"
  The declared entry owns its controls. Hosts should recede and provide at most
  an escape/back affordance outside the content surface.

chrome: "host"
  The host may supply presentation controls around the declared entry.

chrome: "none"
  The entry is content-only.
```

Self-rendering story/reel views and slide decks that include their own progress,
play/pause, close/replay, or next/previous controls should declare
`chrome: "capsule"`. Host-native renderers can still enhance a Capsule from
`presentation_model.cards[]`, but that should be a clearly host-rendered view,
not a second control layer on top of a capsule-owned DOM renderer.

### Required exit hatch for capsule-owned full-screen views (2026-06-03)

Dogfooding in HTML Vault surfaced the corollary: a capsule-owned full-screen view
hides the host's chrome, so it must carry its own way back to the host's main
view, or the reader gets trapped. The convention:

```text
A presentation with profile "reel" + chrome "capsule" MUST include a control
marked data-capsule-action="exit". An X is enough.
```

The exit control's runtime should be host-neutral and degrade gracefully — try a
host capability object, then a host message channel, then a parent-frame
`postMessage({type:"capsule:exit"})`, then `history.back()` / `window.close()`
when opened with no host. This keeps the capsule self-contained (works opened
raw) while letting any host wire its "return" action to a standard hook rather
than a vendor API.

`compiler/validate.py` checks this as a WARN ("Capsule-owned full-screen view
provides an exit hatch"); it can graduate to a hard failure once the multiview
fixtures adopt the hatch. A conforming host may recede entirely when the hatch is
present and supply its own minimal escape only when it is absent. See the
companion host-side write-up in the HTML Vault repo
(`docs/CAPSULE_PRESENTATION_HOST_CONTRACT.md`).

## LLM Role

LLMs are good at:

- writing a readable root document
- extracting section ids and summaries
- drafting a `presentation_model.cards[]` sequence
- mapping cards back to source sections
- proposing titles, beats, and ending actions

LLMs are unreliable at:

- exact manifest shape under pressure
- maintaining four parallel hand-authored views
- polished story/deck behavior
- gesture/timing/accessibility details
- preserving primary meaning when runtime UI becomes seductive

Recommended LLM prompt target:

```text
Make one valid reader-first Capsule.
Include capsule-data.presentation_model.cards[] for possible slides/story
compilation.
Do not hand-author advanced slides or story UI unless explicitly asked.
```

## Compiler Role

The compiler should generate the fussy parts:

- exact `presentations[]` declarations
- the responsive `reader`/`mobile` baseline when generated at seal time
- `#capsule-slides`
- `#capsule-reel`
- asset references from shared `assets[]` records
- viewport and safe-area handling
- progress/timing controls
- tap/swipe/keyboard behavior
- replay/end states
- deterministic print layout
- source-section links on derived screens

When the compiler is the original exporter, it should build the proper views into
one Capsule at once where practical: reader by default, responsive/mobile
support, and optional slides/reel when cards exist. When the compiler operates on
an already-sealed Capsule in Vault, it should produce a new standalone derived
Capsule with a new UUID and provenance pointing back to the source. The source
Capsule remains unchanged.

## Vault Role

HTML Vault should be the workshop:

- detect whether a Capsule is compiler-ready
- show missing reader content, sparse sections, missing cards, and legacy
  presentation shapes
- expose actions such as `Generate Mobile Story View` and `Generate Desktop
  Slides View`
- preview original and derived artifacts side by side
- validate and scan derived bytes before promotion/export

Vault should not define the format. It should consume the spec and apply the
reference compiler contract.

## Study Plan

### Phase 1: Corpus

Build a small corpus of reader-first Capsules with `presentation_model.cards[]`:

- briefing
- release note
- design review
- security review
- timeline/explainer

Each should validate as a normal Capsule before any alternate views are compiled.

### Phase 2: Compiler Experiment

Write a deterministic compiler experiment:

```text
reader Capsule + cards
  -> derived Capsule with reader + slides
  -> derived Capsule with reader + reel
  -> derived Capsule with reader + slides + reel
```

Measure whether the cards are enough or whether we need richer hints such as
`emphasis`, `media_ref`, `duration_ms`, `layout`, or `quote`.

Current experiment:

```text
examples/multiview_chat_summary.json
  -> compiler/compile_multiview_demo.py
  -> spec/examples/presentations/multiview_compiled_capsule.html
```

The current corpus compiles one source model shape with `sections[]`,
`assets[]`, and `presentation_model.cards[]` into one Capsule with five declared
presentations: `reader`, mobile snap, mobile feed, `slides`, and `reel`.
Each generated fixture keeps one UUID across those views, resolves all five
presentation entries, shares the embedded asset by id, and validates as a normal
single-file Capsule.

```text
examples/multiview_chat_summary.json
  -> spec/examples/presentations/multiview_compiled_capsule.html

examples/multiview_directory_demo.json
  -> spec/examples/presentations/multiview_directory_capsule.html

examples/multiview_essay_demo.json
  -> spec/examples/presentations/multiview_essay_capsule.html

examples/multiview_release_notes_demo.json
  -> spec/examples/presentations/multiview_release_notes_capsule.html

examples/multiview_field_safety_demo.json
  -> spec/examples/presentations/multiview_field_safety_capsule.html

examples/multiview_market_watch_demo.json
  -> spec/examples/presentations/multiview_market_watch_capsule.html

examples/multiview_chrome_contract_demo.json
  -> spec/examples/presentations/multiview_chrome_contract_capsule.html

examples/multiview_chrome_contract_locked_demo.json
  -> spec/examples/presentations/multiview_chrome_contract_locked_capsule.html
```

The locked chrome-contract fixture adds `story_behavior: "locked"` to the source
model. The compiler uses that as a rendering hint for mobile reel/story mode:
the story viewport is fixed, page scroll is disabled, pinch/drag-dismiss
gestures are suppressed, and taps/swipes remain available for story navigation.
This is intentionally a presentation behavior of the standalone Capsule, not a
host-only workaround. Hosts such as HTML Vault can then align their chrome and
scroll policy with the declared presentation instead of guessing.

### Phase 3: Evaluation

For each derived view, check:

- Does `capsule-root` remain sufficient with JavaScript off?
- Do slides/story cards introduce any facts absent from the reader/data layer?
- Are source-section references preserved?
- Does the output validate?
- Does mobile story feel native on iOS-sized viewports?
- Does desktop slides feel like a real one-screen presentation?
- Does Safe Preview remain useful?

### Phase 4: Graduation

Only graduate findings into the spec when repeated examples show the same need.
Likely candidates:

- stronger recommended `presentation_model.cards[]` fields
- validator warnings for declared presentations with no source traceability
- compiler fixture for `reader -> reader + reel`
- compiler fixture for `reader -> reader + slides`

## Current Judgment

The project is not over-scoped if the layers stay separate:

```text
Capsule = durable artifact contract
Cards = optional source model for presentation compilation
Renderers = replaceable compiler/host examples
Vault = workshop and custody surface
```

The scope creep begins only if the spec tries to prescribe every renderer detail
or if producers are expected to hand-author several polished views at generation
time. The safer path is to make Capsules reader-first and compiler-ready.
