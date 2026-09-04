/-
  FCO_Invariants.lean — v1.1 (modeling correction)
  TSCP Custody Plane — Formal Conformance Invariants

  Key theorem: custody_receipt_no_authority_path

    canReach Custody AcceptanceReceipt = true
    canReach Custody Authority = false

  Producing a receipt from a custody object does not create a path to
  authority. The receipt is in the custody plane, not the authority plane.

  Classification: Evidence Generator formal invariant, NOT Authority Generator.
  The theorems prove what is NOT possible, not what IS permitted.

  ────────────────────────────────────────────────────────────────────
  v1.1 MODELING CORRECTION (audit 2026-09-03, verified empirically)
  ────────────────────────────────────────────────────────────────────

  v1.0 DEFECT: `canReach` was an independently hard-coded 5×5 relation,
  not a function of `allowed`. Its `by decide` proofs therefore
  established facts about a *declared* table, not about the transition
  algebra — exactly the model/specification divergence a formal
  conformance layer must eliminate.

  The divergence was NOT hypothetical. Cell-by-cell comparison of the
  v1.0 declared table against the true transitive closure of `allowed`
  found 3 divergent cells, each with a witnessing path:

    Authority → Evidence          (via Execution→Evidence)
    Authority → AcceptanceReceipt (via Execution→Evidence→AcceptanceReceipt)
    Execution → AcceptanceReceipt (via Evidence→AcceptanceReceipt)

  The v1.0 comment "the transitive closure of allowed ... is computed by
  exhaustive enumeration" was therefore false as implemented.

  SECURITY IMPACT (verified): all nine v1.0 theorems remain TRUE under
  the true closure. No custody-plane category (Custody, Evidence,
  AcceptanceReceipt) can reach any authority-plane category (Authority,
  Execution). The fail-closed property holds — the defect weakened what
  the proofs established, not the truth of the security claims.

  v1.1 FIX: `canReach` is DERIVED from `allowed` by bounded fixpoint
  iteration (`reachSet`). No independently asserted reachability table
  exists in this file. `by decide` now exhaustively decides properties
  of the derived closure itself. The three formerly-divergent cells are
  recorded as derived theorems (below) so the model cannot silently
  lose them.

  New derived observation: reachability is ASYMMETRIC across planes —
  authority-plane categories can reach custody-plane evidence
  (authority may consume evidence), but no custody-plane category can
  reach any authority-plane category (evidence never confers
  authority). That one-directional flow is now a formal fact of the
  model, not an accident of a table.

  ────────────────────────────────────────────────────────────────────
  EPISTEMIC BOUNDARY
  ────────────────────────────────────────────────────────────────────

  This Lean file ESTABLISHES the closure and its properties by decide.
  The Python test suite (test_closure.py) INDEPENDENTLY cross-checks
  implementations against this formal model; it does not participate in
  establishing the theorems. Cross-agreement between the two is a
  separate observation, recorded where it occurs.

  ────────────────────────────────────────────────────────────────────
  PROOF METHOD

  reachSet k a b = b reachable from a within k steps:
    reachSet 0 a b = (a = b)
    reachSet (k+1) a b = reachSet k a b ∨ ∃c, reachSet k a c ∧ allowed c b

  With 5 categories, any reachable pair admits a simple path of length
  ≤ 4, so reachSet 4 decides exact reachability. If a category is ever
  added, this bound must be revisited.

  NOTE (compile status): authored and semantically cross-validated
  against an independent BFS closure computation (25/25 cells), but not
  yet compiled — no Lean toolchain was available at authoring time.
  Compilation in a Lean 4 environment is the pending conformance step;
  a compile failure is a finding, not a reason to alter this artifact.

  Algebra version binding: FCO_TRANSITION_ALGEBRA.md
    Hash: 53fb4b5a093f7539587be2fc7703f482ac0f5c23c9bbdc89f9ef7614b7df7cda
    The `allowed` table is UNCHANGED from the bound version; v1.1
    corrects only how reachability is derived from it.
