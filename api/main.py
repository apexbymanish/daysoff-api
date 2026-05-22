"""FastAPI entrypoint for daysoff-api.

The HTTP surface wraps the existing CLI modules — see api/services.py.
Endpoints are stateless and read-only. No auth in v1.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


API_VERSION = "1.0.0"

app = FastAPI(
    title="daysoff-api",
    version=API_VERSION,
    description="Read-only public API for holidays, comparisons, and sandwich-day detection.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/v1/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "version": API_VERSION}
