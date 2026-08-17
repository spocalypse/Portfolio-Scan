from datetime import date

from px.data.cache import (
    PricePoint,
    TickerMetadata,
    connect,
    get_cached_metadata,
    get_cached_prices,
    mark_fetched,
    upsert_metadata,
    upsert_prices,
    was_fetched_today,
)


def _conn(tmp_path):
    return connect(tmp_path / "cache.sqlite3")


def test_price_round_trip(tmp_path):
    conn = _conn(tmp_path)
    points = (PricePoint(date(2026, 1, 2), 100.0), PricePoint(date(2026, 1, 5), 101.5))

    upsert_prices(conn, "AAPL", points)

    assert get_cached_prices(conn, "AAPL") == points


def test_upsert_prices_replaces_same_date_value(tmp_path):
    conn = _conn(tmp_path)
    upsert_prices(conn, "AAPL", (PricePoint(date(2026, 1, 2), 100.0),))
    upsert_prices(conn, "AAPL", (PricePoint(date(2026, 1, 2), 105.0),))

    prices = get_cached_prices(conn, "AAPL")

    assert prices == (PricePoint(date(2026, 1, 2), 105.0),)


def test_metadata_round_trip(tmp_path):
    conn = _conn(tmp_path)
    upsert_metadata(conn, "AAPL", TickerMetadata("Information Technology", "Consumer Electronics"))

    assert get_cached_metadata(conn, "AAPL") == TickerMetadata(
        "Information Technology", "Consumer Electronics"
    )


def test_metadata_defaults_to_none_when_uncached(tmp_path):
    conn = _conn(tmp_path)

    assert get_cached_metadata(conn, "NOPE") == TickerMetadata(None, None)


def test_was_fetched_today_false_before_any_fetch(tmp_path):
    conn = _conn(tmp_path)

    assert was_fetched_today(conn, "AAPL", date(2026, 8, 17)) is False


def test_mark_fetched_makes_was_fetched_today_true(tmp_path):
    conn = _conn(tmp_path)
    mark_fetched(conn, "AAPL", date(2026, 8, 17))

    assert was_fetched_today(conn, "AAPL", date(2026, 8, 17)) is True


def test_was_fetched_today_false_on_a_different_day(tmp_path):
    conn = _conn(tmp_path)
    mark_fetched(conn, "AAPL", date(2026, 8, 17))

    assert was_fetched_today(conn, "AAPL", date(2026, 8, 18)) is False


def test_cache_is_isolated_per_ticker(tmp_path):
    conn = _conn(tmp_path)
    upsert_prices(conn, "AAPL", (PricePoint(date(2026, 1, 2), 100.0),))

    assert get_cached_prices(conn, "MSFT") == ()
