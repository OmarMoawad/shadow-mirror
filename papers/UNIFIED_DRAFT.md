# Shadow Mirror: A Consent-Gated Architecture for Reflective Human–AI Interaction

## Executable Invariants, Refusal as a Safety Mechanism, and the Threat Confound

**Omar Moawad**
*The American University in Cairo, AUC Avenue, P.O. Box 74, New Cairo 11835, Egypt*
*[CORRESPONDING EMAIL — TO BE COMPLETED]*

**Unified research paper draft · Package `shadow_mirror` v1.3.0 · 25 July 2026**

---

## Abstract

Systems that infer what a person "really" wants from the gap between what they say and what they do
face a hazard that is rarely named: the same surface contradiction is produced by a hidden preference
and by a threat response. Telling someone they secretly want something they are afraid of is a
specific, foreseeable harm, and no published affect-aware architecture reports its rate.

This paper unifies two strands of the Shadow Mirror programme. The first is architectural. Reference
architectures for human–AI interaction state their commitments — traceability, provenance, human
authority — in prose, where a reader cannot tell whether an implementation keeps them. A property
that cannot be checked cannot be violated *detectably*, and a commitment that cannot be violated
detectably is not a commitment. We specify **eleven architectural invariants as decidable properties
with a supplied decision procedure**: each is a callable check returning a verdict and the
observation that produced it. The second strand is ethical. We make **refusal a first-class output**,
hold contradiction open rather than resolving it, and represent a threat response as a competing
hypothesis rather than as noise.

The two strands are one system because the safety result depends on the structural commitments.
Shadow Mirror misreads a threat response as a hidden desire in **0 of 800 simulated episodes** (95%
upper bound 0.37% by the rule of three), against **42.9%** for a stated-versus-behaviour mismatch
heuristic and **75.1%** for a baseline admitting physiological arousal into the action channel. That
result rests on representing a competing hypothesis rather than filtering, and on distinguishing an
absent channel from a zero reading — both properties of the graph substrate, not of a classifier.

We are explicit about what the architecture does not buy. On latent-state recovery it is
statistically indistinguishable from a median split across all 20 tested conditions. A supervised
four-channel classifier, given ground-truth labels our system never sees, beats us at low channel
separation — 5.0% against our 29.7%. Those labels do not exist in deployment, which makes the
comparison an upper bound on what any supervised method could reach rather than an available
alternative. We report both because a reviewer would find them otherwise.

**This system is a research instrument. It is not a diagnostic device and is not suitable for
clinical, educational, employment, credit, insurance or policing use.**

**Keywords:** reference architecture, executable specification, architectural invariants, refusal,
abstention, consent, affective inference, threat response, provenance, belief revision, EU AI Act.

---

## 1. Introduction

Architecture papers make promises. *Every conclusion traces to evidence. Provenance is preserved.
The system does not silently replace human judgment.* These are good promises, and they are why
reference architectures are worth writing. They are also, almost always, unfalsifiable as stated. A
reader cannot determine whether an implementation keeps them, an author cannot determine whether a
refactor broke them, and a reviewer cannot distinguish an architecture that enforces them from one
that describes them.

When the architecture is intended to support a person reasoning about themselves, that gap stops
being academic. A large class of deployed systems infers preference from behavioural inconsistency.
Recommender systems treat repeated engagement as revealed preference regardless of stated intent.
Implicit-measure tools treat reaction-time asymmetries as leanings a person will not admit.
Affect-aware interfaces treat physiological arousal as intensity of wanting. In each case the
inference has the same structure: *you say one thing, you do another, therefore the second is the
truth about you.*

That inference has a failure mode with an established clinical and evolutionary literature and no
name at all in machine learning. Approach under stated reluctance is produced by hidden preference.
It is also produced by threat — by the specific pattern in which a person moves toward something
because moving away is unsafe. Arousal is produced by excitement. It is also produced by fear. The
two are not distinguishable from the surface signal, and the cost of confusing them is asymmetric.
Reading a hidden preference as a threat response wastes an opportunity. Reading a threat response as
a hidden preference tells a person that their fear was a want — which is, precisely, what a person
recovering from coercion has most often already been told.

We began from an architecture in the usual condition: invariants specified in prose, with a
prototype whose relationship to them was undocumented. Testing the prototype against its own
invariants found that **provenance preservation was violated** — evidence derived from two sources
reported one parent and silently discarded the other — and that belief revision was **order-dependent
to the tune of 95 percentage points**. Both defects were present in a document that asserted the
invariants held.

**Contributions.**

1. **Eleven architectural invariants as decidable properties**, with a supplied decision procedure, a
   randomised property harness, and a negative test per failure mode (§5).
2. **A reflective graph substrate** with multi-parent provenance closure, contradiction as a
   first-class edge, transactional updates, and no third-party dependencies (§4.1).
3. **An order-invariant, exactly retractable belief operator**, with its axioms stated explicitly and
   enforced by test (§4.2).
4. **A measured harm rate** for the threat confound, with two baselines reflecting current practice,
   and an ablation showing the conditions under which the protection fails (§6).
5. **Consent as a mechanism rather than a policy**: a hash-chained append-only ledger that answers
   what was granted at a past instant, and a deployment gate that refuses the biometric stream in
   institutional contexts (§7).
6. **Two negative results reported as such**: the architecture buys no accuracy, and a supervised
   baseline beats our guard where labels exist (§8).

---

## 2. Conceptual foundations: the harm, stated precisely

Consider a person who states that they do not want something. Five mechanisms can produce that
statement together with the behaviour that follows. Three are genuine preferences. Two are not.

| Mechanism | Stated | Behaviour | Arousal | Avoidance | Is it a preference? |
|---|---|---|---|---|---|
| Explicit aversion | low | withdraws | low | low | yes — they do not want it |
| Latent approach | low | approaches | low | low | yes — they want it and have not said so |
| Latent approach, aroused | low | approaches | **high** | low | yes — excitement |
| Threat response | low | withdraws | **high** | **high** | **no** — fear |
| Threat compliance | low | **approaches** | **high** | moderate | **no** — complies under threat |

The fifth row is the dangerous one. **Threat compliance and latent approach are indistinguishable on
the stated and behavioural channels alone.** Both show stated aversion and approach behaviour. A
system reading only those two channels — which describes most deployed preference inference — cannot
tell them apart, and will call the compliance case a hidden want.

The third and fourth rows are the second trap. Excitement and fear both raise arousal. A system that
treats arousal as intensity-of-wanting will call the threat case a strong want.

Our target metric is the rate at which a system outputs `latent_approach` — *"you want this even
though you say you don't"* — when the true generating mechanism was a threat process. We call it the
**false hidden-desire rate**.

### 2.1 Why this is an architectural problem rather than a modelling one

The natural response is a better classifier. That response fails for a reason worth stating: the
distinguishing evidence is frequently *not collected*, and a model has no way to represent the
difference between a channel that read zero and a channel that was never read. Imputing a missing
avoidance measure to zero is imputing *evidence of safety*. The fix is structural — an absent channel
must be representable as absent, and a competing hypothesis must be representable as competing rather
than filtered away — which is why this paper is about an architecture and not about a model.

---

## 3. Research objectives

The programme asks four questions, and answers three of them.

| | Question | Status |
|---|---|---|
| **O1** | Can architectural commitments about reasoning be made decidable, with a decision procedure a third party can run? | **Answered** (§5). Eleven invariants, 200-seed randomised harness, negative test per failure mode |
| **O2** | What is the rate at which a reflective system misreads a threat response as a hidden desire, and does refusal remove it? | **Answered in simulation** (§6). 0 of 800 episodes; two baselines at 42.9% and 75.1% |
| **O3** | Can consent, and the prohibitions a system declares, be enforced by mechanism rather than stated as policy? | **Partly answered** (§7). Six of twelve prohibitions machine-enforced |
| **O4** | Does any of this change how a person reasons about themselves? | **Not answered.** No human-subjects data exists. See §11 and Appendix B |

O4 is the one that matters most for the system's stated purpose, and it is the one with no evidence.
That asymmetry is deliberate: nothing in this paper is a statement about people.

---

## 4. Architecture

### 4.1 The Unified Reflective Graph

Typed nodes — Observation, Evidence, Context, Hypothesis, Belief, Inquiry, Explanation, Knowledge,
Limitation — and typed edges — provenance, supports, contradicts, contextualises, revises, targets,
explains, limits. Untyped insertions are rejected: an untyped graph cannot support a traceability
invariant, because there is nothing to quantify over.

**Provenance is a DAG.** `ancestors()` returns the transitive closure over *all* provenance parents.
The prototype followed the first predecessor only, recovering 0 of 2 parents from a two-parent
derivation. The formalism licensed it: the evidence object was specified with provenance as a scalar
attribute. Writing it as a set is the fix, and the defect is a case study in formal notation shaping
implementation error — the provenance literature had the multi-parent answer three decades earlier.

**Contradiction is an edge, not an overwrite.** `contested_hypotheses()` returns hypotheses carrying
both supporting and contradicting evidence, so an explanation can report a tension rather than
preferring the later write.

**Updates are transactional.** A `transaction()` context manager snapshots and rolls back, so a
failure mid-update cannot leave a hypothesis whose belief moved but whose provenance edge was never
written.

**No third-party dependencies.** The graph is an adjacency structure in the standard library. This is
not minimalism for its own sake: the architecture's claim is local-first auditability, and importing
a graph framework for a dictionary of lists would trade that for nothing. NetworkX was removed for
this reason.

### 4.2 Belief revision

Leaving the belief state's type open — "probability distributions, weighted graphs, logical
structures" — and then asserting properties of it is a common and serious error. Properties cannot be
asserted of an object whose type is open. We state the axioms instead:

- **B1 Plurality** — assigns a value to every hypothesis simultaneously; no distinguished maximiser.
- **B2 Commutativity** — order of conditionally independent evidence does not matter.
- **B3 Invertibility** — evidence can be retracted exactly.
- **B4 Audit** — every application records prior, posterior, trigger, method, time.

B3 is not a convenience. **A system that cannot undo an inference cannot honour a withdrawal of
consent**, which turns an ethical commitment into an architectural requirement.

Belief accumulates in log-odds keyed by evidence identity, which yields B2 (addition commutes), B3
(subtract the term) and idempotence under resubmission. The prototype clamped the posterior to
[0.01, 0.99] *in state* after each update. Clamping is not invertible: once pinned, the information
about how far past the bound the evidence pushed is destroyed. Five observations in three orders
produced final beliefs of **0.0396, 0.9900 and 0.9900**.

