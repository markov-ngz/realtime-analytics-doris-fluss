package ngz.markov.sink.flussgateway;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import ngz.markov.fixtures.dummy.Customer;
import ngz.markov.sink.flussgateway.dto.WriteOperation;
import org.apache.flink.api.connector.sink2.Sink;
import org.junit.jupiter.api.Test;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.http.HttpRequest;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThatNoException;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SerializationTest {

    private static final Map<String, String> PARAMS = Map.of(
            "gatewayurl", "http://localhost:8080",
            "clusterid",  "cluster-1",
            "database",   "mydb",
            "table",      "customers"
    );

    @Test
    void flussGatewayFixtureSinkFactory_shouldBeSerializable() {
        FlussGatewayFixtureSinkFactory factory = new FlussGatewayFixtureSinkFactory();
        assertThatNoException().isThrownBy(() -> serialize(factory));
    }

    @Test
    void sink_builtByFactory_shouldBeSerializable() {
        FlussGatewayFixtureSinkFactory factory = new FlussGatewayFixtureSinkFactory();
        Sink<Customer> sink = factory.create(PARAMS, Customer.class);
        assertThatNoException().isThrownBy(() -> serialize(sink));
    }

    @Test
    void writeBodySerializer_shouldBeSerializable() {
        WriteBodySerializer<Customer> serializer = new WriteBodySerializer<>(WriteOperation.append);
        assertThatNoException().isThrownBy(() -> serialize(serializer));
    }

    @Test
    void configFlussGatewayFixtureSinkFactory_shouldBeSerializable() {
        ConfigFlussGatewayFixtureSinkFactory config = new ConfigFlussGatewayFixtureSinkFactory(PARAMS);
        assertThatNoException().isThrownBy(() -> serialize(config));
    }

    @Test
    void serialize_bodyFitsInSingleChunk_noChunkedEncoding() throws Exception {
        Customer customer = Customer.builder()
                .customerId("456")
                .brandId(1)
                .build();

        WriteBodySerializer<Customer> serializer = new WriteBodySerializer<>(WriteOperation.upsert);
        byte[] body = serializer.serialize(customer);

        // Body must be a self-contained, parseable JSON object in one shot
        // If chunked encoding splits it, partial chunks won't parse
        ObjectMapper mapper = new ObjectMapper();
        JsonNode root = assertDoesNotThrow(
                () -> mapper.readTree(body),
                "Body must parse as complete JSON in a single read — " +
                        "partial chunk parsing will fail with 'expected a sequence'"
        );

        assertTrue(root.isObject(), "Root must be a JSON object (map), not a bare array");
        assertTrue(root.has("entries"), "Root object must have 'entries' key");

        // Confirm Content-Length can be set (body length is known)
        assertTrue(body.length > 0, "Body must have known, non-zero length for Content-Length header");
        HttpRequest.BodyPublisher publisher = HttpRequest.BodyPublishers.ofByteArray(body);
        assertEquals(body.length, publisher.contentLength(),
                "BodyPublisher.contentLength() must equal actual body length — " +
                        "a value of -1 means chunked encoding will be used");
    }

    // ── helper ──────────────────────────────────────────────────────────────

    private static byte[] serialize(Object obj) throws IOException {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
             ObjectOutputStream oos = new ObjectOutputStream(bos)) {
            oos.writeObject(obj);
            return bos.toByteArray();
        }
    }
}
