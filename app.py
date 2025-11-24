# app.py
import gradio as gr
from core.orchestrator import run_pipeline
from core.memory import load_memory

def ui_memory_text():
    mem = load_memory()
    if not mem:
        return "Memory is empty."
    return "\n\n".join([f"[{m['role']}] {m['content'][:300]}..." for m in mem])

def run_topic(topic):
    if not topic or topic.strip() == "":
        return "Please enter a business topic (e.g., 'Health tech using wearables')."
    try:
        output = run_pipeline(topic)
        return output
    except Exception as e:
        return f"Error: {e}"

with gr.Blocks(title="Strategic Co-Founder Agent") as demo:
    gr.Markdown("# Strategic Co-Founder — Multi-Agent")
    with gr.Row():
        topic_input = gr.Textbox(label="Business idea (one line)", placeholder="e.g., Health tech using wearables")
        run_btn = gr.Button("Generate Business Blueprint")
    output_box = gr.Textbox(label="Final output", lines=25)
    run_btn.click(fn=run_topic, inputs=topic_input, outputs=output_box)

    # optional: show memory
    with gr.Accordion("View memory (saved agent outputs)", open=False):
        memory_box = gr.Textbox(label="Agent Memory", lines=10, value=ui_memory_text)

        gr.Markdown("Memory displays the most recent saved snippets (persisted in memory.json).")

if __name__ == "__main__":
    demo.launch()
