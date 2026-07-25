# Invariants You Can Run: An Executable Specification for Reflective Human–AI Architectures

**Omar Moawad**
*The American University in Cairo, AUC Avenue, P.O. Box 74, New Cairo 11835, Egypt*
*[CORRESPONDING EMAIL — TO BE COMPLETED]*

Submitted to *ACM Transactions on Interactive Intelligent Systems*

---

## Abstract

Reference architectures for human–AI interaction are usually specified in prose. Their invariants —
traceability, provenance, human authority — read as commitments, and a reader has no way to tell
whether an implementation keeps them. This is not a documentation problem. A property that cannot be
checked cannot be violated *detectably*, and a commitment that cannot be violated detectably is not a
commitment.

We present Shadow Mirror, a reference architecture for reflective human–AI collaboration whose eleven
architectural invariants are **decidable properties with a supplied decision procedure**. Each is a
callable check returning a verdict and the observation that produced it. Invariants I–X hold across 200
randomised well-formed reflective states and Invariant XI across 200 randomised formation models, and
each is paired with a negative test constructing a state that violates it — because a conformance check
that only ever passes is indistinguishable from one that does nothing. The suite is 673 tests, of which
563 are invariant checks.

Three architectural components carry the invariants. The **Unified Reflective Graph** holds
observations, evidence, context, hypotheses, inquiries and explanations in one typed structure with
multi-parent provenance closure and contradiction as a first-class edge. **Belief revision**
accumulates in log-odds keyed by evidence identity, making it order-invariant across all 120
permutations of a five-observation sequence and exactly retractable — a prototype that clamped the
posterior in state produced final beliefs of 0.0396 or 0.9900 for the same evidence depending on
arrival order. **Inquiry planning** maximises expected information gain, achieving normalised regret
0.161 [0.138, 0.187] against an information-theoretic oracle where a belief-gap heuristic scores
0.579 [0.547, 0.612] against random selection's 0.550 [0.515, 0.584].

We report complexity as measurement rather than assertion, and we are explicit about what the
architecture does *not* buy: on latent-state recovery the graph-backed inference is statistically
indistinguishable from a median split across all 20 tested conditions. The contribution is
structural — traceability, provenance, retained contradiction, decidable conformance — and we claim
nothing beyond it. Two specified operators, causal reflection and knowledge consolidation, are
implemented nowhere and are carried as declared gaps rather than omitted.

**This system is a research instrument. It is not suitable for clinical, educational, employment or
other high-stakes deployment.**

**CCS Concepts:** Human-centered computing → Interactive systems and tools; Computing methodologies →
Reasoning about belief and knowledge; Software and its engineering → Software verification.

**Keywords:** reference architecture, executable specification, architectural invariants, provenance,
belief revision, expected information gain, conformance testing.

---

## 1. Introduction

Architecture papers make promises. *Every conclusion traces to evidence. Provenance is preserved.
The system does not silently replace human judgment.* These are good promises and they are why
reference architectures are worth writing.

They are also, almost always, unfalsifiable as stated. A reader cannot determine whether an
implementation keeps them, an author cannot determine whether a refactor broke them, and a reviewer
cannot distinguish an architecture that enforces them from one that describes them. When the
architecture is intended to support a person reasoning about themselves, that gap is not academic.

We began from an architecture in the usual condition: ten invariants specified in prose (an eleventh
was added later, for reasons reported in §3.7), with a
prototype whose relationship to them was undocumented. Testing the prototype against its own
invariants found that **Invariant II (Provenance Preservation) was violated** — evidence derived
from two sources reported one parent and silently discarded the other — and that belief revision was
**order-dependent to the tune of 95 percentage points**. Both defects had been present in a
document that asserted the invariants held.

This paper reports what changed when the invariants were made executable.

**Contributions.**

1. **Eleven architectural invariants as decidable properties**, with a supplied decision procedure, a
   randomised property harness, and a negative test per failure mode. The eleventh is unusual and is
   reported in §3.7: it exists because a user asked the architecture for a capability the architecture
   should not have, and it makes the refusal checkable rather than merely stated. (§3)
2. **A reflective graph substrate** with multi-parent provenance closure, contradiction as a
   first-class edge, transactional updates, and no third-party dependencies. (§4)
3. **An order-invariant, exactly retractable belief operator**, with the axioms it satisfies stated
   explicitly and enforced by test. (§5)
4. **Information-gain inquiry planning**, measured against an oracle. (§6)
5. **Complexity as measurement.** Four operator bounds, measured, one of which caught a quadratic
   defect in our own implementation. (§7)
6. **A negative result reported as such**: the architecture buys no accuracy. (§8)

---

## 2. Related work

### 2.1 Architecture, and the gap between description and code

Software architecture has been a first-class object of study since Perry and Wolf [14] named its
elements, form and rationale. The persistent problem is drift: the architecture as described and the
architecture as built diverge, silently, under maintenance. Murphy, Notkin and Sullivan's reflexion
models [15] made that divergence itself computable, mapping a source model onto a high-level model
and reporting convergences, divergences and absences. A substantial literature followed on static
conformance checking — dependency-constraint languages [16], comparative evaluation of checking
approaches [17, 18] — and on recovering an architecture from code when no trustworthy description
survives [19].

That literature is almost entirely concerned with *structural* constraints: which module may depend
on which, whether layering is respected, whether a component sits where the diagram says. Those are
the properties for which a decision procedure is straightforward to write, because they are
properties of the dependency graph. What we attempt is conformance checking for *semantic*
commitments about reasoning — not "does module A avoid importing module B" but "does every
explanation this system produces terminate in evidence the person supplied". We are not aware of a
prior conformance suite that takes reasoning-level commitments as its checked properties. §3.5
reports our first evidence that such checks discriminate between implementations rather than merely
restating one API.

### 2.2 Specification, contracts, and executable properties

The idea that a specification should be machine-checkable rather than prose is old and well served.
Design by contract [20] attaches preconditions, postconditions and invariants to program units.
Formal specification languages — TLA+ [21], Alloy [22] — allow properties to be model-checked against
a design. Runtime verification [23] monitors an executing system against a formal property.
Property-based testing, introduced by QuickCheck [24], generates inputs and checks that stated
properties hold across them, rather than that named cases produce named outputs.

