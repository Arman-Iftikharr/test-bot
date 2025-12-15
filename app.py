
# app.py
import os
import requests
import logging
from flask import Flask, request
from dotenv import load_dotenv

from database import save_message
from nlp import detect_intent, extract_entities
from ogra_api_official import get_today_prices, get_price_by_date
from rag_engine import rag_answer

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ogra_bot")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# -----------------------------------------------------------
# 1) VERIFY WEBHOOK (GET)
# -----------------------------------------------------------
@app.get("/webhook")
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully.")
        return challenge, 200

    logger.warning("Webhook verification failed.")
    return "verification failed", 403

# -----------------------------------------------------------
# 2) HANDLE INCOMING MESSAGES (POST)
# -----------------------------------------------------------
@app.post("/webhook")
def incoming_message():
    data = request.get_json()
    logger.info("Incoming Webhook: %s", data)

    try:
        entry = data.get("entry", [])[0]
        change = entry.get("changes", [])[0].get("value", {})

        # ignore statuses
        if "statuses" in change:
            logger.info("Status update received. Ignoring.")
            return "ok", 200

        # no messages? ignore
        if "messages" not in change:
            logger.info("No message found. System/metadata event.")
            return "ok", 200

        msg = change["messages"][0]
        sender = msg.get("from")

        # safely extract text
        text = msg.get("text", {}).get("body")
        if not text:
            logger.info(f"No text found in message from {sender}: {msg}")
            return "ok", 200

        logger.info("User %s said: %s", sender, text)

        # Save to DB
        save_message(sender, text)

        # NLP
        intent = detect_intent(text)
        entities = extract_entities(text)

        # Bot reply
        reply = generate_reply(intent, entities, text)
        send_whatsapp_message(sender, reply)

    except Exception as e:
        logger.exception("Error processing webhook: %s", e)

    return "ok", 200

# -----------------------------------------------------------
# 3) INTENT → RESPONSE HANDLER (IMPROVED)
# -----------------------------------------------------------
def generate_reply(intent, entities, user_input):
    logger.info("Intent: %s | Entities: %s", intent, entities)

    # --------------------------
    # GREETING
    # --------------------------
    if intent == "greeting":
        return (
            "Hello 👋\n"
            "I can help you with:\n"
            "• Today's petrol & diesel prices\n"
            "• Historical price for any date\n"
            "\nExample: 'What's today's price?' or 'Price on 2024-11-01'"
        )

    # --------------------------
    # TODAY'S PRICE
    # --------------------------
    if intent == "today_price":
        data = get_today_prices()
        if not data:
            return "⚠️ Unable to fetch today's fuel prices. Please try again later."
        return rag_answer("today_prices", data)

    # --------------------------
    # PRICE BY DATE
    # --------------------------
    if intent == "date_price":
        date = entities.get("date")

        if not date:
            return (
                "📅 Please provide a date in *YYYY-MM-DD* format.\n"
                "Example: 2025-11-01"
            )

        data = get_price_by_date(date)
        if not data:
            return f"⚠️ Sorry, I couldn't find data for {date}. Try another date."

        return rag_answer("historical_price", data)

    # --------------------------
    # PRICE QUERY (general)
    # --------------------------
    if intent == "pricing":
        data = get_today_prices()
        if not data:
            return "⚠️ Could not retrieve current fuel prices."
        return rag_answer("pricing", data)

    # --------------------------
    # UNKNOWN INTENT (fallback)
    # --------------------------
    return (
        "❓ I couldn't understand that.\n"
        "Try asking:\n"
        "• 'Today petrol price?'\n"
        "• 'Fuel prices today'\n"
        "• 'Price on 2025-05-01'"
    )

# -----------------------------------------------------------
# 4) SEND MESSAGE USING WHATSAPP CLOUD API
# -----------------------------------------------------------
# 4) SEND MESSAGE USING WHATSAPP CLOUD API (MODIFIED FOR DEBUGGING)
def send_whatsapp_message(to, message):
    # Ensure 'to' number starts with the plus sign
    if not to.startswith('+'):
        to = f'+{to}'
    
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message},
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        res.raise_for_status()
        logger.info(f"Sent message to {to} successfully.")
    except requests.exceptions.HTTPError as e:
        # This block catches errors like 400, 401, 403, 404 from the API
        logger.error(f"Failed to send WhatsApp message (HTTP Error): {e}")
        logger.error(f"Response Body: {res.text}") # <-- THIS WILL SHOW META'S ERROR MESSAGE
    except Exception as e:
        logger.exception("Failed to send WhatsApp message (Generic Error): %s", e)


# -----------------------------------------------------------
# 5) START FLASK SERVER
# -----------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

