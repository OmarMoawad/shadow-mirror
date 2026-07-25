# Shadow Mirror — Session 17: The Workaround Hunt

**Author of record:** Omar Moawad · **The American University in Cairo** · **Session date:** 25 July 2026
**Instruction:** *"create a to-dos pending draft at the very end of the paper to include all remaining
pending work … THAT YOU CAN NOT FIND AN ONLINE ALTERNATIVE OR A WORK AROUND IT"*

That instruction inverts the usual order. A limitations section is normally written by listing what you
did not do. This one had to be written by *searching for a way to do each thing first*, and recording
only the residue. Eleven candidate items went in. **Six dissolved. Five survived.**

---

## 1. What a search resolved

### 1.1 Two blocked instruments had free replacements all along

Sessions 15 and 16 left four instruments permission-blocked and listed four emails as the fix. Two of
those emails turn out to be unnecessary.

**Values.** The PVQ-RR was blocked twice over — permission-gated, and its item-to-value mapping file
returned HTTP 403. The **ESS Human Values Scale (PVQ-21)** measures the same construct and is free in a
way that is unusually well documented:

- Items published in full, in GESIS ZIS Table 1 and in every ESS source questionnaire.
- **The item-to-value mapping is published** in ZIS Table 2 — the exact thing the 403 was hiding.
- Two independent grants. ESS ERIC: *"European Social Survey documentation is licensed under CC BY-SA
  4.0"* — no NonCommercial clause, no NoDerivatives clause, so translation is permitted. And GESIS ZIS:
  *"The measurement instrument documented here can use free of charge for non-commercial research
  purposes."* **Schwartz is a named author of the ZIS record**, so the second grant is the instrument
  author's own.
- **An official Arabic version already exists**, fielded by ESS in Israel and hosted by the B. I. Cohen
  Institute at Tel Aviv University. It is Levantine Arabic rather than Egyptian, so dialect review and
  cognitive pretesting are still required — but adapting a professionally TRAPD-translated instrument
  is a smaller and far more defensible job than translating from English.

Cost of the substitution: **10 basic values instead of 19 refined ones**, from 2–3 items each. If a
downstream distinction ever needs societal versus natural universalism, this instrument cannot supply
it. Scoring requires ipsatising — subtract each respondent's mean across all 21 items before comparing
profiles — because values are relative by construction.

One implementation detail worth stating because it is easy to get backwards: ESS codes **1 = "very much
like me"**, so a low raw score means high importance. All 21 items are reverse-scored in our registry so
that a high subscale score means the value matters more, and a test asserts it.

**Wisdom.** The 3D-WS was permission-gated. The **revised Adult Self-Transcendence Inventory** (Koller,
Levenson & Glück 2017) is **CC BY 4.0**, and the reason that matters is structural: **Michael Levenson,
author of the original ASTI, is a named co-author and therefore one of the copyright holders granting
the licence.** It is dimensional across five subscales, and the authors argue explicitly against a
total — *"if some items measure non-attachment while others measure self-knowledge, and these two
constructs can occur independently, then summing up across all items is not informative"* — which is
exactly the commitment this architecture already makes.

**Construct drift is real here and is declared in the caveats.** The ASTI measures *self-transcendence*,
not wisdom. Non-attachment and peace-of-mind overlap Ardelt's reflective and affective dimensions
reasonably; there is **no analogue of her cognitive dimension**, knowledge of the limits of knowing. It
substitutes for the dimensional *form*, not for the construct.

**A trap avoided.** The Brief Wisdom Screening Scale looked like an easier escape — it is CC BY. But its
Table 6 labels each item by source scale, and the sources include Ardelt's 3D-WS. Glück et al. are not
Ardelt and cannot license her items. **Adopting the BWSS to escape Ardelt's permission gate walks
straight back into it.** The same shape defeats the Arabic Claremont paper: CC BY article, but Bronk is
not among its authors, so its licence does not license his items.

### 1.2 "Coverage is unmeasured" became a number, and the number is middling

Both papers previously conceded that nothing measured whether the randomised harness exercises the
state space in any principled sense. Mutation testing measures precisely that, and it took an hour.

**5,114 mutants. 2,319 killed. 1,549 survived. Mutation score 59.9%.** A further 1,244 sit in code with
no covering test at all — 909 of those in a command-line interface that has never had tests and carries
no claim in either paper.

Survivors concentrate in the engine (404), the pattern layer (278), **the invariant checks themselves
(206)** and the formation model (195). A sampled inspection shows most are label and message mutations
rather than behavioural ones, so the raw score understates the suite.

