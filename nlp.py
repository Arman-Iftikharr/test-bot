# nlp.py
import re

MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]


# -------------------------------
# Detect intent
# -------------------------------
def detect_intent(text: str) -> str:
    t = text.lower().strip()

    # Exit / Restart
    if t in ["exit", "menu", "start", "back", "restart"]:
        return "restart"

    # Greetings
    if t in ["hi", "hello", "hey"]:
        return "greeting"

    # Menu options
    if t == "1":
        return "petroleum_menu"

    if t == "2":
        return "e10_menu"
    if t == "3":
        return "ifem_menu"

    if t == "4":
     return "ex_depot_menu"

    if t == "5":
     return "price_buildup_menu"

    # Latest
    if "latest" in t or "today" in t:
        return "latest"

    # Date-based query
    if re.search(r"\b(19|20)\d{2}\b", t):
        return "date_query"

    return "unknown"

# -------------------------------
# Detect category
# -------------------------------
def detect_category(text: str):
    t = text.lower()

    if "petroleum" in t or "oil" in t:
        return "petroleum"

    if "e-10" in t or "e10" in t or "gasoline" in t:
        return "e10"

    if "ifem" in t:
        return "ifem"

    if "ex-depot" in t or "detail computation" in t:
        return "ex_depot"

    if "price buildup" in t or "max ex-depot" in t:
        return "price_buildup"

    return None


# -------------------------------
# Extract entities (month/year)
# -------------------------------
def extract_entities(text: str):
    t = text.lower()
    entities = {}

    # Year
    year_match = re.search(r"\b(19|20)\d{2}\b", t)
    if year_match:
        entities["year"] = year_match.group()

    # Month
    for m in MONTHS:
        if m in t:
            entities["month"] = m.capitalize()
            break

    return entities
