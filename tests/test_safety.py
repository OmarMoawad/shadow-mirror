"""Tests for the safety layer -- the commitments that make this defensible.

The most important one: arousal + avoidance must NOT be read as a hidden want.
"""

from shadow_mirror import ShadowMirror


def _threat_scenario() -> ShadowMirror:
    # Says no, acts away, but with high arousal and high avoidance: the exact
    # trauma-trigger pattern the synthesis warned must never become "want".
    m = ShadowMirror()
    m.add_batch([
        ("desire", "self_report", 0.2),
        ("desire", "behavior", 0.15),
        ("desire", "physiological", 0.9),
        ("desire", "avoidance", 0.9),
        ("desire", "self_report", 0.25),
        ("desire", "behavior", 0.2),
        ("desire", "physiological", 0.85),
        ("desire", "avoidance", 0.88),
    ])
    return m


def test_threat_response_is_flagged():
    m = _threat_scenario()
    assert m.current().threat_prob >= 0.45
    assert "threat_response" in m.safety().flags


def test_threat_suppresses_latent_approach_reading():
    # A near-identical approach pattern but WITHOUT arousal/avoidance would tend
    # toward latent_approach; with the threat signal it must not be labelled a want.
    threat = _threat_scenario()
    top = threat.current().top_desire()
    assert top != "latent_approach"


def test_low_evidence_suppresses_interpretation():
    m = ShadowMirror()
    m.add("desire", "self_report", 0.5)
    report = m.safety()
    assert report.suppress_interpretation
    assert "low_evidence" in report.flags


def test_reactivity_warns_after_repeated_use():
    m = ShadowMirror()
    # Each add() produces a new belief snapshot once inference is active.
    for i in range(10):
        m.add("knowledge", "self_report", 0.6)
        m.add("knowledge", "task_performance", 0.6)
    assert "reactivity" in m.safety().flags
