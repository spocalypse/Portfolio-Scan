from datetime import date, datetime

from pydantic import Field

from px.schemas.common import PXBaseModel, Severity
from px.schemas.metrics import Metrics


class Holding(PXBaseModel):
    """The weight-only boundary (SPEC §6.2): exactly these two fields, nothing else."""

    ticker: str
    weight: float = Field(ge=0, le=1)


class AnalyzeRequest(PXBaseModel):
    holdings: list[Holding]


class Finding(PXBaseModel):
    headline: str
    explanation: str
    severity: Severity
    metrics_referenced: list[str]


class Meta(PXBaseModel):
    request_id: str
    computed_at: datetime
    data_window_days: int = Field(gt=0)
    price_data_as_of: date
    price_data_stale: bool = False
    narrative_model_used: str
    warnings: list[str] = []


class AnalyzeResponse(PXBaseModel):
    metrics: Metrics
    findings: list[Finding] = Field(min_length=3, max_length=6)
    meta: Meta
