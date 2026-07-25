# Refusal as a Safety Mechanism: Consent-Gated Reflective Inference and the Threat Confound

**Omar Moawad**
*The American University in Cairo, AUC Avenue, P.O. Box 74, New Cairo 11835, Egypt*
*[CORRESPONDING EMAIL — TO BE COMPLETED]*

Submitted to *[AIES / FAccT — select before submission; see §11]*

---

## Abstract

Systems that infer what a person "really" wants from the gap between what they say and what they do
face a hazard that is rarely named and, so far as we have been able to establish, has not previously
been quantified: the same surface contradiction is produced both by a hidden preference and by a
threat response. Telling someone they
secretly want something they are afraid of is a specific, foreseeable harm, and no published
affect-aware architecture reports its rate.

We present Shadow Mirror, a consent-gated reflective architecture in which refusal is a first-class
output, contradiction is held open rather than resolved, and a threat response is represented as a
competing hypothesis rather than treated as noise. We evaluate it in simulation against five
generative processes with known latent mechanisms, two of which produce identical stated aversion by
different routes.

Shadow Mirror misreads a threat response as a hidden desire in **0 of 800 episodes**
(point estimate 0.0%; 95% upper bound 0.37% by the rule of three [45]), against **42.9%** [39.5, 46.2] for
a stated-versus-behaviour mismatch heuristic and **75.1%** [72.1, 78.1] for a baseline that admits
physiological arousal into the action channel. A supervised four-channel classifier, given
ground-truth labels our system never sees, matches 0.0% where the confound channels are informative
and beats us in the mid-separation regime; we report that comparison in full (§6.5). Guard sensitivity is 100.0% [100.0, 100.0] and
specificity 94.4% [93.2, 95.7]. The protection is not free: sensitivity to genuine hidden preference
falls from 100.0% to 87.1% [84.9, 89.4], concentrated entirely in high-arousal approach.

An ablation exposes a dependency we report as a design requirement rather than a result. With the
avoidance channel unobserved — a common deployment condition — guard sensitivity in a system that
imputes the missing channel as zero falls to 0.0% and the misreading rate rises to 31.2%
[28.1, 34.4]. We show that treating an absent channel as absent, rather than as evidence of safety,
restores sensitivity to 100.0% at the cost of 33 points of specificity, and argue that a reflective
system must refuse under partial observation rather than degrade silently.

We close with a tension we cannot resolve. The physiological channel exists only to protect people
and demonstrably does so, and it is precisely what brings the system within the EU AI Act's
definition of an emotion recognition system (Art. 3(34), 3(39)) and therefore within the Art. 5(1)(f)
prohibition on emotion inference in workplaces and education institutions. Removing it removes the
legal exposure and reinstates the harm.

**This system is a research instrument. It is not a diagnostic device and is not suitable for
clinical, educational, employment or other high-stakes deployment.**

**Keywords:** refusal, abstention, consent, affective inference, threat response, harm measurement,
EU AI Act, human–AI reflection

---

## 1. Introduction

A large class of deployed systems infers preference from behavioural inconsistency. Recommender
systems treat repeated engagement as revealed preference regardless of stated intent. Implicit-measure
tools treat reaction-time asymmetries as leanings a person will not admit. Affect-aware interfaces
treat physiological arousal as intensity of wanting. In each case the inference has the same
structure: *you say one thing, you do another, therefore the second is the truth about you.*

That inference has a failure mode with an established literature in clinical and evolutionary
psychology [34–37] and no name at all in machine learning.
Approach under stated reluctance is produced by hidden preference. It is also produced by threat:
by compliance — by the specific pattern in which a person moves toward something because
moving away is unsafe. Arousal is produced by excitement. It is also produced by fear.

The two are not distinguishable from the surface signal. They are distinguishable only with evidence
that many deployments do not collect, and the cost of confusing them is asymmetric. Reading a hidden
preference as a threat response wastes an opportunity. Reading a threat response as a hidden
preference tells a person that their fear was a want — which is, precisely, the thing that a person
recovering from coercion has most often already been told.

This paper does three things.

1. **It measures the harm.** We construct generative processes with known latent mechanisms and
   report the rate at which a system misreads threat as desire — for our architecture and for two
   baselines that reflect current practice. We are not aware of a prior published rate for this
   error.
2. **It shows that refusal removes it.** Conditioning the hidden-preference reading on the evidence
   required to exclude a threat response reduces the misreading rate to zero, and we report the
   sensitivity and specificity this costs.
3. **It reports a regulatory tension it cannot resolve.** The mechanism that provides the protection
   is also what places the system inside a prohibition designed to prevent a different harm.

Contribution 1 is the one we would defend most strongly. Design proposals in this space are
plentiful; measured harm rates are not.

---

## 2. Related work

### 2.1 Abstention, selective prediction, and deferral

Declining to answer has a long formal history. Chow [15] gave the optimal error–reject tradeoff for a
classifier permitted to abstain; El-Yaniv and Wiener [16] laid the modern foundations of selective
classification; Geifman and El-Yaniv extended it to deep networks [17] and then built the reject
option into the architecture itself [18]. Confidence-based rejection at the softmax [19] remains the
standard baseline, and it is only as good as the confidence, which is why calibration [20, 21] is
inseparable from abstention. A parallel literature asks not merely whether to answer but to *whom* to
hand the case: learning to defer [22, 23] and the triage view of human effort [24]. Conformal
prediction [25, 26, 27] supplies distribution-free coverage guarantees for the set-valued outputs that
abstention naturally produces, and Kompa et al. [28] argue the clinical case for communicating that a
second opinion is needed.

Our refusal is a different object, and the distinction is the paper's design claim. Every mechanism
above abstains because a *confidence* is low — the model is unsure, so it declines, and the threshold
is a tunable knob trading coverage against accuracy. Our guard abstains because a *specific
alternative explanation cannot be ruled out with the evidence that was collected*. It is not tunable
by a confidence parameter, it does not move when the model becomes more certain, and it fires just as
readily on a high-confidence reading. A selective classifier asks "how sure am I?"; the guard asks
"which question was never asked?" §6.3 reports what that buys and what it costs — including a
specificity cost we do not hide.

### 2.2 Affect inference and its limits

Affective computing as a field dates to Picard [29]. Its central empirical caution is now well
established: Barrett et al. [6] show in an extensive review that emotion cannot be reliably inferred
from facial movement, and Gendron et al. [7] that emotion perception is not culturally universal.
Calvo and D'Mello [8] survey the methods and their uncertainty.

The ethical critique has kept pace. Stark and Hoey [30] examine the value commitments buried in
emotion-AI systems' choice of emotion model; Andalibi and Buss [31] find that people subject to
emotion recognition on social media see risks the deploying platforms do not; Roemmich et al. [32]
show how emotion-AI hiring services frame organisational problems as technical ones amenable to
inference about applicants' inner states.

