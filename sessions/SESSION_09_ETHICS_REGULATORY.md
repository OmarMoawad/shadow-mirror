# Shadow Mirror — Session 09: Ethics, Governance and Regulatory Audit

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverables:** this report, including a rewritten enforceable Prohibited-Use Checklist.
All regulatory provisions were checked against live sources, not recalled.

---

## 0. Summary — and a correction to my own Session 6 recommendation

**In Session 6 I recommended piloting in education because it is low-stakes. Under EU law it is
not.** That recommendation was wrong and I am withdrawing it.

Three findings, in order of consequence:

| # | Finding | Status |
|---|---|---|
| **R-1** | With the physiological stream enabled, Shadow Mirror is plausibly an **emotion recognition system** under AI Act Art. 3(39) — and Art. 5(1)(f) **prohibits** its use in workplaces and education institutions. **In force since 2 February 2025.** | **Critical** |
| **R-2** | An educational deployment that evaluates learning outcomes falls under **Annex III(3)(b) — high-risk**. Those obligations apply from **2 August 2026: eight days from today.** | **Critical** |
| **R-3** | The consent gate as coded meets the dynamic-consent standard it cites on five of seven criteria. Two gaps: no demonstrable consent record at the store layer, and withdrawal is not as easy as granting in the CLI. | High |

The self-mirror mode — a person, on themselves, outside an institution — is unaffected by R-1 and
R-2. That is worth stating early, because it is the mode the architecture was designed for, and the
regulatory exposure comes entirely from the deployment contexts that were proposed *around* it.

---

## 1. R-1 — the emotion-recognition prohibition

### The chain

**AI Act Art. 3(34):** *"'biometric data' means personal data resulting from specific technical
processing relating to the physical, physiological or behavioural characteristics of a natural
person, such as facial images or dactyloscopic data."*

The critical point, and the one most people get wrong: **this definition does not require unique
identification.** GDPR Art. 4(14) does ("which allow or confirm the unique identification"); the AI
Act's does not. So an arousal proxy — a heart-rate-like signal — is personal data from technical
processing of a physiological characteristic, and is therefore **biometric data under the AI Act**
even though it identifies nobody.

**Art. 3(39):** *"'emotion recognition system' means an AI system for the purpose of identifying or
inferring emotions or intentions of natural persons on the basis of their biometric data."*

Shadow Mirror's guard infers `threat_response` — an affective and intentional state — partly on the
basis of the `physiological` stream. When that stream is enabled, the system meets this definition.

**Art. 5(1)(f):** *"the use of AI systems to infer emotions of a natural person in the areas of
workplace and education institutions, except where the use of the AI system is intended to be put in
place or into the market for medical or safety reasons."*

**Applicable since 2 February 2025.**

### What this means concretely

| Deployment | Exposure |
|---|---|
| Self-mirror, private individual, outside an institution | **Out of scope.** Art. 5(1)(f) is scoped to "the areas of workplace and education institutions". |
| Consented-study mode between two private individuals | Out of scope of Art. 5(1)(f); GDPR still applies. |
| A university or school deploying it for students, physiological stream on | **Prohibited**, unless the safety exception holds. |
| An employer deploying it, physiological stream on | **Prohibited**, same caveat. |
| Any institutional deployment with the physiological stream **off** | Outside Art. 3(39) — no biometric basis, so no emotion recognition system. Still possibly high-risk under R-2. |

### The safety exception, and why it must not be assumed

The exception covers systems "intended to be put in place... for medical or safety reasons." Shadow
Mirror's physiological stream exists **only** as a threat confound. Session 2 measured what happens
without it: the misreading rate rises to 31.2%, and 62.5% on compliance-type responses. Session 3
made the guard refuse rather than degrade. The stream's sole documented purpose, in code and in
tests, is to prevent a specific foreseeable harm.

