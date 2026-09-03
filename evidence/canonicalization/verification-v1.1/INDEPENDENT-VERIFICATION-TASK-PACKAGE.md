# Independent Verification Task Package — TSCP Canonicalization v1.1 Candidate

**For execution in:** Aria's environment (the implementing AI, different author
from the reference implementation)
**PI authorization:** 2026-09-03 — "trigger the independent Rust/Lean
conformance run; keep the frozen candidate immutable"
**Prepared by:** Solene (Base44 Superagent) — custody/routing agent only.
Solene authored the Python reference implementation and the vector corpus;
that is exactly why the implementing party for this run must NOT be Solene.
**Status of this package:** trigger artifact — to be committed alongside the
resulting verification artifact so trigger + result share one provenance chain.

---

## 1. Mission

You (Aria) will author an INDEPENDENT implementation of the TSCP
Canonicalization Manifest v1.1 (proposed) pipeline, run it against the frozen
14-vector conformance corpus, and produce a verification artifact recording
every comparison. The expected claim, if all checks pass, is narrow:

> Independent implementation reproduced the specified v1.1 conformance
> behavior for the frozen vector corpus.

Nothing stronger may be inferred. "16/16" is not a claim of protocol
correctness by itself.

## 2. Independence rules (binding)

1. Implement from the SPECIFICATION (v1.0 manifest, which you hold, plus the
   Amendment language inlined in §3 below). Do NOT read, request, or
   port the Python reference implementation (`tscp_canonicalizer.py`) or the
   vector generator (`generate_and_verify_vectors.py`). Reading them
   compromises authorship independence.
2. Implement FIRST, then compare against the corpus. Do not
   reverse-engineer expected outputs into the implementation.
3. Preferred implementation language: **Rust** (matches the TSCP proof stack).
   If your environment cannot compile Rust, implement in whatever toolchain
   you can execute, and record that fact prominently in the artifact —
   language is secondary; authorship independence is the material property.
4. The corpus is IMMUTABLE. If your implementation disagrees with a vector,
   the result is a VERIFICATION FAILURE REQUIRING INVESTIGATION — reported
   honestly, never "fixed" by altering the reference corpus.

## 3. Specification source

Sealed canonical copies (public repo, if you can fetch):
- https://raw.githubusercontent.com/Cartilage-Stairwells/meridian-ops/main/evidence/canonicalization/v1.1-candidate/CANONICALIZATION-MANIFEST-v1.1-AMENDMENTS.md
- https://raw.githubusercontent.com/Cartilage-Stairwells/meridian-ops/main/evidence/canonicalization/v1.1-candidate/vectors-v1.1.json

Amendment language inlined below (authoritative for this run):

# Proposed Amendments — Canonicalization Manifest v1.0 → v1.1

**Status:** PROPOSED v1.1 CANDIDATE — PI decision record 2026-09-03: GO / GO / GO (with
qualification on Amendment 6: ed25519 remains PROVISIONAL / UNSELECTED until selected
against the TSCP threat model). No repository has been modified. Per custody rules:
committing this amendment to a repository does NOT make it authoritative —
verification/acceptance establishes that status.
**Companion audit:** CANONICALIZATION-MANIFEST-v1.0-AUDIT.md (F-CM-001 … F-CM-010)
**Frozen package:** v1.1-candidate/ (MANIFEST.md + SHA256SUMS seal, 2026-09-03)
**Convention:** amendment text below is drop-in language for the manifest sections named. Each item cites its audit finding.

---

## Amendment 1 (resolves F-CM-001, P0) — §2.2 Step 4 and §3 table: key ordering

REPLACE in §2.2 Step 4:

> **Step 4 — Key Sorting**
> JSON object keys are sorted in ascending order by **UTF-16 code unit
> value** (big-endian), per RFC 8785 §3.2.3. This matches ECMAScript, Java,
> and .NET string comparison and is the normative JCS order. NOTE: for
> property names containing characters above U+FFFF, UTF-16 code unit order
> differs from Unicode codepoint order; implementations MUST NOT sort by
> codepoint.

