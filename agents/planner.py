# agents/planner.py
from core.llm import llm_chat
from core.memory import remember

def planner_agent(topic: str) -> str:
    system = "You are a Business Planning Agent. Break ideas into structured work items and milestones."
    user = (
        f"Create a detailed project plan and milestone list for building a startup "
        f"based on this theme: {topic}. Include feature set, MVP scope, and 8-week roadmap."
    )
    out = llm_chat(system, user)
    remember("planner", out)
    return out
