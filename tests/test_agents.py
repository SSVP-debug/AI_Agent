import pytest

from agents.planner import PlannerAgent
from agents.strategist import StrategistAgent
from agents.financial_modeler import FinancialModelerAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent


@pytest.mark.asyncio
async def test_planner_includes_topic_in_prompt(fake_llm):
    agent = PlannerAgent(fake_llm)
    result = await agent.run("pet grooming marketplace")

    assert result.succeeded
    assert result.content == fake_llm.response
    _, user_prompt = fake_llm.calls[0]
    assert "pet grooming marketplace" in user_prompt


@pytest.mark.asyncio
async def test_strategist_produces_result(fake_llm):
    agent = StrategistAgent(fake_llm)
    result = await agent.run("EV charging network")

    assert result.succeeded
    assert "EV charging network" in fake_llm.calls[0][1]


@pytest.mark.asyncio
async def test_financial_modeler_produces_result(fake_llm):
    agent = FinancialModelerAgent(fake_llm)
    result = await agent.run("subscription meal kits")

    assert result.succeeded
    assert "assumptions" in agent.system_prompt.lower()


@pytest.mark.asyncio
async def test_agent_failure_is_isolated_not_raised(failing_llm):
    """An agent whose LLM call fails must return a failed AgentResult,
    never raise — this is what lets the orchestrator keep other branches
    of the graph running."""
    agent = PlannerAgent(failing_llm)
    result = await agent.run("drone delivery for pharmacies")

    assert result.succeeded is False
    assert "simulated LLM failure" in result.error


@pytest.mark.asyncio
async def test_researcher_falls_back_when_search_fails(fake_llm, monkeypatch):
    from tests.conftest import FakeSearchClient

    failing_search = FakeSearchClient(should_fail=True)
    agent = ResearcherAgent(fake_llm, failing_search)

    result = await agent.run("urban vertical farming")

    # Search failing must not fail the whole agent — it should fall back
    # to an explicit "unavailable" note in the prompt and still call the LLM.
    assert result.succeeded is True
    _, user_prompt = fake_llm.calls[0]
    assert "Web search unavailable" in user_prompt


@pytest.mark.asyncio
async def test_writer_synthesizes_all_upstream_context(fake_llm):
    agent = WriterAgent(fake_llm)
    await agent.run(
        "co-working spaces for freelancers",
        plan="PLAN_CONTENT",
        research="RESEARCH_CONTENT",
        strategy="STRATEGY_CONTENT",
        financials="FINANCIALS_CONTENT",
    )

    _, user_prompt = fake_llm.calls[0]
    for expected in ["PLAN_CONTENT", "RESEARCH_CONTENT", "STRATEGY_CONTENT", "FINANCIALS_CONTENT"]:
        assert expected in user_prompt


@pytest.mark.asyncio
async def test_writer_handles_missing_upstream_context_gracefully(fake_llm):
    """If an upstream agent failed, writer should still run — it just gets
    a placeholder instead of crashing on a missing key."""
    agent = WriterAgent(fake_llm)
    result = await agent.run("co-working spaces for freelancers")

    assert result.succeeded is True
    _, user_prompt = fake_llm.calls[0]
    assert "no output" in user_prompt
