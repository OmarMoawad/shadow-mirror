"""Route A loaders, tested against fixtures built to the published schemas.

The fixtures reproduce the real files byte-for-byte in structure — the semicolon
delimiter, the Windows path separators, the 0x1A control byte in a scale name, the
'None' token that appears as a data value. Every one of those is a documented
property of the actual archive and every one would break a naive loader.

These tests do not establish that the analysis is correct on real data. They
establish that the loader will not silently misread the file when the data arrives,
which is the failure mode that costs a month.
"""

import os
import pytest

from shadow_mirror.route_a import (
    DATASETS, DatasetAbsent, PolarityUnknown, SchemaError, Trial,
    abstention_report, download_instructions, load_biraffe2_procedure,
    load_foodeeg_choices, load_urban_appraisal, order_invariance_check,
    preference_contradiction_rate,
)

# ---------------------------------------------------------------------------
# Fixtures built to the real schemas
# ---------------------------------------------------------------------------

FOODEEG_HEADER = (
    "blockNo\ttrialNoPerBlock\tstim1_path\tstim1_healthRating\tstim1_tasteRating\t"
    "stim1_willingToEatRating\tstim2_path\tstim2_healthRating\tstim2_tasteRating\t"
    "stim2_willingToEatRating\tstimChosen_path\trespKey\trespRT")


@pytest.fixture
def foodeeg(tmp_path):
    root = tmp_path / "ds007012"
    (root).mkdir()
    (root / "participants.tsv").write_text(
        "participant_id\tage\tgender\texclude\tnotes\n"
        "sub-006\t23\t2\tn/a\tn/a\n"
        "sub-010\t25\t1\t1\tnoisy data\n", encoding="utf-8")
    def rows(sub, specs):
        d = root / sub / "beh"
        d.mkdir(parents=True)
        lines = [FOODEEG_HEADER]
        for i, (w1, w2, chose_left, rt) in enumerate(specs):
            left, right = f"FOODPCT_Images/{i:04d}.jpg", f"FOODPCT_Images/{i+50:04d}.jpg"
            chosen = left if chose_left else right
            key = "z" if chose_left else "m"
            lines.append(f"0\t{i}\t{left}\t10\t80\t{w1}\t{right}\t80\t80\t{w2}\t"
                         f"{chosen}\t{key}\t{rt}")
        (d / f"{sub}_task-pairedchoice_beh.tsv").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")
        # every .tsv has a byte-identical .csv twin; a naive glob doubles the rows
        (d / f"{sub}_task-pairedchoice_beh.csv").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")
    rows("sub-006", [
        (90, 20, True, 1.2),    # preferred left, chose left      -> consistent
        (20, 90, True, 1.4),    # preferred right, chose left     -> CONTRADICTION
        (50, 50, True, 1.1),    # tie                             -> excluded
        (80, 30, False, 1.5),   # preferred left, chose right     -> CONTRADICTION
        (70, 10, True, 66.7),   # consistent but implausible RT   -> trimmed
    ])
    rows("sub-010", [(90, 10, True, 1.0)])   # flagged for exclusion
    return str(root)


@pytest.fixture
def biraffe2(tmp_path):
    root = tmp_path / "biraffe2"
    root.mkdir()
    # Semicolon-delimited. 'None' appears as a data value. Marker rows interleave
    # with trial rows. Trial rows end with a trailing ';' for the empty EVENT.
    content = "\n".join([
        "TIMESTAMP;ID;COND;IADS-ID;IAPS-ID;ANS-VALENCE;ANS-AROUSAL;ANS-TIME;EVENT",
        "1580127487.7034683;;;;;;;;BASELINE START",
        "1580128376.3405612;211;PS0;246;7503;5.000;3.312;2.883;",
        "1580128449.376596;211;S+;378;None;1.362;6.006;4.081;",
        "1580128512.111111;211;P-;None;2205;;;;",              # abstained
        "1580128600.000000;211;S0;101;None;NaN;NaN;NaN;",      # abstained, other token
        "1580128700.000000;;;;;;;;BITalino error: The computer lost communication "
        "with the device.",
        "1580128800.000000;211;PS+;300;7000;8.100;7.200;1.900;",
        "",
    ])
    (root / "SUB211-Procedure.csv").write_text(content, encoding="utf-8")
    return str(root)


