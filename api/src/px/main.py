from functools import lru_cache

import anthropic
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from px.extract.agent import ExtractionFailedError, extract_holdings
from px.schemas.extract import ExtractResponse

app = FastAPI(title="Portfolio X-Ray")

_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _sniff_media_type(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


@lru_cache
def get_anthropic_client() -> anthropic.Anthropic:
    """Constructed lazily, once per process, so importing this module never requires
    ANTHROPIC_API_KEY to be set (tests override this dependency and never call it)."""
    return anthropic.Anthropic()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/extract", response_model=ExtractResponse)
async def extract(
    image: UploadFile = File(...),
    client: anthropic.Anthropic = Depends(get_anthropic_client),
) -> ExtractResponse:
    data = await image.read(_MAX_UPLOAD_BYTES + 1)
    if len(data) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the size limit.")

    media_type = _sniff_media_type(data)
    if media_type is None:
        raise HTTPException(
            status_code=400, detail="Not a recognized image (PNG/JPEG/WEBP)."
        )

    try:
        return extract_holdings(data, media_type, client=client)
    except ExtractionFailedError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except anthropic.APIError as exc:
        raise HTTPException(
            status_code=502, detail="Extraction service unavailable."
        ) from exc
