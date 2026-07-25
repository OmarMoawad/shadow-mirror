# Shadow Mirror — Outstanding Work

## What is not done, what is blocked, and what would change the conclusions

**Omar Moawad** · *The American University in Cairo*
**Companion appendix to the unified research paper draft · Package `shadow_mirror` v1.3.0 · 25 July 2026**

---

## How to read this document

This is the appendix a reader should check before believing anything in the main draft.

It exists because the programme that produced Shadow Mirror ran under a rule that turns out to be
unusual: **nothing is recorded as pending until a search for a substitute has come back empty.** A
pending list assembled that way is the residue of a search rather than a wishlist, and it is only
worth that if the searches are recorded too. So §2 lists what a search *resolved*, immediately after
§1 lists what it did not.

Four categories, and the distinction between them is the point:

| | | |
|---|---|---|
| **§1** | **Blocked** | Searched for; no substitute exists. Needs collection, permission, or another party |
| **§2** | **Resolved** | Was blocking; a search found a substitute. Recorded with the cost of the substitution |
| **§3** | **Newly found** | Identified while preparing the unified draft. Two are blocking for submission |
| **§4** | **Ordinary** | Simply not done. Nothing external blocks any of it |

A defect that is merely inconvenient does not belong in §1, and putting it there would dilute a list
whose whole value is that every entry has been hunted for and not found.

---

## 1. Blocked: no available substitute

### OW-1 · The threat-confound claim requires primary data collection

The central safety claim — that a reflective system can decline to read threat as desire — is measured
against a simulator. Validating it against people requires four things measured on the same person and
the same item:

1. a stated stance,
2. a behavioural choice that can contradict it,
3. an arousal channel time-locked to that choice, and
4. a coercion manipulation.

Approximately forty public datasets were assessed across affective computing, approach-avoidance
paradigms, ecological momentary assessment, experimental economics and social conformity. **That
four-way intersection does not exist publicly.**

The failure is structural rather than incidental. Corpora with good physiology are passive-viewing
paradigms in which nothing can contradict a rating. Corpora with real choice lack autonomic recording,
self-report, or both. Two published studies used almost exactly the right design and deposited no
data.

**No workaround exists. Only collection.**

### OW-2 · No instrument in the battery is validated in an Egyptian sample

Arabic validations were confirmed for Lebanese, Saudi, Omani, Jordanian, Palestinian, Qatari and
Moroccan samples. **None is Egyptian.**

Four candidate Egyptian-journal papers were identified by DOI, but every `*.ekb.eg` host was
unreachable from the working environment, so their contents are unknown. Egyptian psychometric papers
also frequently construct local instruments rather than translating Western ones, so their relevance
cannot be assumed even if retrieved.

Any use of this battery in Egypt is first-in-population work and must be described as such in the
protocol and in any resulting paper.

**Partially resolvable by a colleague with Egyptian institutional access; not resolvable by open
search.**

### OW-3 · Two instrument constructs have no free replacement

A licence hunt found free, published-mapping substitutes for two of four blocked instruments (§2). It
did not for the other two.

- **An eight-theme Eriksonian inventory.** No openly licensed instrument exists. The two structurally
  correct candidates are both permission-gated, and going upstream from one to the other does not
  escape the gate. The best free material covers two of eight themes and yields single scores rather
  than subscales.
- **Purpose beyond the Meaning in Life Questionnaire.** No free substitute was identified.

**Resolvable only by author permission, which is a letter, not a search.**

### OW-4 · No party outside this project has executed the software

This was the largest risk identified by the programme's own adversarial review, and it was searched
for specifically.

- The **venue route is closed.** Neither ACM TiiS, nor ACM FAccT, nor AAAI/ACM AIES operates an
  artifact-evaluation or badging track that an author can enter at submission time.
- **Archival deposit** satisfies an availability criterion but verifies no execution.
- **Two replication communities** publish work written *by* the replicator and therefore cannot be
  pointed at an artifact.
- **One community code-check service** matches the need exactly — free, accepts submissions on a
  preprint alone, issues a citable certificate naming the person who ran the code. **It has not been
  used.**

The claim the work can currently make is that the code is inspectable, not that it has been
independently run. Note also that this certifies execution, not scientific correctness.

### OW-5 · Invariants X and XI are syntactic proxies for semantic properties