That is as clean a safety-purpose argument as this exception is likely to see. **It is still an
argument, not a conclusion.** It has, to my knowledge, no case law behind it, and the Commission's
guidelines on prohibited practices should be read before anyone relies on it. The honest position
for a paper is to *state* the argument and note that it is untested — which is itself an
interesting contribution, because "a safety guard that is itself an emotion-inference system" is a
real and unresolved tension in the Act.

Recital 18's exclusions do **not** rescue this. They exclude physical states such as pain and
fatigue, and the mere detection of expressions "unless they are used for identifying or inferring
emotions". Shadow Mirror uses arousal precisely to infer whether a response is a threat response.
That is the inferring case, not the detection case.

---

## 2. R-2 — high-risk classification, and the date

**Annex III(3)(b):** *"AI systems intended to be used to evaluate learning outcomes, including when
those outcomes are used to steer the learning process of natural persons in educational and
vocational training institutions at all levels."*

Shadow Mirror ingests `task_performance`, forms hypotheses about a learner's knowledge state
(`blind_spot`, `latent_knowledge`), and emits inquiries that direct what the learner does next. In an
educational institution, that is evaluating learning outcomes and steering the learning process.

**Annex III(4)(b)** catches the workplace equivalent: systems used "to monitor and evaluate the
performance and behaviour of persons" in work relationships.

**Application date: 2 August 2026** — eight days after this session. Systems placed on the market
before that date get a transition, but only until they undergo significant design changes.

High-risk classification is not a prohibition. It is a compliance regime: risk management system,
data governance, technical documentation, logging, transparency to deployers, human oversight,
accuracy/robustness/cybersecurity, quality management, conformity assessment, CE marking,
registration. For a solo researcher that is a serious undertaking, and it is the reason the
recommendation below changes.

### Revised pilot recommendation

**Session 6 said: pilot in education, it is low-stakes. Withdraw that.** In the EU, education is a
named high-risk domain and, with the physiological stream, a prohibited one.

The literature-synthesis pilot proposed alongside it is clean: no personal data, no emotion
inference, no institutional evaluation of a person. **That should be the Phase 3 pilot.** For the
human-subjects study in Session 15, the defensible framing is *individual adults using the
self-mirror on themselves, recruited outside any institutional relationship, not for the purpose of
evaluating their learning* — which keeps it out of Annex III(3) entirely.

---

## 3. R-3 — does the consent gate meet the standard it cites?

`consent.py` cites dynamic consent (Budin-Ljøsne et al., 2017 — verified in Session 6 at
`10.1186/s12910-016-0162-9`). Assessed against GDPR Art. 4(11) and Art. 7:

| Requirement | Provision | As coded | Verdict |
|---|---|---|---|
| **Freely given, not bundled** | Art. 7(4) | `add_stream()` raises `ConsentError` unless each non-obvious stream is acknowledged individually; blanket grant is impossible for `implicit_task`, `physiological`, `avoidance` | ✅ **Meets, and exceeds.** Refusing to let a category be bundled at all is stronger than the Article requires |
| **Specific** | Art. 4(11) | Grants are per-stream and purpose-locked | ✅ Meets |
| **Informed** | Art. 4(11) | Every `Stream` carries `captures` and `may_reveal` in plain language; `disclosure_text()` renders it | ✅ **Meets, and exceeds.** Stating what a stream *may reveal*, not only what it records, is the part most implementations omit |
| **Unambiguous, affirmative** | Art. 4(11) | Explicit call per stream; no defaults, no pre-ticked state | ✅ Meets |
| **Withdrawable at any time** | Art. 7(3) | `revoke()` sets `revoked_at`; `Study.revoke(wipe=True)` erases | ✅ Meets |
| **As easy to withdraw as to give** | Art. 7(3) | Granting is a guided CLI flow (`shadow subject consent alex`); withdrawal is a single command with no equivalent confirmation or receipt | ⚠️ **Gap.** Not a violation on its face — one command is easy — but there is no confirmation to the subject that withdrawal took effect, and no receipt |
| **Demonstrable** | Art. 7(1) | `granted_at`, `revoked_at`, `purpose`, `streams` are on the grant; **there is no append-only consent log** at the store layer, so a revoked-then-regranted history is not reconstructible | ❌ **Gap.** Art. 7(1) requires the controller to *demonstrate* consent was given. A mutable grant object cannot demonstrate what was true last March |