We treat affective signals as one evidence channel with declared uncertainty and never as a
characterisation of an inner state — and §7 argues that even this restrained use falls inside the EU
AI Act's definition of an emotion recognition system, which is a problem for us rather than a defence.

### 2.3 Threat responses, and the vocabulary we borrow

The mechanism this paper is designed to detect — a person complying with something they do not want,
under perceived threat — has an established clinical and evolutionary literature. Bracha [34] sets out
the acute stress response as a spectrum rather than the textbook fight-or-flight dichotomy, adding
freeze and fright. Marx et al. [35] review tonic immobility as an evolved predator defence and its
implications for how survivors' non-resistance is misread. Cantor and Price [36] give the most direct
antecedent: appeasement as an evolved response to traumatic entrapment, spanning hostage reactions
and domestic abuse. Gilbert [37] situates submissive behaviour within social competition and
hierarchy.

We are deliberately explicit about one term. The word "fawn", widely used for the appeasement
response, does not originate in the peer-reviewed clinical literature: its popular source is Walker
[38], a self-published practitioner trade book, and we could locate no refereed source that
establishes it as a validated construct. We therefore do not use "fawn" as a clinical category. Where
this paper says *threat compliance*, it names a pattern that our generative process encodes and our
guard is designed to refuse to overwrite — nothing more. The peer-reviewed constructs above [34–37]
describe phenomena in the same region, and we cite them to locate the concern, not to claim our
simulation instantiates any of them. §9 restates this as a limitation, because a reader could
reasonably conclude we have borrowed more authority than we have earned.

### 2.4 Trauma-informed computing, and technology-facilitated harm

Chen et al. [33] set out trauma-informed computing as a design orientation, arguing that systems
should assume trauma may be present rather than treating it as an edge case. Freed et al. [43]
document how intimate partner abusers exploit everyday technology, which is the concrete deployment
context in which a system that confidently announces a person's hidden desires becomes an instrument.
Our safety argument is downstream of both: the harm we measure is not a wrong prediction in the
abstract but a system telling a person that their compliance under pressure was really their own
wish.

### 2.5 Belief revision, human and formal

Bayesian conditioning on conditionally independent observations is commutative [3]; human revision is
neither commutative nor minimal, being explanation-guided and order-sensitive [4, 5]. We take the
first as a constraint on the arithmetic and the second as a reason to hold contradiction open rather
than resolve it.

### 2.6 Uncertainty, explanation, and reliance

Schäfer et al. [1] show that displaying uncertainty does not by itself produce calibrated reliance;
Rosenbacke et al. [2] find in systematic review that explainability can *decrease* clinician trust
calibration as easily as increase it. Both inform our position that the honest output of a reflective
system is frequently a refusal rather than a better-hedged answer.

### 2.7 Consent, contextual integrity, and the gap between form and substance

Budin-Ljøsne et al. [12] and Kaye et al. [39] set out dynamic consent: granular, revocable and
purpose-locked, designed for exactly the intensive longitudinal collection our system performs. Our
ledger (§8) implements that standard and we report where it falls short.

Three critiques bound what any such mechanism can claim. Nissenbaum [40] argues that privacy is
governed by norms of information flow appropriate to a context, so that a consent obtained in one
context does not license a flow into another. Solove [41] argues that privacy self-management does not
scale — that consent transactions are too numerous and too consequentially opaque for individuals to
manage meaningfully. Nouwens et al. [42] show empirically that post-GDPR consent interfaces are
routinely engineered to produce agreement rather than to elicit it. Wachter and Mittelstadt [44] argue
for a right to reasonable inferences, on the ground that data protection law regulates the inputs to
inference far more tightly than its outputs — which is precisely the gap a system that infers desire
from behaviour occupies.

We take these seriously enough to report an enforcement ratio rather than a consent rate (§8): the
question is not how many people agreed but how many refusals the mechanism actually produced.

### 2.8 Metacognitive architectures

Recent work embeds reflection inside the model: metacognitive reuse [9], meta-memory [10], grounded
metacognitive reasoning [11]. Those systems improve what a model knows about its own reasoning. This
paper concerns what a system is willing to tell a person about *themselves*, which is a different
problem with a different failure mode: being confidently wrong about a model's own chain of thought
costs accuracy, while being confidently wrong about a person's motives costs them something else.

---

## 3. The harm, stated precisely

Consider a person who states that they do not want something.

Five mechanisms can produce that statement together with the behaviour that follows. Three of them
are genuine preferences. Two are not:

| Mechanism | Stated | Behaviour | Arousal | Avoidance | Is it a preference? |
|---|---|---|---|---|---|
| Explicit aversion | low | withdraws | low | low | yes — they do not want it |
| Latent approach | low | approaches | low | low | yes — they want it and have not said so |
| Latent approach, aroused | low | approaches | **high** | low | yes — excitement |
| Threat response | low | withdraws | **high** | **high** | **no** — fear |
| Threat compliance | low | **approaches** | **high** | moderate | **no** — complies under threat |

The fifth row is the dangerous one. **Threat compliance and latent approach are indistinguishable on
the stated and behavioural channels alone.** Both show stated aversion and approach behaviour. A
system that reads only those two channels — which describes most deployed preference inference —
cannot tell them apart, and will call the compliance case a hidden want.

The third and fourth rows are the second trap. Excitement and fear both raise arousal. A system that
treats arousal as intensity-of-wanting will call the threat case a strong want.

We take as our target metric the rate at which a system outputs `latent_approach` — "you want this
even though you say you don't" — when the true generating mechanism was a threat process. We call it
the **false hidden-desire rate**.

---

## 4. Design

Four commitments, each with a code-level enforcement point.

**C1. Refusal is a first-class output.** The system emits `unresolved_approach` — a named state, not
a low-confidence label — when behaviour approaches under stated reluctance and the evidence needed to
exclude a threat response was not collected. It also refuses entirely below a minimum of paired
evidence.

**C2. Absent is not zero.** An unobserved channel is recorded as unobserved. It is never imputed to a
value, because imputing arousal or avoidance to zero is imputing *evidence of safety*. §6.2 measures
what happens when this commitment is dropped.

**C3. Threat is a competing hypothesis, not a filter.** `threat_response` occupies the same
hypothesis space as the preference readings and is scored against them, rather than being applied as
a post-hoc suppression rule.

**C4. Contradiction is held, not resolved.** Supporting and contradicting evidence are both retained
as typed edges; a hypothesis carrying both is reported as contested rather than collapsed to the
later write. Belief accumulates in log-odds so that revision is order-invariant and exactly
retractable — clamping the state destroys retractability, and a system that cannot undo an inference
cannot honour a withdrawal of consent.

The output is a distribution over named states with an explicit uncertainty, or a refusal. There is
no scalar score anywhere in the API.

---

### 4.4 A request the architecture declines

