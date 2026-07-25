# Shadow Mirror — Session 04: One Codebase, v1.0

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverable:** `shadow_mirror_v1.0.zip` — 78 passing tests, zero third-party dependencies,
7/7 architectural conformance.

---

## 0. Summary

The two codebases are now one. The URG, belief revision, inquiry planning and the EWK profile were
rebuilt **on top of** the v0.4 engine rather than beside it, so nothing that made the original work
distinctive was lost: the consent gate, the trauma guard, `ambivalence`, temporal decay, topic
scoping and refusal-as-output are all still there, and now so is the reflective graph layer.

| Defect | Status | Evidence |
|---|---|---|
| **D-10** v1.0 prototype replaced rather than extended v0.3.0 | ✅ Fixed | One package. Every v0.3.0 capability retained; 78 tests |
| **D-20** Belief revision is order-dependent | ✅ Fixed | All **120 permutations** agree to machine precision (was a 0.95 spread) |
| **D-22** Inquiry planner computes no information gain | ✅ Fixed | Regret vs oracle **0.579 → 0.000** on the planner's own test; selects the discriminating observation |
| **D-14** `trace_provenance` truncates multi-parent DAGs | ✅ Fixed | 2/2 parents recovered (was 0/2); branching and cyclic cases tested |
| **D-13** EWK tension never fires on its own demo | ✅ Fixed | Flagship scenario now registers two tensions |
| **D-24** Arousal-only coverage labels excitement a threat | ✅ Fixed | Excitement `threat_response` **100% → 0%**, caution retained |
| **D-15** Naive vs aware timestamps block merging | ✅ Fixed | One aware convention throughout |
| **D-16** `utcnow()` / `node_link_data()` deprecations | ✅ Fixed | NetworkX removed entirely; zero dependencies |
| **D-25** `demo.py` puts context strings in the topic slot | ✅ Fixed | Scenarios now carry real topics |

**Architectural conformance: 4/7 → 7/7.**

---

## 1. Conformance, prototype vs v1.0

Same six checks as Session 2, same definitions, plus one new check for Invariant VIII. Run against
both implementations by `conformance_v10.py`.

| | Prototype | v1.0 |
|---|---|---|
| C1 · I Evidence traceability | PASS | PASS — 0 orphan explanations |
| C2 · II Provenance preservation | **FAIL** — 0/2 parents | **PASS** — 2/2 parents |
| C3 · III Revision history | PASS | PASS |
| C4 · V Hypothesis independence | PASS | PASS — contradiction *held*, 1 contested hypothesis retained |
| C5 · order invariance (120 permutations) | **FAIL** — spread 0.9504 | **PASS** — spread 0.00e+00 |
| C6 · IV Explicit uncertainty | PASS | PASS |
| C7 · VIII Inquiry justification | **FAIL** — no information-gain content | **PASS** — selects the discriminating observation, 0.714 bits |
| | **4/7** | **7/7** |

---

## 2. D-20 — belief revision is now commutative

Bayesian conditioning on conditionally independent observations *is* commutative — Jacobs (2025),
*Commutativity of probabilistic belief revision*, **Frontiers in Cognition**, DOI
`10.3389/fcogn.2025.1623227`. Human belief revision is not, because recency and priming are real, but
that is a fact about people and not a licence for the arithmetic to drift.

The prototype clamped the posterior to [0.01, 0.99] **inside the state** after every update. Clamping
is not invertible: once pinned at 0.99 the information about how far past 0.99 the evidence pushed is
gone, and later contrary evidence starts from the wrong place.

`beliefs.py` accumulates in **log-odds** — unbounded and additive — and stores contributions in a
**dict keyed by evidence id**. Dicts keyed by identity have no meaningful order, which is precisely
the property that was missing. Clamping happens only in `display_probability()`.

Four consequences, each with a test:

- Every one of the 120 permutations of five extreme observations gives the same posterior to within
  1e-12 (prototype: 0.0396 to 0.9900).
- Twenty strongly-confirming observations followed by twenty strongly-disconfirming ones return the
  belief to **exactly 0.5**. The prototype could not do this at all.
- Re-applying the same evidence id does not double-count it.
- `retract()` is exact — removing a contribution restores the previous state bit-for-bit, which is
  what makes an audit trail meaningful rather than decorative.

---

## 3. D-22 — the planner now computes information

`inquiry.py` computes the mutual information between a candidate observation's outcome and the
hypothesis variable, under the current posterior. Against an oracle over 300 randomised trials the
planner's mean normalised regret is **0.000** — it picks the oracle's choice — where the prototype's
belief-gap heuristic scored 0.579 against random selection's 0.550.

Two behavioural changes matter more than the number:

- **It no longer goes silent when hypotheses look settled.** The prototype emitted nothing once the
  belief gap exceeded 0.2, which is backwards: a confidently-held wrong hypothesis is exactly when a
  discriminating observation is worth most.
