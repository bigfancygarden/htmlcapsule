# The Registry Study — a registry is a format, not a service

**Date:** 2026-07-27 · **Status:** Design study with a working prototype; precedes a normative `spec/REGISTRY.md` · **Companion finding:** F49 in RESEARCH.md · **Lineage:** F24 → HOSTING.md compliance sketch → F41/F48 (the host-level problem) → this study

The question: **what should htmlvault.app be, as the registry for capsules?** The candidate answer arrived by analogy — copy the fleet's Astro + Pages Functions + D1 pattern and build a web application. This study argues for a different shape, verifies the prior art that shape rests on, and proves the load-bearing claims with a working prototype.

## 1. What a registry is, per this project's own record

[F24](../RESEARCH.md) drew the line: a **host** serves bytes; a **registry** publishes *commitments* — the bytes stay reachable, indexed by digest, immutable, attested. [`spec/HOSTING.md`](../spec/HOSTING.md) then sketched **Registry Compliance v1**: a contract a host *declares* — permanent `/raw`, attestation headers, visibility commitments, no mutation. And htmlvault's continuous-custody review (Bridge: `htmlvault/continuous-custody-review`) said what registry should *eventually* mean: *"a second custody node that pulls the mirror and runs `verify` independently — two machines independently attesting the same digests."*

Read together, these already contain the conclusion. The compliance sketch defines a registry by its **behavior** — which a user must take on faith, because behavior is a promise about the future. The custody review defines it by its **contents** — a mirror anyone can re-verify. The second definition subsumes most of the first: if the registry's contents are a portable, verifiable structure, then immutability, integrity, and identity stop being promises and become **checks**. The only commitment left that must be taken on faith is *availability* — and that one can never be verified in advance by anyone, about anything.

## 2. Why not a web application

The app path (Astro + Functions + D1 + R2, per the proven 1730 pattern) is buildable this week. It is still the wrong *primary* shape, for reasons that are this project's own findings applied to itself:

