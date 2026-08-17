"""Shared return-series prep for M2-M5 (SPEC §5.5 intro: "Simple daily returns").
Pure, no I/O — takes plain (date, price) pairs so this module never needs to know
where the prices came from.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date


def simple_returns(
    prices: Sequence[tuple[date, float]],
) -> tuple[tuple[date, float], ...]:
    """r_t = (p_t - p_{t-1}) / p_{t-1}. Sorts by date; caller may pass unsorted."""
    ordered = sorted(prices, key=lambda p: p[0])
    return tuple(
        (ordered[i][0], (ordered[i][1] - ordered[i - 1][1]) / ordered[i - 1][1])
        for i in range(1, len(ordered))
    )


def align_returns(
    returns_by_ticker: Mapping[str, Sequence[tuple[date, float]]],
) -> tuple[tuple[date, ...], dict[str, tuple[float, ...]]]:
    """Inner-joins every series onto their common dates — tickers with gaps (holidays,
    late listings, missing cache rows) never desync the resulting matrix.
    """
    per_ticker = {ticker: dict(series) for ticker, series in returns_by_ticker.items()}
    common_dates: set[date] | None = None
    for dates_for_ticker in per_ticker.values():
        keys = set(dates_for_ticker.keys())
        common_dates = keys if common_dates is None else common_dates & keys
    ordered_dates = tuple(sorted(common_dates or ()))
    aligned = {
        ticker: tuple(series[d] for d in ordered_dates)
        for ticker, series in per_ticker.items()
    }
    return ordered_dates, aligned
