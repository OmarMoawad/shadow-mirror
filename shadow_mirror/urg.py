"""The Unified Reflective Graph.

One graph holds observations, evidence, context, hypotheses, beliefs, inquiries
and explanations, connected by typed edges. The point is not storage -- it is
that every conclusion stays reachable from the evidence that produced it, and
that contradiction is a first-class edge rather than something a later write
silently overwrites.

Two deliberate choices:

* **No third-party graph library.** The rest of Shadow Mirror is standard library
  only, on purpose: local-first and auditable. Importing NetworkX for an
  adjacency dict would trade that for nothing. It also removes the deprecated
  ``node_link_data`` call in the v1.0 prototype (D-16).

* **Provenance is a DAG, not a chain.** ``ancestors()`` walks *every* provenance
  parent. The prototype followed ``preds[0]`` only, so a piece of evidence
  derived from two sources reported one of them and silently dropped the other --
  which violates the architecture's own Invariant II (D-14).
"""

from __future__ import annotations

import json
import uuid
import copy
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional, Set, Tuple

# Typed node kinds. Anything else is rejected at insertion time, because an
# untyped graph cannot support a traceability invariant.
NODE_TYPES = (
    "Observation", "Evidence", "Context", "Hypothesis",
    "Belief", "Inquiry", "Explanation", "Knowledge", "Limitation",
)

# Typed edges. `contradicts` is deliberately as first-class as `supports`.
EDGE_TYPES = (
    "provenance",       # child -> parent origin (many parents allowed)
    "supports",         # evidence -> hypothesis
    "contradicts",      # evidence -> hypothesis
    "contextualises",   # context -> anything
    "revises",          # newer -> older
    "targets",          # inquiry -> hypothesis
    "explains",         # explanation -> hypothesis
    "limits",           # limitation -> anything
)


def _now() -> str:
    """Timezone-aware ISO timestamp.

    v1.0 (D-15): the prototype used the naive ``datetime.utcnow()`` while the
    engine used aware timestamps, so the two could not be compared without a
    TypeError. Everything is aware now. ``utcnow()`` is also deprecated from
    Python 3.12 and slated for removal.
    """
    return datetime.now(timezone.utc).isoformat()


class URGError(ValueError):
    pass


