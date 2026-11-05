package ngz.markov.model;

import lombok.Data;
import lombok.ToString;

import java.io.Serial;
import java.io.Serializable;
import java.math.BigDecimal;
import java.sql.Timestamp;

/**
 * Final mart record mirroring mart.hot_search_keywords column-for-column.
 * Produced by the TrendVelocityProcessFunction (Step 4) and printed / sinked.
 */
@Data
@ToString
public class SearchKeywordTrend implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    // Window
    private Timestamp windowStart;
    private Timestamp windowEnd;

    // Keyword dimensions
    private String searchKeyword;
    private String normalizedKeyword;
    private String primaryRegion;

    // Volume & intent
    private long searchCount;
    private long uniqueUserCount;
    private double avgSearchesPerUser; // Note: DDL shows double, let's keep double or match DDL type

    // Channel & device
    private String dominantChannel;
    private String dominantDevice;

    // Financial & conversion (Pre-order & Post-order split)
    private long preOrderSearchCount;
    private BigDecimal attributedRevenue;
    private double conversionProxyRate;
    private long postOrderSearchCount;
    private BigDecimal postOrderRevenue;

    // Trend velocity
    private long baselineSearchCount;
    private long searchCountDelta;
    private double trendVelocityScore;

    // Metadata
    private Timestamp updatedAt;
}