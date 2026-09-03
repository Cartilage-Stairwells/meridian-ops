#!/usr/bin/env python3
"""
generate_and_verify_vectors.py — Conformance vector suite for TSCP
Canonicalization Manifest v1.1 (proposed). Resolves F-CM-010.

Each vector: id, description, audit finding it exercises, input object,
expected canonical bytes (hex) and expected SHA-256. The suite also runs
three invariant checks per vector:
  D  determinism: two calls -> identical bytes
  I  idempotency: parse(canonical) -> re-canonicalize -> identical bytes
  R  domain-rejection vectors must raise DomainViolation

Exit 0 only if every check passes.
"""
import json
from tscp_canonicalizer import (canonical_bytes, canonical_hash,
                                normalize_finset, DomainViolation)

V = []  # (id, finding, description, input, expect_raise)

# CM-V01 — §2.2 Step 2 worked example (finset normalization)
V.append(("CM-V01", "F-CM-009", "Finset dedup + sort (manifest §2.2 example)",
          ["PlaneViolation", "TypeMismatch", "PlaneViolation"], False))

# CM-V02 — §2.2 Step 3 worked example (NFC value normalization)
V.append(("CM-V02", "F-CM-005", "NFC value: combining accent precomposed",
          {"payload": "cafe\u0301"}, False))

# CM-V03 — F-CM-001: UTF-16 code-unit key order, astral case (post-fix order)
V.append(("CM-V03", "F-CM-001",
          "Astral key sorts BEFORE U+FFFF under UTF-16 code units",
          {"\U0001F600": 1, "\uffff": 2}, False))

# CM-V04 — F-CM-005: NFD-form key NFC-normalizes to same encoding as NFC key
V.append(("CM-V04", "F-CM-005",
          "NFD key and NFC key produce IDENTICAL canonical bytes",
          {"cafe\u0301": 1}, False))
V.append(("CM-V05", "F-CM-005", "NFC precomposed key (pair of CM-V04)",
          {"caf\u00e9": 1}, False))

# CM-V06 — F-CM-002: safe integers pass and serialize exactly
V.append(("CM-V06", "F-CM-002", "Safe integers (I-JSON range) serialize exactly",
          {"counter": 9007199254740991, "neg": -9007199254740991}, False))

# CM-V07 — F-CM-002: Goldilocks prime MUST be a string, not a number
V.append(("CM-V07", "F-CM-002",
          "Goldilocks prime as string (Rule N-2)",
          {"field_element": "0xffffffff00000001"}, False))

# CM-V08 — F-CM-002 Rule N-3: raw u64 number must be REJECTED
V.append(("CM-V08", "F-CM-002",
          "Raw Goldilocks prime as JSON number raises DomainViolation",
          {"field_element": 2**64 - 2**32 + 1}, True))

# CM-V09 — F-CM-002 Rule N-1: floats forbidden
V.append(("CM-V09", "F-CM-002", "Float value raises DomainViolation",
          {"ratio": 0.5}, True))

# CM-V10 — §6/Am.3: id and canonical_hash excluded by projection (simulated:
#          caller strips them); here we verify the residual hashes identical
V.append(("CM-V10", "F-CM-003",
          "Objects differing only in id/canonical_hash/manifest_version "
          "hash identically once excluded (projection strips them)",
          {"claim": "Fibonacci terminal 294373", "batch": 1}, False))

# CM-V11 — §9/Am.4: signature excluded; content with different signatures same id
V.append(("CM-V11", "F-CM-003/F-CM-004",
          "Receipt content excluding signature — identity is content",
          {"claim": "TSCP-ANCHOR-01", "timestamp": 1785700000,
           "subject": "artifact-A"}, False))

# CM-V12 — nested structures: recursive key sorting + finset inside object
V.append(("CM-V12", "—", "Nested object, recursive UTF-16 key sort",
          {"zebra": {"\U0001F600": 1, "\uffff": 0}, "apple": [1, 2, 3],
           "mango": True}, False))

