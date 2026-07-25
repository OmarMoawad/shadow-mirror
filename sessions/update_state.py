"""Fold the post-Session-18 review findings into STATE.json.

STATE.json is the machine-readable programme state and the designated resume
point. Findings that live only in prose are invisible to anyone resuming from it,
so the four defects found while assembling the unified draft (OW-6..OW-9) and the
two release decisions (OW-10) are recorded here in the register's own format.

Idempotent: re-running makes no further change.

Run:  python sessions/update_state.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "STATE.json")

NEW_DEFECTS = [
    {
        "id": "D-35",
        "sev": "critical",
        "where": "archive root; P1 Appendix B, P2 Appendix A",
        "issue": (
            "Benchmark and experiment scripts absent from the archive. run_benchmarks.py, "
            "conformance_v10.py, experiment_d23.py, experiment_ambivalence.py, "
            "analyze_v030_vs_v040.py, make_paper_figures.py and their outputs results.json and "
            "v030_vs_v040.json are not present. Both papers state that every number is produced "
            "by a named script a reviewer can run; as shipped, no headline safety figure, "
            "calibration figure or conformance comparison can be re-derived. The six figures "
            "exist but their generator does not."
        ),
        "fix_session": None,
        "status": "OPEN - blocking for submission (OW-6). Recover from the working environment "
                  "that produced results.json, or regenerate and re-verify every dependent number.",
    },
    {
        "id": "D-36",
        "sev": "high",
        "where": "P1 sec 7 and sec 8; P2 sec 8 and sec 9",
        "issue": (
            "Pre-Session-12 figures still in both manuscripts. P1 sec 7 and P2 sec 9 report the "
            "write-then-consult path as quadratic (3.8x per doubling, 1121 ms at 800 pairs); it is "
            "linear since D-28 (2.0x, 5.24 ms). P1 sec 8 reports identifiability at delta=0.45 with "
            "eight topics as 61.3%; soft-assignment EM gives 97.0%. P2 sec 8 states no append-only "
            "consent record and no deployment-context mechanism exist; both were built in Session 12 "
            "(D-31, D-32), moving the enforcement ratio from 5/12 to 6/12. Same class as D-33: "
            "correct when written, stale after a later session moved the underlying number."
        ),
        "fix_session": None,
        "status": "OPEN - blocking for submission (OW-7). Corrected in papers/UNIFIED_DRAFT.md, "
                  "which states where it departs from P1/P2. Propagate into both papers or withdraw "
                  "them in favour of the unified draft.",
    },
    {
        "id": "D-37",
        "sev": "minor",
        "where": "README; P1 sec 3.6; SESSION_12 report",
        "issue": (
            "Test-count drift across documents. The archive README reports 707 passing; P1 reports "
            "673 collected / 671 passing with a breakdown of 563 invariant checks, 14 negative tests "
            "and 4 positive controls; SESSION_12 reports 324. Each is correct for the version it "
            "describes. Re-running pytest against v1.3.0 returns 707 passed, 2 xfailed. The "
            "per-category breakdown has not been recomputed for the current suite."
        ),
        "fix_session": None,
        "status": "OPEN (OW-8). Recompute the breakdown from `pytest --collect-only` and state it "
                  "once, in one place, tagged with the version it belongs to.",
    },
    {
        "id": "D-38",
        "sev": "moderate",
        "where": "papers/bibliography.json; P1 refs 56-58; P2 refs 51-56",
        "issue": (
            "Nine reference-list entries sit outside the verified set, against ground rule 6. "
            "bibliography.json records 105 manuscript references verified in Session 14 with "
            "entries_without_resolvable_identifier: 0 and the note 'Every manuscript reference "
            "confirmed against a live source'. P1 lists 58 references of which 55 are in that set; "
            "P2 lists 56 of which 50 are. The nine entries are six unique psychometric instrument "
            "sources (Loevinger, Kegan subject-object guide, Ardelt 3D-WS, MEPSI, MLQ, BPNSFS), all "
            "introduced in Session 15 - after the verification pass - and never folded into it. Not "
            "a claim that any is wrong; a claim that the summary line overstates coverage."
        ),
        "fix_session": None,
        "status": "OPEN (OW-9). Verify the six and update counts, or mark them explicitly as "
                  "Session-15 additions pending verification.",
    },
    {
        "id": "D-39",
        "sev": "high",
        "where": "repository: archive/ and branch state",
        "issue": (
            "Two release decisions forced by committing the archive. (a) The full working "
            "conversation transcript is in archive/CONVERSATION.md and archive/TARIK_MESSAGES.md "
            "(~150,000 characters of human-authored text). The repository is private, so this is "
            "storage rather than publication - but both papers' data-availability statements promise "
            "a public repository, and the transcript would go public with it. (b) The v1.3.0 archive "
            "sits on branch shadow-mirror-v1.3.0-archive, not on main; main still carries v0.3.0, so "
            "any repository URL quoted in a submission resolves to the superseded package."
        ),
        "fix_session": None,
        "status": "OPEN (OW-10). (a) Decide deliberately: private repo plus code-only public mirror, "
                  "a controlled deposit, or deliberate publication as a provenance record. "
                  "(b) Review and merge the branch before quoting a URL.",
    },
]

REVIEW_BLOCK = {
    "performed": "2026-07-25, after Session 18",
    "what_it_was": (
        "Assembly of papers/UNIFIED_DRAFT.md and papers/APPENDIX_OUTSTANDING_WORK.md from the "
        "archive, with every quantitative claim traced to its source and re-derived where the "
        "producing file was present. Not a programme session; no new research was performed."
    ),
    "re_derived_by_execution": {
        "pytest -q": "707 passed, 2 xfailed",
        "belief order invariance": "all 120 permutations -> 1 distinct posterior, max spread 0.0",
        "invariant catalogue": "11 callable checks plus check_all",
        "deployment gate": "institutional and undeclared refused; self permitted; empty "
                           "safety_exception_basis still refuses; written basis permits",
        "consent ledger": "verify() True; False after editing one historical entry; "
                          "streams_granted_at time-aware; withdrawal_receipt returns 9 fields",
        "formation refusals": "9 refusing methods called, 9 raised a typed refusal, 0 returned",
        "write-then-consult path": "linear, ~1.8-2.1x per doubling over 100-800 evidence pairs",
    },
    "not_re_derived": (
        "All safety rates, the ablation, refusal calibration, ambivalence, the separation sweep, "
        "inquiry regret, median-split parity, calibration ECE/AUC, identifiability and the prototype "
        "conformance comparison. The producing scripts are absent from the archive - see D-35. These "
        "are carried on the authority of the session reports and are labelled as such in the unified "
        "draft's Appendix A."
    ),
    "defects_opened": ["D-35", "D-36", "D-37", "D-38", "D-39"],
    "new_artifacts": [
        "papers/UNIFIED_DRAFT.md - merges the architecture and ethics strands; supersedes P1/P2 "
        "where they disagree with the shipped package",
        "papers/APPENDIX_OUTSTANDING_WORK.md - standalone outstanding-work appendix",
        "papers/make_bibliography.py -> papers/shadow_mirror_sources.bib (201 entries)",
        "verify_claims.py - re-derives every number used in the unified draft",
        "make_urg_visualization.py -> urg_visualization.png, generated from a real graph",
    ],
}


def main():
    with open(PATH, encoding="utf8") as f:
        s = json.load(f)

    existing = {d["id"] for d in s["defect_register"]}
    added = [d for d in NEW_DEFECTS if d["id"] not in existing]
    s["defect_register"].extend(added)

    s["post_session_18_review"] = REVIEW_BLOCK

    # Q2 was answered in Session 14; open_questions never recorded it, and the
    # next-session pointer still blocks on it.
    q2 = s["open_questions"].get("Q2", {})
    if "answer" not in q2:
        q2["answer"] = ("RESOLVED (Session 14): The American University in Cairo, AUC Avenue, "
                        "P.O. Box 74, New Cairo 11835, Egypt.")
        q2["blocks"] = "None"
        s["open_questions"]["Q2"] = q2

    if s.get("next_session_title", "").startswith("BLOCKED"):
        s["next_session_title"] = (
            "Close D-35 (recover the benchmark scripts) and D-36 (propagate the Session-12 "
            "corrections into P1/P2 or withdraw them). Both are blocking for submission."
        )

    s["status"] = (
        "v1.3.0. Unified draft and outstanding-work appendix assembled and claim-checked against the "
        "shipped package. Blocking for submission: D-35 (benchmark scripts absent, no headline number "
        "re-derivable), D-36 (stale figures in P1/P2). Also open: D-37 test-count drift, D-38 nine "
        "unverified references, D-39 transcript-publication and branch-merge decisions. Previously "
        "blocked on: three dataset downloads, CITI/supervisor details, 2 instrument permissions, "
        "Urban Appraisal rating polarity."
    )

    inv = s.setdefault("artifact_inventory", {})
    inv["post_session_18_review"] = REVIEW_BLOCK["new_artifacts"]

    with open(PATH, "w", encoding="utf8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("defects added      : %s" % ([d["id"] for d in added] or "none (already present)"))
    print("defect_register now: %d items" % len(s["defect_register"]))
    print("next_session_title : %s" % s["next_session_title"][:80])


if __name__ == "__main__":
    main()
