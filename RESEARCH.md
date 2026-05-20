# Capsule — Research Project

## What this is

A research project investigating whether HTML can be disciplined into a portable knowledge-artifact format with a machine-readable contract, content provenance, and a structured feedback loop — **without becoming a SaaS platform, a new file format, or a new browser standard.**

The project produces a spec, a reference implementation, and empirical evidence about whether the spec works in practice. The hypothesis is that the substrate (HTML) has won and what's missing is discipline, not a new format.

Started: 2026-05-15
Current Core spec: v0.3.0 · Full spec: v0.3.2
Repo: [bigfancygarden/htmlcapsule](https://github.com/bigfancygarden/htmlcapsule) · Site: [htmlcapsule.org](https://htmlcapsule.org)

## Project identity

**A capsule is a sealed, self-contained HTML memory object for work worth preserving.** The smallest portable structured unit any kind of knowledge work can resolve into — human-readable + machine-readable + provenance-bearing in one object. Not a working format — you still edit in your text editor, design in Figma, cook in your kitchen, think in your LLM chat. A **publish / preserve / share format** that any domain can emit.

Every domain today has good working tools and bad publish formats. PDFs lose interactivity. PNGs lose vector data. Recipe cards lose chef's notes. Exported chats lose structure. LLM conversations lose synthesis to the archive. Capsules are designed to be the universal publish format that preserves more than the alternatives, because:

- HTML is alive (interactive, scriptable, queryable) where PDF is dead.
- The manifest is machine-readable, so the artifact is self-describing.
- Provenance travels with the artifact, not as separate metadata that gets lost.
- The data block is whatever the domain needs; the envelope is consistent.
- Self-contained: opens in any browser, archives anywhere, shares to anyone, re-loadable into any LLM.

The same outer contract serves recipes, research notes, decision briefs, journal entries, design specs, log entries, learning artifacts, project handoffs — and most importantly, **the synthesis that comes out of LLM conversations that today disappears into chat archives**.

### Framing arc

The project's framing has sharpened through the research. Each version was less narrow than the last:

1. *"Compile from your private DB into shareable HTML"* — too narrow; assumed a structured source.
2. *"Boundary object between private system and external recipient"* — better; named the sharing pattern.
3. *"Save state for useful LLM conversations"* — closer; named the most common production path.
4. *"Atomic unit of preserved work, across any domain"* — broader, served the spec well during v0.1–v0.2.
5. *"Sealed, self-contained HTML memory object for work worth preserving"* — current; emerged from peer review in v0.3 (see F18). Adds the human/machine/provenance trio as a differentiating wedge.

The format itself supports each framing without changes — technical work over previous iterations turns out to have been correct under broader interpretations than we started with.

### What this is not

Capsules are not trying to replace working tools. Recipes will still be edited in cooking apps; designs in Figma; data analysis in Jupyter; thinking in LLM chats. The capsule is the **export from** these tools when the work is done, not the editing surface. This is exactly the role PDFs play today — they're just lifeless. Capsules give the same role to HTML, which is alive.

Capsules are also not trying to be a universal data interchange format like JSON-LD or RDF. The capsule's outer contract is universal; the inner content is domain-specific. This split is what gives the format both portability and expressivity.

## Origin

Thariq Shihipar's public observation that LLMs and agents are already producing single self-contained HTML files as their default artifact format. The substrate is winning. The question this project asks: **what does it take to make those files trustworthy — to give them a contract, provenance, versioning, and a structured way for recipients to respond?**

## Research questions

**Primary:** Can a one-page spec, given to an LLM as context, produce a conformant Capsule?

**Secondary:**
1. What discipline makes HTML useful as a boundary object between private knowledge systems and external recipients?
2. Where does the spec need to be strict vs. permissive?
3. What's the gap between compiler-produced and LLM-produced capsules — and is that gap useful (fidelity gradient) or broken?
4. Where does the format break down empirically — size, browser support, distribution friction?
5. Can the recipient side respond in a structured way that the author can programmatically ingest?
6. Will LLMs honestly declare themselves and their limitations when producing capsules?
7. Can a deterministic compiler produced by a third party round-trip through the reference validator at full fidelity? (Substantially answered: yes — see F18's note on independent compiler-kind producers.)

## Methodology

Iterative spec evolution against real artifacts:

```
Hypothesis → Draft spec → Build reference compiler → Compile real artifacts
   ↑                                                          ↓
   |                                                    External review
   |                                                          ↓
   |←─── Adjust spec ←─── What broke or what felt off ←──────┘
```

Three classes of "real artifact" are tested:

1. **Compiler-produced** — deterministic output from our reference Python compiler. Establishes the strict end of conformance.
2. **LLM-produced** — capsules generated by giving the Core spec to commercial LLMs (Claude, Gemini, ChatGPT) and asking them to produce a capsule on a real topic. Establishes the loose-but-honest end.
3. **Hand-written / hybrid** — the spec itself was originally dogfooded as a capsule. Tests whether the format can document itself.

External review at each iteration: code review on the implementation side, plus design review from independent LLM agents and (in v0.3) from third-party producers building compiler-kind capsules against the spec.

The spec can **only loosen** (backward-compatible additions) unless a major breaking issue is found. Tightening would invalidate prior artifacts and would also discourage LLMs from producing capsules at all.

## Findings

### F1: The Core spec works as an LLM prompt

**Experiment:** Pasted `CAPSULE_CORE.md` (one-page short spec, ~120 lines) into fresh Claude, Gemini, and ChatGPT sessions with one prompt: *"Using this spec, can you give me a summary of [public regulatory topic] as a Capsule?"*

**Round 1 result:** Three structurally compatible capsules. All passed validation with 18/21 pass + 3 warn + 0 fail (identical pattern). Each opened in a browser, rendered correctly, declared itself honestly as `generator.kind: "llm"`, included working exports, and presented a useful summary.

**Round 2 result (same day, more specific prompt):** Same pattern, plus prompt specificity successfully disambiguated topic interpretation.

**Conclusion:** Yes. The Core spec works as an LLM prompt. The format propagates through being readable and useful, not through enforcement.

### F2: LLMs deviate from the spec toward honesty

The most significant finding. Across both experiment rounds, LLMs consistently disagreed with the spec in five specific places. In every case, the LLMs were objectively more honest than the spec required:

| Spec field | What spec said | What LLMs reached for | Why LLMs were right |
|---|---|---|---|
| `source.origin` | Constant `"private_database"` | `"web_research"`, `"public_documents"`, `"official_public_sources"` | An LLM synthesizing from public content has no private database |
| `source.snapshot_type` | Database-flavored enum | `"synthesis"`, `"research_summary"`, `"bounded_public_legislative_summary"` | A summary isn't a "portable_excerpt" |
| `synthesis.kind` | `ai_extraction`/`ai_summarization`/etc. | `"llm"`, `"llm_summary"`, `"web_summary"` | The natural words are clearer |
| `type` | Strict enum | `"summary"`, `"briefing"` | None of the original types described what the capsule actually was |
| `feedback_payload` | Required `rating`/`comments`/`suggestions` only | Structured form with `position`/`concern`/`notes` | Real feedback isn't always a 1-5 rating |

In every case the spec was adjusted to accept the more honest values. **The pattern: usage shapes spec, not the other way around.** The spec is a description of what disciplined capsules look like, not a prescription that LLMs must obey.

### F3: The fidelity gradient is real and useful

The validator distinguishes three result tiers (pass / warn / fail). Compiler-produced capsules pass strict. LLM-produced capsules pass degraded — typically missing the `integrity` block (no canonical-JSON content hash) and triggering a capability-marker heuristic false-negative.

This is a designed feature, not a workaround. Recipients of an LLM-produced capsule can see exactly what's verified and what isn't. They can calibrate trust appropriately. A compiler-produced capsule comes with cryptographic integrity; an LLM-produced one comes with structural conformance.

**Conclusion:** The format works for multiple production paths with different trust profiles. The validator's tier system is the load-bearing piece that makes this possible.

### F4: Capability honesty is enforceable

The spec rule "a capsule must implement every capability it declares" was tested against LLM-produced capsules. In every case, declared capabilities matched implemented capabilities:

- One LLM declared `["about", "copy_as_json"]`, implemented exactly those two
- Another declared five capabilities, implemented all five
- A third declared `export_response`, built an actual feedback form with response export

No LLM over-declared. This is meaningful because it shows the LLMs treated the capabilities list as a contract, not as aspirational marketing. Implementation honesty is a property the format can preserve even when LLMs are the producers.

### F5: The format scales empirically through 13 MB

**Experiment:** Synthetic capsules at three sizes (1.35 MB / 6.6 MB / 13.15 MB) with embedded base64 blobs to simulate photo albums.

**Result:**
- Browser parse + JSON parse scales linearly at ~5 MB/sec.
- 13 MB capsule loads in 123ms total, settles to ~14 MB JS heap.
- Sub-millisecond interaction (tab switches, filter changes) on the 13 MB capsule.
- `JSON.stringify` of the full data block: 15ms (well under perceptible-jank threshold).

**Conclusion:** The 15 MB hard cap in the spec is correctly positioned. Browser performance isn't the bottleneck. **Distribution is** — Gmail's 25 MB attachment limit is the real ceiling, hit before browser strain.

### F6: An LLM built half the feedback loop unprompted

The most surprising finding. In round 2, one LLM received only the Core spec and a one-line prompt. It produced a capsule with:

- `export_response` capability declared
- A structured feedback form (position dropdown, concern dropdown, notes textarea)
- A `buildResponseExport()` function emitting valid `response.json` with `capsule_reference` linking back to the originating capsule

The recipient side of the feedback loop was implemented end-to-end by the LLM, without us telling it to. This was always part of the spec's design, but it wasn't part of the prompt. The LLM reached for the architecture.

**Reinforcement:** A later meta-capsule (produced under v0.1.2 with the standard one-line prompt) invented a `spec_compliance_self_check` field — an array grading the capsule against all eleven Core rules with `pass`/`n/a` and a per-rule note. The LLM cited rule 11 ("Runtime JS string-literal rule") by number. The numbered-rule format introduced in v0.1.2 is being consumed as machine-readable structure, not just human guidance.

### F7: Structured response payloads are mostly tally bait; notes carry the meaning

**Experiment:** A recipient opened an LLM-produced capsule, filled out its built-in feedback form (position dropdown + concern dropdown + notes textarea), and exported `response.json`.

**Result:** The structured fields (`position`, `most_important_issue`) contained little information that wasn't already in the `notes` field. The notes carried the actual meaning — the reasoning, the nuance, the position. The structured fields were essentially redundant.

**Generalization:** Structured response fields are *aggregation infrastructure*. They earn their weight when you have many respondents — you can tally positions, group by issue, scan notes within each group. For a single respondent, structured fields are decoration; notes are the response.

**Implication for the spec:** The `response_schema_version` envelope is correct. The eight response types are probably more than needed; the real axes are (per-record vs. whole-capsule) and (structured-for-aggregation vs. prose-only). The `feedback_payload` schema was correctly loosened in this iteration to allow arbitrary fields — its rigidity was preventing the most common real use case.

**Implication for the build:** The "import side as registry + database ingestion" framing was overstated. What's actually useful is much lighter — an archive + a pair viewer (open response + originating capsule side-by-side). The author still does the qualitative reading; the system doesn't try to merge or auto-process.

### F9: The single-document data shape is the natural LLM choice for conversation summaries

**Observation across ~20 personal-use conversation-summary capsules:** Almost every one used the **single-document shape** from §4.1 of the full spec — a top-level JSON object whose keys are themes (`summary`, `key_takeaways`, `decision_matrix`, `quick_recommendations`, etc.) — rather than the `records[]` shape.

The *specific* top-level keys vary per topic — that's expected and good. The shape definition isn't "must contain key X"; it's "top-level object with thematic named sections, each appropriate to the content." LLMs reach for this shape unprompted when summarizing a conversation; they reach for `records[]` when producing decision boards or list-shaped artifacts (the compiler templates).

**Implication:** Section 4.1's two shapes correctly carve the space. The example in the spec for the single-document shape is one possible filling; LLMs invent their own thematic keys per topic, which is the intended behavior.

### F10: The format absorbs primary artifacts (not just syntheses)

**Experiment:** Build capsules that *are* the work product, not summaries of one. Specifically: print-targeted 8.5×11 property-scale claim maps (both an illustrative synthetic one and one built from a public claims GeoJSON snapshot).

**Result:** Both validate cleanly (same shape as chat-summary capsules). No new failure modes appeared in the domain switch. The format absorbed:

- A new manifest type
- Inline SVG rendering (~300 lines of runtime drawing claim polygons, graticule, scale bar, north arrow)
- Print-targeted CSS (`@page size: letter portrait`)
- Honest provenance for non-real data (`generator.kind: "llm"`, `synthesis.kind: "illustrative_synthesis"` where appropriate)

**A third data shape emerged on its own:** the map capsules' data block isn't `records[]` and isn't single-document. It's a *feature collection*: a `property` metadata header + `bbox` + per-feature-class arrays. This is the natural GIS / GeoJSON-ish shape.

**Implication for the spec:** Section 4.1's two-shape carve (records / single-document) may want a third bucket called "feature collection" for geospatial / typed-feature-set domains. Documented as the seed of the `domain.exploration_map` schema in DOMAIN_CAPSULES.md.

### F11: The hybrid producer pattern is the most reliable production path for real-data capsules

**Observation:** Three production paths have produced capsules in this project:

| Path | Who writes HTML | Bug surface | Pattern |
|---|---|---|---|
| A. Pure LLM in chat | LLM session | High (rule 11 bug class, manifest drift) | One-off content |
| B. Pure Python compiler + templates | Reference compiler + per-type template dir | Zero (deterministic) | Records-shaped artifacts |
| C. **LLM-authored Python generator** | One Python script per artifact class, written by LLM, then frozen | Zero (deterministic shell + real data) | Recurring real-data artifacts |
| D. Pure human handcoding | n/a regularly | n/a | Rare |

Path C is the new one. The LLM writes a Python generator once (with all the HTML, CSS, JS frozen as Python strings + a `render_body()` function), then the generator runs from real data on demand.

**Why it works:** the runtime JS is the same code every time, reviewed once, frozen. The manifest fields are computed by Python (validator-clean). The data block contains real data. Path A's recurring failures — JS string-literal bugs (the rule 11 bug class), manifest drift, capability marker mismatches — all disappear because the LLM never re-generates the shell.

**Cost:** Adding a new artifact *class* (e.g. a recipe capsule, a journal entry capsule) requires writing a new generator. Per-instance cost is near zero.

**Implication:** For recurring content (photos, claim maps, perhaps recipes/journals/decisions), Path C is the right default. Path A stays useful for one-off chat-summary capsules where the per-instance content is bespoke. Path B (the reference compiler) is the seed and the validator's intellectual reference, but produces fewer capsules in practice than C.

### F12: Photo-shaped capsules — one artifact, one capsule (atomic-unit framing in its purest form)

**Build:** Example photograph capsules — one image, embedded as base64 in an `<img src="data:image/jpeg;base64,...">` tag. Plus an associated voice memo (m4a/AAC) embedded similarly. Plus metadata: caption, people[], location (lat/lon + accuracy), date (value + precision + is_approximate), tags, alt_text.

**Architectural pivot mid-build:** the first attempt packed multiple photos as `records[]` inside a single album-capsule. That conflicted with the project's atomic-unit thesis — a photograph is itself an atomic unit of preserved work, not a row in a parent file. Rewrote to one-capsule-per-image; the album becomes the *index* listing them, not a container holding them.

**Manifest signal:** new `type: "photograph"`, new `collection` field referencing the conceptual album by name (loose linkage, no parent file). The `included_records` is always 1.

**Data shape:** single-document with a top-level `photo` object containing the photograph's metadata + (originally) the data URIs. After F14's refactor, the data URIs live in the HTML `<img>` and `<audio>` tags directly, and the JSON data block is metadata-only.

### F13: First real CSP loosening — `media-src data:` for embedded audio

**Background:** all prior CSPs across the corpus had been identical:
```
default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';
img-src data:; connect-src 'none'; base-uri 'none'; form-action 'none';
```

That permits inline base64 images via `data:` URIs but not audio (audio falls back to `default-src 'none'` and is blocked).

**Change:** added `media-src data:` to the photo capsule's CSP. One directive. It does **not** open the door to external audio — `default-src 'none'` and `connect-src 'none'` still block remote media. The capsule remains sealed; only inline base64 audio is permitted.

**This was the first feature-driven CSP change in the format.** Documented in the spec as the canonical pattern: *if your capsule has embedded audio or video, add `media-src data:`. Don't broaden it further.*

**Format choice for audio:** AAC in M4A container (`.m4a`). Universal browser support, best compression-to-quality ratio. Python's `mimetypes.guess_type()` claims `.m4a` is `audio/mp4a-latm`, which browsers reject (LATM is a different stream format). Required an explicit `.m4a → audio/mp4` mapping in the build script.

### F14: Capsules are archives, not apps — the JS-render-everything failure mode

**The biggest learning of the early sessions.** Discovered when a photo capsule was AirDropped to iPhone and "didn't load properly."

**Root cause:** iOS Files preview (the QuickLook HTML viewer) doesn't execute inline JavaScript, or restricts it severely. The chat-LLM capsules — and, by pattern-copying, the first version of the photo capsule — were *100% JS-rendered*: the static HTML had empty containers (`<h2 id="title"></h2>`, `<figure id="photo-frame"></figure>`) and runtime JS filled them on load. With JS disabled or restricted, the capsule rendered as a near-blank page.

**Honest acknowledgment:** the pattern had been copied from the existing chat-LLM corpus without examining whether it fit. The thesis says "capsules are archives, portable across decades, self-contained." The implementation said "tiny single-page app that needs my runtime to be useful." Mismatch.

**Architectural fix:** progressive enhancement. Move all rendering to *build time* in Python. The static HTML, as written to disk, already contains the rendered artifact (image, audio, caption, metadata, description, tags, alt-text, manifest dump). JavaScript shrinks to ~3 KB of button click handlers (Print / Copy / Download). With JS fully disabled, the capsule still renders the full content; the three buttons just don't respond.

**Spec response — Core v0.1.3, rule 12:** promoted the principle to a numbered first-class rule, mirroring rule 11's structure (mechanical instruction + WRONG/RIGHT code example). Same hypothesis as rule 11 — LLMs follow syntax-level mechanical rules better than content-level prose guidance.

**Validator response:** `check_progressive_enhancement` heuristic — counts visible text inside `<main id="capsule-root">` after stripping `<script>` and `<style>` blocks and HTML tags. Under 200 chars, the capsule is flagged. WARN, not FAIL — existing JS-rendered fixtures remain validatable; the warning signals they don't follow the v0.1.3 convention.

**Implication for the project's identity:** the failure was the most informative thing in the corpus that session. The atomic-unit framing isn't just a slogan — it has implementation consequences. Archives must be readable by any HTML renderer, not just one that runs the producer's specific JS.

#### F14 follow-up: Rule 12 propagation result — first batches under v0.1.3

**Experiment:** Produce fresh batches of conversation-summary capsules through the same LLM pipeline that produced the v0.1.0–v0.1.2 capsules, this time with the v0.1.3 Core attached. Two batches of five capsules each (10 total), spanning unrelated topical domains.

**Result:** **10/10 PASS rule 12.** Every capsule pre-renders its full readable content (title, summary, takeaways, tables, glossary, source URLs, conversation transcripts, manifest dump in `<details>`) directly in `<main id="capsule-root">`. JS shrunk to button handlers in every one.

Visible-text counts inside `capsule-root` (validator threshold: 200 chars) ranged from ~6,000 to ~13,400 — every capsule cleared the threshold by 30× to 67×.

Rule-12 trajectory (mirrors rule 11's trajectory table):

| Batch | Spec version | Mitigation | Rule 12 PASS rate |
|---|---|---|---|
| 1–20 + early | v0.1.0 – v0.1.2 | none (pattern not yet recognized) | 0/23 |
| Batch A (5) | v0.1.3 | promoted to numbered rule 12 + WRONG/RIGHT code example | **5/5** |
| Batch B (5) | v0.1.3 | (same) | **5/5** |

**Epistemic update after second batch:** the result replicates. Two consecutive batches, 10/10 PASS, same producer, spanning 10 unrelated topical domains. Within-producer replication is solid; cross-producer confirmation is still the remaining open evidence gap before broad generalization.

**Hypothesis confirmed:** the "deeper instinct to build a tiny app" did *not* persist when rule 12 was promoted to a numbered rule with a code example. The same model that produced the JS-render-everything capsules in the earlier batches immediately switched to progressive enhancement when given the v0.1.3 Core.

### F15: Mobile responsiveness is a CSS-layer concern, not a format-layer one

**Trigger:** After F14's fix, an AirDropped photo capsule rendered on iPhone but looked like a thumbnail of an 8.5in letter page in a 375px viewport. Tiny. Required pinch-zoom to read.

**Fix:** mobile-first responsive CSS — same HTML body, three CSS modes:

1. **Default (mobile / narrow):** fluid layout, touch-friendly buttons, readable typography (no sub-12px sizes), stacked title block.
2. **`@media (min-width: 900px)`:** switches to the 8.5×11 letterhead view — fixed page dimensions in inches, two-column grids, desktop typography scale.
3. **`@media print`:** locks to letter portrait independent of viewport.

**Key insight:** the 8.5×11 page is a *print target*, not a *screen requirement*. The screen view can be fluid. Conflating the two was the design mistake.

**Implication for the spec:** This is implementation detail, not a Core rule. No spec change needed. Worth a note in the full spec's UI section that capsules should be screen-readable on any viewport size, with the 8.5×11 form factor reserved for print output.

### F16: Chat-LLM capsules embed source-conversation images when the conversation is image-grounded

**Pattern across two batches under v0.1.3:** When the source conversation included an image (a chart, screenshot, diagram, photo), the LLM embedded that image inline in the resulting capsule as a `data:image/...;base64,...` URI. Each used the same spontaneously-invented `embedded_media` data-block field structure (kind / description / filename / mime_type / embedded_as).

| Batch | Source image type | Capsule file size | CSP change required |
|---|---|---|---|
| Batch A | Screenshot of a public chart | ~254 KB | No (`img-src data:` already in baseline) |
| Batch B | Chart/document from a public source | ~2.2 MB | No |

**Epistemic state:** n=2 from same producer. Cross-producer confirmation still pending. But the within-producer pattern is consistent enough to treat as expected behavior, not anomaly.

**Implications for the spec:** no new rule warranted. The format already absorbs this:
- CSP `img-src data:` (in place since v0.1.0) permits the inline embedding
- Data block is free-form JSON, so the `embedded_media` field is admissible
- File-size cap (15 MB) is well above 2.2 MB

The spec's documentation now notes that when conversations include images, embedding the source image as a `data:` URI is an established pattern. The `embedded_media` data-block field (or a similar shape) is recognized as a recommended convention.

### F17: Prompt-fragment-only Core revisions are a valid spec-evolution mode

**Background:** all Core revisions to date (v0.1.1, v0.1.2, v0.1.3) introduced or promoted at least one numbered rule. v0.1.4 was the first that didn't. It added only prompt-fragment guidance:

1. "Be thorough about real content" — a paragraph pushing back against LLM brevity-truncation, with explicit permission to include all takeaways / sources / caveats / open questions, and an explicit floor on inventing content the conversation didn't produce.
2. "Capture sources and links" — a paragraph recommending a structured `sources` array in the data block, with a shape example.

Neither is a rule. Neither has validator enforcement. Both are producer-behavior hints in the prompt fragment that producers actually see.

**Why these are worth a Core version bump:** the prompt fragment IS the Core to producers. If we silently amend it, the version line lies — producers under "v0.1.3" would actually see different content than the v0.1.3 fragment captured by git tag. The two self-documenting fields (`source.spec_received`, `source.prompt_received`) would lose meaning if the content of a given version drifted.

So: every change that producers will see gets a version bump. Rule changes get major attention. Guidance changes get minor attention.

**Hypothesis:** prompt-fragment guidance will work similarly to rule promotions — explicit, mechanical, included alongside the numbered rules in the producer's context, with examples. The "numbered rule + WRONG/RIGHT code example" pattern addresses mechanical failures. Prompt-fragment guidance addresses *underexplored options* — behaviors that aren't broken but aren't being chosen. Different mechanism, different bar. Worth tracking both separately.

### F8: The atomic-unit framing explains everything we've built

**Reflection rather than experiment.** Across multiple framings the project has tried — "compile from private DB", "boundary object", "save state for LLM chats" — the format itself didn't need to change. Each framing was the same format viewed through a narrower lens. The framing that explains all the previous ones is: **a capsule is the atomic unit of preserved work.**

**Evidence supporting the broader framing:**

| Domain | Working tool | Existing publish format | What capsule preserves |
|---|---|---|---|
| Decision-making | Spreadsheets, meetings | PDF / email thread | Per-option records, evidence, decisions |
| News annotation | Browser + memory | Forwarded link | Article + extracted claims + verdicts |
| Research synthesis | LLM chat | Copy-paste into doc | Synthesis + sources + provenance |
| Recipes | Cooking apps / notebook | Recipe card | Ingredients + steps + scaling + notes |
| Journal | Notion / paper journal | Locked in app | Entry + mood + context |
| Map / geospatial | QGIS / GIS tools | PNG / map service | Features + layers + popups |
| Logs | System logs | Text dump | Events + context + severity |

In every row, the existing publish format loses something the working format had. PDFs lose interactivity. PNGs lose vector data. Recipe cards lose the chef's notes. Capsules preserve more because they're alive (HTML + structured data + provenance + UI).

**The atomic property matters because:**

- Atomic units are searchable individually
- Atomic units compose into larger structures via `parents[]` (the capsule forked from another, the capsule that responds to another)
- Atomic units have their own provenance, not inherited from a container
- Atomic units survive movement between systems

**Consequence for the project's identity:** capsules are to *preserved work output* what JSON is to *data interchange*. A universal portable envelope that any domain can fill with appropriate content. F18 sharpens the framing further into "memory object" but the atomic-unit point remains the structural argument.

### F18: Peer review (2026-05-19) — sharpest framing, landscape position, and trust-model gaps

A peer-review pass on the v0.3.2 state of the project produced three things worth recording in the research log: a sharper one-sentence thesis, a 2026 landscape position, and an explicit naming of the format's open trust-model questions.

**Sharpest framing.** The strongest one-sentence definition that emerged from review:

> "A capsule is a sealed, self-contained HTML memory object for work worth preserving."

"Memory object" is doing real work in this sentence. It captures the **human-readable + machine-readable + provenance-bearing trio in one noun phrase** — the property no neighboring format provides simultaneously. PDF is human-only, JSON export is machine-only, MHTML lacks a manifest, ZIP lacks rendering, .docx lacks a programmatic data block, Notion exports are platform-dependent. The previous framing ("atomic unit of preserved work") remains internally accurate but lacks a differentiating wedge. The new framing has been adopted in README, `CAPSULE_CORE.md`, and `index.html`.

The second insight: **multi-producer interop is the strongest empirical claim the format makes.** LLMs (Claude, ChatGPT, Gemini), deterministic compilers (third-party build scripts), and human authors all produce the same envelope shape. That's what makes capsules different from yet another save format. Personal/team memory is the most accessible adoption vector; multi-producer interop is the differentiator. Don't narrow positioning to wave-one adoption.

The first independent compiler-kind producer (a third-party Python build script) shipped capsules that round-trip through the reference validator at 26/26 in v0.3. Crucially, the producer re-derived the integrity-hash recipe from spec prose alone (§9.1.1) without reading the validator source, and produced bit-identical hashes on first attempt. This is the spec earning its keep as a normative document.

**2026 landscape position.** Neighbors mapped:

| Neighbor | Layer | Relationship |
|---|---|---|
| HTML artifacts (Thariq / Blake Crosley) | Live agent output / control surface | Aligned but upstream — capsules are the seal step downstream |
| Durable interactive artifacts (AgentPatterns) | Workspace objects | Aligned but platform-bound; capsules are portable across tools |
| Intermediate artifacts in agentic systems (arXiv) | Multi-agent internal state | Same instinct, systems-internal scope |
| ARA agent-native research artifacts | Research deliverables | Heavier research-world cousin |
| RO-Crate | Sealed research packages | Direct competing *format* — capsules differ in single-file constraint |
| WACZ/WARC | Web archives | Different layer (archived web, not authored work) |
| C2PA / Content Credentials | Signed media provenance | Complementary *trust* layer, not format competition |
| Agent manifests (agent.json, JSON Agents) | Agents themselves | Adjacent 2026 instinct (machine-readable manifests around AI) |

Strategic conclusion: **HTML is unlikely to be usurped soon as the rendering substrate. The likely future is HTML remaining the human-inspectable surface while JSON / RO-Crate / C2PA-style metadata wrap around or live inside it.** Web Bundles were the only direct technical challenger; their IETF draft is stale and Chrome removed the navigation experiment in 2023. Capsules are betting on the stable layer.

**Open trust-model gap.** The current spec answers *"what is this? where does it claim to come from?"*. It does not answer *"did the claimed author actually publish these exact bytes?"*. The UUID asserts identity but doesn't enforce it — anyone can ship a modified capsule with the same UUID.

A full trust story would require four pieces:

1. **Two-hash split.** `content_hash` (canonical manifest+data, survives DOM round-trip) + `file_hash` (raw bytes, doesn't). Lets a recipient verify two different questions independently.
2. **Author signing**, identity-anchored via a Sigstore/Fulcio-style OIDC issuance. Without identity infrastructure, "signed by author" is just another lie waiting to happen.
3. **Transparency log** (Sigstore/Rekor-shaped). Append-only public record of signed releases, detecting same-UUID-different-content games and backdating.
4. **Out-of-band verification.** Capsule never calls home (Rule 2 preserved). The QR code already embedded in the capsule (Core convention) resolves on the recipient's phone/reader to a verification URL that queries the transparency log. Friction lives on the verifier's side; the capsule stays mute.

Three trust tiers would emerge: **Self-describing** (current baseline), **Signed**, **Logged**.

**Decision: parked, not built.** No reported real-world tampering incident exists in the corpus or among independent producers. Building infrastructure ahead of empirical pressure would be exactly the "spec gravity before daily-use pressure" failure mode the peer review explicitly warned against. Captured in `spec/CAPSULE_SPEC.md` Appendix E.6 as a v0.5+ candidate.

**Two strategic risks named in the review, now internalized as ongoing discipline:**

- **Spec gravity.** Every spec addition should be triggered by a real producer/consumer hitting a real problem. v0.4 candidates (E.1–E.8 in the parked-direction appendix) should be pressure-tested against this rule before any v0.4 work. The corpus is empirical evidence; spec additions that don't respond to empirical gaps are anticipatory engineering.
- **Trust theatre.** Hashes / manifests / capabilities are useful only if they stay honest and legible. The strongest trust signal isn't "this validates perfectly" — it's "you can see what produced it, what data is inside, what was omitted, and what actions are actually supported." The blind re-derivation of the integrity-hash recipe by an independent producer (producing a bit-identical hash from §9.1.1 prose alone, no peeking at validator source) is the bar for trust signals earning their keep through actual second-party verification rather than self-validation.

Both risks are now ongoing discipline rather than one-time fixes.

### F19: Design-tool integration experiment — Claude Design with CAPSULE_CORE.md attached

**Experiment.** Asked a design tool (Claude Design, claude.ai/design) to produce a landing-page design and export the result as a Capsule per Core v0.3.0, with `CAPSULE_CORE.md` attached as conversation context. The session produced *three* relevant artifacts, with quite different structural shapes — all worth recording. Two were valid; one was not.

> **Note on finding evolution.** This finding was substantially revised after the model self-corrected its export choice. An initial draft treated the bundler-wrapped 52 KB file as "the model's capsule output" and framed the discrepancy as "two verifiers checking different criteria." The model's reply clarified — and our reference validator confirmed — that the model first wrote a 40 KB file that **does** validate cleanly (24/25 pass, 0 fail), then a separate "Save as standalone HTML" step ran a general-purpose bundler over that valid file and produced the 52 KB shell. So the finding is not "spec-aware intent, non-conforming output" — it's "spec-aware conforming output, destroyed by a downstream pipeline step that should not have run." The revised version below is the accurate record.

**Output A — three design-variation files from the canvas (dc-card wrapped).**

These were the JSX/HTML mockups exported earlier in the same session, before the user asked for a capsule. Each file:

- Was 4.8–5.7 MB on disk, ~75% of which was per-element inline `style="accent-color:auto; align-content:normal; ..."` CSS resets that Claude Design's canvas applies (≈10 KB per element × ~385 elements). These are normalization for the design canvas, not the design itself.
- Wrapped visible content in `<div class="dc-card" data-om-id="...">` — Claude Design's canvas-card container.
- Had two `<style>` blocks: one in the head (woff2 fonts as `data:` URIs) and one inside the body (the actual design CSS, with a redundant `@import url('https://fonts.googleapis.com/...')` that violated Rule 2 even though the same fonts were already embedded as `data:` URIs above).
- Had no `id="capsule-*"` blocks of any kind. Pure design exports — not capsules, design mockups.

A structural transformation script (strip resets, strip `data-om-*`, strip the redundant `@import`, unwrap dc-card, merge `<style>` blocks into `<style id="capsule-style">`, wrap content in `<main id="capsule-root">`, inject `<script id="capsule-manifest">` + `<script id="capsule-data">` + `<script id="capsule-runtime">`, add CSP meta) converted each to a valid capsule at 25/25, ~1.5 MB final (essentially the embedded woff2 fonts plus thin content). The visual design was preserved bit-for-bit; the bloat removed was Claude Design's canvas safety net, not the design itself.

**Output B1 — the model's actual capsule output (40 KB, pre-bundler).**

After the user asked explicitly for "the landing page as a Capsule per the attached Core spec," the model wrote a 40 KB single HTML file. Validated against the reference validator:

**24/25 pass, 1 warn, 0 fail.**

| Validator check | Result | Notes |
|---|---|---|
| HTML5 doctype | PASS | — |
| `<html>` + `<body>` tags | PASS | — |
| All required sections present | PASS | All five `id="capsule-*"` blocks at the byte level |
| No external resource references | PASS | Zero network fetches |
| Manifest section parseable | PASS | Honest provenance (see below) |
| All required manifest fields | PASS | — |
| Manifest field types | PASS | — |
| Capsule version present | PASS | `capsule_version: "8.0.0"` |
| Recommended manifest fields | PASS | — |
| `generator.kind` recognized | PASS | `"llm"` |
| `source` block | PASS | `origin: "authored"`, snapshot fields populated |
| `privacy` block | PASS | `external_dependencies: false` |
| `spec_version` recognized | PASS | `0.3.0` |
| `spec_version` ↔ `source.spec_received` agree | PASS | — |
| `capabilities` include `about` + one export | PASS | — |
| Data section parseable | PASS | — |
| Content hash verifies | PASS | No integrity block (optional for LLM-kind) — passes by absence |
| Field format patterns | PASS | — |
| All capabilities have impl markers (heuristic) | **WARN** | `copy_as_prompt` — implementation exists but the function name doesn't match the validator's marker regex (false negative on a soft check). |
| Runtime JS strings well-formed | PASS | — |
| Content pre-rendered in HTML | PASS | 5388 chars of visible text in `<main id="capsule-root">` |
| File size under 15 MB | PASS | 41,724 bytes |

This is a third independent producer kind reaching conformance — joining the reference compiler (`generator.kind: "compiler"`) and the hand-authored landing (`generator.kind: "human"` / `"hybrid"`). **All three producer kinds in the spec's interop claim are now empirically demonstrated.**

What the model got right structurally:

- **Five reserved IDs at the byte level** — `capsule-manifest`, `capsule-data`, `capsule-style`, `capsule-root`, `capsule-runtime`, all present in the parsed-as-written file with no JavaScript needing to run.
- **`<main id="capsule-root">` populated with 5,388 chars of pre-rendered visible text** — directly satisfies Rule 12 without ambiguity.
- **Honest provenance**: `generator.kind: "llm"`, `name: "claude.ai"`, `version: "claude"`. Declined to guess its own model ID and noted the user could pin tighter (e.g., `"claude-opus-4-7"`).
- **Correctly handled the Rule 2 / Google Fonts conflict** before writing: picked system-font fallback (`ui-monospace, SF Mono, Cascadia Code, Menlo, Consolas, DejaVu Sans Mono`) rather than `@import` or fetched fonts. The right call.
- **Skipped QR code per spec guidance** — the qrcode library wasn't available in its environment, so it followed the spec's *"don't fake a QR by hand"* directive rather than producing a wrong one.
- **Capabilities declared with implementation intent** — `about`, `copy_as_json`, `copy_as_markdown`, `copy_as_prompt`, `download_json`, `download_capsule`, `print_to_pdf`. Added a self-check that warns to the console for any declared-but-not-implemented capability (Rule 7 self-audit baked into the file).
- **Sensible defaults** — `source.origin: "authored"` rather than `"private_database"`, accessibility nods, print stylesheet.

The single validator warn was a heuristic false-negative on `copy_as_prompt` — the function existed but didn't match the marker regex pattern. Zero hard failures. **The pre-bundler file is a deployable, conforming capsule.**

**Output B2 — the same file after "Save as standalone HTML" ran (52 KB, post-bundler).**

The user then clicked "Save as standalone HTML." Claude Design's bundler — a general-purpose pipeline built to inline external assets for designs that *aren't* self-contained — ran over the already-self-contained B1 and wrapped it in a single-page-app hydration shell:

```
<head>
  <style>… thumbnail + loading styles only …</style>
  <noscript>This page requires JavaScript to display.</noscript>
</head>
<body>
  <div id="__bundler_thumbnail">… social-preview SVG …</div>
  <div id="__bundler_loading">Unpacking…</div>
  <script>
    // 6 KB bundler that:
    //   reads script[type="__bundler/manifest"]
    //   reads script[type="__bundler/template"]
    //   base64-decodes + gzip-decompresses assets
    //   fetch()-rewrites blob URLs
    //   replaces the thumbnail with the actual content via DOM injection
  </script>
  <script type="__bundler/manifest">… base64-encoded assets …</script>
  <script type="__bundler/template">… HTML template as JSON …</script>
</body>
```

Validator score: **4/10 pass, 1 warn, 5 fail** — required sections missing (the bundler uses `script[type="__bundler/*"]` instead of `id="capsule-*"`), `fetch(s.src)` in the asset-assembly step violates Rule 2, manifest unfindable, content not pre-rendered (zero visible text in `<main id="capsule-root">` because no such element exists at parse time).

Architecturally, this is **exactly the failure mode Rule 12 was written to catch** — content packed into JS, rehydrated on load, body empty at parse time. Open the file with JavaScript disabled (iOS Files preview, email previewer, archive viewer, old browser) and you see the loading spinner forever, then a `<noscript>` fallback. Same shape as F14's JS-render-everything failure pattern, but inverted into a deliberate hydration architecture.

The mechanism is innocent — Claude Design's bundler exists for a legitimate purpose (inlining externally-referenced assets into a transportable single file). The bug is that **it should be skipped, not run, when the input is already capsule-shaped.** Running a "make this self-contained" pipeline over a file that is already self-contained is destructive, not idempotent.

**The actual integration boundary: a process-ordering issue, not a verifier-criteria mismatch.**

An earlier draft framed B1 ↔ B2 as a discrepancy between two verifiers checking different things. That was wrong. The clarified mechanism (confirmed by the model and re-checked against our validator):

- The model wrote B1 and ran its own verification on the as-written bytes. B1 validates against both the model's verifier *and* our reference validator. Both agree it's a conforming capsule.
- The user then triggered a separate "Save as standalone HTML" step that ran the bundler over B1, producing B2. The verification gate had already cleared on B1; it did not re-run on B2.
- B2 fails both verifiers, because it is structurally not a capsule — it's a bundler shell that *contains* a capsule template inside an `__bundler/template` block.

So the lesson generalizes as: **"verify-before-mutate, but always re-verify after any pipeline step that touches the artifact."** A multi-step export pipeline that mutates the artifact between verifications can ship a file that the verifier never actually checked. In the Claude Design case, the verifier ran at the right point in the conversation flow but not at the right point in the file-mutation flow.

(This is closer in spirit to the build-pipeline / artifact-signing problem in software supply chains than to a spec-interpretation disagreement. The signature/verification gate has to be the *last* thing that touches the artifact before it leaves the producer, or there is a window where the artifact and the gate disagree.)

**What the model self-corrected.**

After being shown the validator score on B2 alongside the diagnosis, the model's reply was sharp: *"You're right, and the diagnosis is accurate… The file is already standalone. Running the bundler will wrap it in an SPA hydration shell that violates Rules 2, 3, and 12. Skipping the bundler — the file you have is the deliverable."* It correctly identified the actual deployable as B1, named the bundler as the source of the destruction, and rephrased the original "two verifiers" framing as a process bug ("I shipped two files in sequence and only validated the first").

This is itself a relevant data point for multi-producer interop: a spec-aware model, when given the empirical evidence, can self-diagnose the integration boundary and correctly route around it.

**Implications for multi-producer interop:**

- **All three producer kinds are now empirically demonstrated.** Compiler (`compile.py`), LLM (B1, claude.ai/design with `CAPSULE_CORE.md`), and hand-authored / hybrid (the canonical landing page) all produce files passing the reference validator. The interop claim in the README is now backed by an independent third producer.
- **The model can produce conforming capsules from the Core spec prompt alone.** No special tooling, no per-capsule template, no human cleanup step — `CAPSULE_CORE.md` plus a description of the desired content was sufficient.
- **The downstream pipeline is the integration risk, not the model.** A spec-aware producer can be undone by a generic post-processing step that doesn't know about the spec. The mitigation is process discipline (re-verify after every mutation), not a rule change.
- **Self-containment is necessary but not sufficient for capsule-compliance.** B2 is self-contained at runtime; it is still not a capsule. The five-required-blocks contract + reserved IDs + pre-rendered-in-HTML + no-network-at-render are what the format means by "capsule," beyond mere bundling.

**Implications for the spec:**

- **No rule change motivated.** Rule 12 caught exactly what it was designed to catch. The spec's normative content is unchanged by this finding.
- **A formal compatibility note** lives in Appendix E.10 as a v0.4 candidate. It documents the bundler-incompatibility pattern, names the integration point (skip the bundler on already-capsule-shaped input; or, equivalently, the bundler's input is the integration point, not its output), and articulates the verify-before-mutate / re-verify-after-mutate process discipline.
- **The conversion bridge** (the structural-transformation script from the Output A path) is reusable for future canvas-shaped exports from any tool with a similar `dc-card`-style wrapper.

**What we did with the outputs:**

- **Output A** (dc-card raw HTML from the canvas): converted three design-variation files to valid capsules at 25/25 each, ~1.5 MB after stripping the canvas-reset bloat. Deployable.
- **Output B1** (the model's pre-bundler 40 KB file): originally validated 24/25, 0 fail, with one heuristic warn. After a validator improvement motivated by this finding (see postscript below), it validates **25/25, 0 fail.** Documented here as the empirical LLM-producer exemplar. Not shipped as the project's canonical landing (we already have one), but recorded as evidence of the LLM-producer path working end-to-end.
- **Output B2** (post-bundler 52 KB shell): not shipped; failed validation; serves as the empirical evidence for E.10 and for the "skip the bundler on capsule-shaped input" guidance.

The clean record: **the LLM-producer path works.** A spec-aware model with the Core spec attached can produce a conforming capsule on the first try. The integration risk is downstream pipeline steps that mutate the artifact after verification has cleared — the mitigation is process, not a rule change.

**Postscript — validator improvement motivated by this finding.**

The original 1/25 warn was a heuristic false-negative on `copy_as_prompt`. The model used a cleaner Rule 7 verification pattern than our reference examples:

- **Manifest:** `"capabilities": ["copy_as_prompt", …]`
- **DOM binding:** `<button data-capsule-action="copy_as_prompt">copy prompt fragment</button>`
- **JS handler:** `var actions = { copy_as_prompt: function () { … } };`

Same literal string in three places — the most direct manifest-to-implementation link possible, auditable by eyeball without needing a regex translation table from `copy_as_prompt` → `copyPrompt` → `btn-copy-prompt` (our reference examples' three-name convention). The validator's marker regex (`copy[-_]?prompt`) didn't anticipate this convention and false-negatived the cleaner one.

When asked, the model offered to rename the handler to match our regex. We declined: the right fix was the validator, not the file. We added two uniform patterns to the marker-check that apply to every known capability automatically:

```python
escaped_cap = re.escape(cap)
clean_convention_patterns = [
    rf'data-capsule-action\s*=\s*["\']{escaped_cap}["\']',
    rf'\b{escaped_cap}\s*:\s*function\b',
]
```

Both patterns are specific to implementation context — the data-attribute only appears in HTML markup, and the `: function` form requires the `function` keyword, which cannot appear in JSON. No false-positive risk on declared-but-unimplemented capabilities (Rule 7's actual guarantee is preserved bit-for-bit).

Result: the Claude Design file now validates 25/25 clean. All existing examples (the canonical landing, `briefing_example.html`, `implementation_notes_example.html`, the three converted theme files) still validate at their previous scores. The patch is strictly additive.

The lesson generalizes: **when an independent producer finds a cleaner convention than the reference examples, the right response is to recognize the cleaner convention in the tooling, not to demand the producer rename.** This is the difference between a spec that ossifies around its reference implementation and one that improves through external pressure. The patch isn't adding spec surface area — it's improving the validator's ability to recognize compliance. The spec discipline principle ("the corpus drives the spec; spec inflation runs the other direction") cuts toward the patch, not against it.

## Open questions

In rough priority:

### Q1: Does the atomic-unit framing hold across genuinely different domains? **(Substantially answered)**

The format has working artifacts in at least five domains:

| Domain | Data shape | Production path | Status |
|---|---|---|---|
| Decision board | `records[]` | Compiler | working (reference template) |
| News annotation | `records[]` | Compiler | working (reference template) |
| Conversation synthesis | single-document | Pure LLM in chat | working (~30+ capsules across multiple batches) |
| Property-scale map | feature collection | Hybrid (build script) | working (illustrative + real-data instances) |
| Photograph + audio note | single-document with `photo` object | Hybrid (build script) | working |
| Implementation notes | single-document | LLM or hybrid | documented in DOMAIN_CAPSULES.md (Thariq-pattern) |
| Design system | single-document | LLM or hybrid | documented in DOMAIN_CAPSULES.md (Thariq-pattern) |
| Exploration map | feature collection w/ raster option | Compiler | documented in DOMAIN_CAPSULES.md (third-party producer) |

Eight documented domains, three production paths, three data shapes, all sharing the same five-block envelope. The framing holds. Remaining open question is whether more exotic domains strain the format (journal entries, recipes, scanned letters, voice-only notes, video clips, log files).

### Q2: Can the author-side archive be light and still useful?

The previous "biggest gap" framing put the import-side build as a heavyweight registry + ingestion system. F7 dissolved most of that — the lightweight version (SQLite archive + pair viewer) handles the actual common case. Still unbuilt; still a candidate next concrete build.

### Q3: How does the format behave under cross-browser file:// constraints?

All browser testing to date has been via local HTTP. Safari, Firefox, and Chrome have different file:// security policies. Specifically: clipboard API availability, localStorage/IndexedDB behavior, inline font and SVG handling under strict CSPs. The format **should** work identically on file:// and http:// per spec — empirically this is undertested.

### Q4: Does the spec need a content-hash protocol that LLMs can actually compute?

The canonical-JSON content hash is unreproducible by LLMs (which don't reliably canonicalize JSON). LLM-produced capsules omit it. The spec correctly degrades to a warning, but this means LLM-produced capsules are fundamentally less verifiable than compiler-produced ones. Is there a hash protocol that an LLM could plausibly compute correctly? Open.

### Q5: Will the fidelity gradient hold under adversarial use?

What if an LLM produces a capsule that claims `generator.kind: "compiler"` (i.e., lies about its production path)? The validator can't catch this — it's a self-declared field. A capsule that claims to be compiler-produced but has malformed integrity hash would fail integrity verification, but a capsule that just omits the integrity block and claims to be compiler-produced would pass with a warning. The trust model assumes good faith. Real-world deployment may not have it. The E.6 transparency-log direction would partly address this.

### Q6: How big does the spec need to be?

The full `CAPSULE_SPEC.md` is ~1500 lines including v0.4 candidates (Appendix E). The Core is ~120 lines. The Core demonstrably works as an LLM prompt. Does the full spec earn its weight, or could it be trimmed without loss? Open question for a future audit.

## Recurring LLM authoring failures

Across multiple personal-capsule batches (20+ capsules across four spec versions), several classes of bug have recurred.

### Primary recurring failure: string-literal escape errors in markdown export functions

The pattern: LLMs reach for newline characters when generating string-building JavaScript and get the escape level wrong. Either over-escape (`"\\n"` becomes literal backslash-n in output) or under-escape (raw line terminator inside a non-template string literal, which is a SyntaxError that kills the entire runtime silently).

The validator originally couldn't catch this because the runtime is treated as opaque text by the manifest/data parser path. A capsule with a broken runtime could pass 18/21 + 3 warn + 0 fail while having zero working buttons.

**Trajectory across spec versions:**

| Batch | Spec version | Mitigation | Bug recurrence |
|---|---|---|---|
| 1–5 | v0.1.0 | none | 1/5 |
| 6–10 | v0.1.0 | none | 2/5 |
| 11–15 | v0.1.1 | prose tip in prompt fragment | 1/5 |
| 16–20 | v0.1.2 | promoted to numbered rule 11 + WRONG/RIGHT code example | **0/5** |

**Finding:** Promoting the rule from prose guidance to a numbered first-class rule with a concrete code example dropped recurrence from 1/5 to 0/5 in the next batch. All five v0.1.2 capsules used backtick template literals for the markdown export. One batch isn't proof, but the trajectory is monotone improvement and consistent with the hypothesis that LLMs follow mechanical syntax-level rules better than content-level "be careful" prose.

**Belt-and-suspenders mitigation in v0.1.2:** the validator also grew a regex check for the bug pattern (`join("`/`join('` followed by a raw line terminator) inside the runtime block.

### Secondary recurring failure: `spec_version` cargo-cult from example block

A separate, lower-stakes authoring slip appeared in some LLM batches. The LLM correctly recorded `source.spec_received: "v0.1.2 · 2026-05-16"` (the Core version line it actually received) but set `manifest.spec_version: "0.1.0"` — cargo-culted from the example manifest block in the Core, which still showed the old version.

**Two mitigations landed together:**
- Core's example manifest bumped to match the current spec_version so producers see the right value to copy.
- Rule 4's `spec_received` example reminds producers that the two fields should match.
- Validator added a cross-check: when both `spec_version` and `source.spec_received` are present, they must agree on the version.

### Tertiary recurring failure: JS-render-everything pattern (the constrained-renderer problem)

The most architecturally significant failure. Discovered in the photo capsule when AirDropped to iPhone — see F14 for full writeup. Spec response: Core v0.1.3 rule 12 — render content in the HTML at build time, not at runtime. Same numbered-rule + WRONG/RIGHT-example pattern that dropped the rule 11 bug class to 0/5. Empirically validated on two consecutive batches under v0.1.3 (10/10 PASS).

### Quaternary recurring failure (mild): over-broad CSP directives

**Pattern across two v0.1.3 batches:** ~30% of capsules add defensive CSP directives (`media-src`, `font-src`, `blob:`) that the capsule doesn't actually use.

**Severity:** mild. Over-broad CSPs don't *break* anything — they just permit more than the capsule actually exercises. From a security standpoint they're still very restrictive (everything is `'none'` or `data:` only — no host allowed). From a self-documentation standpoint they over-promise.

**Spec response (still deferred):** the pattern is consistent but consistently low-severity. No Core/spec change motivated yet. If a capsule ever declared `'self'` or a host (which would be a real loosening), that would warrant a rule. Pure-`data:` over-declaration doesn't.

## Variance across runs (and what we can and can't control)

After producing 30+ LLM capsules across formal experiment rounds plus personal-use captures, the variance pattern is now clear:

**Between producers (different models):** Quality differs systematically. Thinking / extended-reasoning variants (Claude extended thinking, ChatGPT "Thinking" modes, Gemini deep-think) produce noticeably more careful capsules than standard variants — better personal-use defaults, light+dark themes, working markdown exports, CSP headers, richer data structures. This is repeatable and large enough to be worth noting prominently. The Core spec now includes a note encouraging thinking-mode use when available.

**Within producer (same model, different runs):** Real but smaller variance. Same model with same prompt produces different layouts, different CSS aesthetics, sometimes includes/omits the optional `synthesis` block. This is intrinsic LLM sampling variance (temperature), generally not user-controllable on web UIs. **It is fine.** The structural invariants (manifest, data, runtime, validation) hold across all the variance. Each capsule is still a valid capsule. We cannot expect bit-identical reproduction across runs and shouldn't aim for it — the variance is informative about how robust the format is to natural production noise.

**Content-aware defaulting (correct behavior, not variance):** Thinking variants correctly read social meaning of the conversation and set `visibility` accordingly. A conversation about sensitive content → `visibility: "private"`, `contains_private_data: true`. A conversation about generic intellectual content → `visibility: "shared"`. This isn't variance — it's the LLM doing context-aware honest defaulting on its own. Worth preserving as expected behavior.

## Self-documenting capsules

Two optional manifest fields turn capsules into a self-documenting research record:

- **`source.spec_received`** — the Core version string the producer was given (e.g., `"v0.3.0 · 2026-05-19"`)
- **`source.prompt_received`** — the verbatim prompt

For LLM-produced capsules, these are encouraged. They let future readers correlate output with the spec version and prompt that produced it, without external bookkeeping.

The Core itself is version-stamped (first line of `CAPSULE_CORE.md`). Material changes bump the version and date. Git tags (`core-v0.1.0` through `core-v0.3.0`) preserve historical versions retrievable via `git show core-vX.Y.Z:CAPSULE_CORE.md`.

## Notable methodology choices

These weren't obvious at the start but proved important:

- **Reference implementation is Python stdlib only.** No `pip install` required. Accessibility for adopters matters more than performance.

- **Validator is heuristic by design.** Capability detection uses regex patterns. False negatives are possible. This was a deliberate choice once we recognized that **the long-term real validator is going to be an LLM**, not our Python script. The Python validator is a seed and a teaching artifact, not the endpoint.

- **Spec evolution is empirical. Usage drives; thesis judges.** This is the most load-bearing methodological choice in the project.

  *Usage drives:* we don't design rules from a chair. Every spec move so far has been triggered by an empirical observation in the LLM corpus or the production pipeline — never by "this would be good design." The spec is the *trailing* indicator of what producers actually do, never the leading edge.

  *Thesis judges:* when we observe something, the question is *does this serve "memory object for work worth preserving" or undermine it?* The answer determines the direction of the spec move:

  | Observation type | Move | Examples |
  |---|---|---|
  | Honest deviation (LLM reaches for a more accurate value) | **Loosen** — the spec was too narrow | `source.origin: "web_research"`, `synthesis.kind: "llm"`, loosened enums |
  | Recurring failure (mechanical bug, broken rendering, lost meaning) | **Tighten** — add a numbered rule that names the failure | rule 11 (JS newline), rule 12 (JS-render-everything) |
  | Emergent convention (LLMs invent a useful pattern unprompted) | **Document** — recognize it as a recommended convention without making it required | `embedded_media` field, `sources` array (now in §4.1.2 of the full spec) |
  | Underexplored option (a useful behavior LLMs aren't choosing on their own) | **Add prompt-fragment guidance** — no new rule, just explicit permission/encouragement | v0.1.4 thoroughness + sources guidance |

  Loosening, tightening, documenting, and guiding aren't opposites. They're four flavors of the same reactive mechanism, applied to different kinds of observation. The thesis is the constant; the spec is always catching up.

  *Why this matters:* most spec design is *generative* — decide what the right way is, force practice to conform. That model produces specs that ossify and lose contact with reality. The reactive model produces specs that stay current with how producers actually behave. Same model as Markdown/CommonMark, HTML/WHATWG, Python idiom-layer/PEPs.

  *Limits this principle has, that we should be honest about:*

  1. **Bootstrap problem.** v0.1.0 had to be *something* before any usage existed. The initial draft was unavoidably generative. Every revision since has been reactive.
  2. **Requires a clear thesis.** Without "memory object for work worth preserving" as the arbiter, we couldn't tell honest deviation from broken artifact. The thesis is doing real work; the principle would collapse without it.
  3. **Requires willingness to unwind.** If a rule we added turns out to be wrong, we have to remove it. v0.3 demonstrated this — `capsule_id` (slug) and `related[]` were deprecated when their consumer-side use case didn't materialize.
  4. **Slow under pressure.** When you want to build a new path NOW, the reactive principle says "watch what you build, then formalize." That's slower than designing the framework up front. We have to be willing to accept the slower path.

  This is the project's first-rank methodological commitment.

- **Spec-evolution mechanism: "numbered rule + WRONG/RIGHT code example."** When an LLM-authoring failure recurs and has a mechanical (syntax-level / architectural) fix, the working pattern for propagating the fix is:

  1. Document the failure with empirical evidence (multi-batch trajectory data).
  2. Promote the principle to a *numbered* Core rule (not a prose tip in the prompt fragment).
  3. Include a concrete code example showing WRONG vs RIGHT.
  4. Bump the Core version and re-test on the next batch.

  This has now worked twice empirically:

  | Rule | Failure class | Pre-numbered mitigation | Post-numbered result |
  |---|---|---|---|
  | 11 (v0.1.2) | JS string-literal newlines | prose tip in prompt fragment → 1/5 still failing | numbered rule + WRONG/RIGHT → **0/5** failing in next batch |
  | 12 (v0.1.3) | JS-render-everything | no prior mitigation (pattern not recognized) | numbered rule + WRONG/RIGHT → **10/10 passing** across two batches |

  Two cases isn't a strong statistical sample, but the mechanism is consistent with the broader observation that LLMs reliably follow mechanical, syntactically-explicit rules better than they follow content-level advice. Worth treating as the default spec-evolution pattern going forward.

  **What this is NOT:** a license to add more rules. Each numbered rule consumes prompt budget and cognitive load on the producer side. The bar for adding a rule remains "empirically recurring failure with no other available mitigation."

## Project artifacts

| Artifact | Role |
|---|---|
| [`CAPSULE_CORE.md`](CAPSULE_CORE.md) | One-page short spec, designed for LLM prompts (currently v0.3.0) |
| [`spec/CAPSULE_SPEC.md`](spec/CAPSULE_SPEC.md) | Full normative spec (currently v0.3.2) |
| [`spec/DOMAIN_CAPSULES.md`](spec/DOMAIN_CAPSULES.md) | Per-domain schemas (implementation_notes, design_system, exploration_map) |
| [`spec/SYSTEM_ARCHITECTURE.md`](spec/SYSTEM_ARCHITECTURE.md) | The four-layer architecture (private system / compiler / artifact / format profile) |
| [`spec/manifest.schema.json`](spec/manifest.schema.json) | JSON Schema for the manifest block |
| [`spec/response.schema.json`](spec/response.schema.json) | JSON Schema for response envelopes |
| [`spec/examples/`](spec/examples/) | Canonical example capsules (briefing, implementation_notes) |
| [`compiler/compile.py`](compiler/compile.py) | Reference compiler, stdlib-only |
| [`compiler/validate.py`](compiler/validate.py) | Reference validator (26 checks at v0.3.2) |
| [`templates/decision_board/`](templates/decision_board/) | First template: per-option decisions with verdict export |
| [`templates/news_capsule/`](templates/news_capsule/) | Second template: annotated article with claims/entities/sources |
| [`examples/`](examples/) | Sanitized JSON inputs for the compiler templates |
| [`GLOSSARY.md`](GLOSSARY.md) | Vocabulary, four-layer table, phase status |
| [`PRECEDENTS.md`](PRECEDENTS.md) | Positioning against RO-Crate, TiddlyWiki, MPEG-21, C2PA, etc. |
| [`index.html`](index.html) | Project landing page — itself a valid Capsule |
| Git tags `core-v0.1.0` … `core-v0.3.0` | Historical Core versions retrievable via `git show core-vX.Y.Z:CAPSULE_CORE.md` |

## Reproducibility

To rerun the LLM experiment yourself:

1. Open a fresh chat with the LLM of your choice (Claude, Gemini, ChatGPT, or any model capable of reading attached files).
2. Attach [`CAPSULE_CORE.md`](CAPSULE_CORE.md).
3. Ask: *"Using this spec, give me a summary of [topic] as a Capsule."*
4. Save the resulting HTML.
5. Run `python3 compiler/validate.py <file>.html` to check conformance.

Expected result: roughly 22/25 pass with 3 warns (missing integrity block, capability-marker false negative). Different pattern? That's a finding — either the spec drifted, the LLM behaviour changed, or you've found a new edge case.

To re-derive the integrity hash from spec prose alone (as one independent producer did):

1. Read `spec/CAPSULE_SPEC.md` §9.1.1 ("Content Hash Recipe — normative").
2. Implement the canonical-JSON serialization + placeholder substitution rules in your language of choice.
3. Compute the hash for the worked example given in the spec.
4. Compare against the expected hash also given in the spec.

If your implementation produces the expected hash bit-identical, the spec is doing its job as a normative document. If it doesn't, the spec has a gap.

## Status

As of v0.3.2 (2026-05-20):

- **Core spec v0.3.0** — twelve rules. Five rounds of loosening / additions based on empirical findings:
  - v0.1.1: rule 11 first draft (string-literal mitigation in prompt fragment)
  - v0.1.2: rule 11 promoted to numbered rule with WRONG/RIGHT example; data shape clarifications; spec_version self-doc fields
  - v0.1.3: rule 12 added (render content in HTML, not at runtime) — empirically validated on two consecutive batches
  - v0.1.4: prompt-fragment additions (no new rules) — thoroughness guidance + structured `sources` array recommendation
  - v0.1.5–v0.1.8: minor patches (QR code convention, snapshot_id prefix callout)
  - v0.2.0: schema rename — `capsule_id`/`capsule_version` canonical; `artifact_id`/`artifact_version` deprecated but accepted
  - v0.3.0: added `parents[]` for hard provenance; deprecated `capsule_id` slug and `related[]` field; spec-gravity discipline formalized

- **Full spec v0.3.2** — doc-only patches on top of v0.3.0:
  - v0.3.1: normative content-hash recipe with verifiable test vector (§9.1.1); "Inspecting a served capsule" preamble
  - v0.3.2: `download_capsule` standard capability with implementation pattern (§5.1.1)

- **Reference validator** at 26 checks. New checks since v0.1.0: runtime JS string-literal regex, spec_version ↔ source.spec_received cross-agreement, progressive enhancement heuristic, `parents[]` format checks, deprecation notes for `capsule_id` and `related[]`.

- **Templates**: 2 compiler templates (decision_board, news_capsule).

- **Independent producers shipped:** at least one third-party deterministic compiler producing `generator.kind: "compiler"` capsules that validate clean at 26/26 against the reference validator. The producer re-derived the integrity-hash recipe from spec prose alone and produced bit-identical hashes on first attempt.

- **Domains covered:** decision boards, news annotations, conversation summaries, property-scale geospatial maps, photographs with audio attachments, image-grounded conversations, implementation notes, design systems, exploration maps. Multiple data shapes, multiple production paths.

- **CSP:** one feature-driven loosening landed (`media-src data:` for embedded audio). All other CSP directives unchanged since the format's launch.

- **Empirical size scaling tested** through 13 MB (synthetic).

- **Parked v0.4+ directions** (Appendix E of full spec): remove deprecated fields, compiler-kind UUIDv5 carve-out, reconsider `ai_usage_guidance` in domain capsules, hash-algorithm flexibility, Rule 12 vs. legacy compiler templates, author signing + transparency log, password-protected encrypted capsules, validator refinement for non-resource-loading `<link>` tags. None built; each waits for empirical pressure.

**Biggest unbuilt piece:** author-side import tooling (registry + `import.py`). The producer side has matured significantly and the consumer side hasn't moved. The lightweight version (SQLite archive + pair viewer per F7) remains a candidate next concrete build.

**Biggest untested area:** cross-browser file:// behavior across Safari, Firefox, and Chrome. The format **should** work identically on file:// and http:// per spec — empirically this remains undertested.

## How to read this project

This is a research project that produces a working spec and reference implementation as primary artifacts. The spec is the hypothesis. The fixtures (compiled and LLM-produced capsules) are the evidence. The findings document (this file) is the running narrative of what we've learned. Every commit message is part of the research log — the "why" of each change is preserved in git history.

The project does not have a single "result" or a release date. It's a working investigation. The most likely failure mode is **spec inflation** (the long spec grows beyond what anyone reads) and the second most likely is **import-side abandonment** (we keep polishing the producer side while the consumer side stays unbuilt). Both are explicitly tracked as risks.

The project is not trying to invent something. It's trying to articulate the discipline that's missing from a practice already underway.
