from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_health_reports_both_required_apis():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["required_apis"] == ["Gloo AI Studio", "YouVersion Platform"]


def test_wearable_demo_returns_scripture_and_provenance():
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
    assert body["delivery_surface"] == "haptic_wearable_card"
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
    assert body["suppression_reason"] == "public_autopost_prohibited"


def test_crisis_signal_suppresses_automated_scripture():
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


def test_no_consent_means_no_delivery():
    response = client.post("/v1/experience", json={
        "source": "gaming",
        "moment_type": "repeated_failure",
        "user_opted_in": False
    })
    body = response.json()
    assert body["suppressed"] is True
    assert body["suppression_reason"] == "user_not_opted_in"
