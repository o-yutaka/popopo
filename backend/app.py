from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from clients import GlooClient, YouVersionClient
from models import ContextEvent, ExperienceResponse
from policy import decide_delivery

load_dotenv()
app = FastAPI(
    title="Scripture Everywhere AI",
    version="1.1.0",
    description="Consent-first context → Gloo discernment → YouVersion passage → native delivery.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

gloo = GlooClient()
youversion = YouVersionClient()

SURFACES = {
    "gaming": "respawn_screen",
    "wearable": "haptic_wearable_card",
    "ide": "editor_margin",
    "social": "private_moderator_prompt",
    "creator": "creator_only_overlay",
}


@app.get("/")
def root() -> dict:
    return {
        "name": "Scripture Everywhere AI",
        "docs": "/docs",
        "health": "/health",
        "experience": "POST /v1/experience",
    }


@app.get("/health")
def health() -> dict:
    live = gloo.configured and youversion.configured
    return {
        "ok": True,
        "gloo_configured": gloo.configured,
        "gloo_auth_mode": gloo.auth_mode,
        "gloo_api_version": "v2",
        "youversion_configured": youversion.configured,
        "mode": "live" if live else "demo",
        "required_apis": ["Gloo AI Studio", "YouVersion Platform"],
        "version": app.version,
    }


@app.post("/v1/experience", response_model=ExperienceResponse)
async def create_experience(event: ContextEvent) -> ExperienceResponse:
    discernment = await gloo.discern(event)
    policy = decide_delivery(event, discernment, SURFACES[event.source])
    scripture = (
        await youversion.find_scripture(discernment.theme, event.locale)
        if policy.allowed
        else None
    )
    mode = "live" if gloo.configured and youversion.configured else "demo"

    return ExperienceResponse(
        context=event,
        discernment=discernment,
        scripture=scripture,
        delivery_surface=policy.surface,
        suppressed=not policy.allowed,
        suppression_reason=policy.reason,
        mode=mode,
    )
