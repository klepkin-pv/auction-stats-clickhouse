import argparse
import random
import sys
import time
import uuid
from datetime import UTC, datetime, timedelta

import requests

DEFAULT_URL = "http://localhost:8000/api/v1"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate test auction events and load them into the service API."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="API base url")
    parser.add_argument("--bids", type=int, default=1000, help="number of bids")
    parser.add_argument(
        "--impressions",
        type=int,
        default=0,
        help="number of impressions (0 = 5 * bids)",
    )
    parser.add_argument("--campaigns", type=int, default=3, help="number of campaigns")
    parser.add_argument(
        "--click-rate",
        type=float,
        default=0.05,
        help="share of impressions that get a click, 0..1",
    )
    parser.add_argument("--batch-size", type=int, default=1000, help="rows per request")
    parser.add_argument(
        "--window-hours",
        type=float,
        default=24.0,
        help="spread created_at over the last N hours (0 = now)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.0,
        help="pause between batches in seconds",
    )
    parser.add_argument("--seed", type=int, default=None, help="seed for reproducible data")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print generated rows without sending them",
    )
    return parser.parse_args()


def new_id(rng):
    return str(uuid.UUID(int=rng.getrandbits(128)))


def event_time(rng, window_hours):
    if window_hours <= 0:
        return datetime.now(UTC)
    return datetime.now(UTC) - timedelta(seconds=rng.uniform(0, window_hours * 3600))


def build_bids(rng, campaign_ids, count, window_hours):
    return [
        {
            "id": new_id(rng),
            "campaign_id": rng.choice(campaign_ids),
            "amount": round(rng.uniform(10, 500), 2),
            "created_at": event_time(rng, window_hours).isoformat(),
        }
        for _ in range(count)
    ]


def build_events(rng, campaign_ids, count, window_hours):
    return [
        {
            "id": new_id(rng),
            "campaign_id": rng.choice(campaign_ids),
            "created_at": event_time(rng, window_hours).isoformat(),
        }
        for _ in range(count)
    ]


def build_clicks(rng, impressions, click_rate):
    # клик переиспользует id показа, иначе CTR не сойдётся в join
    clicked = rng.sample(impressions, int(len(impressions) * click_rate))
    return [
        {"id": imp["id"], "campaign_id": imp["campaign_id"], "created_at": imp["created_at"]}
        for imp in clicked
    ]


def batches(rows, size):
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def send(session, url, endpoint, rows, args):
    inserted = 0
    for batch in batches(rows, args.batch_size):
        if args.dry_run:
            inserted += len(batch)
            continue
        response = session.post(f"{url}{endpoint}", json=batch, timeout=30)
        response.raise_for_status()
        inserted += response.json()["inserted"]
        print(f"{endpoint}: {inserted}/{len(rows)}")
        if args.interval:
            time.sleep(args.interval)
    if args.dry_run:
        print(f"{endpoint}: {inserted} rows prepared")
    return inserted


def main():
    args = parse_args()
    if not 0 <= args.click_rate <= 1:
        print("click-rate must be between 0 and 1")
        return 2

    campaign_ids = [f"cmp-{i}" for i in range(1, args.campaigns + 1)]
    impressions_count = args.impressions or args.bids * 5
    rng = random.Random(args.seed)

    bids = build_bids(rng, campaign_ids, args.bids, args.window_hours)
    impressions = build_events(rng, campaign_ids, impressions_count, args.window_hours)
    clicks = build_clicks(rng, impressions, args.click_rate)

    if args.dry_run:
        print(f"campaigns: {', '.join(campaign_ids)}")
        print(f"bid: {bids[0] if bids else None}")
        print(f"impression: {impressions[0] if impressions else None}")
        print(f"click: {clicks[0] if clicks else None}")

    with requests.Session() as session:
        try:
            send(session, args.url, "/bids", bids, args)
            send(session, args.url, "/impressions", impressions, args)
            send(session, args.url, "/clicks", clicks, args)
        except requests.RequestException as exc:
            print(f"request failed: {exc}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
