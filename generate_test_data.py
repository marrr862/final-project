import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/events"

event_types = [
    "click",
    "search",
    "page_view",
    "purchase",
    "add_to_cart"
]

pages = [
    "home",
    "catalog",
    "products",
    "checkout",
    "profile"
]

categories = [
    "tech",
    "books",
    "fashion",
    "electronics",
    "sports"
]

for i in range(200):
    payload = {
        "user_id": random.randint(1, 20),
        "event_type": random.choice(event_types),
        "page": random.choice(pages),
        "product_id": random.randint(100, 999),
        "category": random.choice(categories),
        "timestamp": (
            datetime.now() -
            timedelta(minutes=random.randint(0, 5000))
        ).isoformat()
    }

    response = requests.post(API_URL, json=payload)

    print(
        f"Event {i+1}:",
        response.status_code
    )

print("Finished!")