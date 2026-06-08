# Design Handoff Bundles

**Status:** Informative precedent and Bundle-design input.
**Observed example:** Claude Design export, inspected 2026-06-08.

This note records a design-tool export shape that closely matches the emerging
Bundle role in the htmlcapsule family. It is not a normative spec change. It is
evidence that AI design tools are already producing project-shaped handoff
folders that want the Bundle contract: manifest, entrypoints, file inventory,
hashes, provenance, and optional compiled Capsule outputs.

## Observed Shape

A Claude Design export was delivered as a zip/folder with:

```text
project-export/
  README.md
  project/
    Primary Design.html
    Primary Design (standalone).html
    Asset Kit.html
    app.jsx
    component-files.jsx
    styles.css
    assets/
    uploads/
```

The root `README.md` was explicitly written for coding agents. It identified the
primary file, explained that the design files were prototypes rather than
production code, and instructed agents to recreate the visual output in the
target codebase.

The project folder carried three different kinds of HTML:

- a source prototype entrypoint using local source files and external libraries
- an asset-kit entrypoint showing logos, icons, backgrounds, badges, loaders,
  and other reusable visual material
- a standalone compiled HTML file that inlined resources into one transportable
  artifact

## Why This Matters

This is not quite a Capsule, and that is the point. It is a Bundle-shaped object:

```text
working project + source files + assets + multiple viewers + compiled output
```

The export demonstrates real pressure for `bundle_profile: "project_archive"`
and `bundle_profile: "multi_entry"`:

- the project itself is worth preserving
- the handoff instructions are part of the object
- multiple entrypoints have different roles
- generated standalone HTML can live inside the bundle as one derived output
- a future compiler can emit conforming Capsules from the same source material

## What To Borrow

Bundle should support, or at least not fight, these conventions:

1. **Root handoff file.** A `README.md`, `handoff.md`, or `instructions.md`
   gives humans and agents the first-read contract.
2. **Entry roles.** Additional `entries` should be able to distinguish
   `source_entry`, `asset_kit`, `docs`, `compiled_capsule`,
   `compiled_artifact`, and `preview`.
3. **Source/output separation.** Editable source files and compiled deliverables
   should remain distinct in the manifest.
4. **Asset-kit entrypoints.** A design system or asset catalog is a legitimate
   secondary viewer, not noise.
5. **Derived Capsule outputs.** A Bundle may contain one or more independently
   valid Capsules generated from its source material.

## What Not To Borrow Blindly

The observed standalone HTML used an internal self-unpacking runtime:

- embedded resource manifest
- compressed JavaScript and fonts
- blob URL creation
- template replacement
- script rehydration

That mechanism is useful for design replay, but it is not the Capsule contract.
The internal manifest is an execution manifest, not a provenance/integrity
manifest. A file like this may be useful and portable, but if JavaScript is the
only way to understand the artifact's primary meaning, it is runtime-required
HTML rather than a reader-first Capsule.

The Capsule rule remains:

```text
Runtime code MAY enhance, filter, search, transform, export, or visualize the
artifact.

Runtime code MUST NOT be the only path by which a reader can understand the
artifact's primary meaning.
```

## Bundle Manifest Implications

No new required field is justified yet. The current Bundle v0.1.1 structure can
represent this pattern with existing fields:

```json
{
  "bundle_version": "0.1.1",
  "uuid": "generated-at-seal-time",
  "title": "Example design handoff",
  "bundle_profile": "project_archive",
  "domain": "design_system",
  "entry": "project/Asset Kit.html",
  "entries": {
    "asset_kit": {
      "path": "project/Asset Kit.html",
      "role": "asset_kit"
    },
    "source_prototype": {
      "path": "project/Primary Design.html",
      "role": "source_entry"
    },
    "standalone": {
      "path": "project/Primary Design (standalone).html",
      "role": "compiled_artifact",
      "runtime": "javascript_required"
    }
  },
  "created_by": {
    "name": "Claude Design",
    "kind": "design_tool"
  },
  "files": []
}
```

The main spec pressure is vocabulary, not container mechanics. If this pattern
recurs across more tools, the Bundle spec should consider recommended role
values for design handoff archives.

## Validator Implications

A future Bundle validator should be able to recognize:

- handoff files at the root
- multiple HTML entrypoints
- compiled standalone HTML outputs
- local asset and upload directories
- external dependencies in source entrypoints
- runtime-required standalone files

The validator should not fail a Bundle merely because an entrypoint requires
JavaScript. It should report that fact. A Bundle may contain runtime-heavy
viewers. The stronger reader-first rule applies when claiming a file is a
Capsule.

## Relationship To Vault

HTML Vault can ingest foreign design bundles before they are normalized. That
does not make the foreign export a Bundle spec object. Normalization means:

```text
foreign folder/zip
  -> preserve original files
  -> generate manifest.json
  -> hash inventory
  -> declare entrypoints
  -> classify external dependencies and runtime requirements
  -> optionally compile one or more conforming Capsules
```

This preserves compatibility with real design-tool outputs while keeping the
spec boundary honest.
