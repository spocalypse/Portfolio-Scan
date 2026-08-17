"""The raw tool-call parse target for A1. Not part of the frozen API contract in
px/schemas/ — this is the pre-model_used shape the LLM is allowed to produce; agent.py
attaches model_used itself rather than trusting the model to self-report its identity.
"""

from px.schemas.common import PXBaseModel
from px.schemas.extract import ExtractRow


class ExtractionPayload(PXBaseModel):
    """Mirrors ExtractResponse minus model_used — ExtractRow has no model-identity
    field, so it's reused as-is; only the response envelope adds model_used, which
    this payload deliberately cannot hold.
    """

    rows: list[ExtractRow]
    total_value: float | None
    brokerage_guess: str | None
    warnings: list[str] = []


EXTRACTION_TOOL = {
    "name": "emit_holdings_extraction",
    "description": (
        "Emit the holdings structure transcribed from the screenshot. Call this "
        "exactly once with your complete result."
    ),
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "rows": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "raw_label": {"type": "string"},
                        "ticker_guess": {"type": ["string", "null"]},
                        "quantity": {"type": ["number", "null"]},
                        "market_value": {"type": ["number", "null"]},
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                        },
                    },
                    "required": [
                        "raw_label",
                        "ticker_guess",
                        "quantity",
                        "market_value",
                        "confidence",
                    ],
                },
            },
            "total_value": {"type": ["number", "null"]},
            "brokerage_guess": {"type": ["string", "null"]},
            "warnings": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["rows", "total_value", "brokerage_guess", "warnings"],
    },
}
