"""The price/metadata cache's only I/O boundary (SPEC §5.4). SQLite via stdlib
sqlite3 — no new dependency. Keyed by (ticker, date); loader.py enforces the
once-per-day fetch rule using fetch_log below.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

DEFAULT_CACHE_PATH = (
    Path(__file__).resolve().parents[4] / ".cache" / "price_cache.sqlite3"
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    adj_close REAL NOT NULL,
    PRIMARY KEY (ticker, date)
);
CREATE TABLE IF NOT EXISTS metadata (
    ticker TEXT PRIMARY KEY,
    sector TEXT,
    industry TEXT
);
CREATE TABLE IF NOT EXISTS fetch_log (
    ticker TEXT PRIMARY KEY,
    last_fetched_date TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class PricePoint:
    date: date
    adj_close: float


@dataclass(frozen=True)
class TickerMetadata:
    sector: str | None
    industry: str | None


def connect(path: Path = DEFAULT_CACHE_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def was_fetched_today(conn: sqlite3.Connection, ticker: str, today: date) -> bool:
    row = conn.execute(
        "SELECT last_fetched_date FROM fetch_log WHERE ticker = ?", (ticker,)
    ).fetchone()
    return row is not None and row[0] == today.isoformat()


def mark_fetched(conn: sqlite3.Connection, ticker: str, today: date) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO fetch_log (ticker, last_fetched_date) VALUES (?, ?)",
        (ticker, today.isoformat()),
    )
    conn.commit()


def get_cached_prices(conn: sqlite3.Connection, ticker: str) -> tuple[PricePoint, ...]:
    rows = conn.execute(
        "SELECT date, adj_close FROM prices WHERE ticker = ? ORDER BY date",
        (ticker,),
    ).fetchall()
    return tuple(PricePoint(date.fromisoformat(d), c) for d, c in rows)


def upsert_prices(
    conn: sqlite3.Connection, ticker: str, points: Sequence[PricePoint]
) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO prices (ticker, date, adj_close) VALUES (?, ?, ?)",
        [(ticker, p.date.isoformat(), p.adj_close) for p in points],
    )
    conn.commit()


def get_cached_metadata(conn: sqlite3.Connection, ticker: str) -> TickerMetadata:
    row = conn.execute(
        "SELECT sector, industry FROM metadata WHERE ticker = ?", (ticker,)
    ).fetchone()
    if row is None:
        return TickerMetadata(None, None)
    return TickerMetadata(row[0], row[1])


def upsert_metadata(
    conn: sqlite3.Connection, ticker: str, metadata: TickerMetadata
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO metadata (ticker, sector, industry) VALUES (?, ?, ?)",
        (ticker, metadata.sector, metadata.industry),
    )
    conn.commit()
