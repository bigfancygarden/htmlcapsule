#!/usr/bin/env python3
"""
Capsule Validator v0.1.0

Validates a compiled capsule against the spec's checks (Section 14) plus
capability truthfulness.

Usage:
  validate.py <capsule.html> [--strict]

Exit codes:
  0  All checks passed
  1  One or more checks failed
  2  Could not read or parse the file
"""

import argparse
import hashlib
import json
import re
import sys
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

SPEC_VERSION_KNOWN = {"0.1.0", "0.1.1", "0.1.2", "0.1.3", "0.1.4", "0.1.5", "0.1.6", "0.1.7", "0.1.8", "0.2.0", "0.3.0"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB hard cap (raised from 15 MB in spec v0.3.3)
SOFT_WARN_SIZE = 15 * 1024 * 1024  # 15 MB — soft warning for email-attachment compatibility
HASH_PLACEHOLDER = "sha256:pending"

REQUIRED_SECTIONS = {
    "capsule-manifest": "script",
    "capsule-data": "script",
    "capsule-style": "style",
    "capsule-root": "tag",
    "capsule-runtime": "script",
}

REQUIRED_MANIFEST_FIELDS = {
    "spec_version": str,
    "uuid": str,
    "title": str,
    "description": str,
    "type": str,
    "created_at": str,
    "generator": dict,
    "source": dict,
    "privacy": dict,
    "capabilities": list,
}

# Version field: either capsule_version (v0.2+ canonical) or artifact_version
# (v0.1 legacy). check_required_manifest_fields enforces the at-least-one rule.
EITHER_VERSION_FIELDS = ("capsule_version", "artifact_version")

# Optional manifest fields. Both forms of the id slug are accepted; the
# artifact_id form was the v0.1 name and is deprecated as of v0.2.
OPTIONAL_MANIFEST_FIELDS = {
    "capsule_id": str,
    "artifact_id": str,
}

# Recommended-but-not-required manifest fields. integrity used to live here,
# but check_integrity_hash already handles it with the correct semantics
# (FAIL for compiler, PASS for llm/human/hybrid). Listing it here too was
# double-warning the same condition.
RECOMMENDED_MANIFEST_FIELDS = {}

REQUIRED_SOURCE_FIELDS = {"origin", "snapshot_type", "snapshot_id", "included_records"}
REQUIRED_PRIVACY_FIELDS = {"visibility", "contains_private_data", "redaction_applied", "external_dependencies"}
REQUIRED_INTEGRITY_FIELDS = {"content_hash", "hash_scope"}
REQUIRED_GENERATOR_FIELDS = {"name", "version", "kind"}
VALID_GENERATOR_KINDS = {"compiler", "llm", "human", "hybrid"}

# Heuristic markers for capability implementation.
# Each capability declared must have at least one matching marker in the runtime.
CAPABILITY_MARKERS = {
    "filter":          [r"filter[-_]?select", r"\.filter\b"],
    "sort":            [r"sort[-_]?select", r"sortBy", r"\.sort\("],
    "search":          [r"search[-_]?input", r"\.indexOf\(", r"\.includes\("],
    "annotate":        [r"note[-_]?(area|toggle|textarea)", r"annotation"],
    "highlight":       [r"highlight"],
    "rank":            [r"rank", r"draggable"],
    "group":           [r"group[-_]?select", r"groupBy"],
    "compare":         [r"compare", r"selected[-_]?for[-_]?compare"],
    "copy_as_json":    [r"clipboard\.writeText.*JSON\.stringify", r"copy[-_]?json", r"btn[-_]?copy[-_]?json"],
    "copy_as_markdown":[r"copy[-_]?(md|markdown)", r"btn[-_]?copy[-_]?md", r"\bmarkdown\b"],
    "copy_as_csv":     [r"copy[-_]?csv"],
    "copy_as_prompt":  [r"copy[-_]?prompt"],
    "download_json":   [r"\.json", r"createObjectURL"],
    "download_csv":    [r"\.csv", r"createObjectURL"],
    "download_capsule":[r"document\.documentElement\.outerHTML", r"createObjectURL"],
    "print_to_pdf":    [r"window\.print\(\)", r"btn[-_]?print"],
    "export_response": [r"response_schema_version", r"capsule_reference", r"btn[-_]?export"],
    "about":           [
        # Any id starting with "about" (matches id="about", id="about-content",
        # id="about-section", id="about-panel", etc.). The landing page uses
        # just id="about" on a <details> element; older templates use the
        # longer suffixes.
        r'id\s*=\s*["\']about[\w-]*["\']',
        # Any id starting with "manifest" — commonly the <pre> showing the
        # manifest JSON inside the about panel (manifest-view, manifest-pre,
        # manifest-display, etc.).
        r'id\s*=\s*["\']manifest[\w-]*["\']',
        # Class-based about panels (class="about", class="about-content", etc.).
        r'class\s*=\s*["\'][^"\']*\babout\b',
        # Text-based detection: <summary>About this capsule</summary> on a
        # <details> element is a common pattern with no dedicated id/class.
        r'<summary[^>]*>(?:\s|<[^>]+>)*about\s',
        # aria-label naming the manifest, e.g., aria-label="Capsule manifest JSON"
        r'aria-label\s*=\s*["\'][^"\']*manifest',
        # JS-rendered about panel: many older capsules build the manifest
        # display at runtime rather than embedding it in HTML. Detect via
        # references to the manifest in the runtime code.
        r'JSON\.stringify\s*\(\s*manifest\b',
        r'getElementById\s*\(\s*[`"\']capsule-manifest[`"\']',
    ],
    # Legacy bare-name domain capability that predates the <domain>.<action>
    # naming convention (rule 7, Core v0.1.4). Present in the photo capsule.
    # New domain capabilities should use the dotted form (e.g., media.play_audio).
    "play_audio":      [r'<audio\b', r'audio[-_]?(?:player|element|controls)', r'\.play\(\)'],
}

EXTERNAL_PATTERNS = [
    # External resource references in markup (capsule assets must be inlined)
    (r'<script[^>]+\bsrc=', 'External <script src> reference (capsule JS must be inlined)'),
    (r'<link[^>]+\bhref=["\']\s*(?!data:)[^"\']', 'External <link href> reference (capsule CSS must be inlined)'),
    (r'<img[^>]+\bsrc=["\']\s*https?://', 'External <img> reference'),
    (r'<iframe[^>]+\bsrc=', 'External <iframe src> reference'),
    (r'<video[^>]+\bsrc=["\']\s*https?://', 'External <video> reference'),
    (r'<audio[^>]+\bsrc=["\']\s*https?://', 'External <audio> reference'),
    (r'@import\s+(?:url\s*\(\s*)?["\']?(?!data:)[a-zA-Z./]', 'External CSS @import'),

    # Network APIs — capsules must make zero network requests
    (r'\bfetch\s*\(', 'fetch() call (capsules must not make network requests)'),
    (r'\bXMLHttpRequest\b', 'XMLHttpRequest usage'),
    (r'\bnew\s+EventSource\s*\(', 'EventSource (Server-Sent Events) usage'),
    (r'\bnew\s+WebSocket\s*\(', 'WebSocket usage'),
    (r'\bnavigator\.sendBeacon\s*\(', 'navigator.sendBeacon() usage'),

    # ES module imports — require a server context, prohibited by spec
    (r'\bimport\s+[^.\s][^;\n]*?\s+from\s+["\']', 'ES module import (capsule scripts must be inlined)'),
    (r'(?<!\w)import\s*\(\s*["\']', 'Dynamic import() call (capsule scripts must be inlined)'),
]


class ValidationResult:
    def __init__(self):
        self.checks = []  # each: {name, level (pass|warn|fail), details, heuristic?}

    def add(self, name, level, details="", heuristic=False):
        if level is True: level = "pass"
        elif level is False: level = "fail"
        self.checks.append({"name": name, "level": level, "details": details, "heuristic": heuristic})

    @property
    def passed_count(self):
        return sum(1 for c in self.checks if c["level"] == "pass")

    @property
    def warn_count(self):
        return sum(1 for c in self.checks if c["level"] == "warn")

    @property
    def failed_count(self):
        return sum(1 for c in self.checks if c["level"] == "fail")

    @property
    def all_passed(self):
        return self.failed_count == 0


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_section(html: str, section_id: str, section_kind: str):
    """Return inner text of a script/style by id, or check tag existence."""
    if section_kind == "tag":
        pattern = r'\bid\s*=\s*["\']' + re.escape(section_id) + r'["\']'
        return re.search(pattern, html) is not None

    if section_kind == "script":
        pattern = r'<script\b[^>]*\bid\s*=\s*["\']' + re.escape(section_id) + r'["\'][^>]*>([\s\S]*?)</script>'
    elif section_kind == "style":
        pattern = r'<style\b[^>]*\bid\s*=\s*["\']' + re.escape(section_id) + r'["\'][^>]*>([\s\S]*?)</style>'
    else:
        return None

    m = re.search(pattern, html, re.IGNORECASE)
    return m.group(1).strip() if m else None


def check_html_basics(html: str, result: ValidationResult):
    has_doctype = re.match(r'^\s*<!doctype\s+html\s*>', html, re.IGNORECASE) is not None
    result.add("HTML5 doctype present", has_doctype,
               "" if has_doctype else "Missing <!DOCTYPE html> at start of file")

    has_html_tag = re.search(r'<html[\s>]', html, re.IGNORECASE) is not None
    has_body_tag = re.search(r'<body[\s>]', html, re.IGNORECASE) is not None
    result.add("Has <html> and <body> tags", has_html_tag and has_body_tag,
               "" if (has_html_tag and has_body_tag) else "Missing <html> or <body>")


def check_required_sections(html: str, result: ValidationResult):
    found = {}
    for section_id, kind in REQUIRED_SECTIONS.items():
        present = extract_section(html, section_id, kind)
        found[section_id] = bool(present) if kind == "tag" else (present is not None)
    missing = [sid for sid, ok in found.items() if not ok]
    result.add("All required sections present", not missing,
               "" if not missing else f"Missing: {', '.join(missing)}")
    return found


def check_manifest(html: str, result: ValidationResult):
    raw = extract_section(html, "capsule-manifest", "script")
    if not raw:
        result.add("Manifest section parseable", False, "Manifest section not found")
        return None

    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as e:
        result.add("Manifest section parseable", False, f"Invalid JSON: {e}")
        return None
    result.add("Manifest section parseable", True)

    # Required fields + types
    missing_fields = []
    wrong_types = []
    for field, expected_type in REQUIRED_MANIFEST_FIELDS.items():
        if field not in manifest:
            missing_fields.append(field)
        elif not isinstance(manifest[field], expected_type):
            wrong_types.append(f"{field} (expected {expected_type.__name__}, got {type(manifest[field]).__name__})")
    result.add("All required manifest fields present", not missing_fields,
               "" if not missing_fields else f"Missing: {', '.join(missing_fields)}")
    result.add("Manifest fields have correct types", not wrong_types,
               "" if not wrong_types else f"Wrong types: {', '.join(wrong_types)}")

    # Version field: accept either capsule_version (v0.2 canonical) or
    # artifact_version (v0.1 legacy). At least one must be present.
    has_capsule_version = "capsule_version" in manifest
    has_artifact_version = "artifact_version" in manifest
    if not (has_capsule_version or has_artifact_version):
        result.add("Manifest carries a version field", False,
                   "Missing capsule_version (or legacy artifact_version)")
    elif has_artifact_version and not has_capsule_version:
        result.add("Manifest carries a version field", "pass",
                   "Uses legacy artifact_version — accepted under v0.2 compatibility; "
                   "prefer capsule_version in new capsules.")
    else:
        result.add("Manifest carries a version field", True)

    # Identity slug: optional. As of v0.3, capsule_id (and artifact_id) are
    # deprecated — the UUID is the canonical identifier; slugs are redundant
    # with title and not guaranteed unique. Still accepted with an info note.
    if "artifact_id" in manifest and "capsule_id" not in manifest:
        result.add("Identity slug usage", "pass",
                   "Uses legacy artifact_id — deprecated in v0.2 and remains "
                   "deprecated in v0.3. Planned for removal in v0.4; rely on "
                   "uuid + title in new capsules.")
    elif "capsule_id" in manifest:
        result.add("Identity slug usage", "pass",
                   "Uses capsule_id — deprecated in v0.3 (not a unique "
                   "reference; derivable from title). Still accepted; "
                   "planned for removal in v0.4. Rely on uuid + title.")

    # Deprecated related[] field: emit info note if present.
    if "related" in manifest:
        n = len(manifest["related"]) if isinstance(manifest["related"], list) else 0
        result.add("Legacy related[] field", "pass",
                   f"`related` (with {n} entr{'y' if n == 1 else 'ies'}) is "
                   "deprecated in v0.3 and planned for removal in v0.4. Hard "
                   "provenance now lives in `parents`; soft associations belong "
                   "in capsule prose, not structured metadata.")

    # Recommended fields (warn, don't fail)
    missing_recommended = [f for f in RECOMMENDED_MANIFEST_FIELDS if f not in manifest]
    result.add("All recommended manifest fields present",
               "pass" if not missing_recommended else "warn",
               "" if not missing_recommended else f"Missing (recommended): {', '.join(missing_recommended)}")

    # Generator block requirements
    gen = manifest.get("generator", {})
    if isinstance(gen, dict):
        missing_gen = REQUIRED_GENERATOR_FIELDS - set(gen.keys())
        result.add("Generator block has required fields", not missing_gen,
                   "" if not missing_gen else f"Missing generator.{', generator.'.join(sorted(missing_gen))}")
        kind = gen.get("kind")
        result.add("generator.kind is a recognized value",
                   "pass" if kind in VALID_GENERATOR_KINDS else ("fail" if kind else "warn"),
                   "" if kind in VALID_GENERATOR_KINDS else f"Got: {kind!r}. Valid: {sorted(VALID_GENERATOR_KINDS)}")

    # Nested required fields
    if isinstance(manifest.get("source"), dict):
        missing_source = REQUIRED_SOURCE_FIELDS - set(manifest["source"].keys())
        result.add("Required source fields present", not missing_source,
                   "" if not missing_source else f"Missing source.{', source.'.join(sorted(missing_source))}")

    if isinstance(manifest.get("privacy"), dict):
        missing_privacy = REQUIRED_PRIVACY_FIELDS - set(manifest["privacy"].keys())
        result.add("Required privacy fields present", not missing_privacy,
                   "" if not missing_privacy else f"Missing privacy.{', privacy.'.join(sorted(missing_privacy))}")

    if isinstance(manifest.get("integrity"), dict):
        missing_integrity = REQUIRED_INTEGRITY_FIELDS - set(manifest["integrity"].keys())
        result.add("Required integrity fields present", not missing_integrity,
                   "" if not missing_integrity else f"Missing integrity.{', integrity.'.join(sorted(missing_integrity))}")

    # spec_version known
    spec_version = manifest.get("spec_version")
    spec_ok = spec_version in SPEC_VERSION_KNOWN
    result.add("spec_version is recognized", spec_ok,
               "" if spec_ok else f"Unknown spec_version: {spec_version!r}. Known: {sorted(SPEC_VERSION_KNOWN)}")

    # spec_version and source.spec_received should agree (when both present).
    # Observed authoring slip: LLM correctly records spec_received from the Core
    # version line, but inherits spec_version from a stale example block.
    spec_received = manifest.get("source", {}).get("spec_received")
    if spec_received and spec_version:
        # spec_received looks like "v0.1.2 · 2026-05-16"; extract leading semver
        m = re.search(r"v?(\d+\.\d+\.\d+)", spec_received)
        received_ver = m.group(1) if m else None
        agree = received_ver is None or received_ver == spec_version
        result.add(
            "spec_version agrees with source.spec_received",
            agree,
            "" if agree else
            f"spec_version={spec_version!r} but source.spec_received parses to {received_ver!r}. "
            f"These should match — likely cargo-culted from an old example block.")

    # external_dependencies must be false
    ext_dep = manifest.get("privacy", {}).get("external_dependencies")
    ext_ok = ext_dep is False
    result.add("privacy.external_dependencies is false", ext_ok,
               "" if ext_ok else f"Got: {ext_dep!r}")

    # capabilities: must include 'about' and at least one export
    caps = manifest.get("capabilities", [])
    has_about = "about" in caps
    export_caps = {"copy_as_json", "download_json", "download_capsule", "copy_as_markdown", "print_to_pdf", "export_response"}
    has_export = any(c in caps for c in export_caps)
    result.add("Capabilities include 'about'", has_about,
               "" if has_about else "Spec requires 'about' capability")
    result.add("Capabilities include at least one export", has_export,
               "" if has_export else f"Need one of: {sorted(export_caps)}")

    return manifest


def check_data(html: str, result: ValidationResult):
    raw = extract_section(html, "capsule-data", "script")
    if not raw:
        result.add("Data section parseable", False, "Data section not found")
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        result.add("Data section parseable", False, f"Invalid JSON: {e}")
        return None
    result.add("Data section parseable", True)
    return data


def _strip_data_blocks(html: str) -> str:
    """Remove the manifest and data script blocks before scanning for code-level
    violations. The JSON blocks legitimately contain documentation strings
    (e.g., 'fetch()' as text in an article about fetch APIs), and they're not
    executable. Network-pattern checks should only apply to the runtime JS,
    style CSS, and visible HTML — not to the embedded JSON data."""
    pattern = r'<script\b[^>]*\bid\s*=\s*["\'](?:capsule-manifest|capsule-data)["\'][^>]*>[\s\S]*?</script>'
    return re.sub(pattern, '', html, flags=re.IGNORECASE)


def check_no_external_references(html: str, result: ValidationResult):
    # Strip the data/manifest JSON blocks — they may contain documentation
    # strings that match our patterns but aren't actually code.
    scannable = _strip_data_blocks(html)
    found = []
    for pattern, label in EXTERNAL_PATTERNS:
        if re.search(pattern, scannable, re.IGNORECASE):
            found.append(label)
    result.add("No external resource references", not found,
               "" if not found else "; ".join(found))


def check_integrity_hash(manifest: dict, data: dict, html: str, result: ValidationResult, html_source_path: str = None):
    if manifest is None or data is None:
        result.add("Content hash verifies", "fail", "Manifest or data unavailable")
        return

    integrity = manifest.get("integrity")
    generator_kind = manifest.get("generator", {}).get("kind", "unknown")

    # Missing integrity block entirely:
    #   - compiler: FAIL (deterministic producers must include one)
    #   - llm/human/hybrid: PASS with a note (integrity is optional for
    #     non-compiler producers per the Core spec). Warning noise was making
    #     the validator output read as "broken" for valid LLM/hybrid capsules.
    if not isinstance(integrity, dict):
        if generator_kind == "compiler":
            result.add("Content hash verifies", "fail",
                       "No integrity block present. Compiler-produced capsules must include one.")
        else:
            result.add("Content hash verifies", "pass",
                       f"No integrity block (optional for generator.kind={generator_kind}).")
        return

    declared_hash = integrity.get("content_hash")
    scope = integrity.get("hash_scope", "data+manifest")

    if not declared_hash or not isinstance(declared_hash, str) or not declared_hash.startswith("sha256:"):
        level = "fail" if generator_kind == "compiler" else "warn"
        result.add("Content hash verifies", level,
                   f"Missing or malformed content_hash: {declared_hash!r} (generator.kind={generator_kind})")
        return

    manifest_for_hash = json.loads(json.dumps(manifest))
    manifest_for_hash["integrity"]["content_hash"] = HASH_PLACEHOLDER

    if scope == "data+manifest":
        payload = canonical_json(manifest_for_hash) + "\n" + canonical_json(data)
    elif scope == "data_only":
        payload = canonical_json(data)
    elif scope == "full_document":
        # Read the raw UTF-8 bytes (not decoded text), replace the literal
        # content_hash value with the placeholder, and hash the resulting bytes.
        # Hash strings are ASCII so byte-level find/replace matches text-level.
        try:
            file_bytes = Path(html_source_path).read_bytes() if html_source_path else html.encode("utf-8")
        except Exception:
            file_bytes = html.encode("utf-8")
        declared_bytes = declared_hash.encode("utf-8")
        placeholder_bytes = HASH_PLACEHOLDER.encode("utf-8")
        if declared_bytes not in file_bytes:
            result.add("Content hash verifies", "fail",
                       "hash_scope=full_document but the declared content_hash string does not appear "
                       "literally in the file bytes — cannot verify.")
            return
        replaced_bytes = file_bytes.replace(declared_bytes, placeholder_bytes)
        import hashlib as _h
        computed = f"sha256:{_h.sha256(replaced_bytes).hexdigest()}"
        matches = computed == declared_hash
        result.add("Content hash verifies", "pass" if matches else "fail",
                   "" if matches else f"Declared={declared_hash[:20]}... computed={computed[:20]}... (scope=full_document)")
        return
    else:
        result.add("Content hash verifies", "fail", f"Unknown hash_scope: {scope}")
        return

    computed = f"sha256:{sha256_hex(payload)}"
    matches = computed == declared_hash
    # Wrong hash is always a fail — it indicates tampering or a generator bug
    result.add("Content hash verifies", "pass" if matches else "fail",
               "" if matches else f"Declared={declared_hash[:16]}... computed={computed[:16]}... (scope={scope}). "
                                  "Either the capsule was tampered with, or the producer computed the hash incorrectly.")


def check_capability_truthfulness(manifest: dict, html: str, result: ValidationResult):
    """For each declared capability, verify the runtime has matching markers."""
    if manifest is None:
        return
    runtime = extract_section(html, "capsule-runtime", "script") or ""
    layout_root = extract_section(html, "capsule-root", "tag")
    capabilities = manifest.get("capabilities", [])

    # We scan both runtime JS and the layout HTML — markers may be in either.
    haystack = runtime + "\n" + html

    unsupported = []
    unimplemented = []
    for cap in capabilities:
        # Dotted-namespace capabilities (e.g., 'media.play_audio',
        # 'map.zoom_to_layer') are domain-specific by convention (Core v0.1.4
        # rule 7). The validator can't be expected to have markers for every
        # domain. Skip the implementation-marker and recognition checks for
        # these — domain consumers should validate them, not the core validator.
        if "." in cap:
            continue
        if cap not in CAPABILITY_MARKERS:
            unsupported.append(cap)
            continue
        markers = CAPABILITY_MARKERS[cap]
        # Uniform cleaner-convention patterns. Recognize the capability name
        # used literally as a DOM action binding (data-capsule-action="cap_name")
        # or as a JS handler dispatch key (cap_name: function ...). This rewards
        # the cleanest Rule 7 verification pattern — same literal string in the
        # manifest, the DOM, and the implementation — without weakening any check.
        # Both patterns are specific to implementation context: the data-attribute
        # only appears in HTML element markup, and the `: function` form requires
        # the `function` keyword after the colon, which cannot appear in JSON.
        escaped_cap = re.escape(cap)
        clean_convention_patterns = [
            rf'data-capsule-action\s*=\s*["\']{escaped_cap}["\']',
            rf'\b{escaped_cap}\s*:\s*function\b',
        ]
        all_markers = list(markers) + clean_convention_patterns
        found = any(re.search(p, haystack, re.IGNORECASE | re.DOTALL) for p in all_markers)
        if not found:
            unimplemented.append(cap)

    result.add("All declared capabilities have implementation markers",
               "pass" if not unimplemented else "warn",
               "" if not unimplemented else f"No marker pattern matched for: {', '.join(unimplemented)} — may be a false negative if your template uses non-standard naming.",
               heuristic=True)

    if unsupported:
        result.add("All declared capabilities are recognized", "warn",
                   f"Unrecognized capabilities (validator does not know markers for): {', '.join(unsupported)}. "
                   f"Domain capabilities should follow the '<domain>.<action>' naming convention so the validator can skip them gracefully (Core v0.1.4 rule 7).",
                   heuristic=True)


HASH_FORMAT = re.compile(r'^(sha256|sha384|sha512):[a-f0-9]+$')
CAPSULE_ID_FORMAT = re.compile(r'^capsule:.+$')
ARTIFACT_ID_FORMAT = re.compile(r'^artifact:.+$')
SNAPSHOT_ID_FORMAT = re.compile(r'^snapshot:.+$')
UUID_FORMAT = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
SEMVER_FORMAT = re.compile(r'^\d+\.\d+\.\d+$')
ISO8601_FORMAT = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$')


def check_field_formats(manifest: dict, result: ValidationResult):
    """Check field formats against the schema patterns (catches malformed values
    that hand-rolled presence checks would miss)."""
    if manifest is None:
        return

    issues = []

    def check_pattern(value, pattern, label):
        if value is not None and not pattern.match(str(value)):
            issues.append(f"{label}={value!r} does not match expected format")

    check_pattern(manifest.get("capsule_id"), CAPSULE_ID_FORMAT, "capsule_id")
    check_pattern(manifest.get("artifact_id"), ARTIFACT_ID_FORMAT, "artifact_id")
    check_pattern(manifest.get("spec_version"), SEMVER_FORMAT, "spec_version")
    check_pattern(manifest.get("capsule_version"), SEMVER_FORMAT, "capsule_version")
    check_pattern(manifest.get("artifact_version"), SEMVER_FORMAT, "artifact_version")
    check_pattern(manifest.get("uuid"), UUID_FORMAT, "uuid")
    check_pattern(manifest.get("created_at"), ISO8601_FORMAT, "created_at")

    source = manifest.get("source", {})
    check_pattern(source.get("snapshot_id"), SNAPSHOT_ID_FORMAT, "source.snapshot_id")

    integrity = manifest.get("integrity") or {}
    if "content_hash" in integrity:
        check_pattern(integrity["content_hash"], HASH_FORMAT, "integrity.content_hash")

    # Check source.references[].hash format if present
    refs = source.get("references") or []
    for i, ref in enumerate(refs):
        if "hash" in ref:
            check_pattern(ref["hash"], HASH_FORMAT, f"source.references[{i}].hash")

    # Check parents[] entries (v0.3+): each must have a valid UUID and a title.
    parents = manifest.get("parents") or []
    for i, parent in enumerate(parents):
        if not isinstance(parent, dict):
            issues.append(f"parents[{i}] must be an object, got {type(parent).__name__}")
            continue
        check_pattern(parent.get("uuid"), UUID_FORMAT, f"parents[{i}].uuid")
        if "uuid" not in parent:
            issues.append(f"parents[{i}].uuid is required")
        title = parent.get("title")
        if not isinstance(title, str) or not title.strip():
            issues.append(f"parents[{i}].title is required and must be a non-empty string")

    # Check record _content_hash format if present
    # (data is parsed separately; if records have invalid hashes, that's worth flagging)

    if issues:
        result.add("Field formats match expected patterns", "fail",
                   "; ".join(issues))
    else:
        result.add("Field formats match expected patterns", "pass")


def check_file_size(file_size: int, result: ValidationResult):
    under_limit = file_size <= MAX_FILE_SIZE
    if not under_limit:
        note = f"{file_size:,} bytes exceeds {MAX_FILE_SIZE:,} (20 MB hard cap)"
    elif file_size > SOFT_WARN_SIZE:
        # Above 15 MB but under the 20 MB hard cap — passes, but flag email-attachment risk
        note = (f"{file_size:,} bytes (above {SOFT_WARN_SIZE:,} soft warn — "
                f"may not fit common email attachment limits; hosted distribution recommended)")
    else:
        note = f"{file_size:,} bytes"
    result.add("File size under 20 MB hard cap", under_limit, note)


# Bug pattern (recurring class observed in LLM-produced capsules through v0.1.1):
# a regular string literal in the runtime JS that contains a raw line terminator,
# e.g. `lines.join("\n")` where the \n is a real newline byte. This is a
# JavaScript SyntaxError and breaks the entire runtime silently. Core spec rule 11
# (v0.1.2+) tells LLMs to use backtick template literals instead; this check
# catches whatever still slips through.
JS_STRING_LITERAL_BUG_PATTERN = re.compile(r"""\.join\s*\(\s*["'][\r\n]""")


def check_runtime_js_string_literals(html: str, result: ValidationResult):
    runtime = extract_section(html, "capsule-runtime", "script") or ""
    matches = JS_STRING_LITERAL_BUG_PATTERN.findall(runtime)
    ok = not matches
    detail = ("" if ok else
              f"Found {len(matches)} occurrence(s) of `.join(\"<newline>` or `.join('<newline>` in the runtime. "
              f"This is a JavaScript SyntaxError that breaks the entire runtime. "
              f"Use backtick template literals (`\\n`) — see Core spec rule 11.")
    result.add("Runtime JS strings are well-formed (Core rule 11)", ok, detail)


# Core v0.1.3 rule 12: content lives in the HTML, not at runtime.
# Heuristic: count visible text inside <main id="capsule-root">.
# A JS-render-everything capsule has empty placeholder elements
# and minimal static text. A progressively-enhanced capsule has
# the rendered artifact already in the HTML.
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _capsule_root_text(html: str) -> str:
    """Return the visible text inside <main id="capsule-root">, with
    <script> and <style> blocks removed."""
    # Find the capsule-root opening tag and matching close
    m = re.search(r'<main[^>]+id=["\']capsule-root["\'][^>]*>', html, re.IGNORECASE)
    if not m:
        return ""
    start = m.end()
    # We assume capsule-root is the outermost <main>; scan for </main> matching
    # by depth (cheap depth counter — rough but good enough for a heuristic).
    rest = html[start:]
    depth = 1
    i = 0
    while i < len(rest):
        nxt = re.search(r'<(/?)main\b', rest[i:], re.IGNORECASE)
        if not nxt:
            break
        is_close = nxt.group(1) == "/"
        i += nxt.end()
        if is_close:
            depth -= 1
            if depth == 0:
                inner = rest[: i - nxt.end() + nxt.start()]
                # Strip <script>...</script> and <style>...</style>
                inner = re.sub(r"<script\b[^>]*>.*?</script>", "",
                               inner, flags=re.IGNORECASE | re.DOTALL)
                inner = re.sub(r"<style\b[^>]*>.*?</style>", "",
                               inner, flags=re.IGNORECASE | re.DOTALL)
                # Strip remaining tags, collapse whitespace
                text = _TAG_RE.sub(" ", inner)
                text = _WHITESPACE_RE.sub(" ", text).strip()
                return text
        else:
            depth += 1
    return ""


PROGRESSIVE_ENHANCEMENT_MIN_TEXT = 200  # chars; below this, warn


def _spec_version_tuple(version: str):
    """Parse a semver string like '0.1.4' into a tuple (0, 1, 4) for comparison.
    Returns None if the string can't be parsed."""
    if not isinstance(version, str):
        return None
    try:
        parts = version.split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, AttributeError):
        return None


