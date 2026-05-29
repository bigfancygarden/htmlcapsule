#!/usr/bin/env python3
"""
Bundle Validator v0.1.1

Validates a Bundle directory or zip archive against spec/BUNDLE_SPEC.md v0.1.x.

Usage:
  validate_bundle.py <bundle_dir_or_zip> [--quiet]

Exit codes:
  0  All checks passed
  1  One or more checks failed
  2  Could not read or parse the bundle
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse


BUNDLE_VERSION_KNOWN = {"0.1.0", "0.1.1"}
BUNDLE_PROFILE_KNOWN = {"viewer", "data_package", "multi_entry", "project_archive"}
SHA256_FORMAT = re.compile(r"^sha256:[a-f0-9]{64}$")
UUID_FORMAT = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
SEMVER_FORMAT = re.compile(r"^\d+\.\d+\.\d+$")
HTML_REF_RE = re.compile(
    r"""\b(?:href|src|poster)\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE,
)
CSS_URL_RE = re.compile(
    r"""url\(\s*["']?([^"')]+)["']?\s*\)""",
    re.IGNORECASE,
)


class ValidationResult:
    def __init__(self):
        self.checks: list[dict] = []

    def add(self, name: str, level, details: str = ""):
        if level is True:
            level = "pass"
        elif level is False:
            level = "fail"
        self.checks.append({"name": name, "level": level, "details": details})

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


def sha256_hex_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_external_ref(ref: str) -> bool:
    scheme = urlparse(ref).scheme.lower()
    return scheme in {"http", "https"}


def is_ignored_ref(ref: str) -> bool:
    ref = ref.strip()
    if not ref or ref.startswith("#"):
        return True
    scheme = urlparse(ref).scheme.lower()
    return scheme in {"data", "mailto", "tel", "blob"}


def is_safe_relative_path(path: str) -> bool:
    if not path or "\\" in path:
        return False
    parsed = urlparse(path)
    if parsed.scheme or parsed.netloc:
        return False
    if path.startswith("/"):
        return False
    parts = [p for p in path.split("/") if p not in ("", ".")]
    return ".." not in parts


def is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    mode = info.external_attr >> 16
    return stat.S_IFMT(mode) == stat.S_IFLNK


def normalize_ref(base_file: str, ref: str) -> str:
    ref_path = ref.split("#", 1)[0].split("?", 1)[0]
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(base_file), ref_path))
    return joined


def resolve_local_ref(base_file: str, ref: str):
    raw = ref.split("#", 1)[0].split("?", 1)[0]
    if not raw or "\\" in raw or raw.startswith("/"):
        return None
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        return None
    resolved = normalize_ref(base_file, raw)
    if resolved == ".." or resolved.startswith("../"):
        return None
    return resolved


def load_bundle_root(input_path: Path):
    """Return (root_path, cleanup_path_or_none)."""
    if input_path.is_dir():
        return input_path, None
    if not input_path.exists():
        raise FileNotFoundError(f"Bundle not found: {input_path}")
    if not zipfile.is_zipfile(input_path):
        raise ValueError(f"Expected a bundle directory or zip archive: {input_path}")

    tmpdir = Path(tempfile.mkdtemp(prefix="htmlcapsule-bundle-"))
    with zipfile.ZipFile(input_path) as zf:
        for info in zf.infolist():
            name = info.filename
            if name.endswith("/"):
                continue
            if not is_safe_relative_path(name):
                raise ValueError(f"Unsafe zip entry path: {name!r}")
            if is_zip_symlink(info):
                raise ValueError(f"Bundle zip entries must not be symbolic links: {name!r}")
        zf.extractall(tmpdir)
    return tmpdir, tmpdir


def load_manifest(root: Path, result: ValidationResult):
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        result.add("Root manifest present", False, "Missing manifest.json at bundle root")
        return None
    result.add("Root manifest present", True)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        result.add("Manifest JSON parseable", False, str(e))
        return None
    result.add("Manifest JSON parseable", True)
    return manifest


