import os
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def explain_decision(decision: str, reasons: list[str]) -> str:
    """Explain a deterministic authorization result. This tool never changes the decision."""
    return f"Decision={decision}. Reasons={', '.join(reasons)}. The deterministic policy engine is authoritative."


root_agent = Agent(
    name="actionpermit_agent",
    model=Gemini(model=MODEL),
    instruction=(
        "You are the ActionPermit reasoning agent. Interpret action requests and explain policy outcomes. "
        "Never grant permission, invent authorization, or execute a side effect. The server-side deterministic "
        "policy engine is the sole authorization authority."
    ),
    tools=[explain_decision],
)

app = App(root_agent=root_agent, name="actionpermit")
