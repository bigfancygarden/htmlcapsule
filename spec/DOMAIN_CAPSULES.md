# Domain Capsules — Named Schemas

**Status:** Open namespace. The Core spec defines the outer contract (manifest, data block, sealed convention, capabilities). This document defines named domain schemas that fit inside it.

A Domain Capsule is a regular Capsule whose `manifest.type` follows the `domain.<name>` convention and whose `capsule-data` block conforms to a published schema for that domain. The outer contract is identical to a Conversation Capsule or any other capsule. The difference is that consumers know what to expect inside the data block.

Domain Capsules are how the format absorbs specialist work (maps, datasets, code snapshots, contracts, implementation notes, design systems) without sprawling the Core spec. Each domain owns its own data-block schema. The Core stays small.

## Why named domains exist

Reading the data block of a Conversation Capsule is easy: it's a synthesis of a chat, structured around whatever sections the conversation produced. Reading the data block of an arbitrary Domain Capsule is harder. Without a named schema, every consumer has to reverse-engineer the producer.

The named-domain pattern fixes that. If `manifest.type` is `domain.implementation_notes`, a consumer knows:
- What fields will be in the data block
- What capabilities are likely declared
- What `ai_usage_guidance` rules apply
- How to render it usefully
- What it's *not* (it's not arbitrary unstructured notes)

The convention is open: anyone can declare a new domain. The catalog below is the set of domains the project ships with examples for.

## Naming convention

`manifest.type` for a Domain Capsule:

```
domain.<name>
```

Where `<name>` is a lowercase identifier, optionally with underscores. Examples:

- `domain.implementation_notes`
- `domain.design_system`
- `domain.map`
- `domain.dataset`
- `domain.deal`
- `domain.code_snapshot`

If the domain has internal subtypes, those are expressed inside the data block, not in the type string.

## Required fields beyond the Core

Every Domain Capsule MUST:

1. Declare `manifest.type` in `domain.<name>` form.
2. Conform to the published data-block schema for that name (this document, or a domain-specific spec referenced from here).
3. Include an `ai_usage_guidance` block in the data block with at least:
   - `allowed_tasks`: tasks an AI consumer is permitted to perform with this capsule
   - `restricted_tasks`: tasks an AI consumer should refuse
   - `preferred_language`: tone, register, or audience for AI output derived from this capsule

This is the acceptable-use clause aimed at the next model, not the next human. For Domain Capsules in regulated or high-stakes territory (legal, medical, financial, geospatial, mining), the `ai_usage_guidance` block is where you say "summarize this map, but do not estimate resources or imply economic viability."

## Initial domains

The project ships two initial named domains with canonical examples. Both are battle-tested patterns in the wild rather than theoretical proposals.

### `domain.implementation_notes`

**Purpose:** Preserve the gap between a spec and what actually got built. Capture the decisions an implementer (human or AI) made along the way so the next person picking up the work can re-engage without losing context.

**Origin:** The pattern was popularized by Thariq Shihipar's prompt: *"implement \<SPEC\> and while you do, keep a running implementation-notes.html file ... with decisions you had to make weren't in the spec, things you had to change, tradeoffs you had to make or anything else I should know."*

**Production path:** Almost always live-capture — maintained during the implementation, sealed when the work is handed off.

**Data block schema:**

```json
{
  "spec_reference": {
    "title": "string — what spec this implementation works against",
    "url_or_path": "string — link or path to the spec",
    "version": "string — version of the spec implemented against",
    "scope": "string — which part of the spec this capsule covers"
  },
  "implementation_summary": "string — short paragraph naming what was built",
  "design_decisions": [
    {
      "decision": "string — what was decided",
      "context": "string — what part of the spec was ambiguous or silent",
      "rationale": "string — why this choice",
      "alternatives_considered": ["string"]
    }
  ],
  "deviations": [
    {
      "spec_section": "string — what part of the spec was departed from",
      "deviation": "string — how the implementation differs",
      "why": "string — reason for the departure",
      "reversible": "boolean — can this be brought back into spec compliance later?"
    }
  ],
  "tradeoffs": [
    {
      "question": "string — what choice was being made",
      "options_considered": ["string"],
      "chosen": "string",
      "why": "string"
    }
  ],
  "open_questions": [
    {
      "question": "string — what the implementer wants the spec author to confirm or revise",
      "context": "string",
      "urgency": "low | medium | high"
    }
  ],
  "ai_usage_guidance": {
    "allowed_tasks": [
      "summarize the design decisions",
      "surface open questions for review",
      "identify high-risk deviations",
      "draft a revised spec section based on resolved decisions"
    ],
    "restricted_tasks": [
      "do not treat deviations as bugs without consulting the why",
      "do not auto-resolve open questions",
      "do not collapse tradeoff alternatives into a single recommendation"
    ],
    "preferred_language": "technical, plainspoken, calibrated about uncertainty"
  }
}
```

**Required capabilities:** `about`, plus at least one export. Recommended: `copy_as_markdown` (so the notes can be pasted into a spec-review tool) and `download_json`.

**Canonical example:** [`spec/examples/implementation_notes_example.html`](examples/implementation_notes_example.html).

