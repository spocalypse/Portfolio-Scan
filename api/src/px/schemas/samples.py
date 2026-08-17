from px.schemas.analyze import Holding
from px.schemas.common import PXBaseModel


class SamplePortfolio(PXBaseModel):
    id: str
    name: str
    description: str | None
    holdings: list[Holding]


class SamplesResponse(PXBaseModel):
    samples: list[SamplePortfolio]
