package ngz.markov.sink.fluss;

import lombok.Getter;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

@Getter
public class ConfigFlussFixtureSink {

    private final String bootstrapServers;
    private final String database;
    private final String table;
    private final Map<String, String> options;

    public ConfigFlussFixtureSink(Map<String, String> params) {
        Objects.requireNonNull(params, "params must not be null");

        this.bootstrapServers = required(params, "bootstrapServers");
        this.database = required(params, "database");
        this.table = required(params, "table");

        Map<String, String> remaining = new HashMap<>(params);
        remaining.keySet().removeAll(
                Set.of("bootstrapServers", "database", "table"));

        this.options = Map.copyOf(remaining);
    }

    private static String required(
            Map<String, String> params, String key) {

        String value = params.get(key);

        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "Missing required configuration: " + key);
        }

        return value;
    }
}
