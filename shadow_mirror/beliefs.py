"""Belief revision over hypotheses in a URG.

Bayesian conditioning on conditionally independent observations is commutative:
updating with p then q gives the same posterior as q then p (Jacobs, 2025,
*Commutativity of probabilistic belief revision*, Frontiers in Cognition, DOI
10.3389/fcogn.2025.1623227). Human belief revision is *not* commutative -- recency
and priming are real -- but that is a fact about people, not a licence for the
arithmetic to be order-dependent.

The v1.0 prototype clamped the posterior to [0.01, 0.99] *inside the state* after
every update. Clamping is not invertible: once pinned at 0.99, the information
about how far past 0.99 the evidence pushed is destroyed, and later contrary
evidence starts from the wrong place. Session 2 measured the result -- five
observations in three orders gave final beliefs of 0.0396, 0.9900 and 0.9900, a
95-point swing from ordering alone (D-20).

The fix is to accumulate in log-odds, which is unbounded and additive, and to
clamp only when a number is handed to a human. State stays exact; presentation
stays readable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

# Presentation-layer bounds. Applied on the way *out*, never to the state.
DISPLAY_FLOOR = 0.001
DISPLAY_CEIL = 0.999

# Guard against infinities from a likelihood of exactly 0 or 1.
_LIK_EPS = 1e-9


def logit(p: float) -> float:
    p = min(1.0 - _LIK_EPS, max(_LIK_EPS, p))
    return math.log(p / (1.0 - p))


def expit(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


@dataclass
class Revision:
    """One recorded belief transition (Invariant III)."""
    hypothesis_id: str
    evidence_id: str
    prior: float
    posterior: float
    log_likelihood_ratio: float
    reliability: float
    method: str = "log_odds_bayes"
    timestamp: str = ""


@dataclass
class BeliefLedger:
    """Exact, order-invariant belief state for one hypothesis.

    The state is a *set* of accumulated log-likelihood-ratio contributions, keyed
    by evidence id. Sets have no order, which is the property that was missing.
    Re-applying the same evidence id replaces its contribution rather than
    double-counting it.
    """
    prior: float = 0.5
    contributions: Dict[str, float] = field(default_factory=dict)
    history: List[Revision] = field(default_factory=list)
    #: Running total of ``contributions``. Kept incrementally so an update costs
    #: O(1) rather than O(n) -- Session 7's complexity audit measured the naive
    #: version at ~4x per doubling, i.e. quadratic in the number of updates,
    #: which is exactly the growth the monograph's complexity chapter warns
    #: against (D-27).
    _total: float = 0.0

    def set_contribution(self, evidence_id: str, llr: float) -> None:
        """Add or replace one evidence contribution in O(1)."""
        self._total += llr - self.contributions.get(evidence_id, 0.0)
        self.contributions[evidence_id] = llr

    def drop_contribution(self, evidence_id: str) -> bool:
        if evidence_id not in self.contributions:
            return False
        self._total -= self.contributions.pop(evidence_id)
        return True

    def log_odds(self) -> float:
        return logit(self.prior) + self._total

    def probability(self) -> float:
        """Exact posterior. Not clamped -- this is state, not display."""
        return expit(self.log_odds())

    def display_probability(self) -> float:
        return min(DISPLAY_CEIL, max(DISPLAY_FLOOR, self.probability()))


class BeliefRevisionEngine:
    """Order-invariant Bayesian revision with a full audit trail."""

    def __init__(self, urg=None) -> None:
        self.urg = urg
        self.ledgers: Dict[str, BeliefLedger] = {}

    def ledger(self, hypothesis_id: str, prior: float = 0.5) -> BeliefLedger:
        return self.ledgers.setdefault(hypothesis_id, BeliefLedger(prior=prior))

    def update(self, hypothesis_id: str, evidence_id: str,
               likelihood_if_true: float, likelihood_if_false: float,
               reliability: float = 1.0, prior: float = 0.5,
               timestamp: str = "") -> float:
        """Fold one piece of evidence in. Calling order does not matter.

        ``reliability`` shrinks the likelihood ratio toward 1 (uninformative),
        which is the right place for it: an unreliable observation should move
        the belief less, not be discarded.
        """
        led = self.ledger(hypothesis_id, prior)
        before = led.probability()

        lt = min(1.0 - _LIK_EPS, max(_LIK_EPS, likelihood_if_true))
        lf = min(1.0 - _LIK_EPS, max(_LIK_EPS, likelihood_if_false))
        llr = math.log(lt / lf) * max(0.0, min(1.0, reliability))

        led.set_contribution(evidence_id, llr)
        after = led.probability()
        led.history.append(Revision(
            hypothesis_id=hypothesis_id, evidence_id=evidence_id,
            prior=before, posterior=after, log_likelihood_ratio=llr,
            reliability=reliability, timestamp=timestamp,
        ))
        if self.urg is not None and hypothesis_id in self.urg:
            self.urg.update_node(hypothesis_id,
                                 belief=after,
                                 display_belief=led.display_probability(),
                                 n_revisions=len(led.history))
        return after

    def retract(self, hypothesis_id: str, evidence_id: str) -> Optional[float]:
        """Remove one evidence contribution. Exactly invertible, by construction."""
        led = self.ledgers.get(hypothesis_id)
        if led is None or not led.drop_contribution(evidence_id):
            return None
        return led.probability()

    def belief(self, hypothesis_id: str) -> Optional[float]:
        led = self.ledgers.get(hypothesis_id)
        return None if led is None else led.probability()

    def distribution(self, hypothesis_ids: Sequence[str]) -> Dict[str, float]:
        """Normalised belief across a competing set, for inquiry planning."""
        raw = {h: (self.belief(h) if self.belief(h) is not None else 0.5)
               for h in hypothesis_ids}
        total = sum(raw.values())
        if total <= 0:
            return {h: 1.0 / len(raw) for h in raw}
        return {h: v / total for h, v in raw.items()}

    def revision_history(self, hypothesis_id: str) -> List[Revision]:
        led = self.ledgers.get(hypothesis_id)
        return list(led.history) if led else []
