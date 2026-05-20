# htmlcapsule

> **A capsule is a sealed, self-contained HTML memory object for work worth preserving.**

**Spec home: [htmlcapsule.org](https://htmlcapsule.org)** — landing page is itself a valid Capsule.

`htmlcapsule` is the open specification, reference implementation, and example set for **Capsule** — a profile of HTML for portable, structured, provenance-bearing snapshots of work that's worth preserving across tools, time, and people.

The hypothesis: the substrate (HTML) has already won as the universal display layer. What's missing is discipline — a contract, manifest, versioning, capabilities, and integrity guarantees — so that an LLM conversation, a database query, a hand-written report, a geospatial map, or a research summary can all preserve themselves into the same envelope and live in the same archive. The strongest claim the format makes is **multi-producer interop**: LLMs (Claude, ChatGPT, Gemini), deterministic compilers (Python/Node build scripts), and human authors all produce the same envelope shape.

Capsules are not a working format — you still edit in your tools of choice. They are a **publish / preserve / share** format. PDFs were the previous answer; they're closed and lossy. Capsules give the same role to HTML, which is alive, programmable, and re-readable years later by both audiences that will reopen the work: humans, and the LLMs they'll be asked to continue the work with. AI-native export is the load-bearing case the format is designed for; long-tail human readability falls out for free.

**A note on terminology.** Claude's "artifacts," ChatGPT's "Canvas," and similar features are *working canvases* — editable, iterable, live next to the chat. Capsules are what those become when sealed for preservation, sharing, and archival. Different roles, complementary tools: capsule is the seal step that comes after the canvas step.

**Current state:** Core spec at **v0.3.0**, full spec at **v0.3.2**, reference validator at 26 checks.

## Start here

- **For the format in one page:** [CAPSULE_CORE.md](CAPSULE_CORE.md) — twelve rules, pasteable into any LLM prompt.
- **For the full specification:** [spec/CAPSULE_SPEC.md](spec/CAPSULE_SPEC.md) — formal definition, validation rules, security model, response protocol, integrity-hash recipe.
- **For working examples:** [`examples/`](examples/) (JSON inputs for the compiler) and [`spec/examples/`](spec/examples/) (canonical example capsules).
- **For domain schemas:** [`spec/DOMAIN_CAPSULES.md`](spec/DOMAIN_CAPSULES.md) — `implementation_notes`, `design_system`, `exploration_map`.
- **For the research narrative:** [RESEARCH.md](RESEARCH.md) — what we're investigating, findings F1–F18, open questions, methodology.
- **For the glossary:** [`GLOSSARY.md`](GLOSSARY.md).
- **For positioning vs. related work:** [`PRECEDENTS.md`](PRECEDENTS.md).

## What a capsule is

A single self-contained `.html` file that packages:

- A bounded snapshot of data
- A machine-readable manifest with provenance metadata
- Embedded media (images, audio) as `data:` URIs — no external loads
- An interactive UI for the data (export buttons, navigation, optional in-capsule download)
- Honest version and integrity metadata
- All readable content **pre-rendered in the HTML at build time** (not produced by runtime JavaScript) — capsules are archives, not apps

Designed to be opened, reviewed, interacted with, and shared without requiring a server, network, or live access to the original source data.

## What a capsule isn't

- **Not a new file format.** A profile of HTML — `.html` extension, opens in any browser.
- **Not a SaaS, product, or working tool.** No accounts, no server, no live editing. You edit in your tool of choice (LLM chat, code editor, notes app, database GUI, IDE) and emit a capsule when you have something worth sealing.
- **Not a knowledge graph, second brain, or notes app.** This is the most common misread, so it's worth saying directly: capsules are *atomic outputs, not collected inputs.* The manifest, the UUIDs, and the `parents[]` lineage exist so a single capsule can stand alone with full provenance — *not* so you can traverse from one capsule to a graph of related ones. We deliberately have not built (and likely won't build) a network layer, an importer, a vault format, a graph viewer, or anything that turns a folder of capsules into a navigable wiki. If you're looking for "everything I know, queryable, in one place," the right tools are Roam, Obsidian, Notion, Anytype, TiddlyWiki — capsules are what you might *publish out of* one of those, not what they become.
- **Not a version-control system.** The `parents[]` field is provenance lineage (where this capsule came from), not a version chain to manage. Capsules don't replace git, don't replace your tool's edit history, and don't try to be the place where iterative editing happens. If you need versioning, edit in your working tool and emit a new capsule. A folder of `v1.html` / `v2.html` / `v3-final.html` is the failure mode the format is designed to *avoid*, not its expected workflow.
- **Not competing with Canvas/Artifacts/MCP.** Capsules are the *sealed* layer downstream of working canvases — complementary, not competing.

