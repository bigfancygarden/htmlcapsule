# Capsule — Glossary

Canonical definitions of terms used across the Capsule project. The same definitions appear inside the landing page ([`index.html`](index.html)) for readers, and inside individual capsules where relevant.

If you find a term missing, ambiguous, or used inconsistently in a capsule, that's signal — open an issue.

---

## Core concepts

### Capsule

A single-file HTML document with a manifest, data block, rendered content, styling, and a small runtime — packaging a bounded snapshot for sharing, archiving, and re-loading. A profile of HTML, not a new file format. Every Capsule keeps the same five-block envelope; optional Capsule profiles are validation overlays, not alternate structures. The format was previously called "Artifact Capsule"; the shortened name lands the *sealed* metaphor and avoids collision with Claude's "artifact" (which means a working canvas, not a sealed snapshot).

### Conversation Capsule

A sealed, sourced summary of an AI-assisted work session. Preserves conclusions, decisions, caveats, open questions, and lineage. The dominant family in the early personal capsules (batches 1–47).

### Domain Capsule

A sealed, AI-ready export of a domain object: map, dataset, document, code snapshot, claim package, deal, implementation notes, design system, and so on. Domain-specific schema lives in the data block; the outer contract (manifest, sealed convention, capabilities) is unchanged.

Named domains and their schemas live in [`spec/DOMAIN_CAPSULES.md`](spec/DOMAIN_CAPSULES.md). The namespace is open: anyone can declare a new domain using the `domain.<name>` naming convention.

Currently shipped with formal schema:
- `domain.implementation_notes` — design decisions, deviations, tradeoffs, and open questions captured while implementing a spec. Canonical example: [`spec/examples/implementation_notes_example.html`](spec/examples/implementation_notes_example.html).
- `domain.design_system` — tokens, components, patterns, and usage notes as a portable design-system snapshot.

Subtypes proposed, prototypes exist, formal schema not yet written:
- `domain.map` — spatial data with layers, CRS, data dictionary, interpretation notes
- `domain.dataset` — tabular data with schema, units, quality notes
- `domain.document` — PDF/report/contract with metadata and extracted claims
- `domain.code` — repo snapshot with architecture, dependencies, known issues
- `domain.claims` — mining/land-tenure data with ownership and uncertainty
- `domain.deal` — LOI/option/royalty/transaction terms

### Project Capsule

A sealed snapshot of where a sustained thing (a property, a client, an investigation, a decision in progress) stands at a moment. The unit you'd hand to a colleague to bring them up to speed on something you've been working on for a while.

It's defined by **scope**, not by composition. Conversation Capsules cover one session. Domain Capsules cover one object (one map, one dataset, one deal). Project Capsules cover a thing bigger than either — something with multiple sessions and multiple objects already attached to it.

In practice it pulls from earlier Conversation and Domain capsules and adds its own synthesis on top. A property dossier capsule for a mining claim group, for example, might pull from three conversation capsules where the property was discussed, a map capsule with the claim boundaries, a claims capsule with ownership history, a deal capsule for the LOI, plus a synthesis section saying "what we know, what we don't, what's next." That's a Project Capsule.

The three families answer different questions:
- Conversation Capsule: *what came out of this chat?*
- Domain Capsule: *what is this object, in a form AI can reason about?*
- Project Capsule: *what do we know about X so far?*

---

## Positioning terms

### Sealed handoff format

The role capsules play after work stops being actively edited: a frozen, portable, source-aware package for future use rather than ongoing mutation. Contrast with Canvas/Artifacts (the *editing* layer) and repos (the *production* layer).

### Portable context contract

The capsule's distinctive promise — not merely that an AI can open the file, but that the object declares what it is, where it came from, what it means, and how it should be used.

### Anti-context-loss

The project's positioning. Capsules exist so useful AI work survives across tools, time, sessions, and platform churn — not as an attack on AI platforms, but as durable infrastructure complementary to them.

### Document-first artifact

