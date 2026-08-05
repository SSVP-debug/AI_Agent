from agents.base import BaseAgent


class FinancialModelerAgent(BaseAgent):
    """
    New in the rebuild — the original repo pitched "financial model" as one
    of its seven outputs but had no agent producing one.
    """

    name = "financial_modeler"
    system_prompt = (
        "You are a Financial Modeling Agent for early-stage startups. Produce "
        "grounded, order-of-magnitude estimates with your assumptions stated "
        "explicitly — this is directional modeling for a pitch, not audited "
        "accounting. Always state the assumptions behind any number."
    )

    def build_user_prompt(self, topic: str, **context: str) -> str:
        return (
            f"For this startup theme: {topic}\n\n"
            "Produce a lightweight financial model covering:\n"
            "1. Cost structure (fixed vs variable, key line items)\n"
            "2. Revenue projections for year 1-3 (state your assumptions)\n"
            "3. Unit economics (rough CAC/LTV reasoning if applicable)\n"
            "4. Funding ask and use of funds, if relevant to this stage\n"
        )
