# The Artifact Channel Study — getting our data out of proprietary hosting, complete and verifiable

**Date:** 2026-07-26 · **Status:** Active design study (the F41–F46 arc, synthesized) · **Companion finding:** F46 in RESEARCH.md

The question this study answers: **how do we get work that lives in a proprietary artifact host — today, concretely, Claude's artifact channel — into an offline format that is open, complete, and verifiable?** And its inversion, which turns out to be the stronger move: **how do we publish through such channels without ever surrendering the trust layer in the first place?**

## 0. The point, tightened

**What we want:** an open-source alternative to Claude's artifact hosting — because we don't trust it to stick around, and, more to the point, **we cannot tell whether it will.**

The second clause is the real problem, and it is worth separating from the first. "It might disappear" is a complaint about a vendor. "I cannot determine whether it will" is a complaint about a *structure*, and it is the one that holds.

Claude Artifacts is a **host, not a registry** — F24's distinction, observed at population scale in F41. It stores your work, versions it, renders it, and serves it at a durable-looking URL. But every one of those turns out to be an administrative setting rather than a commitment: retention is configurable by an organization owner; public sharing can be revoked globally without touching any artifact; versioning is host database state that the document itself does not carry; and on team plans even *export* is a permission somebody else holds (F48). Meanwhile the artifact carries no identity, no provenance, and no integrity, and there is **no published format specification of any kind** — so there is nothing to hold anyone to, and nothing in the file that would survive the host.

So the honest statement of the risk is not "this might go away." It is: **there is no commitment to reason about — only settings you do not control.** That is not untrustworthiness; it is *illegibility*. You cannot form a justified belief about the durability of your own work in either direction. Note that this survives even the friendliest possible reading of the vendor's intentions, which is exactly why it is worth building against: no one has to behave badly for you to lose.

**The alternative is not a better host.** A more trustworthy place to put artifacts just relocates the same question. The alternative is to make the artifact **not need one**: identity it carries itself (UUID plus a content hash anyone can recompute), provenance it carries itself (generator, source, `parents[]`, `derived_from[]`), integrity verifiable offline by a stranger with no dependency on us, and rendering that requires nothing but a browser because the file *is* the viewer. Then durability stops being a property of someone's policy and becomes **a property of the bytes**, and a host demotes from load-bearing infrastructure to a convenience you can walk away from.

**And the alternative already exists — it has just never been assembled under one name.** Every column below is built and in production use across the fleet:

| Capability | How the artifact host provides it | Open equivalent, already built |
|---|---|---|
| Creation | the model emits HTML into the product | any LLM given `CAPSULE_CORE.md` — four model families verified (F1, F19, F25, F30) |
| Storage | host database | htmlvault: content-addressed, on your own disk |
| Versioning | a database row the file knows nothing about | `capsule_version` + the `parents[]` chain, inside the file |
| Sharing | a link revocable by global toggle | mindev share tokens with logged delivery — or just sending the file |
| Rendering | host-injected frame runtime | the capsule renders itself, offline, indefinitely |
| Integrity | none | content hash, recomputable in any browser (`tools/validator.html`) |
| Provenance | none | the manifest: generator, source, parents, derived_from |

One sentence, for the launch: **Claude Artifacts, except the artifact is yours** — it carries its own identity, provenance, and integrity, renders anywhere with no runtime, and outlives any host, including ours.

## 1. Where the two projects stand