Our invariants borrow the *form* of each of these and match none of them exactly. They are not
contracts, because they are not attached to a unit and not checked at call boundaries. They are not
model checking, because they run against the implementation rather than a model of it. They are
closest to property-based testing, and the harness of §3.2 is a randomised property harness in the
QuickCheck tradition. The difference we claim is one of subject matter rather than technique: the
properties are architectural commitments published *as part of the architecture*, shipped with a
decision procedure and a negative test per property, and intended to be run by a third party against
a *different* implementation. §10 states plainly what that ambition has not yet achieved.

### 2.3 Provenance

The W3C PROV data model [25, 26] treats derivation as a relation over entities and activities in
which an entity may derive from many others. Database provenance has a longer and more precise
tradition still, distinguishing why-provenance from where-provenance [27] and surveying the design
space [28]. Our Invariant II restates the multi-parent requirement, and the defect reported in §3.6
is exactly what happens when a formalism writes provenance as a scalar attribute rather than a set:
the implementation faithfully follows the formalism, and drops every parent but one. The literature
had the right answer three decades before we made the mistake, which is precisely the argument for
checking the property mechanically rather than trusting that we remembered it.

### 2.4 Belief revision

AGM [1] gives rationality postulates for theory change over a logical closure. Iterated revision needs
more than AGM supplies, and Darwiche and Pearl [29] give the additional conditions; Gärdenfors [30] is
the book-length treatment; Spohn's ordinal conditional functions [31] and Jeffrey's treatment of
uncertain evidence [32] are the two standard routes to graded belief change. On the probabilistic
side, conditioning on conditionally independent observations is commutative [2] — a fact whose
consequences for a belief store occupy §5 — and Pearl [33] is the canonical treatment of the
independence structure that makes it hold.

Human belief revision is neither minimal nor commutative. It is explanation-guided, order-sensitive,
and subject to recency [3, 4]. We take the formal result as a constraint on the *arithmetic* — a
belief store that violates commutativity is broken, not humanlike — and the empirical departure as a
reason to hold contradiction open in the graph, not as licence for the arithmetic to drift. §5.2
reports what enforcing that distinction cost us: a clamping step that looked like prudent numerical
hygiene destroyed both commutativity and exact retractability, and had to go.

### 2.5 Choosing what to ask

The inquiry planner of §6 scores candidate questions by expected information gain. The measure is
Lindley's [34]; the Bayesian experimental design tradition it belongs to is surveyed by Chaloner and
Verdinelli [35]; MacKay [36] brought information-based objectives to active data selection and
Houlsby et al. [37] to Bayesian active learning, within the broader active learning literature [38].

The cognitive-science strand matters more to us than the machine-learning one, because our questions
are asked of a person rather than of an oracle. Oaksford and Chater [39] analysed human data
selection as approximately optimal information gathering; Nelson [40] compared information gain
against diagnosticity, probability gain and impact as competing accounts of what makes a question
useful, and found no single measure dominant. We adopt EIG because it is the standard against which
the alternatives are compared, and we report normalised regret against an information-theoretic
oracle rather than raw performance, so that a reader who prefers a different measure can see how much
of our result is the measure and how much is the planning.

### 2.6 Reflection, self-tracking, and the user's own model

The HCI tradition this work sits inside treats reflection as a design goal rather than a by-product.
Reflective design [41] set out the commitments; Baumer [42] gave reflective informatics its conceptual
dimensions; Fleck and Fitzpatrick [43] framed the design landscape and distinguished levels of
reflection a system might support. Personal informatics supplies the empirical grounding — the
stage-based model [44], its lived revision [45], and what actually happens when people without prior
self-tracking experience meet their own data [46], which is often not the reflective engagement the
designers intended.

The most direct antecedent is the open and scrutable user model. Open learner models [47] show
learners the system's model of them; Kay [48] argues that adaptation must be scrutable — that a person
should be able to interrogate and correct the model driving a system's behaviour toward them.
Bellotti and Edwards [49] made intelligibility and accountability requirements for context-aware
systems, and Lim and Dey [50] measured the demand for them empirically. Horvitz's principles for
mixed-initiative interfaces [51] supply the interaction frame in which a system may ask rather than
assume.

The Unified Reflective Graph (§4) is a scrutable user model with two commitments added: every node
reaches the evidence that produced it, and contested hypotheses are represented rather than resolved.
What this paper adds to that tradition is not the goal but the *check* — a decision procedure that
says whether a given implementation actually has those properties.

### 2.7 Explanation, and what it buys

Explainable AI supplies both our framing and our caution. Doshi-Velez and Kim [10] set out what a
rigorous science of interpretability would require; Miller [11] argues that explanation is a social
process rather than a model-inspection problem; Rudin [12] argues against explaining black boxes at
all where an interpretable model would serve; Lipton [13] shows that "interpretability" names several
mutually incompatible desiderata.

The empirical results are sobering. Explanations do not reliably improve complementary team
performance [52]. Schäfer et al. [5] show that displaying uncertainty does not by itself produce
calibrated reliance, and Rosenbacke et al. [6] find in systematic review that explainability can
decrease trust calibration as easily as increase it. Guidelines for human–AI interaction [53]
codify much of this into design practice.

We take two things from this literature. Inspectability is a property to be *checked* rather than
claimed — which is the entire argument of this paper. And abstention deserves to be a first-class
output rather than a fallback, because a better-hedged wrong answer is still a wrong answer.

### 2.8 Metacognitive architectures

A recent line of work embeds reflection inside the model: reuse of recurring reasoning as named
behaviours [7], evolving meta-memory [8], grounded metacognitive reasoning [9]. Those systems improve
what a model knows about its own reasoning. Our concern is orthogonal, and we think complementary: an
external structure whose reasoning about a person is inspectable *by that person*. A model that
reflects well internally but cannot show its work to the subject of its inferences has solved a
different problem from the one addressed here.

---

## 3. Invariants as an executable specification

### 3.1 The eleven invariants

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
is marked stale — neither silently retained nor silently deleted. The distinction matters because
retention is the failure mode that produces confident conclusions drawn under conditions that no
longer hold.

