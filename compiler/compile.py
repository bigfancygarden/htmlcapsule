#!/usr/bin/env python3
"""
Capsule Compiler v0.1.0

Compiles a Capsule (single self-contained HTML file) from:
  - a source data JSON file
  - a template directory (layout.html, style.css, runtime.js, config.json)

Usage:
  compile.py <source_data.json> <template_dir> -o <output.html>
"""

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

COMPILER_NAME = "capsule-compiler"
COMPILER_VERSION = "0.3.0"
SPEC_VERSION = "0.3.0"

# Compiler accepts either capsule_id (canonical) or artifact_id (legacy)
# on the input side; the source must have one. Output is always canonical.
REQUIRED_SOURCE_FIELDS = {"title", "description", "records"}
RESERVED_RECORD_FIELDS = {"_record_id", "_source_table", "_included_at", "_redacted_fields", "_content_hash"}

HASH_PLACEHOLDER = "sha256:pending"


def canonical_json(obj) -> str:
    """
    Canonical JSON serialization for hashing.
    Sorted keys, no whitespace, UTF-8. Deterministic across Python versions and
    portable to validators in other languages.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_content_hash(manifest: dict, data: dict, scope: str = "data+manifest") -> str:
    """
    Compute the content hash using the placeholder-then-replace protocol.

    The manifest's integrity.content_hash field is set to HASH_PLACEHOLDER during
    computation, the inputs are serialized canonically, concatenated per scope, and
    hashed. The result replaces the placeholder.
    """
    manifest_for_hash = json.loads(json.dumps(manifest))
    manifest_for_hash.setdefault("integrity", {})
    manifest_for_hash["integrity"]["content_hash"] = HASH_PLACEHOLDER

    if scope == "data+manifest":
        payload = canonical_json(manifest_for_hash) + "\n" + canonical_json(data)
    elif scope == "data_only":
        payload = canonical_json(data)
    elif scope == "full_document":
        raise NotImplementedError("hash_scope 'full_document' is computed after assembly, not here")
    else:
        raise ValueError(f"Unknown hash_scope: {scope}")

    return f"sha256:{sha256_hex(payload)}"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_record_hash(record: dict) -> str:
    """Hash a single record's user-facing content for stale-response detection."""
    content_only = {k: v for k, v in record.items() if not k.startswith("_")}
    canonical = json.dumps(content_only, sort_keys=True, separators=(",", ":"))
    return f"sha256:{sha256_hex(canonical)}"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def validate_source(source: dict, template_config: dict = None) -> list:
    """Return list of validation errors (empty if valid)."""
    errors = []
    missing = REQUIRED_SOURCE_FIELDS - set(source.keys())
    if missing:
        errors.append(f"Missing required source fields: {sorted(missing)}")

    if not isinstance(source.get("records"), list):
        errors.append("'records' must be a list")
    elif len(source["records"]) == 0:
        errors.append("'records' is empty — capsule needs at least one record")

    for i, rec in enumerate(source.get("records", [])):
        if not isinstance(rec, dict):
            errors.append(f"records[{i}] must be an object")
            continue
        # Records must have at least one human-meaningful field. Templates
        # define their own per-kind requirements via expected_data_fields.
        if not any(k in rec for k in ("title", "text", "name", "label", "_record_id")):
            errors.append(f"records[{i}] needs at least one of: title, text, name, label, _record_id")

    capsule_id = source.get("capsule_id", "")
    if capsule_id and not capsule_id.startswith("capsule:"):
        errors.append(f"capsule_id must start with 'capsule:' (got: {capsule_id!r})")
    artifact_id = source.get("artifact_id", "")
    if artifact_id and not artifact_id.startswith("artifact:"):
        errors.append(f"artifact_id (legacy alias) must start with 'artifact:' (got: {artifact_id!r})")

    # Apply template-specific per-kind data requirements
    if template_config:
        errors.extend(validate_records_against_template(source.get("records", []), template_config))

    return errors


TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


def _type_name(value) -> str:
    if value is None: return "null"
    if isinstance(value, bool): return "boolean"
    if isinstance(value, int): return "integer"
    if isinstance(value, float): return "number"
    if isinstance(value, str): return "string"
    if isinstance(value, list): return "array"
    if isinstance(value, dict): return "object"
    return type(value).__name__


def _check_record_fields(rec: dict, kind_spec: dict, location: str) -> list:
    """Check required-field presence AND type for one record."""
    errors = []
    types = kind_spec.get("types") or {}
    for field in kind_spec.get("required", []):
        if field not in rec:
            errors.append(f"{location} missing required field: {field!r}")
            continue
        expected_type = types.get(field)
        if expected_type and not TYPE_CHECKS.get(expected_type, lambda _: True)(rec[field]):
            errors.append(f"{location} field {field!r} has wrong type "
                          f"(expected {expected_type}, got {_type_name(rec[field])})")
    # Also check types on optional fields that are present
    for field, expected_type in types.items():
        if field in rec and field not in kind_spec.get("required", []):
            if not TYPE_CHECKS.get(expected_type, lambda _: True)(rec[field]):
                errors.append(f"{location} field {field!r} has wrong type "
                              f"(expected {expected_type}, got {_type_name(rec[field])})")
    return errors


def validate_records_against_template(records: list, template_config: dict) -> list:
    """Enforce expected_data_fields from the template config (presence and type)."""
    errors = []
    expected = template_config.get("expected_data_fields") or {}
    if not expected:
        return errors

    # If template declares record_kinds, validate per-kind. Otherwise apply
    # the generic 'required' list to every record.
    declared_kinds = template_config.get("record_kinds")

    for i, rec in enumerate(records):
        if declared_kinds:
            kind = rec.get("kind")
            if not kind:
                errors.append(f"records[{i}] missing required 'kind' field "
                              f"(template uses kind-based records: {declared_kinds})")
                continue
            if kind not in declared_kinds:
                errors.append(f"records[{i}] has unknown kind {kind!r} "
                              f"(template declares: {declared_kinds})")
                continue
            kind_spec = expected.get(kind)
            if not kind_spec:
                continue
            errors.extend(_check_record_fields(rec, kind_spec, f"records[{i}] (kind={kind})"))
        else:
            # Generic per-record requirements
            generic_spec = expected if "required" in expected else {}
            if generic_spec:
                errors.extend(_check_record_fields(rec, generic_spec, f"records[{i}]"))

    return errors


def normalize_records(records: list, timestamp: str) -> list:
    """Add reserved fields where missing, compute per-record hashes."""
    normalized = []
    for i, rec in enumerate(records):
        out = dict(rec)
        if "_record_id" not in out:
            out["_record_id"] = f"rec_{i+1:03d}"
        if "_included_at" not in out:
            out["_included_at"] = timestamp
        out["_content_hash"] = compute_record_hash(out)
        normalized.append(out)
    return normalized


