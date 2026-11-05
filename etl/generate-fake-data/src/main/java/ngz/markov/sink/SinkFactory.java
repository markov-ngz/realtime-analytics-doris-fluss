package ngz.markov.sink;

import ngz.markov.sink.fluss.FlussFixtureSinkFactory;
import ngz.markov.sink.flussgateway.FlussGatewayFixtureSinkFactory;
import org.apache.flink.api.connector.sink2.Sink;

import java.util.Map;
public final class SinkFactory {

    private static final Map<String, FixtureSinkFactory> FACTORIES =
            Map.of(
                    "fluss", new FlussFixtureSinkFactory(),
                    "fluss-gateway", new FlussGatewayFixtureSinkFactory()
            );
    public static <T> Sink<T> create(
            String sinkType,
            Map<String, String> sinkParams,
            Class<T> clazz) {

        FixtureSinkFactory factory = FACTORIES.get(sinkType);

        if (factory == null) {
            throw new IllegalArgumentException(
                    "Unsupported sink type: " + sinkType);
        }

        return factory.create(sinkParams, clazz);
    }
}