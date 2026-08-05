from agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner"
    system_prompt = (
        "You are a Business Planning Agent. Break startup ideas into structured "
        "work items, an MVP scope, and a realistic build roadmap. Be concrete "
        "and specific, not generic — name actual features, not categories."
    )

    def build_user_prompt(self, topic: str, **context: str) -> str:
        return (
            f"Create a project plan and milestone list for a startup based on this "
            f"theme: {topic}.\n\n"
            "Include:\n"
            "1. Feature set (concrete, not categories)\n"
            "2. MVP scope — what ships first and why\n"
            "3. An 8-week build roadmap with weekly milestones\n"
        )