Two further observations:

- **The 90-day review horizon (`DEFAULT_REVIEW_DAYS`) is a genuine strength** and goes beyond what
  GDPR requires. Consent that lapses unless re-affirmed is the operational meaning of "dynamic".
- **`reaffirm()` refuses to resurrect a revoked grant** — it raises and demands a new one. That is
  the correct semantics and it is rarely implemented.

### Two fixes, both small

1. **Append-only consent ledger.** Every grant, stream addition, re-affirmation and revocation
   written as an immutable event with a timestamp. Satisfies Art. 7(1), and it is the same
   append-only pattern the belief ledger already uses.
2. **Withdrawal receipt.** On revocation, emit a record the subject can keep: what was held, what was
   erased, when. Closes the Art. 7(3) parity gap and costs nothing.

Neither is implemented this session; both are specified for Session 12 rather than rushed in
alongside a regulatory analysis.

### GDPR Article 9

Self-reported emotion and physiological arousal can both constitute **data concerning health** under
Art. 9(1) — mental state and cardiac signals respectively. The lawful basis available is explicit
consent, Art. 9(2)(a), which the per-stream gate provides. **The monograph does not currently name
Art. 9.** It should, because "special category data, processed on explicit consent, per stream,
revocable" is a much stronger sentence than "we take consent seriously".

---

## 4. The Prohibited-Use Checklist, rewritten to be enforceable

Your original checklist (p. 294) is a good list of the right prohibitions. Its weakness is that
every line is an instruction to a reader — *"answer no to every prohibited purpose"* — and nothing
in the system can tell whether the reader did.

Below, each prohibition is tagged with **how it is enforced**: `[CODE]` a mechanism refuses,
`[TEST]` a test asserts the refusal, `[LICENCE]` a licence term binds, `[POLICY]` honour-system only
and labelled as such. Anything left at `[POLICY]` is not a safeguard; it is a wish, and marking it
honestly is the point.

### 4.1 Prohibited outright

| # | Prohibition | Enforcement | Basis |
|---|---|---|---|
| P-1 | Evaluation of a non-consenting third party | **[CODE]** `Study.observe()` raises `ConsentError` when no active grant covers the stream · **[TEST]** `test_consent_and_patterns.py` | GDPR Art. 6 |
| P-2 | Bundling non-obvious streams under a blanket yes | **[CODE]** `add_stream()` raises unless `acknowledged_non_obvious=True` per stream · **[TEST]** | GDPR Art. 7(4) |
| P-3 | Inferring a hidden preference without the evidence to exclude a threat response | **[CODE]** guard coverage gate; `latent_approach` unreachable without both channels · **[TEST]** `test_d19_*` (5 tests) | Project ethics; measured harm |
| P-4 | Emotion inference in a workplace or education institution | **[POLICY]** + **[LICENCE]** — *no code mechanism exists* | **AI Act Art. 5(1)(f)** |
| P-5 | Clinical diagnosis, treatment selection, crisis assessment | **[POLICY]** + **[LICENCE]** | MDR; project ethics |
| P-6 | Hiring, firing, promotion, compensation, worker surveillance | **[POLICY]** + **[LICENCE]** | AI Act Annex III(4) |
| P-7 | Policing, criminal-risk, deception, dangerousness or morality assessment | **[POLICY]** + **[LICENCE]** | AI Act Art. 5(1)(d) |
| P-8 | Credit, insurance, housing, benefits, eligibility | **[POLICY]** + **[LICENCE]** | AI Act Annex III(5) |
| P-9 | Political persuasion or exploitation of vulnerability | **[POLICY]** + **[LICENCE]** | **AI Act Art. 5(1)(b)** |
| P-10 | Inference of origin, upbringing, or protected traits | **[POLICY]** — the model has no such hypothesis, but nothing *prevents* one being added | AI Act Art. 5(1)(g); GDPR Art. 9 |
| P-11 | A global maturity score or opaque peer ranking | **[CODE]** the output is a distribution and a credible set; no scalar score exists anywhere in the API · **[TEST]** `test_operator_G_multiple_hypotheses_coexist` | Project ethics |
| P-12 | Covert operation | **[CODE]** no grant, no ingestion — refusal is the default path · **[TEST]** | GDPR Art. 5(1)(a) |

