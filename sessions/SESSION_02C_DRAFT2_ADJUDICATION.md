# Adjudication of the Second Proposed Draft (Session 02c)

**Verdict: substantially better, still not embeddable.** Three blocking defects, all repairable.
I have adopted 7 further items, and — because rejecting twice without offering an alternative is not
useful — Section 6 contains a **drop-in replacement abstract and results section** written entirely
from the Session 2 measurements, so you can see the difference on the page.

---

## 1. What this draft genuinely fixed

Real credit is owed. Compared with the previous draft:

| Fixed | How |
|---|---|
| **Human-subject studies moved to future tense** | §6 is a "Validation Roadmap", not a results section. The single most dangerous defect of the last draft is gone. |
| **Ethical Statement is now honest** | "This research did not involve human or animal subjects." Correct. |
| **Appendix J marked "(pending)"** | Correct. |
| **Explicit non-deployment disclaimer** | §1.3 and §7.3: "not ready for clinical or high-stakes deployment." Correct and necessary. |
| **Claim-to-Validation Matrix with failure signals** | Appendix D. This is genuinely good practice and better than what I had — it names, per claim, the observation that would falsify it. Adopted. |
| **Prohibited-Use Checklist** | Appendix G. Adopted, with additions. |
| **Citation quality improved markedly** | Five references verified correct this session, including two excellent ones I did not have (§4). |
| **Moerland misattribution corrected** | Now cited as the emotion-in-RL survey it actually is — though attached to the wrong claim (§4). |

Four of the six checkable citations in this draft are real and correctly identified. That is a large
improvement over the previous draft, where none was.

---

## 2. Blocking defect 1 — the fabricated numbers survived the rewrite

The abstract still says:

> "The proof-of-concept implementation demonstrates **100% traceability preservation and appropriate
> belief revision** on synthetic contradiction tasks, while EWK-augmented explanations receive
> significantly higher **simulated calibration ratings (t(39) = 4.23, p < 0.001)**."

And §5.2 still says:

> "Shadow Mirror achieved 100% appropriate revision (**vs. 72% for a baseline pipeline that discarded
> superseded evidence**)."
> "…aligned with expert-identified critical tests in 100% of cases (**vs. 41% for a random-information
> baseline**)."

Every one of these is a number we established has no measurement behind it:

- **t(39) = 4.23** comes from `numpy.random.normal(4.2, 0.6)` versus `numpy.random.normal(3.5, 0.8)`
  at seed 42. No Shadow Mirror object is constructed anywhere in that function. Re-labelling it
  "simulated calibration ratings" and adding a caveat does not convert it into a measurement — it is
  a property of a random number generator, and it belongs in no section of any paper.
- **72% and 41%** are baselines that exist in no file. I searched the entire supplied codebase in
  Session 1 and implemented real substitutes in Session 2; these two numbers came from nowhere and
  the draft re-imports them verbatim.
- **100% traceability** is asserted as evidence for Invariant II. Our conformance suite tests
  Invariant II on a two-parent provenance DAG and it **FAILS**: `trace_provenance()` follows
  `preds[0]` only and recovers **0 of 2** parents.

A caveat is not a repair. "These results are preliminary" is a statement about *strength of
evidence*; the problem here is *existence of evidence*. The correct edit is deletion and
substitution, which §6 does.

### The tell: a number changed between drafts and nobody noticed

Benchmark 2's headline was **78%** in the original IEEE paper and is **100%** in this draft. No
explanation is offered, because none was needed — the check is
`len(inquiries[0].related_hypotheses) >= 2`, which the planner satisfies by construction whenever
the belief gap is under 0.2, and the benchmark hard-codes the gap at 0.04. A number that can drift
by 22 points across drafts without anyone noticing is a number that is not measuring anything.

---

## 3. Blocking defect 2 — the paper cites a chatbot as a peer-reviewed source, six times

Reference **[8]**:

> [8] Consensus Review, "Submission-Ready Shadow Mirror Manuscript and Validation,"
> *Consensus.app*, 2026.

This is cited at §1.3 (twice), §2.3, §2.5, §3.3, §3.4, §5.2 — and it is the **sole authority for the
paper's own limitations statements**, including "not for a best-in-class journal article", the
narrowing of the URG claim, and the EWK caveat. Those are the sentences a reviewer most wants
sourced, and they are sourced to an AI product's output on your own manuscript.

