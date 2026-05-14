"""Korean cultural festivals and observances (축제/기념일).

These are NOT red days — the office stays open. But they're culturally
significant and the user might want to PTO around them.

Categories:
  - 명절 (myeongjeol) — major traditional festivals (Lunar New Year, Chuseok are ALSO red days)
  - 절기 (jeolgi) — seasonal markers (Dongji, Ipchun, Hansik)
  - 기념일 (ginyeomil) — modern commemorative days (Parents', Teachers')
  - 데이 (day) — pop-culture days (Valentine's, Pepero, etc.)
"""
from datetime import date


# Fixed Gregorian-date observances (no lunar conversion needed)
FIXED_FESTIVALS_KR = [
    # (month, day, name_en, name_ko, category)
    (2, 14, "Valentine's Day", "발렌타인데이", "데이"),
    (3, 3, "Samgyeopsal Day", "삼겹살데이", "데이"),
    (3, 14, "White Day", "화이트데이", "데이"),
    (4, 14, "Black Day", "블랙데이", "데이"),
    (5, 1, "Labor Day (workers)", "근로자의날", "기념일"),
    (5, 8, "Parents' Day", "어버이날", "기념일"),
    (5, 15, "Teachers' Day", "스승의날", "기념일"),
    (5, 21, "Couples' Day", "부부의날", "기념일"),
    (6, 25, "Korean War Remembrance", "6·25 한국전쟁일", "기념일"),
    (10, 1, "Armed Forces Day", "국군의날", "기념일"),
    (11, 11, "Pepero Day", "빼빼로데이", "데이"),
    (12, 22, "Winter Solstice", "동지", "절기"),  # approximate; varies by year
]


def fetch(year: int, country: str = "KR") -> list[dict]:
    if country != "KR":
        return []
    out = []
    for month, day, en, ko, cat in FIXED_FESTIVALS_KR:
        try:
            d = date(year, month, day)
        except ValueError:
            continue
        out.append({
            "date": d,
            "name_en": en,
            "name_ko": ko,
            "category": cat,
            "is_red_day": False,
        })
    return out
