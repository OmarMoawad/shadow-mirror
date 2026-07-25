"""Emotion-Will-Knowledge: three observable streams, and the tensions between them.

What this does **not** do: infer a latent psychological state, a trait, a
personality, an upbringing, or a protected characteristic. It compares three
streams of *observable* evidence and reports where they disagree. A disagreement
is a question, not a diagnosis.

  Emotion (E)   -- self-reported or measured affective load
  Will (W)      -- persistence, effort, stated objectives, behavioural choices
  Knowledge (K) -- task performance, demonstrated competence

The v1.0 prototype's ``detect_tension`` required ``K > 0.7 and W < 0.3``, or
``E > 0.7 and K < 0.3``, or ``|K - W| > 0.5``. Its own flagship demonstration
(K = 0.30, W = 0.75, E = 0.80 -- a student working hard, distressed, and not
getting results) missed all three rules by a hair and printed "No significant
tension detected". A detector that cannot fire on the example written to
demonstrate it is not a detector (D-13).

Tensions are now continuous magnitudes over the unit square, so a case that is
clearly a tension registers as one, and borderline cases register as borderline
instead of vanishing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import fmean
from typing import Dict, List, Optional, Sequence, Tuple

#: A tension is reported when its magnitude reaches this. Chosen so that a
#: stream pair disagreeing by roughly 0.6 on a 0-1 scale registers.
TENSION_THRESHOLD = 0.35

#: Minimum observations per stream before any tension is computed.
MIN_PER_STREAM = 2


@dataclass
class Tension:
    name: str
    magnitude: float
    streams: Tuple[str, ...]
    question: str

    def to_dict(self) -> Dict[str, object]:
        return {"name": self.name, "magnitude": round(self.magnitude, 3),
                "streams": list(self.streams), "question": self.question}


@dataclass
class EWKReading:
    emotion: Optional[float]
    will: Optional[float]
    knowledge: Optional[float]
    n: Dict[str, int]
    tensions: List[Tension] = field(default_factory=list)
    status: str = "ok"

    def to_dict(self) -> Dict[str, object]:
        return {
            "status": self.status,
            "streams": {"emotion": self.emotion, "will": self.will,
                        "knowledge": self.knowledge},
            "observations_per_stream": dict(self.n),
            "tensions": [t.to_dict() for t in self.tensions],
            "disclaimer": (
                "These are discrepancies between observed streams, not claims "
                "about an inner state. Each one is a question."
            ),
        }


def _mean(vals: Sequence[float]) -> Optional[float]:
    return fmean(vals) if vals else None


class EWKProfile:
    """Three streams in, disagreements out."""

    def __init__(self, urg=None) -> None:
        self.urg = urg
        self.streams: Dict[str, List[float]] = {"emotion": [], "will": [], "knowledge": []}

    def observe(self, stream: str, value: float) -> None:
        if stream not in self.streams:
            raise ValueError(f"unknown stream {stream!r}")
        self.streams[stream].append(min(1.0, max(0.0, float(value))))

    def observe_many(self, rows: Sequence[Tuple[str, float]]) -> None:
        for s, v in rows:
            self.observe(s, v)

    def read(self, window: int = 8) -> EWKReading:
        e = _mean(self.streams["emotion"][-window:])
        w = _mean(self.streams["will"][-window:])
        k = _mean(self.streams["knowledge"][-window:])
        n = {s: len(v[-window:]) for s, v in self.streams.items()}

        if any(n[s] < MIN_PER_STREAM for s in ("emotion", "will", "knowledge")):
            return EWKReading(e, w, k, n, status="insufficient_evidence")

        tensions: List[Tension] = []

        def consider(name: str, magnitude: float, streams: Tuple[str, ...], question: str) -> None:
            if magnitude >= TENSION_THRESHOLD:
                tensions.append(Tension(name, magnitude, streams, question))

        consider(
            "effort_without_return", w * (1.0 - k), ("will", "knowledge"),
            "You are putting in real effort and it is not showing up in results. "
            "Is the effort going somewhere the task doesn't reward, or is "
            "something missing further back?",
        )
        consider(
            "confidence_without_persistence", k * (1.0 - w), ("knowledge", "will"),
            "You can do this, and you keep stepping away from it. What happens in "
            "the moments just before you stop?",
        )
        consider(
            "distress_without_return", e * (1.0 - k), ("emotion", "knowledge"),
            "This is costing you a lot emotionally and not paying back in results. "
            "What would it take to make that trade look different?",
        )
        consider(
            "distress_under_effort", e * w, ("emotion", "will"),
            "You are pushing hard and it is hard on you. Is this a sprint you have "
            "an end date for, or has it become the normal condition?",
        )
        consider(
            "stream_divergence", abs(k - w), ("knowledge", "will"),
            "What you can do and what you are doing have come apart. Which of the "
            "two would you trust more right now?",
        )

        tensions.sort(key=lambda t: -t.magnitude)
        reading = EWKReading(e, w, k, n, tensions=tensions)

        if self.urg is not None and tensions:
            for t in tensions:
                self.urg.add_node("Hypothesis", {
                    "kind": "ewk_tension", **t.to_dict(),
                    "belief": None,
                })
        return reading
