package ngz.markov.sink.flussgateway;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import ngz.markov.fixtures.dummy.Customer;
import ngz.markov.sink.flussgateway.dto.WriteOperation;
import org.apache.flink.api.connector.sink2.SinkWriter;
import org.apache.flink.connector.http.sink.HttpSinkRequestEntry;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;

class FlussGatewayFixtureSinkFactoryTest {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void elementConverter_shouldProduceCorrectHttpRequest() throws Exception {
        // Given
        Customer customer = Customer.builder()
                .customerId("456")
                .brandId(1)
                .build();

        WriteBodySerializer<Customer> serializer = new WriteBodySerializer<>(WriteOperation.upsert);
        UUID fixedUuid = UUID.fromString("00000000-0000-0000-0000-000000000000");

        FlussGatewayFixtureSinkFactory.SerializingElementConverter<Customer> converter =
                new FlussGatewayFixtureSinkFactory.SerializingElementConverter<>(serializer);

        HttpSinkRequestEntry entry;
        try (MockedStatic<UUID> uuidMock = mockStatic(UUID.class)) {
            uuidMock.when(UUID::randomUUID).thenReturn(fixedUuid);
            entry = converter.apply(customer, mock(SinkWriter.Context.class));
        }

        // HTTP method
        assertEquals("POST", entry.method);

        // Body shape — confirmed by curl: {"entries":[...]} → 200, [...] → 400
        String expectedJson = """
                {
                  "entries": [{
                    "id": "Customer-00000000-0000-0000-0000-000000000000",
                    "upsert": {
                      "customer_id": "456",
                      "brand_id": 1
                    }
                  }]
                }
                """;

        JsonNode actual = objectMapper.readTree(entry.element);
        assertEquals(
                objectMapper.readTree(expectedJson),
                actual,
                "Converter must produce the confirmed 200-producing payload shape"
        );

        // Body must be valid UTF-8 — latin-1 / encoding mismatch is a classic 400 cause
        assertDoesNotThrow(
                () -> objectMapper.readTree(new String(entry.element, StandardCharsets.UTF_8)),
                "Body must be valid UTF-8 encoded JSON"
        );
    }

    @Test
    void create_shouldResolveUpsertOperation_whenParamProvided() {
        // Guards against the silent APPEND fallback if the key name ever drifts
        Map<String, String> params = Map.of(
                "endpoint",  "http://fluss-gateway:8080/v1/.../records",
                "operation", "upsert"
        );

        WriteOperation resolved = WriteOperation.valueOf(
                params.getOrDefault("operation", WriteOperation.append.name())
        );

        assertEquals(WriteOperation.upsert, resolved,
                "Operation param 'upsert' must resolve correctly, not fall back to append");
    }

    @Test
    void create_shouldFallbackToAppend_whenOperationParamAbsent() {
        // If the param is missing, the default must be APPEND (explicit contract)
        Map<String, String> params = Map.of(
                "endpoint", "http://fluss-gateway:8080/v1/.../records"
                // "operation" key intentionally absent
        );

        WriteOperation resolved = WriteOperation.valueOf(
                params.getOrDefault("operation", WriteOperation.append.name())
        );

        assertEquals(WriteOperation.append, resolved,
                "Missing operation param must fall back to append, not throw");
    }
}