REPLACE §3 table row:

> | Key ordering | UTF-16 code unit order (RFC 8785 §3.2.3) |

*(ASCII-only keys — the expected case for the custody plane — are unaffected.)*

---

## Amendment 2 (resolves F-CM-002, P0) — new §3.1: numeric domain

ADD to §3, as §3.1 "Numeric Domain":

> **Rule N-1 (integer domain).** Numeric values in a semantic projection
> MUST be JSON integers in the I-JSON safe range: −(2^53) ≤ n < 2^53 for
> negative values and 0 ≤ n < 2^53 for non-negative values, with the further
> constraint |n| ≤ 2^53 − 1 (the largest safe integer, 9007199254740991).
> Floating-point numbers MUST NOT appear in semantic projections.
>
> **Rule N-2 (out-of-domain encoding).** Any numeric quantity outside the
> safe-integer domain — including 64-bit and 128-bit integers, field
> elements, and large counters — MUST be encoded as a JSON string in
> lowercase hexadecimal (0x-prefixed) or plain decimal, as declared in the
> Layer 0 projection.
>
> **Rule N-3 (conformance behavior).** A conformance checker MUST reject
> (not silently round) any semantic projection containing a numeric value
> outside the safe-integer domain.

*(Determinism rationale: ECMAScript/Pikka-style number serialization of
out-of-range integers is lossy and implementation-divergent — audited as
F-CM-002. Restricting to safe integers removes the entire float-serialization
surface from the custody plane.)*

---

## Amendment 3 (resolves F-CM-003, P1) — §6 exclusion table additions

ADD rows to §6:

> | Field | Reason | Excluded From |
> |---|---|---|
> | `id` | Identity is the hash of content; including it is circular | All hashes |
> | `canonical_hash` | Self-referential if included in its own input | All hashes |
> | `canonicalization_manifest_version` | Conformance-routing metadata; a version bump must not change identity of unchanged content | All hashes |

ADD note to §10:

> The `canonicalization_manifest_version` field is carried **outside** the
> canonical bytes. Conformance checkers read it from the containing object,
> not from the hashed content.

---

## Amendment 4 (resolves F-CM-004, P1) — §9: id construction under non-default algorithms

ADD to §9, after the Key Invariant:

> **Id Algorithm Rule.** The `id` field of an object is always
> SHA-256(canonical_bytes), regardless of the object's declared
> `hash_algorithm`. The declared algorithm governs `canonical_hash` only.
> This keeps object identity stable across algorithm migrations (a
> sha-512-conforming object remains findable by its v1.0-era id).

---

## Amendment 5 (resolves F-CM-005, P1) — §4: NFC scope and corrected rationale

REPLACE §4 Scope:

> **Scope:** NFC normalization is applied to **all string values AND all
> property names** in the semantic projection. It is not applied to binary
> fields (hashes, signatures) or numeric fields.

REPLACE §4 Rationale:

> **Rationale:** NFC produces composed forms of accented and combining
> character sequences, ensuring canonically equivalent strings produce
> identical bytes. NFC does NOT claim to unify all visually similar strings
> (e.g., the ligature U+FB01 vs "fi", or fullwidth U+FF41 vs "a" remain
> distinct under NFC). Visual similarity is not semantic equality.

---

## Amendment 6 (resolves F-CM-006, P1) — new §7.1: signature algorithm registry

ADD to §7, as §7.1 "Signature Algorithms":

> Receipts carry an explicit `signature_algorithm` field. Registry:
>
> | Algorithm | Status | Signature Encoding | Domain Separation Prefix |
> |---|---|---|---|
> | ed25519 | **PROVISIONAL / UNSELECTED** | 64-byte signature, base64url (if selected) | "TSCP-RECEIPT-V1" |
> | (future) | Reserved | — | — |
>
> The signature input is the domain-separation prefix concatenated with the
> 32-byte digest. Signature material authenticates a canonical artifact; it
> is not part of the artifact identity (§9). New algorithms are added to
> this registry; existing entries are never removed.