Everything reported so far concerns a threat confound we generated. This section reports a refusal that
was not generated: a real request, from the person who commissioned this work, declined for stated
reasons that a reader can check by running the code.

**The request.** To add a feature that would "determine and understand who people probably are according
to their will, desire and need — where they come from, how mature they are, what they still need to be
mature enough, what their eventual purpose probably is". It arrived with a qualification: *"I would not
say judge people."*

That qualification did most of the work. It signals an intuition that something in the request was
wrong without identifying which part, and the architecture's job here was to make the split legible
rather than to accept or refuse wholesale.

**The split.** Five asks, separating on whether a validated construct exists and who supplies it.

| Ask | Disposition | Ground |
|---|---|---|
| will, desire, need | **built** | validated self-report exists; the person supplies it |
| where they come from | **declared only** | inference of special-category data (GDPR Art. 9; PDPL Art. 1); on biometric input, prohibited by AI Act Art. 5(1)(g) |
| how mature they are | **refused as a rank** | the rank is the construct, not a summary of it |
| what they still need | **refused** | a directive about identity |
| eventual purpose | **refused** | no validated construct exists; any output would be invented |

The maturity row is the one that took work. We looked for an honest way to report a developmental
construct without collapsing a person into a single number, and found that the instruments which measure
it will not permit that. Loevinger's sentence completion test [51] yields a Total Protocol Rating; Kegan's
subject-object interview [52] yields one position on one ordered scale, defended in writing;
Cook-Greuter's MAP reports a "Center of Gravity" (we located no independent peer-reviewed validation
of the current instrument). In each the ordered position *is* the theory's claim, so a profile
drawn from one would misrepresent it. We therefore dropped the construct rather than softening it, and
substituted instruments that never claimed a stage — Ardelt's three-dimensional wisdom scale [53], whose
own published criterion is conjunctive across dimensions rather than aggregate, and the Modified Erikson
Psychosocial Stage Inventory [54], which measures attributes *associated with* stages rather than
attainment of them.

**What replaces the refused asks.** Not silence. "What do they still need" becomes `open_questions()`,
which returns what the model does not know, phrased as invitations — and is guarded by a test that fails
if the phrasing drifts into *lack*, *deficit*, *should* or *must*. "Their eventual purpose" becomes the
person's own answers to the Meaning in Life Questionnaire [55], which measures presence of and search
for meaning; needs are measured by the Basic Psychological Need Satisfaction and Frustration Scale [56]. The distinction is not cosmetic: one reports what the person said, the other tells them what
they are for.

**Two commitments that cost functionality.** No item text ships with the software; the registry carries
scoring rules, citations, licence status and caveats, and the researcher supplies the licensed
instrument. And an unconfirmed licence is a refusal rather than a warning — of six otherwise usable
instruments, only two carry quoted published permission statements, so the other four cannot be
administered until written permission is on file. Confirming permission requires written evidence of who
granted it and when, not a boolean, for the same reason the safety exception in §4 does.

**Why this belongs in a paper about refusal.** The safety result of §6.1 measures a refusal we designed
against a confound we simulated. This one was demanded by a real person, and the architecture's answer
was to decline four fifths of it and say why in terms the person can read. A reviewer sceptical that our
refusals are load-bearing rather than decorative can run `check_xi_declared_only` against a model in
which the refusal has been removed, and watch it fail.

## 5. Method

**Generative processes.** Five processes, defined by target values on four channels (stated, action,
arousal, avoidance), with observations drawn from Beta distributions around those targets. Ground
truth is the generating process, which exists independently of the inference model.

**Misspecification control.** The inference model assumes each latent state sits at a fixed corner of
a signal space. Generating from exactly those corners would test self-consistency rather than
validity, so every generating centre is displaced by δ in a random direction. We report δ = 0.00 and
δ = 0.10.

**Baselines**, both implemented and executed at benchmark time:

- **Mismatch-only** — stated versus behaviour, no confound channels. Represents systems that infer
  preference from behavioural inconsistency alone.
- **Arousal-as-desire** — folds physiological arousal into the action channel. Not a straw man:
  treating autonomic arousal as an approach signal is documented practice in affect-aware systems.

**Statistics.** *n* = 400 episodes per process per condition, 6 observation rounds each. All rates
carry 2,000-resample percentile bootstrap intervals [46]. The suite is deterministic: two full runs
produce byte-identical output.

**What is not measured.** No human participants were involved at any stage. Every result below is a
statement about simulated signal streams with known generating mechanisms, and none is a statement
about people. [NO DATA YET — human evaluation]

---

## 6. Results

### 6.1 The safety result

δ = 0.10, both confound channels observed, *n* = 400 per process:

| Method | **False hidden-desire rate** | True hidden preference detected |
|---|---|---|
| **Shadow Mirror** | **0.0% [0.0, 0.0]** | 87.1% [84.9, 89.4] |
| Mismatch-only baseline | 42.9% [39.5, 46.2] | 100.0% [100.0, 100.0] |
| Arousal-as-desire baseline | 75.1% [72.1, 78.1] | 89.5% [87.4, 91.8] |

Guard sensitivity 100.0% [100.0, 100.0]; specificity 94.4% [93.2, 95.7]; AUC of the threat score
across all five processes 1.000. At δ = 0.00 the figures are 0.0% [0.0, 0.0], 47.4% [44.0, 50.9] and
75.8% [72.8, 78.6], with specificity 97.4% [96.5, 98.3].

Per process, δ = 0.10, the false hidden-desire rate:

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
of the time, where excitement is mistaken for fear. Approximately 13 points of sensitivity buys the
elimination of the misreading. We regard that as the correct side of the trade for an instrument that
hands its output to a person about themselves, but it is a trade and not a free lunch.

### 6.2 The ablation: what "absent is not zero" is worth

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

Imputing a missing channel to zero is imputing evidence of *safety*, and it silently disables the
guard: sensitivity falls to zero and the compliance case is misread 62.5% of the time, with nothing
in the output indicating that the protection is inactive.

Recording it as absent produces the opposite failure and the better one. The system stops asserting
hidden preference entirely — sensitivity to genuine preference goes to zero because it declines to
make the call — and specificity falls to 67.0% because arousal alone cannot separate fear from
excitement (AUC 0.835), so the caution fires on excitement too.

**This is the paper's central design claim.** Under partial observation a reflective system should
refuse, not degrade; and the refusal must be visible in the output, not implicit in a number that
happens to be low.

### 6.3 Refusal calibration

Refusal is only defensible if it is calibrated. *n* = 300 per condition:

| Condition | Behaviour |
|---|---|
| Evidence genuinely insufficient | refuses **100.0% [100.0, 100.0]** |
| Evidence sufficient and clear | over-refuses **0.0% [0.0, 0.0]** |
| Evidence ample but ambiguous | does not refuse; reports uncertainty **0.405 [0.391, 0.419]** against **0.021 [0.020, 0.021]** on clear evidence |
| Evidence present but expired (decade-old, 30-day half-life) | infers **0.0% [0.0, 0.0]** of the time |