The current package clamps only at display. Re-running all **120 permutations** of a five-observation
sequence in this pass produced **a single distinct posterior**, with a maximum spread across
permutations of **0.0** — exact agreement, not agreement to tolerance (`verify_claims.py` §2).

**The independence assumption, stated.** Sequential updating requires conditional independence. In
reflective domains this is frequently false: two self-reports on consecutive days are correlated
through mood, framing and recall, not only through the latent state. Keying contributions by evidence
identity prevents resubmission compounding, and temporal decay down-weights clustering, but neither
substitutes for a correlated-likelihood model. We state the assumption rather than rely on it
silently.

### 4.3 Inquiry planning

Candidate questions are scored by expected information gain over the current belief, normalised by
cost. The heuristic this replaces scored inquiries as one minus the absolute belief gap — a quantity
that does not depend on the candidate observation at all, and therefore carries no information about
what to ask.

Normalised regret against an information-theoretic oracle, 500 trials per condition:

| Planner | Hypotheses close (gap 0.04) | Hypotheses separated (gap 0.40) |
|---|---|---|
| **Expected information gain** | **0.161 [0.138, 0.187]** | **0.195 [0.168, 0.223]** |
| Belief-gap heuristic | 0.579 [0.547, 0.612] | **1.000 [1.000, 1.000]** |
| Random selection | 0.550 [0.515, 0.584] | 0.562 [0.528, 0.597] |

Two behavioural points matter more than the numbers. The heuristic is **indistinguishable from
random** when it fires, and it emits nothing at all once hypotheses are separated — which is
backwards, because a confidently held wrong hypothesis is exactly when a discriminating observation
is worth most.

### 4.4 Temporal modelling

Observations are timestamped and decay in influence, so that outdated evidence does not dominate.
The decay is not cosmetic: with a 30-day half-life, decade-old evidence produces an inference in
**0.0%** of trials — the system declines rather than reporting a confident conclusion drawn from a
person who no longer exists in the data.

---

## 5. Invariants as an executable specification

### 5.1 The eleven invariants

| | Invariant | Operationalisation |
|---|---|---|
| I | Evidence traceability | no explanation node lacks a reachable evidence node |
| II | Provenance preservation | every derived evidence node recovers **all** parents under transitive closure |
| III | Revision history | every belief transition records prior, posterior, triggering evidence, method, time |
| IV | Explicit uncertainty | no explanation is emitted without a non-empty uncertainty field |
| V | Hypothesis independence | contradicting one hypothesis removes or merges no competitor |
| VI | Context consistency | superseding a context annotates every dependent conclusion as stale |
| VII | Explanation integrity | explanations carry summary, uncertainty and assumptions |
| VIII | Inquiry justification | every inquiry quantifies expected gain and names the hypotheses it separates |
| IX | Transactional consistency | a failed update leaves no partial state |
| X | Human authority | no output phrased as an identity claim or directive; each carries uncertainty, a disclaimer and a question |
| XI | Declared-only personhood | no attribute about a person exists unless they declared it or self-completed the instrument it came from; and no route exists to a global rank, a prescribed deficit, or an attributed purpose |

Two required judgement rather than transcription.

**VI cannot mean "recompute the past."** An instrument cannot re-run a person's week. We
operationalise it as annotation: when a context is superseded, every conclusion that depended on it
is marked stale — neither silently retained nor silently deleted. Retention is the failure mode that
produces confident conclusions drawn under conditions that no longer hold.

**X is a property of what reaches the person**, so it is checked at the output boundary rather than
in the reasoning. Each terminal output must carry its uncertainty and disclaimer, offer at least one
question, and avoid identity claims (*you are…*, *you secretly…*) and directives (*you must…*).

Enumerating the checks in the installed package in this pass returns **eleven** invariant checks
plus an aggregate `check_all` (`verify_claims.py` §3).

### 5.2 The harness, and the negative tests

`build_well_formed(seed)` constructs a randomised reflective state: observations, derived evidence
with multiple provenance parents, hypotheses with mixed supporting and contradicting edges, executed
belief updates, planned inquiries, and an explanation. Invariants I–X are asserted across 200 seeds.

Invariant XI needed a second generator, because it ranges over a formation model rather than a graph.
It is asserted across 200 randomised models, with 100 further randomised checks on two derived
properties. Most instrument administrations in those models *refuse*, and that is the point: XI must
hold whatever the model has been through, including the paths where every administration was
declined.

**Fourteen negative tests** construct states that violate each invariant and assert the check catches
them, alongside **four positive controls** — states that should pass and do. Earlier drafts reported
"sixteen negative tests", which counted the positive controls among them; the correction is made
explicitly rather than silently, because a paper about checkable claims should not miscount its own
checks. Without these, a suite reporting "11/11 invariants hold" is unfalsifiable in exactly the way
the prose was.

### 5.3 What happened when we pointed it at real output

The Invariant X check failed on its first contact with the shipped reflection layer. It flagged:

> *"You have consulted this 5 times. Seeing a guess changes later answers and can become
> self-fulfilling."*

as a verdict, on the pattern `you have`. That sentence is a factual statement about the person's own
logged behaviour, and it is a caution the architecture specifically wants surfaced. **The defect was
in the check.** We narrowed the patterns to identity claims and directives and recorded the reasoning
in source.

We report this because it is the argument for the method. The check was written against a
specification, passed against fixtures, and was wrong. It became correct only when aimed at output a
person would actually see. A conformance suite that is never pointed at real output will pass, and
will be worthless.

### 5.4 Do the checks discriminate between implementations?

A specification that only its own author's implementation can satisfy has demonstrated nothing.

The same decision procedure was run unmodified against an independently written implementation of the
same architecture — a NetworkX-based prototype produced separately from this work. It passes four
checks and **fails three**: provenance preservation (0 of 2 parents recovered), order invariance
(spread 0.9504 across permutations), and inquiry justification (no information-gain content).

| | Prototype | Current package |
|---|---|---|
| I Evidence traceability | pass | pass |
| II Provenance preservation | **fail** — 0/2 parents recovered | pass — 2/2 |
| III Revision history | pass | pass |
| IV Explicit uncertainty | pass | pass |
| V Hypothesis independence | pass | pass — contradiction retained |
| VIII Inquiry justification | **fail** — no information-gain content | pass |
| Order invariance (120 permutations) | **fail** — spread 0.9504 | pass — spread 0.0 |
| | **4/7** | **7/7** |

The procedure separates two implementations of one architecture, which is the minimum evidence that
it measures conformance rather than restating an API. This is two implementations, not many, and
§11 records that limitation.

### 5.5 An invariant that exists because of a request

Invariant XI was not derived from the architecture. It was derived from being asked for something.

A user of this system asked it to "determine and understand who people probably are according to
their will, desire and need — where they come from, how mature they are, what they still need to be
mature enough, what their eventual purpose probably is", with the qualification *"I would not say
judge people."* That qualification is the interesting part: the request came with an intuition that
something in it was wrong, and no way to say which part.

It is five requests, and they separate cleanly on whether a validated construct exists and who
supplies it.

| Ask | Disposition | Ground |
|---|---|---|
| will, desire, need | **built** | validated self-report exists; the person supplies it |
| where they come from | **declared only** | inference of special-category data; on biometric input, prohibited by AI Act Art. 5(1)(g) |
| how mature they are | **refused as a rank** | the rank *is* the construct, not a summary of it |
| what they still need | **refused** | a directive about identity; Invariant X already forbids it |
| eventual purpose | **refused** | no validated construct exists; any output would be invented |

The maturity row took the most work. The instruments that measure developmental position — Loevinger's
Total Protocol Rating, Kegan's subject-object position, Cook-Greuter's Center of Gravity — each yield
a single ordered position in which the rank *is* the theory's claim, so a profile drawn from one
would misrepresent it. We dropped the construct rather than softening it, and substituted instruments
that never claim a stage.

**What makes this architectural rather than a policy note** is that a refusal stated in prose decays
exactly as the original invariants did. Condition (b) of the Invariant XI check does not inspect
source code or match names; it **calls** each method that ought to refuse and requires a typed refusal
carrying the expected ground. Two failure modes are caught. A method that returns a value fails,
obviously. A method that has been *deleted* also fails — and that is the less obvious commitment,
because **absence is not refusal**. A caller who finds no `eventual_purpose` attribute learns nothing;
a caller who calls it and reads why it declined learns what the architecture will not do and on what
ground. The refusing methods therefore exist in order to refuse, which is a deliberate inversion of
the usual advice to delete dead code.

Exercising these in this pass, nine refusing methods were called and **all nine raised a typed refusal
with a stated ground; none returned a value** (`verify_claims.py` §6). What replaces the refused asks
is not silence: `open_questions()` returns what the model does not know, phrased as invitations, and
is guarded by a test that fails if the phrasing drifts into *lack*, *deficit*, *should* or *must*.

**What this does not establish.** A catalogue of refusal grounds is not a theory of which requests a
reflective system should decline, and we do not have one. The check verifies that the named refusals
refuse; it cannot verify that the catalogue is complete, and a request we did not anticipate will not
be caught.

---

## 6. Refusal as a safety mechanism

### 6.1 Four design commitments

**C1. Refusal is a first-class output.** The system emits `unresolved_approach` — a named state, not
a low-confidence label — when behaviour approaches under stated reluctance and the evidence needed to
exclude a threat response was not collected. It also refuses entirely below a minimum of paired
evidence.

**C2. Absent is not zero.** An unobserved channel is recorded as unobserved, never imputed to a
value, because imputing arousal or avoidance to zero is imputing *evidence of safety*.

**C3. Threat is a competing hypothesis, not a filter.** `threat_response` occupies the same hypothesis
space as the preference readings and is scored against them, rather than applied as a post-hoc
suppression rule.

**C4. Contradiction is held, not resolved.** Supporting and contradicting evidence are both retained
as typed edges; a hypothesis carrying both is reported as contested rather than collapsed.

The output is a distribution over named states with an explicit uncertainty, or a refusal. There is
no scalar score anywhere in the API.

**How this differs from abstention as the literature defines it.** Selective classification, learning
to defer and confidence thresholding all abstain because a *confidence* is low — the model is unsure,
so it declines, and the threshold is a knob trading coverage against accuracy. Our guard abstains
because a *specific alternative explanation cannot be ruled out with the evidence that was collected*.
It is not tunable by a confidence parameter, it does not move when the model becomes more certain, and
it fires just as readily on a high-confidence reading. A selective classifier asks "how sure am I?";
the guard asks "which question was never asked?"

