#!/usr/bin/env python3
"""
Capsule reference validator — VALIDATOR_VERSION below tracks the full-spec
version this file enforces.

Validates a compiled capsule against the spec's checks (Section 14) plus
capability truthfulness.

Usage:
  validate.py <capsule.html> [--strict]
  validate.py --version

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

# The validator's own version identity — tracks the full-spec version it
# enforces (spec §14). This file is consumed cross-repo by producer CI (the
# first external consumer: compositor's "non-negotiable #2" workflow), so
# conformance claims need to be legible: every report prints this version,
# and `--version` exists for CI to record or assert. See F35 in RESEARCH.md.
VALIDATOR_VERSION = "0.3.13"

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
VALID_CAPSULE_PROFILES = {"static", "interactive", "data"}
VALID_PRESENTATION_PROFILES = {
    "reader",
    "mobile",
    "print-letter",
    "slides",
    "reel",
    "interactive",
}
VALID_PRESENTATION_NAVIGATION = {"scroll", "paged", "step", "sequence"}
VALID_PRESENTATION_CHROME = {"capsule", "host", "none"}

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

CORE_CAPABILITIES = set(CAPABILITY_MARKERS.keys()) | {
    "media.play",
    "media.pause",
    "media.stop",
    "media.seek",
    "media.tempo_scale",
    "media.loop_bar",
    "media.midi.download",
    "media.audio.download_mix",
    "media.audio.download_stem",
    "media.stems.mute",
    "media.stems.solo",
    "media.stems.set_patch",
    "media.stems.set_volume",
    "export.fragment_provenance",
}
RESTRICTED_CAPABILITIES = {
    "storage.local",
    "native_bridge",
    "ai_context.export",
}
PROHIBITED_CAPABILITIES = {
    "network.request",
}
CAPABILITY_NAME_FORMAT = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
PRESENTATION_ID_FORMAT = re.compile(r"^[a-z][a-z0-9_-]*$")
PRESENTATION_ENTRY_FORMAT = re.compile(r"^#[A-Za-z][A-Za-z0-9_.:-]*$")

# Patterns split by where they're meaningful — scope-aware to avoid false
# positives on rendered documentation that mentions these APIs as text.
#
# MARKUP_PATTERNS: HTML element-level references — only meaningful when they
#   appear as actual HTML markup in the document body. Scanned everywhere.
# JS_PATTERNS: JavaScript network APIs — only meaningful inside <script>
#   blocks. Scanned only there. Free-text mentions in prose (e.g., a paragraph
#   that says "no fetch (rule 2 stays intact)" or a research log entry
#   discussing the fetch API) are not violations.
# CSS_PATTERNS: CSS @import — only meaningful inside <style> blocks. Scanned
#   only there. Code-block content displaying example @import statements is
#   not a violation.

MARKUP_PATTERNS = [
    (r'<script[^>]+\bsrc=', 'External <script src> reference (capsule JS must be inlined)'),
    (r'<link[^>]+\bhref=["\']\s*(?!data:)[^"\']', 'External <link href> reference (capsule CSS must be inlined)'),
    (r'<img[^>]+\bsrc=["\']\s*https?://', 'External <img> reference'),
    (r'<iframe[^>]+\bsrc=', 'External <iframe src> reference'),
    (r'<video[^>]+\bsrc=["\']\s*https?://', 'External <video> reference'),
    (r'<audio[^>]+\bsrc=["\']\s*https?://', 'External <audio> reference'),
]

JS_PATTERNS = [
    (r'\bfetch\s*\(', 'fetch() call (capsules must not make network requests)'),
    (r'\bXMLHttpRequest\b', 'XMLHttpRequest usage'),
    (r'\bnew\s+EventSource\s*\(', 'EventSource (Server-Sent Events) usage'),
    (r'\bnew\s+WebSocket\s*\(', 'WebSocket usage'),
    (r'\bnavigator\.sendBeacon\s*\(', 'navigator.sendBeacon() usage'),
    (r'\bimport\s+[^.\s][^;\n]*?\s+from\s+["\']', 'ES module import (capsule scripts must be inlined)'),
    (r'(?<!\w)import\s*\(\s*["\']', 'Dynamic import() call (capsule scripts must be inlined)'),
]

CSS_PATTERNS = [
    (r'@import\s+(?:url\s*\(\s*)?["\']?(?!data:)[a-zA-Z./]', 'External CSS @import'),
]

# Back-compat: some tests / external tooling may reference EXTERNAL_PATTERNS.
EXTERNAL_PATTERNS = MARKUP_PATTERNS + JS_PATTERNS + CSS_PATTERNS


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
    # §8.1 two-track version story: the manifest declares the normative line;
    # this validator enforces a doc revision of it. State the pair so custody
    # records can store the triple (declared, verified-by, when) — see F36.
    result.add("spec_version is recognized", spec_ok,
               f"declares normative line {spec_version!r}; enforced at doc revision {VALIDATOR_VERSION}"
               if spec_ok else
               f"Unknown spec_version: {spec_version!r}. Known: {sorted(SPEC_VERSION_KNOWN)} "
               f"(declare the normative line, not a full-spec doc revision — see spec §8.1)")

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
    else:
        result.add(
            "spec_version agrees with source.spec_received",
            "pass",
            "source.spec_received not declared; cross-check not applicable.",
        )

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


def check_sealed_sources(data, result: ValidationResult):
    """§4.1.2 `sealed_sources` convention (recommended, not required).

    Checked only when present: an object mapping the content model's source
    keys to the resolved payloads captured at seal time. Shape problems are
    warnings, not failures — the convention is optional, so a malformed block
    degrades the offline-resolution claim without invalidating the capsule.
    """
    if not isinstance(data, dict) or "sealed_sources" not in data:
        return
    sealed = data["sealed_sources"]
    if not isinstance(sealed, dict):
        result.add(
            "Sealed sources convention",
            "warn",
            f"sealed_sources should be an object mapping source keys to resolved "
            f"payloads (§4.1.2), got {type(sealed).__name__}",
        )
        return
    problems = []
    empty_keys = sum(1 for k in sealed if not k.strip())
    if empty_keys:
        problems.append(f"{empty_keys} empty source key(s)")
    null_keys = sorted(k for k, v in sealed.items() if v is None)
    if null_keys:
        # A null payload means resolution failed at seal time — the capsule
        # sealed a failure, not a source.
        problems.append(f"null payload for: {', '.join(null_keys[:5])}")
    if problems:
        result.add("Sealed sources convention", "warn", "; ".join(problems))
    elif not sealed:
        result.add(
            "Sealed sources convention",
            "pass",
            "declared but empty — no source payloads sealed",
        )
    else:
        result.add(
            "Sealed sources convention",
            "pass",
            f"{len(sealed)} resolved source payload(s) sealed in the data block "
            f"(covered by content_hash)",
        )


def check_domain_guidance(manifest, data, result: ValidationResult):
    """DOMAIN_CAPSULES.md registry requirement: every Domain Capsule
    (manifest.type of the form `domain.<name>`) MUST include an
    `ai_usage_guidance` block in the data block with `allowed_tasks`,
    `restricted_tasks`, and `preferred_language`.

    Warn-level: the base validator checks the envelope; domain-registry
    conformance is a layer above it, but the MUST exists precisely for
    high-stakes domains (geospatial, mining, legal), so silence would be
    complicity in the drift it was written to prevent — see F38.
    """
    if not isinstance(manifest, dict) or not isinstance(data, dict):
        return
    capsule_type = manifest.get("type")
    if not isinstance(capsule_type, str) or not capsule_type.startswith("domain."):
        return
    required_keys = ("allowed_tasks", "restricted_tasks", "preferred_language")
    guidance = data.get("ai_usage_guidance")
    if isinstance(guidance, dict):
        missing = [k for k in required_keys if k not in guidance]
        if missing:
            result.add("Domain capsule declares ai_usage_guidance", "warn",
                       f"present but missing: {', '.join(missing)} (DOMAIN_CAPSULES.md requires all three)")
        else:
            result.add("Domain capsule declares ai_usage_guidance", "pass",
                       "allowed_tasks / restricted_tasks / preferred_language present")
    else:
        result.add("Domain capsule declares ai_usage_guidance", "warn",
                   f"{capsule_type} is a Domain Capsule but the data block has no ai_usage_guidance "
                   f"object — DOMAIN_CAPSULES.md requires allowed_tasks / restricted_tasks / "
                   f"preferred_language for every domain.<name> capsule")


ANNOTATION_ANCHOR_FIELDS = {
    "record": ("sourceKey", "featureIndex"),
    "layer": ("layerId",),
    "coordinate": ("crs", "points"),
}


def check_annotation_shape(manifest, data, result: ValidationResult):
    """DOMAIN_CAPSULES.md `domain.annotation`: a sealed layer of marks over a
    digest-pinned base. Checked only for type == 'domain.annotation'.

    Warn-level (like the other domain-convention checks): the base validator
    owns the envelope; this enforces the domain's load-bearing shape — the
    digest pin (without which an annotation can be silently re-targeted) and
    anchor-to-truth (marks addressing the data block, not the regenerable DOM).
    """
    if not isinstance(manifest, dict) or manifest.get("type") != "domain.annotation":
        return
    problems = []

    # (1) Base must be digest-pinned in parents[].
    parents = manifest.get("parents") or []
    pinned = [p for p in parents if isinstance(p, dict) and isinstance(p.get("content_hash"), str)]
    if not parents:
        problems.append("no parents[] — a domain.annotation MUST digest-pin its base capsule (§11.1)")
    elif not pinned:
        problems.append("parents[] present but none carry content_hash — the base pin is what makes "
                        "the annotation resolvable/verifiable; an unpinned base can be silently re-targeted")

    # (2) Data block shape: base + marks.
    if not isinstance(data, dict):
        problems.append("data block is not an object; expected base + marks[]")
    else:
        base = data.get("base")
        if not isinstance(base, dict) or "content_hash" not in base:
            problems.append("data.base missing or lacks content_hash (should mirror parents[0], "
                            "inside the hashed data block)")
        elif pinned and base.get("content_hash") != pinned[0].get("content_hash"):
            problems.append("data.base.content_hash does not match parents[0].content_hash")

        marks = data.get("marks")
        if not isinstance(marks, list) or not marks:
            problems.append("data.marks missing or empty; a domain.annotation carries at least one mark")
        else:
            for i, mark in enumerate(marks):
                if not isinstance(mark, dict):
                    problems.append(f"marks[{i}] is not an object")
                    continue
                if not mark.get("id"):
                    problems.append(f"marks[{i}] missing id")
                if not mark.get("kind"):
                    problems.append(f"marks[{i}] missing kind")
                anchor = mark.get("anchor")
                if not isinstance(anchor, dict):
                    problems.append(f"marks[{i}] missing anchor (must address the base's data block, not the DOM)")
                    continue
                atype = anchor.get("type")
                if atype not in ANNOTATION_ANCHOR_FIELDS:
                    problems.append(f"marks[{i}].anchor.type {atype!r} unknown; "
                                    f"expected one of {sorted(ANNOTATION_ANCHOR_FIELDS)} (anchor to truth, not projection)")
                else:
                    missing = [f for f in ANNOTATION_ANCHOR_FIELDS[atype] if f not in anchor]
                    if missing:
                        problems.append(f"marks[{i}].anchor ({atype}) missing {', '.join(missing)}")

    if problems:
        # Cap the detail so a broken batch doesn't flood the report.
        shown = problems[:6]
        more = f" (+{len(problems) - 6} more)" if len(problems) > 6 else ""
        result.add("Annotation layer shape", "warn", "; ".join(shown) + more)
    else:
        result.add("Annotation layer shape", "pass",
                   f"{len(data['marks'])} mark(s) over a digest-pinned base; anchors address sealed truth")


def check_profile_overlay(manifest: dict, result: ValidationResult):
    if manifest is None:
        return
    profile = manifest.get("profile")
    if profile is None:
        result.add(
            "Capsule profile is valid",
            "pass",
            "No profile declared; treating as unprofiled legacy Capsule.",
        )
        return
    if not isinstance(profile, str):
        result.add("Capsule profile is valid", "fail", f"profile must be a string, got {type(profile).__name__}")
        return
    result.add(
        "Capsule profile is valid",
        profile in VALID_CAPSULE_PROFILES,
        "" if profile in VALID_CAPSULE_PROFILES else f"Got {profile!r}; valid: {sorted(VALID_CAPSULE_PROFILES)}",
    )


def _strip_data_blocks(html: str) -> str:
    """Remove regions before scanning for code-level violations:

    1. The manifest + data script blocks. JSON content can legitimately
       contain documentation strings that match our network/external-resource
       patterns (e.g., 'fetch()' as text in an article about fetch APIs), and
       it's not executable.
    2. <code> and <pre> blocks in the body. Same reason — they hold literal
       text content for display (code examples, spec excerpts, rendered
       markdown excerpts), not executable JS or CSS @import statements.
       Without this, capsules that render documentation about fetch / @import
       / WebSocket / etc. trigger false positives even though the page itself
       makes no network requests.

    Network-pattern checks should only apply to the runtime JS, style CSS,
    and visible (non-code) HTML — not to embedded JSON data or rendered
    code-block content."""
    # Strip JSON blocks
    json_pattern = r'<script\b[^>]*\bid\s*=\s*["\'](?:capsule-manifest|capsule-data)["\'][^>]*>[\s\S]*?</script>'
    out = re.sub(json_pattern, '', html, flags=re.IGNORECASE)
    # Strip <pre>...</pre> and <code>...</code> blocks (literal text content)
    out = re.sub(r'<pre\b[^>]*>[\s\S]*?</pre>',  '', out, flags=re.IGNORECASE)
    out = re.sub(r'<code\b[^>]*>[\s\S]*?</code>', '', out, flags=re.IGNORECASE)
    return out


def check_no_external_references(html: str, result: ValidationResult):
    """Check capsule has no external resource references.

    Scope-aware to avoid false positives:
    - MARKUP patterns scan the whole document with JSON/code/pre stripped.
    - JS patterns scan only inside <script> blocks (not capsule-manifest
      or capsule-data, which are JSON content).
    - CSS patterns scan only inside <style> blocks.

    Rationale: a capsule that renders documentation containing the word
    "fetch" or an @import code example is not making a network call. The
    network/import APIs are only meaningful inside their respective
    language scopes.
    """
    found = []

    # Markup patterns — scan whole document, with data/code/pre stripped
    scannable = _strip_data_blocks(html)
    for pattern, label in MARKUP_PATTERNS:
        if re.search(pattern, scannable, re.IGNORECASE):
            found.append(label)

    # JS patterns — scan only inside <script> blocks, excluding capsule-manifest
    # and capsule-data (which are JSON, not JS)
    script_pattern = r'<script\b(?![^>]*\bid\s*=\s*["\'](?:capsule-manifest|capsule-data)["\'])[^>]*>([\s\S]*?)</script>'
    for m in re.finditer(script_pattern, html, re.IGNORECASE):
        script_body = m.group(1)
        for pattern, label in JS_PATTERNS:
            if re.search(pattern, script_body, re.IGNORECASE):
                found.append(label)

    # CSS patterns — scan only inside <style> blocks
    for m in re.finditer(r'<style\b[^>]*>([\s\S]*?)</style>', html, re.IGNORECASE):
        style_body = m.group(1)
        for pattern, label in CSS_PATTERNS:
            if re.search(pattern, style_body, re.IGNORECASE):
                found.append(label)

    # De-dup labels (same finding may surface in multiple scripts)
    found = list(dict.fromkeys(found))
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
        if not isinstance(cap, str):
            continue
        if cap in RESTRICTED_CAPABILITIES or cap in PROHIBITED_CAPABILITIES:
            continue
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


def check_capability_classes(manifest: dict, result: ValidationResult):
    if manifest is None:
        return
    capabilities = manifest.get("capabilities", [])
    if not isinstance(capabilities, list):
        result.add("Capability names are valid/classes known", "fail", "capabilities must be an array")
        return

    invalid = []
    prohibited = []
    restricted = []
    unknown_bare = []
    extensions = []

    for cap in capabilities:
        if not isinstance(cap, str):
            invalid.append(f"{cap!r} is {type(cap).__name__}, expected string")
            continue
        if not CAPABILITY_NAME_FORMAT.match(cap):
            invalid.append(cap)
            continue
        if cap in PROHIBITED_CAPABILITIES:
            prohibited.append(cap)
        elif cap in RESTRICTED_CAPABILITIES:
            restricted.append(cap)
        elif cap in CORE_CAPABILITIES:
            continue
        elif "." in cap or cap.startswith("x-"):
            extensions.append(cap)
        else:
            unknown_bare.append(cap)

    details = []
    if prohibited:
        details.append("Prohibited in Capsules: " + ", ".join(sorted(prohibited)))
    if invalid:
        details.append("Invalid capability names: " + ", ".join(sorted(invalid)))
    if restricted:
        details.append("Restricted declarations (not permissions; host/reader may deny): " + ", ".join(sorted(restricted)))
    if unknown_bare:
        details.append("Unknown bare capabilities should be core names or namespaced extensions: " + ", ".join(sorted(unknown_bare)))
    if extensions and not (prohibited or invalid or restricted or unknown_bare):
        details.append("Namespaced extension capabilities: " + ", ".join(sorted(extensions)))

    if prohibited or invalid:
        level = "fail"
    elif restricted or unknown_bare:
        level = "warn"
    else:
        level = "pass"

    result.add(
        "Capability names are valid/classes known",
        level,
        "; ".join(details),
        heuristic=bool(restricted or unknown_bare or extensions),
    )


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
    # parents[] is strict Capsule-to-Capsule lineage.
    parents = manifest.get("parents") or []
    for i, parent in enumerate(parents):
        if not isinstance(parent, dict):
            issues.append(f"parents[{i}] must be an object, got {type(parent).__name__}")
            continue
        check_pattern(parent.get("uuid"), UUID_FORMAT, f"parents[{i}].uuid")
        if "uuid" not in parent:
            issues.append(f"parents[{i}].uuid is required (parents[] is Capsule-to-Capsule lineage; for non-Capsule sources use derived_from[] — see spec §11.2)")
        title = parent.get("title")
        if not isinstance(title, str) or not title.strip():
            issues.append(f"parents[{i}].title is required and must be a non-empty string")
        # v0.3.11 digest pinning: optional, but when present it must look like
        # a real content hash (claimed-vs-verifiable — spec §11.1).
        if "content_hash" in parent:
            check_pattern(parent["content_hash"], HASH_FORMAT, f"parents[{i}].content_hash")

    # Check derived_from[] entries (v0.3.6+): each must have a type and a title.
    # derived_from[] holds non-Capsule provenance (compositions, datasets, chats,
    # documents, ...) — anything addressable or describable but lacking a Capsule
    # UUID. See spec §11.2 for the full shape.
    derived = manifest.get("derived_from") or []
    if not isinstance(derived, list):
        issues.append(f"derived_from must be an array, got {type(derived).__name__}")
    else:
        for i, src in enumerate(derived):
            if not isinstance(src, dict):
                issues.append(f"derived_from[{i}] must be an object, got {type(src).__name__}")
                continue
            t = src.get("type")
            if not isinstance(t, str) or not t.strip():
                issues.append(f"derived_from[{i}].type is required and must be a non-empty string")
            title = src.get("title")
            if not isinstance(title, str) or not title.strip():
                issues.append(f"derived_from[{i}].title is required and must be a non-empty string")
            # reference may be a string OR null (honest "no addressable identifier")
            if "reference" in src:
                ref = src["reference"]
                if ref is not None and not isinstance(ref, str):
                    issues.append(f"derived_from[{i}].reference must be a string or null, got {type(ref).__name__}")
            # hash is optional but if present must look like sha256:<hex>
            if "hash" in src:
                check_pattern(src.get("hash"), HASH_FORMAT, f"derived_from[{i}].hash")

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


def _capsule_root_inner(html: str) -> str:
    """Return inner HTML for <main id="capsule-root">."""
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
                return rest[: i - nxt.end() + nxt.start()]
        else:
            depth += 1
    return ""


def _capsule_root_text(html: str) -> str:
    """Return the visible text inside <main id="capsule-root">, with
    <script> and <style> blocks removed."""
    inner = _capsule_root_inner(html)
    if not inner:
        return ""
    inner = re.sub(r"<script\b[^>]*>.*?</script>", "",
                   inner, flags=re.IGNORECASE | re.DOTALL)
    inner = re.sub(r"<style\b[^>]*>.*?</style>", "",
                   inner, flags=re.IGNORECASE | re.DOTALL)
    text = _TAG_RE.sub(" ", inner)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


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

    root_inner = _capsule_root_inner(html)
    text = _capsule_root_text(html)
    n = len(text)
    has_heading = bool(re.search(r"<h[1-6]\b", root_inner, re.IGNORECASE))
    key_markup_count = sum(
        1 for pattern in (
            r"<section\b",
            r"<article\b",
            r"<table\b",
            r"<ul\b",
            r"<ol\b",
            r"<dl\b",
            r"<figure\b",
            r"<img\b",
            r"<audio\b",
            r"<video\b",
            r"<details\b",
        )
        if re.search(pattern, root_inner, re.IGNORECASE)
    )
    ok = n >= PROGRESSIVE_ENHANCEMENT_MIN_TEXT and (has_heading or key_markup_count > 0)
    if ok:
        markers = []
        if has_heading:
            markers.append("heading")
        if key_markup_count:
            markers.append(f"{key_markup_count} structural/media marker(s)")
        detail = f"{n} chars of visible text in <main id=\"capsule-root\">; " + ", ".join(markers)
    else:
        missing = []
        if n < PROGRESSIVE_ENHANCEMENT_MIN_TEXT:
            missing.append(f"visible text below {PROGRESSIVE_ENHANCEMENT_MIN_TEXT} chars")
        if not has_heading and key_markup_count == 0:
            missing.append("no heading, structural section, table/list, or media/fallback marker detected")
        detail = (
            f"{n} chars of visible text in <main id=\"capsule-root\">; "
            f"{'; '.join(missing)}. This capsule may rely on runtime JavaScript "
            f"to render its primary meaning. Per Core rule 12, capsules should "
            f"pre-render title/summary/key sections or equivalent fallback content "
            f"in the HTML so they remain readable in "
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


def _html_id_exists(html: str, element_id: str) -> bool:
    pattern = r'\bid\s*=\s*(["\'])' + re.escape(element_id) + r'\1'
    return re.search(pattern, html, re.IGNORECASE) is not None


def _is_extension_name(name: str) -> bool:
    return name.startswith("x-") or "." in name


def check_presentations(manifest: dict, html: str, result: ValidationResult):
    if manifest is None:
        return

    presentations = manifest.get("presentations")
    if presentations is None:
        result.add(
            "Presentation declarations are valid/resolvable",
            "pass",
            "No presentations declared; consumers must not infer capsule-owned views from layout.",
        )
        return

    if not isinstance(presentations, list):
        result.add(
            "Presentation declarations are valid/resolvable",
            "fail",
            f"presentations must be an array, got {type(presentations).__name__}",
        )
        return

    failures = []
    warnings = []
    seen_ids = set()

    for i, presentation in enumerate(presentations):
        label = f"presentations[{i}]"
        if not isinstance(presentation, dict):
            failures.append(f"{label} must be an object, got {type(presentation).__name__}")
            continue

        presentation_id = presentation.get("id")
        profile = presentation.get("profile")
        entry = presentation.get("entry")
        required = presentation.get("required", False)

        if "required" in presentation and not isinstance(required, bool):
            failures.append(f"{label}.required must be boolean when present")
            required = False

        if not isinstance(presentation_id, str) or not PRESENTATION_ID_FORMAT.match(presentation_id):
            failures.append(f"{label}.id is required and must match {PRESENTATION_ID_FORMAT.pattern}")
        elif presentation_id in seen_ids:
            failures.append(f"{label}.id duplicates {presentation_id!r}")
        else:
            seen_ids.add(presentation_id)

        if not isinstance(profile, str) or not CAPABILITY_NAME_FORMAT.match(profile):
            failures.append(f"{label}.profile is required and must be a valid name")
        elif profile not in VALID_PRESENTATION_PROFILES and not _is_extension_name(profile):
            message = (
                f"{label}.profile={profile!r} is not a core profile and is not namespaced; "
                f"core profiles: {sorted(VALID_PRESENTATION_PROFILES)}"
            )
            if required:
                failures.append(message)
            else:
                warnings.append(message)

        if not isinstance(entry, str) or not PRESENTATION_ENTRY_FORMAT.match(entry):
            failures.append(f"{label}.entry is required and must be a fragment selector like #capsule-root")
        else:
            target_id = entry[1:]
            if not _html_id_exists(html, target_id):
                message = f"{label}.entry={entry!r} does not resolve to an element id in this Capsule"
                if required:
                    failures.append(message)
                else:
                    warnings.append(message)
            elif required and profile == "reader" and entry == "#capsule-root":
                text_len = len(_capsule_root_text(html))
                if text_len < PROGRESSIVE_ENHANCEMENT_MIN_TEXT:
                    failures.append(
                        f"{label} is required reader view but capsule-root has only {text_len} "
                        f"chars of visible text; primary meaning must be readable without JavaScript"
                    )

        media = presentation.get("media")
        if media is not None and not isinstance(media, str):
            failures.append(f"{label}.media must be a string when present")

        navigation = presentation.get("navigation")
        if navigation is not None:
            if not isinstance(navigation, str):
                failures.append(f"{label}.navigation must be a string when present")
            elif navigation not in VALID_PRESENTATION_NAVIGATION:
                message = (
                    f"{label}.navigation={navigation!r} is not recognized; "
                    f"known values: {sorted(VALID_PRESENTATION_NAVIGATION)}"
                )
                if required:
                    failures.append(message)
                else:
                    warnings.append(message)

        chrome = presentation.get("chrome")
        if chrome is not None:
            if not isinstance(chrome, str):
                failures.append(f"{label}.chrome must be a string when present")
            elif chrome not in VALID_PRESENTATION_CHROME:
                message = (
                    f"{label}.chrome={chrome!r} is not recognized; "
                    f"known values: {sorted(VALID_PRESENTATION_CHROME)}"
                )
                if required:
                    failures.append(message)
                else:
                    warnings.append(message)

        for text_field in ("title", "description"):
            value = presentation.get(text_field)
            if value is not None and not isinstance(value, str):
                failures.append(f"{label}.{text_field} must be a string when present")

    if failures:
        result.add(
            "Presentation declarations are valid/resolvable",
            "fail",
            "; ".join(failures + warnings),
        )
    elif warnings:
        result.add(
            "Presentation declarations are valid/resolvable",
            "warn",
            "; ".join(warnings),
            heuristic=True,
        )
    else:
        result.add(
            "Presentation declarations are valid/resolvable",
            "pass",
            f"{len(presentations)} declared presentation(s); entries resolve.",
        )


def check_fullscreen_exit(manifest: dict, html: str, result: ValidationResult):
    """A capsule-owned presentation (chrome 'capsule') draws its own controls and
    a conforming host recedes its own chrome, so the capsule must ship its own way
    back to the host's main view. The convention is a control marked
    data-capsule-action="exit" — its runtime requests the host to return
    (window.capsuleHost.exit() / a capsule:exit message), falling back to
    history/close when opened with no host. An X is enough. WARN, not fail: a
    compliant host can fall back to drawing its own escape for capsules that omit
    it, so this stays advisory until the convention is universal across the
    corpus."""
    if manifest is None:
        return
    presentations = manifest.get("presentations")
    if not isinstance(presentations, list):
        return
    needs_exit = any(
        isinstance(p, dict) and p.get("chrome") == "capsule"
        for p in presentations
    )
    if not needs_exit:
        result.add(
            "Capsule-owned full-screen view provides an exit hatch",
            "pass",
            "No capsule-owned full-screen (reel + chrome:capsule) presentation declared.",
        )
        return
    has_exit = re.search(r'data-capsule-action\s*=\s*["\']exit["\']', html, re.IGNORECASE) is not None
    result.add(
        "Capsule-owned full-screen view provides an exit hatch",
        "pass" if has_exit else "warn",
        "" if has_exit else (
            "A presentation declares profile 'reel' with chrome 'capsule' but no control "
            "marked data-capsule-action=\"exit\" was found. A capsule-owned full-screen view "
            "hides host chrome, so it must include its own exit back to the host (an X is "
            "enough); otherwise the host has to draw its own escape."
        ),
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
    check_sealed_sources(data, result)
    check_domain_guidance(manifest, data, result)
    check_annotation_shape(manifest, data, result)
    check_profile_overlay(manifest, result)
    check_integrity_hash(manifest, data, html, result, html_source_path=str(path))
    check_field_formats(manifest, result)
    check_capability_classes(manifest, result)
    check_capability_truthfulness(manifest, html, result)
    check_runtime_js_string_literals(html, result)
    check_progressive_enhancement(manifest, html, result)
    check_presentations(manifest, html, result)
    check_fullscreen_exit(manifest, html, result)
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
    parser.add_argument(
        "--version",
        action="version",
        version=f"htmlcapsule reference validator {VALIDATOR_VERSION} (enforces full spec v{VALIDATOR_VERSION})",
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
    print(f"  Validator version: {VALIDATOR_VERSION} (enforces full spec v{VALIDATOR_VERSION})")
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
