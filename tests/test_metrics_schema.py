import pytest
from px.schemas.metrics import (
    EtfOverlapPair,
    ExcludedHolding,
    FactorLoading,
    LookThroughHolding,
    M1Weights,
    M2Beta,
    M3RiskContribution,
    M4EffectiveBets,
    M5FactorTilts,
    M6EtfLookThrough,
    Metrics,
    PositionWeight,
    RiskContribution,
    SectorExposure,
    TopSectorConcentration,
)
from pydantic import ValidationError

_ALL_SIX_LOADINGS = [
    FactorLoading(factor="mkt_rf", loading=1.0, t_stat=10.0, significant=True),
    FactorLoading(factor="smb", loading=0.0, t_stat=0.5, significant=False),
    FactorLoading(factor="hml", loading=0.0, t_stat=0.5, significant=False),
    FactorLoading(factor="rmw", loading=0.0, t_stat=0.5, significant=False),
    FactorLoading(factor="cma", loading=0.0, t_stat=0.5, significant=False),
    FactorLoading(factor="mom", loading=0.0, t_stat=0.5, significant=False),
]


def _valid_m1() -> M1Weights:
    hhi = 0.5**2 + 0.5**2
    return M1Weights(
        position_weights=[
            PositionWeight(ticker="AAPL", sector="Information Technology", capital_weight=0.5),
            PositionWeight(ticker="JNJ", sector="Health Care", capital_weight=0.5),
        ],
        sector_exposure=[
            SectorExposure(
                sector="Information Technology", capital_weight=0.5, risk_contribution_pct=0.6
            ),
            SectorExposure(sector="Health Care", capital_weight=0.5, risk_contribution_pct=0.4),
        ],
        top_sector_concentration=[
            TopSectorConcentration(sector="Information Technology", capital_weight=0.5),
            TopSectorConcentration(sector="Health Care", capital_weight=0.5),
        ],
        hhi=hhi,
        effective_position_count=1.0 / hhi,
    )


def test_m1_weights_valid_instance_constructs():
    m1 = _valid_m1()
    assert m1.hhi == pytest.approx(0.5)


def test_m1_rejects_position_weights_not_summing_to_one():
    with pytest.raises(ValidationError):
        M1Weights(
            position_weights=[
                PositionWeight(ticker="AAPL", sector="Information Technology", capital_weight=0.4),
                PositionWeight(ticker="JNJ", sector="Health Care", capital_weight=0.5),
            ],
            sector_exposure=[
                SectorExposure(
                    sector="Information Technology", capital_weight=0.4, risk_contribution_pct=0.6
                ),
                SectorExposure(sector="Health Care", capital_weight=0.6, risk_contribution_pct=0.4),
            ],
            top_sector_concentration=[
                TopSectorConcentration(sector="Information Technology", capital_weight=0.4),
            ],
            hhi=0.32,
            effective_position_count=1.0 / 0.32,
        )


def test_m1_rejects_effective_position_count_not_matching_hhi():
    valid = _valid_m1()
    with pytest.raises(ValidationError):
        M1Weights(
            position_weights=valid.position_weights,
            sector_exposure=valid.sector_exposure,
            top_sector_concentration=valid.top_sector_concentration,
            hhi=valid.hhi,
            effective_position_count=999.0,
        )


def _valid_m3() -> M3RiskContribution:
    return M3RiskContribution(
        portfolio_volatility=0.18,
        contributions=[
            RiskContribution(ticker="AAPL", weight=0.5, mcr=0.2, rc=0.1, rc_pct=0.6),
            RiskContribution(ticker="JNJ", weight=0.5, mcr=0.08, rc=0.04, rc_pct=0.4),
        ],
    )


def test_m3_valid_instance_constructs():
    assert _valid_m3().portfolio_volatility == 0.18


def test_m3_rejects_rc_pct_not_summing_to_one():
    with pytest.raises(ValidationError):
        M3RiskContribution(
            portfolio_volatility=0.18,
            contributions=[
                RiskContribution(ticker="AAPL", weight=0.5, mcr=0.2, rc=0.1, rc_pct=0.6),
                RiskContribution(ticker="JNJ", weight=0.5, mcr=0.08, rc=0.04, rc_pct=0.2),
            ],
        )


def test_factor_loading_rejects_significant_mismatch():
    with pytest.raises(ValidationError):
        FactorLoading(factor="mkt_rf", loading=1.0, t_stat=3.0, significant=False)
    with pytest.raises(ValidationError):
        FactorLoading(factor="mom", loading=0.1, t_stat=0.5, significant=True)


def test_m5_valid_with_all_six_factors_once():
    tilts = M5FactorTilts(loadings=_ALL_SIX_LOADINGS, r_squared=0.7)
    assert len(tilts.loadings) == 6


def test_m5_rejects_missing_factor():
    with pytest.raises(ValidationError):
        M5FactorTilts(loadings=_ALL_SIX_LOADINGS[:-1], r_squared=0.7)


def test_m5_rejects_duplicate_factor():
    with pytest.raises(ValidationError):
        M5FactorTilts(loadings=_ALL_SIX_LOADINGS + [_ALL_SIX_LOADINGS[0]], r_squared=0.7)


def _valid_metrics() -> Metrics:
    m1 = _valid_m1()
    return Metrics(
        m1_weights=m1,
        m2_beta=M2Beta(beta=1.0, r_squared=0.9),
        m3_risk_contribution=_valid_m3(),
        m4_effective_bets=M4EffectiveBets(
            effective_number_of_bets=1.8, naive_position_count=len(m1.position_weights)
        ),
        m5_factor_tilts=M5FactorTilts(loadings=_ALL_SIX_LOADINGS, r_squared=0.7),
        m6_etf_look_through=M6EtfLookThrough(
            snapshot_date="2026-07-01",
            etfs_detected=[],
            pairwise_overlap=[EtfOverlapPair(etf_a="QQQ", etf_b="VOO", overlap_pct=0.2)],
            look_through_weights=[LookThroughHolding(ticker="AAPL", true_weight=0.2)],
        ),
        excluded_holdings=[
            ExcludedHolding(ticker="NEWCO", reason="insufficient_price_history", detail=None)
        ],
    )


def test_metrics_valid_instance_constructs():
    metrics = _valid_metrics()
    assert metrics.m4_effective_bets.naive_position_count == 2


def test_metrics_rejects_naive_count_not_matching_position_count():
    m1 = _valid_m1()
    with pytest.raises(ValidationError):
        Metrics(
            m1_weights=m1,
            m2_beta=M2Beta(beta=1.0, r_squared=0.9),
            m3_risk_contribution=_valid_m3(),
            m4_effective_bets=M4EffectiveBets(effective_number_of_bets=1.8, naive_position_count=99),
            m5_factor_tilts=M5FactorTilts(loadings=_ALL_SIX_LOADINGS, r_squared=0.7),
            m6_etf_look_through=M6EtfLookThrough(
                snapshot_date="2026-07-01",
                etfs_detected=[],
                pairwise_overlap=[],
                look_through_weights=[],
            ),
            excluded_holdings=[],
        )
