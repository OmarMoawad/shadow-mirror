# Shadow Mirror — Session 14B: Can Session 18 Run on Data That Already Exists?

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Question put to this session:** *"for 18's real participants, research the internet for data that is
ready and you can make use of."*

I searched. The answer has three parts, and the first one is a no.

---

## 1. The headline finding

**No public dataset can validate the threat-confound claim. Not one.**

The claim needs four things measured *on the same item, for the same person*:

1. a stated stance ("I do not want this"),
2. a behavioural choice that can contradict it (they approach anyway),
3. an arousal channel time-locked to that choice,
4. a coercion or threat manipulation, so that compliance and hidden preference are separable.

That intersection does not exist publicly. Roughly forty datasets were assessed across affective
computing, approach-avoidance paradigms, ecological momentary assessment, experimental economics, and
social conformity. The failure modes are clean and complementary:

- **Datasets with excellent physiology are passive-viewing paradigms.** DEAP, AMIGOS, ASCERTAIN,
  DREAMER, CASE, POPANE, Emognition — participants watch a clip and rate it. There is no action that
  can contradict the rating. A "liking" score is not a revealed choice.
- **Datasets with real behavioural choice lack autonomic recording, self-report, or both.** FOODEEG
  has an item-matched contradictable choice and no arousal channel. PsPM-PIT has threat, instrumental
  choice and superb psychophysiology, and zero self-report — there is no stated stance to contradict.
  SEMAINE has genuine withdrawal behaviour and neither self-report nor physiology.
- **The EMA and mobile-sensing corpora fail as a class.** StudentLife, GLOBEM, Tesserae, LifeSnaps,
  DAPPER, TILES, PMData, ExtraSensory: every "behavioural" stream is passive telemetry — GPS, steps,
  screen unlocks, app usage — and none of it is labelled with the topic the self-report was about. The
  pairing our model requires simply is not in the data.

The nearest miss is **Klaassen et al.'s passive-avoidance conflict task** — threat-of-shock, ~150
repeated approach-avoid choices, skin conductance *and* freezing. It is the only dataset found
combining an explicit threat manipulation, repeated approach-avoid choices, and autonomic arousal. It
fails on the stated stance (there is none) and on access (restricted).

**Two datasets deserve a note for how close the design gets and how far the deposit falls short.**
Sowden et al. (2018) ran precisely the paradigm we need — a private continuous rating and a public
spoken response on the same item, crossed with majority size — so that the private effect indexes
*acceptance* and public-minus-private indexes *compliance*, within subject. The data were never
deposited. Brouwer et al. (2021) paired a per-item "wanting" rating with a mobile approach-avoidance
task across four food categories, N=71 — our exact structure — with no data availability statement.
For both, emailing the authors is a better route than any download.

---

## 2. What *can* be done with existing data

This is not a dead end; it is a smaller, honest study. Three partial validations are available now,
and together they cover four of the paper's claims without a single new participant.

### Tier 1 — worth doing

**BIRAFFE2** — the best-provisioned public dataset in the review.
Open download, CC BY 4.0, **N = 102**, 117 within-subject stimuli, per-stimulus valence *and* arousal,
per-stimulus response latency, an explicit abstention marker in the logs, 1 kHz ECG + EDA, and three
real gamepad games producing instrumental behaviour. It supports partial validation of **calibration**,
**abstention** and **order-invariance**. It does *not* support the preference-contradiction core,
because the game behaviour is not item-matched to the stimulus ratings.

**FOODEEG** — CC0, **N = 117**. Session 1 collects per-food ratings; Session 2 has participants choose
between food pairs. Because the rating precedes the choice on the same items, a choice can genuinely
contradict a stated preference. It passes five of the six requirements and fails only on arousal. It
is the correct **paradigm skeleton** for a future primary study, and supports **calibration** and
**abstention** now.

**Urban Appraisal** — CC0, **N = 63**, 504 trials, per-item valence and arousal time-locked to EDA and
ECG. It is the mirror image of FOODEEG: correct physiology, no choice. Supports **calibration**.

### Tier 2 — one hand-check that could change the picture

**SWELL-KW.** The design is right: participants **choose which topic to present on**, which is an
item-matched, preference-contradicting choice, and the study includes a genuine time-pressure and
interruption manipulation. The open question is whether the topic-interest ratings and the chosen
topics are actually in the deposit — they are not listed in the documented variables. If they are
present, SWELL-KW meets R1–R6 minus threat at N = 25. If they are not, it collapses to another stress
corpus. **This is a single afternoon's work with a real chance of changing what Phase IV is**, and I
recommend it before anything else.

**Cascio, "Self-construal and Conformity"** (openICPSR, DOI 10.3886/E184271V1) is the only
downloadable resource pairing a *private* rating with a *public* action on the same item, repeated
60–80 times, under experimentally manipulated peer pressure. Three cautions, all real: the N is not
stated anywhere I could verify, the licence is unspecified, and the 6.5 KB behavioural file is small
enough that it is plausibly participant-level summary rather than trial-level — which would eliminate
the per-item pairing entirely. **Verify the file contents before building anything on it.**

### What this does not buy

It does not buy the safety result. The 0-of-800 misread figure, the ablation, and the separation sweep
are all claims about how the system behaves when a threat process is present in the data-generating
process. No public corpus contains that process alongside a stated stance. **Reporting a secondary
analysis as though it validated the threat-confound claim would be exactly the fabrication ground rule
1 forbids**, and I will not do it.

