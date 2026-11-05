import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker


class SearchKeywordTrendMockGenerator:
    """Generates realistic mock data for mart.search_keyword_trend, ensuring strict uniqueness per window."""

    def __init__(self, seed: int = 42):
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)

        self.keywords = [
            "sneakers",
            "blazer",
            "coat",
            "dress",
            "shorts",
            "skirt",
            "socks",
            "sweater",
            "boots",
            "hoodie",
        ]
        self.regions = [
            "Mazowieckie",
            "Wielkopolskie",
            "Małopolskie",
            "Pomorskie",
            "Dolnośląskie",
        ]
        self.channels = ["paid", "organic", "social", "direct"]
        self.devices = ["mobile", "desktop", "tablet"]

    def generate_raw_mart_data(
        self, hours_back: int = 72, keywords_per_window: int = 5
    ) -> pd.DataFrame:
        """
        Generates structured raw rows where each (window_start, window_end, search_keyword)
        combination is entirely unique across the dataset.
        """
        data = []
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        base_time = now - timedelta(hours=hours_back)

        current_window_start = base_time
        while current_window_start < now:
            window_end = current_window_start + timedelta(hours=1)

            window_keywords = random.sample(
                self.keywords, min(keywords_per_window, len(self.keywords))
            )

            for search_keyword in window_keywords:
                search_count = random.randint(50, 2000)
                unique_user_count = int(search_count * random.uniform(0.6, 0.95))
                avg_searches_per_user = round(
                    search_count / max(unique_user_count, 1), 2
                )

                if random.random() < 0.4:
                    pre_order_search_count = random.randint(0, 30)
                    post_order_search_count = random.randint(300, 1500)
                    conversion_proxy_rate = round(random.uniform(0.0, 0.009), 4)
                else:
                    pre_order_search_count = random.randint(10, 300)
                    post_order_search_count = random.randint(10, 200)
                    conversion_proxy_rate = round(random.uniform(0.01, 0.15), 4)

                attributed_revenue = round(
                    pre_order_search_count
                    * conversion_proxy_rate
                    * random.uniform(50, 150),
                    2,
                )
                post_order_revenue = round(
                    post_order_search_count * random.uniform(5, 25), 2
                )

                baseline_search_count = random.randint(100, 1000)
                search_count_delta = search_count - baseline_search_count
                trend_velocity_score = round(
                    search_count_delta / max(baseline_search_count, 1) * 2.5, 4
                )

                row = {
                    "window_start": current_window_start.strftime(
                        "%Y-%m-%dT%H:%M:%S.000"
                    ),
                    "window_end": window_end.strftime("%Y-%m-%dT%H:%M:%S.000"),
                    "search_keyword": search_keyword,
                    "normalized_keyword": search_keyword,
                    "primary_region": random.choice(self.regions),
                    "search_count": search_count,
                    "unique_user_count": unique_user_count,
                    "avg_searches_per_user": avg_searches_per_user,
                    "dominant_channel": random.choice(self.channels),
                    "dominant_device": random.choice(self.devices),
                    "pre_order_search_count": pre_order_search_count,
                    "attributed_revenue": attributed_revenue,
                    "conversion_proxy_rate": conversion_proxy_rate,
                    "post_order_search_count": post_order_search_count,
                    "post_order_revenue": post_order_revenue,
                    "baseline_search_count": baseline_search_count,
                    "search_count_delta": search_count_delta,
                    "trend_velocity_score": trend_velocity_score,
                    "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000"),
                }
                data.append(row)

            current_window_start = window_end

        return pd.DataFrame(data)

    def generate_funnel_analysis_mock(
        self,
        hours_back: int = 72,
        min_post_searches: int = 200,
        max_conversion_rate: float = 0.01,
        min_ratio: float = 2.0,
    ) -> pd.DataFrame:
        """
        Simulates backend CTE calculations and applies analytical threshold filters.
        """
        df = self.generate_raw_mart_data(hours_back=hours_back)

        if df.empty:
            return pd.DataFrame(
                columns=[
                    "window_start",
                    "window_end",
                    "search_keyword",
                    "primary_region",
                    "dominant_channel",
                    "search_count",
                    "pre_order_search_count",
                    "post_order_search_count",
                    "post_to_pre_search_ratio",
                    "attributed_revenue",
                    "post_order_revenue",
                ]
            )

        df["post_to_pre_search_ratio"] = (
            df["post_order_search_count"].astype(float)
            / df["pre_order_search_count"].clip(lower=1)
        ).round(2)

        filtered_df = df[
            (df["post_order_search_count"] > min_post_searches)
            & (df["conversion_proxy_rate"] < max_conversion_rate)
            & (df["post_to_pre_search_ratio"] > min_ratio)
        ][
            [
                "window_start",
                "window_end",
                "search_keyword",
                "primary_region",
                "dominant_channel",
                "search_count",
                "pre_order_search_count",
                "post_order_search_count",
                "post_to_pre_search_ratio",
                "attributed_revenue",
                "post_order_revenue",
            ]
        ]

        return filtered_df.sort_values(
            by=["post_order_search_count", "post_to_pre_search_ratio"],
            ascending=[False, False],
        ).reset_index(drop=True)

    def generate_mock_search_trends(
        self,
        trend_velocity_score: float = 2.0,
        conversion_proxy_rate: float = 0.02,
        lookback_hours: int = 24,
    ) -> pd.DataFrame:
        """
        Mirrors the SQL query:
            SELECT window_start, window_end, search_keyword, primary_region,
                   trend_velocity_score, conversion_proxy_rate, search_count, attributed_revenue
            FROM mart.search_keyword_trend
            WHERE trend_velocity_score > %(trend_velocity_score)s
              AND conversion_proxy_rate < %(conversion_proxy_rate)s
              AND window_start >= CURRENT_TIMESTAMP - INTERVAL %(lookback_hours)s HOUR
            ORDER BY trend_velocity_score DESC

        Returns keywords that are spiking in search volume (high velocity) but
        have not yet converted — the "opportunity gap" for marketing activation.
        """
        df = self.generate_raw_mart_data(hours_back=lookback_hours)

        if df.empty:
            return pd.DataFrame(
                columns=[
                    "window_start",
                    "window_end",
                    "search_keyword",
                    "primary_region",
                    "dominant_channel",
                    "dominant_device",
                    "trend_velocity_score",
                    "conversion_proxy_rate",
                    "search_count",
                    "attributed_revenue",
                    "search_count_delta",
                    "baseline_search_count",
                ]
            )

        # Parse timestamps so we can filter by lookback window
        df["window_start_dt"] = pd.to_datetime(df["window_start"])
        cutoff = datetime.now() - timedelta(hours=lookback_hours)

        filtered = df[
            (df["trend_velocity_score"] > trend_velocity_score)
            & (df["conversion_proxy_rate"] < conversion_proxy_rate)
            & (df["window_start_dt"] >= cutoff)
        ][
            [
                "window_start",
                "window_end",
                "search_keyword",
                "primary_region",
                "dominant_channel",
                "dominant_device",
                "trend_velocity_score",
                "conversion_proxy_rate",
                "search_count",
                "attributed_revenue",
                "search_count_delta",
                "baseline_search_count",
            ]
        ]

        return filtered.sort_values(
            "trend_velocity_score", ascending=False
        ).reset_index(drop=True)
