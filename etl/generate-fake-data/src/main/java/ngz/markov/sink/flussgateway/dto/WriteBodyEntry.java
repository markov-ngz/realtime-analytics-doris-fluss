package ngz.markov.sink.flussgateway.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.constraints.AssertTrue;
import jakarta.validation.constraints.NotBlank;

@JsonIgnoreProperties(ignoreUnknown = false)
public record WriteBodyEntry(
        @NotBlank String id,

        @JsonInclude(JsonInclude.Include.NON_NULL) JsonNode append,
        @JsonInclude(JsonInclude.Include.NON_NULL) JsonNode upsert,
        @JsonInclude(JsonInclude.Include.NON_NULL) JsonNode delete
) {
    // Static factories — exactly one field is ever populated
    public static WriteBodyEntry forAppend(String id, JsonNode payload) {
        return new WriteBodyEntry(id, payload, null, null);
    }

    public static WriteBodyEntry forUpsert(String id, JsonNode payload) {
        return new WriteBodyEntry(id, null, payload, null);
    }

    public static WriteBodyEntry forDelete(String id, JsonNode payload) {
        return new WriteBodyEntry(id, null, null, payload);
    }

    @AssertTrue(message = "Exactly one of append, upsert, or delete must be provided")
    public boolean hasExactlyOneOperation() {
        int count = 0;
        if (append != null && !append.isNull()) count++;
        if (upsert != null && !upsert.isNull()) count++;
        if (delete != null && !delete.isNull()) count++;
        return count == 1;
    }
}