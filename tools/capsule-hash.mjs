/**
 * capsule-hash.mjs — the Capsule integrity hash (spec §9.1.1) in JavaScript.
 *
 * Both recipes, in one file, with no dependencies:
 *   recipe v1 — legacy canonical JSON, for capsules declaring spec_version
 *               0.1.x-0.3.x. Numbers are formatted the way Python 3's repr()
 *               formats them, because that is what the reference implementation
 *               did when the format was young.
 *   recipe v2 — RFC 8785 (JCS), for capsules declaring 0.4.x. Numbers are
 *               ECMAScript's own, which is why this file is short.
 *
 * Why this exists: until now the hash could only be computed by running Python,
 * so nothing could verify a capsule in the place capsules actually live — a
 * browser (RESEARCH.md F45). Runs unmodified in Node 18+ and in browsers; both
 * provide WebCrypto and TextEncoder.
 *
 * The subtlety worth knowing before you edit anything here: JSON.parse cannot
 * tell 55 from 55.0, and under recipe v1 those two tokens canonicalize
 * differently ("55" vs "55.0") and therefore hash differently. So this file
 * tokenizes JSON itself and keeps each number's source text. Do not be tempted
 * to replace the parser with JSON.parse.
 */

/* ------------------------------------------------------------------ *
 * Tokenizing parser: standard JSON, except numbers keep their source. *
 * ------------------------------------------------------------------ */

