"""An append-only consent ledger, and withdrawal receipts.

GDPR Art. 7(1) requires a controller to be able to *demonstrate* that consent was
given. A mutable grant object cannot: once a stream is added and later removed,
nothing records that it was ever granted, and a grant revoked and re-issued looks
identical to one that never lapsed. Session 9 recorded this as D-31.

Art. 7(3) requires that withdrawing consent be as easy as giving it. Revocation
was already a single call, but it produced nothing the subject could keep. A
grant flow that ends with a printed summary and a withdrawal that ends in silence
are not equivalent experiences, whatever the API surface says.

Both are fixed here by the same mechanism the belief layer already uses: an
append-only sequence of events. Nothing is ever mutated or deleted from the
ledger, including on erasure -- the ledger records *that* data was erased, which
is the evidence of compliance, while the data itself is gone.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

GRANTED = "granted"
STREAM_ADDED = "stream_added"
REAFFIRMED = "reaffirmed"
LAPSED = "lapsed"
REVOKED = "revoked"
ERASED = "erased"
CONTEXT_DECLARED = "context_declared"
REFUSED = "refused"

EVENT_TYPES = (GRANTED, STREAM_ADDED, REAFFIRMED, LAPSED, REVOKED, ERASED,
               CONTEXT_DECLARED, REFUSED)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ConsentEvent:
    """One immutable fact about consent, chained to the one before it."""
    seq: int
    event: str
    subject: str
    timestamp: str
    detail: Dict[str, Any] = field(default_factory=dict)
    prev_hash: str = ""
    hash: str = ""

    def compute_hash(self) -> str:
        payload = json.dumps(
            {"seq": self.seq, "event": self.event, "subject": self.subject,
             "timestamp": self.timestamp, "detail": self.detail,
             "prev_hash": self.prev_hash},
            sort_keys=True, default=str,
        )
        return hashlib.sha256(payload.encode()).hexdigest()


class ConsentLedger:
    """Append-only, hash-chained record of every consent event.

    The chain is not cryptographic security -- a local file can be rewritten by
    whoever owns it, and the subject owning their own data is the whole point. It
    is *tamper evidence*: a controller who claims consent was held on a given date
    can show a chain that verifies, and a chain that has been edited will not.
    """

    def __init__(self) -> None:
        self._events: List[ConsentEvent] = []

    def record(self, event: str, subject: str,
               **detail: Any) -> ConsentEvent:
        if event not in EVENT_TYPES:
            raise ValueError(f"unknown consent event {event!r}")
        prev = self._events[-1].hash if self._events else ""
        ev = ConsentEvent(seq=len(self._events), event=event, subject=subject,
                          timestamp=_now(), detail=dict(detail), prev_hash=prev)
        ev = ConsentEvent(**{**asdict(ev), "hash": ev.compute_hash()})
        self._events.append(ev)
        return ev

    # -- Art. 7(1): demonstrate --------------------------------------------
    def events(self, subject: Optional[str] = None) -> List[ConsentEvent]:
        return [e for e in self._events if subject is None or e.subject == subject]

    def streams_granted_at(self, subject: str, when: str) -> List[str]:
        """Which streams were under active grant at an instant. The Art. 7(1) query."""
        active: List[str] = []
        for e in self.events(subject):
            if e.timestamp > when:
                break
            if e.event == GRANTED:
                active = list(e.detail.get("streams", []))
            elif e.event == STREAM_ADDED:
                s = e.detail.get("stream")
                if s and s not in active:
                    active.append(s)
            elif e.event in (REVOKED, LAPSED):
                active = []
        return active

    def verify(self) -> bool:
        """Does the chain still hash-verify end to end?"""
        prev = ""
        for e in self._events:
            recomputed = ConsentEvent(
                seq=e.seq, event=e.event, subject=e.subject,
                timestamp=e.timestamp, detail=e.detail, prev_hash=prev,
            ).compute_hash()
            if recomputed != e.hash or e.prev_hash != prev:
                return False
            prev = e.hash
        return True

    # -- Art. 7(3): withdrawal parity --------------------------------------
    def withdrawal_receipt(self, subject: str) -> Dict[str, Any]:
        """What the subject gets to keep when they withdraw.

        Granting is a guided flow that ends with a summary. Withdrawal must end
        with something equally concrete, or the two are not equally easy however
        few keystrokes each takes.
        """
        evs = self.events(subject)
        revocations = [e for e in evs if e.event == REVOKED]
        erasures = [e for e in evs if e.event == ERASED]
        granted_streams: List[str] = []
        for e in evs:
            if e.event == GRANTED:
                granted_streams = list(e.detail.get("streams", []))
            elif e.event == STREAM_ADDED:
                s = e.detail.get("stream")
                if s and s not in granted_streams:
                    granted_streams.append(s)
        return {
            "subject": subject,
            "withdrawn": bool(revocations),
            "withdrawn_at": revocations[-1].timestamp if revocations else None,
            "streams_that_had_been_granted": granted_streams,
            "records_erased": sum(int(e.detail.get("n_records", 0)) for e in erasures),
            "erased_at": erasures[-1].timestamp if erasures else None,
            "ledger_entries_retained": len(evs),
            "chain_verifies": self.verify(),
            "note": (
                "Your observations have been erased. This receipt and the consent "
                "ledger are retained -- not your data, only the record that consent "
                "was given and then withdrawn. That record is what lets anyone "
                "check afterwards that the withdrawal was honoured."
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {"events": [asdict(e) for e in self._events],
                "chain_verifies": self.verify()}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)
