# Shadow Mirror — Session 14: Related Work, Affiliation, and a Term We Should Not Have Used

**Author of record:** Omar Moawad · **Affiliation:** The American University in Cairo · **Session date:** 25 July 2026
**Deliverables:** expanded P1 and P2, this report, `SESSION_14B_DATA_FEASIBILITY.md`, updated `bibliography.json`.

Session 13 named the thin reference list as the largest remaining risk to either paper, ahead of any
open defect. This session closes it. It also found one substantive error in P2's claim structure and
one ground-rule violation in both papers, neither of which I was looking for.

---

## 1. What was verified

**76 candidate references were checked against live sources. 76 confirmed, 0 rejected, 0 fabricated.**

Verification ran through five independent passes, each required to return a resolvable identifier and
the URL it was confirmed from. The instruction to each pass was that a fabricated citation is worse
than a missing one and that failure to confirm must be reported as failure, not filled in. Nothing
came back unconfirmable, which is itself a mild surprise and suggests the candidate list was
conservative.

**Corrections caught during verification** — every one of these would have been a visible error in a
submitted manuscript:

| Proposed | Actual |
|---|---|
| Roemmich et al., "Values in Emotion AI Hiring **Technologies**: Technosolutionism, Self-Improvement, and Secret Knowledge" | "…Hiring **Services**: **Technosolutions to Organizational Problems**", and a fourth author (S. Fan) was missing |
| Passos et al., IEEE Software 2010, DOI `MS.2010.x` | DOI is `10.1109/MS.2009.117`; "et al." expands to five named authors |
| Terra & Valente, "…object-oriented software **architecture**" | published title is plural, "**architectures**" |
| Oaksford & Chater, "selection task**:** Optimal data selection" | published title is "selection task **as** optimal data selection" |
| Solove, "Privacy Self-Management and the Consent Dilemma" | published title carries the prefix "**Introduction:**" |
| Naeini — first author surname "Naeini" | surname is "**Pakdaman Naeini**" |

Two entries carry deliberate flags rather than corrections. Wachter, Mittelstadt & Russell (2018) has
**no publisher DOI** — the Oxford ORA record is the stable identifier, and anyone reformatting the
bibliography should not invent one. Three of the legal-scholarship entries (Nissenbaum, Solove,
Wachter & Mittelstadt) are **student-edited law reviews, not externally peer reviewed**; that is
normal for the genre and worth knowing when weighing them against the empirical citations.

---

## 2. The reference expansion

| | Before | After | Venue norm |
|---|---|---|---|
| **P1** (TiiS) | 12 | **55** | 30–45 |
| **P2** (AIES/FAccT) | 14 | **50** | 25–40 |

Both are now above the norm rather than below it, which is the right side to err on for a journal
submission and harmless for a conference one.

The expansion is not a reference dump. §2 of each paper was rewritten into subsections that each
position the contribution against a named line of work, and in three places the new literature
*constrains* a claim rather than supporting it:

**P1 §2.2** now concedes explicitly that the invariants "borrow the form of each of these and match
none exactly" — not contracts, not model checking, closest to property-based testing in the QuickCheck
tradition. The claim is narrowed to a difference of *subject matter* rather than technique.

**P1 §2.3** admits that the provenance literature "had the right answer three decades before we made
the mistake". The W3C PROV model and Buneman's why/where distinction both treat derivation as
multi-parent; our D-14 defect was writing it as a scalar. That is now presented as the argument for
mechanical checking rather than as a discovery.

**P1 §2.5** adds Nelson's finding that no single measure of question-usefulness dominates, and states
that we report normalised regret against an oracle precisely so a reader preferring a different
measure can separate the measure from the planning.

**P2 §2.1** is where the new literature does the most work. Fifteen references on selective
prediction, deferral, calibration and conformal prediction now stand behind a sharpened distinction:
every one of those mechanisms abstains because a *confidence* is low and is tunable by a threshold;
our guard abstains because *a specific alternative explanation cannot be ruled out with the evidence
collected*, is not tunable, and fires just as readily on a high-confidence reading. "A selective
classifier asks *how sure am I?*; the guard asks *which question was never asked?*" That sentence is
the paper's design claim, and it could not have been written without knowing what the abstention
literature actually does.

---

## 3. The term we should not have used

Session 13 flagged that P2 borrows clinical authority and left a `[CITATION NEEDED —
trauma-response typology]` marker with the instruction not to remove it without a real citation. I
went looking for that citation. **It does not exist.**

The word **"fawn"** — which P2 used in its introduction, in the §3 mechanism table, and in a
limitation — traces to Pete Walker's *Complex PTSD: From Surviving to Thriving* (2013). That book is
real, and it is the popular origin of the term. It is also **self-published**: Azure Coyote Publishing
is the author's own imprint, issued through Amazon's CreateSpace platform, with no editorial peer
review. No refereed source establishes "fawn" as a validated clinical construct.

There *is* a genuine peer-reviewed literature in the same region, and it is good:

- **Cantor & Price (2007)**, ANZJP — appeasement under traumatic entrapment, spanning hostage
  reactions and domestic abuse. This is the closest real antecedent to what we mean.
- **Marx et al. (2008)**, *Clinical Psychology: Science and Practice* — tonic immobility as an evolved
  predator defence, and how survivors' non-resistance is misread.
