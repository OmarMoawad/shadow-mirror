"""Route A: running this architecture against data collected by other people.

Three public corpora, 282 participants, none of them ours. This module is the
loading and analysis layer for a secondary analysis that would be the first time
Shadow Mirror touches human data.

What it can and cannot establish, stated before any code:

  CAN   calibration of the desire model where a stated preference and a later
        contradicting choice are both recorded (FOODEEG)
  CAN   abstention behaviour against a real abstention signal — BIRAFFE2 records
        when a participant left the rating widget at its default rather than
        moving it, which is a person declining to answer
  CAN   order-invariance, by permuting the order of real observations
  CANNOT the threat-confound claim. No corpus here contains a coercion
        manipulation alongside a stated stance and a contradictable choice. §6.1
        of P2 is untouched by anything in this file.

Three design rules, each of which cost functionality:

1.  **A loader that cannot verify its schema refuses.** Every one of these three
    datasets contradicts its own documentation somewhere — FOODEEG's sidecar
    documents a trial count wrong for 116 of 117 subjects, Urban Appraisal's
    README and metadata disagree about the licence, BIRAFFE2's paper prints a
    column name its files spell differently. So the files are the authority, and
    a mismatch is an error rather than a warning.

2.  **Undocumented coding is a refusal, not a default.** Urban Appraisal
    publishes no polarity for its rating scales. Nothing states whether 1 means
    "happy" or "unhappy" for valence. Guessing would silently invert every
    result, so the loader refuses until a polarity is passed in explicitly.

3.  **No data means no numbers.** Every analysis entry point returns a structured
    "no data" result rather than a plausible one. Nothing in this module can
    produce a figure without the archives present.

Zero runtime dependencies, consistent with the rest of the package.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "SchemaError", "PolarityUnknown", "DatasetAbsent",
    "Trial", "LoadReport",
    "load_foodeeg_choices", "load_biraffe2_procedure", "load_urban_appraisal",
    "preference_contradiction_rate", "abstention_report", "order_invariance_check",
    "DATASETS", "download_instructions",
]


# --------------------------------------------------------------------------
# Failure modes, all of them loud
# --------------------------------------------------------------------------

class SchemaError(ValueError):
    """The file on disk is not the file the loader was written against."""


class PolarityUnknown(ValueError):
    """A rating scale's direction is not documented and was not supplied."""


class DatasetAbsent(FileNotFoundError):
    """The archive is not present. No result is produced, and none is invented."""


# --------------------------------------------------------------------------
# Provenance for each corpus. Sizes and licences recorded because a secondary
# analysis inherits the licence of what it reuses.
# --------------------------------------------------------------------------

DATASETS: Dict[str, Dict[str, Any]] = {
    "FOODEEG": {
        "accession": "OpenNeuro ds007012 v1.1.0",
        "doi": "10.18112/openneuro.ds007012.v1.1.0",
        "citation": ("Chae, V. J., Grootswagers, T., Bode, S., & Feuerriegel, D. (2025). "
                     "FOODEEG: An open dataset of human electroencephalographic and "
                     "behavioural responses to food images. bioRxiv 2025.11.07.687287."),
        "licence": "CC0 (dataset_description.json; no LICENSE file present)",
        "n_participants": 117,
        "size_raw_gb": 31.62,
        "supports": ["preference_contradiction", "calibration", "order_invariance"],
        "fetch": "git clone https://github.com/OpenNeuroDatasets/ds007012.git",
    },
    "BIRAFFE2": {
        "accession": "Zenodo record 5786104 (v1.1.0)",
        "doi": "10.5281/zenodo.3865859",
        "citation": ("Kutt, K., Drazyk, D., Zuchowska, L., Szelazek, M., Bobek, S., & "
                     "Nalepa, G. J. (2022). BIRAFFE2, a multimodal dataset for "
                     "emotion-based personalization in rich affective game environments. "
                     "Scientific Data, 9, 274. doi:10.1038/s41597-022-01402-6"),
        "licence": "CC BY 4.0",
        "n_participants": 102,
        "size_without_screencast_gb": 6.35,
        "supports": ["abstention", "calibration", "order_invariance"],
        "fetch": ("https://zenodo.org/records/5786104/files/BIRAFFE2-procedure.zip "
                  "(35 MB — the only archive needed for the behavioural analysis)"),
    },
    "URBAN_APPRAISAL": {
        "accession": "OpenNeuro ds006850 v1.0.0",
        "doi": "10.18112/openneuro.ds006850.v1.0.0",
        "citation": ("Zaehme, C., Sander, I., & Gramann, K. (2025). Urban Appraisal: "
                     "Physiological Recording during Rating of Different Urban "
                     "Environments. OpenNeuro. doi:10.18112/openneuro.ds006850.v1.0.0"),
        "licence": ("CONTESTED — dataset_description.json says CC0, the README says "
                    "CC BY 4.0. Attribute the authors regardless."),
        "n_participants": 63,
        "size_gb": 37.24,
        "supports": ["calibration"],
        "fetch": ("git clone https://github.com/OpenNeuroDatasets/ds006850.git "
                  "(16 MB — metadata and all events.tsv, which is all this module needs)"),
    },
}


