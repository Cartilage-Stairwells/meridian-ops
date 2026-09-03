# v1.1 Candidate Evidence Package — TSCP Canonicalization Manifest

**Package:** tscp-canonicalization-v1.1-candidate
**Frozen:** 2026-09-03 (America/Los_Angeles)
**Seal:** SHA256SUMS (hash-last; computed after all contents were final)
**Prepared by:** Solene (Base44 Superagent), under PI direction
**PI decision record:** 2026-09-03 — GO / GO / GO, with qualification:
Amendment 6 signature algorithm (ed25519) remains PROVISIONAL / UNSELECTED
until selected against the TSCP threat model.

---

## Epistemic Status (custody rules applied to this package)

| Artifact | Status | What would change it |
|---|---|---|
| v1.0 audit (F-CM-001…010) | OBSERVED — findings empirically reproduced or spec-text cited | re-falsification only |
| v1.1 amendments | **PROPOSED** — committed text is not authoritative; verification/acceptance establishes status | PI acceptance + independent implementation conformance |
| Reference implementation (Python) | EXECUTABLE SPECIFICATION — not the authority | — |
| Conformance vectors | **REFERENCE-GENERATED** — observations of the reference, not yet conformance evidence | an INDEPENDENT implementation reproducing every vector exactly |
| Signature algorithm ed25519 | **PROVISIONAL / UNSELECTED** | explicit threat-model selection decision |

**Provenance chain (preserved):** specification → vector → independent
implementation → verification result.

**Rejected inference (explicitly):** "Python implementation → generated
vectors → therefore correct." The vectors do not certify the reference.

---

## Contents

| File | Role | Target routing (when authorized) |
|---|---|---|
| CANONICALIZATION-MANIFEST-v1.0-AUDIT.md | Audit: 2×P0, 5×P1, 3×P2 findings with reproduction | companion to manifest home repo |
| CANONICALIZATION-MANIFEST-v1.1-AMENDMENTS.md | Proposed drop-in amendment language, F-CM-001…010, Ed25519 provisional | manifest home repo, as proposed v1.1 |
| tscp_canonicalizer.py | Reference implementation / executable specification | meridian-ops |
| generate_and_verify_vectors.py | Suite generator + verifier (determinism, idempotency, domain rejection) | meridian-ops |
| vectors-v1.1.json | 14 vectors (12 positive, 2 domain-rejection), provenance metadata embedded | **meridian-ops / evidence/canonicalization/** |

## Verification state at freeze

- 16/16 checks passed (14 vectors + NFD/NFC pair-equivalence + astral-order assertion)
- Each positive vector checked for: determinism (two calls → identical bytes) and idempotency (parse canonical → re-canonicalize → identical bytes)
- Domain-rejection vectors (CM-V08 raw Goldilocks prime as number; CM-V09 float) raise DomainViolation per Rule N-3 (reject-never-round)

## Outstanding actions (none authorized at freeze)

1. Route amendments to manifest home repository (repo identity to be confirmed — companion docs REVIEWER_DATA_MODEL_v1.0.md / SPECIFICATION_HARDENING_v0.1.md live outside the audited repos).
2. Commit suite to meridian-ops at evidence/canonicalization/ (authorized path confirmed by PI decision record).
3. Independent implementation (Rust firewall / Lean model) runs the 14 vectors — at that point the vectors become cross-implementation conformance evidence and the amendments can advance from PROPOSED toward acceptance.
4. ed25519 selection decision against TSCP threat model.

Per the PI decision record: **no repository commit is authorized by the
decision itself.** This package is the frozen candidate; routing is a
separate authorization.
