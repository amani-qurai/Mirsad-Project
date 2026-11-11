"""The FastAPI application (M-001 scaffold).

Only the liveness probe lives here for now. Docker Compose and CI use it to
know the API process is up. It returns a token, never a sentence (NN-6).
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Mirsad API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
