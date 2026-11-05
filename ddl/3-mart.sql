USE CATALOG fluss_paimon ;

CREATE DATABASE IF NOT EXISTS mart;

CREATE TABLE mart.search_keyword_trend (
    -- Time window (Hopping window metadata)
   window_start            TIMESTAMP(3),
   window_end              TIMESTAMP(3),

    -- Search keyword dimensions
   search_keyword          STRING,
   normalized_keyword      STRING,
   primary_region          STRING, -- Identifies if trend is region-specific (e.g., Mazowieckie)

    -- Volume & Intent Metrics
   search_count            BIGINT,
   unique_user_count       BIGINT,
   avg_searches_per_user   DOUBLE, -- High ratio indicates user friction / difficulty finding the item

    -- Channel & Traffic Quality Driver
   dominant_channel        STRING, -- e.g., 'paid', 'social', 'organic' - tells marketing if ads drove it
   dominant_device         STRING, -- e.g., 'mobile' vs 'desktop'

    -- Financial & Conversion Impact Proxy
   pre_order_search_count   BIGINT,   -- Searches occurring before an order
   attributed_revenue       DECIMAL(18, 2), -- Revenue attributed to pre-order searches
   conversion_proxy_rate   DOUBLE, -- Ratio of searches that led to an order_id within the session
   post_order_search_count  BIGINT,   -- Searches occurring after an order
   post_order_revenue       DECIMAL(18, 2), -- Revenue (if any) tied to post-order behavior

    -- Trend Velocity & Spike Detection
   baseline_search_count   BIGINT, -- Average search count over the past 24 hours
   search_count_delta      BIGINT, -- Absolute change vs baseline
   trend_velocity_score    DOUBLE, -- Rate of acceleration (Z-score or multiplier vs baseline)

    -- Mart processing metadata
    updated_at              TIMESTAMP(3),
    PRIMARY KEY(window_start, window_end, search_keyword) NOT ENFORCED
) WITH (
      'table.delete.behavior' = 'ALLOW',
      'table.datalake.enabled' = 'true',
      'table.datalake.freshness' = '300s'
);