"""Session 15 — the formation model, and the four things it refuses to say.

The negative tests are the point of this file. A refusal that is not tested is a
refusal that will be removed by a well-meaning refactor.
"""

import pytest

from shadow_mirror.deployment import (
    DeploymentContext, SELF, CONSENTED_INDIVIDUAL, INSTITUTIONAL, UNDECLARED,
)
from shadow_mirror.formation import (
    FormationModel, FormationRefusal, REGISTRY, REFUSAL_GROUNDS,
    PSYCHOMETRIC_STREAM, LICENCE_CONFIRMED_FREE,
)
from shadow_mirror.invariants import check_xi_declared_only
from shadow_mirror.ledger import ConsentLedger


# ---------------------------------------------------------------------------
# The four refusals that answer the original request
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method,ground", [
    ("infer_background", "INFERRED_ORIGIN"),
    ("infer_origin", "INFERRED_ORIGIN"),
    ("maturity_level", "GLOBAL_RANKING"),
    ("overall_maturity", "GLOBAL_RANKING"),
    ("developmental_stage", "GLOBAL_RANKING"),
    ("what_they_still_need", "PRESCRIPTIVE_DEFICIT"),
    ("deficits", "PRESCRIPTIVE_DEFICIT"),
    ("eventual_purpose", "PURPOSE_ATTRIBUTION"),
    ("life_purpose", "PURPOSE_ATTRIBUTION"),
])
def test_the_four_asks_are_refused_by_name(method, ground):
    """Each refusal names its ground and explains itself to the person."""
    m = FormationModel("p")
    with pytest.raises(FormationRefusal) as exc:
        getattr(m, method)()
    assert exc.value.ground == ground
    assert len(REFUSAL_GROUNDS[ground]) > 100, "a refusal must explain, not just decline"


def test_refusal_methods_exist_rather_than_being_absent():
    """Absence is not refusal. A missing attribute teaches the caller nothing."""
    m = FormationModel("p")
    for name in ("eventual_purpose", "maturity_level", "infer_background",
                 "what_they_still_need"):
        assert hasattr(m, name), f"{name} must exist in order to refuse"


def test_open_questions_replaces_the_deficit_claim():
    """What the person 'still needs' becomes a question, never a judgement."""
    m = FormationModel("p")
    qs = m.open_questions()
    assert qs, "a model that knows nothing should have questions"
    for q in qs:
        assert q["question"].rstrip().endswith("?")
    joined = " ".join(q["question"] for q in qs).lower()
    for word in ("lack", "deficit", "immature", "should", "must", "need to become"):
        assert word not in joined, f"question phrasing drifted into prescription: {word}"


# ---------------------------------------------------------------------------
# Declared-only: the single route in
# ---------------------------------------------------------------------------

def test_background_is_declared_not_inferred():
    m = FormationModel("p")
    m.declare("background", "grew up between two cities")
    assert m.current("background") == "grew up between two cities"
    with pytest.raises(FormationRefusal) as exc:
        m.infer_background(some_behavioural_signal=0.9)
    assert exc.value.ground == "INFERRED_ORIGIN"


def test_third_party_completion_is_refused():
    m = FormationModel("p")
    with pytest.raises(FormationRefusal) as exc:
        m.administer("MLQ", [4] * 10, self_completed=False)
    assert exc.value.ground == "NOT_SELF_COMPLETED"


def test_invariant_xi_holds_on_a_declared_only_model():
    m = FormationModel("p")
    m.declare("background", "declared by the person")
    r = check_xi_declared_only(m)
    assert r.holds


def test_invariant_xi_fails_when_a_refusal_is_removed():
    """The negative test for Invariant XI: silence the refusal, break the check."""
    class Loosened(FormationModel):
        def eventual_purpose(self):
            return "to become a great engineer"

    r = check_xi_declared_only(Loosened("p"))
    assert not r.holds
    assert "eventual_purpose" in r.observation


def test_invariant_xi_fails_when_a_refusal_is_merely_deleted():
    class Deleted(FormationModel):
        maturity_level = None

    r = check_xi_declared_only(Deleted("p"))
    assert not r.holds
    assert "absent" in r.observation