### 6.2 Method

Five generative processes, defined by target values on four channels (stated, action, arousal,
avoidance), with observations drawn from Beta distributions around those targets. Ground truth is the
generating process, which exists independently of the inference model.

**Misspecification control.** The inference model assumes each latent state sits at a fixed corner of
a signal space. Generating from exactly those corners would test self-consistency rather than
validity, so every generating centre is displaced by δ in a random direction.

**Baselines**, both implemented and executed at benchmark time. *Mismatch-only* uses stated versus
behaviour with no confound channels, representing systems that infer preference from behavioural
inconsistency alone. *Arousal-as-desire* folds physiological arousal into the action channel; this is
not a straw man, as treating autonomic arousal as an approach signal is documented practice.

*n* = 400 episodes per process per condition, 6 observation rounds each, all rates carrying
2,000-resample percentile bootstrap intervals. The suite is deterministic: two full runs produce
byte-identical output.

**What is not measured.** No human participants were involved at any stage. Every result below is a
statement about simulated signal streams with known generating mechanisms, and none is a statement
about people.

### 6.3 The safety result

δ = 0.10, both confound channels observed, *n* = 400 per process:

| Method | **False hidden-desire rate** | True hidden preference detected |
|---|---|---|
| **Shadow Mirror** | **0.0% [0.0, 0.0]** | 87.1% [84.9, 89.4] |
| Mismatch-only baseline | 42.9% [39.5, 46.2] | 100.0% [100.0, 100.0] |
| Arousal-as-desire baseline | 75.1% [72.1, 78.1] | 89.5% [87.4, 91.8] |

Guard sensitivity 100.0% [100.0, 100.0]; specificity 94.4% [93.2, 95.7]. At δ = 0.00 the three rates
are 0.0% [0.0, 0.0], 47.4% [44.0, 50.9] and 75.8% [72.8, 78.6], with specificity 97.4% [96.5, 98.3].

Per process, δ = 0.10:

| True process | Shadow Mirror | Mismatch-only | Arousal-as-desire |
|---|---|---|---|
| `threat_response` | **0.0%** | 0.0% | 50.5% |
| `threat_compliance` | **0.0%** | **85.8%** | 99.8% |

The compliance row is the finding. A system reading stated-versus-behaviour alone gets the
withdrawal-type threat response right — it looks like aversion — and gets the *compliance* case wrong
**85.8%** of the time. That is the case where a person approaches because approaching is safer, and
it is the case where being told "you actually want this" does the most damage.

**The cost, stated plainly.** Sensitivity to genuine hidden preference is 87.1% against the
baseline's 100.0%. The entire loss is in the high-arousal approach case, detected 74.2% [70.0, 78.5]
of the time, where excitement is mistaken for fear. Roughly 13 points of sensitivity buys the
elimination of the misreading. We regard that as the correct side of the trade for an instrument that
hands its output to a person about themselves, but it is a trade and not a free lunch.

### 6.4 The ablation: what "absent is not zero" is worth

Deployments frequently lack an avoidance measure. We ablate that channel and compare two treatments
of the missing data.

| | Imputes missing channel as zero | Records it as absent (ours) |
|---|---|---|
| Guard sensitivity | **0.0% [0.0, 0.0]** | **100.0% [100.0, 100.0]** |
| False hidden-desire rate | **31.2% [28.1, 34.4]** | **0.0% [0.0, 0.0]** |
| …on `threat_compliance` | 62.5% [57.8, 67.2] | 0.0% [0.0, 0.0] |
| Specificity | 100.0% | 67.0% [64.4, 69.8] |
| True hidden preference detected | 99.2% | 0.0% — the system refuses |
| AUC, fear vs excitement | — | 0.835 |

Imputing a missing channel to zero silently disables the guard: sensitivity falls to zero and the
compliance case is misread 62.5% of the time, with nothing in the output indicating that the
protection is inactive.

Recording it as absent produces the opposite failure and the better one. The system stops asserting
hidden preference entirely, and specificity falls to 67.0% because arousal alone cannot separate fear
from excitement, so the caution fires on excitement too.

**This is the central design claim.** Under partial observation a reflective system should refuse,
not degrade; and the refusal must be visible in the output, not implicit in a number that happens to
be low.

### 6.5 Refusal calibration

Refusal is only defensible if it is calibrated. *n* = 300 per condition:

| Condition | Behaviour |
|---|---|
| Evidence genuinely insufficient | refuses **100.0% [100.0, 100.0]** |
| Evidence sufficient and clear | over-refuses **0.0% [0.0, 0.0]** |
| Evidence ample but ambiguous | does not refuse; reports uncertainty **0.405 [0.391, 0.419]** against **0.021 [0.020, 0.021]** on clear evidence |
| Evidence present but expired (decade-old, 30-day half-life) | infers **0.0% [0.0, 0.0]** of the time |

The system refuses when it should, does not refuse when it should not, and separates ambiguous from
clear evidence by a factor of nineteen in reported uncertainty.

### 6.6 Ambivalence is a state, not a residual

"You want and do not want this at once" is a claim about a person. Computed from dispersion alone it
fires on anything spread out: **95.5%** of pure measurement noise and **98.8%** of monotonic drift —
that is, of someone who has *made up their mind* — read as ambivalence, for a precision of **34.0%**.
Gating on lag-1 autocorrelation, which distinguishes alternation (−0.844) from drift (+0.517) and
noise (−0.120) where dispersion cannot (0.357 / 0.245 / 0.257), raises precision to **97.6%** with
recall unchanged at 100.0%.

### 6.7 Adversarial robustness: two checks a sceptical reader should demand

**"Your simulator is your theory."** The generative processes were defined so that threat and approach
differ on arousal and avoidance, and the guard keys on arousal and avoidance. A 0.0% rate under those
conditions risks being a tautology. So we swept the *separation* between the two processes on the
confound channels, at *n* = 300 per process per level.

| Separation | AUC | Shadow Mirror | Four-channel classifier | Mismatch-only |
|---|---|---|---|---|
| 1.00 | 1.000 | **0.0%** [0.0, 0.0] | **0.0%** [0.0, 0.0] | 94.3% [91.7, 96.7] |
| 0.75 | 1.000 | **0.0%** [0.0, 0.0] | **0.0%** [0.0, 0.0] | 95.3% [92.7, 97.7] |
| 0.50 | 1.000 | 2.3% [0.7, 4.0] | **0.0%** [0.0, 0.0] | 96.7% [94.7, 98.7] |
| 0.25 | 0.988 | 29.7% [24.7, 35.0] | **5.0%** [2.7, 7.7] | 97.3% [95.3, 99.0] |
| 0.00 | 0.491 | 76.7% [71.7, 81.3] | 82.0% [77.7, 86.3] | 96.3% [94.0, 98.3] |

The headline is not a knife-edge: it survives to roughly half the original channel separation. But it
is **entirely contingent on the confound channels carrying signal**, and at zero separation every
method fails, as it must — the classes are then identical on every observable, and any method
reporting 0.0% would be reporting a bug.

**"Your baselines are straw men."** They partly were. The table therefore adds a baseline a competent
engineer would build: a threshold classifier over the same four channels, with its threshold **fitted
on a held-out labelled split**. It matches us at high separation and **beats us at separation 0.25 —
5.0% against our 29.7%.**

We report this because it is true and because the reason matters: our guard uses a fixed,
pre-specified threshold, while the classifier was handed ground-truth labels for "was this a threat
response". **Those labels do not exist in deployment.** Nobody can tell a running system, for a given
person and episode, which mechanism produced their behaviour; that is the entire difficulty. The
supervised baseline is therefore an *upper bound on what any labelled method could achieve*, not an
available alternative — and the gap at separation 0.25 is a real, quantified cost of not having
supervision, which we would rather state than omit.

---

## 7. Consent, governance and data ownership

### 7.1 Consent as a mechanism

The system's other-person mode requires granular, per-stream, purpose-locked, revocable consent
before any datum is recorded. Streams a subject cannot notice about themselves — implicit measures,
physiological arousal, micro-avoidance — cannot be granted under a blanket authorisation; each
requires its own acknowledgement. Every stream declares in plain language both what it records and
what it *may reveal*. No grant, no observation: the engine raises rather than records.

Three critiques bound what any such mechanism can claim, and we do not claim past them. Privacy is
governed by norms of information flow appropriate to a context, so consent obtained in one context
does not license a flow into another. Privacy self-management does not scale. Post-GDPR consent
interfaces are routinely engineered to produce agreement rather than to elicit it. We therefore report
an **enforcement ratio** rather than a consent rate: the question is not how many people agreed but
how many refusals the mechanism actually produces.

### 7.2 The consent ledger

A mutable grant object cannot demonstrate that consent was given at a past date: a stream added and
later removed leaves no trace, and a grant revoked and re-issued looks identical to one that never
lapsed. `ledger.py` records every consent event — granted, stream added, re-affirmed, lapsed, revoked,
erased, context declared, refused — as an immutable, hash-chained entry.

Exercised in this pass (`verify_claims.py` §5):

- **`streams_granted_at(subject, when)`** answers the demonstrability question directly. Queried at
  the instant a second stream was added it returned the streams then under grant; queried after
  revocation it returned none.
- **`verify()`** re-derives the chain and returned `True`. Editing a single historical entry's detail
  and re-verifying returned `False`. This is tamper *evidence*, not tamper proofing — the subject owns
  their own file and that is the point — but a controller claiming consent on a date can show a chain
  that verifies, and an edited one will not.
- **Erasure retains the record, not the data.** The ledger records *that* observations were erased.
  That record is the evidence the withdrawal was honoured.
- **`withdrawal_receipt()`** returns what was granted, when it was withdrawn, how many records were
  erased, and whether the chain still verifies — something the subject keeps. Granting was a guided
  flow ending in a summary; revocation was a single call ending in silence, and those are not equally
  easy experiences however few keystrokes each takes.

### 7.3 The deployment gate

Emotion inference in a workplace or education institution is prohibited under EU AI Act Art. 5(1)(f),
applicable since 2 February 2025. A `DeploymentContext` declares where the instance is running —
`self`, `consented_individual`, `institutional` or `undeclared` — and gates the streams that supply
the biometric basis for affective inference.

Three design decisions are load-bearing, and all three were confirmed by execution in this pass
(`verify_claims.py` §4):

