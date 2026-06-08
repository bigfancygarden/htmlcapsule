# Bundle Spec v0.1.1

**Sibling format to Capsule.** A Bundle is a portable, self-describing archive of related files — viewers, data, and assets — designed to be shared, hosted, or stored as a single unit when a single sealed HTML file is not the right shape for the artifact.

Bundle is the second format in the htmlcapsule family. It emerged from real producer pressure (the strata leak investigation; see [F31 in RESEARCH.md](../RESEARCH.md)) when a working artifact carried too much heavy data — large georeferenced rasters, LiDAR point clouds, multiple viewer HTMLs — to fit comfortably inside a Capsule's sealed-singleton commitment.

Bundle borrows three principles from the [Capsule spec](CAPSULE_SPEC.md):

1. **Identity** — every bundle has a UUID, minted by the author at seal time
2. **Integrity** — every file has a SHA-256 hash recorded in the manifest
3. **Provenance** — the manifest records who created it, when, and from what

Where a Capsule is a single sealed HTML file with everything inlined and no network, a Bundle is a **directory of files with a manifest at root** that may carry declared external dependencies. Bundles are for projects that exceed what a single file can reasonably contain — heavy assets, multiple viewers, binary data formats, working substrates that will eventually have sealed Capsule reports derived from them.

**A Bundle is not a relaxed Capsule.** It is a sibling format with a different boundary. If the artifact fits in one offline HTML file, publish a Capsule. If the artifact needs a directory of files, multiple viewers, heavy binary assets, or declared external libraries/resources with primary artifact data local, publish a Bundle. The distinction is semantic, not just packaging: a Capsule's promise is "the whole thing is in this one HTML file"; a Bundle's promise is "the whole project is in this manifest-described set of files."

---

## 1. What makes a valid Bundle

A Bundle is a zip archive (or directory) containing:

1. A `manifest.json` at the root
2. At least one entry HTML file declared in the manifest
3. All payload files listed in `manifest.files[]`
4. All local files referenced by the entry HTML(s), CSS, or other viewers as relative paths inside the bundle

That's the validity floor. Everything else in this spec is convention until real producers and hosts make it load-bearing.

### 1.1 Quick choice rule

Use a **Capsule** when the deliverable is a sealed document or small interactive archive that can stand alone as one `.html` file with no network dependency.

Use a **Bundle** when the artifact is a project-shaped object: multiple files, heavy assets, multiple viewer entry points, binary data formats, or declared external libraries.

If you're unsure, start with Capsule. Move to Bundle only when Capsule's sealed-singleton boundary would force you to lie: external assets, hidden sidecar files, a 100 MB HTML file, or multiple viewers pretending to be one page.

### 1.2 What Bundle inherits from Capsule

Bundle inherits the htmlcapsule family's discipline, not Capsule's exact mechanics.

**Inherited at the family level:**

- Stable identity: one UUID minted at seal time
- Manifest-first description: a recipient can inspect the artifact before trusting or opening every file
- Integrity: declared hashes let a host or recipient verify the payload
- Provenance: the manifest says who/what created the artifact and what it came from
- Portability: the artifact can move as a zip/directory without losing its meaning
- Dependency honesty: anything outside the boundary is declared, not hidden

**Not inherited from Capsule:**

- The five inline Capsule blocks (`capsule-manifest`, `capsule-data`, `capsule-style`, `capsule-root`, `capsule-runtime`)
- The no-network rule as a hard render-time boundary
- The requirement that all readable content be pre-rendered into one HTML root
- Capsule's capability vocabulary and response envelope

A Bundle entry viewer may itself be a valid Capsule, but it does not become one merely by living inside a Bundle. Conversely, a Bundle can contain ordinary HTML viewers that are not Capsules, as long as the Bundle manifest honestly inventories the files and dependencies.

## 2. The manifest

### 2.1 Required fields

| Field | Type | Description |
|---|---|---|
| `bundle_version` | string | Spec version. Currently `"0.1.1"` |
| `uuid` | string | UUID v4, minted by the author at seal time |
| `title` | string | Human-readable title |
| `entry` | string | Relative path to the primary entry HTML. Must point inside the bundle and appear in `files[]` |
| `files` | array | Complete payload-file inventory (see §2.3). Excludes `manifest.json` itself |

### 2.2 Recommended fields

