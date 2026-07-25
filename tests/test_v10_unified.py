"""Regression tests for the v1.0 unification.

Each test targets a defect from the Session 1-3 registers. They fail on the
prototype (`shadow_mirror_v1.py`) and pass on v1.0.
"""

import itertools
import math
import random

import pytest

from shadow_mirror import (BeliefRevisionEngine, CandidateObservation, EWKProfile,
                           InquiryPlanner, ShadowMirror, UnifiedReflectiveGraph,
                           expected_information_gain)
from shadow_mirror.urg import URGError


# ---------------------------------------------------------------------------
# D-14 -- provenance is a DAG, not a chain  (Invariant II)
# ---------------------------------------------------------------------------

def test_d14_multi_parent_provenance_is_fully_recoverable():
    """The prototype followed preds[0] only and recovered 0 of 2 parents."""
    g = UnifiedReflectiveGraph()
    a = g.add_node("Observation", {"src": "quiz"})
    b = g.add_node("Observation", {"src": "self_report"})
    merged = g.add_node("Evidence", {"kind": "derived"})
    g.add_edge(a, merged, "provenance")
    g.add_edge(b, merged, "provenance")
    assert g.ancestors(merged) == {a, b}


def test_d14_deep_and_branching_provenance():
    g = UnifiedReflectiveGraph()
    roots = [g.add_node("Observation", {"i": i}) for i in range(4)]
    mid = [g.add_node("Evidence", {"i": i}) for i in range(2)]
    top = g.add_node("Evidence", {"i": "top"})
    for i, r in enumerate(roots):
        g.add_edge(r, mid[i // 2], "provenance")
    for m in mid:
        g.add_edge(m, top, "provenance")
    assert g.ancestors(top) == set(roots) | set(mid)
    assert len(g.provenance_paths(top)) == 4


def test_d14_provenance_cycles_do_not_hang():
    g = UnifiedReflectiveGraph()
    a = g.add_node("Evidence", {})
    b = g.add_node("Evidence", {})
    g.add_edge(a, b, "provenance")
    g.add_edge(b, a, "provenance")
    assert g.ancestors(b) == {a, b}


def test_urg_rejects_untyped_nodes_and_edges():
    g = UnifiedReflectiveGraph()
    n = g.add_node("Evidence", {})
    with pytest.raises(URGError):
        g.add_node("Vibes", {})
    with pytest.raises(URGError):
        g.add_edge(n, n, "kind_of_relates_to")


def test_urg_round_trips_through_json():
    g = UnifiedReflectiveGraph()
    o = g.add_node("Observation", {"v": 1})
    e = g.add_node("Evidence", {"v": 2})
    g.add_edge(o, e, "provenance")
    back = UnifiedReflectiveGraph.from_dict(g.to_dict())
    assert len(back) == 2 and back.ancestors(e) == {o}


def test_contradiction_is_preserved_not_overwritten():
    """Invariant V: a contradicting write must not erase the supporting one."""
    g = UnifiedReflectiveGraph()
    h = g.add_node("Hypothesis", {"text": "I understand recursion"})
    e1 = g.add_node("Evidence", {"v": "passed the exercise"})
    e2 = g.add_node("Evidence", {"v": "failed the next one"})
    g.add_edge(e1, h, "supports")
    g.add_edge(e2, h, "contradicts")
    contested = g.contested_hypotheses()
    assert len(contested) == 1
    hid, sup, con = contested[0]
    assert hid == h and sup == [e1] and con == [e2]


# ---------------------------------------------------------------------------
# D-20 -- belief revision must be order-invariant
# ---------------------------------------------------------------------------

EXTREME = [(0.99, 0.01), (0.99, 0.01), (0.99, 0.01), (0.02, 0.98), (0.02, 0.98)]


def _run(order, liks=EXTREME):
    eng = BeliefRevisionEngine()
    for i in order:
        lt, lf = liks[i]
        eng.update("H", f"e{i}", lt, lf)
    return eng.belief("H")


def test_d20_belief_is_invariant_under_every_permutation():
    """The prototype gave 0.0396 / 0.9900 / 0.9900 for these five observations in
    three different orders -- a 95-point swing from ordering alone, caused by
    clamping the posterior inside the state."""
    results = [_run(list(p)) for p in itertools.permutations(range(5))]
    assert max(results) - min(results) < 1e-12


def test_d20_extreme_evidence_does_not_saturate_the_state():
    eng = BeliefRevisionEngine()
    for i in range(20):
        eng.update("H", f"e{i}", 0.99, 0.01)
    saturated = eng.belief("H")
    assert saturated > 0.999
    # ...and it is still recoverable: state was never clamped.
    for i in range(20):
        eng.update("H", f"f{i}", 0.01, 0.99)
    assert eng.belief("H") == pytest.approx(0.5, abs=1e-9)


def test_d20_display_is_clamped_but_state_is_not():
    eng = BeliefRevisionEngine()
    for i in range(50):
        eng.update("H", f"e{i}", 0.99, 0.01)
    led = eng.ledger("H")
    assert led.display_probability() <= 0.999
    assert led.probability() > led.display_probability() - 1e-9


def test_d20_re_applying_the_same_evidence_does_not_double_count():
    eng = BeliefRevisionEngine()
    eng.update("H", "e1", 0.9, 0.2)
    once = eng.belief("H")
    eng.update("H", "e1", 0.9, 0.2)
    assert eng.belief("H") == pytest.approx(once, abs=1e-12)


def test_d20_retraction_is_exact():
    eng = BeliefRevisionEngine()
    eng.update("H", "e1", 0.9, 0.2)
    before = eng.belief("H")
    eng.update("H", "e2", 0.1, 0.8)
    eng.retract("H", "e2")
    assert eng.belief("H") == pytest.approx(before, abs=1e-12)


def test_revision_history_records_every_transition():
    """Invariant III."""
    eng = BeliefRevisionEngine()
    for i in range(5):
        eng.update("H", f"e{i}", 0.7, 0.4)
    hist = eng.revision_history("H")
    assert len(hist) == 5
    assert all(r.prior != r.posterior for r in hist)


def test_unreliable_evidence_moves_belief_less():
    strong = BeliefRevisionEngine(); strong.update("H", "e", 0.9, 0.1, reliability=1.0)
    weak = BeliefRevisionEngine(); weak.update("H", "e", 0.9, 0.1, reliability=0.2)
    assert abs(strong.belief("H") - 0.5) > abs(weak.belief("H") - 0.5)


# ---------------------------------------------------------------------------
# D-22 -- the planner must compute information gain
# ---------------------------------------------------------------------------

def test_d22_planner_prefers_the_discriminating_observation():
    posterior = {"H1": 0.5, "H2": 0.5}
    useless = CandidateObservation("a test both hypotheses predict", {"H1": 0.8, "H2": 0.8})
    useful = CandidateObservation("a test that separates them", {"H1": 0.95, "H2": 0.05})
    assert (expected_information_gain(posterior, useful)
            > expected_information_gain(posterior, useless))
    plans = InquiryPlanner().plan(posterior, [useless, useful], top_k=1)
    assert plans and "separates" in plans[0].description


def test_d22_planner_is_not_silent_when_hypotheses_are_separated():
    """The prototype emitted nothing once the belief gap exceeded 0.2 -- regret
    1.000 against the oracle -- which is backwards: a confidently-held wrong
    hypothesis is when a discriminating observation is worth most."""
    posterior = {"H1": 0.9, "H2": 0.1}
    cand = CandidateObservation("decisive test", {"H1": 0.95, "H2": 0.05})
    assert InquiryPlanner().plan(posterior, [cand])


def test_d22_beats_random_selection_against_an_oracle():
    rng = random.Random(7)
    planner_regret, random_regret = [], []
    for _ in range(300):
        prior = {"H1": 0.52, "H2": 0.48}
        cands = [CandidateObservation(f"t{i}",
                                      {"H1": rng.uniform(0.05, 0.95),
                                       "H2": rng.uniform(0.05, 0.95)})
                 for i in range(4)]
        gains = [expected_information_gain(prior, c) for c in cands]
        best = max(gains)
        if best <= 1e-9:
            continue
        chosen = InquiryPlanner().plan(prior, cands, top_k=1)
        planner_regret.append((best - chosen[0].expected_information_gain) / best)
        random_regret.append((best - gains[rng.randrange(4)]) / best)
    assert sum(planner_regret) / len(planner_regret) < 1e-9      # it picks the oracle's choice
    assert sum(random_regret) / len(random_regret) > 0.3


def test_d22_gain_is_zero_when_the_observation_cannot_discriminate():
    posterior = {"H1": 0.5, "H2": 0.5}
    c = CandidateObservation("same under both", {"H1": 0.6, "H2": 0.6})
    assert expected_information_gain(posterior, c) == pytest.approx(0.0, abs=1e-9)


def test_d22_inquiry_states_what_it_would_resolve():
    """Invariant VIII: an inquiry must justify itself."""
    plans = InquiryPlanner().plan({"H1": 0.5, "H2": 0.5},
                                  [CandidateObservation("x", {"H1": 0.9, "H2": 0.1})])
    d = plans[0].to_dict()
    assert d["expected_information_gain_bits"] > 0
    assert d["targets"] and d["motivation"]


def test_d22_planner_writes_justified_inquiries_into_the_urg():
    g = UnifiedReflectiveGraph()
    h1 = g.add_node("Hypothesis", {"text": "A"})
    h2 = g.add_node("Hypothesis", {"text": "B"})
    plans = InquiryPlanner(g).plan({h1: 0.5, h2: 0.5},
                                   [CandidateObservation("x", {h1: 0.9, h2: 0.1})])
    nid = plans[0].inquiry_id
    assert g.node(nid)["node_type"] == "Inquiry"
    assert set(g.successors(nid, "targets")) == {h1, h2}


# ---------------------------------------------------------------------------
# D-13 -- the tension detector must fire on the case written to demonstrate it
# ---------------------------------------------------------------------------

def test_d13_flagship_scenario_now_registers_a_tension():
    """K = 0.30, W = 0.75, E = 0.80: working hard, distressed, not getting results.
    The prototype printed 'No significant tension detected' for exactly this."""
    p = EWKProfile()
    for _ in range(3):
        p.observe_many([("knowledge", 0.30), ("will", 0.75), ("emotion", 0.80)])
    reading = p.read()
    assert reading.status == "ok"
    assert reading.tensions
    names = {t.name for t in reading.tensions}
    assert "effort_without_return" in names
    assert "distress_without_return" in names


def test_d13_aligned_streams_produce_no_tension():
    p = EWKProfile()
    for _ in range(3):
        p.observe_many([("knowledge", 0.80), ("will", 0.75), ("emotion", 0.20)])
    assert p.read().tensions == []


def test_d13_refuses_below_minimum_evidence_per_stream():
    p = EWKProfile()
    p.observe_many([("knowledge", 0.3), ("will", 0.8), ("emotion", 0.9)])
    assert p.read().status == "insufficient_evidence"


def test_d13_every_tension_is_phrased_as_a_question():
    p = EWKProfile()
    for _ in range(3):
        p.observe_many([("knowledge", 0.20), ("will", 0.85), ("emotion", 0.90)])
    for t in p.read().tensions:
        assert t.question.rstrip().endswith("?")


# ---------------------------------------------------------------------------
# D-24 -- partial coverage raises a caution without asserting the hypothesis
# ---------------------------------------------------------------------------

def test_d24_partial_coverage_cautions_without_labelling():
    m = ShadowMirror(half_life_days=0.0)
    for _ in range(3):
        m.add("desire", "self_report", 0.20)
        m.add("desire", "behavior", 0.78)
        m.add("desire", "physiological", 0.80)      # no avoidance channel
    b = m.current()
    assert b.guard_coverage == "arousal_only"
    assert b.top_desire() != "threat_response"      # the label no longer overclaims
    assert b.top_desire() == "unresolved_approach"
    assert b.threat_confound_score is not None      # ...but the caution is computed
    assert "insufficient_confound_coverage" in m.safety().flags


def test_d24_full_coverage_still_asserts_threat():
    m = ShadowMirror(half_life_days=0.0)
    for _ in range(3):
        m.add("desire", "self_report", 0.20)
        m.add("desire", "behavior", 0.15)
        m.add("desire", "physiological", 0.90)
        m.add("desire", "avoidance", 0.88)
    assert m.current().top_desire() == "threat_response"
    assert "threat_response" in m.safety().flags


# ---------------------------------------------------------------------------
# D-15 / D-16 -- one timestamp convention, no deprecated calls
# ---------------------------------------------------------------------------

def test_d15_urg_timestamps_are_timezone_aware():
    from datetime import datetime
    g = UnifiedReflectiveGraph()
    n = g.add_node("Evidence", {})
    ts = datetime.fromisoformat(g.node(n)["created"])
    assert ts.tzinfo is not None


def test_d16_no_third_party_graph_dependency():
    import shadow_mirror.urg as urg_mod
    src = open(urg_mod.__file__).read()
    assert "networkx" not in src


# ---------------------------------------------------------------------------
# D-29 -- ambivalence must mean alternation, not spread
# ---------------------------------------------------------------------------

def _desire_series(stated, action):
    m = ShadowMirror(half_life_days=0.0)
    for s, a in zip(stated, action):
        m.add("desire", "self_report", s, "t")
        m.add("desire", "behavior", a, "t")
    return m.current("t")


def test_d29_alternating_streams_read_as_ambivalence():
    osc = [0.85, 0.15, 0.85, 0.15, 0.85, 0.15]
    b = _desire_series(osc, osc)
    assert b.top_desire() == "ambivalence"


def test_d29_monotonic_drift_is_not_ambivalence():
    """Someone who changed their mind across the window has resolved it, not held
    two positions at once. Dispersion cannot tell the two apart; before the fix
    98.8% of drift episodes were reported as ambivalence."""
    drift = [0.15, 0.29, 0.43, 0.57, 0.71, 0.85]
    b = _desire_series(drift, drift)
    assert b.desire["ambivalence"] < 0.10
    assert b.top_desire() != "ambivalence"


def test_d29_unstructured_noise_is_not_ambivalence():
    """Same dispersion as the oscillating case, no temporal structure."""
    noisy_s = [0.20, 0.75, 0.55, 0.45, 0.62, 0.38]
    noisy_a = [0.65, 0.35, 0.52, 0.58, 0.41, 0.60]
    b = _desire_series(noisy_s, noisy_a)
    assert b.top_desire() != "ambivalence"


def test_d29_dispersion_alone_does_not_trigger_ambivalence():
    """The discriminating property, stated directly: two series with nearly equal
    spread must not both read as ambivalence."""
    import statistics
    osc = [0.85, 0.15, 0.85, 0.15, 0.85, 0.15]
    drift = [0.15, 0.29, 0.43, 0.57, 0.71, 0.85]
    assert abs(statistics.pstdev(osc) - statistics.pstdev(drift)) < 0.12
    assert _desire_series(osc, osc).top_desire() == "ambivalence"
    assert _desire_series(drift, drift).top_desire() != "ambivalence"
