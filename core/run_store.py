"""
Persists each pipeline run to disk under OUTPUT_DIR/<run_id>/.

This replaces the old repo's memory.py / memory.json. That name implied
agents had persistent memory across runs — they don't; every run starts
fresh with no recall of prior runs. What it actually did, and what this
does, is log each run's outputs for later inspection. "Run store" says
that honestly.
"""
from __future__ import annotations

import json
import os

from core.models import PipelineRun


def save_run(run: PipelineRun, output_dir: str) -> str:
    """Writes the run to output_dir/<run_id>/ as individual agent output
    files plus a run.json manifest. Returns the run's directory path."""
    run_dir = os.path.join(output_dir, run.run_id)
    os.makedirs(run_dir, exist_ok=True)

    for agent_name, result in run.results.items():
        path = os.path.join(run_dir, f"{agent_name}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(result.content if result.succeeded else f"[FAILED: {result.error}]")

    if run.final_blueprint:
        with open(os.path.join(run_dir, "final_blueprint.md"), "w", encoding="utf-8") as f:
            f.write(run.final_blueprint)

    manifest = {
        "run_id": run.run_id,
        "topic": run.topic,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "succeeded": run.succeeded,
        "agents": {
            name: {
                "succeeded": r.succeeded,
                "error": r.error,
                "duration_seconds": round(r.duration_seconds, 2),
            }
            for name, r in run.results.items()
        },
    }
    with open(os.path.join(run_dir, "run.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return run_dir