## Reference implementation

- [`compiler/compile.py`](compiler/compile.py) — produces capsules from JSON + template directories
- [`compiler/validate.py`](compiler/validate.py) — reference validator with 26 conformance checks
- [`templates/decision_board/`](templates/decision_board/) and [`templates/news_capsule/`](templates/news_capsule/) — two compiler templates demonstrating the compile path
- [`examples/`](examples/) — sanitized JSON inputs you can compile yourself

Quick check:

```bash
# Compile a sample capsule
python3 compiler/compile.py examples/ai_tool_selection.json templates/decision_board -o /tmp/test.html

# Validate it
python3 compiler/validate.py /tmp/test.html
```

## Multi-producer interop

The format is designed for three producer kinds, all emitting the same envelope shape:

1. **LLMs (Claude, ChatGPT, Gemini, Codex)** — paste [CAPSULE_CORE.md](CAPSULE_CORE.md) into a prompt and the LLM produces a conforming capsule. `generator.kind: "llm"`.
2. **Deterministic compilers** — Python or Node build scripts that query a source and render to inline SVG/HTML. `generator.kind: "compiler"`. The integrity-hash recipe in `spec/CAPSULE_SPEC.md` §9.1.1 is normative and has been independently re-derived from prose alone, producing bit-identical hashes.
3. **Hand-authored** — humans writing capsules directly in a text editor. `generator.kind: "human"` or `"hybrid"`.

All three pass the reference validator. All three carry the same manifest shape with honest `generator.kind` declarations.

## Versioning

Two versions move semi-independently:

- **Core spec** (`CAPSULE_CORE.md`): the short, pasteable-into-an-LLM-prompt version. Currently **v0.3.0**.
- **Full spec** (`spec/CAPSULE_SPEC.md`): the implementer-grade version. Currently **v0.3.2** (doc-only patches on top of v0.3.0).

Core spec versions are tagged in git: `core-v0.1.0` … `core-v0.3.0`. Retrieve any historical version via `git show core-vX.Y.Z:CAPSULE_CORE.md`.

## Trust signals

Capsules currently answer:

- *What is this?* (manifest fields: `type`, `title`, `description`, `uuid`, `capsule_version`)
- *Where does it claim to come from?* (manifest fields: `generator`, `source`, `synthesis`, `parents[]`)
- *Is the payload intact?* (manifest field: `integrity.content_hash` with a normative canonicalization recipe in §9.1.1)
- *What actions does it support?* (manifest field: `capabilities`, with Rule 7: declared = implemented)

What the format deliberately doesn't yet answer: *did the claimed author actually publish these exact bytes?* That's the trust-model gap. The design sketch for a future Sigstore-shaped transparency log is parked in [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) Appendix E.6, awaiting empirical pressure to build.

## Design discipline

This is a research/spec project. The principles:

- **Every spec addition requires empirical pressure.** No new schema fields, capabilities, or hash scopes without a real producer or consumer hitting a real problem. See spec Appendix E for parked v0.4+ candidates.
- **Trust signals stay honest.** Hashes, manifests, and capabilities are useful only if they stay honest and legible. The strongest trust signal isn't "this validates perfectly" — it's "you can see what produced it, what data is inside, what was omitted, and what actions are actually supported."
- **The corpus drives the spec.** Working capsules drive spec evolution; spec inflation runs the other direction and we resist it.
- **Schema-minimal.** Each field has to earn its keep against "what consumer does something load-bearing with this?"

## License

Apache License 2.0. See [LICENSE](LICENSE). The patent grant matters for a format spec — it protects independent implementers.

## Status

| Phase | Name | State |
|---|---|---|
| 1 | Format | Exists (Core v0.3.0, full spec v0.3.2) |
| 2 | Compiler | Half-built — reference compiler + validator + corpus of working capsules |
| 3 | Domain capsules | Partial — `domain.implementation_notes`, `domain.design_system`, and `domain.exploration_map` documented |
| 4 | Network layer | Not built; possibly never. Capsule registry, lineage graph, importers all deferred. Trust-log primitive sketched in Appendix E.6 but not built. |
