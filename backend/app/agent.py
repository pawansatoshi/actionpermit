import os
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def explain_decision(decision: str, reasons: list[str]) -> str:
    """Explain a deterministic authorization result. This tool never changes the decision."""
    return f"Decision={decision}. Reasons={', '.join(reasons)}. The deterministic policy engine is authoritative."


root_agent = Agent(
    name="actionpermit_agent",
    model=Gemini(model=MODEL),
    instruction=(
        "You are the ActionPermit reasoning agent. Explain the supplied deterministic authorization result. "
        "Never grant permission, invent authorization, override policy, or execute a side effect. "
        "The server-side deterministic policy engine is the sole authorization authority."
    ),
    tools=[explain_decision],
)

app = App(root_agent=root_agent, name="actionpermit")


def reason_about(request: dict, decision: str, reasons: list[str]) -> str | None:
    """Run Google ADK for explanation only; its output cannot alter authorization."""
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return None
    try:
        runner = InMemoryRunner(app=app)
        prompt = f"Explain this authorization result in one concise paragraph. Never change it. Request: {request}. Deterministic decision: {decision}. Reasons: {reasons}."
        events = runner.run(types.Content(role="user", parts=[types.Part.from_text(text=prompt)]))
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    return text[:1000]
    except Exception:
        return None
    return None
