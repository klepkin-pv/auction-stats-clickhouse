import random
import uuid

import requests

CAMPAIGNS = ["cmp-1", "cmp-2", "cmp-3"]
URL = "http://localhost:8000/api/v1"


def post_batch(endpoint, rows):
    resp = requests.post(f"{URL}{endpoint}", json=rows)
    resp.raise_for_status()
    return resp.json()["inserted"]


def load():
    bids = [
        {
            "id": str(uuid.uuid4()),
            "campaign_id": random.choice(CAMPAIGNS),
            "amount": round(random.uniform(10, 500), 2),
        }
        for _ in range(1000)
    ]
    print(f"bids inserted: {post_batch('/bids', bids)}")

    impressions = [
        {"id": str(uuid.uuid4()), "campaign_id": random.choice(CAMPAIGNS)}
        for _ in range(5000)
    ]
    print(f"impressions inserted: {post_batch('/impressions', impressions)}")

    # часть показов с кликами
    click_ids = [imp["id"] for imp in random.sample(impressions, 250)]
    clicks = [{"id": iid, "campaign_id": random.choice(CAMPAIGNS)} for iid in click_ids]
    print(f"clicks inserted: {post_batch('/clicks', clicks)}")


if __name__ == "__main__":
    load()
