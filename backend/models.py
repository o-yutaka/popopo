from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


Source = Literal["gaming", "wearable", "ide", "social", "creator"]
Privacy = Literal["private", "public"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ContextEvent(StrictModel):
    source: Source
    moment_type: str = Field(min_length=1, max_length=80)
    metrics: dict[str, float | int | str] = Field(default_factory=dict)
    text: str | None = Field(default=None, max_length=2000)
    locale: str = Field(default="en", min_length=2, max_length=20)
    privacy: Privacy = "private"
    user_opted_in: bool = True
    # Optional pseudonymous token used only for in-memory cooldown enforcement.
    # Do not send a name, email address, device serial, or other direct identifier.
    delivery_key: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("metrics")
    @classmethod
    def limit_metrics(cls, value: dict[str, float | int | str]) -> dict[str, float | int | str]:
        if len(value) > 30:
            raise ValueError("metrics supports at most 30 entries")
        return value


class Discernment(StrictModel):
    need: str
    theme: str
    tone: str
    safe_to_deliver: bool
    public_delivery_allowed: bool = False
    rationale: str = ""


class ScriptureResult(StrictModel):
    reference: str
    text: str
    passage_id: str | None = None
    bible_id: str | None = None
    bible_abbreviation: str | None = None
    bible_title: str | None = None
    copyright: str | None = None
    attribution_url: str | None = None
    source: Literal["youversion", "demo"]


class ExperienceResponse(StrictModel):
    context: ContextEvent
    discernment: Discernment
    scripture: ScriptureResult | None
    delivery_surface: str
    delivery_timing: str
    cooldown_seconds: int = Field(ge=0)
    cooldown_remaining_seconds: int = Field(default=0, ge=0)
    cooldown_enforced: bool
    suppressed: bool
    suppression_reason: str | None = None
    mode: Literal["live", "demo"]
    pipeline: list[str] = Field(default_factory=lambda: [
        "context_normalized",
        "local_preflight_policy",
        "gloo_oauth2_v2_discernment",
        "theme_allowlist",
        "youversion_passage",
        "delivery_policy",
    ])