class UnifiedReflectiveGraph:
    """A typed, append-oriented reflective graph."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._out: Dict[str, List[Tuple[str, str, Dict[str, Any]]]] = {}
        self._in: Dict[str, List[Tuple[str, str, Dict[str, Any]]]] = {}
        self._seq = 0

    # -- construction ------------------------------------------------------
    def add_node(self, node_type: str, data: Optional[Dict[str, Any]] = None,
                 node_id: Optional[str] = None) -> str:
        if node_type not in NODE_TYPES:
            raise URGError(f"unknown node type {node_type!r}")
        nid = node_id or str(uuid.uuid4())
        if nid in self._nodes:
            raise URGError(f"node {nid} already exists; use update_node")
        self._nodes[nid] = {
            "id": nid, "node_type": node_type, "data": dict(data or {}),
            "seq": self._seq, "created": _now(),
        }
        self._seq += 1
        self._out.setdefault(nid, [])
        self._in.setdefault(nid, [])
        return nid

    def update_node(self, node_id: str, **fields: Any) -> None:
        if node_id not in self._nodes:
            raise URGError(f"no such node {node_id}")
        self._nodes[node_id]["data"].update(fields)
        self._nodes[node_id]["updated"] = _now()

    def add_edge(self, source: str, target: str, relationship: str,
                 **attrs: Any) -> None:
        if relationship not in EDGE_TYPES:
            raise URGError(f"unknown edge type {relationship!r}")
        for n in (source, target):
            if n not in self._nodes:
                raise URGError(f"no such node {n}")
        rec = dict(attrs)
        rec["timestamp"] = _now()
        self._out[source].append((target, relationship, rec))
        self._in[target].append((source, relationship, rec))

    # -- access ------------------------------------------------------------
    def node(self, node_id: str) -> Dict[str, Any]:
        return self._nodes[node_id]

    def __contains__(self, node_id: object) -> bool:
        return node_id in self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    def n_edges(self) -> int:
        return sum(len(v) for v in self._out.values())

    def nodes_of_type(self, node_type: str) -> List[str]:
        return [n for n, d in self._nodes.items() if d["node_type"] == node_type]

    def successors(self, node_id: str, relationship: Optional[str] = None) -> List[str]:
        return [t for t, r, _ in self._out.get(node_id, [])
                if relationship is None or r == relationship]

    def predecessors(self, node_id: str, relationship: Optional[str] = None) -> List[str]:
        return [s for s, r, _ in self._in.get(node_id, [])
                if relationship is None or r == relationship]

    def supporting_evidence(self, hypothesis_id: str) -> List[str]:
        return self.predecessors(hypothesis_id, "supports")

    def contradicting_evidence(self, hypothesis_id: str) -> List[str]:
        return self.predecessors(hypothesis_id, "contradicts")

    # -- provenance (Invariant II) ----------------------------------------
    def ancestors(self, node_id: str, relationship: str = "provenance") -> Set[str]:
        """Every reachable provenance ancestor, not just the first one.

        v1.0 (D-14): the prototype's ``trace_provenance`` walked ``preds[0]``
        only, so evidence merged from two sources reported one parent and
        silently discarded the other. That is a direct violation of Invariant II
        (Provenance Preservation), and the Session 2 conformance check caught it.
        """
        if node_id not in self._nodes:
            return set()
        seen: Set[str] = set()
        queue = deque(self.predecessors(node_id, relationship))
        while queue:
            cur = queue.popleft()
            if cur in seen:
                continue
            seen.add(cur)
            queue.extend(self.predecessors(cur, relationship))
        return seen

    def provenance_paths(self, node_id: str,
                         relationship: str = "provenance") -> List[List[str]]:
        """All root-to-node provenance paths. Cycles are cut, not followed."""
        paths: List[List[str]] = []

        def walk(cur: str, path: List[str]) -> None:
            parents = self.predecessors(cur, relationship)
            fresh = [p for p in parents if p not in path]
            if not fresh:
                paths.append(list(reversed(path)))
                return
            for p in fresh:
                walk(p, path + [p])

        walk(node_id, [node_id])
        return paths

    # -- reflective queries ------------------------------------------------
    def contested_hypotheses(self) -> List[Tuple[str, List[str], List[str]]]:
        """Hypotheses carrying both supporting and contradicting evidence.

        Contradiction is held, not resolved. This is what lets an explanation
        report a tension instead of quietly preferring the later write.
        """
        out = []
        for h in self.nodes_of_type("Hypothesis"):
            sup = self.supporting_evidence(h)
            con = self.contradicting_evidence(h)
            if sup and con:
                out.append((h, sup, con))
        return out

    def orphan_conclusions(self) -> List[str]:
        """Explanations with no reachable evidence: Invariant I violations."""
        bad = []
        for e in self.nodes_of_type("Explanation"):
            reach = set()
            for h in self.successors(e, "explains") + self.predecessors(e, "explains"):
                reach |= set(self.supporting_evidence(h))
                reach |= set(self.contradicting_evidence(h))
            if not reach:
                bad.append(e)
        return bad

    # -- context consistency (Invariant VI) --------------------------------
    def revise_context(self, old_context_id: str, data: Dict[str, Any]) -> str:
        """Supersede a context and mark everything that depended on it as stale.

        Invariant VI says a contextual change must trigger recomputation *or*
        explicit annotation. Annotation is the honest option for an instrument
        that cannot recompute a person's past: the conclusion is not deleted, it
        is marked as having been reached under a context that no longer holds.
        """
        new_id = self.add_node("Context", data)
        self.add_edge(new_id, old_context_id, "revises")
        for dependent in self.successors(old_context_id, "contextualises"):
            self.update_node(dependent, stale=True, stale_since=_now(),
                             superseded_context=old_context_id)
        return new_id

    def stale_nodes(self) -> List[str]:
        return [n for n, d in self._nodes.items() if d["data"].get("stale")]

    def contextualise(self, context_id: str, target_id: str) -> None:
        self.add_edge(context_id, target_id, "contextualises")

    # -- transactional consistency (Invariant IX) --------------------------
    @contextmanager
    def transaction(self) -> Iterator["UnifiedReflectiveGraph"]:
        """All-or-nothing updates across nodes and edges.

        Invariant IX requires reflective state updates to be atomic across
        beliefs, uncertainty and provenance. Without this a failure part-way
        through leaves a hypothesis whose belief moved but whose provenance edge
        was never written -- which silently violates Invariant I as well.
        """
        snapshot = (copy.deepcopy(self._nodes), copy.deepcopy(self._out),
                    copy.deepcopy(self._in), self._seq)
        try:
            yield self
        except Exception:
            self._nodes, self._out, self._in, self._seq = snapshot
            raise

    # -- serialisation -----------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        edges = []
        for src, lst in self._out.items():
            for tgt, rel, attrs in lst:
                edges.append({"source": src, "target": tgt,
                              "relationship": rel, **attrs})
        return {"nodes": list(self._nodes.values()), "edges": edges}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "UnifiedReflectiveGraph":
        g = cls()
        for n in d["nodes"]:
            g.add_node(n["node_type"], n.get("data"), node_id=n["id"])
        for e in d["edges"]:
            attrs = {k: v for k, v in e.items()
                     if k not in ("source", "target", "relationship", "timestamp")}
            g.add_edge(e["source"], e["target"], e["relationship"], **attrs)
        return g
