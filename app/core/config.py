from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Auction Stats ClickHouse"
    clickhouse_host: str = "clickhouse"
    clickhouse_port: int = 8123
    clickhouse_database: str = "auction"

    class Config:
        env_file = ".env"


settings = Settings()
