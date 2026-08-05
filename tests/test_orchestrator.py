import asyncio
import time

import pytest

from core.orchestrator import Node, Orchestrator, GraphError
from core.models import AgentResult


class MockAgent:
    """Duck-typed agent for orchestrator tests — no LLM involved at all,
    just controllable async behavior."""

    def __init__(self, name: str, delay: float = 0.0, content: str = "output",
                 succeeded: bool = True, capture_context: dict | None = None):
        self.name = name
        self.delay = delay
        self.content = content
        self.succeeded = succeeded
        self.capture_context = capture_context  # dict to record received context into

    async def run(self, topic: str, **context) -> AgentResult:
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.capture_context is not None:
            self.capture_context.update(context)
        return AgentResult(
            agent_name=self.name,
            content=self.content,
            succeeded=self.succeeded,
            error=None if self.succeeded else "mock failure",
        )


def test_independent_nodes_form_a_single_layer():
    nodes = [
        Node("a", MockAgent("a")),
        Node("b", MockAgent("b")),
        Node("c", MockAgent("c")),
    ]
    orchestrator = Orchestrator(nodes)
    assert len(orchestrator._layers) == 1
    assert set(orchestrator._layers[0]) == {"a", "b", "c"}


def test_dependent_node_forms_second_layer():
    nodes = [
        Node("a", MockAgent("a"), context_key="a_out"),
        Node("b", MockAgent("b"), context_key="b_out"),
        Node("writer", MockAgent("writer"), depends_on=["a", "b"]),
    ]
    orchestrator = Orchestrator(nodes)
    assert len(orchestrator._layers) == 2
    assert set(orchestrator._layers[0]) == {"a", "b"}
    assert orchestrator._layers[1] == ["writer"]


def test_cycle_raises_graph_error():
    nodes = [
        Node("a", MockAgent("a"), depends_on=["b"]),
        Node("b", MockAgent("b"), depends_on=["a"]),
    ]
    with pytest.raises(GraphError):
        Orchestrator(nodes)


def test_missing_dependency_raises_graph_error():
    nodes = [Node("a", MockAgent("a"), depends_on=["nonexistent"])]
    with pytest.raises(GraphError):
        Orchestrator(nodes)


@pytest.mark.asyncio
async def test_independent_agents_actually_run_concurrently():
    """The core claim of this rebuild: planner/researcher/strategist/
    financial_modeler run in parallel, not sequentially. Prove it with
    timing — three 0.2s agents run sequentially would take >=0.6s; run
    concurrently they should take well under that."""
    nodes = [
        Node("a", MockAgent("a", delay=0.2)),
        Node("b", MockAgent("b", delay=0.2)),
        Node("c", MockAgent("c", delay=0.2)),
    ]
    orchestrator = Orchestrator(nodes)

    start = time.monotonic()
    await orchestrator.run("test topic")
    elapsed = time.monotonic() - start

    assert elapsed < 0.4, f"expected concurrent execution, took {elapsed:.2f}s"


@pytest.mark.asyncio
async def test_fan_in_node_receives_upstream_context():
    captured: dict = {}
    nodes = [
        Node("planner", MockAgent("planner", content="PLAN_TEXT"), context_key="plan"),
        Node(
            "writer",
            MockAgent("writer", capture_context=captured),
            depends_on=["planner"],
        ),
    ]
    orchestrator = Orchestrator(nodes)
    await orchestrator.run("test topic")

    assert captured.get("plan") == "PLAN_TEXT"


@pytest.mark.asyncio
async def test_failed_node_does_not_propagate_into_context():
    """If an upstream node fails, its context_key must not appear in the
    downstream node's context — a failed agent shouldn't silently inject
    empty/garbage content into the writer's prompt."""
    captured: dict = {}
    nodes = [
        Node("planner", MockAgent("planner", succeeded=False), context_key="plan"),
        Node("writer", MockAgent("writer", capture_context=captured), depends_on=["planner"]),
    ]
    orchestrator = Orchestrator(nodes)
    run = await orchestrator.run("test topic")

    assert run.results["planner"].succeeded is False
    assert "plan" not in captured


@pytest.mark.asyncio
async def test_pipeline_run_final_blueprint_comes_from_writer():
    nodes = [
        Node("writer", MockAgent("writer", content="FINAL_BLUEPRINT_TEXT")),
    ]
    orchestrator = Orchestrator(nodes)
    run = await orchestrator.run("test topic")

    assert run.final_blueprint == "FINAL_BLUEPRINT_TEXT"
    assert run.succeeded is True
    assert run.finished_at is not None
