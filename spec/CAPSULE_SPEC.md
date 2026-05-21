# Capsule Spec v0.3.4 (Core currently v0.3.0)

> **Looking for the short version?** [`CAPSULE_CORE.md`](../CAPSULE_CORE.md) is one page, twelve rules, designed to be pasted into an LLM prompt. This document is the full specification for implementers — format definition, validation rules, security model, response protocol, registration workflow. If you're just trying to produce a capsule, the Core is enough.

> **Inspecting a served capsule.** To review or validate a capsule hosted at a URL: prefer the **in-capsule "Download capsule" button** if the capsule declares the `download_capsule` capability (§5.1.1) — that's the author's intended export path. Otherwise, fetch the raw file directly: `curl -O <url>` or, in a browser, right-click the link → **Save Link As**. **Do not use Save Page As → Webpage, Single File (.mhtml)** — Chrome and other Chromium browsers wrap the artifact in an MHTML envelope and extract inline `<style>` and `<script>` blocks into separate MIME parts (look for `cid:...@mhtml.blink` URLs in the result). This produces a degraded copy that fails Rules 1, 2, and 3 even when the underlying capsule is fully spec-compliant. A directory listing also isn't the capsule — the capsule is the linked `.html` file itself.

> **Naming note (v0.2).** This format was previously called "Artifact Capsule." It was shortened to "Capsule" in 2026-05 to avoid collision with Anthropic's product term ("artifact" = a working canvas in Claude) and to land the sealing metaphor in one word. The schema field names were renamed to match: `capsule_id` and `capsule_version` are the canonical v0.2 names. The legacy v0.1 names `artifact_id` (with `artifact:` prefix) and `artifact_version` remain accepted by the validator under v0.2 compatibility — new capsules should use the canonical names. See [`../EXPLORATION.md`](../EXPLORATION.md#naming) for the full reasoning.

> **v0.3 changes (2026-05-19).** Added optional `parents` field for hard provenance — a capsule records the UUIDs (with denormalized titles) of upstream capsules it was forked from. Deprecated `capsule_id` (slug) — redundant with `title` and not unique enough to serve as a reference, so the canonical `uuid` is the only identifier going forward; still accepted in v0.3, planned for removal in v0.4. Deprecated the `related` array — unused soft-association field that invited fabricated edges; hard provenance now lives in `parents`, soft associations belong in capsule prose.

> **v0.3.1 changes (2026-05-19).** Doc-only patch. No schema or validator changes. Tightened §9.1.1 into a normative "Content Hash Recipe" with a verifiable test vector — `sha256:3dcff3f89736e2554b3f077dbff063f5400c682d470ffa5125fa4bdd3c652ef8` for the documented minimal manifest+data, so a new compiler can confirm its implementation by re-derivation. Added an "Inspecting a served capsule" preamble flagging that Chrome's Save Page As → MHTML destroys the capsule contract. Cross-reference added from §3.2 Integrity to §9.1.1.

> **v0.3.2 changes (2026-05-19).** Added the `download_capsule` standard capability — an in-capsule button that DOM-serializes the document and triggers a `.html` download, giving recipients a clean export path that doesn't rely on Chrome's broken Save Page As flow. New §5.1.1 spells out the implementation pattern (no network, rule-2 clean) and the one subtle caveat: browsers normalize HTML during DOM serialization, so capsules declaring `download_capsule` SHOULD pair it with `hash_scope: "data+manifest"` or `"data_only"` rather than `"full_document"`. Validator capability marker updated.

## 1. Overview

A Capsule is a profile of HTML. It is not a new file type, browser standard, or protocol. It is a set of conventions that define what a self-contained HTML document must contain in order to function as an **atomic unit of preserved work**.

A capsule packages a bounded snapshot of data, a machine-readable manifest, embedded assets, interface logic, provenance metadata, and export mechanisms into a single file. It may be produced from any structured source — a private database query, an LLM conversation, hand-authored content, output from a domain tool — and is designed to be opened, reviewed, interacted with, archived, and (optionally) shared without requiring live access to the original source.

The distinction from an ordinary HTML page: a random HTML report may look nice but has no stable machine-readable contract. A Capsule guarantees a manifest, a declared data snapshot, provenance, versioning, and export behavior — all in predictable locations inside a standard HTML file. The same outer contract serves recipes, research notes, decision briefs, journal entries, design specs, log entries, learning capsules, and the synthesis that comes out of LLM conversations. Domain-specific content lives in the data block; the envelope stays consistent.

### 1.1 Four Layers

The complete system is best understood as four independent layers. Only the third — the artifact itself — is standardized by this spec.

| Layer | Purpose | Standardized? |
|---|---|---|
| **1. Private authoring system** | Source of truth. Evolves freely. May be a database, file collection, note system, or custom store. | No — your choice |
| **2. Compiler / export pipeline** | Selects, redacts, normalizes, and packages a snapshot. May be implemented in any language. | Behavior described (Section 9.1); implementation free |
| **3. Portable runtime artifact** | The `.html` capsule itself. What this spec defines. | **Yes — this document** |
| **4. Optional format profile** | This spec, plus the response/import contract for feedback loops. | Yes (this document + companion schemas) |

The compiler can change without breaking capsules. Capsules can outlive their compilers. The private database can evolve through schema changes without invalidating already-shared capsules. Each layer is independently replaceable as long as it honors the contracts at its boundaries.

### 1.2 Design Principle

Everything needed by the recipient lives inside the capsule. Everything not needed by the recipient stays in the private database. The innovation is the contract, not the container.

### 1.3 Goals

- Self-contained: no external dependencies, no network requests required
- Shareable: works as an email attachment, file drop, or static hosting
- Human-readable: meaningful UI for non-technical recipients
- Machine-readable: structured manifest and data for programmatic access
- Interactive: filtering, sorting, annotation, exploration
- Exportable: recipients can extract data, notes, and responses
- Versioned: both the spec format and individual artifacts are versioned
- Privacy-aware: redaction is explicit and auditable
- Accessible: semantic HTML, keyboard navigable, screen reader compatible

### 1.4 Non-Goals

- Not a replacement for the private database
- Not a canonical source of truth (it is a snapshot)
- Not optimized for large binary assets (images, audio) — base64 encoding inflates these ~33% and they dominate file size. Large structured data (JSON) is fine.
- Not a multi-user collaborative backend
- Not a substitute for access control on sensitive data
- Not a live connection to the source system

---

## 2. File Structure

Every capsule is a single `.html` file. Internal sections are identified by `id` attributes and `type` attributes on `<script>` and `<style>` elements.

```html
<!DOCTYPE html>
<html lang="en" data-capsule-spec="0.3.0">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="generator" content="capsule-compiler">
  <meta name="capsule-uuid" content="{uuid}">
  <title>{capsule title}</title>

  <!-- REQUIRED: Manifest -->
  <script id="capsule-manifest" type="application/json">
    { ... }
  </script>

  <!-- REQUIRED: Data snapshot -->
  <script id="capsule-data" type="application/json">
    { ... }
  </script>

  <!-- OPTIONAL: Data schema -->
  <script id="capsule-schema" type="application/json">
    { ... }
  </script>

  <!-- OPTIONAL: Response template -->
  <script id="capsule-response-template" type="application/json">
    { ... }
  </script>

  <!-- OPTIONAL: Embedded assets index -->
  <script id="capsule-assets" type="application/json">
    { ... }
  </script>

  <!-- REQUIRED: Styles -->
  <style id="capsule-style">
    /* All CSS */
  </style>

  <!-- OPTIONAL: Print styles -->
  <style id="capsule-print-style" media="print">
    /* Print-specific CSS */
  </style>
</head>
<body>

  <!-- REQUIRED: UI root -->
  <main id="capsule-root">
    <!-- All visible UI -->
  </main>

  <!-- REQUIRED: Runtime -->
  <script id="capsule-runtime">
    // All JavaScript
  </script>

</body>
</html>
```

### 2.1 Required Sections

| Section ID            | Type               | Purpose                                      |
|-----------------------|--------------------|----------------------------------------------|
| `capsule-manifest`   | `application/json` | Identity, provenance, capabilities, privacy   |
| `capsule-data`       | `application/json` | The data snapshot                             |
| `capsule-style`      | CSS                | All visual styling                            |
| `capsule-root`       | HTML               | The UI layout and structure                   |
| `capsule-runtime`    | JavaScript         | Rendering, interaction, and export logic      |

### 2.2 Optional Sections

| Section ID                     | Type               | Purpose                                    |
|--------------------------------|--------------------|--------------------------------------------|
| `capsule-schema`              | `application/json` | Describes the shape of embedded data        |
| `capsule-response-template`   | `application/json` | Template for recipient responses/feedback   |
| `capsule-assets`              | `application/json` | Index of embedded base64 assets             |
| `capsule-print-style`         | CSS (`media=print`)| Print/PDF-specific layout                   |

### 2.3 Rendering Model (Core v0.1.3 rule 12)

The `<main id="capsule-root">` body **must already contain the full readable artifact when the file is opened.** Title, prose, embedded media (`<img src="data:...">`, `<audio src="data:...">`, `<video src="data:...">`), tables, lists, metadata — all rendered into the HTML at build time. Runtime JavaScript may *enhance* the capsule (wire up export buttons, dynamic UI, copy-to-clipboard) but must not be required to produce the readable content.

**Why:** Capsules are archives, not apps. They must remain readable in environments that don't execute inline scripts — iOS Files / QuickLook previews, email client previews, screen readers, search indexers, archive viewers, and future browsers whose JavaScript support has drifted from today's APIs. A capsule whose `capsule-root` is mostly empty `<div id="...">` containers will render as a blank page in any of those environments.

**WRONG** — empty placeholders waiting for JS to render content:
```html
<main id="capsule-root">
  <h2 id="title"></h2>
  <figure id="photo-frame"></figure>
  <p id="caption"></p>
  <dl id="meta"></dl>
</main>
<script id="capsule-runtime">
  /* 200 lines of `el.textContent = data.title` etc. */
</script>
```

**RIGHT** — content is already in the HTML; JS is optional polish:
```html
<main id="capsule-root">
  <h2>The actual title</h2>
  <figure>
    <img src="data:image/jpeg;base64,..." alt="...">
  </figure>
  <p>The actual caption.</p>
  <dl>
    <dt>Date</dt><dd>~1993</dd>
    <dt>Place</dt><dd>Campbell River, BC</dd>
  </dl>
</main>
<script id="capsule-runtime">
  /* ~50 lines: just button click handlers */
</script>
```

**Carve-out for visualization geometry** (added v0.3.3, resolves E.5). Some capsules render data-bearing content as runtime-drawn geometry into a pre-declared container — vector maps with hundreds of polygons, scatter plots, network diagrams, anything where the natural shape of the artifact is "draw N geometric primitives into an SVG/Canvas." Pre-rendering the geometry as static markup is often impractical (file size, structural complexity, the wrong shape for the data). Rule 12 still applies: the file must remain legible when scripts don't run. The accepted pattern is to embed a **static image rendering as the JS-disabled fallback** inside the same container, hidden by runtime when the interactive version is ready.

```html
<!-- The data-bearing container with both renderings -->
<figure class="map-container" aria-label="Project location — 47 claims, BC">
  <img id="map-static" src="data:image/png;base64,iVBORw0KGgo..."
       alt="Static rendering of the project map" class="map-fallback">
  <svg id="map-svg" viewBox="0 0 1000 1294" hidden></svg>
</figure>
<!-- Belt-and-suspenders: hide the SVG entirely when JS is disabled -->
<noscript><style>#map-svg { display: none !important; }</style></noscript>
<script id="capsule-runtime">
  // After hydrating SVG with polygons:
  document.getElementById('map-static').hidden = true;
  document.getElementById('map-svg').hidden = false;
</script>
```

What this gives:

- **JS-restricted environment** (iOS Files / QuickLook preview, email-client preview, search indexers, text-only LLMs ingesting the HTML): renders the embedded image. The data-bearing content IS in the HTML — as a raster — preserving Rule 12's intent.
- **JS-enabled browser**: shows the interactive SVG with hover, zoom, selection, layer toggles. The image is suppressed.
- **The capsule carries both representations.** The image is a true rendering of the data (typically produced by the same pipeline that produced the geometry), not a placeholder. The pre-declared container shape is part of the static HTML.

