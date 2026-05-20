# Capsule — Precedents and Related Work

A working note on prior art and contemporary projects that share parts of the pattern. Not a literature review — just enough to position the work honestly and avoid claiming things are novel when they aren't.

The capsule pattern (single self-describing object with manifest, provenance, and content) has a long history in standards work. Most of it lives in research preservation, library archives, scholarly publishing, and more recently AI/ML "card" formats. The capsule project is a specific variant of an old pattern: single-file HTML, AI-work substrate, sealed convention, minimal contract.

Confidence note: positioning is solid; specific versions, governance details, and current activity levels need checking before any of these get cited in user-facing material.

## Current voices in HTML-for-AI

Not precedents in the historical sense. Contemporaneous voices arguing related cases in 2026. Worth tracking because the discourse is forming in real time and the capsule project sits inside it rather than upstream of it.

The wave around "HTML is the new markdown" (Thariq's thread, the HN debate, Simon Willison's amplification, follow-on tooling like Display.dev and `dogum/html-artifacts`) has validated the *symptom* — that AI tools want to emit rich single-file HTML and that recipients want to read it. It has not yet validated any particular *standard* for what those files should contain. Capsule's bet is that the standard layer is what the substrate is still missing; the wave is the demand signal, not the answer.

### Thariq Shihipar (Claude Code, Anthropic)

Substrate evangelist. The originating public articulation of "HTML is the new markdown." Active on X (@trq212) and on podcasts (the *How I AI* episode with Claire Vo, May 2026). Demonstrates the pattern with concrete examples: `implementation-notes.html` from spec implementation work, `design-system.html` as a portable living style guide, weekly HTML status updates sent to managers. Has assembled a public gallery of 20 HTML artifacts across nine categories (code review, exploration, design systems, prototyping, diagrams, research, reports, custom editors, agent UI).

**Position:** HTML as the live editing medium during work. Long markdown plans aren't read; long HTML plans are. The substrate has already won; what's missing is adoption of the practice.

**Relevance to capsules:** The substrate evangelist provides the cultural air cover. Capsules formalize the contract underneath the substrate. His `implementation-notes.html` pattern is the canonical example for the project's `domain.implementation_notes` schema; his living design-system pattern is the canonical example for `domain.design_system`.

### Blake Crosley

