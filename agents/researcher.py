# agents/research.py
from core.llm import llm_chat
from core.memory import remember

def researcher_agent(topic: str) -> str:
    system = "You are a Research Agent. Provide competitor analysis, market trends, and validation steps."
    user = (
        f"Do competitor analysis, top 5 competitors, differentiation, target segments, "
        f"and market validation experiments for: {topic}."
    )
    out = llm_chat(system, user)
    remember("research", out)
    return out