### `domain.design_system`

**Purpose:** Package a living design system (tokens, components, usage notes) as a single portable HTML file. The capsule is the source of truth for design decisions that span a marketing site, an app, internal tools, and AI-assisted UI generation.

**Origin:** Pattern demonstrated by Thariq Shihipar in his *How I AI* podcast appearance — a `design_system.html` file passed between repos and projects, used as input to AI tools that need to know the visual language.

**Production path:** Usually compile (extracted from a repo or design tool) or hybrid (extracted then hand-edited). Updated as the design system evolves; each version is a new sealed capsule.

**Data block schema:**

```json
{
  "design_system_name": "string",
  "version": "string — semver of the design system itself, not the capsule",
  "tokens": {
    "colors": [{"name": "string", "value": "string", "usage": "string"}],
    "typography": [{"name": "string", "font_family": "string", "size": "string", "weight": "string", "line_height": "string", "usage": "string"}],
    "spacing": [{"name": "string", "value": "string", "usage": "string"}],
    "radius": [{"name": "string", "value": "string", "usage": "string"}],
    "shadows": [{"name": "string", "value": "string", "usage": "string"}]
  },
  "components": [
    {
      "name": "string",
      "purpose": "string",
      "variants": ["string"],
      "states": ["string"],
      "props_or_attributes": [{"name": "string", "type": "string", "default": "string"}],
      "usage_notes": "string",
      "do_not": ["string"]
    }
  ],
  "patterns": [
    {
      "name": "string — composition pattern (form layout, card grid, navigation, etc.)",
      "when_to_use": "string",
      "components_used": ["string"]
    }
  ],
  "ai_usage_guidance": {
    "allowed_tasks": [
      "generate new UI that uses these tokens",
      "compose new components from existing primitives",
      "suggest variant additions consistent with the existing system"
    ],
    "restricted_tasks": [
      "do not invent token values outside the published set",
      "do not deprecate components without flagging the breaking change",
      "do not generate marketing copy that contradicts the design system's tone notes"
    ],
    "preferred_language": "match the system's existing voice (specified separately if needed)"
  }
}
```

**Required capabilities:** `about`, `copy_as_json`, plus optionally domain-specific capabilities like `design.preview_component` or `design.copy_token` for interactive design system browsers.

**Canonical example:** *Forthcoming — pattern is shipped, formal example is the next concrete deliverable.*

### `domain.briefing`

**Purpose:** A single-page printable summary derived from a longer source capsule. Designed to fit on one 8.5×11 sheet in print preview. The thing you'd hand a colleague, a stakeholder, or your future self when the full source is too much to read but the conclusions still need to travel.

**Origin:** The pattern of "long source plus short forked briefing" emerged from real use. Some capsules are inherently long (transcripts, dialogues, detailed research, full domain dumps). Forcing them to fit on a page would damage them. The cleaner move is to keep the source long and produce a separate, sealed one-pager that points back to it.

**Production path:** Almost always *fork* — derived from a parent capsule by AI summary, manual editing, or a compiler step. The briefing carries explicit lineage so the chain back to the source is honest.

**Layout convention:** Single-page letter (8.5×11). Print preview is the source of truth. Two-region design:
- **Top half**: title, lede, key points (the "in one breath" version)
- **Bottom half**: supporting detail, sources, caveats, parent capsule reference

Black-and-white readable. Color is decoration. Soft cap of ~600–900 words of visible text.

**Data block schema:**

```json
{
  "lineage": {
    "parent_uuid": "string — uuid of the source capsule (canonical identifier as of Core v0.1.5)",
    "parent_title": "string — human-readable for the briefing's own use",
    "parent_artifact_id": "string — optional, the source's legacy slug if it had one",
    "derivation_method": "ai_summary | manual_edit | compiler | hybrid",
    "derivation_note": "string — what was kept, what was cut, why"
  },
  "title": "string — short, the one thing to take away",
  "lede": "string — one paragraph, the briefing in one breath",
  "key_points": [
    {"point": "string — the takeaway", "detail": "string — short supporting context (optional)"}
  ],
  "supporting_facts": [
    {"label": "string", "value": "string"}
  ],
  "caveats": ["string"],
  "sources": [
    {
      "label": "string — usually the parent capsule",
      "url_or_path": "string",
      "role": "parent | external_reference | regulatory_source"
    }
  ],
  "ai_usage_guidance": {
    "allowed_tasks": [
      "redistribute as a stakeholder briefing",
      "summarize further",
      "extract the parent reference for deeper context"
    ],
    "restricted_tasks": [
      "do not re-derive substantive content beyond what's in the briefing",
      "do not treat the briefing as the full source of truth — check parent for detail",
      "do not strip the parent reference"
    ],
    "preferred_language": "concise, direct, scannable"
  }
}
```

**Required manifest fields beyond Core:**
- `type: "domain.briefing"`
- `lineage.parent_capsule_id` is required (a briefing without a parent is just a short capsule)
- Optional but encouraged: `layout: "single_page_letter"` to signal the print-ready convention to consumers

**Required capabilities:** `about`, plus at least one export. Recommended: `print_to_pdf` (most direct use case), `copy_as_markdown` (so the briefing can be re-pasted into other tools).

