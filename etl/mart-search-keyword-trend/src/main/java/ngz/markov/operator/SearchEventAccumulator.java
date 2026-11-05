package ngz.markov.operator;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Mutable accumulator for {@link SearchEventAggregateFunction}.
 *
 * Tracks per-window running totals. Frequency maps for channel, device
 * and region are kept small because cardinality is bounded.
 */
public class SearchEventAccumulator {
    public long count = 0;
    public Set<String> uniqueUsers = new HashSet<>();

    // Pre-order tracking
    public long preOrderSearchCount = 0;
    public BigDecimal attributedRevenue = BigDecimal.ZERO;
    public Set<String> preOrderSessions = new HashSet<>();

    // Post-order tracking
    public long postOrderSearchCount = 0;
    public BigDecimal postOrderRevenue = BigDecimal.ZERO;

    // Frequencies for mode computation
    public Map<String, Long> channelFreq = new HashMap<>();
    public Map<String, Long> deviceFreq = new HashMap<>();
    public Map<String, Long> regionFreq = new HashMap<>();

    public String rawKeyword = null;
}