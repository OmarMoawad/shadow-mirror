# Shadow Mirror

**A reference architecture for reflective human–AI interaction, and the research programme around it.**

**Author of record:** Omar Moawad
**Affiliation:** The American University in Cairo, AUC Avenue, P.O. Box 74, New Cairo 11835, Egypt
**Programme:** 18 sessions, complete · **Package:** `shadow_mirror` v1.3.0

---

## Start here

If you have five minutes, open `tracker/shadow_mirror_program_tracker.html` in a browser. It is the
whole programme on one page.

If you have an hour, read `papers/UNIFIED_DRAFT.md`, then `papers/APPENDIX_OUTSTANDING_WORK.md` —
which lists everything the draft cannot yet support — then `sessions/SESSION_13_ADVERSARIAL_REVIEW.md`,
which attacks the papers.

If you want to run something:

```bash
pytest -q                        # 707 passed, 2 xfailed
python verify_claims.py          # re-derives the claims used in the unified draft
python demo.py
python make_urg_visualization.py # regenerates urg_visualization.png from a real graph
```

No dependencies to install. The package has **zero runtime dependencies** by design — that is an
auditability commitment, not an aesthetic one, and it is why NetworkX was removed in Session 4.

---

## What this is

A consent-based, probabilistic **reflection** engine, in two modes: **self-mirror**, where you hold
the mirror about yourself, and **consented study**, where you study another person only with their
informed, granular, revocable consent (see [`ETHICS.md`](ETHICS.md)).

It does **not** classify who a person "really is". It estimates dated, uncertain hypotheses about the
tension between what someone *says*, what they can *do*, and what they *do* — and turns those tensions
into questions to sit with, never verdicts.

The central design claim is that when what a person says and what they do disagree, the honest output
is frequently a **refusal** rather than a better-hedged guess — because approach under stated
reluctance is produced by hidden preference, and it is *also* produced by compliance under perceived
pressure, and the two are not distinguishable from the surface signal.

**Measured result:** 0 of 800 simulated threat episodes misread (95% upper bound 0.37% by the rule of
three) against 42.9% for a mismatch-only reader and 75.1% for an arousal-as-desire reader.

**Measured cost:** a supervised four-channel classifier, given ground-truth labels, beats us at low
channel separation — 5.0% against our 29.7%. That is in the papers because a reviewer would find it
otherwise. The defence is that those labels do not exist in deployment, which makes it an upper bound
on what any supervised method could reach rather than an available alternative.

---

## Layout

| Path | What it is |
|---|---|
| `shadow_mirror/` | The package. Zero runtime dependencies |
| `tests/` | 707 passing, 2 declared `xfail`s recording unimplemented operators |
| `papers/` | The unified draft, the two venue-targeted papers, appendices, bibliography, figures |
| `sessions/` | Eighteen session reports, `PROGRAM_PLAN.md`, and `STATE.json` |
| `submission/` | AUC IRB packet and instrument permission letters. **Not submitted** |
| `tracker/` | The programme on one HTML page |
| `archive/` | The full conversation transcript that produced the work |
| `verify_claims.py` | Re-derives every quantitative claim used in the unified draft |
| `make_urg_visualization.py` | Draws the Unified Reflective Graph from a real graph |

### `papers/`

| File | What it is |
|---|---|
| `UNIFIED_DRAFT.md` | **The unified paper.** Merges the architecture and ethics strands; supersedes P1/P2 where they disagree |
| `APPENDIX_OUTSTANDING_WORK.md` | **Read this before believing the draft.** What is blocked, what a search resolved, what would change the conclusions |
| `P1_ACM_TiiS_draft.md` | *Invariants You Can Run* — the architecture paper. Target: ACM TiiS |
| `P2_AIES_FAccT_draft.md` | *Refusal as a Safety Mechanism* — the ethics paper. Target: AIES / FAccT |
| `FORMAL_APPENDIX_corrected.md` | Notation, operator signatures, belief axioms, complexity table |
| `bibliography.json` | Manuscript references, machine-checked |
| `make_bibliography.py` | Generates `shadow_mirror_sources.bib` from the above |