Control-surface framing. Blog post: "HTML Is the Format AI Agents Want" ([blakecrosley.com/blog/html-is-the-format-agents-want](https://blakecrosley.com/blog/html-is-the-format-agents-want)). Argues HTML preserves spatial structure, interaction, visual hierarchy, and density that markdown linearizes away. Specific stack bet: FastAPI + HTMX, server-rendered, where the format the model produces and the format the browser renders are the same. Cites Thariq's gallery as empirical evidence.

**Position:** HTML as the control surface agents should produce. Live, server-rendered, interactive. The format the user can actually inspect determines what they can verify.

**Memorable lines worth knowing:**
- "The format you ask for is part of the runtime contract."
- "Substrate matters more than components."
- "The format the model wants to produce and the format the browser already renders are the same."

**Relevance to capsules:** Reinforces the substrate case from a different angle (agent UI rather than chat output). Sharpens the lifecycle distinction without naming it. Blake is live; capsules are sealed. Both valid, both compatible, different slots.

### The three-position picture

Same substrate, three positions on the lifecycle:

| Voice | Frame | Slot |
|---|---|---|
| Thariq | Substrate | "HTML is the new markdown" — the editing medium |
| Blake | Control surface | "Format is part of the runtime contract" — agent UI / live render |
| This project | Sealed handoff | The portable archive — manifest, sources, sealed convention |

The three positions are healthy differentiation, not competition. Each sits on the same substrate. None is wrong about HTML. The project's specific contribution is the contract that makes HTML files travel after the live work is done.

## Direct neighbors

### RO-Crate

A packaging standard for research artifacts (data, software, workflows) used by life-sciences infrastructure like ELIXIR and Galaxy, plus digital humanities and reproducibility communities. The unit is a directory or zip containing a `ro-crate-metadata.json` at the root, written in JSON-LD. The metadata model is rich: typed entities (Dataset, SoftwareApplication, Person, Organization), relationships between them, conformance to schema.org. Has *profiles* (Workflow RO-Crate, Workflow Run Crate, Provenance Run Crate) that constrain the general format for specific use cases.

**Where it overlaps with capsules.** Central bet: an artifact needs structured metadata and provenance to be useful later.

**Where it differs.** Folder or zip, not a single HTML file. No rendering layer; you can't open it directly. Designed for archive ingestion (Zenodo, institutional repositories), not browser viewing. Metadata is heavier — full JSON-LD with typed entities, not a flat manifest.

**Possible integration.** A capsule could conform to RO-Crate's metadata vocabulary inside its data block, getting both the capsule's portability and RO-Crate's ecosystem.

### MHTML

The 1999 multipart-HTML format. One file containing HTML plus all assets as MIME parts. Used by old IE "Save As Web Archive" and by Opera. Chrome dropped MHTML save support in 2018. Effectively abandoned.

**Where it overlaps.** Single-file packaging, everything inline.

**Where it differs.** No manifest, no provenance, no structured data, no rendering contract beyond "browser will probably render it."

**Lesson for capsules.** Single-file packaging is necessary but not sufficient. Without a structured contract, the format is just a worse zip.

### TiddlyWiki

Single-file wiki since 2004 (Jeremy Ruston). The whole wiki — content, JavaScript, styling, plugins — lives in one HTML file. You edit it in the browser; saving writes a new version of the same HTML. Active community, version 5.x. Used for personal notebooks, public sites, project knowledge bases.

**Where it overlaps.** Substrate is identical. Single-file HTML, everything inline, works from `file://`, portable.

**Where it differs.** *Purpose.* TiddlyWiki is a workspace (mutable, editable, lives over time). A capsule is a sealed snapshot (immutable, finished, hands off).

**Relationship.** They're orthogonal. TiddlyWiki is an editing surface; capsules are what you'd export from one. You could host capsules inside a TiddlyWiki without conflict.

## Active and relevant

### C2PA (Coalition for Content Provenance and Authenticity)

Most current and most relevant for the AI-provenance angle. Backed by Adobe, Microsoft, BBC, OpenAI, others. Embeds signed provenance metadata in media files; used for tracking AI-generated images and video. Cryptographic signatures, manifest references, action history.

**Relevance to capsules.** If capsules ever add cryptographic signing or an integrity layer, C2PA is the protocol to study and possibly align with. The signing model is mature and has industry adoption.

### BagIt (RFC 8493)

Library of Congress / IETF standard. Simplest possible packaging: a directory with a manifest file listing checksums of every payload file. Widely deployed in institutional preservation, much simpler than RO-Crate.

**Relevance to capsules.** When the optional `integrity` block in the Core spec gets implemented, it should be informed by BagIt's checksum-manifest pattern. Possibly directly compatible.

### Hugging Face Model Cards / Dataset Cards

Markdown with YAML frontmatter. "The model needs to come with its context" — bias, intended use, limitations, training data summary, evaluation results. Influential in the AI/ML world; now standard practice for releasing models.

**Relevance to capsules.** Closest contemporary AI analogue. Same bet — an artifact (a trained model) needs to ship with its provenance, intended use, and limitations. Capsules generalize the pattern to AI work outputs (conversations, syntheses, maps, decisions) rather than just models.

### W3C PROV

Canonical standard for representing "X came from Y" relationships. PROV-O (OWL ontology), PROV-N, PROV-JSON. Not a packaging format; a *vocabulary* for provenance claims. Used inside many other formats (RO-Crate uses PROV concepts).

**Relevance to capsules.** The underlying vocabulary for any rigorous provenance treatment. If capsules ever formalize lineage and source-attribution into a structured field, PROV is the canonical model to align with.

## Further-out cousins

These share parts of the pattern but are more distant from the capsule use case. Grouped for orientation, not for comprehensive coverage.

### Research preservation (XML-heavy, library-grade)

- **METS / PREMIS** — XML standards for digital preservation. The "make sure this artifact survives 100 years" world. Comprehensive, complex.
- **JATS / BITS** — NISO standards for scholarly publishing. Single-file XML with article metadata, body, references.
- **TEI (Text Encoding Initiative)** — XML standard for representing humanities texts. Dominant format in digital humanities for decades.

### Packaging with manifest (substrate pattern match)

- **EPUB** — ZIP-based ebook format. Manifest, content, metadata, navigation. Probably the most successful consumer "package + manifest" format.
- **OpenDocument / OOXML** — Word and Excel files are ZIP packages with internal manifest XML and relationships folders. Same pattern, rendered by Office.
- **Frictionless Data Package** — JSON manifest plus tabular data files. Data-engineering version.

### AI / ML adjacent

- **Jupyter `.ipynb`** — JSON with cells, outputs, metadata. Famous provenance problems (outputs go stale, often hand-edited). HTML export of a notebook is closer to a capsule than the `.ipynb` itself.
- **Activity Streams / ActivityPub** — JSON-LD social activity objects. Different category but same JSON-LD-as-portable-schema pattern.
- **SBOMs (SPDX, CycloneDX)** — Software Bill of Materials. Manifest + provenance for software components. Has had a renaissance with supply-chain security work.

### Single-file substrate, different goal

- **Datasette** — single-file SQLite database served as a queryable HTML interface.
- **Obsidian / Logseq / Roam** — markdown with bidirectional links. Mutable, editing-focused.

### Cultural-heritage / archival

- **IIIF (International Image Interoperability Framework)** — JSON-LD protocol for image and AV. Used by museums and libraries.
- **WARC** — Web ARChive format. Single file holds many web responses with headers. Used by Internet Archive's Wayback Machine.
- **OCFL (Oxford Common File Layout)** — layout spec for digital preservation storage. Designed for institutional repositories.

## What's most worth pulling into the project

If only one or two of these get studied closely, in order of relevance:

1. **C2PA** — for any future signing / integrity work. Current, well-backed, AI-aware.
2. **BagIt** — for the simplest possible integrity-block pattern.
3. **RO-Crate** — for the metadata-vocabulary alignment, especially if capsules ever ship a `domain.dataset` or `domain.research` schema.
4. **Hugging Face Model Cards** — for the AI-acceptable-use framing that's already shaping into `ai_usage_guidance` on Domain Capsules.

## Confidence and TODOs

- All entries: positioning is reliable; versions and recent governance need verification before public citation.
- C2PA, BagIt, EPUB, Hugging Face Model Cards, W3C PROV — most confident (mature, widely documented, widely deployed).
- RO-Crate, TiddlyWiki, MHTML — solid.
- METS, JATS, TEI, IIIF, OCFL, WARC — real but less recently checked; verify before relying on specifics.
- Open question: which of these have active integration paths (importers, exporters, cross-format converters) that capsules could plug into without inventing a new protocol?

---

*Working notes, kept alongside [`CAPSULE_CORE.md`](CAPSULE_CORE.md), [`GLOSSARY.md`](GLOSSARY.md), and [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md). Not a deliverable, not a literature review — just enough background to position the project honestly.*
