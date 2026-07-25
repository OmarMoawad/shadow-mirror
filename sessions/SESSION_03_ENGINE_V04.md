# Shadow Mirror — Session 03: Engine v0.4

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverables:** `shadow_mirror_v0.4.zip` (engine + 51 passing tests + head-to-head analysis),
`v030_vs_v040.json`, `benchmark_results_v040.json`, this report.

---

## 0. Summary

Six defects fixed, three of them by changing what the system is willing to say rather than by
making it cleverer. One critical safety defect is closed. Two new defects were found by the fix
process itself and are recorded rather than hidden.

| Defect | Status | Evidence |
|---|---|---|
| **D-19** Missing avoidance channel silently disables the trauma guard | ✅ **Fixed** | Guard sensitivity under ablation **0.0% → 100.0%**; false "hidden desire" rate **31.2% → 0.0%** |
| **D-12** Decayed evidence still passes the sufficiency gate | ✅ **Fixed** | Inference from decade-old evidence **100% → 0.0%** |
| **D-08** Posterior insensitive to sample size | ✅ **Fixed** | Posterior now sharpens monotonically; ECE where the model applies **0.171 → 0.044** |
| **D-09** Two different numbers both called "threat probability" | ✅ **Fixed** | `threat_confound_score` and `p_threat_response` are now separate, documented fields |
| **D-11** `belief_history` mixes topics | ✅ **Fixed** | History keyed by topic; instability now independent of interleaving |
| **D-21** No injectable clock | ✅ **Fixed** | `ShadowMirror(clock=…)`; inference is a pure function of observations and clock |
| **D-23** Overconfidence persists under *severe* misspecification | 🆕 **New, open** | ECE where the model does not apply **0.151 → 0.221** (regression) |
| **D-24** Arousal-only coverage labels excitement as threat | 🆕 **New, open** | Specificity under ablation **100% → 67.0%** |
| **D-25** `demo.py` puts context strings in the topic slot | 🆕 **New, open** | Demo scenarios silently split across four one-observation topics |

**Tests: 51 passing** (34 original commitments preserved, 1 deliberate documented behaviour change,
16 new regression tests that fail on v0.3.0 and pass on v0.4).

---

## 1. D-19 — the guard now refuses instead of degrading  *(critical)*

### The defect

`_infer_desire` computed `av = self._wmean(avoidance) if avoidance else 0.0`. An unobserved channel
became a reading of **zero avoidance** — that is, positive evidence *against* a threat response.
Session 2 measured the consequence: with the avoidance channel absent, guard sensitivity fell from
100% to **0.0%**, and 62.5% of compliance/fawn episodes were read as a hidden desire.

### The fix

Absent is now distinguished from zero. The engine tracks `guard_coverage` ∈
{`full`, `arousal_only`, `avoidance_only`, `none`} and computes the confound score only from
channels that were actually observed — returning `None` when none were.

The load-bearing decision is what follows from partial coverage. `latent_approach` — the reading
that says *"you want this even though you say you don't"* — is the one reading that requires ruling
out a threat response. It is therefore only assertable under `full` coverage. Otherwise its mass
moves to a new explicit state, **`unresolved_approach`**, and the report says so:

> "Both arousal and avoidance are required to tell a hidden preference apart from a threat response.
> Without them this reading is reported as 'unresolved_approach' and no hidden want is asserted."

### Measured effect

Benchmark suite run **unchanged** from Session 2, so these are directly comparable.

**Ablation condition — avoidance channel not observed (δ = 0.10, n = 400 per process):**

| | v0.3.0 | v0.4 |
|---|---|---|
| Guard sensitivity (threat caught) | 0.0% [0.0, 0.0] | **100.0% [100.0, 100.0]** |
| False "hidden desire" under threat | 31.2% [28.1, 34.4] | **0.0% [0.0, 0.0]** |
| …on the compliance/fawn process | 62.5% [57.8, 67.2] | **0.0% [0.0, 0.0]** |
| Genuine latent approach detected | 99.2% | **0.0%** — the system now refuses |
| Specificity | 100.0% | **67.0% [64.4, 69.8]** ← cost, see D-24 |

Outcome distribution under partial coverage, v0.4:

| True process | v0.4 says |
|---|---|
| `latent_approach` (calm) | `unresolved_approach` 100% — refusal |
| `latent_approach_aroused` | `threat_response` 100% — **false alarm** (D-24) |
| `threat_response` | `threat_response` 100% ✓ |
| `threat_compliance` | `threat_response` 100% ✓ |
| `explicit_aversion` | `explicit_aversion` 100% ✓ |

**Full-coverage condition — nothing lost, something gained:**

| δ = 0.10, both channels observed | v0.3.0 | v0.4 |
|---|---|---|
| False "hidden desire" under threat | 0.0% | 0.0% |
| Genuine latent approach detected | 80.6% [77.9, 83.2] | **87.1% [84.9, 89.4]** |
| …on the hard aroused-approach case | 61.5% | **74.2% [70.0, 78.5]** |
| Specificity | 94.4% | 94.4% |

