from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from px.schemas.common import GicsSector, PXBaseModel

_TOL = 1e-6

FactorName = Literal["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]
_ALL_FACTORS: frozenset[FactorName] = frozenset(
    {"mkt_rf", "smb", "hml", "rmw", "cma", "mom"}
)


def _isclose(a: float, b: float, tol: float = _TOL) -> bool:
    return abs(a - b) <= tol


# --- M1: weights and sector exposure ---


class PositionWeight(PXBaseModel):
    ticker: str
    sector: GicsSector
    capital_weight: float = Field(ge=0, le=1)


class SectorExposure(PXBaseModel):
    sector: GicsSector
    capital_weight: float = Field(ge=0, le=1)
    risk_contribution_pct: float


class TopSectorConcentration(PXBaseModel):
    sector: GicsSector
    capital_weight: float = Field(ge=0, le=1)


class M1Weights(PXBaseModel):
    position_weights: list[PositionWeight]
    sector_exposure: list[SectorExposure]
    top_sector_concentration: list[TopSectorConcentration]
    hhi: float = Field(ge=0, le=1)
    effective_position_count: float = Field(ge=1)

    @model_validator(mode="after")
    def _check_invariants(self) -> "M1Weights":
        capital_sum = sum(p.capital_weight for p in self.position_weights)
        if not _isclose(capital_sum, 1.0):
            raise ValueError(
                f"Σ position_weights.capital_weight = {capital_sum}, want 1.0"
            )

        sector_capital_sum = sum(s.capital_weight for s in self.sector_exposure)
        if not _isclose(sector_capital_sum, 1.0):
            raise ValueError(
                f"Σ sector_exposure.capital_weight = {sector_capital_sum}, want 1.0"
            )

        sector_rc_sum = sum(s.risk_contribution_pct for s in self.sector_exposure)
        if not _isclose(sector_rc_sum, 1.0):
            raise ValueError(
                f"Σ sector_exposure.risk_contribution_pct = {sector_rc_sum}, want 1.0"
            )

        expected_epc = 1.0 / self.hhi
        if not _isclose(self.effective_position_count, expected_epc, tol=1e-3):
            raise ValueError(
                f"effective_position_count = {self.effective_position_count}, "
                f"want 1/hhi = {expected_epc}"
            )
        return self


# --- M2: portfolio beta ---


class M2Beta(PXBaseModel):
    beta: float
    r_squared: float = Field(ge=0, le=1)


# --- M3: risk contribution (headline metric) ---


class RiskContribution(PXBaseModel):
    ticker: str
    weight: float = Field(ge=0, le=1)
    mcr: float
    rc: float
    rc_pct: float


class M3RiskContribution(PXBaseModel):
    portfolio_volatility: float = Field(ge=0)
    contributions: list[RiskContribution]

    @model_validator(mode="after")
    def _check_rc_sums_to_one(self) -> "M3RiskContribution":
        rc_sum = sum(c.rc_pct for c in self.contributions)
        if not _isclose(rc_sum, 1.0):
            raise ValueError(f"Σ contributions.rc_pct = {rc_sum}, want 1.0")
        return self


# --- M4: effective number of bets ---


class M4EffectiveBets(PXBaseModel):
    effective_number_of_bets: float = Field(ge=1)
    naive_position_count: int = Field(ge=1)


# --- M5: factor tilts ---


class FactorLoading(PXBaseModel):
    factor: FactorName
    loading: float
    t_stat: float
    significant: bool

    @model_validator(mode="after")
    def _check_significance_matches_t_stat(self) -> "FactorLoading":
        expected = abs(self.t_stat) >= 2
        if self.significant != expected:
            raise ValueError(
                f"significant={self.significant} but |t_stat|={abs(self.t_stat)} "
                f"implies {expected}"
            )
        return self


class M5FactorTilts(PXBaseModel):
    loadings: list[FactorLoading]
    r_squared: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def _check_all_six_factors_present_once(self) -> "M5FactorTilts":
        factors = [loading.factor for loading in self.loadings]
        if set(factors) != _ALL_FACTORS or len(factors) != len(_ALL_FACTORS):
            raise ValueError(
                f"loadings must cover exactly {sorted(_ALL_FACTORS)} once each, "
                f"got {factors}"
            )
        return self


# --- M6: ETF look-through overlap ---


class EtfOverlapPair(PXBaseModel):
    etf_a: str
    etf_b: str
    overlap_pct: float = Field(ge=0, le=1)


class LookThroughHolding(PXBaseModel):
    ticker: str
    true_weight: float = Field(ge=0, le=1)


class M6EtfLookThrough(PXBaseModel):
    snapshot_date: date
    etfs_detected: list[str]
    pairwise_overlap: list[EtfOverlapPair]
    look_through_weights: list[LookThroughHolding]


# --- Also computed: excluded holdings ---


class ExcludedHolding(PXBaseModel):
    ticker: str
    reason: Literal["non_us_ticker", "insufficient_price_history", "resolution_failure"]
    detail: str | None = None


# --- The full metrics object ---


class Metrics(PXBaseModel):
    m1_weights: M1Weights
    m2_beta: M2Beta
    m3_risk_contribution: M3RiskContribution
    m4_effective_bets: M4EffectiveBets
    m5_factor_tilts: M5FactorTilts
    m6_etf_look_through: M6EtfLookThrough
    excluded_holdings: list[ExcludedHolding]

    @model_validator(mode="after")
    def _check_naive_count_matches_positions(self) -> "Metrics":
        expected = len(self.m1_weights.position_weights)
        actual = self.m4_effective_bets.naive_position_count
        if actual != expected:
            raise ValueError(
                f"m4_effective_bets.naive_position_count = {actual}, "
                f"want len(m1_weights.position_weights) = {expected}"
            )
        return self
