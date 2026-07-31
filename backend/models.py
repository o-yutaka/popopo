from typing import Literal
from pydantic import BaseModel, Field


class ContextEvent(BaseModel):
    source: Literal["gaming", "wearable", "ide", "social", "creator"]
    moment_type: str
    metrics: dict[str, float | int | str] = Field(default_factory=dict)
    text: str | None = None
    locale: str = "en"
    privacy: Literal["private", "public"] = "private"


class Discernment(BaseModel):
    need: str
    theme: str
    tone: str
    safe_to_deliver: bool
    public_delivery_allowed: bool = False
    rationale: str = ""


class ScriptureResult(BaseModel):
    reference: str
    text: str
    bible_id: str | None = None
    source: Literal["youversion", "demo"]


class ExperienceResponse(BaseModel):
    context: ContextEvent
    discernment: Discernment
    scripture: ScriptureResult | None
    delivery_surface: str
    suppressed: bool
    mode: Literal["live", "demo"]
