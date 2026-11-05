package ngz.markov.sink;

import org.apache.flink.api.connector.sink2.Sink;

import java.util.Map;

public interface FixtureSinkFactory {

    <T> Sink<T> create(
            Map<String, String> params,
            Class<T> clazz);

}