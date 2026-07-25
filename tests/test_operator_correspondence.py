"""Every operator in the formal appendix must have an executable counterpart.

A reference architecture earns the word "reference" when the gap between its
formalism and its implementation is enumerable. These tests enumerate it: each
operator in §A.1 is either bound to a callable here, or explicitly recorded as
unimplemented with an xfail carrying the reason.

They also pin the measured complexity bounds in §A.10, so a future change that
reintroduces quadratic growth in the belief update fails the suite rather than
being discovered by a user with a long journal.
"""

import time

import pytest

from shadow_mirror import (BeliefRevisionEngine, CandidateObservation, EWKProfile,
                           InquiryPlanner, ShadowMirror, UnifiedReflectiveGraph,
                           expected_information_gain)
from shadow_mirror.credible import credible_set


# ---------------------------------------------------------------------------
# Operator I -- evidence construction
# ---------------------------------------------------------------------------

def test_operator_I_ingest_attaches_provenance_reliability_and_time():
    m = ShadowMirror(half_life_days=0.0)
    obs = m.add("knowledge", "self_report", 0.9, "algebra", "felt fine", 0.7)
    assert obs.value == 0.9 and obs.reliability == 0.7
    assert obs.topic == "algebra" and obs.timestamp
    assert obs.context == "felt fine"


def test_operator_I_provenance_is_a_set_not_a_scalar():
    """§A.2: p_i is a set. Writing it as a scalar is what licensed D-14."""
    g = UnifiedReflectiveGraph()
    a, b = g.add_node("Observation", {}), g.add_node("Observation", {})
    e = g.add_node("Evidence", {})
    g.add_edge(a, e, "provenance")
    g.add_edge(b, e, "provenance")
    assert g.ancestors(e) == {a, b}


# ---------------------------------------------------------------------------
# Operator K -- context construction
# ---------------------------------------------------------------------------

def test_operator_K_context_revision_annotates_dependents():
    g = UnifiedReflectiveGraph()
    c = g.add_node("Context", {"phase": "exam term"})
    h = g.add_node("Hypothesis", {})
    g.contextualise(c, h)
    g.revise_context(c, {"phase": "vacation"})
    assert g.node(h)["data"]["stale"] is True


# ---------------------------------------------------------------------------
# Operator G -- hypothesis generation (plurality, axiom B1)
# ---------------------------------------------------------------------------