# Rule 12 was added in Core v0.1.3. Capsules made under earlier specs are
# historical artifacts and should not be retroactively in violation.
RULE_12_INTRODUCED_IN = (0, 1, 3)


def check_progressive_enhancement(manifest: dict, html: str, result: ValidationResult):
    # Rule 12 is conditional on the capsule's spec_version. Skip the check for
    # capsules that predate v0.1.3 — they were valid under their own spec.
    spec_version = (manifest or {}).get("spec_version")
    version_tuple = _spec_version_tuple(spec_version)
    if version_tuple is not None and version_tuple < RULE_12_INTRODUCED_IN:
        result.add(
            "Content pre-rendered in HTML (Core rule 12)",
            "pass",
            f"Rule 12 not applicable: capsule declares spec_version={spec_version}, "
            f"rule 12 introduced in v{'.'.join(str(p) for p in RULE_12_INTRODUCED_IN)}.",
            heuristic=True,
        )
        return

    text = _capsule_root_text(html)
    n = len(text)
    ok = n >= PROGRESSIVE_ENHANCEMENT_MIN_TEXT
    if ok:
        detail = f"{n} chars of visible text in <main id=\"capsule-root\">"
    else:
        detail = (
            f"Only {n} chars of visible text in <main id=\"capsule-root\"> — "
            f"this capsule likely relies on runtime JavaScript to render its "
            f"content. Per Core rule 12, capsules should pre-render "
            f"their content in the HTML so they remain readable in "
            f"environments that don't run inline scripts (iOS Files / "
            f"QuickLook, email previews, screen readers, search indexers, "
            f"archive viewers). Use runtime JS for enhancement (export "
            f"buttons, dynamic UI) only."
        )
    # WARN, not FAIL — existing JS-rendered capsules remain validatable;
    # the warning signals they don't follow the v0.1.3+ convention.
    result.add(
        "Content pre-rendered in HTML (Core rule 12)",
        "pass" if ok else "warn",
        detail,
        heuristic=True,
    )


