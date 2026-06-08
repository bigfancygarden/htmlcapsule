#!/usr/bin/env python3
"""
Repair a Capsule manifest integrity hash deterministically.

Usage:
  repair_integrity.py capsule.html -o capsule.repaired.html
  repair_integrity.py capsule.html --in-place

The tool updates only the `capsule-manifest` JSON block. It computes the hash
using the normative placeholder protocol from spec/CAPSULE_SPEC.md §9.1.1.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HASH_PLACEHOLDER = "sha256:pending"


SCRIPT_PATTERN_TEMPLATE = (
    r'(<script\b[^>]*\bid\s*=\s*["\']{section_id}["\'][^>]*>)'
    r'([\s\S]*?)'
    r'(</script>)'
)


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def extract_script_block(html: str, section_id: str) -> tuple[re.Match, str]:
    pattern = SCRIPT_PATTERN_TEMPLATE.format(section_id=re.escape(section_id))
    match = re.search(pattern, html, re.IGNORECASE)
    if not match:
        raise ValueError(f"missing <script id=\"{section_id}\"> block")
    return match, match.group(2).strip()


def replace_match_inner(html: str, match: re.Match, inner: str) -> str:
    return html[: match.start()] + match.group(1) + inner + match.group(3) + html[match.end() :]


def load_json_block(html: str, section_id: str) -> tuple[re.Match, dict]:
    match, text = extract_script_block(html, section_id)
    try:
        return match, json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{section_id} is not valid JSON: {exc}") from exc


def compute_content_hash(manifest: dict, data: dict, html_with_placeholder: str | None = None) -> str:
    scope = manifest.get("integrity", {}).get("hash_scope", "data+manifest")
    manifest_for_hash = json.loads(json.dumps(manifest))
    manifest_for_hash.setdefault("integrity", {})
    manifest_for_hash["integrity"]["content_hash"] = HASH_PLACEHOLDER

    if scope == "data+manifest":
        payload = canonical_json(manifest_for_hash) + "\n" + canonical_json(data)
        return f"sha256:{sha256_text(payload)}"
    if scope == "data_only":
        return f"sha256:{sha256_text(canonical_json(data))}"
    if scope == "full_document":
        if html_with_placeholder is None:
            raise ValueError("full_document repair requires placeholder HTML")
        return f"sha256:{sha256_bytes(html_with_placeholder.encode('utf-8'))}"
    raise ValueError(f"unknown hash_scope: {scope}")


def repair_html(html: str) -> tuple[str, str, str]:
    manifest_match, manifest = load_json_block(html, "capsule-manifest")
    _, data = load_json_block(html, "capsule-data")

    integrity = manifest.setdefault("integrity", {})
    old_hash = integrity.get("content_hash", "")
    integrity.setdefault("hash_scope", "data+manifest")
    integrity["content_hash"] = HASH_PLACEHOLDER

    placeholder_manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False)
    placeholder_html = replace_match_inner(html, manifest_match, placeholder_manifest_text)
    new_hash = compute_content_hash(manifest, data, html_with_placeholder=placeholder_html)

    integrity["content_hash"] = new_hash
    repaired_manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False)
    repaired_html = replace_match_inner(html, manifest_match, repaired_manifest_text)
    return repaired_html, str(old_hash), new_hash


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair a Capsule integrity.content_hash.")
    parser.add_argument("capsule", type=Path, help="Input Capsule HTML file")
    parser.add_argument("-o", "--output", type=Path, help="Output repaired HTML file")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the input file")
    args = parser.parse_args()

    if args.in_place and args.output:
        parser.error("use either --in-place or --output, not both")
    if not args.in_place and not args.output:
        parser.error("provide --output or --in-place")

    try:
        html = args.capsule.read_text(encoding="utf-8")
        repaired_html, old_hash, new_hash = repair_html(html)
        output_path = args.capsule if args.in_place else args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(repaired_html, encoding="utf-8")
    except Exception as exc:
        print(f"repair_integrity: error: {exc}", file=sys.stderr)
        return 2

    print(f"Repaired {output_path}")
    print(f"  old hash: {old_hash or '(missing)'}")
    print(f"  new hash: {new_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