**htmlcapsule (the format)** is at full-spec v0.3.13, Core v0.3.0. The envelope is production-proven across nine named domains and three producer kinds; the newest additions are exactly the machinery this study needs: `sealed_sources` (v0.3.10 — the capsule carries its resolved data), the two-track version story and float-hardened hash recipe (v0.3.11), the annotation layer over digest-pinned bases (v0.3.12), and id-addressed block placement (v0.3.13, from this study's probe). The reference validator runs 30–32 checks, is version-identified, and gates three consuming repos' CI. Known weak points, per F44/F45: the §9.1.1 hash exists only in Python, there is no conformance suite non-Python implementations actually run, and the repo itself has no tests or CI.

**htmlvault (the custody layer)** is the local-first vault and registry: `import → quarantine → scan → validate → hash → preview → sign → publish`, content-addressed object store, sidecar records, Rust + Swift verifiers, an MCP write-only inbox, and a real production custody run behind it (the TOM-04 flagship: digest-pinned, seal-verified, fsck-clean). Its designed-but-unbuilt pieces are exactly what a recovery pipeline lands on: idempotent sync intake (F-CC1/2), policy-gated promotion (F-CC3), source-metadata capture (F-CC4), and ssh-key custody signing (all costed in Bridge: `htmlvault/continuous-custody-review`).

Together they already form the back half of a recovery pipeline. What's been missing is the front half: a contract with the place the work actually lives.

## 2. The artifact channel, measured (primary evidence, 2026-07-26)

We published a valid capsule *as* a Claude artifact and fetched back the served document (owner-authenticated raw fetch). The served anatomy:

- **Host-owned head.** `<!doctype html><html><head>` with an injected **frame-runtime**: a `window.claude` capability proxy driven by a `__FRAME_PREAMBLE` (per-capability module names), dynamic `import("/_runtime/…")` module loads, a WebRTC lockdown, theme stamping (`data-theme` via postMessage from the shell), scroll restoration, resize/engagement telemetry, and cross-origin navigation brokering to the parent shell. Plus injected `<meta charset>`, viewport, and a small reset stylesheet.
- **Author-owned body, byte-preserved.** Our five capsule blocks — manifest JSON, data JSON (including `sealed_sources` payloads), style, root, runtime, and even a trailing HTML comment — came back **byte-true**.
- **Everything else is host database state.** Title, description, favicon, version history, sharing scope, retention: none of it is in the file (confirming F41). The one CSP exception (MCP connector calls) binds the page to the *viewer's* account — anti-portable by construction.
- **Access is session-gated.** The raw document is fetchable by the owner in an authenticated context; there is no unauthenticated raw endpoint for private artifacts. This is *why* the extractor ecosystem lives inside the browser.

## 3. The extractor ecosystem, measured

The de-facto export path (F42, source-verified for `claude-artifacts-downloader`): a Chrome extension that reads the **conversation UUID from the URL**, pulls **chat data from browser localStorage**, walks messages from the most recent root, **regexes artifact content out of message text**, and zips it. Consequences worth stating precisely:

1. **Extractors read the conversation stream, not the artifact page.** They recover *authored* content (pre-wrapper) — a different surface than fetching the served artifact (wrapped). Both converge after block extraction, because capsule integrity is canonical, not positional.
2. **They are brittle by construction** — regex over an undocumented internal message shape, current-conversation scope only, no version history, no metadata. Every host-side shape change breaks every tool.
3. **They emit bare files with zero provenance.** The ZIP knows nothing about where a document came from, which version it was, or whether it arrived intact. This is exactly the gap between *export* and *custody*.

## 4. The experiment, and what it proved (F46)

Round trip: **capsule → artifact channel → recovery → verification.**

| Step | Result |
|---|---|
| Body-only capsule (five blocks, no head placement) validates locally | 30/30 strict — blocks are id-addressed (now explicit in §2.1) |
| Published via the artifact tool; served document fetched back | Blocks byte-preserved inside the host wrapper |
| `data+manifest` hash recomputed from recovered blocks | **Bit-identical to the declared hash** — the trust surface survived the channel |
| Served document validated as-a-capsule | Correctly **fails** (wrapper's dynamic `import()` breaks Rule 2) — the frame is projection, not truth |
| Extract-by-id + minimal rewrap | **30/30 strict**, original hash verifies |

The design lesson: `hash_scope: "data+manifest"` — chosen in v0.3.2 for browser re-save, hardened in F34 as truth-vs-projection — turns out to be a **channel-survival property**. A capsule's verifiable identity tunnels through a proprietary host that re-wraps, re-frames, and re-themes the document, because the host only touches projection. The host is a projection; custody is the truth.

## 5. The gap matrix

| Property | Claude artifact (as served) | Capsule | + Vault custody |
|---|---|---|---|
| Self-contained render | ✅ (CSP-enforced) | ✅ (Rule 1/2) | ✅ |
| Identity in the file | ❌ (host DB) | ✅ uuid + content_hash | ✅ + object digest |
| Provenance | ❌ | ✅ generator/source/parents/derived_from | ✅ + custody events |
| Integrity | ❌ | ✅ §9.1.1, scope-labeled | ✅ independently re-verified |
| Versioning | host DB, revocable | `capsule_version` + parents chain in-file | ✅ + records per version |
| Export contract | none (scrapers) | `download_capsule` + extract-by-id | export = the bytes |
| Survives the host's death | ❌ | ✅ | ✅ |

## 6. Direction — research, spec, tools

**Research (next probes):**
- **R1 — version tunneling:** republish the probe N times; does each host-side version preserve blocks, and can all versions be recovered? (The Compliance API and version picker suggest yes for owners.)
- **R2 — the conversation-JSON shape:** document the localStorage/message schema the extractor population depends on — the de-facto export API — so our tooling reads it once, correctly, instead of five tools regexing it badly.
- **R3 — other channels:** the same tunneling probe against Codex Sites (F32), htmlbin, and email attachments. Hypothesis: any channel that preserves body HTML tunnels capsules.

**Spec (small, mostly done in v0.3.13):**
- **S1 ✅** Id-addressed placement + tunneling/recovery contract (§2.1, this revision). Recovery MUST NOT mutate blocks; recovery provenance lives in custody records, not the artifact.
- **S2** The F44 carry-over: operational number-formatting rules + a language-neutral conformance fixture file (vectors A and B). Prerequisite for T1.
- **S3** When R2 lands: a documented *conversation-recovery* profile for artifacts that were never capsules — what a converter records in `derived_from` (conversation UUID, artifact id/version, extraction time, method).

**Tools (the build order, each unblocking the next):**
- **T1 — the JS/WASM §9.1.1 port** (F45's ~150 lines, written against Vectors A+B). It's the single blocker: in-browser hashing is what lets verification happen *where the extraction happens*.
- **T2 — the recovery adapter, two modes:** (a) *tunneled mode* — extract five blocks by id, rewrap, verify (≈50 lines, proven above); (b) *wrap mode* (F43) — take a bare conformant-substrate artifact and add the missing envelope: manifest with honest defaults, the three ids, a runtime for declared exports, T1's hash.
- **T3 — the provenance-preserving extractor:** the browser extension the scraper ecosystem proves demand for, but emitting capsules instead of bare ZIPs — reads the conversation stream (R2), runs T2, verifies with T1, and hands the result to **htmlvault's MCP inbox** (`receive_html` → quarantine). Recovery provenance goes in the custody record per S1.
- **T4 — vault side:** the already-costed continuous-custody items (idempotent intake, promote policy, source metadata) — T3's landing zone.

**The strategic line.** Two motions, one destination: *publish through* proprietary channels with the envelope intact (tunneling — the host becomes irrelevant to trust), and *recover into* the envelope what was published bare (adapter — the missing utility F43 measured). Both terminate in vault custody, which is where "our data, offline, open, complete" becomes an operational fact instead of an aspiration.
