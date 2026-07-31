import json
import os
import time
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


def _extract_json_object(content: str) -> str:
    """Extract one JSON object from a model response without accepting prose as data."""
    value = content.strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        value = "\n".join(lines).strip()
    start = value.find("{")
    end = value.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Gloo response did not contain a JSON object")
    return value[start : end + 1]


class GlooClient:
    """Official Gloo AI Studio client using OAuth2 client credentials.

    Gloo credentials are exchanged for a short-lived bearer token. An optional
    GLOO_ACCESS_TOKEN is accepted for local/manual testing, but production and
    evidence workflows use GLOO_CLIENT_ID + GLOO_CLIENT_SECRET.
    """

    def __init__(self) -> None:
        self.client_id = os.getenv("GLOO_CLIENT_ID", "")
        self.client_secret = os.getenv("GLOO_CLIENT_SECRET", "")
        self.manual_access_token = os.getenv("GLOO_ACCESS_TOKEN", "")
        self.token_url = os.getenv(
            "GLOO_TOKEN_URL", "https://platform.ai.gloo.com/oauth2/token"
        )
        self.base_url = os.getenv(
            "GLOO_BASE_URL", "https://platform.ai.gloo.com/ai/v2"
        ).rstrip("/")
        self.model = os.getenv("GLOO_MODEL", "gloo-openai-gpt-5-mini")
        self.path = os.getenv("GLOO_CHAT_PATH", "/chat/completions")
        self._cached_access_token = ""
        self._token_expires_at = 0.0

    @property
    def configured(self) -> bool:
        has_auth = bool(
            self.manual_access_token
            or (self.client_id and self.client_secret)
        )
        return bool(has_auth and self.base_url and self.model)

    @property
    def auth_mode(self) -> str:
        if self.manual_access_token:
            return "manual_bearer_token"
        if self.client_id and self.client_secret:
            return "oauth2_client_credentials"
        return "unconfigured"

    async def _get_access_token(self) -> str:
        if self.manual_access_token:
            return self.manual_access_token
        now = time.time()
        if self._cached_access_token and now < self._token_expires_at:
            return self._cached_access_token
        if not (self.client_id and self.client_secret):
            raise RuntimeError("Gloo OAuth2 credentials are not configured")

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                self.token_url,
                auth=httpx.BasicAuth(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()

        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise RuntimeError("Gloo token response did not include access_token")
        expires_in = int(payload.get("expires_in", 3600))
        self._cached_access_token = token
        self._token_expires_at = now + max(30, expires_in - 60)
        return token

    async def discern(self, event: ContextEvent) -> Discernment:
        if not self.configured:
            return self._demo_discernment(event)

        prompt = {
            "task": "Return one strict JSON object and no other text.",
            "allowed_themes": sorted(THEME_PASSAGES),
            "required_fields": [
                "need",
                "theme",
                "tone",
                "safe_to_deliver",
                "public_delivery_allowed",
                "rationale",
            ],
            "rules": [
                "Never diagnose medical or mental-health conditions.",
                "Never claim divine certainty or that God caused an event.",
                "Use exactly one allowed theme.",
                "For distress, self-harm, abuse, or crisis signals: set safe_to_deliver false and require human support.",
                "For sensitive social content: private, human-reviewed delivery only.",
            ],
            "event": event.model_dump(),
        }
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a values-aligned discernment engine. Output valid JSON only.",
                },
                {"role": "user", "content": json.dumps(prompt)},
            ],
            "temperature": 0.1,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}{self.path}", headers=headers, json=payload
            )
            response.raise_for_status()
            response_data = response.json()

        content = response_data["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("Gloo completion content was not a string")
        result = Discernment.model_validate_json(_extract_json_object(content))
        if result.theme not in THEME_PASSAGES:
            result.theme = DEFAULT_THEME
            result.rationale = (
                f"{result.rationale} Theme constrained to safe allowlist."
            ).strip()
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
        self.base_url = os.getenv(
            "YOUVERSION_BASE_URL", "https://api.youversion.com/v1"
        ).rstrip("/")
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

        headers = {
            "X-YVP-App-Key": self.api_key,
            "Accept-Language": locale,
            "Accept": "application/json",
        }
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
