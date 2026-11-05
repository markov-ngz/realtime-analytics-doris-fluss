package ngz.markov.source;


import ngz.markov.model.SaleOrder;
import org.apache.fluss.client.initializer.OffsetsInitializer;
import org.apache.fluss.config.Configuration;
import org.apache.fluss.flink.source.FlussSource;

/**
 * Factory for the staging.sale_order FlussSource.
 * Projection retains only the 5 fields needed for the attribution join.
 * user_id, device_type, channel, region are excluded because they are
 * sourced from the authoritative search_event side during the join.
 */
public final class SaleOrderSource {

    // --- hard-coded skeleton config (replace with actual values / config file) ---
    private static final String BOOTSTRAP_SERVERS = "fluss-coordinator:9123";
    private static final String DATABASE          = "staging";
    private static final String TABLE             = "sale_order";

    private SaleOrderSource() {}

    public static FlussSource<SaleOrder> build(String bootstrapServers, String database , String table , Configuration flussConfig) {
        return FlussSource.<SaleOrder>builder()
                .setBootstrapServers(bootstrapServers)
                .setDatabase(database)
                .setTable(table)
                .setFlussConfig(flussConfig)
                // Projected fields — positional index matches
                // SaleOrderDeserializationSchema.
                .setProjectedFields(
                        "order_id",
                        "order_status",
                        "order_time",
                        "session_id",
                        "revenue"
                )
                .setStartingOffsets(OffsetsInitializer.full())
                .setDeserializationSchema(new SaleOrderDeserializationSchema())
                .build();
    }
}