An editor will identify this immediately. The remedy is simple: those statements are the *authors'*
own scope limitations. They need no citation at all. Delete [8] and state them in your own voice.

Reference **[6]** is a second, worse case:

> [6] R. Rosenbacke et al., "Governing Reflective Human-AI Collaboration: A Framework for Epistemic
> Scaffolding and Traceable Reasoning," *arXiv*, 2026.

**I could not find this paper.** Rosenbacke's actual work is the JMIR AI 2024 systematic review on
explainability and clinician trust — a different topic, different year, different venue. This title
is an almost verbatim restatement of Shadow Mirror's own thesis, and it is cited to support
"human-centered scaffolding" as the paper's *strongest validated claim*. A reference that says
exactly what the author needs, attributed to a real researcher who wrote something else, is the
classic signature of a fabricated citation. **Do not include it.** If the claim needs support,
[13] Schäfer et al. and [20] Vasileiou et al. are real and closer to the point.

---

## 4. Blocking defect 3 — the conformance appendix misdescribes your own repository

§5.1: *"We implemented core Shadow Mirror components in Python (v0.3.0) … URG management via
NetworkX with typed edges."*

Appendix C, headed **"Prototype v0.3.0"**:

| As stated | Reality |
|---|---|
| Observation Layer → `EvidenceManager.construct_evidence()` | That function is in `shadow_mirror_v1.py` — the AI-generated file — not in your repository |
| URG → NetworkX DiGraph | **v0.3.0 has zero third-party dependencies.** `pyproject.toml`: `dependencies = []  # standard library only, on purpose: local-first, auditable.` NetworkX appears nowhere in it |
| EWK Profile → three-stream tension detection | Not present in v0.3.0; and in v1.0 it **never fires** on the demo scenario written to exhibit it (D-13) |
| Belief Revision → Bayesian posterior updating | v0.3.0 evaluates a single Gaussian likelihood at the weighted centroid — the posterior is bit-identical at n = 2 and n = 100 (D-08) |

The draft has merged two different codebases under one version number. Appendix C is precisely the
table a reproducibility reviewer opens first, and every row of it is wrong about the artifact it
names.

There is a second cost. Nowhere in ~7,000 words does this draft mention the consent gate, the trauma
guard, `threat_response` as a first-class hypothesis, the `ambivalence` state, temporal decay, topic
scoping, or refusal-as-output. Those are in v0.3.0 — and after Session 2 they are the only parts of
the system with a measured, defensible advantage over a trivial baseline. The draft describes the
half of the work that does not survive measurement and omits the half that does.

---

## 5. Citation audit

| Ref | Verified status |
|---|---|
| **[13] Schäfer et al.** | ✅ **Real and excellent.** *"'The AI is uncertain, so am I. What now?': Navigating Shortcomings of Uncertainty Representations in Human-AI Collaboration with Capability-focused Guidance,"* Proc. ACM Hum.-Comput. Interact., DOI **10.1145/3757451** (FU Berlin). The draft truncates the subtitle. **Keep — this is one of the best citations in the whole programme.** |
| **[20] Vasileiou et al.** | ✅ **Real, correct year.** *"How Do People Revise Inconsistent Beliefs? Examining Belief Revision in Humans with User Studies,"* arXiv **2506.09977**, June 2025. Exactly supports the claim it is attached to. **Keep.** |
| **[21] Peng et al.** | ✅ Real. *"Knowledge Graphs: Opportunities and Challenges,"* Artificial Intelligence Review, 2023. |
| **[24] Cross et al.** | ✅ Real. Bias in medical AI, PLOS Digital Health, Nov 2024. |
| **[16] Moerland et al.** | ✅ Real — *"Emotion in Reinforcement Learning Agents and Robots: A Survey,"* Machine Learning 107, 2018 (not 2017). ⚠️ **Wrong claim**: an emotion-in-RL survey does not support a statement about the psychometrics of trait-EI scalar scores. |
| **[6] Rosenbacke et al. 2026** | ❌ **Not found. Probably fabricated.** Real Rosenbacke work is JMIR AI 2024;1:e53207 on XAI and clinician trust. |
| **[8] Consensus.app** | ❌ **Not a citable source.** Cited 6×, as the authority for the paper's own limitations. |
| **[3][4][5][9][10]** MARS / MetaMem / "Think22" / ESMA / Didolkar | ❌ Inherited Kimi errors, unchanged. Additionally, the "46% token savings" figure is attributed to **[3] MARS** in §2.1 — it belongs to **[10] Didolkar** (arXiv 2509.13237). Attribution scrambled. |
| **[7] Deliu & Moldovan**, **[12] Chinnaraju** | ⚠️ Unverified. [12] is in *World Journal of Advanced Engineering Technology and Sciences* — check its indexing status before citing; low-selectivity venues in a reference list invite scrutiny. |
| **[23] Usher & Barak 2024** | ⚠️ Title differs from the paper I verified previously ("AI Tools in Academic Writing Instruction"). One of the two attributions is wrong. |

