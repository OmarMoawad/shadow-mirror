"""Regression tests for the v1.1 governance fixes.

D-31 (GDPR Art. 7(1), 7(3)) and D-32 (EU AI Act Art. 5(1)(f)) were both found by
the Session 9 regulatory audit as prohibitions with no mechanism behind them.
"""

import pytest

from shadow_mirror import (CONSENTED_INDIVIDUAL, ConsentLedger, DeploymentContext,
                           DeploymentRefusal, INSTITUTIONAL, SELF, UNDECLARED,
                           self_context)


# --------------------------------------------------------------------------
# D-32 -- deployment context gate
# --------------------------------------------------------------------------

def test_d32_institutional_context_refuses_the_biometric_stream():
    ctx = DeploymentContext(context=INSTITUTIONAL, declared_by="a university")
    with pytest.raises(DeploymentRefusal) as e:
        ctx.require("physiological")
    assert "5(1)(f)" in str(e.value)


def test_d32_undeclared_context_refuses_by_default():
    """Refusal is the safe default: an operator who has not said where this is
    running has not established that the prohibition does not apply."""
    assert not DeploymentContext().permits("physiological")
    assert DeploymentContext().context == UNDECLARED


def test_d32_self_and_consented_individual_contexts_permit_it():
    assert self_context().permits("physiological")
    assert DeploymentContext(context=CONSENTED_INDIVIDUAL).permits("physiological")


def test_d32_non_biometric_streams_are_never_gated():
    ctx = DeploymentContext(context=INSTITUTIONAL)
    for s in ("self_report", "behavior", "task_performance", "avoidance"):
        ctx.require(s)          # must not raise


def test_d32_safety_exception_requires_a_written_basis():
    """A boolean could be set by accident; a sentence has to be written."""
    assert not DeploymentContext(context=INSTITUTIONAL,
                                 safety_exception_basis="   ").permits("physiological")
    claimed = DeploymentContext(
        context=INSTITUTIONAL,
        safety_exception_basis="Used solely as a threat confound; see Session 2 ablation.")
    assert claimed.permits("physiological")
    assert claimed.to_dict()["safety_exception_claimed"] is True
    assert "not legal advice" in claimed.to_dict()["regulatory_note"]


def test_d32_unknown_context_is_rejected():
    with pytest.raises(ValueError):
        DeploymentContext(context="probably_fine")


# --------------------------------------------------------------------------
# D-31 -- append-only consent ledger (Art. 7(1)) and withdrawal receipt (7(3))
# --------------------------------------------------------------------------

def _history():
    led = ConsentLedger()
    led.record("granted", "alex", streams=["self_report"], purpose="our friction")
    led.record("stream_added", "alex", stream="physiological")
    led.record("revoked", "alex", reason="changed my mind")
    led.record("erased", "alex", n_records=42)
    return led


def test_d31_ledger_demonstrates_consent_at_a_past_instant():
    """Art. 7(1): the controller must be able to demonstrate consent was given.
    A mutable grant object cannot answer 'what was true last March'."""
    led = _history()
    evs = led.events("alex")
    after_add = evs[1].timestamp
    assert set(led.streams_granted_at("alex", after_add)) == {"self_report", "physiological"}
    assert led.streams_granted_at("alex", evs[2].timestamp) == []


def test_d31_ledger_is_append_only_and_hash_chained():
    led = _history()
    assert led.verify()
    assert [e.seq for e in led.events()] == [0, 1, 2, 3]


def test_d31_tampering_is_detectable():
    led = _history()
    object.__setattr__(led._events[1], "detail", {"stream": "self_report"})
    assert not led.verify()


def test_d31_erasure_retains_the_record_not_the_data():
    led = _history()
    r = led.withdrawal_receipt("alex")
    assert r["withdrawn"] is True
    assert r["records_erased"] == 42
    assert r["ledger_entries_retained"] == 4
    assert r["chain_verifies"] is True


def test_d31_withdrawal_receipt_names_what_had_been_granted():
    """Art. 7(3) parity: granting ends with a summary, so withdrawal must end
    with something equally concrete."""
    r = _history().withdrawal_receipt("alex")
    assert set(r["streams_that_had_been_granted"]) == {"self_report", "physiological"}
    assert r["withdrawn_at"]
    assert "erased" in r["note"]


def test_d31_unknown_event_types_are_rejected():
    with pytest.raises(ValueError):
        ConsentLedger().record("vibes", "alex")
