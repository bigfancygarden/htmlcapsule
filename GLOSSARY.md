# Capsule — Glossary

Canonical definitions of terms used across the Capsule project. The same definitions appear inside the landing page ([`index.html`](index.html)) for readers, and inside individual capsules where relevant.

If you find a term missing, ambiguous, or used inconsistently in a capsule, that's signal — open an issue.

---

## Core concepts

### Capsule

A single-file HTML document with a manifest, data block, rendered content, styling, and a small runtime — packaging a bounded snapshot for sharing, archiving, and re-loading. A profile of HTML, not a new file format. The format was previously called "Artifact Capsule"; the shortened name lands the *sealed* metaphor and avoids collision with Claude's "artifact" (which means a working canvas, not a sealed snapshot).

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

### Universal AI reader

An AI platform that can read many file types and connect to many sources directly (Claude, ChatGPT with connectors, Gemini, etc.). Complementary to capsules — a smart reader still needs explicit packaging, provenance, intent, and usage rules to reason responsibly.

### Interactive archive

A capsule with runtime tools — measure, filter, search, annotate, sort, export, print, domain-specific affordances like `map.measure` — layered on top of pre-rendered content. The operational litmus is the **JavaScript-off test**: if JS doesn't run, the substance of the artifact is still there (the tools are just gone). Tools query the content; tools never produce it. Contrast with an "app," where the substance itself depends on JS to exist — forbidden by Core rule 12. Named in spec v0.3.4 (§2.3) to head off the recurring misreading that "archives, not apps" means "no interactive features at all." Mintel's `domain.exploration_map` capsules are the canonical example: click-to-measure and click-to-find-coordinates on top of static map content (rendered chrome plus image fallback for geometry).

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

The required JSON block (`<script id="capsule-manifest">`) carrying identity, provenance, capabilities, and privacy metadata. Required fields per Core v0.3.0: `spec_version`, `capsule_version`, `uuid`, `title`, `description`, `type`, `created_at`, `generator`, `source`, `privacy`, `capabilities`. Optional: `parents[]` (provenance — UUIDs of upstream capsules this one was forked from). The v0.1 legacy names `artifact_id` and `artifact_version` are still accepted under v0.2/v0.3 compatibility; `capsule_id` (the slug) was deprecated in v0.3 and is slated for removal in v0.4.

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

Declared affordances the capsule must implement. Required minimum: `about` plus at least one export.

Standard capabilities:
- `about` — a panel showing the manifest (usually a `<details>` block)
- `copy_as_json` — copies the data block to clipboard
- `copy_as_markdown` — copies a markdown rendering to clipboard
- `download_json` — downloads the data as a `.json` file
- `print_to_pdf` — invokes the browser print dialog
- `export_response` — produces a structured response payload (for interactive capsules)

**Capabilities don't lie.** Every capability declared in the manifest must have a working implementation.

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

*Glossary v0.3.0 · 2026-05-19. Lives alongside [`CAPSULE_CORE.md`](CAPSULE_CORE.md) (currently v0.3.0) and [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) (currently v0.3.2).*
