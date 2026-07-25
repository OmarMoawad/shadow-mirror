# Shadow Mirror — Session 12: Camera-Ready Assets and the Defect Sweep

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverables:** six publication figures (PDF + PNG), `shadow_mirror` **v1.1.0** (**324 passing**,
2 xfailed), this report.

---

## 0. Summary

Four defects closed, six figures produced, one regression found and guarded against during the fix.

| Defect | Before | After |
|---|---|---|
| **D-32** No mechanism behind the AI Act Art. 5(1)(f) prohibition | policy only | **`DeploymentContext` refuses the biometric stream** in institutional and undeclared contexts; 6 tests |
| **D-31** Consent could not be demonstrated at a past date (GDPR Art. 7(1)) | mutable grant | **hash-chained append-only ledger**, tamper-evident, plus a withdrawal receipt (Art. 7(3)); 6 tests |
| **D-28** Observation intake quadratic | 3.8× per doubling, 1121 ms at 800 pairs | **2.0× per doubling, 5.2 ms** — 214× faster |
| **D-26** Offset estimator stuck at severe displacement | 61.3% at δ=0.45 | **97.0%** — and a new guard where the estimator was actively harmful |
| **D-17** Literal `\n` in figure labels | present | gone; all six figures regenerated from source |

**Enforcement ratio: 5 of 12 prohibitions machine-enforced → 6 of 12.** The one that moved is the
only one currently unlawful to breach in the EU.

---

## 1. D-32 — the prohibition now has a mechanism

Session 9 found that emotion inference in a workplace or education institution is prohibited under
Art. 5(1)(f), applicable since 2 February 2025, and that Shadow Mirror had **no code path** that
could refuse it.

`deployment.py` supplies one. A `DeploymentContext` declares where the instance is running —
`self`, `consented_individual`, `institutional`, or `undeclared` — and gates the streams that supply
the biometric basis for affective inference.

Three design decisions are load-bearing:

**Refusal is the default.** `undeclared` is treated as institutional. An operator who has not said
where the system is running has not established that the prohibition does not apply, and the safe
reading of silence is the restrictive one.

**The safety exception requires a written basis, not a flag.** `safety_exception_basis` is free text
and must be non-empty to have any effect. A boolean can be set by accident or by a config default; a
sentence has to be written by someone. The stated basis is recorded and exported with the consent
ledger, so the claim is auditable rather than implicit.

**The refusal explains itself.** The exception message carries the article numbers, the applicability
date, the declared context, and the exact call that would claim the exception — because a refusal a
developer cannot act on becomes a refusal a developer removes.

```
DeploymentRefusal: Stream 'physiological' supplies the biometric basis for
inferring an affective state, which makes this an emotion recognition system
under EU AI Act Art. 3(39). Art. 5(1)(f) prohibits emotion inference in workplace
and education institutions (applicable since 2 February 2025)...
```

A Python module does not make anyone compliant, and the module says so in its own output
(*"not legal advice and does not establish compliance"*). What it does is convert a prohibition from
a wish into a mechanism, which is the difference the Session 9 enforcement ratio was measuring.

---

## 2. D-31 — consent that can be demonstrated

GDPR Art. 7(1) requires a controller to *demonstrate* that consent was given. A mutable grant object
cannot: a stream added and later removed leaves no trace, and a grant revoked and re-issued looks
identical to one that never lapsed.

`ledger.py` records every consent event — granted, stream added, re-affirmed, lapsed, revoked,
erased, context declared, refused — as an immutable, hash-chained entry. Three properties follow:

- **`streams_granted_at(subject, when)`** answers the Art. 7(1) question directly: *which streams
  were under active grant at this instant?*
- **`verify()`** re-derives the chain. Editing any historical entry breaks it. This is tamper
  *evidence*, not tamper proofing — the subject owns their own file and that is the point — but a
  controller claiming consent on a date can show a chain that verifies, and an edited one will not.
- **Erasure retains the record, not the data.** The ledger records *that* 42 observations were
  erased. That record is the evidence the withdrawal was honoured.

**The withdrawal receipt** closes the Art. 7(3) parity gap. Granting is a guided flow ending in a
summary; revocation was a single call ending in silence. Those are not equally easy experiences
however few keystrokes each takes. `withdrawal_receipt()` returns what was granted, when it was
withdrawn, how many records were erased, and whether the chain still verifies — something the subject
keeps.

---

## 3. D-28 — the write path is linear

Session 7 measured `add()` at 3.8× per doubling: every observation recomputed every belief.

Beliefs are now computed when the mirror is **consulted**, not when an observation is written.

| Evidence pairs | Before | After |
|---|---|---|
| 100 | 27 ms | 0.74 ms |
| 400 | 296 ms | 2.75 ms |
| 800 | 1121 ms | **5.24 ms** |
| Scaling per doubling | 3.8× | **2.0×** |

