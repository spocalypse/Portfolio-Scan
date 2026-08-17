import numpy as np
import pytest
from px.analytics.m2 import compute_beta, compute_portfolio_returns


def _market_returns(n: int = 260, seed: int = 42) -> tuple[float, ...]:
    rng = np.random.default_rng(seed)
    return tuple(rng.normal(0.0005, 0.01, n).tolist())


def test_100_percent_spy_beta_is_one_and_r_squared_is_high():
    # Portfolio == market proxy exactly: β and R² must both hit their theoretical max.
    market = _market_returns()

    result = compute_beta(market, market)

    assert result.beta == pytest.approx(1.0, abs=0.02)
    assert result.r_squared >= 0.98


def test_50_50_spy_shv_beta_is_approximately_half():
    market = _market_returns()
    shv = tuple(0.0 for _ in market)  # near-riskless proxy: ~zero variance, zero return

    portfolio = compute_portfolio_returns(
        {"SPY": 0.5, "SHV": 0.5}, {"SPY": market, "SHV": shv}
    )
    result = compute_beta(portfolio, market)

    assert result.beta == pytest.approx(0.5, abs=0.05)


def test_uncorrelated_series_give_a_low_r_squared():
    rng = np.random.default_rng(1)
    market = rng.normal(0, 0.01, 500).tolist()
    portfolio = rng.normal(0, 0.01, 500).tolist()

    result = compute_beta(portfolio, market)

    assert result.r_squared < 0.05


def test_compute_portfolio_returns_is_the_weighted_sum_per_day():
    weights = {"A": 0.6, "B": 0.4}
    returns_by_ticker = {"A": (0.01, 0.02, -0.01), "B": (0.0, 0.01, 0.03)}

    result = compute_portfolio_returns(weights, returns_by_ticker)

    assert result == pytest.approx(
        (0.6 * 0.01 + 0.4 * 0.0, 0.6 * 0.02 + 0.4 * 0.01, 0.6 * -0.01 + 0.4 * 0.03)
    )


def test_inverse_scaled_series_gives_negative_beta():
    market = _market_returns()
    inverse = tuple(-r for r in market)

    result = compute_beta(inverse, market)

    assert result.beta == pytest.approx(-1.0, abs=0.02)
    assert result.r_squared >= 0.98
