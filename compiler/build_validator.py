#!/usr/bin/env python3
"""
build_validator.py — assemble the self-contained browser validator page.

Why a build step for one HTML file: the hash implementation must have exactly
one source of truth (`tools/capsule-hash.mjs`, which is also what Node runs
against the conformance suite), but the page has to be a single self-contained
file that works from `file://` with no network. So the module is inlined here
rather than imported at runtime — an ES module import would fail under
`file://` and would break the offline promise the format itself makes.

The page also self-tests on load against real vectors lifted from
`spec/conformance/hash_vectors.json`, so a visitor can see that the page's own
hasher is correct before trusting a verdict it gives them.

Usage:  build_validator.py            # writes tools/validator.html
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "tools" / "validator.template.html"
MODULE = REPO / "tools" / "capsule-hash.mjs"
FIXTURE = REPO / "spec" / "conformance" / "hash_vectors.json"
OUTPUT = REPO / "tools" / "validator.html"

# One vector per recipe: enough to prove both code paths on load without
# bloating the page. A (legacy, no floats) and B2 (JCS, the float battery).
SELF_TEST_IDS = ("A", "B", "A2", "B2")


def main() -> int:
    for path in (TEMPLATE, MODULE, FIXTURE):
        if not path.exists():
            print(f"ERROR: missing {path}", file=sys.stderr)
            return 2

    template = TEMPLATE.read_text(encoding="utf-8")
    module = MODULE.read_text(encoding="utf-8")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    vectors = [
        {
            "id": v["id"],
            "recipe": v["recipe"],
            "manifest_json": v["manifest_json"],
            "data_json": v["data_json"],
            "expected_hash": v["expected_hash"],
        }
        for v in fixture["vectors"]
        if v["id"] in SELF_TEST_IDS
    ]
    if len(vectors) != len(SELF_TEST_IDS):
        print(f"ERROR: fixture is missing one of {SELF_TEST_IDS}", file=sys.stderr)
        return 2

    if "/* __CAPSULE_HASH_MJS__ */" not in template or "__SELF_TEST_VECTORS__" not in template:
        print("ERROR: template markers not found", file=sys.stderr)
        return 2

    # The inlined text sits inside <script>; a literal </script> in a string
    # would end the element early. None is expected, but check rather than hope.
    for name, text in (("module", module), ("vectors", json.dumps(vectors))):
        if "</script" in text.lower():
            print(f"ERROR: {name} contains a closing script tag", file=sys.stderr)
            return 2

    page = template.replace("/* __CAPSULE_HASH_MJS__ */", module)
    page = page.replace("__SELF_TEST_VECTORS__", json.dumps(vectors, ensure_ascii=False))
    OUTPUT.write_text(page, encoding="utf-8")

    size = OUTPUT.stat().st_size
    print(f"  wrote {OUTPUT.relative_to(REPO)}  ({size:,} bytes, self-contained)")
    print(f"  inlined {MODULE.relative_to(REPO)} and self-test vectors {', '.join(v['id'] for v in vectors)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
