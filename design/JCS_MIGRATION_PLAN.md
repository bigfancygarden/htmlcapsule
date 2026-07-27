# JCS Migration Plan — integrity recipe v2 (RFC 8785) for the v0.4 line

**Status:** Ratified by the operator 2026-07-27 · **Feasibility:** proven (spike results below) · **Bridge:** `decisions/jcs-canonicalization-v04` · **Lineage:** F37 → F44 → F45 → F46 → this plan

## The decision

Adopt **RFC 8785 (JSON Canonicalization Scheme, "JCS")** as the canonical JSON form for the §9.1.1 content hash, bound to the **v0.4 normative line**. The current canonical form — "format numbers the way Python 3 `repr` does" — was a historical accident of the reference implementation's language, and F44 measured its cost: every non-Python implementation must imitate CPython's formatting habits, imperfect imitation files false "tampered" verdicts against valid artifacts, and the ecosystem now carries that imitation four times over (Python, Rust, Swift, TypeScript) with no shared standard to lean on. JCS is the published standard for exactly this problem, with native-adjacent implementations in browsers (its number format *is* ECMAScript's) and maintained libraries elsewhere. The project already prefers standards over house conventions where they exist (ISO 8601 for dates, UUID v4, SemVer); numbers now join them.

## What changes, what doesn't

| | |
|---|---|
| **Changes** | The canonicalization function only: Python-repr canonical JSON → JCS |
| **Unchanged** | Payload assembly (canonical manifest with `sha256:pending` placeholder + LF + canonical data), `hash_scope` vocabulary and semantics, SHA-256, the placeholder protocol, `full_document` (byte-based, untouched) |

## Dispatch: how old and new coexist forever

- **The recipe is bound to the normative line.** `spec_version` ≤ 0.3.x ⇒ recipe v1 (the legacy form, preserved in the spec permanently for verification). `spec_version` 0.4.x ⇒ recipe v2 (JCS).
- **Failure is legible by construction** (the F36 principle): a pre-0.4 validator rejects a 0.4 capsule with *"unknown spec_version"* — a clear version statement, never a false "tampered."
- **Explicit label recommended:** 0.4 capsules SHOULD declare `integrity.canonicalization: "rfc8785"` — same display-pairing logic as `hash_scope` beside the hash (§8.4) and validator version beside the declared line (§8.1).
- **Custody needs nothing new.** The triple custody already stores (declared line, verifying validator version, when) fully disambiguates a mixed corpus.
- **Nothing sealed is ever invalidated.** Rollback = producers stay on (or return to) the 0.3 line.

## The new constraints (breaking on purpose)

1. **Numbers must be IEEE-double-safe** on the 0.4 line: integers with |n| ≤ 2^53. The reference implementation errors loudly on violations rather than silently losing precision (stricter than raw ES semantics; I-JSON alignment). The legacy recipe passed big integers verbatim; no observed producer emits them.
2. **The int/float distinction is erased**: `55.0` and `55` canonicalize identically under JCS. Deliberate — it deletes the entire F44 trap class (exponent thresholds, `.0` preservation) instead of requiring every implementation to tiptoe around it.
3. NaN/Infinity: already impossible in JSON; JCS additionally mandates hard error if an implementation is handed them.

## Feasibility: proven (spike, 2026-07-27)

A pure-stdlib Python JCS serializer (~60 lines; ECMAScript `Number::toString` re-presentation over `repr`'s shortest digits, UTF-16 code-unit key sort via `encode("utf-16-be")`, RFC escaping):

- ✅ All RFC 8785 appendix bit-pattern rows, including ±DBL_MAX (`1.7976931348623157e+308`) and `9007199254740992` (2^53)
- ✅ Hard error on NaN/Infinity bit patterns
- ✅ Supplementary-plane key sorting (`"😀"` sorts before `"￿"` — UTF-16 order, opposite of Python's code-point order)
- ✅ Number battery byte-identical to an independent Node oracle (recursive key sort + native `JSON.stringify`): `1e-7`, `1e+21`/`1e20` boundary, `55` (not `55.0`), `0.000015` (not `1.5e-05`), `1e+22`, the F37/F44 ordinates

## Provisional Test Vectors A2 / B2

Manifest: Test Vector A's manifest with `spec_version` set to `"0.4.0"` (the recipe rides the line, so the vectors do too). Data blocks: identical to Vectors A and B. **Dual-derived** — the Python spike and the independent Node oracle produced these byte-identically, which is the derivation standard F44 established (never publish a single-source vector):

```
A2  sha256:0b9e8f372fea068ba6326fd9b13df29d3e3fb9953131bd77a2bccf4cc65dd5d4
B2  sha256:24ea65104301cd83eb484e0cf3fc1af5a772900d21d0f512e8cd75a821286471
```

B2's canonical data, for the eye — note `"int_valued":55` and `"small":0.000015`:

```
{"coord_lat":57.08614,"coord_lon":-108.92228,"count":3,"int_valued":55,"large_exp":1e+22,"long_literal":0.30000000000000004,"small":0.000015,"web_mercator_y":7842318.5018136855}
```

**PROVISIONAL** until Phase 1 lands the production `compiler/jcs.py` with full string-edge tests (lone surrogates → error; U+2028/U+2029 stay raw; astral characters in values). Do not pin these anywhere before Phase 2 marks them normative.

## Phases

**Phase 0 — ratify and record** *(this commit)*. Plan in-repo; decision on Bridge; fleet notified.

**Phase 1 — reference JCS + the conformance file.** `compiler/jcs.py` (productionized spike) and `spec/conformance/hash_vectors.json` — a language-neutral fixture file carrying all four vectors (A, B legacy; A2, B2 jcs) with manifest, data, payload rules, and expected hashes. This is the shared suite F44/F45 demanded, superseding the narrower queued task. Exit: RFC rows, Node cross-check, string-edge battery, all four vectors green.

**Phase 2 — spec v0.4.0-draft.** §9.1.1 splits into *recipe v1* (frozen; verification-forever) and *recipe v2* (JCS by reference to RFC 8785 + the IEEE-safe constraint + Vectors A2/B2 finalized). §8.1 gains the recipe-per-line sentence. The v0.4 bundle stays minimal: recipe v2 plus the long-promised removals (`capsule_id`, `related`); `sealed_sources` stays a recommended convention — its Core-promotion bar (second independent producer) remains honestly unmet. Draft is marked pre-release until the first producer ships a 0.4 capsule.

**Phase 3 — validator and tools go dual-mode.** `SPEC_VERSION_KNOWN` += `0.4.0`; the hash check dispatches on the declared line and the report names which recipe verified; `repair_integrity.py` dispatches the same way; new fixtures (a valid 0.4 capsule; a 0.4 capsule with an unsafe integer that must fail loudly); full sweep + site regen. `VALIDATOR_VERSION` → `0.4.0` (enforces both lines).

**Phase 4 — the JS reference and the validator page.** `tools/` dual-mode hasher: the legacy port (spiked at 94 lines, both legacy vectors green) + JCS mode (near-native). On top of it, the drop-a-file browser validator (F45's highest-leverage artifact) — which also becomes this repo's first regression harness. Browser build swaps Node crypto for WebCrypto.

**Phase 5 — fleet migration, each on its own round, nobody forced.** Ordering rule: Phases 1–4 land first, so every consumer has the vectors and two reference implementations before any producer flips.

| Consumer | Change | Size |
|---|---|---|
| compositor (`seal.ts`) | key-sort + native `JSON.stringify`; manifests declare 0.4.0 | smallest in the fleet — JS is JCS's home turf |
| mindev (`capsule-validator.ts`) | same swap, dispatch on declared line | small |
| htmlvault (Rust) | `serde_jcs` (or ~30-line formatter) for 0.4; keeps the `float_roundtrip` legacy path for ≤0.3 verification | small; pins all four vectors this time |
| mintel (Python builders) | import `jcs.py` from the checkout they already consume | trivial |

## Risks, named

- **Two recipes forever.** Unavoidable — the sealed corpus is immutable by design. Contained: v1 is verification-only and frozen; the conformance file is the drift guard; every implementation pins all four vectors (the F44 distribution failure gets its structural fix here).
- **String edges** are Phase 1's exit criteria, not assumptions: lone surrogates, U+2028/2029 (raw under RFC escaping — confirm the Node oracle agrees), astral values.
- **Big-int data in the wild** would fail loudly at the 0.4 gate. None observed; the failure is the feature.
- **A second Python implementation** (`jcs.py` beside the legacy canonicalizer) in the same file-set — kept as separate modules with separate vector suites so neither can silently borrow from the other.
