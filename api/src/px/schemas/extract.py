from pydantic import Field

from px.schemas.common import PXBaseModel


class ExtractRow(PXBaseModel):
    raw_label: str
    ticker_guess: str | None
    quantity: float | None
    market_value: float | None
    confidence: float = Field(ge=0, le=1)


class ExtractResponse(PXBaseModel):
    rows: list[ExtractRow]
    total_value: float | None
    brokerage_guess: str | None
    warnings: list[str] = []
    model_used: str
