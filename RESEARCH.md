# Capsule — Research Project

## What this is

A research project investigating whether HTML can be disciplined into a portable knowledge-artifact format with a machine-readable contract, content provenance, and a structured feedback loop — **without becoming a SaaS platform, a new file format, or a new browser standard.**

The project produces a spec, a reference implementation, and empirical evidence about whether the spec works in practice. The hypothesis is that the substrate (HTML) has won and what's missing is discipline, not a new format.

Started: 2026-05-15
Current Core spec: v0.3.0 · Full spec: v0.4.0-draft
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

**Conclusion (at time of finding):** The 15 MB hard cap in the spec is correctly positioned. Browser performance isn't the bottleneck. **Distribution is** — Gmail's 25 MB attachment limit is the real ceiling, hit before browser strain.

**Updated by F20 (2026-05-21):** A real production Mintel capsule arrived at 13.7 MB and several real production channels (MinDev hosting, AirDrop, Slack, cloud-storage links) have no equivalent of the email-attachment constraint. Spec v0.3.3 raised the hard cap to 20 MB and added a 15 MB soft warning specifically for email-attachment compatibility — the 15 MB number was always proxying for email-friendliness, not browser strain. The conclusion above still holds; the cap moved up because the distribution-channel landscape has more than one shape.

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

### F20: First publicly-fetchable Mintel production capsule validates spec at scale

**Date:** 2026-05-21

Mintel now publicly serves a real production exploration_map capsule via MinDev. First time the project has end-to-end validated a production third-party capsule (not LLM-corpus, not sanitized example) against the reference validator.

**The capsule:**
- URL: `https://mindev.ca/api/c/9357a933-7ce1-4061-9488-2ca61d81bded/raw`
- Type: `domain.exploration_map`
- Title: "Copper Dome — BC · Project location"
- Size: **13.73 MB** (99.43% data block — GeoJSON for 47 claim polygons)
- Generator: `mintel/build_exploration_map_capsule v0.1.0`, `kind: "compiler"`
- Integrity: `sha256:60282cbd…`, `hash_scope: "data+manifest"` — content hash verifies clean
- Validator result: **26/26 PASS, 0 warn, 0 fail**

**Five empirical findings:**

**1. The 15 MB cap was always a proxy for email-friendliness, not browser strain.** F5 set the cap at 15 MB from Gmail's 25 MB attachment limit. Mintel's distribution channel is MinDev hosting (no equivalent of the email cap), and the empirical desktop parse ceiling is well above 15 MB. v0.3.3 splits the constraints: hard cap raised to 20 MB, with a 15 MB soft warning explicitly for email-attachment compatibility. The number that was always proxying for one thing now names two things.

**2. Rule 12 vs. visualization geometry — image-fallback resolves E.5.** The Copper Dome capsule pre-renders chrome (title, legend, north arrow, info panel, attribution, QR code; 1,373 chars visible) but draws polygons into an empty `<svg id="map-svg">` container at runtime. The validator's surrounding-text heuristic passes; strictly the data-bearing content depends on JS — iOS Files preview would show an empty white box where the map should be.

The principled resolution (now documented in spec §2.3 "Carve-out for visualization geometry"): visualization geometry rendered into a pre-declared named container is allowed IF a static image rendering is embedded as the JS-disabled fallback in the same container. Preserves Rule 12's intent (content IS in the HTML — as a raster) while accommodating geometry that can't reasonably be pre-rendered as static markup. The image rendering is typically free — it's the same raster the pipeline already produces for non-capsule deliverables (PDF/JPEG exports). One extra `<img>` element and a one-line visibility toggle in runtime.

E.5 was parked specifically waiting for this case. v0.3.3 ships the resolution.

**3. MinDev's hosting model is now empirically demonstrated.** The MinDev response includes:

```
x-capsule-content-hash: sha256:60282cbdad54708f...
x-capsule-uuid: 9357a933-7ce1-4061-9488-2ca61d81bded
```

The host attests independently via response headers without modifying the file body — "wrap, don't modify" per Appendix B distribution guidance and E.7 (MinDev pattern). First publicly-fetchable example of this hosting model. Caveat: header attestation is honest about what the host computed; it's not a signature from the original author (that's still E.6 signing territory).

**4. The compiler-kind integrity path works end-to-end on real production data.** Full integrity block present (`content_hash` + `hash_scope: "data+manifest"`), `generator.kind: "compiler"`, and the validator confirms the hash verifies on a 13.7 MB file. Mintel re-derived the integrity-hash recipe from spec prose alone — bit-identical hashes (noted earlier in F18; this finding adds concrete production-capsule evidence at scale).

**5. Custom namespace use is exemplary.** The `x-mintel` block (`project_id`, `project_version_id`, `project_version_number`) uses the `x-` extension prefix correctly per E.3's recommendation. Consumers that don't know about Mintel ignore the block; domain-specific consumers can dereference back to the source.

**Spec moves landed in v0.3.3:**

- §2.3 Rendering Model — image-fallback carve-out for visualization geometry, with worked example
- §6.3 Size Limits — hard cap 15 MB → 20 MB; 15-20 MB soft-warn tier added for email-friendliness
- §14 Validation — list item 11 updated to reflect the new cap and the soft warn
- §16.2 Out of scope — boundary list mention updated
- `domain.exploration_map` — image-fallback as required convention; file-size note updated
- E.5 — resolved (moved from parked-items to shipped)
- `compiler/validate.py` — `MAX_FILE_SIZE` 15 → 20 MB; file-size check now emits a soft-warn note when the file is between 15 MB and 20 MB

**Open questions remaining:**

- The header-attestation pattern (`x-capsule-content-hash`, `x-capsule-uuid`) should be formalized as a "host contract" if/when there are multiple MinDev-shaped hosts. Currently lives as MinDev convention; would benefit from doc-only canonicalization in a future patch.
- Mobile browser parsing above 15 MB is undertested. F5's linear-scaling result was desktop-only. Worth an empirical test on iOS Safari and Android Chrome at the new 15-20 MB range before the cap is taken as fully load-tested.
- The "compact variant" idea (a view-only capsule without the full GeoJSON, just the rendered image + minimal manifest) is interesting for view-only sharing — could shrink a 13.7 MB capsule to ~50 KB. Lacks current empirical pressure but worth flagging.
- Legacy compiler templates (`templates/decision_board`, `templates/news_capsule`) still don't pre-render data-bearing content. Now that the image-fallback carve-out exists, they could either adopt the pattern or be documented as historical. Not urgent.

### F21: Independent convergence on the host-contract pattern (MinDev + htmlbin)

**Date:** 2026-05-21

Two independent hosting layers have converged on the same shape for serving Capsule-style HTML artifacts, without coordination between them:

1. **MinDev** (private, Mintel-tied; serves the F20 Copper Dome capsule and other Mintel-produced exploration_map capsules).
2. **htmlbin.dev** (public, agent-first; launched ~May 17-18, 2026 by Utkarsh Sengar, Cloudflare D1 + KV stack). Independent project; not aware of htmlcapsule at launch.

**Shared shape observed:**

| Aspect | MinDev | htmlbin.dev |
|---|---|---|
| Short URL identity | UUID — `mindev.ca/api/c/{uuid}` | Slug — `htmlbin.dev/p/{slug}` |
| `/raw` byte-identical endpoint | `/api/c/{uuid}/raw` | `/p/{slug}/raw` |
| Host chrome | Recedes to a left rail | Small header + footer attribution |
| Authorship attribution | Response headers (`x-capsule-content-hash`, `x-capsule-uuid`) | Footer text ("content authored by the agent that uploaded it") |
| Content mutation | None — serves uploaded bytes byte-identically | None — serves uploaded bytes byte-identically |
| Validates on upload | Yes (against Capsule spec) | No (accepts any self-contained HTML) |
| Visibility | Private | Public, OAuth-gated first publish |

**Why this matters:**

The convergence is empirical evidence that the host-contract pattern referenced in Appendix E.7 ("hosting-platform auth gates per the MinDev pattern... the platform controls *delivery*; the capsule itself doesn't gate its internal contents") is a real shape that independent producers reach on their own. The format/host split — *the format defines the artifact, the host serves it* — appears stable across implementations.

This is the empirical pressure the project was waiting for to formalize a host contract beyond the single-implementor MinDev reference. The "what a host should do (and not do)" doc that was previously parked can now be drafted as a description of an observed convention across two independent implementations, not a proposal made in a vacuum.

**Practical implication — the format is hosting-agnostic, demonstrably:**

A valid Capsule can be hosted on MinDev, on htmlbin, or self-hosted, with no format change. Hosts adopt the format optionally; the format imposes nothing on the host beyond "serve the bytes you received." The "format-not-platform" stance is now concrete and verifiable, not aspirational.

**Spec moves to consider:**

- A new doc — `spec/HOSTING.md` or `spec/HOST_CONTRACT.md` — describing the observed pattern: short URL identity + `/raw` byte-identical endpoint + minimal host chrome + (optional) integrity attestation in response headers + no content mutation. Not normative; documentary. Cites MinDev and htmlbin as the two convergent implementations.
- Possibly update Appendix B (Distribution Guidance) to add htmlbin alongside MinDev as a concrete hosting example.
- E.7 (MinDev pattern reference) can be annotated as having independent empirical support; no resolution change needed.

**Open questions:**

- Will htmlbin add integrity-attestation headers (`x-capsule-content-hash` style) over time as Capsule-format artifacts get hosted there? If so, the convergence deepens — every host independently arrives at the full pattern, including the attestation layer.
- Will the host contract crystallize as a formal spec, or stay descriptive? Probably the latter for now — formalizing would require multiple host implementations to agree on protocol particulars (header names, slug format, etc.), which would need outreach. Descriptive documentation captures the observation without prescribing.
- Should the project provide a "verify a hosted Capsule" mode in `validate.py`? Currently the validator works on local files; could optionally fetch a URL, recompute the integrity hash, and check it against MinDev's `x-capsule-content-hash` header attestation. Small addition, real utility for recipients who want to verify they got what the host claims they got.
- Worth tracking whether other hosts emerge in this space over the next quarter. Two implementations is convergence; three or more is a pattern that probably deserves formal documentation.

**Cross-references:**
- [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) — the MinDev side of the convergence, with the Copper Dome capsule.
- [PRECEDENTS.md "Current voices in HTML-for-AI"](PRECEDENTS.md) — Utkarsh / htmlbin added as a hosting-layer voice; the three-position picture extended to acknowledge format-layer vs. hosting-layer slots.
- Appendix E.7 in [spec/CAPSULE_SPEC.md](spec/CAPSULE_SPEC.md) — the "MinDev pattern" reference that hinted at this convention; F21 is the empirical validation.

### F22: Independent convergence on the live-editing layer pattern (html-docs + workplane)

**Date:** 2026-05-21

Two independent live-editing tools shipped in approximately the same window (mid-May 2026) with substantially the same workflow shape, without coordinating. This is the parallel finding to F21 (host-pattern convergence): *two* layer-level patterns have now been observed converging independently within this project's first two weeks of running. The pattern of convergence is itself becoming a recurring methodological observation.

**The two tools:**

