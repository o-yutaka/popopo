import asyncio

import clients
from clients import GlooClient, _extract_json_object


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeAsyncClient:
    calls = []

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, **kwargs):
        self.__class__.calls.append((url, kwargs))
        return FakeResponse({
            "access_token": "header.payload.signature",
            "expires_in": 3600,
            "token_type": "Bearer",
        })


def test_gloo_uses_official_oauth_contract(monkeypatch):
    monkeypatch.setenv("GLOO_CLIENT_ID", "client-id")
    monkeypatch.setenv("GLOO_CLIENT_SECRET", "client-secret")
    monkeypatch.delenv("GLOO_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(clients.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.calls.clear()

    client = GlooClient()
    first = asyncio.run(client._get_access_token())
    second = asyncio.run(client._get_access_token())

    assert first == "header.payload.signature"
    assert second == first
    assert client.auth_mode == "oauth2_client_credentials"
    assert len(FakeAsyncClient.calls) == 1

    url, request = FakeAsyncClient.calls[0]
    assert url == "https://platform.ai.gloo.com/oauth2/token"
    assert request["data"] == {
        "grant_type": "client_credentials",
        "scope": "api/access",
    }
    assert request["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
    assert isinstance(request["auth"], clients.httpx.BasicAuth)


def test_manual_short_lived_token_is_supported(monkeypatch):
    monkeypatch.setenv("GLOO_ACCESS_TOKEN", "temporary-token")
    monkeypatch.delenv("GLOO_CLIENT_ID", raising=False)
    monkeypatch.delenv("GLOO_CLIENT_SECRET", raising=False)
    client = GlooClient()
    assert client.configured is True
    assert client.auth_mode == "manual_bearer_token"
    assert asyncio.run(client._get_access_token()) == "temporary-token"


def test_json_extraction_accepts_plain_or_fenced_object():
    plain = '{"need":"endurance"}'
    fenced = '```json\n{"need":"endurance"}\n```'
    assert _extract_json_object(plain) == plain
    assert _extract_json_object(fenced) == plain
