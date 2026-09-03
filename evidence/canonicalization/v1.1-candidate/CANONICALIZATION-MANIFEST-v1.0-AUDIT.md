# ARCHER Audit — Canonicalization Manifest v1.0 (TSCP Custody Plane)

**Auditor:** Solene (Base44 Superagent), under PI direction
**Date:** 2026-09-03
**Method:** GENERATE test cases → EXECUTE → OBSERVE → COMPARE → REPORT. All
P0/P1 findings below include empirically observed evidence (reproducible
commands in Appendix A) or exact spec-text citations. Speculation is labeled.

**Target:** CANONICALIZATION_MANIFEST v1.0 (dated 2026-08-03, status Active)
**Scope:** internal consistency, conformance with referenced standards
(RFC 8785, Unicode NFC), cross-implementation determinism under the
manifest's own §11 conformance criterion.

**Verdict:** The manifest's skeleton is sound — signature-exclusion invariant,
algorithm registry, versioned manifest, exclusion table, and hash-last
discipline are correct and consistent with TSCP's epistemic framework.
However, **two P0 defects cause the manifest's own §11 conformance test
("two independent implementations produce identical canonical bytes") to
FAIL** for legal inputs, and one P0-level internal contradiction exists
between the manifest and the RFC it normatively references. Findings below.

---

## P0 Findings

### F-CM-001 — Key ordering contradicts the referenced RFC (§3 vs RFC 8785 §3.2.3)

**Claim under test:** §3 states key ordering is "Lexicographic (UTF-8
codepoint order)"; §2.2 Step 4 repeats "RFC 8785 lexicographic key ordering."

**Observed:** RFC 8785 §3.2.3 sorts property names by **UTF-16 code unit
values** (ECMAScript string comparison), NOT UTF-8 codepoint order. These
orders diverge for any property names mixing high-BMP characters
(U+E000–U+FFFF) with astral characters (U+10000+).

Reproduced (Appendix A, Observation 1): keys `U+FFFF` and `U+1F600`:
- UTF-8 codepoint order (manifest §3): `U+FFFF` first
- UTF-16 code-unit order (RFC 8785, actual): `U+1F600` first (surrogate pair 0xD83D… sorts below 0xFFFF)

**Consequence:** An implementation following the manifest's letter and an
implementation following the RFC it cites produce **different canonical
bytes** for the same input → different hashes → §11 cross-implementation
conformance fails.

**Required action (one of):**
1. Amend §3/§2.2 Step 4 to "UTF-16 code unit order per RFC 8785 §3.2.3"
   (zero impact on ASCII keys — recommended), or
2. Formally de-profile from RFC 8785 and declare TSCP's own ordering
   (accepting divergence from all JCS ecosystem tooling).

**Severity: P0.** The manifest claims to be the single normative reference;
its normative text contradicts its normative reference.

---

### F-CM-002 — Numeric domain unspecified; values beyond 2^53 break canonicalization (§3, §5, §8)

**Claim under test:** §3 "Number format: shortest representation"; §2.2
Step 5 "Numbers in shortest representation."

**Observed:** RFC 8785 (building on I-JSON) serializes numbers as IEEE 754
doubles (ECMAScript `Number::toString`). Integers above 2^53 are not
representable; canonicalization of such values is either lossy or
implementation-divergent:

- Goldilocks prime `2^64 − 2^32 + 1 = 18446744069414584321` → as double:
  `1.8446744069414584e+19`; round-trip exact: **False** (Appendix A, Obs. 2)
- `2^64 − 1` → as double `1.8446744073709552e+19`; round-trip exact: **False**
- Python `json.dumps` (not JCS-conformant) emits the full integer
  `18446744069414584321`; a JCS-conformant serializer emits
  `1.8446744069414584e+19` → **identical semantic input, different canonical
  bytes across implementations** → §11 fails.

**Unmodeled relationship surfaced:** the manifest governs the custody plane
(State, Receipt, EvalResult objects), and TSCP's proof stack operates over
64-bit fields (Goldilocks) and u64 counters. If any such value enters a
semantic projection as a JSON number, canonicalization corrupts or
destabilizes it.

