"""The symbol table's only I/O boundary (SPEC §5.3). resolver.py is pure and takes a
SymbolTable as a plain argument; nothing there reads a file or hits the network."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DEFAULT_TABLE_PATH = (
    Path(__file__).resolve().parents[4] / "fixtures" / "symbol_table.parquet"
)


@dataclass(frozen=True)
class SymbolEntry:
    ticker: str
    name: str
    exchange: str
    is_etf: bool


SymbolTable = Mapping[str, SymbolEntry]


def load_symbol_table(path: Path = DEFAULT_TABLE_PATH) -> SymbolTable:
    frame = pd.read_parquet(path)
    return {
        row.ticker: SymbolEntry(
            ticker=row.ticker,
            name=row.name,
            exchange=row.exchange,
            is_etf=bool(row.is_etf),
        )
        for row in frame.itertuples(index=False)
    }