**Canonical example:** [`spec/examples/briefing_example.html`](examples/briefing_example.html) — a one-page printable briefing on TN visa eligibility under USMCA, demonstrating the fork pattern (a briefing distilled from a longer source conversation).

### `domain.exploration_map`

**Purpose:** Package a single thematic map of a mineral exploration project as a portable, print-ready deliverable. The capsule is the atomic unit of a map that would appear in a news release, investor deck, technical report exhibit, or regulatory filing — a bounded geographic view of a project area, frozen at a moment, attributable and versioned.

**Origin:** Mineral exploration produces a recurring set of map deliverables: project location maps, geology overlays, drill plans, geochemistry anomaly maps, remote-sensing alteration maps. These get emailed as PDFs of unknown provenance, embedded in slide decks, printed for field use, and forwarded to geologists, investors, and regulators. Each one is a bounded snapshot of specific layers from a spatial database — exactly the capsule contract.

**Production path:** Compiler — a Python build script queries PostGIS for a project's frozen snapshot geometry and relevant thematic layers, renders everything to inline SVG using equirectangular projection, and assembles a validator-clean capsule. The script is deterministic: same inputs, same output. `generator.kind: "compiler"`.

**Layout convention:** 8.5×11 portrait, print-targeted. The page contains: title block (top), map canvas (center), legend + scale bar + north arrow (sidebar or footer), caveats strip (bottom). Screen view adds a sticky toolbar outside the printable area for export controls; hidden at `@media print`.

**Map types:** Internal subtypes expressed via `map_type` in the data block — not separate domains. Four vector-primary types (`project_location`, `geology`, `drill_plan`, `geochem`) share the `layers[].features_geojson` shape. Two raster-primary types (`mineral_spectral`, `geophysics`) use `layers[].raster_data_uri` instead. A single layer carries one or the other, never both.

| `map_type` | Primary layers | Typical source |
|---|---|---|
| `project_location` | Claims outline, surrounding claims, roads, towns, topo grid | Provincial claims tables, NTS grid, infrastructure |
| `geology` | Bedrock geology polygons, project outline | Geological survey datasets |
| `drill_plan` | Collar points, traces, significant intercepts, project outline | Drillhole database + assays |
| `geochem` | Sample points (proportional/classified symbols), project outline | Geochem survey results |
| `mineral_spectral` | ASTER/remote-sensing index heatmap, project outline | S2 grid cells or rasterized COGs |
| `geophysics` | Mag/EM/gravity grids or contours, project outline | Geophysical survey grids |

**Data block schema:**

```json
{
  "map_type": "project_location | geology | drill_plan | geochem | mineral_spectral | geophysics",

  "project": {
    "name": "string — project name",
    "operator": "string — company operating the project",
    "ticker": "string — optional, e.g. 'CSE: LP'",
    "jurisdiction": "string — province/state/country",
    "nts_sheets": ["string — NTS map sheet references"],
    "commodities": ["string — target commodities, e.g. 'Au', 'Cu'"],
    "area_ha": "number — total project area in hectares",
    "snapshot_id": "string — mintel project_version ID or equivalent, ties to source-data provenance"
  },

  "extent": {
    "bbox_wgs84": {
      "min_lon": "number", "min_lat": "number",
      "max_lon": "number", "max_lat": "number"
    },
    "center": { "lon": "number", "lat": "number" },
    "crs": "string — always 'EPSG:4326' for storage; note projection used for rendering",
    "projection": "string — rendering projection, e.g. 'equirectangular'",
    "scale_denominator": "number — intended print scale (valid only at print size)"
  },

  "layers": [
    {
      "name": "string — human label, e.g. 'Property Claims'",
      "type": "polygon | point | line | grid",
      "source": "string — provenance: table name, dataset, or file the data came from",
      "source_date": "string — ISO 8601 date of the source data snapshot",

      "features_geojson": "GeoJSON FeatureCollection — for vector layers (polygon, point, line)",
      "raster_data_uri": "string — data:image/png;base64,... — for grid/raster layers (mineral_spectral, geophysics)",
      "raster_bounds": "object — { min_lon, min_lat, max_lon, max_lat } — georeferencing for raster_data_uri",
      "raster_value_range": "object — { min, max, unit, index_name } — what the colors represent",

      "style": {
        "fill": "string — CSS color",
        "fill_opacity": "number",
        "stroke": "string — CSS color",
        "stroke_width": "number",
        "symbol": "string — optional, for point layers: 'circle', 'triangle', 'cross', etc.",
        "symbol_size_field": "string — optional, field name for proportional symbols",
        "color_field": "string — optional, field name for classified coloring",
        "color_ramp": ["string — CSS colors for classified/graduated rendering"]
      },

      "visible": "boolean — whether this layer is rendered (allows carrying data for export without display)",
      "z_order": "number — draw order (lower = drawn first / underneath)"
    }
  ],

  "legend": [
    {
      "label": "string",
      "layer_ref": "string — matches a layer name",
      "swatches": [
        { "label": "string", "fill": "string", "stroke": "string" }
      ]
    }
  ],

  "title_block": {
    "title": "string — map title",
    "subtitle": "string — optional, e.g. area/district name",
    "figure_number": "string — optional, e.g. 'Figure 1'",
    "date": "string — map production date",
    "author": "string — person or system that produced the map",
    "notes": "string — optional, brief methodological note"
  },

  "scale_bar_segments_m": ["number — distance labels for the scale bar"],

  "caveats": [
    "string — e.g. 'Claim boundaries as of 2026-05-15. Do not use as legal evidence of tenure.'",
    "string — e.g. 'Scale valid only at 8.5×11 print size.'",
    "string — e.g. 'ASTER indices are relative anomaly indicators, not assay values.'"
  ]
}
```

