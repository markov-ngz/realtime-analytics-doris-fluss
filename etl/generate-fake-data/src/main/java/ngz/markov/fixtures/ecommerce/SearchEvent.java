package ngz.markov.fixtures.ecommerce;

import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.annotation.JsonNaming;
import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;

@Data
@Builder
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public class SearchEvent {

    // Unique event identification
    private String eventId;
    private String eventType;
    private Long eventTime;

    // User and session context
    private String userId;
    private String sessionId;
    private String deviceType;
    private String channel;
    private String region;

    // Search context
    private String searchId;
    private String searchText;

    // Product context (nullable for events without a SKU)
    private String skuId;
    private String productId;
    private String categoryId;
    private String brandId;
    private String merchantId;

    // A/B experiment context
    private String experimentId;
    private String experimentVariant;

    // Event-specific attributes
    private Integer searchRank;
    private Integer quantity;
    private String orderId;
    private BigDecimal revenue;

    // Ingestion metadata
    private String sourceSystem;
    private Long ingestionTime;
}