---

## 3. Governance, if a primary study is ever run

Answered while researching your affiliation. Every claim below has a source; the full source list is
in the session log.

### AUC's IRB

- Body: **Institutional Review Board for the Protection of Human Subjects (IRB)**, members appointed
  by the Provost, seven members including one external community member.
- **All research collecting data from human participants requires approval before it begins**,
  including research conducted outside Egypt. Course assignments with no intent to publish are exempt.
- **CITI/NIH human-subjects training is mandatory** and has been since 1 January 2013. For this work
  the correct course is *Social and Behavioral Research, Stage 1, Basic*.
- Three review tracks exist. Our study would most likely be **expedited** — the category explicitly
  covers "behaviour/cognition studies without subject manipulation or stress" — but a threat or
  social-pressure manipulation may well push it to **full board**, and I would submit expecting that.
- Reviews sit on Thursdays; allow one month.
- **Graduate students may be PI but must name a supervisor. Undergraduates may not be PI.**
- ⚠️ The IRB policy PDF and the live web page **name different chairs**, and the PDF's described
  paper-submission process has been superseded by an online portal. Confirm current contacts by
  emailing `irb@aucegypt.edu` before preparing anything.

### The gate that is easy to miss

AUC's own IRB page warns that IRB approval **does not** imply approval by **CAPMAS**, the Egyptian
agency that authorises survey and interview work conducted inside Egypt, and states that the IRB "is
not equipped to handle matters related to CAPMAS". This is a separate national permit with its own
timeline, and it should be started early rather than discovered late.

### The legal position, which is the interesting part

**Law 214/2020 (Clinical Medical Research) does not reach us.** Its Article 1 subject matter is
therapeutic, pharmaceutical, surgical, nutritional, preventive or diagnostic interventions; Article 24
confines lawful research to entities registered with the Ministry of Health. A computing lab is not
such an entity. There is **no binding Egyptian national law governing non-medical human-subjects
research ethics** — a gap noted in the peer-reviewed research-ethics literature. The Supreme Council
of Universities issued a national research-ethics guide in January 2026 whose third book addresses
behavioural and social research committees, but it carries no decree number and no binding-force
clause, and its applicability to private universities is unspecified. Treat it as guidance and ask the
IRB about it.

**PDPL 151/2020 does reach us, and is stricter than the GDPR in three respects.** Its personal-data
definition expressly covers data determining "psychological identity". Its sensitive category covers
"psychological, mental, or physical health, or genetic, biometric or financial data", and Article 12
requires a **licence from the Personal Data Protection Centre** on top of written explicit consent,
with imprisonment and fines to EGP 5,000,000 for breach. And it contains **no scientific-research
exemption of any kind** — the words for "research", "studies" and "university" appear nowhere in the
law or its executive regulations. Article 5(6) relaxes purpose limitation for not-for-profit
statistical or educational processing but does not disapply consent or the Article 12 licence.

**The executive regulations landed on 2 November 2025 with a compliance deadline of 31 October 2026.**
That is roughly three months away. If a study touching physiological, biometric or psychological data
is contemplated, the DPO (`DPO@aucegypt.edu`) is the right first contact, not the IRB.

**Design consequence.** Our existing refusal of the biometric stream is not merely prudent under this
regime; it is the difference between needing a state licence and not. And anonymisation, not
pseudonymisation, is the only route out of scope — a linkable participant identifier keeps the data
personal.

**This is a reading of statutory text by a non-lawyer and has not been reviewed by counsel.** It is
now stated as such in P2 §7.1 and in the §9 limitations.

---

## 4. What I recommend, and what I need from you

**Phase IV as originally scoped — a primary study producing the data for P3 — remains impossible
without collecting it.** No amount of searching changes that, and I would rather say so than dress a
secondary analysis in its clothes.

But the choice is no longer binary. Three options, in the order I would rank them:

**A. Secondary-analysis paper (no participants, ~2 sessions).** Run the architecture against BIRAFFE2,
FOODEEG and Urban Appraisal. Validate calibration, abstention and order-invariance on real human data
for the first time. Report plainly that the threat-confound claim is untouched. This is a real
contribution — it converts "we have never run this on a human" into "we have run this on 282 people
across three corpora" — and it is honest about what it does not show.

**B. Hand-check SWELL-KW first (~1 session), then decide.** If the topic-interest ratings are in the
deposit, option A gains a genuine preference-contradiction result at N = 25 and gets substantially
stronger. Low cost, real upside.

**C. Primary study.** Protocol, AUC IRB, CITI certification, CAPMAS permit, PDPL analysis, and — on
the evidence above — the FOODEEG rating-then-choice structure crossed with a social-pressure
manipulation in the Sowden et al. mould. This is the only route to the threat-confound claim. It is
months of calendar time before a single participant is recruited, most of it waiting on approvals.

**My recommendation is B then A**, with C prepared in parallel as a protocol rather than executed —
because a written, IRB-ready protocol is itself a publishable artefact and it is the thing P2's
reviewers will ask whether you have.

**What I need from you:** which of A, B or C, and whether you want me to draft the IRB packet in the
meantime. I can do everything in A and B without you. C needs your CITI certification and a supervisor
or department name, neither of which I can supply.
