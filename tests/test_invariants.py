"""The ten invariants, checked as properties over randomised reflective states.

Two kinds of test per invariant:

  * a **positive** test -- a well-formed graph satisfies it;
  * a **negative** test -- a graph built to violate it is caught.

A conformance check that only ever passes is indistinguishable from a check that
does nothing. The negative tests are what make the positive ones mean something.

The generator is a small seeded random-graph builder rather than a third-party
property-testing library, because the package has no runtime dependencies and
adding one for the test suite alone would undercut the auditability argument the
architecture rests on. 200 randomised graphs per property is ample for structural
properties, which fail on the first counterexample or not at all.
"""

import random

import pytest

from shadow_mirror import (BeliefRevisionEngine, CandidateObservation,
                           InquiryPlanner, UnifiedReflectiveGraph)
from shadow_mirror.invariants import (check_all, check_i_evidence_traceability,
                                      check_ii_provenance_preservation,
                                      check_iii_revision_history,
                                      check_iv_explicit_uncertainty,
                                      check_ix_transactional_consistency,
                                      check_v_hypothesis_independence,
                                      check_vi_context_consistency,
                                      check_vii_explanation_integrity,
                                      check_viii_inquiry_justification,
                                      check_x_human_authority, summarise)

N_RANDOM = 200


def build_well_formed(seed: int):
    """A randomised but invariant-respecting reflective state."""
    rng = random.Random(seed)
    g = UnifiedReflectiveGraph()
    eng = BeliefRevisionEngine(g)

    ctx = g.add_node("Context", {"topic": f"t{rng.randrange(5)}"})
    observations = [g.add_node("Observation", {"raw": rng.random()})
                    for _ in range(rng.randint(2, 5))]

    evidence = []
    for o in observations:
        e = g.add_node("Evidence", {"value": rng.random(),
                                    "reliability": rng.random()})
        g.add_edge(o, e, "provenance")
        evidence.append(e)
    # Some derived evidence with several parents, to exercise Invariant II.
    for _ in range(rng.randint(0, 2)):
        parents = rng.sample(evidence, min(len(evidence), rng.randint(2, 3)))
        d = g.add_node("Evidence", {"kind": "derived"})
        for p in parents:
            g.add_edge(p, d, "provenance")
        evidence.append(d)

    hypotheses = [g.add_node("Hypothesis", {"text": f"H{i}"})
                  for i in range(rng.randint(2, 4))]
    for h in hypotheses:
        g.contextualise(ctx, h)
        for e in rng.sample(evidence, rng.randint(1, len(evidence))):
            rel = "supports" if rng.random() < 0.7 else "contradicts"
            g.add_edge(e, h, rel)
            eng.update(h, e, rng.uniform(0.55, 0.95), rng.uniform(0.05, 0.45))

    posterior = eng.distribution(hypotheses)
    InquiryPlanner(g).plan(posterior, [
        CandidateObservation(f"probe{i}",
                             {h: rng.uniform(0.05, 0.95) for h in hypotheses})
        for i in range(rng.randint(2, 4))
    ])

    ex = g.add_node("Explanation", {
        "summary": "Readings disagree here.",
        "uncertainty": "wide; two readings remain open",
        "assumptions": ["self-report and performance measure the same thing"],
    })
    for h in hypotheses:
        g.add_edge(ex, h, "explains")
    g.contextualise(ctx, ex)
    return g, eng, hypotheses, ctx, ex


# ---------------------------------------------------------------------------
# Positive: a well-formed state satisfies all ten
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", range(N_RANDOM))
def test_all_ten_invariants_hold_on_randomised_well_formed_states(seed):
    g, eng, hyps, ctx, ex = build_well_formed(seed)
    results = check_all(
        g, eng,
        hypotheses_before=hyps,
        outputs=["Your readings disagree here; that may be worth sitting with."],
        questions=["What changed between those two weeks?"],
        disclaimer_present=True,
    )
    failed = [r for r in results if not r.holds]
    assert not failed, summarise(results)