A **214× improvement at 800 pairs**, and linear.

Two honest notes. First, a semantic change: the reactivity counter now counts consultations rather
than writes — which is arguably what a reactivity measure should have counted from the start, since
it exists to warn that *looking at a guess changes later answers*. `n_reflections()` is kept as an
explicit counter so the caution behaves identically. Second, the asymptotics of a **read-heavy**
pattern are unchanged: one consultation per twenty writes still scales at 3.1× per doubling, because
each consultation is O(n). The constant improved twentyfold; the shape did not. Making reads
incremental as well requires anchored decay accumulators, and is not attempted here.

One existing test was updated: `test_d11_history_is_keyed_by_topic` now consults each topic before
inspecting the history. The property under test — history keyed by topic rather than pooled — is
unchanged, and the docstring records why the test moved.

---

## 4. D-26 — soft assignment, and a regression caught in the act

Session 5's hard-assignment EM converged to a poor local optimum at severe displacement, because its
first assignment was mostly wrong. Soft assignment with likelihood-selected restarts fixes it:

| δ | Topics | Uncorrected | Session 5 (hard EM) | **v1.1 (soft EM)** |
|---|---|---|---|---|
| 0.30 | 5 | 82.3% | 90.8% | **93.4%** |
| 0.30 | 8 | 83.8% | 95.8% | **98.2%** |
| 0.45 | 3 | 54.1% | 55.8% | **76.2%** |
| 0.45 | 5 | 53.6% | 58.4% | **89.5%** |
| 0.45 | 8 | 53.2% | 61.3% | **97.0%** |

At severe displacement with eight topics, **53.2% → 97.0%**.

**But the first version of this fix made things much worse where the data is thin.** At one topic
and δ = 0.30, correcting with the unguarded soft estimate drove accuracy from 81.2% to **20.8%**.
Soft EM is happy to produce a confident estimate from one point, and the estimate is wrong.

The cause is identifiability, not tuning: a single (x, y) point can be moved onto any of four corners
by some offset, so there are more unknowns than equations. The estimator now **refuses below three
topics** and returns a zero offset. That is a condition, not a threshold — and the curve is worth
looking at, because it is the clearest picture in the project of what "observing more" actually buys.

I am flagging this because it nearly shipped. A fix that improves the headline number by 36 points
while quietly destroying the thin-data case is exactly the kind of change that passes a benchmark and
fails a person.

---

## 5. Figures

Six figures, PDF (Type-42 embedded fonts, submission-ready) and PNG (review), all generated from
`results.json` and the experiment outputs by `make_paper_figures.py`. Nothing is typed in.

**P2 — ethics-of-design paper**

1. `fig_p2_1_harm_rate` — the false hidden-desire rate across three conditions and three methods.
   The Shadow Mirror bar is invisible because it is zero; the label carries it.
2. `fig_p2_2_ablation` — imputing a missing channel as zero versus recording it as absent.
3. `fig_p2_3_ambivalence` — dispersion-gated versus structure-gated, before and after.

**P1 — architecture paper**

4. `fig_p1_1_inquiry_regret` — regret against the oracle, three planners, two conditions.
5. `fig_p1_2_credible_sets` — set coverage versus point accuracy, with mean set size annotated and
   the nominal 90% line drawn so the shortfall is visible rather than described.
6. `fig_p1_3_identifiability` — accuracy against topics pooled, with the identifiability boundary
   marked.

**D-17 is closed.** The original figure's node labels contained the literal characters `\n`. Labels
are now constructed with real newlines, and the escape sequence appears nowhere in any output.

---

## 6. Test suite

| | Session 11 | Session 12 |
|---|---|---|
| Passing | 312 | **324** |
| Strict xfails (declared gaps) | 2 | 2 |

Twelve new tests: six for the deployment gate, six for the consent ledger. Every one is written
against the defect rather than the implementation.

---

## 7. Remaining open items

| Item | Status |
|---|---|
| Related-work expansion — 12–14 verified refs against 30–45 expected | Session 13 |
| Read-path complexity still O(n) per consultation | Open; anchored-decay accumulators would fix it |
| D-23 residual — nominal coverage needs conformal calibration | Blocked on labelled outcomes (human study) |
| D-30 — positive autocorrelation ("your position moved steadily") computed and discarded | Proposal |
| Causal reflection, knowledge consolidation | Declared gaps, strict xfail |
| Affiliation, corresponding email, repository URL | **Blocked on you (Q2)** |

---

*Session 13 — adversarial self-review of both papers as a hostile Reviewer 2 — continues
automatically. Session 14 stops for your decision.*