> **P1 and P2 carry four figures superseded by Session 12.** See **OW-7** in the outstanding-work
> appendix. The unified draft carries the corrected values and states where it departs from them.

### `shadow_mirror/`

| Module | What it does |
|---|---|
| `engine.py` | Inference over stated desire, behaviour, arousal and avoidance |
| `urg.py` | Unified Reflective Graph — typed nodes, multi-parent provenance, contradiction as a first-class edge |
| `beliefs.py` | Order-invariant, exactly retractable belief revision |
| `inquiry.py` | Expected information gain over candidate questions |
| `invariants.py` | **Eleven** architectural properties as callable checks |
| `credible.py` | Credible sets, soft-EM person offsets with an identifiability guard |
| `deployment.py` | Refuses the biometric stream outside self/consented contexts |
| `ledger.py` | Hash-chained append-only consent; refuses retroactive grants |
| `formation.py` | Declared-only personhood, instrument registry, named refusals |
| `route_a.py` | Loaders and analyses for three public corpora |

**Mutation score: 59.9%** (5,114 mutants, 2,319 killed, 1,549 survived). Reported rather than tuned.

---

## Why it is shaped this way

| Concern | How the code answers it |
|---|---|
| No ground truth for "unknown" quadrants | Posterior *distributions* over states; refuses to infer below a minimum of paired evidence |
| Fluidity — states shift by the hour | Every output is a **dated snapshot** with an uncertainty interval |
| Reactivity — looking changes the reading | A `reactivity` caution that grows the more you consult it |
| The trauma landmine | `threat_response` is a **first-class hypothesis**; arousal + avoidance is never collapsed into "want" |
| Output should be a question, not a profile | The reflection layer only ever emits open-ended questions |
| Contradiction is often the fact, not a puzzle | A first-class **`ambivalence`** state holds "wants and doesn't want at once" un-collapsed |
| Per-question, not one global type | **Topic scoping** keeps "algebra" and "public speaking" separate |
| Stale readings shouldn't dominate | **Temporal decay** plus per-observation reliability weights |
| A missing channel is not a safe channel | An unobserved channel is recorded as **absent**, never imputed to zero |
| Consent must be demonstrable, not asserted | A hash-chained append-only ledger answers *what was granted at time T* |

---

## The ground rules

These governed every session, and most of what is unusual about this repository follows from them.

1. **No fabricated evidence, ever.** Every number in a paper is produced by code in this repository.
2. No human-subjects data is collected. Simulated participants are never called a result.
3. No text enters a manuscript in the past tense describing work not performed.
4. **No number enters a manuscript unless a file in the repository produces it AND the person writing
   the sentence has run that file.**
5. No additional evidence channel is added until the guard **refuses** rather than silently degrading.
6. **No citation enters a manuscript unless confirmed against a live source** with a resolvable
   identifier.
7. No instrument is administered whose permission terms are unconfirmed, and no item text is bundled
   with the software.
8. **Nothing about a person enters a model unless that person declared it or self-completed the
   instrument it came from.** Absence is not refusal — a refusing method must exist and explain itself.
9. **Nothing is recorded as pending until a search for a substitute has come back empty.**

---

## What is not done

The full list is `papers/APPENDIX_OUTSTANDING_WORK.md`. The short version:

- **No human-subjects evidence exists.** Nothing here establishes any effect on human reasoning,
  comprehension, trust or wellbeing, and no such claim is made.
- **The threat-confound claim requires primary collection.** No public corpus has the four-way
  intersection of stated stance, contradictable choice, time-locked arousal and a coercion
  manipulation.
- **No party outside this project has executed the software.**
- **The benchmark scripts that produce the headline numbers are missing** (OW-6). Recovering them is
  the first thing to do.

---

## Citation

> Moawad, O. (2026). *Shadow Mirror: a reference architecture for reflective human–AI interaction.*
> The American University in Cairo.

The software is a research instrument. **It is not suitable for clinical, educational, employment,
credit, insurance or policing use**, and it refuses to run in institutional deployment contexts.
