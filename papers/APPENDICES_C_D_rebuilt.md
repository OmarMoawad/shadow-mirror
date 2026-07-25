# Appendix C — Prototype-to-Architecture Conformance (rebuilt)

**Drop-in replacement for p. 290.** Every row names the file and, where a behavioural claim is made,
the test that settles it. `shadow_mirror` v1.0, 312 tests passing, 2 recorded xfails.

| Architectural concern | Implementation | Status | Settled by |
|---|---|---|---|
| Structured observation | `models.py` | Implemented | `test_operator_I_ingest_*` |
| Knowledge / desire hypotheses | `engine.py` | Implemented — likelihood-accumulating, not heuristic | `test_d08_posterior_sharpens_*` |
| Temporal decay | `engine.py` | Implemented; 30-day half-life **still unvalidated**; expiry now gates sufficiency | `test_d12_*` |
| Consent state and scope | `consent.py` | Implemented | `test_consent_and_patterns.py` |
| Safety flags and threat guard | `safety.py`, `engine.py` | Implemented — **refuses under partial observation** | `test_d19_*` (5 tests) |
| Longitudinal descriptive patterns | `patterns.py` | Implemented, associative | `test_consent_and_patterns.py` |
| Journal inspect / export / delete | `store.py` | Implemented | `test_reflect_and_store.py` |
| **Unified evidence/context graph** | `urg.py` | **Implemented** — typed, transactional, multi-parent provenance, zero dependencies | `test_v10_unified.py` (7 tests) |
| **Belief revision engine** | `beliefs.py` | **Implemented** — order-invariant, exactly retractable, O(1) per update | `test_axiom_B2/B3/B4`, `test_belief_update_is_linear` |
| **Inquiry planner** | `inquiry.py` | **Implemented** — expected information gain | `test_d22_*` (5 tests) |
| **Architectural invariants I–X** | `invariants.py` | **Implemented as executable checks** | `test_invariants.py` (200 randomised states + 16 negative tests) |
| **Emotion–Will–Knowledge profile** | `ewk.py` | **Implemented** — observable streams, tensions as questions | `test_d13_*` (4 tests) |
| **Credible sets / abstention** | `credible.py` | **Implemented** | `test_operator_X_credible_set_*` |
| **Per-person offset estimation** | `credible.py` | Implemented; effective at moderate misspecification only | `experiment_d23.py` |
| Encryption at rest | — | Not implemented | — |
| **Causal inference** | — | **Not implemented — prose only** (monograph pp. 64–66) | recorded xfail |
| **Knowledge consolidation** $K_t \leftarrow B_t$ | — | **Not implemented — prose only** (p. 145) | recorded xfail |
| Multimodal acquisition | — | Not implemented | — |
| Reflective execution engine / event queue | — | Not implemented | — |
| Human collaboration layer (UI) | `cli.py` only | Partial — command line, no interface | — |
| Distributed deployment | — | Not implemented; **not the bottleneck** — `engine.add()` is quadratic (D-28) | measured, §A.10 |
| Emotion AI / emotion-engineering loop | — | Proposed, research-only | — |
| Four-family hypothesis-and-confirmation module | — | Proposed, research-only | — |
| Human-subject validation | — | **Not performed** | — |
| Clinical or employment use | — | **Prohibited** | `ETHICS.md` |

Fourteen concerns are now implemented and test-backed, against seven in v0.3.0. Four are recorded as
specified-but-unbuilt rather than left ambiguous.

---

# Appendix D — Claim-to-Validation Matrix (rebuilt)

**Drop-in replacement for p. 291.** The original structure — claim, evidence now, required
validation, failure signal — is kept, because it is the right structure and better than most
published architecture papers manage. What changes is the *evidence now* column, which was
"architecture only" or "theory only" for thirteen of fifteen claims and is no longer.

Status key: **Proven** = a test or measurement settles it · **Partial** = measured under
simulation, not with people · **Unsupported** = no evidence yet · **Removed** = withdrawn.

## D.1 Claims that measurement has settled

