"""The safety layer: detect confounds and suppress over-interpretation.

This layer exists because the failure modes of a tool like this are not edge
cases -- they are the default outcome if unguarded. Each flag maps to a specific
warning in your concept documents:

* ``threat_response``   -- the trauma landmine. Arousal + avoidance must never be
                           read as hidden desire.
* ``low_evidence``      -- the ground-truth paradox. With too little data, refuse.
* ``instability``       -- the fluidity problem. States move by the hour; this is
                           a snapshot, not a biography.
* ``reactivity``        -- the Heisenberg effect. Looking at the mirror changes
                           what it measures; the more you check, the louder we say so.
* ``high_uncertainty``  -- honest ignorance; down-weight everything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:  # avoid a circular import at runtime
    from .engine import ShadowMirror


# Thresholds are deliberately cautious: this instrument should under-claim.
THREAT_THRESHOLD = 0.45
UNCERTAINTY_THRESHOLD = 0.65
INSTABILITY_THRESHOLD = 0.35
# After this many reflections, we start actively reminding about reactivity.
REACTIVITY_SOFT_CAP = 5


@dataclass
class SafetyReport:
    flags: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    suppress_interpretation: bool = False

    def add(self, flag: str, message: str, suppress: bool = False) -> None:
        self.flags.append(flag)
        self.messages.append(message)
        if suppress:
            self.suppress_interpretation = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flags": list(self.flags),
            "messages": list(self.messages),
            "suppress_interpretation": self.suppress_interpretation,
        }


def assess_safety(mirror: "ShadowMirror", topic=None) -> SafetyReport:
    report = SafetyReport()
    belief = mirror.current(topic)

    if belief is None:
        report.add(
            "low_evidence",
            "Not enough evidence to infer. Interpretation withheld on purpose.",
            suppress=True,
        )
        return report

    # 1. Trauma landmine. This is the one to protect hardest.
    if belief.threat_prob >= THREAT_THRESHOLD:
        report.add(
            "threat_response",
            "Signals here fit a threat-response at least as well as a preference. "
            "High arousal plus avoidance is NOT evidence of hidden wanting. Do not "
            "read this as 'you secretly want it'.",
        )

    # 1b. v0.4 (D-19): partial observation of the confound channels. Without
    # both arousal and avoidance we cannot separate a hidden preference from a
    # threat response, so the system refuses that reading rather than guessing.
    if getattr(belief, "guard_coverage", "full") != "full" and \
            belief.desire.get("unresolved_approach", 0.0) > 0.15:
        report.add(
            "insufficient_confound_coverage",
            "Your behaviour leans toward something you say you don't want, but "
            "arousal and avoidance were not both observed -- so a hidden "
            "preference cannot be told apart from a threat response. No hidden "
            "want is being asserted. Logging an arousal or avoidance observation "
            "would resolve this.",
        )

    # 1c. v0.4: none of the named hypotheses fit the evidence.
    if max(belief.knowledge.get("unmodelled", 0.0),
           belief.desire.get("unmodelled", 0.0)) >= 0.40:
        report.add(
            "unmodelled",
            "The evidence does not sit close to any hypothesis this instrument "
            "holds. That is a limit of the instrument, not a fact about you.",
            suppress=True,
        )

    # 2. Honest ignorance.
    if belief.uncertainty >= UNCERTAINTY_THRESHOLD:
        report.add(
            "high_uncertainty",
            "Uncertainty is high; treat the most-likely label as a weak guess only.",
            suppress=True,
        )

    # 3. Fluidity -- snapshot, not biography.
    if mirror._instability(topic) >= INSTABILITY_THRESHOLD:
        report.add(
            "instability",
            "Your recent snapshots disagree with each other. This is a moment, not "
            "a trait -- expect it to move again.",
        )

    # 4. Reactivity / Heisenberg. Grows with how often the mirror is consulted.
    n_reflections = mirror.n_reflections()
    if n_reflections >= REACTIVITY_SOFT_CAP:
        report.add(
            "reactivity",
            f"You have consulted this {n_reflections} times. Seeing a guess changes "
            "later answers and can become self-fulfilling. Hold results loosely.",
        )

    return report
