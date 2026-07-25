# Session index

Eighteen sessions. Two of them produced no report of their own, and that is not an omission:
**Sessions 10 and 11 produced the paper drafts themselves** — P2 and P1 respectively — which live in
`../papers/`. Everything else has a report here.

| # | Report | What happened |
|---|---|---|
| 1 | `SESSION_01_AUDIT.md` | Audit of the inherited work. 32 defects found, including a fabricated t-test and a watermark on 8 of 9 pages |
| 2 | `SESSION_02_BENCHMARKS.md` | Benchmark suite v2, byte-reproducible |
| 2b | `SESSION_02B_DRAFT_ADJUDICATION.md` | Adjudication of an externally supplied draft |
| 2c | `SESSION_02C_DRAFT2_ADJUDICATION.md` | Adjudication of a second one; ground rule 7 added here |
| 3 | `SESSION_03_ENGINE_V04.md` | Engine v0.4. D-19: the guard now refuses rather than imputing a missing channel as zero |
| 4 | `SESSION_04_UNIFIED_V1.md` | Unified v1.0. NetworkX removed — zero runtime dependencies |
| 5 | `SESSION_05_INVARIANTS_D23.md` | Invariants made executable. D-23 characterised, not tuned away |
| 6 | `SESSION_06_BIBLIOGRAPHY_VENUE.md` | Bibliography audit and venue selection |
| 7 | `SESSION_07_FORMALISM.md` | Formal appendix corrected. D-27 found by measurement: 4.2× per doubling |
| 8 | `SESSION_08_CLAIM_MATRIX.md` | Every claim mapped to the file that produces it. D-29 ambivalence gate |
| 9 | `SESSION_09_ETHICS_REGULATORY.md` | EU AI Act and GDPR analysis. **Withdrew Session 6's education-pilot recommendation** |
| 10 | *(no report — produced `P2_AIES_FAccT_draft.md`)* | The ethics paper |
| 11 | *(no report — produced `P1_ACM_TiiS_draft.md`)* | The architecture paper |
| 12 | `SESSION_12_ASSETS_DEFECTS.md` | Figures, defect sweep, v1.1.0 |
| 13 | `SESSION_13_ADVERSARIAL_REVIEW.md` | Fourteen attacks. One found a result that weakened the headline |
| 14 | `SESSION_14_RELATED_WORK_AND_AFFILIATION.md` | 76 references verified. "Fawn" found not to be peer-reviewed |
| 14b | `SESSION_14B_DATA_FEASIBILITY.md` | ~40 datasets assessed. None can validate the safety claim |
| 15 | `SESSION_15_FORMATION_MODEL.md` | Declared-only personhood; four refusals; Invariant XI |
| 16 | `SESSION_16_PAPER_RECONCILIATION.md` | Papers reconciled to eleven invariants. D-34 |
| 17 | `SESSION_17_WORKAROUND_HUNT.md` | Eleven blockers searched; six dissolved. Mutation score 59.9% |
| 18 | `SESSION_18_ROUTE_A_AND_IRB.md` | Route A loaders and the AUC IRB packet |

`STATE.json` is the machine-readable state: 34-item defect register, verified citations, ground rules,
blocking questions, and per-session results. Read it first if you are resuming this work.