The system refuses when it should, does not refuse when it should not, and separates ambiguous from
clear evidence by a factor of nineteen in reported uncertainty.

### 6.4 Two supporting results

**Ambivalence is a state, not a residual.** "You want and do not want this at once" is a claim about a
person. Computed from dispersion alone it fires on anything spread out: 95.5% of pure measurement
noise and 98.8% of monotonic drift — that is, of someone who has *made up their mind* — read as
ambivalence, for a precision of 34.0%. Gating on lag-1 autocorrelation, which distinguishes
alternation (−0.844) from drift (+0.517) and noise (−0.120) where dispersion cannot (0.357 / 0.245 /
0.257), raises precision to **97.6%** with recall unchanged at 100.0%.

**Inquiry is information-driven.** When the system asks for more evidence, it selects the observation
that would most reduce uncertainty. Normalised regret against an information-theoretic oracle is
**0.161 [0.138, 0.187]** with a belief-gap heuristic at 0.579 [0.547, 0.612] and random selection at
0.550 [0.515, 0.584] — the heuristic being indistinguishable from random.

### 6.5 Adversarial robustness: two checks a sceptical reader should demand

Two objections are strong enough that answering them in prose would be evasive.

**"Your simulator is your theory."** The generative processes were defined so that threat and
approach differ on arousal and avoidance, and the guard keys on arousal and avoidance. A 0.0% rate
under those conditions risks being a tautology, and the AUC of 1.000 is the tell. So we swept the
*separation* between the two processes on the confound channels, from full (as in §6.1) to none, at
*n* = 300 per process per level.

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

**"Your baselines are straw men."** They partly were. Mismatch-only ignores channels that are
available; arousal-as-desire is a mistake rather than a method. The table above therefore adds a
baseline a competent engineer would build: a threshold classifier over the same four channels, with
its threshold **fitted on a held-out labelled split**.

It matches us at high separation and **beats us at separation 0.25 — 5.0% against our 29.7%.** We
report this because it is true and because the reason matters: our guard uses a fixed, pre-specified
threshold, while the classifier was handed ground-truth labels for "was this a threat response".

**Those labels do not exist in deployment.** Nobody can tell a running system, for a given person and
episode, which mechanism produced their behaviour; that is the entire difficulty. The supervised
baseline is therefore an *upper bound on what any labelled method could achieve*, not an available
alternative — and the gap between it and our unsupervised guard at separation 0.25 is a real,
quantified cost of not having supervision, which we would rather state than omit.

---

## 7. The regulatory tension

We report this because it is unresolved, and because the shape of it is more general than this system.

The EU AI Act defines biometric data as *"personal data resulting from specific technical processing
relating to the physical, physiological or behavioural characteristics of a natural person"*
(Art. 3(34)) [13]. Unlike GDPR Art. 4(14) [14], **it does not require unique identification**. A heart-rate-like
arousal proxy is therefore biometric data under the Act while identifying nobody.

An *emotion recognition system* is one *"for the purpose of identifying or inferring emotions or
intentions of natural persons on the basis of their biometric data"* (Art. 3(39)). Our guard infers a
threat response — an affective and intentional state — partly on the basis of that arousal channel.

Art. 5(1)(f) prohibits *"the use of AI systems to infer emotions of a natural person in the areas of
workplace and education institutions, except where the use of the AI system is intended to be put in
place or into the market for medical or safety reasons."* Applicable since 2 February 2025.

So: **the channel that exists only to protect people, and that §6.2 shows does protect them, is what
brings the system within a prohibition written to prevent a different harm.** Remove it and the
exposure largely disappears; remove it and the false hidden-desire rate returns to 31.2%.

The safety exception is available and, in our reading, applicable: the channel's sole documented
purpose in code, tests and specification is to prevent a specific measured harm, and it is used for
nothing else. We state that as an argument rather than a conclusion. We are aware of no case law
interpreting the exception for a guard of this kind, and a system whose safety mechanism is itself an
emotion-inference system is a case the Act does not obviously anticipate.

We think this generalises. Any protective mechanism that works by observing more about a person will
sit in tension with rules that limit observation. Naming that tension seems more useful than choosing
a side of it in a paper.

---


### 7.1 A second regime, with no research exemption

The EU analysis above is the one the literature rehearses. It is not the only regime a system like
this must survive, and the contrast is instructive enough to report.

This work is conducted under Egyptian jurisdiction, where two instruments matter. Law No. 214 of 2020
on Clinical Medical Research [47] establishes a national ethics architecture — a Supreme Council,
registered institutional committees, criminal penalties reaching ten years where a participant dies.
It does not reach us. Article 1 defines its subject as studies assessing "therapeutic, pharmaceutical,
surgical, nutritional, preventive or diagnostic interventions", and Article 24 confines lawful
research to entities registered with the Ministry of Health. Behavioural, psychological and computing
research falls outside its scope, a gap noted in the empirical research-ethics literature [49].
Egypt's Supreme Council of Universities issued a national academic-integrity and research-ethics guide
in January 2026 whose third book addresses behavioural and social research committees [50], but it
carries no decree number and no binding-force clause, and whether it reaches private universities is
unspecified. We classify it as guidance rather than law.

Personal Data Protection Law No. 151 of 2020 [48] does reach us, and reaches further than the GDPR in
three respects that matter here. Its definition of personal data expressly includes data determining
"psychological ... identity". Its sensitive-data category (Art. 1) covers "psychological, mental, or
physical health, or genetic, biometric or financial data", and Article 12 prohibits processing that
category without a licence from the Personal Data Protection Centre *in addition to* written explicit
consent, on penalty of imprisonment and a fine up to EGP 5,000,000. And — the point we want to put in
front of this venue — **it contains no scientific-research exemption whatsoever**. The GDPR's research
accommodations at Arts. 5(1)(b), 9(2)(j) and 89 have no Egyptian counterpart. We searched the Arabic
text of both the law and its executive regulations (Ministerial Decree No. 816 of 2025, in force
2 November 2025, with a compliance deadline of 31 October 2026): the words for "research", "studies"
and "university" do not appear. Article 5(6) relaxes purpose limitation for not-for-profit statistical
or educational processing, but it does not disapply consent or the Article 12 licence.

The consequence is worth stating plainly, because it inverts a common assumption. A researcher in a
jurisdiction with a *weaker* national human-subjects law can face a *stricter* data-protection
constraint on exactly the physiological and psychological channels this architecture consumes, with
no research carve-out to fall back on. Our design response is the one already described: refuse the
biometric stream rather than seek a basis for it (§4), and treat anonymisation rather than
pseudonymisation as the only route out of scope, since a linkable participant identifier keeps the
data personal.

