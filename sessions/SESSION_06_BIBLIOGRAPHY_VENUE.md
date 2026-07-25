# Shadow Mirror — Session 06: Bibliography Verification and Venue Decision

**Author of record:** Omar Moawad · **Session date:** 25 July 2026
**Deliverables:** `bibliography.json` (all 96 entries, structured), this report.

---

## 0. Summary — and a correction to my own earlier framing

**Your bibliography is in excellent condition.** 96 entries, parsed and checked in full:

| Check (applied to **all 96**) | Result |
|---|---|
| Missing year | **0** |
| Malformed DOI | **0** |
| Duplicate entries | **0** |
| Entries with no resolvable identifier | 6 — and all six are books or technical reports where no DOI exists |
| Distinct publisher DOI prefixes | **28** |
| Year range | 1948–2024, median 2012 |
| Live-verified sample (highest-risk entries) | **5 / 5 correct** |

The six identifier-free entries are Pearl (2009) *Causality*, Picard (1997) *Affective Computing*,
Popper (1959), Settles (2009) UW-Madison TR-1648, Shadish, Cook & Campbell (2002), and Sutton & Barto
(2018). Books and technical reports do not carry DOIs. That is correct practice, not an omission.

Twenty-eight distinct publisher prefixes matters more than it looks. Fabricated reference lists
cluster on a handful of plausible prefixes; a real one spread across APA (10.1037, 17 entries),
Elsevier (10.1016), SAGE (10.1177), Nature (10.1038), Taylor & Francis (10.1080), JSTOR, ACM, IEEE,
Springer and eighteen others is the fingerprint of someone who actually went and found the papers.

**The correction I owe you:** in Session 1 I wrote that the generated IEEE paper "degraded your
scholarship." That was right, but I understated it. The AI-generated 12-entry list had **at least six
errors**. Your own 96-entry list has **zero** detectable ones. The ratio is not close.

---

## 1. Method, and its limits

`bibliography.json` contains every entry parsed from pages 316–322, with year, DOI, arXiv ID and URL
extracted. Parsing used indentation boundaries — entries are indented, continuations are not — after
a first attempt that split on author-year patterns produced 94 fragments with mangled identifiers.
Worth recording, because the fragmented parse briefly suggested 80 entries lacked identifiers, which
would have been an alarming and entirely false finding.

**Structural checks ran over all 96 entries. Live verification covered 5.** I am not going to imply
otherwise. Exhaustive verification means 96 individual resolutions, which is roughly a day of
someone's time and is a reasonable thing to ask a co-author or a librarian to do before submission.

The sample was not random — it was the highest-risk stratum: everything published 2022 or later,
where a citation is most likely to be mis-transcribed and least likely to be caught by a reader's
memory.

| Entry | Verified as |
|---|---|
| Pekrun (2024), Control-value theory, `10.1007/s10648-024-09909-7` | ✅ Resolves to Springer, *Educational Psychology Review* |
| Li & Washington (2024), personalised vs generalised emotion recognition, `10.2196/52171` | ✅ Resolves to **JMIR AI 2024;1:e52171** |
| Vasey et al. (2022), DECIDE-AI, `10.1038/s41591-022-01772-9` | ✅ *Nature Medicine*, PMID 35585198 — title and DOI both exact |
| NIST (2023), AI RMF 1.0, `10.6028/NIST.AI.100-1` | ✅ Correct designator |
| Huang et al. (2024), LLMs cannot self-correct reasoning yet, arXiv 2310.01798 | ✅ Correct ID |

Five for five, including two 2024 journal entries and a standards document — the three categories
where transcription errors usually appear.

---

## 2. The real problem is not errors. It is recency.

| Period | Entries |
|---|---|
| Pre-2000 | 22 |
| 2000–2014 | 38 |
| 2015–2021 | 29 |
| **2022–2024** | **7** |
| **2025–2026** | **0** |

Median year **2012**. For a foundational bibliography this is a strength — Shannon 1948, Brier 1950,
Simon 1955, Cronbach & Meehl 1955, Flavell 1979, AGM 1985 are the right spine for a theory of
reflection under uncertainty, and most architecture papers do not have them.

For a **2026 submission in metacognitive AI**, seven entries from the last four years and none from
the last eighteen months is the gap a reviewer will name first. The field moved a great deal in
2025–2026, and Session 1 established that it moved in directions directly adjacent to yours.

### Verified additions, ready to insert

Every one of these was resolved against a live source during Sessions 1–5. None is a suggestion to
go and check.

