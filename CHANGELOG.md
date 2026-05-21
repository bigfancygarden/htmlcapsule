# Changelog

All notable changes to the htmlcapsule project — spec, reference implementation, landing page, voices archive, and research record. The full-spec version (e.g. `v0.3.4`) is the load-bearing identifier; the Core spec version (`v0.3.0`) bumps only for normative rule changes; landing / notes / voices versions move independently and are tracked here only at major revs or when they coincide with spec work.

Format follows [Keep a Changelog](https://keepachangelog.com/) loosely. Commit IDs in parentheses for cross-reference.

---

## [Unreleased]

Nothing pending. Idea queue (`spec/DOMAIN_CAPSULES.md`) and voices queue (`voices/README.md`) hold candidates that haven't met the empirical-pressure bar.

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
