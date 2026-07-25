# Shadow Mirror — Session 05: Invariants as Executable Specification, and D-23

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverable:** `shadow_mirror_v1.0.zip` (updated) — **294 passing tests**, all ten invariants
executable, plus `experiment_d23.py` and `experiment_d23.json`.

---

## 0. Summary

The ten architectural invariants are no longer prose. They are ten callable checks with a positive
and a negative test each, run over 200 randomised reflective states. That converts the paper's
central claim from *"we define ten invariants"* — which any architecture paper can say — into
*"these ten properties are decidable, here is the procedure that decides them, and here is a
compliant implementation."* A reviewer verifies it by running `pytest`.

D-23 was attacked structurally rather than by tuning, with two experiments. One worked well, one
worked partially, and both are reported.

| | Result |
|---|---|
| Invariants executable | **10 / 10**, holding on 200 randomised well-formed states |
| Negative tests | **16**, one per invariant plus edge cases; each catches its own violation |
| Test suite | 78 → **294 passing** |
| D-23 mitigation A — credible sets | Coverage beats point accuracy at every δ, but **falls short of nominal** under severe misspecification |
| D-23 mitigation B — pool across topics | δ = 0.30: accuracy **83.8% → 95.8%** with 8 topics; offset error 0.187 → 0.092 |

---

## 1. The invariants, as a specification

`shadow_mirror/invariants.py` exposes `check_i_…` through `check_x_…` and a `check_all` runner. Each
returns a verdict plus the observation that produced it, and **never a score** — a property that
holds by construction is not an experimental result, and reporting it as a percentage is precisely
how the original benchmark suite's "100%" figures came to be mistaken for evidence.

Two invariants resisted mechanical checking and were operationalised deliberately rather than
fudged:

**VI (Context Consistency)** cannot mean "recompute the past" — an instrument cannot re-run a
person's week. It is operationalised as: *when a context is superseded, every conclusion that
depended on it is annotated as stale, rather than silently retained or silently deleted*. The URG
gained `revise_context()`, which supersedes a context and marks its dependents. Both branches are
tested: a graph that supersedes a context by hand fails the check; one that uses `revise_context`
passes and the dependent carries `stale=True`.

**X (Human Authority)** is a property of what reaches the person, so it is checked at the output
boundary: every terminal output carries its uncertainty and disclaimer and offers at least one
question, and none is phrased as a verdict about who someone is.

**IX (Transactional Consistency)** needed the URG to actually be transactional. It gained a
`transaction()` context manager that snapshots and rolls back. The negative test subclasses the graph
with a no-op transaction, provokes a failure mid-update, and confirms the check catches the partial
write.

### The property harness

`build_well_formed(seed)` constructs a randomised reflective state — 2–5 observations, derived
evidence with multiple provenance parents, 2–4 hypotheses with a mix of supporting and contradicting
edges, real belief updates, planned inquiries, and an explanation — and all ten invariants are
asserted over 200 seeds.

The generator is a small seeded builder rather than a property-testing library, because the package
has **no runtime dependencies** and adding one for the test suite alone would undercut the
auditability argument the architecture rests on.

### The check that caught itself

Pointing the Invariant X check at the *shipped* reflection prompts rather than at a fixture
immediately produced a failure:

```
1 verdict phrasing(s); first offender: ('\byou have\b',
'(caution) You have consulted this 5 times. Seeing a guess changes late…')
```

That is the reactivity caution — a factual statement about the person's own logged behaviour, and
one the architecture specifically wants surfaced. **The defect was in the check, not the system.**
The patterns were narrowed to claims about who someone is (`you are`, `you secretly`, `your true`,
`you have a/an`) and directives (`you must`, `you should`), and the rationale is recorded in the
source.

It is worth saying plainly why this matters: a conformance suite that is only ever pointed at
fixtures will pass, and will be worthless. This one was pointed at real output on its first run and
found something within a minute.

---

## 2. D-23 — overconfidence under severe misspecification

Session 3 measured the problem: when the model's assumed corners are displaced from where a person's
evidence actually sits, the engine becomes *more* confident as evidence accumulates while accuracy
collapses (ECE 0.151 → 0.221; at the worst cell, abstaining 21% while wrong 54%).

Tuning the abstention threshold cannot fix that, and Session 3 deliberately did not try. The failure
is **identifiability**: a two-channel location model cannot distinguish "state A, displaced" from
"state B" when the displacement points toward B. So the fix has to change either *what is reported*
or *what is observed*. Both were tried.

### A — Report a set, not a label

`credible_set()` returns the smallest set of hypotheses carrying the requested posterior mass.
Correctness then means **coverage**: does the reported set contain the truth at the nominal rate?

*n* = 400 per cell, 8 evidence pairs, nominal coverage 90%:

| δ | Point accuracy | Credible-set coverage | Mean set size | Commits to one |
|---|---|---|---|---|
| 0.00 | 100.0% [100.0, 100.0] | 100.0% [100.0, 100.0] | 1.00 | 99.8% |
| 0.15 | 98.2% [96.8, 99.2] | **99.5% [98.8, 100.0]** | 1.08 | 93.5% |
| 0.30 | 78.2% [74.2, 82.0] | **88.0% [85.0, 91.2]** | 1.45 | 66.0% |
| 0.45 | 51.7% [46.8, 56.5] | **60.5% [55.5, 65.2]** | 1.48 | 62.7% |

