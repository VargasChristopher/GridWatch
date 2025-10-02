"""
python -m agents.bescom_outage    → launches the agent via ADK
adk run agents.bescom_outage      → same effect
"""
import asyncio, uuid, logging
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext
from .agent import make_bescom_agent     # factory from agent.py

async def _main() -> None:
    logging.basicConfig(level=logging.INFO)
    agent = make_bescom_agent()

    sess_service = InMemorySessionService()
    session = await sess_service.create_session(
        session_id="bescom-cli",
        app_name="bescom-outage",
        user_id="cli",
    )

    ctx = InvocationContext(
        session_service=sess_service,
        agent=agent,
        session=session,
        invocation_id=str(uuid.uuid4()),
    )

    async for ev in agent.run_async(ctx):
        if ev.content and ev.content.parts:
            print(ev.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(_main())

