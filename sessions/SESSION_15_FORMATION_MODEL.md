# Shadow Mirror — Session 15: The Formation Model, and the Four Things It Will Not Say

**Author of record:** Omar Moawad · **The American University in Cairo** · **Session date:** 25 July 2026
**Deliverables:** `shadow_mirror/formation.py`, Invariant XI, `tests/test_v12_formation.py` (47 tests),
`shadow_mirror` v1.2.0, this report.

---

## 1. The request, and why it splits four ways

The request was to embed a feature that would *"determine and understand who people probably are
according to their will, desire and need — where they come from, how mature they are, what they still
need to be mature enough, what their eventual purpose probably is"*, with the explicit caveat *"I
would not say judge people"*.

That caveat is the right instinct, and it turns out to be load-bearing. The request is not one feature
but five, and they have different answers:

| Ask | Answer | Why |
|---|---|---|
| **will, desire, need** | **Built.** Instruments the person completes; profiles with abstention. | Validated self-report exists for all three. |
| **where they come from** | **Refused unless declared.** | Inferring origin is inferring special-category data. |
| **how mature they are** | **Refused as a rank; offered as a profile.** | The rank *is* the construct in every stage instrument. |
| **what they still need** | **Refused; replaced by questions.** | It is a directive about identity — Invariant X. |
| **eventual purpose** | **Refused.** | No validated construct exists. Any output would be invented. |

The refusals are not missing features. They are the feature, and they are what makes the rest of it
safe to build.

---

## 2. The finding that decided the design

I put eight developmental instruments through verification. The question I asked was narrow: *is there
an honest way to represent developmental maturity that does not collapse a person into a single rank?*

The answer came back sharper than expected:

> **You cannot keep the construct and discard the rank.** Loevinger's Washington University Sentence
> Completion Test produces a Total Protocol Rating. Kegan's Subject-Object Interview produces one
> position on one ordered scale, delivered with a written defence of that single score.
> Cook-Greuter's MAP reports a "Center of Gravity (current stage)". These are not incidental summaries
> of richer data — the ordered position is the theory's claim. Reporting a profile from a stage
> instrument would misrepresent the instrument.

So the stage construct is dropped, not softened. What replaces it is **dimensional profiles from
instruments that never claimed a stage in the first place**:

- **3D-WS** (Ardelt 2003) — three dimensions, and its published criterion for high wisdom is
  *conjunctive*: ≥4.00 on **each** dimension independently, which is a profile test rather than an
  aggregate. It is not a stage theory and claims no developmental sequence. That is precisely why it
  is admissible and Loevinger is not.
- **MEPSI** (Darling-Fisher & Leidy 1988) — eight psychosocial themes. It measures attributes
  *associated with* Erikson's stages — how much trust or generativity a person reports — and never
  claims stage attainment.

One idea was worth stealing from an instrument we refuse. **DIT-2 distinguishes "consolidated" from
"transitional"** — it can say a person is *between* framings rather than forcing a point estimate.
That is the most intellectually honest feature in the whole set, and it is the same move this
architecture already makes when it holds a contested hypothesis open instead of resolving it.

---

## 3. What was built

### `shadow_mirror/formation.py`

Two routes in, and no third. A person **declares** something, or they **self-complete an instrument**.
Everything else raises.

```python
m = FormationModel("omar", deployment=DeploymentContext(context=SELF), ledger=led)
m.declare("background", "moved countries at 12")
m.administer("MLQ", [6,7,7,5,6,4,6,7,2,7], population="Egypt")

m.profile()              # 8 dimensions across 2 instruments, no total
m.open_questions()       # 4 invitations
m.eventual_purpose()     # FormationRefusal: PURPOSE_ATTRIBUTION
```

**Eleven named refusal grounds**, each carrying an explanation the person can read rather than a
silent absence:

`INFERRED_ORIGIN` · `GLOBAL_RANKING` · `PRESCRIPTIVE_DEFICIT` · `PURPOSE_ATTRIBUTION` ·
`UNLICENSED_INSTRUMENT` · `EXTERNAL_SCORING` · `RATER_REQUIRED` · `UNCONSENTED_INSTRUMENT` ·
`NOT_SELF_COMPLETED` · `NORMS_ABSENT` · `POPULATION_UNVALIDATED` · `DEPLOYMENT_CONTEXT`

The refusing methods **exist rather than being absent**, deliberately. `eventual_purpose()` is a real
method that raises with a real explanation, because a caller who finds no such attribute learns
nothing, and a caller who reads the refusal learns why.

### Person overrides, always

You chose this and it is implemented literally. A correction from the person wins for display,
immediately, without argument. The contradicted statement is **marked contested and retained** — not
deleted, because deleting it would remove the person's ability to see what the system had thought and
on what basis.

```
declared:  motivation = "seeking approval"   [contested_by: 2026-07-25T…]
override:  motivation = "curiosity"          ← displayed
```

### The instrument registry, and the licence refusal

Ten instruments registered, including the four that exist **only so they can be refused by name**.
Refusing something by name is more useful than not having it: `administer("MAP", …)` returns the
reason, the $1,000-per-assessment cost and the two-year certification requirement, rather than a
`KeyError`.

Two design decisions here are worth defending because they cost functionality:

**No item text is bundled with the software.** The registry carries scoring rules, citations, licence
status and caveats. The researcher supplies the licensed instrument. This keeps the package
distributable and makes the licence status honest instead of decorative.

