from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from clients import GlooClient, YouVersionClient
from cooldown import CooldownStore
from models import ContextEvent, Discernment, ExperienceResponse
from policy import COOLDOWN_SECONDS, decide_delivery, preflight_delivery

load_dotenv()
app = FastAPI(
    title="Scripture Everywhere AI",
    version="1.2.0",
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
cooldowns = CooldownStore()

SURFACES = {
    "gaming": "respawn_screen",
    "wearable": "haptic_wearable_card",
    "ide": "editor_margin",
    "social": "private_moderator_prompt",
    "creator": "creator_only_overlay",
}


def _local_suppression_discernment(reason: str | None) -> Discernment:
    crisis = reason == "crisis_signal_requires_human_support"
    return Discernment(
        need="human_support" if crisis else "none",
        theme="comfort" if crisis else "suppressed",
        tone="human_review" if crisis else "none",
        safe_to_deliver=False,
        public_delivery_allowed=False,
        rationale=f"Local preflight policy: {reason}. No sponsor API call was made.",
    )


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
    partial = gloo.configured != youversion.configured
    return {
        "ok": True,
        "gloo_configured": gloo.configured,
        "gloo_auth_mode": gloo.auth_mode,
        "gloo_api_version": "v2",
        "youversion_configured": youversion.configured,
        "partial_configuration": partial,
        "mode": "live" if live else "demo",
        "required_apis": ["Gloo AI Studio", "YouVersion Platform"],
        "version": app.version,
    }


@app.post("/v1/experience", response_model=ExperienceResponse)
async def create_experience(event: ContextEvent) -> ExperienceResponse:
    surface = SURFACES[event.source]
    cooldown_window = COOLDOWN_SECONDS[event.source]
    remaining = cooldowns.remaining_seconds(
        event.delivery_key, event.source, cooldown_window
    )
    preflight = preflight_delivery(event, surface, remaining)
    live = gloo.configured and youversion.configured
    mode = "live" if live else "demo"

    if preflight is not None:
        return ExperienceResponse(
            context=event,
            discernment=_local_suppression_discernment(preflight.reason),
            scripture=None,
            delivery_surface=preflight.surface,
            delivery_timing=preflight.timing,
            cooldown_seconds=preflight.cooldown_seconds,
            cooldown_remaining_seconds=preflight.cooldown_remaining_seconds,
            cooldown_enforced=bool(event.delivery_key),
            suppressed=True,
            suppression_reason=preflight.reason,
            mode=mode,
            sponsor_calls_executed=[],
            pipeline=[
                "context_normalized",
                "local_preflight_policy",
                "delivery_suppressed",
            ],
        )

    sponsor_calls: list[str] = []
    if live:
        discernment = await gloo.discern(event)
        sponsor_calls.append("gloo")
    else:
        # Never create a mixed pipeline where one sponsor is live and the other
        # silently falls back. Both credentials are required for external calls.
        discernment = gloo.demo_discernment(event)

    policy = decide_delivery(event, discernment, surface)
    scripture = None
    if policy.allowed:
        if live:
            scripture = await youversion.find_scripture(discernment.theme, event.locale)
            sponsor_calls.append("youversion")
        else:
            scripture = youversion.demo_scripture(discernment.theme)

    cooldown_enforced = False
    if policy.allowed and scripture is not None:
        cooldown_enforced = cooldowns.record(event.delivery_key, event.source)

    return ExperienceResponse(
        context=event,
        discernment=discernment,
        scripture=scripture,
        delivery_surface=policy.surface,
        delivery_timing=policy.timing,
        cooldown_seconds=policy.cooldown_seconds,
        cooldown_remaining_seconds=policy.cooldown_remaining_seconds,
        cooldown_enforced=cooldown_enforced,
        suppressed=not policy.allowed,
        suppression_reason=policy.reason,
        mode=mode,
        sponsor_calls_executed=sponsor_calls,
    )
