"""Deployment context, and the streams each context may lawfully use.

Session 9's regulatory audit found one prohibition that is currently unlawful to
breach in the EU and had **no code mechanism** behind it. This module supplies it.

The chain, in short. EU AI Act Art. 3(34) defines biometric data as personal data
from technical processing of physiological characteristics -- and, unlike GDPR
Art. 4(14), it does *not* require unique identification. An arousal proxy is
therefore biometric data while identifying nobody. Art. 3(39) defines an emotion
recognition system as one inferring emotions or intentions on the basis of
biometric data, which is what the threat guard does when the physiological stream
is present. Art. 5(1)(f) then prohibits emotion inference "in the areas of
workplace and education institutions", except for medical or safety reasons.
Applicable since 2 February 2025.

A safety-purpose argument is available -- the stream exists solely as a threat
confound and Session 2 measured a 31.2 percentage-point harm increase without it.
That argument is untested in case law. So the default here is refusal, and an
operator who believes the exception applies to their deployment must say so
explicitly, in writing, with a stated basis that is recorded.

The point is not that a Python module makes anyone compliant. It is that a
prohibition nothing can enforce is a wish, and this converts one from a wish into
a mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional, Set

#: A person holding the mirror about themselves, outside any institution.
SELF = "self"
#: Two private individuals, consented study mode, no institutional relationship.
CONSENTED_INDIVIDUAL = "consented_individual"
#: Deployed by or within a workplace or an education institution.
INSTITUTIONAL = "institutional"
#: Context not yet declared. Treated as institutional: refusal is the safe default.
UNDECLARED = "undeclared"

CONTEXTS = (SELF, CONSENTED_INDIVIDUAL, INSTITUTIONAL, UNDECLARED)

#: Streams that make the system an emotion recognition system under Art. 3(39),
#: because they supply the biometric basis for inferring an affective state.
BIOMETRIC_STREAMS: Set[str] = {"physiological"}


class DeploymentRefusal(PermissionError):
    """Raised when a context may not use a stream. Not catchable by accident."""


@dataclass
class DeploymentContext:
    """Where this instance is running, and what that permits.

    ``safety_exception_basis`` is deliberately a free-text field that must be
    non-empty to have any effect. An operator invoking Art. 5(1)(f)'s medical or
    safety exception has to write down why, and the reason is recorded with the
    declaration. A boolean flag would let it be set by accident; a sentence
    cannot be.
    """
    context: str = UNDECLARED
    declared_by: str = ""
    purpose: str = ""
    safety_exception_basis: str = ""
    declared_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if self.context not in CONTEXTS:
            raise ValueError(f"unknown deployment context {self.context!r}; "
                             f"one of {CONTEXTS}")

    # -- the gate ----------------------------------------------------------
    def permits(self, stream: str) -> bool:
        if stream not in BIOMETRIC_STREAMS:
            return True
        if self.context in (SELF, CONSENTED_INDIVIDUAL):
            return True
        # institutional or undeclared
        return bool(self.safety_exception_basis.strip())

    def require(self, stream: str) -> None:
        if self.permits(stream):
            return
        raise DeploymentRefusal(
            f"Stream {stream!r} supplies the biometric basis for inferring an "
            f"affective state, which makes this an emotion recognition system "
            f"under EU AI Act Art. 3(39). Art. 5(1)(f) prohibits emotion "
            f"inference in workplace and education institutions (applicable "
            f"since 2 February 2025). Declared context: {self.context!r}.\n\n"
            f"If the medical-or-safety exception applies to your deployment, "
            f"declare it in writing:\n"
            f"    DeploymentContext(context={self.context!r}, "
            f"safety_exception_basis='...')\n"
            f"The stated basis is recorded and exported with the consent ledger."
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "context": self.context,
            "declared_by": self.declared_by,
            "purpose": self.purpose,
            "safety_exception_claimed": bool(self.safety_exception_basis.strip()),
            "safety_exception_basis": self.safety_exception_basis,
            "declared_at": self.declared_at,
            "biometric_streams_permitted": sorted(
                s for s in BIOMETRIC_STREAMS if self.permits(s)),
            "regulatory_note": (
                "EU AI Act Art. 3(34), 3(39), 5(1)(f). This declaration is a "
                "record of the operator's stated position; it is not legal advice "
                "and does not establish compliance."
            ),
        }


def self_context(purpose: str = "personal reflection") -> DeploymentContext:
    return DeploymentContext(context=SELF, purpose=purpose)
