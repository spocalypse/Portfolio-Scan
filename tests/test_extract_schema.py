import pytest
from px.schemas.extract import ExtractResponse, ExtractRow
from pydantic import ValidationError


def test_extract_row_accepts_full_row():
    row = ExtractRow(
        raw_label="AAPL 10 sh",
        ticker_guess="AAPL",
        quantity=10.0,
        market_value=1500.0,
        confidence=0.95,
    )
    assert row.ticker_guess == "AAPL"


def test_extract_row_allows_null_ticker_for_ambiguous_rows():
    row = ExtractRow(
        raw_label="???",
        ticker_guess=None,
        quantity=None,
        market_value=None,
        confidence=0.0,
    )
    assert row.confidence == 0.0


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_extract_row_rejects_out_of_range_confidence(confidence):
    with pytest.raises(ValidationError):
        ExtractRow(
            raw_label="x",
            ticker_guess="AAPL",
            quantity=1.0,
            market_value=100.0,
            confidence=confidence,
        )


def test_extract_row_has_no_account_identifier_field():
    banned = {"account", "account_number", "account_name", "holder", "owner", "ssn"}
    assert not (set(ExtractRow.model_fields) & banned)


def test_extract_row_rejects_unknown_field():
    with pytest.raises(ValidationError):
        ExtractRow(
            raw_label="x",
            ticker_guess="AAPL",
            quantity=1.0,
            market_value=100.0,
            confidence=0.9,
            account_number="12345",
        )


def test_extract_response_round_trips():
    response = ExtractResponse(
        rows=[
            ExtractRow(
                raw_label="AAPL 10 sh",
                ticker_guess="AAPL",
                quantity=10.0,
                market_value=1500.0,
                confidence=0.95,
            )
        ],
        total_value=1500.0,
        brokerage_guess="Fidelity",
        warnings=[],
        model_used="claude-haiku-4-5-20251001",
    )
    reparsed = ExtractResponse.model_validate_json(response.model_dump_json())
    assert reparsed == response
