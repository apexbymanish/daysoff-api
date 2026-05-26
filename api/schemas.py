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


class CompareEntry(BaseModel):
    date: date
    name: str


class CompareResponse(BaseModel):
    year: int
    countries: list[str]
    shared: list[CompareEntry]
    only: dict[str, list[CompareEntry]]


class SandwichRecord(BaseModel):
    pto_date: date
    weekday: str
    break_start: date
    break_end: date
    break_length: int
    pto_cost: int
    context: str


class SandwichesResponse(BaseModel):
    country: str
    year: int
    workweek: list[str]
    workweek_source: str
    count: int
    sandwiches: list[SandwichRecord]


class PlanTrip(BaseModel):
    break_start: date
    break_end: date
    break_length: int
    pto_dates: list[date]
    pto_cost: int
    anchors: list[str]


class PlanResponse(BaseModel):
    country: str
    year: int
    budget: int
    workweek: list[str]
    workweek_source: str
    results_by_length: dict[str, list[PlanTrip]]
