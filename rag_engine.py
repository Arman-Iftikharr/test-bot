# rag_engine.py
def rag_answer(intent: str, data):
    """Format OGRA API JSON into human-readable messages."""
    if not data:
        return "Sorry — I couldn't fetch data right now. Please try again later."

    # data expected like: {"date": "2025-11-01", "petrol": 275.00, ...}
    date = data.get("date", "unknown date")
    message = ""

    if intent in ("today_prices", "pricing", "general"):
        message = f"⛽ Fuel Prices ({date})\n\n"
        for k, v in data.items():
            if k == "date":
                continue
            message += f"🔹 {k.capitalize()}: {v}\n"
        return message

    if intent == "historical_price":
        message = f"📅 Prices on {date}\n\n"
        for k, v in data.items():
            if k == "date":
                continue
            message += f"🔹 {k.capitalize()}: {v}\n"
        return message

    # default fallback
    return f"Here is the info:\n{data}"
