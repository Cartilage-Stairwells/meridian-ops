# Phase B — Historical Source Verification Specification

**Document ID:** SPEC-PHASE-B-HSV-v1
**Status:** DRAFT — pending review
**Date:** 2026-09-02
**Supersedes:** none
**Depends on:** Phase A fixture architecture (ACCEPTED, verification PENDING)

---

## 0. Phase A Recorded Status

The following status is recorded and must not be upgraded without the
evidence specified in §7.

| Property | Status |
|----------|--------|
| Architecture | ACCEPTED |
| Specification | ACCEPTED |
| Claimed implementation | PLAUSIBLE |
| Independent execution evidence | NOT YET ESTABLISHED |
| Phase A final verification | PENDING |

Rationale: the reported design is correct, but provenance discipline requires
distinguishing "the implementation claims these tests passed" from "we have
independently verified the implementation and its execution." The five
adversarial cases are the right tests. A report that they passed — including a
report from an AI system — is an assertion, not a verification event.

This is not skepticism about the architecture. It is the architecture applied
to itself.

---

## 1. Purpose and Scope

This specification defines the protocol for Phase B: establishing, from primary
sources, the historical evidence object **EVI-TIME-1925**.

Phase B is **source-first, not hypothesis-first**. The protocol exists to
answer: *what does the historical record actually contain?* — before any
question of *what we would like it to contain.* No proposition about the
article's content, significance, or relationship to any modern construct may
enter the record before the source itself is established.

Phase B does not adjudicate TPI (see §6).

---

## 2. Normative Terminology Corrections

The following corrections are binding on all Phase A/B documents, fixtures,
and reports. A system whose purpose is preventing epistemic overclaiming must
not overclaim in its own definitions.

### 2.1 Digest language

| Incorrect | Correct |
|-----------|---------|
| "SHA-256 — The **unique** cryptographic digest of those canonical bytes." | "SHA-256 — The **deterministic digest** of those canonical bytes." |

A cryptographic hash is not mathematically unique; collisions are theoretically
possible. The operationally relevant property is **collision resistance**, not
uniqueness. All documentation, fixtures, and harness output must use
"deterministic digest" language, and may note collision resistance as the
security property relied upon.

### 2.2 Anchor language

| Incorrect | Correct |
|-----------|---------|
| "External Anchor — **Tamper-evident proof**..." | "External Anchor — **Evidence that a particular commitment existed at an externally verifiable point in time**..." |

The anchor's evidentiary content depends on the anchoring mechanism. What an
external anchor establishes is *existence at a time*, per the mechanism's own
security model. It does not, by itself, prove integrity of the committed
content, correctness of the commitment construction, or anything about the
object prior to the anchor event. Phrasing must follow the mechanism.

---

## 3. Evidence Object Lifecycle

EVI-TIME-1925 is a stateful evidence object. State transitions are one-way
and gated by this specification.

```
UNRESOLVED ──(B1 artifact identified)──> IDENTIFIED
IDENTIFIED ──(B2 actual text obtained)──> SOURCED
SOURCED   ──(B3 verbatim excerpt preserved with provenance metadata)──> PRESERVED
PRESERVED ──(B4 independent corroboration)──> CORROBORATED
CORROBORATED ──(B5 canonicalization + hash)──> HASHED
```

**Current state: `UNRESOLVED`.**

Rules:

- No state may be skipped or merged.
- The EVIDENCE hash (§5) is computed only at the CORROBORATED → HASHED
  transition, never before.
- A state regression (e.g., corroboration fails) returns the object to
  `UNRESOLVED` for the failed dimension; it does not silently downgrade.
- An AI-generated description of an article is not a source. It cannot advance
  the object past `UNRESOLVED`.

---

## 4. Phase B Protocol

### B1 — Identify the artifact

Establish, from the archive itself (not from memory, not from an AI summary):

- exact TIME article title
- publication date
- author/byline (including "no byline" if that is the fact)
- archive identifier (any stable ID the archive exposes)
- canonical/stable URL
- page/issue information if available
- **whether the archive reproduces the original article text or merely
  metadata about it** — this determination must be recorded explicitly, because
  it controls whether B2 is even possible against this archive

Output: an IDENTIFICATION record for EVI-TIME-1925, moving the object to
`IDENTIFIED` only if the archive actually contains the article (full text or
scan). If the archive holds only metadata, the object remains `UNRESOLVED` and
the protocol halts at B1 until a full-text source is located.

### B2 — Obtain the actual text

Do not manufacture an excerpt from a description. Do not reconstruct the text
from a summary of its supposed contents.

The evidence object remains `status: UNRESOLVED` until actual historical text
is obtained from a sufficiently reliable source.

"Sufficiently reliable" requires at minimum: the source identifies itself as
a reproduction of the original publication (scan, licensed archive text, or
transcription with stated provenance), and the source exposes enough metadata
to bind the text to the artifact identified in B1.

