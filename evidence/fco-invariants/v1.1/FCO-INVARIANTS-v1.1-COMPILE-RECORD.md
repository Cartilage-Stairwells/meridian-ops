# FCO_Invariants-v1.1.lean — Compilation & Closure Verification Record

**Date:** 2026-09-03 (America/Los_Angeles)
**Performed by:** Solene (Base44 Superagent) — custody/verification agent
**Gates tested:** (1) Lean compilation, (2) independent closure comparison
**Authorization:** PI decision record 2026-09-03 — "Lean compilation of
FCO_Invariants-v1.1.lean; independent closure comparison"
**Routing status:** NONE performed. This record is evidence; routing of
FCO_Invariants-v1.1.lean as a verified formal artifact is a separate PI
decision.

---

## Gate 1 — Lean compilation: PASSED

| Item | Value |
|---|---|
| Artifact | FCO_Invariants-v1.1.lean |
| Artifact SHA-256 | `12000d3d03a9ef5bf9981115753a39a200bb30c512961ec9f8a9fae8c53f359e` |
| Command | `lean FCO_Invariants-v1.1.lean` |
| Exit code | 0 — zero errors, zero warnings |
| Wall time | 0.602s |

### Toolchain

| Item | Value |
|---|---|
| Lean | 4.33.1, commit 819816b2e0a3bf405af45ae5c7af2491d8f5bee6, Release |
| Target | x86_64-unknown-linux-gnu |
| elan | 4.2.4 (227caca13 2026-08-25) |
| Environment | Base44 Superagent sandbox (Linux), fresh install 2026-09-03 |

### Axiom audit — 13/13 theorems, ZERO axioms

`#print axioms` on every theorem in the file reports "does not depend on any
axioms". Every proof is `by decide` — exhaustive kernel computation over the
derived closure. No `sorry`, no custom axioms, nothing beyond the Lean
trusted kernel:

custody_receipt_no_authority_path, custody_no_authority,
evidence_no_authority, receipt_no_authority, custody_plane_separation,
no_plane_crossing, receipt_in_custody_plane, receipt_not_in_authority_plane,
harness_is_evidence_generator, authority_reaches_evidence,
authority_reaches_receipt, execution_reaches_receipt,
authority_reach_into_custody_plane.

## Gate 2 — Independent closure comparison: PASSED (25/25)

**Method.** Harness file `FCO-CLOSURE-CHECK.lean` (artifact content + a
labeled test section; the artifact file itself was not modified) evaluates
`canReach` for all 25 category pairs via `#eval`, kernel-computed. These
Lean-evaluated values were compared cell-by-cell against an independently
written BFS transitive-closure computation of the `allowed` table (Python,
authored before this run and previously used to detect the v1.0 divergence).

| Item | Value |
|---|---|
| Harness | FCO-CLOSURE-CHECK.lean |
| Harness output | closure-check-output.txt (lean stdout/stderr, exit 0) |
| Lean-computed cells | 25/25 evaluated |
| Match with BFS closure | **25/25, zero mismatches** |

### Formerly-divergent cells, now kernel-computed in v1.1

| Cell | v1.0 declared | True closure | Lean v1.1 kernel value |
|---|---|---|---|
| Authority → Evidence | false | true | **true** |
| Authority → AcceptanceReceipt | false | true | **true** |
| Execution → AcceptanceReceipt | false | true | **true** |

### Security summary (from Lean-computed values, not assertions)

Custody-plane → authority-plane cells evaluated true: **0 of 6**.
The fail-closed property is kernel-verified, not table-asserted.

---

## Epistemic scope (explicit)

1. **This closes internal consistency, not authorship independence.** The
   Lean artifact and the Python BFS closure were written by the same agent
   (Solene). The comparison establishes that two independently constructed
   *representations* (Lean kernel decision vs. BFS enumeration) agree on
   all 25 cells — strong internal-consistency evidence. It does not
   substitute for a different-author verification, which the Phase 45
   conformance methodology (independent implementer) addresses elsewhere.
2. **Kernel verification is the strongest form of the claim available
   here:** the theorems are decided against a *derived* closure
   (`reachSet`), per the frozen TSCP formalization invariant (2026-09-03):
   derived relations must be computed from the primitive relation, never
   hand-authored in parallel.
3. **Toolchain provenance:** fresh Lean 4.33.1 install in an isolated
   sandbox; the artifact was compiled exactly as sealed (hash above), with
   no edits between sealing and compilation.

## Gate status

| Gate | Status |
|---|---|
| Lean compilation | ✅ CLOSED (exit 0, 13 theorems, 0 axioms) |
| Independent closure comparison | ✅ CLOSED (25/25 match) |
| Routing as verified formal artifact | ⛔ NOT PERFORMED — awaiting PI decision |
