from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = os.getenv("EVIDENCE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
OUT = Path(os.getenv("EVIDENCE_OUTPUT", "evidence/live-api-evidence.json"))


def main() -> None:
    event = {
        "source": "wearable",
        "moment_type": "effort_peak",
        "metrics": {"heart_rate": 170, "effort": 0.85, "minutes": 18},
        "locale": "en",
        "privacy": "private",
        "user_opted_in": True,
    }
    with httpx.Client(timeout=45) as client:
        health = client.get(f"{BASE_URL}/health")
        health.raise_for_status()
        response = client.post(f"{BASE_URL}/v1/experience", json=event)
        response.raise_for_status()

    health_data = health.json()
    data = response.json()
    if health_data.get("mode") != "live" or data.get("mode") != "live":
        raise RuntimeError("Evidence capture requires both APIs to be configured in live mode")
    scripture = data.get("scripture") or {}
    if scripture.get("source") != "youversion":
        raise RuntimeError("YouVersion live source was not observed")

    text = scripture.pop("text", "")
    evidence = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "claim": "A wearable context event completed the live Gloo -> YouVersion pipeline.",
        "health": health_data,
        "request": event,
        "response": data,
        "scripture_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "scripture_text_length": len(text),
        "redaction": "API keys, raw headers, and full licensed passage text are not stored.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote verified live evidence to {OUT}")


if __name__ == "__main__":
    main()
