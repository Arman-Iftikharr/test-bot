import requests

WEBHOOK_URL = "http://127.0.0.1:5000/webhook"

payload = {
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "messages": [
                            {
                                "from": "+923333475553",
                                "text": {"body": "Hello bot?"}
                            }
                        ]
                    }
                }
            ]
        }
    ]
}

try:
    r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    r.raise_for_status()
    print("ok")
except Exception as e:
    print("Error sending message:", e)
