package ngz.markov.sink.flussgateway;

import lombok.Data;
import ngz.markov.sink.flussgateway.dto.WriteOperation;

import java.io.Serializable;
import java.util.Map;
import java.util.Objects;

@Data
public class ConfigFlussGatewayFixtureSinkFactory implements Serializable {

    private final String apiVersion;
    private final String gatewayUrl;
    private final String clusterId;
    private final String database;
    private final String table;
    private final WriteOperation operation ;

    private final String endpoint;
    private static final String ENDPOINT_FORMAT =
            "%s/%s/clusters/%s/databases/%s/tables/%s/records";
    private final Map<String,String> headers = Map.of(
            "Content-Type","application/json"
    );

    private final Map<String,String> additionalProperties = Map.of(
            "http.sink.writer.request.mode","single"
    );

    public ConfigFlussGatewayFixtureSinkFactory(Map<String, String> params) {
        Objects.requireNonNull(params, "params must not be null");

        this.apiVersion = params.getOrDefault("apiversion","v1");
        this.operation =  WriteOperation.valueOf(
                params.getOrDefault("operation", WriteOperation.append.name())
                        .toLowerCase()
        );
        this.gatewayUrl = required(params, "gatewayurl");
        this.clusterId = required(params,"clusterid");
        this.database = required(params, "database");
        this.table = required(params, "table");

        this.endpoint = String.format(
                ENDPOINT_FORMAT,
                stripTrailingSlash(gatewayUrl),
                apiVersion,
                clusterId,
                database,
                table
        );
    }
    private static String stripTrailingSlash(String url) {
        return url.replaceAll("/+$", "");
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
