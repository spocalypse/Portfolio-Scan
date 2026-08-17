"""Generates fixtures/symbol_table.parquet from NASDAQ Trader's public symbol
directory (SPEC §5.3).

Run manually (`python3.11 scripts/build_symbol_table.py`) to regenerate the frozen
table. Never run as part of `make test` or `make lint` — regenerating it is a
deliberate, logged action, not a side effect, same as build_metrics_fixture.py.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import pandas as pd

TABLE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "symbol_table.parquet"

_NASDAQ_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
_OTHER_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

_OTHER_EXCHANGE_NAMES = {
    "A": "NYSE American",
    "N": "NYSE",
    "P": "NYSE Arca",
    "Z": "Cboe BZX",
    "V": "IEX",
}


def _fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def _parse_nasdaqlisted(text: str) -> pd.DataFrame:
    lines = [line for line in text.splitlines() if line and "|" in line]
    rows = [line.split("|") for line in lines[1:] if not line.startswith("File Creation")]
    frame = pd.DataFrame(
        rows,
        columns=[
            "Symbol",
            "Security Name",
            "Market Category",
            "Test Issue",
            "Financial Status",
            "Round Lot Size",
            "ETF",
            "NextShares",
        ],
    )
    frame = frame[frame["Test Issue"] == "N"]
    return pd.DataFrame(
        {
            "ticker": frame["Symbol"].str.strip().str.upper(),
            "name": frame["Security Name"].str.strip(),
            "exchange": "NASDAQ",
            "is_etf": frame["ETF"] == "Y",
        }
    )


def _parse_otherlisted(text: str) -> pd.DataFrame:
    lines = [line for line in text.splitlines() if line and "|" in line]
    rows = [line.split("|") for line in lines[1:] if not line.startswith("File Creation")]
    frame = pd.DataFrame(
        rows,
        columns=[
            "ACT Symbol",
            "Security Name",
            "Exchange",
            "CQS Symbol",
            "ETF",
            "Round Lot Size",
            "Test Issue",
            "NASDAQ Symbol",
        ],
    )
    frame = frame[frame["Test Issue"] == "N"]
    return pd.DataFrame(
        {
            "ticker": frame["ACT Symbol"].str.strip().str.upper(),
            "name": frame["Security Name"].str.strip(),
            "exchange": frame["Exchange"].map(_OTHER_EXCHANGE_NAMES).fillna("Other"),
            "is_etf": frame["ETF"] == "Y",
        }
    )


def main() -> None:
    nasdaq = _parse_nasdaqlisted(_fetch(_NASDAQ_URL))
    other = _parse_otherlisted(_fetch(_OTHER_URL))

    table = pd.concat([nasdaq, other], ignore_index=True)
    duplicated = table["ticker"].duplicated(keep="first")
    if duplicated.any():
        print(f"Dropping {duplicated.sum()} duplicate ticker(s) across the two files")
        table = table[~duplicated]

    table = table.sort_values("ticker").reset_index(drop=True)
    table.to_parquet(TABLE_PATH, index=False)
    print(f"Wrote {len(table)} rows to {TABLE_PATH}")
    print(f"  NASDAQ: {(table['exchange'] == 'NASDAQ').sum()}")
    print(f"  ETFs: {table['is_etf'].sum()}")


if __name__ == "__main__":
    main()
