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

### Changed — landing page (v10.2 through v10.11)

Eight landing iterations during this version window. Highlights:

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

### Changed — PRECEDENTS.md

- "Current voices in HTML-for-AI" section grown from 2 voices (Thariq, Blake) to 7 voices spanning format, hosting, discovery, and live-editing layers — Karpathy, Steph Ango, Utkarsh / htmlbin, Jeremy Howard / llms.txt, Raunaq / html-docs.com, Matan / Workplane added.
- Position picture: original three-position table → nine-row layered table organized by lifecycle slot (format / live editing / hosting / discovery).

### Changed — Notes essay

- **Notes v1.1.0** (2026-05-20) — added Obsidian + "File over app" paragraphs after the share-link discontent paragraph (`4efb95a`).

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
