"""
Shared fixtures. Every test in this suite runs with zero network calls —
FakeLLMClient and FakeSearchClient are duck-typed stand-ins for LLMClient
and WebSearchClient (same methods, no external calls).
"""
from __future__ import annotations

import pytest


class FakeLLMClient:
    """Duck-typed stand-in for core.llm_client.LLMClient."""

    def __init__(self, response: str = "fake llm response", should_fail: bool = False):
        self.response = response
        self.should_fail = should_fail
        self.calls: list[tuple[str, str]] = []

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3,
                 max_output_tokens: int = 2000) -> str:
        self.calls.append((system_prompt, user_prompt))
        if self.should_fail:
            raise RuntimeError("simulated LLM failure")
        return self.response


class FakeSearchClient:
    """Duck-typed stand-in for core.search_client.WebSearchClient."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    def search(self, query: str, max_results: int = 5):
        if self.should_fail:
            raise RuntimeError("simulated search failure")
        return []

    @staticmethod
    def format_for_prompt(results) -> str:
        return "No search results found." if not results else str(results)


@pytest.fixture
def fake_llm():
    return FakeLLMClient()


@pytest.fixture
def failing_llm():
    return FakeLLMClient(should_fail=True)


@pytest.fixture
def fake_search():
    return FakeSearchClient()
