# ogra_scraper.py
import requests
from bs4 import BeautifulSoup

# -------------------------------
# URLs
# -------------------------------
PETROLEUM_URL = "https://www.ogra.org.pk/notified-petroleum-prices"
E10_URL = "https://www.ogra.org.pk/e-10-gasoline-prices"
IFEM_URL = "https://www.ogra.org.pk/ifem-notifications"
EX_DEPOT_URL = "https://www.ogra.org.pk/detail-computation-ex-depot-sale-price"
PRICE_BUILDUP_URL = "https://www.ogra.org.pk/max-ex-depot-sale-price-price-buildup-period-wise"


# -------------------------------
# Generic HTML Scraper
# -------------------------------
def _scrape_from_url(url, prefix, limit=50):
    """
    Generic scraper for OGRA HTML pages.
    Extracts notification titles starting with a given prefix.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    page_text = soup.get_text(separator="\n")

    results = []

    for line in page_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith(prefix):
            results.append({
                "title": line,
                "link": url
            })

        if len(results) >= limit:
            break

    return results


# -------------------------------
# Petroleum Prices
# -------------------------------
def get_petroleum_notifications(limit=50):
    return _scrape_from_url(
        PETROLEUM_URL,
        "notification petroleum products prices",
        limit
    )


# -------------------------------
# E-10 Gasoline Prices
# -------------------------------
def get_e10_gasoline_notifications(limit=50):
    return _scrape_from_url(
        E10_URL,
        "e-10 gasoline price notification",
        limit
    )


# -------------------------------
# IFEM Notifications
# -------------------------------
def get_ifem_notifications(limit=50):
    return _scrape_from_url(
        IFEM_URL,
        "ifem notification effective dated",
        limit
    )


# -------------------------------
# Ex-Depot Sale Price
# -------------------------------
def get_ex_depot_notifications(limit=50):
    return _scrape_from_url(
        EX_DEPOT_URL,
        "detail computation ex-depot sale price",
        limit
    )


# -------------------------------
# Price Buildup / Max Ex-Depot
# -------------------------------
def get_price_buildup_notifications(limit=50):
    return _scrape_from_url(
        PRICE_BUILDUP_URL,
        "max ex-depot sale price",
        limit
    )
