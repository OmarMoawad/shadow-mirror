"""Tests for the inference engine.

These check the *shape* commitments, not calibrated truths: sufficiency gating,
that each corner of evidence pulls the posterior toward the right hypothesis,
and that uncertainty behaves honestly.
"""

import math

from shadow_mirror import ShadowMirror


def test_refuses_to_infer_without_enough_evidence():
    m = ShadowMirror()
    m.add("knowledge", "self_report", 0.9)
    # Only one axis-half present, below MIN_EVIDENCE pairing -> no belief.
    assert m.current() is None
    assert m.report()["status"] == "insufficient_evidence"


def test_posterior_is_a_normalised_distribution():
    m = ShadowMirror()
    m.add_batch([
        ("knowledge", "self_report", 0.8),
        ("knowledge", "task_performance", 0.8),
        ("knowledge", "self_report", 0.75),
        ("knowledge", "task_performance", 0.82),
    ])
    b = m.current()
    assert b is not None
    assert math.isclose(sum(b.knowledge.values()), 1.0, abs_tol=1e-6)
    assert all(0.0 <= v <= 1.0 for v in b.knowledge.values())


def test_overconfidence_reads_as_blind_spot():
    # High stated confidence, low measured performance -> blind spot.
    m = ShadowMirror()
    m.add_batch([
        ("knowledge", "self_report", 0.9),
        ("knowledge", "task_performance", 0.2),
        ("knowledge", "self_report", 0.88),
        ("knowledge", "task_performance", 0.25),
    ])
    assert m.current().top_knowledge() == "blind_spot"


def test_underconfidence_reads_as_latent_knowledge():
    # Low stated confidence, high measured performance -> latent knowledge.
    m = ShadowMirror()
    m.add_batch([
        ("knowledge", "self_report", 0.2),
        ("knowledge", "task_performance", 0.85),
        ("knowledge", "self_report", 0.25),
        ("knowledge", "task_performance", 0.9),
    ])
    assert m.current().top_knowledge() == "latent_knowledge"


def test_aligned_confidence_reads_as_explicit_knowledge():
    m = ShadowMirror()
    m.add_batch([
        ("knowledge", "self_report", 0.85),
        ("knowledge", "task_performance", 0.85),
        ("knowledge", "self_report", 0.9),
        ("knowledge", "task_performance", 0.88),
    ])
    assert m.current().top_knowledge() == "explicit_knowledge"


def test_desire_says_no_but_acts_yes_without_confounds_is_unresolved():
    """BEHAVIOUR CHANGE in v0.4 (defect D-19).

    In v0.3.0 this asserted ``latent_approach`` -- "you want this even though you
    say you don't" -- from stated aversion plus approach behaviour alone. Session 2
    measured what that costs: a guard-free mismatch reading misidentifies a threat
    response as a hidden desire in 42.9% [39.5, 46.2] of episodes, and 95% of
    compliance/fawn episodes.

    Approach under stated reluctance is exactly the pattern produced *both* by a
    hidden preference *and* by a threat response. Without the arousal and avoidance
    channels the two are not distinguishable, so v0.4 refuses the reading and says
    so, rather than picking the flattering one.
    """
    m = ShadowMirror()
    m.add_batch([
        ("desire", "self_report", 0.15),
        ("desire", "behavior", 0.85),
        ("desire", "self_report", 0.2),
        ("desire", "behavior", 0.8),
    ])
    assert m.current().top_desire() == "unresolved_approach"
    assert m.current().guard_coverage == "none"
    assert "insufficient_confound_coverage" in m.safety().flags


def test_latent_approach_is_still_assertable_with_full_coverage():
    """The capability is not removed -- it is conditioned on being able to rule
    out the threat explanation. Calm arousal + low avoidance does rule it out."""
    m = ShadowMirror()
    m.add_batch([
        ("desire", "self_report", 0.15),
        ("desire", "behavior", 0.85),
        ("desire", "physiological", 0.20),
        ("desire", "avoidance", 0.15),
        ("desire", "self_report", 0.2),
        ("desire", "behavior", 0.8),
        ("desire", "physiological", 0.25),
        ("desire", "avoidance", 0.20),
    ])
    b = m.current()
    assert b.guard_coverage == "full"
    assert b.top_desire() == "latent_approach"


def test_conflicting_signals_raise_uncertainty():
    calm = ShadowMirror()
    calm.add_batch([
        ("knowledge", "self_report", 0.8),
        ("knowledge", "task_performance", 0.8),
        ("knowledge", "self_report", 0.81),
        ("knowledge", "task_performance", 0.79),
    ])
    noisy = ShadowMirror()
    noisy.add_batch([
        ("knowledge", "self_report", 0.1),
        ("knowledge", "task_performance", 0.9),
        ("knowledge", "self_report", 0.9),
        ("knowledge", "task_performance", 0.1),
    ])
    assert noisy.current().uncertainty > calm.current().uncertainty
