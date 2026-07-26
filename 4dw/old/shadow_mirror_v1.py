
"""
Shadow Mirror Reference Implementation v1.0
A computational framework for Reflective Artificial Intelligence (RAI)
Author: Omar Moawad (with architectural assistance)
License: Research-Only / MIT

This implementation demonstrates:
- Unified Reflective Graph (URG) via NetworkX
- Evidence objects with provenance and uncertainty
- Bayesian Belief Revision Engine
- Hypothesis Manager with competing explanations
- Uncertainty Manager with category-based propagation
- Inquiry Planner using expected information gain
- Explanation Generator with EWK-profile integration
- Context Engine with versioning
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import networkx as nx
import numpy as np
from collections import defaultdict

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class EvidenceType(Enum):
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    DERIVED = "derived"
    COMPOSITE = "composite"
    EMOTION = "emotion"
    WILL = "will"
    KNOWLEDGE = "knowledge"

class UncertaintyCategory(Enum):
    MEASUREMENT = "measurement"
    STRUCTURAL = "structural"
    CONTEXTUAL = "contextual"
    PREDICTIVE = "predictive"
    EXPLANATORY = "explanatory"
    MODEL = "model"

class HypothesisStatus(Enum):
    GENERATED = "generated"
    ACTIVE = "active"
    REVISED = "revised"
    ARCHIVED = "archived"

@dataclass
class EvidenceObject:
    evidence_id: str
    observation_id: str
    evidence_type: EvidenceType
    value: Any
    units: Optional[str] = None
    reliability_score: float = 1.0
    uncertainty_estimate: float = 0.0
    uncertainty_category: UncertaintyCategory = UncertaintyCategory.MEASUREMENT
    source: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context_references: List[str] = field(default_factory=list)
    provenance: List[str] = field(default_factory=list)
    related_evidence: List[str] = field(default_factory=list)
    version: int = 1

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["evidence_type"] = self.evidence_type.value
        d["uncertainty_category"] = self.uncertainty_category.value
        return d

@dataclass
class Hypothesis:
    hypothesis_id: str
    description: str
    supporting_evidence: List[str] = field(default_factory=list)
    contradictory_evidence: List[str] = field(default_factory=list)
    context_references: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    current_belief: float = 0.5
    status: HypothesisStatus = HypothesisStatus.GENERATED
    parent_hypotheses: List[str] = field(default_factory=list)
    revision_history: List[Dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: int = 1

@dataclass
class ContextState:
    context_id: str
    historical_state: Dict = field(default_factory=dict)
    environmental_state: Dict = field(default_factory=dict)
    domain_references: List[str] = field(default_factory=list)
    user_state: Dict = field(default_factory=dict)
    operational_constraints: Dict = field(default_factory=dict)
    active_objectives: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: int = 1

@dataclass
class UncertaintyRecord:
    uncertainty_id: str
    source: str
    category: UncertaintyCategory
    magnitude: float
    explanation: str
    related_nodes: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: int = 1

@dataclass
class InquiryRequest:
    inquiry_id: str
    description: str
    motivation: str
    target_uncertainty: str
    related_hypotheses: List[str] = field(default_factory=list)
    expected_benefit: float = 0.0
    suggested_method: str = ""
    priority: int = 5
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class Explanation:
    explanation_id: str
    summary: str
    supporting_evidence: List[str] = field(default_factory=list)
    competing_hypotheses: List[str] = field(default_factory=list)
    active_context: str = ""
    belief_profile: Dict = field(default_factory=dict)
    uncertainty_summary: str = ""
    inquiry_recommendations: List[str] = field(default_factory=list)
    provenance_reference: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

# ============================================================================
# UNIFIED REFLECTIVE GRAPH (URG)
# ============================================================================

class UnifiedReflectiveGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.version_counter = 0

    def add_node(self, node_id: str, node_type: str, data: Dict):
        self.graph.add_node(node_id, node_type=node_type, data=data, version=self.version_counter)
        self.version_counter += 1

    def add_edge(self, source: str, target: str, relationship: str, confidence: float = 1.0, 
                 uncertainty: float = 0.0, provenance: str = ""):
        self.graph.add_edge(source, target, 
                           relationship=relationship, 
                           confidence=confidence,
                           uncertainty=uncertainty,
                           provenance=provenance,
                           timestamp=datetime.utcnow().isoformat())

    def get_neighbors(self, node_id: str, relationship: Optional[str] = None) -> List[str]:
        if node_id not in self.graph:
            return []
        neighbors = []
        for _, target, data in self.graph.out_edges(node_id, data=True):
            if relationship is None or data.get("relationship") == relationship:
                neighbors.append(target)
        return neighbors

    def get_supporting_evidence(self, hypothesis_id: str) -> List[str]:
        return [src for src, _, data in self.graph.in_edges(hypothesis_id, data=True) 
                if data.get("relationship") == "supports"]

    def get_contradictory_evidence(self, hypothesis_id: str) -> List[str]:
        return [src for src, _, data in self.graph.in_edges(hypothesis_id, data=True) 
                if data.get("relationship") == "contradicts"]

    def trace_provenance(self, node_id: str) -> List[str]:
        if node_id not in self.graph:
            return []
        path = []
        current = node_id
        visited = set()
        while current and current not in visited:
            visited.add(current)
            preds = [(src, data) for src, _, data in self.graph.in_edges(current, data=True)
                     if data.get("relationship") == "provenance"]
            if not preds:
                break
            current = preds[0][0]
            path.append(current)
        return path

    def find_cognitive_tension(self) -> List[Tuple[str, str, str]]:
        tensions = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get("node_type") == "Hypothesis":
                supporters = self.get_supporting_evidence(node_id)
                contradictors = self.get_contradictory_evidence(node_id)
                if supporters and contradictors:
                    tensions.append((node_id, supporters[0], contradictors[0]))
        return tensions

    def subgraph_view(self, node_type: Optional[str] = None) -> nx.DiGraph:
        if node_type is None:
            return self.graph
        nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == node_type]
        return self.graph.subgraph(nodes).copy()

    def to_json(self) -> str:
        data = nx.node_link_data(self.graph)
        return json.dumps(data, indent=2, default=str)

# ============================================================================
# EVIDENCE MANAGEMENT LAYER
# ============================================================================

class EvidenceManager:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.evidence_store: Dict[str, EvidenceObject] = {}

    def construct_evidence(self, observation_id: str, value: Any, evidence_type: EvidenceType,
                          source: str = "unknown", reliability: float = 1.0,
                          uncertainty: float = 0.0, context_refs: List[str] = None,
                          provenance: List[str] = None) -> EvidenceObject:
        eid = str(uuid.uuid4())
        ev = EvidenceObject(
            evidence_id=eid,
            observation_id=observation_id,
            evidence_type=evidence_type,
            value=value,
            source=source,
            reliability_score=reliability,
            uncertainty_estimate=uncertainty,
            context_references=context_refs or [],
            provenance=provenance or [observation_id]
        )
        self.evidence_store[eid] = ev
        self.urg.add_node(eid, "Evidence", ev.to_dict())
        self.urg.add_edge(observation_id, eid, "provenance", provenance=observation_id)
        return ev

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceObject]:
        return self.evidence_store.get(evidence_id)

    def link_evidence(self, source_eid: str, target_eid: str, relationship: str):
        if source_eid in self.evidence_store and target_eid in self.evidence_store:
            self.urg.add_edge(source_eid, target_eid, relationship)
            self.evidence_store[source_eid].related_evidence.append(target_eid)

# ============================================================================
# CONTEXT ENGINE
# ============================================================================

class ContextEngine:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.context_history: List[ContextState] = []
        self.current_context: Optional[ContextState] = None

    def initialize_context(self, user_id: str, domain: str, objectives: List[str]) -> ContextState:
        ctx = ContextState(
            context_id=str(uuid.uuid4()),
            user_state={"user_id": user_id},
            domain_references=[domain],
            active_objectives=objectives
        )
        self.current_context = ctx
        self.context_history.append(ctx)
        self.urg.add_node(ctx.context_id, "Context", asdict(ctx))
        return ctx

    def update_context(self, updates: Dict) -> ContextState:
        if self.current_context is None:
            raise ValueError("No active context")
        new_ctx = ContextState(
            context_id=str(uuid.uuid4()),
            historical_state={**self.current_context.historical_state, 
                             self.current_context.timestamp: asdict(self.current_context)},
            environmental_state=updates.get("environmental", self.current_context.environmental_state),
            domain_references=self.current_context.domain_references,
            user_state={**self.current_context.user_state, **updates.get("user", {})},
            operational_constraints=updates.get("constraints", self.current_context.operational_constraints),
            active_objectives=updates.get("objectives", self.current_context.active_objectives),
            version=self.current_context.version + 1
        )
        self.urg.add_node(new_ctx.context_id, "Context", asdict(new_ctx))
        self.urg.add_edge(self.current_context.context_id, new_ctx.context_id, "revises")
        self.current_context = new_ctx
        self.context_history.append(new_ctx)
        return new_ctx

# ============================================================================
# HYPOTHESIS MANAGER
# ============================================================================

class HypothesisManager:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.hypotheses: Dict[str, Hypothesis] = {}

    def generate_hypothesis(self, description: str, supporting_evidence: List[str] = None,
                           assumptions: List[str] = None, context_refs: List[str] = None) -> Hypothesis:
        hid = str(uuid.uuid4())
        hyp = Hypothesis(
            hypothesis_id=hid,
            description=description,
            supporting_evidence=supporting_evidence or [],
            assumptions=assumptions or [],
            context_references=context_refs or [],
            status=HypothesisStatus.ACTIVE
        )
        self.hypotheses[hid] = hyp
        self.urg.add_node(hid, "Hypothesis", asdict(hyp))
        for eid in (supporting_evidence or []):
            self.urg.add_edge(eid, hid, "supports")
        return hyp

    def add_contradictory_evidence(self, hypothesis_id: str, evidence_id: str):
        if hypothesis_id in self.hypotheses:
            self.hypotheses[hypothesis_id].contradictory_evidence.append(evidence_id)
            self.urg.add_edge(evidence_id, hypothesis_id, "contradicts")

    def archive_hypothesis(self, hypothesis_id: str, reason: str = ""):
        if hypothesis_id in self.hypotheses:
            self.hypotheses[hypothesis_id].status = HypothesisStatus.ARCHIVED
            self.hypotheses[hypothesis_id].revision_history.append({
                "action": "archive",
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_active_hypotheses(self) -> List[Hypothesis]:
        return [h for h in self.hypotheses.values() if h.status == HypothesisStatus.ACTIVE]

    def find_similar_hypotheses(self, hypothesis_id: str, threshold: float = 0.7) -> List[str]:
        if hypothesis_id not in self.hypotheses:
            return []
        target = self.hypotheses[hypothesis_id]
        target_ev = set(target.supporting_evidence)
        similar = []
        for hid, hyp in self.hypotheses.items():
            if hid == hypothesis_id:
                continue
            overlap = len(target_ev & set(hyp.supporting_evidence)) / max(len(target_ev), 1)
            if overlap >= threshold:
                similar.append(hid)
        return similar

# ============================================================================
# BELIEF REVISION ENGINE (Bayesian)
# ============================================================================

class BeliefRevisionEngine:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.revision_history: List[Dict] = []

    def bayesian_update(self, hypothesis_id: str, evidence_id: str, 
                       likelihood_if_true: float, likelihood_if_false: float,
                       evidence_reliability: float = 1.0) -> float:
        node_data = self.urg.graph.nodes.get(hypothesis_id, {})
        current_belief = node_data.get("data", {}).get("current_belief", 0.5)

        adj_likelihood_true = 0.5 + (likelihood_if_true - 0.5) * evidence_reliability
        adj_likelihood_false = 0.5 + (likelihood_if_false - 0.5) * evidence_reliability

        numerator = adj_likelihood_true * current_belief
        denominator = numerator + adj_likelihood_false * (1 - current_belief)

        if denominator == 0:
            posterior = current_belief
        else:
            posterior = numerator / denominator

        posterior = max(0.01, min(0.99, posterior))

        if hypothesis_id in self.urg.graph:
            self.urg.graph.nodes[hypothesis_id]["data"]["current_belief"] = posterior
            self.urg.graph.nodes[hypothesis_id]["data"]["last_updated"] = datetime.utcnow().isoformat()

        self.revision_history.append({
            "hypothesis_id": hypothesis_id,
            "evidence_id": evidence_id,
            "prior": current_belief,
            "posterior": posterior,
            "method": "bayesian_update",
            "timestamp": datetime.utcnow().isoformat()
        })

        return posterior

    def revise_beliefs(self, evidence_id: str, affected_hypotheses: List[Tuple[str, float, float]],
                      evidence_reliability: float = 1.0):
        for hid, l_true, l_false in affected_hypotheses:
            self.bayesian_update(hid, evidence_id, l_true, l_false, evidence_reliability)

# ============================================================================
# UNCERTAINTY MANAGER
# ============================================================================

class UncertaintyManager:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.uncertainty_records: Dict[str, UncertaintyRecord] = {}

    def record_uncertainty(self, source: str, category: UncertaintyCategory, 
                          magnitude: float, explanation: str, 
                          related_nodes: List[str] = None) -> UncertaintyRecord:
        uid = str(uuid.uuid4())
        rec = UncertaintyRecord(
            uncertainty_id=uid,
            source=source,
            category=category,
            magnitude=magnitude,
            explanation=explanation,
            related_nodes=related_nodes or []
        )
        self.uncertainty_records[uid] = rec
        self.urg.add_node(uid, "Uncertainty", asdict(rec))
        for node in (related_nodes or []):
            self.urg.add_edge(uid, node, "affects", uncertainty=magnitude)
        return rec

    def propagate_uncertainty(self, source_node: str) -> Dict[str, float]:
        if source_node not in self.urg.graph:
            return {}
        uncertainties = {source_node: 0.0}
        queue = [source_node]
        visited = {source_node}
        while queue:
            current = queue.pop(0)
            for _, target, data in self.urg.graph.out_edges(current, data=True):
                if target not in visited:
                    edge_uncertainty = data.get("uncertainty", 0.0)
                    edge_confidence = data.get("confidence", 1.0)
                    propagated = uncertainties[current] + edge_uncertainty * (1 - edge_confidence)
                    uncertainties[target] = min(1.0, propagated)
                    visited.add(target)
                    queue.append(target)
        return uncertainties

    def identify_uncertainty_sources(self, hypothesis_id: str) -> List[UncertaintyRecord]:
        sources = []
        for uid, rec in self.uncertainty_records.items():
            if hypothesis_id in rec.related_nodes:
                sources.append(rec)
        return sources

# ============================================================================
# INQUIRY PLANNER
# ============================================================================

class InquiryPlanner:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.inquiry_history: List[InquiryRequest] = []

    def plan_inquiry(self, target_hypotheses: List[str], 
                    uncertainty_manager: UncertaintyManager) -> List[InquiryRequest]:
        inquiries = []
        beliefs = []
        for hid in target_hypotheses:
            node_data = self.urg.graph.nodes.get(hid, {})
            belief = node_data.get("data", {}).get("current_belief", 0.5)
            beliefs.append((hid, belief))

        beliefs.sort(key=lambda x: x[1])
        for i in range(len(beliefs) - 1):
            h1, b1 = beliefs[i]
            h2, b2 = beliefs[i + 1]
            gap = abs(b1 - b2)
            if gap < 0.2:
                inquiry = InquiryRequest(
                    inquiry_id=str(uuid.uuid4()),
                    description=f"Distinguish between {h1[:8]} and {h2[:8]}",
                    motivation=f"Belief gap only {gap:.2f}; evidence needed to discriminate",
                    target_uncertainty="explanatory",
                    related_hypotheses=[h1, h2],
                    expected_benefit=1.0 - gap,
                    suggested_method="seek_distinguishing_evidence",
                    priority=3 if gap < 0.1 else 5
                )
                inquiries.append(inquiry)
                self.urg.add_node(inquiry.inquiry_id, "Inquiry", asdict(inquiry))
                self.urg.add_edge(inquiry.inquiry_id, h1, "targets")
                self.urg.add_edge(inquiry.inquiry_id, h2, "targets")

        for hid, belief in beliefs:
            if 0.3 < belief < 0.7:
                unc_sources = uncertainty_manager.identify_uncertainty_sources(hid)
                if unc_sources:
                    inquiry = InquiryRequest(
                        inquiry_id=str(uuid.uuid4()),
                        description=f"Reduce uncertainty for {hid[:8]}",
                        motivation=f"Belief {belief:.2f} is near uncertainty maximum",
                        target_uncertainty=unc_sources[0].category.value,
                        related_hypotheses=[hid],
                        expected_benefit=0.5,
                        priority=2
                    )
                    inquiries.append(inquiry)

        self.inquiry_history.extend(inquiries)
        return inquiries

# ============================================================================
# EXPLANATION GENERATOR
# ============================================================================

class ExplanationGenerator:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg

    def generate_explanation(self, focus_hypotheses: List[str] = None,
                            context_id: str = None) -> Explanation:
        if focus_hypotheses is None:
            focus_hypotheses = [n for n, d in self.urg.graph.nodes(data=True) 
                              if d.get("node_type") == "Hypothesis"]

        hyp_summaries = []
        for hid in focus_hypotheses:
            node_data = self.urg.graph.nodes.get(hid, {})
            data = node_data.get("data", {})
            desc = data.get("description", "Unknown hypothesis")
            belief = data.get("current_belief", 0.5)
            status = data.get("status", "unknown")
            hyp_summaries.append(f"{desc[:60]}... [belief={belief:.2f}, status={status}]")

        summary = "Active explanatory hypotheses: " + " | ".join(hyp_summaries)

        all_supporting = []
        for hid in focus_hypotheses:
            all_supporting.extend(self.urg.get_supporting_evidence(hid))

        competing = [h for h in focus_hypotheses 
                    if self.urg.graph.nodes.get(h, {}).get("data", {}).get("current_belief", 0.5) < 0.8]

        tensions = self.urg.find_cognitive_tension()
        if tensions:
            unc_summary = f"Cognitive tension detected in {len(tensions)} hypothesis(es)."
        else:
            unc_summary = "No major cognitive tensions detected."

        inquiry_nodes = [n for n, d in self.urg.graph.nodes(data=True) 
                        if d.get("node_type") == "Inquiry"]

        exp = Explanation(
            explanation_id=str(uuid.uuid4()),
            summary=summary,
            supporting_evidence=list(set(all_supporting)),
            competing_hypotheses=competing,
            active_context=context_id or "default",
            belief_profile={hid: self.urg.graph.nodes.get(hid, {}).get("data", {}).get("current_belief", 0.5) 
                          for hid in focus_hypotheses},
            uncertainty_summary=unc_summary,
            inquiry_recommendations=inquiry_nodes[:3]
        )

        self.urg.add_node(exp.explanation_id, "Explanation", asdict(exp))
        for hid in focus_hypotheses:
            self.urg.add_edge(hid, exp.explanation_id, "explains")

        return exp

# ============================================================================
# EMOTION-WILL-KNOWLEDGE (EWK) PROFILE
# ============================================================================

class EWKProfile:
    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.stream_history: Dict[str, List[EvidenceObject]] = {
            "emotion": [], "will": [], "knowledge": []
        }

    def ingest_evidence(self, evidence: EvidenceObject):
        if evidence.evidence_type == EvidenceType.EMOTION:
            self.stream_history["emotion"].append(evidence)
        elif evidence.evidence_type == EvidenceType.WILL:
            self.stream_history["will"].append(evidence)
        elif evidence.evidence_type in (EvidenceType.KNOWLEDGE, EvidenceType.QUANTITATIVE, 
                                         EvidenceType.QUALITATIVE, EvidenceType.DERIVED):
            self.stream_history["knowledge"].append(evidence)
        self.urg.add_node(evidence.evidence_id, "Evidence", evidence.to_dict())

    def detect_tension(self, window_size: int = 5) -> Optional[Dict]:
        e_recent = self.stream_history["emotion"][-window_size:]
        w_recent = self.stream_history["will"][-window_size:]
        k_recent = self.stream_history["knowledge"][-window_size:]

        if not (e_recent and w_recent and k_recent):
            return None

        def avg_val(ev_list):
            vals = [e.value for e in ev_list if isinstance(e.value, (int, float))]
            return np.mean(vals) if vals else 0.5

        e_val = avg_val(e_recent)
        w_val = avg_val(w_recent)
        k_val = avg_val(k_recent)

        tensions = []
        if k_val > 0.7 and w_val < 0.3:
            tensions.append("High_confidence_low_motivation")
        if e_val > 0.7 and k_val < 0.3:
            tensions.append("High_stress_low_performance")
        if abs(k_val - w_val) > 0.5:
            tensions.append("Knowledge_will_misalignment")

        if tensions:
            return {
                "tension_types": tensions,
                "emotion_avg": e_val,
                "will_avg": w_val,
                "knowledge_avg": k_val,
                "timestamp": datetime.utcnow().isoformat()
            }
        return None

# ============================================================================
# SELF-LIMITATION FRAMEWORK
# ============================================================================

class SelfLimitationFramework:
    LIMITATIONS = {
        "evidence": "Insufficient or contradictory evidence",
        "context": "Incomplete contextual information",
        "knowledge": "Absence of relevant knowledge artifacts",
        "method": "Unsupported reasoning method for current task",
        "computational": "Resource exhaustion or time constraints",
        "governance": "Policy or regulatory restriction"
    }

    def __init__(self, urg: UnifiedReflectiveGraph):
        self.urg = urg
        self.detected_limitations: List[Dict] = []

    def check_scope(self, task_description: str, available_evidence: List[str],
                   active_hypotheses: List[str]) -> List[Dict]:
        limitations = []
        if len(available_evidence) < 3:
            limitations.append({
                "category": "evidence",
                "severity": "high",
                "description": "Less than 3 evidence items available",
                "recommendation": "Request additional observations before concluding"
            })
        if len(active_hypotheses) == 0:
            limitations.append({
                "category": "method",
                "severity": "critical",
                "description": "No active hypotheses generated",
                "recommendation": "Cannot proceed without explanatory candidates"
            })
        tensions = self.urg.find_cognitive_tension()
        if len(tensions) > 2:
            limitations.append({
                "category": "evidence",
                "severity": "medium",
                "description": f"{len(tensions)} unresolved cognitive tensions",
                "recommendation": "Resolve contradictions or seek additional evidence"
            })
        self.detected_limitations.extend(limitations)
        return limitations

# ============================================================================
# DEMONSTRATION: END-TO-END REFLECTIVE CYCLE
# ============================================================================

def run_demonstration():
    print("=" * 70)
    print("SHADOW MIRROR v1.0 -- Reflective Cycle Demonstration")
    print("=" * 70)

    urg = UnifiedReflectiveGraph()
    evidence_mgr = EvidenceManager(urg)
    context_engine = ContextEngine(urg)
    hypothesis_mgr = HypothesisManager(urg)
    belief_engine = BeliefRevisionEngine(urg)
    uncertainty_mgr = UncertaintyManager(urg)
    inquiry_planner = InquiryPlanner(urg)
    explanation_gen = ExplanationGenerator(urg)
    ewk_profile = EWKProfile(urg)
    limitation_framework = SelfLimitationFramework(urg)

    print("\n[1] Initializing Context...")
    ctx = context_engine.initialize_context(
        user_id="user_001",
        domain="educational_reflection",
        objectives=["improve_problem_solving", "identify_misconceptions"]
    )
    print(f"    Context ID: {ctx.context_id[:8]}")

    print("\n[2] Acquiring Observations & Constructing Evidence...")
    ev1 = evidence_mgr.construct_evidence(
        observation_id="obs_001",
        value=0.3,
        evidence_type=EvidenceType.KNOWLEDGE,
        source="problem_set_grader",
        reliability=0.95,
        uncertainty=0.1,
        context_refs=[ctx.context_id]
    )
    print(f"    Evidence 1 (Knowledge): Performance = {ev1.value} [id={ev1.evidence_id[:8]}]")

    ev2 = evidence_mgr.construct_evidence(
        observation_id="obs_002",
        value=0.75,
        evidence_type=EvidenceType.WILL,
        source="session_timer",
        reliability=0.9,
        uncertainty=0.15,
        context_refs=[ctx.context_id]
    )
    print(f"    Evidence 2 (Will): Persistence = {ev2.value} [id={ev2.evidence_id[:8]}]")

    ev3 = evidence_mgr.construct_evidence(
        observation_id="obs_003",
        value=0.8,
        evidence_type=EvidenceType.EMOTION,
        source="self_report",
        reliability=0.7,
        uncertainty=0.25,
        context_refs=[ctx.context_id]
    )
    print(f"    Evidence 3 (Emotion): Frustration = {ev3.value} [id={ev3.evidence_id[:8]}]")

    ewk_profile.ingest_evidence(ev1)
    ewk_profile.ingest_evidence(ev2)
    ewk_profile.ingest_evidence(ev3)

    print("\n[3] Generating Hypotheses...")
    h1 = hypothesis_mgr.generate_hypothesis(
        description="Student lacks prerequisite knowledge for current problem set",
        supporting_evidence=[ev1.evidence_id],
        assumptions=["prerequisite_knowledge_is_necessary"],
        context_refs=[ctx.context_id]
    )
    h2 = hypothesis_mgr.generate_hypothesis(
        description="Student has knowledge but is struggling with problem interpretation",
        supporting_evidence=[ev2.evidence_id, ev3.evidence_id],
        assumptions=["high_persistence_implies_some_knowledge"],
        context_refs=[ctx.context_id]
    )
    h3 = hypothesis_mgr.generate_hypothesis(
        description="Emotional state (frustration) is interfering with demonstrated competence",
        supporting_evidence=[ev3.evidence_id],
        assumptions=["affect_impairs_performance"],
        context_refs=[ctx.context_id]
    )
    print(f"    H1: {h1.description[:50]}... [id={h1.hypothesis_id[:8]}]")
    print(f"    H2: {h2.description[:50]}... [id={h2.hypothesis_id[:8]}]")
    print(f"    H3: {h3.description[:50]}... [id={h3.hypothesis_id[:8]}]")

    print("\n[4] Belief Revision (Bayesian Updating)...")
    belief_engine.revise_beliefs(
        ev1.evidence_id,
        [(h1.hypothesis_id, 0.9, 0.3),
         (h2.hypothesis_id, 0.4, 0.6),
         (h3.hypothesis_id, 0.3, 0.7)],
        evidence_reliability=ev1.reliability_score
    )
    belief_engine.revise_beliefs(
        ev2.evidence_id,
        [(h1.hypothesis_id, 0.2, 0.8),
         (h2.hypothesis_id, 0.8, 0.3),
         (h3.hypothesis_id, 0.6, 0.5)],
        evidence_reliability=ev2.reliability_score
    )
    belief_engine.revise_beliefs(
        ev3.evidence_id,
        [(h1.hypothesis_id, 0.3, 0.6),
         (h2.hypothesis_id, 0.5, 0.5),
         (h3.hypothesis_id, 0.85, 0.2)],
        evidence_reliability=ev3.reliability_score
    )

    for i, hid in enumerate([h1.hypothesis_id, h2.hypothesis_id, h3.hypothesis_id], 1):
        belief = urg.graph.nodes[hid]["data"]["current_belief"]
        print(f"    H{i} belief = {belief:.3f}")

    print("\n[5] Uncertainty Analysis...")
    unc1 = uncertainty_mgr.record_uncertainty(
        source="self_report_frustration",
        category=UncertaintyCategory.MEASUREMENT,
        magnitude=0.25,
        explanation="Self-reported emotions have higher measurement uncertainty than behavioral data",
        related_nodes=[ev3.evidence_id, h3.hypothesis_id]
    )
    unc2 = uncertainty_mgr.record_uncertainty(
        source="small_sample",
        category=UncertaintyCategory.STRUCTURAL,
        magnitude=0.4,
        explanation="Only 3 evidence items; explanatory coverage is limited",
        related_nodes=[h1.hypothesis_id, h2.hypothesis_id, h3.hypothesis_id]
    )
    print(f"    Recorded: {unc1.explanation[:50]}... [mag={unc1.magnitude}]")
    print(f"    Recorded: {unc2.explanation[:50]}... [mag={unc2.magnitude}]")

    print("\n[6] EWK Profile Tension Detection...")
    tension = ewk_profile.detect_tension()
    if tension:
        print(f"    TENSION DETECTED: {tension['tension_types']}")
        print(f"    Emotion={tension['emotion_avg']:.2f}, Will={tension['will_avg']:.2f}, Knowledge={tension['knowledge_avg']:.2f}")
    else:
        print("    No significant tension detected.")

    print("\n[7] Inquiry Planning...")
    inquiries = inquiry_planner.plan_inquiry(
        [h1.hypothesis_id, h2.hypothesis_id, h3.hypothesis_id],
        uncertainty_mgr
    )
    for inq in inquiries:
        print(f"    Inquiry: {inq.description[:50]}... [priority={inq.priority}, benefit={inq.expected_benefit:.2f}]")

    print("\n[8] Self-Limitation Check...")
    limitations = limitation_framework.check_scope(
        "educational_diagnosis",
        [ev1.evidence_id, ev2.evidence_id, ev3.evidence_id],
        [h1.hypothesis_id, h2.hypothesis_id, h3.hypothesis_id]
    )
    if limitations:
        for lim in limitations:
            print(f"    LIMITATION [{lim['severity'].upper()}]: {lim['description']}")
            print(f"      Recommendation: {lim['recommendation']}")
    else:
        print("    No limitations detected.")

    print("\n[9] Generating Explanation...")
    explanation = explanation_gen.generate_explanation(
        focus_hypotheses=[h1.hypothesis_id, h2.hypothesis_id, h3.hypothesis_id],
        context_id=ctx.context_id
    )
    print(f"    Explanation ID: {explanation.explanation_id[:8]}")
    print(f"    Summary: {explanation.summary[:120]}...")
    print(f"    Uncertainty: {explanation.uncertainty_summary}")

    print("\n[10] Unified Reflective Graph Statistics...")
    print(f"    Total nodes: {urg.graph.number_of_nodes()}")
    print(f"    Total edges: {urg.graph.number_of_edges()}")
    print(f"    Node types: {set(nx.get_node_attributes(urg.graph, 'node_type').values())}")
    print(f"    Cognitive tensions: {len(urg.find_cognitive_tension())}")

    print("\n" + "=" * 70)
    print("Reflective cycle complete. Human interpretation required.")
    print("=" * 70)

    return urg, explanation

if __name__ == "__main__":
    urg, explanation = run_demonstration()