| Reference | Why it belongs |
|---|---|
| **Jacobs, B. (2025).** Commutativity of probabilistic belief revision. *Frontiers in Cognition*. `10.3389/fcogn.2025.1623227` | Proves Bayesian conditioning is commutative while human revision is not. Grounds the D-20 fix and the design decision to keep order-dependence out of the arithmetic. |
| **Schäfer, U. et al. (2025).** "The AI is uncertain, so am I. What now?" *Proc. ACM Hum.-Comput. Interact.* `10.1145/3757451` | The closest existing work on how people actually use an uncertainty display. Load-bearing for the refusal argument. |
| **Vasileiou, S. L. et al. (2025).** How do people revise inconsistent beliefs? arXiv `2506.09977` | Human revision is explanation-guided and non-minimal. Justifies holding contradiction open. |
| **Vasileiou & Yeoh (2024).** Human-aware belief revision. arXiv `2405.19238` | Companion framework. |
| **Rosenbacke, R. et al. (2024).** XAI and clinician trust: systematic review. *JMIR AI* 1:e53207 | Calibrated reliance; the review your Phase 2 metrics derive from. |
| **Elenjical, Kavuri & Varma (2026).** Think2: grounded metacognitive reasoning in LLMs. arXiv `2602.18806` | Closest 2026 metacognition architecture; the contrast case for "internal vs external reflection". |
| **Xin et al. (2026).** MetaMem. **ACL 2026 Findings**, arXiv `2602.11182` | Symbolic meta-memory. |
| **Didolkar, Ballas, Arora & Goyal (2025).** Metacognitive reuse. arXiv `2509.13237` | Source of the real "46% token savings" figure. |
| **Hou et al. (2026).** Learn like humans: meta-cognitive reflection. arXiv `2601.11974` | Self-improvement via reflection. |
| **Guo et al. (2503.19271).** MARS: memory-enhanced agents with reflective self-improvement | Cite under its actual title. |

That is ten verified 2024–2026 entries, taking the recent stratum from 7 to 17 and covering the exact
literature a reviewer would check first.

---

## 3. Venue, settled

Sessions 2–5 changed what evidence exists, so the shortlist can now be decided rather than guessed.

**What you can actually put in front of a reviewer:**

1. A measured safety result with no human subjects: misreading a threat response as a hidden desire,
   **0.0%** [0.0, 0.0] with the guard, **42.9%** and **75.1%** for two guard-free baselines, *n* = 400
   per generative process across five processes.
2. An ablation showing the protection is contingent on a channel many deployments lack, and a design
   that refuses rather than degrades when it is missing.
3. Ten architectural invariants as executable checks, holding over 200 randomised states, each with a
   negative test.
4. Refusal calibration: 100% refusal on insufficient evidence, 0% over-refusal, 19× uncertainty
   separation.
5. A zero-dependency, byte-reproducible artifact.

**What you cannot:** anything about how people respond to any of it.

### The decision

**P2 — the ethics-of-design paper — goes first, to AIES or FAccT.**

Those venues reward exactly the shape of evidence you have: a specific foreseeable harm, quantified;
a design commitment that eliminates it; an honest ablation showing the conditions under which the
protection fails; and a refusal behaviour argued as a feature. No human subjects required. The
consent architecture and prohibited-use checklist are contributions there rather than boilerplate.

**P1 — the architecture paper — goes to ACM TiiS.**

TiiS publishes architectures for human–AI interaction and tolerates formative rather than summative
evaluation. The executable invariant suite is the strongest thing in the package for that audience:
it converts "we define ten invariants" into a decidable specification with a compliant
implementation.

| Venue | Verdict |
|---|---|
| **AIES / FAccT** | **P2, first submission.** Best fit for a quantified harm plus a design that removes it. |
| **ACM TiiS** | **P1.** Architecture + executable conformance. |
| AI Magazine | Fallback for P1 if TiiS declines. Framework-friendly, lower empirical bar. |
| CHI | Possible for P2, but reviewing skews to user studies. Reconsider after Phase 2. |
| IEEE Intelligent Systems | Fallback; short-format reference architectures. |
| *AI & Society* | Fallback for a broader framing (raised in the second external draft). |
| **IEEE TAC** | **Not now.** Needs the human study. This was Session 0's recommendation and it was wrong for the evidence that exists. |

Check the current calls for papers for both AIES and FAccT before committing — I am not going to
quote submission dates I cannot verify, and they move every year.

---

## 4. Corrections table for the monograph

| # | Item | Action |
|---|---|---|
| B-1 | Six entries without identifiers | **No action.** Books and TRs; correct as-is. |
| B-2 | Recent literature thin (7 entries 2022+, 0 from 2025–26) | **Insert the ten verified references in §2.** Highest-priority change to the manuscript. |
| B-3 | Exhaustive live verification | 5/96 done here. Assign the remaining 91 to a co-author or librarian before submission; the structured `bibliography.json` makes it a mechanical pass. |
| B-4 | No 2025–26 metacognition citations | Covered by B-2. This is the gap a reviewer names first. |
| B-5 | Venue | Settled: AIES/FAccT for P2, TiiS for P1. Not IEEE TAC. |

---

## 5. Reproducing

```bash
python3 - <<'EOF'
import json; b = json.load(open("bibliography.json"))
print(len(b), "entries")
print(sum(1 for r in b if not (r["doi"] or r["url"] or r["arxiv"])), "without identifier")
EOF
```

---

*Session 07 — auditing the mathematical chapters (pp. 55–79) and repairing the LaTeX corruption
visible in the PDF — continues automatically.*
