from datetime import date

import pytest
from px.analytics.returns import align_returns, simple_returns


def test_simple_returns_computes_pct_change_and_sorts_first():
    prices = [
        (date(2026, 1, 3), 102.0),
        (date(2026, 1, 2), 100.0),
        (date(2026, 1, 4), 101.0),
    ]

    result = simple_returns(prices)

    assert result[0][0] == date(2026, 1, 3)
    assert result[0][1] == pytest.approx(0.02)
    assert result[1][0] == date(2026, 1, 4)
    assert result[1][1] == pytest.approx(101.0 / 102.0 - 1)


def test_simple_returns_single_price_gives_no_returns():
    assert simple_returns([(date(2026, 1, 2), 100.0)]) == ()


def test_align_returns_inner_joins_on_common_dates():
    a = [
        (date(2026, 1, 2), 0.01),
        (date(2026, 1, 3), 0.02),
        (date(2026, 1, 4), 0.03),
    ]
    b = [(date(2026, 1, 2), 0.05), (date(2026, 1, 4), 0.06)]  # missing 1/3

    dates, aligned = align_returns({"A": a, "B": b})

    assert dates == (date(2026, 1, 2), date(2026, 1, 4))
    assert aligned["A"] == (0.01, 0.03)
    assert aligned["B"] == (0.05, 0.06)


def test_align_returns_with_no_overlap_is_empty_not_a_crash():
    dates, aligned = align_returns(
        {"A": [(date(2026, 1, 2), 0.01)], "B": [(date(2026, 1, 3), 0.02)]}
    )

    assert dates == ()
    assert aligned == {"A": (), "B": ()}
