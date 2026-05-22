"""Pydantic response models for the daysoff-api HTTP surface."""
from datetime import date
from pydantic import BaseModel


class CountryInfo(BaseModel):
    code: str
    name: str
    news_enriched: bool


class CountriesResponse(BaseModel):
    count: int
    countries: list[CountryInfo]