# ---------------------------------------------------------------------------
# Negative: each invariant catches its own violation
# ---------------------------------------------------------------------------

def test_i_catches_an_explanation_with_no_evidence():
    g = UnifiedReflectiveGraph()
    h = g.add_node("Hypothesis", {})
    ex = g.add_node("Explanation", {"summary": "x", "uncertainty": "y", "assumptions": []})
    g.add_edge(ex, h, "explains")          # hypothesis has no evidence at all
    assert not check_i_evidence_traceability(g).holds


def test_ii_catches_a_dropped_provenance_parent():
    """Simulates the D-14 defect: a store that keeps only the first parent."""
    class FirstParentOnly(UnifiedReflectiveGraph):
        def ancestors(self, node_id, relationship="provenance"):
            preds = self.predecessors(node_id, relationship)
            return {preds[0]} if preds else set()

    g = FirstParentOnly()
    a, b = g.add_node("Observation", {}), g.add_node("Observation", {})
    m = g.add_node("Evidence", {})
    g.add_edge(a, m, "provenance")
    g.add_edge(b, m, "provenance")
    assert not check_ii_provenance_preservation(g).holds


def test_iii_catches_a_transition_with_no_triggering_evidence():
    eng = BeliefRevisionEngine()
    eng.update("H", "e1", 0.8, 0.3)
    eng.ledgers["H"].history[0].evidence_id = ""
    assert not check_iii_revision_history(eng).holds


def test_iv_catches_an_explanation_that_hides_its_uncertainty():
    g = UnifiedReflectiveGraph()
    g.add_node("Explanation", {"summary": "definitely this", "assumptions": []})
    assert not check_iv_explicit_uncertainty(g).holds


def test_v_catches_a_competitor_being_dropped():
    g = UnifiedReflectiveGraph()
    kept = g.add_node("Hypothesis", {})
    before = [kept, "a-hypothesis-that-was-deleted"]
    assert not check_v_hypothesis_independence(g, before).holds


def test_vi_catches_a_stale_conclusion_left_unannotated():
    g = UnifiedReflectiveGraph()
    ctx = g.add_node("Context", {"living": "abroad"})
    h = g.add_node("Hypothesis", {})
    g.contextualise(ctx, h)
    new = g.add_node("Context", {"living": "home again"})
    g.add_edge(new, ctx, "revises")        # superseded without annotating h
    assert not check_vi_context_consistency(g).holds


def test_vi_passes_when_revise_context_is_used():
    g = UnifiedReflectiveGraph()
    ctx = g.add_node("Context", {"living": "abroad"})
    h = g.add_node("Hypothesis", {})
    g.contextualise(ctx, h)
    g.revise_context(ctx, {"living": "home again"})
    assert check_vi_context_consistency(g).holds
    assert g.node(h)["data"]["stale"] is True
    assert g.stale_nodes() == [h]


def test_vii_catches_an_explanation_with_no_assumptions_stated():
    g = UnifiedReflectiveGraph()
    g.add_node("Explanation", {"summary": "x", "uncertainty": "wide"})
    assert not check_vii_explanation_integrity(g).holds


def test_viii_catches_an_inquiry_that_justifies_nothing():
    g = UnifiedReflectiveGraph()
    g.add_node("Inquiry", {"description": "just go and find out more"})
    assert not check_viii_inquiry_justification(g).holds


def test_ix_catches_a_partial_write():
    """A store without rollback leaves the failed node behind."""
    class NoRollback(UnifiedReflectiveGraph):
        from contextlib import contextmanager as _cm

        @_cm
        def transaction(self):
            yield self

    g = NoRollback()
    res = check_ix_transactional_consistency(
        g, lambda gg: (gg.add_node("Hypothesis", {}), 1 / 0))
    assert not res.holds


