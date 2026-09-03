#!/usr/bin/env python3
"""
tscp-canonicalizer.py — Reference implementation of TSCP Canonicalization
Manifest v1.1 (proposed). Companion to CANONICALIZATION-MANIFEST-v1.0-AUDIT.md
and CANONICALIZATION-MANIFEST-v1.1-AMENDMENTS.md.

Implements the pipeline given a SEMANTIC PROJECTION (Layer 0 output):
  Step 2  Finset normalization is the caller's concern for semantic collections
          (vector suite supplies pre-normalized or enum-collections; this
          module normalizes enum-valued finsets marked with FINSET sentinel).
  Step 3  NFC on all string values AND property names      (Amendment 5)
  Step 4  UTF-16 code-unit key sorting                      (Amendment 1 / RFC 8785 §3.2.3)
  Step 5  JSON serialization, no whitespace                 (RFC 8785 §3.2.2 escaping)
  Step 6  SHA-256 over canonical bytes                      (hash-last)

Numeric domain (Amendment 2): integers in [-(2^53)+1, 2^53-1] only; anything
larger must be pre-encoded as a string by the projection. Out-of-domain
numbers raise DomainViolation (Rule N-3: reject, never round).

This is a REFERENCE implementation for conformance vector generation, not
production code.
"""
import hashlib
import json
import unicodedata

SAFE_INT_MAX = 2**53 - 1  # 9007199254740991

class DomainViolation(Exception):
    pass

# --- Step 3: NFC on values and keys (Amendment 5) --------------------------

def _nfc_str(s: str) -> str:
    return unicodedata.normalize("NFC", s)

# --- Step 4: UTF-16 code-unit key order (Amendment 1) ---------------------

def _utf16_key(s: str) -> bytes:
    return s.encode("utf-16-be")

# --- Step 5: RFC 8785 §3.2.2-style serialization ---------------------------

_ESCAPES = {
    '"': '\\"', "\\": "\\\\",
    "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t",
}

def _jcs_string(s: str) -> str:
    out = ['"']
    for ch in s:
        if ch in _ESCAPES:
            out.append(_ESCAPES[ch])
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)

def _check_number(n) -> None:
    if isinstance(n, bool):          # bool is handled as literal before this
        return
    if not isinstance(n, int):
        raise DomainViolation(
            f"Non-integer numeric value {n!r} in semantic projection "
            "(Rule N-1: floats are forbidden; encode as string)")
    if n > SAFE_INT_MAX or n < -SAFE_INT_MAX:
        raise DomainViolation(
            f"Integer {n} outside safe range [-(2^53)+1, 2^53-1] "
            "(Rule N-2: encode large quantities as strings)")

def _canonicalize(obj, top: bool = True) -> str:
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if isinstance(obj, str):
        return _jcs_string(_nfc_str(obj))
    if isinstance(obj, (int, float)):
        _check_number(obj)
        return str(obj)                       # safe integers: exact
    if isinstance(obj, list):
        return "[" + ",".join(_canonicalize(x, top=False) for x in obj) + "]"
    if isinstance(obj, dict):
        items = [(_nfc_str(k), v) for k, v in obj.items()]   # keys NFC'd (Am. 5)
        items.sort(key=lambda kv: _utf16_key(kv[0]))          # Am. 1 order
        return "{" + ",".join(
            _jcs_string(k) + ":" + _canonicalize(v, top=False) for k, v in items) + "}"
    raise TypeError(f"Unsupported type in semantic projection: {type(obj)}")

# --- Finset normalization (Step 2) for enum collections --------------------

def normalize_finset(items):
    """Array -> deduplicated sorted array (Step 2). Equality is value equality
    for primitives (Amendment 9); sorted by canonical encoding."""
    seen = []
    for it in items:
        rep = _canonicalize(it)
        if rep not in seen:
            seen.append(rep)
    seen.sort()
    return [json.loads(r) for r in seen]

# --- Public API ------------------------------------------------------------

def canonical_bytes(obj) -> bytes:
    return _canonicalize(obj).encode("utf-8")

def canonical_hash(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()

def version_tag(manifest_version="1.1") -> dict:
    """The manifest-version object carried OUTSIDE canonical bytes (Am. 3)."""
    return {"canonicalization_manifest_version": manifest_version,
            "hash_algorithm": "sha-256"}
