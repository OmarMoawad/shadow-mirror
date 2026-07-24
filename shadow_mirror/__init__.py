"""Shadow Mirror.

A consent-based, self-owned, probabilistic self-reflection engine.

It does NOT classify who a person "really is." It estimates dated, uncertain
hypotheses about the tension between what you *say* (self-report), what you can
*do* (performance), and what you *do* (behaviour) -- and it turns those tensions
into questions you may choose to sit with, never verdicts.

Three commitments are structural, not optional:
  1. Self-owned. The person holds the mirror about themselves. Data is local.
  2. Uncertain. Output is a posterior with an honest uncertainty interval,
     dated as a snapshot -- never an enduring identity.
  3. Trauma-aware. "This is a threat-response, not a preference" is a
     first-class hypothesis; arousal + avoidance is never collapsed into "want".
"""

from .models import Observation, BeliefState, Axis, SignalType
from .engine import ShadowMirror
from .safety import SafetyReport
from .reflect import reflective_prompts
from .consent import (
    ConsentGrant,
    ConsentError,
    DATA_STREAMS,
    NON_OBVIOUS_STREAMS,
    INFERENCE_DOMAINS,
    disclosure_text,
)
from .patterns import Encounter, PatternReading, analyze, reaction_state
from .study import Study

__all__ = [
    # self-owned mirror
    "ShadowMirror",
    "Observation",
    "BeliefState",
    "SafetyReport",
    "Axis",
    "SignalType",
    "reflective_prompts",
    # consented-subject study
    "ConsentGrant",
    "ConsentError",
    "DATA_STREAMS",
    "NON_OBVIOUS_STREAMS",
    "INFERENCE_DOMAINS",
    "disclosure_text",
    "Study",
    "Encounter",
    "PatternReading",
    "analyze",
    "reaction_state",
]

__version__ = "0.3.0"
