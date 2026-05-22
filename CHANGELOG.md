# Changelog

All notable changes to the htmlcapsule project — spec, reference implementation, landing page, voices archive, and research record. The full-spec version (e.g. `v0.3.4`) is the load-bearing identifier; the Core spec version (`v0.3.0`) bumps only for normative rule changes; landing / notes / voices versions move independently and are tracked here only at major revs or when they coincide with spec work.

Format follows [Keep a Changelog](https://keepachangelog.com/) loosely. Commit IDs in parentheses for cross-reference.

---

## [Unreleased]

Active pending — post-v13 landing-cleanup tasks (not blocking, not on critical path; paused 2026-05-22 pending maintainer decision):

- **Sketch cleanup decision.** `landing-sketch.html` (v1, pre-design-system) and `landing-sketch-v2.html` (v2, design-applied) are both now superseded by `index.html` at v13.0.0 (`landing-sketch-v2`'s content is what `index.html` v13 IS). Same for `research-sketch.html` v1 vs `research-sketch-v2.html`. Decision pending on whether to prune the v1 sketches (keep v2s as record-of-exploration), keep both for full lineage, or move all sketches to `sketches/` subfolder so they're catalogued but not at the repo root.
- **Footer cross-link on `index.html`** pointing at `/exploration.html` for visitors who want the long-form research narrative. Not added in v13.0.0 because the integration brief was "make it the real landing" not "wire in cross-references." The existing top-nav has Spec / Examples / GitHub — could add an `Exploration` or `Long-form` link as a fourth.
- **Archive banner URL verification on `exploration.html`.** The banner currently says "production landing is now at htmlcapsule.org" with a link target of `index.html` (relative). Verify both display correctly when deployed and the relative path resolves to the canonical landing in the live environment.
- **Top-nav link verification on the new `index.html`.** The landing-sketch-v2 top-nav had `Spec / Examples / GitHub` links; verify each resolves to the right repo path (`CAPSULE_CORE.md` / `spec/examples/` / GitHub URL). The page may also benefit from a `Notes` link for the production essay at `notes.html`.
- **Possible: feature the `design/` folder.** It's now in the repo but not linked from any of the production pages. Worth considering whether `design/proposal.html` deserves a discoverable surface (e.g., a footer link on `index.html` or an entry in `llms.txt`) so future readers can find the canonical design-system source-of-truth.

Idea queue (`spec/DOMAIN_CAPSULES.md`) and voices queue (`voices/README.md`) hold candidates that haven't met the empirical-pressure bar.

---

## [Landing decision — v13.0.0] — 2026-05-22

**Not a spec change.** The landing-page exploration arc that ran from `v10.x` through `v12.0.0` (nine hero candidates, numbered Observation / Question / Answer editorial spine, devil's-advocate copy revision pass, the Claude Design design-system pass) is now closed. The maintainer has committed to the **Linear/Stripe-style stripped landing direction** — iterated through `landing-sketch.html` (v1, UUID `9bde04e1`) and `landing-sketch-v2.html` (v2, UUID `2860450e`) — as the production landing.

### Changed — `index.html` (v12.0.0 → v13.0.0)

- **Page structure completely replaced.** The 1883-line research-narrative hybrid (hero gallery 01-09 + Observations 1-5 + Questions 1-3 + Answers 1a/1b/2a/2b/2c/3a/3b/3c + downstream framing) is gone from the live page. In its place, the 612-line stripped landing from `landing-sketch-v2.html` (v0.3.0 form, post-design-system-pass): one hero (*"HTML you can keep."*), one primary CTA (*"Read the spec"*), one secondary CTA (*"View an example"*), the 5-block anatomy card with the manifest row highlighted in indigo, the lifecycle pill strip with **Seal** as the solid-indigo project slot, the rose-tinted "What this is not" callout, the slim demo + about + footer.
- **Identity preserved.** UUID `7d1a1ac8-c6d9-4ed1-98a7-f5399466262a` — the canonical landing's stable identity across structural restyles — is retained. `parents[]` records the two sketch UUIDs the design was iterated through (`2860450e` v0.3.0 + `9bde04e1`).
- **Version jump.** `capsule_version` 12.0.0 → 13.0.0 (major structural restyle, not just a token swap).
- **Title.** `"HTML Capsule — hero framing exploration"` → `"HTML Capsule"` (production title, not exploration title).

### Added — `exploration.html`

- **New file.** Captures the prior `index.html` content (the v12.0.0 form: full research-narrative hybrid + 9 hero candidates + numbered editorial spine + the Claude Design design-system pass already applied at the section-kind taxonomy level — Observations teal, Questions violet, Answers amber).
- **Fresh UUID** `881fed04-727e-441b-b626-c0637585043e` — this is now a distinct artifact (an archive page), not the production landing it once was.
- **`capsule_version` 1.0.0** — first version of this file as an independent capsule.
- **`parents[]`** references the canonical landing's `7d1a1ac8` (the v12.0.0 form was the immediate ancestor).
- **Archive banner** (amber-tinted aside, top of body) signals the role explicitly: *"Archive. This page is the landing-exploration phase that ran through May 2026 ... preserved here for record. The production landing is now at htmlcapsule.org."*
- **Why preserved as a live page instead of git-only:** the editorial content (Observations / Questions / Answers with verified-quote sourcing, three convergence findings, the maintainer's case study, the lineage / diff-tool / capsule-aware-review-surfaces argument) is meaningful research material in its own right. Future readers — and future Claude / future-maintainer — should be able to follow the argument as a live document, not have to git-archaeology it.

### Unchanged — sister sketches and notes

- `landing-sketch.html` (v1), `landing-sketch-v2.html` (v2), `research-sketch.html` (v1), `research-sketch-v2.html` (v2), `positioning-sketch.html` — all preserved in place as records of the exploration phase. Each carries its own UUID and design-system-pass version (v0.3.0 / v0.2.0 / etc.). The v2 design-system passes are the canonical record of how the design was applied per genre commitment.
- `notes.html` (v1.3.0) — already the production essay page; no integration needed. Design system already applied; preferred by maintainer in the same breath as the landing.

### What this validates

Three independent reads converged on this commitment over the May 2026 exploration arc: the devil's-advocate critique pass identified the genre tension on the long-form hybrid; the landing-agent's hero pick selected "HTML you can keep." as the strongest single claim; the external ChatGPT Deep Research review framed the project as research that doesn't need a sales-y landing. Each pointed at a different exit from the hybrid; the maintainer's chosen exit is the Linear/Stripe-style stripped landing (the cleanest conversion shape) with the research narrative preserved live at `/exploration.html` for those who want it.

### Added — research record (post-ship)

- **F27 — *The landing-page genre tension for applied-research projects resolves by splitting, not merging.*** Recorded in `RESEARCH.md` as the formal capture of this decision. Generalizable observation: a single URL cannot serve both "convert in 30 seconds" and "walk the full argument with citations" without paying both genres' costs. The two-page split — one URL per audience, same UUID lineage — is what worked. Includes a method-observation: external review convergence on a structural decision (here, three independent reads pointing at the split) is empirical pressure even when the decision feels like cowardice.

---

## [Design system v1] — 2026-05-22

**Not a spec change.** First canonical visual design system for the project's landing pages. Received as a handoff bundle from Claude Design (`claude.ai/design`) after the maintainer asked it to *"propose visual enhancements for all of these"* (the seven landing-page sketches in flight). Claude Design produced two proposals; the maintainer rejected the first (editorial-archival, italic display serif, oxide accent) and accepted the second (modern-sans, weight contrast, semantic color taxonomy). The chat transcript captures the rejection language verbatim and the project preserves both proposals for record.

### Added — design folder

- **`design/proposal.html`** (canonical) — full design memo from Claude Design with mockups of all four target pages (landing, research, positioning, notes). Contains the design's CSS in context. Uses Google Fonts directly; this is a design-tool output, not a Capsule, and is preserved as-received.
- **`design/proposal-v1-editorial.html`** (rejected) — the first version Claude Design produced before the maintainer's redirect. Preserved for record.
- **`design/README.md`** — documents the system in repo-native terms: origin story, five-hue taxonomy table, paper/ink/rule token tables, typography pattern (weight contrast replaces italic), Capsule-compliance discipline (system-font fallback, no network), and a per-page application table mapping each landing page to its lead taxonomy color.
- **`design/tokens.css`** — extractable CSS variable block + utility classes for copy-paste into Capsule `<style>` blocks. System-font fallback only; Core rule 2 compliant when inlined.

### The system in brief

- **Type:** Geist (300, 400, 500, 600, 700, 800) + Geist Mono, with system-sans fallback for Core rule 2 compliance when inlined into Capsules.
- **Paper system (cool fog):** `--paper` `#f5f6f8` / `--paper-soft` `#ebedf1` / `--paper-deep` `#dee1e7` / `--paper-page` `#ffffff`.
- **Ink scale:** five values from `--ink` `#0c0e13` down to `--ink-quiet` `#b0b5be`.
- **Rule scale:** `--rule` / `--rule-soft` / `--rule-strong`.
- **Five semantic hues, each with base/soft/edge/deep variants:**
  - **Indigo** `#4f46e5` — brand · primary CTA · headline emphasis · spec material
  - **Violet** `#7c3aed` — **Questions** · open work · research-flagged
  - **Teal** `#0d9488` — **Observations** · evidence · quotes
  - **Amber** `#b45309` — **Answers** · maintainer voice · essay
  - **Rose** `#be123c` — **Pain** · negation · "shouldn't die" framing
- **Pattern:** weight contrast (300 light + 800 punch) replaces italic emphasis in headlines.
- **Radii:** 8px (controls), 14px (cards), 999px (pills).

### Changed — landing page (`index.html` v11.19.0 → v12.0.0)

First page to adopt the canonical design system. Visual-layer-only pass — editorial copy unchanged from the v11.x devil's-advocate revision pass.

- **`:root` token block** replaced with the full design system (paper / ink / rule scales + five-hue palette with base/soft/edge/deep variants + Geist system-font stack).
- **Back-compat aliases preserved.** `--accent` now maps to `--indigo`; `--accent-soft` is a brighter indigo `#6366f1` (used for dark-frame hover on `data-num="05"`); `--accent-deep` maps to `--indigo-deep`. Existing rules pick up the new brand color without rewriting every reference.
- **Section-kind backgrounds re-mapped to the taxonomy:**
  - `.is-observation` → `var(--teal-soft)` (was white)
  - `.is-question` → `var(--violet-soft)` (was paper-soft grey)
  - `.is-answer` → `var(--amber-soft)` (was cream `#fcfaf3`)
- **Kind-tinted inline text** — `.cb-kicker` (the "Observation 1:" / "Question 2:" / "Answer 3c:" prefix), `.cb-frame-tag` (small mono section labels), and `.cb-aster` pick up their hue's deep variant so the taxonomy carries through to inline text, not just card backgrounds.

UUID `7d1a1ac8` preserved throughout (the page is the same capsule, restyled).

### Changed — sister sketches (parallel design-system pass)

Four sister sketches updated in parallel to apply the same design system, each picking up its lead taxonomy color per the application table in `design/README.md`:

- **`landing-sketch-v2.html`** — lead color: indigo. Hero "HTML you can keep." picks up weight contrast (300 light "HTML you can" + 800 indigo "keep."). Anatomy card with manifest row highlighted in indigo.
- **`research-sketch-v2.html`** — lead color: teal. Paper title "HTML Capsule" picks up weight contrast (300 + 800 teal). Findings O1-O5 converted to a 2×3 grid of taxonomy-colored cards (O1 teal, O2 indigo, O3 amber, O4 violet, O5 rose).
- **`positioning-sketch.html`** — lead colors: rose → indigo. Two-color headline ("die" in rose 800, "seal" in indigo 800). Lifecycle becomes a weighted timeline with the Seal node 30% larger, indigo-filled, on an indigo halo.
- **`notes.html`** — lead color: amber. Amber category chip, margin numerals in amber 700, amber pull quote at the "file over app" pivot moment.

All sister sketches retain their existing UUIDs (capsules are restyled, not replaced); `capsule_version` bumps minor for each.

### Provenance

- Bundle origin: `https://api.anthropic.com/v1/design/h/1h9LEWoDBWZgTL3Fqnnz6w` (received 2026-05-22)
- Bundle path: `html-capsule-improvements/`
- Design tool: Claude Design (`claude.ai/design`)
- Decision chat: preserved in the bundle at `html-capsule-improvements/chats/chat1.md` (the design-tool conversation where direction was decided)

---

## [Spec v0.3.5] — 2026-05-21

Doc-only patch. No schema, validator, or behavior change. Records external-review-driven candidate manifest fields in spec Appendix E without adopting them, preserving the project's "no addition without empirical pressure" discipline while making the considered-but-not-adopted ideas discoverable to future readers (including future Claude / future-maintainer who might re-derive them from scratch otherwise).

### Added — spec

- **Appendix E.11 "Extended manifest fields raised by external review (parked)"** in `spec/CAPSULE_SPEC.md`. Records three candidate fields surfaced by two converging external-LLM reviews of the v11.x landing page's HTML-version-control narrative (Obs 3 → Q3 → Answers 3a/3b/3c):
  - `supersedes[]` — UUIDs of capsules this one explicitly *replaces* (distinct from `parents[]` which records what this descended *from*). Semantic difference: "I came from X" vs. "use me instead of X."
  - `derived_from[]` — non-Capsule sources this artifact was built from (chat sessions, screenshots, external documents, datasets). Different shape from `parents[]` (Capsule-to-Capsule lineage).
  - `change_summary` — short human-readable note about what changed vs. the previous version; like a commit message scoped to the `capsule_version` bump. Would feed a future `capsule-diff` tool.
  
  Each is justified individually for why it's parked, not adopted (no real producer/consumer has hit the limitation yet for `supersedes[]` and `change_summary`; the Mintel producer has some real pressure for `derived_from[]` but no consumer has needed it programmatically yet).

- **Methodological observation** in the same Appendix E entry: external-LLM review is now a recurring source of spec-design candidates, alongside producer pressure, consumer pressure, and maintainer reflection. Worth tracking as a pattern in `RESEARCH.md` if it keeps happening.

### Changed — infrastructure

- `CITATION.cff` version bumped `0.3.4 → 0.3.5`.
- `README.md` updated in three places: intro state, full spec reference, status table.
- `llms.txt` updated to reflect `v0.3.5` in the full-spec entry and the CHANGELOG range.
- `index.html` landing badge updated to `v0.3.5`, About panel reference updated to "full spec v0.3.5", `data.spec.full` field updated to `v0.3.5`. Landing capsule_version bumped `11.15.0 → 11.15.1`.

### Changed — infrastructure (freshness — surfaced by external strategic review)

- **`README.md` F-finding lag fixed** — three places that referenced "F1–F22" or "F22" updated to "F1–F25" / "F25". Added one new sentence acknowledging F24 (host-vs-registry, the missing commitment layer) and F25 (ChatGPT producer-population reads of Core supplementary guidance) as recent findings worth surfacing in the intro paragraph. External ChatGPT Deep Research review explicitly flagged that the summary surface (README, `llms.txt`) lagged the underlying corpus (`RESEARCH.md`) — this fix closes that gap.
- **`llms.txt` F-finding lag fixed** — Research-log line and CHANGELOG-description line both updated from "F1-F21" / "F1–F22" to "F1-F25". Research-log line gained a one-sentence note pointing at F24 and F25 by name.
- **`GLOSSARY.md` "The four layers" section** gained a bridge paragraph explicitly mapping the verb-shaped four-layer model (Think / Shape / Seal / Harden) to the noun-shaped ecosystem-stack framing in `PRECEDENTS.md` (substrate / live editing / seal / host / discover). Both name "seal" as the slot Capsule occupies; the bridge note prevents the two vocabularies from drifting apart as they get used across landing-page sketches and external reviews.

### Added — research record (post-ship additions)

- **F25** — *ChatGPT producer-population reads Core supplementary guidance reliably; aesthetic adapts to content domain; legacy "Artifact Capsule" wording persists in user-side prompt templates.* Recorded in `RESEARCH.md`. Drawn from review of a batch of 7+ ChatGPT (GPT-5.5 Thinking) conversation-summary capsules across varied domains (coding, geology, legal, fire pits, vehicles, mining permits, identity-rights, design-award fit). Five distinct sub-findings: (1) all five required blocks present; (2) Rule 4 supplementary QR-code guidance followed faithfully — placement, sizing, URN encoding all respected, which means Core's supplementary sections (not just the twelve numbered rules) are load-bearing in practice when written as recipes; (3) where Core leaves implementation open (integrity, Rule 7 verification convention) producers diverge; (4) producer aesthetic adapts to content domain (geological capsule → earth tones; fire-pit capsule → warm cream/orange; legal letter → clean neutral; etc.); (5) legacy "Artifact Capsule" terminology persists in user-side prompt templates because Core had no explicit "use the canonical name" reminder. Initial framing of QR-code presence as "emergent producer behavior" was corrected (caught by maintainer) — it's actually Core spec being followed correctly, a stronger positive signal.

- **F26** — *Core spec accommodates 10 MB domain-specific media capsules without rule changes.* Recorded in `RESEARCH.md`. Drawn from a one-off domain-specific song capsule experiment (Paul McCartney & Wings, "Nineteen Hundred and Eighty-Five", 1973) embedding a 7.6 MB MP3 plus Wikipedia-sourced metadata plus a transcribed lyric sheet into a single 10.16 MB self-contained HTML capsule (UUID `e26b58da`, currently at `capsule_version` 1.1.0). Shipped 25/25 against the reference validator on first build with zero spec changes. Seven sub-findings: (1) domain via `type` field (`type: "song"`) — Core accepts arbitrary domain values; (2) CSP delta minimal (`media-src data:` is the only addition required); (3) capability vocabulary extends naturally (`media.play_audio` and `media.download_audio` using `<domain>.<action>`; Rule 7 markers heuristically validated); (4) size limits hold under-cap (10.16 MB under both 15 MB soft-warn and 20 MB hard cap; validator graceful with binary-heavy under-cap); (5) round-trip extraction works (the embedded MP3 is recovered byte-identically via `dataUriToBlob` runtime helper — genuinely portable, not just embedded for display); (6) aesthetic adapts to content domain (warm 1970s earth tones — extending F25's same-pattern-finding from ChatGPT-text-capsules to hybrid-produced media); (7) version semantics in practice (v1.0.0 → v1.1.0 same UUID, `capsule_version` bump alone — the parked Appendix E.11 fields stayed parked correctly since nothing was distributed between versions, but the empirical-pressure point for `supersedes[]` is now recorded for the next time someone hits it).

### Changed — Core spec (post-ship clarification, not a rule change)

- **`CAPSULE_CORE.md`** — added a "use the canonical name when you write your prompt" reminder immediately above the "How to ask an LLM to produce a capsule" section. Cross-references F25. Closes the loop on the legacy-prompt-template leak by making the canonical name unmissable to anyone templating their own prompts. **No rule change** — Core stays at v0.3.0; this is a clarification, not a normative edit. Full spec stays at v0.3.5.

### Changed — landing page (devil's-advocate copy revision pass, v11.16.0 → v11.19.0)

Four-version sequential pass through the landing page's editorial spine — Observation 1, Question 1, Answers 1a/1b, Question 2, Answers 2a/2b/2c, Observation 2, Observation 3, Question 3, Answers 3a/3b/3c, Observation 4, Observation 5. All twelve sections tightened against a single set of devil's-advocate critiques: footnote-apologies → word swaps, redundant cross-references removed, walls-of-bold converted to real `<ul>`s, jargon ("empirical pressure", "anyone technical", "bring your own bucket") replaced with plain English, forward-pointer parentheticals stripped, weak hedges committed-or-cut, punchlines promoted from buried paragraphs to titles where they earned the slot.

- **v11.16.0** — Observation 1 retitled "HTML has emerged as a key substrate" → "HTML is becoming the default output format." Self-apologetic footnote about "substrate" removed (the fix is the word swap, not the apology). Karpathy quote demoted from parallel blockquote to one-line attributed mention in body prose; Thariq carries the structural claim alone.
- **v11.17.0** — Q1/A1a/A1b. Q1 depersonalized ("How do I get HTML out of *my* LLM" → "How do you get HTML out of an LLM"); A1a re-quote redundancy of Karpathy + Thariq dropped; A1b title hedge "(according to the Spec)" dropped; wall-of-bold contract-elements paragraph converted to real `<ul>`; "first-class spec-aware participant" promoted from body prose to `.cb-frame-punchline`.
- **v11.18.0** — Q2/A2a/A2b. Q2 retitled with framing sentence; A2a tag retitled "Viewing strategy" → "View it"; A2b's two-paragraph 270-word architectural description collapsed to one punchline + one short body (~95 words), load-bearing "Format and host are different jobs" finding now visually dominates instead of buried.
- **v11.19.0** — A2c (was held), Obs 2, Obs 3, Q3, A3a, A3b, A3c, Obs 4, Obs 5. A2c title "Maybe let's take it a step further" → "Build your own producer"; A3c punchline "The HTML is the artifact. The manifest is the review surface" promoted to title; Obs 5 title sharpened; Obs 4 hedge replaced with committed scope; cross-reference web removed.

Net effect across the four versions: visible prose 19,113 → 15,675 chars (~18% reduction), with section-level cuts in A1b / A2b / Obs 3 / A3c closer to 40%. UUID `7d1a1ac8` preserved throughout (the page is the same capsule, content-tightened — not a new derived capsule). All four versions validated 25/25 against the reference validator at ship.

### Added — comparison sketches (parallel direction exploration)

Three sibling capsules built alongside `index.html` to test alternative genre commitments before deciding the page's direction. Each one is itself a valid Capsule (5 required blocks, 25/25 against the reference validator) and declares its position relative to `index.html` via the genre signal in its `data` block.

- **`landing-sketch.html`** (350 lines, UUID `9bde04e1`) — Linear / Stripe / Vercel commitment. Hero: "HTML you can keep." One primary CTA, one secondary CTA, one code-block functional demo of the 5 required blocks, slim footer. Single accent color, dark/light theme. Zero numbered observations, zero cross-references, zero research jargon. Roughly 9% of `index.html`'s prose volume.
- **`research-sketch.html`** (490 lines, UUID `766faed9`) — NeRF / gaussian-splatting / academic project page commitment. Structure: Title + author block + abstract + numbered findings O1-O5 (deliberately avoiding collision with `RESEARCH.md` F1-F25) + Methods + Related Work + Spec & Artifacts + Cite this work + slim footer naming the page as a Capsule. Restrained academic aesthetic (serif body, single muted accent, generous margins). Zero CTA buttons; pointers do the conversion job.
- **`landing-sketch-v2.html`** (397 lines, UUID `2860450e`, parents → `9bde04e1`) — `landing-sketch.html` iteration absorbing external strategic review signals (ChatGPT Deep Research + maintainer devil's-advocate critique). Three additions kept from absorbing v1's conversion shape: (1) "Anti-context-loss" accent eyebrow above the hero (project's own native term from `GLOSSARY.md`); (2) sharpened lede itemizing failure modes; (3) CSS-only lifecycle pill strip ("Substrate · Live edit · **Seal** · Host · Discover") naming Capsule's slot in the landscape; (4) a "What this is not" callout pulling verbatim from `GLOSSARY.md`.

These sketches are exploratory artifacts, not landing-page replacements; the production landing remains `index.html` at v11.19.0 pending a maintainer commitment to one of the genres. (`research-sketch-v2.html` and `positioning-sketch.html` still in flight at time of writing.)

---

## [Spec v0.3.4] — 2026-05-20

Interactive-archive category named; lifecycle decomposition (live-editing / format / hosting / discovery) made explicit across the project; voices archive grown from 0 to 2 archived + 2 queued; second convergence finding (F22) documented.

### Added — spec

- **§2.3 "Interactive archive" subsection** — formal name for the category; JavaScript-off litmus test as the operational distinction between archive and app; permitted vs. forbidden examples (Mintel measure-tool as the canonical permitted example) (`56b5b7b`).
- **§2.3 "Carve-out for visualization geometry"** — image-fallback pattern documented as the principled resolution to Rule 12 in cases where geometry can't reasonably be pre-rendered as static markup (`9bdb2db`).
- **`spec/HOSTING.md`** — descriptive host-contract pattern observed across MinDev + htmlbin (short URL + `/raw` endpoint + minimal chrome + honest attribution + optional integrity attestation in response headers) (`ef11394`). Adoption section also recommends hosts publish `/llms.txt` indexing their hosted capsules (`db49dad`).
- **`domain.exploration_map` schema**: image-fallback as a required convention with HTML template (`9bdb2db`).
- **`spec/DOMAIN_CAPSULES.md` "Idea queue" section** + first entry `domain.music_stems` — pre-proposal home for domains noodled on but no working example yet (`29957f8`).
- **GLOSSARY entry for "Interactive archive"** (`56b5b7b`).

### Added — research record

- **F20** — First publicly-fetchable Mintel production capsule (Copper Dome, 13.7 MB) validates spec at scale; five empirical findings around it (`9bdb2db`).
- **F21** — Independent convergence on the host-contract pattern (MinDev + htmlbin) (`2a21d76`).
- **F22** — Independent convergence on the live-editing-layer pattern (html-docs.com + workplane.co) (`1f298cf`).
- **F23** — URN-not-URL QR encoding empirically validated by a host-side visibility-tier removal (MinDev dropped `public`, breaking Mintel-encoded URL QRs for anonymous scanners overnight). Also added "Visibility tiers as host-side policy" section to `spec/HOSTING.md` naming this case.
- **F24** — Refinement of F23. Introduces the **host vs. registry** distinction: a host serves capsules; a registry is a host that commits, publicly, to keeping its behavior stable (URL stability, visibility honor, deprecation discipline, attestation headers, immutability). F23's URN-as-default is correct for producers without signal about host commitments; producers with signal (target host has declared registry compliance) can encode URLs as a calibrated bet against a published contract. **Capsule Registry Compliance v1** sketched in `spec/HOSTING.md` as the optional commitment layer hosts can opt into — including a proposed well-known declaration shape at `<host>/.well-known/capsule-compliance.json`. Not yet adopted by any host; MinDev / htmlbin / the maintainer's planned personal host are natural first candidates. No Core spec change; format stays agnostic. Synthesis came from maintainer pushback on F23's first framing — a research-method observation worth tracking.

### Added — infrastructure & citability

- **`CITATION.cff`** at repo root — makes the project formally citable via GitHub's "Cite this repository" button; consumed directly by Zotero / citation managers (`29fbc9e`).
- **`/llms.txt`** at site root — Chrome Lighthouse-style site-discoverability index per the Jeremy Howard / Answer.AI proposal (`db49dad`).
- **README "How to cite" section** pointing at CITATION.cff (`29fbc9e`).
- **Validator URL mode** — `python3 compiler/validate.py <https://host/.../raw>` fetches the body via the host's raw endpoint, cross-checks any `x-capsule-content-hash` / `x-capsule-uuid` response headers against the manifest, then runs the standard 26 checks (`ef11394`). Real-world tested against the live MinDev Copper Dome capsule.

### Added — voices archive

- **`/voices/` directory established** as a first-class archive for primary-source voices in the conversation Capsule is part of.
- **`voices/karpathy-html-progression-2026.html`** v1.0.0 (UUID `e8a4c1d2`) — Karpathy's "structure your response as HTML" X post + LLM-wiki gist + four-step progression (`02530e9`).
- **`voices/utsengar-htmlbin-2026.html`** v1.0.0 (UUID `b3d8f2a1`) — Utkarsh Sengar's htmlbin.dev, the hosting-layer voice (`ef11394`).
- **`voices/README.md`** — directory index + queue-tracking pattern (parallel to the Idea queue in DOMAIN_CAPSULES); graduation rule for queued → archived (`5ea0296`).

### Changed — maintainer attribution

- **CITATION.cff `authors:` block** — `B. F. Garden` placeholder replaced with the project's actual maintainer: Luke Schuss (Vancouver, CA) with email `info@lukeschuss.com` and website `https://lukeschuss.com`. Citation form is what Zotero / GitHub's "Cite this repository" button consume, so this fixes the citability surface first.
- **`README.md` — new "Maintainer" section** at the end with name, location, website, and email; invites independent-implementation reports and producer/consumer feedback.
- **Notes essay byline** updated in both the data block and rendered byline (linked to `lukeschuss.com`); essay bumped to v1.2.0.
- **Landing-page colophon** — adds "maintained by Luke Schuss · Vancouver" line; also fixes a stale static colophon version string (`v10.11.0` → `v10.13.0`) carried over from v10.11→v10.12 ship. Landing bumped to v10.13.0.
- **GitHub repo description** updated to lead with "HTML Capsule" and include "Maintained by Luke Schuss" (visible on the repo's main page).

### Changed — landing page (v10.2 through v11.0)

The landing went into **hero framing exploration mode** at v11.0.0 — the conventional hero/four-questions/voices/footer structure (v10.x) was replaced with eight numbered candidate hero variants stacked vertically, each with its own framing (discipline / outcome / substrate question / contract / max-short / PDF comparison / mark-first / problem question), its own layout (left-aligned, centered, dark inverted, mark-led), and its own background color. Numbering is for reference; the winning framing will become the page and the rest will be removed. The v10.15 landing structure is preserved in git at commit `94c3802`.

Twelve incremental v10.x iterations preceded the v11.0 reset. Highlights:

- **v10.2** — "File over app, taken further" aside citing Steph Ango's principle (`5457f5b`).
- **v10.3** — Hero pivoted from narrow single-column stack to horizontal two-column split (title left, sub/CTA/stats right) (`5457f5b`).
- **v10.4** — Adjacent Voices panel added with 4 entries: Thariq, Karpathy, Blake, Simon Willison (`6fe2d56`).
- **v10.5** — Karpathy archive link from the panel (`02530e9`).
- **v10.6** — Two-beat bridge: "The durable unit of knowledge is shifting from the note to the artifact." + "So HTML is the substrate. Now what?"; "Tools, not apps." aside naming the interactive-archive category (`56b5b7b`).
- **v10.7** — Utkarsh / htmlbin added (hosting-layer voice) (`2a21d76`).
- **v10.8** — Jeremy Howard / llms.txt added (discovery-layer voice) (`db49dad`).
- **v10.9** — Raunaq Bhutoria / html-docs.com added (first live-editing-layer voice) (`40f7238`).
- **v10.10** — Adjacent Voices panel reorganized into two layer-tagged sub-sections: "Format & substrate observers" and "Layers Capsule composes with" (`5ea0296`).
- **v10.11** — Matan / Workplane added (second live-editing-layer voice); convergence with html-docs documented as F22 (`1f298cf`).
- **v10.12** — Top bar tightened: brand reads "HTML Capsule" (full project name) instead of "Capsule"; small linked version badge (`v0.3.4`) replaces the inline "open spec v0.3.0" subtitle; multi-link primary nav collapses to a single GitHub icon-link with accessible label. Page `<title>` and meta description updated to match. New mobile breakpoint at 600px hides the "GitHub" label (icon-only on phones), tightens topbar/stat spacing, and shrinks the badge; a 380px breakpoint stacks hero CTAs full-width. Stale `data.spec.full` value in the landing's data block bumped from v0.3.2 → v0.3.4 to match the current full-spec version. Same logical landing capsule (UUID `7d1a1ac8` preserved).
- **v10.13** — Maintainer attribution: footer colophon now reads "maintained by Luke Schuss · Vancouver" (linked to `lukeschuss.com`); also fixes a stale static colophon version string (`v10.11.0` → `v10.13.0`) per Rule 12 pre-rendered-content discipline.
- **v10.14** — First real brand mark: the placeholder "C" glyph in the top bar is replaced with an inline-SVG horizontal capsule outline containing the `</>` code symbol — a literal rendering of "HTML in a capsule" (concept from ChatGPT image generation; redrawn as SVG for crisp scaling and `currentColor` integration). Monochrome, picks up `--ink` automatically. 36×20 on desktop, 30×17 on phones via the 600px breakpoint.
- **v10.15** — Brand-mark geometry locked in: capsule outline expanded to fill the full viewBox (rect `30×16`, `rx 8`), stroke weight tightened `2.2 → 1.8` for more refined linework matching the source design more closely, brackets pushed further out (`<` apex at x=6, `>` apex at x=26) so the code symbol breathes inside the capsule. Same SVG shape, same `currentColor` integration, dialed-in proportions.
- **v11.0** — Page restructured to **hero framing exploration mode** (major bump). Topbar + small explorer intro + 8 numbered candidate hero variants stacked vertically + slim footer. Each variant has its own framing tag, layout treatment (left / centered / centered+dark / mark-first), and background color (paper / cream / cool gray / pale blue / ink / sand / soft blue / paper-deep). Variant 05 is dark-inverted to break the visual rhythm. Big mark variant (07) uses a 220px-wide inline SVG render of the brand mark. Data block restructured from the multi-section `hero/bridge/questions/voices/journey` shape to a flat `intro + variants[]` shape; runtime `buildMarkdown` regenerated. `#capsule-root` CSS loosened (no longer max-width-constrained) so frame backgrounds can bleed full-width; child blocks use new `.cb-shell` class for max-width centering where needed. Same UUID `7d1a1ac8` preserved; validator passes 25/25.
- **v11.1** — Variant 09 added (context-led · plain-English on-ramp) — three-paragraph hero with explicit examples of what AI tools produce (reports, maps, demos, dashboards, visual notes, interactive documents), the spec definition stated plainly, and the "It is not a new file format" disclaimer made the explicit second-paragraph beat. Closes with `ONE FILE. NO NETWORK. BUILT TO LAST.` as a mono-uppercase accent tagline before the CTAs. Drawn from an external review's recommendation, which observed that the v11.0 variants spoke too much to readers already inside the format's vocabulary (`discipline`, `substrate`, `artifact`). The near-white warm background (`#fbfaf5`) sets it apart from the other eight without going to ink contrast. Also: variant 06 swap `Like a PDF, but alive.` → `Like a PDF, but inspectable.` (more precise per the same review). Frame labels updated `0X / 08` → `0X / 09` and intro text updated `Eight` → `Nine`. New `.cb-frame-tagline` class for the punctuation-line treatment.
- **v11.2** — Variant **00** added at the TOP of the gallery — an **observation-led preamble** designed to sit *above* whichever hero gets picked, rather than replace one. Opens with `Observation: HTML has emerged as a key substrate* for AI-assisted work.` (with a self-aware italic footnote about "substrate" being overused), then renders two voice blockquotes as the evidence — Thariq Shihipar on markdown becoming restricting under more-powerful agents, and Andrej Karpathy on telling LLMs to "structure your response as HTML" — then a pivot leadin: `So the question becomes: what do you do with all that HTML?`. Editorial/research-paper voice rather than product-pitch voice; quotes the existing Karpathy archive (`voices/karpathy-html-progression-2026.html`) directly. Pure-white background (`#ffffff`) for editorial weight. Label format `00 · preamble` (not `0X / NN`) signals it's a different *kind* of candidate from the nine heroes. CSS: new `.cb-frame.is-observation` modifier, `.cb-quote` figure/blockquote treatment with accent left-border, `.cb-frame-footnote` / `.cb-frame-lead` / `.cb-frame-leadin` for the editorial bones. Explorer intro updated to acknowledge the preamble+heroes split.
- **v11.3** — Removes the meta `Hero framing exploration · Picking the right framing.` explainer section that used to sit between the topbar and variant 00. The page now opens directly into editorial-voice variant 00 instead of a process-page meta-intro. Adds variant **00b** (`Lived practice · maintainer's own use`) — a paired case-study preamble that opens with Thariq's FAQ answer about viewing HTML files (open it locally, or upload to S3 for sharing), then carries the maintainer's first-person account of building map-making tooling that emits HTML conforming to the Capsule spec for clients/colleagues. Explicitly acknowledges the file-size tradeoff: *"Does the file size creep up? Yes — but frankly, I don't care."* Signoff: `— Luke Schuss · maintainer · Vancouver · lukeschuss.com`. Soft-cream background (`#fcfaf3`) immediately below 00's editorial white — keeps the pair visually connected as a unified opening before the hero gallery begins at 01. Variant 00's CTA changed from `Scroll the framings ↓` to `Take it further ↓` (now scrolls to 00b instead of 01). CSS: new `.cb-frame-bridge` / `.cb-frame-prose` / `.cb-frame-kicker-line` / `.cb-frame-signoff` classes for the case-study composition.
- **v11.4** — Tightens the opening pair (00 + 00b) and the topbar. Drops the meta framing-tag rows that read `Observation-led preamble · designed to sit above any hero` and `Lived practice · maintainer's own use` from variants 00 and 00b — the corner labels `00 · preamble` / `00b · case study` carry that signal sufficiently. Frame padding for the preamble pair tightened to `clamp(40px, 5vh, 64px)` (down from the heroes' `clamp(72px, 11vh, 128px)`) with `min-height: 0` so they're sized to their content rather than viewport-height-filling. Variant 00 title font shrunk to `clamp(24px, 3vw, 36px)` (down from `clamp(28px, 3.6vw, 42px)`). Variant 00 CTA changed from a heavy primary button to a quieter mono text-link with arrow (`.cb-frame-jumplink`). Variant 00b bridge font shrunk to `clamp(22px, 2.8vw, 30px)` (down from `clamp(26px, 3.4vw, 38px)`). Blockquote/prose/signoff sizes and spacings all dialed down. Topbar `padding-top` (in `.cb-shell-top`) shrunk `36px → 20px`, `padding-bottom` (in `.cb-topbar`) shrunk `24px → 14px`. Voice quotes also fixed: Thariq's quote now uses proper `&hellip;` Unicode ellipses at the two elision points (after `communicate with us` and after `restricting format`) rather than periods that masked the elisions; Karpathy's pull-quote uses curly typographic `&ldquo;&rdquo;` around the inner `structure your response as HTML` phrase and is bracketed with leading + trailing `&hellip;` to signal it's a mid-sentence extract from the canonical archive at `voices/karpathy-html-progression-2026.html` (which has the full Karpathy passage). Result: opening pair now fits in roughly one viewport-height instead of two; topbar reads as a compact header.
- **v11.5** — Restructures the opening into a clearer narrative arc: **Observation → Question → Case study**, then heroes. Variant 00 (`observation`) drops the `So the question becomes…` leadin and the `Take it further ↓` jumplink — the section now ends after the second voice quote. NEW variant **00b** (`question`, same white background) titled `Question: What do you do with all that HTML?` carries two existing answers in the wild: **Answer A** is Thariq's FAQ quote (open it in a browser locally, or upload to S3 for a shareable link), moved up from the prior case study; **Answer B** is Utkarsh Sengar's [htmlbin.dev](https://htmlbin.dev/) (short URLs + `/raw` endpoint for agent-emitted HTML; independent convergence with the MinDev hosting pattern, format itself stays hosting-agnostic; links to the existing `voices/utsengar-htmlbin-2026.html` archive). Existing case study renumbered **00b → 00c** (soft cream background unchanged), reframed with kicker `Or — the maintainer's answer:` so it reads as a third answer after the two above (rather than as an arbitrary "lived practice" beat). Corner labels updated for parallel naming: `00 · observation` / `00b · question` / `00c · case study`. New `.cb-answer` / `.cb-answer-tag` / `.cb-answer-h` / `.cb-answer-body` CSS classes for the answer-block treatment with a thin `--rule-soft` separator between answers. Reading flow: editorial-voice white pair (00 + 00b) → cream shift (00c, maintainer voice) → hero gallery begins at 01.
- **v11.6** — Expands Answer A and Answer B in the Question section so they actually *do landscape analysis* instead of just naming the answers. **Answer A** keeps Thariq's FAQ blockquote and gains a body paragraph naming what the view-locally-or-S3 approach offers (minimum-viable, portable substrate) and what it leaves open (no default shareable URL — exactly the friction Answer B is designed for) — bridges to B. **Answer B** now leads with htmlbin.dev's own positioning verbatim (`API for agents to share HTML. Agent-native, end to end. Drop HTML — get a public URL.`) attributed to `htmlbin.dev positioning · Utkarsh Sengar (@utsengar)`. Two body paragraphs follow: (1) what htmlbin does — purpose-built public hosting layer, May 2026, OAuth device-code first-publish flow, `/p/{slug}` URLs with byte-identical `/raw` endpoint, minimal host chrome + honest authorship attribution, no format discipline imposed; (2) why htmlbin matters for the project's landscape analysis — htmlbin and **MinDev** independently converged on the same hosting pattern, which is empirical evidence that the **format/host split is real, not theoretical** (hosting is one job, format discipline is another, they compose; valid Capsules can be served by htmlbin, MinDev, or self-hosted). Cross-refs to RESEARCH.md F21, spec/HOSTING.md, and the full voices/utsengar-htmlbin-2026.html archive. Answer tag labels gained slot suffixes: `Answer A · viewing strategy` / `Answer B · hosting layer`. Section lead changed from `A couple of answers in the wild:` to `Two existing answers — different shapes, same question:`. CSS fix: `.cb-answer-body` now has `margin: 0 0 14px` with `:last-child { margin-bottom: 0 }` so multi-paragraph answers breathe properly between paragraphs (Answer B's two-paragraph analysis no longer runs flush).
- **v11.7** — Stronger visual separation between the opening sections, and answer blocks become cards. Variant 00b (Question) background changes white → `var(--paper-soft)` (#eceef2 cool grey), so the opening trio now reads as three distinct visual zones (white observation → grey question → cream case study). The Answer A and Answer B blocks inside 00b are now **white cards** lifted out of the grey backdrop — 8px border-radius, 1px `var(--rule)` border, 28px/32px padding. The thin-rule-separator pattern (between answers) is replaced with 22px gap between cards. Answer typography bumps: heading `19px → 22px`, body `15.5px → 16.5px`, blockquote-inside-card `15.5px → 17px`. Blockquotes inside answer cards lose their own background tint (which would have read as nested boxes inside cards inside a section); just the accent left-border now marks them as quotes. Mobile breakpoint adds tighter card padding (22/20) and proportional type-size reductions so cards don't blow out at 375px. Result: the Question section reads as a clearly-different *kind* of content from the surrounding sections — analytical / inventory-of-answers — rather than just more editorial prose.
- **v11.8** — **Research-paper numbering taxonomy** applied across the opening sections. Corner labels switch from `NN · kind` to bare taxonomy IDs: `Observation 1` (was `00 · observation`), `Question 1` (was `00b · question`), `Answer 1c` (was `00c · case study`). Section H2 kickers gain the number: `Observation 1:` / `Question 1:`. Answer-card tags inside variant 00b update: `Answer A · viewing strategy` → `Answer 1a · viewing strategy`; `Answer B · hosting layer` → `Answer 1b · hosting layer`. Variant 00c (the maintainer's case study) **reframes as Answer 1c** rather than a separate "case study" beat — same prose content and cream background, but the kicker line is now a parallel `.cb-answer-tag` reading `Answer 1c · custom producer + registry · maintainer's own answer`, matching the mono-accent uppercase treatment of 1a and 1b inside the cards above. Question 1 lead now mentions all three answers and links forward to 1c via in-page anchor: *"Three answers, different shapes — two in the wild, one from the maintainer (below in [Answer 1c]):"* The numbering scheme is extensible: future `Observation 2 / Question 2 / Answer 2a/2b/2c` slot in naturally as the landscape analysis grows. `data-num` HTML attributes stay (`00 / 00b / 00c`) for CSS targeting; only the visible labels changed.
- **v11.9** — Adds **Observation 2** (variant 00d) at the end of the opening narrative — after Answer 1c, before the hero gallery — on the same white background as Observation 1 (signals "back to observation mode"). Title: *"Observation 2: File over app is as relevant today as it ever was."* Quotes Steph Ango (Kepano)'s "File over app" essay verbatim: *"If you want to create digital artifacts that last, they must be files you can control, in formats that are easy to retrieve and read."* Attribution links to `https://x.com/kepano` and `https://stephango.com/file-over-app`. Followed by maintainer's commentary on Obsidian's plugin route: well-intentioned but undermines the principle — when presentation requires plugin installs, you're back at *app over file* (italic emphasis on the reversal). Numbering scheme extends naturally: each observation now gets its full arc (Observation 1 + Q1 + Answers 1a/1b/1c, then Observation 2) before the next one. No Question 2 yet; would slot in naturally if/when one becomes useful.
- **v11.10** — **Observations / Questions / Answers each become their own KIND with a distinct color and parallel section formatting.** Backgrounds now driven by KIND class on the `<article>` element instead of per-data-num CSS: `.is-observation` → white (`#ffffff`), `.is-question` → grey (`var(--paper-soft)` #eceef2), `.is-answer` → cream (`#fcfaf3`). CSS specificity is equal across the three KINDs, so later rules win the cascade — a section with both `.is-observation` and `.is-question` resolves to grey; a section with both `.is-observation` and `.is-answer` resolves to cream; plain observation sections stay white. Restructure: Answer 1a (Thariq · viewing strategy) and Answer 1b (htmlbin.dev · hosting layer) — which used to be white CARDS nested *inside* the Question 1 section on grey — are now extracted into their own sibling sections (`data-num="00b1"` and `data-num="00b2"`). Question 1 becomes lean: just the question + a TOC line linking to the three sibling Answer sections (1a / 1b / 1c). Answer 1c (the maintainer's case study) gains the `.is-answer` KIND class alongside its existing `.is-case-study` sub-modifier, so it sits on the same cream as 1a/1b but keeps the italic-emphasis treatment on its title phrase (*"Maybe let's take it a step further."*). All three Answer sections now share the same shape: corner label (e.g., `Answer 1a`), slot-tag eyebrow (e.g., `— VIEWING STRATEGY` in mono accent), H2 with `Answer 1x:` kicker + the heading sentence, then content (blockquote and/or prose). Dropped: the `.cb-answer` card CSS (cards no longer used) and the `.cb-frame-bridge` rule (Answer 1c now uses the standard title pattern with `<em>` for italic). Visual rhythm of the opening: Obs1 white → Q1 grey → A1a/1b/1c cream-cream-cream → Obs2 white → hero gallery (01 paper).
- **v11.11** — Extends the analysis with two new arcs (six new sections total) inserted between Observation 2 and the hero gallery. **(A) HTML version-control arc** — Observation 3 (`00e`, white) quotes Thariq's FAQ note that *"HTML diffs are noisy and hard to review compared to Markdown"* and reframes a related, more general problem: artifact identity (the PDF `v1` / `v2` / `v3-final` / `v3-real-final-USE-THIS` problem people already know). Argues identity and lineage are addressable even when diffs aren't. Question 2 (`00f`, grey) — *"How do you keep track of which version of an artifact you're working with?"* — with TOC to two sibling Answers. Answer 2a (`00f1`, cream) — filename versioning (what people actually do; works because the version lives outside the file; breaks when the filename is dropped). Answer 2b (`00f2`, cream) — the spec's `uuid` + `capsule_version` + `parents[]` identity/lineage fields recorded inside the inline manifest, so the artifact knows what it is and what it descended from regardless of filename. Explicitly acknowledges HTML-diffs-proper are still hard — a semantic diff over manifests + data sections would be tractable but isn't built. **(B) Editor-layer observation** — Observation 4 (`00g`, white) names three projects in different shapes of the live-editing layer emerging around AI-emitted HTML: Claude Design (Anthropic Labs, launched April 17, 2026 — chat-and-preview HTML/CSS/JS generation), html-docs.com (Raunaq Bhutoria — agents publish, humans comment, agents revise async loop), Workplane (Matan / matanrak — MCP-first, multi-agent, same shape as html-docs). Maintainer commentary: Capsule sits downstream as the seal step; format is editor-agnostic; whether the project ever grows its own collab layer is open, and if it does it would be a registry concern (lightweight commenting on hosted Capsules), not a format concern — same posture as the format/host split. All six new sections use the KIND-class color system (`.is-observation` white, `.is-question` grey, `.is-answer` cream) from v11.10. No new CSS needed.
- **v11.11.1** — Attribution cleanup: Answer 1b no longer names MinDev (MinDev belongs to Answer 1c — the maintainer's own custom producer + registry approach — and was previewing too early in 1b). 1b's convergence-evidence paragraph reframed with vague language ("Multiple independent hosting layers have now converged on the same minimal shape...") + the existing F21 / spec/HOSTING.md cross-refs for readers who want the named specifics. Answer 1c's slot tag updated `Custom producer + registry · maintainer's own` → `Custom producer + MinDev registry · maintainer's own` so MinDev is explicitly named where it belongs taxonomically.
- **v11.12** — **Two additions: a new Question 1 upstream of the existing arcs, plus a new Answer 3c on spec-evolution for diffs.** New **Question 1** (`00a`, grey) — *"How do I get HTML out of my LLM?"* — inserted between Observation 1 and the previous Question 1 (which becomes Question 2). Two answers: **Answer 1a** (`00a1`, cream) — *"Just ask the LLM for HTML"* — quotes Karpathy ("structure your response as HTML") and Thariq ("I've started preferring HTML as an output format") as two voices both pointing at the same vague-but-functional default; commentary notes you get unstructured HTML (no manifest, no identity, no integrity, no contract) — fine for one-off viewing, lossy otherwise. **Answer 1b** (`00a2`, cream) — *"Paste the Capsule Core spec into your prompt"* — the contract-based approach: ask for a Capsule (not just HTML); the Core spec is one page (twelve numbered rules) designed to paste into an LLM prompt; the LLM returns a sealed .html with manifest, integrity hash, UUID + parents[], declared capabilities (Rule 7), pre-rendered content (Rule 12), no network deps (Rule 2). Includes the "producer becomes a first-class spec-aware participant" reframe and pointers to CAPSULE_CORE.md, full spec, examples. **Renumbering follows**: existing Question 1 → Question 2 (what do you do with HTML); existing A1a/1b/1c → A2a/2b/2c; existing Question 2 → Question 3 (how do you track versions); existing A2a/2b → A3a/3b. New **Answer 3c** (`00f3`, cream) — *"A Capsule-aware diff over manifest + data + content, layered on the spec"* — addresses the user's note that the prior treatment didn't talk about how the spec could evolve to help with diffs. Sketches what a `capsule-diff` tool would do: semantic diff over each of the five required blocks (manifest field-level JSON delta, data JSON delta, visible-content text delta ignoring presentation, bounded style/runtime diffs). Includes example output. Frames the tool as a layer on the spec (analogous to `git log --oneline` on git's commit graph), not a spec change — the spec's existing structural discipline is what makes a semantic diff tractable. Not built yet; parked in spec Appendix E. Existing Answer 3b's closing paragraph updated to forward-point at 3c instead of just acknowledging diffs are hard. `data-num` values stay stable for renumbered sections (00, 00b, 00b1, 00b2, 00c, 00f, 00f1, 00f2); new data-num values are `00a` / `00a1` / `00a2` (new Q1 + answers) and `00f3` (new A3c). All anchor links in TOC lines updated.
- **v11.13** — Strips the inline TOC `.cb-frame-lead` paragraph from all three Question sections (Q1, Q2, Q3). The answers naturally follow in their own sibling sections below, so the explicit "Answer Na — slot, Answer Nb — slot..." pointer was redundant chrome. Question sections are now lean: just the corner label, the H2 with kicker + the question itself, nothing else. Each Question reads as a single beat that opens its arc; the Answer sections below do the rest.
- **v11.14** — Three changes. (1) **Question 3 title tightened**: *"How do you keep track of which version of an artifact you're working with?"* → *"How do you keep track of which version of an HTML file you're working on?"* — more concrete subject (HTML file, not generic artifact), more direct phrasing. (2) **Observation 3 gains a middle paragraph** about chat-hosted artifacts: Claude's artifacts, ChatGPT's canvas — they don't have a natural versioning system, the artifact mutates in place as you iterate, forking into a new conversation doesn't inherit a clean version label or a "this is v3" anchor; the chat keeps going and the artifact loses its history. Sits between the existing PDF-v1/v2/final analogy paragraph and the "identity and lineage are addressable" closing paragraph. (3) **NEW Observation 5** (`00h`, white) added after Observation 4 and before the hero gallery: *"There's no easy way to get chat-hosted content out of an LLM platform."* Three prose paragraphs — share links exist on every platform but are platform-locked viewing artifacts, not portable; cross-platform interop is poor (a ChatGPT share link handed to Claude doesn't compose: the receiving LLM might fetch and read the URL but doesn't get the structured conversation); the file-as-artifact discipline (Obs 1, Obs 2, Answer 1b cross-linked) is the project's response — a Capsule opens in any browser, can be handed to any LLM, the host doesn't need to be in the loop. *"That's the practical difference between 'I shared a link' and 'I shared a file.'"*
- **v11.14.1** — Answer 1b retitled: `Paste the Capsule Core spec into your prompt.` → `Ask the LLM for a Capsule (according to the Spec).` Sharper phrasing — focuses on the *action* the producer takes (asking for a Capsule) rather than the *implementation detail* (pasting the spec text). The body of Answer 1b already opened with "Instead of asking for HTML, ask for a Capsule…", so the new title aligns with the body's framing. Slot-tag eyebrow updated to match: `Contract-based approach · paste the Core spec` → `Contract-based approach · ask for a Capsule`. Link target unchanged (still CAPSULE_CORE.md; link text shortened "Core spec" → "Spec").
- **v11.15** — Sharpens the **HTML version-control arc** (Observation 3 → Question 3 → Answers 3a/3b/3c) per two converging external reviews. **Observation 3 retitled** *"HTML diffs are noisy. Lineage is the bigger problem."* and rewritten around the explicit three-layer framing (raw diff / semantic diff / lineage), rendered as an ordered list. Opens with the runtime-vs-writing-format explanation (*"Raw HTML diffs are noisy because HTML is closer to a runtime artifact than a writing format"*) — explains *why* diffs are noisy, not just that they are. PDF v1/v2/final analogy and chat-hosted-artifacts paragraph preserved. Closes on *"Capsule doesn't claim raw HTML diffs become pleasant. It claims artifacts need identity and lineage first."* **Answer 3b gains a closing punchline**: *"**Git** tracks files. **Capsule** tracks artifacts."* (mono accent on the subjects). **Answer 3c rewritten** with a new opener punchline *"The HTML **is the artifact**. The manifest **is the review surface**."* followed by an 8-row review-surfaces table (Raw HTML / Manifest / Content / Data / Style / Asset / Render / Runtime diff) replacing the prior single-paragraph block description. Adds **Asset diff** (images, fonts, media by hash) and **Render diff** (screenshot or DOM snapshot before/after) — two surfaces that weren't in the prior treatment. Example-output code block preserved. Closing "layer on the spec, not a spec change" framing kept. New CSS: `.cb-frame-list` (ordered list for the three-layer breakdown), `.cb-frame-punchline` (the two slogan lines, accent-bold on the contrasting noun), `.cb-diff-table` (8-row review-surfaces table with mono accent column headers and tight mobile breakpoint). Three new manifest field ideas raised by the external review (`supersedes`, `derived_from`, `change_summary`) are NOT added to the spec; parked in spec Appendix E pending real-producer empirical pressure.

### Changed — PRECEDENTS.md

- "Current voices in HTML-for-AI" section grown from 2 voices (Thariq, Blake) to 7 voices spanning format, hosting, discovery, and live-editing layers — Karpathy, Steph Ango, Utkarsh / htmlbin, Jeremy Howard / llms.txt, Raunaq / html-docs.com, Matan / Workplane added.
- Position picture: original three-position table → nine-row layered table organized by lifecycle slot (format / live editing / hosting / discovery).

### Changed — Notes essay

- **Notes v1.1.0** (2026-05-20) — added Obsidian + "File over app" paragraphs after the share-link discontent paragraph (`4efb95a`).
- **Notes v1.2.0** (2026-05-21) — byline updated from "B. F. Garden" placeholder to "Luke Schuss · lukeschuss.com" (linked); data block byline updated to match; description records the attribution change.

### Fixed

- Stale `§11 hosting discussion` cross-reference in Appendix E.7 corrected to point at Appendix B (`3068a3b`).

### Resolved (moved out of parked-items)

- **Appendix E.5** — Rule 12 vs. legacy compiler templates: resolved via the image-fallback carve-out in §2.3 (`9bdb2db`).

---

## [Spec v0.3.3] — 2026-05-20

Size cap raised; image-fallback carve-out for visualization geometry shipped; first major external feedback signal (F19 Claude Design experiment, plus F20 Mintel validation) folded in.

### Changed — spec

- **§6.3 Size limits**: hard cap 15 MB → 20 MB; new 15-20 MB soft-warn tier for email-attachment compatibility (`9bdb2db`).
- **§14 Validation list**: item 11 (file size) updated to reflect new cap + soft warn (`9bdb2db`).
- **§16.2 Out of scope**: boundary mention updated (`9bdb2db`).
- **CAPSULE_CORE.md** cap mention updated to point at the new constraint (`9bdb2db`).

### Changed — validator

- **`compiler/validate.py`**: `MAX_FILE_SIZE` raised from 15 to 20 MB; `SOFT_WARN_SIZE` constant added at 15 MB; file-size check emits a contextual note when the body is between 15-20 MB (`9bdb2db`).

### Added — RESEARCH

- **F20** writeup: first publicly-fetchable Mintel production capsule; integrity hash verifies; MinDev hosting-pattern headers documented; image-fallback carve-out motivated.
- F5 conclusion appended with "Updated by F20" addendum tying the size-cap change to the empirical finding.

---

## [Spec v0.3.2] and earlier — 2026-05-19

Initial public release of `bigfancygarden/htmlcapsule` to the world. Project work had been ongoing privately before this; the May-19 commits are the cleanup-and-publish phase.

### Initial release contents

- **Core spec v0.3.0** (`CAPSULE_CORE.md`): twelve numbered rules, designed to paste into an LLM prompt.
- **Full spec v0.3.2** (`spec/CAPSULE_SPEC.md`): implementer-grade definition; integrity-hash recipe with normative test vector; security model; response protocol; Appendix E with parked v0.4+ candidates.
- **Domain schemas** (`spec/DOMAIN_CAPSULES.md`): `domain.implementation_notes`, `domain.design_system`, `domain.exploration_map`, `domain.briefing`.
- **Reference implementation**: `compiler/compile.py` (compiles JSON + template directories → capsule HTML); `compiler/validate.py` with 25 conformance checks initially.
- **Templates**: `templates/decision_board`, `templates/news_capsule`.
- **Examples**: `spec/examples/briefing_example.html`, `spec/examples/implementation_notes_example.html`.
- **Research log**: `RESEARCH.md` with findings F1-F18, methodology, open questions, recurring failure modes.
- **Companion docs**: `GLOSSARY.md`, `PRECEDENTS.md`.
- **Initial landing page** at htmlcapsule.org (multiple visual iterations between May 19 and May 20 from editorial to terminal to bright to essay to layered).

### Post-release v0.3.2-era patches (still pre-v0.3.3)

- **F19** added (2026-05-19/20): Claude Design integration experiment + design-tool theme files cataloged (`b70f58a`, `6f0148b`).
- **Validator 26th check** added (`4696367`): recognizes the cleaner `data-capsule-action="<cap>"` + `<cap>: function` Rule 7 verification convention surfaced by external producers; no spec change.
- **README expansion** clarifying capsules ≠ PKM after independent reader confusion (`8c83a99`).
- **Landing v7.0.0 → v7.1.0** repositioning + "PDF of the interactive web" tagline.
- **Appendix E.8** parked for validator refinement of non-resource-loading `<link>` tags (`566b046`).

---

## Notes essay

Parallel versioning. Tracked here only at major beats.

- **v1.0.0** — 2026-05-20 — split from landing v10.0 (essay-as-landing experiment) into its own capsule (UUID `c5f6a890`); `parents[]` records lineage to landing UUID `7d1a1ac8`.
- **v1.1.0** — 2026-05-20 — added Obsidian + "File over app" paragraphs.

---

## How this changelog is maintained

Updated when each spec version ships (v0.3.x patches; future v0.4+ minor releases). Landing version bumps tracked at major revs (v8, v9, v10); intermediate landing changes (e.g. v10.4 → v10.5 → v10.6) appear under the corresponding spec-version section. Notes essay versions tracked when they ship. Voices archive entries tracked when added. Idea-queue movements not tracked here unless something graduates to "Initial domains" or gets formally dismissed — the queue files (`voices/README.md`, `spec/DOMAIN_CAPSULES.md`) carry their own state.

When in doubt: a change earns a CHANGELOG entry if a future reader (including future-you) would want to find it without scrubbing git log. Internal copy-tweaks, small cleanups, and prose iterations don't necessarily.
