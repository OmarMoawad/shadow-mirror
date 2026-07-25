# Shadow Mirror — Session 13: Adversarial Self-Review

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverables:** this review, `experiment_adversarial.py` + `experiment_adversarial.json`,
patched drafts of P1 and P2.

I reviewed both papers as an unsympathetic Reviewer 2 would: assuming the results are wrong until
forced otherwise, and looking for the sentence that overreaches. Fourteen attacks. **Five conceded,
four answered with new evidence, five fixed in the text.** The two that required new experiments
changed the paper materially, and one of them found a result that weakens the headline.

---

## The two attacks that required running something

### A-1 — "Your simulator is your theory." **Answered with a sweep. Partly conceded.**

*The attack.* You defined `threat_compliance` to differ from `latent_approach` on arousal and
avoidance. Your guard keys on arousal and avoidance. Your AUC is 1.000. You have not measured a harm
rate; you have measured that a classifier separates classes you separated by construction.

*The answer.* Correct enough that prose would be evasive. I swept the separation between the two
processes on the confound channels from full to zero, *n* = 300 per process per level:

| Separation | AUC | Shadow Mirror | Four-channel classifier | Mismatch-only |
|---|---|---|---|---|
| 1.00 | 1.000 | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 94.3% |
| 0.75 | 1.000 | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 95.3% |
| 0.50 | 1.000 | 2.3% [0.7, 4.0] | 0.0% [0.0, 0.0] | 96.7% |
| 0.25 | 0.988 | 29.7% [24.7, 35.0] | 5.0% [2.7, 7.7] | 97.3% |
| 0.00 | 0.491 | 76.7% [71.7, 81.3] | 82.0% [77.7, 86.3] | 96.3% |

**Verdict: partly conceded, and the paper is stronger for it.** The result is not a knife-edge — it
survives to roughly half the original separation. But it is entirely contingent on the confound
channels carrying signal, and at zero separation every method fails, as it must. Added as §6.5.

### A-2 — "Your baselines are straw men." **Conceded. New baseline added, and it beats us.**

*The attack.* Mismatch-only ignores channels that are available. Arousal-as-desire is a mistake, not
a method. Neither is what a competent engineer would build.

*The answer.* They partly were straw men. I built the baseline the objection demands — a threshold
classifier over the same four channels, fitted on a held-out labelled split — and it is in the table
above.

**It matches us at high separation and beats us at separation 0.25: 5.0% against our 29.7%.**

**Verdict: conceded, reported, and reframed.** The reframing is not a dodge, and it is the most
important sentence in the session: *the classifier was given ground-truth labels for "was this a
threat response", and those labels do not exist in deployment.* Nobody can tell a running system
which mechanism produced a person's behaviour — that is the entire difficulty. So the supervised
baseline is an **upper bound on what any labelled method could achieve**, not an available
alternative, and the gap at separation 0.25 is a quantified cost of having no supervision.

A reviewer who finds that unconvincing has a real objection, and I would rather they raise it against
a number we published than discover it themselves.

---

## The other twelve

| # | Attack | Verdict |
|---|---|---|
| A-3 | **"0.0% with CI [0.0, 0.0] is not an interval."** Bootstrapping an all-zero sample yields a degenerate interval that overstates precision. | **Conceded, fixed.** Now reported as *0 of 800 episodes; 95% upper bound 0.37% by the rule of three*. That number, not 0.0%, is what a deployment decision should use. |
| A-4 | **"'Never been measured' is an argument from absence."** | **Conceded, fixed.** Softened to "so far as we have been able to establish, has not previously been quantified". |
| A-5 | **"You borrow clinical authority."** "Fawn", "compliance" and "threat response" carry clinical weight the paper has not earned. | **Conceded, fixed.** Added a limitation stating that the terminology names a pattern our generative process encodes, that no clinical construct is claimed, and a `[CITATION NEEDED — trauma-response typology]` marker. Do not remove that marker without a real citation. |
| A-6 | **"You are not lawyers."** §7 is amateur legal analysis presented with confidence. | **Conceded, fixed.** Explicit limitation: it is a reading, not reviewed by counsel, not advice. §7 already framed the safety exception as an argument rather than a conclusion. |
| A-7 | **"The guard is two thresholds. Where is the generalisation?"** | **Conceded.** It is two thresholds. The contribution is the *decision to refuse* and the measurement of what refusing buys, not the sophistication of the rule. The paper says so; A-1's sweep now bounds where it holds. |
| A-8 | **"Executable invariants is just having tests."** | **Rebutted.** Tests assert behaviour; these are a decision procedure for named architectural properties, shipped with the architecture, with a negative test per property. The distinction is that a third party can run them against a *different* implementation — see A-9. |
| A-9 | **"N = 1 implementation. Your invariants may be trivially satisfiable by your own API."** | **Rebutted with evidence; new §3.5.** The same procedure run unmodified against an independently written prototype passes 4 checks and **fails 3**. It separates two implementations of one architecture, which rules out vacuity. Limitation retained: two is not many, and none was written by a third party. |
| A-10 | **"Invariant X is a regex. Authority is not a matter of pronouns."** | **Conceded, fixed.** New limitation: the check is a syntactic proxy, it produced a documented false positive on first contact with real output, and it will produce false negatives. It raises the floor; it does not measure the property. |
| A-11 | **"200 seeds is not property-based testing; coverage is unmeasured."** | **Conceded, fixed.** Limitation now states what varies across seeds and that nothing measures whether that exercises the state space in any principled sense. |
| A-12 | **"You say the architecture buys no accuracy. Why should TiiS care?"** | **Rebutted, text strengthened.** Accuracy was never the safety-relevant quantity: the companion harm result depends on the structural commitments — representing a competing hypothesis rather than filtering, and distinguishing absent from zero. Structure is what carries it. Added to §8. |
| A-13 | **"Your uncertainty is worse where the model is wrong. That is a regression."** | **Rebutted.** Already reported in both papers with the numbers (ECE 0.171 → 0.044 where applicable, 0.151 → 0.221 where not). Reporting a regression you found yourself is not a weakness to hide. |
| A-14 | **"Related work is thin — 12–14 references."** | **Conceded, outstanding.** Both papers carry a marked expansion note. This is real work and it is not done. |