**X is a property of what reaches the person**, so it is checked at the output boundary rather than
in the reasoning. Each terminal output must carry its uncertainty and disclaimer, offer at least one
question, and avoid identity claims (*you are…*, *you secretly…*, *your true…*) and directives
(*you must…*, *you should…*).

### 3.2 The harness

`build_well_formed(seed)` constructs a randomised reflective state: 2–5 observations, derived
evidence with multiple provenance parents, 2–4 hypotheses with mixed supporting and contradicting
edges, executed belief updates, planned inquiries, and an explanation. Invariants I–X are
asserted across 200 seeds.

Invariant XI needed a second generator, because it ranges over a formation model rather than a graph.
`_random_model(seed)` builds a model from a random sequence of declarations, person overrides and
attempted instrument administrations, under a randomly chosen deployment context and a consent grant
present 80% of the time. Most administrations therefore refuse, and that is the point: XI must hold
whatever the model has been through, *including* the paths where every administration was declined. It
is asserted across 200 seeds, with 100 further randomised checks on two derived properties — that no
model ever retains a non-self-completed administration, and that a person's override always wins for
display.

Without that second harness, XI would have been the one invariant asserted only by hand-built cases,
which is precisely the position the other ten started from.

Both generators are small seeded builders rather than a property-testing library. The package has no
runtime dependencies by design — local-first and auditable — and adding one for the test suite alone
would undercut the argument the architecture rests on.

### 3.3 Negative tests, and why they are the point

**Sixteen negative tests** construct states that violate each invariant and assert the check catches
them: an explanation with no evidence; a store that keeps only the first provenance parent; a
transition with no triggering evidence; an explanation that hides its uncertainty; a dropped
competitor; a superseded context whose dependents are unannotated; an inquiry that justifies nothing;
a store without rollback; verdict phrasing; a missing question; a missing disclaimer; a refusal that
returns a value; a refusal that has been deleted rather than triggered.

There are **fourteen** such tests and **four positive controls** — states that should pass and do.
Earlier drafts of this paper reported "sixteen negative tests", which counted the four positive
controls among them. The correction is small and we make it explicitly rather than silently, because a
paper about checkable claims should not miscount its own checks (D-34).

Without these, a suite reporting "11/11 invariants hold" is unfalsifiable in exactly the way the prose
was.

### 3.4 What happened when we pointed it at real output

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

### 3.5 Do the checks discriminate between implementations?

A specification that only its own author's implementation can satisfy has demonstrated nothing. Two
pieces of evidence say these checks discriminate.

**The negative tests** (§3.3) construct violating states and confirm each check rejects them. That
establishes the checks are not vacuous.

**The prototype.** The same decision procedure was run unmodified against an independently written
implementation of the same architecture — a NetworkX-based prototype produced separately from this
work. It passes four checks and **fails three**: provenance preservation (0 of 2 parents recovered),
order invariance (spread 0.9504 across permutations), and inquiry justification (no information-gain
content). The procedure therefore separates two implementations of one architecture, which is the
minimum evidence that it is measuring conformance rather than restating an API.

This is two implementations, not many. §10 records that limitation.

### 3.6 Results

| | Prototype | v1.0 |
|---|---|---|
| I Evidence traceability | pass | pass |
| II Provenance preservation | **fail** — 0/2 parents recovered | pass — 2/2 |
| III Revision history | pass | pass |
| V Hypothesis independence | pass | pass — contradiction retained |
| Order invariance (120 permutations) | **fail** — spread 0.9504 | pass — spread 0.00 |
| IV Explicit uncertainty | pass | pass |
| VIII Inquiry justification | **fail** — no information-gain content | pass |
| | **4/7** | **7/7** |

Full suite: **673 tests** (671 passing), of which 563 are invariant checks — 200 randomised graph
states for Invariants I–X, 200 randomised formation models plus 100 further randomised property checks
for Invariant XI, 14 negative tests, 4 positive controls, and 45 hand-built cases. A further 16 are
operator-correspondence tests and the remainder are component regressions. Two are strict `xfail`s
recording unimplemented operators (§9).

---

### 3.7 An invariant that exists because of a request

Invariant XI was not derived from the architecture. It was derived from being asked for something.

A user of this system asked it to "determine and understand who people probably are according to their
will, desire and need — where they come from, how mature they are, what they still need to be mature
enough, what their eventual purpose probably is", with the qualification "I would not say judge
people". That qualification is the interesting part: the request came with an intuition that something
in it was wrong, and no way to say which part.

It is five requests, and they separate cleanly on whether a validated construct exists and who supplies
it. *Will*, *desire* and *need* have validated self-report instruments, so the person can supply them.
*Where they come from* is inference of special-category data unless the person declares it. *How mature
they are* is available only from instruments whose output is a single ordered position — Loevinger's
Total Protocol Rating [56], Kegan's subject-object position [57], Cook-Greuter's Center of Gravity —
where the
rank is not a summary of the construct but *is* the construct, so it cannot be reported as a profile
without misrepresenting the instrument. *What they still need to be mature enough* is a directive about
identity, which Invariant X already forbids. *Eventual purpose* has no construct at all. The
substitutes we adopted — a three-dimensional wisdom scale [58] and a psychosocial attribute inventory —
report dimensions and never a stage.

So four of the five are refused, and the refusals are the feature. What makes them an architectural
matter rather than a policy note is that a refusal stated in prose decays exactly as the original ten
invariants did. Invariant XI is the decision procedure that stops it:

```python
def check_xi_declared_only(model) -> InvariantResult:
    # (a) every attribute traces to a declaration or a self-completed instrument
    # (b) each refusing method, when CALLED, raises with the expected ground
```

Condition (b) is the part worth defending. The check does not inspect source code or match names; it
**calls** each method that ought to refuse and requires a typed refusal carrying the expected ground.
Two distinct failure modes are caught. A method that returns a value fails, obviously. A method that has
been *deleted* also fails — and that is the less obvious commitment, because **absence is not refusal**.
A caller who finds no `eventual_purpose` attribute learns nothing; a caller who calls it and reads why
it declined learns what the architecture will not do and on what ground. The refusing methods therefore
exist in order to refuse, which is a deliberate inversion of the usual advice to delete dead code.

