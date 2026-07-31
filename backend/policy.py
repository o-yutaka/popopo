from dataclasses import dataclass

from models import ContextEvent, Discernment


CRISIS_TERMS = {
    "kill myself", "suicide", "self harm", "end my life", "want to die",
    "虐待", "自殺", "死にたい", "消えたい", "自傷",
}


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    surface: str
    reason: str | None = None


def contains_crisis_signal(text: str | None) -> bool:
    normalized = (text or "").casefold()
    return any(term in normalized for term in CRISIS_TERMS)


def decide_delivery(event: ContextEvent, discernment: Discernment, surface: str) -> PolicyDecision:
    if not event.user_opted_in:
        return PolicyDecision(False, surface, "user_not_opted_in")
    if contains_crisis_signal(event.text):
        return PolicyDecision(False, "human_support_route", "crisis_signal_requires_human_support")
    if not discernment.safe_to_deliver:
        return PolicyDecision(False, surface, "gloo_safety_suppression")
    if event.source == "social" and event.privacy == "public":
        return PolicyDecision(True, "private_moderator_prompt", "public_autopost_prohibited")
    return PolicyDecision(True, surface)