-/

namespace TSCP.CustodyPlane

/-- Category in the custody plane topology -/
inductive Category
  | Custody
  | Evidence
  | AcceptanceReceipt
  | Authority
  | Execution
  deriving DecidableEq, Repr

/-- Is this category in the custody plane? -/
def isCustodyPlane : Category → Bool
  | Category.Custody => true
  | Category.Evidence => true
  | Category.AcceptanceReceipt => true
  | Category.Authority => false
  | Category.Execution => false

/-- Is this category in the authority plane? -/
def isAuthorityPlane : Category → Bool
  | Category.Custody => false
  | Category.Evidence => false
  | Category.AcceptanceReceipt => false
  | Category.Authority => true
  | Category.Execution => true

/-- Allowed transitions between categories (total function, 5×5).
    UNCHANGED from v1.0 — bound to the algebra at the pinned hash. -/
def allowed : Category → Category → Bool
  | Category.Custody,           Category.Custody           => true
  | Category.Custody,           Category.Evidence          => true
  | Category.Custody,           Category.AcceptanceReceipt => true
  | Category.Custody,           Category.Authority         => false
  | Category.Custody,           Category.Execution         => false
  | Category.Evidence,          Category.Evidence          => true
  | Category.Evidence,          Category.AcceptanceReceipt => true
  | Category.Evidence,          Category.Authority         => false
  | Category.Evidence,          Category.Execution         => false
  | Category.Evidence,          Category.Custody           => false
  | Category.AcceptanceReceipt, Category.AcceptanceReceipt => true
  | Category.AcceptanceReceipt, Category.Evidence          => true
  | Category.AcceptanceReceipt, Category.Custody           => false
  | Category.AcceptanceReceipt, Category.Authority         => false
  | Category.AcceptanceReceipt, Category.Execution         => false
  | Category.Authority,         Category.Authority         => true
  | Category.Authority,         Category.Execution         => true
  | Category.Authority,         Category.Custody           => false
  | Category.Authority,         Category.Evidence          => false
  | Category.Authority,         Category.AcceptanceReceipt => false
  | Category.Execution,         Category.Execution         => true
  | Category.Execution,         Category.Evidence          => true
  | Category.Execution,         Category.Custody           => false
  | Category.Execution,         Category.Authority         => false
  | Category.Execution,         Category.AcceptanceReceipt => false

/-- Decidable existential over the five categories. -/
def anyCategory (p : Category → Bool) : Bool :=
  p Category.Custody || p Category.Evidence || p Category.AcceptanceReceipt ||
  p Category.Authority || p Category.Execution

/-- Reachability fixpoint: `reachSet k a b` = b reachable from a in ≤ k steps.
    DERIVED from `allowed`; no reachability is ever asserted independently. -/
def reachSet : Nat → Category → Category → Bool
  | 0, a, b => decide (a = b)
  | (k+1), a, b =>
      reachSet k a b || anyCategory (fun c => reachSet k a c && allowed c b)

/-- Reflexive-transitive closure of `allowed` — DERIVED, never asserted.
    5 categories ⇒ simple paths have length ≤ 4 ⇒ reachSet 4 is exact. -/
def canReach (a b : Category) : Bool := reachSet 4 a b

/-- Key theorem: producing a receipt from custody does not create a path
    to authority. Decided against the DERIVED closure of `allowed`. -/
theorem custody_receipt_no_authority_path :
    canReach Category.Custody Category.AcceptanceReceipt = true ∧
    canReach Category.Custody Category.Authority = false := by
  decide

/-- Strengthened: no custody-plane category can reach Authority. -/
theorem custody_no_authority :
    canReach Category.Custody Category.Authority = false := by
  decide

theorem evidence_no_authority :
    canReach Category.Evidence Category.Authority = false := by
  decide

