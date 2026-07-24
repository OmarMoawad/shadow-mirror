# Ethics & scope — read before extending

This tool has two modes, and the line between them is the whole ethical design:

1. **Self-mirror** — a person holds the mirror about *themselves*.
2. **Consented study** — a person studies *another person who has given informed,
   granular, revocable consent to be studied*.

Mode 2 was added deliberately, and only in a form that keeps the guardrails
load-bearing. The thing that makes it defensible is not that the inference is
gentle — it is that **the subject agreed, knew what they were agreeing to, and can
stop it at any moment**. Remove that, and you do not have a more powerful tool; you
have covert profiling, which is the exact thing the earlier self-only build
refused. Consent is the load-bearing wall. Do not knock it out.

## Hard lines

1. **No study without active, per-stream consent.** Every datum about another
   person passes through a consent gate (`study.py` → `consent.py`). No grant, no
   datum — the code raises rather than records. Never add a path that bypasses it,
   and never pre-fill a consent flow for someone who is not present and agreeing.

2. **Granular, not blanket.** "Yes to everything forever" is *not* informed
   consent — nobody can be informed about what they can't foresee. Each data
   stream is granted on its own. The streams a person **cannot notice about
   themselves** (implicit measures, physiological arousal, micro-avoidance) require
   their *own explicit acknowledgement* and cannot be bundled. This is the point
   the subject most needs spelled out, so it is enforced in code.

3. **Never covert.** No hidden logging, no inference about someone who has not
   granted consent and been shown what it means. Provenance (which consented
   stream) rides on every encounter so this stays auditable.

4. **Revocable, inspectable, correctable, erasable — by the subject.** Consent can
   be withdrawn instantly (and wipes by default); grants lapse and must be
   re-affirmed; the subject can see and correct everything held about them. These
   are the subject's rights, not features you may trim.

5. **Questions, not verdicts.** Output is always an open-ended, dated question.
   Never add a feature that prints "this person is X" or a fixed profile — not for
   the self, and *especially* not for another person.

6. **Arousal is not desire.** High arousal + avoidance is a *threat-response*
   hypothesis first, and it surfaces first — in the self-mirror AND in the
   counter-pattern engine. When a reaction "turns into avoidance" over time under
   high arousal, that is read as *became unsafe*, never as *revealed a hidden
   dislike*. This is the trauma landmine; it is structural, not a tuning knob.

7. **Dated snapshots, never identities.** A reading is about a moment or a
   trajectory of moments — not who someone *is*. The weights encode the *shape* of
   the hypotheses, not calibrated truths about human beings.

## Never use this for

Hiring, policing, surveillance, romantic or social manipulation, political
persuasion, clinical diagnosis, credit or eligibility decisions, or judging
anyone's morality — **with or without consent**. Consent authorises study for
understanding; it does not authorise using a person's own data against their
interests. If a use would harm someone were the guess wrong, do not build it.

The honest test of "noble purposes": would you run this flow with the subject
reading over your shoulder, and would they still say yes? If not, it isn't noble —
it's covert with extra steps.

## On PPDS

Per the standing synthesis: this is a research thread, **not** a near-term PPDS
feature. Folding an unvalidated psychological-inference engine — now with a
consented other-person mode — into a health product before PPDS itself is
validated adds the riskiest feature to the least mature part of the stack. If it
ever becomes a PPDS module, only after PPDS is validated, and any other-person use
stays behind the same consent gate that ships here.

## The honest first test

The most useful prototype still isn't the code — it's you, on yourself, over a few
weeks, watching whether these questions actually help. If they help you, they may
help a consenting other. If they don't, no Bayesian machinery saves the idea.
