package ngz.markov.model;


import lombok.Data;
import lombok.ToString;

import java.io.Serializable;
import java.math.BigDecimal;

/**
 * Projected subset of staging.sale_order.
 *
 * Only fields required for the revenue attribution join are kept:
 *   - order identification (order_id, order_status)
 *   - order_time for interval-join time bound
 *   - session_id to join with search_event
 *   - revenue for attributed_revenue aggregation
 *
 * Fields intentionally excluded: user_id, device_type, channel, region,
 * total_items, currency, source_system, ingestion_time.
 * (These are available on the search-event side and sourced from there
 *  as the authoritative context per the transformation plan.)
 */
@Data
@ToString
public class SaleOrder implements Serializable {

    private static final long serialVersionUID = 1L;

    private String orderId;
    private String orderStatus;   // filter: keep only COMPLETED
    private long orderTime;       // epoch-ms — used for interval-join bound

    private String sessionId;     // join key with SearchEvent
    private BigDecimal revenue;

}