- **Bracha (2004)**, *CNS Spectrums* — the acute stress response as a spectrum rather than the
  textbook dichotomy.
- **Gilbert (2001)** — submissive behaviour within social competition and hierarchy.

**What changed in the paper.** "Fawn" has been removed from every load-bearing claim. The introduction
now says the failure mode "has an established literature in clinical and evolutionary psychology
[34–37] and no name at all in machine learning" — which is true, where the previous sentence was not
quite. The §3 mechanism table row reads "complies under threat". The limitation was rewritten from a
hedge into a concession that names the provenance problem directly and ends: *"A reader who suspects
we have borrowed more authority than we have earned is raising the right objection; this paragraph is
our answer, and it concedes most of it."* Walker remains in the bibliography as [38], with a bolded
note in the entry itself stating that it is a self-published trade book and not peer-reviewed
literature, cited only as the term's origin.

This is the second time in this programme that going to look for a supporting citation has weakened a
claim rather than strengthened it. That is the process working.

---

## 4. A ground-rule violation, found by re-running the suite

Ground rule 7: *no number enters a manuscript unless a file in the repository produces it AND the
person writing the sentence has run that file.*

Both drafts stated `312 passed, 2 xfailed`, and P1's abstract and Appendix B stated a suite of **314
tests**. Running `pytest -q` against the shipped v1.1.0 package returns:

```
324 passed, 2 xfailed in 1.22s
```

The figures were correct when written and went stale when Session 12 added the governance tests. No
reviewer would have caught it, and it would have been a discrepancy between a paper and its own
artefact. Corrected in the abstract, §3.6 and Appendix B of P1 and in Appendix A of P2.

**Logged as D-33 — stale derived figures in manuscripts.** The register entry records the general
lesson rather than the specific number: any figure computed from the repository must be regenerated,
not carried forward, whenever the repository changes. A regeneration script is the obvious fix and is
not yet written.

---

## 5. Affiliation, and what it unblocked

Q2 is answered. Both papers now carry:

> **Omar Moawad**
> *The American University in Cairo, AUC Avenue, P.O. Box 74, New Cairo 11835, Egypt*

The institutional name and postal address are taken verbatim from AUC's own Editorial Style Guide —
"The" capitalised, "in Cairo" not "of Cairo". The assembly into a single affiliation line is
conventional rather than AUC-prescribed; AUC publishes no mandated publication format. **The
corresponding email remains blank** because I will not guess at it, and a department name should be
added if you hold one.

Governance research on AUC and on Egyptian law produced two findings substantial enough to change P2
rather than merely inform a submission packet, and they are set out in
`SESSION_14B_DATA_FEASIBILITY.md` §3. In summary:

- **Egypt's Law 214/2020 does not reach this work.** It governs clinical medical research —
  therapeutic, pharmaceutical, surgical, nutritional, preventive or diagnostic interventions — and
  confines lawful research to entities registered with the Ministry of Health. Behavioural and
  computing research falls outside it. There is no binding Egyptian national law governing
  non-medical human-subjects research ethics.
- **Egypt's PDPL 151/2020 does reach it, and contains no scientific-research exemption at all.** The
  GDPR's research accommodations at Arts. 5(1)(b), 9(2)(j) and 89 have no Egyptian counterpart. The
  words for "research", "studies" and "university" do not appear in either the law or its executive
  regulations. Sensitive-data processing — which expressly includes psychological, health and
  biometric data — additionally requires a **licence** from the Personal Data Protection Centre, on
  penalty of imprisonment and a fine up to EGP 5,000,000.

**This became P2 §7.1**, a new subsection arguing something the fairness literature has not much
said: a researcher in a jurisdiction with a *weaker* national human-subjects law can face a *stricter*
data-protection constraint on exactly the physiological channels this architecture consumes, with no
research carve-out to fall back on. It is framed as a reading of statutory text, not advice, and it
repeats the §9 limitation that no counsel has reviewed it. I think it is the most novel paragraph in
the paper, and it exists only because you named your institution.

---

## 6. Verification performed

- **Citation integrity, machine-checked.** Every `[n]` in the body of each paper resolves to a defined
  entry, and every defined entry is cited at least once. Both papers: 0 dangling, 0 orphaned. The
  first run of this check found two orphans in P1 and four in P2; all six were fixed by citing them
  where the corresponding method is actually described, not by deleting them.
- **Test suite re-run** against the shipped package: 324 passed, 2 xfailed.
- **No number was changed except to match what the repository currently produces.**

---

## 7. Where the programme stands

| | |
|---|---|
| P1 (TiiS) | 5,137 words, **55 references**, affiliation set |
| P2 (AIES/FAccT) | 5,987 words, **50 references**, affiliation set, new §7.1 |
| Defect register | 33 identified, 24 resolved, D-23 partially mitigated, **D-33 new** |
| Code | v1.1.0, 324 passed / 2 xfailed, unchanged this session |
| Blocking questions | Q2 **answered**. Q4 superseded — see `SESSION_14B` |

**Remaining before submission:** the corresponding email; a department name if you have one; the
cover letters and author statements (formerly Session 14, now Session 15); and the decision recorded
in `SESSION_14B` about what Phase IV can honestly be.

The single largest risk to either paper is no longer the reference list. It is that nobody outside
this project has run the code.