Coverage beats point accuracy at every level, at a cost of about half a hypothesis in set size, and
the system commits to a single reading two-thirds of the time even under severe misspecification.

**But it does not reach nominal.** At δ = 0.45 a set claiming 90% mass contains the truth 60.5% of
the time. This is not a bug in the set construction — it is the posterior's miscalibration passed
through. **A credible set inherits the calibration of the posterior it is drawn from.** Getting
nominal coverage under misspecification requires calibrating against held-out labelled outcomes
(conformal prediction), and labelled outcomes for a person's latent state do not exist without the
human study. That is a real dependency, and it is now an explicit input to Session 15's design
rather than a hope.

### B — Estimate the displacement instead of tolerating it

If a person is systematically displaced — they habitually under-report confidence relative to
performance — then the displacement is a property of the *person*, shared across topics, and becomes
estimable by pooling. One topic cannot see it; several can.

`estimate_person_offset()` alternates hard assignment and offset estimation (a two-step EM).
*n* = 400 simulated people:

| δ | Topics | Accuracy, uncorrected | Accuracy, offset-corrected | Offset error |
|---|---|---|---|---|
| 0.30 | 1 | 81.2% [77.5, 85.0] | 81.2% (no pooling possible) | 0.187 |
| 0.30 | 3 | 82.8% [80.7, 85.0] | 87.5% [85.7, 89.3] | 0.141 |
| 0.30 | 5 | 82.3% [80.5, 84.0] | 90.8% [89.5, 92.1] | 0.120 |
| 0.30 | **8** | 83.8% [82.5, 85.0] | **95.8% [95.0, 96.4]** | **0.092** |
| 0.45 | 1 | 53.0% [48.2, 58.0] | 53.0% | 0.420 |
| 0.45 | **8** | 53.2% [51.6, 54.9] | **61.3% [59.6, 62.9]** | 0.364 |

At moderate displacement this is a clean structural win: **83.8% → 95.8%** with eight topics, and it
comes from observing more, not from tuning anything.

At severe displacement it helps much less (53.2% → 61.3%), and the reason is visible in the offset
error, which barely moves (0.420 → 0.364). Hard-assignment EM initialises from an assignment that is
mostly wrong at δ = 0.45, so it converges to a poor local optimum. The textbook remedy is soft
assignment weighted by the posterior, with restarts. I have **not** implemented it this session:
having made one deliberate parameter decision already, adding another change whose effect I would
then measure on the same benchmark is how tuning starts. It is scheduled, and named.

### Status of D-23

Downgraded from **high, open** to **characterised, partially mitigated**:

- The failure mode is identified as identifiability, not thresholding.
- One mitigation is measured and substantial at moderate misspecification (multi-topic pooling).
- One mitigation improves the honest reporting at all levels but does not reach nominal coverage
  (credible sets).
- The residual gap has a named cause (posterior miscalibration), a named remedy (conformal
  calibration), and a named blocker (needs labelled outcomes, i.e. the human study).

That is a defensible limitations paragraph. It was not one before.

---

## 3. What can now be claimed

**Claimable, with running code:**

- The ten architectural invariants are decidable, and a compliant implementation exists. All ten hold
  over 200 randomised reflective states; each is accompanied by a negative test proving the check can
  fail.
- Reporting a credible set instead of a point label increases the rate at which the true state is
  contained in the output at every level of model misspecification tested (e.g. 78.2% → 88.0% at
  δ = 0.30), at a mean cost of 0.45 additional hypotheses.
- A person-level displacement is recoverable by pooling across topics: 83.8% → 95.8% accuracy with
  eight topics at δ = 0.30, offset error 0.187 → 0.092.

**Explicitly not claimable:**

- Nominal coverage. A 90% credible set contains the truth 60.5% of the time under severe
  misspecification, and the paper must say so.
- Any benefit of offset correction at severe displacement beyond the 8-point gain measured, which is
  limited by the estimator's initialisation.

---

## 4. Still open

| Defect | Severity | Session |
|---|---|---|
| D-02, D-04, D-05, D-18 — the Kimi paper: fabricated statistic, six wrong citations, vendor watermark, quarter-length | Critical | 6, 11 |
| D-23 residual — nominal coverage needs conformal calibration | Characterised | 15+ (blocked on labelled outcomes) |
| D-26 (new) — soft-assignment EM for offset estimation at severe displacement | Low | 12 |
| D-17 — figure labels contain literal `\n` | Low | 12 |
| Ambivalence as residual bucket (Session 4 watch item) | Watch | 8 |

---

## 5. Reproducing

```bash
unzip shadow_mirror_v1.0.zip && cd shadow_mirror_v1.0
pytest -q                    # 294 passed
python conformance_v10.py    # prototype 4/7 vs v1.0 7/7
python experiment_d23.py     # credible-set coverage + offset recovery
```

---

*Session 06 — verifying the monograph's 96-entry bibliography against live sources — continues
automatically.*
