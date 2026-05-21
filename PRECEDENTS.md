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

### Andrej Karpathy

Substrate-progression articulation. Public posts in 2026 laid out a four-step progression for AI output formats — raw text → markdown → HTML → eventually interactive neural simulations — naming HTML as "early but forming new good default" and recommending "structure your response as HTML" as a practical prompt-time tip ([X post, May 11 2026](https://x.com/karpathy/status/2053872850101285137); archived as a first-class quote-archive capsule at [`voices/karpathy-html-progression-2026.html`](voices/karpathy-html-progression-2026.html)). Separately publishes an "LLM wiki" pattern ([gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), April 2026) — a personal knowledge base of markdown files an LLM authors and maintains, framed as "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

**Position:** HTML as the current best step on a named progression. Markdown for the working/source layer (the wiki he maintains); HTML for the output/render layer (the answer to a query). The two positions reconcile if you read them as format-follows-lifecycle: working format vs. publishing format.

**Memorable lines worth knowing:**
- "Try ask for HTML."
- "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
- "Vision is the preferred output channel for AI."

**Relevance to capsules:** The progression names *why* the discipline matters now. If HTML is the current load-bearing step, then a contract on the HTML file is the load-bearing piece of discipline. Capsule sits between his two layers — HTML as the substrate, with a contract on the file.

### Utkarsh Sengar — htmlbin.dev

Hosting-layer articulation. Launched [htmlbin.dev](https://htmlbin.dev/) in May 2026 (about the same week as htmlcapsule). Tagline: *"API for agents to share HTML. One human auth step, then your agent publishes over HTTP."* Self-positioned as "Agent-first HTML hosting." Stack: Cloudflare D1 + KV. Flow: agent generates HTML, calls the htmlbin API, gets back a short URL like `htmlbin.dev/p/{slug}` with a `/raw` endpoint for byte-identical fetch. Side-project author with prior Webflow / Upwork / OpenTable / eBay experience ([utsengar.com](https://utsengar.com/)).

**Position:** Hosting infrastructure for agent-emitted HTML as a primitive. No format discipline imposed — accepts any self-contained HTML; the host's job is publishing, not validating.

**Memorable lines worth knowing:**
- "Agent-first HTML hosting."
- "First publish needs one human click; after that, the agent owns it."
- "Drop HTML. Get a public URL."

**Relevance to capsules:** htmlbin is the public hosting layer that htmlcapsule didn't build. The two are complementary slots in a stack: Capsule supplies the format discipline (manifest, integrity, no network, pre-rendered content); htmlbin supplies the publishing flow. A valid capsule can be hosted on htmlbin, on MinDev, or self-hosted — the format is hosting-agnostic. The independent convergence of htmlbin's hosting pattern with MinDev's (short URL + `/raw` endpoint + minimal chrome + honest authorship attribution) is documented as F21 — empirical evidence that the host-contract sketch in Appendix E.7 is a real shape independent producers reach on their own.

### Jeremy Howard — llms.txt

Site-discoverability articulation. Published the [`/llms.txt` proposal](https://llmstxt.org/) in September 2024 (fast.ai / Answer.AI). A markdown file at the root of a website that gives a curated, LLM-friendly index of the site's content — H1 with site name, optional blockquote summary, H2-delimited "file lists" with markdown links and notes. Modeled explicitly after `robots.txt` and `sitemap.xml` as a web convention. Now [adopted as a Chrome Lighthouse audit](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt) — the strongest signal that this is becoming part of the web stack. Implementing sites include FastHTML, Answer.AI projects, nbdev-based docs.

**Position:** LLM context windows can't hold full websites; sites need a standard way to expose a concise, curated, machine-readable summary at inference time. Markdown over XML because both humans and LLMs read markdown well.

**Memorable lines worth knowing:**
- The proposal frames the gap as: "Large language models increasingly rely on website information, but face a critical limitation: context windows are too small to handle most websites in their entirety."

**Relevance to capsules:** Different layer, same family of concerns. `llms.txt` is *site-level discoverability* (one file per domain, markdown, an LLM-friendly table of contents). Capsule is *artifact-level preservation* (one file per work product, HTML with embedded everything). They compose naturally — a site that hosts capsules should have an `/llms.txt` that indexes them; the htmlcapsule project now has [its own](https://htmlcapsule.org/llms.txt) following exactly this pattern. The right read is *not* "llms.txt vs. Capsule" but "llms.txt for discovery, Capsule for the actual durable artifacts the discovery points to." Worth flagging: `llms.txt` is the most "adjacent discipline" entry in this section — it's not strictly about HTML, but it's in the same family of LLM-readable content discipline as everything else here.

### Raunaq Bhutoria — html-docs.com

Live-collaboration-layer articulation. Built [html-docs.com](https://html-docs.com/) in May 2026 (timing inferred from [his tweet](https://x.com/raunaqbn) describing it as core to his agentic workflow at Meta). Tagline: *"Create beautiful docs and webpages with your Agents."* / *"Instant web publishing for you and your agents."* Provides three agent-integration paths: a Claude Code skill file (`~/.claude/skills/html-docs/`), an MCP server (`@html-docs/cli --mcp`), and an HTTP API with `x-api-key`. Six tools exposed to agents: `publish`, `publish_file`, `update`, `read`, `comment`, `list_comments`. Real-time multiplayer editing, live comments, version history. Endorsements on the homepage from Ryan Carson, Thariq Shihipar, and Andrej Karpathy.

**Position:** The agent ↔ human review loop as a workflow primitive. *"Review a doc → Comment → Agent reads comments and revises."* No format discipline imposed on the HTML — accepts any agent-emitted output; the discipline is on the workflow shape (publish → comment → revise → iterate), not the artifact shape.

**Memorable lines worth knowing:**
- "Create beautiful docs and webpages with your Agents."
- "Instant web publishing for you and your agents."
- The author's own framing of his Meta workflow: *"1. Create: Claude code generates review-ready HTML docs using html-docs.com/agents. 2. Review: I review the HTML doc with my army of agents and human collaborators. 3. Iterate: Send it back to claude-code to address. If good go build!"*

**Relevance to capsules:** Different lifecycle layer. html-docs.com is the *live editing / collaboration layer* (between agent generation and sealed handoff). Capsule is the *seal step* after the live work stops being actively edited. Same lifecycle distinction the project has already named in the working-vs-publishing-format synthesis (after the Karpathy and Steph Ango discussions). html-docs.com is a concrete example of the canvas-step Capsule explicitly doesn't compete with; Capsule is what a live doc would become when it graduates from active iteration to sealed preservation. SaaS (not open spec), closed-source — which is reasonable for the lifecycle slot it fills (real-time collaboration is hard to do over a sealed file by design).

### The position picture

Multiple positions across the lifecycle and across the layer stack:

| Voice | Layer | Frame |
|---|---|---|
| Thariq | Format — substrate now | "HTML is the new markdown" — the editing medium |
| Karpathy | Format — substrate over time | Four-step progression naming HTML as the current best step (markdown as the working layer beneath it) |
| Blake | Format — control surface | "Format is part of the runtime contract" — agent UI / live render |
| Steph Ango | Format — preservation principle | "File over app" — work should live in files you control |
| This project | Format — sealed handoff | The portable archive — manifest, sources, sealed convention, twelve rules |
| Raunaq / html-docs.com | Live editing | Agent ↔ human review loop — create with Claude Code, review with comments, iterate |
| Utkarsh / htmlbin | Hosting | Agent-first HTML hosting — short URL, /raw endpoint, format-agnostic |
| Jeremy Howard / llms.txt | Site discovery | Markdown index at /llms.txt — what's on this site, optimized for LLM consumption |

The positions are healthy differentiation, not competition. The picture spans the lifecycle of agent-generated HTML:

- **Live editing** (html-docs.com, plus the canvas/artifact UIs of LLM products themselves) — where work is iterated with the agent in the loop, before anything is sealed
- **Format / seal step** (Capsule, plus the substrate observers who frame why the format matters: Thariq, Karpathy, Blake, Steph) — what the artifact becomes when it graduates from live editing to sealed preservation
- **Hosting** (htmlbin, MinDev) — how artifacts get served once sealed
- **Discovery** (llms.txt) — how artifacts get found by LLMs and humans

The layers compose naturally: a discovery layer (llms.txt) points at hosted artifacts; a hosting layer (htmlbin, MinDev) serves format-disciplined artifacts (capsules); the format-layer (Capsule) makes the artifact durable on its own; an artifact that becomes a capsule may have been iterated for hours in a live-editing layer (html-docs.com) before being sealed.

The project's specific contribution is the format/seal-step slot: the contract that makes HTML files travel after the live work is done. The other voices in this picture cover the slots Capsule deliberately doesn't fill.

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