A layer carries **either** `features_geojson` (vector) **or** `raster_data_uri` + `raster_bounds` (raster), never both. This acknowledges that mineral spectral and geophysics data are fundamentally grid-shaped — coercing a 24M-row S2 cell grid into GeoJSON polygons would bloat file size for no benefit. The build script pre-renders the grid to a PNG and embeds it as a data URI, georeferenced by `raster_bounds`.

**Two versioning axes:**
- **Source-data provenance:** `project.snapshot_id` ties the map to the specific frozen snapshot from the source database (e.g., a mintel `project_version` ID). This answers "which version of the claims data was this map built from?"
- **Capsule-to-capsule lineage:** When a map is reissued (new claims staked, new drill results), the new capsule records the previous capsule's UUID in `manifest.parents[]` per Core rule. This answers "what's the history of this deliverable?" without consumers needing access to the source database.

**File size considerations:** Inline GeoJSON for a busy region (hundreds of claim polygons + geology + infrastructure) can exceed 1 MB quickly — and a real production exploration_map capsule has been observed at 13.7 MB (47 polygons + chrome, F20). Build scripts should apply polygon simplification (Douglas-Peucker or similar) to context layers that don't need survey-grade precision. The 20 MB hard cap (raised from 15 MB in spec v0.3.3) gives runway; the 15 MB soft warning flags email-attachment compatibility. Leaner capsules open faster and travel better.

