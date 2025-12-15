# nlp.py (IMPROVED)
import re
from datetime import datetime, timedelta

def detect_intent(text: str) -> str:
    text = text.lower()

    # -----------------------------
    # GREETING (English + Urdu)
    # -----------------------------
    if any(w in text for w in ["hi", "hello", "salam", "assalam", "aslam"]):
        return "greeting"

    # -----------------------------
    # TODAY price queries
    # -----------------------------
    if any(w in text for w in ["today", "aaj", "aj", "current", "abhi"]):
        return "today_price"

    # -----------------------------
    # YESTERDAY
    # -----------------------------
    if any(w in text for w in ["yesterday", "kal"]):
        return "yesterday_price"

    # -----------------------------
    # Specific date (YYYY-MM-DD or DD/MM/YYYY)
    # -----------------------------
    if re.search(r"\d{4}-\d{2}-\d{2}", text) or re.search(r"\d{1,2}/\d{1,2}/\d{4}", text):
        return "date_price"

    # -----------------------------
    # General fuel price queries
    # -----------------------------
    if any(w in text for w in [
        "price", "prices", "petrol", "diesel", "fuel", "kerosene",
        "rate", "cost", "petroleum",
        "lahore", "karachi", "islamabad", "peshawar", "quetta"
    ]):
        return "pricing"

    return "unknown"


def extract_entities(text: str) -> dict:
    """Extract actual dates or city names."""
    text = text.lower()
    entities = {}

    # -----------------------------
    # CITY DETECTION (OPTIONAL)
    # -----------------------------
    cities = ["lahore", "karachi", "islamabad", "peshawar", "quetta", "multan"]
    for c in cities:
        if c in text:
            entities["city"] = c
            break

    # -----------------------------
    # YESTERDAY → auto-generate date
    # -----------------------------
    if "yesterday" in text or "kal" in text:
        yesterday = datetime.now() - timedelta(days=1)
        entities["date"] = yesterday.strftime("%Y-%m-%d")
        return entities

    # -----------------------------
    # YYYY-MM-DD
    # -----------------------------
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        entities["date"] = m.group(1)
        return entities

    # -----------------------------
    # DD/MM/YYYY → convert to YYYY-MM-DD
    # -----------------------------
    m2 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m2:
        dd, mm, yyyy = m2.groups()
        try:
            dt = datetime(int(yyyy), int(mm), int(dd))
            entities["date"] = dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    return entities