The two negative tests are correspondingly shaped: subclass the model so that `eventual_purpose()`
returns a plausible answer, and XI fails; delete `maturity_level` entirely, and XI fails for a different
stated reason.

**What this does not establish.** Eleven refusal grounds are a catalogue, not a theory of which requests
a reflective system should decline, and we do not have one. The check verifies that the named refusals
refuse; it cannot verify that the catalogue is complete, and a request we did not anticipate will not be
caught. It also cannot check phrasing — the accompanying `open_questions()` output is guarded against
prescriptive drift by a keyword test, which carries the same syntactic-proxy weakness we already concede
for Invariant X (§10).

---

## 4. The Unified Reflective Graph

Typed nodes (Observation, Evidence, Context, Hypothesis, Belief, Inquiry, Explanation, Knowledge,
Limitation) and typed edges (provenance, supports, contradicts, contextualises, revises, targets,
explains, limits). Untyped insertions are rejected: an untyped graph cannot support a traceability
invariant, because there is nothing to quantify over.

**Provenance is a DAG.** `ancestors()` returns the transitive closure over *all* provenance parents.
The prototype followed the first predecessor only, recovering 0 of 2 parents from a two-parent
derivation. The formalism licensed it: the evidence object was specified with provenance as a scalar
attribute *p_i*. Writing it as a set — which §A.2 of our formal appendix now does — is the fix, and
the defect is a small case study in formal notation shaping implementation error.

**Contradiction is an edge, not an overwrite.** `contested_hypotheses()` returns hypotheses carrying
both supporting and contradicting evidence, so an explanation can report a tension rather than
preferring the later write. This is Invariant V's teeth.

**Updates are transactional.** A `transaction()` context manager snapshots and rolls back, so a
failure mid-update cannot leave a hypothesis whose belief moved but whose provenance edge was never
written — which would violate Invariants I and IX simultaneously and silently.

**No third-party dependencies.** The graph is an adjacency structure in the standard library. This is
not minimalism for its own sake: the architecture's claim is local-first auditability, and importing
a graph framework for a dictionary of lists would trade that for nothing.

---

## 5. Belief revision

### 5.1 The axioms

Leaving the belief state's type open — "probability distributions, weighted graphs, logical
structures" — and then asserting properties of it is a common and serious error. Properties cannot be
asserted of an object whose type is open. We state the axioms instead:

- **B1 Plurality** — assigns a value to every hypothesis simultaneously; no distinguished maximiser.
- **B2 Commutativity** — order of conditionally independent evidence does not matter.
- **B3 Invertibility** — evidence can be retracted exactly.
- **B4 Audit** — every application records prior, posterior, trigger, method, time.

B3 is not a convenience. **A system that cannot undo an inference cannot honour a withdrawal of
consent**, which turns an ethical commitment into an architectural requirement.

### 5.2 The instantiation, and the defect it repairs

$$\ell_t(h) = \operatorname{logit}\pi(h) + \sum_{e \in \mathcal{E}_t} w_e \lambda_e(h), \qquad
\lambda_e(h) = \log\frac{P(e \mid h)}{P(e \mid \lnot h)}, \qquad B_t(h) = \sigma(\ell_t(h))$$

$\mathcal{E}_t$ is a set **keyed by evidence identity**, which yields B2 (addition commutes), B3
(subtract the term) and idempotence under resubmission.

The prototype clamped the posterior to [0.01, 0.99] *in state* after each update. Clamping is not
invertible: once pinned, the information about how far past the bound the evidence pushed is
destroyed. Five observations in three orders produced final beliefs of **0.0396, 0.9900 and 0.9900**.

v1.0 clamps only at display. Measured consequences:

- All **120 permutations** of the five-observation sequence agree to within 1e-12.
- Twenty strongly-confirming updates followed by twenty strongly-disconfirming ones return the belief
  to **exactly 0.5**. The prototype could not do this at all.
- `retract()` restores the prior state bit-for-bit.

### 5.3 The independence assumption, stated

Sequential updating requires $e_i \perp e_j \mid h$. In reflective domains this is frequently false:
two self-reports on consecutive days are correlated through mood, framing and recall, not only
through the latent state. Keying contributions by identity prevents resubmission compounding, and
temporal decay down-weights clustering, but neither substitutes for a correlated-likelihood model.
We state the assumption rather than rely on it silently.

---

## 6. Inquiry planning

$$\mathrm{EIG}(a) = \mathbb{H}(B) - \mathbb{E}_{Y_a}[\mathbb{H}(B \mid Y_a)], \qquad
\mathcal{Q}(B,\mathcal{A}) = \operatorname*{arg\,max}_{a \in \mathcal{A}} \frac{\mathrm{EIG}(a)}{\mathrm{cost}(a)}$$

The heuristic this replaces scored inquiries as $1 - |B(h_i) - B(h_j)|$ — a quantity that does not
depend on the candidate observation at all, and therefore carries no information about what to ask.

Normalised regret against an oracle, 500 trials per condition, four candidate observations:

| Planner | Hypotheses close (gap 0.04) | Hypotheses separated (gap 0.40) |
|---|---|---|
| **Expected information gain** | **0.161 [0.138, 0.187]** | **0.195 [0.168, 0.223]** |
| Belief-gap heuristic | 0.579 [0.547, 0.612] | **1.000 [1.000, 1.000]** |
| Random selection | 0.550 [0.515, 0.584] | 0.562 [0.528, 0.597] |

Two behavioural points matter more than the numbers. The heuristic is **indistinguishable from
random** when it fires; and it emits nothing at all once hypotheses are separated, which is backwards
— a confidently held wrong hypothesis is exactly when a discriminating observation is worth most.
Invariant VIII requires each inquiry to state what it would resolve, in bits, and which hypotheses it
separates; the information-gain formulation supplies both by construction.

---

## 7. Complexity, measured

The architecture's own complexity chapter warned that unrestricted recomputation "could approach
O(n²)" and gave no bound for any operator it defined. We measured all four, as scaling ratio per
doubling (linear ≈ 2.0×, quadratic ≈ 4.0×):

