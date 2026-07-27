/**
 * check-conformance.mjs — run the JavaScript implementation against
 * spec/conformance/hash_vectors.json.
 *
 * The counterpart of compiler/check_conformance.py. Two independent
 * implementations passing the same fixture is the whole point: F44 recorded
 * what happens when a consuming implementation is never checked against the
 * published vectors.
 *
 * Usage:  node tools/check-conformance.mjs [path/to/hash_vectors.json]
 * Exit:   0 all passed · 1 something failed · 2 fixture unreadable
 */

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import {
  canonicalizeText, escapeString, numberJcs, sha256Hex,
} from "./capsule-hash.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const DEFAULT_FIXTURE = resolve(here, "..", "spec", "conformance", "hash_vectors.json");

let passed = 0, failed = 0;

function check(label, got, want) {
  if (got === want) { passed++; return true; }
  failed++;
  console.log(`  FAIL ${label}`);
  console.log(`         got:  ${JSON.stringify(got)}`);
  console.log(`         want: ${JSON.stringify(want)}`);
  return false;
}
function expectThrow(label, fn) {
  try { const out = fn(); failed++; console.log(`  FAIL ${label}\n         expected an error, produced ${JSON.stringify(out)}`); }
  catch { passed++; }
}

function doubleFromHex(hex) {
  const dv = new DataView(new ArrayBuffer(8));
  for (let i = 0; i < 8; i++) dv.setUint8(i, parseInt(hex.slice(i * 2, i * 2 + 2), 16));
  return dv.getFloat64(0, false);
}

const path = process.argv[2] ? resolve(process.argv[2]) : DEFAULT_FIXTURE;
let fixture;
try {
  fixture = JSON.parse(await readFile(path, "utf8"));
} catch (err) {
  console.error(`ERROR: cannot read fixture ${path}: ${err.message}`);
  process.exit(2);
}

console.log(`Conformance fixture: ${path}`);
console.log(`  schema: ${fixture.schema}`);
console.log();

console.log("Vectors");
for (const v of fixture.vectors) {
  const label = `${v.id} [${v.recipe}]`;
  let canonicalManifest, canonicalData;
  try {
    canonicalManifest = canonicalizeText(v.manifest_json, v.recipe);
    canonicalData = canonicalizeText(v.data_json, v.recipe);
  } catch (err) {
    failed++;
    console.log(`  FAIL ${label} canonicalize\n         ${err.message}`);
    continue;
  }
  check(`${label} canonical manifest`, canonicalManifest, v.canonical_manifest);
  check(`${label} canonical data`, canonicalData, v.canonical_data);
  const payload = canonicalManifest + "\n" + canonicalData;
  check(`${label} canonical payload`, payload, v.canonical_payload);
  check(`${label} content hash`, "sha256:" + (await sha256Hex(payload)), v.expected_hash);
}

console.log("Numbers (ECMAScript Number::toString)");
for (const c of fixture.unit_tests.jcs_numbers) {
  const value = doubleFromHex(c.ieee754_hex);
  // These cases are doubles by construction (they arrive as bit patterns), so
  // they are serialized as floats. That matters: a float of magnitude 1e20 is
  // legal, while the *integer token* 100000000000000000000 is not — integers
  // are range-checked to |n| <= 2**53 and floats are exempt, because a float
  // already is a double (spec §9.1.1, recipe v2).
  try {
    check(`0x${c.ieee754_hex}`, numberJcs({ t: "num", src: String(value), isFloat: true }), c.expected);
  } catch (err) {
    failed++;
    console.log(`  FAIL 0x${c.ieee754_hex}\n         unexpected error: ${err.message}`);
  }
}

console.log("Strings");
for (const c of fixture.unit_tests.jcs_strings) {
  try { check(c.note ?? c.input_json, canonicalizeText(c.input_json, "v2-jcs"), c.expected); }
  catch (err) { failed++; console.log(`  FAIL ${c.input_json}\n         unexpected error: ${err.message}`); }
}

console.log("Key order (UTF-16 code units)");
for (const c of fixture.unit_tests.jcs_key_order) {
  try { check(c.note ?? c.input_json, canonicalizeText(c.input_json, "v2-jcs"), c.expected); }
  catch (err) { failed++; console.log(`  FAIL ${c.input_json}\n         unexpected error: ${err.message}`); }
}

console.log("Must error");
for (const c of fixture.unit_tests.jcs_must_error) {
  if (c.ieee754_hex) {
    const v = doubleFromHex(c.ieee754_hex);
    expectThrow(c.case, () => numberJcs({ t: "num", src: String(v), isFloat: true }));
  } else if (c.input_json) {
    expectThrow(c.case, () => canonicalizeText(c.input_json, "v2-jcs"));
  } else {
    expectThrow(c.case, () => escapeString("a\uD800b"));
  }
}

console.log();
console.log(`Result: ${passed}/${passed + failed} pass, ${failed} fail`);
process.exit(failed === 0 ? 0 : 1);