**This is a reading of statutory text, not legal advice, and it has not been reviewed by counsel**
(§9). We report it because the fairness literature's regulatory analysis is overwhelmingly EU- and
US-centred, and a system designed only against the regimes that grant research exemptions will be
designed wrong for the places that do not.

## 8. Consent, and the honest enforcement ratio

The system's other-person mode requires granular, per-stream, purpose-locked, revocable consent
before any datum is recorded. Streams a subject cannot notice about themselves — implicit measures,
physiological arousal, micro-avoidance — cannot be granted under a blanket authorisation; each
requires its own acknowledgement. Every stream declares in plain language both what it records and
what it *may reveal*. No grant, no observation: the engine raises rather than records.

Assessed against GDPR Art. 4(11) and Art. 7, the implementation meets five criteria and exceeds two
(unbundleable non-obvious streams, and may-reveal disclosure). It falls short on two: there is no
append-only consent record, so a controller cannot demonstrate what consent was true at a past date
(Art. 7(1)); and withdrawal, while a single command, produces no receipt to the subject (Art. 7(3)
parity). Both are reported here rather than fixed before publication, because the enforcement ratio
is the point.

**That ratio: of twelve documented prohibitions, five are enforced by a mechanism and covered by a
test; seven are policy only.** Among the seven is the one prohibition that is currently unlawful to
breach in the EU — emotion inference in a workplace or education institution — for which no code
mechanism exists. We consider a deployment-context declaration that refuses to enable the
physiological stream in institutional contexts, and we have not implemented it.

We suggest that papers proposing ethical architectures should print this ratio. A list of
prohibitions communicates intent; the fraction of them a machine will actually refuse communicates
the safeguard.

---

## 9. Limitations

**No human subjects.** Nothing here establishes any effect on human reasoning, trust, or wellbeing,
and no such claim is made. [NO DATA YET — human evaluation]

**Simulation is not the world.** Our generative processes encode a theory of how threat and
preference differ in observable signal. If that theory is wrong, the measured rates are wrong in the
same direction for every method compared, including the baselines. We regard the *ordering* of the
methods as more robust than the absolute rates, and §6.5 measures how far that ordering survives as
the theory's key assumption is weakened.

**A point estimate of zero is not a guarantee of zero.** Across 800 threat episodes we observed no
misreadings. The 95% upper bound implied by the rule of three [45] is 0.37%, and that — not 0.0% — is the
number a deployment decision should use.

**The clinical vocabulary is borrowed, and one term is not clinical at all.** We use "compliance"
and "threat response" to name a pattern of approach behaviour under low stated desire and high
arousal. There is a genuine peer-reviewed literature in this region — appeasement under traumatic
entrapment [36], tonic immobility as an evolved defence [35], the acute stress response as a spectrum
rather than a dichotomy [34], submissive behaviour in social hierarchies [37] — and we cite it in §2.3
to locate the concern. We do not claim our generative process instantiates any of those constructs,
and no clinical validation has been performed.

One term deserves separate treatment. The word "fawn" is in wide circulation for the appeasement
response, and we used it in earlier drafts as though it were a clinical category. It is not. We traced
it to Walker [38], a self-published practitioner trade book, and could locate no refereed source
establishing it as a validated construct. We have therefore removed it from every load-bearing claim
in this paper and retain it only where we are explicitly discussing the term's provenance. A reader
who suspects we have borrowed more authority than we have earned is raising the right objection; this
paragraph is our answer, and it concedes most of it.

**We are not lawyers.** §7 sets out our reading of the applicable provisions. It is a reading, it
has not been reviewed by counsel, and it should not be relied on as advice.

**The specificity cost is real.** Under partial observation the system labels excitement as a
possible threat 99.0% of the time. A person who is excited and told to consider whether they are
afraid has been mildly misread. We judge this preferable to the converse and do not claim it is
costless.

**Calibration degrades under severe misspecification.** Where the model's assumed structure
approximately holds, expected calibration error is 0.044 and the reported uncertainty predicts error
with AUC 0.949. Where it does not, ECE rises to 0.221. Reporting a credible set instead of a point
label improves the rate at which the truth is contained in the output (78.2% → 88.0% at δ = 0.30) but
does **not** reach nominal coverage: a set claiming 90% mass contains the truth 60.5% [55.5, 65.2] of
the time at δ = 0.45. A credible set inherits its posterior's miscalibration; reaching nominal
coverage requires conformal calibration against held-out labelled outcomes, which do not exist
without a human study.

**Correlated evidence.** Sequential updating assumes conditional independence, which is frequently
false for repeated self-reports. Contributions are keyed by evidence identity so resubmission cannot
compound, and temporal decay down-weights clustering, but neither substitutes for a
correlated-likelihood model.

**Scale.** The observation intake recomputes the full belief state per observation and is quadratic
(3.8× per doubling; 27 ms at 100 evidence pairs, 1121 ms at 800). This is an engineering limitation,
not a conceptual one, and it is the first optimisation target.

---

### 9.1 Measured, not asserted: how strong the test suite is

We previously stated that nothing measured the test suite's coverage of the state space. Mutation
testing now does. Over 5,114 generated mutants the suite killed 2,319 and 1,549 survived — a
**mutation score of 59.9%** — with a further 1,244 mutants in code carrying no covering test, most of
it an untested command-line interface that supports no claim here.

The survivors are concentrated in the inference engine, the pattern layer and the invariant checks
themselves, and a sampled inspection suggests most are message and label mutations rather than
behavioural ones. One was not: mutating an invariant's own identifier survived, meaning nothing
asserted that a check reports the invariant it claims to be. That is now tested.

We report the number rather than improving it first, because a paper that argues for checkable claims
should publish the check that came back middling.

## 10. Ethics statement

This research did not involve human or animal subjects. All results derive from simulated signal
streams generated from specified processes; no personal data of any kind was collected, processed or
analysed.

The system described is a research instrument. It is not a medical device, not a diagnostic
instrument, and is not suitable for clinical, educational, employment, credit, insurance, policing or
other high-stakes deployment. The prohibited-use list and its enforcement status are given in §8.

The authors note the regulatory position described in §7 and do not assert that the safety exception
under Art. 5(1)(f) applies as a settled matter.

**Data and code availability.** The complete implementation, benchmark suite, experiments and
analysis scripts are released under an open licence. The suite is byte-reproducible: two independent
runs produce identical output. Every number in this paper is produced by a named script and none was
transcribed by hand. *[REPOSITORY URL — TO BE COMPLETED]*

---

## 11. Venue note *(remove before submission)*

Recommended: **AIES** or **FAccT**. The paper's shape — a specific foreseeable harm quantified, a
design commitment that removes it, an honest ablation showing the conditions under which the
protection fails, and an unresolved regulatory tension — matches what those venues reward, and
requires no human subjects. Check current calls for papers before committing; dates move annually.

---

## References