**Rule 12 carve-out — required image fallback for the geometry container.** Maps render polygon and raster geometry into a runtime-drawn SVG. Per spec §2.3 "Carve-out for visualization geometry" (v0.3.3), the compiler MUST embed a static raster rendering of the map as a `data:image/png;base64,…` fallback inside the same container, hidden when the interactive SVG hydrates. The build pipeline already produces this raster (it's the same image that would ship as the PDF/JPEG deliverable in non-capsule workflows), so the cost is one extra `<img>` element and a one-line visibility toggle in the runtime. Without the fallback, the map renders as a blank container in iOS Files preview, email-client previews, search indexers, and text-only LLMs ingesting the HTML — environments where Rule 12's intent matters most. Recommended structure:

```html
<figure class="map-container" aria-label="{project name} — {map type}">
  <img id="map-static" src="data:image/png;base64,..." alt="Static rendering of the map" class="map-fallback">
  <svg id="map-svg" viewBox="0 0 1000 1294" hidden></svg>
</figure>
<noscript><style>#map-svg { display: none !important; }</style></noscript>
```

The compiler should generate the PNG at the same projection and bounding box as the SVG so the two renderings are visually equivalent; the SVG's interactive features (hover, layer toggle, click) are pure progressive enhancement on top.

**Required capabilities:** `about`, `print_to_pdf`, `copy_as_json`, `download_json`. Optionally: `map.export_geojson` (if the capsule exposes a GeoJSON download of its vector layers). Do not declare interactive capabilities like `map.zoom_to_layer` or `map.pan` unless the runtime genuinely implements them — most print-targeted maps are static SVG renders where zoom and pan would be dishonest.

**Scale disclaimer:** Because screen zoom changes the effective scale, capsules should display a visible note: "Scale 1:50,000 — valid at 8.5×11 print size." The `scale_denominator` field records the intended print scale; consumers should not assume it holds at arbitrary screen zoom levels.

**Canonical example:** *In progress — first working example targeting a mintel project with `map_type: project_location`.*

### `domain.compositor`

**Purpose:** Preserve a composed document artifact — a Compositor document (authored layers, pages, templates, design tokens, keyed data layers) rendered to a print / slide / reader target — as a sealed capsule that re-opens in the producing editor as a complete working object.

**Producer and schema ownership:** the compositor compiler (external producer; registered 2026-07-06, F33 in RESEARCH.md). The authoritative data-block schema lives in the producer repo (`compositor/packages/capsule/src/seal.ts` — the `CompositorCapsuleData` type); this entry records the shape and the boundary, not a frozen copy. This is the registry's first externally-owned compiler domain whose producer CI validates every sealed example against the reference validator as a merge gate (F35).

**Data block (summary):**

| Field | Type | Notes |
|---|---|---|
| `compositor_document` | object | The canonical content model — "a clean recipe": authored layers, pages, templates, tokens, and *keyed data-source references, unrewritten* |
| `sealed_sources` | object | The §4.1.2 convention's reference instance: resolved GeoJSON FeatureCollections per sourceKey, inline-sourced layers excluded; reopen resolves from this block alone with an empty fixture map |
| `render_snapshot` | object | Output-target snapshot: frame, canvas/asset dimensions, DPI, per-source resolution statuses |
| `context_packet` | object | Bounded consumer/LLM handoff summary (layer stack, feature counts, per-source attribute digests, bounds) — summary-first so an agent can inspect the capsule without enumerating raw GeoJSON |
| `ai_usage_guidance` | object | Required per this document. The geospatial/mining guardrail applies: "summarize the map, but do not infer mineral value or economic viability from map geometry" |

**Manifest notes:** `type: "domain.compositor"`, `generator.kind: "compiler"`, `hash_scope: "data+manifest"` as a deliberate architecture (JSON is truth, HTML is projection — the reopen path never reads the HTML surface; F34), `presentations[]` declared per output target (reader always; slides / print / letter when composed for them).

**Boundary:** not [`domain.exploration_map`](#domainexploration_map) — that is a map-first, single-purpose artifact, while a compositor document is a composed multi-layer print/slide/reader artifact in which maps are one layer kind. Not a `domain.dataset` — the sealed payloads are resolution context for the document, not the artifact itself.

## JS-off fallback guidance per domain (added v0.3.6)

Per `spec/CAPSULE_SPEC.md §2.3.1` (the graceful-degradation principle), every domain capsule SHOULD have a defined behavior in JS-off / iOS-QuickLook-preview environments. For most domains the answer is "the static HTML *is* the substance — no extra work needed." For a few (visualization-heavy, interactive-runtime, or media-playback domains) producers need to bundle a static or media-native representation alongside the runtime one.

| Domain | JS-off fallback shape | Notes |
|---|---|---|
| `domain.implementation_notes` | None required — content is the static HTML | Already document-shaped (decisions, deviations, tradeoffs, open questions); the runtime adds no substance, only export buttons |
| `domain.design_system` | None required — content is the static HTML | Tokens, components, patterns, AI usage constraints all render statically; live component preview rendering is enhancement, not substance |
| `domain.briefing` | None required — content is the static HTML | One-page summary forks are inherently document-shaped |
| `domain.exploration_map` | Image-fallback for geometry (per `CAPSULE_SPEC.md §2.3` worked example) | Static `<img>` rendering of the map's vector content, hidden by runtime when the interactive SVG hydrates; `<noscript>` block ensures the image stays visible if JS is off |
| `domain.compositor` | None required — the rendered document markup is static HTML/SVG in `capsule-root` | Substance is intact without JS; the runtime adds toolbar / About / download affordances only. Reopen-in-editor reads the data block, never the HTML (F34) |
| `domain.midi_stem` (idea queue) | **Recommended: bundled rendered audio mix as `<audio controls>`** + static stems list (one row per channel with instrument label + program + note count) + static manifest panel | A symbolic-only capsule has no native sound without JS; the rendered mix is the preview-mode substance. capsule-midi v0.2.0 currently does NOT bundle the mix (Tier 1 sound only); v0.3.0 Tier 2 / Tier 3 work will add it. Until then, capsule-midi capsules are *runtime-only* on iOS QuickLook (the `<noscript>` warning explains this and directs the user to open in Safari) |
| `domain.song` (idea queue) | **The embedded MP3 already IS the fallback.** Native `<audio controls>` works without JS | No extra producer work — the audio element renders and plays natively in iOS QuickLook. Metadata (personnel, role on album, covers, critical reception, etc.) is in the static HTML. The interactive runtime adds export-provenance + capsule-management; substance is intact without it |
| `domain.photo` (idea queue) | **The image itself is the fallback.** Static `<img>` renders without JS | No extra producer work. Metadata table (who/where/when/why, EXIF, source negative, etc.) is in the static HTML. The runtime adds region-highlight / copy-metadata / face-tag toggles — enhancement, not substance |
| `domain.music_stems` (idea queue, parent) | Pre-rendered mix as `<audio controls>` + static stems list | Same shape as `domain.midi_stem` since this is the multi-modal parent. When this graduates (audio stems + MIDI tracks + effects combined), the producer ships both the per-stem audio AND a pre-rendered combined mix; the JS-off path uses the mix; the runtime adds per-stem mute/solo/effects |

**Producer guidance.** When a domain has a non-trivial fallback shape (the music / map / photo / data-visualization cases), producers SHOULD also declare what they've bundled in the optional `manifest.fallbacks` section (see `CAPSULE_SPEC.md §3.2.1`). This is descriptive only — the actual fallback content must be in the static HTML per Rule 12 — but it lets consumers (registry viewers, downstream tools, validators) discover the available fallback paths without scraping the rendered HTML.

## How to propose a new domain

A new domain earns a place in this document when:

1. The pattern exists in the wild with at least one working example.
2. The data-block schema is concrete (named fields, named types).
3. Consumer guardrails have been thought through — either via `ai_usage_guidance` (structured, opt-in, in the `x-` extension namespace if not load-bearing), `caveats[]` (prose, always available), or the `description` field. The mechanism depends on the domain; the requirement is that the producer has considered what consumers should and shouldn't infer.
4. The boundary against neighboring domains is clear (a `domain.dataset` is not a `domain.code_snapshot` even if it ships data alongside a query).

Proposals can be drafted as a section in this document. The bar isn't "comprehensive coverage of every edge case" — it's "concrete enough that two independent implementers would produce structurally compatible capsules."

## Idea queue — domains noodled on but no working example yet

Sits below the proposal bar above. Things the project (or its users) have thought about that haven't yet earned a slot in "Initial domains" because no working capsule exists. The spec discipline says **prototype first, schema later** — these entries live here until someone produces an example that pushes the idea into the formal proposal flow.

When something graduates from this queue to a real domain, move the entry up to "Initial domains" with a full schema. If an idea sits here long enough without empirical pressure and seems unlikely to materialize, delete the entry — the queue isn't a backlog promise.

### `domain.music_stems`

**Idea (2026-05-21):** Hold the stems of a song / loop / sketch in a single capsule, with mute/solo per stem, optional Web Audio API effects (gain, EQ, reverb, filter), MIDI tracks alongside audio, and the friend-rework workflow as the load-bearing use case.

> **2026-05-22 status note.** Two producer projects are prototyping specializations of this parent idea: [`domain.midi_stem`](#domainmidi_stem) (capsule-midi, symbolic-only, no audio bundled — working v0.2.0 implementation) and [`domain.song`](#domainsong) (Shasta, audio-primary — in progress). The parent `domain.music_stems` entry — combined audio stems + MIDI tracks + effects + friend-rework workflow — remains an idea-queue entry pending a producer that takes on the combined shape. Likely path: graduate `domain.midi_stem` and `domain.song` first when their producers ship publicly-validated capsules; revisit `domain.music_stems` if a future producer wants the combined shape.

**Provenance of the idea:** Maintainer surfaced it after thinking about Studio One (PreSonus DAW) workflows. DAW projects have MIDI tracks, audio tracks, effects, VSTs — and the maintainer used to swap versions with friends: *"I would get a version from them and rework it or they'd take a version from me and steal the drums or a loop or something and rework it."* A capsule for stems would carry that exchange shape without each party needing the same DAW or having compatible plugins.

**Why it fits the format:**

- Embedded audio via `data:` URIs is empirically tested (F14 photo capsules; F16 image-grounded conversation capsules with embedded media). The CSP already permits `media-src data:` for audio (the feature-driven loosening landed earlier).
- The interactive runtime (mute, solo, gain, effects toggles) fits cleanly as "interactive archive" affordances per spec §2.3 — the stems *are* the substance in the HTML; the tools query and transform them at runtime but don't generate them. JS-off litmus passes: the listener sees the stem list, credits, lineage notes, and titles even without playback.
- `parents[]` lineage maps perfectly onto friend-rework workflows. A folder of `.html` capsules with `parents[]` references becomes a traversable history of who-forked-what. The provenance lives in the bytes; visualization is a separate tool.

**Honest constraint:** The 20 MB hard cap scopes this to *sketches, loops, and short songs at lossy quality* (MP3 or Opus at ~128 kbps). Full-length studio multitracks at WAV quality don't fit. That's appropriate — the format is for the *exchange* shape ("here's my version, take what you want"), not the master-recording shape. If empirical pressure ever pushes toward higher-fidelity full-length tracks, a sibling `domain.music_stems.studio` with a different distribution model (separate-file stems + manifest in a `.zip`) could split off.

**Rough data shape (sketch, not normative):**

```json
{
  "track": {
    "title": "…", "tempo_bpm": 120, "key": "Cm",
    "time_signature": "4/4", "duration_seconds": 240,
    "exported_from": "Studio One 6.5"
  },
  "stems": [
    {
      "name": "Drums",
      "audio_data_uri": "data:audio/opus;base64,…",
      "default_gain_db": 0, "default_pan": 0, "default_mute": false,
      "encoding": { "codec": "opus", "bitrate_kbps": 128, "sample_rate_hz": 48000 }
    }
  ],
  "midi_tracks": [
    {
      "name": "Melody (MIDI source)",
      "midi_data_uri": "data:audio/midi;base64,…",
      "default_instrument": "piano",
      "note": "Recipient drops into their own DAW with their own instrument"
    }
  ],
  "effects": [
    { "name": "Reverb",  "type": "convolution", "default_enabled": false, "applies_to": "*" },
    { "name": "Lowpass", "type": "biquad",      "default_enabled": false, "applies_to": "Vocals" }
  ],
  "credits": [{ "role": "Drums", "name": "…", "lineage_note": "from v1" }],
  "rework_note": "Took v2's drums and bassline, rewrote the melody.",
  "license": "CC-BY-NC-SA 4.0"
}
```

**Recommended capabilities if it ever ships:** `about`, `copy_as_json`, `download_json`, `download_capsule`, plus domain-scoped `audio.play`, `audio.mute_solo`, `audio.gain`, `audio.effects`, and optionally `audio.export_mix` (uses `OfflineAudioContext` to render the current mute/gain/effect state to a single mixed audio file the recipient can download). When this graduates, the `media.*` family formalized in `CAPSULE_SPEC.md §5.1.2` (v0.3.6) supersedes the ad-hoc `audio.*` names sketched above — use `media.play` / `media.pause` / `media.stop` / `media.stems.mute` / `media.stems.solo` / `media.stems.set_volume` / `media.audio.download_mix` instead.

**No-JS preview pattern (per `CAPSULE_SPEC.md §2.3.3`, added v0.3.7; organized under §2.3.2's 5-tier framework in v0.3.8).** For the short-loop / sketch scope this domain targets, the natural no-JS preview is a small set of pre-rendered alt mixes — `mix_full`, `mix_no_drums`, `mix_no_bass`, `mix_piano_only`, or whatever the workflow calls for — each as an `<audio controls>` element selectable via radio-button tabs. Watch the size budget: at Opus 96 kbps each ~3-minute variant is ~2 MB, so a 6-alt set fits in ~12 MB (well under the 20 MB cap). Track list, credits, lineage notes, and the workflow's `rework_note` all render statically alongside.

**What's missing to graduate:** A working example. Maintainer should pick a short loop or sketch they have lying around, hand-author or LLM-author a single capsule with stems + a mute/solo/play runtime, and see what breaks (file size, audio API quirks across browsers, mobile playback, transport sync across stems). If it works and someone forks it under `parents[]`, this entry moves up to "Initial domains" with a full schema and at least one canonical example.

---

### `domain.midi_stem`

**Idea (2026-05-22):** Symbolic-only multi-track music capsules. Take a `.mid` file, parse channels into symbolic stems, render a piano roll, synthesize playback via Web Audio at runtime (no bundled audio). Per-stem mute/solo, assignable patches (11 waveform/ADSR/filter recipes), tempo scaling, loop-by-bar, click-to-seek, remix-provenance export.

**Provenance of the idea:** Producer project [`capsule-midi`](https://github.com/bigfancygarden/capsule-midi) v0.2.0 (2026-05-22). Pipeline: pure-stdlib SMF parser → channel grouping & note pairing → Core-conforming manifest assembler → 5-block HTML template builder with embedded MIDI as `data:audio/midi;base64,…` URI. Validates 26/26 against the reference validator on synthetic fixtures and on two real-world MIDIs (Mozart Lacrimosa, 10 components, 1,225 notes, 171.69 s; "Bad Bad Thing" 1999 pop, 8 components, 629 notes, 44.08 s).

**Why it fits the format:**

- Symbolic representation is dense: a 10-component, 1,225-note, ~3-minute symbolic piece encodes at ~10 KB of structured JSON + the source `.mid` (~30 KB base64) = ~40 KB before UI. The full DAW-view capsule is ~220 KB. Well under the 20 MB cap; can scale to symphonic-length works.
- The "interactive archive" pattern from spec §2.3 holds cleanly: lanes + manifest + remix-export panel pre-render statically (Rule 12 passes); the canvas piano roll + Web Audio synth are enhancement layers the runtime adds.
- `parents[]` lineage references composition (e.g., the Mozart Lacrimosa capsule cites `composition:wikidata:Q193326` as a v5-UUID-namespaced parent). **First empirical pressure on the parked `derived_from[]` field** for non-capsule parents — see Q4 in `capsule-midi/FEEDBACK.md` and the upcoming Appendix E.11 graduation.
- Capability namespace surfaces a multi-track-media pattern: `media.stems.mute`, `media.stems.solo`, `media.stems.set_patch`, plus the universal `export.remix_provenance` primitive. See `capsule-midi/FEEDBACK.md` Q2 + Q3 for namespace-formalization asks against the spec.

**Distinction from `domain.music_stems`:** Symbolic-only — *no audio data is bundled*. The Web Audio synth produces sound from MIDI events at playback time. Trade-off: tiny files (200 KB for orchestra; would be ~10 MB if audio-rendered) but synth-quality timbre. Bundled-soundfont and bundled-audio-stems tiers are queued for capsule-midi v0.3.0.

**What's missing to graduate:** First publicly-validated capsule shipped at a stable URL (most likely on `htmlcapsule.org/examples/` or via MinDev). Also: resolution of `capsule-midi/FEEDBACK.md` items Q1 (this entry — formal schema graduation), Q2 (`media.stems.*` namespace), Q3 (`export.remix_provenance` payload shape), and Q4 (`derived_from[]` graduation from Appendix E.11). Schema is sketched in [`capsule-midi/README.md`](https://github.com/bigfancygarden/capsule-midi/blob/main/README.md#domain-schema--domainmidi_stem).

---

### `domain.song`

**Idea (2026-05-22):** Audio-primary song capsules. Embed a rendered MP3 (or per-stem MP3 set) alongside metadata (title, artist, album, release year, personnel, role on album, covers, critical reception, live history, source / license). Playback uses `<audio>` element with the bundled `data:audio/mpeg;base64,…` URI. Optional per-stem control if multi-stem (mute/solo). Optional remix-provenance export referencing time-ranges.

**Provenance of the idea:** Producer project **Shasta** (in progress, separate repo). First experimental capsule shipped during the htmlcapsule landing-page exploration arc: McCartney/Wings "Nineteen Hundred and Eighty-Five" capsule (private, copyright-laden — see [F26](../RESEARCH.md#f26-core-spec-accommodates-10-mb-domain-specific-media-capsules-without-rule-changes)). The song-capsule pattern was the seed; Shasta is the formal producer project building it out.

**Why it fits the format:**

- Audio as `data:audio/mpeg;base64,…` is empirically tested at the 7.6 MB MP3 / 10 MB capsule scale (F26). CSP needs `media-src data:` (single-line addition to default recipe).
- `<audio controls>` element with `data-capsule-action="media.play_audio"` marker satisfies Rule 7; transport buttons (play/pause/stop) are declared capabilities each backed by markers.
- `parents[]` lineage references the composition + the recording (when distinct). The recording itself may carry an additional reference to the album / label / release identifier. Same empirical pressure on `derived_from[]` as `domain.midi_stem` — every song capsule has non-capsule parents (composition, recording, album).
- Wikipedia / MusicBrainz / Discogs / Wikidata identifiers slot naturally into `derived_from[]` once the field graduates.

**Distinction from `domain.music_stems`:** Audio-primary — *a single rendered MP3 (or set) is bundled as inline data*. The friend-rework workflow of `domain.music_stems` is out of scope; the song capsule is a *listening + provenance* artifact, not a *remix-and-rework* artifact.

**What's missing to graduate:** Shasta ships a working capsule + validator pass; coordination with `derived_from[]` graduation; either an open / permissively-licensed song corpus or a clean private-by-default story. Schema sketched per the song-capsule experiment in F26.

---

### `domain.photo`

**Idea (2026-05-22):** Single-image artifacts. Embed one (or a small set of) photograph(s) as inline `data:image/...;base64,…` URI alongside structured metadata: who's in the photo (face tags, names, ages), where it was taken (place, GPS, event), when (date / approximate era), provenance (camera, photographer, original file hash, source negative if scanned). The "family photo + the story behind it" shape.

**Provenance of the idea:** Producer project **capsule-photo** (new, 2026-05-22; separate repo). Use case: family-photo preservation where the *context around the photo* (who, where, when, why) is just as fragile as the image bytes and tends to die with the people who knew. A capsule packages both into one self-contained, sealed, portable artifact that survives the storage medium.

**Why it fits the format:**

- Photos as `data:image/jpeg;base64,…` are inline-friendly; the existing CSP allows `img-src data:` (Rule 4 supplementary guidance already specifies this for QR codes — same primitive). A modest family photo at 4-8 MP and ~80% quality is 0.5-2 MB; well under the 20 MB cap.
- The pre-rendered content rule (Rule 12) is easy for photo capsules: the image and its metadata table are static HTML; runtime adds enhancement (zoom, tagged-region highlights, copy structured metadata).
- `parents[]` lineage for photo capsules has interesting semantics: a *digitized* photo's parent might be a film negative or print; a *cropped / edited* photo's parent is the original capsule. People-and-place references (Wikidata person/place IDs, GEDCOM individual IDs) belong in `derived_from[]` once graduated — same empirical pressure point as MIDI/song.

**Likely capability vocabulary:** `about`, `copy_as_json`, `download_json`, `download_capsule`, `print_to_pdf`, `image.download` (download the embedded photo), `image.copy_metadata` (clipboard-friendly structured-metadata export), possibly `image.regions.highlight` (toggle visibility of face/region overlays). Not in the `media.*` family because photos aren't time-based — `image.*` is the natural sibling namespace.

**No-JS preview pattern (per `CAPSULE_SPEC.md §2.3.3`, added v0.3.7; organized under §2.3.2's 5-tier framework in v0.3.8).** Photo capsules fit the no-JS-interactivity techniques particularly well: the image itself renders without JS (native `<img>`), and **radio-button tabs** can give readers no-JS view-switching between "Photo / Metadata / EXIF / Location / Provenance" without any runtime. **Checkbox layer toggles** can show/hide tagged face regions or location overlays on top of the static image. The interactive runtime adds copy-metadata-to-clipboard and similar conveniences; the substance is intact without it. This is the cleanest fit in the four-producer family for demonstrating the v0.3.7 no-JS techniques in anger.

**Honest constraint:** the 20 MB cap scopes this to *standalone-photo* shape. An album-of-many-photos would need either per-photo capsules with `parents[]` chains pointing at a parent "album" capsule, OR splitting at the storage layer. Either is fine; the format doesn't try to be a photo library.

**What's missing to graduate:** capsule-photo ships a working capsule + validator pass; canonical schema sketched in the producer project's README; coordination with `derived_from[]` graduation; a privacy posture (most family photos are private by default — `privacy.visibility: "private"` per-capsule, with the `private` value already supported by the validator).

## What this document is not

- Not exhaustive. Many domains the format could serve aren't listed yet (legal contracts, scientific datasets, medical records, financial filings). They get added when there's a working example and a thought-through schema.
- Not a closed catalog. Anyone can declare a new domain using the naming convention. This document lists the ones the project itself ships examples for.
- Not a substitute for the Core spec. Every Domain Capsule still must conform to all twelve Core rules. The domain schema sits inside the data block; the outer contract is unchanged.
