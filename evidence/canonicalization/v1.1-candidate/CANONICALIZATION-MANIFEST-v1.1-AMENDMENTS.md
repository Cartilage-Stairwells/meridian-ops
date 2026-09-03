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