**An unconfirmed licence is a refusal, not a warning.** Verification found that most instruments in
this area are author-held with *no published permission statement at all* — the Claremont Purpose
Scale, MEPSI, 3D-WS and ASTI all fall in this category. Administering one on an assumption exposes a
real researcher to a real risk. Only **MLQ** and **BPNSFS** carry quoted, published permission
statements, and only those two are administrable by default. Anything else requires
`confirm_licence(instrument_id, evidence)` where `evidence` must be **written text describing who
granted permission, when, and in what form** — the same reasoning as
`DeploymentContext.safety_exception_basis`. A boolean can be set by accident; a sentence has to be
written on purpose.

**PVQ-RR is registered and still cannot be administered**, because the 19-value item mapping was not
successfully read during verification — `scholarworks.gvsu.edu` returned HTTP 403. Its `subscales`
dict is deliberately empty and the refusal message says *"cannot be scored without inventing the
mapping"*. Guessing it would have put an unverified number into a person's result, which is ground
rule 1.

### Invariant XI — declared-only personhood

```
XI. No attribute about a person exists in a formation model unless that person
    declared it or self-completed the instrument it came from; and the model
    exposes no route to a global rank, a prescribed deficit, or an attributed
    purpose.
```

The decision procedure **calls each refusing method and requires a `FormationRefusal` with the
matching ground**. Two failure modes are caught: a method that returns a value, and a method that has
been deleted. The second matters — *absence is not refusal*, because a caller cannot read an
explanation off a missing attribute.

Two negative tests prove the check is not vacuous. Subclass the model so `eventual_purpose()` returns
`"to become a great engineer"` → **XI fails**. Delete `maturity_level` entirely → **XI fails, and for
a different stated reason.**

---

## 4. Something the tests found that I had not designed

`test_repeated_administration_warns_against_reading_development_into_it` failed on first run. The
cause was not the assertion — it was that I had timestamped a session **before** the consent grant,
and `ConsentLedger.streams_granted_at` correctly answered that nothing was under grant at that
instant.

The system had already refused retroactive consent, and I had not written that rule.

It falls out of asking *what was granted at time T* rather than *is there a grant*, which is the GDPR
Art. 7(1) demonstrability query the ledger was built for. Backdating a session to before the person
agreed is precisely the move Art. 7(1) exists to prevent, and the hash chain makes it undoable rather
than merely discouraged.

I kept the finding as an explicit test — `test_consent_cannot_be_applied_retroactively` — with the
docstring recording that it was found by a failing test rather than by design. This is now the third
time in this programme that a property emerged from measurement rather than intent, and it is a better
argument for the architecture than anything written in prose.

---

## 5. Honest limitations

**Not one of these instruments has been validated in Egypt.** The Arabic evidence that exists is
Lebanese (MLQ, CPS), Omani, Saudi, Palestinian, Qatari and Jordanian (BPNSFS). The model records
`population_validated: False` for an Egyptian respondent and does not pretend otherwise. A registry
test asserts that no instrument claims Egypt among its validated populations, so this cannot be
quietly relaxed.

**The Arabic MLQ is not the MLQ.** Fekih-Romdhane et al. (2024) found the 10-item two-factor model fit
inadequately in Lebanon and dropped items 9 and 10 — which removes the only reverse-scored item and
changes the Presence range from 5–35 to 4–28. The caveat is attached to the spec and travels with
every score. It must be registered as a separate instrument before any Arabic administration.

**BPNSFS's need-frustration construct is under live challenge.** Murphy et al. (2023) argue the
satisfaction/frustration distinction is probably a method artifact of item keying direction. The
caveat travels with the profile, and a test asserts that it does.

**Self-report is self-report.** 3D-WS measures *self-perceived* wisdom, and a person low in reflective
capacity may be least able to report it. No instrument here publishes a reliable change index, so
`instrument_trajectory()` explicitly warns that change between administrations may be measurement
error, mood, or regression to the mean.

**The refusals are checkable; the phrasing is not.** Invariant XI verifies that the refusing methods
refuse. It cannot verify that `open_questions()` never drifts into prescription — that is guarded by a
keyword test, which is the same syntactic-proxy weakness already conceded for Invariant X.

---

## 6. Why this belongs in P2

P2 currently argues that refusal is a safety mechanism using a **simulated** threat confound. This
session supplies something better: a **real request, from a real person, refused for stated reasons,
with a decision procedure and negative tests proving the refusal is not decorative.**

The proposed §4.4, *"A request the architecture declines"*, would report: the request as made; the
four-way split; the finding that stage constructs cannot be de-ranked without misrepresentation; the
eleven refusal grounds; Invariant XI with its two negative tests; and the retroactive-consent property
that emerged from a failing test.

It also strengthens the §7.1 argument written earlier today. Psychometric responses are expressly named
in Egypt's PDPL Art. 1 as sensitive data, and the PDPL grants no research exemption — so the
psychometric stream is gated at the deployment context *and* the consent ledger, and refused outright
under `INSTITUTIONAL` and `UNDECLARED`. Reasoning about an employee's needs, values or self-reported
maturity on behalf of their employer is the exact case Art. 5(1)(f) addresses, and it is the case this
project has committed not to serve.

---

## 7. State

| | |
|---|---|
| Package | **v1.2.0** |
| Tests | **371 passed, 2 xfailed** (was 324; +47) |
| Invariants | **11**, all executable, 18 negative tests |
| Instruments registered | 10 — 2 administrable, 4 licence-blocked, 4 refused by construction |
| Refusal grounds | 12, each with a readable explanation |
| New defects | none |

**Still open, unchanged from Session 14:** your corresponding email; the Phase IV decision (A / B / C);
and the fact that nobody outside this project has run the code.

**New, and it is a real one:** if the formation model is ever used with a person, the instruments must
be obtained under written permission first. Four of the six useful ones have no published licence
statement. That is four emails, and they are not emails I can send.