def build_manifest(source: dict, template_config: dict, record_count: int) -> dict:
    """Construct the manifest from source + template config + generated fields.

    Input accepts capsule_id/capsule_version (v0.2 canonical) or
    artifact_id/artifact_version (v0.1 legacy). Output is always canonical.
    Legacy artifact:* slug values are translated to capsule:* on the way out."""
    capsule_uuid = source.get("uuid") or str(uuid.uuid4())
    capsule_version = (source.get("capsule_version")
                       or source.get("artifact_version")
                       or "1.0.0")
    # Translate legacy artifact:slug → capsule:slug on output. The capsule_id
    # is optional (UUID is canonical); only include it if the source provided one.
    raw_slug = source.get("capsule_id") or source.get("artifact_id")
    capsule_id = None
    if raw_slug:
        if raw_slug.startswith("capsule:"):
            capsule_id = raw_slug
        elif raw_slug.startswith("artifact:"):
            capsule_id = "capsule:" + raw_slug[len("artifact:"):]
    snapshot_id = source.get("snapshot_id") or f"snapshot:sn_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    created_at = source.get("created_at") or now_iso()

    manifest = {
        "spec_version": SPEC_VERSION,
        "capsule_version": capsule_version,
        "uuid": capsule_uuid,
        "title": source["title"],
        "description": source["description"],
        "type": template_config.get("capsule_type") or template_config.get("artifact_type"),
        "profile": template_config.get("profile", "interactive"),
        "created_at": created_at,
        "generator": {
            "name": COMPILER_NAME,
            "version": COMPILER_VERSION,
            "kind": "compiler",
            "spec_provided": True,
            "spec_version_used": SPEC_VERSION
        },
        "source": {
            "origin": "private_database",
            "snapshot_type": source.get("snapshot_type", "portable_excerpt"),
            "snapshot_id": snapshot_id,
            "included_records": record_count
        },
        "privacy": {
            "visibility": source.get("visibility", "shared"),
            "contains_private_data": source.get("contains_private_data", False),
            "redaction_applied": source.get("redaction_applied", False),
            "external_dependencies": False
        },
        "integrity": {
            "content_hash": "sha256:pending",
            "hash_scope": "data+manifest"
        },
        "capabilities": list(template_config["default_capabilities"])
    }

    if capsule_id:
        manifest["capsule_id"] = capsule_id

    if source.get("source_schema_version"):
        manifest["source"]["source_schema_version"] = source["source_schema_version"]
    if source.get("source_references"):
        manifest["source"]["references"] = source["source_references"]
    if source.get("redaction_method"):
        manifest["privacy"]["redaction_method"] = source["redaction_method"]
    if source.get("redaction_profile"):
        manifest["privacy"]["redaction_profile"] = source["redaction_profile"]
    if source.get("reviewed_by"):
        manifest["privacy"]["reviewed_by"] = source["reviewed_by"]
        manifest["privacy"]["reviewed_at"] = now_iso()
    if source.get("audience"):
        manifest["audience"] = source["audience"]
    if source.get("synthesis"):
        manifest["synthesis"] = source["synthesis"]

    return manifest


def build_data(source: dict, normalized_records: list) -> dict:
    """Build the capsule-data JSON object."""
    data = {
        "records": normalized_records,
        "metadata": {
            "record_count": len(normalized_records)
        }
    }
    if source.get("query_description"):
        data["metadata"]["query_description"] = source["query_description"]
    if source.get("computed"):
        data["computed"] = source["computed"]
    return data


def inject(template_text: str, replacements: dict) -> str:
    """Replace {{KEY}} placeholders with values."""
    out = template_text
    for key, value in replacements.items():
        out = out.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{[A-Z_][A-Z0-9_]*\}\}", out)
    if leftover:
        raise ValueError(f"Unresolved placeholders in template: {sorted(set(leftover))}")
    return out


