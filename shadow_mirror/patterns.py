"""Reaction patterns over time: first reaction, counter-pattern, emotion-as-cause.

This is the module that does the thing you actually described: read a person's
**first reaction** to a recurring condition, then watch how, as encounters
accumulate, that reaction can invert into a **counter-pattern** -- and treat the
**emotion as the antecedent cause that bends the behaviour**, not as an
afterthought.

The science it leans on (see the design notes / README):

* **Appraisal theory.** A condition is appraised; the appraisal *is* the emotion;
  the emotion carries an **action tendency** (fear -> freeze/flee, anger ->
  approach, disgust -> avoid, joy -> engage). So emotion is modelled upstream of
  behaviour -- the cause that bends it. Appraisals are idiographic: the same
  condition evokes different emotions in different people, so everything here is
  per-subject, never a group template.
* **Idiographic EMA / state-transition modelling.** Dense, per-person sampling of
  the same condition over time is the established way to see reactions *change* --
  e.g. how negative affect rises after interpersonal conflict, differently for
  each person. A counter-pattern is a state transition in that per-person series.
* **Affective-computing humility.** Implicit and physiological signals are
  valuable precisely because they are hard to fake -- but they have high
  person-to-person variance and are easy to over-read. So every output here is a
  dated, uncertain **hypothesis**, and the trauma guard (arousal + avoidance is
  *threat*, not hidden want) is carried over intact.

Nothing in this file collects data. It only analyses encounters that a consenting
subject's grant has already authorised (see ``consent.py`` / ``study.py``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from statistics import mean, pstdev
from typing import Any, Dict, List, Optional, Tuple

from .models import clamp01

# --- gates & thresholds (deliberately cautious; this should under-claim) -----
MIN_ENCOUNTERS = 2          # below this, we say nothing about a pattern
COUNTER_PATTERN_MIN = 4     # below this, a "reversal" is called tentative, not claimed
BAND = 0.12                 # neutral deadband around 0.5 for direction
FLIP_MARGIN = 0.20          # minimum early->late swing to count as a reversal
AROUSAL_HI = 0.60           # arousal above this + avoidance => threat candidate


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Encounter:
    """One dated instance of a subject meeting a recurring condition.

    ``valence`` (0 = very negative .. 1 = very positive) and ``arousal`` are the
    **emotion** -- the appraised, antecedent state. ``action`` (0 = full
    withdrawal .. 1 = full approach) is the behaviour that follows. ``stream``
    records which *consented* data stream this came from, so provenance -- and
    therefore consent -- is auditable on every single datum.
    """

    subject_id: str
    condition: str
    valence: float
    arousal: float
    action: float
    stream: str = "self_report"
    context: str = ""
    reliability: float = 1.0
    timestamp: str = field(default_factory=_now_iso)

    def __post_init__(self) -> None:
        self.valence = clamp01(self.valence)
        self.arousal = clamp01(self.arousal)
        self.action = clamp01(self.action)
        self.reliability = clamp01(self.reliability)
        self.condition = self.condition or "general"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Encounter":
        return cls(
            subject_id=d["subject_id"],
            condition=d.get("condition", "general"),
            valence=d["valence"],
            arousal=d.get("arousal", 0.5),
            action=d["action"],
            stream=d.get("stream", "self_report"),
            context=d.get("context", ""),
            reliability=d.get("reliability", 1.0),
            timestamp=d.get("timestamp", _now_iso()),
        )


# --- reaction states ---------------------------------------------------------
# A reaction is placed on the (valence x action) plane the appraisal literature
# implies: how it *felt* crossed with which way it *moved*. The "override" and
# "inhibited" corners are the interesting ones -- feeling and action disagree.
def _dir(x: float) -> int:
    if x > 0.5 + BAND:
        return 1
    if x < 0.5 - BAND:
        return -1
    return 0


def reaction_state(valence: float, action: float, arousal: float = 0.5) -> str:
    """Name the reaction. A threat overlay pre-empts a 'preference' reading."""
    v, a = _dir(valence), _dir(action)
    # Threat comes first: high arousal + moving away + feeling bad is a safety
    # signal, and must not be quietly relabelled as 'they just don't want it'.
    if arousal >= AROUSAL_HI and a < 0 and v <= 0:
        return "threat_withdrawal"
    table = {
        (1, 1): "appetitive_approach",     # feels good, moves toward  (congruent)
        (1, -1): "appetitive_inhibited",   # feels good, yet pulls back (inhibition)
        (-1, -1): "aversive_avoid",        # feels bad, moves away      (congruent)
        (-1, 1): "aversive_override",      # feels bad, pushes through  (bracing)
    }
    if (v, a) in table:
        return table[(v, a)]
    if v == 0 and a == 0:
        return "neutral"
    return "mixed"


def _pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    """Plain Pearson r, or None when it would be undefined (no variance)."""
    n = len(xs)
    if n < 3:
        return None
    mx, my = mean(xs), mean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return max(-1.0, min(1.0, cov / (sx * sy)))


def _strength(r: float) -> str:
    a = abs(r)
    if a >= 0.6:
        return "strong"
    if a >= 0.3:
        return "moderate"
    return "weak"


@dataclass
class PatternReading:
    """A dated, uncertain hypothesis about how a reaction moved over time.

    Explicitly NOT a verdict about the person. It answers: what was the first
    reaction, did it invert, and -- if it did -- was the driver a change in the
    *emotion* or a change in how that emotion *bends the behaviour*?
    """

    condition: str
    n_encounters: int
    first_reaction: Optional[str]
    latest_reaction: Optional[str]
    counter_pattern: bool
    kind: str                 # none | behavior_reversal | emotion_reversal | both
    driver: str               # emotion_shift | coupling_shift | both | unclear | n/a
    coupling: Dict[str, Any]  # how emotion appears to bend behaviour (hypothesis)
    threat_flag: bool
    uncertainty: float
    tentative: bool           # True when we have < COUNTER_PATTERN_MIN encounters
    questions: List[str]
    timestamp: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _insufficient(condition: str, n: int) -> PatternReading:
    return PatternReading(
        condition=condition, n_encounters=n, first_reaction=None,
        latest_reaction=None, counter_pattern=False, kind="none", driver="n/a",
        coupling={"status": "insufficient_evidence"}, threat_flag=False,
        uncertainty=1.0, tentative=True,
        questions=[
            f"Only {n} encounter(s) logged for '{condition}'. That is not enough to "
            "say anything about a pattern yet -- and refusing to guess from one or "
            "two moments is deliberate. What happened the next time it came up?"
        ],
    )


def analyze(encounters: List[Encounter]) -> PatternReading:
    """Turn a subject's encounters with ONE condition into a pattern hypothesis."""
    if not encounters:
        return _insufficient("general", 0)
    condition = encounters[0].condition
    seq = sorted(encounters, key=lambda e: e.timestamp)
    n = len(seq)
    if n < MIN_ENCOUNTERS:
        return _insufficient(condition, n)

    vals = [e.valence for e in seq]
    acts = [e.action for e in seq]
    arous = [e.arousal for e in seq]

    first = reaction_state(seq[0].valence, seq[0].action, seq[0].arousal)
    latest = reaction_state(seq[-1].valence, seq[-1].action, seq[-1].arousal)

    # Early vs late windows (split by time order). We compare the halves rather
    # than first-vs-last points so a single noisy encounter can't fake a reversal.
    half = max(1, n // 2)
    early_v, late_v = mean(vals[:half]), mean(vals[-half:])
    early_a, late_a = mean(acts[:half]), mean(acts[-half:])

    behavior_reversal = (
        _dir(early_a) != 0 and _dir(late_a) != 0
        and _dir(early_a) != _dir(late_a)
        and abs(late_a - early_a) >= FLIP_MARGIN
    )
    emotion_reversal = (
        _dir(early_v) != 0 and _dir(late_v) != 0
        and _dir(early_v) != _dir(late_v)
        and abs(late_v - early_v) >= FLIP_MARGIN
    )
    counter = behavior_reversal or emotion_reversal

    if behavior_reversal and emotion_reversal:
        kind, driver = "both", "both"
    elif behavior_reversal:
        kind = "behavior_reversal"
        # Behaviour flipped but feeling held ~steady => the SAME emotion now bends
        # the behaviour the other way. That is a coupling shift, and it is the
        # most interesting case: the person learned/adapted, not "changed heart".
        driver = "coupling_shift" if abs(late_v - early_v) < FLIP_MARGIN else "both"
    elif emotion_reversal:
        kind = "emotion_reversal"
        driver = "emotion_shift"
    else:
        kind, driver = "none", "n/a"

    # Emotion-as-cause: does feeling predict the move, for THIS person, HERE?
    r_va = _pearson(vals, acts)      # +: better feeling -> more approach
    r_aa = _pearson(arous, acts)     # -: more arousal   -> more withdrawal (threat-like)
    coupling: Dict[str, Any] = {}
    if r_va is None and r_aa is None:
        coupling["status"] = "insufficient_evidence"
    else:
        coupling["status"] = "ok"
        if r_va is not None:
            coupling["valence_to_action"] = round(r_va, 3)
            coupling["valence_reading"] = (
                f"{_strength(r_va)} {'appetitive' if r_va >= 0 else 'paradoxical'} "
                "coupling: feeling "
                + ("better goes with approaching" if r_va >= 0
                   else "better goes with pulling back")
            )
        if r_aa is not None:
            coupling["arousal_to_action"] = round(r_aa, 3)
            coupling["arousal_reading"] = (
                f"{_strength(r_aa)} coupling: higher arousal goes with "
                + ("approaching" if r_aa >= 0 else "withdrawing")
            )

    # Threat guard: if the LATE window is high-arousal withdrawal while feeling
    # bad, an apparent "turned into avoidance" counter-pattern must be read as
    # became-unsafe, never as a revealed dislike.
    late_arousal = mean(arous[-half:])
    threat_flag = (late_arousal >= AROUSAL_HI and _dir(late_a) < 0 and late_v <= 0.5)

    # Uncertainty: thin data, noisy halves, and short series all raise it.
    thin = max(0.0, (COUNTER_PATTERN_MIN - n) / COUNTER_PATTERN_MIN)
    noise = (pstdev(vals) + pstdev(acts)) / 2.0 if n > 1 else 0.5
    uncertainty = min(1.0, 0.45 * thin + 0.55 * min(1.0, noise * 2.0))
    tentative = n < COUNTER_PATTERN_MIN

    questions = _questions(condition, seq, first, latest, counter, kind, driver,
                           coupling, threat_flag, tentative)
    return PatternReading(
        condition=condition, n_encounters=n, first_reaction=first,
        latest_reaction=latest, counter_pattern=counter, kind=kind, driver=driver,
        coupling=coupling, threat_flag=threat_flag, uncertainty=round(uncertainty, 3),
        tentative=tentative, questions=questions,
    )


_STATE_PLAIN = {
    "appetitive_approach": "felt good and moved toward it",
    "appetitive_inhibited": "felt good but held back",
    "aversive_avoid": "felt bad and moved away",
    "aversive_override": "felt bad but pushed through anyway",
    "threat_withdrawal": "showed a safety response -- activated, and turning away",
    "neutral": "was fairly flat",
    "mixed": "was mixed / hard to place",
}


def _questions(condition, seq, first, latest, counter, kind, driver, coupling,
               threat_flag, tentative) -> List[str]:
    d0, d1 = seq[0].timestamp[:10], seq[-1].timestamp[:10]
    out: List[str] = []

    # Threat always leads, and survives everything else -- the trauma landmine.
    if threat_flag:
        out.append(
            f"[{d1}] Around '{condition}', the later reactions look like a safety "
            "response -- high arousal and turning away -- more than a change of "
            "preference. If this is a person you are studying with their consent, the "
            "honest question is what made it feel unsafe, not what they 'really want'."
        )

    hedge = "tentatively, " if tentative else ""
    out.append(
        f"[{d0}] The first reaction to '{condition}' {hedge}{_STATE_PLAIN.get(first, first)}. "
        "First reactions are a single moment -- what would you want to check before "
        "trusting it as the baseline?"
    )

    if counter:
        if driver == "coupling_shift":
            out.append(
                f"[{d0}->{d1}] {hedge.capitalize() if hedge else ''}The behaviour toward "
                f"'{condition}' inverted while the underlying feeling stayed close to the "
                "same. That points to the SAME emotion coming to bend the behaviour the "
                "other way -- adaptation or learning, not a changed heart. What changed "
                "between the early encounters and the later ones?"
            )
        elif driver == "emotion_shift":
            out.append(
                f"[{d0}->{d1}] {hedge.capitalize() if hedge else ''}The feeling about "
                f"'{condition}' itself flipped over time, and the behaviour followed it. "
                "What experiences in between might have re-appraised the whole situation?"
            )
        elif driver == "both":
            out.append(
                f"[{d0}->{d1}] {hedge.capitalize() if hedge else ''}Both the feeling and "
                f"the behaviour around '{condition}' reversed. Did the feeling move first "
                "and drag the behaviour, or the other way round?"
            )
    else:
        out.append(
            f"[{d1}] No clear counter-pattern for '{condition}' yet -- the latest reaction "
            f"({_STATE_PLAIN.get(latest, latest)}) is broadly consistent with the first. "
            "Consistency across encounters can be real, or can just mean not enough have "
            "been seen. Which do you suspect?"
        )

    if coupling.get("status") == "ok":
        readings = [coupling[k] for k in ("valence_reading", "arousal_reading")
                    if k in coupling]
        if readings:
            out.append(
                "[emotion-as-cause] For this person under this condition: "
                + "; ".join(readings)
                + ". This is a correlation in a small sample, not a proven mechanism -- "
                "hold it as a hypothesis to test, not a fact."
            )

    out.append(
        "None of the above is a conclusion about anyone. It is one dated, uncertain "
        "reading of how a reaction moved. What would the subject themselves say back to it?"
    )
    return out
