# Shadow Mirror — Session 02: Honest Benchmark Suite v2.0

**Author of record:** Omar Moawad (confirmed this session — Q1 closed)
**Session date:** 25 July 2026
**Deliverables:** `benchmark_suite_v2/` (runnable), `results.json`, three figures, this report.

---

## 0. What this session did

Deleted the fabricated benchmark. Rebuilt the remaining ones so that they measure the
system against a ground truth that exists independently of the system, under a
model-misspecification sweep, against baselines that are implemented in code, with
bootstrap confidence intervals on every headline number.

The suite is now permitted to fail — and it does, in four places. Those failures are
the most valuable output of the session, because each one is a specific, reproducible
finding that improves the work rather than decorating it.

| | v1.0 suite | v2.0 suite |
|---|---|---|
| Benchmarks that execute system code | 2 of 3 | 4 of 4 |
| Distinct scenarios per benchmark | 1 (repeated 50×/30×) | 200–500 independently sampled |
| Ground truth | none | known latent generative state |
| Baselines implemented | 0 (three quoted, none written) | 5 |
| Confidence intervals | none | on every headline number |
| Benchmarks that could fail | 0 | 4 |
| Bit-reproducible across runs | untested | **verified** — two full runs, byte-identical |
| Runtime | <1 s | 103 s |

---

## 1. The deletion

`benchmark_3_explanatory_calibration()` is gone. It drew 40 samples from `N(4.2, 0.6)`
and 40 from `N(3.5, 0.8)` and *t*-tested them; the "effect" was the hard-coded 0.7
difference between the two means, and no Shadow Mirror object was ever instantiated.

**Nothing replaces it that pretends to be human evaluation.** Explanatory calibration
is a question about how people read explanations, and it can only be answered by
asking people. That study is specified in Session 15 with an IRB packet. Until then the
claim does not appear in any paper.

The three invented comparators — "72% baseline pipeline", "41% random-information
baseline", "34% inconsistency reduction" — are retired with it. Two of them now have
real counterparts (§3, §5); the 34% figure has none and is deleted outright.

---

## 2. Method

**Simulator** (`benchmarks/simulator.py`). Observation streams are generated from a
known latent state or process. Values are Beta-distributed around a generating centre;
concentration κ controls per-observation noise.

