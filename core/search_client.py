"""
Thin wrapper around Tavily's search API. This is what makes competitor
research "real" rather than purely LLM-knowledge-based — see README
"Mocked vs Real" section for exactly what this does and doesn't cover.
"""
from __future__ import annotations

from dataclasses import dataclass

from tavily import TavilyClient

from config import Settings


class SearchError(RuntimeError):
    """Raised when the search provider fails or returns nothing usable."""


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


@dataclass
class WebSearchClient:
    settings: Settings

    def __post_init__(self) -> None:
        self._client = TavilyClient(api_key=self.settings.tavily_api_key)

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        try:
            response = self._client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
            )
        except Exception as e:
            raise SearchError(f"Tavily search failed for query '{query}': {e}") from e

        results = response.get("results", [])
        return [
            SearchResult(
                title=r.get("title", "Untitled"),
                url=r.get("url", ""),
                snippet=r.get("content", ""),
            )
            for r in results
        ]

    @staticmethod
    def format_for_prompt(results: list[SearchResult]) -> str:
        if not results:
            return "No search results found."
        lines = []
        for i, r in enumerate(results, start=1):
            lines.append(f"{i}. {r.title} ({r.url})\n   {r.snippet[:400]}")
        return "\n".join(lines)
