from pathlib import Path

import pytest
from px.schemas.analyze import AnalyzeResponse

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "metrics.sample.json"


@pytest.fixture(scope="module")
def fixture_response() -> AnalyzeResponse:
    return AnalyzeResponse.model_validate_json(FIXTURE_PATH.read_text())


def test_fixture_exists():
    assert FIXTURE_PATH.is_file()


def test_fixture_validates_against_analyze_response_model(fixture_response):
    assert fixture_response.metrics.m1_weights.position_weights


def test_fixture_covers_excluded_holdings(fixture_response):
    assert len(fixture_response.metrics.excluded_holdings) >= 1


def test_fixture_covers_both_factor_significance_states(fixture_response):
    significances = {
        loading.significant for loading in fixture_response.metrics.m5_factor_tilts.loadings
    }
    assert significances == {True, False}


def test_fixture_covers_etf_overlap_and_look_through(fixture_response):
    look_through = fixture_response.metrics.m6_etf_look_through
    assert look_through.pairwise_overlap
    assert look_through.look_through_weights


def test_fixture_sector_exposure_spans_at_least_three_sectors(fixture_response):
    assert len(fixture_response.metrics.m1_weights.sector_exposure) >= 3


def test_fixture_top_sector_concentration_populated(fixture_response):
    assert len(fixture_response.metrics.m1_weights.top_sector_concentration) >= 1


def test_fixture_findings_between_three_and_six(fixture_response):
    assert 3 <= len(fixture_response.findings) <= 6


def test_fixture_capital_weights_sum_to_one(fixture_response):
    total = sum(
        p.capital_weight for p in fixture_response.metrics.m1_weights.position_weights
    )
    assert total == pytest.approx(1.0, abs=1e-6)


def test_fixture_risk_contributions_sum_to_one(fixture_response):
    total = sum(
        c.rc_pct for c in fixture_response.metrics.m3_risk_contribution.contributions
    )
    assert total == pytest.approx(1.0, abs=1e-6)