The image-fallback escape hatch is the principled resolution to the long-standing tension between "render content in the HTML" and "geometry naturally wants runtime drawing." It applies to vector maps, charts, diagrams, and any visualization where static markup would be the wrong shape. Domain schemas for visualization-heavy capsule types should recommend this pattern explicitly — see `domain.exploration_map` in `DOMAIN_CAPSULES.md` for the canonical use.

**Interactive archive — tools, not apps** (added v0.3.4). Rule 12's "capsules are archives, not apps" is a short framing for a precise distinction: the **content** must be present in the HTML at build time, but **tools that interrogate that content** are permitted (and encouraged where they help). The operational litmus is the **JavaScript-off test** — if JS doesn't run, does the substance of the artifact survive?

- **Interactive archive (permitted).** With JS off, the user still sees the document — text, tables, lists, embedded media, the rendered chrome of any visualization, the image fallback for geometry. The runtime tools (filter, sort, search, annotate, highlight, rank, group, compare, measure, find-coordinates, export buttons, print) are absent, but the *substance* is intact. Tools query the content; tools never produce it.
- **App (forbidden).** With JS off, the user sees nothing meaningful — only a husk of containers waiting for the runtime to populate them. The substance of the artifact is generated by JS, not present in the HTML.

The standard interactive capabilities listed in §5.1 (`filter`, `sort`, `search`, `annotate`, `highlight`, `rank`, `group`, `compare`) and any domain capabilities under the `<domain>.<action>` convention (e.g., `map.measure`, `map.find_coords`, `map.zoom_to_layer`, `dataset.aggregate`) are all archive-side affordances — they help a recipient interrogate sealed content. They do not move a capsule past Rule 12.

Examples drawn from the corpus:

- **Mintel's `domain.exploration_map` capsules** ship click-to-measure (distance between two points) and click-to-find-coordinates (lat/lon on hover) on top of statically-rendered map content (chrome plus the image fallback above). JS off: the user still sees the map, legend, scale bar, attribution. Tools are gone; substance isn't. **Interactive archive — permitted.**
- **A hypothetical "load on demand" capsule** that shows nothing until the user clicks a "Render" button which fetches data from a server (Rule 2 violation) or runs JS to assemble the substance from compressed binary blobs in the data block (Rule 12 violation). **App, not archive.**
- **A hypothetical interactive REPL capsule** whose substance is whatever the user types in. The capsule has no inherent content — it's a programming environment. Outside the spec entirely; see §16.2 ("Plugin runtime for arbitrary third-party scripts inside capsules" is explicitly out of scope).

The distinction matters because external commentary on the project has periodically conflated "no JS-rendered substance" with "no interactive features at all" — overshooting in both directions ("Capsule forbids interactivity" / "Capsule is a sealed mini-application"). The category "interactive archive" names what is actually permitted, so the conversation can be precise: tools are fine; substance-generation isn't. See also the `Interactive archive` entry in [GLOSSARY.md](../GLOSSARY.md).

**Validator check:** the reference validator's `check_progressive_enhancement` heuristic counts visible-text bytes inside `<main id="capsule-root">` after stripping `<script>` and `<style>` blocks and HTML tags. Below ~200 chars, the capsule is flagged WARN as likely JS-rendered. The carve-out above does not change the validator's measurement — visualization capsules pass because the surrounding chrome (titles, legends, attributions, info panels) provides enough static content; the image fallback adds robustness in non-validator environments where Rule 12's intent matters most.

**Producer-side implications:**

- For LLM-produced capsules: write the readable content directly in the HTML. Don't bind data to placeholder elements via JS.
- For compiler-produced capsules: the compiler template should render content into the static HTML, not defer to runtime population.
- For hybrid (LLM-authored build script) capsules: pre-render content in Python; runtime JS handles only buttons.

**Why this matters historically:** the chat-LLM-produced capsules in the project's corpus prior to v0.1.3 follow the JS-render-everything pattern (training-data shape: build a tiny SPA). They fail rule 12. They remain valid as v0.1.2-era capsules but trigger the WARN under v0.1.3 — flagged as not-future-proof rather than broken.

---

## 3. Manifest

The manifest is the machine-readable contract. It answers: what is this, who is it for, what is included, what was excluded, and what can the recipient do.

### 3.1 Required Fields

```json
{
  "spec_version": "0.3.0",
  "capsule_version": "1.0.0",
  "uuid": "3b31cb55-9bd2-4d37-86dd-7a14ac5cbaf6",
  "title": "AI Workflow Maturity Diagnostic",
  "description": "Interactive assessment of current AI integration across 6 workflow categories.",
  "type": "interactive_report",
  "audience": "engineering-leadership",
  "created_at": "2026-05-15T00:00:00Z",
  "generator": {
    "name": "artifact-compiler",
    "version": "0.1.0",
    "kind": "compiler",
    "spec_provided": true,
    "spec_version_used": "0.1.0"
  },

  "synthesis": null,

  "source": {
    "origin": "private_database",
    "snapshot_type": "portable_excerpt",
    "snapshot_id": "snapshot:sn_001",
    "included_records": 42,
    "source_schema_version": "7",
    "references": [
      { "id": "src-12", "title": "Q1 workflow interviews", "hash": "sha256:7f3a..." },
      { "id": "src-18", "title": "Tool usage analytics export", "hash": "sha256:c1d2..." }
    ]
  },

  "privacy": {
    "visibility": "shared",
    "contains_private_data": false,
    "redaction_applied": true,
    "redaction_method": "field_removal",
    "redaction_profile": "partner-v1",
    "reviewed_by": "author",
    "reviewed_at": "2026-05-15T00:00:00Z",
    "external_dependencies": false
  },

  "integrity": {
    "content_hash": "sha256:a1b2c3d4...",
    "hash_scope": "data+manifest"
  },

  "capabilities": [
    "filter",
    "sort",
    "annotate",
    "copy_as_json",
    "copy_as_markdown",
    "print_to_pdf"
  ],

  "expires_at": null
}
```

### 3.2 Field Definitions

#### Identity

| Field              | Type     | Required | Description                                                        |
|--------------------|----------|----------|--------------------------------------------------------------------|
| `spec_version`     | string   | yes      | Capsule spec version (this document). Semver.                       |
| `capsule_version`  | string   | yes      | Instance version. Semver. Bumps when data or UI changes. Canonical name as of v0.2.0. Either `capsule_version` or the legacy `artifact_version` must be present. |
| `capsule_id`       | string   | no       | **DEPRECATED in v0.3.** Human-readable slug, format `capsule:{short_id}`. Redundant with `title` (derive `slugify(title)` at display time if you need a slug) and not unique enough to serve as a reference. Still accepted in v0.3 for backward compatibility; planned for removal in v0.4. New capsules should rely on `uuid` + `title`. |
| `artifact_id`      | string   | no       | **DEPRECATED.** v0.1 legacy alias for `capsule_id`. Format: `artifact:{short_id}`. Still accepted under v0.2/v0.3 compatibility. |
| `artifact_version` | string   | no       | **DEPRECATED.** v0.1 legacy alias for `capsule_version`. Still accepted under v0.2/v0.3 compatibility. New capsules should use `capsule_version`. |
| `uuid`             | string   | yes      | UUIDv4. *Claimed* identity — useful for human reference and linking. The *verifiable* identity is `integrity.content_hash` (see Section 8.4). |
| `title`            | string   | yes      | Human-readable title.                                               |
| `description`      | string   | yes      | One-paragraph summary of the capsule's purpose.                    |
| `type`             | string   | yes      | Capsule type. Recommended values in Section 3.3; free-form string allowed for cases the canonical types don't cover (e.g., LLMs naturally reach for `"summary"` or `"briefing"`). |
| `created_at`       | string   | yes      | ISO 8601 timestamp.                                                 |
| `generator`        | object   | yes      | What produced the HTML. See *Generator* table below.                |
| `synthesis`        | object   | no       | Present when an LLM or other process *synthesized the data* (extraction, summarization). See *Synthesis* table below. Null or omitted means the data came directly from a structured source. |
| `audience`         | string   | no       | Intended recipient or group (`"partner-engineering"`, `"family"`, `"board-of-directors"`). Distinct from `privacy.visibility` (which is access control); `audience` describes *intent*. |

#### Generator

The generator block describes what produced the HTML file. Different generator kinds have different trust profiles; declaring kind honestly lets validators and recipients calibrate expectations.

| Field                  | Type   | Required | Description                                                  |
|------------------------|--------|----------|--------------------------------------------------------------|
| `generator.name`       | string | yes      | Identifier for the producing tool (e.g., `"artifact-compiler"`, `"claude.ai"`, `"gemini"`, `"codex"`, `"hand"`). |
| `generator.version`    | string | yes      | Version of the producing tool. For LLMs, the model ID (e.g., `"claude-opus-4-7"`, `"gpt-4o"`). |
| `generator.kind`       | string | yes      | One of `"compiler"` (deterministic reference implementation), `"llm"` (LLM-generated), `"human"` (hand-written), `"hybrid"` (e.g., LLM-drafted + compiler-finalized). |
| `generator.spec_provided` | boolean | no    | Whether the producer was given the capsule spec as context. Relevant for `kind: "llm"`. |
| `generator.spec_version_used` | string | no | Spec version the producer targeted (may differ from current `spec_version`). |

#### Synthesis

Present when an LLM or other automated process *generated the data content* (e.g., extracting claims from an article, summarizing meeting transcripts). Absent or null when the data came directly from a structured source (database query, CSV, etc.).

| Field                       | Type    | Required | Description                                             |
|-----------------------------|---------|----------|---------------------------------------------------------|
| `synthesis.kind`            | string  | yes      | Recommended values: `"ai_extraction"`, `"ai_summarization"`, `"ai_generation"`, `"llm_summary"`, `"llm_synthesis"`, `"other"`. Free-form string; the spec does not enforce an enum. |
| `synthesis.model`           | string  | yes      | Model ID (e.g., `"claude-opus-4-7"`).                    |
| `synthesis.source_input`    | string  | no       | Pointer to what the model worked from (URL, file path, description). |
| `synthesis.human_reviewed`  | boolean | yes      | Whether a human reviewed the synthesized content before compilation. |
| `synthesis.synthesized_at`  | string  | no       | ISO 8601 timestamp.                                      |
| `synthesis.notes`           | string  | no       | Free-text notes on the synthesis process or its limitations. |

#### Source

| Field                  | Type     | Required | Description                                                     |
|------------------------|----------|----------|-----------------------------------------------------------------|
| `source.origin`        | string   | yes      | Where the data came from. Recommended values: `"private_database"`, `"web_research"`, `"public_documents"`, `"ai_synthesis"`, `"user_input"`, `"observation"`. Free-form string — the spec does not enforce an enum because the LLM-in-the-wild case has no private database, only public sources. Be honest about origin; recipients use this to calibrate trust. |
| `source.snapshot_type` | string   | yes      | Recommended values: `"portable_excerpt"`, `"full_table"`, `"computed"`, `"summary"`, `"synthesis"`, `"aggregation"`, `"capture"`. Free-form string. |
| `source.snapshot_id`   | string   | yes      | Links to the registry record for this snapshot.                  |
| `source.included_records` | integer | yes   | Count of records in the data section.                            |
| `source.source_schema_version` | string | no | Version of the internal DB schema used at export time.          |
| `source.references`    | array    | no       | Individual upstream sources this capsule draws from. Each entry: `{ id, title, hash }`. Use when the snapshot aggregates multiple distinct sources (e.g., a research brief drawing from several interviews and datasets). Different from `snapshot_id` — that's *when*; references are *what*. |
| `source.spec_received` | string   | no       | Version string of the Core spec the producer was given (e.g., `"v0.1.0 · 2026-05-16"`). Encouraged for LLM-produced capsules — lets future readers correlate output with the spec version that produced it. |
| `source.prompt_received` | string | no       | Verbatim prompt the producer was given. Encouraged for LLM-produced capsules — turns the manifest into a self-documenting research record without external bookkeeping. |

#### Privacy