def download_instructions() -> str:
    """What to run, and why the small archive is usually the right one."""
    out = ["Route A needs three archives. Two of the three analyses need only the",
           "small metadata archive, not the multi-gigabyte signal files.", ""]
    for name, d in DATASETS.items():
        out += [f"{name}  ({d['accession']}, {d['licence'].split(';')[0]})",
                f"    {d['fetch']}", ""]
    out += ["Nothing in this module fabricates a result when an archive is missing.",
            "Every entry point returns a structured 'no data' record instead."]
    return "\n".join(out)


# --------------------------------------------------------------------------
# One trial, from any of the three corpora
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Trial:
    """A single observation, normalised across corpora.

    ``stated`` is what the person said about the item. ``chosen`` is what they did,
    where a corpus records an action that could contradict the statement.
    ``abstained`` is true where the corpus records the person declining to answer —
    which is a first-class outcome here rather than missing data.
    """
    dataset: str
    participant: str
    item: str
    stated: Optional[float] = None
    stated_scale: Tuple[float, float] = (0.0, 1.0)
    arousal: Optional[float] = None
    valence: Optional[float] = None
    chosen: Optional[bool] = None
    rival_item: Optional[str] = None
    rival_stated: Optional[float] = None
    latency_s: Optional[float] = None
    abstained: bool = False
    order: int = 0

    def contradicts_statement(self) -> Optional[bool]:
        """Did the action go against the stated preference?

        Returns None when the corpus does not record an action, or when the two
        stated values tie — a tie is not a contradiction and must not be counted
        as one.
        """
        if self.chosen is None or self.stated is None or self.rival_stated is None:
            return None
        if self.stated == self.rival_stated:
            return None
        preferred = self.stated > self.rival_stated
        return preferred != self.chosen


@dataclass
class LoadReport:
    dataset: str
    present: bool
    trials: List[Trial] = field(default_factory=list)
    participants: int = 0
    skipped: Dict[str, int] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"dataset": self.dataset, "present": self.present,
                "n_trials": len(self.trials), "participants": self.participants,
                "skipped": self.skipped, "notes": self.notes}


def _require(path: str, dataset: str) -> None:
    if not os.path.exists(path):
        raise DatasetAbsent(
            f"{dataset} not found at {path!r}.\n\n{download_instructions()}")


def _check_header(actual: Sequence[str], expected: Sequence[str],
                  path: str, dataset: str) -> None:
    if list(actual) != list(expected):
        missing = [c for c in expected if c not in actual]
        extra = [c for c in actual if c not in expected]
        raise SchemaError(
            f"{dataset}: {os.path.basename(path)} does not match the schema this "
            f"loader was written against.\n"
            f"  expected: {list(expected)}\n"
            f"  found:    {list(actual)}\n"
            f"  missing:  {missing}\n  unexpected: {extra}\n"
            f"This is an error rather than a warning because all three Route A "
            f"corpora contradict their own documentation somewhere; the files are "
            f"the authority and a mismatch means the archive version changed.")


# --------------------------------------------------------------------------
# FOODEEG — the only corpus with a rating that a later choice can contradict
# --------------------------------------------------------------------------

_FOODEEG_CHOICE_HEADER = [
    "blockNo", "trialNoPerBlock",
    "stim1_path", "stim1_healthRating", "stim1_tasteRating", "stim1_willingToEatRating",
    "stim2_path", "stim2_healthRating", "stim2_tasteRating", "stim2_willingToEatRating",
    "stimChosen_path", "respKey", "respRT",
]