/** @returns {{t:'obj'|'arr'|'str'|'num'|'lit', ...}} tagged tree */
export function parseTagged(text) {
  let i = 0;

  const ws = () => {
    while (i < text.length && (text[i] === " " || text[i] === "\t" || text[i] === "\n" || text[i] === "\r")) i++;
  };

  function str() {
    if (text[i] !== '"') throw new SyntaxError(`expected string at ${i}`);
    i++;
    let out = "";
    while (text[i] !== '"') {
      if (i >= text.length) throw new SyntaxError("unterminated string");
      if (text[i] === "\\") {
        const esc = text[++i];
        if (esc === "u") {
          out += String.fromCharCode(parseInt(text.slice(i + 1, i + 5), 16));
          i += 5;
        } else {
          const simple = { '"': '"', "\\": "\\", "/": "/", b: "\b", f: "\f", n: "\n", r: "\r", t: "\t" }[esc];
          if (simple === undefined) throw new SyntaxError(`bad escape \\${esc}`);
          out += simple;
          i++;
        }
      } else {
        out += text[i++];
      }
    }
    i++;
    return out;
  }

  function value() {
    ws();
    const c = text[i];
    if (c === "{") {
      i++;
      const entries = [];
      ws();
      if (text[i] === "}") { i++; return { t: "obj", v: entries }; }
      for (;;) {
        ws();
        const k = str();
        ws();
        if (text[i] !== ":") throw new SyntaxError(`expected ':' at ${i}`);
        i++;
        entries.push([k, value()]);
        ws();
        if (text[i] === ",") { i++; continue; }
        if (text[i] !== "}") throw new SyntaxError(`expected '}' at ${i}`);
        i++;
        return { t: "obj", v: entries };
      }
    }
    if (c === "[") {
      i++;
      const items = [];
      ws();
      if (text[i] === "]") { i++; return { t: "arr", v: items }; }
      for (;;) {
        items.push(value());
        ws();
        if (text[i] === ",") { i++; continue; }
        if (text[i] !== "]") throw new SyntaxError(`expected ']' at ${i}`);
        i++;
        return { t: "arr", v: items };
      }
    }
    if (c === '"') return { t: "str", v: str() };
    if (text.startsWith("true", i)) { i += 4; return { t: "lit", v: "true" }; }
    if (text.startsWith("false", i)) { i += 5; return { t: "lit", v: "false" }; }
    if (text.startsWith("null", i)) { i += 4; return { t: "lit", v: "null" }; }
    const m = /^-?(?:0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/.exec(text.slice(i));
    if (!m) throw new SyntaxError(`unexpected character ${JSON.stringify(c)} at ${i}`);
    i += m[0].length;
    // A token is a "float" if it carries a fraction or an exponent. That is
    // exactly the distinction recipe v1 preserves and JSON.parse destroys.
    return { t: "num", src: m[0], isFloat: Boolean(m[1] || m[2]) };
  }

  const root = value();
  ws();
  if (i !== text.length) throw new SyntaxError(`trailing content at ${i}`);
  return root;
}

/* ------------------------------------------------- *
 * String escaping — identical under both recipes.   *
 * ------------------------------------------------- */

const SHORTHAND = { '"': '\\"', "\\": "\\\\", "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r" };

export function escapeString(s) {
  let out = '"';
  for (const ch of s) {
    const code = ch.codePointAt(0);
    if (SHORTHAND[ch] !== undefined) out += SHORTHAND[ch];
    else if (code < 0x20) out += "\\u" + code.toString(16).padStart(4, "0");
    else if (code >= 0xd800 && code <= 0xdfff) {
      // for..of iterates code points, so a surrogate here is unpaired.
      throw new Error(`lone surrogate U+${code.toString(16).toUpperCase()} in string; input must be valid Unicode`);
    } else out += ch;
  }
  return out + '"';
}

/* --------------------------- *
 * Numbers, per recipe.        *
 * --------------------------- */

/** Recipe v1: Python 3 repr() semantics. */
export function numberLegacy(node) {
  if (!node.isFloat) return node.src; // integers verbatim, arbitrary precision
  const v = Number(node.src);
  if (v === 0) return Object.is(v, -0) ? "-0.0" : "0.0";
  const [mantissa, expText] = v.toExponential().split("e"); // shortest round-trip digits
  const exp = parseInt(expText, 10);
  if (exp < -4 || exp >= 16) {
    // Python's exponent window and style: signed, at least two digits.
    const abs = Math.abs(exp);
    return mantissa + "e" + (exp < 0 ? "-" : "+") + (abs < 10 ? "0" + abs : String(abs));
  }
  // Positional. Integer-valued floats keep the marker that makes them floats.
  return Number.isInteger(v) ? v.toString() + ".0" : v.toString();
}

/** Recipe v2: ECMAScript Number::toString, which is what RFC 8785 specifies. */
export function numberJcs(node) {
  if (!node.isFloat) {
    // Range check on the SOURCE token: Number() would silently round, which is
    // the precise failure the 0.4 line's IEEE-safe rule exists to prevent.
    const asNumber = Number(node.src);
    if (!Number.isSafeInteger(asNumber) && Math.abs(asNumber) > 2 ** 53) {
      throw new Error(
        `integer ${node.src} is outside the IEEE 754 exactly-representable range ` +
        `(|n| <= 2**53); the v0.4 line requires interoperable numbers`
      );
    }
    if (String(asNumber) !== node.src.replace(/^\+/, "")) {
      // e.g. 9007199254740993 parses to ...992: the token cannot survive a
      // double round-trip, so no two implementations would agree on it.
      throw new Error(`integer ${node.src} does not round-trip through IEEE 754 double`);
    }
    return String(asNumber);
  }
  const v = Number(node.src);
  if (!Number.isFinite(v)) throw new Error("NaN and Infinity are not permitted in JSON (RFC 8785)");
  return String(v); // ES Number::toString; 55.0 -> "55", 1.5e-5 -> "0.000015"
}

/* --------------------------- *
 * Key ordering, per recipe.   *
 * --------------------------- */

/** Recipe v1: Unicode code point order. */
function compareCodePoints(a, b) {
  const A = Array.from(a), B = Array.from(b);
  const n = Math.min(A.length, B.length);
  for (let k = 0; k < n; k++) {
    const d = A[k].codePointAt(0) - B[k].codePointAt(0);
    if (d !== 0) return d;
  }
  return A.length - B.length;
}

/** Recipe v2: UTF-16 code units — which is JS's own default string order. */
function compareCodeUnits(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

/* --------------------------- *
 * Canonicalization.           *
 * --------------------------- */

export function canonicalize(node, recipe) {
  const isJcs = recipe === "v2-jcs";
  const num = isJcs ? numberJcs : numberLegacy;
  const cmp = isJcs ? compareCodeUnits : compareCodePoints;

  const walk = (n) => {
    switch (n.t) {
      case "lit": return n.v;
      case "str": return escapeString(n.v);
      case "num": return num(n);
      case "arr": return "[" + n.v.map(walk).join(",") + "]";
      case "obj": {
        const sorted = [...n.v].sort((x, y) => cmp(x[0], y[0]));
        return "{" + sorted.map(([k, v]) => escapeString(k) + ":" + walk(v)).join(",") + "}";
      }
      default: throw new Error(`unknown node ${n.t}`);
    }
  };
  return walk(node);
}

/** Canonicalize a JSON *string* with the given recipe. */
export function canonicalizeText(jsonText, recipe) {
  return canonicalize(parseTagged(jsonText), recipe);
}

/* --------------------------- *
 * Recipe selection + hashing. *
 * --------------------------- */

/**
 * Spec §9.1.1: the recipe is a pure function of the declared spec_version.
 * Returns null when the version cannot be parsed — callers must report an
 * unknown version rather than guess, which is what keeps a version mismatch
 * from masquerading as a tamper.
 */
export function recipeForLine(specVersion) {
  if (typeof specVersion !== "string") return null;
  const parts = specVersion.split(".");
  const major = Number(parts[0]), minor = Number(parts[1]);
  if (!Number.isInteger(major) || !Number.isInteger(minor)) return null;
  return major > 0 || minor >= 4 ? "v2-jcs" : "v1-legacy";
}

/** SHA-256 of UTF-8 text, lowercase hex. Exported so callers that inline this
 *  module (the browser validator) do not declare a second copy. */
export async function sha256Hex(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

const PLACEHOLDER = "sha256:pending";

/**
 * Compute a capsule's content hash from the raw text of its two JSON blocks.
 *
 * Returns { hash, recipe, scope, declared, matches }. Only `data+manifest` and
 * `data_only` are handled here; `full_document` hashes raw file bytes and is
 * recipe-independent (see spec §9.1.1).
 */
export async function contentHash(manifestText, dataText) {
  const manifestNode = parseTagged(manifestText);
  if (manifestNode.t !== "obj") throw new Error("manifest is not a JSON object");

  const entries = new Map(manifestNode.v);
  const specNode = entries.get("spec_version");
  const specVersion = specNode && specNode.t === "str" ? specNode.v : null;
  const recipe = recipeForLine(specVersion);
  if (!recipe) throw new Error(`cannot select a canonicalization recipe: unparseable spec_version ${JSON.stringify(specVersion)}`);

  const integrity = entries.get("integrity");
  let scope = "data+manifest";
  let declared = null;
  if (integrity && integrity.t === "obj") {
    const intMap = new Map(integrity.v);
    const scopeNode = intMap.get("hash_scope");
    if (scopeNode && scopeNode.t === "str") scope = scopeNode.v;
    const hashNode = intMap.get("content_hash");
    if (hashNode && hashNode.t === "str") declared = hashNode.v;
    // Substitute the placeholder in the tagged tree, exactly as the protocol says.
    intMap.set("content_hash", { t: "str", v: PLACEHOLDER });
    integrity.v = [...intMap.entries()];
  }
  if (scope === "full_document") throw new Error("full_document scope hashes raw file bytes; not handled by contentHash()");
  if (scope !== "data+manifest" && scope !== "data_only") throw new Error(`unknown hash_scope: ${scope}`);

  const canonicalData = canonicalizeText(dataText, recipe);
  const payload = scope === "data_only"
    ? canonicalData
    : canonicalize(manifestNode, recipe) + "\n" + canonicalData;

  const hash = "sha256:" + await sha256Hex(payload);
  return { hash, recipe, scope, declared, matches: declared === hash };
}
