"""R — Resolver (SPEC §5.3). Deterministic, no LLM, no I/O, no network — takes a
SymbolTable (see table.py) as a plain argument so it's testable against small synthetic
tables independent of the real fixture.
"""

from __future__ import annotations

import re
import string
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

from px.resolve.table import SymbolTable
from px.schemas.analyze import Holding

ExclusionReason = Literal["not_found", "ambiguous", "non_us_suffix"]

# Small, explicit set — SPEC §5.3 is US-only (D2); this is a cheap first-pass filter,
# not a substitute for the table itself being NASDAQ/NYSE-only.
_NON_US_SUFFIXES = (
    ".TO", ".V", ".L", ".AX", ".HK", ".SI", ".DE", ".PA", ".SW", ".TW",
)

# Matches a share class already spelled with a separator, e.g. "BRK-B", "BRK/B".
_SHARE_CLASS_RE = re.compile(r"^(?P<base>[A-Z]{1,5})[.\-/ ](?P<letter>[A-Z])$")
# Matches a bare base symbol with no class letter at all, e.g. "BRK".
_BARE_BASE_RE = re.compile(r"^[A-Z]{1,5}$")
# No bare "" separator here on purpose: for a bare base like "BRK", trying BRK+letter
# with no separator degenerates into prefix matching against the whole table (real
# unrelated tickers like BRKR/BRKU/BRKC start with "BRK" too) — every brokerage-visible
# share-class rendering actually uses one of these three explicit separators.
_SEPARATORS = (".", "-", "/")


@dataclass(frozen=True)
class ResolvedHolding:
    ticker: str
    weight: float
    is_etf: bool
    exchange: str


@dataclass(frozen=True)
class ExcludedHolding:
    raw_ticker: str
    weight: float
    reason: ExclusionReason
    candidates: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResolveResult:
    resolved: tuple[ResolvedHolding, ...]
    excluded: tuple[ExcludedHolding, ...]


def _share_class_candidates(normalized: str, table: SymbolTable) -> set[str]:
    """Distinct table tickers reachable from `normalized` by treating it as a base
    symbol + share-class letter under any of the separators brokerages actually use.
    An exact table hit is handled by the caller before this ever runs — this only
    covers the "not an exact key, but shaped like a share class" cases.
    """
    found: set[str] = set()

    m = _SHARE_CLASS_RE.match(normalized)
    if m:
        base, letter = m.group("base"), m.group("letter")
        for sep in _SEPARATORS:
            variant = f"{base}{sep}{letter}"
            if variant in table:
                found.add(variant)
        return found

    if _BARE_BASE_RE.match(normalized):
        for sep in _SEPARATORS:
            for letter in string.ascii_uppercase:
                variant = f"{normalized}{sep}{letter}"
                if variant in table:
                    found.add(variant)

    return found


def resolve_holdings(holdings: Sequence[Holding], table: SymbolTable) -> ResolveResult:
    resolved: list[ResolvedHolding] = []
    excluded: list[ExcludedHolding] = []

    for holding in holdings:
        normalized = holding.ticker.strip().upper()

        if normalized.endswith(_NON_US_SUFFIXES):
            excluded.append(
                ExcludedHolding(holding.ticker, holding.weight, "non_us_suffix")
            )
            continue

        if normalized in table:
            entry = table[normalized]
            resolved.append(
                ResolvedHolding(
                    entry.ticker, holding.weight, entry.is_etf, entry.exchange
                )
            )
            continue

        candidates = sorted(_share_class_candidates(normalized, table))
        if len(candidates) == 1:
            entry = table[candidates[0]]
            resolved.append(
                ResolvedHolding(
                    entry.ticker, holding.weight, entry.is_etf, entry.exchange
                )
            )
        elif len(candidates) > 1:
            excluded.append(
                ExcludedHolding(
                    holding.ticker, holding.weight, "ambiguous", tuple(candidates)
                )
            )
        else:
            excluded.append(
                ExcludedHolding(holding.ticker, holding.weight, "not_found")
            )

    return ResolveResult(tuple(resolved), tuple(excluded))