| Field                        | Type     | Required | Description                                                |
|------------------------------|----------|----------|------------------------------------------------------------|
| `privacy.visibility`         | string   | yes      | `"private"`, `"shared"`, or `"public"`.                     |
| `privacy.contains_private_data` | boolean | yes   | True if any PII or sensitive data remains after redaction.   |
| `privacy.redaction_applied`  | boolean  | yes      | Whether redaction was performed during compilation.          |
| `privacy.redaction_method`   | string   | no       | `"field_removal"`, `"value_masking"`, `"aggregation"`, `"none"`. |
| `privacy.redaction_profile`  | string   | no       | Named profile identifier (e.g., `"external-v1"`, `"partner-v2"`, `"public-anonymized"`). The profile rules live in your private system; the capsule just records *which* profile was applied. Enables audit and reproducibility. |
| `privacy.reviewed_by`        | string   | no       | Who reviewed the redaction. `"author"`, `"automated"`, or a name. |
| `privacy.reviewed_at`        | string   | no       | ISO 8601 timestamp of review.                               |
| `privacy.external_dependencies` | boolean | yes   | Must be `false` for a valid capsule.                        |

#### Integrity

| Field                    | Type   | Required    | Description                                                |
|--------------------------|--------|-------------|------------------------------------------------------------|
| `integrity.content_hash` | string | recommended | Format: `{algorithm}:{hex_digest}`. Default: `sha256`. **Required for capsules with `generator.kind: "compiler"`; recommended for `kind: "llm"` (LLMs may not compute it correctly — see Section 8.4). Missing hash → degraded trust; wrong hash → tampering or generator bug.** See §9.1.1 for the normative canonicalization and hashing recipe. |
| `integrity.hash_scope`   | string | recommended | What's hashed: `"data+manifest"`, `"full_document"`, or `"data_only"`. Required when `content_hash` is present. |

#### Capabilities

| Field          | Type     | Required | Description                                              |
|----------------|----------|----------|----------------------------------------------------------|
| `capabilities` | string[] | yes      | List of interaction features. See Section 5.              |
| `expires_at`   | string   | no       | ISO 8601 timestamp. Null means no expiration.             |

### 3.3 Artifact Types

The `type` field is free-form. The values below are recommended for common cases — but if your capsule is honestly described by a word not in this list (LLMs naturally reach for `"summary"` or `"briefing"`), use that word. Recipients use type for orientation; honesty matters more than enum conformance.

| Type                   | Description                                           |
|------------------------|-------------------------------------------------------|
| `interactive_report`   | Data-driven report with filters and exploration        |
| `decision_board`       | Cards/options for ranking, choosing, or prioritizing   |
| `assessment`           | Questionnaire, rubric, or diagnostic                   |
| `reference`            | Read-only reference document or knowledge excerpt      |
| `dashboard`            | Metrics, charts, and KPIs                              |
| `learning_object`      | Educational content with progression or exercises      |
| `collection`           | Gallery, list, or catalog of items                     |
| `form`                 | Structured input collector                             |
| `narrative`            | Long-form content with embedded data                   |
| `summary`              | Condensed overview of a topic (common for LLM output)  |
| `briefing`             | Stakeholder-oriented summary with context and recommendations |
| `custom`               | Anything not covered above. Describe in `description`. |

---

## 4. Data Section

### 4.1 Structure

The `capsule-data` block holds the data snapshot as JSON. Two patterns are recognized as first-class:

**A. Records-array shape** (for discrete-item content — decision boards, claim lists, photo galleries, table data):

```json
{
  "records": [
    {
      "_record_id": "rec_001",
      "_source_table": "workflows",
      "_included_at": "2026-05-15T00:00:00Z",
      "title": "Document Processing Pipeline",
      "category": "automation",
      "maturity_score": 3,
      "notes": "Currently manual with partial automation."
    }
  ],
  "metadata": {
    "record_count": 42,
    "tables_referenced": ["workflows", "categories"],
    "query_description": "All workflows with maturity_score < 4"
  }
}
```

**B. Single-document shape** (for synthesis content — summaries, briefings, research notes, reference documents):

```json
{
  "title": "Conversation summary",
  "summary": {
    "core_answer": "...",
    "main_theme": "..."
  },
  "key_takeaways": [ ... ],
  "main_points": [ { "topic": "...", "point": "..." } ],
  "memorable_phrases": [ ... ],
  "possible_follow_up_questions": [ ... ]
}
```

The top-level keys above are illustrative, not required. The defining property of this shape is "top-level JSON object with thematic named sections, each appropriate to the content." Different topics produce different thematic keys: a restaurant-recommendation capsule might have `quick_recommendations` and `places`; a medical-explainer capsule might have `inflammation_explainer` and `corrected_misconceptions`; a decision-support capsule might have `decision_matrix` and `risk_register`. **All of these are the single-document shape.** The shape is the *structure* (top-level object, thematic sections, mix of strings/objects/arrays at the top level), not a fixed key set.

Both shapes are valid. Use whichever fits the content. LLMs producing synthesis capsules from conversations consistently reach for the single-document shape; that's the natural fit for "summarize this." LLMs producing decision-support or list-shaped artifacts reach for `records[]`. The Reserved Fields (Section 4.2) apply to records-array shape; single-document capsules can omit them.

### 4.1.1 Choosing between the shapes

| If your content is... | Use |
|---|---|
| A set of discrete items that recipients might filter, rank, or decide on individually | `records[]` |
| A synthesis or summary of one topic with thematic sections | Single document |
| A mix of both | Either is fine — pick the dominant shape |

The data block is fundamentally free-form JSON; these two shapes are recognized conventions, not requirements. A capsule with neither shape is still valid if it has structurally well-formed JSON in `capsule-data`.

### 4.1.2 Recommended data-block conventions (not required)

Two top-level data fields have emerged from practice across the LLM-produced corpus and are recommended where they fit. Neither is required by validation; both are recognized conventions that producers should reach for when applicable.

**`sources`** — an array of external references the capsule's content draws on. Recommended when the conversation or synthesis cites URLs, papers, official documents, datasets, regulatory filings, or other external materials.

```json
"sources": [
  {
    "label": "City of Vancouver — False Creek South leases on City land",
    "url": "https://vancouver.ca/...",
    "role": "primary_evidence",
    "accessed_at": "2026-05-17",
    "note": "Used for City ownership, leasehold structure, and LISL payment context."
  }
]
```

Roles observed in practice: `"primary_evidence"`, `"background"`, `"citation"`, `"policy_basis"`, `"data_source"`, `"counterargument"`. Producers may invent additional roles as appropriate.

Why structured rather than inline prose: makes sources queryable across capsules and survives prose summarization. The first capsule to use this pattern (capsule 21 in the personal corpus) had six sources in a structured array plus inline mentions; the structured form is what survives future restatement.

**`embedded_media`** — a metadata block describing any non-text media embedded in the capsule via `data:` URIs in the HTML body. Spontaneously invented by chat-LLM producers when the source conversation contained images (capsules 24, 28 in the personal corpus).

```json
"embedded_media": {
  "kind": "image",
  "description": "User-provided screenshot of a histogram of marathon finish times.",
  "filename": "image(23).png",
  "mime_type": "image/png",
  "embedded_as": "data_uri",
  "byte_size_approx": 254000
}
```

For multiple embedded media items, `embedded_media` may be an array of objects with the same shape. Capsules that embed audio (as the photo capsule does) typically describe it under `audio` rather than `embedded_media`; both shapes are acceptable.

These conventions can evolve. New patterns that emerge consistently across batches will be documented here in future spec revisions.

### 4.2 Reserved Fields

Fields prefixed with `_` are system fields managed by the compiler:

| Field            | Type   | Required | Description                                    |
|------------------|--------|----------|------------------------------------------------|
| `_record_id`     | string | yes      | Stable ID for this record within the capsule    |
| `_source_table`  | string | no       | Originating table in the private database       |
| `_included_at`   | string | no       | ISO 8601 timestamp when record was exported     |
| `_redacted_fields` | string[] | no   | Names of fields removed during redaction        |
| `_content_hash`  | string | no       | Hash of this record's content at compile time. Format: `sha256:{hex}`. Enables stale-response detection when feedback references a record that has since changed in the source database. |

### 4.3 Data Constraints

- All data must be valid JSON
- No circular references
- No live database connections or query strings
- String values must be UTF-8
- Dates must be ISO 8601
- Numeric precision: IEEE 754 double (standard JSON)

### 4.4 Computed Data

If the capsule includes derived or aggregated data, it should be in a separate key:

```json
{
  "records": [ ... ],
  "computed": {
    "averages": { "maturity_score": 2.8 },
    "counts_by_category": { "automation": 12, "manual": 30 }
  },
  "metadata": { ... }
}
```

---

## 5. Capabilities

Capabilities are declared in the manifest and implemented in the runtime. A capsule must implement every capability it declares.

### 5.1 Standard Capabilities

| Capability          | Description                                              |
|---------------------|----------------------------------------------------------|
| `filter`            | Filter records by field values                            |
| `sort`              | Sort records by one or more fields                        |
| `search`            | Free-text search across record fields                     |
| `annotate`          | Add notes or comments to individual records               |
| `highlight`         | Mark/flag records for attention                           |
| `rank`              | Drag or assign priority/rank to records                   |
| `group`             | Group records by category or field                        |
| `compare`           | Side-by-side comparison of selected records               |
| `copy_as_json`      | Copy selected data as JSON to clipboard                   |
| `copy_as_markdown`  | Copy selected data as Markdown to clipboard               |
| `copy_as_csv`       | Copy selected data as CSV to clipboard                    |
| `copy_as_prompt`    | Copy a pre-formatted prompt to clipboard                  |
| `download_json`     | Download data or response as `.json` file                 |
| `download_csv`      | Download data as `.csv` file                              |
| `download_capsule`  | Download the capsule itself as a `.html` file (DOM-serialized; see §5.1.1) |
| `print_to_pdf`      | Print-optimized layout via browser print                  |
| `export_response`   | Generate and download a structured response file          |
| `about`             | Collapsible "About this artifact" section showing manifest |

#### 5.1.1 The `download_capsule` capability

Solves a real recurring failure mode: recipients who want to save a hosted capsule reach for **Save Page As → Webpage, Single File** in Chrome, which wraps the artifact in an MHTML envelope that destroys the capsule contract (see the "Inspecting a served capsule" preamble at the top of this document). A `download_capsule` button gives the author an in-capsule export path that doesn't rely on the browser's broken save flow.

**Implementation pattern.** The runtime serializes its own DOM and triggers a download — no network, no fetch (rule 2 stays intact). The complete pattern, suitable for inlining in `<script id="capsule-runtime">`:

```js
function downloadCapsule() {
  const html = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
  const blob = new Blob([html], {type: 'text/html;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement('a'), {
    href: url,
    download: `${manifest.title.replace(/[^\w-]+/g, '_')}.html`
  });
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}
```

**Recommended scope pairing.** Browsers normalize HTML during `outerHTML` serialization (attribute order, quote style, void-tag form, whitespace inside `<style>`). So the downloaded copy is *functionally* identical to the source but not *byte*-identical. Capsules that declare `download_capsule` SHOULD use `hash_scope: "data+manifest"` or `hash_scope: "data_only"` for `integrity.content_hash` — those scopes hash only the JSON inside `<script type="application/json">` raw-text elements, which browsers don't normalize. Capsules using `hash_scope: "full_document"` will hand recipients a copy whose hash doesn't verify against the original; if `full_document` integrity is essential, omit `download_capsule` and direct recipients to `curl -O` instead.

### 5.2 Minimum Required Capabilities

Every capsule must implement at least:

1. `about` — self-documenting manifest display
2. One **export** capability: `copy_as_json`, `download_json`, `copy_as_markdown`, `print_to_pdf`, or `export_response`

### 5.3 Implementation Honesty

A capsule must implement every capability it declares. Declaring `sort` without a sort UI, or `copy_as_json` without a working button, violates the spec. The validator (Section 14) should detect declared-but-unimplemented capabilities.

If you remove a capability's UI during template evolution, remove it from `default_capabilities` in the template config and from the compiled manifest. The capabilities list is a contract, not a wishlist.

---

## 6. Embedded Assets

### 6.1 Encoding

All assets are base64-encoded and referenced from the `capsule-assets` index:

```json
{
  "assets": [
    {
      "asset_id": "asset_001",
      "filename": "workflow-diagram.png",
      "mime_type": "image/png",
      "size_bytes": 24576,
      "encoding": "base64",
      "data_ref": "asset_001_data"
    }
  ],
  "total_size_bytes": 24576
}
```

The actual base64 data is stored in a corresponding script block:

```html
<script id="asset_001_data" type="text/plain">
  iVBORw0KGgo...
</script>
```

### 6.2 Supported Asset Types