[1] U. Schäfer et al. "'The AI is uncertain, so am I. What now?': Navigating Shortcomings of
Uncertainty Representations in Human-AI Collaboration with Capability-focused Guidance."
*Proc. ACM Hum.-Comput. Interact.*, 2025. DOI: 10.1145/3757451

[2] R. Rosenbacke, Å. Melhus, et al. "How Explainable Artificial Intelligence Can Increase or Decrease
Clinicians' Trust in AI Applications in Health Care: Systematic Review." *JMIR AI*, 1:e53207, 2024.
PMID: 39476365

[3] B. Jacobs. "Commutativity of probabilistic belief revision." *Frontiers in Cognition*, 2025.
DOI: 10.3389/fcogn.2025.1623227

[4] S. L. Vasileiou et al. "How Do People Revise Inconsistent Beliefs? Examining Belief Revision in
Humans with User Studies." arXiv:2506.09977, 2025.

[5] S. L. Vasileiou and W. Yeoh. "Human-Aware Belief Revision: A Cognitively Inspired Framework for
Explanation-Guided Revision of Human Models." arXiv:2405.19238, 2024.

[6] L. F. Barrett, R. Adolphs, S. Marsella, A. M. Martinez, and S. D. Pollak. "Emotional expressions
reconsidered: Challenges to inferring emotion from human facial movements." *Psychological Science in
the Public Interest*, 20(1):1–68, 2019. DOI: 10.1177/1529100619832930

[7] M. Gendron, D. Roberson, J. M. van der Vyver, and L. F. Barrett. "Perceptions of emotion from
facial expressions are not culturally universal." *Emotion*, 14(2):251–262, 2014.
DOI: 10.1037/a0036052

[8] R. A. Calvo and S. D'Mello. "Affect detection: An interdisciplinary review of models, methods, and
their applications." *IEEE Transactions on Affective Computing*, 1(1):18–37, 2010.
DOI: 10.1109/T-AFFC.2010.1

[9] A. Didolkar, N. Ballas, S. Arora, and A. Goyal. "Metacognitive Reuse: Turning Recurring LLM
Reasoning Into Concise Behaviors." arXiv:2509.13237, 2025.

[10] Xin et al. "MetaMem: Evolving Meta-Memory for Knowledge Utilization through Self-Reflective
Symbolic Optimization." *Findings of ACL 2026*. arXiv:2602.11182

[11] A. P. Elenjical, V. H. Kavuri, and V. Varma. "Think2: Grounded Metacognitive Reasoning in Large
Language Models." arXiv:2602.18806, 2026.

[12] I. Budin-Ljøsne et al. "Dynamic consent: A potential solution to some of the challenges of modern
biomedical research." *BMC Medical Ethics*, 18:4, 2017. DOI: 10.1186/s12910-016-0162-9

[13] Regulation (EU) 2024/1689 (Artificial Intelligence Act).
https://eur-lex.europa.eu/eli/reg/2024/1689/oj

[14] Regulation (EU) 2016/679 (General Data Protection Regulation).
https://eur-lex.europa.eu/eli/reg/2016/679/oj

[15] C. K. Chow. "On optimum recognition error and reject tradeoff." *IEEE Transactions on Information
Theory*, 16(1):41–46, 1970. DOI: 10.1109/TIT.1970.1054406

[16] R. El-Yaniv and Y. Wiener. "On the Foundations of Noise-free Selective Classification."
*Journal of Machine Learning Research*, 11(53):1605–1641, 2010.
https://www.jmlr.org/papers/v11/el-yaniv10a.html

[17] Y. Geifman and R. El-Yaniv. "Selective Classification for Deep Neural Networks."
*Advances in Neural Information Processing Systems 30 (NIPS 2017)*.
https://papers.nips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html

[18] Y. Geifman and R. El-Yaniv. "SelectiveNet: A Deep Neural Network with an Integrated Reject
Option." *Proc. 36th International Conference on Machine Learning*, PMLR 97:2151–2159, 2019.
https://proceedings.mlr.press/v97/geifman19a.html

[19] D. Hendrycks and K. Gimpel. "A Baseline for Detecting Misclassified and Out-of-Distribution
Examples in Neural Networks." *ICLR 2017*. arXiv:1610.02136

[20] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger. "On Calibration of Modern Neural Networks."
*Proc. 34th International Conference on Machine Learning*, PMLR 70:1321–1330, 2017.
https://proceedings.mlr.press/v70/guo17a.html

[21] M. Pakdaman Naeini, G. F. Cooper, and M. Hauskrecht. "Obtaining Well Calibrated Probabilities
Using Bayesian Binning." *Proc. AAAI Conference on Artificial Intelligence*, 29(1), 2015.
DOI: 10.1609/aaai.v29i1.9602

[22] D. Madras, T. Pitassi, and R. Zemel. "Predict Responsibly: Improving Fairness and Accuracy by
Learning to Defer." *Advances in Neural Information Processing Systems 31 (NeurIPS 2018)*.
arXiv:1711.06664

[23] H. Mozannar and D. Sontag. "Consistent Estimators for Learning to Defer to an Expert."
*Proc. 37th International Conference on Machine Learning*, PMLR 119:7076–7087, 2020.
https://proceedings.mlr.press/v119/mozannar20b.html

[24] M. Raghu, K. Blumer, G. Corrado, J. Kleinberg, Z. Obermeyer, and S. Mullainathan. "The Algorithmic
Automation Problem: Prediction, Triage, and Human Effort." arXiv:1903.12220, 2019.

[25] V. Vovk, A. Gammerman, and G. Shafer. *Algorithmic Learning in a Random World*. Springer, 2005.
DOI: 10.1007/b106715

[26] A. N. Angelopoulos and S. Bates. "A Gentle Introduction to Conformal Prediction and
Distribution-Free Uncertainty Quantification." arXiv:2107.07511, 2021.

[27] Y. Romano, M. Sesia, and E. J. Candès. "Classification with Valid and Adaptive Coverage."
*Advances in Neural Information Processing Systems 33 (NeurIPS 2020)*, pp. 3581–3591.
https://proceedings.neurips.cc/paper/2020/hash/244edd7e85dc81602b7615cd705545f5-Abstract.html

[28] B. Kompa, J. Snoek, and A. L. Beam. "Second opinion needed: communicating uncertainty in medical
machine learning." *npj Digital Medicine*, 4:4, 2021. DOI: 10.1038/s41746-020-00367-3

[29] R. W. Picard. *Affective Computing*. MIT Press, 1997. ISBN 9780262161701

[30] L. Stark and J. Hoey. "The Ethics of Emotion in Artificial Intelligence Systems."
*Proc. 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21)*, pp. 782–793.
DOI: 10.1145/3442188.3445939

[31] N. Andalibi and J. Buss. "The Human in Emotion Recognition on Social Media: Attitudes, Outcomes,
Risks." *Proc. CHI 2020*, pp. 1–16. DOI: 10.1145/3313831.3376680

