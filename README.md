# Shadow Mirror

A consent-based, probabilistic **reflection** engine, in two modes:

1. **Self-mirror** — you hold the mirror about *yourself*.
2. **Consented study** — you study *another person, only with their informed,
   granular, revocable consent* (see below and [`ETHICS.md`](ETHICS.md)).

It does **not** classify who a person "really is." It estimates *dated, uncertain*
hypotheses about the tension between what someone **says**, what they can **do**,
and what they **do** — and turns those tensions into **questions to sit with**,
never verdicts.

This is the buildable form the concept documents and both external critiques
converged on: not a "shadow algorithm" that reads people covertly, but a mirror
that holds contradictions up — dated, un-collapsed — and, when it is pointed at
another person, only ever with that person's eyes-open agreement.

## Why it's shaped this way

| Concept-doc concern | How the code answers it |
|---|---|
| No ground truth for "unknown" quadrants | Posterior *distributions* over states; refuses to infer below a minimum of paired evidence |
| Fluidity — states shift by the hour | Every output is a **dated snapshot** with an uncertainty interval; an instability flag when snapshots disagree |
| Heisenberg / reactivity | A `reactivity` caution that grows the more you consult it |
| Trauma landmine | `threat_response` is a **first-class hypothesis**; arousal + avoidance is never collapsed into "want", and its caution surfaces *first*, even under suppression |
| "Output is a question, not a profile" | The reflection layer only ever emits open-ended questions |
| Contradiction is often the fact, not a puzzle | A first-class **`ambivalence`** state holds "wants and doesn't want at once" un-collapsed, instead of forcing a winner |
| Per-question, not one global type | **Topic scoping** keeps "algebra" and "public speaking" separate |
| Stale readings shouldn't dominate | **Temporal decay** (configurable half-life) + per-observation **reliability** weights |
| Right to inspect / correct / refuse | Local JSON, full `export`, irreversible `forget` |

## Architecture (four layers)

```
Observation  →  Inference        →  Safety              →  Reflection
(what you     (Bayesian posterior   (threat / reactivity   (questions,
 log, dated)   over hypotheses)      / instability guards)   never labels)
```

- `models.py` — timestamped observations and dated belief snapshots
- `engine.py` — the Bayesian latent-state inference (deterministic, stdlib-only)
- `safety.py` — the confound and over-interpretation guards
- `reflect.py` — turns a posterior into questions
- `store.py` — local, self-owned persistence with consent, export, and delete
- `cli.py` — the `shadow` command

## Install / run

No dependencies. Standard library only (Python ≥ 3.9).

```bash
# from this folder
python -m shadow_mirror consent          # acknowledge self-use terms (once)
python -m shadow_mirror log knowledge self_report 0.9 -t recursion -c "feel solid"
python -m shadow_mirror log knowledge task_performance 0.3 -t recursion -c "quiz"
python -m shadow_mirror reflect -t recursion   # questions to sit with (scoped)
python -m shadow_mirror report  -t recursion   # full posterior + safety, as JSON
python -m shadow_mirror topics                 # list topics + evidence counts

python demo.py                            # a scripted walkthrough (4 scenarios)
```