# ---------------------------------------------------------------------------
# The person outranks the model
# ---------------------------------------------------------------------------

def test_person_override_wins_immediately():
    m = FormationModel("p")
    m.declare("motivation", "seeking approval")
    assert m.current("motivation") == "seeking approval"
    m.override("motivation", "curiosity", reason="that is not why I did it")
    assert m.current("motivation") == "curiosity"


def test_override_contests_rather_than_deletes():
    """The person wins for display; the evidence stays inspectable."""
    m = FormationModel("p")
    m.declare("motivation", "seeking approval", evidence_id="obs-1")
    m.override("motivation", "curiosity")
    ev = m.evidence_behind("motivation")
    assert ev["displayed"] == "curiosity"
    assert ev["overridden_by_person"] is True
    assert len(ev["declarations"]) == 1, "the prior statement must survive"
    assert ev["declarations"][0]["contested_by"], "and be marked contested"
    assert ev["declarations"][0]["value"] == "seeking approval"


def test_override_is_recorded_with_what_it_supersedes():
    m = FormationModel("p")
    m.declare("goal", "a")
    m.declare("goal", "b")
    ov = m.override("goal", "c")
    assert len(ov.supersedes) == 2


# ---------------------------------------------------------------------------
# Instruments: licence, consent, and deployment gating
# ---------------------------------------------------------------------------

def _consented_ledger(subject="p"):
    led = ConsentLedger()
    led.record("granted", subject, streams=[PSYCHOMETRIC_STREAM])
    return led


def test_mlq_scores_against_the_published_key():
    """Item 9 is the only reverse-scored item; Presence = (8-i9) + i1+i4+i5+i6."""
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    responses = [7, 1, 1, 7, 7, 7, 1, 1, 1, 1]   # high presence, low search
    admin = m.administer("MLQ", responses, population="USA")
    presence = admin.scores["presence_of_meaning"]
    search = admin.scores["search_for_meaning"]
    assert presence.total == pytest.approx(7 + 7 + 7 + 7 + (8 - 1))  # 35
    assert search.total == pytest.approx(5)
    assert presence.n_items == 5


def test_bpnsfs_scores_six_subscales_not_three():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    admin = m.administer("BPNSFS", [3] * 24)
    assert len(admin.scores) == 6
    assert "autonomy_frustration" in admin.scores


def test_unlicensed_instrument_is_refused():
    """CPS has no located permission statement. That is a refusal, not a warning."""
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    with pytest.raises(FormationRefusal) as exc:
        m.administer("CPS", [3] * 12)
    assert exc.value.ground == "UNLICENSED_INSTRUMENT"


def test_licence_confirmation_requires_written_evidence_not_a_flag():
    m = FormationModel("p")
    with pytest.raises(ValueError):
        m.confirm_licence("CPS", "")
    m.confirm_licence("CPS", "Email from K. C. Bronk, 2026-07-25, granting academic use.")


def test_confirming_a_licence_unblocks_administration():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    m.confirm_licence("CPS", "Written permission on file, 2026-07-25.")
    admin = m.administer("CPS", [4] * 12)
    assert len(admin.scores) == 3
    assert "beyond_the_self" in admin.scores


def test_stage_instruments_are_refused_because_the_rank_is_the_construct():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    for iid in ("WUSCT", "SOI", "MAP"):
        with pytest.raises(FormationRefusal) as exc:
            m.administer(iid, [1] * REGISTRY[iid].n_items)
        assert exc.value.ground in ("RATER_REQUIRED", "GLOBAL_RANKING")


def test_externally_scored_instrument_is_refused():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    with pytest.raises(FormationRefusal) as exc:
        m.administer("DIT-2", [1] * 60)
    assert exc.value.ground == "EXTERNAL_SCORING"


def test_licence_cannot_be_confirmed_for_a_rater_scored_instrument():
    m = FormationModel("p")
    with pytest.raises(FormationRefusal) as exc:
        m.confirm_licence("WUSCT", "I bought the manual.")
    assert exc.value.ground == "RATER_REQUIRED"