| Operation | Bound | Measured |
|---|---|---|
| Provenance closure `ancestors()` | O(V+E) | **2.0×** ✓ |
| Inquiry planning | O(\|H\|·\|A\|) | 3.9× at \|H\|=\|A\| ✓ (product of two linear factors) |
| Belief update, log-odds ledger | O(1) | **4.2× — quadratic** ❌ → **2.0×** after fix |
| Observation intake, full recompute | O(n) per call | **3.8× — quadratic** |

The third row was a defect in our own code: the ledger summed every contribution on each call,
costing 624 ms at 8,000 updates. Maintaining a running total gives 78 ms at 16,000. **A regression
test fails if the ratio exceeds 3.0×**, using best-of-three timing so that machine load does not
convert a linear algorithm into a failing test.

The fourth row is open. The intake recomputes the full belief state per observation: 27 ms at 100
evidence pairs, 1121 ms at 800. Incremental recompute is the first optimisation target — and it is
worth recording that the prose chapter predicted this growth before the code existed. Its warning was
correct; it simply attached it to a strawman rather than to the operators it specified.

---

## 8. What the architecture does not buy

On latent-state recovery under model misspecification, the graph-backed inference is **statistically
indistinguishable from a median-split quadrant classifier across all 20 tested conditions**, with
paired differences of −2.5 to +2.5 points and 2,000-resample percentile bootstrap intervals [55]
spanning zero everywhere.

A reviewer may reasonably ask why an interactive-systems venue should care about an architecture
that buys no accuracy. The answer is that accuracy was never the safety-relevant quantity here: the
companion result — a measured harm rate reduced from 42.9–75.1% to zero, or a 95% upper bound of
0.37% by the rule of three [54] — depends on the structural
commitments described above, specifically on representing a competing hypothesis rather than
filtering, and on distinguishing an absent channel from a zero reading. Structure is what carries it.

We report the negative result prominently because the temptation to omit it is strong and because it
relocates the contribution rather than diminishing it. **The architecture is not an accuracy technique.** Its value
is structural: conclusions that trace to evidence, provenance that survives derivation, contradiction
that is retained, revision that can be undone, inquiries that justify themselves, and conformance
that is decidable. Any claim that a reflective substrate improves classification should be measured
before it is made; ours does not, and we say so.

Two related measurements complete the picture.

**Calibration.** Where the model's assumed structure approximately holds, accumulating evidence with
an explicit *none-of-these* component reduces expected calibration error from **0.171 to 0.044** and
raises AUC(uncertainty → error) from **0.868 to 0.949**. Where it materially does not hold,
calibration is **worse**: ECE 0.151 → 0.221. The architecture trades uniformly mediocre calibration
for good-when-applicable and poor-when-not, which is an improvement only to the degree the system can
tell which regime it is in. It partly can, and not enough.

**Identifiability.** A two-channel location model cannot distinguish "state A, displaced" from
"state B" when the displacement points toward B. This is not fixable by thresholding. It *is*
partially fixable by observing more: pooling across topics to estimate a person-level displacement
raises accuracy from **83.8% to 95.8%** at δ = 0.30 with eight topics, with offset error falling from
0.187 to 0.092. At δ = 0.45 it reaches only 61.3%, limited by the estimator's initialisation.

---

## 9. Declared gaps

Two operators are specified in the architecture and implemented nowhere. They are carried as strict
`xfail` tests, so they cannot quietly become "implemented" in a later summary:

| Operator | Status |
|---|---|
| **Causal reflection** — intervention, counterfactual query | Prose only. No do-operator exists. Presented as research agenda, not as a component. |
| **Knowledge consolidation** $K_t \leftarrow B_t$ | Prose only. No promotion criterion from belief to revisable knowledge exists. |

Also unimplemented: encryption at rest, multimodal acquisition, a reflective execution engine with
event queues, and any user interface beyond a command line.

A reference architecture earns the word *reference* when the distance between its formalism and its
implementation can be enumerated. We enumerate it.

---

## 10. Limitations

**No human subjects.** Nothing here establishes any effect on human reasoning, comprehension, trust
or task outcome, and no such claim is made. Every result is a property of code or of simulated signal
streams. [NO DATA YET — human evaluation]

**Simulation encodes a theory.** The generative processes embody assumptions about how latent states
manifest in observable signal. If those are wrong, absolute rates are wrong — though comparisons
between methods, which see the same generator, are more robust than the rates themselves.

**Two implementations, not many.** §3.5 shows the decision procedure separating a compliant
implementation from a non-compliant one, which rules out vacuity. It does not establish that the
procedure is portable to an implementation built on different primitives — a graph database, an
event-sourced store, a logic programming substrate. Until someone unconnected to this work runs the
checks against their own system, "decidable" is demonstrated and "decidable usefully" is not.
[NO DATA YET — independent third-party implementation]

**Invariant X is a syntactic proxy for a semantic property.** Whether an output usurps a person's
authority over their own self-understanding is not a matter of which pronouns it contains. Our check
tests phrasing, and §3.4 documents it producing a false positive on its first contact with real
output. It will also produce false negatives: a sentence can be a verdict without matching any
pattern we listed. The check raises the floor; it does not measure the property.

**The randomised harness has unmeasured coverage.** Two hundred seeds vary observation count,
evidence count, provenance branching, hypothesis count, edge polarity, likelihood values and inquiry
candidates. Nothing measures whether that exercises the state space in any principled sense, and we
make no claim that it does.

**Scale.** Everything reported runs on a single machine over thousands of nodes, not millions. The
architecture makes no validated scalability claim, and §7 identifies the binding constraint as an
algorithmic one rather than an infrastructural one.

---

### 10.1 How much of the state space the harness actually reaches

Earlier drafts stated that nothing measured whether the randomised harness exercises the state space
in any principled sense. That is no longer true, and the measurement is not flattering.

Mutation testing over the package produced **5,114 mutants**. The suite killed **2,319** and **1,549
survived**, for a mutation score of **59.9%**. A further 1,244 mutants sit in code with no covering
test at all, 909 of them in a command-line interface that has never had tests and does not carry any
claim in this paper.

Survivors concentrate in the inference engine (404), the pattern layer (278), the invariant checks
themselves (206) and the formation model (195). Inspection of a sample shows most are label and
message mutations rather than behavioural ones — replacing an observation string with `None`, or an
error message with a placeholder — which means the raw score understates the suite. But not all of
them are cosmetic. Mutating an invariant's own identifier from `"I"` to a nonsense string survived,
which means no test asserted that a check returns the invariant it claims to be: a catalogue of named
architectural properties that could be silently renamed. Two tests now close that, and they exist
because a tool found the gap rather than because we thought of it.

