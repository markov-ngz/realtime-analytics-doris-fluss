package ngz.markov.sink.flussgateway;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import ngz.markov.sink.flussgateway.dto.WriteBody;
import ngz.markov.sink.flussgateway.dto.WriteBodyEntry;
import ngz.markov.sink.flussgateway.dto.WriteOperation;

import java.io.Serializable;
import java.util.List;
import java.util.UUID;

public class WriteBodySerializer<T> implements Serializable {

    private static transient ObjectMapper OBJECT_MAPPER = new ObjectMapper()
            .configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);

    private static ObjectMapper mapper() {
        if (OBJECT_MAPPER == null) {
            OBJECT_MAPPER = new ObjectMapper()
                    .configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);
        }
        return OBJECT_MAPPER;
    }
    private final WriteOperation operation;

    public WriteBodySerializer(WriteOperation operation) {
        this.operation = operation;
    }

    public byte[] serialize(T event) throws JsonProcessingException {
        // Convert the event POJO → JsonNode (preserves number precision)
        JsonNode payload = mapper().valueToTree(event);

        // id: "ClassName-UUID" — opaque correlation, unique per entry
        String id = event.getClass().getSimpleName() + "-" + UUID.randomUUID();

        WriteBodyEntry entry = switch (operation) {
            case append -> WriteBodyEntry.forAppend(id, payload);
            case upsert -> WriteBodyEntry.forUpsert(id, payload);
            case delete -> WriteBodyEntry.forDelete(id, payload);
        };

        WriteBody writeBody = new WriteBody(List.of(entry), null);

        return mapper().writeValueAsBytes(writeBody);

    }
}