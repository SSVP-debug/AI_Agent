"""
Base class every agent extends. Owns the one piece of logic that would
otherwise be copy-pasted five times: timing, error isolation, and turning
whatever an agent produces into a well-formed AgentResult (so one agent
failing never crashes the whole pipeline — see orchestrator.py).
"""
from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod

from core.llm_client import LLMClient
from core.models import AgentResult


class BaseAgent(ABC):
    name: str
    system_prompt: str

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    @abstractmethod
    def build_user_prompt(self, topic: str, **context: str) -> str:
        """Construct the user prompt for this agent given the topic and any
        upstream context (e.g. writer needs the other agents' outputs)."""

    async def run(self, topic: str, **context: str) -> AgentResult:
        start = time.monotonic()
        try:
            user_prompt = self.build_user_prompt(topic, **context)
            # LLMClient.generate is a blocking network call; running it in a
            # worker thread is what lets the orchestrator await several
            # agents concurrently instead of one call blocking the loop.
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
