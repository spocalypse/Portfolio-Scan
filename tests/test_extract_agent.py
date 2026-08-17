import logging

import pytest
from conftest import FakeAnthropicClient
from px.extract.agent import (
    MODEL_HAIKU,
    MODEL_SONNET,
    ExtractionFailedError,
    extract_holdings,
)

_CONFIDENT_ROW = {
    "raw_label": "AAPL 10 sh",
    "ticker_guess": "AAPL",
    "quantity": 10.0,
    "market_value": 1500.0,
    "confidence": 0.97,
}

_AMBIGUOUS_ROW = {
    "raw_label": "???",
    "ticker_guess": None,
    "quantity": None,
    "market_value": None,
    "confidence": 0.3,
}


def _payload(rows: list[dict]) -> dict:
    return {
        "rows": rows,
        "total_value": 1500.0,
        "brokerage_guess": "Fidelity",
        "warnings": [],
    }


def test_confident_haiku_result_is_not_escalated():
    client = FakeAnthropicClient(responses=[_payload([_CONFIDENT_ROW])])

    result = extract_holdings(b"fake-image-bytes", "image/png", client=client)

    assert len(client.calls) == 1
    assert client.calls[0]["model"] == MODEL_HAIKU
    assert result.model_used == MODEL_HAIKU
    assert result.rows[0].ticker_guess == "AAPL"


def test_low_confidence_row_escalates_to_sonnet():
    client = FakeAnthropicClient(
        responses=[_payload([_AMBIGUOUS_ROW]), _payload([_CONFIDENT_ROW])]
    )

    result = extract_holdings(b"fake-image-bytes", "image/png", client=client)

    assert len(client.calls) == 2
    assert client.calls[0]["model"] == MODEL_HAIKU
    assert client.calls[1]["model"] == MODEL_SONNET
    assert result.model_used == MODEL_SONNET
    assert result.rows[0].ticker_guess == "AAPL"


def test_zero_rows_does_not_escalate():
    client = FakeAnthropicClient(responses=[_payload([])])

    result = extract_holdings(b"fake-image-bytes", "image/png", client=client)

    assert len(client.calls) == 1
    assert result.model_used == MODEL_HAIKU
    assert result.rows == []


def test_malformed_haiku_output_escalates_to_sonnet():
    malformed = {"rows": [{"raw_label": "x"}], "total_value": None}  # missing fields
    client = FakeAnthropicClient(responses=[malformed, _payload([_CONFIDENT_ROW])])

    result = extract_holdings(b"fake-image-bytes", "image/png", client=client)

    assert len(client.calls) == 2
    assert result.model_used == MODEL_SONNET


def test_haiku_never_calling_the_tool_escalates_to_sonnet():
    client = FakeAnthropicClient(responses=[None, _payload([_CONFIDENT_ROW])])

    result = extract_holdings(b"fake-image-bytes", "image/png", client=client)

    assert len(client.calls) == 2
    assert result.model_used == MODEL_SONNET


def test_both_models_failing_schema_raises_without_fabricating():
    client = FakeAnthropicClient(responses=[None, None])

    with pytest.raises(ExtractionFailedError):
        extract_holdings(b"fake-image-bytes", "image/png", client=client)

    assert len(client.calls) == 2


def test_log_line_contains_only_the_allowlisted_fields(caplog):
    client = FakeAnthropicClient(responses=[_payload([_CONFIDENT_ROW])])

    with caplog.at_level(logging.INFO, logger="px.extract"):
        extract_holdings(
            b"fake-image-bytes", "image/png", client=client, request_id="req-123"
        )

    record = caplog.records[0]
    assert record.request_id == "req-123"
    assert record.model_used == MODEL_HAIKU
    assert record.row_count == 1
    assert record.error_code is None
    assert isinstance(record.duration_ms, float)


def test_hard_failure_still_logs_an_error_code(caplog):
    client = FakeAnthropicClient(responses=[None, None])

    with (
        caplog.at_level(logging.INFO, logger="px.extract"),
        pytest.raises(ExtractionFailedError),
    ):
        extract_holdings(b"fake-image-bytes", "image/png", client=client)

    record = caplog.records[0]
    assert record.error_code == "extraction_schema_failure"
    assert record.model_used is None
    assert record.row_count == 0
