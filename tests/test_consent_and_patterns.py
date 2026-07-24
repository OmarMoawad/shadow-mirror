"""Tests for the consented-subject study: the consent gate, the counter-pattern
engine, emotion-as-cause coupling, and -- most importantly -- that the trauma
guard survives into the new module.

These assert *commitments*, not plumbing:
  * no datum can be recorded without an active, per-stream consent grant;
  * a non-self-noticeable stream cannot be granted without its own explicit ack;
  * revoke wipes; lapsed consent is inactive;
  * a behaviour reversal with steady feeling is read as a *coupling* shift;
  * high arousal + avoidance late is flagged threat, not "changed preference".
"""

import pytest

from shadow_mirror import (
    ConsentGrant, ConsentError, Study, Encounter, analyze, reaction_state,
    NON_OBVIOUS_STREAMS,
)


def _grant(streams, purpose="research", ack_all=True):
    g = ConsentGrant(subject_id="subj", purpose=purpose)
    g.domains = {"reaction_patterns", "emotion_behavior"}
    for s in streams:
        g.add_stream(s, acknowledged_non_obvious=ack_all)
    return g


def _encs(rows, condition="disagreement"):
    """rows: list of (valence, arousal, action); timestamped in order."""
    out = []
    for i, (v, a, act) in enumerate(rows):
        out.append(Encounter(
            subject_id="subj", condition=condition, valence=v, arousal=a,
            action=act, timestamp=f"2026-01-{i+1:02d}T12:00:00+00:00",
        ))
    return out


# --- the consent gate -------------------------------------------------------
def test_observe_refused_without_granted_stream():
    study = Study(_grant(["self_report"]))
    # granted stream works
    study.observe("x", valence=0.5, action=0.5, stream="self_report")
    # ungranted stream is refused, loudly
    with pytest.raises(ConsentError):
        study.observe("x", valence=0.5, action=0.5, stream="physiological")


def test_non_obvious_stream_needs_explicit_ack():
    g = ConsentGrant(subject_id="subj", purpose="research")
    assert "physiological" in NON_OBVIOUS_STREAMS
    # bundling it under a plain add is refused
    with pytest.raises(ConsentError):
        g.add_stream("physiological")
    # only an explicit per-stream acknowledgement lets it in
    g.add_stream("physiological", acknowledged_non_obvious=True)
    assert "physiological" in g.streams


def test_self_noticeable_stream_needs_no_special_ack():
    g = ConsentGrant(subject_id="subj", purpose="research")
    g.add_stream("self_report")  # no ack flag needed
    assert "self_report" in g.streams


def test_revoke_wipes_and_blocks():
    study = Study(_grant(["self_report"]))
    study.observe("x", valence=0.5, action=0.5, stream="self_report")
    assert study.records()
    study.revoke(wipe=True)
    assert study.records() == []
    assert not study.grant.active
    with pytest.raises(ConsentError):
        study.observe("x", valence=0.5, action=0.5, stream="self_report")


def test_lapsed_grant_is_inactive():
    g = _grant(["self_report"])
    g.reaffirmed_at = "2020-01-01T00:00:00+00:00"
    g.review_days = 90
    assert g.lapsed is True
    assert g.active is False
    study = Study(g)
    with pytest.raises(ConsentError):
        study.observe("x", valence=0.5, action=0.5, stream="self_report")
    # re-affirming brings it back
    g.reaffirm()
    assert g.active is True


def test_domain_scoping():
    g = ConsentGrant(subject_id="subj", purpose="research")
    g.add_stream("self_report")
    g.domains = {"reaction_patterns"}  # not emotion_behavior
    study = Study(g)
    study.observe("x", 0.5, 0.5, domain="reaction_patterns")
    with pytest.raises(ConsentError):
        study.observe("x", 0.5, 0.5, domain="emotion_behavior")


# --- reaction-state mapping -------------------------------------------------
def test_reaction_state_corners():
    assert reaction_state(0.9, 0.9, 0.3) == "appetitive_approach"
    assert reaction_state(0.9, 0.1, 0.3) == "appetitive_inhibited"
    assert reaction_state(0.1, 0.1, 0.3) == "aversive_avoid"
    assert reaction_state(0.1, 0.9, 0.3) == "aversive_override"
    assert reaction_state(0.5, 0.5, 0.3) == "neutral"


def test_threat_overlay_preempts_state():
    # high arousal + feeling bad + moving away == a safety response, named as such
    assert reaction_state(0.2, 0.1, 0.9) == "threat_withdrawal"


# --- pattern gating ---------------------------------------------------------
def test_insufficient_evidence_refuses():
    reading = analyze(_encs([(0.5, 0.5, 0.5)]))
    assert reading.counter_pattern is False
    assert reading.coupling["status"] == "insufficient_evidence"
    assert reading.uncertainty == 1.0


# --- the interesting science: coupling vs emotion drivers -------------------
def test_behavior_reversal_with_steady_feeling_is_coupling_shift():
    # feeling stays mildly negative; behaviour flips avoid -> approach.
    reading = analyze(_encs([
        (0.30, 0.4, 0.15),
        (0.33, 0.4, 0.25),
        (0.31, 0.4, 0.75),
        (0.34, 0.4, 0.85),
    ]))
    assert reading.counter_pattern is True
    assert reading.kind == "behavior_reversal"
    assert reading.driver == "coupling_shift"
    assert reading.threat_flag is False


def test_emotion_reversal_drives_emotion_shift():
    # feeling flips negative -> positive while behaviour keeps withdrawing.
    reading = analyze(_encs([
        (0.20, 0.4, 0.20),
        (0.25, 0.4, 0.25),
        (0.75, 0.4, 0.30),
        (0.80, 0.4, 0.35),
    ]))
    assert reading.kind == "emotion_reversal"
    assert reading.driver == "emotion_shift"


def test_stable_reaction_is_not_a_counter_pattern():
    reading = analyze(_encs([
        (0.8, 0.3, 0.8),
        (0.82, 0.3, 0.78),
        (0.79, 0.3, 0.81),
        (0.81, 0.3, 0.79),
    ]))
    assert reading.counter_pattern is False
    assert reading.kind == "none"


# --- the trauma guard, carried into the pattern layer -----------------------
def test_late_arousal_avoidance_is_flagged_threat_not_preference():
    reading = analyze(_encs([
        (0.70, 0.40, 0.80),   # early: feels good, approaches
        (0.65, 0.45, 0.70),
        (0.30, 0.70, 0.20),   # late: feels bad, aroused, withdraws
        (0.25, 0.75, 0.15),
    ]))
    assert reading.threat_flag is True
    # the threat question must come FIRST, before any "reversed preference" read
    assert "safety response" in reading.questions[0]


def test_emotion_as_cause_coupling_sign():
    # better feeling tracks approaching => positive valence->action coupling
    reading = analyze(_encs([
        (0.2, 0.4, 0.2),
        (0.4, 0.4, 0.45),
        (0.6, 0.4, 0.6),
        (0.85, 0.4, 0.9),
    ]))
    assert reading.coupling["status"] == "ok"
    assert reading.coupling["valence_to_action"] > 0


# --- round-trip persistence -------------------------------------------------
def test_study_serialization_roundtrip():
    study = Study(_grant(["self_report", "physiological"]))
    study.observe("x", 0.6, 0.7, arousal=0.5, stream="physiological")
    restored = Study.from_dict(study.to_dict())
    assert restored.grant.subject_id == "subj"
    assert "physiological" in restored.grant.streams
    assert len(restored.records()) == 1