So under full coverage the guard got *more* sensitive to genuine hidden preference (+6.5 points)
while remaining perfect on threat. The refusal only bites where it should: when the evidence needed
to make the distinction was never collected.

### The deliberate breaking change

One of the 34 original tests encoded a commitment v0.4 no longer keeps:

```python
# v0.3.0
def test_desire_says_no_but_acts_yes_reads_latent_approach():
    # stated aversion + approach behaviour, no confound channels at all
    assert m.current().top_desire() == "latent_approach"
```

Approach under stated reluctance is produced *both* by a hidden preference *and* by a threat
response. Session 2 measured what asserting the flattering one costs: a guard-free mismatch reading
misidentifies a threat response as hidden desire in **42.9%** [39.5, 46.2] of episodes and **95%** of
compliance episodes. So v0.4 refuses.

The test was not deleted to make the code pass. It was **rewritten to assert the new behaviour, with
the rationale in the docstring**, and a companion test was added proving the capability is
conditioned rather than removed:

```python
def test_latent_approach_is_still_assertable_with_full_coverage():
    # calm arousal + low avoidance does rule out the threat explanation
    assert b.guard_coverage == "full"
    assert b.top_desire() == "latent_approach"
```

---

## 2. D-08 — the posterior now responds to evidence

### The defect

v0.3.0 computed a weighted mean per channel and evaluated **one** Gaussian likelihood at that
centroid. The posterior was bit-identical at n = 2 and n = 100.

### The fix

Two changes, and the second matters more than the first.

**(a) Accumulate.** For a location model with known observation noise the weighted mean is the
sufficient statistic and the precision of that estimate grows with the total evidence weight *W*.
The log-likelihood is now `-W · (mean − corner)² / (2σ²)` per channel, so confidence grows with how
much evidence there is, not merely with where its centre falls.

**(b) Add an explicit "none of these fit" hypothesis.** `unmodelled` carries the likelihood a
hypothesis would have if the evidence centre sat 0.32 away from its corner — roughly half the
distance between adjacent hypotheses. Without this, accumulation makes the system *more* confident
in the nearest wrong answer as evidence piles up, which is the failure Session 2 measured.

One subtlety worth recording, because getting it wrong cost an implementation round: the
hypothesis-independent scatter term is deliberately excluded from both the named hypotheses and
`unmodelled`. "None of these fit" must mean *the centre of your evidence is not near any of them*,
not *your readings are noisy*. Charging observation noise against the named hypotheses but not
against `unmodelled` made the instrument abstain simply because a person answered inconsistently —
a different finding entirely, and the wrong one. Noise is carried by the dispersion term in the
uncertainty estimate instead.

A second subtlety: oscillating evidence sits far from every *directional* corner, so accumulation
initially read it as model misfit and `unmodelled` swallowed **ambivalence** — the one hypothesis
that actually explains oscillation. Misfit is now discounted by however much ambivalence already
accounts for. Without this, v0.4 would have destroyed a core contribution of the architecture while
appearing to improve.

### Measured effect — head-to-head on identical episodes

`analyze_v030_vs_v040.py` runs both engines on the same 200 episodes per cell, 20 cells.

**Where the model approximately applies (δ ≤ 0.15):**

| | v0.3.0 | v0.4 |
|---|---|---|
| Expected calibration error | 0.171 | **0.044** |
| Accuracy | 0.982 | 0.980 |
| Mean confidence | 0.813 | 0.940 |
| AUC(uncertainty → error) | 0.868 | **0.949** |
| Abstention rate | n/a | 0.3% |

At δ = 0 with n ≥ 16, ECE is **0.000** — the engine's stated confidence and its accuracy coincide
exactly, where v0.3.0 sat at a flat 0.154–0.208 regardless of how much evidence it had.

**Where the model materially does not apply (δ ≥ 0.30) — a regression, reported as such:**

| | v0.3.0 | v0.4 |
|---|---|---|
| Expected calibration error | 0.151 | **0.221** ← worse |
| Accuracy | 0.690 | 0.664 |
| Selective accuracy (when it commits) | n/a | 0.700 |
| AUC(uncertainty → error) | 0.845 | 0.800 |
| Abstention rate | n/a | 5.7% (21% at δ = 0.45, n = 32) |

### Honest reading

v0.4 trades *uniformly mediocre* calibration for *excellent when its model fits, worse when it does
not*. That is a real improvement only to the extent the instrument can tell which regime it is in.
It partly can — abstention rises monotonically with δ, and AUC(uncertainty → error) is 0.949 in the
good regime — but not enough: at δ = 0.45 with 32 observation pairs it abstains only 21% of the time
while being wrong 54% of the time.

**This is now defect D-23, and I have deliberately not tuned it away.** Widening the `unmodelled`
threshold would improve the δ = 0.45 numbers and damage the δ = 0.15 numbers; picking the value that
makes the benchmark look best is exactly the practice this programme exists to avoid. The honest
statement is that a two-parameter location model cannot distinguish "state A, displaced" from
"state B" when the displacement moves the centroid toward B, and no parameter choice fixes that.
Session 5 addresses it structurally, by testing whether more evidence channels or an explicit
misspecification test can separate the two.

