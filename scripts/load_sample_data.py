import random
import uuid

import requests

CAMPAIGNS = ["cmp-1", "cmp-2", "cmp-3"]
URL = "http://localhost:8000/api/v1"


def load():
    bids = [
        {
            "id": str(uuid.uuid4()),
            "campaign_id": random.choice(CAMPAIGNS),
            "amount": round(random.uniform(10, 500), 2),
        }
        for _ in range(1000)
    ]
    requests.post(f"{URL}/bids", json=bids)

    impressions = [
        {"id": str(uuid.uuid4()), "campaign_id": random.choice(CAMPAIGNS)}
        for _ in range(5000)
    ]
    requests.post(f"{URL}/impressions", json=impressions)

    clicks = [
        {"id": str(uuid.uuid4()), "campaign_id": random.choice(CAMPAIGNS)}
        for _ in range(250)
    ]
    requests.post(f"{URL}/clicks", json=clicks)

    print("loaded")


if __name__ == "__main__":
    load()
