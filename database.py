# database.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["test-bot"]
messages_col = db["messages"]

def save_message(sender: str, message: str):
    try:
        messages_col.insert_one({
            "sender": sender,
            "message": message
        })
    except Exception as e:
        # avoid crashing the webhook if DB fails
        print("DB save error:", e)