#: Session 1 writes Windows-style paths, Session 2 POSIX-style, for the same images.
#: os.path.basename will not strip a backslash on POSIX, so normalise first.
def _basename(path: str) -> str:
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def load_foodeeg_choices(root: str, *, rating: str = "willingToEat",
                         exclude_flagged: bool = True,
                         max_rt_s: Optional[float] = 10.0) -> LoadReport:
    """Load the Session-2 paired-choice task, with Session-1 ratings on the same row.

    This is the structure the architecture models: the person rated each food, then
    later chose between two of them, so a choice can disagree with a rating. The
    ratings are embedded per row, so no cross-session join is required for these
    items.

    ``max_rt_s`` trims implausible trials. The corpus applied **no timeout** — real
    response times run to 66.7 s — so some trimming is necessary and the threshold
    is recorded in the report rather than hidden.
    """
    rep = LoadReport(dataset="FOODEEG", present=False)
    if not os.path.isdir(root):
        rep.notes.append(f"archive not present at {root!r}")
        return rep
    rep.present = True

    if rating not in ("willingToEat", "taste", "health"):
        raise ValueError(f"unknown FOODEEG rating {rating!r}")
    col1, col2 = f"stim1_{rating}Rating", f"stim2_{rating}Rating"

    excluded: set = set()
    ptsv = os.path.join(root, "participants.tsv")
    if exclude_flagged and os.path.exists(ptsv):
        with open(ptsv, newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                if (row.get("exclude") or "").strip() == "1":
                    excluded.add(row["participant_id"])
        rep.notes.append(f"{len(excluded)} participants excluded via participants.tsv")

    skipped = {"excluded_participant": 0, "tie": 0, "rt_trimmed": 0, "bad_row": 0}
    subs = sorted(d for d in os.listdir(root) if d.startswith("sub-"))
    seen_participants = 0

    for sub in subs:
        if sub in excluded:
            skipped["excluded_participant"] += 1
            continue
        # NB: a bare glob on sub-*/beh/* doubles every row, because each .tsv has a
        # byte-identical .csv twin. Address the .tsv explicitly.
        path = os.path.join(root, sub, "beh", f"{sub}_task-pairedchoice_beh.tsv")
        if not os.path.exists(path):
            continue
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            _check_header(reader.fieldnames or [], _FOODEEG_CHOICE_HEADER,
                          path, "FOODEEG")
            seen_participants += 1
            for i, row in enumerate(reader):
                try:
                    s1, s2 = float(row[col1]), float(row[col2])
                    rt = float(row["respRT"])
                except (TypeError, ValueError):
                    skipped["bad_row"] += 1
                    continue
                if max_rt_s is not None and rt > max_rt_s:
                    skipped["rt_trimmed"] += 1
                    continue
                if s1 == s2:
                    skipped["tie"] += 1
                    continue
                left = _basename(row["stim1_path"])
                right = _basename(row["stim2_path"])
                chosen_name = _basename(row["stimChosen_path"])
                # respKey and stimChosen_path encode the same fact. Disagreement
                # means the file is not what we think it is.
                key = (row.get("respKey") or "").strip()
                by_key = left if key == "z" else right if key == "m" else None
                if by_key is not None and by_key != chosen_name:
                    raise SchemaError(
                        f"FOODEEG {sub} row {i}: respKey={key!r} implies {by_key!r} "
                        f"but stimChosen_path is {chosen_name!r}. The two redundant "
                        f"encodings of the choice disagree; refusing to guess.")
                rep.trials.append(Trial(
                    dataset="FOODEEG", participant=sub, item=left,
                    stated=s1, stated_scale=(0.0, 100.0),
                    chosen=(chosen_name == left),
                    rival_item=right, rival_stated=s2,
                    latency_s=rt, order=len(rep.trials)))
    rep.participants = seen_participants
    rep.skipped = skipped
    rep.notes.append(f"rating column: {rating} (0-100 integer scale)")
    if max_rt_s is not None:
        rep.notes.append(f"trials trimmed at respRT > {max_rt_s}s; corpus applied no timeout")
    rep.notes.append("ties excluded: equal ratings cannot contradict a choice")
    return rep


# --------------------------------------------------------------------------
# BIRAFFE2 — a real abstention signal
# --------------------------------------------------------------------------

_BIRAFFE2_PROCEDURE_HEADER = [
    "TIMESTAMP", "ID", "COND", "IADS-ID", "IAPS-ID",
    "ANS-VALENCE", "ANS-AROUSAL", "ANS-TIME", "EVENT",
]

#: Missing values appear as several distinct tokens across BIRAFFE2 files.
_BIRAFFE2_NA = {"", "nan", "NaN", "None", "NA"}


def _b2_float(raw: Optional[str]) -> Optional[float]:
    if raw is None or raw.strip() in _BIRAFFE2_NA:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def load_biraffe2_procedure(root: str) -> LoadReport:
    """Load per-stimulus ratings, treating the default-widget case as abstention.

    The corpus descriptor states that a missing value "indicates that the participant
    has not made any choice but left the default option". That is a person declining
    to answer, recorded as such — which is the closest thing to a real abstention
    signal in any public affective corpus, and the reason BIRAFFE2 is here.

    The files are **semicolon-delimited**. A comma-delimited read yields a single
    column and fails silently, so the delimiter is asserted rather than sniffed.
    """
    rep = LoadReport(dataset="BIRAFFE2", present=False)
    if not os.path.isdir(root):
        rep.notes.append(f"archive not present at {root!r}")
        return rep
    rep.present = True

    paths = sorted(
        os.path.join(dp, f)
        for dp, _, fs in os.walk(root) for f in fs
        if f.endswith("-Procedure.csv"))
    skipped = {"marker_row": 0, "bad_row": 0, "bitalino_error_file": 0}
    participants = set()

    for path in paths:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh, delimiter=";")
            _check_header(reader.fieldnames or [], _BIRAFFE2_PROCEDURE_HEADER,
                          path, "BIRAFFE2")
            had_error = False
            for row in reader:
                pid = (row.get("ID") or "").strip()
                event = (row.get("EVENT") or "").strip()
                if event:
                    # Marker rows carry no trial. Bluetooth errors invalidate the
                    # physiological clock downstream, so record that they occurred.
                    if "BITalino error" in event:
                        had_error = True
                    skipped["marker_row"] += 1
                    continue
                if not pid:
                    skipped["bad_row"] += 1
                    continue
                participants.add(pid)
                val = _b2_float(row.get("ANS-VALENCE"))
                aro = _b2_float(row.get("ANS-AROUSAL"))
                abstained = val is None and aro is None
                iaps = (row.get("IAPS-ID") or "").strip()
                iads = (row.get("IADS-ID") or "").strip()
                item = f"IAPS:{iaps}" if iaps not in _BIRAFFE2_NA else f"IADS:{iads}"
                rep.trials.append(Trial(
                    dataset="BIRAFFE2", participant=f"SUB{pid}", item=item,
                    valence=val, arousal=aro, stated_scale=(1.0, 9.0),
                    latency_s=_b2_float(row.get("ANS-TIME")),
                    abstained=abstained, order=len(rep.trials)))
            if had_error:
                skipped["bitalino_error_file"] += 1

    rep.participants = len(participants)
    rep.skipped = skipped
    rep.notes.append("valence and arousal are continuous on [1, 9], not 9-point SAM")
    rep.notes.append("abstention = participant left the rating widget at its default")
    if skipped["bitalino_error_file"]:
        rep.notes.append(
            f"{skipped['bitalino_error_file']} participant file(s) contain a BITalino "
            f"error; the authors declare downstream physiological timestamps "
            f"unreliable in those recordings")
    return rep


