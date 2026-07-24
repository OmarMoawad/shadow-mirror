"""Tests for the reflection layer and local persistence."""

from shadow_mirror import ShadowMirror, reflective_prompts
from shadow_mirror.store import Store


def test_reflection_is_questions_not_verdicts():
    m = ShadowMirror()
    m.add_batch([
        ("knowledge", "self_report", 0.9),
        ("knowledge", "task_performance", 0.2),
        ("knowledge", "self_report", 0.88),
        ("knowledge", "task_performance", 0.25),
    ])
    prompts = reflective_prompts(m)
    assert prompts
    joined = " ".join(prompts).lower()
    # It must never assert identity...
    assert "you are" not in joined
    # ...and it must invite reflection.
    assert "?" in joined


def test_threat_prompt_comes_first_and_is_non_desire():
    m = ShadowMirror()
    m.add_batch([
        ("desire", "self_report", 0.2),
        ("desire", "behavior", 0.15),
        ("desire", "physiological", 0.9),
        ("desire", "avoidance", 0.9),
        ("desire", "self_report", 0.2),
        ("desire", "behavior", 0.2),
        ("desire", "physiological", 0.9),
        ("desire", "avoidance", 0.9),
    ])
    first = reflective_prompts(m)[0].lower()
    assert "unsafe" in first or "threat" in first


def test_store_roundtrip_preserves_observations(tmp_path):
    path = tmp_path / "journal.json"
    store = Store(path)
    store.record_consent()
    m = ShadowMirror()
    m.add("knowledge", "self_report", 0.7, context="algebra")
    m.add("knowledge", "task_performance", 0.4, context="algebra quiz")
    store.save(m)

    reloaded = store.load()
    assert len(reloaded.observations) == 2
    assert reloaded.observations[0].context == "algebra"
    assert store.has_consent()


def test_forget_deletes_everything(tmp_path):
    path = tmp_path / "journal.json"
    store = Store(path)
    store.record_consent()
    assert store.exists()
    store.forget()
    assert not store.exists()
    assert not store.has_consent()
