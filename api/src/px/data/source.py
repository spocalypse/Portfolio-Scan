"""The only module that imports yfinance directly (SPEC §5.4). Version pinned exactly
in api/pyproject.toml — verified against yfinance==1.6.0's actual return shapes before
writing this: history(period="3y", auto_adjust=True) gives a tz-aware DatetimeIndex
and an already-adjusted "Close" column; .info has "sector"/"industry", both None for
ETFs; an unknown ticker returns an empty DataFrame rather than raising.
"""

from __future__ import annotations

from typing import Protocol

import yfinance as yf

from px.data.cache import PricePoint, TickerMetadata

_HISTORY_PERIOD = "3y"


class PriceSource(Protocol):
    def fetch_history(self, ticker: str) -> tuple[PricePoint, ...]: ...

    def fetch_metadata(self, ticker: str) -> TickerMetadata: ...


class YFinanceSource:
    def fetch_history(self, ticker: str) -> tuple[PricePoint, ...]:
        frame = yf.Ticker(ticker).history(period=_HISTORY_PERIOD, auto_adjust=True)
        if frame.empty:
            return ()
        return tuple(
            PricePoint(index.date(), float(close))
            for index, close in frame["Close"].items()
        )

    def fetch_metadata(self, ticker: str) -> TickerMetadata:
        info = yf.Ticker(ticker).info
        return TickerMetadata(info.get("sector"), info.get("industry"))