---

## What changed in the drafts

**P2** — abstract rewritten for the rule-of-three bound and the supervised comparison; novelty claim
softened; **new §6.5** carrying the separation sweep and the four-channel baseline; four limitations
added (point-estimate-of-zero, borrowed clinical vocabulary, not-lawyers, simulation caveat extended).
4,325 → 4,950 words.

**P1** — **new §3.5** on whether the checks discriminate between implementations; §8 answers the
"so what" objection directly; three limitations rewritten (two-implementations, Invariant X as
syntactic proxy, unmeasured harness coverage). 3,987 → 4,360 words.

---

## Rebuttal hardening — for when reviews arrive

**If a reviewer says the simulation is circular:** point to §6.5. The sweep is already there, it
already shows the result degrading, and it already shows every method failing at zero separation. The
concession is in the paper. What you should *not* do is defend the 0.0% as a general fact; defend it
as a statement about identifiability given informative channels.

**If a reviewer says the supervised baseline beats you:** agree immediately — the paper says so — and
move to the labels. The classifier needs ground truth for "was this a threat response". Ask the
reviewer where that comes from in deployment. If they have an answer, it is a genuinely important one
and worth a follow-up paper.

**If a reviewer says "this needs human subjects":** agree. Both papers say so in the abstract, the
limitations, and the ethics statement, with `[NO DATA YET]` markers. The claim is about a system's
behaviour, not about people. Do not be tempted to gesture at plausibility.

**If a reviewer challenges the regulatory reading:** concede the framing (it is a reading, not
advice) and hold the substance. The chain is textual — Art. 3(34) omits the unique-identification
requirement that GDPR Art. 4(14) contains; Art. 3(39) is defined over biometric data; Art. 5(1)(f) is
in force. If they disagree about the safety exception, that is exactly the discussion the section
exists to provoke.

**If a reviewer says the invariants are trivial:** §3.5. Four pass, three fail, on an independently
written implementation.

**If a reviewer asks for a scalability claim:** do not make one. The papers report a quadratic write
path fixed to linear, a read path still linear per consultation, and thousands of nodes rather than
millions. Say the architecture makes no validated scalability claim, because it doesn't.

**The general rule.** Every number in both papers traces to a named script, and the suite is
byte-reproducible. If a reviewer disputes a figure, the reply is a command they can run — which is a
much stronger position than most rebuttals start from.

---

## Honest assessment of where these papers stand

**P2 is the stronger submission.** It has a measured harm rate, an adversarial robustness check that
partly undermines its own headline, a design commitment that produces the result, an unresolved
regulatory tension, and no claims about people. That is a coherent AIES/FAccT paper.

**P1 is solid but narrower.** Its contribution — a decision procedure for architectural invariants
that discriminates between implementations — is real, and the negative result is honestly placed. Its
weakness is that it is one architecture checked by its own author, and no amount of writing fixes
that. It needs a third party to run the suite.

**Both need the related-work expansion**, and both need your affiliation.

**The single largest risk to either paper is no longer a defect.** It is that the reference list is
too thin for the venue, and that nobody outside this project has run the code.

---

## Programme status

Sessions 1–13 complete. Defect register: **31 identified, 24 resolved, 2 open with named blockers,
5 superseded.** `shadow_mirror` v1.1.0, 324 tests passing, 2 declared gaps. Both papers drafted,
figured, and adversarially reviewed.

**Sessions 14 and 15 cannot proceed without you.** They are blocked on Q2, and I will not invent an
affiliation or name an ethics committee.

---

*Programme paused at the decision point. See the accompanying summary.*
