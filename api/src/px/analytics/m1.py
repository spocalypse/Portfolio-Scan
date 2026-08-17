"""M1 — Weights and sector exposure (SPEC §5.5). Pure functions, no I/O, no network
(CLAUDE.md rule 8). Inputs/outputs are this module's own dataclasses, not the frozen
`schemas.metrics` Pydantic models — `SectorExposure` there also carries M3's
risk_contribution_pct, so assembling the actual frozen contract objects is a later
integration step once M2/M3 exist too, not this issue's job.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from px.schemas.common import GicsSector

TOP_SECTOR_COUNT = 3


@dataclass(frozen=True)
class HoldingInput:
    ticker: str
    weight: float
    sector: GicsSector | None
    is_etf: bool


@dataclass(frozen=True)
class Position:
    ticker: str
    capital_weight: float
    sector: GicsSector | None
    is_etf: bool


@dataclass(frozen=True)
class SectorCapitalWeight:
    sector: GicsSector
    capital_weight: float


@dataclass(frozen=True)
class M1Result:
    positions: tuple[Position, ...]
    sector_weights: tuple[SectorCapitalWeight, ...]
    unclassified_weight: float
    top_sector_concentration: tuple[SectorCapitalWeight, ...]
    hhi: float
    effective_position_count: float


def renormalize(holdings: Sequence[HoldingInput]) -> tuple[Position, ...]:
    """w_i = mv_i / Σ mv (SPEC's M1 formula) already happened upstream of the pure
    analytics boundary — no dollar amounts reach this module. What lands here is
    whatever survived resolver/data-layer exclusions, which may no longer sum to 1;
    this restores that invariant over the survivors, per CLAUDE.md rule 3's boundary
    and the Metrics schema's Σ capital_weight == 1.0 requirement.
    """
    total = sum(h.weight for h in holdings)
    if total <= 0:
        raise ValueError("Cannot renormalize: total weight is zero or negative")
    return tuple(
        Position(h.ticker, h.weight / total, h.sector, h.is_etf) for h in holdings
    )


def compute_hhi(weights: Sequence[float]) -> float:
    return sum(w * w for w in weights)


def compute_effective_position_count(hhi: float) -> float:
    return 1.0 / hhi


def aggregate_sector_weights(
    positions: Sequence[Position],
) -> tuple[tuple[SectorCapitalWeight, ...], float]:
    totals: dict[GicsSector, float] = {}
    unclassified = 0.0
    for position in positions:
        if position.sector is None:
            unclassified += position.capital_weight
        else:
            prior = totals.get(position.sector, 0.0)
            totals[position.sector] = prior + position.capital_weight
    weights = tuple(
        SectorCapitalWeight(sector, weight) for sector, weight in totals.items()
    )
    return weights, unclassified


def top_sector_concentration(
    sector_weights: Sequence[SectorCapitalWeight], n: int = TOP_SECTOR_COUNT
) -> tuple[SectorCapitalWeight, ...]:
    ordered = sorted(sector_weights, key=lambda s: (-s.capital_weight, s.sector))
    return tuple(ordered[:n])


def compute_m1(holdings: Sequence[HoldingInput]) -> M1Result:
    positions = renormalize(holdings)
    sector_weights, unclassified = aggregate_sector_weights(positions)
    hhi = compute_hhi([p.capital_weight for p in positions])
    return M1Result(
        positions=positions,
        sector_weights=sector_weights,
        unclassified_weight=unclassified,
        top_sector_concentration=top_sector_concentration(sector_weights),
        hhi=hhi,
        effective_position_count=compute_effective_position_count(hhi),
    )
