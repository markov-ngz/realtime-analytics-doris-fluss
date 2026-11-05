package ngz.markov.fixtures.ecommerce;

import java.math.BigDecimal;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class SaleOrder {

    // Unique order identification
    private String orderId;
    private String orderStatus;
    private Long orderTime; // BIGINT timestamp

    // User and session context (matches search events)
    private String userId;
    private String sessionId;
    private String deviceType;
    private String channel;
    private String region;

    // Financial & basket metrics
    private Integer totalItems;
    private BigDecimal revenue;
    private String currency;

    // Ingestion metadata
    private String sourceSystem;
    private Long ingestionTime; // BIGINT timestamp
}