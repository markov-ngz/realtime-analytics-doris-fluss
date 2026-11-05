package ngz.markov.source;

import ngz.markov.model.SearchEvent;
import org.apache.fluss.client.initializer.OffsetsInitializer;
import org.apache.fluss.config.Configuration;
import org.apache.fluss.flink.source.FlussSource;

/**
 * Factory for the staging.search_event FlussSource.
 *
 * Projection keeps only the 11 fields needed by the hot-search pipeline;
 * all SKU, product, experiment, rank and ingestion-metadata columns are
 * excluded at the source to reduce I/O (column pruning via Arrow log format).
 */
public final class SearchEventSource {

    private SearchEventSource() {}

    public static FlussSource<SearchEvent> build(String bootstrapServers, String database , String table , Configuration flussConfig) {
        return FlussSource.<SearchEvent>builder()
                .setBootstrapServers(bootstrapServers)
                .setDatabase(database)
                .setTable(table)
                .setFlussConfig(flussConfig)
                // Projected fields — column pruning pushed to Fluss storage layer.
                // Order here defines the positional index used in
                // SearchEventDeserializationSchema.
                .setProjectedFields(
                        "event_id",
                        "event_type",
                        "event_time",
                        "user_id",
                        "session_id",
                        "device_type",
                        "channel",
                        "region",
                        "search_text",
                        "order_id",
                        "revenue"
                )
                // Start from the latest snapshot so the job replays from a
                // known consistent point on first startup.
                .setStartingOffsets(OffsetsInitializer.full())
                .setDeserializationSchema(new SearchEventDeserializationSchema())
                .build();
    }
}
