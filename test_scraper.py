from ogra_scraper import get_petroleum_notifications

print("Fetching OGRA notifications...\n")

data = get_petroleum_notifications(10)

print(f"Total: {len(data)}\n")

for i, d in enumerate(data, start=1):
    print(f"{i}. {d['title']}")
    print(f"   {d['link']}\n")
