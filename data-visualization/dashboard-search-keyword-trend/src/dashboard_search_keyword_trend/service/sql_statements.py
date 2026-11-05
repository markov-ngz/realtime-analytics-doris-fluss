QUERY = """
    SELECT *
    FROM search_keyword_trend
    LIMIT 10
"""

HIGH_TREND_VELOCITY_WITH_LOW_CONVERSION = """
SELECT
    window_start,
    window_end,
    search_keyword,
    primary_region,
    trend_velocity_score,
    conversion_proxy_rate,
    search_count,
    attributed_revenue
FROM mart.search_keyword_trend
WHERE trend_velocity_score > %(trend_velocity_score)s  -- High velocity threshold (e.g., Z-score > 2)
  AND conversion_proxy_rate < %(conversion_proxy_rate)s -- Low conversion rate threshold (e.g., < 2%)
  AND window_start >= CURRENT_TIMESTAMP - INTERVAL %(window_start)s HOUR
ORDER BY trend_velocity_score DESC
"""

REGIONAL_LOCALIZATION = """
SELECT
  primary_region,
  search_keyword,
  SUM(search_count) AS total_search_volume,
  AVG(trend_velocity_score) AS avg_trend_velocity,
  MAX(window_end) AS latest_window
FROM mart.search_keyword_trend
WHERE primary_region IS NOT NULL
AND trend_velocity_score > 1.5
AND window_start >= CURRENT_TIMESTAMP - INTERVAL '12' HOUR
GROUP BY primary_region, search_keyword
ORDER BY avg_trend_velocity DESC
"""

CHANNEL_DISTRIBUTION = """
 SELECT
     search_keyword,
     dominant_channel,
     search_count,
     trend_velocity_score,
     conversion_proxy_rate,
     window_start
 FROM mart.search_keyword_trend
 WHERE dominant_channel = 'organic'
   AND trend_velocity_score > 2.0
   AND window_start >= CURRENT_TIMESTAMP - INTERVAL '24' HOUR
 ORDER BY search_count DESC
"""

POST_TO_PRE_SEARCH_RATIO = """
WITH keyword_funnel_analysis AS (
   SELECT
       window_start,
       window_end,
       search_keyword,
       primary_region,
       dominant_channel,
       search_count,
       pre_order_search_count,
       post_order_search_count,
       attributed_revenue,
       post_order_revenue,
       conversion_proxy_rate,
       -- Calculate ratio of post-order searches to pre-order conversions/searches
       CAST(post_order_search_count AS DOUBLE) / NULLIF(pre_order_search_count, 0) AS post_to_pre_search_ratio
   FROM mart.search_keyword_trend
   WHERE window_start >= CURRENT_TIMESTAMP - INTERVAL %(lookback_days)s DAY
)
SELECT
   search_keyword,
   primary_region,
   dominant_channel,
   search_count,
   pre_order_search_count,
   post_order_search_count,
   post_to_pre_search_ratio,
   attributed_revenue,
   post_order_revenue
FROM keyword_funnel_analysis
WHERE post_order_search_count > %(post_order_search_count)s
 AND conversion_proxy_rate < %(conversion_proxy_rate)s
 AND post_to_pre_search_ratio > %(post_to_pre_search_ratio)s
ORDER BY post_order_search_count DESC, post_to_pre_search_ratio DESC
"""