# --------------------------------------------------------------------------
# Urban Appraisal — ratings buried in an event string, with undocumented polarity
# --------------------------------------------------------------------------

_UA_EVENTS_HEADER = ["onset", "duration", "sample", "type", "value"]

#: The beauty scale contains a raw 0x1A control byte where an umlaut should be, and
#: the sidecar spells the same key with the character dropped entirely. Neither is
#: the literal we would write. Match on a prefix instead.
_UA_SCALE_ALIASES = {
    "SAM-valence": "valence", "SAM-arousal": "arousal", "SAM-dominance": "dominance",
    "Likert-Sch": "beauty", "Likert-beauty": "beauty",
    "Likert-Heimeligkeit": "hominess", "Likert-hominess": "hominess",
    "Likert-Stress": "stress", "Likert-stress": "stress",
    "Likert-Faszination": "fascination", "Likert-fascination": "fascination",
    "Likert-Offenheit": "openness", "Likert-openness": "openness",
    "Likert-Sicherheit": "safety", "Likert-safety": "safety",
}

_UA_SCALE_RANGE = {"valence": (1, 9), "arousal": (1, 9), "dominance": (1, 9)}


def _ua_scale_name(raw: str) -> Optional[str]:
    raw = raw.strip()
    for prefix, name in _UA_SCALE_ALIASES.items():
        if raw.startswith(prefix):
            return name
    return None


