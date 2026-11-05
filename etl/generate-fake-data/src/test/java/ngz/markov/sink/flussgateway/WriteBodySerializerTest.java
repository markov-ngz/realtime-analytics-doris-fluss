package ngz.markov.sink.flussgateway;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import ngz.markov.fixtures.dummy.Customer;
import ngz.markov.sink.flussgateway.dto.WriteOperation;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mockStatic;
class WriteBodySerializerTest {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    void serialize_upsert_shouldMatchExpectedPayloadStructure() throws Exception {
        // Given
        Customer customer = Customer.builder()
                .customerId("456")
                .brandId(1)
                .build();

        WriteBodySerializer<Customer> serializer = new WriteBodySerializer<>(WriteOperation.upsert);
        UUID fixedUuid = UUID.fromString("00000000-0000-0000-0000-000000000000");

        byte[] result;
        try (MockedStatic<UUID> uuidMock = mockStatic(UUID.class)) {
            uuidMock.when(UUID::randomUUID).thenReturn(fixedUuid);
            result = serializer.serialize(customer);
        }

        // Root must be an object with an "entries" array — confirmed by curl 200
        JsonNode actual = objectMapper.readTree(result);
        assertTrue(actual.isObject(),      "Root must be a JSON object");
        assertTrue(actual.has("entries"),  "Root object must have 'entries' field");
        assertTrue(actual.get("entries").isArray(), "'entries' must be an array");
        assertEquals(1, actual.get("entries").size(), "Must have exactly one entry");

        JsonNode entry = actual.get("entries").get(0);

        assertTrue(entry.has("id"), "Entry must have an 'id' field");
        assertTrue(entry.get("id").asText().startsWith("Customer-"),
                "ID must start with 'Customer-'");

        assertTrue(entry.has("upsert"),  "Entry must have 'upsert' key for upsert operation");
        assertFalse(entry.has("append"), "Entry must NOT have 'append' key");
        assertFalse(entry.has("delete"), "Entry must NOT have 'delete' key");

        JsonNode upsertPayload = entry.get("upsert");
        assertEquals("456", upsertPayload.get("customer_id").asText());
        assertEquals(1,     upsertPayload.get("brand_id").asInt());
    }

    @Test
    void serialize_upsert_withFixedId_shouldMatchExactPayload() throws Exception {
        Customer customer = Customer.builder()
                .customerId("456")
                .brandId(1)
                .build();

        WriteBodySerializer<Customer> serializer = new WriteBodySerializer<>(WriteOperation.upsert);
        UUID fixedUuid = UUID.fromString("00000000-0000-0000-0000-000000000000");

        byte[] result;
        try (MockedStatic<UUID> uuidMock = mockStatic(UUID.class)) {
            uuidMock.when(UUID::randomUUID).thenReturn(fixedUuid);
            result = serializer.serialize(customer);
        }

        // Exact shape confirmed by: curl -d '{"entries":[...]}' → 200
        //                           curl -d '[...]'             → 400
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

        assertEquals(
                objectMapper.readTree(expectedJson),
                objectMapper.readTree(result),
                "Serialized payload must match the confirmed 200-producing curl shape"
        );
    }

    @Test
    void serialize_append_shouldUseAppendKey() throws Exception {
        Customer customer = Customer.builder().customerId("123").brandId(2).build();
        WriteBodySerializer<Customer> serializer = new WriteBodySerializer<>(WriteOperation.append);

        JsonNode entry = objectMapper.readTree(serializer.serialize(customer))
                .get("entries").get(0);

        assertTrue(entry.has("append"),  "Entry must use 'append' key for append operation");
        assertFalse(entry.has("upsert"), "Entry must NOT have 'upsert' key");
        assertFalse(entry.has("delete"), "Entry must NOT have 'delete' key");
    }

    @Test
    void serialize_delete_shouldUseDeleteKey() throws Exception {
        Customer customer = Customer.builder().customerId("789").brandId(3).build();
        WriteBodySerializer<Customer> serializer = new WriteBodySerializer<>(WriteOperation.delete);

        JsonNode entry = objectMapper.readTree(serializer.serialize(customer))
                .get("entries").get(0);

        assertTrue(entry.has("delete"),  "Entry must use 'delete' key for delete operation");
        assertFalse(entry.has("upsert"), "Entry must NOT have 'upsert' key");
        assertFalse(entry.has("append"), "Entry must NOT have 'append' key");
    }
}