# /voices/ — primary-source voices in the htmlcapsule project

This directory holds primary-source statements from named precedents and adjacent voices, archived as their own Capsule artifacts. Each archive includes verbatim quotes, attribution, archive metadata, commentary on the relevance to Capsule, and related links. The first entry was Karpathy (2026-05-20); subsequent entries follow the same shape.

Two lists below: voices that have been archived, and voices that have been flagged for review but not yet archived. Items move from "Queue" to "Archived" when a `voices/<slug>.html` capsule is written for them. Items can also be dismissed from the queue if review concludes they're not worth archiving as their own capsule — when that happens, leave them in the queue with a struck-through note so the dismissal reason persists.

## Archived

| File | Voice | Topic | Archived |
|---|---|---|---|
| [`karpathy-html-progression-2026.html`](karpathy-html-progression-2026.html) | Andrej Karpathy | HTML as the current best default for LLM output (four-step progression + "structure your response as HTML" tip + LLM wiki gist) | 2026-05-20 |
| [`utsengar-htmlbin-2026.html`](utsengar-htmlbin-2026.html) | Utkarsh Sengar | htmlbin.dev — agent-first HTML hosting (independent convergence with the MinDev hosting pattern; the hosting-layer voice) | 2026-05-21 |

## Queue (flagged for review)

| Source | Flagged by | Flagged date | Notes |
|---|---|---|---|
| [Ryan Carson tweet 2052857429373673482](https://x.com/ryancarson/status/2052857429373673482) | user | 2026-05-21 | Ryan Carson is one of three named endorsers on the html-docs.com homepage (alongside Karpathy and Thariq, both already archived). 4× founder, prior Treehouse / Carsonified / etc. Worth reading the actual tweet to see whether his angle on the html-docs / agent-workflow space adds something to the position picture beyond what html-docs.com's homepage already says. If yes — likely candidate for an archive entry. If no — note the dismissal reason and leave in the queue. |
| Workplane (Matan / matanrak) deeper attribution | system | 2026-05-21 | Workplane was added to landing voices + PRECEDENTS + F22 with attribution via GitHub commit history (Matan, handle `matanrak`, based in Israel, no Twitter linked on profile). No personal site, no Twitter, no LinkedIn surfaced. The workplane.co homepage carries no creator info. If Matan ever publishes a launch post or LinkedIn surface attribution, update the PRECEDENTS entry. Also flagged: the homepage links to `github.com/work-plane/workplane` which 404s; only `/workplane-skills` exists. Either a footer typo or the main repo is private. Worth re-checking quarterly. |

## How a voice graduates from the queue to the archive

A queued voice becomes archive-worthy when *either* of:

1. **It introduces a position the picture doesn't already have.** Examples that earned slots: Karpathy (substrate progression + LLM wiki — neither was named by Thariq or Blake before him); Utkarsh / htmlbin (hosting layer — first articulation of that slot); Jeremy Howard / llms.txt (discovery layer — first articulation of that slot); Raunaq / html-docs.com (live editing layer — first articulation of that slot).
2. **It provides load-bearing empirical evidence** (a production capsule, a documented adoption, an independent convergence with an existing pattern). Example: the F20 Mintel production capsule was archivable territory; the F21 MinDev + htmlbin convergence was archivable territory.

Voices that *just amplify* an existing position without adding a new slot or new evidence are queue candidates but lower-priority archive candidates. They can still be named in PRECEDENTS.md's "Current voices in HTML-for-AI" section without earning a full archive capsule.

## File shape

Each archive capsule follows the structure established by [`karpathy-html-progression-2026.html`](karpathy-html-progression-2026.html):

- `type: "quote_archive"` in the manifest
- `parents[]` recording the lineage to the landing UUID
- `source.origin: "external_quote"`
- `generator.kind: "hybrid"` (human-authored with AI assistance)
- Manifest description naming why this voice is in the archive
- Data block: `attribution` + `archive` + `quote_paragraphs[]` + `commentary` + `related_links[]` + `not_this` disclaimer
- Visible body: title block, attribution dl, blue-left-border quote block, commentary section, related-links aside, about/exports details, footer
- Footer disclaimer: "not an endorsement and not a co-sign"

New archives should match this shape unless there's a specific reason to diverge.