**But one class was not cosmetic, and it is the finding of the session.** Mutating an invariant's own
identifier from `"I"` to a nonsense string **survived**. So did replacing its human-readable name with
`None`. No test asserted that a check returns the invariant it claims to be — meaning this paper's
central contribution, a catalogue of eleven *named* architectural properties, could have been silently
renamed and nothing would have noticed. Two tests now close it, one asserting per-check identity and
one asserting that `check_all` returns exactly `I` through `XI` without duplicates.

That is the fourth time in this programme a property has been found by measurement rather than by
intent, and it is the most embarrassing of the four, because it is a gap in the checking apparatus
itself.

We report 59.9% rather than tuning it first. A mutation score is a lower bound on test strength and an
upper bound on nothing, and 59.9% is middling for a package that makes conformance claims.

### 1.3 The other three

**Independent execution** had a route we had not looked for. Venue artifact tracks are genuinely closed
— **none of TiiS, FAccT or AIES operates one** an author can enter at submission — but **CODECHECK** is
live, free, accepts submissions on the basis of a preprint alone with no venue tie, and ends in a Zenodo
DOI certificate naming the person who ran the code. It certifies execution rather than correctness,
which is exactly the claim we need. It is an action, not a limitation.

**Distribution-free coverage guarantees** (D-23) were blocked on labelled outcomes. Two of the three
Route A corpora supply an item-matched choice that can contradict a stated preference, so this becomes
available under the secondary analysis — for the preference model only. The safety claim is untouched.

**Two dead ends worth recording so nobody re-walks them.** ReScience C and the ML Reproducibility
Challenge both publish work written *by* the replicator; neither has any mechanism to accept an artifact
and find someone to run it. And JOSS changed its scope on 5 January 2026 to require *demonstrated*
research use — *"aspirational statements about future use are not sufficient"* — so it now presupposes
the deadlock it used to break.

---

## 2. What survived: the five irreducible items

These are now **Appendix C** of P1 and **Appendix B** of P2, each with a companion table showing what a
search resolved, so a reader can tell genuine blockage from mere inconvenience.

**1. The threat-confound claim requires primary collection.** ~40 datasets assessed. The four-way
intersection — stated stance, contradictable choice, time-locked arousal, coercion manipulation — does
not exist publicly, and the failure is structural rather than incidental.

**2. No instrument in the battery is validated in an Egyptian sample.** Confirmed Arabic validations are
Lebanese, Saudi, Omani, Jordanian, Palestinian, Qatari, Moroccan. Four Egyptian-journal leads were
identified by DOI but every `*.ekb.eg` host was unreachable, and Egyptian psychometric papers frequently
build local instruments rather than translating, so relevance cannot be assumed. **A colleague with
Egyptian institutional access resolves this in minutes; open search does not.**

**3. Two constructs have no free replacement.** There is no openly licensed eight-theme Eriksonian
inventory — the two structurally correct candidates are both permission-gated, and going upstream from
one to the other does not escape the gate. The free material covers two of eight themes and yields
single scores. For purpose beyond the MLQ, nothing free was found.

**4. No party outside this project has executed the software.** The venue route is verified closed.
CODECHECK is available and unused as of writing, so the paper claims the code is inspectable, not that
it has been independently run.

**5. Invariant X and the question generator are syntactic proxies.** We know of no decision procedure
that settles whether a sentence claims authority over a person, and we do not think one follows from
more patterns. A research problem, not an unfinished task.

**Explicitly excluded from the appendix**, per your instruction: two unimplemented operators recorded as
strict `xfail`s, the linear read path, a candidate drift state, and the 1,549 surviving mutants. None is
blocked on anything external. They are simply not done, and including them would dilute a list whose
whole value is that every entry has been searched for and not found.

---

## 3. State

| | |
|---|---|
| Package | v1.2.1 — **679 passed, 2 xfailed** (was 671) |
| Instruments | 13 registered, **5 administrable** (was 2): MLQ, BPNSFS, **ESS-HVS**, **ASTI-R**, LGS |
| Permission emails still needed | **2, not 4** — Bronk (CPS) and Darling-Fisher (MEPSI) |
| Mutation score | **59.9%**, weakest modules named |
| P1 | 8,783 words, 58 refs, new §10.1 and Appendix C |
| P2 | 9,441 words, 56 refs, new §9.1 and Appendix B |

**Not done this session, and next:** the Route A secondary-analysis pipeline against BIRAFFE2, FOODEEG
and Urban Appraisal, and the AUC IRB packet. Both were scoped and neither was built — the workaround
hunt took the session, and it was the right trade, because two of its findings changed what the other
two sessions should contain.

**One operational note.** I can write the Route A loaders against each corpus's published data
dictionary, but I cannot pull the archives themselves into this environment. Those three downloads are
yours, and they are three commands; I will supply them with the pipeline.