| Category | MIME Types                                      |
|----------|-------------------------------------------------|
| Images   | `image/png`, `image/jpeg`, `image/svg+xml`, `image/webp` |
| Audio    | `audio/mpeg`, `audio/ogg`, `audio/wav`           |
| Icons    | `image/svg+xml`                                  |
| Fonts    | `font/woff2` (embedded via CSS `@font-face`)     |

### 6.3 Size Limits

| Threshold   | Behavior                                                                                   |
|-------------|--------------------------------------------------------------------------------------------|
| < 2 MB      | Normal. No warnings.                                                                        |
| 2 - 5 MB    | Compiler warns. Author confirms.                                                            |
| 5 - 15 MB   | Compiler requires explicit `--allow-large` flag.                                            |
| 15 - 20 MB  | Allowed, but flagged: may not fit common email attachment limits (Gmail = 25 MB envelope).  |
| > 20 MB     | Blocked. Asset must be excluded or downsampled, or use a non-email distribution channel.   |

The 15 MB threshold is a **soft warning for distribution-channel compatibility**, not a structural limit. The 20 MB hard cap (raised from 15 MB in v0.3.3) sits below email-attachment ceilings while leaving headroom for production capsules that travel via hosted channels (per the MinDev pattern in Appendix B), AirDrop, Slack, or cloud-storage links. Empirically: browser parse + JSON parse scales linearly at ~5 MB/sec (F5), so a 20 MB capsule loads in well under 250ms on desktop. Distribution, not browser strain, has always been the binding constraint.

These limits apply to the **total file size** of the compiled capsule. In practice, structured JSON data is compact — size limits are almost always hit by embedded binary assets (images, audio, fonts) or, for visualization capsules, by raw GeoJSON / coordinate data in the data block. A capsule with 100,000 records of textual JSON and no images will typically stay well under 2 MB.

### 6.4 Fallback Behavior

If an asset cannot be embedded (size, format, encoding failure), the compiler must:

1. Insert a placeholder element with `class="capsule-asset-placeholder"`
2. Include the original filename and description as text content
3. Log the exclusion in `manifest.compilation.warnings`

---

## 7. Response and Feedback Schema

When a capsule supports the `export_response` capability, responses must follow this schema.

### 7.1 Response Envelope

```json
{
  "response_schema_version": "0.1.0",
  "capsule_reference": {
    "capsule_version": "1.0.0",
    "uuid": "3b31cb55-9bd2-4d37-86dd-7a14ac5cbaf6",
    "snapshot_id": "snapshot:sn_001"
  },
  "response": {
    "type": "annotation",
    "created_at": "2026-05-16T14:30:00Z",
    "created_by": "recipient",
    "payload": { }
  }
}
```

### 7.2 Response Types

