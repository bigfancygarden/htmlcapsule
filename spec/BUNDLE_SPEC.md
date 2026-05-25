# Bundle Spec v0.1.0

**Sibling format to Capsule.** A bundle is a portable, self-describing archive of related files — viewers, data, and assets — designed to be shared, hosted, or stored as a single unit when a single sealed HTML file is not the right shape for the artifact.

Bundle is the second format in the htmlcapsule family. It emerged from real producer pressure (the strata leak investigation; see [F31 in RESEARCH.md](../RESEARCH.md)) when a working artifact carried too much heavy data — large georeferenced rasters, LiDAR point clouds, multiple viewer HTMLs — to fit comfortably inside a Capsule's sealed-singleton commitment.

Bundle borrows three principles from the [Capsule spec](CAPSULE_SPEC.md):

1. **Identity** — every bundle has a UUID, minted by the author at seal time
2. **Integrity** — every file has a SHA-256 hash recorded in the manifest
3. **Provenance** — the manifest records who created it, when, and from what

Where a Capsule is a single sealed HTML file with everything inlined and no network, a Bundle is a **directory of files with a manifest at root** that may carry declared external dependencies. Bundles are for projects that exceed what a single file can reasonably contain — heavy assets, multiple viewers, binary data formats, working substrates that will eventually have sealed Capsule reports derived from them.

---

## 1. What makes a valid bundle

A bundle is a zip archive (or directory) containing:

1. A `manifest.json` at the root
2. At least one entry HTML file declared in the manifest
3. All files referenced by the entry HTML(s) as relative paths

That's it. Everything else in this spec is convention, not requirement.

## 2. The manifest

### 2.1 Required fields

| Field | Type | Description |
|---|---|---|
| `bundle_version` | string | Spec version. Currently `"0.1.0"` |
| `uuid` | string | UUID v4, minted by the author at seal time |
| `title` | string | Human-readable title |
| `entry` | string | Relative path to the primary entry HTML |
| `files` | array | File inventory (see §2.3) |

### 2.2 Recommended fields

