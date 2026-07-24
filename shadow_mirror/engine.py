"""The inference layer: a small, deterministic Bayesian model.

Design choices, and why:

* **Discrete hypotheses, not a made-up "true self" score.** Each axis has a few
  named hypotheses (see ``models.py``). We compute a posterior *distribution*
  over them. There is deliberately no single number claiming who you are.

* **Likelihood by corners.** Each *directional* hypothesis predicts where evidence
  should land in a small feature space (e.g. blind-spot predicts high stated
  confidence but low performance). Its likelihood is a Gaussian bump around that
  corner; posterior = prior x likelihood, normalised. Two non-directional desire
  hypotheses are injected on top: ``ambivalence`` (the signals oscillate/conflict
  -- the doubleness is the fact) and ``threat_response`` (arousal + avoidance).

* **Weighted evidence.** Each observation carries a ``reliability`` (trust it more
  or less) and decays with age (a configurable half-life), so stale readings stop
  dominating -- a snapshot, not a biography.

* **Topic scoping.** Evidence is grouped by ``topic`` so "algebra" and "public
  speaking" never blend into one meaningless average.

* **Honest uncertainty.** Uncertainty rises when evidence is sparse, when signals
  disagree, and when recent snapshots are unstable. It is reported, not hidden.

* **The weights are not empirically validated.** They encode the *shape* of the
  hypotheses, not calibrated truths about people. Every output is a question.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from statistics import pstdev
from typing import Dict, List, Optional, Sequence, Tuple

from .models import (
    Axis,
    BeliefState,
    DESIRE_HYPOTHESES,
    DIRECTIONAL_DESIRE,
    KNOWLEDGE_HYPOTHESES,
    Observation,
    SignalType,
)
from .safety import SafetyReport, assess_safety

# Minimum paired evidence before we will infer at all on an axis.
MIN_EVIDENCE = 2

# Spread of the likelihood bumps. Larger => softer, more uncertain posteriors.
_SIGMA = 0.28

# Default half-life for temporal decay of evidence.
_DEFAULT_HALF_LIFE_DAYS = 30.0

# Predicted (feature-A, feature-B) corner for each hypothesis, in [0,1]^2.
_KNOWLEDGE_CORNERS: Dict[str, Tuple[float, float]] = {
    "explicit_knowledge": (0.85, 0.85),   # (stated_confidence, task_performance)
    "explicit_uncertainty": (0.15, 0.20),
    "latent_knowledge": (0.25, 0.80),
    "blind_spot": (0.85, 0.25),
}

_DESIRE_CORNERS: Dict[str, Tuple[float, float]] = {
    "explicit_attraction": (0.85, 0.85),   # (explicit_want, action_tendency)
    "explicit_aversion": (0.15, 0.15),
    "latent_approach": (0.20, 0.80),
    "latent_avoidance": (0.80, 0.20),
}


def _gaussian(a: float, b: float, corner: Tuple[float, float], sigma: float) -> float:
    cx, cy = corner
    d2 = (a - cx) ** 2 + (b - cy) ** 2
    return math.exp(-d2 / (2.0 * sigma * sigma))


def _normalize(probs: Dict[str, float]) -> Dict[str, float]:
    total = sum(probs.values())
    if total <= 0:
        return {k: 1.0 / len(probs) for k in probs}
    return {k: v / total for k, v in probs.items()}


def _entropy_fraction(probs: Dict[str, float]) -> float:
    """Shannon entropy normalised to [0, 1] (1 == maximally uncertain)."""
    n = len(probs)
    if n <= 1:
        return 0.0
    ent = -sum(p * math.log(p + 1e-12) for p in probs.values() if p > 0)
    return min(1.0, ent / math.log(n))


class ShadowMirror:
    """A self-owned reflective engine. One instance == one person's mirror."""

    def __init__(self, prior_knowledge: Optional[Dict[str, float]] = None,
                 prior_desire: Optional[Dict[str, float]] = None,
                 half_life_days: float = _DEFAULT_HALF_LIFE_DAYS) -> None:
        self.observations: List[Observation] = []
        self.belief_history: List[BeliefState] = []
        self.half_life_days = max(0.0, float(half_life_days))
        # Flat priors by default: we start by assuming nothing.
        self.prior_knowledge = _normalize(
            prior_knowledge or {h: 1.0 for h in KNOWLEDGE_HYPOTHESES}
        )
        self.prior_desire = _normalize(
            prior_desire or {h: 1.0 for h in DIRECTIONAL_DESIRE}
        )

    # -- observation intake ------------------------------------------------
    def add(self, axis: Axis, signal_type: SignalType, value: float,
            topic: str = "general", context: str = "",
            reliability: float = 1.0) -> Observation:
        obs = Observation(axis=axis, signal_type=signal_type, value=value,
                          topic=topic, context=context, reliability=reliability)
        self.observations.append(obs)
        self._update(topic)
        return obs

    def add_batch(self, rows: Sequence[Tuple]) -> None:
        """Each row: (axis, signal_type, value[, topic[, context[, reliability]]])."""
        for row in rows:
            axis, signal_type, value = row[0], row[1], row[2]
            topic = row[3] if len(row) > 3 else "general"
            context = row[4] if len(row) > 4 else ""
            reliability = row[5] if len(row) > 5 else 1.0
            self.add(axis, signal_type, value, topic, context, reliability)

    def topics(self) -> List[str]:
        seen = []
        for o in self.observations:
            if o.topic not in seen:
                seen.append(o.topic)
        return seen

    # -- weighting ---------------------------------------------------------
    def _weight(self, obs: Observation, now: datetime) -> float:
        """reliability x temporal decay. Recent, trusted evidence weighs most."""
        if self.half_life_days <= 0:
            return obs.reliability
        try:
            ts = datetime.fromisoformat(obs.timestamp)
        except (ValueError, TypeError):
            return obs.reliability
        age_days = max(0.0, (now - ts).total_seconds() / 86400.0)
        decay = 0.5 ** (age_days / self.half_life_days)
        return obs.reliability * decay

    def _wvals(self, axis: Axis, signal_type: SignalType, topic: Optional[str],
               now: datetime) -> List[Tuple[float, float]]:
        return [(o.value, self._weight(o, now)) for o in self.observations
                if o.axis == axis and o.signal_type == signal_type
                and (topic is None or o.topic == topic)]

    @staticmethod
    def _wmean(pairs: List[Tuple[float, float]]) -> Optional[float]:
        tw = sum(w for _, w in pairs)
        if tw <= 0:
            return None
        return sum(v * w for v, w in pairs) / tw

    @staticmethod
    def _spread(pairs: List[Tuple[float, float]]) -> float:
        vals = [v for v, _ in pairs]
        return pstdev(vals) if len(vals) > 1 else 0.0

    # -- inference ---------------------------------------------------------
    def _infer_knowledge(self, topic: Optional[str], now: datetime
                         ) -> Tuple[Dict[str, float], float, int]:
        conf = self._wvals("knowledge", "self_report", topic, now)
        perf = self._wvals("knowledge", "task_performance", topic, now)
        n = min(len(conf), len(perf))
        if n < MIN_EVIDENCE:
            return dict(self.prior_knowledge), 1.0, n

        a, b = self._wmean(conf), self._wmean(perf)
        post = {h: self.prior_knowledge[h] * _gaussian(a, b, corner, _SIGMA)
                for h, corner in _KNOWLEDGE_CORNERS.items()}
        post = _normalize(post)

        dispersion = (self._spread(conf) + self._spread(perf)) / 2.0
        thin = max(0.0, (4 - n) / 4.0)
        unc = min(1.0, 0.6 * _entropy_fraction(post) + 0.25 * dispersion + 0.15 * thin)
        return post, unc, n

    def _infer_desire(self, topic: Optional[str], now: datetime
                      ) -> Tuple[Dict[str, float], float, float, int]:
        explicit = self._wvals("desire", "self_report", topic, now)
        implicit = self._wvals("desire", "implicit_task", topic, now)
        behavior = self._wvals("desire", "behavior", topic, now)
        arousal = self._wvals("desire", "physiological", topic, now)
        avoidance = self._wvals("desire", "avoidance", topic, now)

        n = min(len(explicit), max(len(behavior), len(implicit)))
        if not (explicit and (behavior or implicit)) or n < MIN_EVIDENCE:
            base = _normalize({h: 1.0 for h in DIRECTIONAL_DESIRE})
            base["ambivalence"] = 0.0
            base["threat_response"] = 0.0
            return _normalize(base), 1.0, 0.0, n

        e = self._wmean(explicit)
        parts = []
        if behavior:
            parts.append((self._wmean(behavior), 0.6))
        if implicit:
            parts.append((self._wmean(implicit), 0.4))
        action = sum(v * w for v, w in parts) / sum(w for _, w in parts)

        post = {h: self.prior_desire[h] * _gaussian(e, action, corner, _SIGMA)
                for h, corner in _DESIRE_CORNERS.items()}
        post = _normalize(post)

        # --- Ambivalence: the signals oscillate/conflict. The doubleness IS the
        # fact -- so we refuse to collapse it into a directional "want". Driven by
        # within-signal swing over time (want-and-don't-want) rather than by a
        # single low/high reading.
        oscillation = (self._spread(explicit) + self._spread(behavior)) / 2.0
        ambivalence = min(0.9, 2.2 * oscillation)

        # --- Trauma-aware threat confound (first-class hypothesis). ---
        ar = self._wmean(arousal) if arousal else 0.0
        av = self._wmean(avoidance) if avoidance else 0.0
        threat_prob = (1.0 / (1.0 + math.exp(-4.0 * (ar + av - 1.1)))
                       if (arousal or avoidance) else 0.0)

        # Both ambivalence and threat carve mass away from the directional read,
        # and threat specifically suppresses the "you secretly want this" reading.
        carve = 1.0 - min(0.95, ambivalence + 0.6 * threat_prob)
        full = {h: post[h] * carve for h in post}
        full["latent_approach"] *= (1.0 - 0.5 * threat_prob)
        full["ambivalence"] = ambivalence
        full["threat_response"] = threat_prob
        full = _normalize(full)

        dispersion = (self._spread(explicit) + self._spread(behavior)) / 2.0
        thin = max(0.0, (4 - n) / 4.0)
        unc = min(1.0, 0.6 * _entropy_fraction(full) + 0.25 * dispersion + 0.15 * thin)
        return full, unc, threat_prob, n

    def _instability(self) -> float:
        """How much the last few snapshots have moved. High => snapshot, not trend."""
        if len(self.belief_history) < 3:
            return 0.0
        recent = self.belief_history[-4:]
        tops = [max(b.knowledge.values()) for b in recent]
        return min(1.0, (pstdev(tops) if len(tops) > 1 else 0.0) * 2.0)

    def _compute(self, topic: Optional[str]) -> Optional[BeliefState]:
        now = datetime.now(timezone.utc)
        k_post, k_unc, k_n = self._infer_knowledge(topic, now)
        d_post, d_unc, threat, d_n = self._infer_desire(topic, now)

        active = []
        if k_n >= MIN_EVIDENCE:
            active.append(k_unc)
        if d_n >= MIN_EVIDENCE:
            active.append(d_unc)
        if not active:
            return None

        uncertainty = min(1.0, max(active) + 0.2 * self._instability())
        n_obs = sum(1 for o in self.observations if topic is None or o.topic == topic)
        return BeliefState(
            knowledge=k_post, desire=d_post, threat_prob=threat,
            uncertainty=uncertainty, n_observations=n_obs,
        )

    def _update(self, topic: Optional[str] = None) -> Optional[BeliefState]:
        """Recompute the scoped belief and append a snapshot for trend tracking."""
        belief = self._compute(topic)
        if belief is not None:
            self.belief_history.append(belief)
        return belief

    def current(self, topic: Optional[str] = None) -> Optional[BeliefState]:
        if topic is not None:
            return self._compute(topic)
        return self.belief_history[-1] if self.belief_history else None

    def evidence_pairs(self, topic: Optional[str] = None) -> Tuple[int, int]:
        """(knowledge_pairs, desire_pairs) of usable paired evidence per axis."""
        def count(axis, sig):
            return sum(1 for o in self.observations if o.axis == axis
                       and o.signal_type == sig
                       and (topic is None or o.topic == topic))
        k_n = min(count("knowledge", "self_report"),
                  count("knowledge", "task_performance"))
        d_n = min(count("desire", "self_report"),
                  max(count("desire", "behavior"), count("desire", "implicit_task")))
        return k_n, d_n

    # -- reporting ---------------------------------------------------------
    def safety(self, topic: Optional[str] = None) -> SafetyReport:
        return assess_safety(self, topic=topic)

    def report(self, topic: Optional[str] = None) -> Dict[str, object]:
        """A full, honest snapshot: beliefs + safety flags + provenance."""
        belief = self.current(topic)
        if belief is None:
            return {
                "status": "insufficient_evidence",
                "message": (
                    f"Need at least {MIN_EVIDENCE} paired observations on an axis "
                    "before this will infer anything. That refusal is a feature."
                ),
                "topic": topic,
                "n_observations": sum(1 for o in self.observations
                                      if topic is None or o.topic == topic),
            }
        safety = self.safety(topic)
        k_n, d_n = self.evidence_pairs(topic)

        knowledge = {"evidence_pairs": k_n}
        if k_n >= MIN_EVIDENCE:
            knowledge["posterior"] = {k: round(v, 3) for k, v in belief.knowledge.items()}
            knowledge["most_likely"] = belief.top_knowledge()
        else:
            knowledge["status"] = "insufficient_evidence"

        desire = {"evidence_pairs": d_n}
        if d_n >= MIN_EVIDENCE:
            desire["posterior"] = {k: round(v, 3) for k, v in belief.desire.items()}
            desire["most_likely"] = belief.top_desire()
            desire["threat_response_probability"] = round(belief.threat_prob, 3)
        else:
            desire["status"] = "insufficient_evidence"

        return {
            "status": "ok",
            "topic": topic or "general",
            "timestamp": belief.timestamp,
            "n_observations": belief.n_observations,
            "knowledge": knowledge,
            "desire": desire,
            "uncertainty": round(belief.uncertainty, 3),
            "safety": safety.to_dict(),
            "disclaimer": (
                "This is a dated, uncertain hypothesis about signal tension -- "
                "not a statement about who you are. It is meant to be questioned."
            ),
        }
