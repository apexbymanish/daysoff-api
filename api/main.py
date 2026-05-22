"""FastAPI entrypoint for daysoff-api.

The HTTP surface wraps the existing CLI modules — see api/services.py.
Endpoints are stateless and read-only. No auth in v1.
"""
from datetime import date as _date

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import schemas, services


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


@app.exception_handler(services.ApiInputError)
def _handle_input_error(request: Request, exc: services.ApiInputError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/v1/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "version": API_VERSION}


@app.get("/v1/countries", response_model=schemas.CountriesResponse)
def countries() -> schemas.CountriesResponse:
    items = services.list_countries()
    return schemas.CountriesResponse(count=len(items), countries=items)


@app.get("/v1/holidays", response_model=schemas.HolidaysResponse)
def holidays(
    country: str = Query(..., description="ISO-2 country code (e.g. KR)"),
    year: int = Query(default_factory=lambda: _date.today().year),
    from_today: bool = Query(False),
) -> schemas.HolidaysResponse:
    items = services.get_holidays(country, year, from_today=from_today)
    return schemas.HolidaysResponse(
        country=country.upper(),
        year=year,
        count=len(items),
        holidays=items,
    )


@app.get("/v1/compare", response_model=schemas.CompareResponse)
def compare(
    countries: str = Query(..., description="Comma-separated ISO-2 codes, e.g. KR,NP"),
    year: int = Query(default_factory=lambda: _date.today().year),
) -> schemas.CompareResponse:
    result = services.compare_countries(countries, year)
    return schemas.CompareResponse(**result)
