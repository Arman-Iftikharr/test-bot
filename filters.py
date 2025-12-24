import re

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def extract_date_from_title(title: str) -> dict:
    """
    Extract day, month, year from OGRA notification title
    """
    title = title.lower()

    # Year
    year_match = re.search(r"\b(19|20)\d{2}\b", title)
    year = int(year_match.group()) if year_match else None

    # Month
    month = None
    for m in MONTHS:
        if m in title:
            month = m
            break

    # Day (optional)
    day_match = re.search(r"\b\d{1,2}\b", title)
    day = int(day_match.group()) if day_match else None

    return {
        "year": year,
        "month": month,
        "day": day
    }


def filter_notifications(notifications, entities):
    """
    Filter notifications using extracted entities from NLP
    """
    filtered = []

    for n in notifications:
        date_info = extract_date_from_title(n["title"])

        # Year filter
        if "year" in entities and date_info["year"] != int(entities["year"]):
            continue

        # Month filter
        if "month" in entities:
            if not date_info["month"]:
                continue
            if date_info["month"].lower() != entities["month"].lower():
                continue

        filtered.append(n)

    return filtered