**Circularity control.** The engine assumes each latent state sits at a fixed corner of
a 2-D signal space. Generating from exactly those corners would test self-consistency,
not validity. Every generator therefore displaces the true centre from the engine's
assumed corner by a random vector of magnitude **δ**, and all results are reported as a
function of δ. δ = 0 is the best case (the engine's model is exactly right); δ = 0.45 is
severe misspecification.

**Baselines** (`benchmarks/baselines.py`), all executed at benchmark time:

1. `quadrant_classifier` — median-split the two channels, read off the quadrant. What a
   competent analyst does by hand.
2. `signal_mismatch_only` — stated-vs-behaviour only, no arousal, no guard.
3. `arousal_as_desire` — folds physiological arousal into the action channel. Not a
   straw man: this is documented practice in affect-aware systems, and it is exactly
   what the Shadow Mirror signal table forbids.
4. `belief_gap_planner` — a faithful re-implementation of what v1.0's `InquiryPlanner`
   actually computes.
5. `oracle_planner` — exact expected information gain, given the true likelihoods.

**Statistics.** Percentile bootstrap (2,000 resamples) for every rate and mean; paired
bootstrap with Cohen's *d_z* for method differences; AUC via Mann–Whitney with mid-ranks;
ECE over 10 confidence bins with signed bias.

---

## 3. B1 — Latent state recovery and confidence calibration

*200 episodes per cell · 20 cells · ground truth = the generating latent state*

| δ | n=2 | n=4 | n=8 | n=16 | n=32 | mean confidence | signed bias |
|---|---|---|---|---|---|---|---|
| 0.00 | 95.0% | 99.5% | 100.0% | 100.0% | 100.0% | 0.82–0.85 | −0.15 |
| 0.15 | 92.0% | 96.0% | 99.5% | 100.0% | 100.0% | 0.78–0.81 | −0.19 |
| 0.30 | 76.5% | 79.5% | 79.0% | 89.5% | 90.0% | 0.72–0.76 | −0.10 |
| 0.45 | 59.0% | 57.0% | 57.0% | 50.0% | 52.0% | 0.69–0.75 | **+0.17** |

*(Accuracy of Shadow Mirror. Full table with 95% CIs and the quadrant baseline in `results.json`.)*

### Finding B1-1 — Confidence carries almost no information about correctness

Accuracy falls from **99% to 55%** as misspecification grows. Over the same range the
engine's reported confidence moves from **0.83 to 0.72**. The system is materially
underconfident when it is right (signed bias −0.15 to −0.19) and materially
**overconfident when it is wrong** (+0.17 at δ = 0.45). ECE stays in the 0.05–0.22 band
throughout without tracking the accuracy collapse.

This is defect **D-08** measured rather than asserted. The cause is structural: the
likelihood is evaluated once at the weighted centroid, so posterior sharpness is a
function of *where* the centroid falls, not of how much evidence supports it or how well
the model fits. See Figure 1.

The overconfident-when-wrong direction is the one that matters ethically. A reflection
instrument that becomes *more* confident than it should be exactly when its model of the
person is wrong is failing in the direction that harms the user.

### Finding B1-2 — The Gaussian-corner machinery does not beat a median split

Across all 20 cells, Shadow Mirror and the quadrant-threshold baseline are statistically
indistinguishable; paired differences range from −2.5 to +2.5 points with CIs spanning
zero in every cell.

This is not a criticism of the architecture, but it does relocate the contribution. **The
value of Shadow Mirror is not classification accuracy.** A median split gets the same
answer. The value is in what B2, B3 and the conformance checks measure: the safety guard,
the refusal behaviour, the preserved contradiction, the traceable provenance. The papers
should claim that, and should not claim accuracy advantages that do not exist.

---

## 4. B2 — The safety benchmark (headline result)

*400 episodes per generative process · 5 processes · 3 conditions*

Two processes produce the **same surface contradiction** — a person states aversion.
Only one of them is a hidden preference:

| Process | stated | action | arousal | avoidance | true mechanism |
|---|---|---|---|---|---|
| `latent_approach` | 0.20 | 0.80 | 0.30 | 0.20 | preference |
| `latent_approach_aroused` | 0.20 | 0.78 | 0.75 | 0.20 | preference (excitement) |
| `threat_response` | 0.20 | 0.15 | 0.85 | 0.85 | **threat** |
| `threat_compliance` | 0.20 | 0.60 | 0.85 | 0.65 | **threat (fawn/comply)** |
| `explicit_aversion` | 0.15 | 0.15 | 0.25 | 0.30 | aversion (control) |

The measured quantity is the rate at which each method reads a **threat** process as
`latent_approach` — i.e. tells the user "you secretly want this" when the true mechanism
is fear. This is the specific harm the trauma guard exists to prevent, and to my
knowledge it has not previously been quantified for any system of this kind.

### Finding B2-1 — The guard works, and the effect is large

With the avoidance channel observed (δ = 0.10):

| Method | False "hidden desire" under threat | True latent-approach detected |
|---|---|---|
| **Shadow Mirror (with guard)** | **0.0% [0.0, 0.0]** | 80.6% [77.9, 83.2] |
| Baseline: arousal-as-desire | 75.1% [72.1, 78.1] | 89.5% [87.4, 91.8] |
| Baseline: mismatch-only | 42.9% [39.5, 46.2] | 100.0% |

Guard sensitivity **100%** on both threat processes; specificity **94.4%** [93.2, 95.7].
AUC of the threat score across all five processes: **1.000**.

The cost is real and should be reported as such: sensitivity to genuine latent approach
falls from 100% to ~81%, concentrated entirely in the `latent_approach_aroused` case
(61.5% detected). **The guard trades ~19 points of hidden-preference sensitivity for
zero false threat-as-desire readings.** For an instrument that hands its output to a
person about themselves, that is the right side of the trade — but it is a trade, and the
paper must say so.

### Finding B2-2 (new defect, **D-19**) — The guard collapses to zero when the avoidance channel is missing

Ablating the avoidance channel — a realistic deployment condition, since many settings
have no avoidance measure at all:

| | avoidance observed | avoidance **missing** |
|---|---|---|
| Guard sensitivity | 100.0% | **0.0% [0.0, 0.0]** |
| False "hidden desire" under threat | 0.0% | **31.2% [28.1, 34.4]** |
| …on `threat_compliance` specifically | 0.0% | **62.5% [57.8, 67.2]** |
| AUC, fear vs excitement | 1.000 | 0.835 |

**Cause.** `_infer_desire` computes `av = self._wmean(avoidance) if avoidance else 0.0`.
A missing channel is silently coerced to **zero avoidance**, i.e. to positive evidence
*against* threat. The logistic `σ(4·(arousal + avoidance − 1.1))` then cannot reach the
flag threshold on arousal alone: with arousal ≈ 0.85 and avoidance imputed as 0, the
score is σ(−1.0) ≈ 0.27.

This is a missing-data-as-negative-evidence bug in the single most safety-critical line
of the system. It is silent: nothing in the report tells the user that the guard is
inactive because a channel is absent. **Fix in Session 3:** distinguish *absent* from
*zero*, and refuse to issue a desire reading at all when the guard's required channels
are unavailable.

See Figure 2.

---

## 5. B3 — Refusal calibration

*300 episodes per condition*

| Condition | Behaviour | Target |
|---|---|---|
| Genuinely insufficient evidence (1 pair) | refuses **100.0%** [100.0, 100.0] | ~100% ✅ |
| Clear evidence (8 pairs, δ = 0) | over-refuses **0.0%** [0.0, 0.0] | ~0% ✅ |
| Ambiguous evidence (8 pairs, centred 0.5, high dispersion) | refuses 0.0%; uncertainty **0.618** [0.614, 0.622] vs **0.265** [0.260, 0.271] on clear evidence | — |
| Decade-old evidence, 30-day half-life | reports `status: ok` **100.0%** | ~0% ❌ |

### Finding B3-1 — Refusal gating is correct at the extremes

No over-refusal, no under-refusal. The one behaviour that deserves comment is the
ambiguous case: the system does not refuse, but it does report **2.3× higher
uncertainty**. That is defensible — arguably preferable to refusing, since the elevated
uncertainty is itself the informative output — but it is a design choice that should be
stated rather than left implicit.

### Finding B3-2 — D-12 confirmed at 100%

Four observations from ten years ago, under a 30-day half-life, still yield a confident
report. Their decay weight is ~2⁻¹²¹ ≈ 0. The sufficiency gate counts raw observations;
decay is applied only to the means. The fix (effective sample size `n_eff = (Σw)²/Σw²`)
is scheduled for Session 3.

---

## 6. B4 — Inquiry planning against an information-theoretic oracle

*500 trials per condition · 4 candidate binary tests · planner likelihood-estimation noise σ = 0.12*

| Planner | Regret, close hypotheses | Regret, separated hypotheses | Top-1 agreement with oracle |
|---|---|---|---|
| **Proposed EIG planner** | **0.161** [0.138, 0.187] | **0.195** [0.168, 0.223] | 62.8–67.8% |
| v1.0 belief-gap planner | 0.579 [0.547, 0.612] | **1.000** [1.000, 1.000] | 21.8% / 0.0% |
| Random selection | 0.550 [0.515, 0.584] | 0.562 [0.528, 0.597] | 24.4–25.6% |

### Finding B4-1 — The v1.0 "expected information gain" planner computes no information gain

`InquiryPlanner.plan_inquiry` scores inquiries as `expected_benefit = 1 − gap`, where
`gap` is the difference between two *prior* beliefs. That quantity does not depend on the
candidate observations at all, so the planner carries no signal about which observation
to seek. Measured consequence: **regret 0.579 vs random's 0.550** — it is not better than
random when it fires, and its confidence intervals overlap random's completely.

Worse, when hypotheses are well separated it emits nothing at all (regret 1.000, silent
in 100% of trials), which is exactly backwards: a confidently-held wrong hypothesis is
precisely when a discriminating observation is most valuable.

A genuine EIG planner — 40 lines, in `baselines.py` — achieves **0.16–0.20 regret** even
with substantial noise in its likelihood estimates. The architecture paper's claim of
"information-gain-driven inquiry generation" becomes true only if this replaces the
current heuristic. Scheduled for Session 4.

See Figure 3.

---

## 7. Conformance checks (PASS/FAIL, never scored)

Structural properties that hold or fail *by construction* are not experimental results.
Reporting "100%" for a check that cannot fail is what made the v1.0 numbers look like
evidence when they were not. These are reported as pass/fail with the observation:

| | Invariant | Result | Observation |
|---|---|---|---|
| C1 | I Evidence traceability | ✅ PASS | explanation links to its supporting evidence |
| C2 | II Provenance preservation | ❌ **FAIL** | 0 of 2 parents recovered from a two-parent DAG |
| C3 | III Revision history | ✅ PASS | 5/5 belief transitions recorded |
| C4 | V Hypothesis independence | ✅ PASS | competitor survives contradiction of its rival |
| C5a | order invariance, moderate evidence | ✅ PASS | deviation 4.4 × 10⁻¹⁶ |
| C5b | order invariance, extreme evidence | ❌ **FAIL** | same evidence, three orders → **0.0396 / 0.9900 / 0.9900** |
| C6 | IV Explicit uncertainty | ✅ PASS | uncertainty summary always emitted |

**5 of 7 pass.**

### Finding C5b (new defect, **D-20**) — Belief depends on the order evidence arrives

Five pieces of evidence, three orderings, three different final beliefs — spanning
**0.04 to 0.99**, a 95-percentage-point swing from ordering alone.

The cause is the clamp `posterior = max(0.01, min(0.99, posterior))` in
`BeliefRevisionEngine.bayesian_update`. Clipping is not invertible: once the posterior is
pinned at 0.99, the information about *how far past* 0.99 the evidence pushed it is
destroyed, and subsequent contrary evidence starts from the wrong place.

Order-invariance is not one of the paper's ten invariants, but it is entailed by calling
the operator Bayesian — conditioning on a set of conditionally independent observations
is commutative. A reviewer will test this. **Fix in Session 4:** accumulate in log-odds
space and clamp only at the presentation layer, never in the state.

---

## 8. New defects added to the register

| # | Sev | Where | Defect |
|---|---|---|---|
| **D-19** | **Critical (safety)** | `engine.py:_infer_desire` | Missing avoidance channel is coerced to zero, silently disabling the trauma guard (sensitivity 100% → 0%, false hidden-desire rate 0% → 31%) |
| **D-20** | **High** | `shadow_mirror_v1.py:bayesian_update` | Posterior clipping makes belief order-dependent; 0.04 vs 0.99 for identical evidence |
| **D-21** | Medium | `engine.py` | No injectable clock; wall-clock decay makes results non-reproducible at ~10⁻¹³ and untestable in principle |
| **D-22** | Medium | `engine.py:InquiryPlanner` (v1) | `expected_benefit` computes no information gain; performs no better than random |

D-19 supersedes the earlier severity of the trauma guard as "verified working" — it works
only when a channel that many deployments will not have is present.

---

## 9. What can now be claimed in a paper, and what cannot

**Claimable, with running code behind it:**

- The threat guard reduces the rate of misreading a threat response as a hidden desire
  from 43–75% (guard-free baselines) to 0.0%, at a cost of ~19 points of sensitivity to
  genuine latent approach. *n* = 400 per process, 95% CIs, five generative processes,
  two misspecification levels.
- The guard's protection is entirely contingent on the avoidance channel; with that
  channel absent, protection falls to zero. (Reported as a limitation *and* as a design
  requirement: the system should refuse rather than degrade silently.)
- Refusal gating is exactly calibrated at the extremes: 100% refusal on insufficient
  evidence, 0% over-refusal on clear evidence.
- The system reports 2.3× higher uncertainty on ambiguous evidence than on clear evidence.
- An expected-information-gain planner reduces normalised regret from 0.55–1.00 to
  0.16–0.20 against an information-theoretic oracle.
- 5 of 7 architectural conformance checks pass; the two failures are documented.

**Not claimable, and now deleted:**

- Any statement about human ratings of explanations.
- Any accuracy advantage over simple baselines on latent-state recovery.
- Any claim that the current inquiry planner is information-gain-driven.
- The 72% / 41% / 34% / F1 = 0.81 figures.

---

## 10. Reproducibility

```bash
cd benchmark_suite_v2
pip install matplotlib          # only needed for the figures
python run_benchmarks.py        # ~103 s, writes results.json
python make_figures.py          # reads results.json, writes the three PNGs
```

Determinism was verified by running the full suite twice and diffing `results.json`:
**byte-identical**. Achieving that required freezing temporal decay in the three
benchmarks that do not test it (D-21) — without that, wall-clock-dependent decay
introduces ~10⁻¹³ drift between runs. The stale-evidence probe in B3 deliberately keeps
decay on.

Every figure is generated from `results.json`. No number in this report was typed by hand.

---

*End of Session 02. Session 03 — Engine v0.4, fixing D-08, D-09, D-11, D-12, D-19, D-21 — begins on your next "continue".*
