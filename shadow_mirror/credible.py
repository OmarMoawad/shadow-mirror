"""Credible sets, and per-person offset correction.

Both exist because of one measured failure. Session 3 showed that when the
model's assumed corners are displaced from where a person's evidence actually
sits, the engine becomes *more* confident as evidence accumulates while its
accuracy collapses -- expected calibration error rose from 0.151 to 0.221 for
severe misspecification, and at the worst cell it abstained 21% of the time while
being wrong 54% of the time (D-23).

Tuning the abstention threshold cannot fix that. The failure is identifiability,
not thresholding: a two-channel location model cannot distinguish "state A,
displaced" from "state B" when the displacement points toward B. So the fix has
to change either what is reported or what is observed.

* ``credible_set`` changes **what is reported**: the smallest set of hypotheses
  carrying the requested posterior mass, instead of an argmax. Correctness then
  means *coverage* -- does the reported set contain the truth at the nominal
  rate -- which is a property the instrument can actually keep.

* ``estimate_person_offset`` changes **what is observed**: if a person is
  systematically displaced (they habitually under-report confidence, say), then
  that displacement is shared across topics and becomes estimable by pooling.
  One topic cannot see it; several can.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple


def credible_set(posterior: Dict[str, float], mass: float = 0.90
                 ) -> Tuple[List[str], float]:
    """Smallest set of hypotheses whose posterior mass reaches ``mass``.

    Returns (hypotheses, achieved_mass). Ordering is by descending posterior,
    ties broken by name so the output is deterministic.
    """
    ordered = sorted(posterior.items(), key=lambda kv: (-kv[1], kv[0]))
    chosen: List[str] = []
    acc = 0.0
    for name, p in ordered:
        chosen.append(name)
        acc += p
        if acc >= mass:
            break
    return chosen, acc


def set_report(posterior: Dict[str, float], mass: float = 0.90) -> Dict[str, object]:
    """A reportable reading that does not force a single label."""
    names, achieved = credible_set(posterior, mass)
    return {
        "credible_set": names,
        "requested_mass": mass,
        "achieved_mass": round(achieved, 4),
        "set_size": len(names),
        "committed": len(names) == 1,
        "note": (
            "This is the smallest set of readings the evidence cannot separate. "
            "A set larger than one is not a failure to answer -- it is the answer."
        ),
    }


# ---------------------------------------------------------------------------
# Per-person offset
# ---------------------------------------------------------------------------

def estimate_person_offset(
    topic_means: Sequence[Tuple[float, float]],
    corners: Dict[str, Tuple[float, float]],
    iterations: int = 25,
    sigma: float = 0.28,
    restarts: int = 5,
    min_topics: int = 3,
) -> Tuple[float, float]:
    """Estimate a person-level displacement shared across topics.

    ``topic_means`` is one (channel_a_mean, channel_b_mean) per topic. Each topic
    may be in a different latent state, but the *displacement* is assumed to be a
    property of the person -- how they report relative to how they perform -- and
    therefore common.

    Soft-assignment EM with multiple restarts, selected by likelihood.

    **It refuses below ``min_topics``.** With one topic the displacement is not
    identifiable at all -- a single point can be moved onto any of four corners by
    some offset, so there are more unknowns than equations. Estimating anyway is
    not merely uninformative, it is harmful: measured at one topic and delta=0.30,
    correcting with an unguarded estimate drove accuracy from 81.2% to 20.8%,
    substantially worse than not correcting. The guard is an identifiability
    condition, not a tuned threshold.
    """
    if not topic_means or len(topic_means) < min_topics:
        return (0.0, 0.0)

    import math

    cs = list(corners.values())

    def run(start: Tuple[float, float]) -> Tuple[Tuple[float, float], float]:
        ox, oy = start
        for _ in range(iterations):
            num_x = num_y = tot = 0.0
            loglik = 0.0
            for (a, b) in topic_means:
                ca, cb = a - ox, b - oy
                # Soft assignment: responsibility of each corner, rather than
                # committing to the nearest one. Hard assignment converged to a
                # poor local optimum at severe displacement because its first
                # assignment was mostly wrong (D-26).
                d2 = [((ca - cx) ** 2 + (cb - cy) ** 2) for cx, cy in cs]
                m = min(d2)
                w = [math.exp(-(d - m) / (2.0 * sigma * sigma)) for d in d2]
                z = sum(w)
                loglik += -m / (2.0 * sigma * sigma) + math.log(z)
                for wi, (cx, cy) in zip(w, cs):
                    r = wi / z
                    num_x += r * (a - cx)
                    num_y += r * (b - cy)
                    tot += r
            nx, ny = (num_x / tot, num_y / tot) if tot > 0 else (ox, oy)
            if abs(nx - ox) < 1e-9 and abs(ny - oy) < 1e-9:
                ox, oy = nx, ny
                break
            ox, oy = nx, ny
        return (ox, oy), loglik

    # Multiple starts: the zero start, plus each corner-to-mean residual. The
    # likelihood picks between them, so no benchmark tuning is involved.
    starts = [(0.0, 0.0)]
    mx = sum(a for a, _ in topic_means) / len(topic_means)
    my = sum(b for _, b in topic_means) / len(topic_means)
    for cx, cy in cs[:max(0, restarts - 1)]:
        starts.append((mx - cx, my - cy))

    best, best_ll = (0.0, 0.0), -float("inf")
    for st in starts:
        cand, ll = run(st)
        if ll > best_ll:
            best, best_ll = cand, ll
    return best


def apply_offset(mean: Tuple[float, float], offset: Tuple[float, float]
                 ) -> Tuple[float, float]:
    """Remove an estimated person offset, clipped back into the unit square."""
    return (min(1.0, max(0.0, mean[0] - offset[0])),
            min(1.0, max(0.0, mean[1] - offset[1])))