Invariant X detects verdict phrasing by pattern. The accompanying question generator is guarded
against prescriptive drift by a keyword test. **Both raise a floor and neither measures the
property.**

Whether an output usurps a person's authority over their own self-understanding is not a matter of
which pronouns it contains. The check has already produced one documented false positive on real
output, and it will produce false negatives: a sentence can be a verdict without matching any pattern
in the list.

We know of no decision procedure that settles whether a sentence claims authority over a person, and
we do not think one follows from more patterns. **This is a research problem, not an unfinished
task** — which is why it is stated rather than left for a passing check to imply otherwise.

---

## 2. Resolved by a search — recorded so §1 reads as a residue

| Was blocked | Resolved by | Cost of the substitution |
|---|---|---|
| Values instrument permission-gated, item mapping unreachable | The ESS Human Values Scale, whose items and item-to-value mapping are both published, under CC BY-SA documentation terms plus the instrument author's own non-commercial grant, with an already-fielded Arabic version | 10 basic values instead of 19 refined, from 2–3 items each |
| Wisdom instrument permission-gated | The revised Adult Self-Transcendence Inventory, CC BY 4.0, dimensional, whose authors argue explicitly against a total score | Construct drift: it measures self-transcendence and has no analogue of the cognitive dimension |
| Harness coverage unmeasured | Mutation testing | None; it replaced an admission with a number and a work list |
| Invariant identity untested | Found *by* the mutation run — mutating an invariant's identifier produced surviving mutants — and closed with two tests | None |
| Distribution-free coverage guarantees blocked on labelled outcomes | Available under the secondary-analysis route, where two of three corpora supply an item-matched choice that can contradict a stated preference | Applies to the preference model only; the safety claim is untouched |
| Independent execution | A community code-check service that accepts a preprint alone and issues a citable certificate | Certifies execution, not scientific correctness. **Not yet used — see OW-4** |

Two of the four drafted instrument-permission letters became **unnecessary** as a result of this
search.

---

## 3. Newly identified while preparing the unified draft

These were found by assembling the unified draft against the shipped package and checking each number
rather than transcribing it. Both blocking items are of the same kind: a document asserting something
the archive does not support.

### OW-6 · The benchmark scripts and their outputs are not in the archive · **blocking**

Both source papers state that every number is produced by a named script that a reviewer can run. The
archive as assembled contains the package, the papers, the session reports, the figures and the
submission material — but **not** the scripts or the data they wrote:

| Missing | Supports |
|---|---|
| `run_benchmarks.py`, `results.json` | Every safety rate, the ablation, refusal calibration, inquiry regret, median-split parity |
| `conformance_v10.py` | The prototype-versus-package conformance comparison (4/7 vs 7/7) |
| `experiment_d23.py` | Identifiability and offset pooling |
| `experiment_ambivalence.py` | Ambivalence precision, pre- and post-fix |
| `analyze_v030_vs_v040.py`, `v030_vs_v040.json` | Calibration ECE and AUC(uncertainty → error) |
| `make_paper_figures.py` | All six figures — the PDFs and PNGs exist; their generator does not |

Consequence: the headline safety figures cannot be re-derived from what is on hand. They are carried
on the authority of the session reports and the two source papers, and the unified draft's Appendix A
says so explicitly rather than implying reproducibility it cannot demonstrate.

**Action.** Locate these files in the working environment that produced them and commit them; or
regenerate and re-verify every number they support before submission. Until one of those happens, the
data-availability statement in both papers overclaims.

### OW-7 · The two source papers carry pre-Session-12 figures · **blocking**

Four figures were superseded after P1 and P2 were drafted, and both papers still carry the old values:

| Where | Paper still says | Current package |
|---|---|---|
| P1 §7, P2 §9 | Write-then-consult path is quadratic — 3.8× per doubling, 1121 ms at 800 pairs | **Linear.** ≈2.0× per doubling; 5.24 ms at 800 pairs — a 214× improvement |
| P1 §8 | Identifiability at δ = 0.45, eight topics: 61.3% | **97.0%** under soft-assignment EM, which also refuses below three topics |
| P2 §8 | No append-only consent record exists; withdrawal produces no receipt | **Both exist.** Hash-chained ledger; `withdrawal_receipt()` |
| P2 §8 | No deployment-context mechanism; enforcement ratio five of twelve | **Mechanism exists.** Ratio **six of twelve** |

