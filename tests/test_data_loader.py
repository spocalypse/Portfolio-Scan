from datetime import date, timedelta

from px.data.cache import PricePoint, TickerMetadata, connect, upsert_prices
from px.data.loader import (
    ExcludedTicker,
    FetchedTicker,
    fetch_ticker,
    load_tickers,
    partition_by_history,
)

_TODAY = date(2026, 8, 17)


def _prices(n: int, start: date = date(2024, 1, 2)) -> tuple[PricePoint, ...]:
    return tuple(PricePoint(start + timedelta(days=i), 100.0 + i) for i in range(n))


class FakeSource:
    def __init__(self, history_by_ticker=None, fail_times: int = 0, always_fail=False):
        self._history = history_by_ticker or {}
        self._fail_times = fail_times
        self._always_fail = always_fail
        self.history_calls: list[str] = []

    def fetch_history(self, ticker: str):
        self.history_calls.append(ticker)
        if self._always_fail or len(self.history_calls) <= self._fail_times:
            raise ConnectionError("simulated network failure")
        return self._history.get(ticker, ())

    def fetch_metadata(self, ticker: str) -> TickerMetadata:
        return TickerMetadata("Information Technology", "Software")


def _conn(tmp_path):
    return connect(tmp_path / "cache.sqlite3")


def _no_sleep(calls):
    def _sleep(seconds: float) -> None:
        calls.append(seconds)

    return _sleep


def test_fresh_fetch_populates_cache_and_returns_prices(tmp_path):
    conn = _conn(tmp_path)
    source = FakeSource(history_by_ticker={"AAPL": _prices(260)})

    result = fetch_ticker("AAPL", source=source, conn=conn, today=_TODAY)

    assert len(result.prices) == 260
    assert result.stale is False
    assert source.history_calls == ["AAPL"]


def test_second_fetch_same_day_hits_cache_not_source(tmp_path):
    conn = _conn(tmp_path)
    source = FakeSource(history_by_ticker={"AAPL": _prices(260)})

    fetch_ticker("AAPL", source=source, conn=conn, today=_TODAY)
    fetch_ticker("AAPL", source=source, conn=conn, today=_TODAY)

    assert source.history_calls == ["AAPL"]


def test_next_day_fetch_hits_source_again(tmp_path):
    conn = _conn(tmp_path)
    source = FakeSource(history_by_ticker={"AAPL": _prices(260)})

    fetch_ticker("AAPL", source=source, conn=conn, today=_TODAY)
    fetch_ticker("AAPL", source=source, conn=conn, today=_TODAY + timedelta(days=1))

    assert source.history_calls == ["AAPL", "AAPL"]


def test_retries_with_backoff_before_succeeding(tmp_path):
    conn = _conn(tmp_path)
    source = FakeSource(history_by_ticker={"AAPL": _prices(260)}, fail_times=2)
    sleeps: list[float] = []

    result = fetch_ticker(
        "AAPL",
        source=source,
        conn=conn,
        today=_TODAY,
        max_attempts=3,
        backoff_seconds=1.0,
        sleep_fn=_no_sleep(sleeps),
    )

    assert len(result.prices) == 260
    assert result.stale is False
    assert sleeps == [1.0, 2.0]


def test_total_failure_falls_back_to_cache_and_marks_stale(tmp_path):
    conn = _conn(tmp_path)
    upsert_prices(conn, "AAPL", _prices(260))
    failing_source = FakeSource(always_fail=True)

    result = fetch_ticker(
        "AAPL",
        source=failing_source,
        conn=conn,
        today=_TODAY,
        max_attempts=3,
        sleep_fn=_no_sleep([]),
    )

    assert result.stale is True
    assert len(result.prices) == 260


def test_total_failure_with_no_cache_returns_empty_without_crashing(tmp_path):
    conn = _conn(tmp_path)
    failing_source = FakeSource(always_fail=True)

    result = fetch_ticker(
        "NEWLISTING",
        source=failing_source,
        conn=conn,
        today=_TODAY,
        max_attempts=2,
        sleep_fn=_no_sleep([]),
    )

    assert result.prices == ()
    assert result.stale is True


def test_load_tickers_never_raises_even_if_one_ticker_is_pathological(tmp_path):
    conn = _conn(tmp_path)

    class ExplodingSource(FakeSource):
        def fetch_metadata(self, ticker: str) -> TickerMetadata:
            if ticker == "BOOM":
                raise RuntimeError("unexpected")
            return super().fetch_metadata(ticker)

    source = ExplodingSource(history_by_ticker={"AAPL": _prices(260)})

    results = load_tickers(["AAPL", "BOOM"], source=source, conn=conn, today=_TODAY)

    assert [r.ticker for r in results] == ["AAPL", "BOOM"]
    assert results[1].prices == ()


def test_partition_excludes_short_history_without_crashing():
    fetched = (
        FetchedTicker("AAPL", _prices(260), TickerMetadata(None, None), False, None),
        FetchedTicker("IPO", _prices(30), TickerMetadata(None, None), False, None),
    )

    result = partition_by_history(fetched)

    assert [f.ticker for f in result.included] == ["AAPL"]
    assert result.excluded == (
        ExcludedTicker("IPO", "insufficient_price_history", "30 trading day(s) available, need 250"),
    )


def test_partition_boundary_is_inclusive_at_exactly_min_days():
    fetched = (FetchedTicker("EDGE", _prices(250), TickerMetadata(None, None), False, None),)

    result = partition_by_history(fetched)

    assert [f.ticker for f in result.included] == ["EDGE"]
    assert result.excluded == ()