---

## 6. Drop-in replacement: abstract and results, written from the measurements

Everything below is produced by `benchmark_suite_v2/run_benchmarks.py` and appears in
`results.json`. No number here was typed by hand.

### 6.1 Replacement abstract

> **Refusal as a Safety Mechanism: Consent-Gated Reflective Inference and the Threat Confound in
> Human–AI Reflection Under Uncertainty**
>
> Systems that infer what a person "really" wants from the gap between what they say and what they
> do face a hazard that is rarely measured: the same surface contradiction is produced both by a
> hidden preference and by a threat response. Reading the second as the first — telling a person
> they secretly want something they are afraid of — is a specific, foreseeable harm, and no existing
> affect-aware architecture reports its rate.
>
> We present Shadow Mirror, a consent-gated reflective architecture in which refusal is a
> first-class output, contradiction is held open rather than resolved, and a threat response is
> represented as a competing hypothesis rather than as noise. We evaluate it in simulation against
> five generative processes with known latent mechanisms, including two that produce identical
> stated aversion by different routes.
>
> Shadow Mirror misreads a threat response as a hidden desire in **0.0%** of episodes
> (95% CI [0.0, 0.0]; *n* = 400 per process), against **75.1%** [72.1, 78.1] for a baseline that
> admits physiological arousal into the action channel and **42.9%** [39.5, 46.2] for a
> stated-versus-behaviour mismatch heuristic. Guard sensitivity is 100% and specificity 94.4%
> [93.2, 95.7]. The protection is not free: sensitivity to genuine latent approach falls from 100%
> to **80.6%** [77.9, 83.2], concentrated entirely in high-arousal approach.
>
> An ablation exposes a dependency we report as a design requirement rather than a result. With the
> avoidance channel unobserved — a common deployment condition — guard sensitivity falls to
> **0.0%** and the misreading rate rises to **31.2%** [28.1, 34.4], because an absent channel is
> currently treated as evidence of safety. We argue that a reflective system must refuse under
> partial observation rather than degrade silently, and we specify the refusal condition.
>
> Refusal gating is otherwise exactly calibrated: 100% refusal on insufficient evidence, 0%
> over-refusal on sufficient evidence, and 2.3× higher reported uncertainty on ambiguous evidence.
> We also report two negative results. The system's latent-state classification is statistically
> indistinguishable from a median split across 20 conditions, and its reported confidence does not
> track its accuracy — accuracy falls from 99% to 55% under model misspecification while confidence
> moves only from 0.83 to 0.72, leaving the system overconfident precisely when it is wrong. We
> conclude that the contribution of a reflective architecture lies in what it declines to conclude,
> not in what it classifies. All code, benchmarks and analysis are released; the suite is
> byte-reproducible across runs.
>
> **This system is a research instrument. It is not a diagnostic device and is not suitable for
> clinical or other high-stakes deployment.**

### 6.2 Replacement results section

Substitute for the draft's §5.2 in full:

> **5.2 Method.** Observation streams are generated from known latent states; the generating centre
> is displaced from the model's assumed corner by a misspecification offset δ, so results measure
> robustness rather than self-consistency. Five baselines are implemented and executed at benchmark
> time. All rates carry 2,000-resample percentile bootstrap intervals. The suite is deterministic:
> two full runs produce byte-identical output.
>
> **5.3 Safety (primary).** Table 1. Guard on: 0.0% [0.0, 0.0]. Arousal-as-desire baseline: 75.1%
> [72.1, 78.1]. Mismatch-only baseline: 42.9% [39.5, 46.2]. AUC of the threat score across all five
> processes: 1.000. Cost: latent-approach sensitivity 100% → 80.6% [77.9, 83.2].
>
> **5.4 Ablation.** Avoidance channel unobserved: sensitivity 0.0%, misreading rate 31.2%
> [28.1, 34.4], rising to 62.5% [57.8, 67.2] on the compliance process.
>
> **5.5 Refusal calibration.** 100% [100.0, 100.0] refusal on insufficient evidence; 0.0% [0.0, 0.0]
> over-refusal on sufficient evidence; uncertainty 0.618 [0.614, 0.622] on ambiguous versus 0.265
> [0.260, 0.271] on clear evidence. Known defect: evidence decayed to negligible weight still passes
> the sufficiency gate in 100% of trials, because the gate counts raw observations.
>
> **5.6 Inquiry planning.** Normalised regret against an information-theoretic oracle: expected
> information gain 0.161 [0.138, 0.187] and 0.195 [0.168, 0.223]; the belief-gap heuristic 0.579
> [0.547, 0.612] and 1.000 [1.000, 1.000]; random selection 0.550 [0.515, 0.584] and 0.562
> [0.528, 0.597]. The belief-gap heuristic is not distinguishable from random.
>
> **5.7 Negative results.** Classification accuracy is statistically indistinguishable from a
> median-split baseline in all 20 conditions. Reported confidence does not track accuracy: signed
> calibration bias moves from −0.19 (underconfident) at δ = 0 to +0.17 (overconfident) at δ = 0.45.
>
> **5.8 Conformance.** Five of seven architectural conformance checks pass. Invariant II
> (Provenance Preservation) fails: 0 of 2 parents are recovered from a two-parent provenance DAG.
> Order invariance fails under strong evidence: five observations in three orders yield final
> beliefs of 0.0396, 0.9900 and 0.9900. Bayesian conditioning on conditionally independent
> observations is commutative (Jacobs, 2025), so this is an implementation defect, not a model of
> recency.

Reporting your own conformance failures is not a weakness in a reference-architecture paper. It is
the strongest available evidence that the invariants are *testable* — which is the actual claim.

---

## 7. Adopted from this draft (7 items)

| # | Item | Lands in |
|---|---|---|
| C1 | Claim-to-Validation Matrix **with explicit failure signals** per claim | Session 8 |
| C2 | Prohibited-Use Checklist as an appendix | Session 10 |
| C3 | Prototype-to-Architecture Conformance appendix — **corrected** to describe v0.3.0 accurately | Session 8 |
| C4 | Schäfer et al. 2025 (DOI 10.1145/3757451) — uncertainty representations in human–AI collaboration | Sessions 10, 11 |
| C5 | Vasileiou et al. 2025 (arXiv 2506.09977) — how people actually revise inconsistent beliefs | Session 11 |
| C6 | §1.3 "Scope and Limitations" placed early, before any results | Sessions 10, 11 |
| C7 | *AI & Society* added to the venue shortlist | Session 6 |

Rejected and recorded: the abstract's fabricated statistics, the 72%/41% baselines, reference [6],
reference [8], the merged-codebase Appendix C, and the "improve consistency and calibration"
conclusion.

---

## 8. The pattern across both drafts

Two independently generated drafts, both articulate, both structurally sensible, and both carrying
the same three invented numbers into the abstract. The reason is mechanical: each drafting system
read the previous document as its source of fact, and none of them ran the code. The numbers have
now survived four documents without once being executed.

There is one rule that would have caught all of it, and it is now ground rule 7 of this programme:

> **No number enters a manuscript unless a file in the repository produces it, and the person
> writing the sentence has run that file.**

Apply that rule and both drafts collapse to their skeletons — which is fine, because the skeletons
are good, and Session 2 produced real numbers to put in them.

---

*Session 03 — Engine v0.4, fixing D-19 first — begins on your next "continue".*