def check_manifest_shape(manifest: dict | None, result: ValidationResult):
    if manifest is None:
        return
    required = {
        "bundle_version": str,
        "uuid": str,
        "title": str,
        "entry": str,
        "files": list,
    }
    missing = [k for k in required if k not in manifest]
    wrong = [
        f"{k} expected {t.__name__}, got {type(manifest[k]).__name__}"
        for k, t in required.items()
        if k in manifest and not isinstance(manifest[k], t)
    ]
    result.add("Required manifest fields present", not missing, "" if not missing else ", ".join(missing))
    result.add("Required manifest fields have correct types", not wrong, "" if not wrong else "; ".join(wrong))

    version = manifest.get("bundle_version")
    version_ok = isinstance(version, str) and SEMVER_FORMAT.match(version) and version in BUNDLE_VERSION_KNOWN
    result.add(
        "bundle_version is recognized",
        bool(version_ok),
        "" if version_ok else f"Got {version!r}; known: {sorted(BUNDLE_VERSION_KNOWN)}",
    )

    uuid_value = manifest.get("uuid")
    result.add("uuid is valid UUIDv4", isinstance(uuid_value, str) and bool(UUID_FORMAT.match(uuid_value)),
               "" if isinstance(uuid_value, str) and UUID_FORMAT.match(uuid_value) else f"Got {uuid_value!r}")

    bundle_profile = manifest.get("bundle_profile")
    if bundle_profile is None:
        result.add(
            "bundle_profile is declared and recognized",
            "warn",
            f"Missing bundle_profile; recommended values: {sorted(BUNDLE_PROFILE_KNOWN)}",
        )
    elif isinstance(bundle_profile, str) and bundle_profile in BUNDLE_PROFILE_KNOWN:
        result.add("bundle_profile is declared and recognized", True, bundle_profile)
    else:
        result.add(
            "bundle_profile is declared and recognized",
            False,
            f"Got {bundle_profile!r}; known: {sorted(BUNDLE_PROFILE_KNOWN)}",
        )


def listed_files(manifest: dict | None):
    if not manifest or not isinstance(manifest.get("files"), list):
        return {}
    out = {}
    for i, item in enumerate(manifest["files"]):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            out[item["path"]] = (i, item)
    return out


def check_file_inventory(root: Path, manifest: dict | None, result: ValidationResult):
    if manifest is None:
        return set()

    files = manifest.get("files") if isinstance(manifest.get("files"), list) else []
    issues = []
    seen = set()
    listed = {}

    for i, item in enumerate(files):
        if not isinstance(item, dict):
            issues.append(f"files[{i}] must be an object")
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path:
            issues.append(f"files[{i}].path is required")
            continue
        if path in seen:
            issues.append(f"Duplicate file path listed: {path}")
        seen.add(path)
        if path == "manifest.json":
            issues.append("manifest.json must not be listed in files[]; the manifest is not self-hashing")
            continue
        if not is_safe_relative_path(path):
            issues.append(f"Unsafe file path: {path!r}")
            continue

        actual_path = root / Path(*path.split("/"))
        if not actual_path.exists():
            issues.append(f"Listed file missing: {path}")
            continue
        if actual_path.is_symlink():
            issues.append(f"Listed path must not be a symbolic link: {path}")
            continue
        if not actual_path.is_file():
            issues.append(f"Listed path is not a file: {path}")
            continue

        listed[path] = item

        size = item.get("size")
        if not isinstance(size, int) or size < 0:
            issues.append(f"{path}: size must be a non-negative integer")
        elif actual_path.stat().st_size != size:
            issues.append(f"{path}: declared size {size}, actual {actual_path.stat().st_size}")

        declared_hash = item.get("sha256")
        if not isinstance(declared_hash, str) or not SHA256_FORMAT.match(declared_hash):
            issues.append(f"{path}: sha256 must match sha256:<64 hex>")
        else:
            actual_hash = "sha256:" + sha256_hex_bytes(actual_path.read_bytes())
            if actual_hash != declared_hash:
                issues.append(f"{path}: declared hash {declared_hash}, actual {actual_hash}")

    result.add("File inventory entries are valid and verify", not issues, "; ".join(issues))

    symlink_paths = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_symlink()
    )
    payload_files = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if not p.is_symlink() and p.is_file() and p.relative_to(root).as_posix() != "manifest.json"
    }
    unlisted = sorted(payload_files - set(listed.keys()))
    inventory_issues = []
    if unlisted:
        inventory_issues.append("Unlisted files: " + ", ".join(unlisted))
    if symlink_paths:
        inventory_issues.append("Symbolic links are not allowed: " + ", ".join(symlink_paths))
    result.add(
        "All payload files are listed and no symlinks present",
        not inventory_issues,
        "; ".join(inventory_issues),
    )

    return set(listed.keys())


def entry_paths(manifest: dict | None):
    if not manifest:
        return []
    paths = []
    if isinstance(manifest.get("entry"), str):
        paths.append(manifest["entry"])
    entries = manifest.get("entries")
    if isinstance(entries, dict):
        for value in entries.values():
            if isinstance(value, str):
                paths.append(value)
            elif isinstance(value, dict) and isinstance(value.get("path"), str):
                paths.append(value["path"])
    return paths


