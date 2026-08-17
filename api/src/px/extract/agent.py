"""A1 — Extraction Agent (SPEC §5.2).

Haiku first; escalate to Sonnet only on self-reported confidence < 0.8 or schema
validation failure. The LLM never does arithmetic here either: it transcribes
structure, and every downstream decision (escalate or not, which model_used to
stamp) is deterministic Python, not something asked of the model.
"""

from __future__ import annotations

import base64
import logging
import time
import uuid

from pydantic import ValidationError

from px.extract.payload import EXTRACTION_TOOL, ExtractionPayload
from px.extract.prompts.a1_extraction import A1_SYSTEM_PROMPT
from px.schemas.extract import ExtractResponse

logger = logging.getLogger("px.extract")

MODEL_HAIKU = "claude-haiku-4-5-20251001"
MODEL_SONNET = "claude-sonnet-5"
CONFIDENCE_ESCALATION_THRESHOLD = 0.8
_MAX_TOKENS = 4096


class ExtractionFailedError(Exception):
    """Neither Haiku nor Sonnet produced a schema-valid extraction. No fallback
    fabrication."""


class _ModelOutputInvalid(Exception):
    """Internal: the model's tool call was missing or failed schema validation."""


def _min_confidence(payload: ExtractionPayload) -> float | None:
    if not payload.rows:
        return None
    return min(row.confidence for row in payload.rows)


def _call_model(
    client, model: str, image_b64: str, media_type: str
) -> ExtractionPayload:
    response = client.messages.create(
        model=model,
        max_tokens=_MAX_TOKENS,
        system=A1_SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": EXTRACTION_TOOL["name"]},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Extract the holdings from this screenshot.",
                    },
                ],
            }
        ],
    )

    tool_use = next(
        (
            block
            for block in response.content
            if getattr(block, "type", None) == "tool_use"
        ),
        None,
    )
    if tool_use is None:
        raise _ModelOutputInvalid(f"{model} did not call {EXTRACTION_TOOL['name']}")
    try:
        return ExtractionPayload.model_validate(tool_use.input)
    except ValidationError as exc:
        raise _ModelOutputInvalid(
            f"{model} tool input failed schema validation"
        ) from exc


def extract_holdings(
    image_bytes: bytes,
    media_type: str,
    *,
    client,
    request_id: str | None = None,
) -> ExtractResponse:
    request_id = request_id or str(uuid.uuid4())
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    started = time.monotonic()

    model_used: str | None = None
    payload: ExtractionPayload | None = None
    error_code: str | None = None

    try:
        haiku_payload = _call_model(client, MODEL_HAIKU, image_b64, media_type)
    except _ModelOutputInvalid:
        haiku_payload = None

    if haiku_payload is not None and (
        (confidence := _min_confidence(haiku_payload)) is None
        or confidence >= CONFIDENCE_ESCALATION_THRESHOLD
    ):
        payload, model_used = haiku_payload, MODEL_HAIKU
    else:
        try:
            sonnet_payload = _call_model(client, MODEL_SONNET, image_b64, media_type)
        except _ModelOutputInvalid:
            sonnet_payload = None

        if sonnet_payload is not None:
            payload, model_used = sonnet_payload, MODEL_SONNET
        else:
            error_code = "extraction_schema_failure"

    duration_ms = round((time.monotonic() - started) * 1000, 1)
    logger.info(
        "extraction_request",
        extra={
            "request_id": request_id,
            "duration_ms": duration_ms,
            "model_used": model_used,
            "row_count": len(payload.rows) if payload is not None else 0,
            "error_code": error_code,
        },
    )

    if payload is None or model_used is None:
        raise ExtractionFailedError(
            "Neither Haiku nor Sonnet produced a schema-valid extraction."
        )

    return ExtractResponse(
        rows=payload.rows,
        total_value=payload.total_value,
        brokerage_guess=payload.brokerage_guess,
        warnings=payload.warnings,
        model_used=model_used,
    )
