"""Regression tests locking each v0.4 fix.

Every test in this file FAILS on v0.3.0 and PASSES on v0.4. They are written
against the defect, not against the implementation, so a future refactor that
reintroduces the defect will break the test.

Defect IDs refer to the Session 1 and Session 2 audit registers.
"""

from datetime import datetime, timedelta, timezone

import pytest

from shadow_mirror import ShadowMirror
from shadow_mirror.models import Observation


FIXED_NOW = datetime(2026, 7, 25, 12, 0, 0, tzinfo=timezone.utc)


def frozen(**kw) -> ShadowMirror:
    return ShadowMirror(clock=lambda: FIXED_NOW, **kw)


def _at(m: ShadowMirror, days_ago: float, axis, sig, value, topic="t", rel=1.0):
    ts = (FIXED_NOW - timedelta(days=days_ago)).isoformat()
    m.observations.append(Observation(axis, sig, value, topic=topic,
                                      reliability=rel, timestamp=ts))


# ---------------------------------------------------------------------------
# D-21 -- injectable clock, so inference is reproducible and testable
# ---------------------------------------------------------------------------

def test_d21_clock_is_injectable_and_inference_is_deterministic():
    def build():
        m = frozen()
        for _ in range(4):
            _at(m, 1.0, "knowledge", "self_report", 0.9)
            _at(m, 1.0, "knowledge", "task_performance", 0.2)
        return m.current("t")

    a, b = build(), build()
    assert a.knowledge == b.knowledge
    assert a.uncertainty == b.uncertainty


# ---------------------------------------------------------------------------
# D-08 -- the posterior must sharpen as evidence accumulates
# ---------------------------------------------------------------------------

def test_d08_posterior_sharpens_with_more_evidence():
    """v0.3.0 evaluated one likelihood at the weighted centroid, so the posterior
    was bit-identical at n = 2 and n = 100. It must now respond to evidence."""
    def confidence(n_pairs):
        m = frozen()
        for _ in range(n_pairs):
            _at(m, 0.0, "knowledge", "self_report", 0.9)
            _at(m, 0.0, "knowledge", "task_performance", 0.2)
        post = m.current("t").knowledge
        return post["blind_spot"]

    c2, c4, c8 = confidence(2), confidence(4), confidence(8)
    assert c2 < c4 < c8, (c2, c4, c8)
    assert c8 - c2 > 0.05


def test_d08_uncertainty_falls_as_evidence_accumulates():
    def unc(n_pairs):
        m = frozen()
        for _ in range(n_pairs):
            _at(m, 0.0, "knowledge", "self_report", 0.9)
            _at(m, 0.0, "knowledge", "task_performance", 0.2)
        return m.current("t").uncertainty

    assert unc(8) < unc(2)


def test_d08_evidence_far_from_every_hypothesis_is_reported_as_unmodelled():
    """The fix for 'confident exactly when wrong': an explicit none-of-these
    component, so misspecified evidence does not collapse onto the nearest corner."""
    m = frozen()
    for _ in range(6):
        _at(m, 0.0, "knowledge", "self_report", 0.5)
        _at(m, 0.0, "knowledge", "task_performance", 0.5)
    post = m.current("t").knowledge
    assert post["unmodelled"] > 0.5
    assert m.current("t").top_knowledge() == "unmodelled"


# ---------------------------------------------------------------------------
# D-09 -- one number, one name
# ---------------------------------------------------------------------------

def test_d09_threat_score_and_threat_posterior_are_separately_named():
    m = frozen()
    for _ in range(3):
        _at(m, 0.0, "desire", "self_report", 0.2)
        _at(m, 0.0, "desire", "behavior", 0.15)
        _at(m, 0.0, "desire", "physiological", 0.9)
        _at(m, 0.0, "desire", "avoidance", 0.9)
    r = m.report("t")["desire"]
    assert "threat_confound_score" in r
    assert "p_threat_response" in r
    assert "threat_response_probability" not in r    # the ambiguous v0.3.0 label
    # They are genuinely different quantities and are allowed to differ.
    assert r["threat_confound_score"] is not None


