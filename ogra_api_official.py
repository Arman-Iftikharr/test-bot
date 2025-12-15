# ogra_api_official.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("OGRA_API_BASE")  # e.g. https://api.ogra.gov.pk/fuel-prices

def get_today_prices():
    """GET {BASE}/today -> expects JSON."""
    if not BASE:
        return None
    try:
        url = f"{BASE}/today"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("OGRA API error (today):", e)
        return None

def get_price_by_date(date_str: str):
    """GET {BASE}/by-date?date=YYYY-MM-DD -> expects JSON."""
    if not BASE:
        return None
    try:
        url = f"{BASE}/by-date"
        params = {"date": date_str}
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("OGRA API error (by-date):", e)
        return None