| | html-docs.com | workplane.co |
|---|---|---|
| Creator | Raunaq Bhutoria (Meta engineer; [@raunaqbn](https://x.com/raunaqbn)) | Matan (GitHub: [matanrak](https://github.com/matanrak); based in Israel) |
| Repo | Not public | `work-plane/workplane-skills` (MIT); `/workplane` repo linked but 404s |
| Org created | (n/a — closed SaaS) | `work-plane` GitHub org created 2026-03-29 |
| Most recent push | (closed) | 2026-05-20 (`workplane-skills`) |
| Tagline | "Create beautiful docs and webpages with your Agents." | "Turn AI outputs into live pages." / "The working plane between AI and humans." (README) |
| Open source | No (SaaS, closed) | Partial — agent skill is open MIT; main service may be closed |
| Agent integration | Claude Code skill + MCP server + HTTP API; 6 named tools (publish, publish_file, update, read, comment, list_comments) | MCP-first; works with Claude Code, Codex, Cursor, Devin, Claude Desktop |
| Account gates | Required for some imports | Free for individuals; no account required for commenters |
| Endorsements on homepage | Karpathy, Thariq, Ryan Carson | None visible |

**Shared workflow shape (the actual convergence):**

1. Agent generates HTML/markdown
2. Publish to the tool → live URL with stable identity
3. Humans review with inline comments
4. Agent reads the comments and revises
5. Iteration loop continues until "if good, go build" (Raunaq's framing)

Both tools implement steps 1-5 with MCP as a primary integration path and inline comments as the review surface.

**Differences (mostly orthogonal to the workflow):**
- html-docs is closed/SaaS; workplane is partially open
- html-docs has high-profile endorsements; workplane has none visible
- html-docs requires accounts for some imports; workplane is free without account
- html-docs is HTML-first; workplane lists markdown, HTML, and screenshots
- Creator visibility differs sharply: Raunaq is named and uses html-docs.com publicly in his Meta workflow; Matan is anonymous on the workplane.co homepage and only surfaces via GitHub commit history

**Why this matters:**

The pattern (agent ↔ human review loop with publish-and-comment as the primitive) is now empirically observable as something multiple independent producers reach for. Just like F21 named the hosting-layer convergence (short URL + `/raw` + minimal chrome + honest attribution), F22 names the live-editing-layer convergence:

- Publish endpoint that accepts agent-generated content
- Stable URL identity per published doc
- Inline comments as the review surface
- Agent integration via MCP (in both implementations)
- Version history of the iteration

The MCP common denominator is itself notable — both tools lead with MCP integration, which suggests MCP adoption is the *enabling substrate* for this layer's convergence. Without a standard agent-to-service protocol, each tool would have to ship bespoke integrations; with MCP, the same skill works against any host.

This is the "canvas step" Capsule explicitly doesn't compete with. F22 names that the canvas step is a real, reproducible layer in the lifecycle — not a one-off product idea.

**The composition story is now empirically backed at every layer:**

- **Live editing**: html-docs + workplane converge on the pattern (F22)
- **Format / seal**: Capsule (this project; multi-producer interop already validated across LLMs + Mintel)
- **Hosting**: MinDev + htmlbin converge on the pattern (F21)
- **Discovery**: llms.txt (one major implementation; adoption signal via Chrome Lighthouse rather than convergence)

Four lifecycle layers; convergence-pattern findings at three of them. The format-and-host split + the editing-and-format split + the host-and-discovery split are all real.

**Spec implications:** None directly. Capsule occupies the seal step downstream of the live-editing layer; the live-editing layer doesn't need Capsule's discipline because the artifact is still mutating. The composition is what matters, not Capsule mandating anything in the upstream layer.

**Open questions:**

- What happens when a Workplane or html-docs doc graduates to a sealed Capsule? Neither tool currently has Capsule export. Would there be value in proposing a "freeze to Capsule" capability? Not yet — empirical pressure not there.
- Will the live URLs themselves become canonical (no need to seal)? Or will users still want a sealed downstream artifact for archival? Depends on durability of the live-editing tools over years.
- The MCP-as-enabling-substrate observation deserves its own follow-up — is MCP the common denominator across multiple converging patterns? Worth checking against F21 (do MinDev/htmlbin both use MCP-style standardization for upload?).
- Workplane's "the working plane between AI and humans" framing is sharper than html-docs.com's positioning; worth borrowing the *layer name itself* — possibly rename "live editing layer" to "working plane" in the project's terminology going forward. Defer until the term is stress-tested.
- Will a third live-editing implementation appear, validating this as a proper pattern (per F21's "three or more is a pattern that probably deserves formal documentation" framing)? Track.

**Cross-references:**
- [F21](#f21-independent-convergence-on-the-host-contract-pattern-mindev--htmlbin) — the parallel hosting-layer convergence; same shape of finding
- [PRECEDENTS.md](PRECEDENTS.md) — Raunaq / html-docs.com + Matan / Workplane entries added to "Current voices in HTML-for-AI"; position table grew to 9 rows
- [voices/README.md](voices/README.md) — queue tracking and graduation rule

### F23: URN-not-URL QR encoding — empirical validation of a deliberate spec choice

**Date:** 2026-05-21

The Core spec ([CAPSULE_CORE.md](CAPSULE_CORE.md) Rule 4 supplementary QR-code guidance) recommends embedding a QR code that encodes `urn:uuid:<uuid>` — the URN form, not a live URL. The reasoning at the time was that URNs are non-resolvable but *honest* about being non-resolvable, while URLs encode a host's distribution policy and that policy can change without the format changing. A real-world incident on 2026-05-21 validated this reasoning concretely.

**What happened:**

Mintel's `build_exploration_map_capsule.py` had been encoding `https://mindev.ca/c/<uuid>` in the on-map QR (the rationale: a phone scanning a printed map could land directly on the live capsule). This was a deviation from the spec — fine in isolation because MinDev was a known host and the URLs worked at the time.

On 2026-05-21 MinDev shipped a security-driven schema change that removed the `public` visibility tier entirely. Existing `public` rows migrated to `org`; the `mindev.ca/c/<uuid>` URL pattern now returns `403 {"error":"forbidden"}` to anonymous callers. Org members keep access via Firebase auth; external recipients need a share-token URL (`mindev.ca/api/c/share/<token>`) instead.

**Immediate consequence:** every previously-printed Mintel map carrying a QR pointing at the live URL now resolves to a 403 for any anonymous scanner. The QR didn't break structurally — it still scans, still produces a URL — but the URL has changed semantic meaning. Was: *"fetch this capsule"*. Now: *"fetch this capsule if you happen to be authenticated to the right org on the device scanning the code"*. The producer (Mintel) had no way to know in advance that this change would happen on the host side; the printed maps in the wild can't be recalled.

**What this validates:**

- **URN form for the QR is the right default**, not the URL form. URN is honest about being a pointer-without-resolution-guarantee. URL encodes an assumption about host behavior that the format has no business making.
- **The format/host split documented in [`spec/HOSTING.md`](spec/HOSTING.md) is real, not theoretical.** Format-layer artifacts (capsules) should not bake in host-layer policy decisions (visibility tiers, auth gating, resolution semantics) because those decisions belong to the host and can change without the format changing. The capsule's bytes are identical before and after MinDev's change; what changed was who-can-fetch-them — a pure host concern.
- **The deliberate spec choice was correct**, even though the URN form is "less convenient" for the immediate scan-and-view use case. Convenience that's contingent on host policy isn't durable; honest pointers that require an extra step are durable. The convenience-vs-durability trade-off has now been demonstrated empirically, not just argued abstractly.

**The fallback pattern that does work:**

If a producer wants the QR to resolve to a live capsule via the URL form, the right path is:

1. Producer asks host to mint a share token at upload time (the Mintel-side ask currently flagged in MINTEL_TODOS.md: `?mint_share_token=true` on the upload endpoint, returning a `share_url` in the response)
2. Producer encodes `https://<host>/api/c/share/<token>` in the QR
3. This URL is anonymous-resolvable *by design*, has revocation, has audit, has expiry, has view-cap — and survives host policy changes because the share-token endpoint exists specifically for anonymous resolution

The URN form remains the right default; the share-URL form is opt-in for cases where the producer explicitly wants anonymous resolution AND has minted a token at build time AND has accepted the share-token's audit/revocation tradeoffs.

**Spec implications:**

None directly — the spec already says URN. This is post-hoc empirical validation, not a spec change. A one-paragraph addition to `spec/HOSTING.md` (landed alongside this finding) names visibility tiers as host-side policy and cites this case as the canonical example of why format artifacts shouldn't bake in resolution-semantics assumptions.

**Open question:**

What should a producer's build script do for capsules whose host visibility is `org` (where anonymous scan won't resolve)? Three reasonable patterns, currently unsettled across implementations:

1. **Always encode the URN** (safe default; recipient has to type or paste UUID into a host UI to view).
2. **Encode the URL but add an alt-text/caption** like "Sign in to <org> to view" so a scanner knows what to expect.
3. **Encode the share-URL when a token has been minted** (opt-in to anonymous resolution; requires producer to have requested a share token at upload time).

Currently the canonical convention to recommend isn't settled. Worth tracking whether other compiler-kind producers reach for one shape vs. another — if a second independent producer makes a different choice and ships, the convergence (or divergence) becomes a future finding.

**Methodological note — the agent-to-agent collaboration pattern:**

This finding emerged from a Claude-on-MinDev-side conversation pushed through to a Claude-on-Mintel-side conversation via the user as a human-router. Each agent owned its own system's concerns: MinDev's agent diagnosed the threat model + drove the schema change + posted prod verification; Mintel's agent audited the producer-side fallout + flagged the QR-encoding gap + committed to build-script patches in its own domain. The htmlcapsule project's record (this finding) is then the third surface that absorbs the cross-domain learning. Worth tracking as a pattern: multi-agent + human-router collaboration is producing real research artifacts (this F-finding) faster than a single-agent loop probably would.

**Refinement (2026-05-21, [F24](#f24-host-vs-registry--the-missing-commitment-layer)):** The URN-as-default recommendation in this finding is correct *for producers without signal about host commitments*. The case where a producer knows their target host has declared registry compliance opens a different reasonable choice — encoding the URL becomes a calibrated bet against a published contract rather than a gamble. F24 introduces the host vs. registry distinction and sketches a Capsule Registry Compliance v1 contract in [spec/HOSTING.md](spec/HOSTING.md). The default for general-purpose producers (and for the Mintel build script today, since MinDev has not declared compliance) remains URN; the option to encode URLs becomes available when the destination host has declared compliance.

**Cross-references:**
- [CAPSULE_CORE.md Rule 4 supplementary QR guidance](CAPSULE_CORE.md) — the deliberate URN-not-URL spec choice
- [spec/HOSTING.md "Visibility tiers as host-side policy"](spec/HOSTING.md) — the addition that names this as the canonical example
- [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) — the Mintel Copper Dome capsule observed there used the URL form in its QR
- [F21](#f21-independent-convergence-on-the-host-contract-pattern-mindev--htmlbin) — the broader host-contract pattern; visibility tiers are one axis hosts vary on
- [F24](#f24-host-vs-registry--the-missing-commitment-layer) — the synthesis that refines this finding

### F24: Host vs. registry — the missing commitment layer

**Date:** 2026-05-21

[F23](#f23-urn-not-url-qr-encoding--empirical-validation-of-a-deliberate-spec-choice) documented the empirical case where Mintel's URL-encoded QR codes broke after MinDev removed the `public` visibility tier. The first reading of that finding was: *URN is the right default; URL was a deviation that bit Mintel*. In a conversation following the F23 commit, the maintainer pushed back with a sharper question: at build time, Mintel knows it's uploading to MinDev; the URL form is more useful than URN for the recipient; the failure mode isn't producer error, it's that **the host (MinDev) hadn't committed to keeping the URL working**. The refined synthesis: the project's format/host split has been treated as "format and host are independent strangers," but in real workflows producers and hosts often want to be *coordinated via published contracts*. The format itself stays agnostic; some hosts may want to *declare more*.

**The naming move: host vs. registry**

- A **host** serves capsules. No commitments beyond "the bytes go out the way they came in."
- A **registry** is a host that *commits to keeping serving them in a particular way* — stable URL patterns, visibility honor, deprecation discipline, attestation headers, no surprise breaking changes.

Hosts can choose to remain just hosts or to declare themselves registries (by publishing a compliance statement at a well-known location). The format takes no position; producers and recipients gain a signal they can act on.

**What changes about F23's "URN is the safe default":**

- F23's recommendation is *correct for the case it documented* — producers without signal about host commitments should default to URN because URL form is a bet on unspecified host behavior.
- F23's recommendation is *incomplete*. When producers know their target host has declared registry compliance — including commitments about URL stability and visibility-tier preservation — encoding the URL becomes a calibrated bet against a published contract, not a guess.
- The Mintel/MinDev case wasn't "Mintel made a mistake by deviating from spec." It was "Mintel made a reasonable bet on MinDev behavior that MinDev hadn't promised to keep." The fix isn't "always use URN" — it's "encode URN by default; encode URL when the host has declared compliance and visibility commitments are part of the declaration."

**Sketched Capsule Registry Compliance v1 contract (not yet adopted by any host):**

1. **Stable URL pattern.** `<host>/<prefix>/<uuid-or-slug>`. Pattern doesn't change without a major version bump + redirect period.
2. **`/raw` byte-identical endpoint** at the URL + `/raw`. Never mutates the body.
3. **Visibility commitment is part of the contract.** Whatever visibility tier a capsule is uploaded under is honored for the capsule's lifetime, OR migration is announced with notice. Removing a tier without grandfathering existing capsules is a breaking change.
4. **Host-attestation headers** (`x-capsule-content-hash`, `x-capsule-uuid`) on every `/raw` response.
5. **Honest deprecation.** Breaking changes get a public changelog + deprecation window + migration path. Surprise policy changes that break in-the-wild artifacts are out of compliance.
6. **Capsule immutability.** The registry serves the bytes it received. No mutation, no re-rendering, no injection.

Full sketch with proposed well-known location (`<host>/.well-known/capsule-compliance.json`) and adoption status is in [`spec/HOSTING.md`](spec/HOSTING.md) under "Hosts vs. registries — the optional commitment layer."

**Mapping the MinDev incident onto the proposed contract:**

- MinDev was operating as a *host*, not a registry, at the time of the `public` removal.
- The change was *security-correct* but *registry-breaking*: existing-public capsules' anonymous resolvability was removed without grandfathering or notice.
- If MinDev had been operating under compliance v1, the `public`-removal would have required either grandfathering existing capsules at their original visibility OR a major version bump + migration period.
- MinDev can retroactively declare compliance v1 (with the recent change being framed as the v0→v1 migration event itself) or refuse to claim it. Producers like Mintel benefit either way: a declared host is safe to encode URLs against; an undeclared host is not.

**Why the host-vs-registry distinction matters more broadly:**

The project's layer picture (format / live-editing / hosting / discovery) treats each layer as independent. The compliance layer adds a *coordination axis*: within a layer, implementations can choose to coordinate via published contracts. Registry compliance is one example; spec/HOSTING.md's descriptive host-contract pattern is another, weaker example. This is how the open web works generally — browsers treat URLs as untrusted by default, but sites can opt into stronger trust by adopting HTTPS / HSTS / CSP / etc. The Capsule project can offer the same opt-in for hosts.

The format/host split stays correct as the *baseline*; the compliance layer is the *upgrade path* for hosts that want to be more than baseline.

**Spec implications:**

- New section in [`spec/HOSTING.md`](spec/HOSTING.md): "Hosts vs. registries — the optional commitment layer" sketches the compliance contract. Stays descriptive (matching HOSTING.md's overall disposition) — defines what a host *could* commit to, doesn't force any host to commit.
- F23's "URN-only default" recommendation is refined here, not retracted. Default for producers without signal remains URN. Case where a producer has signal (registry compliance declared) opens the URL option as a calibrated bet.
- **No Core spec change.** CAPSULE_CORE.md Rule 4 supplementary QR guidance still says URN — that remains the right default *for the format itself*, which has no opinion on which hosts produce capsules and where they end up. The format stays agnostic; the registry-compliance layer is opt-in at the host's surface, not at the format's.

**Open questions:**

- **Self-declared vs. third-party verified?** Self-declared (host publishes its own `/.well-known/capsule-compliance.json`) has lower friction; third-party verified has stronger guarantees. No empirical pressure yet to pick. Lean toward self-declared for v1 — easier to bootstrap.
- **Version-bump discipline for the contract itself?** If compliance v1 ships and then needs revision, what's the upgrade path for hosts that have declared v1? Standard semver-shaped questions; deferrable until at least one host signs on.
- **Should the format carry a signal about which compliance level its host declared** — e.g., a manifest field naming the registry's declared compliance? Honestly leaning **no**: that would couple format to host, exactly the thing the project deliberately avoids. The compliance declaration belongs at the host's surface (its `/.well-known/`, its docs), not in the capsule's bytes.
- **First adoption?** MinDev is the natural first candidate — its recent security change can be framed as the v0→v1 migration event. htmlbin is a second candidate; the personal-sharing host the maintainer is planning is a third. If multiple hosts adopt the same compliance level voluntarily, the contract crystallizes into something a future capsule producer can rely on across hosts.

**Methodological note — the pushback was the finding:**

F24 didn't come from a tool, a capsule, or an external piece. It came from the maintainer pushing back on F23's framing during a follow-up conversation: *"isn't what we are dancing around is the registry being htmlcapsule-spec compliant?"* That single sentence reframed F23 from "Mintel made a mistake" into "the project lacks a host-commitment layer." Worth tracking as a research-method observation: the project's most useful conceptual moves are sometimes made by the maintainer pushing back on a finding's first framing, not by new external pressure. F23's empirical event was necessary but not sufficient; the synthesis required the conversational refinement.

**Cross-references:**
- [F23](#f23-urn-not-url-qr-encoding--empirical-validation-of-a-deliberate-spec-choice) — the precipitating finding; URN-as-default refined here, not retracted
- [spec/HOSTING.md "Hosts vs. registries"](spec/HOSTING.md) — the compliance contract sketch this finding motivated
- [F21](#f21-independent-convergence-on-the-host-contract-pattern-mindev--htmlbin) — host-pattern convergence; the compliance contract makes explicit what F21 observed implicitly

### F25: ChatGPT producer-population reads Core supplementary guidance reliably; aesthetic adapts to content domain; legacy "Artifact Capsule" wording persists in user-side prompt templates

**Date:** 2026-05-21

A batch of 7+ ChatGPT-generated capsules (GPT-5.5 Thinking; conversation summaries across varied domains — hands-free coding workflows, geological target reinterpretation, Indigenous-rights conversation, design-award fit assessment, propane fire-pit purchase brief, Kia Sedona vs pickup decision, Swedish mining permits, Colombian pension-refund letter) were reviewed against Core v0.3.0. All produced from the user's prompt template *"Produce an Artifact Capsule per the Core spec (attached) summarizing this conversation."*

This is the largest single-batch empirical sample of a single LLM producer kind working from Core v0.3.0 to date. Five distinct findings emerged.

**1. All five required blocks present.** Rule 2 (no network) and Rule 12 (pre-rendered content) honored across every capsule in the batch. Multi-producer interop validated yet again at scale.

**2. Rule 4 supplementary QR-code guidance followed faithfully across the population.** Every capsule embeds a QR encoded as `urn:uuid:<uuid>` (per [F23](#f23-urn-not-url-qr-encoding--empirical-validation-of-a-deliberate-spec-choice)'s URN-not-URL choice), placed top-right in the header, sized 88×88 px (Core suggested 80–96 px), with `image-rendering: pixelated`, a `data:image/png;base64,...` URI, `alt="QR code for capsule UUID <uuid>"`, and a `<figcaption>` showing the UUID's first 8 chars. **This is independent reproduction of supplementary-guidance compliance, not just compliance with the twelve numbered rules.** When Core writes implementation-recipe-shape guidance — specific placement, exact sizing, a Python `qrcode`-library code example — LLM producers follow it precisely. This strengthens the F18/F19 multi-producer interop claim into a sharper version: *Core's supplementary sections are load-bearing in practice, when they're written as recipes.*

**3. Where Core leaves implementation open, producers diverge with their own conventions:**

   - **Integrity hash:** Core explicitly excludes integrity from required content (it lists *"Content hash protocol and integrity verification"* under *"What this short spec does NOT cover"*). Producers correctly skip the `integrity.content_hash` field. Behavior matches design — *not* a conformance gap, just integrity remaining opt-in for capsules that don't need tamper-detection.
   - **Rule 7 verification convention:** Core says *"Capabilities don't lie. Every capability declared in the manifest must have a working implementation"* but doesn't specify HOW to mark the implementations. The validator's `data-capsule-action="<cap>"` heuristic was added in v0.3.2 (surfaced by external compiler-kind producers and recorded in v0.3.2 release notes) — but that convention lives only in the validator, not in Core. LLM producers in this batch each invent their own pattern (`data-action="copy-json"`, `id="copy-json"`, plain DOMReady listeners). The capabilities ARE implemented and DO work in the browser; only the validator's auto-verification heuristic misses them. **Research signal:** if a Rule 7 verification convention should reach LLM producers, it needs to be in Core (or in the produce-prompt fragment), not only in the validator. A validator heuristic alone doesn't propagate back to producer kinds that aren't being validated by that exact tool.

**4. Producer aesthetic adapts to content domain.** Genuinely new observation. Capsules in the batch use distinctly different visual treatments per subject:

   - Geological target report → warm earth tones (sand/cream), serif headings, sample-card layout that nods at field-notebook aesthetics
   - Propane fire-pit purchase brief → warm cream/orange/brown palette, fire-appropriate vibe, decision-matrix table
   - Legal identification-update letter → neutral clean palette, legal-document neutrality
   - Sweden mining permits → cream with green accents (tonal nod to Swedish flag)
   - Voice/coding workflow → tech-blue with sans, system-font, dashboard feel
   - Indigenous-rights conversation → cool grey/blue editorial
   - Vehicle-decision brief (Sedona vs pickup for camping) → warm woodsy/camping cream-brown
   - DNDA fit assessment → modern blue-grey editorial

   The format constrains structure (five blocks, twelve rules, no network) but does not constrain visual design at all, and producers exploit that to make Capsules feel domain-appropriate. The aesthetic is *part of what's being archived* — a reader opening a geological capsule five years from now will see it in the visual register the producer thought matched the subject, which is itself a form of preservation. This is unspecified-but-useful emergent producer behavior. **For project posture:** if a future "house theme" became tempting (one stylesheet to rule them all), this is the data point that argues against constraining it. Producers treating Capsules as design objects (not just data containers) is doing useful preservation work that a uniform stylesheet would erase.

**5. Legacy "Artifact Capsule" terminology persists in user-side prompt templates.** All capsules in the batch have `prompt_received` containing *"Produce an Artifact Capsule per the Core spec (attached)…"* — using the v0.1 name that was renamed to just "Capsule" in v0.2 (see [GLOSSARY.md](GLOSSARY.md) and [spec/CAPSULE_SPEC.md](spec/CAPSULE_SPEC.md) naming-history notes). The Core spec itself uses "Capsule" everywhere — its own produce-prompt template ([CAPSULE_CORE.md](CAPSULE_CORE.md) §"How to ask an LLM to produce a capsule") says *"Produce a Capsule"* — so the legacy term is propagating via the user's stored prompt template, not via the spec. **Project response (this commit):** added an explicit "use the canonical name" reminder immediately above Core's produce-prompt section, with a back-reference to this finding. Doesn't change spec rules; closes the loop by making the canonical name unmissable to anyone templating their own prompts. The producer-side field values are accepted under legacy v0.2 compatibility per the naming notes in the full spec.

**Cross-references:**
- [F18](#f18-peer-review-2026-05-19--sharpest-framing-landscape-position-and-trust-model-gaps) — peer-review framing of multi-producer interop
- [F19](#f19-design-tool-integration-experiment--claude-design-with-capsule_coremd-attached) — Claude Design as first independent LLM-kind producer reaching conformance from Core alone
- [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) — Mintel as first compiler-kind production capsule
- [F23](#f23-urn-not-url-qr-encoding--empirical-validation-of-a-deliberate-spec-choice) — URN-not-URL QR encoding choice; this batch is the largest sample confirming producers respect that default
- [CAPSULE_CORE.md "How to ask an LLM to produce a capsule"](CAPSULE_CORE.md) — the produce-prompt where the "use canonical name" reminder was added

### F26: Core spec accommodates 10 MB domain-specific media capsules without rule changes

**Date:** 2026-05-21

**Source:** One-off domain-specific song capsule experiment — Paul McCartney & Wings, "Nineteen Hundred and Eighty-Five" (1973). A 7.6 MB MP3 plus Wikipedia-sourced metadata (personnel, role on *Band on the Run*, covers, critical reception, live history, composition genesis quote) plus a transcribed lyric sheet, sealed as a 10.16 MB self-contained HTML capsule (UUID `e26b58da-a3b2-4675-aa33-78511ad93e60`, currently at `capsule_version` 1.1.0). Shipped 25/25 against the reference validator on first build with zero spec changes required.

**Finding.** Core spec v0.3.0 plus the existing supplementary recipes (QR convention, CSP defaults, capability vocabulary) is sufficient for domain-specific binary-media capsules at the 10 MB scale. Spec held at every dimension tested:

- **Domain via `type` field:** `type: "song"` — Core accepts arbitrary domain values without modification; the producer-population pattern from F25 extends straightforwardly to media domains.
- **CSP delta is minimal:** `media-src data:` is the only addition required to the default recipe (default-src 'none' baseline; img-src data: already present for QR codes). No new directives.
- **Capability vocabulary extends naturally:** `media.play_audio` and `media.download_audio` follow the established `<domain>.<action>` convention added in v0.3.2; Rule 7 markers (`data-capsule-action="media.play_audio"` on the `<audio>` element) were validated heuristically as expected.
- **Size limits hold under-cap:** 10.16 MB sits under both the 15 MB soft-warn tier and the 20 MB hard cap. Reference validator does not penalize binary-heavy capsules under-cap; size scaling is graceful.
- **Round-trip extraction works:** the `media.download_audio` capability recovers the embedded MP3 byte-identically via a `dataUriToBlob` runtime helper — the file is genuinely portable, not just embedded-for-display. The downstream "this is just a file" mental model from F21 holds even for 10 MB media.
- **Aesthetic adapts to content domain:** producer (hybrid: Claude Opus 4.7 + maintainer) selected warm earth tones (`#f4ebd9` background, `#b8421a` accent) appropriate to a 1970s rock recording. Extends F25's "aesthetic adapts to content domain" finding from text-only ChatGPT capsules into hybrid-produced media capsules — the pattern is producer-kind-agnostic.
- **Version semantics in practice:** the song capsule went v1.0.0 (audio + metadata only) → v1.1.0 (added transcribed lyric sheet) on the same UUID via `capsule_version` bump alone. No `parents[]` chaining was needed because nothing was distributed between versions.

**Implication for the spec.** Core is not under-specified for binary-media capsules at this scale. No new rules needed; no Core changes triggered. The fidelity gradient between LLM-produced and compiler-produced capsules (per F25) remains the open work, not size or domain scaling.

**Implication for parked Appendix E.11 fields.** The song-with-lyrics-added scenario lived through the exact use case the parked `supersedes[]` / `derived_from[]` / `change_summary` fields (raised by external review, parked in spec Appendix E.11 pending real-producer pressure) would address — same UUID, content change worth signaling to downstream holders, current solution is just a `capsule_version` bump. Since the capsule was *not* distributed between v1.0.0 and v1.1.0, the parked fields stayed parked correctly: empirical pressure point is now recorded for the next time a producer needs to signal "this supersedes my previously-shared v1.0.0" without minting a new UUID.

**Cross-reference.** The producer for this capsule was the in-conversation Claude Opus 4.7 hybrid pattern (the same producer pattern as the project's landing page itself, per its `generator` block). This is the first F-finding from a deliberately one-off, domain-specific, copyright-laden capsule that was not committed to the public repo — a different empirical-pressure source than F25's open-corpus producer population, and a useful complement.

**Related findings:**
- [F19](#f19-design-tool-integration-experiment--claude-design-with-capsule_coremd-attached) — Claude Design as first independent LLM-kind producer reaching conformance from Core alone
- [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) — Mintel as first compiler-kind production capsule
- [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates) — producer-population reads supplementary guidance; aesthetic adapts to content domain (the source claim this finding extends to media)
- [Spec Appendix E.11](spec/CAPSULE_SPEC.md) — parked `supersedes[]` / `derived_from[]` / `change_summary` fields awaiting empirical pressure

### F27: The landing-page genre tension for applied-research projects resolves by splitting, not merging

**Date:** 2026-05-22

**Source.** The May 2026 landing-page exploration arc on this project — from `index.html` v10.x through v13.0.0, plus four comparison sketches (`landing-sketch.html` v1/v2, `research-sketch.html` v1/v2, `positioning-sketch.html`) — and three independent external reads (devil's-advocate critique pass, the in-flight Claude landing-agent's hero pick during the parallel-sketch experiment, and a ChatGPT Deep Research site survey). The maintainer captured the tension directly during the arc: *"it's hard to create a landing page for something which is, at its heart, research, albeit applied."*

**Finding.** A landing page for an applied-research project pays a real cost trying to do both jobs at once. Landing pages convert (one claim, one CTA, one demo, optimize for click); research pages persuade (cite everything, walk the argument, optimize for "you can verify this"). When a single page tries to do both, it pays both costs and converts on neither. The exploration arc tried all three pure-genre commitments plus the hybrid before settling:

1. **Hybrid** (research narrative + landing elements in one page) — `index.html` through v12.0.0. Numbered Observations / Questions / Answers + nine hero candidates + CTAs + research apparatus all on one surface. The genre tension was visible to every reader: research apparatus showed through landing veneer; landing apparatus interrupted research depth. Both genres paid for the other.
2. **Pure landing** (Stripe / Linear stripped) — `landing-sketch.html` / `landing-sketch-v2.html`. Conversion-shaped, ~9% of the prose volume. Lost the research argument; "research project" signal collapsed to "yet another file format."
3. **Pure research-paper** (NeRF-style academic) — `research-sketch.html` / `research-sketch-v2.html`. Author block / abstract / numbered findings / methods / related work / cite-this-work. Lost the conversion shape; the word "Abstract" reads as "not for you" to non-research audiences.
4. **Synthesis** (positioning-led, lifecycle-diagram-centered) — `positioning-sketch.html`. Pain-first hero (*"Your AI work shouldn't die when the chat closes."*), lifecycle SVG as the centerpiece. The most novel of the single-page options; still asks one URL to carry both audiences.

**The resolution that worked.** The two-page split — listed as "Option B" / "Option D" during the exploration but consistently underweighted because splitting *feels* like the hedge move. It isn't. The production landing (`index.html` at v13.0.0, UUID `7d1a1ac8`) is the pure-landing commit, optimized for conversion. The full research-narrative is preserved as a separately-accessible page (`exploration.html`, UUID `881fed04`), optimized for depth. Same UUID lineage (via `parents[]`); distinct identities. Each page is genre-pure; each page pays only its own genre's cost.

**Implication.** The framing "decide between landing-genre and research-genre" was wrong all along — it presumed one URL. The right framing was "decide which page is which." The genre tension dissolves when you stop asking one URL to carry both audiences.

**Generalization.** This pattern likely transfers to any applied-research project with a mixed audience (technical / general / research-leaning). Front door optimized for *"what is this and why should I care in 30 seconds"*; deep page optimized for *"I'm bought in and want the full argument with citations."* Cross-link explicitly. Don't try to merge.

**Method observation.** Three independent reads converged on the split — devil's-advocate critique, the landing-agent's hero pick (which selected "HTML you can keep." as the strongest single claim, implying genre commitment), the ChatGPT Deep Research review (which framed the project as research that doesn't need a sales-y landing). When multiple independent reads converge on a structural conclusion that you'd been resisting (because it feels like a hedge), that convergence is a stronger signal than any single read. Worth tracking as a methodological pattern: *external review convergence on a structural decision is empirical pressure even when the decision feels like cowardice.*

**Related findings:**
- [F18](#f18-peer-review-2026-05-19--sharpest-framing-landscape-position-and-trust-model-gaps) — peer review as a source of structural framing pressure (same kind of empirical-pressure pattern operating at the spec level)
- [F24](#f24-host-vs-registry--the-missing-commitment-layer) — same split-instead-of-merge pattern at the hosting layer; when two roles are tangled, split first
- [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates) — the maintainer's research-method post-mortem on external-LLM review as a recurring source of design pressure
- [CHANGELOG `[Landing decision — v13.0.0]`](CHANGELOG.md) — the operational record of the commit, including the parents[] chain and the role assignment for `exploration.html`
- [`design/proposal.html`](design/proposal.html) — the design memo from Claude Design that synthesized the landing direction (anti-context-loss pain framing + lifecycle layer + indigo brand) before the commitment

### F28: Producers reach for Capsule-shape independently when given the idiom but not the spec — empirical pressure for discoverable onboarding

**Date:** 2026-05-22

**Source.** Review of a ChatGPT-produced MIDI capsule POC (Mozart Lacrimosa, ~220 KB; preserved at [`capsule-midi/proofs/lacrimosa-chatgpt-poc.html`](https://github.com/bigfancygarden/capsule-midi/blob/main/proofs/lacrimosa-chatgpt-poc.html)). The user asked ChatGPT to "make a DAW-like HTML capsule from this MIDI" *without* attaching Core as a prompt fragment.

**Finding.** Without Core attached, the LLM producer (ChatGPT in this case) independently reached for the **Capsule idiom** — single-file HTML, embedded JSON manifest, schema declaration (`capsule_schema: "midi-stem-capsule-v0.1"`), `parents[]` array (with composition reference), `sha256` of source bytes, honest `license_note` with "verify before redistribution" caveat — but missed the **Capsule specifics**:

- ❌ Single `<script id="capsule-json">` block containing both manifest + data, instead of the five separate spec-required blocks (`capsule-manifest`, `capsule-data`, `capsule-style`, `capsule-root`, `capsule-runtime`)
- ❌ No integrity hash block
- ❌ No `data-capsule-action` markers on UI buttons (Rule 7 — declared capabilities have no implementation-binding convention)
- ❌ No CSP `<meta>` block
- ❌ Empty `<div id="lanes">` / `<div id="facts">` populated only at runtime (Rule 12 borderline)

Validator result: **5/10 pass, 1 warn, 4 fail** — the basic-shape checks pass (HTML5 doctype, html/body, no external network refs, well-formed runtime JS, under-cap size), but every structural check fails (5-block requirement, manifest section parseable, data section parseable, content hash verifies).

**Companion to [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates).** F25 observed producers *with* Core attached reliably follow supplementary guidance. F28 observes producers *without* Core attached reach for the shape but miss the specifics. Together: **Core works when attached as a prompt fragment; when not attached, the idiom is reached for organically but the specifics are reinvented.**

**Implication for the spec — discoverable onboarding is empirically warranted.** The Capsule shape is a real attractor — LLMs reach for it even without prompting — but they can't reproduce the structural specifics without seeing them. Possible spec-level responses:

1. **Extend `/llms.txt`** to publish Core as a paragraph-level summary plus a link to the full Core, so any LLM doing web research on htmlcapsule.org lands on the discipline naturally. Cost: small. Benefit: every LLM that's done its own research has Core in context.
2. **Publish a one-page "Producer starter kit"** — Core + minimal example + the most common producer mistakes (5-block vs single-json, missing Rule 7 markers, etc.) — at a stable URL discoverable from `llms.txt`. Cost: medium. Benefit: producers without Core fall back to a clear failure mode (the starter kit) rather than reinventing.
3. **Document the "reached for the shape but missed the specifics" failure pattern** in `spec/CAPSULE_SPEC.md` as a known gap, with the response being "attach Core; without Core attached, expect 5/10 at the validator." Cost: very small. Benefit: sets accurate expectations.

The maintainer's pick (per `capsule-midi/FEEDBACK.md`): option 1 is the smallest and most discoverable. Worth doing as part of the next operational pass.

**Methodological side-finding.** This is the second time a producer-side experiment has yielded research-record material that crosses back into spec design. The pattern is now visible:

```
producer attempts a domain → hits a friction → friction is logged in producer's FEEDBACK.md → harvested into htmlcapsule's RESEARCH.md as an F-finding → may trigger a spec change
```

This is the *cross-project memory pattern* the producer projects (capsule-midi, Shasta, capsule-photo, Mintel) use to feed empirical pressure back into the spec without unilaterally inventing changes. Worth naming as a deliberate methodology — call it **upstream feedback discipline**. The producer projects own the friction; the spec project owns the response.

**Related findings:**
- [F19](#f19-design-tool-integration-experiment--claude-design-with-capsule_coremd-attached) — Claude Design reached conformance from Core alone (Core attached → producer succeeds)
- [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates) — ChatGPT-with-Core-attached reads supplementary guidance reliably (Core attached → producer succeeds at specifics)
- [F26](#f26-core-spec-accommodates-10-mb-domain-specific-media-capsules-without-rule-changes) — Core spec accommodates 10 MB domain-specific media capsules without rule changes (the song capsule experiment; same Lacrimosa POC seeded this line of research)
- [`capsule-midi`](https://github.com/bigfancygarden/capsule-midi) — the producer project that surfaced this finding; raised in its `FEEDBACK.md` as item F-A before being filed here

### F29: iOS QuickLook surfaces graceful degradation as a first-class spec principle, not just a Rule 12 implication

**Date:** 2026-05-22

**Source.** Two pieces of empirical pressure converging:
- The capsule-midi v0.2.0 producer template added a `<noscript>` warning naming iOS Files-app QuickLook explicitly: *"Audio playback &amp; interactivity require JavaScript. On iOS: this file is currently in the Files-app preview. Tap the share icon and choose Open in Safari to enable playback."* That's a producer-side adaptation to a real distribution-environment constraint.
- An external strategic-review discussion (preserved in the parent chat thread) argued at length that iOS QuickLook is the canonical hostile environment Capsules should design for, not against, and proposed promoting graceful degradation to a first-class design principle with manifest-level declarations and per-domain guidance.

**The actual environment.** iOS Files / Mail / Messages / AirDrop / iCloud Drive / Notes preview surfaces route HTML attachments through Apple's [Quick Look](https://developer.apple.com/documentation/quicklook) framework. Quick Look is a passive preview system — it renders HTML/CSS but does not execute `<script>` tags. This is a defensible security posture (untrusted attachment HTML running JS from every preview surface would create real attack vectors) but it means a capsule whose substance lives in the runtime fails the iOS-preview first impression.

**Finding.** The spec **already covers most of this** but doesn't surface it as the design discipline it's pointing at. What's already there:

- **Rule 12** (`CAPSULE_CORE.md`) — pre-rendered content must exist in HTML before JS runs.
- **`spec/CAPSULE_SPEC.md` §2.3 Rendering Model** — explicitly names "iOS Files / QuickLook preview" as a JS-restricted target environment; documents the image-fallback pattern with worked example; articulates "interactive archive (permitted) vs app (forbidden)" with the JS-off litmus test.
- **`domain.exploration_map`** in `DOMAIN_CAPSULES.md` — image-fallback for visualization geometry is documented as a per-domain pattern.

What's missing:
1. **No machine-readable `fallbacks` manifest field.** Producers handle fallbacks ad-hoc in HTML; consumers (validators, registry viewers, downstream tooling) can't programmatically discover "this capsule has a preview-audio fallback at index X."
2. **Per-domain fallback guidance only formalized for `domain.exploration_map`.** Other domains (`domain.midi_stem`, `domain.song`, `domain.photo`) need explicit guidance about what their JS-off representation should be.
3. **The three-mode taxonomy is implicit.** §2.3 articulates the JS-off litmus but doesn't name the architectural framing the pasted discussion landed on: a capsule should degrade from **runtime (full JS app)** → **document (readable artifact)** → **preview (consumable media or static representation)**.
4. **iOS QuickLook is mentioned but not centered** as the canonical hostile environment to design against.

**Architectural alternatives evaluated and rejected** (so the rejection is on the record):

- **Package format** (`.capsule` / `.dawcapsule` / `.zip` with `index.html`). Violates the load-bearing single-file promise. The whole point of the format is that the artifact passes through any document-passing surface (email, AirDrop, USB, Slack attachment, browser save) as one file. Splitting into a folder structure forfeits that.
- **Native iOS Capsule Viewer app.** Out of scope. The project has stayed format-only by design; a canonical viewer app would compete with "open in any browser" and create platform lock-in.
- **Hosted viewer as required runtime.** Reasonable as a downstream tool but breaks the offline / one-file promise if the capsule *requires* the viewer to be useful. Fine as an "open in browser → richer interaction" escape hatch; not fine as a precondition.

**The principle worth promoting.** The pasted discussion's sharpest framing:

> *A capsule should never become useless when JavaScript is unavailable. It should degrade from app → document → preview.*

The spec says this in two paragraphs of §2.3; this single sentence is the version worth elevating to a section tagline.

**Implication for v0.3.6.** Three concrete additions queued for the next spec release:

1. **Generalize §2.3 image-fallback into a domain-agnostic JS-off fallback pattern.** Add the tagline above. Add iOS QuickLook as the named canonical environment.
2. **Add a recommended (not required) `fallbacks` manifest field.** Shape: `{ preview_audio, poster_image, static_summary_present, requires_js_for, preview_mode_description }`. All optional. Lets producers declare what's there without forcing a structure on producers who don't have anything to fall back to.
3. **Per-domain fallback guidance in `DOMAIN_CAPSULES.md`.** For each domain (existing + idea-queue): name the recommended JS-off representation. Examples: `domain.midi_stem` → bundled rendered audio mix as `<audio controls>`; `domain.song` → the embedded MP3 already IS the fallback (explicit note); `domain.photo` → the image itself is the fallback; `domain.exploration_map` → already documented (image-fallback for geometry).

**Methodological observation.** The pattern that produced this finding is now recurring: the *capsule-midi producer-side adaptation* preceded the spec change. The `<noscript>` block in `templates/capsule.html.tpl` was the producer's response to a real environment constraint; the spec catches up by formalizing the principle. This is the **upstream feedback discipline** named in F28 working in the opposite direction: not "spec change first, producer follows" but "producer adapts to environment first, spec generalizes the pattern." Both directions are healthy and worth tracking.

**Related findings:**
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec--empirical-pressure-for-discoverable-onboarding) — the upstream feedback discipline named; this finding is its first deliberate application in the producer-adapts-first direction
- [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) — the image-fallback carve-out in `domain.exploration_map` was the precursor pattern that this finding generalizes
- [`capsule-midi/templates/capsule.html.tpl`](https://github.com/bigfancygarden/capsule-midi/blob/main/templates/capsule.html.tpl) — the producer template with the iOS-QuickLook `<noscript>` warning that surfaced the gap
- [`spec/CAPSULE_SPEC.md` §2.3](spec/CAPSULE_SPEC.md) — the existing rendering-model section that the v0.3.6 generalization will extend

### F30: Microsoft Copilot as the fourth observed LLM producer family — convergent envelope shape, predictable five-item gap profile, real-world lateral-portability handoff

**Date:** 2026-05-23

**Source.** A colleague of the maintainer produced a substantial HTML artifact (a multi-persona program journey map for a public-interest organization, ~30 KB) using Microsoft Copilot, then sent it to the maintainer, who opened it in Claude for review. No coordination with the maintainer's Capsule project. No CAPSULE_CORE.md attached to the producer's prompt. The colleague's brief was almost certainly a generic "make an HTML journey map for this program" — no Capsule shape requested. Specific organizational details kept out of this finding because the artifact is not yet cleared for public publication; the empirical observations stand independently of which program or organization it depicts.

**Finding — three layered observations:**

**(1) Microsoft Copilot is now the fourth named LLM producer family** in the project's corpus, alongside Claude / ChatGPT / Gemini / Codex previously documented in [F19](#f19-design-tool-integration-experiment--claude-design-with-capsule_coremd-attached), [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale), [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates), and [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec--empirical-pressure-for-discoverable-onboarding). Same convergent envelope shape: single-file HTML, pre-rendered content (Rule 12 spirit, satisfied strongly), CSS-only interactivity via class-toggle spotlight pattern, light/dark theme with `localStorage` persistence, full accessibility baseline (skip link, ARIA, `prefers-reduced-motion`, `prefers-color-scheme`, print media query, mobile responsive). The artifact is substantial: 6 personas × 6 stages swim-lane matrix, 5 named crossover dynamics with inline SVG network diagram, color-coded swim lanes, keyboard navigation, Escape key to clear spotlights. Strong information-design work, not throwaway sketch quality.

**(2) The gap profile is consistent across all undocumented-producer artifacts** in the corpus. Every LLM-producing-HTML-without-Core artifact observed in the project's corpus (this one included) has the same predictable five-item gap:

- ❌ External font dependency (this one: Google Fonts `<link>` to `fonts.googleapis.com` — Rule 2 violation)
- ❌ No `<script id="capsule-manifest" type="application/json">` block
- ❌ No `<script id="capsule-data" type="application/json">` block (the data IS in the HTML as rendered content, but not also as a separate structured-JSON block for machine consumers)
- ❌ Missing IDs on `<style>` and runtime `<script>` (no `capsule-style` / `capsule-runtime` IDs)
- ❌ `<main>` uses an ad-hoc ID (`<main id="main">`) instead of the spec-required `capsule-root`

That's the **predictable five-item gap profile** for undocumented LLM producers. The artifact otherwise passes Rule 9 (accessibility — exceeds it actually, with skip link + aria-labels throughout + reduced-motion + dark-mode-with-system-pref-fallback + print stylesheet), Rule 11 (well-formed JS), and Rule 12 (content pre-rendered, strongly). It's roughly an 80% Capsule. The remaining 20% is the five-item mechanical gap that CAPSULE_CORE.md is precisely designed to close.

**(3) Lateral portability got a real-time empirical validation** in the same session the landing-page thesis for it was added. The page's v14.16.0 commit (May 23) introduced a new "Multi-system, by design" section articulating the lateral-portability thesis: *"I don't want all my chats locked into one AI system... Any AI can produce one. Any AI can read one. The format is the neutral substrate."* Within the same conversation, an actual multi-system handoff occurred:

```
Microsoft Copilot (produced)
  → colleague (received, retained, forwarded)
    → maintainer (received from colleague)
      → Claude (received from maintainer for review, parsed cleanly)
```

The artifact moved across three actors and two distinct LLM systems without any platform-specific coordination. The structured content was intelligible to Claude on first read. The handoff worked. **The thesis isn't speculative — it played out in front of the maintainer in the same conversation that named it.**

**Implication for the spec.** No new rule needed. F30 confirms the value proposition of CAPSULE_CORE.md as a paste-into-prompt fragment: the five-item gap profile is exactly what Core covers. Reinforces the F28 recommendation to **extend `/llms.txt`** with a paragraph-level Core summary so any LLM doing web research lands on the discipline naturally. Microsoft Copilot was not in the producer set when the project was named; F30 documents the addition without requiring spec adaptation.

**Implication for the producer corpus.** The colleague's journey-map artifact is a strong candidate for becoming a **real worked example** for the landing page (currently `UC1` and `UC4` carry "coming soon" amber chips), pending the colleague's permission to publish. The artifact already exists, was produced independently, demonstrates a genuinely complex domain (multi-persona swim-lane matrix with crossover network diagram), and would be a 30-minute mechanical upgrade to conformance:

1. Download Atkinson Hyperlegible WOFF2 (≈60 KB at 2 weights), inline as `data:` URI in `@font-face` → kills Google Fonts dependency
2. Add `id="capsule-style"` to `<style>` tag
3. Change `<main id="main">` to `<main id="capsule-root">` + update skip-link `href`
4. Add `id="capsule-runtime"` to `<script>` tag
5. Add `<script id="capsule-manifest" type="application/json">` with `generator.kind: "llm"`, `version: "Microsoft Copilot"`, `type: "domain.journey_map"`, source info, plus the integrity-hash placeholder
6. Add `<script id="capsule-data" type="application/json">` with the persona × stage × touchpoint matrix as structured JSON (lifting from the rendered HTML back into machine-readable form)

Result: validates 25/25 strict, becomes the first Microsoft-Copilot-authored Capsule in the public corpus and the first independent-author (not the maintainer) Capsule beyond the Mintel compiler producer in F20. Pending the colleague's permission to publish.

**Methodological note.** F30 is the first finding logged the day after F29 (which itself was logged same-day as F28) — the cross-project memory pattern named in F28 is also operating cross-conversation now: a conversation about landing-page copy produced an empirical observation that became an F-finding within the same conversation. The upstream-feedback-discipline framing extends to the maintainer's own conversational practice, not just the producer projects.

**Related findings:**
- [F19](#f19-design-tool-integration-experiment--claude-design-with-capsule_coremd-attached) — Claude Design reached conformance from Core alone (Core attached → producer succeeds)
- [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates) — ChatGPT producer-population reads Core supplementary guidance reliably
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec--empirical-pressure-for-discoverable-onboarding) — Producers reach for Capsule-shape independently when given the idiom but not the spec; F30 is the fourth-producer-family confirming data point for F28's "convergent envelope shape" claim
- [`htmlcapsule.org` v14.16.0](https://htmlcapsule.org/) — the landing-page "Multi-system, by design" section that articulated the lateral-portability thesis that F30 validates empirically

### F31: Bundle emerges as sibling format — empirical pressure from a heavy-data investigation produces the project's first sibling spec; producer / format / host pattern named explicitly

**Date:** 2026-05-24

**Source.** A maintainer-led building leak investigation (Loft 495, Vancouver — a real strata building with water intrusion across floors L5–L8) required tooling Capsule was not equipped to handle: four georeferenced floor plan rasters at ~6 MB each (~9000×12500 px), an 83-feature GeoJSON layer with drains / slopes / unit boundaries / leak locations, a 237,473-point LiDAR cloud, and two viewer HTMLs (2D Leaflet map + 3D Three.js point-cloud renderer) depending on CDN-hosted libraries. Total artifact: 60+ MB with multi-viewer needs, heavy binary assets, and runtime dependencies on external libraries. The maintainer spun up a local side project called `leak` to do the work without bloating the destination host (Stratabot), and exported the result as a single portable archive with a `manifest.json` at the root, SHA-256 hashes per file, and a UUID minted at seal time.

That export format was provisionally called a "Bundle" and got documented as a v0.1.0 spec inside the local `leak` project. It was not initially intended as a peer-of-Capsule format; it was a one-off solution for one investigation. Over the course of a design conversation with the maintainer (preserved in the parent chat thread, 2026-05-24), the conversation surfaced that Bundle's structural shape was load-bearing for more than just the leak investigation, and the decision was made to incorporate Bundle directly into the htmlcapsule project as a **sibling format**.

**Three layered findings:**

**(1) Capsule has a real ceiling, and Bundle is what's above it.** The empirical pressure that produced Bundle is the same pressure that produced Capsule's parked appendix candidates over time, except this one couldn't be absorbed by tightening or extending Capsule. The artifact was simply too heavy and too multi-viewer to fit the sealed-singleton commitment. Forcing it into Capsule would have meant either (a) breaking Rule 2 to allow external asset loads (which would have collapsed the entire sealed-boundary thesis just landed in v0.3.8 §1.5), or (b) accepting a ~100 MB single HTML file that would defeat the format's casual-portability promise (no email attachment, no iOS QuickLook, no offline-decades-later guarantee). Neither was acceptable. Bundle takes the honest third path: acknowledge Capsule's ceiling, name what's above it, give it a different format that shares the discipline.

The shared discipline is the three principles Bundle borrows from Capsule's opening: **identity** (UUID at seal time), **integrity** (SHA-256 hashes), and **provenance** (manifest records authorship). The only thing Bundle trades is the **sealed boundary** — Capsule's Rule 2 says no network; Bundle's §3.2 says external dependencies are allowed but must be declared. Everything else about Bundle inherits from Capsule's design instincts. A reader who understands Capsule will understand Bundle in thirty seconds.

**(2) The producer / format / host pattern is now explicit.** Bundle's emergence forced a project-level pattern into visibility that was previously implicit in Capsule's design but never articulated:

> *The host stays light. The producer can be heavy and domain-specific. The portable format is the contract that lets them compose.*

The pattern instantiates twice now:

- **Capsule family**: Mintel (producer) → Capsule (format) → MinDev (host)
- **Bundle family**: leak (producer) → Bundle (format) → Stratabot (host)

Same shape, both times. Future producers can join either family without the format changing. Future hosts can join either family without the format changing. Stratabot specifically may end up multi-format (serving both Capsules and Bundles, dispatching by file type) — that's a desirable property because a domain-aware host should serve whatever sealed/manifested artifact is the right shape for the deliverable, not require producers to choose a host based on format.

Without naming the pattern, Bundle's emergence would have looked like an ad-hoc deviation from Capsule. With the pattern named, Bundle's emergence looks like the project's discipline applied at the next scale up — the same factoring the project uses internally (producer / format / host), now visible as a load-bearing principle of how the family is structured.

**(3) The project's scope expands without renaming.** The project is called "html capsule." It now hosts specs for two formats: Capsule (the original) and Bundle (the sibling). The choice is to keep the project name and let the family relationship be described, not branded. htmlcapsule.org becomes the home for both specs. The Capsule spec remains primary in positioning; the Bundle spec is the acknowledged sibling. Naming a separate umbrella ("[X] artifacts family") was considered and deferred — the cost of adding a new brand outweighs the clarity gain, and "Capsule + Bundle within the htmlcapsule project" is legible enough.

This makes the project the second known case (after the four-producer family for Capsule) where the discipline produces sibling/extension structure rather than format inflation. It's healthier than the alternative — a single format stretched to handle every use case ends up handling none of them well.

**Implication for the spec(s).** No Capsule rule changes. Bundle ships as `spec/BUNDLE_SPEC.md` at v0.1.0. The project version bumps to v0.4.0 to mark the introduction of a sibling spec (the change is significant enough to warrant a minor bump even though no individual existing spec changed). The Capsule spec stays at v0.3.8. CITATION.cff bumps to v0.4.0 because that field tracks project-level versioning. The README state line now reports both spec versions.

**Implication for the producer corpus.** Bundle currently has one producer (`leak`) and one host (Stratabot, possibly multi-format). The trajectory is the same as Capsule's first phase: one producer, one host, spec at v0.1.x, and public tooling beginning from a small reference fixture rather than from the private real-world artifact. As more domain investigations or specialized projects encounter similar heavy-artifact pressure, more Bundle producers will surface. The maintainer's explicit prediction: "there will be more situations like leak. tons more, across all sorts of domains." Each one will either confirm or pressure-test Bundle v0.1.0.

**Postscript (2026-05-26).** The first public Bundle tooling pass landed after this finding: `spec/bundle.schema.json`, `compiler/validate_bundle.py`, and `spec/examples/minimal_bundle/`. This does not change the empirical status of Bundle — the only real producer remains `leak`, and the only real host remains Stratabot — but it gives future producers a concrete starting point. The pass also tightens cross-format lineage: a Capsule derived from a Bundle should record the source Bundle in `derived_from[]` with `type: "bundle"`, because Capsule `parents[]` is strict Capsule-to-Capsule lineage.

**Implication for the project's research narrative.** The empirical-pressure-driven evolution principle (codified in the project's introduction) is now operating at two levels: rule-level within a spec (Capsule v0.1 → v0.3.8 evolution) and format-level within the project (Capsule alone → Capsule + Bundle). The mechanism is the same — real producer pressure surfaces what needs to exist; the spec catches up and writes it down. F31 is the first time the format-level evolution has happened.

**Methodological note.** F31 was logged during the same conversation in which the Bundle-as-sibling decision was made. The conversation itself produced the artifact (decision + spec promotion + research record + cross-document updates) — the upstream-feedback-discipline pattern named in F28 continues to operate cross-conversation, including in conversations that span project boundaries (the conversation started in `/leak/` and concluded with changes to the public `/htmlcapsule/` project).

**Related findings:**
- [F8](#f8-the-atomic-unit-framing-explains-everything-weve-built) — the atomic-unit framing; Bundle is an atomic unit at a different scale than Capsule, same discipline
- [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) — Mintel as Capsule's first independent producer; leak is the parallel for Bundle
- [F21](#f21-independent-convergence-on-the-host-contract-pattern-mindev--htmlbin) — host-contract convergence for Capsules; Stratabot may converge with the same shape for Bundles
- [F24](#f24-host-vs-registry--the-missing-commitment-layer) — host vs registry distinction; carries forward into the Bundle family
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec--empirical-pressure-for-discoverable-onboarding) — upstream feedback discipline; F31 extends it to cross-project format promotion
- [`spec/BUNDLE_SPEC.md`](spec/BUNDLE_SPEC.md) — the formal Bundle spec promoted in this finding
- [`leak/project/BUNDLE_SPEC.md`](https://github.com/) — the originating Bundle spec from the side project (not publicly available; included for trajectory reference)

### F32: Codex Sites validates the hosted-runtime layer while strengthening the case for portable custody

**Date:** 2026-06-03

**Source.** OpenAI's Codex Sites documentation and ChatGPT Sites Terms were reviewed after the maintainer surfaced the feature as relevant to both HTML Capsule and HTML Vault. Sites is a Codex plugin for creating, saving, deploying, and inspecting hosted websites, web apps, and games from inside Codex. OpenAI describes every Sites deployment URL as a production deployment and recommends saving a version for review before deploying. The docs position Sites as preview availability for ChatGPT Business and Enterprise workspaces, with Enterprise enablement controlled through RBAC. The pricing page says Sites is free while in preview, with pricing still pending. The Terms make the user's ownership of website content explicit, but also grant OpenAI and hosting providers the license needed to host, store, reproduce, modify, display, and distribute the site content as needed to make the site available. The Terms also put responsibility for site content, end users, legal compliance, privacy, and functionality on the creator, with restrictions around security threats, malware, children under 13 / applicable digital-consent age, money / crypto / investment transactions, HIPAA PHI, and PCI-regulated payment-card data.

Primary references:

- <https://developers.openai.com/codex/sites>
- <https://developers.openai.com/codex/pricing>
- <https://developers.openai.com/showcase/sites>
- <https://openai.com/policies/chatgpt-sites-terms/>

**Finding — Sites occupies the hosted-runtime layer, not the sealed-artifact layer.** Codex Sites is not a Capsule replacement. It solves a different problem:

```text
Codex Sites publishes things.
HTML Capsule preserves things.
HTML Vault governs things.
```

Sites is an AI-native deployment surface: generated code becomes an OpenAI-hosted site/app. Capsule is a portable artifact format: generated or compiled HTML becomes a self-contained, provenance-bearing object that can survive outside the platform that produced or hosted it. Vault is the custody layer: artifacts arrive, get quarantined, inspected, scanned, validated, hashed, related, signed, exported, archived, and optionally published.

The useful layer map is now:

| Layer | Role | Examples |
|---|---|---|
| Live working canvas | Iterative creation and review before sealing | ChatGPT Canvas, Claude Artifacts, html-docs, Workplane |
| Portable artifact | Self-contained or manifested object that preserves the work | Capsule, Bundle |
| Custody system | Local-first review, quarantine, library, provenance, signing, publishing dispatch | HTML Vault |
| Hosted runtime / publishing | Public or workspace-hosted live site/app | Codex Sites, htmlbin, MinDev, Vercel, Cloudflare, GitHub Pages |
| Discovery | LLM / web index of where artifacts live | `llms.txt`, registry pages, site maps |

The distinction matters because Sites produces useful live deployments, but a live deployment is not a durable record. A deployed site can change, disappear, depend on account state, depend on platform terms, collect end-user data, or carry operational responsibilities that the file alone does not express. Capsule's role is to preserve the reviewed artifact state; Vault's role is to decide whether and how it should move from local custody to a hosted surface.

**Implication for Capsule.** No Capsule rule changes. If anything, Sites reinforces Capsule's sealed-boundary thesis:

- Do not relax Capsule's no-network rule to accommodate hosted app assumptions.
- Do not treat deployment as preservation.
- Do not make Capsule a hosting protocol.
- Do record hosted deployment provenance when relevant, either in `derived_from[]`, producer metadata, or future deployment/provenance sidecars once real consumers need that field.

A Capsule can be the sealed record of a Sites-bound artifact at review time: "these are the bytes/content we approved before deployment" or "this is the offline record of what the deployment represented." If a Sites project is too project-shaped for one HTML file, Bundle is the right preservation target: source, build output, assets, storage exports, deployment metadata, and hashes in one manifest-described package.

**Implication for Vault.** Sites makes Vault more important, not less. If AI tools can turn prompts into production deployments quickly, users need a local system of record for the generated web artifacts:

```text
Codex / ChatGPT / Claude / local agent
        ↓
generated HTML / app / report / dashboard / site candidate
        ↓
HTML Vault quarantine
        ↓
scan / validate / hash / preview / annotate / sign
        ↓
promote to Capsule or Bundle
        ↓
export / publish / archive / send to Codex Sites / send elsewhere
```

The key positioning line:

> Publish anywhere. Preserve locally. Verify independently.

Vault should eventually treat Codex Sites as one publishing endpoint among many, not as the canonical home. Useful future Vault features suggested by this finding:

- import a generated site candidate into quarantine before deployment
- save a sealed Capsule snapshot of the reviewed content
- preserve a Bundle snapshot of a full Sites-style project, including source/build output and storage export metadata
- record deployment URLs, deployment timestamps, access scope, and hosting provider in local provenance
- compare a later downloaded/snapshotted deployment against the sealed local record
- warn when a deployment candidate appears to collect sensitive or regulated data

**Implication for Bundle.** Bundle gets a clearer preservation role for hosted projects. A worker-compatible app with D1/R2 state is not naturally a Capsule unless its meaningful artifact is one offline HTML file. A preserved Sites project may need:

- source tree or build output
- `manifest.json`
- file hashes
- environment-variable names without secret values
- D1 schema and export snapshot when available
- R2 object inventory and hashes when available
- declared external services
- deployment metadata
- one or more entry viewers

That shape is Bundle territory. The same rule from F31 holds: don't stretch Capsule above its ceiling; use the sibling format honestly.

**Positioning update.** Codex Sites validates the broader premise that AI-generated HTML/web artifacts are becoming a normal output class. The more platforms make deployment easy, the more valuable the independent portable object and custody layers become. The project should not frame Sites defensively. Sites is evidence that the ecosystem is moving toward the problem Capsule and Vault already name.

**Related findings:**
- [F21](#f21-independent-convergence-on-the-host-contract-pattern-mindev--htmlbin) — independent convergence on lightweight HTML hosting; Codex Sites is the platform-integrated hosted-runtime version of the same broad pressure
- [F22](#f22-independent-convergence-on-the-live-editing-layer-html-docs--workplane) — live editing layer; Sites sits downstream as a deployment surface
- [F24](#f24-host-vs-registry--the-missing-commitment-layer) — host vs registry distinction; Sites is host/runtime, not registry/commitment layer
- [F31](#f31-bundle-emerges-as-sibling-format--empirical-pressure-from-a-heavy-data-investigation-produces-the-projects-first-sibling-spec-producer--format--host-pattern-named-explicitly) — producer / format / host pattern; Sites adds another hosted target while preserving the same producer/format/host separation

### F33: First data-backed compiler producer seals resolved data — sealed_sources makes the output-is-also-the-source claim literal

**Date:** 2026-07-06

**Source.** The compositor project (sibling repo; a deterministic compiler producing `domain.compositor` capsules from a document-composition editor — the first external compiler producer whose CI validates every sealed example against this project's strict reference validator). An agent-run deep review of compositor (Bridge: `reviews/compositor-deep-review-2026-07`) caught its marketing claim "the output is also the source" being **false for data layers**: capsules sealed dataset *references* (`source.dataset` keys), and reopening only worked because the producing Studio happened to bundle the same fixtures the references pointed at. Uploaded GeoJSON lived in session state and silently died with it. The producer's P1 response shipped the same day this finding was logged: a `sealed_sources` block in the capsule data block — resolved GeoJSON per sourceKey, inline-sourced layers excluded, covered by the integrity hash. The acceptance chain was proven against production: document referencing a live workspace → resolved over the network at authoring time → sealed → reopened offline with an **empty fixture map**, zero warnings, zero network. Their unit tests prove the block is load-bearing in both directions: empty-fixture reopen is clean *and* stripping the block degrades to warnings.

**Finding — reference-vs-data sealing is a distinct failure class for data-backed capsules, invisible to the rendering-level offline guarantee.** Spec §12 has always guaranteed offline *rendering*, and compositor's capsules passed it throughout — the rendered HTML displayed fine with no network. What the guarantee didn't cover: a capsule whose content model references keyed external sources can render offline while silently depending on ambient producer-side fixtures for *re-resolution* — reopening the capsule as a working object. The dependency is real but the file doesn't express it, which is exactly the kind of hidden coupling the format exists to eliminate.

Two design decisions in the producer's fix are worth recording as format doctrine, not just implementation detail:

1. **Seal beside, don't rewrite.** The obvious fix — rewriting each `source.dataset` reference into an inline payload at seal time — was explicitly rejected because it would have rewritten sourceKeys and destroyed the provenance of where each dataset came from. Instead the resolved payloads sit *beside* the document under the document's own reference keys. The producer's phrasing is the cleanest articulation of the principle this project has seen: *"the document stays a clean recipe; the capsule stays the complete meal."*
2. **Sealed data belongs under the hash.** `sealed_sources` lives in the data block, so `content_hash` covers it under every `hash_scope` — stripping or substituting sealed payloads breaks verification. Sealing data outside the hash boundary would have made the offline-resolution claim unverifiable.

**Implication for the spec.** Spec v0.3.10 adds `sealed_sources` as the third recommended data-block convention in §4.1.2 (after `sources[]` and `embedded_media`), composing with `sources[]`: citation metadata describes *what and where*, sealed sources carry *the bytes*. §12 now states the resolution guarantee explicitly: rendering offline is the floor; data-backed capsules SHOULD re-resolve offline. The validator checks shape when the field is present (object, non-empty keys, non-null payloads) at warn level. **Not Core, yet:** this is single-producer evidence, and Core's twelve rules stay minimal. But it is the named Core-promotion candidate for v0.4 — if a second independent data-backed producer converges on the shape, "a data-backed capsule seals what it resolved" graduates to a rule. `domain.compositor` is now registered in DOMAIN_CAPSULES.md with the producer's schema pointer.

**Methodological note.** This is the fastest review-to-spec loop the project has run: an external producer review (logged to shared memory) surfaced a format-level gap, the producer shipped the fix, and the spec absorbed the pattern — all within one week, coordinated across sessions through the shared memory layer rather than through the maintainer's attention. The empirical-pressure discipline (F28, F31) now operates across a fleet of producer projects, with the spec deliberately downstream of the corpus.

**Related findings:**
- [F31](#f31-bundle-emerges-as-sibling-format--empirical-pressure-from-a-heavy-data-investigation-produces-the-projects-first-sibling-spec-producer--format--host-pattern-named-explicitly) — producer / format / host pattern; compositor is the pattern's first *data-backed compiler* instantiation, and the first whose CI mechanically enforces the format contract (see F35)
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec--empirical-pressure-for-discoverable-onboarding) — upstream feedback discipline; F33 extends it to producer-review-driven spec evolution
- [F34](#f34-hash_scope-datamanifest-becomes-a-production-default--the-integrity-hash-covers-truth-not-projection-and-must-say-so) — the same producer's integrity posture; sealed_sources only works as a trust claim because the sealed payloads sit under the hash

### F34: hash_scope data+manifest becomes a production default — the integrity hash covers truth, not projection, and must say so

**Date:** 2026-07-06

**Source.** The same producer (compositor). Spec v0.3.2 (§5.2.1) introduced `hash_scope: "data+manifest"` with a narrow, defensive rationale: browsers normalize HTML during DOM serialization, so capsules declaring `download_capsule` should hash only the JSON blocks or the downloaded copy won't verify. Compositor adopted `data+manifest` not as a workaround but as its **only mode and a deliberate architecture**: its invariant is "JSON is truth, HTML is projection" — the reopen path never reads the HTML surface, which is regenerable from the data block by construction. Tamper and hostile-JSON tests exercise the posture. This is the first producer to treat HTML-surface-excluded-from-integrity as a design commitment rather than a compatibility concession.

**Finding — the scope choice is sound, but a scoped hash displayed without its scope is a trust-communication failure.** The producer's own deep review caught it: the capsule's About panel displayed "Integrity: sha256:…" in a way that implied the hash covered everything, while `data+manifest` deliberately excludes the HTML surface. Two capsules with identical data blocks and different rendered HTML verify identically under that scope. That property is a *feature* — re-rendering a projection doesn't break custody, browser re-saves don't invalidate the artifact — but only when every party knows what the hash covers. A recipient who reads a bare hash as whole-file integrity has been misinformed by omission, and the misinformation compounds downstream: custody systems (htmlvault) attest over `content_hash`, and registries index by it (§8.4 makes it the verifiable identity). An attestation over a `data+manifest` hash certifies truth, not surface — the custody chain needs to say so.

**Implication for the spec.** §8.4 now carries display guidance: any surface showing `content_hash` — in-capsule About panels, hosts, registries, custody tools — SHOULD show `hash_scope` beside it (`sha256:… · data+manifest`). No validator check; this is display-layer guidance the machine can't reliably verify inside arbitrary chrome. No change to the scope vocabulary — the empirical lesson is that v0.3.2's scope design was *more* right than its own rationale claimed (it enables the one-renderer / regenerable-projection architecture), and the missing piece was legibility, not mechanism.

**Related findings:**
- [F33](#f33-first-data-backed-compiler-producer-seals-resolved-data--sealed_sources-makes-the-output-is-also-the-source-claim-literal) — same producer; sealed_sources is only a trust claim because it sits inside the hashed data block
- [F24](#f24-host-vs-registry--the-missing-commitment-layer) — the commitment layer indexes by content hash; scope legibility is what makes those commitments mean what recipients think they mean
- [F32](#f32-codex-sites-validates-the-hosted-runtime-layer-while-strengthening-the-case-for-portable-custody) — custody layer positioning; "verify independently" requires knowing what the verification covers

### F35: The reference validator becomes load-bearing cross-repo infrastructure — producer CI needs a version identity to pin against

**Date:** 2026-07-06

**Source.** Compositor's CI ("non-negotiable #2" in its workflow) checks out `bigfancygarden/htmlcapsule` and runs `compiler/validate.py --strict` over every sealed example as a merge gate, resolving the validator via an `HTMLCAPSULE_VALIDATOR` env var with sibling-checkout and dev-machine fallbacks. The checkout floats on `main` — no ref pin, no version assertion.

**Finding — the validator crossed from reference implementation to consumed infrastructure, and nothing marked the crossing.** Until now the validator's only consumers were this repo's own examples and generated site pages; version identity was irrelevant because validator and spec moved in the same commit. A cross-repo CI consumer changes that. Two silent-drift failure modes appear, one per direction: (a) the spec tightens → producer CI breaks with no producer-side change — *acceptable and intended* (that's what a reference gate is for), but only diagnosable if the failing report says which validator version enforced what; (b) the producer pins an old ref → CI passes forever against a stale spec while the producer claims current conformance — a conformance claim with no version attached is unfalsifiable. Both modes were live risks the day compositor's CI landed: the validator had no version constant, no `--version` flag, and reports didn't state what they enforced. Its docstring still said "v0.1.0" from the project's first week.

**Implication for the reference implementation.** `VALIDATOR_VERSION` now exists and tracks the full-spec version the file enforces (starting at `0.3.10`), `--version` prints it, and every report header states it. §14 documents the consumption contract: pin a ref and record the version, or float on `main` deliberately and read the version off the failing report when the spec moves. Publishing the validator as an installable package (PyPI or similar) is deferred until a second CI consumer materializes — same single-producer discipline as F33's Core-promotion bar. The deeper pattern worth naming: in the producer / format / host split (F31), the format was always described as "the contract that binds them" — this is the first time the contract is *mechanically enforced* on the producer side rather than socially observed, which is exactly the graduation the project hoped the reference validator would earn.

**Related findings:**
- [F31](#f31-bundle-emerges-as-sibling-format--empirical-pressure-from-a-heavy-data-investigation-produces-the-projects-first-sibling-spec-producer--format--host-pattern-named-explicitly) — producer / format / host; the format-as-contract now has mechanical teeth
- [F33](#f33-first-data-backed-compiler-producer-seals-resolved-data--sealed_sources-makes-the-output-is-also-the-source-claim-literal) — the producer whose CI created the pinning question
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec--empirical-pressure-for-discoverable-onboarding) — discoverable onboarding; a versioned, CI-consumable validator is onboarding for *compilers* the way CAPSULE_CORE.md is onboarding for LLMs

### F36: Custody makes version incoherence visible — spec_version declares the normative line, the validator verifies at a doc revision, and the record needs both

**Date:** 2026-07-07

**Source.** The first production custody run (htmlvault, TOM-04 flagship capsule). The custody record faithfully stored what the producer declared — `spec_version: "0.3.0"` — directly beside the gate result "strict-valid, validator 0.3.10," and the custody session flagged the pairing as incoherent: "until the spec's version story is coherent, provenance chains will carry misleading version claims."

**Finding — the wire was right and the vocabulary was missing.** Nothing in the flagged record was wrong: manifests declare `0.3.0` because that is the Core (normative) version, the validator's known-version set caps at `0.3.0` *by design*, and the full-spec document's `v0.3.x` patch stream (now v0.3.11) versions documentation, conventions, test vectors, and validator behavior *within* that normative line. But no document said so. The two version streams — the rule line a capsule declares and the doc revision a validator enforces — had been operating correctly and namelessly since v0.3.1, and the first outside consumer to store both side by side reasonably read them as a contradiction. A correct system that looks incoherent to its first serious consumer has a documentation bug with the trust impact of a real one: custody chains are exactly where ambiguity compounds.

**Implication for the spec.** §8.1 now names the two-track version story: `spec_version` declares the normative line (Core); producers MUST NOT declare full-spec doc revisions and validators MUST reject them as unknown; a conformance statement is the **pair** (declared line + verifying validator version); custody and provenance records SHOULD store the **triple** (declared, verified-by, when); display surfaces SHOULD render `spec 0.3.0 · validated 0.3.11` — the same legibility rule §8.4 applies to hashes (F34), applied to versions. The validator now states the pair in every report's `spec_version` check. The general pattern, now observed twice in one week: **claims without their verification context read as more than they are** — hash without scope (F34), version without validator (F36). Custody surfaces both because custody is where claims get stored next to their verification.

**Related findings:**
- [F34](#f34-hash_scope-datamanifest-becomes-a-production-default--the-integrity-hash-covers-truth-not-projection-and-must-say-so) — the same legibility failure class, for hashes; §8.4 and §8.1 are now the two instances of one rule
- [F35](#f35-the-reference-validator-becomes-load-bearing-cross-repo-infrastructure--producer-ci-needs-a-version-identity-to-pin-against) — the validator version identity that makes the pair statable at all

### F37: A one-ULP float parse files a false tampered verdict — cross-language canonicalization needs a float-bearing test vector and correctly-rounded parsing

**Date:** 2026-07-07

**Source.** htmlvault's Rust custody verifier, during flagship pre-flight. serde_json's default `f64` fast-path parsed the Web-Mercator ordinate `7842318.5018136855` one ULP away from the correctly-rounded double. The canonical re-serialization therefore differed from the reference implementation's by one digit, the recomputed hash diverged, and the vault filed a false "tampered" (INT001 High) against a capsule the reference validator passes 31/31. Fixed on their side with serde_json's `float_roundtrip` feature; their Swift verifier was checked and already correctly rounded.

**Finding — the §9.1.1 canonical form was underspecified in exactly one dimension: numbers.** The hash recipe re-serializes parsed JSON, so canonical bytes depend on the implementation's number formatting and parsing. Test Vector A (v0.3.1) contains no floats, so a verifier could pass it while mis-parsing every float in a real geospatial capsule — the class of capsule the format's heaviest producers emit. Three sub-hazards, all real: correctly-rounded parsing (the empirical serde_json case); exponent formatting style (Python emits `1e+22` and `1.5e-05`; Ryu-style writers emit `1e22` and `1.5e-5`); and integer-valued float preservation (Python keeps `55.0`; ECMAScript/RFC 8785 JCS prints `55`). That last one matters doctrinally: **JCS is not this spec's canonical form**, and pretending otherwise would silently invalidate every existing hash.

**A second lesson from the same event, about test vectors themselves.** The custody session proposed a vector with an expected hash computed against "a minimal manifest" — unspecified which. Reproducing it against Test Vector A's manifest gives a *different* hash. An under-specified test vector is worse than none: it manufactures false failures in every implementation that guesses the missing part differently. Normative vectors must be self-contained — every input byte printed — and independently re-derived by the reference implementation before publication. (Both spec vectors were re-derived from the reference implementation before this revision shipped; Vector A reproduces bit-identically.)

**Implication for the spec.** §9.1.1 gains Test Vector B: Test Vector A's manifest verbatim plus a float-battery data block — the actual biting ordinate, the `0.30000000000000004` shortest-repr shibboleth, both exponent forms, an integer-valued float, a plain integer, and ordinary coordinates — with the reference-derived hash `sha256:47c0aaf0…`. Two new normative requirements: implementations MUST parse numbers correctly rounded, and MUST reproduce the reference (Python 3 `repr`) number formatting. Non-Python verifiers SHOULD pin the vector in a regression test, because this failure mode is silent until it defames a real artifact.

**Related findings:**
- [F35](#f35-the-reference-validator-becomes-load-bearing-cross-repo-infrastructure--producer-ci-needs-a-version-identity-to-pin-against) — second consequence of independent reimplementations of the format's mechanics; the validator got a version, the hash recipe now gets a conformance instrument
- [F33](#f33-first-data-backed-compiler-producer-seals-resolved-data--sealed_sources-makes-the-output-is-also-the-source-claim-literal) — sealed_sources put bulk float data under the hash, which is what raised the stakes on float canonicalization

### F38: Mintel's capsule push flow goes live — the original production compiler re-reviewed against the modern spec: extension namespace in production, and the first unenforced registry MUST

**Date:** 2026-07-07

**Source.** Mintel's claim-group capsule push flow went live (mintel #117, Saskatchewan jurisdiction support): `build_claim_group_capsule.py` / `build_exploration_map_capsule.py` compile PostGIS claim snapshots into `domain.exploration_map` capsules and push them to mindev. Mintel is the format's *original* production compiler ([F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) documented its first publicly-fetchable capsule); what's new is the continuous push path and the jurisdiction expansion — and this is the first full code-level review of its builders against the modern spec (v0.3.11 era, post-sealed_sources, post-hash_scope-doctrine). No emitted artifact was present locally to validate; the builders' manifest, hash, and data assembly were reviewed in full.

**Finding — strong convergence, one shape difference, one real gap, and a milestone for the extension mechanism.**

- **Convergence.** Manifest declares the normative line correctly (`spec_version: "0.3.0"`); `generator.kind: "compiler"`; `hash_scope: "data+manifest"` (the third producer to default to it — F34's posture is now unanimous across the compiler corpus); the §9.1.1 hash recipe is independently reimplemented in Python (placeholder protocol, canonical form) and matches the reference by construction.
- **Shape.** Mintel is an **inline producer**: claims GeoJSON is pre-projected to UTM and embedded directly in the data block as the content itself. `sealed_sources` therefore correctly does not apply — the convention is for content models that *reference* sources by key, and mintel's content *is* the data. Consequence for the Core-promotion bar set in F33: **still unmet.** The newest production flow didn't need the convention, which is itself evidence about the convention's scope: it belongs to reference-shaped content models (editors, composers), not snapshot exporters.
- **Extension milestone.** Mintel moved vendor lineage into a manifest-level `x-mintel` block (project/version ids) after discovering `source` has `additionalProperties: false` — the first observed production use of the `^x-` extension namespace, used exactly as designed: vendor context that travels without polluting the envelope.
- **The gap.** Mintel's capsules declare `domain.exploration_map` but the builders emit **no `ai_usage_guidance` block** — a MUST in DOMAIN_CAPSULES.md, written specifically for this domain's risk surface ("summarize the map, but do not estimate resources or imply economic viability"). The reference validator never checked it, so mintel passes strict while violating the registry requirement. An unenforced MUST consumed by real producers is a spec bug wearing a producer-bug costume.
- **A third consumption path for the validator.** Mintel's docs instruct running the validator from a `/tmp/capsule` checkout — even less pinned than compositor's floating-`main` CI. F35's pinning guidance applies; feedback filed.
- **Display gap, same as F34's.** The capsule footer renders `spec v0.3.0 · … · hash sha256:…` — hash without scope, and (until §8.1) version without validator. Both display rules now exist to point at.

**Implication for the spec and validator.** The validator now warns when a `domain.*` capsule's data block lacks `ai_usage_guidance` (or lacks any of its three required keys). Warn-level is deliberate: the base validator checks the envelope, and domain-registry conformance sits a layer above — but under `--strict` (every producer gate observed so far) a warning fails, which is the enforcement the registry MUST always implied. Blast radius checked before shipping: every other local domain capsule (compositor's seven, the spec's own two worked examples, htmlvault's demo) already carries the block; mintel is the one real gap, and the exact block to add is in the Bridge feedback.

**Related findings:**
- [F33](#f33-first-data-backed-compiler-producer-seals-resolved-data--sealed_sources-makes-the-output-is-also-the-source-claim-literal) — the Core-promotion bar sealed_sources still hasn't met, now with sharper scope (reference-shaped content models only)
- [F35](#f35-the-reference-validator-becomes-load-bearing-cross-repo-infrastructure--producer-ci-needs-a-version-identity-to-pin-against) — third unpinned consumption path
- [F20](#f20-first-publicly-fetchable-mintel-production-capsule-validates-spec-at-scale) — mintel's original production capsule, including the 13.7 MB size datum; exploration_map remains the format's heaviest production domain

### F39: The annotation layer is already a capsule — markup-as-language needs digest-pinned parents and anchor-to-truth, not a new envelope

**Date:** 2026-07-07

**Source.** The fleet's operator-ratified markup-as-language thesis (Bridge: `strategy/markup-review-thesis`): user annotations over documents and maps — circle, highlight, arrow, strikeout, star, margin note — are a first-class *second document*, serialized expertise often more valuable than the base ("a professor's annotated copy; a geologist's field map"). Prospect is the designated first producer, and the foundation is already empirically proven there (circle-to-scope deixis passed its golden test against the flagship target). The dispatched question for this project: should Capsules anticipate an annotation layer — marks with provenance, separable from the base, survivable through seal? The custody layer independently reviewed its side (Bridge: `htmlvault/continuous-custody-review`) and made two asks of the spec: digest-pin the base reference, and keep the annotation layer a normal sealed capsule.

**Finding — reviewed against the envelope, the annotation layer needs almost nothing new, and the two things it does need were worth adding for their own sake.**

What the envelope already provides: a sealed base with a verifiable identity to pin against (`content_hash`, §8.4); `parents[]` for capsule-to-capsule lineage whose vocabulary already reads "forked from, *continued from, compared with*" — layered-over fits the family; free-form domain data blocks for a `marks[]` schema; `sealed_sources` on data-backed bases, which quietly solves annotation's hardest dependency — marks over map features can address sealed data that can never drift; and the §7 response schema as precedent (structured recipient reaction pinned to records via `_content_hash` — annotations are the spatial, gestural sibling of that pattern). Custody-side composition is already designed: two records, one edge, both independently seal-verified.

What was genuinely missing, now added in v0.3.11 because it strengthens *all* provenance, not just annotation's: **digest pinning on `parents[]`** (`content_hash` per entry — a UUID-only parent claim can be silently re-targeted; a digest-pinned one cannot). Pinned as the parent's manifest `content_hash`, not a whole-file digest: the format speaks its own identity, and under `data+manifest` the pin survives projection regeneration.

What must NOT be done yet: the domain schema. The hard problem is **durable anchoring**, and it has a doctrine before it has a schema: **anchor to truth, not projection.** Marks must address the data block — record ids, `sealed_sources` keys + feature ids, coordinates in the document's declared CRS — never the rendered DOM, because under `hash_scope: "data+manifest"` the HTML projection can be regenerated without changing identity (F34), and every CSS/XPath-style anchor shears off with it. (W3C Web Annotation's selector taxonomy is the precedent to mine when the time comes; its web-page-oriented framing is not.) Anchor vocabulary decisions of that kind get made against a producer's real marks or they get made wrong — Prospect's first sealed annotation capsule is the graduation trigger. `domain.annotation` is queued in DOMAIN_CAPSULES.md with the reviewed shape: a normal sealed capsule, `parents[]` digest-pinned to the base, per-mark author/timestamp (labeled claimed until signing exists), sessions sealing periodically — live marking is the working layer; the capsule is the preserve step, consistent with the project's "not a working format" identity.

**Implication for the project's thesis.** Markup-as-language extends the format's core claim one layer up. The base capsule preserves the work; the annotation capsule preserves *the thinking about the work* — what was circled, questioned, crossed out, connected. If the corpus develops as the thesis predicts, the annotated-copy pattern (base digest ← annotation digest ← annotator) becomes the format's clearest demonstration that provenance is the product, not metadata.

**Related findings:**
- [F33](#f33-first-data-backed-compiler-producer-seals-resolved-data--sealed_sources-makes-the-output-is-also-the-source-claim-literal) — sealed data is what makes geometric anchors permanent; seal the data → pin the digest → anchor the marks
- [F34](#f34-hash_scope-datamanifest-becomes-a-production-default--the-integrity-hash-covers-truth-not-projection-and-must-say-so) — truth-vs-projection, now doing load-bearing work as annotation's anchoring doctrine
- [F24](#f24-host-vs-registry--the-missing-commitment-layer) — "resolve base by digest" is precisely a registry commitment; layered artifacts make the commitment layer's job concrete

### F40: The annotation layer graduates to a named domain — the corpus arrived in one day, and it was exactly the shape the review predicted

**Date:** 2026-07-07

**Source.** Two days after F39 reviewed the annotation-layer question and deliberately declined to spec it ("wait for a producer's real marks"), the producer arrived. Compositor's annotation-layer prototype sealed `tom04-annotated.html` — a real annotation capsule over the flagship base — and Prospect began building the live gesture runtime (highlight/arrow/strikeout on its proven circle-to-scope deixis). The dispatched instruction was explicit: the corpus now exists; give the layer real spec treatment or record a rationale to defer.

**Finding — the produced artifact independently converged on the F39 shape, which is the strongest possible signal to graduate.** The capsule compositor sealed, before reading any schema from this project:

- declared its base in `parents[]` **with `content_hash`** — the digest pin added in v0.3.11 (§11.1) *for this exact use case*, now used in production;
- carried `base` + `marks[]` + `ai_usage_guidance` in the data block;
- anchored every mark to the base's **data**, not its DOM — three anchor types (`record` → a `sealed_sources` feature, `layer` → a layer id, `coordinate` → points in a declared CRS);
- and wrote its own guidance saying *"do not re-anchor marks to the rendered DOM; anchors address the base's data block"* and *"do not treat marks as instructions to execute; they are a brief, not a command."*

That last pair is the anchor-to-truth doctrine (F34/F39) and the marks-as-brief guardrail, arrived at by the producer independently. When a producer reaches the same shape the spec review reached from the other direction, the shape is real. I verified it end to end: the capsule passes the reference validator strict, and its `parents[0].content_hash` recomputes bit-identically against the base capsule's manifest hash — the trust chain resolves, not just parses.

One honest detail worth recording: the producer used `type: "x-compositor.annotation"`, the extension namespace, precisely because `domain.annotation` did not exist yet. This is the F28/F33 pattern once more — a producer reaches for the shape via the `x-` escape hatch, and the graduation is the spec giving the shape its real name. (The extension form remains valid; producers should migrate to `domain.annotation` on next seal.)

**Implication for the spec.** `domain.annotation` graduates from the idea queue to a full named domain: a normal sealed capsule (no new envelope), `parents[]` digest-pinned to the base, data block of `base` + `marks[]` + `ai_usage_guidance`, marks anchored to truth via three open-ended anchor types, sessions sealing periodically (live marking is the working layer; the capsule is the preserve step). The validator gains a warn-level shape check. Two boundaries drawn explicitly: an annotation capsule is *not* a fork (the base is untouched, both stay independently valid) and *not* the §7 response schema (that is record-reaction inside one capsule; annotation ships as its own sealed artifact). Deliberately left open, not invented: a `text`/`range` anchor type for paginated-document bases — that waits for the producer who needs it, W3C Web Annotation's selectors as the reference. The named-domain bar (working example + concrete schema + guardrails + clear boundary) is met; single-producer is fine for a *domain* (unlike a Core rule — that distinction is the same one drawn for `domain.exploration_map`).

**Methodological note.** F33 was the fastest review-to-spec loop the project had run (one week). F39→F40 is faster: the review that declined to spec speculatively named the exact fields the producer would need (digest pinning, anchor-to-truth), those fields shipped in v0.3.11, and the producer built against them within two days — so when the corpus arrived, graduation was almost mechanical. The discipline of *reviewing without speccing* is what made the eventual spec cheap and correct: the hard thinking (anchor to truth, pin the base) was done before the schema, so the schema is just naming a proven shape. Waiting was not delay; it was the work.

**Related findings:**
- [F39](#f39-the-annotation-layer-is-already-a-capsule--markup-as-language-needs-digest-pinned-parents-and-anchor-to-truth-not-a-new-envelope) — the review this finding closes; predicted the shape, added the prerequisite (digest pinning), declined to spec speculatively
- [F34](#f34-hash_scope-datamanifest-becomes-a-production-default--the-integrity-hash-covers-truth-not-projection-and-must-say-so) — truth-vs-projection is the load-bearing doctrine of the anchor rule
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec--empirical-pressure-for-discoverable-onboarding) — producer reached the shape via the `x-` namespace before the spec named it; graduation is the naming
- [F33](#f33-first-data-backed-compiler-producer-seals-resolved-data--sealed_sources-makes-the-output-is-also-the-source-claim-literal) — sealed_sources is what makes `record` anchors permanent; annotation is downstream of sealed data

### F41: The dominant AI-artifact producer ships the substrate without the commitment layer — Claude artifacts are envelope-compatible and provenance-free

**Date:** 2026-07-26

**Source.** Direct review of Anthropic's published artifact documentation (`code.claude.com/docs/en/artifacts`, fetched 2026-07-26) plus a targeted search for a format specification, conducted from inside a Claude Code session that was itself publishing artifacts. Claude Code artifacts became generally available across Pro/Max/Team/Enterprise during 2026; they are, by volume, almost certainly the largest population of self-contained AI-generated HTML documents in existence.

**Finding — the physical envelope converged independently; the trust layer did not ship.** The documented constraints are a near-exact match for Capsule's Rule 1 and Rule 2 surface, arrived at from a different direction (sandbox security, not preservation):

| Constraint | Claude artifact | Capsule |
|---|---|---|
| Single self-contained HTML page | required | Rule 1 |
| External requests | CSP-blocked (scripts, styles, fonts, images, `fetch`/XHR/WebSocket) | Rule 2, zero network |
| CSS/JS | inlined | required inline blocks |
| Images | embedded as data URIs | same practice |
| Size ceiling | 16 MiB rendered | 20 MB hard cap (F20) |
| Multi-page | not supported; in-page anchors | single-document model |

What is absent is the entire commitment layer: **no manifest, no `generator` identity, no `source`/provenance block, no integrity hash, no capability declaration inside the file, and no published format specification of any kind.** Anthropic publishes operational documentation — how to create, share, administer, and retain artifacts — but no document defining the artifact *as a file*. Versioning exists, but as host-side database state (each publish becomes a version selectable in the Share control), not as anything the document carries. The one deliberate CSP exception is MCP connector calls, brokered by the host using *the viewer's* account — a live-data affordance that, by construction, makes the page non-portable.

The programmatic retrieval path that does exist is org-admin scoped: a Compliance API with `GET /v1/compliance/code/artifacts/{id}/versions/{id}`. That is a compliance instrument, not a custody instrument — it presumes the organization, not the author, is the party with a retention interest.

**Why this is the strongest available evidence for F24's thesis.** F24 argued that a *host* serves bytes while a *registry* publishes commitments, and that the failure mode is not "wrong identifier" but "no commitment to keep the bytes reachable." That argument was made against a sample of two small hosts (F21) and refined by conversation rather than new evidence. It now has a population-scale instance: the largest artifact host on the planet serves durable-looking URLs with **retention policies configurable by an organization owner**, public sharing that an admin can revoke globally without touching any artifact, and no in-document identity that survives the host. Every property F24 named as a registry commitment is, here, an administrative setting. This is not a criticism of the design — an artifact is documented explicitly as *"a capture of work, not an application"*, and Anthropic makes no preservation claim. It is precisely the point: **the substrate has won exactly as the project's founding hypothesis predicted, and the commitment layer remains unclaimed.**

**Implication for the spec.** No normative change. Two documentation consequences: (a) `spec/HOSTING.md` should record Claude artifacts as the third observed host pattern and the first at population scale, with the honest note that it is a *host* in F24's sense, not a registry, and that its retention and sharing controls are administrative rather than documentary; (b) the project's positioning material should stop describing the ecosystem as moving *toward* the problem Capsule names (the F32 framing) and start describing it as having *arrived at the substrate and stopped* — a materially stronger and more falsifiable claim.

**Related findings:**
- [F24](#f24-host-vs-registry---the-missing-commitment-layer) — host vs. registry; this is that distinction observed at population scale, with every commitment realized as an admin toggle
- [F32](#f32-codex-sites-validates-the-hosted-runtime-layer-while-strengthening-the-case-for-portable-custody) — Codex Sites as hosted-runtime layer; artifacts are the same layer from the other major lab, and the five-layer map holds
- [F21](#f21-independent-convergence-on-the-host-contract-pattern-mindev-htmlbin) — the two-host convergence this extends from n=2 to n=3-with-scale

### F42: Users are writing scrapers to recover their own documents — the export gap is empirically demanded, not hypothesized

**Date:** 2026-07-26

**Source.** Survey of the third-party tooling ecosystem that has formed around artifact export (searched 2026-07-26). Observed instances include `ashwanthkumar/claude-artifacts-downloader` (Chrome extension: extracts the conversation UUID from the URL, reads chat data from browser local storage, emits a ZIP), `elgertam/claude-artifact-downloader`, `Llaves/ClaudeExport` (conversation → HTML), and at least two commercial or freemium offerings. Multiple independent how-to guides exist; the most commonly recommended procedure is manual: *ask the model to print the full HTML in a code block, select all, copy, paste into a text editor, save as `.html`*.

**Finding — the on-ramp gap this project has been reasoning about abstractly has a visible market.** Three things are notable and none of them were predicted by the project's own analysis:

1. **The demand is for byte-level recovery, not for a nicer viewer.** Every tool in the population does the same thing: get the document out, intact, onto local disk. This is the "portable custody" use case stated in the project's own thesis, arrived at by users who have never heard of it.
2. **The implementations are scrapers, and they are fragile by construction.** Reading the host's local storage and parsing conversation JSON means each tool breaks whenever the host changes an internal shape. A population of brittle third-party scrapers is what an ecosystem produces *in the absence of* a format with an export contract — which is precisely the condition Capsule's `download_capsule` capability (§ capabilities, `download_capsule`) exists to remove.
3. **The recommended fallback is copy-paste.** When the most-cited method for preserving a document is "select all, paste into a text editor," the preservation story of the medium has not been written yet.

Read against F25: that finding established that a producer population reliably follows *recipes* when they are written as recipes. This finding establishes the complementary fact on the consumer side — a consumer population reliably *builds its own tooling* when no recipe exists. Both are arguments that the missing artifact is an on-ramp, not a rule.

**Implication for the spec.** None normative — but this is the clearest empirical pressure yet on the acknowledged "biggest unbuilt piece: author-side import tooling" (Status). It also sharpens what that tooling must be: not an importer for capsules (a capsule already carries its own export), but a **converter for the population that exists** — see F43.

**Related findings:**
- [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates) — producers follow recipes; this is consumers building tools in the absence of one
- [F23](#f23-urn-not-url-qr-encoding---empirical-validation-of-a-deliberate-spec-choice) — the printed-QR 403 incident; same class of problem (the artifact outlived its access path) from the opposite direction

### F43: A spec-literate agent published five non-capsules and one valid capsule in the same session — the conversion cost is convention, not capability

**Date:** 2026-07-26

**Source.** Direct self-observation during a working session (mineral-exploration domain, unrelated to this project). The agent — with the full spec available in its working tree — published **five artifacts** through the host's native artifact tool and, later in the same session, **hand-built one Capsule** for the same body of data. The capsule was validated against an *independent third-party implementation* of the format: mindev's TypeScript validator (`keystone/src/capsule-validator.ts`), which enforces the five required blocks, the manifest field set, `generator.kind` membership, the required `source`/`privacy` sub-fields, no-external-references, and the full §9.1.1 placeholder-protocol hash. Result: **VALID**, 148 records, 285 KB, `hash_scope: data+manifest`, content hash verified.

**Finding — the delta between the dominant producer population and conformance is a template.** The five artifacts were structurally ordinary: self-contained, inlined, no external references, several with embedded raster data URIs — Rule 1 and Rule 2 satisfied incidentally, because the host's CSP enforces them. What every one of them lacked was the same five things: the manifest block, the data block, the three required `id` attributes, the declared-capability wiring, and the hash. Adding those took a single working pass, and two of the three validator rejections encountered were *trivial and mechanical* (`<style>` missing `id="capsule-style"`; no `<script id="capsule-runtime">`). Neither was a modelling problem; both were "you forgot the id."

Three observations worth recording:

- **The runtime block forced honesty in the right direction.** Being required to ship a `capsule-runtime` prompted actually implementing the three declared capabilities (`about`, `download_json`, `download_capsule`) rather than declaring them aspirationally — an unplanned confirmation of Rule 7's design intent ([F4](#f4-capability-honesty-is-enforceable): zero over-declaration observed in the corpus).
- **The data block did real work.** Freezing 148 records as `capsule-data` converted a picture-of-data into queryable data — the difference between a screenshot and an artifact — and cost nothing beyond serializing what the session already held.
- **The agent did not do this by default, and would not have.** The host's artifact tool takes an HTML file and publishes it; nothing in that path asks for provenance, and nothing rejects its absence. A producer that *knows the format* still emits non-capsules when the publishing tool doesn't ask. This is the producer-side mirror of F25's validator-heuristic problem: a convention that lives only in a validator does not propagate to producers who are not validated by that tool.

**Implication for the spec.** No rule change. This is direct evidence for a specific piece of tooling: an **artifact→capsule adapter** that takes conformant-substrate HTML (which the population already produces by the million) and adds only the missing envelope — manifest with sane defaults, data block if the producer can supply one, the three ids, a runtime implementing whatever export capabilities are declared, and the hash. The measured gap is small enough that this is a template plus a hash function, and the honest framing for the project is that **the format's adoption problem is now downstream of a single missing utility, not of the rules.**

**Related findings:**
- [F25](#f25-chatgpt-producer-population-reads-core-supplementary-guidance-reliably-aesthetic-adapts-to-content-domain-legacy-artifact-capsule-wording-persists-in-user-side-prompt-templates) — validator-only conventions don't reach unvalidated producers; observed here from the producer side
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec---empirical-pressure-for-discoverable-onboarding) — producers reach for Capsule-shape when given the idiom; this is the case where the idiom was present and the *publishing path* still didn't ask
- [F30](#f30-microsoft-copilot-as-the-fourth-observed-llm-producer-family---convergent-envelope-shape-predictable-five-item-gap-profile-real-world-lateral-portability-handoff) — the predictable five-item gap profile; the gap observed here is the same shape, from a fifth producer path

### F44: `float_roundtrip` is necessary but not sufficient — F37's remediation was scoped to parsing and the formatting half is still open

**Date:** 2026-07-26

**Source.** Independent re-derivation of §9.1.1 Test Vector B against htmlvault's Rust verifier during a code-level review of the custody layer (2026-07-26). serde_json 1.0.145 was built with the `float_roundtrip` feature — the exact remediation recorded in F37 — and the spec's canonical data block was round-tripped through it.

**Finding — the fix addressed the parse hazard and left the format hazard live.** §9.1.1 as revised in v0.3.11 states two distinct MUSTs: implementations MUST parse numbers correctly rounded, **and** MUST reproduce the reference (Python 3 `repr`) number formatting. `float_roundtrip` satisfies only the first. Empirically:

```
python / spec      {…,"small":1.5e-05,…}   → sha256:47c0aaf09948f5f0…   ✅ matches Test Vector B
rust / serde_json  {…,"small":0.000015,…}  → sha256:e44a975765e5ff16…   ❌ diverges
```

The divergence is the exponent-threshold rule, one of the three sub-hazards F37 itself enumerated: Python switches to exponential notation at `1e-05`; serde_json's writer emits positional decimal there. **Any capsule whose data block carries a float below roughly 1e-4 will produce a hash mismatch and, in htmlvault's case, a false `INT001` High "tampered" verdict against a valid artifact.** That is the same defamation failure mode F37 was written to prevent, surviving F37's fix.

Two structural facts make this more than a single-implementation bug:

- **Test Vector B's expected hash appears nowhere in the consuming implementation.** F37 closed with the recommendation that non-Python verifiers SHOULD pin the vector in a regression test. It was not pinned; only the narrower one-ULP ordinate case was. The vector existed and the consumer did not adopt it — which is a distribution failure, not an authoring one.
- **The recipe is now implemented at least four times in three languages** (Python reference, Python producer path, Rust, Swift) plus a partial TypeScript re-implementation, **with no shared conformance harness.** Three different JSON serializers are assumed to agree byte-for-byte on numeric output. Two have now been shown not to. The Swift implementation is untested.

**Implication for the spec.** (a) §9.1.1 should state the number-formatting rule *operationally* rather than by reference to Python's `repr` — the exponent-threshold boundaries (`1e16` upper, `1e-4` lower), the integer-valued-float rule (`55.0` not `55`), and the shortest-round-trip requirement — so an implementer without a Python interpreter can satisfy it from the text alone. (b) The remediation guidance in F37 should be corrected: naming a specific library feature as "the fix" under-specified the problem; the fix is *passing Test Vector B*, and any library advice is downstream of that. (c) The strongest available instrument is a **published conformance suite** — the two vectors plus a float battery, in a language-neutral fixture format, that any implementation can run. This is the same artifact proposed in F45, seen from the integrity side; it is the missing enforcement for a MUST that already exists.

**Related findings:**
- [F37](#f37-a-one-ulp-float-parse-files-a-false-tampered-verdict---cross-language-canonicalization-needs-a-float-bearing-test-vector-and-correctly-rounded-parsing) — the original one-ULP incident and Test Vector B; this finding corrects its remediation record
- [F35](#f35-the-reference-validator-becomes-load-bearing-cross-repo-infrastructure---producer-ci-needs-a-version-identity-to-pin-against) — validator identity for pinning; the same pinning discipline was needed here and wasn't applied

### F45: Every path to a verified capsule routes through Python — the on-ramp terminates at the hash, and one artifact unblocks it

**Date:** 2026-07-26

**Source.** Structured accessibility review of the reference implementation and its documented producer paths (2026-07-26), asking a single question: *can a person who does not use a terminal get from "I have something worth keeping" to "here is a verified capsule"?*

**Finding — the answer is no, and the blocker is a single function.** Three independent paths were traced and all three terminate in the same place:

1. **The LLM path** — the format's genuine achievement ([F1](#f1-the-core-spec-works-as-an-llm-prompt), F19, F25, F30: four model families reach conformance from Core alone) — cannot compute the hash. The project's own prompt pack instructs producers to emit an **all-zero sentinel** by design, and the reference answer is to run `repair_integrity.py`. The path therefore ends at a knowingly-invalid artifact unless a terminal is opened. Open Questions Q4 states this plainly: *"the canonical-JSON content hash is unreproducible by LLMs."*
2. **The verification path** — `python3 compiler/validate.py file.html`. A hosted drag-and-drop validator is sanctioned in the spec and has never been built. Inspection of every generated page on the project site confirms it: the script blocks contain the capsule envelope and small export helpers, and nothing else. **The site is generated capsules describing the tooling; it does not contain the tooling.**
3. **The compiler path** — hand-authoring a JSON source file with `uuid`, `snapshot_id`, ISO-8601 timestamps and template-matched records, then running two or three Python commands. A developer path by construction.

The common blocker is that **§9.1.1 exists only in Python.** That single fact explains the sentinel hash, the absence of any browser tool, the terminal dependency in every documented workflow, and — via F44 — the two non-Python implementations that compute it wrongly.

**The proposal, stated as the smallest sufficient artifact.** A JavaScript/WASM implementation of §9.1.1, written deliberately against Test Vectors A and B rather than assembled from `JSON.stringify` (which cannot satisfy the spec: JCS is explicitly *not* this format's canonical form, and ECMAScript's number formatting differs from the reference at both the integer-valued-float and exponent-threshold boundaries). It is on the order of 150 lines. It unblocks, in dependency order:

- **In-browser hashing**, which converts the LLM path from "ends at a sentinel" to "ends at a verified file."
- **A drop-a-file validator page** — the highest-leverage missing artifact by the project's own reckoning, already sanctioned in §14, and simultaneously the regression harness this repository lacks (there are currently zero tests and no CI, in a repository whose validator is a *merge gate for other repositories' CI*).
- **The conformance suite of F44**, which is the same code with the vectors attached.
- **The artifact→capsule adapter of F43**, which needs exactly one thing beyond a template: a hash it can compute where the author is standing.

**Implication for the spec.** None normative; this is a tooling finding. But it identifies the project's binding constraint precisely, and the constraint is smaller than the surrounding discussion has assumed. The honest summary for the Status section: **the spec is more mature than the tooling, and the tooling is more mature than the on-ramp — and the on-ramp is blocked on one function that exists in one language.**

**Related findings:**
- [F44](#f44-float_roundtrip-is-necessary-but-not-sufficient---f37s-remediation-was-scoped-to-parsing-and-the-formatting-half-is-still-open) — the same missing artifact seen from the cross-implementation integrity side
- [F43](#f43-a-spec-literate-agent-published-five-non-capsules-and-one-valid-capsule-in-the-same-session---the-conversion-cost-is-convention-not-capability) — the adapter this unblocks
- [F42](#f42-users-are-writing-scrapers-to-recover-their-own-documents---the-export-gap-is-empirically-demanded-not-hypothesized) — the population that would use it
- [F28](#f28-producers-reach-for-capsule-shape-independently-when-given-the-idiom-but-not-the-spec---empirical-pressure-for-discoverable-onboarding) — discoverable onboarding; the `/llms.txt` Core-inlining recommendation remains the cheapest complementary fix

### F46: A valid capsule tunnels through the Claude artifact channel — published, wrapped, recovered, verified; data+manifest is a channel-survival property

**Date:** 2026-07-26

**Source.** Direct experiment from inside a Claude Code session (the full protocol and served-document anatomy are in `design/ARTIFACT_CHANNEL_STUDY.md`). A valid capsule — the sealed_sources fixture, restructured with all five blocks in `<body>` — was published through the host's native artifact tool, and the served document was fetched back through an owner-authenticated raw fetch.

**Finding — the trust layer tunnels through the host that lacks one.** Four measured results:

1. **Block placement is id-addressed, not positional.** A capsule with all five blocks in the body validates 30/30 strict before any publishing was involved. This was latent in the validator since v0.1 and never stated; §2.1 now states it (v0.3.13).
2. **The channel preserves author bytes and owns everything else.** The served document wraps the content in a non-portable frame-runtime — a `window.claude` capability proxy, dynamic `import("/_runtime/…")` loads, WebRTC lockdown, postMessage theme/scroll/telemetry plumbing — plus injected metas and a reset stylesheet. Inside that wrapper, the five authored blocks came back **byte-true**, trailing comment included. Title, versions, sharing, and retention remain host database state, exactly as F41 documented.
3. **The declared `data+manifest` hash recomputes bit-identically from the recovered blocks.** The scope chosen in v0.3.2 for browser re-save, and hardened in F34 as truth-vs-projection, is empirically a **channel-survival property**: the host only touches projection, so verifiable identity rides through.
4. **The validator draws the boundary correctly at both ends.** The served document *as a whole* fails validation — the wrapper's dynamic `import()` breaks Rule 2, as it should: the frame really is non-portable. A five-block extract-by-id plus minimal rewrap yields a 30/30 strict capsule with the original hash verifying. Recovery is ~50 lines and MUST NOT mutate the blocks; provenance of the recovery event belongs in custody records (the vault's side), never in the artifact — the recovered capsule *is* the original, same UUID, same hash.

Read against the extractor ecosystem (F42, source-verified the same day: conversation-UUID from the URL → localStorage chat data → regex over message content → ZIP), this splits recovery into two surfaces with a shared endpoint: extractors read the *conversation stream* (authored bytes, pre-wrapper); a fetcher reads the *served artifact* (wrapped bytes). Both converge after block extraction because integrity is canonical, not positional.

**Implication for the spec and the project.** Spec: the v0.3.13 clarification (§2.1 placement; tunneling and the no-mutation recovery contract in the change note) — deliberately small, because the finding's force is strategic. The F41–F45 arc diagnosed the dominant artifact channel as substrate-without-commitment-layer; F46 shows the commitment layer does not need the host's cooperation: **publish capsules through the channel and the trust surface survives it.** The build order that follows (study §6): the JS §9.1.1 port (F45) → the two-mode recovery adapter (tunneled extract + F43's bare-artifact wrap) → the provenance-preserving extractor feeding htmlvault's inbox. The scraper population proved the demand; this finding proves the contract that replaces the scraping.

**Related findings:**
- [F41](#f41-the-dominant-ai-artifact-producer-ships-the-substrate-without-the-commitment-layer--claude-artifacts-are-envelope-compatible-and-provenance-free) — the channel this probes; envelope-compatible turned out to mean *capsule-transparent*
- [F42](#f42-users-are-writing-scrapers-to-recover-their-own-documents--the-export-gap-is-empirically-demanded-not-hypothesized) — the recovery demand; this is the recovery contract
- [F43](#f43-a-spec-literate-agent-published-five-non-capsules-and-one-valid-capsule-in-the-same-session--the-conversion-cost-is-convention-not-capability) — the adapter's wrap mode; F46 adds the tunneled mode
- [F34](#f34-hash_scope-datamanifest-becomes-a-production-default--the-integrity-hash-covers-truth-not-projection-and-must-say-so) — truth-vs-projection, now doing its third job: custody posture, annotation anchoring, channel survival

### F47: Adopting the standard was cheaper than imitating a language — but the imitation is now permanent, and the tool that verifies had to be verified

**Date:** 2026-07-27

**Source.** Implementing the ratified JCS migration (`design/JCS_MIGRATION_PLAN.md`) end to end: reference canonicalizer, conformance suite, spec v0.4.0-draft, dual-mode validator, and the JavaScript hasher plus browser validator page. Three results were not predicted by the plan and are worth recording.

**1. The standard delivered, measurably.** RFC 8785's number format is ECMAScript's `Number::toString`, so the claim "JavaScript reaches it natively" needed testing rather than believing. A differential harness serialized **4,031 IEEE doubles** — 4,000 random bit patterns plus every boundary the format touches (±DBL_MAX, 2^53, denormal minimum, the `1e21`/`1e20` and `1e-6`/`1e-7` switch points, the F37 ordinate) — through the new stdlib-Python implementation and through a Node oracle. **Zero mismatches.** The Python side needed ~60 lines and no float arithmetic at all: the digits come from `repr`'s shortest round-trip output and are then *re-presented* per the ES algorithm, which is why there is nothing to be off-by-one about at the thresholds. Adopting the standard cost less than the imitation it replaced.

**2. The imitation tax is permanent, not eliminated — it stops growing.** The plan framed JCS as ending the "imitate CPython" burden. That is true only for *new* capsules. Every capsule sealed on the 0.3 line is immutable, so recipe v1 must be verifiable forever, and bringing verification to the browser therefore required writing the legacy Python-`repr` number formatter **in JavaScript anyway** — the exponent window, the signed two-digit exponent, and the `55.0`-keeps-its-marker rule, all reimplemented in a language whose own `JSON.stringify` actively destroys the last one. The honest accounting: a house format's cost is not paid once at adoption and refunded at migration; it is paid once per implementation, forever, for as long as the corpus exists. What the standard buys is that the cost stops *accruing*. This generalizes to the appendix E.1 correction made the same day — deprecation paths can never be deleted from a conforming validator, only gated by line.

**3. The tool that verifies had to be verified, and only its real runtime revealed the bug.** The browser validator is built by inlining `capsule-hash.mjs` into the page (an ES module import would fail under `file://` and break the offline promise the format itself makes). That inlining put two top-level `sha256Hex` declarations in one module scope — a duplicate-declaration error that aborts parsing of the *entire* script before a single line executes. The page rendered perfectly: correct layout, correct copy, and a status pill reading "running self-test…" that would have read that way forever. No error surfaced through the console-reading tooling; the file passed every static check; both conformance runners were green because they exercise the module, not the page. It was found only by loading the page over HTTP in a real browser, noticing the pill had not resolved, and re-importing the page's own script text as a blob module to force the parse error into the open.

The generalizable finding: **a verification tool fails silently in the one way that matters — by appearing to work.** Static checks, unit suites, and green cross-language runners all passed while the artifact was inert. The mitigation now shipped is structural rather than procedural: the page runs the four reference vectors on load and states the result in its own interface, so an inert or wrong build announces itself to whoever opens it. A verifier that cannot demonstrate its own correctness is asking for trust it has not earned — which is the same argument this project makes about capsules, turned on the tooling.

**Implication for the spec and the project.** No normative change beyond what v0.4.0-draft already carries. One design correction landed during implementation and is recorded in the plan: the proposed `integrity.canonicalization` manifest field was **dropped**, because a field naming the recipe is a second source of truth that can contradict the declared line, and the line already *is* the recipe's context. That is the inverse of the §8.4 hash/scope and §8.1 version/validator pairings, where the second element supplies context the first genuinely lacks — a useful test for future "should we also declare X?" questions: does the second declaration add context, or add a way to disagree?

**Related findings:**
- [F44](#f44-float_roundtrip-is-necessary-but-not-sufficient--f37s-remediation-was-scoped-to-parsing-and-the-formatting-half-is-still-open) — the finding that forced the migration; its two outstanding asks (operational number rules, a distributed conformance suite) are both discharged here
- [F45](#f45-every-path-to-a-verified-capsule-routes-through-python--the-on-ramp-terminates-at-the-hash-and-one-artifact-unblocks-it) — "every path routes through Python"; the JS hasher and the drop-a-file page are the artifact it named, now built
- [F37](#f37-a-one-ulp-float-parse-files-a-false-tampered-verdict--cross-language-canonicalization-needs-a-float-bearing-test-vector-and-correctly-rounded-parsing) — the original false-tamper incident that started the arc
- [F46](#f46-a-valid-capsule-tunnels-through-the-claude-artifact-channel--published-wrapped-recovered-verified-datamanifest-is-a-channel-survival-property) — verification belongs where the data lives; the browser page is that argument's tooling


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
| Composed map/print artifact | document + sealed source map | Compiler (external: compositor) | working (production; producer CI validates against the reference validator — F33) |

Nine documented domains, three production paths, four data shapes, all sharing the same five-block envelope. The framing holds. Remaining open question is whether more exotic domains strain the format (journal entries, recipes, scanned letters, voice-only notes, video clips, log files).

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

As of v0.3.12 (findings current to 2026-07-26):

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

- **Empirical size scaling tested** through 13 MB (synthetic, F5) and 13.7 MB (real production Mintel capsule, F20). Hard cap raised from 15 MB to 20 MB in spec v0.3.3 with a 15 MB soft warning for email-attachment compatibility.

- **Parked v0.4+ directions** (Appendix E of full spec): remove deprecated fields, compiler-kind UUIDv5 carve-out, reconsider `ai_usage_guidance` in domain capsules, hash-algorithm flexibility, author signing + transparency log, password-protected encrypted capsules, validator refinement for non-resource-loading `<link>` tags. None built; each waits for empirical pressure. **E.5 (Rule 12 vs. legacy templates) was resolved in v0.3.3** via the image-fallback carve-out documented in §2.3 — see F20.

**Biggest unbuilt piece:** author-side import tooling (registry + `import.py`). The producer side has matured significantly and the consumer side hasn't moved. The lightweight version (SQLite archive + pair viewer per F7) remains a candidate next concrete build.

**Biggest untested area:** cross-browser file:// behavior across Safari, Firefox, and Chrome. The format **should** work identically on file:// and http:// per spec — empirically this remains undertested.

## How to read this project

This is a research project that produces a working spec and reference implementation as primary artifacts. The spec is the hypothesis. The fixtures (compiled and LLM-produced capsules) are the evidence. The findings document (this file) is the running narrative of what we've learned. Every commit message is part of the research log — the "why" of each change is preserved in git history.

The project does not have a single "result" or a release date. It's a working investigation. The most likely failure mode is **spec inflation** (the long spec grows beyond what anyone reads) and the second most likely is **import-side abandonment** (we keep polishing the producer side while the consumer side stays unbuilt). Both are explicitly tracked as risks.

The project is not trying to invent something. It's trying to articulate the discipline that's missing from a practice already underway.
