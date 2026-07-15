from clickhouse_driver import Client

from app.db.clickhouse import get_client


def aggregate_lot_stats(lot_id: str, client: Client | None = None) -> None:
    client = client or get_client()
    client.execute(
        """
        INSERT INTO bids_stats (lot_id, total_bids, avg_amount, max_amount, unique_bidders)
        SELECT
            lot_id,
            count() AS total_bids,
            avg(amount) AS avg_amount,
            max(amount) AS max_amount,
            uniqExact(bidder_id) AS unique_bidders
        FROM bids_raw
        WHERE lot_id = %(lot_id)s
        GROUP BY lot_id
        """,
        {"lot_id": lot_id},
    )
