from clickhouse_driver import Client

from app.core.config import settings


def get_client() -> Client:
    return Client(
        host=settings.clickhouse_host,
        port=9000,
        database=settings.clickhouse_database,
    )


def init_db() -> None:
    client = get_client()
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS bids_raw (
            bid_id UUID,
            lot_id String,
            bidder_id String,
            amount Decimal(18, 2),
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (lot_id, created_at)
        """
    )
    client.execute(
        """
        CREATE TABLE IF NOT EXISTS bids_stats (
            lot_id String,
            total_bids UInt64,
            avg_amount Decimal(18, 2),
            max_amount Decimal(18, 2),
            unique_bidders UInt64,
            updated_at DateTime DEFAULT now()
        ) ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY lot_id
        """
    )
