package ngz.markov.operator;

import ngz.markov.model.EnrichedSearchEvent;
import ngz.markov.model.SearchEvent;
import ngz.markov.model.WindowedSearchMetrics;
import ngz.markov.util.KeywordNormalizer;
import org.apache.flink.api.common.functions.AggregateFunction;

import java.util.Map;

public class SearchEventAggregateFunction
        implements AggregateFunction<EnrichedSearchEvent, SearchEventAccumulator, WindowedSearchMetrics> {

    private static final long serialVersionUID = 1L;

    @Override
    public SearchEventAccumulator createAccumulator() {
        return new SearchEventAccumulator();
    }

    @Override
    public SearchEventAccumulator add(EnrichedSearchEvent event, SearchEventAccumulator acc) {
        acc.count++;

        if (event.getUserId() != null) {
            acc.uniqueUsers.add(event.getUserId());
        }

        // Categorize based on attribution join output type
        String searchType = event.getSearchType() != null ? event.getSearchType() : "UNATTRIBUTED";

        switch (searchType) {
            case "PRE_ORDER":
                acc.preOrderSearchCount++;
                if (event.getSessionId() != null) {
                    acc.preOrderSessions.add(event.getSessionId());
                }
                if (event.getRevenue() != null) {
                    acc.attributedRevenue = acc.attributedRevenue.add(event.getRevenue());
                }
                break;

            case "POST_ORDER":
                acc.postOrderSearchCount++;
                if (event.getRevenue() != null) {
                    acc.postOrderRevenue = acc.postOrderRevenue.add(event.getRevenue());
                }
                break;

            case "UNATTRIBUTED":
            default:
                // Handled in total search count, no specific pre/post attribution
                break;
        }

        // Frequency maps for dominant-value computation
        if (event.getChannel() != null) {
            acc.channelFreq.merge(event.getChannel(), 1L, Long::sum);
        }
        if (event.getDeviceType() != null) {
            acc.deviceFreq.merge(event.getDeviceType(), 1L, Long::sum);
        }
        if (event.getRegion() != null) {
            acc.regionFreq.merge(event.getRegion(), 1L, Long::sum);
        }

        // Keep one representative raw keyword
        if (acc.rawKeyword == null && event.getSearchText() != null) {
            acc.rawKeyword = event.getSearchText();
        }

        return acc;
    }

    @Override
    public WindowedSearchMetrics getResult(SearchEventAccumulator acc) {
        WindowedSearchMetrics m = new WindowedSearchMetrics();

        m.setSearchCount(acc.count);
        m.setUniqueUserCount(acc.uniqueUsers.size());
        m.setAvgSearchesPerUser(
                acc.uniqueUsers.isEmpty() ? 0.0 : (double) acc.count / acc.uniqueUsers.size()
        );

        // Pre-order & Post-order split assignment
        m.setPreOrderSearchCount(acc.preOrderSearchCount);
        m.setAttributedRevenue(acc.attributedRevenue);

        // Conversion proxy rate: proportion of searches that drove/preceded an order
        double conversionRate = acc.count == 0 ? 0.0 : (double) acc.preOrderSearchCount / acc.count;
        m.setConversionProxyRate(conversionRate);

        m.setPostOrderSearchCount(acc.postOrderSearchCount);
        m.setPostOrderRevenue(acc.postOrderRevenue);

        // Dimensions
        m.setDominantChannel(mode(acc.channelFreq));
        m.setDominantDevice(mode(acc.deviceFreq));
        m.setPrimaryRegion(mode(acc.regionFreq));

        if (acc.rawKeyword != null) {
            m.setRawKeyword(acc.rawKeyword);
            m.setNormalizedKeyword(KeywordNormalizer.normalize(acc.rawKeyword));
        }

        return m;
    }

    @Override
    public SearchEventAccumulator merge(SearchEventAccumulator a, SearchEventAccumulator b) {
        a.count += b.count;
        a.uniqueUsers.addAll(b.uniqueUsers);

        a.preOrderSearchCount += b.preOrderSearchCount;
        a.preOrderSessions.addAll(b.preOrderSessions);
        a.attributedRevenue = a.attributedRevenue.add(b.attributedRevenue);

        a.postOrderSearchCount += b.postOrderSearchCount;
        a.postOrderRevenue = a.postOrderRevenue.add(b.postOrderRevenue);

        b.channelFreq.forEach((k, v) -> a.channelFreq.merge(k, v, Long::sum));
        b.deviceFreq.forEach((k, v) -> a.deviceFreq.merge(k, v, Long::sum));
        b.regionFreq.forEach((k, v) -> a.regionFreq.merge(k, v, Long::sum));

        if (a.rawKeyword == null) {
            a.rawKeyword = b.rawKeyword;
        }
        return a;
    }

    private static String mode(Map<String, Long> freq) {
        return freq.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);
    }
}