def test_ix_passes_with_rollback():
    g = UnifiedReflectiveGraph()
    g.add_node("Hypothesis", {})
    res = check_ix_transactional_consistency(
        g, lambda gg: (gg.add_node("Hypothesis", {}), 1 / 0))
    assert res.holds
    assert len(g) == 1


def test_x_catches_verdict_phrasing():
    bad = check_x_human_authority(
        ["You are avoiding this because you are afraid."],
        ["What do you notice?"], True)
    assert not bad.holds


def test_x_catches_a_missing_question():
    res = check_x_human_authority(["Readings disagree here."], [], True)
    assert not res.holds


def test_x_catches_a_missing_disclaimer():
    res = check_x_human_authority(["Readings disagree here."],
                                  ["What changed?"], False)
    assert not res.holds


def test_x_accepts_an_offer():
    res = check_x_human_authority(
        ["The two readings disagree, and the evidence does not separate them."],
        ["What was happening around those sessions?"], True)
    assert res.holds


# ---------------------------------------------------------------------------
# The reflection layer must satisfy Invariant X on its real output
# ---------------------------------------------------------------------------

def test_shipped_reflective_prompts_satisfy_human_authority():
    from shadow_mirror import ShadowMirror, reflective_prompts
    m = ShadowMirror(half_life_days=0.0)
    for _ in range(4):
        m.add("knowledge", "self_report", 0.9)
        m.add("knowledge", "task_performance", 0.2)
    prompts = list(reflective_prompts(m))
    res = check_x_human_authority(prompts, prompts,
                                  "disclaimer" in m.report())
    assert res.holds, res.observation


# ---------------------------------------------------------------------------
# Identity of the checks themselves.
#
# Added in Session 17 after mutation testing. mutmut mutated the invariant
# identifier "I" to "XXIXX" and the human-readable name to None, and both mutants
# SURVIVED — no test asserted that a check returns the invariant it claims to be.
# For a paper whose contribution is a named catalogue of architectural properties,
# a silently renameable catalogue is a real gap.
# ---------------------------------------------------------------------------

def test_each_check_returns_its_own_identifier_and_name():
    from shadow_mirror.urg import UnifiedReflectiveGraph
    from shadow_mirror.formation import FormationModel
    import shadow_mirror.invariants as inv

    g = UnifiedReflectiveGraph()
    expected = {
        "check_i_evidence_traceability": ("I", "Evidence traceability"),
        "check_ii_provenance_preservation": ("II", "Provenance preservation"),
        "check_iv_explicit_uncertainty": ("IV", "Explicit uncertainty"),
        "check_vi_context_consistency": ("VI", "Context consistency"),
        "check_vii_explanation_integrity": ("VII", "Explanation integrity"),
        "check_viii_inquiry_justification": ("VIII", "Inquiry justification"),
    }
    for fn_name, (ident, name) in expected.items():
        r = getattr(inv, fn_name)(g)
        assert r.number == ident, f"{fn_name} reported {r.number!r}, expected {ident!r}"
        assert r.name == name, f"{fn_name} reported name {r.name!r}, expected {name!r}"
        assert isinstance(r.observation, str) and r.observation, \
            f"{fn_name} produced no observation; a verdict without evidence is not a check"

    r = inv.check_x_human_authority(["a thought?"], ["a question?"], True)
    assert (r.number, r.name) == ("X", "Human authority")
    r = inv.check_xi_declared_only(FormationModel("p"))
    assert (r.number, r.name) == ("XI", "Declared-only personhood")


def test_invariant_identifiers_are_unique_and_complete():
    from shadow_mirror.urg import UnifiedReflectiveGraph
    from shadow_mirror.formation import FormationModel
    from shadow_mirror.invariants import check_all

    results = check_all(UnifiedReflectiveGraph(), formation=FormationModel("p"))
    idents = [r.number for r in results]
    assert len(idents) == len(set(idents)), f"duplicate invariant identifiers: {idents}"
    assert idents == ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
