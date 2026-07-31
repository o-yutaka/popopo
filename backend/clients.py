import json
import os
from typing import Any

import httpx

from models import ContextEvent, Discernment, ScriptureResult


DEMO_VERSES = {
    "perseverance": ("James 1:12", "Blessed is the one who perseveres under trial."),
    "wisdom": ("James 1:5", "If any of you lacks wisdom, you should ask God, who gives generously."),
    "comfort": ("Psalm 34:18", "The Lord is close to the brokenhearted."),
    "restraint": ("Proverbs 15:1", "A gentle answer turns away wrath."),
    "strength": ("Isaiah 40:31", "Those who hope in the Lord will renew their strength."),
}


class GlooClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("GLOO_API_KEY", "")
        self.base_url = os.getenv("GLOO_BASE_URL", "https://api.gloo.ai").rstrip("/")
        self.model = os.getenv("GLOO_MODEL", "")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.model)

    async def discern(self, event: ContextEvent) -> Discernment:
        if not self.configured:
            return self._demo_discernment(event)

        prompt = {
            "task": "Return strict JSON with need, theme, tone, safe_to_deliver, public_delivery_allowed, rationale.",
            "rules": [
                "Do not diagnose.",
                "Do not claim divine certainty.",
                "For sensitive social content, default to private and human-reviewed delivery.",
                "Use a short canonical theme suitable for Scripture retrieval.",
            ],
            "event": event.model_dump(),
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": json.dumps(prompt)}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        return Discernment.model_validate_json(content)

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
        self.api_key = os.getenv("YOUVERSION_API_KEY", "")
        self.base_url = os.getenv("YOUVERSION_BASE_URL", "https://api.youversion.com").rstrip("/")
        self.bible_id = os.getenv("YOUVERSION_BIBLE_ID", "")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.bible_id)

    async def find_scripture(self, theme: str, locale: str) -> ScriptureResult:
        if not self.configured:
            reference, text = DEMO_VERSES.get(theme.lower(), DEMO_VERSES["strength"])
            return ScriptureResult(reference=reference, text=text, source="demo")

        headers = {"X-YVP-App-Key": self.api_key, "Accept-Language": locale}
        params: dict[str, Any] = {"query": theme, "bible_id": self.bible_id, "limit": 1}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}/v1/scripture/search", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        item = data["data"][0]
        return ScriptureResult(
            reference=item["reference"],
            text=item["text"],
            bible_id=self.bible_id,
            source="youversion",
        )
