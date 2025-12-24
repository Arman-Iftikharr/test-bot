from ogra_scraper import get_petroleum_notifications
from filters import filter_notifications

# Simulate NLP output
entities = {
    "month": "December",
    "year": "2025"
}

notifications = get_petroleum_notifications(20)

filtered = filter_notifications(notifications, entities)

print("\nFiltered Results:\n")

for n in filtered:
    print(n["title"])
