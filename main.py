"""
CLI entrypoint. Usage: python main.py
"""
from __future__ import annotations

import asyncio
import sys

from config import ConfigError, load_settings
from core.llm_client import LLMClient
from core.search_client import WebSearchClient
from core.orchestrator import build_default_orchestrator
from core.run_store import save_run


async def run(topic: str) -> None:
    settings = load_settings()
    llm_client = LLMClient(settings)
    search_client = WebSearchClient(settings)
    orchestrator = build_default_orchestrator(llm_client, search_client)

    print(f"[Running pipeline for: {topic}]")
    print("[Planning, research, strategy, and financial model run in parallel...]")

    pipeline_run = await orchestrator.run(topic)

    for name, result in pipeline_run.results.items():
        status = "ok" if result.succeeded else f"FAILED ({result.error})"
        print(f"  - {name}: {status} ({result.duration_seconds:.1f}s)")

    if not pipeline_run.succeeded:
        print("\n[Some agents failed — writer proceeded with whatever succeeded.]")

    run_dir = save_run(pipeline_run, settings.output_dir)
    print(f"\n===== FINAL BUSINESS BLUEPRINT =====\n")
    print(pipeline_run.final_blueprint or "(writer did not produce output)")
    print(f"\nSaved full run to {run_dir}/")


def main() -> None:
    try:
        topic = input("Enter business idea theme: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return

    if not topic:
        print("Please provide a topic.")
        return

    try:
        asyncio.run(run(topic))
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
