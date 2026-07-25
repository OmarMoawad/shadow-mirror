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
from .urg import UnifiedReflectiveGraph, NODE_TYPES, EDGE_TYPES
from .beliefs import BeliefRevisionEngine, BeliefLedger, logit, expit
from .inquiry import (CandidateObservation, Inquiry, InquiryPlanner,
                      expected_information_gain)
from .ewk import EWKProfile, EWKReading, Tension, TENSION_THRESHOLD
from .invariants import check_all, summarise
from .credible import credible_set, set_report, estimate_person_offset, apply_offset
from .deployment import (DeploymentContext, DeploymentRefusal, self_context,
                         SELF, CONSENTED_INDIVIDUAL, INSTITUTIONAL, UNDECLARED,
                         BIOMETRIC_STREAMS)
from .ledger import ConsentLedger, ConsentEvent
from .route_a import (DATASETS as ROUTE_A_DATASETS, LoadReport, Trial as RouteATrial,
                     load_foodeeg_choices, load_biraffe2_procedure,
                     load_urban_appraisal, preference_contradiction_rate,
                     abstention_report, download_instructions)
from .formation import (FormationModel, FormationRefusal, InstrumentSpec,
                        REGISTRY as INSTRUMENT_REGISTRY, REFUSAL_GROUNDS,
                        PSYCHOMETRIC_STREAM)

__all__ = [
    "ROUTE_A_DATASETS", "RouteATrial", "load_foodeeg_choices",
    "load_biraffe2_procedure", "load_urban_appraisal",
    "preference_contradiction_rate", "abstention_report", "download_instructions",
    "FormationModel", "FormationRefusal", "InstrumentSpec",
    "INSTRUMENT_REGISTRY", "REFUSAL_GROUNDS", "PSYCHOMETRIC_STREAM",
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
    # unified reflective layer (v1.0)
    "UnifiedReflectiveGraph",
    "NODE_TYPES",
    "EDGE_TYPES",
    "BeliefRevisionEngine",
    "BeliefLedger",
    "logit",
    "expit",
    "CandidateObservation",
    "Inquiry",
    "InquiryPlanner",
    "expected_information_gain",
    "EWKProfile",
    "EWKReading",
    "Tension",
    "TENSION_THRESHOLD",
    "check_all",
    "summarise",
    "credible_set",
    "set_report",
    "estimate_person_offset",
    "apply_offset",
    # deployment context and consent record (v1.1)
    "DeploymentContext",
    "DeploymentRefusal",
    "self_context",
    "SELF",
    "CONSENTED_INDIVIDUAL",
    "INSTITUTIONAL",
    "UNDECLARED",
    "BIOMETRIC_STREAMS",
    "ConsentLedger",
    "ConsentEvent",
]

__version__ = "1.3.0"
