# Shadow Mirror — Session 08: The Claim Matrix, Rebuilt

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverables:** `APPENDICES_C_D_rebuilt.md` (drop-in replacements for pp. 290–291),
`experiment_ambivalence.py`, `shadow_mirror_v1.0.zip` (**312 passing**, 2 xfailed).

---

## 0. Summary

Your original Claim-to-Validation Matrix had fifteen claims. **Thirteen of them read "architecture
only", "theory only" or "no evidence".** That was an honest self-assessment when it was written.

It is now out of date, which is the best possible reason to rewrite an appendix.

| | Original (p. 291) | Rebuilt |
|---|---|---|
| Claims with only theoretical support | 13 of 15 | 8 of 24 |
| Claims settled by a test or measurement | 0 | **8** |
| Claims partially settled under simulation | 2 | 4 |
| Claims withdrawn | 0 | **5** |
| Conformance concerns implemented | 7 | **14** |

And the Session 4 watch item turned out to be a real defect with a clean fix: **ambivalence
precision 34.0% → 97.6%.**

---

## 1. Ambivalence was a residual bucket. Now it is not.

Session 4 noted that under partial confound coverage, `ambivalence` was returned for 41–80% of
episodes, and flagged it: *"that may be correct — the streams really do disagree — but 'ambivalence'
is a claim about a person and it is currently the residual bucket."*

The engine computed ambivalence from a weighted standard deviation. Dispersion has at least three
quite different causes and only one of them is ambivalence:

- **oscillation** — swinging toward and away over time. This *is* ambivalence.
- **noise** — a stable middling attitude, measured imprecisely. Not ambivalence.
- **drift** — a monotonic change of mind across the window. Not ambivalence; it is the *opposite*,
  a resolution.

A standard deviation cannot tell them apart. So I generated all three, plus a stable control, at
400 episodes each.

### Before

| True process | Read as ambivalence | Dispersion | Sign-flip rate | Lag-1 autocorrelation |
|---|---|---|---|---|
| oscillation | 100.0% [100.0, 100.0] | 0.357 | 0.999 | **−0.843** |
| noise | **95.5% [93.5, 97.5]** | 0.259 | 0.548 | −0.123 |
| drift | **98.8% [97.5, 99.8]** | 0.246 | 0.219 | **+0.516** |
| stable attraction | 0.0% [0.0, 0.0] | 0.071 | 0.547 | −0.135 |

**Precision 34.0%.** Two of every three ambivalence readings were wrong — and one of those two was
telling a person who had *made up their mind* that they were conflicted. For an instrument whose
entire claim is that it holds contradiction open rather than forcing a resolution, reporting
resolution as contradiction is the exact inversion of the thing it is for.

Note the third and fourth columns. Dispersion is nearly identical for noise (0.259) and drift
(0.246), and not far off oscillation (0.357). But lag-1 autocorrelation separates all three
cleanly: strongly negative for alternation, near zero for noise, strongly positive for drift.

### The fix

Ambivalence is now gated on temporal structure as well as spread:

```
ambivalence = min(0.9, 2.2 · dispersion) · gate,
gate = clip((−ρ₁ − 0.20) / 0.45, 0, 1)
```

where ρ₁ is the mean lag-1 autocorrelation of the stated and action series. Five lines.

### After

| True process | Read as ambivalence |
|---|---|
| oscillation | **100.0% [100.0, 100.0]** — recall unchanged |
| noise | 95.5% → **2.5% [1.0, 4.2]** |
| drift | 98.8% → **0.0% [0.0, 0.0]** |
| stable attraction | 0.0% |

**Precision 34.0% → 97.6%. Recall unchanged at 100%.** Four regression tests pin it, including one
that constructs an oscillating series and a drifting series with dispersion within 0.12 of each
other and asserts that only the first reads as ambivalence.

**A proposal, not implemented.** Strongly *positive* lag-1 autocorrelation is itself an informative
reading — "your position on this moved steadily across the window" — and the engine now computes the
statistic but discards it. That is a candidate new state, and it belongs in the research agenda
rather than in a session that has already made one behaviour change.

---

## 2. Appendix C — conformance