1. **It would be the fourth implementation of artifact records** (vault sidecars, mindev Postgres, the app's D1) — and F44/F47 measured exactly what independent reimplementations of the same semantics cost.
2. **It re-creates the thing the project critiques.** F41/F48 diagnosed the proprietary artifact host: durability as administrative settings, a database the file knows nothing about, export that isn't portability. An app with its own schema, auth, and availability is that diagnosis with our logo on it. The pitch is *"durability is a property of the bytes"*; the registry must be the strongest instance of the pitch, not an exception to it.
3. **Serving-origin risk arrives with the app.** Dynamic rendering of untrusted HTML on an origin you control is a standing security project. Static files by digest, downloaded or verified client-side, mostly dissolve it (rendered previews still belong on a separate origin).

## 3. Prior art — verified, not remembered

The "registry as static files + signed metadata" pattern is not novel; it is how the largest registries in the world actually work. Verified against primary sources this session:

| System | What it proves | The detail worth stealing |
|---|---|---|
| **OCI Image Layout** | A container registry's contents are *specified as a directory*: `oci-layout` version marker + `index.json` entry point + `blobs/<alg>/<digest>`, with "content of `blobs/<alg>/<encoded>` MUST match the digest" | The three-part grammar: layout marker, index, content-addressed blobs. Also its honesty about partial mirrors ("MAY be missing referenced blobs… fulfilled by an external blob store") |
| **PEP 503 (PyPI simple index)** | The world's largest language-package registry read path is **static HTML pages** — root index of anchors, per-project pages, hashes carried in URL fragments (`#sha256=…`) | Static-first enables CDN serving and trivial mirroring; integrity travels *in the reference*, so the client can check without trusting the server |
| **TUF (The Update Framework)** | Static repositories need **signed metadata with expiry** — otherwise a mirror can serve you stale-but-validly-signed content forever (freeze attack) or roll you back | `expires` inside the signed index; signatures over metadata, not just content; role separation is available later if multi-writer ever matters |
| **git / apt / Homebrew taps** | The repository *format* is the product; hosting is a commodity. GitHub is a place a git repo lives, not what a git repo is | The product boundary this study proposes for htmlvault.app |

## 4. The proposed format — Capsule Registry Layout v0.1 (draft)

A registry is a directory tree. Anything that can serve files can serve one; anything that can copy files can mirror one.

```
capsule-registry.json                 # layout marker: schema + layout_version (OCI analog)
index.json                            # entry point: artifact list + generated_at + expires
attestations/
  index.json.sig                      # ssh-keygen -Y signature over index.json bytes
  allowed_signers                     # the registry's public key(s), namespaced
artifacts/<uuid>.json                 # one record per artifact
objects/sha256/<aa>/<bb>/<digest>     # the capsule bytes, content-addressed (vault fan-out)
```

**The record** carries both identities and the verification pair (the F36 custody triple, published):

```json
{
  "schema": "org.htmlcapsule.registry.record/v0",
  "uuid": "…",                          "title": "…",
  "object_digest": "sha256:…",          "object_size": 43395,
  "declared": {"spec_version": "0.4.0", "content_hash": "sha256:…", "hash_scope": "data+manifest"},
  "verified": {"validator_version": "0.4.0", "strict_pass": true, "verified_at": "…"},
  "published": {"source": "…"}
}
```

Design notes, each earned by a prior finding:

- **Two digests per record, never conflated.** `object_digest` is the whole-file address (transport integrity); `declared.content_hash` is the capsule's seal (truth integrity). §11.1 already drew this line for `parents[]` pinning; the prototype's tamper test (below) shows why both are load-bearing.
- **The index is signed and expires.** TUF's freeze-attack lesson: an unsigned or unexpiring index lets any mirror serve yesterday forever. `ssh-keygen -Y` keeps the key story identical to the custody-signing proposal already costed in the vault review — no new key material, no PKI.
- **Records restate the verification pair** (§8.1): declared line + validator version. A registry that says only "valid" repeats the F34/F36 legibility sin.
- **The layout is the vault's own layout, plus an index and a signature.** `objects/sha256/<aa>/<bb>/` fan-out is verbatim what `app.htmlvault.artifact/v1` records point at today, which is what makes `htmlvault publish` a *sync*, not an exporter.

**Client verification procedure** (what "registry compliance" means when it's checkable):
1. Fetch `index.json` + signature; verify against `allowed_signers`; reject if expired. → *catalogue authenticity + freshness*
2. Fetch object by digest; recompute sha256; reject on mismatch. → *transport integrity, no host attestation required*
3. Run the capsule validator (browser `tools/validator.html` or `validate.py`, URL mode). → *truth integrity under the declared line's recipe*
4. Optionally cross-check the host's `x-capsule-*` headers when present — the HOSTING.md behavioral layer, now redundant-but-confirming rather than load-bearing.

## 5. The prototype — every claim above, executed

Built this session in a scratch directory from **five real capsules spanning three spec lines** (0.2.0 briefing + implementation-notes, 0.3.0 sealed-sources + annotation, 0.4.0 JCS), records generated by actually running the reference validator, index signed with a throwaway ed25519 demo key:

| # | Claim | Result |
|---|---|---|
| 1 | Fetch-by-digest + full validation over plain HTTP, zero server logic | `validate.py <url>` → 30/30 strict against `python3 -m http.server` |
| 2 | Transport integrity is client-checkable | fetched bytes' sha256 == path digest ✅ |
| 3 | Catalogue authenticity | `ssh-keygen -Y verify` over the fetched index ✅ |
| 4 | **Host independence** | `cp -r` the tree, serve from a second port, identical verification ✅ — the registry was "migrated between hosts" with a copy command |
| 5 | Tamper detection on a hostile mirror | one byte flipped in a stored object → **digest check caught it instantly; the capsule seal deliberately did not** |

Result 5 is the study's sharpest lesson (recorded as F49). The flipped byte landed in the HTML `<title>` — the *projection* — which `data+manifest` intentionally does not cover (F34: projections are regenerable). So the seal said "truth intact" and the address said "these are not the published bytes," and **both were correct**. The two integrity layers are orthogonal by design: the seal protects what the capsule *means*; the address protects what the registry *serves*; each catches exactly what the other deliberately ignores. A client that runs only the validator, or a registry that publishes only seals without content addresses, has a hole precisely the shape of the other layer.

## 6. What htmlvault.app becomes

- **Reads: static.** The registry tree on the existing Pages project (or R2 behind it). Search at personal scale = client-side over `index.json`. Per-artifact pages can be pre-rendered static HTML *generated from records* — the 1730 Astro pattern applies here, as the site shell, not the registry.
- **Writes: `htmlvault publish`** — the already-costed sync subcommand, targeting a bucket instead of a backup path, plus index regeneration and signing. The vault remains canonical; the registry is a projection of it. (Pleasing symmetry: projections regenerable, truth at home — the capsule's own architecture, one level up.)
- **One dynamic endpoint, maybe:** a receive-link inbox (`POST` → quarantine prefix → vault pulls). This is the only thing static files cannot do, and it can ship later without touching the format.
- **Private sharing stays on mindev**, which has proven share tokens with expiry. Public registry ≠ gated delivery; do not build auth twice.
- **Rendered previews on a separate origin** whenever they arrive. Static-first defers this decision without foreclosing it.

**Relationship to HOSTING.md Compliance v1:** compose, don't compete. The compliance sketch governs a host's *behavior*; this layout governs the *contents*. A host serving a conforming registry tree gets most compliance properties structurally (immutability and integrity become checkable), and the behavioral contract shrinks to availability + the attestation headers. `spec/REGISTRY.md`, when written, should say exactly that.

## 7. Deferred, honestly

- **Multi-writer / accounts / stranger uploads** — a personal-scale registry proving a format needs none of it; TUF's role separation is the known escalation path if it ever matters.
- **Revocation** — doesn't exist and can't: §16.1.1 (non-revocability) applies to registries too. Removal-from-index is the only lever, and the study should never pretend otherwise.
- **Scale** — a single `index.json` is fine for hundreds of artifacts; PEP 503's per-project sharding is the known answer at thousands. Not today's problem.
- **The empirical next step:** point `validate.py` URL mode at the *deployed* registry once published, and run the same five-step proof against production — then HOSTING.md gains its first host that declares compliance *and* proves it structurally.

## 8. Build plan

1. **`spec/REGISTRY.md`** — normative layout v0.1 (the format above), verification procedure, compliance composition. Small; most of it is this study minus the argument.
2. **`htmlvault publish`** — vault → tree sync + index + signature (Rust, in the vault repo; the sync scaffolding is already costed in the custody review).
3. **Deploy** — the tree under the existing `htmlvault-app` Pages project; Astro shell around it later, per the 1730 conventions (QA gate: the registry runs the conformance suite over its own contents at publish time).
4. **Then** the inbox Function, if receive-links earn their keep.
