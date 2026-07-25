# Shadow Mirror — Session 16: Reconciling the Papers to Eleven Invariants

**Author of record:** Omar Moawad · **The American University in Cairo** · **Session date:** 25 July 2026
**Deliverables:** patched P1 and P2, `INSTRUMENT_PERMISSION_EMAILS.md`, defect D-34.

Session 15 added an eleventh invariant. P1 said "ten" in seven places. Fixing that properly turned up a
second problem I was not looking for.

---

## 1. D-34 — the negative-test count was overstated, in our favour

Both papers reported **"16 negative tests"** for Invariants I–X. Counting them exactly:

| | |
|---|---|
| `test_i_catches_an_explanation_with_no_evidence` | negative |
| `test_ii_catches_a_dropped_provenance_parent` | negative |
| `test_iii_catches_a_transition_with_no_triggering_evidence` | negative |
| `test_iv_catches_an_explanation_that_hides_its_uncertainty` | negative |
| `test_v_catches_a_competitor_being_dropped` | negative |
| `test_vi_catches_a_stale_conclusion_left_unannotated` | negative |
| `test_vii_catches_an_explanation_with_no_assumptions_stated` | negative |
| `test_viii_catches_an_inquiry_that_justifies_nothing` | negative |
| `test_ix_catches_a_partial_write` | negative |
| `test_x_catches_verdict_phrasing` | negative |
| `test_x_catches_a_missing_question` | negative |
| `test_x_catches_a_missing_disclaimer` | negative |
| `test_ix_passes_with_rollback` | **positive control** |
| `test_vi_passes_when_revise_context_is_used` | **positive control** |
| `test_x_accepts_an_offer` | **positive control** |
| `test_shipped_reflective_prompts_satisfy_human_authority` | **positive control** |

**Twelve negative tests and four positive controls**, not sixteen negative tests. With Invariant XI's
two, the correct figures are **14 negative and 4 positive controls**.

The error is small and it is the kind that matters here. A paper whose contribution is that
architectural claims should be checkable rather than asserted cannot miscount its own checks. The
correction is stated explicitly in P1 §3.3 rather than made silently:

> *Earlier drafts of this paper reported "sixteen negative tests", which counted the four positive
> controls among them. The correction is small and we make it explicitly rather than silently, because
> a paper about checkable claims should not miscount its own checks.*

This is the second inflated figure the programme has found in its own manuscripts, after D-33's stale
test count. Both were found by re-running rather than re-reading.

---

## 2. Invariant XI got its own randomised harness

Invariants I–X are asserted across 200 randomised graph states. XI ranges over a *formation model*
rather than a graph, so the existing generator could not reach it — which would have left XI as the one
invariant asserted only by hand-built cases, exactly the position the other ten started from before
this programme began.

`_random_model(seed)` builds a model from a random sequence of declarations, person overrides and
**attempted** instrument administrations, under a randomly chosen deployment context, with a consent
grant present 80% of the time. Most administrations therefore refuse.

That is the point. **XI must hold whatever the model has been through, including every path where each
administration was declined.** It is asserted across 200 seeds, with 100 further randomised checks on
two derived properties: that no model ever retains a non-self-completed administration, and that a
person's override always wins for display.

Suite: **673 collected, 671 passing, 2 xfailed.**

---

## 3. What changed in the papers

**P1** — abstract, contributions, the §3.1 invariant table, §3.2 (second harness), §3.3 (the D-34
correction), §3.6 (counts), Appendix B, and a new **§3.7, "An invariant that exists because of a
request"**. That section reports the five-way split of the original request, why stage instruments
cannot be de-ranked, and the design choice that deserves defending: the refusing methods **exist in
order to refuse**, which inverts the usual advice to delete dead code. A caller who finds no
`eventual_purpose` attribute learns nothing; a caller who calls it and reads why it declined learns
what the architecture will not do and on what ground.

55 → 58 references. 5,137 → 6,037 words.

**P2** — a new **§4.4, "A request the architecture declines"**. §6.1 measures a refusal we designed
against a confound we simulated; §4.4 reports a real request, from a real person, declined four-fifths,
on grounds a sceptical reviewer can verify by removing the refusal and watching the check fail.

50 → 56 references. 5,987 → 6,670 words.

Citation integrity machine-checked on both: zero dangling, zero orphaned, zero references without a
resolvable identifier.

---

## 4. The permission letters

Four drafted — Bronk (Claremont Purpose Scale), Ardelt (3D-WS), Darling-Fisher (MEPSI), Schwartz
(PVQ-RR coding instructions). Two placeholders per letter: the corresponding email, and a department if
one applies.

Two of them ask a substantive question alongside the request — whether an Arabic administration is
advisable, and whether MEPSI's reported total-scale alpha of .97 undercuts reading its eight subscales
independently. Instrument authors receive a great many permission requests; the ones worth answering
are the ones that show the instrument has been read.

*Session 17 subsequently made two of these four unnecessary by finding free substitutes.*

---

## 5. State at the end of the session

| | |
|---|---|
| Package | v1.2.0 — 673 collected, 671 passed, 2 xfailed |
| Invariants | 11, all executable |
| Defects | 34 identified; D-34 new this session |
| P1 | 6,037 words, 58 refs |
| P2 | 6,670 words, 56 refs |

Outstanding: the corresponding email; the Phase IV decision; four permission letters to send.
