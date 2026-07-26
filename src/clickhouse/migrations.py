from src.clickhouse.client import get_client

MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS bids (
        id UUID,
        campaign_id String,
        amount Float64,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (campaign_id, id)
    """,
    """
    CREATE TABLE IF NOT EXISTS impressions (
        id UUID,
        campaign_id String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (campaign_id, id)
    """,
    """
    CREATE TABLE IF NOT EXISTS clicks (
        id UUID,
        campaign_id String,
        created_at DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (campaign_id, id)
    """,
]


def run_migrations():
    client = get_client()
    for sql in MIGRATIONS:
        client.command(sql)
