from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PXBaseModel(BaseModel):
    """Base for every model in the frozen contract; fails closed on unknown fields."""

    model_config = ConfigDict(extra="forbid")


GicsSector = Literal[
    "Energy",
    "Materials",
    "Industrials",
    "Consumer Discretionary",
    "Consumer Staples",
    "Health Care",
    "Financials",
    "Information Technology",
    "Communication Services",
    "Utilities",
    "Real Estate",
]


class Severity(StrEnum):
    INFO = "info"
    NOTABLE = "notable"