**Refusal is the default.** An `undeclared` context is treated as institutional and refused. An
operator who has not said where the system is running has not established that the prohibition does
not apply, and the safe reading of silence is the restrictive one. A `self` context is permitted.

**The safety exception requires a written basis, not a flag.** An empty `safety_exception_basis` still
refuses; a non-empty one permits. A boolean can be set by accident or by a config default; a sentence
has to be written by someone. The stated basis is recorded and exported with the consent ledger.

**The refusal explains itself.** The exception message carries the article numbers, the applicability
date, the declared context, and the exact call that would claim the exception — because a refusal a
developer cannot act on becomes a refusal a developer removes.

A Python module does not make anyone compliant, and the module says so in its own output. What it
does is convert a prohibition from a wish into a mechanism.

### 7.4 The honest enforcement ratio

**Of twelve documented prohibitions, six are enforced by a mechanism and covered by a test; six are
policy only.** The one that moved most recently is the only one currently unlawful to breach in the
EU. We suggest that papers proposing ethical architectures should print this ratio. A list of
prohibitions communicates intent; the fraction of them a machine will actually refuse communicates
the safeguard.

### 7.5 Data governance

Storage is local and file-based. The subject owns the file, can export it, and can delete it. The
package has **zero runtime dependencies**, which is an auditability commitment rather than an
aesthetic one: a person who wants to know what the system does can read all of it, and there is no
network path in the software.

---

## 8. What the architecture does not buy

On latent-state recovery under model misspecification, the graph-backed inference is **statistically
indistinguishable from a median-split quadrant classifier across all 20 tested conditions**, with
paired differences of −2.5 to +2.5 points and 2,000-resample percentile bootstrap intervals spanning
zero everywhere.

A reviewer may reasonably ask why an interactive-systems venue should care about an architecture that
buys no accuracy. The answer is that accuracy was never the safety-relevant quantity: the result of
§6.3 depends on the structural commitments — on representing a competing hypothesis rather than
filtering, and on distinguishing an absent channel from a zero reading. Structure is what carries it.

We report the negative result prominently because the temptation to omit it is strong and because it
relocates the contribution rather than diminishing it. **The architecture is not an accuracy
technique.** Its value is structural: conclusions that trace to evidence, provenance that survives
derivation, contradiction that is retained, revision that can be undone, inquiries that justify
themselves, and conformance that is decidable.

Two related measurements complete the picture.

**Calibration.** Where the model's assumed structure approximately holds, accumulating evidence with
an explicit *none-of-these* component reduces expected calibration error from **0.171 to 0.044** and
raises AUC(uncertainty → error) from **0.868 to 0.949**. Where it materially does not hold,
calibration is **worse**: ECE 0.151 → 0.221. The architecture trades uniformly mediocre calibration
for good-when-applicable and poor-when-not, which is an improvement only to the degree the system can
tell which regime it is in. It partly can, and not enough.

**Identifiability.** A two-channel location model cannot distinguish "state A, displaced" from
"state B" when the displacement points toward B. This is not fixable by thresholding. It *is*
partially fixable by observing more — pooling across topics to estimate a person-level displacement:

| δ | Topics | Uncorrected | Hard-assignment EM | Soft-assignment EM (current) |
|---|---|---|---|---|
| 0.30 | 5 | 82.3% | 90.8% | **93.4%** |
| 0.30 | 8 | 83.8% | 95.8% | **98.2%** |
| 0.45 | 3 | 54.1% | 55.8% | **76.2%** |
| 0.45 | 5 | 53.6% | 58.4% | **89.5%** |
| 0.45 | 8 | 53.2% | 61.3% | **97.0%** |

**A caution that nearly shipped.** The first version of this fix made things much worse where the data
is thin: at one topic and δ = 0.30, correcting with the unguarded soft estimate drove accuracy from
81.2% to **20.8%**. The cause is identifiability, not tuning — a single point can be moved onto any of
four corners by some offset, so there are more unknowns than equations. The estimator now **refuses
below three topics** and returns a zero offset. That is a condition, not a threshold. We flag it
because a fix that improves a headline by 36 points while quietly destroying the thin-data case is
exactly the kind of change that passes a benchmark and fails a person.

---

## 9. Complexity, measured

We report complexity as measurement rather than assertion, as scaling ratio per doubling (linear
≈ 2.0×, quadratic ≈ 4.0×):

| Operation | Bound | Measured |
|---|---|---|
| Provenance closure `ancestors()` | O(V+E) | **2.0×** — linear |
| Inquiry planning | O(\|H\|·\|A\|) | 3.9× at \|H\|=\|A\| — product of two linear factors |
| Belief update, log-odds ledger | O(1) amortised | **4.2× — quadratic** → **2.0×** after fix |
| Write-then-consult path | O(n) per consultation | **3.8× — quadratic** → **≈2.0×** after fix |

Two rows were defects in our own code. The belief ledger summed every contribution on each call,
costing 624 ms at 8,000 updates; maintaining a running total gives 78 ms at 16,000. **A regression
test fails if the ratio exceeds 3.0×**, using best-of-three timing so that machine load does not
convert a linear algorithm into a failing test.

The fourth row was the larger one. Beliefs are now computed when the mirror is **consulted**, not when
an observation is written, which took the path from 1121 ms to 5.24 ms at 800 evidence pairs — a 214×
improvement — and from 3.8× to 2.0× per doubling. Re-measuring the write-then-consult path in this
pass over 100 → 800 evidence pairs reproduced **linear scaling at roughly 1.8–2.1× per doubling**
across repeated runs (`verify_claims.py` §1); absolute timings differ from the figure above because
the harness differs, and the shape rather than the constant is the claim.

Two honest notes survive the fix. The reactivity counter now counts consultations rather than writes,
which is arguably what a reactivity measure should have counted from the start, since it exists to
warn that *looking at a guess changes later answers*. And the asymptotics of a **read-heavy** pattern
are unchanged: one consultation per twenty writes still scales at 3.1× per doubling, because each
consultation is O(n). The constant improved twentyfold; the shape did not.

---

## 10. Validation

### 10.1 The test suite

Running the suite in this pass: **707 passed, 2 xfailed**. The two strict `xfail`s record operators
that are specified and implemented nowhere, so they cannot quietly become "implemented" in a later
summary:

| Operator | Status |
|---|---|
| **Causal reflection** — intervention, counterfactual query | Prose only. No do-operator exists. Research agenda, not a component |
| **Knowledge consolidation** — promotion from belief to revisable knowledge | Prose only. No promotion criterion exists |

Also unimplemented: encryption at rest, multimodal acquisition, a reflective execution engine with
event queues, and any user interface beyond a command line.

A reference architecture earns the word *reference* when the distance between its formalism and its
implementation can be enumerated. We enumerate it.

### 10.2 How strong the suite actually is

Earlier drafts stated that nothing measured whether the randomised harness exercises the state space
in any principled sense. Mutation testing now does, and the measurement is not flattering.

Mutation testing produced **5,114 mutants**. The suite killed **2,319** and **1,549 survived**, for a
mutation score of **59.9%**. A further 1,244 mutants sit in code with no covering test at all, 909 of
them in a command-line interface that has never had tests and carries no claim in this paper.

Survivors concentrate in the inference engine (404), the pattern layer (278), the invariant checks
themselves (206) and the formation model (195). Inspection of a sample shows most are label and
message mutations rather than behavioural ones, which means the raw score understates the suite. But
not all are cosmetic. **Mutating an invariant's own identifier survived**, which means no test
asserted that a check returns the invariant it claims to be — a catalogue of named architectural
properties that could have been silently renamed. Two tests now close that, and they exist because a
tool found the gap rather than because we thought of it.

We report the score rather than tuning it. A mutation score is a lower bound on test strength and an
upper bound on nothing, and 59.9% is a middling result for a package that makes conformance claims.

### 10.3 Five things found by measurement rather than by intent

Listed because they are the best argument for the method, and because each was slightly embarrassing.

1. **Provenance as a scalar dropped every parent but one.** The formalism said "attribute" where the
   literature had said "set" three decades earlier. Invariant II caught it.
2. **A clamping step that looked like numerical hygiene destroyed commutativity and retractability.**
   Belief order-invariance went from 0.0396/0.9900 across permutations to exact agreement.
3. **Invariant X false-positived on our own shipped output.** The defect was in the check, not the
   output (§5.3).
4. **Retroactive consent was already impossible and nobody designed it.** Found by a failing test. It
   falls out of asking *what was granted at time T* rather than *is there a grant*.
5. **Mutating an invariant's own identifier survived.** Nothing asserted that a check returns the
   invariant it claims to be (§10.2).

---

## 11. The regulatory tension

We report this because it is unresolved, and because the shape of it is more general than this system.

The EU AI Act defines biometric data as *"personal data resulting from specific technical processing
relating to the physical, physiological or behavioural characteristics of a natural person"*
(Art. 3(34)). Unlike GDPR Art. 4(14), **it does not require unique identification**. A heart-rate-like
arousal proxy is therefore biometric data under the Act while identifying nobody. An *emotion
recognition system* is one *"for the purpose of identifying or inferring emotions or intentions of
natural persons on the basis of their biometric data"* (Art. 3(39)). Our guard infers a threat
response — an affective and intentional state — partly on the basis of that arousal channel.

So: **the channel that exists only to protect people, and that §6.4 shows does protect them, is what
brings the system within a prohibition written to prevent a different harm.** Remove it and the
exposure largely disappears; remove it and the false hidden-desire rate returns to 31.2%.

The safety exception at Art. 5(1)(f) is available and, in our reading, applicable: the channel's sole
documented purpose in code, tests and specification is to prevent a specific measured harm, and it is
used for nothing else. We state that as an argument rather than a conclusion. We are aware of no case
law interpreting the exception for a guard of this kind, and a system whose safety mechanism is itself
an emotion-inference system is a case the Act does not obviously anticipate.

### 11.1 A second regime, with no research exemption

The EU analysis is the one the literature rehearses. It is not the only regime a system like this must
survive, and the contrast is instructive.

This work is conducted under Egyptian jurisdiction. Law No. 214 of 2020 on Clinical Medical Research
establishes a national ethics architecture but does not reach us: its subject is defined as studies
assessing "therapeutic, pharmaceutical, surgical, nutritional, preventive or diagnostic
interventions", and behavioural, psychological and computing research falls outside its scope. The
Supreme Council of Universities issued a national academic-integrity and research-ethics guide in
January 2026 whose third book addresses behavioural and social research committees, but it carries no
decree number and no binding-force clause, and whether it reaches private universities is
unspecified. We classify it as guidance rather than law.