theorem receipt_no_authority :
    canReach Category.AcceptanceReceipt Category.Authority = false := by
  decide

/-- No custody-plane category can reach any authority-plane category. -/
theorem custody_plane_separation :
    canReach Category.Custody Category.Authority = false ∧
    canReach Category.Custody Category.Execution = false ∧
    canReach Category.Evidence Category.Authority = false ∧
    canReach Category.Evidence Category.Execution = false ∧
    canReach Category.AcceptanceReceipt Category.Authority = false ∧
    canReach Category.AcceptanceReceipt Category.Execution = false := by
  decide

/-- No allowed transition crosses from custody plane to authority plane. -/
theorem no_plane_crossing :
    allowed Category.Custody Category.Authority = false ∧
    allowed Category.Custody Category.Execution = false ∧
    allowed Category.Evidence Category.Authority = false ∧
    allowed Category.Evidence Category.Execution = false ∧
    allowed Category.AcceptanceReceipt Category.Authority = false ∧
    allowed Category.AcceptanceReceipt Category.Execution = false := by
  decide

/-- The acceptance receipt stays in the custody plane. -/
theorem receipt_in_custody_plane :
    isCustodyPlane Category.AcceptanceReceipt = true := by
  decide

/-- The acceptance receipt is NOT in the authority plane. -/
theorem receipt_not_in_authority_plane :
    isAuthorityPlane Category.AcceptanceReceipt = false := by
  decide

/-- The harness produces evidence, not authority:
    the receipt is in the custody plane and NOT in the authority plane. -/
theorem harness_is_evidence_generator :
    isCustodyPlane Category.AcceptanceReceipt = true ∧
    isAuthorityPlane Category.AcceptanceReceipt = false := by
  decide

/- ────────────────────────────────────────────────────────────────
   DERIVED OBSERVATIONS — the v1.0 divergent cells, now formal facts.

   These were DECLARED false in the v1.0 hard-coded table. The true
   closure of `allowed` makes them true, with witnessing paths. They
   are recorded here so the model cannot silently lose them, and so
   the authority plane's actual outbound reach is explicit.
   ──────────────────────────────────────────────────────────────── -/

/-- Authority reaches Evidence through Execution (path length 2).
    v1.0 table declared false; the closure of `allowed` says true. -/
theorem authority_reaches_evidence :
    canReach Category.Authority Category.Evidence = true := by
  decide

/-- Authority reaches AcceptanceReceipt through Execution → Evidence.
    v1.0 table declared false; the closure of `allowed` says true. -/
theorem authority_reaches_receipt :
    canReach Category.Authority Category.AcceptanceReceipt = true := by
  decide

/-- Execution reaches AcceptanceReceipt through Evidence.
    v1.0 table declared false; the closure of `allowed` says true. -/
theorem execution_reaches_receipt :
    canReach Category.Execution Category.AcceptanceReceipt = true := by
  decide

/-- The plane flow is one-directional: authority-plane categories can
    reach custody-plane evidence (authority may consume evidence), but
    — by custody_plane_separation — no custody-plane category can reach
    any authority-plane category (evidence never confers authority). -/
theorem authority_reach_into_custody_plane :
    canReach Category.Authority Category.Evidence = true ∧
    canReach Category.Authority Category.AcceptanceReceipt = true ∧
    canReach Category.Execution Category.Evidence = true ∧
    canReach Category.Execution Category.AcceptanceReceipt = true ∧
    canReach Category.Custody Category.Authority = false ∧
    canReach Category.Custody Category.Execution = false ∧
    canReach Category.Evidence Category.Authority = false ∧
    canReach Category.Evidence Category.Execution = false ∧
    canReach Category.AcceptanceReceipt Category.Authority = false ∧
    canReach Category.AcceptanceReceipt Category.Execution = false := by
  decide

end TSCP.CustodyPlane
