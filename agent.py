from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation
from simple_tts import SimpleTTS
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from lm_studio_llm import LMStudioLLM
from tools import (
    assess_client_needs,
    schedule_follow_up,
    schedule_appointment,
    get_clinic_info,
    check_available_slots,
    get_payment_info,
    search_web,
    get_clinic_stats
)
from config import settings
from logging_config import agent_logger

# Database will be initialized when first used by tools


class EloDentalAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=LMStudioLLM(
                api_key=settings.lm_studio_api_key,
                base_url=settings.lm_studio_base_url,
                model="local-model",  # Using local LM Studio model
                temperature=0.7,
            ),
            tts=SimpleTTS(),
            # Using default STT for now
            # stt will be auto-configured by LiveKit
            tools=[
                assess_client_needs,
                schedule_follow_up,
                schedule_appointment,
                get_clinic_info,
                check_available_slots,
                get_payment_info,
                search_web,
                get_clinic_stats
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the Elo Dental Agent"""
    agent_logger.log_database_operation("startup", "agent")
    
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=EloDentalAgent(),
        room_input_options=RoomInputOptions(
            video_enabled=False,
            noise_cancellation=noise_cancellation.BVCTelephony(),
        ),
    )

    await ctx.connect()
    agent_logger.log_database_operation("connected", "livekit")

    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )


if __name__ == "__main__":
    agent_logger.log_database_operation("startup", "cli")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
