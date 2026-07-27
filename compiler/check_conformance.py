#!/usr/bin/env python3
"""
check_conformance.py — run the reference implementation against
spec/conformance/hash_vectors.json.

The fixture is the contract; this is one implementation's proof that it meets
it. The equivalent runner for JavaScript lives in tools/check-conformance.mjs,
and every other implementation in the fleet is expected to grow one. F44 named
the failure this prevents: a test vector published only in prose was not pinned
by a consuming implementation, which then filed a false "tampered" verdict
against a valid capsule.

Usage:
  check_conformance.py [path/to/hash_vectors.json] [--verbose]

Exit codes:
  0  every vector and unit case passed
  1  at least one failed
  2  the fixture could not be read
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import jcs  # noqa: E402
from validate import canonical_json as legacy_canonical  # noqa: E402

DEFAULT_FIXTURE = Path(__file__).resolve().parent.parent / "spec" / "conformance" / "hash_vectors.json"

RECIPES = {
    "v1-legacy": legacy_canonical,
    "v2-jcs": jcs.canonicalize,
}


class Report:
    def __init__(self, verbose: bool = False):
        self.passed = 0
        self.failed = 0
        self.verbose = verbose

    def check(self, label: str, got, want) -> bool:
        if got == want:
            self.passed += 1
            if self.verbose:
                print(f"  ok   {label}")
            return True
        self.failed += 1
        print(f"  FAIL {label}")
        print(f"         got:  {got!r}")
        print(f"         want: {want!r}")
        return False

    def ok(self, label: str) -> None:
        self.passed += 1
        if self.verbose:
            print(f"  ok   {label}")

    def fail(self, label: str, detail: str) -> None:
        self.failed += 1
        print(f"  FAIL {label}\n         {detail}")


def run_vectors(fixture: dict, report: Report) -> None:
    print("Vectors")
    for vector in fixture["vectors"]:
        vid, recipe_name = vector["id"], vector["recipe"]
        canonical = RECIPES.get(recipe_name)
        if canonical is None:
            report.fail(f"{vid}: recipe", f"unknown recipe {recipe_name!r}")
            continue
        try:
            manifest = json.loads(vector["manifest_json"])
            data = json.loads(vector["data_json"])
            canonical_manifest = canonical(manifest)
            canonical_data = canonical(data)
        except Exception as exc:  # noqa: BLE001 - report, don't crash the suite
            report.fail(f"{vid}: canonicalize", f"{type(exc).__name__}: {exc}")
            continue
        report.check(f"{vid} [{recipe_name}] canonical manifest", canonical_manifest, vector["canonical_manifest"])
        report.check(f"{vid} [{recipe_name}] canonical data", canonical_data, vector["canonical_data"])
        payload = canonical_manifest + "\n" + canonical_data
        report.check(f"{vid} [{recipe_name}] canonical payload", payload, vector["canonical_payload"])
        digest = "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()
        report.check(f"{vid} [{recipe_name}] content hash", digest, vector["expected_hash"])


def _double(hex_bits: str) -> float:
    return struct.unpack(">d", bytes.fromhex(hex_bits))[0]


def run_units(fixture: dict, report: Report) -> None:
    units = fixture.get("unit_tests", {})

    print("Numbers (ECMAScript Number::toString)")
    for case in units.get("jcs_numbers", []):
        value = _double(case["ieee754_hex"])
        try:
            report.check(f"0x{case['ieee754_hex']}", jcs.es_number(value), case["expected"])
        except jcs.JcsError as exc:
            report.fail(f"0x{case['ieee754_hex']}", f"unexpected error: {exc}")

    print("Strings")
    for case in units.get("jcs_strings", []):
        try:
            report.check(case.get("note", case["input_json"]),
                         jcs.canonicalize(json.loads(case["input_json"])), case["expected"])
        except jcs.JcsError as exc:
            report.fail(case["input_json"], f"unexpected error: {exc}")

    print("Key order (UTF-16 code units)")
    for case in units.get("jcs_key_order", []):
        try:
            report.check(case.get("note", case["input_json"]),
                         jcs.canonicalize(json.loads(case["input_json"])), case["expected"])
        except jcs.JcsError as exc:
            report.fail(case["input_json"], f"unexpected error: {exc}")

    print("Must error")
    for case in units.get("jcs_must_error", []):
        label = case["case"]
        if "ieee754_hex" in case:
            try:
                produced = jcs.es_number(_double(case["ieee754_hex"]))
                report.fail(label, f"expected an error, produced {produced!r}")
            except jcs.JcsError:
                report.ok(label)
        elif "input_json" in case:
            # json.loads keeps Python ints arbitrary-precision, so the
            # out-of-range integer survives parsing and must be rejected here.
            try:
                produced = jcs.canonicalize(json.loads(case["input_json"]))
                report.fail(label, f"expected an error, produced {produced!r}")
            except jcs.JcsError:
                report.ok(label)
        else:
            # Cases with no machine-readable input (lone surrogate) are
            # exercised directly, since JSON text cannot carry one unpaired.
            try:
                jcs.es_string("a" + chr(0xD800) + "b")
                report.fail(label, "expected an error for a lone surrogate")
            except jcs.JcsError:
                report.ok(label)


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--verbose"]
    verbose = "--verbose" in sys.argv[1:]
    path = Path(args[0]) if args else DEFAULT_FIXTURE
    try:
        fixture = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot read fixture {path}: {exc}", file=sys.stderr)
        return 2

    print(f"Conformance fixture: {path}")
    print(f"  schema: {fixture.get('schema')}")
    print()
    report = Report(verbose=verbose)
    run_vectors(fixture, report)
    print()
    run_units(fixture, report)
    print()
    total = report.passed + report.failed
    print(f"Result: {report.passed}/{total} pass, {report.failed} fail")
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
