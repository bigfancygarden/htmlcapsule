# htmlcapsule

> **A capsule is a versioned, self-contained HTML file for work, data, or information worth preserving — a memory object that's human-readable, machine-readable, and provenance-bearing in one.**

**Spec home: [htmlcapsule.org](https://htmlcapsule.org)** — landing page is itself a valid Capsule.

`htmlcapsule` is a **research project** that produces an open specification, reference implementation, example corpus, and research log for **Capsule** — a profile of HTML for versioned, self-contained, provenance-bearing snapshots of work, data, or information worth preserving.

The hypothesis: the substrate (HTML) has already won as the universal display layer for AI-generated work; what's missing is *discipline* — a contract, manifest, integrity guarantees, capability honesty, and pre-rendered content — so that artifacts from LLMs, deterministic compilers, and human authors all carry the same envelope shape. The strongest claim the format makes is **multi-producer interop**: LLMs (Claude, ChatGPT, Gemini, Codex), deterministic compilers (Python/Node build scripts), and human authors all produce the same envelope shape. Empirically validated as of v0.3.4 with Mintel as the first independent compiler-kind producer (see [F20](RESEARCH.md)).

The project's discipline is **empirical-pressure-driven**: spec changes emerge from observed production failures across multiple producer kinds; rules earn their slot when a real failure forces the addition, and the corpus drives the spec — not the other way around. The current state of that research is recorded in [RESEARCH.md](RESEARCH.md) as numbered findings F1–F31, with parked v0.4+ candidates in [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) Appendix E. Two layer-level convergences have been observed independently within the project's first two weeks: F21 (hosting pattern, MinDev + htmlbin) and F22 (live-editing pattern, html-docs + workplane). F24 then formalizes the host-vs-registry distinction (the missing commitment layer); F25 captures the ChatGPT producer-population's reliable reads of Core supplementary guidance.

Capsules are not a working format — you still edit in your tools of choice. They are a **publish / preserve / share** format. PDFs were the previous answer; they're closed and lossy. Capsules give the same role to HTML, which is alive, programmable, and re-readable years later by both audiences that will reopen the work: humans, and the LLMs they'll be asked to continue the work with. AI-native export is the load-bearing case the format is designed for; long-tail human readability falls out for free.

**A note on terminology.** Claude's "artifacts," ChatGPT's "Canvas," and similar features are *working canvases* — editable, iterable, live next to the chat. Capsules are what those become when sealed for preservation, sharing, and archival. Different roles, complementary tools: capsule is the seal step that comes after the canvas step.

**Current state (project v0.4.0):** Core spec at **v0.3.0**, full Capsule spec at **v0.3.8**, Bundle spec at **v0.1.0** (the new sibling format — see [`spec/BUNDLE_SPEC.md`](spec/BUNDLE_SPEC.md) and [F31 in RESEARCH.md](RESEARCH.md)). Reference validator at 26 checks (Capsule only; Bundle validator pending). Research log at **F31**. Companion docs: [`spec/HOSTING.md`](spec/HOSTING.md) (descriptive host-contract pattern observed across MinDev + htmlbin), [`voices/`](voices/) (archived primary-source voices in the conversation Capsule is part of), [`CITATION.cff`](CITATION.cff) (formal citation), [`/llms.txt`](llms.txt) (site-discoverability index), [`CHANGELOG.md`](CHANGELOG.md) (project trajectory).

## Start here

- **For the format in one page:** [CAPSULE_CORE.md](CAPSULE_CORE.md) — twelve rules, pasteable into any LLM prompt.
- **For the full specification:** [spec/CAPSULE_SPEC.md](spec/CAPSULE_SPEC.md) — formal definition, validation rules, security model, response protocol, integrity-hash recipe.
- **For working examples:** [`examples/`](examples/) (JSON inputs for the compiler) and [`spec/examples/`](spec/examples/) (canonical example capsules).
- **For domain schemas:** [`spec/DOMAIN_CAPSULES.md`](spec/DOMAIN_CAPSULES.md) — `implementation_notes`, `design_system`, `exploration_map`.
- **For the research narrative:** [RESEARCH.md](RESEARCH.md) — what we're investigating, findings F1–F31, open questions, methodology.
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
- [`compiler/validate.py`](compiler/validate.py) — reference validator with 26 conformance checks. Two modes:
  - **Local file mode**: `python3 compiler/validate.py path/to/capsule.html`
  - **URL mode** (added in v0.3.4): `python3 compiler/validate.py <https://host/path/raw>` — fetches the body via the host's `/raw` endpoint, cross-checks any `x-capsule-content-hash` and `x-capsule-uuid` response headers against the manifest, then runs the standard checks. Per the host-contract pattern documented in [`spec/HOSTING.md`](spec/HOSTING.md).
- [`templates/decision_board/`](templates/decision_board/) and [`templates/news_capsule/`](templates/news_capsule/) — two compiler templates demonstrating the compile path
- [`examples/`](examples/) — sanitized JSON inputs you can compile yourself

Quick check:

```bash
# Compile a sample capsule
python3 compiler/compile.py examples/ai_tool_selection.json templates/decision_board -o /tmp/test.html

# Validate a local file
python3 compiler/validate.py /tmp/test.html

# Or validate a hosted capsule by URL (fetches /raw, cross-checks any
# x-capsule-* host-attestation headers against the manifest before
# running the standard 26 checks)
python3 compiler/validate.py https://mindev.ca/api/c/9357a933-7ce1-4061-9488-2ca61d81bded/raw
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
- **Full spec** (`spec/CAPSULE_SPEC.md`): the implementer-grade version. Currently **v0.3.8** (doc-and-validator patches on top of v0.3.0; see [CHANGELOG.md](CHANGELOG.md) for the per-patch trajectory).

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

## How to cite

See [`CITATION.cff`](CITATION.cff). GitHub auto-detects this file and renders a "Cite this repository" button on the repo page; citation tools (Zotero, citation managers) consume it directly. The citation form will gain a Zenodo DOI at the next milestone release for resolvable permanence beyond GitHub.

## Status

| Phase | Name | State |
|---|---|---|
| 1 | Format | Exists (Core v0.3.0, full spec v0.3.8) |
| 2 | Compiler | Half-built — reference compiler + validator (local file mode + URL mode) + growing corpus across producer kinds. First independent compiler-kind producer (Mintel) shipped + validated (F20) |
| 3 | Domain capsules | Partial — `domain.implementation_notes`, `domain.design_system`, `domain.exploration_map`, `domain.briefing` documented. `domain.music_stems` in the Idea queue |
| 4 | Network layer | Not built; possibly never. Capsule registry, lineage graph, importers all deferred. Trust-log primitive sketched in Appendix E.6 but not built. |

## Maintainer

Luke Schuss · Vancouver · [lukeschuss.com](https://lukeschuss.com) · <info@lukeschuss.com>

Feedback, independent implementations, and findings from real producer/consumer pressure are the things this project most wants. Open an issue, email, or drop the artifact you produced into a thread on the repo.
