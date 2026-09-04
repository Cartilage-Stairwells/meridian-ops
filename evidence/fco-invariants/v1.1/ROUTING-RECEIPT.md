# ROUTING RECEIPT — FCO_Invariants v1.1 → meridian-ops

**Routed:** 2026-09-03 (America/Los_Angeles)
**Routed by:** Solene (Base44 Superagent), coordination/verification agent
**PI authorization:** Routing decision executed 2026-09-03 — PI selected
ROUTE → meridian-ops over zksha-rx co-location and over continued
holding. Recorded reasoning: canonicalization v1.1-candidate already
established the evidence/ routing precedent; the artifact's verification
gates are closed and holding serves no remaining purpose; zksha-rx
placement would imply an integration relationship the artifact does not
yet have.

## Artifact identity

| Item | Value |
|---|---|
| Artifact | FCO_Invariants v1.1 (formal custody-plane invariants) |
| Gate 1 — Lean compilation | PASSED — Lean 4.33.1, exit 0, zero errors/warnings, 13 theorems, **0 axioms** (#print axioms clean on all 13) |
| Gate 2 — closure comparison | PASSED — 25/25 kernel-evaluated canReach cells match independent Python BFS closure, zero mismatches |
| Defect corrected by v1.1 | v1.0 hand-authored canReach diverged from true closure in 3 cells; v1.1 derives canReach from `allowed` (frozen invariant: derived relations computed from primitives, never hand-authored in parallel) |
| Epistemic scope | Internal consistency only (two representations, same author). NOT authorship-independent verification. |

## Package contents (SHA256SUMS seal: `af63711f663ad4d637609ba2a6101f9c97d5cecf53bf629ff49f5fff63100300`)

1. `FCO_Invariants-v1.1.lean` — the artifact (13 theorems, 0 axioms)
2. `FCO-INVARIANTS-v1.1-COMPILE-RECORD.md` — compile + closure record
3. `FCO-CLOSURE-CHECK.lean` — closure-comparison harness
4. `closure-check-output.txt` — 25/25 closure output
5. `SHA256SUMS` — content seal (covers files 1–4)

This receipt is committed hash-last: its content is covered by nothing;
it covers the seal above. Seal verified byte-identical on remote after
commit.

## Boundary (per PI decision record)

Placement in meridian-ops is custody placement ONLY. It is NOT evidence
that FCO_Invariants v1.1 has been integrated into zksha-rx — that
composition remains a separate future transition with its own gates.
This receipt confers no authority_status on the artifact: authority
remains 0.
