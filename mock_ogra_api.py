# mock_ogra_api.py
from flask import Flask, jsonify, request
from datetime import date, timedelta
import random

app = Flask("mock_ogra_api")

# Base prices for cities
BASE_PRICES = {
    "islamabad": {"petrol": 275.00, "diesel": 289.50, "kerosene": 180.75},
    "lahore": {"petrol": 276.50, "diesel": 290.25, "kerosene": 181.00},
    "karachi": {"petrol": 274.75, "diesel": 288.50, "kerosene": 179.50},
    "peshawar": {"petrol": 273.50, "diesel": 287.75, "kerosene": 179.00}
}

def dynamic_price(base):
    """Add a small random variation to simulate price changes."""
    return round(base + random.uniform(-2.0, 2.0), 2)

def get_city_prices(city_name):
    base = BASE_PRICES.get(city_name, BASE_PRICES["islamabad"])
    return {fuel: dynamic_price(price) for fuel, price in base.items()}

# --- 1. Today's national average prices --- #
@app.get("/fuel-prices/today")
def today():
    today_str = date.today().isoformat()
    prices = get_city_prices("islamabad")
    return jsonify({"date": today_str, **prices})

# --- 2. Prices by specific date --- #
@app.get("/fuel-prices/by-date")
def by_date():
    d = request.args.get("date", date.today().isoformat())
    prices = get_city_prices("islamabad")
    return jsonify({"date": d, **prices})

# --- 3. Price history for last N days --- #
@app.get("/fuel-prices/history")
def history():
    days = int(request.args.get("days", 7))
    data = []
    for i in range(days):
        day = date.today() - timedelta(days=i)
        prices = get_city_prices("islamabad")
        data.append({"date": day.isoformat(), **prices})
    return jsonify(data)

# --- 4. Average prices over last N days --- #
@app.get("/fuel-prices/average")
def average():
    days = int(request.args.get("days", 7))
    avg_prices = {fuel: round(price + random.uniform(-1.5, 1.5), 2) for fuel, price in BASE_PRICES["islamabad"].items()}
    return jsonify({
        "days": days,
        "average_petrol": avg_prices["petrol"],
        "average_diesel": avg_prices["diesel"],
        "average_kerosene": avg_prices["kerosene"]
    })

# --- 5. Trend (up/down/stable) --- #
@app.get("/fuel-prices/trend")
def trend():
    return jsonify({fuel: random.choice(["up", "down", "stable"]) for fuel in ["petrol", "diesel", "kerosene"]})

# --- 6. City-specific prices --- #
@app.get("/fuel-prices/city")
def city_prices():
    city = request.args.get("city", "Islamabad").lower()
    prices = get_city_prices(city)
    return jsonify({"city": city.title(), "date": date.today().isoformat(), **prices})

# --- 7. Alerts based on thresholds --- #
@app.get("/fuel-prices/alerts")
def price_alerts():
    petrol_th = float(request.args.get("petrol", 280))
    diesel_th = float(request.args.get("diesel", 290))
    kerosene_th = float(request.args.get("kerosene", 185))
    current_prices = get_city_prices("islamabad")
    alerts = {fuel: "ok" if current_prices[fuel] < th else "alert" 
              for fuel, th in [("petrol", petrol_th), ("diesel", diesel_th), ("kerosene", kerosene_th)]}
    return jsonify({"date": date.today().isoformat(), "current_prices": current_prices, "alerts": alerts})

# --- 8. Forecast for next N days --- #
@app.get("/fuel-prices/forecast")
def forecast():
    days = int(request.args.get("days", 3))
    city = request.args.get("city", "Islamabad").lower()
    last_prices = get_city_prices(city)
    forecast_data = []
    for i in range(1, days + 1):
        next_day = date.today() + timedelta(days=i)
        day_prices = {fuel: round(price + random.choice([-1, 0, 1]) * random.uniform(0.5, 2.0), 2)
                      for fuel, price in last_prices.items()}
        forecast_data.append({"date": next_day.isoformat(), **day_prices})
        last_prices = day_prices
    return jsonify({"city": city.title(), "forecast_days": days, "forecast": forecast_data})

# --- 9. Forecast with alerts --- #
@app.get("/fuel-prices/forecast-alerts")
def forecast_alerts():
    days = int(request.args.get("days", 3))
    city = request.args.get("city", "Islamabad").lower()
    petrol_th = float(request.args.get("petrol", 280))
    diesel_th = float(request.args.get("diesel", 290))
    kerosene_th = float(request.args.get("kerosene", 185))
    last_prices = get_city_prices(city)
    forecast_data = []

    for i in range(1, days + 1):
        next_day = date.today() + timedelta(days=i)
        day_prices = {}
        day_alerts = {}
        for fuel, price in last_prices.items():
            trend = random.choice([-1, 0, 1])
            next_price = round(price + trend * random.uniform(0.5, 2.0), 2)
            day_prices[fuel] = next_price
            threshold = {"petrol": petrol_th, "diesel": diesel_th, "kerosene": kerosene_th}[fuel]
            day_alerts[fuel] = "ok" if next_price < threshold else "alert"
        forecast_data.append({"date": next_day.isoformat(), "predicted_prices": day_prices, "alerts": day_alerts})
        last_prices = day_prices

    return jsonify({"city": city.title(), "forecast_days": days, "forecast_with_alerts": forecast_data})

if __name__ == "__main__":
    app.run(port=9000, debug=True)

