"""Yahoo Finance's sector taxonomy (yfinance .info["sector"]) mapped onto the 11
standard GICS sectors SPEC §5.5/schemas.common.GicsSector uses. Verified live against
real tickers spanning all 11 categories before writing this table — it's a clean 1:1
rename, not a lossy collapse; every Yahoo sector has exactly one GICS counterpart.
"""

from __future__ import annotations

from px.schemas.common import GicsSector

YAHOO_TO_GICS: dict[str, GicsSector] = {
    "Technology": "Information Technology",
    "Financial Services": "Financials",
    "Energy": "Energy",
    "Healthcare": "Health Care",
    "Consumer Defensive": "Consumer Staples",
    "Utilities": "Utilities",
    "Real Estate": "Real Estate",
    "Basic Materials": "Materials",
    "Industrials": "Industrials",
    "Communication Services": "Communication Services",
    "Consumer Cyclical": "Consumer Discretionary",
}


def map_to_gics_sector(yahoo_sector: str | None) -> GicsSector | None:
    """None in, None out — covers ETFs and anything yfinance didn't classify.
    Never guesses a sector for something that doesn't have one."""
    if yahoo_sector is None:
        return None
    return YAHOO_TO_GICS.get(yahoo_sector)