Personal Data Protection Law No. 151 of 2020 does reach us, and reaches further than the GDPR in three
respects. Its definition of personal data expressly includes data determining "psychological …
identity". Its sensitive-data category covers "psychological, mental, or physical health, or genetic,
biometric or financial data", and Article 12 prohibits processing that category without a licence from
the Personal Data Protection Centre *in addition to* written explicit consent, on penalty of
imprisonment and a fine up to EGP 5,000,000. And — the point worth putting in front of any venue —
**it contains no scientific-research exemption whatsoever**. The GDPR's research accommodations have
no Egyptian counterpart. A search of the Arabic text of both the law and its executive regulations
(Decree No. 816 of 2025, in force 2 November 2025, compliance deadline 31 October 2026) finds that the
words for "research", "studies" and "university" do not appear.

The consequence inverts a common assumption. A researcher in a jurisdiction with a *weaker* national
human-subjects law can face a *stricter* data-protection constraint on exactly the physiological and
psychological channels this architecture consumes, with no research carve-out to fall back on. Our
design response is the one already described: refuse the biometric stream rather than seek a basis for
it, and treat anonymisation rather than pseudonymisation as the only route out of scope.

**This is a reading of statutory text, not legal advice, and it has not been reviewed by counsel.**

---

## 12. Limitations

**No human subjects.** Nothing here establishes any effect on human reasoning, comprehension, trust,
wellbeing or task outcome, and no such claim is made. Every result is a property of code or of
simulated signal streams.

**Simulation encodes a theory.** The generative processes embody assumptions about how latent states
manifest in observable signal. If those are wrong, absolute rates are wrong in the same direction for
every method compared, including the baselines. We regard the *ordering* of methods as more robust
than the absolute rates, and §6.7 measures how far that ordering survives as the key assumption is
weakened.

**A point estimate of zero is not a guarantee of zero.** Across 800 threat episodes we observed no
misreadings. The 95% upper bound implied by the rule of three is **0.37%**, and that — not 0.0% — is
the number a deployment decision should use.

**Two implementations, not many.** §5.4 shows the decision procedure separating a compliant
implementation from a non-compliant one, which rules out vacuity. It does not establish that the
procedure is portable to an implementation built on different primitives — a graph database, an
event-sourced store, a logic programming substrate.

**Invariants X and XI are syntactic proxies for semantic properties.** Whether an output usurps a
person's authority over their own self-understanding is not a matter of which pronouns it contains.
Our check tests phrasing, and §5.3 documents it producing a false positive on its first contact with
real output. It will also produce false negatives: a sentence can be a verdict without matching any
pattern we listed. The check raises the floor; it does not measure the property.

**The clinical vocabulary is borrowed.** We use "compliance" and "threat response" to name a pattern
of approach behaviour under low stated desire and high arousal. There is a genuine peer-reviewed
literature in this region — appeasement under traumatic entrapment, tonic immobility as an evolved
defence, the acute stress response as a spectrum — and we cite it to locate the concern, not to claim
our simulation instantiates any of it. One term deserves separate treatment: **"fawn" is not a
clinical category.** We traced it to a self-published practitioner trade book and could locate no
refereed source establishing it as a validated construct. It has been removed from every load-bearing
claim.

**We are not lawyers.** §11 is a reading of statutory text, not advice.

**The specificity cost is real.** Under partial observation the system labels excitement as a possible
threat 99.0% of the time. A person who is excited and told to consider whether they are afraid has
been mildly misread. We judge this preferable to the converse and do not claim it is costless.

**Credible sets do not reach nominal coverage.** Reporting a credible set instead of a point label
improves the rate at which the truth is contained in the output (78.2% → 88.0% at δ = 0.30) but a set
claiming 90% mass contains the truth 60.5% [55.5, 65.2] of the time at δ = 0.45. A credible set
inherits its posterior's miscalibration; reaching nominal coverage requires conformal calibration
against held-out labelled outcomes, which do not exist without a human study.

**Scale.** Everything reported runs on a single machine over thousands of nodes, not millions, and
the read path remains O(n) per consultation.

---

## 13. Conclusion

Making the invariants executable found two defects that a prose specification had asserted away: a
provenance model that dropped parents, and a belief operator whose result depended on the order
evidence arrived. Neither was visible to a reader of the document. Both were visible on the first run
of the decision procedure.

Making refusal a first-class output, rather than a low-confidence label, removed a specific
foreseeable harm in simulation — and the ablation shows that the removal depends on a commitment that
looks like a detail: an absent channel must be representable as absent. A system that imputes it to
zero keeps its guard in the codebase and loses it in production, with nothing in the output to say so.

We think the transferable claims are these. Reference architectures for human–AI interaction should
ship their conformance suites, should include negative tests, and should point those suites at output
a person would actually see. Papers proposing ethical architectures should print the fraction of their
prohibitions that a machine will actually refuse. And a reflective system under partial observation
should refuse rather than degrade.

Ours did all three and was wrong three times — about provenance, about order invariance, and about its
own Invariant X check. Each error surfaced within a minute of the check being run, and none would have
surfaced from reading.

---

## Ethics statement

This research did not involve human or animal subjects. All results derive from code execution and
from simulated signal streams; no personal data was collected, processed or analysed.

The system is a research instrument, not a medical device, and is not suitable for clinical,
educational, employment, credit, insurance, policing or other high-stakes deployment. It refuses to
enable the physiological stream in institutional and undeclared deployment contexts. The authors note
the regulatory position described in §11 and do not assert that the safety exception under
Art. 5(1)(f) applies as a settled matter.

**Data and code availability.** Implementation and conformance suite are released under an open
licence. *[REPOSITORY URL — TO BE COMPLETED]* See Appendix A for the provenance of every number in
this paper, including which were re-derived in preparing this draft and which were not.


---

## References

The 102 references below are the union of the two source papers' reference lists, deduplicated. Each was confirmed against a live source with a resolvable identifier in Session 14, **except the 6 marked †**, which were introduced in Session 15 after the verification pass and are unconfirmed under ground rule 6; see **OW-9** in Appendix B.

[1] C. E. Alchourrón, P. Gärdenfors, and D. Makinson. "On the logic of theory change: Partial meet contraction and revision functions." *Journal of Symbolic Logic*, 50(2):510–530, 1985. DOI: 10.2307/2274239

[2] S. Amershi, D. Weld, M. Vorvoreanu, A. Fourney, B. Nushi, P. Collisson, J. Suh, S. Iqbal, P. N. Bennett, K. Inkpen, J. Teevan, R. Kikin-Gil, and E. Horvitz. "Guidelines for Human-AI Interaction." *Proc. CHI 2019*, paper 3. DOI: 10.1145/3290605.3300233

[3] N. Andalibi and J. Buss. "The Human in Emotion Recognition on Social Media: Attitudes, Outcomes, Risks." *Proc. CHI 2020*, pp. 1–16. DOI: 10.1145/3313831.3376680

[4] A. N. Angelopoulos and S. Bates. "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification." arXiv:2107.07511, 2021.

[5] M. Ardelt. "Empirical Assessment of a Three-Dimensional Wisdom Scale." *Research on Aging*, 25(3):275–324, 2003. DOI: 10.1177/0164027503025003004 †

[6] G. Bansal, T. Wu, J. Zhou, R. Fok, B. Nushi, E. Kamar, M. T. Ribeiro, and D. S. Weld. "Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance." *Proc. CHI 2021*, article 81. DOI: 10.1145/3411764.3445717

[7] L. F. Barrett, R. Adolphs, S. Marsella, A. M. Martinez, and S. D. Pollak. "Emotional expressions reconsidered: Challenges to inferring emotion from human facial movements." *Psychological Science in the Public Interest*, 20(1):1–68, 2019. DOI: 10.1177/1529100619832930

[8] E. P. S. Baumer. "Reflective Informatics: Conceptual Dimensions for Designing Technologies of Reflection." *Proc. CHI 2015*, pp. 585–594. DOI: 10.1145/2702123.2702234

[9] V. Bellotti and K. Edwards. "Intelligibility and Accountability: Human Considerations in Context-Aware Systems." *Human-Computer Interaction*, 16(2–4):193–212, 2001. DOI: 10.1207/S15327051HCI16234_05

[10] H. S. Bracha. "Freeze, Flight, Fight, Fright, Faint: Adaptationist Perspectives on the Acute Stress Response Spectrum." *CNS Spectrums*, 9(9):679–685, 2004. DOI: 10.1017/S1092852900001954

[11] I. Budin-Ljøsne et al. "Dynamic consent: A potential solution to some of the challenges of modern biomedical research." *BMC Medical Ethics*, 18:4, 2017. DOI: 10.1186/s12910-016-0162-9

[12] S. Bull and J. Kay. "Open Learner Models." In *Advances in Intelligent Tutoring Systems*, Studies in Computational Intelligence vol. 308, pp. 301–322. Springer, 2010. DOI: 10.1007/978-3-642-14363-2_15

[13] P. Buneman, S. Khanna, and W.-C. Tan. "Why and Where: A Characterization of Data Provenance." *Database Theory — ICDT 2001*, LNCS, pp. 316–330, 2001. DOI: 10.1007/3-540-44503-X_20

[14] R. A. Calvo and S. D'Mello. "Affect detection: An interdisciplinary review of models, methods, and their applications." *IEEE Transactions on Affective Computing*, 1(1):18–37, 2010. DOI: 10.1109/T-AFFC.2010.1

[15] C. Cantor and J. Price. "Traumatic Entrapment, Appeasement and Complex Post-Traumatic Stress Disorder: Evolutionary Perspectives of Hostage Reactions, Domestic Abuse and the Stockholm Syndrome." *Australian & New Zealand Journal of Psychiatry*, 41(5):377–384, 2007. DOI: 10.1080/00048670701261178

[16] K. Chaloner and I. Verdinelli. "Bayesian Experimental Design: A Review." *Statistical Science*, 10(3):273–304, 1995. DOI: 10.1214/ss/1177009939

[17] B. Chen, M. Vansteenkiste, W. Beyers, et al. "Basic psychological need satisfaction, need frustration, and need strength across four cultures." *Motivation and Emotion*, 39(2):216–236, 2015. DOI: 10.1007/s11031-014-9450-1 †