| Field | Type | Description |
|---|---|---|
| `description` | string | One-paragraph summary of the bundle |
| `created_at` | string | ISO 8601 timestamp |
| `sealed_at` | string | ISO 8601 timestamp of when hashes were computed |
| `created_by` | object | Author identification (flexible shape) |
| `domain` | string | Subject domain (e.g. `"building_investigation"`, `"design_system"`) |
| `entries` | object | Additional entry points beyond the primary one |
| `integrity` | object | Hash algorithm and scope declaration |
| `external_dependencies` | array | CDN libraries or other runtime network deps |
| `parents` | array | UUIDs of parent Capsules or Bundles this was forked or derived from |
| `derived_from` | array | Non-Capsule / non-Bundle sources (same shape as Capsule's `derived_from[]`; see CAPSULE_SPEC.md §11.2) |

### 2.3 File inventory

Each item in the `files` array:

| Field | Type | Required | Description |
|---|---|---|---|
| `path` | string | yes | Relative path from bundle root |
| `sha256` | string | yes | SHA-256 hex digest |
| `size` | integer | yes | Size in bytes |
| `role` | string | recommended | One of: `entry`, `data`, `metadata`, `plan`, `raster`, `pointcloud`, `asset` |
| `format` | string | recommended | File format: `html`, `geojson`, `json`, `jpeg`, `png`, `xyz_rgb_binary`, etc. |
| `description` | string | optional | Human-readable description |

Additional fields (like `floor`, `pixels`, `pixel_scale_m`) are allowed and encouraged when they help a consumer understand the file without opening it.

### 2.4 Domain-specific extensions

The manifest can include domain-specific blocks at the top level, similar to Capsule's domain extensions in [`DOMAIN_CAPSULES.md`](DOMAIN_CAPSULES.md). For spatial bundles, a `spatial` block is recommended:

```json
{
  "spatial": {
    "crs": "EPSG:26910",
    "bounds_utm": { "west": 491663, "east": 491701, "south": 5457008, "north": 5457061 },
    "bounds_wgs84": { "west": -123.1144, "east": -123.1141, "south": 49.2659, "north": 49.2662 }
  }
}
```

For investigation bundles, a `data_summary` block:

```json
{
  "data_summary": {
    "features_total": 83,
    "floors": [5, 6, 7, 8],
    "categories": ["roof_deck_drain", "planter_drain", "leak"]
  }
}
```

The spec does not prescribe these shapes — they're conventions that emerge per domain, the same way Capsule's domain schemas earn their slot when a real producer ships a domain capsule.

## 3. The boundary

### 3.1 What's inside the bundle

- Entry HTML files and their relative-path dependencies
- Data files (GeoJSON, JSON, CSV, binary formats)
- Raster assets (JPEG, PNG, TIFF)
- Point clouds, mesh files, and other heavy binary formats
- Metadata files (the manifest, provenance docs)

### 3.2 What's outside the bundle

- CDN-hosted libraries (Leaflet, Three.js, mapping stacks, etc.)
- Live API endpoints
- Authentication / session state
- Databases

Unlike a Capsule, **a Bundle is allowed to have external dependencies**. The manifest SHOULD declare them in `external_dependencies` so a consumer knows what network access is needed. A Bundle without external dependencies is strictly better (works offline), but the spec does not require it.

This is the **load-bearing difference** between the two formats. Capsule's Rule 2 ([`CAPSULE_CORE.md`](../CAPSULE_CORE.md)) elevates "no network" to a definitional boundary — an artifact that depends on external services is a different category, not a degraded Capsule. Bundle relaxes that commitment in exchange for handling heavy artifacts and multi-viewer setups that Capsule's ~20 MB practical ceiling can't realistically contain. Both formats share the rest of the discipline (identity, integrity, provenance); they trade only on the network-boundary question.

### 3.3 Capsule vs. Bundle

| | Capsule | Bundle |
|---|---|---|
| Container | Single `.html` file | Zip archive / directory |
| Network | No external requests | External deps allowed (declared) |
| Size | Practical limit ~10–20 MB | No hard limit |
| Data | Inline JSON block | Separate files, any format |
| Viewers | Built into the HTML | Separate HTML files |
| Use case | Sealed deliverables, reports | Working projects, heavy data, multi-viewer |
| Offline | Always works offline | Works offline if no CDN deps |
| Spec | [CAPSULE_SPEC.md](CAPSULE_SPEC.md) | This document |

**Composition.** A Capsule can be *derived from* a Bundle (a compiler reads the bundle manifest, extracts data, and emits a sealed HTML report). The bundle UUID goes into the capsule's `parents[]` field as provenance. The reverse composition is also valid: a Bundle can be unpacked from a Capsule's data block + inlined assets when the working substrate is needed for further editing.

**Choosing between them.** A producer reaches for:

- **Capsule** when the artifact fits comfortably under 20 MB, all assets can be inlined as `data:` URIs, a single viewer is sufficient, the artifact must work offline without ANY network dependency, and the artifact is the final sealed deliverable.
- **Bundle** when heavy assets (LiDAR, georeferenced rasters, video) make ≤20 MB impossible, multiple viewers want separate HTML entry points, heavy libraries are realistically CDN-delivered, or the artifact is the working substrate from which a sealed Capsule will eventually be derived.

## 4. Packaging

### 4.1 Zip format

The canonical distribution format is a zip archive. The manifest MUST be at the zip root (not inside a subdirectory).

```
my-project.zip
├── manifest.json       ← root level
├── viewer/
│   └── index.html
└── data/
    └── features.geojson
```

Not this:

```
my-project.zip
└── my-project/         ← extra nesting breaks relative paths
    ├── manifest.json
    └── ...
```

### 4.2 Naming

The zip filename is not standardized. The `uuid` in the manifest is the canonical identifier.

### 4.3 Compression

Standard zip deflate. No special requirements.

## 5. Hosting

A host that receives a bundle (Stratabot is the canonical first host; see [HOSTING.md](HOSTING.md) for the equivalent host-contract pattern Capsule hosts follow):

1. Reads `manifest.json` to get the UUID, title, entry path
2. Stores files under a prefix keyed by UUID
3. Serves the entry HTML in an iframe or at a route
4. Serves sibling files at relative paths so the viewer works unchanged
5. Optionally verifies SHA-256 hashes against the manifest
6. Optionally returns response headers attesting hash and UUID (analogous to `x-capsule-content-hash` / `x-capsule-uuid` for Capsules)

The sharing layer (ACLs, share tokens, access logs) attaches to the bundle UUID, not to individual files.

**Multi-format hosts.** A host like Stratabot may accept both Capsules and Bundles, dispatching by file type or manifest shape. That is a desirable property — a domain-aware host should serve whatever sealed/manifested artifact is the right shape for the deliverable, not require producers to choose a host based on format.

## 6. Integrity verification

To verify a bundle's integrity:

```python
import json, hashlib

manifest = json.load(open("manifest.json"))
for f in manifest["files"]:
    actual = hashlib.sha256(open(f["path"], "rb").read()).hexdigest()
    assert actual == f["sha256"], f"MISMATCH: {f['path']}"
print("All files verified.")
```

The manifest itself is not self-hashing (it can't contain its own hash). A host MAY compute and store a hash of the manifest separately for tamper detection.

## 7. Versioning

When a bundle is updated (new features added, plans revised), the author SHOULD:

1. Update `sealed_at` to the new seal time
2. Recompute all file hashes
3. Keep the same `uuid` (it's the same project)
4. Increment a version field if desired (the spec does not currently mandate one)

The previous sealed state can be preserved by keeping the old zip. The manifest does not currently support internal version history — that's a future extension if real producer pressure surfaces.

---

## 8. The producer / format / host pattern

Bundle's emergence makes a project-level pattern explicit that was previously implicit in Capsule's design:

> **The host stays light. The producer can be heavy and domain-specific. The portable format is the contract that lets them compose.**

A producer (a domain-specific tool, a side project, an investigation environment) does the heavy work in whatever stack fits the domain — geospatial, music, photo, document, anything. It emits a sealed/manifested artifact in a portable format. A host receives the artifact and serves it without needing to know what tooling produced it.

The pattern instantiates as:

- **Capsule family**: Mintel (producer) → Capsule (format) → MinDev (host)
- **Bundle family**: leak (producer) → Bundle (format) → Stratabot (host)

Both follow the same shape. Future producers and hosts can be added to either family without changing the format. New sibling formats can emerge when a domain's empirical pressure pushes past both Capsule and Bundle (this is unlikely in the near term but the spec is structured to allow it).

---

*This spec is v0.1.0. It will evolve as real bundles get shared and hosted. The goal is to stay minimal: a manifest, file hashes, and an entry point. Everything else is convention.*

*Bundle joined the htmlcapsule family in project v0.4.0 (2026-05-24). See [F31 in RESEARCH.md](../RESEARCH.md) for the empirical pressure and trajectory that produced it.*