def test_operator_G_multiple_hypotheses_coexist():
    m = ShadowMirror(half_life_days=0.0)
    for _ in range(4):
        m.add("knowledge", "self_report", 0.55)
        m.add("knowledge", "task_performance", 0.55)
    post = m.current().knowledge
    assert sum(1 for v in post.values() if v > 0.05) >= 2
    assert abs(sum(post.values()) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Operator B -- belief revision, axioms B1-B4
# ---------------------------------------------------------------------------

def test_axiom_B2_commutativity():
    a = BeliefRevisionEngine(); b = BeliefRevisionEngine()
    ev = [("e1", 0.9, 0.2), ("e2", 0.3, 0.8), ("e3", 0.7, 0.4)]
    for name, lt, lf in ev:
        a.update("H", name, lt, lf)
    for name, lt, lf in reversed(ev):
        b.update("H", name, lt, lf)
    assert a.belief("H") == pytest.approx(b.belief("H"), abs=1e-12)


def test_axiom_B3_invertibility():
    e = BeliefRevisionEngine()
    e.update("H", "e1", 0.9, 0.2)
    before = e.belief("H")
    e.update("H", "e2", 0.2, 0.9)
    e.retract("H", "e2")
    assert e.belief("H") == pytest.approx(before, abs=1e-12)


def test_axiom_B4_audit_records_every_required_field():
    e = BeliefRevisionEngine()
    e.update("H", "e1", 0.8, 0.3, reliability=0.6)
    r = e.revision_history("H")[0]
    for field in ("hypothesis_id", "evidence_id", "prior", "posterior", "method"):
        assert getattr(r, field) is not None and getattr(r, field) != ""


def test_state_is_not_clamped_but_display_is():
    """§A.4: clamping the state destroys B3."""
    e = BeliefRevisionEngine()
    for i in range(60):
        e.update("H", f"e{i}", 0.99, 0.01)
    led = e.ledger("H")
    assert led.display_probability() <= 0.999
    assert led.log_odds() > 100          # state carries what display cannot show


# ---------------------------------------------------------------------------
# Operator Q -- inquiry planning
# ---------------------------------------------------------------------------

def test_operator_Q_eig_depends_on_the_candidate():
    """The heuristic it replaces did not, which is why it matched random."""
    post = {"H1": 0.5, "H2": 0.5}
    g1 = expected_information_gain(post, CandidateObservation("flat", {"H1": 0.6, "H2": 0.6}))
    g2 = expected_information_gain(post, CandidateObservation("sharp", {"H1": 0.95, "H2": 0.05}))
    assert g1 < g2


def test_operator_Q_ranks_by_gain_per_unit_cost():
    post = {"H1": 0.5, "H2": 0.5}
    cheap = CandidateObservation("cheap", {"H1": 0.8, "H2": 0.2}, cost=1.0)
    dear = CandidateObservation("dear", {"H1": 0.95, "H2": 0.05}, cost=50.0)
    best = InquiryPlanner().best_value_for_cost(post, [cheap, dear])
    assert "cheap" in best.description


# ---------------------------------------------------------------------------
# Operator X -- explanation synthesis, and the credible set of §A.7
# ---------------------------------------------------------------------------

def test_operator_X_credible_set_is_the_smallest_reaching_the_mass():
    post = {"a": 0.5, "b": 0.3, "c": 0.15, "d": 0.05}
    names, mass = credible_set(post, 0.75)
    assert names == ["a", "b"] and mass == pytest.approx(0.8)
    assert credible_set(post, 0.4)[0] == ["a"]


def test_operator_X_ewk_streams_produce_questions_not_labels():
    p = EWKProfile()
    for _ in range(3):
        p.observe_many([("knowledge", 0.30), ("will", 0.75), ("emotion", 0.80)])
    r = p.read()
    assert r.tensions
    assert all(t.question.rstrip().endswith("?") for t in r.tensions)
    assert "not claims about an inner state" in r.to_dict()["disclaimer"]


# ---------------------------------------------------------------------------
# §A.10 -- the measured complexity bounds, pinned
# ---------------------------------------------------------------------------

def _scaling(fn, sizes, repeats: int = 3):
    """Best-of-N timing. Wall-clock on a shared machine is noisy, and a single
    slow sample turns a linear algorithm into a failing test; the minimum over a
    few runs is the standard way to measure the algorithm rather than the load."""
    times = []
    for n in sizes:
        best = float("inf")
        for _ in range(repeats):
            t0 = time.perf_counter()
            fn(n)
            best = min(best, time.perf_counter() - t0)
        times.append(best)
    return [times[i + 1] / max(times[i], 1e-9) for i in range(len(times) - 1)]


def test_belief_update_is_linear_in_the_number_of_updates():
    """D-27: the naive ledger summed all contributions per update, giving ~4x per
    doubling. Anything above 3x here means the running total was lost again."""
    def run(n):
        e = BeliefRevisionEngine()
        for i in range(n):
            e.update("H", f"e{i}", 0.7, 0.4)

    ratios = _scaling(run, [4000, 8000, 16000])
    assert max(ratios) < 3.0, ratios


def test_provenance_closure_is_linear_in_graph_size():
    def run(d):
        g = UnifiedReflectiveGraph()
        prev = g.add_node("Observation", {})
        for _ in range(d):
            n = g.add_node("Evidence", {})
            g.add_edge(prev, n, "provenance")
            prev = n
        g.ancestors(prev)

    ratios = _scaling(run, [2000, 4000, 8000])
    # Linear is 2.0x per doubling; quadratic is 4.0x. 3.0 separates them with room.
    assert max(ratios) < 3.0, ratios


# ---------------------------------------------------------------------------
# Operators with no implementation -- recorded, not hidden
# ---------------------------------------------------------------------------

@pytest.mark.xfail(reason="Causal reflective reasoning (monograph pp. 64-66) has no "
                          "implementation. do-operator, intervention and counterfactual "
                          "queries are specified in prose only. Scheduled: research agenda.",
                   strict=True)
def test_causal_intervention_operator_exists():
    from shadow_mirror import CausalReflection  # noqa: F401


@pytest.mark.xfail(reason="Knowledge consolidation K_t <- B_t (monograph p. 145) is "
                          "specified but unimplemented: no promotion criterion from "
                          "belief to revisable knowledge exists in code.",
                   strict=True)
def test_knowledge_consolidation_operator_exists():
    from shadow_mirror import KnowledgeConsolidation  # noqa: F401
