from agents.base import BaseAgent


class StrategistAgent(BaseAgent):
    name = "strategist"
    system_prompt = (
        "You are a Business Strategy Agent. Produce go-to-market strategy, "
        "pricing, and SWOT analysis. Be specific to the given topic — avoid "
        "generic advice that could apply to any startup."
    )

    def build_user_prompt(self, topic: str, **context: str) -> str:
        return (
            f"For this startup theme: {topic}\n\n"
            "Produce:\n"
            "1. Revenue model options\n"
            "2. Pricing tiers\n"
            "3. Go-to-market strategy\n"
            "4. SWOT analysis\n"
        )