def test_instrument_without_verified_item_mapping_refuses_rather_than_guesses():
    """PVQ-RR's 19-value mapping was not read during verification. So it is not used."""
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    m.confirm_licence("PVQ-RR", "ORPC CC BY-NC-ND, educational use.")
    with pytest.raises(FormationRefusal) as exc:
        m.administer("PVQ-RR", [3] * 57)
    assert exc.value.ground == "UNLICENSED_INSTRUMENT"
    assert "inventing the mapping" in str(exc.value)


@pytest.mark.parametrize("ctx", [INSTITUTIONAL, UNDECLARED])
def test_psychometric_stream_is_refused_outside_self_and_consented_contexts(ctx):
    m = FormationModel("p", deployment=DeploymentContext(context=ctx),
                       ledger=_consented_ledger())
    with pytest.raises(FormationRefusal) as exc:
        m.administer("MLQ", [4] * 10)
    assert exc.value.ground == "DEPLOYMENT_CONTEXT"


def test_administration_without_consent_is_refused():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=ConsentLedger())
    with pytest.raises(FormationRefusal) as exc:
        m.administer("MLQ", [4] * 10)
    assert exc.value.ground == "UNCONSENTED_INSTRUMENT"


def test_consented_individual_context_is_permitted():
    m = FormationModel("p", deployment=DeploymentContext(context=CONSENTED_INDIVIDUAL),
                       ledger=_consented_ledger())
    assert m.administer("MLQ", [4] * 10) is not None


# ---------------------------------------------------------------------------
# What the profile will and will not say
# ---------------------------------------------------------------------------

def test_profile_never_produces_a_total():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    m.administer("MLQ", [5] * 10)
    prof = m.profile()
    assert "dimensions" in prof
    for banned in ("total", "overall", "level", "stage", "score"):
        assert banned not in prof
    assert "no_total_score" in prof


def test_profile_carries_the_instruments_caveats():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    m.administer("BPNSFS", [3] * 24)
    prof = m.profile()
    assert any("method artifact" in c for c in prof["caveats"]), \
        "the Murphy et al. challenge to need frustration must travel with the score"


def test_percentile_refuses_when_no_norms_exist():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    admin = m.administer("MLQ", [4] * 10)
    with pytest.raises(FormationRefusal) as exc:
        admin.scores["presence_of_meaning"].percentile()
    assert exc.value.ground == "NORMS_ABSENT"


def test_population_validation_is_recorded_honestly():
    """No instrument here was validated in Egypt. The model must not pretend."""
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    admin = m.administer("MLQ", [4] * 10, population="Egypt")
    assert admin.population_validated is False
    for spec in REGISTRY.values():
        assert "Egypt" not in spec.validated_populations


# ---------------------------------------------------------------------------
# Trajectory: a record of what was said, not a direction of travel
# ---------------------------------------------------------------------------

def test_trajectory_reports_points_with_evidence():
    m = FormationModel("p")
    m.declare("priority", "stability", evidence_id="e1")
    m.declare("priority", "risk", evidence_id="e2")
    t = m.trajectory("priority")
    assert t["n"] == 2 and t["changed"] is True
    assert [p["evidence_id"] for p in t["points"]] == ["e1", "e2"]


def test_trajectory_refuses_to_interpret_itself():
    m = FormationModel("p")
    m.declare("priority", "a")
    t = m.trajectory("priority")
    assert "not a claim about why" in t["interpretation"]


def test_single_administration_is_not_change():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    m.administer("MLQ", [4] * 10)
    t = m.instrument_trajectory("MLQ", "presence_of_meaning")
    assert t["n"] == 1
    assert "Two or more administrations" in t["interpretation"]


def test_repeated_administration_warns_against_reading_development_into_it():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    m.administer("MLQ", [4] * 10, at="2026-12-01T00:00:00+00:00")
    m.administer("MLQ", [6] * 10, at="2027-06-01T00:00:00+00:00")
    t = m.instrument_trajectory("MLQ", "presence_of_meaning")
    assert t["n"] == 2
    assert "reliable change index" in t["interpretation"]


