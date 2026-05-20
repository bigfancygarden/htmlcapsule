# Capsule System Architecture

The system that creates, manages, and processes Capsules.

---

## Overview

```
Private Database
      |
      v
Export Schema -----> Artifact Compiler -----> Capsule (.html)
      |                     |                       |
      |                     v                       v
      |              Artifact Registry        Recipient
      |              (what was shared)        (interacts)
      |                     ^                       |
      |                     |                       v
      |              Import Workflow <------- Response (.json)
      |                     |
      v                     v
Private Database (updated with feedback)
```

---

## 1. Private Database

The living knowledge base. Source of truth for all data.

### Responsibilities

- Store all entities, claims, notes, relationships, sources, and decisions
- Track versions and change history
- Manage access and ownership
- Serve as the authoritative record (capsules are snapshots, not sources of truth)

### Schema (conceptual, not prescribed)

The database schema is private and can evolve freely. The only requirement is that the **Export Schema** layer can map from whatever the current internal schema is to the stable artifact format.

Core concepts the database typically tracks:

| Concept       | Purpose                                    |
|---------------|--------------------------------------------|
| Sources       | Where information came from                 |
| Entities      | People, orgs, tools, concepts               |
| Claims        | Assertions with evidence and confidence      |
| Notes         | Freeform observations                        |
| Relationships | Links between entities                       |
| Projects      | Groupings of related work                    |
| Decisions     | Choices made, with rationale                 |
| Artifacts     | Records of generated capsules                |
| Snapshots     | Records of what data was exported when       |
| Feedback      | Imported responses from capsule recipients   |

---

## 2. Export Schema

A stable translation layer between the evolving internal database and the capsule format.

### Purpose

The internal database schema changes as needs evolve. The export schema provides a stable mapping so that:

- Capsules remain consistent across database schema versions
- The compiler doesn't need to know about internal schema changes
- Old capsules can be compared with new ones

### Design

```
Internal DB schema v7        Internal DB schema v8
        |                             |
        v                             v
  Export Adapter v7             Export Adapter v8
        |                             |
        v                             v
    Export Schema v1.0           Export Schema v1.0
        |                             |
        v                             v
   Same capsule format          Same capsule format
```

Each internal schema version gets an adapter that maps to the current export schema. When the export schema itself needs to change, that's a major version bump and existing adapters are updated.

### Export Schema Record Format

```json
{
  "_record_id": "rec_001",
  "_source_table": "workflows",
  "_included_at": "2026-05-15T00:00:00Z",
  "_redacted_fields": [],

  "title": "...",
  "category": "...",
  "description": "...",
  "score": 3,
  "tags": ["automation", "pipeline"],
  "source_notes": "..."
}
```

The export schema defines:
- Which fields are available for export
- Type constraints for each field
- Which fields are eligible for redaction
- Default redaction rules by sensitivity level

---

## 3. Artifact Compiler

The engine that produces capsules.

### Pipeline

```
1. Receive compilation request
   - target: which records, which query, which project
   - template: which capsule type / UI template
   - options: redaction level, asset inclusion, capabilities

2. Query data
   - Run the specified query against the private database
   - Apply the export adapter to normalize records

3. Apply redaction
   - Remove fields marked as sensitive
   - Mask values per redaction rules
   - Record what was redacted in _redacted_fields

4. Resolve assets
   - Find referenced images, audio, icons
   - Base64-encode each asset
   - Check total size against limits
   - Generate fallback placeholders for excluded assets

5. Build manifest
   - Generate UUID
   - Assign or increment capsule_version
   - Populate all required manifest fields
   - List actual capabilities of the selected template

6. Assemble HTML
   - Insert manifest JSON
   - Insert data JSON
   - Insert asset data blocks
   - Insert CSS from template
   - Insert HTML structure from template
   - Insert JavaScript runtime from template

7. Validate
   - Run all 11 validation checks from spec Section 14
   - Fail with errors or proceed with warnings

8. Compute integrity hash
   - Hash the specified scope (data+manifest, full document, or data only)
   - Insert hash into manifest

9. Output
   - Write the .html file
   - Register the artifact in the registry

10. Report
    - Return compilation result with file path, size, warnings, and registry ID
```

