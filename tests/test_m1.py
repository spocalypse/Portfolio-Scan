import pytest
from px.analytics.m1 import (
    HoldingInput,
    SectorCapitalWeight,
    aggregate_sector_weights,
    compute_effective_position_count,
    compute_hhi,
    compute_m1,
    renormalize,
    top_sector_concentration,
)

_TOL = 1e-6


def test_100_percent_spy_is_a_single_unclassified_position():
    holdings = [HoldingInput("SPY", 1.0, None, is_etf=True)]

    result = compute_m1(holdings)

    assert result.positions[0].capital_weight == pytest.approx(1.0)
    assert result.unclassified_weight == pytest.approx(1.0)
    assert result.sector_weights == ()
    assert result.top_sector_concentration == ()
    assert result.hhi == pytest.approx(1.0)
    assert result.effective_position_count == pytest.approx(1.0)


def test_50_50_spy_shv_gives_hhi_one_half():
    holdings = [
        HoldingInput("SPY", 0.5, None, is_etf=True),
        HoldingInput("SHV", 0.5, None, is_etf=True),
    ]

    result = compute_m1(holdings)

    assert result.hhi == pytest.approx(0.5)
    assert result.effective_position_count == pytest.approx(2.0)


def test_equal_weight_ten_mega_cap_tech_groups_into_one_sector():
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "ORCL", "CRM"]
    holdings = [
        HoldingInput(t, 0.1, "Information Technology", is_etf=False) for t in tickers
    ]

    result = compute_m1(holdings)

    assert result.hhi == pytest.approx(0.1)
    assert result.effective_position_count == pytest.approx(10.0)
    assert len(result.sector_weights) == 1
    assert result.sector_weights[0].sector == "Information Technology"
    assert result.sector_weights[0].capital_weight == pytest.approx(1.0)
    assert result.unclassified_weight == pytest.approx(0.0)


def test_capital_weights_always_sum_to_one_within_tolerance():
    holdings = [
        HoldingInput("AAPL", 0.13, "Information Technology", is_etf=False),
        HoldingInput("JPM", 0.22, "Financials", is_etf=False),
        HoldingInput("XOM", 0.07, "Energy", is_etf=False),
        HoldingInput("SPY", 0.58, None, is_etf=True),
    ]

    result = compute_m1(holdings)

    assert sum(p.capital_weight for p in result.positions) == pytest.approx(1.0, abs=_TOL)


def test_renormalize_restores_sum_to_one_after_upstream_exclusion():
    # Simulates holdings surviving resolver/data-layer exclusion, no longer summing to 1.
    holdings = [
        HoldingInput("AAPL", 0.5, "Information Technology", is_etf=False),
        HoldingInput("JPM", 0.3, "Financials", is_etf=False),
        HoldingInput("XOM", 0.1, "Energy", is_etf=False),
    ]

    positions = renormalize(holdings)

    assert sum(p.capital_weight for p in positions) == pytest.approx(1.0, abs=_TOL)
    assert positions[0].capital_weight == pytest.approx(0.5 / 0.9)
    assert positions[1].capital_weight == pytest.approx(0.3 / 0.9)
    assert positions[2].capital_weight == pytest.approx(0.1 / 0.9)


def test_renormalize_raises_on_zero_total_weight():
    with pytest.raises(ValueError):
        renormalize([HoldingInput("AAPL", 0.0, "Information Technology", is_etf=False)])


def test_aggregate_sector_weights_separates_unclassified():
    positions = renormalize(
        [
            HoldingInput("AAPL", 0.4, "Information Technology", is_etf=False),
            HoldingInput("MSFT", 0.4, "Information Technology", is_etf=False),
            HoldingInput("SPY", 0.2, None, is_etf=True),
        ]
    )

    sector_weights, unclassified = aggregate_sector_weights(positions)

    assert len(sector_weights) == 1
    assert sector_weights[0].sector == "Information Technology"
    assert sector_weights[0].capital_weight == pytest.approx(0.8)
    assert unclassified == pytest.approx(0.2)


def test_top_sector_concentration_orders_descending_and_caps_at_three():
    weights = [
        SectorCapitalWeight("Energy", 0.1),
        SectorCapitalWeight("Information Technology", 0.5),
        SectorCapitalWeight("Financials", 0.2),
        SectorCapitalWeight("Health Care", 0.2),
    ]

    top = top_sector_concentration(weights, n=3)

    assert [t.sector for t in top] == ["Information Technology", "Financials", "Health Care"]


def test_top_sector_concentration_tiebreaks_deterministically_by_sector_name():
    weights = [
        SectorCapitalWeight("Utilities", 0.5),
        SectorCapitalWeight("Energy", 0.5),
    ]

    top = top_sector_concentration(weights, n=3)

    assert [t.sector for t in top] == ["Energy", "Utilities"]


def test_compute_hhi_matches_effective_position_count_inverse():
    weights = [0.25, 0.25, 0.25, 0.25]

    hhi = compute_hhi(weights)

    assert hhi == pytest.approx(0.25)
    assert compute_effective_position_count(hhi) == pytest.approx(4.0)
