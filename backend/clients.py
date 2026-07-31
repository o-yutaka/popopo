import json
import os
from typing import Any

import httpx

from models import ContextEvent, Discernment, ScriptureResult


# Gloo selects a bounded pastoral theme. We then resolve that theme to a
# canonical USFM passage ID before requesting licensed text from YouVersion.
THEME_PASSAGES: dict[str, tuple[str, str, str]] = {
    "perseverance": ("JAS.1.12", "James 1:12", "Blessed is the one who perseveres under trial."),
    "wisdom": ("JAS.1.5", "James 1:5", "If any of you lacks wisdom, you should ask God, who gives generously."),
    "comfort": ("PSA.34.18", "Psalm 34:18", "The Lord is close to the brokenhearted."),
    "restraint": ("PRO.15.1", "Proverbs 15:1", "A gentle answer turns away wrath."),
    "strength": ("ISA.40.31", "Isaiah 40:31", "Those who hope in the Lord will renew their strength."),
    "peace": ("PHP.4.6-7", "Philippians 4:6–7", "Present your requests to God, and the peace of God will guard your hearts and minds."),
}
DEFAULT_THEME = "strength"


class GlooClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("GLOO_API_KEY", "")
        self.base_url = os.getenv("GLOO_BASE_URL", "").rstrip("/")
        self.model = os.getenv("GLOO_MODEL", "")
        self.path = os.getenv("GLOO_CHAT_PATH", "/v1/chat/completions")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    async def discern(self, event: ContextEvent) -> Discernment:
        if not self.configured:
            return self._demo_discernment(event)

        prompt = {
            "task": "Return strict JSON only.",
            "allowed_themes": sorted(THEME_PASSAGES),
            "required_fields": [
                "need", "theme", "tone", "safe_to_deliver",
                "public_delivery_allowed", "rationale"
            ],
            "rules": [
                "Never diagnose medical or mental-health conditions.",
                "Never claim divine certainty or that God caused an event.",
                "Use exactly one allowed theme.",
                "For distress, self-harm, abuse, or crisis signals: suppress automated Scripture and require human support.",
                "For sensitive social content: private, human-reviewed delivery only.",
            ],
            "event": event.model_dump(),
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": json.dumps(prompt)}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}{self.path}", headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        result = Discernment.model_validate_json(content)
        if result.theme not in THEME_PASSAGES:
            result.theme = DEFAULT_THEME
            result.rationale = f"{result.rationale} Theme constrained to safe allowlist.".strip()
        return result

    @staticmethod
    def _demo_discernment(event: ContextEvent) -> Discernment:
        mapping = {
            "gaming": ("encouragement", "perseverance", "teammate"),
            "wearable": ("endurance", "strength", "concise"),
            "ide": ("clarity", "wisdom", "calm"),
            "social": ("support", "comfort", "gentle"),
            "creator": ("grounding", "restraint", "steady"),
        }
        need, theme, tone = mapping[event.source]
        sensitive = event.source == "social"
        return Discernment(
            need=need,
            theme=theme,
            tone=tone,
            safe_to_deliver=True,
            public_delivery_allowed=not sensitive and event.privacy == "public",
            rationale="Deterministic credential-free demonstration.",
        )


class YouVersionClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("YVP_APP_KEY", os.getenv("YOUVERSION_API_KEY", ""))
        self.base_url = os.getenv("YOUVERSION_BASE_URL", "https://api.youversion.com/v1").rstrip("/")
        self.bible_id = os.getenv("YOUVERSION_BIBLE_ID", "3034")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.bible_id)

    async def find_scripture(self, theme: str, locale: str) -> ScriptureResult:
        passage_id, fallback_reference, fallback_text = THEME_PASSAGES.get(
            theme.lower(), THEME_PASSAGES[DEFAULT_THEME]
        )
        if not self.configured:
            return ScriptureResult(
                reference=fallback_reference,
                text=fallback_text,
                passage_id=passage_id,
                bible_id=self.bible_id,
                source="demo",
            )

        headers = {"X-YVP-App-Key": self.api_key, "Accept-Language": locale}
        url = f"{self.base_url}/bibles/{self.bible_id}/passages/{passage_id}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data: dict[str, Any] = response.json()

        passage = data.get("data", data)
        return ScriptureResult(
            reference=passage.get("reference", fallback_reference),
            text=passage.get("content", fallback_text),
            passage_id=passage.get("id", passage_id),
            bible_id=self.bible_id,
            source="youversion",
        )
