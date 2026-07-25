# Shadow Mirror — Multi-Session Research Program Plan

**Owner:** Tarik Metin · **Started:** 25 July 2026 · **Cadence:** one session per "continue"

Each session is self-contained: it has a defined input, a defined deliverable, and leaves a
`STATE.json` that the next session reads first. Nothing depends on my remembering anything —
re-upload `STATE.json` and the latest deliverables if a session ever starts cold.

---

## Ground rules for this program

1. **No fabricated evidence, ever.** Every number that appears in a paper must be produced by
   code in this repository that a reviewer can run. If a number cannot be produced, the claim
   is deleted, not softened.
2. **Every citation is verified against a live source** before it enters a reference list, with
   arXiv ID or DOI recorded.
3. **Your v0.3.0 engine is the trunk.** New capability is grafted onto it. Nothing that already
   exists — consent gate, trauma guard, ambivalence, decay, topic scoping, refusal — is dropped.
4. **Honest limitation beats impressive claim.** The system's refusals are a feature and will be
   presented as one.
5. **No human-subjects data is collected in these sessions.** Where human evaluation is required,
   I build the *instrument* (protocol, IRB application, analysis plan, pre-registration) so you
   can run it; I do not simulate participants and call it a result.

---

## Phase I — Repair (Sessions 1–5)

| # | Session | Deliverable | Status |
|---|---|---|---|
| **1** | **Audit & program design** | `SESSION_01_AUDIT.md` (18-item defect register, integrity findings, citation verification, monograph map, venue reassessment); this plan; live tracker | ✅ **done** |
| 2 | **Honest benchmark suite v2** | Delete Benchmark 3. Rebuild 1 & 2 as real discriminative tests with genuine scenario generation, real baselines that exist in code, effect sizes with CIs, seeded reproducibility. Add adversarial cases the system should *fail*. Full run log. | ⬜ |
| 3 | **Engine v0.4 — fix the inference core** | Fix D-08 (sample-size sensitivity), D-09 (duplicate threat number), D-11 (topic bleed), D-12 (effective sample size + weighted variance). Extend the test suite to lock each fix. Publish a before/after behavioural diff. | ⬜ |
| 4 | **Unify the two codebases → v1.0-real** | Graft a URG layer onto v0.4 *without* losing consent/trauma/ambivalence. Fix D-13…D-16. Make the demo actually exercise contradiction, tension and refusal. Package as an installable, tested, documented library. | ⬜ |
| 5 | **Conformance suite for the ten invariants** | Turn each architectural invariant into an executable property test (Hypothesis/property-based where possible), so "Invariant II holds" becomes a claim a reviewer can verify by running `pytest`. This is the single strongest evidence a reference-architecture paper can carry. | ⬜ |

## Phase II — Verify the manuscript (Sessions 6–9)

| # | Session | Deliverable | Status |
|---|---|---|---|
| 6 | Bibliography verification, part 1 | Verify every reference in the monograph's 96-entry bibliography against live DOIs; produce a corrections table. | ⬜ |
| 7 | Mathematical chapters audit (pp. 55–79) | Check the formalism for well-definedness, fix the LaTeX corruption visible in the PDF, and confirm each operator has an executable counterpart. | ⬜ |
| 8 | Claim-to-validation matrix, rebuilt | Re-derive the matrix (p. 291) against the *actual* v1.0 code and the conformance suite. Mark every claim: proven / partially supported / unsupported / removed. | ⬜ |
| 9 | Ethics, governance and prohibited-use audit | Check the ethics chapters against GDPR / EU AI Act as currently in force, and against IRB norms for the studies proposed in Phase IV. | ⬜ |

## Phase III — Write the papers (Sessions 10–14)

| # | Session | Deliverable | Status |
|---|---|---|---|
| 10 | **P2 — Ethics-of-design paper** (fastest route to publication; no human subjects needed) | Full draft for AIES / FAccT / CHI: consent as versioned state transition, refusal as output, trauma guard, prohibited-use. Backed by running code. | ⬜ |
| 11 | **P1 — Architecture paper**, draft | Full draft for ACM TiiS / AI Magazine: URG, ten invariants, conformance results, component contracts. | ⬜ |
| 12 | P1 figures and camera-ready assets | Vector figures (PDF/EPS), result charts from real benchmark output, architecture diagrams rebuilt to venue spec. | ⬜ |
| 13 | Adversarial self-review | I review both papers as a hostile Reviewer 2 and produce a rebuttal-hardening pass. | ⬜ |
| 14 | Submission packages | Cover letters, author statements, AI-use disclosure, data/code availability statements, supplementary bundles, formatting compliance checks. | ⬜ |

## Phase IV — Enable the empirical work (Sessions 15+)

| # | Session | Deliverable | Status |
|---|---|---|---|
| 15 | Human-study protocol + IRB packet | Full protocol, consent forms, debrief scripts, risk assessment, and a complete IRB/ethics-committee application for the EWK calibration study. | ⬜ |
| 16 | Pre-registration + analysis plan | OSF-style pre-registration with hypotheses, power analysis, exclusion rules, and the analysis script written *before* data exists. | ⬜ |
| 17 | Deployable study instrument | A runnable web instrument for the study (local-first, consent-gated, exportable), so you can collect data once approved. | ⬜ |
| 18+ | Analysis, P3, and follow-on work | On your data, when it exists. | ⬜ |

---

## Open questions I need from you (these block specific sessions)

| Q | Blocks | Why it can't be guessed |
|---|---|---|
| **Q1. What is the correct author byline?** Is "Omar Moawad" you (pen name), a co-author, or a prior collaborator? If multiple authors, what order and contribution split? | Session 14 | IEEE/ACM authorship policy requires accuracy and consent of all listed authors. |
| **Q2. Do you have an institutional affiliation?** University, lab, or independent? | Sessions 14, 15 | Determines which IRB you can even apply to, and whether "independent researcher" goes on the byline. |
| **Q3. Is the Kimi.ai-generated paper something you want kept at all**, or should I treat it as discarded and write from the monograph directly? | Session 11 | Affects whether Session 11 is a rewrite or a fresh draft. My recommendation: discard it. |
| **Q4. What is your realistic time horizon and appetite for the human study?** Months, or "publish the non-empirical papers and stop"? | Phase IV scoping | Determines whether Phase IV runs at all. |

You can answer these any time — just include them with a "continue". Sessions 2–5 proceed without them.

---

## How to resume

Write **`continue`**. I will read `STATE.json`, pick up the next unstarted session, and deliver it.
If you want to jump the queue ("do session 5 next"), say so and I will re-order.