**Required action:** Add a normative numeric-domain rule to §3/§8:
1. Semantic numeric values MUST be I-JSON compliant (safely representable as
   IEEE 754 doubles; integers ≤ 2^53), and
2. Field elements and any u64/u128 value MUST be encoded as strings (hex or
   decimal), with the encoding declared in Layer 0.

**Severity: P0.** Silent corruption class; fails §11 cross-language.

---

## P1 Findings

### F-CM-003 — Circularity: `id`, `canonical_hash`, `manifest_version` absent from the §6 exclusion table

§6 excludes signature, metadata, transport_headers, audit_timestamp,
optional_annotations. It is **silent** on `id`, `canonical_hash`, and
`canonicalization_manifest_version` (§10 example shows this field inside
objects). If any of these enter the semantic projection:
- `id`/`canonical_hash` make the hash self-referential (undefined),
- `manifest_version` changes the identity when the version bumps even if
  the rules produce identical bytes (a transition anomaly: v1.0- and
  v1.1-conforming objects would carry different hashes for identical
  content).

**Required action:** Add all three to §6 with exclusion scope, and state
whether manifest version is carried outside the hashed content (it must be,
for conformance checkers to route — recommend: outside).

### F-CM-004 — §7/§9 inconsistency: id construction under non-default hash algorithms