def validate(path: Path, strict: bool = False) -> ValidationResult:
    result = ValidationResult()
    html = path.read_text(encoding="utf-8")
    file_size = path.stat().st_size

    check_html_basics(html, result)
    check_required_sections(html, result)
    check_no_external_references(html, result)
    manifest = check_manifest(html, result)
    data = check_data(html, result)
    check_integrity_hash(manifest, data, html, result, html_source_path=str(path))
    check_field_formats(manifest, result)
    check_capability_truthfulness(manifest, html, result)
    check_runtime_js_string_literals(html, result)
    check_progressive_enhancement(manifest, html, result)
    check_file_size(file_size, result)

    return result


def _is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))


def _fetch_url_to_temp(url: str, timeout: int = 30):
    """Fetch a URL to a temp file. Returns (Path, response_headers_dict).

    Used by URL-mode validation to support: `validate.py <https://host/path>` —
    fetches the body, captures response headers, lets the rest of the validator
    operate on the local file. Captured headers are inspected for the host-
    attestation pattern documented in spec/HOSTING.md (x-capsule-content-hash,
    x-capsule-uuid).
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "htmlcapsule-validator/0.3.4 (+https://htmlcapsule.org)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        # Lowercase header keys for case-insensitive access (HTTP headers are case-insensitive)
        headers = {k.lower(): v for k, v in resp.headers.items()}
        status = resp.status
    tmp = tempfile.NamedTemporaryFile(prefix="htmlcapsule-fetched-", suffix=".html", delete=False)
    tmp.write(body)
    tmp.close()
    return Path(tmp.name), headers, status


def _print_host_attestation(url, headers, status, local_path, content_length):
    """Print the URL preamble + host attestation cross-check (informational; not a
    pass/fail validator check, so the 26-check count stays stable for local files)."""
    print(f"Fetched: {url}")
    print(f"  HTTP {status} · {headers.get('content-type', 'unknown')} · {content_length:,} bytes")
    print(f"  Saved: {local_path}")
    print()

    print("Host attestation (from response headers, per spec/HOSTING.md):")

    # Try to extract the manifest from the body for cross-checking.
    html = Path(local_path).read_text(encoding="utf-8")
    manifest_text = extract_section(html, "capsule-manifest", "script")
    manifest = None
    if manifest_text:
        try:
            manifest = json.loads(manifest_text)
        except Exception:
            manifest = None

    found_any = False

    # x-capsule-content-hash: host's independent computation of the integrity hash
    header_hash = headers.get("x-capsule-content-hash")
    if header_hash:
        found_any = True
        manifest_hash = (manifest or {}).get("integrity", {}).get("content_hash") if manifest else None
        if manifest_hash and manifest_hash == header_hash:
            print(f"  x-capsule-content-hash: {header_hash}")
            print(f"                          ✓ matches manifest integrity.content_hash")
            print(f"                            (transitively verified against body by integrity check below)")
        elif manifest_hash:
            print(f"  x-capsule-content-hash: {header_hash}")
            print(f"                          ✗ MISMATCH (manifest integrity.content_hash = {manifest_hash})")
        else:
            print(f"  x-capsule-content-hash: {header_hash}")
            print(f"                          ⚠ capsule has no manifest integrity block; cannot cross-check directly")
            print(f"                            (host's hash is informational only without a body integrity claim)")

    # x-capsule-uuid: host's parsing of the canonical identifier
    header_uuid = headers.get("x-capsule-uuid")
    if header_uuid:
        found_any = True
        manifest_uuid = (manifest or {}).get("uuid") if manifest else None
        if manifest_uuid == header_uuid:
            print(f"  x-capsule-uuid:         {header_uuid}")
            print(f"                          ✓ matches manifest uuid")
        elif manifest_uuid:
            print(f"  x-capsule-uuid:         {header_uuid}")
            print(f"                          ✗ MISMATCH (manifest uuid = {manifest_uuid})")
        else:
            print(f"  x-capsule-uuid:         {header_uuid}")
            print(f"                          ⚠ no manifest uuid available to cross-check")

    if not found_any:
        print("  (none — host did not include x-capsule-* attestation headers)")
        print("  (the host is still a valid Capsule host; it just provides one less independent verification)")

    print()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Validate a Capsule against the spec. Accepts a local file path "
            "OR an http(s):// URL — in URL mode, the validator fetches the body, "
            "captures any x-capsule-* host-attestation headers, and cross-checks "
            "them against the manifest before running the standard checks."
        )
    )
    parser.add_argument(
        "capsule",
        type=str,
        help="Path to a local capsule HTML file, OR an http(s):// URL (typically a host's /raw endpoint)",
    )
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors")
    parser.add_argument("--quiet", action="store_true", help="Only print summary line and failures")
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP fetch timeout in seconds (URL mode only; default 30)",
    )
    args = parser.parse_args()

    url_mode = _is_url(args.capsule)
    headers = None
    status = None
    fetched_temp = None

    if url_mode:
        try:
            local_path, headers, status = _fetch_url_to_temp(args.capsule, timeout=args.timeout)
            fetched_temp = local_path
        except urllib.error.HTTPError as e:
            print(f"ERROR: HTTP {e.code} fetching {args.capsule}: {e.reason}", file=sys.stderr)
            sys.exit(2)
        except urllib.error.URLError as e:
            print(f"ERROR: Failed to fetch {args.capsule}: {e.reason}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"ERROR: Failed to fetch {args.capsule}: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        local_path = Path(args.capsule)
        if not local_path.exists():
            print(f"ERROR: File not found: {local_path}", file=sys.stderr)
            sys.exit(2)

    try:
        result = validate(local_path, strict=args.strict)
    except Exception as e:
        print(f"ERROR: Validation crashed: {e}", file=sys.stderr)
        sys.exit(2)

    # Output report
    if url_mode:
        _print_host_attestation(
            args.capsule, headers, status, local_path, local_path.stat().st_size
        )
        print(f"Validating fetched body: {local_path}")
    else:
        print(f"Validating: {args.capsule}")
    print(f"  Spec version recognized: {sorted(SPEC_VERSION_KNOWN)}")
    print()
    markers = {"pass": "✓", "warn": "⚠", "fail": "✗"}
    status_words = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}
    for check in result.checks:
        level = check["level"]
        if level == "pass" and args.quiet:
            continue
        suffix = " (heuristic)" if check.get("heuristic") else ""
        line = f"  [{status_words[level]}] {markers[level]} {check['name']}{suffix}"
        if check["details"]:
            line += f"\n         {check['details']}"
        print(line)

    print()
    total = len(result.checks)
    print(f"Result: {result.passed_count}/{total} pass, {result.warn_count} warn, {result.failed_count} fail")

    # Clean up the temp file from URL mode (the report is already printed; the
    # temp file isn't needed after validation completes)
    if fetched_temp is not None:
        try:
            fetched_temp.unlink()
        except Exception:
            pass

    if args.strict and result.warn_count > 0:
        sys.exit(1)
    sys.exit(0 if result.all_passed else 1)


if __name__ == "__main__":
    main()
