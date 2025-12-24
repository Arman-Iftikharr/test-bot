# app.py
import os
import logging
import requests
from flask import Flask, request
from dotenv import load_dotenv

from nlp import detect_intent, extract_entities, detect_category
from ogra_scraper import (
    get_petroleum_notifications,
    get_e10_gasoline_notifications,
    get_ifem_notifications,
    get_ex_depot_notifications
)
from filters import filter_notifications

# --------------------------------------------------
# ENV + APP
# --------------------------------------------------
load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ograbot")


VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# --------------------------------------------------
# In-memory user session
# --------------------------------------------------
USER_STATE = {}
WELCOME_MESSAGE = (
    "🤖 *Ograbot* – OGRA WhatsApp Assistant\n"
    "(Oil & Gas Regulatory Authority – Pakistan)\n\n"
    "Please choose a category:\n\n"
    "1️⃣ Notified Petroleum Prices\n"
    "2️⃣ E-10 Gasoline Prices\n"
    "3️⃣ IFEM Notifications\n"
    "4️⃣ Detail Computation Ex-Depot Sale Price\n\n"
    "Examples:\n"
    "• Petrol price May 2021\n"
    "• Gas rate January 2017\n"
    "• IFEM May 2021\n\n"
    "Type `exit` anytime to restart 😊"
)


# --------------------------------------------------
# Webhook Verification
# --------------------------------------------------
@app.get("/webhook")
def verify_webhook():
    if (
        request.args.get("hub.mode") == "subscribe"
        and request.args.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return request.args.get("hub.challenge"), 200
    return "verification failed", 403


# --------------------------------------------------
# Incoming WhatsApp Messages
# --------------------------------------------------
@app.post("/webhook")
def incoming_message():
    data = request.get_json()
    logger.info("Incoming webhook received")

    try:
        change = data["entry"][0]["changes"][0]["value"]

        if "messages" not in change:
            return "ok", 200

        msg = change["messages"][0]
        sender = msg["from"]
        text = msg["text"]["body"].strip()

        logger.info("User message: %s", text)

        intent = detect_intent(text)
        entities = extract_entities(text)
        category = detect_category(text)

        # -------- MEMORY --------
        last_category = USER_STATE.get(sender)

        if category:
            USER_STATE[sender] = category
        elif last_category:
            category = last_category

        logger.info(
            "Intent: %s | Category: %s | Entities: %s",
            intent, category, entities
        )

        reply = generate_reply(sender, intent, entities, category)
        send_whatsapp_message(sender, reply)

    except Exception as e:
        logger.exception("Webhook error: %s", e)

    return "ok", 200


# --------------------------------------------------
# BOT LOGIC
# --------------------------------------------------
def generate_reply(sender, intent, entities, category):

    # -------- EXIT --------
    if intent == "restart":
        USER_STATE.pop(sender, None)
        return WELCOME_MESSAGE

    # -------- GREETING --------
    if intent == "greeting":
        return WELCOME_MESSAGE

    # -------- MENU HANDLERS --------
    if intent == "petroleum_menu":
        USER_STATE[sender] = "petroleum"
        return (
            "🛢️ *Notified Petroleum Prices selected*\n\n"
            "Tell me the time period:\n"
            "• May 2021\n"
            "• January 2017\n"
            "• Latest"
        )

    if intent == "e10_menu":
        USER_STATE[sender] = "e10"
        return (
            "⛽ *E-10 Gasoline Prices selected*\n\n"
            "Tell me the time period:\n"
            "• May 2021\n"
            "• January 2017\n"
            "• Latest"
        )

    if intent == "ifem_menu":
        USER_STATE[sender] = "ifem"
        return (
            "📄 *IFEM Notifications selected*\n\n"
            "Tell me the time period:\n"
            "• May 2021\n"
            "• January 2017\n"
            "• Latest"
        )

    if intent == "ex_depot_menu":
        USER_STATE[sender] = "ex_depot"
        return (
            "📊 *Detail Computation Ex-Depot Prices selected*\n\n"
            "Tell me the time period:\n"
            "• May 2021\n"
            "• Latest"
        )

    # -------- DATA SOURCE --------
    if category == "e10":
        notifications = get_e10_gasoline_notifications(limit=300)
        title = "E-10 Gasoline"
    elif category == "ifem":
        notifications = get_ifem_notifications(limit=300)
        title = "IFEM"
    elif category == "ex_depot":
        notifications = get_ex_depot_notifications(limit=300)
        title = "Ex-Depot Sale Price"
    else:
        notifications = get_petroleum_notifications(limit=300)
        title = "Petroleum"

    logger.info("Total scraped notifications: %d", len(notifications))

    # -------- UX POLISH --------
    if intent == "unknown" and category:
        return (
            f"📌 *{title} selected*\n\n"
            "You can ask:\n"
            "• Latest\n"
            "• May 2021\n"
            "• January 2017\n\n"
            "Type `exit` to restart"
        )

    # -------- LATEST --------
    if intent == "latest":
        reply = f"📊 Latest OGRA {title} Notifications:\n\n"
        for n in notifications[:5]:
            reply += f"• {n['title']}\n{n['link']}\n\n"
        return reply

    # -------- DATE QUERY --------
    if intent == "date_query":
        results = filter_notifications(notifications, entities)

        if not results:
            return "❌ No OGRA notifications found for your query."

        reply = f"📅 OGRA {title} Notifications:\n\n"
        for r in results[:10]:
            reply += f"• {r['title']}\n{r['link']}\n\n"
        return reply

    # -------- FALLBACK --------
    return (
        "❓ I didn’t understand that.\n\n"
        "Try:\n"
        "• Latest\n"
        "• May 2021\n"
        "• IFEM January 2017\n"
        "• exit"
    )


# --------------------------------------------------
# Send WhatsApp Message
# --------------------------------------------------
def send_whatsapp_message(to, message):
    if not to.startswith("+"):
        to = f"+{to}"

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

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    logger.info("WhatsApp API response: %s", response.status_code)


# --------------------------------------------------
# Run App
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
