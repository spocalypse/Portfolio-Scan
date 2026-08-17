"""Generates fixtures/metrics.sample.json from a validated AnalyzeResponse instance.

Run manually (`python3.11 scripts/build_metrics_fixture.py`) to regenerate the frozen
fixture. Never run as part of `make test` or `make lint` — regenerating the contract
is a deliberate, logged action, not a side effect.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from px.schemas import (
    AnalyzeResponse,
    EtfOverlapPair,
    ExcludedHolding,
    FactorLoading,
    Finding,
    LookThroughHolding,
    M1Weights,
    M2Beta,
    M3RiskContribution,
    M4EffectiveBets,
    M5FactorTilts,
    M6EtfLookThrough,
    Meta,
    Metrics,
    PositionWeight,
    RiskContribution,
    SectorExposure,
    Severity,
    TopSectorConcentration,
)

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "metrics.sample.json"

# ticker -> (sector, capital_weight, risk_contribution_pct)
_POSITIONS: dict[str, tuple[str, float, float]] = {
    "AAPL": ("Information Technology", 0.13, 0.16),
    "MSFT": ("Information Technology", 0.13, 0.16),
    "NVDA": ("Information Technology", 0.09, 0.14),
    "QQQ": ("Information Technology", 0.11, 0.13),
    "VOO": ("Information Technology", 0.10, 0.09),
    "AMZN": ("Consumer Discretionary", 0.11, 0.12),
    "JPM": ("Financials", 0.09, 0.08),
    "JNJ": ("Health Care", 0.07, 0.04),
    "XOM": ("Energy", 0.07, 0.03),
    "PG": ("Consumer Staples", 0.10, 0.05),
}

_PORTFOLIO_VOLATILITY = 0.18


def _build_m1() -> M1Weights:
    position_weights = [
        PositionWeight(ticker=ticker, sector=sector, capital_weight=capital_weight)
        for ticker, (sector, capital_weight, _) in _POSITIONS.items()
    ]

    sector_capital: dict[str, float] = {}
    sector_rc: dict[str, float] = {}
    for sector, capital_weight, rc_pct in _POSITIONS.values():
        sector_capital[sector] = sector_capital.get(sector, 0.0) + capital_weight
        sector_rc[sector] = sector_rc.get(sector, 0.0) + rc_pct

    sector_exposure = [
        SectorExposure(
            sector=sector,
            capital_weight=round(sector_capital[sector], 10),
            risk_contribution_pct=round(sector_rc[sector], 10),
        )
        for sector in sector_capital
    ]

    top_3 = sorted(sector_exposure, key=lambda s: s.capital_weight, reverse=True)[:3]
    top_sector_concentration = [
        TopSectorConcentration(sector=s.sector, capital_weight=s.capital_weight) for s in top_3
    ]

    hhi = sum(capital_weight**2 for _, capital_weight, _ in _POSITIONS.values())

    return M1Weights(
        position_weights=position_weights,
        sector_exposure=sector_exposure,
        top_sector_concentration=top_sector_concentration,
        hhi=hhi,
        effective_position_count=1.0 / hhi,
    )


def _build_m3() -> M3RiskContribution:
    contributions = []
    for ticker, (_, capital_weight, rc_pct) in _POSITIONS.items():
        rc = rc_pct * _PORTFOLIO_VOLATILITY
        contributions.append(
            RiskContribution(
                ticker=ticker,
                weight=capital_weight,
                mcr=rc / capital_weight,
                rc=rc,
                rc_pct=rc_pct,
            )
        )
    return M3RiskContribution(
        portfolio_volatility=_PORTFOLIO_VOLATILITY,
        contributions=contributions,
    )


def _build_m5() -> M5FactorTilts:
    loadings = [
        FactorLoading(factor="mkt_rf", loading=1.15, t_stat=14.2, significant=True),
        FactorLoading(factor="smb", loading=-0.08, t_stat=-0.9, significant=False),
        FactorLoading(factor="hml", loading=-0.22, t_stat=-2.4, significant=True),
        FactorLoading(factor="rmw", loading=0.05, t_stat=0.6, significant=False),
        FactorLoading(factor="cma", loading=-0.15, t_stat=-1.8, significant=False),
        FactorLoading(factor="mom", loading=0.10, t_stat=1.1, significant=False),
    ]
    return M5FactorTilts(loadings=loadings, r_squared=0.78)


def _build_m6() -> M6EtfLookThrough:
    return M6EtfLookThrough(
        snapshot_date=date(2026, 7, 1),
        etfs_detected=["QQQ", "VOO"],
        pairwise_overlap=[EtfOverlapPair(etf_a="QQQ", etf_b="VOO", overlap_pct=0.22)],
        look_through_weights=[
            LookThroughHolding(ticker="AAPL", true_weight=0.1502),
            LookThroughHolding(ticker="MSFT", true_weight=0.1475),
            LookThroughHolding(ticker="NVDA", true_weight=0.1059),
        ],
    )


def build() -> AnalyzeResponse:
    m1 = _build_m1()
    metrics = Metrics(
        m1_weights=m1,
        m2_beta=M2Beta(beta=1.15, r_squared=0.87),
        m3_risk_contribution=_build_m3(),
        m4_effective_bets=M4EffectiveBets(
            effective_number_of_bets=5.8,
            naive_position_count=len(m1.position_weights),
        ),
        m5_factor_tilts=_build_m5(),
        m6_etf_look_through=_build_m6(),
        excluded_holdings=[
            ExcludedHolding(
                ticker="NEWCO",
                reason="insufficient_price_history",
                detail="IPO'd 30 days ago; fewer than 250 trading days of price history.",
            )
        ],
    )

    findings = [
        Finding(
            headline="Technology carries more portfolio risk than its dollar weight suggests",
            explanation=(
                "Technology positions account for 56% of capital but 68% of portfolio "
                "risk, driven by correlated moves among AAPL, MSFT, NVDA, and the two "
                "index funds."
            ),
            severity=Severity.NOTABLE,
            metrics_referenced=["m1_weights.sector_exposure", "m3_risk_contribution.contributions"],
        ),
        Finding(
            headline="Portfolio beta sits at 1.15 with a high R-squared",
            explanation=(
                "Over the trailing three years the portfolio moved 1.15x the market on "
                "average, and 87% of that movement is explained by the market alone."
            ),
            severity=Severity.INFO,
            metrics_referenced=["m2_beta.beta", "m2_beta.r_squared"],
        ),
        Finding(
            headline="5.8 effective bets despite 10 holdings",
            explanation=(
                "The effective number of bets is 5.8 versus 10 raw positions, reflecting "
                "how correlated the technology names are with each other."
            ),
            severity=Severity.NOTABLE,
            metrics_referenced=[
                "m4_effective_bets.effective_number_of_bets",
                "m4_effective_bets.naive_position_count",
            ],
        ),
        Finding(
            headline="Market and value loadings are significant; momentum is not",
            explanation=(
                "The market and value (HML) loadings clear the significance bar; the "
                "momentum, size, profitability, and investment loadings do not and should "
                "be read as noise, not tilts."
            ),
            severity=Severity.INFO,
            metrics_referenced=["m5_factor_tilts.loadings"],
        ),
        Finding(
            headline="One holding excluded for insufficient price history",
            explanation=(
                "NEWCO was excluded from covariance-based metrics because it has fewer "
                "than 250 trading days of price history."
            ),
            severity=Severity.NOTABLE,
            metrics_referenced=["excluded_holdings"],
        ),
    ]

    meta = Meta(
        request_id="fixture-0001",
        computed_at=datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc),
        data_window_days=756,
        price_data_as_of=date(2026, 8, 15),
        price_data_stale=False,
        narrative_model_used="claude-sonnet-5",
        warnings=[],
    )

    return AnalyzeResponse(metrics=metrics, findings=findings, meta=meta)


def main() -> None:
    response = build()
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(response.model_dump_json(indent=2) + "\n")
    print(f"Wrote {FIXTURE_PATH}")


if __name__ == "__main__":
    main()
