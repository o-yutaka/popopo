from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = os.getenv("EVIDENCE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
OUT = Path(os.getenv("EVIDENCE_OUTPUT", "evidence/live-api-evidence.json"))


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    event = {
        "source": "wearable",
        "moment_type": "effort_peak",
        "metrics": {"heart_rate": 170, "effort": 0.85, "minutes": 18},
        "locale": "en",
        "privacy": "private",
        "user_opted_in": True,
        "delivery_key": "hackathon-demo-runner-001",
    }
    with httpx.Client(timeout=60) as client:
        health = client.get(f"{BASE_URL}/health")
        health.raise_for_status()
        response = client.post(f"{BASE_URL}/v1/experience", json=event)
        response.raise_for_status()

    health_data = health.json()
    data = response.json()
    if health_data.get("mode") != "live" or data.get("mode") != "live":
        raise RuntimeError("Evidence capture requires both APIs to be configured in live mode")
    if health_data.get("partial_configuration") is not False:
        raise RuntimeError("Evidence capture rejects partial sponsor configuration")
    if health_data.get("gloo_auth_mode") != "oauth2_client_credentials":
        raise RuntimeError("Public evidence requires the official Gloo OAuth2 client-credentials flow")
    if health_data.get("gloo_api_version") != "v2":
        raise RuntimeError("Public evidence requires Gloo Completions API v2")
    if data.get("sponsor_calls_executed") != ["gloo", "youversion"]:
        raise RuntimeError("The response did not prove both sponsor calls in order")
    if data.get("cooldown_enforced") is not True:
        raise RuntimeError("The wearable evidence event must prove cooldown enforcement")

    scripture = data.get("scripture") or {}
    if scripture.get("source") != "youversion":
        raise RuntimeError("YouVersion live source was not observed")
    if not scripture.get("copyright"):
        raise RuntimeError("YouVersion Bible attribution was not captured")

    passage_text = scripture.pop("text", "")
    if not passage_text:
        raise RuntimeError("YouVersion returned no passage text")

    request_evidence = dict(event)
    delivery_key = request_evidence.pop("delivery_key")
    request_evidence["delivery_key_sha256"] = _sha256(delivery_key)
    response_context = data.get("context") or {}
    if isinstance(response_context, dict):
        response_context.pop("delivery_key", None)
        response_context["delivery_key_sha256"] = _sha256(delivery_key)

    evidence = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "claim": "A consented wearable event completed the live Gloo OAuth2/v2 -> YouVersion passage -> delivery-policy pipeline.",
        "health": health_data,
        "request": request_evidence,
        "response": data,
        "scripture_text_sha256": _sha256(passage_text),
        "scripture_text_length": len(passage_text),
        "redaction": "Client Secret, App Key, bearer token, raw delivery key, raw headers, and full licensed passage text are not stored.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote verified live evidence to {OUT}")


if __name__ == "__main__":
    main()
