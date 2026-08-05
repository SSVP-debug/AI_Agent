from agents.base import BaseAgent


class WriterAgent(BaseAgent):
    """
    The one agent that isn't independent — it's the fan-in node, and only
    runs after planner, researcher, strategist, and financial_modeler have
    all completed. See core/orchestrator.py for the dependency graph.
    """

    name = "writer"
    system_prompt = (
        "You are a Startup Report Writer. Synthesize the inputs into a single "
        "coherent business blueprint plus a 10-slide pitch deck outline. Do "
        "not just concatenate the sections — resolve overlaps and write it as "
        "one cohesive document."
    )

    def build_user_prompt(self, topic: str, **context: str) -> str:
        plan = context.get("plan", "(planning agent produced no output)")
        research = context.get("research", "(research agent produced no output)")
        strategy = context.get("strategy", "(strategy agent produced no output)")
        financials = context.get("financials", "(financial model agent produced no output)")

        return (
            f"Topic: {topic}\n\n"
            f"Planning:\n{plan}\n\n"
            f"Research:\n{research}\n\n"
            f"Strategy:\n{strategy}\n\n"
            f"Financial Model:\n{financials}\n\n"
            "Combine the above into:\n"
            "1. A single final business blueprint (well-organized, no duplication)\n"
            "2. A 10-slide pitch deck outline (slide titles + key bullet points per slide)\n"
        )
