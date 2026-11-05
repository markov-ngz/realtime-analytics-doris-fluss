package ngz.markov.model;

import lombok.Data;
import lombok.ToString;

import java.io.Serial;
import java.io.Serializable;
import java.math.BigDecimal;

/**
 * Projected subset of staging.search_event.
 *
 * Only the fields required for the hot_search_keywords pipeline are kept:
 *   - event-time for watermark
 *   - user/session/geo/device/channel for aggregation dimensions
 *   - search text as the core keyword
 *   - order_id & revenue for conversion proxy and revenue attribution
 *
 * Fields intentionally excluded: sku_id, product_id, category_id, brand_id,
 * merchant_id, experiment_id, experiment_variant, search_rank, quantity,
 * source_system, ingestion_time.
 */
@Data
@ToString
public class SearchEvent implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    private String eventId;
    private String eventType;
    private long eventTime;       // epoch-ms — used for watermark

    private String userId;
    private String sessionId;
    private String deviceType;
    private String channel;
    private String region;

    private String searchText;    // raw keyword to normalize + aggregate

    private String orderId;       // non-null when event is a purchase/cart event
    private BigDecimal revenue;   // non-null when order attached

}