| Claim | Status | Evidence now | Falsification signal |
|---|---|---|---|
| **The architecture is safer than a guard-free baseline** | **Proven (simulation)** | Misreading a threat response as a hidden desire: **0.0%** [0.0, 0.0] with the guard vs **42.9%** [39.5, 46.2] (mismatch-only) and **75.1%** [72.1, 78.1] (arousal-as-desire). *n* = 400 per process, 5 processes, 2 misspecification levels. `benchmarks/suite.py::bench_2` | Any baseline matching 0.0%, or the guard exceeding 0.0% under full coverage |
| **Refusal is calibrated** | **Proven (simulation)** | 100% [100.0, 100.0] refusal on insufficient evidence; 0.0% [0.0, 0.0] over-refusal on sufficient evidence. `bench_3` | Over-refusal above 0, or inference below the evidence threshold |
| **Expired evidence stops being evidence** | **Proven** | Inference from decade-old observations 100% → **0.0%**. `test_d12_*` | Any inference from evidence below `EPS_WEIGHT` |
| **Belief revision is order-invariant** | **Proven** | All **120 permutations** agree to machine precision; prototype spread was 0.9504. `test_d20_*` | Any permutation pair differing by more than 1e-12 |
| **Contradiction is preserved, not overwritten** | **Proven** | `contested_hypotheses()` retains both edges. `test_contradiction_is_preserved_*` | A contradicting write reducing the hypothesis count |
| **Provenance is fully recoverable** | **Proven** | 2/2 parents from a two-parent DAG (prototype: 0/2); branching and cyclic cases. `test_d14_*` | Any parent unreachable from `ancestors()` |
| **The ten invariants are decidable** | **Proven** | All ten hold over 200 randomised states; 16 negative tests prove each check can fail. `test_invariants.py` | A well-formed state failing a check, or a violating state passing one |
| **Inquiry planning is information-driven** | **Proven** | Regret vs oracle **0.000** (belief-gap heuristic 0.579; random 0.550). `test_d22_beats_random_*` | Regret indistinguishable from random |
| **Uncertainty is honestly reported** | **Partial** | Where the model applies, ECE **0.044** and AUC(uncertainty→error) **0.949**. Where it does not, ECE **0.221** — reported as a limitation. `analyze_v030_vs_v040.py` | Confidence failing to track accuracy where the model does apply |
| **Multiple hypotheses reduce premature closure** | **Partial** | Credible-set coverage exceeds point accuracy at every misspecification level (78.2% → 88.0% at δ = 0.30) for +0.45 set size. Does **not** reach nominal 90%. `experiment_d23.py` | Coverage no better than point accuracy, or set size exploding |
| **Ambivalence is a distinct state, not a residual** | **Proven (this session)** | Precision **34.0% → 97.6%** once gated on temporal structure; recall unchanged at 100%. `experiment_ambivalence.py`, `test_d29_*` | Non-oscillating processes reading as ambivalence above ~5% |

## D.2 Claims still awaiting people

These are unchanged from your original matrix, because nothing that has happened in code can settle
them. The "required validation" column is yours; I have only made the failure signals sharper where
the code now suggests what to look for.

| Claim | Status | Required validation | Falsification signal |
|---|---|---|---|
| Consent can gate inference | Unit behaviour only | Usability, comprehension and coercion study | Users cannot predict or control data use |
| Questions reduce verdict-like framing | **Partial** — Invariant X now checks output phrasing mechanically (`test_x_*`), which is necessary but not sufficient | Controlled framing study | Equal or greater over-reliance despite question phrasing |
| Uncertainty improves calibration **in people** | Unsupported | Pre-registered calibration study | Worse Brier score or worse trust calibration than a no-uncertainty interface |
| Provenance improves error detection | Unsupported | Human-factors experiment with planted errors | Users miss planted errors at the same rate |
| Longitudinal reflection improves learning | Unsupported | Longitudinal external study | No transfer, or increased dependence |
| Sensor disagreement is informative | **Partial** — the guard ablation shows disagreement *between* channels is decisive for safety | Modality-specific construct study | Unstable or non-generalising effects |
| EI capacities add useful profile information | Evidence synthesis only | Construct-specific tasks, calibration, transfer, incremental validity | Global score adds no value over personality |
| Emotion AI adds evidence beyond self-report | Theory only | Person-independent, subgroup, calibration, abstention and correction study | Benchmark gain does not transfer, or increases false inference |
| Emotion engineering supports user-owned outcomes | Closed-loop proposal | Randomised reversible intervention study | No benefit over a non-adaptive interface, or increased dependence |
| E–W–K coupling predicts context-linked patterns | Formal hypothesis; detector now fires correctly | Intensive longitudinal multilevel study | Coupling reverses or disappears under valid operationalisations |
| Population priors improve question selection | Theory only | Comparison against open-question and personal-evidence baselines | Priors add no coverage or dominate the person |
| Neutral confirmation improves mapping | Protocol only | Randomised suggestion and correction study | False uptake, anchoring, or recall distortion |
| Competency comparison supports development | Construct proposal | Construct, invariance and longitudinal validation | Unstable score, or harmful normative labelling |

## D.3 Claims withdrawn

| Claim | Why |
|---|---|
| EWK-augmented explanations improve calibration ratings, *t*(39) = 4.23, *p* < 0.001 | **Removed.** No such measurement exists; the statistic came from two hard-coded Gaussians. |
| Belief revision appropriate in 100% of cases vs a 72% baseline | **Removed.** The assertion was tautological and the baseline had no implementation. |
| Inquiry recommendations align with expert tests in 100% of cases vs 41% random | **Removed.** Same. Replaced by regret against an information-theoretic oracle. |
| The URG improves reflective reasoning over disaggregated storage | **Removed as stated.** Session 3 measured the inference layer as statistically indistinguishable from a median split in all 20 conditions. The URG's benefits are **structural** — traceability, provenance, contested-hypothesis retention — and the claim is now made in those terms only. |
| Reference architecture is scalable | **Removed as stated.** `engine.add()` is quadratic (measured 3.8× per doubling). Restate as "reference design pending scalability work", and name incremental recompute as the first target. |

---

## D.4 The three sentences this matrix licenses

1. Under simulation with known ground truth, conditioning the hidden-preference reading on the
   evidence needed to rule out a threat response reduces the rate of that misreading from
   42.9–75.1% to 0.0%, at a cost of 19 points of sensitivity and 33 points of specificity when the
   required channel is absent.
2. The ten architectural invariants are decidable properties, and a compliant implementation exists
   with 312 passing tests, including 16 that prove each check can fail.
3. Nothing in this work establishes any effect on human reasoning, and no claim to that effect is
   made.
