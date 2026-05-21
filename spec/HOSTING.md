# Capsule — Hosting Pattern

**Status:** Descriptive, not normative. As of v0.3.4 (2026-05-21), two independent hosts ([MinDev](https://mindev.ca) and [htmlbin.dev](https://htmlbin.dev)) have converged on the shape described below without coordinating with each other or with the Capsule project. This document records that convention so future hosts can adopt it consciously rather than re-derive it. See [`RESEARCH.md` F21](../RESEARCH.md) for the empirical writeup.

The Capsule format is hosting-agnostic by construction. A valid capsule works without any host — it travels as a `.html` file across email, AirDrop, USB, cloud storage, and a recipient's local disk. Hosts are optional: they exist to give a capsule a public URL with a stable identity and to attest, in their own voice, that the bytes they served match the bytes they were given. Nothing in the format requires a host; everything in the format is compatible with one.

This document is a description of what hosts that serve capsules well actually do. It is not a contract producers can rely on; it is a pattern recipients and host implementers can use.

## The observed pattern

| Element | What hosts do | Why it works |
|---|---|---|
| **Short URL identity** | Each capsule gets a stable URL with a compact identifier — UUID (MinDev), random slug (htmlbin), or whatever the host's namespace prefers. | Capsules need a public address that travels via copy-paste, in messages, in citations. UUIDs and slugs are both fine; the discipline is *stable* (the URL never moves) and *compact* (people can share it). |
| **`/raw` byte-identical endpoint** | A second path returns the exact bytes the host received, with no chrome, no modifications, no transformations. MinDev: `/api/c/{uuid}/raw`. htmlbin: `/p/{slug}/raw`. | Recipients (and validators) need a way to fetch the canonical bytes for verification or re-distribution. The "primary" URL may add navigation chrome for browser viewing; the `/raw` URL is the audit path. |
| **Minimal host chrome** | The capsule's own content fills the viewport. The host's UI recedes — a small mark, a footer attribution, a side rail. It never modifies the body. | The host serves the capsule; it doesn't reframe it. A recipient should be able to tell at a glance that what they're looking at is the capsule's own rendering, not the host's repackaging of it. |
| **Honest authorship attribution** | The host says, in its own voice, who uploaded the bytes and when — without claiming to be the author. htmlbin's footer: *"content authored by the agent that uploaded it."* MinDev's response headers: `x-capsule-content-hash`, `x-capsule-uuid`. | Hosts have information producers don't have (upload time, IP, account) and lack information producers do have (generator identity, source provenance). Hosts attest to what they know; the capsule's manifest carries the rest. The two layers stay distinct. |
| **No content mutation** | The host serves the bytes byte-identically. No re-rendering, no minification, no injection, no analytics tags, no rewrites. | The capsule's integrity hash (when present) is computed over the bytes the producer sealed. Any host modification breaks that hash and breaks the trust signal. A host that modifies bytes is no longer hosting the capsule; it's serving a derived object. |

## Optional but recommended: integrity attestation via response headers

MinDev demonstrates this; htmlbin does not (yet). The pattern is small and additive:

```http
HTTP/2 200
content-type: text/html; charset=utf-8
content-length: 13734133
x-capsule-content-hash: sha256:60282cbdad54708f630f516a3b4534fe1f1063ebe670d5c79f0ee2e70eaf0e36
x-capsule-uuid: 9357a933-7ce1-4061-9488-2ca61d81bded
```

What the headers mean:

- **`x-capsule-content-hash`** — the host's independent computation of the capsule's content hash (per the recipe in [§9.1.1 of the spec](CAPSULE_SPEC.md)). A recipient or validator can recompute the same hash from the body and confirm the host didn't modify the bytes.
- **`x-capsule-uuid`** — the host's parsing of the capsule's `manifest.uuid`. Surfaces the canonical identifier at the HTTP layer so tools that don't parse the body can still route on identity.

**These headers are the host attesting to what the host computed.** They are *not* a signature from the original author — that requires the signing layer parked in [Appendix E.6](CAPSULE_SPEC.md#e6-author-signing--transparency-log-sigstore-shaped). What the headers do guarantee: if the host's `x-capsule-content-hash` matches what the recipient recomputes from the body, the host did not modify the bytes in transit.

A host that doesn't include these headers is still a valid host of the pattern — it just provides one less independent verification. A host that includes them and serves bytes that don't match earns the recipient's mistrust.

## Anti-patterns — what hosts of capsules should not do

| Anti-pattern | Why it breaks the pattern |
|---|---|
| **Modify the body** (re-render, minify, inject scripts, add analytics) | Breaks the integrity hash. The host is no longer serving the capsule; it's serving a derived object that lies about its provenance. |
| **Fail to provide a byte-identical fetch path** | Recipients can't verify what they received. The host becomes opaque. |
| **Maximalist chrome** that obscures the capsule's body | The recipient can't tell what's the capsule and what's the host. Authorship attribution gets muddled. |
| **Attest to things the host doesn't know** (e.g., "verified author" without a signing infrastructure) | Hosts can attest only to what they can compute from the bytes they received and the metadata they collected at upload. Anything else is overclaim. |
| **Require host-side execution to view the capsule** (e.g., server-side rendering of the manifest, JS proxies) | Capsules are supposed to work on `file://`. If the host's rendering is required, you've lost the format's portability. |
| **Lock the capsule to the host** (no `/raw` path, no download button, no way to leave) | Capsule rule 10 — "cannot be unshared" — implies recipients can take the bytes with them. A host that prevents this breaks the format's contract with recipients, not with producers. |

## Two reference implementations

**[MinDev](https://mindev.ca)** — private, single-tenant. Hosts capsules produced by [Mintel](../GLOSSARY.md), an industry-tied mining-intelligence system. Validates each capsule against the spec on upload; rejects on mismatch. Per-recipient share tokens (each token a watermark; bytes identical across recipients, access path distinct). Fetch logging (who, when, IP, UA, via which token). Lineage resolution via `parents[]`. Recedes UI to a small rail when displaying — the capsule fills the viewport. Documented as the canonical example of the hosting pattern in [Appendix E.7 of the spec](CAPSULE_SPEC.md#e7-password-protected-encrypted-capsules) ("the MinDev pattern: hosting-platform auth gates control delivery; the capsule itself doesn't gate its internal contents").

**[htmlbin.dev](https://htmlbin.dev)** — public, multi-tenant, agent-first. *"API for agents to share HTML. One human auth step, then your agent publishes over HTTP."* Cloudflare D1 + KV stack. Doesn't impose Capsule format discipline — accepts any self-contained HTML. Adds a small header (`[htmlbin]` mark) and footer (`hosted by htmlbin — content authored by the agent that uploaded it`). Exposes `/p/{slug}/raw` for byte-identical fetch. Documented in [PRECEDENTS.md](../PRECEDENTS.md) "Current voices in HTML-for-AI" and archived as a voice in [`voices/utsengar-htmlbin-2026.html`](../voices/utsengar-htmlbin-2026.html).

The two have very different audiences (industry-tied vs. agent-public), very different feature sets (per-recipient tokens + ACLs vs. open-publish flow), and very different attestation depth (response-header content-hash vs. footer attribution only). They converged on the *shape* anyway. That convergence is what this document records.

## How recipients verify a hosted capsule

```bash
# Fetch via the /raw endpoint (NOT the primary URL — the primary may include host chrome)
curl -O https://mindev.ca/api/c/9357a933-7ce1-4061-9488-2ca61d81bded/raw

# Validate locally
python3 compiler/validate.py raw

# Or, as of v0.3.4, point the validator directly at the URL — it fetches via /raw,
# captures the response headers, and cross-checks any x-capsule-* attestations against
# the body before running the standard 26 checks:
python3 compiler/validate.py https://mindev.ca/api/c/9357a933-7ce1-4061-9488-2ca61d81bded/raw
```

The validator's URL mode reports any `x-capsule-content-hash` and `x-capsule-uuid` headers the host included, cross-checks them against the body's manifest, and surfaces any mismatch — turning the host's attestation into a verifiable claim rather than a trust-me string.

## Why this document is descriptive, not normative

Two implementations is convergence. It's not yet a standard. Formalizing the pattern as a normative spec would require more host implementations to agree on protocol particulars (header names, slug format conventions, error response shapes, token semantics) — and that needs outreach and adoption pressure the project hasn't yet sought.

The reasonable middle path: document the pattern as observed, point future host implementers at it, let third-party implementations either align voluntarily or diverge consciously. If a third or fourth independent implementation appears and stays compatible with this pattern, the case for normative codification gets stronger. Until then: descriptive.

## Open questions

- **Header naming convergence.** MinDev uses `x-capsule-content-hash` / `x-capsule-uuid`. Are these the right names? RFC 6648 deprecates the `x-` prefix; future formalization might prefer `Capsule-Content-Hash` / `Capsule-UUID`. No urgency.
- **Slug format conventions.** UUID vs. random slug vs. content-addressable hash — which does the recipient prefer? Probably all of the above for different use cases. No move yet.
- **Error attestation.** What should a host return when a capsule fails validation on upload? Or when serving a capsule that has been tampered with after upload? No convention yet.
- **Multi-version serving.** When a capsule is updated (new `capsule_version`, same `uuid`), should the URL return the latest or pin to the version at the time of share? MinDev pins per-token; htmlbin pins per-publish. Different choices; both defensible. No convention yet.
- **Signing/transparency layer interaction.** When [E.6](CAPSULE_SPEC.md#e6-author-signing--transparency-log-sigstore-shaped) eventually ships, hosts will likely want to surface signature verification in additional headers. Pattern not yet observed because the layer doesn't exist yet.

## Adoption

If you're building a host that serves capsules, the minimal recommended shape:

1. **Identity:** assign a stable short URL per capsule. UUID (from `manifest.uuid`) or slug is fine.
2. **Raw endpoint:** expose `/raw` (or equivalent) that returns the byte-identical body, no chrome, `Content-Type: text/html; charset=utf-8`.
3. **Chrome:** minimal. The capsule's body is the foreground; the host's UI is a small mark and footer attribution. Never inject into the body.
4. **Attestation (optional but recommended):** include `x-capsule-content-hash` and `x-capsule-uuid` headers in responses to `/raw`. Compute the content hash per [§9.1.1](CAPSULE_SPEC.md). Lets recipients verify your hosting integrity.
5. **No mutation:** serve the bytes you received. If you need to change them, you're building a different kind of service.
6. **Honest authorship:** if you know who uploaded, say so in your voice (footer, response header, whatever fits). Never claim to be the author.
7. **Discoverability (recommended):** publish an [`/llms.txt`](https://llmstxt.org/) at the host's root that indexes the capsules you serve. The llms.txt proposal (Jeremy Howard, fast.ai / Answer.AI, September 2024; adopted as a Chrome Lighthouse audit) is the emerging convention for "give LLMs a curated, machine-readable map of this site's content." A hosting layer that exposes capsules but is invisible to LLM crawlers wastes most of the discoverability upside; an `llms.txt` listing each hosted capsule (with title, short description, and the `/raw` URL) closes that gap with ~zero ongoing maintenance cost. The htmlcapsule project's own site has [one](https://htmlcapsule.org/llms.txt) as a reference shape.

That's the whole pattern. Two independent hosts arrived at it by 2026-05-21; the bar for the third should be lower.
