package ngz.markov.sink.fluss;

import ngz.markov.fixtures.crm.Customer;
import ngz.markov.sink.FixtureSinkFactory;
import ngz.markov.sink.fluss.serializationschema.CustomerSerializationSchema;
import org.apache.flink.api.connector.sink2.Sink;
import org.apache.fluss.flink.sink.FlussSink;

import java.util.Map;

public class FlussFixtureSinkFactory implements FixtureSinkFactory {

    private final SerializationSchemaRegistry schemas ;

    public FlussFixtureSinkFactory(){
        this.schemas =
                new SerializationSchemaRegistry();
        schemas.register(Customer.class, CustomerSerializationSchema::new);
    }

    @Override
    public <T> Sink<T> create(Map<String, String> params, Class<T> clazz){

        ConfigFlussFixtureSink config = new ConfigFlussFixtureSink(params);

        return FlussSink.<T>builder()
                .setBootstrapServers(config.getBootstrapServers())
                .setDatabase(config.getDatabase())
                .setTable(config.getTable())
                .setSerializationSchema(schemas.get(clazz))
                .setOptions(params)
                .build();
    }
}