def test_d09_confound_score_is_none_when_it_cannot_be_computed():
    m = frozen()
    for _ in range(3):
        _at(m, 0.0, "desire", "self_report", 0.2)
        _at(m, 0.0, "desire", "behavior", 0.8)
    assert m.current("t").threat_confound_score is None
    assert m.report("t")["desire"]["threat_confound_score"] is None


# ---------------------------------------------------------------------------
# D-11 -- topic scoping must not leak through the history
# ---------------------------------------------------------------------------

def test_d11_interleaving_topics_does_not_create_instability():
    """Alternating between two internally stable topics reported spurious
    instability in v0.3.0, because one global history mixed them: the metric was
    measuring topic-switching, not belief movement.

    The test compares like with like -- identical per-topic evidence, logged
    interleaved versus logged in blocks. Instability for a topic must not depend
    on what else was being logged in between.
    """
    interleaved = frozen()
    for _ in range(4):
        interleaved.add("knowledge", "self_report", 0.9, "algebra")
        interleaved.add("knowledge", "task_performance", 0.9, "algebra")
        interleaved.add("knowledge", "self_report", 0.1, "speaking")
        interleaved.add("knowledge", "task_performance", 0.1, "speaking")

    blocked = frozen()
    for _ in range(4):
        blocked.add("knowledge", "self_report", 0.9, "algebra")
        blocked.add("knowledge", "task_performance", 0.9, "algebra")
    for _ in range(4):
        blocked.add("knowledge", "self_report", 0.1, "speaking")
        blocked.add("knowledge", "task_performance", 0.1, "speaking")

    assert interleaved._instability("algebra") == pytest.approx(
        blocked._instability("algebra"), abs=1e-6)
    assert interleaved._instability("speaking") == pytest.approx(
        blocked._instability("speaking"), abs=1e-6)
    # ...and neither topic actually moved, so instability is near zero.
    assert interleaved._instability("algebra") < 0.05


def test_d11_history_is_keyed_by_topic():
    """v1.1 (D-28) note: snapshots are recorded when the mirror is *consulted*,
    not when an observation is written, so this test now consults each topic
    before inspecting the history. The property under test -- that history is
    keyed by topic rather than pooled into one global list -- is unchanged."""
    m = frozen()
    m.add_batch([
        ("knowledge", "self_report", 0.9, "a"),
        ("knowledge", "task_performance", 0.9, "a"),
        ("knowledge", "self_report", 0.9, "a"),
        ("knowledge", "task_performance", 0.9, "a"),
        ("knowledge", "self_report", 0.1, "b"),
        ("knowledge", "task_performance", 0.1, "b"),
        ("knowledge", "self_report", 0.1, "b"),
        ("knowledge", "task_performance", 0.1, "b"),
    ])
    m.current("a")
    m.current("b")
    assert set(m.belief_history) == {"a", "b"}
    assert all(len(v) > 0 for v in m.belief_history.values())


# ---------------------------------------------------------------------------
# D-12 -- decay must reach the sufficiency gate, not only the means
# ---------------------------------------------------------------------------

def test_d12_decayed_evidence_no_longer_passes_the_sufficiency_gate():
    """v0.3.0 inferred confidently from decade-old observations in 100% of trials
    because the gate counted raw observations while decay only touched the means."""
    m = frozen(half_life_days=30.0)
    for _ in range(4):
        _at(m, 3650.0, "knowledge", "self_report", 0.9)
        _at(m, 3650.0, "knowledge", "task_performance", 0.2)
    assert m.evidence_pairs("t") == (0, 0)
    assert m.report("t")["status"] == "insufficient_evidence"


def test_d12_fresh_evidence_still_passes():
    m = frozen(half_life_days=30.0)
    for _ in range(4):
        _at(m, 1.0, "knowledge", "self_report", 0.9)
        _at(m, 1.0, "knowledge", "task_performance", 0.2)
    assert m.report("t")["status"] == "ok"