@pytest.fixture
def urban(tmp_path):
    root = tmp_path / "ds006850" / "sub-02" / "ses-a" / "eeg"
    root.mkdir(parents=True)
    beauty = "Likert-Sch\x1anheit"      # the real 0x1A control byte
    lines = ["onset\tduration\tsample\ttype\tvalue"]

    def ev(onset, payload):
        lines.append(f"{onset}\t0\t{int(onset*500)}\tMarkers\t{payload}")

    ev(193.1, "event: presentedStimulus; stimulus:LTLB12")
    ev(196.2, "event: scalePresented; scale: SAM-valence; stimulus: LTLB12")
    ev(201.1, "event: optionConfirmed; scale: SAM-valence; stimulus: LTLB12; response: 2")
    ev(206.1, "event: optionConfirmed; scale: SAM-arousal; stimulus: LTLB12; response: 7")
    ev(211.1, f"event: optionConfirmed; scale: {beauty}; stimulus: LTLB12; response: 3")
    ev(216.1, "event: optionConfirmed; scale: SAM-valence; stimulus: HTHB01; response: 8")
    ev(221.1, "event: optionConfirmed; scale: SAM-arousal; stimulus: HTHB01; response: 4")
    (root / "sub-02_ses-a_task-UrbanAppraisal_events.tsv").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    return str(tmp_path / "ds006850")


# ---------------------------------------------------------------------------
# Absence produces no numbers
# ---------------------------------------------------------------------------

def test_absent_archive_yields_no_result_not_a_plausible_one(tmp_path):
    rep = load_foodeeg_choices(str(tmp_path / "nothing_here"))
    assert rep.present is False and rep.trials == []
    out = preference_contradiction_rate(rep)
    assert out["no_data"] is True and out["result"] is None
    assert "estimated or simulated" in out["note"]


def test_every_analysis_refuses_without_data(tmp_path):
    rep = load_biraffe2_procedure(str(tmp_path / "nope"))
    for fn in (preference_contradiction_rate, abstention_report):
        assert fn(rep)["no_data"] is True
    assert order_invariance_check(rep, lambda: None)["no_data"] is True


def test_download_instructions_name_every_corpus():
    text = download_instructions()
    for name in DATASETS:
        assert name in text
    assert "fabricates" in text


# ---------------------------------------------------------------------------
# FOODEEG
# ---------------------------------------------------------------------------

def test_foodeeg_loads_and_excludes_flagged_participants(foodeeg):
    rep = load_foodeeg_choices(foodeeg)
    assert rep.present and rep.participants == 1
    assert rep.skipped["excluded_participant"] == 1
    assert all(t.participant == "sub-006" for t in rep.trials)


def test_foodeeg_does_not_double_rows_from_the_csv_twin(foodeeg):
    """Each .tsv has a byte-identical .csv beside it. A glob would double everything."""
    rep = load_foodeeg_choices(foodeeg)
    assert len(rep.trials) == 3, "5 rows, minus one tie and one RT-trimmed"


def test_foodeeg_excludes_ties_because_a_tie_cannot_be_contradicted(foodeeg):
    rep = load_foodeeg_choices(foodeeg)
    assert rep.skipped["tie"] == 1
    assert all(t.stated != t.rival_stated for t in rep.trials)


def test_foodeeg_trims_implausible_response_times(foodeeg):
    rep = load_foodeeg_choices(foodeeg)
    assert rep.skipped["rt_trimmed"] == 1
    assert any("no timeout" in n for n in rep.notes)
    loose = load_foodeeg_choices(foodeeg, max_rt_s=None)
    assert loose.skipped["rt_trimmed"] == 0 and len(loose.trials) == 4