**Selection rule (PI decision record, 2026-09-03):** the algorithm
IDENTIFIER is the normative registry value; the ed25519 entry is explicitly
PROVISIONAL / UNSELECTED. Selection is a deliberate threat-model decision,
pending confirmation that the TSCP threat model requires no different
signature ecosystem (e.g., FIPS/PKI interop) or hardware-backed primitive.
A convenient implementation choice MUST NOT silently freeze into a
protocol invariant.

---

## Amendment 7 (resolves F-CM-007, P1) — new §8.1: misuse boundaries

ADD to §8, as §8.1 "Misuse Boundaries":

> The canonical hash establishes **semantic identity** — that two
> projections describe the same semantic content. It does NOT establish:
> - byte identity of any received artifact (normalization may alter bytes),
> - transmission integrity (use transport-layer integrity for that),
> - provenance of the original encoding, or
> - that an artifact A equals the output of a computation C (the §4.5 gap;
>   binding is the custody pipeline's job, not the hash's).
>
> Implementations MUST NOT present canonical-hash equality as
> tamper-evidence for a byte sequence.

---

## Amendment 8 (resolves F-CM-008, P2) — §5: total orders for ordered arrays

REPLACE §5 general rule:

> Arrays of semantic collections (failure_set, transition_history) are
> normalized to sorted arrays. Arrays with inherent ordering preserve their
> order, with a **total-order tiebreak**: entries with equal sort keys are
> sub-ordered by the SHA-256 of their own canonical bytes (hex, ascending).
> No two distinct entries of an ordered array may share a canonical hash.

---

## Amendment 9 (resolves F-CM-009, P2) — §2.2 Step 2: finset element equality

ADD to §2.2 Step 2:

> Finset membership uses the canonical-bytes equality relation: two
> elements are equal iff their canonical encodings (steps 3–5) are byte-
> identical. For primitive elements this coincides with value equality.

---

## Amendment 10 (resolves F-CM-010, P2) — new §12: conformance vectors

ADD as §12:

> The normative conformance vector suite lives at
> `evidence/canonicalization/vectors-v1.1.json` in the meridian-ops
> repository. Every implementation MUST reproduce every
> `expected_canonical_bytes` and `expected_hash` exactly. The suite covers:
> finset normalization, NFC (values and keys), UTF-16 key ordering
> (including the astral case), numeric-domain acceptance and rejection,
> id/version/hash exclusion, signature exclusion, and re-canonicalization
> idempotency.

---

## Version bump

On acceptance of Amendments 1–10, the manifest version increments to 1.1;
§10's versioning rules apply; v1.0 is marked superseded in the version
register with pointers to the audit and amendment documents.


---

## 4. Conformance corpus (immutable, frozen 2026-09-03)

**Sealed corpus identity:** vectors-v1.1.json, SHA-256
`873f69165aa9b3f1a04d31b6cb00bb6ff014539ee437505f2b22377e94e10005`
(at meridian-ops evidence/canonicalization/v1.1-candidate/)

**Delivery encoding:** the copy inlined below is an ASCII-escaped transport
encoding (all non-ASCII as \uXXXX), SHA-256
`9d3d65114020fb0658a5de09813b9a5de2d28908e4ba7393fc0db29a53145b37`.
It is parse-equivalent to the sealed corpus (verified programmatically at
packaging time). It exists ONLY because chat transport can mangle raw
Unicode. Your JSON parser decodes it to identical data. It is not a
modification of the sealed artifact.

Inlined transport copy follows:

```
{
  "package": "tscp-canonicalization-conformance-suite",
  "manifest_version": "1.1 (proposed candidate)",
  "provenance": {
    "status": "REFERENCE-GENERATED",
    "chain": "specification -> vector -> independent implementation -> verification result",
    "anti_chain": "python implementation -> generated vectors -> 'therefore correct' (NOT a valid inference; these vectors do not certify the reference)",
    "generated_by": "tscp_canonicalizer.py (reference implementation, executable specification)",
    "generated_at": "2026-09-03",
    "verification": "PENDING \u2014 these vectors become cross-implementation conformance evidence only when an independent implementation (e.g., Rust firewall) reproduces every expected_canonical_bytes and expected_hash exactly",
    "authority_note": "the specification is the authority; this implementation is an executable specification; these vectors are its observations"
  },
  "vectors": [
    {
      "id": "CM-V01",
      "finding": "F-CM-009",
      "description": "Finset dedup + sort (manifest \u00a72.2 example)",
      "type": "positive",
      "input": [
        "PlaneViolation",
        "TypeMismatch",
        "PlaneViolation"
      ],
      "expected_canonical_bytes_hex": "5b22506c616e6556696f6c6174696f6e222c22547970654d69736d61746368222c22506c616e6556696f6c6174696f6e225d",
      "expected_hash": "e61cfa015a9045dcf5303a9dc8004663ae0ddc78a5176e12c04609269d658817",
      "expected_canonical_json": "[\"PlaneViolation\",\"TypeMismatch\",\"PlaneViolation\"]"
    },
    {
      "id": "CM-V02",
      "finding": "F-CM-005",
      "description": "NFC value: combining accent precomposed",
      "type": "positive",
      "input": {
        "payload": "cafe\u0301"
      },
      "expected_canonical_bytes_hex": "7b227061796c6f6164223a22636166c3a9227d",
      "expected_hash": "3e29815840a779187f1b7a2a814257810e9d931d90bdc211dca2fcad7fe6b1cc",
      "expected_canonical_json": "{\"payload\":\"caf\u00e9\"}"
    },
    {
      "id": "CM-V03",
      "finding": "F-CM-001",
      "description": "Astral key sorts BEFORE U+FFFF under UTF-16 code units",
      "type": "positive",
      "input": {
        "\ud83d\ude00": 1,
        "\uffff": 2
      },
      "expected_canonical_bytes_hex": "7b22f09f9880223a312c22efbfbf223a327d",
      "expected_hash": "c6b1b96b618d8be475f379fe69c6646b44d7a5d3c01630c43509562f09d1024b",
      "expected_canonical_json": "{\"\ud83d\ude00\":1,\"\uffff\":2}"
    },
    {
      "id": "CM-V04",
      "finding": "F-CM-005",
      "description": "NFD key and NFC key produce IDENTICAL canonical bytes",
      "type": "positive",
      "input": {
        "cafe\u0301": 1
      },
      "expected_canonical_bytes_hex": "7b22636166c3a9223a317d",
      "expected_hash": "4ba6f859a6604763e30e1afc74dd00bf3b245be58d902b5d1ae0eaa119e8a141",
      "expected_canonical_json": "{\"caf\u00e9\":1}"
    },
    {
      "id": "CM-V05",
      "finding": "F-CM-005",
      "description": "NFC precomposed key (pair of CM-V04)",
      "type": "positive",
      "input": {
        "caf\u00e9": 1
      },
      "expected_canonical_bytes_hex": "7b22636166c3a9223a317d",
      "expected_hash": "4ba6f859a6604763e30e1afc74dd00bf3b245be58d902b5d1ae0eaa119e8a141",
      "expected_canonical_json": "{\"caf\u00e9\":1}"
    },
    {
      "id": "CM-V06",
      "finding": "F-CM-002",
      "description": "Safe integers (I-JSON range) serialize exactly",
      "type": "positive",
      "input": {
        "counter": 9007199254740991,
        "neg": -9007199254740991
      },
      "expected_canonical_bytes_hex": "7b22636f756e746572223a393030373139393235343734303939312c226e6567223a2d393030373139393235343734303939317d",
      "expected_hash": "8cb8c78141f1c58d9c5a7d2b9990c214b13ff7c755d059cfc331d964afeb3454",
      "expected_canonical_json": "{\"counter\":9007199254740991,\"neg\":-9007199254740991}"
    },
    {
      "id": "CM-V07",
      "finding": "F-CM-002",
      "description": "Goldilocks prime as string (Rule N-2)",
      "type": "positive",
      "input": {
        "field_element": "0xffffffff00000001"
      },
      "expected_canonical_bytes_hex": "7b226669656c645f656c656d656e74223a22307866666666666666663030303030303031227d",
      "expected_hash": "e9dbf95d2a02ed0a75ea75910fbe26c5c1d90b3fdb42537d8c1cf4c25e9e18c2",
      "expected_canonical_json": "{\"field_element\":\"0xffffffff00000001\"}"
    },
    {
      "id": "CM-V08",
      "finding": "F-CM-002",
      "description": "Raw Goldilocks prime as JSON number raises DomainViolation",
      "type": "domain-rejection",
      "input_repr": "{'field_element': 18446744069414584321}",
      "expected": "DomainViolation"
    },
    {
      "id": "CM-V09",
      "finding": "F-CM-002",
      "description": "Float value raises DomainViolation",
      "type": "domain-rejection",
      "input_repr": "{'ratio': 0.5}",
      "expected": "DomainViolation"
    },
    {
      "id": "CM-V10",
      "finding": "F-CM-003",
      "description": "Objects differing only in id/canonical_hash/manifest_version hash identically once excluded (projection strips them)",
      "type": "positive",
      "input": {
        "claim": "Fibonacci terminal 294373",
        "batch": 1
      },
      "expected_canonical_bytes_hex": "7b226261746368223a312c22636c61696d223a224669626f6e61636369207465726d696e616c20323934333733227d",
      "expected_hash": "f1110086590ba87bab878d64e8eb477e1649eba134e9eb40d7a2b37d74cf3e83",
      "expected_canonical_json": "{\"batch\":1,\"claim\":\"Fibonacci terminal 294373\"}"
    },
    {
      "id": "CM-V11",
      "finding": "F-CM-003/F-CM-004",
      "description": "Receipt content excluding signature \u2014 identity is content",
      "type": "positive",
      "input": {
        "claim": "TSCP-ANCHOR-01",
        "timestamp": 1785700000,
        "subject": "artifact-A"
      },
      "expected_canonical_bytes_hex": "7b22636c61696d223a22545343502d414e43484f522d3031222c227375626a656374223a2261727469666163742d41222c2274696d657374616d70223a313738353730303030307d",
      "expected_hash": "87e18795334643d3f88346d8b5fbcea6cc8625ffb69412729c1a3a8b1fdb22ee",
      "expected_canonical_json": "{\"claim\":\"TSCP-ANCHOR-01\",\"subject\":\"artifact-A\",\"timestamp\":1785700000}"
    },
    {
      "id": "CM-V12",
      "finding": "\u2014",
      "description": "Nested object, recursive UTF-16 key sort",
      "type": "positive",
      "input": {
        "zebra": {
          "\ud83d\ude00": 1,
          "\uffff": 0
        },
        "apple": [
          1,
          2,
          3
        ],
        "mango": true
      },
      "expected_canonical_bytes_hex": "7b226170706c65223a5b312c322c335d2c226d616e676f223a747275652c227a65627261223a7b22f09f9880223a312c22efbfbf223a307d7d",
      "expected_hash": "682712c2fe7f45573e263f200f55a379444a91ce016bcd35f60abcc1a768dace",
      "expected_canonical_json": "{\"apple\":[1,2,3],\"mango\":true,\"zebra\":{\"\ud83d\ude00\":1,\"\uffff\":0}}"
    },
    {
      "id": "CM-V13",
      "finding": "\u2014",
      "description": "Empty object, empty array, null, booleans",
      "type": "positive",
      "input": {
        "a": {},
        "b": [],
        "c": null,
        "d": false,
        "e": true
      },
      "expected_canonical_bytes_hex": "7b2261223a7b7d2c2262223a5b5d2c2263223a6e756c6c2c2264223a66616c73652c2265223a747275657d",
      "expected_hash": "ec007d71478451c90c7e32a427b65e92eb6f0f9ee3deae8ffe4767889643b6ca",
      "expected_canonical_json": "{\"a\":{},\"b\":[],\"c\":null,\"d\":false,\"e\":true}"
    },
    {
      "id": "CM-V14",
      "finding": "\u2014",
      "description": "Control chars escaped, lowercase hex",
      "type": "positive",
      "input": {
        "cmd": "line1\nline2\tend\u0007"
      },
      "expected_canonical_bytes_hex": "7b22636d64223a226c696e65315c6e6c696e65325c74656e645c7530303037227d",
      "expected_hash": "0a448de8c155201629c20fd5efd2ebbd4e5ac7845745fce2544b9b47ff2dc229",
      "expected_canonical_json": "{\"cmd\":\"line1\\nline2\\tend\\u0007\"}"
    }
  ]
}
```

