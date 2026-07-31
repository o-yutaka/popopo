from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
import nbformat
from nbclient import NotebookClient

API_URL = os.getenv("DEMO_API_URL", "http://127.0.0.1:8001")
NOTEBOOK = Path(
    os.getenv(
        "SUBMISSION_NOTEBOOK",
        "notebooks/scripture_everywhere_submission.ipynb",
    )
)
OUT = Path(os.getenv("JUDGE_AUDIT_OUT", "build/judge-emulator"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def post(client: httpx.Client, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    response = client.post("/v1/experience", json=payload)
    try:
        body = response.json()
    except Exception as exc:
        raise AssertionError(f"Non-JSON API response {response.status_code}: {response.text}") from exc
    return response.status_code, body


def emulate_api() -> dict[str, Any]:
    scenarios: dict[str, Any] = {}
    with httpx.Client(base_url=API_URL, timeout=15) as client:
        health = client.get("/health")
        require(health.status_code == 200, f"Health failed: {health.status_code}")
        health_body = health.json()
        require(health_body.get("ok") is True, "Health did not report ok=true")
        require(health_body.get("partial_configuration") is False, "Demo API is partially configured")
        scenarios["health"] = health_body

        status, wearable = post(
            client,
            {
                "source": "wearable",
                "moment_type": "breakthrough_wall",
                "metrics": {"heart_rate": 170, "effort_pct": 0.85, "stress_index": 4.0},
                "privacy": "private",
                "user_opted_in": True,
            },
        )
        require(status == 200, f"Wearable failed: {status}")
        require(wearable.get("suppressed") is False, "Wearable was unexpectedly suppressed")
        require(wearable.get("scripture", {}).get("passage_id") == "ISA.40.31", "Wrong wearable passage")
        require(wearable.get("delivery_timing") == "wait_for_recovery_window", "Wrong wearable timing")
        require(wearable.get("sponsor_calls_executed") == [], "Demo mode falsely reported sponsor calls")
        scenarios["wearable"] = wearable

        status, no_consent = post(
            client,
            {
                "source": "gaming",
                "moment_type": "repeated_failure",
                "user_opted_in": False,
            },
        )
        require(status == 200, f"No-consent failed: {status}")
        require(no_consent.get("suppressed") is True, "No-consent event was delivered")
        require(no_consent.get("suppression_reason") == "user_not_opted_in", "Wrong consent suppression")
        require(no_consent.get("sponsor_calls_executed") == [], "No-consent event reached sponsor route")
        scenarios["no_consent"] = no_consent

        status, crisis = post(
            client,
            {
                "source": "social",
                "moment_type": "crisis",
                "text": "I want to die",
                "privacy": "private",
                "user_opted_in": True,
            },
        )
        require(status == 200, f"Crisis failed: {status}")
        require(crisis.get("suppressed") is True, "Crisis event was not suppressed")
        require(crisis.get("scripture") is None, "Crisis route returned automated Scripture")
        require(crisis.get("delivery_surface") == "human_support_route", "Crisis did not route to human support")
        require(crisis.get("sponsor_calls_executed") == [], "Crisis event reached sponsor route")
        scenarios["crisis"] = crisis

        status, social = post(
            client,
            {
                "source": "social",
                "moment_type": "distress",
                "text": "I feel completely alone",
                "privacy": "public",
                "user_opted_in": True,
            },
        )
        require(status == 200, f"Public social failed: {status}")
        require(social.get("delivery_surface") == "private_moderator_prompt", "Public social was not made private")
        require(social.get("delivery_timing") == "after_human_review", "Public social skipped review")
        require(social.get("suppression_reason") == "public_autopost_prohibited", "Auto-post prohibition missing")
        scenarios["public_social"] = social

        cooldown_payload = {
            "source": "wearable",
            "moment_type": "effort_peak",
            "metrics": {"heart_rate": 170},
            "user_opted_in": True,
            "delivery_key": "judge-emulator-runner-001",
        }
        first_status, first = post(client, cooldown_payload)
        second_status, second = post(client, cooldown_payload)
        require(first_status == second_status == 200, "Cooldown HTTP failure")
        require(first.get("suppressed") is False, "First cooldown event was suppressed")
        require(first.get("cooldown_enforced") is True, "Cooldown was not armed")
        require(second.get("suppressed") is True, "Repeated event bypassed cooldown")
        require(second.get("suppression_reason") == "cooldown_active", "Wrong cooldown reason")
        scenarios["cooldown_first"] = first
        scenarios["cooldown_second"] = second

        invalid = client.post(
            "/v1/experience",
            json={"source": "wearable", "moment_type": "effort_peak", "opted_in": True},
        )
        require(invalid.status_code == 422, f"Unknown consent alias was accepted: {invalid.status_code}")
        scenarios["strict_contract"] = {"status_code": invalid.status_code}

    return scenarios


def execute_notebook() -> dict[str, Any]:
    require(NOTEBOOK.exists(), f"Notebook missing: {NOTEBOOK}")
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    require(code_cells, "Notebook has no code cells")

    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        allow_errors=False,
        resources={"metadata": {"path": str(NOTEBOOK.parent)}},
    )
    executed = client.execute()
    output_path = OUT / "executed-scripture-everywhere-submission.ipynb"
    nbformat.write(executed, output_path)

    executed_code = 0
    error_outputs: list[str] = []
    for cell in executed.cells:
        if cell.cell_type != "code":
            continue
        if cell.get("execution_count") is not None:
            executed_code += 1
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                error_outputs.append(output.get("ename", "unknown"))
    require(executed_code == len(code_cells), f"Only {executed_code}/{len(code_cells)} code cells executed")
    require(not error_outputs, f"Notebook errors: {error_outputs}")
    return {
        "path": str(NOTEBOOK),
        "executed_path": str(output_path),
        "code_cells": len(code_cells),
        "executed_code_cells": executed_code,
        "errors": error_outputs,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "api": emulate_api(),
        "notebook": execute_notebook(),
    }
    path = OUT / "runtime-audit.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "api_scenarios": len(report["api"]),
                "notebook_code_cells": report["notebook"]["code_cells"],
                "errors": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
