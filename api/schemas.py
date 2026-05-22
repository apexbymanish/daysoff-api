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


class HolidayRecord(BaseModel):
    date: date
    name: str
    source: str


class HolidaysResponse(BaseModel):
    country: str
    year: int
    count: int
    holidays: list[HolidayRecord]
