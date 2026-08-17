"""Structural proof that /api/analyze cannot carry a currency value (SPEC §6.2).

This is a narrow, model-level guardrail — issue #9 owns the full D9 suite (a live
`pytest -m privacy` run plus a grep of logs for dollar figures). This file only proves
the schema itself cannot hold one.
"""

import typing

import pytest
from px.schemas.analyze import AnalyzeRequest, AnalyzeResponse, Finding, Holding, Meta
from px.schemas.common import PXBaseModel
from px.schemas.extract import ExtractResponse, ExtractRow
from px.schemas.metrics import Metrics
from pydantic import BaseModel, ValidationError

pytestmark = pytest.mark.privacy

# "price" is deliberately excluded: Meta.price_data_as_of / price_data_stale describe
# price-data provenance, not a currency amount held by the contract.
_BANNED_TOKENS = {"value", "amount", "dollar", "balance", "cost", "usd"}


def _iter_annotation_models(annotation: object) -> typing.Iterator[type[BaseModel]]:
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        yield annotation
        return
    for arg in typing.get_args(annotation):
        yield from _iter_annotation_models(arg)


def _reachable_models(root: type[BaseModel]) -> set[type[BaseModel]]:
    seen: set[type[BaseModel]] = set()
    stack = [root]
    while stack:
        model = stack.pop()
        if model in seen:
            continue
        seen.add(model)
        for field in model.model_fields.values():
            for nested in _iter_annotation_models(field.annotation):
                if nested not in seen:
                    stack.append(nested)
    return seen


def test_holding_has_exactly_ticker_and_weight():
    assert set(Holding.model_fields) == {"ticker", "weight"}


def test_analyze_request_has_only_holdings():
    assert set(AnalyzeRequest.model_fields) == {"holdings"}


def test_holding_rejects_a_smuggled_currency_field():
    with pytest.raises(ValidationError):
        Holding.model_validate({"ticker": "AAPL", "weight": 0.1, "market_value": 5000})


@pytest.mark.parametrize("root", [AnalyzeRequest, Metrics, Finding, Meta, AnalyzeResponse])
def test_every_reachable_model_forbids_extra_fields(root):
    for model in _reachable_models(root):
        assert issubclass(model, PXBaseModel), f"{model.__name__} does not inherit PXBaseModel"
        assert model.model_config.get("extra") == "forbid"


@pytest.mark.parametrize("root", [AnalyzeRequest, Metrics, Finding, Meta, AnalyzeResponse])
def test_no_reachable_field_name_suggests_currency(root):
    offenders = []
    for model in _reachable_models(root):
        for field_name in model.model_fields:
            tokens = set(field_name.lower().split("_"))
            if tokens & _BANNED_TOKENS:
                offenders.append(f"{model.__name__}.{field_name}")
    assert not offenders, f"currency-smelling field(s) downstream of the boundary: {offenders}"


@pytest.mark.parametrize("root", [AnalyzeRequest, Metrics, Finding, Meta, AnalyzeResponse])
def test_extraction_side_models_are_unreachable_from_analyze_side(root):
    reachable = _reachable_models(root)
    assert ExtractRow not in reachable
    assert ExtractResponse not in reachable
