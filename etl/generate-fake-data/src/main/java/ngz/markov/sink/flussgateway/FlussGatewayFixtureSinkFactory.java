package ngz.markov.sink.flussgateway;

import com.fasterxml.jackson.core.JsonProcessingException;
import ngz.markov.GenerateFakeDataStreamJob;
import ngz.markov.sink.FixtureSinkFactory;
import org.apache.commons.collections.MapUtils;
import org.apache.flink.api.connector.sink2.Sink;
import org.apache.flink.api.connector.sink2.SinkWriter;
import org.apache.flink.api.connector.sink2.WriterInitContext;
import org.apache.flink.connector.http.HttpPostRequestCallback;
import org.apache.flink.connector.http.HttpSink;
import org.apache.flink.connector.http.HttpSinkBuilder;
import org.apache.flink.connector.http.SchemaLifecycleAwareElementConverter;
import org.apache.flink.connector.http.sink.HttpSinkRequestEntry;
import org.apache.flink.connector.http.sink.httpclient.HttpRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Serializable;
import java.io.UncheckedIOException;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public class FlussGatewayFixtureSinkFactory implements FixtureSinkFactory , Serializable {

    private static final Logger LOG = LoggerFactory.getLogger(FlussGatewayFixtureSinkFactory.class);

    @Override
    public <T> Sink<T> create(Map<String, String> params, Class<T> clazz) {

        ConfigFlussGatewayFixtureSinkFactory config =
                new ConfigFlussGatewayFixtureSinkFactory(params);

        WriteBodySerializer<T> serializer = new WriteBodySerializer<>(config.getOperation());

        HttpSinkBuilder<T> builder = HttpSink.<T>builder()
                .setEndpointUrl(config.getEndpoint())
                .setElementConverter(buildSchemaLifecycleAwareElementConvert(serializer))
                .setProperties(MapUtils.toProperties(config.getAdditionalProperties()))
                .setHttpPostRequestCallback(new HttpPostRequestCallback<HttpRequest>() {
                    private static final Logger LOG = LoggerFactory.getLogger(FlussGatewayFixtureSinkFactory.class);

                    @Override
                    public void call(HttpResponse<String> response,
                                     HttpRequest requestEntry,
                                     String endpointUrl,
                                     Map<String, String> headerMap) {



                        int status = response.statusCode();

                        if (status < 200 || status >= 300) {
                            LOG.error("""
                    HTTP Sink request failed
                      Status  : {}
                      URL     : {}
                      Headers : {}requestEntry
                      Body    : {}
                      Response: {}
                    """,
                                    status,
                                    endpointUrl,
                                    headerMap,
                                    requestEntry.getHttpRequest().bodyPublisher()
                                            .map(p -> "<body publisher present>")
                                            .orElse("<no body>"),
                                    response.body()
                            );
                        } else {
                            LOG.debug("HTTP {} — {}", status, endpointUrl);
                        }
                    }
                })
                ;
        setHeaders(builder, config.getHeaders());

        return builder.build();
    }

    private <T> void setHeaders(HttpSinkBuilder<T> builder, Map<String, String> headers) {
        headers.forEach((key, value) ->
                builder.setProperty("http.sink.header." + key, value)
        );
    }

    private <T> SchemaLifecycleAwareElementConverter<T, HttpSinkRequestEntry>
    buildSchemaLifecycleAwareElementConvert(WriteBodySerializer<T> serializer) {
        return new SerializingElementConverter<>(serializer); // ← named class, serializable
    }

    static final class SerializingElementConverter<T>
            implements SchemaLifecycleAwareElementConverter<T, HttpSinkRequestEntry>,
            Serializable {

        private final WriteBodySerializer<T> serializer;

        SerializingElementConverter(WriteBodySerializer<T> serializer) {
            this.serializer = serializer;
        }

        @Override
        public void open(WriterInitContext context) {}
        @Override
        public HttpSinkRequestEntry apply(T event, SinkWriter.Context context) {
            try {
                byte[] body = serializer.serialize(event);
                // already a fixed array ?
                return new HttpSinkRequestEntry("POST", body);
            } catch (JsonProcessingException e) {
                throw new UncheckedIOException("Failed to serialize event", e);
            }
        }
    }
}