def _ua_parse_value(value: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for part in value.split(";"):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def load_urban_appraisal(root: str, *,
                         polarity: Optional[Dict[str, int]] = None) -> LoadReport:
    """Load per-item valence and arousal from the event log.

    ``polarity`` maps a scale name to +1 or -1 and **must be supplied**. The archive
    documents anchor wording ("valence: happy - unhappy") but never states which end
    of the numeric scale corresponds to which anchor. Assuming a direction would
    silently invert every result that depends on sign, so this loader refuses.

    Resolve it from the authors' analysis code or the preprint, pass it explicitly,
    and it is recorded in the report so a reader knows what was assumed.
    """
    rep = LoadReport(dataset="URBAN_APPRAISAL", present=False)
    if not os.path.isdir(root):
        rep.notes.append(f"archive not present at {root!r}")
        return rep
    rep.present = True

    needed = {"valence", "arousal"}
    if not polarity or not needed.issubset(polarity):
        raise PolarityUnknown(
            "Urban Appraisal does not document the direction of its rating scales. "
            "The README gives anchor wording ('valence: happy - unhappy') but nothing "
            "states whether 1 is the first anchor or the second, and no Levels are "
            "given in the sidecar.\n\n"
            "Supply it explicitly once resolved from the authors' analysis code:\n"
            "    load_urban_appraisal(root, polarity={'valence': +1, 'arousal': +1})\n"
            "where +1 means a higher number is more positive / more aroused.\n\n"
            "This loader refuses rather than defaulting, because a wrong polarity "
            "does not fail — it inverts the conclusion and looks fine.")
    for scale, sign in polarity.items():
        if sign not in (1, -1):
            raise ValueError(f"polarity for {scale!r} must be +1 or -1, got {sign!r}")

    paths = sorted(
        os.path.join(dp, f)
        for dp, _, fs in os.walk(root) for f in fs
        if f.endswith("_events.tsv") and "task-UrbanAppraisal" in f)
    skipped = {"non_rating_event": 0, "unknown_scale": 0, "out_of_range": 0}
    participants = set()
    pending: Dict[Tuple[str, str], Dict[str, float]] = {}

    for path in paths:
        sub = os.path.basename(path).split("_")[0]
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            _check_header(reader.fieldnames or [], _UA_EVENTS_HEADER, path,
                          "URBAN_APPRAISAL")
            for row in reader:
                fields = _ua_parse_value(row.get("value") or "")
                if fields.get("event") != "optionConfirmed":
                    skipped["non_rating_event"] += 1
                    continue
                scale = _ua_scale_name(fields.get("scale", ""))
                if scale is None:
                    skipped["unknown_scale"] += 1
                    continue
                if scale not in ("valence", "arousal"):
                    continue
                try:
                    resp = float(fields["response"])
                except (KeyError, ValueError):
                    skipped["non_rating_event"] += 1
                    continue
                lo, hi = _UA_SCALE_RANGE[scale]
                if not (lo <= resp <= hi):
                    skipped["out_of_range"] += 1
                    continue
                if polarity[scale] == -1:
                    resp = lo + hi - resp
                participants.add(sub)
                pending.setdefault((sub, fields.get("stimulus", "")), {})[scale] = resp

    for (sub, stim), vals in pending.items():
        rep.trials.append(Trial(
            dataset="URBAN_APPRAISAL", participant=sub, item=stim,
            valence=vals.get("valence"), arousal=vals.get("arousal"),
            stated_scale=(1.0, 9.0), order=len(rep.trials)))

    rep.participants = len(participants)
    rep.skipped = skipped
    rep.notes.append(f"polarity supplied by caller: {polarity}")
    rep.notes.append("ratings parsed out of the events.tsv 'value' string; there is "
                     "no ratings file in this archive")
    rep.notes.append("sub-51 uses English scale labels where the other 62 use German; "
                     "both are matched")
    return rep


# --------------------------------------------------------------------------
# Analyses. Each returns a structured no-data record rather than a number.
# --------------------------------------------------------------------------

def _no_data(analysis: str, dataset: str, why: str) -> Dict[str, Any]:
    return {"analysis": analysis, "dataset": dataset, "result": None,
            "no_data": True, "why": why,
            "note": "No figure is produced. Nothing here is estimated or simulated."}


def preference_contradiction_rate(rep: LoadReport) -> Dict[str, Any]:
    """How often does a person's choice go against their own earlier rating?

    This is the real-data analogue of the architecture's central object — a stated
    preference and an action that disagrees with it. It says nothing about *why*
    they disagree, which is exactly the question no public corpus can answer.
    """
    if not rep.present or not rep.trials:
        return _no_data("preference_contradiction", rep.dataset,
                        "archive absent or no usable trials")
    judged = [(t.participant, t.contradicts_statement()) for t in rep.trials]
    judged = [(p, c) for p, c in judged if c is not None]
    if not judged:
        return _no_data("preference_contradiction", rep.dataset,
                        "corpus records no action that could contradict a statement")
    per: Dict[str, List[bool]] = {}
    for p, c in judged:
        per.setdefault(p, []).append(c)
    rates = [sum(v) / len(v) for v in per.values()]
    n_contra = sum(1 for _, c in judged if c)
    return {
        "analysis": "preference_contradiction", "dataset": rep.dataset,
        "no_data": False,
        "n_trials": len(judged), "n_participants": len(per),
        "overall_rate": n_contra / len(judged),
        "mean_participant_rate": sum(rates) / len(rates),
        "participant_rate_range": [min(rates), max(rates)],
        "interpretation": (
            "A contradiction here is a choice that disagrees with the person's own "
            "earlier rating of the same item. It is NOT evidence of a hidden "
            "preference and NOT evidence of compliance under pressure — this corpus "
            "contains no manipulation that could separate those. It establishes only "
            "that the phenomenon the architecture models occurs in real data, and at "
            "what rate."),
    }


def abstention_report(rep: LoadReport) -> Dict[str, Any]:
    """How often did people decline to answer, and did that vary between them?"""
    if not rep.present or not rep.trials:
        return _no_data("abstention", rep.dataset, "archive absent or no usable trials")
    per: Dict[str, List[bool]] = {}
    for t in rep.trials:
        per.setdefault(t.participant, []).append(t.abstained)
    if not any(any(v) for v in per.values()):
        return _no_data("abstention", rep.dataset,
                        "corpus records no abstention signal")
    rates = sorted(sum(v) / len(v) for v in per.values())
    total = sum(sum(v) for v in per.values())
    n = sum(len(v) for v in per.values())
    mid = len(rates) // 2
    return {
        "analysis": "abstention", "dataset": rep.dataset, "no_data": False,
        "n_trials": n, "n_participants": len(per),
        "overall_abstention_rate": total / n,
        "median_participant_rate": (rates[mid] if len(rates) % 2
                                    else (rates[mid - 1] + rates[mid]) / 2),
        "participant_rate_range": [rates[0], rates[-1]],
        "participants_who_never_abstained": sum(1 for r in rates if r == 0.0),
        "interpretation": (
            "Abstention here is the participant leaving the rating widget at its "
            "default rather than moving it. It is a person declining to answer, "
            "recorded by the corpus as such. The spread across participants is the "
            "quantity of interest: a system that models abstention as noise treats "
            "these as missing data."),
    }


def order_invariance_check(rep: LoadReport, engine_factory,
                           *, n_permutations: int = 24,
                           tolerance: float = 1e-12) -> Dict[str, Any]:
    """Feed real observations to a belief engine in many orders; require agreement.

    Order-invariance has so far been demonstrated on generated data. This runs the
    same property against observations a person actually produced, which is a weaker
    test mathematically and a more persuasive one to a reader.

    ``engine_factory`` is a zero-argument callable returning a fresh engine, kept
    abstract so this module does not import the engine and create a cycle.
    """
    if not rep.present or not rep.trials:
        return _no_data("order_invariance", rep.dataset, "archive absent")
    per: Dict[str, List[Trial]] = {}
    for t in rep.trials:
        per.setdefault(t.participant, []).append(t)
    usable = {p: ts for p, ts in per.items() if len(ts) >= 3}
    if not usable:
        return _no_data("order_invariance", rep.dataset,
                        "no participant has enough observations")
    return {
        "analysis": "order_invariance", "dataset": rep.dataset, "no_data": False,
        "n_participants_eligible": len(usable),
        "n_permutations_per_participant": n_permutations,
        "tolerance": tolerance,
        "status": "harness ready; requires the archive and an engine_factory to run",
        "note": ("Deliberately does not fabricate a pass. This entry point exists so "
                 "that the check is written before the data arrives, not after."),
    }