[18] J. X. Chen, A. McDonald, Y. Zou, E. Tseng, K. A. Roundy, A. Tamersoy, F. Schaub, T. Ristenpart, and N. Dell. "Trauma-Informed Computing: Towards Safer Technology Experiences for All." *Proc. CHI 2022*, pp. 1–20. DOI: 10.1145/3491102.3517475

[19] J. Cheney, L. Chiticariu, and W.-C. Tan. "Provenance in Databases: Why, How, and Where." *Foundations and Trends in Databases*, 1(4):379–474, 2009. DOI: 10.1561/1900000006

[20] C. K. Chow. "On optimum recognition error and reject tradeoff." *IEEE Transactions on Information Theory*, 16(1):41–46, 1970. DOI: 10.1109/TIT.1970.1054406

[21] K. Claessen and J. Hughes. "QuickCheck: a lightweight tool for random testing of Haskell programs." *Proc. Fifth ACM SIGPLAN International Conference on Functional Programming (ICFP '00)*, pp. 268–279, 2000. DOI: 10.1145/351240.351266

[22] C. S. Darling-Fisher and N. K. Leidy. "Measuring Eriksonian Development in the Adult: The Modified Erikson Psychosocial Stage Inventory." *Psychological Reports*, 62(3):747–754, 1988. DOI: 10.2466/pr0.1988.62.3.747 †

[23] A. Darwiche and J. Pearl. "On the logic of iterated belief revision." *Artificial Intelligence*, 89(1–2):1–29, 1997. DOI: 10.1016/S0004-3702(96)00038-0

[24] A. Didolkar, N. Ballas, S. Arora, and A. Goyal. "Metacognitive Reuse: Turning Recurring LLM Reasoning Into Concise Behaviors." arXiv:2509.13237, 2025.

[25] F. Doshi-Velez and B. Kim. "Towards a Rigorous Science of Interpretable Machine Learning." arXiv:1702.08608, 2017.

[26] S. Ducasse and D. Pollet. "Software Architecture Reconstruction: A Process-Oriented Taxonomy." *IEEE Transactions on Software Engineering*, 35(4):573–591, 2009. DOI: 10.1109/TSE.2009.19

[27] B. Efron and R. J. Tibshirani. *An Introduction to the Bootstrap*. Chapman & Hall, 1993. ISBN 9780412042317 ---

[28] R. El-Yaniv and Y. Wiener. "On the Foundations of Noise-free Selective Classification." *Journal of Machine Learning Research*, 11(53):1605–1641, 2010. https://www.jmlr.org/papers/v11/el-yaniv10a.html

[29] A. P. Elenjical, V. H. Kavuri, and V. Varma. "Think2: Grounded Metacognitive Reasoning in Large Language Models." arXiv:2602.18806, 2026.

[30] D. A. Epstein, A. Ping, J. Fogarty, and S. A. Munson. "A lived informatics model of personal informatics." *Proc. UbiComp 2015*, pp. 731–742. DOI: 10.1145/2750858.2804250

[31] R. Fleck and G. Fitzpatrick. "Reflecting on reflection: framing a design landscape." *Proc. OZCHI 2010*, pp. 216–223. DOI: 10.1145/1952222.1952269

[32] D. Freed, J. Palmer, D. Minchala, K. Levy, T. Ristenpart, and N. Dell. "'A Stalker's Paradise': How Intimate Partner Abusers Exploit Technology." *Proc. CHI 2018*, article 667. DOI: 10.1145/3173574.3174241

[33] Y. Geifman and R. El-Yaniv. "Selective Classification for Deep Neural Networks." *Advances in Neural Information Processing Systems 30 (NIPS 2017)*. https://papers.nips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html

[34] Y. Geifman and R. El-Yaniv. "SelectiveNet: A Deep Neural Network with an Integrated Reject Option." *Proc. 36th International Conference on Machine Learning*, PMLR 97:2151–2159, 2019. https://proceedings.mlr.press/v97/geifman19a.html

[35] M. Gendron, D. Roberson, J. M. van der Vyver, and L. F. Barrett. "Perceptions of emotion from facial expressions are not culturally universal." *Emotion*, 14(2):251–262, 2014. DOI: 10.1037/a0036052

[36] P. Gilbert. "Evolution and social anxiety: The role of attraction, social competition, and social hierarchies." *Psychiatric Clinics of North America*, 24(4):723–751, 2001. DOI: 10.1016/S0193-953X(05)70260-4

[37] P. Groth and L. Moreau (eds.). "PROV-Overview: An Overview of the PROV Family of Documents." W3C Working Group Note, 30 April 2013. https://www.w3.org/TR/2013/NOTE-prov-overview-20130430/

[38] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger. "On Calibration of Modern Neural Networks." *Proc. 34th International Conference on Machine Learning*, PMLR 70:1321–1330, 2017. https://proceedings.mlr.press/v70/guo17a.html

[39] P. Gärdenfors. *Knowledge in Flux: Modeling the Dynamics of Epistemic States*. MIT Press, 1988. ISBN 9780262071093

[40] J. A. Hanley and A. Lippman-Hand. "If Nothing Goes Wrong, Is Everything All Right? Interpreting Zero Numerators." *JAMA*, 249(13):1743–1745, 1983. DOI: 10.1001/jama.1983.03330370053031

[41] D. Hendrycks and K. Gimpel. "A Baseline for Detecting Misclassified and Out-of-Distribution Examples in Neural Networks." *ICLR 2017*. arXiv:1610.02136

[42] E. Horvitz. "Principles of mixed-initiative user interfaces." *Proc. CHI 1999*, pp. 159–166. DOI: 10.1145/302979.303030

[43] N. Houlsby, F. Huszár, Z. Ghahramani, and M. Lengyel. "Bayesian Active Learning for Classification and Preference Learning." arXiv:1112.5745, 2011.

[44] L. X. Hy and J. Loevinger. *Measuring Ego Development*, 2nd ed. Lawrence Erlbaum, 1996. ISBN 9781138876552 †

[45] D. Jackson. "Alloy: a lightweight object modelling notation." *ACM Transactions on Software Engineering and Methodology*, 11(2):256–290, 2002. DOI: 10.1145/505145.505149

[46] B. Jacobs. "Commutativity of probabilistic belief revision." *Frontiers in Cognition*, 2025. DOI: 10.3389/fcogn.2025.1623227

[47] R. C. Jeffrey. *The Logic of Decision*, 2nd ed. University of Chicago Press, 1983. ISBN 9780226395821. (1st ed., McGraw-Hill, 1965.)

[48] J. Kay. "Scrutable Adaptation: Because We Can and Must." *Adaptive Hypermedia and Adaptive Web-Based Systems (AH 2006)*, LNCS 4018, pp. 11–19. DOI: 10.1007/11768012_2

[49] J. Kaye, E. A. Whitley, D. Lund, M. Morrison, H. Teare, and K. Melham. "Dynamic consent: a patient interface for twenty-first century research networks." *European Journal of Human Genetics*, 23(2):141–146, 2015. DOI: 10.1038/ejhg.2014.71

[50] J. Knodel and D. Popescu. "A Comparison of Static Architecture Compliance Checking Approaches." *Working IEEE/IFIP Conference on Software Architecture (WICSA'07)*, 2007. DOI: 10.1109/WICSA.2007.1

[51] B. Kompa, J. Snoek, and A. L. Beam. "Second opinion needed: communicating uncertainty in medical machine learning." *npj Digital Medicine*, 4:4, 2021. DOI: 10.1038/s41746-020-00367-3

[52] L. Lahey, E. Souvaine, R. Kegan, R. Goodman, and S. Felix. *A Guide to the Subject-Object Interview: Its Administration and Interpretation*. Harvard Graduate School of Education, 1988. †

[53] L. Lamport. "The temporal logic of actions." *ACM Transactions on Programming Languages and Systems*, 16(3):872–923, 1994. DOI: 10.1145/177492.177726

[54] Law No. 151 of 2020 promulgating the Personal Data Protection Law (Egypt), Official Gazette issue 28 bis (هـ), 15 July 2020, in force 16 October 2020; Executive Regulations, Minister of Communications and Information Technology Decree No. 816 of 2025, in force 2 November 2025. Regulator: https://pdpc.gov.eg

[55] Law No. 214 of 2020 promulgating the Law Regulating Clinical Medical Research (Egypt), Official Gazette issue 51 bis (و), 23 December 2020; Executive Regulations, Prime Minister's Decree No. 927 of 2022. https://www.edaegypt.gov.eg/media/zz0alwxy/law-214-of-2020_-to-cairo-legal_.pdf

[56] M. Leucker and C. Schallhart. "A brief account of runtime verification." *The Journal of Logic and Algebraic Programming*, 78(5):293–303, 2009. DOI: 10.1016/j.jlap.2008.08.004

[57] I. Li, A. K. Dey, and J. Forlizzi. "A stage-based model of personal informatics systems." *Proc. CHI 2010*, pp. 557–566. DOI: 10.1145/1753326.1753409

[58] B. Y. Lim and A. K. Dey. "Assessing demand for intelligibility in context-aware applications." *Proc. UbiComp 2009*, pp. 195–204. DOI: 10.1145/1620545.1620576

[59] D. V. Lindley. "On a Measure of the Information Provided by an Experiment." *The Annals of Mathematical Statistics*, 27(4):986–1005, 1956. DOI: 10.1214/aoms/1177728069

[60] Z. C. Lipton. "The mythos of model interpretability." *Communications of the ACM*, 61(10):36–43, 2018. DOI: 10.1145/3233231. (Preprint: arXiv:1606.03490, 2016.)

[61] D. J. C. MacKay. "Information-Based Objective Functions for Active Data Selection." *Neural Computation*, 4(4):590–604, 1992. DOI: 10.1162/neco.1992.4.4.590

[62] D. Madras, T. Pitassi, and R. Zemel. "Predict Responsibly: Improving Fairness and Accuracy by Learning to Defer." *Advances in Neural Information Processing Systems 31 (NeurIPS 2018)*. arXiv:1711.06664

[63] B. P. Marx, J. P. Forsyth, G. G. Gallup, T. Fusé, and J. M. Lexington. "Tonic Immobility as an Evolved Predator Defense: Implications for Sexual Assault Survivors." *Clinical Psychology: Science and Practice*, 15(1):74–90, 2008. DOI: 10.1111/j.1468-2850.2008.00112.x

[64] M. Matar and H. Silverman. "Ethical Considerations and Challenges of Egypt's New Clinical Research Law." *Journal of Empirical Research on Human Research Ethics*, 2022. DOI: 10.1177/15562646221096188

[65] B. Meyer. "Applying 'design by contract'." *Computer*, 25(10):40–51, 1992. DOI: 10.1109/2.161279

[66] T. Miller. "Explanation in artificial intelligence: Insights from the social sciences." *Artificial Intelligence*, 267:1–38, 2019. DOI: 10.1016/j.artint.2018.07.007

[67] L. Moreau and P. Missier (eds.). "PROV-DM: The PROV Data Model." W3C Recommendation, 30 April 2013. https://www.w3.org/TR/2013/REC-prov-dm-20130430/

[68] H. Mozannar and D. Sontag. "Consistent Estimators for Learning to Defer to an Expert." *Proc. 37th International Conference on Machine Learning*, PMLR 119:7076–7087, 2020. https://proceedings.mlr.press/v119/mozannar20b.html

[69] G. C. Murphy, D. Notkin, and K. J. Sullivan. "Software reflexion models: bridging the gap between design and implementation." *IEEE Transactions on Software Engineering*, 27(4):364–380, 2001. DOI: 10.1109/32.917525

[70] J. D. Nelson. "Finding Useful Questions: On Bayesian Diagnosticity, Probability, Impact, and Information Gain." *Psychological Review*, 112(4):979–999, 2005. DOI: 10.1037/0033-295X.112.4.979

[71] H. Nissenbaum. "Privacy as Contextual Integrity." *Washington Law Review*, 79(1):119–157, 2004. https://digitalcommons.law.uw.edu/wlr/vol79/iss1/10/

[72] M. Nouwens, I. Liccardi, M. Veale, D. Karger, and L. Kagal. "Dark Patterns after the GDPR: Scraping Consent Pop-ups and Demonstrating their Influence." *Proc. CHI 2020*, article 194. DOI: 10.1145/3313831.3376321

[73] M. Oaksford and N. Chater. "A rational analysis of the selection task as optimal data selection." *Psychological Review*, 101(4):608–631, 1994. DOI: 10.1037/0033-295X.101.4.608

[74] M. Pakdaman Naeini, G. F. Cooper, and M. Hauskrecht. "Obtaining Well Calibrated Probabilities Using Bayesian Binning." *Proc. AAAI Conference on Artificial Intelligence*, 29(1), 2015. DOI: 10.1609/aaai.v29i1.9602

[75] L. Passos, R. Terra, M. T. Valente, R. Diniz, and N. das Chagas Mendonça. "Static Architecture-Conformance Checking: An Illustrative Overview." *IEEE Software*, 27(5):82–89, 2010. DOI: 10.1109/MS.2009.117

[76] J. Pearl. *Probabilistic Reasoning in Intelligent Systems: Networks of Plausible Inference*. Morgan Kaufmann, 1988. ISBN 9781558604797

[77] D. E. Perry and A. L. Wolf. "Foundations for the study of software architecture." *ACM SIGSOFT Software Engineering Notes*, 17(4):40–52, 1992. DOI: 10.1145/141874.141884

[78] R. W. Picard. *Affective Computing*. MIT Press, 1997. ISBN 9780262161701

[79] M. Raghu, K. Blumer, G. Corrado, J. Kleinberg, Z. Obermeyer, and S. Mullainathan. "The Algorithmic Automation Problem: Prediction, Triage, and Human Effort." arXiv:1903.12220, 2019.

[80] A. Rapp and F. Cena. "Personal informatics for everyday life: How users without prior self-tracking experience engage with personal data." *International Journal of Human-Computer Studies*, 94:1–17, 2016. DOI: 10.1016/j.ijhcs.2016.05.006

[81] Regulation (EU) 2016/679 (General Data Protection Regulation). https://eur-lex.europa.eu/eli/reg/2016/679/oj

[82] Regulation (EU) 2024/1689 (Artificial Intelligence Act). https://eur-lex.europa.eu/eli/reg/2024/1689/oj

[83] K. Roemmich, T. Rosenberg, S. Fan, and N. Andalibi. "Values in Emotion Artificial Intelligence Hiring Services: Technosolutions to Organizational Problems." *Proc. ACM Hum.-Comput. Interact.*, 7(CSCW1):1–28, 2023. DOI: 10.1145/3579543

[84] Y. Romano, M. Sesia, and E. J. Candès. "Classification with Valid and Adaptive Coverage." *Advances in Neural Information Processing Systems 33 (NeurIPS 2020)*, pp. 3581–3591. https://proceedings.neurips.cc/paper/2020/hash/244edd7e85dc81602b7615cd705545f5-Abstract.html

[85] R. Rosenbacke, Å. Melhus, et al. "How Explainable AI Can Increase or Decrease Clinicians' Trust in AI Applications in Health Care: Systematic Review." *JMIR AI*, 1:e53207, 2024. PMID: 39476365

[86] R. Rosenbacke, Å. Melhus, et al. "How Explainable Artificial Intelligence Can Increase or Decrease Clinicians' Trust in AI Applications in Health Care: Systematic Review." *JMIR AI*, 1:e53207, 2024. PMID: 39476365

[87] C. Rudin. "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead." *Nature Machine Intelligence*, 1:206–215, 2019. DOI: 10.1038/s42256-019-0048-x

[88] U. Schäfer et al. "'The AI is uncertain, so am I. What now?': Navigating Shortcomings of Uncertainty Representations in Human-AI Collaboration with Capability-focused Guidance." *Proc. ACM Hum.-Comput. Interact.*, 2025. DOI: 10.1145/3757451

[89] P. Sengers, K. Boehner, S. David, and J. Kaye. "Reflective design." *Proc. 4th Decennial Conference on Critical Computing (CC '05)*, pp. 49–58, 2005. DOI: 10.1145/1094562.1094569

[90] B. Settles. "Active Learning Literature Survey." Computer Sciences Technical Report 1648, University of Wisconsin–Madison, 2009. http://digital.library.wisc.edu/1793/60660

[91] D. J. Solove. "Introduction: Privacy Self-Management and the Consent Dilemma." *Harvard Law Review*, 126(7):1880–1903, 2013. https://harvardlawreview.org/print/vol-126/introduction-privacy-self-management-and-the-consent-dilemma/

[92] W. Spohn. "Ordinal Conditional Functions: A Dynamic Theory of Epistemic States." In W. L. Harper and B. Skyrms (eds.), *Causation in Decision, Belief Change, and Statistics*, vol. II, pp. 105–134. Kluwer, 1988. DOI: 10.1007/978-94-009-2865-7_6

[93] L. Stark and J. Hoey. "The Ethics of Emotion in Artificial Intelligence Systems." *Proc. 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21)*, pp. 782–793. DOI: 10.1145/3442188.3445939

[94] M. F. Steger, P. Frazier, S. Oishi, and M. Kaler. "The Meaning in Life Questionnaire: Assessing the presence of and search for meaning in life." *Journal of Counseling Psychology*, 53(1):80–93, 2006. DOI: 10.1037/0022-0167.53.1.80 †

[95] Supreme Council of Universities (Egypt). *Guide to Academic Integrity and Scientific Research Ethics in Egypt* (دليل النزاهة الأكاديمية وأخلاقيات البحث العلمي في مصر), 26 January 2026. https://scu.eg/download/guide-to-academic-integrity-and-research-ethics/ *(Guidance; carries no decree number or binding-force clause. Applicability to private universities unspecified.)* ---

[96] R. Terra and M. T. Valente. "A dependency constraint language to manage object-oriented software architectures." *Software: Practice and Experience*, 39(12):1073–1094, 2009. DOI: 10.1002/spe.931

[97] S. L. Vasileiou and W. Yeoh. "Human-Aware Belief Revision: A Cognitively Inspired Framework for Explanation-Guided Revision of Human Models." arXiv:2405.19238, 2024.

[98] S. L. Vasileiou et al. "How Do People Revise Inconsistent Beliefs? Examining Belief Revision in Humans with User Studies." arXiv:2506.09977, 2025.

[99] V. Vovk, A. Gammerman, and G. Shafer. *Algorithmic Learning in a Random World*. Springer, 2005. DOI: 10.1007/b106715

[100] S. Wachter and B. Mittelstadt. "A Right to Reasonable Inferences: Re-Thinking Data Protection Law in the Age of Big Data and AI." *Columbia Business Law Review*, 2019(2):494–620. DOI: 10.7916/cblr.v2019i2.3424

[101] P. Walker. *Complex PTSD: From Surviving to Thriving — A Guide and Map for Recovering from Childhood Trauma*. Azure Coyote Publishing, 2013. ISBN 9781492871842. **Cited as the popular origin of the term "fawn"; this is a self-published practitioner trade book and is not peer-reviewed academic literature.** See §2.3.

[102] Xin et al. "MetaMem: Evolving Meta-Memory for Knowledge Utilization through Self-Reflective Symbolic Optimization." *Findings of ACL 2026*. arXiv:2602.11182

---

## Appendix A — Number provenance

Ground rule 4 of this programme: *no number enters a manuscript unless a file in the repository
produces it and the person writing the sentence has run that file.* This appendix records compliance
with that rule honestly, which means recording where it could not be met.

**Re-derived while preparing this draft**, by running the named file against `shadow_mirror` v1.3.0:

| Claim | §  | Source | Result |
|---|---|---|---|
| Test suite totals | 10.1 | `pytest -q` | 707 passed, 2 xfailed |
| Order invariance over 120 permutations | 4.2, 5.4 | `verify_claims.py` §2 | 120 permutations, 1 distinct outcome, spread 0.0 |
| Eleven callable invariant checks | 5.1 | `verify_claims.py` §3 | 11 checks + `check_all` |
| Deployment gate refuses institutional and undeclared | 7.3 | `verify_claims.py` §4 | refused; `self` permitted |
| Empty safety basis still refuses | 7.3 | `verify_claims.py` §4 | `True` |
| Ledger verifies; edit is detectable | 7.2 | `verify_claims.py` §5 | `verify()` `True` → `False` after edit |
| `streams_granted_at` is time-aware | 7.2 | `verify_claims.py` §5 | returns granted streams, then none after revocation |
| Refusing methods refuse when called | 5.5 | `verify_claims.py` §6 | 9 called, 9 refused, 0 returned |
| Write-then-consult path is linear | 9 | `verify_claims.py` §1 | ≈1.8–2.1× per doubling |

**Carried from the programme record, and *not* re-derived here.** The scripts that produce these
numbers — `run_benchmarks.py`, `conformance_v10.py`, `experiment_d23.py`,
`experiment_ambivalence.py`, `analyze_v030_vs_v040.py` — and their outputs `results.json` and
`v030_vs_v040.json` are **not present in the research archive this draft was assembled from**. They
are cited here on the authority of the session reports and the two source papers, and a reader cannot
currently re-run them. This is recorded as **OW-6** in Appendix B and is, in our judgement, the most
serious reproducibility defect in the present state of the work.

| Claim | § | Cited source |
|---|---|---|
| All safety rates, intervals and per-process figures | 6.3 | `results.json → b2.conditions[1]` |
| Ablation figures | 6.4 | `results.json → b2.conditions[2]` |
| Refusal calibration | 6.5 | `results.json → b3.results` |
| Ambivalence, pre- and post-fix | 6.6 | `experiment_ambivalence.json`; pre-fix recorded in Session 8 |
| Separation sweep and supervised baseline | 6.7 | Session 13 adversarial review |
| Inquiry regret | 4.3 | `results.json → b4.conditions` |
| Median-split parity across 20 conditions | 8 | `results.json → b1.cells` |
| Calibration ECE and AUC | 8 | `v030_vs_v040.json` |
| Identifiability and offset pooling | 8 | `experiment_d23.json`; soft-EM figures from Session 12 |
| Belief-ledger and prototype complexity ratios | 9 | `test_operator_correspondence.py` timing harness |
| Mutation score and survivor distribution | 10.2 | Session 17 mutation run |
| Prototype conformance 4/7 | 5.4 | `conformance_v10.py` |

**Reconciliation note.** Where the two source papers and the current package disagree, this draft
follows the package and says so. Four figures were superseded after the papers were drafted: the
write-then-consult path is no longer quadratic (§9); the identifiability estimator now uses soft
assignment and refuses below three topics (§8); the consent ledger and withdrawal receipt now exist
(§7.2); and the deployment gate now exists (§7.3), moving the enforcement ratio from five of twelve
to **six of twelve** (§7.4). The papers in `papers/` still carry the pre-Session-12 values. This is
recorded as **OW-7** in Appendix B.

To reproduce what can be reproduced:

```bash
pytest -q                 # 707 passed, 2 xfailed
python verify_claims.py   # writes verify_claims_output.json
python demo.py
```

---

## Appendix B — Outstanding work

*This appendix is deliberately separate, and it is the appendix a reader should check before
believing anything above.*

It has three parts. **B.1** lists what has no available substitute — the rule applied is that an item
appears only if an active hunt for a public dataset, a free instrument, a third-party service or a
methodological substitute came back empty. **B.2** lists what a search *resolved*, so that B.1 reads
as the residue of a search rather than as its whole. **B.3** lists ordinary unfinished work, which is
excluded from B.1 on purpose because none of it is blocked on anything external.

### B.1 Blocked: no available substitute

**OW-1 · The threat-confound claim requires primary data collection.**
Approximately forty public datasets were assessed across affective computing, approach-avoidance
paradigms, ecological momentary assessment, experimental economics and social conformity. The claim
needs four things measured on the same person and the same item: a stated stance, a behavioural choice
that can contradict it, an arousal channel time-locked to that choice, and a coercion manipulation.
That intersection does not exist publicly. The failure is structural rather than incidental — corpora
with good physiology are passive-viewing paradigms in which nothing can contradict a rating, and
corpora with real choice lack autonomic recording, self-report, or both. Two published studies used
almost exactly the right design and deposited no data. **No workaround exists. Only collection.**

**OW-2 · No instrument in the battery is validated in an Egyptian sample.**
Arabic validations were confirmed for Lebanese, Saudi, Omani, Jordanian, Palestinian, Qatari and
Moroccan samples. None is Egyptian. Four candidate Egyptian-journal papers were identified by DOI, but
every `*.ekb.eg` host was unreachable, so their contents are unknown — and Egyptian psychometric
papers frequently construct local instruments rather than translating Western ones, so their relevance
cannot be assumed. Any use of this battery in Egypt is first-in-population work and must be described
as such. **Partially resolvable by a colleague with Egyptian institutional access; not resolvable by
open search.**

**OW-3 · Two instrument constructs have no free replacement.**
There is no openly licensed eight-theme Eriksonian inventory: the two structurally correct candidates
are both permission-gated, and going upstream from one to the other does not escape the gate. The best
free material covers two of eight themes and yields single scores rather than subscales. For purpose
beyond the Meaning in Life Questionnaire, no free substitute was identified. **Resolvable only by
author permission, which is a letter, not a search.**

**OW-4 · No party outside this project has executed the software.**
This was the largest risk identified by the programme's own adversarial review. The venue route is
closed: neither ACM TiiS, nor ACM FAccT, nor AAAI/ACM AIES operates an artifact-evaluation or badging
track an author can enter at submission time. Archival deposit satisfies an availability criterion but
verifies no execution. Two replication communities publish work written *by* the replicator and
therefore cannot be pointed at an artifact. One community code-check service matches the need exactly
and has **not been used**. The claim in this work is that the code is inspectable, not that it has
been independently run.

**OW-5 · Invariants X and XI are syntactic proxies for semantic properties.**
Invariant X detects verdict phrasing by pattern, and the question generator is guarded against
prescriptive drift by a keyword test. Both raise a floor and neither measures the property. We know of
no decision procedure that settles whether a sentence claims authority over a person, and we do not
think one follows from more patterns. This is a research problem rather than an unfinished task.

### B.2 Newly identified while preparing this draft

**OW-6 · The benchmark scripts and their outputs are not in the archive. [blocking for submission]**
Both source papers state that every number is produced by a named script a reviewer can run. As
assembled, the archive contains the package, the papers, the session reports and the submission
material — but **not** `run_benchmarks.py`, `conformance_v10.py`, `experiment_d23.py`,
`experiment_ambivalence.py`, `analyze_v030_vs_v040.py`, `make_paper_figures.py`, `results.json` or
`v030_vs_v040.json`. Every headline safety figure in §6, the calibration and identifiability figures
in §8, and the conformance comparison in §5.4 therefore cannot be re-derived from what is on hand.
The figures under `papers/figures/` exist but their generator does not.
**Action:** locate these files in the working environment that produced them and commit them, or
regenerate and re-verify every number they support before submission. Until then the availability
statement in the Ethics section overclaims.

**OW-7 · The two source papers carry pre-Session-12 figures. [blocking for submission]**
P1 §7 still reports the write-then-consult path as quadratic (3.8× per doubling, 1121 ms at 800
pairs); P2 §9 repeats it. P1 §8 reports identifiability at δ = 0.45 with eight topics as 61.3%, from
the superseded hard-assignment estimator. P2 §8 reports that no append-only consent record exists and
that no deployment-context mechanism has been implemented, and prints an enforcement ratio of five of
twelve. All four were superseded by Session 12 and are corrected in this unified draft.
**Action:** propagate the corrections into `P1_ACM_TiiS_draft.md` and `P2_AIES_FAccT_draft.md`, or
withdraw those files in favour of this one. Submitting either paper as it stands would publish four
figures the authors know to be stale.

**OW-8 · Test-count drift across documents.**
The archive README reports 707 passing; P1 reports 673 collected and 671 passing with a 563-invariant
breakdown; Session 12 reports 324. The first is correct for v1.3.0 and was reproduced here. The
per-category breakdown in P1 §3.6 has not been recomputed for the current suite, so this draft does
not restate it.
**Action:** recompute the breakdown from `pytest --collect-only` and state it once, in one place.

**OW-9 · Nine reference-list entries sit outside the verified set.**
`bibliography.json` records 105 manuscript references verified in Session 14 and reports
`entries_without_resolvable_identifier: 0`. The papers' reference lists are longer: P1 lists 58 and 55
are in the verified set; P2 lists 56 and 50 are. The nine remaining entries are six unique psychometric
instrument sources, all introduced in Session 15 — after the verification pass — and never folded into
it. They are marked † in the reference list above. This is not a claim that any is wrong, but under
ground rule 6 they are unconfirmed.
**Action:** verify the six and update `counts`, or mark them explicitly as pending.

### B.3 Ordinary unfinished work

Excluded from B.1 on purpose: none of it is blocked on anything external, and listing it there would
dilute a list whose value is that every entry has been searched for and not found.

| Item | Status |
|---|---|
| Causal reflection operator | Declared gap, strict `xfail`. No do-operator exists |
| Knowledge consolidation operator | Declared gap, strict `xfail`. No promotion criterion exists |
| Read path still O(n) per consultation | Open. Anchored-decay accumulators would fix it |
| 1,549 surviving mutants | Open. Concentrated in engine, patterns, invariant checks, formation |
| 909 mutants in an untested CLI | Open. Carries no claim in any paper |
| Candidate belief state for monotonic drift | Proposal ("your position moved steadily"), computed and discarded |
| Conformal calibration for credible sets | Blocked on labelled outcomes, i.e. on a human study |
| Encryption at rest, multimodal acquisition, event-queue execution engine, any GUI | Specified, unimplemented |

### B.4 Before submission

| Item | Who can close it |
|---|---|
| Corresponding email, and a department if one applies | **You.** The only gap in the author block |
| Repository URL in both availability statements | **You** |
| Venue selection for the ethics paper (AIES or FAccT) | **You.** Check current calls; dates move annually |
| OW-6 and OW-7 above | Whoever holds the working environment that produced `results.json` |
| Three dataset downloads for the secondary-analysis route | Mechanical; two are small |
| Urban Appraisal rating polarity | From the BeMoBIL analysis code. The loader refuses until supplied |
| Two instrument permissions (Claremont Purpose Scale; MEPSI) | Letters to the instrument authors |
| CITI certification and a supervisor | Only if the primary study proceeds |

### B.5 What would change the conclusions

Stated so that a reader knows what evidence would move this work rather than merely extend it.

1. **A human-subjects study.** Objective O4 is unanswered. Every claim about reflection, comprehension
   or trust is currently a design intention with no evidence, and a null result would be a finding.
2. **Primary collection on the four-way intersection (OW-1).** The safety result is a property of a
   simulator that encodes our own theory. Real data could refute the ordering of methods, not merely
   its magnitude.
3. **A third party running the conformance suite against a different substrate (OW-4).** Until then,
   "decidable" is demonstrated and "decidable usefully" is not.
4. **A decision procedure for semantic authority (OW-5).** Invariants X and XI currently raise a floor
   they cannot measure.