---

## 5. Checks to run (per vector, unless noted)

For every `type: positive` vector (CM-V01..CM-V07, CM-V10..CM-V14):
- **Canonical-byte comparison:** your canonical bytes (hex) ==
  `expected_canonical_bytes_hex` (exact)
- **Digest comparison:** SHA-256 of your canonical bytes ==
  `expected_hash` (exact)
- **Determinism:** canonicalize the input twice; identical bytes both times
- **Idempotency:** parse your canonical JSON output, re-canonicalize;
  identical bytes

For every `type: domain-rejection` vector:
- **CM-V08** (Goldilocks prime `2^64 - 2^32 + 1` as a JSON number): your
  implementation MUST refuse it (error/rejection), per Rule N-3
  reject-never-round. Silently serializing or rounding = FAILURE.
- **CM-V09** (float 0.5): same — floats are forbidden in semantic
  projections (Rule N-1).

Pairwise assertions (run once over the corpus):
- **CM-V04 ≡ CM-V05:** NFD-key input and NFC-key input must produce
  IDENTICAL canonical bytes and hashes (Amendment 5: NFC applies to keys).
- **CM-V03 order:** the astral key U+1F600 must sort BEFORE U+FFFF in the
  canonical output (Amendment 1: UTF-16 code-unit order, not codepoint).