**Action.** Propagate the corrections into `P1_ACM_TiiS_draft.md` and `P2_AIES_FAccT_draft.md`, or
withdraw those files in favour of the unified draft. Submitting either as it stands would publish four
figures the author knows to be stale — which would breach ground rule 3 of the programme.

### OW-8 · Test-count drift across documents

Three documents state three different totals: the archive README says 707 passing; P1 says 673
collected and 671 passing, with a breakdown of 563 invariant checks, 14 negative tests and 4 positive
controls; Session 12 says 324. The first is correct for v1.3.0 and was reproduced while preparing the
unified draft (`pytest -q` → **707 passed, 2 xfailed**). The others are correct for the versions they
describe.

The per-category breakdown has **not** been recomputed for the current suite, so the unified draft
does not restate it.

**Action.** Recompute from `pytest --collect-only` and state the breakdown once, in one place, with
the version it belongs to.

### OW-9 · Nine references sit outside the verified set

Ground rule 6 of the programme: *no citation enters a manuscript unless confirmed against a live
source with a resolvable identifier.* `bibliography.json` records 105 manuscript references verified
in Session 14, with `entries_without_resolvable_identifier: 0` and the note *"Every manuscript
reference confirmed against a live source in Session 14."*

The papers' reference lists are longer than that set:

| | Listed in the paper | In the verified set | Outside it |
|---|---|---|---|
| P1 | 58 | 55 | **3** — entries [56]–[58] |
| P2 | 56 | 50 | **6** — entries [51]–[56] |

Those nine reference-list entries are **six unique sources** — three are cited in both papers. All six
are psychometric instrument sources: Loevinger's ego-development measure, the Kegan subject-object
interview guide, Ardelt's three-dimensional wisdom scale, the Modified Erikson Psychosocial Stage
Inventory, the Meaning in Life Questionnaire, and the Basic Psychological Need Satisfaction and
Frustration Scale. All were introduced in **Session 15**, which built the formation model and
Invariant XI — *after* the Session 14 verification pass, and they were never added to it.

This is not a claim that any of the nine is wrong; they are well-known instruments and each carries an
identifier in the reference list. It is a claim that the bibliography's own summary line overstates
its coverage, and that under ground rule 6 the nine are unconfirmed until someone confirms them.

**Action.** Verify the nine against live sources and fold them into
`manuscript_references_verified_session_14`, updating `counts`; or mark them explicitly as
Session-15 additions pending verification. `papers/make_bibliography.py` emits every entry with a
`keywords = {verified}` flag so the distinction survives into the `.bib`.

### OW-10 · Two release decisions the repository now forces

Neither is a research defect. Both are consequences of the archive having been committed, and both
need a decision before anything is made public.

**The conversation transcript is in the repository.** `archive/CONVERSATION.md` and
`archive/TARIK_MESSAGES.md` hold the full working transcript — roughly 150,000 characters of
human-authored text, including the original brief. The repository is currently **private**, so this is
storage rather than publication. It stops being true the moment the repository is made public, or a
zip of it is attached to a preprint or an artifact submission. The data-availability statements in both
papers promise a public repository.
**Action.** Decide before publishing: keep the transcript in a private repository and publish a code-
only mirror, move it behind a separate access-controlled deposit, or publish it deliberately as a
provenance record. Publishing it by omission is the one option to avoid.

**The v1.3.0 archive sits on a branch, not on `main`.** It was pushed to
`shadow-mirror-v1.3.0-archive` rather than merged, so `main` still carries v0.3.0 — 34 tests, none of
the papers, and none of the modules the drafts describe. Any repository URL quoted in a submission
would currently resolve to the old package.
**Action.** Review and merge, then confirm that the URL in the availability statements points at the
merged state.

---

## 4. Ordinary unfinished work

Nothing here is blocked on anything external. It is simply not done.

