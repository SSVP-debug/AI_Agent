"""
Graph-based orchestration for the agent pipeline.

Rather than hardcoding "run planner, then researcher, then strategist, then
writer" as a sequential script, the pipeline is expressed as an explicit
dependency graph (a DAG): each node names which other nodes' outputs it
needs. The engine resolves that graph into layers via a topological sort
(Kahn's algorithm) and runs every node within a layer concurrently.

For this pipeline, that resolves to two layers:
  Layer 1 (parallel): planner, researcher, strategist, financial_modeler
  Layer 2:            writer  (depends on all four)

Layer 1 has no real dependencies between its nodes — the original repo ran
them sequentially anyway, so this cuts wall-clock time roughly 3-4x on that
stage. The graph representation also means adding a sixth agent later is a
one-node addition here, not a rewrite of the control flow.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from agents.base import BaseAgent
from core.models import AgentResult, PipelineRun


class GraphError(RuntimeError):
    """Raised for malformed graphs (missing dependency, cycle)."""


@dataclass
class Node:
    name: str
    agent: BaseAgent
    depends_on: list[str] = field(default_factory=list)
    # Key this node's output is exposed under to its dependents' prompts.
    # None for terminal nodes (nothing depends on them).
    context_key: str | None = None


def _topological_layers(nodes: dict[str, Node]) -> list[list[str]]:
    """Kahn's algorithm, grouped into layers that can run concurrently."""
    in_degree = {n: len(node.depends_on) for n, node in nodes.items()}
    for n, node in nodes.items():
        for dep in node.depends_on:
            if dep not in nodes:
                raise GraphError(f"Node '{n}' depends on unknown node '{dep}'")

    layers: list[list[str]] = []
    remaining = dict(in_degree)

    while remaining:
        ready = [n for n, deg in remaining.items() if deg == 0]
        if not ready:
            raise GraphError(f"Cycle detected among nodes: {list(remaining)}")
        layers.append(ready)
        for n in ready:
            del remaining[n]
        for n in remaining:
            for dep in nodes[n].depends_on:
                if dep in ready:
                    remaining[n] -= 1

    return layers


class Orchestrator:
    def __init__(self, nodes: list[Node]):
        self._nodes = {n.name: n for n in nodes}
        self._layers = _topological_layers(self._nodes)

    async def run(self, topic: str) -> PipelineRun:
        run = PipelineRun(run_id=str(uuid.uuid4())[:8], topic=topic)
        context: dict[str, str] = {}

        for layer in self._layers:
            layer_results = await asyncio.gather(
                *(self._run_node(self._nodes[name], topic, context) for name in layer)
            )
            for name, result in zip(layer, layer_results):
                run.results[name] = result
                node = self._nodes[name]
                if node.context_key and result.succeeded:
                    context[node.context_key] = result.content

        writer_result = run.results.get("writer")
        run.final_blueprint = writer_result.content if writer_result and writer_result.succeeded else ""
        run.finished_at = datetime.now(timezone.utc).isoformat()
        return run

    async def _run_node(self, node: Node, topic: str, context: dict[str, str]) -> AgentResult:
        # Only pass through the context keys this node's declared dependencies
        # actually produced — an agent can't accidentally read data it wasn't
        # declared to depend on.
        relevant_context = {
            self._nodes[dep].context_key: context[self._nodes[dep].context_key]
            for dep in node.depends_on
            if self._nodes[dep].context_key in context
        }
        return await node.agent.run(topic, **relevant_context)


def build_default_orchestrator(
    llm_client, search_client
) -> Orchestrator:
    """Wires up the standard 5-agent graph. Kept separate from Orchestrator
    itself so tests can build orchestrators with mock agents instead."""
    from agents.planner import PlannerAgent
    from agents.researcher import ResearcherAgent
    from agents.strategist import StrategistAgent
    from agents.financial_modeler import FinancialModelerAgent
    from agents.writer import WriterAgent

    nodes = [
        Node("planner", PlannerAgent(llm_client), context_key="plan"),
        Node("researcher", ResearcherAgent(llm_client, search_client), context_key="research"),
        Node("strategist", StrategistAgent(llm_client), context_key="strategy"),
        Node("financial_modeler", FinancialModelerAgent(llm_client), context_key="financials"),
        Node(
            "writer",
            WriterAgent(llm_client),
            depends_on=["planner", "researcher", "strategist", "financial_modeler"],
        ),
    ]
    return Orchestrator(nodes)
