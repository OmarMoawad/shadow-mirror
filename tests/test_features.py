"""Tests for the features embedded from the parallel research prototype:
topic scoping, reliability + temporal decay weighting, and the ambivalence state.
"""

from datetime import datetime, timedelta, timezone

from shadow_mirror import ShadowMirror


def test_topics_do_not_blend():
    # Confident-and-correct in algebra; overconfident in public speaking.
    m = ShadowMirror()
    m.add_batch([
        ("knowledge", "self_report", 0.85, "algebra"),
        ("knowledge", "task_performance", 0.85, "algebra"),
        ("knowledge", "self_report", 0.9, "algebra"),
        ("knowledge", "task_performance", 0.88, "algebra"),
        ("knowledge", "self_report", 0.9, "public_speaking"),
        ("knowledge", "task_performance", 0.2, "public_speaking"),
        ("knowledge", "self_report", 0.88, "public_speaking"),
        ("knowledge", "task_performance", 0.25, "public_speaking"),
    ])
    assert m.current("algebra").top_knowledge() == "explicit_knowledge"
    assert m.current("public_speaking").top_knowledge() == "blind_spot"
    # ...and the topics are enumerable.
    assert set(m.topics()) == {"algebra", "public_speaking"}


def test_oscillating_desire_reads_as_ambivalence():
    # Stated want swings hard over time, and so does behaviour: wants and
    # doesn't want at once. Should surface ambivalence, not a forced direction.
    m = ShadowMirror()
    m.add_batch([
        ("desire", "self_report", 0.9, "moving_abroad"),
        ("desire", "behavior", 0.85, "moving_abroad"),
        ("desire", "self_report", 0.1, "moving_abroad"),
        ("desire", "behavior", 0.15, "moving_abroad"),
        ("desire", "self_report", 0.85, "moving_abroad"),
        ("desire", "behavior", 0.8, "moving_abroad"),
        ("desire", "self_report", 0.15, "moving_abroad"),
        ("desire", "behavior", 0.2, "moving_abroad"),
    ])
    b = m.current("moving_abroad")
    assert b.desire["ambivalence"] > 0.25
    assert b.top_desire() == "ambivalence"


def test_reliability_downweights_untrusted_evidence():
    # A rigorous performance score (reliability 1.0) vs. a casually-guessed high
    # self-report (reliability 0.1) should still read as a blind spot, because the
    # trustworthy signal (low performance) dominates.
    m = ShadowMirror()
    m.add_batch([
        ("knowledge", "self_report", 0.95, "chess", "", 0.1),
        ("knowledge", "task_performance", 0.25, "chess", "", 1.0),
        ("knowledge", "self_report", 0.95, "chess", "", 0.1),
        ("knowledge", "task_performance", 0.2, "chess", "", 1.0),
    ])
    # Low-reliability high confidence is discounted; the reading should not be
    # "explicit_knowledge".
    assert m.current("chess").top_knowledge() in ("blind_spot", "explicit_uncertainty")


def test_temporal_decay_favors_recent_evidence():
    # Old evidence said "blind spot"; recent evidence says "calibrated". With a
    # short half-life, the recent picture should win.
    m = ShadowMirror(half_life_days=7.0)
    old = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
    new = datetime.now(timezone.utc).isoformat()
    from shadow_mirror.models import Observation
    for ts, conf, perf in [(old, 0.95, 0.2), (old, 0.95, 0.2),
                           (new, 0.85, 0.85), (new, 0.88, 0.86)]:
        m.observations.append(Observation("knowledge", "self_report", conf,
                                           topic="t", timestamp=ts))
        m.observations.append(Observation("knowledge", "task_performance", perf,
                                           topic="t", timestamp=ts))
    assert m.current("t").top_knowledge() == "explicit_knowledge"