[32] K. Roemmich, T. Rosenberg, S. Fan, and N. Andalibi. "Values in Emotion Artificial Intelligence
Hiring Services: Technosolutions to Organizational Problems." *Proc. ACM Hum.-Comput. Interact.*,
7(CSCW1):1–28, 2023. DOI: 10.1145/3579543

[33] J. X. Chen, A. McDonald, Y. Zou, E. Tseng, K. A. Roundy, A. Tamersoy, F. Schaub, T. Ristenpart,
and N. Dell. "Trauma-Informed Computing: Towards Safer Technology Experiences for All."
*Proc. CHI 2022*, pp. 1–20. DOI: 10.1145/3491102.3517475

[34] H. S. Bracha. "Freeze, Flight, Fight, Fright, Faint: Adaptationist Perspectives on the Acute
Stress Response Spectrum." *CNS Spectrums*, 9(9):679–685, 2004. DOI: 10.1017/S1092852900001954

[35] B. P. Marx, J. P. Forsyth, G. G. Gallup, T. Fusé, and J. M. Lexington. "Tonic Immobility as an
Evolved Predator Defense: Implications for Sexual Assault Survivors." *Clinical Psychology: Science
and Practice*, 15(1):74–90, 2008. DOI: 10.1111/j.1468-2850.2008.00112.x

[36] C. Cantor and J. Price. "Traumatic Entrapment, Appeasement and Complex Post-Traumatic Stress
Disorder: Evolutionary Perspectives of Hostage Reactions, Domestic Abuse and the Stockholm Syndrome."
*Australian & New Zealand Journal of Psychiatry*, 41(5):377–384, 2007. DOI: 10.1080/00048670701261178

[37] P. Gilbert. "Evolution and social anxiety: The role of attraction, social competition, and social
hierarchies." *Psychiatric Clinics of North America*, 24(4):723–751, 2001.
DOI: 10.1016/S0193-953X(05)70260-4

[38] P. Walker. *Complex PTSD: From Surviving to Thriving — A Guide and Map for Recovering from
Childhood Trauma*. Azure Coyote Publishing, 2013. ISBN 9781492871842. **Cited as the popular origin of
the term "fawn"; this is a self-published practitioner trade book and is not peer-reviewed academic
literature.** See §2.3.

[39] J. Kaye, E. A. Whitley, D. Lund, M. Morrison, H. Teare, and K. Melham. "Dynamic consent: a
patient interface for twenty-first century research networks." *European Journal of Human Genetics*,
23(2):141–146, 2015. DOI: 10.1038/ejhg.2014.71

[40] H. Nissenbaum. "Privacy as Contextual Integrity." *Washington Law Review*, 79(1):119–157, 2004.
https://digitalcommons.law.uw.edu/wlr/vol79/iss1/10/

[41] D. J. Solove. "Introduction: Privacy Self-Management and the Consent Dilemma." *Harvard Law
Review*, 126(7):1880–1903, 2013.
https://harvardlawreview.org/print/vol-126/introduction-privacy-self-management-and-the-consent-dilemma/

[42] M. Nouwens, I. Liccardi, M. Veale, D. Karger, and L. Kagal. "Dark Patterns after the GDPR:
Scraping Consent Pop-ups and Demonstrating their Influence." *Proc. CHI 2020*, article 194.
DOI: 10.1145/3313831.3376321

[43] D. Freed, J. Palmer, D. Minchala, K. Levy, T. Ristenpart, and N. Dell. "'A Stalker's Paradise':
How Intimate Partner Abusers Exploit Technology." *Proc. CHI 2018*, article 667.
DOI: 10.1145/3173574.3174241

[44] S. Wachter and B. Mittelstadt. "A Right to Reasonable Inferences: Re-Thinking Data Protection Law
in the Age of Big Data and AI." *Columbia Business Law Review*, 2019(2):494–620.
DOI: 10.7916/cblr.v2019i2.3424

[45] J. A. Hanley and A. Lippman-Hand. "If Nothing Goes Wrong, Is Everything All Right? Interpreting
Zero Numerators." *JAMA*, 249(13):1743–1745, 1983. DOI: 10.1001/jama.1983.03330370053031

[46] B. Efron and R. J. Tibshirani. *An Introduction to the Bootstrap*. Chapman & Hall, 1993.
ISBN 9780412042317

[47] Law No. 214 of 2020 promulgating the Law Regulating Clinical Medical Research (Egypt), Official
Gazette issue 51 bis (و), 23 December 2020; Executive Regulations, Prime Minister's Decree No. 927 of
2022. https://www.edaegypt.gov.eg/media/zz0alwxy/law-214-of-2020_-to-cairo-legal_.pdf

[48] Law No. 151 of 2020 promulgating the Personal Data Protection Law (Egypt), Official Gazette issue
28 bis (هـ), 15 July 2020, in force 16 October 2020; Executive Regulations, Minister of Communications
and Information Technology Decree No. 816 of 2025, in force 2 November 2025.
Regulator: https://pdpc.gov.eg

[49] M. Matar and H. Silverman. "Ethical Considerations and Challenges of Egypt's New Clinical Research
Law." *Journal of Empirical Research on Human Research Ethics*, 2022.
DOI: 10.1177/15562646221096188

[50] Supreme Council of Universities (Egypt). *Guide to Academic Integrity and Scientific Research
Ethics in Egypt* (دليل النزاهة الأكاديمية وأخلاقيات البحث العلمي في مصر), 26 January 2026.
https://scu.eg/download/guide-to-academic-integrity-and-research-ethics/ *(Guidance; carries no decree
number or binding-force clause. Applicability to private universities unspecified.)*

[51] L. X. Hy and J. Loevinger. *Measuring Ego Development*, 2nd ed. Lawrence Erlbaum, 1996.
ISBN 9781138876552

[52] L. Lahey, E. Souvaine, R. Kegan, R. Goodman, and S. Felix. *A Guide to the Subject-Object
Interview: Its Administration and Interpretation*. Harvard Graduate School of Education, 1988.

[53] M. Ardelt. "Empirical Assessment of a Three-Dimensional Wisdom Scale." *Research on Aging*,
25(3):275–324, 2003. DOI: 10.1177/0164027503025003004

[54] C. S. Darling-Fisher and N. K. Leidy. "Measuring Eriksonian Development in the Adult: The Modified
Erikson Psychosocial Stage Inventory." *Psychological Reports*, 62(3):747–754, 1988.
DOI: 10.2466/pr0.1988.62.3.747

[55] M. F. Steger, P. Frazier, S. Oishi, and M. Kaler. "The Meaning in Life Questionnaire: Assessing the
presence of and search for meaning in life." *Journal of Counseling Psychology*, 53(1):80–93, 2006.
DOI: 10.1037/0022-0167.53.1.80

