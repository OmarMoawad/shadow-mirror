"""Inquiry planning by expected information gain.

The v1.0 prototype scored inquiries as ``expected_benefit = 1 - gap``, where
``gap`` was the difference between two *prior* beliefs. That quantity does not
depend on the candidate observation at all, so the planner carried no signal
about which observation to seek. Session 2 measured it against an
information-theoretic oracle: normalised regret 0.579 [0.547, 0.612] versus
random selection's 0.550 [0.515, 0.584] -- indistinguishable from choosing at
random -- and 1.000 when hypotheses were well separated, because it stayed silent
exactly when a discriminating observation was most valuable (D-22).

This module computes the real thing: the mutual information between a candidate
observation's outcome and the hypothesis variable, under the current posterior.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

_EPS = 1e-12


@dataclass
class CandidateObservation:
    """Something the person could go and find out.

    ``likelihoods[h]`` is P(this observation comes back positive | hypothesis h).
    ``cost`` is whatever the person is spending: minutes, discomfort, money.
    """
    name: str
    likelihoods: Dict[str, float]
    cost: float = 1.0
    method: str = ""

    def clamp(self) -> "CandidateObservation":
        return CandidateObservation(
            self.name,
            {h: min(1.0 - 1e-6, max(1e-6, p)) for h, p in self.likelihoods.items()},
            self.cost, self.method,
        )


@dataclass
class Inquiry:
    """A proposed observation, with the justification Invariant VIII requires."""
    description: str
    motivation: str
    expected_information_gain: float
    gain_per_unit_cost: float
    targets: List[str] = field(default_factory=list)
    method: str = ""
    inquiry_id: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "inquiry_id": self.inquiry_id,
            "description": self.description,
            "motivation": self.motivation,
            "expected_information_gain_bits": round(self.expected_information_gain / math.log(2), 4),
            "gain_per_unit_cost": round(self.gain_per_unit_cost, 4),
            "targets": list(self.targets),
            "suggested_method": self.method,
        }


def entropy(probs: Sequence[float]) -> float:
    return -sum(p * math.log(p + _EPS) for p in probs if p > 0)


def expected_information_gain(posterior: Dict[str, float],
                              candidate: CandidateObservation) -> float:
    """Mutual information, in nats, between the outcome and the hypothesis."""
    c = candidate.clamp()
    hs = [h for h in posterior if h in c.likelihoods]
    if len(hs) < 2:
        return 0.0
    total = sum(posterior[h] for h in hs)
    if total <= 0:
        return 0.0
    pri = {h: posterior[h] / total for h in hs}

    h_prior = entropy([pri[h] for h in hs])
    p_pos = sum(pri[h] * c.likelihoods[h] for h in hs)
    gain = h_prior
    for outcome, p_out in ((1, p_pos), (0, 1.0 - p_pos)):
        if p_out <= _EPS:
            continue
        post = []
        for h in hs:
            lik = c.likelihoods[h] if outcome == 1 else 1.0 - c.likelihoods[h]
            post.append(pri[h] * lik / p_out)
        gain -= p_out * entropy(post)
    return max(0.0, gain)


class InquiryPlanner:
    """Rank candidate observations by how much they would actually resolve."""

    def __init__(self, urg=None) -> None:
        self.urg = urg
        self.history: List[Inquiry] = []

    def plan(self, posterior: Dict[str, float],
             candidates: Sequence[CandidateObservation],
             top_k: int = 3,
             min_gain_bits: float = 0.01) -> List[Inquiry]:
        """Return the most informative candidates, best first.

        Unlike the belief-gap heuristic this never goes silent because the
        hypotheses look settled: a confidently-held wrong hypothesis is exactly
        when a discriminating observation is worth most, and the information gain
        says so on its own.
        """
        scored: List[Inquiry] = []
        for cand in candidates:
            gain = expected_information_gain(posterior, cand)
            if gain / math.log(2) < min_gain_bits:
                continue
            targets = sorted(
                (h for h in cand.likelihoods if h in posterior),
                key=lambda h: -posterior[h],
            )[:4]
            inq = Inquiry(
                description=f"Find out: {cand.name}",
                motivation=(
                    f"Would resolve {gain / math.log(2):.2f} bits of the "
                    f"{entropy(list(posterior.values())) / math.log(2):.2f} bits "
                    f"currently unsettled across {len(posterior)} hypotheses."
                ),
                expected_information_gain=gain,
                gain_per_unit_cost=gain / max(1e-9, cand.cost),
                targets=targets,
                method=cand.method or cand.name,
            )
            scored.append(inq)

        scored.sort(key=lambda i: -i.expected_information_gain)
        chosen = scored[:top_k]

        if self.urg is not None:
            for inq in chosen:
                nid = self.urg.add_node("Inquiry", inq.to_dict())
                inq.inquiry_id = nid
                self.urg.update_node(nid, inquiry_id=nid)
                for t in inq.targets:
                    if t in self.urg:
                        self.urg.add_edge(nid, t, "targets",
                                          expected_information_gain=inq.expected_information_gain)
        self.history.extend(chosen)
        return chosen

    def best_value_for_cost(self, posterior: Dict[str, float],
                            candidates: Sequence[CandidateObservation]) -> Optional[Inquiry]:
        plans = self.plan(posterior, candidates, top_k=len(candidates))
        if not plans:
            return None
        return max(plans, key=lambda i: i.gain_per_unit_cost)
