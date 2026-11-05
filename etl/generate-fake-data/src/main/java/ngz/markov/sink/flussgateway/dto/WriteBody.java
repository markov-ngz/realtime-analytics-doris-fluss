package ngz.markov.sink.flussgateway.dto;


import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = false)
public record WriteBody(
        @NotEmpty
        List<@NotNull @jakarta.validation.Valid WriteBodyEntry> entries,

        @JsonProperty("partial_update_columns")
        @JsonInclude(JsonInclude.Include.NON_NULL)
        List<@NotBlank String> partialUpdateColumns
) {
}