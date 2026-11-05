import pandas as pd

from dashboard_search_keyword_trend import DorisConnection
from dashboard_search_keyword_trend.service import sql_statements


class SearchKeywordTrendService:
    """Service layer handling business logic and data retrieval for keyword trends."""

    def __init__(self, db_connection: DorisConnection):
        self.db = db_connection

    def fetch_sample_data(self) -> pd.DataFrame:
        """Fetch the first 10 rows of search keyword trends."""
        rows = self.db.execute("SELECT * FROM search_keyword_trend LIMIT 10")
        return pd.DataFrame(rows)

    def fetch_high_trend_velocity_with_low_conversion(
        self,
        trend_velocity_score: float = 2,
        conversion_proxy_rate: float = 0.02,
        lookback_hours: int = 24,
    ) -> pd.DataFrame:
        params = {
            "trend_velocity_score": trend_velocity_score,
            "conversion_proxy_rate": conversion_proxy_rate,
            "window_start": lookback_hours,
        }
        rows = self.db.execute(
            sql_statements.HIGH_TREND_VELOCITY_WITH_LOW_CONVERSION, params=params
        )
        return pd.DataFrame(rows)

    def fetch_regional_localization(self) -> pd.DataFrame:
        rows = self.db.execute(sql_statements.REGIONAL_LOCALIZATION)
        return pd.DataFrame(rows)

    def fetch_channel_distribution(self) -> pd.DataFrame:
        rows = self.db.execute(sql_statements.CHANNEL_DISTRIBUTION)
        return pd.DataFrame(rows)

    def fetch_post_to_pre_search_ratio(
        self,
        min_post_order_search_count: int = 500,
        max_conversion_proxy_rate: float = 0.01,
        min_post_to_pre_ratio: float = 2.0,
        lookback_days: int = 7,
    ) -> pd.DataFrame:
        """
        Retrieves post-search vs pre-order funnel metrics to identify accessory demand,
        merchandising kits, or customer support documentation gaps.
        """
        params = {
            "post_order_search_count": min_post_order_search_count,
            "conversion_proxy_rate": max_conversion_proxy_rate,
            "post_to_pre_search_ratio": min_post_to_pre_ratio,
            "lookback_days": lookback_days,
        }

        # Execute query passing parameters securely to the Doris connection driver
        rows = self.db.execute(sql_statements.POST_TO_PRE_SEARCH_RATIO, params=params)
        return pd.DataFrame(rows)
