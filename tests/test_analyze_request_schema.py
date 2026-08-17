import pytest
from px.schemas.analyze import AnalyzeRequest, Holding
from pydantic import ValidationError


def test_holding_accepts_ticker_and_weight():
    holding = Holding(ticker="AAPL", weight=0.5)
    assert holding.weight == 0.5


@pytest.mark.parametrize("weight", [-0.01, 1.01])
def test_holding_rejects_out_of_range_weight(weight):
    with pytest.raises(ValidationError):
        Holding(ticker="AAPL", weight=weight)


def test_holding_rejects_market_value_field():
    with pytest.raises(ValidationError):
        Holding(ticker="AAPL", weight=0.5, market_value=5000.0)


def test_analyze_request_holds_only_holdings():
    request = AnalyzeRequest(holdings=[Holding(ticker="AAPL", weight=1.0)])
    assert request.model_dump() == {"holdings": [{"ticker": "AAPL", "weight": 1.0}]}


def test_analyze_request_rejects_unknown_top_level_field():
    with pytest.raises(ValidationError):
        AnalyzeRequest(holdings=[Holding(ticker="AAPL", weight=1.0)], total_value=1000.0)
