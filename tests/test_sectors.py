from px.analytics.sectors import YAHOO_TO_GICS, map_to_gics_sector
from px.schemas.common import GicsSector

_GICS_SECTORS = set(GicsSector.__args__)


def test_every_yahoo_sector_maps_to_a_valid_gics_sector():
    assert set(YAHOO_TO_GICS.values()) <= _GICS_SECTORS


def test_known_yahoo_sector_maps_correctly():
    assert map_to_gics_sector("Technology") == "Information Technology"
    assert map_to_gics_sector("Consumer Cyclical") == "Consumer Discretionary"
    assert map_to_gics_sector("Financial Services") == "Financials"


def test_none_sector_maps_to_none():
    assert map_to_gics_sector(None) is None


def test_unrecognized_sector_maps_to_none_not_a_guess():
    assert map_to_gics_sector("Not A Real Sector") is None