### CLI Interface (Proposed)

```bash
# Basic compilation
artifact compile --query "maturity_score < 4" --template decision_board --output diagnostic.html

# With options
artifact compile \
  --query "project:ai_workflows" \
  --template interactive_report \
  --redaction standard \
  --title "AI Workflow Maturity Diagnostic" \
  --output ai-maturity-diagnostic-1.0.0.html \
  --allow-large

# Recompile existing artifact with fresh data
artifact recompile --artifact-id artifact:art_001 --output ai-maturity-diagnostic-1.1.0.html

# Validate an existing capsule
artifact validate diagnostic.html

# Dry run (validate without writing)
artifact compile --query "..." --template ... --dry-run
```

### Templates

Templates define the UI, CSS, and runtime JavaScript for a capsule type. A template includes:

| Component     | Purpose                                    |
|---------------|--------------------------------------------|
| `layout.html` | HTML structure with placeholder slots       |
| `style.css`   | Styling for this capsule type               |
| `runtime.js`  | Rendering, interaction, and export logic    |
| `config.json` | Default capabilities, options, metadata     |

The compiler merges the template with the data and manifest to produce the final capsule.

---

## 4. Artifact Runtime

The JavaScript embedded inside each capsule. It runs entirely client-side with no network access.

### Initialization

```javascript
(function() {
  // 1. Parse manifest
  var manifest = JSON.parse(
    document.getElementById('capsule-manifest').textContent
  );

  // 2. Parse data
  var data = JSON.parse(
    document.getElementById('capsule-data').textContent
  );

  // 3. Parse assets index (if present)
  var assetsEl = document.getElementById('capsule-assets');
  var assets = assetsEl ? JSON.parse(assetsEl.textContent) : null;

  // 4. Initialize UI based on capabilities
  // 5. Render data
  // 6. Bind event handlers
  // 7. Set up export functions
})();
```

### State Management

The runtime maintains a strict separation between canonical data and user state:

**Canonical data** (from `capsule-data`) is read-only. The runtime reads it on initialization and never modifies it. Filter, sort, and search operations create views over the canonical data without altering the source.

**User state** (annotations, rankings, selections, form inputs) lives exclusively in JavaScript memory. It is:

- Created as the recipient interacts with the capsule
- Never written back to `capsule-data` or any DOM data block
- Serialized into the response envelope only when the recipient triggers an export
- Lost when the tab is closed (no persistent client-side storage required)
- Optionally preserved in `sessionStorage` for tab-refresh survival, but this is a convenience, not a dependency

### Export Functions

Each export capability maps to a function:

| Capability        | Function behavior                                          |
|-------------------|------------------------------------------------------------|
| `copy_as_json`    | `navigator.clipboard.writeText(JSON.stringify(data))`       |
| `copy_as_markdown`| Format data as Markdown table/list, copy to clipboard       |
| `copy_as_csv`     | Format data as CSV, copy to clipboard                       |
| `copy_as_prompt`  | Use response template to format a prompt, copy to clipboard |
| `download_json`   | Create Blob, generate download link, trigger click          |
| `download_csv`    | Create CSV Blob, generate download link, trigger click      |
| `export_response` | Collect annotations/rankings/selections, wrap in response envelope, download as JSON |
| `print_to_pdf`    | Trigger `window.print()` with print stylesheet active       |

---

## 5. Artifact Registry

A local index of everything that has been compiled and shared.

### Purpose

- Track which artifacts exist and their versions
- Record what data was included in each snapshot
- Log who received which capsule and when
- Enable recompilation with fresh data
- Support the import workflow by linking responses to artifacts

### Schema