# ---------------------------------------------------------------------------
# Registry integrity
# ---------------------------------------------------------------------------

def test_every_instrument_carries_a_citation_and_a_licence_status():
    for iid, spec in REGISTRY.items():
        assert spec.citation.strip(), f"{iid} has no citation"
        assert spec.licence, f"{iid} has no licence status"


def test_no_instrument_is_administrable_without_an_explicit_free_licence():
    from shadow_mirror.formation import _ADMINISTRABLE_LICENCES
    assert _ADMINISTRABLE_LICENCES == {LICENCE_CONFIRMED_FREE}
    free = {i for i, s in REGISTRY.items() if s.licence == LICENCE_CONFIRMED_FREE}
    assert free == {"MLQ", "BPNSFS", "ESS-HVS", "ASTI-R", "LGS"}, (
        "only instruments with a quoted, published permission statement may be "
        "administrable by default")
    for iid in free:
        assert REGISTRY[iid].licence_note.strip(), (
            f"{iid} claims a free licence with no quoted permission statement")


def test_rank_producing_instruments_are_registered_so_they_can_be_refused_by_name():
    for iid in ("WUSCT", "SOI", "MAP"):
        assert REGISTRY[iid].produces_single_rank is True


def test_scoring_rejects_a_response_vector_of_the_wrong_shape():
    with pytest.raises(ValueError):
        REGISTRY["MLQ"].score([4] * 9)


def test_scoring_rejects_out_of_range_responses():
    with pytest.raises(ValueError):
        REGISTRY["MLQ"].score([9] * 10)


def test_export_states_what_the_model_does_not_contain():
    m = FormationModel("p")
    m.declare("background", "declared")
    d = m.to_dict()
    assert "no inferred background" in d["note"]
    assert set(d["refusals_available"]) >= {
        "INFERRED_ORIGIN", "GLOBAL_RANKING", "PRESCRIPTIVE_DEFICIT",
        "PURPOSE_ATTRIBUTION"}


def test_consent_cannot_be_applied_retroactively():
    """Found by a failing test, not by design: the ledger already refuses this.

    An administration timestamped BEFORE the consent grant is refused, because
    ``streams_granted_at`` answers what was under grant at that instant and the
    answer is nothing. Backdating a session to before the person agreed is exactly
    the move GDPR Art. 7(1) demonstrability exists to prevent, and the hash-chained
    ledger makes it undoable rather than merely discouraged.
    """
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    with pytest.raises(FormationRefusal) as exc:
        m.administer("MLQ", [4] * 10, at="2020-01-01T00:00:00+00:00")
    assert exc.value.ground == "UNCONSENTED_INSTRUMENT"


# ---------------------------------------------------------------------------
# Randomised property harness for Invariant XI
#
# Invariants I-X are exercised across 200 randomised graph states. XI operates on
# a formation model rather than a graph, so it needs its own generator or it would
# be the one invariant asserted only by hand-built cases.
# ---------------------------------------------------------------------------

import random

_KEYS = ("background", "upbringing", "origin", "motivation", "priority", "goal")
_VALUES = ("a", "b", "c", 1, 2, 3.5, True, None, "", "moved at 12")


def _random_model(seed: int) -> FormationModel:
    rng = random.Random(seed)
    led = ConsentLedger()
    if rng.random() < 0.8:
        led.record("granted", "p", streams=[PSYCHOMETRIC_STREAM])
    ctx = rng.choice([SELF, CONSENTED_INDIVIDUAL, INSTITUTIONAL, UNDECLARED])
    m = FormationModel("p", deployment=DeploymentContext(context=ctx), ledger=led)
    for _ in range(rng.randrange(0, 6)):
        m.declare(rng.choice(_KEYS), rng.choice(_VALUES),
                  evidence_id=f"e{rng.randrange(100)}")
    for _ in range(rng.randrange(0, 3)):
        m.override(rng.choice(_KEYS), rng.choice(_VALUES))
    for _ in range(rng.randrange(0, 3)):
        iid = rng.choice(sorted(REGISTRY))
        spec = REGISTRY[iid]
        n = max(spec.n_items, 1)
        lo, hi = spec.scale_min, max(spec.scale_max, spec.scale_min)
        try:
            m.administer(iid, [rng.randint(lo, hi) for _ in range(n)])
        except (FormationRefusal, ValueError, KeyError):
            pass  # every one of these is a correct outcome; XI must hold regardless
    return m