[56] B. Chen, M. Vansteenkiste, W. Beyers, et al. "Basic psychological need satisfaction, need
frustration, and need strength across four cultures." *Motivation and Emotion*, 39(2):216–236, 2015.
DOI: 10.1007/s11031-014-9450-1

---

## Appendix A — Number provenance

Every figure in this paper, with the script that produces it. No number was transcribed by hand.

| Figure | Source |
|---|---|
| All §6.1 rates and intervals | `results.json → b2.conditions[1]` (δ=0.10, avoidance observed) |
| §6.1 δ=0.00 figures | `results.json → b2.conditions[0]` |
| §6.1 per-process table | `results.json → b2.conditions[1].per_process` |
| All §6.2 ablation figures | `results.json → b2.conditions[2]` (avoidance unobserved) vs. Session 2 baseline run |
| All §6.3 refusal figures | `results.json → b3.results` |
| §6.4 ambivalence, post-fix (2.5%, 0.0%, 100.0%, 97.6%) | `experiment_ambivalence.json` |
| §6.4 ambivalence, **pre-fix** (95.5%, 98.8%, 34.0%) | same script run against the pre-fix engine; recorded in `SESSION_08_CLAIM_MATRIX.md` §1. Reproduce by reverting the `_oscillation_gate` factor in `engine._infer_desire`. |
| §6.4 inquiry regret | `results.json → b4.conditions` |
| §9 calibration and coverage | `v030_vs_v040.json`, `experiment_d23.json` |
| §9 complexity | `test_operator_correspondence.py` timing harness |

Reproduce with:

```bash
pytest -q                        # 671 passed, 2 xfailed
python run_benchmarks.py         # writes results.json
python experiment_ambivalence.py
python experiment_d23.py
python analyze_v030_vs_v040.py
```

---

## Appendix B — Outstanding work with no available substitute

Everything in this appendix was searched for before it was listed. The rule applied was: an item is
only recorded here if an active hunt for a public dataset, a free instrument, a third-party service or
a methodological substitute came back empty. Items that a search *did* resolve are recorded in the
second table, so that a reader can see the difference between what is genuinely blocked and what was
merely inconvenient.

### B.1 What has no substitute

**1. The threat-confound claim requires primary data collection.**
Approximately forty public datasets were assessed across affective computing, approach-avoidance
paradigms, ecological momentary assessment, experimental economics and social conformity. The claim
needs four things measured on the same person and the same item: a stated stance, a behavioural choice
that can contradict it, an arousal channel time-locked to that choice, and a coercion manipulation.
That intersection does not exist publicly. The failure is structural rather than incidental — corpora
with good physiology are passive-viewing paradigms in which nothing can contradict a rating, and
corpora with real choice lack autonomic recording, self-report, or both. Two published studies used
almost exactly the right design and deposited no data. **No workaround exists. Only collection.**

**2. No instrument in the battery has been validated in an Egyptian sample.**
Arabic validations were confirmed for Lebanese, Saudi, Omani, Jordanian, Palestinian, Qatari and
Moroccan samples. None is Egyptian. Four candidate Egyptian-journal papers were identified by DOI, but
every `*.ekb.eg` host was unreachable from our environment, so their contents are unknown — and
Egyptian psychometric papers frequently construct local instruments rather than translating Western
ones, so their relevance cannot be assumed. Any use of this battery in Egypt is first-in-population
work and is described as such. **Partially resolvable by a colleague with Egyptian institutional
access; not resolvable by open search.**

**3. Two instrument constructs have no free replacement.**
A licence hunt found free, published-mapping substitutes for two of the four blocked instruments (see
B.2). It did not for the other two. There is no openly licensed eight-theme Eriksonian
inventory: the two structurally correct candidates are both permission-gated, and going upstream from
one to the other does not escape the gate. The best free material covers two of eight themes and
yields single scores rather than subscales. For purpose beyond the Meaning in Life Questionnaire, no
free substitute was identified. **Resolvable only by author permission, which is a letter, not a
search.**

**4. No party outside this project has executed the software.**
This was the largest risk identified by our own adversarial review, and we searched specifically for
mechanisms that would discharge it. The venue route is closed: neither ACM TiiS, nor ACM FAccT, nor
AAAI/ACM AIES operates an artifact-evaluation or badging track that an author can enter at submission
time. Archival deposit satisfies an availability criterion but verifies no execution. Two replication
communities publish work written *by* the replicator and therefore cannot be pointed at an artifact.
One community service does exist that matches the need exactly, and submitting to it is recorded in
B.2 as an action rather than a limitation — but as of writing it has not been done, and the
claim in this paper is that the code is inspectable, not that it has been independently run.

**5. Two invariants are syntactic proxies for semantic properties.**
Invariant X detects verdict phrasing by pattern, and the accompanying question generator is guarded
against prescriptive drift by a keyword test. Both raise a floor and neither measures the property. We
know of no decision procedure that settles whether a sentence claims authority over a person, and we
do not think one follows from more patterns. This is a research problem rather than an unfinished
task, and we would rather state it than let a passing check imply otherwise.

### B.2 What a search resolved, and how

Recorded so that the list above is read as the residue of a search rather than as its whole.

| Was blocked | Resolved by | Cost of the substitution |
|---|---|---|
| Values instrument permission-gated, item mapping unreachable | The ESS Human Values Scale, whose items and item-to-value mapping are both published, under CC BY-SA documentation terms plus the instrument author's own non-commercial grant — and which has an already-fielded Arabic version | 10 basic values instead of 19 refined, from 2–3 items each |
| Wisdom instrument permission-gated | The revised Adult Self-Transcendence Inventory, CC BY 4.0, whose original author is a named co-licensor, dimensional, and whose authors argue explicitly against a total score | Construct drift: it measures self-transcendence, and has no analogue of the cognitive dimension |
| Harness coverage unmeasured | Mutation testing. Reported in §9 as a measured score with its weakest modules named | None; it replaced an admission with a number and a work list |
| Invariant identity untested | Found *by* the mutation run — mutating an invariant's identifier and name produced surviving mutants — and closed with two tests | None |
| Distribution-free coverage guarantees blocked on labelled outcomes | Available under the secondary-analysis route, where two of the three corpora supply an item-matched choice that can contradict a stated preference | Applies to the preference model only; the safety claim is untouched |
| Independent execution | A community code-check service that accepts submissions on a preprint alone, is free, and issues a citable certificate naming the person who ran the code | Certifies execution, not scientific correctness |

### B.3 What is not in this appendix

Ordinary unfinished work is excluded on purpose: two unimplemented operators recorded as strict
`xfail`s, a read path that remains linear per consultation, a candidate belief state for monotonic
drift, and the surviving mutants named in §9. None of these is blocked on anything external.
They are simply not done, and listing them here would dilute a list whose value is that every entry on
it has been searched for and not found.