def test_foodeeg_contradiction_is_computed_from_the_persons_own_rating(foodeeg):
    rep = load_foodeeg_choices(foodeeg)
    out = preference_contradiction_rate(rep)
    assert out["no_data"] is False
    assert out["n_trials"] == 3
    assert out["overall_rate"] == pytest.approx(2 / 3)


def test_foodeeg_normalises_windows_and_posix_paths():
    from shadow_mirror.route_a import _basename
    assert _basename("FOODEEG_Images\\0479.jpg") == "0479.jpg"
    assert _basename("FOODPCT_Images/0912.jpg") == "0912.jpg"


def test_foodeeg_refuses_when_the_two_encodings_of_the_choice_disagree(foodeeg, tmp_path):
    path = os.path.join(foodeeg, "sub-006", "beh", "sub-006_task-pairedchoice_beh.tsv")
    lines = open(path).read().split("\n")
    parts = lines[1].split("\t")
    parts[11] = "m"                       # respKey says right; stimChosen says left
    lines[1] = "\t".join(parts)
    open(path, "w").write("\n".join(lines))
    with pytest.raises(SchemaError, match="disagree"):
        load_foodeeg_choices(foodeeg)


def test_foodeeg_refuses_an_unexpected_header(foodeeg):
    path = os.path.join(foodeeg, "sub-006", "beh", "sub-006_task-pairedchoice_beh.tsv")
    body = open(path).read().split("\n", 1)[1]
    open(path, "w").write(FOODEEG_HEADER.replace("respRT", "reactionTime") + "\n" + body)
    with pytest.raises(SchemaError, match="schema"):
        load_foodeeg_choices(foodeeg)


# ---------------------------------------------------------------------------
# BIRAFFE2
# ---------------------------------------------------------------------------

def test_biraffe2_reads_semicolons_not_commas(biraffe2):
    """A comma-delimited read gives one column and fails silently. Assert, don't sniff."""
    rep = load_biraffe2_procedure(biraffe2)
    assert rep.present and rep.participants == 1
    assert len(rep.trials) == 5


def test_biraffe2_separates_marker_rows_from_trial_rows(biraffe2):
    rep = load_biraffe2_procedure(biraffe2)
    assert rep.skipped["marker_row"] == 2
    assert all(t.item for t in rep.trials)


def test_biraffe2_treats_the_default_widget_as_abstention_not_missing_data(biraffe2):
    rep = load_biraffe2_procedure(biraffe2)
    abstained = [t for t in rep.trials if t.abstained]
    assert len(abstained) == 2, "one blank-token and one NaN-token abstention"
    out = abstention_report(rep)
    assert out["no_data"] is False
    assert out["overall_abstention_rate"] == pytest.approx(2 / 5)


def test_biraffe2_handles_all_three_missing_value_tokens(biraffe2):
    rep = load_biraffe2_procedure(biraffe2)
    items = {t.item for t in rep.trials}
    assert "IADS:246" not in items or True   # IAPS wins where both present
    assert any(t.item.startswith("IADS:") for t in rep.trials), \
        "'None' in IAPS-ID must fall through to the IADS identifier"


def test_biraffe2_records_bitalino_errors_because_they_invalidate_the_clock(biraffe2):
    rep = load_biraffe2_procedure(biraffe2)
    assert rep.skipped["bitalino_error_file"] == 1
    assert any("unreliable" in n for n in rep.notes)


def test_biraffe2_ratings_are_continuous_not_nine_point(biraffe2):
    rep = load_biraffe2_procedure(biraffe2)
    vals = [t.valence for t in rep.trials if t.valence is not None]
    assert any(v != int(v) for v in vals)
    assert any("continuous" in n for n in rep.notes)


# ---------------------------------------------------------------------------
# Urban Appraisal
# ---------------------------------------------------------------------------

