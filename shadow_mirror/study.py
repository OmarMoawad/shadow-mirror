"""A consented study of one other person -- the gate between consent and data.

``Study`` binds a single subject's :class:`ConsentGrant` to their
:class:`Encounter` records and to the pattern analysis. It exists so that the
consent check is not a politeness you can forget to call: **every** encounter
goes through :meth:`observe`, and :meth:`observe` refuses -- raising
:class:`ConsentError` -- unless an *active* grant covers that exact data stream.
No grant, no datum. That is the whole point.

It also carries the subject-ownership guarantees: inspect everything
(:meth:`records`), correct a datum (:meth:`amend`), erase one stream or the whole
subject (:meth:`revoke` wipes on revoke by default). The analysis layer is
read-only and only ever emits questions.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .consent import ConsentError, ConsentGrant
from .patterns import Encounter, PatternReading, analyze


class Study:
    def __init__(self, grant: ConsentGrant,
                 encounters: Optional[List[Encounter]] = None) -> None:
        self.grant = grant
        self.encounters: List[Encounter] = list(encounters or [])

    # -- ingestion (the gate) ---------------------------------------------
    def observe(self, condition: str, valence: float, action: float,
                arousal: float = 0.5, stream: str = "self_report",
                context: str = "", reliability: float = 1.0,
                domain: str = "reaction_patterns") -> Encounter:
        """Record one encounter -- iff consent actively covers this stream.

        Raising rather than silently dropping is intentional: a covert recording
        is the failure we most need to make impossible, so the unhappy path is
        loud.
        """
        if not self.grant.active:
            raise ConsentError(
                f"No active consent for subject {self.grant.subject_id!r} "
                "(revoked, lapsed, or never granted). Nothing recorded."
            )
        if not self.grant.allows(stream, domain):
            raise ConsentError(
                f"Consent for {self.grant.subject_id!r} does not cover stream "
                f"{stream!r} for {domain!r}. Ask for it explicitly first -- "
                "especially if it is something the subject does not notice about "
                "themselves. Nothing recorded."
            )
        enc = Encounter(
            subject_id=self.grant.subject_id, condition=condition, valence=valence,
            action=action, arousal=arousal, stream=stream, context=context,
            reliability=reliability,
        )
        self.encounters.append(enc)
        return enc

    # -- subject ownership -------------------------------------------------
    def records(self, condition: Optional[str] = None) -> List[Encounter]:
        """Full read access -- the subject can see everything held about them."""
        if condition is None:
            return list(self.encounters)
        return [e for e in self.encounters if e.condition == condition]

    def conditions(self) -> List[str]:
        seen: List[str] = []
        for e in self.encounters:
            if e.condition not in seen:
                seen.append(e.condition)
        return seen

    def amend(self, index: int, **fields) -> Encounter:
        """The subject's right to correct a datum recorded about them."""
        enc = self.encounters[index]
        for k, v in fields.items():
            if hasattr(enc, k):
                setattr(enc, k, v)
        enc.__post_init__()  # re-clamp
        return enc

    def revoke(self, wipe: bool = True) -> None:
        """Revoke consent. By default this also erases the data collected."""
        self.grant.revoke()
        if wipe:
            self.encounters.clear()

    # -- analysis (read-only, questions only) ------------------------------
    def patterns(self, condition: str) -> PatternReading:
        return analyze(self.records(condition))

    def all_patterns(self) -> Dict[str, PatternReading]:
        return {c: self.patterns(c) for c in self.conditions()}

    # -- serialization -----------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "consent": self.grant.to_dict(),
            "encounters": [e.to_dict() for e in self.encounters],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Study":
        grant = ConsentGrant.from_dict(d["consent"])
        encs = [Encounter.from_dict(e) for e in d.get("encounters", [])]
        return cls(grant, encs)
