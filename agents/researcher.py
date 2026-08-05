import asyncio
import time

from agents.base import BaseAgent
from core.llm_client import LLMClient
from core.search_client import WebSearchClient
from core.models import AgentResult


class ResearcherAgent(BaseAgent):
    """
    Unlike the other agents, this one is grounded in real web search results
    (via Tavily) rather than LLM knowledge alone — competitor names, market
    trend claims, and validation ideas are based on live search snippets
    passed into the prompt, not the model's training data. See README
    "Mocked vs Real" for the exact scope of this.
    """

    name = "researcher"
    system_prompt = (
        "You are a Research Agent. You are given real, current web search "
        "results about a market. Use them to ground your competitor analysis "
        "— cite specific companies and facts that appear in the search "
        "results rather than inventing them. If the results are thin, say so "
        "explicitly instead of filling gaps with guesses."
    )

    def __init__(self, llm_client: LLMClient, search_client: WebSearchClient):
        super().__init__(llm_client)
        self.search_client = search_client

    def build_user_prompt(self, topic: str, **context: str) -> str:
        search_summary = context.get("search_summary", "No search results available.")
        return (
            f"Topic: {topic}\n\n"
            f"Live web search results:\n{search_summary}\n\n"
            "Using the results above, produce:\n"
            "1. Top competitors (name real companies found in the search results)\n"
            "2. Differentiation opportunities\n"
            "3. Target market segments\n"
            "4. 2-3 concrete market validation experiments\n"
        )

    async def run(self, topic: str, **context: str) -> AgentResult:
        start = time.monotonic()

        try:
            results = await asyncio.to_thread(
                self.search_client.search, f"{topic} startup competitors market"
            )
            search_summary = self.search_client.format_for_prompt(results)
        except Exception as e:
            # Search failing shouldn't kill the whole agent — fall back to
            # LLM-only reasoning, but say so explicitly in the output.
            search_summary = f"[Web search unavailable: {e}]"

        try:
            user_prompt = self.build_user_prompt(topic, search_summary=search_summary)
            content = await asyncio.to_thread(
                self.llm_client.generate, self.system_prompt, user_prompt
            )
            return AgentResult(
                agent_name=self.name,
                content=content,
                succeeded=True,
                duration_seconds=time.monotonic() - start,
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                content="",
                succeeded=False,
                error=str(e),
                duration_seconds=time.monotonic() - start,
            )
