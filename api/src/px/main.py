from fastapi import FastAPI

app = FastAPI(title="Portfolio X-Ray")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