| Field | Type | Description |
|---|---|---|
| `description` | string | One-paragraph summary of the bundle |
| `revision` | string | Optional human-facing instance/revision label. This is the Bundle's content revision; `bundle_version` is the spec version |
| `created_at` | string | ISO 8601 timestamp |
| `sealed_at` | string | ISO 8601 timestamp of when hashes were computed |
| `created_by` | object | Author identification (flexible shape) |
| `domain` | string | Subject domain (e.g. `"building_investigation"`, `"design_system"`) |
| `bundle_profile` | string | Top-level shape of the manifested file set. Recommended values: `viewer`, `data_package`, `multi_entry`, `project_archive` |
| `entries` | object | Additional entry points beyond the primary one |
| `integrity` | object | Hash algorithm and scope declaration |
| `external_dependencies` | array | CDN libraries or other runtime network deps |
| `parents` | array | UUIDs of parent Capsules or Bundles this was forked or derived from |
| `derived_from` | array | Non-Capsule / non-Bundle sources (same shape as Capsule's `derived_from[]`; see CAPSULE_SPEC.md §11.2) |

### 2.2.1 Bundle profiles

Capsule uses `profile` to describe how one fixed HTML envelope is used. Bundle uses `bundle_profile` to describe the shape of the manifested file set. The field answers a different question: *what kind of project-shaped object is this?*

`bundle_profile` is recommended, not required, in Bundle v0.1.1. If absent, consumers should treat the object as an unprofiled legacy Bundle and apply the base rules.

Initial values:

| Value | Meaning | Typical shape |
|---|---|---|
| `viewer` | The primary experience is an HTML viewer over inventoried local files. | One `entry` HTML file, local data/assets in `files[]`, optional declared external libraries |
| `data_package` | The primary artifact is the manifest-described dataset/file set; the viewer is explanatory or optional. | Data-first inventory with `role: "data"` / domain roles; entry page summarizes the package |
| `multi_entry` | The Bundle has multiple meaningful entry points. | Primary `entry` plus named `entries` for alternate viewers, reports, or modes |
| `project_archive` | The Bundle preserves a bounded working/output folder with provenance. | Source assets, plans, scripts, generated outputs, and one or more viewers/reports |

Do not use `bundle_profile` as a substitute for `domain`. `domain` says what subject area the Bundle is about; `bundle_profile` says what container pattern the Bundle uses. Do not use it as an interactivity tier either. Whether a viewer is mostly static or highly interactive is an implementation detail inside the entry HTML; the Bundle-level profile is about the file set.

Design-tool exports are a useful emerging example of `project_archive` and
`multi_entry` pressure: a root handoff file, editable source files, local assets,
one or more viewer entrypoints, and sometimes a compiled standalone HTML output.
See [`DESIGN_HANDOFF_BUNDLES.md`](DESIGN_HANDOFF_BUNDLES.md) for the current
informative precedent note. This does not change the Capsule boundary: a
runtime-required standalone HTML export is not a reader-first Capsule unless it
also satisfies the Capsule envelope and fallback rules.

#### Adoption plan

1. v0.1.1 establishes `bundle_profile` as recommended manifest vocabulary and adds validator recognition.
2. Existing v0.1.0 Bundles remain valid; missing `bundle_profile` is a warning, not a failure.
3. Profile-specific heuristics should stay conservative until real producers need them. For now, the validator checks only that a declared profile is one of the known values.

### 2.3 File inventory

Each item in the `files` array describes one payload file. The manifest file is not listed in `files[]`, because it cannot contain a stable hash of itself without a second hashing protocol.

| Field | Type | Required | Description |
|---|---|---|---|
| `path` | string | yes | Relative path from bundle root |
| `sha256` | string | yes | SHA-256 hex digest |
| `size` | integer | yes | Size in bytes |
| `role` | string | recommended | One of: `entry`, `data`, `metadata`, `plan`, `raster`, `pointcloud`, `asset` |
| `format` | string | recommended | File format: `html`, `geojson`, `json`, `jpeg`, `png`, `xyz_rgb_binary`, etc. |
| `description` | string | optional | Human-readable description |

Additional fields (like `floor`, `pixels`, `pixel_scale_m`) are allowed and encouraged when they help a consumer understand the file without opening it.

Path rules:

- Paths MUST be relative to the bundle root.
- Paths MUST NOT begin with `/`, contain `..` segments, or use a URI scheme (`file:`, `http:`, `https:`).
- Directory entries are not listed; only files are listed.
- Symbolic links MUST NOT appear in a distributed Bundle.
- Every non-manifest file in the bundle SHOULD appear exactly once in `files[]`.
- Every local file referenced by entry HTML/CSS MUST appear in `files[]`.

### 2.4 External dependencies

Bundles may reference external libraries or runtime resources needed by a viewer. They must be declared so a recipient can tell whether the bundle will work offline, partially offline, or only with network access.

Recommended shape:

```json
"external_dependencies": [
  {
    "url": "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
    "kind": "script",
    "purpose": "2D map viewer",
    "required": true
  },
  {
    "url": "https://cdn.jsdelivr.net/npm/three@0.165.0/build/three.module.js",
    "kind": "script",
    "purpose": "3D point-cloud viewer",
    "required": true
  }
]
```

String entries are also accepted for simple manifests:

```json
"external_dependencies": [
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
]
```

The declaration is not permission to hide live state outside the bundle. A CDN library, basemap service, or rendering helper can be an external dependency; the point cloud, GeoJSON, rasters, notes, reports, and other artifact substance belong inside the bundle.

If the entry viewer fetches the artifact's primary evidence or source data from a live API at view time, the object is no longer a sealed Bundle. It is a connected project or hosted application with a manifest. Useful, but a different category.

### 2.5 Minimal manifest example

```json
{
  "bundle_version": "0.1.1",
  "uuid": "4c64bd22-9573-4b47-9a6f-9f7a685e86a1",
  "title": "Example Investigation Bundle",
  "revision": "1.0.0",
  "description": "A small public example showing one viewer, one stylesheet, and one data file.",
  "created_at": "2026-05-24T00:00:00Z",
  "sealed_at": "2026-05-24T00:00:00Z",
  "created_by": {
    "name": "htmlcapsule reference example",
    "kind": "human"
  },
  "domain": "example",
  "bundle_profile": "viewer",
  "entry": "viewer/index.html",
  "files": [
    {
      "path": "viewer/index.html",
      "sha256": "sha256:...",
      "size": 1234,
      "role": "entry",
      "format": "html"
    },
    {
      "path": "data/summary.json",
      "sha256": "sha256:...",
      "size": 456,
      "role": "data",
      "format": "json"
    }
  ],
  "external_dependencies": []
}
```

### 2.6 Domain-specific extensions

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

### 2.7 Lineage fields

Bundle uses two lineage fields, mirroring Capsule's split between hard family provenance and broader source provenance:

- `parents[]` records upstream Capsules or Bundles this Bundle was forked from or directly derived from. Each entry SHOULD include `uuid`, `title`, and `type` (`"capsule"` or `"bundle"`).
- `derived_from[]` records non-Capsule / non-Bundle sources: datasets, documents, plans, surveys, photographs, chats, or other materials that informed the artifact. Use the same entry shape described in [`CAPSULE_SPEC.md`](CAPSULE_SPEC.md) §11.2.

This differs slightly from Capsule. Capsule `parents[]` is strict Capsule-to-Capsule lineage; when a Capsule is derived from a Bundle, the Bundle belongs in the Capsule's `derived_from[]` array with `type: "bundle"` rather than in `parents[]`.

## 3. The boundary

A Capsule boundary is the HTML file. A Bundle boundary is the root directory plus `manifest.json`.

### 3.1 What's inside the bundle

- Entry HTML files and their relative-path dependencies
- Data files (GeoJSON, JSON, CSV, binary formats)
- Raster assets (JPEG, PNG, TIFF)
- Point clouds, mesh files, and other heavy binary formats
- Metadata files (the manifest, provenance docs)

### 3.2 What's outside the bundle

- CDN-hosted libraries (Leaflet, Three.js, mapping stacks, etc.)
- Live API endpoints that supply artifact substance
- Authentication / session state
- Databases

Unlike a Capsule, **a Bundle is allowed to have external dependencies**. The manifest SHOULD declare them in `external_dependencies` so a consumer knows what network access is needed. A Bundle without external dependencies is strictly better (works offline), but the spec does not require it.

This is a **load-bearing difference** between the two formats, but it should not be misread as "Bundle can put the real artifact somewhere else." Capsule's Rule 2 ([`CAPSULE_CORE.md`](../CAPSULE_CORE.md)) elevates "no network" to a definitional boundary — an artifact that depends on external services is a different category, not a degraded Capsule. Bundle relaxes the no-network commitment in exchange for handling heavy artifacts and multi-viewer setups that Capsule's ~20 MB practical ceiling can't realistically contain. It does not relax the provenance and inventory commitment: the files that make the artifact what it is belong in `files[]`.

### 3.3 Boundary anti-patterns

These are signs the artifact is neither a good Capsule nor a good Bundle yet:

- A "Capsule" that has sibling `data/` or `assets/` folders. That's a Bundle-shaped object; give it a manifest and call it a Bundle.
- A Bundle whose entry HTML fetches undeclared remote data at runtime. Declare the dependency if it's a library; put the data inside the bundle if it's part of the artifact.
- A Bundle that relies on absolute local paths like `/Users/alex/project/data.geojson`. Bundle paths are relative to the root so the archive can move.
- A Bundle that omits large referenced files from `files[]` because they are "obvious." The manifest is the inventory; if it isn't listed, a host or recipient cannot verify it.
- A Bundle used as a workaround for sloppy Capsule production. If the artifact is one HTML file with inline assets and no network, it should remain a Capsule.

### 3.4 Capsule vs. Bundle

| | Capsule | Bundle |
|---|---|---|
| Container | Single `.html` file | Zip archive / directory |
| Boundary promise | Everything needed is in the HTML file | Everything local is in the manifest-described file set; external deps are declared |
| Network | No external requests | Declared external libraries/resources allowed; primary artifact data stays local |
| Size | Practical limit ~10–20 MB | No hard limit |
| Data | Inline JSON block | Separate files, any format |
| Viewers | Built into the HTML | Separate HTML files |
| Use case | Sealed deliverables, reports, small interactive archives | Working projects, heavy data, multi-viewer artifacts |
| Offline | Always works offline | Works offline if no CDN deps |
| Integrity | Optional/required content hash depending on producer kind | Per-file SHA-256 hashes in manifest |
| Best mental model | Portable document | Portable project |
| Spec | [CAPSULE_SPEC.md](CAPSULE_SPEC.md) | This document |

**Composition.** A Capsule can be *derived from* a Bundle: a compiler reads the bundle manifest, extracts a bounded view of the data, and emits a sealed HTML report. Because Capsule `parents[]` is strict Capsule-to-Capsule lineage, a source Bundle belongs in the Capsule manifest's `derived_from[]` array, for example:

```json
"derived_from": [
  {
    "type": "bundle",
    "title": "Loft 495 leak investigation bundle",
    "reference": "urn:uuid:4c64bd22-9573-4b47-9a6f-9f7a685e86a1",
    "role": "source project"
  }
]
```

The reverse relationship is usually containment, not conversion: a Bundle may include one or more Capsules as sealed reports inside its `files[]` inventory, alongside the heavier data and viewers that produced them. Those report files remain independently valid Capsules; the Bundle manifest simply accounts for their file integrity and places them in a project-shaped context.

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

### 4.4 Directory form

During local development, a Bundle may be an ordinary directory. The same root rules apply: `manifest.json` at the directory root, paths relative to that root, and no file references that escape the directory. Zip is the distribution form; directory is the authoring and verification form.

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

To verify a Bundle's integrity, check every file listed in `manifest.files[]` against its declared size and SHA-256 hash:

```python
import json, hashlib

manifest = json.load(open("manifest.json"))
for f in manifest["files"]:
    actual = hashlib.sha256(open(f["path"], "rb").read()).hexdigest()
    assert actual == f["sha256"], f"MISMATCH: {f['path']}"
print("All files verified.")
```

The manifest itself is not self-hashing (it can't contain its own hash). A host MAY compute and store a hash of the manifest separately for tamper detection.

A reference validator lives at [`../compiler/validate_bundle.py`](../compiler/validate_bundle.py). It accepts either a bundle directory or a zip archive:

```bash
python3 compiler/validate_bundle.py spec/examples/minimal_bundle
python3 compiler/validate_bundle.py /tmp/example.bundle.zip
```

## 7. Versioning

`bundle_version` is the version of this specification, not the version of one Bundle instance. If a producer needs a human-facing instance version, use the optional `revision` field. The validity floor remains `sealed_at` plus the per-file hashes.

When a bundle is updated (new features added, plans revised), the author SHOULD:

1. Update `sealed_at` to the new seal time
2. Recompute all file hashes
3. Keep the same `uuid` (it's the same project)
4. Increment `revision` if recipients need a human-facing version label

If the update is a true fork rather than a revision of the same project, mint a new UUID and record the prior Bundle in `parents[]`. The previous sealed state can also be preserved by keeping the old zip. The manifest does not currently support internal version history — that's a future extension if real producer pressure surfaces.

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

*This spec is v0.1.1. It will evolve as real bundles get shared and hosted. The goal is to stay minimal: a manifest, file hashes, profile vocabulary, and an entry point. Everything else is convention.*

*Bundle joined the htmlcapsule family in project v0.4.0 (2026-05-24). See [F31 in RESEARCH.md](../RESEARCH.md) for the empirical pressure and trajectory that produced it.*