---

## 3. D-12, D-09, D-11, D-21 — the rest

**D-12 — decay now reaches the gate.** An observation counts toward sufficiency only if its decayed,
reliability-weighted mass is at least `EPS_WEIGHT = 0.05` (about 4.3 half-lives of age). Dispersion
uses a weighted standard deviation, so a stale outlier no longer inflates uncertainty.

> Inference from decade-old evidence under a 30-day half-life: **100% → 0.0%.**
> Uncertainty on clear evidence 0.265 → **0.021**; on ambiguous evidence 0.618 → 0.405. The ratio
> between them widens from **2.3× to 19×** — the instrument now discriminates "I know this" from
> "I can't tell" far more sharply. Refusal on insufficient evidence remains 100%, over-refusal on
> clear evidence remains 0%.

**D-09 — one number, one name.** `threat_confound_score` is the raw, gate-facing quantity the safety
layer keys on, and is `None` when no confound channel was observed. `p_threat_response` is the
posterior mass of the threat hypothesis after normalisation. The ambiguous label
`threat_response_probability` is gone, and a test asserts it stays gone.

**D-11 — history is per topic.** `belief_history` is a `Dict[str, List[BeliefState]]`.
`_instability(topic)` is computed within a topic; a regression test logs identical per-topic evidence
interleaved and in blocks and asserts the instability figures match to 1e-6. `current(None)` now
means *pooled across topics* and actually computes it, rather than returning whatever snapshot
happened to be written last.

**D-21 — injectable clock.** `ShadowMirror(clock=lambda: fixed_datetime)`. Inference is now a pure
function of the observations and the clock, which is what makes the decay behaviour testable at all.

---

## 4. New defects found by fixing the old ones

**D-24 (medium) — under arousal-only coverage, excitement is labelled a threat.**
Arousal alone cannot separate fear from excitement; both raise it. With avoidance unobserved, v0.4
reports `threat_response` as the top hypothesis for 100% of aroused-approach episodes, dropping
specificity from 100% to **67.0%**. The *caution* is defensible — the architecture's stated design is
that the threat caution surfaces first. The *label* overclaims: the honest answer is "cannot tell",
i.e. `unresolved_approach` with the caution attached. Deferred to Session 4 rather than fixed here,
because one deliberate behaviour change per session is the limit of what can be properly justified.

**D-25 (low) — `demo.py` passes context strings into the topic slot.**
`add_batch` rows are `(axis, signal_type, value, topic, context, reliability)`. The demo passes
`("knowledge", "self_report", 0.9, "I know recursion cold")` — so "I know recursion cold" becomes a
*topic*, and each scenario is silently split across four one-observation topics. Under v0.3.0 this
combined with the broken `current(None)` to make demo scenarios 1 and 2 print
`insufficient_evidence` when sufficient evidence existed. Under v0.4 the pooled read is correct and
the scenarios report normally, but the demo is still mislabelling its own data.

---

## 5. What has changed in the claim inventory

**Now claimable, with running code:**

- Distinguishing an unobserved channel from a zero reading raises trauma-guard sensitivity under
  partial observation from 0.0% to 100.0% and eliminates the hidden-desire misreading (31.2% → 0.0%),
  at a specificity cost of 100% → 67.0%.
- Conditioning the `latent_approach` reading on confound coverage *increases* sensitivity to genuine
  hidden preference under full coverage (80.6% → 87.1%) while preserving a 0.0% misreading rate.
- Accumulating evidence with an explicit none-of-these component reduces expected calibration error
  from 0.171 to 0.044 where the model applies, and raises AUC(uncertainty → error) from 0.868 to
  0.949.
- Gating sufficiency on decayed weight eliminates inference from expired evidence (100% → 0.0%).

**Not claimable, and now measured:**

- Any general calibration improvement. Calibration is *worse* under severe misspecification
  (ECE 0.151 → 0.221).
- Any accuracy improvement. Accuracy is unchanged where the model applies and slightly lower where
  it does not.
- Robustness of the guard under arousal-only observation. It is safe but imprecise there.

---

## 6. Reproducing

```bash
unzip shadow_mirror_v0.4.zip && cd shadow_mirror_v0.4
pip install pytest
pytest -q                          # 51 passed
python demo.py
python analyze_v030_vs_v040.py     # head-to-head, writes v030_vs_v040.json
```

The Session 2 benchmark suite runs against v0.4 unmodified — no metric definition was changed, so
every before/after number in this report is like-for-like. Where v0.4 needed a metric v0.3.0 could
not produce (abstention, selective accuracy), it is reported *in addition to* the unchanged numbers,
never instead of them.

---

*Session 04 — unify the two codebases into v1.0-real, fixing D-10, D-13, D-14, D-15, D-16, D-20,
D-22 and D-24 — begins on your next "continue".*
