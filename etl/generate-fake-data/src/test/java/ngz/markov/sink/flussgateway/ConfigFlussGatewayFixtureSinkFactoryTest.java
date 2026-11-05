package ngz.markov.sink.flussgateway;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatNullPointerException;
import static org.assertj.core.api.Assertions.assertThatIllegalArgumentException;

class ConfigFlussGatewayFixtureSinkFactoryTest {

    // ── minimal valid params ─────────────────────────────────────────────────

    private static Map<String, String> baseParams() {
        return new HashMap<>(Map.of(
                "gatewayurl", "http://localhost:8080",
                "clusterid",  "cluster-1",
                "database",   "mydb",
                "table",      "orders"
        ));
    }

    // ── endpoint building ────────────────────────────────────────────────────

    @Test
    void endpoint_usesDefaultApiVersion() {
        var config = new ConfigFlussGatewayFixtureSinkFactory(baseParams());

        assertThat(config.getEndpoint())
                .isEqualTo("http://localhost:8080/v1/clusters/cluster-1/databases/mydb/tables/orders/records");
    }

    @Test
    void endpoint_usesCustomApiVersion() {
        var params = baseParams();
        params.put("apiversion", "v2");

        var config = new ConfigFlussGatewayFixtureSinkFactory(params);

        assertThat(config.getEndpoint())
                .isEqualTo("http://localhost:8080/v2/clusters/cluster-1/databases/mydb/tables/orders/records");
    }

    @Test
    void endpoint_stripsTrailingSlashFromGatewayUrl() {
        var params = baseParams();
        params.put("gatewayurl", "http://localhost:8080/");

        var config = new ConfigFlussGatewayFixtureSinkFactory(params);

        assertThat(config.getEndpoint())
                .doesNotContain("//v1")
                .startsWith("http://localhost:8080/v1");
    }

    @Test
    void endpoint_stripsMultipleTrailingSlashes() {
        var params = baseParams();
        params.put("gatewayurl", "http://localhost:8080///");

        var config = new ConfigFlussGatewayFixtureSinkFactory(params);

        assertThat(config.getEndpoint())
                .startsWith("http://localhost:8080/v1");
    }

    @Test
    void endpoint_containsAllSegmentsInOrder() {
        var config = new ConfigFlussGatewayFixtureSinkFactory(baseParams());

        assertThat(config.getEndpoint())
                .containsSubsequence(
                        "http://localhost:8080",
                        "/v1/",
                        "clusters/cluster-1/",
                        "databases/mydb/",
                        "tables/orders/",
                        "records"
                );
    }

    // ── defaults ─────────────────────────────────────────────────────────────

    @Test
    void operation_defaultsToAppend() {
        var config = new ConfigFlussGatewayFixtureSinkFactory(baseParams());

        assertThat(config.getOperation().toString()).isEqualTo("append");
    }

    @Test
    void operation_canBeOverridden() {
        var params = baseParams();
        params.put("operation", "upsert");

        var config = new ConfigFlussGatewayFixtureSinkFactory(params);

        assertThat(config.getOperation().toString()).isEqualTo("upsert");
    }

    @Test
    void apiVersion_defaultsToV1() {
        var config = new ConfigFlussGatewayFixtureSinkFactory(baseParams());

        assertThat(config.getApiVersion()).isEqualTo("v1");
    }

    // ── validation ───────────────────────────────────────────────────────────

    @Test
    void constructor_throwsWhenParamsIsNull() {
        assertThatNullPointerException()
                .isThrownBy(() -> new ConfigFlussGatewayFixtureSinkFactory(null));
    }

    @ParameterizedTest(name = "missing required param: {0}")
    @ValueSource(strings = {"gatewayurl", "clusterid", "database", "table"})
    void constructor_throwsWhenRequiredParamIsMissing(String missingKey) {
        var params = baseParams();
        params.remove(missingKey);

        assertThatIllegalArgumentException()
                .isThrownBy(() -> new ConfigFlussGatewayFixtureSinkFactory(params))
                .withMessageContaining(missingKey);
    }

    @ParameterizedTest(name = "blank required param: {0}")
    @ValueSource(strings = {"gatewayurl", "clusterid", "database", "table"})
    void constructor_throwsWhenRequiredParamIsBlank(String blankKey) {
        var params = baseParams();
        params.put(blankKey, "   ");

        assertThatIllegalArgumentException()
                .isThrownBy(() -> new ConfigFlussGatewayFixtureSinkFactory(params))
                .withMessageContaining(blankKey);
    }

    // ── static config ─────────────────────────────────────────────────────────

    @Test
    void headers_containContentType() {
        var config = new ConfigFlussGatewayFixtureSinkFactory(baseParams());

        assertThat(config.getHeaders())
                .containsEntry("Content-Type", "application/json");
    }
}