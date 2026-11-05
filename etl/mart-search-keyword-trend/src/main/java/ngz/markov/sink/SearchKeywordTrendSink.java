package ngz.markov.sink;

import ngz.markov.model.SearchKeywordTrend;
import org.apache.fluss.config.Configuration;
import org.apache.fluss.flink.sink.FlussSink;

public final class SearchKeywordTrendSink {

    private SearchKeywordTrendSink() {
        // Private constructor to prevent instantiation
    }

    public static FlussSink<SearchKeywordTrend> build(String bootstrapServers, String database , String table , Configuration flussConfig) {
        return FlussSink.<SearchKeywordTrend>builder()
                .setBootstrapServers(bootstrapServers)
                .setDatabase(database)
                .setTable(table)
                .setOptions(flussConfig.toMap())
                .setSerializationSchema(new SearchKeywordTrendSerializationSchema())
                .build();
    }
}