Fourteen architectural concerns are now implemented and test-backed, against seven in v0.3.0. The
new rows are the URG, belief revision, inquiry planning, the invariant checks, EWK, credible sets
and per-person offset estimation — each with the file and the tests that settle it.

Four concerns are recorded as **specified but unbuilt** rather than left ambiguous: causal inference,
knowledge consolidation, multimodal acquisition, and the reflective execution engine. Two of those
carry strict `xfail`s in the suite, so they cannot quietly become "implemented" in a future summary.

One row worth reading twice: **distributed deployment is not the bottleneck.** The original appendix
listed it as a gap, and the second external draft proposed Neo4j, Kafka and Kubernetes. Session 7
measured the actual constraint: `engine.add()` recomputes the full belief state on every observation
and is quadratic — 27 ms at 100 evidence pairs, 1121 ms at 800. Incremental recompute buys more than
a cluster does.

---

## 3. Appendix D — what changed in the claim matrix

**Eight claims are now settled by a test or a measurement**, where previously none were. The largest
single change is at the bottom of your original table:

> *Architecture is safer than a baseline — evidence now: **normative proposal***

That row now reads: misreading a threat response as a hidden desire, **0.0%** [0.0, 0.0] with the
guard against **42.9%** and **75.1%** for two guard-free baselines, *n* = 400 per generative process
across five processes and two misspecification levels — with a stated falsification signal and a
named file.

**Five claims are withdrawn**, and it is worth being explicit that four of the five were never yours:
the *t*(39) = 4.23 calibration result, the 72% and 41% baselines, and the "100% appropriate revision"
figure all originated in the generated benchmark suite. The fifth is yours and goes for an honest
reason: *the URG improves reflective reasoning* is removed **as stated**, because Session 3 measured
the inference layer as statistically indistinguishable from a median split across all 20 conditions.
The URG's benefits are structural — traceability, provenance, contested-hypothesis retention — and
the rebuilt matrix claims exactly those and nothing more.

**Thirteen claims still await people**, unchanged from your original, because nothing in code can
settle them. Two moved to *partial*: Invariant X now checks output phrasing mechanically, which is
necessary but nowhere near sufficient for "questions reduce verdict-like framing"; and the guard
ablation is direct evidence that disagreement *between channels* is decisive for safety, which is a
narrow version of "sensor disagreement is informative".

---

## 4. The three sentences the evidence licenses

Every paper drawn from this work should be checkable against these:

1. Under simulation with known ground truth, conditioning the hidden-preference reading on the
   evidence needed to rule out a threat response reduces the rate of that misreading from 42.9–75.1%
   to 0.0%, at a cost of 19 points of sensitivity and 33 points of specificity when the required
   channel is absent.
2. The ten architectural invariants are decidable properties, and a compliant implementation exists
   with 312 passing tests, including 16 that prove each check can fail.
3. Nothing in this work establishes any effect on human reasoning, and no claim to that effect is
   made.

If a sentence in a draft cannot be traced to one of those three or to a row in Appendix D, it does
not belong in the paper.

---

## 5. Defect register

| ID | Status |
|---|---|
| **D-29** ambivalence computed from dispersion alone; 34% precision, 98.8% of monotonic drift misread as ambivalence | ✅ **Fixed this session** — 97.6% precision, 4 regression tests |
| D-28 `engine.add()` quadratic | Open — Session 12 |
| D-23 residual — nominal coverage needs conformal calibration | Characterised; blocked on labelled outcomes |
| D-26 soft-assignment EM for offset estimation | Open — Session 12 |
| D-02, D-04, D-05, D-18 the Kimi paper | Superseded by the Session 6 venue decision; both papers written fresh |
| D-17 figure labels contain literal `\n` | Open — Session 12 |
| **D-30 (new)** positive lag-1 autocorrelation is computed and discarded; "your position moved steadily" is a candidate state | Proposal — research agenda |

---

## 6. Reproducing

```bash
unzip shadow_mirror_v1.0.zip && cd shadow_mirror_v1.0
pytest -q                          # 312 passed, 2 xfailed
python experiment_ambivalence.py   # the before/after in §1
python conformance_v10.py          # prototype 4/7 vs v1.0 7/7
```

---

*Session 09 — the ethics, governance and prohibited-use audit against GDPR and the EU AI Act as
currently in force — continues automatically.*
