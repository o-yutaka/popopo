import app as app_module
from fastapi.testclient import TestClient

client = TestClient(app_module.app)


def test_health_reports_both_required_apis():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["required_apis"] == ["Gloo AI Studio", "YouVersion Platform"]
    assert body["gloo_auth_mode"] in {
        "unconfigured",
        "oauth2_client_credentials",
        "manual_bearer_token",
    }
    assert body["gloo_api_version"] == "v2"
    assert isinstance(body["partial_configuration"], bool)


def test_wearable_demo_returns_scripture_plan_and_attribution():
    response = client.post("/v1/experience", json={
        "source": "wearable",
        "moment_type": "breakthrough_wall",
        "metrics": {"heart_rate": 170, "effort_pct": 0.85, "stress_index": 4.0},
        "privacy": "private",
        "user_opted_in": True
    })
    assert response.status_code == 200
    body = response.json()
    assert body["suppressed"] is False
    assert body["scripture"]["passage_id"] == "ISA.40.31"
    assert body["scripture"]["copyright"]
    assert body["delivery_surface"] == "haptic_wearable_card"
    assert body["delivery_timing"] == "wait_for_recovery_window"
    assert body["cooldown_seconds"] == 900
    assert body["cooldown_enforced"] is False
    assert body["sponsor_calls_executed"] == []
    assert body["pipeline"][-1] == "delivery_policy"


def test_public_social_never_auto_posts():
    response = client.post("/v1/experience", json={
        "source": "social",
        "moment_type": "distress",
        "text": "I feel completely alone",
        "privacy": "public",
        "user_opted_in": True
    })
    body = response.json()
    assert body["suppressed"] is False
    assert body["delivery_surface"] == "private_moderator_prompt"
    assert body["delivery_timing"] == "after_human_review"
    assert body["suppression_reason"] == "public_autopost_prohibited"


def test_crisis_signal_is_suppressed_before_any_sponsor_call(monkeypatch):
    async def forbidden_call(_event):
        raise AssertionError("Gloo must not receive a locally detected crisis event")

    monkeypatch.setattr(app_module.gloo, "discern", forbidden_call)
    response = client.post("/v1/experience", json={
        "source": "social",
        "moment_type": "crisis",
        "text": "I want to die",
        "privacy": "private",
        "user_opted_in": True
    })
    body = response.json()
    assert body["suppressed"] is True
    assert body["scripture"] is None
    assert body["delivery_surface"] == "human_support_route"
    assert body["delivery_timing"] == "immediate_human_support"
    assert body["sponsor_calls_executed"] == []
    assert body["pipeline"] == [
        "context_normalized",
        "local_preflight_policy",
        "delivery_suppressed",
    ]


def test_no_consent_is_suppressed_before_any_sponsor_call(monkeypatch):
    async def forbidden_call(_event):
        raise AssertionError("Gloo must not receive a non-consented event")

    monkeypatch.setattr(app_module.gloo, "discern", forbidden_call)
    response = client.post("/v1/experience", json={
        "source": "gaming",
        "moment_type": "repeated_failure",
        "user_opted_in": False
    })
    body = response.json()
    assert body["suppressed"] is True
    assert body["suppression_reason"] == "user_not_opted_in"
    assert body["sponsor_calls_executed"] == []


def test_pseudonymous_delivery_key_enforces_cooldown():
    event = {
        "source": "wearable",
        "moment_type": "effort_peak",
        "metrics": {"heart_rate": 170},
        "user_opted_in": True,
        "delivery_key": "test-runner-cooldown-001",
    }
    first = client.post("/v1/experience", json=event)
    second = client.post("/v1/experience", json=event)
    assert first.status_code == 200
    assert first.json()["suppressed"] is False
    assert first.json()["cooldown_enforced"] is True
    assert second.status_code == 200
    assert second.json()["suppressed"] is True
    assert second.json()["suppression_reason"] == "cooldown_active"
    assert 1 <= second.json()["cooldown_remaining_seconds"] <= 900
    assert second.json()["sponsor_calls_executed"] == []


def test_unknown_consent_alias_is_rejected():
    response = client.post("/v1/experience", json={
        "source": "wearable",
        "moment_type": "effort_peak",
        "opted_in": True
    })
    assert response.status_code == 422
