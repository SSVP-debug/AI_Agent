# agents/writer.py
from core.llm import llm_chat
from core.memory import remember

def writer_agent(topic: str, planning: str, research: str, strategy: str) -> str:
    system = "You are a Startup Report Writer. Produce a polished business plan + pitch deck."
    user = (
        f"Topic: {topic}\n\n"
        f"Planning:\n{planning}\n\n"
        f"Research:\n{research}\n\n"
        f"Strategy:\n{strategy}\n\n"
        "Combine into a single final business blueprint, and produce a 10-slide pitch deck outline."
    )
    out = llm_chat(system, user, temperature=0.3, max_tokens=2000)
    remember("writer", out)
    return out