| Type          | Payload Structure                                              |
|---------------|----------------------------------------------------------------|
| `annotation`  | `{ "record_id": "rec_001", "note": "...", "field": "..." }`    |
| `ranking`     | `{ "ranked_items": [{ "record_id": "rec_001", "rank": 1 }] }` |
| `selection`   | `{ "selected": ["rec_001", "rec_005"], "reason": "..." }`      |
| `decision`    | Single: `{ "decision": "approved", "conditions": "...", "notes": "..." }` — or multi-record: `{ "decisions": [{ "record_id": "rec_001", "verdict": "approve", "note": "..." }], "summary_verdict": "approved", "summary_notes": "..." }`. Per-record entries must include `record_id` and at least one of `verdict` or `note` (note-only entries are valid — they capture comments on records the recipient didn't judge). |
| `feedback`    | Flexible shape. Recommended fields: `rating`, `comments`, `suggestions`, `position`, `most_important_issue`, `notes`. Additional fields permitted — feedback takes many forms (rating, structured form response, multi-question survey, etc.). |
| `form_data`   | `{ "fields": { "field_name": "value", ... } }`                 |
| `freeform`    | `{ "content": "...", "format": "markdown" }`                   |
| `patch`       | `{ "operations": [{ "op": "replace", "path": "/records/0/title", "value": "..." }] }` — a JSON Patch ([RFC 6902](https://datatracker.ietf.org/doc/html/rfc6902)) array of operations against the capsule's data. Useful for corrections to records (genealogy, document review, data cleanup). The recipient is proposing changes, not asserting authority — the author still reviews before applying. |

### 7.3 Validation Rules

The import workflow must validate:

1. `capsule_reference.uuid` is looked up in the registry. *If found:* full validation including per-record content-hash comparison for stale-response detection. *If not found:* degraded validation (envelope structure, sanitization, schema conformance only) — the user is prompted to register the referenced capsule. The registry is a trust amplifier, not a gate (see Section 11.4).
2. `capsule_reference.capsule_version` matches or is noted as outdated
3. `response.type` is a recognized type
4. `response.payload` conforms to the type's expected structure
5. No executable content in any string field (strip `<script>`, event handlers, `javascript:` URIs)

---

## 8. Versioning

### 8.1 Two Version Fields

| Field              | Tracks                                       | When It Bumps                                     |
|--------------------|----------------------------------------------|---------------------------------------------------|
| `spec_version`     | The capsule format (this document)            | When required sections, fields, or behavior change |
| `capsule_version`  | The individual capsule instance               | When data, UI, or capabilities change              |

Both use [Semantic Versioning](https://semver.org/):

- **Major**: breaking changes (new required fields, removed sections)
- **Minor**: backwards-compatible additions (new optional fields, new capabilities)
- **Patch**: fixes (typos in data, styling corrections, bug fixes in runtime)

### 8.2 Regeneration Rules

| Scenario                         | UUID    | capsule_version  |
|----------------------------------|---------|------------------|
| New capsule                      | New     | `1.0.0`          |
| Same capsule, data refreshed     | New     | Minor bump       |
| Same capsule, bug fix            | New     | Patch bump       |
| Same capsule, UI redesign        | New     | Major bump       |
| Forked from another capsule      | New     | `1.0.0`          |

Every compilation produces a new UUID. The `capsule_version` tracks evolution of a logical capsule. (Prior to v0.3, the optional `capsule_id` slug was the logical-capsule identifier across versions; it is now deprecated. Logical-capsule identity is left to the consumer — typically `title` + the producer's filing system.)

### 8.3 Staleness Indicator

The runtime should display a notice if `expires_at` is set and the current date is past it. This is advisory only — the capsule remains functional.

### 8.4 Claimed vs. Verifiable Identity

A capsule has two identities:

- **Claimed identity** (`uuid`) — a stable, human-readable identifier the producer assigns. Useful for linking and tracking. *Not* a trust anchor; any producer can claim any UUID.
- **Verifiable identity** (`integrity.content_hash`) — computed deterministically from the manifest + data per Section 9.1.1. Cannot be forged without producing a capsule with matching contents. *This is the trust anchor.*

Registries should index capsules by content hash for collision-resistant identity, and store UUIDs as secondary metadata for human reference. Two capsules claiming the same UUID can still be distinguished by content hash. A capsule produced by an LLM that fabricates a UUID matching a real capsule's UUID will still have a different content hash.

LLM-produced capsules may have missing or incorrect content hashes. When importing such capsules, registries should:

1. Compute the actual content hash on import (using the placeholder-then-replace protocol from Section 9.1.1)
2. Compare to any declared hash; warn on mismatch
3. Use the computed hash as the canonical identity in the registry
4. Preserve the declared UUID for human reference

---

## 9. Security

### 9.1 Compilation Security

The compiler is the trust boundary. It must:

1. **Sanitize all data values** — escape HTML entities in any string that will be rendered
2. **Strip executable content from data** — no `<script>`, `onclick`, `javascript:` in data fields
3. **Enforce redaction** before embedding — redaction happens at compile time, not at render time
4. **Validate the manifest** against the spec schema before output
5. **Compute and embed the integrity hash** as the final compilation step

#### 9.1.1 Content Hash Recipe (normative)

The integrity hash is self-referential — it lives inside the manifest it hashes. The recipe below is normative: any conforming producer or verifier MUST produce bit-identical hashes when given the same inputs.

**Supported algorithms.** As of v0.3, `sha256` is the only supported algorithm. The schema pattern reserves `sha384` and `sha512` for future use; producers MUST emit `sha256`. The output format is `sha256:<hex_digest>` where the hex digest is **lowercase** and 64 characters long.

**Canonical JSON form.** "Canonical JSON" in this spec means:
- Keys at every level are sorted lexicographically by Unicode code point (UTF-16 code-unit order is equivalent for the BMP).
- No whitespace anywhere — items are separated by `,` and key/value pairs by `:`, with no spaces.
- Non-ASCII characters are emitted as their UTF-8 bytes — they are NOT escaped to `\uXXXX` form. (Python's `json.dumps(..., ensure_ascii=False)`.)
- The resulting string is encoded to bytes as UTF-8 immediately before hashing.

Reference Python implementation:
```python
import json
def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

**Protocol.** The five-step recipe:

1. **Set the placeholder.** Make a working copy of the manifest. If the working copy has no `integrity` object, create one. Set `integrity.content_hash` to the literal string `sha256:pending` (lowercase ASCII). Set `integrity.hash_scope` to the real scope value.
2. **Canonicalize the inputs.** Apply the canonical JSON rules above to the working-copy manifest and (separately) to the data block.
3. **Assemble the hash payload** based on `hash_scope`:
   - `"data+manifest"` (most common): the UTF-8 bytes of `canonical(manifest)`, followed by a single LF byte (`\n`, 0x0A), followed by the UTF-8 bytes of `canonical(data)`.
   - `"data_only"`: the UTF-8 bytes of `canonical(data)`.
   - `"full_document"`: the raw bytes of the complete output HTML file, with the declared `content_hash` string byte-replaced by `sha256:pending` immediately before hashing. Producers and validators MUST read the file in binary mode and perform byte-level find/replace (the hash and placeholder strings are pure ASCII, so byte- and string-level replacement coincide for well-formed UTF-8 files).
4. **Hash with SHA-256.** Compute `sha256` of the payload bytes. Format as `sha256:` + lowercase hex digest.
5. **Emit the real hash.** Set `integrity.content_hash` on the real manifest to the computed value and embed it in the capsule HTML.

Validators reproduce steps 1–4 against the manifest and data extracted from the capsule and compare against the `content_hash` they read. A match means the manifest and data were not tampered with. A mismatch means tampering, a compiler bug, or a canonicalization disagreement.

##### Test vector A: `data+manifest`

A new compiler can verify its implementation by reproducing this hash from the prose above alone (no peeking at validator source).

*Manifest (working copy with placeholder; pre-canonicalization):*
```json
{
  "spec_version": "0.3.0",
  "uuid": "00000000-0000-4000-8000-000000000000",
  "capsule_version": "1.0.0",
  "title": "Hash Test Vector A",
  "description": "Minimal capsule for hash recipe verification.",
  "type": "reference",
  "created_at": "2026-01-01T00:00:00Z",
  "generator": {"name": "test", "version": "1.0.0", "kind": "compiler"},
  "source": {"origin": "test", "snapshot_type": "portable_excerpt", "snapshot_id": "snapshot:hash_test_a", "included_records": 0},
  "privacy": {"visibility": "private", "contains_private_data": false, "redaction_applied": false, "external_dependencies": false},
  "capabilities": ["about", "copy_as_json"],
  "integrity": {"content_hash": "sha256:pending", "hash_scope": "data+manifest"}
}
```

*Data:*
```json
{"records": []}
```

*Canonical manifest (one line, no whitespace, keys sorted):*
```
{"capabilities":["about","copy_as_json"],"capsule_version":"1.0.0","created_at":"2026-01-01T00:00:00Z","description":"Minimal capsule for hash recipe verification.","generator":{"kind":"compiler","name":"test","version":"1.0.0"},"integrity":{"content_hash":"sha256:pending","hash_scope":"data+manifest"},"privacy":{"contains_private_data":false,"external_dependencies":false,"redaction_applied":false,"visibility":"private"},"source":{"included_records":0,"origin":"test","snapshot_id":"snapshot:hash_test_a","snapshot_type":"portable_excerpt"},"spec_version":"0.3.0","title":"Hash Test Vector A","type":"reference","uuid":"00000000-0000-4000-8000-000000000000"}
```

*Canonical data:*
```
{"records":[]}
```

*Payload:* the canonical manifest bytes, then a single `\n` (LF, 0x0A), then the canonical data bytes — UTF-8 encoded throughout.

*Expected hash:*
```
sha256:3dcff3f89736e2554b3f077dbff063f5400c682d470ffa5125fa4bdd3c652ef8
```

If your implementation produces this value bit-identical, your canonicalization, placeholder substitution, payload assembly, and digest formatting are all correct. If it diverges, the most common causes (in order) are: forgetting `sort_keys`, emitting whitespace inside JSON, escaping non-ASCII to `\uXXXX`, using a separator other than LF between manifest and data, omitting the `integrity` block from the placeholder-substituted manifest, or emitting uppercase hex.

The canonical serialization rules are deliberately strict so that a Python compiler and a Node.js validator produce identical hashes.

### 9.2 Runtime Security

The capsule runtime must:

1. Make **zero network requests** — no fetch, no XHR, no image/script/link external loads
2. Use **no external CDN dependencies** — all libraries are inlined
3. **Never execute `eval()`** or `new Function()` on data content
4. Treat all data fields as **text content**, not HTML (use `textContent`, not `innerHTML` for data)
5. **Sanitize export output** — JSON.stringify for JSON exports, escape for Markdown/CSV
6. **Treat capsule data as read-only** — the `capsule-data` block is canonical and immutable; the runtime must never modify it
7. **Keep user state in memory only** — recipient interactions (annotations, rankings, selections, form inputs) live in JavaScript memory, never written back to the `capsule-data` block; user state only materializes when the recipient triggers an export

#### 9.2.1 Runtime authoring conventions (for LLM producers)

Empirically observed failure modes when LLMs generate the runtime JS:

1. **Use template literals for multi-line strings.** Regular string literals (`"..."` or `'...'`) cannot contain raw line terminators in JavaScript — that's a SyntaxError. When writing functions that build markdown or other multi-line text, use backtick template literals or `Array.prototype.join("\n")` where `"\n"` is the two-character escape sequence, never a literal newline character. This has been the most-recurring LLM authoring bug across the project's personal-capsule corpus; when it happens, the entire runtime fails to parse and all buttons become inert (the static HTML still renders, so the bug is easy to miss without testing interactions).

2. **Test markdown/JSON copy buttons before considering a capsule done.** A capsule that validates structurally can still have a broken runtime. The validator parses the manifest and data blocks but does not execute the runtime JS.

### 9.3 Import Security

When importing a response file back into the database:

1. **Validate the response envelope** against the response schema
2. **Verify `capsule_reference`** matches a known artifact in the registry
3. **Strip all HTML/script content** from string fields
4. **Reject responses over 1 MB** (configurable)
5. **Log the import** with source, timestamp, and validation result
6. **Never auto-execute** imported content — it is data, not instructions

### 9.4 Content Security Policy

Capsules must include a meta CSP tag. The canonical baseline (used across the project's reference compiler and build scripts):

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none';">
```

This:

- Denies everything by default (`default-src 'none'`)
- Permits the embedded `<style>` and `<script>` blocks (`'unsafe-inline'` — but only inline; the same directive does *not* permit external scripts, since no `'self'` or host is listed)
- Permits inline base64 images via `data:` URIs (`img-src data:`)
- Explicitly blocks all network calls (`connect-src 'none'`)
- Blocks `<base href>` injection (`base-uri 'none'`)
- Blocks form submissions to any URL (`form-action 'none'`)

#### Feature-driven extensions

The baseline blocks audio and video. If a capsule embeds audio (e.g. a voice memo attached to a photograph), add `media-src data:`:

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data:; connect-src 'none'; base-uri 'none'; form-action 'none';">
```

Same principle: permits *embedded* base64 audio/video only, still blocks remote media (because no host is listed and `default-src 'none'` covers fallback).

**Do not broaden further.** Adding host-allowed sources (`'self'`, external CDNs, etc.) breaks the self-contained guarantee. If your capsule needs an external resource, it isn't a capsule — it's a web app. The format prioritizes durability and offline portability; that requires honest sealing.

#### Why `'unsafe-inline'` is safe in this context

In a typical web app, `'unsafe-inline'` is a reflected-XSS risk — attacker-supplied content can execute as a script. That threat model doesn't apply to capsules:

- A capsule is a finished, frozen file. There is no server, no input channel from the wild.
- If someone tampers with the file's bytes, they can rewrite the CSP too — the CSP cannot defend against the file rewriting itself.
- So `'unsafe-inline'` here precisely means "the inline scripts and styles that shipped with this file are the ones allowed to run, and no others." Useful, not dangerous.

The CSP still does real work even with `'unsafe-inline'`: it enforces the no-network guarantee, blocks externally-loaded media or scripts that a future edit might introduce, and serves as machine-readable self-documentation that the capsule is sealed.

---

## 10. Accessibility

### 10.1 Requirements

Every capsule must:

1. Use **semantic HTML** — `<main>`, `<nav>`, `<section>`, `<article>`, `<button>`, `<table>` as appropriate
2. Be fully **keyboard navigable** — all interactive elements reachable via Tab, operable via Enter/Space
3. Include **ARIA labels** on interactive controls that lack visible text
4. Maintain **color contrast** ratios of at least 4.5:1 for text (WCAG AA)
5. Provide **visible focus indicators** on all focusable elements
6. Use **`prefers-reduced-motion`** media query to disable animations when requested
7. Include a **skip-to-content** link as the first focusable element
8. Mark the document language via `<html lang="...">`

### 10.2 Data Tables

If data is presented in a table:

- Use `<thead>`, `<tbody>`, `<th scope="col">` / `<th scope="row">`
- Provide a `<caption>` or `aria-label` on the `<table>`
- Sortable columns must indicate current sort state via `aria-sort`

---

## 11. Linking and Discovery

### 11.1 Provenance (`parents`)

When a capsule is forked from one or more earlier capsules — the user pasted a capsule into a new conversation to continue or compare — record each upstream capsule in the optional `parents` array. Each entry pairs a UUID (the machine-actionable reference) with a denormalized `title` (a human-readability hint, frozen at fork-time).

```json
{
  "parents": [
    {
      "uuid": "a7c3e9f8-1234-4abc-9def-1234567890ab",
      "title": "Q1 Workflow Summary"
    },
    {
      "uuid": "b9d4f0a1-5678-4def-9abc-0987654321cd",
      "title": "Q2 Workflow Forecast"
    }
  ]
}
```

Multiple parents are meaningful and supported: a capsule that compares two earlier capsules, or that merged a second capsule into the conversation partway through, records all of them. Order is *introduction order* — the parent that seeded the conversation comes first. The `uuid` is required and must be a valid v4 UUID; the `title` is required as a human-readability hint. Producers must not invent parent references — `parents` is hard provenance, not "thematically related work."

If the conversation didn't start from a capsule, omit `parents` entirely (don't include an empty array — absent and empty are equivalent, and absent is cleaner).

### 11.2 The deprecated `related` field

Prior to v0.3 the schema reserved a `related` array for soft associations between capsules (`parent`, `sibling`, `supersedes`, `related`). It was unused in practice and is **deprecated in v0.3**, planned for removal in v0.4. Hard provenance now lives in `parents` (above). Soft associations — "this capsule is thematically similar to that one" — belong in the capsule's prose, not in structured metadata, because schema fields invite producers to fabricate edges that aren't load-bearing. The validator emits an informational note when it encounters a `related` array on a v0.3 capsule; the field still passes validation for v0.2 backward compatibility.

### 11.3 Index Capsule

An index capsule is a capsule of type `collection` whose data records are references to other capsules. It allows a recipient to see all artifacts shared with them in one view.

### 11.4 Registration and the Three Production Paths

A capsule is *valid* by virtue of meeting this spec, regardless of what produced it. The registry is a *personal tracking layer*, not a gate. Capsules from any source can be registered:

1. **Reference compiler output.** Auto-registers on compile. `generator.kind: "compiler"`. Full fidelity expected; content_hash required.
2. **LLM-produced capsules** (Claude, Gemini, Codex, ChatGPT artifacts, etc.). Manual registration: the user runs a `register` operation on a capsule HTML file they received or produced through an LLM. `generator.kind: "llm"`. Content hash recomputed and stored even if missing or wrong in the manifest.
3. **Hand-authored or hybrid capsules.** Manual registration. `generator.kind: "human"` or `"hybrid"`.

In all three cases, the registry indexes capsules by computed content hash (canonical identity) and stores the declared UUID as secondary metadata. The registry tracks `trust_tier` per capsule based on `generator.kind` — compiler-produced capsules get full-fidelity trust; LLM-produced capsules get external-tier trust with appropriate downstream warnings.

Imports against unregistered capsules degrade gracefully (Section 7.3): envelope validation only, with a prompt to register.

---

## 12. Offline Guarantees

A valid capsule must:

1. Render fully without any network access
2. Contain no `<link>`, `<script src>`, `<img src="http...">`, or `@import url()` referencing external resources
3. Function identically whether opened via `file://` or served via `http://`
4. Not depend on `localStorage`, `sessionStorage`, `IndexedDB`, or cookies for core functionality (may use them for ephemeral session state like filter selections)
5. Not use ES module `import` statements (which require a server context)
6. Rely exclusively on in-memory state for all user interactions — no persistent client-side storage is required for the capsule to function

---

## 13. Compiler Output Metadata

The manifest may include a `compilation` block for debugging and audit:

```json
{
  "compilation": {
    "compiled_at": "2026-05-15T00:00:00Z",
    "source_query": "SELECT * FROM workflows WHERE maturity_score < 4",
    "compilation_duration_ms": 342,
    "warnings": [
      "Asset 'large-diagram.png' exceeded 2MB, included with author confirmation"
    ],
    "output_size_bytes": 187432
  }
}
```

---

## 14. Validation

A capsule is **valid** if:

1. It is well-formed HTML5
2. All five required sections are present (`capsule-manifest`, `capsule-data`, `capsule-style`, `capsule-root`, `capsule-runtime`)
3. The manifest parses as valid JSON
4. All required manifest fields are present and correctly typed
5. `spec_version` matches a known spec version
6. `privacy.external_dependencies` is `false`
7. `integrity.content_hash` matches the computed hash of the specified scope (per the protocol in Section 9.1.1)
8. Every declared capability has a corresponding implementation in the runtime
9. No external resource references exist in HTML, CSS, or JavaScript
10. The data section parses as valid JSON
11. The file size is under 20 MB (with a soft warning between 15 MB and 20 MB for email-attachment compatibility — see §6.3)

A validator tool should produce a report listing pass/fail for each check.

---

## 15. MIME Type and File Extension

| Property       | Value                         |
|----------------|-------------------------------|
| File extension | `.html`                       |
| MIME type       | `text/html`                  |
| Convention      | `{slug}-{version}.html`      |
| Example         | `ai-maturity-diagnostic-1.0.0.html` |

No custom file extension. Capsules are standard HTML files that happen to follow this spec. This maximizes compatibility — they open in any browser without special tooling.

---

## 16. Scope Boundaries

Two kinds of "not in v0.1" exist, and the spec treats them differently.

### 16.1 Deferred features

These are recognized needs that fit the format but require more design work. They will likely arrive in future spec versions.

- **Encryption**: capsules that require a key to open
- **Digital signatures**: cryptographic proof of authorship
- **Multi-capsule bundles**: packaging several capsules in a zip/archive
- **Custom themes**: a theme system for consistent branding across capsules
- **Internationalization**: multi-language support within a single capsule
- **Record-level integrity verification**: hash chains for tamper detection beyond `_content_hash`

### 16.1.1 Non-Revocability

Once shared, a capsule **cannot be unshared**. There is no mechanism — and there will not be one — to retract a capsule the recipient has already received. This is a structural property of self-contained files: the recipient holds a complete copy.

Treat redaction and `audience` decisions as final before sharing. If you discover after sharing that a capsule included content it shouldn't have, the only remediation is to compile a corrected `capsule_version` and ask the recipient to discard the prior copy — they may or may not.

### 16.2 Out of scope — by design

These are not deferred features. They are places where the project would stop being itself. Adopting them would turn capsules into a different kind of thing (a SaaS app, a platform, a replay system, a semantic-web database).

- **Live collaboration** between multiple recipients on the same capsule. A capsule is one author → one or more recipients with async response. Real-time multi-user state is a SaaS problem, not a file problem.
- **Bidirectional editing** of the source database from inside the capsule. The capsule is a snapshot. If recipients can edit the source, you're building a remote client, not a portable artifact.
- **Automatic background sync** with the source database. Capsules are offline-first. Network sync turns them into thin clients.
- **Unbounded media sizes**. Past the 20 MB hard cap (raised from 15 MB in v0.3.3), the single-file model breaks down for normal distribution. Use a different format.
- **General-purpose web archival replay**. That's WACZ's job. Capsules are authored deliverables, not faithful captures of arbitrary websites.
- **Plugin runtime** for arbitrary third-party scripts inside capsules. This breaks the security model — the runtime can only run vetted, inlined code.
- **Streaming or live-updating data**. Capsules are snapshots. Live data requires a different architecture.
- **Full semantic-web provenance modeling** (RO-Crate / PROV-O complete ontology). Capsules use a pragmatic subset; full RDF/OWL integration is RO-Crate's job.

The split matters because the deferred list invites expansion, and the boundary list invites restraint. If a use case requires something from the boundary list, the right answer is usually "use a different tool for that part" — not "extend the capsule spec."

---

## Appendix A: `file://` Protocol Constraints

Modern browsers restrict local HTML files. The capsule spec is designed to work within these constraints:

| Constraint | Impact | How the spec handles it |
|---|---|---|
| No CORS / no `fetch()` to local files | Cannot load companion files | All content is embedded — no companion files exist |
| `localStorage` / `IndexedDB` unreliable on `file://` | Cannot persist state across sessions | User state is memory-only (Section 9.2, rules 6-7) |
| ES modules require server context | `import` statements fail on `file://` | ES modules prohibited (Section 12, rule 5); all JS is bundled inline |
| `data:` URLs treated as opaque origins | Some cross-origin restrictions | Assets use `data:` URLs for rendering, not for navigation |
| Some browsers block clipboard API on `file://` | `navigator.clipboard.writeText()` may fail | Export functions should fall back to selecting text in a textarea if clipboard API is unavailable |

The capsule must function identically on `file://` and `http://`. When a capability cannot work on `file://` due to browser restrictions (e.g., clipboard), the runtime should degrade gracefully rather than fail silently.

---

## Appendix B: Distribution Guidance

This section is non-normative. The capsule format is distribution-agnostic, but practical sharing has friction points.

### Recommended channels

| Method | Notes |
|---|---|
| **Direct file share** (Slack, Teams, AirDrop, USB) | Works without issues. Preferred for most use cases. |
| **Cloud storage link** (Dropbox, Google Drive, S3 presigned URL) | Recipient downloads and opens locally. Reliable. |
| **Static web hosting** | Host at any URL. Capsule works as a normal web page. CSP meta tag (Section 9.4) blocks external loads. |
| **Email (zipped)** | Zip the `.html` file before attaching. Rename to `.zip` extension. |

### Channels to avoid or handle carefully

| Method | Problem | Mitigation |
|---|---|---|
| **Email (raw `.html`)** | Enterprise email filters block HTML attachments containing `<script>` tags as potential phishing/malware | Always zip first |
| **Inline email rendering** | Some clients attempt to render HTML attachments inline, stripping scripts | Capsule requires JS; inline rendering will show broken UI |
| **URL shorteners / redirects** | Obscure the actual file, may trigger security warnings | Use direct links |

### Optional: hosted viewer

For teams that share capsules frequently, a lightweight hosted viewer can provide convenience alongside the offline-first file:

- The capsule `.html` file remains the canonical artifact
- A viewer at a known URL can accept a capsule file (drag-and-drop or upload) and render it
- The viewer adds no functionality the capsule doesn't already have — it simply provides a URL-based access path
- The viewer must never modify, store, or transmit the capsule content

---

## Appendix C: Related Work

The Capsule format sits at an intersection of existing traditions. None of these projects, alone, solves the problem this spec addresses — but each one solves part of it, and the spec borrows from several. Readers familiar with these projects can use the contrasts below to locate the capsule format on the existing map.

### Closest precedents in artifact form

**TiddlyWiki** (2004–present) — A self-contained interactive wiki that runs from a single HTML file. The longest-standing proof that "one HTML file = app + content + UI" works in practice. Capsules share TiddlyWiki's artifact form (single file, embedded app) but differ in purpose: TiddlyWiki is a native authoring environment that saves edits in place; a capsule is a compiled snapshot from a separate source system, not editable.

**MHTML / RFC 2557** (1999) — IETF standard for aggregating an HTML root document with its referenced resources into a single MIME message. Used by browser "save complete page" features (`.mht`, `.mhtml`). Transport-oriented rather than product-oriented: it bundles resources for transfer, but says nothing about manifest, provenance, or interactive behavior. Capsules solve a different problem in a different way (inline base64 + structured manifest), but MHTML is the deepest historical precedent for "single file containing a whole web document."

**SingleFile** — Browser extension that flattens any existing web page into one `.html` file with inlined assets. Excellent capture tool. Captures existing pages; does not compile new ones from a private data source. Useful technical reference for asset inlining patterns.

### Closest precedent in compiled-memory workflow

**Karpathy's LLM Wiki** — Pattern (described in a public gist) for treating a persistent wiki as a synthesized layer over immutable raw sources, with a co-evolving schema. Three layers: raw sources, the wiki, the schema. The closest workflow analog to the Capsule's "private database → compiler → portable artifact" pipeline. Key divergence: the target is a directory of Markdown files, not a single self-contained HTML capsule.

### Closest precedents in manifest and provenance

**RO-Crate** (Research Object Crate) — JSON-LD–based standard for packaging research data with metadata, file lists, and provenance. The strongest precedent for "structured manifest + provenance + packaged resources." Capsules borrow field semantics loosely (lineage, generator info, content references) but use plain JSON in v0.1 rather than full JSON-LD, deferring linked-data integration. RO-Crate is multi-file by design; capsules are single-file.

**Frictionless Data Package** — Lightweight container format with a top-level `datapackage.json` descriptor for data resources. Strong on schema declaration, lighter on provenance. Influenced the capsule's `source` and `metadata` field shapes.

**W3C PROV-DM / PROV-O** — Domain-agnostic vocabulary for representing provenance (entities, activities, agents). Capsules use a pragmatic subset of these ideas (who generated what, from where, when) without adopting the full ontology.

### Closest precedents in packaging and integrity

**WACZ / Webrecorder** — ZIP-based format for portable web archives, optimized for random-access replay. Best precedent for portable web packaging with integrity verification (including a signing proposal). Archival fidelity, not authored deliverables. Use WACZ when you need faithful replay of a captured website; use a capsule when you're publishing a curated artifact.

**Git** — Content-addressable filesystem with version control. Useful backbone for the registry layer (Section 5 of the System Architecture) — capsule versions can be tagged, hashes verified, history audited. Capsules borrow versioning discipline; they are not Git objects.

**IPFS** — Content-addressed network for distributing immutable data by hash. Useful if capsules need verifiable distribution at scale; not required for the format itself.

### Cultural precedent

**Thariq Shihipar's HTML artifacts pattern** — Public examples demonstrating self-contained `.html` files as agent outputs across many work types (reports, prototypes, diagrams, editors). The clearest evidence that the substrate has won: people are *already* making single HTML files as their default artifact format. The Capsule format formalizes the practice with a contract, manifest, provenance, and feedback loop — turning informal HTML artifacts into disciplined ones.

### Adjacent but structurally different

**Jupyter Notebook** — Executable narrative document combining code, output, and prose. Notebook format is JSON-first and execution-centric; HTML is one of many export targets. Capsules are not executable in the runtime sense — they ship pre-computed snapshots, not running code over data.

**Observable Notebooks** — Reactive JavaScript notebooks. Strong on interactive UI, weaker on portable single-file distribution and provenance.

**Static site generators** (Hugo, Jekyll, Quartz, etc.) — Produce multi-file websites from source files. Useful as publication targets *for* capsules; not the format itself.

**Obsidian + export plugins** — Local-first note system with community plugins that export notes/canvases/vaults to HTML (including single-file modes). Strong upstream source system for capsules. The export plugins point toward demand for shareable HTML views from private notes — the capsule format provides a more disciplined version of what those plugins are reaching toward.

### Summary positioning

| Dimension | Closest precedent | How capsules differ |
|---|---|---|
| Single-file HTML artifact | TiddlyWiki, MHTML | Compiled from separate source; not native authoring environment |
| Asset inlining technique | SingleFile, MHTML | Same technique; different upstream |
| Compiled-memory workflow | Karpathy LLM Wiki | Target is single HTML, not Markdown directory |
| Manifest and provenance | RO-Crate, Frictionless | Plain JSON in v0.1; single-file rather than crate |
| Portable packaging | WACZ | Authored deliverables, not archival replay |
| Cultural moment | Thariq HTML artifacts | Adds contract, manifest, versioning, feedback loop |

---

## Appendix D: Minimal Valid Capsule

```html
<!DOCTYPE html>
<html lang="en" data-capsule-spec="0.3.0">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="generator" content="artifact-compiler">
  <meta name="capsule-uuid" content="a0b1c2d3-e4f5-6789-abcd-ef0123456789">
  <title>Minimal Capsule Example</title>

  <script id="capsule-manifest" type="application/json">
  {
    "spec_version": "0.3.0",
    "capsule_version": "1.0.0",
    "uuid": "a0b1c2d3-e4f5-6789-abcd-ef0123456789",
    "title": "Minimal Capsule Example",
    "description": "The smallest valid capsule, demonstrating required sections.",
    "type": "reference",
    "created_at": "2026-05-15T00:00:00Z",
    "generator": { "name": "artifact-compiler", "version": "0.1.0" },
    "source": {
      "origin": "private_database",
      "snapshot_type": "portable_excerpt",
      "snapshot_id": "snapshot:sn_min_001",
      "included_records": 1
    },
    "privacy": {
      "visibility": "shared",
      "contains_private_data": false,
      "redaction_applied": false,
      "external_dependencies": false
    },
    "integrity": {
      "content_hash": "sha256:placeholder",
      "hash_scope": "data+manifest"
    },
    "capabilities": ["about", "copy_as_json"]
  }
  </script>

  <script id="capsule-data" type="application/json">
  {
    "records": [
      {
        "_record_id": "rec_001",
        "title": "Example Record",
        "content": "This is a minimal data record."
      }
    ],
    "metadata": {
      "record_count": 1
    }
  }
  </script>

  <style id="capsule-style">
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 2rem; color: #1a1a1a; }
    .skip-link { position: absolute; left: -9999px; top: 0; }
    .skip-link:focus { left: 0; background: #005fcc; color: white; padding: 0.5rem 1rem; z-index: 1000; }
    h1 { font-size: 1.5rem; margin-bottom: 1rem; }
    .record { border: 1px solid #e0e0e0; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; }
    .record h2 { font-size: 1.1rem; margin-bottom: 0.5rem; }
    .actions { margin-top: 1.5rem; display: flex; gap: 0.5rem; }
    button { padding: 0.5rem 1rem; border: 1px solid #ccc; border-radius: 0.25rem; background: white; cursor: pointer; font-size: 0.9rem; }
    button:hover { background: #f5f5f5; }
    button:focus-visible { outline: 2px solid #005fcc; outline-offset: 2px; }
    details { margin-top: 2rem; border-top: 1px solid #e0e0e0; padding-top: 1rem; }
    summary { cursor: pointer; font-weight: 600; }
    pre { background: #f5f5f5; padding: 1rem; border-radius: 0.25rem; overflow-x: auto; font-size: 0.85rem; margin-top: 0.5rem; }
  </style>
</head>
<body>
  <a href="#capsule-root" class="skip-link">Skip to content</a>

  <main id="capsule-root">
    <h1>Minimal Capsule Example</h1>

    <div id="records"></div>

    <div class="actions">
      <button id="btn-copy-json" aria-label="Copy data as JSON">Copy as JSON</button>
    </div>

    <details id="about-section">
      <summary>About this artifact</summary>
      <pre id="about-content"></pre>
    </details>
  </main>

  <script id="capsule-runtime">
    (function() {
      var manifest = JSON.parse(document.getElementById('artifact-manifest').textContent);
      var data = JSON.parse(document.getElementById('artifact-data').textContent);

      var recordsEl = document.getElementById('records');
      data.records.forEach(function(rec) {
        var div = document.createElement('article');
        div.className = 'record';
        var h2 = document.createElement('h2');
        h2.textContent = rec.title;
        var p = document.createElement('p');
        p.textContent = rec.content;
        div.appendChild(h2);
        div.appendChild(p);
        recordsEl.appendChild(div);
      });

      document.getElementById('about-content').textContent = JSON.stringify(manifest, null, 2);

      document.getElementById('btn-copy-json').addEventListener('click', function() {
        navigator.clipboard.writeText(JSON.stringify(data, null, 2)).then(function() {
          this.textContent = 'Copied!';
          var btn = this;
          setTimeout(function() { btn.textContent = 'Copy as JSON'; }, 2000);
        }.bind(this));
      });
    })();
  </script>
</body>
</html>
```

---

## Appendix E: v0.4 Candidates

Items queued for the next minor revision. None are committed; each is listed with the question it answers and the lean position from current discussion. Schema and validator changes do not happen here — Appendix E is the parking lot for design decisions that need to be made before they ship.

### E.1 Remove deprecated `capsule_id` slug and `related[]`

Both fields were deprecated in v0.3 with an informational validator note. v0.4 should remove them from the schema entirely. The accept-but-warn period gives existing capsules a migration window; v0.4 closes it. Action: drop the fields from `spec/manifest.schema.json`, remove the deprecation paths from `compiler/validate.py`, and update the spec field tables.

### E.2 Compiler-kind UUIDv5 carve-out

**Question.** Should `generator.kind: "compiler"` capsules be allowed (or required) to use UUIDv5 (name-based, SHA-1) rather than UUIDv4 (random)?

**Lean.** Yes, allow v5 for `kind: "compiler"`; keep v4 mandatory for `kind: "llm" | "human" | "hybrid"`. For deterministic producers, UUID-as-identity is a stronger contract than v4 + integrity-hash: two compilers given the same canonical inputs produce the same logical capsule and should land on the same UUID, simplifying registry deduplication and rebuild idempotency.

**Namespace convention (lean: shared namespace).** Two shapes were considered:

1. **Single shared "compiled-capsule" namespace UUID + canonical input string.** One well-known constant in the spec. The input string format is normative: e.g., `<domain.type>|<canonical_inputs_hash>`. Cross-compiler interop is automatic — two compilers producing the same logical artifact land on the same UUID.
2. **Per-domain namespace UUIDs.** More structure; domain authors declare and stabilize their own namespace.

Option 1 is simpler and the canonical-input-string discipline is the load-bearing part. The `compiler` tier already implies "deterministic inputs"; bake that into one namespace constant rather than fragmenting per domain.

**Open before shipping.** (a) Pick the namespace UUID. (b) Specify the canonical input string format normatively. (c) Update schema/validator to accept v5 conditionally on `generator.kind`. (d) Decide whether v5 is *allowed* or *required* for compiler-kind.

### E.3 Reconsider `ai_usage_guidance` in domain capsules

**Question.** Should `domain.implementation_notes` and `domain.design_system` keep the `ai_usage_guidance` field (`allowed_tasks`, `restricted_tasks`, `preferred_language`)?

**Lean.** Demote or remove. The field is editorial intent dressed up as structured metadata. Consumers — human or AI — can't enforce `restricted_tasks`, and `preferred_language` is style guidance that belongs in `description` prose. Existing schema fields (`description`, `caveats`) already carry editorial concerns. Adding more schema slots for "AI should/shouldn't" invites producers to encode wishes as contracts.

**Options.** (a) Cut the field from both domain schemas. (b) Move it under the `x-` extension prefix so consumers treat it as opt-in vendor metadata, not a load-bearing standard field. (c) Keep but document explicitly as advisory/non-enforceable.

### E.4 Hash-algorithm flexibility

The schema's hash pattern already accepts `sha384` and `sha512`, but the validator and reference compiler only emit/verify `sha256`. v0.4 candidate: either implement `sha384`/`sha512` end-to-end, or restrict the pattern to `sha256` until there's a concrete use case for the longer digests. Lean: restrict the pattern. Premature flexibility is more confusing than additive.

### E.5 Rule 12 vs. legacy compiler templates — **RESOLVED in v0.3.3**

**Original question.** Rule 12 (added in Core v0.1.3) says readable content should be pre-rendered in the HTML, not produced by runtime JavaScript. The reference compiler templates `templates/decision_board` and `templates/news_capsule` predate this rule and still render primary content via the runtime. Mintel-style build scripts (Mintel's `build_exploration_map_capsule`) pre-render chrome but draw map geometry via runtime SVG. Both pass the validator's surrounding-text heuristic but fail Rule 12's spirit in environments that don't run JS.

**Resolution.** Rather than tightening Rule 12 enforcement (which would break visualization geometry that can't reasonably be pre-rendered as static markup) or accepting Rule 12 violations as legacy, v0.3.3 names the carve-out explicitly: **§2.3 "Carve-out for visualization geometry"** documents the image-fallback pattern. Data-bearing content rendered into a pre-declared named container is allowed IF a static image rendering is embedded as the JS-disabled fallback inside the same container. The image preserves Rule 12's intent (content IS in the HTML — as a raster) while accommodating geometry that wants runtime drawing.

This resolves both the legacy-template case (those templates could either retire or adopt the image-fallback pattern) and the visualization-geometry case (the principled answer is "carve-out documented, not a Rule 12 exception"). The empirical pressure for this resolution came from F20 — the first publicly-fetchable Mintel production capsule.

**Shipped in v0.3.3:**
- §2.3 carve-out language with WRONG/RIGHT example
- `domain.exploration_map` schema: image-fallback as recommended convention
- No Core rule change; no validator change (the existing heuristic still counts surrounding text)

**Follow-up still open:** the legacy templates (`templates/decision_board`, `templates/news_capsule`) have not been updated. They remain v0.1-era artifacts and should either adopt the image-fallback pattern or be documented as historical. Not urgent — they aren't blocking new producers.

### E.6 Author signing + transparency log (Sigstore-shaped)

**Question.** How does a recipient verify that a capsule they received hasn't been silently tampered with by someone in the forwarding chain? A capsule's UUID asserts "this is identifier X," but UUIDs are not enforced — anyone can ship a modified capsule under the same UUID. The current `integrity.content_hash` detects tampering only if the recipient knows what hash to expect, which they typically don't.

**The unanswered trust question.** Current spec answers *what is this?* and *where does it claim to come from?*. It does not answer *did the claimed author actually publish these exact bytes?*. The current trust signals are honest about what they prove — but the missing question is the one a forwarded-capsule recipient most wants answered.

**Design sketch (not committed).** Three trust tiers, layered:

| Tier | Meaning |
|---|---|
| **Self-describing** | UUID + manifest + content_hash, no external proof. Adequate for personal archives. This is the v0.3 baseline; no change required. |
| **Signed** | `content_hash` (and `file_hash`, see below) signed by an author key, identity-anchored via Sigstore/Fulcio-style OIDC issuance. Detects tampering if you trust the issuing CA. |
| **Logged** | Signed release recorded in an append-only public transparency log (Sigstore/Rekor shape). Detects tampering, backdating, and same-UUID-different-content games across the forwarding chain. |

**Two-hash split.** Two hashes serve two different questions:

- `content_hash` — canonical(manifest) + LF + canonical(data), already specified in §9.1.1. Survives DOM round-trip (the JSON blocks are raw-text script-tag content browsers don't normalize). Answers: *is the meaningful payload intact?*
- `file_hash` — SHA-256 of the raw `.html` file bytes (with the hash field placeholder-substituted per the existing recipe — same protocol as `hash_scope: "full_document"`). Does NOT survive DOM round-trip. Answers: *is this byte-identical to the file the author originally published?*

The current `hash_scope` enum collapses these two questions into one choice per integrity block. The two-hash split would let a capsule carry both simultaneously and resolve the tension we already documented in §5.1.1 between `download_capsule` and `full_document` integrity. The integrity block would grow to `{ content_hash, file_hash?, hash_scope, signature?, log_entry_uuid? }`.

**Verification model: out-of-band, capsule stays mute.**

- The capsule itself never calls home. **Rule 2 (no network) is preserved at render time.** This is non-negotiable.
- Every capsule already embeds a QR code encoding `urn:uuid:<uuid>` in the header (Core spec convention; see CAPSULE_CORE.md rule 4 supplementary guidance).
- A verifier app on the recipient's phone or reader scans the QR, resolves the UUID to a verification URL, and queries the transparency log. The app reports: **verified** / **modified** / **unknown** / **superseded** / **identity warning**.
- Verification is explicitly opt-in friction. The capsule opens and works without it. The recipient who cares about provenance takes an active step; the recipient who doesn't is unaffected.

This trades a small amount of UX friction for the preservation of the no-network guarantee. The alternative — capsule auto-verifies on open — would break Rule 2 and turn every recipient view into a network call against a log operator. Not worth it.

**Precedents to compose, not duplicate:**

- **Sigstore / Rekor** — the model. Append-only transparency log for signed software artifacts, identity-anchored via OIDC issuance through Fulcio. The "Logged" tier would record signed-release statements about specific UUIDs against this existing infrastructure rather than running our own log. Reference: <https://docs.sigstore.dev/logging/overview/>.
- **C2PA / Content Credentials** — relevant trust-model patterns for signed content provenance, especially around metadata-stripping defense. Reference: <https://spec.c2pa.org/>.

**Hard problems to resolve before any shipping decision:**

1. **Author identity.** "Signed by author key" only works if recipients know which key to trust. Without OIDC/Fulcio-style identity issuance, the modifier signs their tampered version with their own key and the verifier sees "signed by some key, who knows whose." This is the entire trust model, not a small implementation detail.
2. **Log operator and governance.** Sigstore is operated by the Linux Foundation. For Capsules, the strong move is to *compose* existing infrastructure (record arbitrary signed JSON statements against existing Rekor) rather than run our own log. Investigate whether Rekor accepts non-software artifact statements before committing.
3. **Two-hash compatibility.** Adding `file_hash` is additive but changes the `hash_scope` semantics. Decide whether `hash_scope: "full_document"` becomes redundant (replaced by always-present `file_hash`) or stays as a third explicit choice.
4. **Empirical pressure.** No real-world tampering incident has been reported in the capsule corpus. Per the spec-gravity discipline: wait for empirical signal before building infrastructure.

**When this earns a v0.4+ schema slot.** Design and ship in a single coordinated patch when *any* of:

1. A real-world capsule-tampering incident is reported (corpus or independent producer);
2. An independent producer or recipient requests verification primitives concretely;
3. A practical Sigstore composition path appears that meaningfully reduces the infrastructure cost.

Until then, this entry is the design memory.

### E.7 Password-protected encrypted capsules

**Question.** Should the format support encrypting a capsule's content with a password so that only recipients with the password can read it? The motivating use case is sensitive personal data, client confidentiality, or selective sharing where the existing redaction primitive isn't sufficient.

**Lean: don't build, advise wrappers.** The format already has the right primitive for "don't share this content" — `privacy.redaction_applied` with `redaction_method` and `redaction_profile`. The intended model is: **decide what's shareable before sealing, redact what isn't, then seal.** Encryption pulls capsules toward "selective-access messaging," which is a different problem space better served by:

- **OS/wrapper-level encryption** (AES-encrypted ZIP, `.age`-encrypted wrappers, `gpg`-encrypted files) around the capsule. Recipient unlocks the wrapper, opens the capsule. The capsule itself stays pure and validator-clean.
- **Hosting-platform auth gates** (per the MinDev pattern; see Appendix B for general distribution guidance). The platform controls *delivery*; the capsule itself doesn't gate its internal contents.
- **Authenticated channels** for transport (Signal, encrypted email, password-protected file storage). The capsule travels through the secure channel; the format itself stays neutral.

**Why building encryption into the format is worse than these alternatives:**

1. **Cryptography is unusually hard to ship in a spec.** Browser-native primitives (WebCrypto: PBKDF2 + AES-GCM) work, but the recipe surface is large — iteration counts, salt and IV handling, authentication-tag verification, side-channel exposure. Compare the integrity-hash recipe in §9.1.1 — that was substantial work for a much simpler primitive. An encryption recipe is roughly 10× the surface and the consequences of bugs are confidentiality breaches, not hash mismatches. Once shipped, the spec inherits a permanent maintenance obligation: when PBKDF2 iteration counts age, when GCM nonce reuse turns out to be exploitable in some browser, the spec has to update and every existing capsule with old parameters becomes ambiguously secure.
2. **Encryption breaks the format's core trust signals for the encrypted portion.** Until decrypted, encrypted content is neither human-readable, machine-readable, nor validator-checkable. Rule 12 (content pre-rendered in HTML) can't apply to the encrypted payload. `content_hash` would have to either hash ciphertext (proving nothing about meaning) or require post-decryption verification (impossible at validation time). The "memory object" framing — human-readable + machine-readable + provenance-bearing in one object — partially evaporates. The capsule has two states: **locked** (none of the three) and **unlocked** (all three).
3. **Password-only encryption is fundamentally weak.** Without a key-derivation infrastructure or hardware-backed keys, password strength is the entire security boundary. Lost passwords mean permanent data loss with no recovery path. This is the right behavior cryptographically but the wrong UX expectation most users have.
4. **No empirical pressure.** Same spec-gravity discipline as E.6. No reported case of "I needed selective access and the redaction primitive wasn't enough." The default path — redact, or wrap with OS-level encryption — has been adequate.

**Design sketch if this ever ships (memory only, not committed).**

Two-tier structure preserving identity in the clear while gating content:

- **Public manifest** carries identity and provenance unencrypted: `uuid`, `title`, `description`, `type`, `created_at`, `generator`, `source`, `privacy`, `capabilities`. Plus a new `encryption` block:
  ```json
  "encryption": {
    "algorithm": "AES-256-GCM",
    "kdf": "PBKDF2-SHA256",
    "kdf_iterations": 600000,
    "salt": "<base64>",
    "iv": "<base64>",
    "encrypted_blocks": ["capsule-data", "capsule-runtime"]
  }
  ```
- **Encrypted payload**: each block listed in `encrypted_blocks` is base64-encoded ciphertext in place of its normal raw-text content. A small "unlock" runtime prompts for password, derives the key via PBKDF2, decrypts each block, parses, and replaces document content.
- **New required capability**: `password_protected`. Declared in `capabilities`. Honest about what the capsule does before unlock.

**Trust signals that survive encryption:**
- Identity (UUID, title, type) — still verifiable
- Provenance (generator, source) — still readable
- Capabilities — still declared
- E.6 signing/log — could sign the *full* artifact (envelope + ciphertext), so recipients can verify the encrypted bytes came from the claimed author *before* attempting decryption

**Trust signals that don't:**
- `content_hash` over data+manifest — meaningless (the data is opaque to the validator)
- Rule 12 pre-rendered content check — can't apply
- Capability-marker heuristics — can't see runtime code

**Hard problems to resolve before any shipping decision:**

1. **Crypto parameters as a versioning problem.** PBKDF2 iteration counts that are appropriate in 2026 will be inadequate in 2030. The spec needs a version field on the encryption block and a deprecation policy. This is real maintenance cost.
2. **Recovery story.** Lost passwords = permanent data loss. Capsules that compose with key-escrow or split-secret schemes would help but multiply the complexity.
3. **Interaction with E.6 signing/log.** Sign before or after encryption? Sign envelope-only, or include ciphertext in the signed scope? Decide before either lands.
4. **What "capabilities" means under encryption.** A capsule that declares `download_capsule` can't actually implement the button until after unlock. Honesty-of-capabilities (Rule 7) gets murky.
5. **Empirical pressure.** Same as E.6 — wait for a reported case where redaction-plus-channel-security isn't sufficient.

**When this earns a v0.4+ schema slot.** Design and ship when *all three* of:

1. A producer or recipient reports a concrete case where redaction + OS-level encryption + authenticated-channel delivery is insufficient;
2. The interaction with E.6 (signing/log) is resolved in design first — encryption and signing have to compose cleanly;
3. A practical answer to the parameter-versioning maintenance burden exists (probably: defer to an external standard like JWE or COSE rather than maintain our own crypto recipe).

Until then: **advise users that the right answer to "I want to share this with only one person" is to encrypt the wrapper, not the capsule.**

### E.8 Validator: distinguish resource-loading `<link>` tags from metadata-only ones

**Issue.** The current `check_no_external_references` validator pattern flags **any** `<link href="...">` tag with a non-`data:` URI as an external resource violation:

```python
(r'<link[^>]+\bhref=["\']\s*(?!data:)[^"\']', 'External <link href> reference (capsule CSS must be inlined)'),
```

The comment ("capsule CSS must be inlined") reveals the intent: catch external stylesheet imports. But the regex is too broad — it also flags **metadata-only** `<link>` tags that don't load any resource:

- `<link rel="canonical" href="https://...">` — SEO canonical hint, no resource loaded
- `<link rel="alternate" href="...">` — alternate-form discovery, no resource loaded
- `<link rel="prev" href="...">` / `<link rel="next">` — pagination hints, no resource loaded

These are pure metadata declarations the browser doesn't fetch. Rule 2 ("no network") doesn't apply to them.

**The right shape.** Refine the check to distinguish resource-loading rel values from metadata-only ones:

- **Resource-loading (should flag external):** `stylesheet`, `preload`, `prefetch`, `preconnect`, `dns-prefetch`, `modulepreload`, `icon` (when not a `data:` URI)
- **Metadata-only (should NOT flag):** `canonical`, `alternate`, `prev`, `next`, `author`, `license`, `help`, `bookmark`, `pingback`

**Implementation sketch:**

```python
def check_external_link_tags(html_scannable):
    """Flag <link> tags that load external resources. Metadata-only rel values
    (canonical, alternate, prev/next, etc.) are allowed because they don't fetch."""
    LOADING_RELS = {"stylesheet", "preload", "prefetch", "preconnect",
                    "dns-prefetch", "modulepreload", "icon"}
    findings = []
    for m in re.finditer(r'<link\b([^>]+)>', html_scannable, re.IGNORECASE):
        attrs = m.group(1)
        href_match = re.search(r'\bhref\s*=\s*["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        if not href_match or href_match.group(1).startswith("data:"):
            continue
        rel_match = re.search(r'\brel\s*=\s*["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        rel_values = (rel_match.group(1).lower().split() if rel_match else ["stylesheet"])
        if any(r in LOADING_RELS for r in rel_values):
            findings.append(f'External <link rel="..." href=...>')
    return findings
```

**Why it's not built yet.** Empirically discovered while wiring `htmlcapsule.org` as the canonical home for the spec: adding `<link rel="canonical" href="https://htmlcapsule.org/">` to a valid capsule made the validator fail it. The canonical link tag was removed for now to keep the validator green. The data-block `links.canonical` field carries the same information machine-readably.

**When this earns a v0.4 schema slot.** Whenever the validator gets its next focused pass — this is a small, contained change that doesn't affect any other rule. Could ship as a v0.3.x validator patch if not bundled with anything else. Low risk: no existing valid capsule uses `<link rel="canonical">` (it would already have failed), so the refinement is purely additive — same capsules still pass, plus canonical-link-bearing ones start passing too.

### E.10 Design-tool bundler compatibility note

**Issue.** Multi-producer interop assumes a producer's output is the artifact a consumer verifies. A subtle integration failure is possible when the producer's *output* is well-formed but a generic post-processing step (typically a "save as standalone HTML" bundler) mutates the artifact *after* verification has cleared. The file shipped to the consumer is then structurally a single-page-app hydration shell, not a capsule, even though every step in isolation looked correct.

Concretely, observed in a Claude Design session with `CAPSULE_CORE.md` attached as context (see RESEARCH.md F19):

1. The model wrote a 40 KB single HTML file that **does** validate against the reference validator (24/25 pass, 1 heuristic warn, 0 fail). Five reserved `id="capsule-*"` blocks present at the byte level, `<main id="capsule-root">` populated with 5,388 chars of pre-rendered visible text, honest provenance (`generator.kind: "llm"`), zero fetch.
2. A subsequent "Save as standalone HTML" step ran a general-purpose bundler over that valid file. The bundler is built to inline external assets for designs that *aren't* self-contained — running it over input that already is self-contained is destructive, not idempotent.
3. The 52 KB output of step 2 is structurally a bundler shell:

```html
<head><style>… thumbnail + loading styles only …</style></head>
<body>
  <div id="__bundler_thumbnail">…</div>
  <div id="__bundler_loading">Unpacking…</div>
  <script>/* bundler reads next two blocks, fetches blob URLs, DOM-injects */</script>
  <script type="__bundler/manifest">… base64+gzip assets …</script>
  <script type="__bundler/template">… HTML template as JSON …</script>
</body>
```

Against the reference validator: 4/10 pass, 5 fail. No reserved `id="capsule-*"` blocks exist *as written* — they would exist after `DOMContentLoaded` hydration runs, but Rule 12 explicitly forbids that pattern (content must be pre-rendered in the HTML at build time, not produced by runtime JavaScript), and Rule 2 is violated by the bundler's `fetch()` calls on blob URLs.

**The mechanism is a process-ordering issue, not a spec-interpretation disagreement.**

Both the producer's verifier and the reference validator agree on the model's actual capsule output (the 40 KB file at step 1) — both score it as conforming. They also agree on the post-bundler file (the 52 KB file at step 3) — both would score it as non-conforming, if asked. The bug is that the verification gate ran at step 1 but did not re-run after step 2 mutated the artifact.

This generalizes as: **verify-before-mutate alone is insufficient; the verification gate must re-run after any pipeline step that touches the artifact, or be the *last* step before the artifact leaves the producer.** A multi-step export pipeline that mutates an artifact between verification and ship can produce a file the verifier never actually checked. This is closer in spirit to the build-pipeline / artifact-signing problem in software supply chains than to a spec-interpretation disagreement.

**What the conversion bridge does (separate path, for canvas mockups not capsules).**

For raw HTML exports from a design canvas — distinct from the bundler output above — a deterministic structural transformation produces valid capsules:

- Strip per-element inline CSS resets (the design canvas's normalization layer, ≈4 MB of bloat per file)
- Strip canvas metadata attributes (`data-om-id`, `data-jsx-*`, `data-om-*`)
- Strip any redundant `@import url('Google Fonts')` (if the same fonts are also embedded as `data:` URIs)
- Unwrap the design canvas's outer wrapper (e.g., `<div class="dc-card">`)
- Merge the two `<style>` blocks (head fonts + body design CSS) into a single `<style id="capsule-style">`
- Wrap the visible content in `<main id="capsule-root">`
- Inject `<script id="capsule-manifest">`, `<script id="capsule-data">`, `<script id="capsule-runtime">`
- Add CSP `<meta http-equiv>` header
- Add an "About this capsule" `<details>` panel for export buttons

This conversion bridge is reusable for any design tool whose raw canvas export is structurally similar. It does *not* apply to bundler-wrapped outputs — for those, the correct mitigation is to skip the bundler entirely on input that is already capsule-shaped.

**Why this is not a rule change.** Rule 12 is doing exactly what it was designed to do: catching the JS-render-everything failure mode in a fresh independent producer. Relaxing the rule to accommodate bundler-SPA outputs would defeat the format's archival-readability property entirely (capsules must be readable years from now, in any browser, including ones where JavaScript fails or is disabled). The spec is not the layer where this problem gets solved — the producer's pipeline ordering is.

**What this earns in v0.4.** Nothing structural — no new fields, no relaxed rules, no validator changes. The right outcome is a **documented integration pattern**:

- **For tool authors:** if your tool produces capsules, the verification gate must be the last thing that touches the artifact, or it must re-run after every subsequent mutation. A generic "make this self-contained" pipeline that runs after the capsule is written will likely destroy the capsule, because the capsule is already self-contained in a specific structural way.
- **For users of design / no-code / app-builder tools:** if your tool offers a separate "save as standalone HTML" step downstream of producing a capsule, that step is probably the bundler — and it may invalidate the capsule. Skip the bundler if the file is already capsule-shaped.
- **For canvas-raw exports** (mockups, not capsules): use a conversion bridge (see structural-transformation list above). The integration point is the canvas export, not the bundler output.
- **For the spec:** no change. This appendix entry is the documentation.

**When this graduates to normative text.** If multiple independent tool integrations hit the same boundary and a common conversion-bridge pattern emerges, the spec could promote that pattern into an informative appendix in a future v0.x — describing the canonical "design-canvas-shape → capsule" mapping without endorsing any specific tool. Until then, the empirical finding lives in RESEARCH.md F19 and the convertor script lives alongside the reference compiler.

**Empirical record.** This is also the first independently-confirmed reproduction of an LLM-kind producer reaching conformance directly from `CAPSULE_CORE.md` as a prompt input — strengthening the multi-producer interop claim in §1. The model produced a 24/25-passing, 0-fail file; the integration failure was downstream of the model, in the bundler step.
