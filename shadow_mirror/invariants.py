"""The ten architectural invariants, as executable checks.

A reference architecture whose invariants are prose is a set of intentions. The
claim this module supports is narrower and much stronger: *these ten properties
are decidable, and here is the procedure that decides them.* Anyone can run it
against any candidate implementation, including a future rewrite of this one.

Each check returns an ``InvariantResult`` with a verdict and the observation that
produced it — never a score. A property that holds by construction is not an
experimental result, and reporting it as a percentage is how a conformance check
gets mistaken for evidence.

Two invariants resist mechanical checking and are operationalised deliberately:

* **VI (Context Consistency)** cannot mean "recompute the past", because an
  instrument cannot re-run a person's week. It is operationalised as: when a
  context is superseded, every conclusion that depended on it is *annotated* as
  stale rather than silently retained or silently deleted.

* **X (Human Authority)** is a property of what reaches the person, so it is
  operationalised at the output boundary: every terminal output carries its
  uncertainty and its disclaimer, and offers at least one question; none is
  phrased as a verdict or an instruction. That is checkable, and it is the part
  that actually protects anyone.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

from .urg import UnifiedReflectiveGraph

#: Phrasings that turn an offer into an instruction, or a reading into an
#: identity claim. Invariant X forbids them at the output boundary.
#:
#: Scoped deliberately to claims about *who someone is* and directives about what
#: they must do. An earlier draft matched any "you have", which flagged the
#: reactivity caution ("You have consulted this 5 times") -- a factual statement
#: about the person's own logged behaviour, and one the architecture specifically
#: wants surfaced. That was a defect in the check, not in the system, and it was
#: found by running the check against the shipped output rather than against a
#: fixture. Conformance suites need to be pointed at real output for exactly this
#: reason.
VERDICT_PATTERNS = (
    r"\byou are\b", r"\byou really\b", r"\byou secretly\b",
    r"\byour true\b", r"\byou actually (want|feel|are)\b",
    r"\byou have (a|an)\b", r"\byou must\b", r"\byou should\b",
    r"\bclearly you\b", r"\bthis proves\b", r"\bthe answer is\b",
    r"\bdiagnos", r"\byour type is\b",
)


@dataclass
class InvariantResult:
    number: str
    name: str
    holds: bool
    observation: str

    def __str__(self) -> str:
        return f"[{'PASS' if self.holds else 'FAIL'}] {self.number} {self.name}: {self.observation}"


# ---------------------------------------------------------------------------
# I -- Evidence Traceability
# ---------------------------------------------------------------------------

def check_i_evidence_traceability(urg: UnifiedReflectiveGraph) -> InvariantResult:
    """Every explanatory statement traces to at least one evidence object."""
    orphans = urg.orphan_conclusions()
    total = len(urg.nodes_of_type("Explanation"))
    return InvariantResult(
        "I", "Evidence traceability", not orphans,
        f"{total - len(orphans)}/{total} explanations reach evidence"
        + (f"; orphans: {orphans[:3]}" if orphans else ""),
    )


# ---------------------------------------------------------------------------
# II -- Provenance Preservation
# ---------------------------------------------------------------------------

def check_ii_provenance_preservation(urg: UnifiedReflectiveGraph) -> InvariantResult:
    """Every evidence node with parents can recover *all* of them."""
    bad = []
    checked = 0
    for e in urg.nodes_of_type("Evidence"):
        direct = set(urg.predecessors(e, "provenance"))
        if not direct:
            continue
        checked += 1
        if not direct <= urg.ancestors(e):
            bad.append(e)
    return InvariantResult(
        "II", "Provenance preservation", not bad,
        f"{checked - len(bad)}/{checked} derived evidence nodes recover every parent",
    )


# ---------------------------------------------------------------------------
# III -- Revision History
# ---------------------------------------------------------------------------

def check_iii_revision_history(engine) -> InvariantResult:
    """Every belief transition preserves prior, posterior, method and evidence."""
    missing, total = [], 0
    for hid, led in getattr(engine, "ledgers", {}).items():
        for rev in led.history:
            total += 1
            if not (rev.evidence_id and rev.method
                    and rev.prior is not None and rev.posterior is not None):
                missing.append((hid, rev.evidence_id))
    return InvariantResult(
        "III", "Revision history", not missing,
        f"{total - len(missing)}/{total} transitions carry prior, posterior, "
        f"triggering evidence and method",
    )


# ---------------------------------------------------------------------------
# IV -- Explicit Uncertainty
# ---------------------------------------------------------------------------

def check_iv_explicit_uncertainty(urg: UnifiedReflectiveGraph) -> InvariantResult:
    """No explanation may be emitted without stating its uncertainty."""
    silent = [e for e in urg.nodes_of_type("Explanation")
              if not str(urg.node(e)["data"].get("uncertainty", "")).strip()]
    total = len(urg.nodes_of_type("Explanation"))
    return InvariantResult(
        "IV", "Explicit uncertainty", not silent,
        f"{total - len(silent)}/{total} explanations state their uncertainty",
    )


# ---------------------------------------------------------------------------
# V -- Hypothesis Independence
# ---------------------------------------------------------------------------

def check_v_hypothesis_independence(urg: UnifiedReflectiveGraph,
                                    before: Optional[Sequence[str]] = None
                                    ) -> InvariantResult:
    """Contradicting one hypothesis must not remove or merge its competitors."""
    now = set(urg.nodes_of_type("Hypothesis"))
    lost = (set(before) - now) if before is not None else set()
    contested = urg.contested_hypotheses()
    return InvariantResult(
        "V", "Hypothesis independence", not lost,
        f"{len(now)} hypotheses retained, {len(lost)} lost; "
        f"{len(contested)} held contested rather than resolved",
    )


# ---------------------------------------------------------------------------
# VI -- Context Consistency
# ---------------------------------------------------------------------------

def check_vi_context_consistency(urg: UnifiedReflectiveGraph) -> InvariantResult:
    """Superseded contexts must leave their dependents annotated, not silent."""
    unannotated = []
    superseded = 0
    for ctx in urg.nodes_of_type("Context"):
        if not urg.predecessors(ctx, "revises"):
            continue
        superseded += 1
        for dep in urg.successors(ctx, "contextualises"):
            if not urg.node(dep)["data"].get("stale"):
                unannotated.append(dep)
    return InvariantResult(
        "VI", "Context consistency", not unannotated,
        f"{superseded} superseded context(s); {len(unannotated)} dependent "
        f"conclusion(s) left unannotated",
    )


# ---------------------------------------------------------------------------
# VII -- Explanation Integrity
# ---------------------------------------------------------------------------

REQUIRED_EXPLANATION_FIELDS = ("summary", "uncertainty", "assumptions")


def check_vii_explanation_integrity(urg: UnifiedReflectiveGraph) -> InvariantResult:
    """An explanation names its evidence, its assumptions and what remains open."""
    bad = []
    for e in urg.nodes_of_type("Explanation"):
        d = urg.node(e)["data"]
        if any(k not in d for k in REQUIRED_EXPLANATION_FIELDS):
            bad.append(e)
    total = len(urg.nodes_of_type("Explanation"))
    return InvariantResult(
        "VII", "Explanation integrity", not bad,
        f"{total - len(bad)}/{total} explanations carry "
        f"{', '.join(REQUIRED_EXPLANATION_FIELDS)}",
    )


# ---------------------------------------------------------------------------
# VIII -- Inquiry Justification
# ---------------------------------------------------------------------------

def check_viii_inquiry_justification(urg: UnifiedReflectiveGraph) -> InvariantResult:
    """Every inquiry says what it would resolve and which hypotheses it separates."""
    bad = []
    for i in urg.nodes_of_type("Inquiry"):
        d = urg.node(i)["data"]
        gain = d.get("expected_information_gain_bits", 0.0)
        if gain <= 0 or not d.get("targets") or not d.get("motivation"):
            bad.append(i)
        elif not urg.successors(i, "targets"):
            bad.append(i)
    total = len(urg.nodes_of_type("Inquiry"))
    return InvariantResult(
        "VIII", "Inquiry justification", not bad,
        f"{total - len(bad)}/{total} inquiries quantify their expected gain and "
        f"name the hypotheses they discriminate",
    )


# ---------------------------------------------------------------------------
# IX -- Transactional Consistency
# ---------------------------------------------------------------------------

def check_ix_transactional_consistency(urg: UnifiedReflectiveGraph,
                                       failing_update: Callable[[UnifiedReflectiveGraph], None]
                                       ) -> InvariantResult:
    """A failed update must leave no partial state behind."""
    before = urg.to_dict()
    raised = False
    try:
        with urg.transaction():
            failing_update(urg)
    except Exception:
        raised = True
    after = urg.to_dict()
    same = (len(before["nodes"]) == len(after["nodes"])
            and len(before["edges"]) == len(after["edges"]))
    return InvariantResult(
        "IX", "Transactional consistency", raised and same,
        f"failure {'raised' if raised else 'did not raise'}; graph "
        f"{'unchanged' if same else 'left partially written'} "
        f"({len(before['nodes'])}→{len(after['nodes'])} nodes, "
        f"{len(before['edges'])}→{len(after['edges'])} edges)",
    )


# ---------------------------------------------------------------------------
# X -- Human Authority
# ---------------------------------------------------------------------------

def check_x_human_authority(outputs: Sequence[str],
                            questions: Sequence[str],
                            disclaimer_present: bool) -> InvariantResult:
    """Nothing that reaches the person may be phrased as a verdict."""
    offenders = []
    for text in outputs:
        low = text.lower()
        for pat in VERDICT_PATTERNS:
            if re.search(pat, low):
                offenders.append((pat, text[:70]))
                break
    has_question = any(q.rstrip().endswith("?") for q in questions)
    holds = not offenders and has_question and disclaimer_present
    return InvariantResult(
        "X", "Human authority", holds,
        f"{len(outputs)} output(s) checked; {len(offenders)} verdict phrasing(s); "
        f"question offered: {has_question}; disclaimer present: {disclaimer_present}"
        + (f"; first offender: {offenders[0]}" if offenders else ""),
    )


def check_xi_declared_only(model) -> InvariantResult:
    """Nothing about a person exists in a formation model unless they put it there.

    Two conditions, both decidable by inspection of the model rather than by trusting
    the code that built it:

    (a) every attribute is either a declaration by the subject or a score from an
        instrument the subject self-completed; and
    (b) the model exposes no route to a global rank, a prescribed deficit, or an
        attributed purpose — calling those methods must refuse rather than return.

    Condition (b) is the interesting one. It is checked by *calling* each refusing
    method and requiring a ``FormationRefusal``. A method that returned a value, or
    that was quietly absent, would both fail: absence is not refusal, because a
    caller cannot read an explanation off a missing attribute.
    """
    from .formation import FormationRefusal

    offenders: List[str] = []

    for admin in getattr(model, "_administrations", []):
        if not admin.self_completed:
            offenders.append(f"instrument {admin.instrument_id} not self-completed")

    refusing = (
        ("infer_background", "INFERRED_ORIGIN"),
        ("infer_origin", "INFERRED_ORIGIN"),
        ("maturity_level", "GLOBAL_RANKING"),
        ("overall_maturity", "GLOBAL_RANKING"),
        ("developmental_stage", "GLOBAL_RANKING"),
        ("what_they_still_need", "PRESCRIPTIVE_DEFICIT"),
        ("deficits", "PRESCRIPTIVE_DEFICIT"),
        ("eventual_purpose", "PURPOSE_ATTRIBUTION"),
        ("life_purpose", "PURPOSE_ATTRIBUTION"),
    )
    for name, expected in refusing:
        fn = getattr(model, name, None)
        if fn is None:
            offenders.append(f"{name} absent; absence is not refusal")
            continue
        try:
            fn()
        except FormationRefusal as exc:
            if exc.ground != expected:
                offenders.append(f"{name} refused on {exc.ground}, expected {expected}")
        except Exception as exc:  # pragma: no cover - defensive
            offenders.append(f"{name} raised {type(exc).__name__}, not FormationRefusal")
        else:
            offenders.append(f"{name} returned a value instead of refusing")

    prof = model.profile()
    if any(k in prof for k in ("total", "overall", "score", "level", "stage")):
        offenders.append("profile() exposes an aggregate")

    holds = not offenders
    return InvariantResult(
        "XI", "Declared-only personhood", holds,
        f"{len(getattr(model, '_administrations', []))} administration(s), "
        f"{len(refusing)} refusing method(s) exercised; {len(offenders)} offender(s)"
        + (f"; first: {offenders[0]}" if offenders else ""),
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def check_all(urg: UnifiedReflectiveGraph, engine=None, *,
              hypotheses_before: Optional[Sequence[str]] = None,
              outputs: Sequence[str] = (), questions: Sequence[str] = (),
              disclaimer_present: bool = False,
              failing_update: Optional[Callable] = None,
              formation=None) -> List[InvariantResult]:
    def boom(g):
        g.add_node("Hypothesis", {"partial": True})
        raise RuntimeError("simulated mid-update failure")

    results = [
        check_i_evidence_traceability(urg),
        check_ii_provenance_preservation(urg),
        check_iii_revision_history(engine) if engine is not None else
        InvariantResult("III", "Revision history", False, "no engine supplied"),
        check_iv_explicit_uncertainty(urg),
        check_v_hypothesis_independence(urg, hypotheses_before),
        check_vi_context_consistency(urg),
        check_vii_explanation_integrity(urg),
        check_viii_inquiry_justification(urg),
        check_ix_transactional_consistency(urg, failing_update or boom),
        check_x_human_authority(outputs, questions, disclaimer_present),
    ]
    if formation is not None:
        results.append(check_xi_declared_only(formation))
    return results


def summarise(results: Sequence[InvariantResult]) -> str:
    lines = [str(r) for r in results]
    passed = sum(1 for r in results if r.holds)
    lines.append(f"-> {passed}/{len(results)} invariants hold")
    return "\n".join(lines)