```sql
CREATE TABLE capsules (
  capsule_id    TEXT PRIMARY KEY,    -- artifact:art_001
  title          TEXT NOT NULL,
  type           TEXT NOT NULL,
  current_version TEXT NOT NULL,
  created_at     TEXT NOT NULL,       -- ISO 8601
  updated_at     TEXT NOT NULL
);

CREATE TABLE capsule_versions (
  uuid           TEXT PRIMARY KEY,    -- UUIDv4
  capsule_id    TEXT NOT NULL REFERENCES capsules(capsule_id),
  version        TEXT NOT NULL,       -- semver
  snapshot_id    TEXT NOT NULL,
  compiled_at    TEXT NOT NULL,
  file_hash      TEXT NOT NULL,       -- sha256 of output file
  file_size      INTEGER NOT NULL,
  output_path    TEXT,
  template_used  TEXT NOT NULL,
  query_used     TEXT,
  record_count   INTEGER NOT NULL,
  warnings       TEXT,                -- JSON array
  UNIQUE(capsule_id, version)
);

CREATE TABLE snapshots (
  snapshot_id    TEXT PRIMARY KEY,    -- snapshot:sn_001
  capsule_id    TEXT NOT NULL REFERENCES capsules(capsule_id),
  created_at     TEXT NOT NULL,
  record_ids     TEXT NOT NULL,       -- JSON array of _record_ids
  source_query   TEXT,
  redaction_level TEXT,
  schema_version TEXT
);

CREATE TABLE shares (
  share_id       TEXT PRIMARY KEY,
  uuid           TEXT NOT NULL REFERENCES capsule_versions(uuid),
  shared_at      TEXT NOT NULL,
  shared_with    TEXT,                -- recipient name or identifier
  shared_via     TEXT,                -- email, link, file_drop
  notes          TEXT
);

CREATE TABLE imports (
  import_id      TEXT PRIMARY KEY,
  uuid           TEXT NOT NULL REFERENCES capsule_versions(uuid),
  imported_at    TEXT NOT NULL,
  response_type  TEXT NOT NULL,
  source_file    TEXT,
  validation     TEXT NOT NULL,       -- passed, failed, warnings
  notes          TEXT
);
```

### Storage

The registry can be implemented as:

- **SQLite** (recommended for single-user): single file, no server, portable
- **PostgreSQL**: if the private database is already Postgres
- **JSON files + Git**: for version-controlled, file-based workflows

---

## 6. Import Workflow

How feedback from capsule recipients returns to the private database.

### Flow

```
1. Recipient interacts with capsule
   - Annotates records, ranks items, makes selections, writes notes

2. Recipient exports response
   - Capsule generates response JSON per Section 7 of the spec
   - Recipient downloads or copies the response file

3. Author receives response file
   - Via email attachment, file share, or direct handoff

4. Import validation
   - Parse JSON
   - Validate against response schema
   - Verify capsule_reference matches a known artifact in registry
   - Check for version mismatch (warn if artifact has been updated since)
   - Sanitize all string content (strip HTML, scripts, event handlers)
   - Reject if file exceeds size limit

5. Import processing
   - Map response to internal database entities
   - Create feedback records linked to original source records
   - Log import in registry (imports table)

6. Author review
   - Author reviews imported feedback in their database
   - Decides what to act on
   - Imported data is flagged as external/unverified by default
```

### CLI Interface (Proposed)

```bash
# Import a response
artifact import response.json

# Import with dry-run (validate only)
artifact import response.json --dry-run

# Import with explicit artifact reference
artifact import response.json --artifact-id artifact:art_001

# List imports for an artifact
artifact imports --artifact-id artifact:art_001
```

### Trust Model

Imported responses are treated as **untrusted external input**:

- They are stored in the database but flagged as `source: external_response`
- They do not overwrite existing data
- They require author review before being treated as authoritative
- String content is sanitized before storage
- No imported content is ever executed as code

---

## Implementation Priority

### Phase 1: Minimal Viable System

1. Define export schema v1.0
2. Build compiler (query, redact, assemble, validate, output)
3. Create one template (decision_board or interactive_report)
4. Create registry (SQLite)
5. Build one working capsule from real data
6. Write capsule validator

### Phase 2: Templates and Capabilities

7. Add 2-3 more templates (assessment, dashboard, collection)
8. Implement full capability set (filter, sort, search, annotate, rank)
9. Add asset embedding pipeline
10. Add response export to runtime

### Phase 3: Feedback Loop

11. Build import workflow
12. Build import validator
13. Add version management (recompile, version bump)
14. Add share tracking

### Phase 4: Polish

15. CLI tool with subcommands
16. Print/PDF styles
17. Accessibility audit
18. Performance optimization for large datasets
19. Index capsule generation
