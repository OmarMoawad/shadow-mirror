"""The inference layer: a small, deterministic Bayesian model.  **v0.4**

Design choices, and why:

* **Discrete hypotheses, not a made-up "true self" score.** Each axis has a few
  named hypotheses (see ``models.py``). We compute a posterior *distribution*
  over them. There is deliberately no single number claiming who you are.

* **Likelihood by corners, accumulated over observations.** Each *directional*
  hypothesis predicts where evidence should land in a small feature space (e.g.
  blind-spot predicts high stated confidence but low performance). Each
  observation contributes its own weighted Gaussian log-likelihood, so the
  posterior genuinely sharpens as evidence accumulates.  *(v0.4 -- fixes D-08,
  where a single likelihood was evaluated at the weighted centroid and the
  posterior was therefore bit-identical at n = 2 and n = 100.)*

* **An explicit "none of these fit" hypothesis.** ``unmodelled`` carries a flat
  likelihood, so when the evidence sits far from every corner the honest answer
  wins instead of the nearest wrong one. This is what stops the engine becoming
  confident precisely when its model of you is wrong.  *(v0.4)*

* **The guard refuses rather than degrades.** ``latent_approach`` -- the reading
  that says "you want this even though you say you don't" -- is the one reading
  that requires ruling out a threat response. It is therefore only assertable
  when both confound channels (arousal, avoidance) are actually observed.
  Otherwise the mass moves to ``unresolved_approach`` and the system says so.
  *(v0.4 -- fixes D-19, where an absent channel was silently read as evidence of
  safety and the guard's sensitivity fell to zero.)*

* **Weighted evidence.** Each observation carries a ``reliability`` and decays
  with age (configurable half-life). An observation whose weight has decayed
  below ``EPS_WEIGHT`` no longer counts toward sufficiency -- stale evidence
  stops being evidence.  *(v0.4 -- fixes D-12.)*

* **Topic scoping, honestly.** Belief history is kept *per topic*, so
  instability means "this topic moved", not "you changed subject".  *(v0.4 --
  fixes D-11.)*

* **An injectable clock.** Inference is a pure function of the observations and
  the clock, so results are reproducible and testable.  *(v0.4 -- fixes D-21.)*

* **The weights are not empirically validated.** They encode the *shape* of the
  hypotheses, not calibrated truths about people. Every output is a question.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Sequence, Tuple

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

# Minimum *usable* paired evidence before we will infer at all on an axis.
MIN_EVIDENCE = 2

# An observation whose weight has decayed below this no longer counts as
# evidence. At any half-life this is roughly 4.3 half-lives of age.
EPS_WEIGHT = 0.05

# Spread of the likelihood bumps. Larger => softer, more uncertain posteriors.
_SIGMA = 0.28

# Flat likelihood of the ``unmodelled`` component. It is calibrated as the
# likelihood a hypothesis would have if the evidence sat ``_UNMODELLED_DISTANCE``
# away from its corner *in the two-dimensional feature space*. 0.32 is
# approximately half the distance between adjacent corners, so evidence landing
# beyond the midpoint between hypotheses is better explained by "none of these"
# than by the nearest one. The 2-D distance is split evenly across the two
# channel observations that make up a pair.
_UNMODELLED_DISTANCE = 0.32
_UNMODELLED_PRIOR = 0.10

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

# Guard coverage states. Only ``full`` permits asserting latent_approach.
COVERAGE_FULL = "full"
COVERAGE_AROUSAL_ONLY = "arousal_only"
COVERAGE_AVOIDANCE_ONLY = "avoidance_only"
COVERAGE_NONE = "none"


def _log_kernel(v: float, c: float) -> float:
    """Log of the (unnormalised) Gaussian kernel for one observation, one axis."""
    return -((v - c) ** 2) / (2.0 * _SIGMA * _SIGMA)


def _normalize(probs: Dict[str, float]) -> Dict[str, float]:
    total = sum(probs.values())
    if total <= 0:
        return {k: 1.0 / len(probs) for k in probs}
    return {k: v / total for k, v in probs.items()}


def _softmax_from_logs(log_scores: Dict[str, float]) -> Dict[str, float]:
    """Numerically stable normalisation of log-space scores."""
    if not log_scores:
        return {}
    m = max(log_scores.values())
    exp_scores = {k: math.exp(v - m) for k, v in log_scores.items()}
    return _normalize(exp_scores)


def _entropy_fraction(probs: Dict[str, float]) -> float:
    """Shannon entropy normalised to [0, 1] (1 == maximally uncertain)."""
    n = len(probs)
    if n <= 1:
        return 0.0
    ent = -sum(p * math.log(p + 1e-12) for p in probs.values() if p > 0)
    return min(1.0, ent / math.log(n))


def _weighted_mean(pairs: Sequence[Tuple[float, float]]) -> Optional[float]:
    tw = sum(w for _, w in pairs)
    if tw <= 0:
        return None
    return sum(v * w for v, w in pairs) / tw


def _weighted_spread(pairs: Sequence[Tuple[float, float]]) -> float:
    """Weighted standard deviation. v0.4: dispersion now respects decay and
    reliability, where v0.3.0 used an unweighted population stdev (D-12)."""
    tw = sum(w for _, w in pairs)
    if tw <= 0 or len(pairs) < 2:
        return 0.0
    mu = sum(v * w for v, w in pairs) / tw
    var = sum(w * (v - mu) ** 2 for v, w in pairs) / tw
    return math.sqrt(max(0.0, var))


def _lag1_autocorrelation(pairs: Sequence[Tuple[float, float]]) -> float:
    """Lag-1 autocorrelation of a time-ordered series, in [-1, 1].

    Strongly negative means the series alternates -- toward, away, toward -- which
    is what ambivalence looks like. Near zero means independent noise. Positive
    means monotonic drift, i.e. someone changing their mind across the window,
    which is the *opposite* of holding two positions at once.

    v1.0 (D-29): ambivalence was previously computed from dispersion alone, and
    dispersion is identical for all three. Measured consequence: genuine
    oscillation read as ambivalence 100% of the time, but so did 95.5% of pure
    noise and 98.8% of monotonic drift -- 34% precision, with two of every three
    ambivalence readings wrong.
    """
    vals = [v for v, _ in pairs]
    n = len(vals)
    if n < 3:
        return 0.0
    mu = sum(vals) / n
    denom = sum((v - mu) ** 2 for v in vals)
    if denom <= 1e-12:
        return 0.0
    num = sum((vals[i] - mu) * (vals[i + 1] - mu) for i in range(n - 1))
    return max(-1.0, min(1.0, num / denom))


def _oscillation_gate(pairs_a: Sequence[Tuple[float, float]],
                      pairs_b: Sequence[Tuple[float, float]]) -> float:
    """1.0 when the streams alternate, 0.0 when they drift or merely scatter."""
    acf = (_lag1_autocorrelation(pairs_a) + _lag1_autocorrelation(pairs_b)) / 2.0
    return max(0.0, min(1.0, (-acf - 0.20) / 0.45))


def _usable(pairs: Sequence[Tuple[float, float]]) -> int:
    """How many observations still carry meaningful weight."""
    return sum(1 for _, w in pairs if w >= EPS_WEIGHT)


class ShadowMirror:
    """A self-owned reflective engine. One instance == one person's mirror."""

    def __init__(self, prior_knowledge: Optional[Dict[str, float]] = None,
                 prior_desire: Optional[Dict[str, float]] = None,
                 half_life_days: float = _DEFAULT_HALF_LIFE_DAYS,
                 clock: Optional[Callable[[], datetime]] = None) -> None:
        self.observations: List[Observation] = []
        # v0.4 (D-11): history is per topic. "__pooled__" holds topic=None reads.
        self.belief_history: Dict[str, List[BeliefState]] = {}
        self._pending = 0                      # writes since the last consultation
        self._dirty: set = set()
        self.half_life_days = max(0.0, float(half_life_days))
        # v0.4 (D-21): injectable clock makes inference reproducible.
        self.clock: Callable[[], datetime] = clock or (lambda: datetime.now(timezone.utc))
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
        # v1.1 (D-28): writing an observation no longer triggers a full belief
        # recompute. Session 7 measured the old path at 3.8x per doubling --
        # quadratic in the number of observations, 27 ms at 100 evidence pairs
        # and 1121 ms at 800 -- because every write recomputed every belief.
        # The belief is now computed when the mirror is *consulted*, which is
        # also the more honest reading of the reactivity counter: it should
        # count how often someone looked, not how often they logged.
        self._pending += 1
        self._dirty.add(self._key(topic))
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
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - ts).total_seconds() / 86400.0)
        decay = 0.5 ** (age_days / self.half_life_days)
        return obs.reliability * decay

    def _wvals(self, axis: Axis, signal_type: SignalType, topic: Optional[str],
               now: datetime) -> List[Tuple[float, float]]:
        return [(o.value, self._weight(o, now)) for o in self.observations
                if o.axis == axis and o.signal_type == signal_type
                and (topic is None or o.topic == topic)]

    # -- likelihood --------------------------------------------------------
    @staticmethod
    def _accumulate(corners: Dict[str, Tuple[float, float]],
                    prior: Dict[str, float],
                    channel_a: Sequence[Tuple[float, float]],
                    channel_b: Sequence[Tuple[float, float]]
                    ) -> Tuple[Dict[str, float], float]:
        """Evidence-weighted log-likelihood per hypothesis, plus ``unmodelled``.

        For a location model with known observation noise, the weighted mean is
        the sufficient statistic and the precision of that estimate grows with
        the total evidence weight W. The log-likelihood of hypothesis h is
        therefore ``-W * (mean - corner)^2 / (2*sigma^2)`` per channel: the
        posterior sharpens as evidence accumulates (fixing D-08), while the
        hypothesis-independent scatter term is left out.

        Leaving scatter out matters for the ``unmodelled`` component. "None of
        these hypotheses fit" should mean *the centre of your evidence is not
        near any of them*, not *your readings are noisy* -- noise is already
        carried by the dispersion term in the uncertainty estimate. Charging
        observation noise against the named hypotheses but not against
        ``unmodelled`` would make the instrument abstain purely because a person
        answers inconsistently, which is a different finding entirely.
        """
        w_a = sum(w for _, w in channel_a)
        w_b = sum(w for _, w in channel_b)
        total_w = w_a + w_b
        mean_a = _weighted_mean(channel_a)
        mean_b = _weighted_mean(channel_b)
        denom = 2.0 * _SIGMA * _SIGMA

        log_scores: Dict[str, float] = {}
        for h, (cx, cy) in corners.items():
            ll = 0.0
            if mean_a is not None:
                ll += -w_a * ((mean_a - cx) ** 2) / denom
            if mean_b is not None:
                ll += -w_b * ((mean_b - cy) ** 2) / denom
            log_scores[h] = math.log(max(prior.get(h, 1e-9), 1e-12)) + ll

        # "None of these hypotheses fit": the likelihood a hypothesis would have
        # if the evidence centre sat _UNMODELLED_DISTANCE away from its corner in
        # the two-dimensional feature space, split evenly across the channels.
        half_sq = (_UNMODELLED_DISTANCE ** 2) / 2.0
        log_scores["unmodelled"] = (math.log(_UNMODELLED_PRIOR)
                                    - (w_a + w_b) * half_sq / denom)
        return _softmax_from_logs(log_scores), total_w

    # -- inference ---------------------------------------------------------
    def _infer_knowledge(self, topic: Optional[str], now: datetime
                         ) -> Tuple[Dict[str, float], float, int, float]:
        conf = self._wvals("knowledge", "self_report", topic, now)
        perf = self._wvals("knowledge", "task_performance", topic, now)
        n = min(_usable(conf), _usable(perf))
        if n < MIN_EVIDENCE:
            base = dict(self.prior_knowledge)
            base["unmodelled"] = 0.0
            return _normalize(base), 1.0, n, 0.0

        post, total_w = self._accumulate(_KNOWLEDGE_CORNERS, self.prior_knowledge,
                                         conf, perf)
        dispersion = (_weighted_spread(conf) + _weighted_spread(perf)) / 2.0
        thin = max(0.0, (4 - n) / 4.0)
        misfit = post.get("unmodelled", 0.0)
        unc = min(1.0, 0.40 * _entropy_fraction(post) + 0.15 * dispersion
                  + 0.10 * thin + 0.35 * misfit)
        return post, unc, n, total_w

    def _guard_coverage(self, arousal: Sequence, avoidance: Sequence) -> str:
        has_ar = _usable(arousal) > 0
        has_av = _usable(avoidance) > 0
        if has_ar and has_av:
            return COVERAGE_FULL
        if has_ar:
            return COVERAGE_AROUSAL_ONLY
        if has_av:
            return COVERAGE_AVOIDANCE_ONLY
        return COVERAGE_NONE

    @staticmethod
    def _threat_confound_score(coverage: str, ar: Optional[float],
                               av: Optional[float]) -> Optional[float]:
        """Raw, gate-facing threat-confound score in [0, 1], or None if unknowable.

        v0.4 (D-19): an unobserved channel is *not* imputed as zero. With only
        one channel the score is computed from that channel alone, on its own
        scale; with neither, it is ``None`` and the caller must refuse rather
        than assume safety.
        """
        if coverage == COVERAGE_FULL:
            return 1.0 / (1.0 + math.exp(-4.0 * ((ar or 0.0) + (av or 0.0) - 1.1)))
        if coverage == COVERAGE_AROUSAL_ONLY:
            return 1.0 / (1.0 + math.exp(-6.0 * ((ar or 0.0) - 0.60)))
        if coverage == COVERAGE_AVOIDANCE_ONLY:
            return 1.0 / (1.0 + math.exp(-6.0 * ((av or 0.0) - 0.60)))
        return None

    def _infer_desire(self, topic: Optional[str], now: datetime
                      ) -> Tuple[Dict[str, float], float, Optional[float], int, str]:
        explicit = self._wvals("desire", "self_report", topic, now)
        implicit = self._wvals("desire", "implicit_task", topic, now)
        behavior = self._wvals("desire", "behavior", topic, now)
        arousal = self._wvals("desire", "physiological", topic, now)
        avoidance = self._wvals("desire", "avoidance", topic, now)

        action_pairs = ([(v, w * 0.6) for v, w in behavior]
                        + [(v, w * 0.4) for v, w in implicit])
        n = min(_usable(explicit), max(_usable(behavior), _usable(implicit)))
        coverage = self._guard_coverage(arousal, avoidance)

        if n < MIN_EVIDENCE or not action_pairs:
            base = {h: 1.0 for h in DIRECTIONAL_DESIRE}
            base.update({"ambivalence": 0.0, "threat_response": 0.0,
                         "unresolved_approach": 0.0, "unmodelled": 0.0})
            return _normalize(base), 1.0, None, n, coverage

        post, total_w = self._accumulate(_DESIRE_CORNERS, self.prior_desire,
                                         explicit, action_pairs)
        raw_misfit = post.pop("unmodelled", 0.0)

        # --- Ambivalence: the signals oscillate/conflict. The doubleness IS the
        # fact -- so we refuse to collapse it into a directional "want".
        oscillation = (_weighted_spread(explicit) + _weighted_spread(action_pairs)) / 2.0
        # v1.0 (D-29): dispersion says how spread the readings are; it does not say
        # whether they alternate. Ambivalence is a claim that they alternate, so it
        # is gated on temporal structure as well as spread.
        ambivalence = min(0.9, 2.2 * oscillation) * _oscillation_gate(explicit, action_pairs)

        # v0.4: oscillating evidence sits far from every *directional* corner, so
        # accumulation reads it as model misfit. But ambivalence is precisely the
        # hypothesis that explains oscillation -- counting it twice would let
        # "none of these fit" swallow the one state that does fit. Misfit is
        # therefore discounted by however much ambivalence already accounts for.
        misfit = raw_misfit * (1.0 - min(0.95, ambivalence))

        # --- Trauma-aware threat confound (first-class hypothesis). ---
        ar = _weighted_mean(arousal)
        av = _weighted_mean(avoidance)
        threat_score = self._threat_confound_score(coverage, ar, av)
        threat_mass = threat_score if threat_score is not None else 0.0

        carve = 1.0 - min(0.95, ambivalence + 0.6 * threat_mass)
        full = {h: post.get(h, 0.0) * carve for h in DIRECTIONAL_DESIRE}
        full["latent_approach"] *= (1.0 - 0.5 * threat_mass)

        # --- v0.4 (D-19): the refusal. "You want this despite saying you don't"
        # is the one reading that requires ruling out a threat response, so it
        # may only be asserted when both confound channels were actually
        # observed. Otherwise the mass becomes an explicit unresolved state.
        if coverage != COVERAGE_FULL:
            full["unresolved_approach"] = full.get("latent_approach", 0.0)
            full["latent_approach"] = 0.0
        else:
            full["unresolved_approach"] = 0.0

        full["ambivalence"] = ambivalence
        # v1.0 (D-24): under partial coverage the threat *caution* still fires --
        # it lives in threat_confound_score and in the safety flags -- but the
        # threat hypothesis is not allowed to win the posterior. One channel can
        # raise a question; it cannot settle one. Arousal alone does not separate
        # fear from excitement, and labelling excitement a threat response was
        # costing 33 points of specificity under the Session 2 ablation.
        full["threat_response"] = threat_mass if coverage == COVERAGE_FULL else 0.0
        full["unmodelled"] = misfit
        full = _normalize(full)

        thin = max(0.0, (4 - n) / 4.0)
        unc = min(1.0, 0.40 * _entropy_fraction(full) + 0.15 * oscillation
                  + 0.10 * thin + 0.35 * misfit)
        if coverage != COVERAGE_FULL:
            unc = min(1.0, unc + 0.10)     # honest penalty for partial observation
        return full, unc, threat_score, n, coverage

    # -- history -----------------------------------------------------------
    @staticmethod
    def _key(topic: Optional[str]) -> str:
        return topic if topic is not None else "__pooled__"

    def _instability(self, topic: Optional[str] = None) -> float:
        """How much the last few snapshots *of this topic* have moved.

        v0.4 (D-11): computed within a topic. In v0.3.0 a single global history
        mixed topics, so alternating between two stable topics reported spurious
        instability.
        """
        hist = self.belief_history.get(self._key(topic), [])
        if len(hist) < 3:
            return 0.0
        recent = hist[-4:]
        tops = [max(b.knowledge.values()) for b in recent]
        mean = sum(tops) / len(tops)
        var = sum((t - mean) ** 2 for t in tops) / len(tops)
        return min(1.0, math.sqrt(var) * 2.0)

    def _compute(self, topic: Optional[str]) -> Optional[BeliefState]:
        now = self.clock()
        k_post, k_unc, k_n, _k_w = self._infer_knowledge(topic, now)
        d_post, d_unc, threat_score, d_n, coverage = self._infer_desire(topic, now)

        active = []
        if k_n >= MIN_EVIDENCE:
            active.append(k_unc)
        if d_n >= MIN_EVIDENCE:
            active.append(d_unc)
        if not active:
            return None

        uncertainty = min(1.0, max(active) + 0.2 * self._instability(topic))
        n_obs = sum(1 for o in self.observations if topic is None or o.topic == topic)
        return BeliefState(
            knowledge=k_post, desire=d_post,
            threat_prob=(threat_score if threat_score is not None else 0.0),
            uncertainty=uncertainty, n_observations=n_obs,
            threat_confound_score=threat_score,
            guard_coverage=coverage,
        )

    def _update(self, topic: Optional[str] = None) -> Optional[BeliefState]:
        """Recompute the scoped belief and append a snapshot for trend tracking."""
        belief = self._compute(topic)
        if belief is not None:
            self.belief_history.setdefault(self._key(topic), []).append(belief)
        return belief

    def current(self, topic: Optional[str] = None) -> Optional[BeliefState]:
        """Current belief. ``topic=None`` means *pooled across all topics*.

        This is where the arithmetic happens. Consulting the mirror records a
        snapshot; logging an observation does not (D-28).
        """
        belief = self._compute(topic)
        if belief is not None:
            key = self._key(topic)
            hist = self.belief_history.setdefault(key, [])
            if not hist or hist[-1].timestamp != belief.timestamp:
                hist.append(belief)
                if len(hist) > 64:             # bounded; instability uses the last 4
                    del hist[:-64]
            self._dirty.discard(key)
        return belief

    def n_reflections(self) -> int:
        """How many times a belief has been formed, whether by write or by read.

        Kept as a counter rather than derived from history length so that the
        reactivity caution behaves identically after the lazy-recompute change
        (D-28): the number of times the mirror has been engaged is unchanged, only
        the moment of arithmetic moved.
        """
        return self._pending + sum(len(v) for v in self.belief_history.values())

    def evidence_pairs(self, topic: Optional[str] = None) -> Tuple[int, int]:
        """(knowledge_pairs, desire_pairs) of *usable* paired evidence per axis.

        v0.4 (D-12): counts only observations whose decayed weight is still
        meaningful, so decade-old evidence no longer passes the gate.
        """
        now = self.clock()

        def usable(axis, sig):
            return _usable(self._wvals(axis, sig, topic, now))

        k_n = min(usable("knowledge", "self_report"),
                  usable("knowledge", "task_performance"))
        d_n = min(usable("desire", "self_report"),
                  max(usable("desire", "behavior"), usable("desire", "implicit_task")))
        return k_n, d_n

    def effective_evidence(self, topic: Optional[str] = None) -> Dict[str, float]:
        """Total decayed, reliability-weighted evidence mass per channel."""
        now = self.clock()
        out = {}
        for axis, sig in (("knowledge", "self_report"), ("knowledge", "task_performance"),
                          ("desire", "self_report"), ("desire", "behavior"),
                          ("desire", "implicit_task"), ("desire", "physiological"),
                          ("desire", "avoidance")):
            pairs = self._wvals(axis, sig, topic, now)
            if pairs:
                out[f"{axis}.{sig}"] = round(sum(w for _, w in pairs), 4)
        return out

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
            # v0.4 (D-09): two distinct quantities, two distinct names. The
            # safety gate keys on threat_confound_score; the posterior mass is
            # the threat hypothesis's share after normalisation against the
            # directional readings. They are not the same number, and v0.3.0
            # reported both under near-identical labels.
            desire["threat_confound_score"] = (
                None if belief.threat_confound_score is None
                else round(belief.threat_confound_score, 3))
            desire["p_threat_response"] = round(belief.desire.get("threat_response", 0.0), 3)
            desire["guard_coverage"] = belief.guard_coverage
            if belief.guard_coverage != COVERAGE_FULL:
                desire["guard_note"] = (
                    "Both arousal and avoidance are required to tell a hidden "
                    "preference apart from a threat response. Without them this "
                    "reading is reported as 'unresolved_approach' and no hidden "
                    "want is asserted."
                )
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
            "effective_evidence": self.effective_evidence(topic),
            "safety": safety.to_dict(),
            "disclaimer": (
                "This is a dated, uncertain hypothesis about signal tension -- "
                "not a statement about who you are. It is meant to be questioned."
            ),
        }