Output: the obtained text, stored exactly as received, with source URL and
access date. Object moves to `SOURCED`.

### B3 — Preserve the source exactly

Capture the smallest useful verbatim excerpt, together with its provenance
metadata.

Prohibitions (absolute):

- No modernization of spelling, punctuation, or typography.
- No paraphrase substituted for quotation.
- No AI reconstruction treated as transcription.
- No silent correction of apparent errors in the original.

The excerpt boundaries (beginning and end position in the source text) must be
recorded so the excerpt is re-derivable from the source.

Output: PRESERVED record: verbatim excerpt + excerpt boundaries + provenance
metadata. Object moves to `PRESERVED`.

### B4 — Independent corroboration

Where possible, compare the TIME archive against an independent archival or
catalog source. Corroboration answers six questions, in order, and each answer
is recorded separately:

1. **Does the article exist?**
2. **Is the metadata correct?** (title, date, byline, issue/page against the
   independent source)
3. **Is this actually the original text?** (does the archive reproduce the
   original, or a later revision / abridgment?)
4. **Is the excerpt accurately transcribed?** (character-for-character against
   the obtained text)
5. **What proposition does the excerpt support?** (stated as a bounded claim
   the words actually assert)
6. **What does it NOT establish?** (mandatory section — no PRESERVED →
   CORROBORATED transition without an explicit negative-scope statement)

These questions are separate. Passing one does not pass the next. An object may
be CORROBORATED for questions 1–4 while the answers to 5–6 remain recorded and
bounded.

Output: CORROBORATION record answering all six questions. Object moves to
`CORROBORATED`.

### B5 — Only then hash it

Once source identity and text are established, in this order:

```
verbatim evidence
      ↓
canonical evidence object   (canonical serialization, per Phase A spec)
      ↓
EVIDENCE hash               (deterministic digest — §2.1 language)
      ↓
edge commitment
      ↓
graph root
```

**The hash records the evidence state. It must never be used to establish the
evidence's historical authenticity retroactively.** Hashing is the last step,
not the first. A hash of an uncorroborated object is a hash of an uncorroborated
object — it proves nothing about 1925.

Output: HASHED record. The EVIDENCE hash is now eligible for edge commitment.

### B6 — TPI remains completely separate

The two unresolved boundaries are independent problems:

- **EVI-TIME-1925** → historical/source verification problem (this spec)
- **TPI** → semantic/scoring-definition recovery problem (a separate work
  stream, separately specified)

Invariants:

- Finding the article does not resolve TPI.
- Resolving TPI does not authenticate the article.
- No Phase B output may be cited as TPI evidence, and no TPI reconstruction may
  be cited as Phase B source material.
- A single document may not carry both the EVI-TIME-1925 and TPI states; their
  state machines are disjoint.

---

## 5. Recording Rules

- Every state transition is an append-only record: timestamp, actor, input
  artifact (with its own digest), and resulting state.
- "Actor" may be a human or an AI system, but AI-sourced content must be
  labeled `authority: 0` unless it is itself a direct mechanical verification
  (e.g., a hash computation). Per TSCP: coherence is not evidence; a generated
  explanation is not recovered provenance.
- If a step was performed by an AI and not independently checked, the record
  says so. The record never says "verified" when it means "reported."

---

## 6. Out of Scope

- TPI recovery or definition (separate work stream)
- Any modernization, interpretation, or analysis of the article's content
  beyond the bounded proposition recorded in B4-Q5
- Fixtures for historical claims — Phase B produces evidence records, not
  test fixtures. The next artifact after this spec is research output under
  B1, not another fixture.

---

## 7. Phase A Verification Requirements (informational)

Recorded here so the Phase A status table in §0 cannot drift. Phase A moves
from PENDING to VERIFIED only when all eight are present:

1. `validate_fixtures.py`
2. `adversarial_harness.py`
3. both `*-v2.json` skeleton fixtures
4. the exact commit/tag containing them
5. raw test output
6. SHA-256 manifest of those files
7. clean-environment rerun
8. independently reproduced results

As of 2026-09-02, items 1–8 do not exist in any repository under
Cartilage-Stairwells or Triune-Oracle (verified by search). The Phase A
artifacts currently exist only in the reporting AI's environment. First
concrete step toward Phase A verification: commit items 1–3 at a tagged
commit so items 4–6 become possible.

---

## 8. Acceptance Criteria for This Specification

This spec is accepted when:

- [ ] The Phase A status table (§0) is agreed as the recorded status.
- [ ] Terminology corrections (§2) are applied to the Phase A report and any
      affected fixture definitions.
- [ ] The lifecycle states (§3) are agreed as the only legal states for
      EVI-TIME-1925.
- [ ] B6 separation is agreed as binding on all future documents touching
      either EVI-TIME-1925 or TPI.

Acceptance of this specification does not verify Phase A. It defines Phase B.
