"""Korea Public Data Portal — official holiday endpoint.

Endpoint: https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo
Requires a free API key from https://data.go.kr (env var: DATA_GO_KR_KEY).
This source is authoritative for substitute (대체) and temporary (임시) holidays.
"""
import os
from datetime import date
import requests
import xml.etree.ElementTree as ET

ENDPOINT = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"


def fetch(year: int, country: str = "KR") -> list[dict]:
    if country != "KR":
        return []
    key = os.environ.get("DATA_GO_KR_KEY")
    if not key:
        return []

    results = []
    for month in range(1, 13):
        params = {
            "ServiceKey": key,
            "solYear": year,
            "solMonth": f"{month:02d}",
            "numOfRows": 50,
        }
        try:
            r = requests.get(ENDPOINT, params=params, timeout=10)
            r.raise_for_status()
        except requests.RequestException:
            continue

        root = ET.fromstring(r.content)
        for item in root.iter("item"):
            is_holiday = (item.findtext("isHoliday") or "").strip() == "Y"
            if not is_holiday:
                continue
            locdate = item.findtext("locdate") or ""
            name = (item.findtext("dateName") or "").strip()
            if len(locdate) != 8:
                continue
            d = date(int(locdate[:4]), int(locdate[4:6]), int(locdate[6:]))
            results.append({
                "date": d,
                "name": name,
                "country": "KR",
                "source": "gov_api",
            })
    return results
