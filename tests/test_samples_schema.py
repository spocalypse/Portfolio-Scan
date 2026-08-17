import pytest
from px.schemas.analyze import Holding
from px.schemas.samples import SamplePortfolio, SamplesResponse

# Maps 3 of SPEC §5.8's 6 golden portfolios onto /api/samples (docs/DECISIONS.md).
GOLDEN_SAMPLES = [
    SamplePortfolio(
        id="spy-100",
        name="100% SPY",
        description="A single S&P 500 index fund.",
        holdings=[Holding(ticker="SPY", weight=1.0)],
    ),
    SamplePortfolio(
        id="spy-shv-5050",
        name="50/50 SPY / SHV",
        description="Half S&P 500, half short-term Treasury bills.",
        holdings=[Holding(ticker="SPY", weight=0.5), Holding(ticker="SHV", weight=0.5)],
    ),
    SamplePortfolio(
        id="tech-10-equal",
        name="Equal-weight mega-cap tech",
        description="Ten large technology names at equal weight.",
        holdings=[
            Holding(ticker=t, weight=0.10)
            for t in [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "NVDA",
                "META",
                "TSLA",
                "AVGO",
                "ORCL",
                "CRM",
            ]
        ],
    ),
]


def test_samples_response_holds_three_portfolios():
    response = SamplesResponse(samples=GOLDEN_SAMPLES)
    assert len(response.samples) == 3


@pytest.mark.parametrize("sample", GOLDEN_SAMPLES, ids=lambda s: s.id)
def test_each_sample_portfolio_weights_sum_to_one(sample):
    total = sum(h.weight for h in sample.holdings)
    assert total == pytest.approx(1.0, abs=1e-9)


def test_samples_response_round_trips():
    response = SamplesResponse(samples=GOLDEN_SAMPLES)
    reparsed = SamplesResponse.model_validate_json(response.model_dump_json())
    assert reparsed == response
