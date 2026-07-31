from dataclasses import dataclass

from models import ContextEvent, Discernment


CRISIS_TERMS = {
    "kill myself", "suicide", "self harm", "end my life", "want to die",
    "虐待", "自殺", "死にたい", "消えたい", "自傷",
}

DELIVERY_TIMING = {
    "gaming": "respawn_or_round_end",
    "wearable": "wait_for_recovery_window",
    "ide": "after_build_completion",
    "social": "after_human_review",
    "creator": "creator_control_pause",
}

COOLDOWN_SECONDS = {
    "gaming": 15 * 60,
    "wearable": 15 * 60,
    "ide": 30 * 60,
    "social": 30 * 60,
    "creator": 10 * 60,
}


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    surface: str
    timing: str
    cooldown_seconds: int
    cooldown_remaining_seconds: int = 0
    reason: str | None = None


def contains_crisis_signal(text: str | None) -> bool:
    normalized = (text or "").casefold()
    return any(term in normalized for term in CRISIS_TERMS)


def preflight_delivery(
    event: ContextEvent,
    surface: str,
    cooldown_remaining: int = 0,
) -> PolicyDecision | None:
    """Block locally before private text or biometrics reach either sponsor API."""
    cooldown = COOLDOWN_SECONDS[event.source]
    if not event.user_opted_in:
        return PolicyDecision(
            allowed=False,
            surface=surface,
            timing="not_scheduled",
            cooldown_seconds=cooldown,
            reason="user_not_opted_in",
        )
    if contains_crisis_signal(event.text):
        return PolicyDecision(
            allowed=False,
            surface="human_support_route",
            timing="immediate_human_support",
            cooldown_seconds=0,
            reason="crisis_signal_requires_human_support",
        )
    if cooldown_remaining > 0:
        return PolicyDecision(
            allowed=False,
            surface=surface,
            timing="deferred_until_cooldown_expires",
            cooldown_seconds=cooldown,
            cooldown_remaining_seconds=cooldown_remaining,
            reason="cooldown_active",
        )
    return None


def decide_delivery(
    event: ContextEvent,
    discernment: Discernment,
    surface: str,
) -> PolicyDecision:
    timing = DELIVERY_TIMING[event.source]
    cooldown = COOLDOWN_SECONDS[event.source]

    if not discernment.safe_to_deliver:
        return PolicyDecision(
            allowed=False,
            surface=surface,
            timing="suppressed_by_safety",
            cooldown_seconds=cooldown,
            reason="gloo_safety_suppression",
        )
    if event.source == "social" and event.privacy == "public":
        return PolicyDecision(
            allowed=True,
            surface="private_moderator_prompt",
            timing="after_human_review",
            cooldown_seconds=cooldown,
            reason="public_autopost_prohibited",
        )
    if event.privacy == "public" and not discernment.public_delivery_allowed:
        return PolicyDecision(
            allowed=True,
            surface="private_user_prompt",
            timing=timing,
            cooldown_seconds=cooldown,
            reason="public_delivery_not_authorized",
        )
    return PolicyDecision(
        allowed=True,
        surface=surface,
        timing=timing,
        cooldown_seconds=cooldown,
    )