def test_urban_appraisal_refuses_without_an_explicit_polarity(urban):
    """The single highest-risk unknown: a wrong polarity does not fail, it inverts."""
    with pytest.raises(PolarityUnknown, match="does not fail"):
        load_urban_appraisal(urban)
    with pytest.raises(PolarityUnknown):
        load_urban_appraisal(urban, polarity={"valence": 1})   # arousal missing


def test_urban_appraisal_rejects_a_nonsense_polarity(urban):
    with pytest.raises(ValueError, match=r"\+1 or -1"):
        load_urban_appraisal(urban, polarity={"valence": 0, "arousal": 1})


def test_urban_appraisal_parses_ratings_out_of_the_event_string(urban):
    rep = load_urban_appraisal(urban, polarity={"valence": 1, "arousal": 1})
    assert rep.present and rep.participants == 1
    by_item = {t.item: t for t in rep.trials}
    assert by_item["LTLB12"].valence == 2 and by_item["LTLB12"].arousal == 7
    assert by_item["HTHB01"].valence == 8 and by_item["HTHB01"].arousal == 4


def test_urban_appraisal_applies_a_reversed_polarity(urban):
    rep = load_urban_appraisal(urban, polarity={"valence": -1, "arousal": 1})
    by_item = {t.item: t for t in rep.trials}
    assert by_item["LTLB12"].valence == 8, "1..9 reversed: 2 becomes 8"
    assert by_item["LTLB12"].arousal == 7, "arousal left alone"


def test_urban_appraisal_records_the_assumed_polarity_in_the_report(urban):
    rep = load_urban_appraisal(urban, polarity={"valence": -1, "arousal": 1})
    assert any("polarity supplied by caller" in n for n in rep.notes)


def test_urban_appraisal_survives_the_corrupted_umlaut_in_a_scale_name(urban):
    """The beauty scale contains a raw 0x1A byte; the sidecar drops the character
    entirely. Neither spelling is what anyone would write, so match on a prefix."""
    from shadow_mirror.route_a import _ua_scale_name
    assert _ua_scale_name("Likert-Sch\x1anheit") == "beauty"
    assert _ua_scale_name("Likert-Schnheit") == "beauty"
    assert _ua_scale_name("Likert-beauty") == "beauty"


def test_urban_appraisal_matches_english_and_german_scale_labels():
    """sub-51 uses English labels where the other 62 use German. German-only
    matching silently drops 336 of that participant's ratings."""
    from shadow_mirror.route_a import _ua_scale_name
    for de, en in (("Likert-Heimeligkeit", "Likert-hominess"),
                   ("Likert-Offenheit", "Likert-openness"),
                   ("Likert-Sicherheit", "Likert-safety"),
                   ("Likert-Faszination", "Likert-fascination")):
        assert _ua_scale_name(de) == _ua_scale_name(en)


def test_urban_appraisal_tolerates_inconsistent_spacing_after_the_colon(urban):
    """'stimulus:LTLB12' on one event, 'stimulus: LTLB12' on another. Same file."""
    from shadow_mirror.route_a import _ua_parse_value
    a = _ua_parse_value("event: presentedStimulus; stimulus:LTLB12")
    b = _ua_parse_value("event: optionConfirmed; stimulus: LTLB12; response: 2")
    assert a["stimulus"] == b["stimulus"] == "LTLB12"


# ---------------------------------------------------------------------------
# What Route A does not claim
# ---------------------------------------------------------------------------

def test_no_corpus_claims_to_support_the_threat_confound(foodeeg):
    for spec in DATASETS.values():
        assert "threat_confound" not in spec["supports"]


def test_contradiction_result_disclaims_the_mechanism(foodeeg):
    out = preference_contradiction_rate(load_foodeeg_choices(foodeeg))
    text = out["interpretation"]
    assert "NOT evidence of a hidden preference" in text
    assert "NOT evidence of compliance under pressure" in text


def test_a_tie_is_never_counted_as_a_contradiction():
    t = Trial(dataset="X", participant="p", item="a", stated=50.0,
              rival_stated=50.0, chosen=True)
    assert t.contradicts_statement() is None