## 6. Verification artifact template

Produce `VERIFICATION-v1.1.md` in Aria's environment containing, at minimum:

1. **Implementation identity** — language, name, version/commit or
   equivalent locator of the code YOU wrote
2. **Environment/toolchain** — OS, compiler/runtime versions, date of run
3. **Vector-suite identity** — "vectors-v1.1.json, sealed SHA-256
   873f6916...45b37 path" (record both hashes above and which you consumed)
4. **Per-vector results, all 14** — id, each check, PASS/FAIL, observed
   values on failure
5. **Canonical-byte comparison results** (summary)
6. **Digest comparison results** (summary)
7. **Domain-rejection results** — explicitly including the Goldilocks
   CM-V08 case and float CM-V09 case, with the exact rejection behavior
8. **Determinism/idempotency results** where applicable
9. **Total pass/fail count** (14 vectors + 2 pairwise assertions = 16 checks)
10. **Timestamp** (with timezone)
11. **Verifier identity/provenance** — "Aria (independent implementer)",
    chain: specification → vector → independent implementation →
    verification result
12. **Claim** — the narrow claim language from §1, nothing stronger

Then compute **SHA-256 of your completed VERIFICATION-v1.1.md** and report
that seal value in the handoff message (the artifact cannot contain its own
hash; hash-last).

## 7. Custody rules

- Do not modify vectors-v1.1.json, the transport copy, or any file in the
  frozen candidate. No accommodation of the corpus to the implementation.
- Do not modify the amendments language.
- On disagreement: report the failure, preserve your implementation as-is,
  and return the artifact with the failure documented. Investigation is a
  subsequent PI-directed event.
- The verification artifact is a NEW artifact. It will be routed (by
  Solene, on PI authorization) to
  `evidence/canonicalization/verification-v1.1/` alongside this task
  package. It will NOT be folded into the frozen candidate.

## 8. Return path

Hand the completed artifact + its SHA-256 seal back through the PI. Solene
recomputes the seal on receipt, verifies content, and requests routing
authorization.
