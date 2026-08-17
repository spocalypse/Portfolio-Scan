import pytest
from conftest import FakeAnthropicClient
from fastapi.testclient import TestClient
from px.main import app, get_anthropic_client

client = TestClient(app)

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"0" * 16

_VALID_PAYLOAD = {
    "rows": [
        {
            "raw_label": "AAPL 10 sh",
            "ticker_guess": "AAPL",
            "quantity": 10.0,
            "market_value": 1500.0,
            "confidence": 0.97,
        }
    ],
    "total_value": 1500.0,
    "brokerage_guess": "Fidelity",
    "warnings": [],
}


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _override_client(fake: FakeAnthropicClient) -> None:
    app.dependency_overrides[get_anthropic_client] = lambda: fake


def test_extract_returns_response_shape_only():
    _override_client(FakeAnthropicClient(responses=[_VALID_PAYLOAD]))

    response = client.post(
        "/api/extract", files={"image": ("shot.png", _PNG_MAGIC, "image/png")}
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {
        "rows",
        "total_value",
        "brokerage_guess",
        "warnings",
        "model_used",
    }
    assert body["model_used"] == "claude-haiku-4-5-20251001"


def test_extract_rejects_non_image_content():
    _override_client(FakeAnthropicClient(responses=[_VALID_PAYLOAD]))

    response = client.post(
        "/api/extract",
        files={"image": ("shot.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400


def test_extract_rejects_oversized_upload():
    _override_client(FakeAnthropicClient(responses=[_VALID_PAYLOAD]))
    oversized = _PNG_MAGIC + b"0" * (10 * 1024 * 1024)

    response = client.post(
        "/api/extract", files={"image": ("shot.png", oversized, "image/png")}
    )

    assert response.status_code == 413


def test_extract_returns_502_on_hard_extraction_failure():
    _override_client(FakeAnthropicClient(responses=[None, None]))

    response = client.post(
        "/api/extract", files={"image": ("shot.png", _PNG_MAGIC, "image/png")}
    )

    assert response.status_code == 502