@pytest.mark.parametrize("seed", range(200))
def test_invariant_xi_holds_across_randomised_models(seed):
    """XI must hold whatever sequence of declarations, overrides and attempted
    administrations the model has been through — including the ones that refused."""
    assert check_xi_declared_only(_random_model(seed)).holds


@pytest.mark.parametrize("seed", range(50))
def test_no_randomised_model_ever_holds_a_non_self_completed_administration(seed):
    m = _random_model(seed)
    assert all(a.self_completed for a in m._administrations)


@pytest.mark.parametrize("seed", range(50))
def test_override_always_wins_across_randomised_models(seed):
    m = _random_model(seed)
    for key, ov in m._overrides.items():
        assert m.current(key) == ov.value, "an override must always win for display"
        assert m.evidence_behind(key)["overridden_by_person"] is True


# ---------------------------------------------------------------------------
# The Session 17 substitutions
# ---------------------------------------------------------------------------

def test_ess_hvs_replaces_the_blocked_pvq_rr():
    """PVQ-RR stayed blocked for two sessions. ESS-HVS measures the same construct
    under a licence that already permits use, and publishes its item mapping."""
    assert REGISTRY["PVQ-RR"].licence != LICENCE_CONFIRMED_FREE
    spec = REGISTRY["ESS-HVS"]
    assert spec.licence == LICENCE_CONFIRMED_FREE
    assert spec.construct == REGISTRY["PVQ-RR"].construct == "will"
    assert len(spec.subscales) == 10
    assert sum(len(v) for v in spec.subscales.values()) == spec.n_items == 21


def test_ess_hvs_scoring_is_reversed_so_high_means_important():
    """ESS codes 1 = 'very much like me'. Every item is reversed so a high subscale
    score means the value matters more, which is what a reader will assume."""
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    responses = [1] * 21          # 'very much like me' on everything
    admin = m.administer("ESS-HVS", responses)
    for sc in admin.scores.values():
        assert sc.mean == pytest.approx(6.0), "1 = most like me must score as high importance"


def test_asti_replaces_the_blocked_3dws_but_declares_the_construct_drift():
    assert REGISTRY["3D-WS"].licence != LICENCE_CONFIRMED_FREE
    spec = REGISTRY["ASTI-R"]
    assert spec.licence == LICENCE_CONFIRMED_FREE
    assert spec.construct == REGISTRY["3D-WS"].construct == "maturity_profile"
    assert len(spec.subscales) == 5
    assert spec.permits_total is False
    assert any("construct drift" in c.lower() for c in spec.caveats),         "a substitution that changes the construct must say so in the caveats"


def test_asti_reverse_scoring_is_applied():
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    admin = m.administer("ASTI-R", [1] * 25)
    pm = admin.scores["peace_of_mind"]        # items 1, 5, 9, 22; 1 and 22 reversed
    assert pm.total == pytest.approx(1 + 4 + 1 + 4)


def test_lgs_is_free_but_still_refuses_because_its_key_is_unverified():
    """Free to use is not the same as safe to score."""
    spec = REGISTRY["LGS"]
    assert spec.licence == LICENCE_CONFIRMED_FREE
    assert spec.subscales == {}
    m = FormationModel("p", deployment=DeploymentContext(context=SELF),
                       ledger=_consented_ledger())
    with pytest.raises(FormationRefusal) as exc:
        m.administer("LGS", [1] * 20)
    assert exc.value.ground == "UNLICENSED_INSTRUMENT"
    assert "inventing the mapping" in str(exc.value)


def test_no_substitute_claims_egyptian_validation():
    for iid in ("ESS-HVS", "ASTI-R", "LGS"):
        assert "Egypt" not in REGISTRY[iid].validated_populations