| Item | Status |
|---|---|
| **Causal reflection** operator — intervention, counterfactual query | Declared gap, strict `xfail`. No do-operator exists. Presented as research agenda, not as a component |
| **Knowledge consolidation** operator — promotion from belief to revisable knowledge | Declared gap, strict `xfail`. No promotion criterion exists |
| Read path still O(n) per consultation | Open. A read-heavy pattern (one consultation per twenty writes) still scales at 3.1× per doubling. Anchored-decay accumulators would fix it |
| 1,549 surviving mutants of 5,114 — mutation score 59.9% | Open. Concentrated in the inference engine (404), the pattern layer (278), the invariant checks themselves (206) and the formation model (195) |
| 909 mutants in an untested command-line interface | Open. Carries no claim in any paper, which is why it is last |
| Candidate belief state for monotonic drift | Proposal. "Your position moved steadily" was computed and discarded |
| Conformal calibration for credible sets | Blocked on labelled outcomes — i.e. on a human study. A set claiming 90% mass contains the truth 60.5% of the time at δ = 0.45 |
| Encryption at rest | Specified, unimplemented |
| Multimodal acquisition | Specified, unimplemented |
| Reflective execution engine with event queues | Specified, unimplemented |
| Any user interface beyond a command line | Specified, unimplemented |

---

## 5. Before submission

| Item | Who can close it |
|---|---|
| Corresponding email, and a department if one applies | **You.** The only gap in the author block |
| Repository URL in both availability statements | **You** |
| Venue selection for the ethics paper — AIES or FAccT | **You.** Check current calls; dates move annually |
| **OW-6** — recover or regenerate the benchmark scripts | Whoever holds the working environment that produced `results.json` |
| **OW-7** — propagate corrections into P1 and P2, or withdraw them | **You**, editorially |
| **OW-10** — decide whether the conversation transcript ships publicly | **You.** Decide before the repository is made public, not after |
| **OW-10** — merge `shadow-mirror-v1.3.0-archive` into `main` | **You.** Until then a quoted repository URL resolves to v0.3.0 |
| Three dataset downloads for the secondary-analysis route | Mechanical. Two are small — 35 MB and 16 MB |
| Urban Appraisal rating polarity | From the BeMoBIL analysis code. The loader refuses until supplied |
| Two instrument permissions — Claremont Purpose Scale, MEPSI | Letters to the instrument authors. Two of the original four are no longer needed |
| CITI certification and a named supervisor | Only if the primary study proceeds |
| AUC IRB packet — `[YOU]` markers | **You.** The packet is drafted and **not submitted** |

---

## 6. What would change the conclusions

Stated separately from everything above, because these are the items that would move the work rather
than merely extend it. Each is phrased so that a null result is still a result.

**1 · A human-subjects study.** Research objective O4 — *does any of this change how a person reasons
about themselves?* — is unanswered. Every claim about reflection, comprehension or trust is currently
a design intention with no evidence behind it. The architecture could be entirely sound and the
interaction could still fail, and nothing collected so far would detect that.

**2 · Primary collection on the four-way intersection (OW-1).** The safety result is a property of a
simulator that encodes the authors' own theory of how threat and preference differ in observable
signal. Real data could refute the *ordering* of the methods, not merely the magnitude of the rates —
and the ordering is the claim.

**3 · A third party running the conformance suite against a different substrate (OW-4).** The
decision procedure has been shown to separate two implementations, which rules out vacuity. It has not
been shown to be portable to a graph database, an event-sourced store, or a logic programming
substrate. Until someone unconnected to this work runs it, *decidable* is demonstrated and *decidable
usefully* is not.

**4 · A decision procedure for semantic authority (OW-5).** Invariants X and XI raise a floor they
cannot measure. A real answer here would change what the strongest invariant in the catalogue is
actually worth.

---

## 7. What is deliberately not in this document

Two things, so their absence is not read as an oversight.

**Speculative extensions.** Physiological sensing beyond the single arousal proxy, hierarchical
Bayesian models, causal inference over the graph, LLM-assisted reflection: these appear in earlier
drafts as "future research". They are not listed here because listing an idea next to a blocked
dependency implies the two are comparable, and they are not. An idea is not outstanding work until
something is waiting on it.

**Applications.** Mental-health support, education, coaching, organisational psychology. Earlier
drafts listed these as potential applications. The regulatory analysis withdrew the education-pilot
recommendation outright, and the software refuses to run in institutional deployment contexts. Naming
application domains for a system with no human-subjects evidence and an active prohibition against
two of those domains would be the kind of claim this appendix exists to prevent.
