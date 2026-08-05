"""
Optional Gradio UI. Not the primary interface — the CLI (main.py) is —
but kept as a thin wrapper to show the same orchestrator working behind
a different front end. Run: python app.py
"""
from __future__ import annotations

import asyncio

import gradio as gr

from config import ConfigError, load_settings
from core.llm_client import LLMClient
from core.search_client import WebSearchClient
from core.orchestrator import build_default_orchestrator
from core.run_store import save_run

try:
    _settings = load_settings()
    _llm_client = LLMClient(_settings)
    _search_client = WebSearchClient(_settings)
    _orchestrator = build_default_orchestrator(_llm_client, _search_client)
    _config_error = None
except ConfigError as e:
    _config_error = str(e)


def run_topic(topic: str) -> str:
    if _config_error:
        return f"Configuration error: {_config_error}"
    if not topic or not topic.strip():
        return "Please enter a business topic (e.g., 'Health tech using wearables')."

    try:
        pipeline_run = asyncio.run(_orchestrator.run(topic.strip()))
        save_run(pipeline_run, _settings.output_dir)
        if not pipeline_run.final_blueprint:
            failures = [
                f"{name}: {r.error}"
                for name, r in pipeline_run.results.items()
                if not r.succeeded
            ]
            return "Pipeline did not produce a final blueprint. Failures:\n" + "\n".join(failures)
        return pipeline_run.final_blueprint
    except Exception as e:
        return f"Error: {e}"


with gr.Blocks(title="Strategic Co-Founder Agent") as demo:
    gr.Markdown("# Strategic Co-Founder — Multi-Agent")
    gr.Markdown(
        "Planner, researcher (real web search), strategist, and financial "
        "modeler run in parallel; a writer agent synthesizes the final "
        "blueprint and pitch deck outline."
    )
    with gr.Row():
        topic_input = gr.Textbox(label="Business idea (one line)", placeholder="e.g., Health tech using wearables")
        run_btn = gr.Button("Generate Business Blueprint")
    output_box = gr.Textbox(label="Final blueprint", lines=25)
    run_btn.click(fn=run_topic, inputs=topic_input, outputs=output_box)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
