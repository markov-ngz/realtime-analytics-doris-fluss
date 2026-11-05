package ngz.markov;

import lombok.Getter;
import org.apache.flink.util.ParameterTool;
import org.apache.fluss.config.Configuration;

import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Getter
public final class JobConfig {

    /** Arguments under this prefix are forwarded to the Fluss client config with the prefix stripped. */
    private static final String FLUSS_CLIENT_PREFIX = "fluss.client.";

    private final String jobName;
    private final String bootstrapServers;
    private final Configuration flussConfig;
    private final Map<String, String> flussOptions;

    // Fluss sources
    private final String saleOrderDatabase;
    private final String saleOrderTable;
    private final String searchEventDatabase;
    private final String searchEventTable;

    // Fluss sink
    private final String searchTrendsDatabase;
    private final String searchTrendsTable;

    // Transformation options
    private final Duration outOfOrdernessBound;
    private final Duration hopWindowSize;
    private final Duration hopWindowSlide;

    // Source idleness timeouts
    private final Duration searchEventIdleTimeout;
    private final Duration saleOrderIdleTimeout;

    private JobConfig(ParameterTool params) {
        require(params,
                "fluss.bootstrap.servers",
                "fluss.source.sale-order.database",
                "fluss.source.sale-order.table",
                "fluss.source.search-event.database",
                "fluss.source.search-event.table",
                "fluss.sink.search-trends.database",
                "fluss.sink.search-trends.table");

        this.jobName = params.get("job.name", "mart-search-trends");
        this.bootstrapServers = params.get("fluss.bootstrap.servers");
        this.saleOrderDatabase = params.get("fluss.source.sale-order.database");
        this.saleOrderTable = params.get("fluss.source.sale-order.table");
        this.searchEventDatabase = params.get("fluss.source.search-event.database");
        this.searchEventTable = params.get("fluss.source.search-event.table");
        this.searchTrendsDatabase = params.get("fluss.sink.search-trends.database");
        this.searchTrendsTable = params.get("fluss.sink.search-trends.table");
        this.outOfOrdernessBound = duration(params, "window.out-of-orderness-bound", Duration.ofSeconds(5));
        this.hopWindowSize = duration(params, "window.hop-size", Duration.ofHours(1));
        this.hopWindowSlide = duration(params, "window.hop-slide", Duration.ofMinutes(5));
        this.searchEventIdleTimeout = duration(params, "source.search-event.idle-timeout", Duration.ofMinutes(1));
        this.saleOrderIdleTimeout = duration(params, "source.sale-order.idle-timeout", Duration.ofMinutes(5));
        this.flussOptions = forwardClientOptions(params);
        this.flussConfig = toFlussConfig(this.flussOptions, this.bootstrapServers);
    }

    public static JobConfig fromArgs(String[] args) {
        return new JobConfig(ParameterTool.fromArgs(args));
    }

    private static void require(ParameterTool params, String... keys) {
        List<String> missing = Stream.of(keys)
                .filter(key -> params.get(key) == null || params.get(key).isBlank())
                .toList();
        if (!missing.isEmpty()) {
            throw new IllegalArgumentException(
                    "Missing required argument(s): "
                            + missing.stream().map(key -> "--" + key).collect(Collectors.joining(", ")));
        }
    }

    private static Duration duration(ParameterTool params, String key, Duration defaultValue) {
        String value = params.get(key);
        return value == null ? defaultValue : Duration.parse(value);
    }

    private static Map<String, String> forwardClientOptions(ParameterTool params) {
        return params.toMap().entrySet().stream()
                .filter(entry -> entry.getKey().startsWith(FLUSS_CLIENT_PREFIX))
                .collect(Collectors.toMap(
                        entry -> entry.getKey().substring(FLUSS_CLIENT_PREFIX.length()),
                        Map.Entry::getValue,
                        (first, second) -> first,
                        LinkedHashMap::new));
    }

    private static Configuration toFlussConfig(Map<String, String> clientOptions, String bootstrapServers) {
        Configuration config = new Configuration();
        config.setString("bootstrap.servers", bootstrapServers);
        clientOptions.forEach(config::setString);
        return config;
    }
}