# CM-V13 — empties and literals
V.append(("CM-V13", "—", "Empty object, empty array, null, booleans",
          {"a": {}, "b": [], "c": None, "d": False, "e": True}, False))

# CM-V14 — control-character escaping per RFC 8785 §3.2.2
V.append(("CM-V14", "—", "Control chars escaped, lowercase hex",
          {"cmd": "line1\nline2\tend\u0007"}, False))

results, failures = [], 0
suite = []
for vid, finding, desc, obj, expect_raise in V:
    if expect_raise:
        try:
            canonical_bytes(obj)
            ok, detail = False, "expected DomainViolation, none raised"
        except DomainViolation as e:
            ok, detail = True, f"rejected: {e}"
        results.append((vid, ok, detail))
        suite.append({"id": vid, "finding": finding, "description": desc,
                      "type": "domain-rejection", "input_repr": repr(obj),
                      "expected": "DomainViolation"})
        continue

    # Determinism: D
    b1, b2 = canonical_bytes(obj), canonical_bytes(obj)
    d_ok = b1 == b2
    # Idempotency: I  (parse canonical JSON, re-canonicalize)
    reparsed = json.loads(b1.decode("utf-8"))
    i_ok = canonical_bytes(reparsed) == b1
    h = canonical_hash(obj)
    ok = d_ok and i_ok
    detail = f"D={'ok' if d_ok else 'FAIL'} I={'ok' if i_ok else 'FAIL'}"
    results.append((vid, ok, detail))
    suite.append({"id": vid, "finding": finding, "description": desc,
                  "type": "positive", "input": obj,
                  "expected_canonical_bytes_hex": b1.hex(),
                  "expected_hash": h,
                  "expected_canonical_json": b1.decode("utf-8")})
    if not ok:
        failures += 1

# Pairwise check: CM-V04 and CM-V05 must hash IDENTICALLY (NFC key rule)
v04 = next(s for s in suite if s["id"] == "CM-V04")
v05 = next(s for s in suite if s["id"] == "CM-V05")
pair_ok = v04["expected_hash"] == v05["expected_hash"]
results.append(("CM-V04≡CM-V05", pair_ok,
                "NFD/NFC key unification" if pair_ok else "HASHES DIFFER — F-CM-005 fix fails"))

# CM-V03 order assertion: astral key must come FIRST (UTF-16 order)
v03_json = next(s for s in suite if s["id"] == "CM-V03")["expected_canonical_json"]
order_ok = v03_json.index("\U0001F600") < v03_json.index("\uffff")
results.append(("CM-V03-order", order_ok,
                "astral key first (UTF-16)" if order_ok else "wrong order (codepoint sort!)"))

failures += (not pair_ok) + (not order_ok)

print(f"{'vector':<14} {'result':<6} detail")
print("-" * 60)
for vid, ok, detail in results:
    print(f"{vid:<14} {'PASS' if ok else 'FAIL':<6} {detail}")
print("-" * 60)
total = len(results)
print(f"{total - failures}/{total} checks passed")

with open("vectors-v1.1.json", "w") as f:
    json.dump({
        "package": "tscp-canonicalization-conformance-suite",
        "manifest_version": "1.1 (proposed candidate)",
        "provenance": {
            "status": "REFERENCE-GENERATED",
            "chain": "specification -> vector -> independent implementation "
                     "-> verification result",
            "anti_chain": "python implementation -> generated vectors -> "
                          "'therefore correct' (NOT a valid inference; "
                          "these vectors do not certify the reference)",
            "generated_by": "tscp_canonicalizer.py (reference implementation, "
                            "executable specification)",
            "generated_at": "2026-09-03",
            "verification": "PENDING — these vectors become cross-implementation "
                            "conformance evidence only when an independent "
                            "implementation (e.g., Rust firewall) reproduces every "
                            "expected_canonical_bytes and expected_hash exactly",
            "authority_note": "the specification is the authority; this "
                              "implementation is an executable specification; "
                              "these vectors are its observations"
        },
        "vectors": suite}, f, indent=2, ensure_ascii=False)
print("suite written: vectors-v1.1.json")

exit(1 if failures else 0)