def check_entries(root: Path, manifest: dict | None, listed: set, result: ValidationResult):
    issues = []
    for path in entry_paths(manifest):
        if not is_safe_relative_path(path):
            issues.append(f"Unsafe entry path: {path!r}")
            continue
        if path not in listed:
            issues.append(f"Entry path not listed in files[]: {path}")
        p = root / Path(*path.split("/"))
        if not p.exists():
            issues.append(f"Entry file missing: {path}")
        elif p.suffix.lower() not in {".html", ".htm"}:
            issues.append(f"Entry file should be HTML: {path}")
    result.add("Entry HTML files exist and are listed", not issues, "; ".join(issues))


def declared_external_urls(manifest: dict | None):
    deps = []
    if not manifest:
        return deps
    raw = manifest.get("external_dependencies") or []
    if not isinstance(raw, list):
        return deps
    for item in raw:
        if isinstance(item, str):
            deps.append(item)
        elif isinstance(item, dict) and isinstance(item.get("url"), str):
            deps.append(item["url"])
    return deps


def external_declared(ref: str, declared: list[str]) -> bool:
    for dep in declared:
        if ref == dep:
            return True
        if dep.endswith("/") and ref.startswith(dep):
            return True
    return False


def references_in_file(root: Path, path: str):
    p = root / Path(*path.split("/"))
    suffix = p.suffix.lower()
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    refs = []
    if suffix in {".html", ".htm"}:
        refs.extend(m.group(1).strip() for m in HTML_REF_RE.finditer(text))
        refs.extend(m.group(1).strip() for m in CSS_URL_RE.finditer(text))
    elif suffix == ".css":
        refs.extend(m.group(1).strip() for m in CSS_URL_RE.finditer(text))
    return refs


def check_references(root: Path, manifest: dict | None, listed: set, result: ValidationResult):
    if manifest is None:
        return
    declared = declared_external_urls(manifest)
    local_missing = []
    local_unlisted = []
    external_undeclared = []
    unsafe_refs = []

    for path in sorted(listed):
        if not path.lower().endswith((".html", ".htm", ".css")):
            continue
        for ref in references_in_file(root, path):
            if is_ignored_ref(ref):
                continue
            if is_external_ref(ref):
                if not external_declared(ref, declared):
                    external_undeclared.append(f"{path} -> {ref}")
                continue
            resolved = resolve_local_ref(path, ref)
            if resolved is None:
                unsafe_refs.append(f"{path} -> {ref}")
                continue
            if resolved not in listed:
                local_unlisted.append(f"{path} -> {ref} resolves to {resolved}")
            if not (root / Path(*resolved.split("/"))).exists():
                local_missing.append(f"{path} -> {ref} resolves to {resolved}")

    issues = []
    if unsafe_refs:
        issues.append("Unsafe local refs: " + "; ".join(unsafe_refs))
    if local_missing:
        issues.append("Missing local refs: " + "; ".join(local_missing))
    if local_unlisted:
        issues.append("Unlisted local refs: " + "; ".join(local_unlisted))
    if external_undeclared:
        issues.append("Undeclared external refs: " + "; ".join(external_undeclared))
    result.add("Viewer references stay inside bundle or are declared external deps", not issues, "; ".join(issues))

    if declared:
        result.add("External dependencies declared", "warn", f"{len(declared)} declared; bundle may need network access")
    else:
        result.add("No external dependencies declared", "pass")


def validate_bundle(input_path: Path) -> ValidationResult:
    root, cleanup = load_bundle_root(input_path)
    try:
        result = ValidationResult()
        manifest = load_manifest(root, result)
        check_manifest_shape(manifest, result)
        listed = check_file_inventory(root, manifest, result)
        check_entries(root, manifest, listed, result)
        check_references(root, manifest, listed, result)
        return result
    finally:
        if cleanup is not None:
            shutil.rmtree(cleanup, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Validate a Bundle directory or zip archive.")
    parser.add_argument("bundle", type=Path, help="Path to a Bundle directory or zip archive")
    parser.add_argument("--quiet", action="store_true", help="Only print summary and failures")
    args = parser.parse_args()

    try:
        result = validate_bundle(args.bundle)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Validation crashed: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"Validating Bundle: {args.bundle}")
    print(f"  Bundle versions recognized: {sorted(BUNDLE_VERSION_KNOWN)}")
    print()
    markers = {"pass": "+", "warn": "!", "fail": "x"}
    status_words = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}
    for check in result.checks:
        level = check["level"]
        if level == "pass" and args.quiet:
            continue
        line = f"  [{status_words[level]}] {markers[level]} {check['name']}"
        if check["details"]:
            line += f"\n         {check['details']}"
        print(line)

    print()
    total = len(result.checks)
    print(f"Result: {result.passed_count}/{total} pass, {result.warn_count} warn, {result.failed_count} fail")
    sys.exit(0 if result.all_passed else 1)


if __name__ == "__main__":
    main()
