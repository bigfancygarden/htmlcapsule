#!/usr/bin/env python3
"""
jcs.py — RFC 8785 (JSON Canonicalization Scheme) for the Capsule v0.4 line.

This is *integrity recipe v2*. It replaces the legacy "serialize the way Python
3's repr does" canonical form (recipe v1, frozen in spec §9.1.1 for verifying
capsules on the 0.3 line and earlier) with the published standard, so that
implementations in other languages can reach byte-identical output using
maintained libraries instead of imitating CPython's formatting habits. See
design/JCS_MIGRATION_PLAN.md and RESEARCH.md F44 for why.

Stdlib only, matching the project discipline. Deliberately independent of the
legacy canonicalizer in validate.py: the two recipes never share code, so
neither can silently drift into the other.

The three parts of RFC 8785:

  1. Numbers are serialized per ECMAScript's `Number::toString` (which is what
     `JSON.stringify` uses). This is the whole reason the standard exists, and
     the part every implementation gets wrong on its own.
  2. Object keys are sorted by their UTF-16 code units as unsigned integers —
     NOT by Unicode code point. The two orders differ for supplementary-plane
     characters (emoji sort before U+FFFF under UTF-16).
  3. Strings escape only what JSON requires: the five shorthand controls, the
     remaining C0 controls as lowercase \\uhhhh, plus quote and backslash.
     Notably U+2028/U+2029 are NOT escaped.

Project-specific constraint on top of the RFC (v0.4 line): integers must be
exactly representable as IEEE 754 doubles (|n| <= 2**53). Python ints are
arbitrary precision, so a value outside that range would round when any other
implementation parsed it — a silent cross-language hash divergence. We raise
instead. Floats are exempt from this check because a Python float already *is*
a double; whatever its magnitude, every implementation sees the same value.
"""

from __future__ import annotations

import math

__all__ = ["canonicalize", "JcsError", "es_number", "es_string", "MAX_SAFE_INT"]

# 2**53 is exactly representable and appears in the RFC's own test table, so
# the bound is inclusive.
MAX_SAFE_INT = 2 ** 53


class JcsError(ValueError):
    """Input cannot be canonicalized under RFC 8785."""


def es_number(value) -> str:
    """Serialize a number per ECMAScript Number::toString (RFC 8785 §3.2.2.3).

    The algorithm is defined over (s, k, n) where s is the shortest decimal
    digit string that round-trips, k is its length, and n positions the decimal
    point such that s * 10**(n-k) == value. Python's repr() already produces
    shortest-round-trip digits, so we recover (s, n) from its text rather than
    reimplementing Grisu/Ryu — a purely textual derivation, no float math, so
    there is nothing to be off-by-one about at the exponent boundaries.
    """
    if isinstance(value, bool):  # bool is a subclass of int; never reached via
        raise JcsError("bool is not a number")  # canonicalize(), kept explicit
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INT:
            raise JcsError(
                f"integer {value} is outside the IEEE 754 exactly-representable range "
                f"(|n| <= 2**53); the v0.4 line requires interoperable numbers"
            )
        return str(value)
    if not isinstance(value, float):
        raise JcsError(f"not a number: {type(value).__name__}")
    if math.isnan(value) or math.isinf(value):
        raise JcsError("NaN and Infinity are not permitted in JSON (RFC 8785 §3.2.2.3)")
    if value == 0:
        return "0"  # covers -0.0, which ECMAScript also renders as "0"

    text = repr(value)
    negative = text.startswith("-")
    if negative:
        text = text[1:]

    mantissa, _, exponent = text.partition("e")
    int_part, _, frac_part = mantissa.partition(".")

    if exponent:
        # repr's exponential form always has exactly one digit before the point.
        digits = (int_part + frac_part).rstrip("0") or "0"
        n = int(exponent) + 1
    elif int_part == "0":
        # "0.000ddd" — leading zeros in the fraction push the point left.
        significant = frac_part.lstrip("0")
        digits = significant.rstrip("0") or "0"
        n = -(len(frac_part) - len(significant))
    else:
        # "ddd" or "ddd.dd" — repr never emits leading zeros here.
        digits = (int_part + frac_part).rstrip("0") or "0"
        n = len(int_part)

    k = len(digits)
    sign = "-" if negative else ""

    if 0 < n <= 21:
        if k <= n:
            return sign + digits + "0" * (n - k)          # integer, pad right
        return sign + digits[:n] + "." + digits[n:]        # point inside digits
    if -6 < n <= 0:
        return sign + "0." + "0" * (-n) + digits           # small, leading zeros
    # Exponential form.
    e = n - 1
    head = digits[0] + ("." + digits[1:] if k > 1 else "")
    return sign + head + "e" + ("+" if e >= 0 else "-") + str(abs(e))


_SHORTHAND = {
    '"': '\\"',
    "\\": "\\\\",
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
}


def es_string(value: str) -> str:
    """Serialize a string per RFC 8785 §3.2.2.2."""
    out = ['"']
    for ch in value:
        escape = _SHORTHAND.get(ch)
        if escape is not None:
            out.append(escape)
        elif ord(ch) < 0x20:
            out.append("\\u%04x" % ord(ch))  # lowercase hex, per the RFC
        elif 0xD800 <= ord(ch) <= 0xDFFF:
            # A lone surrogate cannot be encoded as UTF-8; the RFC requires
            # valid Unicode input. Fail loudly rather than emit invalid bytes.
            raise JcsError(f"lone surrogate U+{ord(ch):04X} in string; input must be valid Unicode")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _sort_key(key: str) -> bytes:
    """Sort keys by UTF-16 code units as unsigned integers (RFC 8785 §3.2.3).

    Big-endian UTF-16 bytes compare lexicographically in exactly that order, so
    the encoding is the comparison. Encoding also rejects lone surrogates.
    """
    if not isinstance(key, str):
        raise JcsError(f"object keys must be strings, got {type(key).__name__}")
    try:
        return key.encode("utf-16-be")
    except UnicodeEncodeError as exc:
        raise JcsError(f"object key is not valid Unicode: {exc}") from exc


def canonicalize(value) -> str:
    """Return the RFC 8785 canonical serialization of a parsed JSON value.

    Input is the output of json.loads (dict / list / str / int / float / bool /
    None). Returns text; encode as UTF-8 to get canonical bytes.
    """
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return es_string(value)
    if isinstance(value, (int, float)):
        return es_number(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(canonicalize(item) for item in value) + "]"
    if isinstance(value, dict):
        parts = []
        for key in sorted(value.keys(), key=_sort_key):
            parts.append(es_string(key) + ":" + canonicalize(value[key]))
        return "{" + ",".join(parts) + "}"
    raise JcsError(f"cannot canonicalize {type(value).__name__}")
