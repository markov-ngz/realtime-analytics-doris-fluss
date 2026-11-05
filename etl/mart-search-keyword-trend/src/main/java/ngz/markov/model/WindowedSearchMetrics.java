package ngz.markov.model;

import lombok.Data;
import lombok.ToString;

import java.io.Serial;
import java.io.Serializable;
import java.math.BigDecimal;

import lombok.Data;
import lombok.ToString;
import java.io.Serial;
import java.io.Serializable;
import java.math.BigDecimal;

@Data
@ToString
public class WindowedSearchMetrics implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    // Window bounds
    private long windowStartMs;
    private long windowEndMs;

    // Aggregation key & dimensions
    private String rawKeyword; // representative raw keyword for downstream mapping
    private String normalizedKeyword;
    private String primaryRegion;

    // Volume metrics
    private long searchCount;
    private long uniqueUserCount;
    private double avgSearchesPerUser;

    // Channel / device modes
    private String dominantChannel;
    private String dominantDevice;

    // Pre-Order & Post-Order Split Metrics
    private long preOrderSearchCount;
    private BigDecimal attributedRevenue = BigDecimal.ZERO;
    private double conversionProxyRate; // preOrderSearchCount / total searchCount (or session ratio)

    private long postOrderSearchCount;
    private BigDecimal postOrderRevenue = BigDecimal.ZERO;

    // Metadata field for downstream use
    private long convertedOrderCount;
}