**Five of twelve are enforced in code and tested. Seven are policy only.** That ratio is the
honest headline, and it is a considerably better one than most systems could produce — but a paper
should print the ratio, not the list.

### 4.2 The two enforcement gaps worth closing

- **P-4** is the only prohibition that is currently *illegal to breach in the EU* and has **no code
  mechanism**. A minimal enforcement point exists: require a deployment context declaration at
  session start (`self` / `consented_individual` / `institutional`), and have the engine refuse to
  enable the `physiological` stream when the context is `institutional`. That is roughly fifteen
  lines and converts P-4 from `[POLICY]` to `[CODE]`. **Specified for Session 12.**
- **P-10** could be enforced by an allow-list of hypothesis kinds, refusing any hypothesis whose
  declared kind is not in the permitted set. Also Session 12.

### 4.3 Required documentation, unchanged

Your original closing paragraph — document the self-directed purpose, lower-burden alternatives,
consent path, withdrawal semantics, data map, construct argument, validation evidence, incident
process, and sunset condition — is retained verbatim. It maps almost one-to-one onto the AI Act's
Art. 11 technical documentation requirements, which is a better position than the monograph
currently claims for itself.

---

## 5. What this changes in the programme

| Change | Effect |
|---|---|
| Education pilot **withdrawn** | Session 15 reframes to individual adults, self-mirror, recruited outside institutions |
| Literature-synthesis pilot **promoted** | Becomes the Phase 3 deployment pilot |
| P2 paper gains a section | "Regulatory position" — Art. 3(34)/(39), Art. 5(1)(f), the safety-exception argument, and the honest note that it is untested. This is a *strength* at AIES/FAccT, not a liability |
| Two new defects | **D-31** no append-only consent ledger (Art. 7(1)); **D-32** no deployment-context gate for P-4 |
| Monograph correction | Part 6 should cite AI Act Art. 3(34), 3(39), 5(1)(f), Annex III(3)–(4) and GDPR Art. 9 by number. It currently cites the instruments but not the provisions |

---

## 6. One thing worth saying plainly

The awkward finding of this session is that **the physiological stream — which exists only to
protect people, and which Session 2 proved does protect them — is the thing that pulls the system
into the AI Act's emotion-recognition prohibition.** Remove it and the legal exposure largely goes
away; remove it and the misreading rate goes from 0.0% to 31.2%.

That is a real tension between a safety mechanism and a rule written to prevent a different harm,
and it is exactly the sort of finding an AIES or FAccT audience exists to discuss. It should be a
section of the paper, not a footnote.

---

*Session 10 — drafting P2, the ethics-of-design paper, for AIES/FAccT — continues automatically.*

**Sources:** [AI Act Art. 5](https://artificialintelligenceact.eu/article/5/) ·
[Art. 3](https://artificialintelligenceact.eu/article/3/) ·
[Annex III](https://artificialintelligenceact.eu/annex/3/) ·
[Recital 18](https://artificialintelligenceact.eu/recital/18/) ·
[Implementation timeline](https://artificialintelligenceact.eu/implementation-timeline/)