Flags for `log`: `-t/--topic` (what it's about), `-c/--context` (free text),
`-r/--reliability` (0..1, how much to trust this one datum).

Optional install so you can just type `shadow`:

```bash
pip install -e .
shadow reflect
```

### Signals you can log

`AXIS` ∈ `knowledge | desire`. `VALUE` ∈ `[0, 1]`.

| SIGNAL | Axis | Meaning |
|---|---|---|
| `self_report` | both | stated confidence / stated want |
| `task_performance` | knowledge | how you actually performed |
| `behavior` | desire | how much you actually approached |
| `implicit_task` | desire | an indirect approach/avoidance measure |
| `physiological` | desire | arousal proxy — **threat confound only** |
| `avoidance` | desire | observed avoidance — **threat confound only** |

The engine needs at least **2 paired observations** on an axis before it will say
anything. That restraint is intentional.

## Studying a consenting other person

The second mode does what "get to know the people around you" was *supposed* to
mean — minus the covert part. It reads a person's **first reaction** to a
recurring condition, watches how that reaction can invert into a
**counter-pattern** across encounters, and models **emotion as the antecedent
cause that bends the behaviour** (appraisal theory: a condition is appraised, the
appraisal *is* the emotion, the emotion carries an action tendency). It is
idiographic — per person, per condition — because the same condition evokes
different emotions in different people.

None of it runs without consent. Consent is **granular and revocable**: each data
stream is granted on its own, and the streams a person *cannot notice about
themselves* (implicit measures, physiological arousal, micro-avoidance) require
their own explicit acknowledgement — they cannot be bundled under a blanket yes.
No grant, no datum; the code refuses rather than records.

```bash
shadow subject consent alex                      # informed, per-stream consent flow (run it WITH them)
shadow subject encounter alex "criticism" \
      --valence 0.30 --action 0.15 --arousal 0.4 --stream self_report
# ... log more encounters with the same condition over time ...
shadow subject patterns alex -c criticism        # first-reaction / counter-pattern questions
shadow subject records alex                       # everything held about them (their right to see)
shadow subject revoke alex                         # withdraw consent + wipe their data
shadow subject list                                # subjects, consent state, counts
```

**What it reports** for a condition: the first reaction; whether a counter-pattern
emerged; and — the interesting part — its *driver*:

- **`coupling_shift`** — the behaviour reversed while the feeling stayed the same:
  the *same emotion* came to bend the behaviour the other way (adaptation/learning,
  not a changed heart).
- **`emotion_shift`** — the feeling itself flipped, and the behaviour followed.
- **`both`** — feeling and behaviour both reversed.

Plus an **emotion-as-cause** coupling (how valence/arousal predict approach vs.
withdrawal *for this person, here*) — always as a small-sample hypothesis, never a
proven mechanism.

The trauma guard carries over intact: if the later reactions are high-arousal
withdrawal, that is flagged as a **safety response** and surfaced *first* — never
relabelled as "they revealed a hidden dislike."

```python
from shadow_mirror import ConsentGrant, Study

grant = ConsentGrant("alex", purpose="understand our recurring friction")
grant.domains = {"reaction_patterns", "emotion_behavior"}
grant.add_stream("self_report")
grant.add_stream("physiological", acknowledged_non_obvious=True)  # explicit, per-stream

study = Study(grant)
study.observe("criticism", valence=0.30, action=0.15, arousal=0.5)  # refused if stream ungranted
# ... more encounters over time ...
print(study.patterns("criticism").questions)
```

## Library use

```python
from shadow_mirror import ShadowMirror, reflective_prompts

m = ShadowMirror()
m.add_batch([
    ("knowledge", "self_report", 0.9),
    ("knowledge", "task_performance", 0.3),
    ("knowledge", "self_report", 0.85),
    ("knowledge", "task_performance", 0.35),
])
print(m.report())
for q in reflective_prompts(m):
    print(q)
```

## Tests

```bash
pip install pytest
pytest
```

The tests verify the *commitments*, not just the plumbing: sufficiency gating,
each evidence corner pulling the right way, and — most importantly —
`test_safety.py` proving arousal + avoidance is **not** read as a hidden want.

## What this is not

Read [`ETHICS.md`](ETHICS.md) before extending it. In short: never point it at
another person, never use it covertly, never treat a most-likely label as truth.
The weights encode the *shape* of the hypotheses, not validated facts about people.

## Status

`v0.3.0` — adds the **consented-study** mode: a granular/revocable consent layer
(`consent.py`), a consent-gated study session (`study.py`), and the
first-reaction / counter-pattern engine with emotion-as-cause (`patterns.py`).
The self-mirror (`engine.py`) is unchanged. Grounded in the research on *dynamic
consent*, *appraisal theory / action tendencies*, *idiographic EMA & state
transitions*, and the known validity limits of implicit/physiological affect
signals — hence: hypotheses, not verdicts.

Still a named research thread. It is **not** wired into PPDS and should not be
until PPDS itself is validated; any other-person use stays behind the consent gate
that ships here. Read [`ETHICS.md`](ETHICS.md) before extending — the consent gate
is the load-bearing wall.

Prior: `v0.2.0` folded in temporal decay, reliability weighting, topic scoping,
and the `ambivalence` state, keeping the deterministic Gaussian-corner inference,
local JSON storage, and the tested trauma guard.
