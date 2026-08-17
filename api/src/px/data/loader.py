"""D — Data Layer orchestration (SPEC §5.4). fetch_ticker/load_tickers do I/O (cache +
network via a PriceSource); partition_by_history is pure and separated out the same way
resolver.py splits detection logic from table.py's I/O, so the 250-day rule is testable
without a cache or a network fetch in sight.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date
from sqlite3 import Connection
from typing import Literal

from px.data.cache import (
    PricePoint,
    TickerMetadata,
    get_cached_metadata,
    get_cached_prices,
    mark_fetched,
    upsert_metadata,
    upsert_prices,
    was_fetched_today,
)
from px.data.source import PriceSource

MIN_TRADING_DAYS = 250
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BACKOFF_SECONDS = 1.0


@dataclass(frozen=True)
class FetchedTicker:
    ticker: str
    prices: tuple[PricePoint, ...]
    metadata: TickerMetadata
    stale: bool
    as_of: date | None


@dataclass(frozen=True)
class ExcludedTicker:
    ticker: str
    reason: Literal["insufficient_price_history"]
    detail: str


@dataclass(frozen=True)
class DataLoadResult:
    included: tuple[FetchedTicker, ...] = field(default_factory=tuple)
    excluded: tuple[ExcludedTicker, ...] = field(default_factory=tuple)


def _as_of(prices: Sequence[PricePoint]) -> date | None:
    return prices[-1].date if prices else None


def _fetch_with_retry(
    ticker: str,
    source: PriceSource,
    *,
    max_attempts: int,
    backoff_seconds: float,
    sleep_fn: Callable[[float], None],
) -> tuple[tuple[PricePoint, ...], TickerMetadata] | None:
    """None means every attempt raised — a transient failure, not "no data exists"
    (an unknown ticker returns an empty-but-successful result, handled by the caller).
    """
    for attempt in range(max_attempts):
        try:
            prices = source.fetch_history(ticker)
            metadata = source.fetch_metadata(ticker)
            return prices, metadata
        except Exception:  # noqa: BLE001 - network boundary, any failure retries
            if attempt < max_attempts - 1:
                sleep_fn(backoff_seconds * (2**attempt))
    return None


def fetch_ticker(
    ticker: str,
    *,
    source: PriceSource,
    conn: Connection,
    today: date,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> FetchedTicker:
    if was_fetched_today(conn, ticker, today):
        prices = get_cached_prices(conn, ticker)
        metadata = get_cached_metadata(conn, ticker)
        return FetchedTicker(ticker, prices, metadata, False, _as_of(prices))

    fetched = _fetch_with_retry(
        ticker,
        source,
        max_attempts=max_attempts,
        backoff_seconds=backoff_seconds,
        sleep_fn=sleep_fn,
    )

    if fetched is not None:
        prices, metadata = fetched
        upsert_prices(conn, ticker, prices)
        upsert_metadata(conn, ticker, metadata)
        mark_fetched(conn, ticker, today)
        return FetchedTicker(ticker, prices, metadata, False, _as_of(prices))

    # Total failure after retries — fall back to whatever is cached, marked stale.
    # An empty cache here just means an empty FetchedTicker; partition_by_history
    # excludes it below rather than crashing.
    cached_prices = get_cached_prices(conn, ticker)
    cached_metadata = get_cached_metadata(conn, ticker)
    return FetchedTicker(
        ticker, cached_prices, cached_metadata, True, _as_of(cached_prices)
    )


def load_tickers(
    tickers: Sequence[str],
    *,
    source: PriceSource,
    conn: Connection,
    today: date | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> tuple[FetchedTicker, ...]:
    today = today or date.today()
    results = []
    for ticker in tickers:
        try:
            results.append(
                fetch_ticker(
                    ticker,
                    source=source,
                    conn=conn,
                    today=today,
                    max_attempts=max_attempts,
                    backoff_seconds=backoff_seconds,
                    sleep_fn=sleep_fn,
                )
            )
        except Exception:  # noqa: BLE001 - one bad ticker must never crash the batch
            results.append(
                FetchedTicker(ticker, (), TickerMetadata(None, None), True, None)
            )
    return tuple(results)


def partition_by_history(
    fetched: Sequence[FetchedTicker], *, min_days: int = MIN_TRADING_DAYS
) -> DataLoadResult:
    included = []
    excluded = []
    for item in fetched:
        if len(item.prices) >= min_days:
            included.append(item)
        else:
            excluded.append(
                ExcludedTicker(
                    item.ticker,
                    "insufficient_price_history",
                    f"{len(item.prices)} trading day(s) available, need {min_days}",
                )
            )
    return DataLoadResult(tuple(included), tuple(excluded))