- **Every inquiry states what it would resolve**, in bits, and which hypotheses it separates — which
  is what Invariant VIII actually asks for. `gain_per_unit_cost` lets a person weigh an inquiry that
  costs them something against one that does not.

---

## 4. D-14 — provenance is a DAG

`urg.ancestors()` walks every provenance parent by breadth-first search. The prototype's
`trace_provenance` followed `preds[0]` only, so evidence derived from two sources reported one and
silently dropped the other — a direct violation of the architecture's own Invariant II.

Tested on the two-parent case, a four-root branching DAG (all four paths recovered), and a cyclic
graph (terminates, does not hang).

The URG is written in **pure standard library**. The rest of Shadow Mirror is dependency-free on
purpose — local-first and auditable — and importing NetworkX for an adjacency dict would have traded
that away for nothing. It also removes the deprecated `node_link_data` call (D-16). A test asserts
the string "networkx" does not appear in the module.

Contradiction is a first-class edge. `contested_hypotheses()` returns hypotheses carrying both
supporting and contradicting evidence, so an explanation can report a tension instead of quietly
preferring the later write.

---

## 5. D-13 — the tension detector fires on its own example

The prototype required `K > 0.7 and W < 0.3`, or `E > 0.7 and K < 0.3`, or `|K − W| > 0.5`. Its
flagship demonstration — K = 0.30, W = 0.75, E = 0.80, a student working hard, distressed, and not
getting results — missed all three by a hair and printed *"No significant tension detected"*.

`ewk.py` computes continuous tension magnitudes over the unit square against a single documented
threshold (0.35). The flagship scenario now registers **two**: `effort_without_return` (0.525) and
`distress_without_return` (0.560). Aligned streams still produce none, and the profile refuses below
two observations per stream.

Every tension is emitted as a question, and the reading carries the disclaimer verbatim: *"These are
discrepancies between observed streams, not claims about an inner state."*

---

## 6. D-24 — a caution that stops overclaiming

Under arousal-only coverage the threat *caution* still fires — the confound score is computed and
`insufficient_confound_coverage` is flagged — but the threat hypothesis is no longer allowed to win
the posterior. One channel can raise a question; it cannot settle one.

Outcome labels with the avoidance channel unobserved (400 episodes per process):

| True process | v0.4 said | v1.0 says |
|---|---|---|
| `latent_approach` | `unresolved_approach` 100% | `unresolved_approach` 100% |
| `latent_approach_aroused` (excitement) | **`threat_response` 100%** | `unresolved_approach` 59%, `ambivalence` 41% |
| `threat_response` | `threat_response` 100% | `explicit_aversion` 86%, `ambivalence` 13% |
| `threat_compliance` | `threat_response` 100% | `ambivalence` 80%, `unresolved_approach` 15% |

The safety-critical number is unchanged: **0.0%** of threat episodes are read as a hidden desire, and
guard sensitivity via the flag remains **100%**. What changed is that the system no longer tells
someone who was excited that they were probably afraid.

---

## 7. No regression elsewhere

The Session 2 benchmark suite was re-run **unmodified** against v1.0. B1, B3 and B4 are numerically
identical to Session 3; B2's headline figures are unchanged (0.0% false hidden-desire under full
coverage, guard sensitivity 100%, genuine latent approach detected 87.1%). The specificity cost under
ablation (67.0%) is unchanged, because it is driven by the caution flag, which was deliberately kept.

`pytest`: **78 passed**. That is 34 original v0.3.0 commitments, one documented behaviour change from
Session 3, and 43 regression tests written against specific defects.

---

## 8. Still open

| Defect | Severity | Session |
|---|---|---|
| **D-23** Overconfidence persists under severe misspecification (ECE 0.151 → 0.221 for δ ≥ 0.30) | High | 5 |
| **D-02, D-04, D-05, D-18** The Kimi-generated paper: fabricated statistic, six wrong citations, vendor watermark, quarter-length | Critical | 6, 11 |
| **D-17** Figure labels contain literal `\n` | Low | 12 |

One observation for Session 5: under partial coverage `ambivalence` now absorbs 41–80% of episodes.
Oscillation in the simulated action channel is being read as genuine ambivalence. That may be
correct — the streams really do disagree — but it deserves a dedicated benchmark before it appears in
a paper, because "ambivalence" is a claim about a person and it is currently the residual bucket.

---

## 9. Reproducing

```bash
unzip shadow_mirror_v1.0.zip && cd shadow_mirror_v1.0
pip install pytest
pytest -q                    # 78 passed
python demo.py
python conformance_v10.py    # prototype 4/7 vs v1.0 7/7
```

No third-party runtime dependencies. `pytest` is needed only for the tests, and `networkx`/`numpy`
only for the archived prototype kept alongside for the comparison.

---

*Session 05 — the conformance suite as executable property tests, plus D-23 — continues automatically.*