The technical thesis underneath the format: **a capsule is a document first, an app second.** *Apps when alive. Documents when dormant.* HTML and CSS are the base substrate; JavaScript is a runtime upgrade layered on top. A well-built capsule stacks interactivity in tiers — Tier 0 static document → Tier 1 native HTML controls (`<details>`, `<audio>`) → Tier 2 CSS-state machines (radio-button tabs, `:target`) → Tier 3 precomputed alternates → Tier 4 JavaScript runtime — such that the substance survives at the lowest tier the producer can land it at, and higher tiers are progressive enhancement. Open the same file in iOS QuickLook and Safari: same file, two experiences, no degradation cliff. The 5-tier framework lives in [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) §2.3.2 (added v0.3.8); the implementation primitives live in §2.3.3. Pairs with **Interactive archive** below (which names what's permitted under Rule 12) and with the **Graceful degradation** principle in spec §2.3.1 (which names what survives).

### Capsule boundary

The definitional line between what's inside a capsule and what isn't. **Inside:** the five required inline blocks, embedded media as `data:` URIs, runtime JavaScript operating on the inline data block, user-provided files dropped into the runtime at use time, computed-at-runtime derived data. **Outside:** network fetches (`fetch`, `XMLHttpRequest`, dynamic imports, WebSockets), external resources (`<script src>`, remote stylesheets, `<img src=http(s)://...>`), live data from APIs / databases / LLM endpoints / RSS feeds, runtime authentication or session state held on remote servers. **The seal is not a restriction; it's what makes the format possible.** Without the boundary there is no floor, no archive, no "open this in ten years and it still works." Rule 2 in [`CAPSULE_CORE.md`](CAPSULE_CORE.md) is the technical statement of the boundary; [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) §1.5 (added v0.3.8) gives the conceptual treatment. Artifacts that cross the boundary — web apps, live dashboards, connected documents, hosted artifacts — aren't *degraded capsules*; they're a different category of artifact entirely, solving a different problem (anti-staleness, always-current data) with a different commitment. Both legitimate; not the same thing. The format doesn't coin a name for what isn't a capsule because the category on the other side already has names; it just names where the line is.

### Bundle

The sibling format to Capsule, introduced in project v0.4.0 (2026-05-24). A Bundle is a **manifested directory of files** — viewers, data, and assets — rather than a single sealed HTML file. Like Capsule, every Bundle has an identity (UUID minted at seal time), integrity (SHA-256 hashes per file recorded in the manifest), and provenance (manifest records authorship). Unlike Capsule, a Bundle MAY have external dependencies (CDN libraries, mapping stacks) declared in `external_dependencies`; those dependencies support viewing, while the artifact's primary data and evidence belong in the file inventory. Bundle is for artifacts that exceed what a Capsule can reasonably contain — heavy georeferenced rasters, LiDAR point clouds, multiple viewer HTMLs, working substrates from which sealed Capsule reports are eventually derived. As of Bundle v0.1.1, producers SHOULD declare `bundle_profile` (`viewer`, `data_package`, `multi_entry`, or `project_archive`) to name the top-level shape of the manifested file set. Spec lives at [`spec/BUNDLE_SPEC.md`](spec/BUNDLE_SPEC.md), with an initial schema at [`spec/bundle.schema.json`](spec/bundle.schema.json), validator at [`compiler/validate_bundle.py`](compiler/validate_bundle.py), and fixture at [`spec/examples/minimal_bundle/`](spec/examples/minimal_bundle/). The format emerged from real producer pressure (the strata leak investigation; see [F31 in RESEARCH.md](RESEARCH.md)). Composition primitive: a Capsule can be derived from a Bundle; because Capsule `parents[]` is strict Capsule-to-Capsule lineage, the source Bundle belongs in the Capsule's `derived_from[]` array with `type: "bundle"`.

### Bundle profile

A recommended Bundle manifest field declared as `bundle_profile`. It describes the file-set pattern, not the subject domain and not the viewer's interactivity level. Current values: `viewer` (one primary HTML viewer over inventoried files), `data_package` (data/file inventory is primary), `multi_entry` (multiple meaningful entry points), and `project_archive` (bounded working/output folder preserved with provenance). This is deliberately separate from Capsule `profile`: Capsule profile answers "how does one sealed HTML envelope behave?"; Bundle profile answers "what kind of manifested file set is this?"

### Sibling format

A second format in the htmlcapsule family that shares Capsule's discipline (identity / integrity / provenance) but trades on the sealed-boundary commitment. Bundle is the first declared sibling format. It is not a relaxed Capsule: if one offline HTML file honestly holds the artifact, use Capsule; if the artifact needs a manifest-described file set, heavy assets, multiple viewers, or declared external libraries/resources with primary artifact data local, use Bundle. Future sibling formats could emerge if real producer pressure surfaces a use case neither Capsule nor Bundle handles well; the project's empirical-pressure-driven evolution principle scales from rule-level (within a spec) to format-level (within the family).

### Producer / format / host pattern

The three-role split that makes the htmlcapsule family of formats composable: **the host stays light; the producer can be heavy and domain-specific; the portable format is the contract that lets them compose.** Named explicitly in project v0.4.0 (see [F31](RESEARCH.md)) once the Bundle family made the pattern visible at two scales. Producer projects (Mintel, capsule-midi, Shasta, capsule-photo, leak) do the heavy work in whatever stack fits the domain. Hosts (MinDev, htmlbin, Stratabot) receive sealed/manifested artifacts and serve them without needing to know what tooling produced them. The format (Capsule, Bundle, or a future sibling) is the contract that binds them. The pattern instantiates twice currently: Mintel → Capsule → MinDev, and leak → Bundle → Stratabot.

### Floor declaration

The optional `<noscript>` reader-notice pattern recommended for tier-4 capsules (DAW transport, live mix, search, in-capsule LLM interaction) so a reader in a no-JS preview surface (iOS QuickLook, Mail preview, archival viewer) understands what tier they're seeing and what the runtime tier adds. *Not an apology* for missing features — a declaration that names the floor. Lives in [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) §2.3.3 (added v0.3.8). Worked snippet uses layer vocabulary (*"You're viewing the document layer of this capsule"*) rather than mechanical framing (*"JavaScript is disabled"*) — the reader didn't disable anything, they're in a preview surface that doesn't run scripts. Tier 0–3 capsules don't need the notice; the substance speaks for itself and there's nothing meaningful to miss.

### Universal AI reader

An AI platform that can read many file types and connect to many sources directly (Claude, ChatGPT with connectors, Gemini, etc.). Complementary to capsules — a smart reader still needs explicit packaging, provenance, intent, and usage rules to reason responsibly.

### Interactive archive

A capsule with runtime tools — measure, filter, search, annotate, sort, export, print, domain-specific affordances like `map.measure` — layered on top of pre-rendered content. The operational litmus is the **JavaScript-off test**: if JS doesn't run, the substance of the artifact is still there (the tools are just gone). Tools query the content; tools never produce it. Contrast with an "app," where the substance itself depends on JS to exist — forbidden by Core rule 12. Named in spec v0.3.4 (§2.3) to head off the recurring misreading that "archives, not apps" means "no interactive features at all." Mintel's `domain.exploration_map` capsules are the canonical example: click-to-measure and click-to-find-coordinates on top of static map content (rendered chrome plus image fallback for geometry).

### Capsule profile

A validation overlay declared in the manifest as `profile`, currently `static`, `interactive`, or `data`. Profiles describe how the fixed five-block envelope is used; they do not make any block optional and they do not turn Bundle into a Capsule subtype. `static` means the document layer is the primary experience; `interactive` means runtime tools enhance an already-understandable document layer; `data` means the structured data block is first-class while `capsule-root` still carries a meaningful summary/fallback view.

### Presentation declaration

An optional manifest entry in `presentations[]` that declares a capsule-owned view such as `reader`, `mobile`, `print-letter`, `slides`, `reel`, or `interactive`. Presentation declarations are not Capsule profiles: `profile` answers how the five-block envelope behaves; `presentations[]` answers which artifact-owned views a host may surface. They are also not Vault or host custody views: Safe Preview, Source, Inspector, Quarantine, and Graph remain app-owned. For single-file Capsules, presentation entries are fragment selectors that resolve inside the same HTML file; file paths and multi-entry viewers belong to Bundle.

---

## The four layers

A useful frame for where capsules sit in the AI work lifecycle:

| Layer | Job | Tool |
|---|---|---|
| **Think** | Explore ideas | Chat |
| **Shape** | Build editable working objects | Canvas, Artifacts, IDE |
| **Seal** | Freeze and hand off | **Capsules** |
| **Harden** | Operationalize for production | Repos, Codex, Git |

Capsules occupy the seal layer — the one nobody had named, and the layer where useful chats currently die.

A related **ecosystem-stack framing** in [`PRECEDENTS.md`](PRECEDENTS.md) maps the same lifecycle to the *tools that populate each slot* rather than the actions a knowledge worker takes: **substrate** (HTML itself, per Karpathy and Thariq) → **live editing** (Canvas, Artifacts, html-docs, Workplane) → **seal** (HTML Capsule) → **host** (htmlbin, MinDev, self-hosted) → **discover** (`llms.txt`, per Jeremy Howard). The four-layer model is verb-shaped (what a knowledge worker does); the ecosystem stack is noun-shaped (where tools sit in the landscape). Both are useful; both name "seal" as the slot Capsule occupies.

---

## Production paths

A capsule can come into existence two ways:

### Export

Wrapping an already-finished work product (Canvas doc, artifact, document, data extract) into capsule format. The work is done; the capsule is the package.

### Compile

Assembling a capsule from a conversation plus a private store, optionally adding fresh source-checks at compile time. The conversation is raw material; the capsule is the output.

Compile-path capsules dominate real-world use — both the reference-compiler templates in this repo and independent compiler-kind producers (e.g., Mintel for geospatial deliverables). The LLM-produced path is also common: any LLM given the Core spec produces compile-path-equivalent capsules at high fidelity.

### Fresh source-check

Authoritative source verification performed at capsule-compile time, beyond what the original conversation contained. Adds verifiability without altering the original chat. The canonical briefing example ([`spec/examples/briefing_example.html`](spec/examples/briefing_example.html)) demonstrates this — the briefing carries a regulatory cross-check the source conversation never had.

---

## Structural fields

### Manifest

The required JSON block (`<script id="capsule-manifest">`) carrying identity, provenance, capabilities, profile, declared presentations, and privacy metadata. Required fields per Core v0.3.0: `spec_version`, `capsule_version`, `uuid`, `title`, `description`, `type`, `created_at`, `generator`, `source`, `privacy`, `capabilities`. Optional: `profile` (validation overlay), `presentations[]` (capsule-owned views), `parents[]` (provenance — UUIDs of upstream capsules this one was forked from), and `derived_from[]` (non-Capsule provenance). The v0.1 legacy names `artifact_id` and `artifact_version` are still accepted under v0.2/v0.3 compatibility; `capsule_id` (the slug) was deprecated in v0.3 and is slated for removal in v0.4.

### Data block

The required JSON block (`<script id="capsule-data">`) carrying the structured snapshot. **Read-only at runtime.** The source of truth for exports. May follow `records[]` shape (for discrete items) or single-document shape (for syntheses).

### Five required blocks

The minimum structural contract per Core v0.3.0 rule 3:

1. `<script id="capsule-manifest" type="application/json">` — the manifest
2. `<script id="capsule-data" type="application/json">` — the data snapshot
3. `<style id="capsule-style">` — all CSS
4. `<main id="capsule-root">` — the UI root
5. `<script id="capsule-runtime">` — all JavaScript

### Capabilities

Declared affordances the capsule must implement. Required minimum: `about` plus at least one export. Capabilities are declarations, not permissions.

Standard capabilities:
- `about` — a panel showing the manifest (usually a `<details>` block)
- `copy_as_json` — copies the data block to clipboard
- `copy_as_markdown` — copies a markdown rendering to clipboard
- `download_json` — downloads the data as a `.json` file
- `print_to_pdf` — invokes the browser print dialog
- `export_response` — produces a structured response payload (for interactive capsules)

**Capabilities don't lie.** Every capability declared in the manifest must have a working implementation.

Capability classes:
- Core — controlled names the base spec understands (`about`, exports, `search`, `filter`, `media.*`, etc.)
- Restricted — known declarations a host or reader may deny by default (`storage.local`, `native_bridge`, `ai_context.export`)
- Extension — namespaced/domain names (`x-mining.map`, `org.example.feature`)
- Prohibited — invalid in Capsules (`network.request`)

### Provenance

Who or what produced the capsule, when, and from what source. `generator.kind` is one of:

- `compiler` — produced by a deterministic compiler from structured input
- `llm` — produced by an LLM
- `human` — written by hand
- `hybrid` — collaboratively produced (e.g., LLM-authored, human-reviewed; human-authored with AI assistance)

If an LLM produced the HTML: set `kind: "llm"` and `version: "<model-id>"`.

### State (emerging convention)

A field marking a capsule as `sealed`, `draft`, `superseded`, or `deprecated`. Not yet required by the Core spec but used inside `capsule_metadata_notes` in newer capsules. Sealed capsules are not edited in place — revisions are forks.

### Lineage (emerging convention)

A pattern for capsules to name a parent (`parent_capsule_id`, `parent_snapshot_id`) so forks and supersessions are traceable. Maps onto the ChatGPT branching pattern: each branch could produce its own capsule with a parent reference.

### `ai_usage_guidance` (emerging convention)

An optional Domain Capsule field declaring:

- `allowed_tasks` — tasks the AI is permitted to perform with this capsule
- `restricted_tasks` — tasks the AI should refuse
- `preferred_language` — tone or register for AI output derived from the capsule

The acceptable-use clause aimed at the next model, not the next human. First proposed in capsule #46 in the context of Map Capsules ("summarize the map but do not estimate resources or imply economic viability").

---

## Project phases

Four phases the project can be discussed and engaged with independently:

| Phase | Name | State |
|---|---|---|
| 1 | Format | Exists (Core v0.3.0, full spec v0.3.2) |
| 2 | Compiler | Half-built (77 working personal capsules in this repo; Mintel as first independent compiler-kind producer) |
| 3 | Domain capsules | Partial — `domain.implementation_notes`, `domain.design_system`, and `domain.exploration_map` documented; more pending |
| 4 | Network layer | Not built; possibly never |

The format pitch (phase 1) is *not* the compiler pitch (phase 2) is *not* the domain pitch (phase 3). Different people will care about different phases.

---

## What this deliberately is not

- **Not a new file format.** It's HTML.
- **Not a new editing surface.** Canvas and Artifacts already cover that.
- **Not a SaaS or product.** No accounts, no server, no service.
- **Not a competitor to MCP.** MCP is a live connection protocol; a capsule is a sealed snapshot. They're complementary.
- **Not a knowledge graph or universal ontology.** Per-type data schemas welcome.
- **Not anti-platform.** Anti-context-loss.
- **Not a standard you have to comply with.** A loose discipline.
- **Not finished.** Active research.

---

## Related work

References that have come up in discussion (positioned, not endorsed). Longer write-ups and further-out cousins live in [`PRECEDENTS.md`](PRECEDENTS.md).

**Historical and contemporary standards:**

- **MPEG-21 / Digital Item** — closest historical precedent. MPEG-21's Digital Item bundled a media object with structure, identity, rights, relationships, and adaptation rules into one self-describing package. Same pattern, different substrate: capsules apply the wrapper logic to AI work outputs rather than media assets. The framing "a file alone is not enough" originated here. Capsules can be thought of as **cognitive Digital Items** — the AI-work analogue.
- **C2PA** — current standard for cryptographically signed content provenance. Backed by Adobe, Microsoft, BBC, OpenAI. The protocol to study if capsules ever add signing.
- **BagIt** (RFC 8493) — simplest possible "package + manifest" precedent. Directory with a checksum manifest. Widely deployed in library digital preservation.
- **W3C PROV** — canonical vocabulary for representing "X came from Y" provenance relationships.
- **RO-Crate** — research-object packaging using JSON-LD. Folder/zip rather than HTML, but the same "manifest + provenance + content" pattern. A capsule could embed RO-Crate metadata in its data block.
- **MHTML** — single-file web archive. No structured manifest, no provenance contract. Mostly abandoned (Chrome dropped support 2018).
- **TiddlyWiki** — single-file wiki since 2004. Same substrate as capsules but a workspace (mutable), not a snapshot (sealed).
- **PDF** — the previous answer to "portable finished work." Loses interactivity and structure.

**AI / ML adjacent:**

- **Hugging Face Model Cards / Dataset Cards** — closest contemporary AI analogue. Markdown + YAML frontmatter describing a model's context, bias, intended use, limitations. Same bet, applied to ML artifacts.
- **MCP (Model Context Protocol)** — live AI-tool connection protocol. Complementary, not competing.
- **OpenAI Canvas / Anthropic Artifacts** — the editing surfaces capsules come *after*.

---

*Glossary v0.4.0 · 2026-05-24. Lives alongside [`CAPSULE_CORE.md`](CAPSULE_CORE.md) (currently v0.3.0), [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) (currently v0.3.9), and [`spec/BUNDLE_SPEC.md`](spec/BUNDLE_SPEC.md) (currently v0.1.1 — the sibling format).*