We report the score rather than tuning it. A mutation score is a lower bound on test strength and an
upper bound on nothing, and 59.9% is a middling result for a package that makes conformance claims.

## 11. Conclusion

Making the invariants executable found two defects that a prose specification had asserted away: a
provenance model that dropped parents, and a belief operator whose result depended on the order
evidence arrived. Neither was visible to a reader of the document. Both were visible on the first run
of the decision procedure.

We think that is the transferable claim. Reference architectures for human–AI interaction should ship
their conformance suites, should include negative tests, and should point those suites at output a
person would actually see. Ours did all three and was wrong three times — about provenance, about
order invariance, and about its own Invariant X check. Each error surfaced within a minute of the
check being run, and none would have surfaced from reading.

---

## Ethics statement

This research did not involve human or animal subjects. All results derive from code execution and
from simulated signal streams; no personal data was collected, processed or analysed.

The system is a research instrument, not a medical device, and is not suitable for clinical,
educational, employment, credit, insurance, policing or other high-stakes deployment. A companion
paper addresses its regulatory position, including a prohibition on emotion inference in workplaces
and education institutions that applies to one of its optional evidence channels.

**Data and code availability.** Implementation, conformance suite, benchmarks and analysis scripts
are released under an open licence. The benchmark suite is byte-reproducible across runs. Every
number in this paper is produced by a named script. *[REPOSITORY URL — TO BE COMPLETED]*

---

## References

[1] C. E. Alchourrón, P. Gärdenfors, and D. Makinson. "On the logic of theory change: Partial meet
contraction and revision functions." *Journal of Symbolic Logic*, 50(2):510–530, 1985.
DOI: 10.2307/2274239

[2] B. Jacobs. "Commutativity of probabilistic belief revision." *Frontiers in Cognition*, 2025.
DOI: 10.3389/fcogn.2025.1623227

[3] S. L. Vasileiou et al. "How Do People Revise Inconsistent Beliefs? Examining Belief Revision in
Humans with User Studies." arXiv:2506.09977, 2025.

[4] S. L. Vasileiou and W. Yeoh. "Human-Aware Belief Revision: A Cognitively Inspired Framework for
Explanation-Guided Revision of Human Models." arXiv:2405.19238, 2024.

[5] U. Schäfer et al. "'The AI is uncertain, so am I. What now?': Navigating Shortcomings of
Uncertainty Representations in Human-AI Collaboration with Capability-focused Guidance."
*Proc. ACM Hum.-Comput. Interact.*, 2025. DOI: 10.1145/3757451

[6] R. Rosenbacke, Å. Melhus, et al. "How Explainable AI Can Increase or Decrease Clinicians' Trust in
AI Applications in Health Care: Systematic Review." *JMIR AI*, 1:e53207, 2024. PMID: 39476365

[7] A. Didolkar, N. Ballas, S. Arora, and A. Goyal. "Metacognitive Reuse: Turning Recurring LLM
Reasoning Into Concise Behaviors." arXiv:2509.13237, 2025.

[8] Xin et al. "MetaMem: Evolving Meta-Memory for Knowledge Utilization through Self-Reflective
Symbolic Optimization." *Findings of ACL 2026*. arXiv:2602.11182

[9] A. P. Elenjical, V. H. Kavuri, and V. Varma. "Think2: Grounded Metacognitive Reasoning in Large
Language Models." arXiv:2602.18806, 2026.

[10] F. Doshi-Velez and B. Kim. "Towards a Rigorous Science of Interpretable Machine Learning."
arXiv:1702.08608, 2017.

[11] T. Miller. "Explanation in artificial intelligence: Insights from the social sciences."
*Artificial Intelligence*, 267:1–38, 2019. DOI: 10.1016/j.artint.2018.07.007

[12] C. Rudin. "Stop explaining black box machine learning models for high stakes decisions and use
interpretable models instead." *Nature Machine Intelligence*, 1:206–215, 2019.
DOI: 10.1038/s42256-019-0048-x

[13] Z. C. Lipton. "The mythos of model interpretability." *Communications of the ACM*, 61(10):36–43,
2018. DOI: 10.1145/3233231. (Preprint: arXiv:1606.03490, 2016.)

[14] D. E. Perry and A. L. Wolf. "Foundations for the study of software architecture."
*ACM SIGSOFT Software Engineering Notes*, 17(4):40–52, 1992. DOI: 10.1145/141874.141884

[15] G. C. Murphy, D. Notkin, and K. J. Sullivan. "Software reflexion models: bridging the gap between
design and implementation." *IEEE Transactions on Software Engineering*, 27(4):364–380, 2001.
DOI: 10.1109/32.917525

[16] R. Terra and M. T. Valente. "A dependency constraint language to manage object-oriented software
architectures." *Software: Practice and Experience*, 39(12):1073–1094, 2009. DOI: 10.1002/spe.931