§7 makes `hash_algorithm` an explicit per-object field with a migration
registry (sha-256 active; sha-384/512, blake3 reserved). §9 states "The id
field of a receipt is the SHA-256 of the receipt content" — fixed SHA-256.
For an object declaring `hash_algorithm: sha-512`, id construction is
undefined (SHA-256 per §9, or declared algorithm per §7's migration intent?).

**Required action:** One sentence resolving id construction (recommend: id
is always SHA-256 for cross-referencing; the declared algorithm governs
content-hash fields only — or id follows the declared algorithm; either is
coherent, but it must be stated).

### F-CM-005 — NFC scope ambiguity (keys vs values) and rationale overclaim (§4)

§4 scope: "Applied to all string values in the semantic projection." Keys
are not explicitly named. Observed: key `"cafe\u0301"` (NFD) and key
`"café"` (NFC) normalize to the same string — if keys are NFC-normalized
these objects hash equal; if keys escape the rule, they are semantically
equal but hash different (Appendix A, Obs. 4).

Separately, the rationale "ensures that visually identical strings with
different Unicode representations produce the same canonical bytes"
**overclaims**: NFC does not unify all visually identical strings. Observed:
`U+FB01` (fi ligature) NFC→ stays a ligature (≠ "fi"); `U+FF41` (fullwidth a)
NFC→ stays fullwidth (≠ "a") (Appendix A, Obs. 3). This is exactly the
prose-overclaim class the Stage 3/4 review standards flag in the manuscript;
in a normative document it is worse, because a conformance-checker author
may implement to the rationale rather than the rule.

**Required action:** §4 scope: "Applied to all string values AND property
names in the semantic projection." Rationale: weaken to "NFC ensures
canonical composition of accented forms; it does not claim to unify all
visually similar strings (see U+FB01, U+FF41)."

### F-CM-006 — No signature algorithm registry (§2.2 Step 7, §9)

Hashes have an explicit algorithm field, registry, and migration rules
(§7). The signature step — "sign the digest with the cryptographic key" —
specifies no algorithm (Ed25519? ECDSA? RSA-PSS?), no encoding, no domain
separation, and no migration path. The manifest is the "single normative
reference for all implementations"; verification interop across the Rust
firewall, external verifiers, and cross-language ports depends on this.

**Required action:** Add a signature algorithm registry parallel to §7
(algorithm, status, encoding, domain-separation string), and an explicit
`signature_algorithm` field on receipts.

### F-CM-007 — Semantic hash ≠ byte hash: the boundary is not stated

By design (and correctly), the canonical hash is computed over a
**normalized projection** — NFC strings, deduplicated/sorted collections.
Therefore two byte-different artifacts can carry the same canonical hash
(state equivalence). The manifest never states the inverse boundary:
**canonical_hash must not be used as transport tamper-evidence or as proof
that a received byte sequence is unmodified.** Given the paper v2.1 §4.5
seam history (artifact-to-proof binding), this misuse seam should be an
explicit normative prohibition, not an implicit property.

**Required action:** Add a "Misuse boundaries" subsection: canonical hash
establishes semantic identity; it does not establish byte identity,
transmission integrity, or provenance of the original encoding.

---

## P2 Findings

### F-CM-008 — Tie-breaking unspecified for ordered arrays (§5)

`audit_trail` is ordered "chronological"; two events with identical
timestamps have no defined order → nondeterministic canonical bytes.
`relationships` sorted "by type, then target" has no tiebreak if two entries
share both. **Action:** define total orders (e.g., timestamp, then
content-hash tiebreak).

### F-CM-009 — Finset element equality undefined for non-primitive elements (§2.2 Step 2)

Dedup requires an equality relation. Defined for string enums (FailureKind);
undefined for object-valued collections. **Action:** state equality-by-
canonical-bytes for object elements, or restrict Finsets to primitives.

### F-CM-010 — No conformance test vectors (§11)

§11's strongest test is cross-implementation byte equality, but the manifest
ships no vectors, and the TSCP profile (NFC + finset + semantic projection)
differs from pure JCS — so RFC 8785's official vectors do not cover the
deltas. **Action:** ship a vector suite in-repo covering: the §2.2 worked
examples, the F-CM-001 astral-key case, the F-CM-002 large-integer policy
(pre/post fix), NFC key/value cases, tie cases, and signature-exclusion
round-trips.

---

## What Survived Falsification (positive results)

- **§9 signature-exclusion invariant** — internally consistent and correct:
  identity = content, signature = authentication. Attempted falsification
  found no contradiction.
- **Hash algorithm as explicit field** (Amendment 5) with never-remove
  registry — sound migration hygiene.
- **`timestamp` (creation) vs `audit_timestamp` (audit) distinction** —
  correct and well-motivated.
- **Finset normalization** — the right solution to collection-order
  nondeterminism; needs only the equality-relation patch (F-CM-009).
- **Hash-last discipline** (canonical bytes → digest → sign) — consistent
  with TSCP's core principle that a declared hash is an assertion, not a
  verification.

---

## Appendix A — Reproduction (observed 2026-09-03, Python 3)

```python
import unicodedata, json

# Obs 1 — key ordering divergence
k1, k2 = '\uffff', '\U0001F600'
sorted([k1,k2], key=lambda s: s.encode('utf-8'))     # [U+FFFF, U+1F600]  (manifest §3)
sorted([k1,k2], key=lambda s: s.encode('utf-16-be')) # [U+1F600, U+FFFF]  (RFC 8785 §3.2.3)

# Obs 2 — numeric domain
g = 2**64 - 2**32 + 1          # 18446744069414584321
float(g)                        # 1.8446744069414584e+19
int(float(g)) == g              # False
json.dumps({'x': g})            # {"x": 18446744069414584321}  (Python, NOT JCS)

# Obs 3 — NFC does not unify all visually identical strings
unicodedata.normalize('NFC', '\ufb01') == 'fi'   # False
unicodedata.normalize('NFC', '\uff41') == 'a'    # False

# Obs 4 — NFC of keys
unicodedata.normalize('NFC', 'cafe\u0301') == 'café'  # True (so key NFC is well-defined; scope just needs to say "keys")
```

RFC 8785 §3.2.3 citation verified against the RFC Editor text and multiple
independent JCS implementations (Erlang rfc8785 package docs; IETF
draft-rundgren §3.2.3 rationale: "basing the sort algorithm on UTF-16 code
units ... maps directly to the string type in ECMAScript, Java and .NET").

---

## Recommended Disposition

- **Fix before any implementation references v1.0:** F-CM-001, F-CM-002.
- **Fix in v1.1 alongside:** F-CM-003 … F-CM-007.
- **Housekeeping:** F-CM-008 … F-CM-010.
- After fixes: bump to v1.1, ship the F-CM-010 vector suite, and mark v1.0
  superseded in the version register.

*Observation/speculation separation: every P0/P1 finding above carries
either executed-and-observed output or direct spec-text citation. No finding
rests on inference alone.*
