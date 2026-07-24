"""Core data types for Shadow Mirror.

Everything is timestamped and normalised to [0, 1]. Nothing here interprets;
these are just the honest records of what was observed.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Literal


# Two hidden axes, plus a derived "reactivity" bookkeeping axis.
Axis = Literal["knowledge", "desire"]

# Where a signal comes from. These are treated very differently by the engine:
# self_report is what you *say*; performance is what you can *do*; behaviour is
# what you actually *do*; implicit is an indirect approach/avoidance task;
# physiological is arousal-like data (used ONLY as a threat confound, never as
# evidence of desire).
SignalType = Literal[
    "self_report",       # stated confidence / stated want, 0..1
    "task_performance",  # measured performance on a knowledge task, 0..1
    "implicit_task",     # indirect approach/avoidance tendency, 0..1
    "behavior",          # observed approach behaviour, 0..1
    "physiological",     # arousal proxy, 0..1  (threat confound only)
    "avoidance",         # observed avoidance behaviour, 0..1 (threat confound)
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp01(x: float) -> float:
    """Clamp to [0, 1]. Everything the engine sees lives in this range."""
    return max(0.0, min(1.0, float(x)))


@dataclass
class Observation:
    """A single, dated piece of evidence on one axis from one signal type.

    ``topic`` scopes inference: readings about "algebra" and "public speaking"
    are kept separate rather than blended into one meaningless average.
    ``reliability`` (0..1) says how much to trust this particular datum -- a
    rigorous task score should outweigh a casual self-rating.
    """

    axis: Axis
    signal_type: SignalType
    value: float
    topic: str = "general"
    context: str = ""
    reliability: float = 1.0
    timestamp: str = field(default_factory=_now_iso)

    def __post_init__(self) -> None:
        self.value = clamp01(self.value)
        self.reliability = clamp01(self.reliability)
        self.topic = self.topic or "general"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Observation":
        return cls(
            axis=d["axis"],
            signal_type=d["signal_type"],
            value=d["value"],
            topic=d.get("topic", "general"),
            context=d.get("context", ""),
            reliability=d.get("reliability", 1.0),
            timestamp=d.get("timestamp", _now_iso()),
        )


@dataclass
class BeliefState:
    """A dated posterior snapshot -- explicitly *not* a biography.

    ``knowledge`` and ``desire`` are probability distributions over hypotheses.
    ``uncertainty`` is 0 (sharp) .. 1 (basically no idea). ``threat_prob`` is the
    first-class "threat-response, not preference" hypothesis for the desire axis.
    """

    knowledge: Dict[str, float]
    desire: Dict[str, float]
    threat_prob: float
    uncertainty: float
    n_observations: int
    timestamp: str = field(default_factory=_now_iso)

    def top_knowledge(self) -> str:
        return max(self.knowledge, key=self.knowledge.get)

    def top_desire(self) -> str:
        return max(self.desire, key=self.desire.get)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BeliefState":
        return cls(
            knowledge=d["knowledge"],
            desire=d["desire"],
            threat_prob=d["threat_prob"],
            uncertainty=d["uncertainty"],
            n_observations=d.get("n_observations", 0),
            timestamp=d.get("timestamp", _now_iso()),
        )


# The four clean epistemic states (Feedback A's reformulation of the original
# double-negative 4x4). Order matters only for stable display.
KNOWLEDGE_HYPOTHESES = (
    "explicit_knowledge",    # believes they know, and they do
    "explicit_uncertainty",  # knows that they do not know
    "latent_knowledge",      # can't report it, but performance contains it
    "blind_spot",            # confident but not supported by performance
)

# Desire states + two first-class alternatives that refuse to force a "want":
#   ambivalence     -- the signals genuinely conflict / oscillate; the doubleness
#                      IS the fact, held up un-collapsed (the humane core move).
#   threat_response -- arousal + avoidance is a threat signal, never a want.
DESIRE_HYPOTHESES = (
    "explicit_attraction",   # says want, acts toward
    "explicit_aversion",     # says don't want, acts away
    "latent_approach",       # doesn't endorse, yet acts toward
    "latent_avoidance",      # endorses, yet acts away
    "ambivalence",           # wants and doesn't want at once; not resolved
    "threat_response",       # arousal + avoidance: a threat signal, not a want
)

# The four *directional* desire states that live on the (want, action) plane.
# ambivalence and threat_response are injected separately, not as corners.
DIRECTIONAL_DESIRE = (
    "explicit_attraction",
    "explicit_aversion",
    "latent_approach",
    "latent_avoidance",
)