def html_escape_attr(s: str) -> str:
    return (s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;"))


def validate_output(html: str) -> list:
    """Run basic offline-safety validation on the compiled output."""
    errors = []
    forbidden_patterns = [
        (r'<script[^>]+src=', 'External <script src> reference found'),
        (r'<link[^>]+href=["\']https?:', 'External <link> reference found'),
        (r'<img[^>]+src=["\']https?:', 'External <img> reference found'),
        (r'@import\s+url\s*\(\s*["\']https?:', 'External CSS @import found'),
    ]
    for pattern, message in forbidden_patterns:
        if re.search(pattern, html, re.IGNORECASE):
            errors.append(message)
    return errors


def compile_capsule(source_path: Path, template_dir: Path, output_path: Path, verbose: bool = False) -> dict:
    """Compile a capsule. Returns a result dict with metadata."""
    if verbose: print(f"Loading source: {source_path}")
    source = load_json(source_path)

    if verbose: print(f"Loading template: {template_dir}")
    template_config = load_json(template_dir / "config.json")
    layout_html = load_text(template_dir / "layout.html")
    style_css = load_text(template_dir / "style.css")
    runtime_js = load_text(template_dir / "runtime.js")

    if verbose: print(f"Validating source data against spec and template...")
    errors = validate_source(source, template_config)
    if errors:
        raise ValueError("Source validation failed:\n  - " + "\n  - ".join(errors))

    timestamp = source.get("created_at") or now_iso()

    if verbose: print(f"Normalizing {len(source['records'])} records...")
    normalized_records = normalize_records(source["records"], timestamp)

    if verbose: print(f"Building manifest...")
    manifest = build_manifest(source, template_config, len(normalized_records))
    data = build_data(source, normalized_records)

    if verbose: print(f"Computing content hash...")
    content_hash = compute_content_hash(manifest, data, scope=manifest["integrity"]["hash_scope"])
    manifest["integrity"]["content_hash"] = content_hash

    manifest_json = json.dumps(manifest, indent=2)
    data_json = json.dumps(data, indent=2)

    if verbose: print(f"Assembling HTML...")
    replacements = {
        "SPEC_VERSION": SPEC_VERSION,
        "GENERATOR_VERSION": COMPILER_VERSION,
        "CAPSULE_ID": html_escape_attr(manifest.get("capsule_id", manifest["uuid"])),
        "TITLE": html_escape_attr(manifest["title"]),
        "MANIFEST_JSON": manifest_json,
        "DATA_JSON": data_json,
        "STYLE_CSS": style_css,
        "RUNTIME_JS": runtime_js
    }
    output_html = inject(layout_html, replacements)

    if verbose: print(f"Validating output...")
    output_errors = validate_output(output_html)
    if output_errors:
        raise ValueError("Output validation failed:\n  - " + "\n  - ".join(output_errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_html, encoding="utf-8")
    file_size = output_path.stat().st_size

    if file_size > 15 * 1024 * 1024:
        raise ValueError(f"Output exceeds 15 MB hard cap: {file_size:,} bytes")

    size_warning = None
    if file_size > 5 * 1024 * 1024:
        size_warning = f"Output is {file_size:,} bytes — requires --allow-large in production use"
    elif file_size > 2 * 1024 * 1024:
        size_warning = f"Output is {file_size:,} bytes — over 2 MB, review embedded assets"

    return {
        "output_path": str(output_path),
        "capsule_id": manifest.get("capsule_id"),
        "capsule_version": manifest["capsule_version"],
        "uuid": manifest["uuid"],
        "snapshot_id": manifest["source"]["snapshot_id"],
        "content_hash": content_hash,
        "record_count": len(normalized_records),
        "file_size_bytes": file_size,
        "template": template_config["template_id"],
        "size_warning": size_warning,
    }


def main():
    parser = argparse.ArgumentParser(description="Compile a Capsule from source data and a template.")
    parser.add_argument("source", type=Path, help="Path to source data JSON file")
    parser.add_argument("template", type=Path, help="Path to template directory")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output HTML file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    try:
        result = compile_capsule(args.source, args.template, args.output, args.verbose)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Compiled: {result['output_path']}")
    print(f"  capsule_id:     {result['capsule_id'] or '(none — UUID is canonical)'}")
    print(f"  version:        {result['capsule_version']}")
    print(f"  uuid:           {result['uuid']}")
    print(f"  template:       {result['template']}")
    print(f"  records:        {result['record_count']}")
    print(f"  file size:      {result['file_size_bytes']:,} bytes ({result['file_size_bytes'] / 1024:.1f} KB)")
    print(f"  content hash:   {result['content_hash']}")
    if result["size_warning"]:
        print(f"  WARNING:        {result['size_warning']}")


if __name__ == "__main__":
    main()
