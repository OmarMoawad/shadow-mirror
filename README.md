# Shadow Mirror

A consent-based, self-owned, probabilistic **self-reflection** engine.

It does **not** classify who a person "really is." It estimates *dated, uncertain*
hypotheses about the tension between what you **say** (self-report), what you can
**do** (performance), and what you **do** (behaviour) — and turns those tensions
into **questions you may choose to sit with**, never verdicts.

This is the buildable form your concept documents and both external critiques
converged on: not a "shadow algorithm" that reads people, but a self-owned mirror
that holds contradictions up, dated and un-collapsed, and refuses to pick a winner.

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

`v0.2.0` — a working prototype of the *self-owned* form only. Per your own
synthesis, this stays a named research thread; it is **not** wired into PPDS, and
should not be until PPDS itself is validated.

`v0.2.0` folded in the genuinely-additive ideas from a parallel research
prototype: temporal decay, reliability weighting, topic scoping, and the
`ambivalence` state — while keeping the deterministic Gaussian-corner inference,
local JSON storage, and the tested trauma guard.