def test_d12_dispersion_is_weighted():
    """A stale outlier must not inflate dispersion the way it did in v0.3.0,
    where the mean was weighted but the spread was not."""
    fresh_only = frozen(half_life_days=7.0)
    with_stale_outlier = frozen(half_life_days=7.0)
    for m in (fresh_only, with_stale_outlier):
        for _ in range(4):
            _at(m, 0.0, "knowledge", "self_report", 0.85)
            _at(m, 0.0, "knowledge", "task_performance", 0.85)
    for _ in range(2):
        _at(with_stale_outlier, 200.0, "knowledge", "self_report", 0.05)
        _at(with_stale_outlier, 200.0, "knowledge", "task_performance", 0.05)
    a = fresh_only.current("t").uncertainty
    b = with_stale_outlier.current("t").uncertainty
    assert abs(a - b) < 0.02


# ---------------------------------------------------------------------------
# D-19 -- the guard refuses instead of silently degrading  (CRITICAL)
# ---------------------------------------------------------------------------

def _threat_rows(m, arousal=True, avoidance=True, action=0.15):
    for _ in range(3):
        _at(m, 0.0, "desire", "self_report", 0.2)
        _at(m, 0.0, "desire", "behavior", action)
        if arousal:
            _at(m, 0.0, "desire", "physiological", 0.88)
        if avoidance:
            _at(m, 0.0, "desire", "avoidance", 0.85)


def test_d19_full_coverage_flags_threat():
    m = frozen()
    _threat_rows(m)
    b = m.current("t")
    assert b.guard_coverage == "full"
    assert b.threat_confound_score >= 0.45
    assert "threat_response" in m.safety("t").flags
    assert b.top_desire() != "latent_approach"


def test_d19_missing_avoidance_does_not_silently_disable_the_guard():
    """The Session 2 ablation: with avoidance unobserved, v0.3.0's guard
    sensitivity fell from 100% to 0.0% and it misread 62.5% of compliance-type
    threat episodes as hidden desire, because a missing channel was imputed as
    zero -- i.e. as positive evidence of safety."""
    m = frozen()
    _threat_rows(m, avoidance=False, action=0.65)     # compliance / fawn pattern
    b = m.current("t")
    assert b.guard_coverage == "arousal_only"
    assert b.top_desire() != "latent_approach"
    assert "insufficient_confound_coverage" in m.safety("t").flags


def test_d19_no_confound_channels_cannot_assert_a_hidden_want():
    m = frozen()
    _threat_rows(m, arousal=False, avoidance=False, action=0.85)
    b = m.current("t")
    assert b.guard_coverage == "none"
    assert b.desire["latent_approach"] == 0.0
    assert b.top_desire() == "unresolved_approach"


def test_d19_missing_channel_is_not_treated_as_a_zero_reading():
    """The precise mechanism: absent must not equal 0.0."""
    absent = frozen()
    _threat_rows(absent, avoidance=False, action=0.65)
    explicit_zero = frozen()
    _threat_rows(explicit_zero, avoidance=False, action=0.65)
    for _ in range(3):
        _at(explicit_zero, 0.0, "desire", "avoidance", 0.0)
    assert absent.current("t").guard_coverage == "arousal_only"
    assert explicit_zero.current("t").guard_coverage == "full"
    # An explicit "no avoidance observed" reading is a real datum and may lower
    # the score; an absent channel may not.
    assert absent.current("t").threat_confound_score is not None
    assert explicit_zero.current("t").threat_confound_score is not None
    assert absent.current("t").threat_confound_score > \
        explicit_zero.current("t").threat_confound_score


def test_d19_partial_coverage_raises_uncertainty():
    full = frozen()
    _threat_rows(full, action=0.65)
    partial = frozen()
    _threat_rows(partial, avoidance=False, action=0.65)
    assert partial.current("t").uncertainty > full.current("t").uncertainty
