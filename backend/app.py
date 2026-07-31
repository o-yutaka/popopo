import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from clients import GlooClient, YouVersionClient
from models import ContextEvent, ExperienceResponse

load_dotenv()
app = FastAPI(title="Scripture Everywhere AI", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

gloo = GlooClient()
youversion = YouVersionClient()

SURFACES = {
    "gaming": "respawn_screen",
    "wearable": "haptic_wearable_card",
    "ide": "editor_margin",
    "social": "private_moderator_prompt",
    "creator": "creator_only_overlay",
}


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "gloo_configured": gloo.configured,
        "youversion_configured": youversion.configured,
        "mode": "live" if gloo.configured and youversion.configured else "demo",
    }


@app.post("/v1/experience", response_model=ExperienceResponse)
async def create_experience(event: ContextEvent) -> ExperienceResponse:
    discernment = await gloo.discern(event)
    suppressed = not discernment.safe_to_deliver
    scripture = None if suppressed else await youversion.find_scripture(discernment.theme, event.locale)

    if event.source == "social" and event.privacy == "public":
        # Never auto-post sensitive social interventions. Route to private human review.
        discernment.public_delivery_allowed = False

    mode = "live" if gloo.configured and youversion.configured else "demo"
    return ExperienceResponse(
        context=event,
        discernment=discernment,
        scripture=scripture,
        delivery_surface=SURFACES[event.source],
        suppressed=suppressed,
        mode=mode,
    )
