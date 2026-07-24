# Ethics & scope — read before extending

This tool was built to the *narrowest defensible form* your concept documents and
both external critiques agreed on. The guardrails below are load-bearing. Removing
them does not make a more powerful version of this tool; it makes a different,
harmful one.

## Hard lines

1. **Self-owned only.** The person holds the mirror about *themselves*. Do not add
   any mode where one person profiles another. The original "engineer gets
   acquainted with the people around him" framing is covert profiling with a kind
   face — the critiques flagged it, and this build deliberately does not support it.

2. **Never covert.** No hidden logging, no inference about someone who did not log
   their own data and acknowledge consent.

3. **Questions, not verdicts.** The output is an open-ended question. Do not add a
   feature that prints "you are X" or a fixed personality profile.

4. **Arousal is not desire.** High arousal + avoidance is a *threat-response*
   hypothesis first. Never collapse it into "secretly wants". This is the trauma
   landmine; it is structural, not a tuning knob.

5. **Dated snapshots, never identities.** A reading is about a moment. Do not build
   anything that treats an output as an enduring trait.

6. **The weights are not validated.** They encode which corner of evidence means
   which hypothesis — not calibrated truths about human beings. Do not present any
   number here as a measurement of a person.

## Never use this for

Hiring, policing, romantic manipulation, political persuasion, clinical diagnosis,
credit or eligibility decisions, or judging anyone's morality. If a use would harm
someone were the guess wrong, do not build it.

## On PPDS

Per your own synthesis: this is a research thread, **not** a near-term PPDS feature.
Folding an unvalidated psychological-inference engine into a health product before
PPDS itself is validated adds the riskiest feature to the least mature part of the
stack. If it ever becomes a PPDS module, only in the self-owned form, and only
after PPDS is validated — with the mentor never seeing a profile.

## The honest first test

The most useful prototype isn't the code — it's you, on yourself, over a few weeks,
watching whether these questions actually help. If they don't, no Bayesian
machinery saves the idea. If they do, the concept has legs.