[17] J. Knodel and D. Popescu. "A Comparison of Static Architecture Compliance Checking Approaches."
*Working IEEE/IFIP Conference on Software Architecture (WICSA'07)*, 2007. DOI: 10.1109/WICSA.2007.1

[18] L. Passos, R. Terra, M. T. Valente, R. Diniz, and N. das Chagas Mendonça. "Static
Architecture-Conformance Checking: An Illustrative Overview." *IEEE Software*, 27(5):82–89, 2010.
DOI: 10.1109/MS.2009.117

[19] S. Ducasse and D. Pollet. "Software Architecture Reconstruction: A Process-Oriented Taxonomy."
*IEEE Transactions on Software Engineering*, 35(4):573–591, 2009. DOI: 10.1109/TSE.2009.19

[20] B. Meyer. "Applying 'design by contract'." *Computer*, 25(10):40–51, 1992. DOI: 10.1109/2.161279

[21] L. Lamport. "The temporal logic of actions." *ACM Transactions on Programming Languages and
Systems*, 16(3):872–923, 1994. DOI: 10.1145/177492.177726

[22] D. Jackson. "Alloy: a lightweight object modelling notation." *ACM Transactions on Software
Engineering and Methodology*, 11(2):256–290, 2002. DOI: 10.1145/505145.505149

[23] M. Leucker and C. Schallhart. "A brief account of runtime verification." *The Journal of Logic
and Algebraic Programming*, 78(5):293–303, 2009. DOI: 10.1016/j.jlap.2008.08.004

[24] K. Claessen and J. Hughes. "QuickCheck: a lightweight tool for random testing of Haskell
programs." *Proc. Fifth ACM SIGPLAN International Conference on Functional Programming (ICFP '00)*,
pp. 268–279, 2000. DOI: 10.1145/351240.351266

[25] L. Moreau and P. Missier (eds.). "PROV-DM: The PROV Data Model." W3C Recommendation, 30 April
2013. https://www.w3.org/TR/2013/REC-prov-dm-20130430/

[26] P. Groth and L. Moreau (eds.). "PROV-Overview: An Overview of the PROV Family of Documents."
W3C Working Group Note, 30 April 2013. https://www.w3.org/TR/2013/NOTE-prov-overview-20130430/

[27] P. Buneman, S. Khanna, and W.-C. Tan. "Why and Where: A Characterization of Data Provenance."
*Database Theory — ICDT 2001*, LNCS, pp. 316–330, 2001. DOI: 10.1007/3-540-44503-X_20

[28] J. Cheney, L. Chiticariu, and W.-C. Tan. "Provenance in Databases: Why, How, and Where."
*Foundations and Trends in Databases*, 1(4):379–474, 2009. DOI: 10.1561/1900000006

[29] A. Darwiche and J. Pearl. "On the logic of iterated belief revision." *Artificial Intelligence*,
89(1–2):1–29, 1997. DOI: 10.1016/S0004-3702(96)00038-0

[30] P. Gärdenfors. *Knowledge in Flux: Modeling the Dynamics of Epistemic States*. MIT Press, 1988.
ISBN 9780262071093

[31] W. Spohn. "Ordinal Conditional Functions: A Dynamic Theory of Epistemic States." In W. L. Harper
and B. Skyrms (eds.), *Causation in Decision, Belief Change, and Statistics*, vol. II, pp. 105–134.
Kluwer, 1988. DOI: 10.1007/978-94-009-2865-7_6

[32] R. C. Jeffrey. *The Logic of Decision*, 2nd ed. University of Chicago Press, 1983.
ISBN 9780226395821. (1st ed., McGraw-Hill, 1965.)

[33] J. Pearl. *Probabilistic Reasoning in Intelligent Systems: Networks of Plausible Inference*.
Morgan Kaufmann, 1988. ISBN 9781558604797

[34] D. V. Lindley. "On a Measure of the Information Provided by an Experiment." *The Annals of
Mathematical Statistics*, 27(4):986–1005, 1956. DOI: 10.1214/aoms/1177728069

[35] K. Chaloner and I. Verdinelli. "Bayesian Experimental Design: A Review." *Statistical Science*,
10(3):273–304, 1995. DOI: 10.1214/ss/1177009939

[36] D. J. C. MacKay. "Information-Based Objective Functions for Active Data Selection."
*Neural Computation*, 4(4):590–604, 1992. DOI: 10.1162/neco.1992.4.4.590

[37] N. Houlsby, F. Huszár, Z. Ghahramani, and M. Lengyel. "Bayesian Active Learning for
Classification and Preference Learning." arXiv:1112.5745, 2011.

[38] B. Settles. "Active Learning Literature Survey." Computer Sciences Technical Report 1648,
University of Wisconsin–Madison, 2009. http://digital.library.wisc.edu/1793/60660

[39] M. Oaksford and N. Chater. "A rational analysis of the selection task as optimal data selection."
*Psychological Review*, 101(4):608–631, 1994. DOI: 10.1037/0033-295X.101.4.608

[40] J. D. Nelson. "Finding Useful Questions: On Bayesian Diagnosticity, Probability, Impact, and
Information Gain." *Psychological Review*, 112(4):979–999, 2005. DOI: 10.1037/0033-295X.112.4.979

[41] P. Sengers, K. Boehner, S. David, and J. Kaye. "Reflective design." *Proc. 4th Decennial
Conference on Critical Computing (CC '05)*, pp. 49–58, 2005. DOI: 10.1145/1094562.1094569

[42] E. P. S. Baumer. "Reflective Informatics: Conceptual Dimensions for Designing Technologies of
Reflection." *Proc. CHI 2015*, pp. 585–594. DOI: 10.1145/2702123.2702234

[43] R. Fleck and G. Fitzpatrick. "Reflecting on reflection: framing a design landscape."
*Proc. OZCHI 2010*, pp. 216–223. DOI: 10.1145/1952222.1952269

[44] I. Li, A. K. Dey, and J. Forlizzi. "A stage-based model of personal informatics systems."
*Proc. CHI 2010*, pp. 557–566. DOI: 10.1145/1753326.1753409

[45] D. A. Epstein, A. Ping, J. Fogarty, and S. A. Munson. "A lived informatics model of personal
informatics." *Proc. UbiComp 2015*, pp. 731–742. DOI: 10.1145/2750858.2804250

[46] A. Rapp and F. Cena. "Personal informatics for everyday life: How users without prior
self-tracking experience engage with personal data." *International Journal of Human-Computer
Studies*, 94:1–17, 2016. DOI: 10.1016/j.ijhcs.2016.05.006

[47] S. Bull and J. Kay. "Open Learner Models." In *Advances in Intelligent Tutoring Systems*,
Studies in Computational Intelligence vol. 308, pp. 301–322. Springer, 2010.
DOI: 10.1007/978-3-642-14363-2_15

[48] J. Kay. "Scrutable Adaptation: Because We Can and Must." *Adaptive Hypermedia and Adaptive
Web-Based Systems (AH 2006)*, LNCS 4018, pp. 11–19. DOI: 10.1007/11768012_2

[49] V. Bellotti and K. Edwards. "Intelligibility and Accountability: Human Considerations in
Context-Aware Systems." *Human-Computer Interaction*, 16(2–4):193–212, 2001.
DOI: 10.1207/S15327051HCI16234_05

[50] B. Y. Lim and A. K. Dey. "Assessing demand for intelligibility in context-aware applications."
*Proc. UbiComp 2009*, pp. 195–204. DOI: 10.1145/1620545.1620576

[51] E. Horvitz. "Principles of mixed-initiative user interfaces." *Proc. CHI 1999*, pp. 159–166.
DOI: 10.1145/302979.303030

[52] G. Bansal, T. Wu, J. Zhou, R. Fok, B. Nushi, E. Kamar, M. T. Ribeiro, and D. S. Weld. "Does the
Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance."
*Proc. CHI 2021*, article 81. DOI: 10.1145/3411764.3445717

[53] S. Amershi, D. Weld, M. Vorvoreanu, A. Fourney, B. Nushi, P. Collisson, J. Suh, S. Iqbal,
P. N. Bennett, K. Inkpen, J. Teevan, R. Kikin-Gil, and E. Horvitz. "Guidelines for Human-AI
Interaction." *Proc. CHI 2019*, paper 3. DOI: 10.1145/3290605.3300233

[54] J. A. Hanley and A. Lippman-Hand. "If Nothing Goes Wrong, Is Everything All Right? Interpreting
Zero Numerators." *JAMA*, 249(13):1743–1745, 1983. DOI: 10.1001/jama.1983.03330370053031

[55] B. Efron and R. J. Tibshirani. *An Introduction to the Bootstrap*. Chapman & Hall, 1993.
ISBN 9780412042317

[56] L. X. Hy and J. Loevinger. *Measuring Ego Development*, 2nd ed. Lawrence Erlbaum, 1996.
ISBN 9781138876552

[57] L. Lahey, E. Souvaine, R. Kegan, R. Goodman, and S. Felix. *A Guide to the Subject-Object
Interview: Its Administration and Interpretation*. Harvard Graduate School of Education, 1988.

[58] M. Ardelt. "Empirical Assessment of a Three-Dimensional Wisdom Scale." *Research on Aging*,
25(3):275–324, 2003. DOI: 10.1177/0164027503025003004

---

## Appendix A — Formal specification

*(The corrected formal appendix — notation, evidence objects as sets, operator signatures with no
symbol collisions, the belief axioms, the independence condition, traceability and provenance
closure, and the measured complexity table — is carried in full as supplementary material
`FORMAL_APPENDIX_corrected.md`.)*

## Appendix B — Number provenance

| Figure | Source |
|---|---|
| Test counts (673 collected, 671 passing, 563 invariant, 14 negative, 4 positive controls) | `pytest --collect-only`; `tests/test_invariants.py`, `tests/test_v12_formation.py` |
| Conformance 4/7 vs 7/7 | `conformance_v10.py` |
| Order invariance, 120 permutations | `test_d20_belief_is_invariant_under_every_permutation` |
| Prototype 0.0396 / 0.9900 | `conformance_v10.py::proto_checks` |
| Inquiry regret | `results.json → b4.conditions` |
| Complexity ratios | `test_operator_correspondence.py` timing harness |
| Median-split parity | `results.json → b1.cells` (20 cells) |
| ECE and AUC(uncertainty→error) | `v030_vs_v040.json` |
| Offset pooling 83.8% → 95.8% | `experiment_d23.json → offset_correction` |

```bash
pytest -q                        # 671 passed, 2 xfailed
python conformance_v10.py
python run_benchmarks.py
python experiment_d23.py
python analyze_v030_vs_v040.py
```

---

## Appendix C — Outstanding work with no available substitute

Everything in this appendix was searched for before it was listed. The rule applied was: an item is
only recorded here if an active hunt for a public dataset, a free instrument, a third-party service or
a methodological substitute came back empty. Items that a search *did* resolve are recorded in the
second table, so that a reader can see the difference between what is genuinely blocked and what was
merely inconvenient.

### C.1 What has no substitute

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
C.2). It did not for the other two. There is no openly licensed eight-theme Eriksonian
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
C.2 as an action rather than a limitation — but as of writing it has not been done, and the
claim in this paper is that the code is inspectable, not that it has been independently run.

**5. Two invariants are syntactic proxies for semantic properties.**
Invariant X detects verdict phrasing by pattern, and the accompanying question generator is guarded
against prescriptive drift by a keyword test. Both raise a floor and neither measures the property. We
know of no decision procedure that settles whether a sentence claims authority over a person, and we
do not think one follows from more patterns. This is a research problem rather than an unfinished
task, and we would rather state it than let a passing check imply otherwise.

### C.2 What a search resolved, and how

Recorded so that the list above is read as the residue of a search rather than as its whole.

| Was blocked | Resolved by | Cost of the substitution |
|---|---|---|
| Values instrument permission-gated, item mapping unreachable | The ESS Human Values Scale, whose items and item-to-value mapping are both published, under CC BY-SA documentation terms plus the instrument author's own non-commercial grant — and which has an already-fielded Arabic version | 10 basic values instead of 19 refined, from 2–3 items each |
| Wisdom instrument permission-gated | The revised Adult Self-Transcendence Inventory, CC BY 4.0, whose original author is a named co-licensor, dimensional, and whose authors argue explicitly against a total score | Construct drift: it measures self-transcendence, and has no analogue of the cognitive dimension |
| Harness coverage unmeasured | Mutation testing. Reported in §10 as a measured score with its weakest modules named | None; it replaced an admission with a number and a work list |
| Invariant identity untested | Found *by* the mutation run — mutating an invariant's identifier and name produced surviving mutants — and closed with two tests | None |
| Distribution-free coverage guarantees blocked on labelled outcomes | Available under the secondary-analysis route, where two of the three corpora supply an item-matched choice that can contradict a stated preference | Applies to the preference model only; the safety claim is untouched |
| Independent execution | A community code-check service that accepts submissions on a preprint alone, is free, and issues a citable certificate naming the person who ran the code | Certifies execution, not scientific correctness |

### C.3 What is not in this appendix

Ordinary unfinished work is excluded on purpose: two unimplemented operators recorded as strict
`xfail`s, a read path that remains linear per consultation, a candidate belief state for monotonic
drift, and the surviving mutants named in §10. None of these is blocked on anything external.
They are simply not done, and listing them here would dilute a list whose value is that every entry on
it has been searched for and not found.

