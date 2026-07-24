"""The consent layer: the front door for studying a *consenting other person*.

This is the module that makes the "other people" mode defensible instead of
covert. The research is unambiguous on one point: for intensive, multi-stream
data collection -- especially streams a person cannot foresee or does not notice
about themselves -- **broad / blanket consent is not meaningful informed consent**
(Budin-Ljosne et al., *dynamic consent*; secondary-use of physiological data is the
canonical hard case). The defensible form is *dynamic consent*: granular,
per-stream, purpose-locked, inspectable, and revocable at any moment.

So consent here is not a single "yes to everything". It is a set of **per-stream
grants**, each acknowledged on its own. The engine refuses to ingest any datum
whose stream is not in an *active* grant. That refusal is the structural
guarantee that this can never be run covertly: no grant, no observation, ever.

Design commitments (all load-bearing):

* **Enumerated, plain-language streams.** Every stream says, in one sentence,
  what it captures and what it could reveal -- so "informed" is real.
* **Non-obvious streams need their own explicit yes.** Implicit, behavioural-trace,
  and physiological signals -- the ones a subject does *not* notice about
  themselves -- are marked ``self_noticeable = False`` and cannot be granted by a
  blanket call; each must be named and acknowledged individually.
* **Purpose lock.** A grant records the purpose it was given for. Uses outside
  that purpose are out of scope (see ETHICS.md's never-for list).
* **Revocable + expiring.** A grant can be revoked instantly, and scoped grants
  carry a review horizon so consent is *re-affirmed*, not signed once forever.
* **The subject owns it.** Everything is inspectable, correctable, and erasable by
  the subject (enforced at the store/CLI layer).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


# ---------------------------------------------------------------------------
# The data streams a subject may consent to, each described honestly.
#
# ``self_noticeable`` == can the subject perceive, in the moment, that this datum
# is being produced about them? For the False ones, the person genuinely cannot
# picture what they are agreeing to unless we spell it out -- so those require a
# separate, explicit acknowledgement and can never be bundled under a blanket yes.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Stream:
    key: str
    label: str
    self_noticeable: bool
    captures: str      # what is recorded
    may_reveal: str    # what could be inferred from it (the informed part)


DATA_STREAMS: Dict[str, Stream] = {
    s.key: s for s in [
        Stream(
            "self_report", "What you tell me", True,
            "your own stated feelings, wants, and confidence, in your words",
            "the gap between what you say and what you do",
        ),
        Stream(
            "stated_emotion", "Emotions you name", True,
            "emotions you explicitly report feeling in a situation",
            "how a named feeling lines up (or not) with how you then act",
        ),
        Stream(
            "behavior", "What you visibly do", True,
            "your observable approach/engagement in a situation",
            "action tendencies -- moving toward or away from things",
        ),
        Stream(
            "implicit_task", "Indirect reaction measures", False,
            "reaction-time / indirect-task tendencies you are not directing on purpose",
            "leanings you may not be aware you have; these can be wrong and are "
            "read only as weak, uncertain signals",
        ),
        Stream(
            "physiological", "Body-arousal signals", False,
            "arousal proxies (e.g. heart-rate-like signals) you do not consciously control",
            "how activated your body is -- used ONLY as a threat/safety cue, never "
            "as proof you 'secretly want' anything",
        ),
        Stream(
            "avoidance", "Turning-away you may not notice", False,
            "micro-avoidance / withdrawal you may not register doing",
            "whether a situation is being experienced as unsafe -- a threat cue, "
            "never read as a hidden preference",
        ),
    ]
}

# Streams the subject cannot self-notice: each needs its own explicit yes.
NON_OBVIOUS_STREAMS: Set[str] = {
    k for k, s in DATA_STREAMS.items() if not s.self_noticeable
}

# What the model may be asked to infer. A grant is scoped to these, too.
INFERENCE_DOMAINS = (
    "reaction_patterns",   # first reaction / counter-pattern across encounters
    "emotion_behavior",    # how emotion appears to bend behaviour
)

# Grants older than this without re-affirmation are treated as lapsed, so
# consent is a living agreement rather than a one-time signature.
DEFAULT_REVIEW_DAYS = 90


class ConsentError(PermissionError):
    """Raised when something is attempted that consent does not cover.

    It is a hard error on purpose: the failure mode we most need to prevent is a
    datum being recorded that nobody agreed to. Better a crash than a quiet leak.
    """


@dataclass
class ConsentGrant:
    """One consenting subject's living, granular agreement.

    A grant is only *active* when it is not revoked and within its review
    horizon. ``allows`` is the single gate every observation must pass.
    """

    subject_id: str
    purpose: str
    streams: Set[str] = field(default_factory=set)
    domains: Set[str] = field(default_factory=set)
    granted_at: str = field(default_factory=lambda: _iso(_now()))
    reaffirmed_at: str = field(default_factory=lambda: _iso(_now()))
    review_days: int = DEFAULT_REVIEW_DAYS
    revoked_at: Optional[str] = None
    # A free record of exactly what the subject was shown, so "informed" is auditable.
    disclosures: List[str] = field(default_factory=list)

    # -- validity ----------------------------------------------------------
    @property
    def revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def lapsed(self) -> bool:
        """True once the review horizon has passed without re-affirmation."""
        if self.review_days <= 0:
            return False
        try:
            base = datetime.fromisoformat(self.reaffirmed_at)
        except (ValueError, TypeError):
            return False
        return _now() > base + timedelta(days=self.review_days)

    @property
    def active(self) -> bool:
        return not self.revoked and not self.lapsed and bool(self.streams)

    def allows(self, stream: str, domain: Optional[str] = None) -> bool:
        if not self.active:
            return False
        if stream not in self.streams:
            return False
        if domain is not None and domain not in self.domains:
            return False
        return True

    # -- mutation ----------------------------------------------------------
    def revoke(self) -> None:
        self.revoked_at = _iso(_now())

    def reaffirm(self) -> None:
        """The subject re-confirms; the review clock restarts."""
        if self.revoked:
            raise ConsentError("Cannot re-affirm a revoked grant; grant a new one.")
        self.reaffirmed_at = _iso(_now())

    def add_stream(self, stream: str, acknowledged_non_obvious: bool = False) -> None:
        """Grant one stream. Non-self-noticeable streams demand an explicit ack.

        ``acknowledged_non_obvious`` must be passed True, per stream, for anything
        the subject cannot notice about themselves. This is the code-level
        expression of "only after they agree to THIS form of data too".
        """
        if stream not in DATA_STREAMS:
            raise ConsentError(f"Unknown data stream: {stream!r}")
        if stream in NON_OBVIOUS_STREAMS and not acknowledged_non_obvious:
            raise ConsentError(
                f"Stream {stream!r} is something the subject does not notice about "
                "themselves. It cannot be bundled under a general yes -- it needs "
                "its own explicit acknowledgement."
            )
        self.streams.add(stream)

    # -- serialization -----------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "purpose": self.purpose,
            "streams": sorted(self.streams),
            "domains": sorted(self.domains),
            "granted_at": self.granted_at,
            "reaffirmed_at": self.reaffirmed_at,
            "review_days": self.review_days,
            "revoked_at": self.revoked_at,
            "disclosures": list(self.disclosures),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ConsentGrant":
        return cls(
            subject_id=d["subject_id"],
            purpose=d.get("purpose", ""),
            streams=set(d.get("streams", [])),
            domains=set(d.get("domains", [])),
            granted_at=d.get("granted_at", _iso(_now())),
            reaffirmed_at=d.get("reaffirmed_at", d.get("granted_at", _iso(_now()))),
            review_days=d.get("review_days", DEFAULT_REVIEW_DAYS),
            revoked_at=d.get("revoked_at"),
            disclosures=list(d.get("disclosures", [])),
        )


def disclosure_text(streams: Set[str], domains: Set[str], purpose: str) -> str:
    """The plain-language script a subject must be shown before granting.

    Returning it as text (rather than burying it in a UI) keeps the informed part
    inspectable and testable: you can assert that every granted stream's meaning
    was actually disclosed.
    """
    lines = [
        "Before you agree, here is exactly what you would be letting this tool do,",
        "and what it could infer. You can say yes to some parts and no to others,",
        "you can see everything it stores, correct anything, and revoke at any time.",
        "",
        f"Purpose you are consenting to: {purpose or '(unstated)'}",
        "",
        "Data streams you are being asked about:",
    ]
    for key in sorted(streams):
        s = DATA_STREAMS[key]
        tag = "" if s.self_noticeable else "  [you may NOT notice this about yourself]"
        lines.append(f"  - {s.label}{tag}")
        lines.append(f"      captures: {s.captures}")
        lines.append(f"      may reveal: {s.may_reveal}")
    lines += [
        "",
        "What this tool will NOT do: it will not tell you (or anyone) who you 'really'",
        "are. Every output is a dated, uncertain question -- not a verdict -- and high",
        "body-arousal plus turning-away is read as feeling unsafe, never as a hidden want.",
        "",
        f"Inference it may perform: {', '.join(sorted(domains)) or '(none)'}",
    ]
    return "\n".join(lines)
