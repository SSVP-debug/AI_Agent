"""
Shared data shapes passed between agents, the orchestrator, and the run store.
Keeping these as explicit dataclasses (instead of raw dicts/strings) is what
lets the orchestrator reason about the pipeline as a graph rather than a
sequence of string concatenations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AgentResult:
    agent_name: str
    content: str
    succeeded: bool
    error: str | None = None
    duration_seconds: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class PipelineRun:
    run_id: str
    topic: str
    results: dict[str, AgentResult] = field(default_factory=dict)
    final_blueprint: str = ""
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: str | None = None

    @property
    def succeeded(self) -> bool:
        return all(r.succeeded for r in self.results.values())
