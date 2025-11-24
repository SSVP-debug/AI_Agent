# agents/strategy.py
from core.llm import llm_chat
from core.memory import remember

def strategist_agent(topic: str) -> str:
    system = "You are a Business Strategy Agent. Produce revenue models, pricing, GTM, and SWOT."
    user = (
        f"Create: revenue model options, pricing tiers, go-to-market strategy, cost structure, "
        f"and a SWOT analysis for: {topic}."
    )
    out = llm_chat(system, user)
    remember("strategy", out)
    return out
