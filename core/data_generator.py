import random
from datetime import datetime
from faker import Faker

fake = Faker()

COUNTRIES = ["India", "USA", "UK", "Germany", "Brazil", "Japan", "Canada"]
PRODUCTS = ["Laptop", "Phone", "Tablet", "Headphones", "Watch", "Camera"]
CHANNELS = ["Web", "Mobile", "Store", "Partner"]


def generate_event():
    qty = random.randint(1, 5)
    price = round(random.uniform(50, 1500), 2)
    is_anomaly = random.random() < 0.05
    if is_anomaly:
        qty *= random.randint(5, 10)

    return {
        "timestamp": datetime.now().isoformat(),
        "customer_id": fake.random_int(1000, 9999),
        "country": random.choice(COUNTRIES),
        "product": random.choice(PRODUCTS),
        "channel": random.choice(CHANNELS),
        "quantity": qty,
        "unit_price": price,
        "session_duration": random.randint(10, 600),
        "pages_viewed": random.randint(1, 30),
        "is_returning": random.choice([0, 1]),
        "revenue": round(qty * price, 2),
        "injected_anomaly": int(is_anomaly),
    }

