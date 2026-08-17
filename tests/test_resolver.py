from px.resolve.resolver import resolve_holdings
from px.resolve.table import SymbolEntry
from px.schemas.analyze import Holding


def _table(*entries: SymbolEntry) -> dict[str, SymbolEntry]:
    return {entry.ticker: entry for entry in entries}


_AAPL = SymbolEntry("AAPL", "Apple Inc.", "NASDAQ", is_etf=False)
_SPY = SymbolEntry("SPY", "SPDR S&P 500 ETF Trust", "NYSE Arca", is_etf=True)


def test_exact_match_resolves():
    table = _table(_AAPL)
    result = resolve_holdings([Holding(ticker="AAPL", weight=1.0)], table)

    assert result.excluded == ()
    assert result.resolved[0].ticker == "AAPL"
    assert result.resolved[0].weight == 1.0
    assert result.resolved[0].is_etf is False
    assert result.resolved[0].exchange == "NASDAQ"


def test_etf_flag_passes_through():
    table = _table(_SPY)
    result = resolve_holdings([Holding(ticker="SPY", weight=1.0)], table)

    assert result.resolved[0].is_etf is True


def test_case_and_whitespace_are_normalized():
    table = _table(_AAPL)
    result = resolve_holdings([Holding(ticker=" aapl ", weight=1.0)], table)

    assert result.resolved[0].ticker == "AAPL"


def test_weight_is_never_renormalized():
    table = _table(_AAPL)
    result = resolve_holdings([Holding(ticker="AAPL", weight=0.37)], table)

    assert result.resolved[0].weight == 0.37


def test_not_found_ticker_is_excluded_and_reported_by_name():
    table = _table(_AAPL)
    result = resolve_holdings([Holding(ticker="ZZZNOPE", weight=1.0)], table)

    assert result.resolved == ()
    assert result.excluded[0].raw_ticker == "ZZZNOPE"
    assert result.excluded[0].reason == "not_found"
    assert result.excluded[0].weight == 1.0


def test_non_us_suffix_is_excluded_with_its_own_reason():
    table = _table(_AAPL)
    result = resolve_holdings([Holding(ticker="SHOP.TO", weight=1.0)], table)

    assert result.excluded[0].reason == "non_us_suffix"


def test_share_class_separator_variant_resolves():
    # Table stores the dot form; a brokerage rendering it with a hyphen should still
    # resolve, never be treated as a different security.
    table = _table(SymbolEntry("BRK.B", "Berkshire Hathaway Inc.", "NYSE", is_etf=False))
    result = resolve_holdings([Holding(ticker="BRK-B", weight=1.0)], table)

    assert result.resolved[0].ticker == "BRK.B"
    assert result.excluded == ()


def test_bare_base_ambiguous_between_two_share_classes():
    table = _table(
        SymbolEntry("BRK.A", "Berkshire Hathaway Inc.", "NYSE", is_etf=False),
        SymbolEntry("BRK.B", "Berkshire Hathaway Inc.", "NYSE", is_etf=False),
    )
    result = resolve_holdings([Holding(ticker="BRK", weight=1.0)], table)

    assert result.resolved == ()
    assert result.excluded[0].reason == "ambiguous"
    assert result.excluded[0].candidates == ("BRK.A", "BRK.B")


def test_three_way_ambiguity_lists_all_candidates_sorted():
    table = _table(
        SymbolEntry("XYZ.A", "Example Corp", "NYSE", is_etf=False),
        SymbolEntry("XYZ.B", "Example Corp", "NYSE", is_etf=False),
        SymbolEntry("XYZ.C", "Example Corp", "NYSE", is_etf=False),
    )
    result = resolve_holdings([Holding(ticker="XYZ", weight=1.0)], table)

    assert result.excluded[0].reason == "ambiguous"
    assert result.excluded[0].candidates == ("XYZ.A", "XYZ.B", "XYZ.C")


def test_exact_match_short_circuits_even_when_variants_would_collide():
    # GOOG is a real, standalone ticker distinct from GOOGL — an exact hit must win
    # outright and never fall into share-class variant scanning.
    table = _table(
        SymbolEntry("GOOG", "Alphabet Inc. Class C", "NASDAQ", is_etf=False),
        SymbolEntry("GOOG.A", "Decoy same-base entry", "NASDAQ", is_etf=False),
        SymbolEntry("GOOG.B", "Decoy same-base entry", "NASDAQ", is_etf=False),
    )
    result = resolve_holdings([Holding(ticker="GOOG", weight=1.0)], table)

    assert result.excluded == ()
    assert result.resolved[0].ticker == "GOOG"


def test_google_and_alphabet_share_classes_never_cross_match():
    table = _table(
        SymbolEntry("GOOG", "Alphabet Inc. Class C", "NASDAQ", is_etf=False),
        SymbolEntry("GOOGL", "Alphabet Inc. Class A", "NASDAQ", is_etf=False),
    )

    goog_result = resolve_holdings([Holding(ticker="GOOG", weight=1.0)], table)
    googl_result = resolve_holdings([Holding(ticker="GOOGL", weight=1.0)], table)

    assert goog_result.resolved[0].ticker == "GOOG"
    assert googl_result.resolved[0].ticker == "GOOGL"


def test_mixed_batch_partitions_resolved_and_excluded_in_order():
    table = _table(_AAPL, _SPY)
    holdings = [
        Holding(ticker="AAPL", weight=0.5),
        Holding(ticker="NOPE", weight=0.3),
        Holding(ticker="SPY", weight=0.2),
    ]

    result = resolve_holdings(holdings, table)

    assert [r.ticker for r in result.resolved] == ["AAPL", "SPY"]
    assert [e.raw_ticker for e in result.excluded] == ["NOPE"]
